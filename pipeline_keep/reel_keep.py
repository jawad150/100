"""BMHC "What did you keep?" (Heart Work), 9:16, 33 s - B&W editorial collage (after the user's Pinterest reference)
with Heritage Magenta as the one accent. Illustrative story built on the brief's recipe-card example.

0-3.4 the detail (the thumb hides the last line - eclipse) | 3.4-9.5 "1. Who gave you this?" | 9.5-15.6 "2. What do you
remember about her?" (retro photo, aurora, cardamom) | 15.6-20.2 the spoons (spiral) | 20.2-24.3 "3. The line" (layercut,
the thumb lifts) | 24.3-26.7 "That was her." | 26.7-31.3 into the drawer + "What's one thing your family has kept?" + arrow
wipe | 31.3-33 end card (official logo + @thebmhc).

Usage: python3 reel_keep.py still 1.0,5.0 | range a b
"""
import os, sys, json, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_keep as G
from frames_keep import (W, H, S, ROOT, INK, WHITE, MAG, DARK, GREYT, BARS, paper, place, dotted_ring, photo_circle, type2, thumb_eclipse,
                         arrow_wipe, caption, tag, paste, rrect, text_sprite, load, logo, aurora, layercut, cover, clamp, prog, e_out,
                         e_inout, e_back, grain, _grid, Clip)

FPS = 30
DUR = 33.0
NF = int(DUR * FPS)
INFO = json.load(open(f'{S}/tts/info.json'))
WORDS = INFO['words']


def norm(w):
    return re.sub(r"[^a-z']", '', w.lower())


def A(wd, k=0):
    n = 0
    for w in WORDS:
        if norm(w[0]) == norm(wd):
            if n == k:
                return w[1]
            n += 1
    raise KeyError(wd)


SL = {s[0]: s[1] for s in INFO['slots']}
C2, C3, C4, C5, C6, C7, C8 = 3.4, 9.45, 15.6, 20.2, 24.3, 26.7, 31.3
T_CARD, T_SPOONS, T_NANI = A('cardamom'), A('spoons'), A('nani')
LIFT0 = C5 + 0.25
LINE = (505, 990)
GATES = load(f'{ROOT}/workspace_bmhc/web/img/W6A9208-1-scaled.jpg')
KITCHEN = None


def kitchen():
    global KITCHEN
    if KITCHEN is None:
        cap = cv2.VideoCapture(f'{ROOT}/workspace_toast/clips/43033.mp4')
        cap.set(cv2.CAP_PROP_POS_MSEC, 3000)
        ok, f = cap.read()
        KITCHEN = f[..., ::-1].astype(np.float32) / 255
    return KITCHEN


def card(c, t, size=1250, cx=600, cy=980, rot=-4, push=0.0):
    place(c, 'recipe', cx, cy, size * (1 + push), 1.0, rot, mono=True)


def s_detail(t):
    c = paper().copy()
    push = 0.04 * prog(t, 0, C2)
    card(c, t, push=push)
    thumb_eclipse(c, LINE[0], LINE[1], 215 * (1 + push), t - 0.1, 0.0)
    tag(c, 'HEART WORK', 64, 150, MAG, a=1.0)
    word = text_sprite('Illustrative story', 500, 24, GREYT)
    paste(c, word, 64 + word.shape[1] / 2, 205)
    type2(c, 'That last line', 'has nothing to do with cooking.', 64, 300, t - SL['o1'] + 0.1, 92)
    return c


def s_who(t):
    c = paper().copy()
    type2(c, '1. Who gave', 'you this?', 64, 260, t - SL['q1'] + 0.05, 92)
    dotted_ring(c, 560, 900, 330, t, 1.0, frac=e_out(prog(t, C2 + 0.05, C2 + 0.8)))
    photo_circle(c, GATES, 560, 900, 300, t - C2 - 0.25, t)
    place(c, 'envelope', 820, 1230, 420, t - T_NANI + 0.1, -8, slide=(400, 0))
    return c


def s_memory(t):
    c = paper().copy()
    c = aurora(c, t, 0.2 * prog(t, SL['o3'] - 0.3, SL['o3'] + 0.8), 0.04, 0.15)
    type2(c, '2. What do you', 'remember about her?', 64, 260, t - SL['q2'] + 0.05, 92)
    dotted_ring(c, 540, 900, 330, t, 1.0, frac=e_out(prog(t, C3, C3 + 0.8)))
    photo_circle(c, kitchen(), 540, 900, 300, t - C3 - 0.25, t)
    place(c, 'cardamom', 300, 1210, 340, t - T_CARD + 0.05, 10, mono=False, slide=(-300, 120))
    return c


def s_spoons(t):
    c = paper().copy()
    u = prog(t, C4, C4 + 1.4)
    k = e_inout(u)
    # SPIRAL: the dotted rings spin and close in on the spoons drawn on the card
    size = 1250 + 450 * k
    card(c, t, size, 600 - 220 * k, 980 + 80 * k, -4)
    for i, r in enumerate((420, 330, 250)):
        dotted_ring(c, 560 + 120 * k, 700 + 40 * k, r * (1 - 0.55 * k), t * (3 + 2 * i) * (1 if i % 2 else -1), 1.0)
    type2(c, 'She never', 'measured anything.', 64, 260, t - SL['o4'] + 0.05, 92)
    place(c, 'spoon', 840, 620, 420, t - T_SPOONS + 0.05, 20, mono=False, slide=(0, -500))
    return c


