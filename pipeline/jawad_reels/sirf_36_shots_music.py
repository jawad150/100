#!/usr/bin/env python3
"""sirf_36_shots_music.py: ORIGINAL music bed of Bijli series #3 "Sirf 36 Shots" (@jawad_mp4). Owner: music-supervisor.

Plan: brand_reels/design/reels/sirf_36_shots/SHOTS.md section (B) + BRIEF.md section 2; notes: .../sirf_36_shots/SOUND.md.
Procedural and deterministic (fixed seeds, numpy/scipy only): a felt upright piano, a round upright-style bass, a brushed
lo-fi kit, a santoor-like hammered shimmer, a cold filtered synth pulse and vinyl crackle are synthesised here; the kick,
hat, clap and pad voices come from the house kit epic_music.py (EM.kick / EM.hat / EM.clap / EM.pad_chord). No sample of
any song, no AI model, no trending audio. Licence: original work made for @jawad_mp4.

Grid: 120 BPM = 15 frames per beat at 30 fps, bar = 60 f = 2.0 s, 18 bars = 36.000 s = 1,080 f = 1,728,000 samples.
Key D minor. Chords per bar (repeating): Dm9 - Bbmaj7 - F/A - C (bar n -> PROG[n % 4]).

    f0-59     bar 0      HOOK: felt piano motif D4 F4 A4 C5 on the four beats, tape wow 0.3 %, crackle; nothing else
    f60-479   bars 1-7   PAST (half-time, 60 BPM feel): soft kick on 1 (+ ghost on 2&), brushed snare on 3, upright bass,
                         piano chords (1, 2&, 3&), santoor shimmer on every bar start, crackle. The kit enters on the
                         flash (f60). STOP f375-f389 (exact digital silence: one beat for the thumb joke), back on f390
    f480-779  bars 8-12  PRESENT (full time): same chords re-voiced cold, synth pulse on 8ths whose low-pass opens
                         350 Hz -> 4.2 kHz over the 5 bars, kick on every beat, closed hats on 8ths (open on 4&), soft
                         clap on 2 and 4, sub bass on quarters (sidechained to the kick). Build f750-f779: snare roll
                         16ths -> 32nds, pulse in 16ths. (The noise riser is the SFX jd_riser: one riser, no doubling)
    f772-780  tape stop  the whole music bus slows to a halt (varispeed (1 - u)^1.6) into the freeze
    f780-809  DROP-OUT   exact digital silence (gate after the reverbs; 64-sample ramps sit before f780 and f810)
    f810-899  PAYOFF     piano Bbmaj7(9) fortissimo (Bb1 F2 Bb2 | D4 F4 A4 C5) + sub swell on Bb1 + warm pad + santoor
                         roll = the music's loudest moment; then sparse piano (F/A f840, A4 f870)
    f900-1079 CLOSER     the hook motif returns soft: C (E4 G4 C5 D5) - Dm9 (D4 F4 A4 C5) - Bbmaj7 (Bb3 D4 F4 A4)
              + OUTRO    under the outro (f960+), crackle; the last notes ring across the seam into the f0 motif
                         (rendered on an extended timeline and folded onto the start: loop-exact)

Bus: per-stem circular reverbs (loop-safe), tape wow on the piano (0.5 Hz / 6 Hz, integer cycles per 36 s), kick
sidechain on bass + keys in the present, the tape-stop warp and the two gates applied identically to every stem, then
one gain + 4x true-peak limiter (circular) iterated to -16.0 LUFS integrated, TP <= -3.0 dBTP. Stems x the same curve sum
to music.wav (piano, bass, drums, keys, fx). A gentle -1.5 dB bell at 2.5 kHz on the bus keeps the VO band open.

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh):
    python3 sirf_36_shots_music.py build    -> <RW>/audio/music.wav + stems/music_{piano,bass,drums,keys,fx}.wav +
                                               music.json (map, events, render numbers, sha256)
    python3 sirf_36_shots_music.py verify   -> music.verify.json + music_spectrogram.png (silence gates, payoff max,
                                               tempo grid, loudness, determinism)
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as E  # noqa: E402
import epic_music as EM  # noqa: E402
from audio import SR, undb, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'sirf_36_shots'
FPS, BPM, NF = 30, 120.0, 1080
DUR = NF / FPS                                  # 36.000 s
N = _n(DUR)
assert N == 1728000
SPF = SR // FPS                                 # 1,600 samples per frame
BEAT, BAR = 60.0 / BPM, 240.0 / BPM             # 0.5 s (15 f), 2.0 s (60 f)
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
TARGET_LUFS, TP_CEILING = -16.0, -3.0
KEY = 'D minor'
STEMS = ('piano', 'bass', 'drums', 'keys', 'fx')
TAIL = 6.0                                      # extended render past DUR, folded back onto the start
PAYOFF_PIANO_DB, PAYOFF_SUB_DB = -8.3, -9.5           # payoff balance (verify: music max at f810, limiter GR small)
CRACKLE_LU = -24.0                              # crackle loudness relative to the music (-40 LUFS at -16)

F_FLASH, F_STOP, F_REHOOK, F_BUILD = 60, (375, 390), 480, 750
F_TAPE, F_DROP, F_PAYOFF, F_CLOSER, F_OUTRO = (772, 780), (780, 810), 810, 900, 960


def F(f):
    return f / FPS


def T(bar, beat=0.0):
    return bar * BAR + beat * BEAT


# voicings: (bass root MIDI, warm piano upper structure, cold synth voicing)
CHORDS = {'Dm9': (38, (53, 57, 60, 64), (62, 69, 72, 76)),
          'Bbmaj7': (34, (50, 53, 57, 62), (58, 65, 69, 74)),
          'F/A': (33, (53, 57, 60, 65), (57, 65, 72, 76)),
          'C': (36, (52, 55, 60, 62), (60, 67, 74, 76))}
PROG = ('Dm9', 'Bbmaj7', 'F/A', 'C')
MOTIF = {'Dm9': (62, 65, 69, 72), 'C': (64, 67, 72, 74), 'Bbmaj7': (58, 62, 65, 69)}
PAYOFF_CHORD = (34, 41, 46, 62, 65, 69, 72)     # Bbmaj7(9): Bb1 F2 Bb2 | D4 F4 A4 C5


def chord(bar):
    return PROG[bar % 4]


def hz(m):
    return E.midi_hz(m)


# ============================================================================================ instruments (mono float64)
def felt_piano(m, dur, vel, r):
    """Felt upright piano: inharmonic partials (B rises with pitch), detuned string pairs (beating), two-stage decay
    (prompt + aftersound), hammer-position comb (1/7), felt low-pass and a 4 ms felt attack, hammer thump, damper
    release 90 ms after `dur`. Peak ~ vel ** 1.4."""
    f0 = hz(m)
    n = _n(dur + 0.45)
    t = np.arange(n) / SR
    Bh = 1.2e-4 * 2 ** ((m - 48) / 18.0)
    tau0 = float(np.clip(2.8 * (220.0 / f0) ** 0.55, 0.7, 6.0))
    bright = 0.3 + 0.7 * vel
    x = np.zeros(n)
    K = int(min(16, 9000.0 // f0))
    for k in range(1, K + 1):
        fk = k * f0 * np.sqrt(1 + Bh * k * k)
        ak = abs(np.sin(np.pi * k / 7.0)) / k ** (1.0 + 1.5 * (1 - bright))
        tk = tau0 / (1 + 0.38 * (k - 1) ** 1.15)
        e = 0.62 * np.exp(-t / (0.3 * tk)) + 0.38 * np.exp(-t / tk)
        d = 0.7e-3 * np.sqrt(k)                                     # +-0.6 cents per partial pair
        ph = r.uniform(0, 2 * np.pi)
        x += ak * e * 0.5 * (np.sin(2 * np.pi * fk * (1 + d) * t + ph) + np.sin(2 * np.pi * fk * (1 - d) * t + ph * 1.3))
    x *= np.clip(t / 0.004, 0, 1) ** 1.5
    thump = A.lp(r.standard_normal(n), 250 + f0, 2) * np.exp(-t / 0.010) * 0.06 * vel
    x = A.lp(x + thump, 700 + 3600 * vel + 1.5 * f0, 2)
    damp = np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.09))
    return x * damp * vel ** 1.4


def upright_bass(m, dur, vel, r):
    """Round upright-style bass: plucked tone (sine + 3 harmonics) with a +10 cent pluck bend (30 ms), finger
    transient, gentle tanh, LP 1.3 kHz, decay 0.9 s, raised-cosine release 80 ms at `dur`."""
    f0 = hz(m)
    n = _n(dur + 0.1)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.006 * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph) + 0.07 * np.sin(4 * ph)
    x = np.tanh(1.3 * x) / np.tanh(1.3)
    env = np.clip(t / 0.006, 0, 1) * np.exp(-t / 0.9) * (0.6 + 0.4 * np.exp(-t / 0.12))
    u = np.clip((t - dur) / 0.08, 0, 1)
    env *= 0.5 + 0.5 * np.cos(np.pi * u)
    pluck = A.bp(r.standard_normal(n), 500, 2200, 2) * np.exp(-t / 0.006) * 0.25
    return A.lp(x * env + pluck, 1300, 2) * vel


def santoor(m, vel, r, dur=2.2):
    """Santoor-like hammered dulcimer: three detuned courses (-3 / 0 / +3 cents), bright slightly inharmonic partials
    with fast high-partial decay, a 2 ms hammer click."""
    f0 = hz(m)
    n = _n(dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 9):
        if k * f0 > 14000:
            break
        fk = k * f0 * np.sqrt(1 + 3e-4 * k * k)
        tk = 1.5 / (1 + 0.6 * (k - 1))
        for c in (-3.0, 0.0, 3.0):
            x += np.sin(2 * np.pi * fk * 2 ** (c / 1200) * t + r.uniform(0, 6.28)) * np.exp(-t / tk) / k ** 0.9 / 3
    x += A.bp(r.standard_normal(n), 3000, 8000, 2) * np.exp(-t / 0.002) * 0.3
    x *= np.clip(t / 0.0015, 0, 1)
    x[-_n(0.05):] *= np.linspace(1, 0, _n(0.05))
    return x * vel


def brush_snare(vel, r, tight=False):
    """Brushed snare tap (bristles: band noise 1.2-9 kHz, 70 ms; shell 190 Hz) or a tight roll stroke (tight=True)."""
    n = _n(0.4)
    t = np.arange(n) / SR
    tau = 0.035 if tight else 0.07
    tap = A.bp(r.standard_normal(n), 1500 if tight else 1200, 9000, 2) * np.exp(-t / tau) * np.clip(t / 0.0015, 0, 1)
    body = np.sin(2 * np.pi * (200 if tight else 190) * t) * np.exp(-t / 0.045) * 0.35
    return (tap / max(np.abs(tap).max(), 1e-9) * 0.9 + body) * vel


def brush_swish(dur, vel, r):
    """Brush sweep leading into a stroke: band noise 2-7 kHz, (u)^2 swell, ends on dur."""
    n = _n(dur)
    u = np.arange(n) / n
    x = A.bp(r.standard_normal(n), 2000, 7000, 2) * u ** 2
    x[-64:] *= np.linspace(1, 0, 64)
    return x / max(np.abs(x).max(), 1e-9) * 0.25 * vel


def pulse_stab(midis, dur, cutoff, vel, r):
    """Cold synth pulse: 2 detuned PolyBLEP saws per note, 3 ms attack, 110 ms decay to a 25 % sustain, LP cutoff,
    HP 150 Hz. Stereo (+-0.3 pan per detuned voice)."""
    n = _n(dur + 0.06)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for m in midis:
        for c in (-1, 1):
            s = E.saw(np.full(n, hz(m) * (1 + c * 0.0025)), r.uniform(0, 1))
            out += A.pan(s, 0.3 * c)
    env = np.clip(t / 0.003, 0, 1) * (0.25 + 0.75 * np.exp(-t / 0.11))
    env *= np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.015))
    out = A.hp(A.lp(out, cutoff, 2), 150, 2) * env[:, None] / (2 * len(midis))
    return out * vel


def sub_note(m, dur, vel):
    """Present-section sub bass: sine + 0.2 x 2nd harmonic, drive, 5 ms attack, 0.35 s decay, 20 ms release."""
    n = _n(dur + 0.03)
    t = np.arange(n) / SR
    ph = 2 * np.pi * hz(m) * t
    x = np.tanh(1.8 * (np.sin(ph) + 0.2 * np.sin(2 * ph))) / np.tanh(1.8)
    env = np.clip(t / 0.005, 0, 1) * np.exp(-t / 0.35) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.02))
    return x * env * vel


def sub_swell(m, vel):
    """Payoff sub: Bb1 sine + octave, 30 ms attack, 1.6 s decay (bass_enhance adds phone harmonics on the bus)."""
    n = _n(3.5)
    t = np.arange(n) / SR
    ph = 2 * np.pi * hz(m) * t
    x = np.sin(ph) + 0.3 * np.sin(2 * ph)
    env = np.clip(t / 0.03, 0, 1) ** 2 * np.exp(-t / 1.6)
    env[-_n(0.1):] *= np.linspace(1, 0, _n(0.1))
    return x * env * vel


def crackle_loop(n, r):
    """Seamless vinyl surface over n samples (circular): small pops ~7/s, a few louder ticks 0.4/s, faint hiss
    (HP 300 / LP 5 kHz). Stereo, unit-ish."""
    x = np.zeros((n, 2))
    for rate, lo, amp in ((7.0, 1500.0, 0.25), (0.4, 600.0, 1.0)):
        k = int(n / SR * rate)
        pos = r.integers(0, n, k)
        for p in pos:
            L = int(r.integers(24, 72))
            g = r.standard_normal(L) * np.exp(-np.arange(L) / (L / 4.0)) * amp * r.lognormal(0, 0.5)
            ch = int(r.integers(0, 3))
            idx = (p + np.arange(L)) % n
            if ch == 2:
                x[idx, 0] += g
                x[idx, 1] += g * 0.7
            else:
                x[idx, ch] += g
    x = A.hp(x, 1000.0, 2)
    x = x / (np.sqrt(np.mean(x ** 2)) + 1e-12)
    x = 4.0 * np.tanh(x / 4.0)                                          # crest <= ~12 dB: no stray giant pops
    hiss = A.lp(A.hp(r.standard_normal((n, 2)), 300, 2), 5000, 2) * 0.25
    return x + hiss


# ============================================================================================ score
class Score:
    def __init__(self, seed=36):
        self.r = np.random.default_rng(seed)
        L = N + _n(TAIL)
        self.st = {k: np.zeros((L, 2)) for k in STEMS}
        self.kick_key = np.zeros(L)
        self.ev = []

    def put(self, stem, x, t, gain_db=0.0, pan=0.0):
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 1:
            x = A.pan(x, pan) if pan else A._st(x)
        A._add(self.st[stem], x * undb(gain_db), t)

    def piano(self, t, m, dur, vel, gain_db=0.0):
        self.put('piano', felt_piano(m, dur, vel, self.r), t, gain_db, pan=float(np.clip((m - 60) / 40.0, -0.4, 0.4)))

    def piano_chord(self, t, midis, dur, vel, roll=0.012, gain_db=0.0):
        for i, m in enumerate(midis):
            self.piano(t + i * roll, m, dur, vel * (0.92 + 0.08 * self.r.random()), gain_db)

    def kick(self, t, punch, gain_db, lpf=None):
        k = EM.kick(self.r, punch)
        if lpf:
            k = A.lp(k, lpf, 2)
        self.put('drums', k, t, gain_db)
        i = _n(t)
        m = min(len(k), len(self.kick_key) - i)
        self.kick_key[i:i + m] += np.abs(k[:m]) * undb(gain_db)

    def event(self, t, what):
        self.ev.append(dict(t=round(t, 4), f=round(t * FPS, 2), bar_beat='%d:%g' % (int(t // BAR), round(t % BAR / BEAT, 3)),
                            what=what))


def compose(seed=36):
    s = Score(seed)
    r = s.r
    # ---- hook (bar 0) and closer (bars 15-17): the motif on the beats
    for i, m in enumerate(MOTIF['Dm9']):
        s.piano(T(0, i), m, 0.9 if i < 3 else 1.6, 0.62 if i == 0 else 0.55)
    s.piano(T(0), 38, 1.9, 0.30)
    s.piano(T(0), 45, 1.9, 0.26)
    s.event(0.0, 'hook motif D4 F4 A4 C5 on the beats (piano only + crackle)')
    for bar, name, vel in ((15, 'C', 0.42), (16, 'Dm9', 0.36), (17, 'Bbmaj7', 0.34)):
        for i, m in enumerate(MOTIF[name]):
            s.piano(T(bar, i), m, 0.9 if i < 3 else 1.7, vel * (1.08 if i == 0 else 1.0))
        root = CHORDS[name][0]
        s.piano(T(bar), root, 1.9, vel * 0.6)
        s.piano(T(bar), root + 7, 1.9, vel * 0.5)
    s.event(T(15), 'closer: motif returns soft (C - Dm9 - Bbmaj7), rings across the seam into the f0 motif')
    # ---- past (bars 1-7): half-time lo-fi
    for bar in range(1, 8):
        name = chord(bar)
        root, up, _ = CHORDS[name]
        t0 = T(bar)
        s.kick(t0, 0.2, -2.0, lpf=3000)
        s.kick(t0 + 1.5 * BEAT, 0.15, -9.0, lpf=2500)                  # ghost on 2&
        s.put('drums', brush_swish(0.18, 0.8, r), t0 + 2 * BEAT - 0.18, -6)
        s.put('drums', brush_snare(0.85, r), t0 + 2 * BEAT, -3)
        for k in range(8):                                             # soft brushed 8ths, light swing
            tt = t0 + k * BEAT / 2 + (0.03 if k % 2 else 0.0)
            s.put('drums', A.lp(EM.hat(r), 9000, 2), tt, -17 if k % 2 else -14, pan=0.25)
        s.put('bass', upright_bass(root, 1.2, 0.9, r), t0)
        s.put('bass', upright_bass(root + 7, 0.45, 0.7, r), t0 + 2.5 * BEAT)
        nxt = CHORDS[chord(bar + 1)][0]
        s.put('bass', upright_bass(nxt - 1 if nxt > root else nxt + 1, 0.22, 0.6, r), t0 + 3.5 * BEAT)
        s.piano(t0, root + 12, 1.9, 0.42)
        s.piano_chord(t0, up, 0.95, 0.42)
        s.piano_chord(t0 + 1.5 * BEAT, up[1:], 0.4, 0.28, roll=0.006)
        s.piano_chord(t0 + 2.5 * BEAT, up, 1.0, 0.33)
        if bar in (2, 4):
            s.piano(t0 + 3 * BEAT, 72, 0.45, 0.30)
            s.piano(t0 + 3.5 * BEAT, 69, 0.45, 0.28)
        for i, m in enumerate((up[-1] + 12, up[-2] + 24, up[-1] + 24)):  # santoor shimmer on the bar start
            s.put('keys', santoor(m, 0.5 - 0.1 * i, r), t0 + i * BEAT / 4, -12, pan=0.45 * (-1) ** i)
    s.event(F(F_FLASH), 'kit enters on the flash pop (half-time: kick 1, brushed snare 3)')
    # ---- present (bars 8-12): full time, cold
    for bar in range(8, 13):
        name = chord(bar)
        root, _, cold = CHORDS[name]
        t0 = T(bar)
        for b in range(4):
            s.kick(t0 + b * BEAT, 0.55, 0.0)
            s.put('bass', sub_note(root + 12, 0.42, 0.8), t0 + b * BEAT, 4.5)
        for b in (1, 3):
            if not (bar == 12 and b == 3):
                s.put('drums', A.lp(EM.clap(r), 7000, 2), t0 + b * BEAT, -7)
        for k in range(8):
            op = (k == 7)
            if bar == 12 and k >= 4:
                continue
            s.put('drums', EM.hat(r, open=op), t0 + k * BEAT / 2, -12 if k % 2 else -10, pan=0.3)
        u0 = (bar - 8) / 5.0
        steps = 8 if bar < 12 else 4
        for k in range(steps):
            u = u0 + k / (8 * 5.0)
            cut = 350.0 * (4200.0 / 350.0) ** u
            s.put('keys', pulse_stab(cold, BEAT / 2 * 0.8, cut, 0.9 if k % 2 == 0 else 0.7, r), t0 + k * BEAT / 2, 8)
    for k in range(8):                                                 # build f750-f779: pulse 16ths, filter open
        tt = F(F_BUILD) + k * BEAT / 4
        s.put('keys', pulse_stab(CHORDS['Dm9'][2], BEAT / 4 * 0.8, 3600 + 600 * k / 8, 0.75 + 0.03 * k, r), tt, 8)
    rolls = [F(F_BUILD) + k * BEAT / 4 for k in range(4)] + [F(F_BUILD) + BEAT + k * BEAT / 8 for k in range(8)]
    for i, tt in enumerate(rolls):
        s.put('drums', brush_snare(0.35 + 0.65 * i / (len(rolls) - 1), r, tight=True), tt, -6, pan=0.1 * (-1) ** i)
    s.event(F(F_REHOOK), 'present: full time, cold pulse 8ths, kick every beat, filter opens over 5 bars')
    s.event(F(F_BUILD), 'build: snare roll 16ths -> 32nds, pulse 16ths')
    # ---- payoff f810
    tp = F(F_PAYOFF)
    for i, m in enumerate(PAYOFF_CHORD):
        s.piano(tp + 0.003 * i, m, 2.2 if m > 50 else 2.6, 1.0, gain_db=PAYOFF_PIANO_DB)
    s.put('fx', sub_swell(34, 1.0), tp, PAYOFF_SUB_DB)
    s.put('keys', EM.pad_chord((46, 53, 57, 62, 65), F(F_OUTRO) - tp + 0.4, r, cutoff=1500, attack=0.08, release=1.2), tp, -0.5)
    for i, m in enumerate((74, 77, 81, 84, 86)):
        s.put('keys', santoor(m, 0.55, r), tp + 0.06 + i * BEAT / 4, -14, pan=0.4 * (-1) ** i)
    s.piano_chord(T(14), CHORDS['F/A'][1], 1.4, 0.36)
    s.piano(T(14), 33 + 12, 1.8, 0.32)
    s.piano(T(14, 2), 69, 1.2, 0.30)
    s.event(tp, 'PAYOFF: piano Bbmaj7(9) ff + sub swell Bb1 + pad + santoor roll (music max)')
    s.event(F(F_STOP[0]), 'stop: one beat of digital silence (thumb joke), back f390')
    s.event(F(F_TAPE[0]), 'tape stop: varispeed to zero into the freeze')
    s.event(F(F_DROP[0]), 'drop-out: digital silence f780-f809')
    return s


# ============================================================================================ bus
def _fold(x):
    out = x[:N].copy()
    rest = x[N:]
    i = 0
    while i < len(rest):
        m = min(N, len(rest) - i)
        out[:m] += rest[i:i + m]
        i += m
    return out


def _wow(x):
    """Tape wow 0.3 % at 0.5 Hz + flutter 0.04 % at 6 Hz (integer cycles per 36 s: seamless), circular read."""
    t = np.arange(len(x)) / SR
    d = 0.003 / (2 * np.pi * 0.5) * np.sin(2 * np.pi * 0.5 * t) + 0.0004 / (2 * np.pi * 6.0) * np.sin(2 * np.pi * 6.0 * t)
    src = (np.arange(len(x)) - d * SR) % len(x)
    i0 = np.floor(src).astype(np.int64)
    fr = (src - i0)[:, None]
    return x[i0] * (1 - fr) + x[(i0 + 1) % len(x)] * fr


def _tape_stop(x):
    i0, i1 = F_TAPE[0] * SPF, F_TAPE[1] * SPF
    L = i1 - i0
    u = np.arange(L) / L
    v = (1 - u) ** 1.6
    src = i0 + np.concatenate([[0.0], np.cumsum(v)[:-1]])
    y = x.copy()
    for c in range(x.shape[1]):
        y[i0:i1, c] = np.interp(src, np.arange(len(x)), x[:, c]) * (1 - 0.6 * u)
    return y


def gate_curve():
    """1 everywhere; exact 0 on the thumb stop f375-f389 and the drop-out f780-f809: a 64-sample ramp down ends on
    the window's first sample (f375 / f780 are silent), a 64-sample ramp up starts on f390 / f810."""
    g = np.ones(N)
    R = 64
    for a, b in (F_STOP, F_DROP):
        ia, ib = a * SPF, b * SPF
        g[ia - R:ia] = np.linspace(1, 0, R)
        g[ia:ib] = 0.0
        g[ib:ib + R] = np.linspace(0, 1, R)    # opens on the frame boundary (the payoff / snare attack is slower)
    return g


