"""ek_frame_ki_keemat_faces.py - JD's face layers for reel 3, C08 "Ek Frame ki Keemat" (face-compositor).

Owner: face-compositor. The reel module (ek_frame_ki_keemat.py) imports this file and never edits it; this file never
edits the shared toolkit. Plan: BRIEF.md section 14 (face plan) + section 7.2 (layers 04 / 05 / 06) + section 4 (JD rules).
FACES.md (same folder as the brief) has the measured numbers, the stills looked at and every deviation with its reason.

One pose only: `suit_threequarter` (no swaps, no mirroring, no other pose). Rim look A (FA.rim_light, light (0.8, -0.5))
split into THREE frame layers, all with one placement (bust bottom-centre at (330, 1926), scale 0.90 of the 2x master):

    import jawad_kit                                   # FIRST (the reel module does this anyway)
    import ek_frame_ki_keemat_faces as FF
    L = FF.face_layers()          # cached dict: base, rim, halo, shadow, l06, anchor, xy, scale, boxes (+ head masks)
    tl = FF.layer_clock(t)        # BRIEF 7.2 layer clock: t (t < 0.3) | 0.3 (paused, 0.3-26.4) | t - 33.6 (t >= 26.4)

    # assembled frame (playing or paused), drawn in the frame's layer order onto ONE canvas:
    ...layers 01-03 in cv...
    FF.draw_layer(cv, 4, tl)      # 04 chehra: the cut-out (warm-dark base + black match + light wrap from what is in cv)
    FF.draw_layer(cv, 5, tl)      # 05 rim light: emissive rim only (alpha 0, adds light)
    FF.draw_layer(cv, 6, tl)      # 06 saaya: soft shadow (black, offset (-24, +18), sigma 28) + emissive halo
    ...layers 07-12...
    #   or FF.draw_all(cv, tl) for 04 + 05 + 06 in one call

    # exploded states: each layer as its own 1080x1920 pane sprite at tl 0.3 (the pause), drawn as a plane:
    bg = <layers 01-03 composited at tl 0.3>          # only layer 04 uses it (light wrap); keeps panes == assembled
    P4 = FF.pane(4, bg) ; P5 = FF.pane(5) ; P6 = FF.pane(6)                    # (1920, 1080, 4) read-only
    K.draw_plane(cv, P4, cam, (0, 0, z_4), 1080, dof=...)

    FF.idle(tl)          -> (dx, dy, rot_deg, breath) the playing idle, RELATIVE to the pause pose (zero at tl 0.3)
    FF.point(tl, uv)     -> screen px of cut-out px uv (head layer), e.g. FF.point(tl, FF.meta()['eye_mid'])
    FF.eye_screen(tl)    -> screen eye midpoint ((465.7, 1282.0) when paused: the C8 punch centre)
    FF.jd_rect(tl, m=28) -> (x0, y0, x1, y1) screen box of JD's silhouette + m px (caption / copy avoid)
    FF.face_rect(tl)     -> screen face box (BRIEF: x 242-564, y 1120-1564 when paused)
    FF.jd_alpha(tl)      -> (1920, 1080) float32 screen matte of JD (QA masks)
    FF.FACES             -> the shot table (one entry per stretch of screen time)
    python3 ek_frame_ki_keemat_faces.py check            -> limits, placement, texture, black match, halo, cost (JSON)
    tools/heavy.sh python3 ek_frame_ki_keemat_faces.py stills   -> test stills (stand-in world, real look + finish)

Conventions: sprites are premultiplied LINEAR float32 (core.py); screen px, y down. Assets (read only):
workspace/brand_reels/charsheet/cutouts/suit_threequarter.png (Real-ESRGAN x4plus 2x master, BiRefNet-portrait matte,
decontaminated), suit_threequarter_depth.png (Depth-Anything-V2-Small, Apache-2.0), suit_threequarter.json (eyes, boxes).
Never-uncanny: the head (hair, ears, face, beard) is ONE rigid layer in every frame (no warp, no depth displacement); no
blink, no lip motion, no morph, no mirroring; the breathing (<= 0.4 %, 0.29 Hz) scales the torso layer only; sway
<= 0.5 deg roll; display scale 0.90 of the 2x master (<= 1.0; the C8 punch 1.09 is the builder's, f789-f791).
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
RW = '/home/user/100/workspace/jawad_reels/ek_frame_ki_keemat'

# faces.py (the charsheet helper library) imported BY PATH under a private name, so its folder never lands on sys.path
_spec = importlib.util.spec_from_file_location('efk_charsheet_faces', os.path.join(CS, 'tools', 'faces.py'))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

FPS = 30
DUR = 33.6
LOOK = 'ember'
POSE = 'suit_threequarter'
LIGHT = (0.8, -0.5)                 # rim look A: the flame key / god-ray source is top-right (layer 02 rays from (1060, 60))
XY = (330.0, 1926.0)                # screen point of the bust bottom-centre (BRIEF 14 placement)
SCALE = 0.90                        # of the 2x master (<= 1.0)
IDLE_SEED = 4                       # FA.idle(tl, seed=4), applied relative to the pause (tl = 0.3)
BREATHE = 0.0025                    # FA.idle breathe amplitude (default 0.004): the pause sits at the breathing trough,
                                    # so relative to it the torso scale runs 1.000 -> 1.005 (limit 0.5 %)
T_PAUSE, T_PLAY = 0.3, 26.4         # layer clock (BRIEF 7.2)
SHADOW = dict(sigma=28.0, off=(-24.0, 18.0), k=0.45)   # screen px: blurred matte, offset left-down, black x0.45
EXTEND = 48                         # cut-out px of edge-replicated suit below the panel cut (idle lift guard, see below)
PADX = 120                          # cut-out px of empty padding left / right on every layer (shadow blur room)

# ============================================================================================ tuning (measured, FACES.md)
# Skin texture (human-realism / photo-realism: keep it, never smooth). Real-ESRGAN x4plus gives this pose crisp pores and
# beard on the face, while the open cheek areas stay smooth: the SR cut-out is kept as it is (k = 1.0, no pull-back);
# FACES.md section 5 has the cheek / forehead Laplacian numbers and the side-by-side board that decided it.
TEX_K = 1.0
# Exposure: warm_dark exposure 0.42 (rim look A default). The subject's blacks are lifted to the world's black with a
# NIGHT_0 airlight veil (premultiplied, alpha unchanged) so his suit sits on the same floor as the void (p2 match, after
# the ember finish on f9: veil 0 -> JD p2 1.70, 0.5 -> 2.34, 1.0 -> 3.05 vs the world around him 1.91 code values).
EXPOSURE = 0.42
VEIL = 0.5
# Light wrap: the world behind him (layers 01-03) blurred sigma 30 px and SCREENED over his outer 14 px at 22 %.
WRAP = dict(width=14.0, sigma=30.0, amount=0.22)
# Layered parallax (no per-pixel warp): the head plane leads the torso plane by the depth map's head-vs-torso nearness
# difference (the head layer's idle translation x HEAD_LEAD); breathing scales the torso layer only.
HEAD_LEAD_GAIN = 0.5


def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def meta():
    return FA.meta(POSE)


def layer_clock(t):
    """BRIEF 7.2: tl = t for t < 0.3; 0.3 while paused (0.3 <= t < 26.4); t - 33.6 for t >= 26.4 (the loop's t < 0 world
    uses tl = t, which is the same clock)."""
    if t < T_PAUSE:
        return t
    if t < T_PLAY:
        return T_PAUSE
    return t - DUR


# ============================================================================================ source (read only)
@functools.lru_cache(maxsize=1)
def skin_mask():
    """Feathered skin mask (HSV skin hues inside the eroded matte): QA patches and the optional texture pull-back."""
    cut = cv2.imread(os.path.join(CUT, POSE + '.png'), cv2.IMREAD_UNCHANGED)
    a = cut[..., 3].astype(np.float32) / 255.0
    hsv = cv2.cvtColor(np.ascontiguousarray(cut[..., :3]), cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = (((h <= 22) | (h >= 170)) & (s > 35) & (s < 170) & (v > 95)).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    core = cv2.erode((a > 0.99).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    return _ro(cv2.GaussianBlur((skin * core).astype(np.float32), (0, 0), 3.0))


@functools.lru_cache(maxsize=2)
def rgb_used(k=None):
    """BGR float (0..255 sRGB) of the cut-out with the skin-only SR pull-back k (1.0 = the SR master untouched)."""
    k = TEX_K if k is None else float(k)
    cut = cv2.imread(os.path.join(CUT, POSE + '.png'), cv2.IMREAD_UNCHANGED)
    sr = cut[..., :3].astype(np.float32)
    if k >= 1.0:
        return _ro(sr)
    nat = cv2.imread(os.path.join(CROPS, POSE + '.png'))
    lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    return _ro(np.clip(sr + (k - 1.0) * (sr - lz) * skin_mask()[..., None], 0, 255))


@functools.lru_cache(maxsize=2)
def plain(k=None):
    """Premultiplied linear cut-out (2x master, 764x1112) with the panel-cut bottom edge-extended by EXTEND px.
    The bust bottom is a cut border (open side) that sits 6 px below the frame; the playing idle can lift it a few px,
    so the last suit rows are replicated downward (black suit, shirt, tie: vertical structure, invisible) instead of
    ever showing the cut. Rows below the original 1112 are never on screen while paused."""
    cut = cv2.imread(os.path.join(CUT, POSE + '.png'), cv2.IMREAD_UNCHANGED)
    rgba = np.empty(cut.shape, np.uint16)
    rgba[..., :3] = np.round(rgb_used(k)[..., ::-1] * 257.0).astype(np.uint16)
    rgba[..., 3] = cut[..., 3].astype(np.uint16) * 257
    spr = K.sprite(rgba)
    spr = cv2.copyMakeBorder(spr, 0, EXTEND, 0, 0, cv2.BORDER_REPLICATE)
    return _ro(spr)


@functools.lru_cache(maxsize=1)
def depth():
    """Depth-Anything-V2-Small relative nearness (1 = near), resized / extended like plain()."""
    d = FA.depth(POSE)
    return _ro(cv2.copyMakeBorder(np.ascontiguousarray(d), 0, EXTEND, 0, 0, cv2.BORDER_REPLICATE))


@functools.lru_cache(maxsize=1)
def head_lead():
    """Depth-derived lead of the head plane over the torso plane (layered parallax, no warp): 1 + gain x (median
    nearness inside the face box - median nearness of the torso below the head box)."""
    m = meta()
    d = depth()
    a = plain()[..., 3]
    fx0, fy0, fx1, fy1 = [int(v) for v in m['face_box']]
    dh = float(np.median(d[fy0:fy1, fx0:fx1][a[fy0:fy1, fx0:fx1] > 0.5]))
    hy1 = int(m['head_box'][3])
    tor = d[hy1:1112][a[hy1:1112] > 0.5]
    dt = float(np.median(tor))
    return 1.0 + HEAD_LEAD_GAIN * (dh - dt), dh, dt


# ============================================================================================ the look, split in layers
@functools.lru_cache(maxsize=1)
def face_layers():
    """BRIEF 14 outputs, built once (~3 s) and cached; every sprite is read-only and has the SAME size and anchor:
        base    04 chehra: warm-dark subject (rim_light gain=0, halo 0) + NIGHT_0 black-match veil, fade_open l/r
        rim     05 rim light: rgb(rim_light(halo_strength=0)) - rgb(base), alpha 0 (emissive)
        halo    06 part 1: rgb(full look A) - rgb(no-halo look), alpha 0 (emissive)
        shadow  06 part 2: black, alpha = blur(matte, 28 px) offset (-24, +18) x 0.45 x (1 - matte)
        l06     06 as drawn: shadow alpha + halo rgb in one premultiplied sprite ('over': halo + bg x (1 - shadow))
        anchor  K.draw anchor (fractions) of the bust bottom-centre; draw at xy = (330, 1926) with scale 0.90
        boxes   screen boxes at the pause pose: face, head, eye_mid, eyes, hair_top_y, jd (silhouette bbox), sprite
        head_w  (H, W) float32 head-plane weight per layer key ('base', 'rim', 'halo', 'l06'): head = spr x w_head,
                torso = spr x w_torso (exact: head over torso == spr at zero offset)"""
    p = plain()
    dep = depth()
    m = meta()
    h, w = p.shape[:2]
    base0 = FA.warm_dark(p, exposure=EXPOSURE)
    veil = np.asarray(K.C['NIGHT_0'], np.float32) * VEIL
    base0[..., :3] += veil * base0[..., 3:4]                          # airlight: his blacks meet the world's blacks
    look_base = FA.rim_light(p, dep, light=LIGHT, gain=0.0, halo_strength=0.0, base=base0)
    look_nohalo = FA.rim_light(p, dep, light=LIGHT, halo_strength=0.0, base=base0)
    look_full = FA.rim_light(p, dep, light=LIGHT, base=base0)
    assert look_base.shape == look_nohalo.shape == look_full.shape
    fb = FA.fade_open(look_base, ('left', 'right'))
    fn = FA.fade_open(look_nohalo, ('left', 'right'))
    ff = FA.fade_open(look_full, ('left', 'right'))
    H0, W0 = fb.shape[:2]
    dx0, dy0 = FA.offset(p, look_base)                                 # (0, 144): padded on the top only
    # pad every layer left / right (room for the shadow blur) and bottom (the shadow's downward offset)
    pb = int(SHADOW['sigma'] / SCALE * 3 + 40)

    def padded(s):
        return cv2.copyMakeBorder(np.ascontiguousarray(s), 0, pb, PADX, PADX, cv2.BORDER_CONSTANT, value=0)
    base = padded(fb)
    rim = padded(fn)
    rim[..., :3] -= base[..., :3]
    rim[..., 3] = 0.0
    halo = padded(ff)
    halo[..., :3] -= padded(fn)[..., :3]
    halo[..., 3] = 0.0
    rim[..., :3] = np.maximum(rim[..., :3], 0)
    halo[..., :3] = np.maximum(halo[..., :3], 0)
    H, W = base.shape[:2]
    a = np.ascontiguousarray(base[..., 3])
    sg = SHADOW['sigma'] / SCALE
    ox, oy = SHADOW['off'][0] / SCALE, SHADOW['off'][1] / SCALE
    M = np.float32([[1, 0, ox], [0, 1, oy]])
    sh = cv2.warpAffine(cv2.GaussianBlur(a, (0, 0), sg), M, (W, H), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    sh = np.clip(sh * SHADOW['k'] * (1.0 - a), 0, 1)
    # the bust bottom is a cut: the blurred matte fades toward the pad rows below it; the frame edge hides that
    shadow = np.zeros((H, W, 4), np.float32)
    shadow[..., 3] = sh
    l06 = shadow.copy()
    l06[..., :3] = halo[..., :3]
    ox_c, oy_c = PADX + dx0, dy0                                       # cut-out px -> layer px offset
    pin = (ox_c + 764 / 2.0, oy_c + 1112.0)                            # bust bottom-centre (original cut row)
    anchor = (pin[0] / W, pin[1] / H)
    # rigid head plane vs breathing torso plane (feathered head_box mask), exact recombination per layer
    hx0, hy0, hx1, hy1 = m['head_box']
    fe = 0.08 * (hx1 - hx0)
    mk = np.zeros((H, W), np.float32)
    mk[0:int(hy1 + oy_c), int(max(0, hx0 + ox_c - fe)):int(min(W, hx1 + ox_c + fe))] = 1
    mk = np.clip(cv2.GaussianBlur(mk, (0, 0), fe / 2) * 2.0, 0, 1)
    head_w = {}
    sprites = dict(base=base, rim=rim, halo=halo, shadow=shadow, l06=l06)
    for nm, s in sprites.items():
        al = s[..., 3]
        den = 1.0 - mk * al
        wt = np.where(den > 1e-4, (1.0 - mk) / np.maximum(den, 1e-4), 0.0).astype(np.float32)
        head_w[nm] = (_ro(mk), _ro(wt))
    out = {k: _ro(v) for k, v in sprites.items()}
    out.update(anchor=anchor, xy=XY, scale=SCALE, pin=pin, off=(ox_c, oy_c), shape=(H, W), head_w=head_w,
               neck_y=float(hy1 + oy_c))
    out['boxes'] = _boxes(out)
    return out


def _boxes(L):
    """Screen boxes at the pause pose (no idle)."""
    m = meta()
    ox, oy = L['off']
    px, py = L['pin']

    def sc(u, v):
        return (XY[0] + (u + ox - px) * SCALE, XY[1] + (v + oy - py) * SCALE)
    fx0, fy0, fx1, fy1 = m['face_box']
    hx0, hy0, hx1, hy1 = m['head_box']
    sx0, sy0, sx1, sy1 = m['subject_bbox']
    f0, f1 = sc(fx0, fy0), sc(fx1, fy1)
    h0, h1 = sc(hx0, hy0), sc(hx1, hy1)
    s0, s1 = sc(sx0, sy0), sc(sx1, sy1)
    sp0 = sc(-ox, -oy)
    sp1 = sc(L['shape'][1] - ox, L['shape'][0] - oy)
    return dict(face=(f0[0], f0[1], f1[0], f1[1]), head=(h0[0], h0[1], h1[0], h1[1]), eye_mid=sc(*m['eye_mid']),
                eyes=[sc(*e) for e in m['eyes']], hair_top_y=s0[1], jd=(max(0.0, s0[0]), s0[1], s1[0], min(1920.0, s1[1])),
                sprite=(sp0[0], sp0[1], sp1[0], sp1[1]))


# ============================================================================================ motion (playing only)
@functools.lru_cache(maxsize=1)
def _idle_rest():
    return FA.idle(T_PAUSE, seed=IDLE_SEED, breathe=BREATHE)


def idle(tl):
    """(dx, dy, rot_deg, breath) of FA.idle(tl, seed=4) RELATIVE to its value at the pause (tl = 0.3), so the paused
    pose (every paused frame, every exploded pane, the C8 centre) is exactly the BRIEF placement. breath = the torso
    layer's vertical scale - 1 (the head layer is never scaled); the torso's horizontal breath is 0.4 x that."""
    dx, dy, rot, (sx, sy) = FA.idle(tl, seed=IDLE_SEED, breathe=BREATHE)
    rx, ry, rr, (rsx, rsy) = _idle_rest()
    return dx - rx, dy - ry, rot - rr, (sy - rsy)


def _xf(tl):
    """(C, R, rot, br, head_shift): torso anchor screen point, rotation, breath, extra head translation."""
    dx, dy, rot, br = idle(tl)
    r = math.radians(rot)
    R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    C = np.array([XY[0] + dx, XY[1] + dy])
    lead = head_lead()[0]
    return C, R, rot, br, np.array([dx, dy]) * (lead - 1.0)


def _head_anchor_screen(tl):
    """Screen point where the head plane's pin (bust bottom-centre in layer px) lands at tl."""
    L = face_layers()
    C, R, rot, br, hs = _xf(tl)
    lift = R @ np.array([0.0, -br * SCALE * (L['pin'][1] - L['neck_y'])])   # head rides the breathing neck, unscaled
    return C + lift + hs


