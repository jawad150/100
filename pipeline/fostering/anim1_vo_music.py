"""anim1_vo_music.py: original background music for ANIM 1 "Day in the Life" (VO version, anim1_vo, 31.2 s).

    cd pipeline/fostering && python3 anim1_vo_music.py        (deterministic: seeded; renders every file below)

Synthesised with music_synth.py (MS) + audio.py (A): numpy / scipy only, no samples. Warm, homely, gently
playful, hopeful. Background music under a voice-over: no lead melody while the voice speaks (the melodic
figures sit in the VO gaps). While a line is spoken, the bus above the bass gets two zero-phase dips: 0.8-5 kHz
by 12 dB (+2 dB level) and 280-800 Hz (the low-mid body of the voice) by 6 dB; and each event is choked per
layer (SPEECH_DB: glock -14, fx -10, piano -8, mallets / snaps / guitars -6, uke -5, pad -4, sub -3 dB). The
choke is monotonic, so a ringing tail never swells back up when the line ends.

KEY F major | 100 BPM | beat n = n * 0.6 s from 0.000 (beat 1 at 0.000 s) | bar = 2.4 s | 13 bars = 52 beats =
31.2 s exactly. Section boundaries are computed in OUTPUT time from the VO module (V = anim1_vo, V.SRC = anim1):
    V.out_time(T_SLIDE0) = 5.275 (frame 2)   -> nearest bar line: bar 2 = 4.80
    V.out_time(T_F3)     = 10.50 (frame 3)   -> mid-bar: on beat 18 = 10.80
    V.out_time(T_F4)     = 21.30 (frame 4)   -> nearest bar line: bar 9 = 21.60
    V.out_time(B(31))    = 25.20 (end card)  -> mid-bar: on beat 42 = 25.20
    (the frame-3 checklist rows start at 14.37 -> sub-phrase on bar 6 = 14.40)

MUSIC MAP (output seconds; VO = V.vo_cues(); hero hit = V.cues() with gain_db >= -6)
 section     | bars    | beats  | t0-t1 s     | edit events                  | music events
 ------------+---------+--------+-------------+------------------------------+------------------------------------------
 A hook      | 0-1     | b0-8   | 0.00-4.80   | stamps WHAT .0 DOES .3       | Fadd9 / Bbadd9 Csus4. Light, curious:
             |         |        |             | FOSTERING .6 REALLY .9 LOOK  | staccato uke picks on 8ths (on the
             |         |        |             | 1.05 LIKE? 1.2; clock lands  | stamps), low warm pad, sub; soft kick
             |         |        |             | 1.35; brackets 1.52; marker  | under WHAT and FOSTERING, then on 1 and
             |         |        |             | 1.8; VO 0.05-2.18,           | 3; brushes in bar 1
             |         |        |             | 2.50-4.53; clock ticks       |
             |         |        |             | 3.3-5.04                     |
 B list      | 2-4.5   | b8-18  | 4.80-10.80  | slide 5.28-5.62; stamps      | M1 glock motif F6-A6-C7-G6 (the
             |         |        |             | SCHOOL RUNS 5.70, HOMEWORK   | "question", ends on G) in the VO gap
             |         |        |             | 7.50, BAKING 8.70 (VO 5.78 / | 4.80-5.40. F Dm7 / Bbadd9 C / Am7.
             |         |        |             | 7.58 / 8.78); bus 6.82; oven | Bouncy: kick + sub on 1 and 3 and on the
             |         |        |             | ding (C7) 9.90; props ->     | 'and's that carry the stamps
             |         |        |             | blocks 10.50-10.74           | (LIST_GROOVE), bass pluck on the 'and's,
             |         |        |             |                              | finger snaps on 2 and 4, shaker 16ths,
             |         |        |             |                              | nylon strums D/U (an up-strum on each
             |         |        |             |                              | stamp). Low marimba dyad on each stamp
             |         |        |             |                              | (top note rising C4-D4-E4); marimba
             |         |        |             |                              | answers the ding C6-A5-E5 in the VO gap
             |         |        |             |                              | 10.05-10.35
 C1 warm     | 4.5-5   | b18-24 | 10.80-14.40 | blocks land 11.10 / 11.70 /  | Bbmaj7 / F/A. Settles warmer, more
             |         |        |             | 12.30 (STABILITY) with       | sustained: snaps, strums, pluck bass out;
             |         |        |             | swishes + poofs; VO          | the pad swells in (1.2 s) and opens;
             |         |        |             | 11.20-13.87                  | sustained sub; the busy tower SFX are
             |         |        |             |                              | left alone until a soft felt-piano F/A
             |         |        |             |                              | chord ON the STABILITY landing (12.30,
             |         |        |             |                              | rolled 3.5 ms/note, all 4 notes within
             |         |        |             |                              | 12 ms of the hit); nylon
             |         |        |             |                              | picked arpeggio, brushes
 C2 warm     | 6-7     | b24-32 | 14.40-19.20 | checklist rows 14.37 / 16.17 | Dm7 / Bbmaj7 C7sus4. Felt-piano Dm7
             |         |        |             | / 18.27 (pop + tick); VO     | anticipation 14.10 and C7sus4 + C5 at
             |         |        |             | 14.50-15.91, 16.40-17.90,    | 18.00 / 18.15 in the VO gaps; arpeggio,
             |         |        |             | 18.50-19.98                  | brushes, kick on 1 and 3 where the rows'
             |         |        |             |                              | pops allow
 C3 pre-lift | 8       | b32-36 | 19.20-21.60 | VO gap 19.98-21.50; page     | Gm7 Am7; the bass starts climbing G1-A1
             |         |        |             | flip 21.12; frame 4 21.30    | (-> Bb1 C2 D2 E2 F2). Melodic hook M2
             |         |        |             |                              | (marimba, glock doubling) F5-A5-C6-G5-E5
             |         |        |             |                              | 20.10-21.00 in the gap; strums return;
             |         |        |             |                              | reverse swell (Bbadd9) into 21.60
 D lift      | 9-10.5  | b36-42 | 21.60-25.20 | headline stamps 21.40 /      | Bbadd9 C / Dm7 C/E, rising bass
             |         |        |             | 21.85 / 22.30; VO            | Bb1-C2-D2-E2 with glides. Gentle lift:
             |         |        |             | 21.50-23.85; house lands     | wider pad voicing, filter opening on C,
             |         |        |             | 22.80; headline sinks 24.43  | full strums, claps on 2 and 4, shaker
             |         |        |             |                              | 16ths, bass-pluck 8ths; kick + strum +
             |         |        |             |                              | sub land with the house (22.80). Marimba
             |         |        |             |                              | run D5 F5 A5 G5 E5 G5 Bb5 in the VO gap
             |         |        |             |                              | 24.00-25.05, resolving Bb5 -> A5 on the
             |         |        |             |                              | end card
 E end card  | 10.5-12 | b42-52 | 25.20-31.20 | light switch + "Could you    | Fadd9 (25.20, with the light switch) /
             |         |        |             | make room?" 25.20; logo      | Bbmaj7 Csus4 C / F (28.80): resolves to
             |         |        |             | sting (C bell) 25.65; VO     | the tonic. Half-time strums, felt-piano
             |         |        |             | 25.35-26.39, 26.74-29.63     | chords, uke picks return in bar 11
             |         |        |             |                              | (bookend), kick on 1 and 3 to 28.80; then
             |         |        |             |                              | the drums stop, the F chord (soft, under
             |         |        |             |                              | "Start your enquiry") rings, soft glock
             |         |        |             |                              | + marimba motif M3 F6-A6-C7-F6 (the
             |         |        |             |                              | "answer", ends on F; 1.8x decay) in the
             |         |        |             |                              | gap after the CTA 29.70-30.30. Fade
             |         |        |             |                              | 29.70-31.17 (1.47 s), last 30 ms silent
 Chords (beat: chord, "|" = bar line): 0 Fadd9 | 4 Bbadd9 6 Csus4 | 8 F 10 Dm7 | 12 Bbadd9 14 C | 16 Am7
 18 Bbmaj7 | 20 F/A | 24 Dm7 | 28 Bbmaj7 30 C7sus4 | 32 Gm7 34 Am7 | 36 Bbadd9 38 C | 40 Dm7 41 C/E 42 Fadd9 |
 44 Bbmaj7 46 Csus4 47 C | 48 Fadd9. Voicings are hand voice-led (CHORDS); bass F2 / Bb1 / C2 / D2 / A1 / G1 /
 E2 (49-87 Hz).

INSTRUMENTS (all from MS): karplus_strong 'uke' (staccato picked figure) and 'nylon' (picked arpeggio), strum
'nylon', marimba, glockenspiel, felt_piano (pedal), pad (wave 'warm', 5 voices, chorus), sub_bass (with
glides), bass_pluck, soft_kick, clap (a 2-burst finger snap in the list, a 4-burst clap in the lift), shaker,
brush, reverse_swell.
MIX: per-layer bus trims (TRIM); sends to hall (pad + piano), plate (mallets, guitars, uke) and room
(percussion), all high-passed at 220-300 Hz. Every layer except kick and bass is high-passed at 120-200 Hz
(zero phase). Gentle kick pump (3 dB) on the pad, guitars and bass. The side channel is high-passed at 150 Hz,
so the low end is mono. Bus: 25 Hz high-pass, bus_comp (-18 dB, 1.6:1), +0.5 dB tilt, then normalised to
-16 LUFS with <= -1.2 dBTP via MS.normalise_lufs.

SFX RULE: no music transient within 12-60 ms of an SFX hero hit. Every percussive or plucked event goes
through clear(), which skips the event (and logs it) when a hero hit is 12-60 ms away. The exception is a hit
within 12 ms: that is support on the same instant, and the later strings of a strum on it count as the same
gesture. 'start'-aligned textures (pen, marker or pencil writing) block only when no hit coincides. Verified
twice: on the event log (log_check) and on the audio (music_onsets / transient_check, a context-relative
onset detector calibrated against the log).

MEASURED (last render; main() prints the full report)
    clean -16.01 LUFS, -1.50 dBTP (ffmpeg -16.0 / -1.5), 1 497 600 samples, last 20 ms digital silence, DC 2e-6,
    no clicks, sub-40 Hz -39.9 dB; beat grid 100.0 BPM, phase +3.7 ms. Bed: duck 8.06 dB median under speech,
    music in the VO gaps at ref - 7.0 LU (median 3 s short-term), voice over music 17.5 LU (median momentary,
    speech frames; lowest line 12.9 LU), 1-4 kHz 100 ms windows median 28.5 dB. Masking (100 ms windows,
    300 Hz-4 kHz, music within 6 dB of the voice): 0 of 303 windows with the voice within 20 dB of its p95,
    5 of 340 (1.5%) within 25 dB. With-music mix -14.02 LUFS, -2.30 dBTP, DC 6e-6 (the delivered VO / SFX stems
    are high-passed at 10 Hz here, removing the -4e-4 DC they carry). SFX rule: 0 log violations; every
    rolled piano note on a hit lies within 11 ms of it. The audio onset check flags the pad's 6.5 dB chorus swell
    37 ms after bus_pass and 6.0-6.1 dB periodic beating (26-34 ms spacing) at 11.70 / 11.75 with no event
    logged at 11.4-11.9 s: sustained-chord ripple, not transients.

DELIVERY (MS.render_bed / MS.master_withmusic, the chain shared by all five reels)
    <AUDIO>/anim1_vo_music.wav             clean, -16 LUFS, <= -1 dBTP, 48 kHz 24-bit, 1 497 600 samples
    <AUDIO>/anim1_vo_music_bed.wav         ducked (9 dB under the VO, 3 dB under the SFX) and levelled bed
    <AUDIO>/anim1_vo_withmusic_mix.wav     VO + SFX + bed mastered to -14 LUFS, <= -2.0 dBTP
    reel/organic_fostering/organic_fostering_anim1_vo_day_in_the_life_music.mp3 (bed) and ..._music_clean.mp3
    <scratchpad>/anim1_vo_music_preview.mp4   picture copied from anim1_vo_preview.mp4, plus the with-music mix
"""
import json
import os
import sys

