"""P.S. Med Spa reel: captions, motion graphics, transitions, grade.

Per output frame:
  plate(shot)  = source frame -> push-in/transition transform -> grade
                 + scene graphics (big words / cards BEHIND her via the RVM matte,
                   cards + glow line in front), pinned to the background track
  transitions  = zoom-blur / whip / flash / blur-dissolve / light-leak at the cuts
  overlay      = small word captions, hero lead-in + italic lines, pills, strike
  post         = flash, bottom gradient, vignette, grain

Usage:
  python3 render.py still 1.2,7.5,...     # preview stills -> $WS/stills
  python3 render.py frames [workers]      # all frames -> $WS/out/frames
"""
import json, math, os, sys, time
import numpy as np, cv2
from multiprocessing import Pool

from common import (WS, HERE, FPS, NFRAMES, NOUT, FW, FH, W, H, CUTS, SHOTS, shot_of, frame_path, matte_path)
import gfx as G
import grade

E = G.E
cv2.setNumThreads(1)

WORDS = json.load(open(os.path.join(HERE, 'words.json')))
DISPLAY = {13: 'P.S.', 21: '&', 54: "patients'", 72: 'pours'}
TRACK = np.array(json.load(open(f'{WS}/track.json')))
JAMB = json.load(open(f'{WS}/jamb.json'))
PICS = [f'{WS}/src/pic{i}.jpg' for i in range(1, 5)]


def wd(i):
    return DISPLAY.get(i, WORDS[i]['w']).replace("'", '\u2019')


def ws(i):
    return WORDS[i]['s']


def words(a, b):
    return [wd(i) for i in range(a, b + 1)], [ws(i) for i in range(a, b + 1)]


def F(t):
    return int(round(t * FPS))


# ------------------------------------------------------------------ camera

# slow push-in per shot: (zoom at shot end, zoom center in output px)
PUSH = {0: (1.06, (430, 470)), 1: (1.05, (540, 900)), 2: (1.0, (540, 960)), 3: (1.0, (540, 960)),
        4: (1.03, (700, 800)), 5: (1.06, (440, 470)), 6: (1.07, (420, 600)), 7: (1.04, (600, 900)),
        8: (1.04, (540, 800)), 9: (1.06, (360, 470)), 10: (1.04, (700, 900)), 11: (1.05, (700, 1100)),
        12: (1.04, (600, 1100)), 13: (1.06, (355, 470))}


def push(k, src_fi):
    a, b = SHOTS[k]
    z1, c = PUSH[k]
    p = (src_fi - a) / max(1, b - a - 1)
    return 1 + (z1 - 1) * (0.5 - 0.5 * math.cos(math.pi * p)), c


# ------------------------------------------------------------------ timeline

def cap(a, b, end=None, y=905, x=540):
    w_, t_ = words(a, b)
    return dict(kind='cap', words=w_, times=t_, end=end if end is not None else ws(b + 1) - 0.045, x=x, y=y)


def times_from(ts, t_min):
    return [max(t, t_min) for t in ts]


# overlay (screen space) captions
OVERLAY = []
# scene elements per shot (drawn into the plate; 'behind' ones are occluded by her)
SCENE = {k: [] for k in range(len(SHOTS))}


CHAR = ('solid', tuple(E.hexc('#333740')[:3]))
FAST = dict(dur=0.22, stagger_total=0.10)


