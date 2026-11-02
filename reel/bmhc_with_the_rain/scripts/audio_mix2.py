"""v2 soundtrack: narration + recitation + ambience + transition sound design + click, with a background bed.
Usage: python3 -I audio_mix2.py BED OUTNAME
  BED = none | vocal | <path to a music file>[@start_seconds]
Writes audio/OUTNAME.wav (48 kHz stereo float, pre-loudnorm). The verse (recitation + translation) always stays free of music and ambience."""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from math import gcd
from scipy.signal import resample_poly, butter, sosfilt
from scipy.ndimage import uniform_filter1d

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
SR = 48000
TL = json.load(open(P('timeline.json')))
VO = json.load(open(P('audio', 'vo', 'lines.json')))
SH = {s['name']: s for s in TL['shots']}
END = TL['end']
N = int((END + 0.5) * SR)
TAP = json.load(open(P('overlays3', 'meta.json')))['tap']
BED = sys.argv[1] if len(sys.argv) > 1 else 'vocal'
OUTNAME = sys.argv[2] if len(sys.argv) > 2 else 'mix2'
rng = np.random.default_rng(7)

def load(path):
    tmp = path + '.48k.wav'
    if not os.path.exists(tmp):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ar', str(SR), '-ac', '2', tmp], check=True)
    x, _ = sf.read(tmp, dtype='float32')
    return np.stack([x, x], 1) if x.ndim == 1 else x
def db(x): return 10 ** (np.asarray(x) / 20)
def rms_db(x):
    m = np.abs(x).max(1) > 1e-4
    return 20 * np.log10(np.sqrt(np.mean(x[m] ** 2 if m.any() else x ** 2)) + 1e-9)
def norm(x, target): return (x * db(target - rms_db(x))).astype(np.float32)
def env(points):
    t = np.arange(N) / SR; ts, gs = zip(*sorted(points)); return db(np.interp(t, ts, gs))[:, None].astype(np.float32)
def place(buf, x, t, gain=1.0):
    i = int(round(t * SR)); j = min(N, i + len(x))
    if i < 0: x = x[-i:]; i = 0
    if j > i: buf[i:j] += x[:j - i] * gain
def filt(x, f, kind, order=4):
    return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x, axis=0).astype(np.float32)
def loop_to(x, n, xf=int(0.5 * SR)):
    out = np.zeros((n, 2), np.float32); fin = np.linspace(0, 1, xf, dtype=np.float32)[:, None]; pos = 0
    while pos < n:
        seg = x.copy()
        if pos > 0: seg[:xf] *= fin
        seg[-xf:] *= fin[::-1]
        k = min(len(seg), n - pos); out[pos:pos + k] += seg[:k]; pos += len(seg) - xf
    return out
def st(y, w=0.0):          # mono -> stereo with a little width
    y = y.astype(np.float32); return np.stack([y * (1 - w), y * (1 + w)], 1)
def T(name): return SH[name]['start']

# ---------------------------------------------------------------- voice
vo = np.zeros((N, 2), np.float32); vo_mask = np.zeros(N, np.float32)
for L in ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9']:
    x, sr = sf.read(P('audio', 'vo', f'{L}.wav'), dtype='float32')
    g = gcd(SR, sr); x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    x = norm(st(filt(x, 80, 'high', 2)), -20.0)
    place(vo, x, TL['vo'][L]); i = int(TL['vo'][L] * SR); vo_mask[i:i + len(x)] = 1
