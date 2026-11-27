"""OF reel "Closer than you think" - 9:16, 37.9 s, 30 fps. FOOH + interface overlays on the brand's own campaign
photography (after the user's references): a search bar types "foster carer near me", a giant 3D plum map pin with the
OF emblem drops into a golden-hour field, "Could I do this?" cards pop, a 3D paper aeroplane lifts off a homework book
and loops round the room, a counter rolls to 6,000, support cards stack, a green circle wipe opens the ivory end card.
Narration: Sonia (edge-tts). Brand: OF guidelines v1.0 (Nunito, plum/magenta/orange/green, ivory, rounded corners,
pillar tags, three-colour bar, no exclamation marks or em dashes, Start your enquiry).

Usage: python3 reel_of.py still 1,5 | range a b
"""
import os, sys, math, functools, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_ofreel'
BG = f'{S}/bgimg'
FON = f'{ROOT}/workspace_sol/fonts'
W, H = 1080, 1920
FPS = 30
INFO = json.load(open(f'{S}/tts/info.json'))
DUR = INFO['dur']
NF = int(DUR * FPS)
T = dict(INFO['scenes'])
ORDER = ['s1', 's2', 's3', 's4', 's5', 's6', 'end']


def WT(word, line):
    for w in INFO['words']:
        if w[3] == line and re.sub(r"[^a-z0-9]", '', w[0].lower()).startswith(word):
            return w[1]
    return INFO['lines'][line][0]


def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


PLUM, MAG, ORANGE, GREEN = hx('#5B174F'), hx('#B7006E'), hx('#FF6411'), hx('#61A80A')
IVORY, PAPER, BLUSH, PEACH, LEAF = hx('#FCF8F5'), hx('#FFFDFB'), hx('#F6EAF3'), hx('#FFD4BA'), hx('#E8F3D8')
INK, MUTED, OINK, GINK, WHITE = hx('#321F35'), hx('#655563'), hx('#933900'), hx('#3F6F08'), hx('#FFFFFF')


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_in(u):
    return clamp(u) ** 3


def e_inout(u):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def e_back(u, s=1.7):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ helpers
def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', int(s))


@functools.lru_cache(maxsize=2048)
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
    if not len(ys):
        return np.zeros((4, 4, 4), np.float32)
    a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 1):xs.max() + 2]
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


def xform(spr, scale=1.0, rot=0.0, sy=None):
    sy = scale if sy is None else sy
    if abs(scale - 1) < 1e-3 and abs(rot) < 1e-3 and abs(sy - 1) < 1e-3:
        return spr
    h, w = spr.shape[:2]
    D = int(math.hypot(w * scale, h * sy)) + 4
    a = math.radians(rot)
    M = np.array([[scale * math.cos(a), sy * math.sin(a), 0], [-scale * math.sin(a), sy * math.cos(a), 0]], np.float32)
    c = M[:, :2] @ np.array([w / 2, h / 2], np.float32)
    M[:, 2] = np.array([D / 2, D / 2]) - c
    return cv2.warpAffine(spr, M, (D, D), flags=cv2.INTER_LINEAR)


@functools.lru_cache(maxsize=128)
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


def with_shadow(spr, blur=18, dy=14, amt=0.28):
    h, w = spr.shape[:2]
    p = blur * 3 + dy
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    sh = np.zeros(out.shape[:2], np.float32)
    sh[p + dy:p + dy + h, p:p + w] = spr[..., 3]
    out[..., 3] = cv2.GaussianBlur(sh, (0, 0), blur) * amt
    reg = out[p:p + h, p:p + w]
    a = spr[..., 3:4]
    reg[..., :3] = spr[..., :3] + reg[..., :3] * (1 - a)
    reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)
    return out


def pop(c, spr, x, y, t, t0, dur=0.45, anchor='c', a=1.0):
    u = (t - t0) / dur
    if u <= 0:
        return
    s = e_back(clamp(u), 1.8)
    sp = xform(spr, max(0.02, s))
    if anchor == 'l':
        x = x + spr.shape[1] / 2
    paste(c, sp, x, y, a * clamp(u * 3))