def hero(shot, l2, t2, end, cx, base, size=None, color='grey', l1=None, l3=None, l3_y=None, pin=1.0,
         l1_size=72, l3_size=100, max_w=900, glow=False, behind=True, l1_fill=('solid', (1.0, 1.0, 1.0)),
         l1_x=None, fast=False, out=0.22):
    if size is None:
        size = G.fit(l2, G.SERIF, 260, max_w)
    width = G.text_width(l2, G.SERIF, size)
    top = base - size * 0.80   # ascender line (k, l, b, d rise above cap height)
    SCENE[shot].append(dict(kind='l2', text=l2, t0=t2, end=end, x=cx, y=base, size=size, color=color,
                            pin=pin, glow=glow, behind=behind, fast=fast, out=out))
    if l1:
        w_, t_ = l1
        OVERLAY.append(dict(kind='l1', words=w_, times=t_, end=end,
                            x=l1_x if l1_x is not None else cx - width / 2 + size * 0.06,
                            y=top - size * 0.06, size=l1_size, fill=l1_fill))
    if l3:
        w_, t_ = l3
        OVERLAY.append(dict(kind='l3', words=w_, times=t_, end=end, x=cx,
                            y=l3_y if l3_y else base + l3_size * 1.15, size=l3_size))


C = [c / FPS for c in CUTS]  # cut times

# shot 0 -- sitting wide: "Hi, I'm / Martika / and I am here"
hero(0, 'Martika', ws(2), 2.64, 761, 432, size=150, l1=words(0, 1), l3=words(3, 6), l3_y=760)
OVERLAY.append(dict(cap(7, 9, end=3.40, y=770), times=[2.80, 2.92, 3.04]))

# shot 1 -- storefront
OVERLAY.append(cap(10, 12, end=4.44, y=1345))
hero(1, 'P.S. Med Spa', ws(13), C[2] - 0.12, 540, 1395, color='red', max_w=820, pin=0.0, glow=True, behind=False)
# shot 2 -- hallway, walking toward camera: "I have been a / cosmetic"
w_, t_ = words(16, 19)
hero(2, 'cosmetic', ws(20), C[3] - 0.22, 540, 890, color='dark', l1=(w_, times_from(t_, C[2] + 0.02)), max_w=880)
# shot 3 -- walks past then away down the hall: "and paramedical / tattoo artist"
w_, t_ = words(21, 22)
hero(3, 'tattoo', ws(23), C[4] - 0.20, 770, 650, size=175, l1=(w_, times_from(t_, C[3] + 0.02)), l1_size=60,
     color='dark')
SCENE[3].append(dict(SCENE[3][-1], text='artist', t0=ws(24), y=650 + 160))
OVERLAY.append(dict(cap(25, 27, end=10.84, y=1470), times=[10.30, 10.32, 10.50]))
# shot 4 -- prep room through the doorway: big "8.5" behind her, "years now."
hero(4, '8.5', ws(28), C[5] - 0.22, 440, 900, size=430, color='red', glow=True,
     l3=words(32, 33), l3_y=975, l3_size=92)
# shot 5 -- sitting: "I help women / wake up / made up."
w_, t_ = words(34, 36)
hero(5, 'wake up', ws(37), 15.05, 756, 432, size=150, l1=(w_, times_from(t_, C[5] + 0.02)), l3=words(39, 40), l3_y=770)
# shot 6 -- sitting closer + her work (photo cards)
for a, b, e in [(41, 44, None), (45, 49, None), (50, 51, None), (52, 54, None), (55, 56, None), (57, 57, 20.42)]:
    OVERLAY.append(cap(a, b, end=e, y=840, x=480))
OVERLAY[-6]['times'] = times_from(OVERLAY[-6]['times'], C[6] - 0.01)
SCENE[6].append(dict(kind='cards'))
# shot 7 -- gloves: "seeing that / glow / in their eyes"
hero(7, 'glow', ws(60), 22.24, 430, 640, size=300, color='red', glow=True,
     l1=words(58, 59), l3=words(61, 63), l3_y=1150, pin=0.6, l1_fill=CHAR)
OVERLAY.append(cap(64, 66, end=23.62, y=1380))
# shot 8 -- pigments: pills "Brows" / "Lips", "into my / heart."
OVERLAY.append(dict(kind='pill', text='Brows', t0=ws(67), end=24.98, x=300, y=1180))
OVERLAY.append(dict(cap(68, 69, end=24.95, y=1196, x=545), times=times_from(words(68, 69)[1], C[8] + 0.05)))
OVERLAY.append(dict(kind='pill', text='Lips', t0=24.10, end=24.98, x=790, y=1180))
OVERLAY.append(cap(71, 74, end=25.70, y=1490))
hero(8, 'heart.', 25.86, C[9] - 0.18, 540, 470, size=230, color='red', glow=True, l1=words(75, 76), pin=0.6,
     behind=False, fast=True, out=0.14, l1_fill=CHAR)
