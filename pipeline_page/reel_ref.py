"""OF reel in the grammar of the user's Pinterest reference (Solution Wagon "Most agencies compete on output"):
one centred cutout per beat on a pale vignetted ground, small light line over a big bold line, words sharpening out of
a blur, whole-frame blur dissolves, a star-bullet list, a pin over swapping text, a UI pill, a words-only beat, a big
out-of-focus pass, a big object half off-frame, a glow bloom, a brand-colour flash into the logo card.
In Organic Fostering colours: ivory ground with a plum vignette, cutouts toned plum, plum/lilac type, magenta/orange/
green accents, plum chrome corner crescents. Only the small things keep their real colour: the drawing, the scarf.

Narration (edge-tts Ryan): "It lives in the small things".  Usage: python3 reel_ref.py still 1,5 | range a b
"""
import os, sys, json, math, functools, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ai'))
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from frames_ai import clamp, prog, e_out, e_inout, e_back, cover

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_page'
A = f'{S}/assets'
FON = f'{ROOT}/workspace_sol/fonts'
W, H = 1080, 1920
FPS = 25
DUR = 34.0
NF = int(DUR * FPS)


def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


IVORY, PLUM, DPLUM = hx('#FCF8F5'), hx('#5B174F'), hx('#2C0A27')
LILAC, SMALL = hx('#C4B2BF'), hx('#85727F')
MAG, ORANGE, GREEN, SKY = hx('#B7006E'), hx('#FF6411'), hx('#61A80A'), hx('#4E9BD6')

INFO = json.load(open(f'{S}/tts2/info.json'))
WORDS = INFO['words']


def norm(w):
    return re.sub(r"[^a-z0-9']", '', w.lower())


def AT(wd, line, k=0):
    n = 0
    for w in WORDS:
        if w[3] == line - 1 and norm(w[0]) == norm(wd):
            if n == k:
                return w[1]
            n += 1
    raise KeyError((wd, line))


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', int(s))


