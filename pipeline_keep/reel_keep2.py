"""BMHC "What did you keep?" v2 - smoother: 60 fps, a slow camera push/drift through every scene, a different eased
transition on every cut (iris out of the thumb, spiral clock-wipe, zoom-through, layercut, whip pan, page slide-up,
arrow-shaped wipe into the end card) with motion blur, and keepsakes that pop with overshoot, settle and float.
Same voice, cuts and story as v1 (reel_keep.py).

Usage: python3 reel_keep2.py still 1.0,5.0 | range a b
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import reel_keep as R
from reel_keep import (C2, C3, C4, C5, C6, C7, C8, SL, T_CARD, T_SPOONS, T_NANI, LIFT0, LINE, GATES, kitchen, subtitles)
from frames_keep import (W, H, S, INK, MAG, DARK, GREYT, BARS, paper, token, dotted_ring, thumb_eclipse, tag, paste,
                         text_sprite, logo, aurora, layercut, cover, clamp, prog, e_out, e_inout, e_back, _grid, grain, bw)

FPS = 60
DUR = R.DUR
NF = int(DUR * FPS)
YY, XX = _grid()


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- camera
def cam(c, z=1.0, rot=0.0, dx=0.0, dy=0.0, cx=W / 2, cy=H / 2):
    if abs(z - 1) < 1e-4 and abs(rot) < 1e-3 and abs(dx) < 0.05 and abs(dy) < 0.05:
        return c
    M = cv2.getRotationMatrix2D((cx, cy), rot, z)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# per scene: zoom from/to, rotation from/to (deg), drift x from/to, drift y from/to, camera centre
CAM = [(1.03, 1.10, -0.6, 0.3, 0, 0, 0, -10, LINE),
       (1.03, 1.08, 0.5, -0.4, 12, -12, 0, 0, (560, 900)),
       (1.03, 1.08, -0.5, 0.5, -10, 10, 6, -6, (540, 900)),
       (1.04, 1.10, 0.8, -0.8, 0, 0, 0, 0, (700, 700)),
       (1.03, 1.14, 0.0, -0.5, 0, 0, 0, 0, LINE),
       (1.03, 1.09, -0.6, 0.6, 0, 0, 10, -10, (540, 880)),
       (1.03, 1.07, 0.4, -0.3, 0, 0, -8, 8, (540, 1000)),
       (1.0, 1.04, 0, 0, 0, 0, 0, 0, (540, 900))]


# ---------------------------------------------------------------- animated pieces
@functools.lru_cache(maxsize=64)
def sprite(name, size, mono):
    """Keepsake cut-out with its soft paper shadow baked in (premultiplied RGBA, padded)."""
    spr = token(name, size, 0, mono)
    p = 70
    h, w = spr.shape[:2]
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    sh = cv2.GaussianBlur(np.pad(spr[..., 3], p), (0, 0), 14) * 0.35
    M = np.float32([[1, 0, 12], [0, 1, 20]])
    sh = cv2.warpAffine(sh, M, (w + 2 * p, h + 2 * p))
    out[..., 3] = sh
    a = spr[..., 3:4]
    reg = out[p:p + h, p:p + w]
    reg[..., :3] = spr[..., :3] + reg[..., :3] * (1 - a)
    reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)
    return out


def place2(c, name, cx, cy, size, u, t, rot=0.0, mono=True, a=1.0, slide=(0, 0), spin=10.0, flt=1.0, seed=0, scale=1.0):
    """Pop in with overshoot and a settling spin, then float (bob + sway)."""
    if u <= 0 or a <= 0:
        return c
    k = e_out(clamp(u / 0.7))
    kb = e_back(clamp(u / 0.6), 1.5)
    s = (0.86 + 0.14 * kb) * scale
    r = rot + spin * (1 - k) + flt * 1.3 * math.sin(t * 1.25 + seed)
    x = cx + slide[0] * (1 - k) + flt * 4 * math.sin(t * 0.9 + seed * 1.7)
    y = cy + slide[1] * (1 - k) + flt * 7 * math.sin(t * 1.1 + seed * 2.3)
    spr = sprite(name, int(size), mono)
    h, w = spr.shape[:2]
    D = int(math.hypot(w, h) * max(s, 0.01)) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), r, s)
    M[0, 2] += D / 2 - w / 2
    M[1, 2] += D / 2 - h / 2
    im = cv2.warpAffine(spr, M, (D, D), flags=cv2.INTER_LINEAR)
    return paste(c, im, x, y, a * clamp(u / 0.18))


@functools.lru_cache(maxsize=128)
def tsp(txt, w, size, col):
    return text_sprite(txt, w, size, np.array(col, np.float32))


def type3(c, bold, light, x, y, u, size=92):
    """Title rises into place behind a soft left-to-right sweep (bold line, then the light line)."""
    if u <= 0:
        return c
    for i, (txt, w, sz, col) in enumerate(((bold, 800, size, tuple(DARK)), (light, 400, int(size * 0.62), tuple(GREYT)))):
        ui = u - i * 0.18
        if not txt or ui <= 0:
            continue
        k = e_out(clamp(ui / 0.75))
        s = tsp(txt, w, sz, col)
        sw = s.shape[1]
        edge = k * 1.3 * (sw + 160)
        m = np.clip((edge - np.arange(sw, dtype=np.float32)) / 160, 0, 1)
        paste(c, s * m[None, :, None], x + sw / 2, y + i * size * 0.95 + (1 - k) * 50, clamp(ui / 0.35))
    return c


def photo2(c, img, cx, cy, r, u, t, z=1.0, seed=0):
    """B&W grainy photo in a circle: elastic pop, then a slow Ken Burns push inside."""
    if u <= 0:
        return c
    k = e_back(clamp(u / 0.55), 1.4)
    rr = int(r * k)
    if rr < 4:
        return c
    im = bw(cover(img, 0.5, 0.5, z, 2 * rr, 2 * rr, dx=6 * math.sin(t * 0.7 + seed)), 1.3)
    rng = np.random.default_rng(int(t * 24))
    im = np.clip(im + rng.normal(0, 0.05, (2 * rr, 2 * rr, 1)), 0, 1)
    m = np.zeros((2 * rr * 4, 2 * rr * 4), np.uint8)
    cv2.circle(m, (rr * 4, rr * 4), rr * 4 - 4, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (2 * rr, 2 * rr), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
    return paste(c, np.dstack([im * m, m[..., 0]]).astype(np.float32), cx, cy, clamp(u / 0.15))


def ring_on(c, cx, cy, r, t, t0, spd=1.0):
    """Dotted ring that draws itself on and keeps turning."""
    return dotted_ring(c, cx, cy, r, t * spd, 1.0, frac=e_inout(prog(t, t0, t0 + 0.9)))


def card(c, t, u=1.0, size=1250, cx=600, cy=980, rot=-4.0, spin=0.0, flt=0.35, slide=(0, 0)):
    return place2(c, 'recipe', cx, cy, size, u, t, rot, True, slide=slide, spin=spin, flt=flt, seed=1)


# ---------------------------------------------------------------- scenes
def s_detail(t):
    c = paper().copy()
    card(c, t, u=0.35 + t, spin=-6, slide=(0, 80))
    thumb_eclipse(c, LINE[0], LINE[1], 215, t - 0.15, 0.0)
    tag(c, 'HEART WORK', 64 - 60 * (1 - e_out(clamp(t / 0.5))), 150, MAG, a=clamp(t / 0.25))
    word = tsp('Illustrative story', 500, 24, tuple(GREYT))
    paste(c, word, 64 + word.shape[1] / 2, 205, clamp((t - 0.3) / 0.4))
    type3(c, 'That last line', 'has nothing to do with cooking.', 64, 300, t - SL['o1'] + 0.1, 92)
    return c


def s_who(t):
    c = paper().copy()
    type3(c, '1. Who gave', 'you this?', 64, 260, t - SL['q1'] + 0.05, 92)
    ring_on(c, 560, 900, 330, t, C2 - 0.1)
    dotted_ring(c, 560, 900, 372, -t * 0.6, 1.0, frac=e_inout(prog(t, C2 + 0.3, C2 + 1.3)), n=120, width=2)
    photo2(c, GATES, 560, 900, 300, t - C2 + 0.05, t, 1.0 + 0.05 * prog(t, C2, C3))
    place2(c, 'envelope', 820, 1230, 420, t - T_NANI + 0.15, t, -8, slide=(380, 60), spin=-14, seed=2)
    return c


def s_memory(t):
    c = paper().copy()
    c = aurora(c, t, 0.22 * prog(t, SL['o3'] - 0.5, SL['o3'] + 0.8), 0.04, 0.15)
    type3(c, '2. What do you', 'remember about her?', 64, 260, t - SL['q2'] + 0.05, 92)
    ring_on(c, 540, 900, 330, t, C3 - 0.15)
    dotted_ring(c, 540, 900, 372, -t * 0.6, 1.0, frac=e_inout(prog(t, C3 + 0.2, C3 + 1.2)), n=120, width=2)
    photo2(c, kitchen(), 540, 900, 300, t - C3 + 0.05, t, 1.0 + 0.07 * prog(t, C3, C4), seed=1)
    place2(c, 'cardamom', 300, 1210, 340, t - T_CARD + 0.1, t, 10, mono=False, slide=(-280, 140), spin=40, seed=3)
    return c


def s_spoons(t):
    c = paper().copy()
    k = e_inout(prog(t, C4 - 0.2, C4 + 1.5))
    card(c, t, size=1250 + 450 * k, cx=600 - 220 * k, cy=980 + 80 * k, rot=-4 + 3 * k, flt=0.2)
    for i, r in enumerate((420, 330, 250)):                     # SPIRAL: rings spin and close in on the drawn spoons
        dotted_ring(c, 560 + 120 * k, 700 + 40 * k, r * (1 - 0.55 * k), t * (3 + 2 * i) * (1 if i % 2 else -1), 1.0,
                    frac=e_inout(prog(t, C4 - 0.2 + 0.12 * i, C4 + 0.7 + 0.12 * i)))
    type3(c, 'She never', 'measured anything.', 64, 260, t - SL['o4'] + 0.05, 92)
    ts = t - T_SPOONS + 0.1
    swing = 16 * math.exp(-2.2 * max(0, ts)) * math.sin(8 * max(0, ts))  # the spoon lands and swings like a pendulum
    place2(c, 'spoon', 840, 620, 420, ts, t, 20 + swing, mono=False, slide=(0, -520), spin=0, seed=4)
    return c


def s_line(t):
    c = paper().copy()
    card(c, t, flt=0.25)
    lift = prog(t, LIFT0, LIFT0 + 1.0)
    thumb_eclipse(c, LINE[0], LINE[1], 215, 1.0, lift)
    if lift > 0.5:                                               # the revealed line glows magenta, breathing
        g = np.exp(-(((XX - 470) / 270) ** 2 + ((YY - 975) / 72) ** 2)) * 0.2 * smooth((lift - 0.5) / 0.5) \
            * (0.8 + 0.2 * math.sin(t * 4)) * (1 - prog(t, SL['o5'] + 1.6, C6 + 0.3))
        c[:] = np.clip(c + g[..., None] * MAG, 0, 1)
    type3(c, '3. The line', 'we could only glimpse.', 64, 300, t - C5 - 0.05, 92)
    return c


def s_her(t):
    c = paper().copy()
    ring_on(c, 540, 880, 330, t, C6 - 0.1)
    dotted_ring(c, 540, 880, 372, -t * 0.6, 1.0, frac=e_inout(prog(t, C6 + 0.2, C6 + 1.1)), n=120, width=2)
    place2(c, 'photo', 540, 880, 560, t - C6 + 0.05, t, 6, slide=(0, 320), spin=16, seed=5)
    type3(c, 'That', 'was her.', 64, 300, t - SL['o6'] + 0.1, 120)
    return c


def s_drawer(t):
    c = paper().copy()
    land = C7 + 1.45
    bump = 0.025 * math.exp(-6 * max(0, t - land)) * math.sin(14 * max(0, t - land)) if t > land else 0.0
    place2(c, 'drawer', 540, 1100, 760, t - C7 + 0.15, t, 0, slide=(0, 260), spin=0, flt=0.3, seed=6, scale=1 + bump)
    u = prog(t, C7 + 0.45, land)
    if u < 1:                                                    # the card arcs down into the drawer, turning as it goes
        k = e_inout(u)
        x = 520 + 160 * math.sin(math.pi * k) * (1 - k)
        y = 700 + 400 * k - 120 * math.sin(math.pi * k)
        place2(c, 'recipe', x, y, 380 * (1 - 0.4 * k), 1.0, t, -40 - 30 * k + 25 * math.sin(math.pi * k), flt=0,
               a=1 - smooth((u - 0.82) / 0.18), seed=1)
    type3(c, 'What’s one thing', 'your family has kept?', 64, 300, t - C7 - 0.2, 92)
    return c


def s_end(t):
    c = np.empty((H, W, 3), np.float32)
    c[:] = INK
    u = t - (C8 - 0.3)
    k = e_out(clamp(u / 0.8))
    lg = logo(820)
    if k > 0:
        s = 0.92 + 0.08 * k
        lg2 = cv2.resize(lg, (int(lg.shape[1] * s), int(lg.shape[0] * s)), interpolation=cv2.INTER_AREA)
        paste(c, lg2, 540, 820 + 24 * (1 - k), clamp(u / 0.4))
    hs = tsp('@thebmhc', 700, 46, (0.8, 0.8, 0.8))
    paste(c, hs, 540, 1120 + 20 * (1 - e_out(clamp((u - 0.3) / 0.5))), clamp((u - 0.3) / 0.4))
    for i, col in enumerate(BARS):
        kk = e_inout(clamp((u - 0.1 * i) / 0.5))
        c[H - 22:, int(W * i / 4):int(W * i / 4 + W / 4 * kk)] = col
    return c


SCENES = [(0, s_detail), (C2, s_who), (C3, s_memory), (C4, s_spoons), (C5, s_line), (C6, s_her), (C7, s_drawer), (C8, s_end)]
ENDS = [s[0] for s in SCENES[1:]] + [DUR]


def scene(i, t):
    c = SCENES[i][1](t)
    z0, z1, r0, r1, x0, x1, y0, y1, ctr = CAM[i]
    p = (t - SCENES[i][0]) / (ENDS[i] - SCENES[i][0])
    p = max(-0.3, min(1.3, p))
    return cam(c, z0 + (z1 - z0) * p, r0 + (r1 - r0) * p, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, *ctr)


# ---------------------------------------------------------------- transitions (A = outgoing frame, B = incoming, u 0..1)
def t_iris(A, B, u, cx=LINE[0], cy=LINE[1]):
    """Eclipse iris: the new scene opens out of the thumb's shadow, edged by a dotted ring."""
    k = e_inout(u)
    r = 2300 * k
    A = cam(A, 1 + 0.12 * k, 0, 0, 0, cx, cy)
    m = np.clip((r - np.hypot(XX - cx, YY - cy)) / 24, 0, 1)[..., None]
    out = A * (1 - m) + B * m
    if 0.02 < k < 0.98:
        dotted_ring(out, cx, cy, r + 10, u * 6, 1.0, n=160, width=5)
    return out


