"""bijli_chali_gayi_world.py - the picture worlds of reel 2, C11 "Bijli Chali Gayi" (motion-timeline-builder's helper).

Imported by bijli_chali_gayi.py as BW. Every shot function is a PURE function of t (render workers draw frames out of
order); static layers are built once per worker in lru_cache'd builders (prewarm()). Geometry, light and strings:
BRIEF.md r2 sections 6.2-6.9 + HANDOFF.md r3 (binding where they differ). f = frame at 30 fps, frame rule
f = floor(30 t + 0.5) (the frame whose shutter holds t: power events snap per frame, never blur across a state).

    room(t, mode)  CAM_ROOM: desk_plate passes + crt / tower / box passes, ceiling fan, bold CRT edit, LED, torch
                   modes 'A' (S1A hook A, lit -> brownout f10-f14 -> torch), 'B' (S1B hook B, torch-lit),
                   'S4' (old room by torch), 'S8a' (power back, plate behind JD), 'lit' (frame-0 clock: S8b + loop tail)
    s2(t)          candle tabletop: match f80, wick f86, pankhi on f100 / f120 / f140, homework copy; tilt f140-f159
    s3(t)          night rooftops (6 planes), far window f220-f221, child's head turn f224-f230, bulbs f240-f245,
                   everything dies f300-f302
    s5(t)          modern desk: glass monitor (the same edit + 9:16 rooftop viewer), HUD 63 -> 64 -> drain -> 0 %
    s6(t)          Ctrl + S keycaps (Ctrl 1 f before S), Saved chips at p + 2, U3F at f712
    s7_macro(t)    candle macro (S7a f720-f739 lean, S7c f840-f879)
    s7b(t)         JD profile by candlelight (BF.cam_s7b world + sparks + BF.draw_s7b)
    s8a(t)         JD smiling over the lit room plate (BF.cam_s8a + BF.draw_s8a)

Camera law (BRIEF 6.9): drift(t) = A(t) * (wiggle 0.35 Hz 7 px, 0.30 Hz 5 px, roll 0.25 Hz 0.5 deg), applied as one
2D warp of the shot (reflect border); locked (no warp at all) while the power is on.
"""
import functools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                   # noqa: F401,E402  FIRST
from jawad_kit import K, T, ui                     # noqa: E402
import jawad_grade                                 # noqa: F401,E402  registers the 'dusk' look (ui cards / chips)
import sprites3d as S3                             # noqa: E402
import bijli_chali_gayi_faces as BF                # noqa: E402

import cv2                                         # noqa: E402
import numpy as np                                 # noqa: E402

RWS = '/home/user/100/workspace/jawad_reels/bijli_chali_gayi'
W, H, FPS = K.W, K.H, K.FPS
HALF = 0.5 / FPS
DUR = 1040 / 30


def lin(h, k=1.0):
    return np.asarray(K.hexlin(h), np.float32) * np.float32(k)


NIGHT_0, NIGHT_1 = lin('#070404'), lin('#170A07')
FLAME, RED, EMBER = lin('#FF6A1A'), lin('#F2312B'), lin('#B3120E')
GOLD, AMBER, SMOKE = lin('#FF9F1C'), lin('#FFB547'), lin('#2A1A15')
IVORY, ASH, INDIGO, WOOD = lin('#FFF3E6'), lin('#A8978C'), lin('#171431'), lin('#3B2A22')
_tc = IVORY * 0.9 + AMBER * 0.25
TORCH = (_tc / _tc.max()).astype(np.float32)               # torch colour (IVORY x0.9 + AMBER x0.25), peak 1
_cc = AMBER * 0.85 + FLAME * 0.15
CANDLE = (_cc / _cc.max()).astype(np.float32)              # candle light colour, peak 1


def F(f):
    return f / FPS


def fi(t):
    """Frame index by the centre rule (the frame whose shutter holds t)."""
    return int(math.floor(t * FPS + 0.5))


def ro(a):
    a.flags.writeable = False
    return a


def ease(name, u):
    return K.EASE[name](min(1.0, max(0.0, u)))


def new(rgb=None):
    cv = np.zeros((H, W, 4), np.float32)
    if rgb is not None:
        cv[..., :3] = rgb
    cv[..., 3] = 1.0
    return cv


def nsamp(t):
    """Base motion-blur samples (BRIEF 7): 5 on f0-f9 (fan), f150-f170 (tilt), f240-f246 (bulbs), f880-f900 (fan
    spin-up), else 3. The reel's samples() takes max(PLAN.samples(t), nsamp(t))."""
    f = int(round(t * FPS))
    if 0 <= f <= 9 or 150 <= f <= 170 or 240 <= f <= 246 or 880 <= f <= 900:
        return 5
    return 3


def warp(cv, dx=0.0, dy=0.0, roll=0.0, scale=1.0, centre=(540.0, 960.0)):
    """The shot camera as one 2D warp (drift translation + roll + push), reflect border. No-op when locked."""
    if abs(dx) < 1e-3 and abs(dy) < 1e-3 and abs(roll) < 1e-4 and abs(scale - 1.0) < 1e-6:
        return cv
    M = cv2.getRotationMatrix2D((float(centre[0]), float(centre[1])), float(roll), float(scale))
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(cv, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def drift(t, amp=1.0):
    """BRIEF 6.9 handheld 'torch operator' drift (dx px, dy px, roll deg) scaled by A(t) = amp."""
    if amp <= 0:
        return 0.0, 0.0, 0.0
    return amp * K.wiggle(t, 0.35, 7.0, 11), amp * K.wiggle(t, 0.30, 5.0, 12), amp * K.wiggle(t, 0.25, 0.5, 13)


def splat(cv, xs, ys, cols, sigma=1.1, q=2):
    """Soft emissive dots: accumulated at 1/q resolution, blurred, upsampled and added. cols (n, 3) linear."""
    if len(xs) == 0:
        return
    h, w = H // q, W // q
    buf = np.zeros((h, w, 3), np.float32)
    xi = (np.asarray(xs, np.float32) / q).astype(np.int32)
    yi = (np.asarray(ys, np.float32) / q).astype(np.int32)
    ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
    if not ok.any():
        return
    np.add.at(buf, (yi[ok], xi[ok]), np.asarray(cols, np.float32)[ok])
    buf = cv2.GaussianBlur(buf, (0, 0), sigma)
    cv[..., :3] += cv2.resize(buf, (W, H), interpolation=cv2.INTER_LINEAR)


def paint(rgb, m, col):
    """rgb = rgb * (1 - m) + col * m (m: coverage (h, w) 0..1; col: (3,) or (h, w, 3))."""
    m3 = m[..., None]
    rgb *= (1.0 - m3)
    rgb += m3 * col


def poly_mask(h, w, polys, ss=4):
    """Anti-aliased coverage (h, w) float32 of the UNION of filled polygons (list of (N, 2) arrays, px); each
    polygon is filled in its own bbox and max-ed in (cv2.fillPoly on several contours is even-odd: overlaps
    would punch holes)."""
    m = np.zeros((h, w), np.float32)
    for p in polys:
        p = np.asarray(p, np.float64)
        x0 = max(0, int(np.floor(p[:, 0].min())) - 2)
        x1 = min(w, int(np.ceil(p[:, 0].max())) + 3)
        y0 = max(0, int(np.floor(p[:, 1].min())) - 2)
        y1 = min(h, int(np.ceil(p[:, 1].max())) + 3)
        if x1 <= x0 or y1 <= y0:
            continue
        tmp = np.zeros((y1 - y0, x1 - x0), np.uint8)
        pts = np.round((p - np.array([x0, y0])) * (1 << ss)).astype(np.int32)
        cv2.fillPoly(tmp, [pts], 255, lineType=cv2.LINE_AA, shift=ss)
        np.maximum(m[y0:y1, x0:x1], tmp.astype(np.float32) * np.float32(1.0 / 255.0), out=m[y0:y1, x0:x1])
    return m


def ellipse_pts(cx, cy, rx, ry, n=48, a0=0.0, a1=360.0):
    a = np.radians(np.linspace(a0, a1, n, endpoint=False))
    return np.c_[cx + rx * np.cos(a), cy + ry * np.sin(a)]


def rim_of(m, dx, dy, width=2.0):
    """Rim band of a silhouette on the side facing direction (dx, dy): pixels inside m whose neighbour `width` px
    toward the light is outside."""
    n = math.hypot(dx, dy) or 1.0
    sx, sy = dx / n * width, dy / n * width
    M = np.float32([[1, 0, -sx], [0, 1, -sy]])
    nb = cv2.warpAffine(m, M, (m.shape[1], m.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return np.clip(m - nb, 0, 1)


def gauss2(h, w, cx, cy, rx, ry):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)).astype(np.float32)


# ================================================================================================ assets
@functools.lru_cache(maxsize=None)
def asset(name):
    return S3.Asset3D(name, 'passes', root=RWS + '/assets3d')


@functools.lru_cache(maxsize=None)
def pass_(name, label):
    return ro(np.array(asset(name).by_label(label), np.float32))


@functools.lru_cache(maxsize=16)
def flame_sprite(height):
    """Procedural candle flame (BRIEF 6.9): teardrop, AMBER x2.6 core, FLAME edge, soft halo. Anchor = the wick at
    (0.5, 0.62) of the sprite. Emissive (alpha 0)."""
    hh = int(height * 3.0)
    ww = max(8, int(height * 2.4))
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    base_y = hh * 0.62
    v = (base_y - yy) / height
    halfw = 0.17 * height * np.maximum(np.sin(np.pi * np.clip(v * 0.92 + 0.08, 0, 1)), 0) ** 0.8 \
        * np.clip(1.25 - v, 0, 1)
    d = np.abs(xx - ww / 2) / np.maximum(halfw, 1e-3)
    inside = np.clip(1.0 - d, 0, 1) * ((v > 0) & (v < 1)).astype(np.float32)
    inside = cv2.GaussianBlur(inside, (0, 0), max(0.6, height * 0.03))
    core = np.clip(inside * 1.6 - 0.45, 0, 1)
    out = np.zeros((hh, ww, 4), np.float32)
    out[..., :3] = inside[..., None] * FLAME * 1.4 + core[..., None] * AMBER * 2.6
    halo = cv2.GaussianBlur(inside, (0, 0), max(1.0, height * 0.35))
    out[..., :3] += halo[..., None] * GOLD * 0.6
    return ro(out)


def candle_flicker(t):
    return BF.candle_flicker(t)


def flame_sway(t, amp=1.0):
    return amp * (K.wiggle(t, 1.5, 3.0, 51) + K.wiggle(t, 4.0, 1.0, 52))


def draw_flame(cv, t, x, y, height, gain=1.0, rot=0.0, sy=1.0):
    """Add the procedural flame (emissive) with its wick at (x, y); gain = brightness, sy = growth (ignition)."""
    K.draw(cv, flame_sprite(int(height)), x, y, scale=(1.0, max(0.02, sy)), rot=rot, opacity=gain,
           anchor=(0.5, 0.62), mode='add')


@functools.lru_cache(maxsize=1)
def led_sprite():
    """The backup box LED (unit white): a 5 px disc with K.glow(sigmas=(4, 12, 30)) so its bloom above luma 90 is
    >= 40 px wide at 1080 (GATE minor 7). Colour and level are applied at draw time."""
    d = K.disc(5, (1.0, 1.0, 1.0))
    return ro(K.glow(d, (1.0, 1.0, 1.0), sigmas=(4, 12, 30), strength=1.0))


@functools.lru_cache(maxsize=4)
def led_col(col_key):
    out = np.array(led_sprite(), np.float32)
    out[..., :3] *= {'A': AMBER, 'F': FLAME}[col_key]
    return ro(out)


# ================================================================================================ CRT edit
TRK = [(40, 88), (98, 146), (156, 204)]
BLK = [[(14, 92, 'F'), (98, 190, 'F'), (196, 250, 'F'), (256, 326, 'F')],
       [(14, 60, 'E'), (66, 170, 'E'), (176, 286, 'E'), (292, 326, 'E')],
       [(14, 120, 'F7'), (126, 214, 'E'), (220, 326, 'F7')]]


@functools.lru_cache(maxsize=4)
def crt_static(width=340, scan=True):
    """BRIEF 6.9 bold CRT edit, 240 px tall x `width` (340 = the glass; stretched for the S5 monitor), without the
    playhead. Returns (image (240, w, 3), multiplier (240, w, 1)): scanlines x0.75 on odd rows + barrel vignette."""
    sx = width / 340.0
    img = np.zeros((240, width, 3), np.float32)
    img[:] = NIGHT_1 * 1.6
    for i, x in enumerate(range(14, 327, 20)):
        X = int(round(x * sx))
        hh = 12 if i % 5 == 0 else 6
        img[30 - hh:30, X:X + 2] = ASH * 0.55
    cols = {'F': FLAME, 'E': EMBER, 'F7': FLAME * 0.7}
    for (y0, y1), row in zip(TRK, BLK):
        img[y0:y1, int(round(14 * sx)):int(round(326 * sx))] = SMOKE * 1.2
        for x0, x1, c in row:
            X0, X1 = int(round(x0 * sx)), int(round(x1 * sx))
            img[y0:y1, X0:X1] = cols[c]
            img[y0:y0 + 3, X0:X1] = cols[c] * 0.5 + AMBER * 0.5
    mul = np.ones((240, width, 1), np.float32)
    if scan:
        mul[1::2] *= 0.75
        yy, xx = np.mgrid[0:240, 0:width].astype(np.float32)
        r2 = ((xx - width / 2) / (width / 2)) ** 2 * 0.5 + ((yy - 120) / 120.0) ** 2 * 0.5
        mul[..., 0] *= 1.0 - 0.30 * r2
    img *= mul
    return ro(img), ro(mul)


def crt_image(t, width=340, scan=True, park=None):
    """The edit at clock t: IVORY playhead 6 px wide + 18 x 16 head, x = 14 + ((136 + 60 t) mod 312) (glass px)."""
    img, mul = crt_static(width, scan)
    img = img.copy()
    sx = width / 340.0
    x = park if park is not None else (14 + ((136 + 60.0 * t) % 312)) * sx
    X = int(round(x))
    a, b = max(0, X - 3), min(width, X + 3)
    img[14:204, a:b] = IVORY * mul[14:204, a:b]
    a, b = max(0, X - 9), min(width, X + 9)
    img[14:30, a:b] = IVORY * mul[14:30, a:b]
    return img


def collapse(img, v=1.0, hs=1.0, gain=1.0, line=False):
    """CRT power-off (BRIEF 6.9): the image squeezed vertically to v (or an 8 px line with an AMBER x1.2 phosphor
    core when line=True), horizontally to hs, brightness x gain, centred."""
    h, w = img.shape[:2]
    out = np.zeros_like(img)
    th = 8 if line else max(1, int(round(h * v)))
    tw = max(2, int(round(w * hs)))
    small = cv2.resize(np.ascontiguousarray(img), (tw, th), interpolation=cv2.INTER_AREA) * np.float32(gain)
    if line:
        small[2:6] += AMBER * 1.2
    y0, x0 = (h - th) // 2, (w - tw) // 2
    out[y0:y0 + th, x0:x0 + tw] = small
    if line:                                     # phosphor halo around the line (f14 floor: >= 2,000 px > luma 90)
        out += cv2.GaussianBlur(out, (0, 0), 5.0) * np.float32(0.9)
    return out


def dot(img_shape, level, r=6.0):
    """The 12 px CRT dot (AMBER x2.5 at level 1) + a small halo, centred in a layer of img_shape."""
    h, w = img_shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2)
    core = np.clip(r + 0.5 - d, 0, 1)
    halo = np.exp(-(d / (r * 2.2)) ** 2) * 0.35
    return ((core + halo)[..., None] * AMBER * np.float32(2.5 * level)).astype(np.float32)


