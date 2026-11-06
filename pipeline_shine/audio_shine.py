"""Soundtrack for BMHC "Shine" — no music (per the PDF's Islamic guidelines check): voice and natural sounds only.

Soft footsteps on a path, a gentle breath as the spark appears, a candle's soft flutter, for each lantern a paper rustle and a
warm low "whump" of light, a quiet rising air as they lift, and a calm evening ambience (soft wind, distant crickets).
Voice: Microsoft neural en-GB-LibbyNeural, lightly polished. Gentle fade-out at the end; nothing clipped. Master -14 LUFS.
"""
import os, sys
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, reverb, SR, tt
import reel_shine as R

T, DUR, OFF, LIGHT = R.T, R.DUR, R.OFF, R.LIGHT
N = int(SR * DUR)
A.DUR, A.N = DUR, N
fx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(3)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def noise(d):
    return rng.normal(0, 1, int(d * SR))


def breath(d=1.1, vel=0.05):
    x = bp(noise(d), 300, 2500, 2)
    t = tt(d)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return x * env * vel


def step(vel=0.08):
    t = tt(0.16)
    x = lp(noise(0.16), 900, 2) * np.exp(-t * 28) + 0.5 * bp(noise(0.16), 1500, 5000, 2) * np.exp(-t * 60)
    return x * vel


def rustle(d=0.5, vel=0.05):
    t = tt(d)
    x = bp(noise(d), 2000, 9000, 2) * (rng.random(len(t)) > 0.4)
    x = lp(x, 7000, 2)
    return x * np.sin(np.pi * t / d) ** 0.7 * vel


def whump(vel=0.22):
    """Warm 'whump' of light: a soft low thump with an airy bloom."""
    t = tt(0.9)
    f = 70 + 40 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    air = lp(noise(0.9), 1400, 2) * np.exp(-t * 4.5) * np.minimum(1, t / 0.03) * 0.5
    return (body + air) * vel


def rise_air(d=4.0, vel=0.06):
    t = tt(d)
    k = t / d
    x = noise(d)
    out = np.zeros_like(x)
    seg = int(0.05 * SR)
    for i in range(0, len(x), seg):
        f0 = 300 + 1800 * k[i]
        out[i:i + seg] = bp(x[i:i + seg + 1000], f0, f0 * 2.2, 2)[:len(out[i:i + seg])]
    return lp(out, 6000, 2) * np.sin(np.pi * np.clip(k, 0, 1)) ** 1.2 * vel


def cricket(vel=0.012):
    t = tt(0.5)
    x = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 32 * t) > 0.3) * (t < 0.22)
    return x * vel


# ------------------------------------------------------------------ ambience: soft evening wind, distant crickets, room air
ts_ = np.arange(N) / SR
wind = lp(rng.normal(0, 1, (N, 2)), 400, 2) * 0.016 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * ts_))[:, None]
amb += wind
for k in range(40):
    add(amb, rng.uniform(0.5, T['Shine'] - 1.5), cricket(rng.uniform(0.006, 0.014)), pan=rng.uniform(-0.8, 0.8))
amb *= np.clip(ts_ / 1.5, 0, 1)[:, None]

# ------------------------------------------------------------------ the story
for k in range(7):                                                          # two pairs of trainers on the path
    add(fx, 0.35 + k * 0.27, step(0.07 if k % 2 else 0.055), pan=(-0.25 if k % 2 else 0.25))
add(fx, 0.15, breath(1.3, 0.05))                                            # the spark breathes in
add(fx, T['spark'] - 0.35, breath(0.9, 0.06))
add(fx, T['spark'] - 0.05, whump(0.12))
add(fx, T['spark'] + 0.25, rise_air(1.6, 0.04))                             # it lifts away
for nm in R.ORDER:
    tl = LIGHT[nm]
    add(fx, tl - 0.55, rise_air(0.6, 0.025))                                # the spark travels
    add(fx, tl - 0.12, rustle(0.45, 0.05), pan=(R.POS[nm][0] - 540) / 700)
    add(fx, tl - 0.04, whump(0.2), pan=(R.POS[nm][0] - 540) / 900)
add(fx, T['shine'] - 0.4, rise_air(4.2, 0.07))                              # they rise
add(fx, T['shine'] - 0.1, whump(0.12))
add(fx, T['Shine'] - 0.5, rise_air(1.2, 0.04))                              # into the end card
add(fx, T['Join'] - 0.05, whump(0.14))
fx = reverb(fx, wet=0.18, length=1.4, key='hall')

# ------------------------------------------------------------------ voice
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x + 0.06 * bp(x, 2500, 6000, 2) + 0.05 * bp(x, 150, 300, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
add(vo, OFF, x, 1.0)
vo = reverb(vo, wet=0.05, length=0.7, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.4 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = amb * (1 - 0.35 * lvl)[:, None] + fx * (1 - 0.2 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.02) / 1.02
fade = np.ones(N)
nf = int(2.2 * SR)                                                          # gentle fade-out (matches the picture)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
vo_end = OFF + INFO_D if (INFO_D := float(R.INFO['dur'])) else 0
print('wrote mix', 'DUR', DUR, 'voice ends', round(OFF + R.INFO['phrases'][-1][1] + R.INFO['phrases'][-1][2], 2))
