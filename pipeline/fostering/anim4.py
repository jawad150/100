"""anim4.py: ANIM 4 "£447.60: BUT WHAT IS IT FOR?" (Organic Fostering). 1080x1920, 30 fps, 25.5 s, 120 BPM.

LOOK: CLEAN LIGHT SaaS + FOLLOW THE MONEY. One continuous white world (true white page, faint plum dot grid on a
plane behind the stations, soft lavender / peach depth glows on a far plane, glossy 3D props with soft plum drop
shadows on the page, crisp white glass chips). A glowing gold light-trail RIBBON + a stream of spinning 3D GBP
coins travels through the whole film; the camera tracks it from the number to each station.
Type: hero "£447.60" extruded 3D gold (AMBER -> ORANGE, light sweep); headlines Nunito Black INK / PLUM;
captions Poppins. SFX only (no music).

GRID: 120 BPM, beat = 0.5 s, B(n) = n * 0.5. Every slam / pop / cut sits on a beat, 8th or 16th.

SHOT LIST (t s | beat | picture | camera | SFX)
 A HOOK 0.00-3.00 (B0-B6), world station S0 (0, 0)
  0.00  B0    "£447.60" (gold extrude 210 px) SLAMS from frame 0 (spring 1.5 -> 1) while a burst of 3D coins
              explodes out from behind it toward the lens (spin blur) and a warm local bloom pulses; light sweep
              0.35-0.95 | static, shake on the slam, slow push | number_slam (impact) + coins_burst + shimmer
  0.50  B1    "per week" (Nunito Black PLUM 76 px) rises under it | | swish
  1.00  B2    "Where does it go?" (INK 84 px) lands per glyph; a glossy 3D "?" pops above the number (spring +
              half spin) | | pop + "?" pop
  1.50  B3    the amount BURSTS into five glass chips radiating out on glowing spokes from a spinning gold coin
              hub, one per 16th: Home | Food | Essentials | Travel | School (3D prop icons) | | chip_burst +
              pops
  2.50  B5    chips SNAP back into the hub, the number re-forms (slam) | | whoosh + coin ring
 B THE MONEY MOVES 3.00-6.00 (B6-B12)
  3.00  B6    the number BREAKS into ~36 coins + light lines that swirl and pour into the gold ribbon flowing
              down-right; "?" and question lift out | slow push | coin cascade + whoosh
  3.25  B6.5  "Fostering payments / help cover the costs of / caring for a child." rises line by line (top)
  5.00  B10   camera leaves, following the lead coins (pull-back swoop, banking) | B10-B12 | whoosh_by
 C HOME 6.00-9.00 (B12-B18) station (1150, 1500)
  6.00  B12   the lead coins pour into the 3D house (pop, door glow); chip "Home" + headline "A safe,
              comfortable / home" (B12.5); bed B13; heart + key / shield glass tiles B14..B14.5 | hold, breathe |
              house pop, pops, coin clinks
  8.00  B16   leave -> FOOD (swoop right then left)
 D FOOD 9.00-12.00 (B18-B24) station (0, 3000)
  9.00  B18   apple (B18) -> sandwich (B19) -> plate (B20) pop along the stream; basket B21; apple + sandwich
              drop into it B21.5 / B22 (basket fills, bounce); headline "Food & everyday / essentials" B18.5
 E CLOTHES 12.00-15.00 (B24-B30) station (1150, 4500)
 12.00  B24   t-shirt B24 -> trainer B25 -> book & pencil B25.5 -> backpack B26; items slide into the backpack
              B27 / B27.5 / B28 (zip on B28); headline "Clothes, school items / & personal needs" B24.5
 F TRAVEL 15.00-18.00 (B30-B36) station (0, 6000)
 15.00  B30   the school bus drives past B30-B31.25 (motion blur, bus pass); football bounces in B31.5 (bounces on
              B32 / B32.5 / B33); paint palette pops B33 with a paint dab B33.5; headline "Travel, activities /
              & experiences" B30.5
 G THE BIGGER PICTURE 18.00-21.00 (B36-B42) station (575, 7500)
 18.00  B36   the stream arrives at the 3D child (logo girl), gold halo ring; every prop flies in and gathers on
              an orbit around her B36.5-B38; headline "It's about supporting / everyday life." B37;
              B40-B41.5 everything fades except the child | slow push | gathering whooshes, shimmer
 H FINAL 21.00-25.50 (B42-B51)
 21.00  B42   coins rise from the halo and form "£447.60/week" (gold, top) | number slam
 21.25  B42.5 "per child · ages 0–4" | 21.50 B43 statement "Fostering payments are there to help / cover the
              costs of caring for a child."
 22.00  B44   the child flies into the girl of the logo while the logo builds; B44.5 "Want to understand
              fostering payments?"; B45 gradient pill "Start the conversation / with Organic Fostering." pops;
              B45.5 "0161 241 1332 · organicfostering.co.uk" + footer "Weekly allowance for one child aged 0–4,
              based on / current published rates. Rates may vary; terms apply."; cursor clicks the pill on B46.5
              (23.25) and leaves by 23.70: settled end 23.75-25.50 (1.75 s) | end chime, CTA click

FLASH POLICY: no full-frame flash / fade anywhere (the page white must never grey, the ink never lift): accents
are local glows at the interaction point (anim4_fx.local_glow).

Render contract: DUR, LOOK, BPM, draw(t) (pure), post(cv, t), samples(t), cues(), prewarm(); BED.
Helpers: anim4_fx.py (world background, dot grid, ribbon, coins, shadows), anim4_props.py (3D props with
stand-ins until the Blender renders land), anim4_sfx.py (extra synthesised SFX + the -18 LUFS / -2 dBTP mix).
"""
import functools
import math

import numpy as np

import core as K
import anim4_fx as X
import anim4_props as P

DUR = 25.5
LOOK = 'airy'
BPM = 120
BEAT = 60.0 / BPM
BED = 'airy_bed'          # synthesised in anim4_sfx.py (registered by cues())
BED_GAIN_DB = -31.0


def B(n):
    """Time of beat n on the 120 BPM grid."""
    return n * BEAT


C = K.C
CX, CY = K.CX, K.CY

# ================================================================================================ world layout
S0 = np.array([0.0, 0.0])
ST = dict(home=np.array([1150.0, 1500.0]), food=np.array([0.0, 3000.0]), cloth=np.array([1150.0, 4500.0]),
          travel=np.array([0.0, 6000.0]), child=np.array([575.0, 7500.0]))
ORDER = ['s0', 'home', 'food', 'cloth', 'travel', 'child']
ARRIVE = dict(s0=0.0, home=B(12), food=B(18), cloth=B(24), travel=B(30), child=B(36))
LEAVE = dict(s0=B(10), home=B(16), food=B(22), cloth=B(28), travel=B(34), child=1e9)
# stream direction leaving / entering each station (world), for the camera swoop handles
EXIT = dict(s0=(0.35, 1.0), home=(1.0, 0.55), food=(-1.0, 0.55), cloth=(1.0, 0.55), travel=(-1.0, 0.55))
ENTRY = dict(home=(1.0, 0.45), food=(-1.0, 0.45), cloth=(1.0, 0.45), travel=(-1.0, 0.45), child=(0.55, 1.0))
COLLECT = dict(home=(0.0, 40.0), food=(0.0, 330.0), cloth=(250.0, 330.0), travel=(0.0, 60.0), child=(0.0, 130.0))

T_PERWEEK, T_Q, T_CHIPS, T_SNAP, T_BREAK, T_MSG = B(1), B(2), B(3), B(5), B(6), B(6.5)
T_FINAL = B(42)


def _st(name):
    return S0 if name == 's0' else ST[name]


@functools.lru_cache(maxsize=1)
def path():
    """The money's route (world, z = -30 so the ribbon floats just in front of the station plane)."""
    h, f, c, tr, ch = ST['home'], ST['food'], ST['cloth'], ST['travel'], ST['child']
    pts = [(0, -80), (60, 170), (230, 520), (430, 930), (560, 1260),
           (h[0] - 330, h[1] - 150), h + COLLECT['home'], (h[0] + 330, h[1] + 140), (h[0] + 640, h[1] + 330),
           (h[0] + 560, h[1] + 820), (f[0] + 900, f[1] - 330), (f[0] + 560, f[1] - 140), (f[0] + 260, f[1] + 160),
           f + COLLECT['food'], (f[0] - 330, f[1] + 330), (f[0] - 640, f[1] + 420),
           (f[0] - 600, f[1] + 900), (c[0] - 900, c[1] - 330), (c[0] - 560, c[1] - 160), (c[0] - 200, c[1] + 120),
           c + COLLECT['cloth'], (c[0] + 560, c[1] + 300), (c[0] + 760, c[1] + 520),
           (c[0] + 560, c[1] + 960), (tr[0] + 900, tr[1] - 330), (tr[0] + 560, tr[1] - 150),
           (tr[0] + 250, tr[1] + 20), tr + COLLECT['travel'], (tr[0] - 330, tr[1] + 160), (tr[0] - 640, tr[1] + 330),
           (tr[0] - 520, tr[1] + 880), (ch[0] - 700, ch[1] - 300), (ch[0] - 330, ch[1] - 20),
           ch + COLLECT['child']]
    return X.Path([(x, y, -30.0) for x, y in pts], step=8.0)


@functools.lru_cache(maxsize=1)
def s_collect():
    pth = path()
    return {k: pth.nearest_s(_st(k) + np.asarray(COLLECT[k])) for k in ST}


# ================================================================================================ camera
def _bez(p0, p1, p2, p3, u):
    a = 1 - u
    return a * a * a * p0 + 3 * a * a * u * p1 + 3 * a * u * u * p2 + u * u * u * p3


def _segment(t):
    """(from, to, u) during a move, or (station, None, 0) during a hold."""
    for i, nm in enumerate(ORDER):
        nxt = ORDER[i + 1] if i + 1 < len(ORDER) else None
        if nxt and LEAVE[nm] <= t < ARRIVE[nxt]:
            return nm, nxt, (t - LEAVE[nm]) / (ARRIVE[nxt] - LEAVE[nm])
        if t < LEAVE[nm]:
            return nm, None, 0.0
    return ORDER[-1], None, 0.0


SWOOP = 380.0