def rise(c, spr, x, y, t, t0, anchor='c', dist=36, dur=0.5, a=1.0):
    u = (t - t0) / dur
    if u <= 0:
        return
    k = e_out(u)
    if anchor == 'l':
        x = x + spr.shape[1] / 2
    paste(c, spr, x, y + dist * (1 - k), a * clamp(u * 1.8))


@functools.lru_cache(None)
def _grid():
    return np.mgrid[0:H, 0:W].astype(np.float32)


# ------------------------------------------------------------------ plates (brand photography, graded, Ken Burns)
@functools.lru_cache(maxsize=8)
def plate_src(name):
    im = cv2.imread(f'{BG}/{name}')[..., ::-1].astype(np.float32) / 255
    return im


def plate(name, t, t0, t1, fx=0.5, fy=0.5, z0=1.0, z1=1.08, dx=0.0):
    img = plate_src(name)
    ih, iw = img.shape[:2]
    u = prog(t, t0 - 0.5, t1 + 0.5)
    z = z0 + (z1 - z0) * u
    sc = max(W / iw, H / ih) * z
    cx = iw * fx + dx * u * iw
    cy = ih * fy
    M = np.float32([[sc, 0, W / 2 - cx * sc], [0, sc, H / 2 - cy * sc]])
    c = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return grade(c)


def grade(c):
    yy, xx = _grid()
    v = 1 - 0.32 * (np.hypot((xx - W / 2) / W, (yy - H / 2) / H) ** 2)
    c = c * v[..., None]
    c = c * np.array((1.03, 1.0, 0.95), np.float32)
    return np.clip(c, 0, 1)


def bottom_shade(c, y0=1150, amt=0.55):
    g = np.clip((np.arange(H, dtype=np.float32) - y0) / (H - y0), 0, 1)[:, None, None] ** 1.2 * amt
    c[:] = c * (1 - g) + INK * g


def top_shade(c, y1=700, amt=0.45):
    g = np.clip(1 - np.arange(H, dtype=np.float32) / y1, 0, 1)[:, None, None] ** 1.5 * amt
    c[:] = c * (1 - g) + INK * g


# ------------------------------------------------------------------ interface pieces
def magnifier(size, col):
    S4 = size * 4
    m = np.zeros((S4, S4), np.uint8)
    cv2.circle(m, (int(S4 * 0.42), int(S4 * 0.42)), int(S4 * 0.28), 255, int(S4 * 0.09), cv2.LINE_AA)
    cv2.line(m, (int(S4 * 0.62), int(S4 * 0.62)), (int(S4 * 0.86), int(S4 * 0.86)), 255, int(S4 * 0.1), cv2.LINE_AA)
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return np.dstack([m[..., None] * np.array(col, np.float32), m])


def search_bar(c, t, t0, query, y=300, a=1.0, typed_until=None, w=920):
    """Rounded search bar that drops in and types the query with a blinking cursor."""
    u = (t - t0) / 0.45
    if u <= 0:
        return
    k = e_out(u)
    bar = rrect(w, 118, 59, PAPER)
    paste(bar, magnifier(44, MUTED), 62, 59)
    t_type = t0 + 0.35
    n = int(clamp((t - t_type) / 0.065, 0, len(query))) if typed_until is None else typed_until
    s = query[:n]
    x = 104
    if s:
        sp = text(s, 700, 44, tuple(INK))
        paste(bar, sp, x, 59, 1, 'l')
        x += sp.shape[1] + 4
    if (int(t * 2.2) % 2 == 0) or n < len(query):
        bar[34:84, int(x):int(x) + 4, :3] = MAG
        bar[34:84, int(x):int(x) + 4, 3] = 1
    paste(c, with_shadow(bar, 22, 14, 0.3), W / 2, y - 60 * (1 - k), a * clamp(u * 2))
    return n


