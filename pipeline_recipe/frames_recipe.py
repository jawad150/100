"""Scene images for Organic Fostering Reel 01 "The Recipe That Wasn't on the Menu" (PDF script word for word).

A kitchen micro-story told with six looks, each tied to a beat of the script:
  RETRO      "She had made this meal a hundred times."  super-8 memory: film frame, sprockets, grain, light leak, tally
  ECLIPSE    "But tonight, she made it differently."    a dark disc slides over the old memory, corona flare, present day
  LAYERCUT   "A different ingredient."                  the spice shot splits into paper-cut layers with soft shadows
  EXPLAINER  "A familiar flavour. A recipe worth learning."  hand-drawn circles, dashed arrows, step labels on the footage
  SPIRAL     "Because caring for a child isn't about asking them to become like you."  swirl into the cookie cutter
  AURORA     "It's about understanding who they already are."  brand-colour aurora ribbons, a seedling rising
then culture / faith / identity pop-ups, "Room to grow. Roots to keep." and the ivory end card.
Brand: Nunito, plum/magenta/orange/green on ivory, rounded photo corners, leaf pattern, three-colour bar, no
exclamation marks. Adults only on camera; no child shown directly.

Usage: python3 frames_recipe.py [n ...] -> workspace_recipe/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_three'))
import numpy as np
import cv2
import frames_three as F3
from frames_three import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, cover)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_recipe'
OUT = f'{S}/frames'
F3.S = f'{ROOT}/workspace_three'
_X, _Y = R._X, R._Y
hexc = R.hexc
PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')
IVORY, PAPER, BLUSH, PEACH, LEAFT = hexc('#FCF8F5'), hexc('#FFFDFB'), hexc('#F6EAF3'), hexc('#FFD4BA'), hexc('#E8F3D8')
INK, ORANGE_INK, GREEN_INK = hexc('#321F35'), hexc('#933900'), hexc('#3F6F08')
WHITE = (1, 1, 1, 1)
N8, N7, N9 = 'Nunito-800', 'Nunito-700', 'Nunito-900'
HAND = 'Caveat-700'


# ------------------------------------------------------------------ sources
def frame_of(cid, t):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def warm(im, amt=1.0):
    """Brand photography: soft daylight, warm highlights, gentle contrast."""
    lum = im.mean(2, keepdims=True)
    im = np.clip((im - 0.5) * 1.05 + 0.52, 0, 1)
    im = im + np.clip((lum - 0.5) * 2, 0, 1) * np.array([0.05, 0.02, -0.03], np.float32) * amt
    return np.clip(im, 0, 1).astype(np.float32)


def shot(cid, t, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    return warm(cover(frame_of(cid, t), fx, fy, z, w, h))


_TOK = {}


def token(name):
    if name not in _TOK:
        p = f'{S}/assets/{name}.png'
        if not os.path.exists(p):
            p = f'{ROOT}/workspace_nq/assets/{name}.png'
        sp = load_png_sprite(p)
        ys, xs = np.where(sp[..., 3] > 0.01)
        _TOK[name] = np.ascontiguousarray(sp[max(0, ys.min() - 6):ys.max() + 7, max(0, xs.min() - 6):xs.max() + 7])
    return _TOK[name]


def pop(c, name, x, y, size, rot=0, rays=True, col=ORANGE):
    sp = token(name)
    sc = size / max(sp.shape[:2])
    if rays:
        lay = np.zeros((H, W), np.uint8)
        r0 = size * 0.52
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = 26 if j % 2 else 42
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((y + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + ln)) * 4), int((y + math.sin(a) * (r0 + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.85
        c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    draw(c, blur_sprite(tint(sp, PLUM[:3]), 20), x + 8, y + 24, scale=sc, rot=rot, opacity=0.45)
    draw(c, sp, x, y, scale=sc, rot=rot)


def rounded(img, r=40):
    h, w = img.shape[:2]
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, r, 2)), (w, h))
    return np.concatenate([img * m[..., None], m[..., None]], 2).astype(np.float32)


def caption(c, lines, keys=(), y=1560, size=64, hl=MAG, col=WHITE):
    """Nunito ExtraBold captions (voice = captions); cue words on a brand-colour highlight, always white on it."""
    lines = [lines] if isinstance(lines, str) else lines
    while size > 36:
        wmax = max(sum(_wmask(w, N8, size).shape[1] for w in l.split()) + size * 0.24 * (len(l.split()) - 1) for l in lines)
        if wmax <= W - 130:
            break
        size -= 2
    light = col != WHITE
    for li, l in enumerate(lines):
        ws = l.split()
        ms = [_wmask(w, N8, size) for w in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ms) - 1)
        x = W / 2 - tw / 2
        yy = y + li * size * 1.24
        for w, m in zip(ws, ms):
            cx = x + m.shape[1] / 2
            key = w.strip('.,?…:').lower() in keys
            if key:
                draw(c, rrect(m.shape[1] + 22, size * 1.14, 18, hl), cx, yy + 3)
            elif not light:
                draw(c, blur_sprite(solid(m, (0.1, 0.02, 0.08, 1)), 10), cx + 3, yy + 7, opacity=0.6)
            draw(c, solid(m, WHITE if key else col), cx, yy)
            x += m.shape[1] + size * 0.24


def shade(c, top=0.62, amt=0.78, col=PLUM):
    g = np.clip((_Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    return c * (1 - amt * g) + np.array(col[:3], np.float32) * amt * g


def top_shade(c, h=0.22, amt=0.45):
    g = np.clip(1 - _Y / (H * h), 0, 1)[..., None] ** 1.5
    return c * (1 - amt * g)


def overlay_text(c, s, x, y, size=70, col=WHITE, font=HAND, rot=-3, shadow=True):
    sp = solid(_wmask(s, font, size), col)
    if shadow:
        draw(c, blur_sprite(solid(_wmask(s, font, size), (0.1, 0.02, 0.08, 1)), 10), x + 4, y + 8, rot=rot, opacity=0.6)
    draw(c, sp, x, y, rot=rot)


def colour_bar(c, y=H - 14, h=14):
    for i, col in enumerate((MAG, ORANGE, GREEN)):
        c[y:y + h, i * W // 3:(i + 1) * W // 3] = np.array(col[:3], np.float32)


# ------------------------------------------------------------------ the six looks
def retro(img, t=0.0, seed=1):
    """Super-8 memory: faded warm grade, heavy grain, gate weave, scratches, light leak, cream film frame with sprockets."""
    rng = np.random.default_rng(seed + int(t * 24))
    lum = img.mean(2, keepdims=True)
    im = img * 0.72 + lum * 0.28
    im = im * np.array([1.08, 0.98, 0.82], np.float32) + np.array([0.06, 0.03, 0.0], np.float32)
    im = np.clip((im - 0.5) * 0.86 + 0.52, 0, 1)
    g = rng.normal(0, 0.055, (H // 2, W // 2, 1)).astype(np.float32)
    im = np.clip(im + cv2.resize(g, (W, H))[..., None], 0, 1)
    leak = np.exp(-(((_X - 980 - 60 * math.sin(t * 1.3)) / 380) ** 2 + ((_Y - 380) / 700) ** 2))[..., None]
    im = np.clip(im + leak * np.array([0.45, 0.18, 0.02], np.float32), 0, 1)
    for _ in range(3):
        x = rng.integers(60, W - 60)
        im[:, x:x + 2] = np.clip(im[:, x:x + 2] + 0.18, 0, 1)
    dx, dy = rng.normal(0, 2.0), rng.normal(0, 2.0)
    im = cv2.warpAffine(im, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    v = np.clip(1 - (((_X - W / 2) / (W * 0.62)) ** 2 + ((_Y - H / 2) / (H * 0.62)) ** 2), 0, 1)[..., None]
    im = im * (0.45 + 0.55 * v)
    # film frame: dark gate with rounded window and sprocket holes
    gate = np.ones((H, W, 3), np.float32) * np.array([0.09, 0.06, 0.05], np.float32)
    win = rounded(np.ones((H - 260, W - 170, 3), np.float32), 46)
    m = np.zeros((H, W), np.float32)
    m[130:130 + win.shape[0], 120:120 + win.shape[1]] = win[..., 3]
    out = gate * (1 - m[..., None]) + im * m[..., None]
    for k in range(9):
        y = 90 + k * 220
        cv2.rectangle(out, (26, y), (86, y + 110), (0.82, 0.76, 0.66), -1, cv2.LINE_AA)
    return out


def date_stamp(c, s="'98", x=880, y=1700):
    sp = solid(_wmask(s, 'Inter-700', 60), (1.0, 0.55, 0.15, 1))
    draw(c, blur_sprite(sp, 6), x, y, opacity=0.8)
    draw(c, sp, x, y)


def eclipse(a, b, k, cx=540, cy=820):
    """A dark moon slides over the old frame; inside the disc the present is revealed; a corona flares at totality."""
    r = 330 + 1300 * max(0, k - 0.55) ** 1.6
    mx = cx + (1 - min(1, k / 0.55)) * 900
    d = np.hypot(_X - mx, _Y - cy)
    disc = np.clip((r - d) / 3, 0, 1)[..., None]
    out = a * (1 - disc) + b * disc
    tot = math.exp(-((k - 0.55) / 0.12) ** 2)
    ring = np.exp(-((d - r) / (10 + 40 * tot)) ** 2)[..., None] * (0.35 + 0.9 * tot)
    corona = np.exp(-np.clip(d - r, 0, None) / 160)[..., None] * (d > r)[..., None] * 0.6 * tot
    out = out + ring * np.array([1.0, 0.75, 0.35], np.float32) + corona * np.array([1.0, 0.5, 0.15], np.float32)
    out = out * (1 - 0.35 * tot * (d > r)[..., None])
    return np.clip(out, 0, 1)


def layercut(img, k=1.0, n=6, seed=3):
    """Paper-cut layers: the frame is sliced by wavy cuts; alternate layers slide apart, each casts a soft shadow,
    brand-colour paper shows in the gaps."""
    rng = np.random.default_rng(seed)
    out = np.ones_like(img) * np.array(BLUSH[:3], np.float32)
    edges = [0]
    for i in range(1, n):
        edges.append(H * i / n + rng.uniform(-60, 60))
    edges.append(H)
    cols = (MAG, ORANGE, GREEN, PLUM, PEACH, MAG)
    layers = []
    for i in range(n):
        ph = rng.uniform(0, 6)
        top = edges[i] + 26 * np.sin(_X[0] / 140 + ph)
        bot = edges[i + 1] + 26 * np.sin(_X[0] / 140 + ph + 1.7) if i < n - 1 else np.full(W, H, np.float32)
        m = ((_Y >= top[None, :]) & (_Y < bot[None, :])).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 0.8)
        dx = (1 if i % 2 else -1) * 70 * k
        dy = (i - n / 2) * 10 * k
        layers.append((m, dx, dy, cols[i % len(cols)]))
    for i, (m, dx, dy, col) in enumerate(layers):
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        mm = cv2.warpAffine(m, M, (W, H))
        im = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        back = cv2.warpAffine(m, np.float32([[1, 0, dx * 0.5], [0, 1, dy * 0.5 + 10]]), (W, H))
        out = out * (1 - back[..., None] * 0.9) + np.array(col[:3], np.float32) * back[..., None] * 0.9
        sh = cv2.GaussianBlur(mm, (0, 0), 14)
        sh = np.roll(sh, 16, 0)
        out = out * (1 - 0.45 * sh[..., None])
        out = out * (1 - mm[..., None]) + im * mm[..., None]
    return np.clip(out, 0, 1)


def spiral(a, b, k):
    """Spiral swirl: the old frame twists into a vortex; the new one unwinds out of it."""
    def twist(img, amt):
        r = np.hypot(_X - W / 2, _Y - H / 2)
        th = np.arctan2(_Y - H / 2, _X - W / 2) + amt * np.exp(-r / 520)
        mx = (W / 2 + r * np.cos(th)).astype(np.float32)
        my = (H / 2 + r * np.sin(th)).astype(np.float32)
        return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    e = 0.5 - 0.5 * math.cos(math.pi * k)
    A = twist(a, 9 * e)
    B = twist(b, -9 * (1 - e))
    r = np.hypot(_X - W / 2, _Y - H / 2)
    th = np.arctan2(_Y - H / 2, _X - W / 2)
    arm = ((th / (2 * math.pi) + r / 420) % 1.0)
    m = np.clip((e * 1.4 - arm * 0.4 - (1 - e) * 0.6) * 4, 0, 1)[..., None]
    m = np.maximum(m, np.clip((e - 0.75) * 4, 0, 1))
    return A * (1 - m) + B * m


AUR = [(MAG, 0.0, 260, 0.8), (ORANGE, 1.7, 400, 0.55), (GREEN, 3.1, 520, 0.6), (MAG, 4.4, 650, 0.45), (GREEN, 5.6, 330, 0.35)]


def aurora(t=0.0):
    """Brand-colour aurora: flowing light curtains over deep plum, with fine vertical rays and stars."""
    c = np.ones((H, W, 3), np.float32) * np.array([0.13, 0.03, 0.12], np.float32)
    k = (_Y / H)[..., None]
    c = c * (1 - 0.5 * k) + np.array(PLUM[:3], np.float32) * 0.6 * k
    rays = 0.75 + 0.25 * np.sin(_X / 9.0 + np.sin(_X / 70 + t) * 3)
    for col, ph, yc, a in AUR:
        curve = yc + 120 * np.sin(_X / 230 + ph + t * 0.6) + 60 * np.sin(_X / 97 + ph * 2 + t)
        d = (_Y - curve[0][None, :] if curve.ndim > 1 else _Y - curve)
        band = np.exp(-np.clip(d, 0, None) / 260) * np.exp(-np.clip(-d, 0, None) / 40) * rays
        c = c + band[..., None] * np.array(col[:3], np.float32) * a
    rng = np.random.default_rng(5)
    for _ in range(90):
        x, y = rng.integers(0, W), rng.integers(0, int(H * 0.7))
        cv2.circle(c, (int(x), int(y)), int(rng.integers(1, 3)), (1, 1, 1), -1, cv2.LINE_AA)
    return np.clip(c, 0, 1)


def dashed_circle(c, x, y, rx, ry, col=WHITE, th=6, k=1.0, rot=-8):
    lay = np.zeros((H, W), np.uint8)
    n = 44
    for i in range(int(n * k)):
        if i % 2:
            continue
        a0, a1 = i / n * 2 * math.pi, (i + 1) / n * 2 * math.pi
        cv2.ellipse(lay, (int(x * 4), int(y * 4)), (int(rx * 4), int(ry * 4)), rot, math.degrees(a0), math.degrees(a1), 255, th * 4,
                    cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def arrow(c, p0, p1, col=WHITE, th=6, bend=60):
    pts = []
    for u in np.linspace(0, 1, 30):
        x = p0[0] + (p1[0] - p0[0]) * u
        y = p0[1] + (p1[1] - p0[1]) * u - bend * math.sin(math.pi * u)
        pts.append((x, y))
    lay = np.zeros((H, W), np.uint8)
    for i in range(0, len(pts) - 1, 2):
        cv2.line(lay, (int(pts[i][0] * 4), int(pts[i][1] * 4)), (int(pts[i + 1][0] * 4), int(pts[i + 1][1] * 4)), 255, th * 4, cv2.LINE_AA, shift=2)
    ex, ey = pts[-1]
    px, py = pts[-3]
    a = math.atan2(ey - py, ex - px)
    for s_ in (2.5, -2.5):
        cv2.line(lay, (int(ex * 4), int(ey * 4)), (int((ex - 34 * math.cos(a + s_ * 0.2)) * 4), int((ey - 34 * math.sin(a + s_ * 0.2)) * 4)),
                 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def label(c, text, x, y, fill=PAPER, ink=PLUM, leaf=MAG, size=36, rot=-3):
    """Brand pillar tag: rounded pill, leaf, sentence-case word."""
    s = ts(text, N8, size, ink)
    p = rrect(s.shape[1] + 86, s.shape[0] + 34, (s.shape[0] + 34) / 2, fill).copy()
    lf = np.zeros((40, 40), np.uint8)
    cv2.ellipse(lf, (20, 20), (16, 8), -45, 0, 360, 255, -1, cv2.LINE_AA)
    paste_spr(p, solid(lf.astype(np.float32) / 255, leaf), 38, p.shape[0] / 2)
    paste_spr(p, s, 62 + s.shape[1] / 2, p.shape[0] / 2)
    draw(c, blur_sprite(tint(p, (0.15, 0.03, 0.12)), 12), x + 6, y + 10, rot=rot, opacity=0.45)
    draw(c, p, x, y, rot=rot)


@functools.lru_cache(maxsize=2)
def leaf_pattern(bg=BLUSH):
    c = np.ones((H, W, 3), np.float32) * np.array(bg[:3], np.float32)
    rng = np.random.default_rng(8)
    for gy in range(0, H + 60, 90):
        for gx in range(0, W + 60, 90):
            col = rng.choice([0, 0, 0, 0, 0, 0, 1, 2])
            colr = (PLUM, MAG, GREEN)[col]
            lf = np.zeros((40, 40), np.uint8)
            cv2.ellipse(lf, (20, 20), (17, 8), [-45, 45][(gx // 90 + gy // 90) % 2], 0, 360, 255, -1, cv2.LINE_AA)
            draw(c, solid(lf.astype(np.float32) / 255, colr), gx + (45 if (gy // 90) % 2 else 0), gy, opacity=0.22)
    return c


@functools.lru_cache(maxsize=1)
def LOGO():
    return F3.logo()


# ------------------------------------------------------------------ scenes (one per voice beat)
def s01():   # RETRO: "She had made this meal a hundred times."
    c = retro(shot('3806', 5.0, 0.5, 0.5, 1.15))
    overlay_text(c, "She'd made this", 420, 330, 80, (1, 0.93, 0.8, 1))
    overlay_text(c, '100 times.', 470, 430, 110, (1, 0.6, 0.2, 1), rot=-4)
    lay = np.zeros((H, W), np.uint8)                                   # tally marks
    for g in range(4):
        x0 = 200 + g * 150
        for i in range(4):
            cv2.line(lay, ((x0 + i * 24) * 4, 1190 * 4), ((x0 + i * 24 - 5) * 4, 1280 * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
        cv2.line(lay, ((x0 - 16) * 4, 1262 * 4), ((x0 + 92) * 4, 1206 * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array([1, 0.92, 0.78], np.float32) * m
    pop(c, 'pot', 800, 1030, 260, rays=False)
    date_stamp(c)
    caption(c, ['She had made this meal', 'a hundred times.'], keys=('hundred',), hl=ORANGE, y=1500)
    return c


def s02():   # RETRO hands at work (the same routine)
    c = retro(shot('26660', 6.0, 0.5, 0.5, 1.0), seed=4)
    overlay_text(c, 'same routine', 380, 360, 72, (1, 0.93, 0.8, 1))
    date_stamp(c, "'04")
    caption(c, ['She had made this meal', 'a hundred times.'], keys=('hundred',), hl=ORANGE, y=1500)
    return c


def s03():   # ECLIPSE: "But tonight…" — the moon slides over the memory, the present appears inside
    a = retro(shot('26660', 7.0, 0.5, 0.5, 1.0), seed=6)
    b = shot('42655', 3.0, 0.45, 0.5, 1.05)
    c = eclipse(a, b, 0.58)
    caption(c, ['But tonight, she made it', 'differently.'], keys=('tonight', 'differently'), hl=MAG, y=1500)
    return c


def s04():   # the recipe card reveal (present day, clean)
    c = shot('42655', 4.5, 0.45, 0.5, 1.05)
    c = top_shade(c)
    pop(c, 'recipecard', 700, 760, 430, rot=6)
    overlay_text(c, 'But tonight…', 360, 380, 100, WHITE, rot=-4)
    c = shade(c)
    caption(c, ['But tonight, she made it', 'differently.'], keys=('tonight', 'differently'), hl=MAG, y=1500)
    return c


def s05():   # LAYERCUT: "A different ingredient."
    c = layercut(shot('32058', 4.0, 0.5, 0.5, 1.0), 1.0)
    pop(c, 'spicejar', 540, 900, 380)
    label(c, 'new ingredient', 540, 1210, fill=PEACH, ink=ORANGE_INK, leaf=ORANGE)
    caption(c, ['A different ingredient.'], keys=('different', 'ingredient'), hl=ORANGE, y=1560, size=70)
    return c


def s06():   # EXPLAINER: "A familiar flavour. A recipe worth learning."
    c = shot('32504', 9.0, 0.5, 0.5, 1.0)
    c = top_shade(c)
    dashed_circle(c, 470, 930, 300, 300, WHITE, 6, rot=-8)
    arrow(c, (840, 520), (640, 760), WHITE, 6, bend=60)
    label(c, 'familiar flavour', 760, 470, fill=BLUSH, ink=PLUM, leaf=MAG)
    for i, (txt, col, lf, ink) in enumerate((('1  spice', PEACH, ORANGE, ORANGE_INK), ('2  stir', BLUSH, MAG, PLUM), ('3  taste', LEAFT, GREEN, GREEN_INK))):
        label(c, txt, 230 + i * 300, 1300, fill=col, ink=ink, leaf=lf, size=34, rot=(-4, 2, -2)[i])
    pop(c, 'bowl', 860, 1060, 240, rays=False)
    overlay_text(c, 'A recipe worth learning.', 540, 300, 76, WHITE, rot=-2)
    c = shade(c, 0.7)
    caption(c, ['A familiar flavour.', 'A recipe worth learning.'], keys=('learning',), hl=GREEN, y=1530)
    return c


def s07():   # SPIRAL: "Because caring for a child isn't about asking them to become like you."
    a = shot('47555', 10.0, 0.5, 0.5, 1.0)
    b = leaf_pattern()
    c = spiral(a, b, 0.55)
    pop(c, 'cutter', 540, 820, 420, rays=False)
    c = shade(c, 0.66)
    caption(c, ["Because caring for a child isn't about", 'asking them to become like you.'], keys=('like', 'you'), hl=MAG, y=1530, size=54)
    return c


def s08():   # the cookie cutter lifts away: same shape is not the point
    c = leaf_pattern().copy()
    for i, (x, y) in enumerate(((300, 700), (540, 640), (780, 700))):
        st = np.zeros((220, 220), np.uint8)
        pts = np.array([[110 + (95 if j % 2 == 0 else 45) * math.sin(j * math.pi / 5), 110 - (95 if j % 2 == 0 else 45) * math.cos(j * math.pi / 5)]
                        for j in range(10)], np.int32)
        cv2.fillPoly(st, [pts], 255, cv2.LINE_AA)
        draw(c, solid(st.astype(np.float32) / 255, (PEACH, BLUSH, LEAFT)[i]), x, y, rot=(-10, 0, 12)[i], opacity=0.9)
    pop(c, 'cutter', 540, 1000, 340, rays=False, rot=10)
    dashed_circle(c, 540, 680, 380, 170, MAG, 6, rot=0)
    caption(c, ["Because caring for a child isn't about", 'asking them to become like you.'], keys=('like', 'you'), hl=MAG, y=1530, size=54, col=PLUM)
    return c


def s09():   # AURORA: "It's about understanding who they already are."
    c = aurora(0.0)
    pop(c, 'seedling', 540, 1000, 620, rays=False)
    overlay_text(c, 'Who they are matters.', 540, 460, 92, WHITE, rot=-2)
    caption(c, ["It's about understanding", 'who they already are.'], keys=('already', 'are'), hl=GREEN, y=1520)
    return c


def s10():   # "At Organic Fostering, culture, faith and identity matter."
    c = leaf_pattern().copy()
    ph = rounded(shot('45977', 3.0, 0.55, 0.5, 1.0, 900, 620), 40)
    draw(c, blur_sprite(tint(ph, PLUM[:3]), 24), 552, 560, opacity=0.4)
    draw(c, ph, 540, 540)
    for i, (obj, lab, x, fill, ink, lf) in enumerate((('culture', 'Culture', 210, PEACH, ORANGE_INK, ORANGE),
                                                      ('lantern', 'Faith', 540, BLUSH, PLUM, MAG),
                                                      ('identity', 'Identity', 870, LEAFT, GREEN_INK, GREEN))):
        pop(c, obj, x, 1050, 250, rays=(i == 1))
        label(c, lab, x, 1250, fill=fill, ink=ink, leaf=lf, size=38, rot=(-4, 2, -3)[i])
    caption(c, ['At Organic Fostering, culture,', 'faith and identity matter.'], keys=('culture', 'faith', 'identity'), hl=MAG, y=1510, size=58, col=PLUM)
    return c


def s11():   # "Room to grow. Roots to keep."
    c = np.ones((H, W, 3), np.float32) * np.array(PLUM[:3], np.float32)
    k = (_Y / H)[..., None]
    c = c * (1 - 0.25 * k) + np.array([0.12, 0.03, 0.1], np.float32) * 0.25 * k
    pop(c, 'seedling', 540, 860, 700, rays=False)
    draw(c, ts('Room to grow.', N8, 96, WHITE), 540, 1330)
    draw(c, ts('Roots to keep.', N8, 96, PEACH), 540, 1450)
    colour_bar(c)
    return c


def s12():   # end card
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    lg = LOGO()
    draw(c, lg, 540, 520, scale=820 / lg.shape[1])
    draw(c, ts('Room to grow.', N8, 84, PLUM), 540, 860)
    draw(c, ts('Roots to keep.', N8, 84, MAG), 540, 960)
    btn = rrect(640, 124, 62, MAG)
    draw(c, blur_sprite(tint(btn, PLUM[:3]), 20), 540, 1180, opacity=0.4)
    draw(c, btn, 540, 1160)
    draw(c, ts('Start your enquiry', N8, 50, WHITE), 540, 1160)
    draw(c, ts('0161 241 1332', N8, 60, PLUM), 540, 1330)
    draw(c, ts('organicfostering.co.uk', N7, 40, hexc('#655563')), 540, 1405)
    colour_bar(c, H - 40, 40)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    which = [int(a) for a in sys.argv[1:]] or range(1, len(SCENES) + 1)
    for j in which:
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', to_u8(SCENES[j - 1]()))
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (270, 480), interpolation=cv2.INTER_AREA) for f in fs]
    while len(th) % 6:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 6]) for i in range(0, len(th), 6)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
