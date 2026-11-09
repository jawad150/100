"""Soundtrack for BMHC "Tuned In". No music (per the brief): the voice carries through every cut, with the room sound of
each place under it, and the voice is EQ'd as if it is coming out of each radio in turn (full in the studio, warm in
the kitchen, a little tinny in the car, crisp in earbuds). Opening: radio static and whistles as the needle searches,
dawn birds and footsteps; the static clears the moment the voice is found. Gentle pops for the 3D objects.
Long, soft fade after the last word. Master -14 LUFS.
"""
import os, sys
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sqe'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import lp, hp, bp, reverb, SR, bird, chime
from sfx_palette import pop, whoosh, shimmer, tick, key_click, ping, crinkle, thud, clack, knock
import reel_tuned as R

T, DUR, OFF, SH = R.T, R.DUR, R.OFF, R.SH
N = int(SR * DUR)
A.DUR, A.N = DUR, N
sfx = np.zeros((N, 2))
amb = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(5)
ts_ = np.arange(N) / SR


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


def win(a, b, ramp=0.15):
    """0..1 window over [a, b] with soft edges."""
    return np.clip((ts_ - a) / ramp + 0.5, 0, 1) * np.clip((b - ts_) / ramp + 0.5, 0, 1)


noise = rng.normal(0, 1, (N, 2))

# ------------------------------------------------------------------ opening: tuning static + whistles, dawn birds, footsteps
st_env = np.clip(ts_ / 0.3, 0, 1) * np.clip((OFF + 0.05 - ts_) / 0.35, 0, 1)
wob = 0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * ts_) * np.sin(2 * np.pi * 0.7 * ts_)
static = bp(noise, 900, 6500, 2) * 0.05 * (st_env * wob)[:, None]
f = 700 + 900 * np.abs(np.sin(2 * np.pi * 0.45 * ts_)) + 500 * np.sin(2 * np.pi * 1.7 * ts_)
whistle = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.012 * st_env
sfx += static + np.stack([whistle, whistle], 1)
for k in range(6):
    add(amb, rng.uniform(0.1, SH['walk'][1] - 0.3), bird(rng.uniform(0.03, 0.06)), pan=rng.uniform(-0.6, 0.6))
for k, tf in enumerate(np.arange(0.35, SH['walk'][1], 0.52)):
    add(sfx, tf, thud(0.07, 140 + 10 * (k % 2)), pan=(-0.15 if k % 2 else 0.15))
    add(sfx, tf + 0.01, crinkle(0.05, 0.03))

# ------------------------------------------------------------------ room sound under each place
a, b = SH['studio']
amb += lp(noise, 220, 2) * 0.008 * win(a, b)[:, None]
a, b = SH['map']
amb += lp(noise, 300, 2) * 0.006 * win(a, b)[:, None]
a, b = SH['radio'][0], SH['tea'][1]                                         # kitchen: kettle simmer rising
kettle = bp(noise, 2500, 7000, 2) * (0.004 + 0.006 * np.clip((ts_ - a) / 3.0, 0, 1))[:, None]
amb += kettle * win(a, b)[:, None]
for k in range(3):
    add(amb, a + 0.4 + k * 1.1, bird(0.025), pan=0.6)
a, b = SH['car']                                                            # rain on the windscreen + indicator
rain = lp(noise, 2200, 2) * 0.03 * win(a, b)[:, None]
amb += rain
for k in range(40):
    add(amb, rng.uniform(a, b), tick(rng.uniform(0.02, 0.05)), pan=rng.uniform(-0.8, 0.8))
for k, ti in enumerate(np.arange(a + 0.3, b - 0.1, 0.42)):
    add(sfx, ti, key_click(0.05 if k % 2 == 0 else 0.035), pan=-0.4)
a, b = SH['walk2']                                                          # city air
amb += lp(noise, 900, 2) * 0.01 * win(a, b)[:, None]
a, b = SH['bus']                                                            # bus hum
amb += (lp(noise, 160, 2) * 0.03 + np.sin(2 * np.pi * 58 * ts_)[:, None] * 0.004) * win(a, b)[:, None]
a, b = SH['trip']
amb += lp(noise, 600, 2) * 0.008 * win(a, b)[:, None]
a, b = SH['pod']
amb += lp(noise, 350, 2) * 0.006 * win(a, b)[:, None]
a, b = SH['dusk']                                                           # evening hush, a distant bird
amb += lp(noise, 400, 2) * 0.007 * win(a, b)[:, None]
add(amb, a + 1.2, bird(0.02), pan=-0.5)
add(amb, a + 2.4, bird(0.018), pan=0.5)

# ------------------------------------------------------------------ transitions
for nm in R.ORDER[1:]:
    kind, td = R.TRANS[nm]
    t0 = SH[nm][0] - td / 2
    if kind is R.tr_static:
        add(sfx, t0, bp(rng.normal(0, 1, int(td * SR)), 800, 7000, 2) * 0.06 * np.hanning(int(td * SR)))
    elif kind in (R.tr_ring, R.tr_ring_in):
        add(sfx, t0, whoosh(td + 0.2, 250, 3000, 0.07, rev=(kind is R.tr_ring_in)))
        add(sfx, t0 + td * 0.4, shimmer(0.8, 0.04, 86))
    elif kind is R.tr_flash:
        add(sfx, t0 + td / 2 - 0.05, shimmer(0.6, 0.05, 90))
    elif kind is R.tr_needle:
        add(sfx, t0, whoosh(td + 0.1, 400, 5000, 0.07))
        add(sfx, t0 + td * 0.5, tick(0.06))
    else:
        add(sfx, t0 - 0.05, whoosh(td + 0.15, 260, 6000, 0.09), pan=0.2)

