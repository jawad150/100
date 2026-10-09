"""faces.py - Jawad face/body asset helpers for the Reels Studio toolkit (core.py conventions).

    import sys
    sys.path[:0] = ['/home/user/100/pipeline/jawad_reels', '/home/user/100/workspace/brand_reels/charsheet/tools']
    import jawad_kit                              # FIRST (brand palette, looks 'ember' / 'noir_ember')
    from jawad_kit import K
    import faces as FA

    spr = FA.load('suit_shocked')                 # premultiplied LINEAR float32 (h, w, 4), read-only, cached
    dep = FA.depth('suit_shocked')                # float32 (h, w) 0..1, 1 = near (nose), edge-extended
    hero = FA.rim_light(spr, dep)                 # brand look: warm-dark subject + orange/red back-rim + halo
    K.draw(cv, hero, K.CX, K.H, anchor=(0.5, 1.0), scale=1.1)

Every function here is pure (returns a NEW sprite) -> build looks ONCE (functools.lru_cache), then draw per frame.
Colours are linear (K.hexlin), brand tokens from pipeline/jawad_reels/project.json: FLAME #FF6A1A, RED #F2312B,
EMBER #B3120E, AMBER #FFB547 (hot cores). No other client's looks or palette.
"""
import functools
import math
import os

import numpy as np
import cv2
import core as K

ROOT = '/home/user/100/workspace/brand_reels/charsheet'
CUT = os.path.join(ROOT, 'cutouts')

ORANGE = K.hexlin('#FF6A1A')     # FLAME: hero light, rims
RED = K.hexlin('#F2312B')        # RED: counter-rim / second accent
HOT = K.hexlin('#FFB547')        # AMBER: hot rim core
EMBER = K.hexlin('#B3120E')      # EMBER: fire depth

NAMES = ['street_fullbody_powerpose', 'street_threequarter_turn', 'street_smirk', 'street_sunglasses',
         'street_chinup_gaze', 'suit_fullbody', 'suit_neutral', 'suit_threequarter', 'suit_profile', 'suit_smirk',
         'suit_shocked', 'suit_confused', 'suit_smiling', 'suit_hand_on_chest']


# ------------------------------------------------------------------------------------------------ loading
def load(name, size=None, scale=None):
    """Cut-out sprite (2x upscaled, matted, decontaminated). size=(w, h) or width int; scale=float."""
    return K.load_image(os.path.join(CUT, name + '.png'), size=size, scale=scale)


@functools.lru_cache(maxsize=32)
def _depth_raw(name):
    d = cv2.imread(os.path.join(CUT, name + '_depth.png'), cv2.IMREAD_UNCHANGED)
    return (d.astype(np.float32) / 65535.0)


@functools.lru_cache(maxsize=32)
def meta(name):
    """cutouts/<name>.json: source crop, sizes, face_box / head_box / eyes / nose / mouth (cut-out px),
    open_sides, usable widths, quality numbers."""
    import json
    with open(os.path.join(CUT, name + '.json')) as f:
        return json.load(f)


