"""anim4_vo_music.py: original background music for ANIM 4 VO "£447.60: where does it go?" (Organic Fostering).

    cd pipeline/fostering && nice -n 5 python3 anim4_vo_music.py      (deterministic, seeded; ~1-2 min)

Synthesised from scratch with music_synth.py + audio.py (numpy / scipy only: no samples, no downloads, no AI).
Mood: bright, optimistic, modern, clear, trustworthy, curious (clean light SaaS look, gold coins on a ribbon).

KEY      D major, with D Lydian colour (E/D = the II-over-I "question" chord, G#).
TEMPO    120 BPM, 4/4. Beat n = n * 0.5 s from 0.000 (beat 1 = 0.000 s), bar = 2.0 s. 25.63 bars: bars 0-25,
         bar 25 cut at 51.267. Every rhythmic event is on the 16th grid (shaker swing 3.75 ms + humanise 3 ms,
         EP chord spread <= 6.5 ms: all within +-8 ms). Length: the clean music is exactly
         round(51.2667 * 48000) = 2460802 samples (the video length); the bed / with-music mix match the VO stem
         (2460816 samples).
EDIT     Section boundaries are computed in OUTPUT time from anim4_vo (V.out_time on the anim4.py constants,
         V.vo_cues(), V.cues() hero hits = gain_db >= -6). A boundary within one beat of a bar line moves to
         that bar line, otherwise to the nearest beat (boundary_beat()).

MUSIC MAP (output time; b = beat index from 0.000 s, bar = b // 4)
section    | beats     | t0-t1 s     | edit events (anim4_vo)                | music events
-----------|-----------|-------------|---------------------------------------|------------------------------------------
HOOK A     | b0-8      | 0.00-4.00   | 0.000 "£447.60" slam (coins burst,    | downbeat ON the slam: Dmaj9 pad (fast
           |           |             | impact); 0.50 "per week"; VO amount   | attack), EP chord, sub D; Bm9 in bar 1;
           |           |             | 0.35-3.63                             | glassy pluck 8ths (rising, speech-
           |           |             |                                       | filtered); no drums
HOOK B     | b8-14     | 4.00-7.00   | 3.767 "?" pop, 4.267 chip burst; VO   | E/D (D Lydian, unresolved) held through
           |           |             | where 3.91-5.10; 6.267 snap (number   | the snap and the break; shaker 8ths creep
           |           |             | re-forms), 6.767 BREAK (coins burst)  | in; QUESTION motif in the gap: FM bell
           |           |             | = the anim4 section edge B6: mid-bar  | E5-F#5-G#5 (5.25 / 5.50 / 5.75, ends on
           |           |             | -> b14                                | the #4); reverse swell into 7.0
JOURNEY    | b14-26    | 7.00-13.00  | coins pulled into the ribbon; VO      | groove drops on 7.0 with the D chord:
           |           |             | payments_help 7.07-10.90; move to     | soft four-on-the-floor kick, shaker
           |           |             | home 11.74                            | 16ths, sub (1 + and-of-3), EP stabs,
           |           |             |                                       | glassy 16th arp, pad. Dadd9, A/C#, Bm9,
           |           |             |                                       | Gmaj9; motif 11.0-11.5
HOME       | b26-34    | 13.00-17.00 | house pop 12.267, arrive 12.777 (mid- | + claps on 2 & 4 (sparingly). D/F#, Em9;
           |           |             | bar -> b26); VO home 13.19-15.06      | motif 15.25-15.50
FOOD       | b34-44    | 17.00-22.00 | arrive 17.011 (clinks 16.951); VO     | SWAP the arp: glassy pluck -> FM bell arp
           |           |             | food 17.52-19.45                      | (octave up). Gmaj9, Asus4-A; motif
           |           |             |                                       | 20.0-20.5
CLOTHES    | b44-54    | 22.00-27.00 | arrive 21.516 (clinks 21.452) -> bar  | claps out, + bass pluck off-beat 8ths
           |           |             | line b44; VO clothes 22.11-25.03      | (octave bounce). Bm9, Gmaj9, D/F#; motif
           |           |             |                                       | 26.0-26.25
TRAVEL     | b54-65    | 27.00-32.50 | arrive 27.016 (clinks 26.952); VO     | + glassy counter-arp (off-beat 8ths,
           |           |             | travel 27.61-30.34                    | panned). E/G# (Lydian lift), Asus4-A;
           |           |             |                                       | motif 30.5-31.5 (the sus resolves)
CHILD      | b65-72    | 32.50-36.00 | child pop 32.125, stream 32.511,      | bass bounce + counter-arp out, + airy
           |           |             | gather 32.971; VO everyday_life       | high pad, FM bell arp in 8ths. Bm9, Em9;
           |           |             | 33.02-35.41                           | motif 35.5-35.75
BREAKDOWN  | b72-75    | 36.00-37.50 | shrink / fade 36.256-36.967; FINAL    | drums out; Asus4 pad over an A pedal;
           |           |             | NUMBER slam 37.267 (mid-bar -> b75)   | riser + reversed G-chord swell peaking at
           |           |             |                                       | 37.25, into the slam
FINAL LIFT | b75-88    | 37.50-44.00 | VO final_amount 37.62-43.87           | fullest texture under the voice: kick,
           |           |             | (statement 37.767)                    | claps 2 & 4 (from b76), shaker, sub +
           |           |             |                                       | bass bounce, EP, both arps, airy + open
           |           |             |                                       | pad. Gmaj9, F#m7, Em9 A7sus4 (IV-iii-
           |           |             |                                       | ii-V)
END CARD   | b88-102.5 | 44.00-51.27 | logo 44.267, pop 44.767, chime        | RESOLVE to Dmaj9 on 44.0 (bells D5 + F#5,
           |           |             | 44.892; VO 44.57-46.68 and            | glock); drums out (shaker 8ths fade in
           |           |             | 46.98-49.65                           | bar 22); D pedal: Dmaj9, Gmaj7/D, E/D,
           |           |             |                                       | Dadd9; ANSWER motif E5-F#5-A5-D6
           |           |             |                                       | (49.75-50.50) resolves the question; fade
           |           |             |                                       | 49.847-51.247, silent after

CHORDS (beat: chord)  0 Dmaj9 | 4 Bm9 | 8 E/D | 14 Dadd9 | 16 A/C# | 20 Bm9 | 24 Gmaj9 | 28 D/F# | 32 Em9 |
36 Gmaj9 | 40 Asus4 | 42 A | 44 Bm9 | 48 Gmaj9 | 52 D/F# | 56 E/G# | 60 Asus4 | 62 A | 64 Bm9 | 68 Em9 |
72 Asus4 | 75 Gmaj9 | 80 F#m7 | 84 Em9 | 86 A7sus4 | 88 Dmaj9 | 92 Gmaj7/D | 96 E/D | 100 Dadd9.
Bass line: D B D | D C# B G F# E G A | B G F# G# A | B E A | G F# E A | D pedal. Hand voice-led 4-5 voice upper
structures (PADV); EP = the same an octave down, opened so no 2nds (ep_voicing); arps / motifs use chord tones.

SPEECH RULES  No melody while the voice speaks: the bell motifs sit only in the VO gaps, between the gap's SFX (no
SFX cue >= -12 dB within +-60 ms of a motif note). The pads / EP / arps / motifs run through a speech-aware filter
(speech_carve: 2-pole low-pass at 1.7 kHz while a VO line plays, 15 kHz in the gaps, plus a -6 dB peaking dip at 2.6
kHz under speech; 60 ms close / 300 ms open); the arps drop 3 dB and the claps 4 dB under speech. Hero hits: no kick
/ clap / motif onset within +-60 ms of an SFX hero hit (gain >= -6); the only same-instant support is the music's
first downbeat on the 0.000 slam. Near a hero hit kicks become -15 dB ghosts, claps are dropped, arp / bass-pluck
notes drop 12 dB, EP stabs and shaker strokes 9 dB, and a sub note there swells in (50 ms attack) (event log +
transient measurement in hero_audit()).

INSTRUMENTS (music_synth)  airy pad (pad 'warm' 5 voices, chorus, slow filter sweep; + 'tri' airy high pad from
the child on), soft electric piano chords (fm_epiano, octave 3), glassy pluck arp (pluck_synth 'square'), FM bell
arp (fm_epiano octave 5, bright tine), FM bell + hand bell motifs (fm_epiano + bell 'hand'), glockenspiel sparkle
(end card), sub bass (sub_bass), bass pluck (bass_pluck, octave bounce), soft kick (soft_kick), clap (clap,
room), shaker 16ths (shaker strokes), riser + reverse_swell (breakdown, hook). Sends: hall (pad + EP), plate
(arps, motifs, claps), air (motifs). Gentle kick pump (pump 2.5 dB) on the harmonic bus. High-pass 150-300 Hz on
everything except kick and bass; sub / kick mono in the centre. Bus: hp 30 Hz, bus_comp -18 / 1.6, tilt +0.8,
fade, normalise_lufs -16 LUFS / -1.2 dBTP.

DELIVERY  M.render_bed (VO duck 9 dB 40 / 400 ms, SFX duck 3 dB, gaps 7 LU under the delivered mix, voice >= 10 LU
over the music) -> M.master_withmusic (-14 LUFS, limiter at -2.3, <= -2.0 dBTP) -> MP3s (M.write_mp3) and the
preview (M.make_preview). Outputs: see OUT_* below.
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
import anim4_vo as V              # noqa: E402

# ============================================================================================ constants
SR = A.SR
BPM = 120.0
KEY = 'D major (D Lydian colour)'
DUR_VIDEO = 51.2667
N = int(round(DUR_VIDEO * SR))            # 2460802 samples
T = N / SR
G = M.Grid(BPM)
BEAT, BAR, STEP = G.beat_s, G.bar_s, G.step_s
END_BEAT = T / BEAT
SEED = 447

AUD = A.AUDIO
OUT_CLEAN = os.path.join(AUD, 'anim4_vo_music.wav')
OUT_BED = os.path.join(AUD, 'anim4_vo_music_bed.wav')
OUT_MIX = os.path.join(AUD, 'anim4_vo_withmusic_mix.wav')
VO_STEM = os.path.join(AUD, 'anim4_vo_vo_stem.wav')
SFX_STEM = os.path.join(AUD, 'anim4_vo_sfx_stem.wav')
REF_MIX = os.path.join(AUD, 'anim4_vo_mix.wav')
REEL = os.path.abspath(os.path.join(HERE, '..', '..', 'reel', 'organic_fostering'))
MP3_BED = os.path.join(REEL, 'organic_fostering_anim4_vo_where_does_it_go_music.mp3')
MP3_CLEAN = os.path.join(REEL, 'organic_fostering_anim4_vo_where_does_it_go_music_clean.mp3')
TITLE = 'Organic Fostering - anim4_vo_where_does_it_go - background music'
SCRATCH = '/tmp/claude-0/-home-user-100/bb73d22e-ad11-5aa0-a0b2-8033920f7c07/scratchpad'
VIDEO_IN = os.path.join(SCRATCH, 'anim4_vo_preview.mp4')
PREVIEW = os.path.join(SCRATCH, 'anim4_vo_music_preview.mp4')

# ============================================================================================ edit timeline
S = V.SRC


def ot(src_t):
    return float(V.out_time(src_t))


EDIT = dict(slam=0.0, question=ot(S.T_Q), chips=ot(S.T_CHIPS), brk=ot(S.T_BREAK), msg=ot(S.T_MSG),
            home=ot(S.ARRIVE['home']), food=ot(S.ARRIVE['food']), cloth=ot(S.ARRIVE['cloth']),
            travel=ot(S.ARRIVE['travel']), child=ot(S.ARRIVE['child']), gather=ot(S.T_GATHER),
            shrink=ot(S.T_FADE[0]), final=ot(S.T_NUM2), stmt=ot(S.T_STMT), logo=ot(S.T_LOGO), ask=ot(S.T_ASK))
VO_LINES = [(c['line'], float(c['start']), float(c['end'])) for c in V.vo_cues()]
HERO = sorted({round(float(c['t']), 4) for c in V.cues() if float(c.get('gain_db', 0.0)) >= -6.0})


def boundary_beat(t):
    """Section change for an edit boundary at t: the nearest bar line if within one beat, else the nearest beat."""
    bb = int(round(t / BAR)) * 4
    if abs(t - bb * BEAT) <= BEAT + 1e-9:
        return bb
    return int(round(t / BEAT))


SEC_EDGES = [('hookA', 0), ('hookB', boundary_beat(EDIT['question'])), ('msg', boundary_beat(EDIT['brk'])),
             ('home', boundary_beat(EDIT['home'])), ('food', boundary_beat(EDIT['food'])),
             ('cloth', boundary_beat(EDIT['cloth'])), ('travel', boundary_beat(EDIT['travel'])),
             ('child', boundary_beat(EDIT['child'])), ('brk', boundary_beat(EDIT['shrink'])),
             ('lift', boundary_beat(EDIT['final'])), ('end', boundary_beat(EDIT['logo']))]
EXPECTED_EDGES = dict(hookA=0, hookB=8, msg=14, home=26, food=34, cloth=44, travel=54, child=65, brk=72, lift=75,
                      end=88)
assert {k: v for k, v in SEC_EDGES} == EXPECTED_EDGES, SEC_EDGES   # the docstring map is built on these


def section(beat):
    name = SEC_EDGES[0][0]
    for k, b in SEC_EDGES:
        if beat >= b - 1e-9:
            name = k
    return name


SUPPORT = (0.0,)        # the hook slam: the music's first downbeat lands on it (same instant, by design)


def near_hero(t, win=0.06, same=0.008):
    """True if t is within +-win of an SFX hero hit. Only a music event on a SUPPORT instant (+-same) ignores the
    hero hits of that slam's own cluster (within 20 ms of it)."""
    sup = any(abs(t - s) <= same for s in SUPPORT)
    for h in HERO:
        if sup and any(abs(h - s) <= 0.02 for s in SUPPORT):
            continue
        if abs(t - h) < win:
            return True
    return False


