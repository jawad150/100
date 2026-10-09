"""reel3_vo_music.py: original background music for REEL 3 VO "Nurture . Develop . Grow" (Organic Fostering).

    cd pipeline/fostering && nice -n 5 python3 reel3_vo_music.py      (deterministic, seeded)

Synthesised from scratch with music_synth.py + audio.py (numpy / scipy only: no samples, no downloads, no AI).
Mood: tender, organic, growing, warm and hopeful (light organic look: ivory / peach, a seed that sprouts, the three
chapters NURTURE / DEVELOP / GROW, the kinds-of-care dial, the trust pills, the sunset end card).

KEY      G major (I-vi-IV-V colour with maj7 / add9 / sus4 extensions; plagal IV -> I close over a G pedal).
TEMPO    92 BPM, 4/4. Beat n = n * 0.652174 s from 0.000 s (beat 1 of bar 1 = 0.000 s); bar = 4 beats = 2.608696 s.
         48.2 s = 73.907 beats = 18.48 bars: bars 1-19 (bar 19 is cut at beat 2.91 = 48.200 s). Every rhythmic event
         sits on the 16th grid (piano / guitar humanise <= 3 ms, shaker <= 2 ms; an onset deliberately ON a hero hit
         slides toward it by at most 7.9 ms: all within +-8 ms, grid_audit()). Length: exactly
         round(48.2 * 48000) = 2313600 samples (= the VO mix and stems).
EDIT     Section edges are computed in OUTPUT time from reel3_vo (V.out_time on the reel3.py constants T_NUR, T_DEV,
         T_GRO, T_KIND, T_TRUST, T_END, E_LAND, TRUST_T; V.vo_cues(); V.cues() hero hits = gain_db >= -6 at their
         hit time, start-aligned cues at t + A.hit_offset). An edge within one beat of a bar line moves to that bar
         line, otherwise (mid-bar) to the nearest beat (edge_beat(); asserted against EXPECTED_EDGES = the table).

MUSIC MAP  bars are 1-based "bar.beat" (bar 1 beat 1 = 0.000 s; 3.2 = bar 3 beat 2); b = beat index from 0.000 s.
section   | bar range    | t0-t1 s       | edit events (reel3_vo, output s)  | music events
----------|--------------|---------------|-----------------------------------|----------------------------------------
SEED +    | 1.1-3.2      | 0.000-5.870   | VO small_beginning 0.10-1.32; SEED| sparse: low-passed pad Gadd9 breathing
GROWTH    | (b0-9)       |               | PLIP 0.652 (b1); iris montage     | in from 0, piano G2 + D3 on b0 (the
          |              |               | swishes 0.87-1.74 (triplets); iris| seed); b1 = soft piano dyad ON the plip;
          |              |               | close 1.957 (b3); grow_swell peak | gap HOOK S D5 (b2.5, between swishes) ->
          |              |               | 4.557 (b6.99); VO change_direction| E5 + Em7 ON the iris close b3; b5 Cmaj9,
          |              |               | 2.61-4.87; leaf gust 5.884 (b9.02)| b7 D7sus4 ON the grow peak (pad filter
          |              |               |                                   | opens across the growth); gap HOOK A
          |              |               |                                   | b8-8.5 (A4 D5, D7) into the gust
NURTURE   | 3.2-5.1      | 5.870-10.435  | T_NUR 5.884 (mid-bar -> b9); VO   | piano + pad: G Em7 Cmaj7, felt-piano
          | (b9-16)      |               | nurture 5.98-6.73, safe_home      | broken 8ths (D3-B4), bass on the changes;
          |              |               | 6.98-9.24; zoom through the U     | b9 downbeat ON the gust; gap HOOK B (the
          |              |               | 9.474 (b14.53)                    | motif B4 D5 E5) b15-16
DEVELOP   | 5.1-8.2      | 10.435-18.913 | whip T_DEV 10.778 (b16.53 -> bar  | + nylon guitar (Karplus-Strong) 8th
          | (b16-29)     |               | line b16); VO develop 10.83-11.56,| fingerpicking ADDED (-13.5 dB); the piano
          |              |               | matching 12.26-18.60; chip pops   | stays: chords on the changes + a broken
          |              |               | 12.72 / 13.81 / 14.35; puzzle     | note on beat 2 of each 2-beat chord;
          |              |               | click 17.070 (b26.17)             | climbing bass Am7 Dadd9 G/B Cmaj7 Am7 Bm7
          |              |               |                                   | Cmaj7 D7sus4 (A B C D -> G); +1.2 dB
          |              |               |                                   | section step on b16; no onset within
          |              |               |                                   | 60 ms of the pops
GROW      | 8.2-10.2     | 18.913-24.130 | air_zoom T_GRO 18.939 (b29.04:    | THE LIFT: reversed Gadd9 swell ENDING on
(lift)    | (b29-37)     |               | mid-bar -> b29); VO grow 18.99-   | b29 + the pad change (no transient on
          |              |               | 19.52, steady_care 19.77-22.60;   | b29: air_zoom 26 ms later; piano pulse
          |              |               | zoom through the O 22.829 (b35.0) | + bass enter on b29.5), pad opens + air
          |              |               |                                   | pad (octave up), marimba off-beat 8ths,
          |              |               |                                   | shaker 16ths, piano quarter pulse, guitar
          |              |               |                                   | 8ths; Gadd9 D/F# Em7 Cmaj9 D7sus4; soft
          |              |               |                                   | pulse ON the O zoom b35; gap HOOK C
          |              |               |                                   | b35.5-37 (B4 D5 E5 -> G5 on kinds pop)
KINDS OF  | 10.2-13.1    | 24.130-31.304 | T_KIND 24.133 (b37.00): heart pop;| FULL BUT SOFT: G Em7 Cmaj7 G/B Am7
CARE      | (b37-48)     |               | VO kinds_of_care 24.61-27.22; tag | D7sus4; broken 8ths, guitar 8ths + 16th
          |              |               | pops 24.79-26.42; dial turns      | pickups, marimba, shaker, soft low pulse
          |              |               | 27.01-30.79 (swish + tap, -8/-11) | (half notes) + sub warmth; MAIN HOOK in
          |              |               |                                   | the 4.4 s VO gap b42-47 (B4 D5 E5 | D5
          |              |               |                                   | B4 A4 | C5 E5 D5, piano + marimba, glock
          |              |               |                                   | E6 on b43), notes clear of the dial cues
TRUST     | 13.1-16.1    | 31.304-39.130 | T_TRUST 31.317 (b48.02 -> bar     | GENTLE PULSE: soft kick every beat from
          | (b48-60)     |               | line b48; whoosh 31.267 / tap /   | b49, sub, guitar 8ths, shaker 8ths; Cmaj7
          |              |               | impact 31.337: a 70 ms cluster);  | Em7 Am7 Cmaj7 G/B Am7 D7sus4 D7 (every
          |              |               | pills 31.643 / 33.450 / 35.275    | pill chord holds E and B). b48: only the
          |              |               | (check_ding E6+B6); VO independent| pad changes (no kick / guitar / piano in
          |              |               | 31.64-33.70, cultural 33.85-35.85,| the slam cluster); ACCENT per pill: pill1
          |              |               | ofsted 36.00-37.78; stack lifts   | = marimba E4+B4 + the Cmaj7 chord + bass
          |              |               | out 38.284                        | ON the ding (b48.5, 5 ms); pills 2 / 3 =
          |              |               |                                   | E4+B4 air swells from b51 / b53.75 whose
          |              |               |                                   | attack peaks ON the ding (3-7 ms); no
          |              |               |                                   | pulse on b54 (58 ms before a ding); gap
          |              |               |                                   | HOOK E b58.5-60 (A4 D5 E5)
END CARD  | 16.1-19.2.91 | 39.130-48.200 | T_END 38.807 (-> bar line b60);   | RESOLVE: Em7 b60; Cmaj9 ON the logo sting
          | (b60-73.91)  |               | leaves fly 39.133; LOGO STING     | b61 (its bell is a C: piano, strum, pad,
          |              |               | 39.785 (b61.00, C bell); CTA pop  | pulse); G/B Am7 D7sus4 -> Gadd9 b68 (the
          |              |               | 40.112, click 40.438; VO tagline  | tonic, bar 18; crescendo b61-68) ->
          |              |               | 40.59-43.37, start_enquiry        | Cadd9/G b70 (plagal; piano, bass, sub
          |              |               | 43.72-46.39                       | held to the end) -> G b72 = a pad change
          |              |               |                                   | only (nothing re-struck); final HOOK F
          |              |               |                                   | b71.5-72 (B4 D5 -> G5 + glock G6, the
          |              |               |                                   | motif resolved); after the last line the
          |              |               |                                   | bass tail eases 4 dB; fade 46.38-48.18
          |              |               |                                   | (1.8 s, every 200 ms window <= the one
          |              |               |                                   | before); silence in the last 20 ms

CHORDS (beat: chord)  0 Gadd9 | 3 Em7 | 5 Cmaj9 | 7 D7sus4 | 8 D7 | 9 G | 12 Em7 | 14 Cmaj7 | 16 Am7 | 18 Dadd9 |
20 G/B | 22 Cmaj7 | 24 Am7 | 26 Bm7 | 27 Cmaj7 | 28 D7sus4 | 29 Gadd9 | 32 D/F# | 34 Em7 | 35 Cmaj9 | 36 D7sus4 |
37 G | 40 Em7 | 42 Cmaj7 | 44 G/B | 46 Am7 | 47 D7sus4 | 48 Cmaj7 | 50 Em7 | 52 Am7 | 54 Cmaj7 | 56 G/B | 57 Am7 |
58 D7sus4 | 59 D7 | 60 Em7 | 61 Cmaj9 | 64 G/B | 66 Am7 | 67 D7sus4 | 68 Gadd9 | 70 Cadd9/G | 72 G.
Hand voice-led 4-5 voice upper structures (CHART, D4-D5), the bass plays the root / slash note (A1-G2); the piano
plays the structure an octave down (broken chords), the guitar adds the bass an octave up.

SPEECH RULES  No melody while the voice speaks: every hook note sits in a VO gap (asserted: onset >= 100 ms after a
line ends, gate end >= 80 ms before the next line, release clipped to the gap, no SFX cue >= -12 dB within +-60 ms
except a support cluster). Pad / piano / guitar / marimba / hooks / shaker pass a speech-aware filter (2-pole
low-pass 1.0 kHz while a line plays, 15 kHz in the gaps, + peak dips of -12 dB at 2 kHz (Q 0.5) and -8 dB at
650 Hz (Q 0.6, the voice's 300 Hz-1.5 kHz body); 60 ms close / 300 ms open); pad / piano -2 dB, guitar and
marimba -3 dB, shaker -4 dB under speech; the bass piano low-passes 1.2 kHz -> 250 Hz under speech. QA gate
(qa: clarity_spec, asserted): in 100 ms windows (50 ms hop) of 300 Hz-4 kHz whose centre is under speech
(M.speech_mask, ungated: quiet word starts, tails, breaths and mask-filled pauses included), the voice is >= 6 dB
above the bed in >= 95 % of windows and the median margin is >= 10 dB (speech_band_overlap is logged only).
Hero hits: no piano /
guitar / marimba / shaker / kick / hook onset within +-60 ms of an SFX hero hit, except music events deliberately
ON a hit (SUPPORT, each <= 15 ms from its hit and nudged <= 7.9 ms toward it: the plip b1, the iris close b3, the
grow peak b7, the gust b9, the O zoom b35, the kinds pop b37, pill 1 b48.5, the logo sting b61). Not support (no
transient): the GROW downbeat b29 (air_zoom +26 ms), the trust slam b48 (whoosh -37 / tap +13 / impact +33 ms),
pills 2 / 3 (nearest 16ths 24-26 ms off: soft swells peak on them instead); hero_audit() logs and measures.

INSTRUMENTS (music_synth)  felt piano (felt_piano: broken chords, chord pulses, bass, hooks), nylon guitar
(karplus_strong fingerpicking + strum), soft string-like pad (pad 'saw' 5 detuned voices, low-passed, slow
attack, chorus) + air pad (pad 'tri' octave up, GROW / KINDS / end card; E4+B4 swells on pills 2 / 3), marimba
(off-beat 8ths, the pill-1 accent, hook doubles), glockenspiel (hook sparkle E6 / G6), shaker (shaker strokes,
16ths / 8ths), very soft low pulse (soft_kick, punch 0.15, no click), sub warmth (sub_bass, KINDS onward),
reversed Gadd9 swell into GROW (reverse_swell). Sends: hall (pad, piano, guitar), plate (marimba, hooks, shaker), air (hooks, end tail). High-pass
120-400 Hz on everything except the bass piano, sub and pulse (sends 200-400 Hz); low end mono in the centre; width
from detune, chorus, pan, Haas (guitar) and reverb. Bus: hp 30 Hz, bus_comp -20 / 1.5, tilt +0.6, section gain
(SEC_GAIN: seed +2.5 (beats 0-4) -> +1.2, NURTURE +0.8, DEVELOP +2, GROW +2.6, KINDS +0.3, TRUST -0.2, end card
+0.4 -> +5.8 into the tonic), fade 1.8 s, normalise_lufs -16 LUFS / -1.2 dBTP.

DELIVERY  pre-duck floor (DUCK_FLOOR_DB 14: total VO duck >= 14 dB wherever the speech mask is on, 60 ms look-ahead,
100 ms hang, 20 / 150 ms) -> M.render_bed (A.sidechain VO duck depth 13 dB, 40 / 400 ms; SFX duck
3 dB; gaps 7 LU under the delivered mix, each >= 1 s gap 6-9 LU; voice >= 10 LU over the music) ->
M.master_withmusic (-14 LUFS, limiter at -2.3, <= -2.0 dBTP) -> MP3s (M.write_mp3) and the preview
(M.make_preview: the video comes from $MUSIC_SCRATCH/reel3_vo_preview.mp4, default the session scratchpad; if it
is missing the script says PREVIEW NOT WRITTEN and exits 2). Outputs: OUT_* / MP3_* / PREVIEW.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import audio as A                 # noqa: E402
import music_synth as M           # noqa: E402
import reel3_vo as V              # noqa: E402

# ============================================================================================ constants
SR = A.SR
BPM = 92.0
KEY = 'G major'
DUR = 48.2
N = int(round(DUR * SR))                  # 2313600 samples
T = N / SR
G = M.Grid(BPM)
BEAT, BAR, STEP = G.beat_s, G.bar_s, G.step_s
END_BEAT = T / BEAT                       # 73.907
SEED = 3924810
assert abs(V.DUR - DUR) < 1e-9 and abs(V.BPM - BPM) < 1e-9

AUD = A.AUDIO
OUT_CLEAN = os.path.join(AUD, 'reel3_vo_music.wav')
OUT_BED = os.path.join(AUD, 'reel3_vo_music_bed.wav')
OUT_MIX = os.path.join(AUD, 'reel3_vo_withmusic_mix.wav')
REEL = os.path.abspath(os.path.join(HERE, '..', '..', 'reel', 'organic_fostering'))
MP3_BED = os.path.join(REEL, 'organic_fostering_reel3_vo_nurture_develop_grow_music.mp3')
MP3_CLEAN = os.path.join(REEL, 'organic_fostering_reel3_vo_nurture_develop_grow_music_clean.mp3')
TITLE = 'Organic Fostering - reel3_vo_nurture_develop_grow - background music'
SCRATCH = os.environ.get('MUSIC_SCRATCH',
                         '/tmp/claude-0/-home-user-100/bb73d22e-ad11-5aa0-a0b2-8033920f7c07/scratchpad')
VIDEO_IN = os.path.join(SCRATCH, 'reel3_vo_preview.mp4')
PREVIEW = os.path.join(SCRATCH, 'reel3_vo_music_preview.mp4')

# ============================================================================================ edit timeline
S = V.SRC


def ot(src_t):
    return float(V.out_time(src_t))


EDIT = dict(plip=ot(S.T_IMPACT), iris=ot(S.T_GROW), nurture=ot(S.T_NUR), zoom_u=ot(S.B(11)), develop=ot(S.T_DEV),
            puzzle=ot(S.B(17)), grow=ot(S.T_GRO), zoom_o=ot(S.B(21)), kinds=ot(S.T_KIND), trust=ot(S.T_TRUST),
            pill1=ot(S.TRUST_T[0]), pill2=ot(S.TRUST_T[1]), pill3=ot(S.TRUST_T[2]), trust_out=ot(S.TRUST_OUT),
            end=ot(S.T_END), logo=ot(S.E_LAND), cta=ot(S.E_CTA), click=ot(S.E_CLICK))
VO_LINES = [(c['line'], float(c['start']), float(c['end'])) for c in V.vo_cues()]


def _hit_time(c):
    t = float(c['t'])
    if c.get('align', 'hit') == 'start':
        t += float(A.hit_offset(c['name'], **c.get('params', {})))
    return t


SFX_CUES = sorted((_hit_time(c), float(c.get('gain_db', 0.0)), c['name']) for c in V.cues())
HERO = sorted({round(t, 4) for t, g, _ in SFX_CUES if g >= -6.0})


def edge_beat(t):
    """Section change for an edit boundary at t: the nearest bar line if within one beat, else the nearest beat."""
    bb = int(round(t / BAR)) * 4
    if abs(t - bb * BEAT) <= BEAT + 1e-9:
        return bb
    return int(round(t / BEAT))


SEC_EDGES = [('seed', 0), ('nurture', edge_beat(EDIT['nurture'])), ('develop', edge_beat(EDIT['develop'])),
             ('grow', edge_beat(EDIT['grow'])), ('kinds', edge_beat(EDIT['kinds'])),
             ('trust', edge_beat(EDIT['trust'])), ('end', edge_beat(EDIT['end']))]
EXPECTED_EDGES = dict(seed=0, nurture=9, develop=16, grow=29, kinds=37, trust=48, end=60)
assert {k: v for k, v in SEC_EDGES} == EXPECTED_EDGES, SEC_EDGES        # the docstring map is built on these
assert abs(EDIT['logo'] - 61 * BEAT) < 0.004 and abs(EDIT['zoom_o'] - 35 * BEAT) < 0.004


def section(beat):
    name = SEC_EDGES[0][0]
    for k, b in SEC_EDGES:
        if beat >= b - 1e-9:
            name = k
    return name


# music events deliberately ON a hero hit (the same instant: asserted <= 15 ms): beat -> the hero hit it supports.
# Each one's cluster = the hero hits within 40 ms of it. The GROW downbeat b29 (air_zoom 26 ms later) and the trust
# slam b48 (whoosh -37 ms, tap +13, impact +33) are NOT support instants: no transient there (the pad changes
# softly on the bar line, the piano / bass move to the next 8th b29.5 / b48.5, no kick / guitar on b29 / b48).
SUPPORT_HITS = {1.0: EDIT['plip'], 3.0: EDIT['iris'], 7.0: 4.5566, 9.0: EDIT['nurture'], 35.0: EDIT['zoom_o'],
                37.0: EDIT['kinds'], 48.5: EDIT['pill1'], 61.0: EDIT['logo']}
SUPPORT = tuple(b * BEAT for b in sorted(SUPPORT_HITS))
PILL_ACCENT = 48.5                  # pill 1: marimba E4 + B4 and the piano chord ON the ding (12.8 ms)
# pills 2 / 3: the grid puts the nearest 16th 24-26 ms off the ding, so no transient there: a soft air-pad swell of
# E4 + B4 starts on a 16th (b51 / b53.75) and its raised-cosine attack is sized so the peak lands ON the ding
PILL_SWELLS = ((51.0, 'pill2'), (53.75, 'pill3'))
PILL_BEATS = (PILL_ACCENT,) + tuple(EDIT[k] / BEAT for _, k in PILL_SWELLS)
for _b, _h in SUPPORT_HITS.items():
    assert abs(_b * BEAT - _h) <= 0.015, (_b, _b * BEAT, _h)
    assert min(abs(h - _h) for h in HERO) < 0.004, (_b, _h)
for _b, _k in PILL_SWELLS:
    assert 0.15 <= EDIT[_k] - _b * BEAT <= 0.30, (_b, _k)


def near_hero(t, win=0.06, support_ok=False):
    """True if t is within +-win of an SFX hero hit. With support_ok, an event on a SUPPORT instant (+-4 ms)
    ignores the hero hits of that instant's own cluster (within 40 ms)."""
    sup = [s for s in SUPPORT if abs(t - s) <= 0.004] if support_ok else []
    for h in HERO:
        if any(abs(h - s) <= 0.04 for s in sup):
            continue
        if abs(t - h) < win:
            return True
    return False


