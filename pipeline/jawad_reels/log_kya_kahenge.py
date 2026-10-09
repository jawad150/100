"""log_kya_kahenge.py - reel 5, C15 "Log Kya Kahenge" (the cardboard stadium), 35.2 s, 75 BPM, look noir_ember.

Sources: brand_reels/design/reels/log_kya_kahenge/HANDOFF.md (r3, binding), BRIEF.md r2 (geometry, strings, contract),
FACES.md (LF API), SOUND.md (cues() stays []). Grid: X.Grid(75): beat 24 f, bar 96 f = 3.2 s; f = frame, t = f / 30.

SHOT LIST (as built)
| shot  | f (s)                    | beat      | picture                                                    | camera                         | out          | SFX (sound-designer stem) |
| S1-01 | 0-95 (0-3.17)            | bar 0     | lit tiers, heads TURNED; head-snap wave f6-f18 (dark hair  | CAM_WIDE 24 mm locked          | continuous   | impact_soft f0, swish f9, |
|       |                          |           | mass -> light face plate + amber eyes, 3 f per head);     |                                |              | whisper swell peak f12,   |
|       |                          |           | lockup LOG KYA / kahenge? (t0 -0.1, out 2.533, gone f87)  |                                |              | shimmer f18               |
| S2-01 | 96-287 (3.2-9.57)        | bars 1-2  | J1 f96 (hold f106), J2 f144 (f152), J3 f180 (f186), J4 f216 | CAM_WIDE locked; crowd leans   | O2 smoke c   | bursts + whoosh_by per    |
|       |                          |           | (f222) fly out of the crowd; lean 1.00 -> 1.03 (in_sine)  | in 1.00 -> 1.03 (cards only)   | f288         | line                      |
| S3-01 | 288-383 (9.6-12.77)      | bar 3     | JD (street_threequarter_turn) small in front of the stands | LF.cam_s3: pedestal 1100 ->    | L3 cut f384  | whoosh_slow 9.6           |
|       |                          |           | (staring), haze behind him, lamp bank enters ~10.8 s      | 1420 mm + tilt -3 -> +3 deg    | push 0.5     |                           |
| S3-02 | 384-479 (12.8-15.97)     | bar 4     | 135 mm rows staring; heads tilt 9 deg f384-f396, back      | CAM_ROWS psi 0 locked          | continuous   | board_flex 12.8; drop-out |
|       |                          |           | f438-f450 (one head 2 f late); drop-out lean 1 -> 1.025    |                                |              | 15.2-16.0                 |
| S4-01 | 480-575 (16.0-19.17)     | bar 5     | REVEAL: rows turn edge-on (lines of light), backs, tape,   | orbit psi 0 -> 70 out_cubic    | continuous   | braam + impact_big 16.0   |
|       |                          |           | struts; the people with phones appear behind each row      | (moving on f480), push 0.8     |              |                           |
| S4-02 | 576-671 (19.2-22.37)     | bar 6     | single image f576-f599; focus pull f600-f624 to the        | CAM_ROWS psi 70 locked         | O6 in shot   | ui_tick 21.6/21.8/22.0    |
|       |                          |           | scroller; one person looks up f640-f646; taps f648/54/60   |                                |              |                           |
| S4-03 | 672-719 (22.4-23.97)     | bar 7     | O6 ember disintegration of the CARD layer only, btt, c f708| locked                         | continuous   | ember crackle, impact     |
| S4-04 | 720-767 (24.0-25.57)     | bar 7     | rows of busy people, amber phones, embers die              | locked                         | L3 cut f768  | reverse swell             |
| S5-01 | 768-863 (25.6-28.77)     | bar 8     | PAYOFF: JD chin-up bust (LF.draw_s5), warm key ignites     | CAM_JD 85 mm plate             | L3 cut f864  | the one clunk f768        |
|       |                          |           | (LF.key_gain); LOG / busy / HAIN. (t0 25.6, out 28.433)    |                                | push 0.4     |                           |
| S6-01 | 864-935 (28.8-31.17)     | bar 9     | emptied stands in warm light, phone dots; the last card    | CAM_WIDE locked                | continuous   | card tap f888             |
|       |                          |           | tips back f876-f888                                        |                                |              |                           |
| S6-02 | 936-1055 (31.2-35.17)    | bars 9-10 | end card US DOST KO / bhejo (settled f992, hold to f1045); | CAM_WIDE locked                | loop seam    | card_slide per flap row   |
|       |                          |           | flaps rise f960-f1011 (heads turned); light hands back to  |                                | -> f0        |                           |
|       |                          |           | the floodlight f1008-f1050; loop_world f1041-f1055         |                                |              |                           |
Hook B (log_kya_kahenge_hookb.py, frames 0-89): S1-01B 135 mm rows, heads turned, snap wave f3-f15, lockup
YEH / log / HAIN KAUN? (out 1.733, gone f63), O2 smoke c f72 to the wide; identical to A from f90.

Deviations from the brief (each one measured; see the hand-back): arc trimmed to +36 deg on the right (the 135 mm side
view would otherwise be filled by the near flank); CAM_ROWS far side darkened by a depth fog that rises with the orbit;
the scroller is the row-3 seat whose phone lands nearest the brief's (600, 1080) at 14-15 m (the brief's row-2 seat sits
at the pivot depth, where a focus pull shows nothing); struts reach 230 mm behind the card (450 mm went through the
people sitting 350 mm behind).

Contract: DUR / LOOK / BPM, assets(), prewarm(), pure draw(t), post(cv, t) -> G.tx_finish, samples(t), cues() = [].
Env: LKK_NOTEXT=1 skips every text overlay (hook lockups, J lines, payoff, end card, captions); LKK_DEBUG=1 appends the
text blocks of every draw to <RW>/qa/text_blocks.log.
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
import jawad_tx as X                               # noqa: E402
import jawad_grade as G                            # noqa: E402
import endcard as E                                # noqa: E402
import snake_captions as SC                        # noqa: E402
import log_kya_kahenge_faces as LF                 # noqa: E402
import log_kya_kahenge_crowd as CR                 # noqa: E402

import cv2                                         # noqa: E402
import numpy as np                                 # noqa: E402

DUR, LOOK, BPM = 35.2, 'noir_ember', 75
GR = X.Grid(75)
FPS = K.FPS
HALF = 0.5 / FPS
RW = '/home/user/100/workspace/jawad_reels/log_kya_kahenge'
NOTEXT = os.environ.get('LKK_NOTEXT', '') == '1'
DEBUG = os.environ.get('LKK_DEBUG', '') == '1'


def fr(n):
    return n / FPS


# ============================================================================================== timeline constants
T_S3, T_ROWS, T_REVEAL, T_ONE, T_O6, T_PAY, T_WIDE, T_CARD = 9.6, 12.8, 16.0, 19.2, 23.6, 25.6, 28.8, 31.2
O6_PRE, O6_POST = 36, 12
CUTS = [(0.0, 0.6), (T_REVEAL, 0.8)]
STEPS = [('O2', T_S3, dict(pre=18, post=18, seed=37, rise=320.0)), ('L3', T_ROWS, dict(push_gain=0.5)),
         ('L3', T_PAY, dict(push_gain=0.6)), ('L3', T_WIDE, dict(push_gain=0.4))]
STEPS_B = [('O2', 2.4, dict(pre=15, post=12, seed=31, rise=260.0))] + STEPS
J_LINES = [('Yeh bhi koi\nkaam hai?', 96, 10, 'c15_judge'), ('Paise milte hain?', 144, 8, 'c15_judge'),
           ('Log hasenge.', 180, 6, 'c15_judge'), ('Naukri kab karoge?', 216, 6, 'c15_judge4')]
J_HOLD = (540.0, 980.0)
J_FROM = (540.0, 905.0)
J_BACK = (540.0, 800.0)
FLAP_LAND = (967, 967, 975, 982, 984, 989, 996, 996, 1004, 1011)       # row i lands upright on this frame (HANDOFF #9)
SUB = "jise 'log' ka darr rokta hai"
WORDS = {'A': RW + '/vo/lkk_vo_A.words.json', 'B': RW + '/vo/lkk_vo_B.words.json'}
HIDE = {'A': ((1.28, 3.0), (31.2, 35.2)), 'B': ((0.0, 2.52), (31.2, 35.2))}
BANK_WIDE = (972.8, 171.5)


# ============================================================================================== assets
@functools.lru_cache(maxsize=1)
def styles():
    j = T.style('jw_body', name='c15_judge', px=84, glow=0.35, glow_color=('EMBER', 0.9), scrim=0.8)
    j4 = T.style('jw_body', name='c15_judge4', px=84, glow=0.5, glow_color=('EMBER', 0.9), scrim=0.8)
    return {'c15_judge': j, 'c15_judge4': j4}


@functools.lru_cache(maxsize=1)
def assets():
    st = styles()
    lines = [T.render(txt, st[sty]) for txt, _, _, sty in J_LINES]
    card = E.EndCard('US DOST KO', 'bhejo', sub=SUB, monogram='JD', dur=4.0)
    card.sub = T.render(SUB, 'jw_body', px=50.0)              # local sub_px override (request R2)
    card._settled = None
    haze = _haze_sprite()
    warm = K.radial(1500, np.asarray(K.C['FLAME'], np.float32) * 0.30, power=1.6)
    dust = K.Particles(150, seed=21, box=((-2500, -5200, 1200), (4200, 300, 4600)), vel=(6, -9, 0), size=(1.5, 4.0),
                       colors=[np.asarray(K.C['ASH'], np.float32) * 0.6, np.asarray(K.C['IVORY'], np.float32) * 0.35],
                       twinkle=0.35, bright=0.45, follow=True, wander=40.0)
    return dict(lines=lines, card=card, haze=haze, warm=warm, dust=dust,
                hookA=J.HouseTitle('LOG KYA', 'kahenge?', caps_px=86, key_px=210, underline=False),
                hookB=J.HouseTitle('YEH', 'log', caps_px=86, key_px=210, underline=False),
                hookB3=T.render('HAIN KAUN?', 'jw_caps', px=86),
                pay=J.HouseTitle('LOG', 'busy', caps_px=86, key_px=210),
                pay3=T.render('HAIN.', 'jw_caps', px=86))


def _haze_sprite():
    """Floodlit haze between JD and the tiers (S3-01): a soft fbm band, emissive (alpha 0), 1080 x 600."""
    n = X.fbm(73, 5.0, 3)
    hz = cv2.resize(np.ascontiguousarray(n, np.float32), (1080, 600), interpolation=cv2.INTER_CUBIC)
    yy = np.linspace(0, 1, 600, dtype=np.float32)[:, None]
    env = np.clip(np.sin(np.pi * yy), 0, None) ** 1.5
    m = np.clip(hz * 1.4 - 0.25, 0, 1) * env
    spr = np.zeros((600, 1080, 4), np.float32)
    spr[..., :3] = m[..., None] * np.asarray(K.C['ASH'], np.float32) * 0.06
    spr.flags.writeable = False
    return spr


@functools.lru_cache(maxsize=2)
def captions(hook='A'):
    return SC.Captions(WORDS[hook], band='lower', avoid=_avoid_fn(hook), hide=HIDE[hook], keep_pairs=(('log', 'kya'),),
                       clear=[(25.6, 25.9)])


def _avoid_fn(hook):
    def avoid(t):
        r = []
        if hook == 'A' and t < 2.9:
            r.append((161, 332, 921, 710))
        if hook == 'B' and t < 2.1:
            r.append((234, 333, 847, 814))
        jr = LF.jd_rect(t)
        if jr is not None:
            r.append(jr)
        if 20.0 <= t < 22.4:
            r.append(CR.scroller_rect(t))
        if 25.6 <= t < 29.7:
            r.append((224, 332, 669, 841))
        if 28.8 <= t < 29.7:
            r.append(LF.jd_rect(28.7667))
        return r
    return avoid


# ============================================================================================== state helpers
def lean_s2(t):
    """S2-01 crowd lean (BRIEF 7.1): 1 + 0.03 in_sine((t - 3.2) / 6.4), 1.030 at 9.6."""
    return 1.0 + 0.03 * K.EASE['in_sine'](K.clamp((t - 3.2) / 6.4))


def lean_rows(t):
    """S3-02 drop-out lean 1.00 -> 1.025 over f456-f479, held through the orbit."""
    return 1.0 + 0.025 * K.EASE['in_sine'](K.clamp((t - fr(456)) / fr(479 - 456)))


def tilt_at(t, late=0):
    """Head tilt 9 deg in sync f384-f396, back f438-f450 (inout_sine); `late` frames later for the one late head."""
    d = late / FPS
    up = K.ramp(t, fr(384) + d, fr(396) + d, 'inout_sine')
    dn = K.ramp(t, fr(438) + d, fr(450) + d, 'inout_sine')
    return 9.0 * (up - dn)


def psi_at(t):
    """S4-01 orbit: yaw 0 -> 70 deg, out_cubic over exactly one bar from 16.0 (moving on the reveal frame)."""
    if t < T_REVEAL:
        return 0.0
    return 70.0 * K.EASE['out_cubic'](K.clamp((t - T_REVEAL) / 3.2))


@functools.lru_cache(maxsize=1)
def scroller_depth():
    _, z = CR.scroller_xy(0.0, 70.0)
    return float(z[0])


def focus_at(t):
    """Focus pull f600-f624 (inout_cubic): the card lines (16 m) -> the scroller."""
    u = K.ramp(t, fr(600), fr(624), 'inout_cubic')
    return K.lerp(16000.0, scroller_depth(), u)


def people_at(t):
    """The real people (and their phones) exist for the camera only from the reveal on."""
    return K.ramp(t, T_REVEAL, T_REVEAL + 0.5, 'inout_sine')


def tap_at(t):
    g = 1.0
    for f in (648, 654, 660):
        g += 0.45 * K.impulse(t, fr(f), decay=22.0)
    return g


def lookup_at(t):
    f = t * FPS
    return 1.0 if 640 <= f < 646 else 0.0


def flap_angles(t):
    """Per-row card angle in S6 (deg): -90 flat on its back -> 0 upright over the 7 frames before the row's landing
    frame (in_cubic: the card speeds up into place), nothing after (no bounce)."""
    out = np.empty(CR.NROWS, np.float64)
    for i, L in enumerate(FLAP_LAND):
        u = K.clamp((t - fr(L - 7)) / fr(7))
        out[i] = -90.0 * (1.0 - u ** 3)
    return out


def last_tip(t):
    """The last card tips over backward f876-f888 (in_cubic, it falls), flat from f888 (the tap)."""
    u = K.clamp((t - fr(876)) / fr(12))
    return -90.0 * u ** 3


def light_handback(t):
    """S6: warm (1) until f1008, back to the floodlight (0) by f1050."""
    return 1.0 - K.ramp(t, fr(1008), fr(1050), 'inout_sine')


def people_s6(t):
    return 1.0 - K.ramp(t, fr(1011), fr(1041), 'inout_sine')


# ============================================================================================== world builders
def _wide_world(cam, t, st, bank=1.0, light=0.0, warm_key=0.0, dust=1.0):
    cv = CR.backdrop(cam, t, bank=bank, light=light, warm_key=warm_key)
    CR.floor(cv, cam)
    lay = CR.render(cam, t, st, 'flood')
    CR.over(cv, lay)
    if light > 0:
        A = assets()
        K.draw(cv, A['warm'], -140.0, 1150.0, opacity=0.8 * light * max(st.light_gain, 0.0), mode='add')
    if dust > 0:
        assets()['dust'].draw(cv, cam, t, opacity=dust)
    return cv


def S_A_state(t, hook):
    """Hook / judgement crowd state. t < 0 (the loop tail) = frame 0's past: heads turned, lean 1."""
    if t < 0:
        return CR.State(head=0.0, lean=1.0, t=t)
    if hook == 'A' and t < 1.5:
        w, j = CR.snap_state(t, 'wide', 0.2, 0.4)
        return CR.State(head=w, jolt=j, lean=1.0, t=t)
    return CR.State(head=1.0, lean=lean_s2(t), t=t)