def base_cam_params(t):
    """Camera target (x, y), distance, roll, yaw, pitch WITHOUT the hold breathing (text rides this camera, so
    held copy stays pixel-locked while the world breathes)."""
    a, b, u = _segment(t)
    if b is None:
        A = _st(a)
        tgt = A.copy()
        dist = 1500.0
        roll = yaw = pitch = 0.0
        if a == 's0':                       # message: drift a touch toward the stream
            v = K.EASE['inout_sine'](K.clamp((t - T_BREAK) / (LEAVE['s0'] - T_BREAK)))
            tgt = tgt + np.array([0.0, 0.0])
        return tgt, dist, roll, yaw, pitch, a, b, u
    A, Bp = _st(a), _st(b)
    e = K.EASE['easy_ease'](K.clamp(u))
    ex, en = np.asarray(EXIT[a], float), np.asarray(ENTRY[b], float)
    ex /= np.linalg.norm(ex)
    en /= np.linalg.norm(en)
    tgt = _bez(A, A + ex * SWOOP, Bp - en * SWOOP, Bp, e)
    bump = math.sin(math.pi * e)
    dist = 1500.0 + 820.0 * bump ** 1.2
    # bank into the turn: sign of the horizontal swing
    vx = (_bez(A, A + ex * SWOOP, Bp - en * SWOOP, Bp, min(1.0, e + 0.01))[0] - tgt[0]) / 0.01
    roll = -2.6 * math.tanh(vx / 2500.0) * bump
    yaw = 1.6 * math.tanh(vx / 2500.0) * bump
    pitch = -1.2 * bump
    return tgt, dist, roll, yaw, pitch, a, b, u


def _breath(t):
    a, b, u = _segment(t)
    if b is not None:
        return 0.0, 0.0, 0.0, 0.0
    t0 = ARRIVE[a]
    t1 = LEAVE[a] if LEAVE[a] < 1e8 else DUR
    v = K.EASE['inout_sine'](K.clamp((t - t0) / max(0.1, t1 - t0)))
    push = -36.0 * v
    return push, K.wiggle(t, 0.22, 5.0, seed=11), K.wiggle(t, 0.19, 4.0, seed=12), K.wiggle(t, 0.15, 0.25, seed=13)


def _hook_shake(t):
    s = K.impulse(t, 0.0, decay=7.0) + 0.6 * K.impulse(t, T_SNAP, decay=8.0) + 0.5 * K.impulse(t, T_BREAK, 8.0)
    return K.shake(t, 9.0 * s, 15.0, seed=4)


def cam(t, breathe=True):
    tgt, dist, roll, yaw, pitch, a, b, u = base_cam_params(t)
    tx, ty = float(tgt[0]), float(tgt[1])
    if breathe:
        push, wx, wy, wr = _breath(t)
        dist += push
        tx += wx
        ty += wy
        roll += wr
        if t < T_BREAK + 0.6:
            sx, sy, sr = _hook_shake(t)
            tx += sx
            ty += sy
            roll += sr * 0.3
    return K.Cam.orbit((tx, ty, 0.0), dist, yaw=yaw, pitch=pitch, roll=roll, aperture=14.0, focus_dist=dist)


def text_cam(t):
    return cam(t, breathe=False)


def screen_of(c, wx, wy, wz=0.0):
    xy, d = c.project(np.array([[wx, wy, wz]]))
    return float(xy[0][0]), float(xy[0][1]), c.focal / float(d[0])


# ================================================================================================ depth layers
NEAR_DEPTH = 640.0
# near-lens bokeh per station hold: (screen x, y at the hold, kind, px size, extra blur, opacity)
NEAR_SPOTS = dict(
    s0=[(50, 1720, 'lav', 320, 8, 0.55), (1030, 150, 'peach', 230, 6, 0.55), (1000, 1860, 'gold', 170, 5, 0.5)],
    home=[(40, 140, 'peach', 250, 7, 0.5), (1020, 1790, 'lav', 340, 8, 0.5), (150, 1880, 'gold', 150, 4, 0.45)],
    food=[(1040, 150, 'lav', 250, 7, 0.5), (50, 1770, 'peach', 330, 8, 0.5), (960, 1890, 'gold', 150, 4, 0.45)],
    cloth=[(40, 140, 'pink', 240, 7, 0.45), (1020, 1770, 'peach', 330, 8, 0.5), (140, 1880, 'gold', 160, 4, 0.45)],
    travel=[(1040, 140, 'peach', 250, 7, 0.5), (50, 1790, 'lav', 330, 8, 0.5), (950, 1880, 'gold', 150, 4, 0.45)],
    child=[(40, 130, 'lav', 250, 7, 0.5), (1030, 1790, 'peach', 320, 8, 0.5), (110, 1870, 'gold', 150, 4, 0.4)])


@functools.lru_cache(maxsize=1)
def _near_items():
    out = []
    for st, spots in NEAR_SPOTS.items():
        S = _st(st)
        c0 = K.Cam.orbit((float(S[0]), float(S[1]), 0.0), 1500.0)
        for (sx, sy, kind, px, bl, op) in spots:
            Pw = X.unproject(c0, sx, sy, NEAR_DEPTH)
            out.append((tuple(Pw), kind, px * NEAR_DEPTH / c0.focal, bl, op))
    return out


def world(t, c, n_samples):
    """Background world: white page + far glows, far defocused coins, dot grid (parallax depth layers)."""
    cv = X.world_bg(t, c, dots=0.0)
    X.far_coins(cv, c, t, _money_assets()['coin'], n_samples, opacity=0.38)
    X.dot_grid(cv, c, t)
    return cv


def near_layer(cv, c, t):
    X.near_bokeh(cv, c, _near_items(), t)


# ================================================================================================ the money
V_FLOW = 420.0          # trickle coin speed along the ribbon (world units / s)
GAP = 150.0             # trickle spacing
N_TRICKLE = 26


@functools.lru_cache(maxsize=1)
def _s_keys():
    sc = s_collect()
    pth = path()
    # s0 frame exit (path leaves the S0 frame bottom ~ y 1000) at about B9
    s_exit0 = pth.nearest_s((470.0, 1000.0))
    keys = [(T_BREAK, 0.0, 'out_cubic'), (B(8.5), s_exit0 * 0.92, 'inout_sine'), (LEAVE['s0'] + 0.05, s_exit0 * 1.02,
                                                                                    'inout_cubic'),
            (ARRIVE['home'] - 0.04, sc['home'], 'hold')]
    for a, b in (('home', 'food'), ('food', 'cloth'), ('cloth', 'travel'), ('travel', 'child')):
        keys.append((LEAVE[a] - 0.12, sc[a], 'inout_cubic'))
        keys.append((ARRIVE[b] - 0.04, sc[b], 'hold'))
    return keys


def s_lead(t):
    """Arc length of the money's head (the lead coins) at time t."""
    if t < T_BREAK:
        return 0.0
    return float(K.Track(_s_keys())(t))


def lead_moving(t):
    """0..1: the lead coins are travelling (between stations)."""
    ks = _s_keys()
    for (t0, s0_, e0), (t1, s1_, e1) in zip(ks[:-1], ks[1:]):
        if t0 <= t < t1 and abs(s1_ - s0_) > 1:
            return math.sin(math.pi * K.clamp((t - t0) / (t1 - t0))) ** 0.5
    return 0.0


@functools.lru_cache(maxsize=1)
def _money_assets():
    d = {}
    d['coin'] = P.prop('coin_gbp', mode='spin', scale=0.32)
    d['coin_m'] = P.prop('coin_gbp', mode='spin', scale=0.55)
    d['coin_l'] = P.prop('coin_gbp', mode='spin', scale=1.0)
    return d


def _coin_asset(size_px):
    A = _money_assets()
    if size_px < 120:
        return A['coin']
    if size_px < 260:
        return A['coin_m']
    return A['coin_l']


def draw_stream(cv, c, t, n_samples, opacity=1.0, rib_from=0.0):
    """Ribbon (drawn up to the head) + trickle coins flowing along it + lead coins at the head."""
    if t < T_BREAK - 0.02:
        return
    pth = path()
    s1 = s_lead(t)
    s0_ = max(rib_from, s1 - 5200.0)
    if s1 - s0_ > 4:
        intro = K.ramp(t, T_BREAK, T_BREAK + 0.35)
        X.draw_ribbon(cv, c, pth, s0_, s1, t, width=36.0, opacity=opacity * intro, head=0.4 + 0.6 * lead_moving(t))
    # trickle coins: flow toward the head, absorbed into it; tail spawn
    mv = lead_moving(t)
    span = N_TRICKLE * GAP
    for i in range(N_TRICKLE):
        back = (i * GAP - (t * V_FLOW) % GAP) % span
        s = s1 - back
        if s < s0_ + 40 or s < 0:
            continue
        a = K.smoothstep(0.0, 90.0, back) * K.smoothstep(span, span - 300.0, back)
        a *= K.smoothstep(s0_ + 40, s0_ + 240, s)
        if a <= 0.02:
            continue
        Pp = pth.at(s)
        tg = pth.tan(s)
        nrm = np.array([-tg[1], tg[0], 0.0])
        wob = 26.0 * math.sin(s * 0.011 + i * 1.7)
        Pw = Pp + nrm * wob + np.array([0.0, 0.0, -40.0 - 30.0 * math.sin(i * 2.1 + t)])
        size = 64.0 + 14.0 * ((i * 37) % 5) / 4.0
        rate = 260.0 + 70.0 * ((i * 13) % 4)
        ang = t * rate + i * 47.0
        X.draw_coin(cv, c, _coin_asset(size * c.focal / 1500.0), Pw, size, ang, rate, n_samples,
                    opacity=a * opacity, rot=-12.0 + 8.0 * math.sin(i))
    # lead packet (bigger coins) while travelling
    if mv > 0.01:
        for j in range(5):
            s = s1 - 60.0 - 70.0 * j
            Pp = pth.at(s)
            tg = pth.tan(s)
            nrm = np.array([-tg[1], tg[0], 0.0])
            Pw = Pp + nrm * (40.0 * math.sin(t * 7.0 + j * 1.9)) + np.array([0.0, 0.0, -80.0 - 40.0 * j])
            size = 120.0 - 10.0 * j
            rate = 420.0 + 60.0 * j
            X.draw_coin(cv, c, _coin_asset(size * c.focal / 1500.0), Pw, size, t * rate + j * 70.0, rate, n_samples,
                        opacity=mv * opacity)


