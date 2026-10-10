"""Score + SFX + voiceover for the 29.4 s voiceover cut (48 kHz stereo WAV).

Reuses the instruments in audio_of.py; timing comes from reel_vo.py (scene times + VO starts).
Music is ducked under the voice with a smoothed sidechain envelope.
"""
import os, sys, math
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio_of as A
from audio_of import (piano, pad, bass, kick, shaker, snap, chime, whoosh, riser, boom, pop, tick, key_click,
                      shimmer, bird, lp, hp, bp, reverb, SR, tt)
import reel_vo as V

DUR = V.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(21)


def add(buf, t0, x, gain=1.0, pan=0.0):
    A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ score (100 BPM, D major I-vi-IV-V)
B = 0.6
BAR = 2.4
START = V.T_MONEY
CH = [(50, [62, 66, 69, 74]), (47, [59, 62, 66, 71]), (43, [59, 62, 67, 71]), (45, [61, 64, 69, 73])]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
MEL = {0: [74, 76, 78], 1: [78, 76, 74], 2: [74, 71, 74], 3: [76, 73, 69]}


def is_night(t):
    return V.T_NIGHT <= t < V.T_MSG


# hook: soft pad swell under the montage so the voice has a bed
add(music, 0.0, pad([62, 66, 69], 2.3, vel=0.22, bright=1400))
bi = 0
while True:
    t0 = START + bi * BAR
    if t0 >= V.T_END:
        break
    root, tones = CH[bi % 4]
    night = is_night(t0)
    dur_bar = min(BAR, V.T_END - t0)
    add(music, t0, pad(tones[:3], dur_bar + 0.6, vel=0.30 if not night else 0.38, bright=1200 if night else 1700))
    add(music, t0, bass(root, dur_bar, 0.32 if not night else 0.18))
    for e8 in range(8):
        te = t0 + e8 * B / 2
        if te >= V.T_END - 0.05:
            break
        m = tones[ARP[e8]] + (12 if e8 in (3, 7) and not is_night(te) else 0)
        vel = (0.28 if e8 % 2 == 0 else 0.20) * (0.85 if is_night(te) else 1.0)
        add(music, te, piano(m, 0.9, vel), pan=-0.25 + 0.5 * (e8 % 2))
    for j, m in enumerate(MEL[bi % 4]):
        tm = t0 + 2 * B + j * B * 0.66
        if tm < V.T_END - 0.1:
            add(music, tm, piano(m + 12, 1.4, 0.15 if not is_night(tm) else 0.2), pan=0.1)
    bi += 1

# pulse: day + message, rests at night and under the hook
i = 0
while True:
    tb = START + i * B
    if tb >= V.T_END:
        break
    if tb >= V.T_BED - 0.01 and not is_night(tb):
        add(music, tb, kick(0.5 if i % 4 == 0 else 0.34))
        add(music, tb + B / 2, shaker(0.14), pan=0.3)
        if i % 2 == 1:
            add(music, tb, snap(0.1), pan=-0.1)
    i += 1

# resolving chord on the end card
add(music, V.T_END, pad([62, 66, 69, 74, 78], DUR - V.T_END, vel=0.42, bright=2200))
add(music, V.T_END, bass(38, DUR - V.T_END - 0.2, 0.4))
for j, m in enumerate([62, 66, 69, 74, 78, 81]):
    add(music, V.T_END + 0.05 + j * 0.06, piano(m, 2.6, 0.26), pan=-0.3 + j * 0.12)
for j, m in enumerate([74, 78, 81, 86]):   # gentle sparkle under "room to grow, roots to keep"
    add(music, V.VO['end'] + 1.3 + j * 0.35, piano(m, 1.2, 0.12), pan=0.2)

music = reverb(music, wet=0.28, length=2.4, key='hall')

# ------------------------------------------------------------------ SFX
TS, TB, TK, TL, TN, TM, TE = V.T_SHOES, V.T_BAG, V.T_KITCHEN, V.T_LIGHT, V.T_NIGHT, V.T_MSG, V.T_END
add(sfx, 0.0, riser(2.0, 0.30))
for c in range(int(2.0 / V.CUT) + 1):
    add(sfx, c * V.CUT, snap(0.18), pan=(-1) ** c * 0.3)
    add(sfx, c * V.CUT, tick(0.22))
add(sfx, V.T_MONEY, boom(0.85))
add(sfx, V.T_MONEY, chime(86, 0.45, 2.2), pan=0.1)
add(sfx, V.T_MONEY + 0.02, shimmer(0.8, 0.3, 86))
add(sfx, V.VO['money'] + 1.1, pop(0.28, 700))
for k in range(14):
    add(sfx, V.VO['money'] + 3.0 + k / 22 + rng.uniform(-0.008, 0.008), key_click(0.12), pan=rng.uniform(-0.2, 0.2))
add(sfx, V.T_BED - 0.47, whoosh(0.5, 400, 7000, 0.4))
add(sfx, V.T_BED - 0.47, shimmer(0.4, 0.22, 91))
add(sfx, V.T_BED - 0.03, boom(0.5))
for tb_ in [6.9, 7.5, 8.2, 9.0, 9.8, 10.6, 11.4, 12.4, 13.2]:
    for j in range(rng.integers(2, 4)):
        add(sfx, tb_ + j * 0.11, bird(0.06), pan=rng.uniform(-0.7, 0.7))
