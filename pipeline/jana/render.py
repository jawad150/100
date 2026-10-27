"""P.S. Med Spa "Meet Jana" reel: captions, motion graphics, transitions, grade.

Per output frame:
  plate(shot)  = source frame -> push-in/transition transform -> grade
                 + scene graphics (big words BEHIND her via the RVM matte, or in front
                   with a red glow), pinned to the background track
  transitions  = only three: zoom-blur push, one whip, brand-red light leak
  overlay      = small word captions, hero lead-in + italic lines
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
DISPLAY = {27: 'P.S.'}
TRACK = np.array(json.load(open(f'{WS}/track.json')))


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
SIT = (1.06, (700, 600))   # interview set: in toward her face
PUSH = {0: SIT, 1: (1.04, (420, 1100)), 2: (1.05, (540, 1000)), 3: (1.03, (540, 700)), 4: (1.04, (500, 600)),
        5: SIT, 6: (1.05, (300, 600)), 7: (1.04, (400, 900)), 8: (1.04, (540, 900)), 9: SIT,
        10: (1.05, (300, 800)), 11: SIT, 12: (1.04, (500, 800)), 13: (1.05, (540, 500))}


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

# shot 0 -- sitting wide: "Hi, I'm / Jana / Strada."  (her head is right of centre: the
# big word sits over the painting and its last letter tucks behind her hair)
hero(0, 'Jana', ws(2), C[1] - 0.18, 455, 640, size=200, l1=words(0, 1), l1_fill=CHAR, l3=words(3, 3), l3_y=880,
     l3_size=96)
OVERLAY[-1]['x'] = 650   # 'Strada.' sits on her black top
# shot 1 -- syringe tray: "I am a cosmetic / injector"
w_, t_ = words(4, 7)
hero(1, 'injector', ws(8), 3.58, 520, 1320, color='dark', l1=(w_, times_from(t_, C[1] + 0.02)), max_w=700,
     pin=0.5, behind=False, l1_fill=CHAR)
OVERLAY.append(dict(cap(9, 11, end=C[2] - 0.06, y=1480, x=520), fill=CHAR))
# shot 2 -- laser close-up: "specialist for the last / 19 / years,"
OVERLAY.append(dict(cap(12, 15, y=520, x=700), times=times_from(words(12, 15)[1], C[2] + 0.02)))
hero(2, '19', ws(16), 6.84, 800, 860, size=400, color='red', glow=True, l3=words(17, 17), l3_y=950, l3_size=96)
OVERLAY.append(dict(cap(18, 22, end=8.02, y=1180), times=times_from(words(18, 22)[1], C[3] + 0.06)))
# shot 3 -- storefront: "Clinic for Plastic Surgery / P.S. Medical Spa"
OVERLAY.append(dict(kind='l3', words=words(23, 26)[0], times=words(23, 26)[1], end=C[4] - 0.14, x=540, y=1180, size=78))
hero(3, 'P.S. Medical Spa', ws(27), C[4] - 0.14, 540, 1350, color='red', max_w=900, pin=0.0, glow=True, behind=False)
# shot 4 -- laser hair removal (she stands left): "My specialty is / really just / listening"
OVERLAY.append(dict(cap(30, 32, y=760, x=470), times=times_from(words(30, 32)[1], C[4] + 0.03)))
hero(4, 'listening', ws(35), 13.20, 420, 920, color='red', max_w=520, l1=words(33, 34), glow=True, behind=False,
     pin=0.5)
OVERLAY.append(cap(36, 38, y=760, x=470))
OVERLAY.append(dict(cap(39, 41, end=C[5] - 0.04, y=760, x=470)))
# shot 5 -- sitting: "achieve the / skin / that they want to be in."
w_, t_ = words(42, 43)
hero(5, 'skin', ws(44), 17.25, 420, 640, size=230, l1=(w_, times_from(t_, C[5] + 0.02)), l1_fill=CHAR,
     l3=words(45, 50), l3_y=980, l3_size=74)
OVERLAY[-1]['x'] = 660
# shot 6 -- ring light: "As their skin is / changing", "through the years,"
w_, t_ = words(51, 54)
hero(6, 'changing', ws(55), 19.24, 760, 720, color='dark', max_w=520, l1=(w_, times_from(t_, C[6] + 0.02)),
     l1_fill=CHAR, l3=words(56, 58), l3_y=900, l3_size=80)
OVERLAY[-1].update(x=470, end=19.62)   # 'through the years,' on her black top, held past the big word
OVERLAY.append(dict(cap(59, 60, y=690, x=760), fill=CHAR))
OVERLAY.append(dict(cap(61, 61, end=C[7] - 0.05, y=690, x=760), fill=CHAR))
# shot 7 -- injecting: "new ways to / correct it", "and to make it"
w_, t_ = words(62, 64)
hero(7, 'correct it', ws(65), 22.38, 660, 1500, color='dark', max_w=700, l1=(w_, times_from(t_, C[7] + 0.02)),
     behind=False, pin=0.5)
OVERLAY.append(dict(cap(67, 70, end=C[8] - 0.03, y=1330, x=720), fill=CHAR))
# shot 8 -- facial handpiece: "flourish."
hero(8, 'flourish.', ws(71), 24.10, 540, 560, color='red', max_w=840, glow=True, behind=False, fast=True, out=0.14)
OVERLAY.append(dict(cap(72, 76, y=720), fill=CHAR))
OVERLAY.append(dict(cap(77, 80, end=C[9] - 0.04, y=720), fill=CHAR))
# shot 9 -- sitting: "is / maintenance"
hero(9, 'maintenance', ws(82), C[10] - 0.12, 470, 440, size=150, l1=words(81, 81), l1_fill=CHAR)
OVERLAY.append(dict(cap(83, 85, end=C[10] - 0.04, y=860, x=380)))
# shot 10 -- injecting close-up: "maintenance is for your / skin health,"
# ('skin' falls 0.38 s before the cut: the big words come in one word early, on 'your', and clear at the cut)
w_, t_ = words(86, 89)
hero(10, 'skin health,', ws(89), C[11] - 0.10, 600, 1450, color='red', max_w=820, l1=(w_, times_from(t_, C[10] + 0.02)),
     glow=True, behind=False, pin=0.5, fast=True, out=0.12)
# shot 11 -- sitting: "not only just the / appearance,", "but definitely"
hero(11, 'appearance,', ws(96), 32.10, 470, 440, size=150, l1=words(92, 95), l1_fill=CHAR)
OVERLAY.append(dict(cap(97, 98, end=C[12] - 0.04, y=860, x=380), fill=CHAR))
# shot 12 -- RF handpiece: "the / health." then the invitation
hero(12, 'health.', ws(100), 33.90, 330, 600, size=200, color='red', glow=True, l1=words(99, 99), l1_fill=CHAR)
OVERLAY.append(dict(cap(101, 105, y=1460, x=520)))
OVERLAY.append(dict(cap(106, 108, y=1460, x=520)))
OVERLAY.append(dict(cap(109, 111, end=C[13] - 0.04, y=1460, x=520)))
# shot 13 -- at work: "skincare journey," ... "I'm definitely eager to / help you."
hero(13, 'skincare journey,', C[13] + 0.03, 38.90, 540, 820, color='red', max_w=880, glow=True, behind=False, pin=0.6)
OVERLAY.append(cap(114, 118, y=980))
hero(13, 'help you.', ws(123), 99.0, 540, 1060, color='red', max_w=820, glow=True, behind=False, pin=0.6,
     l1=words(119, 122))

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
# minimal transitions: the opening push, one whip into the storefront and the brand-red leak
# into 'health.'; the other ten cuts are plain hard cuts (no SFX either: sfx.py follows TRANS)
TRANS = {49: 'zoom', 175: 'whip', 774: 'leak'}
SPAN = {'zoom': (4, 4), 'flash': (3, 4), 'whip': (3, 3), 'whipv': (3, 3), 'punch': (2, 3), 'blur': (4, 4),
        'leak': (5, 5)}

# ------------------------------------------------------------------ plates

_frame_cache = {}


def read_src(fi):
    if fi in _frame_cache:
        return _frame_cache[fi]
    img = cv2.imread(frame_path(fi))[..., ::-1].astype(np.float32) / 255
    img = cv2.GaussianBlur(img, (0, 0), 0.45)
    m = cv2.imread(matte_path(fi), 0).astype(np.float32) / 255
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
    f = E.smooth(E.prog(t, 42.50, NOUT / FPS - 0.02))
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
