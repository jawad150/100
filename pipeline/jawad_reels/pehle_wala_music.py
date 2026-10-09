#!/usr/bin/env python3
"""pehle_wala_music.py: ORIGINAL music bed for Reel 1 · C26 "Pehle Wala Hi Theek Tha (v1 se v27 tak)" (owner:
music-supervisor). Plan: brand_reels/design/reels/pehle_wala/BRIEF.md §12 (+ §0, §7, §11); map and measured
verification: brand_reels/design/reels/pehle_wala/MUSIC_pehle_wala.md.

Procedural and deterministic (fixed seeds, numpy/scipy only). Every sound is synthesised in this repo with the
epic_music building blocks (EM.pad grammar, EM.string_note, EM.epiano, EM.kick, EM.clap, EM.hat, EM.bass808), the
epic_sfx `trailer_hit` and `tape_stop_fx`, and three small instruments defined here (ember pad, sub root, taiko,
shimmer). No sample of any song, no AI model, nothing trending. Licence: original work made for @jawad_mp4.
Style: `dark_pulse` grammar RE-ARRANGED per the brief (not EM.render('dark_pulse'): no _common_fx hits, no 1.2 s end
fade, no level rider), so the music clutters version by version with the frame.

Grid: 112.5 BPM = 16 frames per beat at 30 fps; beat = 8/15 s = 25,600 samples; bar = 32/15 s = 2.1333 s = 64 f;
16 bars = 34.1333 s = 1,024 frames = 1,638,400 samples at 48 kHz. Bar n starts at 2.1333 n s, beat k at 0.5333 k s.
Key D minor (Sa = D3 146.83 Hz), i-VI-III-VII (Dm-Bb-F-C), one chord per bar.

    bar  t0      chord  layers (the music clutters with the frame)
    0    0.000   Dm     v1 motif: ember pad LP 700 + sub root, soft kick on f0, epiano motif D5 (f0), F5 (beat 2)
    1    2.133   Bb     + hats 8ths -9
    2    4.267   F      + string ostinato 16ths LP 1100
    3    6.400   C      hats out ("clean"), pad LP 1300; taiko 16th fill 7.467 -> 8.533 (crescendo)
    4    8.533   Dm     DRUMS IN on the "energetic" pin: kick 1 & 3, clap on 4&, hats 8ths
    5    10.667  Bb     + 808 (sub root hands over to it)
    6    12.800  F      drums + 808 out for 2 beats (Mummy), shimmer layer in; back at 13.867; taiko fill 14.4
    7    14.933  C      half-time "cinematic" bar: kick on 1, clap on 3, strings an octave down; 808 high-passed
                        at 120 Hz (the SFX braam's D1 sub owns this bar's low end)
    8    17.067  Dm     full time, "+2 dB" (tonal layers +1.5 dB; measured +1.9 LU over bar 7), strings 8ve up,
                        trailer_hit on 1 & 3, motif 8ve up (+ doubled)
    9    19.200  Bb     + hats 16ths
    10   21.333  F      peak clutter: taiko 8ths (second drum layer) + 16th kick fill on beat 4
    11   23.467  C      thinning: drums out 23.467, strings out 24.0, 808 out 24.533, pad only;
                        DROP-OUT 25.067-25.600 (gated after the reverbs, 4 ms edge: digital silence)
    12   25.600  Dm     the full clutter for one beat (808 high-passed at 120 Hz: the SFX sub_drop owns the sub);
                        tape stop 26.133 over 0.4 s on every stem, digital silence 26.533-27.733 (the rewind)
    13   27.733  Dm     restart = score bar 0 (v1 motif, soft kick) + a clean warm EP Dm chord
    14   29.867  Bb     score bar 1 (hats 8ths -12) under the end card
    15   32.000  C      score bar 3 material (VII turnaround), motif ends on A (the 5th) -> frame 0's D: loop

Bus: stems (drums, bass, harmony, lead, fx) -> kicks softened at the onset (audio.transient -4 dB) and a fast drum
tamer (soft knee 3.5:1, 7 dB over the drums' active RMS) -> harmony + lead + fx sidechained 5 dB to the kick (5 / 160
ms) and the bass 3 dB (3 / 120 ms), both circular -> studio reverb -18 dB per stem (+ hall -22 dB on harmony, lead,
fx) -> section groups processed apart (A bars 0-11: drop-out gate; B bar 12: tape stop; C bars 13-15: their overhang
past 34.1333 s folded onto the head = circular, loop-friendly) -> -16.0 LUFS integrated -> circular 4x true-peak
limiter at -3.3 dBFS, release 50 ms (<= -3.0 dBTP). No level rider (the v1 -> clutter contrast is the joke). The
stems are processed separately and the mix is their sum, so the five stems sum to music_full.wav exactly.

Hook B (Trial) music, BRIEF §12: bars 0-0.5 (0-1.333 s) = the bar-10 clutter (A's 21.333 s), a 0.3 s raised-cosine
tail fade to 1.633 s, silence under the D1 scrub, the body gated in at 2.6667 s with a 10 ms fade-in: sample-identical
to hook A from 2.6767 s.

CLI (run from pipeline/jawad_reels; heavy work through tools/heavy.sh):
    tools/heavy.sh python3 pehle_wala_music.py build    -> <RW>/music/music_full.wav + stems/, music_hookb.wav +
                                                            stems_hookb/, music_full.json; symlinks
                                                            <RW>/audio/pehle_wala_music_{A,B}.wav (BRIEF names)
    tools/heavy.sh python3 pehle_wala_music.py verify   -> music_full.verify.json + spectrogram PNGs
    (no argument = build + verify)          <RW> = workspace/jawad_reels/pehle_wala
"""
import argparse
import hashlib
import json
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
from scipy.ndimage import uniform_filter1d, maximum_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as E  # noqa: E402
import epic_music as EM  # noqa: E402
from audio import SR, undb, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'pehle_wala'
FPS = 30
BPM = 112.5
BEAT = 8.0 / 15.0                              # 0.5333 s = 16 frames = 25,600 samples
BAR = 4 * BEAT                                 # 2.1333 s = 64 frames
BARS = 16
DUR = BARS * BAR                               # 34.1333 s
N = _n(DUR)
assert N == 1638400 and N == 1024 * SR // FPS
SPB = 25600                                    # samples per beat (exact)
SEED = 101                                     # slot 1 / C26
OVER = 5.0                                     # s rendered past DUR, folded onto the head (circular loop)
MARGIN = 1.0                                   # s more, only to prove nothing is lost past DUR + OVER
NT = _n(DUR + OVER + MARGIN)
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
OUT = os.path.join(RW, 'music')
AUD = os.path.join(RW, 'audio')
STEMS = ('drums', 'bass', 'harmony', 'lead', 'fx')
STEM_DB = dict(drums=0.0, bass=-1.0, harmony=-2.0, lead=-2.0, fx=-3.0)   # = EM.STEM_DB
TARGET_LUFS, TP_CEILING = -16.0, -3.0          # limiter at TP_CEILING - 0.3 dBFS on the 4x true-peak envelope
GATE_EDGE = 0.004
TAME = (7.0, 3.5, 0.001, 0.08)                 # drums tamer: (over_db above active RMS, ratio, attack s, release s)
KICK_SOFTEN_DB = -4.0                          # audio.transient() on every EM.kick: onset -4 dB (crest), body untouched
BASS_DUCK_DB = 3.0                             # 808 / sub root ducked under the kick (the kick's own room)
LIM_RELEASE = 0.05                             # s, bus limiter release (A.limiter_gain default 0.08)
DEBUG = {}                                     # last bus internals (analysis only, never written)
KEY = 'D minor (Sa = D3 146.83 Hz)'


def T(bar, beat=0.0):
    """Reel time (s) of bar.beat (0-based)."""
    return (4 * bar + beat) * BEAT


DROP_OUT = (T(11, 3), T(12))                   # 25.0667-25.6000: 1 beat, music gated after the reverbs
TAPE_STOP = (T(12, 1), 0.4)                    # 26.1333 over 0.4 s: silent from 26.5333 (the Ctrl+Z rewind)
RESTART = T(13)                                # 27.7333: v1 restored = score bar 0
GROUPS = dict(A=(0.0, DROP_OUT[0]), B=(DROP_OUT[1], TAPE_STOP[0] + TAPE_STOP[1]), C=(RESTART, DUR + OVER))
HOOKB = dict(src=T(10), head=T(0, 2.5), fade=0.3, body=T(1, 1), fade_in=0.010)   # 21.333 | 1.333 +0.3 | 2.6667

