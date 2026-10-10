"""Bodyrade soundtrack: 120 BPM energetic gym track + SFX locked to each reel (48 kHz stereo).

Usage: REEL=fresh|five|flavour python3 audio_br.py
"""
import os, sys, math
import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, reverb, SR, tt, chime, whoosh, riser, boom, pop, tick, key_click, shimmer
import reel_br as RB

REEL = RB.REEL
DUR = RB.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
rng = np.random.default_rng(7)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
B = RB.BEAT


def add(buf, t0, x, gain=1.0, pan=0.0):
    A.add(buf, t0, x, gain, pan)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ instruments
def kick(v=1.0):
    t = tt(0.42)
    f = 48 + 140 * np.exp(-t * 38)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    x = np.tanh(x * 2.2) / 1.4
    click = hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 400) * 0.25
    return (x + click) * v


def clap(v=0.6):
    t = tt(0.35)
    n = rng.normal(0, 1, len(t))
    env = np.zeros_like(t)
    for d in (0.0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) * 60), 0)
    env += np.exp(-t * 14) * 0.5
    return bp(n, 900, 5000) * env * v


def hat(v=0.25, open_=False):
    t = tt(0.25 if open_ else 0.06)
    return hp(rng.normal(0, 1, len(t)), 7500) * np.exp(-t * (14 if open_ else 80)) * v


def sub(m, dur, v=0.55):
    t = tt(dur)
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.tanh(3 * np.sin(2 * np.pi * f * t))
    e = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03)
    return x * e * v


def saw_chord(ms, dur, v=0.22, cutoff=2400, pluck=True):
    t = tt(dur)
    x = np.zeros((len(t), 2))
    for m in ms:
        f = mtof(m)
        for det, ch in [(-0.12, 0), (0.12, 1), (-0.05, 1), (0.05, 0)]:
            ph = rng.uniform(0, 1)
            x[:, ch] += 2 * ((f * (1 + det / 100) * t + ph) % 1.0) - 1
    env = np.exp(-t * 7) if pluck else np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.05)
    x = lp(x, cutoff, 2) * env[:, None] * v / len(ms)
    return x


def downlifter(dur=0.9, v=0.4):
    return whoosh(dur, 6000, 200, v, rev=True)


def impact(v=0.9):
    return boom(v) + np.pad(lp(rng.normal(0, 1, int(0.5 * SR)) * np.exp(-tt(0.5) * 9), 3000) * 0.4,
                            (0, int(1.6 * SR) - int(0.5 * SR)))


def buzz(v=0.25):
    t = tt(0.16)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) * np.exp(-t * 18)
    return lp(x, 1800) * v


def tick_roll(dur, v=0.2, rate=28):
    out = np.zeros(int(dur * SR) + 2000)
    for k in range(int(dur * rate)):
        i0 = int(k / rate * SR)
        x = tick(v * (0.6 + 0.4 * k / max(1, dur * rate)))
        out[i0:i0 + len(x)] += x[:len(out) - i0]
    return out


def splash(v=0.4):
    t = tt(0.7)
    n = rng.normal(0, 1, len(t))
    return (bp(n, 300, 3000) * np.exp(-t * 6) + bp(n, 2000, 9000) * np.exp(-t * 12) * 0.5) * v


# ------------------------------------------------------------------ arrangement per reel
PROG = [41, 37, 44, 39]   # F  Db  Ab  Eb  (i VI III VII), bass octave
CHORDS = {41: [65, 68, 72], 37: [61, 65, 68], 44: [63, 68, 72], 39: [63, 67, 70]}

if REEL == 'fresh':
    F = RB.F1
    drop1, breakdown, drop2 = F['problem'], (F['turn'], F['steps']), F['steps']
    end_t = F['end']
elif REEL == 'five':
    F = RB.F2
    drop1, breakdown, drop2 = F['serving'], (F['total'] - 0.01, F['total']), F['actives']
    end_t = F['end']
else:
    F = RB.F3
    drop1, breakdown, drop2 = F['orange'], (F['trio'] - 0.01, F['trio']), F['orange']
    end_t = F['trio']


def section(t):
    if t < drop1:
        return 'build'
    if breakdown[0] <= t < breakdown[1]:
        return 'break'
    if t >= end_t:
        return 'outro'
    return 'drop'


nb = int(DUR / B) + 1
for i in range(nb):
    tb = i * B
    sec = section(tb)
    bar = int(tb / (4 * B))
    root = PROG[bar % 4]
    beat_in_bar = i % 4
    if sec == 'build':
        add(music, tb, hat(0.12 + 0.1 * tb / max(drop1, 0.1)), pan=0.2)
        add(music, tb + B / 2, hat(0.1), pan=-0.2)
        if beat_in_bar in (0, 2):
            add(music, tb, saw_chord(CHORDS[root], B * 2, v=0.12, cutoff=900 + 2000 * tb / max(drop1, 0.1),
                                     pluck=False))
    elif sec == 'drop':
        add(music, tb, kick(0.95))
        if beat_in_bar in (1, 3):
            add(music, tb, clap(0.5))
        for s16 in range(4):
            add(music, tb + s16 * B / 4, hat(0.14 if s16 % 2 else 0.2), pan=0.25 * (1 if s16 % 2 else -1))
        add(music, tb + B / 2, hat(0.12, open_=True), pan=0.1)
        add(music, tb + B / 2, sub(root, B / 2 * 0.95, 0.5))
        add(music, tb + B * 0.75, saw_chord(CHORDS[root], B * 0.4, v=0.2, cutoff=3200), pan=0.0)
        # arp lead on 8ths every other bar
        if bar % 2 == 1:
            for e8 in range(2):
                m = CHORDS[root][(i * 2 + e8) % 3] + 12
                add(music, tb + e8 * B / 2, saw_chord([m], B / 2 * 0.9, v=0.09, cutoff=5000), pan=0.3 - 0.6 * e8)
    elif sec == 'break':
        if beat_in_bar == 0:
            add(music, tb, saw_chord(CHORDS[root], 4 * B, v=0.18, cutoff=1600, pluck=False))
        add(music, tb, hat(0.08), pan=0.3)
    else:  # outro
        if tb < end_t + 0.01:
            pass

