"""reel3.py: REEL 3 "NURTURE · DEVELOP · GROW" (brand story) - 1080x1920, 30 fps, 26.0 s, look 'airy', 92 BPM.

LIGHT & ORGANIC: an ivory/peach daylight world (K.background('airy') + big drifting magenta / peach / orange / lavender
blooms, dappled leaf shadows, soft light shafts), glossy green 3D leaves at three depths (near ones defocused), glossy
orbs, motes; video-in-type chapters with zoom-throughs; ends in a MAGENTA->ORANGE sunset with the logo.
SFX only (no music); every cut / accent sits on the 92 BPM grid: beat = 60/92 = 0.652174 s, B(n) = n * beat.

SHOT LIST (time s | beat | shot: content | camera | transition | SFX)
 0.000-0.652  b0-b1   HOOK / seed: the glowing 3D seed (seed/day_glow) falls in slow motion with a light trail onto
                      the ivory surface (contact shadow + glow on the ground); "A small / beginning" (ink_soft 150 px,
                      crisp 3D ink with soft long shadow) rises per glyph from frame 0 | low close camera (dist 860,
                      pitch 12), drift | - | shimmer, reverse_swell -> b1
 0.652        b1      IMPACT: squash, 4 ripple rings expand on the ground plane (perspective), flash; a circular iris
                      (glass rim MAGENTA->ORANGE) grows from the seed (r 0 -> 335 px) | shake | flash |
                      seed_plip + impact_soft + ripple + swish
 0.652-1.957  b1-b3   IRIS BURST MONTAGE: 6 flashes x a triplet 8th (0.2174 s): c01 9.4 s, c08 1.0, c12 11.4, c15 4.4,
                      c10 19.7, c17 8.9 (faces centred); punch-zoom 1.10 -> 1.0 + flash frame per cut, rim kick |
                      static | cuts inside the iris | swish_small + ui_tick per cut
 1.957        b3      iris collapses back into the seed (flash) | | iris close | reverse_swell, impact_soft, sparkle
 1.957-5.217  b3-b8   GROWTH: the 3D sprout grows from the seed point (sprout/day anim -> day_sway), copy completes:
                      "can change the / direction of a life." (96 px) on b4 / b5; leaves drift | crane up + pull back
                      (dist 860 -> 1450, pitch 12 -> 5) then slow push | - | grow_swell (b3 start), leaf_rustle x2
 5.217        b8      LEAF GUST: 7 big near-lens tumbling 3D leaves sweep up across the frame, dissolve hidden under
                      them | | leaf wipe (5 samples) | whoosh_fast + leaf_rustle
 5.217-7.174  b8-b11  NURTURE: video-in-type "NURTURE" (Nunito Black 191 px, ~925 px wide, bevel rim + extruded back +
                      soft shadow) showing c01 (two mums + girl: the three faces sit in the letter band; footage plate
                      1290 px wide, i.e. faces at letter height), big -> settled entrance, light sweep; glass pill
                      "01 / 03"; glass sub pill "A safe home & everyday care"; glossy 3D house | drift + push |
                      b10 -> b11 ZOOM THROUGH the 2nd "U" (letters x46 in_expo, plate grows x2.6 = parallax, zoom blur,
                      7 samples) | impact_soft, pop, bubble_pop, shimmer, reverse_swell + air_zoom on b11
 7.174-8.478  b11-b13 NURTURE footage: full-frame c01 (girl + right mum), scrim; pills re-enter at the top / lower
                      third | Ken Burns 1.02 -> 1.07 | - | glass_tap
 8.478        b13     VERTICAL WHIP up (content flies up, DEVELOP rises in; whip blur + chroma, 7 samples) | whip
 8.478-11.739 b13-b18 DEVELOP: VIT "DEVELOP" (194 px) with c14 (two mums + baby across the letter band; the brief
                      named c02, whose face / block tower sit on a diagonal and read as sweater texture in the
                      letters), pill "02 / 03"; b14 word glides up (x0.86 -> 167 px); sub "Matching that sees the whole
                      child"; chips Culture · Faith · Language · Identity pop on 16ths from b15 (gradient fill wipes
                      in); the 3D puzzle pair slides in and CLICKS on b17; label pill "Cultural Matching Specialists" |
                      drift | - | bubble_pops, whoosh_fast, puzzle_click + sparkle on b17, pop
11.739        b18     PUSH-THROUGH: DEVELOP flies past the lens (x2.6, zoom blur), GROW revealed | air_zoom
11.739-13.696 b18-b21 GROW: VIT "GROW" (275 px) with c17 (woman + girl with teddy, park greens / blue bench); pill
                      "03 / 03"; sub "Steady care and a sense of belonging"; the swaying 3D sprout | drift |
                      b20 -> b21 ZOOM THROUGH THE O's COUNTER: c16 seen through the hole (portal), grows to full frame
                      | reverse_swell + air_zoom on b21
13.696-15.000 b21-b23 GROW footage: full-frame c16 (woman + child, foreground leaves), scrim, pills | Ken Burns |
                      IRIS CLOSE into the heart (15.0) | leaf_rustle, glass_tap
15.000-20.217 b23-b31 KINDS OF CARE: glossy 3D heart pops out of the iris; headline "Different children / need different
                      / kinds of care" (96 px) rises on b23.5; tilted 3D orbit ring (tilt 38 deg, roll +20 deg; reel 2
                      uses 48 / -12) of six glass IMAGE tags (site photos): Short-term · Long-term · Emergency ·
                      Respite · Siblings · Teenagers, popping on 8ths from b24, depth sorted, back ones smaller /
                      blurred | camera orbits yaw -9 -> +7 deg | - | pop + impact_soft + sparkle, 6 tag pops, whoosh_by
20.217        b31     the ring flies apart, the heart SPIN-MORPHS into the 3D shield | | morph | whoosh_fast, glass_tap
20.217-22.174 b31-b34 TRUST: 3D shield + glass check pills "Independent Fostering Agency" (b31.5) · "Cultural Matching
                      Specialists" (b32) · "Rated Good by Ofsted" (b32.5) | drift | - | check_ding x3
22.174-26.000 b34-    END: trust exits, the sprout pops up; b35 its two top leaves fly into the logo's inner leaves
                      (land on b36) while logo_full.png assembles (mark pop, wordmark wipe, F-leaf pop) and a MAGENTA->
                      ORANGE sunset blooms up from the bottom; tagline "Nurture • Develop • Grow" types on; b36.5 CTA glass
                      pill "Start your enquiry →" + "0161 241 1332 · organicfostering.co.uk" (white on magenta); fully
                      settled by ~24.4 s, hold to 26.0 (1.6 s) | slow push | - | whoosh, leaf_rustle, swishes, riser +
                      logo_sting on b36, typing, pop + glass_tap on b36.5
BED: outdoor_birds at -31 dB (felt, not heard). Mix: audio.build_reel('reel3') -> workspace3/audio/reel3_sfx.wav
(+ _stem.wav), -18 LUFS, <= -1.5 dBTP.

CONTRACT (render.py): DUR, LOOK, BPM, draw(t) (pure), post(cv, t), samples(t) (3; 5-7 on the fall, gust, whip,
zooms, iris, morph, leaf flight), cues(), prewarm(). Helpers: reel3_fx.py (footage plates, masks), reel3_dev.py
(stills strips for critique).

TOOLKIT WORKAROUNDS: type3d.Glyphs._run routes an animator's `blur=` to the draw (DRAW_KEYS), so rise()/slam()
blur-ins can't be set and a constant blur is applied -> glyph_anim() calls anim() + render() directly.
"""
import functools
import math
import os

import numpy as np

import core as K
import footage as F
import sprites3d as S3
import type3d as T
import ui
import reel3_fx as X

DUR, LOOK, BPM = 26.0, 'airy', 92
BEAT = 60.0 / BPM                       # 0.652174 s


def B(n):
    """Time of beat n on the 92 BPM grid."""
    return n * BEAT


BED = 'outdoor_birds'
BED_GAIN_DB = -31.0

# section boundaries (all on the beat grid)
T_IMPACT = B(1)        # 0.652  seed lands
T_GROW = B(3)          # 1.957  iris closes, sprout grows
T_NUR = B(8)           # 5.217  NURTURE
T_DEV = B(13)          # 8.478  DEVELOP
T_GRO = B(18)          # 11.739 GROW
T_KIND = B(23)         # 15.000 kinds of care
T_TRUST = B(31)        # 20.217 trust
T_END = B(34)          # 22.174 end card
FLASH = BEAT / 3.0     # 0.2174 s: triplet-8th montage flashes

C = K.C
IV4 = np.append(C['IVORY'], 1.0).astype(np.float32)


def ease(name):
    return K.EASE[name]


def glyph_anim(g, kind, cv, t, x, y, draw_kw=None, **anim_kw):
    """Workaround (toolkit bug): Glyphs._run routes `blur=` to the draw (it is in DRAW_KEYS), so an animator's own
    blur-in (rise / slam blur=) can't be set and a constant blur is applied instead. Call anim() + render()."""
    states, blk = g.anim(kind, t, **anim_kw)
    return g.render(cv, states, x, y, block=blk, **(draw_kw or {}))


# =============================================================================================== environment
@functools.lru_cache(maxsize=1)
def _env():
    d = {}
    d['bl_mag'] = K.radial(512, C['HOT_PINK'], power=1.4)
    d['bl_peach'] = K.radial(512, K.mix(C['PEACH'], C['ORANGE'], 0.25), power=1.4)
    d['bl_orange'] = K.radial(512, C['ORANGE'], power=1.5)
    d['bl_lav'] = K.radial(512, K.mix(C['LAVENDER'], C['MAGENTA'], 0.25), power=1.4)
    d['gobo'] = _gobo()
    d['rays'] = _rays()
    d['leaf'] = S3.get('leaf', 'day')
    d['leaf_s'] = S3.get('leaf', 'day', scale=0.5)
    orbs = S3.get('orbs', 'day', scale=0.5)
    d['orb_peach'] = orbs.by_label('sphere_peach')
    d['orb_mag'] = orbs.by_label('sphere_magenta')
    d['orb_orange'] = orbs.by_label('sphere_orange')
    d['orb_torus'] = orbs.by_label('torus_glass')
    d['motes'] = K.Particles(90, seed=12, bright=0.55, colors=[C['WHITE'], C['PEACH'], C['AMBER']],
                             size=(1.5, 4.2), vel=(0, -22, 0))
    d['shadow'] = K.radial(400, C['PLUM'], power=1.6)
    return d


def _gobo():
    """Dappled leaf-shadow map (soft blurred leaf silhouettes, like sunlight through a plant): (h, w) alpha."""
    rng = np.random.default_rng(31)
    w, h = 640, 1120
    acc = np.zeros((h, w, 4), np.float32)
    leaf = S3.get('leaf', 'day', scale=0.5)
    for i in range(26):
        fr = leaf.frame(int(rng.choice([0, 4, 16, 20, 26, 40, 47])))
        x = rng.uniform(-40, w + 40)
        y = rng.uniform(-40, h * 0.62) if i < 20 else rng.uniform(h * 0.6, h + 40)
        s = rng.uniform(0.35, 0.9)
        K.draw(acc, fr, x, y, scale=s, rot=rng.uniform(0, 360), opacity=1.0)
    a = acc[..., 3]
    a = K.gblur(a, 7.0)
    a = np.clip(a * 1.2, 0, 1).astype(np.float32)
    return a


def _rays():
    """Soft warm light shafts fanning from above the top-left corner (emissive sprite, alpha 0)."""
    w, h = 720, 1280
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sx, sy = -0.25 * w, -0.18 * h
    ang = np.arctan2(yy - sy, xx - sx)
    dist = np.hypot(xx - sx, yy - sy)
    beams = [(0.60, 0.045, 1.0), (0.74, 0.020, 0.6), (0.86, 0.055, 0.85), (1.00, 0.025, 0.55),
             (1.10, 0.040, 0.7), (0.67, 0.012, 0.45)]
    a = np.zeros_like(xx)
    for c, wd, k in beams:
        a += k * np.exp(-((ang - c) / wd) ** 2)
    a *= np.clip(1 - dist / (1.35 * h), 0, 1) ** 1.3
    a = K.gblur(a, 5.0)
    col = K.mix(C['PEACH'], C['WHITE'], 0.55)
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = a[..., None] * col
    return spr