def S_A(t, hook='A'):
    """S1-01 + S2-01: the lit wide; the judgement lines live in this world (the O2 smoke carries J4 away)."""
    cam = CR.cam_wide()
    cv = _wide_world(cam, t, S_A_state(t, hook))
    if not NOTEXT and t >= 3.0:
        draw_judgements(cv, t)
    return cv


def S_HB(t):
    """S1-01B (hook B): the 135 mm rows at psi 0, heads turned on f0, snap wave f3-f15 (t_s = 0.1 + 0.3 |x-540|/540)."""
    cam = CR.cam_rows(0.0)
    if t < 0:
        st = CR.State(head=0.0, t=t, walls=0)
    else:
        w, j = CR.snap_state(t, 'rows', 0.1, 0.3)
        st = CR.State(head=w, jolt=j, t=t, walls=0)
    cv = CR.backdrop(cam, t, bank=1.0)
    lay = CR.render(cam, t, st, 'rows')
    CR.over(cv, lay)
    return cv


def S_B(t):
    """S3-01: JD alone in front of the staring stands; the whole world rendered with LF.cam_s3(t)."""
    cam = LF.cam_s3(t)
    st = CR.State(head=1.0, lean=1.0, t=t)
    cv = CR.backdrop(cam, t, bank=1.0)
    CR.floor(cv, cam)
    lay = CR.render(cam, t, st, 'flood')
    CR.over(cv, lay)
    A = assets()
    hz = A['haze']
    yb = _s3_haze_y(cam)
    K.draw(cv, hz, 540.0 + 30.0 * math.sin(t * 0.21), yb, scale=(1.25, 1.0), mode='add', opacity=1.0)
    A['dust'].draw(cv, cam, t, opacity=0.8)                      # behind him: nothing in front of his face
    LF.draw_s3(cv, cam, t)
    return cv


