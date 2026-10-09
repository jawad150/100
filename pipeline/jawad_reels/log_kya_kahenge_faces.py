"""log_kya_kahenge_faces.py - Jawad's 2.5D face shots for reel 5, C15 "Log Kya Kahenge" (face-compositor).

Owner: face-compositor. The reel module imports this file and never edits it; this file never edits the shared toolkit.
Plan: BRIEF.md section 14 (two shots, streetwear only, no expression swaps, no mirroring), with the deviations that the
never-uncanny limits force (FACES.md in brand_reels/design/reels/log_kya_kahenge/ explains each one with numbers).

    import jawad_kit                                   # FIRST (the reel module does this anyway)
    import log_kya_kahenge_faces as LF
    LF.prewarm()                                       # builds both looks once per worker (~5 s)

    # S3-01  f288-f383 (9.6-12.8 s): JD full body, small, in the stadium; look D cine; a REAL plane in the K.Scene
    cam = LF.cam_s3(t)                                 # the shot camera: render the whole world of S3-01 with it
    sc = K.Scene(cam) ; ...tiers, barrier, people... ; sc.custom(LF.S3_FEET, lambda cv, c: LF.draw_s3(cv, c, t))
    # draw_s3 = floor contact shadow + JD plane (depth of field from cam) + light wrap from what is already drawn
    # post, 9.6-12.8: LF.s3_rays(cv, t, rays_centre(t), 0.22) BEFORE the finish, then the finish with rays=0
    #                 (the floodlight's god rays without JD acting as a ray source)

    # S5-01  f768-f863 (25.6-28.8 s): JD bust, chin up, look A rim, warm key from screen-left; 2D over the 85 mm plate
    cv = <85 mm plate> ; LF.draw_s5(cv, t)             # torso layer breathes, head is ONE rigid layer; push 1.00->1.03
    LF.key_gain(t)                                     # the clunk ignition 0.6 / 0.3 / 0.9 / 0.95 / 1.0 (f768-f772)

    LF.jd_rect(t)        -> (x0, y0, x1, y1) screen box of JD + 28 px (caption avoid), or None outside both shots
    LF.jd_alpha(t)       -> (1920, 1080) float32 screen alpha of JD (QA masks), or None
    LF.FACES             -> the shot table (t0, t1, pose, P, width, cam_keys, rim_dir, rim_gain, swap_on_beat, note)
    python3 log_kya_kahenge_faces.py check             -> limits, parallax, texture, placement, cost (prints JSON)

Conventions: sprites are premultiplied LINEAR float32 (core.py); world x right, y DOWN, z away; units mm; screen px.
Assets: workspace/brand_reels/charsheet/cutouts/<pose>.png (2x Real-ESRGAN x4plus masters, BiRefNet-portrait matte,
decontaminated), <pose>_depth.png (Depth-Anything-V2-Small, Apache-2.0), <pose>.json (eyes, face/head boxes).
Never-uncanny: the head is rigid in every frame (no warp, no depth displacement on the face); no blink, no lip motion,
no morphs, no cross-dissolves; camera yaw/pitch/roll <= 4/3/2 deg; push <= 8 %/s; head-to-plate parallax <= 3 % of the
frame width per second; breathing <= 0.5 % at 0.29 Hz on the torso only; display scale <= 1.0 of the 2x master.
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

# faces.py (the charsheet helper library) imported BY PATH under a private name, so its folder never lands on sys.path
_spec = importlib.util.spec_from_file_location('lkk_charsheet_faces', os.path.join(CS, 'tools', 'faces.py'))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

FPS = 30
LOOK = 'noir_ember'
POSE_S3 = 'street_threequarter_turn'
POSE_S5 = 'street_chinup_gaze'

# ============================================================================================ texture (human-realism)
# Real-ESRGAN x4plus over-sharpens the streetwear headshots and waxes the cheeks (cheek Laplacian variance 2.3-2.6x the
# Lanczos 2x of the native crop). Pull the SR detail back toward the source by k: rgb = lanczos2x + k (sr - lanczos2x)
# in the opaque interior only (the decontaminated matte edge is kept as cut), kept at 16 bit (8-bit rounding noise alone
# is as large as the Lanczos cheek texture). k = 0.5 puts both cheeks inside 1.5x (float luma Laplacian variance:
# right 3.66x -> 1.30x, left 2.62x -> 1.12x) while eyes, brows, beard and chains stay crisp. The 3/4 full body is shown
# at 0.28 of the 2x master (0.57x native), where SR detail is averaged away: no blend needed.
TEX_K = {POSE_S5: 0.5}
# Matte hand-fix: a 6 x 4 px gap in the hair crest of the chin-up photo (the grey backdrop seen THROUGH the hair) was filled
# opaque by the matte and keeps the backdrop's light grey: a bright speck on top of his head over a dark world (visible on
# the 200 % edge board). Inpainted with the surrounding hair (cut-out px box x0, y0, x1, y1; only pixels brighter than
# the hair, luma > 120, are replaced).
SPECKS = {POSE_S5: [(404, 53, 422, 67)]}


@functools.lru_cache(maxsize=4)
def rgba16(name):
    """Straight-alpha sRGB RGBA uint16 (RGB order) of the cut-out, with the texture pull-back of TEX_K applied."""
    cut = cv2.imread(os.path.join(CUT, name + '.png'), cv2.IMREAD_UNCHANGED)          # BGRA
    k = TEX_K.get(name, 1.0)
    if k < 1.0:
        sr = cv2.imread(os.path.join(CROPS, name + '_2x.png')).astype(np.float32)
        nat = cv2.imread(os.path.join(CROPS, name + '.png'))
        lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        a = cut[..., 3].astype(np.float32) / 255.0
        core = cv2.erode((a > 0.99).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        w = cv2.GaussianBlur(core.astype(np.float32), (0, 0), 2.0)[..., None]
        rgb = cut[..., :3].astype(np.float32) + (k - 1.0) * (sr - lz) * w
    else:
        rgb = cut[..., :3].astype(np.float32)
    for (x0, y0, x1, y1) in SPECKS.get(name, []):
        sub = np.ascontiguousarray(rgb[y0:y1, x0:x1])
        lum = sub @ np.float32([0.114, 0.587, 0.299])
        mk = cv2.dilate((lum > 120).astype(np.uint8), np.ones((3, 3), np.uint8))
        for c in range(3):
            sub[..., c] = cv2.inpaint(np.ascontiguousarray(sub[..., c]), mk, 3, cv2.INPAINT_TELEA)
        rgb[y0:y1, x0:x1] = sub
    out = np.empty(cut.shape, np.uint16)
    out[..., :3] = np.clip(np.round(rgb[..., ::-1] * 257.0), 0, 65535).astype(np.uint16)
    out[..., 3] = cut[..., 3].astype(np.uint16) * 257
    out.setflags(write=False)
    return out


@functools.lru_cache(maxsize=4)
def plain(name):
    """Premultiplied linear sprite of the (texture-corrected) cut-out. Read-only."""
    spr = K.sprite(rgba16(name))
    spr.setflags(write=False)
    return spr


def meta(name):
    return FA.meta(name)


def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


# ============================================================================================ S3-01: full body, look D
S3_T0, S3_T1 = 9.6, 12.8                    # f288 (in under the O2 smoke) .. f383 (hard cut at f384)
S3_FEET = (900.0, 0.0, 2500.0)              # world point of his feet (floor y = 0); plane parallel to the sensor
S3_HEIGHT_MM = 1800.0                       # crown to soles
S3_CAM_X, S3_CAM_Z = 193.0, -1614.0
S3_H0, S3_H1 = 1100.0, 1420.0               # pedestal (mm above the floor), LINEAR: constant-speed crane
S3_P0, S3_P1 = -3.0, 3.0                    # tilt (deg, + looks up), inout_sine: a pure rotation adds no parallax
S3_FOCAL, S3_APERTURE = 1280.0, 10.0        # 24 mm look (focal in px), deep focus
S3_EXPOSURE = 0.55                          # cine_grade exposure (stadium flat floodlight; measured on the frame)
S3_VEIL = 1.0                               # x NIGHT_0 airlight on him: his blacks meet the scene's (p2 match)
S3_BREATH = 0.0025                          # breathing: plane height x(1 +- 0.25 %) about the feet, 0.29 Hz (the
                                            # head moves <= 1.4 px; at 560 px tall a torso split is invisible)
S3_WRAP = dict(width=5.0, sigma=14.0, amount=0.22)


def cam_s3(t):
    """The S3-01 shot camera (render the world of this shot with it). Pedestal 1100 -> 1420 mm at constant speed
    (JD-to-plate parallax <= 32 px/s even against infinity; limit 3 % of 1080 = 32.4 px/s) + a tilt -3 -> +3 deg
    (inout_sine, a pure rotation: no parallax); yaw 0, roll 0, focal 1280 px (24 mm look), aperture 10."""
    u = K.clamp((t - S3_T0) / (S3_T1 - S3_T0))
    h = S3_H0 + (S3_H1 - S3_H0) * u
    pitch = S3_P0 + (S3_P1 - S3_P0) * K.EASE['inout_sine'](u)
    focus = S3_FEET[2] - S3_CAM_Z
    return K.Cam(pos=(S3_CAM_X, -h, S3_CAM_Z), yaw=0.0, pitch=pitch, focal=S3_FOCAL, aperture=S3_APERTURE,
                 focus_dist=focus)


@functools.lru_cache(maxsize=1)
def look_s3():
    """(plain, hero, mm_per_px, feet_anchor): look D cine (cine_grade base) with the floodlight's rim from the top-right
    and a gentle crown-to-feet falloff (1.0 -> 0.8) instead of a light pool. A high floodlight cannot rim the legs or
    the soles: the rim / counter-rim / halo emission fades from 1.0 at the shoulders to 0 at the feet, and the all-round
    outline and red counter-rim are kept low (a full glowing outline on a 560 px figure reads as a sticker)."""
    p = plain(POSE_S3)
    m = meta(POSE_S3)
    dep = FA.depth(POSE_S3)
    base = FA.cine_grade(p, exposure=S3_EXPOSURE)
    x0, y0, x1, y1 = m['subject_bbox']
    ys = np.arange(p.shape[0], dtype=np.float32)
    fall = 1.0 - 0.2 * np.clip((ys - y0) / float(y1 - y0), 0, 1)
    base = base * np.concatenate([np.repeat(fall[:, None], 3, 1), np.ones((len(ys), 1), np.float32)], 1)[:, None, :]
    base[..., :3] += np.asarray(K.C['NIGHT_0'], np.float32) * S3_VEIL * base[..., 3:4]      # 4 m of air in front
    hero = FA.rim_light(p, dep, light=(0.35, -0.95), gain=1.4, back=0.12, outline=0.04, depth_wrap=0.2,
                        halo_strength=0.18, base=base)
    dx, dy = FA.offset(p, hero)
    bp = np.zeros(hero.shape, np.float32)
    bp[dy:dy + p.shape[0], dx:dx + p.shape[1]] = base
    yy = np.arange(hero.shape[0], dtype=np.float32) - dy                      # cut-out rows
    shoulder, hip, hip2 = y0 + 0.20 * (y1 - y0), y0 + 0.45 * (y1 - y0), y0 + 0.60 * (y1 - y0)
    r = np.interp(yy, [y0, shoulder, hip, hip2, y1], [1.0, 1.0, 0.3, 0.0, 0.0]).astype(np.float32)
    hero = bp + (hero - bp) * r[:, None, None]
    mm_per_px = S3_HEIGHT_MM / float(y1 - y0)
    return p, _ro(hero), mm_per_px, FA.feet_anchor(hero)


@functools.lru_cache(maxsize=1)
def _s3_plain_padded():
    """The plain cut-out padded exactly like look_s3's hero (for the halo / matte QA draws)."""
    p, hero, _, _ = look_s3()
    dx, dy = FA.offset(p, hero)
    out = np.zeros(hero.shape, np.float32)
    out[dy:dy + p.shape[0], dx:dx + p.shape[1]] = p
    return _ro(out)


