"""kit_demo.py: worked example / template of a Floret piece built on the installed toolkit (kit.py).

4 s, 1248 x 1248 @ 60: the 3D logo with orbiting market names, a General Sans extruded wordmark with a light
sweep, then a glass dashboard swings in. Copy this file to start a new Floret module.

    python3 kit.py sheet kit_demo 8                           # contact sheet
    python3 kit.py render kit_demo                            # master + SFX mix (workspace4/kit_out/kit_demo/)
"""
import functools

import numpy as np

import kit
from kit import K, T, ui

DUR, LOOK, BPM = 4.0, 'gold', 120


@functools.lru_cache(maxsize=1)
def assets():
    return dict(
        ring=T.OrbitText('PSX  •  PMEX  •  GOLD  •  EQUITIES  •  COMMODITIES  •  ', 'flat',
                         px=34, fill='GOLD_HI', radius=360, tilt=22, roll=-8),
        word=T.render('FLORET CAPITALS', 'extrude3d_gold', px=92, tracking=0.08),
        win=ui.app_window(w=900, h=700, look=LOOK, title='floretcapitals.com', header='Markets', sub='PSX · PMEX',
                          icons=('home', 'chart', 'globe', 'shield', 'settings'), active=1),
        dust=K.Particles(110, seed=5, bright=0.8, colors=[K.C['GOLD_HI'], K.C['GOLD'], K.C['CHAMPAGNE']]))


def prewarm():
    assets()


def draw(t):
    A = assets()
    cam = K.Cam.orbit((0, 0, 0), 1500, yaw=K.lerp(6, -3, K.EASE['easy_ease'](t / DUR)), pitch=3, aperture=18)
    cv = K.background(LOOK, t, cam)
    out = K.ramp(t, 2.0, 2.6, 'in_expo')                         # logo section clears before the window arrives
    if out < 1:
        c = (0, -60 - 120 * out, 0)
        A['ring'].draw(cv, cam, c, t=t, part='back', opacity=1 - out)
        lg = kit.obj('logo', t=min(t, 3.9), loop='hold', scale=0.55)
        if lg is not None:
            xy, _ = cam.project(np.array([c], np.float64))
            K.draw(cv, lg, xy[0][0], xy[0][1], opacity=K.ramp(t, 0.0, 0.4) * (1 - out), blur=8 * out)
        A['ring'].draw(cv, cam, c, t=t, part='front', opacity=1 - out)
        A['word'].draw(cv, K.CX, K.H * 0.80 - 80 * out, opacity=K.ramp(t, 0.5, 0.9) * (1 - out),
                       sweep=K.ramp(t, 0.9, 1.8, 'inout_sine'))
    u = K.ramp(t, 2.4, 3.4, 'out_expo')
    if u > 0:
        win = A['win']
        x, y, sw, sh = win.meta['slot']
        face = win.face_at(sweep=(t * 0.4) % 1.0)
        bars = ui.bar_chart([42, 55, 48, 66, 73, 81], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                            grow=[K.ramp(t, 2.8 + 0.08 * i, 3.4 + 0.08 * i, 'out_back') for i in range(6)],
                            active=5, w=sw, h=380, look=LOOK, fmt=lambda v: '')
        win.put(face, bars, x - 32, y + 20 - 32)
        win.plane(cv, cam, (0, 40 + 260 * (1 - u), 60), 900, rot=(10 + 30 * (1 - u), 12 * (1 - u), -1), face=face)
    A['dust'].draw(cv, cam, t)
    return cv


def post(cv, t):
    return K.post(cv, LOOK, t, flash=0.25 * K.impulse(t, 2.45))


def samples(t):
    return 5 if 2.3 < t < 2.7 else 3


def cues():
    return [dict(t=0.4, name='logo_sting'), dict(t=0.9, name='shimmer'), dict(t=2.45, name='whoosh_fast'),
            dict(t=3.0, name='bar_grow', align='start', params=dict(duration=0.6)), dict(t=3.4, name='ui_click')]
