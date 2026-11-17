"""Organic Fostering Reel 01 "The Recipe That Wasn't on the Menu" (9:16, ~35 s). ElevenLabs voice (IDA, Northern woman).

Every cut is one of the six looks, and each look also lives inside its shot:
  retro_pan -> retro_hands   RETRO      film-roll slip with a gate flash and burn
  retro_hands -> writing     ECLIPSE    a dark moon slides over the memory, corona flare, the present inside the disc
  writing -> spices          LAYERCUT   paper-cut layers slide in from alternate sides
  spices -> explainer        EXPLAINER  a hand-drawn marker ring grows from the pan and reveals the next shot
  explainer -> stir          SPIRAL     the frame twists into a vortex and unwinds into the next
  stir -> cutter             SPIRAL     (second spiral, opposite direction)
  cutter -> aurora           AURORA     a curtain of brand-colour aurora light sweeps up
  aurora -> table            LAYERCUT   paper layers again, leaf pattern beneath
  table -> roots             ECLIPSE    plum disc closes in, ring flare
  roots -> end card          AURORA     a soft aurora glow wipe to ivory
3D objects are 24-angle turntables; captions are the PDF script word for word.

Usage: python3 reel_recipe.py still 1.0,5.0 | python3 reel_recipe.py range 0 100 | python3 reel_recipe.py times
"""
import os, sys, math, json, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_recipe as G
from frames_recipe import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, cover, warm, rounded,
                           PLUM, MAG, ORANGE, GREEN, IVORY, PAPER, BLUSH, PEACH, LEAFT, INK, ORANGE_INK, GREEN_INK, WHITE, N8, N7, HAND,
                           retro, eclipse, layercut, spiral, aurora, label, leaf_pattern, colour_bar, shade, top_shade, LOGO)
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, post

FPS = 30
S = G.S
DUR = 35.5
NF = int(DUR * FPS)
_X, _Y = R._X, R._Y
WORDS = [tuple(w) for w in json.load(open(f'{S}/tts/info.json'))['words']]
SCRIPT = ("She had made this meal a hundred times. But tonight, she made it differently. A different ingredient. "
          "A familiar flavour. A recipe worth learning. Because caring for a child isn't about asking them to become like you. "
          "It's about understanding who they already are. At Organic Fostering, culture, faith and identity matter. "
          "Room to grow. Roots to keep. Start your enquiry with Organic Fostering.").split()
assert len(SCRIPT) == len(WORDS), (len(SCRIPT), len(WORDS))


def WT(i):
    return WORDS[i][1]


PHRASES = [  # (first, last word index, highlight words, highlight colour, light background?)
    (0, 7, ('hundred',), ORANGE), (8, 13, ('tonight', 'differently'), MAG), (14, 16, ('different', 'ingredient'), ORANGE),
    (17, 19, ('familiar',), MAG), (20, 23, ('learning',), GREEN), (24, 36, ('like', 'you'), MAG),
    (37, 43, ('already', 'are'), GREEN), (44, 51, ('culture', 'faith', 'identity'), MAG), (52, 57, ('grow', 'keep'), MAG),
    (58, 63, ('enquiry',), MAG),
]


# ------------------------------------------------------------------ shot timing (from the voice)
SH = {}
SH['pan'] = (0.0, WT(7) + 0.35)
SH['hands'] = (SH['pan'][1], WT(8) - 0.1)
SH['writing'] = (SH['hands'][1], WT(14) - 0.35)
SH['spices'] = (SH['writing'][1], WT(17) - 0.3)
SH['explain'] = (SH['spices'][1], WT(24) - 0.3)
SH['stir'] = (SH['explain'][1], WT(31) - 0.2)
SH['cutter'] = (SH['stir'][1], WT(37) - 0.25)
SH['aurora'] = (SH['cutter'][1], WT(44) - 0.35)
SH['table'] = (SH['aurora'][1], WT(52) - 0.3)
SH['roots'] = (SH['table'][1], WT(58) - 0.45)
SH['end'] = (SH['roots'][1], DUR + 1)
ORDER = ['pan', 'hands', 'writing', 'spices', 'explain', 'stir', 'cutter', 'aurora', 'table', 'roots', 'end']


