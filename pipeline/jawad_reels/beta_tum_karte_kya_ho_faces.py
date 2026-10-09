"""beta_tum_karte_kya_ho_faces.py - Jawad's 2.5D face shots for reel 4, C02 "Beta, tum karte kya ho?" (face-compositor).

Owner: face-compositor. The reel module imports this file and never edits it; this file never edits the shared toolkit.
Plan: BRIEF.md section 6.10 (four suit busts, frontal family, eyes locked at (540, 1280), no mirroring, hard cuts only).
FACES.md (brand_reels/design/reels/beta_tum_karte_kya_ho/) has the numbers, stills and every deviation with its reason.

    import jawad_kit                                    # FIRST (the reel module does this anyway)
    import beta_tum_karte_kya_ho_faces as FF
    FF.prewarm()                                        # builds the four poses' layers once per worker (~6-10 s)

    key = FF.shot_at(t)                                 # 'S0' | 'S3' | 'S6' | 'S10' | 'S12' | None (frame-exact, X.side_b rule)
    if key:
        cv = K.background(LOOK, t, FF.world_cam(t), bokeh=0.6, intensity=FF.window_gain(t))   # the plate moves with
        ...sun disc (S10), anything that sits BEHIND JD...                                    # the dolly (parallax)
        FF.draw_face(cv, key, t)                        # sill shadow + torso + rigid head + rim + light wrap
        ...J.embers in front (cam=FF.world_cam(t)), bubbles / lockups, captions...

    FF.head_rect(key, t)  -> (x0, top, x1, 1920) caption avoid rect (brief 6.10), +6 px margin
    FF.face_rect(key, t)  -> (x0, y0, x1, y1) screen face box;  FF.eye_point(key, t) -> screen eye midpoint (idle incl.)
    FF.bust_bottom(key, t), FF.scale(key, t), FF.cam(key, t) (the 85 mm JD camera), FF.window_gain(t)
    FF.jd_alpha(key, t)   -> (1920, 1080) float32 screen alpha of JD (QA masks: "no face pixel under UI")
    FF.look(pose, kind)   -> the built layer dict (read-only arrays)
    FF.FACES              -> shot table (t0, t1, pose, P, width, cam_keys, rim_dir, rim_gain, swap_on_beat, note, ...)
    python3 beta_tum_karte_kya_ho_faces.py check   -> limits, eye lock, parallax, texture, halo, cost (JSON)
    python3 beta_tum_karte_kya_ho_faces.py export  -> <reel ws>/faces/<pose>/ (rgba, layers, depth, rim mask, meta)
    python3 beta_tum_karte_kya_ho_faces.py boards  -> 200 % edge boards over black / FLAME / white

Conventions: sprites are premultiplied LINEAR float32 (core.py); world x right, y DOWN, z away; screen px.
Assets (read-only): workspace/brand_reels/charsheet/cutouts/<pose>.png (Real-ESRGAN x4plus 2x masters, BiRefNet-portrait
matte (MIT), pymatting decontamination), <pose>_depth.png (Depth-Anything-V2-Small, Apache-2.0), <pose>.json (YuNet
eyes / face box / head box), crops/<pose>.png (native) + crops/<pose>_2x.png (SR before matting).
Never-uncanny: the head is ONE rigid plane in every frame (no warp or depth displacement on eyes, nose, mouth, jaw);
no blink, no lip motion, no morphs, no cross-dissolve (one pose per frame; the reel cuts); yaw/pitch 0, roll <= 0.25 deg
(subject sway), push <= 8 %/s, head-to-plate parallax far under 3 % of the frame width per second; breathing <= 0.4 %
at 0.29 Hz on the torso layer only; display scale <= 0.987 of the 2x master.
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
REEL_WS = os.path.join(K.WS, 'beta_tum_karte_kya_ho')
ASSET_DIR = os.path.join(REEL_WS, 'faces')

# faces.py (the charsheet helper library) imported BY PATH under a private name: its folder never lands on sys.path
_spec = importlib.util.spec_from_file_location('btk_charsheet_faces', os.path.join(CS, 'tools', 'faces.py'))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

FPS = 30
LOOK = 'gold_hour'
HALF = 0.5 / FPS

# ============================================================================================ geometry (BRIEF 6.10)
EYES = (540.0, 1280.0)          # screen eye midpoint in every JD shot (continuity ledger)
S0 = 0.92                       # display scale (of the 2x master) at each shot's push origin t_push0
PUSH = 0.012                    # slow dolly, +1.2 % per second
SWAP_AMT, SWAP_DUR = 0.03, 0.9  # punch-in on the new pose after a hard cut: 1.00 -> 1.03 ...


def _out_quad(x):
    return 1.0 - (1.0 - x) * (1.0 - x)


SWAP_EASE = _out_quad           # ... out_quad, not FA.swap_push's out_cubic: out_cubic starts at 3 x 3.3 %/s = 10 %/s
                                # (+1.2 % dolly = 11.2 %/s > the 8 %/s limit); out_quad peaks at 6.7 + 1.2 = 7.9 %/s

# ============================================================================================ camera (85 mm look)
F85 = 960.0 / math.tan(math.radians(12.0))       # 4516 px: 24 deg vertical FOV = an 85 mm lens on a vertical frame
APERTURE = 24.0                                   # BRIEF World Bible: 85 mm busts, aperture 24 (focus on the head)
Z_TORSO = 100.0                                   # torso plane behind the head plane (units ~0.4 mm: ~4 cm)
Z_PLATE = 6200.0                                  # window wall behind the head plane (~2.5 m): world_cam() parallax
DEPTH_RANGE = 450.0                               # depth-map 0..1 -> ~18 cm of relief on the torso layer
DEPTH_MIN_PX = 0.2                                # skip the torso micro-parallax remap below this displacement

# ============================================================================================ light
RIM_A = dict(gain=2.2, back=0.45, outline=0.04, depth_wrap=0.30, halo_strength=0.16, halo_sigmas=(6, 18, 48))
RIM_D = dict(gain=1.4, back=0.40, outline=0.03, depth_wrap=0.25, halo_strength=0.10, halo_sigmas=(6, 18, 48))
BASE_A = dict(exposure=0.42)                      # FA.warm_dark (low-key warm, backlit room)
BASE_D = dict(exposure=0.52)                      # FA.cine_grade (S-curve with a toe, warm split tone); 0.52 puts
                                                  # the D face at the A face's level (0.80 read +30 code values)
TORSO_FALL = dict(start=30.0, bottom=0.62)        # front fill aimed at the face: x1 at the chin + 30 px -> x0.62 at
                                                  # the bust bottom (backlit room: the shirt is not front-lit)
KNEE = dict(k0=0.19, ymax=0.225)                  # subject highlight shoulder (linear luminance, A scale): the white
                                                  # shirt never outshines the window glow behind him
VEIL = {'A': 0.0, 'D': 0.35}                      # NIGHT_1 airlight on the subject per look: D's toe crushes the
                                                  # suit 2 code values under the room's blacks; +0.35 x NIGHT_1 matches
WRAP = dict(width=14.0, sigma=30.0, amount=0.22)  # light wrap: blurred plate screened over the outer 14 px
PHONE = dict(center=(540.0, 1790.0), radius=560.0, strength=0.22)   # phone screen below frame: amber uplight
SILL = dict(y0=1540.0, y1=1770.0, opacity=0.86)  # wall under the window sill: the plate darkens below his collar
FADE_FRAC = 0.05                                  # soft blend of the panel-cut sides into the dark wall

TEX_K = {'suit_confused': 0.27, 'suit_shocked': 0.23, 'suit_neutral': 0.29, 'suit_hand_on_chest': 0.26}
# Skin-only SR detail pull-back (human-realism): rgb = lanczos2x + k (sr - lanczos2x) on SKIN pixels of the face
# (eyes, brows, lashes, beard, hair, lips' edges, shirt and suit keep the full SR detail, k = 1). Real-ESRGAN x4plus
# put 7.6-11.4x the cheek Laplacian variance of the 2x Lanczos source into these small suit faces (smooth-wax skin with
# crisp edges); k is the largest value (bisection, 0.01 steps) that brings each pose's cheek patch to <= 1.45x.

# Eye anchor: the midpoint of the two eyes' canthi (inner + outer corners), MARKED BY HAND on 4x crops of the 2x masters
# (cut-out px). meta['eye_mid'] (YuNet) sits 10-15 px right / 8-15 px above the eyes and its bias differs between
# poses by up to 7 px, so it cannot lock eyes across shots within 6 px. Corners (x, y): outer-left, inner-left,
# inner-right, outer-right.
EYE_CORNERS = {
    'suit_confused': ((283.0, 340.0), (367.5, 343.75), (432.5, 350.0), (508.75, 355.0)),
    'suit_shocked': ((335.0, 342.5), (406.0, 347.0), (482.5, 349.5), (553.75, 353.75)),
    'suit_neutral': ((351.0, 377.5), (447.5, 380.0), (512.5, 382.0), (595.0, 395.0)),
    'suit_hand_on_chest': ((297.5, 317.5), (383.75, 304.25), (440.75, 293.75), (496.25, 286.25)),
}
EYE_MID = {k: (sum(p[0] for p in v) / 4.0, sum(p[1] for p in v) / 4.0) for k, v in EYE_CORNERS.items()}

POSES = ('suit_confused', 'suit_shocked', 'suit_neutral', 'suit_hand_on_chest')

# ============================================================================================ shot table
# frames are half-open [f0, f1); tau = t + tau_off is the shot's own clock (S12 is the hook at t - 36.4 so the loop is
# continuous); t_push0 is on that clock. swap_on_beat = the hard-cut time whose punch-in (1.00 -> 1.03) runs.
FACES = [
    dict(key='S0', f0=0, f1=84, t0=0.0, t1=2.8, pose='suit_confused', kind='A', t_push0=-0.7, tau_off=0.0,
         swap_on_beat=None, phone=True, rim_dir=(0.8, -0.5), rim_gain=RIM_A['gain'], idle_seed=3,
         note='hook A + cover f30: frozen mid-word under the Mummy pill; dolly continues from S12 across the loop'),
    dict(key='S3', f0=231, f1=252, t0=7.7, t1=8.4, pose='suit_shocked', kind='D', t_push0=7.7, tau_off=0.0,
         swap_on_beat=7.7, phone=True, rim_dir=(0.8, -0.5), rim_gain=RIM_D['gain'], idle_seed=5,
         note='c3 punch-in after "Cartoon?": wide-eyed, mouth shut'),
    dict(key='S6', f0=420, f1=504, t0=14.0, t1=16.8, pose='suit_neutral', kind='D', t_push0=14.0, tau_off=0.0,
         swap_on_beat=14.0, phone=True, rim_dir=(0.8, -0.5), rim_gain=RIM_D['gain'], idle_seed=7,
         note='c6 after the killer line: level stare; window light dims -15 % from 15.4 s'),
    dict(key='S10', f0=861, f1=966, t0=28.7, t1=32.2, pose='suit_hand_on_chest', kind='A', t_push0=28.7, tau_off=0.0,
         swap_on_beat=28.7, phone=False, rim_dir=(0.55, -0.85), rim_gain=RIM_A['gain'], idle_seed=11, rim_back=0.85,
         note='payoff anchor (f900): hand on chest under "MERA BETA cinema BANATA HAI"; sun behind him, rim both '
              'sides; sun swell +35 % at 30.8 s'),
    dict(key='S12', f0=1071, f1=1092, t0=35.7, t1=36.4, pose='suit_confused', kind='A', t_push0=-0.7, tau_off=-36.4,
         swap_on_beat=None, phone=True, rim_dir=(0.8, -0.5), rim_gain=RIM_A['gain'], idle_seed=3,
         note='loop pre-roll = S0 at t - 36.4 (c12 is a hard cut from the end-card world; frame 1091 -> 0 continuous)'),
]
SHOTS = {d['key']: d for d in FACES}


def _fidx(t):
    return int(math.floor(t * FPS + 0.5))         # jawad_tx.fidx: sub-samples of a frame map to that frame


def shot_at(t):
    """Key of the face shot on screen at time t (frame-exact, sub-frame samples belong to their frame), or None."""
    f = _fidx(t)
    for d in FACES:
        if d['f0'] <= f < d['f1']:
            return d['key']
    return None


def window_gain(t):
    """The window light (JD's backlight and the gold_hour world's intensity): S6 dims -15 % over 15.4-16.8 s
    (inout_sine, time begins to pass); S10 swells +35 % on the bar-11 downbeat 30.8-31.3 s (out_cubic). 1.0 elsewhere.
    Use the same value for K.background(..., intensity=FF.window_gain(t)) so JD's rim and the room agree."""
    if 14.0 - HALF <= t < 16.8 - HALF:
        return 1.0 - 0.15 * K.ramp(t, 15.4, 16.8, 'inout_sine')
    if 28.7 - HALF <= t < 32.2 - HALF:
        return 1.0 + 0.35 * K.ramp(t, 30.8, 31.3, 'out_cubic')
    return 1.0


