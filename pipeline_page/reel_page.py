"""OF "Can I add a page?" - 9:16, 34 s, 25 fps (brief: Organic Fostering Reel Motion Guide).
Look after the user's Pinterest reference: pale ivory base with a low-opacity grid, stacked bold/light type with
star bullets, monochrome photo cutouts, soft defocus and a soft expanding circle - with OF plum accents and a
sky-blue scarf. Overhead: a 3D open book (plum cover), photos landing on the page, a 3D scarf, phone, pen.

00-04 the empty page (tap -> four-point star) | 04-10 household in two pictures, the page corner lifts to camera |
10-18 the scarf (mostly monochrome so the blue catches the eye), "GOAL!" / "I KNOW!" bubbles on "text" |
18-26 the pen writes "Match day", "3:00" stamped on "Three" | 26-29 pull back, "Room to grow, roots to keep." |
29-34 ivory circle from the scarf stitch -> end card.

Usage: python3 reel_page.py still 1,5 | range a b | board
"""
import os, sys, json, math, functools, re
HERE = os.path.dirname(os.path.abspath(__file__))
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
FR = 1 / FPS

IVORY = np.array((252, 248, 245), np.float32) / 255
CHAR = np.array((43, 43, 43), np.float32) / 255
PLUM = np.array((91, 23, 79), np.float32) / 255
SKY = np.array((78, 155, 214), np.float32) / 255
GREY = np.array((120, 116, 112), np.float32) / 255

INFO = json.load(open(f'{S}/tts/info.json'))
WORDS = INFO['words']
LINES = INFO['lines']


def norm(w):
    return re.sub(r"[^a-z0-9']", '', w.lower())


def AT(wd, k=0):
    n = 0
    for w in WORDS:
        if norm(w[0]) == norm(wd):
            if n == k:
                return w[1]
            n += 1
    raise KeyError(wd)


T_TAP = AT('this') - 0.05
T_KITCHEN, T_PARK = AT('made'), AT('know')
T_CITY, T_TEXT, T_SCORE = AT('city'), AT('text'), AT('score')
T_THREE = AT('3')
LIFT0, COVER, LIFT1 = 8.6, 9.35, 10.05
PEN0, PEN1 = 18.0, 19.7
PULL0, PULL1 = 25.7, 26.75
LINE0 = 26.55
END0 = 29.0


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def F(w, s):
    names = {400: 'Nunito-400', 700: 'Nunito-700', 800: 'Nunito-800', 900: 'Nunito-900', 'hand': 'Caveat'}
    return ImageFont.truetype(f'{FON}/{names[w]}.ttf', int(s))


@functools.lru_cache(maxsize=256)
def text_spr(s, w, size, col):
    f = F(w, size)
    asc, desc = f.getmetrics()
    im = Image.new('L', (int(f.getlength(s) + 16), asc + desc + 16), 0)
    ImageDraw.Draw(im).text((8, 8), s, font=f, fill=255)
    a = np.asarray(im, np.float32) / 255
    ys, xs = np.where(a > 0.01)
    a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    return np.dstack([a[..., None] * np.array(col, np.float32), a])


def line_spr(parts, w, size):
    """One line made of differently coloured runs, spaced with the font's real word spacing."""
    f = F(w, size)
    asc, desc = f.getmetrics()
    full = ''.join(p for p, _ in parts)
    Wd = int(f.getlength(full) + 16)
    im = np.zeros((asc + desc + 16, Wd, 4), np.float32)
    x = 8
    for txt, col in parts:
        L = Image.new('L', (Wd, asc + desc + 16), 0)
        ImageDraw.Draw(L).text((x, 8), txt, font=f, fill=255)
        a = np.asarray(L, np.float32) / 255
        im[..., :3] += a[..., None] * np.array(col, np.float32)
        im[..., 3] += a
        x += f.getlength(txt)
    im[..., 3] = np.clip(im[..., 3], 0, 1)
    ys, xs = np.where(im[..., 3] > 0.01)
    return im[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]


def paste(c, spr, cx, cy, a=1.0):
    """Premultiplied RGBA sprite centred at (cx, cy) onto c (RGB or premultiplied RGBA)."""
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


