"""Soundtrack for "Leave the Light On": steady rain, story Foley (porch click, phone buzz, ticking clock, sheet snap,
toaster pop, passing car, door), a quiet warm piano that swells at the arrival, and the calm male voiceover ducked over
the top, ending on a gentle fade.
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
from audio_of import (piano, pad, bass, chime, whoosh, riser, boom, pop, tick, key_click, shimmer, lp, hp, bp, reverb,
                      SR, tt)
import reel_lo as RL

T, VO = RL.T, RL.VO
DUR = RL.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(81)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def click(v=0.5):
    t = tt(0.06)
    return (hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 160) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) * 0.4) * v


def buzz(dur=0.35, v=0.45):
    t = tt(dur)
    x = np.tanh(4 * np.sin(2 * np.pi * 150 * t)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t)))
    return lp(x, 900) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03) * v


def snap(v=0.5):
    """Bed sheet snapping open: a soft whoomp of filtered noise."""
    t = tt(0.5)
    x = lp(rng.normal(0, 1, len(t)), 1800, 2) * np.exp(-((t - 0.12) / 0.07) ** 2) * 2.0
    return x * v


def toaster(v=0.5):
    t = tt(0.35)
    spring = np.sin(2 * np.pi * (900 - 500 * t) * t) * np.exp(-t * 18) * 0.5
    thunk = lp(rng.normal(0, 1, len(t)), 700) * np.exp(-t * 40)
    return (spring + thunk) * v


def car(dur=1.6, v=0.4):
    t = tt(dur)
    n = lp(rng.normal(0, 1, len(t)), 500, 2) + 0.4 * np.sin(2 * np.pi * 55 * t)
    env = np.exp(-((t - dur * 0.55) / (dur * 0.28)) ** 2)
    x = np.stack([n * env * np.clip(1.4 - t / dur * 1.4, 0, 1), n * env * np.clip(t / dur * 1.4, 0, 1)], 1)
    return x * v


def door(v=0.5):
    t = tt(0.9)
    creak = bp(rng.normal(0, 1, len(t)), 300, 1200) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) * np.exp(-t * 3)
    latch = hp(rng.normal(0, 1, len(t)), 2000) * np.exp(-t * 120)
    return (creak * 0.5 + latch) * v


# ------------------------------------------------------------------ ambience: steady rain (cosier and muffled indoors)
rain_n = rng.normal(0, 1, (N, 2))
rain = bp(rain_n, 600, 9000, 2) * 0.16 + lp(rain_n, 400, 2) * 0.12
ts = np.arange(N) / SR
inside = np.zeros(N)
for a, b in [(T['call'], T['arrive']), (T['payoff'], T['rise'])]:
    inside += np.clip((ts - a) / 0.3, 0, 1) * np.clip((b - ts) / 0.3, 0, 1)
inside = np.clip(inside, 0, 1)
muffled = lp(rain, 900, 2) * 0.9
amb = rain * (1 - inside[:, None]) + muffled * inside[:, None]
# patter on the window: random drops
for k in range(260):
    add(amb, rng.uniform(0, DUR), tick(rng.uniform(0.02, 0.06)), pan=rng.uniform(-0.8, 0.8))

# ------------------------------------------------------------------ music: quiet warm piano, swells at the arrival
CH = [(41, [65, 69, 72]), (36, [64, 67, 72]), (38, [62, 65, 69]), (34, [62, 65, 70])]   # F C Dm Bb
BAR = 2.4
bi = 0
while True:
    t0 = 0.6 + bi * BAR
    if t0 >= DUR - 1.0:
        break
    root, tones = CH[bi % 4]
    swell = 1.0 if T['arrive'] <= t0 else 0.6
    if t0 >= T['call']:
        add(music, t0, pad(tones, BAR + 0.5, vel=0.14 * swell, bright=1500))
        add(music, t0, bass(root + 12, BAR, 0.16 * swell))
    for j, m in enumerate([tones[0], tones[2], tones[1], tones[2]]):
        add(music, t0 + j * 0.6, piano(m + 12, 1.6, (0.16 if j == 0 else 0.1) * (1.3 if swell == 1 else 1.0)),
            pan=-0.2 + 0.13 * j)
    if swell == 1 and bi % 2 == 0:
        add(music, t0 + 1.5, piano(tones[2] + 24, 1.4, 0.07), pan=0.3)
    bi += 1
add(music, T['end'], pad([65, 69, 72, 77], DUR - T['end'], vel=0.28, bright=2000))
for j, m in enumerate([65, 69, 72, 77, 81]):
    add(music, T['end'] + 0.05 + j * 0.09, piano(m + 12, 2.6, 0.15), pan=-0.3 + j * 0.15)
music = reverb(music, wet=0.32, length=2.6, key='hall')

# ------------------------------------------------------------------ Foley
add(sfx, RL.CLICK, click(0.7))
add(sfx, RL.CLICK + 0.02, shimmer(1.0, 0.12, 81))
for k in range(int((RL.ANSWER - T['call']) / 0.5)):          # phone buzzing until answered
    add(sfx, T['call'] + 0.1 + k * 0.5, buzz(0.32, 0.4))
add(sfx, RL.ANSWER, key_click(0.4))
add(sfx, RL.ANSWER + 0.02, pop(0.25, 600))
for k in range(int((T['arrive'] - T['call']) / 0.5)):        # ticking clock
    add(sfx, T['call'] + 0.25 + k * 0.5, tick(0.16 if k % 2 == 0 else 0.11), pan=-0.4)
r0 = T['ready']
L = RL.SHOT_LEN
add(sfx, r0 - 0.15, whoosh(0.3, 300, 5000, 0.25))
add(sfx, r0 + 0.25, snap(0.6))                               # fresh sheets
add(sfx, r0 + L + 0.3, click(0.5))                            # nightlight clicks on
add(sfx, r0 + L + 0.32, chime(88, 0.12, 1.2))
add(sfx, r0 + 2 * L + 0.9, toaster(0.55))                     # toast pops
for j in range(4):                                           # checklist ticks
    add(sfx, r0 + L * (j + 0.55), pop(0.24, 760 + 80 * j))
add(sfx, T['arrive'] - 1.2, car(1.6, 0.45))                   # headlights / car pulls up
add(sfx, T['arrive'] - 0.05, door(0.6))
add(sfx, T['arrive'], shimmer(1.2, 0.14, 84))
add(sfx, T['payoff'] - 0.1, whoosh(0.3, 300, 4000, 0.2))
add(sfx, VO['never'] + 0.9, pop(0.24, 700))
add(sfx, T['rise'] - 0.1, whoosh(0.6, 200, 3000, 0.25))
add(sfx, T['end'], shimmer(1.2, 0.18, 86))
add(sfx, T['end'] + 0.5, pop(0.22, 760))
sfx = reverb(sfx, wet=0.14, length=1.0, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{RL.S}/tts/lines'


def vo_chain(x, sr):
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 70, 2)
    x = x + 0.15 * bp(x, 2500, 5500, 2)
    x = x + 0.08 * bp(x, 120, 300, 2)                 # a touch of warmth for the male voice
    x = lp(x, 11000, 2)
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))
    thr = 0.2 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 2.5) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name, t0 in VO.items():
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, t0, vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.07, length=0.9, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.4 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = (music * 0.85 + amb * 0.55) * (1 - 0.62 * lvl)[:, None] + sfx * 0.9 * (1 - 0.4 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(RL.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RL.S}/audio', exist_ok=True)
wavfile.write(f'{RL.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RL.S}/audio/mix_raw.wav')