# ================================================================================================ ceiling fan
FAN_PROFILE = [(40, 18), (150, 48), (420, 64), (445, 38)]                # (radius, width) along a blade
FAN_STRIP = 240


def fan_cov(angles, hub=(540.0, 60.0), flat=0.30, y0=0):
    """flat: vertical squash of the blade plane (0.30 = CAM_ROOM; larger when seen from below)."""
    """Blade coverage (FAN_STRIP, W) for a list of blade angles (deg; averaged = the shutter smear) + hub mask."""
    acc = np.zeros((FAN_STRIP, W), np.float32)
    hx, hy = hub[0], hub[1] - y0
    for a0 in angles:
        polys = []
        for b in range(3):
            a = math.radians(a0 + 120 * b)
            pts = []
            for rr, ww in FAN_PROFILE:
                q = a + math.atan2(ww / 2, rr)
                pts.append((hx + rr * math.cos(q), hy + flat * rr * math.sin(q)))
            for rr, ww in reversed(FAN_PROFILE):
                q = a - math.atan2(ww / 2, rr)
                pts.append((hx + rr * math.cos(q), hy + flat * rr * math.sin(q)))
            polys.append(np.array(pts))
        acc += poly_mask(FAN_STRIP, W, polys)
    acc *= np.float32(1.0 / max(1, len(angles)))
    hub_m = poly_mask(FAN_STRIP, W, [ellipse_pts(hx, hy, 36, 36 * 0.55)])
    return acc, hub_m


def fan_angles(t, rev_fn, rate_fn):
    """Blade angles across this sample's slice of the 180-degree shutter (1.5 deg apart): a smooth smear at any
    sample count."""
    n = nsamp(t)
    sl = 0.5 / FPS / n
    dth = 360.0 * abs(rate_fn(t)) * sl
    k = max(1, min(9, int(math.ceil(dth / 1.5))))
    if k == 1:
        return [360.0 * rev_fn(t) + 20.0]
    return [360.0 * rev_fn(t - sl / 2 + (i + 0.5) / k * sl) + 20.0 for i in range(k)]


def draw_fan(cv, angles, m):
    cov, hub_m = fan_cov(angles)
    reg = cv[:FAN_STRIP, :, :3]
    blade = NIGHT_1 + WOOD * 0.12
    edge = np.clip(cov - np.roll(cov, -2, axis=0), 0, 1)              # the blades' lower edge (tube-lit underside)
    paint(reg, cov, blade)
    if m > 0:
        reg += edge[..., None] * AMBER * np.float32(0.10 * m)
    paint(reg, hub_m, NIGHT_1 * 1.4 + WOOD * 0.15)
    cv[0:60, 532:548, :3] = NIGHT_1                                      # down-rod


# ================================================================================================ torch
OPERATOR = (1150.0, 2100.0)


@functools.lru_cache(maxsize=1)
def grid4():
    ys, xs = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    return ro((xs + 0.5) * 4), ro((ys + 0.5) * 4)


def torch_fields(hx, hy, r=230.0):
    """Quarter-res torch fields: I = hotspot (soft ellipse r 230) + 15 % spill ring to 2.2 r; cone = the volumetric
    wedge from the operator (1150, 2100) to the hotspot."""
    X4, Y4 = grid4()
    d2 = ((X4 - hx) / r) ** 2 + ((Y4 - hy) / (0.9 * r)) ** 2
    d = np.sqrt(d2)
    hot = np.exp(-2.2 * d2)
    spill = 0.15 * np.clip(1 - d / 2.2, 0, 1) ** 1.5
    I = hot + spill * (1 - hot)
    ox, oy = OPERATOR
    ax, ay = hx - ox, hy - oy
    L = max(1.0, math.hypot(ax, ay))
    ux, uy = ax / L, ay / L
    px, py = X4 - ox, Y4 - oy
    s = (px * ux + py * uy) / L
    dp = np.abs(px * uy - py * ux)
    hw = 40.0 + (0.75 * r - 40.0) * np.clip(s, 0, 1)
    cone = np.clip(1 - dp / hw, 0, 1) ** 1.6 * np.clip(s, 0, 1) ** 0.7 * np.clip((1.08 - s) / 0.15, 0, 1)
    return I.astype(np.float32), cone.astype(np.float32)


@functools.lru_cache(maxsize=1)
def dust_seed(n=60, seed=21):
    rng = np.random.default_rng(seed)
    out = (rng.uniform(0, W, n), rng.uniform(250, H, n), rng.uniform(0, 2 * np.pi, n), rng.uniform(0.4, 1.0, n),
           rng.uniform(6, 16, n))
    for a in out:
        a.flags.writeable = False
    return out


