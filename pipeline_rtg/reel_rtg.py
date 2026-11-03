"""Organic Fostering — "Room to Grow" (9:16, ~40 s). People walking at first light, a spare room measured up, then the room as
a 3D cutaway miniature that changes on the narrator's words, morning to dusk; the landing; the end card.

Usage: python3 reel_rtg.py still 1.0,5.0 | python3 reel_rtg.py range 0 100 | python3 reel_rtg.py times
"""
import os, sys, math, json, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_rtg as G
from frames_rtg import (F, R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, WHITE, N9, N8,
                        N7, HAND, INK, CREAM, GOLD, S, token, room, hand, eyebrow, sparkle, arch, grade)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
INFO = json.load(open(f'{S}/tts/info.json'))
OFF = 0.8                                   # voice starts after the opening beat
WORDS = [(w, max(0.0, t) + OFF) for w, t, _ in INFO['words']]
DUR = round(OFF + INFO['dur'] + 2.7, 2)
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y


def WT(i):
    return WORDS[i][1]


# word index landmarks (see vo_rtg.PHRASES)
I = dict(small=1, can=3, direction=6, For=10, child=12, it=16, room=21, A_bed=22, bed=24, A_lamp=25, lamp=26, A_place=29,
         belong=32, And=33, leave=37, them=39, Their=40, pictures=41, books=43, name=45, door=48, At=49, matching=52, whole=55,
         culture=57, faith=58, language=59, relationships=60, identity=62, matter=63, You=64, call=71, Start=72, enquiry=74)
T = {k: WT(v) for k, v in I.items()}

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
            return self.cache.get(max(self.cache)) if self.cache else np.zeros((720, 1280, 3), np.uint8)
        self.pos = i
        if len(self.cache) > 40:
            self.cache.clear()
        self.cache[i] = im
        return im


_clips = {}


def cover(im, k, fx, fy, z0, z1, w=W, h=H, drift=(0, 0)):
    ih, iw = im.shape[:2]
    z = lerp(z0, z1, e_inout_cubic(clamp(k)))
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


def footage(cid, ct, fx=0.5, fy=0.5, z0=1.0, z1=1.08, k=0.0, w=W, h=H, drift=(0, 0)):
    """Frame of clip `cid` at clip time ct (s), framed to w x h."""
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return grade(cover(im, k, fx, fy, z0, z1, w, h, drift))


@functools.lru_cache(maxsize=8)
def BACK(time):
    return G.backdrop(time, *( {'morning': ((760, 520), 380), 'day': ((780, 560), 380), 'warm': ((760, 900), 460),
                                'dusk': ((760, 620), 380)}[time]))


@functools.lru_cache(maxsize=4)
def STILL(name):
    return G.still(name)


@functools.lru_cache(maxsize=1)
def LOGO():
    return F.logo()


@functools.lru_cache(maxsize=1)
def LOGO_W():
    lg = F.logo()
    a = lg[..., 3:4]
    return np.concatenate([np.ones_like(lg[..., :3]) * a, a], 2)


# ------------------------------------------------------------------ the miniature: state blends and per-object reveals
@functools.lru_cache(maxsize=8)
def RS(state):
    return room(state)


@functools.lru_cache(maxsize=8)
def DIFF(a, b, th=25, blur=3):
    A = RS(a) * 255
    B = RS(b) * 255
    d = np.abs(A - B).sum(2)
    m = (cv2.GaussianBlur(d, (0, 0), 2) > th).astype(np.uint8)
    return m


@functools.lru_cache(maxsize=1)
def BED_MASK():
    m = DIFF('s2', 's3').astype(np.float32)
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), 3)


@functools.lru_cache(maxsize=1)
def ITEMS():
    """Connected diff regions s4 -> s5, each assigned to frame / shelf / pinboard / card by centroid."""
    m = DIFF('s4', 's5')
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    guess = json.load(open(f'{S}/room/anchors.json'))
    out = {k: np.zeros(m.shape, np.float32) for k in guess}
    cent = {}
    for i in range(1, n):
        if st[i, 4] < 120:
            continue
        k = min(guess, key=lambda g: math.hypot(cen[i][0] - guess[g][0], cen[i][1] - guess[g][1]))
        out[k] = np.maximum(out[k], (lab == i).astype(np.float32))
        cent[k] = tuple(cen[i])
    for k in out:
        out[k] = cv2.GaussianBlur(cv2.dilate(out[k], np.ones((7, 7), np.uint8)), (0, 0), 2)
    return out, cent


def blend(a, b, k):
    if k <= 0:
        return a
    if k >= 1:
        return b
    return a * (1 - k) + b * k


def masked_layer(src, m):
    return src * m[..., None]


def room_sprite(t):
    """The miniature at time t (premultiplied RGBA, room-image space)."""
    s1, s2, s3, s4, s5, s6 = (RS(x) for x in ('s1', 's2', 's3', 's4', 's5', 's6'))
    # 1) clear: boxes lift out on "room"
    kc = prog(t, T['room'], T['room'] + 0.9)
    if kc < 1:
        return blend(s1, s2, e_inout_cubic(kc)), kc
    # 2) bed drops in on "bed"
    kb = prog(t, T['bed'] - 0.12, T['bed'] + 0.4)
    if t < T['A_lamp'] - 0.1:
        if kb <= 0:
            return s2, 1
        m = BED_MASK()
        e = e_out_back(kb, 1.6)
        dy = (1 - e) * -260
        base = s2 * (1 - m[..., None] * min(1, kb * 3))
        lay = masked_layer(s3, m)
        M = np.float32([[1, 0, 0], [0, 1, dy]])
        lay = cv2.warpAffine(lay, M, (lay.shape[1], lay.shape[0]))
        out = base + lay * (1 - base[..., 3:4] * 0) if False else base * (1 - lay[..., 3:4]) + lay
        if kb >= 1:
            out = blend(out, s3, prog(t, T['bed'] + 0.4, T['bed'] + 0.6))
        return out, 1
    # 3) lamp: flicker on "lamp"
    kl = flick(t, T['lamp'] + 0.05)
    if t < T['Their'] - 0.05:
        return blend(s3, s4, kl), 1
    # 4) the spaces: frame + pinboard on "pictures", shelf on "books", card on "name"
    items, _ = ITEMS()
    out = s4.copy()
    for key, t0 in (('frame', T['pictures']), ('pin', T['pictures'] + 0.12), ('shelf', T['books']), ('card', T['name'])):
        k = prog(t, t0 - 0.05, t0 + 0.3)
        if k <= 0:
            continue
        m = items[key] * min(1, k * 2.2)
        out = out * (1 - m[..., None]) + s5 * m[..., None]
    # 5) dusk falls after "Fostering," (time-lapse)
    kd = prog(t, T['At'] + 0.2, T['matching'] + 0.1)
    if kd > 0:
        out = blend(out, s6, e_inout_cubic(kd))
    return out, 1


