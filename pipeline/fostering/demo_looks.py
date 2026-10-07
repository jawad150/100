"""demo_looks.py: integration demo - one polished hero frame per reel look + a 4 s SFX'd clip (not a deliverable).

It composes the whole toolkit (core, footage, type3d, ui, sprites3d, audio, render) into three hero moments and is
the reference the timeline agents can copy patterns from:

    scene_neon(u)   reel 1 "Could YOU be a Foster Carer?": glossy 3D "?" spinning in from depth, extruded
                    gradient "YOU" with a light sweep, deep-glow "Foster Carer?", c01 in a tilted glass card far
                    behind (bokeh DOF), a magenta light ring, dust bokeh, slow orbit + push-in camera.
    scene_amber(u)  reel 2 allowance calculator: perspective glass app window (age chips, glossy bar chart, weeks
                    slider, fine print), a huge gold odometer counter rolling to GBP 23,275.20 with 3D coins
                    orbiting it on a tilted ellipse (depth sorted, back coins defocused), gold dust.
    scene_airy(u)   reel 3 "NURTURE": c11 playing inside the letters (video-in-type), a white glass chapter pill,
                    a swaying 3D sprout with a contact shadow, tumbling 3D leaves at three depths (DOF).
    u = scene-local seconds (each scene is a pure function of u). HERO_U[look] = the settled hero moment.

REEL MODULE (python3 render.py demo_looks): DUR 4.0 s at 120 BPM. 0-1.5 neon, whip pan (7 samples) -> 1.5-2.5
amber, white flash + zoom blur -> 2.5-4.0 airy. cues() is a catalog-name SFX sheet (whip, impacts, slot ticks,
ka-ching, air zoom, leaf rustle, shimmer ...) mixed with BED by `python3 audio.py reel demo_looks`;
render.py then muxes workspace3/audio/demo_looks_sfx.wav into the master.

    python3 demo_looks.py heroes [--samples 3]   -> out/demo_looks/hero_{neon,amber,airy}.png (+ .jpg), full quality
    python3 demo_looks.py clip                   -> builds the SFX mix, renders the 4 s master through render.py and
                                                    verifies duration / streams / loudness (prints a report)
    python3 demo_looks.py selftest               -> out/selftest/demo_looks_{neon,amber,airy}.png (1 sample, fast)
Python: hero_still(look, samples=3) -> uint8 frame; scene(look, u) -> linear canvas; post_look(look, cv, u).
"""
import functools
import math
import os
import sys
import types

import numpy as np

import core as K

DUR = 4.0
LOOK = 'neon'
BPM = 120
BEAT = 60.0 / BPM
CUT1, CUT2 = 1.5, 2.5                      # on the 120 BPM grid (beats 3 and 5)
HERO_U = {'neon': 1.8, 'amber': 2.45, 'airy': 1.62}
BED = [{'name': 'room_tone', 't0': 0.0, 't1': CUT2 + 0.2, 'gain_db': 0.0, 'fade': 0.3},
       {'name': 'outdoor_birds', 't0': CUT2 - 0.1, 't1': DUR, 'gain_db': 2.0, 'fade': 0.4}]
BED_GAIN_DB = -27.0


def _lazy():
    """Heavy modules are imported on first use (keeps `import demo_looks` cheap and side-effect free)."""
    import footage as F
    import sprites3d as S3
    import type3d as T
    import ui
    return F, S3, T, ui


# =============================================================================================== NEON
_NEON_TXT = dict(could=(0.45, -150.0), you=(0.72, 30.0), bea=(1.0, 205.0), fc=(1.12, 345.0))


