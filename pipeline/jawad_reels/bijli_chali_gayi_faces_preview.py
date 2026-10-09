"""bijli_chali_gayi_faces_preview.py - face-compositor test harness for C11 (render.py-compatible; NOT production art).

Stand-in worlds around the two face shots so bijli_chali_gayi_faces.py can be judged in context through the real finish
(G.tx_finish, 'dusk', the brief's CUTS) and the real L4 at f880:
    S7b  f740-f839  dusk wall plate (indigo near-black + the candle's warm pool) at z = BF.Z_WALL, the real Blender
                    candle ('self' pass) at z = BF.Z_CANDLE with a procedural 70 px flame on its wick tip, all through
                    BF.cam_s7b(t); payoff lockup J.HouseTitle('BIJLI NE SIKHAYA', 'sabr') from f800 (screen space)
    S7c  f840-f879  candle macro (flame 150 px at (540, 1240)) + the lockup
    S8a  f880-f919  the real lit room plate (desk_plate 'lit' + crt / tower / box + a stand-in CRT edit + fan) at
                    z = BF.Z_WALL through BF.cam_s8a(), entered through X.Plan([('L4', 880 / 30)])
The timeline builder owns the real worlds (bijli_chali_gayi.py); only the BF calls carry over.

    tools/heavy.sh python3 render.py bijli_chali_gayi_faces_preview --stills 24.7,25.5,27.95 --workers 1
    JAWAD_C11_FACES_MODE=nojd|plain|full   (world only | cut-out without look | the shot)
    tools/heavy.sh python3 bijli_chali_gayi_faces_preview.py qa      -> RWS/out/faces_preview/qa.json + crops
Outputs: <WS>/out/bijli_chali_gayi_faces_preview -> RWS/out/faces_preview (symlink).
"""
import functools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit as J                             # noqa: E402  FIRST
from jawad_kit import K                           # noqa: E402
import jawad_grade as G                           # noqa: E402
import jawad_tx as X                              # noqa: E402
import sprites3d as S3                            # noqa: E402
import bijli_chali_gayi_faces as BF               # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402

DUR = 1040 / 30
LOOK = 'dusk'
BPM = 90
RWS = '/home/user/100/workspace/jawad_reels/bijli_chali_gayi'
OUTQ = os.path.join(RWS, 'out', 'faces_preview')
CUTS = [(0.0, 0.6), (80 / 30, 0.5), (160 / 30, 0.25), (240 / 30, 0.5), (400 / 30, 0.8), (720 / 30, 0.3),
        (740 / 30, 0.2), (920 / 30, 0.3)]                       # BRIEF section 7
PLAN = X.Plan([('L4', 880 / 30)])
MODE = os.environ.get('JAWAD_C11_FACES_MODE', 'full')


def lin(h, k=1.0):
    return np.float32(K.hexlin(h)) * np.float32(k)


def _asset(name):
    return S3.Asset3D(name, 'passes', root=RWS + '/assets3d')


# ============================================================================================ S7b / S7c stand-ins
@functools.lru_cache(maxsize=1)
def wall_s7b():
    """Back wall seen behind him (1080 x 1920 px at rest, drawn as a plane at Z_WALL): NIGHT_0 with the dusk indigo
    in the far corners and the candle's broad warm pool (the flame is ~1.45 m in front of the wall)."""
    h, w = K.H, K.W
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cv = np.zeros((h, w, 4), np.float32)
    cv[..., :3] = lin('#070404')
    cx, cy = BF.CANDLE_XY
    r2 = ((xx - cx) / 520.0) ** 2 + ((yy - cy - 60) / 640.0) ** 2
    pool = np.exp(-r2)[..., None]
    cv[..., :3] += pool * (lin('#FFB547', 0.030) + lin('#FF6A1A', 0.020))
    ind = np.clip(1.0 - pool[..., 0] * 1.6, 0, 1)[..., None] * (0.5 + 0.5 * (yy / h))[..., None]
    cv[..., :3] += ind * lin('#171431', 0.35)
    cv[..., 3] = 1.0
    return cv


