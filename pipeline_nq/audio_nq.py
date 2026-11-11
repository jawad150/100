"""Soundtrack for Organic Fostering "No Qualification Needed" (3D studio version).

Bait: town ambience, then a cold low drone in the stern studio with spotlight clunks and REQUIRED ticks. Switch: the
stamp slams (boom + thud + glass hit), shockwave whoosh, confetti pops, and the music ("Inspired" by Kevin MacLeod,
incompetech.com, CC BY 4.0, credit in the caption) kicks in bright. Each carousel turn: a whoosh and a pop; spiral of
light: shimmer; ring portal: whoosh; end card: chime. Voice: ElevenLabs (Clara V). Gentle fade. Master -14 LUFS.
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
from audio_of import lp, hp, bp, reverb, SR, chime
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, clack, boom, clang
import reel_nq as R

K, SH, DUR = R.K, R.SH, R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
rng = np.random.default_rng(9)
ts_ = np.arange(N) / SR
SLAM = K['noqual'] - 0.15


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ music: kicks in on the slam
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Inspired.mp3'), '-ss', '20',
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.08
music = np.zeros((N, 2))
i0 = int(SLAM * SR)
n = min(len(tr), N - i0)
music[i0:i0 + n] = tr[:n]
music *= (np.clip((ts_ - SLAM) / 0.05, 0, 1) * (1 + 0.3 * np.clip((ts_ - SH['end'][0]) / 1.0, 0, 1)))[:, None]

# ------------------------------------------------------------------ ambience
noise = rng.normal(0, 1, (N, 2))
town = np.clip((SH['walk'][1] + 0.2 - ts_) / 0.4, 0, 1)
amb += lp(noise, 900, 2) * 0.016 * town[:, None]
stern = np.clip((ts_ - SH['write'][0]) / 0.3, 0, 1) * np.clip((SLAM - ts_) / 0.05, 0, 1)
drone = (np.sin(2 * np.pi * 55 * ts_) + 0.5 * np.sin(2 * np.pi * 82.4 * ts_) + 0.3 * np.sin(2 * np.pi * 110.3 * ts_)) * 0.02
amb += (drone[:, None] + lp(noise, 300, 2) * 0.01) * stern[:, None]
riser = np.clip((ts_ - (SLAM - 1.0)) / 1.0, 0, 1) * (ts_ < SLAM)
amb += bp(noise, 2000, 8000, 2) * 0.03 * (riser ** 2)[:, None]

# ------------------------------------------------------------------ SFX
add(sfx, K['before'] + 0.5, whoosh(0.5, 400, 3000, 0.05))                 # cap flies in
add(sfx, K['before'] + 0.8, pop(0.14, 760))
add(sfx, SH['write'][0] - 0.25, whoosh(0.5, 300, 4000, 0.09))               # card flip
add(sfx, SH['write'][0] - 0.05, clack(0.1))
for j in range(3):
    add(sfx, SH['write'][0] + 0.15 * j, whoosh(0.4, 500, 3000, 0.04), pan=(-0.5 + 0.5 * j))
add(sfx, SH['entry'][0] - 0.2, whoosh(0.45, 300, 5000, 0.08))               # zoom-through
for j in range(3):                                                         # spotlights clunk on, tags tick
    add(sfx, SH['entry'][0] + 0.1 + j * 0.12, key_click(0.12), pan=(-0.5 + 0.5 * j))
    add(sfx, SH['entry'][0] + 0.55 + j * 0.12, tick(0.08), pan=(-0.5 + 0.5 * j))
add(sfx, K['withus'] - 0.05, ping(0.05, 1568))                             # "...with us." wink
add(sfx, SLAM, boom(0.9))                                                  # THE SLAM
add(sfx, SLAM, thud(0.6, 60))
add(sfx, SLAM + 0.01, clang(0.12))
add(sfx, SLAM + 0.02, whoosh(0.9, 2000, 200, 0.12))
for k in range(10):                                                        # confetti
    add(sfx, SLAM + 0.05 + rng.uniform(0, 0.6), pop(0.06, rng.uniform(700, 1400)), pan=rng.uniform(-0.8, 0.8))
add(sfx, SLAM + 0.4, shimmer(1.2, 0.1, 86))
add(sfx, SH['top7'][0] - 0.15, whoosh(0.3, 600, 7000, 0.07))
add(sfx, K['approval'] - 0.3, whoosh(0.6, 300, 2500, 0.06))                # giant 7 spins up
add(sfx, K['approval'], pop(0.22, 640))
add(sfx, SH['items'][0] - 0.25, whoosh(0.5, 300, 5000, 0.08))
for j, ti in enumerate(K['items']):
    if j:
        add(sfx, ti - 0.35, whoosh(0.45, 250, 2600, 0.06), pan=0.3)          # carousel turns
    add(sfx, ti + 0.05, pop(0.18, 700 + 60 * j))
    add(sfx, ti + 0.1, ping(0.03, 1760 + 120 * j))
add(sfx, SH['more'][0] - 0.25, whoosh(0.55, 300, 4000, 0.08))              # cube turn
add(sfx, SH['more'][0] + 0.1, shimmer(1.6, 0.08, 84))                      # spiral of light
for j in range(3):
    add(sfx, SH['more'][0] + 0.45 + j * 0.25, pop(0.14, 760 + 90 * j), pan=(-0.4 + 0.4 * j))
add(sfx, SH['end'][0] - 0.3, whoosh(0.7, 200, 3500, 0.1))                  # ring portal
add(sfx, SH['end'][0] + 0.3, chime(84, 0.1, 2.4))
add(sfx, SH['end'][0] + 0.7, pop(0.2, 900))
add(sfx, SH['end'][0] + 1.5, shimmer(0.9, 0.06, 91))
sfx = reverb(sfx, wet=0.12, length=0.8, key='room')

# ------------------------------------------------------------------ voice
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
m = min(len(x), N)
v[:m] = x[:m]
vo = np.stack([v, v], 1) + 0.05 * np.stack([bp(v, 2500, 6000, 2)] * 2, 1)
vo = reverb(vo, wet=0.03, length=0.4, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.6 * lvl)[:, None] + sfx * 0.9 * (1 - 0.25 * lvl)[:, None] + amb
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(2.0 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR, 'voice ends', round(K['end'], 2))