def _circ_sidechain(x, key, depth_db):
    p = _n(1.0)
    xx = np.concatenate([x[-p:], x, x[:p]])
    kk = np.concatenate([key[-p:], key, key[:p]])
    return A.sidechain(xx, A._st(kk), depth_db=depth_db, attack=0.005, release=0.16)[p:p + len(x)]


def _circ_limiter(x, ceiling):
    p = _n(0.5)
    xx = np.concatenate([x[-p:], x, x[:p]])
    return A.limiter_gain(xx, ceiling)[p:p + len(x)]


def render(seed=36):
    s = compose(seed)
    st = {k: _fold(v) for k, v in s.st.items()}
    key = _fold(s.kick_key[:, None])[:, 0]
    st['piano'] = _wow(st['piano'])
    st['piano'] = A.lp(EM_sat(st['piano']), 7500, 2)
    st['bass'] = A.bass_enhance(st['bass'], 0.5)
    st['fx'] = A.bass_enhance(st['fx'], 0.7)
    present = np.zeros(N)
    present[F_REHOOK * SPF:F_DROP[0] * SPF] = 1.0
    for k in ('bass', 'keys'):
        ducked = _circ_sidechain(st[k], key, 4.0)
        st[k] = st[k] * (1 - present[:, None]) + ducked * present[:, None]
    verb = dict(piano=('room', -13.0), bass=('room', -24.0), drums=('room', -19.0), keys=('plate', -13.0),
                fx=('room', -22.0))
    for k, (pre, wet) in verb.items():
        st[k] = A.reverb_circular(st[k], pre, wet)
    stem_db = dict(piano=-2.5, bass=-10.5, drums=6.5, keys=1.0, fx=0.0)
    for k in STEMS:
        st[k] = A.eq(st[k], 'peak', 2500.0, 0.8, -1.5) * undb(stem_db[k])
    # vinyl crackle at CRACKLE_LU under the music's integrated loudness (-40 LUFS in the -16 LUFS track)
    cr = crackle_loop(N, np.random.default_rng(1036))
    l_pre = A.loudness(sum(st.values()) * gate_curve()[:, None])
    st['fx'] = st['fx'] + cr * undb(l_pre + CRACKLE_LU - A.loudness(cr))
    for k in STEMS:
        st[k] = _tape_stop(st[k])
    g = gate_curve()
    for k in STEMS:
        st[k] = st[k] * g[:, None]
    return st, s.ev