# ================================================================================================ type
GOLD_KW = dict(fill=((0.0, '#FFF6E0'), (0.38, '#FFD27F'), (0.72, '#FFB15C'), (1.0, '#FF7A1A')),
               side=(('#E07A12', 1.0), ('#8A3A06', 1.0)), glow=0.0, shadow=0.32, shadow_color='#6B2A40',
               shadow_offset=(0.03, 0.12), shadow_blur=0.10, tracking=0.035, env_ground='#FF8A2A')
HEAD_KW = dict(font='Nunito-Black', fill='INK', line_height=1.04, shadow=0.10, shadow_color='#5B2E52',
               shadow_offset=(0.0, 0.035), shadow_blur=0.05)


@functools.lru_cache(maxsize=1)
def _type():
    import type3d as T
    d = {}
    d['num'] = T.render('£447.60', 'gold', px=210, **GOLD_KW)
    d['perweek'] = T.render('per week', 'flat', px=76, **dict(HEAD_KW, fill='PLUM'))
    d['q'] = T.Glyphs('Where does it go?', 'flat', px=84, **HEAD_KW)
    d['msg'] = [T.render('Fostering payments', 'flat', px=76, **dict(HEAD_KW, fill='PLUM')),
                T.render('help cover the costs of', 'flat', px=76, **HEAD_KW),
                T.render('caring for a child.', 'flat', px=76, **HEAD_KW)]
    heads = dict(home='A safe, comfortable\nhome', food='Food & everyday\nessentials',
                 cloth='Clothes, school items\n& personal needs', travel='Travel, activities\n& experiences',
                 child="It's about supporting\neveryday life.")
    d['head'] = {k: T.render(v, 'flat', px=84, **HEAD_KW) for k, v in heads.items()}
    d['fnum'] = T.render('£447.60', 'gold', px=158, **GOLD_KW)
    d['fweek'] = T.render('/week', 'gold', px=88, **GOLD_KW)
    d['perchild'] = T.render('per child · ages 0–4', 'flat', px=40, font='Poppins-Medium', fill='PLUM')
    d['stmt'] = T.render('Fostering payments are there to help\ncover the costs of caring for a child.', 'flat',
                         px=46, font='Nunito-ExtraBold', fill='INK', line_height=1.18)
    d['ask'] = T.render('Want to understand fostering payments?', 'flat', px=44, font='Nunito-Black', fill='PLUM')
    d['phone'] = T.render('0161 241 1332  ·  organicfostering.co.uk', 'ui_ink', px=40)
    d['foot'] = T.render('Weekly allowance for one child aged 0–4, based on\ncurrent published rates. Rates may vary; '
                         'terms apply.', 'flat', px=28, font='Poppins-Regular', fill='#4A3A4E', line_height=1.3)
    return d


def _rise(t, t0, dur=0.55):
    """(opacity, dy, blur) for an eased rise-in starting at t0."""
    r = K.ramp(t, t0, t0 + dur, 'out_expo')
    return K.ramp(t, t0, t0 + 0.18), 34.0 * (1 - r), 7.0 * (1 - r)


def draw_text_world(cv, ts, tc, wx, wy, t, t_in, t_out=None, out_dur=0.35, sweep=None, anchor=(0.5, 0.5),
                    sweep_kw=None, scale=1.0, opacity=1.0):
    """Text anchored at a world point, drawn in 2D through the text camera (pixel-locked at holds)."""
    if t < t_in:
        return
    op, dy, bl = _rise(t, t_in)
    if t_out is not None and t > t_out:
        o = K.ramp(t, t_out, t_out + out_dur, 'in_cubic')
        op *= 1 - o
        bl += 6.0 * o
        dy -= 20.0 * o
    op *= opacity
    if op <= 0.003:
        return
    x, y, k = screen_of(tc, wx, wy)
    s = k * scale
    snap = abs(s - 1.0) < 1e-3 and bl < 0.05
    if snap:
        x, y = round(x), round(y + dy)
    else:
        y = y + dy * k
    _rec_text(ts, x, y, s, anchor, op)
    ts.draw(cv, x, y, anchor=anchor, scale=s, opacity=op, blur=bl, snap=snap,
            sweep=sweep if sweep is not None and 0 < sweep < 1 else None, sweep_kw=sweep_kw)


def _rec_text(ts, x, y, s, anchor, op, label=None):
    """Dev recorder: ink box of a text sprite (cap-top .. baseline + descender) for anim4.checks()."""
    if X.REC is None or op < 0.3:
        return
    w, h = ts.w * s, ts.h * s
    px = getattr(ts, 'style', None)
    em = (px.px if px is not None else h) * s
    x0 = x - anchor[0] * w
    y0 = y - anchor[1] * h
    X.REC.append(('text', (x0, y0 - 0.04 * em, x0 + w, y0 + h + 0.24 * em), op, label or getattr(ts, 'text', '')))


# ================================================================================================ A. HOOK
NUM_W = (0.0, -90.0)            # number centre (world) -> screen y 870
PW_W = (0.0, 74.0)              # per week -> 1034
Q_W = (0.0, 330.0)              # question -> 1290
QM_W = (0.0, -530.0, -60.0)     # 3D question mark (screen y ~430)
HUB_W = (0.0, -70.0, -40.0)     # chip hub -> 890
CHIPS = [('Home', 'house', (0.0, -235.0)), ('Food', 'apple', (285.0, -110.0)),
         ('Essentials', 'tshirt', (190.0, 170.0)), ('Travel', 'school_bus', (-190.0, 170.0)),
         ('School', 'book_pencil', (-285.0, -110.0))]


@functools.lru_cache(maxsize=1)
def _hook_assets():
    d = {}
    d['q3'] = P.prop('question', 'day', scale=0.6)
    # burst directions in two vertical cones (up / down, 40..140 deg from horizontal): clear of the number
    d['burst'] = [(math.radians((-1 if i % 2 else 1) * (40.0 + 100.0 * ((i * 5) % 7) / 6.0) + 4 * math.sin(i)),
                   0.7 + 0.3 * ((i * 7) % 5) / 4.0) for i in range(14)]
    return d


@functools.lru_cache(maxsize=8)
def _chip(label, icon_name, ready):
    """White glass chip with a 3D prop icon (cached per readiness of the icon render)."""
    import ui
    pr = P.prop(icon_name, scale=0.2)
    ic = pr.at_yaw(-12.0) if not getattr(pr, 'placeholder', False) else pr.frame(0)
    tw = ui.measure(label, 40, 'ui')
    h = 92
    icw = 74
    w = int(math.ceil((26 + icw + 10 + tw + 34) / 4.0) * 4)
    base = ui.glass_card(w, h, r=h / 2, look='airy', rim=0.6, glow=0.4, shadow=0.9)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    # icon: scale the prop sprite into a 74 px box at the left
    bb = X.K.alpha_bbox(ic) if hasattr(X.K, 'alpha_bbox') else (0, 0, ic.shape[1], ic.shape[0])
    x0, y0, x1, y1 = [int(v) for v in bb]
    crop = ic[y0:y1, x0:x1]
    sc = min(icw / max(1, crop.shape[1]), (h - 14) / max(1, crop.shape[0]))
    import cv2
    crop = cv2.resize(crop, (max(1, int(crop.shape[1] * sc)), max(1, int(crop.shape[0] * sc))),
                      interpolation=cv2.INTER_AREA)
    S.paste(crop, p + 26 + icw / 2, p + h / 2, anchor=(0.5, 0.5))
    ui.put_text(f, p + 26 + icw + 10, p + h / 2 + 2, label, 40, 'ui', C['INK'], 'lm')
    return ui.derive_panel(base, f)


def chip_panel(label, icon_name):
    return _chip(label, icon_name, P.ready(icon_name))


def _chip_state(i, t):
    """(out 0..1 along the spoke, opacity) of chip i."""
    t0 = T_CHIPS + 0.125 * i
    o = K.ramp(t, t0, t0 + 0.42, 'out_back') if t < T_SNAP else 1.0
    if t >= T_SNAP - 0.12:
        b = K.ramp(t, T_SNAP - 0.12 + 0.03 * (4 - i), T_SNAP + 0.1, 'in_back')
        o *= 1 - b
    op = K.ramp(t, t0, t0 + 0.1) * (1 - K.ramp(t, T_SNAP + 0.02, T_SNAP + 0.1))
    return K.clamp(o, -0.2, 1.3), op


def _num_state(t):
    """(scale, opacity) of the hook number: slam at 0, out into the chips at B3, re-forms at B5, breaks at B6."""
    if t < T_CHIPS:
        sp = K.spring(t + 0.06, freq=2.4, damping=0.42)
        return K.lerp(1.5, 1.0, sp), 1.0
    if t < T_SNAP:
        u = K.ramp(t, T_CHIPS - 0.02, T_CHIPS + 0.16, 'in_cubic')
        return 1.0 - 0.6 * u, 1.0 - u
    if t < T_BREAK:
        sp = K.spring(t - T_SNAP, freq=2.6, damping=0.62)
        return K.lerp(0.55, 1.0, sp), K.ramp(t, T_SNAP, T_SNAP + 0.06)
    u = K.ramp(t, T_BREAK, T_BREAK + 0.14, 'in_cubic')
    return 1.0 + 0.12 * u, 1.0 - u


