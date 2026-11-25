"""Soundtrack for the reference-style OF reel: narration on top, a gentle music bed ("Lasting Hope", Kevin MacLeod,
CC BY 4.0) under it, soft whooshes on every blur dissolve, pops for bullets/pin/messages, a swell into the glow, a hit
on the plum flash and a chime on the logo. Master -14 LUFS at encode."""
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
from audio_of import lp, hp, reverb, SR, chime
from sfx_palette import pop, whoosh
import reel_ref as R

DUR = R.DUR
N = int(SR * DUR)
AO.DUR, AO.N = DUR, N
sfx = np.zeros((N, 2))


def load(path, start=0.0, dur=None):
    a = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path] + (['-t', str(dur)] if dur else [])
    x = np.frombuffer(subprocess.run(a + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout,
                      np.float32).reshape(-1, 2).astype(np.float64)
    return x / max(1e-6, np.abs(x).max())


def add(t0, x, g=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        AO.add(sfx, t0, x, g, pan)


def thud(f=70, dur=0.25, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    x = np.sin(2 * np.pi * f * t * (1 - 0.3 * t / dur)) * np.exp(-t * 18)
    return np.stack([x, x], 1) * vel


for i, c in enumerate(R.CUTS[1:]):                                       # every blur dissolve
    add(c - 0.25, whoosh(0.5, 250, 2600, 0.12), pan=(-0.25 if i % 2 else 0.25))
add(0.05, whoosh(0.8, 150, 1800, 0.18))
for wd, ln, k in (('spare', 4, 0), ('paperwork', 4, 0), ('training', 4, 0)):
    add(R.AT(wd, ln, k) - 0.1, pop(0.16, 900))                            # star bullets
add(R.CUTS[6] + 0.05, pop(0.25, 600))                                     # pin lands
add(R.CUTS[6] + 0.1, thud(140, 0.1, 0.25))
add(R.AT('text', 8) + 0.05, pop(0.22, 820), pan=-0.2)                     # GOAL
add(R.AT('text', 8) + 0.29, pop(0.2, 1000), pan=0.2)                      # I KNOW
add(R.CUTS[8] + 0.05, whoosh(0.7, 150, 1200, 0.15), pan=0.4)              # the fridge slides in
add(R.CUTS[10] - 0.1, whoosh(0.7, 90, 900, 0.3))                          # the big out-of-focus pass
add(R.CUTS[10] + 1.1, thud(60, 0.3, 0.35))
add(14.6, whoosh(0.8, 200, 4000, 0.16, rev=True))                         # swell into the glow
add(R.END - 0.05, thud(55, 0.4, 0.6))                                     # plum flash
add(R.END + 0.3, chime(76, 0.05, 2.4))
add(R.END + 0.55, chime(83, 0.035, 2.2))
sfx = reverb(sfx, wet=0.15, length=1.2, key='room')

mu = load(f'{R.ROOT}/workspace_sol/music/Lasting_Hope.mp3', 0.0, DUR + 1)[:N]
mu = np.pad(mu, ((0, N - len(mu)), (0, 0)))
tt = np.arange(N) / SR
menv = np.clip(tt / 0.8, 0, 1) * np.clip((DUR - tt) / 2.5, 0, 1)
mus = mu * menv[:, None] * 0.22

x, sr = sf.read(f'{R.S}/tts2/vo.wav')
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 80, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
v[:min(N, len(x))] = x[:N]
vo = reverb(np.stack([v, v], 1), wet=0.05, length=0.5, key='vo')
e = np.abs(vo).max(1)
rel = int(0.3 * SR)
sm = signal.lfilter([1 / rel], [1, -(1 - 1 / rel)], e)
duck = np.clip(sm / (sm.max() + 1e-9) * 4, 0, 1)
mix = (mus * (1 - 0.45 * duck)[:, None]) + sfx * (1 - 0.25 * duck)[:, None] + vo * 1.35
mix = np.tanh(mix * 1.05) / 1.05
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_ref.wav', SR, (mix * 32767).astype(np.int16))
print('wrote mix', DUR)