def airy_bg(t, cam, boost=0.0, rays=1.0, gobo=1.0, blooms=1.0, center=None, seed=0):
    """Ivory backdrop with big drifting colour blooms, dappled leaf shadows and soft light shafts."""
    E = _env()
    cv = K.background('airy', t, cam, boost=boost, center=center, seed=seed)
    px, py = (0.0, 0.0)
    if cam is not None:
        px = -float(cam.yaw) * 6.0 - float(cam.pos[0]) * 0.08
        py = float(cam.pitch) * 6.0 - float(cam.pos[1]) * 0.08
    if blooms > 0:
        b = blooms
        K.draw(cv, E['bl_mag'], 90 + 60 * math.sin(t * 0.31) + px, 1180 + 80 * math.sin(t * 0.23 + 1) + py,
               scale=2.3, opacity=0.30 * b)
        K.draw(cv, E['bl_peach'], 980 + 50 * math.sin(t * 0.27 + 2) + px, 380 + 70 * math.sin(t * 0.19) + py,
               scale=2.6, opacity=0.42 * b)
        K.draw(cv, E['bl_orange'], 1000 + 40 * math.sin(t * 0.21 + 4) + px, 1650 + 60 * math.sin(t * 0.33) + py,
               scale=1.9, opacity=0.30 * b)
        K.draw(cv, E['bl_lav'], 300 + 70 * math.sin(t * 0.17 + 3) + px, 260 + 50 * math.sin(t * 0.29 + 5) + py,
               scale=2.2, opacity=0.35 * b)
    if gobo > 0:
        g = E['gobo']
        gx = 540 + 30 * math.sin(t * 0.37) + px * 1.5
        gy = 960 + 22 * math.sin(t * 0.29 + 1.3) + py * 1.5
        _shadow_map(cv, g, gx, gy, 2.05, 1.6 * math.sin(t * 0.21), 0.085 * gobo)
    if rays > 0:
        K.draw(cv, E['rays'], 540 + px * 0.5, 960 + py * 0.5, scale=1.62, rot=1.5 * math.sin(t * 0.35),
               opacity=0.5 * rays * (0.85 + 0.15 * math.sin(t * 1.1)), mode='add')
    return cv


def _shadow_map(cv, a, cx, cy, scale, rot, strength):
    """Darken the canvas by a (soft) alpha map placed like a sprite (warm plum shadow)."""
    spr = _gobo_sprite(id(a))
    K.draw(cv, spr, cx, cy, scale=scale, rot=rot, opacity=strength)


@functools.lru_cache(maxsize=2)
def _gobo_sprite(_key):
    a = _env()['gobo']
    col = K.mix(C['PLUM'], C['ORANGE'], 0.25) * 0.35
    return np.dstack([a[..., None] * col, a]).astype(np.float32)


def unproject(cam, sx, sy, depth):
    pc = np.array([(sx - K.CX) * depth / cam.focal, (sy - K.CY) * depth / cam.focal, depth])
    return cam.R @ pc + cam.pos


def leaves_world(specs, cam0):
    """specs: (screen x, y, depth, on-screen width, fall px/s, leaf frame, roll) at the reference camera."""
    out = []
    for (x, y, d, w, vy, fr, rl) in specs:
        out.append((unproject(cam0, x, y, d), w * d / cam0.focal, vy * d / cam0.focal, fr, rl))
    return out


def add_leaves(sc, t, world, t_ref=0.0, speed=0.55, op=1.0):
    E = _env()
    for k, (P, w, vy, fr, rl) in enumerate(world):
        x = P[0] + 0.07 * w * math.sin(t * 0.9 + k * 1.7)
        y = P[1] + vy * (t - t_ref)
        tt = fr / 30.0 + (t - t_ref) * speed
        far = P[2] > 2600
        spr = (E['leaf_s'] if far else E['leaf']).at_time(tt, fps=30)
        sc.billboard(spr, (x, y, P[2]), w, rot=rl + 14.0 * math.sin(t * 0.7 + k), opacity=op)


def add_orbs(sc, t, specs, op=1.0):
    """specs: (name, world (x, y, z), width) -> softly bobbing glossy orbs (depth layers)."""
    E = _env()
    for k, (nm, (x, y, z), w) in enumerate(specs):
        sc.billboard(E[nm], (x + 12 * math.sin(t * 0.5 + k), y + 18 * math.sin(t * 0.63 + 2 * k), z), w, opacity=op)


# =============================================================================================== type
@functools.lru_cache(maxsize=1)
def _type():
    d = {}
    ink = dict(px=150)
    d['l1'] = T.Glyphs('A small', 'ink_soft', **ink)
    d['l2'] = T.Glyphs('beginning', 'ink_soft', **ink)
    d['l3'] = T.Glyphs('can change the', 'ink_soft', px=96)
    d['l4'] = T.Glyphs('direction of a life.', 'ink_soft', px=96)
    return d


# =============================================================================================== HOOK + GROWTH
GY = 300.0                                  # ground plane (world y, down = +)
SEED_P = np.array([0.0, GY, 0.0])
SPROUT_S = 0.70                             # sprout sprite scale at 1 px / world unit
Y_L1, Y_L2, Y_L3, Y_L4 = 285, 447, 612, 714

# hook montage: (clip, source in-point, square-crop centre, zoom)
MONTAGE = [('c01', 9.40, (0.50, 0.45), 1.00), ('c08', 1.00, (0.50, 0.27), 1.00),
           ('c12', 11.40, (0.48, 0.36), 1.00), ('c15', 4.40, (0.50, 0.42), 1.00),
           ('c10', 19.70, (0.55, 0.42), 1.05), ('c17', 8.90, (0.42, 0.33), 1.25)]


def hook_cam(t):
    """Close, low camera on the seed (0-2 s) that cranes up and pulls back as the sprout grows (2-5.2 s)."""
    u = ease('inout_cubic')(K.clamp((t - T_GROW + 0.1) / 1.9))
    dist = K.lerp(860.0, 1450.0, u) - 70.0 * K.ramp(t, 3.9, T_NUR + 0.3, 'inout_sine')
    tgt_y = K.lerp(GY - 175.0, GY - 560.0, u)
    pitch = K.lerp(12.0, 5.0, u)
    land = K.impulse(t, T_IMPACT, decay=9.0)
    sx, sy, sr = K.shake(t, 7.0 * land, 18.0, seed=3)
    yaw = K.lerp(-3.0, 2.0, ease('inout_sine')(K.clamp(t / T_NUR))) + K.wiggle(t, 0.22, 0.6, seed=4)
    return K.Cam.orbit((sx, tgt_y + sy, 0.0), dist, yaw=yaw, pitch=pitch + K.wiggle(t, 0.25, 0.3, seed=5),
                       roll=sr * 0.4, aperture=30, focus_dist=dist)


@functools.lru_cache(maxsize=1)
def _hook_assets():
    d = {}
    d['seed'] = S3.get('seed', 'day_glow')
    d['sprout'] = S3.get('sprout', 'day')
    d['sway'] = S3.get('sprout', 'day', mode='sway')
    d['halo'] = K.radial(256, C['AMBER'] * 1.6, power=2.2)
    d['halo2'] = K.radial(256, C['ORANGE'] * 1.2, power=1.4)
    # ripple ring (lies flat on the ground via draw_plane rot=(90, 0, 0)); geometry: r=200 in a 2*(200+60) box
    r = K.ring(200, 7.0, K.mix(C['PEACH'], C['MAGENTA'], 0.5), glow=0.0)
    hi = K.ring(198, 1.6, C['WHITE'] * 1.4)
    pad = (r.shape[0] - hi.shape[0]) // 2
    hi = np.pad(hi, ((pad, pad), (pad, pad), (0, 0)))
    d['ripple'] = (r + hi * 0.8).astype(np.float32)
    d['ripple_r'] = 200.0
    d['iris_rim'] = _iris_rim(340)
    d['trail'] = _trail()
    return d


def _iris_rim(r):
    """Glassy iris rim: white inner edge + MAGENTA->ORANGE gradient band with a soft glow (premultiplied)."""
    band = K.ring(r + 7, 10.0, (1, 1, 1))
    n = band.shape[0]
    g = K.gradient(n, n, [C['MAGENTA'], C['HOT_PINK'], C['ORANGE']], angle=35)
    spr = np.zeros_like(band)
    spr[..., :3] = band[..., 3:4] * g * 1.15
    spr[..., 3] = band[..., 3]
    inner = K.ring(r, 2.2, C['WHITE'] * 1.5)
    p = (n - inner.shape[0]) // 2
    inner = np.pad(inner, ((p, n - inner.shape[0] - p), (p, n - inner.shape[0] - p), (0, 0)))
    spr = spr * (1 - inner[..., 3:4]) + inner
    out = K.glow(spr, K.mix(C['HOT_PINK'], C['ORANGE'], 0.4), (6, 18, 44), 0.55)
    return out


def _trail():
    """Soft vertical light streak (slow-motion trail above the falling seed), emissive."""
    h, w = 420, 90
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.exp(-((xx - w / 2) / (w * 0.16)) ** 2) * (yy / h) ** 1.8
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = a[..., None] * K.mix(C['AMBER'], C['WHITE'], 0.3) * 0.9
    return spr


def seed_y(t):
    """World y of the seed centre (falls 0 -> T_IMPACT, tiny rebound, rests on the ground)."""
    rad = 46.0
    if t < T_IMPACT:
        u = K.clamp(t / T_IMPACT)
        return GY - rad - 300.0 * (1 - u * u)
    dt = t - T_IMPACT
    bounce = 34.0 * math.exp(-dt * 7.0) * abs(math.sin(dt * 11.0))
    return GY - rad - bounce


def draw_seed(cv, cam, t, op=1.0):
    A = _hook_assets()
    P = np.array([[0.0, seed_y(t), 0.0]])
    xy, z = cam.project(P)
    if not (z[0] > 1):
        return
    k = cam.focal / z[0]
    sx, sy = float(xy[0][0]), float(xy[0][1])
    # squash & stretch: stretched while falling, squashed at impact (spring back)
    if t < T_IMPACT:
        st = 1.0 + 0.10 * K.ramp(t, 0.2, T_IMPACT, 'in_cubic')
        sq = (1 / math.sqrt(st), st)
    else:
        s = 0.22 * math.exp(-(t - T_IMPACT) * 9.0) * math.cos((t - T_IMPACT) * 26.0)
        sq = (1 + s, 1 - s)
    sc = K.lerp(0.30, 0.175, K.ramp(t, T_IMPACT + 0.35, T_IMPACT + 0.9, 'inout_sine')) * k
    img = A['seed'].at_time(t)
    if t < T_IMPACT:
        tr = K.ramp(t, 0.0, 0.2) * (1 - K.ramp(t, T_IMPACT - 0.05, T_IMPACT + 0.05))
        K.draw(cv, A['trail'], sx, sy - 40 * k * 0.3, scale=(0.8 * k, 0.7 * k), opacity=0.55 * tr * op,
               anchor=(0.5, 1.0))
    glow_k = 1.0 + 0.9 * K.impulse(t, T_IMPACT, decay=6.0) + 1.2 * K.impulse(t, T_GROW, decay=6.0)
    K.draw(cv, A['halo2'], sx, sy, scale=1.5 * k, opacity=0.18 * glow_k * op, mode='add')
    K.draw(cv, A['halo'], sx, sy, scale=0.9 * k, opacity=0.35 * glow_k * op, mode='add')
    K.draw(cv, img, sx, sy, scale=(sc * sq[0], sc * sq[1]), opacity=op, anchor=(0.5, 0.5),
           blur=float(cam.coc(z[0])) * 0.5)