@functools.lru_cache(maxsize=4)
def flame_sprite(height):
    """Procedural candle flame (BRIEF 6.9): teardrop, AMBER x2.6 core, FLAME edge, soft halo. Anchor = wick (bottom
    centre of the visible flame) at (0.5, 0.62) of the returned sprite (padded so the halo fades out inside it)."""
    hh = int(height * 3.0)
    ww = int(height * 2.4)
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    base_y = hh * 0.62
    v = (base_y - yy) / height                                   # 0 at the wick, 1 at the tip
    halfw = 0.17 * height * np.maximum(np.sin(np.pi * np.clip(v * 0.92 + 0.08, 0, 1)), 0) ** 0.8 \
        * np.clip(1.25 - v, 0, 1)
    d = np.abs(xx - ww / 2) / np.maximum(halfw, 1e-3)
    inside = np.clip(1.0 - d, 0, 1) * ((v > 0) & (v < 1)).astype(np.float32)
    inside = cv2.GaussianBlur(inside, (0, 0), max(1.0, height * 0.03))
    core = np.clip(inside * 1.6 - 0.45, 0, 1)
    out = np.zeros((hh, ww, 4), np.float32)
    out[..., :3] = inside[..., None] * lin('#FF6A1A', 1.4) + core[..., None] * lin('#FFB547', 2.6)
    halo = cv2.GaussianBlur(inside, (0, 0), height * 0.35)
    out[..., :3] += halo[..., None] * lin('#FF9F1C', 0.6)
    return out


@functools.lru_cache(maxsize=1)
def candle_body():
    """'self' (lit by its own flame) + 0.2 x 'key_r' (a little room bounce on the wax), stand-in only."""
    a = _asset('candle')
    spr = np.array(a.by_label('self'), np.float32)
    spr[..., :3] += np.float32(0.2) * a.by_label('key_r')[..., :3]          # light only; alpha stays the matte
    return a, spr


def _candle(cv, cam, t, wick_xy, body_h, z, flame_h):
    """Candle body ('self' pass) as a plane at depth z with its wick tip at screen wick_xy (at rest), plus the flame
    billboard (flicker from BF.candle_flicker, sway from K.wiggle)."""
    a, spr = candle_body()
    wx, wy = a.features['wick_tip']
    bx, by = a.features['base']
    s = body_h / (by - wy)
    k = (z + BF.FOCAL) / BF.FOCAL
    P = ((wick_xy[0] - K.CX) * k, (wick_xy[1] - K.CY) * k, z)
    K.draw_plane(cv, spr, cam, P, spr.shape[1] * s * k, anchor=(wx / spr.shape[1], wy / spr.shape[0]))
    fl = flame_sprite(int(flame_h))
    g = BF.candle_flicker(t)
    sway = K.wiggle(t, 1.5, 3.0, 51) + K.wiggle(t, 4.0, 1.0, 52)
    lay = np.zeros_like(cv)
    K.draw_plane(lay, fl * np.float32(g), cam, P, fl.shape[1] * k, anchor=(0.5, 0.62), rot=(0, 0, sway))
    cv[..., :3] += lay[..., :3]


@functools.lru_cache(maxsize=1)
def lockup():
    return J.HouseTitle('BIJLI NE SIKHAYA', 'sabr', caps_px=86, key_px=260)


def world_s7b(t):
    cam = BF.cam_s7b(t)
    cv = K.new_canvas(K.C['NIGHT_0'])
    w = wall_s7b()
    k = (BF.Z_WALL + BF.FOCAL) / BF.FOCAL
    K.draw_plane(cv, w, cam, (0.0, 0.0, BF.Z_WALL), K.W * k * 1.04)       # 4 % overscan for the drift
    _candle(cv, cam, t, (BF.CANDLE_XY[0], BF.CANDLE_XY[1] + 35), 395.0, BF.Z_CANDLE, 70)
    if MODE != 'nojd':
        BF.draw_s7b(cv, t, cam=cam, mode='plain' if MODE == 'plain' else 'full')
    return cv


def world_s7c(t):
    cam = K.Cam(pos=(0.0, 0.0, -BF.FOCAL), focal=BF.FOCAL, aperture=BF.APERTURE, focus_dist=BF.FOCAL)
    cv = K.new_canvas(K.C['NIGHT_0'])
    k = (BF.Z_WALL + BF.FOCAL) / BF.FOCAL
    w = wall_s7b()
    K.draw_plane(cv, w, cam, (-(BF.CANDLE_XY[0] - 540) * k, 0.0, BF.Z_WALL), K.W * k * 1.6)   # overscan: no edge
    _candle(cv, cam, t, (540.0, 1240.0 + 75), 850.0, 0.0, 150)
    return cv


