"""beta_tum_karte_kya_ho.py - Reel 4 / C02 "Beta, tum karte kya ho?" (look gold_hour, 85.714 BPM, 36.4 s = 1,092 f).

Contract: brand_reels/design/reels/beta_tum_karte_kya_ho/HANDOFF.md (r3, binding) > BRIEF.md r2 (6.2-6.11, 7) >
TOOLKIT.md. Grid X.Grid(600 / 7): beat 0.7 s = 21 f, bar 2.8 s = 84 f. Helpers: beta_tum_karte_kya_ho_ui (UI),
beta_tum_karte_kya_ho_parody (P1 wedding, P2 cartoon, stamp), beta_tum_karte_kya_ho_faces (JD, face-compositor).

SHOT LIST (f = frame; cut times use the HALF rule through jawad_tx.Plan)
  S0  f0-83     hook: JD suit_confused (look A, dolly from t = -0.7), "Mummy" chip + typing pill -> bubble f8-f12,
                H1 BETA, TUM / karte kya / HO? fades in f9-f12 (legible f11), halo flare f42; captions L1
  S1  f84-146   c1 L3 (push 0.5) -> translate card POPs up from y+520 (2.7-3.2); "Video editor" types f98-f116;
                "Shaadi wala?" SETTLE-pops f126; labels / output field / arrow fade f135-f141; window grows f135-f147
  M6  f135-158  c2 4.9 STAR object carry: the ember spark rides PATH, the word rides with it (overlay) and is absorbed f147-f153
  S2  f147-230  big window: P1 wedding ground f147-f159, "Happy Wedding" wipe f153-f165 / out f180-f189, burst f159;
                "Motion designer" types f190-f205; P2 "Cartoon?" pill + halftone + MOTION wobble POP f215 (r3), boing 2 f221
  S3  f231-251  c3 L3 (0.7): JD suit_shocked punch-in (look D)
  S4  f252-335  c4 L3 (0.4): card returns big, "Content creator", window scrim 0.75, stamp SLAM (-7 deg), accent f294
  M3  f327-344  c5 11.2 motion match (re-hook 1): card A swipes left on MOVE, card B arrives at MOVE + 800
  S5  f336-419  card B "Brands ke liye cinematic reels"; loading dots f364-f371; window out f372-f377; card dims x0.55
                f378 under the KILLER bubble (overlay); fold rx 0 -> 80 deg + drop 300 px f410-f419
  S6  f420-503  c6 L3 (0.6): JD suit_neutral (look D); killer bubble holds to f449, exits f450-f458; light -15 % from 15.4
  S7  f504-587  c7 L3 (0.4): time skip: wooden table + light band, face-down phone (creep 39 px / +2.35 deg), flame edge
                glow, chip "Kuch mahine baad" POP f504 / out f540-f545, count pill "Khandaan . 12 -> 47 -> 99+" from f546
  M2  f582-593  c8 19.6 hue bridge (re-hook 2)
  S8  f588-839  "Khandaan" chat: flood f588-f609, forwarded REEL_THUMB (this reel's cover) f651, "Kamaal!" f672, "Wah!"
                f693, "Mummy is typing" f756 (freeze f777-f797, resume f798, slow f819-f824)
  M1  f825-854  c9 28.0 STAR shape match: typing dot 3 -> the sun disc (540, 1260, 110) via match (540, 1260, 180)
  S9  f840-860  PAYOFF: sun; Mummy bubble + P1 MERA BETA / cinema / BANATA HAI (overlay, f840-f965)
  S10 f861-965  c10 L3 (0.7): JD suit_hand_on_chest (look A) before the sun; sun swell f924-f939
  S11 f966-1070 c11 L3 (0.3): end-card world (sun sinks, push 1 %/s), EndCard('GROUP MEIN', 'bhejo') t0 32.2;
                Nani chip + pill POP f1050 (overlay, carried across c12)
  S12 f1071-1091 c12 L3 (0.3): S0 at t - 36.4 (loop pre-roll), seam f1091 -> f0 differs only in the chip word

SOUND: cues() delegates to beta_tum_karte_kya_ho_sfx (lazy; that module reads SFX_EVENTS from here). Render with
--no-sfx-build and --audio <mix wav> (or the VO stem until the mix exists).
"""
import functools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                  # noqa: F401,E402  FIRST
from jawad_kit import K, T, J                     # noqa: E402
import jawad_tx as X                              # noqa: E402
import jawad_grade as G                           # noqa: E402
import endcard as E                               # noqa: E402
import snake_captions as SC                       # noqa: E402
import beta_tum_karte_kya_ho_faces as FF          # noqa: E402
import beta_tum_karte_kya_ho_ui as U              # noqa: E402
import beta_tum_karte_kya_ho_parody as P          # noqa: E402

