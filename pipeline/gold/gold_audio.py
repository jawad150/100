"""Sound design for the gold reel: synthesized cinematic SFX (whooshes, impacts, risers, coin
chings, pops, UI clicks) placed from timeline.SFX, ducked under the original voice track.

Writes $GOLD_WORKDIR/out/audio.wav (48 kHz stereo).
"""
import os, sys, subprocess
import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as TL

S = os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace')))
SR = 48000
DUR = TL.NFRAMES / TL.FPS
N = int(SR * DUR)
rng = np.random.default_rng(21)
sfx = np.zeros((N, 2))


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(t0, x, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if x.ndim == 1:
        l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        x = np.stack([x * l * 1.414, x * r * 1.414], 1)
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), N - i)
    if n > 0:
        sfx[i:i + n] += x[:n] * gain


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
    """Time-varying band-pass (state-variable filter) sweeping f0 -> f1."""
    n = len(x)
    out = np.zeros(n)
    low = band = 0.0
    freqs = f0 * (f1 / f0) ** (np.linspace(0, 1, n) ** curve)
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


_ir = {}


def reverb(x, wet=0.3, length=1.8):
    if length not in _ir:
        n = int(length * SR)
        e = np.exp(-np.linspace(0, 7, n))
        irl, irr = lp(rng.normal(0, 1, n) * e, 6000), lp(rng.normal(0, 1, n) * e, 6000)
        _ir[length] = np.stack([irl, irr], 1) / np.sqrt(np.sum(e ** 2)) * 0.5
    ir = _ir[length]
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    y = np.stack([signal.fftconvolve(x[:, 0], ir[:, 0]), signal.fftconvolve(x[:, 1], ir[:, 1])], 1)
    out = np.zeros_like(y)
    out[:len(x)] = x * (1 - wet)
    return out + y * wet

# ------------------------------------------------------------------ voices


def impact(t0, g):
    t = tt(2.2)
    f = 38 + 90 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 0.9
    nz = lp(rng.normal(0, 1, len(t)), 1800) * np.exp(-t * 14) * 0.5
    crack = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 40) * 0.25
    add(t0, reverb(sub + nz + crack, 0.3, 1.8), 0.9 * g)


def hit_soft(t0, g):
    t = tt(1.0)
    f = 50 + 60 * np.exp(-t * 12)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) + lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 20) * 0.3
    add(t0, reverb(x, 0.25), 0.7 * g)


def boom(t0, g):
    t = tt(3.0)
    f = 32 + 40 * np.exp(-t * 4)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.2)
    x += lp(rng.normal(0, 1, len(t)), 400) * np.exp(-t * 3) * 0.4
    add(t0, reverb(x, 0.25), 0.9 * g)


def whoosh(t0, g, dur=0.5, f0=250, f1=3500, pan0=-0.6, pan1=0.6, peak=0.65):
    n = int(dur * SR)
    y = sweep_bp(rng.normal(0, 1, n), f0, f1, q=1.2)
    p = np.linspace(0, 1, n)
    y = y * np.where(p < peak, (p / peak) ** 2, ((1 - p) / (1 - peak)) ** 1.5)
    pans = np.linspace(pan0, pan1, n)
    st = np.stack([y * np.sqrt(0.5 * (1 - pans)), y * np.sqrt(0.5 * (1 + pans))], 1) * 1.4
    add(t0, reverb(st, 0.2), 0.5 * g / (np.abs(y).max() + 1e-9))


def whoosh_big(t0, g):
    whoosh(t0, g, dur=0.62, f0=160, f1=5200, pan0=-0.9, pan1=0.9, peak=0.5)
    boom(t0 + 0.3, 0.25 * g)


def whoosh_zoom(t0, g):
    whoosh(t0, g, dur=0.55, f0=300, f1=7000, pan0=0, pan1=0, peak=0.55)


def swish(t0, g):
    whoosh(t0, g, dur=0.22, f0=900, f1=6000, pan0=-0.3, pan1=0.3, peak=0.4)


def ching(t0, g):
    """Bright metallic coin ring (inharmonic partials)."""
    t = tt(1.6)
    x = np.zeros(len(t))
    for f, a, d in [(2637, 1.0, 3.5), (3960, 0.7, 4.5), (5274, 0.5, 6), (6330, 0.35, 7), (8120, 0.25, 9),
                    (1318, 0.3, 3)]:
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * d)
    x += hp(rng.normal(0, 1, len(t)), 6000) * np.exp(-t * 120) * 0.6
    add(t0, reverb(x / 3, 0.35, 1.8), 0.6 * g, pan=rng.uniform(-0.3, 0.3))


