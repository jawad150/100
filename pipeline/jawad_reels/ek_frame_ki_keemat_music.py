#!/usr/bin/env python3
"""ek_frame_ki_keemat_music.py: ORIGINAL score for Reel 3 · C08 "Ek Frame ki Keemat" (owner: music-supervisor).

Procedural and deterministic (fixed seeds, numpy/scipy only). Every sound is synthesised in this repo: the instruments
of workspace/brand_reels/sfx/epic_music.py (EM.string_note, EM.hat, EM.bass808, EM.kick as the sidechain key) and the
epic_sfx sounds harmonium_swell, dhol_hit, trailer_hit, shepard_riser and reverse_cymbal. No sample of any song, no AI
model, no trending audio. Licence: original work made for @jawad_mp4.
Plan: brand_reels/design/reels/ek_frame_ki_keemat/BRIEF.md §12 (variant 'c08_epic' of epic_music's desi_epic);
map: brand_reels/design/reels/ek_frame_ki_keemat/MUSIC_ek_frame_ki_keemat.md.

Grid: 100 BPM = 18 frames per beat at 30 fps, bar 2.4 s, 14 bars = 33.6 s = 1,612,800 samples at 48 kHz.
Key D, Phrygian-dominant colour (EM.PHRYG_DOM: D Eb F# G A Bb C), Sa = D4 293.66 Hz.

    bar 0      0.0-2.4    cold: harmonium Sa-Pa-Sa swell (peak 3.456); the loop bar's tails wrap in at frame 0
    bars 1-4   2.4-12.0   strings 8th ostinato enters at 2.4 (LP 900, -6): i i bVI i; swells bars 2, 4
    bar 5      12.0-14.4  re-hook: strings thin (-9) on bII (Eb), the Phrygian question
    bar 6      14.4-16.8  "resolved with": back to i, -5 (a 1 dB lift), LP 900 -> 1200; swell bar 6
    bars 7-10  16.8-26.4  corridor: LP 1200 -> 1500 and -5 -> -3 by bar 10; bVI i bVI bVII; swells bars 8, 10;
                          felt taiko (trailer_hit pitch 0.887 = A1, LP 1500) on beats 1 + 3 of bars 8-10, -14 -> -8;
                          shepard_riser 2.2 s and reverse_cymbal 1.2 s aimed at 26.4, cut dead at 25.8
    gate       25.8-26.4  DROP-OUT: the whole bus (after the reverb) is digital silence 25.800-26.392; 4 ms edges
                          25.796-25.800 and 26.392-26.396, so f774 is silent and the drop's attack is untouched
    bar 11     26.4-28.8  DROP on i: dhol_hit (tuned D2) 0 dB at 26.4, chaal (2&, 3, 4&), hats 8ths -6, 808 D2 -6,
                          strings LP 1500 -3, the bar 10 harmonium swell continues
    bar 12     28.8-31.2  resolve on bVI: chaal -8, 808 -9, no hats, strings LP 1200 -5, swell -6
    bar 13     31.2-33.6  loop bar on bVII (C): strings LP 900 -7, harmonium seam drone (30.0 -> peak 0.72 s after the
                          loop), reverse_cymbal 2.4 s ending exactly on 33.6; bVII -> i across the seam into bar 0

Bus (epic_music's chain, made loop-safe and stem-exact): stem trims (EM.STEM_DB), a 6 dB peak shave on the perc stem
(dhol transients), sidechain of strings + harmonium + fx to the dhol-chaal kick key (3 dB, 5/160 ms), studio reverb
-18 dB per stem (linear, so the stems still sum), two extra bars rendered and folded back onto the start (= circular:
the loop bar's drone and tails continue into frame 0), the drop-out gate, gain + 4x true-peak limiter at -3.3 dBFS
iterated to -16.0 LUFS integrated (TP <= -3.0 dBTP). No fade inside the reel. The stems go through the same gains, so
strings + harmonium + perc + bass + fx == music_full.wav.

CLI (run from pipeline/jawad_reels; heavy work through tools/heavy.sh):
    python3 ek_frame_ki_keemat_music.py render [--out DIR]  -> DIR/music_full.wav (+ ek_frame_ki_keemat_music.wav link),
                                                              DIR/stems/{strings,harmonium,perc,bass,fx}.wav,
                                                              DIR/music_full.json (map, events, render numbers)
    python3 ek_frame_ki_keemat_music.py verify [--out DIR]  -> DIR/music_full.verify.json + DIR/qa/*.png
    python3 ek_frame_ki_keemat_music.py mix [--hook A|B] [--vo WAV] [--sfx WAV] [--vo-b WAV] [--sfx-b WAV]
                                                           -> <RW>/audio/ek_frame_ki_keemat_mix.wav (A), _vo_sfx.wav
                                                              (B, no music), stems, report (epic_mix.mix_reel); hook B:
                                                              ek_frame_ki_keemat_hookb_{mix,vo_sfx}.wav
    python3 ek_frame_ki_keemat_music.py envelopes          -> <RW>/audio/ek_frame_ki_keemat_env.json (per-frame RMS
                                                              dBFS of the A stems, for the S3-03 audio lanes)

    import ek_frame_ki_keemat_music as MU
    res = MU.render()            # dict(mix, stems, info, events); MU.write(res) writes the files
    import epic_music as EM; EM.render('c08_epic', dur=36.0, bpm=100, key='D', drop_bar=11, seed=8)  # quick preview
                                 # through epic_music's own (non-loop) bus; the deliverable is MU.render()
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
MODULE = 'ek_frame_ki_keemat'
DUR, BPM, FPS = 33.6, 100.0, 30
BEAT = 60.0 / BPM                               # 0.6 s = 18 frames
BAR = 4 * BEAT                                  # 2.4 s = 72 frames
BARS = 14
N = _n(DUR)                                     # 1,612,800 samples
assert N == 1612800 and abs(BARS * BAR - DUR) < 1e-9
KEY, ROOT, SEED = 'D', 62, 8                    # ROOT = D4 (MIDI 62) = Sa 293.66 Hz
OVER = 2 * BAR                                  # two extra bars rendered for tails (the seam drone runs to 36.6 s),
                                                # folded back onto the start
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
OUT = os.path.join(RW, 'music')
TARGET_LUFS, TP_CEILING = -16.0, -3.0           # -16 LUFS alone (epic_mix re-levels it to -18 under the VO)
STEMS = ('strings', 'harmonium', 'perc', 'bass', 'fx')
STEM_DB = dict(strings=EM.STEM_DB['harmony'], harmonium=EM.STEM_DB['harmony'], perc=EM.STEM_DB['drums'],
               bass=EM.STEM_DB['bass'], fx=EM.STEM_DB['fx'])
FALLBACK = dict(strings='harmony', harmonium='harmony', perc='drums', bass='bass', fx='fx')   # for EM.render
DUCKED = ('strings', 'harmonium', 'fx')         # sidechained to the kick key (epic_music: harmony + lead + fx)
SC_DEPTH_DB = 3.0                               # epic_music pumps 5 dB; 3 dB keeps the drop's strings in front


def T(bar, beat=0.0):
    """Reel time (s) of bar `bar`, beat `beat` (both from 0), rounded to the microsecond."""
    return round((bar * 4 + beat) * BEAT, 6)


DROP_BAR = 11
DROP_T = T(DROP_BAR)                            # 26.4 s = f792, the payoff
GATE = (T(10, 3), DROP_T)                       # 25.8 -> 26.4: the drop-out (one beat)
EDGE = 0.004                                    # gate edges lie OUTSIDE the drop-out: closes 25.796-25.800 (silent
                                                # from f774 on), opens 26.392-26.396 (the drop's dhol starts at 26.397 =
                                                # hit 26.400 - 3 ms, so its attack is untouched)
LOOP_CYMBAL = (2.4, -8.0)                       # reverse_cymbal ending exactly on DUR (into frame 0)

# ostinato harmony per bar: PHRYG_DOM degree shift of the 8th-note figure (0 = i D, -2 = bVI Bb, -1 = bVII C,
# +1 = bII Eb). Figure = desi_epic's (0, 0, 1, 0, 0, 0, 2, 1), one octave higher than desi_epic so every string
# fundamental sits >= 233 Hz (Bb3), above the male VO's F0 (bible §5.3 VO-register rule).
CHORD = {1: 0, 2: 0, 3: -2, 4: 0, 5: 1, 6: 0, 7: -2, 8: 0, 9: -2, 10: -1, 11: 0, 12: -2, 13: -1}
CHORD_NAME = {0: 'i (D)', -2: 'bVI (Bb)', -1: 'bVII (C)', 1: 'bII (Eb)'}
FIGURE = (0, 0, 1, 0, 0, 0, 2, 1)
STR_OCT = 0
ACCENT = (2.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0)  # dB per 8th: downbeat +2, beats +1, off-beats 0 (a clear pulse)


def _bar_of(t):
    """Bar index of reel time t (robust to float error at bar lines)."""
    return int(np.floor(t / BAR + 1e-6))


def strings_level(t):
    """(gain dB, low-pass Hz) of the string ostinato at time t (BRIEF §12; bars 1-4 sit 1 dB under the brief's -5 so
    bar 6's "alive" lift and the corridor build read as an arc: bible §5.4, lower the intro, not the drop)."""
    bar = _bar_of(t)
    if bar <= 4:
        return -6.0, 900.0
    if bar == 5:
        return -9.0, 900.0                                            # re-hook: thin
    if bar == 6:
        return -5.0, 900.0 + 300.0 * (t - T(6)) / BAR                 # 900 -> 1200 over the bar
    if bar <= 9:
        p = (t - T(7)) / (T(10) - T(7))                               # 0 at 16.8 -> 1 at 24.0
        return -5.0 + 2.0 * p, 1200.0 + 300.0 * p
    if bar <= 11:
        return -3.0, 1500.0
    if bar == 12:
        return -5.0, 1200.0
    return -7.0, 900.0                                                # bar 13: loop bar, cold colour


SWELLS = [(0, -3.0), (2, -3.0), (4, -3.0), (6, -3.0), (8, -3.0), (10, -3.0), (12, -6.0)]   # (bar, dB), 2 bars each
SEAM_SWELL = (T(12, 2), 6.0, -6.0)              # loop bar's cold drone: starts 30.0, peaks 34.32 = 0.72 s after the
                                                # seam (folded), so frame 0 opens on the drone instead of near-silence
TAIKO = [T(b, k) for b in (8, 9, 10) for k in (0, 2)]           # 19.2 20.4 21.6 22.8 24.0 25.2
TAIKO_PITCH = 55.0 / 62.0                       # trailer_hit f0 62 Hz x 0.887 = A1 55 Hz (Pa); the brief's 0.9, in tune
DHOL_PITCH = E.midi_hz(ROOT - 24) / 58.0        # dhol_hit dagga 58 Hz x 1.266 = D2 73.4 Hz (Sa); shell modes land on A3,
                                                # D4, C5. desi_epic's 1.0 / 1.25 put the dagga on Bb and a shell mode on F3
                                                # (F natural against the scale's F#)
CHAAL = [(0.0, -2.0), (1.5, -5.0), (2.0, -4.5), (3.5, -6.0)]   # desi_epic's chaal: (beat, dB): 1, 2&, 3, 4&; 2& / 3
                                                # 1-1.5 dB under desi_epic so the drop hit stays the loudest moment
                                                # (session 4, rebuilt kit: the 2& + 3 pair read 0.4 LU over it)
PERC_SHAVE_DB = 6.0                             # peak shave on the perc stem (dhol transients) before the bus, so the bus
                                                # limiter only touches the drop hit

SECTIONS = [  # (name, t0, t1, bars, picture, music)
    ('cold', 0.0, T(1), '0', 'S1 frame plays, pause 0.3, layers separate', 'harmonium swell (Sa-Pa-Sa), loop tails'),
    ('explode / orbit / fly-through', T(1), T(5), '1-4', 'S2-01..S2-03, counter 12, tags',
     'strings 8ths enter 2.4 (LP 900, -6): i i bVI i; swells bars 2, 4'),
    ('re-hook', T(5), T(6), '5', 'stop on pane 12, flick off/on', 'strings thin -9 on bII (Eb)'),
    ('resolved "with"', T(6), T(7), '6', 'frame alive, C3 approach', 'i, -5 lift, LP 900 -> 1200, swell bar 6'),
    ('corridor / surge / lanes / rush', T(7), GATE[0], '7-10.75',
     'S3-01..S3-04', 'LP 1200 -> 1500, -5 -> -3; bVI i bVI bVII; taiko 19.2-25.2; swells 8, 10; shepard + cymbal'),
    ('drop-out', GATE[0], GATE[1], '10.75-11', 'single stack frozen, play click 26.067', 'silence (gate)'),
    ('DROP', T(11), T(12), '11', 'PAYOFF: frame plays, EK FRAME KI keemat', 'dhol 0 dB, chaal, hats, 808, strings -3'),
    ('resolve', T(12), T(13), '12', 'end card builds (29.4)', 'bVI, chaal -8, 808 -9, swell -6'),
    ('loop bar', T(13), DUR, '13', 'card holds, loop_world crossfade', 'bVII strings LP 900 -7, reverse cymbal -> 33.6'),
]


# ============================================================================================ composition
def _put(s, stem, x, t, gain_db=0.0, p=0.0, hit=0.0, cut=None, name='', events=None):
    """Place x with its hit on reel time t. cut: hard stop (s, reel time) with a 4 ms fade (the pre-drop 'suck')."""
    x = np.asarray(x, dtype=np.float64)
    x = A.pan(x, p) if p else A._st(x)
    t0 = t - hit
    if cut is not None and cut < t0 + len(x) / SR:
        k, f = max(0, _n(cut - t0)), _n(EDGE)
        x = x.copy()
        x[k:] = 0.0
        if k > 0:
            lo = max(0, k - f)
            x[lo:k] *= np.linspace(1.0, 0.0, k - lo)[:, None]
    key = stem if stem in s.st else FALLBACK[stem]
    A._add(s.st[key], x * undb(gain_db), t0)
    if events is not None:
        b_ = _bar_of(t)
        events.append(dict(t=round(t, 4), bar=b_, beat=round((t - T(b_)) / BEAT, 3), name=name,
                           stem=stem, gain_db=round(float(gain_db), 2), **({'cut': cut} if cut is not None else {})))


def _key(s, t, punch=0.5):
    """Kick into the sidechain key only (inaudible): the pump of the drop bars (as desi_epic)."""
    A._add(s.kick_key, EM.kick(s.r, punch), t)


def style_c08(s, drop_bar=DROP_BAR, events=None):
    """The c08_epic arrangement on an EM.Song (BRIEF §12). Registered as EM.STYLES['c08_epic']."""
    r = s.r
    nbars = min(BARS, int(round(s.dur / BAR)))
    # harmonium Sa-Pa-Sa drone swells, two bars each, peak at 0.72 x 4.8 = 3.456 s after the bar line
    for k, (bar, g) in enumerate(SWELLS):
        if bar >= nbars:
            continue
        sw = A.sound('harmonium_swell', duration=2 * BAR, notes=(ROOT - 12, ROOT - 5, ROOT), seed=k)
        _put(s, 'harmonium', sw, T(bar), g, hit=0.0, name='harmonium_swell D3 A3 D4 (peak %.3f)' % (T(bar) + sw.hit),
             events=events)
    if s.dur > DUR:
        t0, d, g = SEAM_SWELL
        sw = A.sound('harmonium_swell', duration=d, notes=(ROOT - 12, ROOT - 5, ROOT), seed=len(SWELLS))
        _put(s, 'harmonium', sw, t0, g, hit=0.0, name='harmonium_swell (seam, peak %.3f -> %.3f after the loop)' % (
            t0 + sw.hit, t0 + sw.hit - DUR), events=events)
    # string ostinato, 8ths, bars 1-13 (no attack inside the drop-out)
    for bar in range(1, nbars):
        sh = CHORD[bar]
        for k in range(8):
            t = T(bar, k * 0.5)
            if GATE[0] <= t < GATE[1]:
                continue
            g, fc = strings_level(t)
            m = s.deg(EM.PHRYG_DOM, FIGURE[k] + sh, STR_OCT)
            x = EM.string_note(E.midi_hz(m), BEAT / 2 * 0.55, r, 0.004, 0.05, fc)
            _put(s, 'strings', x, t, g + ACCENT[k], 0.3 * (-1) ** k,
                 name='string %s (midi %d, LP %d)' % (CHORD_NAME[sh], m, fc) if k == 0 else '', events=events)
    # felt taiko pulse on beats 1 and 3 of bars 8-10 (-14 -> -8), LP 1500 keeps its anvil ring out of the words
    for k, t in enumerate(TAIKO):
        g = -14.0 + 6.0 * k / (len(TAIKO) - 1)
        x = A.lp(np.asarray(A.sound('trailer_hit', pitch=TAIKO_PITCH, seed=k), dtype=np.float64), 1500.0, 2)
        _put(s, 'perc', x, t, g, hit=A.hit_offset('trailer_hit', pitch=TAIKO_PITCH, seed=k), cut=GATE[0],
             name='taiko (trailer_hit A1, LP 1500)', events=events)
    # into the drop: shepard 2.2 s + reverse cymbal 1.2 s aimed at 26.4, both stopped dead at 25.8
    sh_ = A.sound('shepard_riser', duration=2.2)
    _put(s, 'fx', sh_, DROP_T, -10.0, hit=sh_.hit, cut=GATE[0], name='shepard_riser 2.2 s (cut 25.8)', events=events)
    rc = A.sound('reverse_cymbal', duration=1.2)
    _put(s, 'fx', rc, DROP_T, -6.0, hit=rc.hit, cut=GATE[0], name='reverse_cymbal 1.2 s (cut 25.8)', events=events)
    # DROP bar 11 + resolve bar 12: dhol (the one desi voice), hats (bar 11), 808 D2
    for bar, trim, hats, bass_db in ((11, 0.0, True, -6.0), (12, -6.0, False, -9.0)):
        if bar >= nbars:
            continue
        t0 = T(bar)
        for j, (bb, g) in enumerate(CHAAL):
            t = T(bar, bb)
            if bar == DROP_BAR and bb == 0.0:
                d = A.sound('dhol_hit', pitch=DHOL_PITCH, seed=100)                # the drop hit itself
                _put(s, 'perc', d, t, 0.0, hit=d.hit, name='dhol_hit DROP (D2)', events=events)
            else:
                d = A.sound('dhol_hit', pitch=DHOL_PITCH, seed=10 * bar + j)
                _put(s, 'perc', d, t, g + trim, hit=d.hit, name='dhol chaal (D2)', events=events)
            _key(s, t)
        if hats:
            for i in range(8):
                _put(s, 'perc', EM.hat(r), T(bar, i * 0.5), -6.0, 0.3, name='hat' if i == 0 else '',
                     events=events if i == 0 else None)
        _put(s, 'bass', EM.bass808([(0, 3.8 * BEAT, ROOT - 24, None)], _n(BAR), 1.8), t0, bass_db,
             name='808 D2 (73.4 Hz)', events=events)
    # loop bar: reverse cymbal ending exactly on DUR (frame 0's trailer_hit in the SFX stem is the release)
    if s.dur >= DUR:
        rc2 = A.sound('reverse_cymbal', duration=LOOP_CYMBAL[0])
        _put(s, 'fx', rc2, DUR, LOOP_CYMBAL[1], hit=rc2.hit, name='reverse_cymbal 2.4 s -> 33.6', events=events)
    return dict(drop_bar=DROP_BAR, drop_t=DROP_T, end_t=DUR)


EM.STYLES['c08_epic'] = style_c08               # runtime registration (BRIEF §12); epic_music.py is not edited


def compose(seed=SEED):
    E.register()
    s = EM.Song(DUR + OVER, BPM, KEY, seed)
    assert s.root == ROOT
    s.st = {k: np.zeros((s.N, 2)) for k in STEMS}
    events = []
    style_c08(s, DROP_BAR, events)
    return s, events


def gate_curve(n=N):
    """1 outside the drop-out, 0 on [25.800, 26.392); 4 ms cosine edges 25.796-25.800 and 26.392-26.396."""
    g = np.ones(n)
    a, b, f = _n(GATE[0]), _n(GATE[1] - EDGE), _n(EDGE)
    g[a:b - f] = 0.0
    g[a - f:a] = np.cos(np.linspace(0, np.pi / 2, f)) ** 2
    g[b - f:b] = np.sin(np.linspace(0, np.pi / 2, f)) ** 2
    return g


def _fold(x):
    """Circular fold: everything rendered past DUR is added back onto the start (seamless loop)."""
    y = x[:N].copy()
    for k in range(1, int(np.ceil(len(x) / N))):
        seg = x[k * N:(k + 1) * N]
        y[:len(seg)] += seg
    return y


def bus(s):
    """Stem-exact, loop-safe version of epic_music.render's bus. Returns (mix, stems, info)."""
    st = {k: s.st[k] * undb(STEM_DB[k]) for k in STEMS}
    if PERC_SHAVE_DB:
        pk = A.tp_envelope(st['perc'])
        st['perc'] = st['perc'] * A.limiter_gain(st['perc'], float(A.db(pk.max())) - PERC_SHAVE_DB, release=0.06,
                                                 pk=pk)[:, None]
    sc = A.sidechain(np.ones(s.N), s.kick_key, depth_db=SC_DEPTH_DB, attack=0.005, release=0.16)[:, 0]
    for k in DUCKED:
        st[k] = st[k] * sc[:, None]
    st = {k: _fold(A.reverb(v, 'studio', wet_db=-18)) for k, v in st.items()}
    gc = gate_curve()
    st = {k: v * gc[:, None] for k, v in st.items()}
    mix = sum(st[k] for k in STEMS)
    g = TARGET_LUFS - A.loudness(mix)
    for _ in range(10):
        gl = A.limiter_gain(mix * undb(g), TP_CEILING - 0.3)
        y = mix * undb(g) * gl[:, None]
        L = A.loudness(y)
        if abs(L - TARGET_LUFS) < 0.02:
            break
        g += TARGET_LUFS - L
    stems = {k: v * undb(g) * gl[:, None] for k, v in st.items()}
    y = sum(stems[k] for k in STEMS)
    info = dict(bus_gain_db=round(float(g), 3), limiter_max_gr_db=round(float(-A.db(gl.min())), 3),
                limiter_gr_over_1db_s=round(float(np.sum(gl < undb(-1.0)) / SR), 4),
                lufs=round(A.loudness(y), 3), true_peak_dbtp=round(A.true_peak(y), 3),
                lra=round(A.loudness_range(y), 2), max_momentary_lufs=round(A.momentary_max(y), 2))
    return y, stems, info


def render(seed=SEED):
    s, events = compose(seed)
    y, stems, info = bus(s)
    info.update(module=MODULE, source='procedural, original (epic_music instruments + epic_sfx sounds); no samples '
                'of songs, no AI model', licence='original work for @jawad_mp4', bpm=BPM, key='D Phrygian dominant',
                sa_hz=round(E.midi_hz(ROOT), 2), dur=DUR, samples=N, seed=seed, drop_t=DROP_T, gate=list(GATE),
                chords={str(b): CHORD_NAME[c] for b, c in CHORD.items()})
    return dict(mix=y, stems=stems, info=info, events=events)


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def write(res, out=OUT):
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    full = os.path.join(out, 'music_full.wav')
    A._write_wav(full, res['mix'], 24)
    files = dict(full=full)
    for k in STEMS:
        files[k] = A._write_wav(os.path.join(out, 'stems', k + '.wav'), res['stems'][k], 24)
    link = os.path.join(out, MODULE + '_music.wav')          # BRIEF §12 name -> the same file
    if os.path.lexists(link):
        os.remove(link)
    os.symlink('music_full.wav', link)
    info = dict(res['info'], files=files, sha256={k: _sha(v) for k, v in files.items()},
                sections=[dict(name=a, t0=b, t1=c, bars=d, picture=e, music=f) for a, b, c, d, e, f in SECTIONS],
                events=[e for e in res['events'] if e['name']])
    json.dump(info, open(os.path.join(out, 'music_full.json'), 'w'), indent=1)
    return info


# ============================================================================================ verify
def _ffprobe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,'
                        'bits_per_sample,duration_ts,duration', '-of', 'json', p], capture_output=True, text=True)
    return json.loads(r.stdout)['streams'][0]