@functools.lru_cache(maxsize=1)
def _neon_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['could'] = T.render('Could', 'flat', px=104, fill='IVORY', glow=0.55, glow_color=('MAGENTA', 2.2),
                          glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3))
    d['you'] = T.render('YOU', 'extrude3d', px=250, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35,
                        fill_gain=1.25, depth=0.16, glow=0.55, glow_color=('MAGENTA', 1.6))
    d['bea'] = T.render('be a', 'flat', px=96, fill='IVORY', glow=0.5, glow_color=('MAGENTA', 2.0),
                        glow_radii=(0.05, 0.18, 0.45), glow_weights=(0.8, 0.5, 0.3))
    d['fc'] = T.render('Foster Carer?', 'deep_glow', px=122, glow_color=('ORANGE', 2.5),
                       inner_glow_color=('AMBER', 1.25))
    d['q'] = S3.get('question', 'night', mode='spin')
    d['card'] = ui.glass_card(600, 820, r=48, look='neon', rim=1.2, glow=1.0, rim_angle=-60)
    d['clip'] = F.Clip('c01')
    d['ring'] = K.glow(K.ring(300, 4, K.C['HOT_PINK'] * 2.4), K.C['MAGENTA'], (8, 28, 80), 1.3)
    d['dust'] = K.Particles(190, seed=7, bright=0.9, size=(1.2, 3.8))
    d['bokeh'] = K.glow(K.disc(60, K.C['HOT_PINK'] * 0.8), K.C['MAGENTA'], (20, 60), 0.6)
    d['bokeh2'] = K.glow(K.disc(48, K.C['ORANGE'] * 0.9), K.C['ORANGE'], (20, 60), 0.6)
    return d


def neon_cam(u, whip=0.0):
    e = K.EASE['easy_ease'](K.clamp(u / 3.2))
    dist = K.lerp(1780.0, 1560.0, e)
    yaw = K.lerp(8.0, -4.0, e)
    slam = K.impulse(u, _NEON_TXT['you'][0] + 0.02, decay=8.0)
    sx, sy, sr = K.shake(u, 10.0 * slam, 15.0, seed=11)
    cam = K.Cam.orbit((sx, -60.0 + sy, 0.0), dist, yaw=yaw - whip, pitch=1.5 + K.wiggle(u, 0.3, 0.6, seed=2),
                      roll=sr * 0.4, aperture=34)
    return cam


