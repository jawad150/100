"""reel1.py: REEL 1 of 3, "COULD YOU?" (recruitment). NIGHT NEON look. 1080x1920, 30 fps, DUR 26.0 s, 120 BPM.

Render-module contract for render.py: DUR, LOOK, BPM, draw(t) (pure), post(cv, t), samples(t), cues(), prewarm(),
plus BED / BED_GAIN_DB for the SFX bed. AUDIO = SFX ONLY (no music); the client adds 120 BPM music later.

GRID: beat n = n * 0.5 s from t = 0 (bar = 2 s). Every cut, slam and tick lands on a beat, an & (0.25) or a 16th.
The brief's section times (0.45 / 2.45 / 5.3 / 11.6 / 18.4) were snapped onto this grid.

SHOT LIST  (b = beat; SFX = audio.py catalog names, align='hit' at the visual hit)
 time        | shot / on-screen content                         | camera                         | transition in   | SFX
 ------------+--------------------------------------------------+--------------------------------+-----------------+-------------------------------
 0.00-0.50   | 0 COLD OPEN. Near-black void, a thin magenta     | slow push (z +70)              | from black      | heartbeat (lub 0.0, dub 0.30),
 (b0-1)      | light ring irises open on c01 @0.25s (girl's     |                                |                 | ripple 0.04, reverse_swell
             | smile, crop .48/.40 z1.32->1.26); ring pulses on |                                |                 | ending 0.50
             | the lub (0.0) and dub (0.30), blows wide 0.36-0.5|                                |                 |
 0.50-2.50   | 1 HOOK MONTAGE, 8 x 0.25 s full-bleed flashes:   | per-flash punch-in 1.0->1.075, | flash frame on  | flash_hit + impact_soft on the
 (b1-5)      | 0.50 c12@4.15 (.635,.535) mum+boy laughing       | camera shake on each slam      | the beats (word | beats; whip on .75/1.25/2.25
             | 0.75 c10@20.9 (.62,.545) dad+daughter to camera  | (impulse x K.shake),           | slams); whip    | (L/R pan); air_zoom 1.75;
             | 1.00 c08@1.8 piggyback, 1.25 c14@9.5 baby lift + | 1.12x slam punch on beats,     | pans 0.75 /1.25 | shimmer on the leaks 1.25 /
             | kiss, 1.50 c00@1.15 tent, 1.75 c16@2.35 kennel + | zoom-through 1.75, push into   | /2.25 (strip    | 2.25; riser 1.0-2.5
             | leaves, 2.00 c02@4.25 blocks, 2.25 c11@4.45 teddy| the smash at 2.5               | slide + smear), |
             | Slammed 3D words (ivory extrude, plum sides,     |                                | zoom 1.75, light|
             | magenta deep glow, dark scrim slab), one per     |                                | leak sweeps     |
             | beat at y 1300: "A SAFE / HOME." 190px, "EVERY-  |                                | 1.25 / 2.25     |
             | DAY / CARE." 170, "A PLACE" 200, "TO BELONG." 150|                                |                 |
             | (faces framed above the word band y 1150-1460)   |                                |                 |
 2.50-5.50   | 2 THE QUESTION. Smash to the void. Glossy 3D "?" | orbit yaw 8 -> -4, push 1800-> | white smash     | impact_big + sub_drop 2.5;
 (b5-11)     | spins in from z 5600 and lands on b6 (3.0) in a  | 1540 (easy ease), shake on the | frame 2.5; whip | whoosh_by 2.64; glass_tap 3.0;
             | magenta ring portal + glow orb; "Could" 3.25,    | slams, DOF 34; whip DOWN       | down out        | swish 3.25; reverse_swell +
             | "YOU" (3D MAGENTA->ORANGE extrude) slams 3.5,    | 5.25-5.5 (pitch -26, smear)    | 5.25-5.5        | impact_soft 3.5; ui_tick 3.75;
             | "be a" 3.75, "Foster Carer?" (orange deep glow,  |                                |                 | swish 4.0; shimmer 4.05;
             | 132px) 4.0, light sweep on YOU 4.05-4.95; c01 in |                                |                 | whip + whoosh_fast 5.5
             | a tilted glass card far behind (bokeh), dust     |                                |                 |
 5.50-11.50  | 3 "AM I ELIGIBLE?" Perspective glass app window  | arrives from above (pitch 17   | whip down in    | glass_tap 6.0; per tick:
 (b11-23)    | (neon magenta rim, comet sweep, icon sidebar,    | ->0), dolly down the rows      | 5.5; whip pan   | ui_click + check_ding (pitch
             | header "Am I eligible to foster?"). Rows tick    | (labels >= 1.14x, rack focus   | right out       | rising), swish on cursor
             | 6.5 / 7.25 / 8.0 / 8.75 / 9.5 (0.75 s apart):    | follows the active row,        | 11.28-11.5      | moves; sparkle + pop 10.0;
             | arrow cursor glides + clicks, 3D green check tile| aperture 40), pull back 9.75-  |                 | toast_chime 10.5; whip +
             | springs out of the glass, row lights LEAF; ring  | 10.75 to the whole window      |                 | whoosh_fast 11.5
             | 20->100 %, pops on b20 (10.0); toast "You could  | (labels >= 0.98x)              |                 |
             | be a great fit" floats up on b21 (10.5)          |                                |                 |
 11.50-18.50 | 4 SUPPORT DOCK. Headline "Support is part / of   | orbit around the tile row yaw  | whip pan in     | card_slide x3 on 16ths
 (b23-37)    | the role." (100px, sweep 12.3). Three glass tiles| -5 -> 5 (glow plate + bokeh    | 11.5; push into | 11.625-11.875; shimmer 12.3;
             | slide in as a carousel (16ths), coloured glow    | parallax), whip-pan arrival,   | tile 3's footage| per focus: ui_hover, ui_click
             | blobs behind; focus walks L->R on b25/29/33      | push into tile 3 18.22-18.5    | (zoom blur)     | + glass_tap, sparkle glint;
             | (12.5/14.5/16.5): focused tile grows + springs,  |                                | 18.22-18.5      | air_zoom + flash_hit 18.5
             | lights its edge, plays footage (c03@4.6, c04@1.0,|                                |                 |
             | c10@17.4), its glossy 3D icon (grad_cap,         |                                |                 |
             | chat_bubble, coin_gbp night) lifts out to the    |                                |                 |
             | corner, glass glint sweep; hand cursor hovers    |                                |                 |
             | Full Training / Preparation & ongoing learning ·|                                |                 |
             | Ongoing Support / Your supervising social worker |                                |                 |
             | · Weekly Allowance / From £447.60 a week per child|                               |                 |
 18.50-21.00 | 5 PAYOFF. c08 full-bleed, src 3.6 s, 1.0 -> 0.6x | push-in 1.02->1.08 (easy ease) | zoom-through +  | impact_soft + heartbeat
 (b37-42)    | slow-mo, warm key + bottom scrim. "Open your     | + drift; exits with a push +   | flash 18.5;     | reprise 18.75; swish 18.75;
             | home." (112px ivory glow) rises 18.75, "Change a | zoom blur + light leak         | leak flash out  | reverse_swell + impact_soft
             | / child's life." (150px orange deep glow) rises  |                                | 20.7-21.0       | 19.5; shimmer 20.0; riser
             | 19.5; light sweeps 19.2 / 20.0                   |                                |                 | 19.0-21.0
 21.00-26.00 | 6 END CARD. 3D logo mark (logo_mark3d night_anim)| slow settle (z -1700->-1500,   | flash 21.0      | logo_sting + impact_big +
 (b42-52)    | swings in with its specular sweep, magenta/orange| yaw 2->0), float               |                 | sub_drop 21.0; swish 21.75,
             | conic glow rings orbit behind it; wordmark       |                                |                 | shimmer 22.35; sparkle 22.25;
             | (logo_full_onDark crop) wipes in 21.75 + sweep;  |                                |                 | pop 22.75; ui_tick 23.0;
             | "NURTURE • DEVELOP • GROW" 22.25; CTA pill       |                                |                 | sparkle 23.25; swish 23.05;
             | "Start your enquiry →" springs in 22.75; "0161   |                                |                 | ui_click + toggle_on 23.5
             | 241 1332 · organicfostering.co.uk" 23.0; "Rated  |                                |                 |
             | Good by Ofsted / Inspected May 2025" badge 23.25;|                                |                 |
             | hand cursor clicks the CTA on b47 (23.5: press + |                                |                 |
             | ripple), leaves by 24.35; complete card holds    |                                |                 |
             | 24.35-26.0 (1.65 s static, 3.0 s since the click)|                                |                 |
 Bed: room_tone at -30 dB (felt, not heard). Mix: -18 LUFS integrated, <= -1.5 dBTP (audio.build_reel).

Depth on every shot: backdrop / footage plate, the subject layer (type, UI, 3D), and a near layer (defocused bokeh
billboards, dust particles through the camera's DOF, light leaks). Footage is graded 'neon'; montage and payoff
frames use K.post(..., footage=1).

    python3 render.py reel1 --sheet 48 --samples 1 --workers 1
    python3 reel1_dev.py strip 0.6,3.6,8.1 --samples 3       (review helper)
"""
import functools
import math
import os

import numpy as np

import core as K

DUR = 26.0
LOOK = 'neon'
BPM = 120
BEAT = 60.0 / BPM                      # 0.5 s
BED, BED_GAIN_DB = 'room_tone', -30.0

# section starts, all on the 120 BPM grid (beat n at n * 0.5 s from t = 0)
T_HOOK, T_Q, T_LIST, T_DOCK, T_PAY, T_END = 0.5, 2.5, 5.5, 11.5, 18.5, 21.0


def _lazy():
    import footage as F
    import sprites3d as S3
    import type3d as T
    import ui
    return F, S3, T, ui


def _ease(t, t0, t1, e='out_expo'):
    return K.ramp(t, t0, t1, e)


def _post(cv, t, hot=0.0, kick=0.0, **kw):
    """Finishing without K.flash (its additive ivory term lifts the blacks into a grey veil). hot = a cut 'flash
    frame' as an exposure push + bloom (multiplicative: blacks stay black, highlights blow out hot); kick = a warm
    bloom-only lift for slams (adds light only where there already is light)."""
    L = K.LOOKS[LOOK]
    if hot > 1e-3:
        kw['exposure'] = kw.get('exposure', 0.0) + 1.45 * hot
    if hot > 1e-3 or kick > 1e-3:
        kw['bloom'] = kw.get('bloom', L['bloom']) * (1.0 + 0.9 * hot + 0.6 * kick)
        kw['halation'] = kw.get('halation', L['halation']) + 0.10 * kick + 0.06 * hot
    return K.post(cv, LOOK, t, **kw)


def _swell(t, t0, rise=0.15, decay=4.0):
    """Smooth 0..1 kick: eases up over `rise` (no one-frame pop), then decays exponentially."""
    if t < t0:
        return 0.0
    if t < t0 + rise:
        return K.EASE['inout_sine'](K.clamp((t - t0) / rise))
    return math.exp(-(t - t0 - rise) * decay)