def _ebur128(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    get = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I_lufs=get('I'), LRA_lu=get('LRA'), true_peak_dbtp=get('Peak'))


def _flux(x, hop=240, nfft=2048, band=None):
    m = A._st(x).mean(1)
    f, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop)
    M = np.log1p(np.abs(Z) * 100.0)
    if band:
        M = M[(f >= band[0]) & (f <= band[1])]
    return tt[1:], np.maximum(np.diff(M, axis=1), 0).sum(0)


def grid_fit(x, bpm=BPM, t0=0.0, t1=None, band=None, span=0.02, step=0.0005, ostep=0.001):
    """Spectral-flux grid fit (EM.beatgrid's method) on [t0, t1] (t0 on a beat of the reel grid):
    tempo = the best (tempo, phase) pair over bpm x (1 +- span); phase_ms = the best beat phase AT the nominal bpm,
    relative to the reel grid (folded to +-half a beat); on/off = mean flux on the beats / on the off-beat 8ths
    (> 1: the beat is the strongest 8th); strength = on-grid flux / mean flux (> 2 = on a grid). The STFT method reads
    attacks ~5-10 ms early (a 43 ms window sees an onset before its centre does): EM.beatgrid shows the same bias."""
    t1 = DUR if t1 is None else t1
    seg = A._st(x)[_n(t0):_n(t1)]
    tt, fl = _flux(seg, band=band)
    hop = tt[1] - tt[0]

    def score(b, o):
        i = np.round((o + np.arange(0, tt[-1] - o, 60.0 / b) - tt[0]) / hop).astype(int)
        i = i[(i >= 0) & (i < len(fl))]
        return fl[i].mean()
    best = max((score(b, o), b) for b in bpm * np.arange(1 - span, 1 + span + 1e-12, step)
               for o in np.arange(0, 60.0 / b, ostep))
    P = 60.0 / bpm
    offs = np.arange(0, P, ostep)
    prof = np.array([score(bpm, o) for o in offs])
    o = offs[int(np.argmax(prof))]
    on = max(prof[:6].max(), prof[-6:].max())                    # beats (+-5 ms)
    k = int(round(P / 2 / ostep))
    off = prof[k - 5:k + 6].max()                                # off-beat 8ths (+-5 ms)
    return dict(t0=t0, t1=t1, tempo=round(float(best[1]), 3), phase_ms=round(float((o + P / 2) % P - P / 2) * 1000, 1),
                on_off=round(float(on / off), 2), strength=round(float(prof.max() / fl.mean()), 2), band=band or 'full')