# ============================================================================================ S8a stand-in
TL = dict(tracks=[(40, 88), (98, 146), (156, 204)],
          blocks=[[(14, 92, 'F'), (98, 190, 'F'), (196, 250, 'F'), (256, 326, 'F')],
                  [(14, 60, 'E'), (66, 170, 'E'), (176, 286, 'E'), (292, 326, 'E')],
                  [(14, 120, 'F7'), (126, 214, 'E'), (220, 326, 'F7')]])


def crt_edit(t):
    """Stand-in of the BRIEF 6.9 CRT edit (340 x 240 glass px): three FLAME / EMBER clip tracks, IVORY playhead."""
    col = {'F': lin('#FF6A1A'), 'E': lin('#B3120E'), 'F7': lin('#FF6A1A', 0.7)}
    img = np.zeros((240, 340, 3), np.float32)
    img[...] = lin('#170A07', 1.6)
    for (y0, y1), row in zip(TL['tracks'], TL['blocks']):
        img[y0:y1, 14:326] = lin('#2A1A15', 1.2)
        for x0, x1, c in row:
            img[y0:y1, x0:x1] = col[c]
    px = 14 + ((136 + 60 * (t - DUR)) % 312)
    img[14:204, int(px - 3):int(px + 3)] = lin('#FFF3E6')
    img[1::2] *= 0.75
    return img


def room_plate(t):
    """The lit room (S1A frame-0 composition) from the real Blender passes, with the stand-in CRT edit and fan."""
    plate, crt, tower, box = (_asset(n) for n in ('desk_plate', 'crt_room', 'tower_room', 'box_room'))
    cv = K.new_canvas(K.C['NIGHT_0'])
    cv[..., :3] = plate.by_label('lit')[..., :3]
    cv[..., 3] = 1.0
    # fan: 3 dark blades, spinning up after f880 (2.5 s out_cubic to 4.5 rev/s), 5-position blur
    rate = 4.5 * K.ramp(t, 880 / 30, 880 / 30 + 2.5, 'out_cubic')
    acc = np.zeros((K.H, K.W), np.float32)
    for s in range(5):
        a0 = 360.0 * rate * (t + (s / 4 - 0.5) * 0.5 / 30) + 20.0
        m = np.zeros((K.H, K.W), np.uint8)
        for b in range(3):
            a = math.radians(a0 + 120 * b)
            pts = []
            for rr, ww in [(40, 18), (150, 48), (420, 64), (445, 38)]:
                pts.append((540 + rr * math.cos(a + math.atan2(ww / 2, rr)), 60 + 0.3 * rr * math.sin(a + math.atan2(ww / 2, rr))))
            for rr, ww in [(445, 38), (420, 64), (150, 48), (40, 18)]:
                pts.append((540 + rr * math.cos(a - math.atan2(ww / 2, rr)), 60 + 0.3 * rr * math.sin(a - math.atan2(ww / 2, rr))))
            cv2.fillPoly(m, [np.array(pts, np.int32)], 1)
        cv2.circle(m, (540, 60), 36, 1, -1)
        acc += m.astype(np.float32) / 5
    wood = lin('#170A07') + lin('#3B2A22', 0.12)
    cv[..., :3] = cv[..., :3] * (1 - acc[..., None]) + wood * acc[..., None]
    for a in (crt, tower, box):
        fx, fy = a.meta['frame_xy']
        K.draw(cv, a.by_label('room'), fx, fy, anchor=(0, 0))
    for a, k in ((tower, 0.8), (box, 0.30), (crt, 0.8)):
        fx, fy = a.meta['frame_xy']
        K.draw(cv, a.by_label('emit') * np.float32(k), fx, fy, anchor=(0, 0), mode='add')
    sm = crt.by_label('screen_mask')
    q = crt.meta['screen_quad']
    x0, y0, x1, y1 = int(q[0][0]), int(q[0][1]), int(q[2][0]), int(q[2][1])
    mask = sm[y0:y1, x0:x1, :3].mean(2)
    fx, fy = crt.meta['frame_xy']
    cv[fy + y0:fy + y1, fx + x0:fx + x1, :3] += crt_edit(t) * mask[..., None]
    return cv


def world_s8a(t):
    cam = BF.cam_s8a(t)
    cv = K.new_canvas(K.C['NIGHT_0'])
    k = (BF.Z_WALL + BF.FOCAL) / BF.FOCAL
    K.draw_plane(cv, room_plate(t), cam, (0.0, 0.0, BF.Z_WALL), K.W * k)
    if MODE != 'nojd':
        BF.draw_s8a(cv, t, cam=cam, mode='plain' if MODE == 'plain' else 'full')
    return cv


