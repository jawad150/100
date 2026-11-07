"""Organic Fostering — "One Weekend" (9:16, ~33 s). ElevenLabs voice (IDA, Northern Woman). People + a photoreal dateless 3D
calendar whose gradient marker loop draws on, stretches and reshapes on the spoken words; 3D tokens pop on cue; houses,
moon, page flips, the chain of weekends, end card.

Usage: python3 reel_ow.py still 1.0,5.0 | python3 reel_ow.py range 0 100 | python3 reel_ow.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_ow as G
from frames_ow import (F, R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, IVORY, WHITE, N9, N8,
                       N7, HAND, token, cell_box, loop_pts, marker, grad_col, WEEKEND, HOLIDAY, AGREED)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = G.S
INFO = json.load(open(f'{S}/tts/info.json'))
OFF = 0.6
WORDS = [(w, t + OFF) for w, t, _ in INFO['words']]
DUR = 32.0
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y


def WT(i):
    return WORDS[i][1]


I = dict(every=4, day=5, Respite=6, planned=9, A=14, weekend=15, Part=16, school=19, Or=21, agreed=23, It=25, family=32, orgive=33,
         household=37, rest=40, And=41, same=48, home=49, time1=50, time2=52, Although=53, consistency=58, Ask=60, respite=63, Start=65,
         enquiry=67)
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


def footage(cid, ct, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return F.grade(F.cover(im, fx, fy, z, w, h))


@functools.lru_cache(maxsize=1)
def CAL():
    return G.calendar_bg()


@functools.lru_cache(maxsize=1)
def CANVAS():
    return F.canvas()


# ------------------------------------------------------------------ captions with a live-drawn marker loop
@functools.lru_cache(maxsize=256)
def wm(w, size):
    return _wmask(w, N9, size)


def caption(c, lines, t, keys=(), y=1560, size=66, t_out=None):
    keys = {k.lower() for k in keys}
    out = prog(t, t_out, t_out + 0.3) if t_out else 0
    if out >= 1:
        return
    for li, line in enumerate(lines):
        ws = [WORDS[i][0].replace('…', '') if i not in (9, 32) else WORDS[i][0] for i in line]
        ms = [wm(w, size) for w in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ms) - 1)
        x0 = W / 2 - tw / 2
        yy = y + li * size * 1.25
        xx = x0
        spans = []
        for i, w, m in zip(line, ws, ms):
            if w.strip('.,…!?’').lower() in keys:
                spans.append([xx, xx + m.shape[1], WT(i)])
            xx += m.shape[1] + size * 0.24
        if spans:
            groups = [spans[0]]
            for a_, b_, t_ in spans[1:]:
                if a_ - groups[-1][1] < size * 0.5:
                    groups[-1][1] = b_
                else:
                    groups.append([a_, b_, t_])
            for gi, (a_, b_, t_) in enumerate(groups):
                k = prog(t, t_ + 0.05, t_ + 0.55)
                if k > 0:
                    pts = loop_pts(a_ - size * 0.1, yy - size * 0.36, b_ + size * 0.1, yy + size * 0.4, e_inout_cubic(k), seed=li * 7 + gi, pad=10)
                    if len(pts) > 2:
                        tmp = c.copy()
                        marker(tmp, pts, th=7)
                        c[:] = c * out + tmp * (1 - out)
        xx = x0
        for i, w, m in zip(line, ws, ms):
            k = prog(t, WT(i) - 0.08, WT(i) + 0.22)
            if k > 0:
                op = min(1, k * 1.6) * (1 - out)
                dy = (1 - e_out_cubic(k)) * 16 - out * 18
                draw(c, blur_sprite(solid(m, (1, 1, 1, 1)), 10), xx + m.shape[1] / 2, yy + 3 + dy, opacity=0.7 * op)
                draw(c, solid(m, PLUM), xx + m.shape[1] / 2, yy + dy, opacity=op)
            xx += m.shape[1] + size * 0.24


def pop(c, sp, x, y, size, t, t0, rays=True, bob=8, rot=0):
    k = prog(t, t0, t0 + 0.42)
    if k <= 0:
        return
    e = e_out_back(k, 2.2)
    sc = size / max(sp.shape[:2]) * e
    yy = y + bob * math.sin((t - t0) * 2.2) + (1 - e_out_cubic(k)) * 60
    rr = rot + (1 - k) * -14 + 3 * math.sin((t - t0) * 1.7)
    if rays and k < 1:
        lay = np.zeros((H, W), np.uint8)
        r0 = size * 0.48
        kr = e_out_cubic(prog(t, t0, t0 + 0.5))
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = (28 if j % 2 else 46) * (1 - kr * 0.5)
            ra = r0 + kr * 30
            cv2.line(lay, (int((x + math.cos(a) * ra) * 4), int((yy + math.sin(a) * ra) * 4)),
                     (int((x + math.cos(a) * (ra + ln)) * 4), int((yy + math.sin(a) * (ra + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.9 * (1 - kr * 0.6)
        c[:] = c * (1 - m) + np.array(ORANGE[:3], np.float32) * m
    draw(c, blur_sprite(tint(sp, PLUM[:3]), 20), x + 6, yy + 20, scale=sc, rot=rr, opacity=0.4 * min(1, k * 2))
    draw(c, sp, x, yy, scale=sc, rot=rr, opacity=min(1, k * 2.5))


def pill(c, text, x, y, t, t0, t1=None):
    k = prog(t, t0 + 0.1, t0 + 0.45)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.25) if t1 else 0
    if ko >= 1:
        return
    s = ts(text, N8, 36, WHITE)
    w = s.shape[1] + 60
    e = e_out_back(k, 1.8)
    op = min(1, k * 2) * (1 - ko)
    b = F.grad_spr(w, 68, 34)
    draw(c, blur_sprite(tint(b, (0.3, 0.05, 0.2)), 14), x, y + 8, scale=e, opacity=0.4 * op)
    draw(c, b, x, y, scale=e, opacity=op)
    draw(c, s, x, y, scale=e, opacity=op)


def put_card(c, img, x, y, w, h, t, t0, t1=None, rot=0):
    k = prog(t, t0, t0 + 0.45)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.35) if t1 else 0
    if ko >= 1:
        return
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, 30, 2)), (w, h))
    pic = F.cover(img, 0.5, 0.5, 1.0, w, h)
    card = np.concatenate([pic * m[..., None], m[..., None]], 2).astype(np.float32)
    frame = rrect(w + 20, h + 20, 38, (1, 1, 1, 1))
    e = e_out_back(k, 1.6) * (1 - 0.2 * ko)
    op = min(1, k * 2) * (1 - ko)
    yy = y + (1 - e_out_cubic(k)) * 80 - ko * 60
    rr = rot + (1 - k) * 8
    draw(c, blur_sprite(tint(frame, (0.3, 0.05, 0.2)), 24), x + 8, yy + 22, rot=rr, scale=e, opacity=0.45 * op)
    draw(c, frame, x, yy, rot=rr, scale=e, opacity=op)
    draw(c, card, x, yy, rot=rr, scale=e, opacity=op)


def hand_in(c, s, x, y, size, col, t, t0, rot=0):
    k = prog(t, t0, t0 + 0.5)
    if k <= 0:
        return
    sp = solid(_wmask(s, HAND, size), col)
    ramp = np.clip((e_out_cubic(k) * (sp.shape[1] + 20) - np.arange(sp.shape[1])) / 14, 0, 1)[None, :, None]
    draw(c, sp * ramp, x, y, rot=rot)


def span_box(cells):
    return (min(cell_box(*rc)[0] for rc in cells), min(cell_box(*rc)[1] for rc in cells),
            max(cell_box(*rc)[2] for rc in cells), max(cell_box(*rc)[3] for rc in cells))


def fill_span(c, box, amt):
    if amt <= 0:
        return
    x0, y0, x1, y1 = [int(v) for v in box]
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(x1 - x0, y1 - y0, 16, 2)), (x1 - x0, y1 - y0))[..., None] * amt
    reg = c[y0:y1, x0:x1]
    u = np.clip((np.arange(x1 - x0)[None, :]) / max(1, x1 - x0), 0, 1)
    col = grad_col(u)
    reg[:] = reg * (1 - m) + (reg * 0.25 + col * 0.75) * m


# ------------------------------------------------------------------ shots
def sh_walk(t):
    c = footage(4661, 2.0 + t, fy=0.55, z=1.0 + 0.03 * t)
    G.top_veil(c, 460, 0.5)
    g = np.clip((_Y - 1150) / 500, 0, 1)[..., None]
    c = c * (1 - 0.85 * g) + np.array(IVORY[:3], np.float32) * 0.85 * g
    fi = e_inout_cubic(prog(t, 0, 0.5))
    c = c * fi + np.array(IVORY[:3], np.float32) * (1 - fi)
    hand_in(c, 'Friday, 5:30pm', 270, 330, 64, PURPLE, t, 0.35, rot=-4)
    G.logo_small(c)
    pop(c, token('calendar'), 790, 980, 300, t, T['every'] - 0.05)
    caption(c, [[0, 1, 2], [3, 4, 5]], t, keys=('every', 'day'), y=1560)
    return c


SPANS = [(T['planned'], span_box(WEEKEND)), (T['Part'] + 0.05, span_box(HOLIDAY)), (T['Or'] + 0.05, span_box(AGREED))]


def current_span(t):
    """Interpolated loop box (stretching/reshaping between spans)."""
    box = SPANS[0][1]
    for (ta, ba), (tb, bb) in zip(SPANS, SPANS[1:]):
        if t >= tb:
            box = bb
        elif t >= tb - 0.0 and t < tb + 0.55:
            pass
    for j in range(1, len(SPANS)):
        ta, ba = SPANS[j - 1]
        tb, bb = SPANS[j]
        if tb <= t < tb + 0.55:
            e = e_inout_cubic(prog(t, tb, tb + 0.55))
            return tuple(lerp(a, b, e) for a, b in zip(ba, bb)), j, e
        if t >= tb:
            box = bb
    return box, None, 1.0


def sh_calendar(t):
    t0 = T['Respite'] - 0.3
    c = CAL().copy()
    # draw / morph the loop
    if t >= T['planned'] - 0.05:
        box, morph, e = current_span(t)
        kdraw = prog(t, T['planned'] - 0.05, T['planned'] + 0.55)
        idx = 0 if t < SPANS[1][0] else (1 if t < SPANS[2][0] else 2)
        if morph is None:
            fill_span(c, box, 0.72 * prog(t, SPANS[idx][0] + (0.3 if idx else 0.45), SPANS[idx][0] + (0.7 if idx else 0.9)))
        else:
            fill_span(c, box, 0.35)
        pts = loop_pts(*box, e_inout_cubic(kdraw) if t < SPANS[1][0] else 1.0, seed=1 + idx, pad=14)
        if len(pts) > 2:
            marker(c, pts)
    put_card(c, G.frame_of(17412, 0.3) if t < 0 else footage(17412, 3.0 + (t - t0), w=420, h=300), 280, 300, 420, 300, t, t0 + 0.1, T['A'] - 0.25, rot=-4)
    hand_in(c, 'planned', 820, 300, 76, PURPLE, t, T['planned'] + 0.1, rot=-6) if t < T['A'] - 0.2 else None
    # a weekend: bag + packing inset + pill
    wb = span_box(WEEKEND)
    pop(c, token('bag'), 820, 330, 300, t, T['weekend'] - 0.05) if t < T['Part'] + 0.1 else None
    put_card(c, footage(45511, 8.0 + (t - T['A']), w=400, h=280), 300, 290, 400, 280, t, T['A'] - 0.1, T['Part'] - 0.1, rot=3)
    pill(c, 'A weekend', (wb[0] + wb[2]) / 2, wb[3] + 60, t, T['weekend'] - 0.1, T['Part'])
    hb = span_box(HOLIDAY)
    pop(c, token('bucket'), 830, 330, 300, t, T['school'] - 0.05) if T['Part'] - 0.1 < t < T['Or'] + 0.1 else None
    pill(c, 'Part of a school holiday', 540, hb[3] + 60, t, T['Part'] + 0.3, T['Or'])
    ab = span_box(AGREED)
    pop(c, token('clipboard'), 830, 320, 290, t, T['agreed'] - 0.05) if t > T['Or'] - 0.1 else None
    pill(c, 'Another agreed period', 600, ab[3] + 60, t, T['Or'] + 0.3)
    G.ivory_veil(c, 1380)
    caps = [([[6, 7, 8, 9], [10, 11, 12, 13]], T['Respite'] - 0.1, T['A'] - 0.35, ('planned',)),
            ([[14, 15]], T['A'] - 0.1, T['Part'] - 0.3, ('weekend',)),
            ([[16, 17, 18, 19, 20]], T['Part'] - 0.1, T['Or'] - 0.3, ('school', 'holiday')),
            ([[21, 22, 23, 24]], T['Or'] - 0.1, T['It'] - 0.4, ('agreed',))]
    for lines, a, b, keys in caps:
        if a - 0.2 <= t < b + 0.35:
            caption(c, lines, t, keys=keys, y=1560 if len(lines) > 1 else 1600, size=66 if len(lines) > 1 else 74, t_out=b)
    z = 1.0 + 0.035 * e_inout_cubic(prog(t, t0, T['It']))
    if z > 1.001:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * 800]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    return c


def sh_houses(t):
    c = CANVAS().copy()
    kd = prog(t, T['orgive'], T['rest'])
    if kd > 0:
        night = np.clip(1 - np.hypot(_X - 300, _Y - 900) / 520, 0, 1)[..., None] * 0.35 * e_inout_cubic(kd)
        c = c * (1 - night) + np.array([0.32, 0.22, 0.42], np.float32) * night
    hs = token('house')
    kl = prog(t, T['It'] - 0.05, T['It'] + 0.5)
    lay = np.zeros((H, W), np.uint8)
    pts = [(300 + 490 * u, 900 - math.sin(u * math.pi) * 170) for u in np.linspace(0, 1, 60)]
    n = int(58 * e_inout_cubic(prog(t, T['It'] + 0.3, T['family'])))
    for i in range(0, n, 3):
        cv2.line(lay, (int(pts[i][0] * 4), int(pts[i][1] * 4)), (int(pts[i + 1][0] * 4), int(pts[i + 1][1] * 4)), 255, 9 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + grad_col((_X - 300) / 490) * m
    for i, (x, t_on) in enumerate(((300, T['It'] - 0.05), (790, T['family'] - 0.25))):
        k = prog(t, t_on, t_on + 0.45)
        if k <= 0:
            continue
        sp = hs
        if i == 0 and kd > 0:
            sp = hs * np.array([1 - 0.28 * kd, 1 - 0.3 * kd, 1 - 0.15 * kd, 1.0], np.float32)
        e = e_out_back(k, 2.0)
        draw(c, blur_sprite(tint(sp, PLUM[:3]), 20), x + 6, 980, scale=300 / max(hs.shape[:2]) * e, opacity=0.4 * k)
        draw(c, sp, x, 960 + (1 - e_out_cubic(k)) * 60, scale=300 / max(hs.shape[:2]) * e, opacity=min(1, k * 2))
    hand_in(c, 'a family', 300, 1170, 62, PURPLE, t, T['family'] - 0.6, rot=-5)
    hand_in(c, 'you', 790, 1170, 62, ORANGE, t, T['family'] - 0.2, rot=4)
    km = prog(t, T['household'] - 0.2, T['rest'] + 0.1)
    if km > 0:
        mo = token('moon')
        e = e_out_cubic(km)
        y = lerp(260, 640, e) + 6 * math.sin(t * 1.5)
        draw(c, blur_sprite(tint(mo, PLUM[:3]), 20), 306, y + 20, scale=210 / max(mo.shape[:2]), opacity=0.3 * km)
        draw(c, mo, 300, y, scale=210 / max(mo.shape[:2]), rot=-8 * (1 - e), opacity=min(1, km * 2))
    if t > T['rest'] - 0.1:
        hand_in(c, 'zzz', 400, 600, 60, PLUM, t, T['rest'] - 0.1, rot=-8)
    put_card(c, footage(25377, 6.0 + (t - T['orgive']), w=360, h=420), 760, 470, 360, 420, t, T['orgive'] - 0.1, rot=4)
    G.logo_small(c) if t < T['orgive'] else None
    caption(c, [[25, 26, 27, 28, 29], [30, 31, 32]], t, keys=('family',), y=1500, t_out=T['orgive'] - 0.3)
    caption(c, [[33, 34, 35, 36], [37, 38, 39, 40]], t, keys=('rest',), y=1500)
    return c


def sh_door(t):
    t0 = T['And'] - 0.3
    c = footage(21813, 2.5 + (t - t0), fx=0.55, z=1.04 + 0.02 * (t - t0))
    G.top_veil(c, 420, 0.5)
    g = np.clip((_Y - 1200) / 450, 0, 1)[..., None]
    c = c * (1 - 0.88 * g) + np.array(IVORY[:3], np.float32) * 0.88 * g
    pop(c, token('key'), 840, 1180, 240, t, T['same'] - 0.05)
    G.logo_small(c)
    caption(c, [[41, 42, 43, 44], [45, 46, 47, 48, 49]], t, keys=('same', 'home'), y=1540)
    return c


@functools.lru_cache(maxsize=8)
def PAGE(seed):
    return G.mini_month(560, 600, True, seed=seed)


def sh_flip(t):
    t0 = T['time1'] - 0.2
    c = CANVAS().copy()
    rate = 3.0
    k = (t - t0) * rate
    idx = int(max(0, k))
    frac = max(0.0, k - idx)
    # pages underneath
    for j in range(3, 0, -1):
        pg = PAGE((idx + j) % 8)
        x, y = 540 + j * 14, 880 - j * 18
        draw(c, blur_sprite(tint(pg, (0.3, 0.05, 0.2)), 18), x + 6, y + 20, rot=-j * 2.5, opacity=0.3)
        draw(c, pg, x, y, rot=-j * 2.5)
    # the top page flips up from the bottom edge (squash in y around its top)
    pg = PAGE(idx % 8)
    hpg = pg.shape[0]
    sy = math.cos(frac * math.pi / 2) if frac < 1 else 0
    if sy > 0.02:
        sq = cv2.resize(pg, (pg.shape[1], max(2, int(hpg * sy))))
        shade = 1 - 0.35 * frac
        sq = sq * np.array([shade, shade, shade, 1], np.float32)
        draw(c, sq, 540, 880 - hpg / 2 + sq.shape[0] / 2)
    hand_in(c, 'again', 860, 420, 70, ORANGE, t, t0 + 0.3, rot=8)
    hand_in(c, 'and again', 250, 1270, 64, PURPLE, t, t0 + 0.8, rot=-5)
    caption(c, [[50, 51, 52]], t, keys=('time', 'after'), y=1560, size=76)
    return c


def sh_chain(t):
    c = CANVAS().copy()
    t0 = T['Although'] - 0.3
    xs, ys = 540, [420, 620, 820, 1020, 1220]
    kline = e_inout_cubic(prog(t, t0 + 0.3, t0 + 2.2))
    if kline > 0:
        lay = np.zeros((H, W), np.uint8)
        cv2.line(lay, (xs * 4, ys[0] * 4), (xs * 4, int(lerp(ys[0], ys[-1], kline) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255
        c = c * (1 - m) + grad_col((_Y - ys[0]) / (ys[-1] - ys[0])) * m
    for i, y in enumerate(ys):
        k = prog(t, t0 + 0.2 + i * 0.38, t0 + 0.55 + i * 0.38)
        if k <= 0:
            continue
        e = e_out_back(k, 2.0)
        chip = F.grad_spr(300, 120, 60, phase=i * 0.1 + t * 0.05)
        yy = y - (1 - e_out_cubic(k)) * 120
        draw(c, blur_sprite(tint(chip, (0.3, 0.05, 0.2)), 16), xs + 6, yy + 14, scale=e, opacity=0.4 * k)
        draw(c, chip, xs, yy, scale=e, opacity=min(1, k * 2))
        draw(c, ts('S   S', N9, 50, WHITE), xs, yy, scale=e, opacity=min(1, k * 2))
    kc = prog(t, T['consistency'], T['consistency'] + 0.8)
    if 0 < kc < 1:
        g = np.exp(-((_X - xs) ** 2) / (2 * 160 ** 2)) * np.clip(1 - np.abs(_Y - 820) / 520, 0, 1)
        c = np.clip(c + (g * math.sin(math.pi * kc) * 0.25)[..., None] * np.array([1, 0.7, 0.5], np.float32), 0, 1)
    hand_in(c, 'every month', 230, 700, 60, PURPLE, t, t0 + 1.0, rot=-8)
    caption(c, [[53, 54, 55, 56, 57], [58, 59]], t, keys=('consistency',), y=1500)
    return c


def sh_end(t):
    c = CANVAS().copy()
    t0 = T['Ask'] - 0.3
    lg = F.logo()
    kl = prog(t, t0, t0 + 0.5)
    draw(c, lg, W / 2, 520, scale=700 / lg.shape[1] * (0.9 + 0.1 * e_out_back(kl, 1.6)), opacity=min(1, kl * 2))
    hand_in(c, 'one weekend at a time', W / 2, 730, 76, ORANGE, t, t0 + 0.4, rot=-3)
    kb = prog(t, T['Ask'], T['Ask'] + 0.4)
    if kb > 0:
        eb = e_out_back(kb, 2.0)
        pulse = 1 + 0.025 * math.sin((t - T['Ask']) * 4) * prog(t, T['Ask'] + 0.7, T['Ask'] + 1.1)
        btn = F.grad_spr(820, 130, 65, phase=(t * 0.12) % 1)
        draw(c, blur_sprite(btn, 24), W / 2, 980, opacity=0.55 * min(1, kb * 2), scale=eb * pulse)
        draw(c, btn, W / 2, 960, scale=eb * pulse)
        tmp = np.zeros((150, 840, 4), np.float32)
        s = ts('Ask us about respite fostering', N9, 46, WHITE)
        a = F.arrow(WHITE, 46)
        tw = s.shape[1] + 16 + a.shape[1]
        paste_spr(tmp, s, 420 - tw / 2 + s.shape[1] / 2, 75)
        paste_spr(tmp, a, 420 + tw / 2 - a.shape[1] / 2 + 6 * max(0, math.sin((t - T['Ask']) * 5)), 77)
        draw(c, tmp, W / 2, 960, scale=eb * pulse)
        sw = prog(t, T['Ask'] + 0.6, T['Ask'] + 1.3)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(160, 920, sw) - (_Y - 960) * 0.4) / 40) ** 2) * (np.abs(_Y - 960) < 62)
            c = np.clip(c + band[..., None] * 0.3, 0, 1)
    kp = prog(t, T['Start'] - 0.1, T['Start'] + 0.35)
    if kp > 0:
        draw(c, ts('0161 241 1332', N9, 64, PURPLE), W / 2, 1130 + (1 - kp) * 20, opacity=kp)
        draw(c, ts('organicfostering.co.uk', N8, 40, PLUM), W / 2, 1210 + (1 - kp) * 20, opacity=kp)
    ko = prog(t, T['enquiry'] + 0.3, T['enquiry'] + 0.8)
    if ko > 0:
        s = ts('Rated Good by Ofsted', N7, 32, PLUM)
        F.drop(c, rrect(s.shape[1] + 110, 70, 35, (1, 1, 1, 0.95 * ko)), W / 2, 1330, sh=0.25 * ko)
        draw(c, F.star(), W / 2 - s.shape[1] / 2 - 10, 1330, opacity=ko)
        draw(c, s, W / 2 + 20, 1330, opacity=ko)
    return c


def shots():
    return [
        (0.0, T['Respite'] - 0.3, sh_walk),
        (T['Respite'] - 0.3, T['It'] - 0.3, sh_calendar),
        (T['It'] - 0.3, T['And'] - 0.3, sh_houses),
        (T['And'] - 0.3, T['time1'] - 0.2, sh_door),
        (T['time1'] - 0.2, T['Although'] - 0.3, sh_flip),
        (T['Although'] - 0.3, T['Ask'] - 0.3, sh_chain),
        (T['Ask'] - 0.3, DUR + 1, sh_end),
    ]


SHOTS = None


# ------------------------------------------------------------------ transitions
def tr_tear(a, b, p):
    """A calendar page tears away diagonally (ragged edge) to reveal the next shot."""
    e = e_inout_cubic(p)
    rng = np.random.default_rng(4)
    jag = cv2.resize(rng.random((1, 80)).astype(np.float32), (W, 1))[0] * 26
    edge = lerp(-300, H + 300, e) - (_X * 0.35) + jag[None, :].repeat(H, 0)
    m = (_Y < edge).astype(np.float32)[..., None]
    rim = np.clip(1 - np.abs(_Y - edge) / 10, 0, 1)[..., None]
    out = b * m + a * (1 - m)
    return np.clip(out * (1 - rim * 0.6) + rim * 0.6 * np.array([1, 1, 1], np.float32), 0, 1)


def tr_stroke(a, b, p):
    """A fat gradient marker stroke sweeps across and leaves the next shot behind it."""
    e = e_inout_cubic(p)
    pos = lerp(-500, W + 500, e)
    d = (_X - pos) + (_Y - H / 2) * 0.25
    m = (d < 0).astype(np.float32)[..., None]
    band = np.clip(1 - np.abs(d + 120) / 140, 0, 1)[..., None]
    out = a * (1 - m) + b * m
    return out * (1 - band) + grad_col(_Y / H) * band


def tr_whip(a, b, p):
    return R.whip(a, b, p, 1)


def tr_dusk(a, b, p):
    e = e_inout_cubic(p)
    k = math.sin(math.pi * p)
    out = a * (1 - e) + b * e
    return np.clip(out * (1 - 0.25 * k) + np.array([0.3, 0.2, 0.4], np.float32) * 0.25 * k, 0, 1)


def tr_flash(a, b, p):
    src = a if p < 0.5 else b
    k = 1 - abs(p - 0.5) * 2
    return np.clip(src + k ** 2 * 0.4, 0, 1)


def tr_soft(a, b, p):
    e = e_inout_cubic(p)
    return a * (1 - e) + b * e


TRANS = [(tr_tear, 0.55), (tr_stroke, 0.55), (tr_dusk, 0.5), (tr_whip, 0.34), (tr_flash, 0.3), (tr_soft, 0.5)]


def hits():
    return [(T['every'], 0.5), (T['planned'], 0.4), (T['weekend'], 0.6), (T['school'], 0.6), (T['agreed'], 0.6), (T['It'], 0.4),
            (T['family'], 0.4), (T['rest'], 0.3), (T['same'], 0.6), (T['consistency'], 0.5), (T['Ask'], 0.6)]


HITS = None


def energy(t):
    z = 1.0
    for th, pn in HITS:
        d = t - th
        if 0 <= d < 0.3:
            z += 0.02 * pn * (1 - d / 0.3) ** 2
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
    z = energy(t) * (1.0 + 0.004 * math.sin(t * 0.8))
    if z > 1.001:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    fo = prog(t, DUR - 1.6, DUR)
    if fo > 0:
        c = c * (1 - 0.6 * e_inout_cubic(fo)) + np.array(IVORY[:3], np.float32) * 0.6 * e_inout_cubic(fo)
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.08, grain=0.01, vig=0.15)


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
