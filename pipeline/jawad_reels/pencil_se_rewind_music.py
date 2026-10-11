#!/usr/bin/env python3
"""pencil_se_rewind_music.py: ORIGINAL music bed of Bijli series #1 "Pencil Se Rewind" (@jawad_mp4). Owner: music-supervisor.

Binding plan: brand_reels/design/reels/pencil_se_rewind/SHOTS.md section B (music), BRIEF.md sections 2-3 (grid, arc),
SCRIPT.md section 3 (optional VO windows = the VO pocket). Notes + measurements: .../pencil_se_rewind/SOUND.md.

Procedural and deterministic (fixed seeds, numpy/scipy only). Every note is synthesised here or by the house kit
(epic_music: EM.kick / EM.hat / EM.clap / EM.epiano / EM.pad_chord; sfx_jawad: varread, shape, tvf, tape_stop_fx).
No sample of any song, no AI model, no paid service. Licence: original work made for @jawad_mp4.

THE IDEA. The bed is one 16-bar song, "Mix '98 / Side A" (the handwritten label in S4), and the reel plays it the way the
story does: as the underscore in cassette tone (bars 0-4), from the walkman (a wrong spot f322, the right spot f384), eaten
(f448), held breath (bar 8), then "remastered" when the cassette turns out to be a clip in the NLE (bars 9-13, the
filter opens with the pull-back), and back on the cassette for the outro so f1023 flows into f0.

Grid: 112.5 BPM = 16 frames per beat at 30 fps (frame-exact: a 16th = 4 frames = 6,400 samples), bar 2.1333 s = 64 f,
16 bars = 1,024 f = 34.1333 s = 1,638,400 samples at 48 kHz. Key D major. Song chords per bar: | Dmaj9 | Bm9 | Gmaj9 |
A9sus4 -> A13 | (I vi IV V), four times; reel bar 8 (hush) is A9sus4 so the reveal lands deceptively on Bm and the payoff
(bar 12) gets the V -> I. Instruments: Casio-style "vibes" preset lead (additive 1:4:10 vibraphone partials + a thin
odd-harmonic organ voice, 5.6 Hz motor tremolo), dusty drum machine (EM.kick, a modal rimshot, 16th EM.hat), round finger
bass, detuned-saw pad; upgraded tone: EM.epiano + a plucked string, EM.clap on the snare, a sub kick and a soft crash.

REEL MAP (frames; song time in brackets; "tape" = the cassette-tone chain, see TONE)
    f0-f319     underscore = song bars 0-4 [0-f319]; lead hook A (bars 0-1), hook B (2-3), hook A RETROGRADE in 16ths at
                bar 4 (the fast rewind, S5); cut dead on the PLAY key f320 (4 ms fade ending on f320)
    f322-f335   walkman: a wrong spot, mid-phrase [song bar 2 beat 1.5], headphone-leak tone, 40 ms tape start, cut dead
                on the STOP key f336 (the SHOTS list says f334; moved to the visible STOP press)
    f336-f383   no music (REW motor whine is SFX)
    f384-f463   walkman: the right spot = the top of the song [0-f79] ("Mil gaya!"); f420-f447 the tape low-pass closes
                6 kHz -> 1.5 kHz + a sub swell (D2) rises; f448 wow 5 Hz +-6 % ramps in (the walkman eats it), tape stop
                f452 -> halt by f462; f462-f463 silence
    f464-f511   low Bm drone (B1 F#2 B2, LP 340 Hz, beating), fades in 40 ms after the f464 slam (SFX owns the hit)
    f512-f575   hush: A9sus4 pad LP 700 Hz in tape tone + a felt heartbeat kick on the beats (low bus)
    f576-f1023  song bars 9-15 [f576-f1023]: bar 9 Bm reveal (pad, e-piano, half-time kick), the tape chain OPENS over
                f576-f597 with the pull-back; bar 10 G bouncy groove + STUTTER EDITS on the 8ths (f640 back = reversed
                previous 8th, f648 forward = the next 8th, f656 back, f664 continues onto the CUT); bar 11 A build with a
                16th snare roll; DROP-OUT f752-f767 = digital silence (the gate edges lie outside: closes f751.88-f752,
                opens exactly on f768); bar 12 PAYOFF f768: crash + sub kick + full band, hook A on e-piano + pluck,
                bar 13 the hook RESOLVED (rises to a held D5); bars 14-15 outro, the tape chain CLOSES over f896-f927
                (D2 razor), Casio hook B, A13 -> Dmaj9 across the loop seam f1023 -> f0
    loop        the song is rendered with 2 bars of tails folded back onto the start (circular), every effect runs on a
                circular pad, the wow/flutter LFOs have whole cycles in DUR: f1023 -> f0 is continuous

TONE (tape chain on the tape bus; c(t) = 1 cassette, 0 upgraded; c = 1 on f0-f575, 1 -> 0 over f576-f597, 0 on f597-f895,
      0 -> 1 over f896-f927, 1 to the end; a raised-cosine ramp)
    wow 0.55 Hz 0.20 % + flutter 6.2 Hz 0.08 % + drift 0.13 Hz 0.06 % (peak rate deviation ~0.3 %) x c(t), read with a
    cubic fractional delay; tape saturation (sfx_jawad.shape drive 1.8) mixed in by c; time-varying STFT filter: HP
    30 -> 120 Hz and LP 18 -> 6 kHz, both 18 dB/oct (log interpolation by c), the f420-f448 close, the VO POCKET (-3 dB 1-4 kHz inside
    the optional VO windows of SCRIPT section 3, 80 ms ramps); width (M/S side gain) 1.15 upgraded -> 0.28 cassette.
    The low bus (drone, sub swell, heartbeat kick) skips the chain.

BUS: stem reverbs (studio -18 dB, lead plate -15 dB) on the extended song timeline, fold, kick sidechain 2.5 dB on keys
and pad (5 / 160 ms), then the reel assembly, tone chain, gain + 4x true-peak limiter (circular) at -3.3 dBFS iterated
to -16.0 LUFS integrated (TP <= -3.0 dBTP). No fade inside the reel except the designed cuts.

CLI (run from pipeline/jawad_reels; heavy work through tools/heavy.sh):
    python3 pencil_se_rewind_music.py build [--hook A|B|AB]   -> <RWS>/audio/music.wav (+ music_hookB.wav), music.json
    python3 pencil_se_rewind_music.py verify                 -> <RWS>/audio/qa/music_*.png + music.verify.json
<RWS> = workspace/jawad_reels/pencil_se_rewind. Hook B (trial, SHOTS S1B): f0-f63 = the hook A music through
sfx_jawad.tape_stop_fx from f0 (halt by f44, battery dying), silence f44-f63, hard splice back at f64 (5 ms fade-in).
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE ends up first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.ndimage import uniform_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as ES  # noqa: E402
import epic_music as EM  # noqa: E402
import sfx_jawad as SJ  # noqa: E402
from audio import SR, undb, db, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'pencil_se_rewind'
FPS, BPM, NF = 30, 112.5, 1024
DUR = NF / FPS                                  # 34.1333 s
BEAT = 60.0 / BPM                               # 0.5333 s = 16 frames
BAR = 4 * BEAT                                  # 2.1333 s = 64 frames
SPF = SR // FPS                                 # 1,600 samples per frame
N = _n(DUR)
assert N == NF * SPF == 1638400
OVER = 2 * BAR                                  # tails rendered past DUR and folded back onto the start
NX = N + _n(OVER)
RWS = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RWS, 'audio')
QA = os.path.join(AUD, 'qa')
SCRIPT_JSON = os.path.join(REPO, 'brand_reels', 'design', 'reels', MODULE, 'script.json')
TARGET_LUFS, TP_CEILING = -16.0, -3.0
KEY = 'D major (Dmaj9 Bm9 Gmaj9 A9sus4/A13)'
SEED = 98                                       # "Mix '98"


def F(f):
    """Reel time (s) of frame f."""
    return f / FPS


def T(bar, beat=0.0):
    """Song / reel time (s) of bar `bar`, beat `beat` (both from 0)."""
    return (bar * 4 + beat) * BEAT


def hz(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=np.float64) - 69.0) / 12.0)


# ---- reel events (frames; SHOTS section B)
F_PLAY1, F_SNIP0, F_STOP, F_PLAY2 = 320, 322, 336, 384
SNIP_SONG_T = T(2, 1.5)                         # the wrong spot: song bar 2, beat 1.5 (mid-phrase, hook B)
F_CLOSE0, F_EAT, F_TSTOP, F_HALT, F_SLAM = 420, 448, 452, 462, 464
F_HUSH, F_REVEAL, F_OPEN1 = 512, 576, 597
STUTTER = ((640, 'back'), (648, 'fwd'), (656, 'back'))   # 8th slots; f664 lands on the CUT and plays on
F_DROP0, F_DROP1 = 752, 768                     # drop-out f752-f767 (digital silence), payoff on f768
F_CLOSE_T0, F_CLOSE_T1 = 896, 927               # tape chain closes with the D2 razor
F_HOOKB_HALT = 44                               # hook B: tape stop f0 -> halt f44, splice f64

# ---- harmony (MIDI). bass root register 1-2; pad voicings without the root
ROOT = {'D': 38, 'Bm': 35, 'G': 31, 'A': 33}
PAD = {'D': (54, 57, 61, 64), 'Bm': (54, 57, 59, 62), 'G': (57, 59, 62, 66), 'Asus': (55, 59, 62, 64),
       'A13': (55, 59, 61, 64), 'Ahush': (45, 52, 55, 59, 62, 64)}
EP = {'D': (54, 57, 61, 64, 69), 'Bm': (50, 54, 57, 61, 62), 'G': (54, 57, 59, 62, 66), 'A': (55, 59, 61, 64, 66)}
SONG_CHORD = ['D', 'Bm', 'G', 'A'] * 4
# lead hooks: (start in 8ths, MIDI, length in 8ths); hook A over D | Bm, hook B over G | A
HOOK_A1 = ((0, 69, 1.5), (1.5, 66, 0.5), (2, 69, 1), (3, 71, 1), (4, 69, 1), (5, 66, 1), (6, 64, 1), (7, 66, 1))
HOOK_A2 = ((0, 62, 1.5), (1.5, 64, 0.5), (2, 66, 2), (4, 64, 1), (5, 62, 1), (6, 59, 2))
HOOK_B1 = ((0, 71, 1.5), (1.5, 67, 0.5), (2, 71, 1), (3, 74, 1), (4, 73, 1), (5, 71, 1), (6, 69, 1), (7, 67, 1))
HOOK_B2 = ((0, 69, 1), (1, 64, 1), (2, 61, 1), (3, 64, 1), (4, 67, 2), (6, 66, 1), (7, 64, 1))
HOOK_A2_RESOLVED = ((0, 62, 1.5), (1.5, 64, 0.5), (2, 66, 1), (3, 69, 1), (4, 74, 4))
# hook A bar 1 backwards in 16ths (the rewind), twice per bar
RETRO = tuple((k * 0.5, m, 0.5) for k, m in enumerate([n for _, n, _ in HOOK_A1[::-1]] * 2))


# ============================================================================================ instruments
_CAL = {}


def _cal(name, fn):
    """Calibration (dB) that brings an instrument's reference render to REF_LUFS (-20) max momentary (EM.CAL's rule)."""
    if name not in _CAL:
        _CAL[name] = A.REF_LUFS - A.momentary_max(fn())
    return undb(_CAL[name])


def _env(n, attack, rel_at, rel, tau=None):
    t = np.arange(n) / SR
    e = np.clip(t / max(attack, 1e-4), 0, 1)
    if tau:
        e = e * np.exp(-t / tau)
    u = np.clip((t - rel_at) / max(rel, 1e-4), 0, 1)
    return e * (0.5 + 0.5 * np.cos(np.pi * u))


def _vibes_raw(f, dur, r):
    rel = 0.18
    n = _n(dur + rel)
    t = np.arange(n) / SR
    ph = r.uniform(0, 1)
    x = np.zeros(n)
    for ratio, a, tau in ((1.0, 1.0, 1.1), (4.0, 0.32, 0.16), (10.0, 0.07, 0.045)):
        if ratio * f < 15000:
            x += a * np.sin(2 * np.pi * (ratio * f * t + ph * ratio)) * np.exp(-t / tau)
    for k, a in ((1, 0.10), (3, 0.05), (5, 0.025)):              # thin odd-harmonic "home keyboard" voice
        if k * f < 15000:
            x += a * np.sin(2 * np.pi * k * f * t) * np.exp(-t / 0.7)
    x *= 1.0 + 0.22 * np.sin(2 * np.pi * 5.6 * t + r.uniform(0, 6.28))   # motor tremolo
    return x * _env(n, 0.002, dur, rel)


def vibes(f, dur, r):
    """Casio-style 'vibes' preset: vibraphone partials 1 / 4 / 10, thin odd harmonics, 5.6 Hz tremolo. Mono, dur + 0.18 s."""
    return _cal('vibes', lambda: _vibes_raw(hz(69), 0.8, A._rng(0, 'cal'))) * _vibes_raw(f, dur, r)


def _pluck_raw(f, dur, r):
    rel = 0.12
    n = _n(dur + rel)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 14):
        if k * f >= 14000:
            break
        x += (1.0 / k ** 1.1) * np.sin(2 * np.pi * k * f * t + r.uniform(0, 6.28)) * np.exp(-t * (2.5 + 1.6 * k))
    return x * _env(n, 0.001, dur, rel)


def pluck(f, dur, r):
    """Plucked string (additive, higher partials decay faster). Mono, dur + 0.12 s."""
    return _cal('pluck', lambda: _pluck_raw(hz(69), 0.6, A._rng(0, 'cal'))) * _pluck_raw(f, dur, r)


def _bass_raw(f, dur, r):
    rel = 0.04
    n = _n(dur + rel)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t
    x = np.sin(ph) + 0.38 * np.sin(2 * ph) + 0.16 * np.sin(3 * ph) + 0.05 * np.sin(4 * ph)
    x = np.tanh(1.3 * x) / np.tanh(1.3)
    x *= _env(n, 0.004, dur, rel, tau=0.9)
    thump = A.lp(r.standard_normal(n), 500.0, 2) * np.exp(-t / 0.012) * 0.25   # finger on the string
    return x + thump


def bass(f, dur, r):
    """Round finger bass: sine + 2nd / 3rd / 4th harmonics, soft drive, pluck decay, finger thump. Mono."""
    return _cal('bass', lambda: _bass_raw(hz(38), 0.8, A._rng(0, 'cal'))) * _bass_raw(f, dur, r)


def _rim_raw(r):
    n = _n(0.25)
    t = np.arange(n) / SR
    x = A.modal(0.25, [1720.0, 830.0, 3150.0, 520.0], [0.014, 0.022, 0.008, 0.03], [1.0, 0.7, 0.35, 0.3])
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        x = x.mean(1)
    x = x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))
    click = A.bp(r.standard_normal(n), 2500.0, 9000.0, 2) * np.exp(-t / 0.0015) * 0.6
    return x / (np.abs(x).max() + 1e-12) + click


def rim(r):
    """Drum-machine rimshot: modal stick + rim (1.72 kHz / 830 Hz / 3.15 kHz / 520 Hz) + click. Mono."""
    return _cal('rim', lambda: _rim_raw(A._rng(0, 'cal'))) * _rim_raw(r)


def _crash_raw(r):
    n = _n(2.2)
    t = np.arange(n) / SR
    nz = A.hp(r.standard_normal(n), 3500.0, 2) * np.exp(-t / 0.55)
    metal = sum(np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)) * np.exp(-t / tau)
                for f, tau in ((3310.0, 0.9), (4870.0, 0.7), (6120.0, 0.5), (7900.0, 0.4), (9450.0, 0.3)))
    x = nz + 0.08 * metal
    x[:48] *= np.linspace(0, 1, 48)
    return x


def crash(r):
    """Soft synthetic crash (noise HP 3.5 kHz + 5 metal partials), 2.2 s. Mono."""
    return _cal('crash', lambda: _crash_raw(A._rng(0, 'cal'))) * _crash_raw(r)


def sub_kick(r):
    """Sub layer for the upgraded kick: 52 -> 44 Hz sine, 0.35 s, with 2nd harmonic for phones. Mono."""
    n = _n(0.4)
    t = np.arange(n) / SR
    f = 44.0 + 8.0 * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.2 * np.sin(2 * ph)) * _env(n, 0.003, 0.3, 0.1, tau=0.25)
    return _cal('sub_kick', lambda: (lambda tt: np.sin(2 * np.pi * 44 * tt) * np.exp(-tt / 0.25))(np.arange(n) / SR)) * x


# ============================================================================================ song
class Song:
    """The 16-bar song on an extended timeline (DUR + OVER) with raw stems and a kick sidechain key."""
    STEMS = ('drums', 'bass', 'keys', 'pad', 'fx')

    def __init__(self, seed=SEED):
        self.r = A._rng(seed, 'pencil_se_rewind_music')
        self.st = {k: np.zeros((NX, 2)) for k in self.STEMS}
        self.lead = np.zeros((NX, 2))                       # separate send (plate)
        self.key = np.zeros(NX)
        self.events = []

    def put(self, stem, x, t, gain_db=0.0, pan=0.0):
        x = np.asarray(x, dtype=np.float64)
        y = A.pan(x, pan) if (pan or x.ndim == 1) else x
        buf = self.lead if stem == 'lead' else self.st[stem]
        i = _n(t)
        m = min(len(y), NX - i)
        if m > 0 and i >= 0:
            buf[i:i + m] += y[:m] * undb(gain_db)

    def kick(self, t, punch=0.4, gain_db=0.0, lp=None, sub=False):
        x = EM.kick(self.r, punch)
        if lp:
            x = A.lp(x, lp, 2)
        self.put('drums', x, t, gain_db)
        i = _n(t)
        self.key[i:i + len(x)] += x[:max(0, min(len(x), NX - i))] * undb(gain_db)
        if sub:
            self.put('drums', sub_kick(self.r), t, gain_db - 4.0)


def _melody(s, notes, bar, inst, gain_db, pan=0.0, stem='lead', octave=0, staccato=0.92):
    for st8, m, l8 in notes:
        f = hz(m + 12 * octave)
        s.put(stem, inst(f, l8 * BEAT / 2 * staccato, s.r), T(bar, st8 / 2), gain_db, pan)


def _groove_a(s, bar, level=0.0, hats=True):
    """Cassette groove: kick 1, 2&, 3; rim 2, 4; quiet 16th hats (velocity 0 / -8 / -4 / -8 dB)."""
    for k16, g in ((0, 0.0), (6, -3.0), (8, -1.0)):
        s.kick(T(bar, k16 / 4), 0.35, level - 3.0 + g)
    for k16 in (4, 12):
        s.put('drums', rim(s.r), T(bar, k16 / 4), level - 4.0, 0.12)
    if bar % 2 == 1:
        s.put('drums', rim(s.r), T(bar, 15 / 4), level - 15.0, 0.12)        # ghost into the next bar
    if hats:
        for k16 in range(16):
            s.put('drums', EM.hat(s.r), T(bar, k16 / 4), level - 13.0 + (0, -8, -4, -8)[k16 % 4], 0.3)


def _groove_b(s, bar, level=0.0, sub=False, open_hat=True):
    """Upgraded groove: kick 1, 2&, 3, 3a; clap + rim on 2, 4; 16th hats, open hat on 4&."""
    for k16, g in ((0, 0.0), (6, -3.0), (8, -1.0), (11, -6.0)):
        s.kick(T(bar, k16 / 4), 0.55, level - 1.0 + g, sub=sub)
    for k16 in (4, 12):
        s.put('drums', EM.clap(s.r), T(bar, k16 / 4), level - 4.0, 0.0)
        s.put('drums', rim(s.r), T(bar, k16 / 4), level - 9.0, 0.15)
    for k16 in range(16):
        if open_hat and k16 == 14:
            s.put('drums', EM.hat(s.r, open=True), T(bar, k16 / 4), level - 13.0, -0.3)
        else:
            s.put('drums', EM.hat(s.r), T(bar, k16 / 4), level - 11.0 + (0, -7, -3, -7)[k16 % 4], -0.3)


def _bassline(s, bar, chord, nxt, level=0.0):
    """Finger bass on the 8th grid: root (2.5), root on 2& , 5th on 3, octave on 3&, approach on 4& to the next root."""
    r0 = ROOT[chord]
    r1 = ROOT[nxt]
    appr = r1 - 1 if (r1 - 1) != r0 else r1 + 2
    for st8, m, l8 in ((0, r0, 2.5), (3, r0, 0.8), (4, r0 + 7, 1.0), (5, r0 + 12, 0.8), (6, r0 + 7, 0.8),
                       (7, appr, 0.8)):
        s.put('bass', bass(hz(m), l8 * BEAT / 2, s.r), T(bar, st8 / 2), level + (0.0 if st8 == 0 else -2.0))


def _pad(s, bar, voicing, dur_bars=1.0, level=0.0, cutoff=1400.0, attack=0.25, release=0.3):
    x = EM.pad_chord(PAD[voicing], dur_bars * BAR + 0.3, s.r, cutoff=cutoff, attack=attack, release=release)
    s.put('pad', x, T(bar) - 0.15, level)


def compose(seed=SEED):
    """The song. Returns the Song (raw stems on the extended timeline) and its event list."""
    s = Song(seed)
    ev = s.events
    # ---------------- bars 0-4 (cassette underscore) and 14-15 (outro): groove A, Casio vibes lead
    for bar in (0, 1, 2, 3, 4, 14, 15):
        ch = SONG_CHORD[bar]
        nxt = SONG_CHORD[(bar + 1) % 16]
        outro = bar >= 14
        _groove_a(s, bar, -1.0 if outro else 0.0)
        _bassline(s, bar, ch, nxt, -1.0 if outro else 0.0)
        if ch == 'A':
            _pad(s, bar, 'Asus', 0.5, -3.0)
            s.put('pad', EM.pad_chord(PAD['A13'], 0.5 * BAR + 0.3, s.r, cutoff=1400.0, attack=0.1, release=0.3),
                  T(bar, 2) - 0.15, -3.0)
        else:
            _pad(s, bar, ch, 1.0, -3.0)
    lead_db = -2.0
    _melody(s, HOOK_A1, 0, vibes, lead_db, 0.1)
    _melody(s, HOOK_A2, 1, vibes, lead_db, 0.1)
    _melody(s, HOOK_B1, 2, vibes, lead_db, 0.1)
    _melody(s, HOOK_B2, 3, vibes, lead_db, 0.1)
    _melody(s, RETRO, 4, vibes, lead_db - 2.0, 0.1, octave=1, staccato=0.8)     # the rewind: hook A backwards
    _melody(s, HOOK_B1, 14, vibes, lead_db - 3.0, 0.1)                           # outro: under the card / V13 slot
    _melody(s, HOOK_B2, 15, vibes, lead_db - 3.0, 0.1)
    ev += [dict(t=T(0), what='bar 0: hook A on the Casio vibes (cassette groove A)'),
           dict(t=T(4), what='bar 4: hook A retrograde in 16ths (the fast rewind)'),
           dict(t=T(14), what='bars 14-15: outro, hook B at -3 dB, A13 -> Dmaj9 across the seam')]
    # ---------------- bars 5-8: never heard as song (the reel plays the walkman, the drone and the hush there)
    # ---------------- bar 9 (Bm, the reveal): pad swell, e-piano chord + motif, half-time kick, bass pedal
    s.put('pad', EM.pad_chord(PAD['Bm'], BAR + 0.3, s.r, cutoff=2200.0, attack=0.5, release=0.3), T(9) - 0.15, -1.0)
    for k, m in enumerate(EP['Bm']):
        s.put('keys', EM.epiano(hz(m), BAR * 0.95, s.r, 0.5), T(9) + 0.008 * k, -5.0, 0.25 * (-1) ** k)
    _melody(s, ((2, 62, 1), (3, 64, 1), (4, 66, 4)), 9, lambda f, d, r: EM.epiano(f, d, r, 0.7), -4.0, -0.15)
    s.kick(T(9, 0), 0.5, -1.0, sub=True)
    s.kick(T(9, 2), 0.5, -4.0, sub=True)
    s.put('bass', bass(hz(ROOT['Bm']), BAR * 0.95, s.r), T(9), -1.0)
    ev.append(dict(t=T(9), what='bar 9: Bm reveal, pad + e-piano open up (the tape chain opens f576-f597)'))
    # ---------------- bars 10-11 (G, A): bouncy groove B, pluck arps, e-piano offbeats; bar 11 16th snare roll
    for bar in (10, 11):
        ch = SONG_CHORD[bar]
        _groove_b(s, bar, -1.0, sub=False, open_hat=(bar == 10))
        _bassline(s, bar, ch, SONG_CHORD[bar + 1], 0.0)
        _pad(s, bar, 'G' if ch == 'G' else 'A13', 1.0, -4.0, cutoff=2600.0)
        arp = EP[ch]
        for k in range(8):
            m = arp[(0, 2, 1, 3, 2, 4, 3, 1)[k]] + 12
            s.put('keys', pluck(hz(m), BEAT / 2 * 0.8, s.r), T(bar, k / 2), -7.0, 0.35 * (-1) ** k)
        for k in (1, 3, 5, 7):                                                   # e-piano skank on the offbeats
            for j, m in enumerate(EP[ch][1:]):
                s.put('keys', EM.epiano(hz(m), BEAT / 2 * 0.7, s.r, 0.4), T(bar, k / 2) + 0.004 * j, -12.0, -0.2)
    for k in range(4, 12):                                                       # roll: beat 1 -> 2.75 of bar 11
        s.put('drums', EM.clap(s.r), T(11, k / 4), -16.0 + 1.6 * (k - 4), 0.0)
    ev.append(dict(t=T(10), what='bar 10: groove B, pluck arps (stutter edits applied in the reel)'))
    ev.append(dict(t=T(11, 1), what='bar 11: 16th clap roll beats 1-2.75, gone before the f752 drop-out'))
    # ---------------- bars 12-13 PAYOFF (D, Bm): crash, sub kick, full band, hook A -> resolved
    s.put('fx', crash(s.r), T(12), -3.0, 0.2)
    for bar in (12, 13):
        ch = SONG_CHORD[bar]
        _groove_b(s, bar, 0.0, sub=True)
        _bassline(s, bar, ch, SONG_CHORD[bar + 1], 1.0)
        _pad(s, bar, ch, 1.0, -2.0, cutoff=3000.0)
    _melody(s, HOOK_A1, 12, lambda f, d, r: EM.epiano(f, d, r, 0.75), -1.0, -0.1)
    _melody(s, HOOK_A1, 12, pluck, -6.0, 0.25, octave=1)
    _melody(s, HOOK_A2_RESOLVED, 13, lambda f, d, r: EM.epiano(f, d, r, 0.75), -1.0, -0.1)
    _melody(s, HOOK_A2_RESOLVED, 13, pluck, -6.0, 0.25, octave=1)
    ev.append(dict(t=T(12), what='bar 12 PAYOFF: crash + sub kick + full band, hook A on e-piano + pluck'))
    ev.append(dict(t=T(13, 2), what='bar 13: the hook resolves on a held D5'))
    return s


def _fold(x):
    out = np.array(x[:N], copy=True)
    out[:NX - N] += x[N:]
    return out


def render_song(seed=SEED):
    """Song stems -> reverbs on the extended timeline -> kick sidechain -> fold (circular). Returns dict of (N, 2)."""
    s = compose(seed)
    sc = A.sidechain(np.ones(NX), s.key, depth_db=2.5, attack=0.005, release=0.16)[:, 0]
    st = {}
    for k, v in s.st.items():
        v = v * sc[:, None] if k in ('keys', 'pad') else v
        st[k] = A.reverb(v, 'studio', wet_db=-18.0)[:NX]
    st['keys'] = st['keys'] + A.reverb(s.lead * sc[:, None], 'plate', wet_db=-15.0)[:NX]
    out = {k: _fold(v) for k, v in st.items()}
    return out, s.events


# ============================================================================================ reel assembly helpers
def _seg(x, a, b, fin=0.004, fout=0.004):
    """x[a:b] (circular sample indices) with raised-cosine fades of fin / fout s inside the segment."""
    idx = np.arange(a, b) % len(x)
    y = x[idx].copy()
    n = len(y)
    Li, Lo = min(_n(fin), n), min(_n(fout), n)
    if Li > 1:
        y[:Li] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(Li) / Li))[:, None]
    if Lo > 1:
        y[-Lo:] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(Lo) / Lo))[::-1][:, None]
    return y


def _tape_start(y, ramp=0.04):
    """Tape start: playback rate 0.25 -> 1 over `ramp` s (capstan pulling up), then 1. Alias-safe varispeed."""
    n = len(y)
    k = _n(ramp)
    u = np.clip(np.arange(n) / max(k, 1), 0, 1)
    rate = 0.25 + 0.75 * (u * u * (3 - 2 * u))
    pos = np.cumsum(rate) - rate[0]
    out = SJ.varread(y, pos)
    return out * np.clip(np.arange(n) / _n(0.003), 0, 1)[:, None]


def _warble(y, i0, ramp_s=4 / FPS, depth=0.06, f=5.0):
    """Eaten tape: from sample i0 the playback rate wobbles 1 + depth * ramp * sin(2 pi f t) (wow 5 Hz +-6 %)."""
    n = len(y)
    t = (np.arange(n) - i0) / SR
    ramp = np.clip(t / ramp_s, 0, 1) * (t >= 0)
    rate = 1.0 + depth * ramp * np.sin(2 * np.pi * f * np.maximum(t, 0))
    pos = np.cumsum(rate) - rate[0]
    pos = np.minimum(pos, n - 1)
    out = SJ.varread(y, pos)
    out[:i0] = y[:i0]
    return out


def _headphone_leak(y):
    """The walkman's headphones lying on the desk: band 380-3600 Hz, mono, light drive, small room."""
    m = A.bp(y.mean(1), 380.0, 3600.0, 2)
    m = SJ.shape(m / (np.abs(m).max() + 1e-12), 1.6) * (np.abs(m).max() + 1e-12)
    return A.reverb(A._st(m), 'room', wet_db=-14.0)[:len(y)]