def EM_sat(x, drive=1.3):
    pk = float(np.abs(x).max()) + 1e-12
    return np.tanh(drive * x / pk) / np.tanh(drive) * pk


def level(st):
    pre = sum(st.values())
    gdb = TARGET_LUFS - A.loudness(pre)
    gl = np.ones(N)
    for _ in range(12):
        gl = _circ_limiter(pre * undb(gdb), TP_CEILING - 0.3)
        y = pre * undb(gdb) * gl[:, None]
        L = A.loudness(y)
        if abs(L - TARGET_LUFS) < 0.03 and A.true_peak(y) <= TP_CEILING:
            break
        gdb += TARGET_LUFS - L
    curve = undb(gdb) * gl
    out = {k: v * curve[:, None] for k, v in st.items()}
    mix = sum(out.values())
    lc_t, lc = A.loudness_curve(mix, 0.4, 0.01)
    info = dict(lufs=round(A.loudness(mix), 3), true_peak_dbtp=round(A.true_peak(mix), 3),
                lra=round(A.loudness_range(mix), 2), momentary_max_lufs=round(float(lc.max()), 2),
                momentary_max_at_s=round(float(lc_t[np.argmax(lc)]), 3), gain_db=round(float(gdb), 3),
                limiter_max_gr_db=round(float(-A.db(gl.min())), 3))
    return mix, out, info


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def build(out=AUD):
    st, ev = render()
    mix, stems, info = level(st)
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    path = os.path.join(out, 'music.wav')
    A._write_wav(path, mix, 24)
    paths = {}
    for k in STEMS:
        paths[k] = os.path.join(out, 'stems', 'music_%s.wav' % k)
        A._write_wav(paths[k], stems[k], 24)
    meta = dict(module=MODULE, file=path, stems=paths, dur=DUR, frames=NF, samples=N, sr=SR, bits=24, bpm=BPM,
                key=KEY, prog=list(PROG), source='procedural (this file + epic_music voices), seed 36; no samples, '
                'no song, no AI model', licence='original work for @jawad_mp4', events=sorted(ev, key=lambda e: e['t']),
                render=info, sha256=_sha(path))
    json.dump(meta, open(os.path.join(out, 'music.json'), 'w'), indent=1)
    print(json.dumps(dict(file=path, **info), indent=1))
    return meta


