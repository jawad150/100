"""Procedural score + SFX for the reel (48 kHz stereo WAV)."""
import numpy as np, subprocess, sys
from scipy import signal

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
SR = 48000
DUR = 32.0
N = int(SR * DUR)
rng = np.random.default_rng(5)

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))

def at(t):
    return int(t * SR)

def add(buf, t0, x, gain=1.0, pan=0.0):
    i = at(t0)
    if x.ndim == 1:
        l = np.sqrt(0.5 * (1 - pan)); r = np.sqrt(0.5 * (1 + pan))
        x = np.stack([x * l * 1.414, x * r * 1.414], 1)
    if i < 0:
        x = x[-i:]; i = 0
    n = min(len(x), N - i)
    if n > 0:
        buf[i:i + n] += x[:n] * gain

def tt(d):
    return np.arange(int(d * SR)) / SR

def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x, axis=0)

def hp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'high')
    return signal.lfilter(b, a, x, axis=0)

def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], 'band')
    return signal.lfilter(b, a, x, axis=0)

def sweep_bp(x, f0, f1, q=1.4, block=256, curve=1.0):
    """Time-varying band-pass (state-variable filter) sweeping f0->f1."""
    n = len(x)
    out = np.zeros(n)
    low = band = 0.0
    fs = np.linspace(0, 1, n) ** curve
    freqs = f0 * (f1 / f0) ** fs
    damp = 1.0 / q
    for i in range(0, n, block):
        f = 2 * np.sin(np.pi * min(freqs[i], SR / 6) / SR)
        seg = x[i:i + block]
        o = np.empty_like(seg)
        for k, v in enumerate(seg):
            low += f * band
            high = v - low - damp * band
            band += f * high
            o[k] = band
        out[i:i + block] = o
    return out

_ir = None
def reverb(x, wet=0.3, length=1.8):
    global _ir
    if _ir is None:
        n = int(length * SR)
        e = np.exp(-np.linspace(0, 7, n))
        irl = rng.normal(0, 1, n) * e
        irr = rng.normal(0, 1, n) * e
        irl = lp(irl, 6000); irr = lp(irr, 6000)
        _ir = np.stack([irl, irr], 1) / np.sqrt(np.sum(e ** 2)) * 0.5
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([signal.fftconvolve(x[:, 0], _ir[:, 0]), signal.fftconvolve(x[:, 1], _ir[:, 1])], 1)
    out = np.zeros_like(y)
    out[:len(x)] = x * (1 - wet)
    return out + y * wet

# ------------------------------------------------------------------ SFX

def impact(t0, size=1.0):
    d = 2.2
    t = tt(d)
    f = 38 + 90 * np.exp(-t * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 2.2) * 0.9
    nz = lp(rng.normal(0, 1, len(t)), 1800) * np.exp(-t * 14) * 0.5
    crack = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 40) * 0.25
    x = (sub + nz + crack) * size
    add(sfx, t0, reverb(x, 0.3, 1.8), 0.9)

def boom(t0, size=1.0):
    t = tt(3.0)
    f = 32 + 40 * np.exp(-t * 4)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.2)
    x += lp(rng.normal(0, 1, len(t)), 400) * np.exp(-t * 3) * 0.4
    add(sfx, t0, reverb(x * size, 0.25), 0.9)

def whoosh(t0, dur=0.5, f0=250, f1=3500, gain=0.5, pan0=-0.6, pan1=0.6, peak=0.65):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    y = sweep_bp(x, f0, f1, q=1.2)
    p = np.linspace(0, 1, n)
    env = np.where(p < peak, (p / peak) ** 2, ((1 - p) / (1 - peak)) ** 1.5)
    y = y * env
    pans = np.linspace(pan0, pan1, n)
    st = np.stack([y * np.sqrt(0.5 * (1 - pans)), y * np.sqrt(0.5 * (1 + pans))], 1) * 1.4
    add(sfx, t0, reverb(st, 0.2), gain / (np.abs(y).max() + 1e-9))

