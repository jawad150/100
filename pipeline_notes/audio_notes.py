"""Soundtrack for Organic Fostering "The Question in the Notes App".

Delete-key taps under the hook, pops for kinetic words and 3D objects, slice swishes for the layercut, a tape-rewind
squeal for 'that week', the phone set down by the mug, a UK ring tone as she calls, soft rain on 'struggling', node pops
along the explainer path, a low shimmer for the eclipse, typing for the new line and a tick, a chime on the logo.
Voices: ElevenLabs (caller: Kerry; team member: British Warm Friendly). The team member's answer sounds like it is
coming down the phone line; the closing line is clean. Music: "Lasting Hope" by Kevin MacLeod (incompetech.com,
CC BY 4.0), ducked under speech. Master -14 LUFS.
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
from audio_of import lp, hp, bp, reverb, SR, chime, tt
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, thud, clack
import reel_notes as R

DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
rng = np.random.default_rng(9)
ts_ = np.arange(N) / SR
noise = rng.normal(0, 1, (N, 2))


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def env(a, b, fi=0.2, fo=0.3):
    return np.clip((ts_ - a) / fi, 0, 1) * np.clip((b - ts_) / fo, 0, 1)


# ---------------- 0: the hook
add(sfx, 0.05, clack(0.22))                                                    # the first tap of the delete key
n = len(R.HOOK)
for k in range(n):
    add(sfx, 0.35 + (2.4 - 0.35) * k / n, key_click(rng.uniform(0.05, 0.08)), pan=0.2)
for t0, f in ((0.05, 760), (0.25, 860), (0.45, 980)):
    add(sfx, t0, pop(0.1, f))
add(sfx, 0.7, whoosh(0.3, 1500, 5000, 0.05))                                   # strike-through
add(sfx, R.T_QUESTION - 0.05, pop(0.09, 820))
add(sfx, R.T_THREE - 0.05, pop(0.12, 700))
for i in range(5):                                                             # layercut slices
    add(sfx, R.T_THREE + 0.15 + i * 0.05, whoosh(0.22, 800, 4500, 0.035), pan=(-0.5 if i % 2 else 0.5))
add(sfx, R.T_TIMES, ping(0.05, 1760))
add(sfx, R.T_TIMES + 0.08, pop(0.12, 1040))
# retro: a tape rewinding (squealing sweep + hiss)
r0, r1 = R.X_RETRO0, R.X_RETRO1
k = np.clip((ts_ - r0) / (r1 - r0), 0, 1)
f = 900 + 2600 * k
sq = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.012 * env(r0, r1, 0.1, 0.15)
amb += np.stack([sq, sq], 1) + bp(noise, 2000, 9000, 2) * 0.012 * env(r0, r1, 0.1, 0.2)[:, None]
add(sfx, R.T_WEEK - 0.2, pop(0.1, 640))
# spiral down + the phone set beside the mug
add(sfx, R.SP0, whoosh(0.9, 250, 2800, 0.08))
add(sfx, R.SP0 + 0.1, pop(0.08, 560))
add(sfx, R.SP1 - 0.25, thud(0.18, 140))
add(sfx, R.SP1 - 0.24, tick(0.12))
add(sfx, R.CW0, whoosh(0.5, 300, 3500, 0.07))                                  # circle wipe
# UK ring tone (400 + 450 Hz, brr-brr) while she dials
for st in (R.CW1 - 0.25,):
    for j in range(2):
        tt0 = st + j * 0.6
        x = (np.sin(2 * np.pi * 400 * tt(0.4)) + np.sin(2 * np.pi * 450 * tt(0.4))) * 0.006
        x = bp(x, 300, 3400, 2)
        add(sfx, tt0, np.stack([x, x], 1))
# ---------------- 2: the call
amb += lp(noise, 600, 2) * 0.006 * env(R.CW1, R.BW0, 0.3, 0.3)[:, None]       # room
add(sfx, R.T_CAN - 0.05, pop(0.08, 700))
add(sfx, R.T_SOMETHING - 0.05, pop(0.1, 900))
add(sfx, R.T_STRUG - 0.05, pop(0.11, 520))
rain = hp(noise, 3000, 2) * 0.012 * env(R.T_STRUG, R.BW0 + 0.2, 0.4, 0.4)[:, None]
amb += rain
for j in range(40):
    add(sfx, R.T_STRUG + rng.uniform(0, R.BW0 - R.T_STRUG), tick(rng.uniform(0.01, 0.03)), pan=rng.uniform(-0.8, 0.8))
add(sfx, R.T_CHILD - 0.05, pop(0.11, 660))
add(sfx, R.T_CHILD + 0.15, chime(79, 0.035, 1.6))                              # warm light in the doorway
add(sfx, R.BW0, whoosh(0.6, 150, 1800, 0.09))                                  # into night
# ---------------- 3: the answer
add(sfx, R.T_SOCIAL - 0.05, pop(0.12, 740))
add(sfx, R.T_WORKER - 0.1, thud(0.08, 180))                                     # the mug stops
for tt0, f in ((R.T_TALK - 0.4, 820), (R.T_TALK, 920), (R.T_SUPPORT, 1020), (R.T_CALL, 1120)):
    add(sfx, tt0, pop(0.09, f))
    add(sfx, tt0 + 0.02, ping(0.015, f * 2))
add(sfx, R.EC0, whoosh(1.1, 120, 1200, 0.08))                                   # eclipse
add(sfx, R.T_OUTSIDE - 0.1, shimmer(1.6, 0.05, 86))
add(sfx, R.T_OUTSIDE + 0.0, pop(0.1, 600))
amb += bp(noise, 200, 900, 2) * 0.008 * env(R.EC0, R.NW0, 0.6, 0.4)[:, None]    # night air
# ---------------- 4: back to the notes app
add(sfx, R.NW0, whoosh(0.45, 400, 4000, 0.06))
add(sfx, R.NW1 + 0.05, ping(0.035, 1568))                                       # tick
add(sfx, R.T_OKAY - 0.03, pop(0.09, 880))
nn = len(R.NEW)
for k in range(nn):
    if R.NEW[k] != ' ':
        add(sfx, R.T_CAN2 - 0.1 + (R.T_WELL - R.T_CAN2) * k / nn, key_click(rng.uniform(0.05, 0.08)), pan=-0.1)
add(sfx, R.T_TRAIN - 0.05, pop(0.12, 780))
# ---------------- 5: end card
add(sfx, R.END0, whoosh(0.5, 300, 3000, 0.07))
add(sfx, R.END1 + 0.1, chime(84, 0.06, 2.6))
add(sfx, R.T_ENQ, pop(0.1, 880))
sfx = reverb(sfx, wet=0.1, length=0.8, key='room')

# ---------------- music
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Lasting_Hope.mp3'), '-ss', '0',
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.07
music = np.zeros((N, 2))
i0 = int(0.4 * SR)
m = min(len(tr), N - i0)
music[i0:i0 + m] = tr[:m]
mus_env = np.clip((ts_ - 0.4) / 1.5, 0, 1) * (1 - 0.35 * env(R.BW0, R.NW0, 0.6, 0.6)) * (1 + 0.35 * np.clip((ts_ - R.END0) / 1.0, 0, 1))
music *= mus_env[:, None]

# ---------------- voices
info = R.INFO


def load_vo(path):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    y = np.zeros(N)
    y[:min(N, len(x))] = x[:N]
    return hp(y, 70, 2)


vc = load_vo(f'{R.S}/tts/vo_caller.wav')
vt = load_vo(f'{R.S}/tts/vo_team.wav')
phone = np.zeros(N)
for spk, a0, a1, f0, ph in info['segs']:
    if spk == 'team' and ph:
        phone[int(f0 * SR):int((f0 + a1 - a0) * SR)] = 1
phone = np.convolve(phone, np.ones(int(0.02 * SR)) / int(0.02 * SR), mode='same')
vt_phone = np.tanh(bp(vt, 320, 3600, 2) * 2.2) / 2.2 * 1.6
vt = vt * (1 - phone) + vt_phone * phone
pk = max(np.abs(vc).max(), np.abs(vt).max(), 1e-6)
v = (vc + vt) / pk * 0.9
vo = np.stack([v, v], 1)
vo = reverb(vo, wet=0.03, length=0.5, key='vo_room')

e = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], e)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
mix = music * (1 - 0.6 * lvl)[:, None] + sfx * 0.9 * (1 - 0.3 * lvl)[:, None] + amb * (1 - 0.3 * lvl)[:, None] + vo * 1.45
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
