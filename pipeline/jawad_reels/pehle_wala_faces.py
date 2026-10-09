"""pehle_wala_faces.py - JD's reaction-cam tile for reel 1, C26 "Pehle Wala Hi Theek Tha" (face-compositor).

Owner: face-compositor. pehle_wala.py imports this file and never edits it; this file never edits the shared toolkit.
Plan: BRIEF.md section 14 (two showings of a docked webcam tile, streetwear only, no swap inside a showing, no mirror).
Write-up with every measured number: brand_reels/design/reels/pehle_wala/FACES.md.

    import jawad_kit                                  # FIRST (pehle_wala.py does this anyway)
    import pehle_wala_faces as PF
    PF.prewarm()                                      # builds both poses' layers once per worker (~3 s)
    PF.draw_tile(cv, t)                               # in draw(t), after the world / pins / chips, BEFORE captions;
                                                      # draws nothing outside the two showings (pure f(t), in place)
    PF.avoid_rect(t)   -> (70, 952, 430, 1284) while the tile shows, else None   (snake_captions avoid=)
    PF.tile_rect(t)    -> drawn tile + label box this frame (POP / exit applied), else None
    PF.face_rect(t)    -> screen face box (YuNet box of the pose, idle applied), else None  (copy >= 60 px from it)
    PF.eye_screen(t)   -> screen (x, y) of the eye midpoint, else None
    PF.jd_alpha(t)     -> (1920, 1080) alpha of JD's cut-out (QA masks, e.g. the colorist's skin check), else None
    PF.tile_alpha(t)   -> (1920, 1080) alpha of the feed's rounded rect, else None
    PF.draw_tile(cv, t, mode='plate' | 'matte')      -> QA variants (room only / plain cut-out, no look)
    PF.FACES           -> the shot table (BRIEF section 14 keys + t0, t1, pose, P, width, cam_keys, rim_dir, rim_gain,
                          swap_on_beat, note); look='A' (rim, both showings) or 'D' (cine) per shot
    python3 pehle_wala_faces.py check                -> limits, placement, texture, halo, eye lock, cost (JSON)
    python3 pehle_wala_faces.py boards               -> matte over black / FLAME / white at 200 % (display scale)
                                                        in <WS>/pehle_wala/qa/faces/
    Proof on a stand-in world (until pehle_wala.py exists): pehle_wala_faces_proof.py (render.py contract).

What is in the tile (back to front, all at display scale, built once per pose):
    L0 webcam room plate: NIGHT_1 -> NIGHT_0 wall + K.radial(480, FLAME x0.35) at the tile's top-right (the ad /
       monitor light that motivates the rim), JD's soft wall shadow cast down-left of him (the light is up-right)
    L1 torso + shoulders: breathes 0.4 % at 0.29 Hz about the bust bottom; depth-driven micro-parallax from the
       Depth-Anything-V2-Small map (a 1.2 px body micro-turn on shoulders / chest / hair edges, head box rigid)
    L2 head + hair: ONE rigid layer riding the breathing neck (no warp, no depth displacement on the face)
    light wrap of the blurred wall over JD's outer 6 px at 22 %, then the glass card (rim, glow, shadow) around the
    feed and the "JD . editor" tab. Look A rim (FLAME back-rim from screen-right = the ad side, faint RED counter-rim).
Never-uncanny: no blink, no lip motion, no eye re-target, no morph, no cross-dissolve, no swap inside a showing; the
webcam never moves (camera law); display scale 0.40 of the 2x master; skin texture pulled back to within 1.5x of the
source (TEX_K); grain only from G.finish.

Conventions: sprites are premultiplied LINEAR float32 (core.py); screen px, y down.
Assets: workspace/brand_reels/charsheet/cutouts/<pose>.png (Real-ESRGAN x4plus 2x masters, BiRefNet-portrait matte,
decontaminated), <pose>_depth.png (Depth-Anything-V2-Small, Apache-2.0), <pose>.json (eyes, face / head boxes);
crops/<pose>.png + crops/<pose>_2x.png for the texture pull-back.
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
from jawad_kit import K, T, ui                    # noqa: E402
import jawad_grade as G                           # noqa: E402  registers the 'inferno' look (ui glass, post)

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

CS = '/home/user/100/workspace/brand_reels/charsheet'
CUT = os.path.join(CS, 'cutouts')
CROPS = os.path.join(CS, 'crops')

# faces.py (the charsheet helper library) imported BY PATH under a private name, so its folder never lands on sys.path
_spec = importlib.util.spec_from_file_location('pw_charsheet_faces', os.path.join(CS, 'tools', 'faces.py'))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)

FPS = 30
LOOK = 'inferno'

# ============================================================================================ geometry (BRIEF 5.1, 14)
TILE = (70, 980, 430, 1280)                 # x0 y0 x1 y1 of the glass card body
TILE_W, TILE_H, TILE_R = 360, 300, 26
TAB = (82, 952, 352, 1000)                  # label tab body
TAB_TEXT = 'JD · editor'               # jw_mono 34 px (measured 231 px)
EYE_TILE = (190.0, 160.0)                   # eye midpoint in tile px (both poses: eyes locked across the showings)
SCALE = 0.40                                # display scale of the 2x master (<= 1.0)
CAPTION_GAP = 28                            # snake_captions keeps ink this far below an avoid rect
FACE_COPY_GAP = 60                          # no copy within 60 px of the face box

# ============================================================================================ look (A rim) and texture
# Real-ESRGAN x4plus over-sharpens one cheek and waxes the other on these two headshots. Measured at the DISPLAY scale
# (0.4 of the 2x master = 0.8 of the native crop), cheek / forehead Laplacian variance vs the Lanczos 2x of the native
# crop: smirk L 2.12x, R 0.77x, forehead 0.95x; sunglasses L 1.97x, R 1.87x, forehead 0.95x. Pull the SR detail
# back toward the source in the opaque interior (rgb = lanczos2x + k (sr - lanczos2x)): k = 0.3 puts every patch in
# 0.87-1.21x (k = 0.5: 0.81-1.42x) and keeps a little of the SR crispness on eyes, brows, beard and chains. Looked at
# 3x side by side (k 0 / 0.5 / 1): k = 1 waxes the smirk's right cheek and wipes the forehead's pores and spots.
TEX_K = {'street_smirk': 0.3, 'street_sunglasses': 0.3}
# look A (BRIEF 14, hero): warm-dark base (faces.warm_dark), low key so the baked frontal studio light never
# out-shines the ad. Warmth / saturation set so that AFTER the inferno finish the skin keeps the source's OKLab chroma
# (lit cheek / forehead 0.069-0.071 vs 0.071-0.074) and hue (+-4 deg), only darker (L 0.73 -> 0.53): never lightened,
# never orange (faces.warm_dark's default warmth (1, .80, .66) and (1, .86, .74) both pushed the chroma up).
BASE = dict(exposure=0.42, warmth=(1.0, 0.92, 0.84), contrast=1.12, sat=0.85)
# rim from screen-right / up (the ad and its ember glow are right of the tile). Emission inside the silhouette, peak
# ~2.4x linear FLAME (<= 3x); counter-rim and all-round outline kept low (a full glowing outline reads as a sticker at
# 360 px); the outer halo is mostly left to the finish's bloom (keeps the 3 px ring within +6 code values).
RIM = dict(light=(0.8, -0.5), gain=2.4, back=0.08, outline=0.02, depth_wrap=0.3, halo_strength=0.0)
# look D (cine, narration; not used by the BRIEF's two showings, available per shot with look='D'): faces.cine_grade
# base, softer rim (face_assets.md section 3), same light direction and the same geometry as A.
BASE_D = dict(exposure=0.72)
RIM_D = dict(light=(0.8, -0.5), gain=1.4, back=0.06, outline=0.02, depth_wrap=0.3, halo_strength=0.0)

# black-point toe on the subject (linear luminance, hue kept): f(Y) = max(0, Y - b (1 - smoothstep(Y / 4b))), identity
# above 4b. Before the finish his p2 already equals the wall's (0.0011 vs 0.0012 linear); the inferno bloom (threshold
# 0.38, radii 8-170 px) of his own skin / rim and of the ad then veils his hair / beard blacks (p2 4.7 vs 2.1 for the
# wall at the same pixels). The toe pre-compensates (everything it touches is below the finish's crush anyway, so no
# visible shadow detail is lost); the remaining veil is the lens bloom every element in that spot gets (FACES.md).
BLACK_TOE = 0.004
PLATE_GLOW = 0.35                           # K.radial(480, FLAME x0.35) at the tile's top-right (BRIEF 14)
SHADOW = dict(dx=-12.0, dy=7.0, sigma=13.0, k=0.30)     # wall shadow (tile px): light is up-right -> falls down-left
WRAP = dict(width=6.0, sigma=10.0, amount=0.22)         # light wrap (tile px; 6 px = 15 px of the 2x master)
VIGNETTE = 0.20                             # webcam corner fall-off on the feed (multiplicative, never lifts black)
BREATH = 0.004                              # torso breathing (scale y about the bust bottom), 0.29 Hz
BREATH_HZ = 1.0 / 3.4
BOB = 1.1                                   # px, slow drift of the sitting body (0.21 / 0.17 Hz)
SWAY = 0.30                                 # deg, about the bust bottom (0.23 Hz)
PARALLAX_PX = 1.2                           # max depth-driven shift of torso / hair edges vs the rigid head (tile px)

# ============================================================================================ timing (BRIEF 7, 14)
ENTER_F = 6                                 # POP: scale 0.92 -> 1 (POP spring), opacity inout_sine over 6 f
POP_S0 = 0.92
EXIT_F = 10                                 # exit: 10 f in_cubic, y + 24, opacity -> 0, gone half a frame before t1
                                            # (motion-blur samples of the next frame never catch a ghost of the tile)
EXIT_DY = 24.0

FACES = [
    dict(t0=448 / FPS, t1=512 / FPS, f0=448, f1=511, shot='S4-01', pose='street_sunglasses', look='A',
         tile=TILE, scale=SCALE, eye_mid_tile=EYE_TILE, rim_dir=RIM['light'], rim_gain=1.0,
         enter=('POP', ENTER_F), exit=('in_cubic', EXIT_F, 'y+24'), seed=16,
         P=dict(eye_mid_screen=(TILE[0] + EYE_TILE[0], TILE[1] + EYE_TILE[1]), layer='2D tile over the player'),
         width='bust 360 px of the 2x master at 0.40 (face box 110 x 160 px)',
         cam_keys=dict(camera='locked webcam (camera law: the camera never moves)', push=None),
         swap_on_beat=False,
         note='v16 "Thora cinematic": JD in sunglasses watches the flares overload (rim x1.0: x1.12 put the 3 px ring at +6.3 after the finish)'),
    dict(t0=836 / FPS, t1=896 / FPS, f0=836, f1=895, shot='S6-01', pose='street_smirk', look='A',
         tile=TILE, scale=SCALE, eye_mid_tile=EYE_TILE, rim_dir=RIM['light'], rim_gain=1.0,
         enter=('POP', ENTER_F), exit=('in_cubic', EXIT_F, 'y+24'), seed=23,
         P=dict(eye_mid_screen=(TILE[0] + EYE_TILE[0], TILE[1] + EYE_TILE[1]), layer='2D tile over the player'),
         width='bust 366 px of the 2x master at 0.40 (face box 127 x 167 px)',
         cam_keys=dict(camera='locked webcam (camera law: the camera never moves)', push=None),
         swap_on_beat=False,
         note='v1 restored: hero smirk, cover frame 855 (tile settled from ~f846)'),
]
for _sh in FACES:
    _sh['note_swap'] = ('the two showings are 12.9 s apart (separate POP entrances, not a cut between faces); both '
                        'put the eye midpoint on the same tile point, so the second face lands where the first was')


def shot_at(t):
    for sh in FACES:
        if sh['t0'] <= t < sh['t1']:
            return sh
    return None


def visible(t):
    return shot_at(t) is not None


def envelope(t, sh=None):
    """(opacity, scale, dy) of the whole tile (card + feed + tab) at time t, or None outside the showings."""
    sh = sh or shot_at(t)
    if sh is None:
        return None
    u = t - sh['t0']
    op = K.EASE['inout_sine'](K.clamp(u / (ENTER_F / FPS)))
    s = POP_S0 + (1.0 - POP_S0) * K.spring(u, 2.6, 0.50)             # jawad_tx SPRINGS['POP'] = (2.6, 0.50)
    te = sh['t1'] - EXIT_F / FPS
    e = K.EASE['in_cubic'](K.clamp((t - te) / ((EXIT_F - 0.5) / FPS)))
    return op * (1.0 - e), s, EXIT_DY * e


# ============================================================================================ assets
def _ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.setflags(write=False)
    return a


def meta(pose):
    return FA.meta(pose)


@functools.lru_cache(maxsize=2)
def rgba16(pose):
    """Straight-alpha sRGB RGBA uint16 (RGB order) of the cut-out with the texture pull-back of TEX_K applied in the
    opaque interior (the decontaminated matte edge is kept exactly as cut). 16 bit: 8-bit rounding noise alone is as
    large as the source's cheek texture."""
    cut = cv2.imread(os.path.join(CUT, pose + '.png'), cv2.IMREAD_UNCHANGED)          # BGRA uint8
    k = TEX_K.get(pose, 1.0)
    rgb = cut[..., :3].astype(np.float32)
    if k < 1.0:
        sr = cv2.imread(os.path.join(CROPS, pose + '_2x.png')).astype(np.float32)
        nat = cv2.imread(os.path.join(CROPS, pose + '.png'))
        lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        a = cut[..., 3].astype(np.float32) / 255.0
        core = cv2.erode((a > 0.99).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        w = cv2.GaussianBlur(core.astype(np.float32), (0, 0), 2.0)[..., None]
        rgb = rgb + (k - 1.0) * (sr - lz) * w
    out = np.empty(cut.shape, np.uint16)
    out[..., :3] = np.clip(np.round(rgb[..., ::-1] * 257.0), 0, 65535).astype(np.uint16)
    out[..., 3] = cut[..., 3].astype(np.uint16) * 257
    out.setflags(write=False)
    return out


@functools.lru_cache(maxsize=2)
def plain(pose):
    """Premultiplied linear 2x master (texture-corrected). Read-only."""
    return _ro(K.sprite(rgba16(pose)))


def toe(spr, b):
    """Black-point toe on a premultiplied linear sprite (luminance-based, hue kept, monotone, identity above 4b)."""
    if b <= 0:
        return spr
    a = spr[..., 3:4]
    c = np.where(a > 1e-4, spr[..., :3] / np.maximum(a, 1e-4), 0.0)
    Y = np.maximum(K.lum(c), 1e-7)
    x = np.clip(Y / (4.0 * b), 0, 1)
    Yn = np.maximum(0.0, Y - b * (1.0 - x * x * (3 - 2 * x)))
    out = spr.copy()
    out[..., :3] = c * (Yn / Y)[..., None] * a
    return out.astype(np.float32)


@functools.lru_cache(maxsize=4)
def layers(pose, look='A'):
    """Look A + split + display-scale layers for one pose, built once (read-only arrays):
    base (warm-dark subject) and em (rim emission: back-rim, counter-rim, outline, depth wrap, halo) so a shot can
    scale the rim alone; mk / wt = rigid-head mask and torso weight (head over torso == the whole look exactly);
    matte (plain cut-out, no look: QA); field = depth shift field for the torso parallax (head box rigid, |f| <= 1);
    anchors in display px (eye midpoint, bust bottom, neck, face box, subject bbox)."""
    p = plain(pose)
    m = meta(pose)
    dep = FA.depth(pose)
    if look == 'D':
        base = toe(FA.cine_grade(p, **BASE_D), BLACK_TOE)
        hero = FA.rim_light(p, dep, base=base, **RIM_D)
    else:
        base = toe(FA.warm_dark(p, **BASE), BLACK_TOE)
        hero = FA.rim_light(p, dep, base=base, **RIM)
    dx0, dy0 = FA.offset(p, hero)
    basep = np.zeros(hero.shape, np.float32)
    basep[dy0:dy0 + p.shape[0], dx0:dx0 + p.shape[1]] = base
    matte = np.zeros(hero.shape, np.float32)
    matte[dy0:dy0 + p.shape[0], dx0:dx0 + p.shape[1]] = p
    hero, basep = FA.fade_open(hero), FA.fade_open(basep)            # panel-cut sides fade (all outside the tile)
    em = hero - basep
    em[..., 3] = 0.0
    H, W = hero.shape[:2]
    dfull = cv2.copyMakeBorder(np.ascontiguousarray(dep, np.float32), dy0, H - dy0 - p.shape[0], dx0,
                               W - dx0 - p.shape[1], cv2.BORDER_REPLICATE)
    # pad top / left so the display size is exactly SCALE x the master (no anisotropic rounding)
    q = int(round(2.0 / SCALE))                                       # 5 for 0.4
    pt, pl = (-H) % q, (-W) % q
    dx0, dy0 = dx0 + pl, dy0 + pt
    Wd, Hd = int(round((W + pl) * SCALE)), int(round((H + pt) * SCALE))

    def down(img):
        if img.ndim == 3:
            img = cv2.copyMakeBorder(img, pt, 0, pl, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        else:
            img = cv2.copyMakeBorder(img, pt, 0, pl, 0, cv2.BORDER_REPLICATE)
        out = cv2.resize(np.ascontiguousarray(img, np.float32), (Wd, Hd), interpolation=cv2.INTER_AREA)
        if out.ndim == 3:
            out[..., 3] = np.clip(out[..., 3], 0, 1)
        return out
    baseD, emD, matteD, depD = down(basep), down(em), down(matte), down(dfull)
    emD[..., 3] = 0.0
    hb = [v * SCALE for v in (m['head_box'][0] + dx0, m['head_box'][1] + dy0, m['head_box'][2] + dx0,
                              m['head_box'][3] + dy0)]
    # rigid head: depth flattened to its median inside the head box (feathered) and blurred (sigma 6 px at 1080
    # width = 2.4 px here); torso shift field = depth - head median, so the head box does not move (rigid reference)
    depR = FA.rigid_depth(depD, hb, feather=max(6, int((hb[2] - hb[0]) / 6)))
    depR = cv2.GaussianBlur(depR, (0, 0), 2.4)
    x0, y0, x1, y1 = [int(round(v)) for v in hb]
    piv = float(np.median(depR[max(0, y0):y1, max(0, x0):x1]))
    field = depR - piv
    body = matteD[..., 3] > 0.5
    fmax = float(np.abs(field[body]).max()) if body.any() else 1.0
    field = field / max(fmax, 1e-6)
    # head / torso split (exact recombination at zero offset)
    fe = 0.08 * (hb[2] - hb[0])
    mk = np.zeros((Hd, Wd), np.float32)
    mk[int(max(0, hb[1] - 2 * fe)):int(hb[3]), int(max(0, hb[0] - fe)):int(min(Wd, hb[2] + fe))] = 1
    mk = np.clip(cv2.GaussianBlur(mk, (0, 0), fe / 2) * 2.0, 0, 1)
    al = baseD[..., 3]
    den = 1.0 - mk * al
    wt = np.where(den > 1e-4, (1.0 - mk) / np.maximum(den, 1e-4), 0.0).astype(np.float32)
    eye = ((m['eye_mid'][0] + dx0) * SCALE, (m['eye_mid'][1] + dy0) * SCALE)
    bust = (eye[0], (p.shape[0] + dy0) * SCALE)
    neck = (eye[0], hb[3])
    fb = m['face_box']
    face = ((fb[0] + dx0) * SCALE, (fb[1] + dy0) * SCALE, (fb[2] + dx0) * SCALE, (fb[3] + dy0) * SCALE)
    sb = m['subject_bbox']
    subj = ((sb[0] + dx0) * SCALE, (sb[1] + dy0) * SCALE, (sb[2] + dx0) * SCALE, (sb[3] + dy0) * SCALE)
    yy, xx = np.mgrid[0:Hd, 0:Wd].astype(np.float32)
    return dict(base=_ro(baseD), em=_ro(emD), mk=_ro(mk), wt=_ro(wt), matte=_ro(matteD), field=_ro(field),
                xx=_ro(xx), yy=_ro(yy), eye=eye, bust=bust, neck=neck, face=face, subj=subj, size=(Wd, Hd),
                head_box=tuple(hb))


@functools.lru_cache(maxsize=4)
def _lit(pose, look, rim_gain):
    """(head, torso) display layers of the look with the shot's rim gain on the emission only (1.0 = as built)."""
    L = layers(pose, look)
    hero = L['base'] + L['em'] * np.float32(rim_gain)
    return _ro(hero * L['mk'][..., None]), _ro(hero * L['wt'][..., None])


@functools.lru_cache(maxsize=1)
def plate():
    """L0: the webcam room behind JD (tile px, opaque): warm near-black wall, the ad / monitor glow top-right."""
    h, w = TILE_H, TILE_W
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    top, bot = np.float32(K.C['NIGHT_1']), np.float32(K.C['NIGHT_0'])
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = top * (1 - yy) + bot * yy
    out[..., 3] = 1.0
    K.draw(out, K.radial(480, np.float32(K.C['FLAME']) * PLATE_GLOW), w, 0, mode='add')
    out[..., 3] = 1.0
    return _ro(out)


@functools.lru_cache(maxsize=1)
def _plate_blur():
    return _ro(cv2.GaussianBlur(np.ascontiguousarray(plate()[..., :3]), (0, 0), WRAP['sigma']))


@functools.lru_cache(maxsize=1)
def _vignette():
    d = K.rrect_sdf(TILE_W, TILE_H, TILE_R)                            # negative inside
    return _ro(1.0 - VIGNETTE * np.exp(d / 40.0))


@functools.lru_cache(maxsize=1)
def _feed_mask():
    return _ro(K.rrect_alpha(TILE_W, TILE_H, TILE_R, 0))


@functools.lru_cache(maxsize=1)
def card():
    return ui.glass_card(TILE_W, TILE_H, r=TILE_R, look=LOOK, shadow=0.6)


@functools.lru_cache(maxsize=1)
def tab():
    """Label tab: glass 270 x 48 r 16 + "JD . editor" (jw_mono 34, IVORY), centred. Returns (panel, face)."""
    w, h = TAB[2] - TAB[0], TAB[3] - TAB[1]
    pn = ui.glass_card(w, h, r=16, look=LOOK, shadow=0.4)
    f = pn.face_at()
    T.render(TAB_TEXT, 'jw_mono', px=34).draw(f, pn.pad + w / 2.0, pn.pad + h / 2.0)
    return pn, _ro(f)


# ============================================================================================ motion
def idle(t, sh):
    """(dx, dy, rot_deg, breath) of a person sitting still at a webcam, per showing (u = t - t0): a slow drift of
    +-1.1 / 0.6 px, a +-0.3 deg sway about the bust bottom, breathing 0.4 % at 0.29 Hz (torso scale y about the bust
    bottom; the head rides the neck unscaled). Sines at unrelated rates, phases from the shot's seed. Pure f(t)."""
    u = t - sh['t0']
    s = float(sh.get('seed', 16))
    br = BREATH * math.sin(2 * math.pi * BREATH_HZ * u + 0.4 + s)
    return (BOB * math.sin(2 * math.pi * 0.21 * u + 0.9 + s), 0.55 * BOB * math.sin(2 * math.pi * 0.17 * u + 2.1 + s),
            SWAY * math.sin(2 * math.pi * 0.23 * u + 0.5 + s), br)


def turn(t, sh):
    """-1..1 body micro-turn that drives the depth parallax of the torso layer (0.19 Hz, phase from the seed)."""
    return math.sin(2 * math.pi * 0.19 * (t - sh['t0']) + 1.3 + float(sh.get('seed', 16)))


def _xf(t, sh):
    """Feed-px mapping of the HEAD layer: X = B + R (U - Ub) (+ lift). Returns (B, R, rot, br, lift)."""
    L = layers(sh['pose'], sh.get('look', 'A'))
    dx, dy, rot, br = idle(t, sh)
    ex, ey = L['eye']
    bx, by = L['bust']
    B = np.array([EYE_TILE[0] + (bx - ex) + dx, EYE_TILE[1] + (by - ey) + dy])
    r = math.radians(rot)
    R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    lift = R @ np.array([0.0, -br * (by - L['neck'][1])])
    return B, R, rot, br, lift


def feed_point(t, uv, sh=None):
    """Tile (feed) px of a display-layer px uv on the head layer (e.g. layers(pose)['eye'])."""
    sh = sh or shot_at(t)
    L = layers(sh['pose'], sh.get('look', 'A'))
    B, R, rot, br, lift = _xf(t, sh)
    return B + lift + R @ (np.asarray(uv, np.float64) - np.asarray(L['bust']))


# ============================================================================================ drawing
def _shift(img, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                          borderValue=0)


def _parallax(spr, L, k):
    """Torso layer with the depth-driven shift k * PARALLAX_PX * field (px, x only: a body micro-turn); head box rigid."""
    if abs(k) < 1e-4:
        return spr
    ox = L['field'] * np.float32(k * PARALLAX_PX)
    return cv2.remap(np.ascontiguousarray(spr), L['xx'] - ox, L['yy'], cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def feed(t, sh=None, mode='full'):
    """The webcam feed (TILE_H, TILE_W, 4) premultiplied linear at time t.
    mode 'full' | 'plate' (room only: halo / black reference) | 'matte' (plain cut-out over the plate, no look)."""
    sh = sh or shot_at(t)
    pl = plate()
    out = np.array(pl, np.float32)
    if mode == 'plate' or sh is None:
        out[..., :3] *= _vignette()[..., None]
        return out
    L = layers(sh['pose'], sh.get('look', 'A'))
    Wd, Hd = L['size']
    B, R, rot, br, lift = _xf(t, sh)
    anc = (L['bust'][0] / Wd, L['bust'][1] / Hd)
    lay = np.zeros((TILE_H, TILE_W, 4), np.float32)
    if mode == 'matte':
        K.draw(lay, L['matte'], B[0], B[1], rot=rot, anchor=anc)
    else:
        head, torso = _lit(sh['pose'], sh.get('look', 'A'), float(sh.get('rim_gain', 1.0)))
        torso = _parallax(torso, L, turn(t, sh))
        K.draw(lay, torso, B[0], B[1], scale=(1.0, 1.0 + br), rot=rot, anchor=anc)
        K.draw(lay, head, B[0] + lift[0], B[1] + lift[1], rot=rot, anchor=anc)
    a = np.clip(lay[..., 3], 0, 1)
    if mode == 'full':
        sh_a = cv2.GaussianBlur(_shift(a, SHADOW['dx'], SHADOW['dy']), (0, 0), SHADOW['sigma'])
        out[..., :3] *= (1.0 - SHADOW['k'] * sh_a)[..., None]
    out = lay + out * (1.0 - a[..., None])
    if mode == 'full' and WRAP['amount'] > 0:
        k = max(1, int(round(WRAP['width'])))
        inner = cv2.erode(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
        band = cv2.GaussianBlur(np.clip(a - inner, 0, 1), (0, 0), max(0.8, WRAP['width'] * 0.35)) * a
        rgb = out[..., :3]
        rgb += (WRAP['amount'] * band)[..., None] * np.clip(_plate_blur(), 0, 1) * (1.0 - np.clip(rgb, 0, 1))
    out[..., :3] *= _vignette()[..., None]
    out[..., 3] = 1.0
    return out


def tile_face(t, sh=None, mode='full'):
    """The glass card face with the feed inside (card-padded array), for Panel.draw."""
    cd = card()
    f = cd.face_at()
    fd = feed(t, sh, mode)
    m = _feed_mask()
    p = cd.pad
    reg = f[p:p + TILE_H, p:p + TILE_W]
    reg[...] = fd * m[..., None] + reg * (1.0 - m[..., None])
    if cd.rim_layer is not None:                                       # the glass edge stays on top of the video
        reg[..., :3] += cd.rim_layer[p:p + TILE_H, p:p + TILE_W, :3] * m[..., None]
    return f


def draw_tile(cv, t, mode='full', label=True):
    """Draw the reaction-cam tile (card shadow + glass + feed + label tab) into cv at time t; nothing outside the
    two showings. In place; returns the touched bbox or None. Pure function of t."""
    sh = shot_at(t)
    if sh is None:
        return None
    op, s, dy = envelope(t, sh)
    if op <= 1e-4:
        return None
    cx, cy = (TILE[0] + TILE[2]) / 2.0, (TILE[1] + TILE[3]) / 2.0 + dy
    cd = card()
    bb = cd.draw(cv, cx, cy, scale=s, opacity=op, face=tile_face(t, sh, mode), frost=0.0)
    if label:
        pn, f = tab()
        tx, ty = (TAB[0] + TAB[2]) / 2.0, (TAB[1] + TAB[3]) / 2.0
        pn.draw(cv, cx + s * (tx - cx), (TILE[1] + TILE[3]) / 2.0 + dy + s * (ty - (TILE[1] + TILE[3]) / 2.0),
                scale=s, opacity=op, face=f, frost=0.0)
    return bb


# ============================================================================================ layout exports
def _screen(t, sh, xy):
    """Screen px of a feed px under the tile's POP scale / exit offset."""
    op, s, dy = envelope(t, sh)
    cx, cy = (TILE[0] + TILE[2]) / 2.0, (TILE[1] + TILE[3]) / 2.0
    return (cx + s * (TILE[0] + xy[0] - cx), cy + dy + s * (TILE[1] + xy[1] - cy))


def eye_screen(t):
    sh = shot_at(t)
    if sh is None:
        return None
    return _screen(t, sh, feed_point(t, layers(sh['pose'], sh.get('look', 'A'))['eye'], sh))


def face_rect(t):
    """Screen face box (YuNet box of the pose through the head-layer mapping), or None."""
    sh = shot_at(t)
    if sh is None:
        return None
    x0, y0, x1, y1 = layers(sh['pose'], sh.get('look', 'A'))['face']
    pts = [_screen(t, sh, feed_point(t, (x, y), sh)) for x in (x0, x1) for y in (y0, y1)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def jd_alpha(t):
    """(1920, 1080) float32 screen alpha of JD's cut-out (geometry only: POP / exit applied, tile opacity NOT
    applied, clipped to the feed's rounded rect), or None outside the showings. For QA masks."""
    sh = shot_at(t)
    if sh is None:
        return None
    L = layers(sh['pose'], sh.get('look', 'A'))
    Wd, Hd = L['size']
    B, R, rot, br, lift = _xf(t, sh)
    lay = np.zeros((TILE_H, TILE_W, 4), np.float32)
    K.draw(lay, L['matte'], B[0], B[1], rot=rot, anchor=(L['bust'][0] / Wd, L['bust'][1] / Hd))
    a = np.clip(lay[..., 3], 0, 1) * _feed_mask()
    spr = np.dstack([a, a, a, a]).astype(np.float32)
    out = np.zeros((K.H, K.W, 4), np.float32)
    op, s, dy = envelope(t, sh)
    K.draw(out, spr, (TILE[0] + TILE[2]) / 2.0, (TILE[1] + TILE[3]) / 2.0 + dy, scale=s)
    return out[..., 3].copy()


def tile_alpha(t):
    """(1920, 1080) float32 screen alpha of the feed's rounded rect (geometry only), or None."""
    sh = shot_at(t)
    if sh is None:
        return None
    m = _feed_mask()
    spr = np.dstack([m, m, m, m]).astype(np.float32)
    out = np.zeros((K.H, K.W, 4), np.float32)
    op, s, dy = envelope(t, sh)
    K.draw(out, spr, (TILE[0] + TILE[2]) / 2.0, (TILE[1] + TILE[3]) / 2.0 + dy, scale=s)
    return out[..., 3].copy()


def tile_rect(t):
    """Drawn tile + label box this frame (POP scale / exit applied), or None."""
    sh = shot_at(t)
    if sh is None:
        return None
    a = _screen(t, sh, (TAB[0] - TILE[0], TAB[1] - TILE[1]))
    b = _screen(t, sh, (TILE_W, TILE_H))
    c = _screen(t, sh, (0, 0))
    return (min(a[0], c[0]), a[1], b[0], b[1])


# static caption avoid rect: tile + tab, bottom pushed so snake_captions' 28 px gap keeps ink >= 60 px below the
# lowest settled face box of either pose (idle included): sunglasses face bottom 1250.1 -> ink >= 1312 (61.9 px)
AVOID = (TILE[0], TAB[1], TILE[2], 1284)


def avoid_rect(t):
    """snake_captions avoid rect while the tile shows (static, so the caption layout does not jump), else None."""
    return AVOID if visible(t) else None


def prewarm():
    for sh in FACES:
        layers(sh['pose'], sh.get('look', 'A'))
        _lit(sh['pose'], sh.get('look', 'A'), float(sh.get('rim_gain', 1.0)))
    plate()
    _plate_blur()
    _vignette()
    _feed_mask()
    card()
    tab()


# ============================================================================================ checks
def _u8(lin):
    return K.to_srgb8(np.ascontiguousarray(lin, np.float32), 0.0, dither=False)


def _luma8(rgb8):
    return rgb8.astype(np.float32) @ np.float32([0.2126, 0.7152, 0.0722])


def _check():
    out = {}
    prewarm()
    # placement + eye lock + limits, sampled at 240 Hz over each showing
    for sh in FACES:
        ts = np.arange(sh['t0'], sh['t1'], 1.0 / 240)
        eyes = np.array([eye_screen(t) for t in ts])
        frs = np.array([face_rect(t) for t in ts])
        settled = [t for t in ts if envelope(t, sh)[1] > 0.999 and envelope(t, sh)[2] < 1e-6 and
                   t > sh['t0'] + 0.4]
        es = np.array([eye_screen(t) for t in settled])
        fs = np.array([face_rect(t) for t in settled])
        half = [t for t in ts if envelope(t, sh)[0] >= 0.5]
        fh = np.array([face_rect(t) for t in half])
        L = layers(sh['pose'], sh.get('look', 'A'))
        fr_frames = np.array([eye_screen(sh['t0'] + (i + 0.5) / FPS) for i in range(sh['f1'] - sh['f0'] + 1)])
        v_settled = np.linalg.norm(np.diff(es, axis=0), axis=1).max() * 240 / FPS
        par = PARALLAX_PX * float(np.abs(np.diff([turn(t, sh) for t in ts])).max()) * 240 / FPS
        idl = np.array([idle(t, sh) for t in ts])
        out[sh['pose']] = dict(
            frames=(sh['f0'], sh['f1']), seconds=round(sh['t1'] - sh['t0'], 3),
            eye_mid_settled=dict(mean=[round(v, 1) for v in es.mean(0)], min=[round(v, 1) for v in es.min(0)],
                                 max=[round(v, 1) for v in es.max(0)]),
            eye_speed_settled_px_frame=round(float(v_settled), 3),
            face_box_settled=[round(float(v), 1) for v in (fs[:, 0].min(), fs[:, 1].min(), fs[:, 2].max(),
                                                           fs[:, 3].max())],
            face_box_any_opacity_ge_half=[round(float(v), 1) for v in (fh[:, 0].min(), fh[:, 1].min(), fh[:, 2].max(),
                                                                       fh[:, 3].max())],
            face_box_px=(round(L['face'][2] - L['face'][0], 1), round(L['face'][3] - L['face'][1], 1)),
            hair_top_y=round(TILE[1] + EYE_TILE[1] - (L['eye'][1] - L['subj'][1]), 1),
            bust_bottom_y=round(TILE[1] + EYE_TILE[1] + (L['bust'][1] - L['eye'][1]), 1),
            subject_x=(round(TILE[0] + EYE_TILE[0] - (L['eye'][0] - L['subj'][0]), 1),
                       round(TILE[0] + EYE_TILE[0] + (L['subj'][2] - L['eye'][0]), 1)),
            idle_max=dict(dx=round(float(abs(idl[:, 0]).max()), 2), dy=round(float(abs(idl[:, 1]).max()), 2),
                          rot_deg=round(float(abs(idl[:, 2]).max()), 3), breath_pct=round(BREATH * 100, 2),
                          breath_hz=round(BREATH_HZ, 3)),
            parallax_torso_vs_head_px_frame_max=round(float(par), 4), parallax_px_max=PARALLAX_PX,
            scale_of_2x=SCALE, pop=dict(s0=POP_S0, frames=ENTER_F), exit=dict(frames=EXIT_F, dy=EXIT_DY),
            avoid=AVOID, caption_ink_min_y=AVOID[3] + CAPTION_GAP,
            face_to_caption_ink_px=dict(settled=round(AVOID[3] + CAPTION_GAP - float(fs[:, 3].max()), 1),
                                        exit_opacity_ge_half=round(AVOID[3] + CAPTION_GAP - float(fh[:, 3].max()), 1)),
            face_to_tab_px=round(float(fs[:, 1].min()) - TAB[3], 1),
            under_like_column=bool(frs[:, 2].max() > 930 and frs[:, 3].max() > 1050),
            in_bottom_300=bool(frs[:, 3].max() > 1620))
        del fr_frames
    a, b = out['street_sunglasses']['eye_mid_settled']['mean'], out['street_smirk']['eye_mid_settled']['mean']
    out['eye_offset_between_showings_px'] = round(math.hypot(a[0] - b[0], a[1] - b[1]), 2)
    # texture at display scale (cheek / forehead Laplacian variance vs the Lanczos 2x of the native crop)
    patches = {'street_smirk': {'cheekL': (246, 433, 302, 489), 'cheekR': (395, 400, 465, 445),
                                'forehead': (300, 250, 380, 300)},
               'street_sunglasses': {'cheekL': (252, 394, 300, 442), 'cheekR': (395, 395, 460, 440),
                                     'forehead': (300, 230, 380, 290)}}

    def lv(img, bx):
        x0, y0, x1, y1 = [int(round(v * SCALE)) for v in bx]
        g = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1]
        return float(cv2.Laplacian(g, cv2.CV_32F).var())
    tex = {}
    for pose, pts in patches.items():
        sr = cv2.imread(os.path.join(CROPS, pose + '_2x.png')).astype(np.float32)
        nat = cv2.imread(os.path.join(CROPS, pose + '.png'))
        lz = cv2.resize(nat, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        used = np.ascontiguousarray(rgba16(pose)[..., 2::-1]).astype(np.float32) / 257.0
        dn = lambda im: cv2.resize(im, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)  # noqa: E731
        lzd, srd, ud = dn(lz), dn(sr), dn(used)
        tex[pose] = {k: dict(sr_raw=round(lv(srd, bx) / lv(lzd, bx), 2), used=round(lv(ud, bx) / lv(lzd, bx), 2))
                     for k, bx in pts.items()}
    out['texture_display_scale_vs_lanczos2x'] = tex
    # halo: 3 px ring outside the subject's alpha, tile feed with the subject minus the plate-only feed (sRGB code
    # values, no finish) -> matte fringe + designed glow; 'matte' = plain cut-out (matte quality alone)
    halo = {}
    for sh in FACES:
        t = sh['t0'] + 1.0
        L = layers(sh['pose'], sh.get('look', 'A'))
        a_lay = np.zeros((TILE_H, TILE_W, 4), np.float32)
        B, R, rot, br, lift = _xf(t, sh)
        Wd, Hd = L['size']
        K.draw(a_lay, L['matte'], B[0], B[1], rot=rot, anchor=(L['bust'][0] / Wd, L['bust'][1] / Hd))
        a = a_lay[..., 3]
        hard = (a > 0.05).astype(np.uint8)
        ring = (cv2.dilate(hard, np.ones((7, 7), np.uint8)) - hard).astype(bool)
        ring &= _feed_mask() > 0.999
        base = _luma8(_u8(feed(t, sh, 'plate')))
        r = {}
        for md in ('full', 'matte'):
            r[md] = round(float((_luma8(_u8(feed(t, sh, md))) - base)[ring].mean()), 2)
        halo[sh['pose']] = dict(ring_px=int(ring.sum()), full_minus_plate=r['full'], matte_minus_plate=r['matte'])
    out['halo_3px_ring_code_values'] = halo
    # emissive peak (linear) of the rim on the face layers
    out['rim_peak_linear'] = {sh['pose']: round(float(np.max(np.concatenate([_lit(sh['pose'], sh.get('look', 'A'), sh['rim_gain'])[0][..., 0].ravel(),
                                                                            _lit(sh['pose'], sh.get('look', 'A'), sh['rim_gain'])[1][..., 0].ravel()]))), 3)
                              for sh in FACES}
    # cost
    cv = np.zeros((K.H, K.W, 4), np.float32)
    for sh in FACES:
        t0 = time.time()
        for i in range(10):
            draw_tile(cv, sh['t0'] + 0.5 + i * 0.1)
        out['ms_draw_tile_' + sh['pose']] = round((time.time() - t0) / 10 * 1000, 1)
    return out


def _boards():
    """QA boards: matte over black / FLAME / white at 200 %, and the tile feed at 200 % per pose."""
    od = os.path.join(K.WS, 'pehle_wala', 'qa', 'faces')
    os.makedirs(od, exist_ok=True)
    prewarm()
    paths = []
    for sh in FACES:
        L = layers(sh['pose'], sh.get('look', 'A'))
        m = L['matte']
        rows = []
        for bg in ((0, 0, 0), tuple(K.C['FLAME']), (1, 1, 1)):
            c = np.zeros(m.shape, np.float32)
            c[..., :3] = np.float32(bg)
            c[..., 3] = 1
            c = m + c * (1 - m[..., 3:4])
            u8 = _u8(c)
            rows.append(cv2.resize(u8, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
        img = np.concatenate(rows, 1)
        p = os.path.join(od, 'matte200_%s.png' % sh['pose'])
        cv2.imwrite(p, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        paths.append(p)
    print('\n'.join(paths))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        print(json.dumps(_check(), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
    elif len(sys.argv) > 1 and sys.argv[1] == 'boards':
        _boards()
