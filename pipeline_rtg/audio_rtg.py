"""Soundtrack for Organic Fostering "Room to Grow".

Gentle music bed ("Inspired" by Kevin MacLeod, incompetech.com, CC BY 4.0, credit in the caption) ducked under the
narrator (Microsoft neural voice en-GB-SoniaNeural). Morning birdsong and room tone, then a distant evening hum; on the
words: seedling pop, compass whoosh, a tape rip, the measuring-tape zip, boxes thud out, the bed lands, the lamp clicks,
sparkles, pops for each object, the puzzle snaps, a door creak, a phone ping, the end-card shimmer. Master -14 LUFS.
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
from audio_of import lp, hp, bp, reverb, SR, tt, bird
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, zip_up, crinkle, thud, scribble, squeak, clack, knock
import reel_rtg as R

T, DUR, OFF = R.T, R.DUR, R.OFF
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(11)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ music
TRACK = os.environ.get('TRACK', 'Inspired.mp3')
OFFSET = float(os.environ.get('TRACK_OFFSET', '0'))
mpath = os.path.join(HERE, '..', 'workspace_sol', 'music', TRACK)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mpath, '-ss', str(OFFSET), '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR),
                      '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)[:N]
if len(tr) < N:
    tr = np.concatenate([tr, np.zeros((N - len(tr), 2))])
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.085
ts_ = np.arange(N) / SR
shape = np.clip(ts_ / 1.5, 0, 1)
swell = 1 + 0.3 * np.clip(1 - np.abs(ts_ - (T['belong'] + 0.8)) / 1.6, 0, 1) + 0.35 * np.clip((ts_ - T['Start']) / 1.2, 0, 1)
dusk = np.clip((ts_ - T['At']) / 1.5, 0, 1) * np.clip((T['Start'] - ts_) / 0.8, 0, 1)
music = tr * (1 - 0.45 * dusk)[:, None] + lp(tr, 1400, 2) * 0.45 * dusk[:, None]      # warmer, darker at dusk
music = music * (shape * swell)[:, None]

# ------------------------------------------------------------------ ambience: morning birds + room tone, evening hum
for k in range(16):
    tb = rng.uniform(0.2, T['A_lamp'])
    add(amb, tb, bird(rng.uniform(0.04, 0.09)), pan=rng.uniform(-0.7, 0.7))
noise = rng.normal(0, 1, (N, 2))
room_tone = lp(noise, 500, 2) * 0.006
hum = lp(noise, 180, 2) * 0.02 * dusk[:, None] + np.sin(2 * np.pi * 55 * ts_)[:, None] * 0.0015 * dusk[:, None]
amb += room_tone + hum

# ------------------------------------------------------------------ SFX on the words and cuts
shots = R.shots()
for j, (a, b, f) in enumerate(shots[1:]):
    kind, td = R.TRANS[j]
    if kind is R.tr_tape:
        add(sfx, a - td / 2, crinkle(td + 0.1, 0.12), pan=-0.2)
        add(sfx, a - td / 2, whoosh(td, 500, 6000, 0.1))
    elif kind is R.tr_door:
        add(sfx, a - td / 2, squeak(td + 0.2, 0.06))
        add(sfx, a - td / 2 + 0.05, whoosh(td + 0.2, 200, 2500, 0.08))
    elif kind is R.tr_dusk:
        add(sfx, a - td / 2, whoosh(0.9, 200, 1800, 0.05, rev=True))
    elif kind is R.tr_card:
        add(sfx, a - 0.1, shimmer(1.4, 0.12, 84))
    else:
        add(sfx, a - td / 2 - 0.05, whoosh(td + 0.15, 260, 6000, 0.1), pan=(-0.3 if j % 2 else 0.3))
add(sfx, T['small'], pop(0.22, 820))
add(sfx, T['small'] + 0.05, shimmer(0.7, 0.05, 88))
add(sfx, T['small'] + 0.35, scribble(0.6, 0.06))
add(sfx, T['can'], whoosh(0.8, 300, 2500, 0.05))                         # the dashed path
add(sfx, T['direction'], pop(0.2, 700))
add(sfx, T['direction'] + 0.1, tick(0.08))
add(sfx, T['child'], zip_up(0.1, 500, 1600, 0.75))                        # measuring tape
add(sfx, T['child'] + 0.3, scribble(0.8, 0.06))
add(sfx, T['it'] + 0.1, scribble(0.5, 0.06))
for k in range(4):                                                         # boxes thud out
    add(sfx, T['room'] + 0.05 + k * 0.17, thud(0.22, 85 + k * 10), pan=rng.uniform(-0.4, 0.4))
add(sfx, T['room'], whoosh(0.9, 250, 4500, 0.1, rev=True))
add(sfx, T['room'] + 0.3, scribble(0.6, 0.05))
add(sfx, T['bed'] + 0.2, thud(0.3, 70))                                    # bed lands
add(sfx, T['bed'] + 0.22, knock(0.08))
add(sfx, T['bed'] + 0.3, shimmer(0.9, 0.07, 86))
add(sfx, T['lamp'] + 0.02, key_click(0.28))                                # lamp click
add(sfx, T['lamp'] + 0.05, clack(0.12))
add(sfx, T['lamp'] + 0.1, shimmer(0.7, 0.05, 91))
add(sfx, T['A_place'] + 0.1, zip_up(0.05, 400, 1200, 0.9))                 # heart draws
add(sfx, T['belong'], pop(0.2, 760))
add(sfx, T['belong'] + 0.05, shimmer(1.0, 0.08, 84))
add(sfx, T['leave'] - 0.1, whoosh(0.5, 400, 3000, 0.05))                   # placeholder box
add(sfx, T['them'] - 0.1, scribble(0.6, 0.06))
for k, key in enumerate(('pictures', 'books', 'name')):
    add(sfx, T[key] + 0.1, pop(0.2, 760 + 110 * k))
    add(sfx, T[key] + 0.15, ping(0.04, 1320 + 120 * k))
add(sfx, T['matching'], pop(0.2, 620))
add(sfx, T['matching'] + 0.25, clack(0.18))                                # puzzle snaps
add(sfx, T['whole'] - 0.05, scribble(0.6, 0.05))
for k, key in enumerate(('culture', 'faith', 'language', 'relationships', 'identity')):
    add(sfx, T[key], pop(0.16, 700 + 80 * k), pan=(-0.4 + 0.2 * k))
add(sfx, T['matter'], shimmer(1.1, 0.09, 84))
add(sfx, T['You'] + 0.2, pop(0.12, 600))                                   # phone insert
add(sfx, T['call'], ping(0.1, 1568))
add(sfx, T['call'] + 0.12, ping(0.07, 2093))
add(sfx, T['enquiry'] - 0.05, pop(0.22, 880))
add(sfx, T['enquiry'] + 0.45, shimmer(0.8, 0.06, 91))
add(sfx, T['enquiry'] + 0.6, pop(0.12, 980))
sfx = reverb(sfx, wet=0.12, length=0.8, key='room')

# ------------------------------------------------------------------ voiceover (light polish only: it is a natural voice)
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x + 0.08 * bp(x, 2500, 6000, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
add(vo, OFF, x, 1.0)
vo = reverb(vo, wet=0.04, length=0.5, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.35 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.6 * lvl)[:, None] + sfx * 0.95 * (1 - 0.25 * lvl)[:, None] + amb
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.6 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR)
