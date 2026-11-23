"""Organic Fostering "One question is enough" (22 s brief), 9:16.

0  Deep-plum paper. "HOW MANY / QUESTIONS" builds in two quick beats while a 3D magnifying glass reads it (lens zoom).
1  LAYERCUT: the headline slices away into the full question; 3D question mark on "fostering".
2  ECLIPSE ring sweep opens "Can I foster if I rent?" with the 3D key (soft click).
3  EXPLAINER: the key steps aside into a labelled circle; the calendar takes centre: "How would fostering fit around work?"
4  The phone: "Who can I call if I need support?" Three circles together.
5  SPIRAL: three question cards spiral into one speech bubble (magenta accent).
6  "One question is enough to start." typed (retro) under the bubble with a soft AURORA glow. Hold.
7  Warm-ivory end card: logo reveal, "Thinking about fostering in Greater Manchester?", Start your enquiry, Link in bio.

Usage: python3 reel_oneq.py still 1.0,5.0 | range a b | times
"""
import os, sys, json, math, re, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_oneq as G
from frames_oneq import (W, H, S, PLUM, MAG, IVORY, INK, WHITE, GLOW, paper, ivory_paper, lens, ring_sweep, icon_circle, card, pop, word,
                         typed, paste, rrect, text_sprite, layercut, aurora, grain, logo, colour_bar, clamp, prog, e_out, e_inout,
                         e_back, _grid)
import frames_notes as N

FPS = 30
INFO = json.load(open(f'{S}/tts/info.json'))
WORDS = INFO['words']
LIGHT = (0.95, 0.88, 0.93)
PINKT = (1.0, 0.62, 0.85)


def norm(w):
    return re.sub(r"[^a-z']", '', w.lower().replace('’', "'"))


def A(wd, k=0, end=False):
    n = 0
    for w in WORDS:
        if norm(w[0]) == norm(wd):
            if n == k:
                return w[2] if end else w[1]
            n += 1
    raise KeyError(wd)


T_DO, T_BEFORE, T_ABOUT, T_FOST = A('do'), A('before'), A('about'), A('fostering')
T_CAN, T_IF, T_RENT = A('can'), A('if'), A('rent')
T_HOW2, T_FIT, T_WORK = A('how', 1), A('fit'), A('work')
T_WHO, T_IF3, T_SUPPORT_E = A('who'), A('if', 1), A('support', end=True)
T_ONE, T_IS, T_START_E = A('one'), A('is'), A('start', 0, end=True)
T_THINK, T_IN, T_CTA, T_LINK = A('thinking'), A('in'), A('start', 1), A('link')
T_LAST = WORDS[-1][2]
DUR = round(T_LAST + 2.4, 2)
NF = int(DUR * FPS)

LC0, LC1 = T_DO - 0.2, T_DO + 0.3                            # layercut
RS0 = T_CAN - 0.6                                             # ring sweep (eclipse)
Q2, Q3 = T_HOW2 - 0.3, T_WHO - 0.3
SP0, SP1 = T_SUPPORT_E + 0.05, T_ONE - 0.12                   # spiral into the bubble
END0, END1 = T_THINK - 0.5, T_THINK - 0.05
CX, CY = 540, 820


def header(c, a=1.0):
    word(c, 'ORGANIC FOSTERING', 540, 130, 30, 800, LIGHT, a=a)


@functools.lru_cache(None)
def magnifier_geom(size=430):
    """Centre and inner radius of the magnifier's ring inside its sprite (so the lens zoom sits exactly in the ring)."""
    spr = N.token('magnifier', size, 0)
    a = (spr[..., 3] > 0.08).astype(np.uint8)
    h, w = a.shape
    fill = a.copy()
    m = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(fill, m, (0, 0), 1)
    hole = (fill == 0).astype(np.uint8)
    ys, xs = np.nonzero(hole)
    if len(xs) < 10:
        return 0.0, 0.0, size * 0.25
    cxo, cyo = xs.mean() - w / 2, ys.mean() - h / 2
    r = math.sqrt(len(xs) / math.pi)
    return cxo, cyo, r