import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio as A  # noqa: E402
import music_synth as MS  # noqa: E402
import anim1_vo as V  # noqa: E402

SR = A.SR
BPM = float(V.BPM)                      # 100
DUR = float(V.DUR)                      # 31.2
N = int(round(DUR * SR))
BEAT = 60.0 / BPM
SEED = 1101
NAME = 'anim1_vo'
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT_CLEAN = os.path.join(A.AUDIO, NAME + '_music.wav')
OUT_BED = os.path.join(A.AUDIO, NAME + '_music_bed.wav')
OUT_MIX = os.path.join(A.AUDIO, NAME + '_withmusic_mix.wav')
REEL_DIR = os.path.join(REPO, 'reel', 'organic_fostering')
MP3_BED = os.path.join(REEL_DIR, 'organic_fostering_anim1_vo_day_in_the_life_music.mp3')
MP3_CLEAN = os.path.join(REEL_DIR, 'organic_fostering_anim1_vo_day_in_the_life_music_clean.mp3')
TITLE = 'Organic Fostering - anim1_vo_day_in_the_life - background music'
SCRATCH = '/tmp/claude-0/-home-user-100/bb73d22e-ad11-5aa0-a0b2-8033920f7c07/scratchpad'
PREVIEW_IN = os.path.join(SCRATCH, 'anim1_vo_preview.mp4')
PREVIEW_OUT = os.path.join(SCRATCH, 'anim1_vo_music_preview.mp4')

FADE_T0, FADE_T1 = 29.70, 31.17         # final fade (1.47 s); zeros after FADE_T1


def B(n):
    """Beat n in output seconds."""
    return n * BEAT