def _s3_haze_y(cam):
    xy, _ = cam.project(np.array([[0.0, -900.0, 7400.0]]))
    return float(xy[0, 1])


def S_C_state(t, part='all'):
    psi = psi_at(t)
    ppl = people_at(t)
    return CR.State(head=1.0, tilt=tilt_at(t), tilt_late=tilt_at(t, 2), lean=lean_rows(t), people=ppl, phones=ppl,
                    part=part, near_cull=10500.0, fog=psi / 70.0, walls=0.0, tap=tap_at(t), lookup=lookup_at(t), t=t,
                    cards=1.0 if part != 'nocards' else 0.0)


def S_C_layers(t, part='all'):
    """S3-02 / S4 rows world. part 'all' | 'nocards' -> full frame; 'cards' -> the card layer alone (transparent)."""
    cam = CR.cam_rows(psi_at(t), focus_at(t))
    st = S_C_state(t, part)
    lay = CR.render(cam, t, st, 'rows')
    if part == 'cards':
        return lay
    cv = CR.backdrop(cam, t, bank=1.0)
    CR.over(cv, lay)
    return cv


def S_C_cards(t):
    return S_C_layers(t, 'cards')


def S_C(t):
    w = X.TX['O6'].win(T_O6, pre=O6_PRE, post=O6_POST)
    if w.inside(t):
        return o6_cards(t)
    if X.side_b(t, w.t1):
        return S_C_layers(t, 'nocards')
    return S_C_layers(t, 'all')


