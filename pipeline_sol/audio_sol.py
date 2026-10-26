"""Soundtrack for IC London "Why do you want to be a solicitor?": a modern, confident corporate score (B minor -> D,
116 bpm) that starts as a tense pulse under the interview question, builds with a plucked synth, felt piano, strings
and a clean beat through the three points, and resolves on a bright brand chord for the logo. Every animation has a
designed sound: typing, message pops, the TOO GENERIC stamp, blueprint drawing, pieces locking in, sonar target pings,
stone courses landing, rising career-path zips, the emblem snapping together and a logo hit.
Clear male voiceover on top, ducked bed, gentle fade-out.
"""
import os, sys
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import audio_of as A
from audio_of import (piano, pad, bass, kick, shaker, snap, chime, whoosh, riser, boom, pop, tick, key_click, shimmer,
                      lp, hp, bp, reverb, SR, tt)
import reel_sol as R

T, VO, ph = R.T, R.VO, R.ph
DUR = R.DUR
N = int(SR * DUR)
A.DUR, A.N = DUR, N
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
vo = np.zeros((N, 2))
rng = np.random.default_rng(36)
mtof = A.mtof


def add(buf, t0, x, gain=1.0, pan=0.0):
    if 0 <= t0 < DUR:
        A.add(buf, t0, x, gain, pan)


# ------------------------------------------------------------------ instruments
def pluck(m, dur=0.5, vel=0.2, bright=1.0):
    t = tt(dur + 0.3)
    f = mtof(m)
    x = np.zeros_like(t)
    for k in range(1, 14):
        if f * k > 12000:
            break
        x += (1 / k) * np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6)) * np.exp(-t * (4 + k * 3.2 / bright))
    x *= np.minimum(1, t / 0.003) * np.where(t > dur, np.exp(-(t - dur) * 12), 1)
    return x * vel


def sub(m, dur, vel=0.3):
    t = tt(dur)
    x = np.tanh(1.6 * np.sin(2 * np.pi * mtof(m) * t))
    return x * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.08).clip(0, 1) * vel


def hat(vel=0.06, open_=False):
    t = tt(0.25 if open_ else 0.06)
    return hp(rng.normal(0, 1, len(t)), 7000) * np.exp(-t * (18 if open_ else 90)) * vel


def clap(vel=0.12):
    out = np.zeros(int(0.3 * SR))
    for d in (0.0, 0.009, 0.019):
        t = tt(0.25)
        x = bp(rng.normal(0, 1, len(t)), 900, 6000) * np.exp(-t * 30)
        out[int(d * SR):int(d * SR) + len(x)] += x * (0.6 if d else 1.0)
    return out * vel


def strings(ms, dur, vel=0.1, att=0.6, bright=2600):
    t = tt(dur + 0.6)
    x = np.zeros_like(t)
    for m in ms:
        for d in (-0.08, 0.0, 0.07):
            f = mtof(m + d) * (1 + 0.003 * np.sin(2 * np.pi * 5 * t + rng.uniform(0, 6)))
            x += signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    x = lp(x, bright, 2) / (3 * len(ms))
    return x * np.minimum(1, t / att) * np.where(t > dur, np.exp(-(t - dur) * 4), 1) * vel


# ------------------------------------------------------------------ SFX
def thud(vel=0.5, f=70):
    t = tt(0.5)
    body = np.sin(2 * np.pi * (f + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
    click = hp(rng.normal(0, 1, len(t)), 1500) * np.exp(-t * 120) * 0.4
    return (body + click) * vel


def clack(vel=0.4):
    t = tt(0.25)
    x = bp(rng.normal(0, 1, len(t)), 1200, 5000) * np.exp(-t * 70) + np.sin(2 * np.pi * 820 * t) * np.exp(-t * 40) * 0.5
    return x * vel


def bonk(vel=0.3):
    out = np.zeros(int(0.5 * SR))
    for d, f in ((0.0, 420), (0.14, 300)):
        t = tt(0.3)
        x = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)
        x = lp(x, 2000) * np.exp(-t * 12)
        out[int(d * SR):int(d * SR) + len(x)] += x
    return out * vel


def ping(vel=0.15, f=1320):
    t = tt(1.2)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 5) * np.minimum(1, t / 0.003) * vel