def shadowed(spr, blur=10, off=(10, 14), amt=0.3):
    """Add a soft contact shadow cast away from the window (to the right/down)."""
    h, w = spr.shape[:2]
    p = blur * 3 + max(off)
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    sh = np.zeros((h + 2 * p, w + 2 * p), np.float32)
    sh[p + off[1]:p + off[1] + h, p + off[0]:p + off[0] + w] = spr[..., 3]
    sh = cv2.GaussianBlur(sh, (0, 0), blur) * amt
    out[..., 3] = sh
    reg = out[p:p + h, p:p + w]
    a = spr[..., 3:4]
    reg[..., :3] = spr[..., :3] + reg[..., :3] * (1 - a)
    reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)
    return out


@functools.lru_cache(maxsize=16)
def asset(name, width):
    im = cv2.imread(f'{A}/{name}.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3:4]
    ys, xs = np.where(a[..., 0] > 0.6)                          # crop to the object (keep its soft shadow margin)
    pad = 60
    im = im[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    sc = width / (xs.max() - xs.min())
    im = cv2.resize(im, (int(im.shape[1] * sc), int(im.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


# ------------------------------------------------------------------ world: the open book (book.png pixel space)
@functools.lru_cache(None)
def book():
    im = cv2.imread(f'{A}/book.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


LP = (815, 808)          # left page centre (household page)
RP = (1784, 808)         # right page centre (the new page)
PAGE_TOP, PAGE_BOT = 130, 1486


# ------------------------------------------------------------------ page content
@functools.lru_cache(None)
def star_spr(size, col=tuple(PLUM)):
    """Drawn four-point star (reference's star bullets)."""
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


@functools.lru_cache(None)
def photo_card(which, rot):
    if which == 'kitchen':
        cap = cv2.VideoCapture(f'{ROOT}/workspace_toast/clips/43033.mp4')
        cap.set(cv2.CAP_PROP_POS_MSEC, 3000)
        ok, f = cap.read()
        img = f[..., ::-1].astype(np.float32) / 255
        fx, fy = 0.5, 0.5
    else:
        img = cv2.imread(f'{ROOT}/workspace_frame/of/06-respite-outdoor-play.webp')[..., ::-1].astype(np.float32) / 255
        fx, fy = 0.5, 0.45
    pw, ph, b = 540, 400, 18
    ph_ = cover(img, fx, fy, 1.0, pw, ph)
    g = (ph_ * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    ph_ = ph_ * 0.55 + g * 0.45                                    # muted, gently warm
    card = np.ones((ph + 2 * b, pw + 2 * b, 3), np.float32) * np.array((0.985, 0.98, 0.97), np.float32)
    card[b:b + ph, b:b + pw] = ph_
    spr = np.dstack([card, np.ones(card.shape[:2], np.float32)])
    # a faint grid sheet behind it, tilted the other way
    gw, gh = pw + 2 * b + 70, ph + 2 * b + 70
    gs = np.ones((gh, gw, 3), np.float32) * np.array((0.96, 0.955, 0.945), np.float32)
    yy, xx = np.mgrid[0:gh, 0:gw]
    line = ((xx % 34) < 1.5) | ((yy % 34) < 1.5)
    gs[line] = gs[line] * 0.86
    gspr = xform(np.dstack([gs, np.ones((gh, gw), np.float32)]), 1.0, -rot * 1.6)
    out = shadowed(gspr, 8, (6, 8), 0.18)
    cs = shadowed(xform(spr, 1.0, rot), 12, (12, 16), 0.3)
    paste(out, cs, out.shape[1] / 2, out.shape[0] / 2)
    return out


@functools.lru_cache(None)
def label_spr(txt):
    t = text_spr(txt, 700, 40, tuple(CHAR))
    st = star_spr(26)
    w = st.shape[1] + 12 + t.shape[1]
    h = max(st.shape[0], t.shape[0])
    out = np.zeros((h, w, 4), np.float32)
    paste(out, st, st.shape[1] / 2, h / 2)
    paste(out, t, st.shape[1] + 12 + t.shape[1] / 2, h / 2)
    return out


def reveal_lr(spr, u):
    """Left-to-right wipe reveal with a soft edge."""
    if u >= 1:
        return spr
    w = spr.shape[1]
    edge = u * (w + 40)
    m = np.clip((edge - np.arange(w, dtype=np.float32)) / 40, 0, 1)
    return spr * m[None, :, None]


def land(spr, u):
    """Photo lands: 94% -> 103% -> 100% over eight frames."""
    if u <= 0:
        return None, 0
    d = 8 * FR
    k = clamp(u / d)
    s = 0.94 + 0.09 * math.sin(min(1, k / 0.6) * math.pi / 2) if k < 0.6 else 1.03 - 0.03 * smooth((k - 0.6) / 0.4)
    return xform(spr, s), clamp(u / (2 * FR))


@functools.lru_cache(None)
def bubble(txt, col, tail_left):
    t = text_spr(txt, 900, 58, tuple(col))
    bw_, bh = t.shape[1] + 70, t.shape[0] + 54
    S4 = 4
    m = np.zeros(((bh + 40) * S4, (bw_ + 10) * S4), np.uint8)
    cv2.rectangle(m, (bh // 2 * S4, 0), ((bw_ - bh // 2) * S4, bh * S4), 255, -1)
    for x in (bh // 2, bw_ - bh // 2):
        cv2.circle(m, (x * S4, bh // 2 * S4), bh // 2 * S4, 255, -1, cv2.LINE_AA)
    tx = int(bw_ * (0.28 if tail_left else 0.72))
    tail = [(tx - 22, bh - 4), (tx + 22, bh - 4), (tx + (-26 if tail_left else 26), bh + 36)]
    cv2.fillPoly(m, [(np.array(tail) * S4).astype(np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (bw_ + 10, bh + 40), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    paper = np.ones(m.shape + (3,), np.float32) * np.array((0.995, 0.99, 0.985), np.float32)
    spr = np.dstack([paper * m[..., None], m])
    paste(spr, t, bw_ / 2, bh / 2 + 2)
    return shadowed(spr, 9, (8, 12), 0.28)


@functools.lru_cache(None)
def stamp_spr():
    """Plum ink stamp: 3:00 in a rounded box, with ink grain."""
    t = text_spr('3:00', 900, 96, (1, 1, 1))
    w, h = t.shape[1] + 70, t.shape[0] + 50
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.rectangle(m, (12, 12), (w * 4 - 12, h * 4 - 12), 255, 24, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    a = np.zeros((h, w), np.float32)
    ta = t[..., 3]
    y0, x0 = (h - ta.shape[0]) // 2, (w - ta.shape[1]) // 2
    a[y0:y0 + ta.shape[0], x0:x0 + ta.shape[1]] = ta
    a = np.maximum(a, m)
    rng = np.random.default_rng(5)
    grain = cv2.GaussianBlur((rng.random((h, w)) > 0.22).astype(np.float32), (0, 0), 0.8)
    a = a * (0.55 + 0.45 * grain) * 0.88
    return xform(np.dstack([a[..., None] * PLUM, a]), 1.0, -8)


@functools.lru_cache(None)
def hand_text():
    return text_spr('Match day', 'hand', 150, tuple(CHAR))


# positions (world)
STAR_Y = 700
KIT = (LP[0] - 30, 455)
PARK = (LP[0] + 25, 950)
SCARF = (RP[0] + 10, 930)
GOAL = (RP[0] - 200, 610)
IKNOW = (RP[0] + 190, 700)
PHONE = (RP[0] + 300, 1360)
MATCH = (RP[0] - 40, 370)
STAMP = (RP[0] + 190, 1170)
STITCH = (RP[0] - 120, 905)


def world(t):
    c = book().copy()
    # 2 - the household: two photos land, labels reveal left to right
    for spr_name, rot, pos, t0, label in (('kitchen', -4.0, KIT, T_KITCHEN, 'Our kitchen'), ('park', 3.5, PARK, T_PARK, 'The park round the corner')):
        u0 = t - t0 + 0.28
        if u0 > 0:                                               # drops in from above with a little spin, then lands
            k = e_out(clamp(u0 / 0.28))
            sp, a = land(photo_card(spr_name, rot), t - t0)
            if sp is None:
                sp, a = xform(photo_card(spr_name, rot), 1.08, 9 * (1 - k) * (1 if rot < 0 else -1)), clamp(u0 / 0.1)
            paste(c, sp, pos[0] + 60 * (1 - k) * (1 if rot > 0 else -1), pos[1] - 260 * (1 - k), a)
            lu = (t - t0 - 0.2) / (8 * FR)
            if lu > 0:
                ls = label_spr(label)
                paste(c, reveal_lr(ls, lu), pos[0] - 250 + ls.shape[1] / 2, pos[1] + 268)
    # 1 - the tap and the drawn star (drawn over the photos so its flight into the bullet stays visible)
    if t >= T_TAP:
        u = t - T_TAP
        if u < 0.5:                                              # fingertip tap: a soft press ring
            r = 20 + 120 * e_out(u / 0.5)
            ring = np.zeros((300, 300), np.float32)
            cv2.circle(ring, (150, 150), int(r), 1.0, 3, cv2.LINE_AA)
            ring *= 0.35 * (1 - u / 0.5)
            paste(c, np.dstack([ring[..., None] * CHAR, ring]), LP[0], STAR_Y)
        d = 6 * FR
        s = 1.1 * smooth(u / (d * 0.6)) if u < d * 0.6 else 1.1 - 0.1 * smooth((u - d * 0.6) / (d * 0.4))
        fly = e_inout(prog(t, T_KITCHEN - 0.45, T_KITCHEN + 0.2))
        if fly < 1:
            bx, by = KIT[0] - 250 + 13, KIT[1] + 268                   # the label's star bullet
            x = LP[0] + (bx - LP[0]) * fly + 120 * math.sin(math.pi * fly)
            y = STAR_Y + (by - STAR_Y) * fly - 160 * math.sin(math.pi * fly)
            sz = s * (1 - fly) + (26 / 120) * fly
            if sz > 0.01:
                paste(c, xform(star_spr(120), sz, 8 * math.sin(t * 0.8) + 360 * e_inout(fly)), x, y)
    return c


def world_new_page(t, mono):
    """Right-page content that sits under the monochrome grade (bubbles/phone/text), drawn before the scarf."""
    c = book().copy() if False else None
    return c


@functools.lru_cache(None)
def _world_grid():
    h, w = book().shape[:2]
    return np.mgrid[0:h, 0:w].astype(np.float32)


DRAIN0, DRAIN_P = 10.05, (2300.0, 980.0)
FILL0 = PEN0 + 0.1


def mono_map(t):
    """Monochrome amount over the world: a wave drains the colour from the scarf's side, then colour flows back
    out from the pen tip as it starts writing."""
    if t < DRAIN0:
        return None
    full = 0.85
    yy, xx = _world_grid()
    if t < DRAIN0 + 1.0:
        R = 2600 * e_out(prog(t, DRAIN0, DRAIN0 + 1.0))
        m = np.clip((R - np.hypot(xx - DRAIN_P[0], yy - DRAIN_P[1])) / 260, 0, 1) * full
        return m[..., None]
    if t < FILL0:
        return full
    if t < FILL0 + 1.6:
        R = 2800 * e_inout(prog(t, FILL0, FILL0 + 1.6))
        m = (1 - np.clip((R - np.hypot(xx - (MATCH[0] - 330), yy - MATCH[1])) / 300, 0, 1)) * full
        return m[..., None]
    return None


def compose_world(t):
    c = world(t)
    # 3 - the new page (right): bubbles, phone, then the colour scarf on top of the monochrome grade
    if t >= T_TEXT - 0.1:
        u = t - (T_TEXT - 0.15)
        k = e_out(clamp(u / 0.4))
        ph = asset('phone', 150)
        buzz = 6 * math.sin(u * 70) * math.exp(-4 * max(0, u - 0.1)) if u > 0.1 else 0
        paste(c, shadowed(xform(ph, 1, -18 + buzz * 0.4), 8, (8, 10), 0.25), PHONE[0] + 260 * (1 - k) + buzz, PHONE[1])
        for j in range(2):                                         # one quiet buzz: two soft rings
            ur = u - 0.1 - j * 0.12
            if 0 < ur < 0.7:
                ring = np.zeros((420, 420), np.float32)
                cv2.circle(ring, (210, 210), int(60 + 150 * e_out(ur / 0.7)), 1.0, 4, cv2.LINE_AA)
                ring *= 0.45 * (1 - ur / 0.7)
                paste(c, np.dstack([ring[..., None] * PLUM, ring]), PHONE[0], PHONE[1])
        for txt, col, pos, dl, tl in (('GOAL!', PLUM, GOAL, 0.0, True), ('I KNOW!', CHAR, IKNOW, 6 * FR, False)):
            ub = t - T_TEXT - dl
            if ub > 0:
                s = e_back(clamp(ub / 0.3), 2.0)
                bob = 6 * math.sin((t + (0 if tl else 1.3)) * 2.2) * clamp((ub - 0.3) / 0.5)
                paste(c, xform(bubble(txt, tuple(col), tl), max(0.01, s), (-4 if tl else 4) + 1.5 * math.sin(t * 1.7 + dl * 9)),
                      pos[0], pos[1] + bob, clamp(ub / 0.08))
    if t >= PEN0:
        u = (t - PEN0) / (PEN1 - PEN0)
        ht = hand_text()
        paste(c, reveal_lr(ht, u), MATCH[0], MATCH[1])
    if t >= T_THREE:
        u = t - T_THREE
        s = 1.25 - 0.25 * e_out(clamp(u / (4 * FR)))
        paste(c, xform(stamp_spr(), s), STAMP[0], STAMP[1], clamp(u / (2 * FR)))
    mono = mono_map(t)
    if mono is not None:
        g = (c[..., :3] * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
        c[..., :3] = c[..., :3] * (1 - mono) + g * mono
    if t >= T_CITY - 0.35:
        u = t - (T_CITY - 0.35)
        k = e_out(clamp(u / 0.8))
        sc = asset('scarf', 940)
        paste(c, xform(sc, 1.0, -14 + 10 * (1 - k)), SCARF[0] + 900 * (1 - k), SCARF[1] + 40 * (1 - k))
    if PEN0 <= t < PEN1 + 0.7:                                    # the pen writes, its tip on the reveal edge
        u = clamp((t - PEN0) / (PEN1 - PEN0))
        ht = hand_text()
        tipx = MATCH[0] - ht.shape[1] / 2 + u * ht.shape[1]
        tipy = MATCH[1] + 20 + 14 * math.sin(u * 40)
        lift = smooth((t - PEN1) / 0.6)
        pen = xform(asset('pen', 440), 1.0, 32)
        # the pen's tip is its left end before rotation; after a -32 deg turn it sits lower-left of the sprite
        tx = -0.5 * 440 * math.cos(math.radians(32))
        ty = 0.5 * 440 * math.sin(math.radians(32))
        paste(c, shadowed(pen, 10, (14, 18), 0.25), tipx - tx + 160 * lift, tipy - ty - 220 * lift, 1 - lift)
    return c


# ------------------------------------------------------------------ camera (world -> screen)
def cam(t):
    """(centre x, centre y, zoom, rotation deg) in world px."""
    if t < COVER:
        z = 1.10 + 0.07 * prog(t, 0, COVER) + 0.1 * (1 - e_out(prog(t, 0, 1.2)))
        for tl in (T_KITCHEN, T_PARK):                                    # tiny bump as each photo lands
            if t > tl:
                z += 0.012 * math.exp(-9 * (t - tl)) * math.sin(22 * (t - tl))
        return LP[0], LP[1] + 30 - 30 * prog(t, 0, COVER), z, 0.4 - 0.8 * prog(t, 0, COVER)
    if t < PEN0:
        settle = 0.08 * (1 - e_out(prog(t, COVER, LIFT1 + 0.6)))          # the new page settles after the peel
        z = 1.08 + 0.06 * prog(t, COVER, PEN0) + settle
        z += 0.035 * math.exp(-5 * max(0, t - T_TEXT)) * math.sin(14 * max(0, t - T_TEXT)) if t > T_TEXT else 0
        gl = e_inout(prog(t, 14.6, PEN0))                                  # glide along the scarf
        return RP[0] - 50 + 110 * gl, RP[1] + 40 - 50 * prog(t, COVER, PEN0), z, -0.3 + 0.6 * prog(t, COVER, PEN0) + 1.2 * math.sin(math.pi * gl)
    if t < PULL0:
        k = e_inout(prog(t, PEN1 + 0.3, T_THREE - 0.2))
        cx = RP[0] - 40 + 60 * k
        cy = MATCH[1] + 260 + (RP[1] + 60 - MATCH[1] - 260) * k
        z = 1.45 - 0.33 * k
        # the carer draws the book closer: a small slide + turn
        dk = e_inout(prog(t, 18.9, 20.1))
        return cx, cy + 50 * dk, z + 0.03 * prog(t, T_THREE, PULL0), -1.6 * dk
    k = e_inout(prog(t, PULL0, PULL1))
    cx0, cy0, z0, r0 = cam(PULL0 - 1e-3)
    return cx0 + (1300 - cx0) * k, cy0 + (830 - cy0) * k, z0 + (0.52 - z0) * k + 0.015 * prog(t, PULL1, END0), r0 * (1 - k)


def cam_M(t):
    cx, cy, z, r = cam(t)
    if T_THREE < t < T_THREE + 0.3:                                       # the stamp's soft desk tap
        a = 9 * (1 - (t - T_THREE) / 0.3)
        cx += a * math.sin(t * 90)
        cy += a * math.cos(t * 70)
    M = cv2.getRotationMatrix2D((cx, cy), r, z)
    M[0, 2] += W / 2 - cx
    M[1, 2] += H / 2 - cy
    return M


@functools.lru_cache(None)
def _screen_grid():
    return np.mgrid[0:H, 0:W].astype(np.float32)


def table(M):
    """Ivory base with a low-opacity grid that lives in world space (moves with the camera) + soft vignette."""
    yy, xx = _screen_grid()
    Mi = cv2.invertAffineTransform(M)
    wx = Mi[0, 0] * xx + Mi[0, 1] * yy + Mi[0, 2]
    wy = Mi[1, 0] * xx + Mi[1, 1] * yy + Mi[1, 2]
    z = math.hypot(M[0, 0], M[0, 1])
    lw = 1.3 / z
    gx = np.abs(((wx + 32) % 64) - 32) < lw
    gy = np.abs(((wy + 32) % 64) - 32) < lw
    c = np.empty((H, W, 3), np.float32)
    c[:] = IVORY * 0.985
    c[gx | gy] *= 0.93
    r = np.hypot((xx - W / 2) / W, (yy - H / 2) / H)
    return c * (1.02 - 0.2 * r[..., None] ** 2)


# ------------------------------------------------------------------ screen overlays
def page_lift(c, t):
    """The right page corner lifts towards camera until the paper fills the screen; cut under cover."""
    if not (LIFT0 <= t < LIFT1):
        return c
    if t < COVER:
        k = e_inout(prog(t, LIFT0, COVER)) ** 1.3
        P1 = np.array((W - 40 - 3200 * k, H + 20))
        P2 = np.array((W + 20, H - 40 - 4200 * k))
        tip = np.array((W - 140 - 2100 * k, H - 160 - 2900 * k))
        off = np.zeros(2)
    else:
        k = 1.0
        u = e_inout(prog(t, COVER, LIFT1))
        P1, P2, tip = np.array((W - 3240.0, H + 20)), np.array((W + 20.0, H - 4240)), np.array((W - 2240.0, H - 3060))
        off = np.array((-1500 * u, -2600 * u))
    C = np.array((W + 40.0, H + 40.0))
    poly = np.array([P1 + off, tip + off, P2 + off, C + off])
    m = np.zeros((H * 2, W * 2), np.uint8)
    cv2.fillPoly(m, [(poly * 2).astype(np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    sh = cv2.GaussianBlur(np.roll(np.roll(m, 30, 0), -20, 1), (0, 0), 30) * 0.35
    c = c * (1 - sh[..., None])
    yy, xx = _screen_grid()
    n = (P2 - P1)
    n = np.array((-n[1], n[0])) / (np.linalg.norm(n) + 1e-6)
    d = ((xx - (P1 + off)[0]) * n[0] + (yy - (P1 + off)[1]) * n[1]) / 900
    shade = 0.9 + 0.1 * np.clip(np.abs(d), 0, 1)                   # darker near the fold, lighter towards the lifted corner
    paper = IVORY[None, None] * shade[..., None]
    return c * (1 - m[..., None]) + paper * m[..., None]


def overlay_text(c, spr, x, y, a=1.0, anchor='c'):
    if anchor == 'l':
        x = x + spr.shape[1] / 2
    return paste(c, spr, x, y, a)


def title(c, t):
    """Reference-style stacked type, each word rising out of a soft blur in turn (scene 1)."""
    out = clamp((t - 3.5) / 0.45)
    if t < 0.2 or out >= 1:
        return
    items = [('Can I', 400, 52, GREY, W / 2, 378, 0.25)]
    f = F(800, 110)
    full = 'add a page?'
    x0 = W / 2 - f.getlength(full) / 2
    for i, (wd, col) in enumerate((('add', CHAR), ('a', CHAR), ('page?', PLUM))):
        pre = ' '.join(['add', 'a', 'page?'][:i]) + (' ' if i else '')
        items.append((wd, 800, 110, col, x0 + f.getlength(pre) + f.getlength(wd) / 2, 470, 0.45 + 0.14 * i))
    for wd, wt, sz, col, x, y, d0 in items:
        u = clamp((t - d0) / 0.45)
        if u <= 0:
            continue
        k = e_out(u)
        spr = text_spr(wd, wt, sz, tuple(col))
        if u < 1:
            spr = cv2.GaussianBlur(spr, (0, 0), 0.1 + 6 * (1 - k))
        paste(c, spr, x, y + 40 * (1 - k) - 30 * e_inout(out), k * (1 - out))


def wrap2(txt, maxw, f):
    words = txt.split()
    best = [txt]
    if f.getlength(txt) > maxw:
        cut = min(range(1, len(words)), key=lambda i: abs(f.getlength(' '.join(words[:i])) - f.getlength(' '.join(words[i:]))))
        best = [' '.join(words[:cut]), ' '.join(words[cut:])]
    return best


def line_words(lid, t0, t1, txt):
    toks = txt.split()
    ws = [w for w in WORDS if t0 - 0.4 <= w[1] <= t1 + 0.2]
    n, m = len(toks), len(ws)
    out = []
    for i, tk in enumerate(toks):
        j = i if n == m else int(round(i * (m - 1) / max(1, n - 1)))
        out.append((tk, ws[j][1], ws[j][2]))
    return out


def subtitles(c, t):
    """Every spoken line verbatim, lower middle, up to two lines, charcoal on ivory (Nunito regular); each word
    fades up as it is said and the word being said is plum."""
    if t >= PULL0:
        return
    f = F(400, 46)
    sp = f.getlength(' ')
    for lid, spk, t0, t1, txt in LINES:
        if t0 - 0.05 <= t < t1 + 0.35:
            u = t - (t0 - 0.05)
            a = clamp(u / 0.15) * (1 - clamp((t - t1 - 0.2) / 0.15))
            ls = wrap2(txt, 820, f)
            words = line_words(lid, t0, t1, txt)
            rows, k = [], 0
            for l in ls:
                n = len(l.split())
                rows.append(words[k:k + n])
                k += n
            wmax = max(f.getlength(l) for l in ls)
            lh = 60
            pw, ph = int(wmax + 64), int(lh * len(rows) + 30)
            y = 1610 + 10 * (1 - e_out(clamp(u / 0.3)))
            pill = np.ones((ph, pw), np.float32)
            paste(c, np.dstack([pill[..., None] * IVORY, pill * 0.93]), W / 2, y, a)
            yy = y - ph / 2 + 15 + lh / 2
            for row in rows:
                rw = sum(f.getlength(w[0]) for w in row) + sp * (len(row) - 1)
                x = W / 2 - rw / 2
                for tk, ws, we in row:
                    wa = clamp((t - ws + 0.05) / 0.12)
                    col = PLUM if ws - 0.02 <= t < we + 0.08 else CHAR
                    spr = text_spr(tk, 400, 46, tuple(col))
                    paste(c, spr, x + f.getlength(tk) / 2, yy + 6 * (1 - wa), a * (0.25 + 0.75 * wa))
                    x += f.getlength(tk) + sp
                yy += lh
            mark = star_spr(22) if spk == 'yp' else star_spr(22, tuple(CHAR))
            paste(c, mark, W / 2 - pw / 2 + 2, y - ph / 2 + 2, a)


def line_up(c, t, M):
    """'Room to grow, roots to keep.' rises from behind the book's top edge over eight frames."""
    if t < LINE0 or t >= END0 + 0.4:
        return
    u = e_out(clamp((t - LINE0) / (8 * FR)))
    edge = (M @ np.array((1300, 80, 1)))[1]                     # screen y of the book's top edge
    s1 = text_spr('Room to grow,', 800, 84, tuple(CHAR))
    s2 = text_spr('roots to keep.', 800, 84, tuple(PLUM))
    lay = np.zeros((H, W, 3), np.float32)
    la = np.zeros((H, W, 1), np.float32)
    y2 = edge - 70 + 150 * (1 - u)
    for s, y in ((s1, y2 - 100), (s2, y2)):
        tmp = np.dstack([lay, la])
        paste(tmp, s, W / 2, y)
        lay, la = tmp[..., :3], tmp[..., 3:]
    la[int(max(0, edge - 6)):] = 0                                   # hidden behind the page edge
    c[:] = c * (1 - la) + lay
    star = star_spr(36)
    paste(c, star, W / 2 - s1.shape[1] / 2 - 40, y2 - 100, u * (edge - (y2 - 100) > 30))


@functools.lru_cache(None)
def end_card():
    c = np.empty((H, W, 3), np.float32)
    c[:] = IVORY
    yy, xx = _screen_grid()
    g = (np.abs(((xx + 32) % 64) - 32) < 1.0) | (np.abs(((yy + 32) % 64) - 32) < 1.0)
    c[g] *= 0.95
    logo = cv2.imread(f'{ROOT}/workspace_three/web/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    LW = 600
    logo = cv2.resize(logo, (LW, int(logo.shape[0] * LW / logo.shape[1])), interpolation=cv2.INTER_AREA)
    paste(c, np.dstack([logo[..., 2::-1] * logo[..., 3:4], logo[..., 3]]), W / 2, 720)
    l1 = text_spr('Thinking about fostering', 800, 70, tuple(CHAR))
    l2 = line_spr((('in ', tuple(CHAR)), ('Greater Manchester?', tuple(PLUM))), 800, 70)
    paste(c, l1, W / 2, 1010)
    paste(c, l2, W / 2, 1105)
    st = star_spr(30)
    l3 = text_spr('Start your enquiry  ·  Link in bio', 400, 46, tuple(CHAR))
    paste(c, l3, W / 2 + 20, 1235)
    paste(c, st, W / 2 - l3.shape[1] / 2 - 14, 1235)
    return c


def frame(t):
    M = cam_M(t)
    if t >= END0 + 8 * FR:
        c = end_card().copy()
    else:
        c = table(M)
        wd = compose_world(t)
        warped = cv2.warpAffine(wd, M, (W, H), flags=cv2.INTER_LINEAR)
        c = c * (1 - warped[..., 3:4]) + warped[..., :3]
        c = page_lift(c, t)
        if t < 0.6:                                                 # opens on a soft defocus (reference)
            b = 14 * (1 - e_out(t / 0.6))
            if b > 0.3:
                c = cv2.GaussianBlur(c, (0, 0), b)
        if PEN0 - 2 * FR <= t < PEN0 + 5 * FR:                       # cut on the pen: a zoom-blur punch
            amt = 1 - abs(t - PEN0) / (5 * FR)
            acc = c.copy()
            for i in range(1, 5):
                z = 1 + 0.018 * i * amt
                M2 = cv2.getRotationMatrix2D((W / 2, H * 0.4), 0, z)
                acc += cv2.warpAffine(c, M2, (W, H), borderMode=cv2.BORDER_REFLECT)
            c = acc / 5
        if 22.3 <= t < 25.2:                                           # a warm light sweep across the page
            u = (t - 22.3) / 2.9
            yy, xx = _screen_grid()
            d = (xx * 0.6 + yy * 0.8) - (-600 + 3200 * u)
            g = np.exp(-(d / 260) ** 2) * 0.12 * math.sin(math.pi * u)
            c = c + g[..., None] * np.array((1.0, 0.8, 0.55), np.float32)
        title(c, t)
        subtitles(c, t)
        line_up(c, t, M)
        if t >= END0:                                               # ivory circle from the scarf stitch
            p = M @ np.array((STITCH[0], STITCH[1], 1))
            r = 2400 * e_inout(clamp((t - END0) / (8 * FR)))
            yy, xx = _screen_grid()
            dist = np.hypot(xx - p[0], yy - p[1])
            m = np.clip((r - dist) / 3, 0, 1)[..., None]
            edge = np.exp(-((dist - r) / 10) ** 2)[..., None] * 0.6 * (r < 2300)
            c = c * (1 - m) + end_card() * m
            c = c * (1 - edge) + PLUM * edge
    if t < END0 + 8 * FR:
        lab = text_spr('Dramatisation', 400, 32, tuple(CHAR * 0.8))
        paste(c, lab, 56 + lab.shape[1] / 2, 92, 0.9)
    rng = np.random.default_rng(int(t * FPS))
    c = np.clip(c + rng.normal(0, 0.008, (H, W, 1)).astype(np.float32), 0, 1)
    return c


def frame_mb(t):
    """Motion blur through the fast moves (page lift, pull back, scarf slide, star flight)."""
    fast = (LIFT0 <= t < LIFT1) or (PULL0 <= t < PULL1) or (T_CITY - 0.4 <= t < T_CITY + 0.5) or (T_KITCHEN - 0.45 <= t < T_KITCHEN + 0.2) \
        or (END0 <= t < END0 + 8 * FR)
    if not fast:
        return frame(t)
    return (frame(t - FR / 4) + frame(t + FR / 4)) / 2


def write(path, c):
    cv2.imwrite(path, (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        d = f'{S}/stills'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            write(f'{d}/{int(float(ts) * 100):05d}.png', frame(float(ts)))
            print('still', ts, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            write(f'{d}/{i:05d}.png', frame_mb(i / FPS))
            if i % 25 == 0:
                print('frame', i, flush=True)
