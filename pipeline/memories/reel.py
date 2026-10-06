"""Yaadein (Spider-Man) reel - master timeline compositor, 1080x1920 @ 60 fps.

python3 reel.py still <t> [<t> ...]          -> scratch stills for checking
python3 reel.py render [workers]             -> workspace2/out/yaadein_60fps.mp4 (with audio)
python3 reel.py cues                         -> workspace2/work/cues.json (sound design cue sheet)
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anim as A  # noqa: E402
import captions as K  # noqa: E402
import comp as C  # noqa: E402
import ending as E  # noqa: E402
import fx  # noqa: E402
import hud as U  # noqa: E402
from script import LINES  # noqa: E402

FPS = C.FPS
DUR = 32.0
NF = int(DUR * FPS)
WORK = C.ROOT + '/work'
OUT = C.ROOT + '/out'
T_END = 24.6

SHOTS = [('a1', 0.00, 0.80), ('a2', 0.80, 1.55), ('a4', 1.55, 2.20), ('b2', 2.20, 3.40), ('b1', 3.40, 5.00),
         ('a1b', 5.00, 6.30), ('dive', 6.30, 7.40), ('c1', 7.40, 9.40), ('c2', 9.40, 10.80), ('c3', 10.80, 12.30),
         ('d1', 12.30, 13.50), ('d2', 13.50, 14.50), ('d3', 14.50, 15.40), ('d4', 15.40, 15.90), ('e1', 15.90, 16.80),
         ('boom', 16.80, 17.20), ('e3', 17.20, 18.70), ('mont', 18.70, 19.70), ('f1', 19.70, 21.20),
         ('f2', 21.20, 22.60), ('g1', 22.60, T_END), ('end', T_END, DUR)]
LOOK = dict(a1='spider', a2='spider', a4='spider', b2='spider', b1='spider', a1b='spider', dive='memory', c1='memory',
            c2='memory', c3='memory', d1='spider', d2='spider', d3='spider', d4='spider', e1='spider', boom='spider',
            e3='spider', mont='spider', f1='dawn', f2='dawn', g1='dawn', end='orange')


# ================================================================== helpers
def blank():
    return np.zeros((C.H, C.W, 3), np.float32)


def put_plate(cv, name, layer, cam, depth, **kw):
    if fx.has_layer(name, layer):
        C.draw_plate(cv, fx.plate(name, layer), cam, depth, **kw)


def layered(cv, name, cam, d_bg=8.0, d_hero=5.0, d_fg=1.4, fg_op=1.0):
    """bg/hero/fg plates at their depths (falls back to the single 'full' plate)."""
    if fx.has_layer(name, 'bg'):
        put_plate(cv, name, 'bg', cam, d_bg)
        put_plate(cv, name, 'hero', cam, d_hero)
        if fx.has_layer(name, 'fg'):
            put_plate(cv, name, 'fg', cam, d_fg, opacity=fg_op)
    else:
        put_plate(cv, name, 'full', cam, d_hero)
    return cv


CLIPS = {}


def clip(name):
    if name not in CLIPS:
        CLIPS[name] = fx.Clip(name)
    return CLIPS[name]


def clip_frame(cv, name, u, speed=1.0, cam=None, depth=4.0, start=1):
    c = clip(name)
    img = c.frame(start + u * FPS * speed)
    if img is None:
        return cv
    if cam is None:
        cv[..., :3] = fx.fit_frame(img)
    else:
        C.draw_plate(cv, img, cam, depth)
    return cv


# floating memories (3D polaroids drifting through the night ruins)
POL = None


def polaroids():
    global POL
    if POL is None:
        keys = []
        for n, crop in (('c2_mj_portrait', (0.05, 0.12, 0.95, 0.62)), ('c1_temple', (0.0, 0.15, 1.0, 0.7)),
                        ('c2_mj_portrait', (0.15, 0.25, 0.85, 0.6)), ('c1_temple', (0.1, 0.3, 0.9, 0.75))):
            try:
                keys.append(fx.polaroid_key(n, layer='hero' if n == 'c1_temple' and fx.has_layer(n, 'hero') and False else 'full',
                                            crop=crop, aged=0.5))
            except FileNotFoundError:
                pass
        rng = np.random.default_rng(11)
        POL = [dict(key=keys[i % len(keys)], p=rng.uniform((-2.2, -2.6, 1.0), (2.2, 2.6, 9.0)), rot=rng.uniform(-30, 30, 3),
                    w=rng.normal(0, 14, 3), v=rng.normal(0, 0.06, 3) + np.array([0, -0.12, 0])) for i in range(16)] if keys else []
    return POL


def draw_polaroids(cv, cam, t, alpha=1.0, near_boost=False):
    for q in polaroids():
        p = q['p'] + q['v'] * t
        rot = tuple(q['rot'] + q['w'] * t)
        C.draw_sprite3d(cv, q['key'], cam, tuple(p), (0.42, 0.5), rot, opacity=alpha)


RAIN_SHOTS = {'a1', 'a2', 'a4', 'b2', 'b1', 'a1b', 'e3'}


# ================================================================== shots (cv, t global, u local)
def s_a1(cv, t, u):
    # extreme close-up of the mask; lightning reveals it; slow push
    z = A.Track([(0, -0.35), (0.8, 0.25, A.EXPO_OUT)])(u)
    cam = C.Cam(0.02 * A.wiggle(t, 0.6, 1, 1), 0.015 * A.wiggle(t, 0.5, 1, 2), z, roll=A.wiggle(t, 0.3, 0.6, 3))
    put_plate(cv, 'a1_mask', 'full', cam, 3.0)
    cv *= 0.15 + 0.85 * A.ramp(u, 0.0, 0.08, A.LINEAR)
    fx.lightning(cv, t, 0.02, 3.0)
    return cv


def s_a2(cv, t, u):
    # behind-reveal: the pillar slides off as the camera trucks right
    k = A.Track([(0, 0.0), (0.75, 1.0, A.EXPO)])(u)
    cam = C.Cam(-0.55 + 1.1 * k, 0.05 * k, 0.15 * k, roll=-1.5 + 1.5 * k, focus=6.0, aperture=0.02)
    layered(cv, 'a2_reveal', cam, d_bg=9.0, d_hero=6.0, d_fg=1.5)
    draw_polaroids(cv, cam, t)
    return cv


def s_a4(cv, t, u):
    # crane: wide high shot pushing down/in over the ruins
    k = A.Track([(0, 0.0), (0.65, 1.0, A.SMOOTH)])(u)
    cam = C.Cam(0.0, 0.35 - 0.35 * k, 0.6 * k, roll=2 - 2 * k, focus=8, aperture=0.0)
    put_plate(cv, 'a4_wide', 'full', cam, 6.0)
    draw_polaroids(cv, C.Cam(0, 0.6 - 0.6 * k, 0.8 * k, focus=5, aperture=0.03), t + 1.2)
    return cv


def s_b2(cv, t, u):
    # close: his masked face looking down at the glowing photo; slow push + breathing
    z = A.Track([(0, 0.0), (1.2, 0.35, A.SMOOTH)])(u)
    cam = C.Cam(0.03 * math.sin(u * 1.3), 0.02 * math.sin(u * 0.9), z)
    put_plate(cv, 'b2_hands', 'full', cam, 3.5)
    return cv


def s_b1(cv, t, u):
    z = A.Track([(0, 0.0), (1.6, 0.3, A.SMOOTH)])(u)
    cam = C.Cam(-0.04 + 0.08 * A.SMOOTH(min(1, u / 1.6)), 0.0, z)
    put_plate(cv, 'b1_frame', 'full', cam, 3.0)
    return cv


def s_a1b(cv, t, u):
    # tight on the eyes while he decides
    z = A.Track([(0, 0.55), (1.3, 0.85, A.SMOOTH)])(u)
    cam = C.Cam(0.05, 0.12, z, roll=A.wiggle(t, 0.25, 0.5, 9))
    put_plate(cv, 'a1_mask', 'full', cam, 3.0)
    return cv


def s_dive(cv, t, u):
    # push into the photo in his hands -> it fills the frame -> becomes the warm memory (temple)
    k = A.Track([(0, 0.0), (0.85, 1.0, A.EXPO_IN)])(u)
    cam = C.Cam(0, 0.0, 0.3 + 2.4 * k)
    put_plate(cv, 'b1_frame', 'full', cam, 3.0)
    if u > 0.55:
        w = A.ramp(u, 0.55, 0.95, A.SMOOTH)
        mem = blank()
        put_plate(mem, 'c1_temple', 'bg' if fx.has_layer('c1_temple', 'bg') else 'full',
                  C.Cam(0, 0, -1.2 + 1.2 * A.EXPO_OUT(A.clamp((u - 0.55) / 0.55))), 6.0)
        cv[...] = cv * (1 - w) + mem * w
    cv[...] = fx.radial_blur(cv, 0.12 * math.sin(math.pi * A.clamp(u / 0.95)))
    cv += np.float32([1.0, 0.7, 0.45]) * 2.0 * math.exp(-((u - 0.78) / 0.09) ** 2)
    return cv


PETALS = fx.drift_particles(140, 5, ((-3, -2, 0.6), (3, 4, 8)), (0.15, -0.35, -0.05))


def petals(cv, cam, t):
    C.particles(cv, cam, PETALS(t), 0.007, (1.0, 0.55, 0.45), 0.9)


def s_c1(cv, t, u):
    k = A.Track([(0, 0.0), (2.0, 1.0, A.SMOOTH)])(u)
    cam = C.Cam(-0.25 + 0.5 * k, 0.05 * k, 0.4 * k, focus=6, aperture=0.015)
    layered(cv, 'c1_temple', cam, d_bg=10, d_hero=8, d_fg=1.2)
    petals(cv, cam, t)
    fx.light_leak(cv, t, 0.18, seed=3)
    return cv


def s_c2(cv, t, u):
    z = A.Track([(0, 0.0), (1.4, 0.32, A.SMOOTH)])(u)
    cam = C.Cam(0.04 * u, 0.0, z, focus=2.5, aperture=0.03)
    put_plate(cv, 'c2_mj_portrait', 'full', cam, 3.0)
    petals(cv, cam, t)
    return cv


def s_c3(cv, t, u):
    clip_frame(cv, 'c3_together', u)
    petals(cv, C.Cam(0, 0, 0, focus=3, aperture=0.03), t)
    return cv


def void_glow(cv, u):
    return cv


def s_d1(cv, t, u):
    clip_frame(cv, 'd1_lasso', u)
    return cv


def s_d2(cv, t, u):
    clip_frame(cv, 'd2_dagger', u)
    return cv


SHAT = {}


def s_d3(cv, t, u):
    # the memory freezes (desaturated, drained) -> the dagger stabs it on 'sach' -> it shatters to the Goblin
    T_HIT = 15.12 - 14.50
    if u < T_HIT:
        z = 0.15 + 0.05 * u
        put_plate(cv, 'c2_mj_portrait', 'full', C.Cam(0, 0, z), 3.0)
        lum = cv.mean(2, keepdims=True)
        dr = A.ramp(u, 0, 0.4)
        cv[...] = cv * (1 - 0.8 * dr) + lum * np.float32([0.55, 0.6, 0.75]) * 0.8 * dr
        # the dagger flies in
        if u > T_HIT - 0.16:
            q = (u - (T_HIT - 0.16)) / 0.16
            dimg = clip('d2_dagger').frame(clip('d2_dagger').last)
            if dimg is not None:
                cam = C.Cam(0, 0, 0, zoom=0.5 + 2.2 * A.EXPO_IN(q))
                tmp = blank()
                C.draw_plate(tmp, dimg, cam, 3.0)
                cv += tmp * 1.2
        return cv
    # after impact: goblin behind, shards in front
    ui = u - T_HIT
    gob = blank()
    put_plate(gob, 'd4_goblin', 'full', C.Cam(0, 0, 0.1 + 0.15 * ui), 3.0)
    cv[...] = gob
    if 'img' not in SHAT:
        src = blank()
        put_plate(src, 'c2_mj_portrait', 'full', C.Cam(0, 0, 0.15 + 0.05 * T_HIT), 3.0)
        lum = src.mean(2, keepdims=True)
        src = src * 0.2 + lum * np.float32([0.55, 0.6, 0.75]) * 0.8
        SHAT['img'] = fx.Shatter(src, n=80, center=(560, 860))
    SHAT['img'].draw(cv, C.Cam(0, 0, 0), ui)
    cv += np.float32([1.0, 0.9, 0.85]) * 1.6 * math.exp(-ui * 26)
    return cv


def s_d4(cv, t, u):
    z = A.Track([(0, 0.25), (0.5, 0.55, A.EXPO_OUT)])(u)
    put_plate(cv, 'd4_goblin', 'full', C.Cam(0, 0, z, roll=A.wiggle(t, 2, 1.2, 4)), 3.0)
    return cv


def s_e1(cv, t, u):
    clip_frame(cv, 'e1_bomb', u)
    return cv


def s_boom(cv, t, u):
    put_plate(cv, 'e3_kneel', 'full', C.Cam(0, 0, 0.2), 4.0)
    cv *= 0.25
    fx.fireball(cv, u, (560, 900), 1.1)
    return cv


EMBERS = fx.drift_particles(160, 9, ((-3, -3, 1.0), (3, 3, 9)), (0.08, 0.45, 0.0))


def s_e3(cv, t, u):
    z = A.Track([(0, -0.1), (1.5, 0.35, A.SMOOTH)])(u)
    cam = C.Cam(0.06 * math.sin(u * 0.8), 0.0, z, focus=4.5, aperture=0.03)
    put_plate(cv, 'e3_kneel', 'full', cam, 4.5)
    C.particles(cv, cam, EMBERS(t), 0.012, (1.0, 0.35, 0.06), 1.2)
    return cv


MONT = [('a1_mask', 0.0, 0.2), ('c2_mj_portrait', 0.2, 0.36), ('d4_goblin', 0.36, 0.52), ('b2_hands', 0.52, 0.66),
        ('c1_temple', 0.66, 0.78), ('logo', 0.78, 1.0)]


def s_mont(cv, t, u):
    for name, a, b in MONT:
        if a <= u < b:
            uu = u - a
            if name == 'logo':
                clip_frame(cv, 'logo_spin', uu, start=max(1, clip('logo_spin').last - 26))
            else:
                lay = 'full' if fx.has_layer(name, 'full') else 'bg'
                put_plate(cv, name, lay, C.Cam(0, 0, 0.35 + 0.6 * uu, roll=6 * (uu - 0.08)), 3.0)
                if name in ('c2_mj_portrait', 'c1_temple'):
                    lum = cv.mean(2, keepdims=True)
                    cv[...] = cv * 0.4 + lum * 0.6
            cv += 1.6 * math.exp(-uu * 30)                           # flash frame on every cut
            break
    return cv


def s_f1(cv, t, u):
    k = A.Track([(0, 0.0), (1.5, 1.0, A.SMOOTH)])(u)
    cam = C.Cam(0.3 - 0.45 * k, 0.0, 0.1 + 0.35 * k, focus=3.0, aperture=0.025)
    layered(cv, 'f1_grave', cam, d_bg=7, d_hero=3.0, d_fg=0.9)
    return cv


def s_f2(cv, t, u):
    z = A.Track([(0, 0.0), (1.4, 0.4, A.SMOOTH)])(u)
    put_plate(cv, 'f2_rose', 'full', C.Cam(0, -0.04 * u, z), 2.0)
    return cv


def s_g1(cv, t, u):
    clip_frame(cv, 'g1_sunrise', u)
    # sun burst behind him + anamorphic flare
    k = A.ramp(u, 0.2, 1.6, A.SMOOTH)
    yy, xx = fx._yx()
    sx, sy = 640 - 80 * k, 820
    g = np.exp(-((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * 220.0 ** 2)).astype(np.float32)
    cv += cv2.resize(g, (C.W, C.H))[..., None] * np.float32([1.0, 0.55, 0.25]) * 0.8 * k
    return cv


def s_end(cv, t, u):
    prev = None
    if u < 1.2:
        prev = blank()
        clip_frame(prev, 'g1_sunrise', T_END - 22.6)
    return E.draw(cv, u, prev)


DRAW = {k: globals()['s_' + k] for k, _, _ in SHOTS}


# ================================================================== captions & HUD
def phrases():
    words = [(w.lstrip('*'), t, w.startswith('*')) for line in LINES for (w, t) in line]

    def sel(a, b):
        return [w for w in words if a <= w[1] < b]
    # Instagram safe area: x 70..950, y 250..1470 (bottom UI + right-hand buttons stay clear)
    low = lambda y, amp=55: K.Path(K.bezier([(80, y), (320, y - amp), (640, y + amp), (945, y - 10)]))  # noqa: E731
    high = lambda y, amp=45: K.Path(K.bezier([(80, y + 10), (360, y - amp), (660, y + amp), (945, y)]))  # noqa: E731
    P = [
        (sel(0.7, 2.1), low(1330), 2.12),
        (sel(2.1, 3.0), low(1350), 3.55),
        (sel(3.8, 5.3), low(1340), 5.33),
        (sel(5.3, 6.3), high(380), 6.30),
        (sel(6.3, 6.5), K.Path(K.bezier([(240, 1000), (420, 940), (660, 1060), (850, 1000)])), 7.15),
        (sel(8.2, 10.0), low(1350), 10.30),
        (sel(10.4, 12.3), low(1350), 12.28),
        (sel(12.3, 13.0), low(1340), 14.40),
        (sel(14.5, 16.0), low(1350), 15.95),
        (sel(19.7, 21.0), high(400), 20.98),
        (sel(21.0, 22.5), high(400), 22.95),
    ]
    out = []
    for ws, path, t_out in P:
        if ws:
            sc = 1.45 if len(ws) == 1 else 1.0
            out.append(K.Phrase(ws, path, t_out, scale=sc))
    return out


PH = None


def draw_captions(cv, t):
    global PH
    if PH is None:
        PH = phrases()
    for p in PH:
        p.draw(cv, t)


PHOTO_KEY = 'mjphoto'


def hud_layer(cv, t, fr):
    """Spider-HUD panels as 3D planes (frosted glass over the frame)."""
    cam = C.Cam(0, 0, 0)
    if PHOTO_KEY not in U._PHOTOS and fx.has_layer('c2_mj_portrait', 'full'):
        ph = C.to_srgb(fx.plate('c2_mj_portrait')[..., :3])
        h, w = ph.shape[:2]
        U.set_photo(PHOTO_KEY, np.ascontiguousarray(ph[int(h * 0.12):int(h * 0.12) + w, :]))
    # memory card (3.9 - 5.0): flips in on a spring
    if 3.85 < t < 5.15:
        u = t - 3.85
        s = A.spring(u, 1.8, 0.55)
        out = A.ramp(t, 4.95, 5.15, A.EXPO_IN)
        img = U.memory_card(u, PHOTO_KEY)
        C.draw_img3d(cv, img, cam, (0.0, 0.98 + 0.3 * out, 3.0), (1.2, 1.2 * img.shape[0] / img.shape[1]),
                     (0, (1 - s) * 70 + out * -40, (1 - s) * -8), opacity=min(1.0, u * 4) * (1 - out), glass=(fr, 1.0))
    # delete dialog + cursor (5.0 - 6.3)
    if 4.98 < t < 6.42:
        u = t - 4.98
        s = A.spring(u, 1.9, 0.6)
        out = A.ramp(t, 6.24, 6.42, A.EXPO_IN)
        # cursor path: bottom-right -> Delete (hover) -> hesitates -> back to Cancel -> click
        # button centres on the 1.3 m wide dialog plane: Delete (+0.27, -0.24), Cancel (-0.27, -0.24)
        cur = A.Track([(0.0, (0.85, -1.3)), (0.45, (0.30, -0.25), A.SMOOTH), (0.62, (0.25, -0.23)),
                       (0.95, (0.29, -0.26), A.SMOOTH), (1.18, (-0.24, -0.24), A.EXPO), (1.44, (-0.24, -0.24))])(u)
        hover = A.clamp(1 - math.hypot(cur[0] - 0.27, cur[1] + 0.24) / 0.1)
        chover = A.clamp(1 - math.hypot(cur[0] + 0.25, cur[1] + 0.24) / 0.1)
        press = A.clamp(1 - abs(u - 1.26) / 0.06)
        img = U.delete_dialog(u, hover, 0, chover)
        C.draw_img3d(cv, img, cam, (0, -0.1, 3.0), (1.3, 1.3 * img.shape[0] / img.shape[1]),
                     ((1 - s) * -50, (1 - s) * 12, 0), opacity=min(1.0, u * 5) * (1 - out), glass=(fr, 1.0))
        if u > 0.1:
            cs = U.cursor()
            C.draw_img3d(cv, cs, cam, (cur[0] + 0.035, cur[1] - 0.05, 2.95), (0.07 * (1 - 0.1 * press), 0.098 * (1 - 0.1 * press)),
                         (0, 0, 0), opacity=(1 - out))
    # happiness meter (10.3 -> crash on 'sach' 15.12)
    if 10.25 < t < 15.6:
        u = t - 10.25
        val = 92 * A.ramp(t, 10.3, 10.95, A.EXPO_OUT)
        crash = A.ramp(t, 15.12, 15.3)
        val = val * (1 - A.ramp(t, 15.12, 15.45, A.EXPO_OUT))
        s = A.spring(u, 1.6, 0.6)
        out = A.ramp(t, 15.45, 15.6)
        img = U.meter(u, val, 'KHUSHI', crash)
        C.draw_img3d(cv, img, cam, (0.42 + 0.02 * A.ramp(t, 13.55, 13.9, A.SMOOTH), 0.98 - 0.42 * A.ramp(t, 13.55, 13.9, A.SMOOTH), 3.0), (0.48 * s, 0.48 * s), (0, -14, 0),
                     opacity=min(1.0, u * 4) * (1 - out), glass=(fr, 1.0))
    # truth check (13.7 - 15.4)
    if 13.7 < t < 15.5:
        u = t - 13.7
        prog = A.ramp(t, 13.8, 15.05, A.SMOOTH)
        res = A.ramp(t, 15.12, 15.3)
        s = A.spring(u, 1.8, 0.6)
        out = A.ramp(t, 15.35, 15.5)
        img = U.truth_check(u, prog, res)
        C.draw_img3d(cv, img, cam, (-0.05, 1.12, 3.0), (1.15, 1.15 * img.shape[0] / img.shape[1]),
                     ((1 - s) * 60, 0, 0), opacity=min(1.0, u * 4) * (1 - out), glass=(fr, 1.0))
    return cv


# ================================================================== frame
def shot_at(t):
    for k, a, b in SHOTS:
        if a <= t < b:
            return k, a, b
    return SHOTS[-1]


RAIN_CAM = C.Cam(0, 0, 0)

# cut transitions: (time, kind, half-width s)
TRANS = [(0.80, 'whip', 0.09), (1.55, 'zoom', 0.10), (2.20, 'flash', 0.06), (3.40, 'leak', 0.25), (5.00, 'whip', 0.08),
         (7.40, 'leak', 0.35), (9.40, 'dissolve', 0.22), (10.80, 'whip', 0.08), (12.30, 'glitch', 0.12),
         (13.50, 'spin', 0.1), (15.90, 'zoom', 0.1), (17.20, 'flash', 0.08), (19.70, 'dip', 0.22),
         (21.20, 'dissolve', 0.25), (22.60, 'leak', 0.3)]


def shot_draw(k, t):
    for kk, a, b in SHOTS:
        if kk == k:
            cv = blank()
            DRAW[k](cv, t, t - a)
            return cv


def transitions(cv, t):
    for T, kind, w in TRANS:
        dt = t - T
        if abs(dt) > w:
            continue
        bump = math.exp(-(dt / (w * 0.45)) ** 2)
        if kind == 'whip':
            cv[...] = fx.whip(cv, 160 * bump, 0)
            cv[...] = np.roll(cv, int(90 * bump * (-1 if dt < 0 else 1)), axis=1)
        elif kind == 'spin':
            M = cv2.getRotationMatrix2D((C.W / 2, C.H / 2), 25 * bump * (1 if dt < 0 else -1), 1 + 0.15 * bump)
            cv[...] = cv2.warpAffine(cv, M, (C.W, C.H), borderMode=cv2.BORDER_REFLECT)
            cv[...] = fx.radial_blur(cv, 0.06 * bump)
        elif kind == 'zoom':
            cv[...] = fx.radial_blur(cv, 0.22 * bump)
            cv += 0.25 * bump
        elif kind == 'flash':
            cv += np.float32([1.0, 0.92, 0.88]) * 2.2 * bump
        elif kind == 'leak':
            fx.light_leak(cv, t, 1.2 * bump, colors=((1.0, 0.22, 0.04), (1.0, 0.55, 0.18)), seed=int(T * 10))
        elif kind == 'glitch':
            cv[...] = U.glitch(cv, 1.6 * bump, t, seed=int(T))
        elif kind == 'dip':
            cv *= 1 - 0.95 * bump
        elif kind == 'dissolve' and dt < 0:
            nxt = None
            for kk, a, b in SHOTS:
                if abs(a - T) < 1e-6:
                    nxt = kk
            if nxt:
                mix = 0.5 * (1 + dt / w)
                cv[...] = cv * (1 - mix) + shot_draw(nxt, t) * mix
        elif kind == 'dissolve' and dt >= 0:
            prv = None
            for kk, a, b in SHOTS:
                if abs(b - T) < 1e-6:
                    prv = kk
            if prv:
                mix = 0.5 * (1 - dt / w)
                cv[...] = cv * (1 - mix) + shot_draw(prv, t) * mix
    return cv


def draw(t):
    k, a, b = shot_at(t)
    cv = blank()
    DRAW[k](cv, t, t - a)
    transitions(cv, t)
    if k in RAIN_SHOTS:
        C.rain(cv, RAIN_CAM, t, n=650, opacity=0.25)
    if k != 'end':
        if 3.8 < t < 15.6:
            fr = C.frosted(cv)
            hud_layer(cv, t, fr)
        draw_captions(cv, t)
    return cv


def samples_for(t):
    k, a, b = shot_at(t)
    u = t - a
    if k in ('dive', 'boom', 'mont', 'e1', 'd3'):
        return 6
    if any(abs(t - T) < w for T, kind, w in TRANS if kind in ('whip', 'spin', 'zoom')):
        return 6
    if u < 0.12 or b - t < 0.12:
        return 5
    return 3


def finish_frame(f, t):
    k, a, b = shot_at(t)
    f = C.bloom(f, 0.85, 0.35)
    f = C.halation(f, 0.14)
    if k not in ('end',):
        f = C.anamorphic(f, 1.4, 0.18, (0.35, 0.55, 1.0) if LOOK[k] != 'memory' else (1.0, 0.6, 0.3))
    look = LOOK[k]
    if look == 'dawn':
        s = C.grade(f, 'memory', exposure=0.05, sat=1.05, contrast=1.06, vignette=0.6)
    elif look == 'orange':
        s = C.grade(f, 'orange', vignette=0.45)
    else:
        s = C.grade(f, look, exposure=0.0, sat=1.0 if look == 'spider' else 1.05, contrast=1.08, vignette=0.6)
    # cut flashes / dips between shots (1 frame) are inside the shots; global fade in
    s *= A.ramp(t, 0.0, 0.05, A.LINEAR) * 0.0 + 1.0
    s = C.grain(s, t, 0.02)
    return s


def render_frame(i):
    t = i / FPS
    f = C.render_frame(draw, t, samples_for(t))
    return finish_frame(f, t)


# ================================================================== output
def still(ts):
    os.makedirs(WORK + '/stills', exist_ok=True)
    for t in ts:
        s = render_frame(int(round(t * FPS)))
        cv2.imwrite(f'{WORK}/stills/t{t:06.2f}.jpg', (s[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])


def _chunk(args):
    ci, i0, i1 = args
    path = f'{WORK}/chunks/c{ci:03d}.mp4'
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{C.W}x{C.H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                          '-x264-params', 'rc-lookahead=8:sync-lookahead=0', '-threads', '2', '-pix_fmt', 'yuv420p',
                          path + '.part.mp4'], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        s = render_frame(i)
        p.stdin.write((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    os.replace(path + '.part.mp4', path)
    return path


def render(workers=4, chunk=60):
    os.makedirs(WORK + '/chunks', exist_ok=True)
    jobs = [(ci, i0, min(NF, i0 + chunk)) for ci, i0 in enumerate(range(0, NF, chunk))]
    with Pool(workers) as pool:
        paths = pool.map(_chunk, jobs, chunksize=1)
    lst = WORK + '/chunks/list.txt'
    with open(lst, 'w') as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    os.makedirs(OUT, exist_ok=True)
    video = WORK + '/video_60.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    return video


# ================================================================== sound design cue sheet
def cues():
    c = []

    def add(t, kind, g, **kw):
        c.append([round(t, 3), kind, g, kw] if kw else [round(t, 3), kind, g])
    # hook
    add(0.0, 'braam', 1.0)
    add(0.0, 'sub_drop', 0.9)
    add(0.02, 'thunder', 0.75)
    add(0.0, 'rain_bed', 0.32, d=7.5)
    add(0.74, 'whoosh', 0.75, d=0.5, sweep=(-0.8, 0.8))
    add(0.80, 'impact', 0.35)
    add(1.50, 'whoosh_slow', 0.55)
    add(2.16, 'impact', 0.45)
    add(2.25, 'heartbeat', 0.65, n=2)
    add(3.05, 'reverse_swell', 0.6)
    # memory card / dialog / cursor
    add(3.86, 'pop', 0.55)
    add(3.95, 'ticks', 0.35, n=12)
    add(5.00, 'pop', 0.6)
    for tt in (5.42, 5.6, 5.95):
        add(tt, 'click', 0.25)
    add(6.24, 'click', 0.7)
    add(6.25, 'riser', 0.55, d=0.9)
    add(7.05, 'impact', 0.35)
    add(7.08, 'shimmer', 0.6)
    add(7.4, 'chimes', 0.45, d=4.6, n=10)
    add(7.4, 'wind', 0.18, d=4.9)
    # warm memory
    add(8.0, 'whoosh_slow', 0.3)
    add(10.25, 'pop', 0.4)
    add(10.32, 'ticks', 0.3, n=14, gap=0.04)
    add(10.82, 'shimmer', 0.55, d=1.4)
    add(10.78, 'whoosh', 0.4, d=0.6, sweep=(0.6, -0.6))
    # truth
    add(12.28, 'reverse_swell', 0.55)
    add(12.30, 'sub_drop', 0.7)
    add(12.32, 'glitch', 0.35)
    add(12.3, 'rope', 0.5, d=1.2, n=4)
    add(13.45, 'whoosh', 0.6, d=0.45, sweep=(-0.5, 0.5))
    add(13.5, 'blade', 0.8)
    add(13.55, 'shimmer', 0.35, d=0.9)
    add(13.72, 'ticks', 0.28, n=24, gap=0.05)
    add(14.95, 'whoosh', 0.8, d=0.2, sweep=(0.0, 0.0))
    add(15.12, 'glass', 1.0)
    add(15.12, 'impact', 0.85)
    add(15.13, 'glitch', 0.55)
    add(15.14, 'buzz', 0.5)
    add(15.38, 'braam', 0.9)
    # bomb + explosion
    add(15.88, 'whoosh', 0.7, d=0.8, sweep=(0.3, -0.3))
    add(16.2, 'ticks', 0.3, n=10, gap=0.06)
    add(16.80, 'impact', 1.0)
    add(16.80, 'sub_drop', 1.0)
    add(16.82, 'fire', 0.6, d=3.0)
    add(16.85, 'tinnitus', 0.6, d=2.0)
    add(16.9, 'glass', 0.35)
    add(17.2, 'rain_bed', 0.3, d=2.6)
    add(17.25, 'heartbeat', 0.7, n=2, bpm=52)
    # montage
    for tt in (18.70, 18.90, 19.06, 19.22, 19.36, 19.48):
        add(tt, 'impact', 0.35)
        add(tt, 'glitch', 0.18)
    add(19.48, 'thwip', 0.6)
    # dawn burial
    add(19.62, 'reverse_swell', 0.5)
    add(19.72, 'whoosh_slow', 0.35)
    add(19.7, 'wind', 0.3, d=5.2)
    add(19.9, 'fire', 0.18, d=2.6)
    add(20.2, 'chimes', 0.18, d=3.0, n=4)
    add(21.72, 'sub_drop', 0.45)
    add(21.75, 'shimmer', 0.35)
    # sunrise
    add(22.0, 'riser', 0.5, d=1.2)
    add(22.6, 'impact', 0.5)
    add(22.62, 'shimmer', 0.6, d=2.0)
    # end card
    add(T_END + 0.0, 'whoosh_slow', 0.5)
    add(T_END + 0.1, 'shimmer', 0.45, d=1.2)
    add(T_END + E.T_EXPAND - 0.05, 'whoosh', 0.7, d=0.9, sweep=(-0.4, 0.4))
    add(T_END + E.T_BURN, 'reverse_swell', 0.5)
    add(T_END + E.T_GRAD, 'impact', 0.45)
    add(T_END + E.T_AVATAR + 0.02, 'pop', 0.5)
    add(T_END + E.T_USER, 'ticks', 0.4, n=10, gap=0.045)
    add(T_END + E.T_Q, 'whoosh', 0.35, d=0.6)
    add(T_END + E.T_CTA2, 'pop', 0.35)
    add(T_END + E.T_CLICK, 'click', 0.8)
    add(T_END + E.T_CLICK + 0.03, 'pop', 0.55)
    return c


def preview(step=2, workers=1):
    """Fast check cut: every `step`-th frame, 1 sample, half size, with the mix."""
    out = WORK + '/preview_cut.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{C.W // 2}x{C.H // 2}',
                          '-r', str(FPS / step), '-i', '-', '-i', OUT + '/audio.wav', '-c:v', 'libx264', '-crf', '23',
                          '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', out],
                         stdin=subprocess.PIPE)
    for i in range(0, NF, step):
        t = i / FPS
        s = finish_frame(draw(t), t)
        s = cv2.resize(s, (C.W // 2, C.H // 2), interpolation=cv2.INTER_AREA)
        p.stdin.write((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    return out


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'still':
        still([float(x) for x in sys.argv[2:]])
    elif cmd == 'cues':
        os.makedirs(WORK, exist_ok=True)
        json.dump(cues(), open(WORK + '/cues.json', 'w'))
        print(WORK + '/cues.json')
    elif cmd == 'preview':
        print(preview())
    elif cmd == 'render':
        print(render(int(sys.argv[2]) if len(sys.argv) > 2 else 4))