def env_onset(x, t_exp, band, win=0.04, w=0.008):
    """Attack time of one event: the instant t that maximises the band-limited power ratio
    mean(p[t, t + w]) / mean(p[t - w, t]) within +-win of t_exp (p = squared band-passed mono signal). A ratio of
    adjacent windows is robust to the decaying tails of earlier hits. Drums are measured in the band of their stick /
    slap transient (a 73 Hz head has a 14 ms period: no envelope resolves its attack). Returns (t_onset, ratio dB)."""
    y = A._st(x).mean(1)
    a, b = _n(max(t_exp - win - w, 0)), min(len(y), _n(t_exp + win + w))
    lo, hi = max(a - _n(0.25), 0), min(len(y), b + _n(0.25))
    p = np.square(A.bp(y[lo:hi], band[0], band[1], 2))
    c = np.concatenate([[0.0], np.cumsum(p)])
    k = _n(w)
    i = np.arange(_n(t_exp - win) - lo, _n(t_exp + win) - lo)
    after, before = c[i + k] - c[i], c[i] - c[i - k]
    r = after / (before + 1e-4 * after.max() + 1e-30)          # regularised: an attack out of silence peaks at its start
    j = int(np.argmax(r))
    return (lo + i[j]) / SR, float(10 * np.log10(r[j] + 1e-20))