def t_clock(A, B, u, cx=550, cy=900):
    """Spiral clock-wipe around the photo circle, both frames turning a little."""
    k = e_inout(u)
    A = cam(A, 1 + 0.04 * k, 8 * k, 0, 0, cx, cy)
    B = cam(B, 1.04 - 0.04 * k, -8 * (1 - k), 0, 0, cx, cy)
    ang = (np.arctan2(XX - cx, -(YY - cy)) / (2 * np.pi)) % 1.0
    m = np.clip((k * 1.15 - ang) / 0.12, 0, 1)[..., None]
    return A * (1 - m) + B * m


def t_zoom(A, B, u, cx=700, cy=700):
    """Zoom-through: the outgoing frame rushes past, the incoming one settles from close up."""
    k = e_inout(u)
    A = cam(A, 1 + 1.2 * k, 0, 0, 0, cx, cy)
    B = cam(B, 1.45 - 0.45 * k, 0, 0, 0, cx, cy)
    a = smooth((u - 0.25) / 0.5)
    return A * (1 - a) + B * a


def t_layer(A, B, u):
    return layercut(A, B, e_inout(u), n=6)


def t_whip(A, B, u):
    """Whip pan to the left with directional blur that peaks mid-move."""
    k = e_inout(u)
    off = int(W * k)
    out = np.empty_like(A)
    out[:, :W - off] = A[:, off:]
    out[:, W - off:] = B[:, :off]
    v = 1 - abs(2 * u - 1)
    L = int(2 + 150 * v ** 1.5)
    return cv2.blur(out, (L, 1)) if L > 2 else out