# ---------------------------------------------------------------------------------------------- harmony
CHORD_OF_BAR = ['Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'F', 'C', 'Dm', 'Dm', 'Bb', 'C']
PAD_VOICE = dict(Dm=(57, 62, 65, 69), Bb=(58, 62, 65, 70), F=(57, 60, 65, 69), C=(60, 64, 67, 72))  # >= A3 (VO)
SUB_ROOT = dict(Dm=38, Bb=34, F=41, C=36)      # D2 73.4 · Bb1 58.3 · F2 87.3 · C2 65.4 Hz (sine root, < 90 Hz)
B808_ROOT = dict(Dm=38, Bb=34, F=29, C=36)     # D2 73.4 · Bb1 58.3 · F1 43.7 · C2 65.4 Hz (808, phone harmonics)
STR_PAT = dict(Dm=(62, 62, 65, 62), Bb=(58, 58, 62, 58), F=(65, 65, 69, 65), C=(60, 60, 64, 60))  # root,root,3rd,root
SHIMMER = (77, 81, 84)                         # F5 A5 C6 sines x2 octaves up in the synth (F6 A6 C7 = 1397-2093 Hz)
MOTIF = [74, 77, 79, 77, 74, 69, 70, 69]       # EM dark_pulse motif (degrees 7 9 10 9 7 4 5 4): D5 F5 G5 F5 D5 A4 Bb4 A4
SCORE_BAR = {b: b for b in range(13)}
SCORE_BAR.update({13: 0, 14: 1, 15: 3})        # the restart replays score bars 0, 1, 3
NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
CHORD_PCS = dict(Dm=(2, 5, 9), Bb=(10, 2, 5), F=(5, 9, 0), C=(0, 4, 7))

PAD_LP = [700, 800, 1000, 1300, 1300, 1300, 1300, 1300, 2000, 1800, 2000, 1300, 2400, 700, 700, 1300]
CAL_TAIKO = -16.0                              # brings taiko() to EM.kick's momentary loudness (measured: -18.2 = kick)
CAL_SUB = -28.0                                # sub_root() -27.0 LUFS momentary, ~4 LU under a pad chord
CAL_SHIM = -33.0                               # shimmer_pad() -31.6 LUFS momentary, ~9 LU under a pad chord


def _name(m):
    return '%s%d' % (NOTE_NAMES[m % 12], m // 12 - 1)


# ============================================================================================ instruments
def _rc(u):
    """raised-cosine 0 -> 1 for u in [0, 1]"""
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(u, 0.0, 1.0))


def ember_pad(midis, dur, attack, release, cutoff, seed):
    """EM.pad_chord's detuned-saw pad (same CAL, detune and pan), with a raised-cosine attack, a sustain held
    for `dur` and a raised-cosine release AFTER it (legato bar-to-bar crossfades on the bar line)."""
    r = A._rng(seed, 'pw_pad')
    n = _n(dur + release)
    t = np.arange(n) / SR
    x = np.zeros((n, 2))
    for m in midis:
        for c in (-1, 1):
            v = E.saw(np.full(n, E.midi_hz(m) * (1 + c * 0.003)), r.uniform(0, 1))
            A._add(x, A.pan(v, 0.5 * c), 0.0)
    env = _rc(t / attack) * np.where(t < dur, 1.0, 1.0 - _rc((t - dur) / release))
    return undb(EM.CAL['pad']) * A.lp(x, cutoff, 2) * env[:, None] / max(len(midis), 1)


def sub_root(midi, dur, attack, release):
    """Sine root < 90 Hz (+ a little 2nd harmonic and a light audio.py bass_enhance, amount 0.3, so phones imply it
    without the 808's buzz)."""
    n = _n(dur + release)
    t = np.arange(n) / SR
    f = E.midi_hz(midi)
    x = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(4 * np.pi * f * t + 0.4)
    env = _rc(t / attack) * np.where(t < dur, 1.0, 1.0 - _rc((t - dur) / release))
    y = A.bass_enhance(x * env, 0.3, fc=110.0, band=(140.0, 500.0), drive=4.0)
    return undb(CAL_SUB) * y


def taiko(r, pitch=1.0, d=0.8):
    """Short cinema taiko / tom for 16th fills: modal drum body (bible §5.4 perc recipe, shorter taus) + pitched
    skin thump + a stick slap; phone harmonics via bass_enhance. Hit at sample 0."""
    n = _n(d)
    t = np.arange(n) / SR
    f0 = 64.0 * pitch
    body = A.modal(d, [f0 * k for k in (1.0, 1.58, 2.14, 2.76)], [0.30, 0.16, 0.10, 0.06], [1.0, 0.5, 0.3, 0.15],
                   r, contact=0.0012)
    skin = A._thump(0.5, f0 * 0.9, f0 * 1.4, 0.02, 0.12, r, attack=0.0012, drive=2.2, noise=0.5, noise_lp=900.0)
    slap = A._unit(A.bp(r.standard_normal(n), 250.0, 2500.0)) * A._ar(t, 0.0004, 0.010) * 0.3
    x = 0.8 * body + 0.8 * np.pad(skin, (0, n - len(skin))) + slap
    x = A.bass_enhance(x, 0.6, fc=110.0, band=(160.0, 700.0), drive=4.0)
    return undb(CAL_TAIKO) * A._taper(x, sec=0.2)


def shimmer_pad(midis, dur, attack, release, seed):
    """Glitter layer for Mummy's glitter border: sine pairs two octaves above `midis`, detuned +-3 cents (slow
    beating = shimmer, no transients), wide, high-passed at 1.2 kHz."""
    r = A._rng(seed, 'pw_shim')
    n = _n(dur + release)
    t = np.arange(n) / SR
    x = np.zeros((n, 2))
    for k, m in enumerate(midis):
        f = E.midi_hz(m + 24)
        for c in (-1, 1):
            v = np.sin(2 * np.pi * f * (1 + c * 0.0017) * t + r.uniform(0, 2 * np.pi))
            A._add(x, A.pan(v, 0.7 * c * (1 if k % 2 else -1)), 0.0)
    env = _rc(t / attack) * np.where(t < dur, 1.0, 1.0 - _rc((t - dur) / release))
    return undb(CAL_SHIM) * A.hp(x, 1200.0, 2) * env[:, None] / len(midis)


# ============================================================================================ score
def compose():
    """-> the event list (every note / hit of the score, in reel time). gain_db is relative (before STEM_DB)."""
    ev = []

    def add(t, stem, inst, gain_db=0.0, pan=0.0, label='', **args):
        bar = int(np.floor(t / BAR + 1e-9))
        if bar == 12 and t >= GROUPS['B'][1] - 1e-9:
            return                                   # bar 12 past the tape stop's end: silent by design
        ev.append(dict(t=float(t), frame=round(float(t) * FPS, 3), bar=bar,
                       beat=round(float(t / BEAT - 4 * bar), 4), stem=stem, inst=inst, gain_db=round(gain_db, 2),
                       pan=pan, label=label, args=args))

    def pad(bar, gain, attack=0.12, release=0.35, dur=None):
        ch = CHORD_OF_BAR[bar]
        add(T(bar), 'harmony', 'pad', gain, 0.0, 'pad %s LP %d' % (ch, PAD_LP[bar]), midis=list(PAD_VOICE[ch]),
            dur=BAR if dur is None else dur, attack=attack, release=release, cutoff=PAD_LP[bar])

    def sub(bar, gain, beats=4):
        ch = CHORD_OF_BAR[bar]
        add(T(bar), 'bass', 'sub', gain, 0.0, 'sub root %s' % _name(SUB_ROOT[ch]), midi=SUB_ROOT[ch],
            dur=beats * BEAT, attack=0.04, release=0.06)   # short crossfade: two sub roots never beat

    def motif(bar, beats=(0, 2), gain=-2.0, octaves=(0,), dbl_gain=-4.0):
        sb = SCORE_BAR[bar]
        for b in beats:
            m = MOTIF[(2 * sb + b // 2) % len(MOTIF)]
            for j, o in enumerate(octaves):
                add(T(bar, b), 'lead', 'ep', gain + (0.0 if j == 0 else dbl_gain), 0.15 if j == 0 else -0.15,
                    'motif %s' % _name(m + 12 * o), midi=m + 12 * o, dur=2.5, bright=0.8)

    def strings(bar, gain, lp_hz, octaves=(0,), beats=(0, 1, 2, 3), dbl_gain=-3.0):
        pat = STR_PAT[CHORD_OF_BAR[bar]]
        for b in beats:
            for k in range(4):
                for j, o in enumerate(octaves):
                    add(T(bar, b + k / 4), 'harmony', 'str', gain + (2.0 if k == 0 else 0.0)
                        + (0.0 if j == 0 else dbl_gain), 0.25 * (-1) ** k,
                        'str %s' % _name(pat[k] + 12 * o) if (b == beats[0] and k == 0) else '',
                        midi=pat[k] + 12 * o, cutoff=lp_hz)

    def hats(bar, on_db, off_db, beats=(0, 1, 2, 3), sixteenths=None, open_odd=False):
        for b in beats:
            add(T(bar, b), 'drums', 'hat', on_db, -0.3, 'hats' if b == beats[0] else '', open=False)
            add(T(bar, b + 0.5), 'drums', 'hat', off_db, 0.3, '', open=bool(open_odd and b % 2 == 1))
            if sixteenths is not None:
                for q in (0.25, 0.75):
                    add(T(bar, b + q), 'drums', 'hat', sixteenths, 0.15, '', open=False)

    def kick(t, gain, punch=1.0, lp_hz=None, label='kick'):
        add(t, 'drums', 'kick', gain, 0.0, label, punch=punch, lp=lp_hz)

    def clap(t, gain=-2.0):
        add(t, 'drums', 'clap', gain, 0.0, 'clap')

    def tk(t, gain, pitch=1.0, label=''):
        add(t, 'drums', 'taiko', gain, 0.1 if pitch > 1 else -0.1, label, pitch=pitch)

    def b808(bar, b0, b1, gain=-1.0, hp_hz=None):
        ch = CHORD_OF_BAR[bar]
        d = (b1 - b0) * BEAT * (0.95 if b1 - b0 >= 4 else 1.0)
        add(T(bar, b0), 'bass', '808', gain, 0.0, '808 %s%s' % (_name(B808_ROOT[ch]), ' hp %d' % hp_hz if hp_hz else ''),
            midi=B808_ROOT[ch], dur=d, hp=hp_hz)

    def shimmer(bar, gain, dur=BAR, attack=0.4, release=0.6, t0=None):
        ch = CHORD_OF_BAR[bar]
        mids = SHIMMER if ch == 'F' else tuple(m + 12 for m in PAD_VOICE[ch][1:])
        add(T(bar) if t0 is None else t0, 'fx', 'shimmer', gain, 0.0, 'shimmer', midis=list(mids), dur=dur,
            attack=attack, release=release)

    # ---- bar 0 (0.000) Dm: the v1 motif
    pad(0, -2.0)
    sub(0, 0.0)
    kick(T(0), -6.0, 0.6, 1800, 'soft kick f0')
    motif(0, gain=-1.0)
    # ---- bar 1 (2.133) Bb: + hats 8ths -9
    pad(1, -2.0)
    sub(1, 0.0)
    motif(1)
    hats(1, -9.0, -11.0)
    # ---- bar 2 (4.267) F: + string ostinato 16ths LP 1100
    pad(2, -1.5)
    sub(2, 0.0)
    motif(2)
    hats(2, -9.0, -11.0)
    strings(2, -6.0, 1100)
    # ---- bar 3 (6.400) C: hats out ("clean"), pad LP 1300, taiko 16th fill 7.467 -> 8.533
    pad(3, -1.0)
    sub(3, 0.0)
    motif(3)
    strings(3, -6.0, 1100)
    for i in range(8):
        tk(T(3, 2 + i / 4), -18.0 + 10.0 * i / 7, 1.0 if i % 2 == 0 else 1.12, 'taiko fill' if i == 0 else '')
    # ---- bar 4 (8.533) Dm: DRUMS IN (kick 1 & 3, clap on 4&, hats 8ths)
    pad(4, 0.0)
    sub(4, -1.0)
    motif(4, gain=0.0)
    strings(4, -5.0, 1100)
    kick(T(4), -1.0, label='drums in')
    kick(T(4, 2), -1.0)
    clap(T(4, 3.5))
    hats(4, -3.0, -6.0, open_odd=True)
    # ---- bar 5 (10.667) Bb: + 808
    pad(5, 0.0)
    motif(5, gain=0.0)
    strings(5, -5.0, 1100)
    kick(T(5), -1.0)
    kick(T(5, 2), -1.0)
    clap(T(5, 3.5))
    hats(5, -3.0, -6.0, open_odd=True)
    b808(5, 0, 4)
    # ---- bar 6 (12.800) F: drums + 808 out for 2 beats (Mummy), shimmer in; back at 13.867; taiko fill 14.4
    pad(6, 0.0)
    motif(6, gain=0.0)
    strings(6, -5.0, 1100)
    shimmer(6, 0.0)
    kick(T(6, 2), -1.0, label='drums back')
    clap(T(6, 3.5))
    hats(6, -3.0, -6.0, beats=(2, 3), open_odd=True)
    b808(6, 2, 4)
    for i in range(4):
        tk(T(6, 3 + i / 4), -12.0 + 6.0 * i / 3, 1.0 if i % 2 == 0 else 1.12, 'taiko fill' if i == 0 else '')
    # ---- bar 7 (14.933) C: half-time "cinematic" bar (kick on 1, clap on 3, strings 8ve down)
    pad(7, 0.0)
    motif(7, gain=0.0)
    strings(7, -4.0, 1100, octaves=(-1,))
    shimmer(7, -6.0)
    kick(T(7), 0.0, label='half-time')
    clap(T(7, 2), 0.0)
    hats(7, -6.0, -10.0)
    b808(7, 0, 4, hp_hz=120)                        # grit only: the SFX braam (root D1 36.71 Hz, 2.0 s) owns the sub
    # ---- bar 8 (17.067) Dm: full time, "+2 dB" (measured +1.9 LU over bar 7: tonal layers +1.5 dB, drums at the
    #      bar-4 level, they already touch the limiter), strings 8ve up, trailer_hit on 1 & 3
    up = 1.5
    pad(8, 0.0 + up)
    motif(8, gain=-1.0 + up, octaves=(1, 0))
    strings(8, -5.0 + up, 2600, octaves=(1,))
    shimmer(8, -6.0 + up)
    kick(T(8), -1.0, label='full time +2 dB')
    kick(T(8, 2), -1.0)
    clap(T(8, 3.5), -2.0)
    hats(8, -2.0, -5.0, open_odd=True)
    b808(8, 0, 4, -1.0 + up)
    add(T(8), 'drums', 'trailer_hit', -10.0, 0.0, 'trailer_hit', pitch=1.0, seed=SEED + 8)
    add(T(8, 2), 'drums', 'trailer_hit', -12.5, 0.0, 'trailer_hit', pitch=1.0, seed=SEED + 9)
    # ---- bar 9 (19.200) Bb: + hats 16ths
    pad(9, 0.5)
    motif(9, gain=0.0)
    strings(9, -5.0, 1600)
    shimmer(9, -6.0)
    kick(T(9), -1.0)
    kick(T(9, 2), -1.0)
    clap(T(9, 3.5))
    hats(9, -3.0, -6.0, sixteenths=-9.0, open_odd=True)
    b808(9, 0, 4)
    # ---- bar 10 (21.333) F: peak clutter (taiko 8ths = second drum layer, 16th kick fill on beat 4)
    pad(10, 2.0)
    motif(10, gain=0.0, octaves=(1, 0))
    strings(10, -3.0, 2600, octaves=(0, 1))
    shimmer(10, -4.0)
    kick(T(10), -0.5, label='peak clutter')
    kick(T(10, 2), -0.5)
    for q in range(4):
        kick(T(10, 3 + q / 4), -6.0 + 1.5 * q, label='16th kick fill' if q == 0 else '')
    clap(T(10, 3.5), -1.0)
    hats(10, -2.0, -5.0, sixteenths=-8.0, open_odd=True)
    b808(10, 0, 4, 0.0)
    for i in range(8):
        tk(T(10, i / 2), -6.0 if i % 2 == 0 else -9.0, 1.0 if i % 4 == 0 else 1.12, 'taiko 8ths' if i == 0 else '')
    # ---- bar 11 (23.467) C: thinning (drums out, strings out 24.0, 808 out 24.533, pad only), drop-out 25.067
    pad(11, 0.0)
    motif(11, beats=(0,), gain=0.0)
    strings(11, -6.0, 1100, beats=(0,))
    b808(11, 0, 2, -2.0)
    # ---- bar 12 (25.600) Dm: the full clutter for one beat; tape stop at 26.133 (0.4 s)
    pad(12, 5.0, attack=0.006)
    motif(12, gain=3.0, octaves=(1, 0))
    strings(12, 0.0, 2600, octaves=(0, 1), beats=(0, 1))      # beat 1 feeds the tape stop (reads ~0.15 s)
    shimmer(12, 0.0, attack=0.02)
    kick(T(12), 2.0, label='payoff beat')
    hats(12, -1.0, -4.0, beats=(0, 1), sixteenths=-7.0)
    tk(T(12), -3.0, 1.0, 'taiko')
    tk(T(12, 0.5), -6.0, 1.12)
    b808(12, 0, 2, 4.0, hp_hz=120)                  # its grit only: the SFX sub_drop (lp 120) owns the sub band
    # ---- bar 13 (27.733) Dm: restart = score bar 0 + a clean warm EP Dm chord
    pad(13, -2.0, attack=0.03)
    sub(13, 0.0)
    kick(T(13), -6.0, 0.6, 1800, 'soft kick (restart)')
    motif(13, gain=-1.0)
    for j, m in enumerate((57, 62, 65, 69)):
        add(T(13) + 0.012 * j, 'harmony', 'ep', -9.0, 0.3 * (1 if j % 2 else -1), 'warm EP Dm chord' if j == 0 else '',
            midi=m, dur=2.4, bright=0.6, lp=2000)
    # ---- bar 14 (29.867) Bb: score bar 1 (hats -12) under the end card
    pad(14, -2.0)
    sub(14, 0.0)
    motif(14)
    hats(14, -12.0, -14.0)
    # ---- bar 15 (32.000) C: score bar 3 material, the VII turnaround into frame 0's Dm
    pad(15, -1.5)
    sub(15, 0.0)
    motif(15)
    strings(15, -9.0, 1100)
    ev.sort(key=lambda e: (e['t'], e['stem'], e['inst'], e['args'].get('midi', 0)))
    return ev


def group_of(t):
    for g, (a, b) in GROUPS.items():
        if a - 1e-6 <= t < b - 1e-6:
            return g
    raise ValueError('event at %.4f s falls in a silent window' % t)


# ============================================================================================ render
def render_event(e, i):
    a = e['args']
    r = A._rng(SEED, 'ev%d' % i)
    hit = 0.0
    inst = e['inst']
    if inst == 'pad':
        x = ember_pad(a['midis'], a['dur'], a['attack'], a['release'], a['cutoff'], SEED + i)
    elif inst == 'sub':
        x = sub_root(a['midi'], a['dur'], a['attack'], a['release'])
    elif inst == 'ep':
        x = EM.epiano(E.midi_hz(a['midi']), a['dur'], r, a['bright'])
        if a.get('lp'):
            x = A.lp(x, a['lp'], 2)
    elif inst == 'str':
        x = EM.string_note(E.midi_hz(a['midi']), BEAT / 4 * 0.6, r, 0.004, 0.05, a['cutoff'])
    elif inst == 'hat':
        x = EM.hat(r, a['open'])
    elif inst == 'kick':
        x = A.transient(EM.kick(r, a['punch']), KICK_SOFTEN_DB)[:, 0]   # softer click: lower crest, same body
        if a.get('lp'):
            x = A.lp(x, a['lp'], 2)
    elif inst == 'clap':
        x = EM.clap(r)
    elif inst == 'taiko':
        x = taiko(r, a['pitch'])
    elif inst == '808':
        x = EM.bass808([(0.0, a['dur'], a['midi'], None)], _n(a['dur'] + 0.05), 2.2)
        if a.get('hp'):
            x = A.hp(x, a['hp'], 4)
    elif inst == 'shimmer':
        x = shimmer_pad(a['midis'], a['dur'], a['attack'], a['release'], SEED + i)
    elif inst == 'trailer_hit':
        s = A.sound('trailer_hit', pitch=a['pitch'], seed=a['seed'])
        x, hit = np.asarray(s, dtype=np.float64), float(s.hit)
    else:
        raise ValueError(inst)
    x = A.pan(x, e['pan']) if e['pan'] else A._st(x)
    return x * undb(e['gain_db']), hit


def render_groups(ev):
    """-> raw[group][stem] (NT, 2) and the kick key (NT,) in reel time (group C runs on past DUR)."""
    raw = {g: {k: np.zeros((NT, 2)) for k in STEMS} for g in GROUPS}
    key = np.zeros(NT)
    for i, e in enumerate(ev):
        x, hit = render_event(e, i)
        g = group_of(e['t'])
        e['group'] = g
        A._add(raw[g][e['stem']], x, e['t'] - hit)
        if e['inst'] == 'kick':
            A._add(key, x.mean(1), e['t'])
    return raw, key


# ============================================================================================ bus
def fold(x):
    """Circular: the part past DUR (up to DUR + OVER) wraps onto the head (a steady-state loop)."""
    y = x[:N].copy()
    y[:_n(OVER)] += x[N:N + _n(OVER)]
    return y


def circ_sidechain(key, depth_db=5.0, attack=0.005, release=0.16):
    """A.sidechain gain from the kick key, computed on the folded (circular) key with wrap padding; returned
    over NT samples (index mod N), so group C's overhang ducks exactly like the head it folds onto."""
    kc = fold(key[:, None])[:, 0]
    p = _n(0.5)
    kk = np.concatenate([kc[-p:], kc, kc[:p]])
    g = A.sidechain(np.ones(len(kk)), kk, depth_db=depth_db, attack=attack, release=release)[:, 0][p:-p]
    return g[np.arange(NT) % N]


def gate_closed_from(t, n):
    """1 before t - 4 ms, raised-cosine to 0 at t, 0 after (the drop-out gate, applied after the reverbs)."""
    g = np.ones(n)
    a, f = _n(t), _n(GATE_EDGE)
    g[a - f:a] = 0.5 + 0.5 * np.cos(np.pi * np.arange(1, f + 1) / f)
    g[a:] = 0.0
    return g


def tape_stop(x):
    """epic_sfx.tape_stop_fx at 26.1333 s over 0.4 s (silent from 26.5333), entered with a 10 ms crossfade so the
    STFT low-pass of the stop segment never clicks. Linear in x (fixed curves), so it runs per stem."""
    t0, d = TAPE_STOP
    y = E.tape_stop_fx(x, t0, d)
    i0, xf = _n(t0), _n(0.010)
    w = (0.5 - 0.5 * np.cos(np.pi * np.arange(xf) / xf))[:, None]
    y[i0:i0 + xf] = x[i0:i0 + xf] * (1 - w) + y[i0:i0 + xf] * w
    y[_n(t0 + d):] = 0.0
    return y


def tamer_gain(x, over_db, ratio, attack, release):
    """Fast soft-knee compressor gain (linear) for the drums stem: threshold = the stem's active RMS (10 ms windows,
    top 40 dB) + over_db. Shaves the kick / taiko / trailer peaks so the bus limiter only touches rare hits."""
    p = np.square(A._st(x)).max(1)
    lv = 10 * np.log10(np.maximum(uniform_filter1d(p, _n(0.01)), 1e-20))
    act = lv > lv.max() - 40
    thr = 10 * np.log10(np.mean(p[act])) + over_db
    return undb(A.compressor_gain(x, thresh_db=thr, ratio=ratio, knee_db=6.0, attack=attack, release=release,
                                  rms=0.002))


def limiter_circular(x, ceiling_db):
    """A.limiter_gain on the loop: computed on [tail | x | head] so lookahead and release see across the seam."""
    p = _n(0.25)
    xx = np.concatenate([x[-p:], x, x[:p]])
    return A.limiter_gain(xx, ceiling_db, release=LIM_RELEASE)[p:-p]


def bus(raw, key):
    """Raw groups -> (mix, stems, info). Each stage is linear or one gain curve shared by all stems."""
    sc = circ_sidechain(key)
    sc_bass = circ_sidechain(key, depth_db=BASS_DUCK_DB, attack=0.003, release=0.12)
    tame = tamer_gain(sum(raw[g]['drums'] for g in GROUPS) * undb(STEM_DB['drums']), *TAME)
    st = {k: np.zeros((NT, 2)) for k in STEMS}
    for g, (ga, gb) in GROUPS.items():
        for k in STEMS:
            x = raw[g][k] * undb(STEM_DB[k])
            if not np.any(x):
                continue
            if k in ('harmony', 'lead', 'fx'):
                x = x * sc[:, None]
            if k == 'bass':
                x = x * sc_bass[:, None]
            if k == 'drums':
                x = x * tame[:, None]
            y = A.reverb(x, 'studio', wet_db=-18.0)[:NT]
            if k in ('harmony', 'lead', 'fx'):
                y += A.reverb(x, 'hall', wet_db=-22.0, dry=0.0)[:NT]
            if g == 'A':
                y = y * gate_closed_from(DROP_OUT[0], NT)[:, None]
            elif g == 'B':
                y[:_n(ga)] = 0.0
                y = tape_stop(y)
            else:
                y[:_n(ga)] = 0.0
            st[k] += y
    lost = max(float(np.abs(v[_n(DUR + OVER):]).max()) for v in st.values())
    pre_peak = max(float(np.abs(v).max()) for v in st.values())
    folded = {k: fold(st[k]) for k in STEMS}
    pre = sum(folded.values())
    g = TARGET_LUFS - A.loudness(pre)
    for _ in range(12):
        gl = limiter_circular(pre * undb(g), TP_CEILING - 0.3)
        y = pre * undb(g) * gl[:, None]
        L = A.loudness(y)
        if abs(L - TARGET_LUFS) < 0.02:
            break
        g += TARGET_LUFS - L
    curve = undb(g) * gl
    DEBUG.update(gl=gl, pre=pre * undb(g), folded=folded, g=g)
    stems = {k: v * curve[:, None] for k, v in folded.items()}
    mix = sum(stems.values())
    info = dict(lufs=round(A.loudness(mix), 3), true_peak_dbtp=round(A.true_peak(mix), 3),
                lra=round(A.loudness_range(mix), 2), master_gain_db=round(float(g), 2),
                limiter_max_gr_db=round(float(-A.db(gl.min())), 3),
                limiter_gr_over_0p5db_s=round(float(np.sum(gl < undb(-0.5)) / SR), 4),
                limiter_gr_over_2db_s=round(float(np.sum(gl < undb(-2.0)) / SR), 4),
                sidechain_max_db=round(float(A.db(sc.min())), 2),
                drum_tamer_max_db=round(float(A.db(tame.min())), 2),
                drum_tamer_over_1db_s=round(float(np.sum(tame < undb(-1.0)) / SR), 4),
                overhang_lost_dbfs_rel=round(float(A.db(lost / (pre_peak + 1e-12))), 1))
    return mix, stems, info


def hook_b(stems):
    """Hook B (Trial) stems from hook A's processed stems (same gains, so the splice is sample-identical)."""
    i_src, i_head, i_fade = _n(HOOKB['src']), _n(HOOKB['head']), _n(HOOKB['fade'])
    i_body, i_in = _n(HOOKB['body']), _n(HOOKB['fade_in'])
    out = {}
    for k, v in stems.items():
        y = np.zeros_like(v)
        seg = v[i_src:i_src + i_head + i_fade].copy()
        seg[i_head:] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(1, i_fade + 1) / i_fade))[:, None]
        y[:i_head + i_fade] = seg
        y[i_body:] = v[i_body:]
        y[i_body:i_body + i_in] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(i_in) / i_in))[:, None]
        out[k] = y
    return out


