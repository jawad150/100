"""Soundtrack for "Leave the Light On" v2: a warm, bouncy plucked-piano groove (poster-pop, ~100 bpm) under the same
calm male voiceover, with a sound for every animation: switch click + light bloom, blob splats, heart iris shimmer,
room lights clicking on, card flips, the HOME fly-through riser, photo prints sliding in, and a gentle fade-out.
"""
import os, sys
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import audio_of as A
from audio_of import (piano, pad, bass, kick, shaker, snap, chime, whoosh, riser, boom, pop, tick, key_click, shimmer,
                      lp, hp, bp, reverb, SR, tt)
import reel_lo2 as R

T, VO = R.T, R.VO
DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(202)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def switch_click(v=0.7):
    t = tt(0.12)
    a = hp(rng.normal(0, 1, len(t)), 2200) * np.exp(-t * 220)
    b = np.sin(2 * np.pi * 1400 * t) * np.exp(-t * 120) * 0.5 + lp(rng.normal(0, 1, len(t)), 500) * np.exp(-t * 60) * 0.6
    return (a + b) * v


def splat(v=0.4):
    """Soft wet blob splat for the colour wipes."""
    t = tt(0.35)
    body = lp(rng.normal(0, 1, len(t)), 900, 2) * np.exp(-t * 14)
    blip = np.sin(2 * np.pi * (260 - 160 * t) * t) * np.exp(-t * 18) * 0.6
    return (body + blip) * v


def flip(v=0.35):
    """Card flip: two quick paper flaps."""
    out = np.zeros(int(0.3 * SR))
    for d in (0.0, 0.12):
        t = tt(0.1)
        x = bp(rng.normal(0, 1, len(t)), 800, 5000) * np.exp(-t * 60)
        i = int(d * SR)
        out[i:i + len(x)] += x
    return out * v


def buzz(dur=0.32, v=0.35):
    t = tt(dur)
    x = np.tanh(4 * np.sin(2 * np.pi * 150 * t)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t)))
    return lp(x, 900) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03) * v


def slide(v=0.25):
    """A photo print sliding across paper."""
    t = tt(0.45)
    return bp(rng.normal(0, 1, len(t)), 1500, 7000) * np.sin(np.pi * t / 0.45) ** 2 * v


# ------------------------------------------------------------------ music: bright plucked piano groove, 100 bpm
B = 0.6                                                     # one beat
CH = [(41, [65, 69, 72, 76]), (38, [62, 65, 69, 72]), (34, [62, 65, 70, 74]), (36, [64, 67, 72, 76])]   # F Dm Bb C
start = R.SW_END                                           # music starts as the poster world bursts in
bi = 0
while True:
    t0 = start + bi * 4 * B
    if t0 >= T['end']:
        break
    root, tones = CH[bi % 4]
    lift = 1.15 if t0 >= T['payoff'] else 1.0
    add(music, t0, pad(tones[:3], 4 * B + 0.4, vel=0.11 * lift, bright=1800))
    add(music, t0, bass(root + 12, 1.6 * B, 0.2 * lift))
    add(music, t0 + 2.5 * B, bass(root + 12, 1.2 * B, 0.13 * lift))
    for j, m in enumerate([tones[0], tones[2], tones[1], tones[3], tones[2], tones[1], tones[3], tones[2]]):
        add(music, t0 + j * B / 2, piano(m + 12, 0.8, (0.12 if j % 2 == 0 else 0.08) * lift), pan=-0.25 + 0.07 * j)
    bi += 1
i = 0
while True:
    tb = start + i * B
    if tb >= T['end'] - 0.1:
        break
    inside_dive = T['arrive'] - 0.6 <= tb < T['arrive'] + 1.2     # drop out for the arrival
    if not inside_dive:
        add(music, tb, kick(0.26 if i % 4 == 0 else 0.18))
        add(music, tb + B / 2, shaker(0.07), pan=0.3)
        if i % 2 == 1:
            add(music, tb, snap(0.1), pan=-0.1)
    i += 1
add(music, T['arrive'], pad([65, 69, 72, 77], 3.0, vel=0.2, bright=1500))       # tender swell at the welcome
for j, m in enumerate([77, 81, 84]):
    add(music, T['arrive'] + 0.4 + j * 0.5, piano(m, 1.8, 0.1), pan=-0.2 + 0.2 * j)
add(music, T['end'], pad([65, 69, 72, 77], DUR - T['end'], vel=0.26, bright=2000))
for j, m in enumerate([65, 69, 72, 77, 81]):
    add(music, T['end'] + 0.05 + j * 0.09, piano(m + 12, 2.6, 0.15), pan=-0.3 + j * 0.15)