def t_slide_up(A, B, u):
    """The next page slides up over the last one (parallax: the old page drifts up slower and dims)."""
    k = e_inout(u)
    out = cam(A, 1, 0, 0, -0.28 * H * k) * (1 - 0.35 * k)
    y = int(H * (1 - k))
    if y < H:
        out[y:] = B[:H - y]
        y0 = max(0, y - 80)
        if y > y0:
            out[y0:y] *= (1 - np.linspace(0, 0.35, y - y0, dtype=np.float32))[:, None, None]
    return out


def t_arrow(A, B, u):
    """Arrow-shaped wipe (the reference's black diagonal arrow): everything behind the arrowhead becomes the end card."""
    k = e_inout(u)
    d = np.array((0.6, -1.0))
    d /= np.linalg.norm(d)
    n = np.array((-d[1], d[0]))
    tip = np.array((-500 + 2000 * k, H + 450 - 2500 * k))
    hb = tip - d * 260
    head = [tip, hb + n * 300, hb - n * 300]
    body = [hb + n * 4000, hb - n * 4000, hb - n * 4000 - d * 6000, hb + n * 4000 - d * 6000]
    lay = np.zeros((H, W), np.uint8)
    for poly in (head, body):
        cv2.fillPoly(lay, [(np.array(poly) * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    sh = cv2.GaussianBlur(m, (0, 0), 18)[..., None] * 0.35         # soft shadow ahead of the arrow
    return A * (1 - np.maximum(m, sh)) + B * m


# cut time, transition, seconds before the cut, seconds after
TRANS = [(C2, t_iris, 0.3, 0.45), (C3, t_clock, 0.3, 0.45), (C4, t_zoom, 0.3, 0.4), (C5, t_layer, 0.25, 0.45),
         (C6, t_whip, 0.25, 0.35), (C7, t_slide_up, 0.3, 0.45), (C8, t_arrow, 0.8, 0.2)]


def in_trans(t):
    for j, (ct, fn, pre, post) in enumerate(TRANS):
        if ct - pre <= t < ct + post:
            return j + 1, fn, (t - (ct - pre)) / (pre + post)
    return None


def base(t):
    tr = in_trans(t)
    if tr:
        i, fn, u = tr
        return fn(scene(i - 1, t), scene(i, t), u)
    i = max(j for j, (t0, _) in enumerate(SCENES) if t >= t0)
    return scene(i, t)


def frame(t):
    if in_trans(t):                                              # motion blur through the transitions
        c = sum(base(t + o) for o in (-1 / (4 * FPS), 1 / (4 * FPS))) / 2
    else:
        c = base(t)
    c = subtitles(np.ascontiguousarray(c, np.float32), t)
    c = grain(np.clip(c, 0, 1), 0.012, int(t * 30))
    return np.clip(c * smooth(t / 0.25), 0, 1)


def write(i, c, d):
    cv2.imwrite(f'{d}/{i:05d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        d = f'{S}/stills2'
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[2].split(','):
            write(int(float(ts) * 100), frame(float(ts)), d)
            print('still', ts, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        d = f'{S}/frames2'
        os.makedirs(d, exist_ok=True)
        for i in range(a, min(b, NF)):
            write(i, frame(i / FPS), d)
            if i % 60 == 0:
                print('frame', i, flush=True)