def _place(buf, x, f0):
    i = f0 * SPF
    m = min(len(x), len(buf) - i)
    buf[i:i + m] += x[:m]


def tone_curve():
    """c(t): 1 = cassette tone, 0 = upgraded. Raised-cosine ramps f576-f597 (open) and f896-f927 (close)."""
    f = np.arange(N) / SPF
    c = np.ones(N)
    u = np.clip((f - F_REVEAL) / (F_OPEN1 - F_REVEAL), 0, 1)
    c = np.where(f >= F_REVEAL, 0.5 + 0.5 * np.cos(np.pi * u), c)
    v = np.clip((f - F_CLOSE_T0) / (F_CLOSE_T1 - F_CLOSE_T0), 0, 1)
    c = np.where(f >= F_CLOSE_T0, 0.5 - 0.5 * np.cos(np.pi * v), c)
    return c


def vo_windows():
    """Optional VO windows (SCRIPT section 3): (t0, t1) s from start_f and an estimated 2.7 words/s + 0.25 s tail;
    V1B (hook B) is excluded (its window equals V1's). Read from script.json; built-in fallback."""
    try:
        lines = json.load(open(SCRIPT_JSON))['vo']['lines']
        rows = [(int(l['start_f']), int(l['words'])) for l in lines if l['id'] != 'V1B']
    except Exception:  # noqa: BLE001
        rows = [(3, 3), (70, 10), (198, 5), (320, 4), (386, 4), (466, 3), (516, 6), (590, 5), (640, 3), (708, 4),
                (770, 4), (818, 6), (930, 6)]
    out = []
    for f0, w in rows:
        t0 = F(f0)
        t1 = min(DUR, t0 + w / 2.7 + 0.25)
        out.append((round(t0, 4), round(t1, 4)))
    return out


