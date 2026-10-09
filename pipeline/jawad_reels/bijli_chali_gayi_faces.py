"""bijli_chali_gayi_faces.py - Jawad's 2.5D face shots for reel 2, C11 "Bijli Chali Gayi" (face-compositor).

Owner: face-compositor. The reel module imports this file and never edits it; this file never edits the shared toolkit.
Plan: BRIEF.md section 6.13 (two shots, suit wardrobe, no face-to-face swap, no mirroring); FACES.md (same folder as the
brief) gives the measured numbers and every deviation from the brief's wording with its reason.

    import jawad_kit                                   # FIRST (the reel module does this anyway)
    import bijli_chali_gayi_faces as BF
    BF.prewarm()                                       # builds both looks once per worker (~4 s)

    # S7b  f740-f839 (24.667-27.967 s): JD in profile by candlelight, look A rim; handheld "torch operator" drift
    cam = BF.cam_s7b(t)                                # the shot camera: render the WHOLE S7b world with it
    sc = K.Scene(cam) ; sc.plane(wall, (0, 0, BF.Z_WALL), ...) ; sc.plane(candle, ..., z=BF.Z_CANDLE) ...
    cv = sc.render(cv)                                 # (or 2D layers shifted by BF.plate_shift(t, z))
    BF.draw_s7b(cv, t, flicker=BF.candle_flicker(t))   # JD over the world: torso + rigid head planes, rim, wrap
    #   the candle flame of the world should use the same BF.candle_flicker(t) for its brightness (+-8 %)

    # S8a  f880-f919 (29.333-30.633 s): JD smiling in the lit room (power back), look A rim; camera LOCKED
    cv = <the lit room behind him, drawn through BF.cam_s8a()> ; BF.draw_s8a(cv, t, key=1.0)
    #   key = the tube light's state on that frame (0 = off, 1 = on); default 1.0 (mains snap on at f880)

    BF.jd_rect(t) / BF.head_rect(t) -> caption avoid rects (+28 px), None outside both shots
    BF.jd_alpha(t)                  -> (1920, 1080) float32 screen alpha of JD (QA masks), None outside
    BF.eye_screen(t)                -> screen (x, y) of the eye midpoint (eye-lock / QA)
    BF.FACES                        -> the shot table (t0, t1, pose, P, width, cam_keys, rim_dir, rim_gain, ...)
    python3 bijli_chali_gayi_faces.py check   -> limits, eye positions, parallax, texture, placement, cost (JSON)
    Preview + QA renders: bijli_chali_gayi_faces_preview.py (stand-in worlds, render.py-compatible).

Conventions: sprites are premultiplied LINEAR float32 (core.py); world x right, y DOWN, z away. World unit = 1 screen px
at the focus plane z = 0 (the profile's face / the smiling face), FOCAL px from the camera (85 mm look).
Assets: workspace/brand_reels/charsheet/cutouts/<pose>.png (Real-ESRGAN x4plus 2x masters, BiRefNet-portrait matte,
decontaminated, BSD-3 / MIT weights), <pose>_depth.png (Depth-Anything-V2-Small, Apache-2.0), <pose>.json (eyes, boxes).
Never-uncanny: the head (hair, ears, face, beard) is ONE rigid layer in every frame (no warp, no depth displacement on
the face); no blink, no lip motion, no morphs, no cross-dissolves, no mirroring; camera roll <= 0.3 deg, yaw = pitch = 0,
push 0; breathing <= 0.4 % on the torso layer only, compress-only (display scale never above 1.0 of the 2x master).
"""
import functools
import importlib.util
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                  # noqa: F401,E402  FIRST: brand palette, looks, house type
from jawad_kit import K                           # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

CS = '/home/user/100/workspace/brand_reels/charsheet'
CUT = os.path.join(CS, 'cutouts')
CROPS = os.path.join(CS, 'crops')

# faces.py (the charsheet helper library) imported BY PATH under a private name: its folder never lands on sys.path
_spec = importlib.util.spec_from_file_location('bcg_charsheet_faces', os.path.join(CS, 'tools', 'faces.py'))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

FPS = 30
HALF = 0.5 / FPS
LOOK = 'dusk'
POSE_A = 'suit_profile'                     # S7b hero (SLATE 3.2: faces screen-right toward the candle)
POSE_B = 'suit_smiling'                     # S8a power returns

S7B_F0, S7B_F1 = 740, 840                   # on screen f740..f839 (hard cut in at f740, out at f840)
S8A_F0, S8A_F1 = 880, 920                   # on screen f880..f919 (L4 bloom-out cut at f880, glue cut at f920)
S7B_T0, S7B_T1 = S7B_F0 / FPS, S7B_F1 / FPS
S8A_T0, S8A_T1 = S8A_F0 / FPS, S8A_F1 / FPS