# ------------------------------------------------------------------ footage
class Clip:
    def __init__(self, cid):
        self.cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pos = -1
        self.cache = {}

    def frame(self, t):
        t = t % max(0.5, self.n / self.fps - 0.1)
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


def footage(cid, ct, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    im = _clips[cid].frame(ct).astype(np.float32)[..., ::-1] / 255
    return warm(cover(im, fx, fy, z, w, h))


# ------------------------------------------------------------------ 3D turntable objects
@functools.lru_cache(maxsize=None)
def _frames(name):
    return sorted(glob.glob(f'{S}/spin/{name}/*.png'))


@functools.lru_cache(maxsize=400)
def _load(p):
    return load_png_sprite(p)


@functools.lru_cache(maxsize=None)
def _crop(name):
    acc = None
    for f in _frames(name)[::3]:
        a = _load(f)[..., 3] > 0.01
        acc = a if acc is None else (acc | a)
    ys, xs = np.where(acc)
    return max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5


FLAT = {'recipecard', 'culture', 'identity', 'cutter'}


def spin(name, ang):
    fs = _frames(name)
    if not fs:
        return G.token(name)
    if name in FLAT:
        ang = 32 * math.sin(math.radians(ang))
    i = int(round((ang % 360) / 360 * len(fs))) % len(fs)
    y0, y1, x0, x1 = _crop(name)
    return _load(fs[i])[y0:y1, x0:x1]


def obj(c, name, x, y, size, t, t0, rot=0, rays=True, col=ORANGE, spin_speed=50, t1=None):
    """3D object pops in on its word with a fast spin-in, gold rays, then keeps turning slowly and bobbing."""
    k = prog(t, t0, t0 + 0.45)
    if k <= 0:
        return
    ko = prog(t, t1, t1 + 0.25) if t1 else 0
    if ko >= 1:
        return
    e = e_out_back(min(1, k), 2.0) * (1 - 0.3 * ko)
    ang = (t - t0) * spin_speed + (1 - e_out_cubic(k)) * 320
    sp = spin(name, ang)
    sc = size / max(sp.shape[:2]) * e
    yy = y + 7 * math.sin((t - t0) * 2.0) + (1 - e_out_cubic(k)) * 70
    op = min(1, k * 2.5) * (1 - ko)
    if rays and k < 1:
        kr = e_out_cubic(prog(t, t0, t0 + 0.5))
        lay = np.zeros((H, W), np.uint8)
        r0 = size * 0.5 + kr * 30
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = (26 if j % 2 else 44) * (1 - kr * 0.5)
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((yy + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + ln)) * 4), int((yy + math.sin(a) * (r0 + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.85 * (1 - kr * 0.6)
        c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    draw(c, blur_sprite(tint(sp, PLUM[:3]), 20), x + 8, yy + 24, scale=sc, rot=rot, opacity=0.45 * op)
    draw(c, sp, x, yy, scale=sc, rot=rot, opacity=op)


# ------------------------------------------------------------------ animated text helpers
def write_on(c, s, x, y, size, col, t, t0, dur=0.6, rot=-3, font=HAND):
    """Handwriting reveal: the word is uncovered left to right like a pen stroke."""
    k = prog(t, t0, t0 + dur)
    if k <= 0:
        return
    m = _wmask(s, font, size)
    sp = solid(m, col)
    ramp = np.clip((e_inout_cubic(k) * (sp.shape[1] + 30) - np.arange(sp.shape[1])) / 18, 0, 1)[None, :, None].astype(np.float32)
    draw(c, blur_sprite(solid(m, (0.1, 0.02, 0.08, 1)) * ramp, 10), x + 4, y + 8, rot=rot, opacity=0.55)
    draw(c, sp * ramp, x, y, rot=rot)


def tag_pop(c, text, x, y, t, t0, fill=PAPER, ink=PLUM, leaf=MAG, size=36, rot=-3):
    k = prog(t, t0, t0 + 0.35)
    if k <= 0:
        return
    tmp = np.zeros((H, W, 3), np.float32)
    s = ts(text, N8, size, ink)
    p = rrect(s.shape[1] + 86, s.shape[0] + 34, (s.shape[0] + 34) / 2, fill).copy()
    lf = np.zeros((40, 40), np.uint8)
    cv2.ellipse(lf, (20, 20), (16, 8), -45, 0, 360, 255, -1, cv2.LINE_AA)
    paste_spr(p, solid(lf.astype(np.float32) / 255, leaf), 38, p.shape[0] / 2)
    paste_spr(p, s, 62 + s.shape[1] / 2, p.shape[0] / 2)
    e = e_out_back(k, 2.0)
    draw(c, blur_sprite(tint(p, (0.15, 0.03, 0.12)), 12), x + 6, y + 10, rot=rot, scale=e, opacity=0.45 * min(1, k * 2))
    draw(c, p, x, y, rot=rot, scale=e, opacity=min(1, k * 2))


def ring_draw(c, x, y, rx, ry, k, col=WHITE, th=6, rot=-8, dashed=True):
    if k <= 0:
        return
    lay = np.zeros((H, W), np.uint8)
    n = 48
    for i in range(int(n * min(1, k))):
        if dashed and i % 2:
            continue
        a0, a1 = i / n * 360, (i + 1) / n * 360
        cv2.ellipse(lay, (int(x * 4), int(y * 4)), (int(rx * 4), int(ry * 4)), rot, a0 - 90, a1 - 90, 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def arrow_draw(c, p0, p1, k, col=WHITE, th=6, bend=60):
    if k <= 0:
        return
    pts = [(p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u - bend * math.sin(math.pi * u)) for u in np.linspace(0, 1, 30)]
    n = max(2, int(len(pts) * min(1, k)))
    lay = np.zeros((H, W), np.uint8)
    for i in range(0, n - 1, 2):
        cv2.line(lay, (int(pts[i][0] * 4), int(pts[i][1] * 4)), (int(pts[i + 1][0] * 4), int(pts[i + 1][1] * 4)), 255, th * 4, cv2.LINE_AA, shift=2)
    if k >= 1:
        ex, ey = pts[-1]
        px, py = pts[-3]
        a = math.atan2(ey - py, ex - px)
        for s_ in (1, -1):
            cv2.line(lay, (int(ex * 4), int(ey * 4)), (int((ex - 34 * math.cos(a + s_ * 0.5)) * 4), int((ey - 34 * math.sin(a + s_ * 0.5)) * 4)),
                     255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


@functools.lru_cache(maxsize=512)
def wm(w, size):
    return _wmask(w, N8, size)


def captions(c, t, y=1560, size=62):
    for a, b, keys, hl in PHRASES:
        t0 = WT(a) - 0.12
        t1 = WT(PHRASES[PHRASES.index((a, b, keys, hl)) + 1][0]) - 0.15 if b < len(WORDS) - 1 else DUR
        if not (t0 <= t < t1 + 0.2) or a >= 52:              # roots + end card: the big type already says it
            continue
        out = prog(t, t1 - 0.05, t1 + 0.2)
        ws = list(range(a, b + 1))
        # wrap into lines that fit
        sz = size
        lines = [ws]
        if sum(wm(SCRIPT[i], sz).shape[1] for i in ws) + sz * 0.24 * (len(ws) - 1) > W - 130:
            best = None
            for cut in range(1, len(ws)):
                l1, l2 = ws[:cut], ws[cut:]
                w1 = sum(wm(SCRIPT[i], sz).shape[1] for i in l1) + sz * 0.24 * (len(l1) - 1)
                w2 = sum(wm(SCRIPT[i], sz).shape[1] for i in l2) + sz * 0.24 * (len(l2) - 1)
                score = max(w1, w2)
                if best is None or score < best[0]:
                    best = (score, [l1, l2])
            lines = best[1]
            while best[0] > W - 130 and sz > 40:
                sz -= 2
                best = (max(sum(wm(SCRIPT[i], sz).shape[1] for i in l) + sz * 0.24 * (len(l) - 1) for l in lines), lines)
        light = t >= SH['cutter'][0] and t < SH['aurora'][0] or (SH['table'][0] + 0.3 <= t < SH['table'][1])
        col = PLUM if light else WHITE
        yy0 = y if t < SH['end'][0] else 1620
        for li, line in enumerate(lines):
            ms = [wm(SCRIPT[i], sz) for i in line]
            tw = sum(m.shape[1] for m in ms) + sz * 0.24 * (len(ms) - 1)
            x = W / 2 - tw / 2
            yy = yy0 + li * sz * 1.24
            for i, m in zip(line, ms):
                k = prog(t, WT(i) - 0.08, WT(i) + 0.16)
                if k > 0:
                    op = min(1, k * 1.8) * (1 - out)
                    dy = (1 - e_out_cubic(k)) * 16 - out * 14
                    cx = x + m.shape[1] / 2
                    key = SCRIPT[i].strip('.,?…:').lower() in keys
                    if key:
                        kh = e_out_back(prog(t, WT(i), WT(i) + 0.28), 1.8)
                        draw(c, rrect(m.shape[1] + 22, sz * 1.14, 18, hl), cx, yy + 3 + dy, scale=max(0.01, kh), opacity=op)
                    elif not light:
                        draw(c, blur_sprite(solid(m, (0.1, 0.02, 0.08, 1)), 9), cx + 3, yy + 7 + dy, opacity=0.55 * op)
                    draw(c, solid(m, WHITE if key else col), cx, yy + dy, opacity=op)
                x += m.shape[1] + sz * 0.24


# ------------------------------------------------------------------ shots
def tally(c, t, t0, t1, col=(1, 0.92, 0.78)):
    """Tally marks drawing themselves one by one: twenty, as the memory counts up."""
    n = int(20 * prog(t, t0, t1))
    lay = np.zeros((H, W), np.uint8)
    for j in range(n):
        g, i = divmod(j, 5)
        x0 = 200 + g * 150
        if i < 4:
            cv2.line(lay, ((x0 + i * 24) * 4, 1190 * 4), ((x0 + i * 24 - 5) * 4, 1280 * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
        else:
            cv2.line(lay, ((x0 - 16) * 4, 1262 * 4), ((x0 + 92) * 4, 1206 * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col, np.float32) * m


def counter(c, t, t0, t1, x=500, y=470):
    v = int(round(lerp(1, 100, e_inout_cubic(prog(t, t0, t1)))))
    write_on(c, "She'd made this", 420, 330, 80, (1, 0.93, 0.8, 1), t, 0.5, 0.7)
    if t > t0:
        s = f'{v} times.'
        sp = solid(_wmask(s, HAND, 110), (1, 0.6, 0.2, 1))
        draw(c, blur_sprite(solid(_wmask(s, HAND, 110), (0.1, 0.02, 0.08, 1)), 10), x + 4, y + 8, rot=-4, opacity=0.6)
        draw(c, sp, x, y, rot=-4)


def sh_pan(t):
    c = footage('3806', 3.0 + t * 0.8, 0.5, 0.5, 1.12 + 0.02 * t)
    c = retro(c, t, seed=1)
    counter(c, t, 0.9, WT(7))
    tally(c, t, 0.9, WT(7))
    obj(c, 'pot', 800, 1040, 260, t, WT(4) - 0.05, rays=False, spin_speed=40)
    G.date_stamp(c, "'98")
    return c


def sh_hands(t):
    t0 = SH['hands'][0]
    c = footage('26660', 5.5 + (t - t0), 0.5, 0.5, 1.0)
    c = retro(c, t, seed=4)
    write_on(c, 'same routine', 380, 360, 72, (1, 0.93, 0.8, 1), t, t0 + 0.1, 0.5)
    G.date_stamp(c, "'04")
    return c


def sh_writing(t):
    t0 = SH['writing'][0]
    c = footage('42655', 2.0 + (t - t0), 0.45, 0.5, 1.05 + 0.02 * (t - t0))
    c = top_shade(c)
    write_on(c, 'But tonight…', 360, 380, 100, WHITE, t, WT(9), 0.8, rot=-4)
    obj(c, 'recipecard', 700, 780, 440, t, WT(13) - 0.05, rot=4, col=MAG)
    return shade(c)


def sh_spices(t):
    t0 = SH['spices'][0]
    base = footage('32058', 2.0 + (t - t0) * 0.8, 0.5, 0.5, 1.05)
    k = 0.35 + 0.65 * e_out_back(prog(t, WT(15) - 0.1, WT(15) + 0.5), 1.4)       # layers part on "different"
    c = layercut(base, k)
    obj(c, 'spicejar', 540, 900, 380, t, WT(16) - 0.05)
    tag_pop(c, 'new ingredient', 540, 1210, t, WT(16) + 0.2, fill=PEACH, ink=ORANGE_INK, leaf=ORANGE)
    return c


def sh_explain(t):
    t0 = SH['explain'][0]
    c = footage('32504', 7.0 + (t - t0), 0.5, 0.5, 1.0)
    c = top_shade(c)
    ring_draw(c, 470, 930, 300, 300, prog(t, WT(18) - 0.1, WT(18) + 0.6), WHITE, 6)
    arrow_draw(c, (840, 520), (640, 760), prog(t, WT(18) + 0.2, WT(18) + 0.7), WHITE, 6)
    tag_pop(c, 'familiar flavour', 760, 470, t, WT(18), fill=BLUSH, ink=PLUM, leaf=MAG)
    obj(c, 'bowl', 860, 1060, 240, t, WT(19) - 0.05, rays=False)
    for i, (txt, col, lf, ink) in enumerate((('1  spice', PEACH, ORANGE, ORANGE_INK), ('2  stir', BLUSH, MAG, PLUM), ('3  taste', LEAFT, GREEN, GREEN_INK))):
        tag_pop(c, txt, 230 + i * 300, 1300, t, WT(21) + i * 0.3, fill=col, ink=ink, leaf=lf, size=34, rot=(-4, 2, -2)[i])
    write_on(c, 'A recipe worth learning.', 540, 300, 76, WHITE, t, WT(20), 0.9, rot=-2)
    return shade(c, 0.7)


def sh_stir(t):
    t0 = SH['stir'][0]
    c = footage('47555', 8.0 + (t - t0), 0.5, 0.5, 1.05 + 0.03 * (t - t0))
    c = top_shade(c)
    obj(c, 'pot', 820, 520, 220, t, WT(28) - 0.05, rays=False, spin_speed=60)
    return shade(c)


STARS = [(300, 700, PEACH, -10), (540, 640, BLUSH, 0), (780, 700, LEAFT, 12)]


@functools.lru_cache(maxsize=4)
def star_spr(col_i):
    st = np.zeros((220, 220), np.uint8)
    pts = np.array([[110 + (95 if j % 2 == 0 else 45) * math.sin(j * math.pi / 5), 110 - (95 if j % 2 == 0 else 45) * math.cos(j * math.pi / 5)]
                    for j in range(10)], np.int32)
    cv2.fillPoly(st, [pts], 255, cv2.LINE_AA)
    return solid(st.astype(np.float32) / 255, STARS[col_i][2])


def sh_cutter(t):
    """The cutter stamps the same star three times (on 'asking', 'them', 'become'), then a ring loops the copies."""
    t0 = SH['cutter'][0]
    c = leaf_pattern().copy()
    stamps = [WT(31), WT(33), WT(35)]
    cx, cy, press = 540, 1000, 0.0
    for j, ts_ in enumerate(stamps):
        x, y, col, rot = STARS[j]
        if t >= ts_ + 0.12:
            k = e_out_back(prog(t, ts_ + 0.12, ts_ + 0.4), 2.0)
            draw(c, blur_sprite(tint(star_spr(j), PLUM[:3]), 12), x + 6, y + 10, rot=rot, scale=k, opacity=0.35)
            draw(c, star_spr(j), x, y, rot=rot, scale=k)
    # cutter travels to each stamp position and presses down
    pos = [(540, 1050)] + [(x, y) for x, y, _, _ in STARS]
    times = [t0] + stamps
    seg = 0
    for j in range(len(times)):
        if t >= times[j] - 0.3:
            seg = j
    if seg == 0:
        cx, cy = pos[0]
    else:
        pa = pos[seg - 1] if seg > 1 else (540, 1050)
        pb = pos[seg]
        kk = e_inout_cubic(prog(t, times[seg] - 0.3, times[seg]))
        cx, cy = lerp(pa[0], pb[0], kk), lerp(pa[1], pb[1], kk) - 120 * math.sin(math.pi * kk)
        press = math.exp(-((t - times[seg] - 0.08) / 0.07) ** 2)
    if t > WT(36):
        lift = e_in_cubic(prog(t, WT(36) + 0.1, WT(36) + 0.6))
        cy -= lift * 900
    obj(c, 'cutter', cx, cy - 40 + 30 * press, 300 * (1 - 0.08 * press), t, t0 + 0.05, rays=False, spin_speed=30)
    ring_draw(c, 540, 680, 380, 170, prog(t, WT(35) + 0.2, WT(36) + 0.4), MAG, 6, rot=0)
    return c


def sh_aurora(t):
    t0 = SH['aurora'][0]
    c = aurora(t * 0.8)
    k = prog(t, WT(39) - 0.1, WT(39) + 0.5)
    grow = 1 + 0.12 * e_inout_cubic(prog(t, WT(39), SH['aurora'][1]))
    obj(c, 'seedling', 540, 1010, 600 * grow, t, WT(38), rays=False, spin_speed=25)
    write_on(c, 'Who they are matters.', 540, 460, 92, WHITE, t, WT(42) - 0.1, 1.0, rot=-2)
    return c


def sh_table(t):
    t0 = SH['table'][0]
    c = leaf_pattern().copy()
    z = 1.0 + 0.03 * (t - t0)
    ph = rounded(footage('45977', 2.0 + (t - t0) * 0.9, 0.55, 0.5, z, 900, 620), 40)
    draw(c, blur_sprite(tint(ph, PLUM[:3]), 24), 552, 560, opacity=0.4)
    draw(c, ph, 540, 540)
    for i, (o, lab, x, fill, ink, lf, wi) in enumerate((('culture', 'Culture', 210, PEACH, ORANGE_INK, ORANGE, 47),
                                                       ('lantern', 'Faith', 540, BLUSH, PLUM, MAG, 48),
                                                       ('identity', 'Identity', 870, LEAFT, GREEN_INK, GREEN, 50))):
        obj(c, o, x, 1050, 250, t, WT(wi) - 0.05, col=(ORANGE, MAG, GREEN)[i])
        tag_pop(c, lab, x, 1250, t, WT(wi) + 0.15, fill=fill, ink=ink, leaf=lf, size=38, rot=(-4, 2, -3)[i])
    return c


def sh_roots(t):
    t0 = SH['roots'][0]
    c = np.ones((H, W, 3), np.float32) * np.array(PLUM[:3], np.float32)
    kk = (_Y / H)[..., None]
    c = c * (1 - 0.25 * kk) + np.array([0.12, 0.03, 0.1], np.float32) * 0.25 * kk
    g = np.exp(-(((_X - 540) / 500) ** 2 + ((_Y - 860) / 600) ** 2))[..., None]
    c = c + g * np.array(MAG[:3], np.float32) * 0.18
    for j in range(16):                                         # drifting leaves
        rng = np.random.default_rng(j)
        x = (rng.uniform(0, W) + 40 * math.sin(t * 0.7 + j)) % W
        y = (rng.uniform(0, H) - 60 * (t - t0)) % H
        lf = np.zeros((40, 40), np.uint8)
        cv2.ellipse(lf, (20, 20), (16, 7), int(45 + 40 * math.sin(t + j)), 0, 360, 255, -1, cv2.LINE_AA)
        draw(c, solid(lf.astype(np.float32) / 255, (MAG, GREEN, ORANGE)[j % 3]), x, y, opacity=0.35)
    grow = 0.85 + 0.15 * e_out_cubic(prog(t, t0, t0 + 1.5))
    obj(c, 'seedling', 540, 860, 700 * grow, t, t0 + 0.05, rays=False, spin_speed=20)
    for line, col, wi, y in (('Room to grow.', WHITE, 52, 1330), ('Roots to keep.', PEACH, 55, 1450)):
        k = prog(t, WT(wi) - 0.1, WT(wi) + 0.3)
        if k > 0:
            draw(c, ts(line, N8, 96, col), 540, y + (1 - e_out_cubic(k)) * 30, opacity=k)
    colour_bar(c)
    return c


def sh_end(t):
    t0 = SH['end'][0]
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    lg = LOGO()
    kl = prog(t, t0 + 0.1, t0 + 0.7)
    draw(c, lg, 540, 520, scale=820 / lg.shape[1] * (0.94 + 0.06 * e_out_cubic(kl)), opacity=kl)
    for j, (line, col) in enumerate((('Room to grow.', PLUM), ('Roots to keep.', MAG))):
        k = prog(t, t0 + 0.4 + j * 0.15, t0 + 0.8 + j * 0.15)
        if k > 0:
            draw(c, ts(line, N8, 84, col), 540, 860 + j * 100 + (1 - e_out_cubic(k)) * 24, opacity=k)
    kb = prog(t, WT(58) - 0.05, WT(58) + 0.35)
    if kb > 0:
        pulse = 1 + 0.025 * math.sin((t - WT(58)) * 4) * prog(t, WT(58) + 0.6, WT(58) + 1.0)
        e = e_out_back(kb, 2.0) * pulse
        btn = rrect(640, 124, 62, MAG)
        draw(c, blur_sprite(tint(btn, PLUM[:3]), 20), 540, 1180, scale=e, opacity=0.4)
        draw(c, btn, 540, 1160, scale=e)
        draw(c, ts('Start your enquiry', N8, 50, WHITE), 540, 1160, scale=e)
        sw = prog(t, WT(58) + 0.7, WT(58) + 1.4)
        if 0 < sw < 1:
            band = np.exp(-((_X - lerp(240, 840, sw) - (_Y - 1160) * 0.4) / 36) ** 2) * (np.abs(_Y - 1160) < 60)
            c = np.clip(c + band[..., None] * 0.3, 0, 1)
    kp = prog(t, WT(61), WT(61) + 0.4)
    if kp > 0:
        draw(c, ts('0161 241 1332', N8, 60, PLUM), 540, 1330 + (1 - kp) * 20, opacity=kp)
        draw(c, ts('organicfostering.co.uk', N7, 40, R.hexc('#655563')), 540, 1405 + (1 - kp) * 20, opacity=kp)
    colour_bar(c, H - 40, 40)
    return c


FN = dict(pan=sh_pan, hands=sh_hands, writing=sh_writing, spices=sh_spices, explain=sh_explain, stir=sh_stir, cutter=sh_cutter,
          aurora=sh_aurora, table=sh_table, roots=sh_roots, end=sh_end)


# ------------------------------------------------------------------ the six transitions
def tr_retro(a, b, p):
    """Film-roll slip: frames slide up through the gate with a frame line, then an orange burn flash."""
    e = e_inout_cubic(p)
    off = int(e * (H + 60))
    out = np.zeros_like(a)
    out[:max(0, H - off)] = a[off:] if off < H else out[:0]
    yb = H - off + 60
    if yb < H:
        out[max(0, yb):] = b[:H - max(0, yb)]
    k = math.sin(math.pi * p)
    burn = np.exp(-(((_X - 900) / 420) ** 2 + ((_Y - 300) / 520) ** 2))[..., None] * k
    return np.clip(out + burn * np.array([0.9, 0.4, 0.05], np.float32) + k ** 3 * 0.25, 0, 1)


def tr_eclipse(a, b, p):
    return eclipse(a, b, p)


def tr_eclipse_plum(a, b, p):
    return eclipse(a, b, p, 540, 860)


def tr_layercut(a, b, p):
    """Paper layers of the next shot slide in from alternate sides over the old one."""
    e = e_out_cubic(p)
    n = 6
    rng = np.random.default_rng(2)
    out = a.copy()
    cols = (MAG, ORANGE, GREEN, PLUM, PEACH, MAG)
    for i in range(n):
        ph = rng.uniform(0, 6)
        y0 = H * i / n
        top = y0 + 24 * np.sin(_X[0] / 140 + ph)
        bot = y0 + H / n + 24 * np.sin(_X[0] / 140 + ph + 1.7) if i < n - 1 else np.full(W, H, np.float32)
        m = ((_Y >= top[None, :]) & (_Y < bot[None, :] + 2)).astype(np.float32)
        delay = i * 0.08
        k = e_out_cubic(clamp((p - delay) / (1 - 0.5), 0, 1))
        dx = (1 if i % 2 else -1) * W * (1 - k)
        M = np.float32([[1, 0, dx], [0, 1, 0]])
        mm = cv2.warpAffine(m, M, (W, H))
        sh = cv2.GaussianBlur(mm, (0, 0), 14)
        out = out * (1 - 0.4 * np.roll(sh, 14, 0)[..., None])
        edge = cv2.warpAffine(m, np.float32([[1, 0, dx - (1 if i % 2 else -1) * 18], [0, 1, 0]]), (W, H))
        out = out * (1 - edge[..., None]) + np.array(cols[i][:3], np.float32) * edge[..., None]
        out = out * (1 - mm[..., None]) + b * mm[..., None]
    return np.clip(out, 0, 1)


def tr_explainer(a, b, p, cx=470, cy=930):
    """A hand-drawn marker ring grows from the pan; inside it is the next shot."""
    e = e_inout_cubic(p)
    r = 20 + e * 1500
    d = np.hypot(_X - cx, _Y - cy)
    m = np.clip((r - d) / 4, 0, 1)[..., None]
    wob = 6 * np.sin(np.arctan2(_Y - cy, _X - cx) * 7 + p * 6)
    ring = (np.abs(d - r - wob) < 7).astype(np.float32)[..., None]
    out = b * m + a * (1 - m)
    return out * (1 - ring) + ring * np.array([1, 1, 1], np.float32)


def tr_spiral(a, b, p):
    return spiral(a, b, p)


def tr_aurora(a, b, p):
    """A curtain of brand-colour aurora light sweeps up the frame, leaving the next shot behind it."""
    e = e_inout_cubic(p)
    edge = lerp(H + 300, -400, e) + 90 * np.sin(_X / 160 + p * 5) + 40 * np.sin(_X / 61 + p * 9)
    d = _Y - edge
    m = np.clip(d / 20, 0, 1)[..., None]
    out = a * (1 - m) + b * m
    rays = 0.7 + 0.3 * np.sin(_X / 8 + p * 20)
    glow = np.zeros_like(a)
    for col, off, w in ((MAG, 0, 160), (ORANGE, 90, 120), (GREEN, 170, 120)):
        band = np.exp(-((d - off) / w) ** 2) * rays
        glow = glow + band[..., None] * np.array(col[:3], np.float32)
    return np.clip(out + glow * 0.8 * math.sin(math.pi * p) ** 0.5, 0, 1)


TRANS = {'hands': (tr_retro, 0.5), 'writing': (tr_eclipse, 1.2), 'spices': (tr_layercut, 0.7), 'explain': (tr_explainer, 0.7),
         'stir': (tr_spiral, 0.8), 'cutter': (tr_spiral, 0.8), 'aurora': (tr_aurora, 0.9), 'table': (tr_layercut, 0.7),
         'roots': (tr_eclipse_plum, 1.0), 'end': (tr_aurora, 0.9)}


def hits():
    return [(WT(4), 0.4), (WT(13), 0.6), (WT(16), 0.6), (WT(18), 0.4), (WT(23), 0.5), (WT(31), 0.4), (WT(33), 0.4), (WT(35), 0.4),
            (WT(39), 0.4), (WT(47), 0.5), (WT(48), 0.5), (WT(50), 0.5), (WT(52), 0.4), (WT(58), 0.5)]


HITS = hits()


def energy(t):
    z = 1.0
    for th, pn in HITS:
        d = t - th
        if 0 <= d < 0.3:
            z += 0.022 * pn * (1 - d / 0.3) ** 2
    return z


def render_raw(t):
    c = None
    for j in range(1, len(ORDER)):
        nm = ORDER[j]
        a = SH[nm][0]
        kind, td = TRANS[nm]
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
    z = energy(t)
    if z > 1.001:
        c = cv2.warpAffine(c, np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    c = np.ascontiguousarray(c, dtype=np.float32)
    captions(c, t)
    fo = prog(t, DUR - 1.3, DUR)
    if fo > 0:
        c = c * (1 - 0.5 * e_inout_cubic(fo)) + np.array(IVORY[:3], np.float32) * 0.5 * e_inout_cubic(fo)
    return c


def render(fi):
    t = fi / FPS
    return post(render_raw(t), fi, bloom=0.1, grain=0.012, vig=0.14)


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
