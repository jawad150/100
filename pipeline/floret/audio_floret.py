"""Floret Capitals spot - synthesized score + sound design (48 kHz stereo).

Score: D minor corporate-cinematic at 120 bpm (Dm - Bb - F - C, 2 bars each). Pad from the first frame,
kick from frame 2, hats from frame 4, claps + eighth-note bass from frame 6, filtered build + snare roll
through the tunnel (frame 9), a hard stop, then the THINK BIGGER / THINK FLORET hits and a resolving
chord under the logo. SFX are synced to the on-screen events (floret.FRAMES).

python3 audio_floret.py  -> workspace4/work/audio.wav
"""
import os
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'memories'))
import sound as SND  # noqa: E402

SR = SND.SR
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'workspace4'))
DUR = 36.0
BPM = 120
BEAT = 60 / BPM
T_STOP, T_HIT1, T_HIT2, T_LOGO = 30.45, 30.70, 31.22, 32.65
rng = np.random.default_rng(3)


def hz(note):
    return 440.0 * 2 ** ((note - 69) / 12)


CHORDS = [(62, 65, 69), (58, 62, 65), (53, 57, 60), (60, 64, 67)]     # Dm Bb F C (MIDI)
ROOTS = [38, 34, 41, 36]


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na) if na else 1
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw(f, n, detune=0.0, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * f * (1 + detune) + phase) % 1.0) - 1


def pad(dur):
    out = np.zeros((int(dur * SR), 2))
    seg = 4 * BEAT * 2                                          # chord every 2 bars (4 s)
    k = 0
    t0 = 0.0
    while t0 < dur:
        notes = CHORDS[k % 4]
        n = int(min(seg + 0.6, dur - t0) * SR)
        x = np.zeros((n, 2))
        for m in notes + (notes[0] - 12,):
            for d, pan in ((-0.004, -0.6), (0.0, 0.0), (0.0045, 0.6)):
                v = saw(hz(m), n, d, rng.random())
                x[:, 0] += v * (1 - pan) * 0.5
                x[:, 1] += v * (1 + pan) * 0.5
        x = np.stack([SND.lp(x[:, 0], 1400, 2), SND.lp(x[:, 1], 1400, 2)], 1)
        x *= env_adsr(n, 0.8, 0.9)[:, None]
        i = int(t0 * SR)
        L = min(n, len(out) - i)
        out[i:i + L] += x[:L]
        t0 += seg
        k += 1
    out *= 0.08
    return SND.reverb(out, 0.3, 2.4)[:len(out)]


def kick():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 7.5)
    x += 0.4 * np.exp(-t * 300) * rng.normal(0, 1, n)
    return np.tanh(x * 1.6)


def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR)
    x = SND.hp(rng.normal(0, 1, n), 7000, 2) * np.exp(-np.arange(n) / SR * (14 if open_ else 70))
    return x * 0.5


def clap():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    x = SND.bp(rng.normal(0, 1, n), 900, 3200) * (np.exp(-t * 18) + 0.6 * np.exp(-((t - 0.012) % 0.011) * 400) * (t < 0.04))
    return SND.reverb(x, 0.25, 0.8)[:n] * 0.8


def bass(note, d):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = hz(note)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * saw(f, n)
    return np.tanh(x * 1.4) * env_adsr(n, 0.005, d * 0.6)