# ---------------------------------------------------------------------------------------------------- camera / space
FOCAL = 3825.0          # 85 mm on the 24 mm frame width -> 1080 px (BRIEF 6.2: S7b and S8a are 85 mm MCUs)
APERTURE = 64.0         # pupil in world units (~f/3.5 at this scale): wall 1.45 m behind -> CoC r 16 px
DEPTH_UNITS = 1000.0    # world units per unit of relative depth (Depth-Anything-V2-Small, 1 = near): ~380 mm
Z_WALL = FOCAL          # suggested depth of the back wall / room plate (twice the subject distance)
Z_CANDLE = 150.0        # suggested depth of the S7b candle (just beyond his face plane, where he looks)
DRIFT_S7B = (4.0, 4.0 * 5.0 / 7.0, 0.3)   # BRIEF 6.9 drift (7, 5 px, 0.5 deg) capped at 4 px / 0.3 deg for S7b
CANDLE_XY = (800.0, 1130.0)               # S7b flame centre on screen (BRIEF 6.13); the face light is built for it
RIM_FALL = (310.0, 1.5)                   # S7b rim / glow falloff from the flame: radius of full strength (px), power

# ---------------------------------------------------------------------------------------------------- per-pose setup
# P = screen point of meta eye_mid at rest (BRIEF 6.13), scale 1.0 of the 2x master (the maximum allowed).
# NECK: head-layer boundary (cut-out px polyline, the head is everything ABOVE it: hair, ears, face, beard), read off
# the cut-outs on a 50 px grid: the collar / neck skin / shoulders go to the torso layer.
POSES = {
    POSE_A: dict(P=(440.0, 1210.0),
                 neck=[(0, 590), (110, 612), (230, 655), (320, 700), (420, 742), (560, 748), (710, 748)]),
    POSE_B: dict(P=(540.0, 1150.0),
                 neck=[(0, 548), (165, 560), (235, 630), (330, 668), (440, 664), (530, 592), (560, 556), (710, 548)]),
}
BREATH = 0.004          # torso vertical scale 1.000 -> 0.996 (compress-only), 0.29 Hz (period 3.4 s)
BREATH_PERIOD = 3.4
WRAP = {POSE_A: dict(width=14.0, sigma=30.0, amount=0.22),
        POSE_B: dict(width=16.0, sigma=30.0, amount=0.24)}

# look parameters (measured on the preview stills; FACES.md): exposure of the warm-dark base, light shape, rim
LOOK_A = dict(exposure=0.50, contrast=1.10, sat=0.90, amb_share=0.25, veil=0.0,
              hgrad=(0.40, 1.0), hpow=1.6, tint=(1.0, 0.86, 0.70), chest=(600.0, 1112.0, 0.35),
              rim=dict(light=(0.85, -0.15), gain=2.0, back=0.06, outline=0.02, depth_wrap=0.25),
              halo=0.30)
LOOK_B = dict(exposure=0.52, contrast=1.10, sat=0.92, amb_share=0.30, veil=0.0,
              key=(1.0, 0.72), tint=(1.0, 0.95, 0.88), chest=(600.0, 1122.0, 0.45),
              rim=dict(light=(-0.6, -0.8), gain=2.4, back=0.30, outline=0.05, depth_wrap=0.25),
              halo=0.35)


# ============================================================================================ helpers
def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def meta(name):
    return FA.meta(name)


# ============================================================================================ texture (human-realism)
# Real-ESRGAN x4plus gives these suit headshots crisp, real-looking pores, but on the cheeks its Laplacian variance is
# 6.7-7.2x a Lanczos 2x of the native crop (limit: within 1.5x). The SR detail is pulled back toward the native photo on
# SKIN ONLY (HSV skin mask inside the eroded matte, feathered 3 px): rgb = sr + (k - 1) (sr - lanczos2x) * skin, in
# float, stored at 16 bit. Eyes, brows, lashes, beard, hair and suit keep the full SR detail. k per pose puts both cheek
# patches inside 1.5x (profile 1.25 / 1.45, smiling 1.26 / 1.43); FACES.md has the table and the forehead numbers.
TEX_K = {POSE_A: 0.35, POSE_B: 0.25}
TEX_PATCHES = {POSE_A: {'cheek_meta': (487, 451, 537, 501), 'cheek_front': (430, 440, 500, 500),
                        'forehead': (470, 300, 540, 340)},
               POSE_B: {'cheek_meta': (275, 376, 337, 438), 'cheek_right': (420, 360, 490, 420),
                        'forehead': (300, 222, 420, 262)}}