# ============================================================================================ edit timing
SRC = V.SRC
BOUNDS = dict(frame2=V.out_time(SRC.T_SLIDE0), frame3=V.out_time(SRC.T_F3), flip=V.out_time(SRC.T_FLIP0),
              frame4=V.out_time(SRC.T_F4), endcard=V.out_time(SRC.B(31)))
SECTIONS = [  # name, beat0, beat1
    ('A hook', 0, 8), ('B list', 8, 18), ('C1 warm tower', 18, 24), ('C2 warm checklist', 24, 32),
    ('C3 pre-lift', 32, 36), ('D lift', 36, 42), ('E end card', 42, 52)]
VO = V.vo_cues()
CUES = V.cues()
HEROES = sorted((float(c['t']), c['name'], c.get('align', 'hit')) for c in CUES if c.get('gain_db', -99) >= -6)


def clear(t, ignore=()):
    """True if a music transient may sit at t: no hero hit within 12-60 ms, unless a 'hit'-aligned hero lies
    within 12 ms (support on the same instant) and the only other near heroes are 'start'-aligned textures.
    ignore: hero times already supported by the same gesture (the later strings of a strum on a hit): they
    neither block nor need to coincide, and they count as the support."""
    near = [(abs(t - h), al) for h, _, al in HEROES if abs(t - h) <= 0.060
            and not any(abs(h - i) < 1e-6 for i in ignore)]
    if not near:
        return True
    support = bool(ignore) or any(d <= 0.012 and al == 'hit' for d, al in near)
    for d, al in near:
        if d > 0.012 and (al == 'hit' or not support):
            return False
    return True


# ============================================================================================ harmony
# beat, name, bass (MIDI), keys / pad voicing (MIDI), guitar voicing (MIDI)
CHORDS = [
    (0, 'Fadd9', 41, (57, 60, 65, 67), (53, 57, 60, 65, 67)),
    (4, 'Bbadd9', 34, (58, 62, 65, 72), (53, 58, 62, 65, 72)),
    (6, 'Csus4', 36, (60, 65, 67, 72), (55, 60, 65, 67)),
    (8, 'F', 41, (57, 60, 65, 69), (53, 57, 60, 65)),
    (10, 'Dm7', 38, (60, 62, 65, 69), (50, 57, 60, 65)),
    (12, 'Bbadd9', 34, (58, 62, 65, 72), (53, 58, 62, 65, 72)),
    (14, 'C', 36, (60, 64, 67, 72), (52, 55, 60, 64)),
    (16, 'Am7', 33, (60, 64, 67, 69), (52, 57, 60, 67)),
    (18, 'Bbmaj7', 34, (58, 62, 65, 69), (53, 58, 62, 69)),
    (20, 'F/A', 33, (57, 60, 65, 67), (57, 60, 65, 69)),
    (24, 'Dm7', 38, (57, 60, 62, 65), (50, 57, 60, 65)),
    (28, 'Bbmaj7', 34, (58, 62, 65, 69), (53, 58, 62, 69)),
    (30, 'C7sus4', 36, (58, 60, 65, 67), (55, 58, 60, 65)),
    (32, 'Gm7', 31, (58, 62, 65, 67), (50, 55, 58, 65)),
    (34, 'Am7', 33, (57, 60, 64, 67), (52, 57, 60, 67)),
    (36, 'Bbadd9', 34, (58, 62, 65, 72), (53, 58, 62, 65, 72)),
    (38, 'C', 36, (60, 64, 67, 72), (52, 55, 60, 64, 67)),
    (40, 'Dm7', 38, (62, 65, 69, 72), (50, 57, 62, 65, 69)),
    (41, 'C/E', 40, (60, 64, 67, 72), (52, 55, 60, 64, 67)),
    (42, 'Fadd9', 41, (60, 65, 67, 69), (53, 57, 60, 65, 67)),
    (44, 'Bbmaj7', 34, (58, 62, 65, 69), (53, 58, 62, 69)),
    (46, 'Csus4', 36, (60, 65, 67, 72), (55, 60, 65, 67)),
    (47, 'C', 36, (60, 64, 67, 72), (52, 55, 60, 64)),
    (48, 'Fadd9', 41, (57, 60, 65, 67), (53, 57, 60, 65, 67)),
]
END_BEAT = 52


def chord_at(beat):
    """(index, chord tuple) sounding at `beat`."""
    k = max(i for i, c in enumerate(CHORDS) if c[0] <= beat + 1e-9)
    return k, CHORDS[k]


def span(k):
    """(beat0, beat1) of chord k."""
    return CHORDS[k][0], (CHORDS[k + 1][0] if k + 1 < len(CHORDS) else END_BEAT)


def section_of(beat):
    for name, b0, b1 in SECTIONS:
        if b0 <= beat < b1:
            return name
    return SECTIONS[-1][0]


# ============================================================================================ placement
class Arr:
    """Tracks + an event log; transients go through clear()."""

    def __init__(self):
        self.T = {k: MS.Track(DUR, k) for k in ('pad', 'keys', 'gtr', 'uke', 'mallet', 'glock', 'sub', 'pluckb',
                                                'kick', 'perc', 'fx')}
        self.rng = np.random.default_rng(SEED)
        self.log = []
        self.skipped = []

    def put(self, layer, x, t, gain_db=0.0, pan=0.0, check=True, t_check=None, hum=0.003, tag=''):
        tc = t if t_check is None else t_check
        if check and not clear(tc):
            self.skipped.append((round(tc, 3), layer, tag))
            return False
        sup = any(abs(tc - h) <= 0.012 for h, _, _ in HEROES)
        dt = 0.0 if (sup or t <= 0.0 or not hum) else float(self.rng.uniform(-hum, hum))
        t1 = max(0.0, t + dt)
        self.T[layer].add(choke(np.asarray(x, dtype=np.float64), t1, layer), t1, gain_db=gain_db, pan=pan)
        self.log.append((round(tc + dt, 4), layer, tag, bool(check), sup))
        return True


# list groove (beats): kick + sub on every position; the 'and's carry the three stamps (9.5, 12.5, 14.5) and
# the bounce; velocities for the kick
LIST_GROOVE = [(8, 0.78), (9.5, 0.66), (10, 0.72), (11.5, 0.55), (12, 0.78), (12.5, 0.66), (14, 0.72),
               (14.5, 0.66), (16, 0.76), (17.5, 0.6)]
LIST_STRUMS = [(8, 'down'), (9.5, 'up'), (10, 'down'), (11.5, 'up'), (12, 'down'), (12.5, 'up'), (14, 'down'),
               (14.5, 'up'), (15.5, 'up'), (16, 'down'), (17, 'up')]


