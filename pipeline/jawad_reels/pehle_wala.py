"""pehle_wala.py - reel 1, C26 "Pehle Wala Hi Theek Tha (v1 se v27 tak)", 34.1333 s (1,024 f), 112.5 BPM
(16 f / beat, 64 f / bar), look inferno. Owner: motion-timeline-builder.

Sources (binding order): brand_reels/design/SLATE.md 3.1 + 5 -> reels/pehle_wala/BRIEF.md r2 -> HANDOFF.md (re-timed to
the measured VO and the real Blender glass; D1-D6 applied) -> SCRIPT.md / VO_TIMING.md (words) -> SOUND.md / FACES.md.
Helpers (this reel only): pehle_wala_state.py (pure state clock, VERSIONS, pins, pre1 path), pehle_wala_ad.py (the ad
under review), pehle_wala_ui.py (the review player), pehle_wala_faces.py (JD tile, face-compositor),
pehle_wala_sfx.py (cues, sound-designer; needs the shared sound kit epic_sfx / epic_music / epic_mix).

SHOT LIST (as built; camera locked all reel long: the frame under review does all the moving)
| shot   | f (s)                | bar.beat | picture                                                         | transition out | SFX anchor (pehle_wala_sfx) |
| S1-01  | 0-79 (0-2.633)       | 0.0-1.1  | v1 ad, "Approved", v1; pin 1's marker mid-glide (618, 443) on  | splice f80     | impact_soft f0, thock f8,   |
|        |                      |          | f0, falls f5-f8 onto the logo; chip flips f12; lockup BAS EK / |                | ui_click f12, pop f32       |
|        |                      |          | *chhota sa* / CHANGE (t0 -0.1, exit 2.233-2.583); v2 f32, v3 f64|                |                             |
| S2-01  | 80-383 (2.67-12.77)  | 1.1-5.3  | v4 left f96, v5 pop + NEW f128/130 (L3 0.5), v6 cream f192-204, | D7 f384        | thock + slot_tick per pin   |
|        |                      |          | v7 steam outline f224, v8 shake f256, v9 sparkles f288, v10    |                |                             |
|        |                      |          | parody f320, v11 shadows f352                                  |                |                             |
| S3-01  | 384-447 (12.8-14.9)  | 6.0-6.3  | RE-HOOK: Owner ki Mummy's thread (4 cards f384/400/416/432),    | L3 f448 (0.6)  | glitch + whip (D7), Mummy   |
|        |                      |          | glitter, dark returns f400-412, glitter x2, logo x3.75          |                | thocks                      |
| S4-01  | 448-511 (14.9-17.0)  | 7.0-7.3  | v16 letterbox + flares + slow steam, JD tile (sunglasses),      | L3 f512 (0.4)  | braam f448                  |
|        |                      |          | v17 50% OFF SLAM f480, v18 steam x3 f496                        |                |                             |
| S4-02  | 512-703 (17.07-23.4) | 8.0-10.3 | v19 everything x1.2 f512, v20 CALL NOW f544, v21 NEW! + clock   | D7 f640 inside | barrage, clock ticks,       |
|        |                      |          | f576, v22 f592, v23/24 shadows f608/624, v25 shake 8 px f640,   |                | shepard riser               |
|        |                      |          | drawer f656 (v24-v26) + v27 row f672, drawer/clock exit f696    |                |                             |
| S5-01  | 704-767 (23.47-25.57)| 11.0-11.3| the last marker hovers undecided; freezes f752 (drop-out)       | L3 f768 (1.0)  | hover, heartbeat, silence   |
| S5-02  | 768-783 (25.6-26.1)  | 12.0     | PAYOFF: swoop f764-768, "Pehle wala hi theek tha." (56 px)      | D9 press f784  | pin_thock_big, sub_drop     |
| S5-03  | 784-831 (26.13-27.7) | 12.1-12.3| Ctrl+Z x26 chip f784; W_core(tau) rewinds v27 -> v2 (desat,     | D9 cut f832    | typing, tape rewind, ticks  |
|        |                      |          | zoom smear), counter spins down                                 | (push 0.6)     |                             |
| S6-01  | 832-895 (27.73-29.83)| 13.0-13.3| RESTORE = P(t) = W_core(t - DUR): v1, Approved; *pehle wala* /  | end card layer | impact_soft, glass_tap      |
|        |                      |          | HI THEEK THA; JD tile (smirk) f836-895; garam dims to x0.35     |                |                             |
| S6-02  | 896-1023 (29.87-34.1)| 14.0-15.3| END CARD US CLIENT KO / *bhejo* + JD ring + @jawad_mp4 over the | loop seam      | card cues, ui_hover 32.633, |
|        |                      |          | dimmed v1 world; pin 1's marker re-enters f979, hovers, glides  | -> f0          | reverse swell into f0       |
|        |                      |          | during the card exit (656, 465) on f1023 -> (618, 443) on f0    |                |                             |

Contract: DUR / LOOK / BPM, assets(), prewarm(), pure draw(t), post(cv, t) -> G.tx_finish (exposure pushes, D7, pin
ticks, loop push), samples(t), cues() -> pehle_wala_sfx.cues() (imported lazily: the shared sound kit may be absent).
Env: PW_CAPTIONS=0 skips the captions (cover render, hook-B splice checks).
Render ladder (always through tools/heavy.sh, --workers 1, --no-sfx-build --audio <mix> or --no-audio):
    python3 render.py pehle_wala --sheet 16 --samples 1 --workers 1 --no-audio
    python3 render.py pehle_wala --stills 0,0.267,0.533,2.133,... --workers 1 --no-audio
    python3 render.py pehle_wala --range 25.2 28.2 --workers 1 --no-audio

BUILD STATUS (2026-10-09, measured): 53 full-quality beat stills (every row of HANDOFF 2), a 32-frame sheet and the
15 fps preview (VO stem only: no mix exists yet, the shared sound kit is being rebuilt) checked frame by frame.
Cost: 1 sample 0.88 s/frame mean (p90 1.03 s), full samples (3-7) ~2 s/frame, prewarm ~20 s, worker peak 2.3 GB.
f0 luma 38.7 (full range), f0 -> f1 mean abs diff 8.2; loop seam 3.7 vs step 8.2 (E.seam_report ok); pre1 path on the
BRIEF 6.3.1 numbers (f1023 (656, 465), f0 (618, 443)). Known: the p1 luma of the L3 push frames rises 1.9-3.2 code
values (f768, push 1.0: 6.3) over the previous frame (the shared X.finish push, kept as specified); card hand-overs
overlap the outgoing and incoming card for ~4 frames (BRIEF 6.3 collapse / POP timings, kept); hook B
(pehle_wala_hookb.py) not built (LEAD_DECISIONS 6: bonus after version A).
"""
import functools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                   # noqa: F401,E402  FIRST
from jawad_kit import K, T, J                      # noqa: E402
import jawad_grade as G                           # noqa: E402  registers 'inferno'
import jawad_tx as X                               # noqa: E402
import endcard as E                                # noqa: E402
import profile_outro as PO                         # noqa: E402
import snake_captions as SC                        # noqa: E402
import pehle_wala_faces as PF                      # noqa: E402
import pehle_wala_state as S                       # noqa: E402
import pehle_wala_ad as AD                         # noqa: E402
import pehle_wala_ui as UI                         # noqa: E402

