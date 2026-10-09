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
        for i, c in enumerate(txt):
            d.text((x, pad), c, font=font, fill=255)
            x += font.getlength(c)
            if i < len(txt) - 1:
                if dots and c != " " and txt[i + 1] != " ":
                    specs.append([x + (tracking + dot_gap) / 2, pad + asc * 0.84, DOTS[i % 3]])
                x += tracking + dot_gap
        return m, specs, m.getbbox()

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
        dot_gap = font.size * 0.15 if dots else 0
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
        r = font.size * 0.05
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
            fg = self.bg.copy()
            fg.putalpha(self.subject.filter(ImageFilter.GaussianBlur(1.2 * s)))
            out = Image.alpha_composite(out, fg)
        return Image.alpha_composite(out, self.front)

    def save(self, out):
        self.render().convert("RGB").save(out, quality=95, subsampling=0)


# ----------------------------------------------------------------- slides
def cover(raw, out):
    subject = subject_mask(raw)
    img = grade(Image.open(raw))
    img = scrims(img, top_frac=0.46, top_alpha=240, bot_frac=0.40, bot_alpha=252)
    c = Canvas(img, subject)
    s, W, H = c.s, c.W, c.H

    f_kick = c.font(MONT, 24, 800)
    DEPTH = 16
    gap = 30 * s  # identical rhythm between stacked headline rows
    TOP_MARGIN = 56 * s

    # Subject top = highest foreground pixel in the centre band
    sub_np = np.asarray(subject) > 128
    rows = np.where(sub_np[:, int(W * 0.25):int(W * 0.75)].any(1))[0]
    subject_top = rows[0]
    kicker_h = c.ink_height("A BEGINNER'S GUIDE TO", f_kick) + 2 * 14 * s

    # Auto-fit: largest headline whose stack fits between the top margin and the
    # subject (subject covers the lower ~26% of TRADING = masking text), and whose
    # width keeps a 72px side margin.
    for size in range(190, 100, -2):
        f_title = c.font(ANTON, size)
        cap = c.ink_height("TRADING", f_title, 2 * s)
        trading_top = subject_top - cap * 0.74
        margin_top = trading_top - DEPTH * s - gap - cap
        kicker_top = margin_top - gap - kicker_h
        m, _, b = c._glyph_mask("TRADING", f_title, 2 * s, f_title.size * 0.15, True)
        wide = (b[2] - b[0]) + DEPTH * s
        if kicker_top >= TOP_MARGIN and wide <= W - 2 * 72 * s:
            break
    print("title size", size)

    c.pill(kicker_top, "A  BEGINNER'S  GUIDE  TO", f_kick, fg=CREAM, bg=(0, 0, 0, 150),
           border=YELLOW + (255,), tracking=4 * s, label="kicker")
    c.title3d(margin_top, "MARGIN", f_title, face_top=(255, 255, 255),
              face_bot=(226, 222, 214), side=(120, 110, 100), tracking=2 * s, depth=DEPTH)
    c.title3d(trading_top, "TRADING", f_title, face_top=(255, 222, 92),
              face_bot=(240, 160, 30), side=(150, 80, 10), tracking=2 * s, depth=DEPTH)

    # Bottom block, built upward from a fixed bottom margin over the black gradient
    f_sw, f_sub, f_tag = c.font(MONT, 22, 800), c.font(MONT, 25, 600), c.font(MARKER, 42)
    bottom_margin, row_gap = 52 * s, 22 * s
    sw_h = c.ink_height("SWIPE TO LEARN", f_sw) + 2 * 14 * s
    sw_top = H - bottom_margin - sw_h
    sub_top = sw_top - row_gap * 1.3 - c.ink_height("PS5s, GTA 6 & a lesson in trading", f_sub)
    tag_top = sub_top - row_gap - c.ink_height("Chandler explains.  Joey... tries.", f_tag)

    c.text(tag_top, "Chandler explains.  Joey... tries.", f_tag, GOLD, tracking=0.5 * s,
           label="tagline", glow=(255, 150, 40))
    c.text(sub_top, "PS5s, GTA 6 & a lesson in trading", f_sub, CREAM, tracking=1 * s, label="sub")
    c.pill(sw_top, "SWIPE  TO  LEARN   \u2192", f_sw, fg=(20, 14, 8), bg=YELLOW + (255,),
           border=YELLOW + (255,), tracking=3 * s, label="swipe")
    c.save(out)
    print("saved", out, c.bg.size, "| subject top", subject_top, "| kicker top", round(kicker_top))