def zip_up(vel=0.15, f0=300, f1=1400, dur=0.45):
    t = tt(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) ** 2 * vel


def scribble(dur=1.0, vel=0.1):
    t = tt(dur)
    n = bp(rng.normal(0, 1, len(t)), 2500, 7000)
    am = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * t + 3 * np.sin(2 * np.pi * 1.3 * t)))
    return n * am * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.1) * vel


# ------------------------------------------------------------------ music: bright dance-pop groove (A major, 128 bpm)
# piano offbeat stabs, octave-bouncing bass, a catchy pulse-synth hook, four-on-the-floor kick, open hats, claps,
# sidechain pump. Muffled (low-passed) under the interview hook, full drop at "build your answer", breakdown for the
# strong answer, big bright chord on the logo.
LOGO_T = ph('cta', 1) + 0.6
BPM = 128
B = 60 / BPM
BAR = 4 * B
CH = [(45, [69, 73, 76]), (40, [68, 71, 76]), (42, [69, 73, 78]), (38, [69, 74, 78])]      # A  E  F#m  D
HOOK = [76, 78, 81, 78, 76, 73, 76, None, 74, 76, 78, 76, 73, 71, 73, None]               # 8ths over 2 bars


def pulse(m, dur, vel=0.1, width=0.3):
    t = tt(dur + 0.15)
    f = mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.15))
    ph_ = np.cumsum(f) / SR % 1.0
    x = np.where(ph_ < width, 1.0, -1.0) - (2 * width - 1)
    x = lp(x, 3800, 2)
    return x * np.minimum(1, t / 0.008) * np.where(t > dur, np.exp(-(t - dur) * 30), 1) * vel


def stab(ms, vel=0.12):
    out = None
    for m in ms:
        x = piano(m, 0.22, vel)
        out = x if out is None else out[:len(x)] + x[:len(out)]
    return out


def open_hat(vel=0.06):
    return hat(vel, open_=True)


D0 = R.T['hook'] + 0.15                   # groove start
DROP = ph('three', 0) - 0.05              # full drop
BREAK0 = T['cta'] - 0.05                  # breakdown under the emblem snap
groove = np.zeros((N, 2))
bi = 0
while True:
    t0 = D0 + bi * BAR
    if t0 >= BREAK0:
        break
    root, tones = CH[bi % 4]
    full = t0 >= DROP - 0.1
    for q in range(4):
        tb = t0 + q * B
        if tb >= BREAK0:
            break
        add(groove, tb, kick(0.26 if full else 0.2))
        add(groove, tb + B / 2, open_hat(0.05 if full else 0.035), pan=0.3)
        add(groove, tb + B / 2, stab([m for m in tones], 0.09 if full else 0.07), pan=-0.15)       # offbeat piano
        add(groove, tb + B / 2, bass(root + (24 if q % 2 else 12), B * 0.45, 0.16 if full else 0.12))   # octave bounce
        if q % 2 == 1:
            add(groove, tb, clap(0.12 if full else 0.08), pan=0.05)
        if full:
            add(groove, tb + B / 4, hat(0.022), pan=0.4)
            add(groove, tb + 3 * B / 4, hat(0.022), pan=0.4)
    if full and t0 >= T['motiv'] - 0.2:                      # the synth hook from the first point onward
        for j, m in enumerate(HOOK[(bi % 2) * 8:(bi % 2) * 8 + 8]):
            if m is not None:
                add(groove, t0 + j * B / 2, pulse(m, B * 0.42, 0.075), pan=0.2)
    if full:
        add(groove, t0, strings([tones[0], tones[1] + 12, tones[2]], BAR, vel=0.05, att=0.3, bright=2400))
    bi += 1