# shot 9 -- sitting
OVERLAY.append(dict(cap(78, 79, y=1110, x=560), times=times_from(words(78, 79)[1], C[9] + 0.04)))
OVERLAY.append(cap(80, 83, y=1110, x=560))
OVERLAY.append(cap(84, 86, y=1110, x=560))
hero(9, 'time', ws(89), 31.14, 575, 432, size=190, l1=words(87, 88), l1_fill=CHAR)
_tw = G.text_width('time', G.SERIF, 190)
SCENE[9].append(dict(kind='strike', x0=575 - _tw / 2 - 16, x1=575 + _tw / 2 + 16, y=432 - 190 * 0.30,
                     t0=30.70, end=31.14, pin=1.0))
# (l1 of 'time' ends with the word: shorten it)
OVERLAY[-1]['end'] = 30.70
OVERLAY.append(cap(90, 93, end=31.66, y=1110, x=560))
hero(9, 'eyebrows', 31.40, C[10] - 0.04, 720, 432, size=140, max_w=900, fast=True)
# "even in the morning," with a red strike (no more drawing brows every morning)
w_, t_ = words(95, 98)
OVERLAY.append(dict(kind='strike_cap', words=w_, times=times_from(t_, C[10] + 0.01), end=32.95, x=480, y=600,
                    size=88, strike_t=32.50, under=True))
# shot 10 -- tray: "just come / see me."
hero(10, 'see me.', ws(101), 34.45, 385, 878, size=215, color='red', l1=words(99, 100), pin=0.5)
OVERLAY[-1]['end'] = 33.92   # 'just come' clears before 'I am here'
OVERLAY.append(dict(cap(103, 105, end=35.02, y=620, x=470), fill=CHAR))
# shot 11 -- pigment cup
OVERLAY.append(cap(106, 109, y=760))
OVERLAY.append(cap(110, 112, end=36.48, y=760))
# shot 12 -- bottle: "start a / treatment plan"
w_, t_ = words(113, 114)
hero(12, 'treatment plan', ws(115), 38.30, 540, 670, l1=(w_, times_from(t_, C[12] + 0.04)), max_w=920, pin=0.5, l1_fill=CHAR, color='dark')
OVERLAY[-1]['end'] = 37.86
OVERLAY.append(cap(117, 119, end=C[13] - 0.10, y=905))
# shot 13 -- sitting: "tattoo / glow up."
hero(13, 'glow up.', ws(121), 99.0, 684, 432, size=160, color='red', glow=True, l1=words(120, 120), max_w=860,
     l1_fill=CHAR)

def _min_hold(hold=0.38):
    """Delay a caption that replaces another at the same spot so the previous group's last word holds >= `hold` s."""
    caps = sorted([e for e in OVERLAY if e['kind'] == 'cap'], key=lambda e: e['times'][0])
    for prev, nxt in zip(caps, caps[1:]):
        if (prev['x'], prev['y']) != (nxt['x'], nxt['y']):
            continue
        need = prev['times'][-1] + hold
        if nxt['times'][0] < need:
            nxt['times'] = [max(t, need + 0.02 * i) for i, t in enumerate(nxt['times'])]
            prev['end'] = need - 0.09


_min_hold()

# transitions at cuts: (type, frames before, frames after)
TRANS = {78: 'zoom', 137: 'flash', 196: 'whip', 246: 'zoom', 310: 'flash', 362: 'punch', 498: 'zoom',
         570: 'whipv', 637: 'leak', 770: 'zoom', 837: 'blur', 884: 'whip', 937: 'flash'}
SPAN = {'zoom': (4, 4), 'flash': (3, 4), 'whip': (3, 3), 'whipv': (3, 3), 'punch': (2, 3), 'blur': (4, 4),
        'leak': (5, 5)}

