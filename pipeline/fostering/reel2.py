"""reel2.py: REEL 2 of 3, "FINANCIAL SUPPORT" (allowance). Look AMBER DASHBOARD. 1080x1920, 30 fps, 24.0 s.

128 BPM cut grid: B(n) = n * 0.46875 s. Every cut, slam and click lands on a beat or an 8th (half beat).
SFX only (no music): cues() uses audio.py catalog names (align='hit' unless noted), BED room_tone at -30 dB.
Mix: workspace3/audio/reel2_sfx.wav + reel2_sfx_stem.wav (48 kHz 24-bit, -18 LUFS, <= -1.5 dBTP).

SHOT LIST (t in s; B = beat)
 A1 0.000-0.469  B0-B1    COIN. A gold GBP coin (coin_gbp night_spin) flips toward the lens; its spin decelerates
                          so the face lands as it fills the frame (z 300 -> -1180, in_cubic). Amber halo ring, warm
                          glow, 6 far defocused tumbling coins, near bokeh, gold dust. Zoom blur builds, white flash
                          on B1. SFX coin_flip 0.03, whoosh_fast + reverse_swell + flash_hit + impact_soft on B1.
 A2 0.469-1.406  B1-B3    CARD TUNNEL. 18 glass footage cards (stills: c12 3.0, c04 1.4, c09 3.4, c14 10.6, c05 3.0,
                          c13 6.5, c01 4.5, c10 17.5, c15 4.0) on a golden-angle helix emerge from amber fog and rush
                          past the lens; camera surges +z (5600 -> 7300 u/s, eased) rolling 26 deg/s. Slot reels
                          "GBP ###.##" spin as gold streaks at the vanishing point (blur_cap 0.42: never a legible fake
                          amount) and fly through the lens on B2.5-B3 (in_expo). Flash + chroma pulse on every 8th.
                          SFX whoosh_by on B1.5/B2/B2.5 (panned L/R), slot_tick (start 0.52), reverse_swell -> B3.
 A3 1.406-2.344  B3-B5    TITLE. Gold extruded "Financial" slams on B3, "Support" on B3.5 (spring 1.65 -> 1, shake),
                          "for foster carers" rises on B4; light sweep 1.80-2.38. The tunnel brakes (exp) and keeps
                          drifting far behind (dimmed, DOF); dark radial scrim behind the copy. Exit: zoom-through the
                          title + flash on B5. SFX impact_big + sub_drop B3, impact_soft B3.5, shimmer, swish B4,
                          air_zoom B5.
 B  2.344-5.156  B5-B11   THE NUMBER. Gold odometer GBP 0 -> 447.60 (2.39 -> B8, out_expo, per-digit blur), "/ week
                          per child" on B6, glass pill "Ages 0-4" pops on B9. 9 spinning 3D coins orbit the copy on a
                          tilted glowing ellipse (rx 800, rz 740, tilt 54) with a comet head; the ellipse encloses the
                          copy with >= 68 px clearance (front coins pass under, back coins over; _check_coin_ring).
                          Cam.orbit push-in 1700 -> 1460, yaw 7 -> -4 (easy ease). Exit: whip pan on B11.
                          SFX slot_tick (start 2.39), cash_kaching + coin_ring B8, pop B9, whip B11.
 C  5.156-12.656 B11-B27  ALLOWANCE CALCULATOR. Perspective glass app window "Allowance calculator" / "Weekly allowance
                          per child". Whip-in to an isometric close-up (orbit yaw 24, pitch 14) that eases to front by
                          B16. Hand cursor clicks chips 0-4, 5-10, 11-14, 15+ on B12..B15: each glossy 3D bar grows
                          (out_back) to 447.60 / 473.17 / 515.52 / 554.02 and glows while active, values count up;
                          back to 0-4 on B16. Camera pulls back to the hold framing by B17.5; the cursor drags "Weeks of
                          care" 1 -> 52 (B17.5 -> B20) while the gold total above rolls 447.60 x weeks and lands on
                          GBP 23,275.20 on B20; caption "Estimated allowance . 52 weeks . one child aged 0-4"; fine
                          print in the window (32 px, two lines, ~30 px on screen). Hold with slow push, rack focus
                          total -> window, glints on B24. Exit: a big coin wipes across the lens on B27.
                          SFX glass_tap, ui_click + bar_grow on B12..B15, click B16, slider_drag (start B17.5),
                          cash_kaching + coins_burst B20, shimmer, coin_flip + whoosh_by B27.
 D  12.656-17.344 B27-B37 SUPPORT ORBIT. Glossy 3D house (house night) rises; headline "Plus support around / your
                          household" (B27.5 / B28); amber grid floor. Tilted elliptical ring of 5 two-line glass tags
                          (icons): the ring indexes 72 deg on each beat so every tag pops in at the FRONT on B28..B32
                          (Supervising social worker, Ongoing training, Advice outside normal hours, Foster carer
                          community, Education & health help), then drifts; back half dim + blurred (+DOF). Tags stay
                          inside x 70..1010 and y <= 1480 with no tag overlaps (_check_orbit). Orbit cam yaw 10 -> -8.
                          Exit: push into the glowing heart door, zoom-through on B37. SFX impact_soft, pops on
                          B28..B32, riser + air_zoom -> B37.
 E  17.344-20.156 B37-B43 HEART BEAT. Full-bleed c12 (src 3.4 s, centre 0.62/0.44, ramp 0.85 -> 0.36x slow-mo), golden
                          density grade, bottom scrim, bokeh + dust in front. "Recognition" (150 px) rises on B38, "for
                          a skilled role." (92 px) on B39, light sweep B39.6-B41.3. Exit: light-leak flash wipe on B43.
                          SFX heartbeat x2, swishes, shimmer, reverse_swell -> B43.
 F  20.156-24.000 B43-end END CARD. A coin is tossed up spinning; edge-on on B44 it becomes the 3D logo mark
                          (logo_mark3d night_anim swing-in, then a slow float) with a flash and a halo burst. Wordmark
                          (logo_full_onDark crop) B45, "NURTURE . DEVELOP . GROW" B45.5, pill CTA "Discuss your
                          estimate ->" B46, "0161 241 1332 . organicfostering.co.uk" B46.5, disclaimer B47; the cursor
                          clicks the CTA on B48 (22.5) and leaves; every element settled from 22.33: hold 1.67 s.
                          SFX flash_hit, coin_flip, logo_sting hit B44, sparkle, pop B46, ui_click B48.

Render-module contract: DUR, LOOK, BPM, draw(t) (pure), post(cv, t), samples(t), cues(), prewarm(); BED.
samples(t): 3 normally; 5-7 on the coin fly-in, tunnel, slams, zoom-throughs, the B11 whip, the B27 coin wipe,
the ring indexing, the door push and the coin toss (mean 3.67 per frame).
Measured (1 core, worker caches FOSTER_S3_CACHE_MB=448 FOSTER_TYPE_CACHE_MB=256): hook 3.5 s/frame (5-7 samples),
orbit 1.5 s (3) / 2.7 s (5); preview mean 0.82 s/frame (1 sample); worker peak RSS 1.7-2.2 GB.
Final master: cd pipeline/fostering && FOSTER_NICE=10 python3 render.py reel2 --workers 4
Dev helpers: reel2_dev.py (labelled still strips), _check_coin_ring(), _check_orbit().
Toolkit workarounds (kept local): ui.glass_card(shadow=0) crashes (built with a shadow, skipped at draw time);
ui.button glow clipped at its sprite bounds (_feather()).
"""
import functools
import math

import numpy as np

import core as K

DUR = 24.0
LOOK = 'amber'
BPM = 128
BEAT = 60.0 / BPM
BED = 'room_tone'
BED_GAIN_DB = -30.0


def B(n):
    """Time of beat n on the 128 BPM grid."""
    return n * BEAT


T_TUN, T_TITLE, T_NUM, T_CALC, T_ORB, T_HEART, T_END = B(1), B(3), B(5), B(11), B(27), B(37), B(43)

VALS = (447.60, 473.17, 515.52, 554.02)
AGES = ('0–4', '5–10', '11–14', '15+')
TOTAL = 23275.20                       # 447.60 x 52
FINE = 'Rates may vary by region and are subject to change.'


def _lazy():
    import footage as F
    import sprites3d as S3
    import type3d as T
    import ui
    return F, S3, T, ui


def unproject(cam, sx, sy, depth):
    pc = np.array([(sx - K.CX) * depth / cam.focal, (sy - K.CY) * depth / cam.focal, depth])
    return cam.R @ pc + cam.pos


def _ss(e0, e1, x):
    return K.smoothstep(e0, e1, x)


def _hot(cv, a):
    """Transition flash as HOT EXPOSURE (call before K.post): light is multiplied, so blacks stay black and the
    post's warm bloom turns the pushed highlights into a hot amber bloom. Replaces core.post(flash=...), whose
    additive ivory term lifted the blacks into a grey-lavender veil (QA: YMIN 15 -> 29..53 on clicks).
    UI clicks / pops / landings never call this: they get local glows at the interaction point."""
    if a > 1e-3:
        cv[..., :3] *= np.float32(1.0 + 3.0 * a)
    return cv


# ================================================================================================ A. HOOK
TUN_CARDS = [('c12', 3.0, (0.60, 0.42)), ('c04', 1.4, (0.47, 0.38)), ('c09', 3.4, (0.45, 0.42)),
             ('c14', 10.6, (0.38, 0.40)), ('c05', 3.0, (0.55, 0.40)), ('c13', 6.5, (0.66, 0.42)),
             ('c01', 4.5, (0.45, 0.42)), ('c10', 17.5, (0.53, 0.42)), ('c15', 4.0, (0.42, 0.42))]
CARD_W, CARD_H = 480, 624
N_TUN = 18
TUN_V0, TUN_DECAY, TUN_BRAKE = 6600.0, 6.0, 1.22


@functools.lru_cache(maxsize=1)
def _hook_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['coin'] = S3.get('coin_gbp', 'night', mode='spin')
    d['coin_s'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.3)
    d['halo'] = K.glow(K.ring(250, 5, K.C['AMBER'] * 2.4), K.C['ORANGE'], (10, 34, 90), 1.4)
    d['warm'] = K.radial(512, K.C['ORANGE'] * 0.55, power=2.4)
    d['scrim'] = K.radial(512, (0.0, 0.0, 0.0), power=1.3)
    d['bokeh'] = K.glow(K.disc(56, K.C['AMBER'] * 0.9), K.C['ORANGE'], (18, 50), 0.6)
    d['dust'] = K.Particles(180, seed=21, bright=1.0, size=(1.2, 4.2),
                            colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']])
    # NB ui.glass_card(shadow=0) crashes (Panel spad int, toolkit bug): build with a shadow, skip it at draw time
    card = ui.glass_card(CARD_W, CARD_H, r=34, look='amber', rim=1.2, glow=0.8)
    faces = []
    for cid, ts, ctr in TUN_CARDS:
        m = F.Clip(cid).get(ts, CARD_W, CARD_H, center=ctr, look='amber')
        faces.append(ui.media_face(card, m))
    d['card'] = card
    d['faces'] = faces
    d['fin'] = T.render('Financial', 'gold', px=190)
    d['sup'] = T.render('Support', 'gold', px=190)
    d['for'] = T.render('for foster carers', 'flat', px=66, fill='IVORY', glow=0.6, glow_color=('ORANGE', 2.4),
                        glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3))
    d['slot'] = T.Counter('gold', px=170, blur_cap=0.42)       # spinning reels = streaks, never fake amounts
    return d


