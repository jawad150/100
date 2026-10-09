"""Procedural score + sound design for the Organic Fostering reel (48 kHz stereo WAV).

Warm, hopeful D-major piano/pad score with a soft modern pulse, plus SFX locked to
the edit: montage ticks, coin shimmer, orb swishes and chimes, glass UI pops, clock
ticks, typing, whooshes, birdsong (morning) and a resolving logo chord.
"""
import os, math
import numpy as np
from scipy import signal
from scipy.io import wavfile

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_of')))
SR = 48000
DUR = 19.0
N = int(SR * DUR)
rng = np.random.default_rng(11)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(buf, t0, x, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if x.ndim == 1:
        l, r = math.sqrt(0.5 * (1 - pan)) * 1.414, math.sqrt(0.5 * (1 + pan)) * 1.414
        x = np.stack([x * l, x * r], 1)
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), N - i)
    if n > 0:
        buf[i:i + n] += x[:n] * gain


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'high')
    return signal.lfilter(b, a, x, axis=0)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], 'band')
    return signal.lfilter(b, a, x, axis=0)


def env_adsr(n, a=0.005, d=0.2, s=0.0, r=0.3, total=None):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), 0.0)
    dec = (t >= a)
    e = np.where(dec, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)), e)
    if total is not None:
        rel = t > total
        e = np.where(rel, e * np.exp(-(t - total) / max(r, 1e-4)), e)
    return e


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


_ir = {}


def reverb(x, wet=0.3, length=2.2, key='hall'):
    if key not in _ir:
        n = int(length * SR)
        e = np.exp(-np.linspace(0, 6.5, n))
        irl = lp(rng.normal(0, 1, n) * e, 7000)
        irr = lp(rng.normal(0, 1, n) * e, 7000)
        _ir[key] = np.stack([irl, irr], 1) / np.sqrt(np.sum(e ** 2)) * 0.45
    ir = _ir[key]
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([signal.fftconvolve(x[:, 0], ir[:, 0])[:len(x)], signal.fftconvolve(x[:, 1], ir[:, 1])[:len(x)]], 1)
    return x * (1 - wet) + y * wet


# ------------------------------------------------------------------ instruments
def piano(m, dur=1.6, vel=0.6):
    """Felt-piano-ish tone: inharmonic partials, soft hammer, lowpassed."""
    f = mtof(m)
    t = tt(dur + 0.8)
    x = np.zeros_like(t)
    for k, amp in enumerate([1.0, 0.45, 0.22, 0.12, 0.06, 0.03], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        x += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * (1.6 + 0.9 * k))
    hammer = lp(rng.normal(0, 1, len(t)) * np.exp(-t * 60), 2500) * 0.15
    x = (x + hammer) * np.minimum(1, t / 0.004)
    x *= np.where(t > dur, np.exp(-(t - dur) * 6), 1.0)
    return lp(x, 2800 + vel * 2000) * vel


def pad(ms, dur, vel=0.25, bright=1400):
    t = tt(dur)
    x = np.zeros((len(t), 2))
    for m in ms:
        f = mtof(m)
        for det, ch in [(-0.07, 0), (0.07, 1), (0.0, 0), (0.0, 1)]:
            ph = rng.uniform(0, 6.28)
            saw = 2 * ((f * (1 + det / 100) * t + ph / 6.28) % 1.0) - 1
            x[:, ch] += saw * 0.5
    a = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.8)
    x = lp(x, bright, 2) * a[:, None] * vel / max(len(ms), 1)
    return x


def bass(m, dur, vel=0.5):
    t = tt(dur)
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    e = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.1)
    return x * e * vel


def kick(vel=0.8):
    t = tt(0.45)
    f = 45 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 8)
    click = lp(rng.normal(0, 1, len(t)) * np.exp(-t * 300), 4000) * 0.2
    return (x + click) * vel


def shaker(vel=0.2):
    t = tt(0.09)
    return hp(rng.normal(0, 1, len(t)), 6000) * np.exp(-t * 55) * vel


def snap(vel=0.4):
    t = tt(0.12)
    return bp(rng.normal(0, 1, len(t)), 1500, 7000) * np.exp(-t * 70) * vel


def chime(m, vel=0.5, dur=1.8):
    t = tt(dur)
    f = mtof(m)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
         + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10))
    return x * np.exp(-t * 2.6) * np.minimum(1, t / 0.002) * vel


def whoosh(dur=0.5, f0=300, f1=3500, vel=0.5, rev=False):
    t = tt(dur)
    n = rng.normal(0, 1, len(t))
    out = np.zeros_like(n)
    seg = 512
    for i in range(0, len(n), seg):
        u = i / len(n)
        if rev:
            u = 1 - u
        fc = f0 * (f1 / f0) ** u
        out[i:i + seg] = bp(n[max(0, i - 2048):i + seg], fc * 0.6, min(fc * 1.6, 20000))[-len(n[i:i + seg]):]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    if not rev:
        e = e * (t / dur) ** 0.4
    return out * e * vel