def scene_neon(u, whip=0.0):
    _, _, T, ui = _lazy()
    A = _neon_assets()
    cam = neon_cam(u, whip)
    land = K.impulse(u, 0.85, decay=6.0)
    cv = K.background('neon', u, cam, boost=0.35 * land + 0.15 * K.beat_pulse(u, BPM, decay=5.0),
                      center=(0.72, 0.24))
    sc = K.Scene(cam)
    # far plate: c01 inside a tilted neon glass card (bokeh DOF from depth)
    card = A['card']
    media = A['clip'].get(4.0 + u * 0.8, card.w, card.h, zoom=1.08 + 0.02 * u, look='neon')
    face = ui.media_face(card, media, sweep=(0.15 + u * 0.32) % 1.0)
    cpos = (-330.0, -560.0, 1750.0)
    sc.custom(cpos, lambda c, cm: card.plane(c, cm, cpos, 600, rot=(4.0, -24.0, 5.0), face=face, shadow=0.6))
    # light ring portal behind the "?"
    ring_op = K.ramp(u, 0.55, 1.1, 'out_cubic')
    rs = 0.82 + 0.18 * K.ramp(u, 0.55, 1.3, 'out_expo') + 0.02 * math.sin(u * 2.1)
    sc.plane(A['ring'], (110.0, -545.0, 520.0), 1100 * rs, rot=(8.0, -18.0, 0.0), mode='add', opacity=0.85 * ring_op)
    # glossy "?" spinning in from depth (spin asset: any angle; settles into a gentle sway)
    p = K.ramp(u, 0.0, 0.85, 'out_expo')
    qz = K.lerp(5200.0, 120.0, p)
    qx = K.lerp(420.0, 110.0, K.ramp(u, 0.0, 0.85, 'out_cubic'))
    qy = K.lerp(-900.0, -560.0, K.ramp(u, 0.0, 0.85, 'out_quint')) + 10 * math.sin(u * 1.4)
    ang = -720.0 * (1.0 - p) + 16.0 * math.sin(u * 1.25) * K.ramp(u, 0.7, 1.6, 'inout_sine')
    q = A['q']
    qs = q.at_yaw(ang)
    qw = 640.0 * (1.0 + 0.06 * land)
    sc.billboard(qs, (qx, qy, qz), qw, rot=-6.0 + 6.0 * p)
    # type, on planes in the same 3D space (parallax under the orbit)
    you_u = _NEON_TXT['you'][0]
    for key in ('could', 'bea', 'fc'):
        t0, y = _NEON_TXT[key]
        pr = K.ramp(u, t0, t0 + 0.7, 'out_expo')
        if pr <= 0:
            continue
        op = K.ramp(u, t0, t0 + 0.28, 'out_cubic')
        ts = A[key]
        pos = (0.0, y + 70.0 * (1 - pr), -40.0 + 160.0 * (1 - pr))
        sc.custom(pos, lambda c, cm, ts=ts, pos=pos, op=op, pr=pr: ts.draw_plane(
            c, cm, pos, rot=(0, 0, 0), scale=1.0, opacity=op, blur=7.0 * (1 - pr)))
    if u >= you_u:
        sp = K.spring(u - you_u, freq=2.4, damping=0.42)
        s = 1.75 + (1.0 - 1.75) * sp
        op = K.ramp(u, you_u, you_u + 0.05)
        sweep = K.ramp(u, 1.25, 2.3, 'inout_sine')
        pos = (0.0, _NEON_TXT['you'][1], -60.0)
        ts = A['you']
        sc.custom(pos, lambda c, cm: ts.draw_plane(c, cm, pos, scale=s, opacity=op, sweep=sweep if 0 < sweep < 1
                                                   else None, sweep_kw=dict(width=0.12, strength=1.6)))
    # foreground: near defocused bokeh blobs + dust
    sc.billboard(A['bokeh'], (-520.0, 520.0, -900.0), 260, mode='add', opacity=0.55)
    sc.billboard(A['bokeh2'], (470.0, -820.0, -1000.0), 220, mode='add', opacity=0.45)
    sc.particles(A['dust'], u)
    sc.render(cv)
    return cv


def post_neon(cv, u, extra=None):
    slam = K.impulse(u, _NEON_TXT['you'][0], decay=7.0)
    land = K.impulse(u, 0.85, decay=6.0)
    fly = K.ramp(u, 0.0, 0.3) * (1 - K.ramp(u, 0.5, 0.85))
    kw = dict(flash=0.22 * slam + 0.1 * land, chroma=1.8 + 7 * fly + 5 * slam)
    kw.update(extra or {})
    return K.post(cv, 'neon', u, **kw)


# =============================================================================================== AMBER
_VALS = [447.60, 473.17, 515.52, 554.02]
_LABELS = ['0\u20134', '5\u201310', '11\u201314', '15+']
_ROLL = (0.35, 1.75)
_TOTAL = 23275.20


@functools.lru_cache(maxsize=1)
def _amber_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['win'] = ui.app_window(w=860, h=930, look='amber', header='Allowance calculator',
                             sub='Weekly allowance per child', icons=('home', 'pound', 'chart', 'calendar',
                                                                      'settings'), active=1)
    d['counter'] = T.Counter('gold', px=150)
    d['label'] = T.render('Estimated allowance \u00b7 52 weeks', 'ui', px=36, fill='PEACH')
    d['coin'] = S3.get('coin_gbp', 'night', mode='spin')
    d['dust'] = K.Particles(150, seed=3, bright=0.85, colors=[K.C['AMBER'], K.C['ORANGE'], K.C['PEACH']])
    return d