def flick(t, ton, dur=0.3):
    if t < ton:
        return 0.0
    d = t - ton
    if d > dur:
        return 1.0
    return [0, 0.7, 0.15, 0.9, 0.5, 1, 1][min(6, int(d / dur * 7))]


def place(c, sp, cx, cy, w, shadow=0.35):
    sc = w / sp.shape[1]
    m = np.exp(-(((_X - (cx + 20 * sc)) / (430 * sc)) ** 2 + ((_Y - (cy + 330 * sc)) / (95 * sc)) ** 2))[..., None]
    c[:] = c * (1 - shadow * m) + np.array([0.25, 0.08, 0.2], np.float32) * shadow * m
    draw(c, sp, cx, cy, scale=sc)

    def at(px, py):
        return cx + (px - sp.shape[1] / 2) * sc, cy + (py - sp.shape[0] / 2) * sc
    return at


A = G.A


# ------------------------------------------------------------------ animated motifs
@functools.lru_cache(maxsize=64)
def strip(line, cues, size, dark, seed):
    """A caption tape strip; returns sprite and each word's right edge (sprite x)."""
    words = line.split()
    gap = size * 0.24
    sprs = [_wmask(w_, N9, size) for w_ in words]
    tw = sum(s.shape[1] for s in sprs) + gap * (len(words) - 1)
    padx, h = size * 0.42, int(size * 1.42)
    sw = int(tw + padx * 2)
    sp = np.zeros((h + 40, sw + 60, 4), np.float32)
    fill = (0.16, 0.1, 0.24, 0.93) if dark else CREAM
    ink = (1, 0.96, 0.92, 1) if dark else INK
    paste_spr(sp, solid(G.tape_mask(sw, h, seed), fill), sp.shape[1] / 2, sp.shape[0] / 2)
    xx = (sp.shape[1] - sw) / 2 + padx
    ends = []
    for w_, s in zip(words, sprs):
        key = w_.strip('.,?!’\'').lower() in cues
        cx_ = xx + s.shape[1] / 2
        if key:
            km = G.tape_mask(int(s.shape[1] + size * 0.3), int(size * 1.12), seed + 3, teeth=5)
            paste_spr(sp, solid(km, ORANGE), cx_, sp.shape[0] / 2 + 2)
        paste_spr(sp, solid(s, WHITE if key else ink), cx_, sp.shape[0] / 2 + size * 0.04)
        xx += s.shape[1] + gap
        ends.append(xx - gap + padx * 0.9)
    return sp, tuple(ends)


# caption groups: (lines, first word index, cue words, y, size, dark, x)
CAPS = [
    (['A small beginning'], 0, ('small', 'beginning'), 1570, 66, False),
    (['can change the', 'direction of a life.'], 3, ('direction', 'life'), 1510, 66, False),
    (['For a child', 'coming into care,'], 10, ('child',), 1530, 66, False),
    (['it can start', 'with a room.'], 16, ('room',), 1560, 66, False),
    (['A made bed.'], 22, ('bed',), 1620, 70, False),
    (['A lamp left on.'], 25, ('lamp',), 1620, 70, False),
    (['A place to belong.'], 29, ('belong',), 1620, 70, False),
    (['And some things', 'you leave for them.'], 33, ('them',), 1500, 66, False),
    (['Their pictures. Their books.', 'Their name on the door.'], 40, ('pictures', 'books', 'name'), 1560, 58, False),
    (['At Organic Fostering,', 'matching sees the whole child.'], 49, ('matching', 'whole', 'child'), 1540, 56, True),
    (['Culture, faith, language,', 'relationships and identity', 'matter.'], 57, ('matter',), 1440, 56, True),
    (['You don’t need every answer', 'before you call.'], 64, ('call',), 1510, 56, True),
]


def cap_end(j):
    if j + 1 < len(CAPS):
        return WT(CAPS[j + 1][1]) - 0.08
    return T['Start'] - 0.1


def captions(c, t):
    for j, (lines, i0, cues, y, size, dark) in enumerate(CAPS):
        t_in, t_out = WT(i0) - 0.12, cap_end(j)
        if not (t_in <= t < t_out + 0.2):
            continue
        out = prog(t, t_out, t_out + 0.2)
        idx = i0
        for li, ln in enumerate(lines):
            n = len(ln.split())
            sp, ends = strip(ln, tuple(cues), size, dark, li + len(ln))
            # unroll to the end of the last spoken word, eased
            times = [WT(idx + q) for q in range(n)]
            idx += n
            if t < times[0] - 0.12:
                continue
            vis = 0
            for q, tq in enumerate(times):
                if t >= tq - 0.08:
                    prev = ends[q - 1] if q else 30
                    vis = lerp(prev, ends[q], e_out_cubic(prog(t, tq - 0.08, tq + 0.14)))
            vis = max(vis, 30 + 40 * prog(t, times[0] - 0.12, times[0]))
            s2 = sp.copy()
            ramp = np.clip((vis - np.arange(sp.shape[1])) / 8, 0, 1)[None, :, None]
            s2 *= ramp
            rot = (-1.6, 1.2, -0.8, 1.4)[li % 4]
            x = 70 + li * 18 + sp.shape[1] / 2 - 30
            k = prog(t, times[0] - 0.12, times[0] + 0.15)
            yy = y + li * size * 1.5 + (1 - e_out_cubic(k)) * 18 - out * 30
            op = (1 - out)
            draw(c, blur_sprite(tint(s2, (0.25, 0.05, 0.2)), 12), x + 4, yy + 12, rot=rot, opacity=0.35 * op)
            draw(c, s2, x, yy, rot=rot, opacity=op)


