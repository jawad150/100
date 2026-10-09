"""reel1_vo_music.py: original background music for REEL 1 "Could You?" (VO version, reel1_vo, 49.5 s).

    cd pipeline/fostering && python3 reel1_vo_music.py        (deterministic: seeded; renders every file below)

Synthesised with music_synth.py (MS) + audio.py (A): numpy / scipy only, no samples. Emotional and cinematic but
hopeful: tender A minor in the hook and the question, a light pulse under the eligibility checklist, warmer and
moving in the support dock, the emotional peak in C major on the slow-motion payoff, a resolving end card.
Background music under a voice-over: no lead melody while the voice speaks (the felt-piano figures sit in the VO
gaps). While a line is spoken the bus above the bass gets a zero-phase 0.8-5 kHz dip (SPEECH_DIP_DB) and each
event is choked per layer (SPEECH_DB); the choke of a struck event is monotonic, so a ringing tail never swells
back up when the line ends.

KEY A minor -> C major (payoff, end card) | 120 BPM | beat n = n * 0.5 s from 0.000 (beat 1 at 0.000 s) | bar =
2.0 s | 99 beats = 24 bars + 3 beats = 49.5 s exactly. Section boundaries are computed in OUTPUT time from the VO
module (V = reel1_vo, V.SRC = reel1) and snapped to the nearest bar line (within half a beat) or else the nearest
beat (sections()):
    V.out_time(T_Q)    =  4.767 (smash to the question; impact_big + sub_drop)  -> mid-bar: beat 10 =  5.00
    V.out_time(T_LIST) =  8.267 (whip down into the checklist)                  -> mid-bar: beat 17 =  8.50
    V.out_time(T_DOCK) = 24.000 (whip pan into the support dock)                -> bar 12          = 24.00
    V.out_time(T_PAY)  = 37.500 (zoom-through into the slow-motion payoff)      -> mid-bar: beat 75 = 37.50
    V.out_time(T_END)  = 41.767 (logo sting, impact_big)                        -> bar 21          = 42.00
    ticks V.out_time(TICKS) = 10.764 12.247 14.264 16.514 18.764; ring pop 20.998; toast V.out_time(TOAST_T) = 21.50

MUSIC MAP (output seconds; VO = V.vo_cues(); hero hit = V.cues() with gain_db >= -6)
 section      | bars (beats)      | t0-t1 s     | edit events                    | music events
 -------------+-------------------+-------------+--------------------------------+------------------------------------
 A hook       | 0-2.5 (b0-10)     | 0.00-5.00   | heartbeat 0.00 (lub/dub); word | Pad Am(add9) swells in from 0 (no
              |                   |             | slams 0.50 / 1.756 / 2.989 /   | transient under the heartbeat). Felt
              |                   |             | 3.50 (flash + impact) with     | piano chords ON the four slams (same
              |                   |             | whips; air_zoom 3.25; VO "A    | instant): Am(add9) / Fmaj7 / C(add9)
              |                   |             | safe home." 0.58-1.63,         | / Dm(add9), sub A1 F1 C2 D2. Low
              |                   |             | "Everyday care." 1.85-2.99, "A | pulse: dark plucked 8ths from beat 1
              |                   |             | place to belong." 3.14-4.35;   | (0.50) to 4.25. The music breathes
              |                   |             | smash + impact_big + sub_drop  | out (pulse, sub, piano released by
              |                   |             | 4.767, whoosh 4.907            | 4.6) and leaves the smash to the SFX
 B question   | 2.5-4.25 (b10-17) | 5.00-8.50   | ? lands (glass_tap) 5.267; VO  | Held suspension E7sus4: pad swells
              |                   |             | "Could you be a foster carer?" | in (1.0 s) with a slow filter swell
              |                   |             | 5.52-7.03, YOU slam 5.767,     | (700 -> 1500 Hz), soft E2/B2 piano
              |                   |             | ui_tick 6.017; whip down 8.267 | ground at 5.00, sustained sub E2, a
              |                   |             |                                | high air pad (E5 A5 B5) blooms into
              |                   |             |                                | the gap. Motif M1 (felt piano) in the
              |                   |             |                                | VO gap: E5 D5 E5 A5 7.25-8.00, the A5
              |                   |             |                                | (the sus 4th) rings over the whip
 C1 checklist | 4.25-8 (b17-32)   | 8.50-16.00  | glass_tap 8.767; VO "Am I      | Am(add9) Fmaj9 | C(add9) | G6 (bar
              |                   |             | eligible to foster?" 8.67-     | lines 10 / 12 / 14). Soft cinematic
              |                   |             | 10.37; ticks (ui_click +       | kick on every beat from 8.50, light
              |                   |             | check_ding) 10.764 12.247      | pulse (plucked 8ths on the root), sub
              |                   |             | 14.264, each followed by its   | roots. One subtle accent per tick,
              |                   |             | line (spare bedroom / time and | on the tick: a low felt-piano dyad
              |                   |             | flexibility / single or in a   | (top note rising A3 C4 D4 E4 F4) plus
              |                   |             | relationship)                  | an accented pulse note (+6..+8 ms
              |                   |             |                                | from the grid, i.e. within 6 ms of
              |                   |             |                                | the tick)
 C2 checklist | 8-10.75 (b32-43)  | 16.00-21.50 | ticks 16.514 18.764 (rent or   | Am7 | Fmaj7 | Dm9. Adds soft off-beat
              |                   |             | own / no experience); ring pop | hats, pulse alternates root / fifth,
              |                   |             | 20.998                         | sub re-strikes on beat 3, pad opens
 C3 toast     | 10.75-12 (b43-48) | 21.50-24.00 | toast "You could be a great    | Toast 21.50 (beat 43, same instant):
              |                   |             | fit" chime 21.50, VO 21.55-    | C/E piano chord + kick, air pad C5 E5
              |                   |             | 23.10                          | G5 blooms, shaker 16ths; Dm7 (22.0)
              |                   |             |                                | E7sus4 (23.0) E7 (23.5). Pickup in
              |                   |             |                                | the VO gap: E5 D5 B4 (23.25-23.75)
              |                   |             |                                | -> C5 on the dock downbeat (24.00)
 D1 dock      | 12-15 (b48-60)    | 24.00-30.00 | whip pan 24.00 + card_slides   | Deceptive cadence E7 -> Fmaj9 on the
              |                   |             | 24.125/.25/.375; VO "Support   | whip (warm surprise). Fmaj9 | C/E |
              |                   |             | is part of the role." 24.30-   | Dm9: warmer pad (wider, filter sweep)
              |                   |             | 26.12, "Full training." 26.55- | plucked arpeggio in 8ths, kick on the
              |                   |             | 27.70, "Ongoing support."      | beat, sub with motion (beat 1 + the
              |                   |             | 28.55-29.92; tile focus        | 'and' of 3), off-beat hats, shaker
              |                   |             | (hover + click) 26.148/26.498, | 8ths. Piano gap figures G5 A5 F5
              |                   |             | 28.38/28.50, 30.38/30.50       | (27.75-28.25), E5 C5 (30.0-30.25)
 D2 dock      | 15-18 (b60-72)    | 30.00-36.00 | VO "And a weekly allowance,    | Am7 | Fmaj7 | Dm9 C/E. More motion:
              |                   |             | from 447.60 a week per child." | arpeggio in 16ths (filter opening),
              |                   |             | 30.55-36.32                    | shaker 16ths, brushes on 2 and 4
 D3 build     | 18-18.75 (b72-75) | 36.00-37.50 | VO gap 36.32-37.75             | Gsus4 -> G: the kick stops after
              |                   |             |                                | 36.0, shaker crescendo, reverse
              |                   |             |                                | swell (C(add9)) into 37.508, rising
              |                   |             |                                | piano pickup G4 A4 B4 D5 (36.5-37.25)
 E payoff     | 18.75-21 (b75-84) | 37.50-42.00 | zoom-through: air_zoom +       | The emotional peak in C major at
              |                   |             | flash_hit 37.50, impact_soft   | 37.508 (8 ms late: within 12 ms of
              |                   |             | 37.52; VO "Open your home."    | both the flash and the impact):
              |                   |             | 37.75-38.82, "Change a child's | C(add9) piano chord (top E5 = the
              |                   |             | life." 39.08-40.63 (slow-mo    | pickup's arrival), widest pad, low
              |                   |             | footage); riser 39.77-41.77;   | string pad, air pad, arpeggio 16ths,
              |                   |             | logo sting + impact_big 41.767 | half-time kick, sub C2 -> B1 -> A1 ->
              |                   |             |                                | F1 -> G1 with glides: C(add9) G/B
              |                   |             |                                | Am7 Fmaj7 Gsus4. Motif M2 (= M1 in
              |                   |             |                                | C) in the VO gap: E5 D5 E5 G5
              |                   |             |                                | 40.75-41.50 (stops before the sting)
 F end card   | 21-24.75 (b84-99) | 42.00-49.50 | wordmark 42.52; VO "Organic    | Resolves to the tonic: C(add9) (42.0)
              |                   |             | Fostering, rated Good by       | Fmaj9 (44.0) Gsus4 G (45.0-45.5)
              |                   |             | Ofsted." 42.52-45.91; CTA pop  | C(add9) (46.0, in the VO gap) held to
              |                   |             | 43.52; cursor click 46.258     | the end. Kick on 42 / 44 / 46 only,
              |                   |             | (hero); VO "Start your enquiry | arpeggio thins to 8ths and stops at
              |                   |             | today." 46.34-47.93; card      | 46.0, piano note on the CTA click
              |                   |             | holds to 49.5                  | (46.258). Motif M3, the answer, after
              |                   |             |                                | the last line: E5 D5 C5 (48.0-48.5).
              |                   |             |                                | Fade 47.60-49.45, zeros after 49.46
 Chords (beat: chord): 0 Am(add9) 3.5 Fmaj7 6 C(add9) 7 Dm(add9) | 10 E7sus4 | 17 Am(add9) 20 Fmaj9 24 C(add9)
 28 G6 32 Am7 36 Fmaj7 40 Dm9 43 C/E 44 Dm7 46 E7sus4 47 E7 | 48 Fmaj9 52 C/E 56 Dm9 60 Am7 64 Fmaj7 68 Dm9 70 C/E
 72 Gsus4 74 G | 75 C(add9) 78 G/B 80 Am7 82 Fmaj7 83 Gsus4 | 84 C(add9) 88 Fmaj9 90 Gsus4 91 G 92 C(add9).
 Voicings are hand voice-led (CHORDS); sub bass A1 / F1 / C2 / D2 / E2 / G1 / B1 (44-82 Hz).

INSTRUMENTS (all from MS): felt_piano (chords on the slams, tick accents, the motifs, gap figures), pad (wave
'warm', 5 voices, detune, chorus, slow filter swell / LFO sweep), pad 'tri' (high air layer), pad 'saw' (low
string layer, payoff and end card), pluck_synth 'warm' (low pulse, hook and checklist), pluck_synth 'saw'
(plucked arpeggio, dock to end card), sub_bass (glides in the payoff), soft_kick, hat, shaker, brush,
reverse_swell.
MIX: per-layer bus trims (TRIM); zero-phase high-pass on every layer except kick, sub and pulse (keys 120, pad 150,
low strings 120, arp 180, air 300, perc 200, fx 180 Hz); sends to hall (pad, air, low strings, keys) and plate
(arp, perc), high-passed at 220 / 260 Hz; gentle kick pump (3 dB) on the pad, arp, pulse and sub; side channel
high-passed at 150 Hz (mono low end); bus 25 Hz high-pass, bus_comp (-18 dB, 1.6:1), +0.5 dB tilt, then
-16 LUFS with <= -1.2 dBTP via MS.normalise_lufs.

SFX RULE: no music transient 12-60 ms from an SFX hero hit. Every transient event goes through place(): it may
move up to 8 ms off the grid (the humanise budget) so that every hero hit within 60 ms is within 12 ms (support on
the same instant: the slams, the ticks, the toast, the clicks, the payoff flash + impact pair); if no such time
exists the event is skipped and logged. Verified on the event log (log_check) and on the audio (transient_check).

DELIVERY (MS.render_bed / MS.master_withmusic, the chain shared by all five reels)
    <AUDIO>/reel1_vo_music.wav            clean, -16 LUFS, <= -1 dBTP, 48 kHz 24-bit, 2 376 000 samples
    <AUDIO>/reel1_vo_music_bed.wav        ducked (9 dB under the VO, 3 dB under the SFX) and levelled bed
    <AUDIO>/reel1_vo_withmusic_mix.wav    VO + SFX + bed mastered to -14 LUFS, <= -2.0 dBTP
    reel/organic_fostering/organic_fostering_reel1_vo_could_you_music.mp3 (bed) and ..._music_clean.mp3
    <scratchpad>/reel1_vo_music_preview.mp4   picture copied from reel1_vo_preview.mp4, plus the with-music mix
"""
import json
import os
import sys
import time