def S_D(t):
    """S5-01: the 85 mm plate (emptied stands as bokeh, phones), the warm key from screen-left, JD's chin-up bust."""
    cam = CR.cam_jd()
    g = LF.key_gain(t)
    st = CR.State(head=1.0, cards=0.0, part='nocards', last=True, people=1.0, phones=1.0, light=1.0, t=t,
                  light_gain=max(g, 0.05))
    cv = CR.backdrop(cam, t, bank=0.0, light=1.0, warm_key=g)
    lay = CR.render(cam, t, st, 'flood')
    CR.over(cv, lay)
    K.draw(cv, assets()['warm'], -140.0, 980.0, opacity=0.9 * g, mode='add')
    LF.draw_s5(cv, t)
    return cv


def S_E(t):
    """S6-01 / S6-02: the emptied wide in warm light; the last card tips; flaps rise; the floodlight comes back."""
    cam = CR.cam_wide()
    lt = light_handback(t)
    bank = 1.0 - lt
    ppl = people_s6(t)
    st = CR.State(head=0.0, lean=1.0, flap=flap_angles(t), last_tip=last_tip(t), people=ppl, phones=ppl,
                  light=lt, empty=True, t=t, lines=False)
    return _wide_world(cam, t, st, bank=bank, light=lt, warm_key=lt, dust=bank)


