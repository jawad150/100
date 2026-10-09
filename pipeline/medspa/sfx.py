"""Subtle transition SFX mixed under the original audio (voice + music stay untouched).

Whooshes on the cuts, soft pops when the photo cards land, ticks for the pills.
Writes $WS/out/mix.wav (48 kHz stereo).
"""
import subprocess, wave
import numpy as np
from scipy import signal
from common import WS, FPS, CUTS, NOUT
import render as R

SR = 48000
rng = np.random.default_rng(3)


def load_orig():
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{WS}/src/PS-Med-Spa.mov', '-vn', '-f', 's16le',
                          '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], 'band')
    return signal.lfilter(b, a, x)


def whoosh(dur, peak_at, f0=250, f1=3800, bands=7, pan=(-0.5, 0.5)):
    """Band-swept noise: successive bands peak in turn -> rising (or falling) sweep."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    out = np.zeros(n)
    freqs = np.geomspace(f0, f1, bands + 1)
    for i in range(bands):
        x = bp(noise, freqs[i], freqs[i + 1])
        c = peak_at * (0.55 + 0.45 * i / (bands - 1))
        w = dur * 0.30
        env = np.exp(-((t - c) / w) ** 2)
        out += x * env / np.sqrt(bands)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.06)
    out *= env
    p = np.linspace(pan[0], pan[1], n)
    return np.stack([out * np.sqrt(0.5 * (1 - p)), out * np.sqrt(0.5 * (1 + p))], 1)


def pop(freq=520, dur=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t / 0.012))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.045)
    x += bp(rng.normal(0, 1, n), 1500, 6000) * np.exp(-t / 0.006) * 0.3
    return np.stack([x, x], 1) * 0.7


def swell(dur=0.7, peak_at=0.55):
    """Airy reverse-swell for flashes."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bp(rng.normal(0, 1, n), 2500, 11000)
    env = np.where(t < peak_at, (t / peak_at) ** 3, np.exp(-(t - peak_at) / 0.08))
    y = x * env
    return np.stack([y, np.roll(y, 120)], 1)


def add(buf, t0, x, gain):
    i = int(t0 * SR)
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n] * gain


def main():
    orig = load_orig()
    # the reel holds its last frame a little longer: fade the source tail, pad with silence
    n_out = int(round(NOUT / FPS * SR))
    tail = int(0.35 * SR)
    orig[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 2
    orig = np.vstack([orig, np.zeros((max(0, n_out - len(orig)), 2))])
    sfx = np.zeros_like(orig)
    db = lambda d: 10 ** (d / 20)
    for c, typ in R.TRANS.items():
        tc = c / FPS
        if typ in ('zoom', 'punch', 'blur'):
            add(sfx, tc - 0.32, whoosh(0.6, 0.32, 300, 4200), db(-21))
        elif typ in ('whip', 'whipv'):
            add(sfx, tc - 0.22, whoosh(0.45, 0.22, 500, 6000, pan=(-0.8, 0.8)), db(-20))
        elif typ == 'flash':
            add(sfx, tc - 0.55, swell(0.75, 0.55), db(-25))
        elif typ == 'leak':
            add(sfx, tc - 0.40, whoosh(0.9, 0.40, 200, 3000, pan=(0.6, -0.6)), db(-22))
            add(sfx, tc - 0.55, swell(0.8, 0.55), db(-28))
    for i, card in enumerate(R.CARDS):
        add(sfx, card[6] - 0.05, whoosh(0.4, 0.2, 600, 5000, pan=(-0.6 * card[7], 0.0)), db(-27))
        add(sfx, card[6] + 0.30, pop(480 + 60 * i), db(-26))
    for el in R.OVERLAY:
        if el['kind'] == 'pill':
            add(sfx, el['t0'] + 0.05, pop(900, 0.1), db(-28))
    mix = orig + sfx
    peak = np.abs(mix).max()
    if peak > 0.94:   # gentle safety limiter
        mix = np.tanh(mix / 0.94 * 1.0) * 0.94
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(f'{WS}/out/mix.wav', 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('mix peak', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS; sfx peak',
          round(20 * np.log10(np.abs(sfx).max() + 1e-9), 2))


if __name__ == '__main__':
    main()
