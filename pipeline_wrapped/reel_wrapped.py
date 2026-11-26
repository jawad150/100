"""BMHC "Wrapped 2026" reel - 9:16, 43 s, 30 fps. A year-in-review in the 'Wrapped' format (December trend), opened in
the language of the user's reference (light ground with soft colour corners, a sentence with one accented word, UI cards,
a cursor tap), then full-screen Wrapped story slides in BMHC colours with 3D objects, ending on a circle wipe to the logo.

Facts used are only those that are true or stated on bmhc.org.uk (130K+ visitors a year, 14 awards, 12+ years,
Heritage Radio 90.6 FM / DAB+ / app / Alexa, 52 Fridays in 2026). Top-5 order: for BMHC to confirm.

Usage: python3 reel_wrapped.py still 1,5 | range a b
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_wrapped'
FON = f'{ROOT}/workspace_sol/fonts'
OBJ = f'{ROOT}/workspace_bmhc_posts/assets'
IMG = f'{ROOT}/workspace_bmhc/web/img'
W, H = 1080, 1920
FPS = 30
import json, re
INFO = json.load(open(f'{S}/tts/info.json'))
DUR = INFO['dur']
NF = int(DUR * FPS)


def WT(word, line):
    """Start time of the first word in a narration line that begins with `word`."""
    for w in INFO['words']:
        if w[3] == line and re.sub(r"[^a-z0-9]", '', w[0].lower()).startswith(word):
            return w[1]
    return INFO['lines'][line][0]


def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


INK, CHAR, SLATE, STONE, MIST, WHITE = hx('#0B0B0B'), hx('#1F1F1F'), hx('#5C5C5C'), hx('#E9E6DF'), hx('#F6F5F1'), hx('#FFFFFF')
MAG, TEAL, ORANGE, LIME = hx('#E60585'), hx('#2DC892'), hx('#FF4200'), hx('#69FF00')
BARS = (MAG, TEAL, ORANGE, LIME)

# scene cuts
T = dict(INFO['scenes'])


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_inout(u):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def e_back(u, s=1.7):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ drawing helpers
def F(w, s):
    return ImageFont.truetype(f'{FON}/Inter-{w}.ttf', int(s))


@functools.lru_cache(maxsize=1024)
def text(s, w, size, col, track=0.0):
    f = F(w, size)
    asc, desc = f.getmetrics()
    widths = [f.getlength(ch) for ch in s]
    tw = sum(widths) + track * size * max(0, len(s) - 1)
    im = Image.new('L', (int(tw + 24), asc + desc + 24), 0)
    d = ImageDraw.Draw(im)
    x = 12
    for ch, cw in zip(s, widths):
        d.text((x, 12), ch, font=f, fill=255)
        x += cw + track * size
    a = np.asarray(im, np.float32) / 255
    ys, xs = np.where(a > 0.01)
    a = a[ys.min():ys.max() + 1, max(0, xs.min() - 1):xs.max() + 2] if len(ys) else a[:2, :2]
    return np.dstack([a[..., None] * np.array(col, np.float32), a])


def paste(c, spr, x, y, a=1.0, anchor='c'):
    sh, sw = spr.shape[:2]
    if anchor == 'c':
        x, y = x - sw / 2, y - sh / 2
    elif anchor == 'l':
        y = y - sh / 2
    x0, y0 = int(round(x)), int(round(y))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(c.shape[1], x0 + sw), min(c.shape[0], y0 + sh)
    if X1 <= X0 or Y1 <= Y0 or a <= 0:
        return c
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = s[..., 3:4] * a
    reg = c[Y0:Y1, X0:X1]
    if c.shape[2] == 4:
        reg[..., :3] = reg[..., :3] * (1 - al) + s[..., :3] * a
        reg[..., 3:4] = reg[..., 3:4] * (1 - al) + al
    else:
        reg[:] = reg * (1 - al) + s[..., :3] * a
    return c


def xform(spr, scale=1.0, rot=0.0):
    if abs(scale - 1) < 1e-3 and abs(rot) < 1e-3:
        return spr
    h, w = spr.shape[:2]
    D = int(math.hypot(w, h) * scale) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += D / 2 - w / 2
    M[1, 2] += D / 2 - h / 2
    return cv2.warpAffine(spr, M, (D, D), flags=cv2.INTER_LINEAR)


@functools.lru_cache(maxsize=64)
def rmask(w, h, r):
    w, h, r = int(w), int(h), int(r)
    m = np.zeros((h * 2, w * 2), np.uint8)
    cv2.rectangle(m, (r * 2, 0), ((w - r) * 2, h * 2), 255, -1)
    cv2.rectangle(m, (0, r * 2), (w * 2, (h - r) * 2), 255, -1)
    for x in (r, w - r):
        for y in (r, h - r):
            cv2.circle(m, (x * 2, y * 2), r * 2, 255, -1, cv2.LINE_AA)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def rrect(w, h, r, col, a=1.0):
    m = rmask(w, h, r)
    return np.dstack([m[..., None] * np.array(col, np.float32) * a, m * a])


def shadow_of(spr, blur=24, off=(0, 18), amt=0.25):
    p = blur * 3
    a = np.pad(spr[..., 3], p)
    a = cv2.GaussianBlur(a, (0, 0), blur) * amt
    return np.dstack([np.zeros(a.shape + (3,), np.float32), a]), p - off[0], p - off[1]


@functools.lru_cache(maxsize=64)
def obj(name, size):
    im = cv2.imread(f'{OBJ}/{name}.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    solid = (im[..., 3] > 0.5).astype(np.uint8)
    keep = cv2.GaussianBlur(cv2.dilate(solid, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2)
    k = np.clip(keep * 1.2, 0, 1)
    im[..., 3] *= k
    ys, xs = np.where(im[..., 3] > 0.5)
    pad = 20
    im = im[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    sc = size / max(ys.max() - ys.min(), xs.max() - xs.min())
    im = cv2.resize(im, (max(1, int(im.shape[1] * sc)), max(1, int(im.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


def pop_obj(c, name, cx, cy, size, t, t0, rot=0.0, flt=1.0, seed=0, shadow=0.35):
    """3D object pops in with overshoot, then floats."""
    u = (t - t0) / 0.55
    if u <= 0:
        return
    s = e_back(clamp(u), 1.8)
    r = rot + 6 * math.sin(t * 1.2 + seed) * flt + 25 * (1 - e_out(u))
    y = cy + 10 * math.sin(t * 1.5 + seed * 2) * flt
    sp = xform(obj(name, int(size)), max(0.01, s), r)
    if shadow:
        sh, ox, oy = shadow_of(sp, 20, (0, 24), shadow)
        paste(c, sh, cx - sh.shape[1] / 2, y - sh.shape[0] / 2 + 24, clamp(u * 2), 'tl')
    paste(c, sp, cx, y, clamp(u * 3))


def slam(c, spr, x, y, t, t0, anchor='c', dur=0.35, a=1.0):
    """Text slams in: scale 1.35 -> 1 with a quick settle (Wrapped type)."""
    u = (t - t0) / dur
    if u <= 0:
        return
    s = 1 + 0.35 * (1 - e_back(clamp(u), 2.2)) if u < 1 else 1.0
    sp = xform(spr, max(0.2, s))
    if anchor == 'l':
        x = x + spr.shape[1] / 2
    paste(c, sp, x, y, a * clamp(u * 2.5))


def rise(c, spr, x, y, t, t0, anchor='c', dist=40, dur=0.45, a=1.0):
    u = (t - t0) / dur
    if u <= 0:
        return
    k = e_out(u)
    if anchor == 'l':
        x = x + spr.shape[1] / 2
    paste(c, spr, x, y + dist * (1 - k), a * clamp(u * 1.8))


def underline(c, x0, x1, y, u, col=MAG, wdt=7):
    """Hand-drawn swoosh under the accented word, drawn on over u."""
    if u <= 0:
        return
    n = 40
    pts = [(x0 + (x1 - x0) * i / n, y + 7 * math.sin(i / n * 3.4) - 6 * i / n) for i in range(int(n * clamp(u)) + 1)]
    if len(pts) < 2:
        return
    lay = np.zeros((H, W), np.uint8)
    cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, wdt, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col, np.float32) * m


# ------------------------------------------------------------------ grounds
@functools.lru_cache(None)
def _grid():
    return np.mgrid[0:H, 0:W].astype(np.float32)


@functools.lru_cache(None)
def light_ground():
    """The reference's soft ground in BMHC colours: magenta glow top-right, teal glow bottom-left on white."""
    yy, xx = _grid()
    c = np.ones((H, W, 3), np.float32) * WHITE
    g1 = np.exp(-(((xx - 1050) / 520) ** 2 + ((yy - 60) / 520) ** 2))
    g2 = np.exp(-(((xx - 30) / 620) ** 2 + ((yy - 1900) / 640) ** 2))
    c = c * (1 - 0.35 * g1[..., None]) + MAG * 0.35 * g1[..., None]
    c = c * (1 - 0.38 * g2[..., None]) + TEAL * 0.38 * g2[..., None]
    return c.astype(np.float32)