def is_support(b):
    return any(abs(b - s) < 1e-6 for s in SUPPORT_HITS)


def nudge(b):
    """Support events: the onset slides toward its hero hit within the +-8 ms humanise allowance (7.9 ms max), so a
    beat 8.6-14.8 ms off its hit (b7, b9, b48.5) lands within 7 ms of it. 0 for other beats."""
    for sb, h in SUPPORT_HITS.items():
        if abs(b - sb) < 1e-6:
            return float(np.clip(h - sb * BEAT, -0.0079, 0.0079))
    return 0.0


def speaking(t, pre=0.08, post=0.08):
    return any(s - pre <= t <= e + post for _, s, e in VO_LINES)


# ============================================================================================ harmony
# (beat, symbol, upper-structure voicing MIDI (D4-D5), bass MIDI)
CHART = [
    (0, 'Gadd9', [62, 67, 69, 71], 43), (3, 'Em7', [62, 64, 67, 71], 40), (5, 'Cmaj9', [64, 67, 71, 74], 36),
    (7, 'D7sus4', [62, 67, 69, 72], 38), (8, 'D7', [62, 66, 69, 72], 38),
    (9, 'G', [62, 67, 71, 74], 43), (12, 'Em7', [64, 67, 71, 74], 40), (14, 'Cmaj7', [64, 67, 71, 72], 36),
    (16, 'Am7', [64, 67, 69, 72], 33), (18, 'Dadd9', [64, 66, 69, 74], 38), (20, 'G/B', [62, 67, 71, 74], 35),
    (22, 'Cmaj7', [64, 67, 71, 72], 36), (24, 'Am7', [64, 67, 69, 72], 33), (26, 'Bm7', [62, 66, 69, 71], 35),
    (27, 'Cmaj7', [64, 67, 71, 72], 36), (28, 'D7sus4', [62, 67, 69, 72], 38),
    (29, 'Gadd9', [62, 67, 69, 71, 74], 43), (32, 'D/F#', [62, 66, 69, 74], 42), (34, 'Em7', [62, 67, 71, 74], 40),
    (35, 'Cmaj9', [64, 67, 71, 74], 36), (36, 'D7sus4', [62, 67, 69, 72], 38),
    (37, 'G', [62, 67, 71, 74], 43), (40, 'Em7', [64, 67, 71, 74], 40), (42, 'Cmaj7', [64, 67, 71, 72], 36),
    (44, 'G/B', [62, 67, 71, 74], 35), (46, 'Am7', [64, 67, 69, 72], 33), (47, 'D7sus4', [62, 67, 69, 72], 38),
    (48, 'Cmaj7', [64, 67, 71, 72], 36), (50, 'Em7', [64, 67, 71, 74], 40), (52, 'Am7', [64, 67, 69, 72], 33),
    (54, 'Cmaj7', [64, 67, 71, 72], 36), (56, 'G/B', [62, 67, 71, 74], 35), (57, 'Am7', [64, 67, 69, 72], 33),
    (58, 'D7sus4', [62, 67, 69, 72], 38), (59, 'D7', [62, 66, 69, 72], 38),
    (60, 'Em7', [62, 67, 71, 74], 40), (61, 'Cmaj9', [60, 64, 67, 71, 74], 36), (64, 'G/B', [62, 67, 71, 74], 35),
    (66, 'Am7', [64, 67, 69, 72], 33), (67, 'D7sus4', [62, 67, 69, 72], 38),
    (68, 'Gadd9', [62, 67, 69, 71, 74], 43), (70, 'Cadd9/G', [64, 67, 72, 74], 43), (72, 'G', [62, 67, 71, 74], 43),
]
for _b, _s, _v, _bs in CHART:       # every voicing note is a chord tone of its symbol (or its 9th); bass = root/slash
    _base = _s.split('/')[0]
    _pcs = {n % 12 for n in M.chord(_s)} | {(M.chord(_base)[0] + 2) % 12}
    assert all(n % 12 in _pcs for n in _v), (_s, _v)
    assert _bs % 12 == M.bass_note(_s, 2) % 12 and 31 <= _bs <= 47, (_s, _bs)