import numpy as np                                # noqa: E402

DUR, LOOK, BPM = 36.4, 'gold_hour', 600 / 7
FPS = 30
SPLICE_F = 84
HALF = 0.5 / FPS
GR = X.Grid(600 / 7)
RW = '/home/user/100/workspace/jawad_reels/beta_tum_karte_kya_ho'
NOCAP = os.environ.get('BTK_NOCAP', '') == '1'

T_CARTOON = 215 / FPS                       # r3 (HANDOFF 2 #4): "Cartoon?" pop + MOTION wobble start
T_BOING2 = 221 / FPS
SFX_EVENTS = {'cartoon': T_CARTOON}          # read by beta_tum_karte_kya_ho_sfx.events()
T_CARD = 32.2
SUN_K, SUN_GLOW = 0.45, 0.55                 # sun disc (x AMBER, 'over') + glow strength: f850 measured 8-bit max
                                             # R 231 (< 250); the brief's AMBER x 1.3 'add' + 0.9 measured 255 (white)
CLEAR = [(4.2, 4.9), (T_CARTOON, 7.7), (27.5, 28.0)]

# ---------------------------------------------------------------------------------------------- transitions (BRIEF 6.8)
GLUE = [(2.8, 0.5), (7.7, 0.7), (8.4, 0.4), (14.0, 0.6), (16.8, 0.4), (28.7, 0.7), (32.2, 0.3), (35.7, 0.3)]
M6_PATH = ((540, 736), (625, 772), (615, 858), (540, 875))
M6_OPTS = dict(pre=12, post=12, path=M6_PATH)
MOVE = K.Track([(10.9, (540, 0), 'in_cubic'), (11.2, (140, 0), 'out_cubic'), (11.5, (-260, 0))])
M3_OPTS = dict(pre=9, post=9, move=MOVE)
M1_OPTS = dict(pre=15, post=15, a=U.dot3_pose, b=(540.0, 1260.0, 110.0), match=(540.0, 1260.0, 180.0))
FEATURES = [('M6', 4.9, M6_OPTS), ('M3', 11.2, M3_OPTS), ('M2', 19.6, dict(pre=6, post=6)), ('M1', 28.0, M1_OPTS)]
PLAN = X.Plan([('L3', c) for c, g in GLUE] + FEATURES)       # 12 cuts, 13 scenes S0..S12
CUTS = [(0.0, 0.6)] + GLUE
M6_CURVE = X._catmull(M6_PATH)


def fidx(t):
    return int(math.floor(t * FPS + 0.5))


# ---------------------------------------------------------------------------------------------- assets
@functools.lru_cache(maxsize=1)
def card():
    c = E.EndCard('GROUP MEIN', 'bhejo', monogram='JD', dur=4.2)
    return c


@functools.lru_cache(maxsize=1)
def embers():
    return J.embers(60, seed=21, bright=0.4)


@functools.lru_cache(maxsize=1)
def sun_parts():
    """SUN_DISC r 110: an opaque gold disc (drawn 'over', so the bright horizon band never adds into it: the
    brief's AMBER x 1.3 'add' measured white after the finish) + its FLAME glow (sigmas 12/36/90, 'add')."""
    d = K.disc(110, U.C('AMBER', SUN_K))
    g = K.glow(K.disc(110, U.C('AMBER', 1.0)), U.C('FLAME'), sigmas=(12, 36, 90), strength=SUN_GLOW, include=False)
    return U.ro(d), U.ro(g)


@functools.lru_cache(maxsize=1)
def assets():
    P.ensure_fonts()
    a = dict(card=card(), sun=sun_parts(), table=U.table_albedo(), phone=U.phone_sprites(),
             wed=P.wedding_ground(), wt=P.wedding_title(), cg=P.cartoon_ground(), mg=P.motion_glyphs(180),
             stamp=P.stamp_sprite())
    a['card']._settled_layer()
    return a


