"""Soundtrack for "Your Year in Fostering": an upbeat, feel-good 120 BPM pop instrumental, a whoosh on every story
swipe, soft dings on reveals, card-specific Foley, and the calm natural voiceover ducked over the top.

Timing comes from reel_yf.py so every swipe, tick and tap lands on its frame. Ends on a gentle equal-power fade.
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
import reel_yf as RY

T, VO, C = RY.T, RY.VO, RY.C
DUR = RY.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(52)
B = 0.5
BAR = 2.0


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def buzz(dur=0.2, v=0.5):
    t = tt(dur)
    x = np.tanh(4 * np.sin(2 * np.pi * 150 * t)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t)))
    return lp(x, 900) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03) * v


def pluck(m, dur=0.35, v=0.2):
    t = tt(dur)
    f = 440.0 * 2 ** ((m - 69) / 12)
    x = (2 * ((f * t) % 1.0) - 1) * 0.6 + np.sin(2 * np.pi * f * t)
    return lp(x * np.exp(-t * 9), 3500) * v


# ------------------------------------------------------------------ music (G major: I - V - vi - IV)
CH = [(43, [67, 71, 74, 79]), (38, [66, 69, 74, 78]), (40, [64, 67, 71, 76]), (36, [64, 67, 72, 76])]
HOOK = [79, 83, 86, 83, 81, 79, 78, 74]
# hook: anticipation under the phone (soft pad + ticking pulse)
add(music, 0.0, pad([67, 71, 74], C[0] + 0.3, vel=0.2, bright=1300))
for k in range(int(C[0] / B)):
    add(music, k * B, tick(0.11), pan=0.2 * (-1) ** k)
START, END = C[0], T['cta'] + 0.5
bi = 0
while True:
    t0 = START + bi * BAR
    if t0 >= END:
        break
    root, tones = CH[bi % 4]
    d = min(BAR, END - t0)
    breakdown = T['turn'] <= t0 < T['cta']
    add(music, t0, pad(tones[:3], d + 0.4, vel=0.22 if not breakdown else 0.3, bright=2200))
    add(music, t0, bass(root, d, 0.4 if not breakdown else 0.2))
    for e8 in range(8):
        te = t0 + e8 * B / 2
        if te >= END - 0.02:
            break
        m = tones[[0, 2, 1, 3, 2, 1, 3, 2][e8]] + 12
        add(music, te, pluck(m, 0.3, 0.13 if e8 % 2 == 0 else 0.09), pan=-0.35 + 0.7 * (e8 % 2))
    if not breakdown:
        for j, m in enumerate(HOOK[(bi % 2) * 4:(bi % 2) * 4 + 4]):
            add(music, t0 + j * B, piano(m, 0.9, 0.13), pan=0.15)
    bi += 1
i = 0
while True:
    tb = START + i * B
    if tb >= T['turn']:
        break
    add(music, tb, kick(0.46 if i % 4 == 0 else 0.36))
    add(music, tb + B / 2, shaker(0.13), pan=0.3)
    add(music, tb + B / 4, shaker(0.06), pan=-0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.16), pan=-0.1)
        add(music, tb + 0.012, snap(0.08), pan=0.2)
    i += 1
# the turn: kick drops out, a soft pulse returns as the 2027 card lands
for k in range(int((T['cta'] - RY.STORY_T) / B)):
    add(music, RY.STORY_T + k * B, kick(0.24))
# resolving chord + sparkle on the end card, left to ring into the fade
add(music, RY.LOGO_T, pad([67, 71, 74, 79, 83], DUR - RY.LOGO_T, vel=0.38, bright=2400))
add(music, RY.LOGO_T, bass(43, DUR - RY.LOGO_T - 0.2, 0.36))
for j, m in enumerate([67, 71, 74, 79, 83, 86]):
    add(music, RY.LOGO_T + 0.04 + j * 0.06, piano(m, 2.6, 0.2), pan=-0.3 + j * 0.12)
music = reverb(music, wet=0.22, length=2.0, key='hall')

# ------------------------------------------------------------------ SFX
add(sfx, RY.NOTIF - 0.05, buzz(0.2, 0.5))
add(sfx, RY.NOTIF + 0.2, buzz(0.2, 0.5))
add(sfx, RY.NOTIF + 0.05, chime(86, 0.3, 1.4), pan=0.1)
add(sfx, RY.NOTIF + 0.12, chime(91, 0.16, 1.0), pan=-0.1)
add(sfx, 1.1, whoosh(0.8, 300, 2500, 0.1), pan=0.4)
add(sfx, RY.TAP_PLAY, key_click(0.5))
add(sfx, RY.TAP_PLAY + 0.01, pop(0.42, 700))
add(sfx, RY.TAP_PLAY + 0.05, riser(C[0] - RY.TAP_PLAY - 0.05, 0.35))
add(sfx, C[0], boom(0.6))
for j, c in enumerate(C):                                   # whoosh on every swipe, soft ding on each reveal
    add(sfx, c - 0.12, whoosh(0.35, 300, 7000, 0.4), pan=0.3)
    add(sfx, c + 0.5, chime(83 + 2 * (j % 3), 0.22, 1.4), pan=-0.15)
# card 1: moon rises
add(sfx, C[0] + 0.25, shimmer(1.2, 0.2, 86))
# card 2: pizza pops in
add(sfx, C[1] + 0.7, pop(0.4, 600))
# card 3: books land, counter spins
add(sfx, C[2] + 0.35, whoosh(0.5, 2500, 400, 0.15))
add(sfx, C[2] + 0.9, boom(0.45))
add(sfx, C[2] + 0.9, pop(0.3, 300))
for k in range(28):
    add(sfx, C[2] + 0.95 + k * 0.034, tick(0.12))
add(sfx, C[2] + 1.9, pop(0.32, 900))
add(sfx, C[2] + 1.95, chime(88, 0.18, 1.0))
# card 4: four avatars pop in
for j in range(4):
    add(sfx, C[3] + 0.55 + j * 0.18, pop(0.3, 700 + 120 * j), pan=(-1) ** j * 0.3)
# card 5: slot machine
for k in range(int((0.75 + 0.22 * 4 - 0.55) / 0.045)):
    add(sfx, C[4] + 0.55 + k * 0.045, tick(0.14), pan=rng.uniform(-0.3, 0.3))
for r in range(5):
    add(sfx, C[4] + 0.75 + 0.22 * r, pop(0.28, 500 + 90 * r))
    add(sfx, C[4] + 0.75 + 0.22 * r, key_click(0.2))
add(sfx, C[4] + 1.6, chime(88, 0.32, 1.6))
add(sfx, C[4] + 1.62, chime(95, 0.18, 1.4))
add(sfx, C[4] + 1.6, shimmer(0.8, 0.24, 91))
# card 6: the glow holds
add(sfx, C[5] + 0.2, boom(0.4))
add(sfx, C[5] + 0.2, shimmer(2.0, 0.18, 81))
for j, off in enumerate((2.3, 3.0, 3.7)):
    add(sfx, VO['c6'] + off, chime(79 + 4 * j, 0.14, 1.4))
# the turn: fan-out, shuffle riffle, 2027 card lands, button
add(sfx, T['turn'] - 0.2, whoosh(0.45, 300, 8000, 0.4))
for i in range(6):
    add(sfx, T['turn'] + 0.05 + i * 0.06, whoosh(0.2, 1200, 6000, 0.12), pan=-0.5 + 0.2 * i)
for k in range(22):
    add(sfx, T['turn'] + 1.2 + k * 0.03, tick(0.1 + 0.05 * rng.random()), pan=rng.uniform(-0.4, 0.4))
add(sfx, RY.STORY_T - 0.1, boom(0.5))
add(sfx, RY.STORY_T, shimmer(0.8, 0.2, 86))
add(sfx, RY.BTN_T, pop(0.36, 520))
# CTA: tap, flip, toast, logo
add(sfx, RY.TAP_CTA, key_click(0.5))
add(sfx, RY.TAP_CTA + 0.01, pop(0.45, 700))
add(sfx, RY.FLIP_T, whoosh(0.4, 600, 5000, 0.25))
add(sfx, RY.FLIP_T + 0.25, pop(0.4, 800))
for k, m in enumerate([79, 83, 86, 91]):
    add(sfx, RY.FLIP_T + 0.25 + k * 0.07, chime(m, 0.2, 1.4), pan=-0.3 + 0.2 * k)
add(sfx, RY.LOGO_T - 0.3, whoosh(0.4, 4000, 400, 0.2))
add(sfx, RY.LOGO_T, shimmer(1.2, 0.22, 86))
add(sfx, RY.LOGO_T + 0.35, pop(0.22, 760))
sfx = reverb(sfx, wet=0.15, length=1.2, key='room')

# ------------------------------------------------------------------ voiceover (gentle chain, smooth ducking)
LINES = f'{RY.S}/tts/lines'


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
nf = int(RY.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RY.S}/audio', exist_ok=True)
wavfile.write(f'{RY.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RY.S}/audio/mix_raw.wav')
