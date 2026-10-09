"""Cinematic finishing + 3D typography for the Friends margin-trading carousel.

Every slide goes through the same pipeline so fonts, grade and layout stay
consistent:

    grade()      teal/orange cinematic grade, bloom, light rays, vignette, grain
    scrims()     top + bottom black gradients that the text sits on
    Title3D      extruded 3D headline with Friends-style coloured dots
    flat text    kicker / body / handwritten lines with soft shadows

Usage:  python3 finish.py cover <raw.png> <out.jpg>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / "fonts"
ANTON = str(FONT_DIR / "Anton-Regular.ttf")
MARKER = str(FONT_DIR / "PermanentMarker-Regular.ttf")
MONT = str(FONT_DIR / "Montserrat.ttf")

# Friends palette
RED, YELLOW, BLUE = (229, 57, 53), (253, 216, 53), (30, 136, 229)
DOTS = [RED, YELLOW, BLUE]
WHITE = (255, 255, 255)
CREAM = (255, 244, 225)
GOLD = (255, 198, 55)
PURPLE = (94, 53, 177)


# ----------------------------------------------------------------- grading
def grade(img: Image.Image, seed: int = 7) -> Image.Image:
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

    # S-curve contrast
    a = a + 0.10 * (a - 0.5) * (1 - np.abs(2 * a - 1))

    # Teal shadows, warm amber highlights (split tone)
    sh = np.clip(1 - lum * 2.2, 0, 1)[..., None]
    hi = np.clip(lum * 1.6 - 0.6, 0, 1)[..., None]
    a = a + sh * np.array([-0.025, 0.012, 0.035]) + hi * np.array([0.04, 0.018, -0.03])

    # Lift blacks slightly (filmic), roll off whites
    a = 0.015 + a * 0.975
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))

    # Bloom: blurred highlights screened back on
    W, H = out.size
    bright = out.point(lambda v: max(0, v - 185) * 3)
    bloom = bright.filter(ImageFilter.GaussianBlur(W * 0.018))
    out = ImageChops.screen(out, bloom.point(lambda v: int(v * 0.55)))

    # Volumetric light rays from upper-left window
    rays = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(rays)
    src = (-W * 0.1, -H * 0.05)
    for i, ang in enumerate(np.linspace(0.35, 1.05, 7)):
        L = H * 1.6
        w = 0.035 + 0.02 * (i % 2)
        p1 = (src[0] + L * np.cos(ang - w), src[1] + L * np.sin(ang - w))
        p2 = (src[0] + L * np.cos(ang + w), src[1] + L * np.sin(ang + w))
        d.polygon([src, p1, p2], fill=22 + 10 * (i % 3))
    rays = rays.filter(ImageFilter.GaussianBlur(W * 0.03))
    warm = Image.new("RGB", (W, H), (255, 200, 140))
    out = Image.composite(ImageChops.screen(out, warm), out, rays)

    # Vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.52) / (H / 2)) ** 2)
    v = np.clip(1 - 0.38 * np.clip(r - 0.55, 0, None) ** 1.5, 0, 1)
    o = np.asarray(out).astype(np.float32) * v[..., None]

    # Fine film grain
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 4.2, (H, W)).astype(np.float32)
    o = np.clip(o + g[..., None], 0, 255)
    return Image.fromarray(o.astype(np.uint8))


def scrims(img: Image.Image, top_frac=0.40, top_alpha=235, bot_frac=0.34, bot_alpha=250):
    """Black gradients at top and bottom so text is always legible."""
    W, H = img.size
    m = np.zeros((H, 1), np.float32)
    t = int(H * top_frac)
    y = np.arange(t)
    m[:t, 0] = top_alpha * (1 - y / t) ** 1.35
    b = int(H * bot_frac)
    y = np.arange(b)
    m[H - b:, 0] = np.maximum(m[H - b:, 0], bot_alpha * (y / b) ** 1.25)
    mask = Image.fromarray(np.repeat(m, W, 1).astype(np.uint8))
    black = Image.new("RGB", (W, H), (6, 4, 3))
    return Image.composite(black, img.convert("RGB"), mask)


# ----------------------------------------------------------------- text
class Canvas:
    def __init__(self, img):
        self.base = img.convert("RGBA")
        self.W, self.H = self.base.size
        self.s = self.W / 1080  # design grid is 1080 wide
        self.boxes = []  # placed text boxes, to assert no overlaps

    def font(self, path, size, wght=None):
        f = ImageFont.truetype(path, max(1, int(size * self.s)))
        if wght:
            f.set_variation_by_axes([wght])
        return f

    def _claim(self, box, label):
        for b, l in self.boxes:
            if not (box[2] <= b[0] or box[0] >= b[2] or box[3] <= b[1] or box[1] >= b[3]):
                raise RuntimeError(f"text overlap: {label!r} hits {l!r}")
        self.boxes.append((box, label))

    def _paste(self, layer):
        self.base = Image.alpha_composite(self.base, layer)

    # -- flat text with soft shadow ---------------------------------
    def text(self, y, txt, font, fill, tracking=0, shadow=0.8, label=None, glow=None):
        W, s = self.W, self.s
        widths = [font.getlength(c) for c in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        x0 = (W - total) / 2
        lay = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        x = x0
        for c, w in zip(txt, widths):
            d.text((x, y), c, font=font, fill=fill)
            x += w + tracking
        bbox = lay.getbbox()
        self._claim(bbox, label or txt)
        a = lay.getchannel("A")
        if shadow:
            sh = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
            sh.putalpha(a.filter(ImageFilter.GaussianBlur(6 * s)).point(lambda v: int(v * shadow)))
            sh = ImageChops.offset(sh, int(3 * s), int(4 * s))
            self._paste(sh)
        if glow:
            gl = Image.new("RGBA", self.base.size, glow + (0,))
            gl.putalpha(a.filter(ImageFilter.GaussianBlur(14 * s)).point(lambda v: int(v * 0.55)))
            self._paste(gl)
        self._paste(lay)
        return bbox

    # -- extruded 3D headline ---------------------------------------
    def title3d(self, y, txt, font, face_top, face_bot, side, tracking=0, dots=True,
                depth=16, label=None):
        W, s = self.W, self.s
        dot_gap = font.size * 0.15 if dots else 0
        widths = [font.getlength(c) for c in txt]
        total = sum(widths) + (len(txt) - 1) * (tracking + dot_gap)
        x = (W - total) / 2
        mask = Image.new("L", self.base.size, 0)
        dm = ImageDraw.Draw(mask)
        dot_specs = []
        asc, _ = font.getmetrics()
        for i, (c, w) in enumerate(zip(txt, widths)):
            dm.text((x, y), c, font=font, fill=255)
            x += w
            if i < len(txt) - 1:
                if dots and c != " " and txt[i + 1] != " ":
                    dot_specs.append((x + (tracking + dot_gap) / 2, y + asc * 0.84, DOTS[i % 3]))
                x += tracking + dot_gap
        bbox = mask.getbbox()
        dep = int(depth * s)
        self._claim((bbox[0], bbox[1], bbox[2] + dep, bbox[3] + dep), label or txt)

        # Ground shadow
        sh = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
        sh.putalpha(ImageChops.offset(mask, int(dep * 1.2), int(dep * 1.6))
                    .filter(ImageFilter.GaussianBlur(10 * s)).point(lambda v: int(v * 0.85)))
        self._paste(sh)

        # Extrusion: stacked offset copies, darkening towards the back
        ext = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
        for k in range(dep, 0, -1):
            t = k / dep
            col = tuple(int(c * (0.30 + 0.45 * (1 - t))) for c in side) + (255,)
            ext.paste(Image.new("RGBA", self.base.size, col), (0, 0), ImageChops.offset(mask, k, k))
        self._paste(ext)

        # Face: vertical gradient
        top, bot = bbox[1], bbox[3]
        grad = np.zeros((self.H, 1, 3), np.float32)
        yy = np.clip((np.arange(self.H) - top) / max(1, bot - top), 0, 1)[:, None]
        grad[:, 0, :] = np.array(face_top) * (1 - yy) + np.array(face_bot) * yy
        face = Image.fromarray(np.repeat(grad, W, 1).astype(np.uint8)).convert("RGBA")
        face.putalpha(mask)
        self._paste(face)

        # Bevel highlight on the top-left edges
        edge = ImageChops.subtract(mask, ImageChops.offset(mask, int(2 * s), int(2 * s)))
        hl = Image.new("RGBA", self.base.size, (255, 255, 255, 0))
        hl.putalpha(edge.point(lambda v: int(v * 0.75)))
        self._paste(hl)

        # Glossy 3D sphere dots
        lay = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        dsh = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(dsh)
        r = font.size * 0.05
        for cx, cy, col in dot_specs:
            dark = tuple(int(c * 0.45) for c in col)
            o = dep * 0.3
            sd.ellipse([cx - r + o, cy - r + o, cx + r + o, cy + r + o], fill=(0, 0, 0, 170))
            # Shaded sphere: concentric discs drifting toward the top-left light
            steps = 14
            for k in range(steps):
                t = k / (steps - 1)
                rr = r * (1 - 0.82 * t)
                ox = oy = -r * 0.38 * t
                if t < 0.5:
                    cc = tuple(int(dk + (c - dk) * t * 2) for dk, c in zip(dark, col))
                else:
                    cc = tuple(int(c + (255 - c) * (t - 0.5) * 0.7) for c in col)
                d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=cc)
            hr = r * 0.16
            d.ellipse([cx - r * 0.42 - hr, cy - r * 0.42 - hr, cx - r * 0.42 + hr, cy - r * 0.42 + hr],
                      fill=(255, 255, 255, 235))
        self._paste(dsh.filter(ImageFilter.GaussianBlur(3 * s)))
        self._paste(lay)
        return bbox

    # -- pill (rounded tag behind small text) -------------------------
    def pill(self, y, txt, font, fg, bg, border, pad=(26, 12), tracking=0, label=None):
        s = self.s
        w = sum(font.getlength(c) for c in txt) + tracking * (len(txt) - 1)
        asc, desc = font.getmetrics()
        pw, ph = pad[0] * s, pad[1] * s
        x0 = (self.W - w) / 2 - pw
        box = (int(x0), int(y), int(x0 + w + 2 * pw), int(y + asc + desc * 0.2 + 2 * ph))
        self._claim(box, label or txt)
        lay = Image.new("RGBA", self.base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle(box, radius=(box[3] - box[1]) / 2, fill=bg, outline=border, width=max(2, int(2.5 * s)))
        x = x0 + pw
        for c in txt:
            d.text((x, y + ph), c, font=font, fill=fg)
            x += font.getlength(c) + tracking
        self._paste(lay)
        self.boxes.pop()  # text drawn inside the pill shares its box
        self.boxes.append((box, label or txt))
        return box

    def save(self, out):
        self.base.convert("RGB").save(out, quality=95, subsampling=0)


# ----------------------------------------------------------------- slides
def cover(raw, out):
    img = Image.open(raw)
    img = grade(img)
    img = scrims(img, top_frac=0.42, top_alpha=240, bot_frac=0.34, bot_alpha=252)
    c = Canvas(img)
    s, H = c.s, c.H

    c.pill(40 * s, "A  BEGINNER'S  GUIDE  TO", c.font(MONT, 24, 800),
           fg=CREAM, bg=(0, 0, 0, 150), border=YELLOW + (255,), tracking=4 * s, label="kicker")
    c.title3d(90 * s, "MARGIN", c.font(ANTON, 128), face_top=(255, 255, 255),
              face_bot=(226, 222, 214), side=(120, 110, 100), tracking=2 * s)
    c.title3d(234 * s, "TRADING", c.font(ANTON, 128), face_top=(255, 222, 92),
              face_bot=(240, 160, 30), side=(150, 80, 10), tracking=2 * s)

    # Bottom block, over the black gradient
    c.text(H - 196 * s, "Chandler explains.  Joey... tries.", c.font(MARKER, 40), GOLD,
           tracking=0.5 * s, label="tagline", glow=(255, 150, 40))
    c.text(H - 128 * s, "PS5s, GTA 6 & a lesson in trading", c.font(MONT, 25, 600), CREAM,
           tracking=1 * s, label="sub")
    c.pill(H - 78 * s, "SWIPE  TO  LEARN   →", c.font(MONT, 22, 800),
           fg=(20, 14, 8), bg=YELLOW + (255,), border=YELLOW + (255,), tracking=3 * s, label="swipe")
    c.save(out)
    print("saved", out, c.base.size)


if __name__ == "__main__":
    {"cover": cover}[sys.argv[1]](*sys.argv[2:])