def render_all():
    E.register(samples=False)
    ev = compose()
    raw, key = render_groups(ev)
    mix, stems, info = bus(raw, key)
    stems_b = hook_b(stems)
    mix_b = sum(stems_b.values())
    return ev, mix, stems, info, mix_b, stems_b


# ============================================================================================ build
def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def _pcm24(x):
    """The exact bytes A._write_wav(…, 24) writes for x (for bit-identity checks)."""
    q = np.clip(np.round(A._st(x) * 8388607.0), -8388608, 8388607).astype('<i4')
    return q.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes()


def section_table():
    rows = []
    layers = {0: 'v1 motif: pad LP 700 + sub root, soft kick f0, epiano D5 / F5',
              1: '+ hats 8ths -9', 2: '+ string ostinato 16ths LP 1100',
              3: 'hats out (clean), pad LP 1300, taiko 16th fill 7.467-8.533',
              4: 'drums in: kick 1 & 3, clap 4&, hats 8ths', 5: '+ 808 (sub root out)',
              6: 'drums + 808 out beats 0-1, shimmer in, back 13.867, taiko fill 14.4',
              7: 'half-time: kick 1, clap 3, strings 8ve down, 808 hp 120 Hz (braam owns the sub)', 8: '+2 dB (tonal +1.5), strings 8ve up, trailer_hit 1 & 3, motif 8ve up',
              9: '+ hats 16ths', 10: 'peak clutter: taiko 8ths, 16th kick fill beat 4',
              11: 'drums out 23.467, strings out 24.0, 808 out 24.533, pad only; DROP-OUT 25.067-25.600',
              12: 'full clutter one beat (808 hp 120 Hz: sub left to the SFX); tape stop 26.133 / 0.4 s; silence to 27.733',
              13: 'restart = score bar 0 + warm EP Dm chord', 14: 'score bar 1, hats -12',
              15: 'score bar 3 material, VII turnaround -> frame 0 Dm'}
    for b in range(BARS):
        rows.append(dict(bar=b, t0=round(T(b), 4), t1=round(T(b + 1), 4), f0=64 * b, f1=64 * (b + 1) - 1,
                         chord=CHORD_OF_BAR[b], score_bar=SCORE_BAR[b], layers=layers[b]))
    return rows


