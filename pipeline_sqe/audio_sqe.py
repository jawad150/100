"""Soundtrack for IC London "What Is the SQE?" (story version).

Music: "Upbeat Forever" by Kevin MacLeod (incompetech.com), CC BY 4.0 — muffled under the opening street scene, opening
up as London goes to work, dipping under the qualification beat and swelling for the CTA. Modern UI-style sound design
on every cut and pop (swishes, blips, glitch, bells, impacts, confetti crackle). Expressive male voiceover on top,
ducked bed, gentle fade-out.
"""
import os, sys, subprocess
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, reverb, riser, SR, tt
from sfx_palette import (pop, whoosh, boom, thud, shimmer, tick, key_click, clack, ping, zip_up, scribble, squeak, crinkle,
                         clang, knock, bonk)
import reel_sqe as R

P, VO, DUR = R.P, R.VO, R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(5)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def glitch(dur=0.3, vel=0.25):
    t = tt(dur)
    x = np.sign(np.sin(2 * np.pi * rng.uniform(200, 900) * t)) * (rng.random(len(t)) > 0.5)
    x = np.repeat(x[::40], 40)[:len(t)]
    return bp(x, 400, 6000) * np.minimum(1, (dur - t) / 0.05) * vel


# ------------------------------------------------------------------ music
TRACK = os.environ.get('TRACK', 'Upbeat_Forever.mp3')
OFFSET = float(os.environ.get('TRACK_OFFSET', '30'))
mpath = f'{R.S}/../workspace_sol/music/{TRACK}'
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mpath, '-ss', str(OFFSET), '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR),
                      '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)[:N]
if len(tr) < N:
    tr = np.concatenate([tr, np.zeros((N - len(tr), 2))])
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.12
ts_ = np.arange(N) / SR
open_k = np.clip((ts_ - (P('l2', 0) - 0.8)) / 0.8, 0, 1)[:, None]          # opens up as London goes to work
music = lp(tr, 900, 2) * 1.4 * (1 - open_k) + tr * open_k
add(music, P('l2', 0) - 0.8, riser(0.8, 0.18))
add(music, P('l2', 0), boom(0.35))
add(music, P('l5', 0), boom(0.25))
add(music, P('l7', 3) + 0.35, boom(0.4))
music = reverb(music, wet=0.06, length=1.0, key='trk')

# ------------------------------------------------------------------ SFX
add(sfx, 0.25, whoosh(0.35, 800, 6000, 0.12))                        # LONDON 08:00 tag
for k in range(6):
    add(sfx, 0.4 + k * 0.05, key_click(0.08), pan=-0.3)
for j, (a, b, f) in enumerate(R.shots()[1:]):                      # every cut gets a swish
    add(sfx, a - 0.18, whoosh(0.32, 300 + 80 * (j % 4), 6000, 0.17), pan=(-0.3 if j % 2 else 0.3))
for line, i, dt, f in [('l2', 0, 0.05, 700), ('l2', 0, 0.2, 900), ('l2', 1, 0.02, 760), ('l2', 1, 0.15, 960),
                       ('l2', 2, 0.02, 820), ('l2', 2, 0.25, 1000)]:
    add(sfx, P(line, i) + dt, pop(0.26, f))                         # LAW / HR / FINANCE badges and props
add(sfx, P('l3', 0) + 0.15, pop(0.3, 520))                          # question mark
add(sfx, P('l3', 0) + 0.55, pop(0.2, 760))
add(sfx, P('l4', 0) - 0.16, glitch(0.32, 0.22))                    # glitch transition into the confusion
for j in range(6):                                                  # jargon chips swarm in
    add(sfx, P('l4', 0) + 0.08 + j * 0.12, pop(0.16, 500 + 90 * j), pan=-0.5 + 0.2 * j)
add(sfx, P('l4', 1) + 0.1, zip_up(0.14, 300, 1500, 0.6))            # ...and line up neatly
add(sfx, P('l4', 1) + 0.6, shimmer(0.8, 0.18, 88))                  # check
add(sfx, P('l5', 0), pop(0.28, 820))                               # SQE1
add(sfx, P('l5', 1) - 0.05, pop(0.2, 600))                          # bulb pops...
add(sfx, P('l5', 1) + 0.55, key_click(0.25))                        # ...and switches on
add(sfx, P('l5', 1) + 0.57, ping(0.12, 1760))
add(sfx, P('l5', 1) + 0.25, pop(0.18, 900))                         # LEGAL KNOWLEDGE
add(sfx, P('l5', 2) + 0.05, whoosh(0.3, 900, 5000, 0.12))           # exam papers
add(sfx, P('l5', 2) + 0.1, pop(0.24, 700))
for j in range(5):
    add(sfx, P('l5', 2) + 0.5 + j * 0.07, tick(0.18))               # A-E
add(sfx, P('l5', 2) + 1.0, pop(0.22, 1100))                         # answer C
add(sfx, P('l6', 0), pop(0.28, 820))                               # SQE2
for j in range(4):                                                  # skill panels
    tj = P('l6', 2 + j) - 0.05
    add(sfx, tj, thud(0.25, 120), pan=(-0.3 if j % 2 == 0 else 0.3))
    add(sfx, tj + 0.25, pop(0.2, 760 + 120 * j))
add(sfx, P('l7', 0) + 0.1, pop(0.26, 640))                         # cap
add(sfx, P('l7', 0) + 0.4, pop(0.18, 900))
add(sfx, P('l7', 1) + 0.05, crinkle(0.25, 0.2))                     # calendar flips
add(sfx, P('l7', 1) + 0.1, pop(0.24, 700))
add(sfx, P('l7', 1) + 0.35, pop(0.18, 880))
add(sfx, P('l7', 2) + 0.15, pop(0.26, 600))                         # shield
add(sfx, P('l7', 2) + 0.2, ping(0.1, 1320))
add(sfx, P('l7', 2) + 0.45, pop(0.18, 900))
add(sfx, P('l7', 3) + 0.35, shimmer(1.2, 0.22, 86))                 # QUALIFIED + confetti
add(sfx, P('l7', 3) + 0.4, crinkle(0.6, 0.18))
add(sfx, P('l8', 0) + 0.1, whoosh(0.6, 200, 3000, 0.14))            # end card rises
add(sfx, P('l8', 0) + 0.6, shimmer(1.2, 0.18, 84))                  # logo
for j in range(3):
    add(sfx, P('l8', 0) + 0.9 + j * 0.12, pop(0.16, 700 + 140 * j))
add(sfx, P('l8', 1), pop(0.22, 820))                               # url + arrow
sfx = reverb(sfx, wet=0.1, length=0.8, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{R.S}/tts/lines'


def vo_chain(x, sr):
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 75, 2)
    x = x + 0.2 * bp(x, 2500, 6500, 2)
    x = x + 0.07 * bp(x, 110, 260, 2)
    x = lp(x, 12500, 2)
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))
    thr = 0.22 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 2.6) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name in R.ORDER:
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, VO[name], vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.05, length=0.6, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.35 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.68 * lvl)[:, None] + sfx * 0.95 * (1 - 0.3 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(R.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav')