def scale(key, t):
    """Display scale of the head plane (of the 2x master) = BRIEF 6.10 with the out_quad punch-in."""
    d = SHOTS[key]
    tau = t + d['tau_off']
    s = S0 * (1.0 + PUSH * (tau - d['t_push0']))
    if d['swap_on_beat'] is not None:
        s *= 1.0 + SWAP_AMT * K.ramp(t, d['swap_on_beat'], d['swap_on_beat'] + SWAP_DUR, SWAP_EASE)
    return s


def _fill_table():
    """Complete FACES with the face-compositor table fields: P (screen eye midpoint), width (on-screen bust width
    at t_push0, px), cam_keys ((t, head-plane scale) at the shot's first and last frame)."""
    for d in FACES:
        w = plain(d['pose']).shape[1] if '_w' not in d else d['_w']
        d['P'] = EYES
        d['width'] = round(w * S0, 1)
        d['cam_keys'] = [(round(d['f0'] / FPS, 4), round(scale(d['key'], d['f0'] / FPS), 4)),
                         (round((d['f1'] - 1) / FPS, 4), round(scale(d['key'], (d['f1'] - 1) / FPS), 4))]


def _cam_state(key, t):
    """(cz, cy, Dh): camera z / y and its distance to the head plane (z = 0). The camera dollies along the ray through
    the eye point, so the eye midpoint stays at EYES while every other depth scales about it (real parallax)."""
    s = scale(key, t)
    Dh = F85 / s
    return -Dh, -(EYES[1] - K.CY) / s, Dh


def cam(key, t):
    """The 85 mm JD camera (focus on the head plane, aperture 24)."""
    cz, cy, Dh = _cam_state(key, t)
    return K.Cam(pos=(0.0, cy, cz), focal=F85, aperture=APERTURE, focus_dist=Dh)


