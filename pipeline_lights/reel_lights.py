"""BMHC — "Lights On" (people version, 9:16). One day in the 1843 building, Fajr to Isha: every room appears the moment
its light switches on (flicker, flare, warm grade), with the people who use it. Day dial, building icon, word-synced 3D
props, room pills and Poppins captions.

Usage: python3 reel_lights.py still 1.0,5.0 | python3 reel_lights.py range 0 100 | python3 reel_lights.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_bmhc'))
import numpy as np
import cv2
import frames_lights as L
import frames_bmhc as F
from frames_bmhc import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, GREEN_D, IVORY, TEAL, GOLD, MAG, WHITE,
                         PB, PX, PS, PM)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = L.S
INFO = json.load(open(f'{S}/tts/lines/info.json'))
ORDER = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'l10', 'l11', 'l12', 'l13']
GAP = {'l2': 0.45, 'l3': 0.35, 'l4': 0.55, 'l11': 0.55, 'l12': 0.45, 'l13': 0.35}
VO = {}
_t = 0.6
for _k in ORDER:
    if _k != 'l1':
        _t += GAP.get(_k, 0.32)
    VO[_k] = round(_t, 3)
    _t += INFO['dur'][_k]
DUR = round(_t + 2.2, 2)
NF = int(DUR * FPS)
FADE = 1.0
_X, _Y = R._X, R._Y


def P(line, i):
    return VO[line] + INFO['phrases'][line][i][0]


def PD(line, i):
    return INFO['phrases'][line][i][1]


def WT(line, i, f):
    return P(line, i) + PD(line, i) * f


def END(line):
    return VO[line] + INFO['dur'][line]


# ------------------------------------------------------------------ sources
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
            return self.cache.get(max(self.cache) if self.cache else 0)
        self.pos = i
        if len(self.cache) > 60:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def cover(im, k, fx, fy, z0, z1, w=W, h=H, drift=(0, 0)):
    ih, iw = im.shape[:2]
    z = lerp(z0, z1, e_inout_cubic(k))
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    cx = fx * iw + drift[0] * k * iw
    cy = fy * ih + drift[1] * k * ih
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(cy - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    out = cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if sc > 1.6:
        bl = cv2.GaussianBlur(out, (0, 0), 1.5)
        out = np.clip(out * 1.45 - bl * 0.45, 0, 1)
    return out


def footage(cid, tl, start=0.3, fx=0.5, fy=0.5, z0=1.0, z1=1.08, dur=4.0, w=W, h=H):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    c = _clips[cid]
    im = c.frame(start * c.n / c.fps + max(0, tl)).astype(np.float32)[..., ::-1] / 255
    return cover(im, clamp(tl / dur), fx, fy, z0, z1, w, h)


@functools.lru_cache(maxsize=10)
def _photo(name):
    im = cv2.imread(f'{F.IMG}/{name}', cv2.IMREAD_COLOR)
    if max(im.shape[:2]) > 2600:
        s = 2600 / max(im.shape[:2])
        im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return np.ascontiguousarray(im[..., ::-1].astype(np.float32) / 255)


def still(name, tl, fx=0.5, fy=0.5, z0=1.0, z1=1.1, dur=4.0, w=W, h=H, drift=(0, 0)):
    return cover(_photo(name), clamp(tl / dur), fx, fy, z0, z1, w, h, drift)


@functools.lru_cache(maxsize=1)
def FACADE():
    return L.photo('bhmc-f.png', 0.5, 0.5)


@functools.lru_cache(maxsize=16)
def P3(name):
    return L.prop(name)


@functools.lru_cache(maxsize=1)
def LOGO():
    return F.logo()


# ------------------------------------------------------------------ light switching
def flick(t, ton, dur=0.32):
    """0 → 1 with a fluorescent flicker (on, dip, on)."""
    if t < ton:
        return 0.0
    d = t - ton
    if d > dur:
        return 1.0
    seq = [(0.0, 0.0), (0.05, 0.85), (0.09, 0.2), (0.14, 0.95), (0.19, 0.55), (0.24, 1.0), (dur, 1.0)]
    for (a, va), (b, vb) in zip(seq, seq[1:]):
        if a <= d <= b:
            return lerp(va, vb, (d - a) / max(1e-6, b - a))
    return 1.0


def lights(dark_src, lit, k):
    if k >= 1:
        return lit
    dark = dark_src * 0.28 + np.array([0.01, 0.025, 0.05], np.float32)
    return dark * (1 - k) + lit * k


def flare(c, x, y, t, ton, col=(1.0, 0.85, 0.55), size=1.0):
    d = t - ton
    if not 0 <= d < 0.7:
        return
    a = math.sin(math.pi * min(1, d / 0.7)) * 0.8
    g = np.exp(-((_X - x) ** 2 + (_Y - y) ** 2) / (2 * (150 * size) ** 2))[..., None]
    streak = np.exp(-((_Y - y) / (14 * size)) ** 2 - ((_X - x) / (520 * size)) ** 2)[..., None]
    c[:] = np.clip(c + (g * 0.9 + streak * 0.6) * a * np.array(col, np.float32), 0, 1)


# ------------------------------------------------------------------ animated overlays
def rays(c, x, y, r0, kr, col=GOLD, n=12):
    if not 0 < kr < 1:
        return
    lay = np.zeros((H, W), np.uint8)
    r = r0 + 32 * kr
    for j in range(n):
        a = j / n * 2 * math.pi + 0.15
        ln = (30 if j % 2 else 46) * (1 - kr)
        cv2.line(lay, (int((x + math.cos(a) * r) * 4), int((y + math.sin(a) * r) * 4)),
                 (int((x + math.cos(a) * (r + ln)) * 4), int((y + math.sin(a) * (r + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * (1 - kr)
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def pop_in(c, spr, x, y, sc, t, t0, ray=True, float_amp=8):
    k = prog(t, t0, t0 + 0.38)
    if k <= 0:
        return
    e = e_out_back(k, 2.4)
    yy = y + float_amp * math.sin((t - t0) * 2.2) + (1 - e_out_cubic(k)) * 50
    rot = (1 - k) * -16 + 3 * math.sin((t - t0) * 1.7)
    if ray:
        rays(c, x, yy, max(spr.shape[:2]) * sc * 0.45, prog(t, t0, t0 + 0.45))
    draw(c, blur_sprite(tint(spr, (0.0, 0.05, 0.04)), 18), x + 8, yy + 22, scale=sc * e, rot=rot, opacity=0.4 * min(1, k * 2))
    draw(c, spr, x, yy, scale=sc * e, rot=rot, opacity=min(1, k * 2.5))


def pill_in(c, text, t, t0, x=None, y=1470, dark=False):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return
    tmp_c = c
    s = ts(text.upper(), PS, 30, GREEN_D if not dark else IVORY, 0.12)
    w = s.shape[1] + 60
    x = W / 2 if x is None else x
    e = e_out_back(k, 2.0)
    fill = (*IVORY[:3], 0.95) if not dark else (*GREEN_D[:3], 0.85)
    draw(c, rrect(w, 66, 33, fill), x, y + (1 - e_out_cubic(k)) * 24, scale=0.8 + 0.2 * e, opacity=min(1, k * 2))
    draw(c, s, x, y + (1 - e_out_cubic(k)) * 24, scale=0.8 + 0.2 * e, opacity=min(1, k * 2))


@functools.lru_cache(maxsize=512)
def cap_word(w, size, gold):
    return solid(_wmask(w, 'Poppins-Bold', size), GOLD if gold else WHITE)


def caption(c, t, phrases, size=62, y=1650, keys=(), maxw=940):
    """Word-synced Poppins Bold captions, centred, white with soft shadow; key words in gold."""
    words = []
    for line, i in phrases:
        ws = INFO['phrases'][line][i][2].replace('Koran', "Qur'an").replace('G C S E', 'GCSE').replace('eighteen forty-three', '1843') \
            .replace('twenty-four', '24').split(' ')
        t0, d = P(line, i), PD(line, i)
        total = sum(len(w) + 1 for w in ws)
        acc = 0
        for w in ws:
            words.append((w, t0 + d * 0.8 * acc / total))
            acc += len(w) + 1
    if not words or t < words[0][1] - 0.1:
        return
    rows, cur, x = [], [], 0
    for w, ton in words:
        g = w.strip('.,!?').lower() in keys
        wd = cap_word(w, size, g).shape[1]
        if cur and x + wd > maxw:
            rows.append((cur, x - size * 0.22))
            cur, x = [], 0
        cur.append((w, ton, x, g))
        x += wd + size * 0.22
    rows.append((cur, x - size * 0.22))
    y0 = y - (len(rows) - 1) * size * 1.25 / 2
    for li, (row, rw) in enumerate(rows):
        yy = y0 + li * size * 1.25
        x0 = W / 2 - rw / 2
        for w, ton, x, g in row:
            k = prog(t, ton, ton + 0.2)
            if k <= 0:
                continue
            s = cap_word(w, size, g)
            e = e_out_cubic(k)
            draw(c, blur_sprite(tint(s, (0, 0, 0)), 12), x0 + x + s.shape[1] / 2 + 2, yy + 6 + (1 - e) * 22, opacity=0.7 * k)
            draw(c, s, x0 + x + s.shape[1] / 2, yy + (1 - e) * 22, opacity=min(1, k * 2))


def dial(c, t, k0, k1, t0, t1, show=1.0):
    if show <= 0:
        return
    k = lerp(k0, k1, e_inout_cubic(prog(t, t0, t1)))
    if show < 1:
        tmp = c.copy()
        L.day_dial(tmp, k)
        c[:] = c * (1 - show) + tmp * show
    else:
        L.day_dial(c, k)


def bicon(c, t, lit_before, t_on):
    lit = lit_before + (1 if t >= t_on else 0)
    L.building_icon(c, lit)
    k = prog(t, t_on, t_on + 0.4)
    if 0 < k < 1:
        rays(c, 950, 270, 70, k, col=GOLD, n=10)


def grade_bottom(c, amt=0.75, top=0.55):
    return L.bottom(L.topfade(c), amt, top)


# ------------------------------------------------------------------ shots
def sh_gates(t):
    c = L.warm(still('W6A9208-1-scaled.jpg', t, 0.52, 0.5, 1.12, 1.0, 3.6), 0.6)
    flare(c, 880, 260, t, 0.25, size=1.4)
    c = grade_bottom(c)
    k = prog(t, P('l1', 1), P('l1', 1) + 0.45)
    if k > 0:
        F.tag(c, 'COLLEGE ROAD · WHALLEY RANGE', 70 - (1 - e_out_cubic(k)) * 700, 290, icon='pin')
    caption(c, t, [('l1', 0), ('l1', 1)], keys=('gates.',))
    return c


def sh_1843(t):
    t0 = P('l2', 0)
    src = FACADE()
    base = np.clip(L.night(src) * 1.6, 0, 1)
    kz = clamp((t - t0 + 0.4) / 4.5)
    tw = WT('l2', 0, 0.6)
    c = base.copy()
    kw = flick(t, tw)
    if kw > 0:
        L.light_windows(c, src, n=2, amt=kw)
    z = lerp(1.0, 1.08, e_inout_cubic(kz))
    M = np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H * 0.4]])
    c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    flare(c, 490, 680, t, tw)
    c = L.bottom(c, 0.6)
    k = prog(t, tw, tw + 0.4)
    if k > 0:
        n = int(lerp(1800, 1843, e_out_cubic(prog(t, tw, tw + 0.7))))
        s = ts(str(n), PB, 300, GOLD)
        e = e_out_back(k, 2)
        draw(c, blur_sprite(tint(s, (0, 0, 0)), 20), W / 2 + 8, 1330, scale=e, opacity=0.6 * k)
        draw(c, s, W / 2, 1320, scale=e)
    kc = prog(t, tw + 0.5, tw + 0.85)
    if kc > 0:
        F.chip(c, 'Grade II* listed', W / 2, 1490, fill=IVORY, ink=GREEN_D, size=38)
    pop_in(c, _old_card(), 800, 560, 1.0, t, P('l2', 1))
    bicon(c, t, 0, tw)
    caption(c, t, [('l2', 0), ('l2', 1)], y=1690, keys=('1843,', 'college.'))
    return c


@functools.lru_cache(maxsize=1)
def _old_card():
    old = F.photo('BMHC-Year-1866.jpg', fx=0.55, fy=0.5, w=420, h=290, g=False)
    old = old.mean(2, keepdims=True) * np.array([1.0, 0.94, 0.82], np.float32)
    card = rrect(444, 314, 24, IVORY).copy()
    paste_spr(card, F.sprite_of(old, 16), 222, 157)
    return card


def sh_learning(t):
    t0 = P('l3', 0)
    src = still('1-BMHC-web.jpg', t - t0, 0.5, 0.5, 1.0, 1.08, 3.0)
    lit = src * 0.75
    L.lamp_light(lit, 540, 1300, 560, 0.9)
    L.lamp_light(lit, 138, 1220, 200, 0.9)
    lit = L.warm(lit)
    ton = WT('l3', 0, 0.25)
    c = lights(src, lit, flick(t, ton))
    flare(c, 540, 1300, t, ton)
    c = grade_bottom(c, 0.7, 0.6)
    dial(c, t, 0.08, 0.1, t0, t0 + 2, show=prog(t, t0, t0 + 0.5))
    pop_in(c, P3('bulb'), 540, 1060, 0.42, t, WT('l3', 0, 0.75))
    bicon(c, t, 1, ton)
    pill_in(c, 'Still a place of learning', t, WT('l3', 0, 0.5))
    caption(c, t, [('l3', 0)], keys=('learning!',))
    return c


def sh_fajr(t):
    t0 = P('l4', 0)
    src = still('MAS09785-scaled.jpg', t - t0, 0.5, 0.45, 1.08, 1.0, 4.0)
    c = L.dawn(src)
    ton = P('l4', 1)
    for j in range(3):
        kj = flick(t, ton + j * 0.25)
        if kj > 0:
            tmp = c.copy()
            L.ceiling_rows(tmp, 1, 140 + j * 90, 0.8)
            c = c * (1 - kj) + tmp * kj
    kl = prog(t, ton, ton + 1.0)
    if kl > 0:
        L.lamp_light(c, 540, 300, 700, 0.45 * kl, (0.85, 0.9, 1.0))
    c = L.bottom(c, 0.7)
    dial(c, t, 0.0, 0.0, t0, t0 + 1)
    pop_in(c, P3('switch_on') if t > ton else P3('switch_off'), 880, 560, 0.32, t, t0 + 0.2)
    bicon(c, t, 2, ton)
    pill_in(c, 'Daily prayers', t, ton + 0.3)
    caption(c, t, [('l4', 0), ('l4', 1)], keys=('fajr.',))
    return c


def sh_classes(t):
    t0 = P('l5', 0)
    src = still('Screenshot-2025-10-26-033526.png', t - t0, 0.3, 0.5, 1.0, 1.08, 5.0)
    lit = L.warm(src)
    L.lamp_light(lit, 300, 300, 700, 0.35)
    ton = t0 + 0.15
    c = lights(src, lit, flick(t, ton))
    flare(c, 300, 300, t, ton)
    c = grade_bottom(c, 0.75, 0.5)
    dial(c, t, 0.0, 0.18, t0, t0 + 1.2)
    pop_in(c, P3('rehal'), 830, 600, 0.5, t, P('l5', 1))
    bicon(c, t, 3, ton)
    pill_in(c, "Qur'an classes", t, P('l5', 1) + 0.2, x=330, y=1380)
    pill_in(c, 'GCSE Islamic Studies', t, P('l5', 2) + 0.3, x=640, y=1470)
    caption(c, t, [('l5', 0), ('l5', 1), ('l5', 2)], size=56, keys=("qur'an", 'gcse'))
    return c


def sh_sport(t):
    t0 = P('l6', 0)
    src = footage(48142, t - t0, 0.62, 0.55, 0.5, 1.05, 1.0, 3.0)
    lit = L.warm(src)
    ton = t0 + 0.1
    c = lights(src, lit, flick(t, ton))
    flare(c, 540, 300, t, ton, size=1.3)
    c = grade_bottom(c, 0.7, 0.6)
    dial(c, t, 0.18, 0.38, t0, t0 + 1.2)
    pop_in(c, P3('belt'), 860, 620, 0.5, t, P('l6', 1))
    bicon(c, t, 4, ton)
    pill_in(c, 'Taekwondo', t, P('l6', 1) + 0.15)
    caption(c, t, [('l6', 0), ('l6', 1)], keys=('taekwondo!',))
    return c


def sh_radio(t):
    t0 = P('l7', 0)
    src = footage(2957, t - t0, 0.3, 0.42, 0.5, 1.0, 1.06, 5.0) * 0.85
    lit = src.copy()
    ton = t0 + 0.2
    kr = flick(t, ton)
    if kr > 0:
        L.lamp_light(lit, 860, 360, 420, 0.5 * kr, (1.0, 0.35, 0.3))
    c = lights(src, lit, min(1, 0.4 + kr))
    c = grade_bottom(c, 0.75, 0.55)
    dial(c, t, 0.38, 0.5, t0, t0 + 1.2)
    pop_in(c, P3('clock'), 870, 1180, 0.38, t, P('l7', 2))
    k = prog(t, P('l7', 2), P('l7', 2) + PD('l7', 2) * 0.8)
    if k > 0:
        s = ts('%02d HOURS' % int(round(24 * e_out_cubic(k))), PB, 44, GOLD)
        draw(c, s, 870, 1320, opacity=min(1, k * 3))
    bicon(c, t, 5, ton)
    pill_in(c, 'Heritage Radio', t, P('l7', 1) + 0.2)
    caption(c, t, [('l7', 0), ('l7', 1), ('l7', 2)], size=56, keys=('heritage', 'radio', '24'))
    return c


def sh_youth(t):
    t0 = P('l8', 0)
    t1 = P('l8', 1)
    c = np.zeros((H, W, 3), np.float32) + np.array([0.03, 0.07, 0.06], np.float32)
    kt = e_out_cubic(prog(t, t0 - 0.1, t0 + 0.35))
    if kt > 0:
        top = L.warm(footage(5333, t - t0, 0.4, 0.5, 0.5, 1.0, 1.06, 3.0, w=W, h=H // 2))
        yoff = int((1 - kt) * -H // 2)
        a, b = max(0, yoff), H // 2 + yoff
        c[a:max(a, b)] = top[H // 2 - (b - a):] if b > a else c[a:a]
    kb = e_out_cubic(prog(t, t1 - 0.1, t1 + 0.35))
    if kb > 0:
        bot = L.warm(still('scouts.jpg', t - t1, 0.5, 0.4, 1.06, 1.0, 2.5, w=W, h=H // 2))
        yoff = int((1 - kb) * H // 2)
        c[H // 2 + yoff:] = bot[:H // 2 - yoff]
    if kt > 0.5:
        c[H // 2 - 4:H // 2 + 4] = np.array(GOLD[:3], np.float32)
    c = grade_bottom(c, 0.75, 0.62)
    dial(c, t, 0.5, 0.66, t0, t0 + 1.2)
    pop_in(c, P3('dice'), 860, 640, 0.4, t, t0 + 0.25)
    pop_in(c, P3('compass'), 200, 1220, 0.4, t, t1 + 0.2)
    pill_in(c, 'Youth club', t, t0 + 0.3, x=250, y=880)
    pill_in(c, 'Muslim scouts', t, t1 + 0.3, x=800, y=1080)
    bicon(c, t, 6, t0 + 0.2)
    caption(c, t, [('l8', 0), ('l8', 1)], y=1670, keys=('youth', 'scouts.'))
    return c


def sh_open(t):
    t0 = P('l9', 0)
    src = still('476280551_1049256607242153_4186426492440189340_n.jpg', t - t0, 0.5, 0.5, 1.12, 1.0, 4.0)
    lit = L.warm(src)
    ton = t0 + 0.1
    c = lights(src, lit, flick(t, ton))
    flare(c, 700, 400, t, ton)
    c = grade_bottom(c, 0.75, 0.5)
    dial(c, t, 0.66, 0.72, t0, t0 + 1)
    pop_in(c, P3('tea'), 820, 640, 0.48, t, t0 + 0.35)
    bicon(c, t, 7, ton)
    pill_in(c, 'Open days · all welcome', t, WT('l9', 0, 0.5))
    caption(c, t, [('l9', 0), ('l9', 1)], keys=('every', 'faith,', 'none.'))
    return c


def sh_friday(t):
    t0 = P('l10', 0)
    src = still('Screenshot-2025-10-26-055143.png', t - t0, 0.5, 0.5, 1.0, 1.1, 3.6)
    lit = L.warm(src)
    L.lamp_light(lit, 540, 500, 700, 0.3)
    ton = t0 + 0.1
    c = lights(src, lit, flick(t, ton))
    c = grade_bottom(c, 0.75, 0.5)
    dial(c, t, 0.72, 0.25, t0, t0 + 0.8)
    k = prog(t, t0 + 0.15, t0 + 0.45)
    if k > 0:
        F.chip(c, 'FRIDAY', 230, 560 + (1 - e_out_cubic(k)) * 40, fill=GOLD, ink=GREEN_D, size=48, rot=-4)
    bicon(c, t, 8, ton)
    pill_in(c, 'Friday khutbah in English', t, P('l10', 1) + 0.2)
    caption(c, t, [('l10', 0), ('l10', 1)], keys=('friday,', 'english.'))
    return c


def sh_night(t):
    t0 = P('l11', 0)
    src = FACADE()
    c = np.clip(L.night(src) * 1.25, 0, 1)
    n = int(clamp((t - t0) / (P('l11', 1) - t0 + 0.2)) * len(L.WINDOWS))
    if n:
        L.light_windows(c, src, n=n)
    if t > t0 + 0.3:
        for (x, y) in ((138, 1210), (888, 1260)):
            L.lamp_light(c, x, y, 160, 0.9 * flick(t, t0 + 0.3))
    z = lerp(1.1, 1.0, e_inout_cubic(clamp((t - t0) / 4)))
    M = np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H * 0.45]])
    c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    c = L.bottom(np.clip(c, 0, 1), 0.6)
    dial(c, t, 0.25, 1.0, t0, t0 + 1.6)
    L.building_icon(c, 9)
    caption(c, t, [('l11', 0), ('l11', 1)], size=58, keys=('donations',))
    return c


@functools.lru_cache(maxsize=9)
def grid_tile(j):
    kind, src = L.GRID[j]
    cw, ch = 300, 400
    if kind == 'photo':
        im = L.photo(src, fx=0.3 if '033526' in str(src) else 0.5, w=cw, h=ch)
    else:
        im = L.clip(src, 0.5, fx=0.42 if src == 2957 else 0.5, w=cw, h=ch)
    return L.warm(im)


def sh_grid(t):
    t0 = P('l12', 0)
    c = np.zeros((H, W, 3), np.float32) + np.array([0.03, 0.08, 0.1], np.float32)
    cw, ch, gap = 300, 400, 26
    x0 = (W - 3 * cw - 2 * gap) / 2 + cw / 2
    y0 = 330
    order = [4, 0, 8, 2, 6, 1, 7, 3, 5]
    for rank, j in enumerate(order):
        tj = t0 - 0.35 + rank * 0.09
        k = flick(t, tj, 0.28)
        x = x0 + (j % 3) * (cw + gap)
        y = y0 + (j // 3) * (ch + gap)
        im = grid_tile(j)
        im = im * (0.25 + 0.75 * k) + np.array([0.02, 0.04, 0.06], np.float32) * (1 - k)
        if k > 0.5:
            draw(c, blur_sprite(rrect(cw + 30, ch + 30, 20, (1.0, 0.72, 0.35, 0.8)), 22), x, y, opacity=k)
        fr = rrect(cw + 14, ch + 14, 16, (*GOLD[:3], 0.3 + 0.7 * k)).copy()
        paste_spr(fr, F.sprite_of(im.astype(np.float32), 10), (cw + 14) / 2, (ch + 14) / 2)
        draw(c, fr, x, y)
    ts_ = t0 + 0.55
    pop_in(c, P3('switch_on') if t > ts_ else P3('switch_off'), 540, 1480, 0.24, t, t0 - 0.2, ray=t > ts_)
    flare(c, 540, 1480, t, ts_, size=1.6)
    caption(c, t, [('l12', 0)], size=86, y=1680, keys=('lights', 'on.'))
    return c


def sh_end(t):
    t0 = P('l13', 0)
    src = FACADE()
    c = np.clip(L.night(src) * 1.15, 0, 1)
    L.light_windows(c, src)
    g = np.clip((_Y / H - 0.42) / 0.3, 0, 1)[..., None]
    c = c * (1 - 0.9 * g) + np.array(GREEN_D[:3], np.float32) * 0.9 * g
    pop_in(c, LOGO(), W / 2, 1010, 0.8, t, t0 - 0.3, ray=False, float_amp=3)
    k = prog(t, t0 - 0.1, t0 + 0.3)
    if k > 0:
        tmp = c.copy()
        L.cap_text(tmp, ['Help keep the lights on.'], y=1220, size=70, hl=('lights', 'on.'))
        c = c * (1 - k) + tmp * k
    kb = prog(t, t0 + 0.2, t0 + 0.55)
    if kb > 0:
        e = e_out_back(kb, 2)
        draw(c, blur_sprite(rrect(780, 120, 60, (0, 0, 0, 0.6)), 20), W / 2 + 6, 1400, scale=e, opacity=0.5)
        draw(c, rrect(780, 120, 60, GOLD), W / 2, 1380, scale=e)
        draw(c, ts('Become a Friend of the Centre', PB, 44, GREEN_D), W / 2, 1380, scale=e)
        rays(c, W / 2, 1380, 400, prog(t, t0 + 0.2, t0 + 0.7))
    k2 = prog(t, t0 + 0.6, t0 + 1.0)
    if k2 > 0:
        draw(c, ts('bmhc.org.uk/friend-of-the-centre', PS, 36, IVORY), W / 2, 1520, opacity=k2)
        draw(c, ts('Registered charity 1110104', PM, 26, (*IVORY[:3], 0.7)), W / 2, 1580, opacity=k2)
        F.bars(c, W / 2 - 200, 1660, 400 * e_out_cubic(k2), 10, 8)
    pop_in(c, P3('switch_on'), 890, 560, 0.3, t, t0 + 0.1)
    return c


def shots():
    return [(0.0, P('l2', 0) - 0.15, sh_gates), (P('l2', 0) - 0.15, P('l3', 0) - 0.1, sh_1843), (P('l3', 0) - 0.1, P('l4', 0) - 0.2, sh_learning),
            (P('l4', 0) - 0.2, P('l5', 0) - 0.1, sh_fajr), (P('l5', 0) - 0.1, P('l6', 0) - 0.1, sh_classes),
            (P('l6', 0) - 0.1, P('l7', 0) - 0.1, sh_sport), (P('l7', 0) - 0.1, P('l8', 0) - 0.15, sh_radio),
            (P('l8', 0) - 0.15, P('l9', 0) - 0.1, sh_youth), (P('l9', 0) - 0.1, P('l10', 0) - 0.1, sh_open),
            (P('l10', 0) - 0.1, P('l11', 0) - 0.2, sh_friday), (P('l11', 0) - 0.2, P('l12', 0) - 0.4, sh_night),
            (P('l12', 0) - 0.4, P('l13', 0) - 0.35, sh_grid), (P('l13', 0) - 0.35, 999, sh_end)]


SHOTS = None


# ------------------------------------------------------------------ transitions
def tr_dip(a, b, p):
    """Lights out, lights on: dip to near-black with a click, then the next room."""
    k = 1 - abs(p - 0.5) * 2
    src = a if p < 0.5 else b
    return src * (1 - 0.92 * k ** 0.6)


def tr_sweep(a, b, p):
    """A warm band of light sweeps across and leaves the next shot behind it."""
    e = e_inout_cubic(p)
    pos = lerp(-400, W + 400, e)
    d = _X - pos + (_Y - H / 2) * 0.3
    out = np.where((d < 0)[..., None], b, a)
    g = np.exp(-(d / 130) ** 2)[..., None]
    return np.clip(out + g * np.array([1.0, 0.8, 0.5], np.float32) * 0.9, 0, 1)


def tr_blinds(a, b, p):
    """Window blinds: horizontal slats open onto the next shot."""
    e = e_inout_cubic(p)
    n = 12
    sl = (_Y % (H / n)) / (H / n)
    m = (sl < e).astype(np.float32)[..., None]
    m = cv2.GaussianBlur(m, (1, 7), 2)[..., None] if m.ndim == 2 else m
    return a * (1 - m) + b * m


def tr_iris(a, b, p, cx=490, cy=680):
    """Push into a lit window: a warm circle opens from the window onto the next shot."""
    r = e_in_cubic(p) * 2300
    d = np.hypot(_X - cx, _Y - cy)
    hole = np.clip((r - d) / 6, 0, 1)[..., None]
    ring = np.clip((r + 40 - d) / 6, 0, 1)[..., None] - hole
    za = 1 + 0.4 * e_in_cubic(p)
    A = cv2.warpAffine(a, np.float32([[za, 0, (1 - za) * cx], [0, za, (1 - za) * cy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    return A * (1 - hole - ring) + np.array([1.0, 0.78, 0.42], np.float32) * ring + b * hole


def tr_whip(a, b, p, axis=1):
    return R.whip(a, b, p, axis)


def tr_dissolve(a, b, p):
    e = e_inout_cubic(p)
    return a * (1 - e) + b * e


TRANS = [(tr_dip, 0.5), (tr_sweep, 0.5), (tr_dip, 0.55), (tr_blinds, 0.5), (lambda a, b, p: tr_whip(a, b, p, 1), 0.34),
         (tr_dip, 0.45), (lambda a, b, p: tr_whip(a, b, p, 0), 0.34), (tr_blinds, 0.5), (tr_sweep, 0.5), (tr_dip, 0.6),
         (tr_iris, 0.6), (tr_dissolve, 0.6)]


def hits():
    out = [(WT('l2', 0, 0.6), 0.8, 0), (WT('l3', 0, 0.25), 0.6, 0), (P('l4', 1), 0.5, 0), (P('l5', 1), 0.6, 0), (P('l6', 1), 0.8, 6),
           (P('l7', 2), 0.6, 0), (P('l8', 0) + 0.25, 0.5, 0), (P('l8', 1) + 0.2, 0.5, 0), (P('l9', 0) + 0.35, 0.6, 0),
           (P('l10', 0) + 0.15, 0.6, 0), (P('l12', 0) + 0.55, 1.0, 6), (P('l13', 0) + 0.2, 0.8, 0)]
    return out


HITS = None


def energy(t):
    z, sx, sy, ca = 1.0, 0.0, 0.0, 0.0
    for th, pn, sh in HITS:
        d = t - th
        if 0 <= d < 0.3:
            e = (1 - d / 0.3) ** 2
            z += 0.04 * pn * e
            ca = max(ca, 4 * pn * e)
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
    z *= 1.0 + 0.006 * math.sin(t * 0.8)
    if z > 1.001 or abs(sx) + abs(sy) > 0.5:
        M = np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    if t > DUR - FADE:
        c = c * (1 - 0.7 * e_inout_cubic(prog(t, DUR - FADE, DUR)))
    return c


def render(fi):
    t = fi / FPS
    c = render_raw(t)
    _, _, _, ca = energy(t)
    return post(c, fi, bloom=0.16, grain=0.013, vig=0.3, ca=ca)


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
            cv2.imwrite(p, to_u8(render(fi)), [cv2.IMWRITE_JPEG_QUALITY, 96])
            print('frame', fi, flush=True)
    elif mode == 'times':
        print('DUR', DUR, 'NF', NF)
        for k in ORDER:
            print(k, [round(P(k, i), 2) for i in range(len(INFO['phrases'][k]))])
