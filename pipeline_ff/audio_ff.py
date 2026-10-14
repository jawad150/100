"""Soundtrack for "The Fostering Flow": light, optimistic 120 BPM bed + UI SFX + ducked voiceover (48 kHz).

Timing comes from reel_ff.py (scene times, checks, clicks, VO starts), so every tick lands on its beat.
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
                      shimmer, lp, hp, bp, reverb, SR)
import reel_ff as RF

T, VO, CHECKS = RF.T, RF.VO, RF.CHECKS
DUR = RF.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(31)
B = 0.5
BAR = 2.0


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ music (D major: I - V - vi - IV)
CH = [(50, [62, 66, 69, 74]), (45, [61, 64, 69, 73]), (47, [59, 62, 66, 71]), (43, [59, 62, 67, 71])]
ARP = [0, 1, 2, 3, 2, 1, 2, 3]
MEL = {0: [78, 76, 74], 1: [76, 73, 69], 2: [74, 76, 78], 3: [79, 78, 74]}

# hook: tension bed under the montage, then a soft pad under the glass button
add(music, 0.0, pad([62, 66, 69], RF.HOOK_MONTAGE + 0.3, vel=0.18, bright=1100))
add(music, RF.HOOK_MONTAGE, pad([62, 66, 69, 74], T['flow'] - RF.HOOK_MONTAGE + 0.5, vel=0.26, bright=1500))
for k in range(int((T['flow'] - RF.HOOK_MONTAGE) / B)):
    tb = RF.HOOK_MONTAGE + k * B
    add(music, tb, piano([74, 78, 81, 78][k % 4], 0.9, 0.16), pan=0.2 * (-1) ** k)

START, END = T['flow'], T['cta']
bi = 0
while True:
    t0 = START + bi * BAR
    if t0 >= END:
        break
    root, tones = CH[bi % 4]
    d = min(BAR, END - t0)
    full = t0 >= T['s1']
    add(music, t0, pad(tones[:3], d + 0.5, vel=0.24, bright=1900))
    add(music, t0, bass(root, d, 0.36 if full else 0.2))
    for e8 in range(8):
        te = t0 + e8 * B / 2
        if te >= END - 0.02:
            break
        m = tones[ARP[e8]] + (12 if e8 in (3, 7) else 0)
        add(music, te, piano(m, 0.8, 0.22 if e8 % 2 == 0 else 0.15), pan=-0.3 + 0.6 * (e8 % 2))
    if full:
        for j, m in enumerate(MEL[bi % 4]):
            tm = t0 + 2 * B + j * B * 0.5
            add(music, tm, piano(m, 1.2, 0.12), pan=0.1)
    bi += 1

i = 0
while True:
    tb = T['s1'] + i * B
    if tb >= END:
        break
    lift = 1.15 if T['s5'] <= tb < END else 1.0
    add(music, tb, kick((0.5 if i % 4 == 0 else 0.36) * lift))
    add(music, tb + B / 2, shaker(0.13 * lift), pan=0.3)
    add(music, tb + B / 4, shaker(0.06), pan=-0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.12 * lift), pan=-0.1)
    i += 1
# drop the kick for a beat before "approved" so the moment lands
music_gap = (CHECKS[4] - 0.5, CHECKS[4])

# end: bright resolving chord, then let it ring
add(music, END, pad([62, 66, 69, 74, 78], DUR - END, vel=0.40, bright=2400))
add(music, END, bass(38, DUR - END - 0.2, 0.42))
for j, m in enumerate([62, 66, 69, 74, 78, 81]):
    add(music, END + 0.04 + j * 0.06, piano(m, 2.8, 0.24), pan=-0.3 + j * 0.12)
for k in range(8):
    add(music, RF.CLICK_CTA + 0.25 + k * B, piano([86, 81, 78, 74, 81, 78, 74, 69][k], 1.2, 0.1), pan=0.25)
music = reverb(music, wet=0.24, length=2.2, key='hall')
g0, g1 = int(music_gap[0] * SR), int(music_gap[1] * SR)
music[g0:g1] *= np.linspace(1, 0.45, g1 - g0)[:, None]

# ------------------------------------------------------------------ SFX
add(sfx, 0.0, riser(RF.HOOK_MONTAGE, 0.30))
for c in range(6):
    add(sfx, c * 0.25, tick(0.24))
    add(sfx, c * 0.25, snap(0.14), pan=(-1) ** c * 0.3)
add(sfx, RF.HOOK_MONTAGE, boom(0.6))
add(sfx, RF.HOOK_MONTAGE, shimmer(0.7, 0.2, 86))
add(sfx, RF.HOOK_MONTAGE + 0.7, whoosh(0.8, 300, 2500, 0.12), pan=0.4)        # cursor glides in
for tc in (RF.CLICK_HOOK, RF.CLICK_CTA):
    add(sfx, tc, key_click(0.5))
    add(sfx, tc + 0.01, pop(0.45, 700))
    add(sfx, tc + 0.02, boom(0.35))
    add(sfx, tc + 0.05, shimmer(0.5, 0.18, 88))
add(sfx, T['flow'] - 0.25, whoosh(0.35, 400, 7000, 0.4))
add(sfx, T['flow'], boom(0.45))
for k in range(5):                                                              # rows slide in
    add(sfx, T['flow'] + 0.45 + k * 0.12, tick(0.2))
    add(sfx, T['flow'] + 0.5 + k * 0.12, pop(0.12, 900 + 120 * k))
for key in ('s1', 's2', 's3', 's4'):
    add(sfx, T[key] - 0.2, whoosh(0.35, 250, 6500, 0.42))
    add(sfx, T[key] + 0.12, tick(0.2))
add(sfx, T['s5'] - 0.25, whoosh(0.45, 300, 9000, 0.42))
add(sfx, T['s5'], shimmer(0.6, 0.18, 86))
for j, c in enumerate(CHECKS):                                                  # each tick lands on the beat
    add(sfx, c, pop(0.42, 820))
    add(sfx, c + 0.02, chime(81 + 2 * j, 0.32, 1.4), pan=0.15)
    add(sfx, c + 0.05, chime(88 + 2 * j, 0.14, 1.0), pan=-0.15)
    add(sfx, c + 0.1, tick(0.2))
s1, s2, s3, s4, s5 = (T[k] for k in ('s1', 's2', 's3', 's4', 's5'))
# step 1: chat
add(sfx, s1 + 0.2, pop(0.3, 600))
add(sfx, s1 + 0.55, pop(0.3, 1000))
for k in range(6):
    add(sfx, s1 + 1.15 + k * 0.1, key_click(0.07), pan=-0.3)
add(sfx, s1 + 1.75, pop(0.32, 750))
# step 2: house drop, calendar flip, pin drop
add(sfx, s2 + 0.05, whoosh(0.5, 2000, 300, 0.18))
add(sfx, s2 + 0.55, boom(0.55))
add(sfx, s2 + 0.55, pop(0.3, 300))
add(sfx, s2 + 0.4, whoosh(0.3, 900, 5000, 0.14), pan=0.4)
add(sfx, s2 + 1.0, whoosh(0.3, 1200, 6000, 0.16), pan=0.4)
add(sfx, s2 + 1.2, tick(0.3))
add(sfx, s2 + 1.6, whoosh(0.5, 2500, 400, 0.14))
add(sfx, s2 + 2.15, boom(0.4))
add(sfx, s2 + 2.15, pop(0.35, 500))
add(sfx, s2 + 2.2, chime(86, 0.18, 1.0))
# step 3: form typing, training cards
add(sfx, s3 + 0.15, pop(0.25, 700))
for j, val in enumerate(['Ready to make a difference', 'A spare bedroom', 'Partner and two children']):
    tf = s3 + 0.6 + j * 0.42
    for k in range(0, len(val), 3):
        add(sfx, tf + k / 40, key_click(0.06 + 0.02 * rng.random()), pan=rng.uniform(-0.2, 0.2))
    add(sfx, tf + len(val) / 40 + 0.05, pop(0.18, 1300))
for j in range(2):
    add(sfx, s3 + 1.6 + j * 0.35, whoosh(0.3, 800, 6000, 0.16), pan=0.5)
    add(sfx, s3 + 2.2 + j * 0.35, pop(0.22, 1100))
# step 4: profile + tags
add(sfx, s4 + 0.15, pop(0.25, 650))
add(sfx, s4 + 0.45, pop(0.3, 900))
for j in range(4):
    add(sfx, VO['assess'] + 0.35 + j * 0.42, pop(0.26, 900 + 150 * j), pan=(-1) ** j * 0.3)
# step 5: ring fills, approved
add(sfx, s5 + 0.4, riser(CHECKS[4] - s5 - 0.4, 0.28))
add(sfx, CHECKS[4], boom(0.8))
add(sfx, CHECKS[4], shimmer(1.2, 0.32, 86))
for k, m in enumerate([74, 78, 81, 86]):
    add(sfx, CHECKS[4] + 0.05 + k * 0.07, chime(m, 0.22, 1.6), pan=-0.3 + 0.2 * k)
add(sfx, CHECKS[4] + 0.25, whoosh(0.45, 600, 5000, 0.2))
# support bento snaps in
add(sfx, T['sup'] - 0.15, whoosh(0.4, 4000, 400, 0.3))
for j in range(5):
    add(sfx, T['sup'] + 0.25 + j * 0.2, pop(0.28, 700 + 110 * j), pan=(-1) ** j * 0.25)
    add(sfx, T['sup'] + 0.25 + j * 0.2, tick(0.16))
# CTA
add(sfx, T['cta'] - 0.35, whoosh(0.4, 300, 9000, 0.4))
add(sfx, T['cta'], boom(0.55))
add(sfx, RF.CLICK_CTA + 0.25, shimmer(1.0, 0.25, 86))
add(sfx, RF.CLICK_CTA + 0.3, chime(81, 0.3, 2.0))
add(sfx, RF.CLICK_CTA + 1.0, pop(0.22, 760))
sfx = reverb(sfx, wet=0.16, length=1.2, key='room')

# ------------------------------------------------------------------ voiceover (same chain as the OF voiceover cut)
LINES = f'{RF.S}/tts/lines'


def vo_chain(x, sr):
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 85, 2)
    x = x + 0.35 * bp(x, 2500, 5500, 2)
    x = x - 0.12 * bp(x, 250, 450, 2)
    env = np.sqrt(lp(x ** 2, 25, 1).clip(1e-9))
    thr = 0.12 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 4) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name, t0 in VO.items():
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, t0, vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.06, length=0.8, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.25 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
duck_m = 1 - 0.72 * lvl
duck_s = 1 - 0.5 * lvl
bed = music * 0.85 * duck_m[:, None] + sfx * 0.9 * duck_s[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
fade[-int(0.4 * SR):] = np.linspace(1, 0, int(0.4 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RF.S}/audio', exist_ok=True)
wavfile.write(f'{RF.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RF.S}/audio/mix_raw.wav')