# ------------------------------------------------------------------ scenes
def scene_head(t):
    c = paper().copy()
    header(c, clamp(t / 0.3))
    word(c, 'HOW MANY', 540, 600, 150, 900, WHITE, t - 0.1)
    word(c, 'QUESTIONS', 540, 760, 150, 900, WHITE, t - 0.42)
    # the magnifying glass reads the headline
    u = prog(t, 0.25, LC1)
    if 0 < u < 1:
        mx = -120 + 1300 * e_inout(u)
        my = 640 + 120 * math.sin(u * math.pi * 1.3)
        ox, oy, r = magnifier_geom()
        sx, sy = mx, my                                           # ring centre on screen
        c = lens(c, sx, sy, r * 0.98, 1.65)
        pop(c, 'magnifier', sx - ox, sy - oy, 430, 1.0, shadow=False)
    return c


def scene_q(t):
    c = paper().copy()
    header(c)
    word(c, 'HOW MANY QUESTIONS', 540, 470, 80, 900, WHITE, 1.0)
    word(c, 'do you need answered', 540, 600, 62, 700, LIGHT, t - T_DO + 0.05)
    word(c, 'before you enquire', 540, 680, 62, 700, LIGHT, t - T_BEFORE + 0.05)
    word(c, 'about fostering?', 540, 790, 92, 900, PINKT, t - T_ABOUT + 0.05)
    pop(c, 'qmark', 820, 1130, 360, t - T_FOST)
    return c


def big_to_small(u, start, end):
    k = e_inout(u)
    return tuple(a + (b - a) * k for a, b in zip(start, end))


def scene_icons(t):
    c = paper().copy()
    header(c)
    # ECLIPSE: the ring sweeps round to open the first question
    if t < T_CAN + 0.6:
        c = ring_sweep(c, CX, CY, 245, prog(t, RS0, RS0 + 0.9), col=LIGHT)
    # key: centre -> top-left
    uk = prog(t, Q2, Q2 + 0.5)
    kx, ky, kr = big_to_small(uk, (CX, CY, 190), (250, 420, 110))
    icon_circle(c, kx, ky, kr, 'key', t - T_CAN + 0.15, 'Renting' if uk > 0.6 else None, a=1 - 0.4 * uk)
    if t >= Q2:
        uc = prog(t, Q3, Q3 + 0.5)
        cx2, cy2, cr = big_to_small(uc, (CX, CY, 190), (830, 420, 110))
        icon_circle(c, cx2, cy2, cr, 'calendar', t - T_HOW2 + 0.15, 'Work' if uc > 0.6 else None, a=1 - 0.4 * uc)
    if t >= Q3:
        icon_circle(c, CX, CY, 190, 'phone', t - T_WHO + 0.15)
    # the question lines (by voice)
    if t < Q2:
        a = 1 - prog(t, Q2 - 0.2, Q2)
        word(c, 'Can I foster', 540, 1160, 96, 900, WHITE, t - T_CAN, a=a)
        word(c, 'if I rent?', 540, 1270, 96, 900, WHITE, t - T_IF, a=a)
    elif t < Q3:
        a = 1 - prog(t, Q3 - 0.2, Q3)
        word(c, 'How would fostering', 540, 1160, 76, 900, WHITE, t - T_HOW2, a=a)
        word(c, 'fit around work?', 540, 1260, 92, 900, WHITE, t - T_FIT, a=a)
    else:
        a = 1 - prog(t, SP0, SP0 + 0.25)
        word(c, 'Who can I call', 540, 1160, 92, 900, WHITE, t - T_WHO, a=a)
        word(c, 'if I need support?', 540, 1265, 80, 900, WHITE, t - T_IF3, a=a)
    return c


CARDS = (('Can I foster if I rent?', 'key', 210), ('How would it fit around work?', 'calendar', 330), ('Who can I call for support?', 'phone', 90))


def scene_spiral(t):
    c = paper().copy()
    header(c)
    u = prog(t, SP0 + 0.3, SP1)
    # the bubble grows as the cards go in
    pop(c, 'bubble', CX, 860, 300 + 260 * e_out(u), t - SP0 - 0.15, glow=np.array((0.9, 0.2, 0.6), np.float32) * (0.3 + 0.7 * u))
    for i, (txt, nm, ang) in enumerate(CARDS):
        ui = clamp((u - i * 0.08) / 0.84)
        a = math.radians(ang + 260 * e_inout(ui))
        r = 400 * (1 - e_inout(ui))
        x, y = CX + 250 / 400 * r * math.cos(a), 860 + r * math.sin(a)
        sc = 0.85 * (1 - 0.85 * e_inout(ui))
        al = 1 - clamp((ui - 0.75) / 0.25)
        card(c, txt, x, y, 860, nm, t - SP0 - i * 0.08, a=al, scale=max(0.05, sc), rot=(-10, 6, -5)[i] * (1 - ui))
    return c


