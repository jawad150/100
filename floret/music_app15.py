"""Original 15 s music bed for floret_app_15s.mp4, scored to its picture (stereo 48 kHz WAV).

122.6 BPM so beat 24 lands on the logo reveal (11.75 s). Am-F-C-G | F-G, soft pad intro, a light groove
(kick, hats, clap, pluck arpeggio, bass) from 1 s with a slowly opening filter, a riser from 9.8 s with the
drums dropping at 10.77 s (under the video's own whoosh), then an impact and a bright C(add9) chord with
shimmer for the logo, held under the tagline and faded out.

    python3 floret/music_app15.py <out.wav>
"""
import subprocess, sys
import numpy as np
from scipy.signal import lfilter, butter

SR, DUR = 48000, 15.0
N = int(SR * DUR)
t = np.arange(N) / SR
BEAT = 11.75 / 24
BAR = 4 * BEAT
LOGO = 11.75
rng = np.random.default_rng(11)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, cutoff):
    """One-pole-pair lowpass with a time-varying cutoff (array) or a fixed one."""
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * np.clip(cutoff, 20, SR / 2.5) / SR)
    y = np.empty_like(x); z = 0.0
    for _ in range(2):
        out = np.empty_like(x)
        for i in range(len(x)):        # cheap enough for 15 s at 48 kHz
            z = (1 - a[i]) * x[i] + a[i] * z
            out[i] = z
        x = out
    return x


def bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return lfilter(b, a, x)


def hp(x, f):
    b, a = butter(2, f / (SR / 2), 'high')
    return lfilter(b, a, x)


def env_at(start, attack, decay, sustain=0.0, release=None, length=None):
    """ADSR-ish envelope over the whole timeline."""
    e = np.zeros(N)
    i0 = int(start * SR)
    if i0 >= N:
        return e
    n_a, n_d = max(1, int(attack * SR)), max(1, int(decay * SR))
    seg = np.concatenate([np.linspace(0, 1, n_a), sustain + (1 - sustain) * np.exp(-np.linspace(0, 5, n_d))])
    if length:
        hold = max(0, int(length * SR) - len(seg))
        seg = np.concatenate([seg, np.full(hold, seg[-1])])
        if release:
            seg = np.concatenate([seg, seg[-1] * np.exp(-np.linspace(0, 6, int(release * SR)))])
    i1 = min(N, i0 + len(seg))
    e[i0:i1] = seg[:i1 - i0]
    return e


def saw(f, phase=0.0):
    p = (f * t + phase) % 1.0
    return 2 * p - 1


L = np.zeros(N); R = np.zeros(N)


def add(sig, gain=1.0, pan=0.0):
    global L, R
    L += sig * gain * np.sqrt(0.5 * (1 - pan))
    R += sig * gain * np.sqrt(0.5 * (1 + pan))


# chords per bar (MIDI): Am F C G | F G | logo: C(add9)
CHORDS = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67], [53, 57, 60, 65], [55, 59, 62, 67]]
BASS = [45, 41, 48, 43, 41, 43]
LOGO_CHORD = [48, 55, 60, 62, 64, 67, 72]

# ---------------------------------------------------------------- pad (whole bed), opening filter
pad = np.zeros(N)
for b, chord in enumerate(CHORDS):
    s, e = b * BAR, (b + 1) * BAR
    gate = np.clip((t - s) / 0.25, 0, 1) * np.clip((e + 0.25 - t) / 0.25, 0, 1)
    for n in chord:
        f = midi(n)
        pad += gate * (saw(f * 1.003, rng.random()) + saw(f * 0.997, rng.random())) * 0.5
cut = 500 + 2600 * np.clip(t / 10.5, 0, 1) ** 1.5           # filter opens across the phone section
pad = lowpass(pad * 0.06, cut)
pad *= np.clip(t / 1.0, 0, 1) * np.clip((LOGO + 0.05 - t) / 0.08, 0, 1)
add(pad, 1.0, -0.25)
add(np.roll(pad, int(0.011 * SR)), 1.0, 0.25)                 # Haas widening

