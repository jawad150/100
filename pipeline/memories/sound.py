"""Sound design for the Yaadein reel: the original voice+music track (extended under the end card by
looping its last bar), plus synthesized cinematic SFX: braams, sub drops, impacts, whooshes, glass
shatter, thunder, rain bed, fire crackle, heartbeat, glitch zaps, web 'thwip', UI clicks, risers.

python3 sound.py  -> workspace2/out/audio.wav (48 kHz stereo) and workspace2/out/sfx_stem.wav
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'workspace2'))
SR = 48000
rng = np.random.default_rng(5)


class Bus:
    def __init__(self, dur):
        self.N = int(SR * dur)
        self.x = np.zeros((self.N, 2))

    def add(self, t0, x, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if x.ndim == 1:
            l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
            x = np.stack([x * l * 1.414, x * r * 1.414], 1)
        if i < 0:
            x, i = x[-i:], 0
        n = min(len(x), self.N - i)
        if n > 0:
            self.x[i:i + n] += x[:n] * gain


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


def bandsweep(x, f0, f1, curve=1.0, q=1.3, blocks=64):
    """Band-pass sweep f0 -> f1 by filtering short overlapping blocks (fast, smooth)."""
    n = len(x)
    out = np.zeros(n)
    win = np.hanning(2 * (n // blocks) + 2)
    hop = n // blocks
    for k in range(blocks + 1):
        i0 = max(0, k * hop - hop)
        seg = x[i0:i0 + 2 * hop]
        if len(seg) < 16:
            continue
        p = min(1.0, k / blocks) ** curve
        f = f0 * (f1 / f0) ** p
        lo, hi = f / (1 + 1 / q), f * (1 + 1 / q)
        y = bp(seg, max(20, lo), min(hi, SR / 2.2))
        out[i0:i0 + len(y)] += y * win[:len(y)]
    return out


_ir = {}


def reverb(x, wet=0.3, length=1.8, tone=6000):
    key = (length, tone)
    if key not in _ir:
        n = int(length * SR)
        e = np.exp(-np.linspace(0, 7, n))
        irl, irr = lp(rng.normal(0, 1, n) * e, tone), lp(rng.normal(0, 1, n) * e, tone)
        _ir[key] = np.stack([irl, irr], 1) / np.sqrt(np.sum(e ** 2)) * 0.5
    ir = _ir[key]
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([signal.fftconvolve(x[:, 0], ir[:, 0]), signal.fftconvolve(x[:, 1], ir[:, 1])], 1)
    out = np.zeros_like(y)
    out[:len(x)] = x * (1 - wet)
    return out + y * wet


def norm(x, peak=1.0):
    return x / (np.abs(x).max() + 1e-9) * peak


# ------------------------------------------------------------------ voices (each returns stereo/mono array)
def braam(d=2.6):
    """Big cinematic brass hit (detuned saws through a closing low-pass + sub)."""
    t = tt(d)
    f0 = 55.0
    x = np.zeros(len(t))
    for det in (-0.6, -0.25, 0, 0.3, 0.7):
        ph = 2 * np.pi * f0 * (1 + det / 100) * t
        x += signal.sawtooth(ph) + 0.5 * signal.sawtooth(ph * 2.0)
    env = np.clip(t / 0.03, 0, 1) * np.exp(-t * 0.9)
    cut = 1800 * np.exp(-t * 1.6) + 220
    y = np.zeros_like(x)
    blk = 2048
    for i in range(0, len(x), blk):
        y[i:i + blk] = lp(x[i:i + blk], cut[i], 2)
    sub = np.sin(2 * np.pi * 41 * t) * np.exp(-t * 1.1)
    return reverb(norm(y * env) * 0.8 + sub * 0.7, 0.35, 2.6, 3500)


def sub_drop(d=2.0):
    t = tt(d)
    f = 30 + 70 * np.exp(-t * 3)
    return reverb(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5) * np.clip(t / 0.01, 0, 1), 0.2)


def impact(d=2.2):
    t = tt(d)
    f = 38 + 90 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 0.9
    nz = lp(rng.normal(0, 1, len(t)), 1800) * np.exp(-t * 14) * 0.5
    crack = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 40) * 0.25
    return reverb(sub + nz + crack, 0.3, 1.8)


def whoosh(d=0.6, f0=200, f1=4200, sweep=(-0.7, 0.7), peak=0.6):
    n = int(d * SR)
    y = bandsweep(rng.normal(0, 1, n), f0, f1, curve=1.2)
    p = np.linspace(0, 1, n)
    env = np.where(p < peak, (p / peak) ** 2, ((1 - p) / (1 - peak)) ** 1.5)
    y = norm(y * env)
    pp = sweep[0] + (sweep[1] - sweep[0]) * p
    return np.stack([y * np.sqrt(0.5 * (1 - pp)) * 1.4, y * np.sqrt(0.5 * (1 + pp)) * 1.4], 1)


def whoosh_slow(d=1.6):
    return reverb(whoosh(d, 120, 2400, (0.5, -0.5), 0.75), 0.35, 2.0)


def reverse_swell(d=1.8):
    """Reversed reverb cymbal swell into a hit."""
    t = tt(d)
    nz = hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 3.2)
    x = reverb(nz, 0.7, 2.0, 9000)[:len(t)][::-1]
    return norm(x) * (np.linspace(0, 1, len(t)) ** 1.5)[:, None]


def riser(d=2.4):
    n = int(d * SR)
    p = np.linspace(0, 1, n)
    nz = norm(bandsweep(rng.normal(0, 1, n), 200, 7000, curve=2.0))
    f = 90 * (8 ** (p ** 1.6))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.2
    x = (nz * 0.8 + tone) * (p ** 2.2)
    return np.stack([x, np.roll(x, 240)], 1)


def glass(d=2.4):
    """Glass shatter: dense bright transients + ringing partials + debris tail."""
    t = tt(d)
    x = hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 18) * 0.6
    for k in range(60):
        t0 = abs(rng.normal(0, 0.12)) + (0 if k < 10 else rng.uniform(0, 0.9))
        i = int(t0 * SR)
        if i >= len(t):
            continue
        f = rng.uniform(2500, 9500)
        dd = tt(rng.uniform(0.05, 0.4))
        p = np.sin(2 * np.pi * f * dd) * np.exp(-dd * rng.uniform(10, 40)) * rng.uniform(0.1, 0.5)
        x[i:i + len(p)] += p[:len(t) - i]
    x += np.sin(2 * np.pi * 70 * t) * np.exp(-t * 8) * 0.5
    return reverb(norm(x), 0.3, 1.6, 9000)


def thunder(d=4.5):
    t = tt(d)
    crack = hp(rng.normal(0, 1, len(t)), 1500) * np.exp(-t * 9) * 0.6
    roll = lp(rng.normal(0, 1, len(t)), 220) * (np.exp(-t * 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.7 * t) ** 2))
    return reverb(norm(crack + roll * 3), 0.4, 3.0, 2500)


def rain_bed(d):
    n = int(d * SR)
    x = np.stack([bp(rng.normal(0, 1, n), 800, 9000), bp(rng.normal(0, 1, n), 800, 9000)], 1)
    drops = np.zeros((n, 2))
    for _ in range(int(d * 90)):
        i = rng.integers(0, n - 2000)
        dd = tt(0.01)
        drops[i:i + len(dd), rng.integers(0, 2)] += np.sin(2 * np.pi * rng.uniform(2000, 6000) * dd) * np.exp(-dd * 500) * rng.uniform(0.2, 1)
    return norm(x * 0.6 + drops * 0.5) * 0.5


def fire(d=4.0):
    n = int(d * SR)
    x = lp(rng.normal(0, 1, n), 900) * 0.35
    for _ in range(int(d * 40)):
        i = rng.integers(0, n - 4000)
        dd = tt(rng.uniform(0.003, 0.02))
        x[i:i + len(dd)] += hp(rng.normal(0, 1, len(dd)), 2000) * np.exp(-dd * 300) * rng.uniform(0.3, 1.2)
    env = np.clip(np.linspace(0, 1, n) * 4, 0, 1) * np.clip((1 - np.linspace(0, 1, n)) * 3, 0, 1)
    return reverb(x * env, 0.2, 1.2)


def heartbeat(n=3, bpm=58):
    out = np.zeros(int(SR * (60 / bpm * n + 1)))
    for k in range(n):
        for off, g in ((0.0, 1.0), (0.28, 0.7)):
            t = tt(0.35)
            b = np.sin(2 * np.pi * (48 + 30 * np.exp(-t * 25)) * t) * np.exp(-t * 14) * g
            i = int((k * 60 / bpm + off) * SR)
            out[i:i + len(b)] += b
    return reverb(out, 0.2, 1.0, 1200)


def glitch(d=0.45):
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * rng.uniform(80, 400) * t)) * 0.3
    chop = (np.floor(t * 40) % 2).astype(float)
    x = x * chop + hp(rng.normal(0, 1, len(t)), 4000) * 0.2 * (1 - chop)
    x *= np.exp(-t * 3)
    return np.stack([x, np.roll(x, 300)], 1)


def thwip():
    """Web-shooter 'thwip': fast downward chirp + air."""
    t = tt(0.22)
    f = 2600 * np.exp(-t * 22) + 300
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * 0.6 + hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 30) * 0.4
    return reverb(x, 0.15, 0.8)


def click():
    t = tt(0.06)
    return hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 160) * 0.6 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120) * 0.3


def pop():
    t = tt(0.16)
    f = 280 + 700 * (1 - np.exp(-t * 30))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * 0.7


def tick(f=3200):
    t = tt(0.03)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 300) * 0.5


def ticks(n=10, gap=0.045):
    out = np.zeros(int(SR * (n * gap + 0.1)))
    for k in range(n):
        x = tick(2800 + 40 * k)
        i = int(k * gap * SR)
        out[i:i + len(x)] += x
    return out


def shimmer(d=1.8):
    t = tt(d)
    x = np.zeros(len(t))
    for k in range(14):
        x += np.sin(2 * np.pi * rng.uniform(2200, 7500) * t + rng.uniform(0, 6)) * \
            (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(4, 11) * t))
    x *= np.exp(-t * 2.2) * np.clip(t * 30, 0, 1) / 14
    return reverb(x, 0.5, 2.2)


def tape_stop(src, d=0.6):
    """Pitch-down slowdown of a stereo snippet."""
    n = int(d * SR)
    p = np.linspace(0, 1, n)
    speed = (1 - p) ** 1.5
    pos = np.cumsum(speed)
    pos = np.clip(pos, 0, len(src) - 2)
    i = pos.astype(int)
    fr = (pos - i)[:, None]
    return (src[i] * (1 - fr) + src[i + 1] * fr) * (1 - p[:, None] ** 3)


def chimes(d=4.0, n=9):
    """Soft wind chimes (pentatonic metal tones with long decays)."""
    t = tt(d)
    x = np.zeros(len(t))
    notes = [1046.5, 1174.7, 1318.5, 1568.0, 1760.0, 2093.0]
    for k in range(n):
        t0 = rng.uniform(0, d * 0.75)
        i = int(t0 * SR)
        f = notes[rng.integers(0, len(notes))]
        dd = tt(min(2.2, d - t0))
        tone = (np.sin(2 * np.pi * f * dd) + 0.4 * np.sin(2 * np.pi * f * 2.76 * dd) + 0.2 * np.sin(2 * np.pi * f * 5.4 * dd))
        tone *= np.exp(-dd * 2.2) * rng.uniform(0.25, 0.7)
        x[i:i + len(tone)] += tone[:len(x) - i]
    return reverb(x * 0.3, 0.45, 2.4, 8000)


def wind(d=5.0):
    n = int(d * SR)
    x = np.stack([lp(rng.normal(0, 1, n), 700), lp(rng.normal(0, 1, n), 700)], 1)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * np.linspace(0, d, n) * 0.23 + 1.0) * np.sin(2 * np.pi * np.linspace(0, d, n) * 0.07)
    env = np.clip(np.linspace(0, 1, n) * 3, 0, 1) * np.clip((1 - np.linspace(0, 1, n)) * 3, 0, 1)
    return norm(x * (mod * env)[:, None]) * 0.6


def blade(d=1.4):
    """Metallic 'shing': inharmonic ringing partials + a bright scrape."""
    t = tt(d)
    x = np.zeros(len(t))
    for f, a in ((2310, 1.0), (3570, 0.6), (5120, 0.4), (6890, 0.25), (1460, 0.35)):
        x += np.sin(2 * np.pi * f * t * (1 + 0.002 * np.sin(2 * np.pi * 5 * t))) * a * np.exp(-t * 2.5)
    scrape = hp(rng.normal(0, 1, len(t)), 4000) * np.exp(-t * 9) * np.clip(t / 0.03, 0, 1)
    return reverb(norm(x) * 0.6 + scrape * 0.5, 0.35, 1.8, 10000)


def tinnitus(d=1.8, f=3600):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6) * np.clip(t / 0.05, 0, 1) * 0.35


def buzz(d=0.45):
    t = tt(d)
    x = signal.square(2 * np.pi * 110 * t) * 0.5 + signal.square(2 * np.pi * 116 * t) * 0.5
    return lp(x, 1800) * np.exp(-t * 3) * np.clip(t / 0.01, 0, 1) * 0.6


def rope(d=1.2, n=3):
    out = np.zeros((int(d * SR) + SR, 2))
    for k in range(n):
        w = whoosh(0.35, 300, 2600, (-0.6 + 1.2 * (k % 2), 0.6 - 1.2 * (k % 2)), 0.55)
        i = int(k * d / n * SR)
        out[i:i + len(w)] += w
    return out


VOICES = dict(chimes=chimes, wind=wind, blade=blade, tinnitus=tinnitus, buzz=buzz, rope=rope, braam=braam, sub_drop=sub_drop, impact=impact, whoosh=whoosh, whoosh_slow=whoosh_slow,
              reverse_swell=reverse_swell, riser=riser, glass=glass, thunder=thunder, fire=fire,
              heartbeat=heartbeat, glitch=glitch, thwip=thwip, click=click, pop=pop, ticks=ticks, shimmer=shimmer)


# ------------------------------------------------------------------ music
def source_track():
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', ROOT + '/src/audio_src.mp4', '-vn', '-ac', '2', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def bar_length(x, lo=3.15, hi=3.45, ref=(24.4, 27.7)):
    """Find the bar period by correlating the onset envelope with itself one bar earlier."""
    m = x.mean(1)
    f, t, S = signal.stft(m, SR, nperseg=2048, noverlap=2048 - 480)
    flux = np.maximum(np.diff(np.log1p(np.abs(S) * 50), axis=1), 0).sum(0)
    fps = SR / 480
    a0, a1 = int(ref[0] * fps), int(ref[1] * fps)
    best, bl = -1, 3.3
    for L in np.arange(lo, hi, 1 / fps):
        k = int(round(L * fps))
        c = np.corrcoef(flux[a0:a1], flux[a0 - k:a1 - k])[0, 1]
        if c > best:
            best, bl = c, k / fps
    return bl, best


def _spec(x):
    m = x.mean(1)
    f, t, S = signal.stft(m, SR, nperseg=4096, noverlap=4096 - 960)
    S = np.log1p(np.abs(S[:400]) * 30)
    return S, SR / 960


def best_continuation(x, t_end, lo=23.0, hi=None, win=1.2):
    """Earlier time p whose preceding `win` s sound most like the `win` s before t_end (spectral cosine)."""
    S, fps = _spec(x)
    hi = hi or (t_end - 1.0)
    ref = S[:, int((t_end - win) * fps):int(t_end * fps)]
    best, bp = -1, lo
    beat = 0.8245                                   # tempo of the track (onset autocorrelation)
    cands = [q for k in range(3, 9) for q in np.arange(t_end - k * beat - 0.06, t_end - k * beat + 0.06, 1 / fps)
             if lo <= q <= hi]
    for p in cands:
        cand = S[:, int((p - win) * fps):int((p - win) * fps) + ref.shape[1]]
        if cand.shape != ref.shape:
            continue
        c = float(np.sum(cand * ref) / (np.linalg.norm(cand) * np.linalg.norm(ref) + 1e-9))
        if c > best:
            best, bp = c, p
    return bp, best


def extended_music(x, dur, fade=(30.7, 32.0)):
    """Continue the track past its end: jump back to the point whose sound best matches the end,
    crossfade, and play on from there (repeat if needed)."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    m = min(len(x), n)
    out[:m] = x[:m]
    t = len(x) / SR
    xf = int(0.12 * SR)
    src_end = len(x) / SR
    while t < dur - 0.01:
        p, c = best_continuation(x, src_end if t >= src_end else t)
        print(f'continue {t:.2f}s from {p:.2f}s (similarity {c:.3f})')
        i0 = int(t * SR)
        s0 = int(p * SR)
        seg = x[s0:]
        L = min(len(seg), n - i0)
        if L <= xf:
            break
        ramp = np.linspace(0, 1, xf)[:, None] ** 0.5
        out[i0 - xf:i0] = out[i0 - xf:i0] * (1 - ramp) + x[s0 - xf:s0] * ramp
        out[i0:i0 + L] = seg[:L]
        t += L / SR
    a, b = int(fade[0] * SR), int(fade[1] * SR)
    g = np.ones(n)
    g[a:b] = np.cos(np.linspace(0, np.pi / 2, b - a)) ** 2
    g[b:] = 0
    return out * g[:, None]