# risers into each drop, impacts on the drop
for d in sorted({drop1, drop2}):
    add(music, d - 1.6, riser(1.6, 0.35))
    add(music, d, impact(0.85))
# end: big chord + downlifter
add(music, end_t, impact(0.8))
add(music, end_t, saw_chord([53, 60, 65, 68, 72], DUR - end_t, v=0.3, cutoff=2600, pluck=False))
add(music, end_t, sub(29, min(2.0, DUR - end_t), 0.5))
add(music, end_t + 0.05, downlifter(1.0, 0.25))

music = reverb(music, wet=0.16, length=1.4, key='club')

# ------------------------------------------------------------------ SFX
for tc, kind in RB.TRANS:
    if kind == 'whip':
        add(sfx, tc - 0.15, whoosh(0.3, 300, 7000, 0.45))
    elif kind == 'zoom':
        add(sfx, tc - 0.14, whoosh(0.28, 200, 9000, 0.4))
    elif kind == 'flash':
        add(sfx, tc, chime(84, 0.18, 0.8))
    elif kind == 'wipe':
        add(sfx, tc - 0.05, whoosh(0.45, 200, 6000, 0.4))
        add(sfx, tc + 0.05, splash(0.35))

if REEL == 'fresh':
    for k in range(8):
        add(sfx, k * 0.25, A.snap(0.3), pan=(-1) ** k * 0.3)
    add(sfx, 0.05, impact(0.7))
    add(sfx, 0.4, boom(0.4))
    t0 = F['problem']
    for k in range(6):
        add(sfx, t0 + 0.7 + k * 0.5, tick(0.15))           # "LIVE" blips
    add(sfx, t0 + 1.0, whoosh(2.2, 2500, 400, 0.12))      # line falling
    for tt_ in (1.3, 2.0, 2.6):
        add(sfx, t0 + tt_, pop(0.22, 700))
    for tt_ in (3.4, 3.8, 4.2):
        add(sfx, t0 + tt_, buzz(0.22))
    add(sfx, F['turn'] + 0.15, impact(0.6))
    add(sfx, F['turn'], shimmer(0.6, 0.2, 84))
    for k in range(4):
        st = F['steps'] + 3 * k
        add(sfx, st + 0.05, pop(0.28, 900 + 120 * k))
        add(sfx, st + 0.3, tick(0.25))
    add(sfx, F['steps'] + 9.4, A.shaker(0.3))
    for k in range(10):
        add(sfx, F['steps'] + 9.4 + k * 0.09, A.shaker(0.18), pan=rng.uniform(-0.5, 0.5))
    for j in range(3):
        add(sfx, F['benefits'] + 0.6 + j * 0.55, pop(0.3, 800))
        add(sfx, F['benefits'] + 0.8 + j * 0.55, chime(84 + 3 * j, 0.15, 0.6))
    add(sfx, F['end'] + 0.35, shimmer(0.8, 0.22, 86))
elif REEL == 'five':
    for k in range(6):
        add(sfx, k * 0.25, A.snap(0.25), pan=(-1) ** k * 0.3)
    add(sfx, 0.1, whoosh(0.9, 200, 8000, 0.4))
    add(sfx, 0.7, impact(0.7))
    add(sfx, F['serving'] + 0.2, tick_roll(1.4, 0.16, 18))
    for k in range(5):
        st = F['actives'] + 3 * k
        add(sfx, st + 0.05, tick_roll(0.85, 0.18, 30))
        add(sfx, st + 0.9, chime(79 + 2 * k, 0.25, 1.0))
        add(sfx, st + 0.2, whoosh(1.0, 400, 3000, 0.1))
    add(sfx, F['total'] + 0.1, impact(0.6))
    for j in range(3):
        add(sfx, F['total'] + 0.05 + 0.1 * j, pop(0.25, 700 + 100 * j))
    add(sfx, F['end'] + 0.35, shimmer(0.8, 0.22, 86))
else:
    for k in range(10):
        add(sfx, k * 0.25, A.snap(0.3), pan=(-1) ** k * 0.3)
        add(sfx, k * 0.25, pop(0.12, 500 + 80 * (k % 3)))
    for fl, key in (('orange', 84), ('raspberry', 86), ('pear', 88)):
        t0 = F[fl]
        add(sfx, t0 + 0.15, shimmer(0.5, 0.18, key))
        for k in range(4):
            add(sfx, t0 + 0.6 + k * 1.2, whoosh(0.5, 500, 5000, 0.12), pan=rng.uniform(-0.6, 0.6))
        add(sfx, t0 + 0.9, pop(0.22, 750))
    for j in range(3):
        add(sfx, F['trio'] + 0.05 + 0.08 * j, pop(0.3, 650 + 120 * j))
    add(sfx, F['trio'] + 1.0, shimmer(0.8, 0.22, 86))

sfx = reverb(sfx, wet=0.14, length=1.0, key='room')
mix = music * 0.8 + sfx * 0.85
mix = np.tanh(mix * 1.15) / 1.15
fade = np.ones(N)
fade[-int(0.4 * SR):] = np.linspace(1, 0, int(0.4 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RB.S}/audio', exist_ok=True)
wavfile.write(f'{RB.S}/audio/mix_{REEL}.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RB.S}/audio/mix_{REEL}.wav')