def point(tl, uv):
    """Screen px of cut-out pixel uv (head plane) at layer time tl."""
    L = face_layers()
    C, R, rot, br, hs = _xf(tl)
    P = _head_anchor_screen(tl)
    u = np.asarray(uv, np.float64) + np.asarray(L['off'], np.float64) - np.asarray(L['pin'], np.float64)
    return P + R @ (SCALE * u)


def torso_point(tl, uv):
    L = face_layers()
    C, R, rot, br, hs = _xf(tl)
    u = np.asarray(uv, np.float64) + np.asarray(L['off'], np.float64) - np.asarray(L['pin'], np.float64)
    return C + R @ (np.array([SCALE * (1 + 0.4 * br), SCALE * (1 + br)]) * u)


def eye_screen(tl=T_PAUSE):
    return tuple(float(v) for v in point(tl, meta()['eye_mid']))


def face_rect(tl=T_PAUSE):
    x0, y0, x1, y1 = meta()['face_box']
    P = np.array([point(tl, (x0, y0)), point(tl, (x1, y0)), point(tl, (x1, y1)), point(tl, (x0, y1))])
    return (float(P[:, 0].min()), float(P[:, 1].min()), float(P[:, 0].max()), float(P[:, 1].max()))


def jd_rect(tl=T_PAUSE, margin=28):
    x0, y0, x1, y1 = meta()['subject_bbox']
    P = np.array([point(tl, (x0, y0)), point(tl, (x1, y0)), torso_point(tl, (x1, y1)), torso_point(tl, (x0, y1))])
    return (max(0, int(math.floor(P[:, 0].min() - margin))), max(0, int(math.floor(P[:, 1].min() - margin))),
            min(K.W, int(math.ceil(P[:, 0].max() + margin))), min(K.H, int(math.ceil(P[:, 1].max() + margin))))


