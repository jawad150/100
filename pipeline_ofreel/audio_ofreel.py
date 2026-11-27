"""Soundtrack for OF Closer than you think (adapted from the BMHC Wrapped mix): Sonia's narration on top, sound-led (no music, per the BMHC guide): UI clicks,
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
sys.path.insert(0, HERE)
import importlib.util as _u
_spec = _u.spec_from_file_location('reel_ofreel', os.path.join(HERE, 'reel_of.py'))
R = _u.module_from_spec(_spec)
_spec.loader.exec_module(R)

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
from sfx_palette import key_click
# opening + search typing
add(0.0, whoosh(0.6, 200, 1800, 0.12))
q = 'foster carer near me'
for i in range(len(q)):
    add(T['s1'] + 0.25 + 0.35 + i * 0.065, key_click(0.12), 0.9, 0.1 * math.sin(i))
add(T['s1'] + 2.05, pop(0.12, 900))
add(R.WT('land', 'v1') - 0.25, whoosh(0.4, 600, 3000, 0.06))
# zoom-through, pin drop
add(T['s2'] - D, whoosh(0.8, 150, 3500, 0.2))
add(T['s2'] + 0.05, whoosh(0.5, 2500, 400, 0.18))                        # falling whistle
add(T['s2'] + 0.55, thud(55, 0.45, 0.8))
add(T['s2'] + 0.56, wind(0.9), 0.8)
add(T['s2'] + 1.0, whoosh(0.35, 400, 2500, 0.08))
# cards
add(T['s3'] - D, whoosh(0.6, 400, 5000, 0.2), pan=-0.4)                  # whip
for wd in ('answers', 'spare', 'time'):
    add(R.WT(wd, 'v3') - 0.15, pop(0.18, 800))
# plane + tags
add(T['s4'] - D, whoosh(1.0, 150, 1500, 0.12, rev=True))                 # light-leak dissolve
add(T['s4'] + 0.4, whoosh(2.5, 300, 1800, 0.08), pan=0.3)                 # the plane's flight
for wd in ('culture', 'faith', 'language'):
    add(R.WT(wd, 'v4') - 0.1, pop(0.14, 1000))
# trail wipe, counter
add(T['s5'] - D, whoosh(0.7, 200, 3000, 0.22))
ticks(T['s5'] + 0.3, R.WT('6', 'v5') + 0.45, 18, 0.12)
add(R.WT('6', 'v5') + 0.45, thud(75, 0.25, 0.45))
# support
add(T['s6'] - D, whoosh(0.6, 300, 4500, 0.18))
for wd in ('training', 'advice', 'published'):
    add(R.WT(wd, 'v6') - 0.1, whoosh(0.3, 800, 5000, 0.06), pan=0.3)
add(R.WT('allowances', 'v6') + 0.5, whoosh(0.3, 800, 5000, 0.06), pan=0.3)
# end card
add(T['end'] - D, whoosh(0.6, 200, 3000, 0.2, rev=True))
url = 'organicfostering.co.uk'
for i in range(len(url)):
    add(T['end'] + 1.9 + 0.35 + i * 0.065, key_click(0.1), 0.9)
bt0 = max(T['end'] + 2.6, R.WT('start', 'v7'))
add(bt0, pop(0.2, 700))
add(bt0 + 1.9, click(0.5))
add(T['end'] + 0.3, chime(79, 0.035, 2.4))
sfx = reverb(sfx, wet=0.14, length=1.0, key='room')

mu = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(R.ROOT, 'workspace_sol', 'music', 'Wholesome.mp3'), '-t', str(DUR + 1),
                     '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
mu = np.frombuffer(mu, np.float32).reshape(-1, 2).astype(np.float64)[:N]
mu = np.pad(mu, ((0, N - len(mu)), (0, 0)))
mu = mu / max(1e-6, np.abs(mu).max())
tt_ = np.arange(N) / SR
mus = mu * (np.clip(tt_ / 1.2, 0, 1) * np.clip((DUR - tt_) / 2.0, 0, 1))[:, None] * 0.16
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
mix = sfx * (1 - 0.35 * duck)[:, None] + mus * (1 - 0.5 * duck)[:, None] + rt + vo * 1.4
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(0.8 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix.wav', SR, (mix * 32767).astype(np.int16))
print('wrote mix', DUR)
