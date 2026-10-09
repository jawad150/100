#!/usr/bin/env python3
"""epic_music: original procedural music beds for the @jawad_mp4 reels (music-supervisor kit, rebuilt in session 4).

Spec: brand_reels/research/sound_design.md section 5. Everything is synthesised here (numpy) or comes from
audio.py / epic_sfx.py sounds, so the beds are licence-clean (we own every note), deterministic (seeded) and sit
exactly on the edit's BPM grid.

Styles (EM.STYLES; callers may register more at runtime, e.g. EM.STYLES['c08_epic'] = fn):
    dark_pulse  120 BPM  cinematic hybrid: string ostinato, taiko, 808, braam on the drop, piano motif
    desi_drill  142 BPM  sliding 808, hat triplet rolls, half-time clap, sitar hook (D Phrygian dominant)
    lofi_desi    84 BPM  tabla kaharwa, EP chords Dm9-Bbmaj7-Gm9-A7b9, harmonium swells, crackle, tape-stop end
    desi_epic   100 BPM  dhol chaal, harmonium drone, string ostinato, dhol + braam on the drop, sitar hook

API (the five <slug>_music.py modules are the contract):
    Song(dur, bpm, key='D', seed=0)       .dur .bpm .beat .bar .N .key .root (MIDI, D -> 62 = Sa D4) .r (rng)
                                          .st {drums, bass, harmony, lead, fx: (N, 2)} .kick_key (N,) sidechain key
                                          .put(stem, x, t, gain_db=0, pan=0, hit=0)  .deg(scale, degree, octave=0)
                                          .T(bar, beat=0)  .kick(t, punch=0.5, gain_db=0)
    instruments (mono float64 unless noted, calibrated by CAL so gain 0 peaks near audio.REF_LUFS momentary):
        kick(r, punch=0.5)  hat(r, open=False)  clap(r)  bass808(notes, n, drive=2.0)
        epiano(f, dur, r, bright=0.5)  string_note(f, dur, r, attack=0.004, release=0.05, cutoff=1500)
        pad(f, dur, r, cutoff=1200) (stereo)  pad_chord(midis, dur, r, cutoff=1200) (stereo)
    render(style, dur, bpm=None, key='D', drop_bar=None, seed=0, out=None) -> dict(mix, stems, info)
    beatgrid(x, bpm) -> dict(tempo, phase_s, strength)    level_rider(x, ...) -> linear gain curve
    CAL, STEM_DB, STYLES, PHRYG_DOM, MINOR, DORIAN, KAHARWA

CLI: python3 epic_music.py <style> <DUR> [--bpm B] [--key D] [--drop-bar n] [--seed s] [--out file.wav]
     python3 epic_music.py selftest     (all four styles at 30 s against section 5.3's targets)
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.ndimage import uniform_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as E  # noqa: E402
from audio import SR, undb, _n  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx', 'out', 'music')

# ============================================================================================ theory
PHRYG_DOM = (0, 1, 4, 5, 7, 8, 10)     # D Eb F# G A Bb C (Bhairav-ish desi colour)
MINOR = (0, 2, 3, 5, 7, 8, 10)
DORIAN = (0, 2, 3, 5, 7, 9, 10)
KEYS = dict(C=60, Db=61, D=62, Eb=63, E=64, F=65, Gb=66, G=67, Ab=68, A=69, Bb=70, B=71)
KEYS.update({'C#': 61, 'D#': 63, 'F#': 66, 'G#': 68, 'A#': 70})
# kaharwa theka in 8ths: dha ge na tin | na ke dhin na  -> (stroke, level dB)
KAHARWA = (('dha', 0.0), ('ge', -4.0), ('na', -2.0), ('tin', -3.0),
           ('na', -2.0), ('ke', -5.0), ('dhin', -1.0), ('na', -3.0))

STEMS = ('drums', 'bass', 'harmony', 'lead', 'fx')
STEM_DB = dict(drums=0.0, bass=-1.0, harmony=-2.0, lead=-2.0, fx=-3.0)
TARGET_LUFS, TP_CEILING = -16.0, -3.0

# Calibration (dB): brings each raw instrument's max momentary loudness (400 ms, K-weighted) to audio.REF_LUFS
# (-20) at gain 0, so the beds' instruments and the SFX library share one reference. Measured by
# `python3 epic_music.py calibrate` (kick punch 0.5, closed hat, clap, 808 D2 1 s drive 2, EP D4 1 s bright 0.5,
# string D4 0.3 s LP 1500, pad D minor triad 2 s LP 1200).
CAL = dict(kick=-13.9, hat=-11.4, clap=-6.1, bass808=-16.6, epiano=-19.2, string=-11.3, pad=-15.3)


def _key_root(key):
    k = str(key).strip()
    for suf in ('minor', 'min', 'm', 'major', 'maj'):
        if k.lower().endswith(suf) and len(k) > len(suf):
            k = k[:-len(suf)]
            break
    k = k[:1].upper() + k[1:]
    if k not in KEYS:
        raise ValueError('epic_music: unknown key %r' % key)
    return KEYS[k]


def _env_ar(n, attack, release_at, release, sus_tau=None):
    """Linear attack, optional exponential sustain decay, raised-cosine release starting at release_at (s)."""
    t = np.arange(n) / SR
    e = np.clip(t / max(attack, 1e-4), 0, 1)
    if sus_tau:
        e = e * np.exp(-t / sus_tau)
    u = np.clip((t - release_at) / max(release, 1e-4), 0, 1)
    return e * (0.5 + 0.5 * np.cos(np.pi * u))


def _osc(f, n, phase=0.0):
    f = np.broadcast_to(np.asarray(f, dtype=np.float64), (n,))
    return np.sin(2 * np.pi * (phase + np.cumsum(f) / SR))


# ============================================================================================ instruments
def kick(r, punch=0.5):
    """Electronic kick, ~0.6 s, onset on sample 0: sine body with a pitch drop (~110-160 Hz -> 48 Hz) and a short
    click whose level follows `punch` (0..1). Mono."""
    p = float(np.clip(punch, 0.0, 1.0))
    n = _n(0.6)
    t = np.arange(n) / SR
    f = 48.0 + (60.0 + 100.0 * p) * np.exp(-t / 0.028)
    body = _osc(f, n) * np.exp(-t / (0.30 - 0.08 * p))
    body = np.tanh(1.6 * body) / np.tanh(1.6)
    nz = r.standard_normal(n) * np.exp(-t / 0.0025)
    click = A.hp(A.lp(nz, 9000.0, 2), 1800.0, 2) * (0.15 + 0.55 * p)
    x = body + click
    x[:24] *= np.linspace(0.0, 1.0, 24)
    x[-_n(0.02):] *= np.linspace(1.0, 0.0, _n(0.02))
    return undb(CAL['kick']) * x


def hat(r, open=False):
    """Hi-hat: 6 detuned square partials (metal) + noise, HP 7 kHz; closed 35 ms decay, open 220 ms. Mono."""
    op = bool(open) and float(open) != 0.0
    tau = 0.22 if op else 0.035
    n = _n(tau * 5 + 0.01)
    t = np.arange(n) / SR
    metal = sum(np.sign(np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)))
                for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0)) / 6.0
    x = 0.5 * metal + r.standard_normal(n)
    x = A.hp(x, 7000.0, 4) * np.exp(-t / tau)
    x[:12] *= np.linspace(0.0, 1.0, 12)
    return undb(CAL['hat']) * x


def clap(r):
    """Clap: 3 band-passed noise bursts at 0 / 11 / 22 ms (6 ms decays) + a 0.11 s tail from the last. Mono."""
    n = _n(0.6)
    t = np.arange(n) / SR
    nz = A.bp(r.standard_normal(n), 900.0, 4200.0, 2)
    e = np.zeros(n)
    for k, t0 in enumerate((0.0, 0.011, 0.022)):
        u = t - t0
        e += np.where(u >= 0, np.exp(-np.maximum(u, 0) / 0.006), 0.0) * (0.8 + 0.1 * k)
    u = t - 0.022
    e += np.where(u >= 0, 0.45 * np.exp(-np.maximum(u, 0) / 0.11), 0.0)
    x = nz * e
    x[:12] *= np.linspace(0.0, 1.0, 12)
    return undb(CAL['clap']) * x


def bass808(notes, n, drive=2.0):
    """808 bass line rendered into n samples. notes: [(t, dur, midi, glide_to_midi or None), ...]; a glide moves
    the pitch over the note's last 35 %. Sine + 2nd harmonic, tanh drive, 3 ms attack, 0.8 s decay, 30 ms
    release. Mono (n,)."""
    y = np.zeros(int(n))
    d = max(float(drive), 1e-3)
    for (t0, dur, m, glide) in notes:
        k = _n(dur + 0.03)
        tt = np.arange(k) / SR
        mid = np.full(k, float(m))
        if glide is not None:
            g0 = 0.65 * dur
            u = np.clip((tt - g0) / max(dur - g0, 1e-3), 0, 1)
            mid = m + (float(glide) - m) * (u * u * (3 - 2 * u))
        f = E.midi_hz(mid)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sin(ph) + 0.25 * np.sin(2 * ph)
        x = np.tanh(d * x) / np.tanh(d)
        x *= _env_ar(k, 0.003, dur, 0.03, sus_tau=0.8)
        i = _n(t0)
        m_ = min(k, len(y) - i)
        if m_ > 0 and i >= 0:
            y[i:i + m_] += x[:m_]
    return undb(CAL['bass808']) * y


def epiano(f, dur, r, bright=0.5):
    """Electric piano (Rhodes-like): decaying sine partials 1, 2, 3, 4 plus the tine ping (14 x f0, 1 ms attack,
    20 ms decay) scaled by `bright`; 0.3 ms attack, held `dur`, 0.25 s raised-cosine release. Mono, dur + 0.25 s."""
    b = float(np.clip(bright, 0.0, 1.0))
    n = _n(dur + 0.25)
    t = np.arange(n) / SR
    ph = r.uniform(0, 1)
    x = np.zeros(n)
    for k, (a, tau) in enumerate(((1.0, 2.2), (0.30 + 0.25 * b, 0.9), (0.10 + 0.15 * b, 0.5), (0.05 * b, 0.3))):
        x += a * np.sin(2 * np.pi * (f * (k + 1) * t + ph * (k + 1))) * np.exp(-t / tau)
    if 14 * f < 0.45 * SR:
        tine = np.sin(2 * np.pi * 14 * f * t) * np.clip(t / 0.001, 0, 1) * np.exp(-t / 0.020)
        x += 0.35 * b * tine
    x *= 1.0 + 0.04 * np.sin(2 * np.pi * 4.5 * t)                 # gentle tremolo
    x *= _env_ar(n, 0.0003, dur, 0.25)
    return undb(CAL['epiano']) * x


def string_note(f, dur, r, attack=0.004, release=0.05, cutoff=1500.0):
    """Section-string note: 3 detuned band-limited saws (-7 / 0 / +6 cents), LP `cutoff`, attack / held / raised-
    cosine release. Mono, dur + release."""
    n = _n(dur + release)
    x = np.zeros(n)
    for c in (-7.0, 0.0, 6.0):
        x += E.saw(np.full(n, f * 2 ** (c / 1200)), r.uniform(0, 1))
    x = A.lp(x / 3.0, float(cutoff), 2)
    x *= _env_ar(n, attack, dur, release)
    return undb(CAL['string']) * x


def _pad_voices(midis, n, r, detune=0.003, spread=0.5):
    x = np.zeros((n, 2))
    for m in midis:
        for c in (-1, 1):
            v = E.saw(np.full(n, E.midi_hz(m) * (1 + c * detune)), r.uniform(0, 1))
            A._add(x, A.pan(v, spread * c), 0.0)
    return x


def pad_chord(midis, dur, r, cutoff=1200.0, attack=0.35, release=0.6):
    """Detuned-saw pad chord (2 saws per note, +-0.3 %, panned +-0.5), LP `cutoff`, linear attack, held `dur`,
    raised-cosine release after it. Stereo (dur + release, 2)."""
    midis = list(midis)
    n = _n(dur + release)
    x = _pad_voices(midis, n, r)
    env = _env_ar(n, attack, dur, release)
    return undb(CAL['pad']) * A.lp(x, float(cutoff), 2) * env[:, None] / max(len(midis), 1)


def pad(f, dur, r, cutoff=1200.0, attack=0.35, release=0.6):
    """One pad voice at f Hz (the pad grammar, single note). Stereo."""
    n = _n(dur + release)
    x = np.zeros((n, 2))
    for c in (-1, 1):
        A._add(x, A.pan(E.saw(np.full(n, f * (1 + c * 0.003)), r.uniform(0, 1)), 0.5 * c), 0.0)
    env = _env_ar(n, attack, dur, release)
    return undb(CAL['pad']) * A.lp(x, float(cutoff), 2) * env[:, None]


def crackle(n, r, level=0.02):
    """Vinyl crackle + faint hiss, stereo (n, 2)."""
    x = np.zeros((n, 2))
    k = int(n / SR * 30)
    pos = r.integers(0, max(1, n - 64), k)
    for i, p in enumerate(pos):
        x[p:p + 32, i % 2] += r.uniform(-1, 1) * np.exp(-np.arange(32) / 6.0)
    x = A.bp(x, 1500.0, 9000.0, 2) + 0.03 * A.lp(r.standard_normal((n, 2)), 6000.0, 2)
    return level * x


# ============================================================================================ song
class Song:
    """A bar grid with raw stems and a sidechain key. Styles write into it; render() buses it."""

    def __init__(self, dur, bpm, key='D', seed=0, stems=STEMS):
        self.dur, self.bpm, self.key, self.seed = float(dur), float(bpm), key, int(seed)
        self.beat = 60.0 / self.bpm
        self.bar = 4 * self.beat
        self.N = _n(self.dur)
        self.root = _key_root(key)
        self.r = A._rng(self.seed, 'epic_music:%s:%g' % (key, self.bpm))
        self.st = {k: np.zeros((self.N, 2)) for k in stems}
        self.kick_key = np.zeros(self.N)
        self.events = []

    @property
    def nbars(self):
        return int(np.floor(self.dur / self.bar + 1e-9))

    def T(self, bar, beat=0.0):
        return round((bar * 4 + beat) * self.beat, 6)

    def deg(self, scale, d, octave=0):
        """MIDI note of scale degree d (0 = root, negatives go down) at `octave` relative to the root (D4)."""
        d = int(d)
        return int(self.root + 12 * octave + scale[d % len(scale)] + 12 * (d // len(scale)))

    def put(self, stem, x, t, gain_db=0.0, pan=0.0, hit=0.0):
        """Place x (mono or stereo) with its hit on time t (s) into stem, at gain_db and pan."""
        x = np.asarray(x, dtype=np.float64)
        x = A.pan(x, pan) if pan else A._st(x)
        A._add(self.st[stem], x * undb(gain_db), t - hit)

    def kick(self, t, punch=0.5, gain_db=0.0, lp=None):
        x = kick(self.r, punch)
        if lp:
            x = A.lp(x, lp, 2)
        self.put('drums', x, t, gain_db)
        A._add(self.kick_key, x * undb(gain_db), t)

    def sound(self, stem, name, t, gain_db=0.0, pan=0.0, align='hit', **params):
        s = A.sound(name, **params)
        self.put(stem, np.asarray(s, dtype=np.float64), t, gain_db, pan, s.hit if align == 'hit' else 0.0)
        return s


# ============================================================================================ styles
def _common_fx(s, drop_bar, end_bar, riser_db=-8.0, end_db=-4.0, end_sound='trailer_hit'):
    """Reverse cymbal into the drop, the drop's impact, an end hit on end_bar."""
    td, te = s.T(drop_bar), s.T(end_bar)
    if td - 1.5 > 0:
        s.sound('fx', 'reverse_cymbal', td, riser_db, duration=1.5)
    s.sound('fx', 'cinematic_boom', td, -4.0)
    if te < s.dur - 0.3:
        s.sound('fx', end_sound, te, end_db)