# ============================================================================================ reel contract
def WORLD_C(t):
    return world_s7c(t) if X.side_b(t, BF.S7B_T1) else world_s7b(t)


def WORLD_D(t):
    return world_s8a(t)


def draw(t):
    if t < BF.S7B_T0 - X.HALF:
        return K.new_canvas(K.C['NIGHT_0'])
    cv = PLAN.draw(t, [WORLD_C, WORLD_D])
    if 800 / 30 <= t < 29.0 + 0.36:
        lockup().draw(cv, t, 540, 520, t0=800 / 30, out_t0=29.0)
    return cv


def post(cv, t, **kw):
    return G.tx_finish(cv, t, LOOK, cuts=CUTS, **PLAN.post_kw(t), **kw)


def samples(t):
    f = int(math.floor(t * 30 + 0.5))
    return max(PLAN.samples(t), 5 if 880 <= f <= 900 else 3)


def prewarm():
    BF.prewarm()
    wall_s7b()
    candle_body()
    lockup()
    flame_sprite(70)
    flame_sprite(150)


# ============================================================================================ QA (measurements)
def _y(u8):
    return u8[..., :3].astype(np.float32) @ np.float32([0.2126, 0.7152, 0.0722])


def _frame(t, mode, samples_=1, grain=0.0):
    global MODE
    old = MODE
    MODE = mode
    try:
        cv = K.render_frame(draw, t, samples_, 0.5)
        post(cv, t, grain=grain)
        return K.to_srgb8(cv, t, dither=False)
    finally:
        MODE = old