# ============================================================================================== O6 on the card layer
@functools.lru_cache(maxsize=1)
def card_mask4():
    """Card-layer alpha at the window start (1/4 res, dilated 2 px): the only place the burning edge may glow."""
    lay = X._frozen(S_C_cards, fr(708 - O6_PRE))
    a = cv2.resize(np.ascontiguousarray(lay[..., 3]), (X.W4, X.H4), interpolation=cv2.INTER_AREA)
    a = cv2.dilate(a, np.ones((5, 5), np.uint8))
    a.flags.writeable = False
    return a


@functools.lru_cache(maxsize=1)
def o6_seed(n=4000, seed=5):
    """Ember spawn points from the luminance of the frozen CARD layer only (no floor term: >= 98 % inside cards)."""
    lay = X._frozen(S_C_cards, fr(708 - O6_PRE))
    small = cv2.resize(np.ascontiguousarray(lay[..., :3]), (X.W2, X.H2), interpolation=cv2.INTER_AREA)
    asmall = cv2.resize(np.ascontiguousarray(lay[..., 3]), (X.W2, X.H2), interpolation=cv2.INTER_AREA)
    L = (K.lum(small) * (asmall > 0.5)).ravel().astype(np.float64)
    p = np.clip(L, 0, 4) ** 1.5
    p /= p.sum()
    rng = np.random.default_rng(seed)
    idx = rng.choice(L.size, n, p=p)
    y, x = np.divmod(idx, X.W2)
    pts = np.c_[(x + rng.random(n)) * 2.0, (y + rng.random(n)) * 2.0]
    out = (pts, rng.uniform(0, 1, n), rng.normal(0, 1, (n, 2)), L[idx])
    for a in out:
        a.flags.writeable = False
    return out


