"""Soundtrack for BMHC "The First Word" — voice + soft sound design, no music (per BMHC's brief).

Gentle UI-style pops, swishes and chimes land on every word-synced pop-up. The verse section (sacred mode) is left clean:
voice only, no SFX underneath. A faint room-air bed keeps the gaps from sounding dead; it dips away under the verse.
Expressive narrator on top, gentle fade-out after the last word.
"""
import os, sys
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sqe'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, reverb, SR, tt
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, zip_up, crinkle, thud
import reel_bmhc as R

P, PD, END, VO, DUR = R.P, R.PD, R.END, R.VO, R.DUR
SAC0, SAC1 = R.SACRED
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(3)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR and not (SAC0 - 0.3 < t0 < SAC1 - 0.2):          # nothing under the verse
        A.add(buf, t0, x, gain, pan)


def soft_whoosh(t0, j=0, vel=0.12):
    add(sfx, t0, whoosh(0.34, 260 + 70 * (j % 4), 5200, vel), pan=(-0.3 if j % 2 else 0.3))


# ------------------------------------------------------------------ cuts
for j, (a, b, f) in enumerate(R.shots()[1:]):
    kind, td = R.TRANS[j]
    if kind in (R.tr_dissolve, R.tr_ink):
        continue                                                      # quiet transitions in and out of the verse
    soft_whoosh(a - td / 2 - 0.05, j, 0.13 if kind is R.tr_bars else 0.11)

# ------------------------------------------------------------------ word-synced pops
add(sfx, P('l1', 2) - 0.05, whoosh(0.3, 900, 5000, 0.08))              # Whalley Range tag
add(sfx, P('l1', 2) + 0.1, tick(0.12))
tk = P('l2', 1) + PD('l2', 1) * 0.55
add(sfx, tk - 0.1, pop(0.2, 640))                                     # 1866 photo
add(sfx, tk + 0.15, pop(0.16, 900))                                   # since 1843
add(sfx, P('l3', 0) + 0.1, pop(0.18, 760))                            # here's a question
q0, q1 = P('l3', 1), R.END('l3') - 0.2
add(sfx, q0 - 0.2, pop(0.16, 520))                                    # search bar
for k in range(int((q1 - q0) / 0.075)):                               # typing
    add(sfx, q0 + k * 0.075 + rng.uniform(-0.01, 0.01), key_click(0.07), pan=rng.uniform(-0.2, 0.2))
for j in range(4):                                                    # Pray / Fast / Read / Give
    add(sfx, P('l4', j) - 0.03, pop(0.22, 620 + 110 * j), pan=(-0.35 if j % 2 == 0 else 0.35))
tg = P('l4', 4) + PD('l4', 4)
for j in range(3):                                                    # 3-2-1
    add(sfx, tg + j * 0.4, tick(0.16))
add(sfx, P('l5', 0) + 0.35, shimmer(1.4, 0.16, 84))                   # IQRA (soft chime, no 'wrong' sounds for the others)
add(sfx, P('l5', 0) + 0.38, thud(0.18, 90))
add(sfx, P('l5', 1) - 0.1, ping(0.09, 1320))                          # Read.
add(sfx, P('l5', 2) + 0.2, whoosh(0.3, 900, 4000, 0.06))              # source tag
# (verse: silence under the voice)
add(sfx, P('l8', 0) + 0.05, whoosh(1.3, 400, 3000, 0.06))             # the pen line draws across
add(sfx, P('l8', 1) - 0.05, tick(0.12))                               # Baghdad tag
add(sfx, P('l8', 1) + 0.35, pop(0.22, 560))                           # astrolabe
add(sfx, P('l8', 1) + 0.45, pop(0.14, 820))                           # glass card
ta = P('l8', 2) + PD('l8', 2) * 0.62
add(sfx, ta - 0.25, pop(0.18, 700))                                   # al-jabr
add(sfx, ta, zip_up(0.08, 400, 1400, 0.3))                            # -> algebra
add(sfx, ta + 0.25, pop(0.18, 980))
add(sfx, P('l8', 2) + 0.2, pop(0.16, 760))                            # al-Khwarizmi
add(sfx, P('l8', 3), pop(0.15, 820))                                  # Algoritmi
add(sfx, P('l8', 3) + 0.35, pop(0.17, 1040))                          # algorithm
add(sfx, P('l9', 0) + 0.05, pop(0.24, 520))                           # arch
add(sfx, P('l9', 0) + 0.1, shimmer(0.9, 0.08, 79))
add(sfx, P('l9', 1) + PD('l9', 1) * 0.12, pop(0.18, 720))             # Fatima al-Fihri
add(sfx, P('l9', 1) + PD('l9', 1) * 0.6, pop(0.18, 880))              # al-Qarawiyyin
add(sfx, P('l9', 2), tick(0.12))                                      # Fez 859 tag
add(sfx, P('l9', 3), pop(0.16, 640))                                  # still teaching
for k in range(10):                                                   # year counter
    add(sfx, P('l9', 3) + 0.1 + k * 0.09, tick(0.05 + 0.005 * k))