def scene_hook(t, n_samples):
    c = cam(t)
    tc = text_cam(t)
    cv = world(t, c, n_samples)
    A = _hook_assets()
    Ty = _type()
    # warm local bloom behind the number on the slam / snap
    nx, ny, k = screen_of(c, *NUM_W)
    g = K.impulse(t, 0.0, decay=4.0) + 0.7 * K.impulse(t, T_SNAP, decay=5.0)
    X.local_glow(cv, nx, ny, 520.0, 'peach', 0.8 * min(1.0, g + 0.25))
    X.local_glow(cv, nx, ny, 380.0, 'gold', 0.6 * g)
    # coin burst from behind the number (frame 0 already mid-burst: t + 0.12)
    tb = t + 0.2
    if tb < 1.3:
        for i, (ang, sp) in enumerate(A['burst']):
            u = K.EASE['out_cubic'](K.clamp(tb / 1.2))
            r = 1500.0 * sp * u
            z = K.lerp(150.0, -900.0 - 200.0 * (i % 3), u)
            Pw = (NUM_W[0] + math.cos(ang) * r, NUM_W[1] + math.sin(ang) * r * 1.1, z)
            rate = 900.0
            X.draw_coin(cv, c, _coin_asset(300), Pw, 150.0, tb * rate + i * 40, rate, n_samples,
                        opacity=K.ramp(tb, 0.0, 0.05) * (1 - K.ramp(tb, 0.9, 1.3)))
    # 3D question mark (pops on B2, half spin to face-on, floats)
    if t >= T_Q - 0.02:
        sp = K.spring(t - T_Q, freq=2.4, damping=0.45)
        out = K.ramp(t, T_BREAK, T_BREAK + 0.35, 'in_back')
        yaw = -40.0 * (1 - K.spring(t - T_Q, freq=1.8, damping=0.5)) + 10.0 * math.sin(t * 1.9)
        spr = A['q3'].at_yaw(yaw)
        Pq = (QM_W[0], QM_W[1] - 600.0 * out + 10 * math.sin(t * 2.3), QM_W[2])
        X.draw_prop(cv, c, spr, Pq, 330.0 * max(0.0, sp) * (1 - 0.3 * out), opacity=1 - out)
        if t < T_Q + 0.4:
            qx, qy, _ = screen_of(c, QM_W[0], QM_W[1])
            X.local_glow(cv, qx, qy, 260.0, 'mag', 0.6 * K.impulse(t, T_Q, decay=6.0))
    # hub coin + spokes + chips
    if T_CHIPS - 0.05 <= t < T_SNAP + 0.25:
        _draw_chips(cv, c, tc, t, n_samples)
    # number
    s, op = _num_state(t)
    if op > 0.003:
        x, y, k = screen_of(tc, *NUM_W)
        sw = K.ramp(t, 0.30, 0.95, 'inout_sine')
        if sw >= 1:
            sw = K.ramp(t, T_SNAP + 0.1, T_SNAP + 0.55, 'inout_sine')
        Ty['num'].draw(cv, x, y, scale=s * k, opacity=op, snap=False, blur=2.0 * abs(s - 1.0) * 4,
                       sweep=sw if 0 < sw < 1 else None, sweep_kw=dict(width=0.13, strength=1.5))
        _rec_text(Ty['num'], x, y, s * k, (0.5, 0.5), op, '£447.60')
    # per week (rises on B1, leaves into the chips with the number)
    if t >= T_PERWEEK:
        o_out = K.ramp(t, T_CHIPS - 0.02, T_CHIPS + 0.14) * (1 - K.ramp(t, T_SNAP, T_SNAP + 0.12))
        o_brk = K.ramp(t, T_BREAK, T_BREAK + 0.18)
        draw_text_world(cv, Ty['perweek'], tc, *PW_W, t, T_PERWEEK, opacity=(1 - o_out) * (1 - o_brk))
    # question (per-glyph slam on B2)
    if t >= T_Q:
        qx, qy, k = screen_of(tc, *Q_W)
        out = K.ramp(t, T_BREAK - 0.08, T_BREAK + 0.14, 'in_cubic')
        Ty['q'].slam(cv, t, round(qx), round(qy - 80 * out), t0=T_Q, s0=1.45, dur=0.34, stagger=0.012,
                     opacity=1 - out, smear=t < T_Q + 0.45)
        if t > T_Q + 0.45:
            _rec_text(Ty['q'].block, round(qx), round(qy - 80 * out), 1.0, (0.5, 0.5), 1 - out, 'Where does it go?')
    draw_stream(cv, c, t, n_samples)
    if t >= T_BREAK - 0.02:
        _draw_break(cv, c, t, n_samples)
    for i, ts in enumerate(Ty['msg']):
        draw_text_world(cv, ts, tc, *MSG_W[i], t, T_MSG + 0.25 * i)
    near_layer(cv, c, t)
    return cv


def _draw_chips(cv, c, tc, t, n_samples):
    import cv2
    hx, hy, k = screen_of(c, HUB_W[0], HUB_W[1], HUB_W[2])
    hub = K.ramp(t, T_CHIPS - 0.05, T_CHIPS + 0.2, 'out_back') * (1 - K.ramp(t, T_SNAP + 0.05, T_SNAP + 0.2))
    # spokes
    lay = np.zeros((K.H, K.W), np.uint8)
    ends = []
    for i, (lab, icn, off) in enumerate(CHIPS):
        o, op = _chip_state(i, t)
        if op <= 0.01:
            continue
        ex, ey, _ = screen_of(tc, HUB_W[0] + off[0] * o, HUB_W[1] + off[1] * o)
        ends.append((i, ex, ey, o, op))
        S = 16
        cv2.line(lay, (int(hx * S), int(hy * S)), (int(ex * S), int(ey * S)), int(220 * op), 3, cv2.LINE_AA, 4)
    if ends:
        a = lay.astype(np.float32) / 255.0
        halo = K.gblur(a, 6.0, border='constant')
        lay4 = np.zeros((K.H, K.W, 4), np.float32)
        X._over_a(lay4, np.clip(halo * 0.9, 0, 1), K.mix(X.AMBER, X.PEACH, 0.3))
        X._over_a(lay4, a, X.GOLD * 1.1)
        K.over(cv, lay4)
    if hub > 0.01:
        X.local_glow(cv, hx, hy, 260.0, 'gold', 0.5 * hub)
        X.draw_coin(cv, c, _coin_asset(240), HUB_W, 190.0 * hub, t * 300.0, 300.0, n_samples)
    for (i, ex, ey, o, op) in ends:
        lab, icn, off = CHIPS[i]
        pn = chip_panel(lab, icn)
        s = 0.55 + 0.45 * K.clamp(o)
        pn.draw(cv, ex, ey, scale=s, opacity=op)
        if X.REC is not None and op > 0.3 and o > 0.9:
            X.REC.append(('text', (ex - pn.w * s / 2, ey - pn.h * s / 2, ex + pn.w * s / 2, ey + pn.h * s / 2), op,
                          'chip ' + lab))


@functools.lru_cache(maxsize=1)
def _break_seeds():
    """Spawn points of the coins the number breaks into: sampled inside the glyph ink of '£447.60' (world, on the
    number plane), with a burst direction biased down / outward (the message lands above)."""
    import cv2
    ts = _type()['num']
    spr = ts.sprite if hasattr(ts, 'sprite') else None
    rng = np.random.default_rng(5)
    pts = []
    w, h = ts.w, ts.h
    for i in range(40):
        bx = rng.uniform(-0.47, 0.47)
        by = rng.uniform(-0.42, 0.42)
        ang = math.atan2(0.9 + by, bx * 1.4) + rng.uniform(-0.35, 0.35)
        sp = rng.uniform(260.0, 620.0)
        pts.append((NUM_W[0] + bx * w, NUM_W[1] + by * h, rng.uniform(-200, 30), math.cos(ang) * sp,
                    abs(math.sin(ang)) * sp + 120.0, rng.uniform(0.0, 1.0)))
    return pts


BREAK_MERGE = 1.15                  # s after the break: the burst coins have become the stream


def _draw_break(cv, c, t, n_samples):
    """The number breaks into coins: a burst (down / outward, toward the lens), then each coin is pulled into the
    gold stream and carried off with it (fades into the trickle by BREAK_MERGE)."""
    u = t - T_BREAK
    if u < -0.02 or u > BREAK_MERGE + 0.1:
        return
    pth = path()
    sl = s_lead(t)
    for i, (x, y, z, vx, vy, r) in enumerate(_break_seeds()):
        e = K.EASE['out_cubic'](K.clamp(u / 0.55))
        P0 = np.array([x + vx * 0.55 * e, y + vy * 0.55 * e, z - 420.0 * e])
        s_t = max(0.0, sl - 40.0 - 900.0 * r * (1 - K.clamp(u / BREAK_MERGE)))
        P1 = pth.at(s_t) + np.array([0.0, 0.0, -60.0])
        w = K.ramp(u, 0.18 + 0.25 * r, 0.75 + 0.3 * r, 'inout_cubic')
        Pw = P0 * (1 - w) + P1 * w
        a = K.ramp(u, -0.02, 0.03) * (1 - K.ramp(u, 0.75 + 0.3 * r, BREAK_MERGE))
        rate = 900.0 * (1 - 0.6 * w)
        X.draw_coin(cv, c, _coin_asset(160), tuple(Pw), 104.0 - 30.0 * w, t * rate + i * 33, rate, n_samples,
                    opacity=a)


# ================================================================================================ B. MESSAGE
MSG_W = [(0.0, -590.0), (0.0, -498.0), (0.0, -406.0)]     # world (screen y 370 / 462 / 554 at S0)


def scene_message(t, n_samples):
    c = cam(t)
    tc = text_cam(t)
    cv = world(t, c, n_samples)
    Ty = _type()
    draw_stations(cv, c, t, n_samples)
    _draw_break(cv, c, t, n_samples)
    for i, ts in enumerate(Ty['msg']):
        draw_text_world(cv, ts, tc, *MSG_W[i], t, T_MSG + 0.25 * i)
    near_layer(cv, c, t)
    return cv


# ================================================================================================ C-F. STATIONS
@functools.lru_cache(maxsize=8)
def _tile(icon_name):
    """Glossy app-icon tile: white glass square with a MAGENTA->ORANGE gradient glyph."""
    import ui
    s = 132
    base = ui.glass_card(s, s, r=36, look='airy', rim=0.7, glow=0.4, shadow=0.5)   # NB shadow=0 crashes (toolkit)
    f = base.face.copy()
    ic = ui.icon(icon_name, 72, 'WHITE', stroke=2.6, grad=('MAGENTA', 'ORANGE'))
    S = ui.Surf(f.shape[1], f.shape[0], f)
    S.paste(ic, base.pad + s / 2, base.pad + s / 2, anchor=(0.5, 0.5))
    out = K.crop_to_alpha(f, 2)
    out.setflags(write=False)
    return out