def flux_peaks(x, band=None, k=1.5, min_gap=0.1):
    """Blind onset picker on the mix: spectral-flux local maxima above a moving median + k x MAD (1 s)."""
    from scipy.ndimage import median_filter
    tt, fl = _flux(x, hop=120, nfft=1024, band=band)
    w = int(1.0 / (tt[1] - tt[0]))
    med = median_filter(fl, w, mode='nearest')
    mad = median_filter(np.abs(fl - med), w, mode='nearest')
    thr = med + k * np.maximum(mad, 1e-9) + 0.02 * fl.max()
    g = int(min_gap / (tt[1] - tt[0]))
    i = np.nonzero((fl == maximum_filter1d(fl, 2 * g + 1)) & (fl > thr))[0]
    return tt[i] - (tt[1] - tt[0]) / 2


TAIKO_BAND = (300.0, 1500.0)                    # skin slap (the taiko is low-passed at 1.5 kHz)
DHOL_BAND = (1500.0, 8000.0)                    # tilli (stick) modes + crack
PC = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def chroma(x, t0, t1, lo=130.0, hi=700.0):
    m = A._st(x).mean(1)[_n(t0):_n(t1)]
    f, _, Z = signal.stft(m, SR, nperseg=16384, noverlap=16384 - 2048)
    P = (np.abs(Z) ** 2).mean(1)
    sel = (f >= lo) & (f <= hi)
    c = np.zeros(12)
    np.add.at(c, np.round(69 + 12 * np.log2(f[sel] / 440.0)).astype(int) % 12, P[sel])
    o = np.argsort(c)[::-1]
    return [(PC[i], round(float(c[i] / c.max()), 3)) for i in o[:5]]