def amber_cam(u, whip=0.0):
    e = K.EASE['easy_ease'](K.clamp(u / 3.0))
    return K.Cam(pos=(K.lerp(-60.0, 10.0, e), K.lerp(-40.0, 0.0, e), K.lerp(-1640.0, -1520.0, e)),
                 yaw=K.lerp(5.0, 1.0, e) + whip, pitch=K.lerp(-3.0, -0.5, e) + K.wiggle(u, 0.3, 0.4, seed=5),
                 roll=K.lerp(-1.2, 0.0, e), aperture=26, focus_dist=1480.0)


def _amber_face(u):
    _, _, _, ui = _lazy()
    A = _amber_assets()
    win = A['win']
    x, y, sw, sh = win.meta['slot']
    f = win.face_at(sweep=(0.1 + u * 0.3) % 1.0)
    cx = x
    for i, lab in enumerate(_LABELS):
        c = ui.chip(lab, K.ramp(u, 0.25, 0.55, 'out_cubic') if i == 0 else 0.0, look='amber', origin=(0.35, 0.5))
        win.put(f, c, cx - 24, y - 24)
        cx += c.shape[1] - 48 + 16
    grow = [K.ramp(u, 0.3 + 0.16 * i, 1.0 + 0.16 * i, 'out_back') for i in range(4)]
    bars = ui.bar_chart(_VALS, _LABELS, grow=grow, active=0.0, w=sw, h=420, look='amber', depth=12)
    win.put(f, bars, x - 32, y + 100 - 32)
    v = K.ramp(u, 0.9, 1.7, 'inout_cubic')
    wk = int(round(K.lerp(1, 52, v)))
    sl = ui.slider(v, w=sw - 80, look='amber', label='%d weeks' % wk, ticks=[(0, '1'), (1, '52')])
    win.put(f, sl, x, y + 540)
    ui.put_text(f, win.pad + x, win.pad + y + 820, 'Rates may vary by region and are subject to change.', 30,
                'body', ui.LOOKS['amber'].text2, 'ls', max_w=sw)
    return f


def scene_amber(u, whip=0.0):
    A = _amber_assets()
    cam = amber_cam(u, whip)
    land = K.impulse(u, _ROLL[1], decay=6.0)
    cv = K.background('amber', u, cam, boost=0.4 * land, center=(0.3, 0.22))
    sc = K.Scene(cam)
    # the app window, tilted (isometric-ish), lower half of the frame
    win = A['win']
    face = _amber_face(u)
    wpos, wrot = (40.0, 300.0, 160.0), (9.0, 13.0, -1.5)
    sc.custom(wpos, lambda c, cm: win.plane(c, cm, wpos, 860, rot=wrot, face=face))
    # the counter: odometer roll with per-digit motion blur, floating in front of the window
    trk = K.Track([(_ROLL[0], 0.0, 'out_expo'), (_ROLL[1], _TOTAL)])
    val, vel = float(trk(u)), float(trk.vel(u))
    cnt = A['counter']
    cpos = (0.0, -470.0, 0.0)
    pop = 1.0 + 0.06 * land
    sc.custom(cpos, lambda c, cm: cnt.sprite(val, vel).draw_plane(c, cm, cpos, scale=pop, dof=False))
    lab = A['label']
    lpos = (0.0, -335.0, -10.0)
    sc.custom(lpos, lambda c, cm: lab.draw_plane(c, cm, lpos, opacity=K.ramp(u, 0.5, 0.9), dof=False))
    # 3D coins orbiting the number: tilted ellipse, front lower, back higher (back ones defocus)
    coin = A['coin']
    n = 6
    for i in range(n):
        th = 2 * math.pi * (i / n + 0.05 * u + 0.07)
        x = 600.0 * math.cos(th)
        z = 300.0 * math.sin(th)
        y = -470.0 - 0.78 * z
        ent = K.ramp(u, 0.1 + 0.07 * i, 0.7 + 0.07 * i, 'out_back')
        spr = coin.at_yaw((u * 140.0 + i * 61.0) % 360.0)
        sc.billboard(spr, (x, y, z), 190 * ent, rot=-12 + 8 * math.sin(th))
    sc.particles(A['dust'], u)
    sc.render(cv)
    return cv