@functools.lru_cache(None)
def emblem(size):
    rgb = cv2.imread(f'{BG}/img-006.png')[..., ::-1].astype(np.float32) / 255
    al = cv2.imread(f'{BG}/img-007.png', cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    ys, xs = np.where(al > 0.1)
    rgb, al = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1], al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = size / max(al.shape)
    rgb = cv2.resize(rgb, (int(al.shape[1] * sc), int(al.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    al = cv2.resize(al, (int(al.shape[1] * sc), int(al.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    return np.dstack([rgb * al[..., None], al]).astype(np.float32)


@functools.lru_cache(None)
def logo(width):
    lg = cv2.imread(f'{ROOT}/workspace_three/web/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    lg = cv2.resize(lg, (width, int(lg.shape[0] * width / lg.shape[1])), interpolation=cv2.INTER_AREA)
    return np.dstack([lg[..., 2::-1] * lg[..., 3:4], lg[..., 3]]).astype(np.float32)


@functools.lru_cache(None)
def pin_spr(height):
    im = cv2.imread(f'{S}/assets/pin.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    face = json.load(open(f'{S}/assets/pin_face.json'))
    pm = np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]])
    em = emblem(int(face['r'] * 1.5))
    paste(pm, em, face['cx'], face['cy'])
    ys, xs = np.where(pm[..., 3] > 0.5)
    pm = pm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = height / pm.shape[0]
    return cv2.resize(pm, (int(pm.shape[1] * sc), int(pm.shape[0] * sc)), interpolation=cv2.INTER_AREA)


@functools.lru_cache(None)
def plane_spr(size):
    im = cv2.imread(f'{ROOT}/workspace_land/assets/plane.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    ys, xs = np.where(im[..., 3] > 0.5)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = size / max(im.shape[:2])
    im = cv2.resize(im, (int(im.shape[1] * sc), int(im.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


def caption(c, t, t0, plain, accent, y=1640, size=64, col=WHITE):
    """Lower-third line with one accented word (magenta on light, blush on photos) and a hand-drawn underline."""
    f1, f2 = F(800, size), F(800, size)
    w1 = f1.getlength(plain + ' ') + 6
    w2 = f2.getlength(accent)
    x0 = W / 2 - (w1 + w2) / 2
    s1 = text(plain, 800, size, tuple(col), -0.02)
    s2 = text(accent, 800, size, tuple(hx('#FFB3DD') if col is WHITE else MAG), -0.02)
    rise(c, s1, x0, y, t, t0, 'l')
    rise(c, s2, x0 + w1, y, t, t0 + 0.3, 'l')
    u = prog(t, t0 + 0.5, t0 + 0.9)
    if u > 0:
        n = 40
        pts = [(x0 + w1 + (w2 + 8) * i / n, y + size * 0.72 + 6 * math.sin(i / n * 3.3) - 5 * i / n) for i in range(int(n * u) + 1)]
        if len(pts) > 1:
            lay = np.zeros((H, W), np.uint8)
            cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 7, cv2.LINE_AA, shift=2)
            m = lay.astype(np.float32)[..., None] / 255
            c[:] = c * (1 - m) + ORANGE * m


def card_row(label, tick, w=760, tag_col=None):
    """White rounded card with a label and a tick (green) or a soft 'Not needed' pill."""
    cd = rrect(w, 128, 34, PAPER)
    paste(cd, text(label, 800, 46, tuple(INK), -0.02), 44, 64, 1, 'l')
    if tick == 'tick':
        circ = np.zeros((72 * 4, 72 * 4), np.uint8)
        cv2.circle(circ, (144, 144), 140, 255, -1, cv2.LINE_AA)
        circ = cv2.resize(circ, (72, 72), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        sp = np.dstack([circ[..., None] * GREEN, circ])
        tk = np.zeros((72 * 4, 72 * 4), np.uint8)
        cv2.polylines(tk, [np.array([(70, 150), (122, 200), (212, 96)], np.int32)], False, 255, 26, cv2.LINE_AA)
        tk = cv2.resize(tk, (72, 72), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        sp[..., :3] = sp[..., :3] * (1 - tk[..., None]) + WHITE * tk[..., None]
        paste(cd, sp, w - 70, 64)
    else:
        pill = rrect(240, 64, 32, BLUSH)
        paste(pill, text('Not needed', 800, 32, tuple(MAG)), 120, 32)
        paste(cd, pill, w - 150, 64)
    return with_shadow(cd, 18, 12, 0.25)


def tag_pill(word, kind):
    bg, fg, leaf = {'n': (BLUSH, MAG, MAG), 'd': (PEACH, OINK, ORANGE), 'g': (LEAF, GINK, GREEN)}[kind]
    tw = F(800, 46).getlength(word)
    p = rrect(tw + 130, 92, 46, bg)
    lf = np.zeros((40 * 4, 40 * 4), np.uint8)
    cv2.ellipse(lf, (80, 80), (70, 34), -40, 0, 360, 255, -1, cv2.LINE_AA)
    lf = cv2.resize(lf, (40, 40), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    paste(p, np.dstack([lf[..., None] * leaf, lf]), 52, 46)
    paste(p, text(word, 800, 46, tuple(fg)), 82 + tw / 2, 46)
    return with_shadow(p, 16, 10, 0.25)


# ------------------------------------------------------------------ scenes
def s1(t):
    t0, t1 = T['s1'], T['s2']
    c = plate('img-033.jpg', t, t0, t1, 0.5, 0.42, 1.04, 1.12)
    top_shade(c, 760, 0.35)
    bottom_shade(c, 1200, 0.55)
    search_bar(c, t, t0 + 0.25, 'foster carer near me', 300)
    # a suggestion row drops under the bar (as in the reference)
    u = (t - (t0 + 2.05)) / 0.4
    if u > 0:
        row = rrect(920, 120, 30, PAPER)
        paste(row, emblem(70), 70, 60)
        paste(row, text('Organic Fostering', 800, 40, tuple(INK)), 130, 44, 1, 'l')
        paste(row, text('Greater Manchester · near you', 400, 30, tuple(MUTED)), 130, 84, 1, 'l')
        paste(c, with_shadow(row, 18, 12, 0.25), W / 2, 440 + 30 * (1 - e_out(u)), clamp(u * 2))
    caption(c, t, WT('land', 'v1') - 0.25, 'What if the answer is', 'you?')
    if t < t0 + 0.35:
        c = cv2.GaussianBlur(c, (0, 0), 0.1 + 18 * (1 - (t - t0) / 0.35))
    return c


def s2(t):
    t0, t1 = T['s2'], T['s3']
    c = plate('img-000.jpg', t, t0, t1, 0.43, 0.55, 1.0, 1.07)
    tf, ti = t0 + 0.05, t0 + 0.55                                         # pin falls, impact
    if t > ti:                                                             # camera shake after impact
        k = math.exp(-7 * (t - ti))
        M = np.float32([[1, 0, 14 * k * math.sin((t - ti) * 70)], [0, 1, 18 * k * math.cos((t - ti) * 60)]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    gx, gy = 300, 1440                                                     # landing point in open grass
    ph = 820
    if t > tf:
        u = clamp((t - tf) / (ti - tf))
        y = -ph + (gy + ph * 0.02 - (-ph)) * e_in(u)
        squash = 1.0
        if t > ti:
            v = t - ti
            squash = 1 - 0.1 * math.exp(-6 * v) * math.cos(v * 18)
        sp = pin_spr(ph)
        sp = xform(sp, 2 - squash, 0, squash)
        sh = np.zeros((140, 600), np.float32)                              # contact shadow grows as it falls
        cv2.ellipse(sh, (300, 70), (int(80 + 180 * u), int(14 + 26 * u)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        sh = cv2.GaussianBlur(sh, (0, 0), 16) * 0.55 * u
        paste(c, np.dstack([sh[..., None] * INK * 0.0, sh]), gx, gy + 10)
        if u < 1:
            sp = cv2.blur(sp, (1, int(2 + 60 * u)))
        paste(c, sp, gx, y - sp.shape[0] / 2 + ph / 2 * 0 + (sp.shape[0] - ph) / 2 * 0)
        if t > ti:                                                         # dust burst
            v = t - ti
            rng = np.random.default_rng(3)
            for i in range(26):
                a = rng.uniform(math.pi * 1.05, math.pi * 1.95)
                spd = rng.uniform(250, 650)
                r = rng.uniform(10, 34) * (1 + 1.5 * v)
                px = gx + math.cos(a) * spd * (1 - math.exp(-3 * v)) / 1.0
                py = gy + math.sin(a) * spd * 0.35 * (1 - math.exp(-3 * v)) + 60 * v * v
                al = 0.45 * math.exp(-1.6 * v)
                d = np.zeros((int(r * 4) + 2, int(r * 4) + 2), np.float32)
                cv2.circle(d, (d.shape[1] // 2, d.shape[0] // 2), int(r), 1.0, -1, cv2.LINE_AA)
                d = cv2.GaussianBlur(d, (0, 0), r * 0.5) * al
                paste(c, np.dstack([d[..., None] * hx('#D9C4A0'), d]), px, py)
    bottom_shade(c, 1450, 0.4)
    u = (t - (t0 + 1.0)) / 0.45                                            # the result card slides up
    if u > 0:
        cd = rrect(940, 210, 40, PAPER)
        paste(cd, emblem(130), 100, 105)
        paste(cd, text('Organic Fostering', 800, 52, tuple(INK), -0.02), 190, 72, 1, 'l')
        paste(cd, text('Greater Manchester', 400, 34, tuple(MUTED)), 190, 122, 1, 'l')
        badge = rrect(370, 54, 27, LEAF)
        paste(badge, text('Rated Good by Ofsted', 800, 28, tuple(GINK)), 185, 27)
        paste(cd, badge, 190 + 185, 168)
        paste(c, with_shadow(cd, 22, 16, 0.3), W / 2, 1700 + 260 * (1 - e_out(u)), clamp(u * 2))
    return c


def s3(t):
    t0, t1 = T['s3'], T['s4']
    c = plate('img-034.jpg', t, t0, t1, 0.55, 0.4, 1.03, 1.1)
    top_shade(c, 600, 0.4)
    bottom_shade(c, 900, 0.6)
    rise(c, text('Could I do this?', 800, 78, tuple(WHITE), -0.02), W / 2, 250, t, t0 + 0.15)
    rows = [('All the answers', 'not', WT('answers', 'v3') - 0.15), ('A spare bedroom', 'tick', WT('spare', 'v3') - 0.1),
            ('Time and patience', 'tick', WT('time', 'v3') - 0.1)]
    for i, (lab, kind, tt) in enumerate(rows):
        pop(c, card_row(lab, kind), W / 2, 1180 + i * 168, t, tt)
    return c


def plane_path(u):
    """The paper aeroplane's flight across the kitchen: lifts off the book, loops, exits right."""
    pts = np.array([(420, 1720), (600, 1610), (800, 1570), (960, 1460), (880, 1340), (740, 1400), (780, 1550), (960, 1610), (1150, 1530), (1380, 1430)], np.float32)
    P = np.vstack([pts[0], pts, pts[-1]])
    seg = len(pts) - 1
    x = clamp(u) * seg
    i = min(int(x), seg - 1)
    f = x - i
    p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
    pt = 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)
    return pt


def s4(t):
    t0, t1 = T['s4'], T['s5']
    c = plate('img-035.jpg', t, t0, t1, 0.45, 0.45, 1.05, 1.1)
    top_shade(c, 600, 0.45)
    bottom_shade(c, 1500, 0.3)
    rise(c, text('Matching that sees', 800, 70, tuple(WHITE), -0.02), W / 2, 230, t, t0 + 0.2)
    rise(c, text('the whole child.', 800, 70, tuple(hx('#FFB3DD')), -0.02), W / 2, 318, t, t0 + 0.4)
    fa, fb = t0 + 0.4, t1 + 0.1                                            # the plane's flight
    u = e_inout(prog(t, fa, fb))
    if t > fa:
        n = 60
        trail = [plane_path(u * i / n) for i in range(n + 1)]
        lay = np.zeros((H, W), np.uint8)
        cv2.polylines(lay, [(np.array(trail) * 4).astype(np.int32)], False, 255, 22, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.9
        c = c * (1 - m) + PLUM * m
        p = plane_path(u)
        q = plane_path(min(1, u + 0.01))
        hd = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0] + 1e-6))
        sp = xform(plane_spr(260), 1.0, -(hd + 7))
        paste(c, with_shadow(sp, 14, 24, 0.25), p[0], p[1] - 30)
    for i, (w, kind, tt) in enumerate((('Culture', 'n', WT('culture', 'v4')), ('Faith', 'd', WT('faith', 'v4')), ('Language', 'g', WT('language', 'v4')))):
        pop(c, tag_pill(w, kind), (250, 545, 840)[i], 470, t, tt - 0.1)
    return c


def s5(t):
    t0, t1 = T['s5'], T['s6']
    c = plate('img-029.jpg', t, t0, t1, 0.5, 0.5, 1.04, 1.1)
    c = c * 0.7 + INK * 0.3 * 0.6
    bottom_shade(c, 700, 0.75)
    rise(c, text('Right now', 800, 60, tuple(hx('#FFB3DD')), -0.02), W / 2, 760, t, t0 + 0.15)
    t6 = WT('6', 'v5')
    k = e_out(prog(t, t0 + 0.3, t6 + 0.45))
    if t > t0 + 0.3:
        n = int(round(6000 * k / 10) * 10)
        num = text(f'{n:,}', 900, 300, tuple(WHITE), -0.03)
        s = 1 + 0.12 * math.exp(-9 * max(0, t - t6 - 0.45)) * (t > t6 + 0.45)
        paste(c, xform(num, s), W / 2, 1010)
    rise(c, text('more foster families needed', 800, 54, tuple(WHITE), -0.02), W / 2, 1230, t, WT('more', 'v5') - 0.1)
    rise(c, text('across the UK in the next 12 months', 400, 44, tuple(WHITE)), W / 2, 1310, t, WT('more', 'v5') + 0.15)
    rise(c, text('Source: The Fostering Network, 2026', 400, 30, tuple(hx('#D8C8D4'))), W / 2, 1800, t, WT('families', 'v5'))
    return c


def s6(t):
    t0, t1 = T['s6'], T['end']
    c = plate('img-036.jpg', t, t0, t1, 0.55, 0.42, 1.03, 1.09)
    top_shade(c, 650, 0.45)
    bottom_shade(c, 800, 0.5)
    rise(c, text('We stay alongside you', 800, 66, tuple(WHITE), -0.02), W / 2, 240, t, t0 + 0.15)
    u = (t - (t0 + 0.4)) / 0.5                                             # support panel (the reference's "popular times")
    if u > 0:
        pw, ph = 940, 640
        panel = rrect(pw, ph, 40, PAPER)
        paste(panel, text('Support built around your household', 800, 36, tuple(PLUM)), 48, 62, 1, 'l')
        paste(c, with_shadow(panel, 24, 18, 0.3), W / 2, 1250 + 300 * (1 - e_out(u)), clamp(u * 2))
        items = [('Training', WT('training', 'v6')), ('Advice outside normal hours', WT('advice', 'v6')),
                 ('Published allowances', WT('published', 'v6')), ('Rated Good by Ofsted', WT('allowances', 'v6') + 0.6)]
        for i, (lab, tt) in enumerate(items):
            v = (t - (tt - 0.1)) / 0.4
            if v <= 0:
                continue
            y = 1250 - ph / 2 + 160 + i * 118 + 300 * (1 - e_out(u))
            bar_w = 820 * e_out(v)
            paste(c, rrect(max(40, bar_w), 92, 46, LEAF), W / 2 - 410 + max(40, bar_w) / 2, y, clamp(v * 3))
            lf = np.zeros((44 * 4, 44 * 4), np.uint8)
            cv2.ellipse(lf, (88, 88), (78, 38), -40, 0, 360, 255, -1, cv2.LINE_AA)
            lf = cv2.resize(lf, (44, 44), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
            paste(c, np.dstack([lf[..., None] * GREEN, lf]), W / 2 - 360, y, clamp(v * 3))
            paste(c, text(lab, 800, 40, tuple(GINK)), W / 2 - 320, y, clamp((v - 0.2) * 3), 'l')
    return c


@functools.lru_cache(None)
def leaf_pattern():
    """The brand's leaf pattern, very soft, for the end card."""
    c = np.zeros((H, W), np.float32)
    cols = np.zeros((H, W, 3), np.float32)
    rng = np.random.default_rng(5)
    for y in range(40, H, 120):
        for x in range(40 + (60 if (y // 120) % 2 else 0), W, 120):
            lf = np.zeros((48 * 4, 48 * 4), np.uint8)
            cv2.ellipse(lf, (96, 96), (84, 36), rng.choice([-45, 45, -30]), 0, 360, 255, -1, cv2.LINE_AA)
            lf = cv2.resize(lf, (48, 48), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
            col = [PLUM, PLUM, PLUM, MAG, GREEN][rng.integers(0, 5)]
            ys, xs = slice(max(0, y - 24), min(H, y + 24)), slice(max(0, x - 24), min(W, x + 24))
            sub = lf[:ys.stop - ys.start, :xs.stop - xs.start]
            c[ys, xs] = np.maximum(c[ys, xs], sub)
            cols[ys, xs] = np.where(sub[..., None] > 0, col, cols[ys, xs])
    return cols, c


@functools.lru_cache(None)
def end_base():
    c = np.ones((H, W, 3), np.float32) * IVORY
    cols, m = leaf_pattern()
    yy, xx = _grid()
    fade = np.clip((np.hypot(xx - W / 2, yy - 900) - 380) / 500, 0, 1) * 0.10
    c = c * (1 - (m * fade)[..., None]) + cols * (m * fade)[..., None]
    for i, col in enumerate((MAG, ORANGE, GREEN)):                          # three-colour bar sign-off
        c[H - 26:, int(W * i / 3):int(W * (i + 1) / 3)] = col
    return c


def end(t):
    t0 = T['end']
    c = end_base().copy()
    paste(c, logo(560), W / 2, 420, clamp((t - t0 - 0.1) / 0.4))
    head = 'Room to grow, roots to keep.'
    n = int(clamp((t - (t0 + 0.45)) / 0.045, 0, len(head)))
    if n:
        sp = text(head[:n], 800, 74, tuple(PLUM), -0.025)
        full = text(head, 800, 74, tuple(PLUM), -0.025)
        paste(c, sp, W / 2 - full.shape[1] / 2, 700, 1, 'l')
    search_bar(c, t, t0 + 1.9, 'organicfostering.co.uk', 900, w=860)
    bu = (t - WT('start', 'v7') - 0.15) / 0.45
    bt0 = max(t0 + 2.6, WT('start', 'v7'))
    btn = rrect(560, 120, 60, MAG)
    paste(btn, text('Start your enquiry', 800, 46, tuple(WHITE)), 280, 60)
    press = prog(t, bt0 + 1.9, bt0 + 2.15)
    sc = 1 - 0.06 * math.sin(math.pi * press)
    pop(c, xform(with_shadow(btn, 18, 12, 0.3), sc), W / 2, 1110, t, bt0)
    rise(c, text('It carries no obligation.', 700, 38, tuple(MUTED)), W / 2, 1230, t, WT('it', 'v7') - 0.05)
    rise(c, text('0161 241 1332  ·  organicfostering.co.uk', 700, 34, tuple(PLUM)), W / 2, 1720, t, WT('it', 'v7') + 0.3)
    # cursor glides to the button and taps
    if t > bt0 + 0.9:
        k = e_inout(prog(t, bt0 + 0.9, bt0 + 1.8))
        px, py = W + 60 + (W / 2 + 120 - W - 60) * k, H + 60 + (1130 - H - 60) * k
        pts = np.array([(0, 0), (0, 46), (12, 35), (21, 55), (29, 51), (20, 32), (36, 32)], np.float32) * 1.4
        m = np.zeros((96 * 4, 70 * 4), np.uint8)
        cv2.fillPoly(m, [((pts + 6) * 4).astype(np.int32)], 255, cv2.LINE_AA)
        m = cv2.resize(m, (70, 96), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        edge = cv2.dilate(m, np.ones((5, 5), np.uint8))
        cur = np.dstack([m[..., None] * INK + (edge - m)[..., None] * WHITE, edge])
        paste(c, cur, px + 29, py + 42)
        if press > 0 and press < 1:
            ring = np.zeros((240, 240), np.float32)
            cv2.circle(ring, (120, 120), int(20 + 80 * press), 1.0, 5, cv2.LINE_AA)
            ring *= 0.7 * (1 - press)
            paste(c, np.dstack([ring[..., None] * MAG, ring]), px, py)
    return c


SCENES = {'s1': s1, 's2': s2, 's3': s3, 's4': s4, 's5': s5, 's6': s6, 'end': end}


# ------------------------------------------------------------------ transitions
def tr_zoom(A, B, u):
    """Zoom-through: punch into the search result, land in the next scene."""
    if u < 0.5:
        z = 1 + 0.5 * e_in(u / 0.5)
        M = cv2.getRotationMatrix2D((W / 2, 440), 0, z)
        a = cv2.warpAffine(A, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        return cv2.GaussianBlur(a, (0, 0), 0.1 + 14 * (u / 0.5))
    z = 1.3 - 0.3 * e_out((u - 0.5) / 0.5)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    b = cv2.warpAffine(B, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return cv2.GaussianBlur(b, (0, 0), 0.1 + 14 * (1 - (u - 0.5) / 0.5))


def tr_whip(A, B, u):
    k = e_inout(u)
    off = int(W * k)
    out = np.empty_like(A)
    out[:, :W - off] = A[:, off:]
    out[:, W - off:] = B[:, :off]
    v = 1 - abs(2 * u - 1)
    L = int(2 + 150 * v ** 1.5)
    return cv2.blur(out, (L, 1)) if L > 2 else out


def tr_leak(A, B, u):
    k = smooth(u)
    yy, xx = _grid()
    g = np.exp(-((xx * 0.7 + yy * 0.3 - (-400 + 2200 * u)) / 300) ** 2) * math.sin(math.pi * u) * 0.6
    out = A * (1 - k) + B * k
    return np.clip(out + g[..., None] * np.array((1.0, 0.75, 0.45), np.float32), 0, 1)


def tr_trail(A, B, u):
    """The paper aeroplane's plum trail sweeps across and becomes the cut."""
    k = e_inout(u)
    yy, xx = _grid()
    d = (xx * 0.55 - yy * 0.25)
    edge_in = -1200 + 3200 * clamp(k * 1.3)
    edge_out = -1200 + 3200 * clamp(k * 1.3 - 0.3)
    band = ((d < edge_in) & (d > edge_out)).astype(np.float32)
    band = cv2.GaussianBlur(band, (0, 0), 2)[..., None]
    passed = (d <= edge_out).astype(np.float32)[..., None]
    base = A * (1 - passed) + B * passed
    return base * (1 - band) + PLUM * band


def tr_push_up(A, B, u):
    k = e_inout(u)
    off = int(H * k)
    out = np.empty_like(A)
    out[:H - off] = A[off:]
    out[H - off:] = B[:off]
    v = 1 - abs(2 * u - 1)
    L = int(2 + 120 * v ** 1.5)
    return cv2.blur(out, (1, L)) if L > 2 else out


def tr_circle(A, B, u, cx=W / 2, cy=1450):
    k = e_inout(u)
    yy, xx = _grid()
    dist = np.hypot(xx - cx, yy - cy)
    r = 2300 * k
    m = np.clip((r - dist) / 3, 0, 1)[..., None]
    edge = np.exp(-((dist - r) / 12) ** 2)[..., None] * 0.9 * (0 < k < 1)
    out = A * (1 - m) + B * m
    return out * (1 - edge) + GREEN * edge


TR = {'s2': tr_zoom, 's3': tr_whip, 's4': tr_leak, 's5': tr_trail, 's6': tr_push_up, 'end': tr_circle}
D = 0.35


def base(t):
    idx = max(i for i, k in enumerate(ORDER) if t >= T[k])
    key = ORDER[idx]
    nxt = ORDER[idx + 1] if idx + 1 < len(ORDER) else None
    if nxt and t > T[nxt] - D:
        u = (t - (T[nxt] - D)) / (2 * D)
        return TR[nxt](SCENES[key](t), SCENES[nxt](t), u)
    if idx > 0 and t < T[key] + D:
        prev = ORDER[idx - 1]
        u = (t - (T[key] - D)) / (2 * D)
        return TR[key](SCENES[prev](t), SCENES[key](t), u)
    return SCENES[key](t)


def frame(t):
    c = np.clip(base(t), 0, 1)
    rng = np.random.default_rng(int(t * FPS))
    return np.clip(c + rng.normal(0, 0.012, (H, W, 1)).astype(np.float32), 0, 1)       # light film grain


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