def _gain_curve(n, wins, depth_db, ramp=0.08, t_of=None):
    t = np.arange(n) / SR if t_of is None else t_of
    g = np.zeros(n)
    for a, b in wins:
        up = np.clip((t - (a - ramp)) / ramp, 0, 1)
        dn = np.clip(((b + ramp) - t) / ramp, 0, 1)
        g = np.minimum(g, depth_db * (0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn))))
    return g


# ============================================================================================ tone chain
PAD_S = 1.0


def _cpad(x, p):
    return np.concatenate([x[-p:], x, x[:p]], axis=0)


def wow_flutter(x, c):
    """Circular fractional-delay wow / flutter / drift scaled by c(t). LFOs have whole cycles in DUR."""
    t = np.arange(N) / SR
    comps = ((0.55, 0.0020, 0.3), (6.2, 0.0008, 1.1), (0.13, 0.0006, 2.0))
    d = np.zeros(N)
    for f0, a, ph in comps:
        f = ES._cycles(f0, DUR)
        d += -a / (2 * np.pi * f) * np.cos(2 * np.pi * f * t + ph)       # displacement (s) of a rate a sin(...)
    d = d * c * SR                                                        # samples
    p = _n(PAD_S)
    xp = _cpad(x, p)
    pos = np.arange(N) + p + d
    i = np.floor(pos).astype(np.int64)
    fr = (pos - i)[:, None]
    p0, p1, p2, p3 = xp[i - 1], xp[i], xp[i + 1], xp[i + 2]
    return p1 + 0.5 * fr * (p2 - p0 + fr * (2 * p0 - 5 * p1 + 4 * p2 - p3 + fr * (3 * (p1 - p2) + p3 - p0)))


