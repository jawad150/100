"""Look + effects for BMHC "AI can recreate this building. But not what happens inside." (9:16, 1080x1920).

Brand (BMHC guidelines): ink #0B0B0B, white, magenta #E60585 (primary accent), teal #2DC892, orange #FF4200,
lime #69FF00; Inter ExtraBold caps caption bursts (2-3 words), white on an ink pill, key word in magenta; four-bar wipe.
Effects ("skills"): spiral (camera spirals up the AI build), explainer (call-outs), eclipse (the cut inside), layercut
(slices open onto real life), retro (archive film on 'preserve'), aurora (the four colours come alive).
"""
import os, math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_ai'
FON = f'{ROOT}/workspace_sol/fonts'
W, H = 1080, 1920


def hx(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


INK, CHAR, SLATE, STONE, MIST, WHITE = hx('0B0B0B'), hx('1F1F1F'), hx('5C5C5C'), hx('E9E6DF'), hx('F6F5F1'), hx('FFFFFF')
MAG, TEAL, ORANGE, LIME = hx('E60585'), hx('2DC892'), hx('FF4200'), hx('69FF00')
BARS = (MAG, TEAL, ORANGE, LIME)
HOLO = np.array((0.86, 0.97, 1.0), np.float32)


@functools.lru_cache(None)
def F(w, s):
    return ImageFont.truetype(f'{FON}/Inter-{w}.ttf', int(s))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


def e_out(u):
    return 1 - (1 - u) ** 3


def e_inout(u):
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def e_back(u, s=1.7):
    u = u - 1
    return u * u * ((s + 1) * u + s) + 1


def canvas(col=INK):
    c = np.empty((H, W, 3), np.float32)
    c[:] = col
    return c


# ------------------------------------------------------------------ images
@functools.lru_cache(maxsize=64)
def load(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise FileNotFoundError(path)
    im = im.astype(np.float32) / 255
    if im.ndim == 2:
        im = np.dstack([im] * 3)
    if im.shape[2] == 4:
        rgb = im[..., 2::-1] if False else im[..., [2, 1, 0]]
        return np.dstack([rgb * im[..., 3:4], im[..., 3]])               # premultiplied RGBA
    return im[..., [2, 1, 0]].copy()


def cover(img, fx=0.5, fy=0.5, z=1.0, w=W, h=H, dx=0.0, dy=0.0, rot=0.0):
    """Fill w x h from img (zoom z >= 1, focus fx/fy, extra pan dx/dy in output px)."""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * z
    cx, cy = fx * iw, fy * ih
    cx = clamp(cx, w / 2 / s, iw - w / 2 / s)
    cy = clamp(cy, h / 2 / s, ih - h / 2 / s)
    M = np.array([[s, 0, w / 2 - s * cx + dx], [0, s, h / 2 - s * cy + dy]], np.float32)
    if rot:
        R = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0)
        M = (np.vstack([R, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2]
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


class Clip:
    """Sequential reader for a footage file (seek once, then read forwards)."""

    def __init__(self, path):
        self.path = path
        self.cap = None
        self.t = -1
        self.fps = 25.0
        self.last = None

    def at(self, t):
        if self.cap is None or t < self.t - 1e-3 or t > self.t + 1.0:
            if self.cap is not None:
                self.cap.release()
            self.cap = cv2.VideoCapture(self.path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.cap.set(cv2.CAP_PROP_POS_MSEC, max(0, t) * 1000)
            ok, fr = self.cap.read()
            self.t = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            self.last = fr
        while self.t + 1 / self.fps <= t + 1e-4:
            ok, fr = self.cap.read()
            if not ok:
                break
            self.last = fr
            self.t += 1 / self.fps
        return self.last[..., ::-1].astype(np.float32) / 255


def grade(c, warm=0.0, contrast=1.0, sat=1.0, lift=0.0, vig=0.35, exp=1.0):
    c = c * exp
    if warm:
        c = c * np.array((1 + 0.08 * warm, 1 + 0.02 * warm, 1 - 0.1 * warm), np.float32)
    g = c.mean(-1, keepdims=True)
    c = g + (c - g) * sat
    c = (c - 0.5) * contrast + 0.5 + lift
    if vig:
        c = c * vignette(vig)[..., None]
    return np.clip(c, 0, 1)


@functools.lru_cache(None)
def vignette(a):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W * 0.75), (yy - H / 2) / (H * 0.62))
    return np.clip(1 - a * r ** 2.2, 0, 1)


def grain(c, amt=0.035, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)
    return np.clip(c + n[..., None] * amt, 0, 1)


def blend(c, im, a):
    """Composite premultiplied RGBA `im` (same size) with opacity a."""
    al = im[..., 3:4] * a
    c[:] = c * (1 - al) + im[..., :3] * a
    return c


def paste(c, spr, cx, cy, a=1.0):
    """Paste premultiplied RGBA sprite centred at (cx, cy)."""
    sh, sw = spr.shape[:2]
    x0, y0 = int(round(cx - sw / 2)), int(round(cy - sh / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + sw), min(H, y0 + sh)
    if X1 <= X0 or Y1 <= Y0:
        return c
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    reg = c[Y0:Y1, X0:X1]
    al = s[..., 3:4] * a
    reg[:] = reg * (1 - al) + s[..., :3] * a
    return c


@functools.lru_cache(maxsize=256)
def token(name, size, rot=0):
    im = load(f'{S}/assets/{name}.png')
    a = im[..., 3]
    ys, xs = np.where(a > 0.02)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = size / max(im.shape[:2])
    im = cv2.resize(im, (max(1, int(im.shape[1] * sc)), max(1, int(im.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    if rot:
        h_, w_ = im.shape[:2]
        R = cv2.getRotationMatrix2D((w_ / 2, h_ / 2), rot, 1.0)
        cs, sn = abs(R[0, 0]), abs(R[0, 1])
        nw, nh = int(h_ * sn + w_ * cs), int(h_ * cs + w_ * sn)
        R[0, 2] += nw / 2 - w_ / 2
        R[1, 2] += nh / 2 - h_ / 2
        im = cv2.warpAffine(im, R, (nw, nh), flags=cv2.INTER_CUBIC)
    return im


def pop(c, name, cx, cy, size, u, rot=0, shadow=True, glow=None):
    """3D token popping in with an overshoot (u: 0..1+ since the cue word)."""
    if u <= 0:
        return c
    s = e_back(clamp(u / 0.45))
    if s <= 0.02:
        return c
    spr = token(name, max(8, int(size * s)), rot)
    a = clamp(u / 0.12)
    bob = math.sin(u * 2.4) * 8 * clamp(u - 0.45)
    if shadow:
        sh = spr[..., 3]
        pad = 40
        m = np.zeros((sh.shape[0] + 2 * pad, sh.shape[1] + 2 * pad), np.float32)
        m[pad:-pad, pad:-pad] = sh
        m = cv2.GaussianBlur(m, (0, 0), 18) * 0.55
        sp = np.dstack([np.zeros(m.shape + (3,), np.float32), m])
        paste(c, sp, cx + 14, cy + 30 + bob, a)
    if glow is not None:
        gl = cv2.GaussianBlur(spr[..., 3], (0, 0), 30)
        g = np.dstack([gl[..., None] * glow, gl]) * 0.7
        paste(c, g.astype(np.float32), cx, cy + bob, a)
    return paste(c, spr, cx, cy + bob, a)


# ------------------------------------------------------------------ type
def text_sprite(s, w, size, col=WHITE, track=0.02, alpha=1.0):
    f = F(w, size)
    if track:
        widths = [f.getlength(ch) for ch in s]
        tw = sum(widths) + track * size * (len(s) - 1)
    else:
        tw = f.getlength(s)
    asc, desc = f.getmetrics()
    im = Image.new('L', (int(tw + 8), asc + desc + 8), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = 4
        for ch, cw in zip(s, widths):
            d.text((x, 4), ch, font=f, fill=255)
            x += cw + track * size
    else:
        d.text((4, 4), s, font=f, fill=255)
    a = np.asarray(im, np.float32)[..., None] / 255 * alpha
    return np.dstack([a * np.asarray(col, np.float32), a])


def caption(c, parts, y, u=1.0, size=82, pill=True):
    """Caption burst: parts = [(text, colour)], Inter ExtraBold caps, on an ink pill. u animates in (0..1)."""
    if u <= 0:
        return c
    sprs = [text_sprite(t.upper(), 800, size, col) for t, col in parts]
    gap = size * 0.28
    tw = sum(s.shape[1] for s in sprs) + gap * (len(sprs) - 1)
    if tw > W - 180:                                   # keep every burst inside the safe zone
        return caption(c, parts, y, u, int(size * (W - 180) / tw) - 1, pill)
    th = max(s.shape[0] for s in sprs)
    k = e_back(clamp(u / 0.35), 1.3)
    a = clamp(u / 0.15)
    if pill:
        pw, ph = tw + size * 0.9, th + size * 0.32
        rr = rrect(pw * (0.85 + 0.15 * k), ph, ph * 0.22, INK, 0.92)
        paste(c, rr, W / 2, y, a)
    x = W / 2 - tw / 2
    for s in sprs:
        paste(c, s, x + s.shape[1] / 2, y + (1 - k) * 30, a)
        x += s.shape[1] + gap
    return c


def rrect(w, h, r, col, a=1.0):
    w, h = int(max(2, w)), int(max(2, h))
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.rectangle(m, (int(r * 4), 0), (int((w - r) * 4), h * 4), 255, -1)
    cv2.rectangle(m, (0, int(r * 4)), (w * 4, int((h - r) * 4)), 255, -1)
    for x in (r, w - r):
        for y in (r, h - r):
            cv2.circle(m, (int(x * 4), int(y * 4)), int(r * 4), 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255 * a
    return np.dstack([m * np.asarray(col, np.float32), m])


def tag(c, label, x=64, y=150, col=MAG, txt=WHITE, a=1.0):
    """Pillar tag top-left (shown in the first second, per the guidelines)."""
    s = text_sprite(label, 700, 30, txt, track=0.12)
    rr = rrect(s.shape[1] + 52, 58, 29, col)
    paste(c, rr, x + rr.shape[1] / 2, y, a)
    paste(c, s, x + rr.shape[1] / 2, y + 2, a)


# ------------------------------------------------------------------ AI interface + explainer
def prompt_bar(c, typed, y=300, caret=True, t=0.0, status=None, a=1.0):
    w, h = 940, 132
    paste(c, rrect(w, h, 34, CHAR, 0.95), W / 2, y, a)
    edge = rrect(w + 4, h + 4, 36, (0.35, 0.35, 0.35), 0.6)
    paste(c, edge, W / 2, y, a * 0.4)
    paste(c, rrect(w, h, 34, CHAR, 1.0), W / 2, y, a)
    sp = text_sprite('✦' if False else '>', 800, 40, MAG)
    paste(c, sp, W / 2 - w / 2 + 52, y, a)
    s = text_sprite(typed, 500, 34, WHITE) if typed else None
    x0 = W / 2 - w / 2 + 92
    if s is not None:
        if s.shape[1] > w - 140:
            s = s[:, s.shape[1] - (w - 140):]
        paste(c, s, x0 + s.shape[1] / 2, y, a)
        x0 += s.shape[1]
    if caret and (int(t * 2.2) % 2 == 0):
        paste(c, rrect(4, 46, 2, MAG), x0 + 8, y, a)
    if status:
        st = text_sprite(status, 500, 28, (0.62, 0.62, 0.62), track=0.06)
        paste(c, st, W / 2 - w / 2 + 30 + st.shape[1] / 2, y + h / 2 + 40, a)
    return c


def callout(c, p, label, u, side=1, dy=-120, col=MAG):
    """Explainer call-out: a dot on the model, a leader line, a label chip."""
    if u <= 0:
        return c
    x, y = p
    k = e_out(clamp(u / 0.4))
    ex, ey = x + side * 170 * k, y + dy * k
    lay = np.zeros((H, W), np.uint8)
    cv2.circle(lay, (int(x * 4), int(y * 4)), 10 * 4, 255, -1, cv2.LINE_AA, shift=2)
    cv2.line(lay, (int(x * 4), int(y * 4)), (int(ex * 4), int(ey * 4)), 255, 3 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.asarray(col, np.float32) * m
    if u > 0.25:
        s = text_sprite(label, 800, 34, WHITE, track=0.08)
        rr = rrect(s.shape[1] + 40, 64, 14, col)
        a = clamp((u - 0.25) / 0.15)
        bx = ex + side * (rr.shape[1] / 2)
        paste(c, rr, bx, ey, a)
        paste(c, s, bx, ey + 1, a)
    return c


def glow_lines(rgb, alpha, amt=1.0):
    g = cv2.GaussianBlur(rgb, (0, 0), 7) * 1.1 + cv2.GaussianBlur(rgb, (0, 0), 26) * 0.6
    return rgb + g * amt, np.maximum(alpha, cv2.GaussianBlur(alpha, (0, 0), 7) * 0.8)


def blueprint_bg(t=0.0, a=1.0):
    """Dark AI workspace: ink with a faint grid and a soft digital pulse."""
    c = canvas(INK)
    lay = np.zeros((H, W), np.float32)
    step = 60
    off = (t * 20) % step
    for x in np.arange(-step, W + step, step):
        lay[:, int(x + off) % W] = 1
    for y in np.arange(0, H, step):
        lay[int((y + off) % H), :] = 1
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 0.8)
    c += lay[..., None] * (0.035 + 0.02 * pulse) * a
    return c


# ------------------------------------------------------------------ transitions / skills
def eclipse(c, cx, cy, r, u, warm=(1.0, 0.72, 0.38)):
    """A dark disc slides over a light; a warm corona blooms around it (u 0..1)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    off = (1 - e_inout(clamp(u))) * r * 2.2
    d = np.hypot(xx - cx - off, yy - cy)
    disc = np.clip((r - d) / 2.0, 0, 1)
    ring = np.hypot(xx - cx, yy - cy)
    cor = np.exp(-((ring - r) / (r * 0.35)) ** 2) * clamp(u * 1.4) + np.exp(-(ring / (r * 3.2)) ** 2) * 0.35 * clamp(u)
    c[:] = c + cor[..., None] * np.asarray(warm, np.float32) * 1.2
    c[:] = c * (1 - disc[..., None]) + INK * disc[..., None]
    return np.clip(c, 0, 1)


def layercut(a, b, u, n=6, horiz=True):
    """Layer-cut: the frame is cut into slices that slide away in alternate directions, revealing b underneath."""
    out = b.copy()
    for i in range(n):
        y0, y1 = int(H * i / n), int(H * (i + 1) / n)
        d = e_inout(clamp(u * 1.25 - i * 0.05))
        sh = int((1 if i % 2 == 0 else -1) * d * W * 1.05)
        if abs(sh) >= W:
            continue
        sl = a[y0:y1]
        if sh >= 0:
            out[y0:y1, sh:] = sl[:, :W - sh]
        else:
            out[y0:y1, :W + sh] = sl[:, -sh:]
        edge = int(np.clip((sh if sh > 0 else W + sh), 0, W - 1))
        out[y0:y1, max(0, edge - 3):edge + 3] = BARS[i % 4]
    return out


def four_bar_wipe(c, u, vertical=True):
    """BMHC four-bar wipe (magenta, teal, orange, lime, fixed order) covers then uncovers (u 0..1)."""
    for i, col in enumerate(BARS):
        k = clamp(u * 1.6 - i * 0.12)
        if vertical:
            x0, x1 = int(W * i / 4), int(W * (i + 1) / 4)
            if k < 0.5:
                h_ = int(H * e_inout(k * 2))
                c[H - h_:, x0:x1] = col
            else:
                h_ = int(H * (1 - e_inout((k - 0.5) * 2)))
                c[:h_, x0:x1] = col
    return c


def retro(c, t, amt=1.0, seed=0):
    """Archive film: warm sepia, gate weave, flicker, grain, dust, scratches, soft frame edge."""
    rng = np.random.default_rng(int(t * 24) + seed)
    g = c.mean(-1, keepdims=True)
    sep = np.concatenate([g * 1.08 + 0.04, g * 0.95 + 0.02, g * 0.74], -1)
    out = c * (1 - amt) + sep * amt
    M = np.float32([[1, 0, rng.normal(0, 1.2) * amt], [0, 1, rng.normal(0, 2.0) * amt]])
    out = cv2.warpAffine(out, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    out = out * (1 + rng.normal(0, 0.03) * amt)
    out = grain(out, 0.06 * amt, int(t * 24))
    lay = np.zeros((H, W), np.uint8)
    for _ in range(int(6 * amt)):
        cv2.circle(lay, (int(rng.uniform(0, W)), int(rng.uniform(0, H))), int(rng.uniform(1, 4)), 255, -1)
    if rng.uniform() < 0.6:
        x = int(rng.uniform(0, W))
        cv2.line(lay, (x, 0), (x + int(rng.normal(0, 20)), H), 180, 1)
    m = lay.astype(np.float32)[..., None] / 255 * 0.5 * amt
    out = out * (1 - m) + np.array((0.95, 0.9, 0.8), np.float32) * m
    out = out * (vignette(0.9)[..., None] * amt + (1 - amt))
    return np.clip(out, 0, 1)


def aurora(c, t, amt=1.0, y0=0.18, y1=0.55):
    """Aurora ribbons in the four BMHC colours, drifting (screen blend)."""
    if amt <= 0:
        return c
    xs = np.linspace(0, 1, W // 4, dtype=np.float32)
    ys = np.linspace(0, 1, H // 4, dtype=np.float32)[:, None]
    acc = np.zeros((H // 4, W // 4, 3), np.float32)
    for i, col in enumerate(BARS):
        ph = i * 1.7
        cy = y0 + (y1 - y0) * (i / 3) + 0.05 * np.sin(xs * 5 + t * 0.9 + ph) + 0.03 * np.sin(xs * 13 - t * 1.4 + ph)
        width = 0.035 + 0.02 * np.sin(xs * 7 + t + ph) ** 2
        band = np.exp(-((ys - cy) / width) ** 2)
        curtain = np.clip((ys - cy + 0.18) / 0.18, 0, 1) * np.clip((cy - ys + 0.02) / 0.02 + 1, 0, 1)
        rays = 0.6 + 0.4 * np.sin(xs * 90 + t * 3 + ph) ** 2
        v = (band * 0.9 + np.exp(-((ys - cy + 0.08) / 0.09) ** 2) * 0.35 * rays) * (0.55 + 0.45 * np.sin(xs * 3 + t * 0.6 + ph) ** 2)
        acc += v[..., None] * col
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_CUBIC)
    acc = cv2.GaussianBlur(acc, (0, 0), 6) * amt
    return 1 - (1 - c) * (1 - np.clip(acc, 0, 1))


# ------------------------------------------------------------------ logo
@functools.lru_cache(None)
def logo(width=820):
    """BMHC's own reversed logo (white building + wordmark) with its four colour bars, from the supplied website files."""
    IMG = f'{ROOT}/workspace_bmhc/web/img'
    lw = load(f'{IMG}/bmhc-white-logo.png')
    lc = load(f'{IMG}/Website-1-2.png')
    h = lw.shape[0]
    cut = int(h * 0.86)
    out = lw.copy()
    out[cut:] = lc[cut:]
    sc = width / out.shape[1]
    big = cv2.resize(out, (width, int(out.shape[0] * sc)), interpolation=cv2.INTER_CUBIC)
    bl = cv2.GaussianBlur(big, (0, 0), 1.0)
    return np.clip(big * 1.5 - bl * 0.5, 0, 1)
