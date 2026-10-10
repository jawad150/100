"""reel2 "Blink" (Oktrum, 1080x1920, 30 fps): DUR 21.5 s, LOOK 'cine', BPM 120 (beat 0.5 s). BRIEF.md §6.2 / §10.

Cinematic navy hybrid: low-key backdrop (K.background('cine', intensity ~0.3): the light comes from rays and
streaks, not the backdrop), film grain, anamorphic flares, giant Instrument Serif Italic words paired with small
Inter Tight, glass trading UI. Every key word is pinned to its VO word onset (reel2_vo.json phrases, word onsets
read from the waveform valleys of <WS>/audio/reel2_vo.wav; VO starts at 0.20 s).

VO word onsets used (s): Blink 0.24 · already 1.80 · moved 2.24 · "In trading" 2.90 · Every 3.88 ·
millisecond 4.20 · counts 4.92 · "Oktrum runs" 5.73 · ultra-low latency 6.50 · instant order filling 8.45 ·
"on MetaTrader 5" 10.07 (MetaTrader 10.25) · Eliminate 11.60 · lag 12.10 · seize 12.91-13.04 · CTA "Open" 15.15 ·
oktrum (dot com) 16.40.

Shot list as built (t in s, beat = t / 0.5):
 A 0.00-3.00 (b0-6)   HOOK. Macro candle chart on a tilted glass plane (DOF), light rays from top right, slow
                      push-in. Giant serif "Blink." racks into focus 0.00-0.24 (sharp on the word). The eyelids
                      (OK.blink) close 0.62-0.94, hold shut 0.94-1.04 (a cyan anamorphic flare on the lid seam at
                      0.98), reopen 1.04-1.42. While shut: "Blink." is gone, a new candle jumps up and the price
                      tag 67,200 becomes 67,420 ▲ (UP) with an anamorphic streak; focus racks from the word plane to
                      the chart 1.15-1.70. "already" 1.80, "*moved.*" 2.24 (serif, focus pull).  Hard cut 3.00.
 B 3.00-5.50 (b6-11)  THE HIT. Glass candles (candles3d night yaw) whip past the lens 3.00-3.45 (7 samples), a far
                      cluster drifts in the DOF haze, light rays from the top, blurred racing mono digits (never
                      legible). "Every" 3.88, "*millisecond*" 4.20 (serif, focus pull), "counts." 4.92. Cut 5.50.
 C 5.50-11.50 (b11-23) Tilted glass trade_window BTC/USD in 3D, camera dollies in (5.50-7.0) and orbits slowly;
                      chips "Ultra-low latency" 6.50 and "Instant order filling" 8.45 on a nearer plane (rack focus
                      to them, back to the window 8.85-9.20). Hand cursor enters 8.75, hovers BUY 9.10, presses
                      BUY 9.50; a cyan light pulse runs from the button out of frame (9.50-9.64) and back down to
                      the toast; order_toast "Order Filled — BUY 0.5 BTC @ 67,200" 9.75. Chips leave 9.80-10.05,
                      "Powered by / MetaTrader 5" 10.10. Anamorphic pass tamed here (hovered BUY). Hard cut 11.50.
 D 11.50-14.50 (b23-29) line_chart draws up 11.55-13.70 with a streak + rays on its head, push-in with a slight
                      roll. "Eliminate" 11.60, "*lag.*" slams 12.10 (spring, judder, light sweep 12.45-13.25),
                      "Seize every / *opportunity.*" 13.00. Whip pan (screen-space, 7 samples) 14.30-14.70, peak 14.50.
 E 14.50-21.50 (b29-43) End card on navy: the okt_mark (3D dot sphere) assembles at frame centre, glides 15.45-16.00
                      into the flat logo's mark slot while the wordmark wipes in 15.70-16.15 and the sphere
                      crossfades into logo_full (640 px wide) 15.95-16.25. Button "Open Live Account" springs in
                      15.15; hand cursor presses it 15.75 (beat 31.5); "oktrum.com" 16.40; risk line (30 px, two
                      lines) 15.40. Cyan streak drifts BELOW the logo, never on it. Settled 16.65-21.50 (4.85 s).

Placeholders (switch automatically when <WS>/assets3d/<name>/<variant>/meta.json exists):
  candles3d/night  -> 2D glass-candle cluster sprite labelled "candles3d placeholder" (same billboards, same path)
  okt_mark/night_anim -> OK.dot_sphere (the logo mark is a halftone dot sphere) labelled "okt_mark placeholder"

SFX (draft, cues()): heartbeat x2 0.0, flash_hit 0.98 (lid seam), ui_tick 1.04 (price tick), whoosh_slow 1.30,
riser -> 3.0, sub_drop + impact_soft 3.0, whoosh_by 3.05 (panned), glass_tap 6.50 / 8.45, ui_hover 9.10, ui_click
9.50, whoosh_fast 9.57 (pulse), check_ding 9.75, toast_chime 9.80, glass_tap 10.10, sub_drop 11.50, impact_big
12.10, shimmer 12.45, swish_small 13.0, whip 14.50, logo_sting 14.62, pop 15.15, ui_click + toggle_on 15.75,
shimmer 16.0.
"""
import oktrum_kit as OK                       # first: applies the Oktrum profile
import functools, json, math, os
import numpy as np
import cv2
import core as K, type3d as T, ui, sprites3d as S3