def tone_chain(x, c, close=None):
    """Tape chain on the tape bus (see TONE in the docstring). close = extra LP curve (Hz per sample) or None."""
    p = _n(PAD_S)
    y = wow_flutter(x, c)
    pk = np.abs(y).max() + 1e-12
    sat = SJ.shape(_cpad(y, p) / pk * 0.9, 1.8)[p:p + N] * pk / 0.9
    sat *= undb(A.loudness(y) - A.loudness(sat)) if np.any(y) else 1.0
    y = y * (1 - c)[:, None] + sat * c[:, None]
    lpf = np.exp(np.log(6000.0) * c + np.log(18000.0) * (1 - c))
    hpf = np.exp(np.log(120.0) * c + np.log(30.0) * (1 - c))
    if close is not None:
        lpf = np.minimum(lpf, close)
    vo = undb(_gain_curve(N, vo_windows(), -3.0))
    yp = _cpad(y, p)
    np_ = len(yp)
    tp_ = (np.arange(np_) - p) % N                                        # sample index (circular) of each pad sample
    lpp, hpp, vop = lpf[tp_], hpf[tp_], vo[tp_]

    def mask(pp, f):
        k = np.clip(np.round(pp * (np_ - 1)).astype(int), 0, np_ - 1)
        fl, fh, gv = lpp[k][:, None], hpp[k][:, None], vop[k][:, None]
        g = 1.0 / np.sqrt(1.0 + (f[None, :] / fl) ** 6)                  # 18 dB/oct LP
        g = g * (1.0 / np.sqrt(1.0 + (fh / np.maximum(f[None, :], 1.0)) ** 6))   # 18 dB/oct HP
        band = np.exp(-0.5 * (np.log2(np.maximum(f[None, :], 1.0) / 2000.0) / 0.62) ** 2)   # ~1-4 kHz
        return g * (1.0 - (1.0 - gv) * band)
    y = SJ.tvf(yp, mask)[p:p + N]
    w = 0.28 * c + 1.15 * (1 - c)
    m, s_ = (y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2 * w
    return np.stack([m + s_, m - s_], 1)


# ============================================================================================ reel music
def low_layers():
    """Low bus (skips the tape chain): sub swell f420-f462 (dives with the tape stop), Bm drone f464-f511, heartbeat
    kick on the beats of bar 8."""
    r = A._rng(SEED, 'low')
    low = np.zeros((N, 2))
    # sub swell: D2 + its octave, crescendo f420 -> f452, pitch follows the tape stop f452 -> f462
    i0, i1, i2 = F_CLOSE0 * SPF, F_TSTOP * SPF, F_HALT * SPF
    n = i2 - i0
    t = np.arange(n) / SR
    k = np.arange(n) + i0
    rate = np.where(k < i1, 1.0, (1 - np.clip((k - i1) / (i2 - i1), 0, 1)) ** 1.6)
    f = hz(38) * rate
    ph = 2 * np.pi * np.cumsum(f) / SR
    amp = np.clip((k - i0) / (i1 - i0), 0, 1) ** 2 * np.where(k < i1, 1.0, rate ** 0.55)
    x = (np.sin(ph) + 0.35 * np.sin(2 * ph)) * amp
    x[-_n(0.004):] *= np.linspace(1, 0, _n(0.004))
    low[i0:i2] += A._st(x) * undb(-15.0)
    # drone f464-f511 (+ 0.3 s overlap under the hush pad)
    j0, j1 = F_SLAM * SPF, F_HUSH * SPF + _n(0.3)
    n = j1 - j0
    t = np.arange(n) / SR
    dr = np.zeros(n)
    for m, a, det in ((35, 1.0, 0.0), (42, 0.55, 0.6), (47, 0.4, -0.4)):   # B1 F#2 B2, slow beating
        dr += a * ES.saw(np.full(n, hz(m) + det), r.uniform(0, 1))
    dr = A.lp(dr, 340.0, 2)
    env = np.clip(t / 0.04, 0, 1) * np.clip((j1 - j0 - np.arange(n)) / _n(0.3), 0, 1)
    dr = dr * env * (1.0 + 0.15 * np.sin(2 * np.pi * 0.9 * t))
    dr = dr / (np.abs(dr).max() + 1e-12)
    low[j0:j1] += A.width(A.reverb(A._st(dr), 'dark', wet_db=-10.0)[:n], 0.6) * undb(-17.0)
    # heartbeat kick on the beats of bar 8 (f512, 528, 544, 560)
    for fb in (512, 528, 544, 560):
        kx = A.lp(EM.kick(r, 0.2), 260.0, 2)
        _place(low, A._st(kx) * undb(-9.0), fb)
    return low


def render(hook='A', seed=SEED):
    """-> dict(mix (N, 2) at -16 LUFS, tape / low buses, info, events)."""
    ES.register()
    song, ev = render_song(seed)
    sbus = sum(song.values())
    tape = np.zeros((N, 2))
    # R1 underscore f0-f319 (cut dead on f320)
    _place(tape, _seg(sbus, 0, F_PLAY1 * SPF, 0.0, 0.004), 0)
    # R2 walkman wrong spot f322 -> cut on STOP f336
    a = _n(SNIP_SONG_T)
    snip = _tape_start(_seg(sbus, a, a + (F_STOP - F_SNIP0) * SPF, 0.0, 0.003))
    _place(tape, _headphone_leak(snip) * undb(-4.0), F_SNIP0)
    # R3 walkman right spot f384 -> eaten f448, tape stop f452 -> halt f462
    r3 = _tape_start(_seg(sbus, 0, (F_SLAM - F_PLAY2) * SPF, 0.0, 0.0))
    r3 = _warble(r3, (F_EAT - F_PLAY2) * SPF)
    r3 = SJ.tape_stop_fx(r3, F(F_TSTOP - F_PLAY2), F(F_HALT - F_TSTOP))
    _place(tape, r3, F_PLAY2)
    # R5 hush pad f512-f575 (A9sus4, LP 700), crossfades into bar 9 at f576
    r = A._rng(seed, 'hush')
    hush = EM.pad_chord(PAD['Ahush'], BAR + 0.3, r, cutoff=700.0, attack=0.6, release=0.3) * undb(-1.0)
    _place(tape, hush, F_HUSH)
    # R6 song bars 9-15 f576-f1023 (+ the stutters, + the drop-out gate)
    r6 = _seg(sbus, F_REVEAL * SPF, N, 0.004, 0.0)
    off = F_REVEAL * SPF
    src = r6.copy()
    L8 = 8 * SPF
    xf = _n(0.003)
    w = 0.5 - 0.5 * np.cos(np.pi * np.arange(xf) / xf)
    for f0, kind in STUTTER:
        i = f0 * SPF - off
        if kind == 'back':
            sl = src[i - L8:i][::-1].copy()
        else:
            sl = src[i + L8:i + 2 * L8].copy()
        sl[:xf] *= w[:, None]
        sl[-xf:] *= w[::-1][:, None]
        r6[i:i + L8] *= 0.0
        r6[i:i + xf] += src[i:i + xf] * w[::-1][:, None]            # 3 ms crossfade out of the running music
        r6[i:i + L8] += sl
        r6[i + L8 - xf:i + L8] += src[i + L8 - xf:i + L8] * w[:, None]   # ... and back into it
    gate = np.ones(len(r6))
    g0, g1 = F_DROP0 * SPF - off, F_DROP1 * SPF - off
    e = _n(0.004)
    gate[g0 - e:g0] = 0.5 + 0.5 * np.cos(np.pi * np.arange(e) / e)
    gate[g0:g1] = 0.0
    r6 *= gate[:, None]
    _place(tape, r6, F_REVEAL)
    # close curve f420 -> f448: 6 kHz -> 1.5 kHz (log), then held until the halt
    fr = np.arange(N) / SPF
    u = np.clip((fr - F_CLOSE0) / (F_EAT - F_CLOSE0), 0, 1)
    close = np.where((fr >= F_CLOSE0) & (fr < F_SLAM), np.exp(np.log(6000.0) * (1 - u) + np.log(1500.0) * u), 1e9)
    c = tone_curve()
    tape_t = tone_chain(tape, c, close)
    # drop-out stays digital silence after the chain (STFT spill), as do the f336-f383 gap and the halt
    e2 = _n(0.002)
    for a_, b_ in ((F_DROP0, F_DROP1), (F_STOP, F_PLAY2), (F_HALT, F_SLAM)):
        i, j = a_ * SPF, b_ * SPF
        tape_t[i - e2:i] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(e2) / e2))[:, None]
        tape_t[i:j] = 0.0
    low = low_layers()
    bus = tape_t + low
    # level: gain + circular true-peak limiter to -16 LUFS / <= -3 dBTP
    p = _n(0.5)
    pk = A.tp_envelope(_cpad(bus, p))
    g = TARGET_LUFS - A.loudness(bus)
    ceil = TP_CEILING - 0.3
    for attempt in range(4):
        for _ in range(20):
            gl = A.limiter_gain(None, ceil, pk=pk * undb(g))[p:p + N]
            y = bus * undb(g) * gl[:, None]
            L = A.loudness(y)
            if abs(L - TARGET_LUFS) < 0.02:
                break
            g += TARGET_LUFS - L
        tp = A.true_peak(np.concatenate([y[-_n(0.05):], y, y[:_n(0.05)]]))
        if tp <= TP_CEILING - 0.05:
            break
        ceil -= tp - (TP_CEILING - 0.1)
    curve = undb(g) * gl
    info = dict(lufs=round(A.loudness(y), 3), true_peak_dbtp=round(A.true_peak(y), 3),
                lra=round(A.loudness_range(y), 2), momentary_max_lufs=round(A.momentary_max(y), 2),
                gain_db=round(float(g), 3), limiter_max_gr_db=round(float(-db(gl.min())), 3))
    out = dict(mix=y, tape=tape_t * curve[:, None], low=low * curve[:, None], info=info, events=ev, c=c)
    if hook == 'B':
        out['mix'] = hook_b(y)
        out['info'] = dict(info, hook='B', lufs_hookB=round(A.loudness(out['mix']), 3),
                           true_peak_dbtp_hookB=round(A.true_peak(out['mix']), 3))
    return out