@functools.lru_cache(maxsize=1)
def thumb():
    """REEL_THUMB: this reel's cover canvas (t = 1.0, no captions, linear, before post) at 300x533."""
    return U.make_thumb(cover_layers(1.0))


# ---------------------------------------------------------------------------------------------- world helpers
def room(t, cam=None, intensity=1.0):
    return K.background(LOOK, t, cam, bokeh=0.6, intensity=intensity)


def motes(cv, t, cam=None):
    sc = K.Scene(cam if cam is not None else K.Cam())
    sc.particles(embers(), t)
    sc.render(cv)


def sun(cv, x, y, r=110.0, glow_k=1.0, op=1.0):
    d, g = sun_parts()
    s = r / 110.0
    K.draw(cv, g, x, y, scale=s, opacity=op * min(1.0, glow_k), mode='add')
    if glow_k > 1.0:
        K.draw(cv, g, x, y, scale=s, opacity=op * (glow_k - 1.0), mode='add')
    K.draw(cv, d, x, y, scale=s, opacity=op)


def face_world(t, key, tau=None):
    tau = t if tau is None else tau
    wc = FF.world_cam(t, key)
    cv = room(tau, wc, FF.window_gain(t))
    if key == 'S10':
        u = K.ramp(t, 30.8, 31.3, 'out_cubic')
        sun(cv, 540, 1260, glow_k=1.0 + 0.3 * u)
    FF.draw_face(cv, key, t)
    motes(cv, tau, wc)
    return cv


def card_float(t):
    return K.wiggle(t, 0.3, 4.0, 11), K.wiggle(t, 0.25, 3.0, 12)


def card_xf(t, s=1.0, ddx=0.0, ddy=0.0):
    dx, dy = card_float(t)
    return U.Xf(s, dx + ddx, dy + ddy)


def card_base(t):
    cv = room(t)
    motes(cv, t)
    return cv


# ---------------------------------------------------------------------------------------------- scenes
def S0(t):
    return face_world(t, 'S0')


def _enter(t):
    """Card POP up from y + 520 over 2.7-3.2 (already moving at f84; lands ~3.1)."""
    u = K.clamp((t - 2.7) / 0.5)
    return 520.0 * (1.0 - K.EASE['out_back'](u))


def S1(t):
    cv = card_base(t)
    k = fidx(t)
    xf = card_xf(t, ddy=_enter(t))
    U.card_body(cv, xf)
    n = U.typed('Video editor', t, 98 / FPS, 116 / FPS)
    U.card_input(cv, xf, 'Video editor', n=n, caret=(96 <= k < 124), t=t)
    lab = 1.0 - K.ramp(t, 135 / FPS - HALF, 141 / FPS, 'in_cubic')
    U.card_labels(cv, xf, lab)
    u = K.ramp(t, 135 / FPS - HALF, 147 / FPS, 'out_cubic')
    U.card_window(cv, xf, U.window_at(u))
    if 126 <= k < 135:
        if k >= 131:                                    # the carrier spark ignites under the word (rests on path[0])
            K.draw(cv, X.carrier(), 540, 736, mode='add', opacity=K.ramp(t, 131 / FPS - HALF, 134 / FPS, 'inout_sine'))
        s = 0.9 + 0.1 * X.spring(max(0.0, t - 4.2), 'SETTLE')
        op = K.ramp(t, 4.2 - HALF, 4.2 + 3 / FPS, 'out_cubic')
        wx, wy = xf.p(540, 736)
        U.tx('Shaadi wala?', 'jw_key', 130).draw(cv, wx, wy, scale=s, opacity=op)
    return cv