def _rms_db(x, t0, t1):
    seg = A._st(x)[_n(t0):_n(t1)]
    return round(float(A.db(np.sqrt(np.mean(seg ** 2)) + 1e-12)), 1) if len(seg) else None


def verify(out=OUT):
    full = os.path.join(out, 'music_full.wav')
    x, sr = A.read_wav(full)
    st = {k: A.read_wav(os.path.join(out, 'stems', k + '.wav'))[0] for k in STEMS}
    rep = dict(file=full, sha256=_sha(full), ffprobe=_ffprobe(full), ebur128=_ebur128(full),
               py=dict(lufs=round(A.loudness(x), 3), true_peak_dbtp=round(A.true_peak(x), 3),
                       lra=round(A.loudness_range(x), 2), max_momentary=round(A.momentary_max(x), 2)))
    assert sr == SR and len(x) == N, (sr, len(x))
    rep['stems_sum_max_abs_err'] = float(np.abs(sum(st.values()) - x).max())
    # ---- tempo + phase (whole file, the string section, the drop)
    rep['grid'] = [grid_fit(x), grid_fit(x, t0=T(1), t1=GATE[0]), grid_fit(x, t0=DROP_T, t1=T(13)),
                   grid_fit(x, t0=T(8), t1=GATE[0], band=(30, 400))]
    rep['beatgrid_epic_music'] = EM.beatgrid(x, BPM)
    # ---- event onsets on the stems (exact) and on the mix (in context)
    rows = []
    for bar in range(1, BARS):                                        # every downbeat string note
        t = T(bar)
        if GATE[0] <= t < GATE[1]:
            continue
        a, _ = env_onset(st['strings'], t, (150, 3000))
        b, rise = env_onset(x, t, (150, 3000))
        rows.append(dict(event='strings downbeat bar %d' % bar, t=t, stem_ms=round((a - t) * 1000, 1),
                         mix_ms=round((b - t) * 1000, 1), mix_rise_db=round(rise, 1)))
    for t in TAIKO:
        a, _ = env_onset(st['perc'], t, TAIKO_BAND)
        b, rise = env_onset(x, t, TAIKO_BAND)
        rows.append(dict(event='taiko', t=t, stem_ms=round((a - t) * 1000, 1), mix_ms=round((b - t) * 1000, 1),
                         mix_rise_db=round(rise, 1)))
    for bar in (11, 12):
        for bb, _ in CHAAL:
            t = T(bar, bb)
            a, _ = env_onset(st['perc'], t, DHOL_BAND, w=0.005)
            b, rise = env_onset(x, t, DHOL_BAND, w=0.005)
            rows.append(dict(event='DHOL DROP' if (bar == 11 and bb == 0) else 'dhol chaal bar %d beat %.1f' % (
                bar, bb + 1), t=t, stem_ms=round((a - t) * 1000, 1), mix_ms=round((b - t) * 1000, 1),
                mix_rise_db=round(rise, 1)))
    rep['onsets'] = rows
    errs = np.array([r['stem_ms'] for r in rows])
    errm = np.array([r['mix_ms'] for r in rows])
    rep['onset_err_ms'] = dict(stem_max_abs=float(np.abs(errs).max()), mix_max_abs=float(np.abs(errm).max()),
                               mix_median=float(np.median(errm)))
    # blind onsets on the mix vs the 8th grid
    pk = flux_peaks(x)
    grid8 = np.arange(0, DUR + 1e-9, BEAT / 2)
    d = np.array([pk_ - grid8[np.argmin(np.abs(grid8 - pk_))] for pk_ in pk])
    on = np.abs(d) <= 0.02
    rep['blind_onsets'] = dict(n=int(len(pk)), on_8th_grid_within_20ms=int(on.sum()),
                               median_offset_ms=round(float(np.median(d[on]) * 1000), 1) if on.any() else None,
                               off_grid=[round(float(v), 3) for v in pk[~on]][:20])
    # ---- the drop-out, the drop, the loop seam
    g0, g1 = GATE[0], DROP_T - 2 * EDGE                          # fully closed: 25.800 -> 26.392
    seg = x[_n(g0):_n(g1)]
    rep['dropout'] = dict(window=[g0, g1], peak_abs=float(np.abs(seg).max()),
                          rms_dbfs=_rms_db(x, g0, g1), f774_f781_rms_dbfs=_rms_db(x, 774 / FPS, 782 / FPS))
    _, lc = A.loudness_curve(x, 0.4, 0.01)
    tc = 0.2 + np.arange(len(lc)) * 0.01
    i = int(np.argmax(lc))
    rep['max_momentary'] = dict(lufs=round(float(lc[i]), 2), centre_t=round(float(tc[i]), 2),
                                within_0p6s_after_drop=bool(DROP_T - 0.05 <= tc[i] <= DROP_T + 0.65))
    sm = np.abs(np.diff(x[:, 0]))
    rep['loop'] = dict(last_50ms_rms_dbfs=_rms_db(x, DUR - 0.05, DUR), first_50ms_rms_dbfs=_rms_db(x, 0, 0.05),
                       seam_step=float(np.abs(x[0] - x[-1]).max()), median_step=float(np.median(sm)),
                       p99_step=float(np.percentile(sm, 99)),
                       cymbal_peak_t=round(float(np.argmax(np.abs(st['fx'][_n(DUR - 0.5):]).max(1)) / SR + DUR - 0.5),
                                           4))
    # ---- per-bar loudness and section table
    rep['bars'] = [dict(bar=b, t0=T(b), lufs=round(A.loudness(x[_n(T(b)):_n(T(b + 1))]), 1),
                        **{k: round(A.loudness(st[k][_n(T(b)):_n(T(b + 1))]), 1) for k in STEMS})
                   for b in range(BARS)]
    rep['key'] = dict(bar0=chroma(x, 0.6, 2.4), bars1_2=chroma(st['strings'], T(1), T(3)),
                      bar5=chroma(st['strings'], T(5), T(6)), bar10=chroma(st['strings'], T(10), GATE[0]),
                      bar13=chroma(st['strings'], T(13), DUR), drop=chroma(x, DROP_T, T(12)),
                      low_end_drop_hz=_low_peak(st['bass'], DROP_T, T(12)))
    rep['band_energy_db'] = _bands(x)
    os.makedirs(os.path.join(out, 'qa'), exist_ok=True)
    _pictures(x, st, out, rep)
    json.dump(rep, open(os.path.join(out, 'music_full.verify.json'), 'w'), indent=1)
    return rep