def hook_b(y):
    """Hook B (trial): f0-f63 = the music through a tape stop from f0 (halt by f44), silence to f64, splice at f64."""
    z = y.copy()
    head = SJ.tape_stop_fx(y[:64 * SPF], 0.0, F(F_HOOKB_HALT))
    z[:64 * SPF] = head
    k = _n(0.005)
    z[64 * SPF:64 * SPF + k] *= np.linspace(0, 1, k)[:, None]
    return z


# ============================================================================================ files
def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def paths(hook='A'):
    return os.path.join(AUD, 'music.wav' if hook == 'A' else 'music_hookB.wav')


def build(hooks='A'):
    os.makedirs(AUD, exist_ok=True)
    meta = {}
    res = render('A')
    A._write_wav(paths('A'), res['mix'], 24)
    meta['A'] = dict(file=paths('A'), sha256=_sha(paths('A')), **res['info'])
    if 'B' in hooks:
        yb = hook_b(res['mix'])
        A._write_wav(paths('B'), yb, 24)
        meta['B'] = dict(file=paths('B'), sha256=_sha(paths('B')), lufs=round(A.loudness(yb), 3),
                         true_peak_dbtp=round(A.true_peak(yb), 3))
    doc = dict(module=MODULE, dur=DUR, frames=NF, samples=N, sr=SR, bits=24, bpm=BPM, frames_per_beat=16,
               frames_per_bar=64, key=KEY, seed=SEED, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING,
               source='procedural numpy/scipy (this file + epic_music / epic_sfx / sfx_jawad / audio.py); original, '
                      'no samples of songs, no AI model, no paid service',
               licence='original work for @jawad_mp4',
               events=[dict(e, f=round(e['t'] * FPS, 2)) for e in res['events']],
               reel_events=dict(play1=F_PLAY1, snippet=[F_SNIP0, F_STOP], snippet_song_t=SNIP_SONG_T, play2=F_PLAY2,
                                close=[F_CLOSE0, F_EAT], warble=F_EAT, tape_stop=[F_TSTOP, F_HALT], slam=F_SLAM,
                                hush=F_HUSH, reveal_open=[F_REVEAL, F_OPEN1], stutter=[list(s) for s in STUTTER],
                                drop_out=[F_DROP0, F_DROP1 - 1], payoff=F_DROP1, close_tone=[F_CLOSE_T0, F_CLOSE_T1]),
               vo_pocket=dict(windows_s=vo_windows(), depth_db=-3.0, band='1-4 kHz (Gaussian, 2 kHz +-0.62 oct)'),
               render=meta)
    json.dump(doc, open(os.path.join(AUD, 'music.json'), 'w'), indent=1)
    print(json.dumps(meta, indent=1))
    return doc