def world_cam(t, key=None):
    """A default-focal K.Cam for the builder's K.background / bokeh / J.embers during a face shot: it moves the
    gold_hour plate exactly as a wall Z_PLATE behind JD moves under the 85 mm dolly (scale about the screen centre +
    vertical slide), so JD grows faster than the room. None outside the face shots (plate unchanged)."""
    key = key or shot_at(t)
    if key is None:
        return None
    d = SHOTS[key]
    t_ref = d['t_push0'] - d['tau_off']                   # registration time on the reel clock
    cz0, cy0, _ = _cam_state(key, t_ref)
    cz, cy, _ = _cam_state(key, t)
    zp0, zp = Z_PLATE - cz0, Z_PLATE - cz
    s_p = zp0 / zp
    ty = F85 * (cy0 - cy) / zp                            # screen slide of the plate point that was at the centre
    wz = 10500.0 * (1.0 - 1.0 / s_p)                      # core._bg_transform: plate at 9000, default cam at -1500
    wy = -ty * (10500.0 - wz) / 1500.0
    return K.Cam(pos=(0.0, wy, -1500.0 + wz), focal=1500.0, aperture=APERTURE, focus_dist=1500.0 - wz)


# ============================================================================================ assets
def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def meta(pose):
    return FA.meta(pose)


def _smooth(e0, e1, x):
    x = np.clip((x - e0) / (e1 - e0), 0, 1)
    return x * x * (3 - 2 * x)


