"""Soundtrack for Hulk Marketing "Same Business?" (per the concept PDF's sound notes).

A different clashing sound for each BEFORE item (honk, kazoo, ding, boing, squeak, clunk); one clean, identical tick
for every AFTER snap; a deep thump on the reveal. Music ("Fresh Air" by Kevin MacLeod, incompetech.com, CC BY 4.0):
loose and wobbly while the brand is a mess, nearly gone on forest black, then tight with an on-beat pulse once the system
arrives. Voice: Microsoft neural en-GB-RyanNeural. Master -14 LUFS.
"""
import os, sys, subprocess
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sqe'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, reverb, SR, tt, kick
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, squeak, clack, boom, bonk
import reel_sb as R

T, DUR, OFFS = R.T, R.DUR, R.OFFS
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ "before" clashing sounds
def honk(vel=0.25):
    t = tt(0.42)
    seg = (t < 0.18) | (t > 0.24)
    f = np.where(t < 0.2, 392, 330)
    x = signal.square(2 * np.pi * np.cumsum(f) / SR, 0.45) + 0.5 * signal.square(2 * np.pi * np.cumsum(f * 1.5) / SR)
    x = lp(x, 2400, 2) * seg * np.minimum(1, (0.42 - t) / 0.03)
    return x * vel


def kazoo(vel=0.2):
    t = tt(0.5)
    f = 300 * (1 + 0.25 * np.sin(np.pi * t / 0.5)) * (1 + 0.03 * np.sin(2 * np.pi * 7 * t))
    x = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    x = bp(x, 600, 3500, 2) + 0.3 * bp(np.random.default_rng(1).normal(0, 1, len(t)), 1500, 4000, 2)
    return x * np.sin(np.pi * t / 0.5) ** 0.5 * vel


def ding(vel=0.18, f=1975):
    t = tt(1.0)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 4) * vel


def boing(vel=0.22):
    t = tt(0.5)
    f = 180 + 260 * np.exp(-t * 6) * (1 + 0.5 * np.sin(2 * np.pi * 14 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * vel


def clunk(vel=0.3):
    a, b = thud(vel, 140), 0.6 * crinkle(0.25, vel * 0.4)
    n = max(len(a), len(b))
    a = np.pad(a, [(0, n - len(a))] + [(0, 0)] * (a.ndim - 1))
    b = np.pad(b, [(0, n - len(b))] + [(0, 0)] * (b.ndim - 1))
    if a.ndim != b.ndim:
        a = a if a.ndim == 2 else np.stack([a, a], 1)
        b = b if b.ndim == 2 else np.stack([b, b], 1)
    return a + b


def snap_tick(vel=0.22):
    """The one clean, identical 'after' tick."""
    t = tt(0.09)
    x = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) + 0.6 * np.sin(2 * np.pi * 3600 * t) * np.exp(-t * 120)
    return x * vel


# ------------------------------------------------------------------ music
TRACK = os.environ.get('TRACK', 'Fresh_Air.mp3')
mpath = os.path.join(HERE, '..', 'workspace_sol', 'music', TRACK)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mpath, '-ss', '0', '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)[:N]
if len(tr) < N:
    tr = np.concatenate([tr, np.zeros((N - len(tr), 2))])
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.09
ts_ = np.arange(N) / SR
before = np.clip((T['They'] - 0.05 - ts_) / 0.05, 0, 1)
dark = np.clip((ts_ - (T['They'] - 0.05)) / 0.05, 0, 1) * np.clip((T['So'] - 0.15 - ts_) / 0.3, 0, 1)
after = np.clip((ts_ - (T['So'] - 0.2)) / 0.3, 0, 1)
wob = 1 + 0.25 * np.sin(2 * np.pi * 3.3 * ts_)                          # loose, wobbly tremolo while messy
music = tr * (wob * before)[:, None] * 0.9 + lp(tr, 500, 2) * (dark * 0.5)[:, None] + tr * after[:, None] * 1.05
music *= np.clip(ts_ / 0.4, 0, 1)[:, None]
# tight on-beat pulse once the system arrives
bpm = 120
t_beat = T['So'] - 0.15
while t_beat < T['Build'] + 3.0:
    add(sfx, t_beat, np.stack([kick(0.22)] * 2, 1) if kick(0.22).ndim == 1 else kick(0.22))
    t_beat += 60 / bpm

# ------------------------------------------------------------------ SFX
add(sfx, 0.35, whoosh(0.5, 300, 3000, 0.08))                                # van slides in
add(sfx, T['same'] - 0.02, thud(0.3, 90))                                   # "Same business?" slams
add(sfx, T['van'] + 0.02, honk(0.24))
for key, fx in (('sign', kazoo(0.2)), ('card', ding(0.16)), ('website', boing(0.22)), ('instagram', squeak(0.3, 0.12)), ('invoice', clunk(0.3))):
    add(sfx, T[key] - 0.04, fx, pan=np.random.default_rng(len(key)).uniform(-0.3, 0.3))
for j, a in enumerate((T['sign'], T['card'], T['website'], T['instagram'], T['invoice'])):
    add(sfx, a - 0.42, whoosh(0.28, 400, 5000, 0.07), pan=(0.4 if j % 2 else -0.4))   # jolt cuts
add(sfx, T['invoice'] + 0.3, crinkle(0.4, 0.08))                            # the mess jostles
add(sfx, T['They'] - 0.05, boom(0.55))                                      # deep thump on the reveal
add(sfx, T['disjointed'] - 0.05, crinkle(0.6, 0.1))                         # the row cracks apart
add(sfx, T['trust'] + 0.05, whoosh(0.35, 800, 4000, 0.05))
add(sfx, T['So'] - 0.4, whoosh(0.45, 300, 6000, 0.1))                       # lime wipe
for key in ('logo', 'palette', 'typeface'):
    add(sfx, T[key] - 0.02, pop(0.18, 880))
add(sfx, T['Then'] - 0.35, whoosh(0.4, 250, 3500, 0.07))
for j in range(6):
    add(sfx, R.snap_time(j) + 0.02, snap_tick(0.24))                        # identical tick for every snap
add(sfx, T['A'] - 0.15, thud(0.25, 80))
add(sfx, T['sys2'], shimmer(0.8, 0.06, 88))
add(sfx, T['Build'] - 0.35, whoosh(0.45, 300, 5000, 0.08))
add(sfx, T['identity'] - 0.05, pop(0.22, 880))
add(sfx, T['identity'] + 0.6, shimmer(0.9, 0.07, 91))
sfx = reverb(sfx, wet=0.08, length=0.6, key='room')

# ------------------------------------------------------------------ voice
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x + 0.1 * bp(x, 2500, 6000, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
add(vo, OFFS, x, 1.0)
vo = reverb(vo, wet=0.03, length=0.4, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.55 * lvl)[:, None] + sfx * (1 - 0.2 * lvl)[:, None]
mix = bed + vo * 1.6
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.2 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.02 * SR)] = np.linspace(0, 1, int(0.02 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/sb_mix.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/sb_mix.wav', 'DUR', DUR)