def style_dark_pulse(s, drop_bar=6):
    r, nb = s.r, s.nbars
    end_bar = int(np.floor((s.dur - 2.0) / s.bar))
    prog = (0, 0, -2, -1)                          # i i bVI bVII (natural minor degrees)
    for bar in range(nb):
        post = bar >= drop_bar
        if bar >= end_bar:
            break
        sh = prog[bar % 4]
        fc = 900.0 + (1400.0 if post else 300.0 * bar / max(drop_bar, 1))
        for k in range(16 if post else 8):         # ostinato 16ths after the drop, 8ths before
            step = 0.25 if post else 0.5
            m = s.deg(MINOR, sh + (0, 0, 2, 0, 4, 0, 2, 0)[k % 8], -1)
            s.put('harmony', string_note(E.midi_hz(m), s.beat * step * 0.6, r, 0.004, 0.05, fc),
                  s.T(bar, k * step), (-6.0 if post else -9.0) + (2.0 if k % 4 == 0 else 0.0), 0.3 * (-1) ** k)
        if bar >= 2:
            for b in ((0, 2) if not post else (0, 1, 2, 3)):
                s.kick(s.T(bar, b), 0.7 if post else 0.4, 0.0 if post else -6.0)
        if post:
            for b in (1, 3):
                s.put('drums', clap(r), s.T(bar, b), -4.0)
            for i in range(8):
                s.put('drums', hat(r), s.T(bar, i * 0.5), -10.0 + (2.0 if i % 2 else 0.0), 0.3)
            s.put('bass', bass808([(0.0, s.bar * 0.95, s.root - 24 + MINOR[sh % 7] - (12 if sh < 0 else 0), None)],
                                  _n(s.bar)), s.T(bar), -4.0)
            if bar % 2 == 0:
                for j, m in enumerate((s.root, s.root + 3, s.root + 7, s.root + 10)):
                    s.put('lead', epiano(E.midi_hz(m), s.beat * 0.9, r, 0.6), s.T(bar, j), -6.0, 0.15)
        if bar in (drop_bar - 2, drop_bar - 1) and bar >= 0:
            for b in (0, 2):
                s.sound('drums', 'trailer_hit', s.T(bar, b), -10.0, pitch=0.9)
    if drop_bar < nb:
        s.sound('fx', 'braam', s.T(drop_bar), -6.0)
    _common_fx(s, drop_bar, end_bar)
    return dict(drop_bar=drop_bar, drop_t=s.T(drop_bar), end_t=s.T(end_bar))


