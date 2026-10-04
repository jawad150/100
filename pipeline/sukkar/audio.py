"""Audio assembly for the edit: dialogue bites + natural OR sound, numpy at 48 kHz."""
import subprocess

import numpy as np

SR = 48000


def read(path, t0, dur, stream=0, channels=2):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t0):.5f}", "-t", f"{dur:.5f}", "-i", path,
           "-map", f"0:a:{stream}", "-ac", str(channels), "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, channels).copy()
    want = int(round(dur * SR))
    if len(a) < want:
        a = np.vstack([a, np.zeros((want - len(a), channels), np.float32)])
    return a[:want]


def db(x):
    return 10 ** (x / 20)


def fade(a, fin=0.01, fout=0.01, shape="cos"):
    n = len(a)
    i = int(fin * SR)
    o = int(fout * SR)
    if i > 0:
        r = np.linspace(0, 1, i, dtype=np.float32)
        a[:i] *= (0.5 - 0.5 * np.cos(np.pi * r))[:, None] if shape == "cos" else r[:, None]
    if o > 0:
        r = np.linspace(1, 0, o, dtype=np.float32)
        a[n - o:] *= (0.5 - 0.5 * np.cos(np.pi * r))[:, None] if shape == "cos" else r[:, None]
    return a


class Bus:
    def __init__(self, seconds):
        self.buf = np.zeros((int(seconds * SR) + SR, 2), np.float32)

    def add(self, a, at, gain_db=0.0):
        s = int(round(at * SR))
        if s < 0:
            a = a[-s:]
            s = 0
        e = min(len(self.buf), s + len(a))
        self.buf[s:e] += a[:e - s] * db(gain_db)

    def envelope(self, points):
        """Multiply by a piecewise-linear gain curve given as [(sec, dB), ...]."""
        t = np.arange(len(self.buf)) / SR
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        g = db(np.interp(t, xs, ys)).astype(np.float32)
        self.buf *= g[:, None]


def presence(bus, attack=0.06, release=0.35, thresh_db=-45):
    """0..1 envelope of where a bus has signal (for ducking)."""
    x = np.abs(bus.buf).max(axis=1)
    hop = 480
    n = len(x) // hop
    e = x[:n * hop].reshape(n, hop).max(axis=1)
    on = (20 * np.log10(e + 1e-9) > thresh_db).astype(np.float32)
    out = np.zeros_like(on)
    a = 1 - np.exp(-hop / SR / attack)
    r = 1 - np.exp(-hop / SR / release)
    v = 0.0
    for i, s in enumerate(on):
        v += (a if s > v else r) * (s - v)
        out[i] = v
    full = np.repeat(out, hop)
    full = np.concatenate([full, np.full(len(bus.buf) - len(full), full[-1] if len(full) else 0)])
    return full.astype(np.float32)