def draw_ground_fx(cv, cam, t):
    """Contact shadow, reflection glow and ripple rings on the ground plane (y = GY)."""
    A = _hook_assets()
    E = _env()
    xy, z = cam.project(np.array([[0.0, GY, 0.0]]))
    k = cam.focal / z[0]
    h = max(0.0, GY - 46.0 - seed_y(t))
    near = 1.0 / (1.0 + h / 160.0)
    K.draw(cv, E['shadow'], xy[0][0], xy[0][1], scale=(0.42 * k * (1.4 - 0.5 * near), 0.10 * k), opacity=0.35 * near)
    K.draw(cv, A['halo'], xy[0][0], xy[0][1] + 4 * k, scale=(1.2 * k, 0.26 * k), opacity=0.22 * near, mode='add')
    if t < T_IMPACT:
        return
    for i, (d0, amp) in enumerate([(0.0, 1.0), (0.13, 0.8), (0.30, 0.6), (0.55, 0.45)]):
        dt = t - T_IMPACT - d0
        if dt <= 0 or dt > 2.4:
            continue
        u = ease('out_cubic')(K.clamp(dt / 2.4))
        R = 30.0 + 760.0 * u
        op = amp * (1 - K.ramp(dt, 0.5, 2.4, 'in_out_sine' if False else 'inout_sine')) * K.ramp(dt, 0, 0.05)
        w = 2 * R * A['ripple'].shape[1] / (2 * A['ripple_r'])
        K.draw_plane(cv, A['ripple'], cam, (0.0, GY, 0.0), w, rot=(90.0, 0.0, 0.0), opacity=0.9 * op)


def draw_iris(cv, cam, t):
    """Burst montage inside a circular iris growing from the seed (6 flashes of a triplet 8th)."""
    if t < T_IMPACT or t >= T_GROW:
        return
    A = _hook_assets()
    xy, _ = cam.project(np.array([[0.0, GY - 46.0, 0.0]]))
    cx, cy = float(xy[0][0]), float(xy[0][1]) - 70.0 * K.ramp(t, T_IMPACT, T_IMPACT + 0.3, 'out_expo') * (
        1 - K.ramp(t, T_GROW - 0.16, T_GROW, 'in_expo'))
    i = min(5, int((t - T_IMPACT) / FLASH))
    tc = T_IMPACT + i * FLASH
    op = K.ramp(t, T_IMPACT, T_IMPACT + 0.3, 'out_expo')
    cl = K.ramp(t, T_GROW - 0.16, T_GROW, 'in_expo')
    kick = 0.05 * K.impulse(t, tc, decay=14.0) if i > 0 else 0.0
    r = 335.0 * op * (1 - cl) * (1 + kick)
    if r < 2:
        return
    cid, src0, ctr, zm = MONTAGE[i]
    clip = F.Clip(cid)
    D = int(math.ceil(2 * r + 6))
    zp = zm * (1.0 + 0.10 * (1 - K.ramp(t, tc, tc + FLASH, 'out_cubic')))
    img = clip.get(src0 + (t - tc) * 0.6, D, D, center=ctr, zoom=zp, look='airy')
    fl = K.impulse(t, tc, decay=26.0, attack=0.01)
    if fl > 0.01:
        img[..., :3] = img[..., :3] * (1 + 1.6 * fl) + 0.35 * fl
    a, x0, y0 = X.circle_alpha(cx, cy, r, soft=1.2)
    if a is None:
        return
    ox, oy = int(round(cx - D / 2)), int(round(cy - D / 2))
    # align the square crop to the alpha box
    h, w = a.shape
    full = np.zeros((h, w, 4), np.float32)
    sx0, sy0 = x0 - ox, y0 - oy
    sx1, sy1 = min(D, sx0 + w), min(D, sy0 + h)
    full[0:sy1 - sy0, 0:sx1 - sx0] = img[sy0:sy1, sx0:sx1]
    # soft drop shadow under the iris disc
    K.draw(cv, _env()['shadow'], cx, cy + r * 0.9, scale=(r / 140.0, r / 700.0), opacity=0.25)
    X.composite_region(cv, full, x0, y0, alpha=a)
    K.draw(cv, A['iris_rim'], cx, cy, scale=r / 340.0, opacity=min(1.0, op * 1.2))


def draw_sprout(cv, cam, t):
    A = _hook_assets()
    xy, z = cam.project(np.array([[0.0, GY, 0.0]]))
    k = cam.focal / z[0]
    t_sway = T_GROW + 2.61
    if t < t_sway:
        u = K.clamp((t - T_GROW) / 2.61)
        ta = ease('inout_sine')(u) * (119.0 / 30.0)
        img = A['sprout'].at_time(ta)
        spr = A['sprout']
    else:
        img = A['sway'].at_time(t - t_sway)
        spr = A['sway']
    piv = spr.pivot
    rf = _reflection(img)
    K.draw(cv, rf, xy[0][0], xy[0][1] + 2 * k, scale=SPROUT_S * k * 4, anchor=(piv[0] / spr.size[0], 1.0 - piv[1] / spr.size[1]),
           opacity=0.20, blur=2.0)
    K.draw(cv, _env()['shadow'], xy[0][0], xy[0][1] + 3 * k, scale=(0.75 * k, 0.12 * k), opacity=0.22)
    K.draw(cv, img, xy[0][0], xy[0][1], scale=SPROUT_S * k, anchor=(piv[0] / spr.size[0], piv[1] / spr.size[1]),
           blur=float(cam.coc(z[0])) * 0.4)


def _reflection(img):
    """Glossy-floor reflection of a sprite: 1/4-res, flipped vertically, fading out with distance from the base."""
    import cv2
    sm = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)[::-1]
    h = sm.shape[0]
    fade = np.clip(1.0 - np.arange(h, dtype=np.float32) / (0.28 * h), 0, 1) ** 1.6
    return np.ascontiguousarray(sm * fade[:, None, None])


_HOOK_LEAVES = [(140, 1500, 640, 340, 30, 22, -25), (960, 300, 700, 260, 36, 3, 35),
                (900, 1240, 1500, 120, 26, 44, 15), (170, 760, 1700, 110, 20, 20, -40),
                (780, 200, 3200, 80, 14, 46, 60), (300, 1050, 3500, 70, 12, 2, -50),
                (990, 1650, 3200, 76, 15, 24, 10)]
_HOOK_ORBS = [('orb_peach', (-520.0, -900.0, 2600.0), 150), ('orb_mag', (560.0, 380.0, 3000.0), 110),
              ('orb_torus', (470.0, -620.0, 700.0), 150)]


@functools.lru_cache(maxsize=1)
def _hook_leaf_world():
    return leaves_world(_HOOK_LEAVES, hook_cam(0.0))


def scene_hook(t):
    """0 -> T_NUR: seed fall, impact ripple, iris montage, sprout growth with the camera craning up."""
    cam = hook_cam(t)
    cv = airy_bg(t, cam, boost=0.3 * K.impulse(t, T_IMPACT, decay=4.0))
    sc = K.Scene(cam)
    add_orbs(sc, t, _HOOK_ORBS)
    add_leaves(sc, t, _hook_leaf_world())
    sc.custom((0.0, GY, 30.0), lambda c, cm: draw_ground_fx(c, cm, t))
    if t < T_GROW + 0.02:
        sc.custom((0.0, GY - 46.0, 0.0), lambda c, cm: draw_seed(c, cm, t))
    if t >= T_GROW - 0.02:
        sc.custom((0.0, GY - 60.0, -1.0), lambda c, cm: draw_sprout(c, cm, t))
    sc.particles(_env()['motes'], t)
    sc.render(cv)
    draw_iris(cv, cam, t)
    draw_hook_type(cv, t)
    return cv


def draw_hook_type(cv, t):
    Ty = _type()
    # "A small / beginning" rises in during the fall; "can change the / direction of a life." on beats 4 and 5
    glyph_anim(Ty['l1'], 'rise', cv, t, 540, Y_L1, t0=-0.22, stagger=0.045, dur=0.6, dist=0.35, blur=10, scale0=0.92)
    glyph_anim(Ty['l2'], 'rise', cv, t, 540, Y_L2, t0=-0.02, stagger=0.04, dur=0.6, dist=0.35, blur=10, scale0=0.92)
    if t >= B(4) - 0.05:
        glyph_anim(Ty['l3'], 'rise', cv, t, 540, Y_L3, t0=B(4) - 0.05, stagger=0.03, dur=0.55, dist=0.4, blur=8,
                   scale0=0.95)
    if t >= B(5) - 0.05:
        glyph_anim(Ty['l4'], 'rise', cv, t, 540, Y_L4, t0=B(5) - 0.05, stagger=0.03, dur=0.55, dist=0.4, blur=8,
                   scale0=0.95)


# =============================================================================================== chapters
# NURTURE  T_NUR..T_DEV : VIT word (c01: three faces in the letter band) -> zoom through the 2nd U -> full-frame c01
# DEVELOP  T_DEV..T_GRO : VIT word (c02: toddler + coloured blocks) -> glides up, sub, chips, puzzle click, label
# GROW     T_GRO..T_KIND: VIT word (c17: park bench) -> zoom THROUGH the O's counter (c16 portal) -> full-frame c16
N_Z0, N_Z1 = B(10), B(11)               # 6.522 -> 7.174 zoom-through (lands on the beat)
G_Z0, G_Z1 = B(20), B(21)               # 13.043 -> 13.696
D_UP = B(14)                            # 9.130 DEVELOP glides up
D_CHIPS = B(15)                         # 9.783 chips on 16ths
D_CLICK = B(17)                         # 11.087 puzzle click
WORD_Y = 760.0
PILL_Y0, SUB_Y0 = 572.0, 928.0          # chapter pill / sub pill around the word
PILL_Y1, SUB_Y1 = 300.0, 1392.0         # ... and over the full-frame footage (clear of the faces)
HOUSE_Y = 1268.0                        # NURTURE's glossy 3D object
GSPROUT_Y = 1712.0                      # GROW's sprout (soil point)

# plates: (clip, source in-point, playback speed, focus (u, v) in the source, width at rest)
P_NUR = ('c01', 8.70, 0.85, (0.50, 0.43), 1290.0)
P_NUR_END = ((0.58, 0.44), (540.0, 960.0))          # full-frame framing after the zoom: girl + right mum
P_DEV = ('c14', 2.60, 0.85, (0.49, 0.38), 1180.0)    # brief: c02 (see notes)
P_GRO = ('c17', 8.70, 0.85, (0.44, 0.42), 1260.0)
P_C16 = ('c16', 4.60, 0.70, (0.64, 0.34))


@functools.lru_cache(maxsize=1)
def _chap():
    d = {}
    d['vt_n'] = T.VideoType('NURTURE', px=191, tracking=-0.01, look='light')
    d['vt_d'] = T.VideoType('DEVELOP', px=194, tracking=-0.01, look='light')
    d['vt_g'] = T.VideoType('GROW', px=275, tracking=-0.01, look='light')
    for i in (1, 2, 3):
        d['pill%d' % i] = T.render('0%d / 03' % i, 'glass_pill_light', px=44)
    d['sub_n'] = T.render('A safe home & everyday care', 'glass_pill_light', px=44)
    d['sub_d'] = T.render('Matching that sees the whole child', 'ui_ink', px=50)
    d['sub_g'] = T.render('Steady care and a sense of belonging', 'glass_pill_light', px=36)
    d['chips'] = ['Culture', 'Faith', 'Language', 'Identity']
    d['puzzle'] = S3.get('puzzle_pair', 'day', mode='anim')
    d['label'] = ui.tag('Cultural Matching Specialists', look='airy', size=42, h=104, icon_name='puzzle',
                        accent='MAGENTA')
    d['house'] = S3.get('house', 'day')
    d['gsprout'] = S3.get('sprout', 'day', mode='sway')
    d['scrim'] = _scrim()
    return d