def style_desi_drill(s, drop_bar=6):
    r, nb = s.r, s.nbars
    end_bar = int(np.floor((s.dur - 2.0) / s.bar))
    hook = (0, 1, 4, 1, 0, -1, 0, 0)               # PHRYG_DOM degrees, 8ths
    for bar in range(min(nb, end_bar)):
        post = bar >= drop_bar
        # sitar hook every other bar (from bar 1), louder after the drop
        if bar >= 1 and bar % 2 == 1:
            for k, d in enumerate(hook[:4]):
                s.sound('lead', 'sitar_pluck', s.T(bar, k), -6.0 if post else -9.0, 0.2, align='start',
                        note=s.deg(PHRYG_DOM, d, 0), dur=1.2, seed=bar * 8 + k)
        if bar >= 2:
            for i in range(8):                     # hats in 8ths, triplet roll on beat 4 every 2nd bar
                if post and bar % 2 == 1 and i >= 6:
                    continue
                s.put('drums', hat(r), s.T(bar, i * 0.5), -12.0 if not post else -9.0, 0.25)
            if post and bar % 2 == 1:
                for j in range(6):
                    s.put('drums', hat(r), s.T(bar, 3.0 + j / 6), -13.0 + j, 0.25)
        if post:
            s.kick(s.T(bar, 0), 0.8)
            s.kick(s.T(bar, 2.5), 0.6, -2.0)
            s.put('drums', clap(r), s.T(bar, 2), -3.0)
            glide = s.root - 24 + (1 if bar % 2 else -2)
            s.put('bass', bass808([(0.0, s.bar * 0.48, s.root - 24, None),
                                   (s.bar * 0.5, s.bar * 0.45, s.root - 24, glide)], _n(s.bar), 2.6),
                  s.T(bar), -3.0)
        elif bar >= 2:
            s.kick(s.T(bar, 0), 0.4, -6.0)
    _common_fx(s, drop_bar, end_bar, end_sound='dhol_hit')
    return dict(drop_bar=drop_bar, drop_t=s.T(drop_bar), end_t=s.T(end_bar))


