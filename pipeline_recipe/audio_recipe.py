"""Soundtrack for Organic Fostering Reel 01 "The Recipe That Wasn't on the Menu".

As the PDF asks: natural kitchen foley first (a projector purr and soft sizzle under the retro memory, knife on board),
then a soft licensed instrumental comes in at the reveal ("Wholesome" by Kevin MacLeod, incompetech.com, CC BY 4.0,
credit in the caption). Each look has its sound: film flutter (retro), low swell + shimmer (eclipse), paper slides
(layercut), pen squeak (explainer), whoosh (spiral), airy shimmer (aurora); pops for the 3D objects, clacks for the
cookie cutter. Voice: ElevenLabs (IDA). Gentle fade. Master -14 LUFS.
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
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, clack, scribble
import reel_recipe as R

SH, DUR, WT = R.SH, R.DUR, R.WT
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
rng = np.random.default_rng(21)
ts_ = np.arange(N) / SR


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def win(a, b, ramp=0.2):
    return np.clip((ts_ - a) / ramp + 0.5, 0, 1) * np.clip((b - ts_) / ramp + 0.5, 0, 1)


noise = rng.normal(0, 1, (N, 2))

# ------------------------------------------------------------------ music: enters at the reveal (the eclipse)
REVEAL = SH['writing'][0] - 0.3
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Wholesome.mp3'), '-ss', '4',
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.07
music = np.zeros((N, 2))
i0 = int(REVEAL * SR)
n = min(len(tr), N - i0)
music[i0:i0 + n] = tr[:n]
music *= (np.clip((ts_ - REVEAL) / 1.5, 0, 1) * (1 + 0.3 * np.clip((ts_ - SH['end'][0]) / 1.0, 0, 1)))[:, None]

# ------------------------------------------------------------------ foley / ambience
retro_w = win(0, SH['hands'][1])
purr = (np.sin(2 * np.pi * 24 * ts_) > 0.7).astype(float) * 0.012
amb += (lp(noise, 1400, 2) * 0.01 + purr[:, None]) * retro_w[:, None]           # projector purr
amb += bp(noise, 2500, 9000, 2) * 0.012 * win(0, SH['pan'][1])[:, None]         # sizzle under the pan
for k, tk in enumerate(np.arange(SH['hands'][0] + 0.1, SH['hands'][1], 0.33)):   # knife on board
    add(sfx, tk, thud(0.08, 180), pan=0.2)
    add(sfx, tk + 0.01, tick(0.06))
amb += lp(noise, 500, 2) * 0.005 * win(SH['writing'][0], SH['writing'][1])[:, None]
add(sfx, WT(9), scribble(0.8, 0.06), pan=-0.2)                                   # "But tonight…" pen
amb += bp(noise, 2500, 9000, 2) * 0.01 * win(SH['explain'][0], SH['stir'][1])[:, None]   # cooking sizzle
amb += lp(noise, 400, 2) * 0.004 * win(SH['table'][0], SH['table'][1])[:, None]

# ------------------------------------------------------------------ the six transitions
for nm in R.ORDER[1:]:
    kind, td = R.TRANS[nm]
    t0 = SH[nm][0] - td / 2
    if kind is R.tr_retro:
        for k in range(8):
            add(sfx, t0 + k * 0.05, tick(0.07))
        add(sfx, t0 + 0.2, whoosh(0.4, 300, 2500, 0.05))
    elif kind in (R.tr_eclipse, R.tr_eclipse_plum):
        add(sfx, t0, whoosh(td + 0.3, 120, 900, 0.07, rev=True))
        add(sfx, t0 + td * 0.5, shimmer(1.4, 0.09, 84))
        add(sfx, t0 + td * 0.5, chime(79, 0.06, 2.5))
    elif kind is R.tr_layercut:
        for k in range(6):
            add(sfx, t0 + k * 0.08, crinkle(0.18, 0.1), pan=(-0.5 if k % 2 else 0.5))
    elif kind is R.tr_explainer:
        add(sfx, t0, scribble(td, 0.08))
        add(sfx, t0 + td * 0.6, pop(0.12, 900))
    elif kind is R.tr_spiral:
        add(sfx, t0, whoosh(td + 0.2, 200, 4000, 0.1, rev=(nm == 'cutter')))
    elif kind is R.tr_aurora:
        add(sfx, t0, shimmer(td + 0.8, 0.08, 86))
        add(sfx, t0, whoosh(td + 0.3, 300, 2000, 0.05))

# ------------------------------------------------------------------ objects and cues
for i in (4, 13, 16, 19, 28, 38, 47, 48, 50):
    add(sfx, WT(i), pop(0.18, 700 + 30 * (i % 7)), pan=rng.uniform(-0.3, 0.3))
add(sfx, WT(13) + 0.05, crinkle(0.2, 0.08))                                      # recipe card
add(sfx, WT(16) + 0.2, ping(0.04, 1760))                                         # tag
add(sfx, WT(18), scribble(0.6, 0.06), pan=0.3)                                   # explainer ring + arrow
for k in range(3):
    add(sfx, WT(21) + k * 0.3, pop(0.1, 880 + 80 * k), pan=-0.3 + 0.3 * k)       # 1 spice 2 stir 3 taste
add(sfx, WT(20), scribble(0.9, 0.05), pan=-0.2)
for k, i in enumerate((31, 33, 35)):                                             # cookie cutter stamps
    add(sfx, WT(i) + 0.05, clack(0.2))
    add(sfx, WT(i) + 0.06, thud(0.15, 140))
add(sfx, WT(36) + 0.2, scribble(0.5, 0.05))
add(sfx, WT(36) + 0.2, whoosh(0.5, 400, 2500, 0.05))                             # cutter lifts away
add(sfx, WT(42) - 0.1, scribble(1.0, 0.05))                                      # "Who they are matters."
add(sfx, WT(52), chime(84, 0.08, 2.4))
add(sfx, WT(55), chime(91, 0.06, 2.4))
add(sfx, WT(58), pop(0.2, 900))
add(sfx, WT(58) + 0.7, shimmer(0.9, 0.06, 91))
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
vo = reverb(vo, wet=0.035, length=0.45, key='vo_room')

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
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR)