def _scrim():
    """Bottom/top soft dark gradient for white-on-footage moments (premultiplied, alpha only darkens)."""
    h = K.H
    y = np.linspace(0, 1, h, dtype=np.float32)
    a = 0.55 * np.clip((y - 0.55) / 0.45, 0, 1) ** 1.6 + 0.35 * np.clip((0.22 - y) / 0.22, 0, 1) ** 1.8
    spr = np.zeros((h, 8, 4), np.float32)
    spr[..., :3] = (K.C['PLUM'] * 0.15)[None, None, :] * a[:, None, None]
    spr[..., 3] = a[:, None]
    return spr


def chap_cam(t, t0):
    u = t - t0
    e = ease('easy_ease')(K.clamp(u / 3.3))
    return K.Cam(pos=(K.lerp(-30.0, 25.0, e) + K.wiggle(t, 0.3, 6.0, seed=21),
                      K.lerp(18.0, -12.0, e) + K.wiggle(t, 0.27, 5.0, seed=22), K.lerp(-1540.0, -1470.0, e)),
                 yaw=K.lerp(1.0, -0.8, e), pitch=K.wiggle(t, 0.25, 0.3, seed=23), aperture=30, focus_dist=1500.0)


_CH_LEAVES = [(120, 1560, 620, 330, 30, 22, -25), (975, 260, 680, 250, 36, 3, 35),
              (910, 1290, 1600, 118, 26, 44, 15), (160, 420, 1700, 104, 22, 20, -40),
              (760, 180, 3300, 82, 14, 46, 60), (290, 1180, 3500, 72, 12, 2, -50),
              (985, 1620, 3200, 74, 15, 24, 10), (520, 1500, 2800, 64, 18, 16, 80)]
_CH_ORBS = [('orb_peach', (-560.0, -980.0, 2400.0), 160), ('orb_mag', (600.0, 820.0, 2800.0), 120),
            ('orb_torus', (-430.0, 700.0, 650.0), 170)]


@functools.lru_cache(maxsize=4)
def _chap_leaf_world(t0):
    return leaves_world(_CH_LEAVES, chap_cam(t0, t0))


def chap_env(t, t0, cam, op=1.0, near=True):
    """Light ivory world for a chapter (backdrop + 3 depth layers). Returns (canvas, scene)."""
    cv = airy_bg(t, cam, boost=0.2 * K.beat_pulse(t, BPM, decay=4.0))
    sc = K.Scene(cam)
    add_orbs(sc, t, _CH_ORBS, op)
    wl = _chap_leaf_world(t0)
    add_leaves(sc, t, wl if near else [w for w in wl if w[0][2] > 1000], t_ref=t0, op=op)
    sc.particles(_env()['motes'], t)
    return cv, sc


def plate_at(spec, t, t0, x, y, width, focus=None):
    cid, src0, speed, foc, _ = spec if len(spec) == 5 else spec + (None,)
    clip = F.Clip(cid)
    return X.plate(clip, src0 + (t - t0) * speed, x, y, width, focus=focus or foc, look='natural')


def word_entrance(t, t0, dur=0.55):
    """Big-to-settled entrance: (scale, opacity, blur)."""
    p = K.ramp(t, t0, t0 + dur, 'out_expo')
    return K.lerp(1.32, 1.0, p), K.ramp(t, t0, t0 + 0.16, 'out_cubic'), 7.0 * (1 - p)


def zoom_state(t, z0, z1):
    return K.clamp((t - z0) / (z1 - z0))


def draw_leaf_accents(cv, t, pts, op=1.0):
    E = _env()
    for k, (x, y, s, rot, fr) in enumerate(pts):
        spr = E['leaf'].frame(fr)
        K.draw(cv, spr, x + 4 * math.sin(t * 1.3 + k), y + 5 * math.sin(t * 1.1 + 2 * k), scale=s,
               rot=rot + 6 * math.sin(t * 1.7 + k), opacity=op)


def chapter_pills(cv, t, A, idx, sub, t0, z0, z1, t_out=None):
    """Chapter pill (0N / 03) + sub around the word; they duck out while the word zooms (z0..z1) and re-enter
    over the full-frame footage at the top / lower third (clear of the faces)."""
    out = 1 - K.ramp(t, z0 + 0.10, z0 + 0.30, 'in_cubic')
    back = K.ramp(t, z1 - 0.02, z1 + 0.30, 'out_expo')
    if t_out is not None:
        back *= 1 - K.ramp(t, t_out, t_out + 0.14, 'in_cubic')
    after = t >= z1 - 0.02
    po = K.ramp(t, t0 + 0.12, t0 + 0.5, 'out_back')
    if after:
        py, op, sc = PILL_Y1 - 30 * (1 - back), back, 0.9 + 0.1 * back
    else:
        py, op, sc = PILL_Y0, K.ramp(t, t0 + 0.12, t0 + 0.3) * out, (0.8 + 0.2 * po) * (0.92 + 0.08 * out)
    if op > 0.003:
        A['pill%d' % idx].draw(cv, 540, py, scale=sc, opacity=op, snap=False)
    st = t0 + 0.32
    so = K.ramp(t, st, st + 0.5, 'out_expo')
    if after:
        sy, op = SUB_Y1 + 40 * (1 - back), back
    else:
        sy, op = SUB_Y0 + 34 * (1 - so) + 30 * (1 - out), K.ramp(t, st, st + 0.25) * out
    if op > 0.003:
        sub.draw(cv, 540, sy, opacity=op, snap=False)


# ---------------------------------------------------------------------------------------------- NURTURE
def zoom_map(P, z, rest_xy, zp_block, vt):
    """Screen position of a 2D layout point P (rest layout) under a VideoType zoom transform z (so objects around
    the word fly out with it). rest_xy = word centre at rest; zp_block = zoom point (block coords)."""
    ax, ay = rest_xy[0] + (zp_block[0] - vt.w / 2), rest_xy[1] + (zp_block[1] - vt.h / 2)
    return z['x'] + (P[0] - ax) * z['scale'], z['y'] + (P[1] - ay) * z['scale']


def draw_house(cv, t, x, y, scale=1.0, op=1.0, blur=0.0):
    A = _chap()
    h = A['house']
    img = h.float_yaw(t, amp=16, period=5.0, phase=0.2)
    fy = y + 10 * math.sin(t * 1.6)
    K.draw(cv, _env()['shadow'], x, y + 205 * scale, scale=(0.95 * scale, 0.14 * scale), opacity=0.28 * op)
    K.draw(cv, _hook_assets()['halo2'], x, fy, scale=2.6 * scale, opacity=0.10 * op, mode='add')
    K.draw(cv, img, x, fy, scale=0.60 * scale, opacity=op, blur=blur)


def scene_nurture(t):
    A = _chap()
    t0 = T_NUR
    cam = chap_cam(t, t0)
    zu = zoom_state(t, N_Z0, N_Z1)
    spec = P_NUR
    vt = A['vt_n']
    cx, cy = 540.0, WORD_Y
    if zu < 1.0:
        cv, sc = chap_env(t, t0, cam)
        sc.render(cv)
        s_in, op, bl = word_entrance(t, t0)
        ho = K.ramp(t, t0 + 0.18, t0 + 0.75, 'out_back')
        if zu <= 0:
            draw_house(cv, t, 540, HOUSE_Y + 60 * (1 - ho), 0.75 + 0.25 * ho, K.ramp(t, t0 + 0.18, t0 + 0.4))
            pw = spec[4] * s_in ** 0.35 * (1 + 0.025 * K.ramp(t, t0, N_Z0, 'inout_sine'))
            foot = plate_at(spec, t, t0, cx, cy, pw)
            sw = K.ramp(t, t0 + 0.55, t0 + 1.25, 'inout_sine')
            draw_leaf_accents(cv, t, [(118, cy - 88, 0.20, -38, 16), (978, cy + 78, 0.17, 140, 0)], op)
            vt.draw(cv, foot, cx, cy, scale=s_in, opacity=op, blur=bl, sweep=sw if 0 < sw < 1 else None)
        else:
            zp = vt.zoom_point('U', index=4)
            z = vt.zoom(zu, zp, cx, cy, s0=1.0, s1=46.0, ease='in_expo', move_ease='inout_cubic')
            hx, hy = zoom_map((540.0, HOUSE_Y), z, (cx, cy), zp, vt)
            if z['scale'] < 6:
                draw_house(cv, t, hx, hy, z['scale'], 1 - K.ramp(z['scale'], 2.5, 6.0), blur=4 * (z['scale'] - 1))
            ep = ease('in_cubic')(zu)
            (fu, fv), (ex, ey) = P_NUR_END
            foc = (K.lerp(spec[3][0], fu, ep), K.lerp(spec[3][1], fv, ep))
            px_, py_ = K.lerp(cx, ex, ep), K.lerp(cy, ey, ep)
            p0 = spec[4] * 1.025
            p1 = X.cover_width(F.Clip(spec[0]), (fu, fv), ex, ey) * 1.02
            pw = p0 * (p1 / p0) ** ep
            foot = plate_at(spec, t, t0, px_, py_, pw, focus=foc)
            vt.draw(cv, foot, **z)
            K.zoom_blur(cv, 0.12 * ease('in_cubic')(zu) * (1 - K.ramp(zu, 0.92, 1.0)))
    else:
        (fu, fv), (ex, ey) = P_NUR_END
        drift = K.ramp(t, N_Z1 - 0.2, T_DEV + 0.4, 'inout_sine')
        pw = X.cover_width(F.Clip(spec[0]), (fu, fv), ex, ey) * (1.02 + 0.05 * drift)
        cv = plate_at(spec, t, t0, ex, ey, pw, focus=(fu, fv))
        cv[..., 3] = 1.0
        K.over(cv, _scrim_full())
        sc = K.Scene(cam)
        add_leaves(sc, t, [w for w in _chap_leaf_world(t0) if w[0][2] < 1000], t_ref=t0)
        sc.particles(_env()['motes'], t, opacity=0.6)
        sc.render(cv)
    chapter_pills(cv, t, A, 1, A['sub_n'], t0, N_Z0, N_Z1)
    return cv


@functools.lru_cache(maxsize=1)
def _scrim_full():
    import cv2
    s = _chap()['scrim']
    return np.ascontiguousarray(cv2.resize(s, (K.W, K.H), interpolation=cv2.INTER_LINEAR))


# ---------------------------------------------------------------------------------------------- DEVELOP
DEV_Y0, DEV_Y1 = 800.0, 400.0
SUBD_Y, CHIP_Y, PUZ_Y, LABEL_Y = 548.0, 686.0, 1020.0, 1352.0
CHIP_SIZE, CHIP_H = 42, 88