def _deps():
    return {os.path.relpath(p, REPO): _sha(p) for p in (
        os.path.abspath(__file__), os.path.join(HERE, 'audio.py'), os.path.join(SFXDIR, 'epic_music.py'),
        os.path.join(SFXDIR, 'epic_sfx.py'))}


def build(out=OUT):
    ev, mix, stems, info, mix_b, stems_b = render_all()
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    os.makedirs(os.path.join(out, 'stems_hookb'), exist_ok=True)
    full = os.path.join(out, 'music_full.wav')
    fb = os.path.join(out, 'music_hookb.wav')
    A._write_wav(full, mix, 24)
    A._write_wav(fb, mix_b, 24)
    paths, paths_b = {}, {}
    for k in STEMS:
        paths[k] = os.path.join(out, 'stems', 'music_stem_%s.wav' % k)
        A._write_wav(paths[k], stems[k], 24)
        paths_b[k] = os.path.join(out, 'stems_hookb', 'music_hookb_stem_%s.wav' % k)
        A._write_wav(paths_b[k], stems_b[k], 24)
    os.makedirs(AUD, exist_ok=True)                  # the BRIEF §12 names, as relative symlinks (default out only)
    for nm, tgt in ((('pehle_wala_music_A.wav', full), ('pehle_wala_music_B.wav', fb))
                    if os.path.abspath(out) == os.path.abspath(OUT) else ()):
        ln = os.path.join(AUD, nm)
        if os.path.islink(ln) or os.path.exists(ln):
            os.remove(ln)
        os.symlink(os.path.relpath(tgt, AUD), ln)
    meta = dict(module=MODULE, file=full, sha256=_sha(full), hookb=dict(file=fb, sha256=_sha(fb)),
                stems={k: dict(path=p, sha256=_sha(p)) for k, p in paths.items()},
                stems_hookb={k: dict(path=p, sha256=_sha(p)) for k, p in paths_b.items()},
                dur=DUR, frames=1024, samples=N, sr=SR, bits=24, bpm=BPM, beat_s=BEAT, bar_s=BAR, bars=BARS,
                key=KEY, progression='i-VI-III-VII (Dm-Bb-F-C), one chord per bar', seed=SEED,
                drop_out=DROP_OUT, tape_stop=dict(t0=TAPE_STOP[0], dur=TAPE_STOP[1], silent_from=sum(TAPE_STOP),
                                                    silent_to=RESTART),
                restart=RESTART, groups=GROUPS, fold_overhang_s=OVER, hookb_plan=HOOKB,
                target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING, sections=section_table(), bus=info,
                hookb_bus=dict(lufs=round(A.loudness(mix_b), 3), true_peak_dbtp=round(A.true_peak(mix_b), 3)),
                n_events=len(ev), events=ev, deps_sha256=_deps(),
                source='procedural numpy (this file + epic_music / epic_sfx / audio building blocks); original, '
                       'owned, no samples of songs, no AI model, nothing trending')
    json.dump(meta, open(os.path.join(out, 'music_full.json'), 'w'), indent=1)
    print(json.dumps(dict(file=full, sha256=meta['sha256'], hookb=meta['hookb'], n_events=len(ev),
                          hookb_bus=meta['hookb_bus'], **info), indent=1))
    return meta