def post_amber(cv, u, extra=None):
    land = K.impulse(u, _ROLL[1], decay=6.0)
    kw = dict(flash=0.14 * land)
    kw.update(extra or {})
    return K.post(cv, 'amber', u, **kw)


# =============================================================================================== AIRY
@functools.lru_cache(maxsize=1)
def _airy_assets():
    F, S3, T, ui = _lazy()
    d = {}
    d['vt'] = T.VideoType('NURTURE', px=200, tracking=-0.01, look='light')
    d['clip'] = F.Clip('c11')
    d['sub'] = T.render('A safe home & everyday care', 'ui_ink', px=42)
    d['pill'] = T.render('01 / 03', 'glass_pill_light', px=40)
    d['sprout'] = S3.get('sprout', 'day', mode='sway')
    d['leaf'] = S3.get('leaf', 'day')
    d['leaf_s'] = S3.get('leaf', 'day', scale=0.5)
    sh = K.radial(400, K.C['PLUM'], power=1.6)
    d['shadow'] = sh
    d['motes'] = K.Particles(90, seed=12, bright=0.5, colors=[K.C['WHITE'], K.C['PEACH'], K.C['AMBER']],
                             size=(1.5, 4.0))
    return d


# (world pos at u=0, fall speed px/s, phase, width) - three depth layers
_LEAVES = [((-430.0, -720.0, 650.0), 38.0, 0.10, 150.0), ((450.0, -260.0, 900.0), 30.0, 0.55, 140.0),
           ((330.0, -900.0, 2600.0), 22.0, 0.30, 150.0), ((-300.0, 120.0, 2900.0), 20.0, 0.80, 140.0),
           ((-520.0, 820.0, -820.0), 55.0, 0.40, 210.0), ((560.0, -640.0, -760.0), 60.0, 0.70, 190.0),
           ((120.0, -1180.0, 1600.0), 26.0, 0.20, 120.0)]


def airy_cam(u, whip=0.0):
    e = K.EASE['easy_ease'](K.clamp(u / 3.0))
    return K.Cam(pos=(K.lerp(-25.0, 15.0, e), K.lerp(20.0, -10.0, e), K.lerp(-1560.0, -1480.0, e)),
                 yaw=K.lerp(1.2, -0.8, e) + whip, pitch=K.wiggle(u, 0.25, 0.3, seed=8), aperture=30, focus_dist=1500.0)