def flat(col):
    c = np.empty((H, W, 3), np.float32)
    c[:] = col
    return c


def grain(c, t, amt=0.008):
    rng = np.random.default_rng(int(t * FPS))
    return np.clip(c + rng.normal(0, amt, (H, W, 1)).astype(np.float32), 0, 1)


def story_bars(c, t, idx, col=WHITE, n=7, bg_a=0.35):
    """Instagram-story progress segments at the top of each Wrapped slide."""
    x0, x1, y = 40, W - 40, 44
    gap = 10
    sw = (x1 - x0 - gap * (n - 1)) / n
    starts = [T['s1'], T['s2'], T['s3'], T['s4'], T['s5'], T['s6'], T['s7'], T['s8']]
    for i in range(n):
        xa = x0 + i * (sw + gap)
        bar = rrect(sw, 8, 4, col, bg_a)
        paste(c, bar, xa, y, 1, 'tl')
        f = 1.0 if i < idx else (prog(t, starts[i], starts[i + 1]) if i == idx else 0.0)
        if f > 0.01:
            paste(c, rrect(max(8, sw * f), 8, 4, col, 1.0), xa, y, 1, 'tl')


def head(c, col, t):
    """Small header on every slide: building-mark-free wordmark text (the logo itself appears on the end card)."""
    paste(c, text('BMHC WRAPPED 2026', 800, 26, tuple(col), 0.14), 52, 98, 1, 'tl')