def S2(t):
    cv = card_base(t)
    k = fidx(t)
    xf = card_xf(t)
    U.card_body(cv, xf)
    par = K.ramp(t, 147 / FPS - HALF, 150 / FPS, 'inout_sine') * (1.0 - K.ramp(t, 186 / FPS, 189 / FPS, 'inout_sine'))
    par = max(par, K.ramp(t, T_CARTOON - HALF, T_CARTOON + 3 / FPS, 'inout_sine'))
    dim = 1.0 - 0.5 * par
    if k < 186:
        U.card_input(cv, xf, 'Video editor', dim=dim * (1.0 - K.ramp(t, 180 / FPS, 186 / FPS, 'in_cubic')))
    elif k >= 190:
        n = U.typed('Motion designer', t, 190 / FPS, 205 / FPS)
        U.card_input(cv, xf, 'Motion designer', n=n, dim=dim, caret=(188 <= k < 209), t=t)
    U.card_window(cv, xf, U.WIN_BIG)
    P.wedding(cv, t, xf)
    P.cartoon(cv, t, xf, T_CARTOON, T_BOING2)
    if 159 <= k < 166:                                  # the spark at rest on path[-1] fades into the burst
        K.draw(cv, X.carrier(), 540, 875, mode='add', opacity=1.0 - K.clamp((t - 159 / FPS) / (6 / FPS)))
    return cv


def S3(t):
    return face_world(t, 'S3')


def _shake(t, t0=8.4, amp=6.0):
    d = t - t0
    if d <= 0:
        return 0.0, 0.0
    a = amp * math.exp(-d / 0.08)
    return a * math.sin(2 * math.pi * 13.0 * d), 0.6 * a * math.sin(2 * math.pi * 11.0 * d)


def _card_a(dst, t, xf):
    U.card_body(dst, xf)
    U.card_input(dst, xf, 'Content creator')
    U.card_window(dst, xf, U.WIN_BIG)
    U.scrim(dst, U.WIN_BIG, 24, 0.75 * K.ramp(t, 8.4 - HALF, 8.4 + 2 / FPS, 'linear'), xf)
    P.stamp(dst, t, xf)


WHIP_PX = 66.0


def _whipped(cv, t, fn, xf):
    """M3: |k| <= 3 frames around c5 the card layer gets a 66 px horizontal whip smear (BRIEF 6.4 M3)."""
    if abs(fidx(t) - 336) <= 3:
        lay = np.zeros_like(cv)
        fn(lay, t, xf)
        K.whip_blur(lay, WHIP_PX, 0.0)
        U.over(cv, lay)
    else:
        fn(cv, t, xf)


def S4(t, move=None):
    mv = MOVE(t) if move is None else move
    cv = card_base(t)
    acc = K.ramp(t, 9.8, 10.5, 'out_cubic')
    sx, sy = _shake(t)
    xf = card_xf(t, s=1.0 + 0.02 * acc, ddx=(mv[0] - 540.0) + sx, ddy=-6.0 * acc + sy)
    _whipped(cv, t, _card_a, xf)
    return cv


def _card_b(dst, t, xf):
    k = fidx(t)
    U.card_body(dst, xf)
    U.card_input(dst, xf, 'Brands ke liye cinematic reels')
    wo = 1.0 - K.ramp(t, 372 / FPS - HALF, 377 / FPS, 'in_cubic')
    if wo > 1e-4:
        U.card_window(dst, xf, U.WIN_BIG, opacity=wo)
        if 364 <= k:
            U.loading_dots(dst, t, xf, opacity=wo * K.ramp(t, 364 / FPS - HALF, 366 / FPS, 'out_cubic'))
    dk = K.ramp(t, 378 / FPS - HALF, 384 / FPS, 'inout_sine')
    U.scrim(dst, U.CARD, 48, 0.45 * dk, xf)


def S5(t, move=None):
    mv = MOVE(t) if move is None else move
    cv = card_base(t)
    fold = K.ramp(t, 410 / FPS - HALF, 419 / FPS + HALF, 'in_cubic')
    xf = card_xf(t, ddx=(mv[0] + 800.0 - 540.0))
    if fold <= 1e-4:
        _whipped(cv, t, _card_b, xf)
        return cv
    LW, LH = 1120, 1100
    lay = np.zeros((LH, LW, 4), np.float32)
    _card_b(lay, t, U.Xf(1.0, LW / 2 - 540.0, LH / 2 - 736.0))
    cx, cy = xf.p(540, 736)
    cy += 300.0 * fold
    K.draw_plane(cv, U.ro(lay), K.Cam(), (cx - 540.0, cy - 960.0, 0.0), float(LW), rot=(80.0 * fold, 0.0, 0.0),
                 opacity=1.0 - 0.35 * fold, dof=False)
    return cv


def S6(t):
    return face_world(t, 'S6')


