"""Soundtrack for Organic Fostering "Can I Foster If…?" v2.

Light, warm music bed ("Wholesome" by Kevin MacLeod, incompetech.com, CC BY 4.0 — credit in the post caption) ducked under
the narrator; UI sound design on every beat: bookmark tap, pen scribble, key ticks while the bar types, swishes on each
camera move and scroll, a pop per answer pill, notification chimes, a paper-plane whoosh. Master -14 LUFS.
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
from audio_of import lp, hp, bp, reverb, SR, tt
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, zip_up, crinkle, thud, scribble
import reel_cf as R

P, PD, WT, END, VO, DUR = R.P, R.PD, R.WT, R.END, R.VO, R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(7)


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def ding(f=1568, vel=0.12):
    return ping(vel, f) + 0.6 * np.pad(ping(vel * 0.7, f * 1.5), (int(0.09 * SR), 0))[:len(ping(vel, f))]


# ------------------------------------------------------------------ music
TRACK = os.environ.get('TRACK', 'Wholesome.mp3')
OFFSET = float(os.environ.get('TRACK_OFFSET', '4'))
mpath = os.path.join(HERE, '..', 'workspace_sol', 'music', TRACK)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mpath, '-ss', str(OFFSET), '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR),
                      '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)[:N]
if len(tr) < N:
    tr = np.concatenate([tr, np.zeros((N - len(tr), 2))])
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.1
ts_ = np.arange(N) / SR
shape = np.clip(ts_ / 1.2, 0, 1)                                      # soft start
dark = np.clip(1 - np.abs(ts_ - (P('l1', 1) + 0.8)) / 1.2, 0, 1)     # a little muffled on the dark "wondered" beat
music = tr * (1 - 0.6 * dark)[:, None] + lp(tr, 900, 2) * 0.6 * dark[:, None]
swell = 1 + 0.35 * np.clip(1 - np.abs(ts_ - (P('l8', 1) + 1.5)) / 2.0, 0, 1)   # swells on the warm photo
music = music * (shape * swell)[:, None]

# ------------------------------------------------------------------ SFX
shots = R.shots()
for j, (a, b, f) in enumerate(shots[1:]):
    kind, td = R.TRANS[j] if j < len(R.TRANS) else (R.tr_blurfade, 0.4)
    if kind is R.tr_scroll:
        add(sfx, a - td / 2, whoosh(0.32, 500, 4500, 0.08), pan=0.1)
    elif kind is R.tr_blurfade:
        add(sfx, a - td / 2, whoosh(0.5, 300, 2500, 0.06, rev=True))
    else:
        add(sfx, a - td / 2 - 0.05, whoosh(0.36, 280, 6000, 0.12), pan=(-0.3 if j % 2 else 0.3))
tb = WT('l1', 0, 0.75)
add(sfx, tb - 0.02, key_click(0.2))                                    # bookmark tap
add(sfx, tb, pop(0.2, 900))
add(sfx, tb + 0.1, scribble(0.5, 0.08))                               # circle
add(sfx, tb + 0.35, scribble(0.5, 0.07))                              # arrow
add(sfx, tb + 0.6, scribble(0.7, 0.08))                               # "saved it…"
items = R.words_at('l1', 1, span=0.85)
for w, ton in items:
    add(sfx, ton, tick(0.08))                                         # kinetic words
add(sfx, items[0][1] + 0.12, pop(0.14, 760))                          # inline photo
t0 = P('l1', 2)
add(sfx, t0 - 0.05, thud(0.25, 90))                                   # IF… slams in
add(sfx, t0 + 0.2, pop(0.2, 640))                                     # 3D question mark
for k in range(16):                                                   # typing "Can I foster if…"
    add(sfx, t0 + 0.05 + k * PD('l1', 2) * 0.9 / 16, key_click(0.07), pan=rng.uniform(-0.2, 0.2))
add(sfx, WT('l2', 0, 0.35), whoosh(0.4, 400, 5000, 0.1))              # arrow
add(sfx, WT('l2', 0, 0.55), thud(0.22, 110))                          # HONEST ANSWERS.
add(sfx, P('l3', 0) - 0.3, zip_up(0.1, 300, 1200, 0.3))               # popover opens
for i, line in enumerate(R.ALINES):
    tp = P(line, 1) if line != 'l7' else WT('l7', 1, 0.35)
    add(sfx, P(line, 0) + 0.15, key_click(0.12))                      # cursor taps the row
    add(sfx, tp, pop(0.24, 760 + 80 * i))                             # answer pill
    add(sfx, tp + 0.05, ping(0.06, 1320 if R.ROWS[i][1] in ('Yes',) else 1046))
    add(sfx, tp + 0.02, pop(0.16, 520))                               # 3D prop
for tt_, f in ((WT('l3', 2, 0.68), 820), (P('l3', 3) + 0.15, 980), (P('l5', 2) + 0.1, 820), (WT('l6', 2, 0.72), 760),
               (P('l6', 3), 880), (WT('l6', 4, 0.3), 1000)):
    add(sfx, tt_, pop(0.18, f))                                       # chips
add(sfx, P('l4', 2) + 0.1, zip_up(0.08, 400, 1600, 1.0))              # age track runs off the edge
for w, ton in R.words_at('l8', 0, span=0.85):
    add(sfx, ton, tick(0.07))
add(sfx, WT('l8', 0, 0.8), pop(0.2, 700))                             # icon
add(sfx, P('l8', 1) + 0.2, scribble(1.6, 0.07))                       # handwriting
tc = P('l9', 0) + PD('l9', 0) * 0.8
add(sfx, P('l9', 0) - 0.1, zip_up(0.08, 500, 1400, 0.3))              # bar morphs into the button
add(sfx, tc, key_click(0.22))                                         # click
add(sfx, tc + 0.02, pop(0.2, 900))
add(sfx, tc + 0.1, whoosh(0.8, 500, 7000, 0.14))                      # paper plane
add(sfx, P('l9', 1) + 0.1, ding(1568, 0.13))                          # notification 1
add(sfx, P('l9', 3) + 0.1, ding(1760, 0.11))                          # notification 2
add(sfx, WT('l9', 1, 0.5), pop(0.15, 820))
add(sfx, WT('l9', 2, 0.55), pop(0.15, 980))
add(sfx, P('l9', 2), pop(0.18, 640))                                  # speech bubble
add(sfx, P('l10', 0) - 0.25, shimmer(1.4, 0.16, 84))                  # end card
add(sfx, P('l10', 0) + 0.4, pop(0.18, 780))
sfx = reverb(sfx, wet=0.1, length=0.8, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{R.S}/tts/lines'


def vo_chain(x, sr):
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 75, 2)
    x = x + 0.18 * bp(x, 2500, 6500, 2)
    x = x + 0.08 * bp(x, 110, 260, 2)
    x = lp(x, 12500, 2)
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))
    thr = 0.22 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 2.6) / np.maximum(env, 1e-9), 1.0)
    return x * gain / max(1e-6, np.abs(x * gain).max()) * 0.9


for name in R.ORDER:
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, VO[name], vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.05, length=0.6, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.35 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.62 * lvl)[:, None] + sfx * 0.95 * (1 - 0.3 * lvl)[:, None]
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
print('wrote', f'{R.S}/audio/mix_raw.wav', 'last VO end', round(END('l10'), 2), 'DUR', DUR)