DUR, LOOK, BPM = 21.5, 'cine', 120
BEAT = 60.0 / BPM
HALF = 0.5 / K.FPS

_VO = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reel2_vo.json')))
PH = [p['t0'] for p in _VO['phrases']]        # phrase onsets (edit time)

# ---- times (s) -------------------------------------------------------------------------------------------------
T_BLINK = PH[0]                                # 0.24 "Blink"
BL0, BL1 = 0.62, 1.42                          # eyelid blink window (shut 0.94-1.04)
T_SWAP = BL0 + 0.46 * (BL1 - BL0)              # 0.988: price ticks / word leaves behind the shut lids
T_ALREADY, T_MOVED = 1.80, 2.24
CUT_B = 3.0                                    # the hit (beat 6)
T_EVERY, T_MILLI, T_COUNTS = PH[3], 4.20, 4.92
CUT_C = 5.5                                    # beat 11, just before "Oktrum runs" 5.73
T_CHIP1, T_CHIP2 = 6.50, 8.45
T_HOVER, T_PRESS, T_TOAST = 9.10, 9.50, 9.75
T_MT5 = 10.10                                  # "on MetaTrader 5" 10.07
CUT_D = 11.5                                   # beat 23
T_ELIM, T_LAG, T_SEIZE = PH[6], 12.10, 13.00
WHIP = 14.5                                    # beat 29: whip pan peak, end card starts
WH0, WH1 = 14.30, 14.70
T_CTA = PH[8]                                  # 15.15 "Open your live account"
T_CLICK = 15.75                                # beat 31.5
T_URL = 16.40                                  # "oktrum dot com"
T_RISK = 15.40

COPY = dict(cta='Open Live Account', url='oktrum.com',
            risk=('Trading involves high risk.', 'You could lose some or all of your investment.'),
            toast='Order Filled — BUY 0.5 BTC @ 67,200', chip1='Ultra-low latency', chip2='Instant order filling')

UP_HEX = '#34D399'
D0 = 1500.0                                    # default camera distance (z=0 plane is 1 px per unit)


def wp(sx, sy, z):
    """World point that the default camera sees at screen (sx, sy) at world depth z, and its px scale."""
    k = (D0 + z) / D0
    return (sx - K.CX) * k, (sy - K.CY) * k, z


@functools.lru_cache(maxsize=1)
def _low_key():
    """Multiplier that pulls the cine backdrop's blue top (and the bottom) down to a low-key navy."""
    y = np.arange(K.H, dtype=np.float32)
    top = 0.30 + 0.70 * np.clip(y / 760.0, 0, 1) ** 1.4
    bot = 1.0 - 0.35 * np.clip((y - 1400) / 520.0, 0, 1) ** 2
    m = np.ones((K.H, 1, 4), np.float32)
    m[:, 0, :3] = (top * bot)[:, None]
    return m


def backdrop(t, cam, intensity=0.2):
    cv = K.background(LOOK, t, cam, intensity=intensity)
    cv *= _low_key()
    return cv


def have3d(name, folder):
    return os.path.exists(os.path.join(K.ASSETS3D, name, folder, 'meta.json'))


def sans(text, px, font=None, fill='IVORY', tracking=0.0):
    return T.render(text, 'flat', font=font or OK.FONT_HEAD, px=px, fill=fill, tracking=tracking)


def serif(text, px, fill='IVORY'):
    return T.render(text, 'serif_italic', px=px, fill=fill)


