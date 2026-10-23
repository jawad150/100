"""Soundtrack for the IC London "Three CV mistakes" reel: a warm, piano-led lo-fi bed (unlike the cinematic law reel),
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
import reel_cv as RC

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
    tb = T['m1'] + i * B
    if tb >= T['cta'] + 1.2:
        break
    add(music, tb, kick(0.3 if i % 4 == 0 else 0.22))
    add(music, tb + B / 2, shaker(0.08), pan=0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.09), pan=-0.1)
    i += 1
add(music, T['cta'] + 1.2, pad([60, 64, 67, 71, 76], DUR - T['cta'] - 1.2, vel=0.3, bright=2200))
for j, m in enumerate([60, 64, 67, 71, 74]):
    add(music, T['cta'] + 1.25 + j * 0.08, piano(m + 12, 2.8, 0.16), pan=-0.3 + j * 0.15)
music = reverb(music, wet=0.26, length=2.2, key='hall')

# ------------------------------------------------------------------ SFX
for c in range(3):                                         # hook: three cinematic cuts on the paper
    add(sfx, c * 0.55, paper(0.25, 0.32), pan=(-1) ** c * 0.3)
    add(sfx, c * 0.55, tick(0.18))
add(sfx, 1.65, paper(0.5, 0.3))
add(sfx, 1.2, squeak(0.5, 0.3))                            # red underline
for tc in [T['intro'], T['m1'], T['m2'], T['m3'], T['cta']]:
    add(sfx, tc - 0.1, paper(0.4, 0.38), pan=0.2)
    add(sfx, tc - 0.05, whoosh(0.3, 600, 4000, 0.12))
for j in range(3):                                         # tabs + magnifier scan
    add(sfx, T['intro'] + 0.4 + j * 0.25, pop(0.28, 700 + 140 * j), pan=0.4)
add(sfx, T['intro'] + 0.6, shimmer(2.4, 0.1, 86))
add(sfx, VO['intro'] + 0.6, thump(0.4))                    # big "3"
add(sfx, VO['m1'] + 0.6, squeak(0.7, 0.32))                # circle "vague"
add(sfx, VO['m1'] + 1.2, squeak(0.3, 0.22))
for k in range(0, 95, 3):                                  # typing the Prospects example
    add(sfx, RC.M1_FIX + k / 95 * 1.4, key_click(0.07 + 0.03 * rng.random()), pan=rng.uniform(-0.2, 0.2))
add(sfx, RC.M1_FIX + 1.45, pop(0.3, 900))
add(sfx, RC.M1_FIX + 1.47, chime(84, 0.18, 1.2))
add(sfx, VO['m1'] + 2.0, pop(0.26, 600))
for j in range(3):                                         # strike-throughs
    add(sfx, VO['m2'] + 0.5 + j * 0.35, squeak(0.3, 0.3), pan=-0.2 + 0.2 * j)
add(sfx, VO['m2'] + 1.5, squeak(0.35, 0.2))
add(sfx, VO['m2'] + 2.0, whoosh(0.5, 3000, 500, 0.2), pan=0.5)   # lines fly away
add(sfx, RC.M2_TAILOR - 0.1, paper(0.45, 0.35), pan=0.5)          # job advert slides in
add(sfx, RC.M2_TAILOR + 0.5, shimmer(0.6, 0.14, 88))
add(sfx, RC.M2_TAILOR + 0.2, pop(0.26, 650))
add(sfx, VO['m3'] + 0.5, squeak(0.9, 0.3))                 # scribbles over the mess
add(sfx, RC.M3_FIX, riser(0.5, 0.2))
add(sfx, RC.M3_FIX + 0.5, boom(0.35))
for k in range(14):                                        # elements snap into the clean layout
    add(sfx, RC.M3_FIX + 0.1 + k * 0.05, tick(0.12), pan=rng.uniform(-0.4, 0.4))
for tt_ in [RC.M3_FIX + 0.2, RC.M3_FIX + 0.7, VO['m3'] + 4.2, VO['m3'] + 4.8]:
    add(sfx, tt_, pop(0.26, 780))
add(sfx, T['cta'] + 0.6, thump(0.55))                      # READY TO SEND stamp
add(sfx, T['cta'] + 0.62, chime(81, 0.2, 1.6))
add(sfx, T['cta'] + 1.2, pop(0.24, 760))
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