# ============================================================================================ drawing
@functools.lru_cache(maxsize=16)
def _parts(key):
    """(head, torso) sprites of a layer, each cropped to its content bbox, with the pin's anchor inside the crop."""
    L = face_layers()
    spr = L[key]
    wh, wt = L['head_w'][key]
    out = []
    for wgt in (wh, wt):
        s = spr * wgt[..., None]
        nz = (np.abs(s).max(-1) > 1e-5)
        ys, xs = np.nonzero(nz)
        if len(ys) == 0:
            out.append(None)
            continue
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        c = _ro(s[y0:y1, x0:x1])
        out.append((c, ((L['pin'][0] - x0) / c.shape[1], (L['pin'][1] - y0) / c.shape[0])))
    return tuple(out)


_KEY = {4: 'base', 5: 'rim', 6: 'l06', 'base': 'base', 'rim': 'rim', 'l06': 'l06', 'halo': 'halo', 'shadow': 'shadow'}


def _draw_key(cv, key, tl, opacity=1.0):
    """Draw one layer (head + torso planes) into cv with 'over' (premultiplied; alpha-0 parts add light)."""
    head, torso = _parts(key)
    C, R, rot, br, hs = _xf(tl)
    bbs = []
    if torso is not None:
        s, anc = torso
        bbs.append(K.draw(cv, s, C[0], C[1], scale=(SCALE * (1 + 0.4 * br), SCALE * (1 + br)), rot=rot,
                          anchor=anc, opacity=opacity))
    if head is not None:
        s, anc = head
        P = _head_anchor_screen(tl)
        bbs.append(K.draw(cv, s, P[0], P[1], scale=SCALE, rot=rot, anchor=anc, opacity=opacity))
    bbs = [b for b in bbs if b is not None]
    if not bbs:
        return None
    return (min(b[0] for b in bbs), min(b[1] for b in bbs), max(b[2] for b in bbs), max(b[3] for b in bbs))