v = V.VO['big']
for tl_ in (v - 0.05, v + 0.65, v + 1.4):
    add(sfx, tl_, whoosh(0.35, 800, 5000, 0.1))
add(sfx, v + 1.9, shimmer(0.4, 0.15, 93))
for tw, d, g in [(TL - 0.17, 0.3, 0.5), (TS - 0.12, 0.25, 0.42), (TB - 0.12, 0.25, 0.42), (TK - 0.17, 0.35, 0.32),
                 (TN - 0.2, 0.4, 0.28), (TM - 0.23, 0.45, 0.5), (TE - 0.17, 0.35, 0.42)]:
    add(sfx, tw, whoosh(d, 250, 6000, g))
for (ts_, tl_, m) in [(TL + 0.12, TL + 0.72, 81), (TS + 0.02, TS + 0.42, 83), (TB + 0.02, TB + 0.37, 86),
                      (TK + 0.05, TK + 0.4, 88)]:
    add(sfx, ts_, whoosh(tl_ - ts_ + 0.1, 900, 8000, 0.22), pan=-0.4)
    add(sfx, ts_, shimmer(tl_ - ts_, 0.13, m))
    add(sfx, tl_, chime(m, 0.36, 1.6), pan=0.2)
    add(sfx, tl_, chime(m + 7, 0.17, 1.2), pan=-0.2)
for tg in (TS + 0.42, TB + 0.37, TK + 0.4):
    add(sfx, tg, pop(0.3, 820))
    add(sfx, tg + 0.28, pop(0.2, 1500))
    add(sfx, tg + 0.3, tick(0.22))
for tc in (TL + 0.05, TS + 0.05, TB + 0.05, TK + 0.05):
    for j in range(3):
        add(sfx, tc + j * 0.045, tick(0.24))
for j in range(8):
    add(sfx, TN - 0.05 + j * 0.04, tick(0.18))
add(sfx, TN + 0.05, shimmer(0.5, 0.13, 79))
add(sfx, V.VO['breakfast'] + 1.2, pop(0.26, 600))
a = V.VO['asking']
for j in range(4):
    add(sfx, a + 0.35 + j * 0.12, key_click(0.07))
add(sfx, a + 0.85, pop(0.32, 1000))
add(sfx, a + 0.87, chime(88, 0.2, 1.0))
add(sfx, a + 1.4, pop(0.26, 650))
m0 = V.VO['message']
add(sfx, TM, boom(0.55))
add(sfx, m0 + 1.98, boom(0.62))
add(sfx, m0 + 1.98, shimmer(0.7, 0.26, 86))
add(sfx, m0 + 2.5, whoosh(0.6, 2000, 12000, 0.1))
add(sfx, m0 + 3.05, chime(81, 0.26, 1.6))
add(sfx, TE + 0.1, chime(74, 0.36, 2.0))
add(sfx, TE + 0.1, chime(81, 0.26, 2.0))
add(sfx, TE + 0.15, shimmer(0.8, 0.2, 86))
add(sfx, V.VO['end'] + 2.3, pop(0.22, 760))
sfx = reverb(sfx, wet=0.18, length=1.4, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{V.S}/tts/lines'


def vo_chain(x, sr):
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 85, 2)
    x = x + 0.35 * bp(x, 2500, 5500, 2)          # presence
    x = x - 0.12 * bp(x, 250, 450, 2)            # tame boxiness
    # gentle compressor (RMS, 4:1 above threshold)
    env = np.sqrt(lp(x ** 2, 25, 1).clip(1e-9))
    thr = 0.12 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 4) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name, t0 in V.VO.items():
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, t0, vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.07, length=0.8, key='vo_room')

# sidechain duck: music + sfx dip under the voice
env = np.abs(vo).max(axis=1)
att = lp(env, 12, 1)
att = np.maximum.accumulate(att[::-1])[::-1] * 0 + att  # keep shape; smoothing below handles release
rel_kernel = int(0.25 * SR)
smooth = signal.lfilter([1.0 / rel_kernel] * 1, [1, -(1 - 1.0 / rel_kernel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
duck_m = 1 - 0.74 * lvl     # ~ -11.7 dB under speech
duck_s = 1 - 0.55 * lvl

bed = music * 0.85 * duck_m[:, None] + sfx * 0.9 * duck_s[:, None]
mix = bed + vo * 1.5
np.save(f'{V.S}/audio/stems.npy', np.stack([bed.mean(1), (vo * 1.5).mean(1)]).astype(np.float32))
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
fade[-int(0.45 * SR):] = np.linspace(1, 0, int(0.45 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{V.S}/audio', exist_ok=True)
wavfile.write(f'{V.S}/audio/mix_vo_raw.wav', SR, (mix * 32767).astype(np.int16))
wavfile.write(f'{V.S}/audio/vo_only.wav', SR, (vo / max(1e-6, np.abs(vo).max()) * 0.9 * 32767).astype(np.int16))
print('wrote', f'{V.S}/audio/mix_vo_raw.wav')