def build():
    R = Arr()

    # ---------------------------------------------------------------- PAD (warm, chorus; non-transient swells)
    for k, (b0, name, bass, keys, gv) in enumerate(CHORDS):
        s0, s1 = span(k)
        sec = section_of(b0)
        t0, d = B(s0), B(s1 - s0)
        if sec == 'A hook':
            vel, cut, att, gdb = 0.50, 850.0, (1.2 if k == 0 else 0.5), -15.0
        elif sec == 'B list':
            vel, cut, att, gdb = 0.52, 1000.0, 0.35, -15.0
        elif sec.startswith('C'):
            vel, cut, att, gdb = 0.60, 1250.0 + 40.0 * (b0 - 18), (1.2 if b0 == 18 else 0.6), -13.0
        elif sec == 'D lift':
            vel, cut, att, gdb = 0.64, 1500.0, 0.4, -13.5
        else:
            vel, cut, att, gdb = 0.58, 1500.0, 0.35, -13.0
        last = k == len(CHORDS) - 1
        dur = (DUR - t0 - 0.2) if last else d + 0.15
        open_to = 2400.0 if name == 'C' and sec == 'D lift' else None
        notes = list(keys) + ([keys[0] - 12] if sec in ('C1 warm tower', 'C2 warm checklist', 'C3 pre-lift',
                                                         'D lift') else [])
        p = MS.pad(notes, dur=dur, vel=vel, wave='warm', voices=5, detune=12, attack=att,
                   release=(2.2 if last else 1.0), cutoff=cut, q=0.7, sweep=0.25, sweep_rate=0.09,
                   open_to=open_to, chorus_mix=0.35, width=0.85, seed=SEED + k)
        R.put('pad', p, t0, gain_db=gdb, check=False, tag=name)

    # ---------------------------------------------------------------- SUB BASS (+ pluck bass in the list / lift)
    def sub(note, t, dur, vel=0.72, gdb=-6.0, glide_from=None, soft=False):
        ok_t = clear(t)
        x = MS.sub_bass(note, dur=dur, vel=vel, glide_from=glide_from, glide=0.07, drive=1.5, harm=0.10,
                        attack=(0.035 if (soft or not ok_t) else 0.008), release=0.08)
        R.put('sub', x, t, gain_db=gdb, check=False, hum=0, tag='sub %s' % MS.note_name(note, True))

    for k, (b0, name, bass, keys, gv) in enumerate(CHORDS):
        s0, s1 = span(k)
        sec = section_of(b0)
        prev = CHORDS[k - 1][2] if k else None
        if sec == 'A hook':
            sub(bass, B(s0), B(s1 - s0) - 0.12, vel=0.62)
        elif sec == 'B list':
            pos = [b for b, _ in LIST_GROOVE if s0 <= b < s1]
            for i, b in enumerate(pos):
                nxt = pos[i + 1] if i + 1 < len(pos) else s1
                on_beat = abs(b - round(b)) < 1e-9
                if on_beat or clear(B(b)):
                    sub(bass, B(b), B(min(0.9, nxt - b - 0.1)), vel=0.72 if on_beat else 0.62)
                if not on_beat:
                    R.put('pluckb', MS.bass_pluck(bass + 12, dur=B(0.35), vel=0.6, cutoff=380, sub=0.3), B(b),
                          gain_db=-15, tag='pluck')
        elif sec.startswith('C1') or sec.startswith('C2'):
            sub(bass, B(s0), B(s1 - s0) - 0.1, vel=0.66, soft=True)
        elif sec in ('C3 pre-lift', 'D lift'):
            sub(bass, B(s0), B(s1 - s0) - 0.06, vel=0.70, glide_from=prev if sec == 'D lift' else None)
            if sec == 'D lift':
                for e in range(int(round((s1 - s0) * 2))):
                    bt = s0 + 0.5 * e
                    if e % 2 == 1:
                        R.put('pluckb', MS.bass_pluck(bass + 12, dur=B(0.3), vel=0.55, cutoff=420, sub=0.3), B(bt),
                              gain_db=-16, tag='pluck8')
        else:                                   # end card
            last = k == len(CHORDS) - 1
            dur = (FADE_T1 - B(s0) - 0.4) if last else B(s1 - s0) - 0.08
            sub(bass, B(s0), dur, vel=0.70 if not last else 0.66)

    # ---------------------------------------------------------------- KICK (soft, round)
    kick_beats = []
    kick_beats += [(0, 0.6), (1, 0.55), (4, 0.58), (6, 0.52)]                                  # hook: under stamps
    kick_beats += LIST_GROOVE                                                                 # list: bouncy, stamps
    for b in range(18, 32, 2):                                                                # warm: 1 and 3, soft
        kick_beats.append((b, 0.62))
    kick_beats += [(32, 0.68), (34, 0.68), (35, 0.6), (35.5, 0.55)]                           # pre-lift
    kick_beats += [(37.5, 0.56), (38, 0.76), (39.5, 0.56), (40, 0.7), (41, 0.64), (41.5, 0.56)]  # lift
    kick_beats += [(42, 0.8), (44, 0.68), (46, 0.68), (48, 0.74)]                              # end card
    for b, v in kick_beats:
        R.put('kick', MS.soft_kick(vel=v, punch=0.35, tone=52.0, decay=0.28, click=0.18, seed=int(b * 2)), B(b),
              gain_db=-4.0, tag='kick')

    # ---------------------------------------------------------------- PERC: snaps / claps / shaker / brushes
    for b in (9, 11, 13, 15, 17):                                                             # list: snaps 2 & 4
        x = MS.clap(vel=0.62, tone=2100.0, bursts=2, spread=0.004, decay=0.045, room='room', wet_db=-12,
                    seed=b)
        R.put('perc', x, B(b), gain_db=-13.0, pan=0.12, tag='snap')
    for b in (37, 39, 41):                                                                    # lift: claps 2 & 4
        x = MS.clap(vel=0.7, tone=1350.0, seed=b)
        R.put('perc', x, B(b) - 0.03, gain_db=-16.0, t_check=B(b), tag='clap')
    acc16 = (1.0, 0.45, 0.75, 0.5)

    def shaker16(b0, b1, vel, gdb, step=1):
        for s in range(int(round(b0 * 4)), int(round(b1 * 4)), step):
            bt = s / 4.0
            v = vel * acc16[s % 4]
            x = MS.shaker(vel=v, length=0.07, tone=7200.0, attack=0.012, seed=s)
            R.put('perc', x, B(bt) - 0.012, gain_db=gdb, pan=0.28, t_check=B(bt), hum=0.002, tag='shaker')

    def brushes(b0, b1, vel, gdb):
        for e in range(int(round(b0 * 2)), int(round(b1 * 2))):
            bt = e / 2.0
            v = vel * (1.0 if e % 2 == 0 else 0.7)
            R.put('perc', MS.brush(vel=v, length=0.2, seed=e), B(bt), gain_db=gdb, pan=-0.22, tag='brush')

    brushes(4, 8, 0.42, -19.0)                    # hook bar 1
    shaker16(8, 18, 0.62, -20.0)                  # list
    brushes(18, 32, 0.45, -18.5)                  # warm
    shaker16(32, 36, 0.5, -21.0, step=2)          # pre-lift (8ths)
    shaker16(36, 42, 0.64, -19.5)                 # lift
    shaker16(42, 48, 0.5, -21.0, step=2)          # end card (8ths)

    # ---------------------------------------------------------------- UKE: staccato picked figure (hook, end card)
    uke_fig = {0: [65, 72, 69, 72, 67, 72, 69, 67], 4: [70, 74, 72, 74], 6: [67, 72, 65, 67],
               44: [70, 74, 72, 74], 46: [67, 72, 65, 67]}
    for b0, notes in uke_fig.items():
        for e, nt in enumerate(notes):
            bt = b0 + 0.5 * e
            v = 0.58 if e % 2 == 0 else 0.46
            x = MS.karplus_strong(nt, dur=0.2, vel=v, kind='uke', pluck=0.28, damping=0.55, release=0.08,
                                  seed=int(bt * 4))
            R.put('uke', x, B(bt), gain_db=-12.5 if b0 < 8 else -15.0, pan=0.3 * (1 if e % 2 else -1),
                  tag='uke')

    # ---------------------------------------------------------------- GUITAR: strums (list, pre-lift, lift, end)
    def strum_at(bt, direction, vel, dur_beats, gdb, spread=0.011):
        k, c = chord_at(bt)
        gv = list(c[4])
        if direction == 'up':
            gv = gv[-4:]
        x = MS.strum(gv, dur=B(dur_beats), vel=vel, direction=direction, spread=spread, kind='nylon', width=0.55,
                     seed=int(bt * 8))
        span_s = spread * (len(gv) - 1)
        sup = [h for h, _, al in HEROES if abs(B(bt) - h) <= 0.012]
        if not (clear(B(bt)) and clear(B(bt) + span_s, ignore=sup)):
            R.skipped.append((round(B(bt), 3), 'gtr', 'strum'))
            return
        R.put('gtr', x, B(bt), gain_db=gdb, pan=0.3, check=False, tag='strum %s' % direction)

    for bt, dr in LIST_STRUMS:
        v = (0.66 if bt % 4 == 0 else 0.6) if dr == 'down' else 0.5
        strum_at(bt, dr, v, 1.3 if dr == 'down' else 0.45, -13.5 if dr == 'down' else -14.5)
    for off, dr, v in ((32, 'down', 0.5), (33.5, 'up', 0.4), (34, 'down', 0.52), (35, 'up', 0.42),
                       (35.5, 'up', 0.45)):
        strum_at(off, dr, v, 1.2 if dr == 'down' else 0.45, -14.0)
    for bt, dr, v in ((37.5, 'up', 0.5), (38, 'down', 0.72), (38.75, 'up', 0.5), (39, 'down', 0.6),
                      (39.5, 'up', 0.52), (40, 'down', 0.68), (40.5, 'up', 0.5), (41, 'down', 0.66),
                      (41.5, 'up', 0.52)):
        strum_at(bt, dr, v, 0.9 if dr == 'down' else 0.4, -14.0 if dr == 'down' else -15.5)
    for bt, dr, v, db_ in ((42, 'down', 0.66, 1.4), (43.5, 'up', 0.45, 0.45), (44, 'down', 0.6, 1.4),
                           (45.5, 'up', 0.42, 0.45), (46, 'down', 0.58, 0.9), (47, 'down', 0.56, 0.9),
                           (48, 'down', 0.62, 3.6)):
        strum_at(bt, dr, v, db_, -15.0)

    # nylon picked arpeggio (warm section): quarter notes, long ring
    pat = [0, 2, 3, 1]
    for b in range(18, 32):
        bt = b if clear(B(b)) else b + 0.5          # a blocked beat moves to its 'and' (or is skipped)
        k, c = chord_at(bt)
        gv = list(c[4])
        nt = gv[pat[(b - 18) % 4] % len(gv)]
        x = MS.karplus_strong(nt, dur=B(1.6 - (bt - b)), vel=0.5 + 0.08 * (b % 2 == 0), kind='nylon', t60=2.2,
                              pluck=0.3, damping=0.5, release=0.2, seed=b)
        R.put('gtr', x, B(bt), gain_db=-11.5, pan=-0.3 if b % 2 else 0.25, tag='arp')

    # ---------------------------------------------------------------- MALLETS (marimba) + GLOCK: gaps + accents
    def mar(note, bt, vel=0.62, gdb=-10.0, pan=0.0, hard=0.45, decay=1.0, t=None):
        tt = B(bt) if t is None else t
        R.put('mallet', MS.marimba(note, vel=vel, hardness=hard, decay=decay, seed=int(tt * 100)), tt,
              gain_db=gdb, pan=pan, tag='marimba %s' % MS.note_name(MS.midi(note), True))

    def glk(note, bt, vel=0.5, gdb=-17.0, pan=0.0, decay=1.0):
        R.put('glock', MS.glockenspiel(note, vel=vel, hardness=0.55, decay=decay, seed=int(bt * 100)), B(bt),
              gain_db=gdb, pan=pan, tag='glock %s' % note)

    # M1 hook "question" (VO gap 4.53-5.78): F6 A6 C7 G6 (glock), marimba an octave down
    for bt, nt, v in ((8.0, 'F6', 0.5), (8.25, 'A6', 0.44), (8.75, 'C7', 0.5), (9.0, 'G6', 0.46)):
        glk(nt, bt, v, -15.5, pan=0.2, decay=0.6)
        mar(MS.midi(nt) - 12, bt, 0.5, -15.0, pan=-0.15)
    # stamp accents: low marimba dyads (support the stamps, rising top note C4 D4 E4)
    for t_hit, notes in ((5.70, ('F3', 'C4')), (7.50, ('Bb3', 'D4')), (8.70, ('C4', 'E4'))):
        for nt in notes:
            mar(nt, None, 0.72, -9.5, pan=0.0, hard=0.4, t=t_hit)
    # answer to the oven ding (C7) in the gap 9.52-11.2: C6 A5 E5
    for bt, nt in ((16.75, 'C6'), (17.0, 'A5'), (17.25, 'E5')):
        mar(nt, bt, 0.55, -12.0, pan=0.2)
    # M2 hook (VO gap 19.98-21.50): F5 A5 C6 G5 E5, glock doubling softly
    for bt, nt, v in ((33.5, 'F5', 0.6), (33.75, 'A5', 0.55), (34.25, 'C6', 0.6), (34.5, 'G5', 0.55),
                      (35.0, 'E5', 0.52)):
        mar(nt, bt, v, -12.0, pan=-0.12)
        glk(MS.midi(nt) + 12, bt, 0.38, -20.5, pan=0.25, decay=0.6)
    # lift run (VO gap 23.85-25.35): D5 F5 A5 | G5 E5 G5 Bb5 -> A5 on the end card (25.20)
    for bt, nt, v in ((40.0, 'D5', 0.55), (40.25, 'F5', 0.5), (40.5, 'A5', 0.56), (41.0, 'G5', 0.55),
                      (41.25, 'E5', 0.5), (41.5, 'G5', 0.55), (41.75, 'Bb5', 0.58), (42.0, 'A5', 0.62)):
        mar(nt, bt, v, -13.5, pan=0.12)
    # M3 end-card "answer" (after the CTA, 29.63-): F6 A6 C7 F6 (glock), marimba an octave down
    for bt, nt, v in ((49.5, 'F6', 0.5), (49.75, 'A6', 0.45), (50.25, 'C7', 0.5), (50.5, 'F6', 0.5)):
        glk(nt, bt, v, -18.0, pan=0.2, decay=1.8)
        mar(MS.midi(nt) - 12, bt, 0.52, -14.5, pan=-0.15, decay=1.8)

    # ---------------------------------------------------------------- FELT PIANO: warm section + end card
    def piano_chord(notes, t, vel=0.45, gdb=-9.0, tail=3.0, dur=None, roll=0.012, check=True):
        # every rolled note is checked: on a hit, every note must stay within 12 ms of it (one gesture);
        # otherwise every note must be clear (no hit 12-60 ms away)
        sup = [h for h, _, al in HEROES if abs(t - h) <= 0.012 and al == 'hit']
        ok = all((clear(t + roll * i, ignore=sup) and all(abs(t + roll * i - h) <= 0.012 for h in sup))
                 if i else clear(t) for i in range(len(notes)))
        if check and not ok:
            R.skipped.append((round(t, 3), 'keys', 'piano chord'))
            return
        for i, nt in enumerate(sorted(notes)):
            x = MS.felt_piano(nt, dur=dur or B(2), vel=vel * (1.0 - 0.04 * i), pedal=True, felt=0.9, tail=tail,
                              seed=int(t * 10) + i)
            R.put('keys', x, t + roll * i, gain_db=gdb, pan=-0.15 + 0.1 * i, check=False, hum=0,
                  tag='piano %s' % MS.note_name(nt, True))

    # blocks 1 / 2 (11.10 / 11.70) land 40 ms after their swishes (heroes): left to the SFX
    piano_chord(CHORDS[9][3], 12.30, 0.38, tail=4.0, roll=0.0035)   # block 3 STABILITY (F/A), same instant
    piano_chord(CHORDS[10][3], B(23.5), 0.42)                 # Dm7 anticipation in the VO gap (14.10)
    piano_chord(CHORDS[11][3], B(28), 0.36)                   # Bbmaj7 (16.80)
    piano_chord(CHORDS[12][3], B(30), 0.42)                   # C7sus4 in the VO gap (18.00)
    R.put('keys', MS.felt_piano(72, dur=B(1), vel=0.4, pedal=True, tail=2.5, seed=77), B(30.25), gain_db=-10,
          pan=0.2, tag='piano C5')
    piano_chord(CHORDS[13][3], B(32), 0.38)                   # Gm7 (19.20)
    piano_chord(CHORDS[14][3], B(34), 0.4)                    # Am7 (20.40)
    piano_chord(CHORDS[19][3], B(42), 0.46, roll=0.0035)       # Fadd9 end card (25.20, light switch)
    piano_chord(CHORDS[20][3], B(44), 0.38)                   # Bbmaj7
    piano_chord(CHORDS[21][3], B(46), 0.36, dur=B(1))         # Csus4
    piano_chord(CHORDS[22][3], B(47), 0.36, dur=B(1))         # C
    piano_chord((53, 60, 65, 67, 69), B(48), 0.36, tail=5.0, dur=B(3.5))   # final F(add9)

    # ---------------------------------------------------------------- FX: reverse swells into the lift / end card
    R.put('fx', MS.reverse_swell(1.2, vel=0.55, notes=[58, 62, 65, 72], seed=5), B(36) - 1.2, gain_db=-19.0,
          check=False, tag='swell -> lift')
    R.put('fx', MS.reverse_swell(0.6, vel=0.45, notes=[60, 65, 67, 69], seed=6), B(42) - 0.6, gain_db=-21.0,
          check=False, tag='swell -> end card')
    return R