def tick(t0, gain=0.25, f=3200):
    t = tt(0.08)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + hp(rng.normal(0, 1, len(t)), 5000) * np.exp(-t * 200) * 0.4
    add(sfx, t0, reverb(x, 0.15), gain, pan=rng.uniform(-0.3, 0.3))

def click(t0, gain=0.45):
    t = tt(0.05)
    a = bp(rng.normal(0, 1, len(t)), 1500, 7000) * np.exp(-t * 400)
    b = np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 250) * 0.6
    add(sfx, t0, reverb(a + b, 0.1), gain)
    add(sfx, t0 + 0.07, reverb(a * 0.6, 0.1), gain * 0.7)

def pop(t0, gain=0.35, f0=280, f1=950, pan=0.0):
    t = tt(0.22)
    f = f0 + (f1 - f0) * (1 - np.exp(-t * 45))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * np.clip(t * 400, 0, 1)
    add(sfx, t0, reverb(x, 0.2), gain, pan=pan)

def shimmer(t0, dur=1.6, gain=0.18):
    t = tt(dur)
    x = np.zeros(len(t))
    for k in range(14):
        f = rng.uniform(2200, 7500)
        x += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(4, 11) * t))
    x *= np.exp(-t * 2.2) * np.clip(t * 30, 0, 1) / 14
    add(sfx, t0, reverb(x, 0.5, 2.2), gain)

def riser(t0, t1, gain=0.45):
    d = t1 - t0
    n = int(d * SR)
    p = np.linspace(0, 1, n)
    nz = sweep_bp(rng.normal(0, 1, n), 200, 7000, q=1.5, curve=2.0)
    nz = nz / (np.abs(nz).max() + 1e-9)
    f = 90 * (8 ** (p ** 1.6))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.2
    x = (nz * 0.8 + tone) * (p ** 2.2)
    add(sfx, t0, np.stack([x, np.roll(x, 240)], 1), gain)

def rev_swell(t1, d=0.9, gain=0.35):
    n = int(d * SR)
    p = np.linspace(0, 1, n)
    x = hp(rng.normal(0, 1, n), 3000) * p ** 3
    add(sfx, t1 - d, np.stack([x, np.roll(x, 120)], 1), gain)

# ------------------------------------------------------------------ music

BPM = 120
BEAT = 60 / BPM

def kick(t0, gain=0.8):
    t = tt(0.45)
    f = 48 + 110 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    x += hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 300) * 0.15
    add(music, t0, x, gain)

def hat(t0, gain=0.12, open_=False):
    t = tt(0.12 if open_ else 0.05)
    x = hp(rng.normal(0, 1, len(t)), 7500) * np.exp(-t * (30 if open_ else 110))
    add(music, t0, x, gain, pan=0.25)

def saw(f, t, detune=0.0):
    ph = (f * (1 + detune) * t) % 1.0
    return 2 * ph - 1

NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)

def pad(t0, t1, notes, gain=0.12, cutoff=1400, attack=0.6, release=0.8):
    d = t1 - t0 + release
    t = tt(d)
    x = np.zeros((len(t), 2))
    for n in notes:
        f = NOTE(n)
        for k, dt in enumerate([-0.011, -0.004, 0.0, 0.005, 0.012]):
            v = saw(f, t + rng.uniform(0, 1), dt)
            pan = (k - 2) / 2.5
            x[:, 0] += v * np.sqrt(0.5 * (1 - pan))
            x[:, 1] += v * np.sqrt(0.5 * (1 + pan))
    x = lp(x, cutoff, 2) / (len(notes) * 5)
    env = np.clip(t / attack, 0, 1) * np.clip((t1 - t0 + release - t) / release, 0, 1)
    add(music, t0, x * env[:, None], gain)

