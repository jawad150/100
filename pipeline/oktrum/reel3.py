"""reel3 "Peace of mind" (Oktrum, 1080x1920, 30 fps): DUR 21.5 s, LOOK 'airy', BPM 110 (beat 0.545 s).
BRIEF.md §6.3 / §10. Clean SaaS light, "follow the object": one continuous world, no cuts. The ice-white page
(K.background('airy') with its faint navy dot grid, panned by the camera) ends on a navy plate that grows out of
the shield and fills the frame (no fade, no flash).

VO word onsets used (s, read from the waveform of <WS>/audio/reel3_vo.wav, VO starts at 0.20 s): What 0.26 ·
if 0.93 · the 1.02 · market 1.10 · crashes 1.40 · overnight 1.82 · With 2.66 · Oktrum 2.78 · your 3.76 ·
account 3.85 · can 4.27 · never 4.45 · go 4.80 · below 5.00 · zero 5.26 · negative 6.32 · bank(-tier) 8.40 ·
expert 9.90 · Trade (with total) 11.12 · peace 11.98 · Oktrum 13.01 · Trade (with) 13.88 · confidence 14.33 ·
Get (started) 15.30 · oktrum (dot com) 16.04.

Shot list as built (one continuous camera; t in s, beat = t / 0.545):
 0.00-2.66 HOOK (b0-4.9). Ice-white page. Glass chart card (OK.candles, light look) in 3D; a red 3D glass
           candle (candle_red day) is already falling at frame 0 at the right of the frame, accelerates and punches
           through the chart's crash slot at 1.40 ("crashes"): candles(crash=) drops the long DOWN_DEEP candle,
           camera judder, "Balance" counter (JetBrains Mono, DOWN_DEEP, no currency) plunges 8,460.20 -> ~1,180.
           Copy word by word on the VO: "What if the market" (INK 96) / "crashes" (serif DOWN_DEEP 250, slam on
           1.40) / "overnight?" (INK 96, 1.82). Candle smeared vertically per layer (K.whip_blur), 7 samples.
 2.66-5.95 ZERO. Headline fades in 0.28 s as the camera follows the falling counter down (2.66-3.75): the chart
           scrolls off the top. "With Oktrum," (BLUE_DEEP 64, 2.78) / "your account can never" (INK 80, per word)
           / "go below" + "zero." (serif BLUE_DEEP 190, slam 5.26). The counter accelerates toward zero and is
           stopped dead at 0.00 on "zero" (5.26) as shield_lock slams in above it (scale 1.8 -> 1, in_cubic,
           solid on 5.26; damped judder). Counter turns DOWN_DEEP -> BLUE_DEEP. Padlock clicks shut 5.80
           (day_anim click_frame remapped onto 5.80).
 5.70-11.12 JOURNEY (no cuts). The shield launches and leads; it draws a violet -> blue -> cyan light-trail
           ribbon (Catmull-Rom through world stations, twisting flat ribbon with a soft tinted glow). The camera
           rides behind it (moves inout_sine, banked by lateral speed, 7 samples):
             5.70-6.42 to card 1 "Negative Balance / Protection" (pops 6.32 "negative")
             7.66-8.46 to card 2 "Bank-Tier / Encryption" (pops 8.40 "bank")
             9.22-9.96 to card 3 "22/5 Expert / Support" (pops 9.90 "expert"); badge "PCI DSS Compliant" 10.55
           Cards: white frosted glass (ui.glass_card airy) with a VIOLET -> CYAN icon disc, INK titles 52 px.
 11.12-13.01 GATHER. Camera pulls back (dist 1400 -> 2200) as the three cards and the badge fly into a ring
           round the shield (now hero size). "Trade with total" (INK 92, 11.12) / "peace of mind." (serif VIOLET
           170, 11.98).
 13.01-15.30 NAVY PLATE. A rounded navy plate grows out of the shield (13.01), holds as a big card (13.85) and
           fills the frame by 15.15. The shield sinks into it while okt_mark night_anim swirls in at the same spot
           ("Oktrum" 13.01) and rises to y 640. "Trade With" (IVORY 120, 13.88) / "Confidence" (serif CYAN 200,
           slam 14.33); both leave 14.95-15.25.
 15.00-21.50 END CARD on navy: the mark glides into the logo's mark slot and crossfades into logo_full
           (640 px, y 700) 15.55-15.85 while the wordmark wipes in 15.40-15.85; button "Get Started" springs in
           15.30, hand cursor presses it 15.82 (beat 29); "oktrum.com" 16.04; risk line 30 px, two lines, 15.55.
           Settled 16.30-21.50 (5.2 s).

SFX (draft, see cues()): hook whoosh_fast 1.22, impact_soft + downlifter 1.40, swish_small 2.70, slot_tick
3.76-5.26, impact_soft + glass_tap + sub_drop 5.26, ui_click + toggle_on 5.80, whoosh_by 6.10 / 8.10 / 9.62,
pop 6.32 / 8.40 / 9.90 / 10.55, shimmer 6.5, whoosh_slow 11.6, shimmer 11.98, grow_swell 13.01, shimmer 13.05,
impact_soft 14.33, riser -> 15.15, pop 15.30, logo_sting 15.55, ui_click + toggle_on 15.82.

Placeholders (switch automatically when <WS>/assets3d/<name>/<folder>/meta.json exists): candle_red/day (a red
glass candle sprite), shield_lock/day + day_anim (gradient shield with a padlock), okt_mark/night_anim (dot_sphere).
"""
import functools, json, math, os

import numpy as np
import cv2

import oktrum_kit as OK
from oktrum_kit import K, T, ui, S3

DUR, LOOK, BPM = 21.5, 'airy', 110
BEAT = 60.0 / BPM
HALF = 0.5 / K.FPS
D0 = 1500.0

_VO = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reel3_vo.json')))
PH = [p['t0'] for p in _VO['phrases']]

# ---- word onsets (waveform) -------------------------------------------------------------------------------
T_WHAT, T_IF, T_THE, T_MARKET, T_CRASH, T_OVER = PH[0], 0.93, 1.02, 1.10, 1.40, 1.82
T_WITH, T_OKT1 = PH[1], 2.78
T_YOUR, T_ACC, T_CAN, T_NEVER, T_GO, T_BELOW, T_ZERO = PH[2], 3.85, 4.27, 4.45, 4.80, 5.00, 5.26
T_LOCK = 5.80
T_NEG, T_BANK, T_EXP, T_PCI = 6.32, 8.40, 9.90, 10.55
T_TRADE, T_PEACE = PH[6], 11.98
T_OKT2 = PH[7]                       # 13.01 plate + mark
T_TWC, T_CONF = PH[8], 14.33
T_CTA = PH[9]                        # 15.30
T_URL = 15.95                        # lands 16.2 on "oktrum (dot com)" 16.04
T_CLICK = 15.82                      # beat 29
T_RISK = 15.55
T_FULL = 15.15                       # plate covers the frame

