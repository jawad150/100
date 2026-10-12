#!/usr/bin/env python3
"""thoda_left_bas_sfx.py: SFX layer, beds and the VO-led A / B mixes of Bijli series #2 "Thoda Left... Bas Bas!"
(@jawad_mp4). Owner: sound-designer (+ music-supervisor: the final mixes). Plan: SHOTS.md section b (cue list) retimed to
the measured VO (VO_TIMING.md section 3, LEAD_DECISIONS 3: picture beats move to the VO). Notes + measurements: SOUND.md.
Music + THE SIGNAL CLOCK: thoda_left_bas_music.py (TM.sig drives the TV static bed here). VO: thoda_left_bas_vo.py
(vo_stem.wav + words.json).

36.000 s = 1,080 f at 30 fps, 100 BPM (beat 18 f, bar 72 f), key D minor (F major payoff). VO-LED GRID: the r1 plan
(SHOTS.md, 1008 f) gains one bar in the hook (the measured V1 + V2 need 2 bars); r1 frames >= 72 move +72 unless the VO
moved them (VO_TIMING.md section 3, SOUND.md section 2). Nobody on the team can listen:
every claim in SOUND.md is a measurement or a rendered image.

RETIMING: edit CUE_TABLE / BED_TABLE / STATIC_TABLE below (frames), then `python3 thoda_left_bas_sfx.py build`. Every cue
sits on its frame to the sample (frame f = sample f x 1,600); align 'hit' puts the designed hit on the frame (impacts =
transient, whooshes = loudest pass, risers / reverse swells = their end), 'start' starts it there. Placement is circular
(tails past f1079 land on f0: the f1080 reverse swell releases into the hook's f0 impact).

Chain: cues -> sfx_jawad.fit_under_vo (non-hero cues inside a spoken word -3 dB + carving lp / hp) -> audio.duck_under ->
circular placement + 'studio' send -> drop-out gate (exact zero f810-f827 except gate=False cues) -> SFX bus at -18 LUFS
with the beds at absolute levels (sidechained 2 dB under the SFX; the TV static follows TM.sig) -> 2:1 glue -> 4x
true-peak limiter (circular, GR capped at 3 dB) at -2.0 dBTP -> sfx.wav.
Mixes (epic_mix.mix_reel, loop=True, words=VO words, word_floor_lu=8 = LEAD_DECISIONS 1; music ducked 9 dB under the VO
+ the per-word floor so the VO sits >= 8 LU over the bed): mix_A = VO + SFX + music, mix_B = VO + SFX (song-ready), both
-14 LUFS / TP <= -2.0 dBTP; stems/stem_{vo,sfx,music}.wav at A's bus curve sum to A.

Local sounds (numpy only, no samples, no paid service; audio.qc() == [] at the used params, PNGs in <RW>/audio/audition/):
    tlb_tv_lock     THE LOCK (f90 / f378 / f720, the rhyme): 80 ms of static swelling then gated out hard on the hit +
                    a low CRT thunk + a 40 ms tonal "ping" of the picture (D6); hit = the gate / thunk
    tlb_creak       GI pipe turning in the rusted strap clamp: stick-slip pulse train (rate glides) exciting pipe modes
                    + grit; dur = the motion; hit = start
    tlb_clamp_tick  clamp click: metal-on-metal transient + strap ring; pitch in semitones; hit = transient
    tlb_gust        wind gust: band noise swelling to a peak with a faint whistle; hit = start
    tlb_buzz        phone vibration on a wooden desk: 170 Hz motor rattle + wood body; hit = start
    tlb_payoff      the f828 payoff as one designed sound: dhol_hit + impact_soft + sub_drop (LP 140), saturated
                    (drive 3, loudness-matched) for a low crest; hit = start (cue align 'start' on f828)
    tlb_static      bed: CRT static (warm hiss, 2-frame grain flicker, faint 15.625 kHz line whine), seamless 7.2 s loop
    tlb_wind        bed: roof air, gusty (whole AM cycles per loop), seamless 7.2 s loop
    tlb_fan         bed: laptop fan at steady load (air + faint ~925 Hz blade tone), seamless 7.2 s loop

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh):
    python3 thoda_left_bas_sfx.py cues        the cue table after the VO fit (frame, sound, gain, align, event)
    python3 thoda_left_bas_sfx.py audition    local sounds -> <RW>/audio/audition/*.png + audition.json (qc)
    python3 thoda_left_bas_sfx.py build       sfx.wav (+ sfx_fx / sfx_bed), music.wav if stale, mix_A.wav, mix_B.wav,
                                              stems/, sfx_cues.json, mix_summary.json, then verify
    python3 thoda_left_bas_sfx.py verify      ebur128 (wav + AAC), key frames, VO margins, overview PNGs
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.ndimage import maximum_filter1d, median_filter  # noqa: E402

import audio as A  # noqa: E402
from audio import (SR, TWO_PI, _t, _n, _rng, _st, _thump, _click, modal, lp, hp, bp, undb, db, reverb)  # noqa: E402
import epic_sfx as ES  # noqa: E402
import sfx_jawad as SJ  # noqa: E402
import epic_mix as EX  # noqa: E402

MODULE = 'thoda_left_bas'
FPS, BPM, NF = 30, 100.0, 1080
DUR = NF / FPS
N = _n(DUR)
assert N == 1728000
SPF = SR // FPS
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
VOD = os.path.join(RW, 'vo')
AUDITION = os.path.join(AUD, 'audition')
SFX_LUFS, SFX_TP = -18.0, -2.0
BED, BED_GAIN_DB = None, -30.0                 # render.py must NOT rebuild this layer: mux mix_A.wav with --audio
DROP = (810, 828)                              # drop-out frames [f810, f828)
PAYOFF = 828
LOCKS = (90, 378, 720)
BED_DUCK_DB = 2.0
SFX_MIX_LUFS = -18.5                           # the SFX level inside the VO mixes before the word floor
WORD_FLOOR_LU = 12.5                           # VO (-16 LUFS) over the SFX on every word, before the mix's 4 dB VO
WORD_FLOOR_MAX_DB = 18.0                       # sidechain; with the music word floor -> >= 8 LU over the bed
FIT_DEPTH_DB = -3.0                            # fit_under_vo level step (carving lp / hp as usual)
# music rides for the VO mixes: (f0, f1, dB, release ramp s, attack ramp s). The payoff band +3 dB over the rest of the
# music (the 60 ms attack ramp keeps the boost off the hit transient = no extra limiting; +5 dB measured the V14 words
# under the floor); the outro card -1.5 dB (LRA >= 2 LU; back to 0 dB by f1077, so the loop seam is untouched).
MUSIC_RIDE = [(828, 852, 3.0, 0.5, 0.06), (954, 1068, -1.5, 0.3, 0.3)]
MUSIC_GAIN_DB = -3.0                           # music 3 dB under the spec's -18 LUFS: the VO gaps stay open
VO_RIDE = {'V1': -1.0, 'V2': -4.0, 'V12': -3.0, 'V14': 1.0, 'V15': -1.0}  # per-line VO ride (dB) for the mixes, ramps 40 ms inside the gaps:
                                               # the shouted hook / client lines measured louder than the payoff
                                               # window; a ride, never a squash (LEAD_DECISIONS 1)
VO_CREST = 10.0                                # vo_mix.wav: true peak <= integrated + 10 dB (V1 "thoda" plosive)
VO_PEAK = {}
MUSIC_DUCK_SFX_DB = 1.5                        # music under the SFX in the mixes (spec 3 dB)
SFX_VO_CREST = 14.0                            # sfx_vo.wav: true peak <= integrated + 14 dB (transient cap)
SFX_GR_MAX = 3.0                               # stem limiter cap: the stem's loudness follows (see SOUND.md)
HERO_KEEP_S = 0.035                            # a hero transient keeps its first 35 ms (the floor ducks its tail)
LOOP_BED = DUR / 5                             # 7.2 s = 3 bars = 345,600 samples (divides N)
T_END = 954 / FPS                              # profile outro start (PO t_pop 0.10, t_move 0.75, t_q 1.30)
D6 = 1174.66


def F(f):
    return f / FPS


def _po(dt):
    """Frame of profile-outro time dt (s after T_END)."""
    return round((T_END + dt) * FPS, 2)


# ============================================================================================ CUE TABLE (frames)
# (frame, sound, gain_db, options, visual event). options: align ('hit' default | 'start'), pan, lp, hp, dur, params {},
# seed, gate (False = passes the f810-f827 drop-out gate), hero (True = never ducked by the VO fit), vo (False = skip the
# VO fit). Frames follow VO_TIMING.md section 3 (picture moved to the VO).
CUE_TABLE = [
    # S1 hook A (f0-f143): snowy CRT, ghost picture sliding with the yaw; VO V1 f2-f86 / V2 "Bas" f90-f152
    (0, 'impact_soft', -10.0, dict(lp=900), 'frame-0 transient: release of the f1080 reverse swell (loop)'),
    (56, 'tlb_creak', -18.0, dict(align='start', params=dict(dur=0.33), pan=0.2), 'yaw -14 -> +9 (f56-f66): picture slides right'),
    (66, 'swish_small', -15.0, dict(params=dict(direction=1), pan=-0.2), 'H1b keyword flip `*right...*` on V1 "right..." (r1 f18)'),
    (90, 'tlb_tv_lock', -8.5, {}, 'H2 `BAS BAS!` SLAM on V2 "Bas": picture LOCKS (r1 f36); not hero: the shout owns the frame, the word floor ducks the thunk'),
    (136, 'glitch_short', -13.0, {}, 'slip during "theek hai!": picture tears back to snow (r1 f63)'),
    (136, 'notif_ping', -15.0, dict(pan=0.35), 'B0 anachronism bubble pops top-right (x 790) (r1 f63)'),
    # S2 roof day (f144-f269); VO V3 f156-f229, V4 f234-f262
    (180, 'tlb_creak', -12.0, dict(align='start', params=dict(dur=0.17)), 'mast jerks the wrong way on "Nahi!" (f180-f185)'),
    (190, 'tlb_creak', -12.0, dict(align='start', params=dict(dur=0.27, pitch=1.12)), 'second jerk after the regrip (f190-f198)'),
    (234, 'tape_stop', -10.0, dict(align='start', hero=True, params=dict(dur=0.36)), 'R4 `*kiska* left?!` SLAM on "Kiska": freeze + music halt'),
    (252, 'tlb_creak', -16.0, dict(align='start', params=dict(dur=0.57, pitch=0.94)), 'mast turns back (f252-f269)'),
    # S3 CRT room (f270-f341); VO V5 f271-f366
    (304, 'glitch_short', -15.0, dict(seed=1), 'overshoot: picture falls into snow before "nahi nahi" (r1 f214)'),
    # S4 clamp macro (f342-f377): ticks on the 8ths, marks align on the bar-5 downbeat f360 (V6 not in the VO)
    (342, 'tlb_clamp_tick', -12.0, dict(params=dict(pitch=0.0)), 'clamp click 1 (yaw -2)'),
    (351, 'tlb_clamp_tick', -12.0, dict(params=dict(pitch=2.0)), 'clamp click 2 (yaw -1)'),
    (360, 'tlb_clamp_tick', -8.0, dict(params=dict(pitch=5.0)), 'C8 `BAS! BAS!`: the paint marks align'),
    (360, 'slot_tick', -15.0, dict(params=dict(n=3, dur=0.12)), 'marks align: the last detents land'),
    # S5 CRT lock (f378-f449); VO V7 "Ab" f381, "Arre" f432
    (378, 'tlb_tv_lock', -5.0, dict(hero=True, seed=1), 'C9 LOCK + the film starts (TV sting) (r1 f306)'),
    (378, 'sitar_pluck', -14.0, dict(hp=300, lp=4000, params=dict(note=62, meend=0.0, dur=1.6)),
     'TV sting from the CRT speaker (band-limited)'),
    (378, 'harmonium_swell', -16.0, dict(align='start', hp=300, lp=4000, params=dict(duration=1.2, notes=(50, 57, 62))),
     'TV sting: harmonium under the shimmer sweep'),
    (414, 'tlb_gust', -10.0, dict(align='start', params=dict(dur=1.0), pan=-0.3), 'gust (r1 f342), slip f418-f430'),
    (420, 'glitch_short', -13.0, dict(seed=2), 'picture tears, horizontal roll (r1 f348)'),
    # S6 roof wind (f450-f503), M3 f504; VO V8 f470-f534 (L-cut across M3)
    (486, 'tlb_creak', -11.0, dict(align='start', params=dict(dur=0.57, pitch=0.85), pan=-0.25), 'the big swing left (f486-f503)'),
    (504, 'whoosh_fast', -4.0, dict(params=dict(direction=1)), 'M3 match: rod tip -> title clip (track pass)'),
    (512, 'card_slide', -9.0, {}, 'M3: title settles into the timeline (f513)'),
    # S7 UI timeline (f504-f557); VO V10 f540-f663
    (540, 'notif_ping', -10.0, dict(pan=0.0), 'T1 toast `Client / thoda left...` on V10 "Thoda" (re-hook)'),
    (551, 'mouse_click', -12.0, dict(pan=0.3), 'cursor clicks the X readout on "left..." (r1 f477)'),
    (551, 'ui_tick', -16.0, dict(pan=0.3), 'X 540 -> 538, `-2 px` flash'),
    # S8 phone macro (f558-f593)
    (584, 'tlb_buzz', -12.0, dict(align='start'), 'phone buzzes on the desk (jitter 8 f)'),
    (586, 'bubble_pop', -14.0, {}, 'P1b bubble `thoda right...` on V10 "thoda" (r1 f490)'),
    # S9 avalanche (f594-f647): rows every 3 f, X jitter on the 8ths; P1c over it on "nahi,"
    (594, 'slot_tick', -20.0, dict(align='start', params=dict(n=18, dur=1.75, ease='in')), 'revision list stacks a row every 3 f'),
] + [(594 + 9 * k, 'ui_tick', -17.0, dict(seed=k, pan=0.25), 'X readout jitters (8th %d)' % (k + 1)) for k in range(6)] + [
    (626, 'bubble_pop', -14.0, dict(seed=1, params=dict(pitch=0.9)), 'P1c bubble `nahi, pehle wala` on V10 "nahi," (r1 f504)'),
    # S10 TAB / AB split (f648-f719): both eras move on the same frame; VO V11 f669-f702
] + [c for k, f in enumerate((648, 666, 684, 702)) for c in (
    (f, 'tlb_creak', -15.0, dict(align='start', params=dict(dur=0.2, pitch=1.0 + 0.05 * k), pan=0.0, seed=k),
     'split top: antenna moves (6 f)'),
    (f, 'bubble_pop', -16.0, dict(seed=k, pan=0.1), 'split bottom: chat bubble pops'),
    (f, 'ui_tick', -17.0, dict(seed=k + 7, pan=0.1), 'split bottom: title nudges'))] + [
    # S11 client lock (f720-f791); VO V12 "Bas" f720
    (720, 'tlb_tv_lock', -8.5, dict(hero=True, seed=2), 'C14 client `BAS BAS!` = the TV lock (the rhyme) (r1 f648)'),
    (720, 'impact_big', -14.0, dict(hero=True), 'title snaps crisp at X 538, row v27 lights'),
    (788, 'render_complete', -11.0, dict(params=dict(pitch=0.891)), 'export bar reaches 100 % (pitched to D minor) (r1 f716)'),
    (792, 'reverse_swell', -7.0, dict(params=dict(duration=0.6)), 'M2 into the sunset roof (r1 f720)'),
    (792, 'shimmer', -12.0, dict(hp=4000, params=dict(dur=1.2)), 'M2: sunset rays bloom'),
    # S12 sunset roof: DROP-OUT f810-f827, PAYOFF f828; VO V14 f834-f903
    (828, 'reverse_cymbal', -16.0, dict(params=dict(duration=0.25), gate=False, vo=False), 'cymbal swell f820.5 -> f828 (last 0.25 s of the drop-out)'),
    (828, 'tlb_payoff', -4.2, dict(align='start', gate=False, hero=True, dur=2.5), 'PAYOFF `HUM AAJ BHI / *antenna*` (r1 f756)'),
    (900, 'tlb_clamp_tick', -20.0, dict(params=dict(pitch=-2.0)), 'antenna nudges 2 deg by itself (easter egg, r1 f828)'),
    (936, 'whoosh_fast', -7.0, dict(params=dict(direction=-1)), 'M3 match: the nudge -> the TV picture slide (r1 f864)'),
    (944, 'card_slide', -11.0, {}, 'M3: CRT world settles'),
    # S13 CRT loop + profile outro (f954-f1079); VO V15 f978-f1051
    (_po(0.10), 'swish_small', -13.0, dict(align='start'), 'outro: profile pill pops (PO t_pop)'),
    (_po(1.25), 'glass_tap', -13.0, {}, 'outro: card moves (PO t_move + 0.5 s)'),
    (_po(1.50), 'shimmer', -12.0, dict(params=dict(dur=1.5)), 'outro: question lands (PO t_q + 0.2 s)'),
    (1062, 'notif_ping', -15.0, dict(pan=0.35, seed=1), 'B1 bubble `thoda left...` pops (loop tease, r1 f990)'),
    (1080, 'reverse_swell', -11.0, dict(params=dict(duration=0.8)), 'loop: swell f1056 -> f1080 = f0'),
]

# (f0, f1, bed, params, LUFS in the -18 LUFS stem, fade in s, fade out s, note). f1 > 1080 wraps across the seam.
BED_TABLE = [
    (0, 144, 'room_tone', dict(dur=LOOP_BED), -42.0, 0.3, 0.01, 'TV room (hook)'),
    (144, 270, 'tlb_wind', dict(dur=LOOP_BED), -38.0, 0.01, 0.01, 'roof air (S2)'),
    (144, 270, 'outdoor_birds', dict(dur=LOOP_BED), -44.0, 0.01, 0.01, 'roof: sparse birds'),
    (144, 270, 'desi_city', dict(dur=LOOP_BED), -46.0, 0.01, 0.01, 'roof: distant city'),
    (270, 342, 'room_tone', dict(dur=LOOP_BED), -42.0, 0.01, 0.01, 'CRT room (S3)'),
    (342, 378, 'tlb_wind', dict(dur=LOOP_BED), -40.0, 0.01, 0.01, 'clamp macro, outdoors (S4)'),
    (378, 450, 'room_tone', dict(dur=LOOP_BED), -42.0, 0.01, 0.01, 'CRT room (S5)'),
    (450, 504, 'tlb_wind', dict(dur=LOOP_BED, seed=1), -36.0, 0.01, 0.15, 'roof wind (S6, gusty)'),
    (504, 792, 'tlb_fan', dict(dur=LOOP_BED), -46.0, 0.2, 0.05, 'edit room: laptop fan (steady)'),
    (504, 792, 'room_tone', dict(dur=LOOP_BED, seed=1), -44.0, 0.2, 0.05, 'edit room tone'),
    (792, 810, 'tlb_wind', dict(dur=LOOP_BED, seed=2), -40.0, 0.05, 0.004, 'evening roof air'),
    (810, 828, 'tlb_wind', dict(dur=LOOP_BED, seed=2), -50.0, 0.004, 0.004, 'DROP-OUT: wind only, far'),
    (828, 936, 'tlb_wind', dict(dur=LOOP_BED, seed=2), -42.0, 0.004, 0.02, 'evening roof air (payoff)'),
    (828, 936, 'outdoor_birds', dict(dur=LOOP_BED, seed=1), -46.0, 0.3, 0.02, 'evening birds, sparse'),
    (936, 1152, 'room_tone', dict(dur=LOOP_BED), -42.0, 0.02, 0.3, 'CRT room: outro + seam + hook'),
]

# TV static (tlb_static) follows the signal clock: LUFS in the stem = base + 14 * TM.sig(f) on CRT shots, a constant far
# level on the roof (heard through the window). (f0, f1, base LUFS, sig dB, note); 10 ms ramps at the cuts.
STATIC_TABLE = [
    (0, 144, -49.0, 14.0, 'S1 CRT macro (hook)'),
    (144, 270, -54.0, 0.0, 'S2 roof: far, through the window'),
    (270, 342, -46.0, 14.0, 'S3 CRT room'),
    (378, 450, -46.0, 14.0, 'S5 CRT lock / slip'),
    (936, 1080, -49.0, 14.0, 'S13 CRT loop (= f0 world; = S1 level: continuous seam)'),
]


# ============================================================================================ local sounds
def _soft(x, drive):
    pk = float(np.max(np.abs(x))) + 1e-12
    return SJ.shape(np.asarray(x, dtype=np.float64) / pk, drive) * pk


def tlb_tv_lock(seed=0, pitch=1.0):
    """THE LOCK: 80 ms static swell gated out hard on the hit, low CRT thunk, 40 ms D6 'ping'. hit = the gate."""
    r = _rng(seed, 'tlb_tv_lock')
    h = 0.08
    out = np.zeros(_n(0.7))
    t = _t(h)
    st = A.colored(len(t), r, -1.0, 300.0, 11000.0) * (t / h) ** 1.5 * 0.22
    st[-_n(0.002):] *= np.linspace(1, 0, _n(0.002))
    A._add(out, st, 0.0)
    A._add(out, _thump(0.3, 62.0, 55.0, 0.018, 0.05, r, attack=0.0008, drive=2.2, noise=0.4, noise_lp=900.0,
                       click=0.25, click_band=(900.0, 4000.0)) * 0.8, h)
    tp = _t(0.12)
    f0 = D6 * float(pitch)
    ping = (np.sin(TWO_PI * f0 * tp) + 0.35 * np.sin(TWO_PI * 2 * f0 * tp)) * np.exp(-tp / 0.04) * 0.16
    ping *= np.clip(tp / 0.002, 0, 1)
    A._add(out, ping, h + 0.004)
    A._add(out, _click(0.04, r, (2500.0, 9000.0), 0.0012), h)
    return SJ._done(reverb(_st(out), 'room', wet_db=-22), h, -4.0, 'tlb_tv_lock')


def tlb_creak(seed=0, dur=0.3, pitch=1.0):
    """GI pipe turning in the rusted strap: stick-slip pulses (rate glides 38 -> 64 Hz) exciting pipe modes. hit = 0."""
    r = _rng(seed, 'tlb_creak')
    d = float(dur)
    t = _t(d + 0.12)
    out = np.zeros(len(t))
    k = float(pitch)
    tt = 0.004
    modes_f = np.array([610.0, 1470.0, 2630.0, 3880.0]) * k
    while tt < d - 0.01:
        u = tt / d
        rate = (38.0 + 26.0 * np.sin(np.pi * u)) * k * (1 + 0.12 * r.standard_normal())
        env = np.sin(np.pi * min(1.0, u * 1.05)) ** 0.6
        p = modal(0.06, modes_f * (1 + 0.01 * r.standard_normal()), [0.018, 0.012, 0.008, 0.005],
                  [1.0, 0.7, 0.45, 0.25], rng=r)
        p = np.asarray(p, dtype=np.float64)
        p = p if p.ndim == 1 else p.mean(1)
        A._add(out, p * env * (0.7 + 0.3 * r.random()), tt)
        tt += 1.0 / max(rate, 10.0)
    grit = bp(r.standard_normal(len(t)), 900.0, 4200.0, 2) * 0.04 * np.clip(np.sin(np.pi * np.clip(t / d, 0, 1)), 0, 1)
    x = out + grit
    return SJ._done(reverb(_st(x), 'room', wet_db=-20), 0.0, -10.0, 'tlb_creak', keep_until=d)


def tlb_clamp_tick(seed=0, pitch=0.0):
    """Clamp click: metal-on-metal transient + strap ring (pitch in semitones). hit = transient."""
    r = _rng(seed, 'tlb_clamp_tick')
    k = 2 ** (float(pitch) / 12)
    h = 0.003
    out = np.zeros(_n(0.4))
    c = _click(0.12, r, (1500.0, 9000.0), 0.0012,
               modes=[(2310.0 * k, 0.035, 0.5), (3870.0 * k, 0.022, 0.3), (5620.0 * k, 0.012, 0.2), (1240.0 * k, 0.05, 0.3)],
               low=(240.0, 0.008, 0.25))
    A._add(out, c, h)
    ring = modal(0.35, [2310.0 * k, 4720.0 * k], [0.12, 0.06], [0.06, 0.025], rng=r, split=1.5)
    ring = np.asarray(ring, dtype=np.float64)
    A._add(out, ring if ring.ndim == 1 else ring.mean(1), h + 0.001)
    return SJ._done(reverb(_st(out), 'room', wet_db=-22), h, -6.0, 'tlb_clamp_tick')


def tlb_gust(seed=0, dur=1.0):
    """Wind gust: band noise swelling to a peak at 45 % then decaying, a faint whistle on the peak. hit = start."""
    r = _rng(seed, 'tlb_gust')
    d = float(dur)
    x = A.noise_band(d + 0.3, r, [(0, 260.0), (0.45, 820.0), (1.0, 380.0)], bw=0.9, width=0.6)
    x = np.asarray(x, dtype=np.float64)
    t = _t(len(x) / SR)
    p = np.clip(t / d, 0, 1.3)
    env = np.where(p < 0.45, (p / 0.45) ** 1.6, np.exp(-(p - 0.45) / 0.35))
    wh = A.noise_band(d + 0.3, r, [(0, 900.0), (0.45, 1350.0), (1.0, 1000.0)], bw=0.06, width=0.3)
    wh = np.asarray(wh, dtype=np.float64)
    y = _st(x) * env[:, None] + _st(wh) * (env ** 2)[:, None] * 0.25
    return SJ._done(y, 0.0, -8.0, 'tlb_gust', keep_until=d)


def tlb_buzz(seed=0, dur=0.35):
    """Phone vibration on a wooden desk: 170 Hz eccentric-motor rattle + wood body. hit = start."""
    r = _rng(seed, 'tlb_buzz')
    d = float(dur)
    t = _t(d + 0.08)
    f = 170.0 * (1 + 0.02 * np.sin(TWO_PI * 9 * t)) * (1 - np.exp(-t / 0.02))
    ph = TWO_PI * np.cumsum(f) / SR
    motor = np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.7
    rattle = bp(r.standard_normal(len(t)), 1200.0, 5000.0, 2) * np.clip(np.sin(ph), 0, 1) ** 8 * 0.6
    body = lp(motor, 1400.0, 2)
    env = np.clip(t / 0.015, 0, 1) * np.clip((d - t) / 0.03, 0, 1)
    x = (body + rattle) * env
    x = x + bp(x, 160.0, 520.0, 2) * 1.5
    return SJ._done(reverb(_st(x), 'room', wet_db=-22), 0.0, -10.0, 'tlb_buzz', keep_until=d)


PAYOFF_LAYERS = [dict(t=0.0, name='dhol_hit', gain_db=0, params=dict(pitch=1.0)),
                 dict(t=0.0, name='impact_soft', gain_db=-2),
                 dict(t=0.0, name='sub_drop', gain_db=-6, params=dict(dur=1.4), lp=140)]


def tlb_payoff(seed=0):
    """The f828 payoff as one designed sound: dhol + impact_soft + sub (LP 140), saturated (drive 3, loudness-
    matched) so its crest is low. hit = start (cue align 'start' on f828: nothing sounds inside the drop-out)."""
    out, h = SJ.render_cues(PAYOFF_LAYERS, seed)
    out = out[_n(max(h - 0.004, 0.0)):]
    out = _soft(out, 3.0)
    return SJ._done(out, 0.004, 0.0, 'tlb_payoff')


def tlb_static(dur=LOOP_BED, seed=0):
    """Bed: CRT static, warm hiss (300 Hz-11 kHz, -1 dB/oct), 15 fps grain flicker (2-frame hold, whole steps per loop),
    a faint 15.625 kHz line whine. Seamless loop."""
    r = _rng(seed, 'tlb_static')
    L = _n(dur)
    tl = np.arange(L) / SR
    a = A.colored(L, r, -1.0, 300.0, 11000.0)
    b = A.colored(L, r, -1.0, 300.0, 11000.0)
    y = np.stack([a, 0.7 * a + 0.71 * b], 1)
    steps = int(round(dur * 15))
    lv = 1 + 0.18 * r.standard_normal(steps)
    idx = (tl * 15).astype(int) % steps
    g = lv[idx]
    g = np.convolve(np.concatenate([g[-240:], g, g[:240]]), np.ones(240) / 240, mode='same')[240:240 + L]
    y *= g[:, None]
    y += _st(np.sin(TWO_PI * round(15625.0 * dur) / dur * tl) * 0.006)
    return SJ._bed_done(y, 'tlb_static')


def tlb_wind(dur=LOOP_BED, seed=0):
    """Bed: roof air, brown-ish noise LP 1.1 kHz, gusty AM with whole cycles per loop (2 + 5 cycles), faint high air.
    Seamless loop."""
    r = _rng(seed, 'tlb_wind')
    L = _n(dur)
    tl = np.arange(L) / SR
    a = A.colored(L, r, -4.5, 40.0, 1400.0)
    b = A.colored(L, r, -4.5, 40.0, 1400.0)
    y = np.stack([a, 0.5 * a + 0.87 * b], 1)
    ph = r.random(2) * TWO_PI
    am = 1 + 0.35 * np.sin(TWO_PI * 2 / dur * tl + ph[0]) + 0.15 * np.sin(TWO_PI * 5 / dur * tl + ph[1])
    y *= am[:, None]
    air = A.colored(L, r, -2.0, 2500.0, 8000.0)
    y += _st(air * 0.08 * am ** 2)
    return SJ._bed_done(y, 'tlb_wind')


def tlb_fan(dur=LOOP_BED, seed=0):
    """Bed: laptop fan at steady load (the catalog laptop_fan is a spin-up one-shot): soft air (pink, 120 Hz-7 kHz, gentle
    lp) + a faint blade-pass tone near 925 Hz with +-0.4 % drift (whole cycles per loop). Seamless loop."""
    r = _rng(seed, 'tlb_fan')
    L = _n(dur)
    tl = np.arange(L) / SR
    a = A.colored(L, r, -3.0, 120.0, 7000.0)
    b = A.colored(L, r, -3.0, 120.0, 7000.0)
    y = np.stack([a, 0.6 * a + 0.8 * b], 1)
    f0 = round(925.0 * dur) / dur
    fm = (1 + 0.004 * np.sin(TWO_PI * 3 / dur * tl))
    ph = TWO_PI * np.cumsum(f0 * fm) / SR
    ph *= round(ph[-1] / TWO_PI) * TWO_PI / ph[-1]           # whole cycles: seamless
    tone = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * 0.035
    y += _st(tone)
    return SJ._bed_done(y, 'tlb_fan')


META = dict(  # name: (category, character, use, send dB or None)
    tlb_tv_lock=('impact', 'static gate-out + CRT thunk + D6 ping', 'the lock f90 / f378 / f720', -22.0),
    tlb_creak=('texture', 'GI pipe stick-slip squeal in a rusted strap', 'antenna turns', None),
    tlb_clamp_tick=('ui', 'metal clamp click + strap ring', 'clamp ticks on the 8ths', -24.0),
    tlb_gust=('texture', 'wind gust swell + faint whistle', 'f342 gust', None),
    tlb_buzz=('ui', 'phone vibration on wood', 'phone buzz', None),
    tlb_payoff=('impact', 'dhol + impact + sub, saturated (low crest)', 'f828 payoff', -22.0),
    tlb_static=('bed', 'CRT static, seamless', 'CRT shots (signal-driven)', None),
    tlb_wind=('bed', 'roof air, gusty, seamless', 'roof shots', None),
    tlb_fan=('bed', 'laptop fan steady, seamless', 'edit room', None),
)


def register():
    """Register epic_sfx + sfx_jawad + the local sounds (idempotent)."""
    ES.register()
    SJ.register()
    changed = False
    for n, (cat, ch, use, send) in META.items():
        fn = globals()[n]
        cur = A.SOUNDS.get(n)
        if cur is not None and cur['fn'] is fn:
            continue
        A._register(cat, ch, use, send)(fn)
        changed = True
    if changed:
        A._sound_cached.cache_clear()


# ============================================================================================ cues
def raw_cues():
    """CUE_TABLE -> audio.py cue dicts (t in seconds, frame-exact)."""
    register()
    out = []
    for f, name, g, o, ev in CUE_TABLE:
        o = dict(o)
        c = dict(t=F(f), name=name, gain_db=float(g), pan=float(o.pop('pan', 0.0)), align=o.pop('align', 'hit'),
                 params=dict(o.pop('params', {})), frame=f, event=ev, gate=bool(o.pop('gate', True)))
        c.update(o)
        if name not in A.SOUNDS:
            raise KeyError('unknown sound %r (cue f%s)' % (name, f))
        out.append(c)
    return out


def vo_words():
    p = os.path.join(VOD, 'words.json')
    return json.load(open(p, encoding='utf8')) if os.path.exists(p) else None


def cues(report=False):
    """Cues after the VO fit (sfx_jawad.fit_under_vo, hero='warn'). Without a VO stem: the raw table."""
    cl = raw_cues()
    words = vo_words()
    rep = None
    if words:
        fit = [c for c in cl if c.get('vo', True) is not False]
        rest = [c for c in cl if c.get('vo', True) is False]
        fit, rep = SJ.fit_under_vo(fit, [(w['start'], w['end']) for w in words], hero='warn', report=True,
                                   depth_db=FIT_DEPTH_DB, mid_extra_db=-1.0, vo_audio=os.path.join(VOD, 'vo_stem.wav'))
        cl = sorted(fit + rest, key=lambda c: float(c['t']))
    return (cl, rep) if report else cl


def _gate():
    g = np.ones(N)
    ia, ib = DROP[0] * SPF, DROP[1] * SPF
    g[ia - 64:ia] = np.linspace(1, 0, 64)
    g[ia:ib] = 0.0
    return g


def render_fx(cue_list):
    """Circular cue render: duck_under, placement (wraps), room send. Returns (gated bus, pass bus, placed)."""
    cs = A.duck_under([A._norm_cue(c) for c in cue_list])
    buses = {True: np.zeros((N, 2)), False: np.zeros((N, 2))}
    sends = {True: np.zeros((N, 2)), False: np.zeros((N, 2))}
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        y, hit = A._render_cue(c, counts[k] % 4)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        gk = bool(c.get('gate', True))
        SJ._add_wrap(buses[gk], np.asarray(y, dtype=np.float64), start)
        cat = A.SOUNDS[c['name']]['category']
        sdb = c.get('send_db', A.SOUNDS[c['name']]['send'] if A.SOUNDS[c['name']]['send'] is not None
                    else A._CAT_SEND[cat])
        if sdb is not None and sdb > -60:
            SJ._add_wrap(sends[gk], np.asarray(y, dtype=np.float64) * undb(sdb), start)
        placed.append(dict(frame=c.get('frame'), t=round(float(c['t']), 4), name=c['name'], start=round(start, 4),
                           hit=round(start + hit, 4), hit_f=round((start + hit) * FPS, 3), len=round(len(y) / SR, 3),
                           align=c['align'], gain_db=round(float(c['gain_db']), 2), duck_db=c.get('duck_db', 0.0),
                           vo_fit=c.get('vo', ''), lp=c.get('lp'), hp=c.get('hp'), gate=gk, hero=bool(c.get('hero')),
                           event=c.get('event', '')))
    for gk in (True, False):
        if np.any(sends[gk]):
            buses[gk] += A.reverb_circular(sends[gk], 'studio', wet_db=0.0) - sends[gk]
    return buses[True] * _gate()[:, None], buses[False], placed


def _seg_env(n, fin, fout):
    e = np.ones(n)
    a, b = min(n, max(2, _n(fin))), min(n, max(2, _n(fout)))
    e[:a] = 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
    e[-b:] = np.minimum(e[-b:], 0.5 + 0.5 * np.cos(np.pi * np.arange(1, b + 1) / b))
    return e


def static_curve():
    """Per-sample gain (linear, relative to the loop at 0 LUFS offset) of the TV static from STATIC_TABLE x TM.sig."""
    import thoda_left_bas_music as TM
    fr_ = np.arange(NF)
    sg = np.asarray(TM.sig(fr_), dtype=np.float64)
    t = np.arange(N) / SR
    s_t = np.interp(t * FPS, fr_, sg)
    g = np.zeros(N)
    for f0, f1, base, k, note in STATIC_TABLE:
        i0, i1 = f0 * SPF, f1 * SPF
        lvl = undb(base + k * s_t[i0:i1])
        g[i0:i1] += lvl * _seg_env(i1 - i0, 0.01, 0.01)
    return g


def beds():
    """BED_TABLE + the signal-driven static -> bed bus at absolute stem levels (circular). Rows spanning exactly the
    drop-out pass the drop-out gate (they ARE the drop-out); everything else is gated."""
    register()
    out = np.zeros((N, 2))
    keep = np.zeros((N, 2))
    info = []
    for f0, f1, name, prm, lufs, fin, fout, note in BED_TABLE:
        loop = np.asarray(A.sound(name, **prm), dtype=np.float64)
        Lp = len(loop)
        assert N % Lp == 0, (name, Lp)
        g = undb(lufs - A.loudness(loop))
        idx = np.arange(f0 * SPF, f1 * SPF)
        seg = loop[idx % Lp] * g
        dst = keep if (f0, f1) == DROP else out
        dst[idx % N] += seg * _seg_env(len(seg), fin, fout)[:, None]
        info.append(dict(f0=f0, f1=f1, name=name, params=prm, lufs=lufs, note=note))
    st = np.asarray(A.sound('tlb_static', dur=LOOP_BED), dtype=np.float64)
    st = st * undb(-A.loudness(st))
    sc = static_curve()
    out += st[np.arange(N) % len(st)] * sc[:, None]
    info.append(dict(name='tlb_static', table=[list(r) for r in STATIC_TABLE], note='base + 14 x TM.sig(f)'))
    return out * _gate()[:, None] + keep, info


def _circ(fn, x, pad=1.0):
    p = _n(pad)
    xx = np.concatenate([x[-p:], x, x[:p]])
    return fn(xx)[p:p + len(x)]


def _klufs(x, a, b):
    seg = x[max(0, _n(a)):max(_n(b), _n(a) + 480)]
    k = A.kweight(_st(seg))
    return float(-0.691 + 10 * np.log10(np.mean(np.sum(np.square(k), axis=1)) + 1e-20))


def word_floor_curve(bus, vo, words, keep=(), target=WORD_FLOOR_LU, max_db=WORD_FLOOR_MAX_DB, ramp=0.03, pad=0.02):
    """Gain curve (dB, per sample) that keeps the VO >= target LU over `bus` on every word (one-syllable words 1 LU
    less), K-weighted over the word span: cut = deficit (<= max_db), raised-cosine ramps of `ramp` s around the padded
    word; inside `keep` windows (hero transients) the curve stays 0 dB. -> (curve dB, rows)."""
    g = np.zeros(N)
    t = np.arange(N) / SR
    rows = []
    for w in words:
        a, b = w['start'] - pad, w['end'] + pad
        one = len(re.findall(r'[aeiou]+', w['word'].lower())) <= 1
        m = _klufs(vo, w['start'], w['end']) - _klufs(bus, w['start'], w['end'])
        need = (target - (1.0 if one else 0.0)) - m
        if need <= 0:
            continue
        cut = min(need, max_db)
        i0, i1 = max(0, _n(a - ramp)), min(N, _n(b + ramp))
        tt = t[i0:i1]
        up = np.clip((tt - (a - ramp)) / ramp, 0, 1)
        dn = np.clip(((b + ramp) - tt) / ramp, 0, 1)
        g[i0:i1] = np.minimum(g[i0:i1], -cut * (0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn))))
        rows.append(dict(word=w['word'], line=w.get('line'), t=round(w['start'], 3), margin_before=round(m, 1),
                         cut_db=round(cut, 1)))
    for k0, k1 in keep:
        i0, i1 = max(0, _n(k0)), min(N, _n(k1))
        g[i0:i1] = 0.0
    g = np.convolve(g, np.ones(_n(0.008)) / _n(0.008), mode='same')        # 8 ms smoothing: no gain steps
    return g, rows


def sfx_bus(cue_list=None):
    """-> (stem, fx part, bed part, report)."""
    cl, fitrep = cues(report=True) if cue_list is None else (cue_list, None)
    fx_g, fx_p, placed = render_fx(cl)
    fx = fx_g + fx_p
    bb, binfo = beds()
    pad = _n(1.0)
    fxx = np.concatenate([fx[-pad:], fx, fx[:pad]])
    bbx = np.concatenate([bb[-pad:], bb, bb[:pad]])
    bb = A.sidechain(bbx, fxx, depth_db=BED_DUCK_DB)[pad:pad + N]
    g = SFX_LUFS - A.loudness(fx)
    for _ in range(8):
        L = A.loudness(fx * undb(g) + bb)
        if abs(L - SFX_LUFS) < 0.02:
            break
        g += SFX_LUFS - L
    fx = fx * undb(g)
    gr = _circ(lambda z: A.compressor_gain(z, thresh_db=SFX_LUFS + 8.0, ratio=2.0), fx)
    fx = fx * undb(gr)[:, None]
    gl = np.ones(N)
    gr_cap = False
    for _ in range(12):
        y = fx + bb
        gl = _circ(lambda z: A.limiter_gain(z, SFX_TP - 0.3), y, 0.5)
        mgr = float(-db(gl.min()))
        y = y * gl[:, None]
        L = A.loudness(y)
        tp_ok = A.true_peak(y) <= SFX_TP
        if mgr > SFX_GR_MAX + 0.05:                  # never limit more than SFX_GR_MAX
            k = undb(-(mgr - SFX_GR_MAX))
            gr_cap = True
        elif not gr_cap and abs(L - SFX_LUFS) >= 0.03:
            k = undb(SFX_LUFS - L)
        elif tp_ok:
            break
        else:
            k = undb(-0.2)
        fx, bb = fx * k, bb * k
    fx_o, bb_o = fx * gl[:, None], bb * gl[:, None]
    stem = fx_o + bb_o
    pre = fx + bb                                 # glued, before the stem limiter (source of sfx_vo.wav)
    rep = dict(lufs=round(A.loudness(stem), 3), true_peak_dbtp=round(A.true_peak(stem), 3),
               lra=round(A.loudness_range(stem), 2), glue_max_gr_db=round(float(-np.min(gr)), 2),
               limiter_max_gr_db=round(float(-db(gl.min())), 2), limiter_capped=gr_cap,
               limiter_gr_over_1db_s=round(float(np.sum(gl < undb(-1.0)) / SR), 3),
               bed_lufs=round(A.loudness(bb_o), 2), beds=binfo, placed=placed, _pre=pre,
               vo_fit=None if fitrep is None else {k: fitrep[k] for k in ('ducked', 'spans', 'violations',
                                                                         'heroes_ok', 'hero_source')})
    return stem, fx_o, bb_o, rep


def sfx_for_vo(stem, placed):
    """The SFX stem the VO mixes use: the glued SFX bus BEFORE the stem limiter at SFX_MIX_LUFS, transient-capped
    (true peak <= integrated + SFX_VO_CREST), then the VO word floor (two passes, no re-levelling). Written at true peak
    -2.5 dBTP; its integrated loudness is the mix level (epic_mix spec sfx_lufs). -> (array, report)."""
    words = vo_words()
    vo = _st(vo_ride())
    keep = [(p['hit'] - 0.002, p['hit'] + HERO_KEEP_S) for p in placed if p.get('hero')]
    x = stem * undb(SFX_MIX_LUFS - A.loudness(stem))
    Lx = A.loudness(x)
    glx = _circ(lambda z: A.limiter_gain(z, Lx + SFX_VO_CREST), x, 0.5)
    cap_gr = float(-db(glx.min()))
    x = x * glx[:, None]
    total = np.zeros(N)
    rows = []
    for _ in range(2):
        gc, r_ = word_floor_curve(x, vo, words, keep)
        rows = rows or r_
        total += gc
        x = x * undb(gc)[:, None]
    mix_lufs = A.loudness(x)
    y = x * undb(-2.5 - A.true_peak(x))
    after = [round(_klufs(vo, w['start'], w['end']) - _klufs(x, w['start'], w['end']), 1) for w in words]
    return y, dict(sfx_level_before_floor=SFX_MIX_LUFS, mix_lufs=round(mix_lufs, 2), target_lu=WORD_FLOOR_LU,
                   max_db=WORD_FLOOR_MAX_DB, words_cut=rows, max_cut_db=round(float(-total.min()), 1),
                   min_margin_after=min(after), tp_dbtp=round(A.true_peak(y), 2), lufs=round(A.loudness(y), 2),
                   crest_cap_db=SFX_VO_CREST, crest_cap_max_gr_db=round(cap_gr, 2))


# ============================================================================================ build
def _music_stale():
    m = os.path.join(AUD, 'music.wav')
    src = os.path.join(HERE, MODULE + '_music.py')
    vo = os.path.join(VOD, 'words.json')
    newest = max(os.path.getmtime(src), os.path.getmtime(vo) if os.path.exists(vo) else 0)
    return (not os.path.exists(m)) or os.path.getmtime(m) < newest


PROTECT = [(F(PAYOFF) - 0.02, F(PAYOFF) + 0.6)] + [(F(f) - 0.05, F(f) + 0.3) for f in LOCKS]
HERO_F = (90, 234, 378, 720, 828)


def vo_ride():
    """vo_stem.wav x VO_RIDE (per-line dB, raised-cosine 40 ms ramps 60 ms outside the line's voice) + a peak tamer
    (true peak <= integrated + VO_CREST) -> vo_mix.wav (the VO the mixes and the word floor use)."""
    v, _ = A.read_wav(os.path.join(VOD, 'vo_stem.wav'))
    v = np.asarray(v, dtype=np.float64)
    v = v[:, 0] if v.ndim == 2 else v
    words = vo_words()
    g = np.zeros(N)
    t = np.arange(N) / SR
    for lid, d in VO_RIDE.items():
        ws = [w for w in words if w['line'] == lid]
        a, b = ws[0]['start'] - 0.06, ws[-1]['end'] + 0.06
        up = np.clip((t - (a - 0.02)) / 0.04, 0, 1)
        dn = np.clip(((b + 0.02) - t) / 0.04, 0, 1)
        g += d * (0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn)))
    y = _st(v * undb(g))
    L = A.loudness(y)
    gl = _circ(lambda z: A.limiter_gain(z, L + VO_CREST), y, 0.5)
    y = y * gl[:, None]
    VO_PEAK['max_gr_db'] = round(float(-db(gl.min())), 2)
    VO_PEAK['ms_over_1db'] = round(float(np.sum(gl < undb(-1.0)) / SR * 1000), 1)
    A._write_wav(os.path.join(VOD, 'vo_mix.wav'), y, 24)
    return y


def music_ride():
    """music.wav x MUSIC_RIDE (dB segments with raised-cosine attack / release ramps) -> music_mix.wav."""
    m, _ = A.read_wav(os.path.join(AUD, 'music.wav'))
    g = np.zeros(N)
    t = np.arange(N) / SR
    for row in MUSIC_RIDE:
        f0, f1, d, ramp = row[:4]
        att = row[4] if len(row) > 4 else 0.0
        a, b = F(f0), F(f1)
        seg = ((t >= a) & (t < b)).astype(float)
        if att > 0:
            seg = seg * (0.5 - 0.5 * np.cos(np.pi * np.clip((t - a) / att, 0, 1)))
        if ramp > 0:
            seg = np.maximum(seg, np.where(t >= b, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - b) / ramp, 0, 1)), 0.0))
        g += d * seg
    y = _st(m) * undb(g)[:, None]
    A._write_wav(os.path.join(AUD, 'music_mix.wav'), y, 24)
    return y


def mix(spec=None):
    """A = VO + SFX + music, B = VO + SFX via epic_mix.mix_reel(loop=True, word floor 8 LU). Writes mix_A.wav,
    mix_B.wav, stems/stem_{vo,sfx,music}.wav, mix.json, mix.png."""
    work = os.path.join(AUD, '_mixwork')
    os.makedirs(work, exist_ok=True)
    lv = json.load(open(os.path.join(AUD, 'sfx_cues.json')))['sfx_vo']['mix_lufs']
    sp = dict(sfx_lufs=lv, music_duck_sfx_db=MUSIC_DUCK_SFX_DB)
    sp.update(spec or {})
    music_ride()
    rep = EX.mix_reel(MODULE, DUR, vo=os.path.join(VOD, 'vo_mix.wav'), music=os.path.join(AUD, 'music_mix.wav'),
                      sfx=os.path.join(AUD, 'sfx_vo.wav'), out_dir=work, words=os.path.join(VOD, 'words.json'),
                      word_floor_lu=8.0, music_gain_db=MUSIC_GAIN_DB, loop=True, protect=PROTECT, protect_cap_db=0.0,
                      hero_times=[F(f) for f in HERO_F], spec=sp, verbose=False)
    os.makedirs(os.path.join(AUD, 'stems'), exist_ok=True)
    moves = {'%s_mix.wav' % MODULE: 'mix_A.wav', '%s_vo_sfx.wav' % MODULE: 'mix_B.wav',
             '%s_stem_vo.wav' % MODULE: 'stems/stem_vo.wav', '%s_stem_sfx.wav' % MODULE: 'stems/stem_sfx.wav',
             '%s_stem_music.wav' % MODULE: 'stems/stem_music.wav', '%s_mix.png' % MODULE: 'mix.png',
             '%s_mix.json' % MODULE: 'mix.json'}
    for a, b in moves.items():
        if os.path.exists(os.path.join(work, a)):
            shutil.move(os.path.join(work, a), os.path.join(AUD, b))
    shutil.rmtree(work, ignore_errors=True)
    keep = {k: rep.get(k) for k in ('integrated_lufs', 'true_peak_dbtp', 'lra_lu', 'checks', 'vo_lufs_in_mix',
                                    'sfx_lufs_in_mix', 'music_lufs_in_mix', 'vo_over_music_lu', 'vo_over_sfx_lu',
                                    'vo_over_bed_lu', 'warnings')}
    keep['B'] = {k: rep['B_vo_sfx'].get(k) for k in ('lufs', 'tp_dbtp', 'lra', 'limiter_max_gr_db')}
    keep['A'] = {k: rep['A_full'].get(k) for k in ('lufs', 'tp_dbtp', 'lra', 'limiter_max_gr_db', 'glue_max_gr_db',
                                                   'limiter_gr_over_3db_s', 'loop_continuity_error_dbfs', 'seam')}
    w = rep.get('words') or {}
    keep['words'] = {k: w.get(k) for k in ('n', 'min_over_bed_lu', 'below', 'below_one_syllable', 'ok', 'floor_lu')
                     if k in w} if isinstance(w, dict) else w
    return keep


def build():
    register()
    os.makedirs(AUD, exist_ok=True)
    stem, fx, bb, rep = sfx_bus()
    A._write_wav(os.path.join(AUD, 'sfx.wav'), stem, 24)
    A._write_wav(os.path.join(AUD, 'sfx_fx.wav'), fx, 24)
    A._write_wav(os.path.join(AUD, 'sfx_bed.wav'), bb, 24)
    sv, frep = sfx_for_vo(rep.pop('_pre'), rep['placed'])
    A._write_wav(os.path.join(AUD, 'sfx_vo.wav'), sv, 24)
    rep['sfx_vo'] = frep
    rep['vo_mix'] = dict(ride_db=VO_RIDE, crest_db=VO_CREST, **VO_PEAK)
    json.dump(rep, open(os.path.join(AUD, 'sfx_cues.json'), 'w'), indent=1, ensure_ascii=False, default=str)
    print('sfx_vo.wav: word floor max cut %.1f dB, min VO margin %.1f LU; in the mix at %.2f LUFS (%s before the floor)'
          % (frep['max_cut_db'], frep['min_margin_after'], frep['mix_lufs'], SFX_MIX_LUFS))
    print('sfx.wav  %.2f LUFS  TP %.2f dBTP  glue %.1f dB  limiter %.1f dB (%.2f s > 1 dB)' % (
        rep['lufs'], rep['true_peak_dbtp'], rep['glue_max_gr_db'], rep['limiter_max_gr_db'], rep['limiter_gr_over_1db_s']))
    if _music_stale():
        import thoda_left_bas_music as MU
        MU.build('A')
    spec = None
    for attempt in range(3):
        mrep = mix(spec)
        aac = {k: _aac_ebur(os.path.join(AUD, 'mix_%s.wav' % k)) for k in 'AB'}
        if max(v['TP'] for v in aac.values()) <= -1.6:
            break
        c = -2.3 - 0.5 * (attempt + 1)
        spec = dict(limiter_ceiling_dbfs=c, tp_max_dbtp=c + 0.3)
        print('AAC true peak %.2f dBTP > -1.6: re-mastering with the limiter at %.1f dBFS' % (
            max(v['TP'] for v in aac.values()), c))
    mrep['aac'] = aac
    mrep['limiter_spec'] = spec
    json.dump(mrep, open(os.path.join(AUD, 'mix_summary.json'), 'w'), indent=1, default=str)
    print(json.dumps({k: mrep[k] for k in ('A', 'B', 'aac', 'checks', 'words')}, indent=1, default=str))
    return verify()


# ============================================================================================ verify
def ebur128(p, extra=()):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', *extra, '-i', p, '-af', 'ebur128=peak=true', '-f', 'null',
                        '-'], capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    get = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))  # noqa: E731
    return dict(I=get('I'), LRA=get('LRA'), TP=get('Peak'))


def _aac_ebur(wav):
    m4a = os.path.join(AUD, '_aac_check.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', m4a],
                   check=True)
    r = ebur128(m4a)
    os.remove(m4a)
    return r


def onsets(x, hop=120, nfft=1024, k=1.5, min_gap=0.06):
    """Spectral-flux onsets (2.5 ms hop, adaptive threshold). -> (times s, strengths)."""
    m = _st(x).mean(1)
    _, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop, boundary='zeros', padded=True)
    M = np.log1p(np.abs(Z) * 1000.0)
    fl = np.concatenate([[0.0], np.maximum(np.diff(M, axis=1), 0).sum(0)])
    w = int(1.0 * SR / hop)
    med = median_filter(fl, w, mode='wrap')
    mad = median_filter(np.abs(fl - med), w, mode='wrap')
    thr = med + k * np.maximum(mad, 1e-9) + 0.02 * fl.max()
    g = int(min_gap * SR / hop)
    i = np.nonzero((fl == maximum_filter1d(fl, 2 * g + 1, mode='wrap')) & (fl > thr))[0]
    return tt[i] - nfft / SR / 2 + hop / SR, fl[i]


def _mom(x, t, win=0.4):
    """Momentary (K-weighted, ungated) loudness of the window centred at t (circular)."""
    a = _n(t - win / 2)
    idx = (a + np.arange(_n(win))) % len(x)
    k = A.kweight(x[idx])
    return float(-0.691 + 10 * np.log10(np.mean(np.sum(np.square(k), axis=1)) + 1e-20))


HEROES = {0: 'f0 transient', 90: 'LOCK 1 (BAS BAS!)', 136: 'slip glitch', 342: 'clamp tick 1', 360: 'marks align',
          378: 'LOCK 2 (film starts)', 551: 'X nudge click', 720: 'LOCK 3 (client BAS BAS!)', 828: 'PAYOFF'}


def _rise(x, t, before=0.08, after=0.06):
    """Time (s, relative to t) of the steepest rise of the 1 ms RMS envelope (5 ms smoothed) in [t - before, t + after],
    circular. Used for f0, where the f1080 reverse swell and the f0 impact are 36 ms apart: the flux detector's 60 ms
    minimum gap merges them into one onset."""
    m = _st(x).mean(1)
    idx = (_n(t) + np.arange(-_n(before), _n(after))) % len(m)
    env = np.sqrt(np.convolve(m[idx] ** 2, np.ones(48) / 48, mode='same'))
    e5 = np.convolve(env, np.ones(240) / 240, mode='same')
    return (int(np.argmax(np.diff(e5))) - _n(before)) / SR


def keyframes(mixA, sfx, music, placed):
    out = {}
    ot, _ = onsets(sfx)
    sync = []
    for f, what in HEROES.items():
        t = F(f)
        if f == 0:
            d0 = _rise(sfx, 0.0)
            sync.append(dict(f=f, what=what + ' (envelope rise; the flux detector merges it with the f1080 swell)',
                             err_frames=round(d0 * FPS, 2), ok=bool(abs(d0) * FPS <= 1.0)))
            continue
        d = (ot - t + DUR / 2) % DUR - DUR / 2
        j = int(np.argmin(np.abs(d)))
        sync.append(dict(f=f, what=what, nearest_onset_t=round(float(ot[j]), 4),
                         err_frames=round(float(d[j]) * FPS, 2), ok=bool(abs(d[j]) * FPS <= 1.0)))
    out['sync_sfx_stem'] = sync
    lc_t, lc = A.loudness_curve(mixA, 0.4, 0.01)
    st_t, st = A.loudness_curve(mixA, 3.0, 0.05)
    i, j = int(np.argmax(lc)), int(np.argmax(st))
    win = lambda t0, t1: float(lc[(lc_t >= t0) & (lc_t <= t1)].max())  # noqa: E731
    out['loudest'] = dict(momentary_max_lufs=round(float(lc[i]), 2), momentary_max_at_s=round(float(lc_t[i]), 3),
                          momentary_max_at_f=round(float(lc_t[i]) * FPS, 1),
                          short_term_max_lufs=round(float(st[j]), 2), short_term_max_at_f=round(float(st_t[j]) * FPS, 1),
                          payoff_window_max=round(win(F(828), F(860)), 2),
                          lock_windows_max={f: round(win(F(f), F(f + 15)), 2) for f in LOCKS},
                          rest_max=round(max(win(0.3, F(826)), win(F(862), DUR - 0.3)), 2))
    out['loudest']['ok'] = bool(out['loudest']['payoff_window_max'] >= out['loudest']['rest_max'] - 0.2)
    out['dropout'] = dict(music_digital_silence_f810_f827=bool(not np.any(music[DROP[0] * SPF:DROP[1] * SPF])),
                          mix_momentary_f811_f819=round(_mom(mixA, F(815), 0.25), 2),
                          mix_momentary_swell_f821_f827=round(_mom(mixA, F(824), 0.2), 2),
                          mix_momentary_before_f797_f809=round(_mom(mixA, F(803), 0.4), 2),
                          ok=bool(_mom(mixA, F(815), 0.25) <= -36.0))
    w = _n(0.05)
    seam = np.concatenate([mixA[-w:], mixA[:w]])
    dd = np.abs(np.diff(seam, axis=0)).max(1)
    step = float(np.abs(mixA[0] - mixA[-1]).max())
    out['seam'] = dict(step=round(step, 6), local_p99_step=round(float(np.percentile(dd, 99)), 6),
                       momentary_last_0p4s=round(_mom(mixA, DUR - 0.2), 2), momentary_first_0p4s=round(_mom(mixA, 0.2), 2),
                       ok=bool(step <= max(float(np.percentile(dd, 99)), 1e-6) * 1.5))
    inst = {}
    for p in placed:
        inst.setdefault(round(p['hit_f']), []).append(p['name'])
    out['max_sounds_on_one_frame'] = max(len(v) for v in inst.values())
    out['frames_with_3_or_more'] = {k: v for k, v in sorted(inst.items()) if len(v) >= 3}
    out['ok'] = all(out[k]['ok'] for k in ('loudest', 'dropout', 'seam')) and all(s['ok'] for s in sync)
    return out


def overview(x, path, title, marks, placed=None, words=None):
    from PIL import Image, ImageDraw
    W, H = 1800, 640
    im = A.spectro_image(A.Sfx(x, 0, 'mix'), W, 440, None, title, '', fmin=30.0, fmax=20000.0, dyn=80.0)
    canvas = Image.new('RGB', (W, H), (14, 12, 16))
    canvas.paste(im, (0, 0))
    dr = ImageDraw.Draw(canvas)
    lc_t, lc = A.loudness_curve(x, 0.4, 0.02)
    y0, y1 = 460, 630
    lo, hi = -60.0, -5.0
    Y = lambda v: int(y1 - (np.clip(v, lo, hi) - lo) / (hi - lo) * (y1 - y0))  # noqa: E731
    for v in (-50, -40, -30, -20, -14, -10):
        dr.line([(0, Y(v)), (W, Y(v))], fill=(40, 38, 46))
        dr.text((2, Y(v) - 11), '%d' % v, fill=(120, 115, 130))
    dr.line([(int(t / DUR * W), Y(v)) for t, v in zip(lc_t, lc)], fill=(255, 181, 71), width=2)
    for b in range(16):
        xx = int(b * 72 / NF * W)
        dr.line([(xx, 44), (xx, y1)], fill=(70, 64, 84))
    if words:
        for w in words:
            dr.rectangle([int(w['start'] / DUR * W), 444, int(w['end'] / DUR * W), 452],
                         fill=(242, 49, 43) if w['keyword'] else (120, 200, 255))
    if placed:
        for p in placed:
            xx = int((p['hit'] % DUR) / DUR * W)
            dr.line([(xx, 432), (xx, 440)], fill=(200, 200, 220))
    for i, (f, lab, col) in enumerate(marks):
        xx = int(F(f) / DUR * W)
        dr.line([(xx, 44), (xx, y1)], fill=col)
        dr.text((xx + 3, 46 + 13 * (i % 4)), lab, fill=col)
    canvas.save(path)
    return path


def verify():
    register()
    rd = lambda n: A.read_wav(os.path.join(AUD, n))[0]  # noqa: E731
    files = dict(music='music.wav', sfx='sfx.wav', mix_A='mix_A.wav', mix_B='mix_B.wav', stem_vo='stems/stem_vo.wav',
                 stem_sfx='stems/stem_sfx.wav', stem_music='stems/stem_music.wav')
    rep = dict(ebur128={k: ebur128(os.path.join(AUD, v)) for k, v in files.items()})
    rep['aac'] = {k: _aac_ebur(os.path.join(AUD, files[k])) for k in ('mix_A', 'mix_B')}
    for k in files:
        pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,duration_ts',
                             '-of', 'json', os.path.join(AUD, files[k])], capture_output=True, text=True)
        rep.setdefault('format', {})[k] = json.loads(pr.stdout)['streams'][0]
    mA, mB, sx, mu = rd('mix_A.wav'), rd('mix_B.wav'), rd('sfx.wav'), rd('music.wav')
    sv, ss, sm = rd('stems/stem_vo.wav'), rd('stems/stem_sfx.wav'), rd('stems/stem_music.wav')
    rep['stems_sum_residual_dbfs'] = round(float(db(np.max(np.abs(sv + ss + sm - mA)) + 1e-12)), 1)
    placed = json.load(open(os.path.join(AUD, 'sfx_cues.json')))['placed']
    rep['keyframes_A'] = keyframes(mA, sx, mu, placed)
    kb = keyframes(mB, sx, np.zeros_like(mu), placed)
    rep['keyframes_B'] = {k: kb[k] for k in ('loudest', 'dropout', 'seam')}
    words = vo_words() or []

    def lk(x, a, b):
        seg = x[_n(a):max(_n(b), _n(a) + 480)]
        k = A.kweight(seg)
        return float(-0.691 + 10 * np.log10(np.mean(np.sum(np.square(k), axis=1)) + 1e-20))
    wm = []
    for w in words:
        v = lk(sv, w['start'], w['end'])
        wm.append(dict(word=w['word'], line=w['line'], t=w['start'], over_bed_A=round(v - lk(sm + ss, w['start'], w['end']), 1),
                       over_music=round(v - lk(sm, w['start'], w['end']), 1)))
    one = lambda s: len(re.findall(r'[aeiou]+', s.lower())) <= 1  # noqa: E731
    bad = [m for m in wm if m['over_bed_A'] < (7.0 if one(m['word']) else 8.0)]
    rep['vo_words'] = dict(n=len(wm), min_over_bed_A=min(m['over_bed_A'] for m in wm) if wm else None,
                           median_over_bed_A=float(np.median([m['over_bed_A'] for m in wm])) if wm else None,
                           min_over_music_A=min(m['over_music'] for m in wm) if wm else None,
                           below_rule=bad, ok=not bad)
    # VO over the music bed per line (integrated over the line span): the brief's "VO >= 8 LU over the bed"
    lines = {}
    for w in words:
        lines.setdefault(w['line'], [w['start'], w['end']])
        lines[w['line']][1] = w['end']
    rep['vo_lines_over_music_lu'] = {k: round(lk(sv, a, b) - lk(sm, a, b), 1) for k, (a, b) in lines.items()}
    e = rep['ebur128']
    rep['targets'] = dict(
        mix_A=bool(abs(e['mix_A']['I'] + 14) <= 0.5 and e['mix_A']['TP'] <= -2.0),
        mix_B=bool(abs(e['mix_B']['I'] + 14) <= 0.5 and e['mix_B']['TP'] <= -2.0),
        sfx=bool(e['sfx']['TP'] <= -2.0 and (abs(e['sfx']['I'] + 18) <= 0.3 or json.load(open(os.path.join(
            AUD, 'sfx_cues.json')))['limiter_max_gr_db'] <= SFX_GR_MAX + 0.05)),
        aac=bool(all(v['TP'] <= -1.5 and abs(v['I'] + 14) <= 0.5 for v in rep['aac'].values())),
        lra=bool(2.0 <= e['mix_A']['LRA'] <= 9.0),
        vo_lines_8lu=bool(all(v >= 8.0 for v in rep['vo_lines_over_music_lu'].values())),
        format=bool(all(v['codec_name'] == 'pcm_s24le' and int(v['sample_rate']) == SR and int(v['channels']) == 2
                        and int(v['duration_ts']) == N for v in rep['format'].values())))
    marks = [(0, 'f0', (255, 243, 230)), (90, 'f90 LOCK', (255, 181, 71)), (234, 'f234 kiska', (80, 230, 255)),
             (378, 'f378 LOCK', (255, 181, 71)), (504, 'f504 M3', (242, 49, 43)), (648, 'f648 split', (80, 230, 255)),
             (720, 'f720 LOCK', (255, 181, 71)), (810, 'f810 drop', (80, 230, 255)), (828, 'f828 PAYOFF', (255, 181, 71)),
             (954, 'f954 outro', (200, 160, 255))]
    rep['png'] = [overview(mA, os.path.join(AUD, 'mix_A_overview.png'), '%s mix_A (VO + SFX + music)  %.1f LUFS  TP %.1f dBTP'
                           '  (curve = momentary 400 ms, bars = VO words)' % (MODULE, e['mix_A']['I'], e['mix_A']['TP']),
                           marks, placed, words),
                  overview(mB, os.path.join(AUD, 'mix_B_overview.png'), '%s mix_B (VO + SFX)  %.1f LUFS  TP %.1f dBTP' % (
                      MODULE, e['mix_B']['I'], e['mix_B']['TP']), marks, placed, words),
                  overview(sx, os.path.join(AUD, 'sfx_overview.png'), '%s sfx.wav  %.1f LUFS  TP %.1f dBTP' % (
                      MODULE, e['sfx']['I'], e['sfx']['TP']), marks, placed, words)]
    rep['ok'] = all(rep['targets'].values()) and rep['keyframes_A']['ok'] and rep['vo_words']['ok']
    json.dump(rep, open(os.path.join(AUD, 'sound.verify.json'), 'w'), indent=1)
    print(json.dumps({k: rep[k] for k in ('ebur128', 'aac', 'targets', 'stems_sum_residual_dbfs', 'ok')}, indent=1))
    print(json.dumps({k: rep['vo_words'][k] for k in ('n', 'min_over_bed_A', 'median_over_bed_A', 'min_over_music_A', 'ok')},
                     indent=1))
    print(json.dumps(rep['vo_lines_over_music_lu']))
    print(json.dumps({k: rep['keyframes_A'][k] for k in ('loudest', 'dropout', 'seam')}, indent=1))
    return rep


# ============================================================================================ audition
AUDITION_SET = [('tlb_tv_lock', {}), ('tlb_creak', dict(dur=0.2)), ('tlb_creak', dict(dur=0.57, pitch=0.85)),
                ('tlb_clamp_tick', dict(pitch=0.0)), ('tlb_clamp_tick', dict(pitch=5.0)), ('tlb_gust', dict(dur=1.0)),
                ('tlb_buzz', {}), ('tlb_payoff', {})]


def audition():
    register()
    os.makedirs(AUDITION, exist_ok=True)
    rows = []
    for name, prm in AUDITION_SET:
        x = A.sound(name, **prm)
        a = np.asarray(x, dtype=np.float64)
        tag = name + ''.join('_%s%s' % (k, round(v, 3) if isinstance(v, float) else v) for k, v in prm.items())
        A.spectro_image(x, 1000, 420, x.hit, tag, 'hit %.3f s' % x.hit).save(os.path.join(AUDITION, tag + '.png'))
        st = A.stats(a, x.hit)
        q = A.qc(a, x.hit)
        rows.append(dict(sound=tag, dur=round(len(a) / SR, 3), hit=round(x.hit, 4), Mmax=st.get('Mmax'),
                         peak=st.get('peak'), crest=st.get('crest'), qc=q))
        print('%-40s dur %.2f hit %.3f Mmax %s qc %s' % (tag, len(a) / SR, x.hit, st.get('Mmax'), q or 'clean'))
    for bed in ('tlb_static', 'tlb_wind', 'tlb_fan'):
        b = A.sound(bed, dur=LOOP_BED)
        arr = np.asarray(b, dtype=np.float64)
        A.spectro_image(A.Sfx(arr, 0, bed), 1000, 420, None, bed, '7.2 s loop').save(os.path.join(AUDITION, bed + '.png'))
        step = float(np.abs(arr[0] - arr[-1]).max())
        rows.append(dict(sound=bed, dur=round(len(arr) / SR, 3), seam_step=round(step, 5),
                         p99_step=round(float(np.percentile(np.abs(np.diff(arr, axis=0)).max(1), 99)), 5)))
        print('%-40s dur %.2f seam step %.5f (p99 %.5f)' % (bed, len(arr) / SR, step, rows[-1]['p99_step']))
    json.dump(rows, open(os.path.join(AUDITION, 'audition.json'), 'w'), indent=1)
    return rows


def print_cues():
    cl, rep = cues(report=True)
    for c in cl:
        print('f%-7s %-18s %6.1f dB  %-5s %-22s %s' % (c['frame'], c['name'], c['gain_db'], c['align'],
                                                    str(c.get('vo', '')) + ('' if c['gate'] else ' [gate pass]'),
                                                    c['event']))
    if rep:
        print('hero violations:', json.dumps(rep['violations']))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('cues', 'audition', 'build', 'verify', 'mix'))
    a = ap.parse_args(argv)
    if a.cmd == 'cues':
        print_cues()
    elif a.cmd == 'audition':
        audition()
    elif a.cmd == 'build':
        sys.exit(0 if build()['ok'] else 1)
    elif a.cmd == 'mix':
        print(json.dumps(mix(), indent=1, default=str))
    else:
        sys.exit(0 if verify()['ok'] else 1)


if __name__ == '__main__':
    main()