def depth(name, shape=None):
    """0..1 relative depth, 1 = nearest. shape=(h, w) resizes (match a resized sprite)."""
    d = _depth_raw(name)
    if shape is not None and d.shape != tuple(shape[:2]):
        d = cv2.resize(d, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
    return d


def depth_like(name, plain, hero):
    """Depth map padded / cropped exactly like a look built from `plain` (edge-replicated), for parallax on
    the look itself."""
    d = depth(name, plain.shape)
    dx, dy = offset(plain, hero)
    H, W = hero.shape[:2]
    h, w = d.shape
    return cv2.copyMakeBorder(d, dy, H - h - dy, dx, W - w - dx, cv2.BORDER_REPLICATE)


def alpha_of(spr):
    return np.ascontiguousarray(spr[..., 3])


def unpremult(spr):
    a = spr[..., 3:4]
    return np.where(a > 1e-4, spr[..., :3] / np.maximum(a, 1e-4), 0.0).astype(np.float32)


def premult(rgb, a):
    out = np.empty(rgb.shape[:2] + (4,), np.float32)
    out[..., :3] = rgb * a[..., None]
    out[..., 3] = a
    return out


def bottom_fade(spr, frac=0.10, power=1.6):
    """Fade the bottom `frac` of a bust to transparent (headshot panels are cut flat at the jacket).
    Not needed when the bust is anchored to the frame bottom (anchor=(0.5, 1.0) at y=K.H)."""
    h = spr.shape[0]
    n = max(2, int(h * frac))
    k = np.ones(h, np.float32)
    k[h - n:] = np.linspace(1, 0, n, dtype=np.float32) ** power
    return spr * k[:, None, None]


# ------------------------------------------------------------------------------------------------ geometry
def normals(dep, alpha, strength=6.0, blur=2.0):
    """Screen-space surface normals from relative depth. Returns (nx, ny, nz) with nz>0 = toward camera,
    y DOWN (canvas convention). strength scales the depth relief (6 ~ a head; 3 flatter)."""
    d = cv2.GaussianBlur(dep, (0, 0), blur) if blur > 0 else dep
    s = strength * max(dep.shape) / 1000.0
    gx = cv2.Sobel(d, cv2.CV_32F, 1, 0, ksize=3) / 8.0 * s * 100
    gy = cv2.Sobel(d, cv2.CV_32F, 0, 1, ksize=3) / 8.0 * s * 100
    nx, ny, nz = gx, gy, np.ones_like(d)        # d = nearness: surface turns away where d drops -> n along +grad
    nx, ny = -nx, -ny
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx * inv, ny * inv, nz * inv


def edge_normals(alpha, sigma):
    """Outward 2D normals of the silhouette (unit), from the blurred alpha gradient."""
    b = cv2.GaussianBlur(alpha, (0, 0), sigma)
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3)
    m = np.sqrt(gx * gx + gy * gy) + 1e-6
    return -gx / m, -gy / m, b


# ------------------------------------------------------------------------------------------------ looks
def warm_dark(spr, exposure=0.42, warmth=(1.0, 0.80, 0.66), contrast=1.18, sat=0.85):
    """Low-key warm base grade (subject sits in a dark room, lit mostly by the back-rim)."""
    a = alpha_of(spr)
    c = unpremult(spr)
    y = K.lum(c)[..., None]
    c = y + (c - y) * sat
    c = np.power(np.clip(c, 0, None) / 0.18, contrast) * 0.18        # contrast pivot at mid grey (linear)
    c = c * np.asarray(warmth, np.float32) * exposure
    return premult(c.astype(np.float32), a)


