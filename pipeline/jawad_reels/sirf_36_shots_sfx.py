#!/usr/bin/env python3
"""sirf_36_shots_sfx.py: SFX layer, beds and the A / B mixes of Bijli series #3 "Sirf 36 Shots" (@jawad_mp4).
Owner: sound-designer (+ music-supervisor run 2: the final mixes). Plan: SHOTS.md section (B) + section 1 (picture events),
BRIEF.md; notes and measurements: brand_reels/design/reels/sirf_36_shots/SOUND.md. Music: sirf_36_shots_music.py.

36.000 s = 1,080 f at 30 fps, 120 BPM (beat 15 f, bar 60 f), key D minor. Text-led reel: no VO (not approved), the mix
leaves the 1-4 kHz band open (music bus -1.5 dB at 2.5 kHz, SFX sparse under the lockups) so a VO can sit on top later.

RETIMING: edit CUE_TABLE / BED_TABLE below (frames), then `python3 sirf_36_shots_sfx.py build`. Every cue is placed on
its frame to the sample (frame f = sample f x 1,600); align 'hit' puts the sound's designed hit on the frame (impacts =
transient, whooshes = loudest pass, risers / reverse swells = their end), 'start' starts it there. Placement is circular:
anything before f0 or past f1079 wraps across the loop seam (the f1076 ratchet click, tails of the outro).

Chain (loop-exact): cues -> audio.duck_under (cluster gain) -> circular placement + 'studio' room send (circular reverb)
-> drop-out gate (exact zero f780-f809 for every cue except gate=False ones: typing dots, payoff) -> SFX bus to -18 LUFS
with the beds at their absolute levels (sidechained 3 dB under the SFX) -> 2:1 glue -> 4x true-peak limiter (circular)
at -2.0 dBTP -> sfx.wav. Mixes: epic_mix.mix_reel(loop=True) with music.wav: A = music + SFX (-14 LUFS, TP <= -2.0 dBTP),
B = SFX only, mastered on its own (-14 LUFS, for the song-ready upload); stems at A's gains sum to A.

Local sounds (numpy only, no samples; each audio.qc() == [] at its used params, spectrograms in <RW>/audio/audition/):
    s36_wind          thumb-wheel advance: 5 pawl clicks over the 36-ridge knurl (f-19 f-15 f-11 f-7 f-4 before the
                      hit) with knurl burr between them, then the spring detent (hit = the detent, the dial lands 36)
    s36_flash_charge  xenon flash charging: inverter whine rising 1.8 -> 7 kHz (log, 23 Hz ripple) + 120 Hz capacitor
                      hum fading as it charges + faint hiss; hit = the END (ready), duration = the charge
    s36_flash_pop     flash discharge: xenon tick (3-12 kHz, 0.8 ms) + tube snap (1.4 -> 0.5 kHz chirp) + capacitor
                      thump 70 Hz + transformer ring 11.5 kHz; hit = 0
    s36_rewind        fold-out rewind crank spinning by itself at 3.75 rev/s: 14-tooth ratchet ticks (52 Hz grain),
                      film rasp amplitude-modulated per revolution, knob rumble; hit = start (cue align 'start')
    s36_tin_land      135 cartridge landing on laminate: steel end-cap clink (modal 1.3-8.8 kHz) + laminate knock,
                      a 6 px bounce 3 f later, short roll; hit = first contact
    s36_clock_tick    shop wall clock: escapement click + case modes, small room; hit = 0
    s36_paper_plap    kraft envelope landing: air puff -> paper thup + slap + crinkle; hit = contact
    s36_paper_flap    envelope flap opening (f300-f315): gum-strip peel, paper bend crackle, swish, flap flop at 0.5 s;
                      hit = start
    s36_print_slide   glossy 4R print sliding out and landing (seeds 0-4); slap=1 = the thumb print slapped on top;
                      hit = landing
    s36_sticky_peel   magnetic-album adhesive crackle (0.75 s); hit = start
    s36_hdd_spinup    4 portable drives spinning up: motor harmonics rising to 90 Hz (5,400 rpm) + bearing whine +
                      head unpark clack at 1.1 s; hit = start
    s36_error         disk full: double low buzz on D3 (+ D2), 130 ms each; hit = 0
    s36_rehook        THE F480 BOUNCE: whip (f479, HP 300) + impact_soft + sub_drop (LP 160) + glitch_short (0.3 s) +
                      air_zoom, rendered with sfx_jawad.render_cues and glued as ONE designed sound (SHOTS: five
                      stacked layers -> one bounce); hit = the impact on f480
    s36_hdd (bed)     12 s loop: 4 spindles 89.6-90.8 Hz (beating) + harmonics, bearing whine, air; seeks=1 adds head
                      seek ticks quantised to 8ths (the drive LEDs flicker on 8ths)

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh):
    python3 sirf_36_shots_sfx.py cues        the expanded cue table (frame, sound, gain, align, event)
    python3 sirf_36_shots_sfx.py audition    local sounds -> <RW>/audio/audition/*.wav + .png + qc
    python3 sirf_36_shots_sfx.py build       sfx.wav (+ sfx_fx / sfx_bed), music.wav if missing or stale, mix_A.wav,
                                             mix_B.wav, stems/, sfx_cues.json, then verify
    python3 sirf_36_shots_sfx.py verify      ebur128 (wav + AAC), key-frame analysis, overview PNGs -> sound.verify.json
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.ndimage import maximum_filter1d, median_filter  # noqa: E402

import audio as A  # noqa: E402
from audio import (SR, TWO_PI, _t, _n, _rng, _st, _ar, _fade, _thump, _click, _crackle, noise_band, modal,  # noqa: E402
                   lp, hp, bp, undb, db, reverb)
import epic_sfx as ES  # noqa: E402
import sfx_jawad as SJ  # noqa: E402
import epic_mix as EX  # noqa: E402

MODULE = 'sirf_36_shots'
FPS, BPM, NF = 30, 120.0, 1080
DUR = NF / FPS
N = _n(DUR)
assert N == 1728000
SPF = SR // FPS
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
AUDITION = os.path.join(AUD, 'audition')
SFX_LUFS, SFX_TP = -18.0, -2.0
BED, BED_GAIN_DB = None, -30.0                 # render.py must NOT rebuild this layer: mux mix_A.wav with --audio
DROP = (780, 810)                              # drop-out frames [f780, f810)
PAYOFF = 810
BED_DUCK_DB = 3.0


def F(f):
    return f / FPS


# ============================================================================================ CUE TABLE (frames)
# (frame, sound, gain_db, options, visual event). options: align ('hit' default | 'start'), pan, lp, hp, rate, dur,
# width, params {}, seed, send_db, gate (False = passes the f780-f809 drop-out gate). Gains are relative to the house
# calibration (audio.py: gain 0 = the sound's designed level).
GT = 2349.32 / 2096.3                          # glass_tap(seed 0) dominant partial 2096.3 Hz -> D7 (bijli measurement)
CUE_TABLE = [
    # S1 hook: counter macro, thumb wheel, flash charging
    (15, 's36_wind', -6.0, {}, 'thumb wheel: clicks f1076 (wraps) f0 f4 f8 f11, detent f15 = dial lands 36'),
    (0, 'impact_soft', -12.0, dict(lp=900), 'frame-0 transient under the first ratchet click'),
    (58, 's36_flash_charge', -10.0, dict(params=dict(dur=round(43 / FPS, 4))), 'flash charging f15-f58, LED glows'),
    # S2 flash pop, recharge, crank
    (60, 'camera_shutter', 0.0, {}, 'FLASH POP: shutter'),
    (60, 's36_flash_pop', -2.0, {}, 'FLASH POP: xenon discharge (L3 push)'),
    (60, 'jd_hit_soft', -6.0, {}, 'FLASH POP: body; the music kit enters'),
    (106, 's36_flash_charge', -24.0, dict(params=dict(dur=round(42 / FPS, 4), seed=1)), 'flash recharging f64-f106'),
    (105, 's36_rewind', -8.0, dict(align='start', pan=-0.3, params=dict(dur=1.2)), 'rewind crank spins f105-f141'),
    # S3 canister
    (150, 'whip', -6.0, dict(params=dict(direction=-1)), 'C1 whip up into the canister (c = f150)'),
    (160, 'swish_small', -18.0, dict(pan=-0.2), 'canister spin pass 1'),
    (180, 'swish_small', -18.0, dict(pan=0.2), 'canister spin pass 2'),
    (200, 'swish_small', -20.0, dict(pan=-0.1), 'canister spin pass 3 (slowing)'),
    (225, 'whoosh_fast', -12.0, dict(align='start', params=dict(direction=1)), 'canister tips and falls f225-f239 '
     '(in_cubic: the pass peaks at f238, the fastest frame)'),
    # S4 studio counter
    (240, 's36_tin_land', -2.0, dict(pan=-0.3), 'canister lands at (380, 1180), 6 px bounce (L3 cut)'),
    (240, 'impact_soft', -10.0, {}, 'hard cut f240 body'),
    (255, 's36_clock_tick', -12.0, dict(pan=0.3), 'DIN 2: light state cut'),
    (270, 'ui_click', -14.0, dict(lp=3000), 'DIN 3: darkroom safelight switches on'),
    (270, 's36_paper_plap', -4.0, dict(pan=0.15), 'envelope drops in at (620, 1210)'),
    # S5 prints
    (300, 'ui_hover', -12.0, {}, 'C6 rack-focus hand-off (c = f300)'),
    (300, 's36_paper_flap', -8.0, dict(align='start'), 'flap opens f300-f315'),
    (315, 's36_print_slide', -10.0, dict(seed=0, pan=-0.35), 'P1 landscape lands (330, 1130)'),
    (323, 's36_print_slide', -10.0, dict(seed=1, pan=0.03), 'P2 silhouettes lands (560, 1100)'),
    (330, 's36_print_slide', -10.0, dict(seed=2, pan=0.4), 'P3 cake lands (770, 1170)'),
    (338, 's36_print_slide', -16.0, dict(seed=4, pan=0.1), 'negatives strip peeks out'),
    (375, 's36_print_slide', -4.0, dict(seed=3, params=dict(slap=1)), 'THUMB print slaps on top (music stops f375-f389)'),
    (375, 'impact_soft', -8.0, {}, 'thumb print slap body'),
    # S6 album
    (420, 'impact_soft', -10.0, {}, 'hard cut f420: album page'),
    (422, 's36_sticky_peel', -10.0, dict(align='start'), 'album adhesive f422-f445'),
    (450, 'card_slide', -12.0, dict(params=dict(dur=0.62)), 'PVC sleeve slides down f430-f450 (thup = settles)'),
    # S7 re-hook + drives
    (480, 's36_rehook', 0.0, {}, 'RE-HOOK: C8 snap zoom; whip f479 + impact + sub drop + glitch + air zoom (one bounce)'),
    (480, 's36_hdd_spinup', -16.0, dict(align='start', pan=0.1), 'drives spin up; HDD bed starts'),
    (540, 'jd_hit_soft', -4.0, {}, '2 TB slam'),
    (540, 'ui_click', -12.0, {}, 'storage HUD pops in'),
    (540, 'bar_grow', -14.0, dict(align='start', params=dict(duration=round(25 / FPS, 4))), 'storage bar fills f540-f565'),
    (570, 'jd_hit_soft', -4.0, {}, '4 CAMERAS slam'),
    (570, 'glass_tap', -16.0, dict(seed=0, params=dict(pitch=round(GT, 4)), pan=-0.15), 'CAM A label lights (D7)'),
    (574, 'glass_tap', -16.0, dict(seed=0, params=dict(pitch=round(GT * 2 ** (3 / 12), 4)), pan=-0.05), 'CAM B (F7)'),
    (578, 'glass_tap', -16.0, dict(seed=0, params=dict(pitch=round(GT * 2 ** (7 / 12), 4)), pan=0.05), 'CAM C (A7)'),
    (582, 'glass_tap', -16.0, dict(seed=0, params=dict(pitch=round(GT * 2 ** (10 / 12), 4)), pan=0.15), 'CAM D (C8)'),
    # S8 media bin
    (600, 'jd_hit_soft', -2.0, {}, '3,000 TAKES slam (L3 cut)'),
    (600, 'whoosh_slow', -18.0, dict(align='start'), 'thumbnails start scrolling (speed rises)'),
    (600, 'slot_tick', -12.0, dict(align='start', params=dict(n=26, dur=round(50 / FPS, 4), ease='linear')),
     'take counter rolls 0001 -> 3,000 f600-f650'),
    (660, 'whoosh_fast', -8.0, {}, 'in-scene snap zoom x1.5 (out_expo: fastest on f660)'),
    (735, 's36_error', -6.0, {}, 'DISK FULL: bar turns red, chip pops'),
    (735, 'glitch_short', -12.0, {}, 'DISK FULL: 2-frame rgb glitch'),
    (780, 'jd_riser', -8.0, dict(params=dict(bars=1, bpm=120.0)), 'riser into the freeze (1 bar, lands on f780)'),
    (772, 'jd_tape_stop', -8.0, dict(align='start', params=dict(dur=round(8 / FPS, 4))), 'bin slows and freezes f772-f780'),
    # S9 drop-out + payoff
    (795, 'typing', -18.0, dict(align='start', gate=False, params=dict(n=6, cps=12.0)), 'toast typing dots f795-f809'),
    (810, 'jd_stack_velvet_hit', 0.0, dict(gate=False), 'PAYOFF "EK ACHHA SHOT nahi hai." (loudest moment)'),
    (810, 'toast_chime', -2.0, dict(gate=False), 'PAYOFF: toast settles to "Client - abhi"'),
    # S10 closer: C3 portal through the avatar into the counter window (c = f900, window f876-f908)
    (898, 'reverse_swell', -6.0, dict(params=dict(duration=round(22 / FPS, 4))), 'C3 portal suck-in (ends 2 f early)'),
    (900, 'air_zoom', -8.0, {}, 'C3 portal pass'),
    (900, 'impact_soft', -4.0, {}, 'C3 portal lands in the counter window'),
    # S11 outro: profile_outro cues (ProfileOutro.cues(32.0, 36.0)), with SHOTS' 1.5 s reverse swell into f0
    (963, 'swish_small', -12.0, dict(align='start'), 'outro: pill pops'),
    (997.5, 'glass_tap', -12.0, {}, 'outro: card moves'),
    (1005, 'shimmer', -10.0, {}, 'outro: question lands'),
    (1080, 'reverse_swell', -8.0, dict(params=dict(duration=1.5)), 'swell f1035 -> f1080 = f0, releases into the ratchet'),
]

# (f0, f1, bed, params, LUFS in the -18 LUFS stem, fade in s, fade out s, note). f1 > 1080 wraps across the seam.
# Bed loops are 12 s (36 / 12 = 3): indexed by reel time, so a bed crossing the seam stays phase-continuous.
BED_TABLE = [
    (900, 1320, 'jd_room_night_home', dict(dur=12.0), -42.0, 0.6, 0.25, 'warm home at night: closer, outro, '
     'across the seam, hook and the past home shots (to f240)'),
    (240, 270, 'outdoor_birds', dict(dur=12.0), -40.0, 0.03, 0.08, 'studio counter by day (DIN 1 / DIN 2)'),
    (270, 300, 'room_tone', dict(dur=12.0), -46.0, 0.05, 0.1, 'night: the darkroom safelight'),
    (300, 480, 'room_tone', dict(dur=12.0), -45.0, 0.1, 0.05, 'the table: envelope, prints, album'),
    (480, 780, 's36_hdd', dict(dur=12.0, seeks=1), -37.0, 0.3, 0.004, 'edit desk: 4 drives, seeks on 8ths'),
    (780, 810, 's36_hdd', dict(dur=12.0, seeks=0), -50.0, 0.004, 0.004, 'DROP-OUT: frozen, spindles only'),
    (780, 810, 'room_tone', dict(dur=12.0), -51.0, 0.004, 0.004, 'DROP-OUT: room tone'),
    (810, 900, 's36_hdd', dict(dur=12.0, seeks=0), -43.0, 0.004, 0.5, 'payoff: spindles fade toward the portal'),
]


# ============================================================================================ local sounds
def _soft(x, drive):
    pk = float(np.max(np.abs(x))) + 1e-12
    return SJ.shape(np.asarray(x, dtype=np.float64) / pk, drive) * pk


def _mono(x):
    x = np.asarray(x, dtype=np.float64)
    return x if x.ndim == 1 else x.mean(1)


def s36_wind(seed=0):
    """Thumb-wheel advance. hit = the spring detent (the dial lands on the next number)."""
    r = _rng(seed, 's36_wind')
    offs = (-19, -15, -11, -7, -4)
    pre = 19 / FPS + 0.09
    out = np.zeros(_n(pre + 0.45))
    for k, f in enumerate(offs):
        t0 = pre + f / FPS
        jit = 1 + 0.025 * r.standard_normal()
        c = _click(0.06, r, (2500.0, 9000.0), 0.0012,
                   modes=[(3150.0 * jit, 0.006, 0.5), (5400.0 * jit, 0.004, 0.3), (1850.0 * jit, 0.008, 0.25)])
        A._add(out, c * (0.75 + 0.1 * r.random()), t0)
        burr = _mono(_crackle(0.08, r, 700.0, 1500.0, 6500.0, env=lambda p: 0.2 + p, gdur=(0.0004, 0.0016)))
        A._add(out, burr * 0.35, t0 - 0.08)
    det = _click(0.14, r, (1500.0, 7000.0), 0.0018, modes=[(2150.0, 0.03, 0.6), (3900.0, 0.012, 0.3), (980.0, 0.02, 0.3)],
                 low=(420.0, 0.012, 0.5))
    A._add(out, det * 1.25, pre)
    return SJ._done(reverb(_st(out), 'room', wet_db=-24), pre, -6.0, 's36_wind')


def s36_flash_charge(seed=0, dur=1.433, f0=1800.0, f1=7000.0):
    """Xenon flash charging. hit = the END (charged)."""
    r = _rng(seed, 's36_flash_charge')
    d = float(dur)
    t = _t(d + 0.06)
    u = np.clip(t / d, 0, 1)
    f = f0 * (f1 / f0) ** (u ** 0.8) * (1 + 0.004 * np.sin(TWO_PI * 23.0 * t))
    ph = TWO_PI * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    env = np.clip(t / 0.06, 0, 1) * (0.45 + 0.55 * u ** 0.7) * np.where(t < d, 1.0, np.exp(-(t - d) / 0.012))
    hum = sum(a * np.sin(TWO_PI * 120.0 * (k + 1) * t) for k, a in enumerate((1.0, 0.5, 0.35, 0.2, 0.1)))
    hum *= 0.10 * (1 - 0.8 * u) * np.clip(t / 0.03, 0, 1) * np.where(t < d, 1.0, np.exp(-(t - d) / 0.01))
    hiss = bp(r.standard_normal(len(t)), 4000.0, 9000.0, 2) * 0.012 * env
    x = tone * env * 0.5 + hum + hiss
    return SJ._done(reverb(_st(x), 'room', wet_db=-26), d, -8.0, 's36_flash_charge', keep_until=d + 0.03)


def s36_flash_pop(seed=0):
    """Flash discharge. hit = 0."""
    r = _rng(seed, 's36_flash_pop')
    d = 0.6
    t = _t(d)
    tick = bp(r.standard_normal(len(t)), 3000.0, 12000.0, 2) * np.exp(-t / 0.0008)
    tick /= max(np.abs(tick).max(), 1e-9)
    fs = 500.0 + 900.0 * np.exp(-t / 0.002)
    snap = np.sin(TWO_PI * np.cumsum(fs) / SR) * np.exp(-t / 0.008) * 0.55
    thump = _thump(d, 70.0, 90.0, 0.01, 0.05, r, attack=0.001, drive=1.5, noise=0.3) * 0.5
    ring = np.sin(TWO_PI * 11500.0 * t) * np.exp(-t / 0.03) * 0.04
    x = tick + snap + thump + ring
    return SJ._done(reverb(_st(x), 'room', wet_db=-18), 0.0, -3.0, 's36_flash_pop')


def s36_rewind(seed=0, dur=1.2):
    """Rewind crank spinning by itself (3.75 rev/s = 45 deg per frame). hit = start."""
    r = _rng(seed, 's36_rewind')
    d = float(dur)
    t = _t(d + 0.1)
    rate = 3.75 * np.clip(t / 0.08, 0, 1) * np.clip((d - t) / 0.12, 0, 1) ** 0.5
    rev = np.cumsum(rate) / SR
    x = np.zeros(len(t))
    teeth = np.floor(rev * 14)
    idx = np.nonzero(np.diff(teeth) > 0)[0]
    cl = _t(0.012)
    for i in idx:
        g = bp(r.standard_normal(len(cl)), 2000.0, 7000.0, 2) * np.exp(-cl / 0.0006) * r.uniform(0.5, 1.0)
        g += np.sin(TWO_PI * r.uniform(2600, 3000) * cl) * np.exp(-cl / 0.003) * 0.3
        A._add(x, g, i / SR)
    am = 0.6 + 0.4 * np.sin(TWO_PI * rev)
    rasp = bp(r.standard_normal(len(t)), 800.0, 4500.0, 2) * am * 0.12 * (rate / 3.75)
    knob = bp(r.standard_normal(len(t)), 150.0, 500.0, 2) * am * 0.15 * (rate / 3.75)
    x = (x * 0.6 + rasp + knob) * np.clip(t / 0.03, 0, 1)
    return SJ._done(reverb(_st(x), 'room', wet_db=-22), 0.0, -9.0, 's36_rewind', keep_until=d)


def s36_tin_land(seed=0):
    """135 cartridge lands on laminate (+ 6 px bounce + short roll). hit = first contact."""
    r = _rng(seed, 's36_tin_land')
    h = 0.01
    out = np.zeros(_n(0.9))

    def clink(a, k):
        fr = np.array([1320.0, 2870.0, 4510.0, 6650.0, 8800.0]) * (1 + 0.01 * r.standard_normal())
        return modal(0.25, fr, [0.05, 0.03, 0.02, 0.012, 0.008], [0.5, 0.6, 0.45, 0.3, 0.2], r, contact=0.0002) * a \
            + _thump(0.12, 160.0, 140.0, 0.006, 0.03, r, attack=0.0008, drive=1.4, noise=0.4) * 0.6 * k
    A._add(out, clink(1.0, 1.0), h)
    A._add(out, clink(0.35, 0.3), h + 3 / FPS)
    tr = _t(0.4)
    roll = bp(r.standard_normal(len(tr)), 300.0, 2500.0, 2) * (0.6 + 0.4 * np.sin(TWO_PI * 9.0 * tr)) * \
        np.exp(-tr / 0.12) * np.clip(tr / 0.02, 0, 1) * 0.12
    A._add(out, roll, h + 0.16)
    return SJ._done(reverb(_st(out), 'room', wet_db=-20), h, -4.0, 's36_tin_land')


def s36_clock_tick(seed=0):
    """Shop wall clock tick. hit = 0."""
    r = _rng(seed, 's36_clock_tick')
    x = _click(0.1, r, (1800.0, 6500.0), 0.001, modes=[(2600.0, 0.01, 0.5), (4300.0, 0.006, 0.3), (1250.0, 0.015, 0.35)],
               low=(380.0, 0.01, 0.3))
    return SJ._done(reverb(_st(x), 'room', wet_db=-12), 0.0, -9.0, 's36_clock_tick')


def s36_paper_plap(seed=0):
    """Kraft envelope landing flat on the counter. hit = contact (0.04 s)."""
    r = _rng(seed, 's36_paper_plap')
    h = 0.04
    out = np.zeros(_n(0.5))
    ta = _t(h)
    puff = bp(r.standard_normal(len(ta)), 200.0, 1200.0, 2) * (ta / h) ** 2 * 0.15
    A._add(out, puff, 0.0)
    A._add(out, _thump(0.15, 140.0, 90.0, 0.008, 0.035, r, attack=0.001, drive=1.2, noise=0.8, noise_lp=900.0) * 0.7, h)
    ts = _t(0.06)
    A._add(out, bp(r.standard_normal(len(ts)), 900.0, 6000.0, 2) * np.exp(-ts / 0.012) * 0.6, h)
    A._add(out, _mono(_crackle(0.2, r, 300.0, 2500.0, 9000.0, env=lambda p: (1 - p) ** 2)) * 0.25, h + 0.01)
    return SJ._done(reverb(_st(out), 'room', wet_db=-20), h, -5.0, 's36_paper_plap')


def s36_paper_flap(seed=0):
    """Envelope flap opening (0.5 s): gum peel, paper bend, swish, flop. hit = start."""
    r = _rng(seed, 's36_paper_flap')
    out = np.zeros((_n(0.75), 2))
    A._add(out, _crackle(0.14, r, 2600.0, 1500.0, 8000.0, env=lambda p: 1 - 0.6 * p) * 0.55, 0.0)
    A._add(out, _crackle(0.42, r, 420.0, 800.0, 6000.0, env=lambda p: np.sin(np.pi * p) ** 2) * 0.45, 0.06)
    A._add(out, noise_band(0.42, r, [(0.0, 500.0), (0.5, 1600.0), (1.0, 900.0)], bw=0.8, width=0.4) *
           (np.sin(np.pi * np.linspace(0, 1, _n(0.42))) ** 2 * 0.25)[:, None], 0.08)
    A._add(out, _st(_thump(0.1, 180.0, 60.0, 0.005, 0.025, r, attack=0.001, noise=0.8, noise_lp=1200.0) * 0.35), 0.5)
    tf = _t(0.04)
    A._add(out, _st(bp(r.standard_normal(len(tf)), 1000.0, 6000.0, 2) * np.exp(-tf / 0.008) * 0.2), 0.5)
    return SJ._done(reverb(out, 'room', wet_db=-20), 0.0, -9.0, 's36_paper_flap', keep_until=0.6)


def s36_print_slide(seed=0, slap=0):
    """Glossy print slides out and lands (slap=1: slapped down on top). hit = landing."""
    r = _rng(seed, 's36_print_slide')
    h = 0.16 if not slap else 0.09
    out = np.zeros(_n(h + 0.45))
    ts = _t(h)
    env = np.sin(np.pi * np.clip(ts / h, 0, 1) * 0.92) ** 1.5
    sl = bp(r.standard_normal(len(ts)), 1200.0, 7000.0, 2) * env * (0.18 if not slap else 0.1)
    sq = A.reson(r.standard_normal(len(ts)), r.uniform(2100, 2600), 14.0) * env * 0.04
    A._add(out, sl + sq, 0.0)
    tl = _t(0.12)
    if slap:
        crack = bp(r.standard_normal(len(tl)), 1000.0, 8000.0, 2) * np.exp(-tl / 0.004)
        crack /= max(np.abs(crack).max(), 1e-9)
        A._add(out, crack * 0.9 + _thump(0.12, 120.0, 110.0, 0.006, 0.03, r, attack=0.0006, drive=1.6, noise=0.7,
                                         noise_lp=1500.0)[:len(tl)] * 0.8, h)
        A._add(out, _mono(_crackle(0.15, r, 500.0, 2500.0, 9000.0, env=lambda p: (1 - p) ** 2)) * 0.3, h + 0.005)
    else:
        thip = bp(r.standard_normal(len(tl)), 600.0, 5000.0, 2) * np.exp(-tl / 0.008)
        thip /= max(np.abs(thip).max(), 1e-9)
        A._add(out, thip * 0.45 + np.sin(TWO_PI * 230.0 * tl) * np.exp(-tl / 0.015) * 0.25, h)
    return SJ._done(reverb(_st(out), 'room', wet_db=-22), h, -3.0 if slap else -9.0, 's36_print_slide')


def s36_sticky_peel(seed=0, dur=0.75):
    """Magnetic-album adhesive crackle. hit = start."""
    r = _rng(seed, 's36_sticky_peel')
    d = float(dur)
    walk = np.clip(np.cumsum(r.standard_normal(64)) * 0.15 + 0.7, 0.15, 1.2)
    out = _crackle(d, r, 2400.0, 1200.0, 9000.0, env=lambda p: np.interp(p, np.linspace(0, 1, 64), walk) *
                   np.clip(p / 0.05, 0, 1) * np.clip((1 - p) / 0.1, 0, 1), gdur=(0.0003, 0.0018))
    tt = _t(d)
    out += _st(bp(r.standard_normal(len(tt)), 2000.0, 6000.0, 2) * 0.02 * np.sin(np.pi * tt / d))
    tk = _click(0.05, r, (2000.0, 8000.0), 0.001)
    A._add(out, _st(tk * 0.3), d - 0.02)
    return SJ._done(reverb(out, 'room', wet_db=-22), 0.0, -12.0, 's36_sticky_peel', keep_until=d)


def s36_hdd_spinup(seed=0):
    """Four drives spin up to 5,400 rpm + head unpark clack. hit = start."""
    r = _rng(seed, 's36_hdd_spinup')
    t = _t(1.6)
    out = np.zeros(len(t))
    for k, f0 in enumerate((89.6, 90.0, 90.3, 90.8)):
        f = f0 * (1 - np.exp(-t / (0.42 + 0.04 * k)))
        ph = TWO_PI * np.cumsum(f) / SR
        out += (0.5 * np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph) + 0.12 * np.sin(4 * ph)) / 4
        out += np.sin(TWO_PI * np.cumsum(f * 15.7) / SR) * 0.03 * (f / f0)
    out *= np.clip(t / 0.05, 0, 1) * np.clip((1.6 - t) / 0.2, 0, 1)
    for k, tk in enumerate((1.1, 1.13)):
        c = _click(0.05, r, (1500.0, 6000.0), 0.0008, low=(600.0, 0.006, 0.4))
        A._add(out, c * (0.5 if k else 0.35), tk)
    return SJ._done(reverb(_st(out), 'room', wet_db=-24), 0.0, -12.0, 's36_hdd_spinup', keep_until=1.5)


def s36_error(seed=0):
    """Disk full: double low buzz on D3 + D2. hit = 0."""
    r = _rng(seed, 's36_error')
    out = np.zeros(_n(0.6))
    tb = _t(0.13)
    for t0 in (0.0, 0.2):
        ph = TWO_PI * 146.83 * tb
        x = np.tanh(3.0 * (np.sin(ph) + 0.5 * np.sin(0.5 * ph + 0.3) + 0.3 * np.sin(1.003 * ph))) * \
            np.clip(tb / 0.004, 0, 1) * np.clip((0.13 - tb) / 0.02, 0, 1)
        A._add(out, lp(x, 2500.0, 2), t0)
    return SJ._done(reverb(_st(out), 'room', wet_db=-22), 0.0, -5.0, 's36_error')


REHOOK_LAYERS = [dict(t=-1 / FPS, name='whip', gain_db=-6, params=dict(direction=1), hp=300),
                 dict(t=0.0, name='impact_soft', gain_db=0),
                 dict(t=0.0, name='sub_drop', gain_db=-4, params=dict(dur=1.6), lp=160),
                 dict(t=0.0, name='glitch_short', gain_db=-10, dur=0.3),
                 dict(t=0.0, name='air_zoom', gain_db=-8)]


def s36_rehook(seed=0):
    """The f480 re-hook: five layers bounced into one designed sound. hit = the impact (f480)."""
    out, h = SJ.render_cues(REHOOK_LAYERS, seed)
    out = _soft(out, 2.2)
    return SJ._done(out, h, 1.0, 's36_rehook')


def s36_hdd(dur=12.0, seeds=1, seed=0):
    """Bed: 4 spindles (89.6-90.8 Hz, integer cycles per loop) + harmonics, bearing whine, air; seeks=1 adds head
    seek ticks on the 8th grid (0.25 s), random subset. Seamless loop of dur s (dur a multiple of 0.25)."""
    r = _rng(seed, 's36_hdd')
    L = _n(dur)
    tl = np.arange(L) / SR
    q = lambda f: round(f * dur) / dur  # noqa: E731
    x = np.zeros(L)
    for k, f0 in enumerate((89.6, 90.0, 90.3, 90.8)):
        for h, a in ((1, 0.35), (2, 0.5), (3, 0.3), (4, 0.15), (6, 0.06)):
            x += a * np.sin(TWO_PI * q(f0 * h) * tl + r.uniform(0, 6.28)) / 4
        x += 0.025 * np.sin(TWO_PI * q(f0 * 15.7) * tl + r.uniform(0, 6.28))
    air = A.colored(L, r, -3.0, 200, 4000) * 0.03
    y = _st(x) + np.stack([air, A.colored(L, r, -3.0, 200, 4000) * 0.03], 1)
    if seeds:
        for k in range(int(round(dur / 0.25))):
            if r.random() < 0.38:
                n = int(r.integers(1, 4))
                for j in range(n):
                    c = _click(0.03, r, (1500.0, 6000.0), 0.0006, low=(600.0, 0.004, 0.3))
                    c = _st(c) * r.uniform(0.15, 0.35)
                    SJ._add_wrap(y, c, k * 0.25 + j * 0.018)
    return A._bed_finish(y, 's36_hdd')


META = dict(  # name: (category, character, use, send dB or None)
    s36_wind=('ui', 'thumb-wheel ratchet clicks + spring detent', 'frame counter advance (f1076-f15)', -24.0),
    s36_flash_charge=('texture', 'xenon flash charging whine 1.8 -> 7 kHz + capacitor hum', 'flash charge', None),
    s36_flash_pop=('impact', 'flash discharge: xenon tick + tube snap + capacitor thump', 'flash pop', None),
    s36_rewind=('texture', 'rewind crank whirr with ratchet grain', 'crank spins', None),
    s36_tin_land=('impact', 'film cartridge landing on laminate, bounce, roll', 'canister lands', None),
    s36_clock_tick=('ui', 'wall clock tick, small room', 'day passes', None),
    s36_paper_plap=('impact', 'kraft envelope lands flat', 'envelope lands', -24.0),
    s36_paper_flap=('texture', 'envelope flap opening: gum peel, paper bend, flop', 'flap opens', None),
    s36_print_slide=('ui', 'glossy print slide + landing (slap)', 'prints fan, thumb slap', None),
    s36_sticky_peel=('texture', 'album adhesive crackle', 'album page', None),
    s36_hdd_spinup=('texture', 'four drives spinning up + head unpark', 'drives appear', None),
    s36_error=('ui', 'double low buzz D3', 'disk full', None),
    s36_rehook=('impact', 'whip + impact + sub drop + glitch + air zoom as one bounce', 'f480 re-hook', -22.0),
    s36_hdd=('bed', 'four HDD spindles + seek ticks on 8ths, seamless', 'edit desk bed', None),
)
LOCAL = tuple(META)


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
def cues():
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


def _gate():
    g = np.ones(N)
    ia, ib = DROP[0] * SPF, DROP[1] * SPF
    g[ia - 64:ia] = np.linspace(1, 0, 64)
    g[ia:ib] = 0.0
    return g


def _wrap_add(buf, y, start):
    SJ._add_wrap(buf, np.asarray(y, dtype=np.float64), start)


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
        _wrap_add(buses[gk], y, start)
        cat = A.SOUNDS[c['name']]['category']
        sdb = c.get('send_db', A.SOUNDS[c['name']]['send'] if A.SOUNDS[c['name']]['send'] is not None
                    else A._CAT_SEND[cat])
        if sdb is not None and sdb > -60:
            _wrap_add(sends[gk], y * undb(sdb), start)
        placed.append(dict(frame=c.get('frame'), t=round(float(c['t']), 4), name=c['name'], start=round(start, 4),
                           hit=round(start + hit, 4), hit_f=round((start + hit) * FPS, 3), len=round(len(y) / SR, 3),
                           align=c['align'], gain_db=round(float(c['gain_db']), 2), duck_db=c.get('duck_db', 0.0),
                           gate=gk, event=c.get('event', '')))
    for gk in (True, False):
        if np.any(sends[gk]):
            buses[gk] += A.reverb_circular(sends[gk], 'studio', wet_db=0.0) - sends[gk]
    return buses[True] * _gate()[:, None], buses[False], placed


def beds():
    """BED_TABLE -> bed bus at absolute stem levels (unit = final stem scale before the shared limiter)."""
    register()
    out = np.zeros((N, 2))
    info = []
    for f0, f1, name, prm, lufs, fin, fout, note in BED_TABLE:
        loop = np.asarray(A.sound(name, **prm), dtype=np.float64)
        Lp = len(loop)
        assert N % Lp == 0, (name, Lp)
        g = undb(lufs - A.loudness(loop))
        i0, i1 = f0 * SPF, f1 * SPF
        idx = np.arange(i0, i1)
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


def sfx_bus(cue_list=None):
    """-> (stem, fx part, bed part, report)."""
    cl = cues() if cue_list is None else cue_list
    fx_g, fx_p, placed = render_fx(cl)
    fx = fx_g + fx_p
    bb, binfo = beds()
    bb = _circ(lambda z: A.sidechain(z, _circ(lambda q: q, fx), depth_db=BED_DUCK_DB) if False else z, bb)
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
    for _ in range(10):
        y = fx + bb
        gl = _circ(lambda z: A.limiter_gain(z, SFX_TP - 0.3), y, 0.5)
        y = y * gl[:, None]
        L = A.loudness(y)
        if abs(L - SFX_LUFS) < 0.03 and A.true_peak(y) <= SFX_TP:
            break
        fx = fx * undb(SFX_LUFS - L)
        bb = bb * undb(SFX_LUFS - L)
    fx_o, bb_o = fx * gl[:, None], bb * gl[:, None]
    stem = fx_o + bb_o
    rep = dict(lufs=round(A.loudness(stem), 3), true_peak_dbtp=round(A.true_peak(stem), 3),
               lra=round(A.loudness_range(stem), 2), glue_max_gr_db=round(float(-np.min(gr)), 2),
               limiter_max_gr_db=round(float(-db(gl.min())), 2),
               limiter_gr_over_1db_s=round(float(np.sum(gl < undb(-1.0)) / SR), 3),
               bed_lufs=round(A.loudness(bb_o), 2), beds=binfo, placed=placed)
    return stem, fx_o, bb_o, rep


# ============================================================================================ build
def _music_stale():
    m = os.path.join(AUD, 'music.wav')
    src = os.path.join(HERE, MODULE + '_music.py')
    return (not os.path.exists(m)) or os.path.getmtime(m) < os.path.getmtime(src)


PROTECT = [(F(PAYOFF) - 0.02, F(PAYOFF) + 0.6), (F(480) - 0.05, F(480) + 0.3)]
HERO_F = (60, 480, 810)


def mix(spec=None):
    """A (music + SFX) and B (SFX only) via the house kit epic_mix.mix_reel (loop=True). Writes mix_A.wav, mix_B.wav,
    stems/stem_{sfx,music}.wav, mix.json, mix.png."""
    work = os.path.join(AUD, '_mixwork')
    os.makedirs(work, exist_ok=True)
    rep = EX.mix_reel(MODULE, DUR, music=os.path.join(AUD, 'music.wav'), sfx=os.path.join(AUD, 'sfx.wav'), out_dir=work,
                      loop=True, protect=PROTECT, protect_cap_db=0.0, hero_times=[F(f) for f in HERO_F], spec=spec,
                      verbose=False)
    os.makedirs(os.path.join(AUD, 'stems'), exist_ok=True)
    moves = {'%s_mix.wav' % MODULE: 'mix_A.wav', '%s_vo_sfx.wav' % MODULE: 'mix_B.wav',
             '%s_stem_sfx.wav' % MODULE: 'stems/stem_sfx.wav', '%s_stem_music.wav' % MODULE: 'stems/stem_music.wav',
             '%s_mix.png' % MODULE: 'mix.png', '%s_mix.json' % MODULE: 'mix.json'}
    for a, b in moves.items():
        if os.path.exists(os.path.join(work, a)):
            shutil.move(os.path.join(work, a), os.path.join(AUD, b))
    shutil.rmtree(work, ignore_errors=True)
    keep = {k: rep.get(k) for k in ('integrated_lufs', 'true_peak_dbtp', 'lra_lu', 'limiter_max_gr_db', 'checks',
                                    'sfx_lufs_in_mix', 'music_lufs_in_mix', 'warnings')}
    keep['B'] = {k: rep['B_vo_sfx'].get(k) for k in ('lufs', 'tp_dbtp', 'lra', 'limiter_max_gr_db')}
    keep['A'] = {k: rep['A_full'].get(k) for k in ('lufs', 'tp_dbtp', 'lra', 'limiter_max_gr_db', 'glue_max_gr_db',
                                                   'loop_continuity_error_dbfs', 'seam')}
    keep['music'] = rep.get('music')
    return keep


def build():
    register()
    os.makedirs(AUD, exist_ok=True)
    stem, fx, bb, rep = sfx_bus()
    A._write_wav(os.path.join(AUD, 'sfx.wav'), stem, 24)
    A._write_wav(os.path.join(AUD, 'sfx_fx.wav'), fx, 24)
    A._write_wav(os.path.join(AUD, 'sfx_bed.wav'), bb, 24)
    json.dump(rep, open(os.path.join(AUD, 'sfx_cues.json'), 'w'), indent=1)
    print('sfx.wav  %.2f LUFS  TP %.2f dBTP  glue %.1f dB  limiter %.1f dB (%.2f s > 1 dB)' % (
        rep['lufs'], rep['true_peak_dbtp'], rep['glue_max_gr_db'], rep['limiter_max_gr_db'], rep['limiter_gr_over_1db_s']))
    if _music_stale():
        import sirf_36_shots_music as MU
        MU.build(AUD)
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
    json.dump(mrep, open(os.path.join(AUD, 'mix_summary.json'), 'w'), indent=1)
    print(json.dumps({k: mrep[k] for k in ('A', 'B', 'aac', 'checks')}, indent=1))
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
    seg = x[idx]
    k = A.kweight(seg) if hasattr(A, 'kweight') else seg
    ms = np.mean(np.sum(np.square(k), axis=1))
    return float(-0.691 + 10 * np.log10(ms + 1e-20))


def keyframes(mixA, sfx, music, placed):
    """Analysis at the key frames (hook, re-hook, drop-out, payoff, loop seam)."""
    out = {}
    ot, os_ = onsets(sfx)
    heroes = {0: 'hook f0 transient + ratchet click', 15: 'detent: dial lands 36', 60: 'flash pop', 240: 'tin land',
              375: 'thumb slap', 480: 're-hook bounce', 540: '2 TB', 600: '3,000 takes', 735: 'disk full',
              810: 'payoff', 900: 'portal lands', 1076: 'ratchet click across the seam'}
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
                          short_term_max_lufs=round(float(st[j]), 2), short_term_max_at_s=round(float(st_t[j]), 3),
                          payoff_window_max=round(win(F(810), F(830)), 2), rehook_window_max=round(win(F(478), F(500)), 2),
                          flash_window_max=round(win(F(58), F(75)), 2),
                          present_section_max=round(win(F(500), F(779)), 2),
                          ok=bool(F(810) - 0.05 <= lc_t[i] <= F(830)))
    out['dropout'] = dict(music_digital_silence_f780_f809=bool(not np.any(music[DROP[0] * SPF:DROP[1] * SPF])),
                          mixA_momentary_f782_f794=round(_mom(mixA, F(788), 0.4), 2),
                          mixA_rms_dbfs_f781_f794=round(float(db(np.sqrt(np.mean(np.square(mixA[781 * SPF:794 * SPF]))))), 2),
                          mixA_momentary_f796_f808_typing=round(_mom(mixA, F(802), 0.4), 2),
                          mixA_momentary_f765_f777_before=round(_mom(mixA, F(771), 0.4), 2),
                          ok=bool(-48.5 <= _mom(mixA, F(788), 0.4) <= -41.5))
    out['hook'] = dict(momentary_f0_f12=round(_mom(mixA, F(6), 0.4), 2), momentary_f40_f52=round(_mom(mixA, F(46), 0.4), 2),
                       momentary_f60_f72=round(_mom(mixA, F(66), 0.4), 2))
    w = _n(0.05)
    seam = np.concatenate([mixA[-w:], mixA[:w]])
    dd = np.abs(np.diff(seam, axis=0)).max(1)
    step = float(np.abs(mixA[0] - mixA[-1]).max())
    out['seam'] = dict(step=round(step, 6), local_median_step=round(float(np.median(dd)), 6),
                       step_over_local_p99=round(step / max(float(np.percentile(dd, 99)), 1e-9), 3),
                       momentary_last_0p4s=round(_mom(mixA, DUR - 0.2), 2), momentary_first_0p4s=round(_mom(mixA, 0.2), 2),
                       ok=bool(step <= max(float(np.percentile(dd, 99)), 1e-6) * 1.5))
    inst = {}
    for p in placed:
        inst.setdefault(round(p['hit_f']), []).append(p['name'])
    out['max_sounds_on_one_frame'] = max(len(v) for v in inst.values())
    out['frames_with_3_or_more'] = {k: v for k, v in sorted(inst.items()) if len(v) >= 3}
    out['ok'] = all(out[k]['ok'] for k in ('loudest', 'dropout', 'seam')) and all(s['ok'] for s in sync)
    return out


def overview(x, path, title, marks, placed=None):
    from PIL import Image, ImageDraw
    W, H = 1800, 620
    im = A.spectro_image(A.Sfx(x, 0, 'mix'), W, 440, None, title, '', fmin=30.0, fmax=20000.0, dyn=80.0)
    canvas = Image.new('RGB', (W, H), (14, 12, 16))
    canvas.paste(im, (0, 0))
    dr = ImageDraw.Draw(canvas)
    lc_t, lc = A.loudness_curve(x, 0.4, 0.02)
    y0, y1 = 450, 610
    lo, hi = -60.0, -5.0
    Y = lambda v: int(y1 - (np.clip(v, lo, hi) - lo) / (hi - lo) * (y1 - y0))  # noqa: E731
    for v in (-50, -40, -30, -20, -14, -10):
        dr.line([(0, Y(v)), (W, Y(v))], fill=(40, 38, 46))
        dr.text((2, Y(v) - 11), '%d' % v, fill=(120, 115, 130))
    pts = [(int(t / DUR * W), Y(v)) for t, v in zip(lc_t, lc)]
    dr.line(pts, fill=(255, 181, 71), width=2)
    for b in range(19):
        xx = int(b * 2.0 / DUR * W)
        dr.line([(xx, 44), (xx, y1)], fill=(70, 64, 84))
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
    files = dict(music='music.wav', sfx='sfx.wav', mix_A='mix_A.wav', mix_B='mix_B.wav')
    rep = dict(ebur128={k: ebur128(os.path.join(AUD, v)) for k, v in files.items()})
    rep['aac'] = {k: _aac_ebur(os.path.join(AUD, files[k])) for k in ('mix_A', 'mix_B')}
    for k in files:
        pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,duration_ts',
                             '-of', 'json', os.path.join(AUD, files[k])], capture_output=True, text=True)
        rep.setdefault('format', {})[k] = json.loads(pr.stdout)['streams'][0]
    mA, mB, sx, mu = rd('mix_A.wav'), rd('mix_B.wav'), rd('sfx.wav'), rd('music.wav')
    placed = json.load(open(os.path.join(AUD, 'sfx_cues.json')))['placed']
    rep['keyframes_A'] = keyframes(mA, sx, mu, placed)
    kb = keyframes(mB, sx, np.zeros_like(mu), placed)
    rep['keyframes_B'] = {k: kb[k] for k in ('loudest', 'dropout', 'seam')}
    e = rep['ebur128']
    rep['targets'] = dict(
        mix_A=bool(abs(e['mix_A']['I'] + 14) <= 0.5 and e['mix_A']['TP'] <= -2.0),
        mix_B=bool(abs(e['mix_B']['I'] + 14) <= 0.5 and e['mix_B']['TP'] <= -2.0),
        sfx=bool(abs(e['sfx']['I'] + 18) <= 0.3 and e['sfx']['TP'] <= -2.0),
        aac=bool(all(v['TP'] <= -1.5 and abs(v['I'] + 14) <= 0.5 for v in rep['aac'].values())),
        format=bool(all(v['codec_name'] == 'pcm_s24le' and int(v['sample_rate']) == SR and int(v['channels']) == 2
                        and int(v['duration_ts']) == N for v in rep['format'].values())))
    marks = [(0, 'f0 hook', (255, 243, 230)), (15, 'f15 detent', (255, 243, 230)), (60, 'f60 flash', (255, 181, 71)),
             (375, 'f375 thumb/stop', (80, 230, 255)), (480, 'f480 RE-HOOK', (242, 49, 43)),
             (780, 'f780 drop-out', (80, 230, 255)), (810, 'f810 PAYOFF', (255, 181, 71)), (900, 'f900 portal', (200, 160, 255)),
             (960, 'f960 outro', (200, 160, 255)), (1076, 'f1076 click', (255, 243, 230))]
    rep['png'] = [overview(mA, os.path.join(AUD, 'mix_A_overview.png'),
                           'sirf_36_shots mix_A (music + SFX)  %.1f LUFS  TP %.1f dBTP  (curve = momentary 400 ms)' % (
                               e['mix_A']['I'], e['mix_A']['TP']), marks, placed),
                  overview(mB, os.path.join(AUD, 'mix_B_overview.png'),
                           'sirf_36_shots mix_B (SFX only)  %.1f LUFS  TP %.1f dBTP' % (e['mix_B']['I'], e['mix_B']['TP']),
                           marks, placed),
                  overview(sx, os.path.join(AUD, 'sfx_overview.png'),
                           'sirf_36_shots sfx.wav  %.1f LUFS  TP %.1f dBTP' % (e['sfx']['I'], e['sfx']['TP']), marks, placed)]
    rep['ok'] = all(rep['targets'].values()) and rep['keyframes_A']['ok']
    json.dump(rep, open(os.path.join(AUD, 'sound.verify.json'), 'w'), indent=1)
    print(json.dumps({k: rep[k] for k in ('ebur128', 'aac', 'targets', 'keyframes_A', 'keyframes_B', 'ok')}, indent=1))
    return rep


# ============================================================================================ audition
AUDITION_SET = [('s36_wind', {}), ('s36_flash_charge', {}), ('s36_flash_charge', dict(dur=1.4, seed=1)),
                ('s36_flash_pop', {}), ('s36_rewind', dict(dur=1.2)), ('s36_tin_land', {}), ('s36_clock_tick', {}),
                ('s36_paper_plap', {}), ('s36_paper_flap', {}), ('s36_print_slide', {}), ('s36_print_slide', dict(slap=1)),
                ('s36_sticky_peel', {}), ('s36_hdd_spinup', {}), ('s36_error', {}), ('s36_rehook', {})]


def audition():
    register()
    os.makedirs(AUDITION, exist_ok=True)
    rows = []
    for name, prm in AUDITION_SET:
        x = A.sound(name, **prm)
        a = np.asarray(x, dtype=np.float64)
        tag = name + ''.join('_%s%s' % (k, v) for k, v in prm.items())
        A._write_wav(os.path.join(AUDITION, tag + '.wav'), a, 24)
        A.spectro_image(x, 1000, 420, x.hit, tag, 'hit %.3f s' % x.hit).save(os.path.join(AUDITION, tag + '.png'))
        st = A.stats(a, x.hit)
        q = A.qc(a, x.hit)
        rows.append(dict(sound=tag, dur=round(len(a) / SR, 3), hit=round(x.hit, 4), Mmax=st.get('Mmax'),
                         peak=st.get('peak'), crest=st.get('crest'), qc=q))
        print('%-34s dur %.2f hit %.3f Mmax %s qc %s' % (tag, len(a) / SR, x.hit, st.get('Mmax'), q or 'clean'))
    bed = np.asarray(A.sound('s36_hdd', dur=12.0, seeks=1), dtype=np.float64)
    A.spectro_image(A.Sfx(bed, 0, 's36_hdd'), 1000, 420, None, 's36_hdd seeks=1', '12 s loop').save(
        os.path.join(AUDITION, 's36_hdd.png'))
    json.dump(rows, open(os.path.join(AUDITION, 'audition.json'), 'w'), indent=1)
    return rows


def print_cues():
    cl = cues()
    for c in cl:
        print('f%-6s %-20s %6.1f dB  %-5s %s%s' % (c['frame'], c['name'], c['gain_db'], c['align'],
                                                 '' if c['gate'] else '[passes gate] ', c['event']))


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
        print(json.dumps(mix(), indent=1))
    else:
        sys.exit(0 if verify()['ok'] else 1)


if __name__ == '__main__':
    main()