MOVES = [(5.70, 6.42), (7.66, 8.46), (9.22, 9.96)]
GATHER = (11.12, 12.60)

COPY = dict(cta='Get Started', url='oktrum.com',
            risk=('Trading involves high risk.', 'You could lose some or all of your investment.'),
            cards=(('Negative Balance', 'Protection'), ('Bank-Tier', 'Encryption'), ('22/5 Expert', 'Support')),
            badge='PCI DSS Compliant')

INK, BLUE_DEEP, DOWN_DEEP, VIOLET, CYAN, BLUE = '#07091A', '#3A55E0', '#B91C1C', '#8465F4', '#81D4E6', '#5170FF'
TEXT2 = '#4A5070'
NAVY_LIN = K.hexlin('#07091A')


def have3d(name, folder):
    return os.path.exists(os.path.join(K.ASSETS3D, name, folder, 'meta.json'))


def sans(text, px, fill=INK, font=None, tracking=0.0):
    return T.render(text, 'flat', font=font or OK.FONT_HEAD, px=px, fill=fill, tracking=tracking)


def serif(text, px, fill=BLUE_DEEP):
    return T.render(text, 'serif_italic', px=px, fill=fill)


def unproject(cam, sx, sy, d):
    v = np.array([(sx - K.CX) * d / cam.focal, (sy - K.CY) * d / cam.focal, d], np.float64)
    return cam.pos + cam.R @ v


def damp(t, t0, amp, k=7.0, w=24.0):
    """Damped oscillation that starts at 0 on contact (continuity at the hit frame)."""
    d = t - t0
    if d <= 0:
        return 0.0
    return amp * math.exp(-k * d) * math.sin(w * d)


# =================================================================================================== sprites
def _shield_placeholder():
    S = 900
    img = np.zeros((S, S, 4), np.float32)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    u, v = (xx - S / 2) / 330.0, (yy - 120) / 640.0           # shield body: x +-330, y 120..760
    half = np.where(v < 0.55, 1.0 - 0.12 * (v / 0.55) ** 2, 0.88 * np.sqrt(np.clip(1 - ((v - 0.55) / 0.45) ** 2,
                                                                                    0, 1)))
    top = 0.04 * np.cos(u * 1.4)
    d = np.minimum(half - np.abs(u), (v - top) * 3.0)
    a = np.clip(d * 140, 0, 1) * (v < 1.0)
    g = np.clip((xx + yy) / (2 * S), 0, 1)[..., None]
    col = K.hexlin(VIOLET) * (1 - g) + K.hexlin(BLUE) * g
    edge = np.clip(1 - d * 40, 0, 1)[..., None]
    col = col * (0.85 + 0.35 * edge) + 0.18 * np.clip(1 - ((u + 0.35) ** 2 * 6 + (v - 0.25) ** 2 * 4), 0, 1)[..., None]
    img[..., :3] = col * a[..., None]
    img[..., 3] = a * 0.92
    return img


def _padlock(closed):
    S = 900
    s = ui.Surf(S, S)
    silver, dark = ui.col('#E6EAF5'), ui.col('#9AA3BC')
    lift = 0 if closed else 70
    s.ring(450, 420 - lift, 95, 30, dark)
    a, X0, Y0 = s.rrect_mask(330, 420, 240, 190, 36)
    s.fill(a, X0, Y0, silver)
    a, X0, Y0 = s.rrect_mask(330, 420, 240, 50, 20)
    s.fill(a, X0, Y0, ui.col('#FFFFFF'), 0.6)
    s.circle(450, 505, 22, ui.col('#3A3F55'))
    spr = s.sprite()
    spr[:420 - 1, :, :] *= 1.0
    return spr


def _candle_placeholder():
    S = 1000
    s = ui.Surf(S, S)
    s.rrect(486, 120, 28, 760, 14, ui.col('#7A1414'))                   # wick
    s.rrect_grad(380, 260, 240, 480, 30, ui.col('#E04848'), ui.col(DOWN_DEEP), angle=-20)
    s.rrect(400, 280, 46, 440, 22, ui.col('#FFFFFF'), opacity=0.35)       # glass highlight
    return s.sprite()


def _feature_card(lines, icon_name):
    w, h = 780, 236
    base = ui.glass_card(w, h, 64, LOOK, rim=0.6, glow=0.5, shadow=1.0)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    cx, cy = p + 44 + 62, p + h / 2
    c0, c1 = ui._v(K.C['VIOLET']), ui._v(K.C['CYAN'])
    a, X0, Y0 = S.circle(cx, cy, 62, c0)
    S.fill(a, X0, Y0, ui._lingrad(a.shape[1], a.shape[0], c0, c1, -45), 1.0)
    S.sheen(cx - 61, cy - 61, 122, 122, 61, 0.18, 0.0, 0.55)
    S.paste(ui.icon(icon_name, 68, K.C['WHITE'], stroke=2.4), cx, cy, anchor=(0.5, 0.5))
    tx = p + 44 + 124 + 34
    ui.put_text(f, tx, p + h / 2 - 10, lines[0], 52, OK.FONT_HEAD, ui.col(INK), 'ls')
    ui.put_text(f, tx, p + h / 2 + 54, lines[1], 52, OK.FONT_HEAD, ui.col(INK), 'ls')
    return ui.derive_panel(base, f)


def _words(text, px, fill, font=None):
    """Per-word sprites of one line plus each word's left x offset (from the measured prefix)."""
    ws = text.split(' ')
    total = T.measure(text, 'flat', font=font or OK.FONT_HEAD, px=px)[0]
    f = font or OK.FONT_HEAD
    sp = T.measure('a a', 'flat', font=f, px=px)[0] - T.measure('aa', 'flat', font=f, px=px)[0]
    out = []
    for i, w in enumerate(ws):
        x = T.measure(' '.join(ws[:i]), 'flat', font=f, px=px)[0] + sp if i else 0.0
        out.append((sans(w, px, fill, font), x))
    return out, total