def scene_one(t):
    c = paper().copy()
    c = aurora(c, t, 0.22 * prog(t, T_ONE - 0.2, T_ONE + 0.8), 0.04, 0.16)
    header(c)
    k = e_out(prog(t, SP1, SP1 + 0.5))
    pop(c, 'bubble', CX, 860 - 100 * k, 560 + 80 * k, 1.0, glow=np.array((0.9, 0.2, 0.6), np.float32))
    n1 = len('One question') * prog(t, T_ONE - 0.05, T_IS - 0.1)
    typed(c, 'One question', 205, 1190, 104, n1, 900, WHITE, caret=n1 < 12, t=t)
    n2 = len('is enough to start.') * prog(t, T_IS - 0.05, T_START_E)
    if t > T_IS - 0.05:
        typed(c, 'is enough to start.', 150, 1310, 86, n2, 900, PINKT, caret=True, t=t, caret_col=MAG)
    return c


def end_card(t):
    c = ivory_paper().copy()
    lg = logo(760)
    u = prog(t, END0 + 0.15, END1 + 0.45)
    if u > 0:
        k = e_out(u)
        wv = max(2, int(lg.shape[1] * k))
        part = lg[:, :wv]
        paste(c, part, 540 - lg.shape[1] / 2 + wv / 2, 620 + 12 * (1 - k))
    word(c, 'Thinking about fostering', 540, 940, 64, 900, PLUM, t - T_THINK + 0.05)
    word(c, 'in Greater Manchester?', 540, 1020, 64, 900, PLUM, t - T_IN + 0.05)
    if t > T_CTA - 0.1:
        kb = e_back(clamp((t - T_CTA + 0.1) / 0.4))
        paste(c, rrect(560 * kb + 2, 112, 56, MAG), 540, 1180)
        word(c, 'Start your enquiry', 540, 1180, 50, 900, IVORY, t - T_CTA)
    word(c, 'Link in bio', 540, 1300, 44, 800, PLUM, t - T_LINK + 0.05)
    colour_bar(c)
    return c


def base(t):
    if t < LC0:
        return scene_head(t)
    if t < LC1:
        return layercut(scene_head(t), scene_q(t), prog(t, LC0, LC1), n=6)
    if t < RS0:
        return scene_q(t)
    if t < RS0 + 0.25:
        k = prog(t, RS0, RS0 + 0.25)
        return scene_q(t) * (1 - k) + scene_icons(t) * k
    if t < SP0:
        return scene_icons(t)
    if t < SP0 + 0.25:
        k = prog(t, SP0, SP0 + 0.25)
        return scene_icons(t) * (1 - k) + scene_spiral(t) * k
    if t < SP1:
        return scene_spiral(t)
    if t < END0:
        return scene_one(t)
    if t < END1:
        return N.circle_wipe(scene_one(t), end_card(t), prog(t, END0, END1), CX, 760, col=MAG)
    return end_card(t)


def frame(t):
    c = base(t)
    c = grain(np.clip(c, 0, 1), 0.012, int(t * FPS))
    return np.clip(c * prog(t, 0.0, 0.1), 0, 1)


def write(i, c, d):
    cv2.imwrite(f'{d}/{i:05d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'times':
        for k, v in sorted(((k, v) for k, v in globals().items() if re.match(r'^(T|LC|RS|Q|SP|END)\w*$', k) and isinstance(v, float)), key=lambda kv: kv[1]):
            print(f'{k:10s} {v:6.2f}')
        print('DUR', DUR, 'NF', NF)
    elif mode == 'still':
        d = f'{S}/stills_out'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            write(int(float(ts) * 100), frame(float(ts)), d)
            print('still', ts, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            write(i, frame(i / FPS), d)
            if i % 30 == 0:
                print('frame', i, flush=True)
