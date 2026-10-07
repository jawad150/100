"""reel_demo.py: 3-second end-to-end test reel for render.py (not a deliverable).

Animated neon backdrop, a graded footage card (c01) flying in on a 3D plane with real motion blur, a
glowing ring behind it, floating glass chips at several depths (depth of field), drifting dust bokeh,
a light-leak sweep with flash on the landing beat, and the neon finishing stack.

    python3 render.py reel_demo --sheet 12
    python3 render.py reel_demo
"""
import functools
import math

import numpy as np

import core as K
import footage as F

DUR = 3.0
LOOK = 'neon'
BPM = 120
LAND = 1.0            # card lands on beat 2

CARD_W, CARD_H, PAD = 720, 1000, 48

_cam_pos = K.Track([(0.0, (0, 0, -1780)), (DUR, (0, -40, -1420))], ease=K.influence(80, 80))
_cam_yaw = K.Track([(0.0, 6.0), (DUR, -1.5)], ease=K.influence(80, 80))
_card_z = K.Track([(0.12, 3400.0), (LAND, 0.0, 'linear'), (DUR, -60.0)], ease='out_expo')
_card_pos = K.Track([(0.12, (520, -380)), (LAND, (0, -30))], ease='out_quint')
_card_rot = K.Track([(0.12, (24, 62, -18)), (LAND + 0.25, (3, -7, 2)), (DUR, (2, -10, 1))], ease='out_expo')


@functools.lru_cache(maxsize=1)
def _dust():
    return K.Particles(170, seed=7, bright=0.9)


@functools.lru_cache(maxsize=1)
def _card_frame():
    """Static parts of the card: rounded mask and a neon MAGENTA->ORANGE edge glow (padded)."""
    a = K.rrect_alpha(CARD_W, CARD_H, 46, PAD)
    d = K.rrect_sdf(CARD_W, CARD_H, 46, PAD)
    stroke = np.clip(1.5 - np.abs(d + 1.0), 0, 1)
    grad = K.gradient(a.shape[1], a.shape[0], [K.C['HOT_PINK'], K.C['MAGENTA'], K.C['ORANGE']], angle=35)
    edge = np.zeros(a.shape + (4,), np.float32)
    edge[..., :3] = grad * (stroke * 1.6)[..., None]
    edge[..., 3] = stroke * 0.9
    halo = K.gblur(np.ascontiguousarray(edge[..., :3]), 14, border='constant') * 1.2
    edge[..., :3] += halo
    return a, edge


@functools.lru_cache(maxsize=1)
def _chips():
    out = []
    for i, (w, h, col) in enumerate([(260, 96, 'MAGENTA'), (200, 80, 'ORANGE'), (300, 110, 'HOT_PINK'),
                                     (180, 70, 'AMBER'), (240, 90, 'MAGENTA'), (160, 64, 'ORANGE')]):
        a = K.rrect_alpha(w, h, h / 2, 20)
        g = K.gradient(a.shape[1], a.shape[0], [K.C['WHITE'] * 0.10, K.C['WHITE'] * 0.03], angle=-90)
        spr = np.dstack([g * a[..., None], a * 0.55]).astype(np.float32)
        dot = K.disc(h * 0.18, K.C[col] * 2.0)
        K.draw(spr, dot, 20 + h * 0.5, 20 + h / 2)
        bar = np.dstack([np.ones((10, int(w * 0.45), 3), np.float32) * 0.55, np.ones((10, int(w * 0.45)), np.float32)])
        K.draw(spr, bar, 20 + h * 0.95 + w * 0.22, 20 + h / 2)
        out.append(K.glow(spr, K.C[col], (6, 22), 0.35))
    return out


_CHIP_POS = [(-300, -700, 700), (330, -820, 1500), (-360, 640, 300), (300, 560, -450), (-150, 1150, 2200),
             (250, -380, -800)]