def score():
    bus = SND.Bus(DUR)
    p = pad(DUR)
    # intensity: pad louder in the finale, out during the stop
    g = np.ones(len(p))
    a, b = int(T_STOP * SR), int(T_HIT1 * SR)
    g[a:b] = np.linspace(1, 0.05, b - a)
    g[b:] = 1.5
    bus.x += p * g[:, None]
    nb = int(DUR / BEAT)
    for i in range(nb):
        t = i * BEAT
        chord = int(t // (8 * BEAT)) % 4
        if 3.8 <= t < T_STOP:
            bus.add(t, kick(), 0.9)
        if 10.2 <= t < T_STOP:
            bus.add(t + BEAT / 2, hat(i % 4 == 3), 0.35, pan=0.25)
            bus.add(t + BEAT / 4, hat(), 0.12, pan=-0.3)
        if 16.6 <= t < T_STOP and i % 2 == 1:
            bus.add(t, clap(), 0.45)
        if 16.6 <= t < T_STOP:
            for h in (0, 0.5):
                bus.add(t + h * BEAT, bass(ROOTS[chord], BEAT * 0.45), 0.35)
        elif 3.8 <= t < 16.6 and i % 2 == 0:
            bus.add(t, bass(ROOTS[chord], BEAT * 1.8), 0.3)
    # snare roll build in the tunnel
    t = 28.6
    while t < T_STOP - 0.02:
        gap = max(0.045, 0.25 * (1 - (t - 28.6) / (T_STOP - 28.6)) ** 1.5)
        bus.add(t, clap(), 0.18 + 0.4 * (t - 28.6) / (T_STOP - 28.6))
        t += gap
    # finale sub + chord stabs
    bus.add(T_HIT1, bass(26, 2.6), 0.6)
    bus.add(T_LOGO, bass(26, 3.2), 0.5)
    return bus.x


def sfx():
    bus = SND.Bus(DUR)
    V = SND.VOICES

    def add(t, kind, g, pan=0.0, **kw):
        bus.add(t, V[kind](**kw), g, pan)
    # frame 1: logo
    add(0.0, 'reverse_swell', 0.35)
    for i in range(4):
        add(0.42 + 0.2 * i, 'pop', 0.35, pan=-0.3 + 0.2 * i)
    add(1.05, 'whoosh', 0.35, d=0.7, f0=500, f1=6000, sweep=(-0.6, 0.6))
    add(1.6, 'shimmer', 0.4)
    # cuts
    from_frames = [3.8, 6.8, 10.2, 13.4, 16.6, 20.6, 24.4, 27.8]
    for k, t in enumerate(from_frames):
        add(t - 0.28, 'whoosh', 0.42, d=0.55, sweep=(-0.7, 0.7) if k % 2 else (0.7, -0.7))
        add(t, 'sub_drop', 0.18, d=1.0)
    # frame 2
    add(4.0, 'click', 0.35)
    # frame 3: counter + pings
    add(7.15, 'ticks', 0.32, n=26, gap=0.055)
    add(8.75, 'pop', 0.45)
    for i in range(11):
        add(7.3 + 0.11 * i + 0.5, 'click', 0.12, pan=(i % 3 - 1) * 0.5)
    # frame 4: tab switches
    for k in range(4):
        add(10.2 + 0.9 + 0.55 * k, 'click', 0.4)
    add(10.8, 'pop', 0.25, pan=-0.6)
    add(11.0, 'pop', 0.25, pan=0.6)
    # frame 5
    add(14.15, 'impact', 0.4)
    add(14.15, 'glass', 0.12)
    for i in range(3):
        add(14.4 + 0.22 * i, 'pop', 0.35, pan=(i - 1) * 0.6)
    # frame 6
    for i, t in enumerate((16.8, 17.45, 18.1, 18.8)):
        add(t, 'whoosh', 0.22, d=0.4, f0=800, f1=5000)
        add(t + 0.08, 'pop', 0.3, pan=0.4)
    add(19.6, 'whoosh_slow', 0.25)
    # frame 7
    for i in range(4):
        add(21.6 + 0.16 * i, 'pop', 0.3, pan=0.5)
    add(22.2, 'ticks', 0.18, n=14, gap=0.07)
    # frame 8
    add(24.45, 'shimmer', 0.35)
    for i in range(3):
        add(24.6 + 0.55 * i, 'pop', 0.38, pan=-0.4)
    # frame 9: tunnel
    add(27.8, 'riser', 0.5, d=2.6)
    add(27.9, 'whoosh_slow', 0.4)
    # frame 10
    add(T_HIT1, 'impact', 0.9)
    add(T_HIT1, 'braam', 0.45, d=2.4)
    add(T_HIT2, 'impact', 0.8)
    add(T_HIT2, 'sub_drop', 0.5, d=1.6)
    add(T_LOGO - 0.4, 'reverse_swell', 0.35)
    add(T_LOGO, 'shimmer', 0.55)
    add(T_LOGO + 0.1, 'chimes', 0.3, d=3.0)
    add(T_LOGO + 0.6, 'whoosh', 0.25, d=0.8)
    return bus.x


def build():
    mus = score()
    fx = sfx()
    mus = mus / (np.abs(mus).max() + 1e-9) * 0.8
    fx = fx / (np.abs(fx).max() + 1e-9) * 0.75
    # sidechain: music ducks under the big hits
    fenv = SND.lp(np.abs(fx).mean(1), 10, 1)
    side = 1 - 0.35 * np.clip(fenv / (np.percentile(fenv, 99.5) + 1e-9), 0, 1)
    mix = mus * side[:, None] + fx
    n = len(mix)
    g = np.ones(n)
    a = int((DUR - 1.2) * SR)
    g[a:] = np.cos(np.linspace(0, np.pi / 2, n - a)) ** 2
    mix *= g[:, None]
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix = SND.norm(mix, 0.97)
    os.makedirs(ROOT + '/work', exist_ok=True)
    raw = ROOT + '/work/audio_raw.wav'
    wavfile.write(raw, SR, (mix * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.0:LRA=9', '-ar', str(SR),
                    ROOT + '/work/audio.wav'], check=True)
    return ROOT + '/work/audio.wav'


if __name__ == '__main__':
    print(build())