# ============================================================================================ verify
def ebur128(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    get = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))  # noqa: E731
    return dict(I=get('I'), LRA=get('LRA'), TP=get('Peak'))


def grid_fit(x, t0, t1, bpm=BPM):
    """Spectral-flux beat grid on [t0, t1]: best tempo (+-3 %) and phase (s, folded to +-half a beat; 0 = on the
    reel grid). Method bias measured on a reference click track on the exact grid (same window) and subtracted."""
    def raw(sig):
        m = A._st(sig).mean(1)[_n(t0):_n(t1)]
        _, tt, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - 240)
        fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 100), axis=1), 0).sum(0)
        hop = 240 / SR

        def sc(b, off):
            i = np.round((off + np.arange(0, tt[-1] - off, 60 / b)) / hop).astype(int)
            return fl[i[i < len(fl)]].mean()
        best = max((sc(b, o), b, o) for b in bpm * np.arange(0.97, 1.0301, 0.0025) for o in np.arange(0, 60 / b, 0.002))
        sc_, b, off = best
        off = ((off + t0) + 30 / b) % (60 / b) - 30 / b
        return b, off, sc_ / max(fl.mean(), 1e-12)
    b, off, strength = raw(x)
    ref = np.random.default_rng(0).standard_normal((len(x), 2)) * 1e-4
    u = np.arange(_n(0.05)) / SR
    clk = np.sin(2 * np.pi * 160 * u) * np.exp(-u * 60)
    for k in range(int(np.ceil(t0 / BEAT)), int(t1 / BEAT) + 1):
        i = _n(k * BEAT)
        if i + len(u) <= len(ref):
            ref[i:i + len(u)] += clk[:, None] * 0.5
    _, bias, _ = raw(ref)
    return dict(window_s=[t0, t1], tempo_bpm=round(float(b), 3), phase_ms=round(float(off - bias) * 1000, 1),
                strength=round(float(strength), 2), ok=bool(abs(b - bpm) <= 0.2 and abs(off - bias) <= 0.015))