def o6_cards(t, n=4000, seed=5, life=1.2, band=20.0, noise=120.0):
    """jawad_tx._tx_embers ('btt') restricted to the card layer: A = all, B = no cards; the burning edge x the card
    alpha; embers spawn from the card layer's luminance only (request R1)."""
    w = X.TX['O6'].win(T_O6, pre=O6_PRE, post=O6_POST)
    Xg, Yg = X.grid4()
    nz = X.fbm(seed + 40, 7.0)

    def coord(x, y):
        return X.H - y
    corners = [coord(x, y) for x in (0, X.W) for y in (0, X.H)]
    dmin, dmax = min(corners) - noise - band, max(corners) + noise * 0.2 + band
    xn = coord(Xg, Yg) + noise * (nz - 0.5) * 2
    u = w.ua(t)
    front = K.lerp(dmin, dmax, K.EASE['inout_sine'](u))
    if not X.side_b(t, w.c):
        cv = S_C_layers(t, 'all')
        mA = np.clip((xn - front) / 6.0, 0, 1)
        X.mix_mask(cv, S_C_layers(t, 'nocards'), X.up(1.0 - mA))
        edge = np.exp(-((xn - front - band * 0.3) / (band * 0.35)) ** 2).astype(np.float32) * card_mask4()
        X._emit(cv, X._gl(edge, (0.6, 2.5), (1.0, 0.35)), np.float32(K.C['FLAME']) * 1.4 + np.float32(K.C['AMBER']) * 0.3)
    else:
        cv = S_C_layers(t, 'nocards')
    pts, rnd, nrm, lumv = o6_seed(n, seed)
    pc = X.H - pts[:, 1]
    ix = np.clip((pts[:, 0] / 4).astype(int), 0, X.W4 - 1)
    iy = np.clip((pts[:, 1] / 4).astype(int), 0, X.H4 - 1)
    pc = pc + noise * (nz[iy, ix] - 0.5) * 2
    ts_ = w.t0 + X._inv_inout_sine((pc - dmin) / (dmax - dmin)) * (w.pre / FPS)
    tau = t - ts_
    life_i = np.minimum(life, w.last - ts_)
    alive = (tau >= 0) & (tau < life_i)
    if alive.any():
        a = tau[alive]
        P = pts[alive]
        nv = nrm[alive]
        vx = (30 + 50 * rnd[alive]) + 18 * nv[:, 0]
        vy = -46.0 - 40 * rnd[alive] + 14 * nv[:, 1]
        drag = (1 - np.exp(-2.2 * a)) / 2.2
        x = P[:, 0] + vx * drag * 2.0 + 6 * np.sin(a * 7 + rnd[alive] * 40)
        y = P[:, 1] + vy * a - 30 * a * a
        k = a / life_i[alive]
        col = X._ember_ramp(k) * (0.25 + 1.1 * np.clip(lumv[alive] * 3, 0, 1))[:, None]
        buf = np.zeros((X.H2, X.W2, 3), np.float32)
        xi = (x / 2).astype(int)
        yi = (y / 2).astype(int)
        ok = (xi >= 0) & (xi < X.W2) & (yi >= 0) & (yi < X.H2)
        np.add.at(buf, (yi[ok], xi[ok]), col[ok])
        glow = cv2.GaussianBlur(buf, (0, 0), 1.5) * 2.2 + cv2.GaussianBlur(buf, (0, 0), 5.0) * 1.2
        cv[..., :3] += cv2.resize(glow, (X.W, X.H), interpolation=cv2.INTER_LINEAR)
    return cv


# ============================================================================================== O2 without the wrap seam
@functools.lru_cache(maxsize=8)
def _fbm_tall(seed, scale, octaves, extra=220):
    """jawad_tx.fbm with extra rows at the bottom (read-only): the smoke scrolls through it without wrapping, so the
    shared O2's np.roll seam (a hard horizontal line across the smoke) never appears."""
    H4, W4 = X.H4, X.W4
    rows = H4 + extra
    rng = np.random.default_rng(seed)
    acc = np.zeros((rows, W4), np.float32)
    a = 1.0
    for o in range(octaves):
        n = rng.standard_normal((int(rows / scale * 2 ** o) + 2, int(W4 / scale * 2 ** o) + 2)).astype(np.float32)
        acc += a * cv2.resize(n, (W4, rows), interpolation=cv2.INTER_CUBIC)
        a *= 0.5
    acc = (acc - acc.min()) / max(1e-6, float(acc.max() - acc.min()))
    acc.flags.writeable = False
    return acc


def o2_smoke(t, w, A, B, seed=31, rise=260.0):
    """Copy of jawad_tx._tx_smoke (O2) reading its noise from _fbm_tall instead of np.roll (same look, no seam)."""
    u = w.u(t)
    sh = int(rise * u / 4)
    n = _fbm_tall(seed, 18.0, 3)[sh:sh + X.H4]
    n2 = _fbm_tall(seed + 1, 7.0, 3)[2 * sh:2 * sh + X.H4]
    dens = np.clip((n * 0.75 + n2 * 0.25 - 0.2) * 1.6, 0, 1)
    Xg, Yg = X.grid4()
    vert = (Yg / X.H)
    thr_a = K.EASE['inout_sine'](K.clamp(u / 0.55))
    thr_b = K.EASE['inout_sine'](K.clamp((u - 0.45) / 0.55))
    cover = np.clip((thr_a * 1.6 - (dens * 0.7 + (1 - vert) * 0.3)) / 0.12, 0, 1) * \
        (1 - np.clip((thr_b * 1.6 - (dens * 0.7 + vert * 0.3)) / 0.12, 0, 1))
    cv = (B if u >= 0.5 else A)(t)
    Cm = X.up(cover)[..., None] * np.float32(0.88)
    lit = X.up((dens * vert ** 2).astype(np.float32))[..., None]
    smoke = np.float32(K.C['SMOKE']) * (0.5 + 0.6 * X.up(dens)[..., None]) + np.float32(K.C['FLAME']) * 0.45 * lit
    cv[..., :3] = cv[..., :3] * (1 - Cm) + smoke * Cm
    return cv


def plan_draw(plan, t, scenes):
    """plan.draw with every O2 window drawn by the local seam-free o2_smoke (windows, cut rule, samples unchanged)."""
    for i, (x, c, o) in enumerate(plan.steps):
        if x.id == 'O2':
            w = x.win(c, **o)
            if w.inside(t):
                return o2_smoke(t, w, scenes[i], scenes[i + 1], seed=o.get('seed', 31), rise=o.get('rise', 260.0))
    return plan.draw(t, scenes)


