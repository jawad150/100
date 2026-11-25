"""Soundtrack for OF "Can I add a page?": dialogue first; a light instrumental pulse low under the first two scenes,
dipped as the brother is mentioned; then pen and paper carry the reply; ends on room tone. Master -14 LUFS later."""
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
from audio_of import lp, hp, reverb, SR, chime
from sfx_palette import pop, whoosh
import reel_page as R

ROOT = R.ROOT
DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))


def load(path, start=0.0, dur=None, gain=1.0):
    a = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path] + (['-t', str(dur)] if dur else [])
    x = np.frombuffer(subprocess.run(a + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout,
                      np.float32).reshape(-1, 2).astype(np.float64)
    return x / max(1e-6, np.abs(x).max()) * gain


def add(t0, x, g=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(sfx, t0, x, g, pan)


def thud(f=85, dur=0.18, vel=0.6):
    t = np.arange(int(SR * dur)) / SR
    x = np.sin(2 * np.pi * f * t * (1 - 0.3 * t / dur)) * np.exp(-t * 28)
    n = np.random.default_rng(1).normal(0, 1, len(t)) * np.exp(-t * 120) * 0.4
    return np.stack([x + lp(n, 2500), x + lp(n, 2500)], 1) * vel


def buzz(dur=0.42):
    t = np.arange(int(SR * dur)) / SR
    x = np.tanh(3 * np.sin(2 * np.pi * 172 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t))
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    x = lp(x * env, 1400) * 0.35
    return np.stack([x, x], 1)


KS = f'{ROOT}/workspace_keep/sfx'
ES = f'{ROOT}/workspace_ear/sfx'
add(0.0, whoosh(0.7, 200, 1800, 0.25))                                   # opens out of the blur
add(R.T_TAP, thud(140, 0.12, 0.35))                                     # fingertip tap
add(R.T_TAP + 0.04, pop(0.12, 1100))                                    # the star
add(R.T_KITCHEN - 0.45, whoosh(0.6, 500, 3500, 0.12), pan=-0.2)         # star flies into its bullet
for tl in (R.T_KITCHEN, R.T_PARK):                                      # photos land: a soft paper tap
    add(tl - 0.02, thud(120, 0.1, 0.3))
    add(tl - 0.03, load(f'{KS}/2385.mp3', 0.25, 0.25), 0.18)
add(R.LIFT0, load(f'{KS}/1104.mp3'), 0.5)                               # the page lifts to camera
add(R.COVER - 0.2, whoosh(0.8, 150, 1500, 0.3))
add(R.DRAIN0, whoosh(1.0, 120, 900, 0.12))                              # colour drains
add(R.T_CITY - 0.35, load(f'{KS}/1530.mp3'), 0.28, 0.3)                 # the scarf slides in
add(R.T_TEXT - 0.05, buzz(), 0.6, 0.35)                                 # one quiet phone buzz
add(R.T_TEXT, pop(0.22, 750), pan=-0.2)                                 # GOAL!
add(R.T_TEXT + 6 / 25, pop(0.2, 950), pan=0.2)                           # I KNOW!
add(R.PEN0 - 0.08, whoosh(0.3, 400, 4000, 0.18))                        # cut on the pen
add(R.PEN0, load(f'{ES}/2376.mp3', 0.0, R.PEN1 - R.PEN0 + 0.1), 0.45)    # pen on paper
add(18.9, load(f'{KS}/1530.mp3'), 0.15, -0.2)                           # the book is drawn closer
add(R.T_THREE, thud(80, 0.2, 0.7))                                      # 3:00 stamp + soft desk tap
add(R.T_THREE + 0.01, pop(0.1, 300))
add(R.PULL0, whoosh(1.0, 150, 1200, 0.18))                              # pull back
add(R.PULL0 + 0.1, load(f'{KS}/2385.mp3', 0.2, 1.0), 0.22)             # paper rustle carries the cut
add(R.LINE0, pop(0.08, 1300))
add(R.END0 - 0.1, whoosh(0.5, 300, 2500, 0.2))                           # ivory circle
add(R.END0 + 0.35, chime(79, 0.035, 2.2))
sfx = reverb(sfx, wet=0.1, length=0.8, key='room')

# light instrumental pulse under the first two scenes, dipped on "brother"
mu = load(f'{ROOT}/workspace_sol/music/Easy_Lemon.mp3', 0.0, 13.0)
mu = np.pad(mu, ((0, max(0, N - len(mu))), (0, 0)))[:N]
tt = np.arange(N) / SR
menv = np.clip(tt / 1.0, 0, 1) * np.clip((R.AT('brother') + 0.5 - tt) / 1.4, 0, 1)
mus = mu * menv[:, None] * 0.12

rt = load(f'{ROOT}/workspace_ai/sfx/3080.mp3', 12, DUR + 0.5)[:N]
rt = np.pad(rt, ((0, N - len(rt)), (0, 0))) / max(1e-6, np.sqrt(np.mean(rt ** 2))) * 0.01

x, sr = sf.read(f'{R.S}/tts/vo.wav')
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 80, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
v[:min(N, len(x))] = x[:N]
vo = reverb(np.stack([v, v], 1), wet=0.06, length=0.5, key='vo')
e = np.abs(vo).max(1)
rel = int(0.25 * SR)
sm = signal.lfilter([1 / rel], [1, -(1 - 1 / rel)], e)
duck = np.clip(sm / (sm.max() + 1e-9) * 4, 0, 1)
mix = (sfx + mus) * (1 - 0.35 * duck)[:, None] + rt + vo * 1.4
mix = np.tanh(mix * 1.05) / 1.05
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote mix', DUR)