def scene_develop(t):
    A = _chap()
    t0 = T_DEV
    cam = chap_cam(t, t0)
    cv, sc = chap_env(t, t0, cam)
    sc.render(cv)
    vt = A['vt_d']
    s_in, op, bl = word_entrance(t, t0)
    up = ease('inout_cubic')(K.ramp(t, D_UP - 0.12, D_UP + 0.36, 'linear'))
    cy = K.lerp(DEV_Y0, DEV_Y1, up)
    sw_ = K.lerp(1.0, 0.86, up) * s_in
    pw = P_DEV[4] * sw_ ** 0.6
    foot = plate_at(P_DEV, t, t0, 540.0, cy, pw)
    sweep = K.ramp(t, t0 + 0.5, t0 + 1.15, 'inout_sine')
    draw_leaf_accents(cv, t, [(112 + 60 * up, cy - 88 * sw_, 0.19, -35, 16),
                              (985 - 50 * up, cy + 80 * sw_, 0.16, 145, 0)], op)
    vt.draw(cv, foot, 540.0, cy, scale=sw_, opacity=op, blur=bl, sweep=sweep if 0 < sweep < 1 else None)
    po = K.ramp(t, t0 + 0.12, t0 + 0.5, 'out_back')
    A['pill2'].draw(cv, 540, cy - 180 * sw_, scale=0.8 + 0.2 * po, opacity=K.ramp(t, t0 + 0.12, t0 + 0.3), snap=False)
    so = K.ramp(t, D_UP + 0.30, D_UP + 0.80, 'out_expo')
    if so > 0:
        A['sub_d'].draw(cv, 540, SUBD_Y + 26 * (1 - so), opacity=K.ramp(t, D_UP + 0.30, D_UP + 0.50), snap=False)
    chips = A['chips']
    ws = [ui.chip_size(c, size=CHIP_SIZE, h=CHIP_H)[0] for c in chips]
    gap = 16
    x = 540 - (sum(ws) + gap * (len(ws) - 1)) / 2
    for i, (c, w) in enumerate(zip(chips, ws)):
        tc = D_CHIPS + i * BEAT / 4
        if t >= tc - 0.01:
            pop = K.spring(t - tc, freq=2.6, damping=0.45)
            sel = K.ramp(t, tc + 0.16, tc + 0.5, 'out_cubic')
            spr = ui.chip(c, sel, look='airy', size=CHIP_SIZE, h=CHIP_H, origin=(0.3, 0.5))
            ui.place(cv, spr, x + w / 2, CHIP_Y + 18 * (1 - pop), scale=max(0.01, 0.6 + 0.4 * pop),
                     opacity=K.ramp(t, tc, tc + 0.08))
        x += w + gap
    pz = A['puzzle']
    t_start = D_CLICK - 25.0 / 30.0
    if t >= t_start - 0.05:
        ta = max(0.0, t - t_start)
        img = pz.at_time(ta)
        pop = 1.0 + 0.06 * K.impulse(t, D_CLICK, decay=8.0)
        K.draw(cv, _env()['shadow'], 540, PUZ_Y + 235, scale=(1.5, 0.17), opacity=0.24 * K.ramp(t, t_start, D_CLICK))
        gl = K.impulse(t, D_CLICK, decay=6.0)
        K.draw(cv, _hook_assets()['halo2'], 540, PUZ_Y, scale=3.4, opacity=(0.10 + 0.35 * gl) *
               K.ramp(t, t_start, D_CLICK), mode='add')
        K.draw(cv, img, 540, PUZ_Y, scale=0.74 * pop, opacity=K.ramp(t, t_start - 0.05, t_start + 0.12))
    lp = K.ramp(t, D_CLICK + 0.05, D_CLICK + 0.45, 'out_back')
    if lp > 0:
        A['label'].draw(cv, 540, LABEL_Y + 24 * (1 - lp), scale=0.85 + 0.15 * lp,
                        opacity=K.ramp(t, D_CLICK + 0.05, D_CLICK + 0.2))
    return cv


# ---------------------------------------------------------------------------------------------- GROW
def draw_gsprout(cv, t, x, y, scale=1.0, op=1.0, blur=0.0):
    A = _chap()
    sp = A['gsprout']
    img = sp.at_time(t)
    piv = sp.pivot
    K.draw(cv, _env()['shadow'], x, y + 4 * scale, scale=(0.8 * scale, 0.12 * scale), opacity=0.25 * op)
    K.draw(cv, img, x, y, scale=0.56 * scale, opacity=op, blur=blur,
           anchor=(piv[0] / sp.size[0], piv[1] / sp.size[1]))


def scene_grow(t):
    A = _chap()
    t0 = T_GRO
    cam = chap_cam(t, t0)
    zu = zoom_state(t, G_Z0, G_Z1)
    vt = A['vt_g']
    c16 = F.Clip(P_C16[0])
    fu, fv = P_C16[3]
    cx, cy = 540.0, WORD_Y
    if zu < 1.0:
        cv, sc = chap_env(t, t0, cam)
        sc.render(cv)
        s_in, op, bl = word_entrance(t, t0 - 0.16, dur=0.6)
        zp = vt.zoom_point('O', kind='counter')
        gr = K.ramp(t, t0 - 0.05, t0 + 0.65, 'out_back')
        if zu <= 0:
            draw_gsprout(cv, t, 540, GSPROUT_Y + 80 * (1 - gr), 0.7 + 0.3 * gr, K.ramp(t, t0 - 0.05, t0 + 0.15))
            pw = P_GRO[4] * s_in ** 0.35 * (1 + 0.03 * K.ramp(t, t0, G_Z0, 'inout_sine'))
            foot = plate_at(P_GRO, t, t0, cx, cy, pw)
            sw = K.ramp(t, t0 + 0.55, t0 + 1.25, 'inout_sine')
            draw_leaf_accents(cv, t, [(150, cy - 120, 0.22, -30, 16), (950, cy + 120, 0.18, 150, 0)], op)
            vt.draw(cv, foot, cx, cy, scale=s_in, opacity=op, blur=bl, sweep=sw if 0 < sw < 1 else None)
        else:
            z = vt.zoom(zu, zp, cx, cy, s0=1.0, s1=60.0, ease='in_expo', move_ease='inout_cubic')
            sx_, sy_ = zoom_map((540.0, GSPROUT_Y), z, (cx, cy), zp, vt)
            if z['scale'] < 5:
                draw_gsprout(cv, t, sx_, sy_, z['scale'], 1 - K.ramp(z['scale'], 2.0, 5.0), blur=4 * (z['scale'] - 1))
            sc_ = z['scale']
            ox, oy = z['x'], z['y']
            ep = ease('in_cubic')(zu)
            p1 = X.cover_width(c16, (fu, fv), 540.0, 960.0) * 1.02
            pw16 = p1 * 0.45 * (1 / 0.45) ** ep
            portal = X.plate(c16, P_C16[1] + (t - G_Z0) * P_C16[2], ox, oy, pw16, focus=(fu, fv), look='airy',
                             region=True)
            rx, ry = 74.0 * sc_, 88.0 * sc_
            if portal[0] is not None:
                spr, x0, y0 = portal
                yy, xx = np.mgrid[y0:y0 + spr.shape[0], x0:x0 + spr.shape[1]].astype(np.float32)
                d = np.sqrt(((xx + 0.5 - ox) / rx) ** 2 + ((yy + 0.5 - oy) / ry) ** 2)
                a = np.clip((1 - d) * min(rx, ry) / 1.5 + 0.5, 0, 1)
                X.composite_region(cv, spr, x0, y0, alpha=a)
            pwg = P_GRO[4] * 1.03 * (1.6 ** ep)
            foot = plate_at(P_GRO, t, t0, cx + (z['x'] - cx) * 0.3, cy + (z['y'] - cy) * 0.3, pwg)
            vt.draw(cv, foot, **z)
            K.zoom_blur(cv, 0.12 * ease('in_cubic')(zu) * (1 - K.ramp(zu, 0.92, 1.0)))
    else:
        drift = K.ramp(t, G_Z1 - 0.2, T_KIND + 0.4, 'inout_sine')
        pw = X.cover_width(c16, (fu, fv), 540.0, 960.0) * (1.02 + 0.05 * drift)
        cv = X.plate(c16, P_C16[1] + (t - G_Z0) * P_C16[2], 540.0, 960.0, pw, focus=(fu, fv), look='airy')
        cv[..., 3] = 1.0
        K.over(cv, _scrim_full())
        sc = K.Scene(cam)
        sc.particles(_env()['motes'], t, opacity=0.6)
        sc.render(cv)
    chapter_pills(cv, t, A, 3, A['sub_g'], t0, G_Z0, G_Z1, t_out=T_KIND - 0.36)
    return cv


# ---------------------------------------------------------------------------------------------- KINDS + TRUST
# KINDS  T_KIND..T_TRUST : c16 irises down into a glossy 3D heart; headline; tilted orbit ring of six image tags
# TRUST  T_TRUST..T_END  : the ring flies apart, the heart spin-morphs into a 3D shield, three check pills stack in
HEART_W = (0.0, 270.0, 0.0)             # world centre of the heart / ring
TAG_T0 = B(24)                          # first tag pops; then one per 8th note
KH_Y = (330.0, 442.0, 554.0)            # headline lines
SHIELD_XY = (540.0, 640.0)
TRUST_Y = (1004.0, 1136.0, 1268.0)
TRUST_T = (B(31.5), B(32), B(32.5))     # 20.543, 20.870, 21.196
SITE = [('Short-term', '03-short-term-everyday-connection.webp'), ('Long-term', '04-long-term-family-belonging.webp'),
        ('Emergency', '05-emergency-a-calm-welcome.webp'), ('Respite', '06-respite-outdoor-play.webp'),
        ('Siblings', '07-siblings-growing-together.webp'), ('Teenagers', '08-teenagers-time-to-talk.webp')]


@functools.lru_cache(maxsize=1)
def _kinds():
    d = {}
    d['h1'] = T.Glyphs('Different children', 'ink_soft', px=96)
    d['h2'] = T.Glyphs('need different', 'ink_soft', px=96)
    d['h3'] = T.Glyphs('kinds of care', 'ink_soft', px=96)
    tags = []
    for lab, nm in SITE:
        th = F.still(nm, 150, 150, look='airy', center=(0.5, 0.4))
        tags.append(ui.tag(lab, th, look='airy', size=34, h=84, thumb_key=nm))
    d['tags'] = tags
    d['heart'] = S3.get('heart', 'day')
    d['shield'] = S3.get('shield_check', 'day')
    d['pink'] = K.radial(512, C['HOT_PINK'], power=2.0)
    d['trust'] = [ui.tag(x, look='airy', size=40, h=104, icon_name='check', accent='LEAF')
                  for x in ('Independent Fostering Agency', 'Cultural Matching Specialists', 'Rated Good by Ofsted')]
    return d


def kinds_cam(t):
    u = ease('easy_ease')(K.clamp((t - T_KIND + 0.3) / (T_END - T_KIND + 0.3)))
    yaw = K.lerp(-15.0, 11.0, u) + K.wiggle(t, 0.2, 0.6, seed=31)
    pitch = K.lerp(11.0, 4.0, u) + K.wiggle(t, 0.22, 0.4, seed=32)
    dist = K.lerp(1640.0, 1420.0, u)
    tgt = (HEART_W[0], HEART_W[1] + 60.0, HEART_W[2])           # ring centred just above mid-frame
    return K.Cam.orbit(tgt, dist, yaw=yaw, pitch=pitch, aperture=22, focus_dist=dist - 200.0)


_K_LEAVES = [(110, 1560, 640, 320, 28, 22, -25), (985, 300, 700, 240, 34, 3, 35),
             (930, 820, 1700, 110, 24, 44, 15), (140, 760, 1800, 100, 20, 20, -40),
             (780, 160, 3300, 80, 14, 46, 60), (300, 1700, 3400, 72, 12, 2, -50)]
_K_ORBS = [('orb_peach', (-600.0, -1050.0, 2500.0), 170), ('orb_mag', (640.0, 900.0, 2600.0), 120),
           ('orb_torus', (520.0, -760.0, 800.0), 150), ('orb_orange', (-520.0, 980.0, 900.0), 90)]


@functools.lru_cache(maxsize=1)
def _k_leaf_world():
    return leaves_world(_K_LEAVES, kinds_cam(T_KIND))


def heart_pop(t):
    """Heart scale factor: pops from the iris size (0.78) with spring overshoot as the c16 iris lands."""
    if t < T_KIND - 0.04:
        return 0.0
    return 0.78 + 0.22 * K.spring(t - (T_KIND - 0.04), freq=2.4, damping=0.38)