def _wrap(cv, lay, bg, region, width, sigma, amount):
    """Light wrap: blur the world behind the subject and SCREEN it over the subject's outer `width` px."""
    x0, y0, x1, y1 = region
    a = lay[y0:y1, x0:x1, 3]
    if a.max() <= 0.01:
        return
    k = max(1, int(round(width)))
    inner = cv2.erode(a, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * k + 1, 2 * k + 1)))
    band = cv2.GaussianBlur(np.clip(a - inner, 0, 1), (0, 0), max(0.8, width * 0.35)) * a
    q = 4
    h, w = bg.shape[:2]
    small = cv2.resize(np.ascontiguousarray(bg[..., :3]), (max(1, w // q), max(1, h // q)), interpolation=cv2.INTER_AREA)
    bl = cv2.resize(cv2.GaussianBlur(small, (0, 0), sigma / q), (w, h), interpolation=cv2.INTER_LINEAR)
    rgb = cv[y0:y1, x0:x1, :3]
    rgb += (amount * band)[..., None] * np.clip(bl, 0, 1) * (1.0 - np.clip(rgb, 0, 1))


def draw_layer(cv, layer, tl, bg=None, opacity=1.0, wrap=True):
    """Draw frame layer 4 (chehra), 5 (rim light) or 6 (saaya) of JD into cv (in place) at layer time tl.
    Layer 4 adds the light wrap from `bg` (the world behind him: layers 01-03 as composited); bg=None uses what is
    already in cv (assembled drawing). Returns the touched bbox."""
    key = _KEY[layer]
    if key != 'base' or not wrap:
        return _draw_key(cv, key, tl, opacity)
    lay = np.zeros_like(cv)
    bb = _draw_key(lay, key, tl, opacity)
    if bb is None:
        return None
    pad = int(WRAP['sigma'] * 2)
    x0, y0, x1, y1 = (max(0, int(bb[0]) - pad), max(0, int(bb[1]) - pad), min(cv.shape[1], int(bb[2]) + pad),
                      min(cv.shape[0], int(bb[3]) + pad))
    src = cv if bg is None else bg
    bgc = np.array(src[y0:y1, x0:x1], np.float32, copy=True)
    a = lay[y0:y1, x0:x1, 3:4]
    cv[y0:y1, x0:x1] = lay[y0:y1, x0:x1] + cv[y0:y1, x0:x1] * (1.0 - a)
    _wrap(cv, lay, bgc, (x0, y0, x1, y1), **WRAP)
    return bb


def draw_all(cv, tl, bg=None, opacity=1.0):
    """Layers 04, 05, 06 in order (assembled frame)."""
    bb = draw_layer(cv, 4, tl, bg=bg, opacity=opacity)
    draw_layer(cv, 5, tl, opacity=opacity)
    draw_layer(cv, 6, tl, opacity=opacity)
    return bb


@functools.lru_cache(maxsize=3)
def _pane_cached(layer):
    cv = np.zeros((K.H, K.W, 4), np.float32)
    draw_layer(cv, layer, T_PAUSE, wrap=False)
    return _ro(cv)


def pane(layer, bg=None):
    """1080x1920 RGBA sprite of frame layer 4 / 5 / 6 at the pause (tl 0.3), for the exploded stack planes. Pass the
    composited layers 01-03 at tl 0.3 as bg for layer 4 so its light wrap equals the assembled frame (then the result
    is not cached here: cache it in the reel's prewarm)."""
    if layer != 4 or bg is None:
        return _pane_cached(layer)
    cv = np.zeros((K.H, K.W, 4), np.float32)
    draw_layer(cv, 4, T_PAUSE, bg=bg)
    return _ro(cv)


def jd_alpha(tl=T_PAUSE):
    """(1920, 1080) float32 screen matte of JD (layer 04's alpha, no glow, no shadow)."""
    cv = np.zeros((K.H, K.W, 4), np.float32)
    _draw_key(cv, 'base', tl)
    return cv[..., 3].copy()


def prewarm():
    face_layers()
    for k in ('base', 'rim', 'l06'):
        _parts(k)
    head_lead()


# ============================================================================================ the shot table

def _faces_table():
    return [
        dict(t0=0.0, t1=0.3, f0=0, f1=8, shot='S1-01 playing', pose=POSE, look='A rim (layers 04 / 05 / 06)',
             P=dict(xy=XY, anchor='bust bottom-centre', eye_mid_screen=(465.7, 1282.0)), width='scale 0.90 of the 2x master',
             cam_keys='screen-locked (85 mm eq., 1:1); idle FA.idle(tl, seed=4) relative to the pause',
             rim_dir=LIGHT, rim_gain=2.4, swap_on_beat=False, note='hook: JD bottom-left, side-eye to the chip'),
        dict(t0=0.3, t1=26.4, f0=9, f1=791, shot='S1-S3 paused / exploded', pose=POSE, look='A rim, one pane per layer',
             P=dict(xy=XY), width='0.90; C8 punch 1.09 at f789-f791 (builder, zoom blur)',
             cam_keys='the stack cameras (BRIEF 7.3); JD is a flat card (honest layer, up to 52 deg yaw by design)',
             rim_dir=LIGHT, rim_gain=2.4, swap_on_beat=False, note='frozen at the pause pose (tl = 0.3)'),
        dict(t0=26.4, t1=33.6, f0=792, f1=1007, shot='S4-01 / S4-02 playing', pose=POSE, look='A rim (layers 04 / 05 / 06)',
             P=dict(xy=XY), width='0.90 (B settles 1.1 -> 1.0 over 6 f: the builder\'s C8)',
             cam_keys='screen-locked; idle relative to the pause; tl = t - 33.6 runs into f0',
             rim_dir=LIGHT, rim_gain=2.4, swap_on_beat=False,
             note='payoff + end card (dimmed x0.58 from 29.4); readable as a person 26.4-29.4 (3.0 s)'),
    ]


FACES = _faces_table()


# ============================================================================================ stand-in world (tests only)
# Not production art: a rough copy of BRIEF 7.2 layers 01-03, 07-11 and the chip, so the face layers are judged in the
# reel's world with the real look ('ember') and the real finish (G.tx_finish with the brief's CUTS).
CUTS = [(0.0, 0.6), (4.8, 0.3), (12.0, 0.35), (20.4, 0.5), (26.4, 0.6)]


@functools.lru_cache(maxsize=1)
def _haze():
    import jawad_tx as X
    n = X.up(X.fbm(11, 5.0))
    ys = np.arange(K.H, dtype=np.float32)[:, None] / K.H
    a = np.clip(n * 0.20 * (0.35 + 0.65 * (1 - ys)), 0, 1)
    out = np.zeros((K.H, K.W, 4), np.float32)
    out[..., :3] = np.asarray(K.C['SMOKE'], np.float32) * 1.8 * a[..., None]
    out[..., 3] = a
    # god rays from (1060, 60): 5 soft shafts, FLAME x0.10 emissive, fading to the bottom
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    ang = np.degrees(np.arctan2(yy - 60, xx - 1060)) % 360
    r = np.hypot(xx - 1060, yy - 60)
    rays = np.zeros((K.H, K.W), np.float32)
    for c, wdt in ((112, 2.0), (118, 1.2), (124, 2.4), (131, 1.5), (138, 1.0)):
        rays += np.exp(-0.5 * ((ang - c) / wdt) ** 2)
    rays = cv2.GaussianBlur(rays, (0, 0), 32) * np.clip(1 - r / 2200, 0, 1)
    out[..., :3] += np.asarray(K.C['FLAME'], np.float32) * 0.10 * rays[..., None]
    return _ro(out)


@functools.lru_cache(maxsize=1)
def _chip():
    w, h = 330, 72
    a = K.rrect_alpha(w, h, 18)
    a = a if a.shape[:2] == (h, w) else cv2.resize(a, (w, h))
    s = np.zeros((h, w, 4), np.float32)
    inner = cv2.erode(a, np.ones((5, 5), np.uint8))
    s[..., :3] = np.asarray(K.C['SMOKE'], np.float32) * 0.9 * inner[..., None]
    s[..., :3] += np.asarray(K.C['FLAME'], np.float32) * 1.4 * np.clip(a - inner, 0, 1)[..., None]
    s[..., 3] = a
    return _ro(s)


@functools.lru_cache(maxsize=2)
def _title(which):
    J = jawad_kit.J
    if which == 'hook':
        return J.HouseTitle('AAP NE ISE', '0.03 sec', caps_px=86, key_px=210)
    return J.HouseTitle('EK FRAME KI', 'keemat', caps_px=86, key_px=210)


def world_back(tl):
    """Stand-in layers 01-03 at layer time tl (opaque canvas)."""
    cv = K.background('ember', tl, bokeh=0.0)
    h = _haze()
    cv[...] = h + cv * (1 - h[..., 3:4])
    jawad_kit._draw_bokeh(cv, 'ember', tl, None, 1.8, 3, 1.0)
    return cv


def world_front(cv, t, tl):
    """Stand-in layers 07-11 + the chip."""
    J = jawad_kit.J
    J.embers(150, seed=7).draw(cv, K.Cam(aperture=24), tl)
    T = jawad_kit.T
    if t < T_PLAY:
        ht = _title('hook')
        ht.draw(cv, 10.0, 540, 640, t0=0.0)
        T.render('DEKHA', 'jw_caps', px=86).draw(cv, 540, 884.5)
        if t < 32 / FPS:
            K.draw(cv, _chip(), 760, 1282, opacity=1.0 - K.ramp(t, 24 / FPS, 32 / FPS, 'in_cubic'))
    else:
        _title('pay').draw(cv, t, 540, 640, t0=T_PLAY, out_t0=29.1)


def frame(t, layers=True):
    """Stand-in assembled frame at reel time t (playing / paused states), finished with the real look.
    layers: True = JD's layers 04-06 | False = the world without JD | 'base' = layer 04 only, no wrap (matte QA)."""
    import jawad_grade as G
    tl = layer_clock(t)
    cv = world_back(tl)
    if layers == 'base':
        draw_layer(cv, 4, tl, wrap=False)
    elif layers:
        draw_all(cv, tl)
    world_front(cv, t, tl)
    if t >= 29.4:
        cv[..., :3] *= 1.0 - 0.42 * K.ramp(t, 29.4, 29.8, 'out_cubic')        # end-card dim x0.58 (stand-in)
    return G.tx_finish(np.ascontiguousarray(cv), t, LOOK, cuts=CUTS)


def exploded(t, panes=None):
    """Stand-in exploded stack: pane 01 (opaque world) + JD's panes 04-06 as planes with the BRIEF 7.3 cameras."""
    import jawad_grade as G
    cam, gap = _stack_cam(t)
    if panes is None:
        bg = world_back(T_PAUSE)
        panes = {1: _ro(bg), 4: pane(4, bg), 5: pane(5), 6: pane(6)}
    cv = np.zeros((K.H, K.W, 4), np.float32)
    cv[..., :3] = np.asarray(K.C['NIGHT_0'], np.float32)
    cv[..., 3] = 1
    for i in (1, 4, 5, 6):
        z = (6.5 - i) * gap
        K.draw_plane(cv, panes[i], cam, (0.0, 0.0, z), 1080.0, dof=cam.aperture > 0)
    return G.tx_finish(cv, t, LOOK, cuts=CUTS), cam, gap


def _stack_cam(t):
    """BRIEF 7.3 cameras at the test frames (key poses only)."""
    F85, F100 = 4533.0, 5333.0
    if abs(t - 5.1) < 1e-6:
        return K.Cam.orbit((0, -265.0, 0), 9400 * (1 - 0.01 * 0.3), yaw=52, pitch=8, focal=F85), 120.0
    if abs(t - 7.8) < 1e-6 or abs(t - 8.4) < 1e-6:
        k = 4 if t < 8 else 5
        gap = 300.0
        tgt = (440 - 540.0, 1300 - 960.0, (6.5 - k) * gap)
        return K.Cam.orbit(tgt, 4920.0, yaw=32, pitch=3, focal=F85, aperture=420.0), gap
    if abs(t - 13.2) < 1e-6:
        return K.Cam.orbit((0, -306.4, 0), 8600.0, focal=F100), 30.0
    if abs(t - 16.0) < 1e-6:
        D = 7982.9
        return K.Cam.orbit((0, -306.4, 0), D, focal=F100, aperture=900.0, focus_dist=D + 3.5 * 30), 30.0
    raise ValueError('no stand-in camera for t=%r' % t)


# ============================================================================================ checks
def _lv(img, b):
    x0, y0, x1, y1 = b
    g = cv2.cvtColor(np.ascontiguousarray(img, np.float32), cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
    return float(cv2.Laplacian(g, cv2.CV_32F).var())


TEX_PATCHES = {'cheek_meta': (416, 453, 480, 517), 'cheek_right': (560, 470, 620, 530), 'forehead': (420, 240, 560, 300)}


def _check():
    out = {}
    t0 = time.time()
    L = face_layers()
    out['build_s'] = round(time.time() - t0, 2)
    out['sprite_shape'] = L['shape']
    out['anchor'] = [round(v, 5) for v in L['anchor']]
    out['boxes_pause'] = {k: (np.round(np.asarray(v), 1).tolist()) for k, v in L['boxes'].items()}
    out['head_lead'] = [round(v, 4) for v in head_lead()]
    # idle over the playing ranges
    tls = np.concatenate([np.arange(0, 0.3, 1 / FPS), np.arange(-7.2, 0.0, 1 / FPS)])
    m = meta()
    eye = np.array([point(tl, m['eye_mid']) for tl in tls])
    rots = np.array([idle(tl)[2] for tl in tls])
    brs = np.array([idle(tl)[3] for tl in tls])
    seg = tls[1:] - tls[:-1]
    ok = np.abs(seg - 1 / FPS) < 1e-6
    v = np.linalg.norm(np.diff(eye, axis=0), axis=1)[ok]
    # bust bottom corners (the original cut row) at every playing frame: lift above the frame bottom?
    lifts = []
    for tl in tls:
        for u in (0.0, 764.0):
            lifts.append(torso_point(tl, (u, 1112.0))[1])
    lifts = np.array(lifts)
    out['idle'] = dict(eye_dev_px=round(float(np.linalg.norm(eye - np.asarray(eye_screen(T_PAUSE)), axis=1).max()), 2),
                       eye_speed_peak_px_frame=round(float(v.max()), 3),
                       eye_speed_peak_pct_w_s=round(float(v.max()) * FPS / K.W * 100, 3),
                       roll_deg=(round(float(rots.min()), 3), round(float(rots.max()), 3)),
                       breath_pct=(round(float(brs.min()) * 100, 3), round(float(brs.max()) * 100, 3)),
                       bust_cut_row_min_y=round(float(lifts.min()), 2),
                       extend_rows_below_cut_px=EXTEND * SCALE)
    # the cut at 26.4 (f791 paused -> f792 playing) and the loop seam (f1007 -> f0)
    e791 = np.asarray(eye_screen(T_PAUSE))
    e792 = np.asarray(eye_screen(layer_clock(792 / FPS)))
    out['eye_jump_f791_f792_px'] = round(float(np.linalg.norm(e792 - e791)), 2)
    out['eye_step_f1007_f0_px'] = round(float(np.linalg.norm(np.asarray(eye_screen(layer_clock(1007 / FPS)))
                                                            - np.asarray(eye_screen(0.0)))), 3)
    out['face_rect_pause'] = [round(x, 1) for x in face_rect()]
    out['jd_rect_pause'] = jd_rect()
    out['scale_of_2x'] = SCALE
    # texture (cheek / forehead Laplacian variance of what is used vs Lanczos 2x of the native crop)
    sr = cv2.imread(os.path.join(CROPS, POSE + '_2x.png')).astype(np.float32)
    nat = cv2.imread(os.path.join(CROPS, POSE + '.png'))
    lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    used = rgb_used()
    out['texture'] = {k: dict(sr_vs_lanczos=round(_lv(sr, b) / _lv(lz, b), 2), used_vs_lanczos=round(_lv(used, b) /
                                                                                                  _lv(lz, b), 2))
                      for k, b in TEX_PATCHES.items()}
    # cost
    cv = np.zeros((K.H, K.W, 4), np.float32)
    cv[..., 3] = 1
    prewarm()
    t1 = time.time()
    for i in range(6):
        draw_all(cv, -1.0 - i * 0.37)
    out['ms_draw_all'] = round((time.time() - t1) / 6 * 1000, 1)
    return out


def _measure(img8, alpha, world8, base8):
    """Black / exposure / fringe numbers on a finished frame (uint8 RGB), JD's screen matte, the same frame without JD
    and the frame with layer 04 alone (no rim, halo or wrap: the matte's own fringe)."""
    def luma(x):
        x = x.astype(np.float32)
        return 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
    Y, Yw = luma(img8), luma(world8)
    a = alpha
    solid = cv2.erode((a > 0.98).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    vis = np.zeros_like(solid)
    vis[:, 60:] = True                                              # left 60 px: the fade_open ramp
    ring = (cv2.dilate((a > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & (a <= 0.02))
    ring[:, :60] = False
    ring[1900:] = False
    near = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((301, 301), np.uint8)).astype(bool) & (a <= 0.02)
    Yb = luma(base8)
    res = dict(jd_p2_luma=round(float(np.percentile(Y[solid & vis], 2)), 2),
               jd_p50_luma=round(float(np.percentile(Y[solid & vis], 50)), 2),
               jd_p99_luma=round(float(np.percentile(Y[solid & vis], 99)), 2),
               world_near_p2_luma=round(float(np.percentile(Yw[near], 2)), 2),
               world_p99_luma=round(float(np.percentile(Yw, 99)), 2),
               world_max_luma=round(float(Yw.max()), 2),
               fringe_ring3_base_only=round(float((Yb[ring] - Yw[ring]).mean()), 2),
               fringe_ring3_base_only_p95=round(float(np.percentile(Yb[ring] - Yw[ring], 95)), 2),
               ring3_full_look=round(float((Y[ring] - Yw[ring]).mean()), 2))
    return res


def _to8(img):
    import jawad_grade as G
    return np.clip(np.round(G.display(img[..., :3]) * 255), 0, 255).astype(np.uint8)


def stills(out_dir=None):
    """Test stills of every face beat (stand-in world, real look A layers, real finish). Writes PNGs + stills.json."""
    import jawad_grade as G
    out_dir = out_dir or os.path.join(RW, 'faces_test')
    os.makedirs(out_dir, exist_ok=True)
    prewarm()
    res = {}
    beats = [(0, 'f0 hook, playing'), (9, 'f9 pause click'), (26, 'f26 chip fading'), (792, 'f792 payoff cut (B side)'),
             (803, 'f803 VO keemat'), (846, 'f846 hidden-JD glint'), (873, 'f873 lockup exits'),
             (938, 'f938 end card settled (dim x0.58)'), (1007, 'f1007 loop end')]
    for f, note in beats:
        t = f / FPS
        img = frame(t)
        tl = layer_clock(t)
        # same frame without JD for the halo / black numbers (the finish is deterministic per t)
        a = jd_alpha(tl)
        d8, r8, b8 = (_to8(x) for x in (img, frame(t, layers=False), frame(t, layers='base')))
        nm = 'f%04d' % f
        cv2.imwrite(os.path.join(out_dir, nm + '.png'), d8[..., ::-1])
        if f == 0:
            os.makedirs(os.path.join(RW, 'qa'), exist_ok=True)
            cv2.imwrite(os.path.join(RW, 'qa', 'faces_check.png'), d8[..., ::-1])
        cv2.imwrite(os.path.join(out_dir, nm + '_phone.png'), cv2.resize(d8[..., ::-1], (360, 640),
                                                                           interpolation=cv2.INTER_AREA))
        x0, y0, x1, y1 = [int(v) for v in jd_rect(tl, 40)]
        cv2.imwrite(os.path.join(out_dir, nm + '_jd100.png'), d8[y0:y1, x0:x1, ::-1])
        r = _measure(d8, a, r8, b8)
        r.update(note=note, tl=round(tl, 4), eye=[round(v, 1) for v in eye_screen(tl)])
        res[nm] = r
        print(nm, json.dumps(r), flush=True)
    # exploded key poses (stand-in stack: panes 01, 04, 05, 06)
    bg = world_back(T_PAUSE)
    panes = {1: _ro(bg), 4: pane(4, bg), 5: pane(5), 6: pane(6)}
    for t, note in ((5.1, 'f153 cover, side-on yaw 52'), (7.8, 'f234 fly: pane 04 in focus'),
                    (8.4, 'f252 fly: pane 05 (rim alone) in focus'), (13.2, 'f396 frontal, gap 30'),
                    (16.0, 'f480 pushed + racked to pane 03')):
        img, cam, gap = exploded(t, panes)
        d8 = _to8(img)
        nm = 'f%04d' % int(round(t * FPS))
        cv2.imwrite(os.path.join(out_dir, nm + '_stack.png'), d8[..., ::-1])
        cv2.imwrite(os.path.join(out_dir, nm + '_stack_phone.png'), cv2.resize(d8[..., ::-1], (360, 640),
                                                                                 interpolation=cv2.INTER_AREA))
        res[nm + '_stack'] = dict(note=note, gap=gap)
        print(nm, note, flush=True)
    # panes alone over black (for the rim / halo / shadow read)
    for i in (4, 5, 6):
        p = panes[i]
        rgb = p[..., :3] + np.asarray(K.C['NIGHT_0'], np.float32) * (1 - p[..., 3:4])
        d8 = np.clip(np.round(K.to_srgb(np.clip(rgb, 0, 1)) * 255), 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(out_dir, 'pane%02d.png' % i), d8[900:1920, 0:760, ::-1])
    with open(os.path.join(out_dir, 'stills.json'), 'w') as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'check':
        print(json.dumps(_check(), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
    elif cmd == 'stills':
        stills(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(__doc__)