def _tri(size, color):
    s = int(size)
    a = np.zeros((s * 4, s * 4), np.uint8)
    pts = np.array([[s * 2, 0], [s * 4, s * 4 - 1], [0, s * 4 - 1]], np.int32)
    pts[:, 1] = (pts[:, 1] * 0.86).astype(np.int32) + int(s * 0.28)
    cv2.fillPoly(a, [pts], 255, lineType=cv2.LINE_AA)
    a = cv2.resize(a, (s, s), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    spr = np.zeros((s, s, 4), np.float32)
    spr[..., :3] = a[..., None] * np.asarray(color, np.float32)
    spr[..., 3] = a
    return spr


def _candle_cluster(w=620, h=760, seed=3):
    """Stand-in for candles3d/night: three glass candles (UP, DOWN, UP) with wicks, emissive rims, label."""
    S = 2
    img = np.zeros((h * S, w * S, 4), np.float32)
    up, dn = K.hexlin(UP_HEX), K.hexlin('#F87171')
    specs = [(0.22, 0.30, 0.78, up), (0.50, 0.12, 0.62, dn), (0.78, 0.22, 0.92, up)]
    for cx, top, bot, colr in specs:
        bw = int(0.17 * w * S)
        x0 = int(cx * w * S - bw / 2)
        y0, y1 = int(top * h * S + 0.08 * h * S), int(bot * h * S - 0.08 * h * S)
        wx = int(cx * w * S)
        img[int(top * h * S):int(bot * h * S), wx - 3 * S:wx + 3 * S, :3] = colr * 0.9
        img[int(top * h * S):int(bot * h * S), wx - 3 * S:wx + 3 * S, 3] = 0.9
        m = np.zeros((h * S, w * S), np.uint8)
        cv2.rectangle(m, (x0, y0), (x0 + bw, y1), 255, -1, cv2.LINE_AA)
        a = m.astype(np.float32) / 255.0
        grad = np.linspace(0.55, 0.25, h * S, dtype=np.float32)[:, None]
        body = a * grad
        rim = np.zeros_like(m)
        cv2.rectangle(rim, (x0, y0), (x0 + bw, y1), 255, 3 * S, cv2.LINE_AA)
        r = rim.astype(np.float32) / 255.0
        for c in range(3):
            img[..., c] = img[..., c] * (1 - body) + body * colr[c] * 0.6 + r * colr[c] * 1.6
        img[..., 3] = np.maximum(img[..., 3], np.maximum(body, r))
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    img = K.glow(img, None, (6, 18), 0.5)
    lab = T.render('candles3d placeholder', 'flat', font=OK.FONT_MONO, px=22, fill='IVORY')
    lab.draw(img, img.shape[1] / 2, img.shape[0] - 30, opacity=0.6)
    return img


@functools.lru_cache(maxsize=1)
def assets():
    rng = np.random.default_rng(5)
    strips = []
    for k in range(6):
        s = '  '.join(''.join(str(d) for d in rng.integers(0, 10, 6)) for _ in range(9))
        strips.append(T.render(s, 'flat', font=OK.FONT_MONO_BOLD, px=58, fill=('CYAN', 0.9)).sprite)
    logo = K.load_image(os.path.join(K.BRAND, 'logo_full.png'), size=640)
    lh, lw = logo.shape[:2]
    mk = int(round(244 / 1102 * lw))
    logo_mark = np.ascontiguousarray(logo[:, :mk + 2])
    logo_word = np.ascontiguousarray(logo[:, mk + 2:])
    return dict(
        blink=serif('Blink.', 340),
        btc=sans('BTC / USD', 34, OK.FONT_UI, fill=('IVORY', 0.75), tracking=0.12),
        p0=T.render('67,200', 'mono', font=OK.FONT_MONO_BOLD, px=118, fill='IVORY'),
        p1=T.render('67,420', 'mono', font=OK.FONT_MONO_BOLD, px=118, fill=UP_HEX),
        tri=_tri(56, K.hexlin(UP_HEX) * 1.15),
        already=sans('already', 66, tracking=0.06),
        moved=serif('moved.', 290),
        every=sans('Every', 78, tracking=0.04),
        milli=serif('millisecond', 205),
        counts=sans('counts.', 78, tracking=0.04),
        strips=strips,
        cluster=_candle_cluster(),
        chip1=ui.chip(COPY['chip1'], 1.0, look=LOOK, size=40, h=84, icon_name=None),
        chip1g=ui.chip(COPY['chip1'], 0.0, look=LOOK, size=40, h=84),
        chip2=ui.chip(COPY['chip2'], 1.0, look=LOOK, size=40, h=84),
        chip2g=ui.chip(COPY['chip2'], 0.0, look=LOOK, size=40, h=84),
        powered=sans('Powered by', 42, OK.FONT_UI, fill=('IVORY', 0.78), tracking=0.06),
        mt5=sans('MetaTrader 5', 104),
        toast=OK.order_toast(COPY['toast'], LOOK, w=720),
        elim=sans('Eliminate', 104, tracking=0.01),
        lag=serif('lag.', 300),
        seize=sans('Seize every', 64, tracking=0.04),
        opp=serif('opportunity.', 158),
        pool=K.radial(1100, K.hexlin('#07091A') * 0.6),
        dotglow=K.radial(160, K.C['CYAN'] * 1.6),
        logo=logo, logo_mark=logo_mark, logo_word=logo_word,
        url=sans(COPY['url'], 46, OK.FONT_UI, tracking=0.02),
        risk=[sans(s, 30, OK.FONT_BODY, fill=('IVORY', 0.72)) for s in COPY['risk']],
        mark_label=T.render('okt_mark placeholder', 'flat', font=OK.FONT_MONO, px=22, fill='IVORY'),
        dust=K.Particles(70, seed=9, bright=0.5),
    )


def prewarm():
    assets()
    OK.trade_window(look=LOOK)


# =================================================================================================== shot A
CH_A = dict(center=(-30.0, 330.0, 260.0), width=1180.0, rot=(18.0, -10.0, 0.0))


def cam_a(t):
    u = K.ramp(t, 0.0, 3.0, 'inout_sine')
    z = K.lerp(-1500, -1330, u)
    x = K.lerp(-30, 25, u) + K.wiggle(t, 0.35, 3.0, seed=2)
    y = K.lerp(-10, 15, u) + K.wiggle(t, 0.3, 2.0, seed=5)
    d_word = (-150.0) - z                      # word plane z=-150
    d_chart = 230.0 - z
    fd = K.lerp(d_word, d_chart, K.ramp(t, 1.15, 1.70, 'inout_sine'))
    return K.Cam(pos=(x, y, z), roll=K.lerp(-1.2, 0.4, u), aperture=30, focus_dist=fd)


def chart_a(t):
    prog = 29.0 / 30.0 if t < T_SWAP else 1.0
    spr, inf = OK.candles(30, 1000, 620, prog, t, seed=8, look=LOOK, axis=False, trend=0.5, vol=0.0045,
                          price=67200.0, info=True, tick=0.6)
    return spr, inf


def shot_a(t):
    A = assets()
    cam = cam_a(t)
    cv = backdrop(t, cam, 0.2)
    OK.light_rays(cv, (900, 210), 0.42 + 0.06 * math.sin(t * 1.3), t, angle=118, cone=80, length=1300)
    spr, inf = chart_a(t)
    c = CH_A
    K.draw_plane(cv, spr, cam, c['center'], c['width'], rot=c['rot'])
    # head of the chart (newest candle) on screen: glow + streak
    sh, sw_ = spr.shape[:2]
    lx, ly = inf['last']
    P = K.plane_point(c['center'], c['width'], c['width'] * sh / sw_, c['rot'], (lx / sw_, ly / sh))
    hxy = cam.project(np.array([P]))[0][0]
    jump = K.impulse(t, T_SWAP + 0.06, 3.5) if t >= T_SWAP else 0.0
    K.draw(cv, A['dotglow'], hxy[0], hxy[1], scale=1.0 + 0.8 * jump, opacity=0.55 + 0.45 * jump, mode='add')
    OK.streaks(cv, [(hxy[0], hxy[1], 1.0)], strength=0.35 + 0.65 * jump, length=520, thickness=5)
    # "Blink." on its own plane (rack focus), gone behind the shut lids
    if t < T_SWAP:
        u = K.ramp(t, 0.0, T_BLINK, 'out_cubic')
        drift = K.ramp(t, T_BLINK, 1.0, 'linear')
        x, y, z = wp(540, 560, -150)
        A['blink'].draw_plane(cv, cam, (x, y, z), scale=(D0 - 150) / D0 * K.lerp(1.10, 1.0, u) * (1 + 0.025 * drift),
                              opacity=K.lerp(0.7, 1.0, u), blur=10 * (1 - u))
    # price block (2D, screen-locked: the info the eye reads after the blink)
    py = 905
    A['btc'].draw(cv, 92, 812, anchor=(0.0, 0.5), opacity=0.85)
    if t < T_SWAP:
        A['p0'].draw(cv, 88, py, anchor=(0.0, 0.5))
    else:
        k = K.ramp(t, T_SWAP, T_SWAP + 0.5, 'out_cubic')
        A['p1'].draw(cv, 88, py, anchor=(0.0, 0.5))
        K.draw(cv, A['tri'], 88 + 440 + 22, py - 4, opacity=1.0)
        OK.streaks(cv, [(330, py, 1.0)], strength=0.85 * K.impulse(t, BL1 - 0.25, 2.6) + 0.12, length=700,
                   thickness=6, color=K.hexlin(UP_HEX) * 0.9 + K.C['CYAN'] * 0.3)
    # "already moved."
    if t >= T_ALREADY - 0.02:
        u = K.ramp(t, T_ALREADY - 0.02, T_ALREADY + 0.30, 'out_cubic')
        A['already'].draw(cv, 540, 468 + 26 * (1 - u), opacity=u)
    if t >= T_MOVED - 0.04:
        u = K.ramp(t, T_MOVED - 0.04, T_MOVED + 0.22, 'out_cubic')
        A['moved'].draw(cv, 540, 610, scale=K.lerp(1.08, 1.0, u), opacity=K.ramp(t, T_MOVED - 0.04, T_MOVED + 0.06,
                        'linear'), blur=9 * (1 - u))
    # eyelids + a cyan anamorphic flare on the shut seam
    OK.blink(cv, K.remap(t, BL0, BL1))
    fl = K.impulse(t, T_SWAP - 0.01, 9) if t > BL0 + 0.25 else 0.0
    if fl > 0.01:
        OK.streaks(cv, [(540, 0.55 * K.H, 1.0)], strength=0.9 * fl, length=980, thickness=6)
    return cv


# =================================================================================================== shot B
FLY = [  # x, y, z at CUT_B, width, yaw, speed (units/s)
    (-430, -260, 500, 900, -18, 5200),
    (520, 380, 900, 1000, 22, 5600),
    (-120, 640, 1500, 900, 8, 6200),
    (380, -620, 2100, 800, -10, 6400),
]
FAR = [(-360, -420, 2600, 900, 12), (420, 520, 3000, 1000, -16), (40, 60, 3600, 1100, 4)]


def cam_b(t):
    u = K.ramp(t, CUT_B, CUT_C, 'out_cubic')
    return K.Cam(pos=(K.wiggle(t, 0.5, 4, seed=3), K.wiggle(t, 0.4, 3, seed=4), K.lerp(-1500, -1400, u)),
                 roll=K.lerp(-2.0, 0.0, u), aperture=42, focus_dist=1500.0)


def _cluster_spr(yaw):
    if have3d('candles3d', 'night'):
        return S3.get('candles3d', 'night').at_yaw(yaw)
    return assets()['cluster']


def shot_b(t):
    A = assets()
    cam = cam_b(t)
    cv = backdrop(t, cam, 0.18)
    OK.light_rays(cv, (540, 40), 0.30 + 0.35 * K.impulse(t, CUT_B, 2.2), t, angle=90, cone=75, length=1500)
    # racing digits: a fast horizontal smear, never legible
    for yy, op, sp, k0 in ((1290, 0.22, 5200, 0), (585, 0.12, -4300, 3)):
        lay = np.zeros((170, K.W, 4), np.float32)
        s = A['strips'][(int(t * K.FPS) + k0) % 6]
        off = (t * sp) % (s.shape[1] * 0.5)
        K.draw(lay, s, K.W / 2 - off + s.shape[1] * 0.25, 85)
        lay = cv2.blur(lay, (151, 1))
        lay = cv2.blur(lay, (75, 1))
        lay = cv2.GaussianBlur(lay, (0, 0), sigmaX=2, sigmaY=9)
        K.draw(cv, lay, K.CX, yy, opacity=op, mode='add')
    sc = K.Scene(cam)
    dt = t - CUT_B
    for x, y, z, w, yaw in FAR:
        sc.billboard(_cluster_spr(yaw + 6 * dt), (x, y, z - 160 * dt), w, opacity=0.8)
    for i, (x, y, z, w, yaw, v) in enumerate(FLY):
        zz = z - v * dt
        if zz > -1380 + 60:
            sc.billboard(_cluster_spr(yaw + 40 * dt), (x * (1 + 0.15 * dt), y, zz), w)
    sc.render(cv)
    # dark pool behind the copy so the far candles never fight the words
    K.draw(cv, A['pool'], 540, 935, scale=(1.0, 0.55), opacity=K.ramp(t, T_EVERY - 0.3, T_EVERY + 0.2, 'inout_sine'))
    # copy (2D, crisp)
    if t >= T_EVERY - 0.03:
        u = K.ramp(t, T_EVERY - 0.03, T_EVERY + 0.28, 'out_cubic')
        A['every'].draw(cv, 540, 770 + 22 * (1 - u), opacity=u)
    if t >= T_MILLI - 0.04:
        u = K.ramp(t, T_MILLI - 0.04, T_MILLI + 0.22, 'out_cubic')
        A['milli'].draw(cv, 540, 935, scale=K.lerp(1.07, 1.0, u),
                        opacity=K.ramp(t, T_MILLI - 0.04, T_MILLI + 0.06, 'linear'), blur=10 * (1 - u))
    if t >= T_COUNTS - 0.03:
        u = K.ramp(t, T_COUNTS - 0.03, T_COUNTS + 0.28, 'out_cubic')
        A['counts'].draw(cv, 540, 1095 + 22 * (1 - u), opacity=u)
    return cv


# =================================================================================================== shot C
WIN_P, WIN_W, WIN_R = (0.0, -10.0, 0.0), 760.0, (7.0, -13.0, 0.0)
CHIP_Z = -240.0


def cam_c(t):
    u = K.ramp(t, CUT_C, 7.0, 'out_quart')
    v = K.ramp(t, CUT_C, CUT_D, 'easy_ease')
    dist = K.lerp(1900, 1520, u) - 70 * v
    yaw = K.lerp(10, -5, v)
    fd_chip = dist + CHIP_Z
    rk = K.ramp(t, T_CHIP1 - 0.05, T_CHIP1 + 0.30, 'inout_sine') * (1 - K.ramp(t, 8.85, 9.20, 'inout_sine'))
    rk = max(rk, K.ramp(t, T_MT5 - 0.05, T_MT5 + 0.35, 'inout_sine'))
    fd = K.lerp(dist, fd_chip, rk)
    return K.Cam.orbit((0, -10, 0), dist, yaw=yaw, pitch=K.lerp(4, 1, v), roll=K.lerp(-1.5, 0.5, v),
                       aperture=34, focus_dist=fd)


def _pulse_path(s, bxy):
    """Light pulse: button -> out of frame top right -> back to the toast. s in 0..1."""
    out = np.array([1180.0, -140.0])
    toast = np.array([540.0, 1335.0])
    if s < 0.5:
        return bxy + (out - bxy) * (s / 0.5) ** 3
    q = (s - 0.5) / 0.5
    return out + (toast - out) * (1 - (1 - q) ** 3)


def shot_c(t):
    A = assets()
    cam = cam_c(t)
    cv = backdrop(t, cam, 0.2)
    OK.light_rays(cv, (130, 150), 0.30, t, angle=60, cone=70, length=1300, seed=3)
    hv = K.ramp(t, T_HOVER, T_HOVER + 0.25, 'inout_sine') * (1 - K.ramp(t, 10.1, 10.5, 'inout_sine'))
    pr = K.impulse(t, T_PRESS, 9) if t >= T_PRESS - 0.02 else 0.0
    win = OK.trade_window(look=LOOK, hover=hv, press=pr, chart='line')
    win.plane(cv, cam, WIN_P, WIN_W, rot=WIN_R)
    bx, by, bw, bh = win.meta['buy']
    bxy = np.array(win.screen(cam, WIN_P, WIN_W, WIN_R, bx + bw / 2, by + bh / 2), np.float64)
    # chips on a nearer plane (rack focus)
    for (key, t0, sy) in (('chip1', T_CHIP1, 300), ('chip2', T_CHIP2, 405)):
        if t < t0 - 0.03:
            continue
        a = K.ramp(t, t0 - 0.03, t0 + 0.12, 'linear') * (1 - K.ramp(t, 9.80, 10.05, 'in_cubic'))
        s = K.lerp(0.82, 1.0, K.spring(t - (t0 - 0.03), freq=2.6, damping=0.5))
        sel = K.ramp(t, t0 + 0.05, t0 + 0.45, 'inout_sine')
        spr = A[key] if sel >= 1 else A[key + 'g']
        x, y, z = wp(540, sy - 30 * K.ramp(t, 9.80, 10.05, 'in_cubic'), CHIP_Z)
        wd = spr.shape[1] * (D0 + CHIP_Z) / D0 * s
        K.draw_plane(cv, spr, cam, (x, y, z), wd, rot=(0, -6, 0), opacity=a)
        if 0 < sel < 1:
            K.draw_plane(cv, A[key], cam, (x, y, z), wd, rot=(0, -6, 0), opacity=a * sel)
    # Powered by MetaTrader 5
    if t >= T_MT5 - 0.03:
        u = K.ramp(t, T_MT5 - 0.03, T_MT5 + 0.30, 'out_cubic')
        k = (D0 + CHIP_Z) / D0
        A['powered'].draw_plane(cv, cam, wp(540, 318 + 18 * (1 - u), CHIP_Z), scale=k, opacity=u)
        A['mt5'].draw_plane(cv, cam, wp(540, 418 + 24 * (1 - u), CHIP_Z), scale=k,
                            opacity=K.ramp(t, T_MT5 + 0.02, T_MT5 + 0.25, 'linear'))
    # toast (closest plane)
    if t >= T_TOAST - 0.02:
        u = K.ramp(t, T_TOAST - 0.02, T_TOAST + 0.38, 'out_cubic')
        A['toast'].plane(cv, cam, wp(540, 1335 + 50 * (1 - u), -300), 720 * (D0 - 300) / D0, rot=(4, -8, 0),
                         opacity=K.ramp(t, T_TOAST - 0.02, T_TOAST + 0.15, 'linear'))
    # light pulse round trip
    if T_PRESS <= t <= T_TOAST + 0.12:
        s = K.clamp((t - T_PRESS) / (T_TOAST - T_PRESS))
        for j in range(8):
            sj = K.clamp(s - j * 0.025)
            p = _pulse_path(sj, bxy)
            K.draw(cv, A['dotglow'], p[0], p[1], scale=0.9 - j * 0.08, opacity=(1 - j / 8) * 0.9, mode='add')
    # cursor
    if 8.70 <= t <= 10.45:
        off = K.Track([(8.70, (430.0, 560.0)), (9.30, (14.0, 18.0), 'out_cubic'), (9.95, (14.0, 18.0), 'in_cubic'),
                       (10.45, (520.0, 620.0))], ease='out_cubic')(t)
        op = K.ramp(t, 8.70, 8.90, 'linear') * (1 - K.ramp(t, 10.15, 10.45, 'linear'))
        ui.draw_cursor(cv, bxy[0] + off[0], bxy[1] + off[1], 'hand', 84, press=pr,
                       click=(t - T_PRESS) if t >= T_PRESS else None, look=LOOK, opacity=op)
    return cv


# =================================================================================================== shot D
LC_P, LC_W, LC_R = (0.0, 90.0, 80.0), 1020.0, (12.0, -9.0, 0.0)
LC_VALUES = tuple(float(v) for v in (np.cumsum(np.random.default_rng(21).normal(0.45, 1.0, 44))
                                     + 3 * np.sin(np.linspace(0, 6, 44))))


def cam_d(t, whip=0.0):
    u = K.ramp(t, CUT_D, WHIP, 'inout_sine')
    return K.Cam(pos=(K.lerp(-20, 30, u), K.lerp(10, -10, u), K.lerp(-1500, -1360, u)),
                 roll=K.lerp(1.4, -0.8, u), aperture=26, focus_dist=1500.0)


def shot_d(t):
    A = assets()
    cam = cam_d(t)
    sh = 9 * K.impulse(t, T_LAG, 7) if t >= T_LAG else 0.0
    cv = backdrop(t, cam, 0.2)
    prog = K.lerp(0.22, 1.0, K.ramp(t, CUT_D, 13.70, 'inout_sine'))
    lc = OK.line_chart(940, 440, LC_VALUES, prog, LOOK)
    K.draw_plane(cv, lc, cam, LC_P, LC_W, rot=LC_R)
    # head of the line (approx: x by progress, y by value)
    v = np.asarray(LC_VALUES)
    xi = prog * (len(v) - 1)
    yv = np.interp(xi, np.arange(len(v)), v)
    hu = (OK.PAD + prog * 940) / (940 + 2 * OK.PAD)
    hv = (OK.PAD + (v.max() - yv) / (v.max() - v.min()) * 440) / (440 + 2 * OK.PAD)
    lh = LC_W * (440 + 2 * OK.PAD) / (940 + 2 * OK.PAD)
    hxy = cam.project(np.array([K.plane_point(LC_P, LC_W, lh, LC_R, (hu, hv))]))[0][0]
    if prog > 0.01:
        OK.light_rays(cv, tuple(hxy), 0.16, t, angle=-90, cone=360, length=420, seed=7)
        OK.streaks(cv, [(hxy[0], hxy[1], 1.0)], strength=0.55, length=640, thickness=5)
    dx = sh * math.sin(t * 90)
    dy = sh * 0.6 * math.cos(t * 77)
    if t >= T_ELIM - 0.03:
        u = K.ramp(t, T_ELIM - 0.03, T_ELIM + 0.30, 'out_cubic')
        A['elim'].draw(cv, 540 + dx * 0.5, 400 + 24 * (1 - u) + dy * 0.5, opacity=u)
    if t >= T_LAG - 1.0 / K.FPS:
        s = K.lerp(1.45, 1.0, K.spring(t - (T_LAG - 1.0 / K.FPS), freq=3.0, damping=0.5))
        sw = K.ramp(t, T_LAG + 0.35, T_LAG + 1.15, 'inout_sine')
        A['lag'].draw(cv, 540 + dx, 610 + dy, scale=s, opacity=1.0, sweep=sw if 0 < sw < 1 else None)
    if t >= T_SEIZE - 0.03:
        u = K.ramp(t, T_SEIZE - 0.03, T_SEIZE + 0.30, 'out_cubic')
        A['seize'].draw(cv, 540, 1300 + 20 * (1 - u), opacity=u)
        u2 = K.ramp(t, T_SEIZE + 0.08, T_SEIZE + 0.34, 'out_cubic')
        A['opp'].draw(cv, 540, 1408, scale=K.lerp(1.06, 1.0, u2), blur=8 * (1 - u2),
                      opacity=K.ramp(t, T_SEIZE + 0.08, T_SEIZE + 0.18, 'linear'))
    return cv


# =================================================================================================== shot E
LOGO_C = (540.0, 700.0)
BTN_C = (540.0, 1065.0)


def _mark_geom():
    lg = assets()['logo']
    lh, lw = lg.shape[:2]
    mk = 244 / 1102 * lw
    cx = LOGO_C[0] - lw / 2 + mk / 2
    return cx, LOGO_C[1], min(mk, lh) * 0.47        # mark centre and sphere radius on the flat logo


@functools.lru_cache(maxsize=1)
def _mark_bbox():
    a = S3.get('okt_mark', 'night', mode='anim')
    f = a.frame(a.n - 1)
    return K.alpha_bbox(f)


@functools.lru_cache(maxsize=4)
def _feather(h, w, f=44):
    y = np.minimum(np.arange(h), np.arange(h)[::-1]).astype(np.float32)
    x = np.minimum(np.arange(w), np.arange(w)[::-1]).astype(np.float32)
    m = np.clip(y[:, None] / f, 0, 1) * np.clip(x[None, :] / f, 0, 1)
    return (m * m * (3 - 2 * m))[..., None]


def end_card(t):
    A = assets()
    cam = K.Cam(pos=(0.0, 0.0, -D0), aperture=0)
    cv = backdrop(t, cam, 0.18)
    K.draw(cv, A['pool'], LOGO_C[0], LOGO_C[1] + 40, opacity=0.9)
    # a gentle cyan streak BELOW the logo (never on it)
    OK.streaks(cv, [(540 + 120 * math.sin(t * 0.35), 905, 1.0)], strength=0.22, length=900, thickness=4, wide=0.5)
    e = t - WHIP
    mx, my, mr = _mark_geom()
    g = K.ramp(t, 15.45, 16.00, 'inout_cubic')
    cx, cy = K.lerp(540, mx, g), K.lerp(720, my, g)
    r = K.lerp(250, mr, g)
    sph_op = 1 - K.ramp(t, 15.95, 16.25, 'inout_sine')
    if sph_op > 0.002:
        if have3d('okt_mark', 'night_anim'):
            a = S3.get('okt_mark', 'night', mode='anim')
            spr = a.at_time(max(0.0, t - (WH0 - 0.1)), loop=False)
            x0, y0, x1, y1 = _mark_bbox()
            sc = 2 * r / max(1.0, (y1 - y0))
            K.draw(cv, spr, cx, cy, scale=sc, opacity=sph_op,
                   anchor=((x0 + x1) / 2 / spr.shape[1], (y0 + y1) / 2 / spr.shape[0]))
        else:
            asm = K.lerp(0.5, 1.0, K.ramp(t, WH0, 15.30, 'out_cubic'))
            OK.dot_sphere(cv, cam, (cx - K.CX, cy - K.CY, 0.0), r, t, spin=K.lerp(60, 6, asm), assemble=asm,
                          look=LOOK, opacity=sph_op * K.ramp(t, WH0, WH0 + 0.2, 'linear'), dof=False)
            A['mark_label'].draw(cv, cx, cy + r + 34, opacity=0.55 * sph_op)
    # flat logo: mark crossfades in, wordmark wipes in left -> right
    lg = A['logo']
    lh, lw = lg.shape[:2]
    x0 = LOGO_C[0] - lw / 2
    mo = K.ramp(t, 15.95, 16.25, 'inout_sine')
    if mo > 0:
        K.draw(cv, A['logo_mark'], x0, LOGO_C[1], anchor=(0.0, 0.5), opacity=mo)
    wu = K.ramp(t, 15.70, 16.15, 'inout_cubic')
    if wu > 0:
        wd = A['logo_word']
        ww = wd.shape[1]
        edge = wu * (ww + 80)
        m = np.clip((edge - np.arange(ww, dtype=np.float32)) / 80.0, 0, 1)
        spr = wd * m[None, :, None]
        K.draw(cv, spr, x0 + A['logo_mark'].shape[1], LOGO_C[1], anchor=(0.0, 0.5), blur=4 * (1 - wu))
    # CTA button
    if t >= T_CTA - 0.03:
        b = K.spring(t - (T_CTA - 0.03), freq=2.6, damping=0.5)
        hv = K.ramp(t, T_CLICK - 0.35, T_CLICK - 0.1, 'inout_sine')
        pr = K.impulse(t, T_CLICK, 9) if t >= T_CLICK - 0.02 else 0.0
        btn = ui.button(COPY['cta'], hover=hv, press=pr, ripple=(t - T_CLICK) if t >= T_CLICK else None, look=LOOK)
        btn = btn * _feather(*btn.shape[:2])          # ui.button's glow is clipped at the sprite edge: feather it
        ui.place(cv, btn, BTN_C[0], BTN_C[1], scale=K.lerp(0.7, 1.0, b),
                 opacity=K.ramp(t, T_CTA - 0.03, T_CTA + 0.10, 'linear'))
    if t >= T_RISK:
        o = K.ramp(t, T_RISK, T_RISK + 0.5, 'inout_sine')
        A['risk'][0].draw(cv, 540, 1320, opacity=o)
        A['risk'][1].draw(cv, 540, 1364, opacity=o)
    if t >= T_URL - 0.03:
        u = K.ramp(t, T_URL - 0.03, T_URL + 0.25, 'out_cubic')
        A['url'].draw(cv, 540, 1212 + 16 * (1 - u), opacity=u)
    # cursor press
    if 15.30 <= t <= 16.40:
        p = K.Track([(15.30, (900.0, 1640.0)), (15.68, (612.0, 1088.0), 'out_cubic'), (15.95, (612.0, 1088.0),
                    'in_cubic'), (16.40, (960.0, 1700.0))], ease='out_cubic')(t)
        op = K.ramp(t, 15.30, 15.45, 'linear') * (1 - K.ramp(t, 16.15, 16.40, 'linear'))
        ui.draw_cursor(cv, p[0], p[1], 'hand', 84, press=K.impulse(t, T_CLICK, 9) if t >= T_CLICK - 0.02 else 0.0,
                       click=(t - T_CLICK) if t >= T_CLICK else None, look=LOOK, opacity=op)
    return cv


# =================================================================================================== dispatch
def _shift(cv, dx):
    M = np.float32([[1, 0, dx], [0, 1, 0]])
    return cv2.warpAffine(cv, M, (K.W, K.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def whip_pos(t):
    return K.ramp(t, WH0, WH1, 'inout_quart')


def draw(t):
    tc = t + HALF
    if tc < CUT_B:
        return shot_a(t)
    if tc < CUT_C:
        return shot_b(t)
    if tc < CUT_D:
        return shot_c(t)
    if t < WH0:
        return shot_d(t)
    if t > WH1:
        return end_card(t)
    s = whip_pos(t)
    a = _shift(shot_d(t), -s * K.W)
    b = _shift(end_card(t), (1 - s) * K.W)
    cv = a + b
    cv[..., 3] = 1.0
    # smear proportional to the pan speed (px per frame)
    sp = (whip_pos(t + 0.5 / K.FPS) - whip_pos(t - 0.5 / K.FPS)) * K.W
    K.whip_blur(cv, min(260.0, sp * 1.6), 0.0)
    return cv


def post(cv, t):
    tc = t + HALF
    push = 1.1 * K.impulse(t, CUT_B - 0.02, 14) * (tc >= CUT_B) + 0.5 * K.impulse(t, CUT_D - 0.02, 16) * (tc >= CUT_D) \
        + 0.3 * K.impulse(t, T_LAG - 0.02, 14) * (t >= T_LAG - 0.04)
    ana = 0.30
    if CUT_C <= tc < CUT_D:
        ana = 0.10                               # tame the anamorphic pass on the hovered BUY button
    elif tc >= CUT_D:
        ana = K.lerp(0.30, 0.06, K.ramp(t, WH0, WHIP, 'linear'))   # end card: no flare band through the CTA
    L = K.LOOKS[LOOK]
    return K.post(cv, LOOK, t, exposure=L['exposure'] + push, bloom=L['bloom'] * (1 + 0.8 * push), anamorphic=ana)


def samples(t):
    tc = t + HALF
    if CUT_B - 0.05 <= tc < CUT_B + 0.55 or WH0 - 0.05 <= t <= WH1 + 0.05:
        return 7
    if BL0 <= t <= BL1 or CUT_C <= tc < CUT_C + 0.7 or T_PRESS <= t <= T_TOAST + 0.1 or T_LAG <= t <= T_LAG + 0.2:
        return 5
    return 3


from reel2_sfx import cues, BED, BED_GAIN_DB  # noqa: E402,F401  (sound designer owns the cue sheet)
