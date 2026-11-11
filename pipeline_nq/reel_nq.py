"""Organic Fostering "No Qualification Needed" (9:16, ~32 s). 3D studio version: no paper.

Story: dusk, people walk home through town; a woman writes in her notebook (real footage) -> her card flips away into a
stern, cold 3D studio: ENTRY REQUIREMENTS, a degree cap, a certificate and books turning on spot-lit pedestals, each
tagged REQUIRED. "...with us." A 3D NO QUALIFICATION NEEDED stamp slams down: shockwave, the requirements are blasted
away, the studio floods with brand colour, confetti. "What you'll learn before approval" -> a giant spinning 3D seven
-> a 3D CAROUSEL of seven glowing platforms that turns to each topic on its word (spinning 3D object, 3D numeral,
floating photo card of real people). "And it doesn't stop" -> laptop, workshop easel and chat bubbles orbit up a spiral
of light. "Ask us about training" -> zoom through a gold ring into the end card.

Every 3D object is a 24-angle turntable render (blender_spin.py), so they really turn.

Usage: python3 reel_nq.py still 1.0,5.0 | python3 reel_nq.py range 0 100 | python3 reel_nq.py times
"""
import os, sys, math, json, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_three'))
import numpy as np
import cv2
import frames_three as F3
from frames_three import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, PURPLE, ORANGE,
                          PLUM, IVORY, LAV, PEACH, LEAF, WHITE, N9, N8, N7, cover, grade)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post, draw3d

FPS = 30
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_nq'
F3.S = f'{ROOT}/workspace_three'
DUR = 37.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y
HAND = 'Caveat-700'
GOLD = (1.0, 0.82, 0.45, 1)
COLD = (0.62, 0.72, 0.9, 1)

TOPICS = [  # title, 3D object, photo (clip, t) or None
    ('Why children enter care', 'umbrella', ('4661', 4.0)),
    ('The role of a foster carer', 'house', ('4950', 4.0)),
    ('Safeguarding & professional boundaries', 'shield', None),
    ('Identity, culture, equality & inclusion', 'network', ('4809', 3.0)),
    ('Working with birth families', 'tree', None),
    ('How trauma can influence behaviour', 'heartplaster', None),
    ('Recording, confidentiality & teamwork', 'padlock', ('4807', 6.0)),
]

# ------------------------------------------------------------------ timing (from the voice when it exists)
INFO = f'{S}/tts/info.json'
if os.path.exists(INFO):
    _info = json.load(open(INFO))
    K = _info['keys']
    WORDS = [tuple(w) for w in _info['words']]
else:                                                        # placeholder timeline for the scene stills
    K = dict(before=0.7, study=2.6, withus=5.0, noqual=5.8, needed=6.8, learn=7.6, approval=8.8,
             items=[10.0 + 2.0 * i for i in range(7)], stop=24.0, learning=25.3, throughout=26.6, ask=28.4, training=29.2, end=29.9)
    WORDS = []
ITEMS = K['items']


# ------------------------------------------------------------------ 3D sprites
@functools.lru_cache(maxsize=None)
def _spin_frames(name):
    fs = sorted(glob.glob(f'{S}/spin/{name}/*.png'))
    return fs


@functools.lru_cache(maxsize=600)
def _spin_load(path):
    sp = load_png_sprite(path)
    return sp


@functools.lru_cache(maxsize=None)
def _spin_crop(name):
    """One crop box for every angle of an object (so it does not jitter as it turns)."""
    fs = _spin_frames(name)
    acc = None
    for f in fs[::3]:
        a = _spin_load(f)[..., 3] > 0.01
        acc = a if acc is None else (acc | a)
    ys, xs = np.where(acc)
    return max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5