def _tun_z(t):
    """Camera z through the tunnel: a rush that surges mid-way (v = v0 (1 + 0.3 sin), eased, never linear),
    then an exponential brake into the title."""
    if t <= T_TUN:
        return -1500.0
    L = TUN_BRAKE - T_TUN
    a = min(t, TUN_BRAKE) - T_TUN
    z = -1500.0 + TUN_V0 * (a + 0.3 * L / math.pi * (1 - math.cos(math.pi * a / L)))
    if t > TUN_BRAKE:
        z += TUN_V0 / TUN_DECAY * (1 - math.exp(-TUN_DECAY * (t - TUN_BRAKE)))
    return z


@functools.lru_cache(maxsize=1)
def _tun_layout():
    out = []
    for k in range(N_TUN):
        th = math.radians(-58.0 + 137.5 * k)
        r = (600.0 if k % 2 else 820.0) + 80.0 * ((k * 7) % 3)
        z = 900.0 + 560.0 * k
        x, y = r * math.cos(th), r * math.sin(th) * 1.15
        rx = -26.0 * math.sin(th)
        ry = 26.0 * math.cos(th)
        rz = ((k * 37) % 21 - 10) * 1.2
        out.append((k % len(TUN_CARDS), np.array([x, y, z]), (rx, ry, rz)))
    return out


def _tun_cam(t):
    z = _tun_z(t)
    roll = 34.0 * K.EASE['out_cubic'](K.clamp((t - T_TUN) / (T_NUM - T_TUN)))      # eased barrel roll
    slam = K.impulse(t, T_TITLE, decay=8.0) + 0.7 * K.impulse(t, B(3.5), decay=8.0)
    sx, sy, sr = K.shake(t, 9.0 * slam, 15.0, seed=4)
    return K.Cam(pos=(sx + K.wiggle(t, 0.6, 14, seed=1), sy + K.wiggle(t, 0.5, 10, seed=2), z),
                 yaw=K.wiggle(t, 0.4, 1.2, seed=3), roll=roll + sr, aperture=26 if t < T_TITLE else 34,
                 focus_dist=2600.0 if t < T_TITLE else 1500.0)


def _draw_cards(sc, A, t, title):
    card = A['card']
    cam = sc.cam
    for k, (fi, P, rot) in enumerate(_tun_layout()):
        d = cam.depth(P)
        if d < 40 or d > 7800:
            continue
        op = _ss(7800.0, 5600.0, d)
        if title:
            op *= _ss(2000.0, 2900.0, d) * 0.45
        if op <= 0.01:
            continue
        rot2 = (rot[0], rot[1], rot[2] + 8.0 * math.sin(0.9 * t + k))
        face = A['faces'][fi]
        sc.custom(P, lambda c, cm, face=face, P=P, rot2=rot2, op=op: card.plane(
            c, cm, P, 520.0, rot2, opacity=op, face=face, frost=0.0, shadow=0.0, dof_scale=1.4))


def _scene_coin(t):
    A = _hook_assets()
    u = K.clamp(t / T_TUN)
    cam = K.Cam(pos=(K.wiggle(t, 0.7, 5, seed=5), K.wiggle(t, 0.6, 4, seed=6), -1500.0),
                roll=K.lerp(3.0, -1.5, u), aperture=24, focus_dist=1500.0 + K.lerp(420.0, 0.0, u))
    cv = K.background('amber', t, cam, boost=0.35 + 0.5 * u, center=(0.5, 0.42), rim=0)
    sc = K.Scene(cam)
    e = 0.35 * u + 0.65 * K.EASE['in_cubic'](u)              # steady approach that explodes at the end
    z = K.lerp(420.0, -1180.0, e)
    pos = (K.lerp(30.0, 0.0, u), K.lerp(40.0, 0.0, u) - 18.0 * math.sin(math.pi * u), z)
    ang = 720.0 * (1.0 - u) ** 1.6
    W = 700.0
    sc.billboard(A['warm'], (pos[0], pos[1], z + 420.0), W * 2.4, mode='add', opacity=0.9)
    sc.billboard(A['halo'], (pos[0], pos[1], z + 60.0), W * 1.25, mode='add', opacity=0.75 * (1 - 0.6 * u),
                 rot=t * 40.0)
    sc.billboard(A['coin'].at_yaw(ang), pos, W, rot=K.lerp(-16.0, 0.0, K.EASE['out_cubic'](u)))
    # far defocused coins (depth layer behind), each tumbling
    for i in range(6):
        th = i * 1.047 + 0.4
        P = (math.cos(th) * 900.0, math.sin(th) * 1300.0, 3200.0 + 500.0 * (i % 3))
        sc.billboard(A['coin_s'].at_yaw((t * 300.0 + i * 70.0) % 360.0), P, 260.0, rot=i * 25.0, opacity=0.8)
    sc.billboard(A['bokeh'], (-560.0, 700.0, -900.0), 240.0, mode='add', opacity=0.5)
    sc.billboard(A['bokeh'], (520.0, -760.0, -1000.0), 200.0, mode='add', opacity=0.4)
    sc.particles(A['dust'], t)
    sc.render(cv)
    return cv


def _scene_tunnel(t):
    A = _hook_assets()
    cam = _tun_cam(t)
    title = t >= T_TITLE
    ti = K.ramp(t, T_TITLE - 0.1, T_TITLE + 0.3)
    cv = K.background('amber', t, cam, boost=0.25 * (1 - ti) + 0.25 * K.beat_pulse(t, BPM * 2, decay=8.0),
                      center=(K.lerp(0.5, 0.3, ti), K.lerp(0.45, 0.22, ti)), rim=0, parallax=0.35,
                      intensity=K.lerp(0.8, 0.55, ti))
    sc = K.Scene(cam)
    _draw_cards(sc, A, t, title)
    # slot reels at the vanishing point, then through the lens
    if t < T_TITLE + 0.02:
        fly = K.ramp(t, B(2.5), T_TITLE, 'in_expo')
        dep = K.lerp(1600.0, 110.0, fly)
        ts = A['slot'].slot_sprite(t, 447.60, t0=T_TUN - 0.05, dur=2.6, stagger=0.05, spins=12)
        spr = ts.sprite
        P = cam.pos + cam.forward * dep
        Pb = cam.pos + cam.forward * (dep + 60.0)
        op = K.ramp(t, T_TUN, T_TUN + 0.12) * (1 - K.ramp(t, T_TITLE - 0.06, T_TITLE + 0.02))
        sw = spr.shape[1] * 1.15 * (1 + 0.15 * fly)
        sc.custom(Pb, lambda c, cm: K.draw_billboard(c, A['scrim'], cm, Pb, sw * 1.5, opacity=0.85 * op, dof=False))
        sc.custom(Pb, lambda c, cm: K.draw_billboard(c, A['warm'], cm, Pb, sw * 1.6, mode='add', opacity=0.5 * op,
                                                     dof=False))
        sc.custom(P, lambda c, cm: K.draw_billboard(c, spr, cm, P, sw, opacity=op, dof=False, blur=10.0 * fly))
    sc.particles(A['dust'], t)
    sc.render(cv)
    if title:
        _draw_title(cv, t, A)
    return cv


TITLE_Y = (850.0, 1040.0, 1186.0)


def _draw_title(cv, t, A):
    ex = K.ramp(t, T_NUM - 0.17, T_NUM, 'in_expo')               # zoom-through exit
    zs = 1.0 + 1.8 * ex
    op_all = 1.0 - K.ramp(t, T_NUM - 0.07, T_NUM)
    slam = K.impulse(t, T_TITLE, decay=8.0) + 0.7 * K.impulse(t, B(3.5), decay=8.0)
    dx, dy, _ = K.shake(t, 7.0 * slam, 17.0, seed=9)
    # dark soft scrim behind the copy (legibility over the far cards)
    K.draw(cv, A['scrim'], 540, 1010, scale=(2.6, 1.9), opacity=0.8 * K.ramp(t, T_TITLE - 0.05, T_TITLE + 0.1) *
           op_all)
    cy0 = 1000.0
    for key, t0, y in (('fin', T_TITLE, TITLE_Y[0]), ('sup', B(3.5), TITLE_Y[1])):
        if t < t0:
            continue
        sp = K.spring(t - t0, freq=2.6, damping=0.45)
        s = K.lerp(1.65, 1.0, sp) * zs
        op = K.ramp(t, t0, t0 + 0.045) * op_all
        sw = K.ramp(t, 1.80 + (0.08 if key == 'sup' else 0.0), 2.30 + (0.08 if key == 'sup' else 0.0), 'inout_sine')
        yy = cy0 + (y - cy0) * zs + dy
        A[key].draw(cv, 540 + dx, yy, scale=s, opacity=op, blur=6.0 * ex, snap=False,
                    sweep=sw if 0 < sw < 1 else None, sweep_kw=dict(width=0.12, strength=1.5))
    if t >= B(4) - 0.1:
        r = K.ramp(t, B(4) - 0.05, B(4) + 0.45, 'out_expo')
        yy = cy0 + (TITLE_Y[2] - cy0) * zs + 36.0 * (1 - r) + dy
        A['for'].draw(cv, 540 + dx, yy, scale=zs, opacity=K.ramp(t, B(4) - 0.05, B(4) + 0.2) * op_all,
                      blur=8.0 * (1 - r) + 6.0 * ex, snap=False)


def _post_hook(cv, t):
    fl = 0.0
    ch = 1.6
    if t < T_TUN + 0.1:
        z = K.ramp(t, 0.30, T_TUN, 'in_cubic')
        if z > 0.01 and t < T_TUN:
            K.zoom_blur(cv, 0.10 * z)
        fl += 0.9 * K.ramp(t, T_TUN - 0.07, T_TUN, 'in_expo') * (t < T_TUN) + 0.9 * K.impulse(t, T_TUN, 9.0)
    if T_TUN <= t < T_TITLE + 0.3:
        # flash + chroma pulse on every 8th through the tunnel
        p = sum(K.impulse(t, T_TUN + B(0.5) * k, decay=14.0) for k in range(1, 4))
        fl += 0.10 * p
        ch += 4.0 + 6.0 * p * (t < T_TITLE)
        if B(2.5) < t < T_TITLE:
            K.zoom_blur(cv, 0.06 * K.ramp(t, B(2.5), T_TITLE, 'in_expo'))
    fl += 0.45 * K.impulse(t, T_TITLE, decay=10.0) + 0.25 * K.impulse(t, B(3.5), decay=10.0)
    if t > T_NUM - 0.2:
        z = K.ramp(t, T_NUM - 0.2, T_NUM, 'in_expo')
        K.zoom_blur(cv, 0.12 * z)
        fl += 0.8 * K.ramp(t, T_NUM - 0.08, T_NUM, 'in_expo')
    foot = 0.5 if T_TUN <= t < T_TITLE else 0.0
    _hot(cv, fl)
    return K.post(cv, LOOK, t, chroma=ch, footage=foot)