def style_lofi_desi(s, drop_bar=4):
    r, nb = s.r, s.nbars
    end_bar = int(np.floor((s.dur - 2.0) / s.bar))
    swing = 0.06 * s.beat
    root = s.root - 12
    chords = ((root, (5 + 12, 10 + 12, 14 + 12, 16 + 12)),                    # Dm9: D | F C E (+A)
              (root - 4, (4 + 12, 7 + 12, 11 + 12, 14 + 12)),                 # Bbmaj7
              (root - 7, (10 + 12, 14 + 12, 17 + 12, 21 + 12)),               # Gm9
              (root - 5, (11 + 12, 14 + 12, 17 + 12, 20 + 12)))               # A7b9
    for bar in range(min(nb, end_bar)):
        post = bar >= drop_bar
        rt, up = chords[bar % 4]
        for k, m in enumerate([rt + 12] + [rt + u - 12 for u in up]):
            s.put('harmony', epiano(E.midi_hz(m), s.bar * 0.92, r, 0.45), s.T(bar) + k * 0.009,
                  -7.0 if post else -9.0, 0.3 * (1 if k % 2 else -1) * (k > 0))
        for i, (st, g) in enumerate(KAHARWA):
            if not post and bar < 1:
                break
            t = s.T(bar, i * 0.5) + (swing if i % 2 else 0.0)
            s.sound('drums', 'tabla_hit', t, g - (2.0 if post else 5.0), 0.1, stroke=st, seed=(bar * 8 + i) % 4)
        if post:
            s.kick(s.T(bar, 0), 0.5, -4.0, lp=1800.0)
            s.kick(s.T(bar, 2.5), 0.4, -7.0, lp=1800.0)
            s.put('drums', A.lp(clap(r), 5000.0, 2), s.T(bar, 2), -8.0)
            s.put('bass', bass808([(0.0, s.bar * 0.9, rt - 12, None)], _n(s.bar), 1.4), s.T(bar), -6.0)
        if bar % 2 == 0:
            s.sound('harmony', 'harmonium_swell', s.T(bar), -14.0, align='start', duration=2 * s.bar,
                    notes=(s.root - 12, s.root - 5, s.root), seed=bar)
    s.st['fx'] += crackle(s.N, r)
    te = s.T(end_bar)
    if te < s.dur:
        for k in s.st:
            s.st[k] = E.tape_stop_fx(s.st[k], te - 0.6, 0.6)
    if drop_bar < nb:
        s.sound('fx', 'dhol_hit', s.T(drop_bar), -6.0)
    return dict(drop_bar=drop_bar, drop_t=s.T(drop_bar), end_t=te)


