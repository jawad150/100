"""Soundtrack for "Support Update Available": light, confident 120 BPM bed + phone/UI SFX + ducked voiceover.

Timing comes from reel_su.py so the buzz, taps, check pops and toast land on their frames.
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
import reel_su as RS

T, VO = RS.T, RS.VO
DUR = RS.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(41)
B = 0.5
BAR = 2.0


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def buzz(dur=0.35, v=0.5):
    """Phone vibration: low square-ish hum with a tremolo."""
    t = tt(dur)
    x = np.tanh(4 * np.sin(2 * np.pi * 150 * t)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 22 * t)))
    return lp(x, 900) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03) * v


# ------------------------------------------------------------------ music (F major: I - V - vi - IV)
CH = [(41, [65, 69, 72, 77]), (36, [64, 67, 72, 76]), (38, [62, 65, 69, 74]), (34, [62, 65, 70, 74])]
ARP = [0, 1, 2, 3, 2, 1, 2, 3]
# hook + lock screen: filtered pad and ticking pulse (anticipation)
add(music, 0.0, pad([65, 69, 72], T['check'] + 0.4, vel=0.2, bright=1200))
for k in range(int(T['check'] / B)):
    add(music, k * B, tick(0.12), pan=0.2 * (-1) ** k)
START, END = T['check'], T['cta']
bi = 0
while True:
    t0 = START + bi * BAR
    if t0 >= END:
        break
    root, tones = CH[bi % 4]
    d = min(BAR, END - t0)
    add(music, t0, pad(tones[:3], d + 0.4, vel=0.24, bright=2000))
    add(music, t0, bass(root, d, 0.38))
    for e8 in range(8):
        te = t0 + e8 * B / 2
        if te >= END - 0.02:
            break
        add(music, te, piano(tones[ARP[e8]] + (12 if e8 in (3, 7) else 0), 0.7, 0.2 if e8 % 2 == 0 else 0.14),
            pan=-0.3 + 0.6 * (e8 % 2))
    bi += 1
i = 0
while True:
    tb = START + i * B
    if tb >= END:
        break
    care = T['care'] <= tb < T['install']
    add(music, tb, kick((0.48 if i % 4 == 0 else 0.34) * (0.6 if care else 1.0)))
    add(music, tb + B / 2, shaker(0.12), pan=0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.11), pan=-0.1)
    i += 1
add(music, END, pad([65, 69, 72, 77, 81], DUR - END, vel=0.4, bright=2400))
add(music, END, bass(41, DUR - END - 0.2, 0.4))
for j, m in enumerate([65, 69, 72, 77, 81, 84]):
    add(music, END + 0.04 + j * 0.06, piano(m, 2.4, 0.24), pan=-0.3 + j * 0.12)
music = reverb(music, wet=0.22, length=2.0, key='hall')

# ------------------------------------------------------------------ SFX
add(sfx, 0.0, riser(T['lock'], 0.32))
for c in range(4):
    add(sfx, c * 0.25, snap(0.16), pan=(-1) ** c * 0.3)
    add(sfx, c * 0.25, tick(0.24))
    add(sfx, c * 0.25 + 0.01, whoosh(0.12, 2000, 9000, 0.12))
add(sfx, T['lock'], boom(0.55))
add(sfx, T['lock'], whoosh(0.6, 300, 4000, 0.25))
for tb in (RS.NOTIF - 0.05, RS.NOTIF + 0.2):
    add(sfx, tb, buzz(0.2, 0.5))
add(sfx, RS.NOTIF + 0.05, chime(84, 0.3, 1.4), pan=0.1)
add(sfx, RS.NOTIF + 0.12, chime(91, 0.16, 1.0), pan=-0.1)
add(sfx, T['lock'] + 1.3, whoosh(0.7, 300, 2500, 0.1), pan=0.4)
for tc in (T['tap'], RS.TAP_INSTALL):
    add(sfx, tc, key_click(0.5))
    add(sfx, tc + 0.01, pop(0.42, 700))
    add(sfx, tc + 0.03, shimmer(0.5, 0.16, 88))
add(sfx, T['tap'] + 0.35, riser(0.6, 0.22))
add(sfx, T['check'] - 0.15, whoosh(0.3, 400, 8000, 0.4))
add(sfx, T['check'], boom(0.4))
for j, q in enumerate(RS.Q_T):                       # each question card + its spinner
    add(sfx, q, whoosh(0.22, 900, 6000, 0.12), pan=0.3)
    add(sfx, q + 0.05, pop(0.2, 650 + 80 * j))
    for k in range(3):
        add(sfx, q + 0.1 + k * 0.09, tick(0.08))
add(sfx, T['notes'] - 0.18, whoosh(0.35, 250, 7000, 0.4))
add(sfx, T['notes'] + 0.05, whoosh(0.5, 2500, 400, 0.18))
for j, c in enumerate(RS.CHK_T):                     # satisfying check cascade on eighth notes
    add(sfx, c, pop(0.42, 820 + 60 * j))
    add(sfx, c + 0.02, chime(77 + 2 * j, 0.26, 1.2), pan=-0.3 + 0.12 * j)
add(sfx, RS.OFSTED_T, boom(0.45))
add(sfx, RS.OFSTED_T, shimmer(0.7, 0.24, 86))
add(sfx, RS.IND_T, shimmer(0.6, 0.16, 88))
add(sfx, RS.IND_T, pop(0.2, 900))
add(sfx, RS.ALL_T, pop(0.4, 520))
add(sfx, RS.ALL_T + 0.05, chime(84, 0.3, 1.6))
add(sfx, RS.ALL_T + 0.05, chime(89, 0.16, 1.4))
add(sfx, T['care'], boom(0.35))
add(sfx, T['care'], shimmer(0.9, 0.14, 81))
add(sfx, T['care'] + 0.3, pop(0.3, 900))
for k in range(8):
    add(sfx, RS.CARE_CUT - 1.0 + k * 0.12, key_click(0.06), pan=-0.3)
add(sfx, RS.CARE_CUT - 0.15, whoosh(0.3, 300, 6000, 0.3))
add(sfx, RS.CARE_CUT, boom(0.3))
add(sfx, RS.CARE_CUT + 0.1, pop(0.3, 700))
add(sfx, RS.CARE_CUT + 0.45, chime(86, 0.18, 1.0))
add(sfx, T['care'] + 0.5, whoosh(0.4, 600, 4000, 0.1))
add(sfx, T['install'] - 0.18, whoosh(0.35, 250, 7000, 0.4))
add(sfx, T['install'] + 0.05, pop(0.3, 600))
add(sfx, T['install'] + 0.55, whoosh(0.3, 800, 5000, 0.2))      # button flips to "Explore a transfer"
add(sfx, T['install'] + 0.7, tick(0.3))
add(sfx, RS.TAP_INSTALL + 0.1, riser(RS.TOAST_T - RS.TAP_INSTALL - 0.1, 0.3))
add(sfx, RS.TAP_INSTALL + 0.1, shimmer(RS.TOAST_T - RS.TAP_INSTALL, 0.22, 84))
add(sfx, RS.TOAST_T, boom(0.6))
add(sfx, RS.TOAST_T + 0.15, pop(0.45, 800))
for k, m in enumerate([77, 81, 84, 89]):
    add(sfx, RS.TOAST_T + 0.15 + k * 0.07, chime(m, 0.24, 1.6), pan=-0.3 + 0.2 * k)
add(sfx, T['cta'] - 0.1, whoosh(0.4, 300, 9000, 0.35))
add(sfx, T['cta'] + 0.05, shimmer(1.0, 0.22, 86))
add(sfx, T['cta'] + 0.6, chime(81, 0.26, 2.0))
add(sfx, T['cta'] + 0.95, pop(0.22, 760))
add(sfx, T['cta'] + 1.1, pop(0.18, 900))
sfx = reverb(sfx, wet=0.15, length=1.2, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{RS.S}/tts/lines'


def vo_chain(x, sr):
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 85, 2)
    x = x + 0.2 * bp(x, 2500, 5500, 2)               # gentle presence, keeps it soft
    x = x - 0.1 * bp(x, 250, 450, 2)
    x = lp(x, 11000, 2)                               # tame sibilance
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))       # slow detector -> no pumping
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
bed = music * 0.85 * (1 - 0.72 * lvl)[:, None] + sfx * 0.9 * (1 - 0.5 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(RS.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2      # smooth equal-power style fade-out
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{RS.S}/audio', exist_ok=True)
wavfile.write(f'{RS.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{RS.S}/audio/mix_raw.wav')