def sticker_star(size, col, rot=0.0):
    S4 = size * 4
    pts = []
    for i in range(16):
        r = S4 / 2 if i % 2 == 0 else S4 * 0.3
        a = -math.pi / 2 + i * math.pi / 8
        pts.append((S4 / 2 + r * math.cos(a), S4 / 2 + r * math.sin(a)))
    m = np.zeros((S4, S4), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return xform(np.dstack([m[..., None] * np.array(col, np.float32), m]), 1.0, rot)


def blob(c, t, cx, cy, r, col, a=0.7, seed=0):
    """A soft drifting colour blob (Wrapped 'aura' look)."""
    yy, xx = _grid()
    x = cx + 80 * math.sin(t * 0.7 + seed)
    y = cy + 80 * math.cos(t * 0.6 + seed * 1.3)
    g = np.exp(-(((xx - x) / r) ** 2 + ((yy - y) / (r * 1.1)) ** 2)) * a
    c[:] = c * (1 - g[..., None]) + np.array(col, np.float32) * g[..., None]


@functools.lru_cache(None)
def photo(name, w, h, fx=0.5, fy=0.5, z=1.0):
    p = f'{IMG}/{name}'
    img = cv2.imread(p)[..., ::-1].astype(np.float32) / 255
    ih, iw = img.shape[:2]
    sc = max(w / iw, h / ih) * z
    rs = cv2.resize(img, (int(iw * sc) + 2, int(ih * sc) + 2), interpolation=cv2.INTER_AREA)
    x0 = int((rs.shape[1] - w) * fx)
    y0 = int((rs.shape[0] - h) * fy)
    return rs[y0:y0 + h, x0:x0 + w]


@functools.lru_cache(None)
def logo_light(width):
    """The official logo (as supplied by the user) with its light background keyed out - for light grounds."""
    lg = cv2.imread(f'{ROOT}/workspace_bmhc_posts/bmhc_logo_colour.png', cv2.IMREAD_UNCHANGED)[..., 2::-1].astype(np.float32) / 255
    big = cv2.resize(lg, (lg.shape[1] * 3, lg.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
    lum = (big * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1)
    sat = big.max(-1) - big.min(-1)
    bar = np.clip((sat - 0.18) / 0.12, 0, 1)
    la = np.clip((0.9 - lum) / 0.7, 0, 1)
    alpha = np.maximum(bar, la)
    rgb = INK[None, None] * (1 - bar[..., None]) + big * bar[..., None]
    ys, xs = np.where(alpha > 0.1)
    rgb, alpha = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1], alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hh = int(alpha.shape[0] * width / alpha.shape[1])
    rgb = cv2.resize(rgb, (width, hh), interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(alpha, (width, hh), interpolation=cv2.INTER_AREA)
    return np.dstack([rgb * alpha[..., None], alpha]).astype(np.float32)


def cursor(c, x, y, press=0.0):
    S4 = 4
    pts = np.array([(0, 0), (0, 46), (12, 35), (21, 55), (29, 51), (20, 32), (36, 32)], np.float32) * 1.3
    m = np.zeros((90 * S4, 70 * S4), np.uint8)
    cv2.fillPoly(m, [((pts + 6) * S4).astype(np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (70, 90), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    edge = cv2.dilate(m, np.ones((5, 5), np.uint8))
    spr = np.dstack([(m[..., None] * INK + (edge - m)[..., None] * WHITE), edge])
    spr = xform(spr, 1 - 0.15 * press)
    paste(c, spr, x + spr.shape[1] / 2 - 6, y + spr.shape[0] / 2 - 6)
    if press > 0:
        r = int(20 + 60 * press)
        ring = np.zeros((200, 200), np.float32)
        cv2.circle(ring, (100, 100), r, 1.0, 4, cv2.LINE_AA)
        ring *= 0.6 * (1 - press)
        paste(c, np.dstack([ring[..., None] * MAG, ring]), x, y)


def sentence(c, t, t0, plain, accent, y=250, size=60):
    """Reference-style line: plain words, then one accented word in magenta with a hand-drawn underline."""
    f1, f2 = F(500, size), F(800, size)
    w1 = f1.getlength(plain + ' ') + 12
    w2 = f2.getlength(accent)
    x0 = W / 2 - (w1 + w2) / 2
    s1 = text(plain, 500, size, tuple(INK))
    s2 = text(accent, 800, size, tuple(MAG))
    rise(c, s1, x0, y, t, t0, 'l', 30)
    rise(c, s2, x0 + w1, y, t, t0 + 0.35, 'l', 30)
    underline(c, x0 + w1 - 4, x0 + w1 + w2 + 6, y + size * 0.78, prog(t, t0 + 0.55, t0 + 1.0))


# ------------------------------------------------------------------ scenes
def s0(t):
    """Intro, reference language: light ground, a sentence, a card stack, a cursor taps Play."""
    c = light_ground().copy()
    tg = text('COMMUNITY', 800, 22, tuple(WHITE), 0.12)
    paste(c, rrect(tg.shape[1] + 34, tg.shape[0] + 22, 8, INK), 52, 60, 1, 'tl')
    paste(c, tg, 52 + 17, 60 + 11, 1, 'tl')
    sentence(c, t, 0.25, 'Your 2026 at the centre is', 'ready.')
    # stack of story cards fanning in
    cw, ch = 700, 1000
    for i, (col, rot, dx) in enumerate(((LIME, -9, -70), (TEAL, 7, 60), (MAG, -2, 0))):
        u = e_out(prog(t, 0.4 + 0.15 * i, 1.1 + 0.15 * i))
        card = rrect(cw, ch, 48, col)
        if i == 2:
            paste(card, text('BMHC', 800, 54, tuple(WHITE), 0.1), 70, 110, 1, 'l')
            paste(card, text('Wrapped', 900, 128, tuple(WHITE)), 70, 420, 1, 'l')
            paste(card, text('2026', 900, 128, tuple(WHITE)), 70, 570, 1, 'l')
            pill = rrect(330, 100, 50, WHITE)
            paste(pill, text('▶  Play', 800, 44, tuple(INK)), 165, 50)
            paste(card, pill, 70 + 165, 840)
        sp = xform(card, 0.9 + 0.1 * u, rot * u + (1 - u) * 20)
        sh, ox, oy = shadow_of(sp, 30, (0, 30), 0.25)
        cx, cy = W / 2 + dx * u, 1130 + 500 * (1 - u)
        paste(c, sh, cx - sh.shape[1] / 2, cy - sh.shape[0] / 2 + 30, u, 'tl')
        paste(c, sp, cx, cy, clamp(u * 2))
    # 3D bits peeking out from behind the stack
    pop_obj(c, 'lantern', 230, 760, 220, t, 1.4, -10, seed=1)
    pop_obj(c, 'radio', 880, 1580, 230, t, 1.6, 8, seed=2)
    pop_obj(c, 'rings', 860, 720, 170, t, 1.8, 10, seed=3)
    # cursor travels to Play and taps
    k = e_inout(prog(t, 2.2, 3.15))
    px, py = 1100 + (W / 2 - 350 + 70 + 165 - 1100) * k, 1900 + (1130 - 500 + 840 - 30 - 1900) * k
    press = prog(t, 3.2, 3.6) if t > 3.2 else 0
    if t > 2.2:
        cursor(c, px * 0.93 + 20, py, press if press < 1 else 0)
    return c


def s1(t):
    """Title slide - magenta, huge stacked type, 3D objects orbiting."""
    c = flat(MAG)
    blob(c, t, 900, 400, 420, hx('#FF4FAE'), 0.5, 1)
    blob(c, t, 150, 1500, 480, hx('#B8006A'), 0.55, 2)
    story_bars(c, t, 0)
    head(c, WHITE, t)
    u0 = T['s1']
    slam(c, text('BMHC', 900, 110, tuple(WHITE), 0.08), 80, 470, t, u0 + 0.25, 'l')
    slam(c, text('Wrapped', 900, 186, tuple(WHITE)), 64, 690, t, u0 + 0.45, 'l')
    s26 = text('2026', 900, 300, tuple(INK))
    slam(c, s26, 64, 990, t, u0 + 0.7, 'l')
    rise(c, text('A year at the British Muslim Heritage Centre', 500, 38, tuple(WHITE)), 80, 1210, t, u0 + 1.1, 'l')
    for i, (n, ang, rr, sz) in enumerate((('lantern', 0, 300, 230), ('ball', 1.25, 330, 170), ('rehal', 2.5, 300, 200), ('rings', 3.8, 320, 170), ('mappin', 5.0, 300, 190))):
        a = ang + (t - u0) * 0.45
        pop_obj(c, n, W / 2 + 60 + rr * 1.25 * math.cos(a), 1560 + rr * 0.55 * math.sin(a), sz * (0.85 + 0.15 * math.sin(a)), t, u0 + 1.2 + 0.12 * i, seed=i)
    return c


def s2(t):
    """52 Fridays - teal, a counter rolls, the lantern glows."""
    c = flat(TEAL)
    blob(c, t, 850, 1450, 460, hx('#7FE8C2'), 0.5, 3)
    story_bars(c, t, 1, INK)
    head(c, INK, t)
    u0 = T['s2']
    rise(c, text('This year, you showed up.', 700, 56, tuple(INK)), 80, 330, t, u0 + 0.2, 'l')
    t52, tfr = WT('52', 'v3'), WT('fridays', 'v3')
    n = int(round(52 * e_out(prog(t, u0 + 0.6, t52 + 0.1))))
    if t > u0 + 0.6:
        num = text(str(n), 900, 520, tuple(INK))
        slam(c, num, 70, 760, t, u0 + 0.6, 'l', 0.3)
    slam(c, text('Fridays.', 900, 150, tuple(WHITE)), 80, 1150, t, tfr - 0.05, 'l')
    rise(c, text('52 Jummahs at the centre.', 600, 48, tuple(INK)), 84, 1300, t, tfr + 0.45, 'l')
    pop_obj(c, 'lantern', 800, 1560, 420, t, u0 + 0.9, 6, seed=4)
    for i, (x, y, s) in enumerate(((930, 380, 70), (180, 1640, 54), (700, 1080, 40))):
        if t > u0 + 1.5 + 0.2 * i:
            paste(c, xform(sticker_star(s, WHITE), e_back(prog(t, u0 + 1.5 + 0.2 * i, u0 + 1.9 + 0.2 * i)), t * 40 + i * 30), x, y)
    return c


def s3(t):
    """Most played - orange, the radio and a live equaliser."""
    c = flat(ORANGE)
    blob(c, t, 200, 400, 420, hx('#FF7A3D'), 0.6, 5)
    story_bars(c, t, 2, INK)
    head(c, INK, t)
    u0 = T['s3']
    rise(c, text('Most played', 700, 56, tuple(INK)), 80, 330, t, u0 + 0.2, 'l')
    pop_obj(c, 'radio', W / 2, 760, 600, t, u0 + 0.35, -4, seed=6, shadow=0.3)
    slam(c, text('Heritage', 900, 170, tuple(INK)), 72, 1200, t, WT('heritage', 'v4') - 0.05, 'l')
    slam(c, text('Radio', 900, 170, tuple(WHITE)), 72, 1380, t, WT('radio', 'v4') - 0.05, 'l')
    rise(c, text('90.6 FM  ·  DAB+  ·  the app  ·  Alexa', 600, 44, tuple(INK)), 80, 1540, t, WT('on', 'v4'), 'l')
    if t > u0 + 1.0:                                                    # equaliser
        for i in range(14):
            hgt = 40 + 140 * abs(math.sin(t * (3 + i * 0.37) + i))
            bar = rrect(46, hgt, 14, INK)
            paste(c, bar, 90 + i * 66, 1760 - hgt / 2, clamp((t - u0 - 1.0) * 3))
    return c


TOP5 = [('Friday Jummah', 'lantern'), ("Qur'an classes", 'rehal'), ('Youth clubs & taekwondo', 'ball'),
        ('Heritage tours & Umrah', 'mappin'), ('Nikah ceremonies', 'rings')]


def s4(t):
    """Your top 5 - ink, rows slide in one by one with their 3D object."""
    c = flat(INK)
    blob(c, t, 900, 300, 400, hx('#3A0A26'), 0.7, 7)
    story_bars(c, t, 3)
    head(c, WHITE, t)
    u0 = T['s4']
    slam(c, text('Your top 5', 900, 120, tuple(WHITE)), 72, 330, t, u0 + 0.2, 'l')
    for i, (lab, ob) in enumerate(TOP5):
        t0 = INFO['lines'][f't{i + 1}'][0] - 0.12
        u = (t - t0) / 0.5
        if u <= 0:
            continue
        k = e_out(u)
        y = 560 + i * 245
        x = 72 + 700 * (1 - k)
        row = rrect(936, 210, 40, CHAR)
        paste(row, text(str(i + 1), 900, 110, tuple(BARS[i % 4] if i < 4 else WHITE)), 80, 105)
        paste(row, text(lab, 800, 52 if len(lab) < 20 else 44, tuple(WHITE)), 170, 105, 1, 'l')
        paste(c, row, x, y, clamp(u * 2), 'tl')
        pop_obj(c, ob, x + 830, y + 100, 190, t, t0 + 0.15, seed=i, shadow=0.0)
    return c


def counter(v, k):
    return v if k >= 1 else int(round(v * k))


def s5(t):
    """Your year in numbers - lime (ink type), counters roll up."""
    c = flat(LIME)
    blob(c, t, 150, 1700, 520, hx('#B6FF7A'), 0.6, 8)
    story_bars(c, t, 4, INK)
    head(c, INK, t)
    u0 = T['s5']
    slam(c, text('Your year', 900, 120, tuple(INK)), 72, 330, t, u0 + 0.2, 'l')
    slam(c, text('in numbers', 900, 120, tuple(INK)), 72, 460, t, u0 + 0.35, 'l')
    rows = [(130, 'K+', 'visitors a year'), (14, '', 'awards'), (12, '+', 'years of Muslim heritage')]
    for i, (v, suf, lab) in enumerate(rows):
        t0 = (WT('130', 'v6'), WT('14', 'v6'), WT('over', 'v6'))[i] - 0.1
        if t < t0:
            continue
        k = e_out(prog(t, t0, t0 + 1.0))
        y = 760 + i * 380
        num = text(f'{counter(v, k)}{suf}', 900, 260, tuple(INK))
        slam(c, num, 72, y, t, t0, 'l', 0.3)
        rise(c, text(lab, 700, 52, tuple(INK)), 80, y + 175, t, t0 + 0.3, 'l')
    rise(c, text('Figures as stated on bmhc.org.uk', 500, 28, tuple(INK * 0.6 + LIME * 0.4)), 80, 1840, t, WT('over', 'v6') + 0.6, 'l')
    return c


def s6(t):
    """Your aura - mist ground, drifting colour blobs, the centre's personality words."""
    c = flat(MIST)
    for i, (col, x, y) in enumerate(((MAG, 300, 700), (TEAL, 800, 900), (ORANGE, 400, 1300), (LIME, 780, 1450))):
        blob(c, t * 1.6, x, y, 330, col, 0.55, i * 1.7)
    c = cv2.GaussianBlur(c, (0, 0), 6)
    story_bars(c, t, 5, INK)
    head(c, INK, t)
    u0 = T['s6']
    rise(c, text('Your aura', 700, 56, tuple(INK)), 80, 330, t, u0 + 0.15, 'l')
    slam(c, text('Welcoming', 900, 158, tuple(INK)), W / 2, 1000, t, WT('welcoming', 'v7') - 0.05)
    for i, (w, x, y) in enumerate((('Grounded', 300, 1240), ('Clear', 720, 1240), ('Proud of heritage', W / 2, 1360))):
        chip = rrect(F(700, 46).getlength(w) + 70, 92, 46, WHITE)
        paste(chip, text(w, 700, 46, tuple(INK)), chip.shape[1] / 2, 46)
        u = (t - (WT('welcoming', 'v7') + 0.35 + 0.2 * i)) / 0.4
        if u > 0:
            paste(c, xform(chip, e_back(clamp(u), 1.8)), x, y, clamp(u * 3))
    return c


def s7(t):
    """1 tower. 4 seasons. - the building, snow dissolving into autumn, slow push."""
    u0 = T['s7']
    z = 1.0 + 0.08 * prog(t, u0, T['s8'])
    snow = photo('1-BMHC-web.jpg', W, H, 0.47, 0.5, z)
    aut = photo('bhmc-f.png', W, H, 0.47, 0.5, z)
    k = smooth(prog(t, WT('four', 'v8') - 0.3, WT('four', 'v8') + 0.8))
    c = snow * (1 - k) + aut * k
    if 0 < k < 1:                                                       # a warm light leak through the dissolve
        yy, xx = _grid()
        g = np.exp(-((xx - 200 - 700 * k) / 380) ** 2) * math.sin(math.pi * k) * 0.35
        c = np.clip(c + g[..., None] * np.array((1.0, 0.7, 0.4), np.float32), 0, 1)
    yy, xx = _grid()
    shade = np.clip((yy - 900) / 1000, 0, 1)[..., None] * 0.7
    c = c * (1 - shade)
    story_bars(c, t, 6)
    head(c, WHITE, t)
    slam(c, text('1 tower.', 900, 170, tuple(WHITE)), 72, 1440, t, WT('one', 'v8') - 0.05, 'l')
    slam(c, text('4 seasons.', 900, 170, tuple(WHITE)), 72, 1620, t, WT('four', 'v8') - 0.05, 'l')
    rise(c, text('Whalley Range, Manchester', 600, 44, tuple(WHITE)), 80, 1760, t, WT('four', 'v8') + 0.5, 'l')
    return c


def s8(t):
    """CTA - back to the reference's light ground: See you in 2027, a share card, the cursor taps."""
    c = light_ground().copy()
    u0 = T['s8']
    sentence(c, t, u0 + 0.1, 'See you in', '2027.')
    card = rrect(760, 820, 48, WHITE)
    paste(card, logo_light(560), 380, 260)
    paste(card, text('Your 2026 at the centre', 700, 44, tuple(INK)), 380, 470)
    btn = rrect(520, 112, 56, MAG)
    paste(btn, text('Share your Wrapped', 800, 42, tuple(WHITE)), 260, 56)
    paste(card, btn, 380, 640)
    u = e_out(prog(t, u0 + 0.2, u0 + 0.8))
    sh, ox, oy = shadow_of(card, 34, (0, 30), 0.22)
    paste(c, sh, W / 2 - sh.shape[1] / 2, 1050 - sh.shape[0] / 2 + 30 + 300 * (1 - u), u, 'tl')
    paste(c, card, W / 2, 1050 + 300 * (1 - u), clamp(u * 2))
    pop_obj(c, 'ball', 180, 1500, 200, t, u0 + 0.7, seed=9)
    pop_obj(c, 'lantern', 900, 640, 200, t, u0 + 0.9, seed=10)
    k = e_inout(prog(t, u0 + 0.8, u0 + 1.6))
    bx, by = W / 2, 1050 - 410 + 640
    px, py = W + 60 + (bx + 20 - W - 60) * k, H + 60 + (by + 10 - H - 60) * k
    press = prog(t, u0 + 1.65, u0 + 2.05)
    if t > u0 + 0.8:
        cursor(c, px, py, press if press < 1 else 0)
    return c


@functools.lru_cache(None)
def end_card():
    c = light_ground().copy()
    paste(c, logo_light(760), W / 2, 820)
    paste(c, text('Join us at the centre', 800, 66, tuple(INK)), W / 2, 1120)
    paste(c, text('in Whalley Range', 800, 66, tuple(MAG)), W / 2, 1205)
    paste(c, text('bmhc.org.uk', 600, 44, tuple(SLATE)), W / 2, 1330)
    return c


def end(t):
    c = end_card().copy()
    u = t - T['end']
    for i, col in enumerate(BARS):                                       # four bars wipe in from the left, fixed order
        k = e_out(clamp((u - 0.1 * i) / 0.45))
        c[H - 24:, int(W * i / 4):int(W * i / 4 + W / 4 * k)] = col
    return c


SCENES = [('s0', s0), ('s1', s1), ('s2', s2), ('s3', s3), ('s4', s4), ('s5', s5), ('s6', s6), ('s7', s7), ('s8', s8)]
STARTS = [T[k] for k, _ in SCENES] + [T['end']]


def scene_at(t):
    i = max(j for j in range(len(SCENES)) if t >= STARTS[j])
    return i


# ------------------------------------------------------------------ transitions
def tr_zoom_through(a_fn, b_fn, t, t0, d, cx, cy, card_w, card_h):
    """The Play card grows to fill the screen and becomes the first slide."""
    u = e_inout(prog(t, t0, t0 + d))
    A = a_fn(t)
    B = b_fn(t)
    w = card_w + (W - card_w) * u
    h = card_h + (H - card_h) * u
    x0 = cx + (W / 2 - cx) * u - w / 2
    y0 = cy + (H / 2 - cy) * u - h / 2
    r = 48 * (1 - u)
    m = np.zeros((H, W), np.float32)
    mm = rmask(max(4, w), max(4, h), max(1, min(r, w / 2 - 1, h / 2 - 1)))
    paste(m[..., None].repeat(4, 2), np.dstack([np.zeros(mm.shape + (3,), np.float32), mm]), 0, 0)
    X0, Y0 = int(x0), int(y0)
    hh, ww = mm.shape
    xs0, ys0 = max(0, X0), max(0, Y0)
    xs1, ys1 = min(W, X0 + ww), min(H, Y0 + hh)
    if xs1 > xs0 and ys1 > ys0:
        m[ys0:ys1, xs0:xs1] = mm[ys0 - Y0:ys1 - Y0, xs0 - X0:xs1 - X0]
    m = m[..., None]
    return A * (1 - m) + B * m


def tr_push(A, B, u, horiz=True):
    """Story swipe: push left with motion blur at the peak."""
    k = e_inout(u)
    off = int(W * k)
    out = np.empty_like(A)
    out[:, :W - off] = A[:, off:]
    out[:, W - off:] = B[:, :off]
    v = 1 - abs(2 * u - 1)
    L = int(2 + 120 * v ** 1.5)
    return cv2.blur(out, (L, 1)) if L > 2 else out


def tr_iris(A, B, u, cx, cy):
    k = e_inout(u)
    yy, xx = _grid()
    r = 2300 * k
    m = np.clip((r - np.hypot(xx - cx, yy - cy)) / 4, 0, 1)[..., None]
    return A * (1 - m) + B * m


def tr_bars(A, B, u):
    """The four bars sweep down the screen in brand order and leave the next slide behind them."""
    out = A.copy()
    for i, col in enumerate(BARS):
        k = e_inout(clamp(u * 1.4 - i * 0.12))
        y = int((H + 300) * k)
        top = max(0, y - 300)
        out[:max(0, top)] = B[:max(0, top)]
        if y > top:
            out[top:min(H, y)] = col
    return out


def tr_punch(A, B, u):
    """Cut on the beat with a zoom punch into the next slide."""
    if u < 0.5:
        z = 1 + 0.12 * (u / 0.5) ** 2
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        return cv2.warpAffine(A, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    z = 1.12 - 0.12 * e_out((u - 0.5) / 0.5)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    return cv2.warpAffine(B, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def tr_dissolve(A, B, u):
    k = smooth(u)
    a = cv2.GaussianBlur(A, (0, 0), 0.1 + 18 * k)
    b = cv2.GaussianBlur(B, (0, 0), 0.1 + 18 * (1 - k))
    return a * (1 - k) + b * k


def tr_blob(A, B, u):
    """Morph: the aura blobs swell into the photograph."""
    yy, xx = _grid()
    k = e_inout(u)
    f = np.zeros((H, W), np.float32)
    for i, (x, y) in enumerate(((300, 700), (800, 900), (400, 1300), (780, 1450))):
        r = 60 + 1500 * k * (0.8 + 0.1 * i)
        f = np.maximum(f, np.clip((r - np.hypot(xx - x, yy - y)) / 30, 0, 1))
    return A * (1 - f[..., None]) + B * f[..., None]


def tr_whip_up(A, B, u):
    k = e_inout(u)
    off = int(H * k)
    out = np.empty_like(A)
    out[:H - off] = A[off:]
    out[H - off:] = B[:off]
    v = 1 - abs(2 * u - 1)
    L = int(2 + 160 * v ** 1.5)
    return cv2.blur(out, (1, L)) if L > 2 else out


D = 0.45
TRANS = {1: 'zoom', 2: 'push', 3: 'iris', 4: 'bars', 5: 'punch', 6: 'dissolve', 7: 'blob', 8: 'whip'}


def base(t):
    i = scene_at(t)
    fn = SCENES[i][1]
    if t >= T['end']:
        c = end(t)
        k = prog(t, T['end'] - 0.0, T['end'] + 0.45)                     # magenta circle wipe from the Share button
        if k < 1:
            yy, xx = _grid()
            r = 2400 * e_inout(k)
            ring = np.exp(-((np.hypot(xx - W / 2, yy - 1280) - r) / 60) ** 2)[..., None]
            c = c * (1 - ring * 0.9) + MAG * ring * 0.9
        return c
    if T['end'] - 0.45 <= t < T['end']:                                  # circle grows out of the Share button
        u = prog(t, T['end'] - 0.45, T['end'])
        A = s8(t)
        yy, xx = _grid()
        r = 2400 * e_inout(u)
        m = np.clip((r - np.hypot(xx - W / 2, yy - 1280)) / 3, 0, 1)[..., None]
        return A * (1 - m) + MAG * m
    nxt = i + 1
    if nxt < len(SCENES) and t > STARTS[nxt] - D:
        u = (t - (STARTS[nxt] - D)) / (2 * D)
        return transition(nxt, t, u)
    if i > 0 and t < STARTS[i] + D:
        u = (t - (STARTS[i] - D)) / (2 * D)
        return transition(i, t, u)
    return fn(t)


def transition(i, t, u):
    a_fn, b_fn = SCENES[i - 1][1], SCENES[i][1]
    kind = TRANS[i]
    if kind == 'zoom':
        return tr_zoom_through(a_fn, b_fn, t, STARTS[i] - D, 2 * D, W / 2, 1130, 700, 1000)
    A, B = a_fn(t), b_fn(t)
    if kind == 'push':
        return tr_push(A, B, u)
    if kind == 'iris':
        return tr_iris(A, B, u, W / 2, 760)
    if kind == 'bars':
        return tr_bars(A, B, u)
    if kind == 'punch':
        return tr_punch(A, B, u)
    if kind == 'dissolve':
        return tr_dissolve(A, B, u)
    if kind == 'blob':
        return tr_blob(A, B, u)
    if kind == 'whip':
        return tr_whip_up(A, B, u)
    return B


def frame(t):
    return grain(np.clip(base(t), 0, 1), t)


def write(path, c):
    cv2.imwrite(path, (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        d = f'{S}/stills'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            write(f'{d}/{int(round(float(ts) * 100)):05d}.png', frame(float(ts)))
            print('still', ts, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            write(f'{d}/{i:05d}.png', frame(i / FPS))
            if i % 30 == 0:
                print('frame', i, flush=True)