@functools.lru_cache(maxsize=None)
def _static(name):
    if name.startswith('n') and name[1:].isdigit():
        return ts(name[1:], N9, 300, ORANGE)
    p = f'{S}/assets/{name}.png'
    if not os.path.exists(p):
        p = f'{ROOT}/workspace_three/assets/{name}.png'
    sp = load_png_sprite(p)
    ys, xs = np.where(sp[..., 3] > 0.01)
    return np.ascontiguousarray(sp[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def spin(name, ang):
    fs = _spin_frames(name)
    if not fs:
        return _static(name)
    n = len(fs)
    i = int(round((ang % 360) / 360 * n)) % n
    y0, y1, x0, x1 = _spin_crop(name)
    return _spin_load(fs[i])[y0:y1, x0:x1]


FLAT = {'shield', 'heartplaster', 'phone', 'workshop', 'nostamp'}


def obj3d(c, name, x, y, size, ang=0.0, k=1.0, reflect=True, glow=None, floor_y=None, opacity=1.0, blur=0):
    """A turning 3D object: pops in with a fast spin, keeps slowly turning; soft floor shadow and a faint reflection."""
    if k <= 0:
        return
    e = e_out_back(min(1, k), 1.8)
    if name in FLAT or name.startswith('n'):                     # flat things sway instead of turning edge-on
        ang = 38 * math.sin(math.radians(ang))
    a = ang + (1 - min(1, e_out_cubic(k))) * 300
    sp = spin(name, a)
    if blur:
        sp = blur_sprite(sp, blur)
    sc = size / max(sp.shape[:2]) * e
    hh = sp.shape[0] * sc
    if glow:
        gl = blur_sprite(tint(sp, glow[:3]), 30)
        draw(c, gl, x, y, scale=sc * 1.15, opacity=0.55 * opacity * min(1, k))
    fy = floor_y if floor_y is not None else y + hh / 2 + 10
    sh = rrect(max(4, int(sp.shape[1] * sc * 0.8)), max(4, int(sp.shape[1] * sc * 0.16)), int(sp.shape[1] * sc * 0.08) + 1, (0, 0, 0, 0.55))
    draw(c, blur_sprite(sh, 14), x, fy, opacity=0.6 * opacity * min(1, k))
    if reflect:
        ref = sp[::-1].copy()
        fade = np.linspace(0.35, 0, ref.shape[0], dtype=np.float32)[:, None, None]
        draw(c, ref * fade, x, fy + hh / 2 + 6, scale=sc, opacity=opacity * min(1, k))
    draw(c, sp, x, y, scale=sc, opacity=opacity * min(1, k * 2))


# ------------------------------------------------------------------ studio world
def _grad(top, bot):
    k = (_Y / H)[..., None]
    return np.array(top[:3], np.float32) * (1 - k) + np.array(bot[:3], np.float32) * k


@functools.lru_cache(maxsize=4)
def STUDIO(mood):
    if mood == 'stern':
        c = _grad(R.hexc('#10141E'), R.hexc('#262C3A'))
        spot = (0.55, 0.62, 0.8)
    else:
        c = _grad(R.hexc('#2A0826'), R.hexc('#6E1A5E'))
        spot = (1.0, 0.55, 0.75)
    # floor: a lit stage that falls off towards the horizon
    fl = np.clip((_Y - 1180) / 700, 0, 1)[..., None]
    c = c * (1 - 0.35 * fl) + np.array(spot, np.float32) * 0.18 * fl * np.exp(-((_X - 540) / 620) ** 2)[..., None]
    hz = np.exp(-((_Y - 1180) / 26) ** 2)[..., None] * 0.18
    c = c + hz * np.array(spot, np.float32)
    g = np.exp(-(((_X - 540) / 520) ** 2 + ((_Y - 720) / 820) ** 2))[..., None]
    c = c + g * np.array(spot, np.float32) * 0.18
    return np.clip(c, 0, 1).astype(np.float32)


_RNG = np.random.default_rng(12)
BOKEH = [(_RNG.uniform(0, W), _RNG.uniform(0, H), _RNG.uniform(10, 46), _RNG.uniform(-14, 14), _RNG.uniform(-30, -8), _RNG.uniform(0.04, 0.16))
         for _ in range(36)]


@functools.lru_cache(maxsize=8)
def _dot(r):
    d = np.zeros((int(r * 2 + 4), int(r * 2 + 4)), np.float32)
    cv2.circle(d, (int(r + 2), int(r + 2)), int(r), 1.0, -1, cv2.LINE_AA)
    d = cv2.GaussianBlur(d, (0, 0), r * 0.25 + 1)
    return d


def bokeh(c, t, col=(1, 0.8, 0.9), amt=1.0):
    for x, y, r, vx, vy, a in BOKEH:
        xx = (x + vx * t) % W
        yy = (y + vy * t) % H
        d = _dot(int(r))
        draw(c, solid(d, col + (1,)), xx, yy, opacity=a * amt)


def studio(t, mood='warm', amt=1.0):
    c = STUDIO(mood).copy()
    bokeh(c, t, (0.75, 0.82, 1.0) if mood == 'stern' else (1.0, 0.75, 0.85), amt)
    return c


def beams(c, t, x, col=COLD, amt=1.0, w=180):
    """Spotlight cone from above onto a pedestal."""
    top_w, bot_w = 40, w
    yy = np.clip(_Y / 1300, 0, 1)
    half = top_w + (bot_w - top_w) * yy
    m = np.clip(1 - np.abs(_X - x) / half, 0, 1) ** 1.5 * (_Y < 1320) * (0.85 + 0.15 * math.sin(t * 2 + x))
    c[:] = np.clip(c + (m * 0.22 * amt)[..., None] * np.array(col[:3], np.float32), 0, 1)


def pedestal(c, x, y, w, col=(0.3, 0.33, 0.42), rim=COLD, k=1.0):
    """A round glossy plinth: top ellipse, side band, rim light."""
    if k <= 0:
        return
    w = int(w * e_out_cubic(min(1, k)))
    if w < 8:
        return
    h = int(w * 0.24)
    lay = np.zeros((h * 2 + 80, w + 40, 4), np.float32)
    cx, cy = (w + 40) // 2, h // 2 + 20
    side = np.zeros(lay.shape[:2], np.uint8)
    cv2.ellipse(side, (cx, cy + 50), (w // 2, h // 2), 0, 0, 180, 255, -1, cv2.LINE_AA)
    cv2.rectangle(side, (cx - w // 2, cy), (cx + w // 2, cy + 50), 255, -1)
    sm = side.astype(np.float32)[..., None] / 255
    shade = np.linspace(0.75, 0.45, lay.shape[0], dtype=np.float32)[:, None, None]
    lay[..., :3] += sm * np.array(col, np.float32) * shade
    lay[..., 3:] = np.maximum(lay[..., 3:], sm)
    top = np.zeros(lay.shape[:2], np.uint8)
    cv2.ellipse(top, (cx, cy), (w // 2, h // 2), 0, 0, 360, 255, -1, cv2.LINE_AA)
    tm = top.astype(np.float32)[..., None] / 255
    lay[..., :3] = lay[..., :3] * (1 - tm) + tm * np.array(col, np.float32) * 1.35
    lay[..., 3:] = np.maximum(lay[..., 3:], tm)
    rr = np.zeros(lay.shape[:2], np.uint8)
    cv2.ellipse(rr, (cx, cy), (w // 2, h // 2), 0, 180, 360, 255, 3, cv2.LINE_AA)
    rm = rr.astype(np.float32)[..., None] / 255
    lay[..., :3] = lay[..., :3] * (1 - rm) + rm * np.array(rim[:3], np.float32)
    draw(c, blur_sprite(tint(lay, (0, 0, 0)), 16), x, y + 30, opacity=0.5)
    draw(c, lay, x, y + lay.shape[0] / 2 - cy)


def title3d(c, text, x, y, size, face=WHITE, side=(0.35, 0.05, 0.3, 1), depth=10, k=1.0, font=N9, rot=0):
    """Extruded 3D title: stacked offset copies for the side, bright face on top."""
    if k <= 0:
        return
    m = _wmask(text, font, size)
    e = e_out_back(min(1, k), 1.6)
    sd = solid(m, side)
    for d in range(depth, 0, -1):
        draw(c, sd, x + d * 0.6, y + d, scale=e, rot=rot, opacity=min(1, k * 2))
    draw(c, blur_sprite(solid(m, (0, 0, 0, 1)), 14), x + depth, y + depth + 10, scale=e, rot=rot, opacity=0.45 * min(1, k * 2))
    draw(c, solid(m, face), x, y, scale=e, rot=rot, opacity=min(1, k * 2))


def tag(c, text, x, y, col=(0.85, 0.2, 0.25, 1), k=1.0, rot=-4):
    if k <= 0:
        return
    s = ts(text, N9, 30, WHITE, 0.1)
    p = rrect(s.shape[1] + 40, 54, 12, col).copy()
    paste_spr(p, s, p.shape[1] / 2, 27)
    draw(c, p, x, y, rot=rot, scale=e_out_back(min(1, k), 2.0), opacity=min(1, k * 2))


def photo_card(img, w=420, h=300, border=16):
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, 18, 2)), (w, h))
    card = np.ones((h + 2 * border, w + 2 * border, 4), np.float32)
    bm = cv2.resize(R.sdf_fill(R.rrect_alpha(w + 2 * border, h + 2 * border, 26, 2)), (w + 2 * border, h + 2 * border))
    card[..., :3] = bm[..., None]
    card[..., 3] = bm
    card[border:border + h, border:border + w, :3] = img * m[..., None] + card[border:border + h, border:border + w, :3] * (1 - m[..., None])
    return card


def shockwave(c, x, y, k, col=ORANGE):
    if not 0 < k < 1:
        return
    r = 40 + e_out_cubic(k) * 1300
    d = np.hypot(_X - x, _Y - y)
    ring = np.exp(-((d - r) / (28 + 60 * k)) ** 2) * (1 - k)
    c[:] = np.clip(c + ring[..., None] * (0.6 * np.array(col[:3], np.float32) + 0.4), 0, 1)


CONF = [(_RNG.uniform(-1, 1), _RNG.uniform(-1.2, -0.3), _RNG.uniform(0, 360), _RNG.uniform(-720, 720),
         [ORANGE, PURPLE, (1, 0.85, 0.3, 1), LEAF, WHITE][i % 5], _RNG.uniform(14, 26)) for i in range(70)]


def confetti(c, t, t0, x=540, y=900):
    d = t - t0
    if d <= 0 or d > 3.0:
        return
    for vx, vy, a0, va, col, sz in CONF:
        px = x + vx * 900 * d
        py = y + vy * 1500 * d + 900 * d * d
        if not (-50 < px < W + 50 and -50 < py < H + 50):
            continue
        rect = rrect(sz, sz * 0.5, 2, col)
        draw(c, rect, px, py, rot=a0 + va * d, opacity=max(0, 1 - d / 3.0))


def light_sweep(c, k, y0=0, y1=H, amt=0.3):
    if not 0 < k < 1:
        return
    pos = lerp(-400, W + 400, k)
    band = np.exp(-(((_X - pos) + (_Y - H / 2) * 0.35) / 70) ** 2)
    c[:] = np.clip(c + band[..., None] * amt, 0, 1)


def stamp(c, k, x=540, y=900, rot=-8):
    """3D NO QUALIFICATION NEEDED stamp: drops from above the lens, slams, settles with a bounce."""
    if k <= 0:
        return
    s1 = ts('NO QUALIFICATION', N9, 84, WHITE, 0.01)
    s2 = ts('NEEDED', N9, 124, WHITE, 0.02)
    w = max(s1.shape[1], s2.shape[1]) + 90
    face = F3.grad_spr(w, 300, 44, ORANGE, (1.0, 0.45, 0.1, 1))
    face = face.copy()
    paste_spr(face, s1, w / 2, 95)
    paste_spr(face, s2, w / 2, 205)
    sidec = rrect(w, 300, 44, (0.6, 0.18, 0.02, 1))
    e = e_out_cubic(min(1, k / 0.35))
    sc = lerp(3.2, 1.0, e)
    bounce = 1 + 0.06 * math.sin(max(0, k - 0.35) * 18) * math.exp(-max(0, k - 0.35) * 6)
    op = min(1, k * 4)
    draw(c, blur_sprite(tint(sidec, (0, 0, 0)), 26), x + 20, y + 40, rot=rot, scale=sc * bounce, opacity=0.55 * op)
    for d in range(14, 0, -2):
        draw(c, sidec, x + d * 0.5, y + d, rot=rot, scale=sc * bounce, opacity=op)
    draw(c, face, x, y, rot=rot, scale=sc * bounce, opacity=op)


# ------------------------------------------------------------------ footage
class Clip:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pos = -1
        self.cache = {}

    def frame(self, t):
        i = int(clamp(t * self.fps, 0, self.n - 1))
        if i in self.cache:
            return self.cache[i]
        if i != self.pos + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, im = self.cap.read()
        if not ok:
            return self.cache[max(self.cache)] if self.cache else np.zeros((720, 1280, 3), np.uint8)
        self.pos = i
        if len(self.cache) > 20:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def footage(cid, ct, kind='realist', fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    if cid not in _clips:
        for d in ('workspace_nq', 'workspace_three2', 'workspace_three', 'workspace_tuned'):
            p = f'{ROOT}/{d}/clips/{cid}.mp4'
            if os.path.exists(p):
                _clips[cid] = Clip(p)
                break
    cl = _clips[cid]
    ct = ct % max(0.5, cl.n / cl.fps - 0.1)
    im = cl.frame(ct).astype(np.float32)[..., ::-1] / 255
    return grade(cover(im, fx, fy, z, w, h), kind)


@functools.lru_cache(maxsize=16)
def photo_still(cid, t, w, h):
    return photo_card(footage(cid, t, 'realist', 0.5, 0.45, 1.0, w, h), w, h)


# ------------------------------------------------------------------ captions (voice = captions; cue words highlighted)
PHRASES = [  # (text, start key, end key, highlight words, colour)
    ("Before you can foster,", 'before', 'study', (), ORANGE),
    ("Before you can foster, | you'll need to study…", 'study', 'withus', ('study',), (0.55, 0.62, 0.8, 1)),
    ("…with us.", 'withus', 'noqual', ('us',), ORANGE),
    ("No qualification needed.", 'noqual', 'learn', ('no', 'qualification', 'needed'), ORANGE),
    ("What you'll learn | before approval:", 'learn', 0, ('learn',), PURPLE),
] + [(f"{i + 1}. {TOPICS[i][0]}", i, i + 1, (), PURPLE) for i in range(7)] + [
    ("And it doesn't stop: learning | continues throughout fostering.", 'stop', 'ask', ('learning', 'continues'), ORANGE),
    ("Ask us about training.", 'ask', 'END', ('training',), ORANGE),
]


def kt(key):
    if key == 'END':
        return DUR
    if isinstance(key, int):
        return ITEMS[key] if key < 7 else K['stop']
    return K[key]


def captions(c, t, y=1610, size=60):
    for text, a, b, keys, hl in PHRASES:
        t0, t1 = kt(a) - 0.08, kt(b) - 0.1
        if not (t0 <= t < t1):
            continue
        lines = [l.strip() for l in text.split('|')]
        k = prog(t, t0, t0 + 0.25)
        sz = size
        while sz > 40:
            wmax = max(sum(_wmask(w, N9, sz).shape[1] for w in l.split()) + sz * 0.24 * (len(l.split()) - 1) for l in lines)
            if wmax <= W - 140:
                break
            sz -= 2
        tmp = c.copy()
        F3.caption(tmp, lines, keys=keys, y=y, size=sz, hl=hl)
        e = e_out_cubic(k)
        dy = (1 - e) * 30
        if dy > 0.5:
            tmp = cv2.warpAffine(tmp, np.float32([[1, 0, 0], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
        band = (np.abs(_Y - (y + 40)) < 160).astype(np.float32)[..., None] * min(1, k * 2)
        c[:] = c * (1 - band) + tmp * band


# ------------------------------------------------------------------ shots
def sh_walk(t):
    c = footage('3428', 8.0 + t, 'optimist', 0.5, 0.55, 1.05 + 0.02 * t)
    c = F3.top_shade(c)
    c = F3.shade(c, 0.7, 0.7)
    obj3d(c, 'gradcap', 780, 820, 260, ang=t * 60, k=prog(t, K['before'] + 0.5, K['before'] + 0.95), reflect=False, glow=GOLD)
    return c


def sh_write(t):
    """The writer's footage on a floating 3D card in the cold studio; books and certificate orbit her."""
    t0 = SH['write'][0]
    c = studio(t, 'stern')
    d = t - t0
    ry = -14 + 6 * math.sin(d * 0.8)
    card = photo_still('4953', 4.0 + round(d * 6) / 6 % 5, 560, 820)
    draw3d(c, card, 520, 860, 0, w=600, h=600 * card.shape[0] / card.shape[1], ry=ry, rx=4)
    for j, (nm, ph) in enumerate((('books', 0), ('certificate', 2.1), ('gradcap', 4.2))):
        a = d * 1.4 + ph
        x = 540 + 420 * math.cos(a)
        y = 860 + 120 * math.sin(a)
        dep = (math.sin(a) + 1) / 2
        obj3d(c, nm, x, y - 200, 170 + 90 * dep, ang=d * 90 + j * 80, k=prog(t, t0 + 0.15 * j, t0 + 0.15 * j + 0.4),
              reflect=False, glow=COLD, opacity=0.6 + 0.4 * dep)
    return c


REQ = [('gradcap', 220, 'DEGREE'), ('certificate', 540, 'CHILDCARE COURSE'), ('books', 860, 'EXAMS')]


def sh_entry(t):
    t0 = SH['entry'][0]
    c = studio(t, 'stern')
    title3d(c, 'ENTRY', 540, 300, 150, face=(0.86, 0.9, 1, 1), side=(0.2, 0.25, 0.35, 1), k=prog(t, t0, t0 + 0.4))
    title3d(c, 'REQUIREMENTS', 540, 440, 104, face=(0.86, 0.9, 1, 1), side=(0.2, 0.25, 0.35, 1), k=prog(t, t0 + 0.12, t0 + 0.5))
    for j, (nm, x, lab) in enumerate(REQ):
        kk = prog(t, t0 + 0.1 + j * 0.12, t0 + 0.45 + j * 0.12)
        beams(c, t, x, COLD, kk)
        pedestal(c, x, 1130, 250, k=kk)
        obj3d(c, nm, x, 960, 220, ang=(t - t0) * 70 + j * 40, k=kk, reflect=False, glow=COLD, floor_y=1135)
        tag(c, lab, x, 1290, k=prog(t, t0 + 0.4 + j * 0.12, t0 + 0.65 + j * 0.12), col=(0.3, 0.35, 0.48, 1))
        tag(c, 'REQUIRED', x, 760, k=prog(t, t0 + 0.55 + j * 0.12, t0 + 0.8 + j * 0.12), rot=(-6, 4, -3)[j])
    return c


def sh_switch(t):
    """The stamp slams: shockwave, the requirements are blasted off screen, the studio floods with colour."""
    t0 = SH['switch'][0]
    ts_ = K['noqual'] - 0.15                                         # slam time
    kc = prog(t, ts_ + 0.1, ts_ + 0.5)                              # colour flood
    c = studio(t, 'stern') * (1 - kc) + studio(t, 'warm') * kc
    if t < ts_ + 0.9:
        kb = prog(t, ts_ + 0.05, ts_ + 0.8)
        for j, (nm, x, lab) in enumerate(REQ):
            dx = (x - 540) * 3 * e_in_cubic(kb) + (j - 1) * 80 * kb
            dy = -900 * e_in_cubic(kb) * (0.6 + 0.4 * j / 2)
            if kb < 1:
                pedestal(c, x, 1130 + 400 * e_in_cubic(kb), 250)
                for gh in range(4 if kb > 0 else 1):                # motion-blur ghosts
                    obj3d(c, nm, x + dx * (1 - gh * 0.08), 960 + dy * (1 - gh * 0.08), 220, ang=(t - t0) * 70 + j * 40 + kb * 400,
                          reflect=False, opacity=1.0 / (1 + gh * 1.5), floor_y=-500)
    if t < ts_ + 0.3:
        title3d(c, 'ENTRY', 540, 300 - 900 * prog(t, ts_, ts_ + 0.3), 150, face=(0.86, 0.9, 1, 1), side=(0.2, 0.25, 0.35, 1))
        title3d(c, 'REQUIREMENTS', 540, 440 - 900 * prog(t, ts_, ts_ + 0.3), 104, face=(0.86, 0.9, 1, 1), side=(0.2, 0.25, 0.35, 1))
    shockwave(c, 540, 900, prog(t, ts_, ts_ + 0.8))
    confetti(c, t, ts_ + 0.05, 540, 900)
    k = prog(t, ts_ - 0.25, ts_ + 0.8)
    stamp(c, k, 540, 900)
    if K['withus'] - 0.1 <= t < ts_ - 0.2:                           # "...with us." tiny smile: a glint of orange
        title3d(c, 'with us.', 540, 640, 120, face=ORANGE, side=(0.5, 0.15, 0.05, 1), font=HAND, k=prog(t, K['withus'] - 0.1, K['withus'] + 0.2))
    light_sweep(c, prog(t, ts_ + 0.4, ts_ + 1.1))
    return c


def sh_top7(t):
    t0 = SH['top7'][0]
    c = studio(t, 'warm')
    title3d(c, "WHAT YOU'LL LEARN", 540, 330, 82, k=prog(t, t0, t0 + 0.35))
    title3d(c, 'BEFORE APPROVAL', 540, 440, 82, k=prog(t, t0 + 0.1, t0 + 0.45))
    k7 = prog(t, K['approval'] - 0.3, K['approval'] + 0.3)
    pedestal(c, 540, 1240, 420, col=(0.5, 0.12, 0.42), rim=GOLD, k=prog(t, t0 + 0.2, t0 + 0.6))
    obj3d(c, 'n7', 540, 960, 520, ang=(t - t0) * 50 - 20, k=max(0.001, k7), reflect=True, glow=ORANGE, floor_y=1245)
    title3d(c, 'my top 7', 540, 610, 96, face=ORANGE, side=(0.5, 0.15, 0.05, 1), font=HAND, rot=-4, k=prog(t, K['approval'], K['approval'] + 0.3))
    return c


CAR_R, CAR_Y = 440, 1250


def carousel(c, t, focus):
    """Seven platforms in a ring; `focus` (float) is the item facing the viewer."""
    items = []
    for i in range(7):
        th = (i - focus) * 2 * math.pi / 7
        x = 540 + CAR_R * math.sin(th)
        z = math.cos(th)                                             # 1 = front
        y = CAR_Y - 260 * (1 - z) / 2
        items.append((z, i, x, y, th))
    for z, i, x, y, th in sorted(items):
        s = 0.34 + 0.66 * ((z + 1) / 2) ** 1.4
        dim = 0.25 + 0.75 * ((z + 1) / 2) ** 1.2
        title, obj, photo = TOPICS[i]
        tmp = np.zeros_like(c)
        pedestal(c, x, y, 380 * s, col=(0.5 * dim, 0.12 * dim, 0.42 * dim), rim=GOLD if z > 0.9 else (0.6, 0.4, 0.55, 1))
        blur = 0 if z > 0.6 else int(8 * (0.6 - z))
        obj3d(c, obj, x, y - 260 * s, 430 * s, ang=t * 60 + i * 50, reflect=False, glow=ORANGE if z > 0.9 else None,
              floor_y=y, opacity=0.35 + 0.65 * dim, blur=blur)
        if z > 0.75:                                                 # only the front platform shows its 3D numeral
            kz = (z - 0.75) / 0.25
            obj3d(c, f'n{i + 1}', x - 250 * s, y - 560 * s, 200 * s, ang=math.degrees(-th) * 2 + 12 * math.sin(t * 1.3),
                  reflect=False, opacity=kz, glow=ORANGE)


def sh_items(t):
    t0 = SH['items'][0]
    c = studio(t, 'warm')
    # focus moves from item to item on the words, with an eased turn
    f = 0.0
    for i in range(1, 7):
        f += e_inout_cubic(prog(t, ITEMS[i] - 0.35, ITEMS[i] + 0.1))
    carousel(c, t, f)
    i = int(round(f))
    ki = prog(t, ITEMS[i] - 0.05, ITEMS[i] + 0.35) if i < 7 else 1
    title, obj, photo = TOPICS[min(6, i)]
    if photo:
        ph = photo_still(photo[0], photo[1], 380, 260)
        e = e_out_back(ki, 1.6)
        draw3d(c, ph, 760, 520 - (1 - e) * 120, 0, w=400 * e + 1, ry=-18, rx=6, rz=4, opacity=min(1, ki * 2))
    # title on a glossy glass bar
    words = title.split()
    kb = e_out_cubic(ki)
    bar = rrect(960, 150, 40, (1, 1, 1, 0.16))
    draw(c, bar, 540, 300, opacity=kb)
    sz = 62
    while _wmask(title, N9, sz).shape[1] > 880 and sz > 36:
        sz -= 2
    draw(c, solid(_wmask(title, N9, sz), WHITE), 540, 300 + (1 - kb) * 30, opacity=kb)
    # progress: seven dots
    for j in range(7):
        col = ORANGE if j <= i else (1, 1, 1, 0.3)
        draw(c, rrect(22 if j == i else 16, 22 if j == i else 16, 11, col), 540 + (j - 3) * 46, 410)
    light_sweep(c, prog(t, ITEMS[i] - 0.05, ITEMS[i] + 0.5), amt=0.18)
    return c


def sh_more(t):
    t0 = SH['more'][0]
    c = studio(t, 'warm')
    d = t - t0
    # spiral of light rising
    lay = np.zeros((H, W), np.uint8)
    pts = []
    for u in np.linspace(0, 1, 160):
        a = u * 4 * math.pi + d * 1.2
        pts.append((540 + 330 * math.cos(a) * (1 - 0.3 * u), 1350 - u * 900 + 60 * math.sin(a)))
    n = int(160 * e_inout_cubic(prog(t, t0, t0 + 1.4)))
    if n > 2:
        cv2.polylines(lay, [(np.array(pts[:n]) * 4).astype(np.int32)], False, 255, 6 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32) / 255
        glow_ = cv2.GaussianBlur(m, (0, 0), 10)
        c[:] = np.clip(c + (m * 0.8 + glow_ * 1.2)[..., None] * np.array(GOLD[:3], np.float32), 0, 1)
    title3d(c, 'LEARNING', 540, 300, 120, k=prog(t, K['learning'] - 0.1, K['learning'] + 0.3))
    title3d(c, 'CONTINUES', 540, 430, 120, face=ORANGE, side=(0.5, 0.15, 0.05, 1), k=prog(t, K['learning'] + 0.2, K['learning'] + 0.5))
    objs = (('laptop', 'online', 0.0), ('workshop', 'workshops', 2.1), ('bubbles', 'group discussion', 4.2))
    order = []
    for j, (nm, lab, ph) in enumerate(objs):
        a = d * 1.1 + ph
        x = 540 + 330 * math.cos(a)
        y = 1000 + 120 * math.sin(a) - 80 * j
        z = math.sin(a)
        order.append((z, j, nm, lab, x, y))
    for z, j, nm, lab, x, y in sorted(order):
        k = prog(t, t0 + 0.4 + j * 0.25, t0 + 0.8 + j * 0.25)
        s = 0.7 + 0.3 * (z + 1) / 2
        obj3d(c, nm, x, y, 250 * s, ang=d * 80 + j * 60, k=k, reflect=False, glow=GOLD if z > 0.3 else None)
        if k > 0.5:
            tg = ts(lab, HAND, 50, WHITE)
            draw(c, tg, x, y + 160 * s, opacity=min(1, (k - 0.5) * 2) * (0.5 + 0.5 * (z + 1) / 2))
    return c


@functools.lru_cache(maxsize=1)
def LOGO():
    return F3.logo()


def sh_end(t):
    t0 = SH['end'][0]
    c = studio(t, 'warm')
    kc = prog(t, t0, t0 + 0.6)
    card = rrect(900, 1080, 60, (1, 1, 1, 1)).copy()
    lg = LOGO()
    paste_spr(card, cv2.resize(lg, (700, int(lg.shape[0] * 700 / lg.shape[1]))), 450, 200)
    paste_spr(card, ts('Ask us about', N9, 84, PLUM), 450, 440)
    paste_spr(card, ts('training', HAND, 150, ORANGE), 450, 580)
    paste_spr(card, ts('0161 241 1332', N9, 70, PURPLE), 450, 820)
    paste_spr(card, ts('organicfostering.co.uk', N8, 42, PLUM), 450, 905)
    ry = (1 - e_out_back(kc, 1.4)) * -90
    draw3d(c, blur_sprite(tint(card, (0, 0, 0)), 30), 560, 860, 40, w=900, ry=ry, opacity=0.5 * kc)
    draw3d(c, card, 540, 820, 0, w=900, ry=ry, opacity=min(1, kc * 3))
    kb = prog(t, t0 + 0.5, t0 + 0.9)
    if kb > 0:
        pulse = 1 + 0.03 * math.sin((t - t0) * 4) * prog(t, t0 + 1.2, t0 + 1.6)
        btn = F3.grad_spr(680, 124, 62, phase=(t * 0.12) % 1)
        e = e_out_back(kb, 2.0) * pulse
        draw(c, blur_sprite(btn, 24), 540, 1500, scale=e, opacity=0.6)
        draw(c, btn, 540, 1480, scale=e)
        s = ts('Start your enquiry', N9, 50, WHITE)
        draw(c, s, 540 - 20 * e, 1480, scale=e)
        tri = np.zeros((44, 36), np.uint8)
        cv2.fillPoly(tri, [np.array([[4, 4], [4, 40], [32, 22]])], 255, cv2.LINE_AA)
        draw(c, solid(tri.astype(np.float32) / 255, WHITE), 540 + (s.shape[1] / 2 + 10) * e + 6 * max(0, math.sin((t - t0) * 5)), 1480, scale=e)
        light_sweep(c, prog(t, t0 + 1.4, t0 + 2.1), amt=0.25)
    obj3d(c, 'phone', 930, 330, 220, ang=(t - t0) * 70, k=prog(t, t0 + 0.8, t0 + 1.2), reflect=False, glow=ORANGE)
    confetti(c, t, t0 + 0.6, 540, 1100)
    return c


def build_shots():
    s = {}
    s['walk'] = (0.0, K['study'] - 1.0)
    s['write'] = (s['walk'][1], K['study'] + 0.1)
    s['entry'] = (s['write'][1], K['withus'] - 0.05)
    s['switch'] = (s['entry'][1], K['learn'] - 0.15)
    s['top7'] = (s['switch'][1], ITEMS[0] - 0.3)
    s['items'] = (s['top7'][1], K['stop'] - 0.2)
    s['more'] = (s['items'][1], K['ask'] - 0.25)
    s['end'] = (s['more'][1], DUR + 1)
    return s


SH = build_shots()
ORDER = ['walk', 'write', 'entry', 'switch', 'top7', 'items', 'more', 'end']
FN = dict(walk=sh_walk, write=sh_write, entry=sh_entry, switch=sh_switch, top7=sh_top7, items=sh_items, more=sh_more, end=sh_end)


# ------------------------------------------------------------------ transitions
def tr_cardflip(a, b, p):
    """The whole frame is a card that flips around its vertical axis to the next shot."""
    c = studio(0, 'stern')
    if p < 0.5:
        draw3d(c, np.concatenate([a, np.ones(a.shape[:2] + (1,), np.float32)], 2), 540, 960, 0, w=W, h=H, ry=e_in_cubic(p * 2) * 90)
    else:
        draw3d(c, np.concatenate([b, np.ones(b.shape[:2] + (1,), np.float32)], 2), 540, 960, 0, w=W, h=H, ry=-(1 - e_out_cubic((p - 0.5) * 2)) * 90)
    return c


def tr_zoomthrough(a, b, p):
    e = e_inout_cubic(p)
    za = 1 + e * 1.4
    A = cv2.warpAffine(a, np.float32([[za, 0, (1 - za) * W / 2], [0, za, (1 - za) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    zb = 0.6 + 0.4 * e
    B = cv2.warpAffine(b, np.float32([[zb, 0, (1 - zb) * W / 2], [0, zb, (1 - zb) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    out = A * (1 - e) + B * e
    k = math.sin(math.pi * p)
    return cv2.GaussianBlur(out, (0, 0), 0.1 + 8 * k) if k > 0.1 else out


def tr_ringportal(a, b, p):
    """A gold ring flies at the lens; the next shot is inside it."""
    e = e_inout_cubic(p)
    r = 30 + e * 1400
    d = np.hypot(_X - 540, _Y - 900)
    m = np.clip((r - d) / 6, 0, 1)[..., None]
    rim = np.exp(-((d - r) / 16) ** 2)[..., None]
    out = b * m + a * (1 - m)
    return np.clip(out + rim * np.array(GOLD[:3], np.float32) * 0.9, 0, 1)


def tr_glitchflash(a, b, p):
    src = (a if p < 0.5 else b).copy()
    k = 1 - abs(p - 0.5) * 2
    sh = int(26 * k)
    if sh:
        src[..., 0] = np.roll(src[..., 0], sh, 1)
        src[..., 2] = np.roll(src[..., 2], -sh, 1)
    return np.clip(src + k ** 2 * 0.5, 0, 1)


def tr_cube(a, b, p):
    """3D cube turn: the old shot is one face, the new shot the next face."""
    e = e_inout_cubic(p)
    c = np.zeros_like(a)
    hw = W / 2
    ang = e * 90
    for img, base in ((a, 0), (b, -90)):
        th = math.radians(ang + base)
        if math.cos(th) <= 0.02:
            continue
        cx = 540 + hw * math.sin(th) * 1.0
        cz = hw * (1 - math.cos(th))
        rgba = np.concatenate([img * (0.55 + 0.45 * math.cos(th)), np.ones(img.shape[:2] + (1,), np.float32)], 2)
        draw3d(c, rgba, 540 + hw * math.sin(th) - hw * math.sin(th) * 0, 960, cz + 200 * math.sin(math.pi * p), w=W, h=H, ry=-(ang + base))
    return c


TRANS = {'write': (tr_cardflip, 0.5), 'entry': (tr_zoomthrough, 0.45), 'switch': (None, 0), 'top7': (tr_glitchflash, 0.3),
         'items': (tr_zoomthrough, 0.5), 'more': (tr_cube, 0.55), 'end': (tr_ringportal, 0.6)}


def hits():
    return [(K['study'], 0.4), (K['noqual'] - 0.15, 1.6), (K['approval'], 0.6)] + [(x, 0.5) for x in ITEMS] + \
           [(K['learning'], 0.6), (K['training'], 0.6)]


HITS = hits()


def energy(t):
    z, sx = 1.0, 0.0
    for th, pn in HITS:
        d = t - th
        if 0 <= d < 0.35:
            z += 0.025 * pn * (1 - d / 0.35) ** 2
            sx += 14 * pn * math.sin(d * 60) * (1 - d / 0.35) ** 2 if pn > 1 else 0
    return z, sx


def render_raw(t):
    c = None
    for j in range(1, len(ORDER)):
        nm = ORDER[j]
        a = SH[nm][0]
        kind, td = TRANS[nm]
        if kind is None:
            continue
        d = t - (a - td / 2)
        if 0 <= d < td:
            c = kind(FN[ORDER[j - 1]](min(t, a - 0.01)), FN[nm](max(t, a)), d / td)
            break
    if c is None:
        for nm in ORDER:
            s0, s1 = SH[nm]
            if s0 <= t < s1:
                c = FN[nm](t)
                break
        if c is None:
            c = FN['end'](t)
    z, sx = energy(t)
    if z > 1.001 or abs(sx) > 0.5:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    c = np.ascontiguousarray(c, dtype=np.float32)
    if t < SH['end'][0] + 0.4:
        captions(c, t)
    fo = prog(t, DUR - 1.2, DUR)
    if fo > 0:
        c = c * (1 - 0.6 * e_inout_cubic(fo))
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.14, grain=0.01, vig=0.2)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for tt_ in sys.argv[2].split(','):
            t = float(tt_)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 88])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            p = f'{S}/frames_out/{fi:04d}.jpg'
            if os.environ.get('RESUME') and os.path.exists(p):
                continue
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_JPEG_QUALITY, 95])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print('DUR', DUR, 'NF', NF)
        print({k: (round(a, 2), round(b, 2)) for k, (a, b) in SH.items()})