# sidechain pump: duck the groove (except kicks) after each beat
tt_ = np.arange(N) / SR
ph_b = ((tt_ - D0) % B) / B
pump = np.where(tt_ > D0, 0.55 + 0.45 * np.clip(ph_b / 0.45, 0, 1) ** 0.6, 1.0)
groove *= pump[:, None]
# muffled (low-passed) under the hook, opening up into the drop
filt = lp(groove, 900, 2)
mixk = np.clip((tt_ - (DROP - 1.2)) / 1.2, 0, 1)[:, None]
music += filt * (1 - mixk) * 1.3 + groove * mixk
add(music, DROP - 1.0, riser(1.0, 0.22))
add(music, DROP, boom(0.5))
for tc in [T['motiv'], T['exp'], T['goals']]:
    for j in range(8):
        add(music, tc - 0.5 + j * 0.0625, clap(0.03 + 0.01 * j), pan=-0.1)       # clap roll into each point
    add(music, tc - 0.8, riser(0.8, 0.15))
    add(music, tc, boom(0.3))
# breakdown: piano chords + strings while the emblem snaps; then the bright logo chord
add(music, BREAK0, strings([69, 73, 76, 81], 2.4, vel=0.1, att=0.2, bright=3000))
for j in range(4):
    add(music, BREAK0 + j * B * 2, stab([69, 73, 76], 0.1), pan=-0.1)
add(music, BREAK0, bass(45 + 12, 2.0, 0.14))
add(music, LOGO_T, strings([69, 73, 76, 81, 85], DUR - LOGO_T, vel=0.13, att=0.1, bright=3800))
add(music, LOGO_T, bass(45 + 12, DUR - LOGO_T, 0.15))
add(music, LOGO_T, kick(0.32))
add(music, LOGO_T, boom(0.3))
for j, m in enumerate([81, 85, 88, 93]):
    add(music, LOGO_T + j * 0.06, piano(m, 2.4, 0.13), pan=-0.3 + 0.2 * j)
    add(music, LOGO_T + 0.3 + j * 0.12, pulse(m + 12, 0.18, 0.04), pan=0.3 - 0.2 * j)
music = reverb(music, wet=0.2, length=1.8, key='hall')

# ------------------------------------------------------------------ SFX palette v2 (modern UI / tech sound design)
# Redefined here so the music above keeps its own instruments; everything below uses these.
def pop(vel=0.3, f=900):
    """Bubbly UI blip: fast upward chirp with a soft body."""
    t = tt(0.16)
    fr = f * 0.7 * (1 + 1.2 * (1 - np.exp(-t * 60)))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 26)
    return (x + 0.25 * np.sin(4 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 40)) * np.minimum(1, t / 0.002) * vel


def whoosh(dur=0.5, f0=300, f1=3500, vel=0.5, rev=False):
    """Reverse-swell swish: filtered noise that swells in, with a faint tonal sweep."""
    t = tt(dur)
    k = t / dur
    env = (k ** 2.2) * np.exp(-((k - 0.85) / 0.25) ** 2 * (k > 0.85))
    noise = rng.normal(0, 1, len(t))
    fa, fb = sorted((f0, f1))
    lo = bp(noise, max(80, fa * 0.6), min(16000, fb * 1.2), 2)
    f = f0 * (f1 / max(1, f0)) ** k
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    x = (lo + tone) * env
    return np.stack([x, np.roll(x, 90)], 1) * vel


def boom(vel=0.5):
    """Punchy sub-drop impact."""
    t = tt(1.1)
    f = 40 + 90 * np.exp(-t * 14)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    crack = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 70) * 0.5
    return np.tanh((sub + crack) * 1.4) * vel