def ruler_k(t):
    keys = [(0, 0.0), (T['small'], 0.06), (T['direction'], 0.12), (T['child'], 0.18), (T['room'], 0.28), (T['bed'], 0.38),
            (T['lamp'], 0.46), (T['belong'], 0.56), (T['them'], 0.62), (T['name'], 0.72), (T['whole'], 0.8), (T['matter'], 0.9),
            (T['call'], 1.0)]
    for (a, ka), (b, kb) in zip(keys, keys[1:]):
        if t < b:
            return lerp(ka, kb, e_inout_cubic(prog(t, a, b)))
    return 1.0


def pop(c, sp, x, y, size, t, t0, rings=True, col=ORANGE, sparks=True, rot=0, bob=8, dur=0.42):
    k = prog(t, t0, t0 + dur)
    if k <= 0:
        return
    e = e_out_back(k, 2.2)
    sc = size / max(sp.shape[:2]) * e
    yy = y + bob * math.sin((t - t0) * 2.1) + (1 - e_out_cubic(k)) * 60
    rr = rot + (1 - k) * -18 + 3 * math.sin((t - t0) * 1.6)
    if rings:
        kr = prog(t, t0, t0 + 0.7)
        lay = np.zeros((H, W), np.uint8)
        r0 = size * (0.4 + 0.25 * e_out_cubic(kr))
        cv2.circle(lay, (int(x * 4), int(yy * 4)), int(r0 * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
        cv2.circle(lay, (int(x * 4), int(yy * 4)), int(r0 * 1.22 * 4), 255, 2 * 4, cv2.LINE_AA, shift=2)
        burst = prog(t, t0, t0 + 0.5)
        if burst < 1:
            rb = size * (0.5 + 0.6 * e_out_cubic(burst))
            cv2.circle(lay, (int(x * 4), int(yy * 4)), int(rb * 4), int(255 * (1 - burst)), 3 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.85 * min(1, k * 2)
        c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    draw(c, blur_sprite(tint(sp, (0.3, 0.06, 0.22)), 22), x + 10, yy + 30, scale=sc, rot=rr, opacity=0.38 * min(1, k * 2))
    draw(c, sp, x, yy, scale=sc, rot=rr, opacity=min(1, k * 2.5))
    if sparks:
        for j, (dx, dy, s) in enumerate(((0.58, -0.5, 22), (-0.62, -0.28, 15), (0.48, 0.55, 13))):
            tw = 0.6 + 0.4 * math.sin((t - t0) * 6 + j * 2)
            ks = prog(t, t0 + 0.1 + j * 0.06, t0 + 0.4 + j * 0.06)
            if ks > 0:
                sparkle(c, x + dx * size, yy + dy * size, s * e_out_back(ks) * tw)


def sparkles(c, t, t0, pts, dur=1.4):
    for j, (x, y, s) in enumerate(pts):
        k = prog(t, t0 + j * 0.07, t0 + j * 0.07 + 0.3)
        f = 1 - prog(t, t0 + dur, t0 + dur + 0.4)
        if k > 0 and f > 0:
            sparkle(c, x, y - (t - t0) * 20, s * e_out_back(k) * f * (0.7 + 0.3 * math.sin(t * 9 + j)))


def hand_in(c, s, x, y, size, col, t, t0, rot=0, anchor='c'):
    """Handwritten note written on: a left-to-right wipe."""
    k = prog(t, t0, t0 + 0.5)
    if k <= 0:
        return
    sp = solid(_wmask(s, HAND, size), col)
    ramp = np.clip((e_out_cubic(k) * (sp.shape[1] + 20) - np.arange(sp.shape[1])) / 14, 0, 1)[None, :, None]
    draw(c, sp * ramp, x + (sp.shape[1] / 2 if anchor == 'l' else 0), y, rot=rot)


def line_draw(c, pts, k, col, th=4, dashed=False, dot0=False):
    if k <= 0:
        return
    pts = np.array(pts, np.float32)
    n = max(2, int(len(pts) * k))
    lay = np.zeros((H, W), np.uint8)
    p = pts[:n]
    if dashed:
        for i in range(0, n - 1, 3):
            cv2.line(lay, tuple((p[i] * 4).astype(int)), tuple((p[min(n - 1, i + 1)] * 4).astype(int)), 255, th * 4, cv2.LINE_AA, shift=2)
    else:
        cv2.polylines(lay, [(p * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    if dot0:
        cv2.circle(lay, tuple((pts[0] * 4).astype(int)), 9 * 4, 255, -1, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    if dot0:
        draw(c, rrect(9, 9, 4.5, WHITE), pts[0][0], pts[0][1])


def curve(p, q, lift=40, n=40):
    mid = ((p[0] + q[0]) / 2, min(p[1], q[1]) - lift)
    return [((1 - u) ** 2 * p[0] + 2 * (1 - u) * u * mid[0] + u * u * q[0], (1 - u) ** 2 * p[1] + 2 * (1 - u) * u * mid[1] + u * u * q[1])
            for u in np.linspace(0, 1, n)]


def dashed_box(c, x, y, w, h, t, t0, col=PURPLE, th=4, dash=18, gap=12, r=12):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return
    e = e_out_back(k, 1.8)
    ph = (t - t0) * 40
    w2, h2 = w * e, h * e
    lay = np.zeros((H, W), np.uint8)
    per = 2 * (w2 + h2)
    pts = []
    for s0 in np.arange(-ph % (dash + gap) - (dash + gap), per, dash + gap):
        a, b = max(0, s0), min(per, s0 + dash)
        if b <= a:
            continue
        pts.append((a, b))

    def pos(s):
        if s < w2:
            return x - w2 / 2 + s, y - h2 / 2
        s -= w2
        if s < h2:
            return x + w2 / 2, y - h2 / 2 + s
        s -= h2
        if s < w2:
            return x + w2 / 2 - s, y + h2 / 2
        s -= w2
        return x - w2 / 2, y + h2 / 2 - s
    for a, b in pts:
        ss = np.linspace(a, b, 6)
        poly = np.array([pos(s) for s in ss], np.float32)
        cv2.polylines(lay, [(poly * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    g = cv2.GaussianBlur(m[..., 0], (0, 0), 6)[..., None] * 0.55
    c[:] = c * (1 - g) + np.array([1, 1, 1], np.float32) * g
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


@functools.lru_cache(maxsize=1)
def _motes():
    rng = np.random.default_rng(3)
    return [(rng.uniform(0, W), rng.uniform(0, H * 0.85), rng.uniform(1.2, 3.2), rng.uniform(0, 6.28), rng.uniform(0.2, 0.6)) for _ in range(40)]


def motes(c, t, amt=0.7, col=(1.0, 0.92, 0.75)):
    lay = np.zeros((H, W), np.float32)
    for x, y, r, ph, sp in _motes():
        xx = (x + math.sin(t * sp + ph) * 30 + t * 8) % W
        yy = (y - t * 14 * sp) % (H * 0.85)
        cv2.circle(lay, (int(xx), int(yy)), int(r), 1.0, -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.6)[..., None] * amt
    c[:] = np.clip(c + lay * np.array(col, np.float32), 0, 1)


def god_rays(c, x, y, t, amt=0.22, col=(1.0, 0.86, 0.6), n=9, length=1300, ang0=1.9, spread=0.7):
    lay = np.zeros((H, W), np.uint8)
    for j in range(n):
        a = ang0 + (j / (n - 1) - 0.5) * spread + 0.03 * math.sin(t * 0.7 + j)
        w = 30 + 25 * math.sin(j * 1.7)
        p2 = (x + math.cos(a) * length, y + math.sin(a) * length)
        pa = (x + math.cos(a + w / length) * length, y + math.sin(a + w / length) * length)
        cv2.fillPoly(lay, [np.array([(x, y), p2, pa], np.int32)], 255, cv2.LINE_AA)
    m = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 22)
    fall = np.clip(1 - np.hypot(_X - x, _Y - y) / length, 0, 1)
    m = (m * fall)[..., None] * amt
    c[:] = np.clip(c + m * np.array(col, np.float32), 0, 1)


def ruler(c, t, dark=False):
    G.ruler(c, ruler_k(t), dark)


def eyebrow_in(c, t, t0=0.0, dark=False):
    k = prog(t, t0, t0 + 0.5)
    if k > 0:
        tmp = np.zeros_like(c)
        G.eyebrow(c, dark=dark) if k >= 1 else None
        if k < 1:
            s = ts('ROOM TO GROW', 'Poppins-SemiBold', 26, WHITE if dark else PLUM, 0.18)
            draw(c, rrect(14, 14, 7, ORANGE), 77, 150, scale=e_out_back(k))
            draw(c, s, 100 + s.shape[1] / 2, 150, opacity=k)


def put_arch(c, img, x, y, w, h, t, t0, t1=None, rot=0):
    k = prog(t, t0, t0 + 0.45)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.3) if t1 else 0
    if ko >= 1:
        return
    a = arch(img, w, h)
    e = e_out_back(k, 1.7) * (1 - e_in_cubic(ko))
    yy = y + (1 - e_out_cubic(k)) * 120 + e_in_cubic(ko) * 80
    draw(c, blur_sprite(tint(a, (0.25, 0.05, 0.18)), 26), x + 8, yy + 26, scale=e, rot=rot + (1 - k) * 8, opacity=0.45 * k * (1 - ko))
    draw(c, a, x, yy, scale=e, rot=rot + (1 - k) * 8, opacity=min(1, k * 2) * (1 - ko))


def bottom_veil(c, top=0.58, amt=0.8):
    c[:] = F.shade(c, top, amt, PLUM)


def top_veil(c, h=380, amt=0.35, col=(1.0, 0.85, 0.7)):
    G.top_veil(c, h, amt, col)


# ------------------------------------------------------------------ shots
def sh_walk(t):
    c = footage(939, 3.0 + t, fx=0.5, fy=0.55, z0=1.12, z1=1.0, k=t / 2.4)
    top_veil(c, 380, 0.35)
    bottom_veil(c)
    god_rays(c, 640, 380, t, 0.16, ang0=1.8, spread=1.4)
    eyebrow_in(c, t, 0.15, True)
    pop(c, token('seedling'), 790, 1080, 300, t, T['small'] - 0.05)
    hand_in(c, 'it starts small', 790, 1350, 58, GOLD, t, T['small'] + 0.35, rot=-5)
    return c


def sh_heritage(t):
    t0 = T['can'] - 0.15
    c = footage(6472, 7.5 + (t - t0), fx=0.5, fy=0.6, z0=1.0, z1=1.1, k=(t - t0) / 2.8)
    top_veil(c, 380, 0.3, (1.0, 0.8, 0.6))
    bottom_veil(c, 0.55)
    god_rays(c, 560, 1000, t, 0.14, ang0=-1.6, spread=2.4, length=1500)
    G.eyebrow(c, dark=True)
    pts = [(120 + u * 760, 1260 - math.sin(u * math.pi * 0.9) * 340) for u in np.linspace(0, 1, 60)]
    line_draw(c, pts, prog(t, t0 + 0.1, T['direction'] + 0.2), GOLD, 8, dashed=True)
    pop(c, token('compass'), 840, 880, 270, t, T['direction'] - 0.05, rot=-10 * math.sin(t * 2))
    return c


def sh_measure(t):
    t0 = T['For'] - 0.15
    c = BACK('morning').copy()
    G.eyebrow(c)
    G.logo_small(c)
    put_arch(c, footage(23392, 1.2 + (t - t0), w=760, h=1000, z0=1.0, z1=1.06, k=(t - t0) / 2.2), W / 2 + 30, 820, 760, 1000, t, t0 - 0.2, rot=1.2)
    k = prog(t, T['child'], T['child'] + 0.8)
    if k > 0:
        x1 = lerp(170, 930, e_inout_cubic(k))
        lay = np.zeros((H, W), np.uint8)
        cv2.line(lay, (170 * 4, 1390 * 4), (int(x1 * 4), 1390 * 4), 255, 4 * 4, cv2.LINE_AA, shift=2)
        cv2.line(lay, (170 * 4, 1365 * 4), (170 * 4, 1415 * 4), 255, 4 * 4, cv2.LINE_AA, shift=2)
        if k >= 1:
            cv2.line(lay, (930 * 4, 1365 * 4), (930 * 4, 1415 * 4), 255, 4 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255
        c[:] = c * (1 - m) + np.array(PURPLE[:3], np.float32) * m
    hand_in(c, 'measuring up the spare room', W / 2 + 20, 1350, 52, PURPLE, t, T['child'] + 0.3, rot=-1.5)
    return c


def cam_room(t):
    """(cx, cy, w) of the miniature over time: slow push-ins on each object, a pull back on 'belong'."""
    keys = [(T['it'] - 0.2, (W / 2, 1010, 1080)), (T['room'], (W / 2, 1020, 1160)), (T['A_bed'], (W / 2, 1040, 1180)),
            (T['bed'] + 0.3, (W / 2 + 60, 1060, 1330)), (T['A_lamp'], (W / 2 + 20, 1050, 1300)), (T['lamp'] + 0.4, (W / 2 - 70, 1090, 1380)),
            (T['A_place'], (W / 2 - 40, 1060, 1320)), (T['belong'] + 0.3, (W / 2, 990, 1060)), (T['And'] - 0.1, (W / 2, 985, 1040))]
    if t <= keys[0][0]:
        return keys[0][1]
    for (a, pa), (b, pb) in zip(keys, keys[1:]):
        if t < b:
            e = e_inout_cubic(prog(t, a, b))
            return tuple(lerp(x, y, e) for x, y in zip(pa, pb))
    return keys[-1][1]


def sh_room_day(t):
    """Boxroom -> cleared -> bed -> lamp -> belong (one continuous miniature shot, morning into afternoon)."""
    kw = prog(t, T['A_lamp'] - 0.3, T['lamp'] + 0.6)
    c = blend(BACK('morning'), BACK('warm'), e_inout_cubic(kw)).copy() if kw > 0 else BACK('morning').copy()
    if t < T['lamp']:
        god_rays(c, 900, 380, t, 0.12, ang0=2.2, spread=0.9, length=1400)
    sp, kc = room_sprite(t)
    cx, cy, w = cam_room(t)
    cx += 10 * math.sin(t * 0.6)
    at = place(c, sp, cx, cy, w)
    # ghost boxes rising during the clear
    if 0 < kc < 1:
        rs = RS('s1')
        gm = DIFF('s1', 's2', 60).astype(np.float32)
        gm = cv2.GaussianBlur(gm, (0, 0), 3)
        ghost = rs * gm[..., None]
        sc = w / rs.shape[1]
        for j, op in enumerate((0.3, 0.18, 0.1)):
            dy = -e_out_cubic(kc) * (220 + j * 170)
            draw(c, blur_sprite(ghost, 1 + j * 3), cx + j * 30 * kc, cy + dy, scale=sc, opacity=op * (1 - kc) * 1.6)
    G.eyebrow(c)
    G.logo_small(c)
    if t < T['room'] + 0.3:
        hand_in(c, 'the boxroom', 300, 520, 70, PURPLE, t, T['it'] + 0.1, rot=-6)
        line_draw(c, curve(at(*A['boxes']), (330, 580)), prog(t, T['it'] + 0.3, T['it'] + 0.8), PURPLE, 3, dot0=True)
    # people inserts: packing, painting
    put_arch(c, footage(31218, 9.0 + (t - T['room']), w=400, h=540), 290, 470, 400, 540, t, T['room'] - 0.05, T['A_bed'] - 0.25, rot=-3)
    put_arch(c, footage(2296, 4.0 + (t - T['room']), w=360, h=480), 790, 420, 360, 480, t, T['room'] + 0.25, T['A_bed'] - 0.15, rot=3)
    if T['room'] < t < T['A_bed']:
        hand_in(c, 'cleared', 300, 790, 60, PURPLE, t, T['room'] + 0.35, rot=-4)
        hand_in(c, 'freshened', 800, 720, 60, PURPLE, t, T['room'] + 0.6, rot=4)
    # bed
    bx, by = at(*A['bed'])
    sparkles(c, t, T['bed'] + 0.25, [(bx - 150, by - 130, 30), (bx + 120, by - 170, 22), (bx + 190, by - 40, 16), (bx - 210, by + 30, 14)])
    if T['bed'] < t < T['A_lamp']:
        hand_in(c, 'fresh sheets', bx - 230, by - 260, 60, PURPLE, t, T['bed'] + 0.2, rot=-6)
    # lamp: real switch inserted, room lamp clicks on with the same beat
    lx, ly = at(*A['lamp'])
    ct = 4.05 - (T['lamp'] - t)
    put_arch(c, footage(46393, ct, w=400, h=540), 300, 470, 400, 540, t, T['A_lamp'] - 0.35, T['A_place'] - 0.2, rot=-2.5)
    kl = flick(t, T['lamp'] + 0.05)
    if kl > 0:
        g = np.exp(-((_X - lx) ** 2 + (_Y - ly) ** 2) / (2 * 140 ** 2))[..., None] * 0.4 * kl
        c[:] = np.clip(c * (1 - g) + np.array([1.0, 0.8, 0.5], np.float32) * g, 0, 1)
        fl = 1 - prog(t, T['lamp'] + 0.05, T['lamp'] + 0.6)
        if fl > 0:
            G.sparkle(c, lx, ly - 20, 60 * fl, (1, 0.9, 0.6, 1))
    if T['lamp'] < t < T['A_place']:
        hand_in(c, 'click.', 600, 400, 84, ORANGE, t, T['lamp'] + 0.05, rot=-8)
    # belong: a heart drawn around the room
    k = prog(t, T['A_place'] + 0.1, T['belong'] + 0.3)
    if k > 0:
        u = np.linspace(0, 2 * math.pi * k, max(3, int(300 * k)))
        hx = 16 * np.sin(u) ** 3
        hy = -(13 * np.cos(u) - 5 * np.cos(2 * u) - 2 * np.cos(3 * u) - np.cos(4 * u))
        pts = np.stack([W / 2 + hx * 31, 950 + hy * 31], 1)
        lay = np.zeros((H, W), np.uint8)
        cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, 6 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255
        g = cv2.GaussianBlur(m[..., 0], (0, 0), 10)[..., None] * 0.5
        c[:] = c * (1 - g) + np.array(WHITE[:3], np.float32) * g
        uu = np.clip(_X / W, 0, 1)[..., None]
        col = np.array(PURPLE[:3], np.float32) * (1 - uu) + np.array(ORANGE[:3], np.float32) * uu
        c[:] = c * (1 - m) + col * m
    pop(c, token('house'), 880, 470, 220, t, T['belong'] - 0.05, rings=True, sparks=True)
    motes(c, t, 0.5)
    return c


def sh_frame(t):
    t0 = T['And'] - 0.1
    k = (t - t0) / 2.4
    base = STILL('frame')
    z = lerp(1.08, 1.0, e_out_cubic(clamp(k)))
    c = cv2.warpAffine(base, np.float32([[z, 0, (1 - z) * 452], [0, z, (1 - z) * 672]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    # rack focus: soft at first, sharp on the empty frame by "leave"
    blur = 9 * (1 - e_inout_cubic(prog(t, t0, T['leave'])))
    if blur > 0.4:
        c = cv2.GaussianBlur(c, (0, 0), blur)
    c = grade(c, 0.6)
    top_veil(c, 300, 0.25, (1, 0.97, 0.94))
    bottom_veil(c, 0.66, 0.7)
    dashed_box(c, 452, 672, 560, 460, t, T['leave'] - 0.1)
    hand_in(c, 'left for them', 470, 960, 80, PURPLE, t, T['them'] - 0.1, rot=-3)
    motes(c, t, 0.45)
    G.eyebrow(c)
    return c


def sh_spaces(t):
    """Their pictures / books / name; then dusk falls and the puzzle locks ("matching sees the whole child")."""
    kd = e_inout_cubic(prog(t, T['At'] + 0.2, T['matching'] + 0.1))
    c = blend(BACK('warm'), BACK('dusk'), kd).copy() if kd > 0 else BACK('warm').copy()
    sp, _ = room_sprite(t)
    t0 = T['Their'] - 0.2
    kz = e_inout_cubic(prog(t, t0, t0 + 1.2))
    w = lerp(1150, 1250, kz)
    cy = lerp(1060, 1080, kz)
    if kd > 0:
        w = lerp(w, 1180, kd)
        cy = lerp(cy, 1060, kd)
    at = place(c, sp, W / 2, cy, w, shadow=0.35 + 0.15 * kd)
    items, cent = ITEMS()
    spots = (('frame', 'frame', T['pictures'], (820, 430)), ('shelf', 'books', T['books'], (420, 440)), ('card', 'doortag', T['name'], (190, 820)))
    fade = 1 - prog(t, T['At'] - 0.1, T['At'] + 0.4)
    if fade > 0:
        for key, tok, t1, (tx, ty) in spots:
            if key not in cent:
                continue
            x, y = at(*cent[key])
            bw = {'frame': 92, 'shelf': 120, 'card': 50}[key] * w / 1250
            bh = {'frame': 74, 'shelf': 40, 'card': 46}[key] * w / 1250
            tmp = c.copy()
            dashed_box(tmp, x, y, bw, bh, t, t1 - 0.05, th=3, dash=9, gap=6, r=6)
            line_draw(tmp, curve((x, y), (tx, ty + 90)), prog(t, t1, t1 + 0.35), PLUM, 3, dot0=True)
            pop(tmp, token(tok), tx, ty, 240, t, t1 + 0.1, rings=False, sparks=True)
            c[:] = c * (1 - fade) + tmp * fade
    # dusk + matching
    if kd > 0:
        G.eyebrow(c, dark=kd > 0.5)
        pop(c, token('puzzle'), W / 2 + 10, 440, 340, t, T['matching'] - 0.05, col=GOLD)
        hand_in(c, 'the whole child', W / 2, 640, 70, GOLD, t, T['whole'] - 0.05, rot=-3)
        if kd > 0.5:
            lg = LOGO_W()
            draw(c, lg, 930, 150, scale=200 / lg.shape[1], opacity=prog(t, T['matching'], T['matching'] + 0.4))
    else:
        G.eyebrow(c)
        G.logo_small(c)
    motes(c, t, 0.35 + 0.3 * kd, (1, 0.88, 0.7))
    return c


ORBIT = (('globe', 'Culture', 'culture'), ('lantern', 'Faith', 'faith'), ('speech', 'Language', 'language'),
         ('rings', 'Relationships', 'relationships'), ('fingerprint', 'Identity', 'identity'))


def sh_orbit(t):
    t0 = T['culture'] - 0.3
    c = BACK('dusk').copy()
    k = e_inout_cubic(prog(t, t0, t0 + 0.8))
    sp = RS('s6')
    place(c, sp, W / 2, lerp(1060, 1000, k), lerp(1180, 820, k), shadow=0.5)
    cx, cy, rx, ry = W / 2, 930, 410, 520
    spin = (t - t0) * 0.06
    for i, (tok, lab, key) in enumerate(ORBIT):
        a = math.radians(-160 + i * 70) + spin
        x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry * 0.78 - 60
        t1 = T[key] - 0.05
        pop(c, token(tok), x, y, 170, t, t1, rings=True, sparks=False, col=GOLD)
        kl = prog(t, t1 + 0.1, t1 + 0.4)
        if kl > 0:
            s = ts(lab, N9, 36, WHITE)
            e = e_out_back(kl)
            draw(c, rrect(s.shape[1] + 34, 54, 27, (0.72, 0.0, 0.43, 0.92)), x, y + 118, scale=e)
            draw(c, s, x, y + 118, scale=e)
    # "matter": the tokens pulse together
    km = prog(t, T['matter'], T['matter'] + 0.6)
    if 0 < km < 1:
        g = np.exp(-((_X - cx) ** 2 + (_Y - cy) ** 2) / (2 * (300 + 600 * km) ** 2))[..., None] * 0.25 * (1 - km)
        c[:] = np.clip(c + g * np.array([1, 0.8, 0.5], np.float32), 0, 1)
    G.eyebrow(c, dark=True)
    motes(c, t, 0.5, (1, 0.88, 0.7))
    return c


def sh_landing(t):
    t0 = T['You'] - 0.2
    k = clamp((t - t0) / 3.2)
    base = STILL('landing')
    z = lerp(1.0, 1.1, e_inout_cubic(k))
    c = cv2.warpAffine(base, np.float32([[z, 0, (1 - z) * 640], [0, z, (1 - z) * 1100]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    c = grade(c, 1.0)
    fl = 0.2 + 0.03 * math.sin(t * 7.3) + 0.02 * math.sin(t * 13.1)
    g = np.exp(-((_X - 640) ** 2 + (_Y - 1250) ** 2) / (2 * 330 ** 2))[..., None] * fl
    c[:] = c * (1 - g) + np.array([1.0, 0.75, 0.45], np.float32) * g
    god_rays(c, 660, 760, t, 0.1, col=(1, 0.75, 0.45), ang0=2.0, spread=1.2, length=1200)
    put_arch(c, footage(39803, 2.5 + (t - t0), w=380, h=520), 300, 520, 380, 520, t, t0 + 0.2, rot=-2)
    pop(c, token('phone'), 800, 470, 230, t, T['call'] - 0.05, col=GOLD)
    motes(c, t, 0.45, (1, 0.85, 0.6))
    G.eyebrow(c, dark=True)
    return c


def sh_end(t):
    t0 = T['Start'] - 0.25
    base = STILL('landing')
    c = grade(base, 1.0)
    kb = prog(t, t0, t0 + 0.6)
    c = cv2.GaussianBlur(c, (0, 0), 0.5 + 6 * kb)
    c = c * (1 - 0.15 * kb)
    k = prog(t, t0, t0 + 0.55)
    e = e_out_back(k, 1.4)
    cw, ch = 940, 1080
    yy = 960 + (1 - e_out_cubic(k)) * 900
    card = rrect(cw, ch, 48, CREAM)
    draw(c, blur_sprite(tint(card, (0.1, 0.02, 0.08)), 40), W / 2, yy + 30, opacity=0.6 * k)
    draw(c, card, W / 2, yy)
    dy = yy - 960
    lg = LOGO()
    kl = prog(t, t0 + 0.3, t0 + 0.7)
    if kl > 0:
        draw(c, lg, W / 2, 610 + dy, scale=620 / lg.shape[1] * e_out_back(kl, 1.5), opacity=min(1, kl * 2))
    hand_in(c, 'there’s room to grow', W / 2, 800 + dy, 74, ORANGE, t, t0 + 0.55, rot=-3)
    kt = prog(t, t0 + 0.6, t0 + 0.9)
    if kt > 0:
        draw(c, ts('You don’t need every answer', N9, 46, PLUM), W / 2, 905 + dy + (1 - kt) * 20, opacity=kt)
        draw(c, ts('before you call.', N9, 46, PLUM), W / 2, 965 + dy + (1 - kt) * 20, opacity=kt)
    kbt = prog(t, T['enquiry'] - 0.1, T['enquiry'] + 0.3)
    if kbt > 0:
        eb = e_out_back(kbt, 2.0)
        btn = F.grad_spr(700, 124, 62, phase=(t * 0.15) % 1)
        pulse = 1 + 0.025 * math.sin((t - T['enquiry']) * 4) * prog(t, T['enquiry'] + 0.5, T['enquiry'] + 0.9)
        draw(c, blur_sprite(btn, 22), W / 2, 1110 + 18 + dy, scale=eb * pulse, opacity=0.5)
        draw(c, btn, W / 2, 1110 + dy, scale=eb * pulse)
        tmp = np.zeros((140, 720, 4), np.float32)
        sx = ts('Start your enquiry', N9, 50, WHITE)
        ar = F.arrow(WHITE, 50)
        tw = sx.shape[1] + 16 + ar.shape[1]
        paste_spr(tmp, sx, 360 - tw / 2 + sx.shape[1] / 2, 70)
        paste_spr(tmp, ar, 360 + tw / 2 - ar.shape[1] / 2 + 8 * max(0, math.sin((t - T['enquiry']) * 5)), 72)
        draw(c, tmp, W / 2, 1110 + dy, scale=eb * pulse)
        # light sweep across the button
        sw = prog(t, T['enquiry'] + 0.4, T['enquiry'] + 1.1)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(200, 880, sw) - (_Y - 1110 - dy) * 0.4) / 40) ** 2) * (np.abs(_Y - 1110 - dy) < 58)
            c[:] = np.clip(c + band[..., None] * 0.35, 0, 1)
    kf = prog(t, T['enquiry'] + 0.4, T['enquiry'] + 0.8)
    if kf > 0:
        draw(c, rrect(cw - 140, 2, 1, (0.36, 0.09, 0.31, 0.25)), W / 2, 1250 + dy, opacity=kf)
        s1 = ts('organicfostering.co.uk', N8, 34, PLUM)
        s2 = ts('0161 241 1332', N9, 38, PURPLE)
        draw(c, s1, W / 2 - cw / 2 + 70 + s1.shape[1] / 2, 1320 + dy + (1 - kf) * 16, opacity=kf)
        draw(c, s2, W / 2 + cw / 2 - 70 - s2.shape[1] / 2, 1320 + dy + (1 - kf) * 16, opacity=kf)
    pop(c, token('doortag'), 860, 1520, 170, t, T['enquiry'] + 0.6, rings=False, sparks=True, rot=8 + 6 * math.sin(t * 2.2), bob=4)
    return c


def shots():
    return [
        (0.0, T['can'] - 0.15, sh_walk),
        (T['can'] - 0.15, T['For'] - 0.15, sh_heritage),
        (T['For'] - 0.15, T['it'] - 0.2, sh_measure),
        (T['it'] - 0.2, T['And'] - 0.1, sh_room_day),
        (T['And'] - 0.1, T['Their'] - 0.2, sh_frame),
        (T['Their'] - 0.2, T['culture'] - 0.3, sh_spaces),
        (T['culture'] - 0.3, T['You'] - 0.2, sh_orbit),
        (T['You'] - 0.2, T['Start'] - 0.25, sh_landing),
        (T['Start'] - 0.25, DUR + 1, sh_end),
    ]


SHOTS = None


# ------------------------------------------------------------------ transitions
def tr_flare(a, b, p):
    """Sun flare: a warm bloom washes over and leaves the next shot."""
    e = e_inout_cubic(p)
    k = math.sin(math.pi * p)
    out = a * (1 - e) + b * e
    g = np.exp(-((_X - 700) ** 2 + (_Y - 500) ** 2) / (2 * (300 + 900 * k) ** 2))[..., None] * k
    return np.clip(out + g * np.array([1.0, 0.82, 0.55], np.float32) * 1.1, 0, 1)


def tr_tape(a, b, p):
    """A wide strip of tape pulls across on the diagonal and reveals the next shot."""
    e = e_inout_cubic(p)
    pos = lerp(-700, W + 900, e)
    d = (_X - pos) + (_Y - H / 2) * 0.35
    m = (d < 0).astype(np.float32)
    band = ((d > -170) & (d < 0)).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]
    out = a * (1 - m) + b * m
    band = cv2.GaussianBlur(band, (0, 0), 1.2)[..., None]
    tape = np.array(CREAM[:3], np.float32) * 0.97
    out = out * (1 - band * 0.92) + tape * band * 0.92
    return out


def tr_archgrow(a, b, p):
    """The arch doorway grows to fill the frame (into the room)."""
    e = e_in_cubic(p)
    w = 760 + e * 2400
    h = 1000 + e * 3000
    cx, cy = W / 2 + 30, 820 + e * 200
    xr = (_X - cx) / (w / 2)
    top = cy - h / 2
    inside = (np.abs(xr) <= 1) & ((_Y >= top + w / 2) | (((_Y - (top + w / 2)) / (w / 2)) ** 2 + xr ** 2 <= 1)) & (_Y <= cy + h / 2)
    m = cv2.GaussianBlur(inside.astype(np.float32), (0, 0), 2)[..., None]
    return a * (1 - m) + b * m


def tr_zoom(a, b, p):
    """Push into the room (zoom blur) and arrive on the close-up."""
    src = a if p < 0.5 else b
    sp = math.sin(math.pi * p)
    cx, cy = (650, 760) if p < 0.5 else (452, 672)
    acc = src.copy()
    for k in range(1, 6):
        z = 1 + 0.05 * k * sp + (0.25 * p if p < 0.5 else 0)
        acc += cv2.warpAffine(src, np.float32([[z, 0, (1 - z) * cx], [0, z, (1 - z) * cy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    out = acc / 6
    return np.clip(out + (1 - abs(p - 0.5) * 2) ** 3 * 0.3, 0, 1)


def tr_whip(a, b, p):
    return R.whip(a, b, p, 1)


def tr_dusk(a, b, p):
    e = e_inout_cubic(p)
    return a * (1 - e) + b * e


def tr_door(a, b, p):
    """A door swings open (hinged at the left) onto the landing; its edge glows warm."""
    e = e_inout_cubic(p)
    x_edge = lerp(W, 0, e)
    persp = (1 - e) * 0.18
    top = (_Y < (H * persp * (_X / W)))
    door = (_X < x_edge)
    m = door.astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 1.5)[..., None]
    shade = 1 - 0.55 * e
    out = b * (1 - m) + a * shade * m
    g = np.exp(-((_X - x_edge) / 24) ** 2)[..., None]
    return np.clip(out + g * np.array([1.0, 0.75, 0.42], np.float32) * 0.9, 0, 1)


def tr_card(a, b, p):
    e = e_inout_cubic(p)
    return a * (1 - e) + b * e


TRANS = [(tr_flare, 0.6), (tr_tape, 0.55), (tr_archgrow, 0.55), (tr_zoom, 0.5), (tr_whip, 0.36), (tr_dusk, 0.5), (tr_door, 0.7),
         (tr_card, 0.4)]


def hits():
    return [(T['small'], 0.7, 0), (T['direction'], 0.7, 0), (T['room'], 1.0, 6), (T['bed'] + 0.25, 0.9, 6), (T['lamp'] + 0.05, 0.7, 0),
            (T['belong'], 0.6, 0), (T['pictures'] + 0.1, 0.5, 0), (T['books'] + 0.1, 0.5, 0), (T['name'] + 0.1, 0.5, 0),
            (T['matching'], 0.8, 4), (T['culture'], 0.35, 0), (T['faith'], 0.35, 0), (T['language'], 0.35, 0),
            (T['relationships'], 0.35, 0), (T['identity'], 0.35, 0), (T['matter'], 0.8, 0), (T['call'], 0.7, 0), (T['enquiry'], 0.9, 4)]


HITS = None


def energy(t):
    z, sx, sy, ca = 1.0, 0.0, 0.0, 0.0
    for th, pn, sh in HITS:
        d = t - th
        if 0 <= d < 0.3:
            e = (1 - d / 0.3) ** 2
            z += 0.03 * pn * e
            ca = max(ca, 3 * pn * e)
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
    c = c.copy()
    dark = t > T['At'] + 0.5
    if t < T['Start'] - 0.25:
        ruler(c, t, dark)
        captions(c, t)
    z, sx, sy, _ = energy(t)
    z *= 1.0 + 0.006 * math.sin(t * 0.8)
    if z > 1.001 or abs(sx) + abs(sy) > 0.5:
        M = np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    if t < 0.4:
        c = c * e_out_cubic(prog(t, 0, 0.4))
    if t > DUR - 0.8:
        c = c * (1 - 0.6 * e_inout_cubic(prog(t, DUR - 0.8, DUR)))
    return c


def render(fi):
    t = fi / FPS
    c = render_raw(t)
    _, _, _, ca = energy(t)
    return post(c, fi, bloom=0.14, grain=0.012, vig=0.24, ca=ca)


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