# ---------------------------------------------------------------- groove from 1 s (beat 2) to the drop at beat 22
GROOVE_START, DROP = 2, 22
kick = np.zeros(N); hat = np.zeros(N); clap = np.zeros(N)
noise = rng.standard_normal(N)
for k in range(GROOVE_START, DROP):
    bt = k * BEAT
    e = env_at(bt, 0.002, 0.28)
    fsweep = 45 + 70 * env_at(bt, 0.001, 0.05)
    phase = 2 * np.pi * np.cumsum(fsweep) / SR
    kick += np.sin(phase) * e
    if k % 4 in (1, 3):
        clap += noise * env_at(bt, 0.002, 0.16)
    for h in (0.5,):
        hat += noise * env_at(bt + h * BEAT, 0.001, 0.05)
    hat += noise * env_at(bt, 0.001, 0.025) * 0.5
add(kick * 0.32, 1.0)
add(bp(clap, 900, 3500) * 0.10, 1.0, 0.1)
add(hp(hat, 7000) * 0.06, 1.0, 0.35)

# ---------------------------------------------------------------- bass (8th notes, from the groove start)
bass = np.zeros(N)
for k in range(GROOVE_START * 2, DROP * 2):
    bt = k * BEAT / 2
    f = midi(BASS[int(bt // BAR)])
    bass += np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 2 * f * t)) * env_at(bt, 0.004, 0.22, 0.0)
add(lowpass(bass, 900) * 0.16, 1.0)

# ---------------------------------------------------------------- pluck arpeggio (16ths, ping-pong), from beat 4
arp_l = np.zeros(N); arp_r = np.zeros(N)
for k in range(4 * 4, DROP * 4):
    bt = k * BEAT / 4
    chord = CHORDS[int(bt // BAR)]
    n = chord[[0, 1, 2, 3, 2, 1, 3, 2][k % 8]] + 12
    s = (saw(midi(n)) * 0.6 + np.sin(2 * np.pi * midi(n) * t) * 0.4) * env_at(bt, 0.002, 0.18)
    (arp_l if k % 2 == 0 else arp_r)[:] += s
arp_cut = 1200 + 3000 * np.clip((t - 2) / 8.5, 0, 1)
L += lowpass(arp_l, arp_cut) * 0.035
R += lowpass(arp_r, arp_cut) * 0.035

# ---------------------------------------------------------------- riser into the logo (9.8 s -> 11.75 s)
rise = np.clip((t - 9.8) / (LOGO - 9.8), 0, 1) * (t < LOGO)
riser = lowpass(noise * rise ** 2, 300 + 7000 * rise ** 2) * 0.22
tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * rise ** 2) / SR) * rise ** 3 * 0.05
add(riser + tone, 1.0)

# ---------------------------------------------------------------- logo: impact + bright chord + shimmer, held to the end
boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * env_at(LOGO, 0.001, 0.12)) / SR) * env_at(LOGO, 0.002, 1.6)
add(boom * 0.45, 1.0)
add(lowpass(noise * env_at(LOGO, 0.001, 0.6), 2500) * 0.12, 1.0)
hold = np.clip((t - LOGO) / 0.05, 0, 1) * np.clip((DUR - t) / 1.6, 0, 1)
chord = np.zeros(N)
for n in LOGO_CHORD:
    f = midi(n)
    chord += (saw(f * 1.004, rng.random()) + saw(f * 0.996, rng.random())) * 0.5
chord = lowpass(chord * 0.05, 1800 + 2400 * np.exp(-np.clip(t - LOGO, 0, None) * 1.2))
add(chord * hold, 1.0, -0.2)
add(np.roll(chord * hold, int(0.013 * SR)), 1.0, 0.2)
for j, n in enumerate([84, 88, 91, 96, 91, 95]):              # shimmer bells as the logo draws (to 13 s)
    st = LOGO + 0.18 * j
    bell = (np.sin(2 * np.pi * midi(n) * t) + 0.3 * np.sin(2 * np.pi * midi(n) * 2.76 * t)) * env_at(st, 0.002, 1.4)
    add(bell * 0.035, 1.0, -0.5 + 0.2 * j)

# ---------------------------------------------------------------- master
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.4) / 1.4                                # gentle glue / soft clip
mix /= np.abs(mix).max() / 0.9
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', sys.argv[1]],
               input=mix.astype(np.float64).tobytes(), check=True)
print(sys.argv[1])
