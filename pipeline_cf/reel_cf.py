"""Organic Fostering — "Can I Foster If…?" v2 (9:16). Phone-UI story after the client's reference reel; PDF script word
for word. Real people live each answer in feed posts; every answer is quoted from organicfostering.co.uk/faqs.

Usage: python3 reel_cf.py still 1.0,5.0 | python3 reel_cf.py range 0 100 | python3 reel_cf.py times
"""
import os, sys, math, json, functools, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_cf as F
import frames_cf2 as F2
from frames_cf import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask, PURPLE, ORANGE,
                       PLUM, IVORY, LAV, PEACH, LEAF, LAV_D, WHITE, N9, N8, N7, ANS)
from frames_cf2 import I4, I6, I8, I9, HAND, INK
from engine import prog, clamp, lerp, e_out_back, e_out_cubic, e_in_cubic, e_inout_cubic, draw3d, post

FPS = 30
S = F.S
INFO = json.load(open(f'{S}/tts/lines/info.json'))
ORDER = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'l10']
GAP = {'l2': 0.15, 'l3': 0.35, 'l8': 0.35, 'l9': 0.3, 'l10': 0.35}
VO = {}
_t = 0.5
for _k in ORDER:
    if _k != 'l1':
        _t += GAP.get(_k, 0.25)
    VO[_k] = round(_t, 3)
    _t += INFO['dur'][_k]
DUR = round(_t + 1.8, 2)
NF = int(DUR * FPS)
FADE = 1.0
_Y, _X = R._Y, R._X
GREY = np.array((0.93, 0.93, 0.94), np.float32)


def P(line, i):
    return VO[line] + INFO['phrases'][line][i][0]


def PD(line, i):
    return INFO['phrases'][line][i][1]


def END(line):
    return VO[line] + INFO['dur'][line]


def WT(line, i, frac):
    """Time of a word inside a phrase (fraction of the phrase)."""
    return P(line, i) + PD(line, i) * frac


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


def clip_img(cid, tl, w, h, start=0.3, fx=0.5, fy=0.5, z0=1.0, z1=1.1, dur=4.0):
    if cid not in _clips:
        _clips[cid] = Clip(cid)
    c = _clips[cid]
    im = c.frame(start * c.n / c.fps + max(0, tl)).astype(np.float32)[..., ::-1] / 255
    z = lerp(z0, z1, e_inout_cubic(clamp(tl / dur)))
    return F.grade(F.cover(im, fx, fy, z, w, h))


@functools.lru_cache(maxsize=24)
def web(name, w, h, fx=0.5, fy=0.5):
    return F2.web(name, w, h, fx, fy)


@functools.lru_cache(maxsize=16)
def P3(name):
    return F.prop(name)


@functools.lru_cache(maxsize=4)
def LO2(name):
    return F.lo2(name)


@functools.lru_cache(maxsize=1)
def DARK():
    return F2.dark_grad()


@functools.lru_cache(maxsize=1)
def DOTS():
    return F2.dot_matrix()


def grey():
    return np.ones((H, W, 3), np.float32) * GREY


def camera(c, z=1.0, rot=0.0, dx=0.0, dy=0.0, cx=W / 2, cy=H / 2):
    if abs(z - 1) < 1e-3 and abs(rot) < 1e-3 and abs(dx) + abs(dy) < 0.5:
        return c
    M = cv2.getRotationMatrix2D((cx, cy), rot, z)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# ------------------------------------------------------------------ animated pieces
