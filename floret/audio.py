"""Soft music bed + UI sound design for the Floret phone animation, with the voiceover mixed on top.

    python3 floret/audio.py <out.wav> [voiceover.wav] [vo_start_seconds]
"""
import sys, wave
import numpy as np

SR, DUR = 48000, 12.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(3)


def env(start, attack, decay, length=None):
    e = np.zeros(N)
    i0 = int(start * SR)
    a = int(attack * SR)
    d = int(decay * SR)
    seg = np.concatenate([np.linspace(0, 1, max(a, 1)), np.exp(-np.linspace(0, 6, max(d, 1)))])
    i1 = min(N, i0 + len(seg))
    e[i0:i1] = seg[:i1 - i0]
    return e


def lowpass(x, cutoff):
    k = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - k) * v + k * acc
        y[i] = acc
    return y


# ---- pad: warm minor-9 chord, slow swell
def note(f):
    return sum(np.sin(2 * np.pi * f * m * t + rng.uniform(0, 6)) / m ** 1.6 for m in (1, 2, 3))

chord = [110.0, 130.81, 164.81, 196.0, 246.94]  # A2 C3 E3 G3 B3
pad = sum(note(f) * (1 + 0.15 * np.sin(2 * np.pi * (0.13 + k * 0.05) * t)) for k, f in enumerate(chord))
pad *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 1.2, 0, 1) * 0.045

# ---- soft pulse (sub kick every beat at 96 bpm, starting after the intro)
beat = 60 / 96
pulse = np.zeros(N)
for b in np.arange(0.8, DUR - 0.5, beat):
    e = env(b, 0.002, 0.35)
    pulse += np.sin(2 * np.pi * (48 + 40 * e) * t) * e
pulse *= 0.16 * np.clip(t / 2.0, 0, 1)

# ---- airy shimmer arpeggio
arp = np.zeros(N)
notes = [440.0, 523.25, 659.25, 783.99, 987.77, 783.99, 659.25, 523.25]
for k, s in enumerate(np.arange(0.8, DUR - 0.8, beat / 2)):
    f = notes[k % len(notes)]
    e = env(s, 0.004, 0.5)
    arp += np.sin(2 * np.pi * f * t) * e * (0.6 + 0.4 * np.sin(k))
arp *= 0.018 * np.clip(t / 2.5, 0, 1) * np.clip((DUR - t) / 1.0, 0, 1)

# ---- one soft air swell under the fade-in; the shot itself is a continuous glide
noise = rng.standard_normal(N)
swell = np.zeros(N)
i1 = int(2.4 * SR)
swell[:i1] = np.sin(np.pi * np.linspace(0, 1, i1)) ** 2
fx = lowpass(noise * swell, 700) * 0.22

# ---- faint price ticks
for s in np.arange(1.0, DUR - 0.4, 0.61):
    e = env(s + rng.uniform(-0.05, 0.05), 0.0005, 0.02)
    fx += np.sin(2 * np.pi * 2400 * t) * e * 0.014

music = pad + pulse + arp

# ---- voiceover
out_path = sys.argv[1]
vo = np.zeros(N)
if len(sys.argv) > 2:
    with wave.open(sys.argv[2]) as w:
        assert w.getframerate() == SR and w.getsampwidth() == 2, 'resample the voiceover to 48 kHz s16 first'
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
        if w.getnchannels() == 2:
            raw = raw.reshape(-1, 2).mean(1)
    start = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    i0 = int(start * SR)
    raw = raw[:N - i0]
    vo[i0:i0 + len(raw)] = raw / (np.abs(raw).max() + 1e-9) * 0.9
    # duck the music under the voice
    level = lowpass(np.abs(vo), 6)
    duck = 1 - 0.55 * np.clip(level / (level.max() + 1e-9) * 3, 0, 1)
    music *= duck

mix = music + fx * 0.8 + vo
mix /= max(1.0, np.abs(mix).max() / 0.95)
with wave.open(out_path, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(out_path)