import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio as A  # noqa: E402
import music_synth as MS  # noqa: E402
import reel1_vo as V  # noqa: E402

SR = A.SR
NAME = 'reel1_vo'
BPM = float(V.BPM)                      # 120
DUR = float(V.DUR)                      # 49.5
N = int(round(DUR * SR))
BEAT = 60.0 / BPM                       # 0.5 s
BAR = 4 * BEAT
SEED = 4101
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT_CLEAN = os.path.join(A.AUDIO, NAME + '_music.wav')
OUT_BED = os.path.join(A.AUDIO, NAME + '_music_bed.wav')
OUT_MIX = os.path.join(A.AUDIO, NAME + '_withmusic_mix.wav')
REEL_DIR = os.path.join(REPO, 'reel', 'organic_fostering')
MP3_BED = os.path.join(REEL_DIR, 'organic_fostering_reel1_vo_could_you_music.mp3')
MP3_CLEAN = os.path.join(REEL_DIR, 'organic_fostering_reel1_vo_could_you_music_clean.mp3')
TITLE = 'Organic Fostering - reel1_vo_could_you - background music'
SCRATCH = '/tmp/claude-0/-home-user-100/bb73d22e-ad11-5aa0-a0b2-8033920f7c07/scratchpad'
PREVIEW_IN = os.path.join(SCRATCH, 'reel1_vo_preview.mp4')
PREVIEW_OUT = os.path.join(SCRATCH, 'reel1_vo_music_preview.mp4')

FADE_T0, FADE_T1 = 47.60, 49.45        # final fade (1.85 s); zeros after FADE_T1 (last 50 ms silent)


def B(n):
    """Beat n in output seconds."""
    return n * BEAT


# ============================================================================================ edit timing
SRC = V.SRC
BOUNDS = dict(question=V.out_time(SRC.T_Q), checklist=V.out_time(SRC.T_LIST), dock=V.out_time(SRC.T_DOCK),
              payoff=V.out_time(SRC.T_PAY), endcard=V.out_time(SRC.T_END))