# ============================================================================================ mix
def speech_env(lead=0.08, tail=0.0, ramp_in=0.06, ramp_out=0.08):
    """0..1 envelope: 1 while a VO line is spoken (cue start - lead .. end + tail), raised-cosine ramps (in before
    the start, out after the end). tail 0: the cue end already trails the speech, and a gap note struck right
    after a line must not be caught by the ramp."""
    t = np.arange(N) / SR
    e = np.zeros(N)
    for c in VO:
        a, b = c['start'] - lead, c['end'] + tail
        u = np.clip(np.minimum((t - (a - ramp_in)) / ramp_in, ((b + ramp_out) - t) / ramp_out), 0.0, 1.0)
        e = np.maximum(e, 0.5 - 0.5 * np.cos(np.pi * u))
    return e


_ENV = {}


def env_cached():
    if 'e' not in _ENV:
        _ENV['e'] = speech_env()
    return _ENV['e']


def choke(x, t, layer):
    """Per-event speech choke: the event's gain follows SPEECH_DB[layer] * (running max of the speech envelope
    over the event), so a note struck in a gap is pulled down when the next line starts and stays down (a
    ringing tail never swells back up when the line ends)."""
    db = SPEECH_DB.get(layer, 0.0)
    if not db:
        return x
    e = env_cached()
    i0 = int(round(t * SR))
    n = len(x)
    seg = np.zeros(n)
    a, b = max(0, i0), min(N, i0 + n)
    if b > a:
        seg[a - i0:b - i0] = e[a:b]
    g = A.undb(db * np.maximum.accumulate(seg))
    return x * (g[:, None] if x.ndim == 2 else g)


