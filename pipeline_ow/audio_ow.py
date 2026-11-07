"""Soundtrack for Organic Fostering "One Weekend".

Gentle bed ("Wholesome" by Kevin MacLeod, incompetech.com, CC BY 4.0, credit in the caption) ducked under the ElevenLabs
voice (IDA, Northern Woman). Evening street air for the walk, then on the words: marker squeaks as the loop draws and
stretches, pops for each 3D object, paper rips and strokes on the cuts, a soft night hush for "rest", a key jingle,
page flips, chain clicks, the end-card shimmer. Long gentle fade so nothing is cut off. Master -14 LUFS.
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
from audio_of import lp, hp, bp, reverb, SR, bird, chime
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, scribble, clack, knock
import reel_ow as R

T, DUR, OFF = R.T, R.DUR, R.OFF
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(7)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ music
TRACK = os.environ.get('TRACK', 'Wholesome.mp3')
OFFSET = float(os.environ.get('TRACK_OFFSET', '0'))
mpath = os.path.join(HERE, '..', 'workspace_sol', 'music', TRACK)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mpath, '-ss', str(OFFSET), '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR),
                      '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)[:N]
if len(tr) < N:
    tr = np.concatenate([tr, np.zeros((N - len(tr), 2))])
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.08
ts_ = np.arange(N) / SR
shape = np.clip(ts_ / 1.2, 0, 1)
night = np.clip((ts_ - T['orgive']) / 1.0, 0, 1) * np.clip((T['And'] + 0.3 - ts_) / 0.6, 0, 1)
swell = 1 + 0.35 * np.clip((ts_ - (T['Ask'] - 0.4)) / 1.2, 0, 1)
music = tr * (1 - 0.5 * night)[:, None] + lp(tr, 1200, 2) * 0.5 * night[:, None]     # softer, darker for "rest"
music = music * (shape * swell)[:, None]

# ------------------------------------------------------------------ ambience: evening street for the walk, quiet room after
noise = rng.normal(0, 1, (N, 2))
street = np.clip((R.T['Respite'] - 0.1 - ts_) / 0.6, 0, 1)
amb += lp(noise, 700, 2) * 0.012 * street[:, None]
for k in range(5):
    add(amb, rng.uniform(0.3, T['Respite'] - 0.6), bird(rng.uniform(0.03, 0.06)), pan=rng.uniform(-0.6, 0.6))
amb += lp(noise, 450, 2) * 0.005 * (1 - street)[:, None]

# ------------------------------------------------------------------ SFX on the cuts
shots = R.shots()
for j, (a, b, f) in enumerate(shots[1:]):
    kind, td = R.TRANS[j]
    t0 = a - td / 2
    if kind is R.tr_tear:
        add(sfx, t0, crinkle(td + 0.15, 0.22), pan=0.2)
        add(sfx, t0, whoosh(td, 600, 7000, 0.08))
    elif kind is R.tr_stroke:
        add(sfx, t0, scribble(td + 0.1, 0.08), pan=-0.2)
        add(sfx, t0, whoosh(td + 0.1, 300, 4500, 0.1))
    elif kind is R.tr_dusk:
        add(sfx, t0, whoosh(0.9, 200, 1600, 0.05, rev=True))
    elif kind is R.tr_flash:
        add(sfx, t0 + td / 2 - 0.05, shimmer(0.8, 0.07, 88))
    elif kind is R.tr_soft:
        add(sfx, a - 0.2, shimmer(1.4, 0.1, 84))
    else:
        add(sfx, t0 - 0.05, whoosh(td + 0.15, 260, 6000, 0.1), pan=(-0.3 if j % 2 else 0.3))

# ------------------------------------------------------------------ SFX on the words
add(sfx, 0.4, scribble(0.5, 0.04), pan=-0.4)                               # "Friday, 5:30pm" handwriting
add(sfx, T['every'], pop(0.22, 760))                                       # calendar token
add(sfx, T['every'] + 0.06, tick(0.1))
add(sfx, T['Respite'], thud(0.12, 120), pan=-0.3)                          # inset card lands
add(sfx, T['planned'], scribble(0.6, 0.09), pan=0.2)                       # loop draws round the weekend
add(sfx, T['planned'] + 0.15, scribble(0.5, 0.05), pan=0.4)                # "planned" handwriting
add(sfx, T['A'], thud(0.12, 110), pan=-0.3)
add(sfx, T['weekend'], pop(0.24, 820))                                     # bag
add(sfx, T['weekend'] + 0.1, ping(0.05, 1568))
add(sfx, T['Part'] + 0.02, scribble(0.5, 0.08), pan=-0.2)                  # loop stretches
add(sfx, T['school'], pop(0.24, 700))                                      # bucket
add(sfx, T['school'] + 0.1, ping(0.05, 1760))
add(sfx, T['Or'] + 0.02, scribble(0.5, 0.08), pan=0.2)                     # loop reshapes
add(sfx, T['agreed'], pop(0.24, 900))                                      # clipboard
add(sfx, T['agreed'] + 0.08, clack(0.1))
add(sfx, T['It'], pop(0.2, 640), pan=-0.3)                                 # first house
add(sfx, T['It'] + 0.35, whoosh(1.2, 300, 2200, 0.04))                     # the link arcs over
add(sfx, T['family'] - 0.25, pop(0.2, 760), pan=0.3)                       # second house
add(sfx, T['family'] - 0.5, scribble(0.4, 0.04), pan=-0.3)
add(sfx, T['orgive'] - 0.1, thud(0.1, 120), pan=0.3)                       # tea card
add(sfx, T['household'] - 0.2, whoosh(1.2, 900, 300, 0.035))               # moon floats down
add(sfx, T['rest'], chime(84, 0.18, 2.2))                                  # soft night chime
add(sfx, T['rest'] + 0.25, chime(91, 0.1, 2.0))
add(sfx, T['same'] - 0.05, pop(0.22, 820))                                 # key
for k in range(4):
    add(sfx, T['same'] + 0.05 + k * 0.06, ping(0.03, 2600 + rng.uniform(-300, 300)), pan=0.4)  # jingle
flip_t0 = T['time1'] - 0.2
for k in range(int((T['Although'] - 0.3 - flip_t0) * 3.0)):                # page flips at 3/s
    add(sfx, flip_t0 + k / 3.0 + 0.05, crinkle(0.16, 0.14), pan=rng.uniform(-0.2, 0.2))
t0c = T['Although'] - 0.3
for i in range(5):                                                          # chain chips drop
    add(sfx, t0c + 0.25 + i * 0.38, pop(0.16, 620 + 70 * i), pan=-0.2 + 0.1 * i)
    add(sfx, t0c + 0.3 + i * 0.38, tick(0.06))
add(sfx, T['consistency'], shimmer(1.0, 0.08, 86))
add(sfx, T['Ask'] - 0.1, pop(0.24, 880))                                   # button
add(sfx, T['Ask'] + 0.6, shimmer(0.9, 0.06, 91))
add(sfx, T['Start'] - 0.1, ping(0.06, 1568))
add(sfx, T['enquiry'] + 0.3, pop(0.12, 980))                               # Ofsted badge
add(sfx, T['enquiry'] + 0.35, chime(96, 0.08, 2.0))
sfx = reverb(sfx, wet=0.12, length=0.8, key='room')

# ------------------------------------------------------------------ voiceover: natural ElevenLabs read, light polish only
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x + 0.06 * bp(x, 2500, 6000, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
add(vo, OFF, x, 1.0)
vo = reverb(vo, wet=0.035, length=0.5, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.35 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.6 * lvl)[:, None] + sfx * 0.95 * (1 - 0.25 * lvl)[:, None] + amb
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
vo_end = OFF + len(x) / SR                                                  # fade starts after the last word has rung out
nf = int(max(1.6, DUR - vo_end) * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR, 'vo_end', round(vo_end, 2))