def scene_airy(u, whip=0.0):
    _, _, T, ui = _lazy()
    A = _airy_assets()
    cam = airy_cam(u, whip)
    cv = K.background('airy', u, cam)
    sc = K.Scene(cam)
    # far leaves first (scene sorts by depth anyway)
    leaf, leaf_s = A['leaf'], A['leaf_s']
    for (p0, vy, ph, w) in _LEAVES:
        x = p0[0] + 40.0 * math.sin(u * 0.9 + ph * 6.0)
        y = p0[1] + vy * u
        spr = (leaf_s if p0[2] > 2000 else leaf).at_time(u * 0.55 + ph * 1.6, fps=30)
        sc.billboard(spr, (x, y, p0[2]), w, rot=25.0 * math.sin(u * 0.7 + ph * 9))
    # sprout on the ivory surface, with a soft contact shadow
    sp = A['sprout']
    base = (0.0, 620.0, 120.0)

    def draw_sprout(c, cm):
        xy, z = cm.project(np.array([base]))
        k = cm.focal / z[0]
        K.draw(c, A['shadow'], xy[0][0], xy[0][1] + 8 * k, scale=(1.1 * k, 0.16 * k), opacity=0.22)
        img = sp.at_time(u)
        piv = sp.pivot
        K.draw(c, img, xy[0][0], xy[0][1], scale=0.6 * k, anchor=(piv[0] / sp.size[0], piv[1] / sp.size[1]),
               blur=cm.coc(z[0]) * 0.5)
    sc.custom(base, draw_sprout)

    # video-in-type + pill + sub on the focus plane (2D, drawn as one depth item)
    def draw_type(c, cm):
        cx, cy = cm.project(np.array([[0.0, -140.0, 0.0]]))[0][0]
        vt = A['vt']
        s_in = K.ramp(u, 0.0, 0.9, 'out_expo')
        sc_ = K.lerp(1.12, 1.0, s_in) * (1.0 + 0.01 * u)
        foot = A['clip'].get(1.0 + 0.85 * u, K.W, K.H, zoom=1.06 + 0.015 * u, look='airy')
        sweep = K.ramp(u, 1.15, 2.0, 'inout_sine')
        vt.draw(c, foot, cx, cy, scale=sc_, opacity=K.ramp(u, 0.0, 0.25), sweep=sweep if 0 < sweep < 1 else None)
        po = K.ramp(u, 0.25, 0.7, 'out_back')
        A['pill'].draw(c, cx, cy - 210, scale=0.85 + 0.15 * po, opacity=K.ramp(u, 0.25, 0.45))
        so = K.ramp(u, 0.45, 1.0, 'out_expo')
        A['sub'].draw(c, cx, cy + 165 + 30 * (1 - so), opacity=so, snap=False)
    sc.custom((0.0, -140.0, 0.0), draw_type)
    sc.particles(A['motes'], u)
    sc.render(cv)
    return cv


def post_airy(cv, u, extra=None):
    kw = dict(extra or {})
    return K.post(cv, 'airy', u, **kw)


SCENES = {'neon': (scene_neon, post_neon), 'amber': (scene_amber, post_amber), 'airy': (scene_airy, post_airy)}


def scene(look, u, whip=0.0):
    return SCENES[look][0](u, whip)


def post_look(look, cv, u, **extra):
    return SCENES[look][1](cv, u, extra)


# =============================================================================================== 4 s reel
def _seg(t):
    """(look, local u) for clip time t."""
    if t < CUT1:
        return 'neon', t
    if t < CUT2:
        return 'amber', 0.25 + (t - CUT1) * 1.6
    return 'airy', 0.35 + (t - CUT2) * 0.85


def _whip(t):
    """Signed whip amount around CUT1: ramps up into the cut, decays out of it (-1..1)."""
    a = K.ramp(t, CUT1 - 0.14, CUT1, 'in_expo')
    b = 1.0 - K.ramp(t, CUT1, CUT1 + 0.2, 'out_expo')
    return a if t < CUT1 else -b


def draw(t):
    look, u = _seg(t)
    w = _whip(t)
    cv = scene(look, u, whip=38.0 * w)          # a real camera whip (yaw swing, parallax), blurred by samples
    if abs(w) > 1e-3:
        K.whip_blur(cv, 160.0 * abs(w), angle=0.0)
    return cv


def post(cv, t):
    look, u = _seg(t)
    w = abs(_whip(t))
    f2 = K.impulse(t, CUT2, decay=7.0, attack=0.08) + K.ramp(t, CUT2 - 0.12, CUT2, 'in_expo') * (t < CUT2)
    extra = dict(chroma=1.8 + 9.0 * w)
    f1 = K.impulse(t, CUT1, decay=10.0)
    fl = 0.5 * f1 + 1.1 * f2
    if fl > 1e-3:
        extra['flash'] = fl
    cv = post_look(look, cv, u, **extra)
    if abs(t - CUT2) < 0.3:
        z = 0.1 * (K.ramp(t, CUT2 - 0.2, CUT2, 'in_cubic') if t < CUT2 else 1 - K.ramp(t, CUT2, CUT2 + 0.25))
        if z > 1e-3:
            K.zoom_blur(cv, z)
    return cv