def style_desi_epic(s, drop_bar=5):
    r, nb = s.r, s.nbars
    end_bar = int(np.floor((s.dur - 2.0) / s.bar))
    figure = (0, 0, 1, 0, 0, 0, 2, 1)
    chaal = ((0.0, -2.0), (1.5, -4.0), (2.0, -3.0), (3.5, -6.0))
    prog = (0, 0, -2, 0)
    for bar in range(min(nb, end_bar)):
        post = bar >= drop_bar
        if bar % 2 == 0:
            s.sound('harmony', 'harmonium_swell', s.T(bar), -10.0, align='start', duration=2 * s.bar,
                    notes=(s.root - 12, s.root - 5, s.root), seed=bar)
        if bar >= 1:
            for k in range(8):
                m = s.deg(PHRYG_DOM, figure[k] + prog[bar % 4], -1)
                s.put('harmony', string_note(E.midi_hz(m), s.beat / 2 * 0.55, r, 0.004, 0.05,
                                             1600.0 if post else 1000.0),
                      s.T(bar, k * 0.5), (-5.0 if post else -9.0) + (2.0 if k == 0 else 0.0), 0.3 * (-1) ** k)
        if post or bar >= drop_bar - 2:
            for b, g in chaal:
                t = s.T(bar, b)
                s.sound('drums', 'dhol_hit', t, g + (0.0 if post else -6.0), seed=bar * 4 + int(b * 2))
                A._add(s.kick_key, kick(r, 0.5), t)
        if post:
            for i in range(8):
                s.put('drums', hat(r), s.T(bar, i * 0.5), -12.0, 0.3)
            s.put('bass', bass808([(0.0, 3.8 * s.beat, s.root - 24, None)], _n(s.bar), 1.8), s.T(bar), -6.0)
            if (bar - drop_bar) % 2 == 1:
                for k, d in enumerate((4, 5, 4, 1)):
                    s.sound('lead', 'sitar_pluck', s.T(bar, k), -8.0, 0.2, align='start',
                            note=s.deg(PHRYG_DOM, d, 0), dur=1.4, seed=bar * 4 + k)
    if drop_bar < nb:
        s.sound('fx', 'braam', s.T(drop_bar), -8.0)
    _common_fx(s, drop_bar, end_bar, end_sound='dhol_hit')
    return dict(drop_bar=drop_bar, drop_t=s.T(drop_bar), end_t=s.T(end_bar))