def speaking(t, pre=0.05, post=0.1):
    return any(s - pre <= t <= e + post for _, s, e in VO_LINES)


# ============================================================================================ harmony
CHART = [(0, 'Dmaj9'), (4, 'Bm9'), (8, 'E/D'), (14, 'Dadd9'), (16, 'A/C#'), (20, 'Bm9'), (24, 'Gmaj9'),
         (28, 'D/F#'), (32, 'Em9'), (36, 'Gmaj9'), (40, 'Asus4'), (42, 'A'), (44, 'Bm9'), (48, 'Gmaj9'),
         (52, 'D/F#'), (56, 'E/G#'), (60, 'Asus4'), (62, 'A'), (64, 'Bm9'), (68, 'Em9'), (72, 'Asus4'),
         (75, 'Gmaj9'), (80, 'F#m7'), (84, 'Em9'), (86, 'A7sus4'), (88, 'Dmaj9'), (92, 'Gmaj7/D'), (96, 'E/D'),
         (100, 'Dadd9')]
# hand voice-led upper structures (MIDI), one per CHART entry (the bass plays the root / slash note)
PADV = [[66, 69, 73, 76], [66, 69, 73, 74], [64, 68, 71, 76], [66, 69, 74, 76], [64, 69, 73, 76],
        [66, 69, 73, 74], [66, 69, 71, 74], [66, 69, 74, 76], [67, 71, 74, 78], [69, 71, 74, 78],
        [69, 71, 74, 76], [69, 71, 73, 76], [69, 73, 74, 78], [69, 71, 74, 78], [66, 69, 74, 76],
        [64, 68, 71, 76], [64, 69, 74, 76], [64, 69, 73, 76], [66, 69, 73, 74], [67, 71, 74, 78],
        [69, 71, 74, 76], [66, 69, 71, 74, 78], [66, 69, 73, 76, 78], [64, 67, 71, 74, 78], [64, 67, 69, 74, 76],
        [66, 69, 73, 76], [67, 71, 74, 78], [68, 71, 74, 76], [66, 69, 74, 76]]