def bass(t0, dur, note, gain=0.3, cutoff=420):
    t = tt(dur + 0.05)
    f = NOTE(note)
    x = saw(f, t) * 0.6 + np.sin(2 * np.pi * f * t) * 0.7
    x = lp(x, cutoff, 2)
    env = np.clip(t / 0.01, 0, 1) * np.clip((dur + 0.05 - t) / 0.05, 0, 1) * (0.7 + 0.3 * np.exp(-t * 6))
    add(music, t0, x * env, gain)

def pluck(t0, note, gain=0.08, pan=0.0):
    t = tt(0.5)
    f = NOTE(note)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * saw(f, t)) * np.exp(-t * 9)
    x = lp(x, 5000)
    add(music, t0, reverb(x, 0.35), gain, pan=pan)

# chord progression (A minor): Am - F - C - G ; each chord 2 beats... use 1 bar (4 beats = 2 s)
PROG = [(57, [57, 60, 64], 33), (53, [53, 57, 60], 29), (48, [55, 60, 64], 36), (55, [55, 59, 62], 31)]

def build():
    # ---------- HOOK 0 - 6.8 : tension pad + half-time pulse
    for bar in range(4):
        t0 = bar * 2.0
        if t0 >= 6.8:
            break
        root, ch, bn = PROG[bar % 4]
        pad(t0, min(t0 + 2.0, 6.75), ch, gain=0.5, cutoff=1100 + bar * 300, attack=0.3 if bar else 0.05)
        for k in range(4):
            tb = t0 + k * BEAT
            if tb < 6.6:
                bass(tb, BEAT * 0.9, bn, gain=0.55, cutoff=260 + 60 * bar)
        for k in range(2):
            tb = t0 + k * 1.0
            if tb < 6.6:
                kick(tb, 0.65)
        for k in range(8):
            tb = t0 + k * 0.25 + 0.125
            if 0.5 < tb < 6.6:
                hat(tb, 0.05)
    # ---------- STEPS 8.6 - 21.4 : driving groove
    t = 8.6
    bar = 0
    while t < 21.4 - 1e-6:
        root, ch, bn = PROG[bar % 4]
        pad(t, min(t + 2.0, 21.4), ch, gain=0.3, cutoff=1600, attack=0.2, release=0.4)
        for k in range(4):
            tb = t + k * BEAT
            if tb < 21.0:
                kick(tb, 0.75)
                bass(tb, BEAT * 0.45, bn, 0.5, 520)
                bass(tb + BEAT / 2, BEAT * 0.4, bn + 12 if k % 2 else bn, 0.35, 520)
            if tb + BEAT / 2 < 21.0:
                hat(tb + BEAT / 2, 0.1, open_=(k == 3))
            if tb + BEAT / 4 < 21.0:
                hat(tb + BEAT / 4, 0.04)
                hat(tb + 3 * BEAT / 4, 0.04)
        t += 2.0
        bar += 1
    # ---------- PAYOFF 21.58 - 25.9
    pad(21.58, 23.6, [57, 60, 64, 69], gain=0.6, cutoff=2600, attack=0.02, release=0.6)
    pad(23.58, 25.9, [53, 57, 60, 65], gain=0.55, cutoff=2400, attack=0.3, release=0.4)
    bass(21.58, 2.0, 33, 0.7, 300)
    bass(23.58, 2.3, 29, 0.7, 300)
    for tb in np.arange(21.58, 25.8, 1.0):
        kick(tb, 0.7)
    for tb in np.arange(21.83, 25.8, 0.5):
        hat(tb, 0.07)
    # ---------- OUTRO 25.95 - 30
    pad(25.95, 30.0, [48, 55, 60, 64, 67], gain=0.55, cutoff=2200, attack=0.05, release=0.3)
    bass(25.95, 3.9, 36, 0.6, 300)
    arp = [72, 76, 79, 84, 79, 76]
    k = 0
    for tb in np.arange(26.45, 29.7, 0.125):
        pluck(tb, arp[k % len(arp)], 0.09, pan=0.4 * np.sin(k))
        k += 1
    for tb in np.arange(26.95, 29.6, 1.0):
        kick(tb, 0.55)

    # ---------------- SFX timeline
    impact(0.02, 0.9); whoosh(0.0, 0.7, 180, 3000, 0.45)
    for k, tw in enumerate([0.42, 0.49, 0.56, 0.62, 0.69, 0.76]):
        tick(tw, 0.12, 2600 + k * 150)
    pop(0.85, 0.3, 350, 1100)
    pop(1.1, 0.3, 260, 850, pan=0.5); pop(1.2, 0.28, 300, 900, pan=-0.5); pop(1.35, 0.25, 320, 1000, pan=0.4)
    shimmer(1.4, 1.2, 0.12); whoosh(1.3, 0.35, 800, 5000, 0.15)
    whoosh(2.72, 0.4, 3500, 300, 0.4, 0.5, -0.5, peak=0.45); impact(2.9, 0.35)
    # exit + HERE'S HOW
    rev_swell(6.85, 0.8, 0.3); whoosh(6.45, 0.45, 300, 5000, 0.5)
    impact(6.85, 0.9)
    for k in range(6):
        tick(6.78 + k * 0.04, 0.16, 2000 + k * 200)
    for k in range(3):
        boom(7.06 + k * 0.07, 0.35 + 0.15 * k)
    boom(7.2, 0.8)
    for k, tp in enumerate([7.05, 7.15, 7.25, 7.35]):
        pop(tp, 0.28, 250 + 40 * k, 900 + 60 * k, pan=[-0.6, 0.6, -0.5, 0.5][k])
    whoosh(7.45, 0.35, 1000, 4000, 0.15)
    whoosh(8.35, 0.5, 200, 4500, 0.55); impact(8.62, 0.6)
    # step transitions
    for b in [11.4, 14.8, 19.2]:
        whoosh(b - 0.25, 0.45, 3500, 400, 0.4, -0.7, 0.7, peak=0.5)
        tick(b + 0.05, 0.12, 2400)
    for b in [8.6, 11.4, 14.8, 19.2]:
        for k in range(3):
            tick(b + 0.05 + k * 0.07, 0.08, 3000 + 300 * k)
    # clicks (keep in sync with reel.CLICKS)
    for tc in [11.4 + (22.85 - 19.55) / 1.12, 14.8 + 1.3, 17.95 + 0.14, 19.3, 20.7, 21.45]:
        click(tc, 0.5)
    for tp in [8.95, 11.75, 15.15, 19.55]:
        pop(tp, 0.22, 300, 950)
    # clone sequence
    whoosh(16.1, 0.5, 300, 3000, 0.35); pop(16.45, 0.2, 400, 1200)
    whoosh(16.9, 0.45, 600, 6000, 0.35, -0.8, 0.8); shimmer(16.95, 1.0, 0.16)
    whoosh(17.5, 0.5, 5000, 400, 0.4, 0.6, -0.6, peak=0.8); pop(17.97, 0.3, 500, 1500)
    # build + drop
    riser(19.6, 21.45, 0.5); rev_swell(21.58, 1.2, 0.35)
    impact(21.58, 1.2); boom(21.58, 1.0); shimmer(21.62, 1.6, 0.14)
    pop(22.05, 0.25, 300, 1000); pop(22.3, 0.22, 280, 900, pan=-0.5); pop(22.5, 0.22, 300, 950, pan=0.5)
    for k in range(5):
        tick(21.8 + k * 0.07, 0.1, 2500 + 150 * k)
    # wall
    whoosh(24.1, 0.9, 200, 2500, 0.55, 0.0, 0.0, peak=0.4); boom(24.2, 0.5)
    for k in range(4):
        tick(24.55 + k * 0.06, 0.1, 2800)
    whoosh(25.7, 0.35, 4000, 300, 0.35)
    # outro
    rev_swell(25.97, 0.7, 0.3); impact(25.97, 1.0); shimmer(26.0, 2.2, 0.2)
    for k, tp in enumerate([27.0, 27.1, 27.2, 27.3]):
        pop(tp, 0.25, 280 + 30 * k, 950 + 50 * k, pan=[-0.6, 0.6, -0.5, 0.5][k])
    for k in range(7):
        tick(27.45 + k * 0.07, 0.08, 2600 + 120 * k)
    pop(28.0, 0.3, 250, 800)