def _low_peak(x, t0, t1):
    m = A._st(x).mean(1)[_n(t0):_n(t1)]
    f = np.fft.rfftfreq(len(m), 1 / SR)
    P = np.abs(np.fft.rfft(m * np.hanning(len(m))))
    sel = (f > 20) & (f < 200)
    return round(float(f[sel][np.argmax(P[sel])]), 2)


def _bands(x):
    m = A._st(x).mean(1)
    f, P = signal.welch(m, SR, nperseg=8192)
    tot = P.sum()
    out = {}
    for name, lo, hi in (('sub <60', 0, 60), ('low 60-250', 60, 250), ('lowmid 250-1k', 250, 1000),
                         ('presence 1-4k', 1000, 4000), ('high 4-8k', 4000, 8000), ('air >8k', 8000, 24000)):
        out[name] = round(float(10 * np.log10(P[(f >= lo) & (f < hi)].sum() / tot + 1e-12)), 1)
    return out


def _pictures(x, st, out, rep):
    from PIL import Image, ImageDraw
    W, H = 1800, 640

    def marks(im, t0, t1, top=44):
        dr = ImageDraw.Draw(im)
        w, h = im.size
        X = lambda t: int((t - t0) / (t1 - t0) * w)
        for b in range(BARS + 1):
            t = T(b)
            if t0 <= t <= t1:
                dr.line([(X(t), top), (X(t), h - 18)], fill=(110, 110, 130), width=1)
                dr.text((X(t) + 2, top + 2), str(b), fill=(220, 220, 235))
        for t, col in ((GATE[0], (255, 70, 60)), (GATE[1], (255, 70, 60)), (DROP_T, (80, 230, 255))):
            if t0 <= t <= t1:
                dr.line([(X(t), top), (X(t), h - 18)], fill=col, width=2)
        return im

    im = A.spectro_image(x, W, H, None, 'C08 Ek Frame ki Keemat: music_full.wav  100 BPM  D Phrygian dominant',
                         '%.2f LUFS  %.2f dBTP  LRA %.1f  |  bar numbers on the grid, red = drop-out 25.8-26.4, '
                         'cyan = drop 26.4' % (rep['ebur128']['I_lufs'], rep['ebur128']['true_peak_dbtp'],
                                              rep['ebur128']['LRA_lu']))
    marks(im, 0, DUR).save(os.path.join(out, 'qa', 'music_full_spectrogram.png'))
    a, b = _n(T(9)), _n(T(12))
    im = A.spectro_image(x[a:b], W, H, None, 'zoom 21.6-28.8 s: taiko, shepard + cymbal, drop-out, DROP',
                         'bars 9-11; red = gate 25.8 / 26.4; cyan = drop 26.4')
    marks(im, T(9), T(12)).save(os.path.join(out, 'qa', 'music_zoom_drop.png'))
    seam = np.concatenate([x[_n(T(12)):], x[:_n(T(2))]])             # 28.8-33.6 then 0-4.8: the loop as heard
    im = A.spectro_image(seam, W, H, 4.8, 'loop seam: 28.8-33.6 | 0-4.8 (cyan = seam 33.6 -> 0.0)',
                         'bars 12-13 then bars 0-1, played as the loop plays them')
    im.save(os.path.join(out, 'qa', 'music_loop_seam.png'))
    # stem loudness lanes
    H2 = 120 * (len(STEMS) + 1) + 30
    img = Image.new('RGB', (W, H2), (14, 10, 18))
    dr = ImageDraw.Draw(img)
    lo, hi = -60.0, -6.0
    for r_, (name, sig) in enumerate([('mix', x)] + [(k, st[k]) for k in STEMS]):
        y0 = 20 + r_ * 120
        dr.text((6, y0), name, fill=(240, 235, 230))
        tt, lv = A.loudness_curve(sig, 0.4, 0.02)
        pts = [(int(t / DUR * W), y0 + 110 - int((np.clip(l, lo, hi) - lo) / (hi - lo) * 100)) for t, l in zip(tt, lv)]
        dr.line(pts, fill=(255, 120, 40) if r_ else (250, 245, 240), width=2)
        for ref in (-16, -30):
            yy = y0 + 110 - int((ref - lo) / (hi - lo) * 100)
            dr.line([(0, yy), (W, yy)], fill=(50, 45, 60))
            dr.text((W - 50, yy - 11), '%d' % ref, fill=(120, 110, 130))
    for b_ in range(BARS + 1):
        xx = int(T(b_) / DUR * W)
        dr.line([(xx, 15), (xx, H2 - 10)], fill=(70, 70, 90))
        dr.text((xx + 2, H2 - 14), str(b_), fill=(200, 200, 220))
    for t, col in ((GATE[0], (255, 70, 60)), (GATE[1], (255, 70, 60))):
        dr.line([(int(t / DUR * W), 15), (int(t / DUR * W), H2 - 10)], fill=col)
    img.save(os.path.join(out, 'qa', 'music_stems_loudness.png'))


