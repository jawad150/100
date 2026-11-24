"""Soundtrack for BMHC "Name this place by ear": sound-led, no music (BMHC guidelines; the brief is about sound).
Real effects (Mixkit): ball bounces, a trainer squeak, a page turn, a pencil, a switch click; a quiet room tone under
everything with silence around each sound. The reveal replays the same three sounds over the wide shots.
Voices: ElevenLabs - narrator (Drew C) + Heritage Radio presenter (Payyal Modi). Master -14 LUFS.
"""
import os, sys, json, subprocess
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
import reel_ear as R

DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
SFX = f'{R.S}/sfx'
ts_ = np.arange(N) / SR


def load(name, start=0.0, dur=None, gain=1.0):
    a = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', f'{SFX}/{name}.mp3']
    if dur:
        a += ['-t', str(dur)]
    x = np.frombuffer(subprocess.run(a + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout,
                      np.float32).reshape(-1, 2).astype(np.float64)
    return x / max(1e-6, np.abs(x).max()) * gain


def add(t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(sfx, t0, x, gain, pan)


BOUNCE = load('2085', 0, None, 0.9)
RUSTLE = load('1101', 0.0, 0.9, 0.7)
PAGE = load('1104', 0, None, 0.8)
PENCIL = load('2376', 0, None, 0.6)
CLICK = load('2582', 0, 0.5, 0.8)
SQUEAK = load('1013', 0, 0.8, 0.45)

# hook: three sounds cut into the silence
add(R.SND['h_bounce'], BOUNCE, 0.9)
add(R.SND['h_rustle'], RUSTLE, 0.8)
add(R.SND['h_click'], CLICK, 0.9)
for t0, f in ((0.3, 760), (1.0, 860), (1.45, 960)):
    add(t0, pop(0.05, f))
add(1.95, whoosh(0.3, 800, 5000, 0.03))
# first clue
for b, g in (('b1', 1.0), ('b2', 0.85), ('b3', 0.7)):
    add(R.SND[b] - 0.01, BOUNCE, g, pan=0.2 - 0.15 * ('b1', 'b2', 'b3').index(b))
add(R.SND['squeak'], SQUEAK, 0.55, pan=-0.2)
# second clue
add(R.SND['page'] - 0.08, PAGE, 0.9)
add(R.SND['page'] + 0.05, RUSTLE * 0.5, 0.6)
add(R.SND['pencil'], PENCIL, 0.75)
# last one
add(R.SND['fader'], CLICK, 1.0)
add(R.SND['phones'] + 0.3, whoosh(0.3, 300, 1500, 0.03))
# got a guess: a beat of near-silence, then the three sounds again over the wide shots
add(R.C5, pop(0.06, 700))
add(R.SND['r_bounce'], BOUNCE, 0.9)
add(R.SND['r_rustle'] - 0.05, PAGE, 0.85)
add(R.SND['r_click'], CLICK, 0.9)
# reveal + end
add(R.C7, whoosh(0.6, 200, 2000, 0.05))
add(R.C8 + 0.05, chime(84, 0.05, 2.4))
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')

# room tone (quiet; the brief wants room around each sound)
rt = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '5', '-i', os.path.join(R.ROOT, 'workspace_ai', 'sfx', '3080.mp3'), '-t', str(DUR + 0.5),
                     '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
rt = np.frombuffer(rt, np.float32).reshape(-1, 2).astype(np.float64)[:N]
rt = np.pad(rt, ((0, N - len(rt)), (0, 0))) / max(1e-6, np.sqrt(np.mean(rt ** 2))) * 0.01

# voices
vo = np.zeros(N)
for name in ('vo_nar', 'vo_pres'):
    p = f'{R.S}/tts/{name}.wav'
    if os.path.exists(p):
        x, sr = sf.read(p)
        if x.ndim > 1:
            x = x.mean(1)
        if sr != SR:
            x = signal.resample_poly(x, SR, sr)
        if name == 'vo_pres':                                     # on air: a touch of broadcast EQ
            x = bp(x, 120, 9000, 2) * 1.0 + 0.15 * bp(x, 2500, 6000, 2)
        x = hp(x, 70, 2)
        m = min(len(x), N)
        vo[:m] += x[:m]
    else:
        print('NOTE: missing', name)
if np.abs(vo).max() > 0:
    vo = vo / np.abs(vo).max() * 0.9
vo2 = reverb(np.stack([vo, vo], 1), wet=0.03, length=0.4, key='vo')
e = np.abs(vo2).max(1)
rel = int(0.25 * SR)
sm = signal.lfilter([1 / rel], [1, -(1 - 1 / rel)], e)
lvl = np.clip(sm / (sm.max() + 1e-9) * 4, 0, 1)
mix = sfx * (1 - 0.3 * lvl)[:, None] + rt * (1 - 0.5 * lvl)[:, None] + vo2 * 1.4
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.2 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote mix', DUR)