# ------------------------------------------------------------------ SFX on the words
add(sfx, T['room'] - 0.1, key_click(0.2))                                  # ON AIR switches on
add(sfx, T['room'] - 0.05, pop(0.18, 700))
add(sfx, T['Whalley'], pop(0.18, 820))
for k in range(8):                                                          # neighbourhoods light up as the rings pass
    add(sfx, T['to'] + 0.4 + k * 0.32, ping(0.018, 1400 + 120 * (k % 4)), pan=rng.uniform(-0.6, 0.6))
add(sfx, T['Manchester'], pop(0.22, 760))
add(sfx, SH['radio'][0] + 0.15, key_click(0.16))                           # the radio switch
add(sfx, SH['radio'][0] + 0.18, bp(rng.normal(0, 1, int(0.25 * SR)), 800, 6000, 2) * 0.03 * np.hanning(int(0.25 * SR)))
add(sfx, T['faith'], pop(0.2, 700))
add(sfx, T['tea'], pop(0.18, 820))
add(sfx, T['tea'] + 0.25, ping(0.05, 2637), pan=0.3)                       # spoon on the cup
add(sfx, T['tea'] + 0.38, ping(0.03, 3136), pan=0.3)
add(sfx, T['Community'], pop(0.2, 760))
add(sfx, T['Community'] + 0.05, crinkle(0.2, 0.08))
for k in range(5):                                                          # dashboard digits tune up to 90.6
    add(sfx, T['way'] - 0.15 + k * 0.1, tick(0.04))
add(sfx, T['work'] + 0.1, ping(0.04, 1760))
add(sfx, T['wellbeing'], pop(0.2, 800))
add(sfx, T['family'], pop(0.16, 640))
add(sfx, T['conversations'], pop(0.2, 900))
add(sfx, SH['trip'][0] + 0.05, ping(0.05, 2093), pan=0.3)                  # shop bell
add(sfx, SH['trip'][0] + 0.12, ping(0.04, 2637), pan=0.3)
for k in range(3):
    add(sfx, SH['trip'][0] + k * 0.22, whoosh(0.35, 400, 4000, 0.04), pan=(0.4 if k % 2 == 0 else -0.4))
add(sfx, T['you'], pop(0.18, 700))
add(sfx, T['are'], pop(0.18, 880))
add(sfx, T['podcast'], pop(0.2, 760))
add(sfx, T['podcast'] + 0.3, key_click(0.1))
for k, key in enumerate(('inform', 'inspire', 'elevate')):
    add(sfx, T[key], pop(0.16, 700 + 120 * k))
add(sfx, T['elevate'] + 0.05, shimmer(0.9, 0.06, 88))
add(sfx, SH['dial'][0], whoosh(0.8, 300, 2500, 0.05))                      # the dial sweeps
add(sfx, T['ninety'] - 0.05, pop(0.24, 820))                               # 90.6 locks
add(sfx, T['ninety'], chime(84, 0.12, 2.2))
add(sfx, T['DAB'], pop(0.14, 700))
add(sfx, T['free'], pop(0.2, 900))
add(sfx, T['free'] + 0.7, shimmer(0.9, 0.05, 91))
add(sfx, T['app'], pop(0.16, 760))
add(sfx, T['app'] + 0.6, chime(91, 0.07, 2.4))
sfx = reverb(sfx, wet=0.1, length=0.7, key='room')

# ------------------------------------------------------------------ voice, EQ'd to each radio in turn
x, sr = sf.read(f'{R.S}/tts/vo.wav')
if x.ndim > 1:
    x = x.mean(1)
if sr != SR:
    x = signal.resample_poly(x, SR, sr)
x = hp(x, 70, 2)
x = x / max(1e-6, np.abs(x).max()) * 0.9
v = np.zeros(N)
i0 = int(OFF * SR)
n = min(len(x), N - i0)
v[i0:i0 + n] = x[:n]
full = v + 0.05 * bp(v, 2500, 6000, 2)
warm = lp(v, 5200, 2) + 0.15 * lp(v, 300, 2)                               # kitchen radio
tinny = bp(v, 380, 3800, 2) * 1.5                                          # car speaker
crisp = hp(v, 140, 2) + 0.12 * bp(v, 3000, 8000, 2)                        # earbuds
wk = win(SH['radio'][0], SH['tea'][1], 0.25) * 0.55
wt = win(SH['car'][0], SH['car'][1], 0.25) * 0.45
wc = win(SH['walk2'][0], SH['pod'][1], 0.25) * 0.5
wf = 1 - wk - wt - wc
mono = full * wf + warm * wk + tinny * wt + crisp * wc
vo = np.stack([mono, mono], 1)
vo = reverb(vo, wet=0.03, length=0.4, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.3 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = sfx * 0.95 * (1 - 0.3 * lvl)[:, None] + amb * (1 - 0.35 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
vo_end = T['end'] + 0.35
nf = int(max(1.6, DUR - vo_end) * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav', 'DUR', DUR, 'fade from', round(DUR - nf / SR, 2))