# ================================================================================================ B. THE NUMBER
NUM_ROLL = (T_NUM + 0.05, B(8))
NUM_Y = (-80.0, 82.0, 202.0)                    # world y of counter / caption / chip (camera target y = 40)
COIN_RING = dict(center=(0.0, 20.0, 0.0), rx=800.0, rz=740.0, tilt=54.0, roll=0.0, n=9, size=215.0, speed=0.085)


@functools.lru_cache(maxsize=1)
def _num_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['cnt'] = T.Counter('gold', px=210)
    d['per'] = T.render('/ week per child', 'flat', px=64, fill='IVORY', glow=0.5, glow_color=('ORANGE', 2.0),
                        glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3))
    d['chip'] = T.render('Ages 0–4', 'glass_pill', px=52, pill_tint=('ORANGE', 1.5), pill_tint_amount=0.5)
    d['coin'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.45)
    d['coin_big'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.6)
    d['warm'] = K.radial(512, K.C['ORANGE'] * 0.5, power=2.2)
    d['dust'] = K.Particles(160, seed=31, bright=0.9, colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']])
    return d


def _num_trk():
    return K.Track([(NUM_ROLL[0], 0.0, 'out_expo'), (NUM_ROLL[1], VALS[0])])


def _num_whip(t):
    """Signed whip (-1..1) around the B -> C cut (camera yaw swing)."""
    a = K.ramp(t, T_CALC - 0.16, T_CALC, 'in_expo')
    b = 1.0 - K.ramp(t, T_CALC, T_CALC + 0.26, 'out_expo')
    return a if t < T_CALC else -b


def _num_cam(t):
    e = K.EASE['easy_ease'](K.clamp((t - T_NUM) / (T_CALC - T_NUM)))
    land = K.impulse(t, NUM_ROLL[1], decay=7.0)
    sx, sy, sr = K.shake(t, 6.0 * land, 14.0, seed=12)
    w = _num_whip(t) if t < T_CALC else 0.0
    return K.Cam.orbit((sx, 40.0 + sy, 0.0), K.lerp(1700.0, 1460.0, e), yaw=K.lerp(7.0, -4.0, e) + 34.0 * w,
                       pitch=K.lerp(3.0, 1.0, e) + K.wiggle(t, 0.3, 0.5, seed=13), roll=sr * 0.4, aperture=30)


def _ring_xyz(th, R):
    th = np.asarray(th, np.float64)
    x, z = R['rx'] * np.cos(th), R['rz'] * np.sin(th)
    tl = math.radians(R['tilt'])
    y = -z * math.sin(tl)
    z2 = z * math.cos(tl)
    rl = math.radians(R['roll'])
    xr, yr = x * math.cos(rl) - y * math.sin(rl), x * math.sin(rl) + y * math.cos(rl)
    c = R['center']
    return np.stack([c[0] + xr, c[1] + yr, c[2] + z2], -1), z


def _orbit_line(cv, cam, R, part, opacity, head, color=None, width=2.2):
    """Glowing elliptical orbit line (the 'back' or 'front' half) with a bright comet head at angle `head`."""
    import cv2
    a = np.linspace(0, 2 * math.pi, 361)
    P, z = _ring_xyz(a, R)
    xy, d = cam.project(P)
    ok = np.isfinite(xy).all(1)
    if ok.sum() < 8:
        return
    x0, y0 = np.nanmin(xy[ok], 0) - 50
    x1, y1 = np.nanmax(xy[ok], 0) + 50
    X0, Y0 = max(0, int(x0)), max(0, int(y0))
    X1, Y1 = min(K.W, int(x1)), min(K.H, int(y1))
    if X1 <= X0 + 4 or Y1 <= Y0 + 4:
        return
    m8 = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
    for i in range(0, 360, 4):
        zz = z[i:i + 5].mean()
        if (part == 'back') != (zz > 0):
            continue
        seg = xy[i:i + 5]
        if not np.isfinite(seg).all():
            continue
        dh = (a[i] - head) % (2 * math.pi)
        k = 0.28 + 0.72 * math.exp(-dh / 0.9) + 0.6 * math.exp(-(2 * math.pi - dh) / 0.08)
        k *= 0.55 if part == 'back' else 1.0
        pts = np.round((seg - (X0, Y0)) * 16).astype(np.int32)
        cv2.polylines(m8, [pts], False, int(min(255, 255 * k)), max(1, int(round(width))), cv2.LINE_AA, shift=4)
    m = m8.astype(np.float32) * np.float32(1 / 255.0)
    gl = K.gblur(m, 5.0, border='constant') * 1.1 + K.gblur(m, 16.0, border='constant') * 0.7
    c = K.C['AMBER'] if color is None else color
    cv[Y0:Y1, X0:X1, :3] += (m * 1.6 + gl)[..., None] * c * np.float32(opacity)


def _coin_ring_pos(t, i):
    R = COIN_RING
    n = R['n']
    tau = max(0.0, t - T_NUM)
    th = 2 * math.pi * (i / n + R['speed'] * tau + 0.10 * (1 - math.exp(-2.5 * tau)) + 0.11)   # surge, then cruise
    x, z = R['rx'] * math.cos(th), R['rz'] * math.sin(th)
    tl = math.radians(R['tilt'])
    y = -z * math.sin(tl)
    z2 = z * math.cos(tl)
    rl = math.radians(R['roll'])
    xr, yr = x * math.cos(rl) - y * math.sin(rl), x * math.sin(rl) + y * math.cos(rl)
    c = R['center']
    return np.array([c[0] + xr, c[1] + yr, c[2] + z2]), th


def _scene_number(t):
    A = _num_assets()
    cam = _num_cam(t)
    land = K.impulse(t, NUM_ROLL[1], decay=6.0)
    cv = K.background('amber', t, cam, boost=0.15 + 0.45 * land, center=(0.62, 0.3), rim=0.6, intensity=0.75)
    sc = K.Scene(cam)
    sc.billboard(A['warm'], (0.0, -40.0, 500.0), 1900.0, mode='add', opacity=0.55 + 0.4 * land)
    # counter (odometer roll, per-digit motion blur) + caption + chip, on the focus plane
    trk = _num_trk()
    val, vel = float(trk(t)), float(trk.vel(t))
    ts = A['cnt'].sprite(val, vel)
    pop = 1.0 + 0.05 * land
    sw = K.ramp(t, NUM_ROLL[1] + 0.12, NUM_ROLL[1] + 0.85, 'inout_sine')
    Pc = (0.0, NUM_Y[0], 0.0)
    op_c = K.ramp(t, T_NUM, T_NUM + 0.12)
    sc.custom(Pc, lambda c, cm: ts.draw_plane(c, cm, Pc, scale=pop, opacity=op_c, dof=False,
                                              sweep=sw if 0 < sw < 1 else None,
                                              sweep_kw=dict(width=0.12, strength=1.5)))
    r1 = K.ramp(t, B(6), B(6) + 0.6, 'out_expo')
    if r1 > 0:
        P1 = (0.0, NUM_Y[1] + 40.0 * (1 - r1), 0.0)
        sc.custom(P1, lambda c, cm: A['per'].draw_plane(c, cm, P1, opacity=K.ramp(t, B(6), B(6) + 0.2),
                                                        blur=8.0 * (1 - r1), dof=False))
    r2 = K.ramp(t, B(9), B(9) + 0.45, 'out_back')
    if r2 > 0:
        P2 = (0.0, NUM_Y[2], 0.0)
        sc.custom(P2, lambda c, cm: A['chip'].draw_plane(c, cm, P2, scale=0.7 + 0.3 * r2,
                                                         opacity=K.ramp(t, B(9), B(9) + 0.12), dof=False))
    # 3D coins orbiting the copy (tilted ellipse that encloses it; depth sorted, back ones defocus)
    for i in range(COIN_RING['n']):
        P, th = _coin_ring_pos(t, i)
        ent = K.ramp(t, T_NUM + 0.04 * i, T_NUM + 0.55 + 0.04 * i, 'out_cubic')
        if ent <= 0:
            continue
        Pe = P * np.array([1.0 + 1.6 * (1 - ent), 1.0, 1.0]) + np.array([0.0, 0.0, 2600.0 * (1 - ent)])
        spr = A['coin'].at_yaw((t * 160.0 + i * 51.0) % 360.0)
        sc.billboard(spr, tuple(Pe), COIN_RING['size'], rot=-14.0 + 10.0 * math.sin(th), opacity=min(1.0, ent * 2))
    # the orbit line itself: back half behind everything, front half in front of the copy plane
    lo = K.ramp(t, T_NUM + 0.1, T_NUM + 0.8)
    head = 2 * math.pi * (COIN_RING['speed'] * 2.2 * (t - T_NUM)) + 1.0
    sc.custom(2600.0, lambda c, cm: _orbit_line(c, cm, COIN_RING, 'back', 0.8 * lo, head))
    sc.custom(1.0, lambda c, cm: _orbit_line(c, cm, COIN_RING, 'front', 0.9 * lo, head))
    # near defocused coin (foreground depth layer), bottom-left corner
    Pn = (-700.0, 1050.0, -800.0)
    sc.billboard(A['coin_big'].at_yaw((t * 90.0) % 360.0), Pn, 420.0, rot=20.0, opacity=0.9)
    sc.particles(A['dust'], t)
    sc.render(cv)
    w = abs(_num_whip(t)) if t < T_CALC else 0.0
    if w > 1e-3:
        K.whip_blur(cv, 180.0 * w, angle=0.0)
    return cv


def _post_number(cv, t):
    fl = 0.9 * K.impulse(t, T_NUM, decay=9.0)                 # landing on B8: local glow only (scene)
    w = abs(_num_whip(t))
    _hot(cv, fl)
    return K.post(cv, LOOK, t, chroma=1.6 + 9.0 * w)


def _check_coin_ring(step=1.0 / 30):
    """Dev check: min screen gap (px) between orbiting coins and the copy over scene B (negative = overlap)."""
    A = _num_assets()
    worst = (1e9, None)
    for t in np.arange(T_NUM + 0.6, T_CALC - 0.2, step):
        cam = _num_cam(t)
        boxes = []
        for (P, ts, sc_) in (((0, NUM_Y[0], 0), A['cnt'].sprite(VALS[0]), 1.0), ((0, NUM_Y[1], 0), A['per'], 1.0),
                             ((0, NUM_Y[2], 0), A['chip'], 1.0)):
            xy, d = cam.project(np.array([P]))
            k = cam.focal / d[0]
            w_, h_ = ts.w * k, ts.h * k
            pad = 0.25 * h_ if ts is A['chip'] else 0.12 * h_
            boxes.append((xy[0][0] - w_ / 2 - pad, xy[0][1] - h_ / 2 - pad, xy[0][0] + w_ / 2 + pad,
                          xy[0][1] + h_ / 2 + pad))
        for i in range(COIN_RING['n']):
            P, th = _coin_ring_pos(t, i)
            xy, d = cam.project(np.array([P]))
            r = 0.40 * COIN_RING['size'] * cam.focal / d[0]
            cx, cy = xy[0]
            for (x0, y0, x1, y1) in boxes:
                dx = max(x0 - cx, 0, cx - x1)
                dy = max(y0 - cy, 0, cy - y1)
                gap = math.hypot(dx, dy) - r
                if gap < worst[0]:
                    worst = (gap, (round(t, 2), i, round(cx), round(cy)))
    return worst


# ================================================================================================ C. CALCULATOR
WIN_W, WIN_H = 860, 1040
WIN_C = (0.0, 24.0, 120.0)                     # world centre of the window (hold cam = default Cam)
CLICKS = (B(12), B(13), B(14), B(15), B(16))   # chip clicks: 0-4, 5-10, 11-14, 15+, back to 0-4
DRAG = (B(17.5), B(20))                        # weeks slider 1 -> 52 (total lands on B20)
TOT_P = (0.0, -642.0, 0.0)                     # total counter (screen y ~318 in the hold)
CAP_P = (0.0, -528.0, 0.0)                     # caption under it
SUB_Y, CHIP_Y, CHART_Y, CHART_H, SLIDER_Y, FINE_Y = 238, 272, 368, 316, 670, (966, 1006)
CHIP_PX = 36                                   # chip text px (34 x 0.93 on screen would be < 34)
SLIDER_KY = SLIDER_Y + 168                    # knob / track centre (ui.slider_knob y)


@functools.lru_cache(maxsize=1)
def _calc_assets():
    F, S3, T, ui = _lazy()
    d = {}
    win = ui.app_window(w=WIN_W, h=WIN_H, look='amber', header='Allowance calculator', sub=None,
                        icons=('home', 'pound', 'chart', 'calendar', 'settings'), active=1)
    x0, y0, sw, sh = win.meta['slot']
    base = win.face.copy()
    L = ui.LOOKS['amber']
    ui.put_text(base, win.pad + x0, win.pad + SUB_Y, 'Weekly allowance per child', 36, 'body', L.text2, 'ls')
    for k, line in enumerate(('Rates may vary by region', 'and are subject to change.')):
        ui.put_text(base, win.pad + x0, win.pad + FINE_Y[k], line, 32, 'body', L.text2, 'ls')
    d['win'] = ui.derive_panel(win, base, win.meta)
    d['x0'], d['sw'] = x0, sw
    xs, wsz = [], []
    cx = x0
    for lab in AGES:
        w_, h_ = ui.chip_size(lab, CHIP_PX)
        xs.append(cx + w_ / 2)
        wsz.append(w_)
        cx += w_ + 16
    d['chip_x'], d['chip_w'] = xs, wsz
    d['cnt'] = T.Counter('gold', px=150)
    d['cap'] = T.render('Estimated allowance · 52 weeks · one child aged 0–4', 'ui', px=34, fill='PEACH')
    d['coin'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.6)      # near coin + the B27 wipe (motion-blurred)
    d['coin_s'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.35)
    d['dust'] = K.Particles(150, seed=3, bright=0.85, colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']])
    d['warm'] = K.radial(512, K.C['ORANGE'] * 0.5, power=2.2)
    d['scrim'] = K.radial(512, (0.0, 0.0, 0.0), power=1.4)
    return d


def _chip_sel(i, t):
    ons = [(CLICKS[k], CLICKS[k + 1] if k + 1 < len(CLICKS) else 1e9) for k in range(len(CLICKS))
           if (k % 4) == i and not (k == 4 and i != 0)]
    s_ = 0.0
    for on, off in ons:
        s_ = max(s_, K.ramp(t, on, on + 0.22, 'out_cubic') * (1 - K.ramp(t, off, off + 0.16, 'out_cubic')))
    return s_


@functools.lru_cache(maxsize=1)
def _act_track():
    c = CLICKS
    return K.Track([(c[0], 0.0, 'hold'), (c[1], 0.0, 'out_cubic'), (c[1] + 0.2, 1.0, 'hold'), (c[2], 1.0, 'out_cubic'),
                    (c[2] + 0.2, 2.0, 'hold'), (c[3], 2.0, 'out_cubic'), (c[3] + 0.2, 3.0, 'hold'),
                    (c[4], 3.0, 'inout_cubic'), (c[4] + 0.28, 0.0)])


def _active(t):
    return float(_act_track()(t))


def _slider_v(t):
    return K.ramp(t, DRAG[0], DRAG[1], 'inout_sine')


def _weeks(t):
    return int(round(1 + 51 * _slider_v(t)))


def _calc_face(t):
    _, _, _, ui = _lazy()
    A = _calc_assets()
    win = A['win']
    x0, sw = A['x0'], A['sw']
    lt = K.ramp(t, DRAG[1] + 0.1, DRAG[1] + 1.1)
    if lt >= 1:
        lt = K.ramp(t, B(23), B(25), 'inout_sine')
    f = win.face_at(sweep=(0.15 + (t - T_CALC) * 0.22) % 1.0, light=lt)
    for i, lab in enumerate(AGES):
        sel = _chip_sel(i, t)
        c = ui.chip(lab, sel, look='amber', size=CHIP_PX, origin=(0.4, 0.55))
        win.put(f, c, A['chip_x'][i], CHIP_Y + 36, anchor=(0.5, 0.5))
    grow = [K.ramp(t, CLICKS[i], CLICKS[i] + 0.5, 'out_back') for i in range(4)]
    act = _active(t) if t >= CLICKS[0] else None
    bars = ui.bar_chart(VALS, AGES, grow=grow, active=act, w=sw, h=CHART_H, look='amber', depth=12,
                        label_size=36, value_size=34)
    win.put(f, bars, x0 - 32, CHART_Y - 32)
    v = _slider_v(t)
    wk = _weeks(t)
    sl = ui.slider(v, w=sw - 80, look='amber', label='%d week%s' % (wk, '' if wk == 1 else 's'),
                   ticks=[(0, '1'), (1, '52')])
    win.put(f, sl, x0, SLIDER_Y)
    ui.put_text(f, win.pad + x0 + sw / 2, win.pad + SLIDER_KY + 66, 'Weeks of care', 36, 'ui', ui.LOOKS['amber'].text,
                'ms')
    return f


def _calc_cam(t):
    keys = [(T_CALC, (-20.0, -10.0, 120.0, 1060.0, 24.0, 14.0, -2.5)),
            (CLICKS[4], (0.0, 30.0, 120.0, 1180.0, 5.0, 4.0, -0.5)),
            (DRAG[0], (0.0, 0.0, 0.0, 1500.0, 0.0, 0.0, 0.0)),
            (DRAG[1] + 0.3, (0.0, 0.0, 0.0, 1500.0, 0.0, 0.2, 0.0)),
            (T_ORB, (0.0, -8.0, 0.0, 1460.0, -1.6, 1.0, 0.3))]
    trk = K.Track(keys, ease=K.EASE['easy_ease'])
    tx, ty, tz, dist, yaw, pitch, roll = [float(v) for v in trk(t)]
    w = _num_whip(t)                                         # arrival half of the whip from scene B
    yaw += -34.0 * min(0.0, w) * -1.0 if w < 0 else 0.0
    land = K.impulse(t, DRAG[1], decay=7.0)
    sx, sy, sr = K.shake(t, 5.0 * land, 14.0, seed=21)
    focus = K.lerp(dist, dist + 120.0, K.ramp(t, DRAG[1] + 1.3, DRAG[1] + 2.2, 'inout_sine'))
    return K.Cam.orbit((tx + sx, ty + sy, tz), dist, yaw=yaw + K.wiggle(t, 0.25, 0.4, seed=22),
                       pitch=pitch + K.wiggle(t, 0.3, 0.3, seed=23), roll=roll + sr * 0.4,
                       aperture=K.lerp(22.0, 34.0, K.ramp(t, DRAG[1], DRAG[1] + 0.6)), focus_dist=focus)


def _cursor_xy(t):
    """Cursor target in card px + press amount + click time (for the ring)."""
    A = _calc_assets()
    # click hotspot at each chip's lower-right, so the hand hangs below the label instead of covering it
    cxs = [x_ + 0.30 * A['chip_w'][i] for i, x_ in enumerate(A['chip_x'])]
    cy_ = CHIP_Y + 62
    pts = [(T_CALC + 0.15, (WIN_W + 120.0, 900.0)), (CLICKS[0] - 0.06, (cxs[0], cy_))]
    for k in range(1, 5):
        i = k % 4
        pts.append((CLICKS[k - 1] + 0.12, (cxs[(k - 1) % 4], cy_)))
        pts.append((CLICKS[k] - 0.06, (cxs[i], cy_)))
    kx0 = A['x0'] + 40.0
    ky = float(SLIDER_KY)
    pts.append((CLICKS[4] + 0.12, (cxs[0], cy_)))
    pts.append((DRAG[0] - 0.05, (kx0 + 4, ky + 6)))
    pts.append((DRAG[0] + 0.05, (kx0 + 4, ky + 6)))
    pts.append((DRAG[1], (kx0 + (A['sw'] - 80) + 4, ky + 6)))
    pts.append((DRAG[1] + 0.25, (kx0 + (A['sw'] - 80) + 4, ky + 6)))
    pts.append((DRAG[1] + 0.9, (kx0 + (A['sw'] - 80) + 90, ky + 260)))
    keys = []
    for k, (tk, p_) in enumerate(pts):
        e = 'inout_cubic'
        if k + 1 < len(pts) and DRAG[0] + 0.04 < tk < DRAG[1] - 0.01:
            e = 'linear'
        keys.append((tk, p_, e))
    trk = K.Track(keys)
    xy = trk(t)
    if DRAG[0] <= t <= DRAG[1]:                    # glue to the knob while dragging
        xy = np.array([kx0 + _slider_v(t) * (A['sw'] - 80) + 4, ky + 6])
    press = 0.0
    click = None
    for c in CLICKS:
        press = max(press, K.impulse(t, c, decay=10.0, attack=0.04))
        if c <= t < c + 0.65:
            click = t - c
    press = max(press, K.ramp(t, DRAG[0] - 0.05, DRAG[0] + 0.05) * (1 - K.ramp(t, DRAG[1] + 0.1, DRAG[1] + 0.2)) * 0.8)
    if DRAG[0] - 0.05 <= t < DRAG[0] + 0.6:
        click = t - (DRAG[0] - 0.05)
    op = K.ramp(t, T_CALC + 0.15, T_CALC + 0.4) * (1 - K.ramp(t, DRAG[1] + 0.5, DRAG[1] + 0.9))
    return xy, press, click, op


def _calc_wipe(t):
    """Coin wipe across the C -> D cut: (x, y, width, angle, amount) or None."""
    u = K.ramp(t, T_ORB - 0.2, T_ORB + 0.2, 'inout_sine')
    if u <= 0 or u >= 1:
        return None
    x = K.lerp(-900.0, 1980.0, u)
    y = K.lerp(2500.0, -560.0, u)
    return x, y, 2100.0, (t * 900.0) % 360.0, u


def _draw_wipe(cv, t, A_coin):
    w = _calc_wipe(t)
    if w is None:
        return
    x, y, wd, ang, u = w
    spr = A_coin.at_yaw(ang)
    K.draw(cv, spr, x, y, scale=wd / spr.shape[1], rot=-35.0)


def _scene_calc(t):
    _, _, _, ui = _lazy()
    A = _calc_assets()
    cam = _calc_cam(t)
    land = K.impulse(t, DRAG[1], decay=6.0)
    cv = K.background('amber', t, cam, boost=0.15 + 0.15 * land, center=(0.28, 0.2), rim=0.0,
                      intensity=0.8)
    sc = K.Scene(cam)
    win = A['win']
    face = _calc_face(t)
    sc.billboard(A['warm'], (0.0, 300.0, 900.0), 2200.0, mode='add', opacity=0.5 + 0.3 * land)
    sc.custom(WIN_C, lambda c, cm: win.plane(c, cm, WIN_C, WIN_W, (0.0, 0.0, 0.0), face=face, shadow=0.8))
    # total counter + caption above the window (appear for the drag)
    tin = K.ramp(t, CLICKS[4] + 0.2, DRAG[0] - 0.05, 'out_expo')
    if tin > 0:
        wk = _weeks(t)
        val = VALS[0] * wk
        vel = VALS[0] * 51 * (_slider_v(min(t + 0.01, DRAG[1])) - _slider_v(t)) / 0.01 if t < DRAG[1] else 0.0
        ts = A['cnt'].sprite(val, vel)
        pop = 1.0 + 0.06 * land
        sw = K.ramp(t, DRAG[1] + 0.15, DRAG[1] + 1.0, 'inout_sine')
        if sw >= 1:
            sw = K.ramp(t, B(24), B(25.6), 'inout_sine')            # second glint on the hold
        Pt = (TOT_P[0], TOT_P[1] + 50.0 * (1 - tin), TOT_P[2])
        sc.custom(Pt, lambda c, cm: K.draw_billboard(c, A['scrim'], cm, Pt, 1500.0, opacity=0.35 * tin, dof=False))
        sc.custom(Pt, lambda c, cm: ts.draw_plane(c, cm, Pt, scale=pop, opacity=tin, blur=6.0 * (1 - tin),
                                                  sweep=sw if 0 < sw < 1 else None,
                                                  sweep_kw=dict(width=0.12, strength=1.6)))
        cr = K.ramp(t, DRAG[1] + 0.1, DRAG[1] + 0.6, 'out_expo')
        if cr > 0:
            Pc = (CAP_P[0], CAP_P[1] + 24.0 * (1 - cr), CAP_P[2])
            sc.custom(Pc, lambda c, cm: A['cap'].draw_plane(c, cm, Pc, opacity=cr, blur=5.0 * (1 - cr)))
    # depth layers: far coins at the frame edges, a near defocused coin at the bottom corner
    for i, (P, wd, sp) in enumerate((((-760.0, -520.0, 1900.0), 300.0, 110.0), ((780.0, 380.0, 2100.0), 330.0, -90.0),
                                     ((-700.0, 1350.0, 900.0), 300.0, 70.0))):
        sc.billboard(A['coin_s'].at_yaw((t * sp + 40 * i) % 360.0), P, wd, rot=20.0 * i - 10.0, opacity=0.85)
    Pn = (250.0, 520.0, -560.0)
    sc.billboard(A['coin'].at_yaw((t * 70.0 + 200.0) % 360.0), Pn, 230.0, rot=-25.0, opacity=0.8)
    sc.particles(A['dust'], t)
    sc.render(cv)
    xy, press, click, op = _cursor_xy(t)
    if op > 0.01:
        sxy = win.screen(cam, WIN_C, WIN_W, (0.0, 0.0, 0.0), float(xy[0]), float(xy[1]), z=-40.0)
        ui.draw_cursor(cv, sxy[0], sxy[1], 'hand', 84, press=press, click=click, opacity=op, look='amber')
    _draw_wipe(cv, t, A['coin'])
    w = _num_whip(t)
    if w < -1e-3:
        K.whip_blur(cv, 180.0 * abs(w), angle=0.0)
    return cv


def _post_calc(cv, t):
    w = abs(_num_whip(t))
    wp = _calc_wipe(t)
    fl = 0.5 * K.impulse(t, T_CALC, decay=12.0) + (0.25 * math.sin(math.pi * wp[4]) ** 2 if wp else 0.0)
    ch = 1.6 + 9.0 * w + (6.0 * math.sin(math.pi * wp[4]) if wp else 0.0)
    _hot(cv, fl)
    return K.post(cv, LOOK, t, chroma=ch)


# ================================================================================================ D. SUPPORT ORBIT
TAGS = ((('Supervising', 'social worker'), 'user'), (('Ongoing', 'training'), 'graduation'),
        (('Advice outside', 'normal hours'), 'clock'), (('Foster carer', 'community'), 'users'),
        (('Education &', 'health help'), 'book'))
HOUSE_P = (0.0, -150.0, 0.0)
HOUSE_W = 470.0
DOOR_UV = (360.0 / 720.0, 470.0 / 720.0)       # heart on the door, in sprite uv (yaw 0)
# Tag ring: explicit slot angles (deg; -90 = front centre, +90 = back centre, hidden behind the house: unused).
# Back slots sit ABOVE the roof and front slots BELOW the house, so the parked ring shows all five tags readable.
RING = dict(center=(0.0, -150.0, 0.0), rx=205.0, rz=545.0, tilt=62.0, roll=0.0)
SLOTS = (-150.0, -30.0, -90.0, 30.0, 150.0)     # per TAGS entry: front-left, front-right, front-centre, back-R, back-L
ENTER_FROM = (50.0, -45.0, 0.0, 0.0, 0.0)      # ring-angle offset each front tag slides in from
ENTER_RISE = (0.0, 0.0, 40.0, 90.0, 90.0)       # world px a tag rises while popping (back tags rise out from
                                                # behind the roof: they are drawn before the house)
ORB_TGT = (0.0, 0.0, 0.0)
ORB_YAW = (7.0, -6.0)
ZOOM = (B(35.5), T_HEART)                      # push into the glowing door -> c12


def _tag2(lines, icon_name):
    _, _, _, ui = _lazy()
    L = ui.LOOKS['amber']
    tw = max(ui.measure(l, 34, 'ui') for l in lines)
    h = 128
    w = int(math.ceil((22 + 56 + 16 + tw + 26) / 4.0) * 4)
    base = ui.glass_card(w, h, r=40, look='amber', rim=0.7, glow=0.7, shadow=0.8)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    cx, cy = p + 22 + 28, p + h / 2
    a, X0, Y0 = S.rrect_grad(cx - 28, cy - 28, 56, 56, 28, L.grad[0], L.grad[1], 35, 1.0, 1.0)
    S.glow(a, X0, Y0, L.glow, (6, 16), 0.45, knock=0.9)
    S.sheen(cx - 27, cy - 27, 54, 54, 27, 0.12, 0.0, 0.6)
    S.paste(ui.icon(icon_name, 32, K.C['WHITE'], stroke=2.2), cx, cy, anchor=(0.5, 0.5))
    x = 22 + 56 + 16
    ui.put_text(f, p + x, p + 56, lines[0], 34, 'ui', L.text, 'ls')
    ui.put_text(f, p + x, p + 100, lines[1], 34, 'ui', L.text, 'ls')
    return ui.derive_panel(base, f)


@functools.lru_cache(maxsize=1)
def _orb_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['tags'] = [_tag2(l, ic) for l, ic in TAGS]
    d['house'] = S3.get('house', 'night')
    d['h1'] = T.render('Plus support around', 'flat', px=84, fill='IVORY', glow=0.5, glow_color=('ORANGE', 2.0),
                       glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3))
    d['h2'] = T.render('your household', 'gold', px=116)
    d['warm'] = K.radial(512, K.C['ORANGE'] * 0.6, power=2.0)
    d['door'] = K.radial(512, K.C['AMBER'] * 2.5, power=1.6)
    d['pop'] = K.radial(300, K.C['AMBER'] * 1.2, power=2.2)
    d['shadow'] = K.radial(400, K.C['NIGHT_0'] * 0.0, power=1.6)
    d['scrim'] = K.radial(512, (0.0, 0.0, 0.0), power=1.3)
    d['dust'] = K.Particles(170, seed=41, bright=0.9, colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']])
    d['coin'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.35)
    return d


def _orb_cam(t):
    """Orbit camera, then ONE continuous push into the door: the look-at target glides to the door heart and the
    orbit distance shrinks (in_expo starts with zero velocity, so there is no jump at ZOOM[0])."""
    e = K.EASE['easy_ease'](K.clamp((t - T_ORB) / (ZOOM[0] - T_ORB)))
    z = K.ramp(t, ZOOM[0], ZOOM[1], 'in_expo')
    s_ = K.ramp(t, ZOOM[0], ZOOM[1], 'inout_sine')
    d0 = K.lerp(1560.0, 1480.0, e)
    f0 = d0 + 40.0
    tgt = np.asarray(ORB_TGT, np.float64)
    if s_ > 0:
        tgt = tgt + (np.asarray(_door_world(t)) - tgt) * s_
    dist = K.lerp(d0, 110.0, z)
    return K.Cam.orbit(tuple(tgt), dist, yaw=K.lerp(ORB_YAW[0], ORB_YAW[1], e),
                       pitch=K.lerp(8.0, 5.0, e) + K.wiggle(t, 0.3, 0.35, seed=31), aperture=12.0 * (1 - z),
                       focus_dist=K.lerp(f0, dist, s_))


def _house_yaw(t):
    e = K.EASE['easy_ease'](K.clamp((t - T_ORB) / (ZOOM[0] - T_ORB)))
    return K.lerp(-16.0, 12.0, e) * (1 - K.ramp(t, ZOOM[0], ZOOM[0] + 0.5, 'inout_sine')) + 3.0 * math.sin(t * 1.3)


def _house_pos(t):
    rise = K.ramp(t, T_ORB, T_ORB + 0.5, 'out_back')
    return (HOUSE_P[0], HOUSE_P[1] + 220.0 * (1 - rise) + 8.0 * math.sin(t * 1.7), HOUSE_P[2])


def _door_world(t):
    P = _house_pos(t)
    return (P[0] + (DOOR_UV[0] - 0.5) * HOUSE_W, P[1] + (DOOR_UV[1] - 0.5) * HOUSE_W, P[2] - 30.0)


def _tag_state(k, t):
    """(enter 0..1, ring angle deg) of tag k: pops on B(28 + k), sliding into its slot along the ring; then the
    whole ring drifts a few degrees (eased) so the orbit keeps breathing."""
    t0 = B(28 + k) - 0.06
    en = K.ramp(t, t0, t0 + 0.42)
    sl = K.ramp(t, t0, t0 + 0.55, 'out_cubic')
    drift = 5.0 * K.EASE['inout_sine'](K.clamp((t - B(28)) / (ZOOM[0] - B(28)))) - 2.5
    return en, SLOTS[k] + ENTER_FROM[k] * (1 - sl) + drift


def _tag_world(k, t):
    en, ang = _tag_state(k, t)
    P, z = _ring_xyz(math.radians(ang), RING)
    P = np.asarray(P, np.float64).reshape(3).copy()
    P[1] += ENTER_RISE[k] * (1.0 - K.ramp(t, B(28 + k) - 0.06, B(28 + k) + 0.5, 'out_cubic'))
    return en, P, float(np.asarray(z).reshape(-1)[0])


def _scene_orbit(t):
    A = _orb_assets()
    cam = _orb_cam(t)
    z = K.ramp(t, ZOOM[0], ZOOM[1], 'in_expo')
    cv = K.background('amber', t, cam, boost=0.2 + 0.3 * K.impulse(t, T_ORB, 5.0), center=(0.5, 0.42),
                      rim=0.45, intensity=0.8)
    K.grid_floor(cv, cam, y=520.0, spacing=170.0, extent=4200.0, color=K.C['AMBER'], opacity=0.3 * (1 - z), width=1.3)
    sc = K.Scene(cam)
    hp = _house_pos(t)
    sc.billboard(A['warm'], (hp[0], hp[1] + 60.0, 600.0), 1800.0, mode='add', opacity=0.6)
    for i, P in enumerate(((-1150.0, -80.0, 2700.0), (1150.0, 40.0, 2900.0), (-950.0, 480.0, 3200.0),
                           (980.0, 560.0, 2600.0))):
        sc.billboard(A['coin'].at_yaw((t * 120.0 + 70.0 * i) % 360.0), P, 260.0, rot=15.0 * i, opacity=0.75)
    sc.particles(A['dust'], t)
    sc.render(cv)
    fade = 1.0 - K.ramp(t, ZOOM[0], ZOOM[0] + 0.45, 'in_cubic')
    head = math.radians(-90.0) + 2 * math.pi * 0.16 * (t - T_ORB)
    lo = K.ramp(t, T_ORB + 0.2, B(28), 'out_cubic') * fade
    tags = []
    for k in range(len(TAGS)):
        en, P, zz = _tag_world(k, t)
        if en > 0 and fade > 0.01:
            tags.append((cam.depth(P), k, en, P, zz))
    tags.sort(key=lambda r: -r[0])
    pn = A['tags']

    def draw_tag(c, k, en, P, zz):
        back = zz > 0
        s_ = 0.62 + 0.38 * K.EASE['out_back'](min(en, 1.0))
        op = min(1.0, en * 2.0) * fade * (0.92 if back else 1.0)
        pnl = pn[k]
        pnl.plane(c, cam, tuple(P), pnl.w * s_, (cam.pitch, cam.yaw, cam.roll), opacity=op, dof=True,
                  shadow=0.7 * (0.6 if back else 1.0))
        g = K.impulse(t, B(28 + k), decay=7.0)                     # pop: local glow at the tag, not a frame flash
        if g > 0.02:
            xy, d = cam.project(P[None, :])
            K.draw(c, A['pop'], xy[0][0], xy[0][1], scale=pnl.w * cam.focal / d[0] / 300.0, mode='add',
                   opacity=0.55 * g * fade)

    if lo > 0:
        _orbit_line(cv, cam, RING, 'back', 0.7 * lo, head)
    for (d, k, en, P, zz) in tags:
        if zz > 0:
            draw_tag(cv, k, en, P, zz)
    K.draw_billboard(cv, A['house'].at_yaw(_house_yaw(t)), cam, hp, HOUSE_W)
    gk = K.ramp(t, ZOOM[0], ZOOM[1], 'in_cubic')
    if gk > 0:
        K.draw_billboard(cv, A['door'], cam, _door_world(t), 200.0 * (1 + 2.5 * gk), mode='add', opacity=gk,
                         dof=False)
    if lo > 0:
        _orbit_line(cv, cam, RING, 'front', 0.9 * lo, head)
    for (d, k, en, P, zz) in tags:
        if zz <= 0:
            draw_tag(cv, k, en, P, zz)
    # headline (2D overlay, top safe zone)
    for key, t0, y in (('h1', B(27.5), 318.0), ('h2', B(28) + 0.05, 432.0)):
        r = K.ramp(t, t0, t0 + 0.55, 'out_expo')
        if r <= 0:
            continue
        op = K.ramp(t, t0, t0 + 0.2) * fade
        sw = K.ramp(t, B(30), B(31.5), 'inout_sine') if key == 'h2' else None
        A[key].draw(cv, 540, y + 40.0 * (1 - r), opacity=op, blur=8.0 * (1 - r), snap=False,
                    sweep=sw if sw is not None and 0 < sw < 1 else None, sweep_kw=dict(width=0.12, strength=1.4))
    if z > 0.05:
        K.zoom_blur(cv, 0.12 * z)
    _draw_wipe(cv, t, _calc_assets()['coin'])
    return cv


def _post_orbit(cv, t):
    z = K.ramp(t, ZOOM[1] - 0.12, ZOOM[1], 'in_expo')
    wp = _calc_wipe(t)
    ch = 1.6 + (6.0 * math.sin(math.pi * wp[4]) if wp else 0.0) + 6.0 * z
    fl = 0.25 * K.impulse(t, T_ORB, 9.0) + (0.25 * math.sin(math.pi * wp[4]) ** 2 if wp else 0.0) + 1.0 * z
    _hot(cv, fl)
    return K.post(cv, LOOK, t, chroma=ch)


# ================================================================================================ E. HEART BEAT
HEART_SRC0 = 3.4
HEART_CTR = (0.62, 0.44)
REC_T = (B(38), B(39))
REC_Y = (1296.0, 1438.0)


@functools.lru_cache(maxsize=1)
def _heart_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['clip'] = F.Clip('c12')
    d['ramp'] = F.SpeedRamp([(0.0, 0.85), (0.6, 0.36, 'inout_sine'), (3.2, 0.36)], src0=HEART_SRC0)
    d['rec'] = T.Glyphs('Recognition', 'flat', px=150, fill='IVORY', glow=0.6, glow_color=('ORANGE', 2.2),
                        glow_radii=(0.04, 0.14, 0.4), glow_weights=(0.8, 0.55, 0.35), scrim=0.55)
    d['role'] = T.Glyphs('for a skilled role.', 'flat', px=92, fill='PEACH', glow=0.5, glow_color=('ORANGE', 2.0),
                         glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3), scrim=0.5)
    hh = 1000
    yy = np.linspace(0.0, 1.0, hh, dtype=np.float32)[:, None]
    a = (np.clip((yy - 0.02) / 0.55, 0, 1) ** 1.1 * 0.88).astype(np.float32) * np.ones((1, K.W), np.float32)
    col = (K.C['NIGHT_0'] * 0.6 + K.C['PLUM'] * 0.05).astype(np.float32)
    d['scrim'] = np.dstack([a[..., None] * col, a]).astype(np.float32)
    d['dust'] = K.Particles(120, seed=51, bright=1.0, size=(1.4, 4.5),
                            colors=[K.C['AMBER'], K.C['PEACH'], K.C['ORANGE']])
    d['bokeh'] = K.glow(K.disc(60, K.C['AMBER'] * 0.8), K.C['ORANGE'], (20, 60), 0.6)
    return d


def _scene_heart(t):
    A = _heart_assets()
    u = t - T_HEART
    e = K.EASE['easy_ease'](K.clamp(u / (T_END - T_HEART)))
    zoom = K.lerp(1.0, 1.05, e)
    src = float(A['ramp'](u))
    cv = A['clip'].get(src, K.W, K.H, center=(HEART_CTR[0], HEART_CTR[1] - 0.01 * e), zoom=zoom, look='amber')
    # golden-hour density: pull the white wall down and warm it (the plate is very bright)
    rgb = cv[..., :3]
    rgb *= np.float32(0.80)
    rgb **= np.float32(1.12)
    rgb *= np.array([1.05, 0.97, 0.86], np.float32)
    K.draw(cv, A['scrim'], 540, 1920, anchor=(0.5, 1.0))
    cam = K.Cam(pos=(K.wiggle(t, 0.4, 20, seed=61), K.wiggle(t, 0.35, 16, seed=62), -1500.0), aperture=40)
    # foreground depth layer: warm defocused bokeh + dust drifting in front of the plate
    K.draw_billboard(cv, A['bokeh'], cam, (-520.0, -620.0, -800.0), 300.0, mode='add', opacity=0.45)
    K.draw_billboard(cv, A['bokeh'], cam, (560.0, 380.0, -900.0), 240.0, mode='add', opacity=0.35)
    A['dust'].draw(cv, cam, t, opacity=0.8)
    out = K.ramp(t, T_END - 0.3, T_END, 'in_cubic')
    sw = K.ramp(t, B(39.6), B(41.3), 'inout_sine')
    A['rec'].rise(cv, t, 540, REC_Y[0], t0=REC_T[0], stagger=0.03, dur=0.7, dist=0.45,
                  opacity=1 - out, sweep=sw if 0 < sw < 1 else None, sweep_kw=dict(width=0.12, strength=1.5))
    A['role'].rise(cv, t, 540, REC_Y[1], t0=REC_T[1], stagger=0.025, dur=0.6, dist=0.45, opacity=1 - out)
    return cv


def _post_heart(cv, t):
    lk = K.ramp(t, T_END - 0.35, T_END, 'in_cubic')
    if lk > 0:
        K.light_leak(cv, t, strength=1.2 * lk, seed=7, sweep=K.ramp(t, T_END - 0.35, T_END + 0.2, 'inout_sine'))
    fl = 0.65 * K.impulse(t, T_HEART, decay=11.0) + 0.9 * K.ramp(t, T_END - 0.1, T_END, 'in_expo')
    _hot(cv, fl)
    return K.post(cv, LOOK, t, footage=1.0, leak=0.12, leak_seed=3, vignette=0.55)


# ================================================================================================ F. END CARD
T_SWAP = B(44)                                 # coin edge-on -> logo mark
LOGO_XY, LOGO_S = (540.0, 560.0), 0.62
WM_Y, TAG_Y, BTN_Y, PH_Y, DIS_Y = 905.0, 1084.0, 1255.0, 1374.0, 1434.0
T_WM, T_TAG, T_BTN, T_PH, T_DIS, T_CLICK = B(45), B(45.5), B(46), B(46.5), B(47), B(48)


@functools.lru_cache(maxsize=1)
def _end_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['coin'] = S3.get('coin_gbp', 'night', mode='spin')
    d['coin_s'] = S3.get('coin_gbp', 'night', mode='spin', scale=0.3)
    d['anim'] = S3.get('logo_mark3d', 'night_anim')
    d['logo'] = S3.get('logo_mark3d', 'night')
    full = K.load_image(K.BRAND + '/logo_full_onDark.png')
    wm = np.ascontiguousarray(full[110:1056, 1915:3901])
    d['wm'] = K.sprite(cv2_resize(wm, 560))
    # tagline: words + LEAF dots (the logo's own tagline is too thin to read at this size)
    words = ('NURTURE', 'DEVELOP', 'GROW')
    sz, tr = 32, 0.16
    ws = [ui.measure(w_, sz, 'ui', tr) for w_ in words]
    gap = 58
    tw = sum(ws) + 2 * gap
    S = ui.Surf(int(tw) + 40, 70)
    x = 20
    for i, w_ in enumerate(words):
        ui.put_text(S.img, x, 47, w_, sz, 'ui', K.C['PEACH'], 'ls', tracking=tr)
        x += ws[i]
        if i < 2:
            S.circle(x + gap / 2, 36, 7, K.C['LEAF_HI'] * 0.9, 1.0)
            x += gap
    d['tag'] = S.sprite()
    d['ph'] = T.render('0161 241 1332  \u00b7  organicfostering.co.uk', 'ui', px=36, fill='IVORY')
    d['dis'] = T.render(FINE, 'ui', px=30, fill='PEACH', font='Poppins-Regular')
    d['halo'] = K.glow(K.ring(300, 4, K.C['AMBER'] * 2.0), K.C['ORANGE'], (10, 30, 80), 1.2)
    d['halo2'] = K.glow(K.ring(300, 3, K.C['HOT_PINK'] * 1.4), K.C['MAGENTA'], (10, 30, 70), 1.0)
    d['warm'] = K.radial(512, K.C['ORANGE'] * 0.6, power=2.0)
    d['dust'] = K.Particles(150, seed=71, bright=0.9, colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']])
    return d


@functools.lru_cache(maxsize=8)
def _feather_mask(h, w, m):
    yy = np.minimum(np.arange(h), np.arange(h)[::-1]).astype(np.float32)[:, None]
    xx = np.minimum(np.arange(w), np.arange(w)[::-1]).astype(np.float32)[None, :]
    d = np.minimum(yy, xx)
    k = np.clip(d / m, 0, 1)
    return (k * k * (3 - 2 * k)).astype(np.float32)[..., None]


def _feather(spr, m=52.0):
    """Workaround (toolkit): ui.button's glow is clipped at its padded sprite bounds (hard-edged rectangle,
    worse with hover). Fade the outer m px of the sprite to zero."""
    return spr * _feather_mask(spr.shape[0], spr.shape[1], float(m))


def cv2_resize(rgba_u8, width):
    import cv2
    h, w = rgba_u8.shape[:2]
    return cv2.resize(rgba_u8, (int(width), int(round(h * width / w))), interpolation=cv2.INTER_AREA)


def _end_logo(t, A):
    """(sprite, scale, anchor) of the coin -> logo flip at time t."""
    if t < T_SWAP:
        u = K.clamp((t - T_END) / (T_SWAP - T_END))
        ang = 450.0 * K.EASE['out_cubic'](u)
        spr = A['coin'].at_yaw(ang % 360.0)
        return spr, K.lerp(0.48, 0.78, K.EASE['out_cubic'](u)), (0.5, 0.5)
    fr = (t - T_SWAP) * 30.0 * 1.45
    an = A['anim']
    if fr < an.n - 1:
        spr = an.blend(fr) if hasattr(an, 'blend') else an.frame(int(fr))
        ap = an.anchor
    else:
        ts = T_SWAP + (an.n - 1) / (30.0 * 1.45)
        lg = A['logo']
        yaw = 6.0 * math.sin(2 * math.pi * (t - ts) / 4.5) * K.ramp(t, ts, ts + 1.0, 'inout_sine')
        spr = lg.at_yaw(yaw, interp='flow')
        ap = lg.anchor
    return spr, LOGO_S, (ap[0] / spr.shape[1], ap[1] / spr.shape[0])


def _scene_end(t):
    _, _, T, ui = _lazy()
    A = _end_assets()
    cam = K.Cam(pos=(K.wiggle(t, 0.3, 6, seed=81), K.wiggle(t, 0.3, 5, seed=82), K.lerp(-1500.0, -1440.0,
                K.EASE['easy_ease'](K.clamp((t - T_END) / (DUR - T_END))))), aperture=24, focus_dist=1500.0)
    sw_ = K.impulse(t, T_SWAP, decay=4.0)
    cv = K.background('amber', t, cam, boost=0.2 + 0.5 * sw_, center=(0.5, 0.28), rim=0.35, intensity=0.75)
    sc = K.Scene(cam)
    for i, P in enumerate(((-1400.0, -1050.0, 2800.0), (1450.0, -600.0, 3100.0), (-1450.0, 700.0, 3000.0),
                           (1400.0, 1300.0, 2700.0))):
        sc.billboard(A['coin_s'].at_yaw((t * 100.0 + 80.0 * i) % 360.0), P, 300.0, rot=20.0 * i, opacity=0.7)
    sc.particles(A['dust'], t)
    sc.render(cv)
    # glow + halo rings behind the logo
    lx, ly = LOGO_XY
    rise = K.ramp(t, T_END, T_SWAP, 'out_cubic')
    cy = K.lerp(1700.0, ly, rise)
    K.draw(cv, A['warm'], lx, ly, scale=2.6, mode='add', opacity=0.55 + 0.5 * sw_)
    hr = K.ramp(t, T_SWAP - 0.05, T_WM - 0.05, 'out_cubic')      # halo burst, gone before the wordmark arrives
    if 0 < hr < 1:
        fo = (1 - hr) ** 1.5
        K.draw(cv, A['halo'], lx, ly, scale=K.lerp(0.5, 1.5, hr), mode='add', opacity=0.9 * fo, rot=t * 20.0)
        K.draw(cv, A['halo2'], lx, ly, scale=K.lerp(0.4, 1.8, hr), mode='add', opacity=0.6 * fo)
    spr, sc_, an = _end_logo(t, A)
    pop = 1.0 + 0.05 * K.impulse(t, T_SWAP, decay=6.0)
    K.draw(cv, spr, lx, cy, scale=sc_ * pop, anchor=an, rot=K.lerp(-12.0, 0.0, rise) if t < T_SWAP else 0.0)
    # wordmark, tagline
    r = K.ramp(t, T_WM, T_WM + 0.6, 'out_expo')
    if r > 0:
        K.draw(cv, A['wm'], 540, WM_Y + 30 * (1 - r), opacity=K.ramp(t, T_WM, T_WM + 0.25), blur=8 * (1 - r))
    r = K.ramp(t, T_TAG, T_TAG + 0.6, 'out_expo')
    if r > 0:
        K.draw(cv, A['tag'], 540, TAG_Y, scale=(K.lerp(1.12, 1.0, r), 1.0), opacity=K.ramp(t, T_TAG, T_TAG + 0.3),
               blur=6 * (1 - r))
    # CTA button + cursor click on B48
    if t >= T_BTN:
        pop = K.spring(t - T_BTN, freq=2.6, damping=0.5)
        hover = K.ramp(t, T_CLICK - 0.35, T_CLICK - 0.1)
        press = K.impulse(t, T_CLICK, decay=9.0, attack=0.04)
        rip = t - T_CLICK if t >= T_CLICK else None
        btn = _feather(ui.button('Discuss your estimate', hover=0.6 * hover, press=press, ripple=rip,
                                 ripple_at=(0.88, 0.55), look='amber'))
        ui.place(cv, btn, 540, BTN_Y, scale=K.lerp(0.6, 1.0, pop), opacity=K.ramp(t, T_BTN, T_BTN + 0.12))
    r = K.ramp(t, T_PH, T_PH + 0.5, 'out_expo')
    if r > 0:
        A['ph'].draw(cv, 540, PH_Y + 20 * (1 - r), opacity=K.ramp(t, T_PH, T_PH + 0.25), blur=5 * (1 - r), snap=False)
    r = K.ramp(t, T_DIS, T_DIS + 0.5, 'out_expo')
    if r > 0:
        A['dis'].draw(cv, 540, DIS_Y, opacity=0.9 * K.ramp(t, T_DIS, T_DIS + 0.3))
    if t >= T_CLICK - 0.75:
        trk = K.Track([(T_CLICK - 0.75, (900.0, 1720.0), 'out_cubic'), (T_CLICK - 0.08, (812.0, 1262.0), 'hold'),
                       (T_CLICK + 0.45, (812.0, 1262.0), 'inout_cubic'), (T_CLICK + 1.2, (1010.0, 1230.0))])
        x, y = trk(t)
        press = K.impulse(t, T_CLICK, decay=9.0, attack=0.04)
        cop = K.ramp(t, T_CLICK - 0.75, T_CLICK - 0.55) * (1 - K.ramp(t, T_CLICK + 0.55, T_CLICK + 0.95))
        if cop > 0.01:
            ui.draw_cursor(cv, x, y, 'hand', 84, press=press, click=(t - T_CLICK) if t >= T_CLICK else None,
                           opacity=cop, look='amber')
    return cv


def _post_end(cv, t):
    fl = 0.9 * K.impulse(t, T_END, decay=10.0) + 0.3 * K.impulse(t, T_SWAP, decay=8.0)   # CTA click: local only
    lk = 1.0 - K.ramp(t, T_END, T_END + 0.12, 'out_cubic')     # leak tail ends on the cut (no veil on the void)
    if lk > 0:
        K.light_leak(cv, t, strength=0.8 * lk, seed=7, sweep=K.ramp(t, T_END - 0.35, T_END + 0.2, 'inout_sine'))
    _hot(cv, fl)
    return K.post(cv, LOOK, t, chroma=1.6 + 4.0 * K.impulse(t, T_SWAP, decay=8.0))


# ================================================================================================ dispatch
def _placeholder(t):
    cam = K.Cam()
    return K.background('amber', t, cam)


def draw(t):
    if t < T_TUN:
        return _scene_coin(t)
    if t < T_NUM:
        return _scene_tunnel(t)
    if t < T_CALC:
        return _scene_number(t)
    if t < T_ORB:
        return _scene_calc(t)
    if t < T_HEART:
        return _scene_orbit(t)
    if t < T_END:
        return _scene_heart(t)
    return _scene_end(t)


def post(cv, t):
    if t < T_NUM:
        return _post_hook(cv, t)
    if t < T_CALC:
        return _post_number(cv, t)
    if t < T_ORB:
        return _post_calc(cv, t)
    if t < T_HEART:
        return _post_orbit(cv, t)
    if t < T_END:
        return _post_heart(cv, t)
    return _post_end(cv, t)


def samples(t):
    """Motion-blur sub-samples: 3 normally, 5-7 on fly-ins, whips, wipes and zoom-throughs."""
    if t < T_TUN - 0.15:
        return 5                                    # coin flipping toward the lens
    if t < B(3.6):
        return 7                                    # coin fill + card tunnel + title slams
    if T_NUM - 0.25 < t < T_NUM + 0.05:
        return 5                                    # zoom-through the title
    if T_CALC - 0.18 < t < T_CALC + 0.3:
        return 7                                    # whip pan B -> C
    if T_ORB - 0.22 < t < T_ORB + 0.22:
        return 7                                    # coin wipe C -> D
    if B(28.3) < t < B(32):
        return 5                                    # ring indexing 72 deg per beat
    if ZOOM[1] - 0.45 < t < T_HEART + 0.05:
        return 5                                    # push / zoom-through the door
    if T_END - 0.05 < t < T_SWAP + 0.12:
        return 5                                    # coin toss + flip into the logo
    return 3


def prewarm():
    _hook_assets()
    _tun_layout()
    _num_assets()
    _calc_assets()
    _orb_assets()
    _heart_assets()
    _end_assets()


def cues():
    """SFX cue sheet (audio.py catalog names; align='hit' puts the designed hit on t). SFX only, no music."""
    c = []
    a = c.append
    # A1 coin -> flash into the tunnel (B1)
    a(dict(t=0.03, name='coin_flip', gain_db=-1))
    a(dict(t=T_TUN - 0.01, name='whoosh_fast', gain_db=-3))
    a(dict(t=T_TUN, name='reverse_swell', gain_db=-7, params=dict(duration=0.42)))
    a(dict(t=T_TUN, name='flash_hit', gain_db=-3))
    a(dict(t=T_TUN + 0.01, name='impact_soft', gain_db=-5))
    # A2 card tunnel: whoosh-bys on the 8ths, slot reels spinning
    for k, tt in enumerate((B(1.5), B(2.0), B(2.5))):
        a(dict(t=tt, name='whoosh_by', gain_db=-6, pan=0.55 * (-1) ** k,
               params=dict(dur=0.8, direction=(-1) ** k)))
    a(dict(t=T_TUN + 0.05, name='slot_tick', gain_db=-4, align='start', params=dict(n=16, dur=0.85)))
    a(dict(t=T_TITLE, name='reverse_swell', gain_db=-5, params=dict(duration=0.6)))
    # A3 title slams
    a(dict(t=T_TITLE, name='impact_big', gain_db=-1))
    a(dict(t=T_TITLE + 0.01, name='sub_drop', gain_db=-5, params=dict(dur=1.4)))
    a(dict(t=B(3.5), name='impact_soft', gain_db=-3))
    a(dict(t=B(3.85), name='shimmer', gain_db=-9, params=dict(dur=0.9)))
    a(dict(t=B(4), name='swish_small', gain_db=-4))
    a(dict(t=T_NUM, name='air_zoom', gain_db=-3))
    # B the number
    a(dict(t=NUM_ROLL[0], name='slot_tick', gain_db=-3, align='start',
           params=dict(n=18, dur=NUM_ROLL[1] - NUM_ROLL[0])))
    a(dict(t=T_NUM + 0.35, name='whoosh_by', gain_db=-9, pan=-0.4, params=dict(dur=1.0, direction=1)))
    a(dict(t=B(6), name='swish_small', gain_db=-5, pan=0.1))
    a(dict(t=NUM_ROLL[1], name='cash_kaching', gain_db=0))
    a(dict(t=NUM_ROLL[1] + 0.02, name='coin_ring', gain_db=-7, pan=0.2))
    a(dict(t=B(9), name='pop', gain_db=-4))
    a(dict(t=B(9.6), name='whoosh_by', gain_db=-12, pan=0.5, params=dict(dur=1.2, direction=-1)))
    a(dict(t=T_CALC, name='whip', gain_db=-2, params=dict(direction=1)))
    # C calculator
    a(dict(t=T_CALC + 0.25, name='glass_tap', gain_db=-5))
    for i, ct in enumerate(CLICKS):
        a(dict(t=ct, name='ui_click', gain_db=-2, pan=-0.15 + 0.1 * i))
        if i < 4:
            a(dict(t=ct, name='bar_grow', gain_db=-5, align='start', params=dict(duration=0.5, pitch=0.9 + 0.1 * i)))
    a(dict(t=B(16.8), name='whoosh_slow', gain_db=-11))
    a(dict(t=DRAG[0], name='ui_click', gain_db=-4))
    a(dict(t=DRAG[0], name='slider_drag', gain_db=-2, align='start',
           params=dict(duration=DRAG[1] - DRAG[0], detents=12)))
    a(dict(t=DRAG[1], name='cash_kaching', gain_db=0))
    a(dict(t=DRAG[1] + 0.03, name='coins_burst', gain_db=-7))
    a(dict(t=DRAG[1] + 0.2, name='ui_tick', gain_db=-7))
    a(dict(t=DRAG[1] + 0.2, name='shimmer', gain_db=-9, params=dict(dur=1.0)))
    a(dict(t=B(24.2), name='shimmer', gain_db=-11, params=dict(dur=1.4)))          # second glint on the hold
    a(dict(t=B(25.5), name='whoosh_slow', gain_db=-14, pan=-0.3))                # slow push breath before the wipe
    # C -> D coin wipe
    a(dict(t=T_ORB - 0.12, name='coin_flip', gain_db=-6))
    a(dict(t=T_ORB, name='whoosh_by', gain_db=-2, params=dict(dur=1.0, direction=1)))
    # D support orbit
    a(dict(t=T_ORB + 0.12, name='impact_soft', gain_db=-5))
    a(dict(t=B(27.5), name='swish_small', gain_db=-5))
    a(dict(t=B(28), name='swish_small', gain_db=-6, pan=0.2))
    for k in range(len(TAGS)):
        a(dict(t=B(28 + k), name='pop', gain_db=-4, pan=0.15 * (-1) ** k, params=dict(pitch=0.9 + 0.06 * k)))
        if k:
            a(dict(t=B(28 + k) - 0.06, name='swish_small', gain_db=-11, pan=-0.3))
    a(dict(t=B(33), name='whoosh_slow', gain_db=-12))
    a(dict(t=T_HEART, name='riser', gain_db=-6, params=dict(duration=1.3)))
    a(dict(t=T_HEART, name='air_zoom', gain_db=-2))
    # E heart beat
    a(dict(t=T_HEART + 0.08, name='heartbeat', gain_db=-3, params=dict(n=2, bpm=64)))
    a(dict(t=REC_T[0], name='swish_small', gain_db=-6))
    a(dict(t=REC_T[1], name='swish_small', gain_db=-7, pan=0.2))
    a(dict(t=B(39.6), name='shimmer', gain_db=-10, params=dict(dur=1.0)))
    a(dict(t=T_END, name='reverse_swell', gain_db=-5, params=dict(duration=0.8)))
    # F end card: coin -> logo, CTA click
    a(dict(t=T_END, name='flash_hit', gain_db=-4))
    a(dict(t=T_END + 0.03, name='coin_flip', gain_db=-3))
    a(dict(t=T_SWAP - 0.12, name='whoosh_fast', gain_db=-9))
    a(dict(t=T_SWAP, name='logo_sting', gain_db=-1))
    a(dict(t=T_SWAP + 0.03, name='sparkle', gain_db=-9))
    a(dict(t=T_WM, name='swish_small', gain_db=-6))
    a(dict(t=T_BTN, name='pop', gain_db=-4))
    a(dict(t=T_PH, name='ui_tick', gain_db=-8))
    a(dict(t=T_CLICK, name='ui_click', gain_db=-1))
    return c


def _check_orbit(step=1.0 / 30, t0=None, t1=None, verbose=False):
    """Dev check for scene D over every frame: returns dict of worst margins (px; negative = violation):
    safe = inside x 70..1010 / y 490..1480 (below the headline), like = right edge <= 930 when the tag reaches
    y >= 1050, gap = min gap between visible tags, house = gap between back tags and the house sprite bbox,
    plus per-tag readable seconds (fully entered, fade > 0.95)."""
    import sprites3d as S3
    A = _orb_assets()
    hs = S3.get('house', 'night')
    bx0, by0, bx1, by1 = hs.bbox
    worst = dict(safe=(1e9, None), like=(1e9, None), gap=(1e9, None), house=(1e9, None))
    readable = [0.0] * len(TAGS)
    t0 = B(28) if t0 is None else t0
    t1 = ZOOM[0] + 0.45 if t1 is None else t1

    def upd(key, v, where):
        if v < worst[key][0]:
            worst[key] = (round(float(v), 1), where)
    for t in np.arange(t0, t1, step):
        cam = _orb_cam(t)
        fade = 1.0 - K.ramp(t, ZOOM[0], ZOOM[0] + 0.45, 'in_cubic')
        hp = _house_pos(t)
        hxy, hd = cam.project(np.array([hp]))
        k_ = cam.focal / hd[0] * HOUSE_W / hs.size[0]
        hcx, hcy = hxy[0]
        hbox = (hcx + (bx0 - hs.size[0] / 2) * k_, hcy + (by0 - hs.size[1] / 2) * k_,
                hcx + (bx1 - hs.size[0] / 2) * k_, hcy + (by1 - hs.size[1] / 2) * k_)
        rects = []
        for k in range(len(TAGS)):
            en, P, zz = _tag_world(k, t)
            if en <= 0.3 or fade < 0.3:
                continue
            xy, d = cam.project(P[None, :])
            sc_ = (0.62 + 0.38 * K.EASE['out_back'](min(en, 1.0))) * cam.focal / d[0]
            pnl = A['tags'][k]
            w_, h_ = pnl.w * sc_, pnl.h * sc_
            r = (xy[0][0] - w_ / 2, xy[0][1] - h_ / 2, xy[0][0] + w_ / 2, xy[0][1] + h_ / 2)
            rects.append((k, r, zz > 0))
            if en >= 1 and fade > 0.95:
                readable[k] += step
            where = (round(float(t), 2), k)
            upd('safe', min(r[0] - 70, 1010 - r[2], r[1] - 490, 1480 - r[3]), where)
            if r[3] >= 1050:
                upd('like', 930 - r[2], where)
            if zz > 0:
                g = max(hbox[0] - r[2], r[0] - hbox[2], hbox[1] - r[3], r[1] - hbox[3])
                upd('house', g, where)
        for a in range(len(rects)):
            for b_ in range(a + 1, len(rects)):
                ka, ra, _ = rects[a]
                kb, rb, _ = rects[b_]
                g = max(rb[0] - ra[2], ra[0] - rb[2], rb[1] - ra[3], ra[1] - rb[3])
                upd('gap', g, (round(float(t), 2), ka, kb))
    out = dict(worst)
    out['readable_s'] = [round(r, 2) for r in readable]
    if verbose:
        print(out)
    return out