def samples(t):
    if CUT1 - 0.2 <= t <= CUT1 + 0.25 or CUT2 - 0.15 <= t <= CUT2 + 0.2:
        return 7
    if t < 0.9:                     # the "?" flying in fast from depth
        return 5
    return 3


def prewarm():
    _neon_assets(), _amber_assets(), _airy_assets()
    for lk in ('neon', 'amber', 'airy'):
        scene(lk, HERO_U[lk])


def cues():
    """SFX cue sheet (catalog names, align = hit unless stated). Beats: 0.5 s grid."""
    c = [
        dict(t=0.80, name='whoosh_by', gain_db=-4, params=dict(dur=1.0, direction=-1)),     # "?" from depth
        dict(t=0.85, name='glass_tap', gain_db=-6),                                          # "?" lands
        dict(t=0.45, name='swish_small', gain_db=-2, pan=-0.2),                              # Could
        dict(t=0.72, name='reverse_swell', gain_db=-5, params=dict(duration=0.6)),           # into the slam
        dict(t=0.72, name='impact_big', gain_db=-3),                                         # YOU slam
        dict(t=0.74, name='sub_drop', gain_db=-5, params=dict(dur=1.4)),
        dict(t=1.00, name='ui_tick', gain_db=-4, pan=0.2),                                   # be a
        dict(t=1.12, name='swish_small', gain_db=-4, pan=0.3),                               # Foster Carer?
        dict(t=1.25, name='shimmer', gain_db=-8, params=dict(dur=1.0)),                      # light sweep
        dict(t=CUT1, name='whip', gain_db=-1, params=dict(direction=1)),                     # whip pan
        dict(t=CUT1, name='flash_hit', gain_db=-6),
        dict(t=CUT1 + 0.04, name='coin_flip', gain_db=-6),
        dict(t=CUT1 + 0.03, name='bar_grow', gain_db=-8, align='start', params=dict(duration=0.7)),
        dict(t=CUT1 + (_ROLL[0] - 0.25) / 1.6, name='slot_tick', gain_db=-4, align='start',
             params=dict(n=14, dur=(_ROLL[1] - _ROLL[0]) / 1.6)),
        dict(t=CUT1 + (_ROLL[1] - 0.25) / 1.6, name='cash_kaching', gain_db=-3),             # total lands
        dict(t=CUT2, name='air_zoom', gain_db=-2),                                           # flash / zoom
        dict(t=CUT2, name='impact_soft', gain_db=-4),
        dict(t=CUT2 + 0.22, name='pop', gain_db=-6, pan=-0.1),                               # 01 / 03 pill
        dict(t=CUT2 + 0.15, name='leaf_rustle', gain_db=-5, pan=0.35, params=dict(dur=1.2)),
        dict(t=CUT2 + 0.95, name='shimmer', gain_db=-9, params=dict(dur=1.2)),               # sweep on NURTURE
    ]
    return c


# =============================================================================================== stills / clip
def hero_module(look):
    """A render.py-compatible module object for one look's hero scene (draw / post / samples)."""
    return types.SimpleNamespace(__name__='demo_' + look, DUR=3.0, LOOK=look, draw=lambda u: scene(look, u),
                                 post=lambda cv, u: post_look(look, cv, u), samples=lambda u: 3)


def hero_still(look, samples=3, u=None):
    import render
    return render.render_still(hero_module(look), HERO_U[look] if u is None else u, samples)


def render_heroes(samples=3, out_dir=None, looks=('neon', 'amber', 'airy')):
    import time
    out_dir = out_dir or os.path.join(K.OUT, 'demo_looks')
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for lk in looks:
        t0 = time.time()
        u8 = hero_still(lk, samples)
        p = K.save_png(os.path.join(out_dir, 'hero_%s.png' % lk), u8)
        K.save_png(os.path.join(out_dir, 'hero_%s.jpg' % lk), u8)
        paths.append(p)
        print('hero %-5s u=%.2f  %d samples  %.1fs -> %s' % (lk, HERO_U[lk], samples, time.time() - t0, p))
    return paths


