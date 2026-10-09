"""reel2_vo_music.py: original background music for REEL 2 VO "Financial support" (Organic Fostering).

    cd pipeline/fostering && nice -n 5 python3 reel2_vo_music.py      (deterministic, seeded)

Synthesised from scratch with music_synth.py + audio.py (numpy / scipy only: no samples, no downloads, no AI).
Mood: confident, positive, premium corporate-electronic, reassuring (money talk without being salesy). Amber
dashboard look: gold 3D coins, the GBP 447.60 counter, the allowance calculator, the support ring, the end card.

KEY      Eb major (Ab-Lydian colour on the IV: Bb/Ab).
TEMPO    128 BPM, 4/4. Beat n = n * 0.46875 s from 0.000 (beat 1 of the music = 0.000 s), bar = 1.875 s.
         94.72 beats = 23.68 bars (bars 0-23, bar 23 cut at 44.400). Every rhythmic event sits on the 16th grid
         (EP chord spread <= 6 ms, shaker / hat humanise <= 3 ms: all within +-8 ms).
         Length: exactly round(44.4 * 48000) = 2131200 samples (= the VO mix / stems).
EDIT     Section edges are computed in OUTPUT time from reel2_vo (V.out_time on the reel2.py constants T_NUM,
         T_CALC, DRAG, T_ORB, T_HEART, T_END; V.vo_cues(); V.cues() hero hits = gain_db >= -6, start-aligned cues
         at t + A.hit_offset). An edge within one beat of a bar line moves to that bar line, otherwise to the
         nearest beat (edge_beat(); asserted against the table below).

MUSIC MAP (output time; b = beat index from 0.000 s, bar = b // 4)
section  | beats      | t0-t1 s      | edit events (reel2_vo)                 | music events
---------|------------|--------------|----------------------------------------|------------------------------------------
HOOK     | b0-8       | 0.000-3.750  | coin flip 0.03, tunnel B1 0.469         | b0-3: Ab/Bb pad swelling (filter opening),
(bars    |            |              | (flash), whooshes b1.5-2.5, TITLE SLAM | short riser + reversed Ebmaj9 swell ENDING
 0-1)    |            |              | b3 1.406 (impact_big), "Support" b3.5, | on the slam; b3: music downbeat ON the slam
         |            |              | swish b4; VO financial_support         | (kick, sub Eb, EP + pad Ebmaj9), kick on
         |            |              | 0.20-3.76                              | b3.5 ("Support"); Cm9 b6; filtered pluck
         |            |              |                                        | arp 8ths, shaker 8ths creep in
NUMBER   | b8-26      | 3.750-12.188 | T_NUM 4.011 (air_zoom, b8.56 -> bar    | steady pulse: soft four-on-the-floor kick,
(bars    |            |              | line b8), counter rolls 4.06, LANDS    | offbeat hats, sub (1 + and-of-2), EP stabs,
 2-6)    |            |              | 5.417 (kaching); pop 5.886; VO         | 16th saw-pluck arp; claps 2 & 4 + shaker
         |            |              | from_amount 5.20-11.35                 | 16ths from b16. Abmaj9 Ebmaj7/G Cm9 Fm9
         |            |              |                                        | Bb9sus Ebadd9. Gap motifs b9-10.5 (rising,
         |            |              |                                        | under the roll) and b24.5-25.5
CALC A   | b26-32     | 12.188-15.000| T_CALC whip 12.190 (b26.005, mid-bar ->| downbeat ON the whip (kick, sub, EP Abmaj9);
(clicks) |            |              | b26); chip clicks b27-31 (+2.5 ms);    | then NO kick: the clicks are the beat. Pad
         |            |              | VO rise_with_age 12.86-14.99           | Abmaj9 Bb/Ab (Lydian lift) Cm9, shaker 16ths
         |            |              |                                        | between the clicks, offbeat pluck 8ths
DRAG     | b32-35     | 15.000-16.406| slider drag 15.237 (b32.5) -> TOTAL    | kick back b32-34, Fm9 -> Bb9, rising pluck/
         |            |              | GBP 23,275.20 lands 16.409 (b35.005)   | bell motif b32.75-34 in the gap, snare
         |            |              |                                        | pickup b34.5-34.75, downbeat ON the landing
CALC B   | b35-62     | 16.406-29.063| VO fifty_two_weeks 16.16-24.37,        | groove: kick, claps 2 & 4, hats, shaker,
(groove) |            |              | rates_vary 24.82-28.39; coin wipe      | sub, EP, arp. b44: + bass-pluck bounce, EP
         |            |              | 28.97-29.21 (T_ORB 29.090 = b62.06:    | syncopated, arp pattern B. b52: arp octave
         |            |              | mid-bar -> b62)                        | up, hats 16ths, glass pad. Ebmaj9 Cm9
         |            |              |                                        | Abmaj9 Bb9sus Bb Ebmaj7/G Abmaj9 Fm9 Bb9sus;
         |            |              |                                        | gap motifs b52.25-52.5, b60.75-61.5
ORBIT A  | b62-68     | 29.063-31.875| tag pops b63-67 (+27.5 ms); VO         | drums OUT (the pops are the rhythm): open
(tags)   |            |              | support_household 29.32-31.37          | Abmaj9 -> Gm7, floating arp on the 16ths
         |            |              |                                        | between the pops, offbeat shaker, glass pad
ORBIT B  | b68-76     | 31.875-35.625| VO gap 31.37-35.65; push into the door | reversed swell into b68; THEME (pluck + FM
(theme)  |            |              | 34.47, riser -> air_zoom 35.177        | bell) b68-74.5 over Cm9 Fm9 Bb9sus; groove
         |            |              | (b75.05), heartbeat 35.26 / 36.19      | b68-74.75; drums out b75 (the heartbeat)
LIFT     | b76-84     | 35.625-39.375| T_HEART -> bar line b76; VO            | harmonic + brightness lift: Abmaj9 Bb/Ab
(recogn.)|            |              | recognition 35.65-37.85; light-leak    | Cm9 Fm9 Bb9sus, pad opens, airy pad; full
         |            |              | wipe T_END 38.923 (b83.04)             | groove b78-82.75 (after the heartbeat):
         |            |              |                                        | hats 16ths, bass bounce, arp octave up +
         |            |              |                                        | counter-arp; LIFT motif b81-82.5 (the high
         |            |              |                                        | point Eb6); nothing on b83 (wipe)
END CARD | b84-94.72  | 39.375-44.400| logo sting 39.392 (b84.035), CTA pop   | RESOLVE to Eb (Eb6/9 with the sting's C) as
(bars    |            |              | 40.095, click 40.563; VO discuss       | a soft swell under the sting; no drums; Eb
 21-23)  |            |              | 40.10-42.72                            | pedal: Eb6/9 Ab/Eb Bb/Eb Eb; EP swells,
         |            |              |                                        | thinning 8th arp; ANSWER motif b91.5-92 ->
         |            |              |                                        | Eb6 + glock on b92 (43.125); fade 43.08-
         |            |              |                                        | 44.38, silent after

CHORDS (beat: chord)  0 Ab/Bb | 3 Ebmaj9 | 6 Cm9 | 8 Abmaj9 | 12 Ebmaj7/G | 16 Cm9 | 20 Fm9 | 22 Bb9sus4 |
24 Ebadd9 | 26 Abmaj9 | 28 Bb/Ab | 30 Cm9 | 32 Fm9 | 34 Bb9 | 35 Ebmaj9 | 40 Cm9 | 44 Abmaj9 | 48 Bb9sus4 |
50 Bb | 52 Ebmaj7/G | 56 Abmaj9 | 58 Fm9 | 60 Bb9sus4 | 62 Abmaj9 | 66 Gm7 | 68 Cm9 | 72 Fm9 | 74 Bb9sus4 |
76 Abmaj9 | 78 Bb/Ab | 80 Cm9 | 82 Fm9 | 83 Bb9sus4 | 84 Eb6/9 | 88 Ab/Eb | 90 Bb/Eb | 92 Eb.
Hand voice-led 4-voice upper structures (VOICING), the bass plays the root / slash note (folded to Ab1-G2); the EP
plays the same structure an octave down (no seconds); arps and motifs use chord tones.

SPEECH RULES  No melody while the voice speaks: every motif sits in a VO gap (asserted: >= 80 ms after a line ends,
>= 80 ms before the next starts, no SFX cue >= -12 dB within +-60 ms). Pads / EP / arps / motifs pass a speech-aware
filter (2-pole low-pass 1.7 kHz while a line plays, 15 kHz in the gaps, + a -6 dB peak dip at 2.6 kHz; 60 ms close /
300 ms open); arps -3 dB and claps -4 dB under speech; FX get the dip only. Hero hits: no kick / clap / snare / arp /
motif / EP / shaker / hat onset within +-60 ms of an SFX hero hit, except music downbeats deliberately ON a slam
(SUPPORT: the title slam b3 and "Support" b3.5, the calculator whip b26, the 52-week total b35: kick, sub, EP, pad);
sub notes near a hero hit swell in (50 ms attack); chord changes there are pad swells (hero_audit() logs and measures).

INSTRUMENTS (music_synth)  glassy pad (pad 'warm' 5 voices + 'tri' glass top an octave up, chorus, filter per
section), warm electric piano (fm_epiano), plucky saw arp (pluck_synth 'saw', filter envelope) + counter-arp
(pluck_synth 'square'), FM bell + saw-pluck motif layer (fm_epiano bright tine + pluck_synth), glockenspiel
(end), sub bass (sub_bass), bass pluck (bass_pluck, octave bounce), soft punchy kick (soft_kick), clap (room),
closed hats (hat), shaker (shaker strokes), snare pickup (snare_soft), riser + reverse_swell (hook, theme entry).
Sends: hall (pad + EP), plate (arps, motifs, claps), air (motifs). Kick pump 2.5 dB on the harmonic bus and
3 dB on the sub (the kick owns its transient). High-pass
150-300 Hz on everything except kick and bass; sub / kick mono in the centre; width from detune, chorus, pan and
reverb. Bus: hp 30 Hz, bus_comp -18 / 1.6, tilt +0.8, fade, normalise_lufs -16 LUFS / -1.2 dBTP.

DELIVERY  M.render_bed (VO duck 9 dB 40 / 400 ms, SFX duck 3 dB, gaps 7 LU under the delivered mix, voice >= 10 LU
over the music) -> M.master_withmusic (-14 LUFS, limiter at -2.3, <= -2.0 dBTP) -> MP3s (M.write_mp3) and the
preview (M.make_preview). Outputs: OUT_* / MP3_* / PREVIEW below.
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
import reel2_vo as V              # noqa: E402

# ============================================================================================ constants
SR = A.SR
BPM = 128.0
KEY = 'Eb major'
DUR = 44.4
N = int(round(DUR * SR))                  # 2131200 samples
T = N / SR
G = M.Grid(BPM)
BEAT, BAR, STEP = G.beat_s, G.bar_s, G.step_s
END_BEAT = T / BEAT                       # 94.72
SEED = 2327520
assert abs(V.DUR - DUR) < 1e-9 and abs(V.BPM - BPM) < 1e-9

AUD = A.AUDIO
OUT_CLEAN = os.path.join(AUD, 'reel2_vo_music.wav')
OUT_BED = os.path.join(AUD, 'reel2_vo_music_bed.wav')
OUT_MIX = os.path.join(AUD, 'reel2_vo_withmusic_mix.wav')
REEL = os.path.abspath(os.path.join(HERE, '..', '..', 'reel', 'organic_fostering'))
MP3_BED = os.path.join(REEL, 'organic_fostering_reel2_vo_financial_support_music.mp3')
MP3_CLEAN = os.path.join(REEL, 'organic_fostering_reel2_vo_financial_support_music_clean.mp3')
TITLE = 'Organic Fostering - reel2_vo_financial_support - background music'
SCRATCH = '/tmp/claude-0/-home-user-100/bb73d22e-ad11-5aa0-a0b2-8033920f7c07/scratchpad'
VIDEO_IN = os.path.join(SCRATCH, 'reel2_vo_preview.mp4')
PREVIEW = os.path.join(SCRATCH, 'reel2_vo_music_preview.mp4')

# ============================================================================================ edit timeline
S = V.SRC


def ot(src_t):
    return float(V.out_time(src_t))


EDIT = dict(slam=ot(S.T_TITLE), num=ot(S.T_NUM), land=ot(S.NUM_ROLL[1]), calc=ot(S.T_CALC),
            drag=ot(S.DRAG[0]), total=ot(S.DRAG[1]), orb=ot(S.T_ORB), push=ot(S.ZOOM[0]), heart=ot(S.T_HEART),
            end=ot(S.T_END), logo=ot(S.T_SWAP), btn=ot(S.T_BTN))
VO_LINES = [(c['line'], float(c['start']), float(c['end'])) for c in V.vo_cues()]


def _hit_time(c):
    t = float(c['t'])
    if c.get('align', 'hit') == 'start':
        t += float(A.hit_offset(c['name'], **c.get('params', {})))
    return t


SFX_CUES = sorted((_hit_time(c), float(c.get('gain_db', 0.0)), c['name']) for c in V.cues())
HERO = sorted({round(t, 4) for t, g, _ in SFX_CUES if g >= -6.0})
# the heartbeat cue (n=2 at 64 BPM) has a second 'lub' one period later, and a 'dub' 0.285 s after each lub
_HB = [t for t, g, nm in SFX_CUES if nm == 'heartbeat']
HERO = sorted(set(HERO) | {round(t + 60.0 / 64.0, 4) for t in _HB})
THUMPS = sorted({round(t + k * 60.0 / 64.0 + 0.29 * np.sqrt(62.0 / 64.0), 4) for t in _HB for k in (0, 1)})


def edge_beat(t):
    """Section change for an edit boundary at t: the nearest bar line if within one beat, else the nearest beat."""
    bb = int(round(t / BAR)) * 4
    if abs(t - bb * BEAT) <= BEAT + 1e-9:
        return bb
    return int(round(t / BEAT))


SEC_EDGES = [('hook', 0), ('number', edge_beat(EDIT['num'])), ('calcA', edge_beat(EDIT['calc'])),
             ('drag', edge_beat(EDIT['drag'])), ('calcB', int(round(EDIT['total'] / BEAT))),
             ('orbA', edge_beat(EDIT['orb'])), ('orbB', 68), ('lift', edge_beat(EDIT['heart'])),
             ('end', edge_beat(EDIT['logo']))]
EXPECTED_EDGES = dict(hook=0, number=8, calcA=26, drag=32, calcB=35, orbA=62, orbB=68, lift=76, end=84)
assert {k: v for k, v in SEC_EDGES} == EXPECTED_EDGES, SEC_EDGES        # the docstring map is built on these
assert edge_beat(EDIT['end']) == 84 and abs(EDIT['slam'] - 3 * BEAT) < 1e-3


def section(beat):
    name = SEC_EDGES[0][0]
    for k, b in SEC_EDGES:
        if beat >= b - 1e-9:
            name = k
    return name


# music downbeats deliberately ON a slam (same instant): the title slam, "Support", the whip, the 52-week total.
# Each one's cluster = the hero hits within 40 ms of it (the slot reels' landing tick 37 ms before the title slam).
SUPPORT = (3 * BEAT, 3.5 * BEAT, 26 * BEAT, 35 * BEAT)
for _s in SUPPORT:
    assert min(abs(h - _s) for h in HERO) < 0.004, _s


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


def speaking(t, pre=0.08, post=0.08):
    return any(s - pre <= t <= e + post for _, s, e in VO_LINES)


# ============================================================================================ harmony
# (beat, symbol, upper-structure voicing MIDI); the bass plays the root / slash note
CHART = [
    (0, 'Ab/Bb', [63, 68, 70, 72]), (3, 'Ebmaj9', [65, 67, 70, 74]), (6, 'Cm9', [63, 67, 70, 74]),
    (8, 'Abmaj9', [63, 67, 70, 72]), (12, 'Ebmaj7/G', [62, 67, 70, 75]), (16, 'Cm9', [63, 67, 70, 74]),
    (20, 'Fm9', [63, 65, 68, 72]), (22, 'Bb7sus4', [63, 68, 70, 72]), (24, 'Ebadd9', [65, 67, 70, 75]),
    (26, 'Abmaj9', [63, 67, 70, 72]), (28, 'Bb/Ab', [62, 65, 70, 74]), (30, 'Cm9', [63, 67, 70, 74]),
    (32, 'Fm9', [63, 65, 68, 72]), (34, 'Bb9', [62, 65, 68, 72]), (35, 'Ebmaj9', [63, 67, 70, 74]),
    (40, 'Cm9', [62, 67, 70, 75]), (44, 'Abmaj9', [63, 67, 70, 72]), (48, 'Bb7sus4', [63, 68, 70, 72]),
    (50, 'Bb', [62, 65, 70, 74]), (52, 'Ebmaj7/G', [62, 67, 70, 75]), (56, 'Abmaj9', [63, 67, 70, 72]),
    (58, 'Fm9', [63, 65, 68, 72]), (60, 'Bb7sus4', [63, 68, 70, 72]), (62, 'Abmaj9', [67, 70, 72, 75]),
    (66, 'Gm7', [65, 70, 74, 77]), (68, 'Cm9', [67, 70, 75, 79]), (72, 'Fm9', [68, 72, 75, 79]),
    (74, 'Bb7sus4', [68, 72, 75, 77]), (76, 'Abmaj9', [67, 70, 72, 75]), (78, 'Bb/Ab', [65, 70, 74, 77]),
    (80, 'Cm9', [67, 70, 75, 79]), (82, 'Fm9', [68, 72, 75, 79]), (83, 'Bb7sus4', [68, 72, 75, 77]),
    (84, 'Eb6', [67, 70, 72, 77]), (88, 'Ab/Eb', [68, 70, 72, 75]), (90, 'Bb/Eb', [65, 70, 74, 77]),
    (92, 'Eb', [67, 70, 75, 79]),
]
for _b, _s, _v in CHART:            # every voicing note is a chord tone of its symbol, its 9th, or the slash bass
    _base = _s.split('/')[0]
    _pcs = {n % 12 for n in M.chord(_s)} | {(M.chord(_base)[0] + 2) % 12}
    assert all(n % 12 in _pcs for n in _v), (_s, _v)
VOICING = [v for _, _, v in CHART]


def chord_index(beat):
    i = 0
    for k, (b, _, _) in enumerate(CHART):
        if beat >= b - 1e-9:
            i = k
    return i


def chord_span(i):
    b0 = CHART[i][0]
    b1 = CHART[i + 1][0] if i + 1 < len(CHART) else END_BEAT
    return b0, b1


def next_change(b):
    i = chord_index(b)
    return CHART[i + 1][0] if i + 1 < len(CHART) else END_BEAT


def bass_of(i):
    """Bass MIDI note of chord i folded into Ab1..G2 (32-43: 52-98 Hz)."""
    m = M.bass_note(CHART[i][1], 2)
    while m > 43:
        m -= 12
    while m < 32:
        m += 12
    return m


def ep_voicing(i):
    """EP voicing: the pad structure an octave down (kept >= Bb3), no two notes a 2nd apart (the upper one of a
    2nd moves up an octave)."""
    v = sorted(n - 12 if n - 12 >= 55 else n for n in VOICING[i])
    for _ in range(6):
        bad = [k for k in range(len(v) - 1) if v[k + 1] - v[k] <= 2]
        if not bad:
            break
        k = bad[0]
        v[k + 1] += 12
        v = sorted(set(v))
    return v


# motifs: (beat, MIDI, vel, dur_beats). Every note sits in a VO gap (asserted in layer_motif)
MOTIFS = [
    # gap 1, under the counter roll: rising chord tones of Abmaj9 toward the landing
    (9.0, 72, 0.42, 0.5), (10.0, 75, 0.44, 0.4), (10.5, 79, 0.48, 0.6),
    # gap 2, before the whip: Ebadd9
    (24.5, 75, 0.44, 0.4), (25.0, 79, 0.46, 0.4), (25.5, 82, 0.50, 0.5),
    # gap 3, the drag (Fm9 -> Bb9): rising to the Ab, which the Ebmaj9 on the total resolves
    (32.75, 72, 0.42, 0.25), (33.0, 75, 0.44, 0.4), (33.5, 77, 0.46, 0.4), (34.0, 80, 0.50, 0.6),
    # gap 4 (0.45 s between the 52-week line and the fine print): a two-note answer
    (52.25, 79, 0.40, 0.25), (52.5, 82, 0.44, 0.5),
    # gap 5 (before the coin wipe): falling into the orbit
    (60.75, 84, 0.44, 0.25), (61.0, 82, 0.44, 0.4), (61.5, 77, 0.46, 0.6),
    # THEME (the long gap after "support around your household"): Cm9 -> Fm9 -> Bb9sus4
    (68.0, 79, 0.48, 0.45), (68.5, 82, 0.50, 0.45), (69.0, 84, 0.56, 1.3), (70.5, 82, 0.48, 0.45),
    (71.0, 79, 0.48, 0.45), (71.5, 75, 0.46, 0.45), (72.0, 77, 0.50, 0.45), (72.5, 80, 0.52, 0.45),
    (73.0, 84, 0.56, 0.9), (74.0, 82, 0.52, 1.4),
    # LIFT (after "recognition for a skilled role"): up to the high Eb
    (81.0, 79, 0.48, 0.45), (81.5, 82, 0.50, 0.45), (82.0, 84, 0.54, 0.45), (82.5, 87, 0.58, 0.9),
    # ANSWER on the end card (after the last line): lands on the tonic on bar 23
    (91.5, 82, 0.46, 0.25), (91.75, 84, 0.48, 0.25), (92.0, 87, 0.54, 2.0),
]

EVENTS = []          # (t, kind, gain_db) for the hero-hit audit
# stem trims (dB) applied when the stems are summed (set from the measured stem loudness, see qa: stems_lufs)
TRIM = dict(pad=7.0, ep=4.0, arps=7.0, motif=3.0, sub=-3.0, bass_pluck=5.0, kick=-2.0, clap=7.0, hats=3.0,
            fx=4.0)
# section dynamics (dB, applied after the bus compressor): the hook swells into the slam, the tag ring breathes,
# the lift lifts, the end card settles
SEC_GAIN = [(0.0, -3.0), (3 * BEAT - 0.05, 0.0), (62 * BEAT, 0.0), (62 * BEAT + 0.3, -1.5), (68 * BEAT - 0.5, -1.5),
            (68 * BEAT, 0.0), (76 * BEAT, 0.0), (76 * BEAT + 0.5, 1.0), (84 * BEAT - 0.3, 1.0), (84 * BEAT + 0.5, -0.5)]


def log(t, kind, gain_db):
    EVENTS.append((round(float(t), 4), kind, round(float(gain_db), 1)))


# ============================================================================================ layers
PAD_CUT = dict(hook=900.0, number=1800.0, calcA=1900.0, drag=2000.0, calcB=2100.0, orbA=2400.0, orbB=2500.0,
               lift=3000.0, end=2200.0)
PAD_DB = dict(hook=-14.0, number=-15.0, calcA=-14.5, drag=-14.5, calcB=-15.0, orbA=-13.5, orbB=-14.0,
              lift=-13.5, end=-13.5)
GLASS_SECS = ('orbA', 'orbB', 'lift', 'end')


def layer_pad():
    pad, glass = M.Track(T, 'pad'), M.Track(T, 'glass')
    for i in range(len(CHART)):
        b0, b1 = chord_span(i)
        t0, t1 = b0 * BEAT, b1 * BEAT
        sec = section(b0)
        last = i == len(CHART) - 1
        dur = (t1 - t0 - 0.08) if not last else (T - t0 - 0.3)
        if b0 == 0:
            att, cut, open_to = 0.9, 700.0, 2200.0          # the hook swell: opens into the slam
        else:
            att = 0.03 if b0 == 3 else (0.06 if b0 in (26, 35) else 0.25)
            cut, open_to = PAD_CUT[sec], (PAD_CUT[sec] * 1.5 if sec in ('lift', 'orbB') else None)
        x = M.pad(VOICING[i], dur=dur, vel=0.6, wave='warm', voices=5, detune=12.0, attack=att,
                  release=0.5 if not last else 1.2, cutoff=cut, q=0.7, sweep=0.2, sweep_rate=0.07,
                  open_to=open_to, chorus_mix=0.3, width=0.85, seed=SEED + i)
        pad.add(A.hp(x, 150.0, 2), t0, gain_db=PAD_DB[sec])
        if sec in GLASS_SECS or (b0 < 52 < b1) or (52 <= b0 < 62):
            ts = max(t0, 52 * BEAT)
            top = [n + 12 for n in VOICING[i][-2:]]
            d2 = (t1 - ts - 0.08) if not last else (T - ts - 0.35)
            y = M.pad(top, dur=d2, vel=0.5, wave='tri', voices=4, detune=9.0, attack=0.35, release=0.6 if not last
                      else 1.2, cutoff=5000.0 if sec != 'lift' else 6500.0, chorus_mix=0.45, width=1.0,
                      seed=SEED + 100 + i)
            gdb = dict(calcB=-27.0, orbA=-24.0, orbB=-24.5, lift=-23.0, end=-24.5)[sec]
            glass.add(A.hp(y, 350.0, 2), ts, gain_db=gdb)
    return pad.buf, glass.buf


def layer_ep():
    """Warm FM electric piano, octave 3-4. Pattern P1 = 1, and-of-2, (3 short); P2 = 1, and-of-1 (short),
    and-of-2, and-of-3 (more syncopated: CALC B2 and the lift). Long chords on the slam, Cm9 (hook), the whip and
    the drag; swells on the end card. A chord never rings over the next change."""
    tr = M.Track(T, 'ep')
    rng = np.random.default_rng(SEED + 1)
    hits = [(3.0, 2.9, 0.50, True), (6.0, 1.9, 0.40, False), (26.0, 1.9, 0.46, True), (32.0, 1.9, 0.44, False),
            (34.0, 0.9, 0.46, False), (35.0, 0.9, 0.50, True), (78.0, 0.4, 0.50, False), (85.0, 2.8, 0.36, False), (88.0, 1.9, 0.36, False),
            (90.0, 1.9, 0.34, False)]
    P1 = [(0.0, 1.0, 0.46), (1.5, 0.8, 0.40), (3.0, 0.4, 0.34)]
    P2 = [(0.0, 0.4, 0.46), (0.5, 0.4, 0.36), (1.5, 0.8, 0.42), (2.5, 0.8, 0.40)]
    for bar in range(int(np.ceil(END_BEAT / 4))):
        bb = bar * 4
        for q, dl, vel in (P2 if (44 <= bb < 52 or bb >= 76) else P1):
            b = bb + q
            sec = section(b)
            if sec in ('number', 'calcB', 'orbB', 'lift') and not (sec == 'lift' and b < 78) \
                    and not (sec == 'orbB' and b >= 74.5) and not (sec == 'lift' and b >= 83):
                if sec == 'calcB' and b < 36:
                    continue
                hits.append((b, dl, vel + (0.04 if sec == 'lift' else 0.0), False))
    for j, (b, dl, vel, sup) in enumerate(sorted(hits)):
        t = b * BEAT
        i = chord_index(b)
        dl = min(dl, next_change(b) - b - 0.06)
        if near_hero(t, support_ok=sup):
            continue
        g = -15.0
        notes = ep_voicing(i)
        for k, n in enumerate(notes):
            x = M.fm_epiano(n, dur=dl * BEAT, vel=vel + 0.03 * (k == len(notes) - 1), release=0.35, bright=0.85,
                            tine=0.7, detune=0.5, seed=SEED + j * 7 + k)
            off = 0.0015 * k + rng.uniform(-0.0015, 0.0015)          # gentle spread, <= 6 ms
            tr.add(A.hp(x, 160.0, 2), t + off, gain_db=g, pan=-0.2)
        log(t, 'ep_sup' if sup else 'ep', g)
    return tr.buf


ARP = dict(
    A=[0, 2, 1, 3, 2, 4, 3, 1, 0, 2, 1, 3, 2, 4, 3, 5],                  # 16ths, rolling
    B=[0, 3, 1, 4, 2, 5, 1, 3, 0, 4, 2, 5, 3, 1, 4, 2],                  # 16ths, wider
    hook=[0, 1, 2, 3, 4, 3, 2, 1],                                       # 8ths
    float=[None, 3, 4, 5, None, 4, 2, 3, None, 2, 4, 5, None, 3, 1, 4],   # 16ths, no downbeats (the tag pops)
    counter=[None, 5, None, 4, None, 3, None, 4],                        # off-beat 8ths
)


def _pool(i):
    v = VOICING[i][:4]
    return v + [v[0] + 12, v[1] + 12]


def layer_arps():
    arp, cnt = M.Track(T, 'arp'), M.Track(T, 'counter')
    n16 = int(END_BEAT * 4)
    for k in range(n16):
        b = k / 4.0
        t = k * STEP
        sec = section(b)
        i = chord_index(b)
        pool = _pool(i)
        acc = 0.64 if k % 4 == 0 else (0.54 if k % 2 == 0 else 0.46)
        p, oct_, gdb, cut = None, 0, -18.0, 900.0
        if sec == 'hook' and b >= 4.5 and k % 2 == 0:
            p, gdb, cut = ARP['hook'][(k // 2) % 8], -20.0, 750.0
        elif sec == 'number':
            p, gdb = ARP['A'][k % 16], -19.0 + (0.5 if b >= 16 else 0.0)
        elif sec == 'calcA' and k % 4 == 2:
            p, gdb = ARP['hook'][(k // 2) % 8], -19.0
        elif sec == 'calcB' and b >= 36:
            if b < 44:
                p, gdb = ARP['A'][k % 16], -19.0
            elif b < 52:
                p, gdb, cut = ARP['B'][k % 16], -19.0, 1000.0
            elif b < 60.5:
                p, oct_, gdb, cut = ARP['B'][k % 16], 1, -21.0, 1100.0
        elif sec == 'orbA':
            p, oct_, gdb, cut = ARP['float'][k % 16], 1, -21.0, 1200.0
        elif sec == 'orbB' and b < 74.75:
            p, gdb, cut = ARP['A'][k % 16], -19.5, 1000.0
        elif sec == 'lift':
            p, oct_, gdb, cut = ARP['B'][(k + 8) % 16], 1, -20.5, 1300.0
            if b >= 82.75:
                p = None
        elif sec == 'end' and k % 4 == 0 and b < 90:
            p, oct_, gdb, cut = ARP['hook'][(k // 4) % 8], 1, -21.0 - 0.6 * (b - 84), 1000.0
        if p is not None and not near_hero(t):
            x = M.pluck_synth(pool[p] + 12 * oct_, dur=STEP * 0.8, vel=acc, cutoff=cut, env_oct=2.6, decay=0.07,
                              amp_decay=0.22, q=1.15, wave='saw', detune=6.0, release=0.06, seed=SEED + k)
            arp.add(A.hp(x, 220.0, 2), t, gain_db=gdb, pan=0.3 if k % 2 else -0.3)
            log(t, 'arp', gdb)
        # counter-arp (off-beat 8ths, square pluck): the lift groove
        if sec == 'lift' and 78 <= b < 82.75 and k % 2 == 0:
            cp = ARP['counter'][(k // 2) % 8]
            if cp is not None and not near_hero(t):
                x = M.pluck_synth(pool[cp] + 12, dur=STEP * 0.9, vel=0.5, cutoff=1400.0, env_oct=2.0, decay=0.05,
                                  amp_decay=0.16, q=1.0, wave='square', detune=6.0, release=0.05,
                                  seed=SEED + 3000 + k)
                cnt.add(A.hp(x, 300.0, 2), t, gain_db=-23.0, pan=0.5)
                log(t, 'arp', -23.0)
    return arp.buf, cnt.buf


def layer_motif():
    tr, glk = M.Track(T, 'motif'), M.Track(T, 'glock')
    for j, (b, m, vel, dl) in enumerate(MOTIFS):
        t = b * BEAT
        assert not near_hero(t), ('motif near a hero hit', b, t)
        assert not speaking(t), ('motif under speech', b, t)
        assert not any(abs(t - c) < 0.06 and g >= -12.0 for c, g, _ in SFX_CUES), ('motif on an SFX cue', b, t)
        x = M.fm_epiano(m, dur=dl * BEAT, vel=vel, release=0.5, bright=1.25, tine=1.5, detune=1.0,
                        seed=SEED + 7000 + j)
        y = M.pluck_synth(m, dur=min(dl * BEAT, 0.3), vel=vel, cutoff=1400.0, env_oct=2.4, decay=0.09,
                          amp_decay=0.3, q=1.1, wave='saw', detune=8.0, release=0.1, seed=SEED + 7100 + j)
        tr.add(A.hp(x, 250.0, 2), t, gain_db=-13.0, pan=0.12)
        tr.add(A.hp(y, 300.0, 2), t, gain_db=-19.0, pan=-0.15)
        log(t, 'motif', -13.0)
    for b, m in ((92.0, 99),):                      # glock sparkle on the final tonic
        t = b * BEAT
        assert not near_hero(t) and not speaking(t)
        g = M.glockenspiel(m, vel=0.4, hardness=0.4, decay=0.8, seed=SEED + 9)
        glk.add(A.hp(g, 400.0, 2), t, gain_db=-24.0, pan=0.2)
        log(t, 'glock', -24.0)
    return tr.buf, glk.buf


GROOVE_BASS = ('number', 'calcB', 'orbB', 'lift')


def layer_bass():
    sub, bp = M.Track(T, 'sub'), M.Track(T, 'bpluck')
    hits = []                                       # (beat, dur_beats, vel, support)
    hits += [(3.0, 2.85, 0.80, True), (6.0, 1.9, 0.72, False)]                   # hook: from the slam
    for bar in range(2, int(np.ceil(END_BEAT / 4))):
        bb = bar * 4
        for q, dl, vel in ((0.0, 1.6, 0.78), (2.5, 1.3, 0.68)):
            b = bb + q
            sec = section(b)
            if sec in GROOVE_BASS and not (sec == 'calcB' and b < 36) and not (sec == 'orbB' and b >= 74.5) \
                    and not (sec == 'lift' and (b < 78 or b >= 83)):
                hits.append((b, min(dl, next_change(b) - b - 0.05), vel, False))
    # held notes: calc A (one per chord), drag (Fm9, Bb9, the total), orbit A, the lift entry, end card
    for b in (26.0, 28.0, 30.0, 32.0, 34.0, 35.0, 62.0, 66.0, 76.0, 83.0, 84.0, 88.0, 90.0, 92.0):
        i = chord_index(b)
        b1 = next_change(b)
        last = b >= 92
        dl = (END_BEAT - b - 0.9) if last else (b1 - b - 0.08)
        hits.append((b, dl, 0.74 if b < 84 else 0.68, b in (26.0, 35.0)))
    hits.sort()
    for b, dl, vel, sup in hits:
        t = b * BEAT
        i = chord_index(b)
        soft = near_hero(t, support_ok=sup) or any(abs(t - h) < 0.06 for h in THUMPS)
        att = 0.05 if soft else 0.008                # near a hero hit: a slow swell, no onset
        x = M.sub_bass(bass_of(i), dur=dl * BEAT, vel=vel, drive=1.5, harm=0.14, attack=att, release=0.09)
        sub.add(x, t, gain_db=-8.0)
        log(t, 'sub_swell' if soft else ('sub_sup' if sup else 'sub'), -8.0)
    # bass pluck octave bounce (off-beat 8ths): calc B from b44, the lift groove
    for k in range(int(END_BEAT * 2)):
        b = k / 2.0
        if k % 2 == 0:
            continue
        sec = section(b)
        if (sec == 'calcB' and 44 <= b < 60.5) or (sec == 'lift' and 78 <= b < 82.75):
            t = b * BEAT
            if near_hero(t):
                continue
            i = chord_index(b)
            x = M.bass_pluck(bass_of(i) + 12, dur=0.16, vel=0.55, cutoff=420.0, env_oct=2.2, decay=0.07, sub=0.4,
                             seed=SEED + k)
            bp.add(x, t, gain_db=-18.0)
            log(t, 'bass', -18.0)
    return sub.buf, bp.buf


def kick_beats():
    out = [3.0, 3.5]
    for b in range(int(np.ceil(END_BEAT))):
        sec = section(b)
        if sec == 'number' or (sec == 'calcB' and b <= 61) or (sec == 'orbB' and b <= 74) \
                or (sec == 'lift' and 78 <= b <= 82):
            out.append(float(b))
    out += [26.0, 32.0, 33.0, 34.0]
    return sorted(set(out))


def layer_drums():
    kick, clap, hats = M.Track(T, 'kick'), M.Track(T, 'clap'), M.Track(T, 'hats')
    rng = np.random.default_rng(SEED + 2)
    kick_times = []
    for b in kick_beats():
        t = b * BEAT
        sup = any(abs(t - s) < 0.004 for s in SUPPORT)
        if near_hero(t, support_ok=sup) or any(abs(t - h) < 0.06 for h in THUMPS):
            continue
        sec = section(b)
        vel = 0.84 if int(b) % 2 == 0 else 0.76
        if sup:
            vel = 0.9 if b != 3.5 else 0.78
        if sec == 'lift':
            vel += 0.04
        x = M.soft_kick(vel=vel, punch=0.6, tone=50.0, decay=0.27, click=0.3, drive=1.4)
        kick.add(x, t, gain_db=-5.0)
        kick_times.append(t)
        log(t, 'kick_sup' if sup else 'kick', -5.0)
    # claps on 2 and 4 (beat % 4 in (1, 3)): number from b16, calc B, orbit B, the lift groove
    for b in range(int(np.ceil(END_BEAT))):
        sec = section(b)
        if b % 4 not in (1, 3):
            continue
        if (sec == 'number' and b >= 16) or (sec == 'calcB' and 37 <= b <= 59) or (sec == 'orbB' and b <= 73) \
                or (sec == 'lift' and 79 <= b <= 81):
            t = b * BEAT
            if near_hero(t):
                continue
            g = -15.0 - (4.0 if speaking(t, 0.05, 0.1) else 0.0)
            c = M.clap(vel=0.62, tone=1200.0, room='room', wet_db=-8.0, seed=b % 4)
            clap.add(A.hp(c, 220.0, 2), t - 0.03, gain_db=g)
            log(t, 'clap', g)
    # snare pickup into the 52-week total
    for b, vel in ((34.5, 0.42), (34.75, 0.52)):
        t = b * BEAT
        if not near_hero(t):
            x = M.snare_soft(vel=vel, tone=190.0, snappy=0.45, decay=0.12, seed=int(b * 4))
            clap.add(A.hp(x, 180.0, 2), t, gain_db=-17.0, pan=0.05)
            log(t, 'snare', -17.0)
    # closed hats (off-beat 8ths; 16ths from b52 and in the lift) + shaker strokes (16ths; peak on the 16th)
    acc = (1.0, 0.45, 0.75, 0.5)
    for k in range(int(END_BEAT * 4)):
        b = k / 4.0
        sec = section(b)
        t = k * STEP
        if near_hero(t):
            continue
        hv = None
        if k % 4 == 2 and (sec == 'number' or (sec == 'calcB' and b >= 36) or (sec == 'orbB' and b < 75)):
            hv, hg = 0.6, -19.0
        elif sec == 'calcB' and 52 <= b < 60.5 and k % 4 != 2:
            hv, hg = 0.4, -24.0
        elif sec == 'lift' and 78 <= b < 82.75:
            hv, hg = (0.6, -19.0) if k % 4 == 2 else (0.42, -23.5)
        if hv is not None:
            h = M.hat(vel=hv, open=False, tone=1.05, seed=k % 8)
            hats.add(A.hp(h, 500.0, 2), t + rng.uniform(-0.002, 0.002), gain_db=hg, pan=0.2)
            log(t, 'hat', hg)
        sv = None
        if sec == 'hook' and b >= 6 and k % 2 == 0:
            sv, sg = 0.5, -25.0 + 1.0 * (b - 6)
        elif sec == 'number' and b >= 16:
            sv, sg = 0.55, -22.0
        elif sec == 'calcA' and k % 4 != 0:
            sv, sg = 0.5, -23.0
        elif sec in ('drag', 'calcB') and b < 61:
            sv, sg = 0.55, -22.0
        elif sec == 'orbA' and k % 4 == 2:
            sv, sg = 0.5, -23.0
        elif sec == 'orbB' and b < 74.75:
            sv, sg = 0.55, -22.0
        elif sec == 'lift' and 78 <= b < 82.75:
            sv, sg = 0.55, -21.5
        if sv is not None:
            x = M.shaker(vel=sv * acc[k % 4], length=0.06, tone=7600.0, attack=0.012, seed=k % 16)
            hats.add(x, t - 0.012 + rng.uniform(-0.002, 0.002), gain_db=sg, pan=-0.25 if k % 2 else -0.12)
    return kick.buf, clap.buf, hats.buf, kick_times


def layer_fx():
    fx = M.Track(T, 'fx')
    slam = 3 * BEAT
    # the short riser + a reversed Ebmaj9 swell, both ENDING on the title slam (b3, 1.406)
    fx.add(A.hp(M.riser(2 * BEAT, vel=0.55, f_start=350.0, f_end=5000.0, seed=SEED), 250.0, 2), slam - 2 * BEAT,
           gain_db=-21.0)
    fx.add(A.hp(M.reverse_swell(2 * BEAT, vel=0.5, notes=VOICING[1], bright=0.8, seed=SEED + 1), 200.0, 2),
           slam - 2 * BEAT, gain_db=-22.0)
    # a reversed Cm9 swell into the theme (b68, 31.875: no SFX hit near)
    t68 = 68 * BEAT
    assert not near_hero(t68)
    fx.add(A.hp(M.reverse_swell(2 * BEAT, vel=0.5, notes=VOICING[chord_index(68)], bright=0.9, seed=SEED + 2),
                200.0, 2), t68 - 2 * BEAT, gain_db=-23.0)
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


SPEECH_LP = (1700.0, 15000.0)      # low-pass cutoff under speech / in the gaps
SPEECH_DIP = (2600.0, 0.8, -6.0)   # + a peaking dip under speech (Hz, Q, dB)


def speech_dip(x, s):
    f, q, g = SPEECH_DIP
    return x + s[:, None] * (A.eq(x, 'peak', f, q, g) - x)


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
    pad, glass = (y * u('pad') for y in layer_pad())
    ep = layer_ep() * u('ep')
    arp, cnt = (y * u('arps') for y in layer_arps())
    motif, glock = (y * u('motif') for y in layer_motif())
    sub, bpl = layer_bass()
    sub, bpl = sub * u('sub'), bpl * u('bass_pluck')
    kick, clap, hats, kick_times = layer_drums()
    kick, clap, hats = kick * u('kick'), clap * u('clap'), hats * u('hats')
    fx = layer_fx() * u('fx')
    sp = speech_env(N)
    harm = speech_carve(M.pump(pad + glass + ep, kick_times, depth_db=2.5, attack=0.004, release=0.2), sp)
    ar_f = speech_carve(M.pump(arp + cnt, kick_times, depth_db=2.5, attack=0.004, release=0.2), sp)
    ar_f *= A.undb(-3.0 * sp)[:, None]                   # the arps also sit 3 dB lower under speech
    mot_f = speech_carve(motif + glock, sp)
    clap_f = speech_dip(clap, sp)
    fx_f = speech_dip(fx, sp)
    sends = (M.reverb_send(harm, 'hall', wet_db=-16.0, hp_hz=250.0)
             + M.reverb_send(ar_f + clap_f, 'plate', wet_db=-16.0, hp_hz=300.0)
             + M.reverb_send(mot_f, 'plate', wet_db=-13.0, hp_hz=300.0)
             + M.reverb_send(mot_f, 'air', wet_db=-15.0, hp_hz=500.0))
    low = M.pump(A.lp(sub, 400.0, 2), kick_times, depth_db=3.0, attack=0.003, release=0.12) + bpl   # sub ducks the kick
    mix = harm + ar_f + mot_f + low + kick + clap_f + hats + fx_f + sends
    mix = A.hp(mix, 30.0, 2)
    mix = M.bus_comp(mix, thresh_db=-18.0, ratio=1.6, attack=0.012, release=0.2)
    mix = M.tilt_eq(mix, 0.8)
    mix = M.gain_ramp(mix, SEC_GAIN)
    mix = M.fade_out(mix, 1.3, end=T - 0.02)             # fade 43.08-44.38, silence in the last 20 ms
    mix, info = M.normalise_lufs(mix, target=-16.0, tp_ceiling=-1.2)
    mix[int(round((T - 0.02) * SR)):] = 0.0
    stems = dict(pad=pad + glass, ep=ep, arps=arp + cnt, motif=motif + glock, sub=sub, bass_pluck=bpl,
                 kick=kick, clap=clap, hats=hats, fx=fx, sends=sends)
    PARTS.clear()
    PARTS.update(harm=harm, arps=ar_f, motif=mot_f, low=low, kick=kick, clap=clap_f, hats=hats, fx=fx_f,
                 sends=sends)
    if verbose:
        print('render: %.1f s, normalise %s' % (time.time() - t0, info))
    return mix, stems, info


# ============================================================================================ QA
def band_db(x, lo=1000.0, hi=4000.0, win=0.1):
    """Per-window energy (dB) of the 1-4 kHz band of a stereo signal (mono sum), 100 ms windows."""
    y = A.bp(A._st(x).mean(1), lo, hi, 2)
    w = int(win * SR)
    m = len(y) // w
    e = (y[:m * w] ** 2).reshape(m, w).mean(1)
    return 10 * np.log10(e + 1e-20)


def hero_audit(clean):
    """Music transients near the SFX hero hits. (1) Event log: arrangement onsets within +-60 ms of a hero hit
    that are not on a SUPPORT instant (should be none, apart from pad / sub swells). (2) Measurement on the clean
    music, high-passed at 150 Hz, 8 ms RMS: onset rise = the level jump over 10 ms. Per hero hit (outside the
    support clusters): the largest rise inside +-60 ms and the level there, relative to the median kick onset."""
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

    kicks = [e[0] for e in EVENTS if e[1] == 'kick']
    ob = np.array([onset(t - 0.01, t + 0.03) for t in kicks])
    r_ref, l_ref = float(np.median(ob[:, 0])), float(np.median(ob[:, 1]))
    rows = []
    for h in HERO:
        if any(abs(h - s) <= 0.04 for s in SUPPORT):
            continue
        r, lv = onset(h - 0.06, h + 0.06)
        rows.append((h, round(r - r_ref, 1), round(lv - l_ref, 1)))
    rows.sort(key=lambda r: -(r[1] + r[2]))
    typ = np.array([onset(t - 0.06, t + 0.06) for t in np.arange(4.03, 28.0, 0.137)
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


def qa(clean, bed, bedm, mix, rep, stems):
    out = {}
    q = M.qa(clean)
    tail = float(A.db(np.max(np.abs(clean[-int(0.02 * SR):])) + 1e-12))
    out['clean'] = dict(samples=len(clean), dur=round(len(clean) / SR, 5), lufs=q['lufs'], true_peak=q['true_peak'],
                        peak_dbfs=q['peak_dbfs'], clip=q['clip'], last20ms_dbfs=round(tail, 1),
                        dc=q['dcrep']['dc'], sub20_db=q['dcrep']['sub20_db'], sub40_db=q['dcrep']['sub40_db'],
                        low60_pct=q['dcrep']['low60_pct'], clicks=q['clicks']['count'],
                        click_events=q['clicks']['events'][:3], lra=round(A.loudness_range(clean), 2))
    lo = A.lp(clean, 120.0, 4)
    mid, side = lo.mean(1), 0.5 * (lo[:, 0] - lo[:, 1])
    out['clean']['low120_side_minus_mid_db'] = round(float(10 * np.log10((side ** 2).sum() / (mid ** 2).sum()
                                                                         + 1e-20)), 1)
    out['clean']['corr_LR'] = round(float(np.corrcoef(clean[:, 0], clean[:, 1])[0, 1]), 3)
    # section loudness (short-term 3 s median per section) of the clean music
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
    out['stems_lufs'] = {k: round(A.loudness(v), 1) for k, v in stems.items() if np.any(v)}
    out['bed'] = dict(bedm, lufs=round(A.loudness(bed), 2), true_peak=round(A.true_peak(bed), 2), samples=len(bed),
                      last20ms_dbfs=round(float(A.db(np.max(np.abs(bed[-int(0.02 * SR):])) + 1e-12)), 1))
    out['withmusic'] = {k: v for k, v in rep.items() if k != 'stems'}
    out['withmusic']['samples'] = len(mix)
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
    # gaps: music short-term loudness vs the delivered mix (bed laid at 0 dB under reel2_vo_mix.wav)
    out['hero'] = hero_audit(clean)
    return out


# ============================================================================================ main
def main():
    t0 = time.time()
    print('edit (output s):', {k: round(v, 3) for k, v in EDIT.items()})
    print('sections (beat -> s):', [(k, b, round(b * BEAT, 3)) for k, b in SEC_EDGES])
    clean, stems, info = render()
    assert len(clean) == N
    A._write_wav(OUT_CLEAN, clean, 24)
    st = M.load_reel_stems('reel2')
    assert st['n'] == N, st['n']
    bed, bedm = M.render_bed(clean, st['vo'], st['sfx'], st['mix'], gap_lu=7.0, min_vo_lu=10.0, vo_duck_db=9.0,
                             vo_attack=0.04, vo_release=0.4, sfx_duck_db=3.0, sfx_attack=0.01, sfx_release=0.25)
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
    rpt = qa(clean, bed, bedm, mix, rep, stems)
    rpt['mp3'] = []
    for p in (MP3_BED, MP3_CLEAN):
        pr = ffprobe(p)
        s0 = pr['streams'][0]
        rpt['mp3'].append(dict(path=p, codec=s0.get('codec_name'), bit_rate=int(s0.get('bit_rate', 0)),
                               sample_rate=int(s0.get('sample_rate', 0)), channels=s0.get('channels'),
                               dur=round(float(pr['format']['duration']), 3),
                               title=pr['format'].get('tags', {}).get('title')))
    if prev:
        pr = ffprobe(prev)
        rpt['preview'] = dict(path=prev, size_mb=round(os.path.getsize(prev) / 1e6, 2),
                              dur=round(float(pr['format']['duration']), 3),
                              streams=[(s['codec_type'], s['codec_name'], s.get('sample_rate'), s.get('bit_rate'))
                                       for s in pr['streams']])
    rpt['render_s'] = round(time.time() - t0, 1)
    print(json.dumps(rpt, indent=1, default=str))
    return rpt


if __name__ == '__main__':
    main()