def S7(t):
    return U.skip_scene(t)


def S8(t):
    cv = card_base(t)
    U.chat(cv, t, thumb())
    return cv


def S9(t):
    cv = room(t)
    sun(cv, 540, 1260)
    return cv


def S10(t):
    return face_world(t, 'S10')


def S11(t):
    u = K.clamp((t - T_CARD) / 3.5)
    s = 1.0 + 0.01 * max(0.0, t - T_CARD)
    wz = 10500.0 * (1.0 - 1.0 / s)
    cam = K.Cam(pos=(0.0, 0.0, -1500.0 + wz), focal=1500.0, aperture=24.0, focus_dist=1500.0 - wz)
    cv = room(t, cam)
    sun(cv, 540, 1400 + 40 * u, r=92.0, op=1.0 - 0.4 * u)
    motes(cv, t, cam)
    return cv


def S12(t):
    return face_world(t, 'S12', tau=t - DUR)


SCENES = [S0, S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12]


# ---------------------------------------------------------------------------------------------- overlays
def carried_word(cv, t):
    """M6: 'Shaadi wala?' rides the spark's path f135-f153 (scale 1 -> 0.85 f135-f147, then absorbed 0.85 -> 0.5 with
    opacity 1 -> 0, in_cubic, f147-f153)."""
    k = fidx(t)
    if not (135 <= k < 154):
        return
    u = K.clamp((t - 4.5) / (23 / FPS))
    x, y = X._path_at(M6_CURVE, K.EASE['inout_cubic'](u))
    if t < 4.9:
        s = K.lerp(1.0, 0.85, K.EASE['inout_cubic'](K.clamp((t - 4.5) / 0.4)))
        op = 1.0
    else:
        v = K.ramp(t, 4.9, 153 / FPS, 'in_cubic')
        s, op = K.lerp(0.85, 0.5, v), 1.0 - v
    if op > 1e-4:
        U.tx('Shaadi wala?', 'jw_key', 130).draw(cv, x, y, scale=s, opacity=op)


def overlays(cv, t):
    k = fidx(t)
    if k < SPLICE_F:
        U.hook_ui(cv, t, 'Mummy')
    if 84 <= k < 420 or 588 <= k < 840:
        U.pov(cv)
    carried_word(cv, t)
    U.killer(cv, t)
    U.payoff(cv, t)


def nani(cv, t):
    if t >= 35.0 - HALF:
        U.hook_ui(cv, t - DUR, 'Nani', pop=(t, 35.0), pov_op=K.ramp(t, 35.0 - HALF, 35.2, 'out_cubic'))


# ---------------------------------------------------------------------------------------------- captions (HANDOFF 6)
def AVOID(t):
    """Caption avoid rects by scene (HANDOFF 6; scene ranges in reel seconds, as the caption dry run used them)."""
    if t < 2.8:
        return [FF.head_rect('S0', t), U.BUBBLE_H, U.CHIP_R, U.POV_R]
    if t < 7.7 or 8.4 <= t < 14.0:
        return [U.CARD, U.POV_R]
    if t < 8.4:
        return [FF.head_rect('S3', t)]
    if t < 16.8:
        r = [FF.head_rect('S6', t)]
        if t < 15.3:
            r.append((150, 252, 930, 520))
        return r
    if t < 19.6:
        return [U.CHIP_PILL, U.PHONE_BOX]
    if t < 28.0:
        return [U.CARD, U.POV_R]
    if t < 28.7:
        return [U.PAYOFF_R, U.CHIP_R, U.SUN_BOX]
    return [U.PAYOFF_R, U.CHIP_R, FF.head_rect('S10', min(t, 32.2 - 1.0 / FPS))]


@functools.lru_cache(maxsize=1)
def captions():
    FF.prewarm()
    W = json.load(open(RW + '/vo/words.json'))
    l1 = [w for w in W if w['line'] == 'L1']
    body = [w for w in W if w['line'] != 'L1']
    hook = SC.Captions(l1, band='upper', y=880, avoid=lambda t: AVOID(min(t, 2.79)))
    main = SC.Captions(body, band='upper', y=880, avoid=lambda t: AVOID(max(t, 2.8)),
                       hide=((16.85, 18.2), (32.2, 36.4)), clear=CLEAR)
    return hook, main