# ============================================================================================ verify helpers
def _ffprobe(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,'
                        'bits_per_sample,duration_ts,duration', '-of', 'json', p],
                       capture_output=True, text=True, check=True)
    return json.loads(o.stdout)['streams'][0]


def _ebur128(p):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    tail = o.stderr[o.stderr.rfind('Summary:'):]

    def grab(label):
        m = re.search(label + r':\s+(-?[\d.]+|-inf)', tail)
        return float(m.group(1)) if m and m.group(1) != '-inf' else None
    return dict(I_lufs=grab('I'), LRA_lu=grab('LRA'), TP_dbtp=grab('Peak'))


def _rms_db(x, a, b):
    s = x[_n(a):_n(b)]
    return round(float(A.db(np.sqrt(np.mean(np.square(s))) + 1e-15)), 1) if len(s) else None


def flux_onsets(x, hop=48, nfft=1024, delta=0.12, min_gap=0.035):
    """Spectral-flux onset times (s) of x: 1 ms hop, log-magnitude half-wave flux, adaptive threshold (moving median
    + delta x max), local maxima at least min_gap apart. Times carry the STFT bias (calibrate with clicks)."""
    m = A._mono(np.asarray(x, dtype=np.float64))
    _, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
    fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 1000), axis=1), 0).sum(0)
    tt = tt[1:]
    fl = fl / (fl.max() + 1e-20)
    from scipy.ndimage import median_filter
    thr = median_filter(fl, 301) + delta
    loc = (fl == maximum_filter1d(fl, int(min_gap * SR / hop) | 1)) & (fl > thr)
    return tt[loc], fl[loc], (tt, fl)


def click_bias(times):
    """flux_onsets' timing bias: synthetic 1 ms clicks placed exactly at `times`."""
    x = np.zeros(N)
    c = A.bp(np.r_[np.zeros(64), np.ones(48), np.zeros(4000)], 300, 8000, 2)
    for t in times:
        A._add(x, c, t - 64 / SR)
    det, _, _ = flux_onsets(x)
    dev = [float(d - times[np.argmin(np.abs(np.asarray(times) - d))]) for d in det]
    return float(np.median(dev)), len(det)


def env_onset(x, t, pre=0.03, post=0.03, frac=0.1, smooth=0.0005):
    """Precise onset near an expected time t: the first sample in [t - pre, t + post] where the 0.5 ms smoothed
    |x| exceeds frac x its max in that window, minus the level that was already there before."""
    a, b = _n(t - pre), _n(t + post)
    s = np.abs(A._mono(x[max(a, 0):b]))
    s = uniform_filter1d(s, max(1, _n(smooth)))
    base = np.median(s[:_n(pre * 0.5)]) if _n(pre * 0.5) > 0 else 0.0
    pk = s.max()
    if pk <= base * 1.5 + 1e-9:
        return None
    j = int(np.argmax(s > base + frac * (pk - base)))
    return (max(a, 0) + j) / SR


def mf_lag(sig, tmpl, p0, search=0.03, L=0.03, hp_hz=300.0):
    """Matched filter: lag (s) and normalised correlation of the first L s of `tmpl` against `sig` around sample p0
    (where tmpl's first sample is scheduled), +-search s, circular (loop) indexing. Both are high-passed first (the
    same zero-delay-difference filter on both), so the attack, not a low periodic tone, sets the lag (no cycle slips)."""
    s = A.hp(A._mono(sig), hp_hz, 4)
    w = A.hp(A._mono(tmpl), hp_hz, 4)[:_n(L)]
    S = _n(search)
    seg = s[np.arange(p0 - S, p0 + S + len(w)) % len(s)]
    c = signal.correlate(seg, w, mode='valid')
    e = np.sqrt(np.convolve(seg ** 2, np.ones(len(w)), mode='valid') * np.sum(w ** 2)) + 1e-20
    j = int(np.argmax(c))                      # raw correlation: the direct sound, not a quieter early reflection
    return (j - S) / SR, float(c[j] / e[j])