import cv2                                         # noqa: E402
import numpy as np                                 # noqa: E402

DUR = 1024 / 30.0
LOOK = 'inferno'
BPM = 112.5
BEAT = 60.0 / BPM
FPS = K.FPS
HALF = 0.5 / FPS
RW = '/home/user/100/workspace/jawad_reels/pehle_wala'
VO_A = os.path.join(RW, 'vo', 'pehle_wala_vo_A.words.json')
T_CARD = 896 / 30.0                                # 29.8667: end card t0
T_RESTORE = 832 / 30.0                             # 27.7333: D9 cut (v1 restored)
T_SPLICE = 80 / 30.0                               # hook A == hook B from here
CAPTIONS = os.environ.get('PW_CAPTIONS', '1') != '0'

GR = X.Grid(112.5)
PLAN = X.Plan([('L3', GR.at(2), dict(push_gain=0.5)), ('D7', GR.at(6)), ('L3', GR.at(7), dict(push_gain=0.6)),
               ('L3', GR.at(8), dict(push_gain=0.4)), ('D7', GR.at(10)), ('L3', GR.at(12), dict(push_gain=1.0)),
               ('D9', GR.at(13), dict(pre=48, post=2, press=6, R=GR.at(12, 1), keys_y=-2000.0))])
TICKS = [f / 30.0 - 0.02 for f in S.landings_tick()]