STYLES = dict(dark_pulse=style_dark_pulse, desi_drill=style_desi_drill, lofi_desi=style_lofi_desi,
              desi_epic=style_desi_epic)
DEFAULTS = dict(dark_pulse=dict(bpm=120, drop_bar=6), desi_drill=dict(bpm=142, drop_bar=6),
                lofi_desi=dict(bpm=84, drop_bar=4), desi_epic=dict(bpm=100, drop_bar=5))


# ============================================================================================ analysis
def beatgrid(x, bpm, rel_span=0.02, rel_step=0.0002, phase_step=0.005, hop=240, nfft=2048):
    """Spectral-flux grid fit around `bpm`: STFT (2048 / 5 ms hop), positive log-magnitude flux, then the tempo /
    phase whose beat positions collect the most flux. Returns tempo (BPM), phase_s (in (-B/2, B/2]) and strength
    (mean flux on the grid / mean flux; > 2 = clearly on a grid). Its phase carries the 43 ms window's attack bias
    (onsets read ~5-10 ms early): read it against a click-grid reference when ms matter."""
    m = A._mono(np.asarray(x, dtype=np.float64))
    _, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
    fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 100), axis=1), 0).sum(0)
    tt = tt[1:]
    if len(fl) < 4 or fl.mean() <= 0:
        return dict(tempo=float(bpm), phase_s=0.0, strength=0.0)
    h = hop / SR
    t0 = tt[0]
    best = (-1.0, float(bpm), 0.0)
    for b in bpm * (1 + np.arange(-rel_span, rel_span + 1e-12, rel_step)):
        per = 60.0 / b
        offs = np.arange(0, per, phase_step)
        k = np.arange(int(tt[-1] / per) + 1)
        pos = (offs[:, None] + k[None, :] * per - t0) / h
        ok = (pos >= 0) & (pos < len(fl) - 1)
        sc = np.where(ok, np.interp(pos, np.arange(len(fl)), fl), 0).sum(1) / np.maximum(ok.sum(1), 1)
        j = int(np.argmax(sc))
        if sc[j] > best[0]:
            best = (float(sc[j]), float(b), float(offs[j]))
    s, b, off = best
    per = 60.0 / b
    off = (off + per / 2) % per - per / 2
    return dict(tempo=round(b, 3), phase_s=round(off, 4), strength=round(s / float(fl.mean()), 2))