def tick(t0, g, f=3200):
    t = tt(0.08)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + hp(rng.normal(0, 1, len(t)), 5000) * np.exp(-t * 200) * 0.4
    add(t0, reverb(x, 0.15), g, pan=rng.uniform(-0.3, 0.3))


def tick_run(t0, g):
    for k in range(9):
        tick(t0 + 0.25 + k * 0.1, g * (0.6 + 0.05 * k), f=2400 + k * 120)


def click(t0, g):
    t = tt(0.05)
    a = bp(rng.normal(0, 1, len(t)), 1500, 7000) * np.exp(-t * 400)
    b = np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 250) * 0.6
    add(t0, reverb(a + b, 0.1), g)
    add(t0 + 0.07, reverb(a * 0.6, 0.1), g * 0.7)


def pop(t0, g, f0=280, f1=950):
    t = tt(0.22)
    f = f0 + (f1 - f0) * (1 - np.exp(-t * 45))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * np.clip(t * 400, 0, 1)
    add(t0, reverb(x, 0.2), g, pan=rng.uniform(-0.4, 0.4))


def shimmer(t0, g, dur=1.6):
    t = tt(dur)
    x = np.zeros(len(t))
    for k in range(14):
        x += np.sin(2 * np.pi * rng.uniform(2200, 7500) * t + rng.uniform(0, 6)) * \
            (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(4, 11) * t))
    x *= np.exp(-t * 2.2) * np.clip(t * 30, 0, 1) / 14
    add(t0, reverb(x, 0.5, 2.2), 0.5 * g)


def riser(t0, g, d=0.55):
    n = int(d * SR)
    p = np.linspace(0, 1, n)
    nz = sweep_bp(rng.normal(0, 1, n), 200, 7000, q=1.5, curve=2.0)
    nz = nz / (np.abs(nz).max() + 1e-9)
    f = 90 * (8 ** (p ** 1.6))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.2
    x = (nz * 0.8 + tone) * (p ** 2.2)
    add(t0, np.stack([x, np.roll(x, 240)], 1), g)


def riser_long(t0, g):
    riser(t0, g, d=2.4)


KINDS = dict(impact=impact, hit_soft=hit_soft, boom=boom, whoosh=whoosh, whoosh_big=whoosh_big,
             whoosh_zoom=whoosh_zoom, swish=swish, ching=ching, tick_run=tick_run, click=click, pop=pop,
             shimmer=shimmer, riser=riser, riser_long=riser_long, tick=tick)


def main():
    os.makedirs(S + '/out', exist_ok=True)
    cues = TL.SFX
    if os.environ.get('CUES'):                        # e.g. the reference cut's cue sheet (ref_reel.py sfx)
        import json
        cues = json.load(open(os.environ['CUES']))
    for t, kind, g in cues:
        KINDS[kind](max(t, 0.0), g)
    # original voice from the color-corrected render
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', S + '/src/color_correction.mp4', '-vn', '-ac', '2', '-ar',
                          str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    voice = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    voice = np.pad(voice, ((0, max(0, N - len(voice))), (0, 0)))[:N]
    # duck the effects under speech (~6 dB), with fast attack / slow release
    env = np.abs(voice).mean(1)
    env = lp(env, 8, 1)
    lvl = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
    duck = 1 - 0.5 * lp(lvl, 3, 1)
    fx = sfx / (np.abs(sfx).max() + 1e-9) * 0.55
    mix = voice + fx * duck[:, None]
    stem = fx * duck[:, None]                             # SFX-only stem, exactly as it sits in the mix
    from scipy.io import wavfile as _wf
    _wf.write(S + '/out/sfx_stem.wav', SR, (np.clip(stem * 0.97 / (np.abs(stem).max() + 1e-9), -1, 1) * 32767).astype(np.int16))
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix *= 0.97 / (np.abs(mix).max() + 1e-9)
    tmp = S + '/out/audio_raw.wav'
    from scipy.io import wavfile
    wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', 'loudnorm=I=-12:TP=-1.0:LRA=11', '-ar', str(SR),
                    S + '/out/audio.wav'], check=True)
    print('audio done', DUR)


if __name__ == '__main__':
    main()
