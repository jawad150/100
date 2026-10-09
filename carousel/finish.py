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

import design as ui
from design import (F_BLUE, F_GREEN, F_ORANGE, F_PURPLE, F_RED, F_YELLOW, GWFF, INK, MINUS,
                    Rich, footer, glass, rrect_mask)

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

    # Friends split tone: Monica-purple shadows, warm peephole-yellow highlights
    sh = np.clip(1 - lum * 2.2, 0, 1)[..., None]
    hi = np.clip(lum * 1.6 - 0.6, 0, 1)[..., None]
    a = a + sh * np.array([0.020, -0.008, 0.042]) + hi * np.array([0.045, 0.028, -0.035])

    # Lift blacks slightly (filmic), roll off whites
    a = 0.015 + a * 0.975
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))

    # Bloom: blurred highlights screened back on
    W, H = out.size
    bright = out.point(lambda v: max(0, v - 185) * 3)
    bloom = bright.filter(ImageFilter.GaussianBlur(W * 0.018))
    out = ImageChops.screen(out, bloom.point(lambda v: int(v * 0.55)))

    # Film halation: warm red-orange glow bleeding around bright highlights
    hal = out.convert("L").point(lambda v: max(0, v - 200) * 4).filter(ImageFilter.GaussianBlur(W * 0.006))
    hal_rgb = Image.merge("RGB", (hal, hal.point(lambda v: int(v * 0.42)), hal.point(lambda v: int(v * 0.18))))
    out = ImageChops.screen(out, hal_rgb.point(lambda v: int(v * 0.45)))

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
    g = rng.normal(0, 3.4, (H, W)).astype(np.float32)
    g2 = np.asarray(Image.fromarray((rng.normal(128, 30, (H // 2, W // 2))).clip(0, 255).astype(np.uint8))
                    .resize((W, H), Image.BICUBIC), np.float32) - 128   # clumpier film grain
    o = np.clip(o + (g + g2 * 0.09)[..., None], 0, 255)
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
def subject_mask(raw_path):
    """Foreground (characters + props) mask, cached next to the raw render."""
    raw_path = Path(raw_path)
    cache = raw_path.with_name(raw_path.stem + "_mask.png")
    if not cache.exists():
        from rembg import new_session, remove
        im = Image.open(raw_path).convert("RGB")
        remove(im, session=new_session("birefnet-general"), only_mask=True).save(cache)
    return Image.open(cache).convert("L")


class Canvas:
    """Two text planes: `behind` (occluded by the subject = masking text) and `front`."""

    def __init__(self, img, subject=None):
        self.bg = img.convert("RGBA")
        self.W, self.H = self.bg.size
        self.s = self.W / 1080  # design grid is 1080 wide
        self.behind = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        self.front = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        self.subject = subject
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

    def _paste(self, layer, plane):
        setattr(self, plane, Image.alpha_composite(getattr(self, plane), layer))

    def _shift(self, im, dx, dy):
        out = Image.new(im.mode, im.size, 0)
        out.paste(im, (int(round(dx)), int(round(dy))))
        return out

    def _glyph_mask(self, txt, font, tracking, dot_gap=0, dots=False):
        """Render text at origin; return mask, dot centres, ink bbox."""
        m = Image.new("L", self.bg.size, 0)
        d = ImageDraw.Draw(m)
        x, specs = 0.0, []
        asc, _ = font.getmetrics()
        pad = self.H * 0.25  # keep ascenders inside the canvas
        hb = font.getbbox("H")
        wi = 0
        fb = self._fallback(font)
        for i, c in enumerate(txt):
            if fb and c in fb[0]:
                ffont, yoff, kern = fb[1], fb[2], fb[3]
                x += kern if c == "'" else 0
                d.text((x, pad + yoff), c, font=ffont, fill=255)
                x += ffont.getlength(c) + (kern if c == "'" else 0)
                if i < len(txt) - 1:
                    x += tracking
                continue
            if dots == "words" and c == " ":
                gapw = font.getlength(" ") + font.size * 0.30
                if i == 0 or txt[i - 1] not in ".,!?:":
                    specs.append([x + gapw / 2 - tracking / 2, pad + (hb[1] + hb[3]) / 2, DOTS[wi % 3]])
                    wi += 1
                else:
                    gapw = font.getlength(" ") + font.size * 0.12
                x += gapw + tracking
                continue
            d.text((x, pad), c, font=font, fill=255)
            x += font.getlength(c)
            if i < len(txt) - 1:
                if dots is True and c != " " and txt[i + 1] != " ":
                    specs.append([x + (tracking + dot_gap) / 2, pad + asc * 0.84, DOTS[i % 3]])
                x += tracking + (dot_gap if dots is True else 0)
        return m, specs, m.getbbox()

    def _fallback(self, font):
        """Gabriel Weiss' Friends draws '5' like an S and a tiny apostrophe:
        take those from Permanent Marker, scaled to the same cap height."""
        path = getattr(font, "path", "")
        if "GabrielWeiss" not in str(path):
            return None
        key = font.size
        cache = self.__dict__.setdefault("_fb", {})
        if key not in cache:
            g = font.getbbox("H")
            probe = ImageFont.truetype(ui.MARKER, 100)
            m = probe.getbbox("H")
            size = max(1, int(round(100 * (g[3] - g[1]) / (m[3] - m[1]))))
            mk = ImageFont.truetype(ui.MARKER, size)
            mb = mk.getbbox("H")
            cache[key] = ("5'", mk, g[1] - mb[1], font.size * 0.06)
        return cache[key]

    # -- measuring helpers (for layout) ------------------------------
    def ink_height(self, txt, font, tracking=0):
        _, _, b = self._glyph_mask(txt, font, tracking)
        return b[3] - b[1]

    # -- flat text with soft shadow ---------------------------------
    def text(self, top, txt, font, fill, tracking=0, shadow=0.85, label=None, glow=None,
             plane="front"):
        """Draw text whose INK top sits at `top`, centred on its ink box."""
        s = self.s
        m, _, b = self._glyph_mask(txt, font, tracking)
        dx = (self.W - (b[2] - b[0])) / 2 - b[0]
        dy = top - b[1]
        m = self._shift(m, dx, dy)
        box = m.getbbox()
        self._claim(box, label or txt)
        if shadow:
            sh = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
            sh.putalpha(self._shift(m, 3 * s, 4 * s).filter(ImageFilter.GaussianBlur(6 * s))
                        .point(lambda v: int(v * shadow)))
            self._paste(sh, plane)
        if glow:
            gl = Image.new("RGBA", self.bg.size, glow + (0,))
            gl.putalpha(m.filter(ImageFilter.GaussianBlur(14 * s)).point(lambda v: int(v * 0.5)))
            self._paste(gl, plane)
        face = Image.new("RGBA", self.bg.size, fill + (0,))
        face.putalpha(m)
        self._paste(face, plane)
        return box

    # -- extruded 3D headline ---------------------------------------
    def title3d(self, top, txt, font, face_top, face_bot, side, tracking=0, dots=True,
                depth=16, label=None, plane="behind"):
        """3D headline: face ink top at `top`; face+extrusion mass centred horizontally."""
        W, s = self.W, self.s
        dot_gap = font.size * 0.15 if dots is True else 0
        mask, specs, b = self._glyph_mask(txt, font, tracking, dot_gap, dots)
        dep = int(depth * s)
        dx = (W - (b[2] - b[0] + dep)) / 2 - b[0]
        dy = top - b[1]
        mask = self._shift(mask, dx, dy)
        for sp in specs:
            sp[0] += dx
            sp[1] += dy
        bbox = mask.getbbox()
        self._claim((bbox[0], bbox[1], bbox[2] + dep, bbox[3] + dep), label or txt)

        sh = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        sh.putalpha(self._shift(mask, dep * 1.2, dep * 1.6)
                    .filter(ImageFilter.GaussianBlur(10 * s)).point(lambda v: int(v * 0.85)))
        self._paste(sh, plane)

        ext = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        for k in range(dep, 0, -1):
            t = k / dep
            col = tuple(int(c * (0.30 + 0.45 * (1 - t))) for c in side) + (255,)
            ext.paste(Image.new("RGBA", self.bg.size, col), (0, 0), self._shift(mask, k, k))
        self._paste(ext, plane)

        top_y, bot_y = bbox[1], bbox[3]
        grad = np.zeros((self.H, 1, 3), np.float32)
        yy = np.clip((np.arange(self.H) - top_y) / max(1, bot_y - top_y), 0, 1)[:, None]
        grad[:, 0, :] = np.array(face_top) * (1 - yy) + np.array(face_bot) * yy
        face = Image.fromarray(np.repeat(grad, W, 1).astype(np.uint8)).convert("RGBA")
        face.putalpha(mask)
        self._paste(face, plane)

        edge = ImageChops.subtract(mask, self._shift(mask, 2 * s, 2 * s))
        hl = Image.new("RGBA", self.bg.size, (255, 255, 255, 0))
        hl.putalpha(edge.point(lambda v: int(v * 0.75)))
        self._paste(hl, plane)

        # Glossy sphere dots
        lay = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        dsh = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(dsh)
        r = font.size * (0.07 if dots == "words" else 0.05)
        for cx, cy, col in specs:
            dark = tuple(int(c * 0.45) for c in col)
            o = dep * 0.3
            sd.ellipse([cx - r + o, cy - r + o, cx + r + o, cy + r + o], fill=(0, 0, 0, 170))
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
        self._paste(dsh.filter(ImageFilter.GaussianBlur(3 * s)), plane)
        self._paste(lay, plane)
        return (bbox[0], bbox[1], bbox[2] + dep, bbox[3] + dep)

    # -- pill (rounded tag behind small text) -------------------------
    def pill(self, top, txt, font, fg, bg, border, pad=(28, 14), tracking=0, label=None,
             plane="front"):
        """Pill whose OUTER top is `top`; text optically centred inside by ink box."""
        s = self.s
        m, _, b = self._glyph_mask(txt, font, tracking)
        tw, th = b[2] - b[0], b[3] - b[1]
        pw, ph = pad[0] * s, pad[1] * s
        box = (round((self.W - tw) / 2 - pw), round(top),
               round((self.W + tw) / 2 + pw), round(top + th + 2 * ph))
        self._claim(box, label or txt)
        lay = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle(box, radius=(box[3] - box[1]) / 2, fill=bg,
                                              outline=border, width=max(2, int(2.5 * s)))
        self._paste(lay, plane)
        m = self._shift(m, (self.W - tw) / 2 - b[0], top + ph - b[1])
        face = Image.new("RGBA", self.bg.size, fg + (0,))
        face.putalpha(m)
        self._paste(face, plane)
        return box

    # -- small glossy sphere (bullets, footer, dividers) ---------------
    def sphere(self, cx, cy, r, col, plane="front"):
        lay = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        dark = tuple(int(c * 0.45) for c in col)
        steps = 12
        for k in range(steps):
            t = k / (steps - 1)
            rr = r * (1 - 0.82 * t)
            ox = oy = -r * 0.38 * t
            if t < 0.5:
                cc = tuple(int(dk + (c - dk) * t * 2) for dk, c in zip(dark, col))
            else:
                cc = tuple(int(c + (255 - c) * (t - 0.5) * 0.7) for c in col)
            d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=cc)
        hr = r * 0.17
        d.ellipse([cx - r * 0.42 - hr, cy - r * 0.42 - hr, cx - r * 0.42 + hr, cy - r * 0.42 + hr],
                  fill=(255, 255, 255, 235))
        self._paste(lay, plane)

    # -- rich text --------------------------------------------------
    STYLES = {
        "n": (CREAM, 520),
        "b": (GOLD, 800),
        "g": ((96, 222, 128), 800),
        "r": ((255, 104, 92), 800),
    }

    def _tokens(self, markup):
        """**gold**  ++green++  ~~red~~ ; '\\n' = paragraph break.
        Returns paragraphs of units; a unit is a list of (text, style) segments
        that must stay together (e.g. a highlighted word and the full stop after it)."""
        import re
        markup = re.sub(r"Rs\. (?=\d)", "Rs.\u00a0", markup)
        out = []
        for para in markup.split("\n"):
            units, glue = [], False
            for part in re.split(r"(\*\*.+?\*\*|\+\+.+?\+\+|~~.+?~~)", para):
                if not part:
                    continue
                st = "n"
                if part.startswith("**"):
                    st, part = "b", part[2:-2]
                elif part.startswith("++"):
                    st, part = "g", part[2:-2]
                elif part.startswith("~~"):
                    st, part = "r", part[2:-2]
                words = part.split(" ")
                for i, w in enumerate(words):
                    if not w:
                        continue
                    if i == 0 and glue and units:
                        units[-1].append((w, st))
                    else:
                        units.append([(w, st)])
                glue = not part.endswith(" ")
            out.append(units)
        return out

    def _fonts(self, size):
        return {k: self.font(MONT, size, w) for k, (_, w) in self.STYLES.items()}

    def _wrap(self, markup, size, max_w):
        fonts = self._fonts(size)
        space = fonts["n"].getlength(" ")
        paras = []
        for units in self._tokens(markup):
            lines, cur, cur_w = [], [], 0.0
            for u in units:
                segs = [(t, st, fonts[st].getlength(t)) for t, st in u]
                uw = sum(x[2] for x in segs)
                add = uw + (space if cur else 0)
                if cur and cur_w + add > max_w:
                    lines.append((cur, cur_w))
                    cur, cur_w, add = [], 0.0, uw
                cur.append(segs)
                cur_w += add
            if cur:
                lines.append((cur, cur_w))
            paras.append(lines)
        return paras, fonts, space

    def paragraph_height(self, markup, size, max_w, lh=1.38, pgap=0.55):
        paras, _, _ = self._wrap(markup, size, max_w * self.s)
        n = sum(len(p) for p in paras)
        L = size * self.s * lh
        return n * L + (len(paras) - 1) * L * pgap - (L - size * self.s * 1.02)

    def paragraph(self, top, markup, size, max_w, lh=1.38, pgap=0.55, label="body",
                  align="center", x0=None, plane="front"):
        s = self.s
        paras, fonts, space = self._wrap(markup, size, max_w * s)
        L = size * s * lh
        lay = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        asc = fonts["n"].getmetrics()[0]
        cap_off = asc - size * s * 0.74  # put the cap-height top at `top`
        y = top - cap_off
        for pi, lines in enumerate(paras):
            for units, w in lines:
                x = (self.W - w) / 2 if align == "center" else x0
                for segs in units:
                    for wd, st, ww in segs:
                        d.text((x, y), wd, font=fonts[st], fill=self.STYLES[st][0])
                        x += ww
                    x += space
                y += L
            y += L * pgap
        box = lay.getbbox()
        self._claim(box, label)
        a = lay.getchannel("A")
        sh = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        sh.putalpha(self._shift(a, 2 * s, 3 * s).filter(ImageFilter.GaussianBlur(5 * s))
                    .point(lambda v: int(v * 0.9)))
        self._paste(sh, plane)
        self._paste(lay, plane)
        return box

    def card(self, box, plane="front"):
        s = self.s
        lay = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle(box, radius=28 * s, fill=(10, 7, 5, 150),
                                              outline=(255, 198, 55, 110), width=max(2, int(2 * s)))
        self._paste(lay.filter(ImageFilter.GaussianBlur(0.6 * s)), plane)

    # -- footer -----------------------------------------------------
    def footer(self, page, total, arrow=True):
        s = self.s
        f = self.font(MONT, 19, 700)
        y = self.H - 46 * s - self.ink_height("MARGIN", f)
        lay = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        left = "MARGIN  TRADING  101"
        right = f"{page:02d} / {total:02d}" + ("   \u2192" if arrow else "")
        m, _, b = self._glyph_mask(left, f, 2 * s)
        lm = self._shift(m, 72 * s - b[0], y - b[1])
        m2, _, b2 = self._glyph_mask(right, f, 2 * s)
        rm = self._shift(m2, self.W - 72 * s - b2[2], y - b2[1])
        both = ImageChops.lighter(lm, rm)
        box = both.getbbox()
        self._claim((0, box[1], self.W, box[3]), "footer")
        face = Image.new("RGBA", self.bg.size, CREAM + (0,))
        face.putalpha(both.point(lambda v: int(v * 0.85)))
        self._paste(face, "front")
        cy = (box[1] + box[3]) / 2
        for i, col in enumerate(DOTS):
            self.sphere(self.W / 2 + (i - 1) * 26 * s, cy, 7 * s, col)
        return box

    def render(self):
        out = Image.alpha_composite(self.bg, self.behind)
        if self.subject is not None:
            s = self.s
            # Soft contact shadow of the subject falling onto the masked text
            text_a = np.asarray(self.behind.getchannel("A"), np.float32) / 255
            sub = self._shift(self.subject, -6 * s, 10 * s).filter(ImageFilter.GaussianBlur(14 * s))
            sh_a = (np.asarray(sub, np.float32) / 255) * text_a * 0.55
            sh = Image.new("RGBA", self.bg.size, (0, 0, 0, 0))
            sh.putalpha(Image.fromarray((sh_a * 255).astype(np.uint8)))
            out = Image.alpha_composite(out, sh)
            # Subject back on top of the text (feathered edge)
            bb = self.behind.getchannel("A").getbbox()
            if bb:
                zone = Image.new("L", self.bg.size, 0)
                ImageDraw.Draw(zone).rectangle([0, 0, self.W, bb[3] + int(40 * s)], fill=255)
                fg = self.bg.copy()
                fg.putalpha(ImageChops.multiply(self.subject.filter(ImageFilter.GaussianBlur(1.2 * s)), zone))
                out = Image.alpha_composite(out, fg)
        return Image.alpha_composite(out, self.front)

    def save(self, out):
        self.render().convert("RGB").save(out, quality=95, subsampling=0)


# ----------------------------------------------------------------- layout
TOTAL = 10
TOP_MARGIN_G = 50
DEPTH_G = 13
GAP_G = 22
MARGIN_G = 72
FACES = [((255, 255, 255), (232, 226, 236), (92, 58, 150)),    # white face, purple side
         ((255, 226, 70), (255, 176, 20), (150, 84, 10))]      # Friends yellow


def _subject_top(sub_np, x0, x1, H):
    cols = sub_np[:, max(0, int(x0)):int(x1)]
    rows = np.where(cols[int(H * 0.12):].any(1))[0]
    return rows[0] + int(H * 0.12) if len(rows) else H


def detect_faces(img):
    """Face boxes (x0, y0, x1, y1) in image pixels, used to keep panels off faces."""
    try:
        import cv2
    except ImportError:
        return []
    g = np.asarray(img.convert("L"))
    sc = 0.5
    small = cv2.resize(g, None, fx=sc, fy=sc)
    out = []
    for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
        cas = cv2.CascadeClassifier(cv2.data.haarcascades + name)
        for flip in (False, True) if "profile" in name else (False,):
            im = cv2.flip(small, 1) if flip else small
            for (x, y, w, h) in cas.detectMultiScale(im, 1.1, 6, minSize=(100, 100)):
                if flip:
                    x = im.shape[1] - x - w
                out.append((x / sc, y / sc, (x + w) / sc, (y + h) / sc))
    return out


def headline(c, kicker, lines, subject, dots="words", spec_max=108):
    """Tape kicker + stacked 3D Friends-font headline. Last line is masked by the
    subject when that reads cleanly; otherwise the headline sits in front."""
    s, W, H = c.s, c.W, c.H
    kimg = ui.kicker_img(c, kicker).rotate(-2.0, resample=Image.BICUBIC, expand=True)
    kicker_h = kimg.size[1]
    dep, gap, top_m = DEPTH_G * s, GAP_G * s, TOP_MARGIN_G * s
    sub_np = np.asarray(subject) > 128
    tr = 1.5 * s

    def lw(ln, f):
        b = c._glyph_mask(ln, f, tr, 0, dots)[2]
        return b[2] - b[0] + dep

    def heights(f):
        return [(lambda b: b[3] - b[1])(c._glyph_mask(ln, f, tr, 0, dots)[2]) for ln in lines]

    def tops(f, first_top):
        hs, out, y = heights(f), [], first_top
        for h in hs:
            out.append(y)
            y += h + dep + gap
        return out

    def line_masks(f, cap, first_top):
        out = []
        for ln, t in zip(lines, tops(f, first_top)):
            m, _, b = c._glyph_mask(ln, f, tr, 0, dots)
            m = c._shift(m, (W - (b[2] - b[0] + dep)) / 2 - b[0], t - b[1])
            out.append(np.asarray(m) > 128)
        return out

    def reads_cleanly(masks, cap):
        band = max(4, int(cap * 0.45))
        for i, ink in enumerate(masks):
            limit = 0.16 if i == len(masks) - 1 else 0.10
            cols = np.where(ink.any(0))[0]
            for x in range(cols[0], cols[-1] + 1, band // 2):
                sl = ink[:, x:x + band]
                tot = sl.sum()
                if tot and (sl & sub_np[:, x:x + band]).sum() / tot > limit + 0.005:
                    return False
        return True

    plan = None
    for overlap in (0.26, 0.18, 0.10):
        for size in range(spec_max, 56, -2):
            f = c.font(GWFF, size)
            cap = c.ink_height("H", f)
            widths = [lw(ln, f) for ln in lines]
            if max(widths) > W - 2 * MARGIN_G * s:
                continue
            st = _subject_top(sub_np, (W - widths[-1]) / 2, (W + widths[-1]) / 2, H)
            hs = heights(f)
            first_top = st - hs[-1] * (1 - overlap) - sum(h + dep + gap for h in hs[:-1])
            kicker_top = first_top - gap * 1.2 - kicker_h
            if kicker_top < top_m:
                continue
            if reads_cleanly(line_masks(f, cap, first_top), cap):
                plan = (f, cap, kicker_top, first_top, "behind")
            break
        if plan:
            break
    if plan is None:
        for size in range(spec_max, 56, -2):
            f = c.font(GWFF, size)
            if all(lw(ln, f) <= W - 2 * MARGIN_G * s for ln in lines):
                break
        cap = c.ink_height("H", f)
        kicker_top = top_m
        plan = (f, cap, kicker_top, kicker_top + kicker_h + gap * 1.2, "front")
    f, cap, kicker_top, first_top, plane = plan

    ui.paste_center(c, kimg, W / 2, kicker_top + kicker_h / 2, label="kicker")
    bottom = 0
    for i, (ln, t) in enumerate(zip(lines, tops(f, first_top))):
        ft, fb, sd = FACES[i % 2] if len(lines) > 1 else FACES[1]
        box = c.title3d(t, ln, f, ft, fb, sd, tracking=tr,
                        dots=dots, depth=DEPTH_G, label=f"h{i}", plane=plane)
        bottom = box[3]
    print(f"  headline size {f.size / s:.0f}, plane {plane}")
    return bottom


def shift_down(img, mask, frac):
    """Move the scene down by `frac` of the height; extend the top with a blurred,
    darkened mirror of the top strip (it sits under the dark top gradient anyway)."""
    W, H = img.size
    dy = int(H * frac)
    img = img.convert("RGB")
    out = Image.new("RGB", (W, H))
    out.paste(img, (0, dy))
    strip = img.crop((0, 0, W, dy)).transpose(Image.FLIP_TOP_BOTTOM)
    strip = strip.filter(ImageFilter.GaussianBlur(W * 0.02)).point(lambda v: int(v * 0.6))
    out.paste(strip, (0, 0))
    m = Image.new("L", (W, H), 0)
    m.paste(mask, (0, dy))
    return out, m


def check_faces(c, faces, names):
    """Fail loudly if any panel / sticker / bubble covers more than a sliver of a face."""
    bad = []
    for fx0, fy0, fx1, fy1 in faces:
        fa = (fx1 - fx0) * (fy1 - fy0)
        for b, l in c.boxes:
            if l not in names:
                continue
            ix = max(0, min(fx1, b[2]) - max(fx0, b[0]))
            iy = max(0, min(fy1, b[3]) - max(fy0, b[1]))
            if ix * iy / fa > 0.12:
                bad.append((l, round(ix * iy / fa, 2), [int(v) for v in (fx0, fy0, fx1, fy1)]))
    return bad


def content_slide(spec, raw, out):
    subject = subject_mask(raw)
    img = Image.open(raw)
    if spec.get("shift"):
        img, subject = shift_down(img, subject, spec["shift"])
    faces = detect_faces(img)
    c = Canvas(grade(img), subject)
    s, W, H = c.s, c.W, c.H
    X0, X1 = MARGIN_G * s, W - MARGIN_G * s
    PADX, AV, AVJ = 44 * s, 104 * s, 92 * s
    rich = Rich(c, spec.get("size", 34))
    text_w = (X1 - X0) - 2 * PADX

    # ---- measure the content of the glass card
    f_term, f_mean = c.font(ui.MONT, 30, 800), c.font(ui.MONT, 30, 560)
    capT = f_term.getbbox("H")[3] - f_term.getbbox("H")[1]
    row_h = spec.get("row_h", 58) * s
    bullet_gap = 22 * s
    if "body" in spec:
        content_h = rich.height(spec["body"], text_w)
    elif "rows" in spec:
        content_h = (len(spec["rows"]) - 1) * row_h + capT
    else:
        content_h = sum(rich.height(b, text_w - 46 * s) for _, b in spec["bullets"]) \
            + bullet_gap * (len(spec["bullets"]) - 1) + rich.L * 0.0
    f_disc = c.font(ui.MONT, 21, 560)
    disc_h = (f_disc.getbbox("H")[3] - f_disc.getbbox("H")[1] + 30 * s) if spec.get("disclaimer") else 0
    pad_top, pad_bot = AV / 2 + spec.get("pad_top", 30) * s, spec.get("pad_bot", 40) * s
    card_h = pad_top + content_h + disc_h + pad_bot

    # ---- vertical stack, bottom-up: footer, Joey's reply, Chandler's card
    footer_top = H - 50 * s - 14 * s
    jpos = spec.get("joey_pos")
    bub = None
    if spec.get("joey") and not jpos:
        bub = ui.bubble_img(c, spec["joey"], 640 - AVJ / s, tail="right")
    if bub is not None:
        joey_h = max(bub.size[1], AVJ)
        joey_bottom = footer_top - 40 * s
        joey_top = joey_bottom - joey_h
        card_bottom = joey_top + 30 * s   # bubble overlaps the card edge like a pop-up
    else:
        card_bottom = footer_top - 44 * s
    card_top = card_bottom - card_h

    c.bg = scrims(c.bg, top_frac=0.42, top_alpha=230,
                  bot_frac=min(0.78, (H - card_top + 220 * s) / H), bot_alpha=200).convert("RGBA")
    head_bottom = headline(c, spec["kicker"], spec["lines"], subject)
    if card_top - AV / 2 < head_bottom + 18 * s:
        raise RuntimeError(f"card collides with headline on slide {spec['page']} "
                           f"(card top {card_top:.0f}, headline bottom {head_bottom:.0f})")

    # ---- glass card + Chandler avatar / name tag
    glass(c, rrect_mask((W, H), (X0, card_top, X1, card_bottom), 38 * s))
    c._claim((int(X0), int(card_top), int(X1), int(card_bottom)), "card")
    c.boxes.pop()  # the card hosts text; keep it out of the overlap set, check faces separately
    av_cx = X0 + PADX + AV / 2 - 6 * s
    ui.paste_center(c, ui.avatar_img(c, "chandler", AV, F_YELLOW, F_PURPLE), av_cx, card_top, label="avatar")
    tag = ui.name_tag_img(c, "CHANDLER", F_YELLOW, INK)
    ui.paste_center(c, tag, av_cx + AV / 2 + 14 * s + tag.size[0] / 2, card_top, label="nametag")
    if spec.get("sticker"):
        st = spec["sticker"]
        im = ui.sticker_img(c, st["kind"], st["lines"], st.get("color"))
        if st.get("scale"):
            im = im.resize((int(im.size[0] * st["scale"]), int(im.size[1] * st["scale"])), Image.LANCZOS)
        ang = st.get("angle", 7)
        rw = im.rotate(ang, expand=True).size
        cy_st = min(card_top - 8 * s, card_top + pad_top - 14 * s - rw[1] / 2)
        cx_st = X1 - rw[0] / 2 + 18 * s
        if st.get("pos"):
            cx_st, cy_st = st["pos"][0] * W, st["pos"][1] * H
        ui.paste_center(c, im, cx_st, cy_st, angle=ang, label="sticker")

    # ---- card content
    tx, ty = X0 + PADX, card_top + pad_top
    if "body" in spec:
        rich.draw(tx, ty, spec["body"], text_w)
    elif "rows" in spec:
        col_w = max(f_term.getlength(a) for a, _ in spec["rows"])
        lay = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        hbT = f_term.getbbox("H")
        for i, (a, b) in enumerate(spec["rows"]):
            yy = ty + i * row_h - hbT[1]
            d.text((tx, yy), a, font=f_term, fill=F_YELLOW + (255,))
            d.text((tx + col_w + 26 * s, yy), "→", font=f_mean, fill=(255, 255, 255, 150))
            d.text((tx + col_w + 74 * s, yy), b, font=f_mean, fill=(255, 255, 255, 255))
            if i:
                ly = ty + i * row_h - (row_h - capT) / 2
                d.line([(tx, ly), (X1 - PADX, ly)], fill=(255, 255, 255, 38), width=max(1, int(1.5 * s)))
        c._claim(lay.getchannel("A").getbbox(), "rows")
        c._paste(lay, "front")
    else:
        yy = ty
        for i, (col, mk) in enumerate(spec["bullets"]):
            c.sphere(tx + 12 * s, yy + rich.px * 0.36, 12 * s, col)
            rich.draw(tx + 46 * s, yy, mk, text_w - 46 * s, label=f"b{i}")
            yy += rich.height(mk, text_w - 46 * s) + bullet_gap
    if spec.get("disclaimer"):
        d_top = card_bottom - pad_bot - (f_disc.getbbox("H")[3] - f_disc.getbbox("H")[1])
        lay = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((tx, d_top - f_disc.getbbox("H")[1]), spec["disclaimer"], font=f_disc,
                                 fill=(255, 255, 255, 215))
        c._claim(lay.getchannel("A").getbbox(), "disclaimer")
        c._paste(lay, "front")

    # ---- Joey's reply bubble + avatar (right-aligned to the margin)
    if bub is not None:
        cy = joey_bottom - AVJ / 2
        jx = X1 - AVJ / 2
        ui.paste_center(c, ui.avatar_img(c, "joey", AVJ, F_BLUE, F_ORANGE), jx, cy, label="joey_avatar")
        jt = ui.name_tag_img(c, "JOEY", F_BLUE, (255, 255, 255))
        ui.paste_center(c, jt, jx, cy + AVJ / 2 + 2 * s, label="joey_tag", claim=False)
        bx1 = X1 - AVJ - 12 * s
        bcy = min(cy, joey_bottom - bub.size[1] / 2) + 3 * s
        ui.paste_center(c, bub, bx1 - bub.size[0] / 2 + 3 * s, bcy, label="joey_bubble")

    if jpos:  # speech-bubble pop-up right next to Joey, tail pointing at him
        pb = ui.bubble_img(c, spec["joey"], 480, tail="down")
        ui.paste_center(c, pb, jpos[0] * W, jpos[1] * H, label="joey_bubble")

    footer(c, spec["page"], TOTAL)
    c.boxes.append(((int(X0), int(card_top), int(X1), int(card_bottom)), "card"))
    bad = check_faces(c, faces, {"card", "sticker", "joey_bubble", "avatar", "nametag", "joey_avatar"})
    for b in bad:
        print("  WARNING face covered:", b)
    c.save(out)
    print("saved", out)


def cover(raw, out):
    subject = subject_mask(raw)
    img = Image.open(raw)
    faces = detect_faces(img)
    c = Canvas(grade(img), subject)
    s, W, H = c.s, c.W, c.H
    X0, X1 = MARGIN_G * s, W - MARGIN_G * s
    AV = 112 * s

    # ---- bottom stack: footer, swipe pill, glass card
    f_tag = c.font(GWFF, 50)
    f_sub = c.font(ui.MONT, 26, 600)
    capg = c.ink_height("Chandler", f_tag)
    caps = f_sub.getbbox("H")[3] - f_sub.getbbox("H")[1]
    footer_top = H - 50 * s - 14 * s
    f_sw = c.font(ui.MONT, 21, 900)
    sw_txt = "SWIPE  TO  LEARN  →"
    tr = 3 * s
    sw_w = sum(f_sw.getlength(ch) for ch in sw_txt) + tr * (len(sw_txt) - 1)
    hb = f_sw.getbbox("H")
    pill_w, pill_h = int(sw_w + 64 * s), int((hb[3] - hb[1]) + 34 * s)
    sw_bottom = footer_top - 34 * s
    sw_top = sw_bottom - pill_h
    card_bottom = sw_top - 34 * s
    card_h = AV / 2 + 30 * s + capg + 26 * s + caps + 42 * s
    card_top = card_bottom - card_h
    c.bg = scrims(c.bg, top_frac=0.46, top_alpha=235,
                  bot_frac=min(0.6, (H - card_top + 200 * s) / H), bot_alpha=205).convert("RGBA")

    # ---- title: Friends-font, logo-style letter dots, masked by the subject
    kimg = ui.kicker_img(c, "A  BEGINNER'S  GUIDE  TO").rotate(-2.0, resample=Image.BICUBIC, expand=True)
    gap = 26 * s
    sub_np = np.asarray(subject) > 128
    rows = np.where(sub_np[:, int(W * 0.25):int(W * 0.75)].any(1))[0]
    subject_top = rows[0]
    for size in range(170, 90, -2):
        f_title = c.font(GWFF, size)
        hM = c._glyph_mask("MARGIN", f_title, 2 * s, f_title.size * 0.15, True)[2]
        hT = c._glyph_mask("TRADING", f_title, 2 * s, f_title.size * 0.15, True)[2]
        trading_top = subject_top - (hT[3] - hT[1]) * 0.78
        margin_top = trading_top - (DEPTH_G + 3) * s - gap - (hM[3] - hM[1])
        kicker_top = margin_top - gap * 1.2 - kimg.size[1]
        b = c._glyph_mask("TRADING", f_title, 2 * s, f_title.size * 0.15, True)[2]
        if kicker_top >= TOP_MARGIN_G * s and (b[2] - b[0]) + DEPTH_G * s <= W - 2 * MARGIN_G * s:
            break
    ui.paste_center(c, kimg, W / 2, kicker_top + kimg.size[1] / 2, label="kicker")
    c.title3d(margin_top, "MARGIN", f_title, *FACES[0], tracking=2 * s, depth=DEPTH_G + 3)
    c.title3d(trading_top, "TRADING", f_title, *FACES[1], tracking=2 * s, depth=DEPTH_G + 3)

    # ---- glass card with both avatars on its top edge
    glass(c, rrect_mask((W, H), (X0, card_top, X1, card_bottom), 38 * s))
    ui.paste_center(c, ui.avatar_img(c, "chandler", AV, F_YELLOW, F_PURPLE), W / 2 - AV * 0.42, card_top,
                    label="av_c")
    c.boxes.pop()
    ui.paste_center(c, ui.avatar_img(c, "joey", AV, F_BLUE, F_ORANGE), W / 2 + AV * 0.42, card_top,
                    label="av_j")
    c.text(card_top + AV / 2 + 30 * s, "Chandler explains. Joey... tries.", f_tag, F_YELLOW,
           tracking=1 * s, label="tagline", glow=(255, 140, 30))
    c.text(card_top + AV / 2 + 30 * s + capg + 26 * s, "PS5s, GTA 6 & a lesson in trading", f_sub,
           (255, 255, 255), tracking=1 * s, label="sub", shadow=0.5)

    # ---- swipe pill (comic pop)
    pill = ui.local_rrect(pill_w, pill_h, pill_h / 2, F_YELLOW + (255,), INK + (255,), 3 * s)
    d = ImageDraw.Draw(pill)
    x = (pill_w - sw_w) / 2
    for ch in sw_txt:
        d.text((x, (pill_h - (hb[3] - hb[1])) / 2 - hb[1]), ch, font=f_sw, fill=INK + (255,))
        x += f_sw.getlength(ch) + tr
    ui.paste_center(c, ui.hard_shadow(pill, 5 * s, 6 * s), W / 2 + 2.5 * s, sw_top + pill_h / 2 + 3 * s,
                    label="swipe")
    footer(c, 1, TOTAL)
    c.boxes.append(((int(X0), int(card_top), int(X1), int(card_bottom)), "card"))
    for b in check_faces(c, faces, {"card", "swipe", "av_j"}):
        print("  WARNING face covered:", b)
    c.save(out)
    print("saved", out)


SLIDES = {
    2: dict(kicker="THE  SETUP", lines=["A PS5 COSTS", "RS. 200,000"],
            body="That's the price **today**.\nBut I think **GTA 6** is coming soon, "
                 "so PS5 prices will ++rise++.",
            sticker=dict(kind="burst", lines=["GTA 6", "HYPE!"], color=F_YELLOW, angle=8, scale=0.85),
            joey="Wait... it gets MORE expensive?"),
    3: dict(kicker="THE  DEAL", lines=["THE TOKEN", "MONEY"],
            body="I pay a token amount of **Rs. 10,000** as **margin** "
                 "to lock the PS5 at **Rs. 200,000**.\n"
                 "**30 days from now**, I buy the PS5 for **Rs. 200,000**.",
            sticker=dict(kind="calendar", lines=["EXPIRY", "30", "DAYS"], angle=6),
            joey="So you paid for a PS5... and didn't get a PS5?"),
    4: dict(kicker="SCENARIO  1", lines=["GTA 6", "RELEASES!"],
            body="30 days later, the PS5 goes up to ++Rs. 220,000++.\n"
                 "I get it at **Rs. 200,000** and sell it at ++Rs. 220,000++. "
                 "And I only paid **Rs. 10,000** upfront.",
            sticker=dict(kind="burst", lines=["+Rs. 20,000", "PROFIT"], color=F_GREEN, angle=7,
                         scale=0.85, pos=(0.80, 0.14)),
            joey="We're rich! ...Right?"),
    5: dict(kicker="SCENARIO  2", lines=["GTA 6 GETS", "DELAYED"],
            body="30 days later, the PS5 drops to ~~Rs. 180,000~~.\n"
                 "I bought at **Rs. 200,000** and now sell at ~~Rs. 180,000~~, "
                 "so I bear a ~~loss of Rs. 20,000~~.",
            sticker=dict(kind="burst", lines=[MINUS + "Rs. 20,000", "LOSS"], color=F_RED, angle=-7,
                         scale=0.8),
            joey="Can we at least still play it?"),
    6: dict(kicker="THE  BIG  IDEA", lines=["WHAT DID CHANDLER", "ACTUALLY CREATE?"],
            body="A **margin\u00a0contract\u00a0/\u00a0trade**: a financial agreement to buy or sell "
                 "an asset at a __fixed price__ on a __future date__, by paying a "
                 "**small\u00a0upfront\u00a0amount**.",
            sticker=dict(kind="stamp", lines=["CONTRACT"], angle=-8),
            joey="Could you say that again... slower?"),
    7: dict(kicker="PLOT  TWIST", lines=["NOW REPLACE THE PS5", "WITH A COMMODITY"],
            body="People make similar agreements on the "
                 "**Pakistan Mercantile Exchange (PMEX)**.\nThis is called **Margin Trading**.",
            sticker=dict(kind="tag", lines=["PMEX", "PAKISTAN"], color=F_PURPLE, angle=7),
            joey="Wait. I can do this with GOLD?!"),
    8: dict(kicker="TERMS  USED  IN", shift=0.07, lines=["MARGIN TRADING"], row_h=50, pad_top=22, pad_bot=34,
            rows=[("PS5", "Underlying Asset"), ("Rs. 200,000", "Futures Price"),
                  ("Rs. 10,000", "Margin"), ("30 Days Later", "Expiry Date"),
                  ("Chandler's Deal", "Margin Trade")],
            sticker=dict(kind="tag", lines=["SHEET", "CHEAT"], color=F_YELLOW, angle=7),
            joey="Okay... and which one is the pizza?", joey_pos=(0.70, 0.285)),
    9: dict(kicker="THE  WHY", lines=["WHY DO PEOPLE", "TRADE ON MARGIN?"],
            bullets=[(F_GREEN, "They think prices will ++rise++."),
                     (F_RED, "They think prices will ~~fall~~."),
                     (F_YELLOW, "They want to **lock in today's price** and **reduce risk**.")],
            sticker=dict(kind="burst", lines=["3", "REASONS"], color=F_YELLOW, angle=8),
            joey="I'm on finger four. Is that bad?"),
    10: dict(kicker="THE  TAKEAWAY", lines=["THAT'S HOW MARGIN", "TRADING WORKS"],
             body="Margin trading lets you trade **futures contracts** by paying a small "
                  "upfront amount known as **Margin** or **Token Money**.",
             disclaimer="For education only. Margin trading carries a risk of loss.",
             sticker=dict(kind="burst", lines=["SAVE", "THIS!"], color=F_YELLOW, angle=8),
             joey="How you doin'? Now send this to your Joey!"),
}


def slide(n, raw, out):
    n = int(n)
    spec = dict(SLIDES[n], page=n)
    print(f"slide {n}")
    content_slide(spec, raw, out)


if __name__ == "__main__":
    {"cover": cover, "slide": slide}[sys.argv[1]](*sys.argv[2:])
