"""Soundtrack for BMHC "Lights On": voice, room tone and a light-switch click on every room. No music (BMHC guideline).

Per room: dawn birds at Fajr, a hall echo for taekwondo, a studio hum for Heritage Radio, dice for the youth club, a tea
pour for the open day. Soft pops on the 3D objects, swishes on the camera moves, blinds rattle, and a warm shimmer on the
final "lights on".
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
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud
import reel_lights as R

P, PD, WT, END, VO, DUR = R.P, R.PD, R.WT, R.END, R.VO, R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(11)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def switch(t0, vel=0.32):
    add(sfx, t0 - 0.02, key_click(vel))
    add(sfx, t0, thud(vel * 0.4, 150))
    add(sfx, t0 + 0.04, bp(rng.normal(0, 1, int(0.25 * SR)), 2000, 7000) * np.exp(-np.linspace(0, 9, int(0.25 * SR))) * vel * 0.12)


def bird(t0, f=3200, vel=0.05):
    d = rng.uniform(0.12, 0.25)
    t = tt(d)
    fm = f * (1 + 0.25 * np.sin(2 * np.pi * rng.uniform(18, 30) * t)) * (1 + 0.2 * t / d)
    x = np.sin(2 * np.pi * np.cumsum(fm) / SR) * np.sin(np.pi * t / d) ** 2
    add(amb, t0, x * vel, pan=rng.uniform(-0.6, 0.6))


def room(t0, t1, lo=80, hi=900, vel=0.012):
    n = int((t1 - t0) * SR)
    if n <= 0:
        return
    x = bp(rng.normal(0, 1, (n, 2)), lo, hi) * vel
    env = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.25 * SR))[:, None]
    add(amb, t0, x * env)


def hum(t0, t1, vel=0.01):
    n = int((t1 - t0) * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 100 * t) * 0.6 + np.sin(2 * np.pi * 200 * t) * 0.25) * vel + bp(rng.normal(0, 1, n), 4000, 9000) * vel * 0.5
    env = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.3 * SR))
    add(amb, t0, x * env)


def pour(t0, dur=1.6, vel=0.06):
    n = int(dur * SR)
    x = bp(rng.normal(0, 1, n), 600, 3500) * (0.6 + 0.4 * np.sin(np.linspace(0, 40, n)) ** 2)
    env = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.15 * SR))
    add(amb, t0, x * env * vel)


def dice(t0, vel=0.12):
    for k in range(7):
        add(sfx, t0 + k * 0.06 * (1 + k * 0.15), tick(vel * (1 - k * 0.1)), pan=rng.uniform(-0.3, 0.3))


def rattle(t0, dur=0.45, vel=0.06):
    for k in range(12):
        add(sfx, t0 + k * dur / 12, tick(vel), pan=rng.uniform(-0.4, 0.4))


# ------------------------------------------------------------------ room tone + ambience per shot
shots = R.shots()
for j, (a, b, f) in enumerate(shots):
    b = min(b, DUR)
    name = f.__name__
    if name == 'sh_gates':
        room(a, b, 200, 3000, 0.01)
        for k in range(6):
            bird(a + 0.4 + k * 0.45, rng.uniform(2800, 4200), 0.03)
    elif name == 'sh_fajr':
        room(a, b, 60, 500, 0.012)
        for k in range(10):
            bird(a + 0.3 + k * 0.28, rng.uniform(3000, 4500), 0.045)
    elif name == 'sh_radio':
        hum(a, b, 0.012)
    elif name == 'sh_sport':
        room(a, b, 150, 1500, 0.014)
    elif name in ('sh_night', 'sh_1843', 'sh_end'):
        room(a, b, 40, 300, 0.012)
        for k in range(4):
            bird(a + 0.8 + k * 1.1, rng.uniform(1800, 2400), 0.012) if name == 'sh_1843' else None
    else:
        room(a, b, 100, 1200, 0.011)
amb = reverb(amb, wet=0.2, length=1.4, key='amb')

# ------------------------------------------------------------------ transitions
for j, (a, b, f) in enumerate(shots[1:]):
    kind, td = R.TRANS[j]
    if kind is R.tr_dip:
        add(sfx, a - td / 2, whoosh(td, 900, 200, 0.05, rev=True))
    elif kind is R.tr_blinds:
        rattle(a - td / 2, td)
    elif kind is R.tr_sweep:
        add(sfx, a - td / 2, whoosh(td + 0.1, 300, 4000, 0.09))
    elif kind is R.tr_iris:
        add(sfx, a - td / 2, whoosh(td + 0.2, 200, 3000, 0.08))
    elif kind is R.tr_dissolve:
        pass
    else:
        add(sfx, a - td / 2 - 0.05, whoosh(0.36, 280, 6000, 0.11), pan=0.3)

# ------------------------------------------------------------------ switches, pops and room sounds on the cues
switch(WT('l2', 0, 0.6))                                           # the first window
add(sfx, P('l2', 1), pop(0.18, 640))                              # 1866 photo
add(sfx, WT('l2', 0, 0.6) + 0.5, pop(0.14, 900))                  # Grade II* chip
switch(WT('l3', 0, 0.25))                                         # door lamp
add(sfx, WT('l3', 0, 0.75), pop(0.18, 760))                       # bulb
add(sfx, WT('l3', 0, 0.75) + 0.05, ping(0.06, 1568))
for j in range(3):                                                # Fajr: ceiling rows
    switch(P('l4', 1) + j * 0.25, 0.2 if j else 0.3)
add(sfx, P('l4', 1) + 0.3, pop(0.14, 700))                         # daily prayers pill
switch(P('l5', 0) + 0.15)
add(sfx, P('l5', 1), pop(0.18, 620))                              # stand + book
add(sfx, P('l5', 1) + 0.2, pop(0.13, 860))
add(sfx, P('l5', 2) + 0.3, pop(0.13, 960))
switch(P('l6', 0) + 0.1)
add(sfx, P('l6', 1), thud(0.18, 110))                             # belts
add(sfx, P('l6', 1) + 0.05, pop(0.16, 700))
switch(P('l7', 0) + 0.2, 0.25)
add(sfx, P('l7', 1) + 0.2, pop(0.13, 820))
add(sfx, P('l7', 2), pop(0.17, 660))                              # clock
for k in range(12):
    add(sfx, P('l7', 2) + 0.05 + k * PD('l7', 2) * 0.8 / 12, tick(0.05))
add(sfx, P('l8', 0) + 0.25, pop(0.15, 760))
dice(P('l8', 0) + 0.3)
add(sfx, P('l8', 1) + 0.2, pop(0.15, 880))                        # compass
add(sfx, P('l8', 1) + 0.25, ping(0.05, 1760))
switch(P('l9', 0) + 0.1)
add(sfx, P('l9', 0) + 0.35, pop(0.16, 620))                        # tea
pour(P('l9', 0) + 0.5, 1.5, 0.05)
switch(P('l10', 0) + 0.1)
add(sfx, P('l10', 0) + 0.15, pop(0.15, 760))                       # FRIDAY chip
add(sfx, P('l10', 1) + 0.2, pop(0.13, 900))
t0, t1 = P('l11', 0), P('l11', 1) + 0.2
for k in range(12):                                                 # windows light one by one
    add(sfx, t0 + (t1 - t0) * k / 12, key_click(0.07 + 0.01 * (k % 3)), pan=rng.uniform(-0.4, 0.4))
for j in range(9):                                                  # the grid of rooms flickers on
    add(sfx, P('l12', 0) - 0.35 + j * 0.09, key_click(0.06), pan=rng.uniform(-0.5, 0.5))
switch(P('l12', 0) + 0.55, 0.4)                                     # the big switch
add(sfx, P('l12', 0) + 0.6, shimmer(1.6, 0.14, 84))
add(sfx, P('l13', 0) + 0.2, pop(0.18, 780))                         # button
add(sfx, P('l13', 0) - 0.3, shimmer(1.2, 0.08, 79))
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')

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
    return x * gain / max(1e-6, np.abs(x * gain).max()) * 0.9


for name in R.ORDER:
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, VO[name], vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.06, length=0.7, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
mix = amb * (1 - 0.4 * lvl)[:, None] + sfx * 0.95 * (1 - 0.25 * lvl)[:, None] + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.4 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'last VO end', round(END('l13'), 2), 'DUR', DUR)