def s_line(t):
    c = paper().copy()
    zoom = 0.05 * prog(t, LIFT0, C6)
    card(c, t, push=zoom)
    lift = prog(t, LIFT0, LIFT0 + 0.8)
    thumb_eclipse(c, LINE[0], LINE[1], 215, 1.0, lift)
    if lift > 0.6:                                               # the revealed line glows magenta for a moment
        yy, xx = _grid()
        g = np.exp(-(((xx - 470) / 260) ** 2 + ((yy - 975) / 70) ** 2)) * 0.18 * clamp((lift - 0.6) / 0.4) * (1 - prog(t, SL['o5'] + 1.5, C6))
        c[:] = np.clip(c + g[..., None] * MAG, 0, 1)
    type2(c, '3. The line', 'we could only glimpse.', 64, 300, t - C5 - 0.1, 92)
    return c


def s_her(t):
    c = paper().copy()
    dotted_ring(c, 540, 880, 330, t, 1.0, frac=e_out(prog(t, C6, C6 + 0.7)))
    place(c, 'photo', 540, 880, 560, t - C6 - 0.2, 6, slide=(0, 300))
    type2(c, 'That', 'was her.', 64, 300, t - SL['o6'] + 0.1, 120)
    return c


def s_drawer(t):
    c = paper().copy()
    place(c, 'drawer', 540, 1100, 760, t - C7 - 0.05, 0, slide=(0, 200))
    u = prog(t, C7 + 0.6, C7 + 1.6)
    if u < 1:
        k = e_inout(u)
        place(c, 'recipe', 520, 760 + 330 * k, 360 * (1 - 0.35 * k), 1.0, -70 + 10 * k, a=1 - clamp((u - 0.85) / 0.15))
    type2(c, 'What’s one thing', 'your family has kept?', 64, 300, t - C7 - 0.3, 92)
    return c


def s_end(t):
    c = np.empty((H, W, 3), np.float32)
    c[:] = INK
    u = t - C8
    lg = logo(820)
    paste(c, lg, 540, 820 + 16 * (1 - e_out(clamp(u / 0.5))), clamp(u / 0.3))
    s = text_sprite('@thebmhc', 700, 46, (0.8, 0.8, 0.8))
    paste(c, s, 540, 1120, clamp((u - 0.2) / 0.3))
    for i, col in enumerate(BARS):
        kk = clamp((u - 0.08 * i) / 0.3)
        c[H - 22:, int(W * i / 4):int(W * i / 4 + W / 4 * e_out(kk))] = col
    return c


SCENES = [(0, s_detail), (C2, s_who), (C3, s_memory), (C4, s_spoons), (C5, s_line), (C6, s_her), (C7, s_drawer), (C8, s_end)]


def base(t):
    i = max(j for j, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[i]
    c = fn(t)
    if i and t - t0 < 0.35 and fn is not s_end:                 # collage slide-in on each cut
        k = e_out((t - t0) / 0.35)
        prev = SCENES[i - 1][1](t)
        if fn is s_line:
            return layercut(prev, c, k, n=6)                      # LAYERCUT into the reveal
        sh = int(W * (1 - k))
        out = prev.copy()
        out[:, :W - sh] = prev[:, sh:] if sh else prev
        out[:, W - sh:] = c[:, :sh] if sh else out[:, W - sh:]
        return out
    if fn is s_drawer and t > C8 - 0.75:
        c = arrow_wipe(c, prog(t, C8 - 0.75, C8 + 0.05))
    return c


KEY = {'nani', 'cardamom', 'spoons', 'more', 'her'}


def chunks():
    out, cur = [], []
    for i, w in enumerate(WORDS):
        cur.append(w)
        nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
        if nxt is None or len(cur) == 3 or w[0].endswith(('.', ',', '?', '…')) or nxt[1] - w[2] > 0.45 or nxt[3] != w[3]:
            out.append(cur)
            cur = []
    merged = []
    for ch in out:
        if len(ch) == 1 and merged and len(merged[-1]) <= 2 and ch[0][1] - merged[-1][-1][2] < 0.4 and ch[0][3] == merged[-1][-1][3]:
            merged[-1] = merged[-1] + ch
        else:
            merged.append(ch)
    return merged


CH = chunks()


def subtitles(c, t):
    for i, ch in enumerate(CH):
        t0 = ch[0][1] - 0.05
        t1 = min(ch[-1][2] + 0.45, CH[i + 1][0][1] - 0.05) if i + 1 < len(CH) else ch[-1][2] + 0.6
        if t0 <= t < t1 and t < C7:
            parts = [(w[0], MAG if norm(w[0]) in KEY else WHITE) for w in ch]
            caption(c, parts, 1660, t - t0, 56)
    return c


def frame(t):
    c = base(t)
    c = subtitles(c, t)
    c = grain(np.clip(c, 0, 1), 0.012, int(t * FPS))
    return np.clip(c * prog(t, 0, 0.12), 0, 1)


def write(i, c, d):
    cv2.imwrite(f'{d}/{i:05d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'times':
        print([' '.join(w[0] for w in ch) for ch in CH])
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