def thud(vel=0.5, f=70):
    t = tt(0.45)
    fr = f * 0.8 + f * 1.6 * np.exp(-t * 40)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 11)
    snap_ = bp(rng.normal(0, 1, len(t)), 2000, 9000) * np.exp(-t * 160) * 0.5
    return (body + snap_) * vel


def shimmer(dur=0.9, vel=0.3, base=84):
    """Glassy FM bell sparkle arpeggio."""
    out = np.zeros(int((dur + 0.8) * SR))
    for j, iv in enumerate([0, 7, 12, 16, 19]):
        t = tt(dur + 0.6)
        f = mtof(base + iv)
        x = np.sin(2 * np.pi * f * t + 1.8 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 6)) * np.exp(-t * 4.5)
        i = int(j * 0.045 * SR)
        out[i:i + len(x)] += x[:len(out) - i] * (0.9 ** j)
    return out * vel * 0.5


def tick(vel=0.3):
    t = tt(0.03)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 400) * vel + hp(rng.normal(0, 1, len(t)), 6000) * np.exp(-t * 500) * vel * 0.5


def key_click(vel=0.18):
    """Mechanical keyboard clack: switch tick + key bottoming out."""
    out = np.zeros(int(0.08 * SR))
    for d, f, a in ((0.0, 4200, 1.0), (0.018, 1400, 0.7)):
        t = tt(0.05)
        x = bp(rng.normal(0, 1, len(t)), f * 0.6, min(15000, f * 1.6), 2) * np.exp(-t * 220) * a
        i = int(d * SR)
        out[i:i + len(x)] += x[:len(out) - i]
    return out * vel * 1.4


def clack(vel=0.4):
    t = tt(0.18)
    return (np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 60) * 0.6 + bp(rng.normal(0, 1, len(t)), 3000, 10000) * np.exp(-t * 120)) * vel


def ping(vel=0.15, f=1320):
    """FM bell plink for the target rings."""
    t = tt(1.0)
    return np.sin(2 * np.pi * f * 0.75 * t + 2.5 * np.sin(2 * np.pi * f * 1.4 * t) * np.exp(-t * 8)) * np.exp(-t * 6) * vel


def zip_up(vel=0.15, f0=300, f1=1400, dur=0.45):
    """Laser rise: detuned saw sweep."""
    t = tt(dur)
    f = f0 * (f1 / f0) ** ((t / dur) ** 1.4)
    x = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + signal.sawtooth(2 * np.pi * np.cumsum(f * 1.01) / SR)
    return lp(x, 5000, 2) * np.sin(np.pi * t / dur) ** 1.5 * vel * 0.5


def scribble(dur=1.0, vel=0.1):
    """Felt-tip writing: short scratchy strokes."""
    t = tt(dur)
    n = bp(rng.normal(0, 1, len(t)), 3000, 9000)
    strokes = (np.sin(2 * np.pi * 5.5 * t + 2 * np.sin(2 * np.pi * 1.7 * t)) > -0.2).astype(float)
    strokes = np.convolve(strokes, np.ones(400) / 400, mode='same')
    return n * strokes * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.08).clip(0, 1) * vel


def squeak(dur=0.3, vel=0.12):
    """Marker swipe."""
    t = tt(dur)
    f = 1800 + 2600 * t / dur
    return bp(rng.normal(0, 1, len(t)), 1500, 8000) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR / 40)) * np.sin(np.pi * t / dur) * vel * 1.3


def crinkle(dur=0.35, vel=0.3):
    out = np.zeros(int(dur * SR) + 4000)
    for _ in range(26):
        t = tt(0.02)
        x = bp(rng.normal(0, 1, len(t)), 2500, 11000) * np.exp(-t * 300)
        i = int(rng.uniform(0, dur) * SR)
        out[i:i + len(x)] += x * rng.uniform(0.4, 1.0)
    return out * vel


