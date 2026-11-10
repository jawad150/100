"""Organic Fostering "Three of Me" (9:16, ~32 s). One woman, three versions of her (Worrier, Optimist, Realist), hard jump
cuts with punch-ins and colour-flash frames, every factor slapped on as a glossy 3D sticker on its spoken word, split
screen for "You ask.", end card. ElevenLabs voice (Ella), one voice in three moods.

Usage: python3 reel_three.py still 1.0,5.0 | python3 reel_three.py range 0 100 | python3 reel_three.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_three as G
from frames_three import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, IVORY, LAV,
                          LEAF, SLATE, WHITE, N9, N8, CHAR, sticker, grade, cover)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_inout_cubic, post

FPS = 30
S = G.S
OFF = 0.8
WORDS = [(w, a + OFF, b + OFF) for w, a, b in json.load(open(f'{S}/tts/info.json'))['words']]
DUR = 32.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y


def WT(i):
    return WORDS[i][1]


T = dict(work=WT(1), full=WT(2), so=WT(4), foster=WT(7), right=WT(8), Wait=WT(9), no=WT(15), The=WT(16), possibly=WT(20),
         It=WT(21), hours=WT(25), flexibility=WT(27), support=WT(29), childs=WT(33), needs=WT(34), Theres=WT(35), training=WT(36),
         meetings=WT(37), school=WT(38), some=WT(40), working=WT(42), Plan=WT(44), So=WT(47), know=WT(51), works=WT(54), You=WT(57),
         ask=WT(58), end=WORDS[-1][2])

# captions: (speaker, [lines of (word, index)], cue words)
LINES = [
    ('worrier', [[('I', 0), ('work', 1), ('full', 2), ('time.', 3)], [('So', 4), ('I', 5), ("can't", 6), ('foster,', 7), ('right?', 8)]], ('full', 'time', 'foster')),
    ('optimist', [[('Wait.', 9), ('Nobody', 10), ('said', 11), ("that's", 12)], [('an', 13), ('automatic', 14), ('no.', 15)]], ('automatic', 'no')),
    ('realist', [[('The', 16), ('honest', 17), ('answer', 18), ('is:', 19)], [('possibly.', 20)]], ('possibly',)),
    ('realist', [[('It', 21), ('depends', 22), ('on', 23), ('your', 24), ('hours,', 25)], [('your', 26), ('flexibility,', 27)]], ('hours', 'flexibility')),
    ('realist', [[('your', 28), ('support', 29), ('network', 30)], [('and', 31), ('the', 32), ("child's", 33), ('needs.', 34)]], ('support', 'network', "child's", 'needs')),
    ('optimist', [[("There's", 35), ('training,', 36)], [('meetings,', 37), ('school', 38), ('events…', 39)]], ('training', 'meetings', 'school', 'events')),
    ('realist', [[('…some', 40), ('in', 41), ('working', 42), ('hours.', 43)], [('Plan', 44), ('for', 45), ('that.', 46)]], ('working', 'hours', 'plan')),
    ('worrier', [[('So', 47), ('how', 48), ('do', 49), ('I', 50), ('know', 51)], [('if', 52), ('it', 53), ('works', 54), ('for', 55), ('me?', 56)]], ('works',)),
    ('all', [[('You', 57), ('ask.', 58)]], ()),
]
HL = {'worrier': SLATE, 'optimist': ORANGE, 'realist': PURPLE, 'all': ORANGE}


@functools.lru_cache(maxsize=512)
def wmask(w, size):
    return _wmask(w, N9, size)


@functools.lru_cache(maxsize=32)
def line_size(k, size=68):
    while size > 40:
        wmax = max(sum(wmask(w, size).shape[1] for w, _ in l) + size * 0.24 * (len(l) - 1) for l in LINES[k][1])
        if wmax <= W - 150:
            return size
        size -= 2
    return size


def captions(c, t, y=1450):
    for k, (who, lines, keys) in enumerate(LINES):
        t0 = WT(lines[0][0][1]) - 0.1
        t1 = WT(LINES[k + 1][1][0][0][1]) - 0.12 if k + 1 < len(LINES) else DUR
        if who == 'all' or not (t0 <= t < t1):
            continue
        size = line_size(k)
        for li, line in enumerate(lines):
            ms = [wmask(w, size) for w, _ in line]
            tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ms) - 1)
            x = W / 2 - tw / 2
            yy = y + li * size * 1.22
            for (w, i), m in zip(line, ms):
                ki = prog(t, WT(i) - 0.08, WT(i) + 0.12)
                if ki > 0:
                    cx = x + m.shape[1] / 2
                    if w.strip('.,?!…:').lower() in keys:
                        kh = e_out_back(prog(t, WT(i), WT(i) + 0.25), 2.0)
                        draw(c, rrect(m.shape[1] + 20, size * 1.12, 18, HL[who]), cx, yy + 3, scale=max(0.01, kh), rot=-2)
                    else:
                        draw(c, blur_sprite(solid(m, (0.1, 0.02, 0.08, 1)), 10), cx + 3, yy + 7, opacity=0.6 * ki)
                    sc = 1 + 0.25 * (1 - e_out_cubic(ki))
                    draw(c, solid(m, WHITE), cx, yy, scale=sc, opacity=min(1, ki * 2))
                x += m.shape[1] + size * 0.24


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
            return self.cache[max(self.cache)] if self.cache else np.zeros((720, 1280, 3), np.uint8)
        self.pos = i
        if len(self.cache) > 20:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def footage(cid, ct, kind, fx=0.5, fy=0.45, z=1.0, w=W, h=H):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    ct = ct % (_clips[cid].n / _clips[cid].fps - 0.1)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return grade(cover(im, fx, fy, z, w, h), kind)


# ------------------------------------------------------------------ animated pieces
def slap(c, name, x, y, size, t, t0, rot=-6, t1=None):
    """Sticker slapped on: drops in big from above the glass, lands with a snap and a little wobble."""
    k = prog(t, t0, t0 + 0.28)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.2) if t1 else 0
    if ko >= 1:
        return
    st = sticker(name, size)
    e = e_out_cubic(k)
    sc = lerp(1.6, 1.0, e) * (1 - 0.4 * ko)
    wob = 3 * math.sin((t - t0) * 9) * math.exp(-(t - t0) * 4) if k >= 1 else 0
    rr = rot + (1 - e) * 18 + wob
    sh_off = lerp(60, 16, e)
    op = min(1, k * 3) * (1 - ko)
    draw(c, blur_sprite(tint(st, (0.15, 0.05, 0.12)), 14), x + sh_off * 0.6, y + sh_off, scale=sc, rot=rr, opacity=0.45 * op)
    yy = y - (1 - e) * 30 + 4 * math.sin((t - t0) * 1.8) * (k >= 1)
    draw(c, st, x, yy, scale=sc, rot=rr, opacity=op)


def word_sticker(c, text, x, y, t, t0, fill=ORANGE, size=96, rot=-4):
    k = prog(t, t0, t0 + 0.28)
    if k <= 0:
        return
    tmp = np.zeros((H, W, 3), np.float32)
    s = ts(text, N9, size, WHITE, 0.01)
    p = rrect(s.shape[1] + 70, s.shape[0] + 40, 30, fill).copy()
    paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
    b = rrect(p.shape[1] + 26, p.shape[0] + 26, 42, WHITE).copy()
    paste_spr(b, p, b.shape[1] / 2, b.shape[0] / 2)
    e = e_out_cubic(k)
    sc = lerp(1.7, 1.0, e)
    rr = rot + (1 - e) * 14
    draw(c, blur_sprite(tint(b, (0.15, 0.05, 0.12)), 14), x + 10, y + lerp(60, 16, e), scale=sc, rot=rr, opacity=0.45 * min(1, k * 3))
    draw(c, b, x, y, scale=sc, rot=rr, opacity=min(1, k * 3))


def name_tag(c, kind, t, t0, x=70, y=330):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    label, col, _ = CHAR[kind]
    s = ts(label, N9, 40, WHITE, 0.08)
    p = rrect(s.shape[1] + 60, 74, 37, col).copy()
    paste_spr(p, s, p.shape[1] / 2, 37)
    e = e_out_back(k, 1.8)
    xx = x + p.shape[1] / 2 - (1 - e_out_cubic(k)) * 500
    draw(c, blur_sprite(tint(p, (0.1, 0.03, 0.08)), 12), xx + 6, y + 10, opacity=0.4 * min(1, k * 2))
    draw(c, p, xx, y, rot=-2 * (1 - k))


def clock_tag(c, t, t0, x=70, y=330):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    s = ts('5:30 PM', N9, 44, WHITE, 0.06)
    p = rrect(s.shape[1] + 60, 80, 40, (0.1, 0.05, 0.1, 0.72)).copy()
    paste_spr(p, s, p.shape[1] / 2, 40)
    draw(c, p, x + p.shape[1] / 2 - (1 - e_out_cubic(k)) * 400, y)


def strike(c, t, t0, a=(150, 1180), b=(520, 980)):
    k = e_out_cubic(prog(t, t0, t0 + 0.25))
    if k <= 0:
        return
    lay = np.zeros((H, W), np.uint8)
    p = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    cv2.line(lay, (int(a[0] * 4), int(a[1] * 4)), (int(p[0] * 4), int(p[1] * 4)), 255, 22 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(LEAF[:3], np.float32) * m


def zoom(c, z, cx=W / 2, cy=H * 0.42):
    if abs(z - 1) < 1e-3:
        return c
    return cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * cx], [0, z, (1 - z) * cy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)


# ------------------------------------------------------------------ shots
def sh_legs(t):
    c = footage(25890, 2.0 + t * 0.8, 'worrier', 0.5, 0.6, 1.05 + 0.02 * t)
    c = G.top_shade(c)
    clock_tag(c, t, 0.2)
    slap(c, 'briefcase', 300, 1050, 300, t, T['work'] - 0.05, rot=-8)
    slap(c, 'clock', 780, 760, 300, t, T['full'] - 0.05, rot=8)
    return G.shade(c)


def sh_wor1(t):
    t0 = SH['wor1'][0]
    c = footage(4833, 6.6 + (t - t0), 'worrier', 0.52, 0.45, 1.0 + 0.02 * (t - t0))
    c = G.top_shade(c)
    name_tag(c, 'worrier', t, t0 + 0.05)
    slap(c, 'mug', 840, 1050, 240, t, t0 + 0.25, rot=6)
    slap(c, 'house', 250, 720, 250, t, T['foster'] - 0.05, rot=-8)
    slap(c, 'question', 420, 560, 150, t, T['right'] - 0.05, rot=10)
    return G.shade(c)


def sh_opt1(t):
    t0 = SH['opt1'][0]
    c = footage(4869, 0.9 + (t - t0), 'optimist', 0.70, 0.45, 1.05)
    c = G.top_shade(c)
    name_tag(c, 'optimist', t, t0 + 0.05)
    slap(c, 'sun', 260, 640, 240, t, t0 + 0.2, rot=-8)
    slap(c, 'nostamp', 330, 1080, 330, t, T['no'] - 0.05, rot=-10)
    strike(c, t, T['no'] + 0.4)
    return G.shade(c)


def sh_rea1(t):
    t0 = SH['rea1'][0]
    c = footage(4834, 2.4 + (t - t0), 'realist', 0.52, 0.45, 1.0)
    c = G.top_shade(c)
    name_tag(c, 'realist', t, t0 + 0.05)
    slap(c, 'clipboard', 860, 1030, 250, t, t0 + 0.25, rot=8)
    slap(c, 'possibly', 300, 660, 260, t, T['possibly'] - 0.1, rot=-6)
    word_sticker(c, 'POSSIBLY.', 540, 1180, t, T['possibly'] + 0.05, fill=PURPLE)
    return G.shade(c)


FACTORS = [('clock', 210, 600, -8, 'hours', 'hours'), ('calendar', 870, 620, 7, 'flexibility', 'flexibility'),
           ('network', 220, 1110, 6, 'support network', 'support'), ('heart', 870, 1090, -6, "child's needs", 'childs')]


def sh_rea2(t):
    t0 = SH['rea2'][0]
    jump = t >= T['support'] - 0.15                                     # a jump cut mid-list: punch in
    c = footage(4834, (6.0 if not jump else 8.6) + (t - t0), 'realist', 0.52, 0.42, 1.12 if not jump else 1.28)
    c = G.top_shade(c)
    name_tag(c, 'realist', t, -10)
    for name, x, y, r, lab, key in FACTORS:
        slap(c, name, x, y, 230, t, T[key] - 0.05, rot=r)
        k = prog(t, T[key] + 0.1, T[key] + 0.35)
        if k > 0:
            s = ts(lab, N9, 34, WHITE)
            p = rrect(s.shape[1] + 40, 58, 29, PURPLE).copy()
            paste_spr(p, s, p.shape[1] / 2, 29)
            draw(c, p, x, y + 150, rot=r * 0.5, scale=e_out_back(k, 2.0), opacity=min(1, k * 2))
    return G.shade(c, 0.66)


def sh_opt2(t):
    t0 = SH['opt2'][0]
    c = footage(4869, 3.2 + (t - t0), 'optimist', 0.70, 0.45, 1.12)
    c = G.top_shade(c)
    name_tag(c, 'optimist', t, t0 + 0.03)
    slap(c, 'gradcap', 280, 640, 230, t, T['training'] - 0.05, rot=-8)
    slap(c, 'calendar', 820, 560, 210, t, T['meetings'] - 0.05, rot=6)
    slap(c, 'backpack', 300, 1060, 230, t, T['school'] - 0.05, rot=8)
    return G.shade(c)


def sh_rea3(t):
    t0 = SH['rea3'][0]
    c = footage(4834, 11.0 + (t - t0), 'realist', 0.52, 0.42, 1.15)
    c = G.top_shade(c)
    name_tag(c, 'realist', t, t0 + 0.03)
    slap(c, 'briefcase', 800, 640, 240, t, T['working'] - 0.05, rot=-6)
    slap(c, 'clipboard', 260, 1040, 240, t, T['Plan'] - 0.05, rot=6)
    word_sticker(c, 'PLAN FOR THAT.', 600, 1220, t, T['Plan'] + 0.2, fill=PURPLE, size=70, rot=-3)
    return G.shade(c)


def sh_wor2(t):
    t0 = SH['wor2'][0]
    z = 1.1 + 0.22 * e_inout_cubic(prog(t, t0, SH['wor2'][1]))       # the Worrier leans in
    c = footage(4833, 7.6 + (t - t0) * 0.8, 'worrier', 0.52, 0.40, z)
    c = G.top_shade(c)
    name_tag(c, 'worrier', t, t0 + 0.03)
    slap(c, 'magnifier', 800, 760, 280, t, T['know'] - 0.05, rot=10)
    return G.shade(c)


def sh_split(t):
    t0 = SH['split'][0]
    c = np.ones((H, W, 3), np.float32) * np.array(PLUM[:3], np.float32)
    pw = (W - 16) // 3
    for i, (kind, cid, ct, fx) in enumerate((('worrier', 4833, 7.6, 0.52), ('optimist', 4869, 11.0, 0.70), ('realist', 4834, 12.2, 0.52))):
        k = e_out_cubic(prog(t, t0 + i * 0.1, t0 + i * 0.1 + 0.3))
        if k <= 0:
            continue
        sub = footage(cid, ct + (t - t0), kind, fx, 0.42, 1.0, pw, 1240)
        x0 = i * (pw + 8)
        dy = int((1 - k) * (1300 if i % 2 == 0 else -1300))
        y0 = 200 + dy
        ya, yb = max(0, y0), min(H, y0 + 1240)
        if yb > ya:
            c[ya:yb, x0:x0 + pw] = sub[ya - y0:yb - y0]
        label, col, prop = CHAR[kind]
        s = ts(label.replace('THE ', ''), N9, 30, WHITE, 0.06)
        p = rrect(s.shape[1] + 34, 54, 27, col).copy()
        paste_spr(p, s, p.shape[1] / 2, 27)
        draw(c, p, x0 + pw / 2, 1390 + dy, opacity=k)
        slap(c, prop, x0 + pw / 2, 300, 150, t, t0 + 0.3 + i * 0.1, rot=(-8, 6, -4)[i])
    word_sticker(c, 'YOU ASK.', 540, 1560, t, T['ask'] - 0.05, fill=ORANGE, size=110, rot=-3)
    slap(c, 'phone', 900, 1560, 200, t, T['ask'] + 0.25, rot=10)
    return c


@functools.lru_cache(maxsize=1)
def CANVAS():
    return G.canvas()


@functools.lru_cache(maxsize=1)
def LOGO():
    return G.logo()


def sh_end(t):
    t0 = SH['end'][0]
    c = CANVAS().copy()
    lg = LOGO()
    kl = prog(t, t0, t0 + 0.4)
    draw(c, lg, W / 2, 470, scale=760 / lg.shape[1] * (0.9 + 0.1 * e_out_back(kl, 1.6)), opacity=kl)
    for j, (txt, col) in enumerate((('Ask us about fostering', PLUM), ('around your work', PURPLE))):
        k = prog(t, t0 + 0.3 + j * 0.15, t0 + 0.6 + j * 0.15)
        if k > 0:
            draw(c, ts(txt, N9, 70, col), W / 2, 760 + j * 90 + (1 - e_out_cubic(k)) * 30, opacity=k)
    kb = prog(t, t0 + 0.7, t0 + 1.1)
    if kb > 0:
        pulse = 1 + 0.025 * math.sin((t - t0) * 4) * prog(t, t0 + 1.4, t0 + 1.8)
        e = e_out_back(kb, 2.0) * pulse
        btn = G.grad_spr(700, 130, 65, phase=(t * 0.12) % 1)
        draw(c, blur_sprite(btn, 24), W / 2, 1035, scale=e, opacity=0.5 * min(1, kb * 2))
        draw(c, btn, W / 2, 1015, scale=e)
        tmp = np.zeros((150, 720, 4), np.float32)
        s = ts('Start your enquiry', N9, 52, WHITE)
        paste_spr(tmp, s, 360 - 24, 75)
        tri = np.zeros((44, 36), np.uint8)
        cv2.fillPoly(tri, [np.array([[4, 4], [4, 40], [32, 22]])], 255, cv2.LINE_AA)
        paste_spr(tmp, solid(tri.astype(np.float32) / 255, WHITE), 360 + s.shape[1] / 2 + 6 + 6 * max(0, math.sin((t - t0) * 5)), 75)
        draw(c, tmp, W / 2, 1015, scale=e)
        sw = prog(t, t0 + 1.5, t0 + 2.2)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(200, 880, sw) - (_Y - 1015) * 0.4) / 36) ** 2) * (np.abs(_Y - 1015) < 62)
            c = np.clip(c + band[..., None] * 0.35, 0, 1)
    kp = prog(t, t0 + 1.0, t0 + 1.4)
    if kp > 0:
        draw(c, ts('0161 241 1332', N9, 72, PURPLE), W / 2, 1200 + (1 - kp) * 20, opacity=kp)
        draw(c, ts('organicfostering.co.uk', N8, 42, PLUM), W / 2, 1285 + (1 - kp) * 20, opacity=kp)
    for j, (name, x, y, r) in enumerate((('mug', 200, 1520, -8), ('sun', 540, 1560, 4), ('clipboard', 880, 1520, 8))):
        slap(c, name, x, y, 200, t, t0 + 1.3 + j * 0.15, rot=r)
    return c


def build_shots():
    s = {}
    s['legs'] = (0.0, T['so'] - 0.15)
    s['wor1'] = (s['legs'][1], T['Wait'] - 0.1)
    s['opt1'] = (s['wor1'][1], T['The'] - 0.15)
    s['rea1'] = (s['opt1'][1], T['It'] - 0.1)
    s['rea2'] = (s['rea1'][1], T['Theres'] - 0.12)
    s['opt2'] = (s['rea2'][1], T['some'] - 0.1)
    s['rea3'] = (s['opt2'][1], T['So'] - 0.1)
    s['wor2'] = (s['rea3'][1], T['You'] - 0.15)
    s['split'] = (s['wor2'][1], T['end'] + 1.3)
    s['end'] = (s['split'][1], DUR + 1)
    return s


SH = build_shots()
ORDER = ['legs', 'wor1', 'opt1', 'rea1', 'rea2', 'opt2', 'rea3', 'wor2', 'split', 'end']
FN = dict(legs=sh_legs, wor1=sh_wor1, opt1=sh_opt1, rea1=sh_rea1, rea2=sh_rea2, opt2=sh_opt2, rea3=sh_rea3, wor2=sh_wor2,
          split=sh_split, end=sh_end)
KIND = dict(legs='worrier', wor1='worrier', opt1='optimist', rea1='realist', rea2='realist', opt2='optimist', rea3='realist',
            wor2='worrier', split='all', end='all')


# ------------------------------------------------------------------ cuts: hard jump cuts with a colour flash and a punch-in
def cut_fx(c, t):
    """Right after each cut: two frames of the new character's colour flash, then a punch-in that settles."""
    for nm in ORDER[1:]:
        a = SH[nm][0]
        d = t - a
        if 0 <= d < 0.35:
            col = CHAR.get(KIND[nm], ('', ORANGE, ''))[1]
            if d < 2.0 / FPS:
                c = c * 0.45 + np.array(col[:3], np.float32) * 0.55
            z = 1 + 0.08 * (1 - e_out_cubic(d / 0.35))
            c = zoom(c, z)
            if d < 0.12:                                                   # quick chromatic snap
                sh = int(14 * (1 - d / 0.12))
                c = c.copy()
                c[..., 0] = np.roll(c[..., 0], sh, 1)
                c[..., 2] = np.roll(c[..., 2], -sh, 1)
    return c