for v, key in (('094005', 'rec5'), ('094006', 'rec6')):
    x, sr = sf.read(P('audio', f'rec_{v}.wav'), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    g = gcd(SR, sr); x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    x = norm(st(x), -20.5); place(vo, x, TL['vo'][key]); i = int(TL['vo'][key] * SR); vo_mask[i:i + len(x)] = 1

# ---------------------------------------------------------------- ambience (follows the pictures)
v0, v1 = T('verse'), SH['verse']['end']
amb = np.zeros((N, 2), np.float32)
glass = norm(load(P('audio', 'sfx', '1248.mp3')), -30)
street = norm(load(P('audio', 'sfx', '1247.mp3')), -31)
city = norm(load(P('audio', 'sfx', '2930.mp3')), -42)
umb = filt(norm(load(P('audio', 'sfx', '1263.mp3')), -35), 6000, 'low')
indoor = filt(norm(load(P('audio', 'sfx', '1253.mp3')), -34), 2200, 'low')
light = norm(load(P('audio', 'sfx', '2393.mp3')), -35)
door = filt(norm(load(P('audio', 'sfx', '193.mp3')), -34), 5000, 'low')
m0, u0, w0, e0, c0, p0, b0, i0, k0, E0 = (T(n) for n in ('man', 'umbrella', 'with2', 'ease', 'console', 'phonep', 'bmhc', 'inside', 'convo', 'endcard'))
amb += loop_to(glass, N) * env([(0, -60), (0.15, -18), (1.2, 0), (m0 - 0.2, 0), (m0 + 0.4, -60), (END, -60)])
amb += loop_to(street, N) * env([(0, -70), (m0 - 0.35, -70), (m0, 0), (v0 - 0.3, 0), (v0 + 0.5, -80), (END, -80)])
amb += loop_to(city, N) * env([(0, -70), (m0, -70), (m0 + 0.5, 0), (v0 - 0.3, 0), (v0 + 0.5, -80), (END, -80)])
amb += loop_to(umb, N) * env([(0, -80), (u0 - 0.05, -80), (u0 + 0.5, 0), (e0 - 0.1, 0), (e0 + 0.3, -80), (END, -80)])
amb += loop_to(street, N)[::-1].copy() * env([(0, -80), (e0 - 0.2, -80), (e0 + 0.3, -2), (c0, -2), (c0 + 0.4, -80), (END, -80)])
amb += loop_to(indoor, N) * env([(0, -80), (c0 - 0.2, -80), (c0 + 0.3, -1), (b0 - 0.1, -1), (b0 + 0.3, -80), (i0, -80), (i0 + 0.4, -8), (E0 + 0.3, -8), (E0 + 1.5, -80), (END, -80)])
amb += loop_to(light, N) * env([(0, -80), (b0 - 0.2, -80), (b0 + 0.3, 0), (i0 - 0.1, 0), (i0 + 0.3, -80), (END, -80)])
place(amb, door, b0 - 0.12, 0.9)

# ---------------------------------------------------------------- transition sound design (synthesised, quiet)
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def sweep(d, f0, f1, q_bw=0.6, curve=1.0):
    """filtered-noise whoosh: a band that moves from f0 to f1, rendered in short blocks"""
    n = int(d * SR); x = noise(d); out = np.zeros(n, np.float32); blk = 1024
    for a in range(0, n, blk):
        u = (a / n) ** curve; f = f0 * (f1 / f0) ** u
        lo, hi = max(40, f * (1 - q_bw / 2)), min(SR / 2 - 100, f * (1 + q_bw / 2))
        out[a:a + blk] = sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x[max(0, a - 2048):a + blk])[-len(x[a:a + blk]):]
    return out
def shape(x, a, r):
    n = len(x); t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-3)) * np.minimum(1, (n / SR - t) / max(r, 1e-3))
    return x * e.astype(np.float32)
def droplet():
    t = np.arange(int(0.35 * SR)) / SR; f = 1500 * np.exp(-t * 9) + 380
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) + 0.25 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * np.exp(-t * 22)
    return y.astype(np.float32)
def buzz():
    d = 0.3; t = np.arange(int(d * SR)) / SR
    tone = np.sign(np.sin(2 * np.pi * 172 * t)) * 0.5 + np.sin(2 * np.pi * 344 * t) * 0.3
    x = filt(shape(tone.astype(np.float32), 0.01, 0.03), 1400, 'low')
    return np.concatenate([x, np.zeros(int(0.15 * SR), np.float32), x])
def click():
    t = np.arange(int(0.09 * SR)) / SR
    tick = noise(0.09) * np.exp(-t * 900); body = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 160) * 0.6 + np.sin(2 * np.pi * 620 * t) * np.exp(-t * 90) * 0.5
    up = np.zeros(int(0.07 * SR), np.float32); t2 = np.arange(int(0.05 * SR)) / SR
    rel = (np.sin(2 * np.pi * 2400 * t2) * np.exp(-t2 * 220) * 0.35 + noise(0.05) * np.exp(-t2 * 1200) * 0.4).astype(np.float32)
    return np.concatenate([(tick * 0.8 + body).astype(np.float32), up, rel])
