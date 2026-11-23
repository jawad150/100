"""Soundtrack for Organic Fostering "One question is enough".
A swoosh as the magnifying glass reads the headline, slice swishes for the layercut, a swish for the ring sweep, a SOFT
CLICK as each question card lands (brief), a whoosh as the cards spiral into the bubble and a pop when it settles,
typewriter keys for "One question is enough to start.", a chime on the logo. Voice: ElevenLabs (Emilia Bennett).
Music: "Easy Lemon" by Kevin MacLeod (incompetech.com, CC BY 4.0), low and ducked under the voice. Master -14 LUFS.
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
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, thud, clack
import reel_oneq as R

DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
rng = np.random.default_rng(12)
ts_ = np.arange(N) / SR


def add(t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(sfx, t0, x, gain, pan)


def soft_click(v=0.12):
    a, b = clack(v) * 0.7, tick(v * 0.6)
    n = max(len(a), len(b))
    pad = lambda x: np.pad(x, [(0, n - len(x))] + [(0, 0)] * (x.ndim - 1))
    if a.ndim != b.ndim:
        a = a if a.ndim == 2 else np.stack([a, a], 1)
        b = b if b.ndim == 2 else np.stack([b, b], 1)
    return pad(a) + pad(b)


add(0.1, pop(0.1, 700))
add(0.42, pop(0.1, 820))
add(0.25, whoosh(1.2, 300, 2200, 0.05))                                       # the magnifier glides
for i in range(6):
    add(R.LC0 + 0.05 + i * 0.05, whoosh(0.22, 900, 5000, 0.03), pan=(-0.5 if i % 2 else 0.5))
add(R.T_FOST + 0.02, pop(0.12, 600))
add(R.RS0, whoosh(0.9, 400, 3000, 0.06))                                       # ring sweep
for t0 in (R.T_CAN - 0.12, R.T_HOW2 - 0.12, R.T_WHO - 0.12):                  # each card lands: a soft click
    add(t0, soft_click(0.14))
    add(t0 + 0.02, ping(0.012, 2093))
for t0 in (R.Q2, R.Q3):
    add(t0, whoosh(0.4, 500, 3000, 0.035))
add(R.SP0 + 0.2, whoosh(1.0, 200, 2400, 0.08))                                # spiral in
for i in range(3):
    add(R.SP0 + 0.6 + i * 0.12, soft_click(0.08))
add(R.SP1 - 0.05, pop(0.14, 560))
add(R.SP1, thud(0.1, 120))
for k, ch in enumerate('One question is enough to start.'):
    if ch != ' ':
        t0 = R.T_ONE + (R.T_START_E - R.T_ONE) * k / 31
        add(t0, key_click(rng.uniform(0.05, 0.08)), pan=-0.1)
add(R.T_ONE + 0.1, shimmer(1.4, 0.03, 88))
add(R.END0, whoosh(0.5, 300, 3000, 0.06))
add(R.END1, chime(84, 0.06, 2.6))
add(R.T_CTA, pop(0.1, 880))
add(R.T_LINK, tick(0.08))
sfx = reverb(sfx, wet=0.1, length=0.8, key='room')

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Easy_Lemon.mp3'), '-ss', '0',
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.06
music = np.zeros((N, 2))
m = min(len(tr), N)
music[:m] = tr[:m]
music *= (np.clip(ts_ / 0.6, 0, 1) * (1 + 0.3 * np.clip((ts_ - R.END0) / 1.0, 0, 1)))[:, None]

x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
v[:min(N, len(x))] = x[:N]
vo = np.stack([v, v], 1)
vo = reverb(vo, wet=0.03, length=0.5, key='vo_room')
e = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], e)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
mix = music * (1 - 0.55 * lvl)[:, None] + sfx * 0.9 * (1 - 0.25 * lvl)[:, None] + vo * 1.45
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.5 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.02 * SR)] = np.linspace(0, 1, int(0.02 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR)
