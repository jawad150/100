"""Modern UI / tech sound-effect palette (shared). Extracted from audio_sol.py."""
import os, sys
import numpy as np
from scipy import signal
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, SR, tt
mtof = A.mtof
rng = np.random.default_rng(77)


# ------------------------------------------------------------------ SFX palette v2 (modern UI / tech sound design)
# Redefined here so the music above keeps its own instruments; everything below uses these.
def pop(vel=0.3, f=900):
    """Bubbly UI blip: fast upward chirp with a soft body."""
    t = tt(0.16)
    fr = f * 0.7 * (1 + 1.2 * (1 - np.exp(-t * 60)))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 26)
    return (x + 0.25 * np.sin(4 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 40)) * np.minimum(1, t / 0.002) * vel


def whoosh(dur=0.5, f0=300, f1=3500, vel=0.5, rev=False):
    """Reverse-swell swish: filtered noise that swells in, with a faint tonal sweep."""
    t = tt(dur)
    k = t / dur
    env = (k ** 2.2) * np.exp(-((k - 0.85) / 0.25) ** 2 * (k > 0.85))
    noise = rng.normal(0, 1, len(t))
    fa, fb = sorted((f0, f1))
    lo = bp(noise, max(80, fa * 0.6), min(16000, fb * 1.2), 2)
    f = f0 * (f1 / max(1, f0)) ** k
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    x = (lo + tone) * env
    return np.stack([x, np.roll(x, 90)], 1) * vel


def boom(vel=0.5):
    """Punchy sub-drop impact."""
    t = tt(1.1)
    f = 40 + 90 * np.exp(-t * 14)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    crack = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 70) * 0.5
    return np.tanh((sub + crack) * 1.4) * vel


def thud(vel=0.5, f=70):
    t = tt(0.45)
    fr = f * 0.8 + f * 1.6 * np.exp(-t * 40)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 11)
    snap_ = bp(rng.normal(0, 1, len(t)), 2000, 9000) * np.exp(-t * 160) * 0.5
    return (body + snap_) * vel


def shimmer(dur=0.9, vel=0.3, base=84):
    """Glassy FM bell sparkle arpeggio."""
    out = np.zeros(int((dur + 0.8) * SR))
    for j, iv in enumerate([0, 7, 12, 16, 19]):
        t = tt(dur + 0.6)
        f = mtof(base + iv)
        x = np.sin(2 * np.pi * f * t + 1.8 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 6)) * np.exp(-t * 4.5)
        i = int(j * 0.045 * SR)
        out[i:i + len(x)] += x[:len(out) - i] * (0.9 ** j)
    return out * vel * 0.5


def tick(vel=0.3):
    t = tt(0.03)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 400) * vel + hp(rng.normal(0, 1, len(t)), 6000) * np.exp(-t * 500) * vel * 0.5


def key_click(vel=0.18):
    """Mechanical keyboard clack: switch tick + key bottoming out."""
    out = np.zeros(int(0.08 * SR))
    for d, f, a in ((0.0, 4200, 1.0), (0.018, 1400, 0.7)):
        t = tt(0.05)
        x = bp(rng.normal(0, 1, len(t)), f * 0.6, min(15000, f * 1.6), 2) * np.exp(-t * 220) * a
        i = int(d * SR)
        out[i:i + len(x)] += x[:len(out) - i]
    return out * vel * 1.4


def clack(vel=0.4):
    t = tt(0.18)
    return (np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 60) * 0.6 + bp(rng.normal(0, 1, len(t)), 3000, 10000) * np.exp(-t * 120)) * vel


def ping(vel=0.15, f=1320):
    """FM bell plink for the target rings."""
    t = tt(1.0)
    return np.sin(2 * np.pi * f * 0.75 * t + 2.5 * np.sin(2 * np.pi * f * 1.4 * t) * np.exp(-t * 8)) * np.exp(-t * 6) * vel


def zip_up(vel=0.15, f0=300, f1=1400, dur=0.45):
    """Laser rise: detuned saw sweep."""
    t = tt(dur)
    f = f0 * (f1 / f0) ** ((t / dur) ** 1.4)
    x = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + signal.sawtooth(2 * np.pi * np.cumsum(f * 1.01) / SR)
    return lp(x, 5000, 2) * np.sin(np.pi * t / dur) ** 1.5 * vel * 0.5


def scribble(dur=1.0, vel=0.1):
    """Felt-tip writing: short scratchy strokes."""
    t = tt(dur)
    n = bp(rng.normal(0, 1, len(t)), 3000, 9000)
    strokes = (np.sin(2 * np.pi * 5.5 * t + 2 * np.sin(2 * np.pi * 1.7 * t)) > -0.2).astype(float)
    strokes = np.convolve(strokes, np.ones(400) / 400, mode='same')
    return n * strokes * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.08).clip(0, 1) * vel


def squeak(dur=0.3, vel=0.12):
    """Marker swipe."""
    t = tt(dur)
    f = 1800 + 2600 * t / dur
    return bp(rng.normal(0, 1, len(t)), 1500, 8000) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR / 40)) * np.sin(np.pi * t / dur) * vel * 1.3


def crinkle(dur=0.35, vel=0.3):
    out = np.zeros(int(dur * SR) + 4000)
    for _ in range(26):
        t = tt(0.02)
        x = bp(rng.normal(0, 1, len(t)), 2500, 11000) * np.exp(-t * 300)
        i = int(rng.uniform(0, dur) * SR)
        out[i:i + len(x)] += x * rng.uniform(0.4, 1.0)
    return out * vel


def clang(vel=0.35):
    """Tin-can clank."""
    t = tt(0.9)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((780, 1, 6), (1910, 0.7, 9), (3020, 0.5, 12), (4470, 0.3, 16)))
    return (x + bp(rng.normal(0, 1, len(t)), 1000, 6000) * np.exp(-t * 50) * 0.8) * vel


def knock(vel=0.3):
    """Snappy click for the signs."""
    t = tt(0.12)
    return (np.sin(2 * np.pi * 900 * t) * np.exp(-t * 70) + hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 150) * 0.6) * vel


def bonk(vel=0.3):
    """Wrong-answer buzz: two detuned square blips falling."""
    out = np.zeros(int(0.45 * SR))
    for d, f in ((0.0, 330), (0.15, 233)):
        t = tt(0.22)
        x = np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.012 * t))
        x = lp(x, 1800) * np.exp(-t * 9) * 0.5
        out[int(d * SR):int(d * SR) + len(x)] += x
    return out * vel


def slam(vel=0.6):
    """Rubber-stamp slam: impact + metallic ring."""
    t = tt(0.8)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dd) * a for f, a, dd in ((410, 0.5, 7), (1130, 0.3, 10)))
    return boom(1.0)[:len(t)] * vel + ring * vel * 0.4