@functools.lru_cache(maxsize=1)
def _ring():
    return K.glow(K.ring(300, 5, K.C['HOT_PINK'] * 2.2), K.C['MAGENTA'], (8, 30, 80), 1.2)


def prewarm():
    F.Clip('c01').get(4.0, CARD_W, CARD_H, look=LOOK)
    _card_frame(), _chips(), _ring(), _dust()
    K.background(LOOK, 0.0, K.Cam())


def camera(t):
    p = _cam_pos(t)
    dx = K.wiggle(t, 0.35, 8, seed=3)
    dy = K.wiggle(t, 0.3, 6, seed=4)
    land = K.impulse(t, LAND, decay=9.0)
    sx, sy, sr = K.shake(t, 14 * land, 16, seed=9)
    return K.Cam(pos=(p[0] + dx + sx, p[1] + dy + sy, p[2]), yaw=_cam_yaw(t), roll=sr, aperture=38,
                 focus_dist=-p[2])


def card_sprite(t):
    clip = F.Clip('c01')
    src = 4.0 + t * 0.9
    foot = clip.get(src, CARD_W, CARD_H, zoom=1.06 + 0.04 * t, look=LOOK)
    a, edge = _card_frame()
    spr = edge.copy()
    inner = spr[PAD:PAD + CARD_H, PAD:PAD + CARD_W]
    m = a[PAD:PAD + CARD_H, PAD:PAD + CARD_W, None]
    inner *= 1.0 - m
    inner += foot * m
    # glass sheen + edge light on top
    spr += edge * np.float32(0.6)
    return spr


def draw(t):
    cam = camera(t)
    beat = K.beat_pulse(t, BPM, decay=5.0)
    cv = K.background(LOOK, t, cam, boost=0.25 * beat)
    sc = K.Scene(cam)
    z = _card_z(t)
    x, y = _card_pos(t)
    rx, ry, rz = _card_rot(t)
    fl = math.sin(t * 1.3) * 10
    sc.plane(_ring(), (0, -30, z + 260), 1900 * (0.85 + 0.15 * K.ramp(t, 0.6, LAND + 0.4)), mode='over',
             opacity=K.ramp(t, 0.5, LAND + 0.2, 'out_cubic'))
    sc.plane(card_sprite(t), (x, y + fl, z), CARD_W + 2 * PAD, rot=(rx, ry, rz))
    for i, (spr, (px, py, pz)) in enumerate(zip(_chips(), _CHIP_POS)):
        a = K.ramp(t, 0.3 + 0.12 * i, 0.9 + 0.12 * i, 'out_expo')
        sc.billboard(spr, (px, py + 30 * math.sin(t * 0.9 + i), pz + (1 - a) * 900), spr.shape[1] * 1.2,
                     opacity=a)
    sc.particles(_dust(), t)
    sc.render(cv)
    return cv


def post(cv, t):
    land = K.impulse(t, LAND, decay=7.0, attack=0.02)
    flight = K.ramp(t, 0.12, 0.5, 'out_cubic') * (1 - K.ramp(t, 0.8, LAND, 'out_cubic'))
    if 0.85 < t < 1.6:
        K.light_leak(cv, t, strength=0.75 * land + 0.1, seed=2, sweep=K.ramp(t, 0.9, 1.5, 'inout_sine'))
    return K.post(cv, LOOK, t, flash=0.35 * land, chroma=1.8 + 9 * flight + 5 * land)


def samples(t):
    return 7 if 0.12 <= t <= LAND + 0.2 else 3


def cues():
    return [{'t': 0.12, 'sfx': 'whoosh_in', 'gain_db': -3},
            {'t': LAND, 'sfx': 'impact_glass', 'gain_db': 0},
            {'t': LAND + 0.02, 'sfx': 'sub_drop', 'gain_db': -4},
            {'t': 2.0, 'sfx': 'shimmer', 'gain_db': -8}]