@functools.lru_cache(maxsize=1)
def assets():
    logo = K.load_image(os.path.join(K.BRAND, 'logo_full.png'), size=640)
    lh, lw = logo.shape[:2]
    mk = int(round(244 / 1102 * lw))
    return dict(
        l1=_words('What if the market', 96, INK), crashes=serif('crashes', 250, DOWN_DEEP),
        over=sans('overnight?', 96),
        with_=sans('With Oktrum,', 64, BLUE_DEEP),
        l2=_words('your account can never', 80, INK), gobelow=sans('go below', 80), zero=serif('zero.', 190),
        trade=sans('Trade with total', 92), peace=serif('peace of mind.', 170, VIOLET),
        twith=sans('Trade With', 120, 'IVORY'), conf=serif('Confidence', 200, CYAN),
        balance=sans('Balance', 40, TEXT2, font=OK.FONT_UI, tracking=0.08),
        cnt_red=T.Counter('flat', prefix='', decimals=2, sep=',', font=OK.FONT_MONO_BOLD, px=150, fill=DOWN_DEEP),
        cnt_blue=T.Counter('flat', prefix='', decimals=2, sep=',', font=OK.FONT_MONO_BOLD, px=150, fill=BLUE_DEEP),
        chart_card=ui.glass_card(960, 560, 48, LOOK, rim=0.5, glow=0.4, shadow=1.0),
        cards=[_feature_card(COPY['cards'][0], 'shield'), _feature_card(COPY['cards'][1], 'key'),
               _feature_card(COPY['cards'][2], 'users')],
        badge=ui.badge(COPY['badge'], look=LOOK, icon_name='check', size=36),
        shield_ph=_shield_placeholder(), lock_open=_padlock(False), lock_shut=_padlock(True),
        candle_ph=_candle_placeholder(),
        ph_label=lambda s: T.render(s, 'flat', font=OK.FONT_MONO, px=22, fill=TEXT2),
        glow_v=K.radial(512, K.hexlin(VIOLET), 2.2), glow_c=K.radial(512, K.hexlin(CYAN), 2.2),
        head=K.radial(256, K.hexlin(CYAN) * 1.4, 2.0),
        logo=logo, logo_mark=np.ascontiguousarray(logo[:, :mk + 2]), logo_word=np.ascontiguousarray(logo[:, mk + 2:]),
        url=sans(COPY['url'], 46, 'IVORY', font=OK.FONT_UI, tracking=0.02),
        risk=[sans(s, 30, ('IVORY', 0.78), font=OK.FONT_BODY) for s in COPY['risk']],
    )


@functools.lru_cache(maxsize=8)
def label(s):
    return T.render(s, 'flat', font=OK.FONT_MONO, px=22, fill=TEXT2)


def prewarm():
    assets()
    path()
    ring_slots()


# =================================================================================================== world
# beat-2 framing: camera target (0, 1100, 0); counter at world y 1400 (screen 1290), shield at 960 (screen ~830)
TGT2 = np.array([0.0, 1100.0, 0.0])
SHIELD0 = np.array([0.0, 1015.0, -60.0])
CNT_Y = K.Track([(T_WITH, 420.0, 'inout_cubic'), (3.75, 1430.0)])          # counter falls with the camera
STATIONS = [np.array(p, np.float64) for p in ((240.0, 2150.0, 250.0), (-280.0, 3200.0, 560.0),
                                              (220.0, 4250.0, 860.0))]
SIDE = (-1, 1, -1)                                                       # shield parks left / right / left
G = np.array([0.0, 5000.0, 1100.0])                                      # gather centre
DIST_ST, DIST_G = 1400.0, 2200.0
GOFF = np.array([0.0, 200.0, 0.0])                                      # shield sits above frame centre


def card_home(i):
    return STATIONS[i] + np.array([0.0, -205.0, 0.0])


def park(i):
    return STATIONS[i] + np.array([SIDE[i] * 235.0, 265.0, -150.0])


def _vec(tg, dist, yaw=0.0, pitch=0.0, roll=0.0):
    return [float(tg[0]), float(tg[1]), float(tg[2]), dist, yaw, pitch, roll]


_d = lambda v: np.array(v, np.float64)
CAMTRK = K.Track([
    (0.00, _vec((0, 0, 0), 1500.0), 'linear'),
    (T_WITH, _vec((0, -8, 0), 1450.0, 0, 0, 0.5), 'inout_cubic'),
    (3.75, _vec(TGT2, 1500.0, 0, -1.5, 0), 'linear'),
    (MOVES[0][0], _vec(TGT2 + _d((0, 12, 0)), 1450.0, 0, -1.5, 0), 'inout_sine'),
    (MOVES[0][1], _vec(STATIONS[0], DIST_ST, -3, 1.5, 0), 'linear'),
    (MOVES[1][0], _vec(STATIONS[0] + _d((14, 40, 0)), DIST_ST - 40, -2, 1, 0), 'inout_sine'),
    (MOVES[1][1], _vec(STATIONS[1], DIST_ST, 3, 1.5, 0), 'linear'),
    (MOVES[2][0], _vec(STATIONS[1] + _d((-14, 40, 0)), DIST_ST - 40, 2, 1, 0), 'inout_sine'),
    (MOVES[2][1], _vec(STATIONS[2], DIST_ST, -3, 1.5, 0), 'inout_sine'),
    (GATHER[0], _vec(STATIONS[2] + _d((40, 110, 0)), DIST_ST + 60, -2, 1, 0), 'inout_cubic'),
    (GATHER[1], _vec(G + GOFF, DIST_G, -4, 3, 0), 'linear'),
    (DUR, _vec(G + GOFF, DIST_G - 260, -1, 2, 0)),
])
SHAKES = ((T_CRASH, 16.0), (T_ZERO, 11.0))


def cam(t, aperture=None):
    v = CAMTRK(t)
    tx, ty, tz, dist, yaw, pitch, roll = (float(a) for a in v)
    vx = float(CAMTRK(t + 0.04)[0] - CAMTRK(t - 0.04)[0]) / 0.08
    roll += float(np.clip(-vx * 0.0016, -3.5, 3.5))                       # bank into lateral moves
    for t0, a in SHAKES:
        tx += damp(t, t0, a * 0.6, 9.0, 31.0)
        ty += damp(t, t0, a, 8.0, 26.0)
    ap = aperture if aperture is not None else (12.0 if t < MOVES[0][0] else 22.0)
    return K.Cam.orbit((tx, ty, tz), dist, yaw=yaw, pitch=pitch, roll=roll, aperture=ap)


