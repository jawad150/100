"""Build the BMHC "With the Rain" soundtrack: VO + recitation + ambience + SFX (+ optional vocal-pad bed).
Writes audio/mix_bed.wav and audio/mix_nobed.wav (48 kHz stereo, pre-loudnorm)."""
import json, os, subprocess
import numpy as np, soundfile as sf
from math import gcd
from scipy.signal import resample_poly, butter, sosfilt

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
SR = 48000
TL = json.load(open(P('timeline.json')))
VO = json.load(open(P('audio', 'vo', 'lines.json')))
END = TL['end']
N = int((END + 0.5) * SR)

def load(path, mono=False):
    tmp = path + '.48k.wav'
    if not os.path.exists(tmp):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ar', str(SR), '-ac', '2', tmp], check=True)
    x, sr = sf.read(tmp, dtype='float32')
    if x.ndim == 1: x = np.stack([x, x], 1)
    return x.mean(1, keepdims=True).repeat(2, 1) if mono else x

def db(x): return 10 ** (x / 20)
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
def norm(x, target_db): return x * db(target_db - rms_db(x[np.abs(x).max(1) > 1e-4] if (np.abs(x).max(1) > 1e-4).any() else x))
def env(points):
    """piecewise-linear gain envelope from [(t, gain_db), ...]"""
    t = np.arange(N) / SR
    ts, gs = zip(*points)
    return db(np.interp(t, ts, gs))[:, None]
def place(buf, x, t, gain=1.0):
    i = int(t * SR); j = min(N, i + len(x))
    if j > i: buf[i:j] += x[:j - i] * gain
def lp(x, f, order=4):
    sos = butter(order, f, 'low', fs=SR, output='sos'); return sosfilt(sos, x, axis=0)
def hp(x, f, order=2):
    sos = butter(order, f, 'high', fs=SR, output='sos'); return sosfilt(sos, x, axis=0)
def loop_to(x, n, xf=int(0.5 * SR)):
    out = np.zeros((n, 2), np.float32)
    fin = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
    pos = 0
    while pos < n:
        seg = x.copy()
        if pos > 0: seg[:xf] *= fin
        seg[-xf:] *= fin[::-1]
        k = min(len(seg), n - pos); out[pos:pos + k] += seg[:k]
        pos += len(seg) - xf
    return out

# ---------------------------------------------------------------- voice
vo = np.zeros((N, 2), np.float32)
vo_mask = np.zeros(N, np.float32)   # 1 while a voice/recitation plays (for ducking)
for L in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9']:
    x, sr = sf.read(P('audio', 'vo', f'{L}.wav'), dtype='float32')
    g = gcd(SR, sr); x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    x = hp(x, 80)
    x = np.stack([x, x], 1)
    x = norm(x, -20.0)
    t = TL['vo'][L]
    place(vo, x, t)
    vo_mask[int(t * SR): int(t * SR) + len(x)] = 1
for v, key in (('094005', 'rec5'), ('094006', 'rec6')):
    x, sr = sf.read(P('audio', f'rec_{v}.wav'), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    g = gcd(SR, sr); x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    x = np.stack([x, x], 1); x = norm(x, -20.5)
    t = TL['vo'][key]; place(vo, x, t)
    vo_mask[int(t * SR): int(t * SR) + len(x)] = 1

# ---------------------------------------------------------------- ambience + sfx
amb = np.zeros((N, 2), np.float32)
sh = {s['name']: s for s in TL['shots']}
v_start, v_end = sh['verse']['start'], sh['verse']['end']
glass = norm(load(P('audio', 'sfx', '1248.mp3')), -30)        # rain on glass, interior
street = norm(load(P('audio', 'sfx', '1247.mp3')), -31)       # long rain ambience
city = norm(load(P('audio', 'sfx', '2930.mp3')), -42)         # distant traffic
umb = lp(norm(load(P('audio', 'sfx', '1263.mp3')), -35), 6000)          # rain on umbrella
indoor = lp(norm(load(P('audio', 'sfx', '1253.mp3')), -33), 2500)
light = norm(load(P('audio', 'sfx', '2393.mp3')), -34)
door = norm(load(P('audio', 'sfx', '193.mp3')), -33)
amb += loop_to(glass, N) * env([(0, -60), (0.3, 0), (sh['man']['start'] - 0.2, 0), (sh['man']['start'] + 0.4, -60), (END, -60)])
amb += loop_to(street, N) * env([(0, -60), (sh['man']['start'] - 0.4, -60), (sh['man']['start'], 0), (v_start - 0.1, 0), (v_start + 0.55, -80), (END, -80)])
amb += loop_to(city, N) * env([(0, -60), (sh['man']['start'], -60), (sh['man']['start'] + 0.5, 0), (v_start - 0.1, 0), (v_start + 0.5, -80), (END, -80)])
u0 = sh['umbrella']['start']
amb += loop_to(umb, N) * env([(0, -80), (u0 - 0.1, -80), (u0 + 0.5, 0), (sh['mug']['start'], 0), (sh['mug']['start'] + 0.5, -80), (END, -80)])
m0 = sh['mug']['start']; b0 = sh['bmhc']['start']
amb += loop_to(indoor, N) * env([(0, -80), (m0 - 0.2, -80), (m0 + 0.3, -2), (b0 - 0.1, -2), (b0 + 0.4, -80), (END, -80)])
e0 = sh['endcard']['start']
amb += loop_to(light, N) * env([(0, -80), (b0 - 0.3, -80), (b0 + 0.3, 0), (e0, -2), (e0 + 2.2, -60), (END, -80)])
place(amb, door, TL['vo']['L7'] + 0.25, 1.0)

# phone buzz (synth): two short vibration pulses on wood
def buzz():
    d = 0.32; t = np.arange(int(d * SR)) / SR
    tone = (np.sign(np.sin(2 * np.pi * 172 * t)) * 0.5 + np.sin(2 * np.pi * 344 * t) * 0.3)
    e = np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.03)
    x = lp(tone * e, 1400).astype(np.float32)
    gap = np.zeros(int(0.16 * SR), np.float32)
    y = np.concatenate([x, gap, x])
    return np.stack([y, y], 1)