@functools.lru_cache(maxsize=4)
def skin_mask(name):
    cut = cv2.imread(os.path.join(CUT, name + '.png'), cv2.IMREAD_UNCHANGED)
    a = cut[..., 3].astype(np.float32) / 255.0
    hsv = cv2.cvtColor(np.ascontiguousarray(cut[..., :3]), cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = (((h <= 22) | (h >= 170)) & (s > 35) & (s < 170) & (v > 95)).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    core = cv2.erode((a > 0.99).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    return _ro(cv2.GaussianBlur((skin * core).astype(np.float32), (0, 0), 3.0))


@functools.lru_cache(maxsize=4)
def rgb_used(name):
    """BGR float (0..255 sRGB) of the cut-out after the skin texture pull-back (what every look is built from)."""
    cut = cv2.imread(os.path.join(CUT, name + '.png'), cv2.IMREAD_UNCHANGED)
    sr = cut[..., :3].astype(np.float32)
    nat = cv2.imread(os.path.join(CROPS, name + '.png'))
    lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    k = TEX_K.get(name, 1.0)
    out = sr + (k - 1.0) * (sr - lz) * skin_mask(name)[..., None]
    return _ro(np.clip(out, 0, 255))


@functools.lru_cache(maxsize=4)
def plain(name):
    """Premultiplied linear cut-out (2x master, straight alpha as matted) with the skin texture pull-back."""
    cut = cv2.imread(os.path.join(CUT, name + '.png'), cv2.IMREAD_UNCHANGED)
    rgba = np.empty(cut.shape, np.uint16)
    rgba[..., :3] = np.round(rgb_used(name)[..., ::-1] * 257.0).astype(np.uint16)
    rgba[..., 3] = cut[..., 3].astype(np.uint16) * 257
    return _ro(K.sprite(rgba))


def _neck_mask(name, H, W, off, feather=9.0):
    """Head-layer mask (padded layer px): 1 above the neck polyline, feathered, 0 below."""
    pts = [(x + off[0], y + off[1]) for x, y in POSES[name]['neck']]
    pts = [(-200.0, pts[0][1])] + pts + [(W + 200.0, pts[-1][1])]
    poly = np.array([(-200.0, -200.0)] + pts + [(W + 200.0, -200.0)], np.float64)
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(poly * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
    m = m.astype(np.float32) / 255.0
    return np.clip(cv2.GaussianBlur(m, (0, 0), feather), 0, 1)


def _side_halo(spr, light, color, strength, sigmas=(5, 16, 44), pad=None):
    """Emissive glow OUTSIDE the silhouette on the lit side only (the flame / tube scattering at the lit edge, bloomed
    by the lens), none along the panel-cut borders. Same padding rules as FA.rim_light. Returns emission (h, w, 3)
    for the padded frame, alpha 0."""
    pad = int(pad if pad is not None else 3 * sigmas[-1])
    a_ext, a, sides = FA._ext_alpha(spr, pad)
    L = np.asarray(light, np.float32)
    L = L / (np.linalg.norm(L) + 1e-6)
    nx, ny, b = FA.edge_normals(a_ext, 3.0)
    face = np.clip(nx * L[0] + ny * L[1], 0, 1)
    src = face * cv2.GaussianBlur(a_ext, (0, 0), 2) * (1 - a_ext)
    g = np.zeros_like(a)
    for i, s in enumerate(sigmas):
        g += cv2.GaussianBlur(src, (0, 0), s) * (0.6 ** i)
    g = g / max(float(g.max()), 1e-6) * (1 - a_ext)
    em = np.zeros(a.shape + (4,), np.float32)
    em[..., :3] = g[..., None] * np.asarray(color, np.float32) * strength
    return FA._crop_open(em, pad, sides)


# ============================================================================================ looks (built once)
def _shade_A(name, h, w):
    """S7b candle light in cut-out px: horizontal multiply 0.55 (back of the head) -> 1.0 (face front) toward the
    flame at screen-right eye height (BRIEF 6.13), warm tint (1.0, 0.86, 0.70) weighted to the lit side, and the chest
    falling off below the collar (the flame is at eye height). 2D only: never a depth relight."""
    m = meta(name)
    hx0 = m['head_box'][0] - 250.0           # back of the hair (the YuNet head box is face-centred)
    fx1 = m['face_box'][2]                   # face front (nose tip side)
    g0, g1 = LOOK_A['hgrad']
    xs = np.arange(w, dtype=np.float32)
    s = g0 + (g1 - g0) * _smooth((xs - hx0) / (fx1 - hx0)) ** LOOK_A['hpow']
    ys = np.arange(h, dtype=np.float32)
    c0, c1, cmin = LOOK_A['chest']
    v = 1.0 - (1.0 - cmin) * _smooth((ys - c0) / (c1 - c0))
    shade = s[None, :] * v[:, None]
    wlit = ((s - g0) / (g1 - g0))[None, :] * np.ones((h, 1), np.float32)
    tint = 1.0 + wlit[..., None] * (np.asarray(LOOK_A['tint'], np.float32) - 1.0)
    return shade[..., None] * tint


def _shade_B(name, h, w):
    """S8a tube light from top-left: a soft diagonal across the head (1.0 toward the tube -> 0.72 at the far jaw),
    warm-white tint, chest falling off below the collar (the light is aimed at the face). 2D only."""
    m = meta(name)
    x0, y0, x1, y1 = m['head_box']
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = np.float32([-0.6, -0.8])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    proj = ((xx - cx) * L[0] + (yy - cy) * L[1]) / (0.5 * math.hypot(x1 - x0, y1 - y0))
    k1, k0 = LOOK_B['key']
    s = k0 + (k1 - k0) * _smooth(proj * 0.5 + 0.5)
    c0, c1, cmin = LOOK_B['chest']
    v = 1.0 - (1.0 - cmin) * _smooth((yy - c0) / (c1 - c0))
    return (s * v)[..., None] * np.asarray(LOOK_B['tint'], np.float32)


@functools.lru_cache(maxsize=2)
def layers(name):
    """Build a pose's look once: ambient + key (light) parts, look A rim + side halo as emission (key part), panel-cut
    sides faded, then split into a rigid HEAD layer and a breathing TORSO layer (exact recombination at rest).
    Returns a dict of read-only arrays + geometry (padded-layer px)."""
    L = LOOK_A if name == POSE_A else LOOK_B
    p = plain(name)
    m = meta(name)
    dep = FA.depth(name)
    h, w = p.shape[:2]
    a = np.ascontiguousarray(p[..., 3])
    base = FA.warm_dark(p, exposure=L['exposure'], warmth=(1.0, 1.0, 1.0), contrast=L['contrast'], sat=L['sat'])
    shade = (_shade_A if name == POSE_A else _shade_B)(name, h, w)
    lit = base.copy()
    lit[..., :3] *= shade
    amb = lit.copy()
    amb[..., :3] *= L['amb_share']
    if L['veil']:
        amb[..., :3] += np.asarray(K.C['NIGHT_0'], np.float32) * L['veil'] * a[..., None]
    key = lit * np.float32(1.0 - L['amb_share'])
    key[..., 3] = 0.0
    zero = FA.premult(np.zeros((h, w, 3), np.float32), a)
    r = L['rim']
    rim = FA.rim_light(p, dep, light=r['light'], gain=r['gain'], back=r['back'], outline=r['outline'],
                       depth_wrap=r['depth_wrap'], halo_strength=0.0, base=zero)            # emission + alpha
    dx, dy = FA.offset(p, rim)
    H, W = rim.shape[:2]
    hcol = FA.HOT * 0.55 + FA.ORANGE * 0.45
    halo = _side_halo(p, r['light'], hcol, L['halo'], pad=3 * 48)    # FA.rim_light's default pad
    if halo.shape[:2] != (H, W):
        raise RuntimeError('halo / rim padding mismatch %s %s' % (halo.shape, rim.shape))

    def padto(s):
        o = np.zeros((H, W, 4), np.float32)
        o[dy:dy + h, dx:dx + w] = s
        return o
    ambP = padto(amb)
    keyP = padto(key)
    em = rim[..., :3] + halo[..., :3]
    if name == POSE_A:
        # the candle is a point source at eye height: its rim / glow fall off with distance from the flame
        # (softened inverse square, 1.0 within RIM_FALL[0] px): quiff front ~0.7, hair top ~0.3, chest edge ~0.3
        P = POSES[name]['P']
        fx = CANDLE_XY[0] - P[0] + m['eye_mid'][0] + dx
        fy = CANDLE_XY[1] - P[1] + m['eye_mid'][1] + dy
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt((xx - fx) ** 2 + (yy - fy) ** 2)
        r0, pw = RIM_FALL
        em *= np.clip((r0 / np.maximum(r, r0)) ** pw, 0, 1)[..., None]
    keyP[..., :3] += em
    plainP = padto(p)
    # fade the panel-cut sides exactly as FA.fade_open (frac 0.12, power 1.5), after the look (no rim along the
    # fade), on every layer alike; the bust bottoms sit below the frame
    sd = FA.open_sides(plainP)
    kx = np.ones(W, np.float32)
    nfx = max(2, int(W * 0.12))
    ramp = np.linspace(0, 1, nfx, dtype=np.float32) ** 1.5
    if sd['left']:
        kx[:nfx] *= ramp
    if sd['right']:
        kx[W - nfx:] *= ramp[::-1]
    for s in (ambP, keyP, plainP):
        s *= kx[None, :, None]
    # rigid head / breathing torso split; torso weight wt so that head over torso == the whole at rest
    mk = _neck_mask(name, H, W, (dx, dy))
    al = ambP[..., 3]
    den = 1.0 - mk * al
    wt = np.where(den > 1e-4, (1.0 - mk) / np.maximum(den, 1e-4), 0.0).astype(np.float32)
    out = dict(off=(dx, dy), shape=(H, W), eye=(m['eye_mid'][0] + dx, m['eye_mid'][1] + dy),
               bottom=float(dy + h), neck_y=float(max(y for _, y in POSES[name]['neck']) + dy))
    for nm, src in (('amb', ambP), ('key', keyP), ('plain', plainP)):
        out[nm + '_head'] = _ro(src * mk[..., None])
        out[nm + '_torso'] = _ro(src * wt[..., None])
    out['plain'] = _ro(plainP)
    hd = FA.depth(name)
    hm = _neck_mask(name, h, w, (0, 0)) > 0.5
    am = a > 0.9
    zh = float(np.median(hd[hm & am]))
    zt = float(np.median(hd[(~hm) & am]))
    out['z_head'] = 0.0                                          # focus plane: the eyes
    out['z_torso'] = -(zt - zh) * DEPTH_UNITS                    # depth map: the torso sits nearer than the head
    out['depth_med'] = (round(zh, 3), round(zt, 3))
    return out


@functools.lru_cache(maxsize=1)
def _alpha_layers():
    out = {}
    for n in (POSE_A, POSE_B):
        Ls = layers(n)
        for part in ('head', 'torso'):
            s = Ls['plain_' + part]
            o = np.zeros_like(s)
            o[..., :3] = s[..., 3:4]
            o[..., 3] = s[..., 3]
            out[(n, part)] = _ro(o)
    return out


# ============================================================================================ cameras and motion
def drift_s7b(t):
    """(dx, dy, roll_deg) of the S7b handheld drift: BRIEF 6.9 drift (wiggle 0.35 Hz 7 px, 0.30 Hz 5 px, roll 0.25 Hz
    0.5 deg, seeds 11/12/13) scaled to the S7b cap 4 px / 0.3 deg. The power is off for all of S7b (A(t) = 1)."""
    ax, ay, ar = DRIFT_S7B
    return K.wiggle(t, 0.35, ax, 11), K.wiggle(t, 0.30, ay, 12), K.wiggle(t, 0.25, ar, 13)


def cam_s7b(t):
    """The S7b shot camera (render the whole S7b world with it): translation drift + roll, no yaw / pitch / push.
    Focus on z = 0 (his eyes); aperture 64 -> the wall at Z_WALL gets a CoC radius of ~16 px."""
    dx, dy, roll = drift_s7b(t)
    return K.Cam(pos=(-dx, -dy, -FOCAL), roll=roll, focal=FOCAL, aperture=APERTURE, focus_dist=FOCAL)


def cam_s8a(t=None):
    """The S8a camera: LOCKED (power on). Same lens and focus as S7b."""
    return K.Cam(pos=(0.0, 0.0, -FOCAL), focal=FOCAL, aperture=APERTURE, focus_dist=FOCAL)


def plate_shift(t, z):
    """For a 2D-drawn S7b layer at depth z (world units, 0 = his face): the screen offset (dx, dy) to apply so it moves
    exactly as a plane at that depth under cam_s7b(t) (roll is not included: draw through cam_s7b for roll)."""
    dx, dy, _ = drift_s7b(t)
    k = FOCAL / (FOCAL + z)
    return dx * k, dy * k


def candle_flicker(t):
    """Candle light level (BRIEF 6.9: flicker +-8 %, sway noise at 1.5 / 4 Hz, no frame-to-frame boiling). The
    world's flame should use the same function so the light on his face tracks the flame."""
    v = 0.75 * K.wiggle(t, 1.5, 1.0, 41) + 0.25 * K.wiggle(t, 4.0, 1.0, 42)
    return 1.0 + 0.08 * max(-1.0, min(1.0, v))


def breath(t, t0):
    """Torso vertical scale: 1.0 at the shot start, compress-only to 1 - BREATH (exhale), 0.29 Hz."""
    return 1.0 - BREATH * (0.5 - 0.5 * math.cos(2 * math.pi * (t - t0) / BREATH_PERIOD))


def _pose_at(t):
    if S7B_T0 - HALF <= t < S7B_T1 - HALF:
        return POSE_A, S7B_T0
    if S8A_T0 - HALF <= t < S8A_T1 - HALF:
        return POSE_B, S8A_T0
    return None, None


def _geometry(name, t, t0, cam):
    """World placement of the two layers (fixed in the world; the camera moves). Returns a dict with the draw_plane
    arguments of the head and torso layers and the breathing state."""
    Ls = layers(name)
    H, W = Ls['shape']
    ex, ey = Ls['eye']
    P = POSES[name]['P']
    sy = breath(t, t0)
    bot = Ls['bottom']
    lift = (1.0 - sy) * (bot - Ls['neck_y'])                       # the head rides the breathing neck (down)

    def unproject(sx, sy_, z):
        k = (z + FOCAL) / FOCAL
        return np.array([(sx - K.CX) * k, (sy_ - K.CY) * k, z])
    zt, zh = Ls['z_torso'], Ls['z_head']
    # torso: anchored at the bust bottom below the eye column, height scaled by the breath about that line
    tb = (P[0], P[1] + (bot - ey))
    torso = dict(center=unproject(tb[0], tb[1], zt), width=W * (zt + FOCAL) / FOCAL,
                 height=H * (zt + FOCAL) / FOCAL * sy, anchor=(ex / W, 1.0))
    head = dict(center=unproject(P[0], P[1] + lift, zh), width=W * (zh + FOCAL) / FOCAL,
                height=H * (zh + FOCAL) / FOCAL, anchor=(ex / W, ey / H))
    return dict(torso=torso, head=head, sy=sy, lift=lift)


def _wrap(cv, lay, bg, region, width, sigma, amount):
    """Light wrap: blur the background behind the subject and SCREEN it over the subject's outer `width` px."""
    x0, y0, x1, y1 = region
    a = lay[y0:y1, x0:x1, 3]
    if a.max() <= 0.01:
        return
    k = max(1, int(round(width)))
    inner = cv2.erode(a, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * k + 1, 2 * k + 1)))
    band = cv2.GaussianBlur(np.clip(a - inner, 0, 1), (0, 0), max(0.8, width * 0.35)) * a
    q = 4
    h, w = bg.shape[:2]
    small = cv2.resize(np.ascontiguousarray(bg[..., :3]), (max(1, w // q), max(1, h // q)),
                       interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(small, (0, 0), sigma / q), (w, h), interpolation=cv2.INTER_LINEAR)
    rgb = cv[y0:y1, x0:x1, :3]
    rgb += (amount * band)[..., None] * np.clip(bl, 0, 1) * (1.0 - np.clip(rgb, 0, 1))


def _region(bb, pad, shape):
    x0, y0, x1, y1 = bb
    return (max(0, int(x0) - pad), max(0, int(y0) - pad), min(shape[1], int(x1) + pad), min(shape[0], int(y1) + pad))


def _draw(cv, name, t, t0, cam, gain, mode):
    Ls = layers(name)
    G = _geometry(name, t, t0, cam)
    if mode == 'full':
        torso = Ls['amb_torso'] + np.float32(gain) * Ls['key_torso']
        head = Ls['amb_head'] + np.float32(gain) * Ls['key_head']
    elif mode == 'plain':
        torso, head = Ls['plain_torso'], Ls['plain_head']
    elif mode == 'alpha':
        al = _alpha_layers()
        torso, head = al[(name, 'torso')], al[(name, 'head')]
    else:
        raise ValueError(mode)
    lay = np.zeros_like(cv)
    bbs = []
    for spr, g in ((torso, G['torso']), (head, G['head'])):           # photo occlusion order: head over torso
        info = K.draw_plane(lay, spr, cam, g['center'], g['width'], height=g['height'], anchor=g['anchor'],
                            dof=(mode == 'full'))
        if info is not None:
            bbs.append(info['bbox'])
    if not bbs:
        return None
    bb = (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs), max(b[3] for b in bbs))
    wr = WRAP[name]
    reg = _region(bb, int(wr['sigma'] * 2), cv.shape)
    x0, y0, x1, y1 = reg
    bg = cv[y0:y1, x0:x1].copy() if mode == 'full' else None
    a = lay[y0:y1, x0:x1, 3:4]
    cv[y0:y1, x0:x1] = lay[y0:y1, x0:x1] + cv[y0:y1, x0:x1] * (1.0 - a)
    if mode == 'full':
        _wrap(cv, lay, bg, reg, **wr)
    return bb


# ============================================================================================ public draw calls
def draw_s7b(cv, t, cam=None, flicker=None, mode='full'):
    """S7b: JD in profile by candlelight over the world already in cv (drawn with cam_s7b(t)). In place.
    flicker: candle light level (default candle_flicker(t)) on the candle-lit part (key + rim + halo; 75 %).
    mode 'full' | 'plain' (cut-out only: matte QA) | 'alpha' (white silhouette). Returns the touched bbox."""
    cam = cam if cam is not None else cam_s7b(t)
    g = candle_flicker(t) if flicker is None else float(flicker)
    return _draw(cv, POSE_A, t, S7B_T0, cam, g, mode)


def draw_s8a(cv, t, cam=None, key=1.0, mode='full'):
    """S8a: JD smiling in the lit room over the world already in cv (drawn with cam_s8a()). In place.
    key: tube-light level on his key / rim (0 off .. 1 on; mains snap, never fade). Returns the touched bbox."""
    cam = cam if cam is not None else cam_s8a(t)
    return _draw(cv, POSE_B, t, S8A_T0, cam, float(key), mode)


def draw(cv, t, mode='full', **kw):
    """Draw whichever face shot is on screen at time t (by the frame rule: frame k shows the pose whose window holds
    k); no-op outside both shots. Returns the bbox or None."""
    name, t0 = _pose_at(t)
    if name == POSE_A:
        return draw_s7b(cv, t, mode=mode, **kw)
    if name == POSE_B:
        return draw_s8a(cv, t, mode=mode, **kw)
    return None


def _project_pts(name, t, t0, cam, uv_pts, layer='head'):
    """Screen px of cut-out pixels (head or torso layer) at time t."""
    Ls = layers(name)
    G = _geometry(name, t, t0, cam)
    g = G[layer]
    dx, dy = Ls['off']
    H, W = Ls['shape']
    uv = np.array([[(u + dx) / W, (v + dy) / H] for u, v in uv_pts], np.float64)
    Pw = K.plane_point(g['center'], g['width'], g['height'], uv=uv, anchor=g['anchor'])
    xy, _ = cam.project(np.atleast_2d(Pw))
    return xy


def _cam_at(name, t):
    return cam_s7b(t) if name == POSE_A else cam_s8a(t)


def eye_screen(t):
    """Screen (x, y) of the eye midpoint (meta eye_mid) at time t, or None outside both shots."""
    name, t0 = _pose_at(t)
    if name is None:
        return None
    xy = _project_pts(name, t, t0, _cam_at(name, t), [meta(name)['eye_mid']])
    return float(xy[0, 0]), float(xy[0, 1])


def jd_rect(t, margin=28):
    """Caption avoid rect of JD's whole silhouette (subject bbox + margin, clipped), or None outside his shots."""
    name, t0 = _pose_at(t)
    if name is None:
        return None
    x0, y0, x1, y1 = meta(name)['subject_bbox']
    cam = _cam_at(name, t)
    xy = np.vstack([_project_pts(name, t, t0, cam, [(x0, y0), (x1, y0)], 'head'),
                    _project_pts(name, t, t0, cam, [(x0, y1), (x1, y1)], 'torso')])
    return (max(0, int(math.floor(xy[:, 0].min() - margin))), max(0, int(math.floor(xy[:, 1].min() - margin))),
            min(K.W, int(math.ceil(xy[:, 0].max() + margin))), min(K.H, int(math.ceil(xy[:, 1].max() + margin))))


def head_rect(t, margin=28):
    """Caption avoid rect of the head (meta head_box widened to the back of the hair for the profile) + margin."""
    name, t0 = _pose_at(t)
    if name is None:
        return None
    x0, y0, x1, y1 = meta(name)['head_box']
    if name == POSE_A:
        x0 = 20.0                                                   # the profile's hair reaches x ~25 (cut-out px)
    sb = meta(name)['subject_bbox']
    y0 = min(y0, sb[1])
    xy = _project_pts(name, t, t0, _cam_at(name, t), [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    return (max(0, int(math.floor(xy[:, 0].min() - margin))), max(0, int(math.floor(xy[:, 1].min() - margin))),
            min(K.W, int(math.ceil(xy[:, 0].max() + margin))), min(K.H, int(math.ceil(xy[:, 1].max() + margin))))


def jd_alpha(t):
    """(1920, 1080) float32 screen alpha of JD at time t (the cut-out matte, no glow), or None outside his shots."""
    name, t0 = _pose_at(t)
    if name is None:
        return None
    cv = np.zeros((K.H, K.W, 4), np.float32)
    _draw(cv, name, t, t0, _cam_at(name, t), 1.0, 'alpha')
    return cv[..., 3].copy()


def prewarm():
    layers(POSE_A)
    layers(POSE_B)
    _alpha_layers()


# ============================================================================================ the shot table
FACES = [
    dict(t0=S7B_T0, t1=S7B_T1, f0=S7B_F0, f1=S7B_F1 - 1, shot='S7b', pose=POSE_A, look='A rim (candle)',
         P=POSES[POSE_A]['P'], width=710, scale=1.0,
         cam_keys=dict(fn='cam_s7b', drift_px=DRIFT_S7B[:2], roll_deg=DRIFT_S7B[2], yaw=0, pitch=0, push=0,
                       focal=FOCAL, aperture=APERTURE, focus='z=0 (eyes)'),
         rim_dir=LOOK_A['rim']['light'], rim_gain=LOOK_A['rim']['gain'], swap_on_beat=False,
         layers='torso (z from depth, breathes 0.4 % compress-only) + rigid head (z=0, rides the neck)',
         note='faces screen-right toward the candle flame at %s; candle light = horizontal multiply 0.55 -> 1.0 + warm '
              'tint (1.0, 0.86, 0.70) on the lit side + chest falloff, flicker +-8 %% (candle_flicker) on the lit '
              'part; never a depth relight; side halo on the lit edge only; light wrap from the world' % (CANDLE_XY,)),
    dict(t0=S8A_T0, t1=S8A_T1, f0=S8A_F0, f1=S8A_F1 - 1, shot='S8a', pose=POSE_B, look='A rim (tube + CRT)',
         P=POSES[POSE_B]['P'], width=710, scale=1.0,
         cam_keys=dict(fn='cam_s8a', locked=True, push=0, focal=FOCAL, aperture=APERTURE),
         rim_dir=LOOK_B['rim']['light'], rim_gain=LOOK_B['rim']['gain'], swap_on_beat=False,
         layers='torso (z from depth, breathes compress-only) + rigid head (z=0)',
         note='appears on the L4 cut f880 (bar 11 downbeat; no dissolve); tube light top-left key (key=), CRT glow '
              'behind the head as rim (light wrap from the room + RED counter-rim); shoulders faded at the panel cuts'),
]


# ============================================================================================ checks
def _lap_var(img_bgr_f, box):
    x0, y0, x1, y1 = box
    g = cv2.cvtColor(img_bgr_f.astype(np.float32), cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
    return float(cv2.Laplacian(g, cv2.CV_32F).var())


def texture_report():
    """Laplacian variance (float luma) of the SR cut-out and of the texture-corrected sprite, each vs a Lanczos 2x of
    the native crop (rule: cheeks within 1.5x), on two cheek patches and a forehead patch per pose (cut-out px)."""
    out = {}
    for n, pp in TEX_PATCHES.items():
        cut = cv2.imread(os.path.join(CUT, n + '.png'), cv2.IMREAD_UNCHANGED)[..., :3].astype(np.float32)
        nat = cv2.imread(os.path.join(CROPS, n + '.png'))
        lz = cv2.resize(nat, (cut.shape[1], cut.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        used = rgb_used(n)
        res = {'k_skin': TEX_K.get(n, 1.0)}
        for k, b in pp.items():
            res[k] = dict(box=list(b), sr_vs_lanczos=round(_lap_var(cut, b) / _lap_var(lz, b), 2),
                          used_vs_lanczos=round(_lap_var(used, b) / _lap_var(lz, b), 2),
                          skin_mask_mean=round(float(skin_mask(n)[b[1]:b[3], b[0]:b[2]].mean()), 2))
        out[n] = res
    return out


def _check():
    out = {}
    for name, t0, t1 in ((POSE_A, S7B_T0, S7B_T1), (POSE_B, S8A_T0, S8A_T1)):
        Ls = layers(name)
        m = meta(name)
        f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
        ts = [f / FPS for f in range(f0, f1)]
        P = np.array(POSES[name]['P'])
        eye = np.array([_project_pts(name, t, t0, _cam_at(name, t), [m['eye_mid']])[0] for t in ts])
        dev = np.linalg.norm(eye - P, axis=1)
        H, W = Ls['shape']
        dx, dy = Ls['off']
        # bust bottom: the lowest row of the torso layer, both ends of the on-screen part
        bl = np.array([_project_pts(name, t, t0, _cam_at(name, t), [(-dx, Ls['bottom'] - dy - 0.01),
                                                                    (W - dx, Ls['bottom'] - dy - 0.01)], 'torso')
                       for t in ts])
        ex_l = (0 - P[0]) + m['eye_mid'][0]                          # cut-out x at the left frame edge
        ex_r = (K.W - P[0]) + m['eye_mid'][0]
        bot_on = np.array([_project_pts(name, t, t0, _cam_at(name, t),
                                        [(max(-dx, ex_l), Ls['bottom'] - dy - 0.01),
                                         (min(W - dx, ex_r), Ls['bottom'] - dy - 0.01)], 'torso')
                           for t in ts])
        # per-layer screen motion (px / frame) and head-to-plate parallax (px / s)
        def track(fn):
            return np.array([fn(t) for t in ts])
        head_pt = track(lambda t: _project_pts(name, t, t0, _cam_at(name, t), [m['eye_mid']], 'head')[0])
        torso_pt = track(lambda t: _project_pts(name, t, t0, _cam_at(name, t),
                                                [(m['eye_mid'][0], m['subject_bbox'][3] - 150)], 'torso')[0])
        G0 = _geometry(name, t0, t0, _cam_at(name, t0))
        res = {}
        for zn, z in (('candle (z=%d)' % Z_CANDLE, Z_CANDLE), ('wall (z=%d)' % Z_WALL, Z_WALL)):
            Pw = np.array([(P[0] - K.CX) * (z + FOCAL) / FOCAL, (P[1] - K.CY) * (z + FOCAL) / FOCAL, z])
            pl = track(lambda t: _cam_at(name, t).project(Pw[None])[0][0])
            rel = head_pt - pl
            v = np.linalg.norm(np.diff(rel, axis=0), axis=1) * FPS
            res[zn] = dict(peak_px_s=round(float(v.max()), 2), pct_width_s=round(float(v.max()) / K.W * 100, 3),
                           peak_px_frame=round(float(v.max()) / FPS, 3),
                           range_px=round(float(np.ptp(rel, axis=0).max()), 2))
        hv = np.linalg.norm(np.diff(head_pt, axis=0), axis=1)
        tv = np.linalg.norm(np.diff(torso_pt, axis=0), axis=1)
        ht = np.linalg.norm(np.diff(head_pt - torso_pt, axis=0), axis=1)
        dr = np.array([drift_s7b(t) for t in ts]) if name == POSE_A else np.zeros((len(ts), 3))
        out[name] = dict(
            frames=(f0, f1 - 1), seconds=round((f1 - f0) / FPS, 3), P=P.tolist(),
            eye_mid_first=[round(v, 2) for v in eye[0]], eye_mid_last=[round(v, 2) for v in eye[-1]],
            eye_dev_from_P_max_px=round(float(dev.max()), 2),
            bust_bottom_min_y_onscreen=round(float(bot_on[:, :, 1].min()), 1),
            bust_bottom_rest=[round(float(v), 1) for v in bl[0, :, 1]],
            head_speed_peak_px_frame=round(float(hv.max()), 3), torso_speed_peak_px_frame=round(float(tv.max()), 3),
            head_vs_torso_peak_px_frame=round(float(ht.max()), 3),
            parallax_head_vs=res,
            drift_max=dict(dx=round(float(np.abs(dr[:, 0]).max()), 2), dy=round(float(np.abs(dr[:, 1]).max()), 2),
                           roll_deg=round(float(np.abs(dr[:, 2]).max()), 3)),
            breath_min_scale=round(min(breath(t, t0) for t in ts), 5),
            z_head=Ls['z_head'], z_torso=round(Ls['z_torso'], 1), depth_medians_head_torso=Ls['depth_med'],
            display_scale_head=round(float(G0['head']['width'] * FOCAL / (FOCAL + Ls['z_head']) / W), 5),
            display_scale_torso=round(float(G0['torso']['width'] * FOCAL / (FOCAL + Ls['z_torso']) / W), 5),
            coc_px=dict(head=round(float(_cam_at(name, t0).coc(FOCAL + Ls['z_head'])), 2),
                        torso=round(float(_cam_at(name, t0).coc(FOCAL + Ls['z_torso'])), 2),
                        wall=round(float(_cam_at(name, t0).coc(FOCAL + Z_WALL)), 2)),
            head_rect_first=head_rect(t0), jd_rect_first=jd_rect(t0), jd_rect_last=jd_rect(ts[-1]))
    out['texture'] = texture_report()
    prewarm()
    cv = np.zeros((K.H, K.W, 4), np.float32)
    for name, fn, tt in ((POSE_A, draw_s7b, 26.0), (POSE_B, draw_s8a, 29.6)):
        fn(cv, tt)
        t0 = time.time()
        for i in range(5):
            fn(cv, tt + i * 0.03)
        out['ms_draw_' + name] = round((time.time() - t0) / 5 * 1000, 1)
    em = []
    for name in (POSE_A, POSE_B):
        Ls = layers(name)
        em.append((name, round(float((Ls['key_head'][..., :3] + Ls['amb_head'][..., :3]).max()), 3)))
    out['max_linear_emission_head_layer'] = em
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        print(json.dumps(_check(), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