def level_rider(x, amount=0.3, win=1.5, max_db=9.0, floor_rel_db=40.0):
    """Slow level rider: pulls loud passages down / quiet ones up by `amount` of their deviation from the median
    K-weighted level (win-second windows), clipped to +-max_db and smoothed over 1 s. Silence (more than
    floor_rel_db under the loudest window) is left alone. Returns a linear gain curve (N,)."""
    p = np.square(A.kweight(A._st(x))).mean(1)
    lv = 10 * np.log10(np.maximum(uniform_filter1d(p, _n(win), mode='nearest'), 1e-12))
    act = lv > lv.max() - floor_rel_db
    if not act.any():
        return np.ones(len(p))
    med = np.median(lv[act])
    g = np.clip(-amount * (lv - med), -max_db, max_db) * act
    return undb(uniform_filter1d(g, _n(1.0), mode='nearest'))


# ============================================================================================ render
def bus(s, end_fade=0.6, rider=True):
    """epic_music's bus: stem trims, 5 dB kick sidechain (5 / 160 ms) on bass, harmony, lead and fx, a studio
    room (-18 dB), level rider, end fade, then gain + true-peak limiter iterated to -16 LUFS / -3 dBTP.
    Returns (mix, stems, info); the stems sum to the mix."""
    N = s.N
    st = {k: np.array(v[:N]) * undb(STEM_DB.get(k, 0.0)) for k, v in s.st.items()}
    if np.any(s.kick_key):
        sc = A.sidechain(np.ones(N), s.kick_key, depth_db=5.0, attack=0.005, release=0.16)[:, 0]
        for k in ('bass', 'harmony', 'lead', 'fx'):
            if k in st:
                st[k] = st[k] * sc[:, None]
    st = {k: A.reverb(v, 'studio', wet_db=-18.0)[:N] for k, v in st.items()}
    mix = sum(st.values())
    g_r = level_rider(mix) if rider else np.ones(N)
    fo = np.ones(N)
    if end_fade:
        f = min(N, _n(end_fade))
        fo[N - f:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(1, f + 1) / f)
    curve = g_r * fo
    st = {k: v * curve[:, None] for k, v in st.items()}
    mix = sum(st.values())
    g = TARGET_LUFS - A.loudness(mix)
    gl = np.ones(N)
    for _ in range(12):
        gl = A.limiter_gain(mix * undb(g), TP_CEILING - 0.3)
        y = mix * undb(g) * gl[:, None]
        L = A.loudness(y)
        if abs(L - TARGET_LUFS) < 0.02:
            break
        g += TARGET_LUFS - L
    stems = {k: v * undb(g) * gl[:, None] for k, v in st.items()}
    y = sum(stems.values())
    info = dict(bus_gain_db=round(float(g), 3), limiter_max_gr_db=round(float(-A.db(gl.min())), 3),
                lufs=round(A.loudness(y), 3), true_peak_dbtp=round(A.true_peak(y), 3),
                lra=round(A.loudness_range(y), 2), max_momentary_lufs=round(A.momentary_max(y), 2))
    return y, stems, info


