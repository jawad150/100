"""'You made it' studio reel - the creator's still (kid = younger self, man = creator) brought to life as a
cinematic 1080x1920 @ 60 fps shot over the original dialogue.

Live-action feel from one image: a 2.5D camera that pushes in on whoever speaks (handheld drift, motion
blur), volumetric spotlight beams with drifting haze and dust, an orange deep-glow rim around the speaker
(masked out of the person), depth of field, anamorphic flares, a teal/warm Netflix-style grade and grain.
Snake captions (Poppins + Gwyner) and the minimal Genjutsu-style end card from the Yaadein reel.

python3 studio.py still <t> [<t> ...]   -> workspace3/work/stills/*.jpg
python3 studio.py render [workers]      -> workspace3/out/studio_reel_60fps.mp4 (with audio)
"""
import functools
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'memories'))
import anim as A  # noqa: E402
import captions as K  # noqa: E402
import comp as C  # noqa: E402
import ending as E  # noqa: E402
import sound as S  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'workspace3'))
WORK, OUT = ROOT + '/work', ROOT + '/out'
FPS = C.FPS
W, H = C.W, C.H
SW, SH = 1125, 2000                 # still (source image) coordinates
BASE = W / SW                       # 0.96: the still fills the frame at zoom 1
D = 1.0                             # cold open before the dialogue starts
T_END = 29.9                        # end card starts
DUR = T_END + E.END
NF = int(round(DUR * FPS))
ORANGE = np.float32([1.0, 0.33, 0.03])
WARM = np.float32([1.0, 0.78, 0.55])
LIGHTS = ((233, 352), (804, 352))   # the two ceiling spotlights (still px)

# ------------------------------------------------------------------ dialogue (reference times, s)
LINES = [
    ('kid', [('Are', 0.02), ('you', 0.12), ('*tired?', 0.28)]),
    ('man', [('*No.', 5.30)]),
    ('kid', [('You', 8.72), ('*made', 8.96), ('it.', 9.28)]),
    ('man', [('*Working', 10.32), ('on', 10.66), ('it?', 10.86)]),
    ('kid', [('No,', 11.40), ('you', 11.74), ('*made', 12.06), ('it.', 12.50)]),
    ('kid', [('I', 13.62), ('*knew', 13.78), ('you', 14.06), ('would.', 14.28)]),
    ('man', [('I', 17.42), ('think', 17.74), ('about', 18.00), ('you', 18.30), ('*often.', 18.56)]),
    ('kid', [('I', 19.98), ('think', 20.22), ('about', 20.44), ('you', 20.72), ('*everyday.', 20.94)]),
    ('man', [('Am', 23.28), ('I', 23.60), ('what', 23.76), ('you', 23.88), ('*expected?', 23.98)]),
    ('kid', [('*No.', 25.45)]),
    ('kid', [("You're", 27.48), ('*better.', 27.82)]),
]
LINE_END = [0.54, 5.64, 9.52, 11.0, 12.72, 14.42, 19.40, 21.54, 24.32, 25.82, 28.14]

# end card punch line
E.HEADLINE = (('WOULD YOUR', 80, False), ('YOUNGER SELF', 80, False), ('BE PROUD?', 100, True))


# ------------------------------------------------------------------ assets
@functools.lru_cache(maxsize=1)
def plates():
    """Linear plates of the 4x Real-ESRGAN still: level 1 (1125x2000) and level 2 (2250x4000)."""
    im = cv2.imread(ROOT + '/assets/still_x4.png', cv2.IMREAD_UNCHANGED)[..., ::-1].astype(np.float32) / 65535
    l2 = cv2.resize(im, (SW * 2, SH * 2), interpolation=cv2.INTER_AREA)
    l1 = cv2.resize(im, (SW, SH), interpolation=cv2.INTER_AREA)
    return np.ascontiguousarray(C.to_lin(l1)), np.ascontiguousarray(C.to_lin(l2))


@functools.lru_cache(maxsize=1)
def masks():
    out = {}
    for k in ('kid', 'man'):
        m = cv2.imread(ROOT + f'/assets/mask_{k}.png', 0).astype(np.float32) / 255
        out[k] = cv2.resize(m, (SW * 2, SH * 2), interpolation=cv2.INTER_CUBIC).clip(0, 1)
    return out


