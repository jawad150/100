"""Look for BMHC "Manchester, can you name this place by ear?" - rebuilt scene by scene from the user's Pinterest
reference (a product-launch motion piece): soft gradient light scenes with colour blobs, dark scenes with a glowing
blob 'landscape', kinetic words with a highlight box, floating 3D objects and notification pills, orbiting nodes,
floating cards in perspective, confetti, logo reveal and end card.
BMHC brand: ink #0B0B0B, white/mist, Heritage Magenta (clue numbers, key words), teal/orange/lime only as accents,
Inter ExtraBold subtitles (white on ink, 2-3 words), sound captions in [brackets], official reversed logo at the end.
"""
import os, sys, math, functools
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ai'))
import frames_ai as FA
from frames_ai import (W, H, INK, CHAR, WHITE, MAG, TEAL, ORANGE, LIME, BARS, load, cover, paste, rrect, text_sprite, caption, F,
                       clamp, prog, e_out, e_inout, e_back, _grid, grain, logo, Clip, tag)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_ear'
MIST = np.array((0.965, 0.96, 0.945), np.float32)


@functools.lru_cache(maxsize=8)
def light_bg(seed=0):
    """White/mist with soft magenta + teal blobs (the reference's white-to-lime gradient, in BMHC colours)."""
    yy, xx = _grid()
    c = np.empty((H, W, 3), np.float32)
    c[:] = MIST
    rng = np.random.default_rng(seed)
    for col, (cx, cy, r) in ((MAG, (W * 0.85, H * 0.12, 420)), (TEAL, (W * 0.1, H * 0.9, 520)), (MAG, (W * 0.05, H * 0.35, 260))):
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2))[..., None] * 0.55
        c = c * (1 - g) + (col * 0.55 + MIST * 0.45) * g
    return c.astype(np.float32)


@functools.lru_cache(maxsize=8)
def dark_bg(seed=0, landscape=False):
    """Ink with magenta/teal glow; optional glowing blob 'landscape' at the bottom (reference scene 4)."""
    yy, xx = _grid()
    c = np.empty((H, W, 3), np.float32)
    c[:] = INK
    for col, (cx, cy, r, a) in ((MAG, (W * 0.8, H * 0.2, 520, 0.22)), (TEAL, (W * 0.15, H * 0.55, 480, 0.15))):
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r ** 2))[..., None] * a
        c = c + col * g
    if landscape:
        ridge = H * 0.72 + 70 * np.sin(xx / 210 + 0.6) + 40 * np.sin(xx / 97)
        d = (yy - ridge) / 90
        body = np.clip(d, 0, 1)[..., None]
        glow = np.exp(-np.clip(-d, 0, None) ** 2 * 2)[..., None] * (d < 0)[..., None]
        rng = np.random.default_rng(seed)
        speck = (rng.random((H, W)) > 0.985).astype(np.float32)[..., None] * body * 0.5
        c = c * (1 - body) + (MAG * 0.36 + np.array((0.04, 0.02, 0.03), np.float32)) * body + MAG * glow * 0.3 + speck
    return np.clip(c, 0, 1).astype(np.float32)


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
        im = cv2.warpAffine(im, R, (w_, h_), flags=cv2.INTER_CUBIC)
    return im


def pop(c, name, cx, cy, size, u, rot=0, shadow=True, a=1.0, glow=None):
    if u <= 0 or a <= 0:
        return c
    s = e_back(clamp(u / 0.4))
    if s < 0.02:
        return c
    spr = token(name, max(8, int(size * s)), int(rot))
    al = clamp(u / 0.12) * a
    bob = math.sin(u * 2.3) * 8 * clamp(u - 0.4)
    if shadow:
        m = cv2.GaussianBlur(np.pad(spr[..., 3], 40), (0, 0), 16) * 0.4
        paste(c, np.dstack([np.zeros(m.shape + (3,), np.float32), m]), cx + 10, cy + 26 + bob, al)
    if glow is not None:
        g = cv2.GaussianBlur(np.pad(spr[..., 3], 60), (0, 0), 30)
        paste(c, np.dstack([g[..., None] * np.asarray(glow, np.float32), g]).astype(np.float32) * 0.6, cx, cy + bob, al)
    return paste(c, spr, cx, cy + bob, al)


def word(c, s, x, y, size, col=WHITE, u=1.0, w=800, a=1.0, anchor='c'):
    if u <= 0 or a <= 0:
        return c
    k = e_back(clamp(u / 0.3), 1.4)
    spr = text_sprite(s, w, size * (0.7 + 0.3 * k), col, alpha=clamp(u / 0.12) * a)
    ox = 0 if anchor == 'c' else spr.shape[1] / 2
    return paste(c, spr, x + ox, y + 16 * (1 - k))