def cap_draw(cv, t, version='A'):
    hook, main = captions()
    if t < 2.8:
        if version == 'A':
            hook.draw(cv, t, opacity=1.0 - K.ramp(t, 2.6, 2.8, 'in_cubic'))
    else:
        main.draw(cv, t, opacity=1.0 - K.ramp(t, 32.0, 32.25, 'in_cubic'))


# ---------------------------------------------------------------------------------------------- render contract
def frame(t, version='A', caps=True):
    """The reel frame at t (linear, before post). version 'B' = hook-B splice frames: no caption layer before 2.8 s."""
    cv = PLAN.draw(t, SCENES)
    overlays(cv, t)
    if caps and not NOCAP:
        cap_draw(cv, t, version)
    card().draw(cv, t, T_CARD)
    nani(cv, t)
    return cv


def draw(t):
    return frame(t, 'A')


def post(cv, t):
    kw = {}
    for tid, c, o in FEATURES:                     # feature post (M2 exposure bridge ...); NOT PLAN.post_kw
        for k_, v in X.TX[tid].post_kw(t, c, **o).items():
            kw[k_] = kw.get(k_, 0.0) + v if k_ == 'push' else v
    kw['push'] = kw.get('push', 0.0) + card().post_kw(t, T_CARD, DUR).get('push', 0.0)
    return G.tx_finish(cv, t, LOOK, cuts=CUTS, rays=0.0, **kw)


def samples(t):
    s = PLAN.samples(t)
    k = fidx(t)
    if 84 <= k <= 92 or 252 <= k <= 256 or 410 <= k <= 419:
        s = max(s, 5)
    if 829 <= k <= 845:                          # M1: the push into dot 3 / the sun's pull-back (fast zoom)
        s = max(s, 11)
    return s


def cues():
    """Delegate to the sound designer's module (lazy: it imports this module for SFX_EVENTS)."""
    try:
        import beta_tum_karte_kya_ho_sfx as S
        return S.cues()
    except Exception as e:                           # the rebuilt sound kit is not ready yet (KIT_READY missing)
        sys.stderr.write('beta_tum_karte_kya_ho.cues(): sfx module unavailable (%s); no cues\n' % e)
        return []


def cover_layers(t=1.0):
    """The cover's layers at t (world, JD, Mummy chip, bubble, H1, POV), no captions, linear, before post."""
    cv = S0(t)
    U.hook_ui(cv, t, 'Mummy')
    return cv


def cover():
    """f30 cover frame without captions, finished (linear canvas after post)."""
    return post(cover_layers(1.0), 1.0)


def blocks(t):
    """QA: designed text blocks on screen at t -> [(name, (x0, y0, x1, y1))] (+ the caption chunk)."""
    k = fidx(t)
    out = []
    if k < 9:
        out.append(('pill', U.PILL))
    elif k < 84:
        out.append(('H1 bubble', U.BUBBLE_H))
    elif k < 231:
        out.append(('card', U.CARD))
    elif 252 <= k < 378:
        out.append(('card', U.CARD))
    elif 378 <= k < 420:
        out += [('card B', U.CARD), ('killer', U.killer_rect(t))]
    elif 420 <= k < 459:
        out.append(('killer', U.killer_rect(t)))
    elif 504 <= k < 588:
        out.append(('chip', U.CHIP_PILL))
    elif 588 <= k < 840:
        out.append(('chat', U.CARD))
    elif 840 <= k < 966:
        out.append(('payoff', U.PAYOFF_R))
    if k >= 966:
        bx = card().boxes()
        out.append(('endcard', (min(b[0] for b in bx.values()), min(b[1] for b in bx.values()),
                                max(b[2] for b in bx.values()), max(b[3] for b in bx.values()))))
    if k >= 1050:
        out.append(('nani', U.PILL))
    hook, main = captions()
    cap = hook if t < 2.8 else main
    for ch in cap.chunks:
        if ch.t_in <= t < ch.t_exit1 and getattr(ch, 'lay', None):
            out.append(('cap:' + ' '.join(w['word'] for w in ch.words), tuple(ch.lay['bbox'])))
    return out


def prewarm():
    P.ensure_fonts()
    FF.prewarm()
    assets()
    hook, main = captions()
    hook.prewarm()
    main.prewarm()
    thumb()