def event_timing(ev, stem_sig, pick, hp_hz=300.0):
    """Re-render the picked events (same index -> same seed, same gain and pan), sum the ones that start on the same
    sample into one composite template, and measure where that composite sits in its stem (matched filter)."""
    E.register(samples=False)
    groups = {}
    for i, e in enumerate(ev):
        if pick(e):
            x, hit = render_event(e, i)
            p = _n(e['t'])
            groups.setdefault(p, []).append((x, _n(e['t'] - hit) - p, e))
    out = []
    for p, items in sorted(groups.items()):
        o0 = min(o for _, o, _ in items)
        tmpl = np.zeros((max(o + len(x) for x, o, _ in items) - o0, 2))
        for x, o, _ in items:
            tmpl[o - o0:o - o0 + len(x)] += x
        lag, nc = mf_lag(stem_sig, tmpl, p + o0, hp_hz=hp_hz)
        e0 = items[0][2]
        out.append(dict(t=p / SR, bar=e0['bar'], beat=e0['beat'], insts='+'.join(sorted(e['inst'] for _, _, e in items)),
                        lag_ms=round(lag * 1000, 3), corr=round(nc, 3)))
    return out


def chroma(x, a, b, lo=110.0, hi=1100.0):
    s = A._mono(x)[_n(a):_n(b)]
    S = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    f = np.fft.rfftfreq(len(s), 1.0 / SR)
    m = (f >= lo) & (f <= hi)
    pc = np.round(12 * np.log2(f[m] / 440.0) + 69).astype(int) % 12
    c = np.bincount(pc, weights=S[m], minlength=12)
    return c / (c.max() + 1e-20)


def band_rms_db(x, a, b, lo, hi):
    s = A._mono(x)[_n(a):_n(b)]
    S = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    f = np.fft.rfftfreq(len(s), 1.0 / SR)
    tot = S.sum() + 1e-30
    return round(float(10 * np.log10(S[(f >= lo) & (f < hi)].sum() / tot + 1e-30)), 1)


def short_term(x, a, b):
    """Max and median momentary (400 ms) loudness inside [a, b)."""
    tt, lc = A.loudness_curve(x, 0.4, 0.05)
    m = (tt >= a) & (tt < b)
    return (round(float(lc[m].max()), 1), round(float(np.median(lc[m])), 1)) if m.any() else (None, None)


