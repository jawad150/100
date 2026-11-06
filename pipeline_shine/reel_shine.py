"""BMHC — "Shine" (9:16, ~33 s). Story with no faces (feet and hands only), 3D paper lanterns lit on the spoken cue words,
lanterns rising past the 1843 tower, end card. Gentle female voice; no music (voice + natural sounds).

Usage: python3 reel_shine.py still 1.0,5.0 | python3 reel_shine.py range 0 100 | python3 reel_shine.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_shine as G
from frames_shine import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, GOLD, TEAL, MAG, ORANGE, GREEN, WHITE, PB, PS,
                          LANT, ORDER, POS, RISE, hexf, dusk, R_cover, frame_of, lantern, glow, pool, spark, stars, night, building, arch_card, FB)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = G.S
INFO = json.load(open(f'{S}/tts/info.json'))
OFF = 1.2
WORDS = [(w, t + OFF) for w, t, _ in INFO['words']]
DUR = 33.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y


def WT(i):
    return WORDS[i][1]


I = dict(Every=0, girl=1, has=2, spark=4, At=5, faith=10, character=12, creativity=13, life=14, wellbeing=17, sport=18, And=19,
         friendship=20, Give=21, shine=29, grow=30, confident=33, Shine=34, girls=38, fourteen=39, eighteen=41, Join=42, today=43)
T = {k: WT(v) for k, v in I.items()}
LIGHT = {'faith': T['faith'], 'creative': T['creativity'], 'wellbeing': T['wellbeing'] - 0.15, 'sport': T['sport'], 'social': T['friendship']}


# ------------------------------------------------------------------ footage
class Clip:
    def __init__(self, cid):
        self.cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
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
            return self.cache.get(max(self.cache)) if self.cache else np.zeros((720, 1280, 3), np.uint8)
        self.pos = i
        if len(self.cache) > 30:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def footage(cid, ct, fx=0.5, fy=0.5, z=1.0, w=W, h=H, amt=1.0):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return dusk(R_cover(im, fx, fy, z, w, h), amt)


@functools.lru_cache(maxsize=2)
def GHOST():
    return building('bhmc-f.png', 0.5, 0.45, 1.0, 0.9, W, 560)


@functools.lru_cache(maxsize=2)
def LBG():
    c = night(1300, 0.08)
    b = building('bhmc-f.png', 0.5, 0.5, 1.0, 0.95, W, 600)
    m = np.clip((np.arange(600) - 80) / 300, 0, 1)[:, None, None] * 0.35
    c[1320:1920] = c[1320:1920] * (1 - m) + b * m
    G.stars(c, 70, y1=700, amt=0.5)
    return c


@functools.lru_cache(maxsize=2)
def TOWER():
    b = building('x.jpg', 0.5, 0.55, 1.0, 0.95, W, int(H * 1.25))
    return np.clip(b * 0.72 + np.array(hexf('#0A1F1B'), np.float32) * 0.12, 0, 1).astype(np.float32)


@functools.lru_cache(maxsize=2)
def ENDBG():
    c = night(700, 0.12)
    G.stars(c, 80, y1=1900, amt=0.35)
    return c


@functools.lru_cache(maxsize=1)
def LOGO():
    return FB.logo(True)


# ------------------------------------------------------------------ captions (words appear as they are spoken)
@functools.lru_cache(maxsize=256)
def wmask(w, size):
    return _wmask(w, PB, size)


def caption(c, groups, t, y=1600, size=62, keys=(), keycol=GOLD, t_out=None):
    """groups: list of lines, each a list of word indices; words fade/rise in at their times."""
    keys = {k.strip('.,…!?').lower() for k in keys}
    out = prog(t, t_out, t_out + 0.35) if t_out else 0
    if out >= 1:
        return
    for li, line in enumerate(groups):
        ws = [WORDS[i][0] for i in line]
        disp = [display_word(i) for i in line]
        ms = [wmask(d, size) for d in disp]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ms) - 1)
        xx = W / 2 - tw / 2
        yy = y + li * size * 1.22
        for i, d, m in zip(line, disp, ms):
            k = prog(t, WT(i) - 0.08, WT(i) + 0.25)
            if k > 0:
                kk = d.strip('.,…!?').lower() in keys
                col = keycol if kk else WHITE
                op = min(1, k * 1.6) * (1 - out)
                dy = (1 - e_out_cubic(k)) * 18 - out * 20
                if kk:
                    draw(c, blur_sprite(solid(m, col), 14), xx + m.shape[1] / 2, yy + dy, opacity=0.8 * op)
                draw(c, blur_sprite(solid(m, (0, 0, 0, 1)), 10), xx + m.shape[1] / 2 + 2, yy + 5 + dy, opacity=0.6 * op)
                draw(c, solid(m, col), xx + m.shape[1] / 2, yy + dy, opacity=op)
            xx += m.shape[1] + size * 0.24


DISPLAY = {4: 'spark.', 6: 'Shine,', 12: 'character…', 13: '…creativity…', 14: '…life', 17: 'well-being…', 18: '…sport…', 19: '…and',
           20: 'friendship.', 29: 'shine,', 30: 'grow,', 33: 'confident.', 1: 'girl', 36: 'Club,', 41: 'eighteen.', 43: 'today.'}


def display_word(i):
    return DISPLAY.get(i, WORDS[i][0])


# ------------------------------------------------------------------ lanterns (animated)
def sway(t, j):
    return (3.2 * math.sin(t * 0.9 + j * 1.7), 9 * math.sin(t * 0.7 + j * 2.3), 6 * math.cos(t * 0.6 + j))


def lantern_live(c, nm, x, y, size, t, t_on, rot=0, cast=True):
    """Unlit until t_on, then a quick bloom (glow radius 0 -> 120 px in 0.4 s), a soft coloured pool, a slow breath."""
    k = prog(t, t_on - 0.05, t_on + 0.35)
    col = LANT[nm][2]
    if k > 0 and cast:
        breath = 1 + 0.06 * math.sin((t - t_on) * 2.2)
        pool(c, x, y + size * 0.1, col, r=size * 0.9 * (0.4 + 0.6 * e_out_cubic(k)), amt=0.32 * k * breath)
        glow(c, x, y, max(4, 120 * e_out_cubic(k)) * size / 560 * 1.6, col, 0.35 * k * breath)
        if k < 1:
            glow(c, x, y, 160 * e_out_cubic(k), (1, 0.95, 0.85), 0.5 * (1 - k))
    off = lantern(nm, False)
    on = lantern(nm, True)
    sc = size / on.shape[0]
    if k < 1:
        draw(c, off, x, y, scale=sc * 0.94, rot=rot, opacity=0.75 * (1 - k))
    if k > 0:
        draw(c, on, x, y, scale=sc * (0.94 + 0.06 * e_out_back(k, 2.0)), rot=rot, opacity=k)


def pill(c, text, x, y, col, t, t0, size=34):
    k = prog(t, t0 + 0.15, t0 + 0.5)
    if k <= 0:
        return
    s = ts(text, PS, size, WHITE)
    w = s.shape[1] + 56
    e = e_out_back(k, 1.8)
    yy = y - (1 - e_out_cubic(k)) * 40
    draw(c, blur_sprite(tint(rrect(w, size * 1.9, size * 0.95, col), (0, 0, 0)), 14), x, yy + 8, opacity=0.4 * k, scale=e)
    draw(c, rrect(w, size * 1.9, size * 0.95, col), x, yy, scale=e, opacity=min(1, k * 2))
    draw(c, s, x, yy, scale=e, opacity=min(1, k * 2))


def bez(p0, p1, u, lift=160):
    mx, my = (p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - lift
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * mx + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * my + u * u * p1[1])


def spark_path(t):
    """Where the travelling spark is (None when resting inside a lantern)."""
    legs = [((820, 160), POS['faith'][:2], LIGHT['faith'] - 0.9, LIGHT['faith'])]
    prev = 'faith'
    for nm in ORDER[1:]:
        legs.append((POS[prev][:2], POS[nm][:2], LIGHT[nm] - 0.75, LIGHT[nm]))
        prev = nm
    for p0, p1, a, b in legs:
        if a <= t < b:
            u = e_inout_cubic(prog(t, a, b))
            return bez(p0, p1, u), (p0, p1, a, b)
    return None, None


def draw_trail(c, leg, t, n=26):
    p0, p1, a, b = leg
    u1 = e_inout_cubic(prog(t, a, b))
    pts = [bez(p0, p1, u1 * k / n) for k in range(n + 1)]
    lay = np.zeros((H, W), np.uint8)
    p = np.array(pts[max(0, n - 18):], np.float32)
    if len(p) > 1:
        cv2.polylines(lay, [(p * 4).astype(np.int32)], False, 255, 3 * 4, cv2.LINE_AA, shift=2)
        m = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 3)[..., None]
        c[:] = np.clip(c + m * 0.75 * np.array([1, 0.85, 0.55], np.float32), 0, 1)


def put_arch(c, img, x, y, w, h, col, t, t0, t1=None):
    k = prog(t, t0, t0 + 0.5)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.4) if t1 else 0
    a = arch_card(img, w, h, glow_col=col)
    e = e_out_back(k, 1.6) * (1 - 0.3 * ko)
    op = min(1, k * 2) * (1 - ko)
    draw(c, blur_sprite(tint(a, col[:3]), 26), x, y, opacity=0.5 * op, scale=e)
    draw(c, a, x, y + (1 - e_out_cubic(k)) * 60, scale=e, opacity=op)


# ------------------------------------------------------------------ shots
def sh_open(t):
    """Dark breath -> feet walking towards the Centre -> cupped hands around a flame; the spark lifts away."""
    tf = T['has'] - 0.25
    kf = prog(t, tf, tf + 0.6)
    a = footage(32616, 2.0 + t, fx=0.42, fy=0.75) if kf < 1 else None
    if a is not None:
        G.top_shade(a, 520, 0.7)
        G.shade(a, 0.6, 0.8)
        m = np.clip(1 - np.abs(np.arange(560) - 280) / 280, 0, 1)[:, None, None] ** 0.8 * 0.45
        a[60:620] = a[60:620] * (1 - m) + GHOST() * m
    b = None
    if kf > 0:
        b = footage(41739, 3.0 + (t - tf), fy=0.62, z=1.25 + 0.04 * (t - tf), amt=0.6)
        G.top_shade(b, 700, 0.85)
        G.shade(b, 0.66, 0.8)
    if a is None:
        c = b
    elif b is None:
        c = a
    else:
        c = a * (1 - e_inout_cubic(kf)) + b * e_inout_cubic(kf)
    # fade up from dark
    fi = e_inout_cubic(prog(t, 0.0, 1.3))
    c = c * fi + np.array(hexf('#0A1A17'), np.float32) * (1 - fi)
    # the spark: breathes in the dark, floats ahead of the feet, settles in the flame, then lifts away
    if t < tf:
        sx, sy = 760 + 20 * math.sin(t * 1.3), 860 + 15 * math.sin(t * 1.9)
        s = 0.6 + 0.25 * math.sin(t * 3.0) + 0.3 * prog(t, 0.2, 1.0)
    elif t < T['spark'] + 0.2:
        u = e_inout_cubic(prog(t, tf, T['spark']))
        sx, sy = lerp(760, 545, u), lerp(860, 900, u)
        s = 0.9 + 0.8 * prog(t, T['spark'] - 0.1, T['spark'] + 0.2)
    else:
        u = e_inout_cubic(prog(t, T['spark'] + 0.2, T['At'] - 0.3))
        sx, sy = bez((545, 900), (820, 160), u, 120)
        s = 1.6 - 0.6 * u
        pts = [bez((545, 900), (820, 160), u * k / 30, 120) for k in range(31)]
        lay = np.zeros((H, W), np.uint8)
        cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 3 * 4, cv2.LINE_AA, shift=2)
        m = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 3)[..., None]
        c = np.clip(c + m * 0.6 * np.array([1, 0.85, 0.55], np.float32), 0, 1)
    spark(c, sx, sy, s)
    if t > 1.0:
        G.eyebrow(c)
    caption(c, [[0, 1, 2, 3, 4]], t, y=1540, size=70, keys=('spark.',))
    return c


def sh_lanterns(t):
    c = LBG().copy()
    t0 = T['At'] - 0.4
    kz = e_inout_cubic(prog(t, t0, T['Give']))
    # strings
    lay = np.zeros((H, W), np.uint8)
    for j, nm in enumerate(ORDER):
        x, y, _ = POS[nm]
        dx, dy, _ = sway(t, j)
        cv2.line(lay, (int(x + dx * 0.3), 0), (int(x + dx), int(y + dy - 200)), 255, 1, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255 * 0.25
    c = c * (1 - m) + np.array(hexf('#C9A15A'), np.float32) * m
    for j, nm in enumerate(ORDER):
        x, y, rot = POS[nm]
        dr, dx, dy = sway(t, j)
        lantern_live(c, nm, x + dx, y + dy, 560, t, LIGHT[nm], rot + dr)
    p, leg = spark_path(t)
    if p is not None:
        draw_trail(c, leg, t)
        spark(c, p[0], p[1], 0.9)
    # pills, one at a time
    for j, nm in enumerate(ORDER):
        t_on = LIGHT[nm]
        nxt = LIGHT[ORDER[j + 1]] - 0.8 if j + 1 < len(ORDER) else T['Give'] - 0.5
        if t_on - 0.1 < t < nxt + 0.3:
            x, y, _ = POS[nm]
            tmp = c.copy()
            pill(tmp, LANT[nm][1], min(max(x, 230), W - 230), y + 245, LANT[nm][2], t, t_on)
            fo = prog(t, nxt, nxt + 0.3)
            c = c * fo + tmp * (1 - fo)
    put_arch(c, footage(32622, 3.0 + (t - T['sport']), w=250, h=330, amt=0.5), 545, 420, 250, 330, GREEN, t, T['sport'] - 0.1, T['And'] - 0.3)
    put_arch(c, footage(32616, 5.0 + (t - T['And']), w=250, h=330, amt=0.5), 545, 420, 250, 330, GOLD, t, T['And'] - 0.1, T['Give'] - 0.6)
    G.shade(c, 0.76, 0.85)
    caps = [
        ([[5, 6, 7, 8, 9], [10, 11, 12]], T['At'] - 0.1, T['creativity'] - 0.45, ('faith', 'character…'), TEAL),
        ([[13]], T['creativity'] - 0.1, T['life'] - 0.4, ('…creativity…',), MAG),
        ([[14, 15, 16, 17]], T['life'] - 0.1, T['sport'] - 0.45, ('well-being…',), ORANGE),
        ([[18]], T['sport'] - 0.1, T['And'] - 0.4, ('…sport…',), GREEN),
        ([[19, 20]], T['And'] - 0.1, T['Give'] - 0.6, ('friendship.',), GOLD),
    ]
    for lines, a, b, keys, col in caps:
        if a - 0.2 <= t < b + 0.4:
            caption(c, lines, t, y=1610, size=62, keys=keys, keycol=col, t_out=b)
    # slow push-in
    z = 1.0 + 0.04 * kz
    if z > 1.001:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H * 0.45]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    return c


def sh_rise(t):
    """On 'shine' the lanterns lift and drift up past the 1843 tower; the camera tilts up; the sky warms."""
    t0 = T['Give'] - 0.3
    tilt = e_inout_cubic(prog(t, t0, T['Shine'] - 0.2))
    bg = TOWER()
    oy = int(lerp(bg.shape[0] - H, 0, tilt))
    c = bg[oy:oy + H].copy()
    warm = 0.15 + 0.4 * prog(t, T['shine'] - 0.3, T['confident'] + 0.6)
    g = np.exp(-((_X - W / 2) ** 2 + (_Y - 600) ** 2) / (2 * 750 ** 2))[..., None] * warm
    c = np.clip(c + g * np.array([0.5, 0.36, 0.14], np.float32), 0, 1)
    G.stars(c, 60, y1=500, amt=0.45)
    lift = e_in_cubic(prog(t, T['shine'] - 0.1, T['Shine'] + 0.4))
    for j, nm in enumerate(ORDER):
        x0, y0, r0 = POS[nm]
        x1, y1, r1 = RISE[nm]
        settle = e_inout_cubic(prog(t, t0, t0 + 1.4))
        dr, dx, dy = sway(t, j)
        x = lerp(x0, x1, settle) + dx * 1.4
        y = lerp(y0, y1 + 160, settle) + dy - lift * (900 + j * 90)
        size = lerp(560, 250, settle) * (1 - 0.35 * lift)
        lantern_live(c, nm, x, y, size, t, -1.0, lerp(r0, r1, settle) + dr * 1.5)
        if lift > 0:
            lay = np.zeros((H, W), np.uint8)
            cv2.line(lay, (int(x), int(y + size * 0.45)), (int(x - dx * 0.5), int(y + size * 0.45 + 260 * lift)), 255, 3, cv2.LINE_AA)
            m = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 4)[..., None] * 0.6
            c = np.clip(c + m * np.array(LANT[nm][2][:3], np.float32), 0, 1)
    if lift > 0:
        rng = np.random.default_rng(9)
        for k in range(36):
            px, py0 = rng.uniform(80, 1000), rng.uniform(300, 1500)
            py = py0 - (t - T['shine']) * rng.uniform(40, 110)
            glow(c, px + 12 * math.sin(t * 2 + k), py, rng.uniform(2, 5), (1, 0.9, 0.6), rng.uniform(0.3, 0.9) * min(1, lift * 3))
    G.shade(c, 0.64, 0.82)
    G.eyebrow(c)
    caption(c, [[21, 22, 23, 24, 25], [26, 27, 28, 29]], t, y=1500, size=62, keys=('shine,',), t_out=T['grow'] - 0.72)
    caption(c, [[26, 27, 28, 29], [30, 31, 32, 33]], t if t >= T['grow'] - 0.34 else -1, y=1500, size=62, keys=('shine,', 'grow,', 'confident.'))
    return c


def sh_end(t):
    c = ENDBG().copy()
    t0 = T['Shine'] - 0.4
    spark(c, W / 2, 330 + 6 * math.sin(t * 1.4), 1.0 + 0.1 * math.sin(t * 2.6))
    k = prog(t, T['Shine'] - 0.1, T['Shine'] + 0.6)
    if k > 0:
        m = _wmask('Shine', 'Caveat-700', 260)
        ramp = np.clip((e_out_cubic(k) * (m.shape[1] + 40) - np.arange(m.shape[1])) / 30, 0, 1)[None, :]
        mm = m * ramp
        draw(c, blur_sprite(solid(mm, GOLD), 26), W / 2, 560, opacity=0.9)
        draw(c, solid(mm, (1, 0.93, 0.78, 1)), W / 2, 560)
    for txt, y, font, size, col, ta in (('Youth Club for girls · 14–18', 760, PB, 46, WHITE, T['girls'] - 0.1),
                                        ('Qualified female mentors · weekly at BMHC', 840, PS, 32, (1, 1, 1, 0.8), T['eighteen'] + 0.1)):
        kk = prog(t, ta, ta + 0.4)
        if kk > 0:
            draw(c, ts(txt, font, size, col), W / 2, y + (1 - e_out_cubic(kk)) * 20, opacity=kk)
    kb = prog(t, T['Join'] - 0.1, T['Join'] + 0.35)
    if kb > 0:
        eb = e_out_back(kb, 2.0)
        pulse = 1 + 0.02 * math.sin((t - T['Join']) * 3.5) * prog(t, T['Join'] + 0.6, T['Join'] + 1.0)
        btn = rrect(720, 120, 60, GOLD)
        draw(c, blur_sprite(btn, 30), W / 2, 1000, opacity=0.6 * min(1, kb * 2), scale=eb * pulse)
        draw(c, btn, W / 2, 1000, scale=eb * pulse)
        draw(c, ts('Join Shine Youth Club', PB, 46, hexf('#122F2A') + (1,)), W / 2, 1000, scale=eb * pulse)
        sw = prog(t, T['Join'] + 0.5, T['Join'] + 1.3)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(200, 880, sw) - (_Y - 1000) * 0.4) / 40) ** 2) * (np.abs(_Y - 1000) < 58)
            c = np.clip(c + band[..., None] * 0.3, 0, 1)
    kp = prog(t, T['today'], T['today'] + 0.5)
    if kp > 0:
        draw(c, ts('0161 881 8062 · link in bio', PS, 34, (1, 1, 1, 0.85)), W / 2, 1130, opacity=kp)
    kl = prog(t, t0 + 0.3, t0 + 1.0)
    if kl > 0:
        lg = LOGO()
        draw(c, lg, W / 2, 1360, scale=520 / lg.shape[1], opacity=kl)
    for i, nm in enumerate(ORDER):
        kk = prog(t, t0 + 0.2 + i * 0.12, t0 + 0.6 + i * 0.12)
        if kk > 0:
            dr, dx, dy = sway(t, i)
            lantern_live(c, nm, 180 + i * 180 + dx * 0.5, 1640 + dy * 0.6 + (1 - e_out_cubic(kk)) * 120, 260, t, -1, dr, cast=False)
    return c


def shots():
    return [
        (0.0, T['At'] - 0.4, sh_open),
        (T['At'] - 0.4, T['Give'] - 0.3, sh_lanterns),
        (T['Give'] - 0.3, T['Shine'] - 0.4, sh_rise),
        (T['Shine'] - 0.4, DUR + 1, sh_end),
    ]


SHOTS = None


def tr_dark(a, b, p):
    """Through the dark: the warm flame scene dims to night green before the lanterns appear."""
    k = 1 - abs(p - 0.5) * 2
    src = a if p < 0.5 else b
    return src * (1 - 0.7 * k ** 0.8) + np.array(hexf('#0A1A17'), np.float32) * 0.7 * k ** 0.8


def tr_bloom(a, b, p):
    e = e_inout_cubic(p)
    k = math.sin(math.pi * p)
    out = a * (1 - e) + b * e
    g = np.exp(-((_X - W / 2) ** 2 + (_Y - 800) ** 2) / (2 * (300 + 800 * k) ** 2))[..., None] * k * 0.7
    return np.clip(out + g * np.array([1.0, 0.85, 0.55], np.float32), 0, 1)


def tr_iris(a, b, p):
    e = e_in_cubic(p)
    r = e * 2300
    d = np.hypot(_X - W / 2, _Y - 330)
    hole = np.clip((r - d) / 40, 0, 1)[..., None]
    ring = np.clip((r + 60 - d) / 40, 0, 1)[..., None] - hole
    return np.clip(a * (1 - hole - ring * 0.5) + b * hole + ring * 0.5 * np.array([1, 0.85, 0.55], np.float32), 0, 1)


TRANS = [(tr_dark, 0.8), (tr_bloom, 0.8), (tr_iris, 0.9)]


def hits():
    return [(T['spark'], 0.6), (LIGHT['faith'], 0.4), (LIGHT['creative'], 0.4), (LIGHT['wellbeing'], 0.4), (LIGHT['sport'], 0.4),
            (LIGHT['social'], 0.5), (T['shine'], 0.5), (T['Join'], 0.5)]


HITS = None


def energy(t):
    z = 1.0
    for th, pn in HITS:
        d = t - th
        if 0 <= d < 0.4:
            z += 0.012 * pn * (1 - d / 0.4) ** 2
    return z


def render_raw(t):
    global SHOTS, HITS
    if SHOTS is None:
        SHOTS = shots()
        HITS = hits()
    c = None
    for j, (a, b, f) in enumerate(SHOTS[1:]):
        kind, td = TRANS[j]
        d = t - (a - td / 2)
        if 0 <= d < td:
            c = kind(SHOTS[j][2](min(t, a - 0.01)), f(max(t, a)), d / td)
    if c is None:
        for a, b, f in SHOTS:
            if a <= t < b:
                c = f(t)
                break
        if c is None:
            c = SHOTS[-1][2](t)
    z = energy(t) * (1.0 + 0.004 * math.sin(t * 0.7))
    if z > 1.001:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    fo = prog(t, DUR - 2.2, DUR)                     # gentle fade-out, no abrupt ending
    if fo > 0:
        c = c * (1 - e_inout_cubic(fo)) + np.array(hexf('#0A1A17'), np.float32) * e_inout_cubic(fo)
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.22, grain=0.012, vig=0.3)


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
        print({k: round(v, 2) for k, v in T.items()})