# ============================================================================================ run 2: mix + envelopes
AUD = os.path.join(RW, 'audio')
VO_A = os.path.join(RW, 'vo', MODULE + '_vo.wav')
VO_B = os.path.join(RW, 'vo', MODULE + '_hookb_vo.wav')
SFX_A = os.path.join(AUD, MODULE + '_sfx_stem.wav')
SFX_B = os.path.join(AUD, MODULE + '_hookb_sfx_stem.wav')
SPLICE = 3.0                                    # hook B frames 0-89, the body from f90 (BRIEF §6.2)


def _need(*paths):
    miss = [p for p in paths if not (p and os.path.exists(p))]
    if miss:
        raise SystemExit('missing input(s): %s' % ', '.join(miss))


def _xfade(a, b, t, d=0.005):
    """a before t, b after t, equal-power crossfade of d s centred on t (both full-length stereo arrays)."""
    a, b = A._st(a), A._st(b)
    y = b.copy()
    i0, i1 = _n(t - d / 2), _n(t + d / 2)
    y[:i0] = a[:i0]
    w = np.linspace(0, np.pi / 2, i1 - i0)[:, None]
    y[i0:i1] = a[i0:i1] * np.cos(w) + b[i0:i1] * np.sin(w)
    return y


GLUE = dict(ratio=1.5, below_p98_db=1.5)          # session 4 kit: the default 2:1 / -3 dB glue left A at LRA 1.8 and B at
                                                # 1.9 LU (< LEAD_DECISIONS 1's 2.0); this gentler glue: A 2.4, B 2.2, limiter <= 2.7 dB