def clang(vel=0.35):
    """Tin-can clank."""
    t = tt(0.9)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((780, 1, 6), (1910, 0.7, 9), (3020, 0.5, 12), (4470, 0.3, 16)))
    return (x + bp(rng.normal(0, 1, len(t)), 1000, 6000) * np.exp(-t * 50) * 0.8) * vel


def knock(vel=0.3):
    """Snappy click for the signs."""
    t = tt(0.12)
    return (np.sin(2 * np.pi * 900 * t) * np.exp(-t * 70) + hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 150) * 0.6) * vel


def bonk(vel=0.3):
    """Wrong-answer buzz: two detuned square blips falling."""
    out = np.zeros(int(0.45 * SR))
    for d, f in ((0.0, 330), (0.15, 233)):
        t = tt(0.22)
        x = np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.012 * t))
        x = lp(x, 1800) * np.exp(-t * 9) * 0.5
        out[int(d * SR):int(d * SR) + len(x)] += x
    return out * vel


def slam(vel=0.6):
    """Rubber-stamp slam: impact + metallic ring."""
    t = tt(0.8)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dd) * a for f, a, dd in ((410, 0.5, 7), (1130, 0.3, 10)))
    return boom(1.0)[:len(t)] * vel + ring * vel * 0.4


# ------------------------------------------------------------------ SFX timeline
add(sfx, 0.1, pop(0.18, 900))                                         # chip
add(sfx, 0.35, pop(0.3, 520))                                         # 3D question mark pops
add(sfx, 0.35, whoosh(0.3, 600, 5000, 0.12))
add(sfx, 0.3, whoosh(0.5, 300, 4000, 0.18))                           # chat card slides up
for k in range(6):
    add(sfx, 0.78 + k * 0.05, key_click(0.05), pan=-0.3)             # typing dots
add(sfx, 1.05, pop(0.22, 700))                                        # question arrives
for k in range(11):
    add(sfx, 1.3 + k * 0.055, key_click(0.1), pan=0.2)               # typing "I love law."
add(sfx, 2.25, whoosh(0.18, 2000, 8000, 0.12))                        # send
add(sfx, 2.27, pop(0.2, 950))
add(sfx, ph('hook', 1) + 0.3, bonk(0.28))                             # wrong answer buzz
for i, (x, y, rot, d, sp, sc) in enumerate(R.COPIES):                 # everyone says the same thing
    add(sfx, T['generic'] + 0.05 + d * 1.1, pop(0.07, 600 + (i * 53) % 700), pan=(x - 540) / 700)
st = ph('generic', 0) + 0.65
add(sfx, st, slam(0.6))                                               # TOO GENERIC stamp
add(sfx, st, thud(0.5, 60))
fall0 = R.FALL0
add(sfx, fall0, whoosh(0.7, 3000, 200, 0.2))                          # bubbles fall away
for k in range(10):
    add(sfx, fall0 + 0.25 + rng.uniform(0, 0.5), tick(0.1), pan=rng.uniform(-0.7, 0.7))
add(sfx, T['three'] + 0.15, scribble(1.05, 0.08))                     # blueprint draws itself
add(sfx, T['three'] + 0.15, zip_up(0.05, 200, 900, 1.05))
for j in range(3):
    add(sfx, T['three'] + 1.2 + j * 0.2, tick(0.18))                  # labels
    t_fly = T['three'] + 0.85 + (4 + 7 * j) / 24
    add(sfx, t_fly, whoosh(0.4, 400, 3000, 0.16), pan=[-0.5, 0.5, 0][j])
    add(sfx, t_fly + 0.6, clack(0.25))
add(sfx, T['motiv'] - 0.2, shimmer(0.9, 0.16, 88))                    # circle iris
add(sfx, T['motiv'] - 0.25, whoosh(0.5, 500, 6000, 0.18))
add(sfx, ph('motiv', 0), pop(0.18, 800))
for k in range(4):
    add(sfx, T['motiv'] + 0.6 + k * 1.43, ping(0.1, 1320))             # target sonar