assert len(PADV) == len(CHART)
for _i, (_b, _s) in enumerate(CHART):           # every voicing note is a chord tone of its symbol (or its 9th)
    _pcs = {n % 12 for n in M.chord(_s)} | {(M.chord(_s.split('/')[0])[0] + 2) % 12}
    assert all(n % 12 in _pcs for n in PADV[_i]), (_s, PADV[_i])


def chord_index(beat):
    i = 0
    for k, (b, _) in enumerate(CHART):
        if beat >= b - 1e-9:
            i = k
    return i


def chord_span(i):
    b0 = CHART[i][0]
    b1 = CHART[i + 1][0] if i + 1 < len(CHART) else END_BEAT
    return b0, b1


def bass_of(i):
    """Bass MIDI note of chord i folded into A1..G#2 (33-44: 55-104 Hz)."""
    m = M.bass_note(CHART[i][1], 2)
    while m > 44:
        m -= 12
    while m < 33:
        m += 12
    return m


# motifs in the VO gaps, placed between the SFX of each gap (no SFX cue >= -12 dB within +-60 ms): (t, MIDI, vel, dur)
MOTIFS = [
    # QUESTION (hook B gap after "But where does it go?"): rising whole steps ending on the Lydian #4 (G#)
    (5.25, 76, 0.50, 0.22), (5.50, 78, 0.52, 0.22), (5.75, 80, 0.56, 0.60),
    (11.00, 73, 0.44, 0.22), (11.25, 74, 0.46, 0.22), (11.50, 78, 0.50, 0.50),      # Bm9, before the move home
    (15.25, 74, 0.44, 0.12), (15.375, 76, 0.46, 0.12), (15.50, 78, 0.50, 0.40),     # D/F# (home)
    (20.00, 74, 0.44, 0.30), (20.375, 76, 0.46, 0.12), (20.50, 81, 0.50, 0.35),     # Asus4 (food)
    (26.00, 74, 0.44, 0.12), (26.125, 76, 0.46, 0.12), (26.25, 81, 0.50, 0.40),     # D/F# (clothes)
    (30.50, 76, 0.44, 0.22), (31.00, 81, 0.46, 0.22), (31.50, 85, 0.50, 0.45),      # Asus4 -> A: the sus resolves
    (35.50, 79, 0.44, 0.22), (35.75, 83, 0.46, 0.40),                               # Em9, into the breakdown
    (44.00, 74, 0.46, 0.60), (44.00, 78, 0.40, 0.60),                               # end card: the resolution
    # ANSWER (after the last line): the question's shape, now landing on the tonic
    (49.75, 76, 0.46, 0.22), (50.00, 78, 0.48, 0.22), (50.25, 81, 0.48, 0.22), (50.50, 86, 0.50, 0.70),
]
SFX_CUES = [(float(c['t']), float(c.get('gain_db', 0.0))) for c in V.cues()]