# ------------------------------------------------------------------ sprites
def paste(c, spr, cx, cy, a=1.0):
    Hc, Wc = c.shape[:2]
    sh, sw = spr.shape[:2]
    x0, y0 = int(round(cx - sw / 2)), int(round(cy - sh / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(Wc, x0 + sw), min(Hc, y0 + sh)
    if X1 <= X0 or Y1 <= Y0 or a <= 0:
        return c
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    reg = c[Y0:Y1, X0:X1]
    al = s[..., 3:4] * a
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


def blur(spr, s):
    if s < 0.3:
        return spr
    p = int(s * 3)
    sp = np.pad(spr, ((p, p), (p, p), (0, 0)))
    return cv2.GaussianBlur(sp, (0, 0), s)


@functools.lru_cache(maxsize=512)
def text_spr(s, w, size, col):
    f = F(w, size)
    asc, desc = f.getmetrics()
    im = Image.new('L', (int(f.getlength(s) + 20), asc + desc + 20), 0)
    ImageDraw.Draw(im).text((10, 10), s, font=f, fill=255)
    a = np.asarray(im, np.float32) / 255
    ys, xs = np.where(a > 0.01)
    a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    return np.dstack([a[..., None] * np.array(col, np.float32), a])


def duotone(rgb, keep=None):
    """Plum monochrome: deep plum shadows -> plum mids -> ivory highlights (keep = mask of pixels to leave in colour)."""
    L = (rgb * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    L = np.clip((L - 0.5) * 1.15 + 0.52, 0, 1)
    lo = DPLUM + (hx('#8A5C80') - DPLUM) * np.clip(L / 0.55, 0, 1)
    out = np.where(L < 0.55, lo, hx('#8A5C80') + (IVORY - hx('#8A5C80')) * np.clip((L - 0.55) / 0.45, 0, 1))
    if keep is not None:
        out = out * (1 - keep[..., None]) + rgb * keep[..., None]
    return out.astype(np.float32)


def load_rgba(path, width=None, tone=True, keep_sat=0.0, keep_blue=False, crop_thr=0.5):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    if im.shape[2] == 3:
        im = np.dstack([im, np.ones(im.shape[:2], np.float32)])
    a = im[..., 3]
    ys, xs = np.where(a > crop_thr)
    pad = 50
    im = im[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    if width:
        sc = width / (xs.max() - xs.min())
        im = cv2.resize(im, (int(im.shape[1] * sc), int(im.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    rgb = im[..., 2::-1]
    if tone:
        keep = None
        if keep_sat or keep_blue:
            mx, mn = rgb.max(-1), rgb.min(-1)
            sat = (mx - mn) / np.maximum(mx, 1e-4)
            keep = np.clip((sat - keep_sat) / 0.15, 0, 1) if keep_sat else np.zeros(rgb.shape[:2], np.float32)
            if keep_blue:
                keep = np.maximum(keep, np.clip((rgb[..., 2] - rgb[..., 0] - 0.08) / 0.1, 0, 1))
        rgb = duotone(rgb, keep)
    return np.dstack([rgb * im[..., 3:4], im[..., 3]]).astype(np.float32)


@functools.lru_cache(None)
def asset(name, width):
    paths = {'houses': f'{A}/houses.png', 'house': f'{A}/house.png', 'book3q': f'{A}/book3q.png', 'pin': f'{A}/pin.png',
             'crescent': f'{A}/crescent.png', 'fridge': f'{ROOT}/workspace_fridge/render2/fridge.png', 'heart': f'{ROOT}/workspace_fridge/props/heart.png'}
    if name == 'crescent' or name == 'pin':
        return load_rgba(paths[name], width, tone=False)
    if name == 'heart':
        return load_rgba(paths[name], width, tone=False)
    if name == 'fridge':
        return load_rgba(paths[name], width, keep_sat=0.38)
    return load_rgba(paths[name], width)


@functools.lru_cache(None)
def photo(name, w, h, fx=0.5, fy=0.5):
    """A website photo as a soft-edged plum-toned cutout (feathered into the ground)."""
    img = cv2.imread(f'{ROOT}/workspace_frame/of/{name}.webp')[..., ::-1].astype(np.float32) / 255
    im = duotone(cover(img, fx, fy, 1.0, w, h))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.maximum(np.abs(xx - w / 2) / (w / 2), np.abs(yy - h / 2) / (h / 2))
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    m = np.clip((1 - np.maximum(d, r * 0.82)) / 0.28, 0, 1) ** 1.4
    return np.dstack([im * m[..., None], m]).astype(np.float32)


@functools.lru_cache(None)
def drawing_card():
    im = cv2.imread(f'{ROOT}/workspace_fridge/tex/drawing.png').astype(np.float32)[..., ::-1] / 255
    im = cv2.resize(im, (640, 480), interpolation=cv2.INTER_AREA)
    spr = np.dstack([im, np.ones(im.shape[:2], np.float32)])
    return shadowed(xform(spr, 1, 5))


def shadowed(spr, b=14, off=(12, 22), amt=0.3):
    h, w = spr.shape[:2]
    p = b * 3 + max(off)
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    sh = np.zeros(out.shape[:2], np.float32)
    sh[p + off[1]:p + off[1] + h, p + off[0]:p + off[0] + w] = spr[..., 3]
    out[..., 3] = cv2.GaussianBlur(sh, (0, 0), b) * amt
    out[..., :3] = DPLUM * 0.0
    reg = out[p:p + h, p:p + w]
    a = spr[..., 3:4]
    reg[..., :3] = spr[..., :3] + reg[..., :3] * (1 - a)
    reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)
    return out


@functools.lru_cache(None)
def spread():
    """The overhead book from the brief's reel (photos, scarf, Match day, 3:00), toned plum - scarf kept sky blue."""
    import reel_page as RP
    w = RP.compose_world(27.5)
    a = w[..., 3:4]
    rgb = w[..., :3] / np.maximum(a, 1e-4)
    keep = np.clip((rgb[..., 2] - rgb[..., 0] - 0.1) / 0.1, 0, 1)
    rgb = duotone(rgb, keep)
    out = np.dstack([rgb * a, a[..., 0]])
    ys, xs = np.where(a[..., 0] > 0.5)
    out = out[ys.min() - 40:ys.max() + 40, xs.min() - 40:xs.max() + 40]
    sc = 1180 / out.shape[1]
    return cv2.resize(out, (int(out.shape[1] * sc), int(out.shape[0] * sc)), interpolation=cv2.INTER_AREA)


# ------------------------------------------------------------------ ground, persistent logo + crescents
@functools.lru_cache(None)
def ground():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W * 0.62), (yy - H * 0.47) / (H * 0.6))
    v = np.clip((r - 0.55) / 0.75, 0, 1) ** 1.3
    c = IVORY[None, None] * (1 - v[..., None]) + hx('#9C8796')[None, None] * v[..., None]
    rng = np.random.default_rng(1)
    c = c + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 30)[..., None] * 0.02
    return np.clip(c, 0, 1).astype(np.float32)


@functools.lru_cache(None)
def logo_spr(width):
    lg = cv2.imread(f'{ROOT}/workspace_three/web/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    lg = cv2.resize(lg, (width, int(lg.shape[0] * width / lg.shape[1])), interpolation=cv2.INTER_AREA)
    return np.dstack([lg[..., 2::-1] * lg[..., 3:4], lg[..., 3]]).astype(np.float32)


def chrome(c, t):
    cr = asset('crescent', 520)
    paste(c, xform(cr, 1.0, 150 + 6 * math.sin(t * 0.5)), 40 + 10 * math.sin(t * 0.4), 40)
    paste(c, xform(cr, 1.0, -30 + 6 * math.sin(t * 0.45 + 1)), W - 40, H - 30 + 10 * math.sin(t * 0.35))


# ------------------------------------------------------------------ type
def row(c, txt, t, t0, x, y, size=100, w=800, col=PLUM, align='c', track=False):
    """A line sharpening out of a blur, lilac -> its colour, rising a little (reference type motion)."""
    u = (t - t0) / 0.4
    if u <= 0:
        return 0
    k = e_out(clamp(u))
    final = text_spr(txt, w, size, tuple(col))
    pale = text_spr(txt, w, size, tuple(LILAC + (IVORY - LILAC) * 0.3))
    spr = final * k + pale * (1 - k)
    spr = blur(spr, 9 * (1 - k))
    spr = xform(spr, 1.06 - 0.06 * k)
    xx = x if align == 'c' else x + spr.shape[1] / 2
    paste(c, spr, xx, y + 16 * (1 - k), k ** 0.7)
    return final.shape[1]


def spaced(c, words, t, x, y, size, gap=70):
    f = F(400, size)
    tw = sum(f.getlength(w) for w, _ in words) + gap * (len(words) - 1)
    xx = x - tw / 2
    for wd, t0 in words:
        L = f.getlength(wd)
        row(c, wd, t, t0, xx + L / 2, y, size, 400, SMALL)
        xx += L + gap


def bullet(c, txt, col, t, t0, x, y, rot=0.0):
    u = (t - t0) / 0.4
    if u <= 0:
        return
    k = e_out(clamp(u))
    st = star(30, tuple(col))
    paste(c, xform(st, 0.4 + 0.6 * e_back(clamp(u), 2.0), 90 * (1 - k)), x, y)
    row(c, txt, t, t0 + 0.05, x + 30, y, 52, 700, PLUM, align='l')


@functools.lru_cache(None)
def star(size, col):
    S4 = size * 4
    pts = []
    for i in range(8):
        r = S4 / 2 if i % 2 == 0 else S4 * 0.13
        a = -math.pi / 2 + i * math.pi / 4
        pts.append((S4 / 2 + r * math.cos(a), S4 / 2 + r * math.sin(a)))
    m = np.zeros((S4, S4), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return np.dstack([m[..., None] * np.array(col, np.float32), m])


def img_in(c, spr, t, t0, cx, cy, kb=0.04, dur=2.5, scale=1.0, rot=0.0, a=1.0):
    """Cutout arriving out of a defocus (blur + scale), then a slow push (Ken Burns)."""
    u = (t - t0) / 0.5
    if u <= 0:
        return
    k = e_out(clamp(u))
    s = scale * (1.1 - 0.1 * k + kb * clamp((t - t0) / dur))
    sp = xform(spr, s, rot)
    sp = blur(sp, 16 * (1 - k))
    paste(c, sp, cx, cy, a * clamp(u * 1.5))


# ------------------------------------------------------------------ timing (from the narration)
L = {i + 1: (a, b) for i, a, b, _ in INFO['lines']}
CUTS = [0.0, 2.08, 4.38, 6.72, 11.42, 13.22, 15.38, 16.86, 18.66, 20.34, 21.6, 23.5, 25.22, 28.3]
END = 28.3


def s1(c, t):
    img_in(c, asset('houses', 1250), t, 0.15, W / 2, 1000, dur=2.0)
    row(c, "If you're", t, AT("if", 1), W / 2, 430, 50, 400, SMALL)
    row(c, 'Thinking', t, AT('thinking', 1), W / 2, 520, 120, 800, PLUM)
    row(c, 'About', t, AT('about', 1), W / 2, 1330, 50, 400, SMALL)
    row(c, 'Fostering', t, AT('fostering', 1), W / 2, 1430, 132, 800, LILAC)


def s2(c, t):
    img_in(c, photo('06-respite-outdoor-play', 820, 900, 0.5, 0.45), t, 2.05, W / 2, 1010, dur=2.3)
    row(c, "You're probably", t, AT("you're", 2), W / 2, 450, 50, 400, SMALL)
    row(c, 'Picturing', t, AT('picturing', 2), W / 2, 540, 116, 800, PLUM)
    row(c, 'Something big', t, AT('something', 2), W / 2, 1430, 128, 800, LILAC)


def s3(c, t):
    # arrives from a giant out-of-focus close-up and pulls back sharp (the reference's statue beat)
    u = e_inout(prog(t, CUTS[2] - 0.05, CUTS[2] + 0.75))
    ph = photo('01-hero-cultural-belonging', 900, 900, 0.42, 0.5)
    sp = blur(xform(ph, 2.6 - 1.6 * u + 0.04 * prog(t, CUTS[2], CUTS[3])), 22 * (1 - u))
    paste(c, sp, W / 2 + 120 * (1 - u), 1060 - 200 * (1 - u))
    yy = np.linspace(0, 1, 420, dtype=np.float32)[:, None]               # soft mist across the bottom
    mist = np.clip((yy - 0.15) / 0.6, 0, 1) ** 1.2 * 0.95
    c[1380:1800] = c[1380:1800] * (1 - mist[..., None]) + IVORY * mist[..., None]
    row(c, 'Most people imagine', t, AT('most', 3), W / 2, 460, 50, 400, SMALL)
    row(c, 'The big moments', t, AT('big', 3), W / 2, 548, 110, 800, PLUM)


def s4(c, t):
    tilt = 4 * smooth((t - (CUTS[4] - 0.6)) / 0.5)
    img_in(c, asset('book3q', 980), t, CUTS[3] + 0.05, W / 2, 1180, dur=4.5)
    for i, (txt, col, wd) in enumerate((('A spare room', ORANGE, ('spare', 0)), ('The paperwork', GREEN, ('paperwork', 0)),
                                        ('The training', MAG, ('training', 0)))):
        bullet(c, txt, col, t, AT(wd[0], 4, wd[1]) - 0.1, 150 + 10 * i * tilt / 4, 400 + i * 86 - tilt * i * 6, -tilt)


@functools.lru_cache(None)
def floor():
    """Perspective ivory/lilac checker floor (the reference's chess board, in OF colours)."""
    n, sz = 16, 120
    tex = np.zeros((n * sz, n * sz, 3), np.float32)
    for i in range(n):
        for j in range(n):
            tex[i * sz:(i + 1) * sz, j * sz:(j + 1) * sz] = IVORY * 0.97 if (i + j) % 2 else hx('#CDBBC8')
    src = np.float32([[0, 0], [n * sz, 0], [n * sz, n * sz], [0, n * sz]])
    dst = np.float32([[-300, 1150], [W + 300, 1150], [W + 2600, H + 400], [-2600, H + 400]])
    M = cv2.getPerspectiveTransform(src, dst)
    fl = cv2.warpPerspective(tex, M, (W, H))
    m = cv2.warpPerspective(np.ones((n * sz, n * sz), np.float32), M, (W, H))
    fade = np.clip((np.arange(H, dtype=np.float32) - 1150) / 260, 0, 1)[:, None]
    return fl, (m * fade)[..., None]


def s5(c, t):
    fl, m = floor()
    u = smooth((t - CUTS[4]) / 0.5)
    c[:] = c * (1 - m * u) + fl * m * u
    img_in(c, asset('house', 240), t, CUTS[4] + 0.1, 250, 1180, dur=1.8)
    img_in(c, asset('house', 640), t, CUTS[4] + 0.2, 700, 1290, dur=1.8)
    row(c, 'But', t, AT('but', 5), 110, 430, 50, 400, SMALL, 'l')
    row(c, 'Belonging', t, AT('belonging', 5), 104, 520, 116, 800, PLUM, 'l')
    row(c, "Doesn't live there.", t, AT("doesn't", 5), 110, 620, 50, 400, SMALL, 'l')


def s6(c, t):
    img_in(c, spread(), t, CUTS[5] + 0.02, W / 2, 1040, kb=0.06, dur=2.2)
    card = np.ones((330, 760), np.float32)
    k = smooth((t - AT('it', 6) + 0.1) / 0.3)
    paste(c, np.dstack([card[..., None] * IVORY, card * 0.88 * k]), W / 2, 1040)
    row(c, 'It lives in', t, AT('it', 6), W / 2, 950, 48, 400, SMALL)
    row(c, 'The small', t, AT('small', 6), W / 2, 1035, 104, 800, PLUM)
    row(c, 'Things', t, AT('things', 6), W / 2, 1135, 104, 800, LILAC)
    # glow bloom from the centre into the next beat
    b = prog(t, 14.95, CUTS[6] + 0.05)
    if b > 0:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = 30 + 1500 * e_in(b)
        g = np.clip(1 - (np.hypot(xx - W / 2, yy - 1040) - r) / 160, 0, 1)[..., None]
        c[:] = c * (1 - g) + IVORY * g


def e_in(u):
    return u ** 2.2


def pin_top(c, t, t0):
    u = (t - t0) / 0.45
    if u <= 0:
        return
    k = e_back(clamp(u), 1.6)
    paste(c, xform(asset('pin', 110), 1.0, 0), W / 2, 300 - 180 * (1 - clamp(u * 1.4)) + 0 * k, clamp(u * 3))


def pin_text(c, t, big, small, tb, ts, out_t=None):
    a = 1.0
    if out_t is not None and t > out_t:
        a = 1 - clamp((t - out_t) / 0.25)
    tmp = c.copy()
    row(tmp, big, t, tb, W / 2, 470, 112, 800, PLUM)
    row(tmp, small, t, ts, W / 2, 560, 50, 400, SMALL)
    if a < 1:
        tmp = cv2.GaussianBlur(tmp, (0, 0), 0.1 + 10 * (1 - a))
        m = np.zeros((H, W, 1), np.float32)
        m[350:640] = 1
        c[:] = c * (1 - m * 1.0) + (tmp * a + c * (1 - a)) * m
    else:
        c[:] = tmp


def s7(c, t):
    pin_top(c, t, CUTS[6] + 0.05)
    pin_text(c, t, 'A name', 'on the page', AT('name', 7), AT('on', 7), CUTS[7] - 0.25)
    sp = drawing_card()
    u = (t - (CUTS[6] + 0.25)) / 0.5
    if u > 0:
        k = e_out(clamp(u))
        img_in(c, sp, t, CUTS[6] + 0.25, W / 2, 1060, dur=1.4)
        cut = 1 - smooth((t - (CUTS[7] - 0.25)) / 0.25)
        if cut < 1:
            pass


@functools.lru_cache(None)
def pill(txt, col, avatar):
    t = text_spr(txt, 800, 66, tuple(col))
    w, h = t.shape[1] + (190 if avatar else 110), 140
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.rectangle(m, (h * 2, 0), (w * 4 - h * 2, h * 4), 255, -1)
    for x in (h * 2, w * 4 - h * 2):
        cv2.circle(m, (x, h * 2), h * 2, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    spr = np.dstack([m[..., None] * np.array((0.99, 0.985, 0.98), np.float32), m])
    if avatar:
        av = np.zeros((360, 360), np.uint8)
        cv2.circle(av, (180, 180), 172, 255, -1, cv2.LINE_AA)
        av = cv2.resize(av, (104, 104), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        paste(spr, np.dstack([av[..., None] * SKY, av]), 18 + 52, h / 2)
        paste(spr, text_spr('B', 900, 52, (1, 1, 1)), 18 + 52, h / 2)
        paste(spr, t, 140 + t.shape[1] / 2, h / 2)
    else:
        paste(spr, t, w / 2, h / 2)
    return shadowed(spr, 16, (0, 18), 0.22)


def s8(c, t):
    pin_top(c, t, -10)
    pin_text(c, t, 'A text', 'when City score', AT('text', 8), AT('when', 8), CUTS[8] - 0.25)
    for txt, col, av, t0, x in (('GOAL', PLUM, True, AT('text', 8) + 0.05, 470), ('I KNOW', hx('#2B2B2B'), False, AT('text', 8) + 0.29, 700)):
        u = (t - t0) / 0.35
        if u > 0:
            k = e_out(clamp(u))
            sp = blur(pill(txt, tuple(col), av), 8 * (1 - k))
            paste(c, sp, x + (-260 if av else 260) * (1 - k), 1000 + (0 if av else 150), clamp(u * 2))


def s9(c, t):
    pin_top(c, t, -10)
    pin_text(c, t, 'A drawing', 'on the fridge', AT('drawing', 9), AT('on', 9), CUTS[9] - 0.25)
    u = e_out(prog(t, CUTS[8] + 0.05, CUTS[8] + 0.75))
    fr = asset('fridge', 640)
    sp = blur(xform(fr, 1.0 + 0.03 * prog(t, CUTS[8], CUTS[9])), 12 * (1 - u))
    paste(c, sp, W / 2 + 140 + 600 * (1 - u), 1210, clamp(u * 2))


def s10(c, t):
    spaced(c, [('When', AT('when', 10)), ('those', AT('those', 10)), ('are', AT('are', 10))], t, W / 2, 880, 44)
    row(c, 'Missing', t, AT('missing', 10), W / 2, 980, 168, 900, PLUM)


def s11(c, t):
    # a giant out-of-focus house sweeps past the lens first (reference's falling-figure pass)
    p = prog(t, CUTS[10] - 0.1, CUTS[10] + 0.55)
    if 0 < p < 1:
        big = blur(xform(asset('house', 900), 2.2, 30), 28)
        paste(c, big, W / 2 - 200 + 300 * p, -400 + 1700 * e_inout(p), 0.9 * math.sin(math.pi * p))
    fl = prog(t, CUTS[10] + 0.25, CUTS[11])
    if fl > 0:
        y = 760 + 360 * e_out(fl)
        rot = 28 - 40 * fl
        sh = np.zeros((90, 520), np.float32)
        cv2.ellipse(sh, (260, 45), (int(150 + 100 * fl), 26), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        sh = cv2.GaussianBlur(sh, (0, 0), 14) * 0.25 * fl
        paste(c, np.dstack([sh[..., None] * DPLUM, sh]), W / 2, 1440)
        img_in(c, xform(asset('house', 520), 1.0, rot), t, CUTS[10] + 0.25, W / 2, y, kb=0.0)
    row(c, 'A bigger', t, AT('bigger', 11) - 0.12, W / 2, 440, 50, 400, SMALL)
    row(c, 'House', t, AT('house', 11), W / 2, 535, 118, 800, PLUM)
    row(c, "Doesn't fix it", t, AT("doesn't", 11), W / 2, 650, 92, 800, LILAC)


def s12(c, t):
    hz = asset('heart', 900)
    u = e_out(prog(t, CUTS[11], CUTS[11] + 0.7))
    paste(c, blur(xform(hz, 0.5, -20), 6 * (1 - u)), -40 + 80 * u, 380, u)
    paste(c, blur(xform(hz, 1.05 + 0.04 * prog(t, CUTS[11], CUTS[12]), 18), 10 * (1 - u)), W - 120 - 120 * u, 1500, u)
    row(c, 'Being noticed', t, AT('being', 12), W / 2, 880, 52, 400, SMALL)
    row(c, 'Does.', t, AT('does', 12), W / 2, 985, 150, 900, PLUM)


def s13(c, t):
    swap = AT('and', 13) - 0.15
    if t < swap + 0.25:
        a = 1 - clamp((t - swap) / 0.25)
        tmp = c.copy()
        row(tmp, "That's why we", t, AT("that's", 13), W / 2, 880, 50, 400, SMALL)
        row(tmp, 'Start small', t, AT('start', 13), W / 2, 980, 130, 800, PLUM)
        if a < 1:
            tmp = cv2.GaussianBlur(tmp, (0, 0), 0.1 + 12 * (1 - a))
        c[:] = c * (1 - a) + tmp * a
    if t >= swap:
        row(c, 'and', t, AT('and', 13) - 0.05, W / 2, 880, 50, 400, SMALL)
        row(c, 'Stay close', t, AT('stay', 13), W / 2, 980, 130, 800, PLUM)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]


def scene(i, t):
    c = ground().copy()
    SCENES[i](c, t)
    return c


@functools.lru_cache(None)
def end_card():
    c = ground().copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    c = c * 0.35 + IVORY * 0.65
    return c


def end(t):
    c = end_card().copy()
    u = t - END
    lg = logo_spr(640)
    k = e_out(clamp((u - 0.25) / 0.7))
    if k > 0:
        paste(c, blur(xform(lg, 1.12 - 0.12 * k), 14 * (1 - k)), W / 2, 760, k)
    row(c, 'Thinking about fostering', t, END + 0.95, W / 2, 1040, 66, 800, PLUM)
    row(c, 'in Greater Manchester?', t, END + 1.15, W / 2, 1125, 66, 800, PLUM)
    st = star(30, tuple(MAG))
    if u > 1.5:
        paste(c, st, W / 2 + 20 - F(400, 46).getlength('Start your enquiry  ·  Link in bio') / 2 - 34, 1250, clamp((u - 1.5) / 0.3))
    row(c, 'Start your enquiry  ·  Link in bio', t, END + 1.5, W / 2 + 20, 1250, 46, 400, SMALL)
    row(c, 'organicfostering.co.uk', t, END + 1.9, W / 2, 1760, 34, 400, SMALL)
    return c


def frame(t):
    if t >= END:
        c = end(t)
        f = prog(t, END, END + 0.45)                                  # plum flash into the end card
        if f < 1:
            fl = math.sin(math.pi * min(1, f * 1.15))
            c = c * (1 - fl) + PLUM * fl
        return c
    i = max(j for j in range(len(SCENES)) if t >= CUTS[j])
    D = 0.2
    nxt = CUTS[i + 1] if i + 1 < len(CUTS) else 99
    if i + 1 < len(SCENES) and t > nxt - D:                           # whole-frame blur dissolve into the next beat
        u = (t - (nxt - D)) / (2 * D)
        a = cv2.GaussianBlur(scene(i, t), (0, 0), 0.1 + 22 * u)
        b = cv2.GaussianBlur(scene(i + 1, t), (0, 0), 0.1 + 22 * (1 - u))
        k = smooth(u)
        c = a * (1 - k) + b * k
    elif i > 0 and t < CUTS[i] + D:
        u = (t - (CUTS[i] - D)) / (2 * D)
        a = cv2.GaussianBlur(scene(i - 1, t), (0, 0), 0.1 + 22 * u)
        b = cv2.GaussianBlur(scene(i, t), (0, 0), 0.1 + 22 * (1 - u))
        k = smooth(u)
        c = a * (1 - k) + b * k
    else:
        c = scene(i, t)
    if t > END - 0.3:                                                  # the ground sinks to lilac before the flash
        g = smooth((t - (END - 0.3)) / 0.3)
        c = c * (1 - 0.4 * g) + hx('#B9A7B4') * 0.4 * g
    chrome(c, t)
    lg = logo_spr(200)
    paste(c, lg, W / 2, 78, clamp(t / 0.4))
    if t < 0.3:
        c = cv2.GaussianBlur(c, (0, 0), 0.1 + 20 * (1 - t / 0.3))
    return c


def final(t):
    c = frame(t)
    rng = np.random.default_rng(int(t * FPS))
    return np.clip(c + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32), 0, 1)


def write(path, c):
    cv2.imwrite(path, (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        d = f'{S}/stills_ref'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            write(f'{d}/{int(float(ts) * 100):05d}.png', final(float(ts)))
            print('still', ts, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames_ref'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            write(f'{d}/{i:05d}.png', final(i / FPS))
            if i % 25 == 0:
                print('frame', i, flush=True)