def riser(dur=0.85, vel=0.4):
    t = tt(dur)
    f = 300 * (12 ** (t / dur))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + whoosh(dur, 400, 9000, 1.0)[:len(t)]
    return x * (t / dur) ** 2 * vel


def boom(vel=0.8):
    t = tt(1.6)
    f = 38 + 70 * np.exp(-t * 9)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    nz = lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 7) * 0.4
    return (x + nz) * vel


def pop(vel=0.4, f=900):
    t = tt(0.12)
    fr = f * (1 + 1.5 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 38) * vel


def tick(vel=0.3):
    t = tt(0.03)
    return bp(rng.normal(0, 1, len(t)), 2500, 9000) * np.exp(-t * 300) * vel


def key_click(vel=0.18):
    t = tt(0.05)
    return (bp(rng.normal(0, 1, len(t)), 1800, 6000) * np.exp(-t * 180) + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90) * 0.4) * vel


def shimmer(dur=0.9, vel=0.3, base=84):
    out = np.zeros(int(dur * SR) + SR)
    for i in range(14):
        m = base + rng.choice([0, 2, 4, 7, 9, 12, 14, 16])
        c = chime(m, 0.25, 0.7)
        i0 = int(rng.uniform(0, dur) * SR)
        out[i0:i0 + len(c)] += c[:len(out) - i0]
    return out * vel


def bird(vel=0.12):
    t = tt(0.16)
    f = 3800 + 1600 * np.sin(np.pi * t / 0.16) + 300 * np.sin(2 * np.pi * 38 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.16) ** 2 * vel


# ------------------------------------------------------------------ score
BPM = 100.0
B = 60 / BPM          # 0.6 s
BAR = 4 * B           # 2.4 s
START = 0.84          # music downbeat on the coin hit
# D major: I vi IV V  (D, Bm, G, A)
CHORDS = [(50, [62, 66, 69, 74]), (47, [59, 62, 66, 71]), (43, [59, 62, 67, 71]), (45, [61, 64, 69, 73]),
          (50, [62, 66, 69, 74]), (47, [59, 62, 66, 71]), (43, [59, 62, 67, 71]), (45, [61, 64, 69, 76])]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]   # index into chord tones per eighth note

for bi, (root, tones) in enumerate(CHORDS):
    t0 = START + bi * BAR
    if t0 >= DUR:
        break
    night = 11.0 <= t0 < 14.1
    add(music, t0, pad(tones[:3], BAR + 0.6, vel=0.30 if not night else 0.38, bright=1200 if night else 1700))
    add(music, t0, bass(root, BAR, 0.32 if not night else 0.18))
    for e8 in range(8):
        te = t0 + e8 * B / 2
        if te >= DUR - 0.2:
            break
        m = tones[ARP[e8]] + (12 if e8 in (3, 7) and not night else 0)
        vel = 0.30 if e8 % 2 == 0 else 0.22
        if t0 < 2.7:
            vel *= 0.8
        add(music, te, piano(m, 0.9, vel), pan=-0.25 + 0.5 * (e8 % 2))
    # melody on top in the second half of each bar (simple, singable)
    mel = {0: [74, 76, 78], 1: [78, 76, 74], 2: [74, 71, 74], 3: [76, 73, 69]}[bi % 4]
    for j, m in enumerate(mel):
        add(music, t0 + 2 * B + j * B * 0.66, piano(m + 12, 1.4, 0.18 if not night else 0.22), pan=0.1)

# pulse: soft kick on beats + shaker offbeats (day), drops out at night, returns at the message
for i in range(int((DUR - START) / B) + 1):
    tb = START + i * B
    if tb >= 16.85:
        break
    if 11.0 <= tb < 14.15 or tb < 2.75:
        continue
    add(music, tb, kick(0.55 if i % 4 == 0 else 0.38))
    add(music, tb + B / 2, shaker(0.16), pan=0.3)
    if i % 2 == 1:
        add(music, tb, snap(0.12), pan=-0.1)

# big resolving chord for the end card
add(music, 16.85, pad([62, 66, 69, 74, 78], 2.3, vel=0.42, bright=2200))
add(music, 16.85, bass(38, 2.1, 0.4))
for j, m in enumerate([62, 66, 69, 74, 78, 81]):
    add(music, 16.9 + j * 0.06, piano(m, 2.0, 0.26), pan=-0.3 + j * 0.12)

music = reverb(music, wet=0.28, length=2.4, key='hall')

