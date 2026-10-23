"""Soundtrack for the IC London "Three CV mistakes" reel v2 (footage-led cut): a warm, piano-led bed with soft drums,
desk Foley (paper slides, marker squeaks, typing, a stamp), and the calm natural voiceover with a gentle fade-out.
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
from audio_of import (piano, pad, bass, kick, shaker, snap, chime, whoosh, riser, boom, pop, tick, key_click,
                      shimmer, lp, hp, bp, reverb, SR, tt)
import reel_cv2 as RC

T, VO = RC.T, RC.VO
DUR = RC.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(71)
B = 0.6          # 100 BPM, laid back
BAR = 2.4


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def squeak(dur=0.5, v=0.25):
    """Felt-tip marker on paper: band-passed noise with a wobbling centre."""
    t = tt(dur)
    n = rng.normal(0, 1, len(t))
    x = bp(n, 1800, 5200, 2) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) ** 2
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06)
    return x * env * v


def paper(dur=0.35, v=0.3):
    t = tt(dur)
    x = lp(rng.normal(0, 1, len(t)), 2500, 2)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return x * env * v


def thump(v=0.5):
    t = tt(0.3)
    x = np.sin(2 * np.pi * (90 + 120 * np.exp(-t * 40)) * t) * np.exp(-t * 18)
    return (x + lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 40) * 0.4) * v


# ------------------------------------------------------------------ music (C maj7 - A m7 - F maj7 - G)
CH = [(36, [64, 67, 71, 72]), (33, [60, 64, 67, 69]), (29, [60, 64, 65, 69]), (31, [62, 65, 67, 71])]
add(music, 0.0, pad([64, 67, 71], T['intro'] + 0.4, vel=0.2, bright=1500))
bi = 0
while True:
    t0 = bi * BAR
    if t0 >= DUR - 1.5:
        break
    root, tones = CH[bi % 4]
    d = min(BAR, DUR - t0)
    add(music, t0, pad(tones[:3], d + 0.4, vel=0.18, bright=1800))
    if t0 >= T['intro'] - 0.1:
        add(music, t0, bass(root + 12, d, 0.28))
    for j, m in enumerate([tones[0], tones[2], tones[3], tones[1]]):
        add(music, t0 + j * B, piano(m + 12, 1.4, 0.2 if j == 0 else 0.13), pan=-0.2 + 0.13 * j)
    if bi % 2 == 1:
        add(music, t0 + 2.5 * B, piano(tones[3] + 24, 1.0, 0.08), pan=0.3)
    bi += 1
i = 0
while True:
    tb = 0.6 + i * B
    if tb >= T['brand']:
        break
    add(music, tb, kick(0.3 if i % 4 == 0 else 0.22))
    add(music, tb + B / 2, shaker(0.08), pan=0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.09), pan=-0.1)
    i += 1
add(music, T['brand'], pad([60, 64, 67, 71, 76], DUR - T['brand'], vel=0.3, bright=2200))
for j, m in enumerate([60, 64, 67, 71, 74]):
    add(music, T['brand'] + 0.05 + j * 0.08, piano(m + 12, 2.8, 0.16), pan=-0.3 + j * 0.15)
music = reverb(music, wet=0.26, length=2.2, key='hall')

# ------------------------------------------------------------------ SFX
for c in [0.0, 0.65, 1.3, 1.95]:                             # hook cuts
    add(sfx, c, whoosh(0.18, 2000, 9000, 0.14), pan=0.2)
    add(sfx, c, tick(0.2))
add(sfx, 0.6, squeak(0.4, 0.15))                            # staircase line draws
for tb in RC.BLINDS:                                        # blind-strip transitions
    for i in range(6):
        add(sfx, tb + i * 0.04, whoosh(0.18, 900, 6000, 0.08), pan=-0.5 + 0.2 * i)
add(sfx, VO['intro'] + 0.6, thump(0.5))                     # big "3"
for ft in RC.FIX_T:                                         # meter bar fills after each fix
    add(sfx, ft + 0.3, pop(0.3, 900))
    add(sfx, ft + 0.32, chime(84, 0.2, 1.2))
add(sfx, VO['m1'] + 2.0, squeak(0.5, 0.28))                 # strike "Responsible for..."
add(sfx, VO['m1'] + 2.35, pop(0.3, 520))                    # TOO VAGUE tag
for k in range(0, 70, 3):                                   # the stronger line types in
    add(sfx, RC.FIX_T[0] + 0.1 + k / 70 * 1.0, key_click(0.07 + 0.03 * rng.random()), pan=rng.uniform(-0.2, 0.2))
for j in range(3):
    add(sfx, T['m2'] + 0.4 + j * 0.18, pop(0.24, 700 + 120 * j))
    add(sfx, VO['m2'] + 0.6 + j * 0.3, squeak(0.3, 0.26))
add(sfx, VO['m2'] + 1.9, whoosh(0.5, 3000, 500, 0.22), pan=0.6)
for j in range(3):
    add(sfx, RC.FIX_T[1] + 0.3 + j * 0.2, pop(0.26, 800 + 120 * j))
add(sfx, VO['m3'] + 0.5, pop(0.28, 480))                    # HARD TO SKIM
add(sfx, RC.FIX_T[2], riser(0.5, 0.2))
for k in range(12):
    add(sfx, RC.FIX_T[2] + 0.1 + k * 0.06, tick(0.12), pan=rng.uniform(-0.4, 0.4))
add(sfx, RC.FIX_T[2] + 0.8, pop(0.3, 900))
add(sfx, T['panel'] - 0.05, paper(0.5, 0.4), pan=0.5)      # cream panel wipes in
add(sfx, VO['cta'] + 0.3, thump(0.45))
add(sfx, VO['cta'] + 0.75, thump(0.4))
add(sfx, T['panel'] + 0.6, squeak(1.2, 0.12))
add(sfx, T['brand'], whoosh(0.4, 300, 6000, 0.25))
add(sfx, T['brand'] + 0.1, shimmer(1.2, 0.2, 86))
add(sfx, T['brand'] + 0.15, chime(81, 0.24, 2.0))
sfx = reverb(sfx, wet=0.12, length=1.0, key='room')

# ------------------------------------------------------------------ voiceover (gentle chain)
LINES = f'{RC.S}/tts/lines'


def vo_chain(x, sr):
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 85, 2)
    x = x + 0.2 * bp(x, 2500, 5500, 2)
    x = x - 0.1 * bp(x, 250, 450, 2)
    x = lp(x, 11000, 2)
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))
    thr = 0.2 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 2.5) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name, t0 in VO.items():
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, t0, vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.06, length=0.8, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.4 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * 0.85 * (1 - 0.68 * lvl)[:, None] + sfx * 0.9 * (1 - 0.45 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(RC.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RC.S}/audio', exist_ok=True)
wavfile.write(f'{RC.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RC.S}/audio/mix_raw.wav')