EVENTS = []          # (t, kind, gain_db) for the hero-hit audit

# stem trims (dB) applied when the stems are summed (balance measured as stem LUFS in qa: stems_lufs)
TRIM = dict(pad=5.0, ep=3.0, arps=3.5, motif=1.0, sub=-8.0, bass_pluck=3.0, kick=-6.0, clap=4.0, shaker=6.0, fx=0.0)


def log(t, kind, gain_db):
    EVENTS.append((round(float(t), 4), kind, round(float(gain_db), 1)))


# ============================================================================================ layers
def layer_pad():
    tr, air = M.Track(T, 'pad'), M.Track(T, 'airpad')
    cut = dict(hookA=1300.0, hookB=1500.0, msg=1700.0, home=1800.0, food=1900.0, cloth=2000.0, travel=2200.0,
               child=2300.0, brk=2000.0, lift=2600.0, end=1800.0)
    gdb = dict(hookA=-13.0, hookB=-13.0, msg=-14.0, home=-14.0, food=-14.0, cloth=-14.0, travel=-13.5,
               child=-13.0, brk=-12.0, lift=-12.5, end=-13.0)
    for i in range(len(CHART)):
        b0, b1 = chord_span(i)
        t0, t1 = b0 * BEAT, b1 * BEAT
        sec = section(b0)
        last = i == len(CHART) - 1
        dur = (t1 - t0 - 0.12) if not last else (T - t0 - 0.2)
        att = 0.04 if b0 == 0 else (0.35 if sec == 'brk' else 0.22)
        x = M.pad(PADV[i], dur=dur, vel=0.6, wave='warm', voices=5, detune=12.0, attack=att,
                  release=0.45 if not last else 1.0, cutoff=cut[sec], q=0.7, sweep=0.25, sweep_rate=0.09,
                  open_to=cut[sec] * 1.6 if sec == 'brk' else None, chorus_mix=0.3, width=0.9, seed=SEED + i)
        tr.add(A.hp(x, 150.0, 2), t0, gain_db=gdb[sec])
        if sec in ('child', 'lift', 'end') or (b0 < 65 <= b1):
            ts = max(t0, 65 * BEAT) if b0 < 65 else t0
            top = [n + 12 for n in PADV[i][-2:]]
            d2 = (t1 - ts - 0.12) if not last else (T - ts - 0.25)
            y = M.pad(top, dur=d2, vel=0.5, wave='tri', voices=4, detune=9.0, attack=0.5 if ts > t0 else 0.25,
                      release=0.5 if not last else 1.0, cutoff=5200.0, chorus_mix=0.45, width=1.0,
                      seed=SEED + 50 + i)
            air.add(A.hp(y, 300.0, 2), ts, gain_db=-25.0 if sec != 'lift' else -23.5)
    return tr.buf, air.buf


GROOVE = ('msg', 'home', 'food', 'cloth', 'travel', 'child', 'lift')


def next_change(b):
    """Beat of the next chord change after beat b (or the end)."""
    i = chord_index(b)
    return CHART[i + 1][0] if i + 1 < len(CHART) else END_BEAT


