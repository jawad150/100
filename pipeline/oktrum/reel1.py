"""reel1 "Every market" (Oktrum): 22.0 s, LOOK 'neon' (Oktrum profile), BPM 124 (beat 0.484 s).

Contract: BRIEF.md 1-6.1, 9, 10. Scene times follow the real VO (reel1_vo.json, VO wav starts at 0.20 s; the
phrase times below are already edit time). Word onsets inside phrases are read from the VO envelope (see W).
Every on-screen key word is legible on its spoken word (+-2 frames).

Shot list as built (t in s, beat n = n * 0.4839)
| t | VO word | picture / camera | transition | SFX (draft cues) |
|---|---|---|---|---|
| 0.00-0.97 | Forex 0.26 | coin_usd flips in from depth to below the word; FOREX extrude3d_brand 210 px slams at y 760 (solid 0.26), camera judder, exposure kick | whip right at beat 2 (0.968) | whoosh_fast 0.16, impact_big 0.26 |
| 0.97-1.94 | Gold 1.19 | gold_bar punches in with a warm rim light (the reel's only gold); GOLD in the gold preset | whip at beat 4 (1.935) | whip 0.968, impact_big + coin_ring 1.19 |
| 1.94-2.90 | Bitcoin 2.10 | coin_btc flips in with spin blur (7 samples); BITCOIN | whip at beat 6 (2.903) | whip, coin_flip 1.98, impact_big 2.10 |
| 2.90-3.87 | Nvidia 3.17 | chip slides in from the right with a cyan core flare; ticker_tape streaks across behind it (y ~1300) | whip at beat 8 (3.871) | whip, impact_big 3.17, riser -> 3.871 |
| 3.87-5.80 | All on one platform 4.11 / one 4.42 / platform 4.62 | the four objects ring the centre, are pulled in (4.05-4.50) and burst into the dot_sphere (assemble 4.30-5.10); "All on *one* / platform." words rise on their words; six asset_tag on an orbit ring from 4.85 | camera orbits (easy ease) | whip 3.871 (+ music drop), sub_drop 3.871, impact_soft 4.50, shimmer 4.70 |
| 5.80-8.42 | forex 6.12 commodities 6.67 stocks 7.36 indices 7.80 crypto 8.33 | sphere rises to y ~760; glass chips pop one per word (newest selected) at y 1290/1395; orbit continues | | glass_tap per chip |
| 8.42-9.05 | MetaTrader 8.95 | dolly zoom-through the sphere (zoom blur, 7 samples) into a glass MT5 dashboard window (candles + 3 site ticker rows) | continuous camera | reverse_swell -> 8.78, air_zoom 8.78 |
| 8.95-10.20 | (on MetaTrader 5) | "Powered by MetaTrader 5" rises at 8.95, light sweep; window drifts, candles draw | camera pushes into the window, cut 10.20 inside a zoom blur | |
| 10.20-12.52 | Spreads 10.44 / zero 11.0 / two 11.71 / pips 11.95 | card tunnel of market cards rushes and brakes on the counter card (11.05); "Spreads from" at 10.44; counter rolls 2.0 -> 0.2 (lands 11.71) + PIPS | whip down, cut 12.52 | whoosh_by 10.40, slot_tick (start) 11.0, check_ding 11.71 |
| 12.52-14.03 | Zero 12.69 / hidden 13.0 / fees 13.40 | "0%" slams at 12.69 and shatters a glass fee tag; "Zero Hidden Fees" word by word | push-through + zoom blur, cut 14.03 (beat 29) | whip 12.52, impact_big + glitch_short 12.69 |
| 14.03-16.80 | Oktrum 14.24 / Trade 15.08 / markets 15.62 / precision 16.30 | the dot globe re-assembles big at the bottom; the Oktrum wordmark (logo file, dark pool, no bloom) at 14.24; "Trade the global / markets with / *precision.*" (serif accent) with a light sweep 16.35 | continuous | impact_soft 14.03, shimmer 14.24, shimmer 16.35, riser -> 16.85 |
| 16.80-22.00 | Try 17.24 / demo 17.68 | type exits; the globe flies up and shrinks into the logo mark; okt_mark night_anim resolves (16.95-17.55) and cross-fades dot-for-dot into the flat logo (17.45-17.60, 760 px wide) as the wordmark wipes in; "Try Demo Free" button pops 17.24, cursor press 17.68; oktrum.com; risk line (30 px); settled 18.25-22.0 | hold | logo_sting 17.05, pop 17.24, ui_click + toggle_on 17.68 |

Placeholders: every 3D asset whose <WS>/assets3d/<name>/<folder>/meta.json is missing is drawn as a labelled
stand-in of the same size and anchor (coins flip, bar and chip yaw); the real sprites switch in automatically.
Brand: logo files only (never re-typeset), dark pool behind the logo, logo drawn after the bloom (post) so no
bloom crosses the wordmark; no particles on logo or copy. Ticker figures: only EUR/USD, BTC/USD, XAU/USD carry
site figures; NVDA / S&P 500 / WTI OIL tags are label-only.
"""
import functools
import json
import math
import os

import cv2
import numpy as np

import oktrum_kit as OK
from oktrum_kit import K, T, ui, S3

DUR, LOOK, BPM = 22.0, 'neon', 124
BEAT = 60.0 / BPM
HALF = 0.5 / K.FPS
HERE = os.path.dirname(os.path.abspath(__file__))


def B(n):
    return K.beat(n, BPM)


# ---------------------------------------------------------------------------------------------- VO word times
def _phrases():
    try:
        with open(os.path.join(HERE, 'reel1_vo.json')) as f:
            return [p['t0'] for p in json.load(f)['phrases']]
    except (OSError, KeyError, ValueError):
        return [0.26, 1.19, 2.10, 3.17, 4.11, 5.79, 10.44, 12.69, 14.24, 15.08, 17.24]


_P = _phrases()
# phrase onsets from reel1_vo.json; words inside phrases from the VO envelope (10 ms RMS, gaps / plosive closures)
W = dict(forex=_P[0], gold=_P[1], bitcoin=_P[2], nvidia=_P[3], allon=_P[4], one=4.42, platform=4.62,
         trade=_P[5], l_forex=6.12, l_comm=6.67, l_stocks=7.36, l_ind=7.80, l_crypto=8.33, mt5=8.95,
         spreads=_P[6], zero=11.00, two=11.71, pips=11.95, zero_fees=_P[7], hidden=13.00, fees=13.40,
         oktrum=_P[8], trade_g=_P[9], markets=15.62, precision=16.30, cta=_P[10], demo=17.68)

# section boundaries (hard switches happen at whip peaks / inside zoom blurs; dispatch on t + HALF)
WHIPS = (B(2), B(4), B(6), B(8))            # 0.968 1.935 2.903 3.871: hook whips, the last one into the globe
T_TUN = 10.20                               # dashboard push-in -> card tunnel
T_ZERO = 12.52                              # whip down -> 0 % fees
T_GLOBE2 = B(29)                            # 14.03: globe returns (cut inside a zoom blur)
E0 = 16.80                                  # end card begins (type exits, globe -> logo mark)
TC = W['demo']                              # cursor press
WD, WDIST = 0.13, 1300.0                    # whip half-duration and travel (world px)
BG_I = 0.34                                 # backdrop intensity: the poster's black void

INK = OK.ink(LOOK)