# prop specs per station: (asset, variant, rel world pos (x, y), width, pop time, yaw (base, amp), z)
# the first item of each station is its COLLECTOR (the money pours into it); z < 0 items float in front of the
# ribbon (drawn after the stream), z >= 0 behind it.
SPECS = dict(
    home=[('house', 'day', (0.0, 40.0), 560.0, B(11), (-10.0, 8.0), 0.0),
          ('bed', 'day', (-255.0, 430.0), 420.0, B(13), (14.0, 6.0), -70.0),
          ('heart', 'day', (300.0, -190.0), 220.0, B(13.5), (0.0, 18.0), -110.0),
          ('tile:key', None, (215.0, 470.0), 132.0, B(14), (0.0, 0.0), -90.0),
          ('tile:shield', None, (375.0, 400.0), 132.0, B(14.25), (0.0, 0.0), -90.0)],
    food=[('basket', 'day', (0.0, 330.0), 470.0, B(17), (-8.0, 6.0), 0.0),
          ('apple', 'day', (-270.0, -40.0), 250.0, B(18.5), (0.0, 16.0), -60.0),
          ('sandwich', 'day', (30.0, -110.0), 290.0, B(19), (0.0, 14.0), -60.0),
          ('plate', 'day', (310.0, 30.0), 300.0, B(19.5), (0.0, 10.0), -60.0)],
    cloth=[('backpack', 'day', (250.0, 330.0), 470.0, B(23), (-8.0, 8.0), 0.0),
           ('tshirt', 'day', (-300.0, -50.0), 320.0, B(24.5), (0.0, 16.0), -60.0),
           ('trainer', 'day', (-10.0, -120.0), 280.0, B(25), (0.0, 14.0), -60.0),
           ('book_pencil', 'day', (-290.0, 300.0), 260.0, B(25.5), (0.0, 12.0), -60.0)],
    travel=[('school_bus', 'side', (0.0, 420.0), 600.0, B(30), (0.0, 0.0), -70.0),
            ('football', 'day', (250.0, 170.0), 230.0, B(31.5), (0.0, 0.0), -70.0),
            ('paint_palette', 'day', (-270.0, 150.0), 320.0, B(32.5), (0.0, 10.0), -70.0)])
# items that move into their station's collector: (station, item index, t0, t1)
INTO = [('food', 1, B(20), B(20.5)), ('food', 2, B(20.5), B(21)),
        ('cloth', 1, B(26), B(26.5)), ('cloth', 2, B(26.5), B(27)), ('cloth', 3, B(27), B(27.5))]
FULL_AT = dict(food=B(20.5))
BOUNCES = (B(32), B(32.5), B(33), B(33.5))


def _spr_for(name, variant, yaw):
    if name.startswith('tile:'):
        return _tile(name[5:])
    a = P.prop(name, variant)
    if getattr(a, 'mode', 'yaw') == 'static':
        return a.frame(0)
    return a.at_yaw(yaw)


def _collector_kick(st, t):
    """Squash / bounce of a collector when items land in it (and when the money arrives)."""
    k = K.impulse(t, ARRIVE[st], decay=5.0) * 0.6
    for (sn, it, a0, a1) in INTO:
        if sn == st:
            k += K.impulse(t, a1, decay=7.0)
    return k


def _prop_state(st, i, t):
    """(pos rel (x, y, z), scale, opacity, yaw, squash) of prop i of station st at t."""
    name, var, rel, w, t0, (yb, ya), z = SPECS[st][i]
    sp = K.spring(t - t0, freq=2.5, damping=0.42) if t >= t0 else 0.0
    x, y = rel
    bob = 10.0 * math.sin(t * 1.6 + i * 1.3)
    yaw = yb + ya * math.sin(t * 0.9 + i)
    op = K.ramp(t, t0, t0 + 0.08)
    s = sp
    sq = 0.0
    if i == 0:
        kk = _collector_kick(st, t)
        sq = 0.07 * kk * math.cos((t - t0) * 18.0) if kk > 0.01 else 0.0
        bob *= 0.5
    for (sn, it, a0, a1) in INTO:
        if sn == st and it == i and t >= a0:
            u = K.ramp(t, a0, a1, 'in_cubic')
            cx, cy = SPECS[st][0][2]
            arc = -150.0 * math.sin(math.pi * K.ramp(t, a0, a1, 'out_sine'))
            x = K.lerp(x, cx, u)
            y = K.lerp(y, cy - 30.0, u) + arc
            s *= 1.0 - 0.6 * u
            op *= 1.0 - K.ramp(t, a1 - 0.08, a1)
            yaw += 40.0 * u
    if name == 'school_bus':
        u = K.ramp(t, t0, t0 + 1.25, 'inout_sine')
        x = K.lerp(-1050.0, 1100.0, u)
        live = t0 <= t < t0 + 1.3
        s = 1.0 if live else 0.0
        op = 1.0 if live else 0.0
        bob = 5.0 * abs(math.sin(t * 19.0)) * (1 - abs(2 * u - 1))
    if name == 'football' and t >= t0:
        if t < BOUNCES[0]:
            u = K.ramp(t, t0, BOUNCES[0], 'linear')
            x = K.lerp(640.0, rel[0] + 70.0, u)
            y = rel[1] - 460.0 * (1 - u * u)
        else:
            k = max(j for j in range(len(BOUNCES)) if BOUNCES[j] <= t)
            if k + 1 < len(BOUNCES):
                uu = (t - BOUNCES[k]) / (BOUNCES[k + 1] - BOUNCES[k])
                hgt = 230.0 * (0.5 ** k)
                y = rel[1] - 4 * hgt * uu * (1 - uu)
                x = rel[0] + 70.0 - 23.0 * (k + uu)
            else:
                y, x = rel[1], rel[0]
        s, op, bob = 1.0, 1.0, 0.0
        yaw = -t * 260.0
    return (x, y + bob, z), s, op, yaw, sq


def _station_items(st, t):
    out = []
    S = ST[st]
    for i, spec in enumerate(SPECS[st]):
        name, var, rel, w, t0, yawp, z = spec
        if t < t0 - 0.02:
            continue
        pos, s, op, yaw, sq = _prop_state(st, i, t)
        if s <= 0.01 or op <= 0.01:
            continue
        if name == 'basket' and t >= FULL_AT.get(st, 1e9):
            var = 'day_full'
        out.append(dict(i=i, name=name, var=var, P=(S[0] + pos[0], S[1] + pos[1], pos[2]), s=s, op=op, yaw=yaw,
                        sq=sq, w=w, t0=t0, z=pos[2]))
    return out


def _draw_item(cv, c, it, t, n_samples):
    name = it['name']
    if name == 'football':
        a = P.prop('football', 'day')
        spr = X.coin_sprite(a, it['yaw'], 260.0, n_samples) if getattr(a, 'mode', '') == 'spin' else \
            a.at_yaw(10.0 * math.sin(t * 3.0))
    else:
        spr = _spr_for(name, it['var'], it['yaw'])
    pop = K.impulse(t, it['t0'], decay=6.0)
    if pop > 0.02:
        sx, sy, k = screen_of(c, *it['P'])
        X.local_glow(cv, sx, sy, 0.75 * it['w'] * k, 'peach', 0.75 * pop)
    sq = it['sq']
    X.draw_prop(cv, c, spr, it['P'], it['w'] * it['s'], opacity=it['op'], scale_xy=(1.0 + sq, 1.0 - sq),
                anchor=(0.5, 0.5))


def _visible_stations(c):
    out = []
    for st in SPECS:
        S = ST[st]
        if abs(c.pos[1] - S[1]) < 2600 and abs(c.pos[0] - S[0]) < 2400:
            out.append(st)
    return out


def _paint_dab(cv, c, t):
    t0 = B(33)
    if t < t0:
        return
    S = ST['travel']
    cols = [C['MAGENTA'], C['ORANGE'], C['LEAF'], X.lin('#4C7BD9'), C['AMBER']]
    base = SPECS['travel'][2][2]
    for j, (dx, dy, r) in enumerate([(30, 150, 30), (85, 185, 20), (-10, 205, 16), (60, 120, 14), (110, 140, 11)]):
        u = K.ramp(t, t0 + 0.03 * j, t0 + 0.3 + 0.03 * j, 'out_back')
        x, y, k = screen_of(c, S[0] + base[0] + dx, S[1] + base[1] + dy, -75.0)
        rr = r * k * u
        if rr > 0.6:
            K.draw(cv, _dab_spr(j % len(cols)), x, y, scale=rr / 64.0, rot=37.0 * j,
                   opacity=0.95 * K.ramp(t, t0 + 0.03 * j, t0 + 0.08 + 0.03 * j))


@functools.lru_cache(maxsize=8)
def _dab_spr(j):
    """Glossy paint blob (soft-edged disc with a highlight)."""
    cols = [C['MAGENTA'], C['ORANGE'], C['LEAF'], X.lin('#4C7BD9'), C['AMBER']]
    d = K.disc(64, cols[j], soft=1.5)
    hi = K.disc(18, C['WHITE'] * 1.2, soft=6.0)
    p0 = (d.shape[0] - hi.shape[0]) // 2
    out = d.copy()
    y0, x0 = p0 - 22, p0 - 20
    sub = out[y0:y0 + hi.shape[0], x0:x0 + hi.shape[1]]
    sub *= 1 - 0.55 * hi[..., 3:4]
    sub += 0.55 * hi
    return out


def draw_stations(cv, c, t, n_samples, stream_op=1.0):
    """Props of the visible stations: collectors / behind-ribbon items, the money stream, then the front items."""
    sts = _visible_stations(c)
    items = []
    for st in sts:
        items += [(st, it) for it in _station_items(st, t)]
    for st, it in sorted([r for r in items if r[1]['z'] >= 0], key=lambda r: -r[1]['z']):
        _draw_item(cv, c, it, t, n_samples)
    draw_stream(cv, c, t, n_samples, opacity=stream_op)
    for st, it in sorted([r for r in items if r[1]['z'] < 0], key=lambda r: -r[1]['z']):
        _draw_item(cv, c, it, t, n_samples)
    if 'travel' in sts:
        _paint_dab(cv, c, t)


HEAD_DY = -495.0           # headline block centre relative to the station (screen y 465 at the hold)


def _draw_station_text(cv, tc, t):
    Ty = _type()
    for st in ('home', 'food', 'cloth', 'travel', 'child'):
        S = ST[st]
        t_in = ARRIVE[st] + 0.25
        t_out = B(40) if st == 'child' else None
        if t < t_in or (t_out is not None and t > t_out + 0.7):
            continue
        if t > LEAVE.get(st, 1e9) + 1.2:
            continue
        draw_text_world(cv, Ty['head'][st], tc, S[0], S[1] + HEAD_DY, t, t_in, t_out=t_out, out_dur=0.6)