def soft_ripple():
    """a light, airy water sound for the ripple: a breath of high air plus one gentle bubble, both in a soft room"""
    from scipy.signal import fftconvolve
    d = 1.3; n = int(d * SR); t = np.arange(n) / SR
    air = filt(filt(noise(d), 2500, 'high', 2), 9000, 'low', 2) * (np.minimum(1, t / 0.35) * np.exp(-np.maximum(0, t - 0.35) * 3.2))
    bt = np.arange(int(0.07 * SR)) / SR
    bub = np.sin(2 * np.pi * np.cumsum(520 + 380 * bt / 0.07) / SR) * np.hanning(len(bt))
    dry = air * 0.8; dry[int(0.3 * SR):int(0.3 * SR) + len(bub)] += bub * 0.22
    ir_t = np.arange(int(0.9 * SR)) / SR
    L = fftconvolve(dry, filt(noise(0.9) * np.exp(-ir_t * 5), 6000, 'low', 2))[:n]
    R = fftconvolve(dry, filt(noise(0.9) * np.exp(-ir_t * 5), 6000, 'low', 2))[:n]
    w = np.stack([dry * 0.5 + L * 0.06, dry * 0.5 + R * 0.06], 1)
    return w * np.minimum(1, (d - t) / 0.4)[:, None]
def pop():   # soft bubble under the ripple on the button
    t = np.arange(int(0.25 * SR)) / SR; f = 300 + 500 * (1 - np.exp(-t * 30))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)).astype(np.float32)

fx = np.zeros((N, 2), np.float32)
place(fx, st(norm(st(shape(sweep(0.75, 900, 90, 0.8, 0.7), 0.25, 0.2)), -36)[:, 0], 0.05), v0 - 0.7)     # sinking into the dark, into silence
place(fx, norm(soft_ripple().astype(np.float32), -43), u0 - 0.32)                                              # a light, airy ripple sound (replaces the v2 drop)
place(fx, st(norm(st(shape(sweep(0.5, 300, 2400, 0.7, 1.4), 0.3, 0.15)), -40)[:, 0], 0.2), w0 - 0.28)     # motion handoff
place(fx, st(norm(st(shape(sweep(0.55, 200, 5000, 0.9, 1.8), 0.45, 0.08)), -41)[:, 0], 0.15), e0 - 0.5)   # light breaks through
place(fx, st(norm(st(shape(sweep(0.75, 5200, 900, 0.5, 0.8), 0.1, 0.3)), -42)[:, 0], 0.1), c0 - 0.32)     # streak running down the glass
place(fx, norm(st(buzz()), -31), p0 + 0.01)                                                                # the call (hard cut)
place(fx, st(norm(st(shape(sweep(0.6, 150, 3000, 0.8, 1.6), 0.5, 0.06)), -40)[:, 0], 0.15), i0 - 0.55)   # through the lit door
place(fx, st(norm(st(shape(sweep(0.7, 600, 2600, 0.5, 1.0), 0.3, 0.35)), -44)[:, 0], 0.2), E0 - 0.45)    # gold line opens the panel
place(fx, norm(st(click()), -27), TAP - 0.035)                                                            # the button tap
place(fx, norm(st(pop()), -38), TAP + 0.02)
fx = filt(fx, 60, 'high', 2)

wet = 0.22 * np.tanh((amb + fx) / 0.22)
silence = env([(0, 0), (v0 + 0.55, 0), (v0 + 0.65, -90), (v1 - 0.25, -90), (v1 - 0.1, 0), (END, 0)])
wet = (wet * silence).astype(np.float32)

# ---------------------------------------------------------------- bed
def pitched(pitch, name, src='654', ss=1.0, dur=4.6):
    out = P('audio', f'pad2_{name}.wav')
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', P('audio', 'sfx', f'{src}.mp3'), '-af',
                        f'rubberband=pitch={pitch}:tempo=0.28:formant=preserved,aecho=0.8:0.88:140|300|560|900:0.35|0.26|0.16|0.1,lowpass=f=2400,highpass=f=55',
                        '-ar', str(SR), '-ac', '2', out], check=True)
    x, _ = sf.read(out, dtype='float32')
    f = int(1.4 * SR); w = np.ones(len(x), np.float32)
    w[:f] = np.sin(np.linspace(0, np.pi / 2, f)) ** 2; w[-f:] = np.cos(np.linspace(0, np.pi / 2, f)) ** 2
    return loop_to(x * w[:, None], N, xf=f)