TICKS = [V.out_time(t) for t in SRC.TICKS]
TOAST = V.out_time(SRC.TOAST_T)


def snap_beat(t):
    """Section start (in beats) for a boundary at t: the nearest bar line if it is within half a beat, else the
    nearest beat."""
    bar = round(t / BAR) * 4
    if abs(t - B(bar)) <= 0.5 * BEAT + 1e-9:
        return int(bar)
    return int(round(t / BEAT))


SEC_BEAT = {k: snap_beat(v) for k, v in BOUNDS.items()}
# the arrangement below is written for these section beats; a change in the VO edit must show up here
assert SEC_BEAT == dict(question=10, checklist=17, dock=48, payoff=75, endcard=84), SEC_BEAT
END_BEAT = int(round(DUR / BEAT))       # 99
SECTIONS = [  # name, beat0, beat1
    ('A hook', 0, 10), ('B question', 10, 17), ('C1 checklist', 17, 32), ('C2 checklist', 32, 43),
    ('C3 toast', 43, 48), ('D1 dock', 48, 60), ('D2 dock', 60, 72), ('D3 build', 72, 75), ('E payoff', 75, 84),
    ('F end card', 84, END_BEAT)]
VO = V.vo_cues()
CUES = V.cues()
HEROES = sorted((float(c['t']), c['name']) for c in CUES if c.get('gain_db', -99) >= -6)
HERO_T = np.unique(np.round([h for h, _ in HEROES], 4))


def place(t, hum=0.0):
    """Placement time for a transient whose grid time is t, or None. With no hero hit within 68 ms: t + hum.
    Otherwise the shift of at most 8 ms (the humanise budget) that brings every hero hit within 60 ms closest,
    accepted only if all of them end up within 12 ms (same-instant support)."""
    near = HERO_T[np.abs(HERO_T - t) <= 0.068]
    if not len(near):
        return t + hum
    best = None
    for k in range(-16, 17):
        c = t + 0.0005 * k
        nn = HERO_T[np.abs(HERO_T - c) <= 0.060]
        worst = float(np.max(np.abs(nn - c))) if len(nn) else 0.0
        if worst <= 0.012 and (best is None or (worst, abs(k)) < best[0]):
            best = ((worst, abs(k)), c)
    return None if best is None else best[1]


def in_speech(t, pad=0.05):
    return any(c['start'] - pad <= t <= c['end'] for c in VO)


# ============================================================================================ harmony
# beat, name, sub bass (MIDI), pad voicing (MIDI, voice-led)
CHORDS = [
    (0, 'Am(add9)', 33, (52, 57, 60, 64, 71)),
    (3.5, 'Fmaj7', 29, (53, 57, 60, 64, 69)),
    (6, 'C(add9)', 36, (52, 55, 60, 62, 67)),
    (7, 'Dm(add9)', 38, (53, 57, 62, 64, 69)),
    (10, 'E7sus4', 40, (52, 57, 59, 62, 64)),
    (17, 'Am(add9)', 33, (52, 57, 59, 60, 64)),
    (20, 'Fmaj9', 29, (53, 57, 60, 64, 67)),
    (24, 'C(add9)', 36, (52, 55, 60, 62, 67)),
    (28, 'G6', 31, (50, 55, 59, 62, 64)),
    (32, 'Am7', 33, (52, 57, 60, 64, 67)),
    (36, 'Fmaj7', 29, (53, 57, 60, 64, 69)),
    (40, 'Dm9', 38, (50, 53, 57, 60, 64)),
    (43, 'C/E', 40, (52, 55, 60, 64, 67)),
    (44, 'Dm7', 38, (53, 57, 60, 62, 65)),
    (46, 'E7sus4', 40, (52, 57, 59, 62, 64)),
    (47, 'E7', 40, (52, 56, 59, 62, 64)),
    (48, 'Fmaj9', 29, (53, 57, 60, 64, 67)),
    (52, 'C/E', 40, (52, 55, 60, 64, 67)),
    (56, 'Dm9', 38, (50, 53, 57, 60, 64)),
    (60, 'Am7', 33, (52, 57, 60, 64, 67)),
    (64, 'Fmaj7', 29, (53, 57, 60, 64, 69)),
    (68, 'Dm9', 38, (50, 53, 57, 60, 64)),
    (70, 'C/E', 40, (52, 55, 60, 64, 67)),
    (72, 'Gsus4', 31, (50, 55, 60, 62, 67)),
    (74, 'G', 31, (50, 55, 59, 62, 67)),
    (75, 'C(add9)', 36, (48, 55, 62, 64, 67, 72)),
    (78, 'G/B', 35, (47, 55, 62, 67, 71)),
    (80, 'Am7', 33, (45, 52, 60, 64, 67, 72)),
    (82, 'Fmaj7', 29, (53, 57, 60, 64, 69, 72)),
    (83, 'Gsus4', 31, (50, 55, 60, 62, 67, 72)),
    (84, 'C(add9)', 36, (48, 55, 60, 62, 64, 67)),
    (88, 'Fmaj9', 29, (53, 57, 60, 64, 67)),
    (90, 'Gsus4', 31, (50, 55, 60, 62, 67)),
    (91, 'G', 31, (50, 55, 59, 62, 67)),
    (92, 'C(add9)', 36, (48, 55, 60, 62, 64, 67)),
]


def chord_at(beat):
    """(index, chord tuple) sounding at `beat`."""
    k = max(i for i, c in enumerate(CHORDS) if c[0] <= beat + 1e-9)
    return k, CHORDS[k]


def span(k):
    """(beat0, beat1) of chord k."""
    return CHORDS[k][0], (CHORDS[k + 1][0] if k + 1 < len(CHORDS) else END_BEAT)


def section_of(beat):
    for name, b0, b1 in SECTIONS:
        if b0 <= beat + 1e-9 < b1:
            return name
    return SECTIONS[-1][0]


# ============================================================================================ speech handling
def speech_env(lead=0.08, tail=0.0, ramp_in=0.06, ramp_out=0.25):
    """0..1 envelope: 1 while a VO line is spoken (cue start - lead .. end + tail), raised-cosine ramps."""
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


# extra level (dB) while a VO line is spoken, per layer, applied per event. Struck layers hold the reduction
# (running max: a tail never swells back up); sustained layers follow the envelope.
SPEECH_DB = dict(keys=-4.0, air=-7.0, arp=-3.0, perc=-4.0, fx=-6.0, pulse=-1.5, pad=-1.5, low=-1.0, sub=-1.0)
HOLD = {'keys', 'arp', 'perc', 'fx', 'pulse'}
SPEECH_DIP_DB, SPEECH_DIP_LEVEL = 10.0, 1.5


def choke(x, t, layer):
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
    if layer in HOLD:
        seg = np.maximum.accumulate(seg)
    g = A.undb(db * seg)
    return x * (g[:, None] if x.ndim == 2 else g)


_BAND_SOS = signal.butter(2, [800.0, 5000.0], 'bandpass', fs=SR, output='sos')


def speech_dip(x, e, depth_db=SPEECH_DIP_DB, level_db=SPEECH_DIP_LEVEL):
    """Zero-phase 0.8-5 kHz band cut of depth_db (and level_db overall) while e = 1."""
    band = signal.sosfiltfilt(_BAND_SOS, x, axis=0)
    k = 1.0 - 10.0 ** (-depth_db / 20.0)
    g = 10.0 ** (-level_db * e / 20.0)
    return (x - (e * k)[:, None] * band) * g[:, None]