_BAND_SOS = signal.butter(2, [800.0, 5000.0], 'bandpass', fs=SR, output='sos')
_LOWMID_SOS = signal.butter(2, [280.0, 800.0], 'bandpass', fs=SR, output='sos')


def speech_dip(x, e, depth_db=12.0, level_db=2.0, sos=None):
    """Zero-phase 0.8-5 kHz band cut (or the band of `sos`) of depth_db (and level_db overall) while e = 1."""
    band = signal.sosfiltfilt(_BAND_SOS if sos is None else sos, x, axis=0)
    k = 1.0 - 10.0 ** (-depth_db / 20.0)
    g = 10.0 ** (-level_db * e / 20.0)
    return (x - (e * k)[:, None] * band) * g[:, None]


def mono_low(x, fc=150.0):
    """High-pass the side channel (zero phase): the low end is mono."""
    m, s = 0.5 * (x[:, 0] + x[:, 1]), 0.5 * (x[:, 0] - x[:, 1])
    s = signal.sosfiltfilt(signal.butter(2, fc, 'highpass', fs=SR, output='sos'), s)
    return np.stack([m + s, m - s], 1)


def zpf_hp(x, fc, order=2):
    return signal.sosfiltfilt(signal.butter(order, fc, 'highpass', fs=SR, output='sos'), x, axis=0)


# bus trims (dB) on top of the per-event gains: the balance measured as per-layer integrated LUFS
TRIM = dict(pad=8.0, sub=-6.0, kick=-1.0, keys=2.0, gtr=9.0, uke=8.5, mallet=2.0, glock=2.0, perc=8.0, pluckb=4.0,
            fx=5.0)