@functools.lru_cache(maxsize=1)
def _s3_shadow():
    """Floor contact shadow (premultiplied black, alpha only), built in FLOOR millimetres at 2 mm/px and drawn as a
    floor plane (rot x 90), so it foreshortens with the camera exactly like the floor. Rows run from near (z - 270 mm)
    to far (z + 530 mm) of the feet point. Where the soles land on the floor (measured from the cut-out's soles seen
    from the mid-shot camera height): near foot toe (-17, 0) to heel (+218, +159) mm, far foot toe (-188, +257) to heel
    (-30, +271) mm. A 60 % core under each sole + a soft 45 % ellipse round both; 40 mm left of the feet (the bank is
    right)."""
    w, h = 500, 400
    xs = (np.arange(w, dtype=np.float32) + 0.5) * 2.0 - 500.0
    zs = (np.arange(h, dtype=np.float32) + 0.5) * 2.0 - 270.0
    X, Z = np.meshgrid(xs, zs)

    def blob(cx, cz, rx, rz, ang, k, pw):
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        u = ((X - cx) * c + (Z - cz) * s_) / rx
        v = (-(X - cx) * s_ + (Z - cz) * c) / rz
        return k * np.clip(1 - np.sqrt(u * u + v * v), 0, 1) ** pw
    a = blob(-20, 110, 400, 270, 0, 0.45, 1.2)
    a = np.maximum(a, blob(95, 70, 190, 72, 34, 0.60, 0.8))
    a = np.maximum(a, blob(-110, 255, 135, 62, 5, 0.60, 0.8))
    a = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 6)
    out = np.zeros((h, w, 4), np.float32)
    out[..., 3] = a
    return _ro(out)