# ============================================================================================ placement
class Arr:
    """Tracks + an event log; transients go through place()."""
    LAYERS = ('pad', 'air', 'low', 'keys', 'pulse', 'arp', 'sub', 'kick', 'perc', 'fx')

    def __init__(self):
        self.T = {k: MS.Track(DUR, k) for k in self.LAYERS}
        self.rng = np.random.default_rng(SEED)
        self.log = []
        self.skipped = []

    def put(self, layer, x, t, gain_db=0.0, pan=0.0, transient=True, hum=0.003, offset=0.0, tag=''):
        """Place event x whose audible onset is at grid time t (x starts at t - offset). Transients go through
        place() (hum: random humanise, s). Returns the placed onset time or None (skipped)."""
        if transient:
            h = float(self.rng.uniform(-hum, hum)) if hum else 0.0
            tp = place(t, h)
            if tp is None:
                self.skipped.append((round(t, 3), layer, tag))
                return None
            sup = bool(np.any(np.abs(HERO_T - tp) <= 0.012))
        else:
            tp, sup = t, False
        t0 = tp - offset
        self.T[layer].add(choke(np.asarray(x, dtype=np.float64), t0, layer), t0, gain_db=gain_db, pan=pan)
        self.log.append((float(tp), layer, tag, bool(transient), sup))
        return tp