def load_original():
    """Original scene audio from the Genjutsu result (used as texture under hook/payoff)."""
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', S + '/src/result_split.mp4', '-vn', '-ac', '2',
                          '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def place_original(orig):
    out = np.zeros((N, 2))
    # (out_t0, out_t1, src_t0)
    for a, b, s0 in [(0.0, 2.9, 0.2), (2.9, 6.8, 21.0), (21.58, 24.2, 0.25)]:
        i0, i1 = at(a), at(b)
        s = at(s0)
        seg = orig[s:s + (i1 - i0)]
        n = len(seg)
        fade = np.ones(n)
        f = int(0.04 * SR)
        fade[:f] = np.linspace(0, 1, f); fade[-f:] = np.linspace(1, 0, f)
        out[i0:i0 + n] += seg * fade[:, None]
    return out

VO_LINES = [(0.35, 0), (3.7, 1), (6.95, 2), (8.85, 3), (11.65, 4), (14.95, 5), (19.3, 6), (22.25, 7),
            (24.5, 8), (29.5, 9)]

def load_vo(i):
    import wave
    w = wave.open(f'{S}/tts/vo_{i}.wav')
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    x = signal.resample_poly(x, SR, w.getframerate())
    # voice polish: low cut, presence lift, gentle compression, short room
    x = hp(x, 90)
    x = x + 0.35 * bp(x, 2500, 6000)
    env = np.abs(signal.hilbert(x))
    env = lp(env, 12)
    g = np.where(env > 0.12, (0.12 / (env + 1e-9)) ** 0.5, 1.0)
    x = x * g
    x = x / (np.abs(x).max() + 1e-9)
    return reverb(x, 0.08, 0.6)