# ============================================================================================ local lockup helpers
class KeyFirstTitle:
    """Keyword first, caps under the underline (SHARED_REQUESTS #2): jw_key_core glyph rise + jw_key_halo +
    J.underline + a jw_caps line (the payoff `*pehle wala* / HI THEEK THA`)."""

    def __init__(self, key, caps, key_px=210, caps_px=86, ul_len=918):
        self.key_txt = key
        self.glyphs = T.Glyphs(key, 'jw_key_core', px=key_px)
        self.static = T.render(key, 'jw_key_core', px=key_px)
        self.halo = T.render(key, 'jw_key_halo', px=key_px)
        self.caps = T.render(caps, 'jw_caps', px=caps_px)
        self.ul_len = ul_len
        self.ul = J.underline(ul_len, thick=max(4.0, key_px * 0.026))

    def draw(self, cv, t, xk, yk, y_ul, y_caps, t_key, t_caps, t_ul, op=1.0, caps_dur=0.6, ul_dur=0.5):
        if op <= 1e-3:
            return
        if t >= t_key:
            hk = K.ramp(t, t_key, t_key + 0.5 + 0.03 * len(self.key_txt), 'inout_sine')
            self.halo.draw(cv, xk, yk, opacity=op * hk)
            if t - t_key < 1.2 or op < 1:
                self.glyphs.rise(cv, t, xk, yk, t0=t_key, stagger=0.025, dur=0.5, dist=0.3, blur=7, scale0=0.94,
                                 opacity=op)
            else:
                self.static.draw(cv, xk, yk, opacity=op)
        uc = K.ramp(t, t_caps, t_caps + caps_dur, 'out_cubic')
        if t >= t_caps:
            self.caps.draw(cv, xk, y_caps + 28 * (1 - uc), opacity=op * K.ramp(t, t_caps, t_caps + caps_dur * 0.7,
                                                                                 'inout_sine'), blur=6 * (1 - uc))

        def uu(tt):
            return K.ramp(tt, t_ul, t_ul + ul_dur, 'inout_cubic')
        u = uu(t)
        if u > 0:
            speed = (uu(t + 0.004) - uu(t - 0.004)) / 0.008 * self.ul_len
            self.ul.draw(cv, xk - self.ul_len / 2, y_ul, u=u, opacity=op, smear=speed * 0.25 / FPS)


@functools.lru_cache(maxsize=4)
def scrim_mask(cx, cy, rx, ry, sigma=60):
    """Feathered ellipse (region-local float32) + its top-left: a multiplicative dim behind a lockup."""
    pad = int(3 * sigma)
    x0, y0 = max(0, cx - rx - pad), max(0, cy - ry - pad)
    x1, y1 = min(K.W, cx + rx + pad), min(K.H, cy + ry + pad)
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    cv2.ellipse(m, (cx - x0, cy - y0), (rx, ry), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), sigma)
    m.flags.writeable = False
    return x0, y0, m


def dim_scrim(cv, key, k):
    if k <= 1e-3:
        return
    x0, y0, m = scrim_mask(*key)
    reg = cv[y0:y0 + m.shape[0], x0:x0 + m.shape[1], :3]
    reg *= (1.0 - np.float32(k) * m)[..., None]


@functools.lru_cache(maxsize=1)
def player_mask():
    """Soft rounded-rect mask of the player body (x 80-1000, y 236-1268), for the dim under the end card."""
    pad = 24
    a = K.rrect_alpha(920, 1032, 44, pad)
    a = cv2.GaussianBlur(a, (0, 0), 6)
    a.flags.writeable = False
    return 80 - pad, 236 - pad, a


def player_dim(cv, t):
    """Local extra dim on the player under the end card (SHARED_REQUESTS #4): k = 0.65 x card envelope."""
    u = t - T_CARD
    if u <= 0:
        return
    k = 0.65 * K.ramp(u, 0.0, 0.5, 'inout_sine') * (1.0 - card_exit(t))
    if k <= 1e-3:
        return
    x0, y0, m = player_mask()
    reg = cv[y0:y0 + m.shape[0], x0:x0 + m.shape[1], :3]
    reg *= (1.0 - np.float32(k) * m)[..., None]


def card_exit(t):
    return K.ramp(t, T_CARD + 4.2667 - 0.36, DUR - 1.0 / FPS, 'in_cubic')


def garam_dim(t):
    """The ad keyword's focus dim in P(t) (BRIEF 6.2 AD2): 1 -> 0.35 over 27.733-28.233, back with the card exit."""
    return 1.0 - 0.65 * K.ramp(t, 27.7333, 28.2333, 'inout_sine') * (1.0 - card_exit(t))