add(sfx, T['motiv'] + 0.55, tick(0.15))
add(sfx, ph('motiv', 2) + 0.1, pop(0.2, 600))                         # idea bulb appears...
add(sfx, ph('motiv', 2) + 0.1 + 14 / 24, key_click(0.25))             # ...and switches on
add(sfx, ph('motiv', 2) + 0.12 + 14 / 24, chime(91, 0.12, 1.4))
add(sfx, T['exp'] - 0.27, whoosh(0.55, 150, 2500, 0.24))              # navy base wipe
add(sfx, ph('exp', 0), pop(0.18, 800))
for k in range(4):                                                    # foundation courses land
    land = R.exp_seq0() + (8 + 18 * k + 9) / 24
    add(sfx, land, thud(0.45, 55 + 6 * k))
    add(sfx, land + 0.02, clack(0.12))
    add(sfx, land + 0.08, tick(0.12))
add(sfx, ph('exp', 3) - 0.1, zip_up(0.1, 400, 1200, 0.6))             # lines converge
add(sfx, ph('exp', 3) + 0.3, pop(0.26, 900))
add(sfx, T['goals'] - 0.25, whoosh(0.5, 200, 5000, 0.22))             # spire wipe
add(sfx, ph('goals', 0), pop(0.18, 800))
add(sfx, ph('goals', 3), shimmer(1.0, 0.16, 90))
add(sfx, T['cta'] - 0.25, whoosh(0.5, 300, 6000, 0.24))               # red square zoom
add(sfx, T['cta'], boom(0.3))
for j in range(3):
    sn = T['cta'] + (6 + 9 * j + 12) / 24
    add(sfx, sn, clack(0.35))
    add(sfx, sn, thud(0.25, 90))
    add(sfx, sn + 0.05, pop(0.16, 900 + 100 * j))
add(sfx, T['cta'] + 1.9, shimmer(0.8, 0.14, 92))                     # light sweep
add(sfx, ph('cta', 1) + 0.2, whoosh(0.6, 200, 3000, 0.16))            # card rises
add(sfx, LOGO_T, shimmer(1.4, 0.2, 86))
add(sfx, ph('cta', 1) + 0.8, pop(0.22, 700))                          # graduation cap
add(sfx, ph('cta', 1) + 1.3, whoosh(0.4, 1500, 7000, 0.1))            # underline swish

def squeak(dur=0.3, vel=0.12):
    t = tt(dur)
    f = 2200 + 500 * np.sin(2 * np.pi * 9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * bp(rng.normal(0, 1, len(t)), 1500, 6000) * 0.5 * np.sin(np.pi * t / dur) * vel + \
        bp(rng.normal(0, 1, len(t)), 2000, 7000) * np.sin(np.pi * t / dur) * vel * 0.6


def crinkle(dur=0.35, vel=0.3):
    t = tt(dur)
    n = hp(rng.normal(0, 1, len(t)), 1500)
    gate = (rng.random(len(t)) < 0.02).astype(float)
    gate = np.convolve(gate, np.exp(-np.arange(200) / 30), mode='same')
    return n * np.clip(gate, 0, 1) * np.sin(np.pi * t / dur) * vel


def clang(vel=0.35):
    t = tt(1.4)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((520, 1, 3.5), (1340, 0.6, 5), (2210, 0.4, 7), (3170, 0.25, 9)))
    return (x + hp(rng.normal(0, 1, len(t)), 2000) * np.exp(-t * 60) * 0.5) * vel


def knock(vel=0.3):
    t = tt(0.2)
    return (np.sin(2 * np.pi * 240 * t) * np.exp(-t * 35) + bp(rng.normal(0, 1, len(t)), 600, 2500) * np.exp(-t * 60) * 0.4) * vel


