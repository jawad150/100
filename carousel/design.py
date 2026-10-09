"""Friends-themed UI kit for the carousel: liquid glass, stickers, chat bubbles,
avatars, highlighter text, progress footer.

All drawing happens on a `Canvas` (see finish.py). Every element registers its
box with Canvas._claim so the layout can never overlap itself.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / "fonts"
GWFF = str(FONT_DIR / "GabrielWeissFriends.ttf")    # Friends logo-style handwriting
MARKER = str(FONT_DIR / "PermanentMarker-Regular.ttf")
MONT = str(FONT_DIR / "Montserrat.ttf")
ASSETS = HERE / "assets"

# ---- Friends palette ------------------------------------------------------
F_RED = (238, 64, 54)        # logo dot
F_YELLOW = (255, 206, 18)    # logo dot / peephole frame
F_BLUE = (40, 150, 232)      # logo dot
F_PURPLE = (92, 58, 150)     # Monica's door
F_PURPLE_DEEP = (34, 18, 58)
F_ORANGE = (214, 108, 48)    # Central Perk couch
F_GREEN = (30, 170, 98)
INK = (33, 17, 52)           # deep purple-black for text on yellow / white
PAPER = (255, 251, 240)
WHITE = (255, 255, 255)
DOTS = [F_RED, F_YELLOW, F_BLUE]

MINUS = "−"


def _rgba(c, a=255):
    return tuple(c[:3]) + (a,)


# ---------------------------------------------------------------- primitives
def rrect_mask(size, box, r):
    """Anti-aliased rounded-rect mask (drawn 3x and downsampled)."""
    k = 3
    W, H = size
    x0, y0, x1, y1 = box
    pad = 4
    lx0, ly0 = int(x0) - pad, int(y0) - pad
    w, h = int(x1 - lx0) + pad, int(y1 - ly0) + pad
    big = Image.new("L", (w * k, h * k), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        [(x0 - lx0) * k, (y0 - ly0) * k, (x1 - lx0) * k, (y1 - ly0) * k], radius=r * k, fill=255)
    small = big.resize((w, h), Image.LANCZOS)
    m = Image.new("L", size, 0)
    m.paste(small, (lx0, ly0))
    return m


def local_rrect(w, h, r, fill, outline=None, width=0, k=3):
    big = Image.new("RGBA", (int(w * k), int(h * k)), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=r * k, fill=fill,
                                          outline=outline, width=int(width * k))
    return big.resize((int(w), int(h)), Image.LANCZOS)


def hard_shadow(img, dx, dy, color=INK, alpha=235, blur=0):
    """Comic 'pop' shadow: solid offset copy of the alpha."""
    a = img.getchannel("A")
    W, H = img.size
    out = Image.new("RGBA", (W + abs(int(dx)) + 4, H + abs(int(dy)) + 4), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, _rgba(color, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    if blur:
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh, (max(0, int(dx)), max(0, int(dy))))
    out.alpha_composite(img, (max(0, -int(dx)), max(0, -int(dy))))
    return out


# ---------------------------------------------------------------- glass
def glass(canvas, mask, tint=F_PURPLE_DEEP, tint_a=0.58, blur=22, refract=18, edge=34,
          shadow=0.55, sat=1.3):
    """Liquid-glass panel baked into canvas.bg: frosted blur, edge refraction with
    slight chromatic split, specular rim (lit from top-left), top sheen, drop shadow."""
    from scipy import ndimage as ndi

    s = canvas.s
    W, H = canvas.W, canvas.H
    bb = mask.getbbox()
    M = int((refract + blur * 2 + 40) * s)
    x0, y0 = max(0, bb[0] - M), max(0, bb[1] - M)
    x1, y1 = min(W, bb[2] + M), min(H, bb[3] + M)
    base = canvas.bg.convert("RGB").crop((x0, y0, x1, y1))
    bg = np.asarray(base, np.float32)
    m = np.asarray(mask.crop((x0, y0, x1, y1)), np.float32) / 255.0
    h, w = m.shape

    # soft drop shadow below the panel
    sh = ndi.gaussian_filter(np.roll(m, int(16 * s), axis=0), 20 * s) * shadow
    bg = bg * (1 - (sh * (1 - m))[..., None])

    frost = np.asarray(base.filter(ImageFilter.GaussianBlur(blur * s)), np.float32)
    inside = m > 0.5
    d_in = ndi.distance_transform_edt(inside).astype(np.float32)
    e = np.clip(1 - d_in / (edge * s), 0, 1) ** 2 * inside
    ds = ndi.gaussian_filter(d_in, 2.5 * s)
    gy, gx = np.gradient(ds)
    nrm = np.hypot(gx, gy) + 1e-6
    nx, ny = -gx / nrm, -gy / nrm          # outward normal
    disp = e * refract * s
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = np.empty_like(frost)
    for ch, k in ((0, 1.18), (1, 1.0), (2, 0.82)):  # chromatic split at the rim
        out[..., ch] = ndi.map_coordinates(frost[..., ch], [yy + ny * disp * k, xx + nx * disp * k],
                                           order=1, mode="nearest")
    lum = out.mean(-1, keepdims=True)
    out = lum + (out - lum) * sat
    out = out * (1 - tint_a) + np.array(tint, np.float32) * tint_a

    rim = np.exp(-d_in / (2.4 * s)) * inside
    light = np.clip(-(nx * 0.45 + ny * 0.89), 0, 1)
    opp = np.clip(nx * 0.45 + ny * 0.89, 0, 1)
    out += 255 * (rim * (0.12 + 0.72 * light) + rim * 0.30 * opp)[..., None]
    # inner refraction glow along the rim
    out += 255 * (e * 0.10)[..., None]
    # top sheen
    top, hgt = bb[1] - y0, bb[3] - bb[1]
    t = np.clip((yy - top) / (0.45 * hgt), 0, 1)
    out += 255 * (0.075 * (1 - t) * inside)[..., None]

    res = bg * (1 - m[..., None]) + np.clip(out, 0, 255) * m[..., None]
    patch = Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)).convert("RGBA")
    canvas.bg.paste(patch, (x0, y0))


# ---------------------------------------------------------------- text helpers
class Rich:
    """Highlighter-pen rich text. Markup: **yellow highlight**, ++green pill++,
    ~~red pill~~ ; '\\n' starts a new paragraph."""

    STYLES = {
        "n": (WHITE, 560, None),
        "b": (INK, 800, F_YELLOW),
        "g": (WHITE, 800, F_GREEN),
        "r": (WHITE, 800, F_RED),
        "w": (WHITE, 800, None),
    }

    def __init__(self, canvas, size, lh=1.56, pgap=0.42):
        self.c = canvas
        self.size = size
        self.px = size * canvas.s
        self.L = self.px * lh
        self.pgap = pgap
        self.fonts = {k: canvas.font(MONT, size, w) for k, (_, w, _) in self.STYLES.items()}
        self.space = self.fonts["n"].getlength(" ")

    def tokens(self, markup):
        import re
        markup = re.sub(r"Rs\. (?=\d)", "Rs. ", markup)
        out = []
        for para in markup.split("\n"):
            units, glue = [], False
            for part in re.split(r"(\*\*.+?\*\*|\+\+.+?\+\+|~~.+?~~|__.+?__)", para):
                if not part:
                    continue
                st = "n"
                if part.startswith("__"):
                    st, part = "w", part[2:-2]
                elif part.startswith("**"):
                    st, part = "b", part[2:-2]
                elif part.startswith("++"):
                    st, part = "g", part[2:-2]
                elif part.startswith("~~"):
                    st, part = "r", part[2:-2]
                for i, wd in enumerate(part.split(" ")):
                    if not wd:
                        continue
                    if i == 0 and glue and units:
                        units[-1].append((wd, st))
                    else:
                        units.append([(wd, st)])
                glue = not part.endswith(" ")
            out.append(self._flag(units))
        return out

    def _hl(self, st):
        return self.STYLES[st][2] is not None

    def _flag(self, units):
        """pre/post padding only where a highlight run starts/ends."""
        res = []
        for i, u in enumerate(units):
            prev_st = units[i - 1][-1][1] if i else None
            next_st = units[i + 1][0][1] if i + 1 < len(units) else None
            pre = self._hl(u[0][1]) and prev_st != u[0][1]
            post = self._hl(u[-1][1]) and next_st != u[-1][1]
            res.append((u, pre, post))
        return res

    def wrap(self, markup, max_w):
        paras = []
        hl_pad = 0.30 * self.px  # highlights stick out a little; keep them inside
        for units in self.tokens(markup):
            lines, cur, cur_w = [], [], 0.0
            for u, pre, post in units:
                segs = [(t, st, self.fonts[st].getlength(t)) for t, st in u]
                segs = (segs, pre or (not cur and self._hl(segs[0][1])), post)
                uw = sum(x[2] for x in segs[0]) + self.px * 0.16 * (segs[1] + segs[2])
                add = uw + (self.space if cur else 0)
                if cur and cur_w + add > max_w - hl_pad:
                    lines.append((cur, cur_w))
                    cur, cur_w, add = [], 0.0, uw
                cur.append(segs)
                cur_w += add
            if cur:
                lines.append((cur, cur_w))
            paras.append(lines)
        return paras

    def hpad(self, segs):
        """Extra advance so highlight boxes never touch neighbouring words."""
        p = 0.0
        if self.STYLES[segs[0][1]][2] is not None:
            p += self.px * 0.16
        if self.STYLES[segs[-1][1]][2] is not None:
            p += self.px * 0.16
        return p

    def height(self, markup, max_w):
        paras = self.wrap(markup, max_w)
        n = sum(len(p) for p in paras)
        return (n - 1) * self.L + (len(paras) - 1) * self.L * self.pgap + self.px * 0.92

    def draw(self, x0, top, markup, max_w, plane="front", label="body", align="left"):
        """`top` = cap-height top of the first line."""
        c = self.c
        s = c.s
        lay = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
        hl = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
        d, dh = ImageDraw.Draw(lay), ImageDraw.Draw(hl)
        asc = self.fonts["n"].getmetrics()[0]
        cap = self.px * 0.70
        base = top + cap
        for lines in self.wrap(markup, max_w):
            for units, w in lines:
                x = x0 if align == "left" else x0 + (max_w - w) / 2
                runs = []
                for ui, (segs, pre, post) in enumerate(units):
                    if pre or (ui == 0 and self._hl(segs[0][1])):
                        x += self.px * 0.16
                    for wd, st, ww in segs:
                        d.text((x, base - asc), wd, font=self.fonts[st], fill=self.STYLES[st][0])
                        if self.STYLES[st][2] is not None:
                            if runs and runs[-1][2] == st and x - runs[-1][1] <= self.space + 2:
                                runs[-1][1] = x + ww
                            else:
                                runs.append([x, x + ww, st])
                        x += ww
                    if post:
                        x += self.px * 0.16
                    x += self.space
                for rx0, rx1, st in runs:
                    col = self.STYLES[st][2]
                    yt, yb = base - self.px * 0.86, base + self.px * 0.24
                    px = 0.12 * self.px
                    if st == "b":  # marker swipe: slightly skewed, rough ends
                        dh.polygon([(rx0 - px, yt + 3 * s), (rx1 + px * 1.1, yt - 1 * s),
                                    (rx1 + px * 0.8, yb + 1 * s), (rx0 - px * 1.2, yb + 3 * s)],
                                   fill=_rgba(col, 245))
                    else:          # solid pill
                        dh.rounded_rectangle([rx0 - px, yt, rx1 + px, yb], radius=8 * s,
                                             fill=_rgba(col, 250))
                base += self.L
            base += self.L * self.pgap
        bbox = ImageChopsLighter(lay, hl).getbbox()
        c._claim(bbox, label)
        a = lay.getchannel("A")
        sh = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
        sh.putalpha(c._shift(a, 0, 2 * s).filter(ImageFilter.GaussianBlur(3 * s))
                    .point(lambda v: int(v * 0.55)))
        c._paste(hl, plane)
        c._paste(sh, plane)
        c._paste(lay, plane)
        return bbox


def ImageChopsLighter(a, b):
    from PIL import ImageChops
    return ImageChops.lighter(a.getchannel("A"), b.getchannel("A"))


def wrap_plain(font, text, max_w):
    """Greedy wrap, then re-balance so lines have similar widths."""
    lines = _greedy(font, text, max_w)
    if len(lines) > 1:
        lo, hi = max(font.getlength(w) for w in text.split(" ")), max_w
        while hi - lo > 2:
            mid = (lo + hi) / 2
            if len(_greedy(font, text, mid)) == len(lines):
                hi = mid
            else:
                lo = mid
        lines = _greedy(font, text, hi)
    return lines


def _greedy(font, text, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and font.getlength(t) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- avatar
def avatar_img(canvas, name, d, ring, disc):
    s = canvas.s
    k = 2
    D = int(d * k)
    out = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    circ = Image.new("L", (D, D), 0)
    ImageDraw.Draw(circ).ellipse([0, 0, D - 1, D - 1], fill=255)
    bgd = Image.new("RGBA", (D, D), _rgba(disc))
    # subtle radial light on the disc
    yy, xx = np.mgrid[0:D, 0:D].astype(np.float32)
    rr = np.hypot(xx - D * 0.35, yy - D * 0.3) / D
    glow = np.clip(1 - rr * 1.6, 0, 1) * 70
    arr = np.asarray(bgd, np.float32)
    arr[..., :3] = np.clip(arr[..., :3] + glow[..., None], 0, 255)
    bgd = Image.fromarray(arr.astype(np.uint8))
    head = Image.open(ASSETS / f"{name}.png").convert("RGBA")
    hs = int(D * 1.08)
    head = head.resize((hs, hs), Image.LANCZOS)
    bgd.alpha_composite(head, ((D - hs) // 2, int(D * 0.06)))
    out.paste(bgd, (0, 0), circ)
    dr = ImageDraw.Draw(out)
    rw = int(6 * s * k)
    dr.ellipse([rw / 2, rw / 2, D - 1 - rw / 2, D - 1 - rw / 2], outline=_rgba(ring), width=rw)
    dr.ellipse([0, 0, D - 1, D - 1], outline=_rgba(INK), width=int(2 * s * k))
    return out.resize((int(d), int(d)), Image.LANCZOS)


# ---------------------------------------------------------------- stickers
def starburst(n, ro, ri, cx, cy, rot=0.0):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = math.pi * i / n + rot
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sticker_img(canvas, kind, lines, color=None):
    """Returns an un-rotated RGBA sticker image."""
    s = canvas.s
    k = 2
    if kind in ("burst",):
        fill = color or F_YELLOW
        txt_col = INK if fill == F_YELLOW else WHITE
        f1 = canvas.font(MONT, 30 * k, 900)
        f2 = canvas.font(MONT, 20 * k, 800)
        w1 = f1.getlength(lines[0])
        w2 = f2.getlength(lines[1]) if len(lines) > 1 else 0
        R = max(w1, w2) / 2 + 46 * s * k
        D = int(R * 2 + 20 * s * k)
        im = Image.new("RGBA", (D, D), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        cx = cy = D / 2
        dr.polygon(starburst(18, R, R * 0.84, cx, cy), fill=_rgba(WHITE))
        dr.polygon(starburst(18, R - 7 * s * k, R * 0.84 - 7 * s * k, cx, cy), fill=_rgba(fill))
        h1 = f1.getbbox("H")[3] - f1.getbbox("H")[1]
        h2 = (f2.getbbox("H")[3] - f2.getbbox("H")[1]) if len(lines) > 1 else 0
        gap = 10 * s * k if len(lines) > 1 else 0
        tot = h1 + gap + h2
        y = cy - tot / 2 - f1.getbbox("H")[1]
        dr.text((cx - w1 / 2, y), lines[0], font=f1, fill=_rgba(txt_col))
        if len(lines) > 1:
            y2 = cy - tot / 2 + h1 + gap - f2.getbbox("H")[1]
            dr.text((cx - w2 / 2, y2), lines[1], font=f2, fill=_rgba(txt_col))
        im = im.resize((D // k, D // k), Image.LANCZOS)
        return hard_shadow(im, 5 * s, 6 * s)

    if kind == "calendar":
        fbig = canvas.font(GWFF, 58 * k)
        fsm = canvas.font(MONT, 17 * k, 900)
        w = int(150 * s * k)
        h = int(162 * s * k)
        im = local_rrect(w, h, 18 * s * k, _rgba(PAPER), _rgba(INK), 3 * s * k, k=1)
        dr = ImageDraw.Draw(im)
        strip = int(44 * s * k)
        top = local_rrect(w, strip + 20 * s * k, 18 * s * k, _rgba(F_RED), k=1)
        im.alpha_composite(top.crop((0, 0, w, strip)), (0, 0))
        dr.rectangle([0, strip - 3 * s * k, w, strip], fill=_rgba(INK))
        dr.rounded_rectangle([0, 0, w - 1, h - 1], radius=18 * s * k, outline=_rgba(INK), width=int(3 * s * k))
        for rx in (0.3, 0.7):  # binder rings
            dr.ellipse([w * rx - 7 * s * k, -6 * s * k, w * rx + 7 * s * k, 10 * s * k], fill=_rgba(INK))
        hb = fsm.getbbox("H")
        lw = fsm.getlength(lines[0])
        dr.text(((w - lw) / 2, (strip - (hb[3] - hb[1])) / 2 - hb[1] + 2 * s * k), lines[0], font=fsm,
                fill=_rgba(WHITE))
        bw = fbig.getlength(lines[1])
        bb = fbig.getbbox(lines[1])
        fun = canvas.font(MONT, 15 * k, 900)
        ub = fun.getbbox("H")
        uh = ub[3] - ub[1]
        tot = (bb[3] - bb[1]) + 8 * s * k + uh
        y0 = strip + (h - strip - tot) / 2
        dr.text(((w - bw) / 2, y0 - bb[1]), lines[1], font=fbig, fill=_rgba(INK))
        uw = fun.getlength(lines[2])
        dr.text(((w - uw) / 2, y0 + (bb[3] - bb[1]) + 8 * s * k - ub[1]), lines[2], font=fun,
                fill=_rgba(F_RED))
        im = im.resize((w // k, h // k), Image.LANCZOS)
        return hard_shadow(im, 5 * s, 6 * s)

    if kind == "stamp":
        col = color or F_RED
        f = canvas.font(MONT, 30 * k, 900)
        tw = f.getlength(lines[0]) + 6 * s * k * (len(lines[0]) - 1)
        w, h = int(tw + 56 * s * k), int(78 * s * k)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.rounded_rectangle([4, 4, w - 5, h - 5], radius=12 * s * k, outline=_rgba(col), width=int(6 * s * k))
        dr.rounded_rectangle([14 * s * k, 14 * s * k, w - 14 * s * k, h - 14 * s * k], radius=6 * s * k,
                             outline=_rgba(col), width=int(2 * s * k))
        hb = f.getbbox("H")
        x = (w - tw) / 2
        for ch in lines[0]:
            dr.text((x, (h - (hb[3] - hb[1])) / 2 - hb[1]), ch, font=f, fill=_rgba(col))
            x += f.getlength(ch) + 6 * s * k
        # ink texture: knock out speckles
        rng = np.random.default_rng(3)
        a = np.asarray(im.getchannel("A"), np.float32)
        a *= (rng.random(a.shape) > 0.08) * 0.95
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        im = im.resize((w // k, h // k), Image.LANCZOS)
        # paper backing so it reads on any background
        back = local_rrect(im.size[0], im.size[1], 10 * s, _rgba(PAPER, 235))
        back.alpha_composite(im)
        return hard_shadow(back, 4 * s, 5 * s, alpha=180, blur=2 * s)

    # 'tag' : price-tag shape with a punched hole and string
    fill = color or F_YELLOW
    txt_col = INK if fill == F_YELLOW else WHITE
    f1 = canvas.font(MONT, 28 * k, 900)
    f2 = canvas.font(MONT, 17 * k, 800)
    w1 = f1.getlength(lines[0])
    w2 = f2.getlength(lines[1]) if len(lines) > 1 else 0
    tw = max(w1, w2)
    notch = 38 * s * k
    w = int(tw + notch + 44 * s * k)
    h = int((96 if len(lines) > 1 else 72) * s * k)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    poly = [(notch, 0), (w - 12 * s * k, 0), (w, 12 * s * k), (w, h - 12 * s * k), (w - 12 * s * k, h),
            (notch, h), (0, h / 2)]
    dr.polygon(poly, fill=_rgba(INK))
    inset = 4 * s * k
    poly2 = [(notch + inset * 0.6, inset), (w - 12 * s * k - inset * 0.4, inset), (w - inset, 12 * s * k + inset * 0.4),
             (w - inset, h - 12 * s * k - inset * 0.4), (w - 12 * s * k - inset * 0.4, h - inset),
             (notch + inset * 0.6, h - inset), (inset * 2.2, h / 2)]
    dr.polygon(poly2, fill=_rgba(fill))
    hr = 8 * s * k
    dr.ellipse([notch * 0.55 - hr, h / 2 - hr, notch * 0.55 + hr, h / 2 + hr], fill=(0, 0, 0, 0),
               outline=_rgba(INK), width=int(3 * s * k))
    # punch the hole
    a = im.getchannel("A")
    ImageDraw.Draw(a).ellipse([notch * 0.55 - hr + 3 * s * k, h / 2 - hr + 3 * s * k,
                               notch * 0.55 + hr - 3 * s * k, h / 2 + hr - 3 * s * k], fill=0)
    im.putalpha(a)
    tx0 = notch + 14 * s * k
    h1 = f1.getbbox("H")
    if len(lines) > 1:
        h2 = f2.getbbox("H")
        th = (h1[3] - h1[1]) + 9 * s * k + (h2[3] - h2[1])
        y = (h - th) / 2
        dr.text((tx0 + (tw - w2) / 2, y - h2[1]), lines[1], font=f2, fill=_rgba(txt_col))
        dr.text((tx0 + (tw - w1) / 2, y + (h2[3] - h2[1]) + 9 * s * k - h1[1]), lines[0], font=f1,
                fill=_rgba(txt_col))
    else:
        dr.text((tx0 + (tw - w1) / 2, (h - (h1[3] - h1[1])) / 2 - h1[1]), lines[0], font=f1,
                fill=_rgba(txt_col))
    im = im.resize((w // k, h // k), Image.LANCZOS)
    return hard_shadow(im, 5 * s, 6 * s)


def kicker_img(canvas, text):
    """Yellow 'tape' sticker for the slide label."""
    s = canvas.s
    k = 2
    f = canvas.font(MONT, 22 * k, 800)
    tr = 4 * s * k
    tw = sum(f.getlength(ch) for ch in text) + tr * (len(text) - 1)
    hb = f.getbbox("H")
    w, h = int(tw + 2 * 30 * s * k), int((hb[3] - hb[1]) + 2 * 16 * s * k)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    # tape with zig-zag torn ends
    zz = 7 * s * k
    n = 6
    left = [(0 if i % 2 == 0 else zz, h * i / n) for i in range(n + 1)]
    right = [(w - (0 if i % 2 == 0 else zz), h * (n - i) / n) for i in range(n + 1)]
    dr.polygon(left + right, fill=_rgba(F_YELLOW))
    x = (w - tw) / 2
    y = (h - (hb[3] - hb[1])) / 2 - hb[1]
    for ch in text:
        dr.text((x, y), ch, font=f, fill=_rgba(INK))
        x += f.getlength(ch) + tr
    im = im.resize((w // k, h // k), Image.LANCZOS)
    return hard_shadow(im, 4 * s, 5 * s, color=(0, 0, 0), alpha=150, blur=3 * s)


def name_tag_img(canvas, text, fill, fg):
    s = canvas.s
    f = canvas.font(MONT, 17, 900)
    tr = 3 * s
    tw = sum(f.getlength(ch) for ch in text) + tr * (len(text) - 1)
    hb = f.getbbox("H")
    w, h = int(tw + 32 * s), int((hb[3] - hb[1]) + 22 * s)
    im = local_rrect(w, h, h / 2, _rgba(fill), _rgba(INK), 2.5 * s)
    dr = ImageDraw.Draw(im)
    x = (w - tw) / 2
    for ch in text:
        dr.text((x, (h - (hb[3] - hb[1])) / 2 - hb[1]), ch, font=f, fill=_rgba(fg))
        x += f.getlength(ch) + tr
    return hard_shadow(im, 3 * s, 4 * s, alpha=220)


def paste_center(canvas, img, cx, cy, plane="front", angle=0.0, label=None, claim=True):
    if angle:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = int(round(cx - img.size[0] / 2)), int(round(cy - img.size[1] / 2))
    lay = Image.new("RGBA", canvas.bg.size, (0, 0, 0, 0))
    lay.alpha_composite(img, (max(0, x), max(0, y)))
    if claim:
        canvas._claim(lay.getchannel("A").getbbox(), label or "element")
    canvas._paste(lay, plane)
    return lay.getchannel("A").getbbox()


# ---------------------------------------------------------------- chat bubble
def bubble_img(canvas, text, max_w, tail="right"):
    """Comic speech bubble (Joey). White paper, ink outline, hard pop shadow."""
    s = canvas.s
    k = 2
    f = canvas.font(MARKER, 31 * k)
    lines = wrap_plain(f, text, max_w * s * k)
    asc, desc = f.getmetrics()
    lh = 44 * s * k
    hb = f.getbbox("Hy")
    tw = max(f.getlength(ln) for ln in lines)
    padx, pady = 30 * s * k, 22 * s * k
    th = (len(lines) - 1) * lh + (hb[3] - hb[1])
    bw, bh = int(tw + 2 * padx), int(th + 2 * pady)
    tl = 26 * s * k  # tail length
    if tail == "down":
        im = Image.new("RGBA", (bw + 8, bh + int(tl) + 8), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        lw = int(3.5 * s * k)
        dr.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=30 * s * k, fill=_rgba(PAPER), outline=_rgba(INK),
                             width=lw)
        tx = bw * 0.68
        tri = [(tx - 18 * s * k, bh - lw * 1.2), (tx + 10 * s * k, bh + tl), (tx + 14 * s * k, bh - lw * 1.2)]
        dr.polygon(tri, fill=_rgba(PAPER))
        dr.line(tri, fill=_rgba(INK), width=lw, joint="curve")
        y = pady - hb[1]
        for ln in lines:
            dr.text(((bw - f.getlength(ln)) / 2, y), ln, font=f, fill=_rgba(INK))
            y += lh
        im = im.resize((im.size[0] // k, im.size[1] // k), Image.LANCZOS)
        return hard_shadow(im, 6 * s, 7 * s)
    W = bw + int(tl) + 8
    im = Image.new("RGBA", (W, bh + 8), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    ox = 0 if tail == "right" else int(tl)
    lw = int(3.5 * s * k)
    body = [ox, 0, ox + bw - 1, bh - 1]
    dr.rounded_rectangle(body, radius=30 * s * k, fill=_rgba(PAPER), outline=_rgba(INK), width=lw)
    cy = bh * 0.5
    if tail == "right":
        tri = [(ox + bw - lw * 1.2, cy - 16 * s * k), (ox + bw + tl, cy + 4 * s * k),
               (ox + bw - lw * 1.2, cy + 14 * s * k)]
    else:
        tri = [(ox + lw * 1.2, cy - 16 * s * k), (ox - tl, cy + 4 * s * k), (ox + lw * 1.2, cy + 14 * s * k)]
    dr.polygon(tri, fill=_rgba(PAPER))
    dr.line([tri[0], tri[1], tri[2]], fill=_rgba(INK), width=lw, joint="curve")
    y = pady - hb[1]
    for ln in lines:
        lx = ox + (bw - f.getlength(ln)) / 2
        dr.text((lx, y), ln, font=f, fill=_rgba(INK))
        y += lh
    im = im.resize((im.size[0] // k, im.size[1] // k), Image.LANCZOS)
    return hard_shadow(im, 6 * s, 7 * s)


# ---------------------------------------------------------------- footer
def footer(canvas, page, total, label="MARGIN  TRADING  101"):
    c = canvas
    s, W, H = c.s, c.W, c.H
    f = c.font(MONT, 16, 800)
    hb = f.getbbox("H")
    capH = hb[3] - hb[1]
    y_mid = H - 50 * s - capH / 2
    lay = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tr = 3 * s

    def spaced(x, txt, col, anchor="l"):
        tw = sum(f.getlength(ch) for ch in txt) + tr * (len(txt) - 1)
        if anchor == "r":
            x -= tw
        for ch in txt:
            d.text((x, y_mid - capH / 2 - hb[1]), ch, font=f, fill=col)
            x += f.getlength(ch) + tr
        return tw

    spaced(72 * s, label, (255, 255, 255, 215))
    right = f"{page:02d} / {total:02d}" + ("  →" if page < total else "")
    spaced(W - 72 * s, right, (255, 255, 255, 215), anchor="r")
    # progress bar: past = white, current = yellow (wide), future = faint
    seg, cur_w, gap, bh = 20 * s, 44 * s, 7 * s, 7 * s
    total_w = (total - 1) * seg + cur_w + (total - 1) * gap
    x = W / 2 - total_w / 2
    for i in range(1, total + 1):
        ww = cur_w if i == page else seg
        col = _rgba(F_YELLOW) if i == page else ((255, 255, 255, 200) if i < page else (255, 255, 255, 70))
        d.rounded_rectangle([x, y_mid - bh / 2, x + ww, y_mid + bh / 2], radius=bh / 2, fill=col)
        x += ww + gap
    box = lay.getchannel("A").getbbox()
    c._claim((0, box[1], W, box[3]), "footer")
    sh = Image.new("RGBA", c.bg.size, (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(3 * s)).point(lambda v: int(v * 0.6)))
    c._paste(sh, "front")
    c._paste(lay, "front")
    return box