VOICING = [v for _, _, v, _ in CHART]
for _p in PILL_BEATS:               # every chord under a pill ding (E6 + B6) holds E and B
    _s = CHART[max(k for k, c in enumerate(CHART) if c[0] <= _p)][1]
    assert {4, 11} <= {n % 12 for n in M.chord(_s)}, (_p, _s)


def chord_index(beat):
    i = 0
    for k, (b, _, _, _) in enumerate(CHART):
        if beat >= b - 1e-9:
            i = k
    return i


def next_change(b):
    i = chord_index(b)
    return CHART[i + 1][0] if i + 1 < len(CHART) else END_BEAT


def bass_of(i):
    return CHART[i][3]


def piano_pool(i):
    """Felt-piano notes of chord i for broken chords: the voicing an octave down (D3-D4) + its 2nd / 3rd notes in
    place (G4-B4): 5-6 notes, D3-C5."""
    v = VOICING[i]
    return sorted(set([n - 12 for n in v] + [v[1], v[2]]))


def guitar_set(i):
    """Nylon-guitar 'strings' of chord i: the bass an octave up (A2-G3 range, >= E2) + the voicing an octave down."""
    b = bass_of(i)
    while b < 40:
        b += 12
    up = sorted(set(n - 12 for n in VOICING[i]))
    return [b] + [n for n in up if n > b]


# ============================================================================================ hooks
# (beat, MIDI, vel, gate_beats, phrase). Every note sits in a VO gap: onset >= 100 ms after a line ends, gate end
# >= 80 ms before the next line starts, release clipped to the rest of the gap (asserted in layer_hooks).
HOOKS = [
    # S: the first VO gap (between the iris swishes, which are triplets): D5 -> E5 ON the iris close (b3)
    (2.5, 74, 0.38, 0.45, 'S'), (3.0, 76, 0.44, 0.7, 'S'),
    # A: seed gap, over D7: into the leaf gust
    (8.0, 69, 0.40, 0.45, 'A'), (8.5, 74, 0.44, 0.5, 'A'),
    # B: NURTURE gap (Cmaj7 -> Am7): the motif B4 D5 E5, landing on the DEVELOP bar line
    (15.0, 71, 0.42, 0.45, 'B'), (15.5, 74, 0.44, 0.45, 'B'), (16.0, 76, 0.48, 0.45, 'B'),
    # C: GROW -> KINDS gap (Cmaj9 | D7sus4 | G): the motif rising on to G5, ON the heart pop
    (35.5, 71, 0.42, 0.45, 'C'), (36.0, 74, 0.44, 0.45, 'C'), (36.5, 76, 0.46, 0.45, 'C'), (37.0, 79, 0.50, 0.6, 'C'),
    # D: MAIN HOOK in the 4.4 s gap after "kinds of care" (Cmaj7 | G/B | Am7 | D7sus4), clear of the dial cues
    (42.0, 71, 0.44, 0.45, 'D'), (42.5, 74, 0.46, 0.45, 'D'), (43.0, 76, 0.52, 0.9, 'D'),
    (44.0, 74, 0.46, 0.45, 'D'), (44.5, 71, 0.44, 0.6, 'D'), (45.25, 69, 0.42, 0.6, 'D'),
    (46.0, 72, 0.46, 0.45, 'D'), (46.5, 76, 0.50, 0.45, 'D'), (47.0, 74, 0.50, 0.9, 'D'),
    # E: after "Rated Good by Ofsted" (D7sus4 | D7 | Em7): A4 D5 E5 -> the logo sting's C bell completes it
    (58.5, 69, 0.42, 0.5, 'E'), (59.25, 74, 0.44, 0.5, 'E'), (60.0, 76, 0.48, 0.9, 'E'),
    # F: after the CTA line: the motif resolved to the tonic (B4 D5 -> G5)
    (71.5, 71, 0.40, 0.25, 'F'), (71.75, 74, 0.36, 0.25, 'F'), (72.0, 79, 0.45, 1.55, 'F'),   # balanced so every
    #                                                     200 ms window from the end of the last line steps down
]
GLOCK = [(43.0, 88, 0.34), (60.0, 88, 0.30), (72.0, 91, 0.34)]


def gap_after(t):
    """(end of the VO line before t, start of the next VO line after t) in seconds (0 / T when none)."""
    prev = max([e for _, _, e in VO_LINES if e <= t + 1e-9] or [0.0])
    nxt = min([s0 for _, s0, _ in VO_LINES if s0 >= t] or [T])
    return prev, nxt