def open_sides(spr, thresh=0.5):
    """Which image borders the subject is CUT by (panel crop): dict top/bottom/left/right -> bool.
    Headshots are cut at the bottom (and often the shoulders at left/right)."""
    a = spr[..., 3]
    k = max(2, a.shape[0] // 200)
    return {'top': bool(a[:k].max() > thresh), 'bottom': bool(a[-k:].max() > thresh),
            'left': bool(a[:, :k].max() > thresh), 'right': bool(a[:, -k:].max() > thresh)}


def _ext_alpha(spr, pad):
    """Alpha padded by `pad` px: replicated across cut (open) borders so they get no rim / halo,
    transparent elsewhere. Returns (a_ext, a_draw, sides)."""
    a = np.ascontiguousarray(spr[..., 3])
    sides = open_sides(spr)
    a_draw = cv2.copyMakeBorder(a, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a_ext = cv2.copyMakeBorder(a, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
    h, w = a.shape
    m = np.zeros_like(a_ext)
    m[pad:pad + h, pad:pad + w] = 1
    if sides['top']:
        m[:pad, pad:pad + w] = 1
    if sides['bottom']:
        m[pad + h:, pad:pad + w] = 1
    if sides['left']:
        m[pad:pad + h, :pad] = 1
    if sides['right']:
        m[pad:pad + h, pad + w:] = 1
    if sides['bottom'] and sides['left']:
        m[pad + h:, :pad] = 1
    if sides['bottom'] and sides['right']:
        m[pad + h:, pad + w:] = 1
    return a_ext * m, a_draw, sides


def _crop_open(out, pad, sides):
    """Drop the padding on cut borders so anchor=(.5, 1) still means 'bottom of the bust'."""
    y0 = pad if sides['top'] else 0
    y1 = out.shape[0] - (pad if sides['bottom'] else 0)
    x0 = pad if sides['left'] else 0
    x1 = out.shape[1] - (pad if sides['right'] else 0)
    return np.ascontiguousarray(out[y0:y1, x0:x1])


def halo(spr, color=None, sigmas=(6, 18, 48), strength=0.8, pad=None):
    """Emissive brand glow around the silhouette (alpha 0 -> plain 'over' adds light), none along cut
    borders. Returns a NEW sprite padded on the closed sides only (subject pixels included)."""
    color = (ORANGE * 0.6 + RED * 0.3) if color is None else np.asarray(color, np.float32)
    pad = int(pad if pad is not None else 3 * sigmas[-1])
    a_ext, a_draw, sides = _ext_alpha(spr, pad)
    out = K.pad(spr, pad)
    g = np.zeros_like(a_ext)
    for i, s in enumerate(sigmas):
        g += cv2.GaussianBlur(a_ext, (0, 0), s) * (0.55 ** i)
    out[..., :3] += (g * (1 - a_ext) * strength)[..., None] * color
    return _crop_open(out, pad, sides)


def rim_light(spr, dep=None, light=(0.75, -0.55), color=None, color2=None, hot=None, width=None, gain=2.4,
              back=0.5, outline=0.15, depth_wrap=0.3, halo_strength=0.55, halo_sigmas=(6, 18, 48), base=None,
              pad=None):
    """Brand rim: warm-dark subject + emissive orange back-rim on the silhouette (strongest on the `light`
    side; screen direction, y down), red counter-rim on the opposite side (`back`), a thin all-round outline,
    depth-normal wrap into cheeks / nose / jaw (needs dep), and an emissive outer halo. Cut panel borders
    (bust bottoms) get no rim and no halo. Returns a NEW sprite padded on the closed sides only, so
    anchor=(0.5, 1.0) is still the bottom of a bust; for full bodies use FA.feet_anchor(hero)."""
    color = ORANGE if color is None else np.asarray(color, np.float32)
    color2 = RED if color2 is None else np.asarray(color2, np.float32)
    hot = HOT if hot is None else np.asarray(hot, np.float32)
    h, w = spr.shape[:2]
    width = width or max(3.0, 0.005 * math.hypot(h, w))
    pad = int(pad if pad is not None else 3 * halo_sigmas[-1])
    a_ext, a, sides = _ext_alpha(spr, pad)
    sub = K.pad(warm_dark(spr) if base is None else base, pad)
    L = np.asarray(light, np.float32)
    L = L / (np.linalg.norm(L) + 1e-6)
    nx, ny, b = edge_normals(a_ext, width)
    face = nx * L[0] + ny * L[1]
    band = a * np.clip(1.0 - (b - 0.5) / 0.5, 0, 1) ** 1.5          # inner band, ~width px wide
    em = np.zeros(a.shape + (3,), np.float32)
    em += (band * np.clip(face, 0, 1) ** 0.8)[..., None] * (color * 0.7 + hot * 0.3)
    em += (band * np.clip(-face, 0, 1) ** 0.8 * back)[..., None] * color2
    em += (band * outline)[..., None] * color
    if dep is not None and depth_wrap > 0:
        d = cv2.copyMakeBorder(np.ascontiguousarray(dep, np.float32), pad, pad, pad, pad, cv2.BORDER_REPLICATE)
        Nx, Ny, Nz = normals(d, a)
        ndl = Nx * L[0] + Ny * L[1] - Nz * 0.55                       # light sits behind the subject
        near = cv2.GaussianBlur(band, (0, 0), width * 4) * 3.0           # wrap only close to the silhouette
        wrap = np.clip(ndl + 0.1, 0, 1) ** 2 * a * np.clip(near, 0, 1)
        em += (wrap * depth_wrap)[..., None] * color
    out = sub
    out[..., :3] += em * gain * np.sqrt(a)[..., None]
    if halo_strength > 0:
        g = np.zeros_like(a)
        for i, s in enumerate(halo_sigmas):
            g += cv2.GaussianBlur(a_ext, (0, 0), s) * (0.55 ** i)
        side = cv2.GaussianBlur(np.clip(face, 0, 1) * cv2.GaussianBlur(a_ext, (0, 0), 2) * (1 - a_ext), (0, 0),
                                halo_sigmas[1])
        side = side / max(float(side.max()), 1e-6)
        k = (1 - a_ext) * halo_strength
        out[..., :3] += (g * k)[..., None] * (color * 0.45 + color2 * 0.3) + (side * k)[..., None] * hot * 0.35
    return _crop_open(out, pad, sides)


def feet_anchor(spr, thresh=0.5):
    """anchor=(ax, ay) that puts the lowest solid pixel (feet) at the draw point, horizontally centred on
    the alpha bbox. e.g. K.draw(cv, hero, 540, 1860, scale=s, anchor=FA.feet_anchor(hero))"""
    bb = K.alpha_bbox(spr, thresh)
    return ((bb[0] + bb[2]) / 2.0 / spr.shape[1], bb[3] / spr.shape[0])


def duotone(spr, stops=None, contrast=1.15, glow=0.0):
    """Gradient map on perceptual luminance: black -> ember red -> red -> brand orange -> hot peach."""
    stops = stops or [(0.0, '#000000'), (0.30, '#3A0603'), (0.52, '#B3150A'), (0.74, '#FF4A1C'),
                      (0.92, '#FFA060'), (1.0, '#FFE2C4')]
    a = alpha_of(spr)
    c = unpremult(spr)
    y = K.to_srgb(np.clip(K.lum(c), 0, 1))
    y = np.clip((y - 0.5) * contrast + 0.5, 0, 1)
    xs = np.array([p for p, _ in stops], np.float32)
    cols = np.stack([K.hexlin(hx) for _, hx in stops]).astype(np.float32)
    rgb = np.stack([np.interp(y, xs, cols[:, i]) for i in range(3)], -1).astype(np.float32)
    out = premult(rgb, a)
    if glow > 0:
        out = halo(out, strength=glow, sigmas=(6, 20))
    return out


def halftone(spr, cell=9.0, angle=45.0, ink=None, paper=None, gamma=0.9):
    """Halftone dots in brand orange (size = local brightness) on near-black paper inside the silhouette."""
    ink = ORANGE * 1.4 if ink is None else np.asarray(ink, np.float32)
    paper = K.hexlin('#0D0201') if paper is None else np.asarray(paper, np.float32)
    a = alpha_of(spr)
    c = unpremult(spr)
    y = K.to_srgb(np.clip(K.lum(c), 0, 1)) ** gamma
    y = cv2.GaussianBlur(y.astype(np.float32), (0, 0), cell * 0.35)
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = math.radians(angle)
    u = xx * math.cos(r) + yy * math.sin(r)
    v = -xx * math.sin(r) + yy * math.cos(r)
    fu = (u / cell) - np.floor(u / cell) - 0.5
    fv = (v / cell) - np.floor(v / cell) - 0.5
    dist = np.sqrt(fu * fu + fv * fv) * cell                          # px from the cell centre
    rad = np.sqrt(np.clip(y, 0, 1)) * cell * 0.62
    dot = np.clip(rad - dist + 0.5, 0, 1)                             # anti-aliased disc
    hotmix = np.clip((y - 0.6) / 0.4, 0, 1)[..., None]
    col = ink * (1 - hotmix) + HOT * 1.3 * hotmix
    rgb = paper * (1 - dot[..., None]) + col * dot[..., None]
    return premult(rgb.astype(np.float32), a)


def cine_grade(spr, exposure=0.8, sat=0.82, contrast=0.65, toe=1.18, shadow=(1.0, 0.80, 0.70),
               high=(1.0, 0.93, 0.86)):
    """High-contrast cinematic warm grade: S-curve in display space with a toe (blacks stay black, never
    lifted), warm shadows/mids, peach-neutral highlights, mild desaturation. Skin stays natural."""
    a = alpha_of(spr)
    c = unpremult(spr) * exposure
    y = K.lum(c)[..., None]
    c = y + (c - y) * sat
    x = K.to_srgb(np.clip(c, 0, 1))
    x = x * (1 - contrast) + x * x * (3 - 2 * x) * contrast             # S-curve
    x = np.power(np.clip(x, 0, 1), toe)                              # toe: crush, never lift
    lin = K.to_lin(x)
    yl = np.clip(K.to_srgb(np.clip(K.lum(lin), 0, 1)), 0, 1)[..., None]
    tint = np.asarray(shadow, np.float32) * (1 - yl) + np.asarray(high, np.float32) * yl
    return premult((lin * tint).astype(np.float32), a)


# ------------------------------------------------------------------------------------------------ motion
def rigid_depth(dep, box, feather=None):
    """Flatten the depth inside `box` (x0, y0, x1, y1 px, e.g. meta 'head_box') to its median, feathered:
    the face then moves as ONE rigid plane (no warping of eyes / nose / mouth / jaw)."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    h, w = dep.shape
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    feather = feather or max(8, (x1 - x0) // 6)
    m = np.zeros_like(dep)
    m[y0:y1, x0:x1] = 1
    m = cv2.GaussianBlur(m, (0, 0), feather / 2.0)
    m = np.clip(m * 2.0, 0, 1)
    v = float(np.median(dep[y0:y1, x0:x1]))
    return dep * (1 - m) + v * m


def parallax(spr, dep, dx=0.0, dy=0.0, zoom=0.0, pivot=0.5, center=None, rigid_box=None):
    """2.5D move of a single photo: pixels shift by (dx, dy) * (depth - pivot) px and scale about `center`
    by zoom * (depth - pivot). Near parts move more than far parts. For portraits ALWAYS pass rigid_box
    (meta 'head_box'): the head moves as one plane and only torso / hair edges travel (never-uncanny rule).
    Limits: |dx|, |dy| <= 4 px at 1080 width (per shot, not per frame), |zoom| <= 0.02."""
    if rigid_box is not None:
        dep = rigid_depth(dep, rigid_box)
    dep = cv2.GaussianBlur(np.ascontiguousarray(dep, np.float32), (0, 0), 6)
    h, w = dep.shape
    cx, cy = center if center is not None else (w / 2.0, h / 2.0)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    def off(d):
        k = d - pivot
        return dx * k + (xx - cx) * zoom * k, dy * k + (yy - cy) * zoom * k
    ox, oy = off(dep)
    for _ in range(2):                                               # fixed-point: depth at the source
        dsrc = cv2.remap(dep, xx - ox, yy - oy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        ox, oy = off(dsrc)
    out = cv2.remap(np.ascontiguousarray(spr), xx - ox, yy - oy, cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return out


def idle(t, seed=0, breathe=0.004, sway=0.5, bob=3.0):
    """Puppet idle for a still: returns (dx, dy, rot_deg, (sx, sy)) to feed K.draw. Breathing scales y
    about the anchor, slow sway rotates, bob drifts. All pure functions of t."""
    br = math.sin(2 * math.pi * t / 3.4 + seed)
    return (K.wiggle(t, 0.18, bob, seed), K.wiggle(t, 0.15, bob * 0.6, seed + 7) - br * bob * 0.3,
            K.wiggle(t, 0.22, sway, seed + 3), (1.0 + breathe * 0.4 * br, 1.0 + breathe * br))


def swap_push(t, t_swap, amount=0.03, dur=0.9):
    """Scale for the NEW pose after a hard-cut expression swap on a beat: 1.00 -> 1.03 push-in (sells the cut).
    Never cross-dissolve two faces. Align eye centres (meta 'eyes') within 6 px on screen."""
    return 1.0 + amount * K.ramp(t, t_swap, t_swap + dur, 'out_cubic')


def eye_align(meta_a, meta_b, scale_a, scale_b, anchor_px_a):
    """Screen position for pose B so its eye midpoint lands where pose A's was. anchor_px_a = screen (x, y)
    where pose A's sprite (0, 0) corner sits. Returns screen (x, y) for pose B's (0, 0) corner."""
    ea = np.mean(np.asarray(meta_a['eyes'], np.float64), 0) * scale_a + np.asarray(anchor_px_a, np.float64)
    eb = np.mean(np.asarray(meta_b['eyes'], np.float64), 0) * scale_b
    return tuple(ea - eb)


# ------------------------------------------------------------------------------------------------ layout
def offset(spr, hero):
    """(dx, dy) of the plain cut-out's (0, 0) inside a padded look (rim_light / halo pad closed sides only).
    Point p in cut-out px (e.g. meta 'eye_mid') is at p + offset in the look."""
    sd = open_sides(spr)
    ew, eh = hero.shape[1] - spr.shape[1], hero.shape[0] - spr.shape[0]
    dx = 0 if sd['left'] else (ew if sd['right'] else ew // 2)
    dy = 0 if sd['top'] else (eh if sd['bottom'] else eh // 2)
    return dx, dy


def anchor_at(spr, hero, point):
    """K.draw anchor (fractions of `hero`) that pins cut-out pixel `point` (e.g. meta(name)['eye_mid'])."""
    dx, dy = offset(spr, hero)
    return ((point[0] + dx) / hero.shape[1], (point[1] + dy) / hero.shape[0])


def split_head(spr, m, off=(0, 0), feather=None):
    """Rigid head layer + torso layer (same size as spr) from meta head_box: the head (hair, ears, face,
    chin) as ONE plane, the torso keeps the neck under it so small relative moves (<= 4 px) never open a gap.
    off = FA.offset(plain, hero) when splitting a padded look."""
    x0, y0, x1, y1 = m['head_box']
    x0, x1, y0, y1 = x0 + off[0], x1 + off[0], y0 + off[1], y1 + off[1]
    h, w = spr.shape[:2]
    feather = feather or 0.08 * (x1 - x0)
    mk = np.zeros((h, w), np.float32)
    cy0 = int(max(0, y0 - 2 * feather))
    mk[cy0:int(y1), int(max(0, x0 - feather)):int(min(w, x1 + feather))] = 1
    mk = cv2.GaussianBlur(mk, (0, 0), feather / 2)
    head = spr * mk[..., None]
    return np.ascontiguousarray(head, np.float32), np.ascontiguousarray(spr, np.float32)


def contact_shadow(width, height=None, strength=0.55):
    """Soft dark ellipse for under the feet (full-body poses): draw with mode='over' at the feet line."""
    height = height or width * 0.12
    w, h = int(width * 1.6), int(height * 4)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (width / 2)) ** 2 + ((yy - h / 2) / (height / 2)) ** 2)
    a = np.clip(1 - r, 0, 1) ** 1.5 * strength
    a = cv2.GaussianBlur(a, (0, 0), height * 0.35)
    out = np.zeros((h, w, 4), np.float32)
    out[..., 3] = a
    return out


def fade_open(spr, sides=('left', 'right'), frac=0.12, power=1.5):
    """Soft fade toward the CUT borders (panel crops slice the shoulders flat): apply to the finished look
    (after rim_light / halo, so no rim is drawn along the fade). Only borders the subject really touches
    are faded; pass sides=('left', 'right', 'bottom') when the bust bottom is not hidden by the frame edge."""
    sd = open_sides(spr)
    h, w = spr.shape[:2]
    kx = np.ones(w, np.float32)
    ky = np.ones(h, np.float32)
    nx, ny = max(2, int(w * frac)), max(2, int(h * frac))
    ramp_x = np.linspace(0, 1, nx, dtype=np.float32) ** power
    ramp_y = np.linspace(0, 1, ny, dtype=np.float32) ** power
    if 'left' in sides and sd['left']:
        kx[:nx] *= ramp_x
    if 'right' in sides and sd['right']:
        kx[w - nx:] *= ramp_x[::-1]
    if 'top' in sides and sd['top']:
        ky[:ny] *= ramp_y
    if 'bottom' in sides and sd['bottom']:
        ky[h - ny:] *= ramp_y[::-1]
    return spr * (ky[:, None] * kx[None, :])[..., None]
