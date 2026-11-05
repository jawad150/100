"""Original 15 s music bed for floret_app_15s.mp4, scored to its picture (stereo 48 kHz WAV).

122.6 BPM so beat 24 lands on the logo reveal (11.75 s). Am-F-C-G | F-G, then C(add9) for the logo.

    0.0-1.0   wide pad swells in under a reverse-cymbal sweep
    1.0-10.8  groove: layered kick, clap, 16th hats, shaker, open hats, sidechained sub/mid bass, supersaw pad
              with a slowly opening filter, ping-pong pluck arpeggio, a soft bell hook from bar 3
    9.8-11.75 riser (noise + pitch sweep, snare roll); drums drop at 10.8 s
    11.75     impact (sub boom + cymbal) and a bright C(add9) chord with shimmer, held under the tagline, fading out

Mastered: low-cut, glue compression, soft limiter, peak -1 dBFS.

    python3 floret/music_app15.py <out.wav>
"""
import subprocess, sys
import numpy as np
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR, DUR = 48000, 15.0
N = int(SR * DUR)
t = np.arange(N) / SR
BEAT = 11.75 / 24
BAR = 4 * BEAT
LOGO = 11.75
GROOVE_START, DROP = 2, 22                          # beats
rng = np.random.default_rng(11)
noise = rng.standard_normal(N)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def sweep_lp(x, cutoff, q=0.7, block=1024):
    """Lowpass with a time-varying cutoff (array): 2nd-order biquad updated every block, state carried over."""
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    y = np.empty_like(x)
    zi = np.zeros(2)
    for i in range(0, len(x), block):
        fc = float(np.clip(cutoff[i], 30, SR / 2.3))
        w = 2 * np.pi * fc / SR
        alpha = np.sin(w) / (2 * q)
        b = np.array([(1 - np.cos(w)) / 2, 1 - np.cos(w), (1 - np.cos(w)) / 2])
        a = np.array([1 + alpha, -2 * np.cos(w), 1 - alpha])
        y[i:i + block], zi = lfilter(b / a[0], a / a[0], x[i:i + block], zi=zi)
    return y


def filt(x, kind, f):
    return sosfilt(butter(2, np.asarray(f) / (SR / 2), kind, output='sos'), x)


def env_at(start, attack, decay, curve=5.0):
    e = np.zeros(N)
    i0 = int(start * SR)
    if i0 >= N or start < -1:
        return e
    seg = np.concatenate([np.linspace(0, 1, max(1, int(attack * SR))), np.exp(-np.linspace(0, curve, max(1, int(decay * SR))))])
    i1 = min(N, i0 + len(seg))
    e[max(0, i0):i1] = seg[max(0, -i0):i1 - i0]
    return e


def saw(f, phase=0.0):
    return 2 * ((f * t + phase) % 1.0) - 1


def reverb_ir(seconds, damp, seed):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-tt * 6.9 / seconds)
    ir = filt(ir, 'low', damp)
    ir[:int(0.012 * SR)] = 0                               # pre-delay
    return ir / np.sqrt((ir ** 2).sum())


IR_L, IR_R = reverb_ir(2.4, 6000, 1), reverb_ir(2.4, 6000, 2)


def reverb(x):
    return fftconvolve(x, IR_L)[:N], fftconvolve(x, IR_R)[:N]


class Bus:
    def __init__(self):
        self.L = np.zeros(N); self.R = np.zeros(N)

    def add(self, sig, gain=1.0, pan=0.0):
        self.L += sig * gain * np.sqrt(0.5 * (1 - pan))
        self.R += sig * gain * np.sqrt(0.5 * (1 + pan))

    def add_st(self, l, r, gain=1.0):
        self.L += l * gain; self.R += r * gain


dry, wet = Bus(), Bus()                                   # wet bus goes through the reverb

# ---------------------------------------------------------------- sidechain pump (from the kick)
beats = [k * BEAT for k in range(GROOVE_START, DROP)]
pump = np.ones(N)
for bt in beats:
    i0 = int(bt * SR); n = int(BEAT * SR)
    x = np.arange(n) / SR
    pump[i0:i0 + n] = np.minimum(pump[i0:i0 + n], 1 - 0.55 * np.exp(-x / 0.09))

# ---------------------------------------------------------------- harmony
CHORDS = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67], [53, 57, 60, 65], [55, 59, 62, 67]]
BASS = [45, 41, 48, 43, 41, 43]
LOGO_CHORD = [36, 48, 55, 60, 62, 64, 67, 72, 76]