def build(cues, dur, out_dir=None, music_gain=1.0, duck_db=4.0):
    out_dir = out_dir or ROOT + '/out'
    os.makedirs(out_dir, exist_ok=True)
    bus = Bus(dur)
    for c in cues:
        t0, kind, g = c[0], c[1], c[2]
        kw = dict(c[3]) if len(c) > 3 else {}
        pan = kw.pop('pan', 0.0)
        if kind == 'rain_bed':
            x = rain_bed(kw.get('d', 4.0))
        else:
            x = VOICES[kind](**kw)
        bus.add(t0, x, g, pan)
    src = source_track()
    music = extended_music(src, dur)
    # duck SFX a little under the voice (voice + music share the source track)
    env = lp(np.abs(src.mean(1)), 8, 1)
    env = np.pad(env, (0, max(0, bus.N - len(env))))[:bus.N]
    lvl = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
    duck = 1 - (1 - 10 ** (-duck_db / 20)) * lp(lvl, 3, 1)
    fx = bus.x / (np.abs(bus.x).max() + 1e-9) * 0.85 * duck[:, None]
    # sidechain: the music dips (up to ~4 dB) under big hits so impacts punch through
    fenv = lp(np.abs(fx).mean(1), 12, 1)
    side = 1 - 0.37 * np.clip(fenv / (np.percentile(fenv, 99.5) + 1e-9), 0, 1)
    mix = music * music_gain * side[:, None] + fx
    wavfile.write(out_dir + '/sfx_stem.wav', SR, (np.clip(norm(fx, 0.97), -1, 1) * 32767).astype(np.int16))
    mix = np.tanh(mix * 1.15) / np.tanh(1.15)
    mix = norm(mix, 0.97)
    tmp = out_dir + '/audio_raw.wav'
    wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', 'loudnorm=I=-12:TP=-1.0:LRA=11', '-ar', str(SR),
                    out_dir + '/audio.wav'], check=True)
    return out_dir + '/audio.wav'


if __name__ == '__main__':
    cues = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 32.0
    print(build(cues, dur))
