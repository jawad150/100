"""Soundtrack for Organic Fostering "Asked the internet? Ask us instead."

Night room tone; the projector hums on with a flicker crackle; a soft click for every typed key and backspace, a deeper
click on Enter; "a thousand answers" is a rising glitchy wash of blips and whooshes that cuts to silence, then one clean
chime for the real result; a soft whoosh and thud as the home rises; a riser and whoosh through the window into a warm
room; end-card chime. Music: "Dreamer" by Kevin MacLeod (incompetech.com, CC BY 4.0, credit in the caption), entering
on the real result. Voice: ElevenLabs (IDA). Master -14 LUFS.
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
from audio_of import lp, hp, bp, reverb, SR, chime, tt
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, thud, clack
import reel_search as R

DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
rng = np.random.default_rng(41)
ts_ = np.arange(N) / SR


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


noise = rng.normal(0, 1, (N, 2))
amb += lp(noise, 350, 2) * 0.006                                           # night room tone
on = np.clip((ts_ - 0.6) / 1.0, 0, 1) * np.clip((R.FLY0 + 0.5 - ts_) / 0.5, 0, 1)
hum = (np.sin(2 * np.pi * 100 * ts_) * 0.004 + np.sin(2 * np.pi * 200 * ts_) * 0.002)
amb += np.stack([hum, hum], 1) * on[:, None]
for k in range(10):                                                        # flicker crackle
    add(sfx, 0.6 + k * 0.1 + rng.uniform(0, 0.04), tick(rng.uniform(0.04, 0.09)), pan=rng.uniform(-0.3, 0.3))
add(sfx, 1.55, ping(0.04, 2093))
for tt_, act, ch in R.SCHED:                                               # typing
    add(sfx, tt_, key_click(rng.uniform(0.07, 0.11) if act == 'add' else 0.08), pan=rng.uniform(-0.2, 0.2))
add(sfx, R.ENTER, clack(0.18))
add(sfx, R.ENTER, thud(0.12, 120))
c0, c1 = R.ENTER + 0.1, R.REAL - 0.05                                      # the flood of answers
u = np.clip((ts_ - c0) / (c1 - c0), 0, 1) * (ts_ < c1) * (ts_ > c0)
amb += bp(noise, 600, 6000, 2) * 0.03 * (u ** 1.5)[:, None]
for k in range(70):
    tk = c0 + (c1 - c0) * (k / 70) ** 0.8
    add(sfx, tk, ping(rng.uniform(0.01, 0.035), rng.uniform(900, 3000)), pan=rng.uniform(-0.8, 0.8))
    if k % 6 == 0:
        add(sfx, tk, whoosh(0.3, 500, 6000, 0.03), pan=rng.uniform(-0.6, 0.6))
i1 = int(c1 * SR)
sfx[i1:i1 + int(0.3 * SR)] *= np.linspace(1, 0, int(0.3 * SR))[:, None]
add(sfx, R.REAL, chime(84, 0.12, 3.0))                                     # one real answer
add(sfx, R.REAL + 0.12, chime(91, 0.07, 2.6))
add(sfx, R.RISE - 0.1, whoosh(0.9, 200, 1500, 0.07))                       # the home rises
add(sfx, R.RISE + 0.75, thud(0.25, 80))
add(sfx, R.RISE + 0.8, shimmer(1.2, 0.06, 88))
add(sfx, R.FLY0, whoosh(R.FLY1 - R.FLY0 + 0.4, 150, 3000, 0.12))           # through the window
rise = np.clip((ts_ - R.FLY0) / (R.FLY1 - R.FLY0), 0, 1) * (ts_ < R.FLY1 + 0.1)
amb += bp(noise, 1500, 8000, 2) * 0.02 * (rise ** 2)[:, None]
warm = np.clip((ts_ - R.FLY1) / 0.5, 0, 1) * np.clip((R.END0 + 0.3 - ts_) / 0.3, 0, 1)
amb += lp(noise, 700, 2) * 0.008 * warm[:, None]                           # a warm room
add(sfx, R.END0 + 0.2, chime(84, 0.07, 2.8))
add(sfx, R.WT(53), pop(0.14, 880))
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Dreamer.mp3'), '-ss', '2',
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.075
music = np.zeros((N, 2))
i0 = int((R.REAL - 0.2) * SR)
m = min(len(tr), N - i0)
music[i0:i0 + m] = tr[:m]
music *= (np.clip((ts_ - R.REAL + 0.2) / 1.5, 0, 1) * (1 + 0.3 * np.clip((ts_ - R.FLY1) / 1.0, 0, 1)))[:, None]

x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
mm = min(len(x), N)
v[:mm] = x[:mm]
vo = np.stack([v, v], 1) + 0.05 * np.stack([bp(v, 2500, 6000, 2)] * 2, 1)
vo = reverb(vo, wet=0.035, length=0.5, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.6 * lvl)[:, None] + sfx * 0.9 * (1 - 0.25 * lvl)[:, None] + amb * (1 - 0.3 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.8 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR)