def chord_at(time):
    return CHORDS[min(len(CHORDS) - 1, int(time // BAR))]


# ---------------------------------------------------------------- supersaw pad, filter opening over the phone section
pad_l = np.zeros(N); pad_r = np.zeros(N)
for b, chord in enumerate(CHORDS):
    s, e = b * BAR, (b + 1) * BAR
    gate = np.clip((t - s + 0.15) / 0.3, 0, 1) * np.clip((e + 0.3 - t) / 0.3, 0, 1)
    for n in chord:
        f = midi(n)
        for d, side in ((-0.012, -1), (-0.005, 1), (0.0, 0), (0.006, -1), (0.013, 1)):
            v = saw(f * (1 + d), rng.random()) * gate
            if side <= 0: pad_l += v
            if side >= 0: pad_r += v
cut = 380 + 3200 * np.clip(t / 10.6, 0, 1) ** 1.6
intro = np.clip(t / 1.1, 0, 1) ** 2
outro = np.clip((LOGO + 0.04 - t) / 0.06, 0, 1)
pad_l = sweep_lp(pad_l, cut) * 0.022 * intro * outro * (0.55 + 0.45 * pump)
pad_r = sweep_lp(pad_r, cut) * 0.022 * intro * outro * (0.55 + 0.45 * pump)
dry.add_st(pad_l, pad_r, 0.8)
wet.add_st(pad_l, pad_r, 0.6)

# ---------------------------------------------------------------- drums
kick = np.zeros(N); clap = np.zeros(N); hats = np.zeros(N); shaker = np.zeros(N); ohat = np.zeros(N)
for k, bt in zip(range(GROOVE_START, DROP), beats):
    body = np.sin(2 * np.pi * np.cumsum(48 + 110 * env_at(bt, 0.0005, 0.045, 4)) / SR) * env_at(bt, 0.001, 0.32, 4.5)
    click = filt(noise * env_at(bt, 0.0002, 0.006), 'band', [1500, 6000])
    kick += np.tanh(body * 1.6) + click * 0.35
    if k % 4 in (1, 3):
        snap = filt(noise * (env_at(bt, 0.001, 0.14) + 0.6 * env_at(bt + 0.012, 0.001, 0.12) + 0.4 * env_at(bt + 0.024, 0.001, 0.18)),
                    'band', [800, 5000])
        tone = np.sin(2 * np.pi * 190 * t) * env_at(bt, 0.001, 0.08)
        clap += snap + tone * 0.5
    ohat += env_at(bt + BEAT / 2, 0.002, 0.16) * (k >= 6)
for j in range(GROOVE_START * 4, DROP * 4):
    bt = j * BEAT / 4
    vel = (1.0, 0.45, 0.75, 0.45)[j % 4] * (0.9 + 0.2 * rng.random())
    hats += env_at(bt, 0.0005, 0.035) * vel
    shaker += env_at(bt + 0.01, 0.008, 0.06) * (0.4 + 0.6 * (j % 2))
hats = filt(noise * hats, 'high', 8000)
ohat = filt(noise * ohat, 'high', 6500)
shaker = filt(noise * shaker * (t > 4 * BEAT), 'band', [5000, 11000])
# snare roll into the logo (last bar before the drop accelerates)
roll = np.zeros(N)
for j in range(16):
    bt = (DROP - 4) * BEAT + j * BEAT / 4
    roll += env_at(bt, 0.001, 0.09) * (0.25 + 0.75 * j / 15)
roll = filt(noise * roll, 'band', [600, 4500])
dry.add(kick, 0.42)
dry.add(clap, 0.16, 0.05); wet.add(clap, 0.10)
dry.add(hats, 0.050, 0.3)
dry.add(ohat, 0.030, -0.3)
dry.add(shaker, 0.045, 0.45)
dry.add(roll, 0.10); wet.add(roll, 0.06)

# ---------------------------------------------------------------- bass: sub sine + filtered mid saw, 8ths, sidechained
sub = np.zeros(N); mid = np.zeros(N)
for j in range(GROOVE_START * 2, DROP * 2):
    bt = j * BEAT / 2
    f = midi(BASS[min(5, int(bt // BAR))])
    e = env_at(bt, 0.004, 0.24, 3.0)
    sub += np.sin(2 * np.pi * f * t) * e
    mid += saw(f * 2) * env_at(bt, 0.003, 0.14, 4.0)
bass = sub * 0.9 + sweep_lp(mid, 900, 1.2) * 0.35
dry.add(bass * pump, 0.20)

# ---------------------------------------------------------------- pluck arpeggio (16ths) with dotted-8th ping-pong delay
arp = np.zeros(N)
for j in range(4 * 4, DROP * 4):
    bt = j * BEAT / 4
    ch = chord_at(bt)
    n = ch[[0, 1, 2, 3, 2, 1, 3, 2][j % 8]] + 12
    f = midi(n)
    tone = saw(f) * 0.5 + np.sin(2 * np.pi * f * t) * 0.5
    arp += sweep_lp(tone * env_at(bt, 0.002, 0.16), 2600, 0.9) if False else tone * env_at(bt, 0.002, 0.16)
arp = sweep_lp(arp, 1300 + 3600 * np.clip((t - 2) / 8.6, 0, 1), 0.9) * pump
dly = int(0.75 * BEAT * SR)
arp_l = arp + 0.0 * arp; arp_r = np.zeros(N)
fb = 0.38
for tap in range(1, 5):
    seg = np.zeros(N); seg[tap * dly:] = arp[:N - tap * dly] * fb ** tap
    if tap % 2: arp_r += seg
    else: arp_l += seg
dry.add_st(arp_l, arp_r, 0.030)
wet.add_st(arp_l, arp_r, 0.022)

# ---------------------------------------------------------------- bell hook (FM e-piano-ish), from bar 3
HOOK = [(8, 76, 1), (9.5, 74, 0.5), (10, 72, 1), (11, 69, 1),           # beat, midi, length (beats)
        (12, 71, 1), (13.5, 72, 0.5), (14, 74, 2),
        (16, 72, 1), (17.5, 74, 0.5), (18, 76, 1), (19, 79, 2.5)]
bell = np.zeros(N)
for b0, n, ln in HOOK:
    st = b0 * BEAT
    f = midi(n)
    e = env_at(st, 0.003, ln * BEAT + 0.6, 3.5)
    mod = np.sin(2 * np.pi * f * 3.5 * t) * 1.8 * env_at(st, 0.001, 0.25, 4)
    bell += np.sin(2 * np.pi * f * t + mod) * e
dry.add(bell, 0.040, 0.15)
wet.add(bell, 0.050)

# ---------------------------------------------------------------- transitions: reverse-cymbal swell into the groove, riser into the logo
swell = np.clip((t - 0.1) / 0.9, 0, 1) ** 3 * (t < GROOVE_START * BEAT)
dry.add(filt(noise * swell, 'high', 3000), 0.07)
rise = np.clip((t - 9.8) / (LOGO - 9.8), 0, 1) * (t < LOGO)
riser = sweep_lp(noise * rise ** 2, 400 + 9000 * rise ** 2, 1.4)
tone = np.sin(2 * np.pi * np.cumsum(180 + 720 * rise ** 2.2) / SR) * rise ** 3
dry.add(riser, 0.16); wet.add(riser, 0.12)
dry.add(tone, 0.035); wet.add(tone, 0.03)

# ---------------------------------------------------------------- logo: impact, cymbal, bright chord + shimmer, held and faded
boom = np.tanh(1.5 * np.sin(2 * np.pi * np.cumsum(34 + 70 * env_at(LOGO, 0.001, 0.15)) / SR)) * env_at(LOGO, 0.002, 2.2, 4)
dry.add(boom, 0.45)
cym = filt(noise * env_at(LOGO, 0.001, 2.6, 4), 'high', 4500)
dry.add(cym, 0.06); wet.add(cym, 0.08)
hold = np.clip((t - LOGO) / 0.03, 0, 1) * np.clip((DUR - t) / 1.8, 0, 1)
ch_l = np.zeros(N); ch_r = np.zeros(N)
for n in LOGO_CHORD:
    f = midi(n)
    ch_l += saw(f * 0.995, rng.random()) + saw(f * 1.007, rng.random())
    ch_r += saw(f * 1.005, rng.random()) + saw(f * 0.993, rng.random())
open_ = 1500 + 4500 * np.exp(-np.clip(t - LOGO, 0, None) * 0.9)
ch_l = sweep_lp(ch_l, open_) * hold * 0.014
ch_r = sweep_lp(ch_r, open_) * hold * 0.014
dry.add_st(ch_l, ch_r, 0.9); wet.add_st(ch_l, ch_r, 0.8)
for j, n in enumerate([84, 88, 91, 96, 91, 95, 100]):
    st = LOGO + 0.16 * j
    b = (np.sin(2 * np.pi * midi(n) * t) + 0.3 * np.sin(2 * np.pi * midi(n) * 2.76 * t)) * env_at(st, 0.002, 1.5)
    dry.add(b, 0.028, -0.6 + 0.2 * j); wet.add(b, 0.04)

# ---------------------------------------------------------------- mix + master
rl, rr = reverb(wet.L + wet.R)
L = dry.L + rl * 0.55
R = dry.R + rr * 0.55
mix = np.stack([L, R], 1)
mix = filt(mix.T, 'high', 28).T                              # low-cut rumble
mix[:, :] += filt(mix.T, 'low', 120).T * 0.15                 # a little low-end weight
# glue compression (RMS detector, 2:1 above -16 dBFS), then soft limiting to -1 dBFS peak
rms = np.sqrt(np.convolve((mix ** 2).mean(1), np.ones(2400) / 2400, mode='same')) + 1e-9
level = 20 * np.log10(rms)
gain_db = np.where(level > -16, -(level + 16) * 0.5, 0.0)
mix *= 10 ** (gain_db / 20)[:, None]
mix /= np.abs(mix).max()
mix = np.tanh(mix * 1.5) / np.tanh(1.5)
mix *= 10 ** (-1 / 20) / np.abs(mix).max()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f64le', '-ar', str(SR), '-ac', '2', '-i', '-', sys.argv[1]],
               input=mix.astype(np.float64).tobytes(), check=True)
print(sys.argv[1])
