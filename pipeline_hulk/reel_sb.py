"""Hulk Marketing — "Same Business?" (9:16, ~34 s), video version with people and 3D touchpoints, per the concept PDF.

Before = jittery, off-grid, overshooting pops. After = precise snaps to a grid with crisp ease-outs (0.3 s morphs).
Usage: python3 reel_sb.py still 1.0,5.0 | python3 reel_sb.py range 0 100 | python3 reel_sb.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_sb as B
from frames_sb import (F, R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, OFF, FOREST, LIME, NAVY, AMBER, WHITE,
                       CAP, CAPB, SMALL, ITEMS, JIT, t3, offwhite, forest, vivid, logo, cutout, label, tick, guideline, pop_ring)
import frames_hulk as K
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = B.S
INFO = json.load(open(f'{S}/tts/info.json'))
OFFS = 0.6
WORDS = [(w, t + OFFS) for w, t, _ in INFO['words']]
DUR = 34.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y


def WT(i):
    return WORDS[i][1]


I = dict(quick=0, same=5, business=6, van=8, sign=10, card=12, website=14, instagram=16, invoice=18, They=19, And=21, either=26,
         disjointed=27, trust=30, So=31, system=35, logo=37, palette=39, typeface=41, Then=42, roll=43, every=47, touchpoint=48,
         A=49, sys2=54, file=58, Build=59, identity=62, Hulk=64)
T = {k: WT(v) for k, v in I.items()}


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


def footage(cid, ct, w, h, fx=0.5, fy=0.5, z=1.0):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return vivid(F.cover(im, fx, fy, z, w, h))


@functools.lru_cache(maxsize=2)
def OFFW():
    return offwhite()


@functools.lru_cache(maxsize=2)
def FOR(g=0.12):
    return forest(g)


# ------------------------------------------------------------------ motion helpers
def wobble(t, t0, amp=3.0, seed=0):
    """Jittery 'before' motion: small restless rotation + offset."""
    d = t - t0
    return (amp * math.sin(d * 7.1 + seed) + amp * 0.5 * math.sin(d * 13.3 + seed * 2),
            4 * math.sin(d * 9.7 + seed), 3 * math.cos(d * 8.3 + seed))


def pop_obj(c, name, x, y, size, t, t0, rot=0, jitter=True, seed=0, ring=True, dur=0.4):
    """Before-item pop: overshooting scale, then a restless wobble."""
    k = prog(t, t0, t0 + dur)
    if k <= 0:
        return
    e = e_out_back(k, 3.0)
    sp = t3(name)
    sc = size / max(sp.shape[:2]) * e
    r, dx, dy = wobble(t, t0, 2.5, seed) if jitter else (0, 0, 0)
    if ring and k < 1:
        kr = prog(t, t0, t0 + 0.45)
        rr = size * (0.3 + 0.25 * e_out_cubic(kr))
        lay = np.zeros((H, W), np.uint8)
        cv2.circle(lay, (int(x * 4), int(y * 4)), int(rr * 4), 255, 6 * 4, cv2.LINE_AA, shift=2)
        for j in range(10):
            a = j / 10 * 2 * math.pi + 0.2
            cv2.line(lay, (int((x + math.cos(a) * rr * 1.18) * 4), int((y + math.sin(a) * rr * 1.18) * 4)),
                     (int((x + math.cos(a) * rr * 1.42) * 4), int((y + math.sin(a) * rr * 1.42) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * (1 - kr)
        c[:] = c * (1 - m) + np.array(LIME[:3], np.float32) * m
    draw(c, sp, x + dx, y + dy + (1 - e_out_cubic(k)) * 80, scale=sc, rot=rot + r + (1 - k) * -20, opacity=min(1, k * 3))


def obj(c, name, x, y, size, rot=0, opacity=1.0, sc_mul=1.0):
    sp = t3(name)
    draw(c, sp, x, y, scale=size / max(sp.shape[:2]) * sc_mul, rot=rot, opacity=opacity)


def words_in(c, text, x, y, size, t, t0s, col=None, key=(), dark=False, font=CAP, center=False):
    """A line whose words appear on their spoken times (pop up with a small overshoot)."""
    key = {k.lower() for k in key}
    ws = text.split()
    ms = [_wmask(w_, font, size) for w_ in ws]
    tw = sum(m.shape[1] for m in ms) + size * 0.22 * (len(ws) - 1)
    xx = W / 2 - tw / 2 if center else x
    for w_, m, t0 in zip(ws, ms, t0s):
        k = prog(t, t0 - 0.06, t0 + 0.16)
        if k > 0:
            e = e_out_back(k, 2.0)
            kk = w_.strip('.,?!’\'…:').lower() in key
            yy = y + (1 - e_out_cubic(k)) * 26
            if kk and not dark:
                draw(c, rrect(m.shape[1] + size * 0.2, size * 1.1, 10, LIME), xx + m.shape[1] / 2, yy + size * 0.04, scale=e, opacity=min(1, k * 2))
                draw(c, solid(m, FOREST), xx + m.shape[1] / 2, yy, scale=e, opacity=min(1, k * 2))
            else:
                cc = col or (LIME if kk else (WHITE if dark else FOREST))
                draw(c, solid(m, cc), xx + m.shape[1] / 2, yy, scale=e, opacity=min(1, k * 2))
        xx += m.shape[1] + size * 0.22


def counter(c, k, t, t0, x=W - 150, y=290):
    kk = prog(t, t0, t0 + 0.25)
    e = 1 + 0.25 * math.sin(math.pi * kk) if 0 < kk < 1 else 1
    draw(c, rrect(170, 74, 37, LIME), x, y, scale=e)
    draw(c, ts(f'{k} / 6', CAPB, 40, FOREST), x, y, scale=e)


def hulk_tag(c, x=70, y=150):
    lg = logo()
    draw(c, lg, x + 100, y, scale=200 / lg.shape[1], opacity=0.9)


def put_card(c, img, x, y, w, h, rot=0, sh=0.35, scale=1.0, opacity=1.0):
    k = B.card(img, w, h)
    draw(c, blur_sprite(tint(k, (0.05, 0.08, 0.06)), 30), x + 8, y + 28, rot=rot, opacity=sh * opacity, scale=scale)
    draw(c, k, x, y, rot=rot, scale=scale, opacity=opacity)


# ------------------------------------------------------------------ shots
def sh_hook(t):
    c = OFFW().copy()
    k = prog(t, 0.0, 0.45)
    put_card(c, footage(6302, 3.0 + t, 940, 900, fy=0.45), W / 2, 680 + (1 - e_out_cubic(k)) * 60, 940, 900, scale=0.94 + 0.06 * e_out_back(k))
    # the red van slides in from the left, overshoots, honks on "van"
    kv = prog(t, 0.35, 0.95)
    if kv > 0:
        x = lerp(-420, 560, e_out_back(kv, 1.6))
        r, dx, dy = wobble(t, 0.35, 2.0, 1)
        honk = prog(t, T['van'], T['van'] + 0.35)
        sq = 1 + (0.12 * math.sin(math.pi * honk) if 0 < honk < 1 else 0)
        obj(c, 'van_before', x + dx, 1090 + dy, 720, rot=-4 + r, sc_mul=sq)
        if 0 < honk < 1:
            for j in range(3):
                lay = np.zeros((H, W), np.uint8)
                a0 = -0.6 + j * 0.3
                cv2.line(lay, (int((x - 380) * 4), int((1000 + j * 40) * 4)), (int((x - 450 - honk * 60) * 4), int((990 + j * 55) * 4)), 255, 6 * 4, cv2.LINE_AA, shift=2)
                m = lay.astype(np.float32)[..., None] / 255 * (1 - honk)
                c[:] = c * (1 - m) + np.array(FOREST[:3], np.float32) * m
    counter(c, 1, t, 0.35)
    hulk_tag(c)
    words_in(c, 'Quick one.', 70, 1320, 46, t, [WT(0), WT(1)], col=(0.07, 0.11, 0.09, 0.7))
    # "Same business?" slams on "same"
    ks = prog(t, T['same'] - 0.04, T['same'] + 0.18)
    if ks > 0:
        for i, w_ in enumerate(('Same', 'business?')):
            m = _wmask(w_, CAPB, 150)
            e = lerp(1.7, 1.0, e_out_cubic(ks))
            draw(c, solid(m, FOREST), 70 + m.shape[1] / 2, 1520 + i * 150, scale=e, opacity=min(1, ks * 3))
    words_in(c, 'Are these the', 70, 1382, 46, t, [WT(2), WT(3), WT(4)], col=(0.07, 0.11, 0.09, 0.7))
    return c


TOUCH = {   # item: (clip, clip start s, fx, fy, size, ox, oy, word key, counter)
    'sign': (15997, 6.0, 0.5, 0.6, 700, W / 2, 900, 'sign', 2),
    'card': (30012, 2.0, 0.5, 0.5, 620, W / 2, 1020, 'card', 3),
    'web': (4713, 4.0, 0.5, 0.5, 700, W / 2, 1000, 'website', 4),
    'insta': (4919, 4.0, 0.5, 0.5, 640, 760, 900, 'instagram', 5),
    'invoice': (46505, 4.0, 0.5, 0.5, 640, 780, 980, 'invoice', 6),
}
WORDTXT = {'sign': 'The sign.', 'card': 'The card.', 'web': 'The website.', 'insta': 'The Instagram.', 'invoice': 'The invoice.'}


def make_touch(item):
    cid, cs, fx, fy, size, ox, oy, key, n = TOUCH[item]
    t_word = T[key]
    i_word = I[key]

    def sh(t):
        c = OFFW().copy()
        t0 = t_word - 0.25
        put_card(c, footage(cid, cs + (t - t0), 940, 1000, fx, fy), W / 2, 760, 940, 1000, rot=JIT[item] * 0.3)
        pop_obj(c, f'{item}_before', ox, oy, size, t, t_word - 0.05, rot=JIT[item], seed=n)
        if item == 'sign':
            obj(c, 'van_before', 860 + 6 * math.sin(t * 9), 1260, 300, rot=8 + 3 * math.sin(t * 7))
        counter(c, n, t, t_word - 0.05)
        hulk_tag(c)
        words_in(c, WORDTXT[item], 70, 1500, 86, t, [WT(i_word - 1), WT(i_word)])
        return c
    return sh


POS = B.POS


def sh_mess(t):
    t0 = T['invoice'] + 0.35
    c = OFFW().copy()
    for j, it in enumerate(ITEMS):
        x, y, s = POS[it]
        k = prog(t, t0 + j * 0.03, t0 + 0.25 + j * 0.03)
        r, dx, dy = wobble(t, t0, 4.0, j * 1.7)
        obj(c, f'{it}_before', x + JIT[it] * 4 + dx, y + JIT[it] * 3 + dy, s * e_out_back(k, 2.4) if k > 0 else 1, rot=JIT[it] * 1.5 + r,
            opacity=min(1, k * 3))
    counter(c, 6, t, 0)
    hulk_tag(c)
    m = _wmask('Same business?', CAP, 90)
    draw(c, solid(m, FOREST), 70 + m.shape[1] / 2, 1540)
    return c


def row_pos(j, shrink):
    return 110 + j * 172, 330


def sh_reveal(t):
    """'They are.' on forest black; the six shrink to a faint row; the confused customer; then the row cracks apart."""
    c = FOR(0.12).copy()
    t0 = T['They'] - 0.05
    kr = e_inout_cubic(prog(t, t0, t0 + 0.5))
    kc = prog(t, T['disjointed'] - 0.1, T['disjointed'] + 0.6)
    rng = np.random.default_rng(3)
    for j, it in enumerate(ITEMS):
        x0, y0, s0 = POS[it]
        x1, y1 = 110 + j * 172, 330
        x, y, s = lerp(x0, x1, kr), lerp(y0, y1, kr), lerp(s0, 150, kr)
        dx, dy, dr = rng.uniform(-30, 30), rng.uniform(-40, 40), rng.uniform(-10, 10)
        if kc > 0:
            ec = e_out_cubic(kc)
            y = lerp(y, 760, e_inout_cubic(prog(t, T['disjointed'] - 0.1, T['disjointed'] + 0.4)))
            s = lerp(s, 160, ec)
            x += dx * ec
            y += dy * ec
        op = lerp(1.0, 0.45, kr) if kc <= 0 else lerp(0.45, 1.0, kc)
        obj(c, f'{it}_before', x, y, s, rot=JIT[it] * (1 + kc) + dr * kc, opacity=op)
    if kc > 0:
        B.cracks_dark(c) if kc > 0.6 else None
    # the confused customer (fades out as the cost line arrives)
    ka = prog(t, T['And'] - 0.15, T['And'] + 0.3)
    ko = prog(t, T['disjointed'] - 0.3, T['disjointed'])
    if ka > 0 and ko < 1:
        put_card(c, footage(9248, 8.0 + (t - T['And']), 820, 640, fy=0.4), W / 2, 820 + (1 - e_out_cubic(ka)) * 80, 820, 640, sh=0.6,
                 opacity=min(1, ka * 2) * (1 - ko))
    if ko < 1:
        kt = prog(t, T['They'] - 0.04, T['They'] + 0.14)
        if kt > 0:
            m = _wmask('They are.', CAPB, 130)
            draw(c, solid(m, WHITE), 70 + m.shape[1] / 2, 1290, scale=lerp(1.5, 1.0, e_out_cubic(kt)), opacity=min(1, kt * 3) * (1 - ko))
        for li, (ln, i0) in enumerate((('And your customers', 21), ('can’t tell either.', 24))):
            tmp = c.copy()
            words_in(tmp, ln, 70, 1440 + li * 84, 74, t, [WT(i0 + q) for q in range(len(ln.split()))], col=LIME, dark=True)
            c[:] = c * ko + tmp * (1 - ko)
    if kc > 0:
        words_in(c, 'Disjointed brand,', 70, 1250, 96, t, [WT(27), WT(28)], dark=True)
        words_in(c, 'diluted trust.', 70, 1250 + 107, 96, t, [WT(29), WT(30)], key=('trust',), dark=True)
        ku = prog(t, T['trust'] + 0.05, T['trust'] + 0.45)
        if ku > 0:
            wd = _wmask('diluted', CAP, 96).shape[1] + 96 * 0.22
            wt = _wmask('trust.', CAP, 96).shape[1]
            ux0, uy = 70 + wd, 1250 + 107 + 62
            ux1 = ux0 + (wt - 30) * e_out_cubic(ku)
            lay = np.zeros((H, W), np.uint8)
            cv2.line(lay, (int(ux0 * 4), int(uy * 4)), (int(ux1 * 4), int(uy * 4)), 255, 7 * 4, cv2.LINE_AA, shift=2)
            m = lay.astype(np.float32)[..., None] / 255
            c[:] = c * (1 - m) + np.array(LIME[:3], np.float32) * m
    return c


def sh_system(t):
    c = OFFW().copy()
    c[:] = np.ones_like(c) * np.array(OFF[:3], np.float32)
    t0 = T['So'] - 0.15
    kl = prog(t, t0 + 0.1, t0 + 0.4)
    if kl > 0:
        label(c, 'Copperline · brand guidelines', 70, 150)
        draw(c, rrect(940 * e_out_cubic(kl), 2, 1, (0.07, 0.11, 0.09, 0.2)), 70 + 470 * e_out_cubic(kl), 190)
    # the mark draws itself (wipe from left) on "system"→"logo", then settles
    km = prog(t, T['system'] - 0.05, T['logo'] + 0.2)
    if km > 0:
        sp = t3('mark')
        sc = 330 / max(sp.shape[:2]) * (0.85 + 0.15 * e_out_back(prog(t, T['logo'] - 0.05, T['logo'] + 0.3)))
        ramp = np.clip((e_inout_cubic(km) * (sp.shape[1] + 40) - np.arange(sp.shape[1])) / 30, 0, 1)[None, :, None]
        draw(c, sp * ramp, 320, 420, scale=sc, rot=-6 * (1 - e_out_cubic(km)))
        label(c, '01  Logo', 70, 640) if t > T['logo'] else None
    if t > T['palette'] - 0.05:
        k = prog(t, T['palette'] - 0.05, T['palette'] + 0.3)
        obj(c, 'swatches', 360, 820 + (1 - e_out_cubic(k)) * 60, 520 * e_out_back(k, 1.8) if k > 0 else 1, opacity=min(1, k * 3))
        label(c, '02  Palette', 70, 1010)
    # the Hulk team member brings the swatch cards
    ko = prog(t, T['palette'] - 0.3, T['palette'] + 0.2)
    if ko > 0:
        sp = cutout('CUT-07-oliver-james-whitmore.webp')
        draw(c, sp, lerp(1300, 860, e_out_cubic(ko)), 980, scale=620 / sp.shape[0])
    if t > T['typeface'] - 0.05:
        k = prog(t, T['typeface'] - 0.05, T['typeface'] + 0.3)
        obj(c, 'aa', 260, 1150, 280 * e_out_back(k, 1.8) if k > 0 else 1, opacity=min(1, k * 3))
        draw(c, ts('Inter Tight', 'Headline-700', 40, FOREST), 520, 1130, opacity=k)
        label(c, '03  Typeface', 70, 1290)
    words_in(c, 'So we build one system:', 70, 1430, 66, t, [WT(31 + q) for q in range(5)], key=('system:',))
    words_in(c, 'one logo, one palette,', 70, 1430 + 74, 66, t, [WT(36 + q) for q in range(4)])
    words_in(c, 'one typeface.', 70, 1430 + 148, 66, t, [WT(40), WT(41)])
    return c


GX, GY = (290, 790), (430, 790, 1150)


def snap_time(j):
    return T['roll'] - 0.05 + j * ((T['touchpoint'] + 0.35 - T['roll']) / 6)


def sh_snap(t):
    c = OFFW().copy()
    t0 = T['Then'] - 0.15
    kg = prog(t, t0, t0 + 0.35)
    for x in GX:
        guideline(c, x, 230, x, 230 + 1100 * e_out_cubic(kg))
    for j, it in enumerate(ITEMS):
        x, y = GX[j % 2], GY[j // 2]
        ts_ = snap_time(j)
        ks = prog(t, ts_, ts_ + 0.3)
        draw(c, rrect(470, 330, 30, (1, 1, 1, 0.85 * min(1, kg * 2))), x, y)
        if ks <= 0:
            r, dx, dy = wobble(t, t0, 3.0, j)
            bx, by, bs = B.POS[it]
            obj(c, f'{it}_before', lerp(bx, x, e_out_cubic(kg)) + dx + JIT[it] * 3, lerp(by, y, e_out_cubic(kg)) + dy, 380, rot=JIT[it] * 1.3 + r)
        else:
            e = e_out_cubic(ks)
            sq = 1 + 0.14 * math.sin(math.pi * min(1, ks * 1.6)) if ks < 0.62 else 1.0
            if ks < 0.5:
                obj(c, f'{it}_before', x, y, 380, rot=JIT[it] * (1 - e), opacity=1 - ks * 2, sc_mul=sq)
            obj(c, f'{it}_after', x, y, 400, opacity=min(1, ks * 2.2), sc_mul=sq)
            fl = 1 - prog(t, ts_, ts_ + 0.18)
            if fl > 0:
                g = np.exp(-((_X - x) ** 2 + (_Y - y) ** 2) / (2 * 160 ** 2))[..., None] * 0.6 * fl
                c[:] = np.clip(c + g * np.array(LIME[:3], np.float32), 0, 1)
            kt = prog(t, ts_ + 0.15, ts_ + 0.35)
            if kt > 0:
                tick(c, x + 200, y - 130, 26 * e_out_back(kt, 2.0))
    hulk_tag(c)
    words_in(c, 'Then roll it out across', 70, 1450, 70, t, [WT(42 + q) for q in range(5)])
    words_in(c, 'every touchpoint.', 70, 1450 + 78, 70, t, [WT(47), WT(48)], key=('every',))
    return c


def sh_line(t):
    c = FOR(0.18).copy()
    t0 = T['A'] - 0.1
    k = prog(t, t0, t0 + 0.45)
    put_card(c, footage(49023, 3.0 + (t - t0), 860, 600, fx=0.6, fy=0.4), W / 2, 560 + (1 - e_out_cubic(k)) * 60, 860, 600, sh=0.6,
             scale=0.95 + 0.05 * e_out_cubic(k))
    kv = prog(t, t0 + 0.25, t0 + 0.6)
    if kv > 0:
        obj(c, 'van_after', lerp(-300, 330, e_out_cubic(kv)), 860, 440, rot=-2)
    kc = prog(t, t0 + 0.45, t0 + 0.8)
    if kc > 0:
        obj(c, 'card_after', 800, 900 + (1 - e_out_cubic(kc)) * 50, 330 * e_out_back(kc, 1.6), rot=6)
    words_in(c, 'A premium brand', 70, 1180, 92, t, [WT(49), WT(50), WT(51)], font=CAPB, dark=True)
    words_in(c, 'is a system,', 70, 1288, 92, t, [WT(52), WT(53), WT(54)], font=CAPB, col=LIME, dark=True)
    words_in(c, 'not a logo file.', 70, 1396, 92, t, [WT(55), WT(56), WT(57), WT(58)], font=CAPB, dark=True)
    return c


def sh_end(t):
    c = FOR(0.2).copy()
    t0 = T['Build'] - 0.15
    kl = prog(t, t0, t0 + 0.45)
    lg = logo()
    draw(c, lg, W / 2, 560, scale=820 / lg.shape[1] * (0.9 + 0.1 * e_out_back(kl, 1.6)), opacity=min(1, kl * 2))
    kk = prog(t, t0 + 0.3, t0 + 0.7)
    draw(c, ts('A premium brand is a system, not a logo file.', 'Hanken-700', 34, (1, 1, 1, 0.8)), W / 2, 690, opacity=kk)
    kb = prog(t, T['identity'] - 0.1, T['identity'] + 0.3)
    if kb > 0:
        eb = e_out_back(kb, 2.0)
        pulse = 1 + 0.025 * math.sin((t - T['identity']) * 4) * prog(t, T['identity'] + 0.6, T['identity'] + 1.0)
        btn = rrect(800, 140, 70, LIME)
        draw(c, blur_sprite(btn, 30), W / 2, 960, opacity=0.5 * min(1, kb * 2), scale=eb * pulse)
        draw(c, btn, W / 2, 960, scale=eb * pulse)
        tmp = np.zeros((150, 820, 4), np.float32)
        s = ts('Build My Brand Identity', CAPB, 50, FOREST)
        a = K.arrow_ne(40, FOREST)
        tw = s.shape[1] + 14 + a.shape[1]
        paste_spr(tmp, s, 410 - tw / 2 + s.shape[1] / 2, 75)
        paste_spr(tmp, a, 410 + tw / 2 - a.shape[1] / 2 + 6 * max(0, math.sin((t - T['identity']) * 5)), 72)
        draw(c, tmp, W / 2, 960, scale=eb * pulse)
        sw = prog(t, T['identity'] + 0.5, T['identity'] + 1.2)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(160, 920, sw) - (_Y - 960) * 0.4) / 40) ** 2) * (np.abs(_Y - 960) < 68)
            c[:] = np.clip(c + band[..., None] * 0.35, 0, 1)
    kf = prog(t, T['Hulk'] - 0.1, T['Hulk'] + 0.3)
    if kf > 0:
        draw(c, ts('hulkmarketing.co.uk', CAPB, 44, LIME), W / 2, 1130 + (1 - kf) * 16, opacity=kf)
        draw(c, ts('07577 764436', CAPB, 44, WHITE), W / 2, 1200 + (1 - kf) * 16, opacity=kf)
    return c


def shots():
    return [
        (0.0, T['sign'] - 0.3, sh_hook),
        (T['sign'] - 0.3, T['card'] - 0.3, make_touch('sign')),
        (T['card'] - 0.3, T['website'] - 0.3, make_touch('card')),
        (T['website'] - 0.3, T['instagram'] - 0.3, make_touch('web')),
        (T['instagram'] - 0.3, T['invoice'] - 0.3, make_touch('insta')),
        (T['invoice'] - 0.3, T['invoice'] + 0.35, make_touch('invoice')),
        (T['invoice'] + 0.35, T['They'] - 0.05, sh_mess),
        (T['They'] - 0.05, T['So'] - 0.15, sh_reveal),
        (T['So'] - 0.15, T['Then'] - 0.15, sh_system),
        (T['Then'] - 0.15, T['A'] - 0.1, sh_snap),
        (T['A'] - 0.1, T['Build'] - 0.15, sh_line),
        (T['Build'] - 0.15, DUR + 1, sh_end),
    ]


SHOTS = None


# ------------------------------------------------------------------ transitions
def tr_jolt(a, b, p, d=1):
    """Jittery 'before' cut: the new shot slams in from the side with a slight rotation and overshoot."""
    e = e_out_back(min(1, p * 1.05), 1.4)
    off = (1 - e) * W * d
    ang = (1 - e) * 6 * d
    M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1.0)
    M[0, 2] += off
    B_ = cv2.warpAffine(b, M, (W, H), borderMode=cv2.BORDER_CONSTANT, borderValue=tuple(float(v) for v in OFF[:3]))
    m = cv2.warpAffine(np.ones((H, W), np.float32), M, (W, H))[..., None]
    return a * (1 - m) + B_ * m


def tr_cut(a, b, p):
    return a if p < 0.5 else b


def tr_thump(a, b, p):
    """Hard cut to black with a quick zoom punch."""
    if p < 0.35:
        return a
    z = 1 + 0.06 * (1 - prog(p, 0.35, 1.0))
    return cv2.warpAffine(b, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)


def tr_limewipe(a, b, p):
    e = e_inout_cubic(p)
    pos = lerp(-600, W + 700, e)
    d = (_X - pos) + (_Y - H / 2) * 0.45
    m = (d < 0).astype(np.float32)[..., None]
    band = ((d > -140) & (d < 0)).astype(np.float32)[..., None]
    out = a * (1 - m) + b * m
    return out * (1 - band) + np.array(LIME[:3], np.float32) * band


def tr_push(a, b, p):
    e = e_inout_cubic(p)
    off = int(e * H)
    out = np.empty_like(a)
    out[:H - off] = a[off:]
    out[H - off:] = b[:off]
    return out


def tr_flash(a, b, p):
    src = a if p < 0.5 else b
    k = 1 - abs(p - 0.5) * 2
    return np.clip(src + k ** 2 * np.array(LIME[:3], np.float32) * 0.6, 0, 1)


def tr_zoomout(a, b, p):
    e = e_inout_cubic(p)
    z = lerp(1.0, 0.7, e)
    A = cv2.warpAffine(a, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    return A * (1 - e) + b * e


TRANS = [(lambda a, b, p: tr_jolt(a, b, p, 1), 0.22), (lambda a, b, p: tr_jolt(a, b, p, -1), 0.22), (lambda a, b, p: tr_jolt(a, b, p, 1), 0.22),
         (lambda a, b, p: tr_jolt(a, b, p, -1), 0.22), (lambda a, b, p: tr_jolt(a, b, p, 1), 0.22), (tr_zoomout, 0.25), (tr_thump, 0.12),
         (tr_limewipe, 0.45), (tr_push, 0.4), (tr_flash, 0.3), (tr_zoomout, 0.45)]


def hits():
    out = [(T['same'], 1.0, 8), (T['van'], 0.6, 6)]
    for k in ('sign', 'card', 'website', 'instagram', 'invoice'):
        out.append((T[k], 0.7, 7))
    out += [(T['They'], 1.0, 0), (T['trust'], 0.6, 0), (T['logo'], 0.4, 0), (T['palette'], 0.4, 0), (T['typeface'], 0.4, 0),
            (T['sys2'], 0.5, 0), (T['identity'], 0.8, 0)]
    out += [(snap_time(j) + 0.02, 0.35, 0) for j in range(6)]
    return out


HITS = None


def energy(t):
    z, sx, sy, ca = 1.0, 0.0, 0.0, 0.0
    for th, pn, sh in HITS:
        d = t - th
        if 0 <= d < 0.28:
            e = (1 - d / 0.28) ** 2
            z += 0.025 * pn * e
            ca = max(ca, 2.5 * pn * e)
            if sh:
                sx += sh * e * math.sin(t * 97 + th)
                sy += sh * e * math.cos(t * 83 + th)
    return z, sx, sy, ca


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
    z, sx, sy, _ = energy(t)
    if z > 1.001 or abs(sx) + abs(sy) > 0.5:
        M = np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    if t > DUR - 0.6:
        c = c * (1 - 0.5 * e_inout_cubic(prog(t, DUR - 0.6, DUR)))
    return c


def render(fi):
    t = fi / FPS
    c = render_raw(t)
    _, _, _, ca = energy(t)
    return post(c, fi, bloom=0.08, grain=0.01, vig=0.12, ca=ca)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/sb_stills', exist_ok=True)
        for tt_ in sys.argv[2].split(','):
            t = float(tt_)
            cv2.imwrite(f'{S}/sb_stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 88])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/sb_out', exist_ok=True)
        for fi in range(a, b):
            p = f'{S}/sb_out/{fi:04d}.jpg'
            if os.environ.get('RESUME') and os.path.exists(p):
                continue
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_JPEG_QUALITY, 95])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print('DUR', DUR, 'NF', NF)
        print({k: round(v, 2) for k, v in T.items()})