# ============================================================================================ assets
def cap_avoid(t):
    r = [(80, 236, 1000, 1268)]                    # the player: pins, ad, UI
    a = PF.avoid_rect(t)
    if a:
        r.append(a)
    if 26.1 <= t < 27.95:
        r.append((335, 1340, 745, 1436))          # the Ctrl+Z chip (no VO then anyway)
    return r


@functools.lru_cache(maxsize=1)
def assets():
    return dict(
        embers=J.embers(60, seed=26, bright=0.8), cam=K.Cam(aperture=24),
        hook=J.HouseTitle('BAS EK', 'chhota sa', caps_px=86, key_px=200),
        change=T.render('CHANGE', 'jw_caps', px=86),
        payoff=KeyFirstTitle('pehle wala', 'HI THEEK THA', key_px=210, caps_px=86, ul_len=918),
        card=PO.ProfileOutro("Tumhare client ka 'chhota sa change' kya tha?", key='Comment mein batao',
                             dur=4.2667),                    # Jawad 10-09: Genjutsu-style profile outro
        cap=SC.Captions(VO_A, band='lower', y=1400, avoid=cap_avoid, hide=[(0.0, 2.6667), (T_CARD + 1.2, DUR)], clear=[(21.8667, 23.40)]))


def prewarm():
    A = assets()
    AD.prewarm()
    UI.prewarm()
    PF.prewarm()
    A['cap'].prewarm()
    A['card']._settled_layer()
    scrim_mask(540, 860, 520, 330)
    scrim_mask(540, 740, 500, 230)
    player_mask()


# ============================================================================================ scenes
def W_core(s, a=None, garam_k=1.0, sv=1.0):
    """The world at state time s (ambient a, default s): void + embers, the review player, the ad, pins, chips,
    counter, drawer. No faces, no lockups, no captions, no Ctrl+Z chip, never pre1. sv = ds/dt (counter blur)."""
    a = s if a is None else a
    st = S.state(s)
    A = assets()
    cv = K.background(LOOK, a, bokeh=1.0)
    A['embers'].draw(cv, A['cam'], a)
    dx, dy = st['shake']
    UI.draw_window(cv, dx, dy)
    ad = AD.canvas(st, a, garam_k)
    ad *= AD.round_mask()[..., None]
    K.draw(cv, ad, AD.AD_X + dx, AD.AD_Y + dy, anchor=(0, 0))
    cvel = (S.counter_value(s + 1e-3) - S.counter_value(s - 1e-3)) / 2e-3 * sv
    UI.draw_ui(cv, st, dx, dy, counter_vel=cvel)
    return cv


def hook_overlay(cv, t):
    """Hook A lockup (BRIEF 6.1 HA1-HA3): scrim + BAS EK / *chhota sa* (J.HouseTitle t0 -0.1) + CHANGE."""
    A = assets()
    out = 1.0 - K.ramp(t, 2.2333, 2.5833, 'in_cubic')
    if out <= 0:
        return
    dim_scrim(cv, (540, 860, 520, 330), 0.6 * K.ramp(t, -0.1, 0.4, 'inout_sine') * out)
    A['hook'].draw(cv, t, 540, 820, t0=-0.1, out_t0=2.2333)
    if t >= 0.25:
        uc = K.ramp(t, 0.25, 0.85, 'out_cubic')
        A['change'].draw(cv, 540, 1028 + 28 * (1 - uc), opacity=out * K.ramp(t, 0.25, 0.67, 'inout_sine'),
                         blur=6 * (1 - uc))


def draw_pre1(cv, s):
    p = S.pre1(s)
    if p is not None:
        UI.marker(cv, (p[0], p[1] + S.DISC_UP), 'C', p[2])


def W(t):
    """Hook A head + body: W_core(t) + the hook lockup (t < 2.667) + pin 1's loop-tail marker on top (t < 5/30)."""
    cv = W_core(t)
    if t < T_SPLICE:
        hook_overlay(cv, t)
    if t < S.S_PIN1:
        draw_pre1(cv, t)
    return cv


def _rewind_sv(x):
    """ds/dt of the D9 rewind source at state x (tau = 26.3333 - 26.1333 in_cubic(u), u over 1.4 s)."""
    if x >= 25.0:
        return 1.0
    u = ((26.3333 - x) / 26.1333) ** (1.0 / 3.0)
    return -3.0 * 26.1333 * u * u / 1.4