# ============================================================================================ verify
def verify(out=OUT):
    full = os.path.join(out, 'music_full.wav')
    fb = os.path.join(out, 'music_hookb.wav')
    meta = json.load(open(os.path.join(out, 'music_full.json')))
    ev = meta['events']
    x, sr = A.read_wav(full)
    xb, _ = A.read_wav(fb)
    rep = dict(file=full, sha256=_sha(full), sha256_matches_build=_sha(full) == meta['sha256'])
    # ---- format
    pr, prb = _ffprobe(full), _ffprobe(fb)
    rep['ffprobe'] = pr
    rep['format_ok'] = bool(sr == SR and x.shape == (N, 2) and pr['codec_name'] == 'pcm_s24le'
                            and int(pr['sample_rate']) == 48000 and int(pr['channels']) == 2
                            and int(pr['duration_ts']) == N and xb.shape == (N, 2)
                            and prb['codec_name'] == 'pcm_s24le' and int(prb['duration_ts']) == N)
    rep['samples'], rep['dur_s'] = int(x.shape[0]), round(x.shape[0] / SR, 6)
    # ---- determinism: fresh in-memory render == the files on disk, byte for byte
    ev2, mix2, stems2, _, mixb2, stemsb2 = render_all()
    raw_a = open(full, 'rb').read()
    raw_b = open(fb, 'rb').read()
    rep['bit_identical_rerender'] = dict(
        mix_A=raw_a.endswith(_pcm24(mix2)) and len(raw_a) - len(_pcm24(mix2)) == 44,
        mix_B=raw_b.endswith(_pcm24(mixb2)) and len(raw_b) - len(_pcm24(mixb2)) == 44,
        stems_A=all(open(os.path.join(out, 'stems', 'music_stem_%s.wav' % k), 'rb').read().endswith(_pcm24(stems2[k]))
                    for k in STEMS),
        stems_B=all(open(os.path.join(out, 'stems_hookb', 'music_hookb_stem_%s.wav' % k), 'rb').read()
                    .endswith(_pcm24(stemsb2[k])) for k in STEMS),
        n_events=len(ev2) == len(ev))
    rep['deps_unchanged'] = _deps() == meta['deps_sha256']
    # ---- loudness
    rep['lufs_integrated'] = round(A.loudness(x), 2)
    rep['true_peak_dbtp'] = round(A.true_peak(x), 2)
    rep['lra_lu'] = round(A.loudness_range(x), 2)
    rep['max_momentary_lufs'] = round(A.momentary_max(x), 2)
    tt, lc = A.loudness_curve(x, 0.4, 0.01)
    rep['max_momentary_at_s'] = round(float(tt[np.argmax(lc)]), 2)
    rep['ebur128'] = _ebur128(full)
    rep['hookb'] = dict(lufs_integrated=round(A.loudness(xb), 2), true_peak_dbtp=round(A.true_peak(xb), 2),
                        ebur128=_ebur128(fb))
    # ---- stems
    st = {k: A.read_wav(os.path.join(out, 'stems', 'music_stem_%s.wav' % k))[0] for k in STEMS}
    stb = {k: A.read_wav(os.path.join(out, 'stems_hookb', 'music_hookb_stem_%s.wav' % k))[0] for k in STEMS}
    rep['stems_sum_residual_dbfs'] = round(float(A.db(np.abs(sum(st.values()) - x).max() + 1e-15)), 1)
    rep['stems_hookb_sum_residual_dbfs'] = round(float(A.db(np.abs(sum(stb.values()) - xb).max() + 1e-15)), 1)
    rep['stems'] = {k: dict(lufs=(round(A.loudness(v), 2) if np.any(v) else None),
                            true_peak_dbtp=round(A.true_peak(v), 2)) for k, v in st.items()}
    rep['all_tp_ok'] = bool(max([rep['true_peak_dbtp'], rep['hookb']['true_peak_dbtp']]
                                + [v['true_peak_dbtp'] for v in rep['stems'].values()]) <= -2.0)
    # ---- grid: EM.beatgrid (music-supervisor's spectral-flux fit) on the mix and the drums stem
    beats = [k * BEAT for k in range(BARS * 4)]
    ref = np.zeros(N)
    c = A.bp(np.r_[np.zeros(64), np.ones(48), np.zeros(4000)], 300, 8000, 2)
    for t in beats:
        A._add(ref, c, t - 64 / SR)
    rep['beatgrid'] = dict(mix=EM.beatgrid(x, BPM), drums=EM.beatgrid(st['drums'], BPM),
                           click_reference=EM.beatgrid(ref, BPM))
    bg = rep['beatgrid']['mix']
    rep['beatgrid']['pass'] = bool(abs(bg['tempo'] - BPM) <= 0.2 and abs(bg['phase_s']) <= 0.015
                                   and bg['strength'] > 2)
    # ---- onsets: every detected onset vs the 16th grid; every scheduled hit vs its measured onset
    bias, _ = click_bias(beats)
    rep['onset_flux_bias_ms'] = round(bias * 1000, 2)
    det, strength, _ = flux_onsets(x)
    det = det - bias
    sx = BEAT / 4
    dev16 = (det + sx / 2) % sx - sx / 2
    strong = strength >= 0.25
    rep['onsets_mix'] = dict(n=int(len(det)), n_strong=int(strong.sum()),
                             strong_on_16th_grid_within_10ms=int(np.sum(np.abs(dev16[strong]) <= 0.010)),
                             strong_off_grid=[round(float(t), 3) for t in det[strong][np.abs(dev16[strong]) > 0.010]],
                             median_abs_dev16_ms=round(float(np.median(np.abs(dev16[strong]))) * 1000, 2))
    claps = np.array([e['t'] for e in ev if e['inst'] == 'clap'])
    off = det[strong][np.abs(dev16[strong]) > 0.010]
    burst = [bool(np.any((t - claps >= 0) & (t - claps <= 0.035))) for t in off]
    rep['onsets_mix']['off_grid_are_clap_bursts'] = burst
    rep['onsets_mix']['note'] = ('EM.clap = 3 noise bursts at 0 / 11 / 22 ms (+0.11 s tail); the flux peak picker '
                                 'takes its loudest (last) burst, so a clap reads +22..30 ms late here. Its first '
                                 'burst is measured on the grid by the matched filter (drum_hits_measured)')
    # matched filter: every scheduled drum hit and motif note vs where it actually sits in its stem
    dh = event_timing(ev, st['drums'], lambda e: e['stem'] == 'drums' and e['inst'] in
                      ('kick', 'taiko', 'clap', 'trailer_hit'))
    lags = np.array([d['lag_ms'] for d in dh])
    rep['drum_hits_measured'] = dict(n_instants=len(dh), n_events=sum(len(d['insts'].split('+')) for d in dh),
                                     max_abs_ms=round(float(np.abs(lags).max()), 3),
                                     mean_ms=round(float(lags.mean()), 3), min_corr=min(d['corr'] for d in dh),
                                     within_1_frame=int(np.sum(np.abs(lags) <= 1000 / FPS)),
                                     within_1ms=int(np.sum(np.abs(lags) <= 1.0)), hits=dh)
    # motif notes: onset of the epiano's tine ping (1 ms attack, 14 x f0) in the lead stem above 5 kHz, where the
    # previous notes' pings have decayed; a matched filter cycle-slips on these sustained FM tones under the sidechain
    hl = A.hp(A._mono(st['lead']), 5000.0, 4)
    hl = np.stack([hl, hl], 1)
    tb = np.array([d['t'] for d in dh]) / BEAT                # scheduled beat index of each drum instant
    tm = np.array([d['t'] + d['lag_ms'] / 1000 for d in dh])  # measured time of that instant
    per, off0 = np.polyfit(tb, tm, 1)
    rep['tempo_from_measured_hits'] = dict(bpm=round(60.0 / per, 5), beat0_offset_ms=round(off0 * 1000, 3),
                                           span_s=round(float(tm.max() - tm.min()), 3), n=len(tm))
    mo = []
    for t in sorted(set(e['t'] for e in ev if e['inst'] == 'ep' and e['stem'] == 'lead')):
        o = env_onset(hl, t, pre=0.03, post=0.03, frac=0.3, smooth=0.0003)
        mo.append(dict(t=t, bar=int(t // BAR), onset_ms=None if o is None else round((o - t) * 1000, 3)))
    ml = np.array([d['onset_ms'] for d in mo if d['onset_ms'] is not None])
    rep['motif_notes_measured'] = dict(n_instants=len(mo), found=len(ml), max_abs_ms=round(float(np.abs(ml).max()), 3),
                                       mean_ms=round(float(ml.mean()), 3),
                                       note='first sample of the hp-5 kHz envelope at 30 % of its rise; includes the '
                                            '3 ms attack ramp, so ~0.4-0.5 ms is the attack, not a placement error')
    rep['downbeats_kick_lag_ms'] = {str(d['bar']): d['lag_ms'] for d in dh
                                    if 'kick' in d['insts'] and abs(d['beat']) < 1e-6}
    # blind downbeat analysis on the mix: (1) low-band (30-200 Hz) energy rise across each beat, (2) harmonic change
    # (chroma distance, 110-1100 Hz) across each beat; averaged per beat position in the bar. Circular windows (the
    # bar-0 downbeat is measured across the loop seam); beats whose windows touch a silent window are skipped.
    low = A.hp(A.lp(A._mono(x), 200.0, 4), 30.0, 2)
    mx = A._mono(x)

    def cwin(sig, a, b):
        return sig[np.arange(_n(a), _n(b)) % N]

    def silent(a, b):
        return any(a < w1 and b > w0 for w0, w1 in (DROP_OUT, (sum(TAPE_STOP), RESTART)))

    def chroma_c(a, b):
        seg = cwin(mx, a, b)
        S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        f = np.fft.rfftfreq(len(seg), 1.0 / SR)
        m = (f >= 110) & (f <= 1100)
        c = np.bincount(np.round(12 * np.log2(f[m] / 440.0) + 69).astype(int) % 12, weights=S[m], minlength=12)
        return c / (np.linalg.norm(c) + 1e-20)

    rise = {k: [] for k in range(4)}
    chg = {k: [] for k in range(4)}
    for b in range(BARS):
        for k in range(4):
            t = T(b, k)
            if silent(t - 0.3, t + 0.3):
                continue
            pre_e, post_e = np.mean(cwin(low, t - 0.06, t) ** 2), np.mean(cwin(low, t, t + 0.06) ** 2)
            rise[k].append(10 * np.log10((post_e + 1e-20) / (pre_e + 1e-20)))
            chg[k].append(1.0 - float(np.dot(chroma_c(t - 0.25, t - 0.03), chroma_c(t + 0.06, t + 0.3))))
    mr = [round(float(np.mean(rise[k])), 2) for k in range(4)]
    mc = [round(float(np.mean(chg[k])), 4) for k in range(4)]
    rep['downbeat_blind'] = dict(low_band_rise_db_by_position=mr, chroma_change_by_position=mc,
                                 n_beats_by_position=[len(rise[k]) for k in range(4)],
                                 strongest_low=int(np.argmax(mr)), strongest_harmonic=int(np.argmax(mc)),
                                 strongest_position=int(np.argmax(mr)) if np.argmax(mr) == np.argmax(mc) else -1)
    # downbeat accent: low-band (30-150 Hz) energy just after bar lines vs beats 1 and 3, bars 4-10 (drums)
    lo = A.lp(A.hp(A._mono(st['drums']), 30, 2), 150, 4)
    e_lo = uniform_filter1d(lo ** 2, _n(0.03))
    on_bar = [e_lo[_n(T(b) + 0.015)] for b in range(4, 11)]
    off_bar = [e_lo[_n(T(b, k) + 0.015)] for b in range(4, 11) for k in (1, 3)]
    rep['downbeat_accent_db'] = round(float(10 * np.log10(np.mean(on_bar) / (np.mean(off_bar) + 1e-20))), 1)
    # ---- harmony: chroma of the harmony stem per bar vs the scored chord
    hm = st['harmony']
    rows = []
    for b in range(BARS):
        a0, a1 = T(b) + 0.15, T(b + 1) - 0.05
        if b == 11:
            a1 = DROP_OUT[0] - 0.01
        if b == 12:
            a1 = TAPE_STOP[0]
        cvec = chroma(hm, a0, a1)
        top3 = sorted(np.argsort(cvec)[-3:].tolist())
        want = sorted(CHORD_PCS[CHORD_OF_BAR[b]])
        rows.append(dict(bar=b, chord=CHORD_OF_BAR[b], top3=[NOTE_NAMES[i] for i in top3], match=top3 == want))
    rep['chords'] = dict(per_bar=rows, all_match=all(r['match'] for r in rows))
    # ---- section levels (momentary max / median per bar), sub band share per bar
    lv = []
    for b in range(BARS):
        a0, a1 = T(b), T(b + 1)
        mx, md = short_term(x, a0, a1)
        lv.append(dict(bar=b, chord=CHORD_OF_BAR[b], m_max=mx, m_median=md, rms_db=_rms_db(x, a0, a1),
                       sub_lt60_db_rel=band_rms_db(x, a0, a1, 20, 60) if b != 12 else
                       band_rms_db(x, a0, TAPE_STOP[0], 20, 60)))
    rep['bars'] = lv
    # ---- drop-out, tape stop, silence, restart
    i0, i1 = _n(DROP_OUT[0]), _n(DROP_OUT[1])
    rep['drop_out'] = dict(window=DROP_OUT, peak_abs=float(np.abs(x[i0:i1]).max()),
                           digital_silence=bool(np.all(x[i0:i1] == 0) and all(np.all(v[i0:i1] == 0) for v in st.values())),
                           rms_last_beat_before_dbfs=_rms_db(x, DROP_OUT[0] - BEAT, DROP_OUT[0]),
                           onset_after_ms=None)
    o = env_onset(x, DROP_OUT[1], pre=0.01, post=0.02)
    rep['drop_out']['onset_after_ms'] = None if o is None else round((o - DROP_OUT[1]) * 1000, 2)
    s0, s1 = _n(sum(TAPE_STOP)), _n(RESTART)
    rep['rewind_silence'] = dict(window=(sum(TAPE_STOP), RESTART),
                                 digital_silence=bool(np.all(x[s0:s1] == 0) and all(np.all(v[s0:s1] == 0) for v in st.values())))
    seg = A._mono(x[_n(TAPE_STOP[0] - 0.1):_n(sum(TAPE_STOP))])
    fr = []
    for k in range(0, len(seg) - _n(0.05), _n(0.05)):
        s = seg[k:k + _n(0.05)]
        S = np.abs(np.fft.rfft(s * np.hanning(len(s))))
        f = np.fft.rfftfreq(len(s), 1 / SR)
        fr.append(dict(t=round(TAPE_STOP[0] - 0.1 + k / SR, 3), rms_db=round(float(A.db(np.sqrt(np.mean(s ** 2)) + 1e-15)), 1),
                       centroid_hz=round(float((S * f).sum() / (S.sum() + 1e-20)), 0)))
    rep['tape_stop_frames'] = fr
    o = env_onset(x, RESTART, pre=0.01, post=0.02)
    rep['restart_onset_ms'] = None if o is None else round((o - RESTART) * 1000, 2)
    # ---- loop seam
    j = 0.005
    rep['loop_seam'] = dict(
        rms_last_100ms_dbfs=_rms_db(x, DUR - 0.1, DUR), rms_first_100ms_dbfs=_rms_db(x, 0, 0.1),
        rms_last_bar_dbfs=_rms_db(x, T(15), DUR),
        step_at_seam=round(float(np.abs(x[0] - x[-1]).max()), 6),
        median_sample_step=round(float(np.median(np.abs(np.diff(x, axis=0)).max(1))), 6),
        p99_sample_step=round(float(np.percentile(np.abs(np.diff(x, axis=0)).max(1), 99)), 6),
        no_fade_to_silence=bool(_rms_db(x, DUR - j, DUR) > -45),
        chroma_last_beat_top3=[NOTE_NAMES[i] for i in sorted(np.argsort(chroma(st['harmony'], DUR - BEAT, DUR))[-3:])],
        chroma_first_beat_top3=[NOTE_NAMES[i] for i in sorted(np.argsort(chroma(st['harmony'], 0.15, BEAT))[-3:])])
    # ---- hook B
    ib = _n(HOOKB['body'] + HOOKB['fade_in'])
    ih, ihf = _n(HOOKB['head']), _n(HOOKB['head'] + HOOKB['fade'])
    rep['hookb'].update(
        identical_to_A_from_s=round(HOOKB['body'] + HOOKB['fade_in'], 4),
        identical_after_splice=bool(np.array_equal(xb[ib:], x[ib:])),
        head_equals_A_bar10=bool(np.array_equal(xb[:ih], x[_n(HOOKB['src']):_n(HOOKB['src']) + ih])),
        silent_between=bool(np.all(xb[ihf:_n(HOOKB['body'])] == 0)),
        silent_window=(round(HOOKB['head'] + HOOKB['fade'], 4), round(HOOKB['body'], 4)))
    # ---- pass/fail summary
    rep['checks'] = dict(
        format=bool(rep['format_ok']), bit_identical=all(rep['bit_identical_rerender'].values()),
        lufs_minus16=abs(rep['lufs_integrated'] - TARGET_LUFS) <= 0.1 and abs(rep['ebur128']['I_lufs'] - TARGET_LUFS) <= 0.15,
        tp_le_minus2=rep['all_tp_ok'] and rep['ebur128']['TP_dbtp'] <= -2.0 and rep['hookb']['ebur128']['TP_dbtp'] <= -2.0,
        beatgrid=rep['beatgrid']['pass'] and abs(rep['tempo_from_measured_hits']['bpm'] - BPM) < 0.001,
        drum_hits_within_1ms=rep['drum_hits_measured']['within_1ms'] == rep['drum_hits_measured']['n_instants'],
        motif_notes_within_1ms=rep['motif_notes_measured']['found'] == rep['motif_notes_measured']['n_instants']
        and rep['motif_notes_measured']['max_abs_ms'] <= 1.0,
        strong_onsets_on_grid=all(rep['onsets_mix']['off_grid_are_clap_bursts']),
        downbeat_strongest=rep['downbeat_blind']['strongest_position'] == 0,
        chords=rep['chords']['all_match'],
        drop_out_silent=rep['drop_out']['digital_silence'], rewind_silent=rep['rewind_silence']['digital_silence'],
        stems_sum=rep['stems_sum_residual_dbfs'] < -120 and rep['stems_hookb_sum_residual_dbfs'] < -120,
        loop_no_fade=rep['loop_seam']['no_fade_to_silence'],
        hookb_splice=rep['hookb']['identical_after_splice'] and rep['hookb']['head_equals_A_bar10']
        and rep['hookb']['silent_between'],
        overhang_not_lost=meta['bus']['overhang_lost_dbfs_rel'] < -100)
    rep['checks'] = {k: bool(v) for k, v in rep['checks'].items()}
    rep['all_pass'] = all(rep['checks'].values())
    json.dump(rep, open(os.path.join(out, 'music_full.verify.json'), 'w'), indent=1, default=float)
    _spectro(x, os.path.join(out, 'music_full_spectrogram.png'), rep)
    _zooms(x, xb, os.path.join(out, 'music_full_zooms.png'))
    print(json.dumps(dict(checks=rep['checks'], all_pass=rep['all_pass'], lufs=rep['lufs_integrated'],
                          tp=rep['true_peak_dbtp'], ebur128=rep['ebur128'], hookb=rep['hookb']['ebur128'],
                          beatgrid=rep['beatgrid'], tempo_from_hits=rep['tempo_from_measured_hits'], drum_hits={k: v for k, v in rep['drum_hits_measured'].items()
                                                               if k != 'hits'},
                          downbeats=rep['downbeats_kick_lag_ms'], accent=rep['downbeat_accent_db'],
                          downbeat_blind=rep['downbeat_blind'],
                          motif=rep['motif_notes_measured'],
                          onsets=rep['onsets_mix'], max_momentary=(rep['max_momentary_lufs'], rep['max_momentary_at_s']),
                          bars=[(r['bar'], r['m_max'], r['m_median']) for r in rep['bars']]), indent=1, default=float))
    return rep


# ============================================================================================ pictures
def _font(sz):
    return A._font(sz)


def _spectro(x, path, rep):
    from PIL import Image, ImageDraw
    W, H = 2048, 900
    top = 64
    img = A.spectro_image(x, W, H - top, None, '', '')
    sheet = Image.new('RGB', (W, H), (10, 8, 12))
    sheet.paste(img, (0, top))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 4), 'pehle_wala music_full.wav  112.5 BPM  D minor  16 bars = 34.133 s', fill=(250, 245, 240),
            font=_font(18))
    dr.text((8, 28), '%.2f LUFS  %.2f dBTP  LRA %.1f  |  bar lines orange (labels = bar:chord), drop-out / silence '
                     'windows red, tape stop cyan' % (rep['lufs_integrated'], rep['true_peak_dbtp'], rep['lra_lu']),
            fill=(190, 180, 200), font=_font(13))
    for b in range(BARS + 1):
        xx = int(min(T(b) / DUR, 1.0) * (W - 1))
        dr.line([(xx, top + 40), (xx, H - 18)], fill=(255, 140, 40), width=1)
        if b < BARS:
            dr.text((xx + 3, top + 44), '%d:%s' % (b, CHORD_OF_BAR[b]), fill=(255, 190, 120), font=_font(13))
    for (a, b) in (DROP_OUT, (sum(TAPE_STOP), RESTART)):
        dr.rectangle([int(a / DUR * W), H - 16, int(b / DUR * W), H - 4], fill=(230, 50, 40))
    xa, xb2 = int(TAPE_STOP[0] / DUR * W), int(sum(TAPE_STOP) / DUR * W)
    dr.rectangle([xa, H - 16, xb2, H - 4], fill=(80, 230, 255))
    sheet.save(path)


def _zooms(x, xb, path):
    from PIL import Image, ImageDraw
    spans = [('hook A 0-2.7 s (f0 soft kick + D5, beat 2 F5, bar 1)', x, 0.0, 2.7),
             ('drums in 7.2-9.8 s (taiko fill -> bar 4 downbeat 8.533)', x, 7.2, 9.8),
             ('thin -> drop-out -> payoff -> tape stop -> rewind silence -> restart 24.4-28.6 s', x, 24.4, 28.6),
             ('loop seam: 33.133-34.133 | 0-1.0 (cyan = seam)', x, None, None),
             ('hook B 0-3.2 s (bar-10 clutter, fade, silence, body from 2.667)', xb, 0.0, 3.2),
             ('peak clutter bar 10 21.2-23.6 s', x, 21.2, 23.6)]
    W, H = 1000, 380
    sheet = Image.new('RGB', (W * 2, H * 3), (0, 0, 0))
    for k, (lab, sig, a, b) in enumerate(spans):
        if a is None:
            seg = np.concatenate([sig[_n(DUR - 1.0):], sig[:_n(1.0)]])
            off = DUR - 1.0
        else:
            seg, off = sig[_n(a):_n(b)], a
        im = A.spectro_image(seg, W, H, 1.0 if a is None else None, lab,
                             't0 = %.3f s; white ticks (top of the spectrogram) = beats, tall cyan = bar lines'
                             % off)
        dr = ImageDraw.Draw(im)
        dur = len(seg) / SR
        for kk in range(-4, BARS * 4 + 5):
            tb = kk * BEAT
            if a is None:
                loc = tb - (DUR - 1.0) if tb >= DUR - 1.0 - 1e-9 else (tb + 1.0 if tb <= 1.0 else None)
                if tb > DUR + 1e-9:
                    continue
            else:
                loc = tb - a if a - 1e-9 <= tb <= b + 1e-9 else None
            if loc is None or loc < 0 or loc > dur:
                continue
            xx = int(min(loc / dur, 1.0) * (W - 1))
            tall = kk % 4 == 0
            y0 = 44 + int(H * 0.26) + 4                  # top of A.spectro_image's spectrogram area
            dr.line([(xx, y0), (xx, y0 + (34 if tall else 14))], fill=(120, 255, 255) if tall else (235, 235, 245),
                    width=3 if tall else 2)
        sheet.paste(im, ((k % 2) * W, (k // 2) * H))
    sheet.save(path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', nargs='?', default='all', choices=['build', 'verify', 'all'])
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args()
    if a.cmd in ('build', 'all'):
        build(a.out)
    if a.cmd in ('verify', 'all'):
        verify(a.out)