def ep_voicing(i):
    """EP voicing of chord i: the pad's upper structure an octave down, opened up so no two notes sit a 2nd apart
    (the upper note of a 2nd goes up an octave, or the lower one down, up to D5 / from D3)."""
    v = sorted(n - 12 for n in PADV[i][:4])
    for _ in range(8):
        pairs = [(v[k + 1] - v[k], k) for k in range(len(v) - 1) if v[k + 1] - v[k] <= 2]
        if not pairs:
            break
        _, k = min(pairs)
        lo_, hi_ = v[k], v[k + 1]
        if hi_ + 12 <= 74:
            v[k + 1] = hi_ + 12
        elif lo_ - 12 >= 50:
            v[k] = lo_ - 12
        else:
            v.pop(k)
        v = sorted(set(v))
    return v


def layer_ep():
    """Soft FM electric piano, octave 3. Hook / end card: one long chord per chord change; groove sections:
    stabs on 1, the and-of-2 and the and-of-3 (+ the and-of-4 in travel and the lift); section entries that fall
    mid-bar (b14, b75) get their own downbeat stab. A chord never rings over the next change."""
    tr = M.Track(T, 'ep')
    rng = np.random.default_rng(SEED + 1)
    hits = []                                                     # (beat, dur_beats, vel)
    for i, (b0, _) in enumerate(CHART):
        if section(b0) in ('hookA', 'hookB', 'end'):
            hits.append((b0, 6.0, 0.40))
    for bar in range(int(np.ceil(END_BEAT / 4))):
        bb = bar * 4
        pat = [(0.0, 0.9, 0.46), (1.5, 0.6, 0.38), (2.5, 0.8, 0.42)]
        if section(bb) in ('travel', 'lift') or section(bb + 3.5) in ('travel', 'lift'):
            pat.append((3.5, 0.4, 0.34))
        for q, dl, vel in pat:
            if section(bb + q) in GROOVE:
                hits.append((bb + q, dl, vel + (0.05 if section(bb + q) == 'lift' else 0.0)))
    for b in (14, 75):                                            # mid-bar section entries
        hits = [h for h in hits if not (b < h[0] < b + 1)]
        hits.append((b, 0.9, 0.5))
    for j, (b, dl, vel) in enumerate(sorted(hits)):
        if b >= END_BEAT - 0.5:
            continue
        i = chord_index(b)
        t = b * BEAT
        dl = min(dl, next_change(b) - b - 0.08)
        g = -16.0 - (9.0 if near_hero(t) else 0.0)
        notes = ep_voicing(i)
        for k, n in enumerate(notes):
            x = M.fm_epiano(n, dur=dl * BEAT, vel=vel + 0.03 * (k == len(notes) - 1), release=0.35, bright=0.8,
                            tine=0.6, detune=0.5, seed=SEED + j * 7 + k)
            off = 0.0015 * k + rng.uniform(-0.002, 0.002)          # gentle spread, <= 6.5 ms
            tr.add(A.hp(x, 150.0, 2), t + off, gain_db=g, pan=-0.22)
        log(t, 'ep', g)
    return tr.buf


ARP_PAT = dict(
    hook=[0, 1, 2, 3, 4, 3, 2, 1],                                         # 8ths, rising
    msg=[0, 2, 1, 3, 2, 4, 3, 1, 0, 2, 1, 3, 2, 4, 3, 5],                  # 16ths
    food=[3, None, 2, 4, None, 3, 1, None, 4, None, 2, 3, None, 5, 3, None],
    child=[0, 2, 4, 2, 1, 3, 5, 3],                                        # 8ths
    counter=[None, 4, None, 3, None, 5, None, 2],                          # off-beat 8ths
    end=[0, 2, 1, 3, 2, 4, 3, 2],                                          # 8ths
)


def _pool(i):
    v = PADV[i][:4]
    return v + [v[0] + 12, v[1] + 12]