def build_and_render_clip(workers=4):
    """SFX mix -> render.py full render (muxes the wav) -> verification report."""
    import json
    import subprocess
    import audio as AU
    import render
    rep = AU.build_reel('demo_looks', verbose=False)
    print('SFX: %.2f LUFS  %.2f dBTP  -> %s' % (rep['integrated_lufs'], rep['true_peak_dbtp'],
                                                ', '.join(rep.get('files', []))))
    render.main(['demo_looks', '--workers', str(workers)])
    out = os.path.join(K.OUT, 'demo_looks', 'demo_looks.mp4')
    return verify_master(out)


def verify_master(path, dur=DUR):
    """ffprobe streams + duration, and ffmpeg ebur128 loudness of the muxed audio. Returns a dict."""
    import json
    import re
    import subprocess
    pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                         'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,color_space,'
                         'color_transfer,color_primaries,sample_rate,channels,bit_rate,nb_frames,duration'
                         ':format=duration', '-of', 'json', path], stdout=subprocess.PIPE, text=True)
    info = json.loads(pr.stdout or '{}')
    eb = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-map', '0:a:0', '-af',
                         'ebur128=peak=true', '-f', 'null', '-'], stderr=subprocess.PIPE, text=True)
    tail = eb.stderr[eb.stderr.rfind('Summary:'):] if 'Summary:' in eb.stderr else ''
    m_i = re.search(r'I:\s+(-?[\d.]+) LUFS', tail)
    m_p = re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail)
    rep = {'streams': info.get('streams', []), 'format_duration': float(info.get('format', {}).get('duration', 0)),
           'loudness_lufs': float(m_i.group(1)) if m_i else None,
           'true_peak_dbfs': float(m_p.group(1)) if m_p else None}
    v = [s for s in rep['streams'] if s.get('codec_type') == 'video']
    a = [s for s in rep['streams'] if s.get('codec_type') == 'audio']
    rep['checks'] = {
        'video_h264_high_yuv420p_bt709': bool(v) and v[0].get('codec_name') == 'h264' and
        v[0].get('profile') == 'High' and v[0].get('pix_fmt') == 'yuv420p' and v[0].get('color_space') == 'bt709',
        'size_1080x1920_30fps': bool(v) and (v[0].get('width'), v[0].get('height')) == (1080, 1920) and
        v[0].get('r_frame_rate') == '30/1',
        'frames': bool(v) and int(v[0].get('nb_frames', 0)) == int(round(dur * K.FPS)),
        'audio_aac_48k': bool(a) and a[0].get('codec_name') == 'aac' and a[0].get('sample_rate') == '48000',
        'duration': abs(rep['format_duration'] - dur) < 0.05,
        'loudness_-18': rep['loudness_lufs'] is not None and abs(rep['loudness_lufs'] + 18.0) < 0.6,
        'true_peak': rep['true_peak_dbfs'] is not None and rep['true_peak_dbfs'] <= -1.0,
    }
    print(json.dumps({k: rep[k] for k in ('format_duration', 'loudness_lufs', 'true_peak_dbfs', 'checks')},
                     indent=1))
    return rep


def selftest():
    os.makedirs(K.SELFTEST, exist_ok=True)
    out = []
    for lk in ('neon', 'amber', 'airy'):
        u8 = hero_still(lk, samples=1)
        out.append(K.save_png(os.path.join(K.SELFTEST, 'demo_looks_%s.png' % lk), u8))
        print('wrote', out[-1])
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
    elif args[0] == 'selftest':
        selftest()
    elif args[0] == 'heroes':
        n = int(args[args.index('--samples') + 1]) if '--samples' in args else 3
        looks = [a for a in args[1:] if a in SCENES] or ('neon', 'amber', 'airy')
        render_heroes(n, looks=looks)
    elif args[0] == 'clip':
        build_and_render_clip()
    else:
        print(__doc__)
