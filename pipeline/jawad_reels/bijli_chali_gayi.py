"""bijli_chali_gayi.py - reel 2, C11 "Bijli Chali Gayi" (34.667 s = 1040 f, 90 BPM, look dusk). @jawad_mp4.

Sources (binding order): brand_reels/design/reels/bijli_chali_gayi/HANDOFF.md r3 > BRIEF.md r2 (sections 6.1-6.9, 7) >
packet.yaml; LEAD_DECISIONS.md over all. Worlds live in bijli_chali_gayi_world.py (BW), faces in
bijli_chali_gayi_faces.py (BF, face-compositor). Grid: 90 BPM, beat 20 f, bar 80 f; f = frame, t = f / 30.
Env: JAWAD_C11_HOOK=A|B (hook B renders f0-f79 only, spliced at f80), JAWAD_C11_COVER=1 (H1 at 1.0 for the cover still).

SHOT LIST (as built)
| shot | f (s)                 | picture                                                         | camera                       | out / tx            | SFX (sound-designer stem) |
| S1A  | 0-79 (0-2.63)         | lit room: fan 4.5 rev/s, bold CRT edit, tube; brownout f10-f13, | locked f0-f19, drift from    | splice f80 (glue,   | impact_soft f0, relay /   |
|      |                       | mains 0 f14 (8 px CRT line), dot f15; torch f20 -> box f24-f38; | f20 (0 -> 1 over 15 f)       | push 0.5)           | crt_off f12-f14, beeps    |
|      |                       | LED f40/44/60/64; H1 Bijli f15 (0.35 -> 0.70, torch 1.0, 0.75), |                              |                     | f40/44/60/64              |
|      |                       | H2 CHALI GAYI. f18; exit f72-f79                                |                              |                     |                           |
| S1B  | 0-79 (hook B)         | torch-lit room, LED f0/4/40/44, beam box -> CRT f30-f70;        | drift                        | splice f80          | beeps f0/4/40/44          |
|      |                       | YEH / awaaz (t0 -0.1, out 2.267), YAAD HAI? (t0 1.25)          |                              |                     |                           |
| S2   | 80-159 (2.67-5.30)    | match f80, wick f86, pankhi on f100/f120/f140, homework copy;   | drift; tilt +900 px in_cubic | glue f160 push .25  | match_strike f80, rustle  |
|      |                       | tilt up through the ceiling f140-f159 (dead fan rim-lit)        | f140-f159 (+ smear)          |                     |                           |
| S3   | 160-319 (5.33-10.63)  | rooftops (haze band, pools, rims); far window f220-f221; child  | settle -300 -> 0 f160-f180;  | L7 f308-f331        | hum blip f220, thunk f240 |
|      |                       | head turn f224-f230; bulbs f240-f245 + AA GAYI! slam f240;      | drift; LOCKED f240-f299;     | (crosses x 540 f320)| cheer, thunk f300         |
|      |                       | all dies f300-f302, AA GAYI! darken flicker f300-f305           | drift from f300              |                     |                           |
| S4   | 320-399 (10.67-13.30) | old room by torch: copy by f340, sweep to the CRT f351-f366,    | drift + push 1.00 -> 1.04    | glue f400 push 0.8  | beep f380                 |
|      |                       | hold; LED f380/f384                                             |                              |                     |                           |
| S5   | 400-559 (13.33-18.63) | glass monitor: same edit (playhead parked) + 9:16 rooftop       | locked; drift from f480      | L8 f551-f570        | thunk f480, crt_off,      |
|      |                       | viewer; RENDERING 63 % -> 64 % f440; brownout f470; dies f480,  |                              | (closed f560 only)  | HUD ticks f486-f520       |
|      |                       | collapse f480-f485, drain f486-f520 (RED < 20), 0 % pulsing     |                              |                     |                           |
| S6   | 560-719 (18.67-23.97) | Ctrl + S keycaps: presses f580/600/620, 8ths f640-f710 (Ctrl    | locked                       | glue f720 push 0.3  | thocks, ui_tick at p+2    |
|      |                       | 1 f before S), Saved chips at p+2, U3F 'Saved . har 30 sec' f712|                              |                     |                           |
| S7a  | 720-739 (24.0-24.63)  | candle macro, flame leans and recovers                          | drift x0.5                   | glue f740 push 0.2  | impact_soft lp 900        |
| S7b  | 740-839 (24.67-27.97) | JD profile by candlelight (BF), sparks; payoff lockup f800      | BF.cam_s7b (4 px / 0.3 deg)  | hard cut f840       | drop-out f790-f799,       |
|      |                       | (BIJLI NE SIKHAYA / sabr, out_t0 28.95)                         |                              |                     | harmonium peak f820       |
| S7c  | 840-879 (28.0-29.30)  | candle macro under the lockup                                   | drift x0.5                   | L4 f870-f889        | riser into f880           |
| S8a  | 880-919 (29.33-30.63) | power returns: JD smiling over the lit room plate (tube strike  | locked                       | glue f920 push 0.3  | appliance chorus          |
|      |                       | f882, CRT on f883, fan spins up)                                |                              |                     |                           |
| S8b  | 920-1039 (30.67-34.63)| the frame-0 lit room on the t - DUR clock + end card            | locked                       | loop seam -> f0     | reverse_swell into f0     |

Contract: DUR / LOOK / BPM, assets(), prewarm(), pure draw(t), post(cv, t) -> G.tx_finish, samples(t), cues() = []
(BED None: the sound-designer's stem / the mix-stage file is muxed with --audio; render with --no-sfx-build).
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
import jawad_grade as G                            # noqa: E402
import jawad_tx as X                               # noqa: E402
import endcard as E                                # noqa: E402
import snake_captions as SC                        # noqa: E402
import bijli_chali_gayi_faces as BF                # noqa: E402
import bijli_chali_gayi_world as BW                # noqa: E402

DUR, LOOK, BPM = 1040 / 30, 'dusk', 90
BEAT = 60.0 / BPM
FPS = K.FPS
HALF = 0.5 / FPS
RWS = BW.RWS
HOOK = os.environ.get('JAWAD_C11_HOOK', 'A').strip().upper()
COVER = os.environ.get('JAWAD_C11_COVER', '') == '1'
NOTEXT = os.environ.get('JAWAD_C11_NOTEXT', '') == '1'
BED, BED_GAIN_DB = None, None
T_END = 920 / 30                     # literal frame 920 (SHARED_REQUESTS #2: DUR - card.dur rounds off)


def F(f):
    return f / FPS


def ease(name, u):
    return K.EASE[name](min(1.0, max(0.0, u)))


PLAN = X.Plan([
    ('L7', 320 / 30, dict(src=(540, -900), a0=-40, a1=40, width=2.2, haze=0.45, rays=0.0)),   # f308-f331
    ('L8', 560 / 30, dict(n=7, black=0)),                                                      # f551-f570
    ('L4', 880 / 30),                                                                          # f870-f889
])
CUTS = [(0.0, 0.6), (80 / 30, 0.5), (160 / 30, 0.25), (240 / 30, 0.5), (400 / 30, 0.8), (720 / 30, 0.3),
        (740 / 30, 0.2), (920 / 30, 0.3)]


# ================================================================================================ worlds
def side(t, f):
    return X.side_b(t, F(f))


def WORLD_A(t):
    """Hook (A or B) + S2 + S3 (valid to the end of the L7 window, f331)."""
    if not side(t, 80):
        return BW.room(t, 'B' if HOOK == 'B' else 'A')
    if not side(t, 160):
        return BW.s2(t)
    return BW.s3(t)


def WORLD_B(t):
    """S4 (from the L7 window, f308) + S5 (to the L8 window end)."""
    if not side(t, 400):
        return BW.room(t, 'S4')
    return BW.s5(t)


def WORLD_C(t):
    """S6 keycaps + S7a macro + S7b JD profile + S7c macro."""
    if not side(t, 720):
        return BW.s6(t)
    if not side(t, 740):
        return BW.s7_macro(t, lean=True)
    if not side(t, 840):
        return BW.s7b(t)
    return BW.s7_macro(t)


def WORLD_D(t):
    """S8a (power returns, JD smiling) + S8b (the frame-0 lit room on the t - DUR clock)."""
    if not side(t, 920):
        return BW.s8a(t)
    return BW.room(t - DUR, 'lit')


def world(t):
    if t < -HALF:
        return BW.room(t, 'lit')                     # the loop tail: frame 0's past (lit room, both versions)
    if t < 0:
        return WORLD_A(t)                            # frame 0's own shutter (B: never blur across the seam cut)
    return PLAN.draw(t, [WORLD_A, WORLD_B, WORLD_C, WORLD_D])


# ================================================================================================ type
@functools.lru_cache(maxsize=1)
def assets():
    card = E.EndCard('COMMENT MEIN', 'batao', sub='Chhat ya candle?', monogram='JD', dur=4.0,
                     y_mono=360.0, y_key=730.0, y_sub=965.0, y_sig=1575.0)
    return dict(
        h1=T.render('Bijli', 'jw_key', px=250),
        h2=T.render('CHALI GAYI.', 'jw_caps', px=96),
        hb=J.HouseTitle('YEH', 'awaaz', caps_px=96, key_px=240, underline=False),
        hb3=T.render('YAAD HAI?', 'jw_caps', px=96),
        r1g=T.Glyphs('AA GAYI!', 'jw_caps_bold', px=170),
        r1=T.render('AA GAYI!', 'jw_caps_bold', px=170),
        pay=J.HouseTitle('BIJLI NE SIKHAYA', 'sabr', caps_px=86, key_px=260),
        card=card)


def h1_opacity(t):
    """H1 'Bijli' (BRIEF 6.3 / 6.6): glows on at f15 0.35 -> 0.70 by f24 (inout_sine); the torch finds it at f20
    (1.0 by f22, out_cubic), it settles to 0.75 over f30-f38; exit f72-f79 (handled by the caller)."""
    if COVER:
        return 1.0
    if t < F(15) - HALF:
        return 0.0
    o = 0.35 + 0.35 * ease('inout_sine', (t - F(15)) / F(9))
    if t >= F(20):
        o = o + (1.0 - o) * ease('out_cubic', (t - F(20)) / F(2))
        o = o + (0.75 - o) * ease('inout_sine', (t - F(30)) / F(8))
    return o


def rise_line(cv, spr, t, x, y, t0, out_t0, op_dur=0.42, y_dur=0.6, out_dur=0.35):
    """A caps line rising like the house caps (opacity inout_sine op_dur, y +28 -> 0 out_cubic y_dur, blur 6 -> 0),
    exit in_cubic over out_dur (opacity, 8 px up, blur 0 -> 6)."""
    if t < t0:
        return
    ex = ease('in_cubic', (t - out_t0) / out_dur) if out_t0 is not None else 0.0
    if ex >= 1.0:
        return
    uy = ease('out_cubic', (t - t0) / y_dur)
    op = ease('inout_sine', (t - t0) / op_dur) * (1.0 - ex)
    spr.draw(cv, x, y + 28.0 * (1.0 - uy) - 8.0 * ex, opacity=op, blur=6.0 * (1.0 - uy) + 6.0 * ex)


def draw_overlays(cv, t):
    """Designed text in reel time over the worlds (cuts, transitions and the loop tail never touch it)."""
    A = assets()
    if HOOK == 'A' and t < F(80):
        o = h1_opacity(t)
        ex = ease('in_cubic', (t - F(72)) / F(8))             # 8 frames f72-f79 (f79 keeps a lit element)
        if o > 0 and ex < 1.0:
            A['h1'].draw(cv, 540.0, 520.0 - 8.0 * ex, opacity=o * (1.0 - ex), blur=6.0 * ex)
        if t >= F(18) - HALF:
            ex2 = ex
            if ex2 < 1.0:
                uy = ease('out_cubic', (t - F(18)) / F(18))
                op = ease('inout_sine', (t - F(18) + HALF) / F(13))
                A['h2'].draw(cv, 540.0, 720.0 + 28.0 * (1.0 - uy) - 8.0 * ex2, opacity=op * (1.0 - ex2),
                             blur=6.0 * (1.0 - uy) + 6.0 * ex2)
    if HOOK == 'B' and t < F(80):
        A['hb'].draw(cv, t, 540.0, 520.0, t0=-0.1, out_t0=2.267)
        rise_line(cv, A['hb3'], t, 540.0, 700.0, 1.25, 2.267)
    if F(240) - HALF <= t < F(306):
        f = BW.fi(t)
        if t < 8.6:
            A['r1g'].slam(cv, t, 540.0, 620.0, t0=8.0 - HALF, fade=0, s0=1.14, dur=0.25, smear=False)  # f240 x1.125: ink x 72-1008
        else:
            op = {300: 0.35, 301: 0.80, 302: 0.15, 303: 0.45, 304: 0.05}.get(f, 1.0 if f < 300 else 0.0)
            if op > 0:
                A['r1'].draw(cv, 540.0, 620.0, opacity=op)
    if F(800) - HALF <= t < 28.95 + 0.36:
        A['pay'].draw(cv, t, 540.0, 520.0, t0=26.667, out_t0=28.95)


# ================================================================================================ captions
def avoid_at(t):
    """HANDOFF 6 avoid rects (x0, y0, x1, y1) per shot; S7b adds JD's rect (incl. his back hair)."""
    r = []
    if 80 / 30 <= t < 160 / 30:
        r += [(60, 1150, 1020, 1660), (440, 780, 640, 1020)]
    elif 160 / 30 <= t < 8.0:
        r += [(290, 995, 370, 1085), (650, 1280, 870, 1430)]
    elif 320 / 30 <= t < 400 / 30:
        r += [(250, 1010, 690, 1380)]
    elif 400 / 30 <= t < 560 / 30:
        r += [(100, 440, 980, 960), (110, 990, 920, 1110)]
    elif 560 / 30 <= t < 720 / 30:
        r += [(165, 900, 495, 1200), (585, 720, 855, 990), (600, 380, 960, 720)]
    elif 720 / 30 <= t < 740 / 30:
        r += [(380, 600, 700, 1300), (450, 1290, 630, 1920)]       # S7a flame + the macro candle's body below it
    elif 740 / 30 <= t < 840 / 30:
        r += [(700, 1040, 900, 1560)]
        h = BF.jd_rect(t)
        if h:
            r.append(tuple(h))
    return r