def _lanczos_plain(name):
    """The same cut-out with its RGB replaced by a Lanczos 2x of the NATIVE crop (same matte): texture A/B."""
    cut = cv2.imread(os.path.join(BF.CUT, name + '.png'), cv2.IMREAD_UNCHANGED)
    nat = cv2.imread(os.path.join(BF.CROPS, name + '.png'))
    lz = cv2.resize(nat, (cut.shape[1], cut.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    rgba = np.dstack([lz[..., ::-1], cut[..., 3]])
    spr = K.sprite(rgba)
    spr.setflags(write=False)
    return spr


def _luma8(lin):
    return K.to_srgb(np.clip(lin, 0, 1)) @ np.float32([0.2126, 0.7152, 0.0722]) * 255.0


def fringe(name, t):
    """Matte fringe in context (the asset pipeline's halo_cv method, here over the REAL plate behind him): composite
    of the cut-out colours over the plate minus the same composite with interior-extended colour (no contamination
    possible), mean / p95 luma8 on the 3 px ring outside alpha 0.5; also over pure black. Cut-out px = screen px - the
    placement offset (scale 1.0). <= +6 passes."""
    a = BF.plain(name)[..., 3]
    F = np.where(a[..., None] > 1e-4, BF.plain(name)[..., :3] / np.maximum(a[..., None], 1e-4), 0).astype(np.float32)
    w = (a > 0.95).astype(np.float32)
    num = F * w[..., None]
    den = w.copy()
    ref = np.zeros_like(F)
    filled = w > 0
    ref[filled] = F[filled]
    for sg in (2, 4, 8, 16, 32):
        nb = cv2.GaussianBlur(num, (0, 0), sg)
        db = cv2.GaussianBlur(den, (0, 0), sg)
        new = (~filled) & (db > 1e-3)
        ref[new] = nb[new] / db[new, None]
        filled |= new
    m = (a >= 0.5).astype(np.uint8)
    ring = (cv2.dilate(m, np.ones((7, 7), np.uint8)) > 0) & (m == 0)
    ring[:3, :] = ring[-3:, :] = False
    ring[:, :3] = ring[:, -3:] = False
    # plate behind: the world without JD, pre-finish, linear, at the cut-out's screen placement (rest)
    global MODE
    old, MODE = MODE, 'nojd'
    try:
        plate = draw(t)
    finally:
        MODE = old
    P = BF.POSES[name]['P']
    ex, ey = BF.meta(name)['eye_mid']
    ox, oy = int(round(P[0] - ex)), int(round(P[1] - ey))
    h, w_ = a.shape
    B = np.zeros((h, w_, 3), np.float32)
    ys0, xs0 = max(0, oy), max(0, ox)
    ys1, xs1 = min(K.H, oy + h), min(K.W, ox + w_)
    B[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox] = plate[ys0:ys1, xs0:xs1, :3]
    vis = np.zeros_like(ring)
    vis[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox] = True
    out = {}
    for nm, bg in (('black', np.zeros_like(B)), ('plate', B)):
        c = _luma8(F * a[..., None] + bg * (1 - a[..., None]))
        r = _luma8(ref * a[..., None] + bg * (1 - a[..., None]))
        rr = ring & vis
        out[nm] = dict(mean=round(float((c - r)[rr].mean()), 2), p95=round(float(np.percentile((c - r)[rr], 95)), 2),
                       ring_px=int(rr.sum()))
    return out


def qa():
    os.makedirs(OUTQ, exist_ok=True)
    prewarm()
    res = {}
    res['fringe'] = {BF.POSE_A: fringe(BF.POSE_A, 790 / 30), BF.POSE_B: fringe(BF.POSE_B, 900 / 30)}
    print('fringe', res['fringe'], flush=True)
    frames = {'s7b_first': 740, 's7b_mid': 790, 's7b_lockup': 820, 's7b_last': 839, 's8a_first': 880, 's8a_mid': 900,
              's8a_last': 919}
    skin_src = {}
    for name in (BF.POSE_A, BF.POSE_B):
        cut = cv2.imread(os.path.join(BF.CUT, name + '.png'), cv2.IMREAD_UNCHANGED)
        a = cut[..., 3:4].astype(np.float32) / 255
        comp = (cut[..., 2::-1].astype(np.float32) * a + 128 * (1 - a)).astype(np.uint8)
        fx0, fy0, fx1, fy1 = [int(v) for v in BF.meta(name)['face_box']]
        skin_src[name] = G.skin_stats(comp, (fx0, fy0, fx1 - fx0, fy1 - fy0))
    res['skin_source'] = skin_src
    for key, f in frames.items():
        t = f / 30.0
        name = BF.POSE_A if f < 840 else BF.POSE_B
        full = _frame(t, 'full')
        nojd = _frame(t, 'nojd')
        plain = _frame(t, 'plain')
        al = BF.jd_alpha(t)
        if al is None:
            continue
        m = (al > 0.5).astype(np.uint8)
        ring = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) - m          # 3 px outside
        ring = ring.astype(bool)
        # exclude the frame border rows / cols (panel-cut bust bottoms run off the frame)
        ring[-4:, :] = False
        ring[:, :4] = False
        ring[:, -4:] = False
        yf, yn, yp = _y(full), _y(nojd), _y(plain)
        inside = al > 0.98
        far = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))) == 0
        lockrows = np.zeros_like(far)
        lockrows[230:800] = True                                     # the payoff lockup rows (S7b from f800)
        bgm = far & ~lockrows
        r = dict(frame=f, pose=name,
                 halo_plain_ring_minus_plate=round(float(yp[ring].mean() - yn[ring].mean()), 2),
                 halo_plain_ring_p95_minus_plate=round(float(np.percentile(yp[ring] - yn[ring], 95)), 2),
                 full_ring_minus_plate=round(float(yf[ring].mean() - yn[ring].mean()), 2),
                 jd_p2=round(float(np.percentile(yf[inside], 2)), 2), scene_p2=round(float(np.percentile(yf[bgm], 2)), 2),
                 jd_p50=round(float(np.percentile(yf[inside], 50)), 1),
                 jd_p995=round(float(np.percentile(yf[inside], 99.5)), 1), jd_max=round(float(yf[inside].max()), 1),
                 scene_max=round(float(yn.max()), 1), scene_p999=round(float(np.percentile(yn, 99.9)), 1),
                 frame_mean_full=round(float(yf.mean()), 2), eye_screen=[round(v, 2) for v in BF.eye_screen(t)],
                 jd_rect=BF.jd_rect(t), head_rect=BF.head_rect(t))
        r['black_match_dcv'] = round(r['jd_p2'] - r['scene_p2'], 2)
        # what the ring excess IS in the full look: share of the brightened ring px that are red-orange (the designed
        # rim / glow) vs low-saturation (a grey halo would be neutral)
        exc = (yf - yn)[ring] > 3
        hsv = cv2.cvtColor(np.ascontiguousarray(full), cv2.COLOR_RGB2HSV)[ring][exc]
        if len(hsv):
            hue = hsv[:, 0].astype(np.float32) * 2
            r['full_ring_excess_px'] = int(exc.sum())
            r['full_ring_excess_red_orange_share'] = round(float(((hue <= 45) | (hue >= 340)).mean()), 3)
            r['full_ring_excess_low_sat_share'] = round(float((hsv[:, 1] < 40).mean()), 3)
        # skin on the final frame: the face box on screen
        fb = BF.meta(name)['face_box']
        Ls = BF.layers(name)
        xy = BF._project_pts(name, t, BF.S7B_T0 if name == BF.POSE_A else BF.S8A_T0, BF._cam_at(name, t),
                             [(fb[0], fb[1]), (fb[2], fb[3])])
        bx0, by0 = int(xy[0, 0]), int(xy[0, 1])
        bx1, by1 = int(xy[1, 0]), int(xy[1, 1])
        bx0c = max(bx0, 0)
        r['skin_final'] = G.skin_stats(np.ascontiguousarray(full), (bx0c, by0, bx1 - bx0c, by1 - by0))
        r['face_box_screen'] = [bx0, by0, bx1, by1]
        cv2.imwrite(os.path.join(OUTQ, 'face_%s_f%d.png' % (key, f)),
                    cv2.cvtColor(full[max(0, by0 - 60):by1 + 60, max(0, bx0 - 60):bx1 + 60], cv2.COLOR_RGB2BGR))
        # 200 % edge crops over the world: hair crest and face front / shoulder
        for tag, (cx, cy) in {'crest': ((bx0 + bx1) // 2, by0 - 180), 'front': (bx1 + 10, (by0 + by1) // 2)}.items():
            x0, y0 = int(np.clip(cx - 90, 0, K.W - 180)), int(np.clip(cy - 90, 0, K.H - 180))
            crop = full[y0:y0 + 180, x0:x0 + 180]
            crop = cv2.resize(crop, (360, 360), interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(os.path.join(OUTQ, 'edge200_%s_%s.png' % (key, tag)), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
        res[key] = r
    # texture A/B in the final pipeline (grain off): SR master vs Lanczos 2x of the native crop, same matte, same look
    tex = {}
    for name, f, patch in ((BF.POSE_A, 790, 'cheek_patch'), (BF.POSE_B, 900, 'cheek_patch')):
        t = f / 30.0
        t0 = BF.S7B_T0 if name == BF.POSE_A else BF.S8A_T0
        cp = BF.meta(name)[patch]
        xy = BF._project_pts(name, t, t0, BF._cam_at(name, t), [(cp[0], cp[1]), (cp[2], cp[3])])
        x0, y0, x1, y1 = int(xy[0, 0]) + 2, int(xy[0, 1]) + 2, int(xy[1, 0]) - 2, int(xy[1, 1]) - 2
        a_sr = _frame(t, 'full').astype(np.float32)
        orig = BF.plain
        BF.layers.cache_clear()
        BF.plain = _lanczos_plain
        try:
            a_lz = _frame(t, 'full').astype(np.float32)
        finally:
            BF.plain = orig
            BF.layers.cache_clear()
        def lv(img):
            g = (img[y0:y1, x0:x1] @ np.float32([0.2126, 0.7152, 0.0722])).astype(np.float32)
            return float(cv2.Laplacian(g, cv2.CV_32F).var())
        tex[name] = dict(frame=f, box=[x0, y0, x1, y1], lapvar_sr=round(lv(a_sr), 3), lapvar_lanczos=round(lv(a_lz), 3),
                         ratio=round(lv(a_sr) / max(lv(a_lz), 1e-6), 2))
        cv2.imwrite(os.path.join(OUTQ, 'tex_%s_sr_vs_lanczos.png' % name),
                    cv2.cvtColor(np.hstack([cv2.resize(a_sr[y0 - 40:y1 + 40, x0 - 40:x1 + 40].astype(np.uint8), None, fx=3, fy=3,
                                                       interpolation=cv2.INTER_NEAREST),
                                            cv2.resize(a_lz[y0 - 40:y1 + 40, x0 - 40:x1 + 40].astype(np.uint8), None, fx=3, fy=3,
                                                       interpolation=cv2.INTER_NEAREST)]), cv2.COLOR_RGB2BGR))
    res['texture_final_pipeline'] = tex
    with open(os.path.join(OUTQ, 'qa.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    print(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'qa':
        qa()