place(amb, norm(buzz(), -31), sh['phone']['start'] + 0.02)
# ceramic clink (synth)
def clink():
    t = np.arange(int(0.6 * SR)) / SR
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((2217, 1, 9), (3520, .6, 12), (5130, .35, 16), (7400, .2, 22)))
    y = y * np.minimum(1, t / 0.002)
    return np.stack([y, y * 0.9], 1).astype(np.float32)
place(amb, norm(clink(), -36), m0 + 0.55)

# soft-limit ambience transients
amb = (0.22 * np.tanh(amb / 0.22)).astype(np.float32)
# sacred silence safety: zero ambience during recitation + translation
amb *= env([(0, 0), (v_start + 0.6, 0), (v_start + 0.65, -90), (v_end - 0.05, -90), (v_end, 0), (END, 0)])

# ---------------------------------------------------------------- vocal pad bed (placeholder)
def make_pad():
    src = P('audio', 'sfx', '654.mp3')
    outs = []
    for name, pitch in (('pad_root', 0.5), ('pad_fifth', 0.749), ('pad_oct', 1.0)):
        out = P('audio', f'{name}.wav')
        if not os.path.exists(out):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.0', '-t', '4.6', '-i', src, '-af',
                            f'rubberband=pitch={pitch}:tempo=0.30:formant=preserved,aecho=0.8:0.85:120|260|510:0.35|0.25|0.15,lowpass=f=2200,highpass=f=90',
                            '-ar', str(SR), '-ac', '2', out], check=True)
        x, _ = sf.read(out, dtype='float32')
        outs.append(x)
    n = min(len(o) for o in outs)
    pad = outs[0][:n] * 1.0 + outs[1][:n] * 0.55 + outs[2][:n] * 0.18
    # smooth the swell: equal-power fade in/out on the segment
    f = int(1.2 * SR); w = np.ones(n, np.float32); w[:f] = np.sin(np.linspace(0, np.pi / 2, f)) ** 2; w[-f:] = np.cos(np.linspace(0, np.pi / 2, f)) ** 2
    return pad * w[:, None]

pad = make_pad()
bed = np.zeros((N, 2), np.float32)
step = len(pad) - int(1.6 * SR)
pos = 0
while pos < N:
    k = min(len(pad), N - pos); bed[pos:pos + k] += pad[:k]; pos += step
bed = norm(bed, -33)
# ducking under voice
from scipy.ndimage import uniform_filter1d
duck = uniform_filter1d(vo_mask, int(0.35 * SR))
duck_gain = db(-7.0 * np.clip(duck * 1.3, 0, 1))[:, None]
bed *= duck_gain
bed *= env([(0, -60), (0.2, -60), (1.6, 0), (v_start - 0.6, 0), (v_start + 0.2, -90), (v_end + 0.1, -90), (v_end + 1.6, 1.0),
            (TL['vo']['L7'], 1.0), (TL['vo']['L7'] + 1.5, 3.0), (TL['vo']['L8'] + 2.0, 1.5), (e0 + 2.5, 1.5), (END - 1.4, 0), (END - 0.1, -60), (END + 0.5, -90)])

# ---------------------------------------------------------------- sums
for name, use_bed in (('mix_bed', True), ('mix_nobed', False)):
    mix = vo + amb + (bed if use_bed else 0)
    mix = hp(mix, 30)
    sf.write(P('audio', f'{name}.wav'), mix.astype(np.float32), SR, subtype='FLOAT')
    print(name, 'peak', round(float(np.abs(mix).max()), 3))
sf.write(P('audio', 'stem_vo.wav'), vo, SR, subtype='PCM_24')
sf.write(P('audio', 'stem_amb.wav'), amb, SR, subtype='PCM_24')
sf.write(P('audio', 'stem_bed.wav'), bed, SR, subtype='PCM_24')
print('done', round(END, 2))