def vocal_bed():
    """voices only: a low choir drone. Before the verse it holds a minor colour; after it, the third lifts to major."""
    root, fifth, octv = pitched(0.5, 'root'), pitched(0.749, 'fifth'), pitched(1.0, 'oct')
    sub = filt(pitched(0.25, 'sub'), 380, 'low')
    m3, M3 = pitched(0.5 * 1.1892, 'min3'), pitched(0.5 * 1.2599, 'maj3')
    pre = env([(0, 0), (v0 - 0.2, 0), (v0 + 0.3, -90), (END, -90)])
    post = env([(0, -90), (v1 - 0.3, -90), (v1 + 0.6, 0), (END, 0)])
    bed = root * 1.0 + fifth * 0.5 + sub * 0.55 + octv * 0.16 + m3 * 0.38 * pre + M3 * 0.42 * post
    lfo = (1 + 0.12 * np.sin(2 * np.pi * np.arange(N) / SR / 11.0))[:, None]
    return (bed * lfo).astype(np.float32)
def music_bed(spec):
    """path@pre@post: the intro plays from `pre` seconds into the track; after the verse the track
    re-enters from `post`, chosen so its build peaks on the brand reveal."""
    path, pre, post = (spec.split('@') + ['0', '0'])[:3]
    x = load(path); out = np.zeros((N, 2), np.float32)
    a = int(float(pre) * SR); n1 = int((v0 + 0.3) * SR); seg = x[a:a + n1]; out[:len(seg)] += seg
    b = int(float(post) * SR); i = int((v1 - 0.4) * SR); seg = x[b:b + (N - i)]
    f = np.linspace(0, 1, int(1.2 * SR), dtype=np.float32)[:, None]; seg = seg.copy(); seg[:len(f)] *= f[:len(seg)]
    out[i:i + len(seg)] += seg
    return out

if BED == 'none':
    bed = np.zeros((N, 2), np.float32)
else:
    bed = vocal_bed() if BED == 'vocal' else music_bed(BED)
    bed = norm(bed, -28.5 if BED == 'vocal' else -29)
    # carve a little room for the voice (presence band) and keep the low end tidy
    bed = filt(bed, 50, 'high', 2)
    vb = filt(bed, [1200, 4200], 'band', 2)
    duck = uniform_filter1d(vo_mask, int(0.35 * SR))
    bed = bed - vb * (0.45 * np.clip(duck * 1.3, 0, 1))[:, None]
    bed *= db(-8.0 * np.clip(duck * 1.3, 0, 1))[:, None]
    # shape across the film: rise in, step back for the problem, silent for the verse, lift for ease, swell at the brand reveal
    bed *= env([(0, -60), (0.3, -30), (2.2, 0), (m0, 0), (m0 + 0.6, -1.5), (v0 - 0.75, -1.5), (v0 - 0.05, -90), (v1 - 0.2, -90),
                (u0 + 0.9, -1), (e0, 0.5), (c0 + 0.5, 1.5), (b0, 2.0), (k0, 2.0), (E0 + 0.6, 3.5), (TAP + 1.0, 3.0),
                (END - 1.6, 1.5), (END - 0.05, -60), (END + 0.5, -90)])

mix = filt(vo + wet + bed, 30, 'high', 2)
sf.write(P('audio', f'{OUTNAME}.wav'), mix.astype(np.float32), SR, subtype='FLOAT')
sf.write(P('audio', f'{OUTNAME}_stem_bed.wav'), bed.astype(np.float32), SR, subtype='FLOAT')
sf.write(P('audio', 'stem2_vo.wav'), vo, SR, subtype='FLOAT'); sf.write(P('audio', 'stem2_fx.wav'), wet, SR, subtype='FLOAT')
print(OUTNAME, 'bed', BED, 'peak', round(float(np.abs(mix).max()), 3), 'len', round(END, 2), 'tap', TAP)