EVENTS = []          # (t, kind, gain_db) for the hero-hit and grid audits
# stem trims (dB) applied when the stems are summed (set from the measured stem loudness, see qa: stems_lufs)
TRIM = dict(pad=1.0, air=5.0, comp=0.0, bass=-1.0, guitar=5.0, marimba=4.0, hooks=-1.0, glock=3.0, shaker=10.0,
            kick=-7.0, sub=-10.0, fx=4.0)
# section dynamics (dB, applied after the bus compressor): the seed breathes in, DEVELOP builds, GROW lifts, the
# trust pulse steps back a little, the end card swells on the sting and settles
SEC_GAIN = [(0.0, 2.5), (4 * BEAT, 2.5), (5 * BEAT, 1.15), (9 * BEAT - 0.05, 1.3), (9 * BEAT, 0.8),
            (16 * BEAT - 0.05, 0.8), (16 * BEAT, 2.0),
            (28 * BEAT, 2.0), (29 * BEAT, 2.6), (34 * BEAT, 2.6), (35 * BEAT, 0.5), (37 * BEAT, 0.3), (47 * BEAT, 0.3),
            (48 * BEAT, -0.2), (60 * BEAT, -0.2), (61 * BEAT, 0.4), (68 * BEAT, 5.8)]
FADE_S = 1.8                         # final fade (s), ending 20 ms before the last sample: 46.38-48.18
SWELL_DB = -22.0                     # pill 2 / 3 air-pad swells (into the pad / air bus)
HOOK_DB = dict(S=-8.0, A=-7.0, B=-7.0)       # hook level per phrase (default -9 dB): the seed / NURTURE gaps carry more


def log(t, kind, gain_db):
    EVENTS.append((round(float(t), 4), kind, round(float(gain_db), 1)))


def onset_ok(b, support=False):
    """An onset at beat b is allowed if it is not within 60 ms of a hero hit (support events: their own cluster
    excepted)."""
    return not near_hero(b * BEAT, support_ok=support)


def hum(rng, ms=3.0):
    return float(rng.uniform(-ms, ms)) * 1e-3


# ============================================================================================ layers
PAD_CUT = dict(seed=650.0, nurture=1250.0, develop=1450.0, grow=1800.0, kinds=1900.0, trust=1600.0, end=1500.0)
PAD_DB = dict(seed=-15.0, nurture=-14.5, develop=-14.5, grow=-13.5, kinds=-14.0, trust=-14.5, end=-14.0)
AIR_SECS = ('grow', 'kinds', 'end')


def layer_pad():
    """Soft string-like pad: 5 detuned saws per note, low-passed, slow attack, chorus. Seed: the filter opens with
    the growth (650 -> 1300 Hz over b0-9). GROW: opens further (the lift) + the air pad (tri, octave up)."""
    pad, air = M.Track(T, 'pad'), M.Track(T, 'air')
    for i in range(len(CHART)):
        b0 = CHART[i][0]
        b1 = CHART[i + 1][0] if i + 1 < len(CHART) else END_BEAT
        t0, t1 = b0 * BEAT, b1 * BEAT
        sec = section(b0)
        last = i == len(CHART) - 1
        dur = (t1 - t0 - 0.05) if not last else (T - t0 - 0.6)
        cut = PAD_CUT[sec]
        open_to = None
        if sec == 'seed':                                     # the growth: 650 -> 1300 Hz across the section
            cut = 650.0 * 2.0 ** (b0 / 9.0)
            open_to = 650.0 * 2.0 ** (b1 / 9.0)
        elif b0 == 29:
            open_to = 2600.0
        att = 1.6 if b0 == 0 else (0.12 if is_support(b0) else 0.35)
        rel = 0.7 if not last else 1.0
        x = M.pad(VOICING[i], dur=dur, vel=0.6, wave='saw', voices=5, detune=13.0, attack=att, release=rel,
                  cutoff=cut, q=0.65, sweep=0.15, sweep_rate=0.06, open_to=open_to, chorus_mix=0.35, width=0.85,
                  seed=SEED + i)
        pad.add(A.hp(x, 150.0, 2), t0, gain_db=PAD_DB[sec])
        if sec in AIR_SECS and not (sec == 'end' and b0 < 61):
            top = [n + 12 for n in VOICING[i][-2:]]
            y = M.pad(top, dur=dur, vel=0.5, wave='tri', voices=4, detune=8.0, attack=0.5 if b0 != 29 else 1.0,
                      release=rel + 0.3, cutoff=4500.0, chorus_mix=0.45, width=1.0, seed=SEED + 100 + i)
            gdb = dict(grow=-25.0, kinds=-26.0, end=-27.0)[sec]
            air.add(A.hp(y, 400.0, 2), t0, gain_db=gdb)
    return pad.buf, air.buf


def comp_events():
    """Felt-piano accompaniment -> [(beat, notes, vel, gate_beats, support)].
    SEED: a few chords (b0, b1 dyad ON the plip, b3, b5, b7, b8). NURTURE / KINDS: broken 8ths (dyad on the
    change, then single notes). DEVELOP: one chord per change. GROW: quarter-chord pulse. TRUST: chord on each
    change + the pill accents. END: long chords."""
    ev = []
    pool = piano_pool
    # SEED
    ev.append((0.0, [50, 55], 0.30, 0.95, False))                    # G (the seed), with the pad
    ev.append((1.0, [55, 62], 0.34, 1.9, True))                      # ON the plip
    ev.append((3.0, [52, 55, 59, 62], 0.34, 1.9, True))              # Em7 ON the iris close
    ev.append((5.0, [52, 55, 59, 64], 0.30, 1.9, False))             # Cmaj9
    ev.append((7.0, [50, 55, 57, 60], 0.36, 0.95, True))             # D7sus4 ON the grow peak
    ev.append((8.0, [50, 54, 57, 60], 0.30, 0.95, False))            # D7 (under hook A)
    # NURTURE + KINDS broken 8ths: dyad (pool[0] + pool[2]) on the change, then BROKEN[k] single notes
    BROKEN = [None, 3, 2, 4, 3, 5, 4, 2]

    def broken(b0, b1, vel_on=0.34, vel_off=0.26):
        k = 0
        b = b0
        while b < b1 - 1e-9:
            i = chord_index(b)
            p = pool(i)
            first = abs(b - CHART[i][0]) < 1e-9
            if first:
                k = 0
            if first or BROKEN[k % 8] is None:
                ev.append((b, [p[0], p[2]], vel_on, min(1.0, next_change(b) - b), is_support(b)))
            else:
                j = min(BROKEN[k % 8], len(p) - 1)
                ev.append((b, [p[j]], vel_off + (0.03 if b % 1 == 0 else 0.0), 0.9, False))
            k += 1
            b += 0.5

    broken(9.0, 16.0)
    broken(37.0, 42.0, 0.34, 0.27)
    # DEVELOP: one chord per change (lower 4 notes) + one soft broken note on the 2nd beat of each 2-beat chord
    # (the piano stays under the new guitar, so DEVELOP adds a layer instead of swapping one)
    for i, (b0, _, _, _) in enumerate(CHART):
        if 16 <= b0 < 29:
            ev.append((float(b0), pool(i)[:4], 0.30, next_change(b0) - b0, False))
            if next_change(b0) - b0 >= 2:
                p = pool(i)
                ev.append((b0 + 1.0, [p[min(4, len(p) - 1)]], 0.22, 0.9, False))
    # GROW: quarter-chord pulse (upper 3 of the pool, short), accent on the changes
    for b in range(29, 37):
        i = chord_index(b)
        acc = abs(b - CHART[i][0]) < 1e-9
        ev.append((float(b), pool(i)[1:4], 0.32 if acc else 0.25, 0.8, is_support(b)))
    # KINDS during the main hook: chords on the changes only (room for the hook)
    for i, (b0, _, _, _) in enumerate(CHART):
        if 42 <= b0 < 48:
            ev.append((float(b0), pool(i)[:3], 0.26, next_change(b0) - b0, False))
    # TRUST: chords on the changes; the first (Cmaj7 E3 G3 B3 C4) moves off the slam cluster to b48.5, ON pill 1
    for i, (b0, _, _, _) in enumerate(CHART):
        if 48 <= b0 < 60:
            b = PILL_ACCENT if b0 == 48 else float(b0)
            ev.append((b, pool(i)[:4], 0.32 if b0 == 48 else 0.28, next_change(b0) - b, b0 == 48))
    # END: Em7, Cmaj9 ON the sting (long), then the resolution
    ev.append((60.0, pool(chord_index(60))[:4], 0.28, 1.0, False))
    ev.append((61.0, [48, 52, 55, 59, 62], 0.40, 2.9, True))
    for b0 in (64, 66, 67, 68, 70):
        i = chord_index(b0)
        gate = (next_change(b0) - b0) if b0 != 70 else (END_BEAT - b0)
        ev.append((float(b0), pool(i)[:4], 0.30 if b0 != 68 else 0.34, gate, False))
    # (no piano chord on b72: the b68 / b70 chords and the pedal tail carry the resolution, so the tail decays)
    return sorted(ev, key=lambda e: e[0])