def scene_kinds(t):
    A = _kinds()
    cam = kinds_cam(t)
    cv = airy_bg(t, cam, boost=0.35 * K.impulse(t, T_KIND, decay=4.0) + 0.15 * K.beat_pulse(t, BPM, decay=5.0),
                 center=(0.5, 0.55))
    sc = K.Scene(cam)
    add_orbs(sc, t, _K_ORBS)
    add_leaves(sc, t, _k_leaf_world(), t_ref=T_KIND)
    sc.particles(_env()['motes'], t)
    sc.render(cv)
    hxy, hz = cam.project(np.array([HEART_W]))
    hx, hy = float(hxy[0][0]), float(hxy[0][1])
    k = cam.focal / hz[0]
    # morph timing (heart -> shield) and ring exit
    mo = K.ramp(t, T_TRUST - 0.12, T_TRUST + 0.22, 'inout_cubic')
    ring_out = K.ramp(t, T_TRUST - 0.30, T_TRUST + 0.08, 'in_cubic')
    # the hero sits between the ring halves; it travels up to the shield spot during the morph
    gx = K.lerp(hx, SHIELD_XY[0], mo)
    gy = K.lerp(hy, SHIELD_XY[1], mo)

    def hero(c):
        pop = heart_pop(t)
        if pop <= 0:
            return
        K.draw(c, A['pink'], gx, gy, scale=1.5 * k * pop, opacity=(0.22 + 0.4 * K.impulse(t, T_KIND, 6.0)) * (1 - 0.5 * mo))
        if mo < 1:
            yaw = 14 * math.sin((t - T_KIND) * 1.3) * (1 - mo) + 40 * mo
            img = A['heart'].at_yaw(yaw)
            K.draw(c, img, gx, gy + 8 * math.sin(t * 1.5), scale=0.60 * k * pop * (1 - 0.35 * mo), opacity=1 - mo)
        if mo > 0:
            simg = A['shield'].at_yaw(-40 * (1 - mo) + 10 * math.sin((t - T_TRUST) * 1.2) * mo)
            K.draw(c, A['pink'], gx, gy, scale=1.4, opacity=0.18 * mo)
            K.draw(c, _env()['shadow'], gx, gy + 265, scale=(1.15, 0.15), opacity=0.22 * mo)
            K.draw(c, simg, gx, gy + 6 * math.sin(t * 1.4), scale=0.72 * (0.6 + 0.4 * mo), opacity=mo)
    if t < T_TRUST + 0.1:
        enter = [K.ramp(t, TAG_T0 + i * BEAT / 2, TAG_T0 + i * BEAT / 2 + 0.35, 'linear') for i in range(6)]
        phase = 0.06 + (t - T_KIND) * 0.058 + 0.10 * (1 - math.exp(-2.5 * max(0.0, t - T_KIND))) + 0.35 * ring_out ** 2
        rad = (342.0 * (1 + 0.9 * ring_out), 330.0 * (1 + 0.9 * ring_out))
        image_ring(cv, cam, A['tags'], phase, HEART_W, rad, 38.0, 20.0, mid=hero, enter=enter,
                   opacity=1 - ring_out, wave=0.0)
    else:
        hero(cv)
    # headline (rises in on the off-beat, lifts out before the morph)
    for i, (g, y) in enumerate(zip((A['h1'], A['h2'], A['h3']), KH_Y)):
        t0 = B(23.5) + 0.09 * i
        if t >= t0:
            sw = K.ramp(t, B(26) + 0.08 * i, B(27.5) + 0.08 * i, 'inout_sine')
            glyph_anim(g, 'rise', cv, t, 540, y, draw_kw=dict(sweep=sw) if 0 < sw < 1 else None, t0=t0,
                       stagger=0.025, dur=0.55, dist=0.4, blur=8, scale0=0.95, out_t0=T_TRUST - 0.32 + 0.04 * i,
                       out_dur=0.3)
    # trust pills
    if t >= TRUST_T[0] - 0.02:
        for i, (p_, y, tt) in enumerate(zip(A['trust'], TRUST_Y, TRUST_T)):
            if t < tt - 0.01:
                continue
            sp = K.spring(t - tt, freq=2.3, damping=0.5)
            out = K.ramp(t, T_END - 0.20 + 0.04 * i, T_END + 0.16 + 0.04 * i, 'in_cubic')
            p_.draw(cv, 540, y + 90 * (1 - sp) + 260 * out, scale=0.9 + 0.1 * sp,
                    opacity=K.ramp(t, tt, tt + 0.1) * (1 - out))
    return cv


def _ring_points(angles, radius, tilt, roll):
    """Tilted, rolled ellipse points (same convention as ui.orbit_ring): returns (N, 3), pre-roll depth z."""
    rx, rz = radius
    x = rx * np.cos(angles)
    z = rz * np.sin(angles)
    tl, rl = math.radians(tilt), math.radians(roll)
    y = -z * math.sin(tl)
    z2 = z * math.cos(tl)
    return np.stack([x * math.cos(rl) - y * math.sin(rl), x * math.sin(rl) + y * math.cos(rl), z2], 1), z


def image_ring(cv, cam, panels, phase, center, radius, tilt, roll, mid=None, enter=None, opacity=1.0, wave=48.0,
               back_scale=0.80, back_dim=0.68, back_blur=3.0):
    """Orbit ring of glass image tags (like ui.orbit_ring, which has no per-item offsets): neighbouring tags are
    alternately raised / lowered by `wave` world units, so two tags passing the front side by side never overlap.
    Depth sorted; back half smaller, dimmer, blurred (+ camera DOF); thin ring line; mid() drawn between halves."""
    n = len(panels)
    ang = 2 * math.pi * (np.arange(n) / n + phase) + math.pi / 2
    P, z = _ring_points(ang, radius, tilt, roll)
    P[:, 1] += wave * np.where(np.arange(n) % 2 == 0, -1.0, 1.0)
    zr = float(np.max(np.abs(z))) or 1.0
    Pw = P + np.asarray(center, np.float64)
    depths = np.array([cam.depth(q) for q in Pw])
    rc = ui.LOOKS['airy'].accent
    ui._ring_line(cv, cam, center, radius, tilt, roll, rc, 'back', 0.30 * opacity, light=True)
    rot = (cam.pitch, cam.yaw, cam.roll)
    drew_mid = False
    for idx in np.argsort(-depths):
        back = float((z[idx] / zr + 1) / 2)
        if not drew_mid and back < 0.5:
            if mid is not None:
                mid(cv)
            ui._ring_line(cv, cam, center, radius, tilt, roll, rc, 'front', 0.55 * opacity, light=True)
            drew_mid = True
        e = 1.0 if enter is None else float(enter[idx])
        if e <= 0:
            continue
        pnl = panels[idx]
        sc = (1 + (back_scale - 1) * back) * (0.6 + 0.4 * K.EASE['out_back'](min(e, 1.0)))
        op = opacity * (1 + (back_dim - 1) * back) * min(1.0, e * 2)
        pnl.plane(cv, cam, Pw[idx], pnl.w * sc, rot, opacity=op, dof=True, blur=back_blur * back ** 1.5,
                  shadow=0.7 * (1 - back * 0.6))
    if not drew_mid:
        if mid is not None:
            mid(cv)
        ui._ring_line(cv, cam, center, radius, tilt, roll, rc, 'front', 0.55 * opacity, light=True)


def iris_to_heart(cv, t, inner):
    """GROW footage (inner canvas) irises down into the heart's position (circle mask + glass rim)."""
    u = ease('in_cubic')(K.ramp(t, T_KIND - 0.30, T_KIND, 'linear'))
    fade = 1 - K.ramp(t, T_KIND, T_KIND + 0.07, 'linear')
    cam = kinds_cam(t)
    hxy, _ = cam.project(np.array([HEART_W]))
    cx = K.lerp(540.0, float(hxy[0][0]), u)
    cy = K.lerp(960.0, float(hxy[0][1]), u)
    r = K.lerp(1150.0, 165.0, u) * (1 - 0.25 * (1 - fade))
    a, x0, y0 = X.circle_alpha(cx, cy, r, soft=1.5)
    if a is not None:
        X.composite_region(cv, inner[y0:y0 + a.shape[0], x0:x0 + a.shape[1]], x0, y0, alpha=a, opacity=fade)
    K.draw(cv, _hook_assets()['iris_rim'], cx, cy, scale=r / 340.0, opacity=K.ramp(u, 0.0, 0.3) * fade)
    return cv


# ---------------------------------------------------------------------------------------------- END
# T_END: trust exits, the sprout pops up; B35 two top leaves fly into the logo's inner leaves (land B36), the logo
# assembles on ivory while a MAGENTA->ORANGE sunset blooms up from the bottom; tagline types on; B37 CTA pill.
LOGO_W = 920.0
LOGO_Y = 730.0                          # centre of the lockup (tagline row excluded)
TAGLINE_Y = 944.0
CTA_Y, CONTACT_Y = 1404.0, 1532.0
E_SPROUT_Y = 1560.0
SUN_TOP0, SUN_TOP1 = 1960.0, 1050.0     # sunset horizon (alpha 0 line) start / end
E_FLY0, E_LAND = B(35), B(36)           # 22.826 -> 23.478
E_TYPE0 = B(36) + 0.10
E_CTA = B(36.5)                         # 23.804