# extra level (dB) while a VO line is spoken, per layer, applied per event by choke(): the ringing / bright
# layers are choked under the voice (a glock note struck in a gap is pulled down when the next line starts)
SPEECH_DB = dict(glock=-14.0, mallet=-6.0, uke=-5.0, gtr=-6.0, perc=-6.0, keys=-8.0, pad=-4.0, fx=-10.0, sub=-3.0)


def mixdown(R):
    e = env_cached()
    T = {k: v.buf * A.undb(TRIM.get(k, 0.0)) for k, v in R.T.items()}
    T['pad'] = zpf_hp(T['pad'], 150.0)
    T['keys'] = zpf_hp(T['keys'], 120.0)
    T['gtr'] = zpf_hp(T['gtr'], 130.0)
    T['uke'] = zpf_hp(T['uke'], 200.0)
    T['mallet'] = zpf_hp(T['mallet'], 140.0)
    T['glock'] = zpf_hp(T['glock'], 200.0)
    T['perc'] = zpf_hp(T['perc'], 200.0)
    T['fx'] = zpf_hp(T['fx'], 180.0)
    T['pluckb'] = zpf_hp(T['pluckb'], 60.0)
    T['sub'] = zpf_hp(T['sub'], 32.0)
    T['kick'] = zpf_hp(T['kick'], 30.0)
    kick = T['kick']
    # gentle kick pump on the pad / guitars and on the bass (same key, same gain curve)
    tonal = MS.duck(T['pad'] + T['gtr'], kick, depth_db=3.0, attack=0.004, release=0.17)
    sub_d = MS.duck(T['sub'] + T['pluckb'], kick, depth_db=3.0, attack=0.004, release=0.17)
    sends = (MS.reverb_send(T['pad'] + T['keys'], 'hall', wet_db=-14.0, hp_hz=220.0)
             + MS.reverb_send(T['mallet'] + T['glock'] + T['gtr'] + T['uke'], 'plate', wet_db=-16.0, hp_hz=250.0)
             + MS.reverb_send(T['perc'], 'room', wet_db=-17.0, hp_hz=300.0))
    # everything in / near the speech band gets the speech dip; the sub, bass pluck and kick bypass it
    upper = tonal + T['keys'] + T['uke'] + T['mallet'] + T['glock'] + T['perc'] + T['fx'] + sends
    upper = speech_dip(upper, e)
    upper = speech_dip(upper, e, depth_db=6.0, level_db=0.0, sos=_LOWMID_SOS)   # 280-800 Hz low-mid dip
    mix = upper + sub_d + kick
    mix = A.hp(mix, 25.0, 2)
    mix = mono_low(mix, 150.0)
    mix = MS.bus_comp(mix, thresh_db=-18.0, ratio=1.6, knee_db=6.0, attack=0.012, release=0.2)
    mix = MS.tilt_eq(mix, 0.5, 900.0)
    mix = MS.fade_out(mix, FADE_T1 - FADE_T0, end=FADE_T1)
    mix[int(round(FADE_T1 * SR)):] = 0.0
    nf = int(0.001 * SR)                          # 1 ms start ramp: sample 0 exactly 0 (beat 1 stays at 0.000)
    mix[:nf] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(nf) / nf))[:, None]
    y, info = MS.normalise_lufs(mix, target=-16.0, tp_ceiling=-1.2)
    y[int(round(FADE_T1 * SR)):] = 0.0
    return y, info, T


# ============================================================================================ measurements
def band_db(x, lo=1000.0, hi=4000.0, win=0.1, hop=0.05):
    sos = signal.butter(4, [lo, hi], 'bandpass', fs=SR, output='sos')
    y = signal.sosfiltfilt(sos, A._st(x).mean(1))
    nw, nh = int(win * SR), int(hop * SR)
    c = np.concatenate([[0.0], np.cumsum(y * y)])
    st = np.arange(0, len(y) - nw, nh)
    return st, 10 * np.log10((c[st + nw] - c[st]) / nw + 1e-20)