TOTAL = 10
TOP_MARGIN_G = 56
DEPTH_G = 16
GAP_G = 26
FACES = [((255, 255, 255), (226, 222, 214), (120, 110, 100)),   # white
         ((255, 222, 92), (240, 160, 30), (150, 80, 10))]      # gold


def _subject_top(sub_np, x0, x1, H):
    cols = sub_np[:, max(0, int(x0)):int(x1)]
    rows = np.where(cols[int(H * 0.12):].any(1))[0]
    return rows[0] + int(H * 0.12) if len(rows) else H


def headline(c, kicker, lines, subject):
    """Kicker pill + stacked 3D headline. Last line is masked by the subject
    when that reads cleanly; otherwise the headline sits in front."""
    s, W, H = c.s, c.W, c.H
    f_kick = c.font(MONT, 24, 800)
    kicker_h = c.ink_height(kicker, f_kick) + 2 * 14 * s
    dep, gap, top_m = DEPTH_G * s, GAP_G * s, TOP_MARGIN_G * s
    sub_np = np.asarray(subject) > 128

    def line_masks(f, cap, first_top):
        out = []
        for i, ln in enumerate(lines):
            m, _, b = c._glyph_mask(ln, f, 2 * s)
            m = c._shift(m, (W - (b[2] - b[0] + dep)) / 2 - b[0],
                         first_top + i * (cap + dep + gap) - b[1])
            out.append(np.asarray(m) > 128)
        return out

    def reads_cleanly(masks, cap):
        """Every glyph-sized column band of every line must stay mostly visible."""
        band = max(4, int(cap * 0.45))
        for i, ink in enumerate(masks):
            limit = 0.16 if i == len(masks) - 1 else 0.0
            cols = np.where(ink.any(0))[0]
            for x in range(cols[0], cols[-1] + 1, band // 2):
                sl = ink[:, x:x + band]
                tot = sl.sum()
                if tot and (sl & sub_np[:, x:x + band]).sum() / tot > limit + 0.005:
                    return False
        return True

    plan = None
    for overlap in (0.26, 0.18, 0.10):
        for size in range(150, 70, -2):
            f = c.font(ANTON, size)
            cap = c.ink_height("H", f)
            widths = [c._glyph_mask(ln, f, 2 * s)[2] for ln in lines]
            widths = [b[2] - b[0] + dep for b in widths]
            if max(widths) > W - 2 * 72 * s:
                continue
            lw = widths[-1]
            st = _subject_top(sub_np, (W - lw) / 2, (W + lw) / 2, H)
            first_top = st - cap * (1 - overlap) - (len(lines) - 1) * (cap + dep + gap)
            kicker_top = first_top - gap - kicker_h
            if kicker_top < top_m:
                continue
            if reads_cleanly(line_masks(f, cap, first_top), cap):
                plan = (f, cap, kicker_top, first_top, "behind")
            break
        if plan:
            break
    if plan is None:  # subject too high: stack from the top margin, text in front
        for size in range(130, 70, -2):
            f = c.font(ANTON, size)
            if all(c._glyph_mask(ln, f, 2 * s)[2][2] - c._glyph_mask(ln, f, 2 * s)[2][0] + dep
                   <= W - 2 * 72 * s for ln in lines):
                break
        cap = c.ink_height("H", f)
        kicker_top = top_m
        plan = (f, cap, kicker_top, kicker_top + kicker_h + gap, "front")
    f, cap, kicker_top, first_top, plane = plan

    c.pill(kicker_top, kicker, f_kick, fg=CREAM, bg=(0, 0, 0, 150), border=YELLOW + (255,),
           tracking=4 * s, label="kicker")
    bottom = 0
    for i, ln in enumerate(lines):
        ft, fb, sd = FACES[i % 2] if len(lines) > 1 else FACES[1]
        box = c.title3d(first_top + i * (cap + dep + gap), ln, f, ft, fb, sd, tracking=2 * s,
                        dots=False, depth=DEPTH_G, label=f"h{i}", plane=plane)
        bottom = box[3]
    print(f"  headline size {f.size / s:.0f}, plane {plane}")
    return bottom


def content_slide(spec, raw, out):
    subject = subject_mask(raw)
    c = Canvas(grade(Image.open(raw)), subject)
    s, W, H = c.s, c.W, c.H
    head_bottom = headline(c, spec["kicker"], spec["lines"], subject)

    # ---- bottom block, built upward from the footer
    fbox = c.footer(spec["page"], TOTAL, arrow=spec["page"] < TOTAL)
    y = fbox[1] - 40 * s
    if spec.get("disclaimer"):
        fd = c.font(MONT, 17, 500)
        h = c.ink_height(spec["disclaimer"], fd)
        c.text(y - h, spec["disclaimer"], fd, (200, 190, 175), label="disclaimer", shadow=0.6)
        y -= h + 26 * s
    if spec.get("cta"):
        fc = c.font(MONT, 22, 800)
        h = c.ink_height(spec["cta"], fc) + 2 * 14 * s
        c.pill(y - h, spec["cta"], fc, fg=(20, 14, 8), bg=YELLOW + (255,), border=YELLOW + (255,),
               tracking=3 * s, label="cta")
        y -= h + 34 * s

    if "body" in spec:
        size = spec.get("size", 33)
        bh = c.paragraph_height(spec["body"], size, 900)
        top = y - bh
        c.paragraph(top, spec["body"], size, 900)
        block_top = top
    elif "rows" in spec:
        fl, fr = c.font(MONT, 30, 800), c.font(MONT, 30, 520)
        row_h = 62 * s
        n = len(spec["rows"])
        top = y - 34 * s - n * row_h + (row_h - c.ink_height("H", fl))
        card_top = top - 40 * s
        lw = max(fl.getlength(a) for a, _ in spec["rows"])
        rw = max(fr.getlength(b) for _, b in spec["rows"])
        mid = W / 2 + (lw - rw) / 2 * 0  # centre column at page centre
        c.card((int(mid - lw - 70 * s), int(card_top), int(mid + rw + 70 * s), int(y)))
        for i, (a, b) in enumerate(spec["rows"]):
            ty = top + i * row_h
            for txt, fnt, col, right in ((a, fl, GOLD, True), (b, fr, CREAM, False)):
                m, _, bb = c._glyph_mask(txt, fnt, 0)
                capt = c._glyph_mask("H", fnt, 0)[2][1]
                dx = (mid - 30 * s - bb[2]) if right else (mid + 30 * s - bb[0])
                m = c._shift(m, dx, ty - capt)
                c._claim(m.getbbox(), f"row{i}{'L' if right else 'R'}")
                face = Image.new("RGBA", c.bg.size, col + (0,))
                face.putalpha(m)
                c._paste(face, "front")
            c.sphere(mid, ty + c.ink_height("H", fl) / 2, 7 * s, DOTS[i % 3])
        block_top = card_top
    elif "bullets" in spec:
        size = 32
        maxw = 760
        items = spec["bullets"]
        widths, heights = [], []
        for col, mk in items:
            paras, _, _ = c._wrap(mk, size, maxw * s)
            widths.append(max(w for p in paras for _, w in p))
            heights.append(c.paragraph_height(mk, size, maxw))
        indent = 46 * s
        block_w = indent + max(widths)
        x0 = (W - block_w) / 2
        gapb = 30 * s
        total_h = sum(heights) + gapb * (len(items) - 1)
        top = y - 40 * s - total_h
        card_top = top - 44 * s
        c.card((int(x0 - 50 * s), int(card_top), int(x0 + block_w + 50 * s), int(y)))
        ty = top
        for i, ((col, mk), h) in enumerate(zip(items, heights)):
            c.sphere(x0 + 12 * s, ty + size * s * 0.37, 11 * s, col)
            c.paragraph(ty, mk, size, maxw, label=f"b{i}", align="left", x0=x0 + indent)
            ty += h + gapb
        block_top = card_top

    if block_top < head_bottom + 30 * s:
        raise RuntimeError(f"body block collides with headline on slide {spec['page']}")
    bot_frac = min(0.70, (H - block_top + 190 * s) / H)
    c.bg = scrims(c.bg, top_frac=0.44, top_alpha=235, bot_frac=bot_frac, bot_alpha=252).convert("RGBA")
    c.save(out)
    print("saved", out)


SLIDES = {
    2: dict(kicker="THE  SETUP", lines=["A PS5 COSTS", "RS. 200,000"],
            body="That's the price **today**.\nBut Chandler thinks **GTA 6** is coming soon, "
                 "so PS5 prices will ++rise++."),
    3: dict(kicker="THE  DEAL", lines=["THE TOKEN", "MONEY"],
            body="Chandler pays a token amount of **Rs. 10,000** as **margin** "
                 "to lock the PS5 at **Rs. 200,000**.\n"
                 "**30 days from now**, he buys the PS5 for **Rs. 200,000**."),
    4: dict(kicker="SCENARIO  1", lines=["GTA 6", "RELEASES!"],
            body="30 days later, the PS5 goes up to ++Rs. 220,000++.\n"
                 "Chandler gets it at **Rs. 200,000** and sells it at ++Rs. 220,000++. "
                 "He only paid **Rs. 10,000** as margin upfront."),
    5: dict(kicker="SCENARIO  2", lines=["GTA 6 GETS", "DELAYED"],
            body="30 days later, the PS5 drops to ~~Rs. 180,000~~.\n"
                 "Chandler bought at **Rs. 200,000** and now sells at ~~Rs. 180,000~~, "
                 "so he bears a ~~loss of Rs. 20,000~~."),
    6: dict(kicker="THE  BIG  IDEA", lines=["WHAT DID CHANDLER", "ACTUALLY CREATE?"],
            body="A **margin contract / trade**: a financial agreement to buy or sell an asset "
                 "at a **fixed price** on a **future date**, by paying a **small upfront amount**."),
    7: dict(kicker="PLOT  TWIST", lines=["NOW REPLACE THE PS5", "WITH A COMMODITY"],
            body="People make similar agreements on the "
                 "**Pakistan Mercantile Exchange (PMEX)**.\nThis is called **Margin Trading**."),
    8: dict(kicker="THE  LINGO", lines=["TERMS USED IN", "MARGIN TRADING"],
            rows=[("PS5", "Underlying Asset"), ("Rs. 200,000", "Futures Price"),
                  ("Rs. 10,000", "Margin"), ("30 Days Later", "Expiry Date"),
                  ("Chandler's Deal", "Margin Trade")]),
    9: dict(kicker="THE  WHY", lines=["WHY DO PEOPLE", "TRADE ON MARGIN?"],
            bullets=[((60, 200, 100), "They think prices will ++rise++."),
                     ((235, 70, 60), "They think prices will ~~fall~~."),
                     (GOLD, "They want to **lock in today's price** and **reduce risk**.")]),
    10: dict(kicker="THE  TAKEAWAY", lines=["THAT'S HOW MARGIN", "TRADING WORKS"],
             body="Margin trading lets you trade **futures contracts** by paying a small "
                  "upfront amount known as **Margin** or **Token Money**.",
             cta="SAVE  THIS  \u2022  SEND  IT  TO  YOUR  JOEY",
             disclaimer="For education only. Margin trading carries a risk of loss."),
}


def slide(n, raw, out):
    n = int(n)
    spec = dict(SLIDES[n], page=n)
    print(f"slide {n}")
    content_slide(spec, raw, out)


if __name__ == "__main__":
    {"cover": cover, "slide": slide}[sys.argv[1]](*sys.argv[2:])