# ============================================================================================ verify
def ebur128(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))  # noqa: E731
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def rms_db(x):
    x = np.asarray(x, dtype=np.float64)
    if not np.any(x):
        return None
    return round(float(db(np.sqrt(np.mean(np.square(x))))), 2)


def env_db(x, win=0.010):
    p = np.square(A._st(x)).mean(1)
    return db(np.sqrt(np.maximum(uniform_filter1d(p, max(1, _n(win)), mode="wrap"), 0.0) + 1e-20))


def spec_png(x, t0, t1, path, title, sub='', w=1600, h=460, marks=(), shade=()):
    """audio.spectro_image of [t0, t1] (circular) with bar / beat lines and labelled frame markers."""
    from PIL import Image, ImageDraw
    i0, i1 = _n(t0), _n(t1)
    seg = A._st(x)[np.arange(i0, i1) % len(x)]
    im = A.spectro_image(A.Sfx(seg.astype(np.float32), 0, 'music'), w, h, None, title, sub, fmin=30.0, fmax=20000.0,
                         dyn=80.0).convert('RGBA')
    X = lambda t: int(round((t - t0) / (t1 - t0) * w))  # noqa: E731
    top, bot = 44, h - 18
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    do = ImageDraw.Draw(ov)
    for a, b in shade:
        do.rectangle([max(X(a), 0), top, min(X(b), w) - 1, bot], fill=(60, 120, 200, 70))
    im = Image.alpha_composite(im, ov).convert('RGB')
    dr = ImageDraw.Draw(im)
    k0, k1 = int(math.ceil(t0 / BEAT - 1e-9)), int(math.floor(t1 / BEAT + 1e-9))
    for k in range(k0, k1 + 1):
        xx = X(k * BEAT)
        if k % 4 == 0:
            dr.line([(xx, top), (xx, bot)], fill=(110, 100, 130))
            dr.text((xx + 3, top + 2), 'bar %d' % ((k // 4) % 16), fill=(200, 190, 215), font=A._font(11))
        elif (t1 - t0) < 8:
            dr.line([(xx, bot - 8), (xx, bot)], fill=(150, 140, 170))
    for i, (t, label, col) in enumerate(marks):
        xx = X(t)
        dr.line([(xx, top), (xx, bot)], fill=col, width=1)
        dr.text((xx + 3, top + 16 + 14 * (i % 3)), label, fill=col, font=A._font(11))
    im.save(path)
    return path


PCN = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
CHORD_PC = {'D': (2, 6, 9), 'Bm': (11, 2, 6), 'G': (7, 11, 2), 'A': (9, 1, 4), 'Asus': (9, 2, 4)}


def chroma(seg, lo=60.0, hi=1200.0):
    m = A._st(seg).mean(1)
    S = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2
    f = np.fft.rfftfreq(len(m), 1 / SR)
    sel = (f >= lo) & (f <= hi)
    pc = np.zeros(12)
    np.add.at(pc, np.round(69 + 12 * np.log2(f[sel] / 440.0)).astype(int) % 12, S[sel])
    return pc / max(pc.sum(), 1e-30)


def chord_check(x):
    """Per heard bar: the strongest pitch class in 25-200 Hz must be the chord root (the bass), and the chord's triad
    (sus4 for bar 8) must hold >= 40 % of the 60-1200 Hz chroma (the 9ths / 7ths / melody take the rest)."""
    plan = {0: 'D', 1: 'Bm', 2: 'G', 3: 'A', 4: 'D', 6: 'D', 8: 'Asus', 9: 'Bm', 10: 'G', 11: 'A', 12: 'D', 13: 'Bm',
            14: 'G', 15: 'A'}
    rows, ok = {}, True
    for bar, ch in plan.items():
        a, b = _n(T(bar) + 0.05), _n(T(bar + 1) - 0.05)
        if bar == 11:
            b = F_DROP0 * SPF
        if bar == 6:
            a = F_PLAY2 * SPF + _n(0.05)
        pc = chroma(x[a:b])
        share = float(sum(pc[i] for i in CHORD_PC[ch]))
        top = [PCN[i] for i in np.argsort(pc)[::-1][:3]]
        lo = chroma(x[a:b], 25.0, 200.0)
        root = PCN[int(np.argmax(lo))]
        rows['bar %d (%s)' % (bar, ch)] = dict(triad_share=round(share, 3), top3=top, bass_root=root,
                                               root_ok=root == PCN[CHORD_PC[ch][0]])
        ok &= root == PCN[CHORD_PC[ch][0]] and share >= 0.4
    rows['ok'] = bool(ok)
    return rows


def verify():
    os.makedirs(QA, exist_ok=True)
    p = paths('A')
    x, sr = A.read_wav(p)
    assert sr == SR and len(x) == N, (sr, len(x))
    rep = dict(file=p, sha256=_sha(p))
    eb = ebur128(p)
    rep['loudness'] = dict(ffmpeg=eb, toolkit_lufs=round(A.loudness(x), 3), toolkit_tp=round(A.true_peak(x), 3),
                           ok=abs(eb['I'] - TARGET_LUFS) <= 0.2 and eb['TP'] <= TP_CEILING + 0.05)
    res = render('A')
    q = np.clip(np.round(res['mix'] * 8388607.0), -8388608, 8388607)
    rep['deterministic'] = dict(int24_samples_differing=int(np.count_nonzero(q != np.round(x * 8388608.0))))
    rep['deterministic']['ok'] = rep['deterministic']['int24_samples_differing'] == 0
    fseg = lambda a, b: x[a * SPF:b * SPF]  # noqa: E731
    rep['silences'] = dict(drop_out_f752_f767=rms_db(fseg(F_DROP0, F_DROP1)), gap_f336_f383=rms_db(fseg(F_STOP, F_PLAY2)),
                           halt_f462_f463=rms_db(fseg(F_HALT, F_SLAM)),
                           ok=not np.any(fseg(F_DROP0, F_DROP1)) and not np.any(fseg(F_STOP, F_PLAY2)))
    e = env_db(x, 0.010)
    keyf = dict(hook_f0=0, slam_f16=16, play_f320=320, snip_f322=322, play_f384=384, eat_f448=448, slam_f464=464,
                hush_f512=512, reveal_f576=576, scrub_f640=640, cut_f664=664, drop_f752=752, payoff_f768=768,
                razor_f896=896, seam_f1023=1023)
    rep['rms10ms_db_at_frames'] = {k: dict((('f%+d' % d), round(float(e[((v + d) * SPF + SPF // 2) % N]), 1))
                                           for d in (-1, 0, 1)) for k, v in keyf.items()}
    # payoff attack: first sample after the gate where the music is back, and its level
    nz = np.nonzero(np.abs(x[F_DROP1 * SPF:F_DROP1 * SPF + SPF]).max(1) > 1e-5)[0]
    rep['payoff'] = dict(first_nonzero_after_f768_ms=round(float(nz[0]) / SR * 1000, 2) if len(nz) else None,
                         rms_f768_f775=rms_db(fseg(768, 776)), rms_f744_f751=rms_db(fseg(744, 752)))
    w = _n(0.05)
    d = np.abs(np.diff(np.concatenate([x[-w:], x[:w]]), axis=0)).max(1)
    rep['seam'] = dict(step=round(float(np.abs(x[0] - x[-1]).max()), 6), local_median_step=round(float(np.median(d)), 6),
                       rms_last_0p5=rms_db(x[-_n(0.5):]), rms_first_0p5=rms_db(x[:_n(0.5)]),
                       lufs_last_2bars=round(A.loudness(x[-_n(2 * BAR):]), 2),
                       lufs_first_2bars=round(A.loudness(x[:_n(2 * BAR)]), 2))
    rep['seam']['ok'] = rep['seam']['step'] <= 4 * rep['seam']['local_median_step'] + 1e-4
    bg = {}
    for nm, (a, b) in dict(cassette_bars_0_4=(0, T(5)), upgraded_bars_10_13=(T(10), T(14)),
                           outro_bars_14_15=(T(14), DUR)).items():
        g = EM.beatgrid(x[_n(a):_n(b)], BPM)
        ph = (g['phase_s'] + a) % BEAT
        ph = ph - BEAT if ph > BEAT / 2 else ph
        bg[nm] = dict(g, phase_vs_reel_grid_s=round(ph, 4))
    rep['beatgrid'] = bg

    def band(seg, lo, hi):
        S = np.abs(np.fft.rfft(seg.mean(1) * np.hanning(len(seg)))) ** 2
        f = np.fft.rfftfreq(len(seg), 1 / SR)
        return float(S[(f >= lo) & (f < hi)].sum() / S.sum())
    rep['tone'] = dict(cassette_bars_1_3=dict(below_100=round(band(x[_n(T(1)):_n(T(4))], 0, 100), 4),
                                              above_8k=round(band(x[_n(T(1)):_n(T(4))], 8000, 24000), 5)),
                       upgraded_bars_12_13=dict(below_100=round(band(x[_n(T(12)):_n(T(14))], 0, 100), 4),
                                                above_8k=round(band(x[_n(T(12)):_n(T(14))], 8000, 24000), 5)))
    corr = lambda seg: float(np.corrcoef(seg[:, 0], seg[:, 1])[0, 1])  # noqa: E731
    rep['tone']['lr_corr_cassette'] = round(corr(x[_n(T(1)):_n(T(4))]), 3)
    rep['tone']['lr_corr_upgraded'] = round(corr(x[_n(T(12)):_n(T(14))]), 3)
    rep['chords'] = chord_check(x)
    rep['ok'] = all(rep[k]['ok'] for k in ('loudness', 'deterministic', 'silences', 'seam', 'chords'))
    gold, cyan, red, ivory = (255, 181, 71), (80, 230, 255), (242, 49, 43), (255, 243, 230)
    marks = [(F(320), 'f320 PLAY cut', gold), (F(384), 'f384 PLAY', gold), (F(448), 'f448 eaten', red),
             (F(464), 'f464 re-hook', red), (F(576), 'f576 reveal', cyan), (F(640), 'f640 scrub', cyan),
             (F(768), 'f768 PAYOFF', ivory), (F(896), 'f896 razor', gold)]
    rep['png'] = [
        spec_png(x, 0, DUR, os.path.join(QA, 'music_full.png'), 'Pencil Se Rewind · music bed (Mix \'98) · 34.133 s',
                 '%.2f LUFS · %.2f dBTP · bars of 112.5 BPM · blue = drop-out f752-f767' % (eb['I'], eb['TP']),
                 marks=marks, shade=[(F(752), F(768))]),
        spec_png(x, F(300), F(600), os.path.join(QA, 'music_zoom_walkman.png'), 'f300-f600: PLAY cut, wrong spot, REW gap, '
                 'right spot, eaten, drone, hush', 'ticks = beats (16 f)', w=1600,
                 marks=[(F(f), 'f%d' % f, gold) for f in (320, 322, 336, 384, 420, 448, 452, 462, 464, 512, 576)]),
        spec_png(x, F(620), F(800), os.path.join(QA, 'music_zoom_scrub_payoff.png'), 'f620-f800: stutters, build, drop-out, '
                 'payoff', 'blue = drop-out', w=1600, marks=[(F(f), 'f%d' % f, cyan) for f in (640, 648, 656, 664, 704, 752, 768)],
                 shade=[(F(752), F(768))]),
        spec_png(x, DUR - 2.0, DUR + 2.0, os.path.join(QA, 'music_zoom_seam.png'), 'loop seam: last 2 s -> first 2 s (circular)',
                 'the seam is at the centre (f1023 -> f0)', w=1400, marks=[(DUR, 'seam f1024 = f0', ivory)])]
    json.dump(rep, open(os.path.join(AUD, 'music.verify.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--hook', default='AB', choices=('A', 'B', 'AB'))
    sub.add_parser('verify')
    a = ap.parse_args()
    if a.cmd == 'build':
        build(a.hook)
    else:
        r = verify()
        sys.exit(0 if r['ok'] else 1)


if __name__ == '__main__':
    main()