# ---- the light-trail path ------------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def path():
    """Catmull-Rom path S0 -> park1 -> park2 -> park3 -> G: points (N, 3), arc-length s (N,), station s."""
    ctrl = [SHIELD0, SHIELD0 + _d((-120, 380, 60)), park(0) + _d((-60, -260, 20)), park(0),
            park(0) + _d((120, 330, 80)), park(1) + _d((80, -300, 10)), park(1),
            park(1) + _d((-120, 330, 80)), park(2) + _d((-60, -300, 10)), park(2),
            park(2) + _d((150, 300, 60)), G]
    P = np.array(ctrl, np.float64)
    k = 60
    pts = OK._catmull(P, k)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.r_[0.0, np.cumsum(seg)]
    s /= s[-1]
    st = [float(s[i * k]) for i in (3, 6, 9)]
    return pts, s, st


def path_at(u):
    pts, s, _ = path()
    u = float(np.clip(u, 0, 1))
    return np.array([np.interp(u, s, pts[:, j]) for j in range(3)])


@functools.lru_cache(maxsize=1)
def shield_track():
    _, _, st = path()
    keys = [(MOVES[0][0], 0.0, 'inout_sine'), (MOVES[0][1] - 0.08, st[0], 'linear'),
            (MOVES[1][0], st[0], 'inout_sine'), (MOVES[1][1] - 0.08, st[1], 'linear'),
            (MOVES[2][0], st[1], 'inout_sine'), (MOVES[2][1] - 0.08, st[2], 'linear'),
            (GATHER[0], st[2], 'inout_cubic'), (GATHER[1] - 0.1, 1.0)]
    return K.Track(keys)


SHIELD_W = K.Track([(MOVES[0][0], 450.0, 'inout_sine'), (MOVES[0][1], 300.0, 'linear'), (GATHER[0], 300.0,
                    'inout_cubic'), (GATHER[1], 440.0)])


def shield_pos(t):
    if t < MOVES[0][0]:
        return SHIELD0.copy()
    p = path_at(shield_track()(t))
    p[1] += 8.0 * math.sin(t * 2.1) * K.ramp(t, MOVES[0][1], MOVES[0][1] + 0.5, 'inout_sine')
    return p


@functools.lru_cache(maxsize=1)
def ring_slots():
    """World positions / rotations of the cards and badge in the gather ring, from the final camera."""
    c = cam(GATHER[1], aperture=0)
    slots = [((345, 1095), 2250, (2, 10, -2)), ((735, 1255), 2250, (2, -10, 2)), ((345, 1415), 2250, (-2, 8, 1)),
             ((540, 588), 1700, (0, 0, 0))]
    return [(unproject(c, sx, sy, d), rot) for (sx, sy), d, rot in slots]


# =================================================================================================== pieces
def draw_chart(cv, c, t):
    if t > T_WITH + 0.52:
        return
    crash = K.ramp(t, T_CRASH - 0.02, T_CRASH + 0.42, 'out_cubic')
    spr = OK.candles(26, 860, 420, 1.0, t, seed=11, crash=crash, look=LOOK, price=1.0847 * 1000, vol=0.004,
                     trend=0.12, drop=120)
    P = np.array([0.0, 40.0, 160.0])
    A = assets()
    op = 1.0 - K.ramp(t, T_WITH, T_WITH + 0.5, 'inout_sine')
    A['chart_card'].plane(cv, c, P, 960, rot=(6, -5, 0), opacity=op)
    K.draw_plane(cv, spr, c, P, float(spr.shape[1]), rot=(6, -5, 0), opacity=op,
                 anchor=(0.5, (OK.PAD + 210) / spr.shape[0]))


def crash_x():
    """World x of the crash slot (last slot of the plot) on the chart plane."""
    return 330.0


def draw_candle(cv, c, t):
    """The red 3D candle falling through the frame (hook)."""
    if t > 2.15:
        return
    if t < T_CRASH:
        y = -1000.0 + 300.0 * t + 0.5 * 580.0 * t * t
        vy = 300.0 + 580.0 * t
    else:
        d = t - T_CRASH
        y0 = -1000.0 + 300.0 * T_CRASH + 0.5 * 580.0 * T_CRASH ** 2
        v0 = 300.0 + 580.0 * T_CRASH
        y = y0 + v0 * d + 0.5 * 6500.0 * d * d
        vy = v0 + 6500.0 * d
    P = np.array([crash_x(), y, -260.0])
    yaw = -18.0 + 26.0 * t
    if have3d('candle_red', 'day'):
        spr = S3.get('candle_red', 'day').at_yaw(K.lerp(-30, 30, (t / 2.15)))
    else:
        spr = assets()['candle_ph']
    layer = np.zeros_like(cv)
    K.draw_billboard(layer, spr, c, P, 900.0, rot=-6.0 + 3.0 * math.sin(t * 2.0), dof=False)
    xy, z = c.project(P[None])
    pxs = vy * (c.focal / max(float(z[0]), 1.0)) / K.FPS                 # px per frame on screen
    K.whip_blur(layer, min(240.0, 0.5 * pxs), 90.0)
    if not have3d('candle_red', 'day'):
        label('candle_red placeholder').draw(layer, xy[0][0], xy[0][1] + 300, opacity=0.6)
    cv[..., :3] = cv[..., :3] * (1 - layer[..., 3:4]) + layer[..., :3]
    del yaw


def counter_value(t):
    if t < T_CRASH:
        return 8460.20 - 410.0 * t - 60.0 * math.sin(t * 5.0), -410.0
    if t < 2.30:
        u = K.ramp(t, T_CRASH, 2.30, 'out_cubic')
        v = K.lerp(8460.20 - 410.0 * T_CRASH, 1180.40, u)
        return v, (K.lerp(8460.20 - 410.0 * T_CRASH, 1180.40, K.ramp(t + 0.01, T_CRASH, 2.30, 'out_cubic')) - v) / 0.01
    if t < T_ZERO:
        u = (t - 2.30) / (T_ZERO - 2.30)
        v = 1180.40 * (1 - (0.35 * u + 0.65 * u * u))
        dv = -1180.40 * (0.35 + 1.3 * u) / (T_ZERO - 2.30)
        return max(v, 0.0), dv
    return 0.0, 0.0


def draw_counter(cv, c, t):
    if t > 6.4:
        return
    A = assets()
    v, dv = counter_value(t)
    y = CNT_Y(t) + damp(t, T_ZERO, 22.0, 8.0, 22.0)
    P = np.array([0.0, y, 0.0])
    op = 1.0 - K.ramp(t, MOVES[0][0] + 0.05, MOVES[0][0] + 0.33, 'linear')
    if op <= 0:
        return
    vel = max(-60000.0, dv)
    A['balance'].draw_plane(cv, c, P + np.array([0.0, -118.0, 0.0]), opacity=op)
    sw = K.ramp(t, T_ZERO, T_ZERO + 0.25, 'inout_sine')
    if sw < 1:
        A['cnt_red'].sprite(v, vel).draw_plane(cv, c, P, opacity=op)
    if sw > 0:
        A['cnt_blue'].sprite(v, vel).draw_plane(cv, c, P, opacity=op * sw)