# ------------------------------------------------------------------ SFX
# hook montage: riser + ticks on each cut
add(sfx, 0.0, riser(0.86, 0.38))
for i in range(6):
    add(sfx, i * 0.14, snap(0.35), pan=(-1) ** i * 0.3)
    add(sfx, i * 0.14, tick(0.4))
# coin hit + shimmer
add(sfx, 0.84, boom(0.9))
add(sfx, 0.84, chime(86, 0.5, 2.2), pan=0.1)
add(sfx, 0.86, shimmer(0.8, 0.35, 86))
add(sfx, 1.35, pop(0.3, 700))                       # pill
for k in range(17):                                 # typing "Where does it go?"
    add(sfx, 1.75 + k / 24 + rng.uniform(-0.008, 0.008), key_click(0.16), pan=rng.uniform(-0.2, 0.2))
add(sfx, 2.28, whoosh(0.5, 400, 7000, 0.45))        # orbs burst out
add(sfx, 2.28, shimmer(0.4, 0.25, 91))
add(sfx, 2.72, boom(0.55))
# bedroom: morning birds + word swishes
for tb in [2.95, 3.4, 3.9, 4.3, 5.4, 5.9, 6.6, 7.3, 7.9]:
    for j in range(rng.integers(2, 4)):
        add(sfx, tb + j * 0.11, bird(0.07), pan=rng.uniform(-0.7, 0.7))
for tl in (3.0, 3.45, 3.75):
    add(sfx, tl, whoosh(0.35, 800, 5000, 0.12), pan=0.0)
add(sfx, 4.15, shimmer(0.4, 0.18, 93))
# transitions
for tw, d, v in [(4.93, 0.3, 0.55), (5.98, 0.25, 0.45), (7.13, 0.25, 0.45), (8.3, 0.35, 0.35), (10.85, 0.4, 0.3),
                 (13.92, 0.45, 0.55), (16.68, 0.35, 0.45)]:
    add(sfx, tw, whoosh(d, 250, 6000, v))
# orbs: swish in + chime on landing; tag pop + check tick
for (ts, tl, m) in [(5.25, 5.85, 81), (6.12, 6.5, 83), (7.27, 7.62, 86), (8.5, 8.85, 88)]:
    add(sfx, ts, whoosh(tl - ts + 0.1, 900, 8000, 0.25), pan=-0.4)
    add(sfx, ts, shimmer(tl - ts, 0.15, m))
    add(sfx, tl, chime(m, 0.42, 1.6), pan=0.2)
    add(sfx, tl, chime(m + 7, 0.2, 1.2), pan=-0.2)
for tg in (6.5, 7.62, 8.9):
    add(sfx, tg, pop(0.35, 820))
    add(sfx, tg + 0.28, pop(0.22, 1500))
    add(sfx, tg + 0.3, tick(0.25))
# clock pill ticks on time change
for tc in (5.15, 6.15, 7.3, 8.5):
    for j in range(3):
        add(sfx, tc + j * 0.045, tick(0.28))
add(sfx, 11.05, shimmer(0.5, 0.15, 79))
for j in range(8):
    add(sfx, 10.95 + j * 0.04, tick(0.2))
# kitchen heart pop
add(sfx, 9.6, pop(0.3, 600))
# night: chat typing dots + message pop + heart
for j in range(4):
    add(sfx, 12.95 + j * 0.12, key_click(0.08))
add(sfx, 13.4, pop(0.38, 1000))
add(sfx, 13.42, chime(88, 0.22, 1.0))
add(sfx, 13.95, pop(0.3, 650))
# message: 3D 'extraordinary' impact + shimmer, 'change.' sparkle
add(sfx, 14.15, boom(0.6))
add(sfx, 15.05, boom(0.7))
add(sfx, 15.05, shimmer(0.7, 0.3, 86))
add(sfx, 15.55, whoosh(0.6, 2000, 12000, 0.12))
add(sfx, 15.45, chime(81, 0.3, 1.6))
# logo reveal
add(sfx, 16.95, chime(74, 0.4, 2.0))
add(sfx, 16.95, chime(81, 0.3, 2.0))
add(sfx, 17.0, shimmer(0.8, 0.22, 86))
add(sfx, 17.7, pop(0.25, 760))

sfx = reverb(sfx, wet=0.18, length=1.4, key='room')

mix = music * 0.85 + sfx * 0.9
# gentle bus glue: soft clip
mix = np.tanh(mix * 1.1) / 1.1
fade = np.ones(N)
fade[-int(0.35 * SR):] = np.linspace(1, 0, int(0.35 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{S}/audio', exist_ok=True)
wavfile.write(f'{S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{S}/audio/mix_raw.wav')