def tr_peel(a, b, p):
    """The split screen peels away like a sticker to reveal the end card."""
    e = e_inout_cubic(p)
    edge = lerp(-200, W + H * 0.6 + 200, e) - _Y * 0.6
    m = (_X < edge).astype(np.float32)[..., None]
    rim = np.clip(1 - np.abs(_X - edge) / 40, 0, 1)[..., None]
    out = b * m + a * (1 - m)
    return np.clip(out * (1 - rim * 0.5) + rim * 0.5, 0, 1)


def hits():
    return [(T['full'], 0.5), (T['foster'], 0.5), (T['no'], 0.8), (T['possibly'], 0.8), (T['hours'], 0.4), (T['flexibility'], 0.4),
            (T['support'], 0.4), (T['childs'], 0.4), (T['training'], 0.4), (T['meetings'], 0.4), (T['school'], 0.4), (T['Plan'], 0.5),
            (T['know'], 0.4), (T['ask'], 0.9)]


HITS = hits()


def energy(t):
    z = 1.0
    for th, pn in HITS:
        d = t - th
        if 0 <= d < 0.25:
            z += 0.025 * pn * (1 - d / 0.25) ** 2
    return z


def render_raw(t):
    a = SH['end'][0]
    td = 0.5
    if a - td / 2 <= t < a + td / 2:
        c = tr_peel(FN['split'](min(t, a - 0.01)), FN['end'](max(t, a)), (t - (a - td / 2)) / td)
    else:
        c = None
        for nm in ORDER:
            s0, s1 = SH[nm]
            if s0 <= t < s1:
                c = FN[nm](t)
                break
        if c is None:
            c = FN['end'](t)
        c = cut_fx(c, t)
    c = zoom(c, energy(t), W / 2, H / 2)
    c = np.ascontiguousarray(c, dtype=np.float32)
    captions(c, t)
    fo = prog(t, DUR - 1.2, DUR)
    if fo > 0:
        c = c * (1 - 0.5 * e_inout_cubic(fo)) + np.array(IVORY[:3], np.float32) * 0.5 * e_inout_cubic(fo)
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.08, grain=0.01, vig=0.14)


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
        print({k: (round(a, 2), round(b, 2)) for k, (a, b) in SH.items()})