def shield_anim_frame(t):
    """shield_lock sprite at t, 'slam' scale and placeholder flag."""
    if t >= MOVES[0][0] + 0.9 and have3d('shield_lock', 'day'):
        yaw = float(np.clip((shield_pos(t + 0.03)[0] - shield_pos(t - 0.03)[0]) / 0.06 * 0.012, -28, 28))
        yaw += 6.0 * math.sin(t * 0.9)
        return S3.get('shield_lock', 'day').at_yaw(yaw), False
    if have3d('shield_lock', 'day_anim'):
        a = S3.get('shield_lock', 'day', mode='anim')
        cf = float(a.meta.get('click_frame', 25)) / 30.0
        t0 = T_ZERO - 0.20
        if t < T_LOCK:
            at = K.lerp(0.0, cf, (t - t0) / (T_LOCK - t0))
        else:
            at = cf + (t - T_LOCK)
        return a.at_time(max(0.0, at), loop=False), False
    if have3d('shield_lock', 'day'):
        return S3.get('shield_lock', 'day').at_yaw(0.0), False
    return None, True


@functools.lru_cache(maxsize=4)
def _bbox_frac(key):
    if key == 'ph':
        spr = assets()['shield_ph']
    else:
        a = S3.get('shield_lock', 'day', mode=None if key == 'day' else 'anim')
        spr = a.frame(a.n - 1 if key == 'anim' else a.n // 2)
    x0, y0, x1, y1 = K.alpha_bbox(spr)
    return (x1 - x0) / spr.shape[1]


def draw_shield(cv, c, t, P=None, width=None, opacity=1.0):
    if t < T_ZERO - 0.22:
        return
    A = assets()
    P = shield_pos(t) if P is None else P
    w = SHIELD_W(t) if width is None else width
    # slam: scale 1.8 -> 1 (in_cubic), solid on T_ZERO, then a damped squash
    u = K.ramp(t, T_ZERO - 0.20, T_ZERO, 'in_cubic')
    sc = K.lerp(1.8, 1.0, u) + damp(t, T_ZERO, 0.07, 7.0, 20.0)
    op = opacity * K.ramp(t, T_ZERO - 0.20, T_ZERO - 0.10, 'linear')
    spr, ph = shield_anim_frame(t)
    if ph:
        spr = A['shield_ph'].copy()
        lk = A['lock_shut'] if t >= T_LOCK else A['lock_open']
        spr[..., :3] = spr[..., :3] * (1 - lk[..., 3:4]) + lk[..., :3]
        spr[..., 3:4] = spr[..., 3:4] + lk[..., 3:4] * (1 - spr[..., 3:4])
        frac = _bbox_frac('ph')
    else:
        frac = _bbox_frac('day')
    blur = 10.0 * (1 - u) if u < 1 else 0.0
    # comet head glow behind the shield while it travels
    if t > MOVES[0][0]:
        K.draw_billboard(cv, A['head'], c, P + np.array([0.0, 0.0, 30.0]), w * 1.5, opacity=0.35 * op, dof=False)
    K.draw_billboard(cv, spr, c, P, w / frac * sc, opacity=op, dof=True, blur=blur)
    if ph:
        xy, z = c.project(P[None])
        label('shield_lock placeholder').draw(cv, xy[0][0], xy[0][1] + w * 0.6 * c.focal / z[0], opacity=0.6 * op)
    if T_LOCK - 0.02 <= t <= T_LOCK + 0.6:                                  # click ring on the padlock
        xy, z = c.project((P + np.array([0.0, w * 0.05, -20.0]))[None])
        cr = ui.click_ring(t - T_LOCK, int(w * 0.32 * c.focal / z[0]), look=LOOK)
        if cr is not None:
            K.draw(cv, cr, xy[0][0], xy[0][1], opacity=0.8)


def card_state(i, t):
    """(position, rot, opacity, scale) of feature card i (3 = the PCI badge)."""
    tpop = (T_NEG, T_BANK, T_EXP, T_PCI)[i]
    if t < tpop - 0.04:
        return None
    if i < 3:
        home = card_home(i)
        rot0 = (4.0, SIDE[i] * -10.0, 0.0)
    else:
        home = card_home(2) + np.array([150.0, 270.0, -60.0])
        rot0 = (2.0, -6.0, 0.0)
    g = K.ramp(t, GATHER[0] + 0.07 * i, GATHER[1] - 0.25 + 0.07 * i, 'inout_cubic')
    P = home
    rot = rot0
    if g > 0:
        slot, rot1 = ring_slots()[i]
        lift = np.array([0.0, -140.0 * math.sin(math.pi * g), 0.0])
        P = home + (slot - home) * g + lift
        rot = tuple(K.lerp(a, b, g) for a, b in zip(rot0, rot1))
    op = K.ramp(t, tpop - 0.04, tpop + 0.10, 'linear')
    sc = K.lerp(0.82, 1.0, K.spring(max(0.0, t - (tpop - 0.04)), freq=2.6, damping=0.55))
    P = P + np.array([0.0, 6.0 * math.sin(t * 1.7 + i), 0.0])
    return P, rot, op, sc


def draw_card(cv, c, t, i):
    st = card_state(i, t)
    if st is None:
        return
    P, rot, op, sc = st
    A = assets()
    if i < 3:
        A['cards'][i].plane(cv, c, P, 780 * sc, rot=rot, opacity=op, dof_scale=1.0)
    else:
        A['badge'].plane(cv, c, P, A['badge'].w * 1.05 * sc, rot=rot, opacity=op)


# ---- ribbon ------------------------------------------------------------------------------------------
_RIB_STOPS = (VIOLET, BLUE, CYAN)


@functools.lru_cache(maxsize=1)
def _rib_cols():
    pts, s, _ = path()
    stops = np.array([K.hexlin(h) for h in _RIB_STOPS], np.float32)
    x = np.clip(s, 0, 1) * (len(stops) - 1)
    i = np.minimum(x.astype(int), len(stops) - 2)
    f = (x - i)[:, None]
    return stops[i] * (1 - f) + stops[i + 1] * f


def draw_ribbon(cv, c, t, s_head, opacity=1.0, width=34.0):
    if s_head <= 0.002 or opacity <= 0:
        return
    pts, s, _ = path()
    n = int(np.searchsorted(s, s_head))
    P = np.vstack([pts[:n], path_at(s_head)[None]])
    ss = np.r_[s[:n], s_head]
    cols = np.vstack([_rib_cols()[:n], _rib_cols()[min(n, len(s) - 1)][None]])
    xy, z = c.project(P)
    ok = np.isfinite(xy[:, 0]) & (z > 60)
    if ok.sum() < 2:
        return
    tw = np.cos(ss * 26.0 + t * 1.4)
    wpx = width * c.focal / np.maximum(z, 1.0) * (0.30 + 0.70 * np.abs(tw))
    d = np.gradient(xy, axis=0)
    nrm = np.c_[-d[:, 1], d[:, 0]]
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
    L = xy + nrm * wpx[:, None] / 2
    R = xy - nrm * wpx[:, None] / 2
    shade = (0.75 + 0.35 * tw)[:, None]
    fade = np.clip(ss / 0.03, 0, 1) * np.clip((s_head - ss) / 0.004 + 0.3, 0, 1)
    lay = np.zeros((K.H, K.W, 4), np.float32)
    SH = 4
    for j in range(len(P) - 1):
        if not (ok[j] and ok[j + 1]):
            continue
        q = np.array([L[j], L[j + 1], R[j + 1], R[j]])
        if q[:, 0].max() < -50 or q[:, 0].min() > K.W + 50 or q[:, 1].max() < -50 or q[:, 1].min() > K.H + 50:
            continue
        a = float(fade[j])
        col = cols[j] * shade[j] * a
        cv2.fillConvexPoly(lay, np.round(q * (1 << SH)).astype(np.int32),
                           (float(col[0]), float(col[1]), float(col[2]), a), lineType=cv2.LINE_AA, shift=SH)
    # soft tinted glow (quarter res), then the ribbon body, then a light core
    small = cv2.resize(lay, (K.W // 4, K.H // 4), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 7)
    glow = cv2.resize(small, (K.W, K.H), interpolation=cv2.INTER_LINEAR) * (0.55 * opacity)
    cv[..., :3] = cv[..., :3] * (1 - glow[..., 3:4]) + glow[..., :3]
    lay *= opacity
    cv[..., :3] = cv[..., :3] * (1 - lay[..., 3:4]) + lay[..., :3] * 1.18


def draw_far_glows(cv, c, t):
    A = assets()
    for k, (x, y, z, w, key, o) in enumerate(((-700, 1900, 2600, 2200, 'glow_v', 0.30),
                                              (800, 3100, 3000, 2400, 'glow_c', 0.30),
                                              (-600, 4300, 3400, 2600, 'glow_v', 0.26),
                                              (700, 5300, 3600, 3000, 'glow_c', 0.30),
                                              (-500, 300, 2400, 2000, 'glow_v', 0.22))):
        K.draw_billboard(cv, A[key], c, np.array([x, y, z], np.float64), w, opacity=o, dof=False)


# ---- copy (screen-locked text camera) ----------------------------------------------------------------
def word_in(t, tw):
    u = K.ramp(t, tw - 0.04, tw + 0.24, 'out_cubic')
    return K.ramp(t, tw - 0.04, tw + 0.10, 'linear'), 24.0 * (1 - u), 5.0 * (1 - u)


def slam(t, tw, s0=1.5):
    u = K.ramp(t, tw - 0.14, tw, 'in_cubic')
    sc = K.lerp(s0, 1.0, u) - damp(t, tw, 0.05, 7.0, 18.0)
    return K.ramp(t, tw - 0.14, tw - 0.07, 'linear'), sc, 8.0 * (1 - u)


def line(cv, words, total, times, cx, base, t, exit_op=1.0, dy=0.0):
    x0 = cx - total / 2
    for (spr, x), tw in zip(words, times):
        if t < tw - 0.05:
            continue
        op, rise, bl = word_in(t, tw)
        spr.draw(cv, x0 + x, base + rise + dy, anchor=(0.0, 1.0), opacity=op * exit_op, blur=bl)


def copy_hook(cv, t):
    A = assets()
    ex = 1 - K.ramp(t, T_WITH, T_WITH + 0.28, 'linear')
    if ex <= 0:
        return
    dy = -60.0 * K.ramp(t, T_WITH, T_WITH + 0.35, 'in_cubic')
    w, tot = A['l1']
    line(cv, w, tot, (T_WHAT, T_IF, T_THE, T_MARKET), 540, 310, t, ex, dy)
    if t >= T_CRASH - 0.15:
        op, sc, bl = slam(t, T_CRASH)
        A['crashes'].draw(cv, 540, 485 + dy, scale=sc, opacity=op * ex, blur=bl)
    if t >= T_OVER - 0.05:
        op, rise, bl = word_in(t, T_OVER)
        A['over'].draw(cv, 540, 712 + rise + dy, anchor=(0.5, 1.0), opacity=op * ex, blur=bl)


def copy_zero(cv, t):
    A = assets()
    if t < T_OKT1 - 0.1:
        return
    ex = 1 - K.ramp(t, MOVES[0][0] + 0.02, MOVES[0][0] + 0.30, 'linear')
    if ex <= 0:
        return
    dy = -50.0 * K.ramp(t, MOVES[0][0], MOVES[0][0] + 0.4, 'in_cubic')
    op, rise, bl = word_in(t, T_OKT1)
    A['with_'].draw(cv, 540, 300 + rise + dy, anchor=(0.5, 1.0), opacity=op * ex, blur=bl)
    w, tot = A['l2']
    line(cv, w, tot, (T_YOUR, T_ACC, T_CAN, T_NEVER), 540, 410, t, ex, dy)
    gw = A['gobelow'].w if hasattr(A['gobelow'], 'w') else 339.5
    zw = A['zero'].w
    x0 = 540 - (gw + 26 + zw) / 2
    if t >= T_GO - 0.05:
        op, rise, bl = word_in(t, T_GO)
        A['gobelow'].draw(cv, x0, 540 + rise + dy, anchor=(0.0, 1.0), opacity=op * ex, blur=bl)
    if t >= T_ZERO - 0.15:
        op, sc, bl = slam(t, T_ZERO)
        A['zero'].draw(cv, x0 + gw + 26 + zw / 2, 540 + dy, anchor=(0.5, 1.0), scale=sc, opacity=op * ex, blur=bl)


def copy_peace(cv, t):
    A = assets()
    if t < T_TRADE - 0.05:
        return
    ex = 1 - K.ramp(t, T_OKT2, T_OKT2 + 0.30, 'linear')
    if ex <= 0:
        return
    dy = -40.0 * K.ramp(t, T_OKT2, T_OKT2 + 0.4, 'in_cubic')
    op, rise, bl = word_in(t, T_TRADE)
    A['trade'].draw(cv, 540, 330 + rise + dy, anchor=(0.5, 1.0), opacity=op * ex, blur=bl)
    if t >= T_PEACE - 0.05:
        op, rise, bl = word_in(t, T_PEACE)
        A['peace'].draw(cv, 540, 480 + rise + dy, anchor=(0.5, 1.0), opacity=op * ex, blur=bl)


# ---- navy plate + end card ----------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def shield_screen_g():
    c = cam(T_OKT2, aperture=0)
    xy, _ = c.project(G[None])
    return float(xy[0][0]), float(xy[0][1])


@functools.lru_cache(maxsize=1)
def plate_track():
    sx, sy = shield_screen_g()
    return K.Track([(T_OKT2 - 0.02, (sx, sy, 60.0, 70.0, 60.0), 'out_cubic'),
                    (13.85, (540.0, 900.0, 500.0, 640.0, 120.0), 'inout_cubic'),
                    (T_FULL, (540.0, 960.0, 780.0, 1200.0, 110.0))])


@functools.lru_cache(maxsize=1)
def _grid():
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    return xx + 0.5, yy + 0.5


def plate_mask(t):
    cx, cy, hw, hh, r = (float(v) for v in plate_track()(t))
    X, Y = _grid()
    qx = np.abs(X - cx) - (hw - r)
    qy = np.abs(Y - cy) - (hh - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return np.clip(0.5 - d, 0, 1), d, (cx, cy, hw, hh, r)


def plate_fill():
    return _plate_fill()


@functools.lru_cache(maxsize=1)
def _plate_fill():
    y = np.linspace(0, 1, K.H, dtype=np.float32)[:, None, None]
    top, bot = K.hexlin('#0C1233'), K.hexlin('#07091A')
    col = top * (1 - y) + bot * y
    out = np.broadcast_to(col, (K.H, K.W, 3)).copy()
    yy, xx = np.mgrid[0:K.H, 0:K.W].astype(np.float32)
    rr = np.sqrt(((xx - 900) / 700) ** 2 + ((yy - 1750) / 600) ** 2)
    out += (np.clip(1 - rr, 0, 1) ** 2)[..., None] * K.hexlin(VIOLET) * 0.10
    return out


def _mark_geom():
    lg = assets()['logo']
    lh, lw = lg.shape[:2]
    mk = 244 / 1102 * lw
    return LOGO_C[0] - lw / 2 + mk / 2, LOGO_C[1], min(mk, lh) * 0.47


LOGO_C = (540.0, 700.0)
BTN_C = (540.0, 1065.0)


@functools.lru_cache(maxsize=1)
def _okt_bbox():
    a = S3.get('okt_mark', 'night', mode='anim')
    return K.alpha_bbox(a.frame(a.n - 1))


@functools.lru_cache(maxsize=4)
def _feather(h, w, f=44):
    y = np.minimum(np.arange(h), np.arange(h)[::-1]).astype(np.float32)
    x = np.minimum(np.arange(w), np.arange(w)[::-1]).astype(np.float32)
    m = np.clip(y[:, None] / f, 0, 1) * np.clip(x[None, :] / f, 0, 1)
    return (m * m * (3 - 2 * m))[..., None]


def plate_content(lay, c, t):
    A = assets()
    sx, sy = shield_screen_g()
    # the shield sinks into the plate
    if t < T_OKT2 + 0.6:
        k = K.ramp(t, T_OKT2, T_OKT2 + 0.55, 'inout_sine')
        draw_shield(lay, c, t, P=G.copy(), width=440.0 * K.lerp(1.0, 0.55, k), opacity=1 - k)
    # okt mark: swirl in at the shield, rise to y 640, then glide into the logo's mark slot
    mx, my, mr = _mark_geom()
    rise = K.ramp(t, T_OKT2 + 0.15, 13.95, 'inout_cubic')
    glide = K.ramp(t, 15.00, 15.62, 'inout_cubic')
    cx = K.lerp(K.lerp(sx, 540.0, rise), mx, glide)
    cy = K.lerp(K.lerp(sy, 640.0, rise), my, glide)
    r = K.lerp(K.lerp(130.0, 165.0, rise), mr, glide)
    sph = 1 - K.ramp(t, 15.55, 15.85, 'inout_sine')
    if sph > 0.002:
        if have3d('okt_mark', 'night_anim'):
            a = S3.get('okt_mark', 'night', mode='anim')
            spr = a.at_time(max(0.0, (t - T_OKT2) * 1.15), loop=False)
            x0, y0, x1, y1 = _okt_bbox()
            sc = 2 * r / max(1.0, (y1 - y0))
            K.draw(lay, spr, cx, cy, scale=sc, opacity=sph,
                   anchor=((x0 + x1) / 2 / spr.shape[1], (y0 + y1) / 2 / spr.shape[0]))
        else:
            asm = K.ramp(t, T_OKT2, T_OKT2 + 1.3, 'out_cubic')
            OK.dot_sphere(lay, K.Cam(aperture=0), (cx - K.CX, cy - K.CY, 0.0), r, t, assemble=K.lerp(0.4, 1, asm),
                          look='neon', opacity=sph * K.ramp(t, T_OKT2, T_OKT2 + 0.3, 'linear'), dof=False)
            label('okt_mark placeholder').draw(lay, cx, cy + r + 30, opacity=0.55 * sph)
    # "Trade With Confidence"
    if T_TWC - 0.05 <= t <= 15.3:
        ex = 1 - K.ramp(t, 14.95, 15.22, 'linear')
        dy = -50.0 * K.ramp(t, 14.95, 15.3, 'in_cubic')
        op, rise_, bl = word_in(t, T_TWC)
        A['twith'].draw(lay, 540, 1060 + rise_ + dy, anchor=(0.5, 1.0), opacity=op * ex, blur=bl)
        if t >= T_CONF - 0.15:
            op, sc, bl = slam(t, T_CONF, 1.4)
            A['conf'].draw(lay, 540, 1250 + dy, anchor=(0.5, 1.0), scale=sc, opacity=op * ex, blur=bl)
    # flat logo
    lg = A['logo']
    lh, lw = lg.shape[:2]
    x0 = LOGO_C[0] - lw / 2
    mo = K.ramp(t, 15.55, 15.85, 'inout_sine')
    if mo > 0:
        K.draw(lay, A['logo_mark'], x0, LOGO_C[1], anchor=(0.0, 0.5), opacity=mo)
    wu = K.ramp(t, 15.40, 15.85, 'inout_cubic')
    if wu > 0:
        wd = A['logo_word']
        ww = wd.shape[1]
        edge = wu * (ww + 80)
        m = np.clip((edge - np.arange(ww, dtype=np.float32)) / 80.0, 0, 1)
        K.draw(lay, wd * m[None, :, None], x0 + A['logo_mark'].shape[1], LOGO_C[1], anchor=(0.0, 0.5),
               blur=4 * (1 - wu))
    # CTA
    if t >= T_CTA - 0.03:
        b = K.spring(t - (T_CTA - 0.03), freq=2.6, damping=0.5)
        hv = K.ramp(t, T_CLICK - 0.35, T_CLICK - 0.1, 'inout_sine')
        pr = K.impulse(t, T_CLICK, 9) if t >= T_CLICK - 0.02 else 0.0
        btn = ui.button(COPY['cta'], hover=hv, press=pr, ripple=(t - T_CLICK) if t >= T_CLICK else None, look='neon')
        btn = btn * _feather(*btn.shape[:2])
        ui.place(lay, btn, BTN_C[0], BTN_C[1], scale=K.lerp(0.7, 1.0, b),
                 opacity=K.ramp(t, T_CTA - 0.03, T_CTA + 0.10, 'linear'))
    if t >= T_RISK:
        o = K.ramp(t, T_RISK, T_RISK + 0.5, 'inout_sine')
        A['risk'][0].draw(lay, 540, 1320, opacity=o)
        A['risk'][1].draw(lay, 540, 1364, opacity=o)
    if t >= T_URL - 0.03:
        u = K.ramp(t, T_URL - 0.03, T_URL + 0.25, 'out_cubic')
        A['url'].draw(lay, 540, 1212 + 16 * (1 - u), opacity=u)
    if T_CTA + 0.05 <= t <= 16.25:
        p = K.Track([(T_CTA + 0.05, (900.0, 1640.0)), (15.66, (612.0, 1088.0), 'out_cubic'),
                     (15.92, (612.0, 1088.0), 'in_cubic'), (16.25, (960.0, 1700.0))], ease='out_cubic')(t)
        op = K.ramp(t, T_CTA + 0.05, T_CTA + 0.2, 'linear') * (1 - K.ramp(t, 15.95, 16.20, 'linear'))
        ui.draw_cursor(lay, p[0], p[1], 'hand', 84, press=K.impulse(t, T_CLICK, 9) if t >= T_CLICK - 0.02 else 0.0,
                       click=(t - T_CLICK) if t >= T_CLICK else None, look='neon', opacity=op)


def draw_plate(cv, c, t):
    full = t >= T_FULL + 0.02
    if full:
        m = None
        cv[..., :3] = plate_fill()
    else:
        m, d, (cx, cy, hw, hh, r) = plate_mask(t)
        # tinted soft shadow on the page
        sm = cv2.resize(m, (K.W // 8, K.H // 8), interpolation=cv2.INTER_AREA)
        sm = cv2.GaussianBlur(sm, (0, 0), 4 + 0.02 * hw)
        sh = cv2.resize(sm, (K.W, K.H), interpolation=cv2.INTER_LINEAR)
        sh = np.roll(sh, int(18 + 0.03 * hh), axis=0)[..., None] * 0.30
        cv[..., :3] = cv[..., :3] * (1 - sh) + K.hexlin('#1A2050') * sh
        mm = m[..., None]
        cv[..., :3] = cv[..., :3] * (1 - mm) + plate_fill() * mm
        rim = np.clip(1.6 - np.abs(d + 1.2), 0, 1)[..., None] * 0.55
        cv[..., :3] += K.hexlin(CYAN) * rim * (1 - K.ramp(t, 14.2, T_FULL, 'linear'))
    lay = np.zeros_like(cv)
    plate_content(lay, c, t)
    if m is not None:
        lay *= m[..., None]
    cv[..., :3] = cv[..., :3] * (1 - lay[..., 3:4]) + lay[..., :3]


# =================================================================================================== frame
def draw(t):
    c = cam(t)
    if t >= T_FULL + 0.02:
        cv = np.zeros((K.H, K.W, 4), np.float32)
        cv[..., 3] = 1.0
        draw_plate(cv, c, t)
        return cv
    cv = K.background(LOOK, t, c, parallax=0.35)
    draw_far_glows(cv, c, t)
    draw_chart(cv, c, t)
    if t >= MOVES[0][0]:
        st = shield_track()(t)
        draw_ribbon(cv, c, t, st, opacity=1.0 - 0.35 * K.ramp(t, GATHER[0], GATHER[1], 'inout_sine'))
    items = []
    if t <= 6.4:
        items.append((c.depth((0.0, CNT_Y(t), 0.0)), lambda: draw_counter(cv, c, t)))
    if T_ZERO - 0.22 <= t < T_OKT2 + 0.02:
        P = shield_pos(t)
        items.append((c.depth(P) - 40.0, lambda: draw_shield(cv, c, t)))
    for i in range(4):
        st_ = card_state(i, t)
        if st_ is not None:
            items.append((c.depth(st_[0]), (lambda i=i: draw_card(cv, c, t, i))))
    items.sort(key=lambda q: -q[0])
    for _, fn in items:
        fn()
    draw_candle(cv, c, t)
    copy_hook(cv, t)
    copy_zero(cv, t)
    copy_peace(cv, t)
    if t >= T_OKT2 - 0.02:
        draw_plate(cv, c, t)
    return cv


def post(cv, t):
    push = 0.35 * K.impulse(t, T_CRASH - 0.02, 14) * (t >= T_CRASH - 0.04) \
        + 0.25 * K.impulse(t, T_ZERO - 0.02, 14) * (t >= T_ZERO - 0.04)
    L = K.LOOKS[LOOK]
    return K.post(cv, LOOK, t, exposure=L['exposure'] + push, bloom=L['bloom'] * (1 + 0.6 * push))


def samples(t):
    if t < 2.15:
        return 7
    if any(a - 0.05 <= t <= b + 0.1 for a, b in MOVES):
        return 9                      # shield peaks ~67 px/frame
    if T_WITH <= t <= 3.8 or T_ZERO - 0.22 <= t <= T_ZERO + 0.25:
        return 5
    if GATHER[0] <= t <= GATHER[1] + 0.1 or T_OKT2 <= t <= 13.95:
        return 6
    if T_CTA - 0.05 <= t <= 16.35 or T_CONF - 0.15 <= t <= T_CONF + 0.2 or 14.95 <= t <= 15.65:
        return 5
    return 3


from reel3_sfx import cues, BED, BED_GAIN_DB  # noqa: E402,F401  (sound designer owns the cue sheet)