def draw_dust(cv, t, cone4, level=1.0):
    """60 dust motes (BRIEF 6.9: J.embers(60, seed=21, bright=0.5) x the cone): slow drift, lit only inside the cone."""
    bx, by, ph, br, sp = dust_seed()
    x = (bx + 22 * np.sin(0.31 * t + ph)) % W
    y = (by - sp * t) % H
    xi = np.clip((x / 4).astype(int), 0, W // 4 - 1)
    yi = np.clip((y / 4).astype(int), 0, H // 4 - 1)
    k = cone4[yi, xi] * br * (0.75 + 0.25 * np.sin(2.1 * t + ph * 3)) * level
    cols = k[:, None] * (IVORY * 0.5)[None, :] * 4.0
    splat(cv, x, y, cols, sigma=0.9)


# ================================================================================================ room (CAM_ROOM)
PROPS = ('tower_room', 'crt_room', 'box_room')
LED_POS = (799.5, 1265.0)
KEY_GAIN = 1.6


@functools.lru_cache(maxsize=1)
def room_static():
    lit = np.ascontiguousarray(pass_('desk_plate', 'lit')[..., :3])
    prac = np.array(pass_('desk_plate', 'practicals')[..., :3], np.float32)
    # the dusk sky card in the window stays low in the dark plate (cover: window mean luma <= 10, never violet)
    win = np.zeros((H, W), np.float32)
    win[300:900, 720:1010] = 1.0
    win = cv2.GaussianBlur(win, (0, 0), 6.0)
    prac *= (1.0 - 0.55 * win)[..., None]
    L = K.lum(lit).astype(np.float32)
    illum = cv2.GaussianBlur(L, (0, 0), 90) + 0.012
    alb = np.clip(lit / illum[..., None], 0, 2.0) * np.float32(0.62)
    props = {}
    for n in PROPS:
        fx, fy = asset(n).meta['frame_xy']
        props[n] = dict(xy=(int(fx), int(fy)), room=pass_(n, 'room'), kl=pass_(n, 'key_l'), kr=pass_(n, 'key_r'),
                        emit=pass_(n, 'emit'))
    sm = pass_('crt_room', 'screen_mask')
    mask = np.ascontiguousarray(sm[65:305, 75:415, :3].mean(-1))
    return dict(lit=ro(lit), prac=ro(prac), alb=ro(alb), props=props, scr=ro(mask), scr_xy=(300, 1050))


def mains_hook(f):
    """Hook A mains factor: lit f0-f9, brownout f10-f13 = 0.45, 0.80, 0.35, 0.15, dead from f14 (negative f = the
    lit loop tail)."""
    if f < 10:
        return 1.0
    return {10: 0.45, 11: 0.80, 12: 0.35, 13: 0.15}.get(f, 0.0)


T_FAN_OFF = F(14)


def fan_rev_hook(t):
    if t <= T_FAN_OFF:
        return 4.5 * t
    return 4.5 * (T_FAN_OFF + 1.0 * (1.0 - math.exp(-(t - T_FAN_OFF) / 1.0)))


def fan_rate_hook(t):
    return 4.5 if t <= T_FAN_OFF else 4.5 * math.exp(-(t - T_FAN_OFF) / 1.0)


T_ON8 = F(880)


def fan_rev_up(t):
    """S8a: spins up over 2.5 s (out_cubic) after the power returns at f880."""
    if t <= T_ON8:
        return 0.0
    u = min(1.0, (t - T_ON8) / 2.5)
    r = 4.5 * 2.5 * (u - (1.0 - (1.0 - u) ** 4) / 4.0)
    if t > T_ON8 + 2.5:
        r += 4.5 * (t - T_ON8 - 2.5)
    return r


def fan_rate_up(t):
    if t <= T_ON8:
        return 0.0
    u = min(1.0, (t - T_ON8) / 2.5)
    return 4.5 * (1.0 - (1.0 - u) ** 3)


def crt_hook_layer(t):
    """Hook A CRT (BRIEF 6.3 / 6.9): image x mains to f11; f12 squeezed to 40 % (x1.6), f13 6 % (x2.2), f14 the
    8 px line (x2.5 + AMBER core, full width), f15 on the 12 px dot (AMBER x2.5, decays tau 0.35 s)."""
    f = fi(t)
    if f < 12:
        return crt_image(t) * np.float32(mains_hook(f))
    if f == 12:
        return collapse(crt_image(t), v=0.40, gain=1.6)
    if f == 13:
        return collapse(crt_image(t), v=0.06, gain=2.2)
    if f == 14:
        return collapse(crt_image(t), line=True, gain=2.5)
    return dot((240, 340), math.exp(-(t - F(15)) / 0.35))


TRACK_A = K.Track([(F(20), (560.0, 600.0)), (F(24), (560.0, 600.0), 'inout_sine'), (F(38), (830.0, 1300.0))])
TRACK_B = K.Track([(F(0), (830.0, 1300.0)), (F(30), (830.0, 1300.0), 'inout_sine'), (F(70), (470.0, 1170.0))])
TRACK_S4 = K.Track([(F(300), (100.0, 1330.0), 'inout_sine'), (F(340), (160.0, 1345.0)),
                    (F(351), (160.0, 1345.0), 'inout_sine'), (F(366), (470.0, 1170.0))])


def room_state(mode, t):
    f = fi(t)
    st = dict(m=0.0, torch=None, crt=None, led=(60, 'F'), fan=None, cam=(0.0, 0.0, 0.0), scale=1.0,
              centre=(540.0, 960.0), clock=t)
    if mode == 'lit' or (mode == 'A' and f < 0):
        st.update(m=1.0, crt=crt_image(t), led=(30, 'A'), fan=fan_angles(t, lambda x: 4.5 * x, lambda x: 4.5))
        return st
    if mode == 'A':
        st.update(m=mains_hook(f), crt=crt_hook_layer(t), fan=fan_angles(t, fan_rev_hook, fan_rate_hook))
        if f < 14:
            st['led'] = (30, 'A')
        else:
            st['led'] = (300 if f in (40, 41, 44, 45, 60, 61, 64, 65) else 60, 'F')
        if f >= 20:
            hx, hy = TRACK_A(t)
            st['torch'] = (float(hx), float(hy), 1.0)
        st['cam'] = drift(t, ease('inout_sine', (t - F(20)) / F(15)) if t >= F(20) else 0.0)
        return st
    if mode == 'B':
        hx, hy = TRACK_B(t)
        st.update(torch=(float(hx), float(hy), 1.0), led=(300 if f in (0, 1, 4, 5, 40, 41, 44, 45) else 60, 'F'),
                  cam=drift(t, 1.0))
        return st
    if mode == 'S4':
        hx, hy = TRACK_S4(t)
        st.update(torch=(float(hx), float(hy), 1.0), led=(300 if f in (380, 381, 384, 385) else 60, 'F'),
                  cam=drift(t, 1.0), scale=1.0 + 0.04 * ease('easy_ease', (t - F(320)) / F(80)), centre=(500.0, 1100.0))
        return st
    if mode == 'S8a':
        m = {880: 0.6, 881: 0.6, 882: 1.0, 883: 0.7}.get(f, 1.0 if f >= 884 else 0.6)
        st.update(m=m, crt=crt_image(t - DUR) * np.float32(m) if f >= 883 else None, led=(30, 'A'),
                  fan=fan_angles(t, fan_rev_up, fan_rate_up))
        return st
    raise ValueError(mode)


def room_render(st, t):
    """Compose CAM_ROOM for a state (no camera): plate (lit x m over practicals) + torch on the plate, fan, props
    (room x m, torch key passes x beam), CRT content x screen mask, LEDs, beam cone + dust."""
    S = room_static()
    m = st['m']
    cv = np.empty((H, W, 4), np.float32)
    rgb = cv[..., :3]
    if m >= 1.0:
        rgb[:] = S['lit']
    elif m <= 0.0:
        rgb[:] = S['prac']
    else:
        np.multiply(S['prac'], np.float32(1.0 - m), out=rgb)
        rgb += S['lit'] * np.float32(m)
    cv[..., 3] = 1.0
    I = cone4 = None
    hx = 540.0
    if st['torch'] is not None:
        hx, hy, lev = st['torch']
        I4, cone4 = torch_fields(hx, hy)
        I = cv2.resize(I4 * np.float32(lev), (W, H), interpolation=cv2.INTER_LINEAR)
        rgb += S['alb'] * (I[..., None] * np.float32(0.55)) * TORCH
    if st['fan'] is not None:
        draw_fan(cv, st['fan'], m)
    for n in PROPS:
        p = S['props'][n]
        x0, y0 = p['xy']
        spr = p['room']
        h, w = spr.shape[:2]
        h = min(h, H - y0)
        w = min(w, W - x0)
        reg = cv[y0:y0 + h, x0:x0 + w, :3]
        a = spr[:h, :w, 3:4]
        reg *= (1.0 - a)
        if m > 0:
            reg += spr[:h, :w, :3] * np.float32(m)
        if I is not None:
            wr = float(np.clip((hx - (x0 + w / 2.0)) / 400.0 + 0.5, 0.0, 1.0))
            key = p['kl'][:h, :w, :3] * np.float32(1.0 - wr) + p['kr'][:h, :w, :3] * np.float32(wr)
            reg += key * (I[y0:y0 + h, x0:x0 + w, None] * np.float32(KEY_GAIN))
        if n != 'box_room' and m > 0:
            reg += p['emit'][:h, :w, :3] * np.float32(0.8 * m)
    if st['crt'] is not None:
        sx, sy = S['scr_xy']
        cv[sy:sy + 240, sx:sx + 340, :3] += st['crt'] * S['scr'][..., None]
    lev, ck = st['led']
    bx = S['props']['box_room']
    x0, y0 = bx['xy']
    e = bx['emit']
    cv[y0:y0 + e.shape[0], x0:x0 + e.shape[1], :3] += e[..., :3] * np.float32(lev / 100.0)
    K.draw(cv, led_col(ck), LED_POS[0], LED_POS[1], mode='add', opacity=lev / 100.0)
    if cone4 is not None:
        cone = cv2.resize(cone4, (W, H), interpolation=cv2.INTER_LINEAR)
        rgb += cone[..., None] * TORCH * np.float32(0.07 * st['torch'][2])
        draw_dust(cv, t, cone4, st['torch'][2])
    return cv


def room(t, mode):
    """CAM_ROOM shot at t: compose + the shot camera (drift / push) as one warp."""
    st = room_state(mode, t)
    cv = room_render(st, t)
    dx, dy, roll = st['cam']
    return warp(cv, dx, dy, roll, st['scale'], st['centre'])


# ================================================================================================ S2 candle tabletop
S2_Y0 = 900                 # world row -900 is array row 0 (the ceiling above the table, for the tilt)
S2_H = 2880
WICK2 = (540.0, 1000.0)
CANDLE2_H = 450.0           # wick tip -> saucer base on screen (85 mm tabletop)


@functools.lru_cache(maxsize=1)
def candle_sprites():
    """Candle body 'self' pass (lit by its own flame) + 0.18 x key_r, at the S2 / S7b / macro scales."""
    a = asset('candle')
    spr = np.array(pass_('candle', 'self'), np.float32)
    spr[..., :3] += np.float32(0.18) * pass_('candle', 'key_r')[..., :3]
    wx, wy = a.meta['features']['wick_tip']
    bx, by = a.meta['features']['base']
    return ro(spr), (wx, wy), (by - wy)


@functools.lru_cache(maxsize=8)
def candle_scaled(body_h):
    spr, (wx, wy), span = candle_sprites()
    s = body_h / span
    sm = cv2.resize(spr, (max(2, int(round(spr.shape[1] * s))), max(2, int(round(spr.shape[0] * s)))),
                    interpolation=cv2.INTER_AREA)
    return ro(sm), (wx * s, wy * s)


def blit(cv, spr, x0, y0, gain=1.0):
    """Premultiplied 'over' of spr with its top-left at integer (x0, y0) (clipped); rgb x gain (alpha kept)."""
    x0, y0 = int(round(x0)), int(round(y0))
    h, w = spr.shape[:2]
    ax0, ay0 = max(0, x0), max(0, y0)
    ax1, ay1 = min(W, x0 + w), min(cv.shape[0], y0 + h)
    if ax1 <= ax0 or ay1 <= ay0:
        return
    s = spr[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
    reg = cv[ay0:ay1, ax0:ax1]
    reg[..., :3] *= (1.0 - s[..., 3:4])
    reg[..., :3] += s[..., :3] * np.float32(gain)


@functools.lru_cache(maxsize=1)
def copy_sprite():
    """The homework copy, open (kraft-brown cover AMBER x0.4, ruled pages, no legible text), flat 420 x 250."""
    w, h = 420, 250
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = AMBER * 0.40 * np.float32(0.55) + EMBER * 0.05
    spr[..., 3] = 1.0
    page = IVORY * 0.26
    for x0, x1 in ((12, 204), (216, 408)):
        spr[10:h - 10, x0:x1, :3] = page
        for y in range(34, h - 14, 14):
            spr[y:y + 1, x0 + 8:x1 - 8, :3] = page * 0.62
        spr[10:h - 10, x0 + 26:x0 + 27, :3] = page * 0.55 + RED * 0.05
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    spine = np.exp(-((xx - 210) / 10.0) ** 2) * 0.55
    spr[..., :3] *= (1.0 - spine[..., None])
    return ro(spr)


@functools.lru_cache(maxsize=1)
def s2_static():
    """S2 world rows -900..1980 (array row = y + S2_Y0): albedo, the candle-lit layer (light at level 1) and the
    ambient layer (dusk indigo floor). Ceiling slab (y < -100) with the dead fan, wall, teak table from y 1260,
    the copy on the table at the left."""
    h, w = S2_H, W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    wy = yy - S2_Y0
    alb = np.empty((h, w, 3), np.float32)
    alb[:] = SMOKE * 0.78 + ASH * 0.22
    alb[wy < -100] = NIGHT_1 * 2.0
    table = wy >= 1260
    teak = WOOD * 0.9 + EMBER * 0.012
    alb[table] = teak
    grain = (np.sin(xx * 0.05 + np.sin(wy * 0.013) * 3.0) * 0.5 + 0.5) * 0.25 + 0.88
    alb[table] *= grain[table][:, None]
    for cx, cy, rx, ry in ((770.0, 1560.0, 70.0, 20.0), (905.0, 1700.0, 62.0, 18.0), (180.0, 1760.0, 58.0, 16.0)):
        ring = np.abs(np.sqrt(((xx - cx) / rx) ** 2 + ((wy - cy) / ry) ** 2) - 1.0) < 0.06
        alb[ring] *= 1.5
    # the open copy, in perspective on the table (left of the candle)
    cp = copy_sprite()
    src = np.float32([[0, 0], [cp.shape[1], 0], [cp.shape[1], cp.shape[0]], [0, cp.shape[0]]])
    dst = np.float32([[112, 1336 + S2_Y0], [440, 1322 + S2_Y0], [484, 1528 + S2_Y0], [70, 1546 + S2_Y0]])
    M = cv2.getPerspectiveTransform(src, dst)
    cw = cv2.warpPerspective(cp, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    a = cw[..., 3:4]
    alb[:] = alb * (1.0 - a) + cw[..., :3]
    # candle light: point-like falloff from the flame on the wall, a foreshortened pool on the table
    fx, fy = WICK2[0], WICK2[1] - 40.0
    r = np.sqrt((xx - fx) ** 2 + (wy - fy) ** 2)
    Lw = 1.0 / (1.0 + (r / 230.0) ** 2)
    rt = np.sqrt((xx - fx) ** 2 + ((wy - 1450.0) * 2.0) ** 2)
    Lt = 1.15 / (1.0 + (rt / 230.0) ** 2)
    Lc = np.where(table, Lt, Lw).astype(np.float32)
    Lc[wy < -100] = 0.0
    lit = alb * (Lc[..., None] * np.float32(1.8)) * CANDLE
    amb = alb * np.float32(0.035) + INDIGO * np.float32(0.22)
    # ceiling slab: the dead fan rim-lit from below + a faint uplight on the slab's lower edge
    up = np.clip(1.0 - (-100.0 - wy) / 500.0, 0, 1) ** 2 * (wy < -100)
    amb += up[..., None] * (AMBER * 0.012)
    cov, hub = fan_cov([28.0], hub=(540.0, -560.0 + S2_Y0), flat=0.42, y0=-560 + S2_Y0 - 60)
    y_f = -560 + S2_Y0 - 60
    reg_a = amb[y_f:y_f + FAN_STRIP]
    reg_l = lit[y_f:y_f + FAN_STRIP]
    edge = np.clip(cov - np.roll(cov, -3, axis=0), 0, 1) + np.clip(hub - np.roll(hub, -3, axis=0), 0, 1)
    paint(reg_a, np.clip(cov + hub, 0, 1), NIGHT_0)
    reg_l *= (1.0 - np.clip(cov + hub, 0, 1))[..., None]
    reg_a += edge[..., None] * AMBER * 0.16
    return ro(amb.astype(np.float32)), ro(lit.astype(np.float32))


@functools.lru_cache(maxsize=1)
def pankhi_sprite():
    a = asset('pankhi')
    spr = pass_('pankhi', 'key_l')
    s = 0.5
    sm = cv2.resize(spr, (int(spr.shape[1] * s), int(spr.shape[0] * s)), interpolation=cv2.INTER_AREA)
    px, py = a.meta['features']['pivot']
    return ro(sm), (px / spr.shape[1], py / spr.shape[0])


PANKHI_PIVOT = (1150.0, 1330.0)


def pankhi_angle(t):
    """Swings in from the right on the beats f100 / f120 / f140 (a hand fanning off-frame): rest +10 deg, peak -55."""
    b = 0.0
    for f in (100, 120, 140):
        b += math.exp(-0.5 * ((t - F(f)) / 0.15) ** 2)
    return 10.0 - 65.0 * min(1.0, b)


def match_level(t):
    """Match: flares f80 (impulse), burns, lights the wick at f86, dies f94-f100 as it is pulled away."""
    if t < F(80) - HALF:
        return 0.0
    lv = 1.0 + 0.9 * math.exp(-max(0.0, t - F(80)) / 0.07)
    return lv * (1.0 - ease('in_cubic', (t - F(94)) / F(6)))


def candle_level(t):
    """The wick catches at f86 (flame grows out_cubic over 10 f); flicker +-8 % (BF.candle_flicker)."""
    return ease('out_cubic', (t - F(86)) / F(10)) * candle_flicker(t)


def s2(t):
    f = fi(t)
    tilt = 900.0 * ease('in_cubic', (t - F(140)) / F(20))
    ti = int(math.floor(tilt))
    tf = tilt - ti
    amb, lit = s2_static()
    r0 = S2_Y0 - ti
    lc = candle_level(t)
    lm = match_level(t)
    L = lc + 0.75 * lm
    cv = np.empty((H, W, 4), np.float32)
    rgb = cv[..., :3]
    np.multiply(lit[r0:r0 + H], np.float32(L), out=rgb)
    rgb += amb[r0:r0 + H]
    cv[..., 3] = 1.0
    # candle body (lit by its own flame + the match)
    spr, (wx, wy) = candle_scaled(CANDLE2_H)
    blit(cv, spr, WICK2[0] - wx, WICK2[1] + ti - wy, gain=0.15 + 0.85 * min(1.2, L))
    # match: stick + flame near the wick, pulled away down-right f94-f104
    if F(80) - HALF <= t < F(104):
        u = ease('in_cubic', (t - F(94)) / F(10))
        mx, my = 588.0 + 180.0 * u, 990.0 + 120.0 * u + ti
        st = np.array([[mx - 3, my + 6], [mx + 140, my + 96], [mx + 136, my + 102], [mx - 6, my + 12]])
        cov = poly_mask(H, W, [st])
        paint(rgb, cov, WOOD * (0.4 + 1.2 * min(1.0, lm)))
        if lm > 0.01:
            draw_flame(cv, t, mx, my, 44, gain=lm, rot=-25.0 + flame_sway(t, 2.0), sy=1.0)
    if lc > 0.001:
        g = ease('out_cubic', (t - F(86)) / F(10))
        draw_flame(cv, t, WICK2[0], WICK2[1] + ti, 120, gain=candle_flicker(t), rot=flame_sway(t), sy=g)
    # pankhi (lit from the candle side), swinging in on the beats
    ang = pankhi_angle(t)
    if ang < 8.0:
        ps, anc = pankhi_sprite()
        lay = np.zeros((H, W, 4), np.float32)
        K.draw(lay, ps, PANKHI_PIVOT[0], PANKHI_PIVOT[1] + ti, rot=ang, anchor=anc)
        bc = (PANKHI_PIVOT[0] + 311.0 * math.sin(math.radians(ang)), PANKHI_PIVOT[1] - 311.0 * math.cos(math.radians(ang)))
        rr = math.hypot(bc[0] - WICK2[0], bc[1] - WICK2[1])
        g = (0.10 + 1.6 * L / (1.0 + (rr / 300.0) ** 2))
        rgb *= (1.0 - lay[..., 3:4])
        rgb += lay[..., :3] * np.float32(g)
    dx, dy, roll = drift(t, 1.0)
    out = warp(cv, dx, dy + tf, roll)
    if F(140) <= t < F(160):
        v = 900.0 * 3.0 * (max(0.0, (t - F(140)) / F(20))) ** 2 / 20.0          # px per frame (in_cubic)
        amt = v * 0.5 / nsamp(t)
        if amt > 1.0:
            K.whip_blur(out, amt, angle=90.0)
    return out


# ================================================================================================ S3 rooftops
S3_H = 2240
CHILD_HEAD = (720.0, 1335.0)
FAR_WIN = (330.0, 1040.0)
PLASTER = 0.32                 # albedo of the lime-wash parapets / charpai rope under the candle pools
ADULT_LIGHT = (0.84, 0.55)     # direction to the charpai candle (rim side)
CHILD_LIGHT = (-0.55, 0.83)    # direction to the parapet candle at x 610 (rim on his profile side)


def _rng(seed):
    return np.random.default_rng(seed)


def _rim_glow(m, d, width=2.5, k=0.9):
    r = rim_of(m, d[0], d[1], width)
    return (r + cv2.GaussianBlur(r, (0, 0), 2.0) * 0.6)[..., None] * AMBER * np.float32(k)


def adult_polys():
    """Neighbour sitting on the charpai (head about (290, 1250)), fanning himself with a pankhi in his right hand."""
    return [ellipse_pts(290, 1250, 27, 32),
            np.array([[279, 1274], [301, 1274], [303, 1294], [277, 1294]]),
            np.array([[244, 1300], [262, 1290], [318, 1290], [338, 1300], [346, 1340], [338, 1424], [250, 1426],
                      [238, 1340]]),
            np.array([[328, 1300], [346, 1296], [380, 1350], [372, 1360], [340, 1330]]),
            np.array([[366, 1352], [380, 1350], [400, 1272], [390, 1268]]),
            ellipse_pts(410, 1226, 27, 31),
            np.array([[391, 1270], [397, 1270], [409, 1252], [403, 1250]]),
            np.array([[236, 1414], [338, 1414], [346, 1428], [214, 1446], [206, 1440]])]


def child_body_polys():
    """Child standing at the parapet, back three-quarter (the parapet hides him below y 1500)."""
    return [np.array([[709, 1356], [731, 1356], [733, 1370], [707, 1370]]),
            np.array([[692, 1374], [704, 1366], [736, 1366], [750, 1374], [758, 1420], [756, 1510], [684, 1510],
                      [682, 1420]]),
            np.array([[744, 1376], [760, 1370], [788, 1350], [794, 1358], [766, 1388], [752, 1398]])]


@functools.lru_cache(maxsize=1)
def s3_static():
    """Static rooftop base (1080 x S3_H; rows 0..S3_H at settle offset 0) + the dynamic element lists.
    Planes (BRIEF 6.9): sky (NIGHT_0 -> indigo x0.14) + warm dust-haze band + stars; far skyline (tops 1010-1065:
    roofs, stairwell rooms, water tanks, TV antennas) flat NIGHT_0; clotheslines; mid roofs (tops 1170-1230)
    NIGHT_1 x0.6; near parapet (top 1500); charpai (top 1440-1470); the adult and the child (NIGHT_0 + 2.5 px AMBER
    rim on the candle side). Candle pools are light on plaster (albedo 0.32); each flame also gets a soft
    atmospheric glow behind the silhouettes, so the dark shapes read against it."""
    h, w = S3_H, W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rgb = np.zeros((h, w, 3), np.float32)
    u = np.clip(yy / 1010.0, 0, 1) ** 1.6
    rgb[:] = NIGHT_0 * (1 - u[..., None]) + INDIGO * 0.14 * u[..., None]
    band = np.exp(-((yy - 985.0) / 120.0) ** 2)
    rgb += band[..., None] * (SMOKE * 2.0 + AMBER * 0.006)
    rng = _rng(80)
    sx, sy = rng.uniform(10, w - 10, 80), rng.uniform(40, 860, 80)
    sb = rng.uniform(0.10, 0.42, 80)
    for x, y, b in zip(sx, sy, sb):
        r = 1.6 if b > 0.32 else 1.0
        g = gauss2(9, 9, 4 + (x % 1), 4 + (y % 1), r, r)
        rgb[int(y) - 4:int(y) + 5, int(x) - 4:int(x) + 5] += g[..., None] * (IVORY * b)
    # far skyline
    rng = _rng(7)
    polys = []
    x = -20.0
    tops = []
    while x < w + 20:
        ww = rng.uniform(70, 170)
        top = rng.uniform(1010, 1065)
        polys.append(np.array([[x, top], [x + ww + 1, top], [x + ww + 1, 1400], [x, 1400]]))
        tops.append((x, x + ww, top))
        x += ww
    stair = [(290.0, 378.0, 985.0)]
    for (x0, x1, top) in tops:
        if rng.random() < 0.35 and not (230 < x0 < 430) and not (230 < x1 < 430):
            sw = rng.uniform(50, 90)
            sx0 = rng.uniform(x0, max(x0 + 1, x1 - sw))
            stair.append((sx0, sx0 + sw, top - rng.uniform(35, 70)))
    for x0, x1, top in stair:
        polys.append(np.array([[x0, top], [x1, top], [x1, 1300], [x0, 1300]]))
        polys.append(np.array([[x0 - 4, top], [x1 + 4, top], [x1 + 4, top + 5], [x0 - 4, top + 5]]))
    for (x0, x1, top) in tops:
        if rng.random() < 0.4:
            tw = rng.uniform(34, 56)
            th = rng.uniform(24, 38)
            tx = rng.uniform(x0 + 4, max(x0 + 5, x1 - tw - 4))
            ty = top - th - 10
            polys.append(np.array([[tx, ty], [tx + tw, ty], [tx + tw, ty + th], [tx, ty + th]]))
            polys.append(ellipse_pts(tx + tw / 2, ty, tw / 2, 5))
            polys.append(np.array([[tx + 4, ty + th], [tx + 7, ty + th], [tx + 7, top + 1], [tx + 4, top + 1]]))
            polys.append(np.array([[tx + tw - 7, ty + th], [tx + tw - 4, ty + th], [tx + tw - 4, top + 1],
                                   [tx + tw - 7, top + 1]]))
    for i in range(9):
        x0, x1, top = tops[int(rng.integers(0, len(tops)))]
        ax = rng.uniform(x0 + 6, x1 - 6)
        ah = rng.uniform(40, 85)
        polys.append(np.array([[ax - 1, top - ah], [ax + 1, top - ah], [ax + 1, top + 1], [ax - 1, top + 1]]))
        for k in range(int(rng.integers(2, 4))):
            cy = top - ah + 6 + k * 9
            cw = rng.uniform(14, 30) * (1 - 0.2 * k)
            polys.append(np.array([[ax - cw / 2, cy], [ax + cw / 2, cy], [ax + cw / 2, cy + 1.6], [ax - cw / 2, cy + 1.6]]))
    far = poly_mask(h, w, polys)
    paint(rgb, far, NIGHT_0)
    # clotheslines strung above the mid roofs, silhouetted against the haze band
    lines = []
    for (xa, ya, xb, yb, sag) in ((560.0, 1075.0, 1010.0, 1080.0, 24.0), (40.0, 1092.0, 300.0, 1088.0, 16.0)):
        s = np.linspace(0, 1, 60)
        px = xa + (xb - xa) * s
        py = ya + (yb - ya) * s + sag * 4 * s * (1 - s)
        lines.append(np.r_[np.c_[px, py - 0.8], np.c_[px[::-1], py[::-1] + 0.8]])
        for c0 in np.linspace(0.12, 0.82, 5):
            cx = xa + (xb - xa) * c0
            cy = ya + (yb - ya) * c0 + sag * 4 * c0 * (1 - c0)
            cwid = rng.uniform(18, 34)
            ch = rng.uniform(24, 44)
            lines.append(np.array([[cx, cy], [cx + cwid, cy + 1], [cx + cwid - 2, cy + ch], [cx + 2, cy + ch - 3]]))
        for pxp in (xa, xb):
            lines.append(np.array([[pxp - 1.5, ya - 6], [pxp + 1.5, ya - 6], [pxp + 1.5, 1240], [pxp - 1.5, 1240]]))
    paint(rgb, poly_mask(h, w, lines), NIGHT_0 * 1.4)
    # mid roofs (tops 1170-1230) with a faint haze-lit coping edge
    rng = _rng(11)
    mids = []
    x = -30.0
    while x < w + 30:
        ww = rng.uniform(130, 270)
        mids.append((x, x + ww, rng.uniform(1170, 1230)))
        x += ww
    mid_m = poly_mask(h, w, [np.array([[a, tp], [b + 1, tp], [b + 1, 1700], [a, 1700]]) for a, b, tp in mids])
    paint(rgb, mid_m, NIGHT_1 * 0.6)
    edge = poly_mask(h, w, [np.array([[a + 2, tp], [b - 2, tp], [b - 2, tp + 2.5], [a + 2, tp + 2.5]]) for a, b, tp in mids])
    rgb += edge[..., None] * (AMBER * 0.035)
    face_m = poly_mask(h, w, [np.array([[a, tp], [b, tp], [b, tp + 44], [a, tp + 44]]) for a, b, tp in mids])
    # near parapet (top 1500, coping 16 px) + charpai
    par = poly_mask(h, w, [np.array([[-10, 1500], [w + 10, 1500], [w + 10, h + 10], [-10, h + 10]])])
    paint(rgb, par, SMOKE * 0.30)
    cop = poly_mask(h, w, [np.array([[-10, 1500], [w + 10, 1500], [w + 10, 1516], [-10, 1516]])])
    paint(rgb, cop, SMOKE * 0.50)
    char = poly_mask(h, w, [np.array([[170, 1446], [522, 1438], [524, 1470], [168, 1476]])])
    weave = (np.sin(xx * 0.9 + yy * 0.9) * np.sin(xx * 0.9 - yy * 0.9) * 0.5 + 0.5) * 0.6 + 0.4
    paint(rgb, char, SMOKE * 0.25)
    rails = poly_mask(h, w, [np.array([[166, 1440], [526, 1432], [526, 1440], [166, 1448]]),
                             np.array([[164, 1470], [526, 1464], [526, 1472], [164, 1478]]),
                             np.array([[164, 1440], [176, 1440], [176, 1500], [164, 1500]]),
                             np.array([[512, 1432], [524, 1432], [524, 1500], [512, 1500]])])
    paint(rgb, rails, NIGHT_1 * 0.9)
    # candles: (x, y_base, flame_h, kind)
    candles = [(150.0, 1500.0, 22.0, 'near'), (610.0, 1500.0, 22.0, 'near'), (930.0, 1500.0, 22.0, 'near'),
               (436.0, 1446.0, 18.0, 'charpai'), (95.0, None, 10.0, 'mid'), (338.0, None, 10.0, 'mid'),
               (585.0, None, 10.0, 'mid'), (842.0, None, 10.0, 'mid')]
    cand = []
    light = np.zeros((h, w), np.float32)
    glow = np.zeros((h, w), np.float32)
    for (cx, cy, fh, kind) in candles:
        if kind == 'mid':
            cy = [tp for a, b, tp in mids if a <= cx < b][0]
        cand.append((cx, cy, fh, kind))
        if kind == 'near':
            light += gauss2(h, w, cx, cy, 230, 34) * 0.30 * par
            light += gauss2(h, w, cx, cy + 60, 160, 90) * 0.18 * par
            glow += gauss2(h, w, cx, cy - 14, 70, 60)
        elif kind == 'charpai':
            light += gauss2(h, w, cx, cy + 10, 200, 60) * 0.30 * char * weave
            glow += gauss2(h, w, cx, cy - 12, 90, 80) * 1.2
        else:
            light += gauss2(h, w, cx, cy + 22, 110, 45) * 0.16 * face_m
            glow += gauss2(h, w, cx, cy - 6, 40, 34) * 0.8
    rgb += (light * PLASTER)[..., None] * AMBER * 2.2
    rgb += glow[..., None] * (AMBER * 0.030 + FLAME * 0.012)
    for (cx, cy, fh, kind) in cand:
        stub_h, stub_w = (14.0, 8.0) if kind != 'mid' else (7.0, 4.0)
        stub = poly_mask(h, w, [np.array([[cx - stub_w / 2, cy - stub_h], [cx + stub_w / 2, cy - stub_h],
                                          [cx + stub_w / 2, cy], [cx - stub_w / 2, cy]])])
        paint(rgb, stub, IVORY * (0.30 if kind != 'mid' else 0.18))
    # the two silhouettes (NIGHT_0, rim on the candle side)
    adult = poly_mask(h, w, adult_polys())
    paint(rgb, adult, NIGHT_0)
    rgb += _rim_glow(adult, ADULT_LIGHT)
    child = poly_mask(h, w, child_body_polys())
    paint(rgb, child, NIGHT_0)
    rgb += _rim_glow(child, CHILD_LIGHT) * (1 - par)[..., None]
    # bulbs (12, far -> near) on stairwell walls and parapets; distant windows
    bulbs = [(95.0, 1024.0, 3.0), (210.0, 1006.0, 3.0), (452.0, 1020.0, 3.0), (690.0, 1008.0, 3.0),
             (1000.0, 1026.0, 3.0), (520.0, 1044.0, 3.2), (60.0, 1196.0, 4.5), (250.0, 1214.0, 4.5),
             (640.0, 1224.0, 4.5), (880.0, 1198.0, 4.5), (40.0, 1462.0, 7.0), (1010.0, 1458.0, 7.0)]
    wins = [(FAR_WIN[0], FAR_WIN[1], 22.0, 30.0)]
    for (x0, x1, top) in stair[1:6]:
        wins.append(((x0 + x1) / 2, top + 22, 10.0, 14.0))
    for (a, b, tp) in mids[1:6:2]:
        wins.append((a + (b - a) * 0.6, tp + 64, 14.0, 18.0))
    return dict(base=ro(rgb.astype(np.float32)), cand=cand, bulbs=bulbs, wins=wins, par=ro(par))


@functools.lru_cache(maxsize=16)
def bulb_sprite(r):
    """A bare bulb: AMBER core (<= 3x linear) + K.glow + a soft pool on its wall (unit level, emissive)."""
    d = K.disc(r, AMBER * 3.0)
    g = K.glow(d, AMBER, sigmas=(1.5 * r + 2, 5 * r + 4, 14 * r + 10), strength=1.0)
    pw, ph = int(24 * r + 40), int(14 * r + 24)
    spr = np.zeros((max(g.shape[0], ph * 2 + 1), max(g.shape[1], pw * 2 + 1), 4), np.float32)
    cy, cx = spr.shape[0] // 2, spr.shape[1] // 2
    spr[..., :3] += gauss2(spr.shape[0], spr.shape[1], cx, cy + r * 3, pw * 0.5, ph * 0.5)[..., None] * AMBER * 0.14
    y0, x0 = cy - g.shape[0] // 2, cx - g.shape[1] // 2
    spr[y0:y0 + g.shape[0], x0:x0 + g.shape[1], :3] += g[..., :3]
    spr[..., 3] = 0.0
    return ro(spr)


@functools.lru_cache(maxsize=8)
def win_sprite(w_, h_, glow):
    spr = np.zeros((int(h_), int(w_), 4), np.float32)
    spr[..., :3] = IVORY
    spr[..., 3] = 1.0
    if glow:
        g = K.glow(spr, IVORY, sigmas=(4, 12), strength=0.8)
    else:
        g = K.glow(spr, IVORY, sigmas=(3,), strength=0.4)
    g = np.array(g, np.float32)
    g[..., 3] = 0.0
    return ro(g)


def bulb_level(i, f):
    """Ignite far -> near f240-f245, 2 per frame (bulb 7 a frame late, buzzing); die near -> far f300-f302 with one
    1-frame relight on the nearest (darken-only)."""
    on = 240 + i // 2 + (1 if i == 7 else 0)
    if f < on:
        return 0.0
    if f < 300:
        return 0.88 + 0.12 * math.sin(f * 2.7) if i == 7 else 1.0
    off = 300 + (11 - i) // 4
    if i == 11 and f == 301:
        return 0.8
    return 1.0 if f < off else 0.0


def child_head(u):
    """Child head polygon: three-quarter back (u=0) -> profile facing screen-left (u=1), same vertex count."""
    cx, cy = CHILD_HEAD
    a = np.radians(np.linspace(0, 360, 96, endpoint=False))
    rx, ry = 25.0, 28.0
    deg = np.degrees(a)

    def bump(c, wdt, amp):
        d = (deg - c + 180) % 360 - 180
        return amp * np.exp(-(d / wdt) ** 2)
    r_back = 1.0 + bump(0, 16, 0.07) + bump(300, 40, 0.04)
    r_prof = 1.0 + bump(178, 7, 0.26) + bump(198, 6, 0.10) + bump(214, 8, 0.12) - bump(160, 10, 0.07) \
        + bump(20, 30, 0.08) + bump(300, 40, 0.04)
    r = (1 - u) * r_back + u * r_prof
    return np.c_[cx + rx * r * np.cos(a), cy + ry * r * np.sin(a)]


def s3(t):
    f = fi(t)
    S = s3_static()
    settle = 300.0 * (1.0 - ease('out_cubic', (t - F(160)) / F(20))) if t < F(180) else 0.0
    si = int(math.floor(settle))
    sf = settle - si
    cv = np.empty((H, W, 4), np.float32)
    cv[..., :3] = S['base'][si:si + H]
    cv[..., 3] = 1.0
    rgb = cv[..., :3]
    oy = -si
    # the child's head (turns f224-f230 toward the far window, holds) and the pankhi he fans with
    u = ease('out_cubic', (t - F(224)) / F(6))
    y0 = int(CHILD_HEAD[1] + oy - 70)
    if 0 <= y0 < H - 160:
        reg = rgb[y0:y0 + 160]
        hp = child_head(u) - np.array([0.0, y0 - oy])
        ang = math.radians(-22.0 + 14.0 * math.sin(2 * math.pi * 1.6 * t))
        hx, hy = 790.0, 1352.0 - (y0 - oy)
        bx, by = hx + 64 * math.sin(ang), hy - 64 * math.cos(ang)
        pk = [ellipse_pts(bx, by, 27, 31), np.array([[hx - 2.5, hy], [hx + 2.5, hy], [bx + 2.5, by], [bx - 2.5, by]])]
        m = poly_mask(160, W, [hp] + pk)
        paint(reg, m, NIGHT_0)
        r = rim_of(m, CHILD_LIGHT[0], CHILD_LIGHT[1], 2.5)
        reg += (r + cv2.GaussianBlur(r, (0, 0), 2.0) * 0.6)[..., None] * AMBER * 0.9
    for i, (cx, cy, fh, kind) in enumerate(S['cand']):
        g = 1.0 + 0.08 * max(-1.0, min(1.0, K.wiggle(t, 1.5, 1.0, 60 + i)))
        draw_flame(cv, t, cx, cy - (14.0 if kind != 'mid' else 7.0) + oy, fh, gain=g, rot=flame_sway(t + i, 0.6))
    for j, (wx, wy, ww, wh) in enumerate(S['wins']):
        lev = 0.0
        if j == 0 and f in (220, 221):
            lev = 0.9
        if 240 + min(j, 3) <= f < 300 + (2 if j < 3 else 1):
            lev = 0.4
        if lev > 0:
            K.draw(cv, win_sprite(int(ww), int(wh), j == 0 and lev > 0.5), wx, wy + oy, mode='add', opacity=lev)
    for i, (bx_, by_, r) in enumerate(S['bulbs']):
        lv = bulb_level(i, f)
        if lv > 0:
            spr = bulb_sprite(r)
            sh, sw = spr.shape[:2]
            x0, yb = int(round(bx_ - sw / 2)), int(round(by_ + oy - sh / 2))
            ax0, ay0, ax1, ay1 = max(0, x0), max(0, yb), min(W, x0 + sw), min(H, yb + sh)
            if ax1 > ax0 and ay1 > ay0:
                rgb[ay0:ay1, ax0:ax1] += spr[ay0 - yb:ay1 - yb, ax0 - x0:ax1 - x0, :3] * np.float32(lv)
    amp = 1.0
    if f >= 240:
        amp = 1.0 - ease('out_cubic', (t - F(240)) / F(4))
        if f >= 300:
            amp = ease('inout_sine', (t - F(300)) / F(15))
    dx, dy, roll = drift(t, amp)
    out = warp(cv, dx, dy + sf, roll)
    if F(160) <= t < F(172):
        v = 300.0 * 3.0 * (1.0 - (t - F(160)) / F(20)) ** 2 / 20.0
        amt = v * 0.5 / nsamp(t)
        if amt > 1.0:
            K.whip_blur(out, amt, angle=90.0)
    return out


@functools.lru_cache(maxsize=1)
def rooftop_still():
    """The 9:16 rooftop viewer still for the S5 monitor (236 x 420): S3 at 7.0 s (no drift), exposure x2.2."""
    S = s3_static()
    cv = new()
    cv[..., :3] = S['base'][:H]
    for i, (cx, cy, fh, kind) in enumerate(S['cand']):
        draw_flame(cv, 7.0, cx, cy - (14.0 if kind != 'mid' else 7.0), fh)
    sm = cv2.resize(np.ascontiguousarray(cv[..., :3]), (236, 420), interpolation=cv2.INTER_AREA) * np.float32(2.2)
    return ro(sm.astype(np.float32))


# ================================================================================================ S5 modern desk
CARD_C = (540.0, 700.0)
CARD_WH = (880, 520)


@functools.lru_cache(maxsize=1)
def s5_static():
    """Wall + desk (ambient) + the light layers (desk lamp, monitor glow) + the monitor face (glass card with the same
    edit, parked playhead, + the 9:16 rooftop viewer) + housing, stand, the cold chai cup."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    amb = np.empty((H, W, 3), np.float32)
    amb[:] = NIGHT_1 * 0.9 + INDIGO * 0.18
    desk = yy >= 1150
    amb[desk] = SMOKE * 0.30
    lamp_r = np.sqrt((xx - 150) ** 2 + (yy - 200) ** 2)
    lamp = (1.0 / (1.0 + (lamp_r / 300.0) ** 2))
    wall_alb = (SMOKE * 0.78 + ASH * 0.22) * 2.2
    desk_alb = WOOD * 1.1
    lamp_l = (lamp[..., None] * (AMBER * 0.35)).astype(np.float32)
    lamp_l *= np.where(desk[..., None], desk_alb, wall_alb)
    mon_r = np.sqrt(((xx - CARD_C[0]) / 520.0) ** 2 + ((yy - 1180.0) / 140.0) ** 2)
    mon = (np.exp(-mon_r ** 2) * desk)[..., None] * (FLAME * 0.035 + IVORY * 0.025)
    halo = np.exp(-(((xx - 540) / 620.0) ** 2 + ((yy - 700) / 420.0) ** 2))[..., None] * (FLAME * 0.022) * (~desk)[..., None]
    mon = (mon + halo).astype(np.float32)
    lamp_l += gauss2(H, W, 150, 200, 46, 46)[..., None] * AMBER * 0.45            # the lamp's bulb, seen soft
    # monitor stand + housing (dark, always)
    stand = poly_mask(H, W, [np.array([[516, 958], [564, 958], [572, 1150], [508, 1150]]),
                             ellipse_pts(540, 1158, 150, 16)])
    paint(amb, stand, SMOKE * 0.55)
    housing = K.rrect_alpha(904, 544, 34, 0)
    hm = np.zeros((H, W), np.float32)
    hm[700 - 272:700 + 272, 540 - 452:540 + 452] = housing[..., 3] if housing.ndim == 3 else housing
    paint(amb, hm, NIGHT_0 * 1.2 + SMOKE * 0.10)
    # the cold chai cup at the right edge + the ring stain under it
    cup = poly_mask(H, W, [np.array([[972, 1200], [1090, 1200], [1090, 1326], [984, 1326]]), ellipse_pts(1031, 1200, 59, 11)])
    paint(amb, cup, ASH * 0.035 + SMOKE * 0.2)
    lamp_l *= (1.0 - cup[..., None] * 0.7)
    rimc = rim_of(cup, -1.0, -0.3, 2.0)
    amb += rimc[..., None] * AMBER * 0.10
    tea = poly_mask(H, W, [ellipse_pts(1031, 1202, 52, 8)])
    paint(amb, tea, EMBER * 0.05 + WOOD * 0.3)
    ring = np.abs(np.sqrt(((xx - 1010) / 92.0) ** 2 + ((yy - 1352) / 16.0) ** 2) - 1.0) < 0.08
    amb[ring] *= 0.55
    # monitor face: glass card + the edit (stretched, no scanlines, playhead parked at x 440) + rooftop viewer
    card = ui.glass_card(CARD_WH[0], CARD_WH[1], r=28, look='dusk')
    face = np.zeros((H, W, 4), np.float32)
    card.draw(face, CARD_C[0], CARD_C[1], frost=0.0, shadow=0.0)
    ed = crt_image(0.0, width=560, scan=False, park=440 - 128)
    face[590:830, 128:688, :3] = ed
    face[590:830, 128:688, 3] = 1.0
    vw = rooftop_still()
    face[480:900, 716:952, :3] = vw
    face[480:900, 716:952, 3] = 1.0
    face[478:480, 714:954, :3] = ASH * 0.25
    face[900:902, 714:954, :3] = ASH * 0.25
    face[480:900, 714:716, :3] = ASH * 0.25
    face[480:900, 952:954, :3] = ASH * 0.25
    return dict(amb=ro(amb), lamp=ro(lamp_l), mon=ro(mon), face=ro(face))


def mains_s5(f):
    if f < 470:
        return 1.0
    if f < 480:
        return {470: 0.6, 471: 0.9}.get(f, 1.0)
    return {480: 0.4, 481: 0.1}.get(f, 0.0)


@functools.lru_cache(maxsize=160)
def hud_text(s, col):
    st = 'jw_mono'
    return T.render(s, st, px=72 if s.endswith('%') else 40, fill=col)


def hud_value(f):
    if f < 440:
        return 63
    if f < 486:
        return 64
    if f < 520:
        return int(round(64 * (1.0 - ease('in_cubic', (f - 486) / 34.0))))
    return 0


@functools.lru_cache(maxsize=1)
def hud_bar_grad():
    x = np.linspace(0, 1, 770, dtype=np.float32)[:, None]
    return ro((FLAME[None, :] * (1 - x) + RED[None, :] * x).astype(np.float32))


def draw_hud(cv, t):
    f = fi(t)
    if f < 400:
        return
    a1 = ease('out_cubic', (t - F(400)) / F(5))
    u1 = hud_text('RENDERING', 'ASH')
    w1, _ = T.measure('RENDERING', 'jw_mono', px=40)
    u1.draw(cv, 130 + w1 / 2, 1030, opacity=a1)
    v = hud_value(f)
    col = 'RED' if v < 20 else 'IVORY'
    s = '%d%%' % v
    u2 = hud_text(s, col)
    w2, _ = T.measure(s, 'jw_mono', px=72)
    op = 1.0
    if f >= 520:
        op = 0.85 + 0.15 * math.cos(2 * math.pi * 1.5 * (t - F(520)))
    u2.draw(cv, 900 - w2 / 2, 1030, opacity=op)
    cv[1080:1094, 130:900, :3] = SMOKE * 1.6
    wv = int(round(v / 100.0 * 770))
    if wv > 0:
        cv[1080:1094, 130:130 + wv, :3] = hud_bar_grad()[:wv][None, :, :] * np.float32(op)


def monitor_layer(t):
    """The monitor face at t: x mains (dip f470-f472), then the collapse f480-f485 and the dot from f485."""
    f = fi(t)
    S = s5_static()
    face = S['face']
    if f < 480:
        return face, mains_s5(f)
    x0, x1, y0, y1 = 100, 980, 440, 960
    body = np.ascontiguousarray(face[y0:y1, x0:x1, :3])
    out = np.zeros((H, W, 4), np.float32)
    if f == 480:
        return face, 0.4
    if f == 481:
        img = collapse(body, v=0.45, gain=1.5)
    elif f == 482:
        img = collapse(body, v=0.08, gain=2.0)
    elif f == 483:
        img = collapse(body, line=True, gain=2.5)
    elif f == 484:
        img = collapse(body, line=True, hs=0.5, gain=2.5)
    else:
        img = dot(body.shape, math.exp(-(t - F(485)) / 0.35))
    out[y0:y1, x0:x1, :3] = img
    return out, 1.0


def s5(t):
    f = fi(t)
    S = s5_static()
    m = mains_s5(f)
    cv = np.empty((H, W, 4), np.float32)
    rgb = cv[..., :3]
    rgb[:] = S['amb']
    if m > 0:
        rgb += S['lamp'] * np.float32(m) + S['mon'] * np.float32(m)
    cv[..., 3] = 1.0
    face, g = monitor_layer(t)
    if g > 0:
        if face is S['face']:
            a = face[..., 3:4]
            rgb *= (1.0 - a)
            rgb += face[..., :3] * np.float32(g)
        else:
            rgb += face[..., :3]
    draw_hud(cv, t)
    amp = 0.0
    if f >= 400:
        amp = 1.0 - ease('out_cubic', (t - F(400)) / F(4))
    if f >= 480:
        amp = ease('inout_sine', (t - F(480)) / F(15))
    if f < 400:
        amp = 1.0
    dx, dy, roll = drift(t, amp)
    return warp(cv, dx, dy, roll)


# ================================================================================================ S6 keycaps
KEY_SCALE = 330.0 / 694.0
CTRL_C = (330.0, 1050.0)
S_C = (720.0, 860.0)
PRESSES = (580, 600, 620, 640, 650, 660, 670, 680, 690, 700, 710)
CHIPS = (582, 602, 622, 642, 652, 662, 672, 682, 692, 702)
U3F_F = 712
CHIP_XY = (780.0, 640.0)


@functools.lru_cache(maxsize=1)
def key_sprites():
    out = {}
    for n in ('keycap_ctrl', 'keycap_s'):
        kl, kr, em = pass_(n, 'key_l'), pass_(n, 'key_r'), pass_(n, 'emit')
        lit = kl * np.float32(0.6) + kr * np.float32(0.4)
        lit[..., 3] = np.maximum(kl[..., 3], kr[..., 3])
        sz = (int(round(900 * KEY_SCALE)), int(round(900 * KEY_SCALE)))
        lit = cv2.resize(lit, sz, interpolation=cv2.INTER_AREA)
        em = cv2.resize(em, sz, interpolation=cv2.INTER_AREA)
        em[..., 3] = 0.0
        em[..., :3] *= 1.8
        out[n] = (ro(lit.astype(np.float32)), ro(em.astype(np.float32)))
    return out


@functools.lru_cache(maxsize=1)
def s6_static():
    """Macro keyboard deck: NIGHT_0, monitor glow from above-front, defocused neighbour keys, a crumb."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cv = new(NIGHT_0)
    g = np.clip(1.0 - yy / 1100.0, 0, 1) ** 2
    cv[..., :3] += g[..., None] * (AMBER * 0.035 + FLAME * 0.02)
    ks = key_sprites()
    bg = np.zeros((H, W, 4), np.float32)
    for (x, y, s, n) in ((80, 640, 0.85, 'keycap_s'), (420, 560, 0.75, 'keycap_s'), (1010, 600, 0.9, 'keycap_s'),
                         (1000, 1060, 1.0, 'keycap_s'), (640, 1270, 1.05, 'keycap_ctrl'), (90, 1460, 1.1, 'keycap_s'),
                         (980, 1500, 1.15, 'keycap_s'), (520, 1640, 1.2, 'keycap_ctrl')):
        K.draw(bg, ks[n][0], x, y, scale=s)
    bg = cv2.GaussianBlur(bg, (0, 0), 15.0)
    bg[..., :3] *= 0.30
    cv[..., :3] = cv[..., :3] * (1 - bg[..., 3:4]) + bg[..., :3]
    crumb = poly_mask(H, W, [np.array([[512, 1168], [524, 1162], [533, 1170], [528, 1181], [515, 1180]])])
    paint(cv[..., :3], crumb, AMBER * 0.22 + WOOD * 0.3)
    return ro(cv)


def key_press(t, frames, lead=0):
    """(dy px, flare 0..1) of a key pressed on `frames` (minus `lead`): +16 px in 2 f (in_cubic), hold 2 f, POP
    spring release (starts where the hold ends); legend flare impulse (decay 9)."""
    last = None
    for p in frames:
        if t >= F(p - lead) - 1e-9:
            last = p - lead
    if last is None:
        return 0.0, 0.0
    d = t - F(last)
    if d < F(2):
        y = 16.0 * ease('in_cubic', d / F(2))
    elif d < F(4):
        y = 16.0
    else:
        y = 16.0 * (1.0 - K.spring(d - F(4), 2.6, 0.5))
    fl = 0.0
    for p in frames:
        fl += K.impulse(t, F(p - lead), decay=9.0)
    return y, min(1.0, fl)


@functools.lru_cache(maxsize=4)
def chip_sprite(text, sel):
    return ro(np.array(ui.chip(text, sel, look='dusk', size=36, h=76), np.float32))


def draw_chips(cv, t):
    f = fi(t)
    if f < CHIPS[0] - 1 or t >= F(720):
        return
    n = len(CHIPS)
    for i, s in enumerate(CHIPS):
        age = t - F(s)
        if age < -HALF:
            continue
        ex0 = min(F(s) + 0.9, F(706))
        if i + 3 < n:
            ex0 = min(ex0, F(CHIPS[i + 3]))
        ex = ease('in_cubic', (t - ex0) / F(6))
        if ex >= 1.0:
            continue
        newer = 0.0
        for j in range(i + 1, n):
            newer += ease('out_cubic', (t - F(CHIPS[j])) / F(5))
        y = CHIP_XY[1] - 92.0 * newer
        sc = 0.85 + 0.15 * K.spring(max(0.0, age), 2.6, 0.5)
        op = ease('linear', (age + HALF) / F(2)) * (1.0 - ex)
        sel_new = 1.0 - min(1.0, newer)
        K.draw(cv, chip_sprite('Saved', 0.0), CHIP_XY[0], y - 6.0 * ex, scale=sc, opacity=op)
        if sel_new > 0.01:
            K.draw(cv, chip_sprite('Saved', 1.0), CHIP_XY[0], y - 6.0 * ex, scale=sc, opacity=op * sel_new)
    if f >= U3F_F:
        age = t - F(U3F_F)
        sc = 0.85 + 0.15 * K.spring(max(0.0, age), 2.6, 0.5)
        K.draw(cv, chip_sprite('Saved · har 30 sec', 1.0), CHIP_XY[0], CHIP_XY[1], scale=sc,
               opacity=ease('linear', (age + HALF) / F(2)))


def s6(t):
    cv = np.array(s6_static())
    ks = key_sprites()
    for n, c, lead in (('keycap_ctrl', CTRL_C, 1), ('keycap_s', S_C, 0)):
        lit, em = ks[n]
        dy, fl = key_press(t, PRESSES, lead)
        sc = 1.0 - 0.015 * dy / 16.0
        K.draw(cv, lit, c[0], c[1] + dy, scale=sc)
        K.draw(cv, em, c[0], c[1] + dy, scale=sc, mode='add', opacity=0.6 * (1.0 + 0.8 * fl) / 1.8)
    draw_chips(cv, t)
    return cv


# ================================================================================================ S7 candle macro / S7b
MACRO_WICK = (540.0, 1315.0)


@functools.lru_cache(maxsize=1)
def macro_wall():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cv = new(NIGHT_0)
    r2 = ((xx - 540.0) / 520.0) ** 2 + ((yy - 1180.0) / 640.0) ** 2
    pool = np.exp(-r2)[..., None]
    cv[..., :3] += pool * (AMBER * 0.030 + FLAME * 0.020)
    ind = np.clip(1.0 - pool[..., 0] * 1.6, 0, 1)[..., None] * (0.5 + 0.5 * (yy / H))[..., None]
    cv[..., :3] += ind * INDIGO * 0.35
    return ro(cv)


def s7_macro(t, lean=False):
    """S7a / S7c: the candle macro (flame 150 px on the wick at (540, 1315)); S7a's flame leans and recovers."""
    cv = np.array(macro_wall())
    g = candle_flicker(t)
    cv[..., :3] *= np.float32(0.85 + 0.15 * g)
    spr, (wx, wy) = candle_scaled(850.0)
    blit(cv, spr, MACRO_WICK[0] - wx, MACRO_WICK[1] - wy, gain=0.9 * g)
    rot = flame_sway(t, 0.5)
    if lean:
        rot += -14.0 * K.impulse(t, F(722), decay=5.0)
    draw_flame(cv, t, MACRO_WICK[0], MACRO_WICK[1], 150, gain=g, rot=rot)
    dx, dy, roll = drift(t, 0.5)
    return warp(cv, dx, dy, roll)


@functools.lru_cache(maxsize=1)
def wall_s7b():
    h, w = H, W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cv = np.zeros((h, w, 4), np.float32)
    cv[..., :3] = NIGHT_0
    cx, cy = BF.CANDLE_XY
    r2 = ((xx - cx) / 520.0) ** 2 + ((yy - cy - 60) / 640.0) ** 2
    pool = np.exp(-r2)[..., None]
    cv[..., :3] += pool * (AMBER * 0.030 + FLAME * 0.020)
    ind = np.clip(1.0 - pool[..., 0] * 1.6, 0, 1)[..., None] * (0.5 + 0.5 * (yy / h))[..., None]
    cv[..., :3] += ind * INDIGO * 0.35
    cv[..., 3] = 1.0
    return ro(cv)


@functools.lru_cache(maxsize=1)
def spark_seed(n=20, seed=31):
    rng = np.random.default_rng(seed)
    out = (rng.uniform(0, 1.6, n), rng.uniform(0.9, 1.5, n), rng.uniform(150, 230, n), rng.uniform(0, 2 * np.pi, n),
           rng.uniform(0.5, 1.0, n))
    for a in out:
        a.flags.writeable = False
    return out


def draw_sparks(cv, t, cam):
    """J.embers(20, seed=31)-style sparks from the S7b flame: each rises <= 240 px and is gone before y 850."""
    ph, life, rise, wob, br = spark_seed()
    period = 1.6
    age = (t - ph) % period
    alive = age < life
    if not alive.any():
        return
    k = age[alive] / life[alive]
    fx, fy = BF.CANDLE_XY
    dx, dy = BF.plate_shift(t, BF.Z_CANDLE)
    x = fx + dx + 18 * np.sin(wob[alive] + age[alive] * 3.0) * k
    y = fy - 40 + dy - rise[alive] * (1 - (1 - k) ** 1.6)
    b = (1 - k) ** 1.5 * br[alive] * (y > 860)
    cols = b[:, None] * (FLAME * 0.9 + AMBER * 0.6)[None, :] * 3.0
    splat(cv, x, y, cols, sigma=0.8)


def s7b(t):
    cam = BF.cam_s7b(t)
    cv = new(NIGHT_0)
    k = (BF.Z_WALL + BF.FOCAL) / BF.FOCAL
    K.draw_plane(cv, wall_s7b(), cam, (0.0, 0.0, BF.Z_WALL), K.W * k * 1.04)
    spr, (wx, wy) = candle_scaled(395.0)
    kz = (BF.Z_CANDLE + BF.FOCAL) / BF.FOCAL
    wick = (BF.CANDLE_XY[0], BF.CANDLE_XY[1] + 35.0)
    P = ((wick[0] - K.CX) * kz, (wick[1] - K.CY) * kz, BF.Z_CANDLE)
    g = candle_flicker(t)
    sp = spr.copy()
    sp[..., :3] *= np.float32(0.9 * g)
    K.draw_plane(cv, sp, cam, P, spr.shape[1] * kz, anchor=(wx / spr.shape[1], wy / spr.shape[0]))
    fl = flame_sprite(70)
    lay = np.zeros_like(cv)
    K.draw_plane(lay, fl, cam, P, fl.shape[1] * kz, anchor=(0.5, 0.62), rot=(0, 0, flame_sway(t)))
    cv[..., :3] += lay[..., :3] * np.float32(g)
    draw_sparks(cv, t, cam)
    BF.draw_s7b(cv, t, cam=cam, flicker=g)
    return cv


# ================================================================================================ S8a
def s8a(t):
    cam = BF.cam_s8a(t)
    st = room_state('S8a', t)
    plate = room_render(st, t)
    cv = new(NIGHT_0)
    k = (BF.Z_WALL + BF.FOCAL) / BF.FOCAL
    K.draw_plane(cv, plate, cam, (0.0, 0.0, BF.Z_WALL), K.W * k)
    BF.draw_s8a(cv, t, cam=cam, key=st['m'])
    return cv


def prewarm():
    room_static()
    led_sprite()
    for c in ('A', 'F'):
        led_col(c)
    crt_static(340, True)
    crt_static(560, False)
    s2_static()
    candle_sprites()
    candle_scaled(CANDLE2_H)
    candle_scaled(850.0)
    candle_scaled(395.0)
    pankhi_sprite()
    copy_sprite()
    s3_static()
    for r in (2.0, 2.2, 3.0, 4.5):
        bulb_sprite(r)
    s5_static()
    key_sprites()
    s6_static()
    macro_wall()
    wall_s7b()
    for hgt in (10, 18, 22, 44, 70, 120, 150):
        flame_sprite(hgt)
    for sel in (0.0, 1.0):
        chip_sprite('Saved', sel)
    chip_sprite('Saved · har 30 sec', 1.0)
    BF.prewarm()