def skin_mask(lz_bgr, m):
    """Face / ear / neck skin of the Lanczos source (hue <= 30-45 deg or >= 345, saturation 0.10-0.75, value >= 0.42),
    inside the dilated face box, eroded 2 px and feathered 3 px. Brows, lashes, irises, beard and hair are dark or
    unsaturated and fall outside it."""
    hsv = cv2.cvtColor(np.clip(lz_bgr, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0] * 2.0, hsv[..., 1] / 255.0, hsv[..., 2] / 255.0
    hue = np.clip(1.0 - np.maximum(h - 30.0, 0) / 15.0, 0, 1) * (h <= 60)
    hue = np.maximum(hue, (h >= 345).astype(np.float32))
    sk = hue * _smooth(0.10, 0.18, s) * (1 - _smooth(0.62, 0.75, s)) * _smooth(0.42, 0.55, v)
    fx0, fy0, fx1, fy1 = m['face_box']
    box = np.zeros(sk.shape, np.float32)
    box[max(0, int(fy0 - 60)):int(fy1 + 80), max(0, int(fx0 - 120)):int(fx1 + 120)] = 1
    sk = cv2.erode(((sk * box) > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    return np.clip(cv2.GaussianBlur(sk, (0, 0), 3), 0, 1)


@functools.lru_cache(maxsize=8)
def _sources(pose):
    """(cut BGRA uint8, sr BGR float, lanczos2x BGR float) at the 2x master size."""
    cut = cv2.imread(os.path.join(CUT, pose + '.png'), cv2.IMREAD_UNCHANGED)
    sr = cv2.imread(os.path.join(CROPS, pose + '_2x.png')).astype(np.float32)
    nat = cv2.imread(os.path.join(CROPS, pose + '.png'))
    lz = cv2.resize(nat.astype(np.float32), (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    return cut, sr, lz


def textured_rgb(pose, k=None):
    """Straight-alpha sRGB float (0..255, BGR) of the cut-out with the skin-only SR pull-back, and its alpha 0..1.
    Only the opaque interior is touched (the decontaminated matte edge stays as cut)."""
    cut, sr, lz = _sources(pose)
    k = TEX_K.get(pose, 1.0) if k is None else k
    a = cut[..., 3].astype(np.float32) / 255.0
    rgb = cut[..., :3].astype(np.float32)
    if k < 1.0:
        sk = skin_mask(lz, meta(pose))
        core = cv2.erode((a > 0.99).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        w = cv2.GaussianBlur(core.astype(np.float32), (0, 0), 2.0) * sk
        rgb = rgb + ((k - 1.0) * w)[..., None] * (sr - lz)
    return np.clip(rgb, 0, 255), a


@functools.lru_cache(maxsize=8)
def plain(pose):
    """Premultiplied linear sprite of the texture-corrected cut-out (read-only)."""
    rgb, a = textured_rgb(pose)
    lin = K.to_lin(rgb[..., ::-1] / 255.0).astype(np.float32)
    return _ro(FA.premult(lin, a))


def cheek_ratio(pose, k=None):
    """Cheek-patch Laplacian variance of the shipped texture / the 2x Lanczos source (float luma, meta cheek_patch)."""
    _, _, lz = _sources(pose)
    rgb, _ = textured_rgb(pose, k)
    x0, y0, x1, y1 = meta(pose)['cheek_patch']
    lw = np.float32([0.114, 0.587, 0.299])

    def lv(img):
        return float(cv2.Laplacian(np.ascontiguousarray((img @ lw)[y0:y1, x0:x1]), cv2.CV_32F).var())
    return lv(rgb) / max(lv(lz), 1e-6)


def _screen_of_sprite(pose, s=S0):
    """Screen x, y grids of the cut-out pixels at scale s with the eye midpoint on EYES (for the phone uplight)."""
    p = plain(pose)
    h, w = p.shape[:2]
    ex, ey = EYE_MID[pose]
    xs = EYES[0] + (np.arange(w, dtype=np.float32) + 0.5 - ex) * s
    ys = EYES[1] + (np.arange(h, dtype=np.float32) + 0.5 - ey) * s
    return xs, ys


def _phone_light(pose):
    """Amber uplight from the phone below frame, ALBEDO-modulated (light x surface colour): the white shirt, the
    collar and the underside of the jaw warm up, the black suit stays black, no shading change on the features."""
    p = plain(pose)
    a = p[..., 3]
    alb = FA.unpremult(p)
    xs, ys = _screen_of_sprite(pose)
    cx, cy = PHONE['center']
    r = np.sqrt((xs[None, :] - cx) ** 2 + (ys[:, None] - cy) ** 2) / PHONE['radius']
    fall = np.clip(1.0 - r, 0, 1) ** 2
    col = np.asarray(K.C['AMBER'], np.float32)
    out = np.zeros_like(p)
    out[..., :3] = alb * col * (PHONE['strength'] * fall * a)[..., None]
    return out


def _shade(pose, base, kind):
    """Torso fill falloff below the chin and a soft highlight shoulder on the subject (colour ratios kept: the
    luminance is compressed, the hue / saturation of shirt and skin stay). Face values sit under the knee."""
    m = meta(pose)
    a = base[..., 3]
    h = a.shape[0]
    ys = np.arange(h, dtype=np.float32)
    y0 = m['face_box'][3] + TORSO_FALL['start']
    f = 1.0 - (1.0 - TORSO_FALL['bottom']) * _smooth(y0, float(h), ys)
    out = base * np.concatenate([np.repeat(f[:, None], 3, 1), np.ones((h, 1), np.float32)], 1)[:, None, :]
    rgb = FA.unpremult(out)
    Y = K.lum(rgb)
    k0, ym = KNEE['k0'], KNEE['ymax']                                 # one knee: D is exposure-matched to A (BASE_D)
    Yc = np.where(Y > k0, k0 + (ym - k0) * (1.0 - np.exp(-(Y - k0) / (ym - k0))), Y)
    g = np.where(Y > 1e-6, Yc / np.maximum(Y, 1e-6), 1.0).astype(np.float32)
    out[..., :3] *= g[..., None]
    return out


def _split_masks(m, off, shape):
    """Head mask (feathered head box, hair + halo above included) and the exact-recombination torso weight:
    head = L * mk, torso = L * wt with wt = (1 - mk) / (1 - mk * a), so head OVER torso == L at zero offset."""
    H, W = shape
    hx0, hy0, hx1, hy1 = m['head_box']
    dx, dy = off
    fe = 0.08 * (hx1 - hx0)
    mk = np.zeros((H, W), np.float32)
    mk[0:int(hy1 + dy), int(max(0, hx0 + dx - fe)):int(min(W, hx1 + dx + fe))] = 1
    mk = np.clip(cv2.GaussianBlur(mk, (0, 0), fe / 2) * 2.0, 0, 1)
    return mk, fe


@functools.lru_cache(maxsize=12)
def look(pose, kind='A', phone=False, rim_dir=(0.8, -0.5), rim_back=None):
    """Build a pose's layers ONCE (read-only): base (warm_dark A / cine_grade D, + phone uplight), rim emission (FA
    rim_light on a zero base, so it can follow the window light), split into a rigid head layer and a torso layer,
    the torso depth offsets and the anchors. Coordinates: 'hero' = the padded look canvas."""
    p = plain(pose)
    m = meta(pose)
    dep = FA.depth(pose)
    h, w = p.shape[:2]
    a = np.ascontiguousarray(p[..., 3])
    rim_kw = dict(RIM_A if kind == 'A' else RIM_D)
    if rim_back is not None:
        rim_kw['back'] = rim_back
    base = FA.warm_dark(p, **BASE_A) if kind == 'A' else FA.cine_grade(p, **BASE_D)
    if phone:
        base = base + _phone_light(pose)
    base = _shade(pose, base, kind)
    if VEIL[kind] > 0:
        base[..., :3] += np.asarray(K.C['NIGHT_1'], np.float32) * VEIL[kind] * base[..., 3:4]
    zero = FA.premult(np.zeros((h, w, 3), np.float32), a)
    em = FA.rim_light(p, dep, light=rim_dir, base=zero, **rim_kw)       # emission only (+ alpha of the silhouette)
    dx, dy = FA.offset(p, em)
    H, W = em.shape[:2]
    baseP = np.zeros((H, W, 4), np.float32)
    baseP[dy:dy + h, dx:dx + w] = base
    emP = np.ascontiguousarray(em, np.float32).copy()
    emP[..., 3] = 0.0                                                    # pure light: alpha comes from the base
    # soft blend of the panel-cut sides (base and rim) into the dark wall under the sill
    fade = FA.fade_open(np.dstack([np.ones((H, W, 3), np.float32), baseP[..., 3:4]]), sides=('left', 'right'),
                        frac=FADE_FRAC)[..., 0]
    baseP *= fade[..., None]
    emP[..., :3] *= fade[..., None]
    mk, fe = _split_masks(m, (dx, dy), (H, W))
    al = baseP[..., 3]
    den = 1.0 - mk * al
    wt = np.where(den > 1e-4, (1.0 - mk) / np.maximum(den, 1e-4), 0.0).astype(np.float32)
    seam_y = m['head_box'][3] + dy                                       # head layer's lower edge (hero px)
    y_head1 = int(min(H, seam_y + fe + 4))
    xs_head = np.where(mk.max(0) > 1e-3)[0]
    hx0, hx1 = int(xs_head.min()), int(xs_head.max()) + 1
    L = {}
    L['base_head'] = _ro((baseP * mk[..., None])[:y_head1, hx0:hx1])
    L['em_head'] = _ro((emP * mk[..., None])[:y_head1, hx0:hx1])
    L['base_torso'] = _ro(baseP * wt[..., None])
    L['em_torso'] = _ro(emP * wt[..., None])
    L['head_off'] = (hx0, 0)                                             # head layer origin in hero px
    # torso micro-parallax: depth offsets (units, + = further than the torso plane), flattened to 0 under the head
    # layer and its seam (the head never warps and the seam never opens), blurred sigma 6 px
    d = FA.depth_like(pose, p, em)
    d = cv2.GaussianBlur(np.ascontiguousarray(d, np.float32), (0, 0), 6)
    torso_ref = float(np.median(d[int(seam_y):][al[int(seam_y):] > 0.9])) if (al[int(seam_y):] > 0.9).any() else 0.5
    keep = np.clip(1.0 - cv2.GaussianBlur(mk, (0, 0), fe / 2) * 1.6, 0, 1)
    L['delta'] = _ro((torso_ref - d) * DEPTH_RANGE * keep)
    L['eye'] = (EYE_MID[pose][0] + dx, EYE_MID[pose][1] + dy)           # hero px (hand-marked canthi midpoint)
    L['_dist'] = _ro(np.sqrt((np.arange(W, dtype=np.float32)[None, :] - L['eye'][0]) ** 2 +
                             (np.arange(H, dtype=np.float32)[:, None] - L['eye'][1]) ** 2))
    L['pivot'] = (dx + w / 2.0, dy + h)                                  # bust bottom centre (sway pivot, hero px)
    L['seam_y'] = float(seam_y)
    L['shape'] = (H, W)
    L['off'] = (dx, dy)
    L['plain_pad'] = _ro(np.pad(p, ((dy, H - h - dy), (dx, W - w - dx), (0, 0))))
    L['alpha_hero'] = _ro(al)
    return L


def _look_for(key):
    d = SHOTS[key]
    return look(d['pose'], d['kind'], d['phone'], tuple(d['rim_dir']), d.get('rim_back'))


def prewarm():
    for d in FACES:
        _look_for(d['key'])
    _fill_table()


# ============================================================================================ motion
BREATH, BREATH_PERIOD = 0.004, 3.4        # torso layer only: 0.4 % at 0.29 Hz
SWAY_DEG, BOB_PX = 0.25, 1.5              # subject micro-sway about the bust bottom, drift in screen px


def idle(key, t):
    """(dx, dy, roll_deg, breath) of the subject on the shot clock tau (continuous across the S12 -> S0 loop)."""
    d = SHOTS[key]
    tau = t + d['tau_off']
    sd = d['idle_seed']
    br = BREATH * math.sin(2 * math.pi * tau / BREATH_PERIOD + sd)
    return (K.wiggle(tau, 0.16, BOB_PX, sd), K.wiggle(tau, 0.13, BOB_PX * 0.6, sd + 7),
            K.wiggle(tau, 0.20, SWAY_DEG, sd + 3), br)


def _planes(key, t):
    """World placement of the two layers at time t: dict(cam, head=(center, width, height, anchor, rot),
    torso=(...), rot, breath, idle)."""
    d = SHOTS[key]
    L = _look_for(key)
    t_ref = d['t_push0'] - d['tau_off']
    _, _, Dh0 = _cam_state(key, t_ref)
    c = cam(key, t)
    dxs, dys, roll, br = idle(key, t)
    ex, ey = L['eye']
    px, py = L['pivot']
    H, W = L['shape']
    uh = 1.0                                         # world units per hero px on the head plane (1 unit ~ 0.44 mm)
    ut = (Dh0 + Z_TORSO) / Dh0                       # ... on the torso plane (registers with the head at t_push0)
    # eye points: head eye at the origin; torso eye on the same camera ray (registered at t_push0)
    e_off = EYES[1] - K.CY
    Eh = np.array([0.0, 0.0, 0.0])
    Et = np.array([0.0, e_off * Z_TORSO / F85, Z_TORSO])
    # subject idle (screen px at the head -> world), applied to both layers (rigid bust)
    sh = np.array([dxs / S0, dys / S0, 0.0])
    r = math.radians(roll)
    R2 = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])

    def place(E, u, ox, oy, lw, lh, piv_extra=(0.0, 0.0), sy=1.0):
        """Plane whose layer px (x, y) (layer origin at hero (ox, oy)) maps so that hero eye -> E; rotation `roll`
        about the bust-bottom pivot; returns (center, width, height, anchor)."""
        pv = np.array([px - ex, py - ey]) * u                         # pivot relative to the eye (world, unrotated)
        center = E + np.array([pv[0], pv[1], 0.0]) + sh
        center[:2] += np.asarray(piv_extra)
        anchor = ((px - ox) / lw, (py - oy) / lh)
        return center, lw * u, lh * u * sy, anchor

    # torso: breathing = height scale about the bottom pivot
    tor = place(Et, ut, 0, 0, W, H, sy=1.0 + br)
    # head: rides on the torso: lifted by the torso's displacement at the seam, rotated with the bust
    lift = br * (py - L['seam_y']) * uh
    lv = R2 @ np.array([0.0, -lift])
    hd_h, hd_w = L['base_head'].shape[:2]
    hox, hoy = L['head_off']
    hea = place(Eh, uh, hox, hoy, hd_w, hd_h, piv_extra=lv)
    rot = (0.0, 0.0, roll)
    return dict(cam=c, head=hea, torso=tor, rot=rot, breath=br, idle=(dxs, dys, roll))


def _project(c, P):
    q, _ = c.project(np.atleast_2d(P))
    return q[0]


def _layer_point(plane, rot, uv_px, lw, lh):
    center, width, height, anchor = plane
    return K.plane_point(center, width, height, rot, uv=(uv_px[0] / lw, uv_px[1] / lh), anchor=anchor)


def eye_point(key, t):
    """Screen position of the eye midpoint (head layer) at time t, idle included."""
    P = _planes(key, t)
    L = _look_for(key)
    hd_h, hd_w = L['base_head'].shape[:2]
    hox, hoy = L['head_off']
    ex, ey = L['eye']
    w = _layer_point(P['head'], P['rot'], (ex - hox, ey - hoy), hd_w, hd_h)
    return tuple(float(v) for v in _project(P['cam'], w))


def _hero_to_screen(key, t, pts, layer='head'):
    P = _planes(key, t)
    L = _look_for(key)
    if layer == 'head':
        lh, lw = L['base_head'].shape[:2]
        ox, oy = L['head_off']
    else:
        lh, lw = L['shape']
        ox, oy = 0, 0
    out = []
    for (x, y) in pts:
        w = _layer_point(P[layer], P['rot'], (x - ox, y - oy), lw, lh)
        out.append(_project(P['cam'], w))
    return np.array(out)


def face_rect(key, t):
    """Screen box of the YuNet face box (head layer)."""
    L = _look_for(key)
    m = meta(SHOTS[key]['pose'])
    dx, dy = L['off']
    x0, y0, x1, y1 = m['face_box']
    q = _hero_to_screen(key, t, [(x0 + dx, y0 + dy), (x1 + dx, y0 + dy), (x1 + dx, y1 + dy), (x0 + dx, y1 + dy)])
    return (float(q[:, 0].min()), float(q[:, 1].min()), float(q[:, 0].max()), float(q[:, 1].max()))


def head_rect(key, t, margin=6.0):
    """BRIEF 6.10 caption avoid rect (head_x0, head_top, head_x1, 1920) at time t, + margin px."""
    L = _look_for(key)
    m = meta(SHOTS[key]['pose'])
    dx, dy = L['off']
    hx0, _, hx1, _ = m['head_box']
    top = m['subject_bbox'][1]
    q = _hero_to_screen(key, t, [(hx0 + dx, top + dy), (hx1 + dx, top + dy)])
    return (float(q[:, 0].min()) - margin, float(q[:, 1].min()) - margin, float(q[:, 0].max()) + margin, float(K.H))


def bust_bottom(key, t):
    """Lowest screen y of the bust's bottom edge (must stay >= 1926 so the panel cut is never seen)."""
    L = _look_for(key)
    H, W = L['shape']
    q = _hero_to_screen(key, t, [(0, H), (W, H), (W / 2, H)], layer='torso')
    return float(q[:, 1].min())


# ============================================================================================ draw
def _torso_micro(key, t, spr):
    """Depth micro-parallax of the torso layer for the dolly: a point delta units behind the torso plane scales about
    the eye by Z0 / (Z0 - dz) instead of Zt0 / (Zt0 - dz): displacement ~ -(p - eye) delta dz / (Zt0 - dz)^2.
    The head layer never warps; the seam band has delta = 0. Returns (sprite, max displacement px)."""
    d = SHOTS[key]
    L = _look_for(key)
    t_ref = d['t_push0'] - d['tau_off']
    _, _, Dh0 = _cam_state(key, t_ref)
    _, _, Dh = _cam_state(key, t)
    dz = Dh0 - Dh
    Zt0 = Dh0 + Z_TORSO
    k = -dz / (Zt0 - dz) ** 2
    delta = L['delta']
    ex, ey = L['eye']
    H, W = delta.shape
    xs = np.arange(W, dtype=np.float32) - ex
    ys = np.arange(H, dtype=np.float32) - ey
    kd = (np.float32(k) * delta)
    dist = L.get('_dist')
    if dist is None:
        dist = np.sqrt(xs[None, :] ** 2 + ys[:, None] ** 2).astype(np.float32)
    mx = float(np.abs(kd * dist * (L['alpha_hero'] > 0.02)).max())
    if mx < DEPTH_MIN_PX:
        return spr, mx
    mapx = (np.arange(W, dtype=np.float32)[None, :] - kd * xs[None, :])
    mapy = (np.arange(H, dtype=np.float32)[:, None] - kd * ys[:, None])
    out = cv2.remap(np.ascontiguousarray(spr), mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                    borderValue=(0, 0, 0, 0))
    return out, mx


def sill(cv, key, t):
    """The wall under the window sill, drawn BEHIND JD: the gold_hour horizon band (sun core behind his chest) ends at a
    soft sill line and the plate below falls to near-black (NIGHT_0, 86 %), so the panel-cut sides of the bust sit in
    shadow instead of against the brightest part of the plate (a cut column there reads as a pasted sticker). The line
    rides the plate (world_cam: scale about the centre + slide), smoothstep y0 -> y1."""
    wc = world_cam(t, key)
    s, _, _, ty = K._bg_transform(wc, 1.0) if wc is not None else (1.0, 0.0, 0.0, 0.0)
    y0 = K.CY + ty + s * (SILL['y0'] - K.CY)
    y1 = K.CY + ty + s * (SILL['y1'] - K.CY)
    r0 = max(0, int(y0) - 1)
    ys = np.arange(r0, cv.shape[0], dtype=np.float32) + 0.5
    a = (SILL['opacity'] * _smooth(y0, y1, ys)).astype(np.float32)[:, None, None]
    night = np.asarray(K.C['NIGHT_0'], np.float32)
    cv[r0:, :, :3] = cv[r0:, :, :3] * (1.0 - a) + night * a


def _wrap(cv, lay, bg, region, width, sigma, amount):
    """Light wrap: the plate behind JD, blurred (sigma px), SCREENED over his outer `width` px."""
    x0, y0, x1, y1 = region
    a = lay[y0:y1, x0:x1, 3]
    if a.max() <= 0.01 or amount <= 0:
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


def _alpha_white(spr):
    out = np.zeros_like(spr)
    out[..., :3] = spr[..., 3:4]
    out[..., 3] = spr[..., 3]
    return out


def draw_face(cv, key, t, mode='full', micro=True):
    """Draw JD for shot `key` at time t onto cv (the world behind him already drawn). mode 'full' (the shot) |
    'plain' (texture-corrected cut-out only, no look / sill / wrap: matte QA) | 'alpha' (white silhouette).
    Returns dict(bbox, eye, micro_px, gain)."""
    L = _look_for(key)
    P = _planes(key, t)
    c, rot = P['cam'], P['rot']
    g = window_gain(t)
    if mode == 'full':
        base_k = g if g < 1.0 else 1.0 + 0.3 * (g - 1.0)    # the room bounce IS window light: it dims with it (S6);
                                                             # the S10 swell lifts it a little (the sun is the key)
        kk = np.float32([base_k, base_k, base_k, 1.0])                # light only: alpha is never scaled
        head = L['base_head'] * kk + L['em_head'] * np.float32(g)
        torso = L['base_torso'] * kk + L['em_torso'] * np.float32(g)
        sill(cv, key, t)
    else:
        pp = L['plain_pad']
        mk_t = L['base_torso'][..., 3:4] / np.maximum(L['alpha_hero'][..., None], 1e-6)
        torso = pp * np.clip(mk_t, 0, 1)
        hox, hoy = L['head_off']
        hh, hw = L['base_head'].shape[:2]
        mk_h = L['base_head'][..., 3:4] / np.maximum(L['alpha_hero'][hoy:hoy + hh, hox:hox + hw, None], 1e-6)
        head = pp[hoy:hoy + hh, hox:hox + hw] * np.clip(mk_h, 0, 1)
        if mode == 'alpha':
            torso, head = _alpha_white(torso), _alpha_white(head)
    micro_px = 0.0
    if micro:
        torso, micro_px = _torso_micro(key, t, torso)
    lay = np.zeros_like(cv)
    it = K.draw_plane(lay, np.ascontiguousarray(torso), c, P['torso'][0], P['torso'][1], rot=rot,
                      height=P['torso'][2], anchor=P['torso'][3])
    ih = K.draw_plane(lay, np.ascontiguousarray(head), c, P['head'][0], P['head'][1], rot=rot,
                      height=P['head'][2], anchor=P['head'][3])
    boxes = [i['bbox'] for i in (it, ih) if i]
    if not boxes:
        return None
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    pad = int(WRAP['sigma'] * 2)
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(cv.shape[1], x1 + pad), min(cv.shape[0], y1 + pad)
    bg = cv[Y0:Y1, X0:X1].copy() if mode == 'full' else None
    a = lay[Y0:Y1, X0:X1, 3:4]
    cv[Y0:Y1, X0:X1] = lay[Y0:Y1, X0:X1] + cv[Y0:Y1, X0:X1] * (1.0 - a)
    if mode == 'full':
        _wrap(cv, lay, bg, (X0, Y0, X1, Y1), WRAP['width'], WRAP['sigma'], WRAP['amount'] * min(g, 1.2))
    return dict(bbox=(x0, y0, x1, y1), eye=eye_point(key, t), micro_px=micro_px, gain=g)


def jd_alpha(key, t):
    """(1920, 1080) float32 screen alpha of JD at time t (QA: face pixels under UI, caption masks)."""
    lay = np.zeros((K.H, K.W, 4), np.float32)
    draw_face(lay, key, t, mode='alpha', micro=False)
    return lay[..., 3].copy()


# ============================================================================================ QA (python3 <this> check)
def _luma(u8):
    return u8[..., 0] * 0.2126 + u8[..., 1] * 0.7152 + u8[..., 2] * 0.0722


def shot_frames(key):
    d = SHOTS[key]
    return list(range(d['f0'], d['f1']))


def _frame_u8(t, finish=True, samples=1):
    """A finished preview frame (world + JD + stand-ins) as uint8 RGB, through the preview harness."""
    import beta_tum_karte_kya_ho_faces_preview as PV
    cv = K.render_frame(PV.draw, t, samples)
    if finish:
        cv = PV.post(cv, t)
    return K.to_srgb8(cv, t, dither=False)


def _halo_ring(key, t, mode):
    """Mean luma (8-bit, no finish) of a 3 px ring OUTSIDE JD's alpha 0.5 minus the plate's, over the plate he stands
    on (gold_hour world + sill). The panel-cut sides / bottom (faded on purpose) are excluded."""
    wc = world_cam(t, key)
    plate = K.background(LOOK, t, wc, bokeh=0.0, intensity=window_gain(t))
    sill(plate, key, t)
    comp = plate.copy()
    draw_face(comp, key, t, mode=mode, micro=False)
    a = jd_alpha(key, t)
    m = (a > 0.5).astype(np.uint8)
    ring = (cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) - m).astype(bool)
    L = _look_for(key)
    ring[int(min(K.H, bust_bottom(key, t) - 60)):] = False
    # exclude the cut sides: columns within 60 px of the bust's left / right screen edges below the shoulders
    q = _hero_to_screen(key, t, [(0, L['shape'][0] * 0.5), (L['shape'][1], L['shape'][0] * 0.5)], layer='torso')
    xl, xr = int(q[0][0]) + 60, int(q[1][0]) - 60
    yc = int(_hero_to_screen(key, t, [(0, L['shape'][0] * 0.55)], layer='torso')[0][1])
    side = np.zeros_like(ring)
    side[yc:, :max(0, xl)] = True
    side[yc:, max(0, xr):] = True
    ring &= ~side
    lp = _luma(K.to_srgb8(plate, t, dither=False).astype(np.float32))
    lc = _luma(K.to_srgb8(comp, t, dither=False).astype(np.float32))
    return float((lc[ring] - lp[ring]).mean()), float(np.percentile(lc[ring] - lp[ring], 95)), int(ring.sum())


def _parallax(key):
    """Per-frame screen motion (px/frame, max over the shot) of head points, torso points and the plate at the same
    screen points; head-to-plate relative speed in % of the frame width per second."""
    L = _look_for(key)
    m = meta(SHOTS[key]['pose'])
    dx, dy = L['off']
    hx0, _, hx1, hy1 = m['head_box']
    top = m['subject_bbox'][1]
    ex, ey = L['eye']
    hp = [(ex, top + dy + 4), (hx0 + dx, ey), (hx1 + dx, ey), (ex, m['face_box'][3] + dy)]
    H, W = L['shape']
    tp = [(30, H * 0.62), (W - 30, H * 0.62), (W * 0.5, H * 0.75)]
    fr = shot_frames(key)
    prev = None
    out = dict(head=0.0, torso=0.0, plate=0.0, rel=0.0)
    for f in fr:
        t = f / FPS
        qh = _hero_to_screen(key, t, hp, 'head')
        qt = _hero_to_screen(key, t, tp, 'torso')
        wc = world_cam(t, key)
        s, rot, tx, ty = K._bg_transform(wc, 1.0)
        if prev is not None:
            ph, pt, (ps, prot, ptx, pty) = prev
            dh = np.hypot(*(qh - ph).T)
            dt_ = np.hypot(*(qt - pt).T)
            # plate point under each head point at the previous frame -> where it is now
            pp = (ph - [K.CX + ptx, K.CY + pty]) / ps
            pn = pp * s + [K.CX + tx, K.CY + ty]
            dp = np.hypot(*(pn - ph).T)
            rel = np.hypot(*((qh - ph) - (pn - ph)).T)
            out['head'] = max(out['head'], float(dh.max()))
            out['torso'] = max(out['torso'], float(dt_.max()))
            out['plate'] = max(out['plate'], float(dp.max()))
            out['rel'] = max(out['rel'], float(rel.max()) * FPS / K.W * 100.0)
        prev = (qh, qt, (s, rot, tx, ty))
    return {k: round(v, 3) for k, v in out.items()}


def eye_measured(u8, key, t, rx=130, ry=45, search=40):
    """Independent check of where the eyes really land in a rendered frame: the plain cut-out's eye band (EYE_MID
    +- rx, ry, cut-out px) scaled to the shot's scale is template-matched (normalised cross-correlation of the gradient
    magnitude, so the grade does not matter) inside +- search px of the expected point. Returns ((x, y), score)."""
    pose = SHOTS[key]['pose']
    p = plain(pose)
    ex, ey = EYE_MID[pose]
    sub = p[int(ey - ry):int(ey + ry), int(ex - rx):int(ex + rx)]
    s_ = scale(key, t)
    rgb = sub[..., :3] + (1 - sub[..., 3:4]) * 0.18
    g = K.to_srgb(np.clip(K.lum(rgb), 0, 1)).astype(np.float32)
    g = cv2.resize(g, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA)

    def grad(im):
        im = cv2.GaussianBlur(im, (0, 0), 1.0)
        return cv2.magnitude(cv2.Sobel(im, cv2.CV_32F, 1, 0), cv2.Sobel(im, cv2.CV_32F, 0, 1))
    tpl = grad(g)
    fr = _luma(u8.astype(np.float32)) / 255.0
    exp_ = eye_point(key, t)
    cx0 = int(exp_[0] - rx * s_ - search)
    cy0 = int(exp_[1] - ry * s_ - search)
    win = grad(np.ascontiguousarray(fr[cy0:cy0 + tpl.shape[0] + 2 * search, cx0:cx0 + tpl.shape[1] + 2 * search]))
    res = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
    _, mxv, _, loc = cv2.minMaxLoc(res)
    # sub-pixel peak (parabola fit)
    x, y = loc
    dxs = dys = 0.0
    if 0 < x < res.shape[1] - 1:
        l_, c_, r_ = res[y, x - 1], res[y, x], res[y, x + 1]
        dxs = 0.5 * (l_ - r_) / max(l_ - 2 * c_ + r_, -1e9) if (l_ - 2 * c_ + r_) < 0 else 0.0
    if 0 < y < res.shape[0] - 1:
        u_, c_, d_ = res[y - 1, x], res[y, x], res[y + 1, x]
        dys = 0.5 * (u_ - d_) / max(u_ - 2 * c_ + d_, -1e9) if (u_ - 2 * c_ + d_) < 0 else 0.0
    mx_ = cx0 + x + dxs + (ex - int(ex - rx)) * s_
    my_ = cy0 + y + dys + (ey - int(ey - ry)) * s_
    return (float(mx_), float(my_)), float(mxv)


def check(render=True):
    import jawad_grade as G
    rep = dict(texture={}, shots={}, source_skin={})
    for pose in POSES:
        p = plain(pose)
        u8 = K.to_srgb8(np.ascontiguousarray(p[..., :3] + (1 - p[..., 3:4]) * 0.5), 0.0, dither=False)
        fx0, fy0, fx1, fy1 = [int(v) for v in meta(pose)['face_box']]
        rep['source_skin'][pose] = G.skin_stats(u8, (fx0, fy0, fx1 - fx0, fy1 - fy0))
    for pose in POSES:
        rep['texture'][pose] = dict(k=TEX_K[pose], cheek_ratio_shipped=round(cheek_ratio(pose), 3),
                                    cheek_ratio_sr=round(cheek_ratio(pose, 1.0), 3))
    prewarm()
    for d in FACES:
        key = d['key']
        fr = shot_frames(key)
        ts = [f / FPS for f in fr]
        sc = [scale(key, t) for t in ts]
        eyes = np.array([eye_point(key, t) for t in ts])
        eoff = np.hypot(eyes[:, 0] - EYES[0], eyes[:, 1] - EYES[1])
        rates = [(scale(key, t + 0.002) / scale(key, t) - 1) / 0.002 * 100 for t in ts]
        idl = [idle(key, t) for t in ts]
        r = dict(frames=[fr[0], fr[-1]], t=[round(ts[0], 3), round(ts[-1] + 1 / FPS, 3)], pose=d['pose'],
                 look=d['kind'], dur_s=round(len(fr) / FPS, 3),
                 scale=[round(min(sc), 4), round(max(sc), 4)], push_max_pct_s=round(max(rates), 2),
                 eye_max_off_px=round(float(eoff.max()), 2), eye_first=[round(v, 1) for v in eyes[0]],
                 eye_last=[round(v, 1) for v in eyes[-1]],
                 roll_max_deg=round(max(abs(i[2]) for i in idl), 3),
                 breath_max_pct=round(max(abs(i[3]) for i in idl) * 100, 3),
                 face_first=[round(v) for v in face_rect(key, ts[0])], face_last=[round(v) for v in face_rect(key, ts[-1])],
                 head_rect_first=[round(v) for v in head_rect(key, ts[0])],
                 bust_bottom_min=round(min(bust_bottom(key, t) for t in ts), 1),
                 parallax=_parallax(key))
        # torso micro-parallax: measured on the real layer at the last frame (largest dolly)
        L = _look_for(key)
        _, mpx = _torso_micro(key, ts[-1], L['base_torso'])
        r['micro_px_max'] = round(mpx, 3)
        # cost
        cvb = K.background(LOOK, ts[len(ts) // 2])
        t0 = time.time()
        for t in ts[:: max(1, len(ts) // 5)][:5]:
            c2 = cvb.copy()
            draw_face(c2, key, t)
        r['ms_per_draw_face'] = round((time.time() - t0) * 1000 / min(5, len(ts[:: max(1, len(ts) // 5)][:5])), 1)
        # guards: JD never becomes see-through or subtracts light (alpha <= 1, canvas >= 0) at start / mid / end
        bad = []
        for t in (ts[0], ts[len(ts) // 2], ts[-1]):
            c2 = K.background(LOOK, t, world_cam(t, key), bokeh=0.6, intensity=window_gain(t))
            lay = np.zeros_like(c2)
            draw_face(lay, key, t)
            draw_face(c2, key, t)
            if float(lay[..., 3].max()) > 1.0 + 1e-4 or float(c2[..., :3].min()) < -1e-4:
                bad.append(round(t, 3))
        r['guard_alpha_le1_canvas_ge0'] = 'ok' if not bad else bad
        # copy distance: the brief's text rects over this shot vs the face rect (>= 60 px)
        texts = {'S0': [(147, 280, 933, 740)], 'S12': [(147, 280, 467, 420)], 'S3': [], 'S6': [(150, 280, 930, 520)],
                 'S10': [(147, 280, 933, 790)]}[key]
        fr0 = min((face_rect(key, t) for t in ts), key=lambda b: b[1])
        r['copy_gap_px'] = round(min([fr0[1] - b[3] for b in texts]), 1) if texts else None
        tm = ts[len(ts) // 2]
        # the scene's key: the plate's brightest light behind / around JD (no UI), finished, 8-bit luma
        pl = K.background(LOOK, tm, world_cam(tm, key), bokeh=0.6, intensity=window_gain(tm))
        if key == 'S10':
            import beta_tum_karte_kya_ho_faces_preview as PV
            K.draw(pl, PV._sun(), 540, 1260, mode='add', opacity=1.0 + 0.3 * K.ramp(tm, 30.8, 31.3, 'out_cubic'))
        sill(pl, key, tm)
        G.finish(pl, LOOK, tm, rays=0.0)
        r['plate_key_p99_5'] = round(float(np.percentile(_luma(K.to_srgb8(pl, tm, dither=False).astype(np.float32))
                                                         [1250:1560, 300:780], 99.5)), 1)
        r['halo_plain_cv'] = [round(v, 2) for v in _halo_ring(key, tm, 'plain')[:2]]
        r['halo_look_cv'] = [round(v, 2) for v in _halo_ring(key, tm, 'full')[:2]]
        if render:
            u8 = _frame_u8(tm)
            a = jd_alpha(key, tm)
            inner = cv2.erode((a > 0.98).astype(np.uint8), np.ones((13, 13), np.uint8)).astype(bool)
            inner[1880:] = False
            outer = cv2.dilate((a > 0.01).astype(np.uint8), np.ones((61, 61), np.uint8)) == 0
            lu = _luma(u8.astype(np.float32))
            fx0, fy0, fx1, fy1 = [int(round(v)) for v in face_rect(key, tm)]
            r['luma'] = dict(jd_p2=round(float(np.percentile(lu[inner], 2)), 1),
                             scene_p2=round(float(np.percentile(lu[outer], 2)), 1),
                             jd_p99=round(float(np.percentile(lu[inner], 99)), 1),
                             scene_max=round(float(np.percentile(lu[outer], 99.9)), 1),
                             face_mean=round(float(lu[fy0:fy1, fx0:fx1][inner[fy0:fy1, fx0:fx1]].mean()), 1))
            r['skin'] = G.skin_stats(u8, (fx0, fy0, fx1 - fx0, fy1 - fy0))
            em, score = eye_measured(u8, key, tm)
            r['eye_measured'] = dict(mid=[round(v, 1) for v in em], ncc=round(score, 3),
                                     off_from_EYES_px=round(math.hypot(em[0] - EYES[0], em[1] - EYES[1]), 2),
                                     off_from_model_px=round(math.hypot(em[0] - eye_point(key, tm)[0],
                                                                        em[1] - eye_point(key, tm)[1]), 2))
        rep['shots'][key] = r
    # loop seam S12 -> S0: JD alone over black (no finish), mean |delta| f1091 -> f0 vs a normal step f1090 -> f1091
    def jd_only(f):
        c = np.zeros((K.H, K.W, 4), np.float32)
        draw_face(c, shot_at(f / FPS), f / FPS, micro=True)
        return K.to_srgb8(c, 0.0, dither=False).astype(np.float32)
    a90, a91, a0 = jd_only(1090), jd_only(1091), jd_only(0)
    rep['loop_seam'] = dict(step_f1090_f1091=round(float(np.abs(a91 - a90).mean()), 3),
                            seam_f1091_f0=round(float(np.abs(a0 - a91).mean()), 3),
                            eye_f1091=[round(v, 2) for v in eye_point('S12', 1091 / FPS)],
                            eye_f0=[round(v, 2) for v in eye_point('S0', 0.0)],
                            scale_f1091=round(scale('S12', 1091 / FPS), 5), scale_f0=round(scale('S0', 0.0), 5))
    return rep


def export():
    """Write this reel's face assets for reuse / inspection: <reel ws>/faces/<pose>/{rgba.png (16-bit straight sRGB,
    texture-corrected), depth.png (16-bit, as source), rim_mask.png (8-bit, look A rim emission luma),
    layers/head.png + layers/torso.png (16-bit straight sRGB of look A), meta.json}."""
    out = {}
    for pose in POSES:
        d = os.path.join(ASSET_DIR, pose)
        os.makedirs(os.path.join(d, 'layers'), exist_ok=True)
        rgb, a = textured_rgb(pose)
        img = np.dstack([np.round(rgb * 257.0), np.round(a * 65535.0)]).astype(np.uint16)
        cv2.imwrite(os.path.join(d, 'rgba.png'), img)
        cv2.imwrite(os.path.join(d, 'depth.png'), cv2.imread(os.path.join(CUT, pose + '_depth.png'),
                                                             cv2.IMREAD_UNCHANGED))
        L = look(pose, 'A')
        emf = np.zeros(L['shape'] + (3,), np.float32)
        emf += L['em_torso'][..., :3]
        hox, hoy = L['head_off']
        hh, hw = L['em_head'].shape[:2]
        emf[hoy:hoy + hh, hox:hox + hw] += L['em_head'][..., :3]
        cv2.imwrite(os.path.join(d, 'rim_mask.png'), np.clip(K.lum(emf) / 2.0 * 255, 0, 255).astype(np.uint8))
        for nm, spr in (('head', L['base_head'] + L['em_head']), ('torso', L['base_torso'] + L['em_torso'])):
            al = spr[..., 3:4]
            st = K.to_srgb(np.clip(spr[..., :3] / np.maximum(al, 1e-4), 0, 1))
            im = np.dstack([st[..., ::-1] * 65535.0, al * 65535.0])
            cv2.imwrite(os.path.join(d, 'layers', nm + '.png'), np.round(im).astype(np.uint16))
        m = dict(meta(pose))
        m.update(eye_mid_hand=EYE_MID[pose], eye_corners_hand=EYE_CORNERS[pose],
                 note_eyes='eye_mid_hand (canthi midpoint, marked by hand) is the eye lock; eye_mid is YuNet',
                 tex_k=TEX_K[pose], cheek_ratio=round(cheek_ratio(pose), 3), hero_offset=L['off'],
                 head_layer_offset=L['head_off'], head_pivot_hero=L['pivot'], seam_y_hero=L['seam_y'],
                 layer_z=dict(head=0.0, torso=Z_TORSO, plate=Z_PLATE), focal_px=F85, s0=S0,
                 eye_screen=EYES, sources=dict(cutout=os.path.join(CUT, pose + '.png'),
                                               sr=os.path.join(CROPS, pose + '_2x.png'),
                                               native=os.path.join(CROPS, pose + '.png')))
        with open(os.path.join(d, 'meta.json'), 'w') as f:
            json.dump(m, f, indent=1)
        out[pose] = d
    return out


def boards():
    """200 % edge boards of the shipped cut-outs (texture-corrected, plain) over black / FLAME / white: hair crest,
    ear + beard edge, and (hand pose) the fingers. -> <reel ws>/out/faces_preview/boards/edges_<pose>.jpg"""
    od = os.path.join(REEL_WS, 'out', 'faces_preview', 'boards')
    os.makedirs(od, exist_ok=True)
    bgs = [(0.0, 0.0, 0.0), tuple(K.C['FLAME']), (1.0, 1.0, 1.0)]
    paths = []
    for pose in POSES:
        p = plain(pose)
        m = meta(pose)
        ex, ey = EYE_MID[pose]
        fx0, fy0, fx1, fy1 = m['face_box']
        crops = [(int(ex - 180), 0, int(ex + 180), 200),                              # hair crest
                 (max(0, int(fx0 - 150)), int(ey - 40), int(fx0 + 110), int(ey + 220)),   # left ear / beard edge
                 (int(fx1 - 110), int(ey - 40), min(p.shape[1], int(fx1 + 150)), int(ey + 220))]
        if pose == 'suit_hand_on_chest':
            crops.append((260, 850, 620, 1050))
        rows = []
        for (x0, y0, x1, y1) in crops:
            sub = p[y0:y1, x0:x1]
            cols = []
            for b in bgs:
                c = np.asarray(b, np.float32) * (1 - sub[..., 3:4]) + sub[..., :3]
                u8 = K.to_srgb8(np.ascontiguousarray(c), 0.0, dither=False)
                u8 = cv2.resize(u8, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
                cols.append(u8)
                cols.append(np.full((u8.shape[0], 6, 3), 128, np.uint8))
            rows.append(np.hstack(cols[:-1]))
        wmax = max(r.shape[1] for r in rows)
        rows = [np.pad(r, ((0, 6), (0, wmax - r.shape[1]), (0, 0)), constant_values=128) for r in rows]
        path = os.path.join(od, 'edges_%s.jpg' % pose)
        cv2.imwrite(path, np.vstack(rows)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
        paths.append(path)
    return paths


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if cmd == 'check':
        rep = check(render='--no-render' not in sys.argv)
        js = json.dumps(rep, indent=1)
        print(js)
        os.makedirs(os.path.join(REEL_WS, 'out', 'faces_preview'), exist_ok=True)
        with open(os.path.join(REEL_WS, 'out', 'faces_preview', 'check.json'), 'w') as f:
            f.write(js)
    elif cmd == 'export':
        print(json.dumps(export(), indent=1))
    elif cmd == 'boards':
        print('\n'.join(boards()))
    else:
        raise SystemExit('usage: %s [check [--no-render] | export | boards]' % sys.argv[0])