# ------------------------------------------------------------------ photo cards (shot 6)

CARDS = [  # pic, w, h, final center, ry, rz, t_in, from side, behind
    (0, 300, 280, (140, 600), 26, -5, 15.35, -1, True),
    (1, 250, 420, (895, 560), -26, 5, 15.78, 1, True),
    (2, 330, 309, (285, 1340), 18, 5, 16.30, -1, False),
    (3, 320, 300, (800, 1250), -18, -5, 16.78, 1, False),
]
LINE_PTS = [(-60, 1150), (170, 1060), (330, 1290), (545, 1135), (790, 1265), (950, 1080), (1150, 1010)]
LINE_T = (17.62, 19.35)
CARDS_OUT = (20.42, 20.80)


def card_state(i, t):
    pi, w, h, (fx, fy), ry, rz, t_in, side, behind = CARDS[i]
    p = E.prog(t, t_in, t_in + 0.60)
    if p <= 0:
        return None
    e = E.e_out_expo(p)
    x = fx + side * 760 * (1 - e)
    y = fy + 120 * (1 - e)
    z = 500 * (1 - e)
    ryy = ry + side * -60 * (1 - e)
    rzz = rz * e + side * 14 * (1 - e)
    op = E.prog(t, t_in, t_in + 0.18)
    # float
    tt = t - t_in
    y += math.sin(tt * 1.7 + i) * 7 * e
    ryy += math.sin(tt * 1.1 + i * 2) * 3 * e
    # fly out toward camera
    q = E.prog(t, CARDS_OUT[0] + i * 0.03, CARDS_OUT[1])
    if q > 0:
        qe = E.e_in_cubic(q)
        z -= 1150 * qe
        x += (fx - 540) * 1.2 * qe
        y += (fy - 960) * 1.2 * qe
        op *= 1 - E.prog(q, 0.55, 1.0)
    return (PICS[pi], w, h, x, y, z, ryy, rzz, op, behind)


def draw_cards(layer_b, layer_f, t, sub=1):
    """Cards with optional sub-frame motion blur (sub>1 averages sub samples over half a frame)."""
    for i in range(len(CARDS)):
        samples = [t - (0.5 / FPS) * (s / max(1, sub - 1) - 0.5) for s in range(sub)] if sub > 1 else [t]
        acc = None
        for ts in samples:
            st = card_state(i, ts)
            if st is None:
                continue
            path, w, h, x, y, z, ry, rz, op, behind = st
            tmp = G.new_layer()
            G.draw_card(tmp, path, x, y, w, h, ry=ry, rz=rz, z=z, opacity=op)
            acc = tmp if acc is None else acc + tmp
        if acc is not None:
            acc /= len(samples)
            G.over(layer_b if card_state(i, t) and card_state(i, t)[9] else layer_f, acc)


def card_moving(t):
    for i in range(len(CARDS)):
        t_in = CARDS[i][6]
        if t_in <= t <= t_in + 0.45 or t >= CARDS_OUT[0]:
            return True
    return False


# ------------------------------------------------------------------ plates

_frame_cache = {}


def read_src(fi):
    if fi in _frame_cache:
        return _frame_cache[fi]
    img = cv2.imread(frame_path(fi))[..., ::-1].astype(np.float32) / 255
    img = cv2.GaussianBlur(img, (0, 0), 0.45)
    m = cv2.imread(matte_path(fi), 0).astype(np.float32) / 255
    if shot_of(fi) == 12:   # only her hands occlude here; the cabinet's red light up top is not foreground
        m[:int(690 * FH / H)] = 0
    if str(fi) in JAMB:   # foreground door jamb in shot 4 also occludes the scene text
        xs = (np.arange(FW, dtype=np.float32) - (JAMB[str(fi)] - 30) * FW / W) / (60.0 * FW / W)
        m = np.maximum(m, np.clip(xs + 0.5, 0, 1)[None, :])
    if len(_frame_cache) > 6:
        _frame_cache.pop(next(iter(_frame_cache)))
    _frame_cache[fi] = (img, m)
    return img, m