S3_SHADOW_W_MM = 1000.0
S3_SHADOW_C = (-40.0, 130.0)                               # sprite centre relative to the feet point (x, z) mm


def _s3_place(t):
    """(center, width, height, anchor) of the JD plane at time t (breathing = height scale about the feet)."""
    p, hero, mmpp, anc = look_s3()
    br = S3_BREATH * math.sin(2 * math.pi * (t - S3_T0) / 3.4 + 0.7)
    width = hero.shape[1] * mmpp
    height = hero.shape[0] * mmpp * (1.0 + br)
    return S3_FEET, width, height, anc


def _wrap(cv, lay, bg, region, width, sigma, amount):
    """Light wrap: blur the background behind the subject and SCREEN it over the subject's outer `width` px."""
    x0, y0, x1, y1 = region
    a = lay[y0:y1, x0:x1, 3]
    if a.max() <= 0.01:
        return
    k = max(1, int(round(width)))
    inner = cv2.erode(a, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * k + 1, 2 * k + 1)))   # separable: fast
    band = cv2.GaussianBlur(np.clip(a - inner, 0, 1), (0, 0), max(0.8, width * 0.35)) * a
    q = 4 if sigma >= 12 else 1                                     # blur the plate at 1/4 res (sigma 20-40 px)
    h, w = bg.shape[:2]
    small = cv2.resize(np.ascontiguousarray(bg[..., :3]), (max(1, w // q), max(1, h // q)), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(small, (0, 0), sigma / q), (w, h), interpolation=cv2.INTER_LINEAR)
    rgb = cv[y0:y1, x0:x1, :3]
    rgb += (amount * band)[..., None] * np.clip(bl, 0, 1) * (1.0 - np.clip(rgb, 0, 1))


def _region(bb, pad, shape):
    x0, y0, x1, y1 = bb
    return (max(0, int(x0) - pad), max(0, int(y0) - pad), min(shape[1], int(x1) + pad), min(shape[0], int(y1) + pad))


def draw_s3(cv, cam, t, mode='full'):
    """S3-01: contact shadow on the floor + JD as a plane at S3_FEET (DOF from cam) + light wrap. Call from the world's
    K.Scene: sc.custom(LF.S3_FEET, lambda c, cm: LF.draw_s3(c, cm, t)) so everything behind him is drawn first.
    mode 'full' (the shot) | 'plain' (cut-out only, no look / shadow / wrap: matte QA) | 'alpha' (white silhouette)."""
    p, hero, mmpp, anc = look_s3()
    center, width, height, anc = _s3_place(t)
    if mode == 'full':
        sp = _s3_shadow()
        sc = (center[0] + S3_SHADOW_C[0], center[1], center[2] + S3_SHADOW_C[1])
        K.draw_plane(cv, sp, cam, sc, S3_SHADOW_W_MM, rot=(90.0, 0.0, 0.0))
    spr = hero if mode == 'full' else (_s3_plain_padded() if mode == 'plain' else _alpha_white(hero))
    lay = np.zeros_like(cv)
    info = K.draw_plane(lay, spr, cam, center, width, height=height, anchor=anc)
    if info is None:
        return None
    reg = _region(info['bbox'], int(S3_WRAP['sigma'] * 2), cv.shape)
    x0, y0, x1, y1 = reg
    bg = cv[y0:y1, x0:x1].copy() if mode == 'full' else None
    a = lay[y0:y1, x0:x1, 3:4]
    cv[y0:y1, x0:x1] = lay[y0:y1, x0:x1] + cv[y0:y1, x0:x1] * (1.0 - a)
    if mode == 'full':
        _wrap(cv, lay, bg, reg, **S3_WRAP)
    return info


# ============================================================================================ S5-01: bust, look A
S5_T0, S5_T1 = 25.6, 28.8                   # f768 (hard cut + the clunk) .. f863 (hard cut at f864)
S5_PIN_CUT = (470.0, 615.0)                 # cut-out px: bust centre-x at the beard's lowest point (y 608-615)
S5_PIN_SCR = (700.0, 1617.0)                # screen px of that point: the whole face stays above y 1620
S5_SCALE0, S5_PUSH = 0.75, 0.03             # 0.750 -> 0.7725 of the 2x master (BRIEF), push about the pin, easy_ease
S5_NECK_Y = 592.0                           # cut-out y of the head layer's lower edge (meta head_box bottom)
S5_BREATH = 0.004                           # torso layer only (<= 0.5 %), period 3.4 s (0.29 Hz)
S5_AMBIENT = 0.24                           # share of the subject's light that is not the warm key (phones, bounce)
S5_EXPOSURE = 0.42                          # warm_dark exposure
S5_FADE = (690.0, 964.0, 820.0)             # light falls off below the collar (y 690 -> 964 to x0.30); alpha 820 -> 964
S5_WRAP = dict(width=16.0, sigma=30.0, amount=0.24)
_GAIN = {768: 0.6, 769: 0.3, 770: 0.9, 771: 0.95}


def key_gain(t):
    """Warm key ignition on the clunk, per frame (constant inside a frame so motion-blur samples agree): f768 0.6,
    f769 0.3, f770 0.9, f771 0.95, 1.0 from f772. Before f768 the key is off (0); use it for the world's light too."""
    f = int(round(t * FPS))
    if f < 768:
        return 0.0
    return _GAIN.get(f, 1.0)


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


@functools.lru_cache(maxsize=1)
def _s5_layers():
    """Build the S5 look once: ambient + warm-key subject light, look A rim (light=(-0.9, -0.3)) as emission, the
    falloff below the collar, then the rigid head / breathing torso split. Returns a dict of read-only arrays."""
    p = plain(POSE_S5)
    m = meta(POSE_S5)
    dep = FA.depth(POSE_S5)
    h, w = p.shape[:2]
    a = np.ascontiguousarray(p[..., 3])
    base = FA.warm_dark(p, exposure=S5_EXPOSURE)
    # warm key from screen-left, slightly above: soft lateral falloff across the subject + a little depth-normal shape
    nx, ny, nz = FA.normals(dep, a, strength=4.0, blur=8.0)
    L = np.float32([-0.78, -0.30, 0.55])
    L = L / np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    lam = cv2.GaussianBlur(lam, (0, 0), 6)
    fx0, fy0, fx1, fy1 = m['face_box']
    xs = np.arange(w, dtype=np.float32)
    lat = 1.0 - 0.70 * _smooth((xs - (fx0 - 40)) / ((fx1 + 120) - (fx0 - 40)))       # 1.0 left -> 0.30 right
    shade = np.clip(0.65 * lat[None, :] + 0.35 * lam, 0, 1)
    # light falloff below the collar (the key is aimed at his face) + an alpha fade of the panel-cut bottom edge
    ys = np.arange(h, dtype=np.float32)
    fall = 1.0 - 0.70 * _smooth((ys - S5_FADE[0]) / (S5_FADE[1] - S5_FADE[0]))
    afade = 1.0 - _smooth((ys - S5_FADE[2]) / (S5_FADE[1] - S5_FADE[2]))
    amb = base.copy()
    amb[..., :3] *= S5_AMBIENT                                           # light only: alpha stays the matte
    key = base * (shade * (1.0 - S5_AMBIENT))[..., None]
    key[..., 3] = 0.0
    zero = FA.premult(np.zeros((h, w, 3), np.float32), a)
    rim = FA.rim_light(p, dep, light=(-0.9, -0.3), back=0.3, outline=0.12, base=zero)  # look A, emission only
    dx, dy = FA.offset(p, rim)
    H, W = rim.shape[:2]
    # HANDOFF risk 9 (checked on the real plate, motion-timeline-builder 2026-10-09): the all-round outline + counter-rim
    # saturated to an even stroke on BOTH sides after the finish (rendered edge luma: left 209-214, right 107-112), a
    # sticker edge against the brief's light plot. The rim emission now falls off from the face centre to the right
    # (1.0 at x <= 450 -> 0.25 at x 741, cut-out px): left rim unchanged (209-214), right edge 60-75.
    xs_r = np.arange(W, dtype=np.float32) - dx
    rim = rim.copy()
    rim[..., :3] *= (1.0 - 0.75 * _smooth((xs_r - 450.0) / (741.0 - 450.0)))[None, :, None]

    def padto(s):
        o = np.zeros((H, W, 4), np.float32)
        o[dy:dy + h, dx:dx + w] = s
        return o
    ambP = padto(amb)
    keyP = padto(key)
    keyP[..., :3] += rim[..., :3]
    yy = np.arange(H, dtype=np.float32) - dy
    fallP = np.interp(yy, ys, fall, left=1.0, right=fall[-1]).astype(np.float32)
    afP = np.interp(yy, ys, afade, left=1.0, right=0.0).astype(np.float32)
    ambP[..., :3] *= (fallP * afP)[:, None, None]                      # premultiplied: fade = rgb and alpha
    ambP[..., 3] *= afP[:, None]
    keyP[..., :3] *= (fallP * afP)[:, None, None]
    # rigid head layer vs breathing torso layer (exact recombination at zero offset: head over torso == whole)
    hx0, hy0, hx1, hy1 = m['head_box']
    fe = 0.08 * (hx1 - hx0)
    mk = np.zeros((H, W), np.float32)
    mk[int(max(0, hy0 + dy - 2 * fe)):int(hy1 + dy), int(max(0, hx0 + dx - fe)):int(min(W, hx1 + dx + fe))] = 1
    mk = np.clip(cv2.GaussianBlur(mk, (0, 0), fe / 2) * 2.0, 0, 1)
    al = ambP[..., 3]
    den = 1.0 - mk * al
    wt = np.where(den > 1e-4, (1.0 - mk) / np.maximum(den, 1e-4), 0.0).astype(np.float32)
    lay = {}
    for nm, src in (('amb', ambP), ('key', keyP)):
        lay[nm + '_head'] = _ro(src * mk[..., None])
        lay[nm + '_torso'] = _ro(src * wt[..., None])
    plainP = padto(p) * afP[:, None, None]
    lay['plain'] = _ro(plainP)
    lay['off'] = (dx, dy)
    lay['shape'] = (H, W)
    return lay


@functools.lru_cache(maxsize=3)
def _s5_lit(g):
    L = _s5_layers()
    return (_ro(L['amb_head'] + g * L['key_head']), _ro(L['amb_torso'] + g * L['key_torso']))


def s5_scale(t):
    return S5_SCALE0 * (1.0 + S5_PUSH * K.EASE['easy_ease'](K.clamp((t - S5_T0) / (S5_T1 - S5_T0))))


def s5_idle(t):
    """(dx, dy, rot_deg, breath): a standing person's micro-sway; breathing applies to the torso layer only."""
    tt = t - S5_T0
    br = S5_BREATH * math.sin(2 * math.pi * tt / 3.4 + 0.4)
    return K.wiggle(t, 0.18, 1.6, 11), K.wiggle(t, 0.15, 1.0, 18), K.wiggle(t, 0.22, 0.25, 14), br


def _s5_transform(t):
    """Screen mapping of cut-out px for the HEAD layer: X = C + R s (U - pin). Returns (C, s, rot, R, breath)."""
    dx, dy, rot, br = s5_idle(t)
    s = s5_scale(t)
    r = math.radians(rot)
    R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    C = np.array([S5_PIN_SCR[0] + dx, S5_PIN_SCR[1] + dy])
    return C, s, rot, R, br


def s5_point(t, uv):
    """Screen px of cut-out pixel uv (head layer; e.g. meta eye_mid) at time t."""
    C, s, rot, R, br = _s5_transform(t)
    return C + R @ (s * (np.asarray(uv, np.float64) - np.asarray(S5_PIN_CUT)))


def draw_s5(cv, t, mode='full'):
    """S5-01: JD bust over the plate already in cv. mode 'full' | 'plain' (cut-out only: matte QA) | 'alpha'."""
    L = _s5_layers()
    dx0, dy0 = L['off']
    H, W = L['shape']
    C, s, rot, R, br = _s5_transform(t)
    pin = (S5_PIN_CUT[0] + dx0, S5_PIN_CUT[1] + dy0)                 # in padded-layer px
    bot = (S5_PIN_CUT[0] + dx0, 964.0 + dy0)
    if mode == 'full':
        head, torso = _s5_lit(key_gain(t))
    elif mode == 'plain':
        head, torso = None, L['plain']
    else:
        head, torso = None, _alpha_white(L['plain'])
    # torso: scale (1, 1 + br) about the bust bottom, then the global push / sway about the pin
    cb = C + R @ (s * (np.asarray(bot) - np.asarray(pin)))
    lay = np.zeros_like(cv)
    bb1 = K.draw(lay, torso, cb[0], cb[1], scale=(s, s * (1.0 + br)) if head is not None else s, rot=rot,
                 anchor=(bot[0] / W, bot[1] / H))
    bb2 = None
    if head is not None:
        lift = R @ np.array([0.0, -br * s * (964.0 - S5_NECK_Y)])  # the head rides the breathing neck, unscaled
        bb2 = K.draw(lay, head, C[0] + lift[0], C[1] + lift[1], scale=s, rot=rot, anchor=(pin[0] / W, pin[1] / H))
    bbs = [b for b in (bb1, bb2) if b is not None]
    if not bbs:
        return None
    bb = (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs), max(b[3] for b in bbs))
    reg = _region(bb, int(S5_WRAP['sigma'] * 2), cv.shape)
    x0, y0, x1, y1 = reg
    bg = cv[y0:y1, x0:x1].copy() if mode == 'full' else None
    a = lay[y0:y1, x0:x1, 3:4]
    cv[y0:y1, x0:x1] = lay[y0:y1, x0:x1] + cv[y0:y1, x0:x1] * (1.0 - a)
    if mode == 'full':
        _wrap(cv, lay, bg, reg, **S5_WRAP)
    return bb


# ============================================================================================ shared helpers / exports
_AW = {}


def _alpha_white(spr):
    k = id(spr)
    if k not in _AW:
        o = np.zeros_like(spr)
        o[..., :3] = spr[..., 3:4]
        o[..., 3] = spr[..., 3]
        _AW[k] = _ro(o)
    return _AW[k]


def jd_alpha(t):
    """(1920, 1080) float32 screen alpha of JD at time t (the cut-out matte, no glow), or None outside his shots."""
    cv = np.zeros((K.H, K.W, 4), np.float32)
    if S3_T0 <= t < S3_T1:
        draw_s3(cv, cam_s3(t), t, mode='alpha')
    elif S5_T0 <= t < S5_T1:
        draw_s5(cv, t, mode='alpha')
    else:
        return None
    return cv[..., 3].copy()


def s3_rays(cv, t, center, strength=0.22, look=LOOK):
    """S3-01 god rays with JD held out as a SOURCE (call in post BEFORE the finish, then pass rays=0 to the finish for
    9.6-12.8). G.finish's rays smear every bright pixel away from the centre; his white tee, hand, watch and trainers
    would stream a faint light trail down-left of his legs (measured on the stand-in: p99 +6, max +9 code values in
    the floor band beside him), i.e. he would look like a light source. Same call as G.finish (K.god_rays, the look's
    threshold / length, tint (1.0, 0.78, 0.45)); everything else in the frame still emits, and the rays still pass
    over him. In place; returns cv."""
    import jawad_grade as G                                        # read-only shared module (lazy: post only)
    if strength <= 0 or not (S3_T0 <= t < S3_T1):
        return cv
    P = G.FIN[look]
    a = jd_alpha(t)
    src = cv.copy()
    src[..., :3] *= (1.0 - np.clip(a, 0, 1))[..., None]
    base = src[..., :3].copy()
    K.god_rays(src, center, strength=strength, threshold=P.get('rays_threshold', 0.3),
               length=P.get('rays_length', 0.4), tint=(1.0, 0.78, 0.45))
    cv[..., :3] += src[..., :3] - base
    return cv


def jd_rect(t, margin=28):
    """Caption avoid rect: JD's projected subject bbox + margin px, clipped to the frame; None outside his shots.
    S3-01 follows cam_s3(t); S5-01 is the bust from the hair crest down to the frame bottom."""
    if S3_T0 <= t < S3_T1:
        p, hero, mmpp, anc = look_s3()
        center, width, height, anc = _s3_place(t)
        dx, dy = FA.offset(p, hero)
        x0, y0, x1, y1 = meta(POSE_S3)['subject_bbox']
        uv = np.array([[x0 + dx, y0 + dy], [x1 + dx, y0 + dy], [x1 + dx, y1 + dy], [x0 + dx, y1 + dy]], np.float64)
        uv = uv / np.array([hero.shape[1], hero.shape[0]])
        P = K.plane_point(center, width, height, uv=uv, anchor=anc)
        xy, _ = cam_s3(t).project(P)
    elif S5_T0 <= t < S5_T1:
        x0, y0, x1, y1 = meta(POSE_S5)['subject_bbox']
        xy = np.array([s5_point(t, (x0, y0)), s5_point(t, (x1, y0)), s5_point(t, (x0, 964)), s5_point(t, (x1, 964))])
        xy[:, 1] = np.maximum(xy[:, 1], 0)
    else:
        return None
    return (max(0, int(math.floor(xy[:, 0].min() - margin))), max(0, int(math.floor(xy[:, 1].min() - margin))),
            min(K.W, int(math.ceil(xy[:, 0].max() + margin))), min(K.H, int(math.ceil(xy[:, 1].max() + margin))))


def prewarm():
    look_s3()
    _s3_plain_padded()
    _s3_shadow()
    _s5_layers()
    _s5_lit(1.0)


# ============================================================================================ the shot table
FACES = [
    dict(t0=S3_T0, t1=S3_T1, f0=288, f1=383, shot='S3-01', pose=POSE_S3, look='D cine',
         P=dict(world_feet=S3_FEET, height_mm=S3_HEIGHT_MM, plane='parallel to the sensor (yaw 0)', layer='K.Scene custom'),
         width='1800 mm tall: ~560 px on screen (0.28 of the 2x master)',
         cam_keys=dict(fn='cam_s3', pos=(S3_CAM_X, '-h', S3_CAM_Z), h_mm=(S3_H0, S3_H1, 'linear'),
                       pitch_deg=(S3_P0, S3_P1, 'inout_sine'), yaw=0, roll=0, focal=S3_FOCAL, aperture=S3_APERTURE),
         rim_dir=(0.35, -0.95), rim_gain=1.4, swap_on_beat=False,
         note='alone in front of the staring stands; flat floodlight (crown 1.0 -> feet 0.8), no cone, no light pool; '
              'floor contact shadow falls left; breathing 0.25 % only (no drift: the feet stay planted)'),
    dict(t0=S5_T0, t1=S5_T1, f0=768, f1=863, shot='S5-01', pose=POSE_S5, look='A rim',
         P=dict(pin_cutout=S5_PIN_CUT, pin_screen=S5_PIN_SCR, eye_mid_screen=(641, 1371)),
         width='scale 0.750 -> 0.7725 of the 2x master (bust 668-688 px wide)',
         cam_keys=dict(push=(1.0, 1.0 + S5_PUSH, 'easy_ease'), about='pin (beard bottom)', plate='CAM_JD 85 mm'),
         rim_dir=(-0.9, -0.3), rim_gain=2.4, swap_on_beat=False,
         note='payoff, liberation: warm key from screen-left ignites on the clunk (key_gain), right cheek falls off; '
              'head = one rigid layer, torso breathes 0.4 %; chest falls off into the dark below the collar'),
]


# ============================================================================================ checks (python3 ... check)
def _check():
    out = {}
    # S3 camera limits and parallax. Plates = the world points seen DIRECTLY BEHIND his head at mid-shot (depths of the
    # tier rows, the K.background reference plane and the lamp bank's distance), tracked over the shot: their relative
    # screen speed is the head-to-plate parallax (the tilt is a pure rotation and moves head and plate alike).
    ts = np.linspace(S3_T0, S3_T1 - 1e-3, 97)
    head = np.array([S3_FEET[0], -1700.0, S3_FEET[2]])
    cm = cam_s3((S3_T0 + S3_T1) / 2)
    ray = head - cm.pos
    ray = ray / np.linalg.norm(ray)
    plates = {}
    for nm, depth in (('row0 (depth ~8.6 m)', 8614.0), ('row9 (depth ~15.8 m)', 15814.0),
                      ('backdrop ref (depth ~10.6 m)', 10614.0), ('lamp-bank distance (~17 m)', 17100.0),
                      ('infinity', 1e9)):
        plates[nm] = cm.pos + ray * depth / float(ray @ cm.forward)
    pos = {k: [] for k in ['head'] + list(plates)}
    for t in ts:
        c = cam_s3(t)
        pos['head'].append(c.project(head[None])[0][0])
        for k, P in plates.items():
            pos[k].append(c.project(P[None])[0][0])
    pos = {k: np.array(v) for k, v in pos.items()}
    dt = ts[1] - ts[0]
    par = {}
    for k in plates:
        rel = pos['head'] - pos[k]
        v = np.linalg.norm(np.diff(rel, axis=0), axis=1) / dt
        par[k] = dict(peak_px_s=round(float(v.max()), 1), pct_width_s=round(float(v.max()) / K.W * 100, 2),
                      peak_px_frame=round(float(v.max()) / FPS, 2))
    hv = np.linalg.norm(np.diff(pos['head'], axis=0), axis=1) / dt
    out['S3'] = dict(pitch=(S3_P0, S3_P1), yaw=0, roll=0, pedestal_mm=S3_H1 - S3_H0,
                     view_angle_change_deg=round(math.degrees(math.atan((S3_H1 - S3_H0) / (S3_FEET[2] - S3_CAM_Z))), 2),
                     head_screen_speed_peak_px_frame=round(float(hv.max()) / FPS, 2),
                     parallax_head_vs=par, rect_f288=jd_rect(9.6), rect_f383=jd_rect(12.7667),
                     scale_of_2x=round(S3_FOCAL / (S3_FEET[2] - S3_CAM_Z) * look_s3()[2], 4))
    # S5 push rate, face position, bottom zone, breathing
    ts5 = np.linspace(S5_T0, S5_T1 - 1e-3, 97)
    sc = np.array([s5_scale(t) for t in ts5])
    rate = np.abs(np.diff(sc)) / (ts5[1] - ts5[0]) / sc[:-1] * 100
    m = meta(POSE_S5)
    eye = np.array([s5_point(t, m['eye_mid']) for t in ts5])
    beard = np.array([s5_point(t, (420.0, 615.0)) for t in ts5])
    crest = np.array([s5_point(t, (470.0, m['subject_bbox'][1])) for t in ts5])
    out['S5'] = dict(scale=(round(sc[0], 4), round(sc[-1], 4)), push_peak_pct_s=round(float(rate.max()), 2),
                     eye_mid_f768=[round(v, 1) for v in eye[0]], eye_mid_f863=[round(v, 1) for v in eye[-1]],
                     beard_bottom_y_max=round(float(beard[:, 1].max()), 1), crest_y=(round(float(crest[0, 1]), 1),
                                                                                    round(float(crest[-1, 1]), 1)),
                     face_x=(round(float(s5_point(S5_T0, (m['face_box'][0], 0))[0]), 1),
                             round(float(s5_point(S5_T0, (m['face_box'][2], 0))[0]), 1)),
                     eye_speed_peak_px_frame=round(float(np.linalg.norm(np.diff(eye, axis=0), axis=1).max()
                                                         / (ts5[1] - ts5[0]) / FPS), 2),
                     rect_f768=jd_rect(25.6), rect_f863=jd_rect(28.7667),
                     breath_pct=S5_BREATH * 100, breath_hz=round(1 / 3.4, 3))
    # texture (cheek Laplacian variance vs Lanczos 2x of the native crop) for the S5 pose
    sr = cv2.imread(os.path.join(CROPS, POSE_S5 + '_2x.png'))
    nat = cv2.imread(os.path.join(CROPS, POSE_S5 + '.png'))
    lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    used = np.ascontiguousarray(rgba16(POSE_S5)[..., 2::-1]).astype(np.float32) / 257.0      # BGR, 0..255 float

    def lv(img, b):                                 # float luma (no 8-bit rounding), Laplacian variance on the patch
        x0, y0, x1, y1 = b
        g = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
        return float(cv2.Laplacian(g, cv2.CV_32F).var())
    pts = {'r_cheek': (490, 345, 555, 415), 'l_cheek': (285, 345, 315, 395)}
    out['texture_S5'] = {k: dict(sr_raw=round(lv(sr, b) / lv(lz, b), 2), used=round(lv(used, b) / lv(lz, b), 2))
                         for k, b in pts.items()}
    # cost
    prewarm()
    cv = np.zeros((K.H, K.W, 4), np.float32)
    t0 = time.time()
    for i in range(5):
        draw_s3(cv, cam_s3(10.0 + i * 0.4), 10.0 + i * 0.4)
    out['ms_draw_s3'] = round((time.time() - t0) / 5 * 1000, 1)
    t0 = time.time()
    for i in range(5):
        draw_s5(cv, 26.0 + i * 0.4)
    out['ms_draw_s5'] = round((time.time() - t0) / 5 * 1000, 1)
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        print(json.dumps(_check(), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