# ---------------------------------------------------------------------------------------------- 3D assets
OBJ = dict(usd=('coin_usd', 'night', 'spin', 900, '#C9D2E6', 'coin'),
           btc=('coin_btc', 'night', 'spin', 900, '#F2C46D', 'coin'),
           gold=('gold_bar', 'night', None, 720, '#E8B54A', 'bar'),
           chip=('chip', 'night', None, 720, '#1B2140', 'chip'),
           mark=('okt_mark', 'night', 'anim', 1000, '#5170FF', 'coin'))


def _folder(var, mode):
    return f'{var}_{mode}' if mode else var


def ready(key):
    """True once the Blender artist's meta.json exists (render finished); checked per frame (a stat call)."""
    name, var, mode = OBJ[key][:3]
    return os.path.exists(os.path.join(K.ASSETS3D, name, _folder(var, mode), 'meta.json'))


@functools.lru_cache(maxsize=8)
def placeholder(key):
    """Labelled stand-in, same sprite size as the real render (half resolution; it is drawn at world size)."""
    name, var, mode, size, hexc, shape = OBJ[key]
    s = size // 2
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    cx = cy = s / 2
    col = K.hexlin(hexc)
    if shape == 'coin':
        r = s * 0.36
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        m = np.clip(r - d, 0, 1.5) / 1.5
        shade = 0.55 + 0.45 * np.clip(1 - (yy - cy + r) / (2 * r), 0, 1)
        ring = np.clip(1 - np.abs(d - r * 0.82) / 3, 0, 1)
        rgb = col * shade[..., None] * 0.8 + ring[..., None] * 0.6
    elif shape == 'bar':
        m = ((np.abs(xx - cx) < s * 0.36) & (np.abs(yy - cy) < s * 0.16)).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        rgb = col * (0.5 + 0.5 * np.clip((cy + s * 0.16 - yy) / (s * 0.32), 0, 1))[..., None]
    else:
        m = ((np.abs(xx - cx) < s * 0.30) & (np.abs(yy - cy) < s * 0.30)).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        core = np.clip(1 - np.maximum(np.abs(xx - cx), np.abs(yy - cy)) / (s * 0.12), 0, 1)
        rgb = col * 0.6 + core[..., None] * K.C['CYAN'] * 2.0
    spr = np.zeros((s, s, 4), np.float32)
    spr[..., :3] = rgb * m[..., None]
    spr[..., 3] = m
    lab = T.render(f'{name} {_folder(var, mode)} placeholder', 'ui', px=max(14, s // 22), fill='IVORY')
    lab.draw(spr, s / 2, s * 0.90)
    return spr


def obj_sprite(key, ang=0.0, t=None):
    """(sprite, x_squash): the real Blender frame at angle `ang` (spin: any deg; yaw: clamped) or the stand-in.
    The stand-in fakes a coin flip with a horizontal squash, so pass x_squash to the billboard width."""
    if ready(key):
        name, var, mode = OBJ[key][:3]
        a = S3.get(name, var, mode=mode)
        if mode == 'anim' and t is not None:
            return a.at_time(t, loop=False), 1.0
        return a.at_yaw(ang), 1.0
    sq = 1.0
    if OBJ[key][5] == 'coin' and key != 'mark':
        sq = max(0.06, abs(math.cos(math.radians(ang))))
    return placeholder(key), sq


# ---------------------------------------------------------------------------------------------- static sprites
TAGS = (('EUR/USD', '1.0847', 0.12), ('XAU/USD', '2,338.40', -0.44), ('BTC/USD', '67,420', 2.34),
        ('NVDA', None, None), ('S&P 500', None, None), ('WTI OIL', None, None))   # site figures only on the first 3
CHIPS = (('Forex', 'l_forex'), ('Commodities', 'l_comm'), ('Stocks', 'l_stocks'), ('Indices', 'l_ind'),
         ('Crypto', 'l_crypto'))
RISK = ('Trading involves high risk. You could lose', 'some or all of your investment.')


@functools.lru_cache(maxsize=1)
def assets():
    d = {}
    d['FOREX'] = T.render('FOREX', 'extrude3d_brand', px=210)
    d['GOLD'] = T.render('GOLD', 'gold', px=210)
    d['BITCOIN'] = T.render('BITCOIN', 'extrude3d_brand', px=210)
    d['NVIDIA'] = T.render('NVIDIA', 'extrude3d_brand', px=210)
    d['allon'] = T.render('All on', 'flat', px=150, fill='IVORY')
    d['one'] = T.render('one', 'serif_italic', px=190, fill=('HOT_PINK', 'CYAN'), fill_angle=-45)
    d['platform'] = T.render('platform.', 'flat', px=150, fill='IVORY')
    d['powered'] = T.render('Powered by MetaTrader 5', 'flat', px=70, fill='IVORY')
    d['spreads'] = T.render('Spreads from', 'flat', px=72, fill='IVORY')
    d['pips'] = T.render('PIPS', 'flat', px=96, fill='CYAN')
    d['counter'] = T.Counter('mono', px=230, prefix='', decimals=1, fill='IVORY')
    d['zero'] = T.render('0%', 'extrude3d_brand', px=330)
    for w in ('Zero', 'Hidden', 'Fees'):
        d['zf_' + w] = T.render(w, 'flat', px=100, fill='IVORY')
    d['l1'] = T.render('Trade the global', 'flat', px=110, fill='IVORY')
    d['l2'] = T.render('markets with', 'flat', px=110, fill='IVORY')
    d['prec'] = T.render('precision.', 'serif_italic', px=200, fill=('HOT_PINK', 'CYAN'), fill_angle=-45)
    d['url'] = T.render('oktrum.com', 'ui', px=40, fill='IVORY')
    d['risk'] = [T.render(s, 'ui', px=30, fill=('IVORY', 0.82)) for s in RISK]
    d['tags'] = [OK.asset_tag(lab, pr, ch, look=LOOK, size=26, h=64) for lab, pr, ch in TAGS]
    d['chips'] = [ui.chip(c, 0.0, look=LOOK, size=38, h=84) for c, _ in CHIPS]
    d['chips_sel'] = [ui.chip(c, 1.0, look=LOOK, size=38, h=84) for c, _ in CHIPS]
    d['glow'] = K.radial(512, (1, 1, 1), power=2.2)
    d['pool'] = K.radial(1400, K.C['NAVY'] * 0.25, power=1.4)
    d['dust'] = K.Particles(90, seed=11, bright=0.45, colors=[K.C['CYAN'], K.C['HOT_PINK'], K.C['VIOLET']])
    d['win'] = ui.app_window(w=860, h=980, look=LOOK, title='MetaTrader 5', header='Integrated Multi-Asset Dashboard',
                             header_size=40, sidebar=False, icons=())
    d['tunnel'] = tunnel_cards()
    d['ccard'] = ui.glass_card(820, 520, r=48, look=LOOK, rim=1.2)
    d['fee'] = fee_tag()
    d['logo'] = logo_parts()
    return d


def prewarm():
    assets()


# ---------------------------------------------------------------------------------------------- helpers
def whip_ox(t, t_in=None, t_out=None):
    """Camera pan offset (world px) for a shot that whips in at t_in and out at t_out (None = no whip)."""
    ox = 0.0
    if t_in is not None and t < t_in + WD:
        u = K.clamp((t - t_in) / WD)
        ox = -WDIST * (1 - K.EASE['out_cubic'](u))
    if t_out is not None and t > t_out - WD:
        u = K.clamp((t - (t_out - WD)) / WD)
        ox = WDIST * K.EASE['in_cubic'](u)
    return ox


def whip_speed(t, t_in=None, t_out=None):
    e = 1.0 / 240
    return abs(whip_ox(t + e, t_in, t_out) - whip_ox(t - e, t_in, t_out)) / (2 * e)


def judder(t, t0, amp=16.0, freq=7.0, decay=9.0, seed=0):
    """Damped hit judder (starts at 0 on the hit: sin, so no jump inside the hit frame)."""
    d = t - t0
    if d <= 0 or d > 1.2:
        return 0.0, 0.0
    e = amp * math.exp(-decay * d)
    return e * math.sin(2 * math.pi * freq * d), 0.6 * e * math.sin(2 * math.pi * freq * 1.31 * d + 0.7 + seed)


def rise(cv, ts, t, t0, x, y, dy=42.0, dur=0.40, out0=None, out_dur=0.25, blur=9.0, anchor=(0.5, 0.5),
         sweep=None, sweep_kw=None, lead=0.10):
    """Word build-on that is legible on t0 (starts `lead` s before), eased exit from out0."""
    if t < t0 - lead:
        return
    u = K.ramp(t, t0 - lead, t0 - lead + dur, 'out_cubic')
    op = K.ramp(t, t0 - lead, t0 + 0.02, 'inout_sine')
    yy = y + dy * (1 - u)
    b = blur * (1 - K.ramp(t, t0 - lead, t0 + 0.04, 'out_cubic'))
    if out0 is not None and t > out0:
        e = K.ramp(t, out0, out0 + out_dur, 'in_cubic')
        op *= 1 - e
        yy -= 36 * e
        b += 10 * e
    if op > 1e-3:
        ts.draw(cv, x, yy, anchor=anchor, opacity=op, blur=b, sweep=sweep, sweep_kw=sweep_kw)


def slam_word(cv, ts, t, t0, x, y, out0=None):
    """Hero slam: 1.45x -> 1 on a spring, solid on t0 (opacity ramps over the 3 frames before)."""
    if t < t0 - 0.11:
        return
    s = K.lerp(1.45, 1.0, K.spring(t - (t0 - 0.11), freq=3.0, damping=0.48))
    op = K.ramp(t, t0 - 0.11, t0 - 0.01, 'linear')
    b = 7.0 * (1 - K.ramp(t, t0 - 0.11, t0, 'out_cubic'))
    s *= 1 + 0.035 * K.ramp(t, t0, t0 + 1.2, 'linear')
    if out0 is not None:
        op *= 1 - K.ramp(t, out0, out0 + 0.07, 'linear')
    if op > 1e-3:
        ts.draw(cv, x, y, scale=s, opacity=op, blur=b)


def keep_mask(rects, soft=60.0):
    return _keep_mask(tuple(tuple(int(v) for v in r) for r in rects), soft)


@functools.lru_cache(maxsize=8)
def _keep_mask(rects, soft):
    yy = np.arange(K.H, dtype=np.float32)[:, None]
    xx = np.arange(K.W, dtype=np.float32)[None, :]
    m = np.ones((K.H, K.W), np.float32)
    for x0, y0, x1, y1 in rects:
        dx = np.maximum(np.maximum(x0 - xx, xx - x1), 0)
        dy = np.maximum(np.maximum(y0 - yy, yy - y1), 0)
        m = np.minimum(m, np.clip(np.sqrt(dx * dx + dy * dy) / soft, 0, 1))
    return m[..., None]


def dust_clear_of(cv, cam, t, rects, opacity=1.0):
    layer = np.zeros_like(cv)
    assets()['dust'].draw(layer, cam, t)
    cv[..., :3] += layer[..., :3] * keep_mask(rects) * opacity


def glow_at(cv, cam, P, width, color, strength):
    """Additive soft light of `width` world units at world P (projected; no DOF)."""
    if strength <= 1e-3:
        return
    spr = assets()['glow']
    xy, dep = cam.project(np.array([P], np.float64))
    if dep[0] <= 10:
        return
    sc = width * cam.focal / dep[0] / spr.shape[1]
    _add_tinted(cv, spr, xy[0][0], xy[0][1], sc, np.asarray(color, np.float32) * strength)


def _add_tinted(cv, spr, x, y, scale, rgb):
    """Additive tinted copy of a white radial (no per-frame sprite build: tint applied on the patch)."""
    sh, sw = spr.shape[:2]
    w = int(sw * scale)
    if w < 4:
        return
    img = cv2.resize(spr[..., 3], (w, w), interpolation=cv2.INTER_LINEAR)
    x0, y0 = int(round(x - w / 2)), int(round(y - w / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(K.W, x0 + w), min(K.H, y0 + w)
    if X1 <= X0 or Y1 <= Y0:
        return
    a = img[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    cv[Y0:Y1, X0:X1, :3] += a[..., None] * rgb[None, None, :3]


# ---------------------------------------------------------------------------------------------- hook (0-3.87)
HOOK = (dict(key='usd', word='FOREX', ts=W['forex'], acc=('CYAN', 0.9), fly=0.55, spin=-300.0),
        dict(key='gold', word='GOLD', ts=W['gold'], acc=('AMBER', 1.0), fly=0.42, spin=0.0),
        dict(key='btc', word='BITCOIN', ts=W['bitcoin'], acc=('VIOLET', 1.0), fly=0.50, spin=-720.0),
        dict(key='chip', word='NVIDIA', ts=W['nvidia'], acc=('CYAN', 1.2), fly=0.38, spin=0.0))
OBJ_Y = 300.0          # object rest position (world y; z=0 -> screen y 1260)
WORD_Y = 760


def hook_obj(k, t):
    """World position, billboard width, sprite angle, opacity of the hook object k."""
    h = HOOK[k]
    ts, fly = h['ts'], h['fly']
    t0 = ts - fly
    u = K.clamp((t - t0) / fly)
    drift = 160.0 * K.ramp(t, ts, ts + 1.6, 'linear')
    if h['key'] == 'chip':
        e = K.EASE['out_cubic'](u)
        x = K.lerp(1100.0, 0.0, e)
        z = K.lerp(900.0, 0.0, e) - drift
        ang = K.lerp(-34.0, 0.0, e) + 6.0 * math.sin(1.7 * (t - ts))
    else:
        e = K.EASE['out_quart'](u)
        x = K.lerp(-60.0, 0.0, e)
        z = K.lerp(7200.0, 0.0, e) - drift
        if h['key'] == 'gold':
            ang = K.lerp(-40.0, 0.0, K.EASE['out_cubic'](u)) + 9.0 * math.sin(1.4 * (t - ts))
        else:
            ang = h['spin'] * (1 - K.EASE['out_cubic'](K.clamp((t - t0) / (fly + 0.12)))) \
                + 14.0 * math.sin(1.5 * max(0.0, t - ts))
    # landing bump: slight squash toward the camera, spring back (starts at 0 on the hit)
    d = t - ts
    if d > 0:
        z -= 90.0 * math.exp(-7.0 * d) * math.sin(2 * math.pi * 2.2 * d)
    op = K.ramp(t, t0, t0 + 0.06, 'linear')
    width = 900.0 if h['key'] in ('usd', 'btc') else 980.0
    return (x, OBJ_Y, z), width, ang, op


def hook_cam(k, t, ox):
    ts = HOOK[k]['ts']
    jx, jy = judder(t, ts, amp=18.0, seed=k)
    return K.Cam(pos=(ox + jx, jy, -1500.0), aperture=26, focus_dist=1500.0)


def draw_hook(t, k):
    A = assets()
    h = HOOK[k]
    t_in = WHIPS[k - 1] if k > 0 else None
    t_out = WHIPS[k]
    ox = whip_ox(t, t_in, t_out)
    cam = hook_cam(k, t, ox)
    ts = h['ts']
    hit = K.impulse(t, ts, decay=5.0)
    cv = K.background(LOOK, t, cam, center=(0.5, 0.64), rim=0.0, intensity=BG_I + 0.2 * hit, boost=0.3 * hit)
    P, width, ang, op = hook_obj(k, t)
    acc = K.C[h['acc'][0]] * h['acc'][1]
    # accent light behind the object (warm only on GOLD)
    glow_at(cv, cam, (P[0], P[1] - 20, P[2] + 260), 1500.0, acc * 0.35, op * (0.55 + 0.9 * hit))
    if h['key'] == 'chip':
        top = K.ramp(t, ts - 0.12, ts + 0.05, 'inout_sine') * (1 - K.ramp(t, t_out - WD, t_out - WD + 0.1, 'linear'))
        if top > 0:
            OK.ticker_tape(cv, t, 0, look=LOOK, speed=900.0, size=34, h=92, opacity=top,
                           plane=dict(cam=cam, center=(0.0, 360.0, 420.0), width=2300, rot=(10, -16, -7)))
    spr, sq = obj_sprite(h['key'], ang)
    if op > 0:
        K.draw_billboard(cv, spr, cam, P, width * sq, opacity=op, height=width)
    if h['key'] == 'gold':          # warm rim: the reel's only gold beat
        glow_at(cv, cam, (P[0] + 260, P[1] - 120, P[2] - 40), 700.0, K.C['AMBER'] * 0.9, op * 0.5 * (0.4 + hit))
    dust_clear_of(cv, cam, t, [(80, WORD_Y - 130, 1000, WORD_Y + 130)], opacity=0.8)
    wx = 540.0 - ox
    jx, jy = judder(t, ts, amp=10.0, seed=k + 3)
    out0 = t_out - WD
    slam_word(cv, A[h['word']], t, ts, wx + jx, WORD_Y + jy, out0=out0)
    # flare on the hit
    if hit > 0.02:
        xy, dep = cam.project(np.array([P], np.float64))
        if dep[0] > 10:
            col = K.C['CYAN'] if h['key'] != 'gold' else K.C['AMBER']
            OK.streaks(cv, [(xy[0][0], xy[0][1] - 40, 1.0)], strength=0.8 * hit, color=col, length=760)
    v = whip_speed(t, t_in, t_out)
    K.whip_blur(cv, v / 60.0 * 0.85)
    return cv


# ---------------------------------------------------------------------------------------------- globe (3.87-10.2)
C = np.array([0.0, 120.0, 0.0])
RING_OFF = ((-390.0, -250.0), (390.0, -250.0), (-390.0, 250.0), (390.0, 250.0))
ZS0, ZS1 = 8.50, 9.00            # zoom-through dolly
WIN_D = 2800.0                    # window distance beyond the sphere along the zoom axis
DIST_END = -1350.0


def globe_dist(t):
    """Orbit distance (negative = past the sphere centre) for the dolly-through and the window push."""
    if t < ZS0:
        return 1500.0
    if t < ZS1:
        return K.lerp(1500.0, DIST_END, K.EASE['inout_cubic'](K.clamp((t - ZS0) / (ZS1 - ZS0))))
    d = DIST_END - 60.0 * (t - ZS1)
    if t > 9.92:
        d -= 1150.0 * K.EASE['in_cubic'](K.clamp((t - 9.92) / (T_TUN - 9.92)))
    return d


def globe_cam(t):
    ox = whip_ox(t, WHIPS[3], None)
    yaw = K.lerp(-26.0, 0.0, K.EASE['easy_ease'](K.ramp(t, WHIPS[3], ZS0, 'linear')))
    pitch = K.lerp(9.0, 3.0, K.ramp(t, WHIPS[3], ZS0, 'inout_sine'))
    lift = 200.0 * K.ramp(t, 5.55, 6.25, 'inout_cubic')
    dist = globe_dist(t)
    tgt = C + np.array([ox, lift, 0.0])
    # focus: the sphere, then the window once the camera is through
    d_sph = max(dist, 200.0)
    d_win = WIN_D - (-dist) if dist < 0 else WIN_D + dist
    f = K.ramp(t, 8.62, 8.95, 'inout_sine')
    focus = K.lerp(d_sph, max(d_win, 200.0), f)
    roll = 2.0 * math.sin(0.6 * t)
    return K.Cam.orbit(tgt, dist, yaw=yaw, pitch=pitch, roll=roll, aperture=30, focus_dist=focus), tgt


def window_pose():
    """Fixed world pose of the dashboard window: on the zoom axis (yaw 0, pitch 3) WIN_D beyond the sphere."""
    cam0 = K.Cam.orbit(C + np.array([0.0, 200.0, 0.0]), 1500.0, yaw=0.0, pitch=3.0)
    fwd = cam0.forward
    return C + np.array([0.0, 200.0, 0.0]) + fwd * WIN_D + np.array([0.0, 40.0, 0.0])


def draw_window(cv, cam, t):
    A = assets()
    win = A['win']
    op = K.ramp(t, 8.58, 8.92, 'inout_sine')
    if op <= 0:
        return
    face = win.face_at(sweep=((t - 8.6) * 0.32) % 1, light=K.ramp(t, 9.2, 9.9, 'inout_sine'))
    x, y, sw, sh = win.meta['slot']
    ch = OK.candles(26, int(sw), 430, K.ramp(t, 8.7, 9.9, 'linear'), t, look=LOOK, seed=4, glow=1.0)
    win.put(face, ch, x - OK.PAD, y - OK.PAD + 10)
    ty = y + 470
    for i, tg in enumerate(A['tags'][:3]):
        e = K.ramp(t, 9.05 + 0.12 * i, 9.35 + 0.12 * i, 'out_cubic')
        if e > 0:
            win.put(face, tg.face, x - tg.pad, ty + i * 92 - tg.pad + 20 * (1 - e), opacity=e)
    P = window_pose()
    rot = (4.0 + 1.5 * math.sin(0.8 * t), -8.0 + 3.0 * K.ramp(t, 8.9, 10.2, 'inout_sine'), -1.0)
    win.plane(cv, cam, P, 860.0, rot=rot, face=face, opacity=op)


def draw_globe(t):
    A = assets()
    cam, tgt = globe_cam(t)
    hit = K.impulse(t, 4.50, decay=4.0)
    cv = K.background(LOOK, t, cam, center=(0.5, 0.42), rim=0.0, intensity=BG_I + 0.15 * hit, parallax=0.6)
    draw_window(cv, cam, t)
    # the four hook objects, pulled into the centre
    pull = K.ramp(t, 4.05, 4.50, 'in_cubic')
    if t < 4.55:
        for i, key in enumerate(('usd', 'gold', 'btc', 'chip')):
            ox_, oy_ = RING_OFF[i]
            P = C + np.array([ox_ * (1 - pull), oy_ * (1 - pull), 120.0 * math.sin(i + t)])
            spr, sq = obj_sprite(key, 40.0 * t + 70 * i if key in ('usd', 'btc') else 18 * math.sin(2 * t + i))
            wdt = K.lerp(380.0, 40.0, pull)
            K.draw_billboard(cv, spr, cam, P, wdt * sq, height=wdt, opacity=1 - K.ramp(t, 4.36, 4.52, 'linear'))
    glow_at(cv, cam, C, 1600.0, K.C['BLUE'] * 0.9, hit * 1.2 + 0.25 * K.ramp(t, 4.3, 5.0, 'linear'))
    # sphere + orbit tags (sphere drawn between back and front tags)
    s_op = K.ramp(t, 4.32, 4.62, 'inout_sine')
    asm = K.ramp(t, 4.32, 5.15, 'out_cubic')
    t_op = 1 - K.ramp(t, ZS0 - 0.02, ZS0 + 0.22, 'in_cubic')
    enter = [K.ramp(t, 4.85 + 0.11 * i, 5.25 + 0.11 * i, 'out_cubic') for i in range(len(A['tags']))]

    def mid(c):
        if s_op > 0:
            OK.dot_sphere(c, cam, tuple(C), 300.0, t, spin=14.0, assemble=asm, n=6000, dot=0.22, opacity=s_op,
                          glow=1.0 + 0.6 * hit)
    if t_op > 0 and t > 4.8:
        ui.orbit_ring(cv, cam, A['tags'], phase=(t - 4.8) * 0.045, center=tuple(C), radius=(360.0, 360.0),
                      tilt=16.0, roll=-9.0, look=LOOK, mid=mid, enter=enter, opacity=t_op)
    else:
        mid(cv)
    # copy: "All on one / platform."
    out = 5.55
    x0 = 540 - (408 + 38 + 244) / 2
    rise(cv, A['allon'], t, W['allon'], x0 + 204, 450, anchor=(0.5, 1.0), out0=out)
    rise(cv, A['one'], t, W['one'], x0 + 408 + 38 + 122, 450, anchor=(0.5, 1.0), out0=out, dy=60)
    rise(cv, A['platform'], t, W['platform'], 540, 612, anchor=(0.5, 1.0), out0=out)
    draw_chips(cv, t)
    zb = 0.12 * math.sin(math.pi * K.ramp(t, ZS0 + 0.04, ZS1, 'linear')) ** 2 \
        + 0.10 * K.ramp(t, 9.95, T_TUN, 'in_cubic')
    if zb > 0.003:
        K.zoom_blur(cv, zb)
    # "Powered by MetaTrader 5" (over the zoom blur: legible on its word)
    rise(cv, A['powered'], t, W['mt5'], 540, 330, out0=9.95, out_dur=0.2,
         sweep=K.ramp(t, 9.25, 9.95, 'inout_sine'))
    K.whip_blur(cv, whip_speed(t, WHIPS[3], None) / 60.0 * 0.85)
    return cv


CHIP_ROWS = ((0, 1, 2), (3, 4))


@functools.lru_cache(maxsize=1)
def chip_layout():
    ws = [ui.chip_size(c, 38, 84)[0] for c, _ in CHIPS]
    pos = {}
    for r, row in enumerate(CHIP_ROWS):
        gap = 22
        tot = sum(ws[i] for i in row) + gap * (len(row) - 1)
        x = 540 - tot / 2
        for i in row:
            pos[i] = (x + ws[i] / 2, 1290 + r * 106)
            x += ws[i] + gap
    return pos


def draw_chips(cv, t):
    A = assets()
    pos = chip_layout()
    ex = K.ramp(t, ZS0, ZS0 + 0.2, 'in_cubic')
    times = [W[k] for _, k in CHIPS]
    for i, (c, k) in enumerate(CHIPS):
        t0 = W[k]
        if t < t0 - 0.10:
            continue
        sp = K.spring(t - (t0 - 0.10), freq=3.2, damping=0.5)
        s = K.lerp(0.55, 1.0, sp) * (1 + 0.12 * ex)
        op = K.ramp(t, t0 - 0.10, t0 + 0.0, 'inout_sine') * (1 - ex)
        nxt = times[i + 1] if i + 1 < len(times) else 99.0
        sel = K.ramp(t, t0 - 0.02, t0 + 0.22, 'inout_sine') * (1 - K.ramp(t, nxt, nxt + 0.25, 'inout_sine'))
        x, y = pos[i]
        y += 30 * (1 - K.ramp(t, t0 - 0.10, t0 + 0.25, 'out_cubic'))
        if op <= 1e-3:
            continue
        K.draw(cv, A['chips'][i], x, y, scale=s, opacity=op * (1 - sel), blur=6 * ex)
        if sel > 1e-3:
            K.draw(cv, A['chips_sel'][i], x, y, scale=s, opacity=op * sel, blur=6 * ex)


# ---------------------------------------------------------------------------------------------- tunnel + counter
ZC = 6200.0                     # counter card z
TUN_L = 4300.0
TUN_T1 = 11.05


@functools.lru_cache(maxsize=1)
def tunnel_cards():
    card = ui.glass_card(460, 300, r=36, look=LOOK, rim=1.0)
    faces = []
    rows = (('EUR/USD', '1.0847', 0.12), ('BTC/USD', '67,420', 2.34), ('XAU/USD', '2,338.40', -0.44),
            ('NVDA', None, None), ('S&P 500', None, None), ('WTI OIL', None, None))
    for i, (lab, pr, ch) in enumerate(rows):
        f = card.face_at(sweep=(i * 0.17) % 1)
        tg = OK.asset_tag(lab, pr, ch, look=LOOK, size=26, h=60, rim=0.0)
        card.put(f, tg.face, 18 - tg.pad, 16 - tg.pad)
        lc = OK.line_chart(400, 150, None, 1.0, LOOK, color=K.C['UP'] if (ch or 1) > 0 else K.C['DOWN'],
                           seed=3 + i, glow=0.8, width=3.0)
        card.put(f, lc, 30 - OK.PAD, 110 - OK.PAD)
        faces.append(f)
    lay = []
    for k in range(16):
        th = math.radians(-60.0 + 137.5 * k)
        r = 560.0 + 160.0 * (k % 3)
        P = np.array([r * math.cos(th), 1.25 * r * math.sin(th), ZC - 1500.0 - TUN_L + 700.0 + 300.0 * k])
        rot = (-24.0 * math.sin(th), 24.0 * math.cos(th), ((k * 37) % 21 - 10) * 1.0)
        lay.append((k % len(faces), P, rot))
    return card, faces, lay


def tunnel_z(t):
    u = K.clamp((t - T_TUN) / (TUN_T1 - T_TUN))
    z = ZC - 1500.0 - TUN_L * (1 - K.EASE['out_cubic'](u))
    return z + 40.0 * max(0.0, t - TUN_T1)


def counter_value(t):
    return 2.0 - 1.8 * K.ramp(t, W['zero'], W['two'], 'out_cubic')


def counter_vel(t):
    e = 1.0 / 240
    return (counter_value(t + e) - counter_value(t - e)) / (2 * e)


def draw_tunnel(t):
    A = assets()
    card, faces, lay = A['tunnel']
    ox = whip_ox(t, None, T_ZERO)        # vertical whip out (applied on y)
    roll = 26.0 * (1 - K.ramp(t, T_TUN, TUN_T1 + 0.3, 'out_cubic'))
    cam = K.Cam(pos=(0.0, ox, tunnel_z(t)), roll=roll, aperture=24, focus_dist=1500.0)
    cv = K.background(LOOK, t, cam, center=(0.5, 0.5), rim=0.0, intensity=BG_I, parallax=0.35)
    sc = K.Scene(cam)
    for fi, P, rot in lay:
        dep = cam.depth(P)
        if 30 < dep < 7000:
            op = K.smoothstep(7000.0, 5200.0, dep)
            sc.custom(P, lambda c, cm, P=P, rot=rot, f=faces[fi], op=op: card.plane(
                c, cm, P, 460.0, rot=rot, opacity=op, face=f, frost=0.0, shadow=0.0, dof_scale=1.4))
    ccard = A['ccard']
    PC = (0.0, 0.0, ZC)

    def counter_card(c, cm):
        f = ccard.face_at(sweep=((t - T_TUN) * 0.35) % 1, light=K.ramp(t, W['two'] - 0.1, W['two'] + 0.6,
                                                                         'inout_sine'))
        ccard.plane(c, cm, PC, 820.0, rot=(0, 0, 0), face=f)
        v = counter_value(t)
        spr = A['counter'].sprite(v, counter_vel(t))
        land = K.impulse(t, W['two'], decay=6.0)
        spr.draw_plane(c, cm, (-120.0, 30.0, ZC - 4.0), scale=1.0 + 0.05 * land, anchor=(0.5, 0.5))
        A['pips'].draw_plane(c, cm, (225.0, 30.0 + 42.0, ZC - 4.0), anchor=(0.5, 1.0),
                             opacity=K.ramp(t, W['pips'] - 0.12, W['pips'] + 0.02, 'inout_sine'))
    sc.custom(PC, counter_card)
    sc.render(cv)
    if W['two'] - 0.05 < t < W['two'] + 0.8:
        glow_at(cv, cam, (0.0, 30.0, ZC + 60.0), 1300.0, K.C['BLUE'] * 0.6, K.impulse(t, W['two'], decay=5.0))
    rise(cv, A['spreads'], t, W['spreads'], 540, 590, out0=T_ZERO - WD - 0.04, out_dur=0.12)
    zb = 0.12 * (1 - K.ramp(t, T_TUN, T_TUN + 0.35, 'out_cubic'))
    if zb > 0.003:
        K.zoom_blur(cv, zb)
    K.whip_blur(cv, whip_speed(t, None, T_ZERO) / 60.0 * 0.85, angle=90)
    return cv


# ---------------------------------------------------------------------------------------------- zero fees
@functools.lru_cache(maxsize=1)
def fee_tag():
    """Glass price tag (no copy: a muted % only) cut into shards (Voronoi cells) for the shatter."""
    card = ui.glass_card(440, 250, r=40, look=LOOK, rim=0.9, rim_color=K.C['DOWN'] * 0.8)
    f = card.face.copy()
    pct = T.render('%', 'mono', px=150, fill=('DOWN', 0.9))
    pct.draw(f, card.pad + 290, card.pad + 125)
    hh, ww = f.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    hx, hy = card.pad + 70, card.pad + 125
    d = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
    f *= np.clip((d - 20) / 2.0, 0, 1)[..., None]
    rng = np.random.default_rng(5)
    n = 15
    seeds = np.c_[rng.uniform(card.pad, ww - card.pad, n), rng.uniform(card.pad, hh - card.pad, n)]
    dist = np.stack([(xx - sx) ** 2 + (yy - sy) ** 2 for sx, sy in seeds])
    lab = dist.argmin(0)
    shards = []
    for i in range(n):
        m = (lab == i)
        if m.sum() < 50:
            continue
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        piece = f[y0:y1, x0:x1] * m[y0:y1, x0:x1, None]
        cxp, cyp = (x0 + x1) / 2 - ww / 2, (y0 + y1) / 2 - hh / 2
        shards.append((np.ascontiguousarray(piece, np.float32), cxp, cyp, rng.uniform(-1, 1), rng.uniform(0.6, 1.4)))
    return np.ascontiguousarray(f, np.float32), shards


def draw_zero(t):
    A = assets()
    ts = W['zero_fees']
    oy = whip_ox(t, T_ZERO, None)
    jx, jy = judder(t, ts, amp=20.0, seed=7)
    push = K.ramp(t, 13.88, T_GLOBE2, 'in_cubic')
    cam = K.Cam(pos=(jx, oy + jy, -1500.0 + 300.0 * push), aperture=20)
    hit = K.impulse(t, ts, decay=5.0)
    cv = K.background(LOOK, t, cam, center=(0.5, 0.46), rim=0.0, intensity=BG_I + 0.2 * hit, boost=0.3 * hit)
    sy = -oy
    full, shards = A['fee']
    tag_y = 880 + sy
    if t < ts:
        sw = 6.0 * math.sin(2 * math.pi * 0.9 * (t - T_ZERO))
        K.draw(cv, full, 540, tag_y, rot=sw, opacity=K.ramp(t, T_ZERO - 0.05, T_ZERO + 0.05, 'linear'))
    else:
        d = t - ts
        for piece, cx, cy, spin, spd in shards:
            r = math.hypot(cx, cy) + 1e-3
            vx, vy = cx / r, cy / r
            dist = (520.0 * spd) * (1 - math.exp(-3.2 * d)) + 60.0 * d
            x = 540 + cx * (1 + 0.6 * K.ramp(t, ts, ts + 0.5, 'out_cubic')) + vx * dist
            y = tag_y + cy + vy * dist + 380.0 * d * d
            op = 1 - K.ramp(t, ts + 0.25, ts + 0.75, 'linear')
            if op > 1e-3:
                K.draw(cv, piece, x, y, rot=spin * 260.0 * d, scale=1 + 0.5 * d, opacity=op, blur=3 + 10 * d)
    if hit > 0.02:
        glow_at(cv, cam, (0.0, -60.0, 200.0), 1500.0, K.C['BLUE'] * 0.8, hit)
    sc = 1 + 0.5 * push
    op_all = 1 - K.ramp(t, 13.88, T_GLOBE2, 'linear')
    if t >= ts - 0.11:
        s = K.lerp(2.1, 1.0, K.spring(t - (ts - 0.11), freq=3.0, damping=0.5)) * sc
        op = K.ramp(t, ts - 0.11, ts - 0.01, 'linear') * op_all
        b = 8.0 * (1 - K.ramp(t, ts - 0.11, ts, 'out_cubic')) + 10 * push
        A['zero'].draw(cv, 540 + jx * 0.5, 840 + sy + jy * 0.5, scale=s, opacity=op, blur=b,
                       sweep=K.ramp(t, 13.45, 13.95, 'inout_sine'))
    # "Zero Hidden Fees" word by word on one line
    ws = [T.measure(w, 'flat', px=100)[0] for w in ('Zero', 'Hidden', 'Fees')]
    gap = 30
    x = 540 - (sum(ws) + 2 * gap) / 2
    for w, wd, key in zip(('Zero', 'Hidden', 'Fees'), ws, ('zero_fees', 'hidden', 'fees')):
        cx = x + wd / 2
        x += wd + gap
        if op_all > 0:
            ts_ = A['zf_' + w]
            t0 = W[key] + (0.06 if key == 'zero_fees' else 0.0)
            if t >= t0 - 0.1:
                u = K.ramp(t, t0 - 0.1, t0 + 0.3, 'out_cubic')
                op = K.ramp(t, t0 - 0.1, t0 + 0.02, 'inout_sine') * op_all
                ts_.draw(cv, 540 + (cx - 540) * sc, 1180 + sy + 40 * (1 - u) + 120 * push, scale=sc, opacity=op,
                         blur=8 * (1 - u) + 10 * push)
    zb = 0.10 * push
    if zb > 0.003:
        K.zoom_blur(cv, zb)
    K.whip_blur(cv, whip_speed(t, T_ZERO, None) / 60.0 * 0.85, angle=90)
    return cv


# ---------------------------------------------------------------------------------------------- globe 2 + end card
C9 = (0.0, 300.0, 0.0)
R9 = 380.0
LOGO_W, LOGO_Y = 760, 790
BTN_Y, URL_Y, RISK_Y = 1135, 1292, 1405


@functools.lru_cache(maxsize=1)
def logo_parts():
    full = K.load_image(os.path.join(K.BRAND, 'logo_full.png'), size=LOGO_W)
    wm = K.load_image(os.path.join(K.BRAND, 'logo_wordmark.png'), size=620)
    mark_src = K.load_image(os.path.join(K.BRAND, 'logo_mark.png'))
    s = LOGO_W / 1102.0
    mw = int(round(244 * s))
    a = mark_src[..., 3] > 0.05
    ys, xs = np.nonzero(a)
    # mark sphere in logo px (bbox of the dots), scaled to the end card
    mb = (xs.min() * s, ys.min() * s, (xs.max() + 1) * s, (ys.max() + 1) * s)
    mark = np.ascontiguousarray(full[:, :mw])
    word = np.ascontiguousarray(full[:, mw:])
    return dict(full=full, wm=wm, mark=mark, word=word, mw=mw, mb=mb, h=full.shape[0])


def mark_screen():
    """Screen centre and radius of the logo's dot sphere on the end card."""
    L = assets()['logo']
    x0 = 540 - LOGO_W / 2
    y0 = LOGO_Y - L['h'] / 2
    mb = L['mb']
    return x0 + (mb[0] + mb[2]) / 2, y0 + (mb[1] + mb[3]) / 2, (mb[3] - mb[1]) / 2


def end_cam(t):
    return K.Cam(pos=(0.0, 0.0, -1500.0 + 120.0 * K.ramp(t, T_GLOBE2, DUR, 'linear')), aperture=18,
                 focus_dist=1500.0)


def draw_finale(t):
    A = assets()
    cam = end_cam(t)
    kick = K.impulse(t, T_GLOBE2, decay=5.0)
    endk = K.ramp(t, E0, E0 + 0.8, 'inout_sine')
    cv = K.background(LOOK, t, cam, center=(0.5, 0.66 - 0.2 * endk), rim=0.0, intensity=K.lerp(BG_I + 0.04, BG_I - 0.06, endk),
                      boost=0.3 * kick)
    # globe: big at the bottom, then flies to the logo mark
    mx, my, mr = mark_screen()
    dep = 1500.0 - 120.0 * K.ramp(t, T_GLOBE2, DUR, 'linear')
    mP = ((mx - 540) * dep / 1500.0, (my - 960) * dep / 1500.0, cam.pos[2] + dep)
    mR = mr * dep / 1500.0
    g = K.EASE['inout_cubic'](K.ramp(t, E0, E0 + 0.55, 'linear'))
    P = tuple(K.lerp(np.array(C9, float), np.array(mP, float), g))
    R = K.lerp(R9, mR, g)
    asm = K.ramp(t, T_GLOBE2 - 0.05, T_GLOBE2 + 0.55, 'out_cubic')
    big_op = K.ramp(t, T_GLOBE2 - 0.03, T_GLOBE2 + 0.12, 'inout_sine') * (1 - K.ramp(t, E0 + 0.15, E0 + 0.45,
                                                                                       'inout_sine'))
    if big_op > 0:
        glow_at(cv, cam, (P[0], P[1], P[2] + R), R * 4.0, K.C['BLUE'] * 0.35, big_op * (1 - g))
        OK.dot_sphere(cv, cam, P, R, t, spin=18.0, assemble=asm, n=6000, dot=0.22, opacity=big_op,
                      glow=1.0 + 0.5 * kick)
    # okt_mark 3D (night_anim) resolving at the logo mark position, then the flat logo (drawn in post)
    m_op = K.ramp(t, E0 + 0.12, E0 + 0.35, 'inout_sine') * (1 - K.ramp(t, 17.47, 17.62, 'inout_sine'))
    if m_op > 0:
        if ready('mark'):
            a = S3.get('okt_mark', 'night', mode='anim')
            fr = a.blend(K.clamp((t - (E0 + 0.12)) / (17.52 - (E0 + 0.12))) * (a.n - 1))
            bx0, by0, bx1, by1 = a.bbox
            sc = (2 * mr) / max(1.0, (by1 - by0))
            K.draw(cv, fr, mx, my, scale=sc, opacity=m_op,
                   anchor=(((bx0 + bx1) / 2) / fr.shape[1], ((by0 + by1) / 2) / fr.shape[0]))
        else:
            OK.dot_sphere(cv, cam, mP, mR, t, rot=(-14.0, -50.0 * (1 - K.ramp(t, E0, 17.5, 'out_cubic')), -8.0),
                          spin=0.0, assemble=K.ramp(t, E0 + 0.1, 17.5, 'out_cubic'), n=2600, dot=0.30,
                          opacity=m_op, dof=False)
            ph = T.render('okt_mark night_anim placeholder', 'ui', px=18, fill=('IVORY', 0.6))
            ph.draw(cv, mx, my + mr + 30, opacity=m_op * 0.8)
    # copy
    out = E0 - 0.02
    rise(cv, A['l1'], t, W['trade_g'], 540, 420, out0=out, sweep=K.ramp(t, 16.35, 16.85, 'inout_sine'))
    rise(cv, A['l2'], t, W['markets'], 540, 552, out0=out + 0.04, sweep=K.ramp(t, 16.42, 16.92, 'inout_sine'))
    rise(cv, A['prec'], t, W['precision'], 540, 712, out0=out + 0.08, dy=56,
         sweep=K.ramp(t, 16.40, 16.95, 'inout_sine'))
    # end card UI
    if t > W['cta'] - 0.15:
        b = K.spring(t - (W['cta'] - 0.12), freq=2.6, damping=0.55)
        hover = K.ramp(t, TC - 0.30, TC - 0.08, 'inout_sine')
        btn = ui.button('Try Demo Free', hover=hover, press=K.impulse(t, TC, 9), look=LOOK, h=120, size=44,
                        ripple=(t - TC) if t >= TC else None)
        ui.place(cv, btn, 540, BTN_Y, scale=K.lerp(0.6, 1.0, b), opacity=K.clamp(1.6 * b))
    rise(cv, A['url'], t, 17.40, 540, URL_Y, dy=22, blur=6)
    for i, r in enumerate(A['risk']):
        rise(cv, r, t, 17.50 + 0.05 * i, 540, RISK_Y + 42 * i, dy=16, blur=5)
    cur = K.Track([(TC - 0.42, (840.0, 1640.0)), (TC - 0.04, (575.0, 1158.0)), (TC + 0.30, (575.0, 1158.0)),
                   (TC + 0.62, (880.0, 1700.0))], ease='inout_cubic')
    cop = K.ramp(t, TC - 0.42, TC - 0.26, 'inout_sine') * (1 - K.ramp(t, TC + 0.40, TC + 0.60, 'inout_sine'))
    if cop > 1e-3:
        ui.draw_cursor(cv, *cur(t), 'hand', 84, press=K.impulse(t, TC, 9), click=t - TC if t >= TC else None,
                       look=LOOK, opacity=cop)
    zb = 0.12 * (1 - K.ramp(t, T_GLOBE2, T_GLOBE2 + 0.3, 'out_cubic'))
    if zb > 0.003:
        K.zoom_blur(cv, zb)
    return cv


def draw_logo_post(cv, t):
    """Logo files composited after the bloom (BRAND: no bloom across the wordmark), dark pool drawn in draw()."""
    L = assets()['logo']
    # mid-reel wordmark on "Oktrum"
    ow = K.ramp(t, W['oktrum'] - 0.10, W['oktrum'] + 0.02, 'inout_sine') * (1 - K.ramp(t, 14.95, 15.15, 'in_cubic'))
    if ow > 1e-3:
        s = K.lerp(0.94, 1.0, K.ramp(t, W['oktrum'] - 0.10, W['oktrum'] + 0.5, 'out_cubic'))
        K.draw(cv, L['wm'], 540, 560 - 20 * K.ramp(t, 14.95, 15.15, 'in_cubic'), scale=s, opacity=ow,
               blur=6 * (1 - K.ramp(t, W['oktrum'] - 0.10, W['oktrum'] + 0.04, 'out_cubic')))
    if t < 17.30:
        return cv
    x0 = 540 - LOGO_W / 2
    mo = K.ramp(t, 17.47, 17.62, 'inout_sine')
    if mo > 0:
        K.draw(cv, L['mark'], x0, LOGO_Y, opacity=mo, anchor=(0.0, 0.5))
    u = K.ramp(t, 17.28, 17.62, 'inout_cubic')
    if u > 0:
        wd = L['word']
        ww = wd.shape[1]
        cut = u * (ww + 60)
        ramp_ = np.clip((cut - np.arange(ww, dtype=np.float32)) / 60.0, 0, 1)
        K.draw(cv, wd * ramp_[None, :, None], x0 + L['mw'], LOGO_Y, anchor=(0.0, 0.5),
               blur=4 * (1 - u))
    return cv


# ---------------------------------------------------------------------------------------------- dispatch
SLAMS = (W['forex'], W['gold'], W['bitcoin'], W['nvidia'], W['zero_fees'])


def section(t):
    tc = t + HALF
    for k, tw in enumerate(WHIPS):
        if tc < tw:
            return ('hook', k)
    if tc < T_TUN:
        return ('globe', 0)
    if tc < T_ZERO:
        return ('tunnel', 0)
    if tc < T_GLOBE2:
        return ('zero', 0)
    return ('finale', 0)


def draw(t):
    s, k = section(t)
    if s == 'hook':
        return draw_hook(t, k)
    if s == 'globe':
        return draw_globe(t)
    if s == 'tunnel':
        return draw_tunnel(t)
    if s == 'zero':
        return draw_zero(t)
    cv = draw_finale(t)
    # dark pool behind the logo / wordmark (NAVY, not a glow of the logo's blue)
    pa = max(K.ramp(t, W['oktrum'] - 0.2, W['oktrum'], 'inout_sine') * (1 - K.ramp(t, 15.0, 15.3, 'linear')),
             K.ramp(t, E0 + 0.2, E0 + 0.7, 'inout_sine'))
    if pa > 0:
        y = 560 if t < 15.5 else LOGO_Y
        K.draw(cv, assets()['pool'], 540, y, opacity=0.85 * pa, scale=(0.75 if t < 15.5 else 1.0))
    return cv


def post(cv, t):
    push = sum(K.impulse(t, s, decay=14.0) for s in SLAMS) + 0.6 * K.impulse(t, T_GLOBE2, decay=12.0)
    cv = K.post(cv, LOOK, t, exposure=0.5 * push)
    if section(t)[0] == 'finale':
        draw_logo_post(cv, t)
    return cv


def samples(t):
    fast = any(abs(t - w) < WD + 0.03 for w in WHIPS + (T_ZERO,))
    if fast:
        return 5
    for h in HOOK:
        if h['ts'] - h['fly'] < t < h['ts'] + 0.08:
            return 7 if h['key'] == 'btc' else 5
    if 4.0 < t < 4.6 or 14.0 < t < 14.2 or E0 < t < E0 + 0.6 or 12.6 < t < 13.3:
        return 5
    if ZS0 < t < ZS1 + 0.05 or 9.9 < t < TUN_T1:
        return 7
    return 3


# ---------------------------------------------------------------------------------------------- cues (draft)
def cues():
    c = [dict(t=W['forex'] - 0.10, name='whoosh_fast'), dict(t=W['forex'], name='impact_big')]
    for i, tw in enumerate(WHIPS):
        c.append(dict(t=tw, name='whip', params=dict(direction=1), pan=0.2 if i % 2 else -0.2))
    c += [dict(t=W['gold'], name='impact_big'), dict(t=W['gold'] + 0.02, name='coin_ring', gain_db=-4),
          dict(t=W['bitcoin'] - 0.12, name='coin_flip', gain_db=-2), dict(t=W['bitcoin'], name='impact_big'),
          dict(t=W['nvidia'], name='impact_big'),
          dict(t=WHIPS[3], name='riser', params=dict(duration=0.65), gain_db=-3),
          dict(t=WHIPS[3], name='sub_drop'),
          dict(t=4.50, name='impact_soft'), dict(t=4.70, name='shimmer', gain_db=-4)]
    for _, k in CHIPS:
        c.append(dict(t=W[k], name='glass_tap', gain_db=-2))
    c += [dict(t=8.78, name='reverse_swell', params=dict(duration=0.45), gain_db=-4),
          dict(t=8.78, name='air_zoom'),
          dict(t=W['mt5'], name='shimmer', gain_db=-6),
          dict(t=T_TUN + 0.15, name='whoosh_by', params=dict(direction=1)),
          dict(t=W['zero'], name='slot_tick', align='start', params=dict(dur=W['two'] - W['zero'])),
          dict(t=W['two'], name='check_ding'),
          dict(t=T_ZERO, name='whip', params=dict(direction=-1)),
          dict(t=W['zero_fees'], name='impact_big'), dict(t=W['zero_fees'], name='glitch_short', gain_db=-3),
          dict(t=W['hidden'], name='swish_small', gain_db=-6), dict(t=W['fees'], name='swish_small', gain_db=-6),
          dict(t=T_GLOBE2, name='impact_soft'), dict(t=W['oktrum'], name='shimmer', gain_db=-4),
          dict(t=16.40, name='shimmer', gain_db=-6),
          dict(t=E0 + 0.05, name='riser', params=dict(duration=1.2), gain_db=-6),
          dict(t=E0 + 0.25, name='logo_sting'),
          dict(t=W['cta'], name='pop', gain_db=-3),
          dict(t=TC, name='ui_click'), dict(t=TC + 0.03, name='toggle_on', gain_db=-3)]
    return c
