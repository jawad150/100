"""Soundtrack for Organic Fostering Reel 02 "You Don't Have to Be the Whole Team" (film cut).

No music in the first half: rain, the alarm bell, the car, pen and calculator, a phone buzz. "A hundred things": the
layers pile up (buzzes, ticks, paper, a heartbeat that speeds up, a rising tone) and stop dead on the smash cut.
23:05: room tone and one slow clock tick. When the door opens the score enters ("Touching Moments Two - Higher" by
Kevin MacLeod, incompetech.com, CC BY 4.0, credit in the caption; not the earlier reels' tune), carries through the
hands and the next morning, and resolves on the end card. Voice: ElevenLabs (IDA). Master -14 LUFS.
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
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, clack, boom
import reel_team as R

SH, DUR, WT = R.SH, R.DUR, R.WT
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
rng = np.random.default_rng(31)
ts_ = np.arange(N) / SR
CUT = SH['silence'][0]
TURN = SH['door'][0] - 0.5


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def win(a, b, ramp=0.2):
    return np.clip((ts_ - a) / ramp + 0.5, 0, 1) * np.clip((b - ts_) / ramp + 0.5, 0, 1)


noise = rng.normal(0, 1, (N, 2))

# ------------------------------------------------------------------ the day (no music)
rain = lp(noise, 3500, 2) * 0.035 + bp(noise, 3000, 9000, 2) * 0.01
amb += rain * win(0, SH['alarm'][1] + 0.3, 0.5)[:, None]
for k in range(60):                                                         # drops on the glass
    add(amb, rng.uniform(0, SH['alarm'][1]), tick(rng.uniform(0.02, 0.06)), pan=rng.uniform(-0.7, 0.7))
bell = np.zeros(int(1.4 * SR))                                             # the alarm bell
tb = np.arange(len(bell)) / SR
for f in (2600, 3150):
    bell += np.sin(2 * np.pi * f * tb) * (np.sin(2 * np.pi * 18 * tb) > 0)
bell *= 0.05 * np.minimum(1, tb / 0.01) * np.clip((1.4 - tb) / 0.05, 0, 1)
add(sfx, SH['alarm'][0] + 0.1, bell, pan=0.3)
add(sfx, SH['alarm'][0] + 1.5, key_click(0.2), pan=0.3)                    # switched off
eng = (lp(noise, 160, 2) * 0.05 + np.sin(2 * np.pi * 48 * ts_)[:, None] * 0.006)
amb += eng * win(*SH['drive'], 0.1)[:, None]
for k, ti in enumerate(np.arange(SH['drive'][0] + 0.5, SH['drive'][1], 0.45)):  # indicator
    add(sfx, ti, key_click(0.05 if k % 2 == 0 else 0.035), pan=-0.4)
amb += lp(noise, 450, 2) * 0.006 * win(SH['home'][0], SH['phone'][1])[:, None]
for k in range(10):                                                        # pen + calculator
    add(sfx, SH['home'][0] + 0.2 + k * 0.2, tick(0.05 + 0.03 * (k % 3)), pan=0.2)
buzz = np.sin(2 * np.pi * 180 * tt(0.35)) * (np.sin(2 * np.pi * 30 * tt(0.35)) > 0) * 0.05
for k in range(3):
    add(sfx, SH['phone'][0] + 0.15 + k * 0.5, buzz, pan=0.2)

# ------------------------------------------------------------------ "a hundred things": the pile-up, then dead stop
h0, h1 = SH['hundred']
u = np.clip((ts_ - h0) / (h1 - h0), 0, 1) * (ts_ < CUT)
riser = np.sin(2 * np.pi * np.cumsum(80 + 300 * u ** 2) / SR) * 0.03 * u ** 1.5
amb += np.stack([riser, riser], 1) * (ts_ < CUT)[:, None]
amb += bp(noise, 400, 3000, 2) * 0.03 * (u ** 2)[:, None]
t = h0
k = 0
while t < CUT - 0.05:                                                      # heartbeat, faster and faster
    gap = 0.85 - 0.5 * ((t - h0) / (h1 - h0))
    add(sfx, t, thud(0.35, 55))
    add(sfx, t + 0.16, thud(0.25, 50))
    t += max(0.32, gap)
for k in range(40):                                                        # the hundred things
    tk = h0 + 0.4 + (CUT - h0 - 0.5) * (k / 40) ** 0.7
    if tk >= CUT - 0.05:
        continue
    choice = k % 4
    if choice == 0:
        add(sfx, tk, buzz * 0.8, pan=rng.uniform(-0.8, 0.8))
    elif choice == 1:
        add(sfx, tk, crinkle(0.2, 0.12), pan=rng.uniform(-0.8, 0.8))
    elif choice == 2:
        add(sfx, tk, ping(0.03, rng.uniform(1200, 2400)), pan=rng.uniform(-0.8, 0.8))
    else:
        add(sfx, tk, tick(0.08), pan=rng.uniform(-0.8, 0.8))
sfx[int(CUT * SR):int((CUT + 0.02) * SR)] *= np.linspace(1, 0, int(0.02 * SR))[:, None]
sfx[int((CUT + 0.02) * SR):int(TURN * SR)] = 0                              # SMASH CUT: total silence
amb[int((CUT + 0.02) * SR):int((CUT + 0.6) * SR)] = 0

# ------------------------------------------------------------------ 23:05: the quiet room
room = lp(noise, 300, 2) * 0.004 * win(CUT + 0.6, SH['door'][0] + 0.3, 0.4)[:, None]
amb += room
for k, tk in enumerate(np.arange(CUT + 0.9, SH['door'][0] - 0.2, 1.0)):
    add(sfx, tk, tick(0.04), pan=0.5)

# ------------------------------------------------------------------ the turn: door, light, score
add(sfx, SH['door'][0] - 0.3, whoosh(1.2, 150, 1600, 0.06))
add(sfx, SH['door'][0] - 0.1, shimmer(1.6, 0.07, 84))
add(sfx, SH['door'][0] + 0.2, thud(0.12, 90))                              # latch
creak = bp(rng.normal(0, 1, int(0.7 * SR)), 300, 900, 2) * np.hanning(int(0.7 * SR)) * 0.04
add(sfx, SH['door'][0] + 0.3, creak, pan=-0.3)
amb += lp(noise, 2500, 2) * 0.004 * win(SH['door'][0], SH['next'][1])[:, None]   # outdoor air / warm room
for k, w in enumerate((36, 37, 39)):
    add(sfx, R.WT(w), pop(0.1, 700 + 90 * k), pan=-0.3 + 0.3 * k)
add(sfx, SH['next'][0] - 0.2, shimmer(1.4, 0.07, 88))                      # into the next morning
bell2 = bell[:int(0.5 * SR)] * np.linspace(1, 0, int(0.5 * SR)) * 0.5
add(sfx, SH['next'][0] + 0.3, bell2, pan=0.3)                              # the alarm again, but soft
add(sfx, SH['next'][0] + 0.75, key_click(0.15), pan=0.3)
add(sfx, SH['end'][0] + 0.3, chime(84, 0.06, 2.8))
add(sfx, R.WT(54), pop(0.12, 880))
sfx = reverb(sfx, wet=0.14, length=1.0, key='room')

raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Touching_Moments_Two_-_Higher.mp3'),
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.1
music = np.zeros((N, 2))
i0 = int(TURN * SR)
n = min(len(tr), N - i0)
music[i0:i0 + n] = tr[:n]
music *= (np.clip((ts_ - TURN) / 2.0, 0, 1) * (1 + 0.25 * np.clip((ts_ - SH['clasp'][0]) / 2.0, 0, 1)))[:, None]

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
vo = reverb(vo, wet=0.04, length=0.6, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.55 * lvl)[:, None] + sfx * 0.9 * (1 - 0.25 * lvl)[:, None] + amb * (1 - 0.3 * lvl)[:, None]
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
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR)