def _blip(t, t0, rise=0.012, decay=14.0):
    """Sharp 0..1 pulse peaking at t0 (a flash frame on the cut), symmetric-ish attack."""
    if t < t0 - rise:
        return 0.0
    if t < t0:
        return K.clamp((t - (t0 - rise)) / rise)
    return math.exp(-(t - t0) * decay)


# =============================================================================================== shared assets
@functools.lru_cache(maxsize=1)
def _common():
    d = {}
    d['ring'] = K.glow(K.ring(300, 4, K.C['HOT_PINK'] * 2.4), K.C['MAGENTA'], (8, 28, 80), 1.3)
    d['dust'] = K.Particles(170, seed=7, bright=0.85, size=(1.2, 3.6))
    # near, heavily defocused bokeh for the foreground depth layer over footage
    d['fg_bokeh'] = K.Particles(16, seed=21, box=((-900, -1500, 220), (900, 1500, 900)), vel=(0, -40, 0),
                                size=(5.0, 12.0), colors=[K.C['HOT_PINK'], K.C['ORANGE'], K.C['AMBER']],
                                bright=0.55, twinkle=0.3)
    return d


def _static_cam(t, aperture=40):
    return K.Cam(pos=(0, 0, -1500), aperture=aperture, focus_dist=1500)


# =============================================================================================== 0. COLD OPEN
IRIS_C = (540.0, 860.0)


def _iris_r(t):
    """Iris radius: spark on the heartbeat (t=0), opens to 360 px, a pulse on the 'dub' (0.30), then blows wide
    into the first montage cut at 0.5."""
    r = 360.0 * K.ramp(t, 0.02, 0.32, 'out_expo')
    r += 26.0 * K.impulse(t, 0.0, decay=10.0) + 34.0 * K.impulse(t, 0.30, decay=9.0)
    r += 1150.0 * K.ramp(t, 0.36, 0.5, 'in_cubic')
    return r


def s_cold(t):
    F, S3, T, ui = _lazy()
    A = _common()
    cam = K.Cam(pos=(0, 0, -1500 + 140 * t), aperture=40, focus_dist=1500)
    cv = K.background('neon', t, cam, intensity=0.25 + 0.5 * K.ramp(t, 0.0, 0.4), dots=0.4, rim=0.0,
                      center=(0.5, 0.42))
    r = _iris_r(t)
    cx, cy = IRIS_C
    if r > 2:
        foot = F.Clip('c01').get(0.25 + t * 0.9, K.W, K.H, center=(0.48, 0.40), zoom=1.32 - 0.12 * t,
                                 look='neon')
        yy, xx = np.ogrid[0:K.H, 0:K.W]
        d = np.sqrt((xx.astype(np.float32) - cx) ** 2 + (yy.astype(np.float32) - cy) ** 2)
        m = np.clip((r - d) / 3.0 + 0.5, 0, 1)
        # soft inner falloff so the iris edge glows into the picture
        foot[..., :3] *= (0.55 + 0.45 * np.clip((r - d) / max(r * 0.35, 1), 0, 1))[..., None]
        cv[..., :3] = cv[..., :3] * (1 - m[..., None]) + foot[..., :3] * m[..., None]
        beat = 0.6 * K.impulse(t, 0.0, decay=8.0) + 0.6 * K.impulse(t, 0.30, decay=8.0)
        K.draw(cv, A['ring'], cx, cy, scale=r / 300.0, mode='add', opacity=0.8 + 0.6 * beat)
    A['dust'].draw(cv, cam, t)
    A['fg_bokeh'].draw(cv, cam, t, opacity=0.6)
    return cv


# =============================================================================================== 1. HOOK MONTAGE
# (clip, source in-point s, crop centre, zoom). 8 flashes of 0.25 s (eighth notes) from 0.5 to 2.5.
HOOK = [('c12', 4.15, (0.635, 0.535), 1.08),    # mum + boy laughing (faces lifted above the word band)
        ('c10', 20.90, (0.62, 0.545), 1.10),    # dad + daughter smiling to camera
        ('c08', 1.80, (0.50, 0.50), 1.05),      # piggyback, both smiling to camera
        ('c14', 9.50, (0.42, 0.46), 1.08),      # baby lifted + kiss
        ('c00', 1.15, (0.40, 0.525), 1.06),     # tent, girl to camera
        ('c16', 2.35, (0.60, 0.42), 1.06),      # dog kennel, leaves in front
        ('c02', 4.25, (0.38, 0.46), 1.16),      # toddler stacking blocks
        ('c11', 4.45, (0.56, 0.48), 1.08)]      # mum + child + teddy
HOOK_DT = 0.25
# cut INTO flash k (k = 0..7) and the smash out at 2.5: 'flash' on the beats (word slams), whips / zoom on the &s
CUTS = ['flash', 'whip', 'flash', 'whip', 'flash', 'zoom', 'flash', 'whip', 'smash']
WHIP_DIR = {1: 1, 3: -1, 7: 1}
# sized so that inside y 1050..1700 every right edge stays <= ~910 (brief 3.2: like/share column at x > 930)
WORDS = [('A SAFE\nHOME.', 190), ('EVERYDAY\nCARE.', 142), ('A PLACE', 180), ('TO\nBELONG.', 165)]
WORD_Y = [1300, 1300, 1330, 1300]
WORD_X = [530.0, 515.0, 515.0, 520.0]
WHIP_HALF = 0.06                      # a whip spans tc - 0.06 .. tc + 0.06


def _cut_t(k):
    return T_HOOK + HOOK_DT * k


@functools.lru_cache(maxsize=1)
def _hook_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['words'] = [T.Glyphs(w, 'extrude3d', px=px, line_height=1.0, fill=((0.0, '#FFFFFF'), (0.6, '#FFF3F9'),
                                                                        (1.0, '#F4D6E8')),
                           depth=0.13, angle=-72, persp=0.05, side=(('#A3136A', 1.0), ('#2A0624', 1.0)),
                           rim_color=('HOT_PINK', 1.6), glow=0.85, glow_color=('MAGENTA', 2.6),
                           glow_radii=(0.06, 0.18, 0.45, 0.9), glow_weights=(0.9, 0.7, 0.55, 0.35),
                           scrim=0.84, scrim_size=0.55)
                  for w, px in WORDS]
    # soft dark backing per word (a blurred rounded slab, NIGHT_0): words stay crisp over bright footage
    d['scrims'] = [_scrim_sprite(g.w + 150, g.h + 130, 0.78) for g in d['words']]
    return d


def _scrim_sprite(w, h, amount, blur=46):
    pad = int(blur * 2.2)
    a = K.rrect_alpha(int(w), int(h), min(w, h) * 0.45, pad)
    a = K.gblur(a, blur, border='constant')
    a = np.clip(a * 1.15, 0, 1) ** 0.9 * amount
    col = K.C['NIGHT_0'] * 0.6 + K.C['PLUM'] * 0.08
    return np.dstack([a[..., None] * col, a]).astype(np.float32)


def _hook_shake(t):
    """Camera shake from the word slams (on the beats)."""
    dx = dy = rot = 0.0
    for i in range(4):
        tb = T_HOOK + i * BEAT
        a = K.impulse(t, tb, decay=9.0)
        if a > 1e-3:
            sx, sy, sr = K.shake(t, 22.0 * a, 16.0, seed=3 + i)
            dx, dy, rot = dx + sx, dy + sy, rot + sr * 0.5
    return dx, dy, rot


def _flash_sprite(k, t, extra_zoom=1.0):
    F = _lazy()[0]
    cid, src, cen, z = HOOK[k]
    u = t - _cut_t(k)
    zoom = z * (1.0 + 0.075 * K.ramp(u, -0.06, 0.31, 'out_cubic')) * extra_zoom
    if CUTS[k] == 'flash':        # slam punch: lands from 1.12x
        zoom *= 1.0 + 0.12 * (1.0 - K.ramp(u, 0.0, 0.16, 'out_expo'))
    if CUTS[k] == 'zoom':         # zoom-through arrival: from 1.35x
        zoom *= 1.0 + 0.35 * (1.0 - K.ramp(u, 0.0, 0.14, 'out_expo'))
    if CUTS[k + 1] in ('zoom', 'smash'):     # push into the zoom cut / the smash to the void
        zoom *= 1.0 + 0.30 * K.ramp(u, 0.17, 0.25, 'in_expo')
    sx, sy, _ = _hook_shake(t)
    return F.Clip(cid).get(src + max(u, -0.1) * 1.15, K.W, K.H, center=cen, zoom=zoom, look='neon',
                           pan=(sx, sy))


