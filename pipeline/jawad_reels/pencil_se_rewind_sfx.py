#!/usr/bin/env python3
"""pencil_se_rewind_sfx.py: SFX layer, beds and the VO-led A / B mixes of Bijli series #1 "Pencil Se Rewind" (@jawad_mp4).
Owner: sound-designer (+ music-supervisor: the final mixes). Plan: SHOTS.md section B (cue list) retimed to the measured
VO (VO_TIMING.md section 3, LEAD_DECISIONS 3: picture beats move to the VO). Notes + measurements: SOUND.md.
Music: pencil_se_rewind_music.py. VO: pencil_se_rewind_vo.py (vo_stem.wav + words.json).

34.133 s = 1,024 f at 30 fps, 112.5 BPM (beat 16 f, bar 64 f), key D major. Nobody on the team can listen: every claim in
SOUND.md is a measurement or a rendered image.

RETIMING: edit CUE_TABLE / BED_TABLE below (frames), then `python3 pencil_se_rewind_sfx.py build`. Every cue sits on its
frame to the sample (frame f = sample f x 1,600); align 'hit' puts the designed hit on the frame (impacts = transient,
whooshes = loudest pass, risers / reverse swells = their end), 'start' starts it there. Placement is circular (tails past
f1023 land on f0: the outro ratchet and the f1024 reverse swell release into the hook).

Chain: cues -> sfx_jawad.fit_under_vo (non-hero cues inside a spoken word -6 dB, air hp 5.5 kHz, dark lp 1.1 kHz, mid
-2 dB more; spans over speech lp) -> audio.duck_under -> circular placement + 'studio' send -> drop-out gate (exact zero
f752-f767 except gate=False cues) -> SFX bus at -18 LUFS with the beds at absolute levels (sidechained 2 dB under the
SFX) -> 2:1 glue -> 4x true-peak limiter (circular) at -2.0 dBTP -> sfx.wav.
Mixes (epic_mix.mix_reel, loop=True, words=VO words, word_floor_lu=8 = LEAD_DECISIONS 1): mix_A = VO + SFX + music,
mix_B = VO + SFX (song-ready), both -14 LUFS / TP <= -2.0 dBTP; stems/stem_{vo,sfx,music}.wav at A's bus curve sum to A.

Local sounds (numpy only, no samples, no paid service; audio.qc() == [] at the used params, PNGs in <RW>/audio/audition/):
    psr_ratchet   hex pencil turning the cassette hub: 6 wood-on-POM ticks per revolution (one rev = 16 f at rate 1),
                  hub friction whir modulated per rev; rate 0.5 / 1 / 3; hit = start (cues start on multiples of 16 f,
                  so the tick phase is the global f mod 16 and f1023 -> f0 is continuous)
    psr_key       walkman piano key: two transients 8 ms apart (key + latch) + spring ring + ABS body thock; kind
                  'down' / 'up'; hit = first transient
    psr_motor     small DC capstan motor at speed: 180-260 Hz whine + harmonics + gear grind; hit = start
    psr_lid_pop   cassette lid springing open: latch click, spring twang (modal 0.9 / 1.5 kHz), plastic knock;
                  hit = the latch
    psr_crinkle   tape ribbon spilling (granular cellophane crinkle); reverse=1 = drawn back in; hit = start
    psr_rehook    the f464 slam as one designed sound: D7 (glitch_short + whip) + impact_soft + sub_drop (LP 160);
                  hit = the impact
    psr_payoff    the f768 payoff as one designed sound: PLAY clack + impact_soft + impact_big + sub (LP 140),
                  saturated (drive 3, loudness-matched) for a low crest; hit = the clack (cue align 'start')
    psr_hiss      bed: cassette hiss (2-12 kHz, 0.3 % wow AM), seamless 8.533 s loop (4 bars)

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh):
    python3 pencil_se_rewind_sfx.py cues        the cue table after the VO fit (frame, sound, gain, align, event)
    python3 pencil_se_rewind_sfx.py audition    local sounds -> <RW>/audio/audition/*.png + audition.json (qc)
    python3 pencil_se_rewind_sfx.py build       sfx.wav (+ sfx_fx / sfx_bed), music.wav if stale, mix_A.wav, mix_B.wav,
                                                stems/, sfx_cues.json, mix_summary.json, then verify
    python3 pencil_se_rewind_sfx.py verify      ebur128 (wav + AAC), key frames, VO margins, overview PNGs
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
from audio import (SR, TWO_PI, _t, _n, _rng, _st, _thump, _click, _crackle, modal, lp, hp, bp, undb, db,  # noqa: E402
                   reverb)
import epic_sfx as ES  # noqa: E402
import sfx_jawad as SJ  # noqa: E402
import epic_mix as EX  # noqa: E402

MODULE = 'pencil_se_rewind'
FPS, BPM, NF = 30, 112.5, 1024
DUR = NF / FPS
N = _n(DUR)
assert N == 1638400
SPF = SR // FPS
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
VOD = os.path.join(RW, 'vo')
AUDITION = os.path.join(AUD, 'audition')
SFX_LUFS, SFX_TP = -18.0, -2.0
BED, BED_GAIN_DB = None, -30.0                 # render.py must NOT rebuild this layer: mux mix_A.wav with --audio
DROP = (752, 768)                              # drop-out frames [f752, f768)
PAYOFF = 768
BED_DUCK_DB = 2.0
SFX_MIX_LUFS = -18.5                           # the SFX level inside the VO mixes (epic_mix spec sfx_lufs; house -18 is
                                               # for a text-led reel: here the VO covers 24 of 34 s)
WORD_FLOOR_LU = 12.5                           # VO (-16 LUFS in the mix) over the SFX on every word, before the mix's
WORD_FLOOR_MAX_DB = 18.0                       # 4 dB VO sidechain; with the music word floor -> >= 8 LU over the bed
FIT_DEPTH_DB = -3.0                            # fit_under_vo level step (carving lp / hp as usual); the word floor
                                               # below sets the real VO margins in the VO mixes
# gentle music level ride for the VO mixes (LEAD_DECISIONS 1: "try a gentle level ride first"): (f0, f1, dB, ramp s)
MUSIC_RIDE = [(768, 790, 3.0, 0.5)]            # the payoff band +3 dB over the rest of the music (f768-f789 + 0.5 s)
MUSIC_GAIN_DB = -3.0                           # music 3 dB under the spec's -18 LUFS (epic_mix re-levels music_mix.wav
                                               # by its integrated loudness, then this offset): the VO gaps stay open
VO_RIDE = {'V2': -0.5, 'V5': -1.0, 'V7': -2.5, 'V10': -2.5, 'V11': 0.5, 'V13': -1.0}   # per-line VO ride (dB) for the mixes: V7 is the whisper (it measured
                                               # the loudest VO momentary, K-weighted air), V10 the dry line before the
                                               # drop-out; V2 / V5 trimmed so the payoff stays the loudest; ramps 40 ms
                                               # inside the >= 0.12 s gaps. LEAD_DECISIONS 1: a ride, never a squash
VO_CREST = 12.0                                # vo_mix.wav: true peak <= integrated + 12 dB
VO_PEAK = {}
MUSIC_DUCK_SFX_DB = 1.5                        # music under the SFX in the mixes (spec 3 dB): the payoff keeps the band
SFX_VO_CREST = 14.0                            # sfx_vo.wav: true peak <= integrated + 13 dB (transient cap)
SFX_GR_MAX = 3.0                               # stem limiter cap: the stem's loudness follows (see SOUND.md)
HERO_KEEP_S = 0.035                            # a hero transient keeps its first 35 ms (the floor ducks its tail)
LOOP_BED = DUR / 4                             # 8.533 s = 4 bars = 409,600 samples (divides N)
GT = 2349.32 / 2096.3                          # glass_tap(seed 0) partial 2096.3 Hz -> D7 (bijli measurement)


def F(f):
    return f / FPS


# ============================================================================================ CUE TABLE (frames)
# (frame, sound, gain_db, options, visual event). options: align ('hit' default | 'start'), pan, lp, hp, rate, dur,
# params {}, seed, gate (False = passes the f752-f767 drop-out gate), hero (True = never ducked by the VO fit; a hit on a
# word is reported), vo (False = skip the VO fit). Frames follow VO_TIMING.md section 3 (picture moved to the VO).
CUE_TABLE = [
    # S1 hook A (f0-f63): pencil already turning; VO V1 f3-f62 "Rewind button? Pencil."
    (0, 'psr_ratchet', -14.0, dict(align='start', dur=round(64 / FPS + 0.04, 4), params=dict(dur=round(64 / FPS, 4), rate=1.0)),
     'R1 loop: pencil turns the hub, 1 rev per beat (f0-f63)'),
    (0, 'impact_soft', -12.0, dict(lp=900), 'frame-0 transient: release of the f1024 reverse swell'),
    (43, 'impact_soft', -9.0, dict(hero=True, lp=1400), '`Pencil.` slam (moved f16 -> f43, 0.1 s before the VO word)'),
    (43, 'shimmer', -18.0, dict(hp=5500, params=dict(dur=1.2)), '`Pencil.` glint'),
    # S2-S3 (f64-f191): walkman, then the hub crop; VO V2 f70-f186
    (128, 'psr_ratchet', -16.0, dict(align='start', dur=round(64 / FPS + 0.04, 4), params=dict(dur=round(64 / FPS, 4), rate=1.0)),
     'S3 hub crop: pencil teeth biting the hex (f128-f191)'),
    # S4 label (f192-f255) + D8 speed-ramp f256 + S5 fast rewind; VO V3 f198-f273
    (192, 'leaf_rustle', -20.0, dict(params=dict(dur=0.6), pan=0.1), 'S4 cut: paper label (track list)'),
    (256, 'riser', -12.0, dict(params=dict(duration=0.35)), 'D8 speed-ramp in (window f249-f262)'),
    (256, 'whoosh_fast', -8.0, {}, 'D8 speed-ramp pass'),
    (256, 'impact_soft', -6.0, {}, 'D8 lands on the fast rewind'),
    (256, 'psr_ratchet', -11.0, dict(align='start', dur=round(64 / FPS + 0.04, 4), params=dict(dur=round(64 / FPS, 4), rate=3.0)),
     'S5 R1 at a 3x clock: the fast rewind (f256-f319)'),
    # S6 keys (f320-f391); VO V4 "Play." f320 / "Galat!" f347 / "Phir se." f376
    (320, 'psr_key', -5.0, dict(params=dict(kind='down'), pan=-0.15), 'PLAY key down (spools 1x); music wrong spot'),
    (347, 'psr_key', -6.0, dict(params=dict(kind='down'), pan=-0.05), 'STOP key on "Galat!" (moved f336 -> f347)'),
    (347, 'psr_key', -14.0, dict(params=dict(kind='up'), pan=-0.15), 'PLAY key pops up'),
    (376, 'psr_key', -7.0, dict(params=dict(kind='down'), pan=0.1), 'REW key on "Phir se." (moved f340 -> f376)'),
    (376, 'psr_motor', -17.0, dict(align='start', vo=False, params=dict(dur=round(16 / FPS, 4), speed=1.6)),
     'REW motor, spools reversed 4x (f376-f391)'),
    # S7 lid window (f392-f447): 2nd PLAY; VO V5 "Mil gaya!" f395, "Aur phir..." f430
    (392, 'psr_key', -5.0, dict(params=dict(kind='down'), pan=-0.15), '2nd PLAY key + cut to S7 (moved f384 -> f392)'),
    (392, 'psr_motor', -28.0, dict(align='start', vo=False, params=dict(dur=round(56 / FPS, 4), speed=1.0)),
     'capstan motor at play speed under the right spot (f392-f447)'),
    # S8 re-hook (f448-f511): eaten tape; VO V6 f466-f505 after the slam
    (452, 'psr_lid_pop', -6.0, dict(pan=0.1), 'lid springs open (frames 0-5 of R4b)'),
    (458, 'psr_crinkle', -9.0, dict(align='start', params=dict(dur=0.87), pan=0.15), 'tape ribbon spills out (f458-f483)'),
    (464, 'psr_rehook', -13.0, dict(hero=True), 'RE-HOOK `phans gayi!` SLAM + D7 (45.3 %)'),
    # S9 rescue (f512-f575); VO V7 f509-f590 whispered
    (512, 'psr_ratchet', -14.0, dict(align='start', dur=round(64 / FPS + 0.04, 4), params=dict(dur=round(64 / FPS, 4), rate=0.5)),
     'R1b: pencil turns slowly, the loop is drawn back (f512-f575)'),
    (530, 'psr_crinkle', -18.0, dict(align='start', params=dict(dur=1.0, reverse=1), pan=0.1),
     'crinkled tape drawn back into the shell'),
    (576, 'riser', -14.0, dict(params=dict(duration=1.0)), 'riser into the reveal (f546-f575)'),
    # S10 reveal (f576-f639); VO V8 f594-f648
    (586, 'whoosh_slow', -12.0, {}, 'pull-back into the NLE viewer (inout_sine f576-f597: fastest f586)'),
    (600, 'glass_tap', -16.0, dict(seed=0, params=dict(pitch=round(GT, 4)), pan=0.2), 'timeline panel + header land (D7)'),
    # S11 scrub (f648-f703): one 8th later than SHOTS (V8 "hain." ends f648); V9 not in the VO (text-led)
    (648, 'jd_timeline_scrub', -8.0, dict(align='start', params=dict(duration=0.22, speed=-2.0), pan=-0.2),
     'playhead jumps BACK + `Peeche.`'),
    (656, 'jd_timeline_scrub', -8.0, dict(align='start', params=dict(duration=0.22, speed=2.0), pan=0.2),
     'playhead jumps FORWARD + `Aage.`'),
    (664, 'jd_timeline_scrub', -8.0, dict(align='start', params=dict(duration=0.22, speed=-2.0), pan=-0.2),
     'playhead jumps BACK + `Peeche.`'),
    (672, 'jd_timeline_scrub', -9.0, dict(align='start', params=dict(duration=0.18, speed=2.0), pan=0.15),
     'playhead lands on the CUT marker + `Yahan.`'),
    (672, 'ui_click', -13.0, {}, 'CUT marker chip pops'),
    (672, 'pop', -14.0, dict(params=dict(pitch=1.2)), 'CUT chip POP spring'),
    # S12 push into the timeline (f704-f767); VO V10 f698-f750; DROP-OUT f752-f767
    (724, 'whoosh_slow', -16.0, {}, 'push into the timeline (inout_cubic f704-f744: fastest f724)'),
    (768, 'reverse_swell', -22.0, dict(params=dict(duration=0.2), gate=False, vo=False),
     'swell f762 -> f768 at the end of the drop-out'),
    # S13 PAYOFF f768; VO V11 f769-f840 + V12 f843-f908
    (768, 'psr_payoff', -2.5, dict(align='start', gate=False, hero=True, dur=2.5),
     'PAYOFF: walkman PLAY clack = the downbeat + impact + body + sub (one saturated, low-crest sound)'),
    (832, 'ui_tick', -10.0, {}, 'pencil-playhead snaps to the cut on "Pencil." (moved f800 -> f832)'),
    (832, 'pop', -16.0, dict(params=dict(pitch=0.9)), 'clips glow FLAME on contact'),
    # D2 razor f896 + profile outro (card f896-f1023); VO V12 tail f897-f908, V13 f930-f995
    (896, 'ui_click', -6.0, dict(params=dict(pitch=0.8)), 'D2 razor cut'),
    (898, 'card_slide', -10.0, {}, 'D2: card slides'),
    (896, 'psr_ratchet', -20.0, dict(align='start', params=dict(dur=round(128 / FPS, 4), rate=1.0)),
     'S14 R1 loop under the card (global phase; continuous into f0)'),
    (899, 'swish_small', -14.0, dict(align='start'), 'outro: profile pill pops (PO t_pop 0.1 s)'),
    (933, 'glass_tap', -16.0, dict(seed=0, params=dict(pitch=round(GT, 4))), 'outro: card moves (PO t_move + 0.5 s)'),
    (941, 'shimmer', -14.0, dict(params=dict(dur=1.5)), 'outro: question lands (PO t_q + 0.2 s)'),
    (1024, 'reverse_swell', -12.0, dict(params=dict(duration=0.8)), 'loop: swell f1000 -> f1024 = f0'),
]

# (f0, f1, bed, params, LUFS in the -18 LUFS stem, fade in s, fade out s, note). f1 > 1024 wraps across the seam.
BED_TABLE = [
    (896, 1600, 'psr_hiss', dict(dur=LOOP_BED), -44.0, 0.6, 0.02, 'cassette hiss: outro, seam, hook .. S9 (to f576)'),
    (0, 752, 'room_tone', dict(dur=LOOP_BED), -40.0, 0.3, 0.004, 'warm room, whole reel up to the drop-out'),
    (464, 512, 'room_tone', dict(dur=LOOP_BED, seed=1), -42.0, 0.05, 0.3, 're-hook: the room opens up (+room)'),
    (752, 768, 'room_tone', dict(dur=LOOP_BED), -48.0, 0.004, 0.004, 'DROP-OUT: room tone only'),
    (768, 1024, 'room_tone', dict(dur=LOOP_BED), -40.0, 0.004, 0.3, 'payoff + outro room'),
]


# ============================================================================================ local sounds
def _mono(x):
    x = np.asarray(x, dtype=np.float64)
    return x if x.ndim == 1 else x.mean(1)


def _soft(x, drive):
    pk = float(np.max(np.abs(x))) + 1e-12
    return SJ.shape(np.asarray(x, dtype=np.float64) / pk, drive) * pk


def psr_ratchet(seed=0, dur=64 / FPS, rate=1.0):
    """Hex pencil turning a cassette hub: 6 ticks per revolution (rev = 16 frames / rate), hub whir. hit = start."""
    r = _rng(seed, 'psr_ratchet')
    d = float(dur)
    rev = (16 / FPS) / float(rate)
    t = _t(d + 0.06)
    out = np.zeros(len(t))
    k = 0
    while True:
        t0 = (k + 0.5) * rev / 6.0
        if t0 >= d - 0.004:
            break
        jit = 1 + 0.03 * r.standard_normal()
        c = _click(0.05, r, (1300.0, 6500.0), 0.0009,
                   modes=[(1950.0 * jit, 0.005, 0.45), (3350.0 * jit, 0.003, 0.25), (880.0 * jit, 0.007, 0.3)],
                   low=(310.0, 0.006, 0.35))
        acc = 1.0 if k % 6 == 0 else 0.72 + 0.1 * r.random()          # the hex arris that bites hardest
        A._add(out, c * acc * min(1.0, 0.75 + 0.25 / max(rate, 1.0)), t0)
        k += 1
    ph = TWO_PI * t / rev
    am = 0.55 + 0.45 * np.sin(ph) ** 2
    whir = bp(r.standard_normal(len(t)), 260.0, 1700.0, 2) * am * 0.05 * min(rate, 2.0)
    env = np.clip(t / 0.01, 0, 1) * np.clip((d - t) / 0.02, 0, 1)
    x = (out + whir) * env
    return SJ._done(reverb(_st(x), 'room', wet_db=-24), 0.0, -10.0, 'psr_ratchet', keep_until=d)


def psr_key(seed=0, kind='down'):
    """Walkman piano key: key transient + latch 8 ms later + spring ring + ABS body. hit = first transient."""
    r = _rng(seed, 'psr_key_' + kind)
    h = 0.004
    out = np.zeros(_n(0.35))
    up = kind == 'up'
    for j, (dt, a) in enumerate(((0.0, 1.0), (0.008, 0.7 if not up else 0.45))):
        c = _click(0.08, r, (1800.0, 8000.0) if not up else (2200.0, 9000.0), 0.0011,
                   modes=[(2450.0 * (1 + 0.02 * j), 0.006, 0.5), (4100.0, 0.004, 0.3), (1150.0, 0.012, 0.35)])
        A._add(out, c * a, h + dt)
    if not up:
        A._add(out, _thump(0.12, 185.0, 120.0, 0.004, 0.025, r, attack=0.0006, drive=1.6, noise=0.5,
                           noise_lp=1400.0) * 0.55, h + 0.002)
    tr = _t(0.18)
    ring = (np.sin(TWO_PI * 2870.0 * tr) * 0.6 + np.sin(TWO_PI * 5130.0 * tr) * 0.25) * np.exp(-tr / 0.03) * 0.05
    A._add(out, ring, h + 0.01)
    return SJ._done(reverb(_st(out), 'room', wet_db=-20), h, -6.0 if not up else -12.0, 'psr_key')


def psr_motor(seed=0, dur=0.53, speed=1.0):
    """Small DC capstan motor: whine (180 Hz x speed) + harmonics + gear grind; spin-up 40 ms. hit = start."""
    r = _rng(seed, 'psr_motor')
    d = float(dur)
    t = _t(d + 0.05)
    f = 180.0 * float(speed) * (1 - np.exp(-t / 0.04)) * (1 + 0.004 * np.sin(TWO_PI * 7.3 * t))
    ph = TWO_PI * np.cumsum(f) / SR
    x = 0.5 * np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.22 * np.sin(3 * ph) + 0.1 * np.sin(5 * ph)
    grind = bp(r.standard_normal(len(t)), 900.0, 3800.0, 2) * (0.5 + 0.5 * np.sin(ph * 6)) ** 2 * 0.12
    env = np.clip(t / 0.02, 0, 1) * np.clip((d - t) / 0.04, 0, 1)
    return SJ._done(reverb(_st((x + grind) * env), 'room', wet_db=-24), 0.0, -12.0, 'psr_motor', keep_until=d)


def psr_lid_pop(seed=0):
    """Cassette lid springing open: latch click, spring twang, plastic knock at the stop. hit = the latch."""
    r = _rng(seed, 'psr_lid_pop')
    h = 0.005
    out = np.zeros(_n(0.6))
    A._add(out, _click(0.06, r, (2000.0, 9000.0), 0.0008, modes=[(3300.0, 0.004, 0.4), (5200.0, 0.003, 0.2)]), h)
    tw = _t(0.4)
    fsw = 900.0 * (1 + 0.06 * np.exp(-tw / 0.05))
    tw_x = (np.sin(TWO_PI * np.cumsum(fsw) / SR) + 0.4 * np.sin(TWO_PI * np.cumsum(fsw * 1.68) / SR)) * \
        np.exp(-tw / 0.09) * 0.22
    A._add(out, tw_x, h + 0.01)
    A._add(out, _thump(0.1, 230.0, 160.0, 0.004, 0.02, r, attack=0.0006, drive=1.5, noise=0.6, noise_lp=2000.0) * 0.6,
           h + 5 / FPS)
    A._add(out, _click(0.05, r, (1500.0, 7000.0), 0.001, modes=[(1700.0, 0.008, 0.4)]) * 0.5, h + 5 / FPS)
    return SJ._done(reverb(_st(out), 'room', wet_db=-18), h, -5.0, 'psr_lid_pop')


def psr_crinkle(seed=0, dur=0.87, reverse=0):
    """Tape ribbon spilling (cellophane-like crinkle, dense then sparse); reverse=1: drawn back in. hit = start."""
    r = _rng(seed, 'psr_crinkle')
    d = float(dur)
    env = (lambda p: np.clip(p / 0.06, 0, 1) * (1.0 - 0.75 * p) ** 1.5) if not reverse else \
        (lambda p: np.clip((1 - p) / 0.08, 0, 1) * (0.3 + 0.7 * p) ** 1.2)
    out = _crackle(d, r, 2600.0, 1500.0, 9500.0, env=env, gdur=(0.0004, 0.0022))
    out += _crackle(d, r, 500.0, 600.0, 3000.0, env=env, gdur=(0.002, 0.008)) * 0.5
    tt = _t(d)
    rub = bp(r.standard_normal(len(tt)), 1200.0, 5000.0, 2) * 0.015 * env(np.clip(tt / d, 0, 1))
    out += _st(rub)
    return SJ._done(reverb(out, 'room', wet_db=-20), 0.0, -10.0, 'psr_crinkle', keep_until=d)


REHOOK_LAYERS = [dict(t=0.0, name='glitch_short', gain_db=-6, dur=0.3),           # D7 cue 1
                 dict(t=0.0, name='whip', gain_db=-8, params=dict(direction=1), hp=300),   # D7 cue 2
                 dict(t=0.0, name='impact_soft', gain_db=-2),
                 dict(t=0.0, name='sub_drop', gain_db=-8, params=dict(dur=1.4), lp=160)]


def psr_rehook(seed=0):
    """The f464 re-hook slam as one designed sound (D7 cues + impact + sub). hit = the impact."""
    out, h = SJ.render_cues(REHOOK_LAYERS, seed)
    out = _soft(out, 2.0)
    return SJ._done(out, h, 0.0, 'psr_rehook')


PAYOFF_LAYERS = [dict(t=0.0, name='psr_key', gain_db=-2, params=dict(kind='down')),
                 dict(t=0.0, name='impact_soft', gain_db=0),
                 dict(t=0.0, name='impact_big', gain_db=-2),
                 dict(t=0.0, name='sub_drop', gain_db=-6, params=dict(dur=1.4), lp=140)]


def psr_payoff(seed=0):
    """The f768 payoff as one designed sound: PLAY clack + impact_soft + impact_big + sub (LP 140), saturated
    (drive 3.0, loudness-matched) so its crest is low: the master limiter keeps its loudness. hit = start of the
    clack (cue align 'start' on f768: nothing sounds inside the drop-out)."""
    out, h = SJ.render_cues(PAYOFF_LAYERS, seed)
    out = out[_n(max(h - 0.004, 0.0)):]
    out = _soft(out, 3.0)
    return SJ._done(out, 0.004, 0.0, 'psr_payoff')


def psr_hiss(dur=LOOP_BED, seed=0):
    """Bed: cassette hiss (2-12 kHz, slightly decorrelated L/R, 0.55 Hz wow AM with whole cycles). Seamless loop."""
    r = _rng(seed, 'psr_hiss')
    L = _n(dur)
    tl = np.arange(L) / SR
    a = A.colored(L, r, -1.5, 1800, 12000)
    b = A.colored(L, r, -1.5, 1800, 12000)
    y = np.stack([a, 0.6 * a + 0.8 * b], 1)
    f_w = round(0.55 * dur) / dur
    y *= (1 + 0.06 * np.sin(TWO_PI * f_w * tl))[:, None]
    return A._bed_finish(y, 'psr_hiss')


META = dict(  # name: (category, character, use, send dB or None)
    psr_ratchet=('ui', 'hex pencil turning a cassette hub: 6 ticks / rev + whir', 'R1 / R1b loops', -26.0),
    psr_key=('ui', 'walkman piano key: key + latch + spring + body', 'PLAY / STOP / REW / payoff clack', -22.0),
    psr_motor=('texture', 'small DC capstan motor whine + gear grind', 'REW / play motor', None),
    psr_lid_pop=('impact', 'cassette lid latch, spring twang, knock', 'lid springs open', None),
    psr_crinkle=('texture', 'tape ribbon crinkle (granular), reversible', 'tape spill / drawn back', None),
    psr_rehook=('impact', 'D7 glitch + whip + impact + sub as one slam', 'f464 re-hook', -22.0),
    psr_payoff=('impact', 'PLAY clack + impact + body + sub, saturated (low crest)', 'f768 payoff', -22.0),
    psr_hiss=('bed', 'cassette hiss, seamless', 'cassette-tone sections', None),
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


def beds():
    """BED_TABLE -> bed bus at absolute stem levels (circular)."""
    register()
    out = np.zeros((N, 2))
    info = []
    for f0, f1, name, prm, lufs, fin, fout, note in BED_TABLE:
        loop = np.asarray(A.sound(name, **prm), dtype=np.float64)
        Lp = len(loop)
        assert N % Lp == 0, (name, Lp)
        g = undb(lufs - A.loudness(loop))
        idx = np.arange(f0 * SPF, f1 * SPF)
        seg = loop[idx % Lp] * g
        n = len(seg)
        e = np.ones(n)
        a, b = max(2, _n(fin)), max(2, _n(fout))
        e[:a] = 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
        e[-b:] = np.minimum(e[-b:], 0.5 + 0.5 * np.cos(np.pi * np.arange(1, b + 1) / b))
        out[idx % N] += seg * e[:, None]
        info.append(dict(f0=f0, f1=f1, name=name, params=prm, lufs=lufs, note=note))
    return out, info


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
        if mgr > SFX_GR_MAX + 0.05:                  # sparse VO-led layer: never limit more than SFX_GR_MAX
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
    """The SFX stem the VO mixes use. The glued SFX bus BEFORE the stem limiter, set to SFX_MIX_LUFS (its level in
    the mix BEFORE the floor), transient-capped (true peak <= integrated + SFX_VO_CREST), then the VO word floor
    (word_floor_curve against the VO stem at -16 LUFS; two passes, NO re-levelling: re-levelling to a fixed loudness
    after cutting the words would push every unspoken hit up by the same dB). The floored stem's integrated loudness
    is the mix level (epic_mix spec sfx_lufs = report['mix_lufs']); written at true peak -2.5 dBTP.
    -> (array, report)."""
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


PROTECT = [(F(PAYOFF) - 0.02, F(PAYOFF) + 0.6), (F(464) - 0.05, F(464) + 0.3)]
HERO_F = (43, 464, 768)


def vo_ride():
    """vo_stem.wav x VO_RIDE (per-line dB, raised-cosine 40 ms ramps centred 60 ms outside the line's voice) ->
    vo_mix.wav (mono, the VO the mixes and the word floor use). Line spans from words.json."""
    v, _ = A.read_wav(os.path.join(VOD, 'vo_stem.wav'))
    v = np.asarray(v, dtype=np.float64)
    v = v[:, 0] if v.ndim == 2 else v                 # the VO stem is mono (N, 1)
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
    # VO peak tamer: true peak <= integrated + VO_CREST dB (lookahead limiter; only the plosive bursts reach it, e.g.
    # V13 "Aap" hit the master limiter 4 ms off any hero window); a peak control, not a level squash
    L = A.loudness(y)
    gl = _circ(lambda z: A.limiter_gain(z, L + VO_CREST), y, 0.5)
    y = y * gl[:, None]
    VO_PEAK['max_gr_db'] = round(float(-db(gl.min())), 2)
    VO_PEAK['ms_over_1db'] = round(float(np.sum(gl < undb(-1.0)) / SR * 1000), 1)
    A._write_wav(os.path.join(VOD, 'vo_mix.wav'), y, 24)        # dual mono (epic_mix levels by loudness)
    return y


def music_ride():
    """music.wav x MUSIC_RIDE (sum of dB segments with raised-cosine ramps after f1; the payoff segment starts on
    f768 out of the drop-out's digital silence) -> music_mix.wav (the music the VO mixes use)."""
    m, _ = A.read_wav(os.path.join(AUD, 'music.wav'))
    g = np.zeros(N)
    t = np.arange(N) / SR
    for f0, f1, d, ramp in MUSIC_RIDE:
        a, b = F(f0), F(f1)
        seg = ((t >= a) & (t < b)).astype(float)
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
    json.dump(rep, open(os.path.join(AUD, 'sfx_cues.json'), 'w'), indent=1, ensure_ascii=False)
    print('sfx_vo.wav: word floor max cut %.1f dB, min VO margin %.1f LU; in the mix at %.2f LUFS (%s before the floor)'
          % (frep['max_cut_db'], frep['min_margin_after'], frep['mix_lufs'], SFX_MIX_LUFS))
    print('sfx.wav  %.2f LUFS  TP %.2f dBTP  glue %.1f dB  limiter %.1f dB (%.2f s > 1 dB)' % (
        rep['lufs'], rep['true_peak_dbtp'], rep['glue_max_gr_db'], rep['limiter_max_gr_db'], rep['limiter_gr_over_1db_s']))
    if _music_stale():
        import pencil_se_rewind_music as MU
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


def keyframes(mixA, sfx, music, placed):
    out = {}
    ot, _ = onsets(sfx)
    heroes = {0: 'f0 transient', 43: '`Pencil.` slam', 320: 'PLAY key', 347: 'STOP key',
              376: 'REW key', 392: '2nd PLAY key', 452: 'lid pop', 464: 're-hook slam', 672: 'CUT marker',
              768: 'PAYOFF clack', 832: 'pencil snap', 896: 'D2 razor'}
    sync = []
    for f, what in heroes.items():
        t = F(f)
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
                          payoff_window_max=round(win(F(768), F(800)), 2), rehook_window_max=round(win(F(462), F(490)), 2),
                          rest_max=round(max(win(0, F(460)), win(F(492), F(766)), win(F(802), DUR - 0.2)), 2))
    out['loudest']['ok'] = bool(out['loudest']['payoff_window_max'] >= out['loudest']['rest_max'] - 0.5)
    out['dropout'] = dict(music_digital_silence_f752_f767=bool(not np.any(music[DROP[0] * SPF:DROP[1] * SPF])),
                          mixA_momentary_f752_f764=round(_mom(mixA, F(758), 0.4), 2),
                          mixA_momentary_f740_f751_before=round(_mom(mixA, F(745), 0.4), 2),
                          ok=bool(_mom(mixA, F(758), 0.4) <= -36.0))
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
    for b in range(17):
        xx = int(b * 64 / NF * W)
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
    # VO over the bed per word (K-weighted, word span): VO stem vs music + sfx stems in A, vs sfx in B
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
                           below_rule=bad, ok=not bad)
    e = rep['ebur128']
    rep['targets'] = dict(
        mix_A=bool(abs(e['mix_A']['I'] + 14) <= 0.5 and e['mix_A']['TP'] <= -2.0),
        mix_B=bool(abs(e['mix_B']['I'] + 14) <= 0.5 and e['mix_B']['TP'] <= -2.0),
        sfx=bool(e['sfx']['TP'] <= -2.0 and (abs(e['sfx']['I'] + 18) <= 0.3 or json.load(open(os.path.join(
            AUD, 'sfx_cues.json')))['limiter_max_gr_db'] <= SFX_GR_MAX + 0.05)),
        aac=bool(all(v['TP'] <= -1.5 and abs(v['I'] + 14) <= 0.5 for v in rep['aac'].values())),
        lra=bool(2.0 <= e['mix_A']['LRA'] <= 9.0),
        format=bool(all(v['codec_name'] == 'pcm_s24le' and int(v['sample_rate']) == SR and int(v['channels']) == 2
                        and int(v['duration_ts']) == N for v in rep['format'].values())))
    marks = [(0, 'f0', (255, 243, 230)), (43, 'f43 Pencil.', (255, 243, 230)), (256, 'f256 D8', (255, 181, 71)),
             (320, 'f320 PLAY', (80, 230, 255)), (464, 'f464 RE-HOOK', (242, 49, 43)), (576, 'f576 reveal', (80, 230, 255)),
             (648, 'f648 scrub', (80, 230, 255)), (752, 'f752 drop-out', (80, 230, 255)), (768, 'f768 PAYOFF', (255, 181, 71)),
             (896, 'f896 outro', (200, 160, 255))]
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
    print(json.dumps({k: rep['vo_words'][k] for k in ('n', 'min_over_bed_A', 'median_over_bed_A', 'ok')}, indent=1))
    return rep