def highlight(c, s, x, y, size, u, box=MAG, txt=WHITE):
    """The reference's highlighted word: a box that wipes on, the word inside, little bracket ticks."""
    if u <= 0:
        return c
    spr = text_sprite(s, 800, size, txt)
    w, h = spr.shape[1] + 30, int(size * 1.35)
    k = e_out(clamp(u / 0.35))
    paste(c, rrect(max(4, w * k), h, 10, box, 0.95), x - w / 2 + w * k / 2, y)
    if k > 0.6:
        paste(c, spr, x, y, clamp((k - 0.6) / 0.3))
    for s_ in (-1, 1):
        paste(c, rrect(6, h + 26, 3, box, 1.0), x + s_ * (w / 2 + 14), y, clamp(u / 0.2))
    return c


def pill(c, text, x, y, u, dark=True, a=1.0, icon=None):
    """Notification pill (reference scene 3) carrying a sound caption, e.g. [ball bouncing]."""
    if u <= 0 or a <= 0:
        return c
    k = e_back(clamp(u / 0.35))
    s = text_sprite(text, 700, 38, WHITE if dark else INK)
    w, h = s.shape[1] + 120, 86
    bg = CHAR if dark else np.array((1, 1, 1), np.float32)
    paste(c, rrect(w * k, h * k, h * k / 2, bg, 0.94), x, y, a)
    if k > 0.5:
        dot = rrect(46, 46, 23, MAG, 1.0)
        paste(c, dot, x - w / 2 + 50, y, a)
        paste(c, s, x + 30, y, a * clamp((k - 0.5) / 0.3))
    return c


def clue_no(c, n, x, y, u, size=300):
    """Big clue number in Heritage Magenta (brief)."""
    return word(c, f'0{n}', x, y, size, MAG, u, 800)


def card(c, img, cx, cy, w, h, u, tilt=0.0, label=None, a=1.0):
    """Floating rounded card in slight perspective (reference scene 8) holding a wide shot."""
    if u <= 0 or a <= 0:
        return c
    k = e_back(clamp(u / 0.45), 1.2)
    ww, hh = int(w * k), int(h * k)
    if ww < 10:
        return c
    im = cv2.resize(img, (ww, hh), interpolation=cv2.INTER_AREA)
    m = rrect(ww, hh, 26 * k, (1, 1, 1), 1.0)[..., 3]
    spr = np.dstack([im * m[..., None], m])
    if tilt:
        src = np.float32([[0, 0], [ww, 0], [ww, hh], [0, hh]])
        d = tilt * ww
        dst = np.float32([[0, d * 0.4], [ww, 0], [ww, hh], [0, hh - d * 0.4]])
        Mx = cv2.getPerspectiveTransform(src, dst)
        spr = cv2.warpPerspective(spr, Mx, (ww, hh))
    sh = cv2.GaussianBlur(np.pad(spr[..., 3], 50), (0, 0), 20) * 0.5
    paste(c, np.dstack([np.zeros(sh.shape + (3,), np.float32), sh]), cx + 14, cy + 30, a)
    paste(c, spr, cx, cy, a)
    if label:
        pill(c, label, cx, cy + hh / 2 + 30, u - 0.3, dark=True, a=a)
    return c


def orbit(c, cx, cy, r, t, items, u):
    """Orbiting nodes (reference scene 7): a dotted ring with small round nodes riding it."""
    lay = np.zeros((H, W), np.uint8)
    n = 80
    for i in range(0, n, 2):
        a0 = i * 360 / n + t * 12
        cv2.ellipse(lay, (int(cx * 4), int(cy * 4)), (int(r * 4), int(r * 4)), 0, a0, a0 + 360 / n * 0.6, 255, 3 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * clamp(u / 0.4) * 0.5
    c[:] = c * (1 - m) + np.array((0.95, 0.9, 0.95), np.float32) * m
    for i, (col, sz) in enumerate(items):
        ang = math.radians(t * 22 + i * 360 / len(items))
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        k = e_back(clamp((u - 0.1 * i) / 0.3))
        if k > 0:
            paste(c, rrect(sz * k, sz * k, sz * k / 2, col, 1.0), x, y)
            paste(c, rrect(sz * k * 0.45, sz * k * 0.45, sz * k * 0.225, (1, 1, 1), 0.9), x, y)
    return c


def confetti(c, t, u, n=60, seed=3):
    """Falling four-colour confetti (the reference's emoji burst, in BMHC bar colours)."""
    if u <= 0:
        return c
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(40, W - 40)
        y0 = rng.uniform(-400, 200)
        sp = rng.uniform(250, 520)
        y = y0 + sp * u
        col = BARS[i % 4]
        ang = (rng.uniform(0, 180) + u * rng.uniform(-200, 200))
        w_, h_ = rng.uniform(16, 30), rng.uniform(30, 52)
        spr = rrect(w_, h_, 5, col, 1.0)
        R = cv2.getRotationMatrix2D((w_ / 2, h_ / 2), ang, 1.0)
        spr = cv2.warpAffine(spr, R, (int(w_ * 1.8), int(h_ * 1.4)))
        paste(c, spr, x, y, clamp(1.6 - u))
    return c