# ============================================================================================== text
def _jline_state(i, t):
    """(x, y, scale, opacity, blur) of judgement line i at t, or None. Arrival out_expo from the crowd (scale 0.35,
    blurred) to the hold (scale 1, sharp); when the next line starts it recedes up/back (9 f) then fades (to +24 f)."""
    txt, f0, arr, _ = J_LINES[i]
    t0 = fr(f0)
    if t < t0:
        return None
    u = K.ramp(t, t0, t0 + fr(arr), 'out_expo')
    x = K.lerp(J_FROM[0], J_HOLD[0], u)
    y = K.lerp(J_FROM[1], J_HOLD[1], u)
    s = K.lerp(0.35, 1.0, u)
    b = K.lerp(8.0, 0.0, u)
    op = K.ramp(t, t0, t0 + fr(2), 'linear')
    if i + 1 < len(J_LINES):
        n0 = fr(J_LINES[i + 1][1])
        if t >= n0:
            v = K.ramp(t, n0, n0 + fr(9), 'inout_cubic')
            x, y = K.lerp(x, J_BACK[0], v), K.lerp(y, J_BACK[1], v)
            s = K.lerp(s, 0.72, v)
            b = K.lerp(b, 6.0, v)
            op = K.lerp(op, 0.45, v) * (1.0 - K.ramp(t, n0 + fr(9), n0 + fr(24), 'inout_sine'))
    if op <= 0.002:
        return None
    return x, y, s, op, b


def draw_judgements(cv, t):
    A = assets()
    n = 0
    for i in range(len(J_LINES)):
        s = _jline_state(i, t)
        if s is None:
            continue
        x, y, sc, op, b = s
        A['lines'][i].draw(cv, x, y, scale=sc, opacity=op, blur=b)
        n += 1
    return n


def draw_overlays(cv, t, hook='A'):
    """Designed text in reel time (never inside the world: cuts and the loop tail do not touch it)."""
    A = assets()
    blocks = []
    if hook == 'A' and t < 2.95:
        A['hookA'].draw(cv, t, 540.0, 560.0, t0=-0.1, out_t0=2.533)
        if t < 2.9:
            blocks.append('hookA')
    if hook == 'B' and t < 2.2:
        A['hookB'].draw(cv, t, 540.0, 560.0, t0=-0.1, out_t0=1.733)
        _rise_line(cv, A['hookB3'], t, 540.0, 752.0, 0.25, 1.733)
        blocks.append('hookB')
    if T_PAY <= t < T_WIDE:
        A['pay'].draw(cv, t, 430.0, 560.0, t0=T_PAY, out_t0=28.433)
        _rise_line(cv, A['pay3'], t, 430.0, 781.3, T_PAY + 0.35, 28.433)
        blocks.append('payoff')
    return blocks


def _rise_line(cv, spr, t, x, y, t0, out_t0, dur=0.6):
    """A caps line rising like HouseTitle's caps (28 px rise, 6 px blur-in, out_cubic) with the lockup's exit."""
    if t < t0:
        return
    out = 1.0 - K.ramp(t, out_t0, out_t0 + 0.35, 'in_cubic')
    if out <= 0:
        return
    uc = K.ramp(t, t0, t0 + dur, 'out_cubic')
    spr.draw(cv, x, y + 28 * (1 - uc), opacity=out * K.ramp(t, t0, t0 + dur * 0.7, 'inout_sine'), blur=6 * (1 - uc))


# ============================================================================================== build (A / B)
def build(hook='A'):
    """-> draw, post, samples, cues, prewarm for hook 'A' (public) or 'B' (Trial: frames 0-89 differ)."""
    plan = X.Plan(STEPS if hook == 'A' else STEPS_B)

    def SA(t):
        return S_A(t, hook)
    scenes = [SA, S_B, S_C, S_D, S_E] if hook == 'A' else [S_HB, SA, S_B, S_C, S_D, S_E]

    def world(tt):
        if tt < 0:
            return S_A(tt, 'A')                       # frame 0's past for both versions (the seam lands on A's f0)
        return plan_draw(plan, tt, scenes)

    def draw(t):
        cv = E.loop_world(world, t, DUR, d=0.5)
        if NOTEXT:
            return cv
        blocks = draw_overlays(cv, t, hook)
        assets()['card'].draw(cv, t, T_CARD)
        ch = captions(hook).draw(cv, t)
        if DEBUG:
            _log_blocks(t, hook, blocks, ch)
        return cv

    def post(cv, t):
        r, c = rays_at(t, hook)
        if r > 0 and c is not None:
            bank_rays(cv, t, c, r)                    # the floodlight bank is the ONLY ray source (not type, not JD)
        kw = _merge(plan.post_kw(t), X.TX['O6'].post_kw(t, T_O6, pre=O6_PRE, post=O6_POST, push_gain=0.3),
                    assets()['card'].post_kw(t, T_CARD, DUR))
        kw.update(rays=0.0)
        return G.tx_finish(cv, t, LOOK, cuts=CUTS, **kw)

    def samples(t):
        f = int(round(t * FPS))
        s = plan.samples(t)
        if 480 <= f <= 503:
            s = 7
        elif 504 <= f <= 575:
            s = 5
        w = X.TX['O6'].win(T_O6, pre=O6_PRE, post=O6_POST)
        if w.inside(t):
            s = X.TX['O6'].samples_at(t, T_O6, 3, pre=O6_PRE, post=O6_POST)
        for _, f0, arr, _ in J_LINES:
            if f0 <= f < f0 + 2:
                s = max(s, 7)
            elif f0 + 2 <= f < f0 + arr:
                s = max(s, 5)
        if 876 <= f <= 888 or 960 <= f <= 1011:
            s = max(s, 5)
        return s

    def cues():
        return []

    def _prewarm():
        prewarm()
        captions(hook).prewarm()

    draw.plan = plan
    return draw, post, samples, cues, _prewarm