def layer_piano():
    """Felt piano: accompaniment (comp) and the bass voice (one note per chord change)."""
    comp, bass = M.Track(T, 'comp'), M.Track(T, 'bass')
    rng = np.random.default_rng(SEED + 1)
    for j, (b, notes, vel, gate, sup) in enumerate(comp_events()):
        t = b * BEAT
        if not onset_ok(b, sup):
            b2 = b + 0.5                       # move off the hero hit by an 8th if the chord still holds
            if b2 < next_change(b) and onset_ok(b2, is_support(b2)) and len(notes) > 1:
                b, t, gate, sup = b2, b2 * BEAT, gate - 0.5, is_support(b2)
            else:
                continue
        last = b >= 70
        g = -9.0
        for k, n in enumerate(sorted(notes)):
            x = M.felt_piano(n, dur=max(0.15, gate * BEAT - 0.03), vel=vel + 0.02 * (k == len(notes) - 1),
                             pedal=last, release=0.35, felt=0.85, tail=1.4 if last else 6.0, seed=SEED + j * 7 + k)
            off = (nudge(b) if sup else 0.0 if b % 1 == 0 and len(notes) > 1 else hum(rng)) \
                + 0.0015 * (k - (len(notes) - 1) / 2)
            comp.add(A.hp(x, 120.0, 2), t + off, gain_db=g, pan=-0.18 + 0.06 * k)
        log(t + (nudge(b) if sup else 0.0), 'comp_sup' if sup else 'comp', g)
    for i, (b0, _, _, bn) in enumerate(CHART):
        if b0 >= 72:                           # G2 is already sounding from b70 (Cadd9/G): held, not re-struck
            continue
        b = float(b0)
        sup = is_support(b)
        if not onset_ok(b, sup):
            b = b + 0.5                        # GROW b29 -> b29.5, trust slam b48 -> b48.5 (ON pill 1)
            sup = is_support(b)
            if not (b < next_change(b0) and onset_ok(b, sup)):
                continue
        t = b * BEAT
        last = b0 >= 70
        dl = (next_change(b0) - b) if not last else (END_BEAT - b)
        x = M.felt_piano(bn, dur=max(0.2, dl * BEAT - 0.06), vel=0.46 if not sup else 0.5, pedal=last,
                         release=0.3, felt=0.9, tail=1.2, seed=SEED + 500 + i)
        t += nudge(b) if sup else 0.0
        bass.add(A.hp(x, 35.0, 2), t, gain_db=-8.0)
        log(t, 'bass_sup' if sup else 'bass', -8.0)
    return comp.buf, bass.buf


GT_SEQ = [0, 2, 3, 4, 1, 3, 2, 4]          # 8ths from the chord change: thumb, then i-m-a-m-i style


def guitar_vel(sec, b):
    base = dict(develop=0.50, grow=0.54, kinds=0.56, trust=0.48, end=0.44)[sec]
    return base + (0.06 if b % 1 == 0 else 0.0)


GT_DB = dict(develop=-13.5, grow=-14.5, kinds=-14.0, trust=-15.5, end=-15.5)


def layer_guitar():
    """Nylon guitar (Karplus-Strong): 8th fingerpicking from DEVELOP (b16) to b60.5, 16th pickups in KINDS, a
    strum ON the logo sting (b61), slow quarter arpeggio on the end card, a rolled strum on the tonic b68."""
    gt = M.Track(T, 'guitar')
    rng = np.random.default_rng(SEED + 2)
    k8 = 0
    n8 = int(END_BEAT * 2)
    for k in range(32, n8):                     # b16 ...
        b = k / 2.0
        if b >= 60.75:
            break
        sec = section(b)
        i = chord_index(b)
        if abs(b - CHART[i][0]) < 1e-9:
            k8 = 0
        gs = guitar_set(i)
        if 42 <= b < 47.75 or 58.25 <= b < 60:          # the main hook / hook E: the guitar holds back to 1 + 3
            if b % 2 != 0 and not abs(b - CHART[i][0]) < 1e-9:
                k8 += 1
                continue
        n = gs[min(GT_SEQ[k8 % 8], len(gs) - 1)]
        k8 += 1
        t = b * BEAT
        sup = is_support(b) and b in (35.0, 37.0)
        if not onset_ok(b, sup):
            continue
        ring = min(1.5, next_change(b) - b) * BEAT
        x = M.karplus_strong(n, dur=max(0.2, ring - 0.02), vel=guitar_vel(sec, b), kind='nylon', release=0.15,
                             seed=SEED + 1000 + k)
        g = GT_DB[sec]
        gt.add(A.hp(x, 120.0, 2), t + (nudge(b) if sup else hum(rng)), gain_db=g, pan=0.32)
        log(t + (nudge(b) if sup else 0.0), 'guitar_sup' if sup else 'guitar', g)
        # KINDS: 16th pickup (the 'a' of beats 2 and 4, upper string) outside the hook
        if sec == 'kinds' and b < 42 and b % 2 == 1.5:
            b16 = b + 0.25
            if onset_ok(b16) and b16 < next_change(b):
                x = M.karplus_strong(gs[-1], dur=0.25, vel=0.42, kind='nylon', release=0.1, seed=SEED + 1500 + k)
                gt.add(A.hp(x, 120.0, 2), b16 * BEAT + hum(rng), gain_db=g - 2.0, pan=0.36)
                log(b16 * BEAT, 'guitar', g - 2.0)
    # END: strum ON the logo sting, slow quarter arpeggio, rolled strums on b68 and b72
    st = M.strum([48, 52, 55, 59, 64], dur=3.0 * BEAT, vel=0.52, direction='down', spread=0.018, kind='nylon',
                 width=0.5, seed=SEED + 61)
    gt.add(A.hp(st, 120.0, 2), 61 * BEAT + nudge(61.0), gain_db=-14.0, pan=0.25)
    log(61 * BEAT + nudge(61.0), 'guitar_sup', -14.0)
    for b in (63.0, 64.0, 65.0, 66.0, 67.0):
        i = chord_index(b)
        gs = guitar_set(i)
        n = gs[[0, 3, 0, 2, 0][int(b) - 63]] if b != 63 else gs[3]
        if not onset_ok(b):
            continue
        x = M.karplus_strong(n, dur=0.95 * BEAT, vel=0.42, kind='nylon', release=0.15, seed=SEED + 1700 + int(b))
        gt.add(A.hp(x, 120.0, 2), b * BEAT + hum(rng), gain_db=-16.0, pan=0.32)
        log(b * BEAT, 'guitar', -16.0)
    for b, notes, vel, sp in ((68.0, [43, 50, 55, 59, 62, 69], 0.46, 0.022),):     # (no re-strike on b72: the
        d = 3.9 * BEAT                                                                # tail decays from here)
        st = M.strum(notes, dur=d, vel=vel, direction='down', spread=sp, kind='nylon', width=0.6, seed=SEED + int(b))
        gt.add(A.hp(st, 120.0, 2), b * BEAT, gain_db=-15.0, pan=0.25)
        log(b * BEAT, 'guitar', -15.0)
    return M.haas(gt.buf, ms=11.0, side='left', level_db=-4.0)


