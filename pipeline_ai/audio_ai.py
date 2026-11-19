"""Soundtrack for BMHC "AI can recreate this building". No music (BMHC guidelines: ambient sound only, voice first).

AI section: a dark room tone, a slow digital pulse, key clicks as the prompt types, a crackle of light as the lines
draw, whooshes on each camera move, UI ticks on the call-outs, soft pops for the 3D objects, a counter's rattle.
"Inside": a reverse swell into the eclipse, a deep low hit, the electronics cut away. Real life: authentic ambience
under each place (iftar chatter and a clink of tea glasses, a hall, an exhibition), the four-bar wipe as four soft
swishes, a film projector under the archive shot, the fair for 'alive', the night air as the windows light up.
Voice (ElevenLabs) on top, ambience ducked ~15 dB under speech. Master -14 LUFS.
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
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, thud, boom
import reel_ai as R

DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
rng = np.random.default_rng(23)
ts_ = np.arange(N) / SR
SFXD = f'{R.S}/sfx'


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def load(name, start=0.0, dur=None):
    a = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', f'{SFXD}/{name}.mp3']
    if dur:
        a += ['-t', str(dur)]
    raw = subprocess.run(a + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    return x / max(1e-6, np.sqrt(np.mean(x ** 2)))


def bed(name, t0, t1, gain, start=0.0, fin=0.25, fout=0.35, filt=None):
    x = load(name, start, t1 - t0 + 0.1)
    if filt:
        x = filt(x)
    n = min(len(x), int((t1 - t0) * SR))
    x = x[:n].copy()
    e = np.ones(n)
    a, b = int(fin * SR), int(fout * SR)
    e[:a] = np.linspace(0, 1, a) ** 1.5
    e[-b:] = np.linspace(1, 0, b) ** 1.5
    i = int(t0 * SR)
    amb[i:i + n] += x * e[:, None] * gain


def env(t, a, b, fi=0.3, fo=0.3):
    return np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1)


noise = rng.normal(0, 1, (N, 2))
AI_END = R.T_LC0 + 0.05

# ---------------- underneath everything: a dark cinematic room tone (deeper in the AI section)
rt = load('3081', 3.0, DUR + 0.5)[:N]
rt = np.pad(rt, ((0, max(0, N - len(rt))), (0, 0)))
amb += rt * (0.05 * env(ts_, 0.0, AI_END, 0.4, 0.2) + 0.022 * env(ts_, AI_END, DUR, 1.0, 1.5))[:, None]

# ---------------- AI section
pulse_t = np.arange(0.2, AI_END - 0.2, 1.25)
for p in pulse_t:                                                             # slow digital pulse
    add(sfx, p, thud(0.16, 52))
    add(sfx, p + 0.004, ping(0.012, 1760), pan=0.0)
q = 'Recreate this historic Manchester building.'
for k in range(len(q)):                                                       # typing
    t = 0.08 + (1.05 - 0.08) * k / len(q)
    add(sfx, t, key_click(rng.uniform(0.06, 0.1)), pan=rng.uniform(-0.2, 0.2))
add(sfx, 1.08, key_click(0.14))
# light crackling as lines draw (follows the build speed)
bp_ = np.array([R.build_progress(t) for t in ts_[::480]])
spd = np.clip(np.gradient(bp_, 480 / SR) / 0.8, 0, 1)
spd = np.interp(ts_, ts_[::480], spd)
amb += bp(noise, 3000, 11000, 2) * 0.02 * spd[:, None] * (ts_ < AI_END)[:, None]
for k in range(140):
    t = rng.uniform(0.3, R.T_SECONDS + 0.5)
    if rng.uniform() < np.interp(t, ts_[::480], spd[::480]) + 0.1:
        add(sfx, t, tick(rng.uniform(0.02, 0.06)), pan=rng.uniform(-0.7, 0.7))
add(sfx, R.T_SECONDS + 0.45, chime(88, 0.05, 1.6))                            # 'done'
for tk in (1.7, R.T_SECONDS + 0.35, R.T_WINDOW - 0.35, R.T_BRICK - 0.4, R.T_DETAIL - 0.4, R.T_BUT - 0.35):
    add(sfx, tk, whoosh(0.55, 200, 2600, 0.09), pan=rng.uniform(-0.4, 0.4))   # camera moves
for tk in (R.T_WINDOW, R.T_BRICK, R.T_DETAIL):
    add(sfx, tk + 0.05, tick(0.12))                                            # call-out
    add(sfx, tk + 0.25, ping(0.03, 2093))
    add(sfx, tk + 0.02, pop(0.14, 760))                                        # 3D pop
for k in range(22):                                                            # brick counter
    add(sfx, R.T_BRICK + 0.05 + 0.7 * (k / 22) ** 0.6, tick(0.035), pan=0.3)
add(sfx, R.T_INSIDE - 0.8, whoosh(1.0, 100, 900, 0.12, rev=False))             # into the eclipse
add(sfx, R.T_INSIDE - 0.05, boom(0.32))
cut = int(AI_END * SR)                                                         # the electronics drop away
tail = int(0.5 * SR)
sfx_ai = sfx[:cut + tail].copy()
sfx[:cut + tail] = 0
sfx_ai[cut:cut + tail] *= np.linspace(1, 0, tail)[:, None] ** 2
sfx[:cut + tail] = sfx_ai
for i in range(6):                                                             # layercut slices
    add(sfx, R.T_LC0 + 0.05 + i * 0.06, whoosh(0.25, 600, 4000, 0.035), pan=(-0.5 if i % 2 else 0.5))

# ---------------- real life
bed('364', R.T_LC0 + 0.1, R.C_FRIEND + 0.2, 0.05, start=5, fin=0.5)            # welcome: people around
bed('444', R.C_FRIEND, R.C_KNOW + 0.15, 0.075, start=12)                       # iftar
add(sfx, R.T_FRIEND + 0.15, load('154', 0.0, 1.2)[:int(1.2 * SR)] * 0.05)      # tea glasses clink
add(sfx, R.T_FRIEND + 0.08, pop(0.1, 700))
bed('366', R.C_KNOW, R.C_YOUNG + 0.1, 0.05, start=4)                           # exhibition talk
add(sfx, R.T_KNOW + 0.05, pop(0.1, 820))
for k in range(4):                                                             # pages
    add(sfx, R.T_KNOW + 0.25 + k * 0.09, whoosh(0.12, 2000, 6000, 0.03))
bed('364', R.C_YOUNG, R.C_CONV + 0.1, 0.06, start=22)                          # the hall
add(sfx, R.T_YOUNG + 0.1, pop(0.1, 760))
add(sfx, R.T_CONF - 0.15, whoosh(0.3, 800, 5000, 0.07, rev=False))             # arrow
add(sfx, R.T_CONF + 0.12, thud(0.35, 90))
add(sfx, R.T_CONF + 0.12, tick(0.15))
bed('366', R.C_CONV, R.W_HER0 + 0.5, 0.06, start=12)                           # conversation + laughter
add(sfx, R.T_CONV + 0.02, pop(0.12, 880))
add(sfx, R.T_CONV + 0.22, pop(0.1, 1040))
add(sfx, R.T_TOG, pop(0.09, 660))
for i in range(4):                                                             # four-bar wipe
    add(sfx, R.W_HER0 + i * 0.07, whoosh(0.3, 300, 2500, 0.05), pan=-0.6 + 0.4 * i)
# archive film: projector rattle + hiss under the heritage shot
p0, p1 = R.C_HER, R.X_ALIVE1
proj = np.zeros(N)
clicks = np.arange(p0, p1, 1 / 24)
for c_ in clicks:
    i = int(c_ * SR)
    if i + 200 < N:
        proj[i:i + 200] += rng.normal(0, 1, 200) * np.exp(-np.arange(200) / 40)
proj = bp(proj, 900, 5000, 2) * 0.05
hiss = bp(noise[:, 0], 2000, 9000, 2) * 0.012
pe = env(ts_, p0, p1, 0.3, 0.5)
amb += np.stack([proj + hiss, proj * 0.9 + hiss], 1) * pe[:, None]
add(sfx, R.T_HER + 0.05, pop(0.1, 600))
add(sfx, R.X_ALIVE0, whoosh(0.9, 150, 2500, 0.08))                             # it comes alive
add(sfx, R.T_ALIVE - 0.05, shimmer(1.6, 0.05, 86))
bed('368', R.X_ALIVE0 + 0.2, R.C_BRIT + 0.2, 0.06, start=3, fin=0.6)           # the fair
add(sfx, R.T_KEEP - 0.08, pop(0.1, 700))
bed('3080', R.C_BRIT - 0.1, R.C_END + 0.5, 0.05, start=10, fin=0.4)            # night air
for k in range(14):                                                            # windows lighting up
    add(sfx, R.T_LIVING - 1.0 + k * 0.12 + rng.uniform(0, 0.06), ping(0.007, rng.choice([1568, 1760, 2093, 2349])), pan=rng.uniform(-0.6, 0.6))
for i in range(4):                                                             # four-bar wipe to the end card
    add(sfx, R.W_END0 + i * 0.07, whoosh(0.3, 300, 2500, 0.05), pan=-0.6 + 0.4 * i)
add(sfx, R.T_COME + 0.05, chime(84, 0.05, 3.0))
add(sfx, R.T_EXP + 0.2, pop(0.08, 660))
sfx = reverb(sfx, wet=0.14, length=1.2, key='room')

# ---------------- voice
vo_path = f'{R.S}/tts/vo.wav'
if os.path.exists(vo_path) and not R.INFO.get('placeholder'):
    x, sr = sf.read(vo_path)
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 60, 2)
    x = x / max(1e-6, np.abs(x).max()) * 0.9
    v = np.zeros(N)
    i0 = int(R.OFF * SR)
    m = min(len(x), N - i0)
    v[i0:i0 + m] = x[:m]
    vo = np.stack([v, v], 1) + 0.04 * np.stack([bp(v, 2500, 6000, 2)] * 2, 1)
    vo = reverb(vo, wet=0.05, length=0.7, key='vo_room')
else:
    vo = np.zeros((N, 2))
    print('NOTE: no real voice yet - soundtrack without voiceover')

e = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], e)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
mix = sfx * 0.9 * (1 - 0.45 * lvl)[:, None] + amb * (1 - 0.82 * lvl)[:, None] + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.6 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.02 * SR)] = np.linspace(0, 1, int(0.02 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR)
