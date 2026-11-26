"""Soundtrack for BMHC Wrapped 2026: Sonia's narration on top, sound-led (no music, per the BMHC guide): UI clicks,
transition whooshes, slam hits, counter ticks, a radio dial sweep, an airy aura shimmer, wind under the snow-to-autumn
dissolve, room tone. Master -14 LUFS at encode."""
import os, sys, subprocess
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sqe'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as AO
from audio_of import lp, hp, bp, reverb, SR, chime
from sfx_palette import pop, whoosh, tick
import reel_wrapped as R

DUR = R.DUR
N = int(SR * DUR)
AO.DUR, AO.N = DUR, N
sfx = np.zeros((N, 2))
T = R.T
rng = np.random.default_rng(3)


def add(t0, x, g=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        AO.add(sfx, t0, x, g, pan)


def thud(f=70, dur=0.25, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    x = np.sin(2 * np.pi * f * t * (1 - 0.3 * t / dur)) * np.exp(-t * 18)
    return np.stack([x, x], 1) * vel


def click(vel=0.35):
    t = np.arange(int(SR * 0.04)) / SR
    x = rng.normal(0, 1, len(t)) * np.exp(-t * 180)
    x = bp(x, 1500, 6000) * vel
    return np.stack([x, x], 1)


def ticks(t0, t1, n=14, vel=0.18):
    """Counter ticks that speed up towards the landing value."""
    for i in range(n):
        u = i / (n - 1)
        tt = t0 + (t1 - t0) * (1 - (1 - u) ** 2)
        add(tt, tick(vel * (0.6 + 0.4 * u)) if callable(tick) else click(vel), 1.0, 0.15 * math.sin(i))


def dial(dur=1.2):
    t = np.arange(int(SR * dur)) / SR
    n = rng.normal(0, 1, len(t))
    f = 500 + 2500 * t / dur
    sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    stat = bp(n, 1200, 5000) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
    env = np.clip(t / 0.1, 0, 1) * np.clip((dur - t) / 0.3, 0, 1)
    x = (sweep + stat) * env
    return np.stack([x, x * 0.9], 1)


def wind(dur=3.0):
    t = np.arange(int(SR * dur)) / SR
    n = rng.normal(0, 1, len(t))
    x = lp(n, 600) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t)) * np.sin(np.pi * t / dur) * 0.25
    return np.stack([x, np.roll(x, 400)], 1)


import math
D = R.D
# intro
add(0.05, whoosh(0.7, 200, 2000, 0.15))
for i in range(3):
    add(0.4 + 0.15 * i, whoosh(0.35, 600, 3000, 0.08), pan=(-0.3 + 0.3 * i))
for i, tt in enumerate((1.4, 1.6, 1.8)):
    add(tt, pop(0.14, 700 + 150 * i))
add(3.2, click(0.45))
# transitions
add(T['s1'] - D, whoosh(0.9, 150, 3500, 0.22))                          # zoom-through
add(T['s2'] - D, whoosh(0.6, 400, 5000, 0.2), pan=-0.4)                   # story push
add(T['s3'] - D, whoosh(0.7, 300, 2500, 0.18))                            # iris
for i in range(4):
    add(T['s4'] - D + 0.08 * i, whoosh(0.3, 500, 4000, 0.09), pan=(-0.4 + 0.27 * i))   # four-bar wipe
add(T['s5'] - 0.02, thud(65, 0.25, 0.45))                                 # zoom punch
add(T['s5'] - D, whoosh(0.45, 200, 3000, 0.15))
add(T['s6'] - D, whoosh(1.0, 150, 1500, 0.12, rev=True))                  # blur dissolve swell
add(T['s7'] - D, whoosh(0.9, 120, 1800, 0.16))                            # blob morph
add(T['s8'] - D, whoosh(0.6, 300, 4500, 0.2))                             # whip up
add(T['end'] - 0.45, whoosh(0.6, 200, 3000, 0.22, rev=True))              # circle wipe
# slide details
for k, dt in enumerate((0.25, 0.45, 0.7)):
    add(T['s1'] + dt, thud(90 + 20 * k, 0.15, 0.3))
    add(T['s1'] + dt, pop(0.1, 500 + 200 * k))
for i in range(5):
    add(T['s1'] + 1.2 + 0.12 * i, pop(0.1, 900 + 80 * i), pan=(-0.4 + 0.2 * i))
ticks(T['s2'] + 0.6, R.WT('52', 'v3') + 0.1, 16)
add(R.WT('52', 'v3') + 0.12, chime(84, 0.05, 1.6))
add(R.WT('fridays', 'v3'), thud(80, 0.2, 0.35))
add(T['s3'] + 0.3, dial(1.3), 0.8)
add(R.WT('heritage', 'v4'), thud(90, 0.15, 0.25))
add(R.WT('radio', 'v4'), thud(100, 0.15, 0.25))
add(T['s4'] + 0.25, thud(85, 0.2, 0.3))
for i in range(5):
    add(R.INFO['lines'][f't{i + 1}'][0] - 0.1, whoosh(0.25, 800, 5000, 0.07), pan=0.4)
    add(R.INFO['lines'][f't{i + 1}'][0] + 0.15, pop(0.12, 900))
for wd in ('130', '14', 'over'):
    t0 = R.WT(wd, 'v6') - 0.1
    ticks(t0, t0 + 0.9, 10, 0.12)
    add(t0, thud(85, 0.18, 0.3))
add(R.WT('welcoming', 'v7'), chime(79, 0.04, 2.2))
add(R.WT('welcoming', 'v7') + 0.1, chime(86, 0.025, 2.0))
add(T['s7'] + 0.2, wind(3.2), 0.9)
add(R.WT('one', 'v8'), thud(70, 0.2, 0.25))
add(R.WT('four', 'v8'), thud(70, 0.2, 0.25))
add(T['s8'] + 0.2, whoosh(0.5, 400, 2500, 0.1))
add(T['s8'] + 1.65, click(0.45))
add(T['end'] + 0.2, chime(76, 0.04, 2.6))
sfx = reverb(sfx, wet=0.14, length=1.0, key='room')

rt = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '12', '-i', os.path.join(R.ROOT, 'workspace_ai', 'sfx', '3080.mp3'), '-t', str(DUR + 0.5),
                     '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
rt = np.frombuffer(rt, np.float32).reshape(-1, 2).astype(np.float64)[:N]
rt = np.pad(rt, ((0, N - len(rt)), (0, 0))) / max(1e-6, np.sqrt(np.mean(rt ** 2))) * 0.008

x, sr = sf.read(f'{R.S}/tts/vo.wav')
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 75, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
v[:min(N, len(x))] = x[:N]
vo = reverb(np.stack([v, v], 1), wet=0.05, length=0.5, key='vo')
e = np.abs(vo).max(1)
rel = int(0.25 * SR)
sm = signal.lfilter([1 / rel], [1, -(1 - 1 / rel)], e)
duck = np.clip(sm / (sm.max() + 1e-9) * 4, 0, 1)
mix = sfx * (1 - 0.35 * duck)[:, None] + rt + vo * 1.4
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(0.8 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix.wav', SR, (mix * 32767).astype(np.int16))
print('wrote mix', DUR)