def mix(hook='A', vo=None, sfx=None, music=None, vo_b=None, sfx_b=None, out_dir=None):
    """Run 2 (after the VO and the SFX stem exist): epic_mix.mix_reel -> A (VO + SFX + music) and B (VO + SFX), stems,
    report. hook='B' also builds the Trial-Reel audio: hook-B VO/SFX for 0-3.0 s, then the hook-A mixes from 3.000 s
    (5 ms crossfade), so the body equals version A (to 1 LSB: audio.py's 24-bit read/write scaling differs by 1 code)."""
    import epic_mix as M
    out_dir = out_dir or AUD
    vo, sfx, music = vo or VO_A, sfx or SFX_A, music or os.path.join(OUT, 'music_full.wav')
    _need(vo, sfx, music)
    rep = M.mix_reel(MODULE, DUR, vo=vo, sfx=sfx, music=music, out_dir=out_dir, glue=GLUE)
    rep['ebur128'] = {k: M.ebur128(rep['files'][k]) for k in ('mix', 'vo_sfx')}
    if hook == 'B':
        vo_b, sfx_b = vo_b or VO_B, sfx_b or SFX_B
        _need(vo_b, sfx_b)
        tmp = os.path.join(out_dir, '_hookb_tmp')
        os.makedirs(tmp, exist_ok=True)
        for src_b, src_a, name in ((vo_b, vo, 'vo'), (sfx_b, sfx, 'sfx')):
            A._write_wav(os.path.join(tmp, name + '.wav'), _xfade(M.load(src_b, DUR), M.load(src_a, DUR), SPLICE), 24)
        rb = M.mix_reel(MODULE + '_hookb', DUR, vo=os.path.join(tmp, 'vo.wav'), sfx=os.path.join(tmp, 'sfx.wav'),
                        music=music, out_dir=tmp, glue=GLUE)
        for k in ('mix', 'vo_sfx'):
            y = _xfade(A.read_wav(rb['files'][k])[0], A.read_wav(rep['files'][k])[0], SPLICE)
            p = os.path.join(out_dir, '%s_hookb_%s.wav' % (MODULE, k))
            A._write_wav(p, y, 24)
            rep['hookb_' + k] = dict(file=p, lufs=round(A.loudness(y), 2), true_peak_dbtp=round(A.true_peak(y), 2),
                                     ebur128=M.ebur128(p))
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
        os.rmdir(tmp)
    json.dump(rep, open(os.path.join(out_dir, MODULE + '_mix.json'), 'w'), indent=1)
    return rep


def envelopes(out_dir=None):
    """<RW>/audio/ek_frame_ki_keemat_env.json = {fps, vo, sfx, music}: RMS dBFS per video frame (1,008 frames) of the
    A-mix stems at their mix gains (BRIEF §7.3, the S3-03 audio lanes). Floor -90 dBFS."""
    out_dir = out_dir or AUD
    files = {k: os.path.join(out_dir, '%s_stem_%s.wav' % (MODULE, k)) for k in ('vo', 'sfx', 'music')}
    _need(*files.values())
    nf = int(round(DUR * FPS))
    spf = SR // FPS
    env = dict(fps=FPS, frames=nf, unit='RMS dBFS per frame (stereo mean power), floor -90', source=files)
    for k, p in files.items():
        x = A._st(A.read_wav(p)[0])[:nf * spf]
        x = np.pad(x, ((0, nf * spf - len(x)), (0, 0)))
        pw = np.square(x).mean(1).reshape(nf, spf).mean(1)
        env[k] = [round(float(v), 2) for v in np.maximum(10 * np.log10(pw + 1e-30), -90.0)]
    p = os.path.join(out_dir, MODULE + '_env.json')
    json.dump(env, open(p, 'w'))
    return p


# ============================================================================================ CLI
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('render', 'verify', 'mix', 'envelopes'))
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--hook', default='A', choices=('A', 'B'))
    ap.add_argument('--vo')
    ap.add_argument('--sfx')
    ap.add_argument('--vo-b')
    ap.add_argument('--sfx-b')
    ap.add_argument('--music')
    ap.add_argument('--out-dir')
    a = ap.parse_args()
    if a.cmd == 'render':
        info = write(render(), a.out)
        print(json.dumps({k: v for k, v in info.items() if k not in ('events', 'sections')}, indent=1))
    elif a.cmd == 'verify':
        rep = verify(a.out)
        print(json.dumps({k: v for k, v in rep.items() if k not in ('onsets', 'bars')}, indent=1))
        for r in rep['onsets']:
            print('  %-30s t=%7.3f  stem %+6.1f ms  mix %+6.1f ms  rise %5.1f dB' % (
                r['event'], r['t'], r['stem_ms'], r['mix_ms'], r['mix_rise_db']))
        for r in rep['bars']:
            print('  bar %2d %6.2f s  mix %6.1f LUFS  | ' % (r['bar'], r['t0'], r['lufs']) +
                  '  '.join('%s %6.1f' % (k, r[k]) for k in STEMS))
    elif a.cmd == 'mix':
        print(json.dumps(mix(a.hook, a.vo, a.sfx, a.music, a.vo_b, a.sfx_b, a.out_dir), indent=1))
    else:
        print(envelopes(a.out_dir))