add(sfx, P('l10', 0) + 0.3, pop(0.14, 600))                           # THEN
add(sfx, P('l10', 1) + 0.2, whoosh(0.9, 300, 3500, 0.1))              # then -> now wipe
add(sfx, P('l10', 2) + 0.3, pop(0.16, 900))                           # NOW
add(sfx, P('l11', 0), pop(0.18, 700))                                 # TODAY
add(sfx, P('l11', 0) + 0.6, shimmer(1.2, 0.14, 84))                   # logo
for j in range(4):                                                    # programme cards
    add(sfx, P('l11', 1 + j) - 0.05, thud(0.14, 120), pan=(-0.3 if j % 2 == 0 else 0.3))
    add(sfx, P('l11', 1 + j) + 0.13, pop(0.18, 700 + 120 * j))
tv = P('l11', 5)
for k in range(14):                                                   # 130K counter
    add(sfx, tv + k * PD('l11', 5) * 0.8 / 14, tick(0.05))
add(sfx, tv + PD('l11', 5) * 0.8, ping(0.1, 1760))
tw = P('l12', 0) + PD('l12', 0) * 0.7
add(sfx, tw, pop(0.2, 620))                                           # star
add(sfx, tw + 0.05, shimmer(1.0, 0.1, 86))
s0, s1 = P('l12', 1), R.END('l12') - 0.1
add(sfx, s0 - 0.2, pop(0.15, 560))
for k in range(int((s1 - s0) / 0.07)):
    add(sfx, s0 + k * 0.07 + rng.uniform(-0.01, 0.01), key_click(0.06), pan=rng.uniform(-0.2, 0.2))
add(sfx, P('l13', 0) - 0.2, shimmer(1.4, 0.14, 84))                   # logo
add(sfx, P('l13', 1), pop(0.22, 780))                                 # url button
add(sfx, P('l13', 1) + 0.1, crinkle(0.4, 0.1))
for j in range(3):                                                    # Learn / Meet / Belong
    add(sfx, P('l13', 1) + 0.7 + j * 0.15, pop(0.13, 760 + 140 * j))
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')

# ------------------------------------------------------------------ room air (not music): faint, dips under the verse
ts_ = np.arange(N) / SR
air = np.stack([lp(hp(rng.normal(0, 1, N), 120), 1800, 2), lp(hp(rng.normal(0, 1, N), 120), 1800, 2)], 1)
air = air / np.sqrt(np.mean(air ** 2)) * 0.006
duck = 1 - 0.85 * np.clip(np.minimum((ts_ - (SAC0 - 0.6)) / 0.6, ((SAC1 + 0.4) - ts_) / 0.6), 0, 1)
air *= duck[:, None]

# ------------------------------------------------------------------ voiceover
LINES = f'{R.S}/tts/lines'


def vo_chain(x, sr):
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 75, 2)
    x = x + 0.18 * bp(x, 2500, 6500, 2)
    x = x + 0.08 * bp(x, 110, 260, 2)
    x = lp(x, 12500, 2)
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))
    thr = 0.22 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 2.6) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name in R.ORDER:
    x, sr = sf.read(f'{LINES}/{name}.wav')
    A.add(vo, VO[name], vo_chain(x, sr), 1.0)
vo_dry = vo.copy()
vo = reverb(vo, wet=0.05, length=0.6, key='vo_room')
sac = np.clip(np.minimum((ts_ - SAC0) / 0.5, (SAC1 - ts_) / 0.5), 0, 1)[:, None]      # a touch more space on the verse
vo = vo + reverb(vo_dry, wet=0.12, length=1.6, key='vo_hall') * sac * 0.6

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
mix = sfx * 0.9 * (1 - 0.3 * lvl)[:, None] + air + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(R.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav')
