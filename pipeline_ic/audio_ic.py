"""Soundtrack for the IC London "No law degree?" reel: a confident, cinematic corporate bed (D minor -> F major lift),
UI Foley locked to the picture, and the calm natural voiceover ducked over the top, ending on a gentle fade.
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
import reel_ic as RI

T, VO = RI.T, RI.VO
DUR = RI.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(61)
B = 0.5
BAR = 2.0


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def pluck(m, dur=0.35, v=0.2):
    t = tt(dur)
    f = 440.0 * 2 ** ((m - 69) / 12)
    x = (2 * ((f * t) % 1.0) - 1) * 0.5 + np.sin(2 * np.pi * f * t)
    return lp(x * np.exp(-t * 8), 3200) * v


# ------------------------------------------------------------------ music
MINOR = [(38, [62, 65, 69, 74]), (34, [62, 65, 70, 74]), (41, [60, 65, 69, 72]), (36, [60, 64, 67, 72])]   # Dm Bb F C
LIFT = [(41, [65, 69, 72, 77]), (36, [64, 67, 72, 76]), (38, [62, 65, 69, 74]), (34, [62, 65, 70, 74])]    # F C Dm Bb
# hook: tense pulse under the montage
add(music, 0.0, pad([62, 65, 69], T['turn'] + 0.4, vel=0.22, bright=1200))
for k in range(int(T['turn'] / B)):
    add(music, k * B, bass(38, 0.4, 0.22 if k % 2 == 0 else 0.14))
    add(music, k * B, tick(0.1), pan=0.2 * (-1) ** k)
START, END = T['turn'], T['cta'] + 1.0
bi = 0
while True:
    t0 = START + bi * BAR
    if t0 >= END:
        break
    lift = t0 >= T['route'] + 4.0
    root, tones = (LIFT if lift else MINOR)[bi % 4]
    d = min(BAR, END - t0)
    add(music, t0, pad(tones[:3], d + 0.4, vel=0.24, bright=2100))
    add(music, t0, bass(root, d, 0.38))
    for e8 in range(8):
        te = t0 + e8 * B / 2
        if te >= END - 0.02:
            break
        add(music, te, pluck(tones[[0, 2, 1, 3, 2, 1, 3, 2][e8]] + 12, 0.3, 0.12 if e8 % 2 == 0 else 0.08),
            pan=-0.35 + 0.7 * (e8 % 2))
    bi += 1
i = 0
while True:
    tb = T['route'] + i * B
    if tb >= T['cta']:
        break
    add(music, tb, kick(0.42 if i % 4 == 0 else 0.3))
    add(music, tb + B / 2, shaker(0.11), pan=0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.12), pan=-0.1)
    i += 1
add(music, T['cta'], pad([65, 69, 72, 77, 81], DUR - T['cta'], vel=0.36, bright=2400))
add(music, T['cta'], bass(41, DUR - T['cta'] - 0.2, 0.36))
for j, m in enumerate([65, 69, 72, 77, 81, 84]):
    add(music, T['cta'] + 0.05 + j * 0.06, piano(m, 2.6, 0.2), pan=-0.3 + j * 0.12)
music = reverb(music, wet=0.24, length=2.2, key='hall')

# ------------------------------------------------------------------ SFX
add(sfx, 0.0, riser(T['turn'], 0.26))
for c in range(8):
    add(sfx, c * 0.45, snap(0.15), pan=(-1) ** c * 0.3)
    add(sfx, c * 0.45, whoosh(0.15, 2000, 9000, 0.1))
add(sfx, 0.95, whoosh(0.4, 600, 5000, 0.18))                       # red underline draws
add(sfx, T['turn'], boom(0.55))
add(sfx, T['turn'] + 0.15, pop(0.25, 700))
for k in range(0, 27, 2):                                            # typing the destination
    add(sfx, T['turn'] + 0.35 + k / 34, key_click(0.08 + 0.03 * rng.random()), pan=rng.uniform(-0.2, 0.2))
add(sfx, RI.NOT_NEC, key_click(0.5))                                 # toggle flips
add(sfx, RI.NOT_NEC + 0.02, pop(0.42, 520))
add(sfx, RI.NOT_NEC + 0.05, chime(81, 0.2, 1.2))
for j in range(2):
    add(sfx, RI.ANY_SUBJ + 0.5 + j * 0.45, pop(0.32, 800 + 150 * j))
    add(sfx, RI.ANY_SUBJ + 0.55 + j * 0.45, chime(84 + 3 * j, 0.18, 1.0))
for k in range(10):
    add(sfx, RI.RECALC + 0.1 + k * 0.12, tick(0.12))
add(sfx, T['route'] - 0.25, riser(0.4, 0.22))
add(sfx, T['route'], boom(0.55))
add(sfx, T['route'], whoosh(0.6, 3000, 300, 0.25))
for j, wt in enumerate(RI.WAY_T[1:]):                                # arrive at each waypoint
    add(sfx, wt - 0.75, whoosh(0.7, 400, 3000, 0.1), pan=0.2)
    add(sfx, wt, pop(0.38, 650 + 90 * j))
    add(sfx, wt + 0.02, chime(77 + 2 * j, 0.24, 1.4), pan=-0.2 + 0.1 * j)
add(sfx, RI.WAY_T[5], boom(0.5))
add(sfx, RI.WAY_T[5] + 0.05, shimmer(1.2, 0.26, 86))
add(sfx, T['ic'] - 0.15, whoosh(0.35, 300, 8000, 0.4))
add(sfx, T['ic'] + 0.3, whoosh(0.5, 2500, 400, 0.15))
for j, ct in enumerate(RI.CHIP_T):
    add(sfx, ct, pop(0.3, 750 + 110 * j))
    add(sfx, ct + 0.02, tick(0.18))
add(sfx, T['cta'] - 0.1, whoosh(0.4, 300, 9000, 0.35))
add(sfx, T['cta'] + 0.05, shimmer(1.0, 0.2, 86))
add(sfx, RI.TAP_CTA, key_click(0.45))
add(sfx, RI.TAP_CTA + 0.01, pop(0.4, 700))
add(sfx, RI.TAP_CTA + 0.05, chime(84, 0.22, 1.6))
sfx = reverb(sfx, wet=0.15, length=1.2, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{RI.S}/tts/lines'


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
bed = music * 0.85 * (1 - 0.7 * lvl)[:, None] + sfx * 0.9 * (1 - 0.5 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(RI.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RI.S}/audio', exist_ok=True)
wavfile.write(f'{RI.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RI.S}/audio/mix_raw.wav')