def music_onsets(x, thr_db=6.0, hp_hz=300.0, floor_db=30.0):
    """Onsets of the clean music: the 300 Hz+ power (3 ms smoothing, 0.5 ms hop) of the next 8 ms vs the mean
    of a 40 ms window ending 10 ms before (a transient vs its context, so chorus-beating notches do not count),
    peaks >= thr_db, within floor_db of the 99.5th-percentile power. Returns [(t_s, strength_db)]."""
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    y = A.hp(A._st(x).mean(1), hp_hz, 2)
    hop = int(0.0005 * SR)
    p = uniform_filter1d(y * y, int(0.003 * SR))[::hop]
    n_pre, gap, n_post = 80, 20, 16
    c = np.concatenate([[0.0], np.cumsum(p)])
    idx = np.arange(len(p))
    a = np.clip(idx - gap - n_pre, 0, len(p))
    b = np.clip(idx - gap, 0, len(p))
    pre = (c[b] - c[a]) / np.maximum(b - a, 1)
    post = maximum_filter1d(p, n_post, origin=-(n_post // 2))
    s = 10 * np.log10((post + 1e-14) / (pre + 1e-14))
    lvp = 10 * np.log10(post + 1e-14)
    fl = 10 * np.log10(np.percentile(p, 99.5)) - floor_db
    out = []
    i = n_pre + gap
    while i < len(s):
        if s[i] >= thr_db and lvp[i] > fl:
            j = i + int(np.argmax(s[i:i + 30]))
            out.append((j * hop / SR, float(s[j])))
            i = j + 50
        else:
            i += 1
    return out


def transient_check(clean, log):
    """Audio check of the SFX rule: music onsets (music_onsets) whose time lies 12-60 ms from a 'hit'-aligned
    hero, after removing the detector's timing bias (median offset to the logged event times). An onset that
    belongs to an event logged as a same-instant support (strings 2-5 of a strum on a hit) is listed apart."""
    ons = music_onsets(clean)
    ev = np.array(sorted(t for t, *_ in log))
    offs = []
    for t, r in ons:
        j = np.searchsorted(ev, t)
        cand = [ev[k] for k in (j - 1, j) if 0 <= k < len(ev)]
        if cand:
            d = min(cand, key=lambda e: abs(t - e))
            if abs(t - d) < 0.015:
                offs.append(t - d)
    bias = float(np.median(offs)) if offs else 0.0
    sup_t = np.array(sorted(t for t, _, _, _, sup in log if sup)) if any(e[4] for e in log) else np.array([])
    bad, sup_bad = [], []
    hits = [(h, n) for h, n, al in HEROES if al == 'hit']
    for t, r in ons:
        tc = t - bias
        for h, n in hits:
            if 0.012 < abs(tc - h) <= 0.060:
                own = len(sup_t) and np.min(np.abs(sup_t - h)) <= 0.012 and 0 <= tc - h <= 0.06
                (sup_bad if own else bad).append([round(tc, 3), round(r, 1), round(h, 3), n])
    return dict(onsets=len(ons), bias_ms=round(bias * 1000, 1), matched=len(offs), violations=bad,
                support_tails=sup_bad)


def log_check(log):
    """The SFX rule on the event log (exact placement times)."""
    hits = [h for h, _, al in HEROES if al == 'hit']
    bad = []
    for t, layer, tag, chk, sup in log:
        if not chk:
            continue
        near = [abs(t - h) for h in hits if 0.012 < abs(t - h) <= 0.060]
        if near and not sup:
            bad.append((t, layer, tag, round(min(near) * 1000, 1)))
    return bad


def main():
    import time
    t0 = time.time()
    R = build()
    clean, ninfo, T = mixdown(R)
    assert len(clean) == N
    A._write_wav(OUT_CLEAN, clean, 24)
    st = MS.load_reel_stems('anim1')
    bed, m = MS.render_bed(clean, st['vo'], st['sfx'], st['mix'])
    A._write_wav(OUT_BED, bed, 24)
    # 10 Hz high-pass on the delivered VO / SFX stems: removes their inherited DC (-4e-4) from the with-music mix
    mix, rep = MS.master_withmusic(A.hp(st['vo'], 10.0, 2), A.hp(st['sfx'], 10.0, 2), bed)
    A._write_wav(OUT_MIX, mix, 24)
    os.makedirs(REEL_DIR, exist_ok=True)
    mp3b = MS.write_mp3(OUT_BED, MP3_BED, TITLE + ' (ducked bed)')
    mp3c = MS.write_mp3(OUT_CLEAN, MP3_CLEAN, TITLE + ' (clean, full level)')
    prev = None
    if os.path.exists(PREVIEW_IN):
        MS.make_preview(PREVIEW_IN, OUT_MIX, PREVIEW_OUT)
        prev = PREVIEW_OUT

    # ---- measurements
    rd = lambda p: A.read_wav(p)[0]                                          # noqa: E731
    cw, bw, mw = rd(OUT_CLEAN), rd(OUT_BED), rd(OUT_MIX)
    q = MS.qa(cw)
    sp = MS.speech_mask(st['vo'])
    s_idx, vo_b = band_db(rep['stems']['vo'])
    _, mu_b = band_db(rep['stems']['music'])
    nw = int(0.1 * SR)
    frac = np.array([sp[i:i + nw].mean() for i in s_idx])
    sel = frac > 0.5
    diff = (vo_b - mu_b)[sel]
    act = sel & (vo_b > np.percentile(vo_b[sel], 95) - 20.0)     # frames where the voice is actually sounding
    dact = (vo_b - mu_b)[act]
    # masking: 100 ms windows (50 ms hop), 300 Hz-4 kHz, music within 6 dB of the voice; all speech windows and
    # the windows where the voice is within 20 / 25 dB of its p95 band level
    _, vo_w = band_db(rep['stems']['vo'], 300.0, 4000.0)
    _, mu_w = band_db(rep['stems']['music'], 300.0, 4000.0)
    dw, p95w = vo_w - mu_w, np.percentile(vo_w[sel], 95)
    masking = dict(speech_windows=int(sel.sum()), within6=int((dw[sel] < 6).sum()),
                   within6_pct=round(float(100 * (dw[sel] < 6).mean()), 1))
    for r_ in (20, 25):
        a_ = sel & (vo_w > p95w - r_)
        masking['voice_p95-%d' % r_] = '%d/%d (%.1f%%)' % ((dw[a_] < 6).sum(), a_.sum(), 100 * (dw[a_] < 6).mean())
    tc = transient_check(cw, R.log)
    lay_on = {k: music_onsets(v) for k, v in T.items() if np.any(v)}
    for v in tc['violations']:
        v.append([k for k, ons in lay_on.items() if any(abs(t - v[0]) < 0.012 for t, _ in ons)])
    tc['transient_layer_violations'] = [v for v in tc['violations'] if set(v[-1]) - {'pad', 'sub', 'fx'}
                                        or not v[-1]]
    secl = {nm: round(A.loudness(cw[int(B(b0) * SR):int(B(b1) * SR)]), 1) for nm, b0, b1 in SECTIONS}
    probes = []
    for pth in (MP3_BED, MP3_CLEAN):
        pr = MS._probe(pth)
        st0 = (pr.get('streams') or [{}])[0]
        probes.append(dict(file=os.path.basename(pth), codec=st0.get('codec_name'), channels=st0.get('channels'),
                           sample_rate=st0.get('sample_rate'), bit_rate=st0.get('bit_rate'),
                           duration=pr.get('format', {}).get('duration'),
                           title=(pr.get('format', {}).get('tags') or {}).get('title')))
    if prev:
        pr = MS._probe(prev)
        prev_streams = [(x.get('codec_name'), x.get('sample_rate'), x.get('bit_rate'), x.get('duration'))
                        for x in pr.get('streams', [])]
    out = dict(
        render_s=round(time.time() - t0, 1),
        bounds={k: round(v, 3) for k, v in BOUNDS.items()},
        clean=dict(samples=len(cw), dur=len(cw) / SR, lufs=round(A.loudness(cw), 2),
                   true_peak=round(A.true_peak(cw), 2),
                   peak_dbfs=round(float(A.db(np.abs(cw).max())), 2),
                   last20ms_dbfs=round(float(A.db(np.abs(cw[-int(0.02 * SR):]).max() + 1e-12)), 1),
                   first_sample_abs=float(np.abs(cw[0]).max()), normalise=ninfo,
                   dc=q.get('dcrep'), clicks={k: q['clicks'][k] for k in ('clean', 'count', 'worst_ratio')}),
        beat_grid=MS.beat_grid_check(cw, BPM),
        bed=dict(m, file_lufs=round(A.loudness(bw), 2), file_true_peak=round(A.true_peak(bw), 2)),
        withmusic=dict({k: v for k, v in rep.items() if k != 'stems'}, file_lufs=round(A.loudness(mw), 2),
                       file_true_peak=round(A.true_peak(mw), 2)),
        speech_band_100ms=dict(frames=int(sel.sum()), median_db=round(float(np.median(diff)), 1),
                               p10_db=round(float(np.percentile(diff, 10)), 1), min_db=round(float(diff.min()), 1),
                               active_frames=int(act.sum()), active_median_db=round(float(np.median(dact)), 1),
                               active_p10_db=round(float(np.percentile(dact, 10)), 1),
                               active_min_db=round(float(dact.min()), 1)),
        masking_300_4k=masking, sections_lufs=secl, mp3_probe=probes,
        hero_rule=dict(log_violations=log_check(R.log), audio=tc),
        mp3=[mp3b, mp3c], preview=dict(path=prev, mb=round(os.path.getsize(prev) / 1e6, 2),
                                       streams=prev_streams) if prev else None,
        events=len(R.log), skipped=R.skipped)
    for k, tr in sorted(T.items()):
        x = tr
        if np.any(x):
            out.setdefault('layers_lufs', {})[k] = round(A.loudness(x), 1)
    sk = out.pop('skipped')
    print(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
    print('skipped (hero hit within 12-60 ms): ' + ', '.join('%.3f %s/%s' % s_ for s_ in sk))
    out['skipped'] = sk
    return out


if __name__ == '__main__':
    main()