music = reverb(music, wet=0.24, length=2.0, key='hall')

# ------------------------------------------------------------------ SFX
amb = lp(rng.normal(0, 1, (int(SR * R.SW_END), 2)), 400) * 0.05            # quiet night room before the switch
add(sfx, 0.0, amb * np.linspace(1, 0, len(amb))[:, None] ** 0.5)
add(sfx, R.SW_FLIP, switch_click(0.75))
add(sfx, R.SW_FLIP + 0.03, shimmer(1.0, 0.16, 84))
add(sfx, R.SW_END - 0.1, whoosh(0.5, 300, 6000, 0.3))
for k, d in enumerate([0.05, 0.25, 0.45]):                  # headline words stamp in
    add(sfx, R.SW_END + d + 0.1, pop(0.22, 500 + 120 * k))
add(sfx, R.SW_END + 0.75, whoosh(0.45, 1500, 7000, 0.1))    # brush stroke
for k in range(int((R.ANSWER - T['call'] - 0.2) / 0.5)):     # phone buzzing until answered
    add(sfx, T['call'] + 0.3 + k * 0.5, buzz(0.3, 0.32))
add(sfx, R.ANSWER, key_click(0.4))
add(sfx, T['call'] - 0.1, splat(0.45))                      # orange blob wipe
add(sfx, T['call'] + 0.1, flip(0.3))                        # flip-card clock
add(sfx, T['call'] + 1.25, pop(0.2, 700))                   # sticker
add(sfx, T['ready'] - 0.05, shimmer(0.8, 0.14, 86))         # heart iris
add(sfx, T['ready'], whoosh(0.4, 400, 5000, 0.15))
for j in range(4):
    s0 = T['ready'] + j * R.SHOT_LEN
    add(sfx, s0 + R.ROOM_ON, switch_click(0.35), pan=-0.2)   # room light clicks on
    add(sfx, s0 + R.ROOM_ON + 0.02, chime(84 + [0, 3, 5, 7][j], 0.1, 1.2))
    add(sfx, s0 + R.Z0, whoosh(0.5, 200, 3500, 0.16))        # dive into the room
    add(sfx, s0 + R.M0 + 0.1, pop(0.24, 600))                # photo shape pops open
    add(sfx, s0 + R.M0 + 0.2, pop(0.16, 900))                # sticker
    add(sfx, s0 + 1.25, pop(0.26, 760 + 80 * j))             # tick stamp
    if j == 1:
        add(sfx, s0 - 0.02, whoosh(0.35, 800, 6000, 0.14))   # split slide
    if j == 2:
        add(sfx, s0, flip(0.32))                             # card flip
    if j == 3:
        add(sfx, s0, splat(0.38))                            # blob wipe
add(sfx, R.HOME0 - 0.1, riser(0.65, 0.22))                  # flying through the 3D HOME
add(sfx, R.HOME0 + 0.3, whoosh(0.6, 150, 4000, 0.3))
add(sfx, T['arrive'] + 0.05, shimmer(1.4, 0.18, 84))
add(sfx, T['arrive'] + 0.6, pop(0.16, 650))                 # speech bubbles
add(sfx, T['arrive'] + 1.5, pop(0.16, 750))
add(sfx, T['payoff'] - 0.05, whoosh(0.35, 800, 6000, 0.16)) # split slide
add(sfx, VO['never'] + 0.7, slide(0.25))                    # photo prints
add(sfx, VO['never'] + 1.0, pop(0.18, 700))
add(sfx, VO['never'] + 3.0, slide(0.25))
add(sfx, T['rise'], flip(0.32))                             # card flip into the sunset
add(sfx, T['rise'] + 1.2, whoosh(1.2, 300, 3000, 0.08))     # light sweep
add(sfx, T['end'] - 0.05, splat(0.4))                       # magenta blob wipe
add(sfx, T['end'] + 0.6, shimmer(1.2, 0.16, 88))            # 3D heart
add(sfx, T['end'] + 0.85, pop(0.2, 760))                    # CTA pill
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')

# ------------------------------------------------------------------ voiceover (same calm male lines as v1)
LINES = f'{R.V1.S}/tts/lines'


def vo_chain(x, sr):
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 70, 2)
    x = x + 0.15 * bp(x, 2500, 5500, 2)
    x = x + 0.08 * bp(x, 120, 300, 2)
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
bed = music * 0.8 * (1 - 0.62 * lvl)[:, None] + sfx * 0.9 * (1 - 0.35 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(R.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav')