@functools.lru_cache(maxsize=1)
def avatar():
    """The creator's head and shoulders from the (4x) still, for the end-card ring and badge."""
    im = cv2.imread(ROOT + '/assets/still_x4.png', cv2.IMREAD_UNCHANGED)[..., ::-1].astype(np.float32) / 65535
    cx, cy, side = 838 * 4, 922 * 4, 236 * 4
    sub = im[cy - side // 2:cy + side // 2, cx - side // 2:cx + side // 2]
    sub = cv2.resize(sub, (512, 512), interpolation=cv2.INTER_AREA)
    sub = np.clip((sub - 0.02) * 1.12, 0, 1)                    # lift the face out of the dark studio
    return np.ascontiguousarray(C.to_lin(sub))


E.avatar = avatar


# ------------------------------------------------------------------ camera
# framings: (centre x, centre y, zoom) in still px
WIDE_HI = (562, 930, 1.13)
WIDE = (562, 1010, 1.04)
TWO = (560, 1120, 1.32)
KID = (300, 1150, 1.95)
KID_T = (296, 1120, 2.35)
MAN = (790, 1060, 1.75)
MAN_T = (800, 980, 2.15)


CAM_KEYS = [                       # output time (s), framing, ease into the next key
    (0.0, WIDE_HI, A.SMOOTH), (1.05, WIDE, A.SMOOTH), (1.6, WIDE, A.EXPO),
    (4.2, (KID[0], KID[1], 1.75), A.SMOOTH), (5.9, (KID[0] - 4, KID[1], 1.82), A.EXPO),       # "Are you tired?"
    (6.55, MAN, A.SMOOTH), (8.6, (MAN[0], MAN[1] + 10, 1.84), A.EXPO),                         # "No."
    (9.4, KID, A.SMOOTH), (10.9, (KID[0], KID[1] - 10, 2.05), A.EXPO),                         # "You made it."
    (11.45, MAN, A.SMOOTH), (12.05, (MAN[0], MAN[1], 1.8), A.EXPO),                            # "Working on it?"
    (12.55, KID, A.SMOOTH), (15.6, KID_T, A.EXPO),                                             # "No, you made it. I knew..."
    (17.4, TWO, A.SMOOTH), (17.6, TWO, A.EXPO),
    (18.35, MAN, A.SMOOTH), (20.6, (MAN[0], MAN[1] - 20, 2.0), A.EXPO),                        # "I think about you often."
    (21.2, KID, A.SMOOTH), (22.9, (KID[0], KID[1] - 15, 2.15), A.EXPO),                        # "...everyday."
    (24.05, MAN_T, A.SMOOTH), (25.9, (MAN_T[0], MAN_T[1] - 10, 2.3), A.EXPO),                  # "Am I what you expected?"
    (26.4, KID_T, A.SMOOTH), (28.0, (KID_T[0], KID_T[1] - 10, 2.55), A.SMOOTH),                # "No." ... "You're better."
    (29.2, (KID_T[0], KID_T[1] - 12, 2.62), A.EXPO), (T_END + 0.05, TWO, A.SMOOTH),
]
CAM = A.Track([(t, f, e) for t, f, e in CAM_KEYS])


def clamp_view(cx, cy, z, margin=1.045):
    hw, hh = SW / (2 * z * margin), SH / (2 * z * margin)
    return min(max(cx, hw), SW - hw), min(max(cy, hh), SH - hh)


def camera(t):
    """(cx, cy, zoom, roll) in still px, with operator handheld + breathing push."""
    cx, cy, z = CAM(t)
    amp = 0.6 + 0.5 * A.clamp((z - 1.0) / 1.2)
    cx += amp * (7 * A.wiggle(t, 0.33, 1, 11) + 1.3 * A.wiggle(t, 3.1, 1, 12)) / z
    cy += amp * (6 * A.wiggle(t, 0.29, 1, 13) + 1.1 * A.wiggle(t, 2.7, 1, 14)) / z
    roll = amp * 0.32 * A.wiggle(t, 0.22, 1, 15)
    z *= 1.0 + 0.004 * math.sin(t * 0.9)
    cx, cy = clamp_view(cx, cy, z)
    return cx, cy, z, roll


def cam_matrix(cam, src_scale=1.0):
    """2x3 affine: source px (still px * src_scale) -> output px."""
    cx, cy, z, roll = cam
    s = BASE * z / src_scale
    r = math.radians(roll)
    c, sn = math.cos(r) * s, math.sin(r) * s
    tx, ty = cx * src_scale, cy * src_scale
    return np.float32([[c, -sn, W / 2 - (c * tx - sn * ty)], [sn, c, H / 2 - (sn * tx + c * ty)]])


def to_screen(cam, x, y):
    M = cam_matrix(cam)
    return M[0, 0] * x + M[0, 1] * y + M[0, 2], M[1, 0] * x + M[1, 1] * y + M[1, 2]


def cam_speed(t):
    a, b = camera(t - 0.01), camera(t + 0.01)
    return math.hypot(*np.subtract(to_screen(b, 562, 1100), to_screen(a, 562, 1100))) / 0.02 + abs(b[2] - a[2]) / 0.02 * 400


# ------------------------------------------------------------------ speaking activity
SPANS = [(sp, ws[0][1] + D, LINE_END[i] + D) for i, (sp, ws) in enumerate(LINES)]


def activity(who, t):
    v = 0.0
    for sp, a, b in SPANS:
        if sp == who:
            v = max(v, A.ramp(t, a - 0.25, a + 0.15, A.SMOOTH) * (1 - A.ramp(t, b + 0.35, b + 1.3, A.SMOOTH)))
    return v


@functools.lru_cache(maxsize=1)
def voice_env():
    """Speech envelope of the reference (60 Hz), for the rim-glow pulse."""
    p = ROOT + '/work/ref48.wav'
    from scipy.io import wavfile
    sr, x = wavfile.read(p)
    x = x.astype(np.float32).mean(1) / 32768
    x = S.bp(x, 300, 3400)
    hop = sr // FPS
    e = np.sqrt(np.convolve(x ** 2, np.ones(hop * 4) / (hop * 4), 'same')[::hop])
    e = np.clip((e - np.percentile(e, 40)) / (np.percentile(e, 99) - np.percentile(e, 40) + 1e-9), 0, 1)
    return e


def voice(t):
    e = voice_env()
    i = int((t - D) * FPS)
    return float(e[i]) if 0 <= i < len(e) else 0.0


# ------------------------------------------------------------------ lights, haze, dust
def light_level(i, t):
    """Cold open: the spotlights clunk on (with a flicker), then breathe a little."""
    on = (0.18, 0.52)[i]
    if t < on:
        return 0.0
    u = t - on
    if u < 0.16:
        k = (1.0, 0.25, 0.9, 0.15)[min(3, int(u / 0.04))]
    else:
        k = 1.0
    return k * (1 + 0.018 * A.wiggle(t, 1.7, 1, 30 + i) + 0.01 * math.sin(t * 47 + i))


@functools.lru_cache(maxsize=1)
def _qgrid():
    yy, xx = np.mgrid[0:SH // 4, 0:SW // 4].astype(np.float32)
    return xx * 4 + 2, yy * 4 + 2


@functools.lru_cache(maxsize=1)
def cones():
    """Soft spotlight cones (quarter-res still grid), one per light."""
    xx, yy = _qgrid()
    out = []
    for (lx, ly), (fx, fy) in zip(LIGHTS, ((300, 1480), (760, 1480))):
        ax, ay = fx - lx, fy - ly
        L = math.hypot(ax, ay)
        ax, ay = ax / L, ay / L
        dx, dy = xx - lx, yy - ly
        along = dx * ax + dy * ay
        perp = np.abs(dx * ay - dy * ax)
        width = 30 + along * math.tan(math.radians(15))
        c = np.exp(-(perp / np.maximum(width, 1)) ** 2 * 1.6) * (along > 0)
        c *= np.clip(along / 120, 0, 1) * np.exp(-np.clip(along - 900, 0, None) / 400)
        out.append(c.astype(np.float32))
    return out


@functools.lru_cache(maxsize=1)
def noise_tex():
    rng = np.random.default_rng(3)
    acc = np.zeros((SH // 4, SW // 4), np.float32)
    for sig, a in ((22, 1.0), (9, 0.55), (4, 0.3)):
        n = rng.standard_normal((SH // 4, SW // 4)).astype(np.float32)
        acc += cv2.GaussianBlur(n, (0, 0), sig, borderType=cv2.BORDER_REFLECT) * a * sig
    acc = (acc - acc.mean()) / acc.std()
    return acc


def haze(t):
    """Drifting smoke texture (quarter-res still grid)."""
    n = noise_tex()
    h, w = n.shape
    M1 = np.float32([[1, 0, -t * 3.0], [0, 1, t * 0.8]])
    M2 = np.float32([[1.3, 0, t * 2.1 - 40], [0, 1.3, -t * 1.6 - 60]])
    a = cv2.warpAffine(n, M1, (w, h), borderMode=cv2.BORDER_REFLECT)
    b = cv2.warpAffine(n, M2, (w, h), borderMode=cv2.BORDER_REFLECT)
    return np.clip(0.55 + 0.32 * a + 0.22 * b, 0, 1.6)


def volumetrics(cv, cam, t):
    """Beams + room haze, rendered on the still grid and projected through the camera."""
    hz = haze(t)
    xx, yy = _qgrid()
    c1, c2 = cones()
    l1, l2 = light_level(0, t), light_level(1, t)
    room = np.clip((yy - 600) / 900, 0, 1) * 0.35 + 0.15
    q = (c1 * l1 + c2 * l2) * hz * 1.0 + room * hz * 0.18 * max(l1, l2)
    M = cam_matrix(cam, 0.25)
    vol = cv2.warpAffine(q, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    cv += vol[..., None] * C.to_lin(WARM) * 0.055


@functools.lru_cache(maxsize=1)
def dust():
    rng = np.random.default_rng(9)
    n = 700
    return dict(x=rng.uniform(-50, SW + 50, n), y=rng.uniform(250, 1750, n), k=rng.uniform(0.85, 1.12, n),
                vx=rng.normal(0, 3, n), vy=rng.normal(-1.5, 3.5, n), ph=rng.uniform(0, 6.28, n),
                r=rng.uniform(0.6, 1.8, n), b=rng.uniform(0.4, 1.0, n))


@functools.lru_cache(maxsize=1)
def bokeh():
    rng = np.random.default_rng(21)
    n = 26
    return dict(x=rng.uniform(-100, SW + 100, n), y=rng.uniform(300, 1900, n), k=rng.uniform(1.25, 1.7, n),
                vx=rng.normal(0, 4, n), vy=rng.normal(-2, 3, n), ph=rng.uniform(0, 6.28, n),
                r=rng.uniform(10, 26, n), b=rng.uniform(0.25, 0.7, n))


def _particles(cam, P, t, layer_sharp):
    cx, cy, z, roll = cam
    x = (P['x'] + P['vx'] * t + 14 * np.sin(t * 0.35 + P['ph'])) % (SW + 200) - 100
    y = (P['y'] + P['vy'] * t + 10 * np.sin(t * 0.27 + P['ph'] * 1.7) - 250) % 1500 + 250
    # depth: k > 1 sits closer to the lens -> moves and scales more with the camera
    k = P['k']
    s = BASE * z * k
    X = (x - cx) * s + W / 2
    Y = (y - cy) * s + H / 2
    xi, yi = np.clip((x / 4).astype(int), 0, SW // 4 - 1), np.clip((y / 4).astype(int), 0, SH // 4 - 1)
    c1, c2 = cones()
    lit = 0.12 + c1[yi, xi] * light_level(0, t) + c2[yi, xi] * light_level(1, t)
    tw = 0.65 + 0.35 * np.sin(t * 2.3 + P['ph'] * 3)
    return X, Y, P['r'] * s, P['b'] * lit * tw


def draw_dust(cv, cam, t):
    X, Y, R, B = _particles(cam, dust(), t, True)
    ov = np.zeros((H // 2, W // 2), np.float32)
    for x, y, r, b in zip(X, Y, R, B):
        if -20 < x < W + 20 and -20 < y < H + 20 and b > 0.02:
            cv2.circle(ov, (int(x * 4), int(y * 4)), max(1, int(r * 4 * 0.6)), float(b), -1, cv2.LINE_AA, shift=3)
    ov = cv2.GaussianBlur(ov, (0, 0), 0.8)
    cv += cv2.resize(ov, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] * C.to_lin(WARM) * 0.9
    # out-of-focus foreground bokeh
    X, Y, R, B = _particles(cam, bokeh(), t, False)
    ov = np.zeros((H // 4, W // 4), np.float32)
    for x, y, r, b in zip(X, Y, R, B):
        if -60 < x < W + 60 and -60 < y < H + 60:
            cv2.circle(ov, (int(x * 2), int(y * 2)), max(2, int(r * 2)), float(b), -1, cv2.LINE_AA, shift=3)
    ov = cv2.GaussianBlur(ov, (0, 0), 1.6)
    cv += cv2.resize(ov, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] * C.to_lin(np.float32([1.0, 0.7, 0.45])) * 0.10


def light_sources(cv, cam, t):
    """Hot cores on the two ceiling lights, so they flare (anamorphic + deep glow)."""
    for i, (lx, ly) in enumerate(LIGHTS):
        lv = light_level(i, t)
        if lv <= 0:
            continue
        X, Y = to_screen(cam, lx, ly)
        r = 9 * BASE * cam[2]
        x0, y0 = int(X - r * 6), int(Y - r * 6)
        x1, y1 = int(X + r * 6), int(Y + r * 6)
        if x1 < 0 or y1 < 0 or x0 >= W or y0 >= H:
            continue
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
        g = np.exp(-((xx - X) ** 2 + (yy - Y) ** 2) / (2 * r * r))
        cv[Y0:Y1, X0:X1] += g[..., None] * np.float32([1.0, 0.85, 0.65]) * 2.6 * lv


# ------------------------------------------------------------------ the shot
@functools.lru_cache(maxsize=1)
def _illum_w():
    xx, yy = _qgrid()
    wl = 1 / (1 + np.exp((xx - 560) / 140))
    return wl.astype(np.float32)


def plate(cam, t):
    l1p, l2p = plates()
    z = cam[2]
    src, sc = (l2p, 2.0) if z * BASE > 1.2 else (l1p, 1.0)
    M = cam_matrix(cam, sc)
    cv = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC if sc == 2.0 else cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REFLECT)
    # cold open: the room is dark until each spotlight comes on
    if t < 1.2:
        wl = _illum_w()
        il = 0.07 + 0.93 * (wl * light_level(0, t) + (1 - wl) * light_level(1, t))
        cv *= cv2.warpAffine(il, cam_matrix(cam, 0.25), (W, H), borderMode=cv2.BORDER_REFLECT)[..., None]
    return cv, M, sc


def person_masks(cam):
    M = cam_matrix(cam, 2.0)
    return {k: cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0) for k, m in masks().items()}


def dof(cv, pm, cam, focus):
    """Shallow depth of field on push-ins: everything but the people softens (more far from the feet line)."""
    z = cam[2]
    k = A.clamp((z - 1.3) / 0.8)
    if k <= 0.02:
        return cv
    people = np.maximum(pm['kid'], pm['man'])
    keep = cv2.GaussianBlur(cv2.dilate(people, np.ones((5, 5), np.uint8)), (0, 0), 3)
    _, Yf = to_screen(cam, 560, 1420)
    yy = np.arange(H, dtype=np.float32)[:, None]
    depthw = np.clip(np.abs(yy - Yf) / (380 * BASE * z), 0.25, 1.0)
    q = cv2.resize(cv, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(q, (0, 0), 2.6 * k + 0.4), (W, H), interpolation=cv2.INTER_LINEAR)
    w = ((1 - keep) * depthw * min(1.0, k * 1.3))[..., None]
    return cv * (1 - w) + bl * w


def rim(cv, pm, cam, t):
    """Orange deep glow on the speaker's silhouette edge, masked out of the person (+ a thin inner rim)."""
    z = cam[2]
    for who in ('kid', 'man'):
        a = activity(who, t)
        if t > T_END - 1.5:
            a = max(a, 0.55 * A.ramp(t, T_END - 1.3, T_END - 0.4))
        if a <= 0.01:
            continue
        m = pm[who]
        if m.max() < 0.05:
            continue
        k = a * (0.8 + 0.45 * voice(t))
        ys, xs = np.where(m > 0.05)
        pad = int(90 * z)
        x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad)
        y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad)
        mm = m[y0:y1, x0:x1]
        er = max(1, int(round(1.2 * z)))
        edge = np.clip(mm - cv2.erode(mm, np.ones((2 * er + 1, 2 * er + 1), np.uint8)), 0, 1)
        q = cv2.resize(mm, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        glow = np.zeros_like(q)
        for sig, w in ((1.2, 0.9), (3.5, 0.55), (9.0, 0.3), (22.0, 0.15)):
            glow += cv2.GaussianBlur(q, (0, 0), sig * (0.6 + 0.4 * z)) * w
        glow = cv2.resize(glow, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
        outer = glow * (1 - mm)                                   # masked out of the person
        reg = cv[y0:y1, x0:x1]
        reg += outer[..., None] * C.to_lin(ORANGE) * 0.5 * k
        reg += edge[..., None] * C.to_lin(np.float32([1.0, 0.55, 0.2])) * 1.2 * k
    return cv


def story(t):
    cam = camera(t)
    cv, M, sc = plate(cam, t)
    pm = person_masks(cam)
    cv = dof(cv, pm, cam, None)
    volumetrics(cv, cam, t)
    light_sources(cv, cam, t)
    rim(cv, pm, cam, t)
    draw_dust(cv, cam, t)
    return cv


# ------------------------------------------------------------------ captions
def _head_screen(who, t):
    cam = CAM(t)
    hx, hy = (252, 1035) if who == 'kid' else (838, 862)
    cx, cy = clamp_view(cam[0], cam[1], cam[2])
    s = BASE * cam[2]
    return (hx - cx) * s + W / 2, (hy - cy) * s + H / 2


def phrases():
    out = []
    starts = [ws[0][1] + D for _, ws in LINES]
    for i, (who, ws) in enumerate(LINES):
        words = [(w.lstrip('*'), tt + D, w.startswith('*')) for w, tt in ws]
        t_settle = starts[i] + 0.5
        hx, hy = _head_screen(who, t_settle)
        y = float(np.clip(hy - 230, 300, 1300))
        n = len(ws)
        half = 200 if n == 1 else 330
        x0, x1 = hx - half, hx + half
        if x0 < 90:
            x0, x1 = 90, 90 + 2 * half
        if x1 > 940:
            x0, x1 = 940 - 2 * half, 940
        amp = 34 if n > 1 else 18
        path = K.Path(K.bezier([(x0, y + 8), (x0 + (x1 - x0) * 0.3, y - amp), (x0 + (x1 - x0) * 0.62, y + amp), (x1, y - 6)]))
        nxt = starts[i + 1] - 0.12 if i + 1 < len(LINES) else T_END - 0.3
        t_out = max(LINE_END[i] + D + 0.1, min(nxt - 0.63, LINE_END[i] + D + 1.5))   # gone before the next enters
        out.append(K.Phrase(words, path, t_out, scale=1.25 if n == 1 else 1.0))
    return out


PH = None


def draw_captions(cv, t):
    global PH
    if PH is None:
        PH = phrases()
    for p in PH:
        p.draw(cv, t)


# ------------------------------------------------------------------ frame
def draw(t):
    if t >= T_END:
        u = t - T_END
        prev = None
        if u < 1.0:
            prev = story_graded_lin(t)
        cv = np.zeros((H, W, 3), np.float32)
        return E.draw(cv, u, prev)
    cv = story(t)
    draw_captions(cv, t)
    return cv


def story_graded_lin(t):
    """Finished story frame brought back to linear so the end card's grade reproduces it inside the ring."""
    s = finish_story(story(t), t, grain_on=False)
    lin = C.to_lin(s)
    return lin / np.maximum(1 - 0.22 * lin, 0.2)          # undo the end-card tonemap


def netflix(img, exposure=0.0):
    """Linear -> display: filmic shoulder, teal shadows, warm skin/highlights, soft-crushed blacks."""
    x = img * (2 ** exposure)
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14              # ACES-ish (Narkowicz)
    x = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    s = C.to_srgb(x)
    lum = (s @ np.float32([0.2126, 0.7152, 0.0722]))[..., None]
    sh = np.clip(1 - lum / 0.45, 0, 1) ** 1.5
    hl = np.clip((lum - 0.4) / 0.6, 0, 1)
    s = s + sh * np.float32([-0.030, 0.014, 0.040]) + hl * np.float32([0.050, 0.012, -0.035])
    # warm/orange hues a touch richer, the rest pulled toward teal-grey
    sat = s.max(2, keepdims=True) - s.min(2, keepdims=True)
    warm = np.clip((s[..., :1] - s[..., 2:3]) * 4, 0, 1)
    s = lum + (s - lum) * (0.92 + 0.22 * warm)
    s = np.clip((s - 0.018) / 0.982, 0, 1)
    s = 0.012 + s * 0.988                                     # milky floor (Netflix soft black)
    s = s * s * (3 - 2 * s) * 0.32 + s * 0.68                 # S-curve
    del sat
    return np.clip(s, 0, 1)


@functools.lru_cache(maxsize=1)
def _vig():
    yy, xx = np.mgrid[:H, :W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2 * 0.7)
    return np.clip(1 - 0.75 * np.clip(r - 0.4, 0, None) ** 1.7, 0, 1).astype(np.float32)[..., None]


def finish_story(f, t, grain_on=True):
    cam = camera(min(t, T_END))
    for i, (lx, ly) in enumerate(LIGHTS):
        X, Y = to_screen(cam, lx, ly)
        if -200 < X < W + 200 and -300 < Y < H:
            f = C.god_rays(f, (X, Y), 0.12 * light_level(i, t), threshold=0.55, length=0.3)
    f = C.deep_glow(f, 0.55, 0.42, (1.0, 0.62, 0.45))
    f = C.halation(f, 0.14)
    f = C.anamorphic(f, 1.1, 0.07, (0.45, 0.65, 1.0), 0.3)
    f = C.chroma_fringe(f, 1.2)
    # "You're better": warm light swells in
    sw = A.ramp(t, 27.5 + D, 28.6 + D, A.SMOOTH)
    if sw > 0:
        f = f * (1 + 0.12 * sw) + C.to_lin(np.float32([1.0, 0.55, 0.25])) * 0.012 * sw
    s = netflix(f, -0.05) * _vig()
    if grain_on:
        s = C.grain(s, t, 0.02)
    return s


def finish_frame(f, t):
    if t >= T_END:
        f = C.deep_glow(f, 0.7, 0.45, (1.0, 0.7, 0.5))
        f = C.halation(f, 0.16)
        s = C.grade(f, 'orange', vignette=0.45)
        return C.grain(s, t, 0.016)
    return finish_story(f, t)


def samples_for(t):
    if t >= T_END:
        return 3 if t - T_END < 2.2 else 2
    v = cam_speed(t)
    return 6 if v > 900 else 4 if v > 250 else 2


def render_frame(i):
    t = i / FPS
    f = C.render_frame(draw, t, samples_for(t))
    return finish_frame(f, t)


# ------------------------------------------------------------------ output
def still(ts):
    os.makedirs(WORK + '/stills', exist_ok=True)
    for t in ts:
        s = render_frame(int(round(t * FPS)))
        cv2.imwrite(f'{WORK}/stills/t{t:06.2f}.jpg', (s[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])


def _chunk(args):
    ci, i0, i1 = args
    path = f'{WORK}/chunks/c{ci:03d}.mp4'
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                          '-x264-params', 'rc-lookahead=8:sync-lookahead=0', '-threads', '2', '-pix_fmt', 'yuv420p',
                          path + '.part.mp4'], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        s = render_frame(i)
        p.stdin.write((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    os.replace(path + '.part.mp4', path)
    return path


def render(workers=4, chunk=60):
    os.makedirs(WORK + '/chunks', exist_ok=True)
    jobs = [(ci, i0, min(NF, i0 + chunk)) for ci, i0 in enumerate(range(0, NF, chunk))]
    with Pool(workers) as pool:
        paths = list(pool.imap_unordered(_chunk, jobs))
    paths.sort()
    lst = WORK + '/chunks/list.txt'
    with open(lst, 'w') as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    os.makedirs(OUT, exist_ok=True)
    video = WORK + '/video_60.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    return video


# ------------------------------------------------------------------ sound
QUIET = [(0.62, 4.95), (5.75, 8.35), (21.6, 22.95), (28.25, 29.6)]     # reference spans without dialogue


def ref_audio():
    from scipy.io import wavfile
    sr, x = wavfile.read(ROOT + '/work/ref48.wav')
    return x.astype(np.float64) / 32768


def music_bed(x, dur):
    """Reference track delayed by D, continued under the end card by jumping back into dialogue-free
    spans whose sound best matches where it is (spectral cosine), with equal-power crossfades."""
    SR = S.SR
    n = int(dur * SR)
    out = np.zeros((n, 2))
    i0 = int(D * SR)
    m = min(len(x), n - i0)
    out[i0:i0 + m] = x[:m]
    Sx, fps = S._spec(x)
    win = 0.8
    t_src = len(x) / SR - 0.15                      # leave the last breath of the file
    t_out = t_src + D
    xf = int(0.35 * SR)
    used = []
    while t_out < dur:
        ref = Sx[:, int((t_src - win) * fps):int(t_src * fps)]
        best, bp = -1, None
        for a, b in QUIET:
            if (a, b) in used[-1:]:
                continue
            for p in np.arange(a + win, b - 1.5, 1 / fps):
                cand = Sx[:, int((p - win) * fps):int((p - win) * fps) + ref.shape[1]]
                if cand.shape != ref.shape:
                    continue
                c = float(np.sum(cand * ref) / (np.linalg.norm(cand) * np.linalg.norm(ref) + 1e-9))
                if c > best:
                    best, bp, span = c, (p, b), (a, b)
        p, b = bp
        used.append(span)
        print(f'music: {t_out:.2f}s continues from {p:.2f}s (similarity {best:.3f})')
        seg = x[int(p * SR) - xf:int((b - 0.05) * SR)]
        j = int(t_out * SR) - xf
        L = min(len(seg), n - j)
        if L <= 2 * xf:
            break
        r = np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
        out[j:j + xf] = out[j:j + xf] * np.cos(np.linspace(0, np.pi / 2, xf))[:, None] + seg[:xf] * r
        out[j + xf:j + L] = seg[xf:L]
        out[j + L:] = 0
        t_out = (j + L) / SR
        t_src = b - 0.05
    a, b = int((dur - 1.6) * SR), n
    g = np.ones(n)
    g[a:b] = np.cos(np.linspace(0, np.pi / 2, b - a)) ** 2
    return out * g[:, None]


def cues():
    c = []

    def add(t, kind, g, **kw):
        c.append((t, kind, g, kw))
    add(0.0, 'wind', 0.18, d=2.6)
    add(0.18, 'impact', 0.55, pan=-0.4)
    add(0.18, 'click', 0.5, pan=-0.4)
    add(0.52, 'impact', 0.6, pan=0.4)
    add(0.52, 'click', 0.5, pan=0.4)
    add(0.55, 'sub_drop', 0.45)
    for t0, pan in ((5.95, 0.4), (9.0, -0.4), (11.05, 0.4), (12.15, -0.4), (17.65, 0.4), (20.65, -0.4),
                    (23.45, 0.4), (25.95, -0.4)):
        add(t0, 'whoosh', 0.16, d=0.6, sweep=(-pan, pan), peak=0.5)
    add(15.7, 'whoosh_slow', 0.18)
    add(24.7, 'heartbeat', 0.5, n=3, bpm=62)
    add(26.75, 'riser', 0.22, d=1.6)
    add(28.5, 'shimmer', 0.32)
    add(28.5, 'sub_drop', 0.35)
    add(T_END - 0.05, 'reverse_swell', 0.35)
    add(T_END + E.T_EXPAND - 0.05, 'whoosh', 0.7, d=0.9, sweep=(-0.4, 0.4))
    add(T_END + E.T_BURN, 'reverse_swell', 0.5)
    add(T_END + E.T_GRAD, 'impact', 0.45)
    add(T_END + E.T_AVATAR + 0.02, 'pop', 0.5)
    add(T_END + E.T_USER, 'ticks', 0.4, n=10, gap=0.045)
    add(T_END + E.T_Q, 'whoosh', 0.35, d=0.6)
    add(T_END + E.T_CTA2, 'pop', 0.35)
    add(T_END + E.T_CLICK, 'click', 0.5)
    return c


def build_audio():
    SR = S.SR
    bus = S.Bus(DUR)
    for t0, kind, g, kw in cues():
        kw = dict(kw)
        pan = kw.pop('pan', 0.0)
        bus.add(t0, S.VOICES[kind](**kw), g, pan)
    x = ref_audio()
    music = music_bed(x, DUR)
    env = S.lp(np.abs(music.mean(1)), 8, 1)
    vo = np.zeros(bus.N)
    for sp, a, b in SPANS:
        vo[int((a - 0.1) * SR):int((b + 0.2) * SR)] = 1
    duck = 1 - 0.55 * S.lp(vo, 4, 1)
    fx = bus.x / (np.abs(bus.x).max() + 1e-9) * 0.7 * duck[:, None]
    fenv = S.lp(np.abs(fx).mean(1), 12, 1)
    side = 1 - 0.3 * np.clip(fenv / (np.percentile(fenv, 99.5) + 1e-9), 0, 1) * (1 - vo)
    mix = music * side[:, None] + fx
    del env
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = S.norm(mix, 0.97)
    os.makedirs(OUT, exist_ok=True)
    from scipy.io import wavfile
    wavfile.write(WORK + '/audio_raw.wav', SR, (mix * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', WORK + '/audio_raw.wav', '-af', 'loudnorm=I=-13:TP=-1.0:LRA=11',
                    '-ar', str(SR), WORK + '/audio.wav'], check=True)
    return WORK + '/audio.wav'


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'still'
    if cmd == 'still':
        still([float(x) for x in sys.argv[2:]] or [0.5, 2.0, 6.5, 13.0, 19.0, 24.8, 28.9, 30.5, 34.0])
    elif cmd == 'sound':
        print(build_audio())
    elif cmd == 'render':
        print(render(int(sys.argv[2]) if len(sys.argv) > 2 else 4))