def s_hook(t):
    A = _common()
    H = _hook_assets()
    k = int(np.clip((t - T_HOOK) // HOOK_DT, 0, 7))
    tc_in, tc_out = _cut_t(k), _cut_t(k + 1)
    cv = None
    # whip transition window (both frames side by side, the pair slides past the lens)
    for kk, tc in ((k, tc_in), (k + 1, tc_out)):
        if kk in WHIP_DIR and abs(t - tc) <= WHIP_HALF:
            d = WHIP_DIR[kk]
            p = K.ramp(t, tc - WHIP_HALF, tc + WHIP_HALF, 'inout_quart')
            cv = K.new_canvas(K.C['NIGHT_0'])
            out_s = _flash_sprite(kk - 1, t)
            in_s = _flash_sprite(kk, t)
            K.draw(cv, out_s, K.CX - d * K.W * p, K.CY)
            K.draw(cv, in_s, K.CX + d * K.W * (1 - p), K.CY)
            # speed of the slide -> directional smear (on top of the shutter sub-samples)
            eps = 1e-3
            v = abs(K.ramp(t + eps, tc - WHIP_HALF, tc + WHIP_HALF, 'inout_quart') -
                    K.ramp(t - eps, tc - WHIP_HALF, tc + WHIP_HALF, 'inout_quart')) / (2 * eps) * K.W
            K.whip_blur(cv, min(360.0, v / 60.0), angle=0.0)
            break
    if cv is None:
        cv = _flash_sprite(k, t).copy()
        if CUTS[k] == 'zoom' and t - tc_in < 0.12:
            K.zoom_blur(cv, 0.16 * (1 - K.ramp(t, tc_in, tc_in + 0.12, 'out_cubic')))
        if CUTS[k + 1] in ('zoom', 'smash') and tc_out - t < 0.08:
            K.zoom_blur(cv, 0.16 * K.ramp(t, tc_out - 0.08, tc_out, 'in_cubic'))
    # foreground depth layer: near defocused bokeh
    cam = _static_cam(t)
    A['fg_bokeh'].draw(cv, cam, t, opacity=0.55)
    # slammed word of this beat
    i = int(np.clip((t - T_HOOK) // BEAT, 0, 3))
    tb = T_HOOK + i * BEAT
    sx, sy, sr = _hook_shake(t)
    g = H['words'][i]
    sc = min(1.0, 930.0 / g.w)
    # dark scrim behind the word: lands with the slam (a touch larger while the word overshoots)
    sp = K.spring(max(t - tb, 0.0) / 0.42 * 0.45, 3.2, 0.45) if t >= tb else 0.0      # Glyphs.slam's own spring
    K.draw(cv, H['scrims'][i], WORD_X[i] + sx * 0.6, WORD_Y[i] + sy * 0.6, scale=sc * (1.2 - 0.2 * sp),
           opacity=K.ramp(t, tb, tb + 0.05))
    g.slam(cv, t, WORD_X[i] + sx * 0.6, WORD_Y[i] + sy * 0.6, t0=tb, s0=1.4, dur=0.42, scale=sc, rot=sr,
           smear=False)
    # light-leak sweep across the whip cuts at 1.25 and 2.25
    for tc in (_cut_t(3), _cut_t(7)):
        if abs(t - tc) < 0.16:
            K.light_leak(cv, t, strength=0.9, sweep=K.ramp(t, tc - 0.16, tc + 0.16, 'inout_sine'), angle=20,
                         colors=[K.C['HOT_PINK'], K.C['ORANGE'], K.C['AMBER']])
    return cv


def post_hook(cv, t):
    fl = 0.0
    for kk in range(0, 9):
        if CUTS[kk] in ('flash', 'smash'):
            fl = max(fl, 0.95 * _blip(t, _cut_t(kk), rise=0.02, decay=16.0))
    whip = 0.0
    for kk in WHIP_DIR:
        whip = max(whip, 1.0 - K.clamp(abs(t - _cut_t(kk)) / WHIP_HALF))
    zoom = max(0.0, 1.0 - abs(t - _cut_t(5)) / 0.1)
    slam = max(K.impulse(t, T_HOOK + i * BEAT, decay=10.0) for i in range(4))
    return _post(cv, t, hot=fl, kick=slam, footage=1.0, chroma=1.8 + 8.0 * whip + 6.0 * zoom + 4.0 * slam)


# =============================================================================================== 2. THE QUESTION
# scene-local u = t - T_Q. "?" flies in 0 -> 0.5 (lands on beat 6, 3.0 s); words on the eighth-note grid.
Q_TXT = dict(could=(0.75, -150.0), you=(1.0, 32.0), bea=(1.25, 210.0), fc=(1.5, 352.0))
Q_SWEEP = (1.55, 2.45)
Q_X = dict(could=-10.0, you=-10.0, bea=-10.0, fc=-28.0)     # world x: keeps the block clear of x > 930 (y >= 1050)
YOU_STYLE = dict(px=250, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, fill_gain=0.92, env=0.0,
                 ambient=0.74, spec=0.65, depth=0.24, angle=-70, persp=0.08, side=(('#9A1066', 1.0), ('#22041C', 1.0)),
                 side_key=0.5, side_ambient=0.35, side_rim=0.25, edge_rim=0.8, rim_color=('HOT_PINK', 1.4), glow=0.45,
                 glow_color=('MAGENTA', 1.7))
WHIP_DOWN = 0.25                      # the whip down into the checklist spans T_LIST - 0.2 .. T_LIST + 0.45


@functools.lru_cache(maxsize=1)
def _q_assets():
    F, S3, T, ui = _lazy()
    d = {}
    soft = dict(glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3))
    d['could'] = T.render('Could', 'flat', px=112, fill='IVORY', glow=0.55, glow_color=('MAGENTA', 2.2), **soft)
    d['you'] = T.render('YOU', 'extrude3d', **YOU_STYLE)
    d['bea'] = T.render('be a', 'flat', px=100, fill='IVORY', glow=0.5, glow_color=('MAGENTA', 2.0), **soft)
    d['fc'] = T.render('Foster Carer?', 'deep_glow', px=124, glow_color=('ORANGE', 2.5),
                       inner_glow_color=('AMBER', 1.25))
    d['q'] = S3.get('question', 'night', mode='spin', scale=0.6)        # <= ~600 px on screen
    d['card'] = ui.glass_card(600, 820, r=48, look='neon', rim=1.2, glow=1.0, rim_angle=-60)
    d['bokeh'] = K.glow(K.disc(60, K.C['HOT_PINK'] * 0.8), K.C['MAGENTA'], (20, 60), 0.6)
    d['bokeh2'] = K.glow(K.disc(48, K.C['ORANGE'] * 0.9), K.C['ORANGE'], (20, 60), 0.6)
    d['orb'] = K.radial(300, K.C['MAGENTA'] * 1.2, power=2.2)
    return d


def _q_cam(u, t):
    e = K.EASE['easy_ease'](K.clamp(u / 3.0))
    dist = K.lerp(1800.0, 1540.0, e)
    yaw = K.lerp(8.0, -4.0, e)
    slam = K.impulse(u, Q_TXT['you'][0], decay=8.0) + 0.8 * K.impulse(u, 0.0, decay=6.0)
    sx, sy, sr = K.shake(u, 12.0 * slam, 15.0, seed=11)
    # whip down out of the scene (camera tilts down fast: content rushes up)
    wd = K.ramp(t, T_LIST - WHIP_DOWN, T_LIST, 'in_cubic')
    return K.Cam.orbit((sx, -60.0 + sy, 0.0), dist, yaw=yaw, pitch=1.5 + K.wiggle(u, 0.3, 0.6, seed=2) - 26.0 * wd,
                       roll=sr * 0.4, aperture=34)


def s_question(t):
    _, _, T, ui = _lazy()
    A = _q_assets()
    C = _common()
    u = t - T_Q
    cam = _q_cam(u, t)
    land = _swell(u, 0.5, rise=0.08, decay=6.0)
    cv = K.background('neon', u + 3.0, cam, boost=0.55 * K.impulse(u, 0.0, decay=4.0) + 0.2 * land +
                      0.15 * K.beat_pulse(t, BPM, decay=5.0), center=(0.72, 0.24))
    sc = K.Scene(cam)
    # far plate: c01 inside a tilted neon glass card (bokeh DOF from depth)
    card = A['card']
    media = _lazy()[0].Clip('c01').get(4.0 + u * 0.8, card.w, card.h, zoom=1.08 + 0.02 * u, look='neon')
    media[..., :3] *= np.float32(0.72)
    face = ui.media_face(card, media, sweep=(0.15 + u * 0.32) % 1.0)
    cin = K.ramp(u, 0.2, 1.2, 'out_expo')
    cpos = (-830.0 - 300 * (1 - cin), -1500.0, 2700.0 + 1500 * (1 - cin))
    sc.custom(cpos, lambda c, cm: card.plane(c, cm, cpos, 820, rot=(4.0, -26.0, 6.0), face=face, shadow=0.6,
                                             opacity=0.9 * cin, dof_scale=2.2, blur=1.5))
    # magenta glow orb behind the "?" (volumetric light), light-ring portal
    sc.billboard(A['orb'], (160.0, -560.0, 900.0), 1700, mode='add', opacity=0.35 + 0.35 * land)
    ring_op = K.ramp(u, 0.35, 0.8, 'out_cubic')
    rs = 0.82 + 0.18 * K.ramp(u, 0.4, 1.1, 'out_expo') + 0.02 * math.sin(u * 2.1) + 0.05 * land
    sc.plane(C['ring'], (110.0, -545.0, 520.0), 1100 * rs, rot=(8.0, -18.0, 0.0), mode='add', opacity=0.85 * ring_op)
    # glossy "?" spinning in from depth, lands on beat 6, then sways
    p = K.ramp(u, 0.0, 0.5, 'out_expo')
    qz = K.lerp(5600.0, 120.0, p)
    qx = K.lerp(460.0, 110.0, K.ramp(u, 0.0, 0.5, 'out_cubic'))
    qy = K.lerp(-980.0, -560.0, K.ramp(u, 0.0, 0.5, 'out_quint')) + 10 * math.sin(u * 1.4)
    ang = -760.0 * (1.0 - p) + 16.0 * math.sin(u * 1.25) * K.ramp(u, 0.45, 1.3, 'inout_sine')
    qs = A['q'].at_yaw(ang)
    sc.billboard(qs, (qx, qy, qz), 640.0 * (1.0 + 0.06 * land), rot=-8.0 + 8.0 * p)
    # type on planes in the same 3D space (parallax under the orbit)
    for key in ('could', 'bea', 'fc'):
        t0, y = Q_TXT[key]
        pr = K.ramp(u, t0, t0 + 0.6, 'out_expo')
        if pr <= 0:
            continue
        op = K.ramp(u, t0, t0 + 0.2, 'out_cubic')
        ts = A[key]
        pos = (Q_X[key], y + 70.0 * (1 - pr), -40.0 + 180.0 * (1 - pr))
        sc.custom(pos, lambda c, cm, ts=ts, pos=pos, op=op, pr=pr: ts.draw_plane(
            c, cm, pos, rot=(0, 0, 0), scale=1.0, opacity=op, blur=7.0 * (1 - pr)))
    you_u = Q_TXT['you'][0]
    if u >= you_u:
        sp = K.spring(u - you_u, freq=2.4, damping=0.42)
        s = 1.35 + (1.0 - 1.35) * sp                     # overshoot stays clear of "Could" above
        op = K.ramp(u, you_u, you_u + 0.04)
        sweep = K.ramp(u, Q_SWEEP[0], Q_SWEEP[1], 'inout_sine')
        pos = (Q_X['you'], Q_TXT['you'][1], -60.0)
        ts = A['you']
        sc.custom(pos, lambda c, cm: ts.draw_plane(c, cm, pos, scale=s, opacity=op, sweep=sweep if 0 < sweep < 1
                                                   else None, sweep_kw=dict(width=0.12, strength=1.7)))
    # foreground: near defocused bokeh blobs + dust
    sc.billboard(A['bokeh'], (-520.0, 520.0, -900.0), 260, mode='add', opacity=0.55)
    sc.billboard(A['bokeh2'], (470.0, -820.0, -1000.0), 220, mode='add', opacity=0.45)
    sc.particles(C['dust'], u)
    sc.render(cv)
    wd = K.ramp(t, T_LIST - WHIP_DOWN, T_LIST, 'in_cubic')
    if wd > 0.02:
        K.whip_blur(cv, 300.0 * wd ** 1.5, angle=90.0)
    return cv


def post_question(cv, t):
    u = t - T_Q
    slam = K.impulse(u, Q_TXT['you'][0], decay=7.0)
    land = _swell(u, 0.5, rise=0.08, decay=6.0)
    fly = K.ramp(u, 0.0, 0.2) * (1 - K.ramp(u, 0.3, 0.5))
    wd = K.ramp(t, T_LIST - WHIP_DOWN, T_LIST, 'in_cubic')
    smash = _blip(t, T_Q, rise=0.02, decay=32.0)
    return _post(cv, t, hot=0.95 * smash, kick=0.8 * slam + 0.4 * land,
                 chroma=1.8 + 7 * fly + 5 * slam + 9 * wd + 6 * smash)


# =============================================================================================== 3. CHECKLIST
ROWS = ['A spare bedroom', 'Time & flexibility', 'Single or in a relationship', 'Rent or own your home',
        'No previous experience needed']
TICKS = [6.5, 7.25, 8.0, 8.75, 9.5]           # 0.75 s apart, on the eighth-note grid
RING_POP, TOAST_T = 10.0, 10.5                # 100 % pop on beat 20, toast on beat 21
WHIP_OUT = 0.22                               # whip pan out: T_DOCK - 0.22 .. T_DOCK (and in over 0.4 s)
WIN_W, WIN_H = 960, 1220            # slot 752 wide: the longest label keeps its full 38 px
WIN_C = (0.0, 40.0, 0.0)
WIN_ROT = (6.0, -10.0, 1.0)
ROW_DY = 120


@functools.lru_cache(maxsize=1)
def _list_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['win'] = ui.app_window(w=WIN_W, h=WIN_H, look='neon', header='Am I eligible to foster?',
                             icons=('home', 'users', 'chat', 'calendar', 'settings'), active=0)
    d['toast'] = ui.toast('You could be a great fit', None, look='neon', w=620)
    d['tile'] = S3.get('check_tile', 'night', scale=0.25)
    d['bokeh'] = K.glow(K.disc(54, K.C['HOT_PINK'] * 0.8), K.C['MAGENTA'], (20, 60), 0.6)
    d['bokeh2'] = K.glow(K.disc(44, K.C['ORANGE'] * 0.9), K.C['ORANGE'], (20, 60), 0.6)
    return d


def _row_card_xy(i):
    """Card px of row i's checkbox centre."""
    x, y, sw, sh = _list_assets()['win'].meta['slot']
    return x + 28 + 30, y + i * ROW_DY + 48


# camera: solved from "card point (cx, cy) at screen (sx, sy) with s screen px per card px" so the dolly keeps
# every label >= 1.1x and inside x 70..1010, and the pull-back keeps them >= 0.95x (UI body stays >= 36 px)
def _lcam_solve(cx, cy, sx, sy, sc):
    P = _list_assets()['win'].world(WIN_C, WIN_W, WIN_ROT, cx, cy)
    depth = 1500.0 / sc
    return np.array([P[0] - (sx - K.CX) * depth / 1500.0, P[1] - (sy - K.CY) * depth / 1500.0, P[2] - depth])


def _lcam_pos(t):
    g = K.ramp(t, 6.3, 9.7, 'inout_sine')                        # dolly progress along the rows
    dolly = _lcam_solve(284, 280 + 480 * g, 250, 790 + 260 * g, K.lerp(1.11, 1.15, g))
    if t < 6.3:
        a = K.ramp(t, T_LIST, 6.3, 'out_cubic')
        return _lcam_solve(284, 280, 262, 760, 1.08) * (1 - a) + dolly * a
    full = _lcam_solve(480, 640, K.lerp(588, 592, K.ramp(t, 10.75, T_DOCK)), K.lerp(880, 872, K.ramp(t, 10.75, T_DOCK)),
                       K.lerp(0.985, 0.975, K.ramp(t, 10.75, T_DOCK, 'out_sine')))
    a = K.ramp(t, 9.75, 10.75, 'easy_ease')
    return dolly * (1 - a) + full * a


def _list_cam(t):
    A = _list_assets()
    pos = _lcam_pos(t)
    arrive = 1.0 - K.ramp(t, T_LIST, T_LIST + 0.45, 'out_expo')     # whip-down arrival (from above)
    wo = K.ramp(t, T_DOCK - WHIP_OUT, T_DOCK, 'in_cubic')           # whip pan out to the right
    yaw = K.lerp(-1.5, 1.5, K.ramp(t, T_LIST, T_DOCK, 'inout_sine')) + 26.0 * wo
    pitch = 17.0 * arrive + K.wiggle(t, 0.25, 0.35, seed=4)
    # rack focus: follow the row being ticked, then the ring / toast
    i = int(np.clip(np.searchsorted(TICKS, t + 0.35), 0, 4))
    cam0 = K.Cam(pos=pos, yaw=yaw, pitch=pitch)
    win = A['win']
    rx, ry = _row_card_xy(i)
    if t > TICKS[4] + 0.3:
        ry = K.lerp(ry, 967.0, K.ramp(t, TICKS[4] + 0.3, RING_POP, 'inout_cubic'))
    fd = cam0.depth(win.world(WIN_C, WIN_W, WIN_ROT, WIN_W * 0.5, ry))
    return K.Cam(pos=pos, yaw=yaw, pitch=pitch, roll=K.lerp(-0.6, 0.4, K.ramp(t, T_LIST, T_DOCK)), aperture=40,
                 focus_dist=float(fd))


def _ring_p(t):
    return sum(0.2 * K.ramp(t, tk + 0.05, tk + 0.45, 'out_cubic') for tk in TICKS)


def _list_face(t):
    _, _, _, ui = _lazy()
    A = _list_assets()
    win = A['win']
    x, y, sw, sh = win.meta['slot']
    f = win.face_at(sweep=(0.1 + (t - T_LIST) * 0.28) % 1.0)
    for i, lab in enumerate(ROWS):
        tk = TICKS[i]
        hl = K.ramp(t, tk - 0.45, tk - 0.2, 'out_cubic') * (1 - K.ramp(t, tk + 0.25, tk + 0.55, 'inout_cubic'))
        r = ui.check_row(lab, None, w=sw, t=(t - tk) if t >= tk else None, look='neon', hl=round(hl * 8) / 8)
        win.put(f, r, x - ui.ROW_PAD, y + i * ROW_DY - ui.ROW_PAD)
    p = _ring_p(t)
    n = sum(1 for tk in TICKS if t >= tk + 0.2)          # label snaps per tick (a counting label ghosts under blur)
    ring = ui.progress_ring(round(p * 40) / 40, 236, 22, 'neon', label='%d%%' % (20 * n))
    pop = K.spring(t - RING_POP, freq=3.0, damping=0.4) if t >= RING_POP else 0.0
    rs = 1.0 + 0.10 * math.sin(math.pi * min(1.0, max(0.0, t - RING_POP) / 0.35)) if t >= RING_POP else 1.0
    win.put(f, ring, x + sw / 2, y + 5 * ROW_DY + 135, anchor=(0.5, 0.5), scale=rs)
    if t >= RING_POP:
        g = K.impulse(t, RING_POP, decay=3.0)
        win.put(f, _ring_glow(), x + sw / 2, y + 5 * ROW_DY + 135,
                anchor=(0.5, 0.5), mode='add', opacity=0.5 * g + 0.15 * pop)
    return f


@functools.lru_cache(maxsize=1)
def _ring_glow():
    return K.glow(K.ring(118, 10, K.C['HOT_PINK'] * 1.5), K.C['MAGENTA'], (10, 30, 70), 1.2)


def s_list(t):
    _, _, _, ui = _lazy()
    A = _list_assets()
    C = _common()
    cam = _list_cam(t)
    cv = K.background('neon', t, cam, boost=0.1 * K.beat_pulse(t, BPM, decay=5.0), center=(0.75, 0.3), rim=0.6)
    win = A['win']
    face = _list_face(t)
    sc = K.Scene(cam)
    sc.custom(WIN_C, lambda c, cm: win.plane(c, cm, WIN_C, WIN_W, rot=WIN_ROT, face=face))
    # 3D green check tiles pop out of the glass on each tick (spring scale + yaw settle), lifted toward the viewer
    tile = A['tile']
    for i, tk in enumerate(TICKS):
        if t < tk:
            continue
        sp = K.spring(t - tk, freq=2.6, damping=0.38)
        yaw = -38.0 * (1.0 - K.ramp(t, tk, tk + 0.5, 'out_back'))
        spr = tile.at_yaw(yaw)
        cx, cy = _row_card_xy(i)
        P = win.world(WIN_C, WIN_W, WIN_ROT, cx, cy, z=-34.0)
        k = 78.0 / (tile.bbox[2] - tile.bbox[0])           # 3D tile ~78 card px wide
        sc.custom(P, lambda c, cm, spr=spr, cx=cx, cy=cy, sp=sp, k=k: win.child(
            c, cm, WIN_C, WIN_W, WIN_ROT, spr, cx, cy, z=-34.0, scale=k * sp))
    # toast floats in front of the window
    if t >= TOAST_T:
        q = K.ramp(t, TOAST_T, TOAST_T + 0.5, 'out_back')
        tp = win.world(WIN_C, WIN_W, WIN_ROT, WIN_W / 2 + 40, 1150 + 90 * (1 - q), z=-150.0)
        tst = A['toast']
        sc.custom(tp, lambda c, cm: tst.plane(c, cm, tp, 620, rot=WIN_ROT, opacity=0.97 * K.ramp(t, TOAST_T,
                                                                                               TOAST_T + 0.2)))
    sc.billboard(A['bokeh'], (-560.0, 700.0, -950.0), 260, mode='add', opacity=0.5)
    sc.billboard(A['bokeh2'], (520.0, -760.0, -1050.0), 210, mode='add', opacity=0.4)
    sc.particles(C['dust'], t)
    sc.render(cv)
    # cursor (screen space, on top): glides between checkboxes, clicks on the ticks
    xy, press, click, op = _cursor_state(t, cam)
    if op > 0:
        ui.draw_cursor(cv, xy[0], xy[1], 'arrow', 78, press=press, click=click, look='neon', opacity=op)
    arrive = 1.0 - K.ramp(t, T_LIST, T_LIST + 0.45, 'out_expo')
    wo = K.ramp(t, T_DOCK - WHIP_OUT, T_DOCK, 'in_cubic')
    if arrive > 0.05:
        K.whip_blur(cv, 300.0 * arrive ** 1.5, angle=90.0)
    if wo > 0.02:
        K.whip_blur(cv, 320.0 * wo, angle=0.0)
    return cv


def _cursor_state(t, cam):
    """Arrow cursor: enters from the lower right, glides (inout) to each checkbox 0.12 s before its tick,
    presses on the tick, then drifts off toward the ring and fades."""
    A = _list_assets()
    win = A['win']

    def box(i):
        cx, cy = _row_card_xy(i)
        p = win.screen(cam, WIN_C, WIN_W, WIN_ROT, cx + 6, cy + 8, z=-60.0)
        return np.array(p, np.float64)
    if t < 5.95 or t > 10.6:
        return (0, 0), 0.0, None, 0.0
    if t < TICKS[0] - 0.12:
        a = K.ramp(t, 5.95, TICKS[0] - 0.12, 'out_cubic')
        xy = (1 - a) * np.array([1180.0, 1700.0]) + a * box(0)
    elif t >= TICKS[4] + 0.2:
        a = K.ramp(t, TICKS[4] + 0.2, 10.6, 'in_cubic')
        xy = (1 - a) * box(4) + a * np.array([1200.0, 1500.0])
    else:
        i = int(np.clip(np.searchsorted(TICKS, t + 0.12) - 1, 0, 4))
        if i < 4 and t > TICKS[i] + 0.2:
            a = K.ramp(t, TICKS[i] + 0.2, TICKS[i + 1] - 0.12, 'inout_cubic')
            xy = (1 - a) * box(i) + a * box(i + 1)
        else:
            xy = box(i)
    j = int(np.argmin([abs(t - tk) for tk in TICKS]))
    tk = TICKS[j]
    press = K.impulse(t, tk - 0.03, decay=9.0) if t >= tk - 0.03 else 0.0
    click = (t - tk) if t >= tk else None
    op = K.ramp(t, 5.95, 6.1) * (1 - K.ramp(t, 10.35, 10.6))
    return (float(xy[0]), float(xy[1])), press, click, op


def post_list(cv, t):
    arrive = 1.0 - K.ramp(t, T_LIST, T_LIST + 0.45, 'out_expo')
    wo = K.ramp(t, T_DOCK - WHIP_OUT, T_DOCK, 'in_cubic')
    return _post(cv, t, chroma=1.8 + 8 * arrive + 9 * wo)


# =============================================================================================== 4. SUPPORT DOCK
# footage per tile: (clip, source in-point, crop centre, zoom, speed). c03: both children's faces stay inside the slot
# over source 2.35..3.35 s, hence the slow 0.4x play
TILES = [('Full Training', 'Preparation & ongoing learning', 'MAGENTA', 'grad_cap', ('c03', 2.45, (0.61, 0.45), 1.0, 0.4)),
         ('Ongoing Support', 'Your supervising social worker', 'HOT_PINK', 'chat_bubble',
          ('c04', 1.0, (0.5, 0.4), 1.1, 0.9)),
         ('Weekly Allowance', 'From £447.60 a week per child', 'ORANGE', 'coin_gbp', ('c10', 17.4, (0.6, 0.42), 1.1, 0.9))]
TILE_W, TILE_H, TILE_GAP = 264, 560, 18
FOCUS_GROW, FOCUS_Z = 0.06, -30.0
DOCK_X = 492.0                                # row centre: every tile text stays at x <= ~915 (like/share column)
FOCUS_T = [12.5, 14.5, 16.5]                  # focus moves on beats 25, 29, 33 (2 s per tile)
DOCK_Y = 1030.0                               # tile centre (screen y at z = 0)
HEAD_T = 11.5
ZOOM_OUT = 0.28                               # push into the last tile's footage: T_PAY - 0.28 .. T_PAY


def _dock_tile(title, sub, accent, w=TILE_W, h=TILE_H, title_size=38, sub_size=29, max_sub=3):
    """ui.dock_tile variant (built here, the toolkit's is left untouched): 3 subtitle lines instead of 2 so the
    subtitles keep >= 30 px inside a 292 px tile (three tiles + the focus enlargement fit the 940 px safe width).
    meta['icon'] = None: the glossy 3D icon is drawn as its own billboard (it lifts out of the tile on focus)."""
    _, _, _, ui = _lazy()
    L = ui.LOOKS['neon']
    base = ui.glass_card(w, h, 44, 'neon', rim=0.7, glow=0.8)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    ac = ui.col(accent)
    tl = ui.wrap(title, title_size, 'ui', w - 40)[:2]
    sl = ui.wrap(sub, sub_size, 'body', w - 40)[:max_sub]
    text_h = 24 + 2 * (title_size + 8) + 8 + max_sub * (sub_size + 10) + 20     # same slot on every tile
    sx, sy, sw = 18, 18, w - 36
    sh = int(h - sy - text_h)
    sr = 44 - 16
    S.rrect(p + sx, p + sy, sw, sh, sr, L.tint_bot, 0.55)
    blob = K.radial(int(sw * 1.2), ac, power=1.8)
    bm, X0, Y0 = S.rrect_mask(p + sx, p + sy, sw, sh, sr)
    tmp = np.zeros_like(f)
    K.draw(tmp, blob, p + sx + sw / 2, p + sy + sh * 0.62, mode='add')
    f[Y0:Y0 + bm.shape[0], X0:X0 + bm.shape[1], :3] += tmp[Y0:Y0 + bm.shape[0], X0:X0 + bm.shape[1], :3] * \
        bm[..., None] * 0.9
    S.stroke_rrect(p + sx, p + sy, sw, sh, sr, 1.3, K.C['WHITE'], 0.22,
                   weight=lambda xs, ys: np.clip(1.2 - (ys - p - sy) / sh, 0.2, 1))
    y = sy + sh + 24 + title_size * 0.78
    for ln in tl:
        ui.put_text(f, p + 20, p + y, ln, title_size, 'ui', L.text, 'ls')
        y += title_size + 8
    y += 8 + sub_size * 0.2
    for ln in sl:
        ui.put_text(f, p + 20, p + y, ln, sub_size, 'body', L.text2, 'ls')
        y += sub_size + 10
    return ui.derive_panel(base, f, {'slot': (sx, sy, sw, sh, sr), 'accent': tuple(ac), 'icon': None})


@functools.lru_cache(maxsize=1)
def _dock_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['tiles'] = [_dock_tile(ti, su, ac) for (ti, su, ac, _, _) in TILES]
    d['icons'] = [S3.get(ic, 'night', scale=0.5) for (_, _, _, ic, _) in TILES]
    d['head'] = T.render('Support is part\nof the role.', 'flat', px=100, fill='IVORY', line_height=1.06, glow=0.6,
                         glow_color=('MAGENTA', 2.4), glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.85, 0.55, 0.35))
    d['blobs'] = [K.radial(240, ui.col(ac), power=2.0) for (_, _, ac, _, _) in TILES]
    d['bokeh'] = K.glow(K.disc(56, K.C['HOT_PINK'] * 0.8), K.C['MAGENTA'], (20, 60), 0.6)
    d['bokeh2'] = K.glow(K.disc(46, K.C['ORANGE'] * 0.9), K.C['ORANGE'], (20, 60), 0.6)
    return d


def _focus(t):
    """Fractional focus index (0..2); -1 before the dock lights up."""
    f = -1.0 + K.ramp(t, FOCUS_T[0] - 0.25, FOCUS_T[0] + 0.1, 'out_cubic')
    f += K.ramp(t, FOCUS_T[1] - 0.15, FOCUS_T[1] + 0.25, 'inout_cubic')
    f += K.ramp(t, FOCUS_T[2] - 0.15, FOCUS_T[2] + 0.25, 'inout_cubic')
    return f


def _pop(t, tf):
    """Springy overshoot when a tile takes focus (a quick decaying wobble on top of the focus growth)."""
    if t < tf:
        return 0.0
    dt = t - tf
    return 0.035 * math.exp(-dt * 5.0) * math.sin(dt * 15.0)


def _tile_layout(t):
    """[(x centre, scale, weight)] in screen px at z = 0: tiles laid out left->right, the focused one 12 % larger,
    the row recentred so it stays inside the safe width."""
    f = _focus(t)
    ws = [max(0.0, 1.0 - abs(i - f)) for i in range(3)]
    sc = [1.0 + FOCUS_GROW * w + _pop(t, FOCUS_T[i]) for i, w in enumerate(ws)]
    widths = [TILE_W * s for s in sc]
    total = sum(widths) + 2 * TILE_GAP
    x = DOCK_X - total / 2
    out = []
    for i in range(3):
        out.append((x + widths[i] / 2, sc[i], ws[i]))
        x += widths[i] + TILE_GAP
    return out


def _dock_cam(t):
    """Orbit around the tile row (the tiles stay framed inside the safe width while the glow plate behind and the
    bokeh in front slide past: a truck with parallax), whip-pan arrival, then a push into tile 3's footage."""
    arrive = 1.0 - K.ramp(t, T_DOCK, T_DOCK + 0.45, 'out_expo')
    yaw = K.lerp(-3.0, 1.5, K.ramp(t, T_DOCK + 0.3, T_PAY - 0.3, 'inout_sine')) + 0.4 * math.sin((t - T_DOCK) * 0.7)
    dist = 1500.0 - 40.0 * K.ramp(t, T_DOCK, T_PAY, 'inout_sine')
    cam = K.Cam.orbit((0.0, 0.0, 0.0), dist, yaw=yaw, pitch=K.wiggle(t, 0.22, 0.3, seed=12), aperture=30)
    cam = K.Cam(pos=cam.pos, yaw=cam.yaw - 17.0 * arrive, pitch=cam.pitch, roll=0.0, aperture=30,
                focus_dist=dist + 60.0)
    zo = K.ramp(t, T_PAY - ZOOM_OUT, T_PAY, 'in_expo')
    if zo > 0:
        lay = _tile_layout(t)
        tgt = np.array([lay[2][0] - K.CX, DOCK_Y - K.CY - 110.0, -170.0])
        pos = cam.pos * (1 - zo) + tgt * zo
        cam = K.Cam(pos=pos, yaw=cam.yaw * (1 - zo), pitch=cam.pitch * (1 - zo), aperture=30,
                    focus_dist=max(200.0, dist * (1 - zo) + 170.0 * zo))
    return cam


def s_dock(t):
    F, S3, T, ui = _lazy()
    A = _dock_assets()
    C = _common()
    cam = _dock_cam(t)
    f = _focus(t)
    cv = K.background('neon', t, cam, boost=0.15 * K.beat_pulse(t, BPM, decay=5.0),
                      center=(0.3 + 0.2 * max(f, 0) / 2, 0.62), rim=0.5)
    sc = K.Scene(cam)
    lay = _tile_layout(t)
    # coloured glow blobs behind the tiles (parallax plate)
    for i, (x, s, w) in enumerate(lay):
        sc.billboard(A['blobs'][i], (x - K.CX, DOCK_Y - K.CY + 40, 700.0), 900 * (1.0 + 0.35 * w), mode='add',
                     opacity=0.22 + 0.4 * w)
    # headline
    hp = K.ramp(t, HEAD_T, HEAD_T + 0.7, 'out_expo')
    if hp > 0:
        hpos = (DOCK_X - K.CX + 20.0, 470.0 - K.CY + 60 * (1 - hp), 60.0 + 200 * (1 - hp))
        sweep = K.ramp(t, 12.3, 13.2, 'inout_sine')
        hd = A['head']
        sc.custom(hpos, lambda c, cm: hd.draw_plane(c, cm, hpos, opacity=K.ramp(t, HEAD_T, HEAD_T + 0.25),
                                                    blur=6.0 * (1 - hp), sweep=sweep if 0 < sweep < 1 else None,
                                                    sweep_kw=dict(width=0.1, strength=1.3)))
    # tiles: slide in from the right as a carousel (staggered), then the focus walks left -> right
    for i, (x, s, w) in enumerate(lay):
        tin = K.ramp(t, T_DOCK - 0.05 + 0.125 * i, T_DOCK + 0.75 + 0.125 * i, 'out_expo')
        if tin <= 0:
            continue
        tile = A['tiles'][i]
        tf = FOCUS_T[i]
        media = None
        mix = K.ramp(t, tf - 0.1, tf + 0.3, 'out_cubic') * (1 - K.ramp(t, tf + 1.85, tf + 2.2, 'inout_cubic')
                                                             if i < 2 else 1.0)
        if mix > 0.01:
            cid, src, cen, mz, spd = TILES[i][4]
            sx_, sy_, sw_, sh_, sr_ = tile.meta['slot']
            media = F.Clip(cid).get(src + (t - tf) * spd, sw_, sh_, center=cen, zoom=mz + 0.03 * max(t - tf, 0.0),
                                    look='neon')
        light = K.ramp(t, tf + 0.15, tf + 0.95, 'inout_sine')
        face = ui.dock_face(tile, focus=w, sweep=((t - T_DOCK) * 0.3 + i * 0.33) % 1.0)
        if media is not None:
            ui.put_media(tile, face, media, *tile.meta['slot'], opacity=mix)
        if 0 < light < 1:
            tile._add_light(face, light, None, -28.0, 0.07)      # diagonal glass glint (light sweep)
        px = x - K.CX + 900.0 * (1 - tin)
        pz = FOCUS_Z * w + 500.0 * (1 - tin)
        P = (px, DOCK_Y - K.CY + 7.0 * math.sin((t - T_DOCK) * 1.3 + i * 2.1) * (1 - 0.6 * w), pz)
        rot = (1.5 * math.sin((t - T_DOCK) * 0.9 + i), -38.0 * (1 - tin) - 4.0 * (i - 1) * (1 - w), 0.0)
        sc.custom(P, lambda c, cm, tile=tile, P=P, rot=rot, face=face, s=s, tin=tin: tile.plane(
            c, cm, P, TILE_W * s, rot=rot, face=face, opacity=K.ramp(tin, 0.0, 0.3)))
        # glossy 3D icon: floats in the slot, lifts out to the tile's top-left corner when the tile is focused
        ic = A['icons'][i]
        spr = ic.float_yaw(t + i * 0.7, amp=16, period=4.0)
        sx_, sy_, sw_, sh_, sr_ = tile.meta['slot']
        k = TILE_W * s / tile.w
        slot_c = (px + (sx_ + sw_ / 2 - tile.w / 2) * k, P[1] + (sy_ + sh_ / 2 - tile.h / 2) * k, pz - 20)
        corner = (px + (-tile.w / 2 + 50) * k, P[1] + (-tile.h / 2 - 50) * k, pz - 110)     # above the top edge
        lift = mix
        ipos = tuple(slot_c[j] * (1 - lift) + corner[j] * lift for j in range(3))
        iw = K.lerp(sw_ * 0.78, 122.0, lift) * k * (ic.size[0] / (ic.bbox[2] - ic.bbox[0]))
        sc.billboard(spr, ipos, iw, opacity=K.ramp(tin, 0.2, 0.6))
    # hand cursor hovers the focused tile's footage (hover drives focus)
    sc.billboard(A['bokeh'], (-520.0, 640.0, -950.0), 260, mode='add', opacity=0.5)
    sc.billboard(A['bokeh2'], (500.0, -700.0, -1050.0), 210, mode='add', opacity=0.4)
    sc.particles(C['dust'], t)
    sc.render(cv)
    xy, op = _dock_cursor(t, cam, lay)
    if op > 0:
        ui.draw_cursor(cv, xy[0], xy[1], 'hand', 78, look='neon', opacity=op,
                       press=max(K.impulse(t, tf - 0.05, decay=9.0) if t >= tf - 0.05 else 0.0 for tf in FOCUS_T))
    arrive = 1.0 - K.ramp(t, T_DOCK, T_DOCK + 0.45, 'out_expo')
    if arrive > 0.05:
        K.whip_blur(cv, 320.0 * arrive ** 1.5, angle=0.0)
    zo = K.ramp(t, T_PAY - ZOOM_OUT, T_PAY, 'in_expo')
    if zo > 0.02:
        K.zoom_blur(cv, 0.22 * zo, center=(K.CX, K.CY))
    return cv


def _dock_cursor(t, cam, lay):
    """Hand cursor glides (inout) to the lower-right of each tile's media slot just before its focus beat."""
    if t < FOCUS_T[0] - 0.6 or t > FOCUS_T[2] + 1.3:
        return (0.0, 0.0), 0.0
    tiles = _dock_assets()['tiles']

    def target(i):
        x, s, w = lay[i]
        sx_, sy_, sw_, sh_, sr_ = tiles[i].meta['slot']
        k = TILE_W * s / tiles[i].w
        P = np.array([[x - K.CX + (sx_ + sw_ * 0.72 - tiles[i].w / 2) * k,
                       DOCK_Y - K.CY + (sy_ + sh_ * 0.78 - tiles[i].h / 2) * k, FOCUS_Z * w - 60]])
        xy, _ = cam.project(P)
        return xy[0]
    if t < FOCUS_T[0] - 0.12:
        a = K.ramp(t, FOCUS_T[0] - 0.6, FOCUS_T[0] - 0.12, 'out_cubic')
        xy = (1 - a) * np.array([1150.0, 1500.0]) + a * target(0)
    elif t < FOCUS_T[1] - 0.6:
        xy = target(0)
    elif t < FOCUS_T[1] - 0.12:
        a = K.ramp(t, FOCUS_T[1] - 0.6, FOCUS_T[1] - 0.12, 'inout_cubic')
        xy = (1 - a) * target(0) + a * target(1)
    elif t < FOCUS_T[2] - 0.6:
        xy = target(1)
    elif t < FOCUS_T[2] - 0.12:
        a = K.ramp(t, FOCUS_T[2] - 0.6, FOCUS_T[2] - 0.12, 'inout_cubic')
        xy = (1 - a) * target(1) + a * target(2)
    else:
        a = K.ramp(t, FOCUS_T[2] + 0.8, FOCUS_T[2] + 1.3, 'in_cubic')
        xy = (1 - a) * target(2) + a * np.array([1180.0, 1450.0])
    op = K.ramp(t, FOCUS_T[0] - 0.6, FOCUS_T[0] - 0.45) * (1 - K.ramp(t, FOCUS_T[2] + 1.1, FOCUS_T[2] + 1.3))
    return (float(xy[0]), float(xy[1])), op


def post_dock(cv, t):
    arrive = 1.0 - K.ramp(t, T_DOCK, T_DOCK + 0.45, 'out_expo')
    zo = K.ramp(t, T_PAY - ZOOM_OUT, T_PAY, 'in_expo')
    return _post(cv, t, hot=0.9 * zo ** 3, chroma=1.8 + 8 * arrive + 8 * zo)


# =============================================================================================== 5. PAYOFF
PAY_L1, PAY_L2 = 18.75, 19.5                  # "Open your home." on the & of beat 37, "Change a child's life." beat 39
PAY_OUT = 0.3                                 # push + leak into the end card: T_END - 0.3 .. T_END


@functools.lru_cache(maxsize=1)
def _pay_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['ramp'] = F.SpeedRamp([(T_PAY, 1.0), (T_PAY + 0.2, 0.6, 'inout_sine'), (T_END, 0.6)], src0=3.6)
    d['l1'] = T.Glyphs('Open your home.', 'flat', px=96, fill='IVORY', glow=0.6, glow_color=('MAGENTA', 2.4),
                       glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.85, 0.55, 0.35))
    d['l2'] = T.Glyphs("Change a\nchild\u2019s life.", 'deep_glow', px=150, line_height=1.02, glow_color=('ORANGE', 2.5),
                       inner_glow_color=('AMBER', 1.25))
    # bottom gradient scrim (NIGHT_0, 0 at y 700 -> 0.9 from y 1400 down), plum-tinted
    y = np.arange(K.H, dtype=np.float32)
    a = np.clip((y - 700.0) / 700.0, 0, 1) ** 1.1 * 0.9
    d['scrim_a'] = a.astype(np.float32)[:, None, None]                  # (H, 1, 1) alpha column
    d['scrim_c'] = (K.C['NIGHT_0'] * 0.7 + K.C['PLUM'] * 0.06).astype(np.float32)
    # top falloff: the grey studio wall above the faces sinks toward plum (night palette, depth)
    top = np.clip(1.0 - y / 620.0, 0, 1) ** 1.6
    d['top_k'] = (1.0 - 0.45 * top).astype(np.float32)[:, None, None]
    d['top_tint'] = (K.C['PLUM'] * 0.05).astype(np.float32)
    d['warm'] = K.radial(350, K.C['ORANGE'] * 0.5, power=2.2)
    d['bokeh'] = K.Particles(22, seed=31, box=((-900, -1500, 260), (900, 1500, 1000)), vel=(0, -30, 0),
                             size=(5.0, 11.0), colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']], bright=0.5,
                             twinkle=0.3)
    return d


def s_payoff(t):
    F = _lazy()[0]
    A = _pay_assets()
    u = t - T_PAY
    arrive = 1.0 - K.ramp(t, T_PAY, T_PAY + 0.35, 'out_expo')          # lands from the zoom-through
    out = K.ramp(t, T_END - PAY_OUT, T_END, 'in_expo')
    zoom = 1.02 * (1.0 + 0.06 * K.EASE['easy_ease'](K.clamp(u / 2.5))) * (1.0 + 0.25 * arrive) * (1.0 + 0.18 * out)
    cv = F.Clip('c08').get(A['ramp'](t), K.W, K.H, center=(0.5, 0.4), zoom=zoom, look='neon',
                           pan=(4.0 * math.sin(u * 0.9), -8.0 * u)).copy()
    # warm grade: a soft orange key from the lower right (screen), then the scrim for the type
    K.draw(cv, A['warm'], 900, 1500, scale=6.0, mode='screen', opacity=0.45)
    cv[..., :3] = cv[..., :3] * A['top_k'] + A['top_tint'] * (1.0 - A['top_k'])
    sa = A['scrim_a'] * np.float32(K.ramp(t, T_PAY, T_PAY + 0.4))
    cv[..., :3] = cv[..., :3] * (1.0 - sa) + A['scrim_c'] * sa
    cam = _static_cam(t)
    A['bokeh'].draw(cv, cam, t, opacity=0.7)
    # type: lead-in line rises, the hero line slams up; light sweeps run across both
    s1 = K.ramp(t, PAY_L1 + 0.45, PAY_L1 + 1.15, 'inout_sine')
    A['l1'].rise(cv, t, 515.0, 1112, t0=PAY_L1, stagger=0.03, dur=0.6, sweep=s1 if 0 < s1 < 1 else None,
                 sweep_kw=dict(width=0.12, strength=1.4))
    s2 = K.ramp(t, PAY_L2 + 0.5, PAY_L2 + 1.25, 'inout_sine')
    A['l2'].rise(cv, t, 515.0, 1328, t0=PAY_L2, stagger=0.025, dur=0.55, dist=0.35, scale0=1.15,
                 sweep=s2 if 0 < s2 < 1 else None, sweep_kw=dict(width=0.12, strength=1.4))
    if arrive > 0.05:
        K.zoom_blur(cv, 0.2 * arrive ** 1.5)
    if out > 0.02:
        K.zoom_blur(cv, 0.2 * out)
        K.light_leak(cv, t, strength=1.2 * out, sweep=0.5 * out, angle=35,
                     colors=[K.C['HOT_PINK'], K.C['ORANGE'], K.C['AMBER']])
    return cv


def post_payoff(cv, t):
    arrive = _blip(t, T_PAY, rise=0.02, decay=20.0)
    out = K.ramp(t, T_END - PAY_OUT, T_END, 'in_expo')
    return _post(cv, t, hot=0.85 * arrive + 0.9 * out ** 2, footage=1.0 - 0.6 * out,
                  chroma=1.8 + 6 * arrive + 6 * out)


# =============================================================================================== 6. END CARD
LOGO_Y, WORD_Y_END, TAG_Y, CTA_Y, CONTACT_Y, BADGE_Y = 455.0, 805.0, 1000.0, 1128.0, 1262.0, 1385.0
WM_T, TAG_T, CTA_T, CONTACT_T, BADGE_T, CLICK_T = 21.75, 22.25, 22.75, 23.0, 23.25, 23.5
LOGO_W = 600.0                                 # on-screen width of the mark's visible body


@functools.lru_cache(maxsize=1)
def _end_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['anim'] = S3.get('logo_mark3d', 'night_anim', scale=0.7)          # mark body <= ~640 px on screen
    d['still'] = S3.get('logo_mark3d', 'night', scale=0.7)
    # wordmark straight from the provided on-dark logo (never recoloured): x 1901.., y 0..1080
    from PIL import Image
    im = Image.open(os.path.join(K.BRAND, 'logo_full_onDark.png')).convert('RGBA').crop((1905, 100, 3901, 1060))
    im = im.resize((1040, int(round(im.size[1] * 1040 / im.size[0]))), Image.LANCZOS)    # 2x its display width
    d['wm'] = np.ascontiguousarray(K.crop_to_alpha(K.sprite(im), margin=6))
    # tagline set like the logo's lockup: tracked caps, LEAF dots and rules (the logo's own tagline strip is too thin
    # to stay >= 28 px at this width)
    d['tag'] = _tagline_sprite()
    d['ring'] = _conic_ring(330, 9)
    d['ring2'] = _conic_ring(392, 4, phase=0.5)
    d['btn_size'] = ui.button_size('Start your enquiry', 112, 40)
    d['contact'] = T.render('0161 241 1332  ·  organicfostering.co.uk', 'ui', px=38, fill='IVORY')
    d['badge'] = ui.badge('Rated Good by Ofsted', 'Inspected May 2025', look='neon')
    d['glow'] = K.radial(360, K.C['MAGENTA'] * 1.1, power=2.0)
    d['bokeh'] = K.glow(K.disc(56, K.C['HOT_PINK'] * 0.8), K.C['MAGENTA'], (20, 60), 0.6)
    d['bokeh2'] = K.glow(K.disc(46, K.C['ORANGE'] * 0.9), K.C['ORANGE'], (20, 60), 0.6)
    return d


def _tagline_sprite():
    _, _, T, _ = _lazy()
    words = [T.render(w, 'flat', font='Nunito-ExtraBold', px=38, tracking=0.16, fill='IVORY') for w in
             ('NURTURE', 'DEVELOP', 'GROW')]
    gap, dot_r, rule = 28, 7, 56
    wsum = sum(w.w for w in words) + 4 * gap + 2 * (2 * dot_r) + 2 * (rule + gap)
    W, H = int(wsum + 40), 110
    spr = np.zeros((H, W, 4), np.float32)
    leaf = K.C['LEAF'] * 1.25
    x = 20.0
    cy = H / 2

    def put_rule(x0):
        a = K.rrect_alpha(rule, 7, 3.5, 2)
        r = np.dstack([a[..., None] * leaf, a]).astype(np.float32)
        K.draw(spr, r, x0 + rule / 2, cy)
    put_rule(x)
    x += rule + gap
    for i, w in enumerate(words):
        w.draw(spr, x, cy, anchor=(0.0, 0.5))
        x += w.w + gap
        if i < 2:
            K.draw(spr, K.disc(dot_r, leaf), x + dot_r, cy)
            x += 2 * dot_r + gap
    put_rule(x)
    return spr


def _conic_ring(r, width, phase=0.0):
    """Ring whose colour runs MAGENTA -> HOT_PINK -> ORANGE -> MAGENTA around it (rotate it with K.draw rot)."""
    base = K.ring(r, width, (1, 1, 1))
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = (np.arctan2(yy - h / 2, xx - w / 2) / (2 * np.pi) + 0.5 + phase) % 1.0
    c0, c1, c2 = K.C['MAGENTA'] * 2.2, K.C['HOT_PINK'] * 2.6, K.C['ORANGE'] * 2.4
    t3 = (ang * 3)[..., None]
    col = np.where(t3 < 1, c0 + (c1 - c0) * t3, np.where(t3 < 2, c1 + (c2 - c1) * (t3 - 1), c2 + (c0 - c2) * (t3 - 2)))
    spr = base.copy()
    spr[..., :3] = col * base[..., 3:4]
    return K.glow(spr, None, (6, 22, 60), 1.3)


def _sweep_add(cv, spr, cx, cy, u, scale=1.0, width=0.10, strength=1.3, angle=-30.0):
    """Light sweep over any sprite: a diagonal band masked by the sprite's alpha, added at (cx, cy)."""
    if not (0 < u < 1):
        return
    h, w = spr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    q = (xx / w) * math.cos(a) - (yy / h) * math.sin(a) * h / w
    qmin, qmax = float(q.min()), float(q.max())
    c = qmin - 0.2 + (qmax - qmin + 0.4) * u
    band = np.exp(-((q - c) / width) ** 2) + 0.8 * np.exp(-((q - c) / (width * 0.25)) ** 2)
    m = (band * spr[..., 3] * strength).astype(np.float32)
    add = np.zeros_like(spr)
    add[..., :3] = m[..., None] * np.float32([1.0, 0.92, 0.95])
    K.draw(cv, add, cx, cy, scale=scale, mode='add')


def _end_cam(t):
    u = t - T_END
    e = K.EASE['easy_ease'](K.clamp(u / 3.2))
    return K.Cam(pos=(K.lerp(-30.0, 0.0, e), K.lerp(30.0, 0.0, e), K.lerp(-1700.0, -1500.0, e)),
                 yaw=K.lerp(2.0, 0.0, e) + K.wiggle(t, 0.2, 0.25, seed=21), pitch=K.wiggle(t, 0.18, 0.2, seed=22),
                 aperture=24, focus_dist=1500.0 + K.lerp(200.0, 0.0, e))


def s_end(t):
    _, _, T, ui = _lazy()
    A = _end_assets()
    C = _common()
    u = t - T_END
    cam = _end_cam(t)
    land = _swell(t, T_END + 0.35, rise=0.4, decay=1.5)              # the mark settles: glow eases in, then relaxes
    cv = K.background('neon', t, cam, boost=0.5 * K.impulse(t, T_END, decay=3.0) + 0.2 * land,
                      center=(0.78, 0.94), rim=0.8)
    sc = K.Scene(cam)
    ly = LOGO_Y - K.CY
    # volumetric glow + magenta/orange glow rings behind the mark
    sc.billboard(A['glow'], (0.0, ly + 80.0, 700.0), 1700, mode='add',
                 opacity=(0.22 + 0.25 * land) * K.ramp(t, T_END, T_END + 0.5, 'out_cubic'))
    rp = K.ramp(t, T_END + 0.1, T_END + 1.0, 'inout_sine')
    if rp > 0:
        # magenta/orange glow rings: tilted ellipses orbiting behind the mark (the conic colours spin)
        sc.plane(A['ring'], (0.0, ly + 120.0, 140.0), 940.0 * (0.6 + 0.4 * rp), rot=(-74.0, 0.0, u * 40.0),
                 mode='add', opacity=1.0 * rp)
        sc.plane(A['ring2'], (0.0, ly + 120.0, 200.0), 1100.0 * (0.6 + 0.4 * rp), rot=(-74.0, 0.0, -u * 26.0),
                 mode='add', opacity=0.7 * rp)
    # 3D logo mark: swing-in animation (2 s, own specular sweep), then a gentle float
    if u < 2.0:
        spr = A['anim'].at_time(u)
    else:
        spr = A['still'].float_yaw(u - 2.0, amp=5.0, period=6.0)
    bb = A['still'].bbox
    lw = LOGO_W * (spr.shape[1] / (bb[2] - bb[0]))
    sc.billboard(spr, (0.0, ly + 6.0 * math.sin(u * 1.1), 0.0), lw * (0.9 + 0.1 * K.ramp(u, 0.0, 0.6, 'out_back')),
                 opacity=K.ramp(u, 0.0, 0.12))
    sc.billboard(A['bokeh'], (-520.0, 620.0, -950.0), 260, mode='add', opacity=0.45)
    sc.billboard(A['bokeh2'], (500.0, -760.0, -1050.0), 210, mode='add', opacity=0.4)
    sc.particles(C['dust'], t)
    sc.render(cv)
    # flat UI layer (screen space, crisp): wordmark, tagline, CTA, contact, badge
    k = cam.focal / 1500.0 * 1500.0 / cam.depth(np.array([0.0, 0.0, 0.0]))
    def sy(y):
        return K.CY + (y - K.CY) * k
    # wordmark builds: soft left->right wipe + rise, then a light sweep
    wp = K.ramp(t, WM_T, WM_T + 0.6, 'inout_cubic')
    if wp > 0:
        wm = A['wm']
        ws = 520.0 / wm.shape[1] * k
        _draw_wiped(cv, wm, K.CX, sy(WORD_Y_END) + 30 * (1 - K.ramp(t, WM_T, WM_T + 0.7, 'out_expo')), ws, wp)
        _sweep_add(cv, wm, K.CX, sy(WORD_Y_END), K.ramp(t, WM_T + 0.6, WM_T + 1.4, 'inout_sine'), scale=ws)
    tp = K.ramp(t, TAG_T, TAG_T + 0.6, 'out_expo')
    if tp > 0:
        tg = A['tag']
        K.draw(cv, tg, K.CX, sy(TAG_Y), scale=(K.lerp(0.86, 1.0, tp) * k, k), opacity=K.ramp(t, TAG_T, TAG_T + 0.3),
               blur=4.0 * (1 - tp))
    # CTA pill: springs in, hover glow when the cursor arrives, press + ripple on the click (beat 48)
    if t >= CTA_T:
        sp = K.spring(t - CTA_T, freq=2.6, damping=0.45)
        hover = K.ramp(t, CLICK_T - 0.35, CLICK_T - 0.1, 'out_cubic')
        press = K.impulse(t, CLICK_T - 0.02, decay=8.0) if t >= CLICK_T - 0.02 else 0.0
        btn = ui.button('Start your enquiry', hover=round(hover * 10) / 10, press=round(press * 20) / 20,
                        ripple=(t - CLICK_T) if t >= CLICK_T else None, look='neon')
        ui.place(cv, btn, K.CX, sy(CTA_Y), scale=max(sp, 0.01) * k, opacity=K.ramp(t, CTA_T, CTA_T + 0.08))
    if t >= CONTACT_T:
        cp = K.ramp(t, CONTACT_T, CONTACT_T + 0.5, 'out_expo')
        A['contact'].draw(cv, K.CX, sy(CONTACT_Y) + 24 * (1 - cp), opacity=K.ramp(t, CONTACT_T, CONTACT_T + 0.25),
                          scale=k, snap=False)
    if t >= BADGE_T:
        bp = K.spring(t - BADGE_T, freq=2.4, damping=0.5)
        A['badge'].draw(cv, K.CX, sy(BADGE_Y), scale=max(bp, 0.01) * k, opacity=K.ramp(t, BADGE_T, BADGE_T + 0.1))
    # cursor: glides in from the lower right, clicks the CTA on beat 48, rests beside it
    if t >= CLICK_T - 0.75:
        a = K.ramp(t, CLICK_T - 0.75, CLICK_T - 0.08, 'out_cubic')
        bx, by = K.CX + 212.0, sy(CTA_Y) + 18.0          # fingertip on the arrow: the hand never covers the label
        x = K.lerp(1160.0, bx, a)                  # enters from the right at button height (clear of the URL line)
        y = K.lerp(by + 30.0, by, a)
        away = K.ramp(t, CLICK_T + 0.35, CLICK_T + 0.85, 'in_cubic')
        x, y = K.lerp(x, bx + 520.0, away), K.lerp(y, by - 20.0, away)
        press = K.impulse(t, CLICK_T - 0.02, decay=9.0) if t >= CLICK_T - 0.02 else 0.0
        op = K.ramp(t, CLICK_T - 0.75, CLICK_T - 0.6) * (1 - K.ramp(t, CLICK_T + 0.5, CLICK_T + 0.85))
        if op > 0:
            ui.draw_cursor(cv, x, y, 'hand', 80, press=press, click=(t - CLICK_T) if t >= CLICK_T else None,
                           look='neon', opacity=op)
    arrive = 1.0 - K.ramp(t, T_END, T_END + 0.3, 'out_expo')
    if arrive > 0.05:
        K.zoom_blur(cv, 0.15 * arrive)
    return cv


def _draw_wiped(cv, spr, cx, cy, scale, p, soft=0.18):
    """Draw spr with a soft left->right reveal (p 0..1)."""
    if p >= 1:
        K.draw(cv, spr, cx, cy, scale=scale)
        return
    h, w = spr.shape[:2]
    xs = (np.arange(w, dtype=np.float32) + 0.5) / w
    edge = p * (1 + soft) - soft
    m = np.clip((edge + soft - xs) / soft, 0, 1).astype(np.float32)
    tmp = spr * m[None, :, None]
    K.draw(cv, tmp, cx, cy, scale=scale)


def post_end(cv, t):
    arrive = _blip(t, T_END, rise=0.02, decay=20.0)
    return _post(cv, t, hot=0.7 * arrive, chroma=1.8 + 5 * arrive)


# =============================================================================================== placeholder
def s_void(t):
    cam = _static_cam(t)
    cv = K.background('neon', t, cam)
    _common()['dust'].draw(cv, cam, t)
    return cv


# =============================================================================================== contract
def draw(t):
    if t < T_HOOK:
        return s_cold(t)
    if t < T_Q:
        return s_hook(t)
    if t < T_LIST:
        return s_question(t)
    if t < T_DOCK:
        return s_list(t)
    if t < T_PAY:
        return s_dock(t)
    if t < T_END:
        return s_payoff(t)
    return s_end(t)


def post(cv, t):
    if t < T_HOOK:
        f = _blip(t, T_HOOK, rise=0.03, decay=16.0)
        return _post(cv, t, hot=0.9 * f, footage=K.ramp(t, 0.3, 0.5),
                      chroma=1.8 + 3.0 * K.impulse(t, 0.0, decay=6.0))
    if t < T_Q:
        return post_hook(cv, t)
    if t < T_LIST:
        return post_question(cv, t)
    if t < T_DOCK:
        return post_list(cv, t)
    if t < T_PAY:
        return post_dock(cv, t)
    if t < T_END:
        return post_payoff(cv, t)
    return post_end(cv, t)


def samples(t):
    """Motion-blur sub-samples: 7 on whips / smash cuts / zoom-throughs, 5 on fast fly-ins and slams, else 3."""
    for kk in range(0, 9):                                   # montage cuts (0.5 .. 2.5)
        if abs(t - _cut_t(kk)) < 0.07:
            return 7
    for a_, b_ in ((T_LIST - WHIP_DOWN - 0.02, T_LIST + 0.45), (T_DOCK - WHIP_OUT - 0.02, T_DOCK + 0.45),
                   (T_PAY - ZOOM_OUT - 0.02, T_PAY + 0.35), (T_END - PAY_OUT - 0.02, T_END + 0.3)):
        if a_ <= t <= b_:
            return 7
    for a_, b_ in ((T_HOOK, T_Q), (T_Q, T_Q + 0.6), (T_Q + 0.95, T_Q + 1.2), (T_DOCK, T_DOCK + 0.95),
                   (T_END, T_END + 0.9), (CTA_T, CTA_T + 0.3)):
        if a_ <= t <= b_:
            return 5
    return 3


def _cap_caches():
    """Per-process cache caps for this reel (runtime attributes only; the toolkit sources are untouched). The 3D
    sprites are loaded pre-scaled, so smaller budgets keep the hit rate while a render worker stays near ~2 GB."""
    F, S3, T, ui = _lazy()
    mb = 1024 * 1024
    S3.CACHE.budget = min(S3.CACHE.budget, 192 * mb)
    K._CACHE.budget = min(K._CACHE.budget, 128 * mb)
    T._CACHE.budget = min(T._CACHE.budget, 160 * mb)
    F._FRAMES.budget = min(F._FRAMES.budget, 128 * mb)


def prewarm():
    _cap_caches()
    _common()
    _hook_assets()
    _q_assets()
    _list_assets()
    _ring_glow()
    _dock_assets()
    _pay_assets()
    _end_assets()


def cues():
    """SFX cue sheet (audio.py catalog names; align='hit' puts each sound's designed hit on t). No music."""
    c = []

    def q(t, name, gain_db=0.0, pan=0.0, align='hit', **params):
        c.append(dict(t=round(float(t), 4), name=name, gain_db=gain_db, pan=pan, align=align, params=params))
    # 0. cold open: heartbeat (lub 0.0, dub 0.3 = the iris pulses), iris shimmer, suck into the first cut
    q(0.0, 'heartbeat', 0, n=1)
    q(0.04, 'ripple', -9, dur=0.9)
    q(T_HOOK, 'reverse_swell', -6, duration=0.45)
    # 1. hook: flash hits + slams on the beats (words), whips on the &s, a zoom on 1.75, leaks shimmer
    for i in range(4):
        tb = T_HOOK + i * BEAT
        q(tb, 'flash_hit', -2, pan=0.0)
        q(tb, 'impact_soft', -3)
    for kk, d in WHIP_DIR.items():
        q(_cut_t(kk), 'whip', -2, pan=0.35 * d, direction=d)
    q(_cut_t(5), 'air_zoom', -5)
    for kk in (3, 7):
        q(_cut_t(kk), 'shimmer', -13, dur=0.5)
    # 2. the question: riser -> smash (boom + sub drop), "?" fly-in + landing, words, sweep, whip down
    q(T_Q, 'riser', -5, duration=1.5)
    q(T_Q, 'impact_big', 0)
    q(T_Q, 'sub_drop', -2, dur=1.8)
    q(T_Q + 0.14, 'whoosh_by', -6, dur=0.7, direction=-1)
    q(T_Q + 0.5, 'glass_tap', -5)
    q(T_Q + Q_TXT['could'][0], 'swish_small', -7, pan=-0.2)
    q(T_Q + Q_TXT['you'][0], 'reverse_swell', -9, duration=0.4)
    q(T_Q + Q_TXT['you'][0], 'impact_soft', -1)
    q(T_Q + Q_TXT['bea'][0], 'ui_tick', -6, pan=0.15)
    q(T_Q + Q_TXT['fc'][0], 'swish_small', -6, pan=0.2)
    q(T_Q + Q_SWEEP[0], 'shimmer', -11, dur=1.0)
    q(T_LIST, 'whip', -1, direction=-1)
    q(T_LIST, 'whoosh_fast', -7)
    # 3. checklist: window settles, click + check ding per row (rising), cursor swishes, 100 % pop, toast, whip out
    q(6.0, 'glass_tap', -6)
    for i, tk in enumerate(TICKS):
        q(tk, 'ui_click', -2, pan=-0.1)
        q(tk, 'check_ding', -4, pan=0.1, pitch=1.0 + 0.04 * i)
        if i < 4:
            q(tk + 0.42, 'swish_small', -15, pan=0.1)
    q(RING_POP, 'sparkle', -6)
    q(RING_POP, 'pop', -6)
    q(TOAST_T, 'toast_chime', -3)
    q(T_DOCK, 'whip', -1, direction=1)
    q(T_DOCK, 'whoosh_fast', -7)
    # 4. dock: tiles slide in on 16ths, headline sweep, focus hovers + taps on beats 25 / 29 / 33, glints, zoom-through
    for i in range(3):
        q(T_DOCK + 0.125 + 0.125 * i, 'card_slide', -4, pan=0.3 - 0.3 * i)
    q(12.3, 'shimmer', -13, dur=0.9)
    for i, tf in enumerate(FOCUS_T):
        q(tf - 0.12, 'ui_hover', -5, pan=-0.3 + 0.3 * i)
        q(tf, 'ui_click', -6, pan=-0.3 + 0.3 * i)
        q(tf, 'glass_tap', -7, pan=-0.3 + 0.3 * i, pitch=1.0 + 0.05 * i)
        q(tf + 0.55, 'sparkle', -13, pan=-0.3 + 0.3 * i)
        if i > 0:
            q(tf - 0.36, 'swish_small', -12, pan=-0.45 + 0.3 * i)          # cursor glides to the next tile
    q(T_PAY, 'air_zoom', -3)
    q(T_PAY, 'flash_hit', -5)
    # 5. payoff: soft landing + heartbeat reprise, the two lines, sweeps, riser into the end card
    q(T_PAY + 0.02, 'impact_soft', -4)
    q(T_PAY + 0.25, 'heartbeat', -7, n=2, bpm=64)
    q(PAY_L1, 'swish_small', -8)
    q(PAY_L2, 'reverse_swell', -9, duration=0.5)
    q(PAY_L2, 'impact_soft', -6)
    q(PAY_L2 + 0.5, 'shimmer', -11, dur=0.9)
    q(T_END, 'riser', -3, duration=2.0)
    # 6. end card: logo sting (swell -> impact + shimmer + bell + air tail), build ticks, CTA pop, the click
    q(T_END, 'logo_sting', 0)
    q(T_END, 'impact_big', -6, tail=1.2)
    q(T_END, 'sub_drop', -7, dur=1.6)
    q(WM_T, 'swish_small', -8)
    q(WM_T + 0.6, 'shimmer', -12, dur=0.9)
    q(TAG_T, 'sparkle', -10)
    q(CTA_T, 'pop', -4)
    q(CONTACT_T, 'ui_tick', -8)
    q(BADGE_T, 'sparkle', -8, pan=0.1)
    q(CLICK_T - 0.45, 'swish_small', -13, pan=0.3)
    q(CLICK_T, 'ui_click', 0)
    q(CLICK_T, 'toggle_on', -5)
    return c