def scene_stations(t, n_samples):
    c = cam(t)
    tc = text_cam(t)
    cv = world(t, c, n_samples)
    fade = 1.0 - K.ramp(t, B(40), B(41.4), 'inout_sine')
    draw_stations(cv, c, t, n_samples, stream_op=fade)
    if t >= ARRIVE['child'] - 1.0:
        _draw_child_scene(cv, c, tc, t, n_samples, fade)
    _draw_station_text(cv, tc, t)
    near_layer(cv, c, t)
    return cv


# ================================================================================================ G. CHILD
CHILD_REL = (0.0, 150.0, 0.0)
CHILD_W = 620.0
RING = dict(cx=0.0, cy=185.0, rx=430.0, ry=330.0, rz=300.0)
GATHER = [('house', 'day'), ('bed', 'day'), ('apple', 'day'), ('sandwich', 'day'), ('basket', 'day_full'),
          ('tshirt', 'day'), ('trainer', 'day'), ('backpack', 'day'), ('school_bus', 'day'), ('football', 'day'),
          ('paint_palette', 'day'), ('book_pencil', 'day')]
T_GATHER = B(36.5)
T_CHILD_POP = B(35.25)
T_FADE = (B(40), B(41.4))


def _child_pos(t):
    S = ST['child']
    return (S[0] + CHILD_REL[0], S[1] + CHILD_REL[1] + 8.0 * math.sin(t * 1.4), CHILD_REL[2])