@functools.lru_cache(maxsize=1)
def _logo():
    import cv2
    im = cv2.imread(os.path.join(K.BRAND, 'logo_full.png'), cv2.IMREAD_UNCHANGED)
    im = im[:1080]                                          # lockup without the small tagline row (typed big)
    a = im[..., 3]
    b, g, r = im[..., 0].astype(int), im[..., 1].astype(int), im[..., 2].astype(int)
    green = ((g > r + 20) & (g > b + 20) & (a > 128)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(green)
    comps = {}
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if area < 5000 or w < 60:
            continue
        key = 'leafF' if y < 50 else ('leafL' if x < 500 else 'leafR')
        comps[key] = (lab == i)
    sc = LOGO_W / im.shape[1]
    out_w, out_h = int(round(LOGO_W)), int(round(im.shape[0] * sc))
    rgba = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
    base = K.sprite(rgba)                                   # premultiplied linear
    d = {'size': (out_w, out_h), 'scale': sc}
    masks = {}
    for kname, m in comps.items():
        mm = cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
        masks[kname] = mm
    rest = np.ones(a.shape, np.float32)
    for mm in masks.values():
        rest -= mm
    rest = np.clip(rest, 0, 1)
    xs = np.arange(im.shape[1])[None, :]
    mark_m = rest * (xs < 1785)
    word_m = rest * (xs >= 1785)

    def lay(m):
        spr = base * m[..., None]
        return cv2.resize(spr, (out_w, out_h), interpolation=cv2.INTER_AREA)
    d['mark'] = lay(mark_m)
    d['word'] = lay(word_m)
    for kname, mm in masks.items():
        d[kname] = lay(mm)
        ys, xs_ = np.nonzero(comps[kname])
        d[kname + '_c'] = (float(xs_.mean()) * sc, float(ys.mean()) * sc)
        d[kname + '_h'] = float(ys.max() - ys.min()) * sc
    d['tagline'] = T.Glyphs('Nurture • Develop • Grow', 'flat', px=58, font='Nunito-ExtraBold',
                            fill=('MAGENTA', 'ORANGE'), fill_angle=0, shadow=0.12, shadow_color='#5B2E52',
                            shadow_offset=(0.0, 0.04), shadow_blur=0.05)
    d['cta'] = T.render('Start your enquiry →', 'glass_pill_light', px=50, fill='INK', pill_tint='WHITE',
                        pill_tint_amount=0.2, pill_shadow=0.3)
    d['contact'] = T.render('0161 241 1332  ·  organicfostering.co.uk', 'ui', px=38, fill='WHITE',
                            shadow=0.45, shadow_color='#5B174F', shadow_offset=(0.0, 0.05), shadow_blur=0.12)
    d['sunset'] = _sunset()
    return d


def _sunset():
    """Sunset bloom sprite (1080 x 1100, drawn with its top row on the horizon line): transparent at the horizon,
    AMBER -> ORANGE -> HOT_PINK -> MAGENTA -> PLUM going down (soft 360 px alpha ramp, slight 35 deg warmth)."""
    import cv2
    w, h = 270, 275
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    y = yy * 4.0                        # canvas px below the horizon
    x = xx / w
    stops = [(0.0, C['AMBER'] * 1.1), (170.0, C['ORANGE']), (400.0, C['HOT_PINK']), (620.0, C['MAGENTA']),
             (1100.0, K.mix(C['MAGENTA'], C['PLUM'], 0.6))]
    col = np.zeros((h, w, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (y >= p0) & (y <= p1)
        f = np.clip((y - p0) / (p1 - p0), 0, 1)[..., None]
        col = np.where(m[..., None], c0 * (1 - f) + c1 * f, col)
    col *= (1 + 0.10 * (x - 0.5))[..., None] * np.array([1.0, 1.0, 1.0], np.float32)
    a = np.clip(y / 380.0, 0, 1)
    a = a * a * (3 - 2 * a)
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = col * a[..., None]
    spr[..., 3] = a
    return np.ascontiguousarray(cv2.resize(spr, (K.W, 1100), interpolation=cv2.INTER_CUBIC))


def end_cam(t):
    u = ease('easy_ease')(K.clamp((t - T_END) / (DUR - T_END)))
    return K.Cam(pos=(K.lerp(-20.0, 10.0, u), K.lerp(10.0, -10.0, u), K.lerp(-1520.0, -1440.0, u)),
                 yaw=K.lerp(0.8, -0.4, u), pitch=K.wiggle(t, 0.2, 0.25, seed=41), aperture=24, focus_dist=1500.0)


def logo_xy(cx_logo, cy_logo, p):
    W_, H_ = _logo()['size']
    return cx_logo - W_ / 2 + p[0], cy_logo - H_ / 2 + p[1]


def scene_end(t):
    L = _logo()
    cam = end_cam(t)
    sun = ease('inout_cubic')(K.ramp(t, E_FLY0, E_FLY0 + 1.1, 'linear'))
    cv = airy_bg(t, cam, rays=1.0 - 0.5 * sun)
    sc = K.Scene(cam)
    add_orbs(sc, t, _K_ORBS[:3])
    add_leaves(sc, t, [w for w in _k_leaf_world() if w[0][2] > 1000], t_ref=T_KIND)
    sc.particles(_env()['motes'], t)
    sc.render(cv)
    # sunset rises from the bottom (horizon edge from y 1920 -> ~1180)
    if sun > 0:
        top = K.lerp(SUN_TOP0, SUN_TOP1, sun)
        K.draw(cv, L['sunset'], 540, top, anchor=(0.5, 0.0), opacity=1.0)
        # the low sun: a soft white-amber glow sitting on the horizon + warm haze above it
        K.draw(cv, _hook_assets()['halo'], 540 + 60 * math.sin(t * 0.3), top + 300, scale=(3.6, 1.5),
               opacity=0.32 * sun, mode='add')
        K.draw(cv, _hook_assets()['halo2'], 540, top + 160, scale=(8.0, 1.6), opacity=0.16 * sun, mode='add')
    # sprout pops up, its top leaves fly into the logo, then it fades back into the sunset
    sp = _hook_assets()['sway']
    grow = K.spring(t - (T_END - 0.05), freq=2.0, damping=0.5) if t >= T_END - 0.05 else 0.0
    fade = K.ramp(t, E_FLY0 + 0.05, E_LAND - 0.05, 'inout_sine')
    ss = 0.62
    if grow > 0 and fade < 1:
        img = sp.at_time(t - T_END)
        if t >= E_FLY0:                       # the two top leaves have left: cut them off the sprite
            img = img * _top_leaf_cut()[:, None, None]
        piv = sp.pivot
        K.draw(cv, _env()['shadow'], 540, E_SPROUT_Y + 4, scale=(0.75 * grow, 0.12), opacity=0.22 * (1 - fade))
        K.draw(cv, img, 540, E_SPROUT_Y + 40 * fade, scale=ss * max(grow, 0.01) * (1 - 0.15 * fade),
               anchor=(piv[0] / sp.size[0], piv[1] / sp.size[1]), opacity=1 - fade, blur=6 * fade)
    # logo assembly
    lp = K.spring(t - E_FLY0, freq=2.0, damping=0.55) if t >= E_FLY0 else 0.0
    if lp > 0:
        op = K.ramp(t, E_FLY0, E_FLY0 + 0.15)
        mark_s = 0.7 + 0.3 * lp
        K.draw(cv, L['mark'], 540, LOGO_Y, scale=mark_s, opacity=op, blur=4 * (1 - min(lp, 1.0)))
        wp = K.ramp(t, E_FLY0 + 0.12, E_FLY0 + 0.55, 'out_expo')
        if wp > 0:
            _wipe_draw(cv, L['word'], 540, LOGO_Y, wp, scale=mark_s)
    # flying leaves (from the sprout's top leaves to the logo's inner leaves)
    land = t >= E_LAND
    E = _env()
    for key, feat, side in (('leafL', 'leaf_top_l', -1), ('leafR', 'leaf_top_r', 1)):
        tx, ty = logo_xy(540, LOGO_Y, L[key + '_c'])
        if t < E_FLY0:
            continue
        if not land:
            u = (t - E_FLY0) / (E_LAND - E_FLY0)
            fx, fy = sp.features[feat]
            piv = sp.pivot
            sx0 = 540 + (fx - piv[0]) * ss
            sy0 = E_SPROUT_Y + (fy - piv[1]) * ss
            e = ease('inout_cubic')(u)
            arc = math.sin(math.pi * e) * 170
            x = K.lerp(sx0, tx, e) + side * arc
            y = K.lerp(sy0, ty, e) - 0.4 * arc
            size = K.lerp(150.0, L[key + '_h'] * 1.15, e)
            spr = E['leaf'].at_time(0.53 + 1.2 * e * side, fps=30)
            K.draw(cv, spr, x, y, scale=size / 420.0, rot=side * (40 - 400 * e) * (1 - e) + side * 25 * e,
                   opacity=1.0 - 0.3 * K.ramp(u, 0.85, 1.0))
    if land:
        gl = K.impulse(t, E_LAND, decay=6.0)
        for key in ('leafL', 'leafR', 'leafF'):
            px, py = logo_xy(540, LOGO_Y, L[key + '_c'])
            K.draw(cv, L[key], 540, LOGO_Y, opacity=K.ramp(t, E_LAND, E_LAND + 0.06))
            if gl > 0.02:
                K.draw(cv, _hook_assets()['halo'], px, py, scale=0.9, opacity=0.6 * gl, mode='add')
    # light sweep across the settled logo
    lsw = K.ramp(t, B(37.5), B(39), 'inout_sine')
    if 0 < lsw < 1:
        _logo_sweep(cv, L, lsw)
    # tagline types on
    if t >= E_TYPE0:
        g = L['tagline']
        g.typewriter(cv, t, 540, TAGLINE_Y, t0=E_TYPE0, cps=40, caret=False)
    # CTA pill + contact
    cp = K.spring(t - E_CTA, freq=2.4, damping=0.5) if t >= E_CTA else 0.0
    if cp > 0:
        L['cta'].draw(cv, 540, CTA_Y + 40 * (1 - cp), scale=0.85 + 0.15 * cp, opacity=K.ramp(t, E_CTA, E_CTA + 0.1),
                      sweep=K.ramp(t, E_CTA + 0.5, E_CTA + 1.2, 'inout_sine') if E_CTA + 0.5 < t < E_CTA + 1.2 else None)
        co = K.ramp(t, E_CTA + 0.15, E_CTA + 0.6, 'out_expo')
        L['contact'].draw(cv, 540, CONTACT_Y + 24 * (1 - co), opacity=co, snap=False)
    return cv


@functools.lru_cache(maxsize=1)
def _top_leaf_cut():
    """Row mask for the sway sprout sprite: 0 above the top-leaf junction (y < 332), soft 10 px edge."""
    h = _hook_assets()['sway'].size[1]
    return np.clip((np.arange(h, dtype=np.float32) - 332.0) / 10.0, 0, 1)


@functools.lru_cache(maxsize=1)
def _logo_alpha():
    L = _logo()
    a = L['mark'][..., 3] + L['word'][..., 3] + L['leafL'][..., 3] + L['leafR'][..., 3] + L['leafF'][..., 3]
    return np.clip(a, 0, 1).astype(np.float32)


def _logo_sweep(cv, L, u):
    """Diagonal white light band across the logo (emissive, masked by the logo's alpha)."""
    a = _logo_alpha()
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = xx + 0.45 * yy - K.lerp(-200.0, w + 200.0, u)
    band = np.exp(-(d / 40.0) ** 2) * a * 0.38
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = band[..., None] * np.array([1.0, 0.95, 0.9], np.float32)
    K.draw(cv, spr, 540, LOGO_Y)


def _wipe_draw(cv, spr, x, y, u, scale=1.0):
    """Draw a sprite revealed left->right by a soft wipe (u 0..1)."""
    h, w = spr.shape[:2]
    xs = np.arange(w, dtype=np.float32)
    edge = u * (w + 80) - 40
    m = np.clip((edge - xs) / 40.0, 0, 1)
    tmp = spr * m[None, :, None]
    K.draw(cv, tmp, x, y, scale=scale)


# ---------------------------------------------------------------------------------------------- transitions
LEAF_WIPE = [  # (x0, y0, x1, y1, width px, frame, rot0, spin, delay)
    (1150, 2150, -260, -380, 980, 16, 30, -70, 0.00), (820, 2300, 120, -520, 760, 0, -20, 60, 0.04),
    (1300, 1500, -320, 260, 820, 20, 70, -40, 0.02), (300, 2250, 980, -300, 640, 40, 10, 50, 0.07),
    (1250, 900, -200, -420, 560, 4, 110, -80, 0.05), (-150, 1700, 700, -560, 700, 47, -60, 40, 0.09),
    (1180, 2400, 400, -600, 900, 26, 0, 30, 0.11)]


def draw_leaf_wipe(cv, t, tc, dur=0.62):
    """A gust of big near-lens leaves sweeping up across the frame, centred on the cut at tc."""
    E = _env()
    for (x0, y0, x1, y1, w, fr, r0, spin, dl) in LEAF_WIPE:
        u = (t - (tc - dur / 2) - dl) / dur
        if u <= 0 or u >= 1:
            continue
        e = ease('inout_sine')(u)
        x, y = K.lerp(x0, x1, e), K.lerp(y0, y1, e)
        spr = E['leaf'].at_time(fr / 30.0 + u * 0.5, fps=30)
        K.draw(cv, spr, x, y, scale=w / 600.0 * 1.6, rot=r0 + spin * u, blur=9.0)


def whip_shift(cv, dy):
    """Shift canvas content vertically by dy px (reflect at the borders) - the vertical whip."""
    import cv2
    M = np.float32([[1, 0, 0], [0, 1, dy]])
    cv[...] = cv2.warpAffine(cv, M, (cv.shape[1], cv.shape[0]), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REFLECT101)
    return cv


# =============================================================================================== contract
WIPE_HALF = 0.31


def draw(t):
    # growth -> NURTURE: leaf gust with a short dissolve hidden under it
    if t < T_NUR:
        cv = scene_hook(t)
        if t > T_NUR - 0.09:
            nv = scene_nurture(t)
            k = np.float32(K.ramp(t, T_NUR - 0.09, T_NUR + 0.05))
            cv += (nv - cv) * k
        if t > T_NUR - WIPE_HALF:
            draw_leaf_wipe(cv, t, T_NUR)
        return cv
    if t < T_DEV:
        if t > T_NUR + 0.05:
            cv = scene_nurture(t)
        else:
            cv = scene_nurture(t)
            hv = scene_hook(t)
            k = np.float32(K.ramp(t, T_NUR - 0.09, T_NUR + 0.05))
            cv = hv + (cv - hv) * k
        if t < T_NUR + WIPE_HALF:
            draw_leaf_wipe(cv, t, T_NUR)
        if t > T_DEV - 0.16:                       # vertical whip out (content flies up)
            a = ease('in_expo')(K.ramp(t, T_DEV - 0.16, T_DEV, 'linear'))
            whip_shift(cv, -1100 * a)
            K.whip_blur(cv, 260 * a, angle=90)
        return cv
    if t < T_GRO:
        cv = scene_develop(t)
        if t < T_DEV + 0.22:                       # ... whip in from below
            a = 1 - ease('out_expo')(K.ramp(t, T_DEV, T_DEV + 0.22, 'linear'))
            whip_shift(cv, 1100 * a)
            K.whip_blur(cv, 260 * a, angle=90)
        if t > T_GRO - 0.14:                       # push-through: DEVELOP flies past the lens
            a = ease('in_cubic')(K.ramp(t, T_GRO - 0.14, T_GRO, 'linear'))
            gv = scene_grow(t)
            _push(cv, gv, a)
        return cv
    if t < T_KIND:
        cv = scene_grow(t)
        if t > T_KIND - 0.30:
            base = scene_kinds(t)
            iris_to_heart(base, t, cv)
            cv = base
        return cv
    if t < T_END:
        cv = scene_kinds(t)
        if t < T_KIND + 0.07:
            iris_to_heart(cv, t, scene_grow(t))
        return cv
    return scene_end(t)


def _push(cv, nxt, a):
    """cv (outgoing) scales up past the lens and fades, revealing nxt (incoming, scaling up from 0.86)."""
    import cv2
    s_out = 1.0 + 1.6 * a
    s_in = 0.86 + 0.14 * a
    M_in = cv2.getRotationMatrix2D((K.CX, K.CY), 0, s_in)
    inn = cv2.warpAffine(nxt, M_in, (K.W, K.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    M_out = cv2.getRotationMatrix2D((K.CX, K.CY), 0, s_out)
    out = cv2.warpAffine(cv, M_out, (K.W, K.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    k = np.float32(ease('in_cubic')(a))
    cv[...] = out * (1 - k) + inn * k
    K.zoom_blur(cv, 0.15 * math.sin(math.pi * a))
    return cv


def footage_amount(t):
    """0..1: how much of the frame is bright full-bleed footage (for K.post(..., footage=))."""
    f = 0.0
    f = max(f, K.ramp(t, N_Z1 - 0.12, N_Z1, 'linear') * (1 - K.ramp(t, T_DEV, T_DEV + 0.1, 'linear')))
    f = max(f, K.ramp(t, G_Z1 - 0.12, G_Z1, 'linear') * (1 - K.ramp(t, T_KIND - 0.25, T_KIND, 'linear')))
    f = max(f, 0.45 * K.ramp(t, T_IMPACT, T_IMPACT + 0.2, 'linear') * (1 - K.ramp(t, T_GROW - 0.15, T_GROW, 'linear')))
    return f


def post(cv, t):
    fl = (0.10 * K.impulse(t, T_IMPACT, decay=12.0) + 0.17 * K.impulse(t, T_GROW, decay=10.0)
          + 0.10 * K.impulse(t, D_CLICK, decay=9.0) + 0.18 * K.impulse(t, T_KIND, decay=8.0)
          + 0.12 * K.impulse(t, T_TRUST, decay=8.0) + 0.07 * K.impulse(t, E_LAND, decay=8.0)
          + 0.12 * K.impulse(t, T_NUR, decay=12.0))
    whip = 1 - min(1.0, abs(t - T_DEV) / 0.2)
    zoom = max(0.0, 1 - min(abs(t - N_Z1), abs(t - G_Z1), abs(t - T_GRO)) / 0.18)
    kw = dict(chroma=0.9 + 6.0 * whip + 4.0 * zoom)
    if fl > 1e-3:
        kw['flash'] = fl
    fa = footage_amount(t)
    if fa > 1e-3:
        kw['footage'] = fa
    return K.post(cv, LOOK, t, **kw)


def samples(t):
    fast = [(0.0, T_IMPACT + 0.08, 5), (T_NUR - WIPE_HALF, T_NUR + WIPE_HALF, 5),
            (N_Z1 - 0.32, N_Z1 + 0.04, 7), (T_DEV - 0.17, T_DEV + 0.23, 7), (T_GRO - 0.15, T_GRO + 0.05, 5),
            (G_Z1 - 0.32, G_Z1 + 0.04, 7), (T_KIND - 0.31, T_KIND + 0.05, 5), (T_TRUST - 0.32, T_TRUST + 0.26, 5),
            (E_FLY0, E_LAND + 0.03, 5)]
    for a_, b_, n in fast:
        if a_ <= t <= b_:
            return n
    return 3


def prewarm():
    _env(), _type(), _hook_assets(), _hook_leaf_world(), _chap(), _scrim_full(), _kinds(), _k_leaf_world(), _logo()
    for t in (0.3, 1.0, 3.0):
        scene_hook(t)


def cues():
    """SFX cue sheet (audio.py catalog names; align='hit' puts each sound's designed hit on t). No music.
    Every structural hit sits on the 92 BPM grid (B(n)); montage flashes on triplet 8ths, chips on 16ths."""
    c = []

    def q(t, name, gain_db=0.0, pan=0.0, **kw):
        d = dict(t=round(float(t), 4), name=name, gain_db=gain_db, pan=pan)
        d.update(kw)
        c.append(d)
    # ---- HOOK: glowing seed falls, plips onto the ivory surface, ripple; iris burst montage
    q(0.03, 'shimmer', -12, 0.1, params=dict(dur=1.0))
    q(T_IMPACT, 'reverse_swell', -9, 0.0, params=dict(duration=0.6))
    q(T_IMPACT, 'seed_plip', 0.0)
    q(T_IMPACT, 'impact_soft', -4)
    q(T_IMPACT + 0.01, 'ripple', -4, params=dict(dur=2.4))
    q(T_IMPACT + 0.06, 'swish_small', -7, -0.1)
    for k in range(1, 6):
        q(T_IMPACT + k * FLASH, 'swish_small', -6, 0.35 * (-1) ** k, params=dict(direction=(-1) ** k))
        q(T_IMPACT + k * FLASH, 'ui_tick', -12, -0.2 * (-1) ** k, params=dict(pitch=0.9 + 0.05 * k))
    # ---- GROWTH: iris closes into the seed, the sprout grows, type completes
    q(T_GROW, 'reverse_swell', -9, params=dict(duration=0.35))
    q(T_GROW, 'impact_soft', -6)
    q(T_GROW + 0.01, 'sparkle', -9, 0.15)
    q(T_GROW, 'grow_swell', -2, align='start', params=dict(duration=2.6))
    q(2.95, 'leaf_rustle', -5, -0.25, params=dict(dur=1.4))
    q(3.95, 'leaf_rustle', -7, 0.3, params=dict(dur=1.2))
    q(B(4), 'swish_small', -10, 0.1)
    q(B(5), 'swish_small', -10, -0.1)
    # ---- NURTURE: leaf gust, word lands, pills, sweep; zoom through the U into the footage
    q(T_NUR, 'whoosh_fast', -3, -0.2, params=dict(direction=-1))
    q(T_NUR, 'leaf_rustle', -3, 0.2, params=dict(dur=1.0))
    q(T_NUR + 0.04, 'impact_soft', -7)
    q(T_NUR + 0.20, 'pop', -9, 0.0)
    q(T_NUR + 0.30, 'bubble_pop', -9, 0.1, params=dict(pitch=0.85))
    q(T_NUR + 0.40, 'swish_small', -11, -0.1)
    q(T_NUR + 0.62, 'shimmer', -13, 0.2, params=dict(dur=1.0))
    q(N_Z1, 'reverse_swell', -7, params=dict(duration=0.65))
    q(N_Z1, 'air_zoom', -1)
    q(N_Z1 + 0.12, 'glass_tap', -12, 0.0)
    # ---- DEVELOP: vertical whip, word glides up, chips on 16ths, puzzle click, label
    q(T_DEV, 'whip', -2, 0.0, params=dict(direction=-1))
    q(T_DEV + 0.05, 'impact_soft', -7)
    q(T_DEV + 0.20, 'pop', -9, 0.0)
    q(D_UP, 'swish_small', -8, 0.0)
    q(D_UP + 0.32, 'swish_small', -12, 0.1)
    for i in range(4):
        q(D_CHIPS + i * BEAT / 4, 'bubble_pop', -6, -0.45 + 0.3 * i, params=dict(pitch=0.95 + 0.08 * i))
    q(D_CLICK - 0.18, 'whoosh_fast', -10, 0.0)
    q(D_CLICK, 'puzzle_click', 0.0)
    q(D_CLICK + 0.02, 'sparkle', -9, 0.1)
    q(D_CLICK + 0.08, 'pop', -8, 0.0, params=dict(pitch=1.1))
    # ---- GROW: push-through, sprout, zoom through the O's counter into c16
    q(T_GRO, 'air_zoom', -4)
    q(T_GRO + 0.03, 'impact_soft', -6)
    q(T_GRO + 0.20, 'pop', -9, 0.0)
    q(T_GRO + 0.25, 'leaf_rustle', -9, 0.2, params=dict(dur=1.0))
    q(T_GRO + 0.62, 'shimmer', -13, -0.2, params=dict(dur=1.0))
    q(G_Z1, 'reverse_swell', -7, params=dict(duration=0.65))
    q(G_Z1, 'air_zoom', -1)
    q(G_Z1 + 0.10, 'leaf_rustle', -10, -0.3, params=dict(dur=1.2))
    q(G_Z1 + 0.12, 'glass_tap', -12, 0.0)
    # ---- KINDS OF CARE: iris into the heart, headline, six tag pops on 8ths, orbit
    q(T_KIND, 'reverse_swell', -8, params=dict(duration=0.32))
    q(T_KIND, 'pop', -2, 0.0, params=dict(pitch=0.75))
    q(T_KIND + 0.01, 'impact_soft', -6)
    q(T_KIND + 0.03, 'sparkle', -9, -0.1)
    q(B(23.5), 'swish_small', -9, 0.0)
    for i in range(6):
        q(TAG_T0 + i * BEAT / 2, 'pop', -7, (-0.4, 0.4, -0.2, 0.3, -0.35, 0.2)[i], params=dict(pitch=0.9 + 0.06 * i))
    q(B(28), 'whoosh_by', -14, 0.0, params=dict(dur=2.0, speed=20.0, dist=3.0, direction=1))
    q(T_TRUST - 0.05, 'whoosh_fast', -4, 0.2)
    # ---- TRUST: heart spin-morphs into the shield, three check pills
    q(T_TRUST, 'glass_tap', -4)
    q(T_TRUST + 0.02, 'impact_soft', -6)
    q(T_TRUST + 0.05, 'shimmer', -12, 0.0, params=dict(dur=0.9))
    for i, tt in enumerate(TRUST_T):
        q(tt, 'check_ding', -6, (-0.15, 0.0, 0.15)[i], params=dict(pitch=1.0 + 0.06 * i))
    # ---- END: sprout, leaves fly into the logo, sunset, tagline types, CTA
    q(T_END, 'whoosh_fast', -7, 0.0, params=dict(direction=1))
    q(T_END + 0.05, 'leaf_rustle', -6, 0.0, params=dict(dur=0.9))
    q(T_END + 0.06, 'bubble_pop', -10, 0.0, params=dict(pitch=0.8))
    q(E_FLY0 + 0.25, 'swish_small', -8, -0.35, params=dict(direction=-1))
    q(E_FLY0 + 0.32, 'swish_small', -8, 0.35)
    q(E_LAND, 'riser', -10, params=dict(duration=0.65))
    q(E_LAND, 'logo_sting', 0.0)
    q(E_LAND + 0.02, 'sparkle', -7, 0.1)
    q(E_TYPE0, 'typing', -11, 0.0, align='start', params=dict(n=20, cps=36.0))
    q(E_CTA, 'pop', -5, 0.0, params=dict(pitch=1.05))
    q(E_CTA + 0.02, 'glass_tap', -9, 0.0)
    q(E_CTA + 0.25, 'swish_small', -12, 0.0)
    q(E_CTA + 0.55, 'shimmer', -14, 0.0, params=dict(dur=0.9))
    return c
