"""Soundtrack for BMHC "What did you keep?": no music (BMHC guidelines) - quiet window-side room tone and the small
sounds the brief asks for: paper unfolding, a page, the drawer opening and closing; voices (owner + interviewer).
Master -14 LUFS."""
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
from sfx_palette import pop, whoosh, tick
import reel_keep as R
DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
SF = f'{R.S}/sfx'


def load(name, start=0.0, dur=None, gain=1.0):
    a = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', f'{SF}/{name}.mp3'] + (['-t', str(dur)] if dur else [])
    x = np.frombuffer(subprocess.run(a + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout,
                      np.float32).reshape(-1, 2).astype(np.float64)
    return x / max(1e-6, np.abs(x).max()) * gain


def add(t0, x, g=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(sfx, t0, x, g, pan)


add(0.05, load('2385', 0.2, 1.2), 0.35)                       # paper unfolding
add(R.C2 - 0.3, whoosh(0.8, 250, 2200, 0.05))                   # iris opens out of the thumb
add(R.C3 - 0.3, whoosh(0.75, 400, 3000, 0.04), pan=0.3)          # clock wipe
add(R.C3 - 0.05, load('1530'), 0.25, 0.3)
add(R.T_NANI, load('2379', 0.5, 0.9), 0.35)                     # the envelope
add(R.T_CARD, pop(0.06, 700))
add(R.T_SPOONS, tick(0.08))
add(R.C4 - 0.3, whoosh(0.7, 150, 3500, 0.06))                   # zoom-through
add(R.C4 + 0.2, whoosh(1.2, 300, 2000, 0.03))                   # spiral
for i in range(6):
    add(R.C5 + i * 0.05, whoosh(0.2, 900, 4500, 0.02), pan=(-0.4 if i % 2 else 0.4))
add(R.LIFT0, load('1104'), 0.45)                                 # the thumb lifts off the card
add(R.C6 - 0.25, whoosh(0.5, 600, 6000, 0.07), pan=-0.3)        # whip pan
add(R.C7 - 0.3, whoosh(0.7, 200, 1800, 0.04))                   # page slides up
add(R.C7 + 0.1, load('1530'), 0.25)
add(R.C7 + 0.05, load('1906', 0, 1.2), 0.4)                     # drawer opens
add(R.C7 + 1.4, load('1907', 0, 1.0), 0.45)                     # and closes
add(R.C8 - 0.8, whoosh(1.0, 200, 2500, 0.06))                   # arrow wipe
add(R.C8 + 0.1, chime(84, 0.04, 2.0))
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')
rt = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '12', '-i', os.path.join(R.ROOT, 'workspace_ai', 'sfx', '3080.mp3'), '-t', str(DUR + 0.5),
                     '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
rt = np.frombuffer(rt, np.float32).reshape(-1, 2).astype(np.float64)[:N]
rt = np.pad(rt, ((0, N - len(rt)), (0, 0))) / max(1e-6, np.sqrt(np.mean(rt ** 2))) * 0.008
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
v[:min(N, len(x))] = x[:N]
vo = reverb(np.stack([v, v], 1), wet=0.05, length=0.6, key='vo')
e = np.abs(vo).max(1)
rel = int(0.25 * SR)
sm = signal.lfilter([1 / rel], [1, -(1 - 1 / rel)], e)
lvl = np.clip(sm / (sm.max() + 1e-9) * 4, 0, 1)
mix = sfx * (1 - 0.3 * lvl)[:, None] + rt + vo * 1.4
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.2 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix2_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote mix', DUR)