def _gather_state(i, t):
    """(world P, scale, opacity, depth-sign) of gathered item i."""
    S = ST['child']
    n = len(GATHER)
    t0 = T_GATHER + 0.125 * (i // 2)
    u = K.ramp(t, t0, t0 + 0.62, 'inout_cubic')
    rot = 0.045 * max(0.0, t - T_GATHER) * 2 * math.pi
    th = 2 * math.pi * i / n + 0.26 + rot
    xr, yr, zr = RING['rx'] * math.cos(th), RING['ry'] * math.sin(th), RING['rz'] * math.sin(th)
    # fly in from beyond the left / right frame edges (never across the headline), curving into the slot
    side = 1.0 if math.cos(th) >= 0 else -1.0
    xo = xr + side * 900.0 * (1 - u) ** 1.5
    yo = yr + 260.0 * (1 - u) * (0.5 + 0.5 * math.sin(th)) + 120.0 * math.sin(math.pi * u) * side * 0.0
    Pw = np.array([S[0] + RING['cx'] + xo, S[1] + RING['cy'] + yo + 8.0 * math.sin(t * 1.7 + i), zr])
    s = 0.7 + 0.3 * u
    op = K.ramp(t, t0, t0 + 0.12)
    # fade: everything shrinks into the child and dissolves (only the child stays)
    f = K.ramp(t, T_FADE[0] + 0.03 * i, T_FADE[0] + 0.55 + 0.03 * i, 'in_cubic')
    if f > 0:
        C0 = np.array(_child_pos(t))
        Pw = Pw * (1 - 0.55 * f) + C0 * 0.55 * f
        s *= 1 - 0.7 * f
        op *= 1 - f
    return Pw, s, op, math.sin(th)


def _draw_child(cv, c, t, n_samples, opacity=1.0, scale=1.0, pos=None):
    a = P.prop('child_figure', 'day')
    pop = K.spring(t - T_CHILD_POP, freq=2.3, damping=0.45) if t >= T_CHILD_POP else 0.0
    if pop <= 0.01:
        return
    spr = a.at_yaw(6.0 * math.sin(t * 0.8)) if not getattr(a, 'placeholder', False) else a.frame(0)
    Pw = pos if pos is not None else _child_pos(t)
    X.draw_prop(cv, c, spr, Pw, CHILD_W * pop * scale, opacity=opacity)


def _child_halo(cv, c, t, amount):
    if amount <= 0.01:
        return
    Pw = _child_pos(t)
    sx, sy, k = screen_of(c, *Pw)
    X.local_glow(cv, sx, sy, 560.0 * k, 'peach', 0.6 * amount)
    X.local_glow(cv, sx, sy - 40 * k, 300.0 * k, 'gold', 0.35 * amount * (0.6 + 0.4 * K.impulse(t, ARRIVE['child'], 4.0)))


def _draw_child_scene(cv, c, tc, t, n_samples, fade):
    # arrival: the stream pours into the child (gold halo); gathered props orbit around her
    if t >= T_FINAL - 0.6:
        return _draw_final(cv, c, tc, t, n_samples)
    _child_halo(cv, c, t, K.ramp(t, ARRIVE['child'] - 0.2, ARRIVE['child'] + 0.4))
    items = []
    for i, (nm, var) in enumerate(GATHER):
        if t < T_GATHER + 0.125 * (i // 2):
            continue
        Pw, s, op, dz = _gather_state(i, t)
        if op <= 0.01:
            continue
        items.append((dz, i, nm, var, Pw, s, op))
    for (dz, i, nm, var, Pw, s, op) in sorted([r for r in items if r[0] > 0], key=lambda r: -r[0]):
        _draw_gathered(cv, c, t, i, nm, var, Pw, s, op)
    _draw_child(cv, c, t, n_samples)
    for (dz, i, nm, var, Pw, s, op) in sorted([r for r in items if r[0] <= 0], key=lambda r: -r[0]):
        _draw_gathered(cv, c, t, i, nm, var, Pw, s, op)


def _draw_gathered(cv, c, t, i, nm, var, Pw, s, op):
    a = P.prop(nm, var)
    spr = a.frame(0) if getattr(a, 'mode', 'yaw') == 'static' else a.at_yaw(12.0 * math.sin(t * 0.9 + i))
    w = 170.0 if nm != 'school_bus' else 210.0
    t0 = T_GATHER + 0.125 * (i // 2) + 0.62
    land = K.impulse(t, t0, decay=7.0)
    if land > 0.03 and op > 0.5:
        sx, sy, k = screen_of(c, *Pw)
        X.local_glow(cv, sx, sy, 160.0 * k, 'peach', 0.6 * land)
    X.draw_prop(cv, c, spr, tuple(Pw), w * s, opacity=op)


# ================================================================================================ H. FINAL
F_NUM_Y, F_PC_Y, F_ST_Y, F_ASK_Y, F_BTN_Y, F_LOGO_Y, F_PH_Y, F_FOOT_Y = 330, 452, 588, 742, 892, 1124, 1300, 1410
T_NUM2, T_PC, T_STMT, T_LOGO, T_ASK, T_BTN, T_PH, T_CLICK = (B(42), B(42.5), B(43), B(44), B(44.5), B(45), B(45.5),
                                                             B(46.5))
LOGO_W = 560.0
BTN_W, BTN_H, BTN_PX = 620, 150, 42


@functools.lru_cache(maxsize=1)
def _final_assets():
    import cv2
    d = {}
    im = cv2.imread(K.BRAND + '/logo_full.png', cv2.IMREAD_UNCHANGED)[:1080]      # lockup without tagline row
    rgba = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    # the girl (left orange figure of the emblem): orange pixels, left-most component
    r, g, b, a = [rgba[..., k].astype(int) for k in range(4)]
    orange = ((r > 200) & (g > 70) & (g < 160) & (b < 90) & (a > 128)).astype(np.uint8)
    orange[:, 1785:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(orange)
    comps = sorted([(st[i][0], i) for i in range(1, n) if st[i][4] > 4000])
    gi = comps[0][1]
    x, y, w, h, _ = st[gi]
    sc = LOGO_W / im.shape[1]
    d['girl'] = ((x + w / 2) * sc, (y + h / 2) * sc, h * sc)         # centre + height in logo px at LOGO_W
    d['logo'] = K.sprite(cv2.resize(rgba, (int(LOGO_W), int(round(im.shape[0] * sc))), interpolation=cv2.INTER_AREA))
    d['logo_size'] = (int(LOGO_W), int(round(im.shape[0] * sc)))
    return d


def _pill(hover, press, ripple):
    """Two-line brand CTA pill: MAGENTA -> ORANGE gradient (ui.button body) + white Poppins SemiBold lines + arrow."""
    import cv2
    import ui
    base = _pill_base(round(hover * 12) / 12.0)
    out = base
    if press > 0:
        s = 1 - 0.06 * press
        hh, ww = base.shape[:2]
        M = np.float32([[s, 0, ww / 2 * (1 - s)], [0, s, hh / 2 * (1 - s)]])
        out = cv2.warpAffine(base, M, (ww, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        out[..., :3] *= np.float32(1 - 0.12 * press)
    if ripple is not None and 0 <= ripple < 0.9:
        out = out.copy() if out is base else out
        ui._button_ripple(out, ripple, (0.86, 0.5), BTN_W, BTN_H, 1 - 0.06 * press)
    return out


@functools.lru_cache(maxsize=16)
def _pill_base(hover):
    import ui
    spr = ui.button(' ', hover=hover, look='airy', h=BTN_H, size=BTN_PX, icon_name=None, w=BTN_W).copy()
    P_ = ui.BUTTON_PAD
    lines = ('Start the conversation', 'with Organic Fostering.')
    tw = max(ui.measure(l, BTN_PX, 'ui') for l in lines)
    x0 = P_ + BTN_W / 2 - (tw + BTN_PX + 22) / 2
    ui.put_text(spr, x0, P_ + BTN_H / 2 - 8, lines[0], BTN_PX, 'ui', C['WHITE'], 'ls')
    ui.put_text(spr, x0, P_ + BTN_H / 2 + 44, lines[1], BTN_PX, 'ui', C['WHITE'], 'ls')
    ic = ui.icon('arrow_right', BTN_PX + 4, C['WHITE'], stroke=2.8)
    S = ui.Surf(spr.shape[1], spr.shape[0], spr)
    S.paste(ic, x0 + tw + 22 + BTN_PX / 2 + 8 * hover, P_ + BTN_H / 2 + 2, anchor=(0.5, 0.5))
    spr.setflags(write=False)
    return spr


def _feather(spr, m=40.0):
    """ui.button's glow is clipped at its padded sprite bounds (toolkit): fade the outer m px to zero."""
    h, w = spr.shape[:2]
    yy = np.minimum(np.arange(h), np.arange(h)[::-1]).astype(np.float32)[:, None]
    xx = np.minimum(np.arange(w), np.arange(w)[::-1]).astype(np.float32)[None, :]
    k = np.clip(np.minimum(yy, xx) / m, 0, 1)
    return spr * (k * k * (3 - 2 * k))[..., None]


def _final_num_coins(cv, c, t, n_samples):
    """Coins rise from the child's halo and converge on the number (B41.5 -> B42)."""
    t0, t1 = T_NUM2 - 0.5, T_NUM2 + 0.04
    if not (t0 <= t < t1 + 0.05):
        return
    S = ST['child']
    Cw = np.array(_child_pos(t))
    ts = _type()['fnum']
    for i in range(14):
        u = K.ramp(t, t0 + 0.012 * i, t1, 'in_cubic')
        tx = S[0] - 120.0 + (i / 13.0 - 0.5) * ts.w * 0.9
        ty = S[1] + (F_NUM_Y - 960.0)
        sx0 = Cw[0] + 180.0 * math.cos(i * 2.4)
        sy0 = Cw[1] - 80.0 + 60.0 * math.sin(i * 1.7)
        x = K.lerp(sx0, tx, u) + 160.0 * math.sin(math.pi * u) * math.cos(i * 1.3)
        y = K.lerp(sy0, ty, u)
        X.draw_coin(cv, c, _coin_asset(140), (x, y, -80.0), 96.0 * (1 - 0.4 * u), t * 700 + i * 40, 700.0,
                    n_samples, opacity=K.ramp(t, t0 + 0.012 * i, t0 + 0.1 + 0.012 * i) * (1 - K.ramp(t, t1 - 0.06, t1)))


def _draw_final(cv, c, tc, t, n_samples):
    Ty = _type()
    FA = _final_assets()
    S = ST['child']

    def wy(y):                          # world y of a screen y at the child hold
        return S[1] + (y - 960.0)
    # child: holds, then (B44) flies into the girl of the logo while the logo builds
    lw, lh = FA['logo_size']
    gx, gy, gh = FA['girl']
    lx0, ly0 = 540.0 - lw / 2, F_LOGO_Y - lh / 2
    u = K.ramp(t, T_LOGO, T_LOGO + 0.6, 'inout_cubic')
    _child_halo(cv, c, t, 1.0 - u)
    if u < 1:
        C0 = np.array(_child_pos(t))
        tgt = np.array([S[0] + (lx0 + gx - 540.0), wy(ly0 + gy), 0.0])
        Pw = C0 * (1 - u) + tgt * u
        a = P.prop('child_figure', 'day')
        bb = getattr(a, 'bbox', (0, 0, a.size[0], a.size[1]))
        vis_h = (bb[3] - bb[1]) / a.size[0] * CHILD_W          # visible height in world units at scale 1
        sc_end = gh / max(vis_h, 1.0)
        _draw_child(cv, c, t, n_samples, opacity=1.0 - K.ramp(t, T_LOGO + 0.4, T_LOGO + 0.62), pos=tuple(Pw),
                    scale=K.lerp(1.0, sc_end, u))
    _final_num_coins(cv, c, t, n_samples)
    # logo (fades / scales in as the child lands in it)
    if t >= T_LOGO + 0.2:
        r = K.ramp(t, T_LOGO + 0.2, T_LOGO + 0.75, 'out_cubic')
        x, y, k = screen_of(tc, S[0], wy(F_LOGO_Y))
        K.draw(cv, FA['logo'], round(x) if r >= 1 else x, round(y) if r >= 1 else y, scale=K.lerp(0.94, 1.0, r),
               opacity=K.ramp(t, T_LOGO + 0.2, T_LOGO + 0.5))
    # number "£447.60" + "/week"
    if t >= T_NUM2 - 0.02:
        sp = K.spring(t - T_NUM2, freq=2.6, damping=0.45)
        s = K.lerp(1.35, 1.0, sp)
        x, y, k = screen_of(tc, S[0], wy(F_NUM_Y))
        wn, ww_ = Ty['fnum'].w, Ty['fweek'].w
        gap = 10.0
        tot = wn + gap + ww_
        xl = x - tot / 2
        sw = K.ramp(t, T_NUM2 + 0.3, T_NUM2 + 0.95, 'inout_sine')
        if sw >= 1:
            sw = K.ramp(t, B(48), B(49.5), 'inout_sine')
        op = K.ramp(t, T_NUM2, T_NUM2 + 0.05)
        settled = abs(s - 1.0) < 1e-3
        cxn = xl + wn / 2
        if settled:
            Ty['fnum'].draw(cv, round(cxn), round(y), opacity=op, sweep=sw if 0 < sw < 1 else None,
                            sweep_kw=dict(width=0.13, strength=1.5))
            Ty['fweek'].draw(cv, round(xl + wn + gap), round(y + Ty['fnum'].h / 2), anchor=(0.0, 1.0), opacity=op,
                             sweep=sw if 0 < sw < 1 else None, sweep_kw=dict(width=0.13, strength=1.5))
            _rec_text(Ty['fnum'], round(cxn), round(y), 1.0, (0.5, 0.5), op, '£447.60 final')
            _rec_text(Ty['fweek'], round(xl + wn + gap), round(y + Ty['fnum'].h / 2), 1.0, (0.0, 1.0), op, '/week')
        else:
            Ty['fnum'].draw(cv, x + (cxn - x) * s, y, scale=s, opacity=op, snap=False)
            Ty['fweek'].draw(cv, x + (xl + wn + gap - x) * s, y + Ty['fnum'].h / 2 * s, anchor=(0.0, 1.0), scale=s,
                             opacity=op, snap=False)
        g = K.impulse(t, T_NUM2, decay=5.0)
        X.local_glow(cv, x, y, 420.0, 'gold', 0.5 * g)
    draw_text_world(cv, Ty['perchild'], tc, S[0], wy(F_PC_Y), t, T_PC)
    draw_text_world(cv, Ty['stmt'], tc, S[0], wy(F_ST_Y), t, T_STMT)
    draw_text_world(cv, Ty['ask'], tc, S[0], wy(F_ASK_Y), t, T_ASK)
    # CTA pill (pops on B45), cursor click on B46.5
    if t >= T_BTN:
        import ui
        pop = K.spring(t - T_BTN, freq=2.6, damping=0.5)
        hover = K.ramp(t, T_CLICK - 0.35, T_CLICK - 0.1) * (1 - K.ramp(t, T_CLICK + 0.3, T_CLICK + 0.6))
        press = K.impulse(t, T_CLICK, decay=9.0, attack=0.04)
        rip = 1.4 * (t - T_CLICK) if t >= T_CLICK else None
        spr = _feather(_pill(hover, press, rip))
        x, y, k = screen_of(tc, S[0], wy(F_BTN_Y))
        sc = K.lerp(0.6, 1.0, pop)
        settled = abs(sc - 1.0) < 1e-3
        ui.place(cv, spr, round(x) if settled else x, round(y) if settled else y, scale=sc,
                 opacity=K.ramp(t, T_BTN, T_BTN + 0.1))
        if X.REC is not None and settled:
            X.REC.append(('text', (x - BTN_W / 2, y - BTN_H / 2, x + BTN_W / 2, y + BTN_H / 2), 1.0, 'CTA pill'))
    draw_text_world(cv, Ty['phone'], tc, S[0], wy(F_PH_Y), t, T_PH)
    draw_text_world(cv, Ty['foot'], tc, S[0], wy(F_FOOT_Y), t, T_PH + 0.06)
    # cursor: enters from the right at pill height, clicks the arrow, leaves the same way
    if T_CLICK - 0.75 <= t < T_CLICK + 0.6:
        import ui
        ty = F_BTN_Y + 26.0
        trk = K.Track([(T_CLICK - 0.75, (1180.0, ty + 30.0), 'out_cubic'), (T_CLICK - 0.06, (842.0, ty), 'hold'),
                       (T_CLICK + 0.1, (842.0, ty), 'in_cubic'), (T_CLICK + 0.45, (1190.0, ty + 40.0))])
        x, y = trk(t)
        press = K.impulse(t, T_CLICK, decay=9.0, attack=0.04)
        cop = K.ramp(t, T_CLICK - 0.75, T_CLICK - 0.55) * (1 - K.ramp(t, T_CLICK + 0.25, T_CLICK + 0.45))
        if cop > 0.01:
            ui.draw_cursor(cv, x, y, 'hand', 84, press=press, click=(t - T_CLICK) if t >= T_CLICK else None,
                           opacity=cop, look='airy')


# ================================================================================================ contract
def draw(t):
    # n_samples is needed for the spin blur share: derive it from samples(t) (pure)
    n = samples(round(t * K.FPS) / K.FPS)
    if t < T_BREAK + 0.6:
        return scene_hook(t, n)
    if t < LEAVE['s0'] + 0.3:
        return scene_message(t, n)
    return scene_stations(t, n)


def post(cv, t):
    return K.post(cv, LOOK, t, vignette=0.10, grain=0.006, bloom=0.35, bloom_threshold=1.3,
                  chroma=0.6 + 2.5 * _move_amount(t))


def _move_amount(t):
    a, b, u = _segment(t)
    return math.sin(math.pi * K.clamp(u)) if b is not None else 0.0


def samples(t):
    if t < 0.45:
        return 5                                   # slam + coin burst toward the lens
    if T_CHIPS - 0.05 < t < T_CHIPS + 0.7 or T_SNAP - 0.15 < t < T_SNAP + 0.2:
        return 5
    if T_BREAK - 0.05 < t < T_BREAK + 0.9:
        return 5
    if _move_amount(t) > 0.05:
        return 6
    if B(30) - 0.05 < t < B(31.4):
        return 5                                   # bus pass
    return 3


def prewarm():
    _type()
    path()
    s_collect()
    _money_assets()
    _hook_assets()
    _break_seeds()
    _near_items()
    _final_assets()


def cues():
    """SFX cue sheet (audio.py catalog names + anim4_sfx customs, align='hit' puts each designed hit on t).
    SFX only, no music. Structural hits sit on the 120 BPM grid (B(n)); pops on 8ths / 16ths."""
    import anim4_sfx
    anim4_sfx.register()
    c = []

    def q(t, name, gain_db=0.0, pan=0.0, **kw):
        d = dict(t=round(float(t), 4), name=name, gain_db=gain_db, pan=pan)
        d.update(kw)
        c.append(d)
    # ---- A HOOK: number slam with coin shimmer, "?" pop, chip burst, snap back
    q(0.0, 'impact_big', -6, params=dict(tail=0.6))
    q(0.0, 'coins_burst', -1)
    q(0.01, 'coin_ring', -5, 0.15)
    q(0.05, 'shimmer', -11, params=dict(dur=1.2))
    q(0.32, 'whoosh_by', -13, -0.3, params=dict(dur=0.8, direction=1))      # burst coins flying past
    q(T_PERWEEK, 'swish_small', -6, -0.1)
    q(T_Q, 'pop', -1, 0.1, params=dict(pitch=0.8))
    q(T_Q, 'bubble_pop', -7, 0.1)
    q(T_Q + 0.01, 'whoosh_fast', -12)
    q(T_CHIPS - 0.02, 'coin_flip', -7)
    q(T_CHIPS, 'swish_small', -5)
    for i in range(5):
        q(T_CHIPS + 0.125 * i + 0.05, 'pop', -5, -0.5 + 0.25 * i, params=dict(pitch=0.95 + 0.07 * i))
        q(T_CHIPS + 0.125 * i + 0.06, 'glass_tap', -13, -0.5 + 0.25 * i, params=dict(pitch=1.0 + 0.05 * i))
    q(T_SNAP, 'reverse_swell', -8, params=dict(duration=0.45))
    q(T_SNAP, 'impact_soft', -4)
    q(T_SNAP + 0.01, 'coin_ring', -6, -0.1, params=dict(pitch=1.05))
    # ---- B the number breaks into coins: coin cascade + stream whoosh; message lines
    q(T_BREAK, 'coins_burst', 0, 0.0, params=dict(n=34))
    q(T_BREAK + 0.02, 'coin_clinks', -4, 0.3, params=dict(n=9, dur=1.1))
    q(T_BREAK + 0.25, 'whoosh_slow', -9, 0.2)
    for i in range(3):
        q(T_MSG + 0.25 * i, 'swish_small', -11, 0.05 * i)
    # money-stream whooshes on every journey leg (peak mid-move), coins chinking along
    legs = [('s0', 'home', 1), ('home', 'food', -1), ('food', 'cloth', 1), ('cloth', 'travel', -1),
            ('travel', 'child', 1)]
    for a, b, dr in legs:
        tm = 0.5 * (LEAVE[a] + ARRIVE[b])
        q(tm, 'whoosh_by', -5, 0.0, params=dict(dur=1.2, direction=dr))
        q(LEAVE[a] + 0.05, 'swish_small', -10, -0.3 * dr)
        q(ARRIVE[b] - 0.05, 'coin_clinks', -6, 0.1 * dr, params=dict(n=6, dur=0.7))
    # ---- C HOME
    q(B(11), 'house_pop', -1)
    q(ARRIVE['home'], 'impact_soft', -9)
    q(ARRIVE['home'] + 0.02, 'sparkle', -14, 0.2)
    q(B(12.5), 'swish_small', -11)
    q(B(13), 'pop', -5, -0.3, params=dict(pitch=0.85))
    q(B(13) + 0.03, 'fabric_swish', -8, -0.3)
    q(B(13.5), 'bubble_pop', -6, 0.35)
    q(B(14), 'glass_tap', -6, 0.3)
    q(B(14.25), 'glass_tap', -7, 0.4, params=dict(pitch=1.12))
    # ---- D FOOD
    q(B(17), 'basket_drop', -3)
    q(ARRIVE['food'], 'impact_soft', -10)
    q(B(18.5), 'pop', -4, -0.3, params=dict(pitch=1.1))
    q(B(18.5), 'swish_small', -12, -0.3)
    q(B(19), 'pop', -5, 0.0, params=dict(pitch=0.95))
    q(B(19.5), 'glass_tap', -5, 0.3, params=dict(pitch=0.8))
    q(B(20) + 0.1, 'swish_small', -11, -0.2)
    q(B(20.5), 'basket_drop', -3, -0.1)
    q(B(20.5) + 0.1, 'swish_small', -12, 0.1)
    q(B(21), 'basket_drop', -5, 0.1)
    # ---- E CLOTHES
    q(B(23), 'impact_soft', -7, 0.2)
    q(B(23) + 0.01, 'fabric_swish', -5, 0.2)
    q(ARRIVE['cloth'], 'impact_soft', -11)
    q(B(24.5), 'fabric_swish', -5, -0.3)
    q(B(25), 'pop', -6, 0.0, params=dict(pitch=0.8))
    q(B(25.5), 'pop', -7, -0.3, params=dict(pitch=1.05))
    for k, tl in enumerate((B(26.5), B(27), B(27.5))):
        q(tl - 0.2, 'fabric_swish', -7, -0.2 + 0.2 * k)
        q(tl, 'impact_soft', -11, 0.2)
    q(B(28), 'zip_pull', -2, 0.2)
    # ---- F TRAVEL
    q(B(30) + 0.625, 'bus_pass', -1, params=dict(dur=1.6))
    q(BOUNCES[0], 'ball_bounce', -1, 0.25)
    q(BOUNCES[1], 'ball_bounce', -5, 0.22, params=dict(pitch=1.05))
    q(BOUNCES[2], 'ball_bounce', -9, 0.2, params=dict(pitch=1.1))
    q(BOUNCES[3], 'ball_bounce', -14, 0.18, params=dict(pitch=1.15))
    q(B(32.5), 'pop', -5, -0.3, params=dict(pitch=0.9))
    q(B(33), 'paint_dab', -2, -0.25)
    q(B(33) + 0.09, 'paint_dab', -9, -0.2)
    # ---- G THE BIGGER PICTURE: arrival at the child, everything gathers, then fades
    q(T_CHILD_POP, 'pop', -4, params=dict(pitch=0.75))
    q(ARRIVE['child'], 'sparkle', -8)
    q(ARRIVE['child'] + 0.02, 'shimmer', -12, params=dict(dur=1.4))
    q(T_GATHER + 0.25, 'whoosh_slow', -7)
    for k in range(6):
        t0 = T_GATHER + 0.125 * k
        q(t0 + 0.3, 'swish_small', -12, (-1) ** k * 0.5)
        q(t0 + 0.62, 'pop', -13, (-1) ** k * 0.4, params=dict(pitch=0.9 + 0.05 * k))
    q(B(37) + 0.25, 'swish_small', -11)
    q(T_FADE[0] + 0.3, 'whoosh_slow', -11, 0.0)
    q(T_FADE[0] + 0.2, 'shimmer', -13, params=dict(dur=1.4))
    # ---- H FINAL: coins rise into the number, end chime, CTA click
    q(T_NUM2 - 0.5, 'coin_flip', -8)
    q(T_NUM2, 'reverse_swell', -9, params=dict(duration=0.5))
    q(T_NUM2, 'impact_soft', -3)
    q(T_NUM2 + 0.01, 'coin_ring', -4)
    q(T_NUM2 + 0.3, 'shimmer', -12, params=dict(dur=1.0))
    q(T_PC, 'swish_small', -11)
    q(T_STMT, 'swish_small', -10, 0.1)
    q(T_LOGO + 0.05, 'whoosh_fast', -10, -0.2)
    q(T_LOGO + 0.55, 'soft_chime', -2)
    q(T_ASK, 'swish_small', -11)
    q(T_BTN, 'pop', -5, params=dict(pitch=0.9))
    q(T_PH, 'ui_tick', -10)
    q(T_CLICK, 'ui_click', 0, 0.3)
    return c


# ================================================================================================ dev checks
def checks(step=1.0 / 15, t0=0.0, t1=None, verbose=True):
    """Dev layout QA over [t0, t1): renders each sampled frame (1 sample, no post) with the box recorder on and
    returns worst margins (px; negative = violation): 'safe' (text inside x 70..1010 / y 230..1480, footer to
    1620; holds only), 'like' (text right edge <= 930 where it spans y 1050..1700; holds only), 'coin_text' /
    'prop_text' (gap between text and coins / props, any time), 'text_text'; plus a list of violations."""
    t1 = DUR if t1 is None else t1
    prewarm()
    worst = dict(safe=(1e9, None), like=(1e9, None), coin_text=(1e9, None), prop_text=(1e9, None),
                 text_text=(1e9, None))
    bad = []

    def upd(k, v, where):
        if v < worst[k][0]:
            worst[k] = (round(float(v), 1), where)
        if v < 0:
            bad.append((k, round(float(v), 1), where))

    def gap(a, b):
        return max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])
    for t in np.arange(t0, t1, step):
        X.REC = []
        try:
            draw(float(t))
            rec = X.REC
        finally:
            X.REC = None
        a_, b_, u_ = _segment(t)
        hold = b_ is None
        texts = [r for r in rec if r[0] == 'text']
        for r in texts:
            x0, y0, x1, y1 = r[1]
            lab = r[3] if len(r) > 3 else ''
            where = (round(float(t), 3), lab)
            if hold and r[2] > 0.9:
                ylim = 1620.0 if 'Weekly' in lab else 1480.0
                upd('safe', min(x0 - 70, 1010 - x1, y0 - 230, ylim - y1), where)
                if y1 > 1050 and y0 < 1700:
                    upd('like', 930 - x1, where)
            morph = lab == '£447.60' and (T_BREAK - 0.01 <= t < T_BREAK + 0.15 or T_CHIPS - 0.06 <= t < T_CHIPS + 0.2
                                          or T_SNAP - 0.15 <= t < T_SNAP + 0.1)   # the number <-> coins / hub
            for o in rec:
                if o[0] in ('coin', 'prop') and o[2] > 0.15 and not morph:
                    upd(o[0] + '_text', gap(r[1], o[1]), where + (o[0],))
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                upd('text_text', gap(texts[i][1], texts[j][1]),
                    (round(float(t), 3), texts[i][3] if len(texts[i]) > 3 else '',
                     texts[j][3] if len(texts[j]) > 3 else ''))
    if verbose:
        for k, v in worst.items():
            print('%-10s %s' % (k, v))
        print('violations: %d' % len(bad))
        for b in bad[:60]:
            print('   ', b)
    return worst, bad