def affine(z, c, dx=0.0, dy=0.0, r=1.0):
    px, py = c
    return np.float32([[z * r, 0, px * (1 - z) + dx], [0, z * r, py * (1 - z) + dy]])


def scene_graphics(k, t, src_fi):
    """Behind / front scene layers for shot k in unzoomed plate coords (or None)."""
    els = SCENE[k]
    if not els:
        return None, None
    lb, lf = None, None
    for el in els:
        if el['kind'] == 'l2':
            if t < el['t0'] or t > el['end'] + el['out'] + 0.02:
                continue
            a_fi = min(max(F(el['t0']), SHOTS[k][0]), SHOTS[k][1] - 1)
            off = (TRACK[src_fi] - TRACK[a_fi]) * el['pin']
            tgt = G.new_layer()
            if el['glow']:
                g = G.new_layer()
                G.hero_l2(g, t, el['text'], el['t0'], el['end'], el['x'] + off[0], el['y'] + off[1], el['size'],
                          el['color'], drift=0.0, out_dur=el['out'], **(FAST if el['fast'] else {}))
                aura = cv2.resize(cv2.GaussianBlur(cv2.resize(g, (W // 4, H // 4), interpolation=cv2.INTER_AREA),
                                                   (0, 0), 7), (W, H), interpolation=cv2.INTER_LINEAR)
                col = np.array([1.0, 0.25, 0.27], np.float32)
                aura = np.concatenate([aura[..., 3:4] * col, aura[..., 3:4]], 2) * 0.55
                G.over(tgt, aura)
                G.over(tgt, g)
            else:
                G.hero_l2(tgt, t, el['text'], el['t0'], el['end'], el['x'] + off[0], el['y'] + off[1], el['size'],
                          el['color'], drift=0.0, out_dur=el['out'], **(FAST if el['fast'] else {}))
            if el['behind']:
                lb = tgt if lb is None else G.over(lb, tgt)
            else:
                lf = tgt if lf is None else G.over(lf, tgt)
        elif el['kind'] == 'strike':
            if t < el['t0'] or t > el['end'] + 0.2:
                continue
            a_fi = min(max(F(el['t0']), SHOTS[k][0]), SHOTS[k][1] - 1)
            off = (TRACK[src_fi] - TRACK[a_fi]) * el['pin']
            lb = G.new_layer() if lb is None else lb
            G.strike(lb, t, el['x0'] + off[0], el['x1'] + off[0], el['y'] + off[1], el['t0'], el['end'], thick=12)
        elif el['kind'] == 'cards':
            if t < CARDS[0][6] or t > CARDS_OUT[1] + 0.05:
                continue
            lb = G.new_layer() if lb is None else lb
            lf = G.new_layer() if lf is None else lf
            a_fi = F(CARDS[0][6])
            off = (TRACK[src_fi] - TRACK[a_fi]) * 0.5
            M = np.float32([[1, 0, off[0]], [0, 1, off[1]]])
            cb, cf = G.new_layer(), G.new_layer()
            draw_cards(cb, cf, t, sub=(12 if t >= CARDS_OUT[0] else 6) if card_moving(t) else 1)
            # glowing line between her and the front cards
            pl = E.prog(t, *LINE_T)
            if pl > 0:
                tail = E.prog(t, 19.95, 20.55)
                lay = G.new_layer()
                G.glow_line(lay, LINE_PTS, E.e_inout_cubic(pl), E.e_in_cubic(tail),
                            opacity=1 - E.prog(t, 20.45, 20.6))
                G.over(lf, lay)
            G.over(lb, cv2.warpAffine(cb, M, (W, H)))
            G.over(lf, cv2.warpAffine(cf, M, (W, H)))
    return lb, lf


def plate(k, src_fi, t, zx=1.0, dx=0.0, dy=0.0):
    """Graded plate of shot k at source frame src_fi with scene graphics, in output coords."""
    src_fi = min(src_fi, NFRAMES - 1)   # the end hold repeats the last frame
    z0, c = push(k, src_fi)
    z = z0 * zx
    img, m = read_src(src_fi)
    M = affine(z, c, dx, dy, r=W / FW)
    rgb = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    mat = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    rgb = grade.grade(rgb, k)
    lb, lf = scene_graphics(k, t, src_fi)
    if lb is not None or lf is not None:
        ML = affine(z, c, dx, dy)
        out = rgb.copy()
        if lb is not None:
            lb = cv2.warpAffine(lb, ML, (W, H), flags=cv2.INTER_LINEAR)
            out = out * (1 - lb[..., 3:4]) + lb[..., :3]
            mm = np.clip((mat - 0.08) / 0.77, 0, 1)
            mm = (mm * mm * (3 - 2 * mm))[..., None]
            out = out * (1 - mm) + rgb * mm
        if lf is not None:
            lf = cv2.warpAffine(lf, ML, (W, H), flags=cv2.INTER_LINEAR)
            out = out * (1 - lf[..., 3:4]) + lf[..., :3]
        rgb = out
    return np.clip(rgb, 0, 1.2).astype(np.float32)


# ------------------------------------------------------------------ transitions

def radial_blur(img, amount, c=(540, 960), n=8):
    if amount < 0.004:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        s = 1 + amount * i / (n - 1)
        acc += cv2.warpAffine(img, affine(s, c), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n


def trans_at(fi):
    for c, typ in TRANS.items():
        b, a = SPAN[typ]
        if c - b <= fi < c + a:
            return c, typ
    return None, None


_whip_blur = {}
_ov_blur = {}


def compose_plate(fi, t):
    """Video plate (with scene graphics) incl. transitions. Returns (rgb, flash_amount, leak_params)."""
    k = shot_of(fi)
    c, typ = trans_at(fi)
    flash = 0.0
    leak = None
    if typ is None:
        return plate(k, fi, t), 0.0, None
    b, a = SPAN[typ]
    k_out, k_in = shot_of(c - 1), shot_of(c)
    if typ == 'zoom':
        if fi < c:
            p = (fi - (c - b) + 1) / b
            zx = 1 + 0.30 * E.e_in_cubic(p)
            img = radial_blur(plate(k_out, fi, t, zx=zx), 0.10 * p ** 2)
        else:
            p = (fi - c + 1) / (a + 1)
            zx = 1 + 0.30 * (1 - E.e_out_cubic(p))
            img = radial_blur(plate(k_in, fi, t, zx=zx), 0.10 * (1 - p) ** 2)
        flash = 0.22 * math.exp(-abs(fi - c + 0.5) / 1.0)
        return img, flash, None
    if typ == 'flash':
        img = plate(k, fi, t)
        d = abs(fi - c + 0.5)
        flash = 0.95 * math.exp(-d / 1.15)
        s = 9 * math.exp(-d / 1.3)
        if s > 0.6:
            img = cv2.GaussianBlur(img, (0, 0), s)
        return img, flash, None
    if typ in ('whip', 'whipv'):
        n = b + a
        u = E.e_inout_cubic((fi - (c - b) + 0.5) / n)
        u2 = E.e_inout_cubic((fi - (c - b) + 1.0) / n)
        L = W if typ == 'whip' else H
        if typ == 'whip':
            p_out = plate(k_out, min(fi, c - 1), t, dx=-u * L)
            p_in = plate(k_in, max(fi, c), t, dx=(1 - u) * L)
        else:
            p_out = plate(k_out, min(fi, c - 1), t, dy=u * L)
            p_in = plate(k_in, max(fi, c), t, dy=-(1 - u) * L)
        # stitch: the outgoing plate covers its moved rectangle, the incoming the rest
        if typ == 'whip':
            edge = W - u * L
            ramp = np.clip((edge - np.arange(W, dtype=np.float32)) / 160 + 0.5, 0, 1)[None, :]
        else:
            edge = u * L
            ramp = np.clip((np.arange(H, dtype=np.float32) - edge) / 160 + 0.5, 0, 1)[:, None]
        cov = np.broadcast_to(ramp, (H, W))
        img = p_out * cov[..., None] + p_in * (1 - cov[..., None])
        vel = abs(u2 - u) * L
        k_len = int(min(220, max(vel * 0.9, 61))) | 1
        if k_len > 2:
            img = cv2.blur(img, (k_len, 1) if typ == 'whip' else (1, k_len))
        _whip_blur[fi] = (k_len, 1) if typ == 'whip' else (1, k_len)
        return img, 0.06 * math.exp(-abs(fi - c + 0.5) / 1.0), None
    if typ == 'punch':
        if fi < c:
            p = (fi - (c - b) + 1) / b
            img = plate(k_out, fi, t, zx=1 + 0.04 * p)
        else:
            p = (fi - c + 1) / a
            img = plate(k_in, fi, t, zx=1 + 0.10 * (1 - E.e_out_cubic(p)))
            img = radial_blur(img, 0.03 * (1 - p))
        return img, 0.10 * math.exp(-abs(fi - c + 0.5) / 0.8), None
    if typ == 'blur':
        n = b + a
        mix = E.smooth((fi - (c - b) + 0.5) / n)
        s = 16 * math.sin(math.pi * mix)
        p_out = plate(k_out, min(fi, c - 1), t)
        p_in = plate(k_in, max(fi, c), t)
        img = p_out * (1 - mix) + p_in * mix
        if s > 0.6:
            img = cv2.GaussianBlur(img, (0, 0), s)
            _ov_blur[fi] = s * 0.5
        return img, 0.0, None
    if typ == 'leak':
        p = (fi - (c - b) + 0.5) / (b + a)
        kk = k_out if fi < c else k_in
        zx = 1 + 0.05 * math.sin(math.pi * p)
        img = plate(kk, fi, t, zx=zx)
        return img, 0.25 * math.exp(-abs(fi - c + 0.5) / 1.2), p
    return plate(k, fi, t), 0.0, None


_leak_grid = None


def light_leak(img, p):
    """Brand-red light sweep across the frame (additive), p: 0..1 through the transition."""
    global _leak_grid
    if _leak_grid is None:
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
        _leak_grid = (xx, yy)
    xx, yy = _leak_grid
    ang = math.radians(28)
    d = xx * math.cos(ang) + yy * math.sin(ang)
    pos = -500 + p * 2300
    env = math.sin(math.pi * min(max(p, 0), 1))
    band = np.exp(-((d - pos) / 260) ** 2) * env
    core = np.exp(-((d - pos) / 70) ** 2) * env
    red = np.array(G.RED, np.float32)
    warm = np.array([1.0, 0.78, 0.62], np.float32)
    lay = band[..., None] * red * 1.1 + core[..., None] * warm * 0.9
    lay = cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)
    return 1 - (1 - img) * (1 - np.clip(lay, 0, 1))


# ------------------------------------------------------------------ overlay

def draw_overlay(t, base):
    lay = G.new_layer()
    for el in OVERLAY:
        k = el['kind']
        if k == 'cap':
            G.caption(lay, t, el['words'], el['times'], el['end'], el['x'], el['y'],
                      fill=el.get('fill', ('solid', (1.0, 1.0, 1.0))))
        elif k == 'l1':
            G.hero_l1(lay, t, el['words'], el['times'], el['end'], el['x'], el['y'], size=el['size'], fill=el['fill'])
        elif k == 'l3':
            G.hero_l3(lay, t, el['words'], el['times'], el['end'], el['x'], el['y'], size=el['size'])
        elif k == 'pill':
            G.glass_pill(lay, base, t, el['text'], el['x'], el['y'], el['t0'], el['end'])
        elif k == 'strike_cap':
            G.hero_l3(lay, t, el['words'], el['times'], el['end'], el['x'], el['y'], size=el['size'])
            text = ' '.join(el['words'])
            wdt = G.text_width(text, G.SERIF_I, el['size'])
            y_line = el['y'] + el['size'] * 0.16 if el.get('under') else el['y'] - el['size'] * 0.30
            G.strike(lay, t, el['x'] - wdt / 2 - 14, el['x'] + wdt / 2 + 14, y_line,
                     el['strike_t'], el['end'], thick=7 if el.get('under') else 9)
    return lay


# ------------------------------------------------------------------ post

_post = {}


def post(img, fi, flash):
    if not _post:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.70)) ** 2)
        vig = np.clip(1 - 0.22 * r ** 2.6, 0.6, 1)
        bot = np.clip((yy / H - 0.80) / 0.20, 0, 1) ** 1.6 * 0.30
        _post['mul'] = (vig * (1 - bot))[..., None].astype(np.float32)
        rng = np.random.default_rng(11)
        _post['grain'] = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]
    out = img * _post['mul']
    if flash > 0.01:
        glow = cv2.GaussianBlur(cv2.resize(out, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 6)
        glow = cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR)
        out = out + glow * flash * 0.8
        out = 1 - (1 - out) * (1 - flash * 0.85)
    g = cv2.resize(_post['grain'][fi % 8], (W, H), interpolation=cv2.INTER_LINEAR)
    lum = out.mean(2, keepdims=True)
    out = out + g[..., None] * 0.012 * (1.2 - lum)
    # end fade
    t = fi / FPS
    f = E.smooth(E.prog(t, 40.58, 41.06))
    if f > 0:
        out = out * (1 - f)
    return np.clip(out, 0, 1)