def build():
    R = Arr()

    # ---------------------------------------------------------------- PAD: warm, detuned, slow filter swell
    for k, (b0, name, sub, voic) in enumerate(CHORDS):
        s0, s1 = span(k)
        sec = section_of(b0)
        t0, d = B(s0), B(s1 - s0)
        att, rel, sweep, open_to = 0.3, 0.8, 0.2, None
        if sec == 'A hook':
            vel, cut, gdb = 0.55, 800.0, -14.0
            if k == 0:
                att, open_to = 1.6, 1000.0                  # swells in from silence under the heartbeat
            else:                                           # pre-lap: swells into each slam (no pad onset on it)
                att = 0.4
                if b0 == 7:
                    d, rel = B(9) - t0, 1.2                 # released before the smash (4.767)
        elif sec == 'B question':
            vel, cut, gdb, att, open_to = 0.6, 700.0, -14.0, 1.0, 1500.0
        elif sec.startswith('C'):
            vel, gdb = 0.55, -14.0
            cut = 950.0 + 12.0 * (b0 - 17)                  # opens slowly through the checklist
            if b0 == 43:
                open_to = 1700.0                            # toast lift
        elif sec.startswith('D'):
            vel, gdb, cut, sweep = 0.6, -13.0, 1300.0 + 10.0 * (b0 - 48), 0.3
            if b0 == 72:
                open_to = 2000.0
        elif sec == 'E payoff':
            vel, gdb, cut, sweep, att = 0.7, -12.0, 2000.0, 0.25, 0.12
        else:
            vel, gdb, cut, sweep = 0.62, -12.5, 1600.0, 0.2
        last = k == len(CHORDS) - 1
        if last:
            d, rel, open_to = FADE_T1 - t0, 0.4, 900.0
        tstart = t0
        if sec == 'A hook' and k > 0:
            tstart, d = t0 - 0.25, d + 0.25
        if b0 == 75:                                        # payoff: swells in under the pickup, full by the flash
            tstart, att, d = t0 - 0.25, 0.3, d + 0.25
        p = MS.pad(list(voic), dur=d + (0.12 if not last else 0.0), vel=vel, wave='warm', voices=5, detune=13,
                   attack=att, release=rel, cutoff=cut, q=0.7, sweep=sweep, sweep_rate=0.09, open_to=open_to,
                   chorus_mix=0.35, width=0.85, seed=SEED + k)
        R.put('pad', p, tstart, gain_db=gdb, transient=False, tag='pad ' + name)

    # ---------------------------------------------------------------- AIR: high shimmer (question, toast, payoff, end)
    def air(notes, t, dur, vel=0.45, gdb=-21.0, att=1.0, rel=1.2, cut=3800.0, seed=0, tag='air'):
        p = MS.pad(list(notes), dur=dur, vel=vel, wave='tri', voices=3, detune=7, attack=att, release=rel,
                   cutoff=cut, q=0.6, sweep=0.15, sweep_rate=0.12, chorus_mix=0.4, width=1.0, seed=seed)
        R.put('air', p, t, gain_db=gdb, transient=False, tag=tag)

    air((76, 81, 83), 6.0, B(17) - 6.0, att=1.2, rel=1.0, seed=31, tag='air E7sus4')
    air((72, 76, 79), B(43), B(48) - B(43), att=0.6, rel=1.4, seed=32, tag='air toast C')
    air((76, 79, 84), B(75) - 0.25, B(78) - B(75) + 0.25, att=0.35, rel=0.8, gdb=-20.0, seed=33, tag='air C')
    air((74, 79, 83), B(78), B(80) - B(78), att=0.3, rel=0.8, gdb=-20.0, seed=34, tag='air G/B')
    air((76, 79, 84), B(80), B(82) - B(80), att=0.3, rel=0.8, gdb=-20.0, seed=35, tag='air Am7')
    air((76, 81, 84), B(82), B(83) - B(82), att=0.2, rel=0.6, gdb=-20.0, seed=36, tag='air F')
    air((74, 79, 84), B(83), B(84) - B(83), att=0.2, rel=0.6, gdb=-20.0, seed=37, tag='air Gsus4')
    air((76, 79, 86), B(84), B(88) - B(84), att=0.3, rel=1.0, gdb=-21.0, seed=38, tag='air end C')
    air((76, 79, 86), B(92), FADE_T1 - B(92), att=0.8, rel=0.4, gdb=-21.0, seed=39, tag='air end C2')

    # ---------------------------------------------------------------- LOW strings pad (payoff + end card)
    for k, (b0, name, sub, voic) in enumerate(CHORDS):
        if b0 < 75:
            continue
        s0, s1 = span(k)
        root = sub + 12
        while root < 45:
            root += 12
        notes = [root, root + 7]
        last = k == len(CHORDS) - 1
        d = (FADE_T1 - B(s0)) if last else B(s1 - s0) + 0.1
        p = MS.pad(notes, dur=d + (0.25 if b0 == 75 else 0.0), vel=0.62, wave='saw', voices=4, detune=8,
                   attack=0.32 if b0 == 75 else 0.25,
                   release=0.5 if last else 0.7, cutoff=650.0, q=0.6, sweep=0.15, sweep_rate=0.07,
                   chorus_mix=0.3, width=0.7, seed=SEED + 100 + k)
        R.put('low', p, B(s0) - (0.25 if b0 == 75 else 0.0), gain_db=-16.0, transient=False, tag='low ' + name)

    # ---------------------------------------------------------------- SUB BASS
    def sub(note, t, dur, vel=0.7, gdb=-6.0, glide_from=None, attack=0.012, tag='sub'):
        if attack >= 0.1:                               # a slow swell: a clean sine, no harmonics to 'click' in
            x = MS.sub_bass(note, dur=dur, vel=vel, drive=1.0, harm=0.0, attack=attack, release=0.2)
            R.put('sub', x, t, gain_db=gdb, transient=False, tag=tag)
            return
        x = MS.sub_bass(note, dur=dur, vel=vel, glide_from=glide_from, glide=0.09, drive=1.5, harm=0.14,
                        attack=attack, release=0.1)
        if attack < 0.03 and place(t) is None:          # never a low thump 12-60 ms from a hero: soften instead
            x = MS.sub_bass(note, dur=dur, vel=vel, glide_from=glide_from, glide=0.09, drive=1.5, harm=0.14,
                            attack=0.06, release=0.1)
            R.put('sub', x, t, gain_db=gdb, transient=False, tag=tag + ' soft')
            return
        R.put('sub', x, t, gain_db=gdb, transient=attack < 0.03, hum=0.0, tag=tag)

    # hook: one note per slam; released before the smash (4.767)
    sub(33, 0.5, 1.2, vel=0.62, tag='sub A1')
    sub(29, B(3.5), 1.15, vel=0.62, tag='sub F1')
    sub(36, B(6), 0.45, vel=0.6, tag='sub C2')
    sub(38, B(7), 0.95, vel=0.62, tag='sub D2')
    # question: soft held E2
    sub(40, B(10), B(17) - B(10) - 0.05, vel=0.46, attack=0.35, gdb=-7.0, tag='sub E2 (held)')
    for k, (b0, name, sn, voic) in enumerate(CHORDS):
        if b0 < 17:
            continue
        s0, s1 = span(k)
        sec = section_of(b0)
        prev = CHORDS[k - 1][2]
        if sec in ('C1 checklist', 'C3 toast'):
            sub(sn, B(s0), B(s1 - s0) - 0.08, vel=0.64 if sec[1] == '1' else 0.57, tag='sub ' + name)
        elif sec == 'C2 checklist':
            for bb in np.arange(s0, s1, 2.0):
                ln = min(2.0, s1 - bb)
                sub(sn, B(bb), B(ln) - 0.08, vel=0.66 if bb == s0 else 0.58, tag='sub ' + name)
        elif sec in ('D1 dock', 'D2 dock'):
            for bb in np.arange(s0, s1, 4.0):
                sub(sn, B(bb), B(1.7), vel=0.7, glide_from=prev if bb == s0 and k % 2 == 0 else None,
                    tag='sub ' + name)
                if bb + 2.5 < s1 - 0.4:                      # push on the 'and' of 3 (4-beat chords)
                    sub(sn, B(bb + 2.5), B(min(1.3, s1 - bb - 2.5)) - 0.06, vel=0.6, tag='sub push ' + name)
        elif sec == 'D3 build':
            sub(sn, B(s0), B(s1 - s0) - 0.06, vel=0.66, tag='sub ' + name)
        elif sec == 'E payoff':
            sub(sn, B(s0), B(s1 - s0) - 0.02, vel=0.74, glide_from=prev if b0 != 75 else None,
                tag='sub ' + name)
        else:                                               # end card
            last = k == len(CHORDS) - 1
            dur = (FADE_T1 - B(s0) - 0.3) if last else B(s1 - s0) - 0.04
            sub(sn, B(s0), dur, vel=0.7 if not last else 0.66, glide_from=prev if b0 in (88, 90) else None,
                tag='sub ' + name)

    # ---------------------------------------------------------------- LOW PULSE (hook) / LIGHT PULSE (checklist)
    def pulse_note(beat, fifth=False):
        _, c = chord_at(beat)
        r = c[2] + 12
        return r + 7 if fifth else r

    tick_steps = {int(round(round(t / (BEAT / 2)))) for t in TICKS}      # 8th index nearest each tick
    for e8 in range(2, 18):                                  # hook: 8ths from beat 1 (0.50) to 4.25
        bt = e8 / 2.0
        v = (0.5 if e8 % 2 == 0 else 0.4) * (0.85 + 0.15 * e8 / 17)
        x = MS.pluck_synth(pulse_note(bt), dur=0.2, vel=v, cutoff=230.0, env_oct=1.8, decay=0.05,
                           amp_decay=0.16, q=0.9, wave='warm', detune=5.0, release=0.06, seed=e8)
        R.put('pulse', x, B(bt), gain_db=-9.0, tag='pulse hook')
    for e8 in range(34, 96):                                 # checklist: 8ths 8.50-23.75
        bt = e8 / 2.0
        sec = section_of(bt)
        on = e8 % 2 == 0
        fifth = sec != 'C1 checklist' and e8 % 4 == 2
        v = (0.5 if on else 0.38) + (0.05 if sec != 'C1 checklist' else 0.0)
        cut = 260.0 + (60.0 if sec != 'C1 checklist' else 0.0)
        tag = 'pulse'
        if e8 in tick_steps:
            v, cut, tag = 0.7, 380.0, 'pulse tick accent'
        if sec == 'C3 toast' and bt == 43:
            v, cut, tag = 0.66, 360.0, 'pulse toast'
        x = MS.pluck_synth(pulse_note(bt, fifth), dur=0.2, vel=v, cutoff=cut, env_oct=1.9, decay=0.05,
                           amp_decay=0.17, q=0.9, wave='warm', detune=5.0, release=0.06, seed=100 + e8)
        R.put('pulse', x, B(bt), gain_db=-9.5, tag=tag)

    # ---------------------------------------------------------------- KICK (soft, cinematic)
    kick_beats = []
    kick_beats += [(b, 0.6 + 0.004 * (b - 17)) for b in range(17, 32)]         # C1: every beat, soft
    kick_beats += [(b, 0.7) for b in range(32, 43)]                             # C2
    kick_beats += [(b, 0.74) for b in range(43, 48)]                            # C3 toast lift
    kick_beats += [(b, 0.76 if b % 2 == 0 else 0.7) for b in range(48, 72)]    # dock
    kick_beats += [(72, 0.72)]                                                  # build: the kick stops
    kick_beats += [(75, 0.7), (76, 0.68), (78, 0.74), (80, 0.74), (82, 0.72), (83, 0.66)]   # payoff half-time
    kick_beats += [(84, 0.66), (88, 0.58), (92, 0.58)]                           # end card
    for b, v in kick_beats:
        R.put('kick', MS.soft_kick(vel=v, punch=0.3, tone=48.0, decay=0.32, click=0.12, drive=1.3,
                                   seed=int(b)), B(b), gain_db=-4.0, tag='kick')

    # ---------------------------------------------------------------- PERC: hats, shaker, brushes
    for b in list(range(32, 48)) + list(range(48, 60)):                         # off-beat hats C2 + D1
        R.put('perc', MS.hat(vel=0.34 if b < 48 else 0.38, seed=b), B(b + 0.5), gain_db=-22.0, pan=0.22,
              tag='hat')
    acc16 = (1.0, 0.45, 0.75, 0.5)

    def shaker(b0, b1, vel, gdb, step=1, cresc=0.0):
        for s in range(int(round(b0 * 4)), int(round(b1 * 4)), step):
            bt = s / 4.0
            v = vel * acc16[s % 4] * (1.0 + cresc * (bt - b0) / max(b1 - b0, 1e-6))
            x = MS.shaker(vel=min(v, 0.95), length=0.065, tone=7200.0, attack=0.012, seed=s)
            R.put('perc', x, B(bt), gain_db=gdb, pan=-0.25, offset=0.012, hum=0.002, tag='shaker')

    shaker(43, 48, 0.5, -22.0)                       # toast lift: 16ths
    shaker(48, 60, 0.5, -22.0, step=2)               # D1: 8ths
    shaker(60, 72, 0.55, -21.0)                      # D2: 16ths
    shaker(72, 75, 0.42, -23.0, cresc=0.5)           # D3: crescendo into the payoff
    shaker(75, 84, 0.48, -22.5)                      # payoff
    shaker(84, 92, 0.42, -23.0, step=2)              # end card: 8ths, stop at 46.0
    for b in range(61, 72, 2):                       # D2: brushes on 2 and 4
        R.put('perc', MS.brush(vel=0.42, length=0.2, seed=b), B(b), gain_db=-20.0, pan=0.2, tag='brush')
    for b in (77, 79, 81):                           # payoff: brushes on the half-time backbeat
        R.put('perc', MS.brush(vel=0.38, length=0.24, seed=b), B(b), gain_db=-21.0, pan=0.2, tag='brush')

    # ---------------------------------------------------------------- ARPEGGIO (plucked), dock -> end card
    def arp_tones(beat):
        _, c = chord_at(beat)
        v = sorted(c[3])
        while v[0] < 55:
            v = v[1:] + [v[0] + 12]
            v.sort()
        return v

    pat8 = (0, 2, 1, 3, 2, 4, 3, 1)
    pat16 = (0, 2, 1, 3, 2, 4, 3, 1, 0, 2, 4, 3, 2, 1, 3, 2)
    for s in range(48 * 4, 92 * 4):
        bt = s / 4.0
        sec = section_of(bt)
        if sec == 'D1 dock' or (sec == 'F end card'):
            if s % 2:
                continue
            idx = pat8[(s // 2) % 8]
            dur, cut = 0.2, 760.0 if sec == 'D1 dock' else 820.0
            v = 0.52 if s % 4 == 0 else 0.44
            if sec == 'F end card':
                v *= 1.0 - 0.35 * (bt - 84) / 8.0
        else:
            idx = pat16[s % 16]
            dur = 0.12
            cut = {'D2 dock': 880.0 + 4.0 * (bt - 60), 'D3 build': 1000.0 + 60.0 * (bt - 72),
                   'E payoff': 1150.0}[sec]
            v = (0.5, 0.36, 0.44, 0.38)[s % 4]
            if sec == 'D3 build':
                v *= 0.85 + 0.15 * (bt - 72) / 3.0
        tones = arp_tones(bt)
        nt = tones[idx % len(tones)]
        x = MS.pluck_synth(nt, dur=dur, vel=v, cutoff=cut, env_oct=2.2, decay=0.08, amp_decay=0.3, q=0.9,
                           wave='saw', detune=6.0, release=0.08, seed=1000 + s)
        R.put('arp', x, B(bt), gain_db=-14.0 if sec == 'D2 dock' else -14.5, pan=0.28 if s % 2 else -0.28, hum=0.002, tag='arp %s' % sec)

    # ---------------------------------------------------------------- FELT PIANO
    def piano(notes, t, vel=0.5, dur=1.0, pedal=False, tail=3.0, rel=0.35, gdb=-8.0, pan=-0.1, felt=1.0,
              roll=0.0, tag='piano'):
        """A chord (or one note): one placement for all notes (no roll on a hero hit)."""
        tp = place(t)
        if tp is None:
            R.skipped.append((round(t, 3), 'keys', tag))
            return None
        sup = bool(np.any(np.abs(HERO_T - tp) <= 0.012))
        for i, nt in enumerate(sorted(notes)):
            x = MS.felt_piano(nt, dur=dur, vel=vel * (1.0 - 0.03 * i), pedal=pedal, release=rel, felt=felt,
                              tail=tail, seed=int(t * 100) + i)
            ti = tp + (0.0 if sup else roll * i)
            R.put('keys', x, ti, gain_db=gdb, pan=pan + 0.06 * i, transient=False,
                  tag='%s %s' % (tag, MS.note_name(nt, True)))
            R.log[-1] = R.log[-1][:3] + (True, sup)
        return tp

    # hook: sustained chords ON the four slams (same instant)
    piano((45, 52, 60, 64, 71), B(1), vel=0.46, dur=1.2, rel=0.45, gdb=-9.0, tag='slam1 Am(add9)')
    piano((41, 48, 57, 64, 69), B(3.5), vel=0.46, dur=1.15, rel=0.45, gdb=-9.0, tag='slam2 Fmaj7')
    piano((48, 55, 62, 64, 67), B(6), vel=0.44, dur=0.5, rel=0.3, gdb=-9.0, tag='slam3 C(add9)')
    piano((38, 45, 53, 57, 64), B(7), vel=0.5, dur=1.05, rel=0.5, gdb=-9.0, tag='slam4 Dm(add9)')
    # question: soft ground, then motif M1 in the VO gap (the A5 rings over the whip into the checklist)
    piano((40, 47), B(10), vel=0.36, dur=3.0, rel=0.6, gdb=-9.0, tag='ground E')
    for bt, nt, v, d in ((14.5, 76, 0.44, 0.3), (15.0, 74, 0.4, 0.3), (15.5, 76, 0.44, 0.3),
                         (16.0, 81, 0.48, 1.6)):
        piano((nt,), B(bt), vel=v, dur=d, pedal=bt == 16.0, tail=2.2, rel=0.3, gdb=-9.5, pan=0.12, felt=0.9,
              tag='M1')
    # checklist: one subtle accent per tick (low dyad, rising top note), on the tick
    for t, notes in zip(TICKS, ((41, 57), (48, 60), (43, 62), (45, 64), (41, 65))):
        g8 = round(t / (BEAT / 2)) * (BEAT / 2)              # the 8th-note grid point of the tick
        piano(notes, g8, vel=0.42, dur=0.6, rel=0.4, gdb=-9.0, tag='tick accent')
    # toast (21.50, same instant): C/E chord
    piano((40, 52, 55, 60, 64), TOAST, vel=0.46, dur=1.2, rel=0.5, gdb=-8.5, tag='toast C/E')
    # pickup into the dock in the VO gap (23.10-24.30), resolving to C5 on the whip downbeat
    for bt, nt, v in ((46.5, 76, 0.42), (47.0, 74, 0.4), (47.5, 71, 0.42)):
        piano((nt,), B(bt), vel=v, dur=0.3, rel=0.3, gdb=-9.5, pan=0.12, felt=0.9, tag='pickup')
    piano((53, 60, 72), B(48), vel=0.42, dur=1.0, rel=0.5, gdb=-9.5, tag='dock F/C5')
    # dock gap figures
    for bt, nt, v in ((55.5, 79, 0.4), (56.0, 81, 0.42), (56.5, 77, 0.38)):
        piano((nt,), B(bt), vel=v, dur=0.3, rel=0.3, gdb=-10.0, pan=0.15, felt=0.9, tag='gap fig')
    for bt, nt, v in ((60.0, 76, 0.4), (60.5, 72, 0.36)):
        piano((nt,), B(bt), vel=v, dur=0.3, rel=0.3, gdb=-10.0, pan=0.15, felt=0.9, tag='gap fig')
    # build: rising pickup G4 A4 B4 D5 -> the payoff chord (top E5) at 37.508
    for bt, nt, v in ((73.0, 67, 0.4), (73.5, 69, 0.43), (74.0, 71, 0.46), (74.5, 74, 0.5)):
        piano((nt,), B(bt), vel=v, dur=0.35, rel=0.3, gdb=-9.0, pan=0.1, felt=0.9, tag='payoff pickup')
    piano((48, 55, 64, 72, 76), B(75), vel=0.47, dur=1.4, rel=0.6, gdb=-9.5, tag='payoff C(add9)')
    piano((47, 55, 62, 67), B(78), vel=0.4, dur=0.95, rel=0.4, gdb=-9.5, tag='payoff G/B')
    piano((45, 52, 60, 64), B(80), vel=0.4, dur=0.95, rel=0.4, gdb=-9.5, tag='payoff Am7')
    # motif M2 (= M1 in C) in the VO gap 40.63-41.77, before the logo sting
    for bt, nt, v in ((81.5, 76, 0.44), (82.0, 74, 0.42), (82.5, 76, 0.44), (83.0, 79, 0.48)):
        piano((nt,), B(bt), vel=v, dur=0.3 if bt < 83 else 0.6, rel=0.3, gdb=-9.0, pan=0.12, felt=0.9,
              tag='M2')
    piano((41, 48, 57, 64), B(82), vel=0.38, dur=0.45, rel=0.3, gdb=-10.0, tag='payoff Fmaj7')
    # end card
    piano((48, 55, 64, 67, 72), B(84), vel=0.44, dur=1.8, rel=0.6, gdb=-9.5, roll=0.014, tag='end C(add9)')
    piano((41, 48, 57, 64, 67), B(88), vel=0.36, dur=0.95, rel=0.4, gdb=-10.0, tag='end Fmaj9')
    piano((43, 50, 60, 62, 67), B(90), vel=0.34, dur=0.95, rel=0.4, gdb=-10.0, tag='end Gsus4')
    piano((48, 55, 62, 64, 67), B(92), vel=0.44, dur=2.5, rel=0.8, gdb=-9.0, roll=0.012, tag='end C(add9) resolve')
    piano((79,), B(92.5), vel=0.38, dur=0.4, rel=0.3, gdb=-10.0, pan=0.15, felt=0.9, tag='CTA click G5')
    # motif M3, the answer, after the last line (47.93-): E5 D5 C5 over the held C
    for bt, nt, v, d in ((96.0, 76, 0.44, 0.3), (96.5, 74, 0.4, 0.3), (97.0, 72, 0.46, 1.2)):
        piano((nt,), B(bt), vel=v, dur=d, pedal=bt == 97.0, tail=1.5, rel=0.3, gdb=-9.0, pan=0.12, felt=0.9,
              tag='M3')
    piano((36, 48), B(97), vel=0.36, dur=1.2, pedal=True, tail=1.5, rel=0.3, gdb=-10.0, tag='M3 bass C')

    # ---------------------------------------------------------------- FX: reverse swells
    sw = MS.reverse_swell(1.0, vel=0.45, notes=[53, 57, 60, 64, 67], bright=0.7, seed=5)
    R.put('fx', sw, B(48) - 1.0, gain_db=-22.0, transient=False, tag='swell -> dock')
    t_pay = place(B(75))
    sw = MS.reverse_swell(1.6, vel=0.6, notes=[60, 64, 67, 74], bright=0.8, seed=6)
    R.put('fx', sw, t_pay - 1.6, gain_db=-17.0, transient=False, tag='swell -> payoff')
    return R


# ============================================================================================ mix
def mono_low(x, fc=150.0):
    """High-pass the side channel (zero phase): the low end is mono."""
    m, s = 0.5 * (x[:, 0] + x[:, 1]), 0.5 * (x[:, 0] - x[:, 1])
    s = signal.sosfiltfilt(signal.butter(2, fc, 'highpass', fs=SR, output='sos'), s)
    return np.stack([m + s, m - s], 1)


def zpf_hp(x, fc, order=2):
    return signal.sosfiltfilt(signal.butter(order, fc, 'highpass', fs=SR, output='sos'), x, axis=0)


# bus trims (dB) on top of the per-event gains
TRIM = dict(pad=9.0, air=12.0, low=6.0, keys=2.0, pulse=4.0, arp=9.0, sub=-2.0, kick=-1.5, perc=15.0, fx=10.0)
HPF = dict(pad=150.0, air=300.0, low=120.0, keys=120.0, arp=180.0, perc=200.0, fx=180.0, pulse=45.0, sub=30.0,
           kick=28.0)


def mixdown(R):
    e = env_cached()
    T = {k: v.buf * A.undb(TRIM.get(k, 0.0)) for k, v in R.T.items()}
    T = {k: zpf_hp(v, HPF[k]) for k, v in T.items()}
    kick = T['kick']
    tonal = MS.duck(T['pad'] + T['low'] + T['arp'] + T['pulse'], kick, depth_db=3.0, attack=0.004, release=0.17)
    sub_d = MS.duck(T['sub'], kick, depth_db=3.5, attack=0.004, release=0.17)
    sends = (MS.reverb_send(T['pad'] + T['air'] + T['low'] + T['keys'], 'hall', wet_db=-14.0, hp_hz=220.0)
             + MS.reverb_send(T['arp'] + T['perc'], 'plate', wet_db=-17.0, hp_hz=260.0))
    upper = tonal + T['keys'] + T['air'] + T['perc'] + T['fx'] + sends
    upper = speech_dip(upper, e)
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
    """Speech-band (lo-hi Hz) level in win-s windows every hop s: (window starts (samples), dB)."""
    sos = signal.butter(4, [lo, hi], 'bandpass', fs=SR, output='sos')
    y = signal.sosfiltfilt(sos, A._st(x).mean(1))
    nw, nh = int(win * SR), int(hop * SR)
    c = np.concatenate([[0.0], np.cumsum(y * y)])
    st = np.arange(0, len(y) - nw, nh)
    return st, 10 * np.log10((c[st + nw] - c[st]) / nw + 1e-20)


def music_onsets(x, thr_db=6.0, hp_hz=300.0, floor_db=30.0, refractory=0.05, renew_db=3.0):
    """Onsets of the clean music: the 300 Hz+ power (3 ms smoothing, 0.5 ms hop) of the next 8 ms vs the mean of
    a 40 ms window ending 10 ms before (a transient against its context) >= thr_db, within floor_db of the
    99.5th-percentile power. The onset time is the threshold crossing (its constant lead is removed by the bias
    correction in transient_check); a re-detection of the same event (within `refractory` s of an onset and not
    renew_db louder) is not counted. Returns [(t_s, strength_db)]."""
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
    last_t, last_lv = -1.0, -999.0
    i = n_pre + gap
    while i < len(s):
        if s[i] >= thr_db and lvp[i] > fl:
            j = i + int(np.argmax(s[i:i + 30]))
            t_on = i * hop / SR
            lv = float(np.max(lvp[i:j + 1]))
            if t_on - last_t < refractory and lv < last_lv + renew_db:
                last_lv = max(last_lv, lv)
            else:
                out.append((t_on, float(s[j])))
                last_t, last_lv = t_on, lv
            i = j + 50
        else:
            i += 1
    return out


def transient_check(clean, log):
    """Audio check of the SFX rule: music onsets 12-60 ms from a hero hit, after removing the detector's timing
    bias (median offset to the logged transient times). A flagged onset within 15 ms of a logged transient that
    was placed as a same-instant support (within 12 ms of every near hero, log_check) is that event read with
    the detector's +-5 ms timing scatter: listed under 'support_events'; anything else is a violation."""
    ons = music_onsets(clean)
    ev = np.array(sorted(t for t, _, _, tr, _ in log if tr))
    offs = []
    for t, r in ons:
        j = np.searchsorted(ev, t)
        cand = [ev[k] for k in (j - 1, j) if 0 <= k < len(ev)]
        if cand:
            d = min(cand, key=lambda q: abs(t - q))
            if abs(t - d) < 0.015:
                offs.append(t - d)
    bias = float(np.median(offs)) if offs else 0.0
    sup_t = np.array(sorted(t for t, _, _, tr, sup in log if tr and sup))
    bad, sup_ev = [], []
    for t, r in ons:
        tc = t - bias
        near = HERO_T[np.abs(HERO_T - tc) <= 0.060]
        if len(near) and np.any(np.abs(near - tc) > 0.012):
            row = [round(tc, 3), round(r, 1), [round(float(h), 3) for h in near]]
            own = len(sup_t) and float(np.min(np.abs(sup_t - tc))) <= 0.015
            (sup_ev if own else bad).append(row)
    return dict(onsets=len(ons), bias_ms=round(bias * 1000, 1), matched=len(offs), violations=bad,
                support_events=sup_ev)


def log_check(log):
    """The SFX rule on the event log (exact placement times)."""
    bad = []
    for t, layer, tag, tr, sup in log:
        if not tr:
            continue
        near = HERO_T[np.abs(HERO_T - t) <= 0.060]
        if len(near) and np.any(np.abs(near - t) > 0.012 + 1e-9):
            bad.append((round(t, 4), layer, tag))
    return bad


def grid_check(log):
    """Every transient within 8 ms of the 16th-note grid."""
    step = BEAT / 4
    off = [(t, layer, tag, round(1000 * (t - round(t / step) * step), 1)) for t, layer, tag, tr, _ in log if tr]
    worst = max(abs(o[3]) for o in off) if off else 0.0
    return dict(n=len(off), worst_ms=worst, over8=[o for o in off if abs(o[3]) > 8.0001])


def melody_check(log):
    """Motif / gap-figure notes struck while a VO line is spoken (should be none)."""
    return [(t, tag) for t, layer, tag, tr, _ in log
            if layer == 'keys' and tag.split()[0] in ('M1', 'M2', 'M3', 'pickup', 'gap', 'payoff', 'CTA')
            and tag.split()[1] not in ('C(add9)', 'G/B', 'Am7', 'Fmaj7') and in_speech(t, 0.0)]


def main():
    t0 = time.time()
    R = build()
    clean, ninfo, T = mixdown(R)
    assert len(clean) == N
    A._write_wav(OUT_CLEAN, clean, 24)
    st = MS.load_reel_stems('reel1')
    assert st['n'] == N, (st['n'], N)
    bed, m = MS.render_bed(clean, st['vo'], st['sfx'], st['mix'], gap_lu=7.0, min_vo_lu=10.0, vo_duck_db=9.0,
                           vo_attack=0.04, vo_release=0.4, sfx_duck_db=3.0, sfx_attack=0.01, sfx_release=0.25)
    A._write_wav(OUT_BED, bed, 24)
    mix, rep = MS.master_withmusic(st['vo'], st['sfx'], bed, target=-14.0, tol=0.2, ceiling=-2.3, tp_max=-2.0)
    A._write_wav(OUT_MIX, mix, 24)
    os.makedirs(REEL_DIR, exist_ok=True)
    mp3b = MS.write_mp3(OUT_BED, MP3_BED, TITLE + ' (ducked bed)', artist='Organic Fostering')
    mp3c = MS.write_mp3(OUT_CLEAN, MP3_CLEAN, TITLE + ' (clean, full level)', artist='Organic Fostering')
    prev = None
    if os.path.exists(PREVIEW_IN):
        MS.make_preview(PREVIEW_IN, OUT_MIX, PREVIEW_OUT)
        prev = PREVIEW_OUT

    # ---- measurements (on the files as written)
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
    act = sel & (vo_b > np.percentile(vo_b[sel], 95) - 20.0)
    dact = (vo_b - mu_b)[act]
    # gap level of the bed vs the delivered mix (short-term 3 s, VO gaps)
    tc = transient_check(cw, R.log)
    secl = {nm: round(A.loudness(cw[int(B(b0) * SR):int(B(b1) * SR)]), 1) for nm, b0, b1 in SECTIONS}
    probes = []
    for pth in (MP3_BED, MP3_CLEAN):
        pr = MS._probe(pth)
        st0 = (pr.get('streams') or [{}])[0]
        probes.append(dict(file=os.path.basename(pth), codec=st0.get('codec_name'), channels=st0.get('channels'),
                           sample_rate=st0.get('sample_rate'), bit_rate=st0.get('bit_rate'),
                           duration=pr.get('format', {}).get('duration'),
                           title=(pr.get('format', {}).get('tags') or {}).get('title')))
    prev_info = None
    if prev:
        pr = MS._probe(prev)
        prev_info = dict(path=prev, mb=round(os.path.getsize(prev) / 1e6, 2),
                         streams=[(s_.get('codec_name'), s_.get('sample_rate'), s_.get('bit_rate'),
                                   s_.get('duration')) for s_ in pr.get('streams', [])])
    out = dict(
        render_s=round(time.time() - t0, 1),
        bounds={k: round(v, 3) for k, v in BOUNDS.items()}, section_beats=SEC_BEAT,
        ticks=[round(t, 3) for t in TICKS], toast=round(TOAST, 3),
        clean=dict(samples=len(cw), dur=len(cw) / SR, lufs=round(A.loudness(cw), 2),
                   true_peak=round(A.true_peak(cw), 2), peak_dbfs=round(float(A.db(np.abs(cw).max())), 2),
                   last20ms_dbfs=round(float(A.db(np.abs(cw[-int(0.02 * SR):]).max() + 1e-12)), 1),
                   first_sample_abs=float(np.abs(cw[0]).max()), normalise=ninfo, dc=q.get('dcrep'),
                   clicks={k: q['clicks'][k] for k in ('clean', 'count', 'worst_ratio', 'events')}),
        beat_grid=MS.beat_grid_check(cw, BPM),
        bed=dict(m, file_lufs=round(A.loudness(bw), 2), file_true_peak=round(A.true_peak(bw), 2),
                 last20ms_dbfs=round(float(A.db(np.abs(bw[-int(0.02 * SR):]).max() + 1e-12)), 1),
                 clicks=MS.click_report(bw)['clean']),
        withmusic=dict({k: v for k, v in rep.items() if k != 'stems'}, file_lufs=round(A.loudness(mw), 2),
                       file_true_peak=round(A.true_peak(mw), 2), samples=len(mw)),
        speech_band_100ms=dict(frames=int(sel.sum()), median_db=round(float(np.median(diff)), 1),
                               p10_db=round(float(np.percentile(diff, 10)), 1), min_db=round(float(diff.min()), 1),
                               active_frames=int(act.sum()), active_median_db=round(float(np.median(dact)), 1),
                               active_p10_db=round(float(np.percentile(dact, 10)), 1),
                               active_min_db=round(float(dact.min()), 1)),
        sections_lufs=secl, mp3_probe=probes,
        hero_rule=dict(log_violations=log_check(R.log), audio=tc), grid=grid_check(R.log),
        melody_in_speech=melody_check(R.log),
        mp3=[mp3b, mp3c], preview=prev_info, events=len(R.log))
    for k, tr in sorted(T.items()):
        if np.any(tr):
            out.setdefault('layers_lufs', {})[k] = round(A.loudness(tr), 1)
    print(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
    print('skipped (hero hit within 12-60 ms): ' + (', '.join('%.3f %s/%s' % s_ for s_ in R.skipped) or 'none'))
    out['skipped'] = R.skipped
    return out


if __name__ == '__main__':
    main()