def rays(c, x, y, r0, kr, col=ORANGE, n=12):
    if not 0 < kr < 1:
        return
    lay = np.zeros((H, W), np.uint8)
    r = r0 + 30 * kr
    for j in range(n):
        a = j / n * 2 * math.pi + 0.15
        ln = (28 if j % 2 else 44) * (1 - kr)
        cv2.line(lay, (int((x + math.cos(a) * r) * 4), int((y + math.sin(a) * r) * 4)),
                 (int((x + math.cos(a) * (r + ln)) * 4), int((y + math.sin(a) * (r + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * (1 - kr)
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def pop_in(c, spr, x, y, sc, t, t0, ray=True, float_amp=8, tilt=False, rot0=-16):
    k = prog(t, t0, t0 + 0.38)
    if k <= 0:
        return
    e = e_out_back(k, 2.4)
    yy = y + float_amp * math.sin((t - t0) * 2.2) + (1 - e_out_cubic(k)) * 50
    rot = (1 - k) * rot0 + 3 * math.sin((t - t0) * 1.7)
    if ray:
        rays(c, x, yy, max(spr.shape[:2]) * sc * 0.45, prog(t, t0, t0 + 0.45))
    draw(c, blur_sprite(tint(spr, PLUM[:3]), 18), x + 8, yy + 22, scale=sc * e, rot=rot, opacity=0.35 * min(1, k * 2))
    if tilt:
        draw3d(c, spr, x, yy, 0, spr.shape[1] * sc * e, None, ry=18 * math.sin((t - t0) * 1.5), rx=5 * math.sin((t - t0) * 1.1))
    else:
        draw(c, spr, x, yy, scale=sc * e, rot=rot, opacity=min(1, k * 2.5))


@functools.lru_cache(maxsize=64)
def pill_spr(text, size=44):
    fill, ink, outline = ANS[text]
    s = ts(text, N9, size, ink)
    p = rrect(s.shape[1] + 52, s.shape[0] + 28, (s.shape[0] + 28) / 2, fill).copy()
    if outline:
        st = R.sdf_stroke(R.rrect_alpha(p.shape[1], p.shape[0], p.shape[0] / 2, 0), 3.0)
        p = R.over_spr(p, solid(cv2.resize(st, (p.shape[1], p.shape[0])), outline))
    paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
    return p


@functools.lru_cache(maxsize=64)
def chip_spr(text, fill, ink, size=36):
    s = ts(text, N8, size, ink)
    p = rrect(s.shape[1] + 52, s.shape[0] + 28, (s.shape[0] + 28) / 2, fill).copy()
    paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
    return p


def chip_in(c, spr, x, y, t, t0, rot=0):
    k = prog(t, t0, t0 + 0.3)
    if k <= 0:
        return
    e = e_out_back(k, 2.6)
    yy = y + 4 * math.sin((t - t0) * 2.2)
    draw(c, blur_sprite(tint(spr, PLUM[:3]), 12), x + 5, yy + 12, scale=e, rot=rot, opacity=0.35 * k)
    draw(c, spr, x, yy, scale=e, rot=rot * (0.4 + 0.6 * k), opacity=min(1, k * 3))


@functools.lru_cache(maxsize=512)
def cap_word(w, size, dark):
    return ts(w, I8, size, INK if dark else WHITE)


def caption(c, t, phrases, dark=False, size=52, y=1720, maxw=900):
    """Word-synced caption (= the voiceover). phrases: [(line, idx)]. Words rise in as spoken."""
    words = []
    for line, i in phrases:
        ws = INFO['phrases'][line][i][2].replace('...', '…').split(' ')
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
        wd = cap_word(w, size, dark).shape[1]
        if cur and x + wd > maxw:
            rows.append((cur, x - size * 0.28))
            cur, x = [], 0
        cur.append((w, ton, x))
        x += wd + size * 0.28
    rows.append((cur, x - size * 0.28))
    n = len(rows)
    y0 = y - (n - 1) * size * 1.25
    for li, (row, rw) in enumerate(rows):
        yy = y0 + li * size * 1.25
        x0 = W / 2 - rw / 2
        for w, ton, x in row:
            k = prog(t, ton, ton + 0.2)
            if k <= 0:
                continue
            s = cap_word(w, size, dark)
            e = e_out_cubic(k)
            if not dark:
                draw(c, blur_sprite(tint(s, (0, 0, 0)), 10), x0 + x + s.shape[1] / 2 + 2, yy + 5 + (1 - e) * 20, opacity=0.6 * k)
            draw(c, s, x0 + x + s.shape[1] / 2, yy + (1 - e) * 20, opacity=min(1, k * 2))


def kinetic_t(c, t, items, y, size=80, font=I8, col=WHITE, gap=None):
    """Centered sentence where each item appears at its own time: items = [(word or ('IMG', spr), t_on)]."""
    gap = gap or size * 0.32
    sprs = [(w[1] if isinstance(w, tuple) else ts(w, font, size, col), ton) for w, ton in items]
    total = sum(s.shape[1] for s, _ in sprs) + gap * (len(sprs) - 1)
    x = W / 2 - total / 2
    for s, ton in sprs:
        k = prog(t, ton, ton + 0.28)
        if k > 0:
            e = e_out_back(k, 2.0)
            blur = (1 - k) * 8
            sp = blur_sprite(s, blur) if blur > 0.5 else s
            draw(c, sp, x + s.shape[1] / 2, y + (1 - e_out_cubic(k)) * 30, scale=0.85 + 0.15 * e, opacity=min(1, k * 2))
        x += s.shape[1] + gap


def words_at(line, i, start=0.0, span=0.8):
    ws = INFO['phrases'][line][i][2].replace('...', '…').split(' ')
    t0, d = P(line, i), PD(line, i)
    total = sum(len(w) + 1 for w in ws)
    out, acc = [], 0
    for w in ws:
        out.append((w, t0 + d * span * acc / total))
        acc += len(w) + 1
    return out


# ------------------------------------------------------------------ cached UI sprites
@functools.lru_cache(maxsize=1)
def POST1():
    img = web('hero-family.webp', 860, 860, 0.5, 0.45)
    return (F2.post_card(img, ['Could you foster? Your circumstances', 'deserve a conversation.'], saved=False),
            F2.post_card(img, ['Could you foster? Your circumstances', 'deserve a conversation.'], saved=True))


@functools.lru_cache(maxsize=1)
def CURSOR():
    return LO2('cursor')


@functools.lru_cache(maxsize=1)
def THUMB():
    return F2.thumb(web('hero-family.webp', 170, 120))


@functools.lru_cache(maxsize=1)
def GRAD_IF():
    return F2.grad_text('if…', I9, 470)


@functools.lru_cache(maxsize=1)
def WALL():
    tiles = [('balanced-home-outdoors-2026-09-23.webp', 'I have pets?'), ('06-respite-outdoor-play.webp', 'I’m retired?'),
             ('balanced-home-learning-2026-09-23.webp', 'I work?'), ('balanced-home-reading-2026-09-23.webp', 'I have children?'),
             ('adviser-conversation.webp', 'A health condition?'), ('03-short-term-everyday-connection.webp', 'I rent?'),
             ('07-siblings-growing-together.webp', 'I’m single?'), ('home-belonging.webp', 'No experience?'),
             ('04-long-term-family-belonging.webp', 'Too old?')]
    ww = 2200
    c = np.ones((1500, ww, 3), np.float32) * GREY
    for j, (name, lab) in enumerate(tiles):
        x = 200 + j * 240
        y = 400 + (j % 2) * 620
        im = web(name, 300, 400)
        t = F2.thumb(im, r=22)
        draw(c, t, x, y)
        sp = chip_spr(lab, PURPLE if j % 2 == 0 else ORANGE, WHITE, 28)
        draw(c, sp, x, y + 170)
    return c


@functools.lru_cache(maxsize=1)
def ARROW():
    a = np.zeros((300, 400), np.uint8)
    cv2.fillPoly(a, [np.array([[20, 110], [240, 110], [240, 30], [380, 150], [240, 270], [240, 190], [20, 190]])], 255, cv2.LINE_AA)
    return solid(a.astype(np.float32) / 255, WHITE)


ROWS = [('I have pets', 'Usually'), ('I’m retired', 'Yes'), ('I already have children', 'Yes'), ('I work', 'Possibly'),
        ('A health condition', 'Not automatically')]
ALINES = ['l3', 'l4', 'l5', 'l6', 'l7']
PROPS = ['paw', 'infinity', 'speech', 'clock', 'heart']


@functools.lru_cache(maxsize=1)
def POP_BASE():
    w = 880
    rh = 108
    h = 150 + rh * 5 + 150
    card = rrect(w, h, 34, WHITE).copy()
    s = ts('Can I foster if…', I8, 42, INK)
    paste_spr(card, s, 50 + s.shape[1] / 2, 76)
    tg = F.grad_spr(90, 50, 25).copy()
    paste_spr(tg, rrect(40, 40, 20, WHITE), 65, 25)
    paste_spr(card, tg, w - 95, 76)
    btn = F.grad_spr(w - 100, 96, 48).copy()
    a = F.arrow(WHITE, 40)
    s = ts('Send your question', N9, 40, WHITE)
    tw = s.shape[1] + 14 + a.shape[1]
    paste_spr(btn, s, (w - 100) / 2 - tw / 2 + s.shape[1] / 2, 48)
    paste_spr(btn, a, (w - 100) / 2 + tw / 2 - a.shape[1] / 2, 50)
    paste_spr(card, btn, w / 2, h - 90)
    return card, rh


@functools.lru_cache(maxsize=8)
def ROW_TEXT(j):
    return ts(ROWS[j][0], I6, 36, INK)


def popover(c, t, cx, cy, sc=1.0, active=0, t_pill=None, opacity=1.0, rot=0.0):
    """Popover: rows 0..active-1 already answered; row 'active' highlighted; its pill pops at t_pill."""
    base, rh = POP_BASE()
    card = base.copy()
    w = card.shape[1]
    hy = 150 + rh * active + rh / 2
    paste_spr(card, rrect(w - 40, rh - 14, 18, LAV), w / 2, hy)
    for j in range(5):
        y = 150 + rh * j + rh / 2
        paste_spr(card, ROW_TEXT(j), 50 + ROW_TEXT(j).shape[1] / 2, y)
        p = pill_spr(ROWS[j][1], 32)
        if j < active:
            paste_spr(card, p, w - 50 - p.shape[1] / 2, y)
    draw(c, blur_sprite(tint(card, (0, 0, 0)), 30), cx + 4, cy + 30, scale=sc, rot=rot, opacity=0.2 * opacity)
    draw(c, card, cx, cy, scale=sc, rot=rot, opacity=opacity)
    if t_pill is not None:
        k = prog(t, t_pill, t_pill + 0.35)
        if k > 0:
            p = pill_spr(ROWS[active][1], 32)
            px = cx + (w / 2 - 50 - p.shape[1] / 2) * sc
            py = cy + (hy - card.shape[0] / 2) * sc
            draw(c, p, px, py, scale=sc * e_out_back(k, 2.6), opacity=min(1, k * 3))
            rays(c, px, py, p.shape[1] * sc * 0.5, prog(t, t_pill, t_pill + 0.45), col=PURPLE)
            return px, py
    return None


FEED = {  # line: (clip, fx, fy, caption lines, pill)
    'l3': (42735, 0.5, 0.45, ['“Pets are assessed for temperament, care, safety', 'and likely response to a child.”']),
    'l4': (4764, 0.45, 0.4, ['“There’s no fixed upper age limit.”']),
    'l5': (15800, 0.5, 0.45, ['“Your children’s views, ages, needs and the possible', 'effect of fostering on family life form part of', 'assessment.”']),
    'l6': (4954, 0.5, 0.45, ['“It depends on your hours, flexibility, support', 'network, household and the child’s needs.”']),
    'l7': (47980, 0.5, 0.42, ['“A disability, medical condition or mental-health', 'history does not automatically prevent fostering.”']),
}
QS = {'l3': 'Can I foster if… I have pets?', 'l4': 'Can I foster if… I’m retired?', 'l5': 'Can I foster if… I already have children?',
      'l6': 'Can I foster if… I work?', 'l7': 'Can I foster if… I have a health condition?'}


@functools.lru_cache(maxsize=8)
def feed_frame(line):
    """Static post chrome (white card) with a transparent photo hole; the clip is drawn under it each frame."""
    cid, fx, fy, cap = FEED[line]
    blank = np.zeros((620, 860, 3), np.float32)
    card = F2.post_card(blank, cap, sub=QS[line])
    return card


def feed_post(c, t, line, t0, cx, cy):
    cid, fx, fy, cap = FEED[line]
    card = feed_frame(line)
    im = clip_img(cid, t - t0, 860, 620, 0.25, fx, fy, 1.0, 1.08, 5.0)
    m = R.sdf_fill(R.rrect_alpha(860, 620, 20, 2))
    m = cv2.resize(m, (860, 620))
    ph = np.concatenate([im * m[..., None], m[..., None]], 2).astype(np.float32)
    top = cy - card.shape[0] / 2
    draw(c, blur_sprite(tint(card, (0, 0, 0)), 30), cx, cy + 26, opacity=0.18)
    draw(c, card, cx, cy)
    draw(c, ph, cx, top + 130 + 310)
    return top + 130, top + 130 + 620          # photo top / bottom


# ------------------------------------------------------------------ shots
def sh_post(t):            # "Thinking about fostering?"  — the saved post, up close
    c = grey()
    c0, c1 = POST1()
    tb = WT('l1', 0, 0.75)
    card = c1 if t > tb else c0
    z = lerp(1.0, 1.22, e_inout_cubic(clamp(t / (P('l1', 1)))))
    draw(c, blur_sprite(tint(card, (0, 0, 0)), 30), W / 2, 960 + 30, opacity=0.18)
    draw(c, card, W / 2, 960)
    bx, by = W / 2 + 390, 960 - card.shape[0] / 2 + 130 + 860 + 55
    rays(c, bx, by, 30, prog(t, tb, tb + 0.45), col=PURPLE)
    kc = prog(t, tb + 0.1, tb + 0.6)
    if kc > 0:
        _scribble_circle(c, bx, by, 52, 46, kc)
    ks = prog(t, tb + 0.35, tb + 0.85)
    if ks > 0:
        _scribble_arrow(c, [(bx - 360, by + 210), (bx - 200, by + 170), (bx - 70, by + 60)], ks)
    kw = prog(t, tb + 0.6, tb + 1.3)
    if kw > 0:
        s = solid(_wmask('saved it…', HAND, 88), PURPLE)
        cut = int(s.shape[1] * kw)
        s2 = s.copy()
        s2[:, cut:] = 0
        draw(c, s2, bx - 470, by + 240, rot=-6)
    c = camera(c, z, 0, 0, 0, cx=bx - 150, cy=by - 120)
    cr = CURSOR()
    kx = prog(t, 0.0, tb)
    draw(c, cr, lerp(700, W / 2 + 120, e_inout_cubic(kx)), lerp(1500, 1210, e_inout_cubic(kx)), scale=0.16)
    caption(c, t, [('l1', 0)], dark=True, y=1780)
    return c


def _scribble_circle(c, x, y, rx, ry, k, col=PURPLE, w=6):
    rng = np.random.default_rng(2)
    tt = np.linspace(0, 2 * math.pi * 1.15 * k, max(3, int(140 * k)))
    pts = np.stack([x + rx * np.cos(tt) * (1 + 0.05 * np.sin(3 * tt)) + rng.normal(0, 1.2, len(tt)),
                    y + ry * np.sin(tt) * (1 + 0.06 * np.cos(2 * tt)) + rng.normal(0, 1.2, len(tt))], 1)
    lay = np.zeros((H, W), np.uint8)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, w * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def _scribble_arrow(c, pts, k, col=PURPLE, w=6):
    p = np.array(pts, np.float32)
    seg = np.cumsum(np.r_[0, np.hypot(*np.diff(p, axis=0).T)])
    L = seg[-1] * k
    keep = [q for q, s in zip(p, seg) if s <= L]
    i = len(keep)
    if i < len(p):
        u = (L - seg[i - 1]) / (seg[i] - seg[i - 1])
        keep.append(p[i - 1] + (p[i] - p[i - 1]) * u)
    if len(keep) < 2:
        return
    F2.scribble_line(c, keep, col=col, w=w, head=k > 0.95, wobble=3)


def sh_wonder(t):          # "You've probably wondered:"
    c = DARK().copy()
    items = words_at('l1', 1, span=0.85)
    kinetic_t(c, t, [(items[0][0], items[0][1]), (('IMG', THUMB()), items[0][1] + 0.12)], 860, 84)
    kinetic_t(c, t, items[1:], 990, 84)
    cr = CURSOR()
    k = prog(t, P('l1', 1), P('l2', 0))
    draw(c, cr, lerp(300, 180, k), lerp(1300, 1500, k), scale=0.15, rot=-15, opacity=0.9)
    return c


def sh_if(t):              # "can I foster if…"
    t0 = P('l1', 2)
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    k = prog(t, t0 - 0.05, t0 + 0.3)
    if k > 0:
        g = GRAD_IF()
        e = e_out_back(k, 1.6)
        sp = blur_sprite(g, (1 - k) * 14) if k < 1 else g
        draw(c, sp, W / 2 + 20, 820, scale=1.3 - 0.3 * e, opacity=min(1, k * 2))
    pop_in(c, P3('qmark'), 860, 520, 0.7, t, t0 + 0.2, ray=True)
    full = 'Can I foster if…'
    n = int(len(full) * clamp((t - t0 + 0.05) / max(0.2, PD('l1', 2) * 0.9)))
    F.search_bar(c, full[:n] if n else '', y=1320, w=860, phase=(t * 0.3) % 1, label=None)
    return c


def sh_wall(t):            # "Here are the honest answers."
    t0 = P('l2', 0)
    wall = WALL()
    k = clamp((t - t0 + 0.4) / (PD('l2', 0) + 0.4))
    off = lerp(0, wall.shape[1] - W, e_inout_cubic(k))
    x0 = int(off)
    c = np.ones((H, W, 3), np.float32) * GREY
    c[200:1700] = wall[:, x0:x0 + W]
    speed = abs(math.sin(math.pi * k))
    if speed > 0.05:
        c = F2.motion_blur(c, int(9 + 90 * speed) | 1)
    ka = prog(t, WT('l2', 0, 0.35), WT('l2', 0, 0.55))
    if ka > 0:
        draw(c, blur_sprite(tint(ARROW(), (0, 0, 0)), 20), lerp(-300, W / 2, e_out_cubic(ka)) + 10, 880 + 16, opacity=0.4)
        draw(c, ARROW(), lerp(-300, W / 2, e_out_cubic(ka)), 880)
    kh = prog(t, WT('l2', 0, 0.55), WT('l2', 0, 0.75))
    if kh > 0:
        s = ts('HONEST ANSWERS.', I9, 96, INK, 0.0)
        draw(c, blur_sprite(s, (1 - kh) * 10), W / 2, 1300, scale=1.4 - 0.4 * e_out_cubic(kh), opacity=min(1, kh * 2))
    caption(c, t, [('l2', 0)], dark=True, y=1820, size=46)
    return c


def sh_ask(t, idx):        # popover: "<question>? <answer>."
    line = ALINES[idx]
    t0 = P(line, 0)
    c = grey()
    t_pill = P(line, 1) if line != 'l7' else WT('l7', 1, 0.35)
    k_in = prog(t, t0 - 0.3, t0 + 0.15) if idx == 0 else 1.0
    sc = lerp(0.3, 1.0, e_out_back(k_in, 1.4)) if idx == 0 else 1.0
    cy = 1040
    rot = 1.5 * math.sin((t - t0) * 1.2)
    draw(c, F2.icon('bookmark_fill', 110, INK), 170, 280)
    pp = popover(c, t, W / 2, cy, sc, idx, t_pill, opacity=min(1, k_in * 2), rot=rot)
    pop_in(c, P3(PROPS[idx]) if PROPS[idx] in ('paw', 'infinity', 'speech') else LO2(PROPS[idx]), 860, 330, 0.48, t, t_pill)
    cr = CURSOR()
    rh = POP_BASE()[1]
    ry = cy + (150 + rh * idx + rh / 2 - POP_BASE()[0].shape[0] / 2)
    kc = prog(t, t0, t0 + 0.4)
    draw(c, cr, lerp(760, 820, kc), lerp(ry + 160, ry + 30, e_out_cubic(kc)), scale=0.15)
    if line == 'l7':
        caption(c, t, [(line, 0), (line, 1)], dark=True)
    else:
        caption(c, t, [(line, 0), (line, 1)], dark=True)
    draw(c, ts('From our FAQs · organicfostering.co.uk/faqs', 'Poppins-Medium', 24, (0.3, 0.3, 0.35, 1)), W / 2, 1860)
    return c


def sh_feed(t, idx):       # feed post: a real person lives the answer
    line = ALINES[idx]
    ts0 = P(line, 2) if line != 'l7' else P('l7', 1) + PD('l7', 1) * 0.6
    c = grey()
    cy = 830 - 40 * e_inout_cubic(clamp((t - ts0) / 4))
    ptop, pbot = feed_post(c, t, line, ts0 - 0.4, W / 2, cy)
    chip_in(c, pill_spr(ROWS[idx][1], 40), 760, ptop + 70, t, ts0 - 0.2, rot=3)
    if line == 'l3':
        chip_in(c, chip_spr('Temperament', PURPLE, WHITE), 300, pbot - 80, t, WT('l3', 2, 0.68), rot=-3)
        chip_in(c, chip_spr('Safety', ORANGE, WHITE), 640, pbot - 60, t, P('l3', 3) + 0.15, rot=3)
    elif line == 'l4':
        k = prog(t, P('l4', 2) + 0.1, P('l4', 2) + PD('l4', 2) + 0.3)
        if k > 0:
            lay = np.zeros((H, W), np.uint8)
            yy = int(pbot - 70)
            cv2.line(lay, (90 * 4, yy * 4), (int(lerp(90, W + 60, e_inout_cubic(k))) * 4, yy * 4), 255, 9 * 4, cv2.LINE_AA, shift=2)
            m = lay.astype(np.float32)[..., None] / 255
            col = np.array(LEAF[:3], np.float32) * (1 - (_X / W)[..., None]) + np.array(ORANGE[:3], np.float32) * (_X / W)[..., None]
            c[:] = c * (1 - m) + col * m
            for j, a in enumerate((30, 50, 70, 90)):
                x = 150 + j * 230
                if lerp(90, W + 60, e_inout_cubic(k)) > x:
                    draw(c, rrect(5, 28, 2, WHITE), x, yy)
                    draw(c, ts(str(a), N8, 32, WHITE), x, yy - 40)
    elif line == 'l5':
        chip_in(c, chip_spr('Their views', LAV_D, PLUM), 280, ptop + 80, t, P('l5', 2) + 0.1, rot=-3)
    elif line == 'l6':
        for j, (lab, col, ink, tt_) in enumerate((('Hours', PURPLE, WHITE, WT('l6', 2, 0.72)), ('Flexibility', ORANGE, WHITE, P('l6', 3)),
                                                   ('Support', PEACH, PLUM, WT('l6', 4, 0.3)))):
            chip_in(c, chip_spr(lab, col, ink), 220 + j * 310, pbot - 70, t, tt_, rot=(-3, 2, -2)[j])
    caption(c, t, [(line, i) for i in range(2 if line == 'l7' else 2, len(INFO['phrases'][line]))] if line != 'l7'
            else [('l7', 1)], dark=True)
    return c


def sh_dots(t):            # "Your question's not on the list?"
    c = DOTS().copy()
    c = c * (0.85 + 0.15 * math.sin(t * 3))
    items = words_at('l8', 0, span=0.85)
    kinetic_t(c, t, items[:3], 860, 84)
    kinetic_t(c, t, items[3:], 990, 84)
    pop_in(c, F2.avatar(120), W / 2, 1250, 1.0, t, WT('l8', 0, 0.8), ray=True)
    return c


@functools.lru_cache(maxsize=1)
def FILM():
    im = F2.film(web('06-respite-outdoor-play.webp', 900, 1100, 0.55, 0.45))
    bg = cv2.GaussianBlur(F.cover(im, 0.5, 0.5, 1.0), (0, 0), 50)
    d = np.hypot((_X - W / 2) / (W * 0.6), (_Y - H / 2) / (H * 0.45))
    bg = (bg * np.clip(1 - d, 0, 1)[..., None] ** 1.5 * 0.85).astype(np.float32)
    return bg, F2.thumb(im, r=40, border=(1, 1, 1, 0))


def sh_film(t):            # "Your circumstances deserve a conversation."
    t0 = P('l8', 1)
    bg, card = FILM()
    c = bg.copy()
    z = lerp(0.96, 1.04, clamp((t - t0) / 4))
    draw(c, card, W / 2, H / 2 - 80, scale=z)
    items = words_at('l8', 1, span=0.85)
    kinetic_t(c, t, items[:2], 300, 64, font=I8)
    kw = prog(t, items[2][1], items[-1][1] + 0.5)
    if kw > 0:
        s = solid(_wmask('deserve a conversation', HAND, 96), (1.0, 0.84, 0.35, 1.0))
        s2 = s.copy()
        s2[:, int(s.shape[1] * kw):] = 0
        draw(c, s2, W / 2, 1640, rot=-5)
    return c


def sh_send(t):            # "Send your question"
    t0 = P('l9', 0)
    c = grey()
    km = prog(t, t0 - 0.2, t0 + 0.4)
    w = lerp(860, 760, e_inout_cubic(km))
    if km < 1:
        F.search_bar(c, 'Can I foster if', y=960, w=int(w), caret=True, phase=(t * 0.3) % 1)
    if km > 0:
        btn = F.grad_spr(760, 130, 65, phase=(t * 0.3) % 1)
        e = e_out_back(km, 1.6)
        draw(c, blur_sprite(btn, 24), W / 2, 980, scale=e, opacity=0.55 * km)
        draw(c, btn, W / 2, 960, scale=e, opacity=km)
        if km > 0.6:
            F.text_arrow(c, 'Send your question', W / 2, 960)
    tc = t0 + PD('l9', 0) * 0.8
    kc = prog(t, t0, tc)
    cr = CURSOR()
    press = 0.85 if 0 < t - tc < 0.15 else 1.0
    draw(c, cr, lerp(900, 700, e_inout_cubic(kc)), lerp(1500, 990, e_inout_cubic(kc)), scale=0.16 * press)
    kr = prog(t, tc, tc + 0.5)
    if 0 < kr < 1:
        lay = np.zeros((H, W), np.float32)
        cv2.circle(lay, (680, 975), int(20 + 160 * kr), 1.0, 6, cv2.LINE_AA)
        c = c * (1 - lay[..., None] * (1 - kr)) + np.array(PURPLE[:3], np.float32) * lay[..., None] * (1 - kr)
    kp = prog(t, tc + 0.1, tc + 1.0)
    if kp > 0:
        x = lerp(560, 1250, e_in_cubic(kp))
        y = lerp(960, 300, e_in_cubic(kp))
        draw(c, P3('plane'), x, y, scale=0.6 + 0.4 * kp, rot=10)
    caption(c, t, [('l9', 0)], dark=True)
    return c


@functools.lru_cache(maxsize=4)
def BANNER(j):
    if j == 0:
        return F2.banner('Organic Fostering', 'A real person replies · Manchester team', time='now')
    return F2.banner('Organic Fostering', 'No pressure, no obligation.', time='now')


def sh_notify(t):          # "to a real person in our Manchester team. No pressure, no obligation."
    t1, t2 = P('l9', 1), P('l9', 3)
    c = grey()
    c = c * 0.92 + F.canvas() * 0.08
    for j, (tj, base_y) in enumerate(((t1, 980), (t2, 980))):
        k = prog(t, tj, tj + 0.45)
        if k <= 0:
            continue
        b = BANNER(j)
        y = lerp(-120, base_y, e_out_back(k, 1.3))
        if j == 0 and t > t2:
            push = e_out_cubic(prog(t, t2, t2 + 0.45))
            y = lerp(base_y, base_y - 190, push)
            draw(c, blur_sprite(tint(b, (0, 0, 0)), 24), W / 2, y + 18, scale=1 - 0.05 * push, opacity=0.15)
            draw(c, b, W / 2, y, scale=1 - 0.05 * push, opacity=1 - 0.15 * push)
            continue
        draw(c, blur_sprite(tint(b, (0, 0, 0)), 24), W / 2, y + 18, opacity=0.2 * k)
        draw(c, b, W / 2, y)
    pop_in(c, P3('speech'), 860, 560, 0.5, t, P('l9', 2))
    chip_in(c, chip_spr('A real person replies', WHITE, PLUM), 330, 1320, t, WT('l9', 1, 0.5), rot=-2)
    chip_in(c, chip_spr('Manchester team', PURPLE, WHITE), 760, 1400, t, WT('l9', 2, 0.55), rot=2)
    caption(c, t, [('l9', 1), ('l9', 2)] if t < t2 - 0.1 else [('l9', 3), ('l9', 4)], dark=True)
    return c


@functools.lru_cache(maxsize=1)
def END_BG():
    return np.zeros((H, W, 3), np.float32) + 0.015


def sh_end(t):             # "Organic Fostering."
    t0 = P('l10', 0)
    c = END_BG().copy()
    F.glow(c, W / 2, 700, 360, PURPLE, 0.25 * prog(t, t0 - 0.3, t0 + 0.5))
    pop_in(c, F2.avatar(170), W / 2, 640, 1.0, t, t0 - 0.25, ray=True, float_amp=4)
    k = prog(t, t0, t0 + 0.4)
    if k > 0:
        draw(c, ts('Organic Fostering', N9, 84, WHITE), W / 2, 820 + (1 - e_out_cubic(k)) * 20, opacity=k)
    kb = prog(t, t0 + 0.4, t0 + 0.75)
    if kb > 0:
        btn = F.grad_spr(680, 116, 58, phase=(t * 0.3) % 1)
        draw(c, blur_sprite(btn, 24), W / 2, 1010, scale=e_out_back(kb, 2), opacity=0.5)
        draw(c, btn, W / 2, 990, scale=e_out_back(kb, 2))
        if kb > 0.7:
            F.text_arrow(c, 'Send your question', W / 2, 990, size=46)
    k2 = prog(t, t0 + 0.7, t0 + 1.0)
    if k2 > 0:
        draw(c, ts('0161 241 1332', N9, 56, WHITE), W / 2, 1150, opacity=k2)
        draw(c, ts('organicfostering.co.uk', I6, 36, (1, 1, 1, 0.8)), W / 2, 1225, opacity=k2)
    k3 = prog(t, t0 + 0.9, t0 + 1.2)
    if k3 > 0:
        s = ts('Rated Good by Ofsted · Inspected May 2025', I4, 28, (1, 1, 1, 0.75))
        draw(c, F.star(ORANGE, 30), W / 2 - s.shape[1] / 2 - 26, 1330, opacity=k3)
        draw(c, s, W / 2 + 8, 1330, opacity=k3)
    caption(c, t, [('l10', 0)], dark=False, y=1760)
    return c


def shots():
    out = [(0.0, P('l1', 1), sh_post), (P('l1', 1), P('l1', 2) - 0.1, sh_wonder), (P('l1', 2) - 0.1, P('l2', 0) - 0.1, sh_if),
           (P('l2', 0) - 0.1, P('l3', 0) - 0.15, sh_wall)]
    for i, line in enumerate(ALINES):
        sw = P(line, 2) - 0.15 if line != 'l7' else P('l7', 1) + PD('l7', 1) * 0.55
        nxt = P(ALINES[i + 1], 0) - 0.15 if i < 4 else P('l8', 0) - 0.15
        out.append((P(line, 0) - 0.15 if i else P(line, 0) - 0.15, sw, (lambda t, i=i: sh_ask(t, i))))
        out.append((sw, nxt, (lambda t, i=i: sh_feed(t, i))))
    out += [(P('l8', 0) - 0.15, P('l8', 1) - 0.1, sh_dots), (P('l8', 1) - 0.1, P('l9', 0) - 0.15, sh_film),
            (P('l9', 0) - 0.15, P('l9', 1) - 0.05, sh_send), (P('l9', 1) - 0.05, P('l10', 0) - 0.3, sh_notify),
            (P('l10', 0) - 0.3, 999, sh_end)]
    return out


SHOTS = None


# ------------------------------------------------------------------ transitions (camera moves with motion blur)
def tr_whip(a, b, p, axis=1):
    return R.whip(a, b, p, axis)


def tr_zoom(a, b, p):
    e = e_in_cubic(min(1, p * 1.6))
    za = 1 + 0.7 * e
    A = cv2.warpAffine(a, np.float32([[za, 0, (1 - za) * W / 2], [0, za, (1 - za) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    zb = 1.3 - 0.3 * e_out_cubic(clamp(p * 1.4 - 0.3))
    B = cv2.warpAffine(b, np.float32([[zb, 0, (1 - zb) * W / 2], [0, zb, (1 - zb) * H / 2]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    k = clamp((p - 0.35) / 0.3)
    out = A * (1 - k) + B * k
    blur = int(1 + 34 * math.sin(math.pi * p))
    if blur > 2:
        out = cv2.addWeighted(out, 0.5, cv2.blur(out, (blur, blur)), 0.5, 0)
    return out


def tr_blurfade(a, b, p):
    """Defocus out, refocus in (the reference's soft blur dissolve)."""
    s = math.sin(math.pi * p) * 26
    e = e_inout_cubic(p)
    out = a * (1 - e) + b * e
    return cv2.GaussianBlur(out, (0, 0), s) if s > 0.6 else out


def tr_scroll(a, b, p):
    """Feed-style vertical scroll with motion blur."""
    e = e_inout_cubic(p)
    off = int(H * e)
    out = np.empty_like(a)
    out[:H - off] = a[off:]
    out[H - off:] = b[:off]
    sp = math.sin(math.pi * p)
    if sp > 0.05:
        out = F2.motion_blur(out, int(9 + 70 * sp) | 1, axis=0)
    return out


def tr_flash(a, b, p):
    k = 1 - abs(p - 0.5) * 2
    return (a if p < 0.5 else b) * (1 - k) + k * np.array([1.0, 0.97, 0.95], np.float32)


def tr_cut(a, b, p):
    return a if p < 0.5 else b


# per cut index: (kind, duration)
TRANS = [(tr_zoom, 0.4), (tr_blurfade, 0.35), (lambda a, b, p: tr_whip(a, b, p, 1), 0.34), (tr_zoom, 0.4),
         (tr_scroll, 0.36), (tr_scroll, 0.36), (tr_scroll, 0.36), (tr_scroll, 0.36), (tr_scroll, 0.36), (tr_scroll, 0.36),
         (tr_scroll, 0.36), (tr_scroll, 0.36), (tr_scroll, 0.36), (tr_blurfade, 0.5), (tr_blurfade, 0.5),
         (tr_flash, 0.3), (lambda a, b, p: tr_whip(a, b, p, 0), 0.34), (tr_blurfade, 0.5)]


def hits():
    hs = [(WT('l1', 0, 0.75), 0.7, 0), (P('l1', 2), 0.8, 0), (WT('l2', 0, 0.55), 0.9, 8)]
    for line in ALINES:
        hs.append((P(line, 1) if line != 'l7' else WT('l7', 1, 0.35), 0.7, 0))
    hs += [(WT('l9', 0, 0.8), 0.8, 0), (P('l9', 1), 0.5, 0), (P('l9', 3), 0.5, 0), (P('l10', 0) - 0.25, 0.8, 0)]
    return hs


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
        kind, td = TRANS[j] if j < len(TRANS) else (tr_blurfade, 0.4)
        d = t - (a - td / 2)
        if 0 <= d < td:
            prev = SHOTS[j][2](min(t, a - 0.01))
            nxt = f(max(t, a))
            c = kind(prev, nxt, d / td)
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
    if t > DUR - FADE:
        c = c * (1 - 0.7 * e_inout_cubic(prog(t, DUR - FADE, DUR)))
    return c


def render(fi):
    t = fi / FPS
    c = render_raw(t)
    _, _, _, ca = energy(t)
    return post(c, fi, bloom=0.1, grain=0.012, vig=0.12, ca=ca)


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
        for a, b, f in shots():
            print(round(a, 2), round(b, 2), getattr(f, '__name__', 'lambda'))