for j in range(2):                                              # red X marker strokes
    add(sfx, R.X0 + j * 0.17, squeak(0.18, 0.14), pan=-0.2 + 0.4 * j)
add(sfx, R.X0 + 0.32, pop(0.22, 500))                           # "Too generic" pill
add(sfx, R.CR0, crinkle(0.32, 0.35))                            # crumple
add(sfx, R.BIN0 - 0.35, whoosh(0.4, 200, 2500, 0.15))           # bin slides up
add(sfx, R.BIN0, whoosh(0.5, 900, 3500, 0.16))                  # toss
add(sfx, R.BIN0 + 1.0, clang(0.32))                             # into the bin
add(sfx, R.BIN0 + 1.0, thud(0.25, 80))
add(sfx, ph('motiv', 2) + 0.6, thud(0.2, 140))                  # sticky note slaps on
add(sfx, ph('motiv', 2) + 0.9, scribble(1.3, 0.07))             # pen writing
for j in range(3):                                              # signpost boards swing in
    tj = R.sign_t0() + (8 + 18 * j + 8) / 24
    add(sfx, tj, knock(0.3), pan=0.3 if j != 1 else -0.3)
    add(sfx, tj, pop(0.15, 700 + 120 * j))
add(sfx, ph('goals', 3) - 0.6, zip_up(0.14, 250, 1600, 1.0))    # growth arrow rises
add(sfx, ph('goals', 3) + 0.4, pop(0.24, 950))
add(sfx, ph('cta', 1) + 1.8, pop(0.22, 820))                    # red arrow button
add(sfx, T['generic'] - 0.2, whoosh(0.4, 400, 7000, 0.22))      # whip pans
add(sfx, T['three'] - 0.2, whoosh(0.4, 400, 7000, 0.22))
sfx = reverb(sfx, wet=0.12, length=0.9, key='room')

# ------------------------------------------------------------------ voiceover
LINES = f'{R.S}/tts/lines'


def vo_chain(x, sr):
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    x = hp(x, 75, 2)
    x = x + 0.18 * bp(x, 2500, 6000, 2)            # presence / clarity
    x = x + 0.06 * bp(x, 120, 280, 2)
    x = lp(x, 12000, 2)
    env = np.sqrt(lp(x ** 2, 12, 1).clip(1e-9))
    thr = 0.22 * env.max()
    gain = np.where(env > thr, (thr + (env - thr) / 2.8) / np.maximum(env, 1e-9), 1.0)
    x = x * gain
    return x / max(1e-6, np.abs(x).max()) * 0.9


for name in R.ORDER:
    x, sr = sf.read(f'{LINES}/{name}.wav')
    add(vo, VO[name], vo_chain(x, sr), 1.0)
vo = reverb(vo, wet=0.05, length=0.7, key='vo_room')

env = np.abs(vo).max(axis=1)
rel = int(0.35 * SR)
smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
lvl = np.clip(smooth / (smooth.max() + 1e-9) * 4.0, 0, 1)
bed = music * 0.95 * (1 - 0.6 * lvl)[:, None] + sfx * 0.95 * (1 - 0.3 * lvl)[:, None]
mix = bed + vo * 1.5
mix = np.tanh(mix * 1.05) / 1.05
fade = np.ones(N)
nf = int(R.FADE * SR)
fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2
fade[:int(0.03 * SR)] = np.linspace(0, 1, int(0.03 * SR))
mix *= fade[:, None]
mix /= max(1e-6, np.abs(mix).max()) / 0.89
os.makedirs(f'{R.S}/audio', exist_ok=True)
wavfile.write(f'{R.S}/audio/music_stem.wav', SR, (music / max(1e-6, np.abs(music).max()) * 0.9 * 32767).astype(np.int16))
wavfile.write(f'{R.S}/audio/mix_raw.wav', SR, (mix * 32767).astype(np.int16))
print('wrote', f'{R.S}/audio/mix_raw.wav')