def layer_arps():
    glass, bellarp = M.Track(T, 'glass'), M.Track(T, 'bellarp')
    n16 = int(END_BEAT * 4)
    for k in range(n16):
        b = k / 4.0
        t = k * STEP
        sec = section(b)
        i = chord_index(b)
        pool = _pool(i)
        acc = 0.66 if k % 4 == 0 else (0.56 if k % 2 == 0 else 0.48)
        hg = -12.0 if near_hero(t) else 0.0
        # glassy pluck: hook (8ths), message + home (16ths), lift (16ths), end bar 22-23 (8ths, thinning)
        gp = None
        if sec in ('hookA', 'hookB') and k % 2 == 0:
            gp, oct_, gdb = ARP_PAT['hook'][(k // 2) % 8], 0, -19.0
        elif sec in ('msg', 'home'):
            gp, oct_, gdb = ARP_PAT['msg'][k % 16], 0, -19.5
        elif sec == 'lift' and b >= 76:
            gp, oct_, gdb = ARP_PAT['msg'][(k + 4) % 16], 0, -19.0
        elif sec == 'end' and k % 2 == 0 and b < 96:
            gp, oct_, gdb = ARP_PAT['end'][(k // 2) % 8], 0, -21.0 - 0.5 * (b - 88)
        if gp is not None:
            x = M.pluck_synth(pool[gp] + 12 * oct_, dur=STEP * 0.8, vel=acc, cutoff=1000.0, env_oct=2.4, decay=0.06,
                              amp_decay=0.2, q=1.1, wave='square', detune=5.0, release=0.06, seed=SEED + k)
            glass.add(A.hp(x, 200.0, 2), t, gain_db=gdb + hg, pan=0.32 if k % 2 else -0.32)
            log(t, 'arp', gdb + hg)
        # glassy counter-arp: travel (off-beat 8ths, octave up)
        if sec == 'travel' and k % 2 == 0:
            cp = ARP_PAT['counter'][(k // 2) % 8]
            if cp is not None:
                x = M.pluck_synth(pool[cp] + (12 if cp < 4 else 0), dur=STEP * 0.9, vel=0.5, cutoff=1300.0,
                                  env_oct=2.0, decay=0.05, amp_decay=0.16, q=1.0, wave='square', detune=6.0,
                                  release=0.05, seed=SEED + 3000 + k)
                glass.add(A.hp(x, 250.0, 2), t, gain_db=-22.0 + hg, pan=0.45)
                log(t, 'arp', -22.0 + hg)
        # FM bell arp: food, clothes, travel (16th pattern), child (8ths), lift (16ths)
        fp = None
        if sec in ('food', 'cloth', 'travel'):
            fp, fdb = ARP_PAT['food'][k % 16], -20.0
        elif sec == 'child' and k % 2 == 0:
            fp, fdb = ARP_PAT['child'][(k // 2) % 8], -20.5
        elif sec == 'lift':
            fp, fdb = ARP_PAT['food'][(k + 8) % 16], -20.0
        if fp is not None:
            x = M.fm_epiano(pool[fp] + (12 if fp < 4 else 0), dur=0.09, vel=acc - 0.04, release=0.22, bright=1.2,
                            tine=1.4, detune=0.8, seed=SEED + 5000 + k)
            bellarp.add(A.hp(x, 250.0, 2), t, gain_db=fdb + hg, pan=-0.3 if k % 2 else 0.3)
            log(t, 'arp', fdb + hg)
    return glass.buf, bellarp.buf


def layer_motifs():
    tr, glk = M.Track(T, 'motif'), M.Track(T, 'glock')
    for j, (t, m, vel, dur) in enumerate(MOTIFS):
        assert not near_hero(t), ('motif near a hero hit', t)
        assert not speaking(t, pre=0.08, post=0.05), ('motif under speech', t)
        assert not any(abs(t - c) < 0.06 and g >= -12.0 for c, g in SFX_CUES), ('motif on an SFX cue', t)
        x = M.fm_epiano(m, dur=dur, vel=vel, release=0.6, bright=1.25, tine=1.5, detune=1.0, seed=SEED + 7000 + j)
        y = M.bell(m, vel=vel * 0.85, kind='hand', hardness=0.35, decay=0.45, seed=SEED + 7100 + j)
        tr.add(A.hp(x, 250.0, 2), t, gain_db=-13.0, pan=0.12)
        tr.add(A.hp(y, 300.0, 2), t, gain_db=-21.0, pan=-0.1)
        log(t, 'motif', -13.0)
    for t, m in ((44.0, 98), (50.5, 98)):          # glock sparkle on the resolution and on the answer's tonic
        assert not near_hero(t)
        tr_ = M.glockenspiel(m, vel=0.4, hardness=0.4, decay=0.7, seed=SEED + int(t * 10))
        glk.add(A.hp(tr_, 400.0, 2), t, gain_db=-25.0, pan=0.2)
        log(t, 'glock', -25.0)
    return tr.buf, glk.buf


def layer_bass():
    sub, bp = M.Track(T, 'sub'), M.Track(T, 'bpluck')
    groove = GROOVE
    hits = []                                       # (beat, dur_beats, vel)
    # hook: one long note per chord
    for i in range(3):
        b0, b1 = chord_span(i)
        hits.append((b0, b1 - b0 - 0.2, 0.72))
    for bar in range(3, int(np.ceil(END_BEAT / 4))):
        bb = bar * 4
        sec = section(bb)
        if sec in groove:
            for q, dl, vel in ((0.0, 1.6, 0.78), (2.5, 1.2, 0.66)):
                if section(bb + q) in groove:
                    hits.append((bb + q, dl, vel))
        elif section(bb + 2) in groove:              # the journey enters mid-bar (b14): D on the entry beat
            hits.append((bb + 2, 1.6, 0.8))
        elif sec == 'brk':
            hits.append((bb, 2.8, 0.68))           # A pedal under the breakdown
        elif sec == 'end':
            last = bb + 4 > END_BEAT
            hits.append((bb, (END_BEAT - bb - 0.5) if last else 3.7, 0.7 if bar == 22 else 0.62))
    hits.append((75.0, 1.6, 0.8))                  # the lift (37.5, mid-bar) and the A7sus4 on b86
    hits.append((86.0, 0.9, 0.7))
    hits.sort()
    for b, dl, vel in hits:
        t = b * BEAT
        i = chord_index(b)
        g = -8.0
        att = 0.05 if near_hero(t) else 0.008       # near a hero hit: a slow swell, no onset
        x = M.sub_bass(bass_of(i), dur=dl * BEAT, vel=vel, drive=1.5, harm=0.15, attack=att, release=0.08)
        sub.add(x, t, gain_db=g)
        log(t, 'sub', g)
    # bass pluck octave bounce (off-beat 8ths): clothes, travel, lift (from bar 19)
    for k in range(int(END_BEAT * 2)):
        b = k / 2.0
        if k % 2 == 0:
            continue
        sec = section(b)
        if sec in ('cloth', 'travel') or (sec == 'lift' and b >= 76):
            t = b * BEAT
            i = chord_index(b)
            g = -18.0 - (12.0 if near_hero(t) else 0.0)
            x = M.bass_pluck(bass_of(i) + 12, dur=0.16, vel=0.55, cutoff=420.0, env_oct=2.2, decay=0.07, sub=0.4,
                             seed=SEED + k)
            bp.add(x, t, gain_db=g)
            log(t, 'bass', g)
    return sub.buf, bp.buf


def layer_drums():
    kick, clap, shk = M.Track(T, 'kick'), M.Track(T, 'clap'), M.Track(T, 'shaker')
    rng = np.random.default_rng(SEED + 2)
    kick_secs = ('msg', 'home', 'food', 'cloth', 'travel', 'child', 'lift')
    kick_times = []
    for b in range(int(np.ceil(END_BEAT))):
        sec = section(b)
        t = b * BEAT
        if sec in kick_secs:
            vel = 0.82 if b % 2 == 0 else 0.74
            if sec == 'lift':
                vel += 0.05
            if near_hero(t):
                x, g = M.soft_kick(vel=0.5, punch=0.4, tone=52.0, decay=0.22, click=0.1, drive=1.2), -15.0
            else:
                x, g = M.soft_kick(vel=vel, punch=0.4, tone=52.0, decay=0.26, click=0.15, drive=1.3), -5.0
                kick_times.append(t)
            kick.add(x, t, gain_db=g)
            log(t, 'kick', g)
        # claps on 2 and 4: home + food, and the lift from bar 19
        if (sec in ('home', 'food') or (sec == 'lift' and b >= 76)) and b % 4 in (1, 3):
            if not near_hero(t):
                g = -16.0 - (4.0 if speaking(t) else 0.0)
                clap.add(A.hp(M.clap(vel=0.62, tone=1150.0, room='room', wet_db=-8.0, seed=b % 4), 200.0, 2),
                         t - 0.03, gain_db=g)
                log(t, 'clap', g)
    # shaker strokes (peak on the 16th): hook B 8ths, groove 16ths, end bar 22 8ths fading
    acc = (1.0, 0.45, 0.75, 0.5)
    for k in range(int(END_BEAT * 4)):
        b = k / 4.0
        sec = section(b)
        if sec == 'hookB':
            if k % 2:
                continue
            g, vel = -27.0 + 1.0 * (b - 8), 0.5
        elif sec in kick_secs:
            g, vel = (-21.0 if sec != 'lift' else -20.0), 0.55
            if sec == 'msg' and b < 16:
                g -= 1.5
        elif sec == 'end' and b < 92:
            if k % 2:
                continue
            g, vel = -22.0 - 1.5 * (b - 88), 0.5
        else:
            continue
        t = k * STEP + (0.03 * STEP if k % 2 else 0.0) + rng.uniform(-0.003, 0.003)
        if near_hero(k * STEP):
            g -= 9.0
        x = M.shaker(vel=vel * acc[k % 4], length=0.06, tone=7500.0, attack=0.012, seed=k % 16)
        shk.add(x, t - 0.012, gain_db=g, pan=0.25 if k % 2 else 0.15)
    return kick.buf, clap.buf, shk.buf, kick_times


def layer_fx():
    fx = M.Track(T, 'fx')
    # hook: soft reversed Dadd9 swell into the groove entry (b14, 7.0 s), under the break's coin burst
    fx.add(A.hp(M.reverse_swell(1.0, vel=0.5, notes=PADV[3], bright=0.8, seed=SEED), 200.0, 2), 14 * BEAT - 1.0,
           gain_db=-24.0)
    # breakdown: riser + reversed G chord swell peaking on 37.25 (into the final-number slam at 37.267)
    hit = 74.5 * BEAT
    fx.add(A.hp(M.riser(1.25, vel=0.55, f_start=500.0, f_end=6000.0, note=69, seed=SEED), 250.0, 2), hit - 1.25,
           gain_db=-21.0)
    fx.add(A.hp(M.reverse_swell(1.0, vel=0.55, notes=PADV[21][:4], seed=SEED + 1), 200.0, 2), hit - 1.0,
           gain_db=-20.0)
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


def speech_carve(x, s):
    """The speech-aware filter: a 2-pole low-pass sliding between SPEECH_LP[1] (gaps) and SPEECH_LP[0] (speech)
    in the log domain, plus a SPEECH_DIP peaking cut cross-faded in by the speech envelope s."""
    lo, hi = SPEECH_LP
    fc = np.exp(np.log(hi) + s * (np.log(lo) - np.log(hi)))
    y = M.tv_lowpass(x, fc, q=0.707)
    f, q, g = SPEECH_DIP
    return y + s[:, None] * (A.eq(y, 'peak', f, q, g) - y)


# ============================================================================================ render
PARTS = {}           # the processed parts of the last render (for QA / debugging)


def render(verbose=True):
    t0 = time.time()
    EVENTS.clear()
    u = lambda k: A.undb(TRIM[k])                     # noqa: E731
    pad, airpad = (y * u('pad') for y in layer_pad())
    ep = layer_ep() * u('ep')
    glass, bellarp = (y * u('arps') for y in layer_arps())
    motif, glock = (y * u('motif') for y in layer_motifs())
    sub, bpl = layer_bass()
    sub, bpl = sub * u('sub'), bpl * u('bass_pluck')
    kick, clap, shk, kick_times = layer_drums()
    kick, clap, shk = kick * u('kick'), clap * u('clap'), shk * u('shaker')
    fx = layer_fx() * u('fx')
    sp = speech_env(N)
    pe_f = speech_carve(M.pump(pad + airpad + ep, kick_times, depth_db=2.5, attack=0.004, release=0.2), sp)
    ar_f = speech_carve(M.pump(glass + bellarp, kick_times, depth_db=2.5, attack=0.004, release=0.2), sp)
    ar_f *= A.undb(-3.0 * sp)[:, None]                   # the arps also sit 3 dB lower under speech
    mot_f = speech_carve(motif + glock, sp)
    sends = (M.reverb_send(pe_f, 'hall', wet_db=-16.0, hp_hz=250.0)
             + M.reverb_send(ar_f + clap, 'plate', wet_db=-15.0, hp_hz=300.0)
             + M.reverb_send(mot_f, 'plate', wet_db=-13.0, hp_hz=300.0)
             + M.reverb_send(mot_f, 'air', wet_db=-15.0, hp_hz=500.0))
    low = A.lp(sub, 400.0, 2) + bpl
    PARTS.clear()
    PARTS.update(pad_ep=pe_f, arps=ar_f, motif=mot_f, low=low, kick=kick, clap=clap, shaker=shk, fx=fx, sends=sends)
    mix = pe_f + ar_f + mot_f + low + kick + clap + shk + fx + sends
    mix = A.hp(mix, 30.0, 2)
    mix = M.bus_comp(mix, thresh_db=-18.0, ratio=1.6, attack=0.012, release=0.2)
    mix = M.tilt_eq(mix, 0.8)
    mix = M.fade_out(mix, 1.4, end=T - 0.02)             # fade 49.847-51.247, silence in the last 20 ms
    mix, info = M.normalise_lufs(mix, target=-16.0, tp_ceiling=-1.2)
    mix[int(round((T - 0.02) * SR)):] = 0.0
    stems = dict(pad=pad + airpad, ep=ep, arps=glass + bellarp, motif=motif + glock, sub=sub, bass_pluck=bpl,
                 kick=kick, clap=clap, shaker=shk, fx=fx, sends=sends)
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
    (outside the slam's support instant) and their gain; loud = kick / clap / motif / glock above -15 dB.
    (2) Measurement on the clean music, high-passed at 150 Hz (so sub ripple does not read as onsets), 8 ms RMS:
    onset rise = the level jump over 10 ms. Per hero hit: the largest rise inside +-60 ms and the level at it,
    both relative to the median kick-beat onset (rise_rel_db, level_rel_db). A loud transient there would read
    about 0 / 0; the beats read 0 / 0 by definition."""
    near = [e for e in EVENTS if near_hero(e[0])]
    loud = [e for e in near if e[1] in ('kick', 'clap', 'motif', 'glock') and e[2] > -15.0]
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

    kicks = [e[0] for e in EVENTS if e[1] == 'kick' and e[2] > -10.0]
    ob = np.array([onset(t - 0.01, t + 0.03) for t in kicks])
    r_ref, l_ref = float(np.median(ob[:, 0])), float(np.median(ob[:, 1]))
    rows = []
    for h in HERO:
        if any(abs(h - s) <= 0.02 for s in SUPPORT):
            continue
        r, lv = onset(h - 0.06, h + 0.06)
        rows.append((h, round(r - r_ref, 1), round(lv - l_ref, 1)))
    rows.sort(key=lambda r: -(r[1] + r[2]))
    # the same metric on +-60 ms windows at arbitrary instants of the groove (every 0.137 s, 7-36 s), for scale
    typ = np.array([onset(t - 0.06, t + 0.06) for t in np.arange(7.03, 36.0, 0.137)
                    if not any(abs(t - h) < 0.12 for h in HERO)])
    return dict(n_hero=len(HERO), events_near=len(near), loud_events_near=loud,
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
    # low end mono: side / mid energy below 120 Hz; stereo correlation
    lo = A.lp(clean, 120.0, 4)
    mid, side = lo.mean(1), 0.5 * (lo[:, 0] - lo[:, 1])
    out['clean']['low120_side_minus_mid_db'] = round(float(10 * np.log10((side ** 2).sum() / (mid ** 2).sum()
                                                                         + 1e-20)), 1)
    out['clean']['corr_LR'] = round(float(np.corrcoef(clean[:, 0], clean[:, 1])[0, 1]), 3)
    out['beatgrid'] = M.beat_grid_check(clean, BPM)
    out['stems_lufs'] = {k: round(A.loudness(v), 1) for k, v in stems.items() if np.any(v)}
    out['bed'] = dict(bedm, lufs=round(A.loudness(bed), 2), true_peak=round(A.true_peak(bed), 2), samples=len(bed))
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
    voiced = spw & (bv > np.median(bv[spw]) - 15.0)      # speech windows with the voice within 15 dB of its median
    dv = (bv - bm)[voiced]
    out['voice_vs_music'] = dict(momentary_median_lu=round(float(np.median(d)), 2),
                                 momentary_p10_lu=round(float(np.percentile(d, 10)), 2),
                                 band1_4k_100ms_median_db=round(float(np.median(db_)), 2),
                                 band1_4k_100ms_p10_db=round(float(np.percentile(db_, 10)), 2),
                                 n_windows=int(spw.sum()),
                                 voiced_band1_4k_100ms_median_db=round(float(np.median(dv)), 2),
                                 voiced_band1_4k_100ms_p10_db=round(float(np.percentile(dv, 10)), 2),
                                 voiced_band1_4k_100ms_min_db=round(float(np.min(dv)), 2), n_voiced=int(voiced.sum()))
    out['hero'] = hero_audit(clean)
    return out


# ============================================================================================ main
def main():
    t0 = time.time()
    print('sections (beat -> s):', [(k, b, b * BEAT) for k, b in SEC_EDGES])
    clean, stems, info = render()
    assert len(clean) == N
    A._write_wav(OUT_CLEAN, clean, 24)
    st = M.load_reel_stems('anim4')
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
