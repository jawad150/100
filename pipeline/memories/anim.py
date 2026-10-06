"""After Effects-style animation curves for the Yaadein compositor.

Every animated property is a Track of keyframes. Each segment is eased with a cubic bezier speed
graph defined like AE's keyframe velocity dialog: outgoing influence on the left key and incoming
influence on the right key (speed 0 at both ends = 'Easy Ease'; influence 33% is AE's default,
75-95% gives the long, liquid 'expo' glide motion designers dial in on the graph editor).
Springs give physically settling overshoot.
"""
import math

import numpy as np


class Bezier:
    """CSS/AE cubic-bezier timing function y(x) through (0,0),(x1,y1),(x2,y2),(1,1)."""

    def __init__(self, x1, y1, x2, y2):
        self.c = (x1, y1, x2, y2)

    @staticmethod
    def _b(t, a, b):
        return 3 * a * (1 - t) ** 2 * t + 3 * b * (1 - t) * t ** 2 + t ** 3

    @staticmethod
    def _db(t, a, b):
        return 3 * a * (1 - t) ** 2 + 6 * (b - a) * (1 - t) * t + 3 * (1 - b) * t ** 2

    def __call__(self, x):
        x1, y1, x2, y2 = self.c
        x = np.clip(np.asarray(x, np.float64), 0, 1)
        t = x.copy()
        for _ in range(8):                                   # Newton on x(t) = x
            d = self._db(t, x1, x2)
            t = np.clip(t - np.where(np.abs(d) > 1e-6, (self._b(t, x1, x2) - x) / np.where(np.abs(d) > 1e-6, d, 1), 0), 0, 1)
        for _ in range(12):                                  # bisection polish where Newton stalls
            err = self._b(t, x1, x2) - x
            if np.all(np.abs(err) < 1e-7):
                break
            t = np.clip(t - err * 0.5, 0, 1)
        y = self._b(t, y1, y2)
        return float(y) if y.ndim == 0 else y


def influence(out_inf=33, in_inf=33):
    """AE keyframe velocity: speed 0 on both keys, outgoing/incoming influence in percent."""
    return Bezier(out_inf / 100.0, 0.0, 1 - in_inf / 100.0, 1.0)


LINEAR = Bezier(0, 0, 1, 1)
EASY = influence(33, 33)                 # AE F9
SMOOTH = influence(70, 70)               # long liquid glide
EXPO = influence(90, 90)                 # graph-editor 'expo' S-curve
EXPO_OUT = Bezier(0.16, 1.0, 0.3, 1.0)   # fast start, very long settle (whip-in)
EXPO_IN = Bezier(0.7, 0.0, 0.84, 0.0)    # slow start, fast end (whip-out)
QUART_OUT = Bezier(0.25, 1.0, 0.5, 1.0)
BACK_OUT = Bezier(0.34, 1.56, 0.64, 1.0)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ramp(t, t0, t1, ease=EASY):
    """0..1 eased progress between t0 and t1."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return ease(clamp((t - t0) / (t1 - t0)))


class Track:
    """keys: [(time, value), ...] with optional ease per segment: [(t, v, ease_to_next), ...].
    Values can be scalars or tuples (interpolated component-wise)."""

    def __init__(self, keys, ease=SMOOTH):
        ks = []
        for k in keys:
            t, v = k[0], np.atleast_1d(np.asarray(k[1], np.float64))
            e = k[2] if len(k) > 2 else ease
            ks.append((float(t), v, e))
        self.k = sorted(ks, key=lambda q: q[0])
        self.scalar = np.ndim(keys[0][1]) == 0

    def __call__(self, t):
        k = self.k
        if t <= k[0][0]:
            v = k[0][1]
        elif t >= k[-1][0]:
            v = k[-1][1]
        else:
            for i in range(len(k) - 1):
                if k[i][0] <= t < k[i + 1][0]:
                    t0, v0, e = k[i]
                    t1, v1, _ = k[i + 1]
                    v = v0 + (v1 - v0) * e((t - t0) / (t1 - t0))
                    break
        return float(v[0]) if self.scalar else tuple(float(x) for x in v)


def spring(t, freq=2.2, damping=0.42):
    """Unit step response of a damped spring at time t (s) after release: 0 -> 1 with overshoot."""
    if t <= 0:
        return 0.0
    w = 2 * math.pi * freq
    z = damping
    if z < 1:
        wd = w * math.sqrt(1 - z * z)
        return 1 - math.exp(-z * w * t) * (math.cos(wd * t) + z * w / wd * math.sin(wd * t))
    return 1 - math.exp(-w * t) * (1 + w * t)


def wiggle(t, freq=1.0, amp=1.0, seed=0, octaves=3):
    """Smooth AE-style wiggle(): sum of detuned sines, deterministic per seed."""
    rng = np.random.default_rng(seed)
    v = 0.0
    a = amp
    f = freq
    for _ in range(octaves):
        ph = rng.uniform(0, 2 * math.pi, 2)
        fr = f * rng.uniform(0.8, 1.25)
        v += a * 0.5 * (math.sin(2 * math.pi * fr * t + ph[0]) + math.sin(2 * math.pi * fr * 1.618 * t + ph[1]))
        a *= 0.5
        f *= 2.1
    return v