def W_rew(x):
    """Scene 6: the live payoff world, then the D9 rewind source (jawad_tx calls it with tau)."""
    return W_core(x, sv=_rewind_sv(x))


def payoff_lockup(cv, t):
    """*pehle wala* / HI THEEK THA (BRIEF 6.1 PO1 / PO2): key rises per glyph from f832, caps 27.833-28.433,
    underline 27.983-28.483 at y 821, exit f886-f896 (in_cubic); scrim (540, 740) x (500, 230) x0.55."""
    if t < T_RESTORE - HALF or t >= T_CARD:
        return
    A = assets()
    out = 1.0 - K.ramp(t, 886 / 30.0, 896 / 30.0 - HALF, 'in_cubic')
    dim_scrim(cv, (540, 740, 500, 230), 0.55 * K.ramp(t, T_RESTORE - HALF, T_RESTORE + 0.3, 'inout_sine') * out)
    A['payoff'].draw(cv, t, 540, 670, 821, 891, t_key=T_RESTORE - HALF, t_caps=27.8333, t_ul=27.9833, op=out)


def P(t):
    """Restore + end card: W_core(t - DUR) (frame 0's past) + player dim + payoff lockup + end card + pre1 on top."""
    s = t - DUR
    cv = W_core(s, garam_k=garam_dim(t))
    player_dim(cv, t)
    payoff_lockup(cv, t)
    assets()['card'].draw(cv, t, T_CARD)
    draw_pre1(cv, s)
    return cv


SCENES = [W, W, W, W, W, W, W_rew, P]


def plan_draw(t, scenes=SCENES, plan=PLAN):
    """PLAN.draw with the hard-cut transitions (L3, D7: their work is in post) drawn here as the plain cut (cut rule,
    windows, samples and post_kw unchanged): jawad_tx's Tx.__call__ hands the step options (push_gain) to _tx_cut,
    which takes none -> TypeError on the 4 frames after every L3 cut (SHARED_REQUESTS #13)."""
    for i, (x, c, o) in enumerate(plan.steps):
        if not x.win(c, **o).inside(t):
            continue
        if x.fn is X._tx_cut:
            return (scenes[i + 1] if X.side_b(t, c) else scenes[i])(t)
        return x(t, c, scenes[i], scenes[i + 1], **o)
    return scenes[plan.segment(t)](t)


# ============================================================================================ contract
def draw(t):
    cv = plan_draw(t)
    UI.draw_ctrlz(cv, t)
    PF.draw_tile(cv, t)
    if CAPTIONS:
        assets()['cap'].draw(cv, t, opacity=1.0 - K.ramp(t, 33.7733, 34.1, 'in_cubic'))
    return cv


def pin_tick(t):
    return 0.25 * sum(K.impulse(t, c, 20.0) for c in TICKS if -0.05 < t - c < 0.5)


def post(cv, t):
    kw = PLAN.post_kw(t)
    push = kw.pop('push', 0.0) + assets()['card'].post_kw(t, T_CARD, DUR).get('push', 0.0)
    rgb = kw.pop('rgb_split', 0.0) + pin_tick(t)
    return G.tx_finish(cv, t, LOOK, cuts=[(0.0, 0.6)], push=push, rgb_split=rgb, **kw)


SLAM_FRAMES = {130, 131, 480, 481, 544, 545, 576, 577}


def samples(t):
    n = PLAN.samples(t)
    f = int(round(t * FPS))
    if f in SLAM_FRAMES or f <= 8 or t >= 33.8 - 1e-6:
        n = max(n, 5)
    if 764 <= f <= 768:
        n = max(n, 7)                              # the payoff swoop (up to ~90 px / frame)
    return n


def cues():
    """The sound-designer's cue sheet (never drafted here). Imported lazily so the picture renders without the kit."""
    import pehle_wala_sfx
    return pehle_wala_sfx.cues()


def __getattr__(name):
    """BED / BED_GAIN_DB from the sound-designer's module; an AttributeError (not an ImportError) while the shared
    sound kit (epic_sfx / epic_music / epic_mix) is being rebuilt, so hasattr / getattr(..., default) keep working."""
    if name in ('BED', 'BED_GAIN_DB'):
        try:
            import pehle_wala_sfx
        except ImportError as e:
            raise AttributeError('%s: pehle_wala_sfx not importable (%s)' % (name, e)) from None
        return getattr(pehle_wala_sfx, name)
    raise AttributeError(name)