def render(style, dur, bpm=None, key='D', drop_bar=None, seed=0, out=None, stems_dir=None):
    """Render a style to a mastered bed. Returns dict(mix, stems, info). With out=<file.wav> it also writes the
    wav, <out>.json (the report) and <out stem>_stems/<stem>.wav."""
    t_start = time.time()
    E.register()
    d = DEFAULTS.get(style, {})
    bpm = float(bpm or d.get('bpm', 100))
    s = Song(dur, bpm, key, seed)
    fn = STYLES[style]
    db_ = d.get('drop_bar') if drop_bar is None else drop_bar
    meta = fn(s, db_) if db_ is not None else fn(s)
    y, stems, info = bus(s)
    info.update(style=style, dur=float(dur), bpm=bpm, key=key, seed=int(seed), render_s=round(time.time() - t_start, 2),
                beatgrid=beatgrid(y, bpm), source='procedural numpy (epic_music + epic_sfx + audio.py); original, '
                'no samples of songs, no AI model', **(meta or {}))
    if out:
        A._write_wav(out, y)
        sd = stems_dir or os.path.splitext(out)[0] + '_stems'
        for k, v in stems.items():
            A._write_wav(os.path.join(sd, '%s.wav' % k), v)
        with open(os.path.splitext(out)[0] + '.json', 'w') as f:
            json.dump(info, f, indent=2)
        info['out'] = out
    return dict(mix=y, stems=stems, info=info)


# ============================================================================================ tools
def calibrate():
    """Measure each raw instrument (CAL = 0) and print the CAL that brings it to REF_LUFS momentary max."""
    global CAL
    keep = dict(CAL)
    CAL = {k: 0.0 for k in keep}
    r = lambda: A._rng(0, 'cal')  # noqa: E731
    try:
        raw = dict(kick=kick(r(), 0.5), hat=hat(r()), clap=clap(r()),
                   bass808=bass808([(0, 1.0, 38, None)], _n(1.1), 2.0),
                   epiano=epiano(E.midi_hz(62), 1.0, r()), string=string_note(E.midi_hz(62), 0.3, r(), cutoff=1500),
                   pad=pad_chord([62, 65, 69], 2.0, r()))
        res = {k: round(A.REF_LUFS - A.momentary_max(v), 1) for k, v in raw.items()}
    finally:
        CAL = keep
    return res


def selftest(dur=30.0, out_dir=OUT):
    os.makedirs(out_dir, exist_ok=True)
    rows, ok = [], True
    for name in ('dark_pulse', 'desi_drill', 'lofi_desi', 'desi_epic'):
        res = render(name, dur, out=os.path.join(out_dir, '%s.wav' % name))
        i, bg = res['info'], res['info']['beatgrid']
        bpm = i['bpm']
        p = dict(tempo=abs(bg['tempo'] - bpm) <= 0.2, phase=abs(bg['phase_s']) <= 0.015, strength=bg['strength'] > 2,
                 lufs=abs(i['lufs'] - TARGET_LUFS) <= 0.2, tp=i['true_peak_dbtp'] <= TP_CEILING,
                 finite=bool(np.all(np.isfinite(res['mix']))))
        ok &= all(p.values())
        rows.append(dict(style=name, bpm=bpm, render_s=i['render_s'], lufs=i['lufs'], tp=i['true_peak_dbtp'],
                         lra=i['lra'], drop_t=i.get('drop_t'), end_t=i.get('end_t'), beatgrid=bg, checks=p))
    return ok, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('style', help='a style name, "selftest" or "calibrate"')
    ap.add_argument('dur', nargs='?', type=float, default=30.0)
    ap.add_argument('--bpm', type=float)
    ap.add_argument('--key', default='D')
    ap.add_argument('--drop-bar', type=int)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    if a.style == 'calibrate':
        print(json.dumps(calibrate(), indent=1))
        return 0
    if a.style == 'selftest':
        ok, rows = selftest(a.dur)
        for r_ in rows:
            print(json.dumps(r_))
        print('SELFTEST', 'PASS' if ok else 'FAIL')
        return 0 if ok else 1
    out = a.out or os.path.join(OUT, '%s_%gs.wav' % (a.style, a.dur))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    res = render(a.style, a.dur, a.bpm, a.key, a.drop_bar, a.seed, out)
    print(json.dumps(res['info'], indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