@functools.lru_cache(maxsize=2)
def captions(hook='A'):
    words = RWS + '/vo/bijli_chali_gayi_vo_%s.words.json' % hook
    return SC.Captions(words, band='auto', avoid=avoid_at, white_px=64, key_px=128,
                       hide=[(0.0, 80 / 30), (800 / 30, 880 / 30), (920 / 30, DUR)],
                       clear=[(7.94, 8.6), (26.27, 26.667)])          # gone 2 f before the slam f240 / drop-out f790


# ================================================================================================ contract
def draw(t):
    cv = E.loop_world(world, t, DUR, d=0.6)
    if NOTEXT:
        return cv
    draw_overlays(cv, t)
    captions(HOOK).draw(cv, t)
    assets()['card'].draw(cv, t, T_END)
    return cv


def post(cv, t):
    kw = dict(PLAN.post_kw(t))
    kw['push'] = kw.get('push', 0.0) + assets()['card'].post_kw(t, T_END, DUR).get('push', 0.0)
    return G.tx_finish(cv, t, LOOK, cuts=CUTS, **kw)


def samples(t):
    return max(PLAN.samples(t), BW.nsamp(t))


def cues():
    return []                         # the sound-designer's stem / the mix stage carries every sound (HANDOFF 5)


def prewarm():
    BW.prewarm()
    A = assets()
    A['card']._settled_layer()
    captions(HOOK).prewarm()