def verify(out=AUD):
    path = os.path.join(out, 'music.wav')
    meta = json.load(open(os.path.join(out, 'music.json')))
    x, sr = A.read_wav(path)
    assert sr == SR and len(x) == N
    rep = dict(file=path, sha256_matches_build=_sha(path) == meta['sha256'])
    eb = ebur128(path)
    rep['loudness'] = dict(ffmpeg=eb, ok=abs(eb['I'] - TARGET_LUFS) <= 0.2 and eb['TP'] <= TP_CEILING + 0.05)
    sil = {}
    for nm, (a, b) in (('stop_f375_f389', F_STOP), ('dropout_f780_f809', F_DROP)):
        seg = x[a * SPF:b * SPF]
        sil[nm] = dict(max_abs=float(np.abs(seg).max()), digital_silence=bool(not np.any(seg)))
    sil['ok'] = all(v['digital_silence'] for v in sil.values() if isinstance(v, dict))
    rep['silence'] = sil
    lc_t, lc = A.loudness_curve(x, 0.4, 0.01)
    imax = int(np.argmax(lc))
    rep['payoff'] = dict(momentary_max_lufs=round(float(lc[imax]), 2), at_s=round(float(lc_t[imax]), 3),
                         at_f=round(float(lc_t[imax]) * FPS, 1),
                         ok=bool(F(F_PAYOFF) <= lc_t[imax] <= F(F_PAYOFF) + 0.6))
    sections = dict(hook=(0, 60), past=(60, 480), present=(480, 780), payoff=(810, 900), closer=(900, 960),
                    outro=(960, 1080))
    rep['sections_lufs'] = {k: round(A.loudness(x[a * SPF:b * SPF]), 2) for k, (a, b) in sections.items()}
    rep['grid_past'] = grid_fit(x, T(1), T(6))
    rep['grid_present'] = grid_fit(x, T(8), T(12))
    w = _n(0.05)
    seam = np.concatenate([x[-w:], x[:w]])
    d = np.abs(np.diff(seam, axis=0)).max(1)
    rep['seam'] = dict(step=float(np.abs(x[0] - x[-1]).max()), local_median_step=float(np.median(d)),
                       ok=bool(np.abs(x[0] - x[-1]).max() <= 8 * max(float(np.median(d)), 1e-6)))
    rep['ok'] = all(rep[k]['ok'] for k in ('loudness', 'silence', 'payoff', 'grid_past', 'grid_present', 'seam'))
    png = os.path.join(out, 'music_spectrogram.png')
    im = A.spectro_image(A.Sfx(x, 0, 'music'), 1800, 460, None, 'sirf_36_shots music.wav (bars of 120 BPM)',
                         '%.1f LUFS  TP %.1f dBTP  momentary max %.1f LUFS at f%.0f' % (
                             eb['I'], eb['TP'], lc[imax], lc_t[imax] * FPS), fmin=30.0, fmax=20000.0, dyn=80.0)
    from PIL import ImageDraw
    dr = ImageDraw.Draw(im)
    for b in range(19):
        xx = int(b * BAR / DUR * 1800)
        dr.line([(xx, 44), (xx, 442)], fill=(110, 100, 130))
    for f, c in ((375, (80, 230, 255)), (390, (80, 230, 255)), (780, (80, 230, 255)), (810, (255, 181, 71)), (480, (242, 49, 43))):
        xx = int(F(f) / DUR * 1800)
        dr.line([(xx, 44), (xx, 442)], fill=c)
        dr.text((xx + 2, 46), 'f%d' % f, fill=c)
    im.save(png)
    rep['png'] = png
    json.dump(rep, open(os.path.join(out, 'music.verify.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('build', 'verify'))
    ap.add_argument('--out', default=AUD)
    a = ap.parse_args()
    if a.cmd == 'build':
        build(a.out)
    else:
        sys.exit(0 if verify(a.out)['ok'] else 1)


if __name__ == '__main__':
    main()
