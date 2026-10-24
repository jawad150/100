"""Soundtrack for "Leave the Light On" v2: a warm, heartfelt acoustic track (guitar, felt piano, strings, glockenspiel) under the same
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


# ------------------------------------------------------------------ music: warm acoustic, heartfelt (G major, 92 bpm)
# strummed acoustic guitar (Karplus-Strong), felt piano melody, soft strings, glockenspiel sparkles, light claps
mtof = A.mtof


def guitar_note(m, dur=2.2, vel=0.3, bright=0.5):
    f = mtof(m)
    n = int(SR / f)
    L = int(SR * dur)
    exc = np.zeros(L)
    burst = rng.normal(0, 1, n)
    burst = lp(burst, 1500 + 4500 * bright, 1)
    exc[:n] = burst
    g = 0.996
    a = np.zeros(n + 2)
    a[0] = 1.0
    a[n] -= g * 0.5
    a[n + 1] -= g * 0.5
    y = signal.lfilter([1.0], a, exc)
    y = hp(y, 80, 1)
    y *= np.minimum(1, (L - np.arange(L)) / (0.05 * SR))
    return y / max(1e-6, np.abs(y).max()) * vel


def strum(t0, notes, vel=0.25, up=False, dur=2.0, bright=0.5, pan=0.0):
    ns = notes[::-1] if up else notes
    for k, m in enumerate(ns):
        add(music, t0 + k * (0.009 if up else 0.013), guitar_note(m, dur, vel * (0.75 if up else 1.0), bright),
            pan=pan + (k - len(ns) / 2) * 0.05)


def strings(ms, dur, vel=0.12, att=0.8, bright=2200):
    t = tt(dur + 0.8)
    x = np.zeros_like(t)
    for m in ms:
        for d in (-0.07, 0.0, 0.08):
            f = mtof(m + d) * (1 + 0.003 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6)))
            x += signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    x = lp(x, bright, 2) / (len(ms) * 3)
    env = np.minimum(1, t / att) * np.where(t > dur, np.exp(-(t - dur) * 3), 1.0)
    return x * env * vel


def glock(m, vel=0.12):
    t = tt(1.6)
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + \
        0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12)
    return x * np.exp(-t * 3.2) * np.minimum(1, t / 0.001) * vel


def clap(vel=0.12):
    out = np.zeros(int(0.25 * SR))
    for d in (0.0, 0.008, 0.017):
        t = tt(0.2)
        x = bp(rng.normal(0, 1, len(t)), 900, 5000) * np.exp(-t * 35)
        i = int(d * SR)
        out[i:i + len(x)] += x * (0.6 if d else 1.0)
    return out * vel


BPM = 92
B = 60 / BPM
BAR = 4 * B
GTR = [[43, 47, 50, 55, 59, 67], [50, 57, 62, 66], [40, 47, 52, 55, 59, 64], [48, 52, 55, 60, 64]]   # G D Em C
ROOT = [43, 38, 40, 36]
PADN = [[55, 59, 62, 67], [54, 57, 62, 66], [55, 59, 64, 67], [55, 60, 64, 67]]
MEL = [[71, 74, 79, 78], [74, 69, 66, 69], [71, 67, 64, 67], [72, 76, 79, 76]]
M0 = R.SW_FLIP                                   # music blooms with the light switch
ARR0, ARR1 = R.HOME0 + 0.3, T['payoff']          # tender breakdown for the arrival
STRUM = [(0, False, 1.0), (1, False, 0.7), (1.5, True, 0.6), (2.5, True, 0.6), (3, False, 0.8), (3.5, True, 0.6)]
bi = 0
while True:
    t0 = M0 + bi * BAR
    if t0 >= T['end'] - 0.2:
        break
    c = bi % 4
    tender = ARR0 - 0.2 <= t0 < ARR1 - 0.3
    sec = 'hook' if t0 < T['call'] - 0.3 else 'call' if t0 < T['ready'] - 0.5 else 'full'
    # felt piano melody, all the way through (quieter under the busier sections)
    for j, m in enumerate(MEL[c]):
        add(music, t0 + j * B, piano(m, 1.4, (0.13 if sec == 'hook' or tender else 0.09) * (1.0 if j == 0 else 0.8)),
            pan=0.15)
    if sec == 'hook':
        add(music, t0, strings(PADN[c], BAR, vel=0.11, att=0.9, bright=2000))
        strum(t0, GTR[c], 0.2, dur=BAR, bright=0.6)
        strum(t0 + 2 * B, GTR[c], 0.13, up=True, dur=BAR / 2, bright=0.6)
        add(music, t0, bass(ROOT[c] + 12, BAR, 0.08))
    elif tender:
        add(music, t0, strings(PADN[c] + [PADN[c][0] + 12], BAR, vel=0.18, att=0.9, bright=2200))
        add(music, t0, bass(ROOT[c] + 12, BAR, 0.08))
        strum(t0, GTR[c], 0.17, dur=BAR + 0.5, bright=0.45)
    else:
        lift = 1.15 if t0 >= T['payoff'] else 1.0
        if sec == 'call':
            for q in range(4):                                   # gentle palm-muted strums on each beat
                strum(t0 + q * B, GTR[c][:4], 0.15, dur=0.35, bright=0.5)
        else:
            for (bt, up, v) in STRUM:
                strum(t0 + bt * B, GTR[c], 0.2 * v * lift, up=up, dur=1.2, bright=0.75, pan=-0.15)
            add(music, t0, strings(PADN[c], BAR, vel=0.07 * lift, att=0.6, bright=2200))
            add(music, t0 + 1 * B, clap(0.1 * lift), pan=0.1)
            add(music, t0 + 3 * B, clap(0.1 * lift), pan=0.1)
            add(music, t0 + 2 * B + B / 2, glock(MEL[c][2] + 12, 0.06), pan=0.35)
        add(music, t0, bass(ROOT[c] + 12, 1.8 * B, 0.12 * lift))
        add(music, t0 + 2 * B, bass(ROOT[c] + 12, 1.5 * B, 0.085 * lift))
        for q in range(4):
            add(music, t0 + q * B, kick(0.11 if q % 2 == 0 else 0.07))
    bi += 1
for j, m in enumerate([79, 83, 86]):                           # glockenspiel sparkle as the light comes on
    add(music, R.SW_FLIP + 0.05 + j * 0.11, glock(m, 0.1), pan=-0.2 + 0.2 * j)
# end card: big warm G chord, ringing strum + strings + glock
strum(T['end'], GTR[0], 0.22, dur=DUR - T['end'], bright=0.6)
add(music, T['end'], strings([55, 59, 62, 67, 71], DUR - T['end'], vel=0.14, att=0.5, bright=2600))
add(music, T['end'], bass(43 + 12, DUR - T['end'], 0.15))
for j, m in enumerate([79, 83, 86, 91]):
    add(music, T['end'] + 0.3 + j * 0.18, glock(m, 0.08), pan=-0.3 + 0.2 * j)
music = reverb(music, wet=0.28, length=2.3, key='hall')

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
bed = music * 1.05 * (1 - 0.72 * lvl)[:, None] + sfx * 0.9 * (1 - 0.35 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(R.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/music_stem.wav', SR, (music / max(1e-6, np.abs(music).max()) * 0.9 * 32767).astype(np.int16))
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav')