def rays_at(t, hook='A'):
    """God-ray strength and centre: 0.22 while the bank is in a wide frame (0-9.6 CAM_WIDE, 9.6-12.8 cam_s3),
    0 in the 135 / 85 mm shots and the warm wide, ramping back 0 -> 0.22 over 33.6-35.0 (frame 0 matches)."""
    if hook == 'B' and t < 2.4 + fr(12):
        k = K.ramp(t, 2.4 - fr(15), 2.4 + fr(12), 'inout_sine')
        return 0.22 * k, BANK_WIDE
    if t < T_S3:
        return 0.22, BANK_WIDE
    if t < T_ROWS:
        b = CR.bank_xy(LF.cam_s3(t))
        return 0.22, b
    if t < 33.6:
        return 0.0, None
    return 0.22 * K.ramp(t, 33.6, 35.0, 'inout_sine'), BANK_WIDE


def bank_rays(cv, t, center, strength):
    """The finish's god rays (same K.god_rays maths, threshold / length / tint as G.finish) with the source restricted
    to the lamp bank's neighbourhood: the hook / payoff type, the captions and JD (S3-01, also held out by his matte as
    LF.s3_rays does) never stream light. In place, before the finish (which then runs with rays=0)."""
    P = G.FIN[LOOK]
    q = K._quarter(cv)[..., :3]
    lw, lh = q.shape[1], q.shape[0]
    xs = (np.arange(lw, dtype=np.float32) + 0.5) * 4
    ys = (np.arange(lh, dtype=np.float32) + 0.5) * 4
    d = np.sqrt(((xs[None, :] - center[0]) / 230.0) ** 2 + ((ys[:, None] - center[1]) / 190.0) ** 2)
    m = np.clip(1.6 - d, 0, 1).astype(np.float32)
    if LF.S3_T0 <= t < LF.S3_T1:
        a = LF.jd_alpha(t)
        if a is not None:
            m = m * (1.0 - cv2.resize(a, (lw, lh), interpolation=cv2.INTER_AREA))
    q = K._bright_pass(q * m[..., None], P.get('rays_threshold', 0.3), 0.2)
    cx, cy = center[0] / 4, center[1] / 4
    length, n = P.get('rays_length', 0.4), 10
    acc = K._radial_smear(q, cx, cy, length, n, True)
    acc = K._radial_smear(acc, cx, cy, length / n, n, False)
    acc = cv2.GaussianBlur(acc, (0, 0), 0.8)
    acc *= np.float32([1.0, 0.78, 0.45])
    K._add_lowres(cv, acc * np.float32(strength * 3))
    return cv


def _merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            if k == 'push':
                out['push'] = out.get('push', 0.0) + v
            elif k == 'bloom_scale':
                out[k] = out.get(k, 1.0) * v
            else:
                out[k] = v
    return out


def _log_blocks(t, hook, blocks, ch):
    n = list(blocks)
    for i in range(len(J_LINES)):
        st = _jline_state(i, t)
        if st is not None and st[3] > 0.02:
            n.append('J%d' % (i + 1))
    f = int(round(t * FPS))
    if T_CARD <= t:
        n.append('endcard')
    if ch is not None:
        n.append('cap:' + ch.text)
    os.makedirs(RW + '/qa', exist_ok=True)
    with open(RW + '/qa/text_blocks_%s.log' % hook, 'a') as fh:
        fh.write('%d\t%.4f\t%d\t%s\n' % (f, t, len(n), '|'.join(n)))


draw, post, samples, cues, prewarm_A = build('A')


def prewarm():                                     # render.py calls it once per worker
    CR.prewarm()
    LF.prewarm()
    A = assets()
    A['card']._settled_layer()
    captions('A').prewarm()
    o6_seed()
    card_mask4()