def render_frame(fi):
    t = fi / FPS
    base, flash, leak = compose_plate(fi, t)
    base = np.clip(base, 0, 1)
    if leak is not None:
        base = light_leak(base, leak)
    lay = draw_overlay(t, base)
    sb = _ov_blur.pop(fi, None)
    if sb:
        lay = cv2.GaussianBlur(lay, (0, 0), sb)
    kb = _whip_blur.pop(fi, None)
    if kb is not None and max(kb) > 2:
        lay = cv2.blur(lay, (max(1, kb[0] // 2) | 1, max(1, kb[1] // 2) | 1))
    out = base * (1 - lay[..., 3:4]) + lay[..., :3]
    return post(out, fi, flash)


def save(img, path):
    cv2.imwrite(path, (np.clip(img, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8),
                [cv2.IMWRITE_PNG_COMPRESSION, 1] if path.endswith('.png') else [cv2.IMWRITE_JPEG_QUALITY, 93])


def _work(args):
    fis, outdir = args
    for fi in fis:
        p = f'{outdir}/{fi:04d}.png'
        if os.path.exists(p):
            continue
        save(render_frame(fi), p + '.tmp.png')
        os.replace(p + '.tmp.png', p)
    return len(fis)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'still'
    if cmd == 'still':
        os.makedirs(f'{WS}/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            fi = int(ts) if '.' not in ts else F(float(ts))
            t0 = time.time()
            save(render_frame(fi), f'{WS}/stills/f{fi:04d}.jpg')
            print('still', fi, f'{fi / FPS:.2f}s', f'{time.time() - t0:.2f}s', flush=True)
    elif cmd == 'frames':
        nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        hi = int(sys.argv[4]) if len(sys.argv) > 4 else NOUT
        outdir = os.environ.get('FRAMES_DIR', f'{WS}/out/frames')
        os.makedirs(outdir, exist_ok=True)
        fis = list(range(lo, hi))
        # contiguous chunks keep the per-process frame cache useful
        n = max(1, len(fis) // (nw * 6))
        chunks = [fis[i:i + n] for i in range(0, len(fis), n)]
        t0 = time.time()
        with Pool(nw) as pool:
            done = 0
            for n in pool.imap_unordered(_work, [(c, outdir) for c in chunks]):
                done += n
                print(f'{done}/{len(fis)} {time.time() - t0:.0f}s', flush=True)