# ============================================================================================ audition
AUDITION_SET = [('psr_ratchet', dict(dur=64 / FPS, rate=1.0)), ('psr_ratchet', dict(dur=64 / FPS, rate=3.0)),
                ('psr_ratchet', dict(dur=64 / FPS, rate=0.5)), ('psr_key', dict(kind='down')), ('psr_key', dict(kind='up')),
                ('psr_motor', dict(dur=16 / FPS, speed=1.6)), ('psr_lid_pop', {}), ('psr_crinkle', dict(dur=0.87)),
                ('psr_crinkle', dict(dur=1.0, reverse=1)), ('psr_rehook', {}), ('psr_payoff', {})]


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
    bed = A.sound('psr_hiss', dur=LOOP_BED)
    A.spectro_image(A.Sfx(np.asarray(bed), 0, 'psr_hiss'), 1000, 420, None, 'psr_hiss', '8.533 s loop').save(
        os.path.join(AUDITION, 'psr_hiss.png'))
    json.dump(rows, open(os.path.join(AUDITION, 'audition.json'), 'w'), indent=1)
    return rows


def print_cues():
    cl, rep = cues(report=True)
    for c in cl:
        print('f%-6s %-18s %6.1f dB  %-5s %-22s %s' % (c['frame'], c['name'], c['gain_db'], c['align'],
                                                    c.get('vo', '') + ('' if c['gate'] else ' [gate pass]'), c['event']))
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
