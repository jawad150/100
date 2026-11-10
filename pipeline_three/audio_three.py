"""Soundtrack for Organic Fostering "Three of Me".

Light bed ("Wholesome" by Kevin MacLeod, incompetech.com, CC BY 4.0, credit in the caption) ducked under the ElevenLabs
voice (Ella), which plays all three characters. Street bustle for the 5:30 pm opener; a sticker slap (paper smack + pop)
for every 3D sticker; a quick swish on every jump cut; "You ask." is all three of her at once (both takes plus a lifted
copy). The bed swells on the end card and fades gently. Master -14 LUFS.
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
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, clack
import reel_three as R

T, DUR, OFF, SH = R.T, R.DUR, R.OFF, R.SH
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(3)
ts_ = np.arange(N) / SR


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def load(path):
    x, sr = sf.read(path)
    if x.ndim > 1:
        x = x.mean(1)
    return signal.resample_poly(x, SR, sr) if sr != SR else x


# ------------------------------------------------------------------ music bed
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, '..', 'workspace_sol', 'music', 'Wholesome.mp3'), '-ss', '6',
                      '-t', str(DUR + 1), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
tr = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)[:N]
tr = np.concatenate([tr, np.zeros((max(0, N - len(tr)), 2))])
tr = tr / max(1e-6, np.sqrt(np.mean(tr ** 2))) * 0.075
shape = np.clip(ts_ / 0.8, 0, 1) * (1 + 0.45 * np.clip((ts_ - SH['split'][0]) / 1.0, 0, 1))
music = tr * shape[:, None]
# the Worrier's lines get a darker, thinner bed
dark = np.zeros(N)
for nm in ('legs', 'wor1', 'wor2'):
    a, b = SH[nm]
    dark = np.maximum(dark, np.clip((ts_ - a) / 0.1 + 0.5, 0, 1) * np.clip((b - ts_) / 0.1 + 0.5, 0, 1))
music = music * (1 - 0.45 * dark)[:, None] + lp(music, 900, 2) * 0.35 * dark[:, None]

# ------------------------------------------------------------------ ambience: the walk home
noise = rng.normal(0, 1, (N, 2))
a, b = SH['legs']
street = np.clip((b + 0.1 - ts_) / 0.3, 0, 1)
amb += lp(noise, 900, 2) * 0.018 * street[:, None]
for k, tf in enumerate(np.arange(0.15, b, 0.27)):
    add(amb, tf, thud(0.05, 150 + 20 * (k % 3)), pan=rng.uniform(-0.5, 0.5))
amb += lp(noise, 400, 2) * 0.004 * (1 - street)[:, None]                 # quiet room after


# ------------------------------------------------------------------ sticker slaps and cut swishes
def slap_sfx(t0, pan=0.0, f=800):
    add(sfx, t0 + 0.2, crinkle(0.07, 0.2), pan=pan)
    add(sfx, t0 + 0.22, thud(0.14, 160), pan=pan)
    add(sfx, t0 + 0.2, pop(0.14, f), pan=pan)


SLAPS = [(T['work'] - 0.05, -0.4), (T['full'] - 0.05, 0.4),
         (SH['wor1'][0] + 0.25, 0.4), (T['foster'] - 0.05, -0.4), (T['right'] - 0.05, -0.2),
         (SH['opt1'][0] + 0.2, -0.4), (T['no'] - 0.05, -0.3),
         (SH['rea1'][0] + 0.25, 0.4), (T['possibly'] - 0.1, -0.4), (T['possibly'] + 0.05, 0.0),
         (T['hours'] - 0.05, -0.4), (T['flexibility'] - 0.05, 0.4), (T['support'] - 0.05, -0.4), (T['childs'] - 0.05, 0.4),
         (T['training'] - 0.05, -0.4), (T['meetings'] - 0.05, 0.4), (T['school'] - 0.05, -0.4),
         (T['working'] - 0.05, 0.4), (T['Plan'] - 0.05, -0.4), (T['Plan'] + 0.2, 0.1),
         (T['know'] - 0.05, 0.4),
         (SH['split'][0] + 0.3, -0.5), (SH['split'][0] + 0.4, 0.0), (SH['split'][0] + 0.5, 0.5),
         (T['ask'] - 0.05, 0.0), (T['ask'] + 0.25, 0.5)]
for j, (t0, pan) in enumerate(SLAPS):
    slap_sfx(t0, pan, 700 + 60 * (j % 5))
add(sfx, T['no'] + 0.4, whoosh(0.25, 800, 5000, 0.08), pan=-0.3)         # the NO is struck out
add(sfx, T['no'] + 0.45, clack(0.12))
for nm in R.ORDER[1:-1]:                                                   # jump cuts
    a = SH[nm][0]
    add(sfx, a - 0.06, whoosh(0.18, 600, 7000, 0.08), pan=rng.uniform(-0.4, 0.4))
    add(sfx, a, tick(0.06))
for k in range(3):                                                          # split-screen panels land
    add(sfx, SH['split'][0] + k * 0.1, whoosh(0.25, 400, 5000, 0.05), pan=(-0.5 + 0.5 * k))
a = SH['end'][0]
add(sfx, a - 0.25, crinkle(0.5, 0.14))                                     # the split peels away
add(sfx, a - 0.2, whoosh(0.5, 300, 4000, 0.07))
add(sfx, a + 0.7, pop(0.2, 880))
add(sfx, a + 1.5, shimmer(0.9, 0.06, 91))
add(sfx, a + 1.0, chime(84, 0.08, 2.0))
sfx = reverb(sfx, wet=0.1, length=0.6, key='room')

# ------------------------------------------------------------------ voice: one woman, three moods; "You ask." in chorus
info = R.json.load(open(f'{R.S}/tts/info.json'))
w1, w2 = info['words'], info['take2']
x1 = hp(load(f'{R.S}/tts/take1.wav'), 70, 2)
x2 = hp(load(f'{R.S}/tts/take2.wav'), 70, 2)
pk = max(np.abs(x1).max(), 1e-6)
x1, x2 = x1 / pk * 0.9, x2 / pk * 0.9
v = np.zeros(N)
i0 = int(OFF * SR)
n = min(len(x1), N - i0)
v[i0:i0 + n] = x1[:n]
y1 = w1[57][1]                                                              # "You" in take 1
y2 = w2[57][1]                                                              # "You" in take 2
seg2 = x2[int((y2 - 0.15) * SR):]
lift = signal.resample_poly(x1[int((y1 - 0.15) * SR):], 100, 106)           # a slightly lifted third voice
vL = v.copy()
vR = v.copy()
s2 = int((OFF + y1 - 0.15 + 0.025) * SR)
s3 = int((OFF + y1 - 0.15 + 0.045) * SR)
for buf, seg, st, g in ((vL, seg2, s2, 0.55), (vR, lift, s3, 0.5)):
    m = min(len(seg), N - st)
    buf[st:st + m] += seg[:m] * g
vR[s2:s2 + min(len(seg2), N - s2)] += seg2[:min(len(seg2), N - s2)] * 0.25
vL[s3:s3 + min(len(lift), N - s3)] += lift[:min(len(lift), N - s3)] * 0.2
vo = np.stack([vL, vR], 1) + 0.04 * np.stack([bp(v, 2500, 6000, 2)] * 2, 1)
vo = reverb(vo, wet=0.03, length=0.4, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * (1 - 0.6 * lvl)[:, None] + sfx * 0.9 * (1 - 0.25 * lvl)[:, None] + amb
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(1.8 * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR, 'voice ends', round(OFF + len(x1) / SR, 2))