def ending_sfx():
    whoosh(28.2, 0.9, 200, 3000, 0.5, 0.0, 0.0, peak=0.7)
    impact(29.12, 0.7); shimmer(29.15, 1.8, 0.16)
    whoosh(29.3, 0.6, 600, 4000, 0.25, -0.6, 0.2)
    for k in range(4):
        tick(29.7 + k * 0.08, 0.1, 2600 + 150 * k)
    pop(30.2, 0.35, 260, 900)
    for k, tp in enumerate([30.1, 30.2, 30.3, 30.4]):
        pop(tp, 0.2, 280 + 30 * k, 950 + 50 * k, pan=[-0.6, 0.6, -0.5, 0.5][k])

if __name__ == '__main__':
    build()
    ending_sfx()
    vo = np.zeros((N, 2))
    for t0, i in VO_LINES:
        add(vo, t0, load_vo(i), 1.0)
    # duck SFX under the voice
    venv = lp(np.abs(vo[:, 0]), 6)
    venv = venv / (venv.max() + 1e-9)
    duck = 1 - 0.55 * np.clip(venv * 4, 0, 1)
    mix = sfx * 0.6 * duck[:, None] + vo * 0.9
    fo = at(31.6)
    mix[fo:] *= np.linspace(1, 0, N - fo)[:, None] ** 1.5
    mix = hp(mix, 25)
    rms = np.sqrt(np.mean(mix ** 2))
    mix *= 10 ** (-16 / 20) / (rms + 1e-9)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix *= 0.93 / np.abs(mix).max()
    import wave
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(S + '/out/audio.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('audio written', mix.shape, 'rms dB', 20 * np.log10(np.sqrt(np.mean(mix ** 2))))