def layer_marimba():
    """Marimba: off-beat 8ths in GROW and KINDS (top two voicing notes, D4-D5), resting under hook C and the main
    hook; the pill-1 accent (E4 + B4) ON the first ding in TRUST."""
    mr = M.Track(T, 'marimba')
    rng = np.random.default_rng(SEED + 3)
    for k in range(int(END_BEAT * 2)):
        b = k / 2.0
        if b % 1 == 0:
            continue
        if not (29.5 <= b < 35.0 or 37.5 <= b < 41.75):
            continue
        i = chord_index(b)
        v = VOICING[i]
        n = v[-1] if (k // 2) % 2 == 0 else v[-2]
        if not onset_ok(b):
            continue
        g = -17.0 if section(b) == 'grow' else -17.5
        x = M.marimba(n, vel=0.42 + 0.04 * ((k // 2) % 2 == 0), hardness=0.3, decay=0.9, seed=SEED + 2000 + k)
        mr.add(A.hp(x, 200.0, 2), b * BEAT + hum(rng, 2.0), gain_db=g, pan=-0.3 if (k // 2) % 2 else -0.1)
        log(b * BEAT, 'marimba', g)
    for j, b in enumerate((PILL_ACCENT,)):                  # an octave under the dings (E6 + B6): out of the way
        t = b * BEAT + nudge(b)                             # of the voice's 1-4 kHz band
        assert onset_ok(b, True)
        for n, pn in ((64, -0.2), (71, 0.2)):
            x = M.marimba(n, vel=0.55, hardness=0.3, decay=1.0, seed=SEED + 2500 + j * 2 + (n == 71))
            mr.add(A.hp(x, 200.0, 2), t, gain_db=-14.0, pan=pn)
        log(t, 'accent_sup', -14.0)
    return mr.buf


def layer_pill_swells():
    """Pills 2 and 3: a soft air-pad swell of E4 + B4 (tri, one voice, no chorus: the peak is not smeared) on a 16th
    (b51 / b53.75) with a raised-cosine attack that ends exactly ON the ding (EDIT pill2 / pill3), then releasing:
    an accent per pill with no transient 24-26 ms off the ding."""
    sw = M.Track(T, 'swell')
    for j, (b, k) in enumerate(PILL_SWELLS):
        t0 = b * BEAT
        att = EDIT[k] - t0
        y = M.pad([64, 71], dur=att, vel=0.5, wave='tri', voices=1, attack=att, release=0.45, cutoff=3000.0,
                  chorus_mix=0.0, drift=0.0, seed=SEED + 300 + j)       # one voice per note, centred: no detune
        #                                                                  beating / Haas delay to move the peak
        sw.add(A.hp(y, 250.0, 2), t0, gain_db=SWELL_DB)
        log(t0, 'swell_sup', SWELL_DB)
    return sw.buf


def layer_hooks():
    """Hooks (felt piano, brighter felt; marimba double from hook C on) + glockenspiel sparkle, all in VO gaps."""
    hk, gl = M.Track(T, 'hooks'), M.Track(T, 'glock')
    for j, (b, m, vel, dl, ph) in enumerate(HOOKS):
        t = b * BEAT
        prev, nxt = gap_after(t)
        sup = is_support(b)
        assert onset_ok(b, sup), ('hook near a hero hit', b, t)
        assert not speaking(t, 0.1, 0.1) and t - prev >= 0.1, ('hook under speech', b, t)
        assert t + dl * BEAT <= nxt - 0.08, ('hook gate runs into the next line', b, t, nxt)
        assert sup or not any(abs(t - c) < 0.06 and g >= -12.0 for c, g, _ in SFX_CUES), ('hook on an SFX cue', b)
        last = nxt >= T - 1e-6
        rel = 0.5 if last else float(np.clip(nxt - (t + dl * BEAT) - 0.08, 0.1, 0.6))
        x = M.felt_piano(m, dur=dl * BEAT, vel=vel, pedal=False, release=rel, felt=0.7, seed=SEED + 7000 + j)
        t += nudge(b) if sup else 0.0
        hk.add(A.hp(x, 180.0, 2), t, gain_db=HOOK_DB.get(ph, -9.0), pan=0.08)
        if ph in 'CDEF':
            y = M.marimba(m, vel=vel * 0.9, hardness=0.4, decay=0.9 if not last else 1.3, seed=SEED + 7100 + j)
            if not last:                                          # the wood ring dies in the gap
                y = y[:int((nxt - t - 0.08) * SR)]
                y = M.fade_out(y[:, None], 0.06)[:, 0] if len(y) > int(0.07 * SR) else y
            hk.add(A.hp(y, 200.0, 2), t, gain_db=-16.0, pan=-0.12)
        log(t, 'hook_sup' if sup else 'hook', HOOK_DB.get(ph, -9.0))
    for j, (b, m, vel) in enumerate(GLOCK):
        t = b * BEAT
        prev, nxt = gap_after(t)
        assert onset_ok(b) and not speaking(t, 0.1, 0.1)
        y = M.glockenspiel(m, vel=vel, hardness=0.4, decay=0.6, seed=SEED + 9 + j)
        if nxt < T - 1e-6:
            y = y[:int((nxt - t - 0.05) * SR)]
            y = M.fade_out(y[:, None], 0.2)[:, 0]
        gl.add(A.hp(y, 400.0, 2), t, gain_db=-24.0, pan=0.22)
        log(t, 'glock', -24.0)
    return hk.buf, gl.buf


def layer_perc():
    """Shaker (16ths in GROW and KINDS, 8ths in TRUST; stroke peak on the step) and the very soft low pulse
    (soft_kick: support hits on b35 / b37 / b61, half notes in KINDS, every beat in TRUST from b49)."""
    sh, kick = M.Track(T, 'shaker'), M.Track(T, 'kick')
    rng = np.random.default_rng(SEED + 4)
    acc = (1.0, 0.45, 0.75, 0.5)
    for k in range(int(END_BEAT * 4)):
        b = k / 4.0
        sec = section(b)
        t = k * STEP
        sv = None
        if sec == 'grow' and b >= 29.5:
            sv, sg = 0.5, -29.0 + 2.0 * (b - 29.5) / 7.5          # grows in across GROW
        elif sec == 'kinds':
            sv, sg = 0.55, -26.5
        elif sec == 'trust' and k % 2 == 0 and b < 58.5:
            sv, sg = 0.55, -27.0
        if sv is None or not onset_ok(b):
            continue
        x = M.shaker(vel=sv * acc[k % 4], length=0.065, tone=7000.0, attack=0.012, seed=k % 16)
        sh.add(A.hp(x, 300.0, 2), t - 0.012 + rng.uniform(-0.002, 0.002), gain_db=sg, pan=0.38 if k % 2 else 0.18)
    beats = [35.0, 37.0, 38.0, 40.0, 42.0, 44.0, 46.0] + [float(b) for b in range(49, 60)] + [61.0]
    kick_times = []
    for b in beats:
        sup = b in (35.0, 37.0, 61.0)
        if not onset_ok(b, sup):
            continue
        t = b * BEAT + (nudge(b) if sup else 0.0)
        vel = 0.62 if sup else (0.70 if b % 2 == 0 else 0.58)     # support pulses soft: they sum with the hit
        x = M.soft_kick(vel=vel, punch=0.15, tone=50.0, decay=0.32, click=0.03, drive=1.15)
        kick.add(A.lp(x, 900.0, 2), t, gain_db=-6.0)
        kick_times.append(t)
        log(t, 'kick_sup' if sup else 'kick', -6.0)
    return sh.buf, kick.buf, kick_times


def layer_sub():
    """Sub warmth under KINDS, TRUST and the end card: a soft sine-like sub on the bass note, swelling in."""
    sub = M.Track(T, 'sub')
    for i, (b0, _, _, bn) in enumerate(CHART):
        if b0 < 37 or b0 >= 72:              # the b70 G2 sub holds to the end (no re-attack on b72)
            continue
        last = b0 >= 70
        dl = (next_change(b0) - b0) if not last else (END_BEAT - b0)
        x = M.sub_bass(bn, dur=dl * BEAT - (0.08 if not last else 0.9), vel=0.6, drive=1.1, harm=0.05, attack=0.04,
                       release=0.12 if not last else 0.8)
        sub.add(x, b0 * BEAT, gain_db=-12.0)
        log(b0 * BEAT, 'sub_swell', -12.0)
    return sub.buf


def layer_fx():
    """A reversed Gadd9 swell ENDING on the GROW downbeat b29 (the air_zoom 26 ms later)."""
    fx = M.Track(T, 'fx')
    t29 = 29 * BEAT
    d = 2.0 * BEAT
    fx.add(A.hp(M.reverse_swell(d, vel=0.5, notes=VOICING[chord_index(29)], bright=0.8, seed=SEED + 5), 250.0, 2),
           t29 - d, gain_db=-20.0)
    return fx.buf


# ============================================================================================ speech-aware filter
def speech_env(n, pre=0.06, post=0.12, close=0.06, open_=0.30):
    """Per-sample speech envelope 0..1: 1 while a VO line plays (start - pre .. end + post), 0 in the gaps, moving
    with a one-pole (close / open_ time constants) at a 64-sample control rate."""
    blk = 64
    m = (n + blk - 1) // blk
    tb = (np.arange(m) + 0.5) * blk / SR
    tgt = np.zeros(m)
    for _, s0, e0 in VO_LINES:
        tgt[(tb >= s0 - pre) & (tb <= e0 + post)] = 1.0
    y = np.empty(m)
    v = tgt[0]
    ca, cr = np.exp(-blk / (close * SR)), np.exp(-blk / (open_ * SR))
    for j in range(m):
        c = ca if tgt[j] > v else cr
        v = c * v + (1.0 - c) * tgt[j]
        y[j] = v
    return np.interp(np.arange(n), (np.arange(m) + 0.5) * blk, y)


VO_DUCK_DB = 13.0                  # A.sidechain depth under the VO (full depth only near the voice's peak level;
#                                    measured median under speech in qa: bed.duck_median_under_speech_db)
DUCK_FLOOR_DB = 14.0               # minimum total duck while the speech mask is on (60 ms look-ahead, 100 ms hang,
#                                    20 / 150 ms ballistics): quiet word starts, tails and breaths get the full duck
SPEECH_LP = (1000.0, 15000.0)      # low-pass cutoff under speech / in the gaps
SPEECH_DIP = (2000.0, 0.5, -12.0)   # + a peaking dip under speech (Hz, Q, dB)
SPEECH_DIP_LO = (650.0, 0.6, -8.0)  # + a broad low-mid dip under speech: the voice's 300 Hz-1.5 kHz body, where the
#                                     pad / piano / bass piano masked it (1.5-4 kHz measured >= 13 dB clear)
SPEECH_HARM_DB = -2.0              # pad / air / piano level under speech
BASS_LP = (250.0, 1200.0)          # bass-piano low-pass under speech / in the gaps (upper partials sit on the voice)


def speech_dip(x, s):
    y = x
    for f, q, g in (SPEECH_DIP, SPEECH_DIP_LO):
        y = A.eq(y, 'peak', f, q, g)
    return x + s[:, None] * (y - x)


def speech_carve(x, s):
    """2-pole low-pass sliding between SPEECH_LP[1] (gaps) and SPEECH_LP[0] (speech) in the log domain, plus the
    SPEECH_DIP peaking cut cross-faded in by the speech envelope s."""
    lo, hi = SPEECH_LP
    fc = np.exp(np.log(hi) + s * (np.log(lo) - np.log(hi)))
    return speech_dip(M.tv_lowpass(x, fc, q=0.707), s)


# ============================================================================================ render
PARTS = {}


def render(verbose=True):
    t0 = time.time()
    EVENTS.clear()
    u = lambda k: A.undb(TRIM[k])                     # noqa: E731
    pad, air = (y * u(k) for y, k in zip(layer_pad(), ('pad', 'air')))
    air = air + layer_pill_swells()
    comp, bass = layer_piano()
    comp, bass = comp * u('comp'), bass * u('bass')
    gtr = layer_guitar() * u('guitar')
    mar = layer_marimba() * u('marimba')
    hooks, glock = layer_hooks()
    hooks, glock = hooks * u('hooks'), glock * u('glock')
    shaker, kick, kick_times = layer_perc()
    shaker, kick = shaker * u('shaker'), kick * u('kick')
    sub = layer_sub() * u('sub')
    fx = layer_fx() * u('fx')
    sp = speech_env(N)
    trust_k = [t for t in kick_times if 48 * BEAT - 0.01 <= t < 60 * BEAT]
    hl = sp.copy()                                    # pad / piano level dip: held after the last line (the outro
    hl[int(VO_LINES[-1][2] * SR):] = 1.0              # does not swell back up under hook F; the filters still open)
    harm = speech_carve(M.pump(pad + air + comp, trust_k, depth_db=1.5, attack=0.004, release=0.25), sp) \
        * A.undb(SPEECH_HARM_DB * hl)[:, None]
    gtr_f = speech_carve(gtr, sp) * A.undb(-3.0 * sp)[:, None]
    mar_f = speech_carve(mar, sp) * A.undb(-3.0 * sp)[:, None]
    hk_f = speech_carve(hooks + glock, sp)
    sh_f = speech_carve(shaker, sp) * A.undb(-4.0 * sp)[:, None]
    fx_f = speech_carve(fx, sp)
    sends = (M.reverb_send(harm + gtr_f, 'hall', wet_db=-15.0, hp_hz=250.0)
             + M.reverb_send(mar_f + hk_f + sh_f, 'plate', wet_db=-16.0, hp_hz=300.0)
             + M.reverb_send(hk_f, 'air', wet_db=-17.0, hp_hz=400.0)
             + M.reverb_send(harm, 'air', wet_db=-24.0, hp_hz=400.0))
    blp = np.exp(np.log(BASS_LP[1]) + sp * (np.log(BASS_LP[0]) - np.log(BASS_LP[1])))
    low = M.tv_lowpass(bass, blp, q=0.707) + M.pump(A.lp(sub, 300.0, 2), trust_k, depth_db=2.0, attack=0.004,
                                                    release=0.2)
    # outro: once the last line ends the bass piano + sub tail eases down 4 dB over 0.6 s, under hook F
    low = low * A.undb(np.interp(np.arange(N) / SR, [VO_LINES[-1][2], VO_LINES[-1][2] + 0.6], [0.0, -4.0]))[:, None]
    mix = harm + gtr_f + mar_f + hk_f + sh_f + fx_f + low + kick + sends
    mix = A.hp(mix, 30.0, 2)
    mix = M.bus_comp(mix, thresh_db=-20.0, ratio=1.5, attack=0.015, release=0.25)
    mix = M.tilt_eq(mix, 0.6)
    mix = M.gain_ramp(mix, SEC_GAIN)
    mix = M.fade_out(mix, FADE_S, end=T - 0.02)          # fade 46.38-48.18, silence in the last 20 ms
    mix, info = M.normalise_lufs(mix, target=-16.0, tp_ceiling=-1.2)
    mix[int(round((T - 0.02) * SR)):] = 0.0
    stems = dict(pad=pad, air=air, comp=comp, bass=bass, guitar=gtr, marimba=mar, hooks=hooks, glock=glock,
                 shaker=shaker, kick=kick, sub=sub, fx=fx, sends=sends)
    PARTS.clear()
    PARTS.update(harm=harm, guitar=gtr_f, marimba=mar_f, hooks=hk_f, shaker=sh_f, fx=fx_f, low=low, kick=kick,
                 sends=sends)
    if verbose:
        print('render: %.1f s, normalise %s' % (time.time() - t0, info))
    return mix, stems, info


# ============================================================================================ QA
def band_db(x, lo=1000.0, hi=4000.0, win=0.1, order=2):
    """Per-window energy (dB) of the lo-hi band (default 1-4 kHz) of a stereo signal (mono sum), 100 ms windows."""
    y = A.bp(A._st(x).mean(1), lo, hi, order)
    w = int(win * SR)
    m = len(y) // w
    e = (y[:m * w] ** 2).reshape(m, w).mean(1)
    return 10 * np.log10(e + 1e-20)


def grid_audit():
    """Every logged event onset vs the 16th grid."""
    worst = (0.0, None)
    for t, kind, _ in EVENTS:
        dev = abs(t - round(t / STEP) * STEP)
        if dev > worst[0]:
            worst = (dev, (t, kind))
    return dict(n_events=len(EVENTS), max_dev_ms=round(worst[0] * 1000, 2), worst=worst[1],
                ok=bool(worst[0] <= 0.008))


def hero_audit(clean):
    """Music transients near the SFX hero hits. (1) Event log: arrangement onsets within +-60 ms of a hero hit
    that are not on a SUPPORT instant (should be none, apart from sub swells). (2) Measurement on the clean
    music, high-passed at 150 Hz, 8 ms RMS: onset rise = the level jump over 10 ms. Per hero hit (outside the
    support clusters): the largest rise inside +-60 ms and the level there, relative to the median piano / guitar
    onset."""
    near = [e for e in EVENTS if near_hero(e[0]) and not e[1].endswith('_sup') and e[1] != 'sub_swell']
    sup = [e for e in EVENTS if e[1].endswith('_sup')]
    m = A.hp(A._st(clean).mean(1), 150.0, 2)
    w = int(0.008 * SR)
    env = 10 * np.log10(np.convolve(m * m, np.ones(w) / w, 'same') + 1e-12)
    lag = int(0.010 * SR)
    rise = np.zeros_like(env)
    rise[lag:] = env[lag:] - env[:-lag]

    def onset(t0, t1):
        a, b = max(lag, int(t0 * SR)), min(len(env), int(t1 * SR))
        j = a + int(np.argmax(rise[a:b]))
        return float(rise[j]), float(env[j])

    refs = [e[0] for e in EVENTS if e[1] in ('comp', 'guitar') and abs(e[0] / BEAT - round(e[0] / BEAT)) < 1e-3]
    ob = np.array([onset(t - 0.01, t + 0.03) for t in refs])
    r_ref, l_ref = float(np.median(ob[:, 0])), float(np.median(ob[:, 1]))
    rows = []
    for h in HERO:
        if any(abs(h - s) <= 0.04 for s in SUPPORT):
            continue
        r, lv = onset(h - 0.06, h + 0.06)
        rows.append((h, round(r - r_ref, 1), round(lv - l_ref, 1)))
    rows.sort(key=lambda r: -(r[1] + r[2]))
    typ = np.array([onset(t - 0.06, t + 0.06) for t in np.arange(6.03, 46.0, 0.137)
                    if not any(abs(t - h) < 0.12 for h in HERO)])
    return dict(n_hero=len(HERO), n_support_events=len(sup), events_near=near,
                beat_onset_rise_db=round(r_ref, 1), worst_rise_rel_level_rel=rows[:6],
                typical_window_rise_rel_level_rel=(round(float(np.median(typ[:, 0])) - r_ref, 1),
                                                   round(float(np.median(typ[:, 1])) - l_ref, 1)),
                hero_median_rise_rel_level_rel=(round(float(np.median([r[1] for r in rows])), 1),
                                                round(float(np.median([r[2] for r in rows])), 1)))


def ffprobe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path],
                       capture_output=True, text=True)
    return json.loads(r.stdout or '{}')


def qa(clean, bed, bedm, mix, rep, stems, vo_stem):
    out = {}
    q = M.qa(clean)
    tail = float(A.db(np.max(np.abs(clean[-int(0.02 * SR):])) + 1e-12))
    out['clean'] = dict(samples=len(clean), dur=round(len(clean) / SR, 5), lufs=q['lufs'], true_peak=q['true_peak'],
                        peak_dbfs=q['peak_dbfs'], clip=q['clip'], last20ms_dbfs=round(tail, 1),
                        dc=q['dcrep']['dc'], sub20_db=q['dcrep']['sub20_db'], sub40_db=q['dcrep']['sub40_db'],
                        low60_pct=q['dcrep']['low60_pct'], dc_ok=q['dcrep']['ok'], clicks=q['clicks']['count'],
                        click_events=q['clicks']['events'][:3], lra=round(A.loudness_range(clean), 2))
    lo = A.lp(clean, 120.0, 4)
    mid, side = lo.mean(1), 0.5 * (lo[:, 0] - lo[:, 1])
    out['clean']['low120_side_minus_mid_db'] = round(float(10 * np.log10((side ** 2).sum() / (mid ** 2).sum()
                                                                         + 1e-20)), 1)
    out['clean']['corr_LR'] = round(float(np.corrcoef(clean[:, 0], clean[:, 1])[0, 1]), 3)
    full_side = 0.5 * (clean[:, 0] - clean[:, 1])
    out['clean']['side_minus_mid_db'] = round(float(10 * np.log10((full_side ** 2).sum() /
                                                                  (clean.mean(1) ** 2).sum() + 1e-20)), 1)
    _, st = A.loudness_curve(clean, win=3.0, hop=0.1)
    tt = np.arange(len(st)) * 0.1 + 1.5
    secl = {}
    for j, (k, b0) in enumerate(SEC_EDGES):
        b1 = SEC_EDGES[j + 1][1] if j + 1 < len(SEC_EDGES) else END_BEAT
        sel = (tt >= b0 * BEAT) & (tt < b1 * BEAT)
        if sel.any():
            secl[k] = round(float(np.median(st[sel])), 1)
    out['clean']['section_st_lufs'] = secl
    out['beatgrid'] = M.beat_grid_check(clean, BPM)
    out['grid'] = grid_audit()
    out['stems_lufs'] = {k: round(A.loudness(v), 1) for k, v in stems.items() if np.any(v)}
    out['bed'] = dict(bedm, lufs=round(A.loudness(bed), 2), true_peak=round(A.true_peak(bed), 2), samples=len(bed),
                      last20ms_dbfs=round(float(A.db(np.max(np.abs(bed[-int(0.02 * SR):])) + 1e-12)), 1),
                      clicks=M.click_report(bed)['count'])
    out['withmusic'] = {k: v for k, v in rep.items() if k != 'stems'}
    out['withmusic']['samples'] = len(mix)
    out['withmusic']['clicks'] = M.click_report(mix)['count']
    # voice vs music under speech (in the final master): momentary median and 100 ms speech-band windows
    vo_m, mu_m = rep['stems']['vo'], rep['stems']['music']
    _, lv = A.loudness_curve(vo_m)
    _, lm = A.loudness_curve(mu_m)
    sel = lv > lv.max() - 15.0
    d = (lv - lm)[sel]
    sp = M.speech_mask(vo_m)
    w = int(0.1 * SR)
    nw = len(sp) // w
    spw = sp[:nw * w].reshape(nw, w).mean(1) > 0.8
    bv, bm = band_db(vo_m)[:nw], band_db(mu_m)[:nw]
    db_ = (bv - bm)[spw]
    voiced = spw & (bv > np.median(bv[spw]) - 15.0)
    dv = (bv - bm)[voiced]
    out['voice_vs_music'] = dict(momentary_median_lu=round(float(np.median(d)), 2),
                                 momentary_p10_lu=round(float(np.percentile(d, 10)), 2),
                                 band1_4k_100ms_median_db=round(float(np.median(db_)), 2),
                                 band1_4k_100ms_p10_db=round(float(np.percentile(db_, 10)), 2),
                                 n_windows=int(spw.sum()),
                                 voiced_band1_4k_100ms_median_db=round(float(np.median(dv)), 2),
                                 voiced_band1_4k_100ms_p10_db=round(float(np.percentile(dv, 10)), 2),
                                 voiced_band1_4k_100ms_min_db=round(float(np.min(dv)), 2), n_voiced=int(voiced.sum()))
    # speech-band overlap gate: vo_stem vs the bed as delivered, 300 Hz-4 kHz, 100 ms windows, speech windows =
    # speech mask mean > 0.8; share of windows with the voice < 6 dB above the bed (all / voice within 15, 10 dB
    # of its median); the gate is the 15 dB set <= OVERLAP_MAX
    vs = A._st(vo_stem)
    spf = M.speech_mask(vs)
    nwf = len(spf) // w
    spwf = spf[:nwf * w].reshape(nwf, w).mean(1) > 0.8
    ov = {}
    for o in (2, 4):
        bvf = band_db(vs, 300.0, 4000.0, order=o)[:nwf]
        dd = bvf - band_db(bed, 300.0, 4000.0, order=o)[:nwf]
        mv = np.median(bvf[spwf])
        r = dict(all_lt6='%d/%d' % ((dd[spwf] < 6).sum(), spwf.sum()),
                 median_margin_db=round(float(np.median(dd[spwf])), 1))
        for gwin in (15.0, 10.0):
            sel = spwf & (bvf > mv - gwin)
            r['voiced%d_lt6' % gwin] = '%d/%d' % ((dd[sel] < 6).sum(), sel.sum())
            r['voiced%d_share' % gwin] = round(float((dd[sel] < 6).mean()), 4)
        sel = spwf & (bvf > mv - 15.0)
        r['lt6_at_s'] = [round(i * 0.1 + 0.05, 2) for i in np.where(sel & (dd < 6))[0]]
        ov['order%d' % o] = r
    out['speech_band_overlap'] = ov
    # the spec's voice-clarity rule (asserted): vo_stem vs the bed, 300 Hz-4 kHz (2-pole), 100 ms windows, 50 ms
    # hop, speech = M.speech_mask at the window centre (ungated: quiet word starts, tails, breaths included); the
    # share of windows with the voice < 6 dB above the bed <= OVERLAP_MAX, median >= 10 dB
    Wn, Hn = int(0.1 * SR), int(0.05 * SR)
    s0 = np.arange(0, len(vs) - Wn + 1, Hn)

    def _wdb(y):
        c = np.concatenate([[0.0], np.cumsum(y * y)])
        return 10 * np.log10((c[s0 + Wn] - c[s0]) / Wn + 1e-20)
    dd = _wdb(A.bp(vs.mean(1), 300.0, 4000.0, 2)) - _wdb(A.bp(A._st(bed).mean(1), 300.0, 4000.0, 2))
    ins = spf[s0 + Wn // 2]
    out['clarity_spec'] = dict(lt6='%d/%d' % ((dd[ins] < 6).sum(), ins.sum()),
                               share=round(float((dd[ins] < 6).mean()), 4),
                               median_db=round(float(np.median(dd[ins])), 1),
                               lt6_at_s=[round(float(s0[i] / SR + 0.05), 2) for i in np.where(ins & (dd < 6))[0]])
    assert out['clarity_spec']['share'] <= OVERLAP_MAX and out['clarity_spec']['median_db'] >= 10.0, \
        out['clarity_spec']
    # ending: 200 ms RMS windows of the clean music from the end of the last line; each <= the one before
    t_last = VO_LINES[-1][2]
    wv = int(0.2 * SR)
    ends = [(round(t, 2), round(float(10 * np.log10((clean[int(t * SR):int(t * SR) + wv] ** 2).mean() + 1e-20)), 2))
            for t in np.arange(t_last, T - 0.2, 0.2)]
    out['end_decay'] = dict(windows=ends, monotonic=bool(all(ends[i + 1][1] <= ends[i][1] for i in
                                                               range(len(ends) - 1))))
    # each VO gap (from 0.4 s after a line, past the duck release, to 50 ms before the next): bed loudness vs the
    # delivered mix's integrated loudness (the bed is laid at 0 dB under reel3_vo_mix.wav)
    ref = bedm['ref_lufs']
    rows = []
    edges = [(0.0, VO_LINES[0][1])] + [(VO_LINES[i][2], VO_LINES[i + 1][1]) for i in range(len(VO_LINES) - 1)] \
        + [(VO_LINES[-1][2], T)]
    for a, b in edges:
        a2, b2 = a + 0.4, b - 0.05
        if b2 - a2 >= 0.4:
            lb = A.loudness(bed[int(a2 * SR):int(b2 * SR)])
            rows.append((round(a, 2), round(b, 2), round(lb, 1), round(lb - ref, 1)))
    out['gaps_bed_lufs_minus_ref'] = rows
    out['hero'] = hero_audit(clean)
    return out


OVERLAP_MAX = 0.05                 # QA gate: share of speech windows (300 Hz-4 kHz, 100 ms / 50 ms hop, ungated),
#                                    voice - bed < 6 dB


# ============================================================================================ main
def main():
    t0 = time.time()
    print('edit (output s):', {k: round(v, 3) for k, v in EDIT.items()})
    print('sections (beat -> s):', [(k, b, round(b * BEAT, 3)) for k, b in SEC_EDGES])
    clean, stems, info = render()
    assert len(clean) == N
    A._write_wav(OUT_CLEAN, clean, 24)
    st = M.load_reel_stems('reel3')
    assert st['n'] == N, st['n']
    # duck floor keyed on the speech mask: the level-proportional A.sidechain only reaches full depth near the
    # voice's peak, so quiet word starts / tails / breaths got ~5 dB; pre-duck so the total is >= DUCK_FLOOR_DB
    sp = M.speech_mask(st['vo'])
    g_sc = A.db(A.sidechain(np.ones((N, 2)), st['vo'], depth_db=VO_DUCK_DB, attack=0.04, release=0.4)[:, 0])
    g_fl = A._ballistics(-DUCK_FLOOR_DB * M._dilate(sp, 0.06, 0.10), 0.02, 0.15)
    pre = clean * A.undb(np.minimum(0.0, g_fl - g_sc))[:, None]
    bed, bedm = M.render_bed(pre, st['vo'], st['sfx'], st['mix'], gap_lu=7.0, min_vo_lu=10.0,
                             vo_duck_db=VO_DUCK_DB, vo_attack=0.04, vo_release=0.4, sfx_duck_db=3.0, sfx_attack=0.01,
                             sfx_release=0.25)
    bed[-int(0.02 * SR):] = 0.0
    A._write_wav(OUT_BED, bed, 24)
    mix, rep = M.master_withmusic(st['vo'], st['sfx'], bed, target=-14.0, tol=0.2, ceiling=-2.3, tp_max=-2.0)
    A._write_wav(OUT_MIX, mix, 24)
    os.makedirs(REEL, exist_ok=True)
    M.write_mp3(OUT_BED, MP3_BED, TITLE + ' (ducked bed)', artist='Organic Fostering')
    M.write_mp3(OUT_CLEAN, MP3_CLEAN, TITLE + ' (clean, full level)', artist='Organic Fostering')
    prev = None
    if os.path.exists(VIDEO_IN):
        prev = M.make_preview(VIDEO_IN, OUT_MIX, PREVIEW, audio_bitrate='192k')
    else:
        print('PREVIEW NOT WRITTEN: %s is missing (set MUSIC_SCRATCH to the folder holding reel3_vo_preview.mp4)'
              % VIDEO_IN, file=sys.stderr)
    rpt = qa(clean, bed, bedm, mix, rep, stems, st['vo'])
    rpt['mp3'] = []
    for p in (MP3_BED, MP3_CLEAN):
        pr = ffprobe(p)
        s0 = pr['streams'][0]
        rpt['mp3'].append(dict(path=p, codec=s0.get('codec_name'), bit_rate=int(s0.get('bit_rate', 0)),
                               sample_rate=int(s0.get('sample_rate', 0)), channels=s0.get('channels'),
                               dur=round(float(pr['format']['duration']), 3),
                               title=pr['format'].get('tags', {}).get('title')))
    if prev:
        pr = ffprobe(PREVIEW)
        rpt['preview'] = dict(path=PREVIEW, size_mb=round(os.path.getsize(PREVIEW) / 1e6, 2),
                              dur=round(float(pr['format']['duration']), 3),
                              streams=[(s['codec_type'], s['codec_name'], s.get('sample_rate'), s.get('bit_rate'))
                                       for s in pr['streams']])
    rpt['render_s'] = round(time.time() - t0, 1)
    print(json.dumps(rpt, indent=1, default=str))
    if not prev:
        print('PREVIEW NOT WRITTEN: %s' % PREVIEW, file=sys.stderr)
        sys.exit(2)
    return rpt


if __name__ == '__main__':
    main()
