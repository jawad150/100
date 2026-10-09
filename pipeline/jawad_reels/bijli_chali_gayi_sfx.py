"""bijli_chali_gayi_sfx.py - SFX layer of Reel 2 / C11 "Bijli Chali Gayi" (@jawad_mp4). Owner: sound-designer.

Binding plan: brand_reels/design/reels/bijli_chali_gayi/BRIEF.md r2 section 6.10 (cue list, custom sounds, beds), 6.1-6.9
(frame-exact beat grid, power timeline, picture events), 6.11 (no music bed; the harmonium is the only music), SLATE
section 3.2 (sound motif = the double backup beep, registered as `backup_beep`, never labelled UPS / inverter) and 5.1
(-14 LUFS, TP <= -2.0 dBTP, VO >= 8 LU over the bed, <= 3 sounds on one instant, one drop-out at the reveal). Key from
MUSIC_bijli_chali_gayi.md: D major (backup_beep = D7 2349.32 Hz, end-card glass_tap tuned to D7). VO: the measured Vlad
stems and word timings in <RW>/vo/ (VO_TIMING.md). Cue sheet + measurements: SOUND.md in the same design folder.

What this module owns
    register()        adds the 12 local sounds to audio.SOUNDS (idempotent), after epic_sfx and sfx_jawad
    raw_cues(hook)    the brief's cue list for hook 'A' (public, blackout) or 'B' (Trial, torch-lit), frame-exact, before
                      the VO fit. The harmonium (music=True) is listed for the instant count but is NOT rendered into the
                      SFX stem: it lives in the music-supervisor's music_full.wav (one harmonium source only)
    cues(hook)        raw_cues -> sfx_jawad.fit_under_vo (words + the VO audio) -> local VO rules (keycaps low-passed
                      under words; tails carved under later speech)
    beds(hook)        exact bed automation (power timeline, loop phase locked so the A seam f1039 -> f0 is continuous)
    mix_loop(...)     audio.mix's chain on a LOOP: duck_under -> studio room send -> drop-out gate -> fold tails past DUR
                      onto t = 0 -> -18 LUFS -> 2:1 glue -> beds (exact levels, sidechained 5 dB under the SFX) ->
                      4x true-peak limiter (circular) at -2.0 dBTP
    BED, BED_GAIN_DB  None / -30: audio.mix cannot reproduce the per-frame beds or the loop. Do not let render.py build
                      this reel's SFX: render with `--no-sfx-build --audio <final mix>`.

Local sounds (each audio.qc() == [] at its default and used params; spectrograms in <RW>/audio/audition/)
    backup_beep(far)        THE SOUND MOTIF. Two 70 ms sine pulses at D7 2349.32 Hz (+ 3rd harmonic -20 dB: a piezo),
                            4 ms raised-cosine edges, pulse 2 +4 frames (the LED's f40/f44 pulses); far=1: lp 2600 + wetter
    match_strike            sandpaper scratch (58 ms) -> ignition crackle + flare 900 -> 2800 Hz + low whoomp + sizzle;
                            hit = the ignition (0.06 s)
    relay_click             backup box switching to battery: 2-6 kHz contact click + 120 Hz body + 6 ms contact bounce
    power_thunk(on)         55 Hz breaker thump + contact click; on=1 a 100/200/300 Hz mains hum swells in and settles
                            -18 dB, on=0 the hum falls 100 -> 60 Hz and is dead in 0.25 s
    crt_off(whine)          15.625 kHz line whine (-30 dB, 0.15 s pre-roll, stops on the hit) + 70 Hz "thoomp" + static;
                            whine=0 for the modern monitor (f480)
    crt_on                  degauss thunk + 50/100 Hz "bwong" (0.45 s) + static "tsss" + line whine
    tube_light_on(tinks)    strike click + tink + 100 Hz choke buzz settling to -20 dB; `tinks` starter tinks BEFORE the
                            hit (cued with tinks=0 here: in the picture the tubes snap on on the power-on frame)
    tube_flicker(n)         n x 25 ms 100 Hz buzz stutters, 40 ms apart (brownouts; n=2 for 2-frame blips)
    fan_wind(mode, ...)     ceiling / PC fan air: noise band amplitude-modulated at the blade-pass rate (3 blades x 4.5
                            rev/s = 13.5 Hz); down = rate decays exp(-t / tau) (tau 1.0 s = the picture), up = 0 -> rate
                            out_cubic over `duration`, then `hold`, then `release`; 100 Hz motor hum only while powered
    keycap_thock(pitch)     mechanical keycap: modal "thock" + 160 Hz body + contact click, release click 4 frames later
                            (the 2D press holds 2 f after a 2 f press); pitch = resample (Ctrl 0.94, S 1.0)
    mohalla_cheer(dur, cut) the neighbourhood cheering, WORDLESS: granular resynthesis of the CC0 "Crowd shouting/speaking
                            ambience" (starninjas, OpenGameArt; crowd_cheer_real's source) - reversed 60-100 ms grains
                            from random positions, +-1.5 st, 80 grains/s, band 180-6500 Hz, outdoor reverb. The raw
                            sample is NOT wordless (faster-whisper small/medium hear "Oh my God, look at that!" at
                            p 0.52-0.82), so crowd_cheer_real is never used. `verify` re-checks with whisper.
    room_mains   (bed)      8 s loop: fan run (13.5 Hz AM, 108 cycles) + 100 Hz motor -24 + tube buzz -30 + CRT whine
                            15.625 kHz -42 + room tone -6
    night_crickets (bed)    DUR-long loop (34.667 s, so one phase reference is seamless at the seam): 6 field-cricket
                            voices 4.2-4.9 kHz, chirps of 3-4 pulses (18 ms on / 30 ms period), 1.8-3.0 chirps/s, slow
                            detune, pans -0.7..0.7, + night_air at -10 rel, outdoor reverb (circular)

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
    python3 bijli_chali_gayi_sfx.py cues [--hook A|B]       cue table after the VO fit
    python3 bijli_chali_gayi_sfx.py audition                 local sounds -> <RW>/audio/audition/*.wav + .png + qc
    python3 bijli_chali_gayi_sfx.py build [--hook A|B|AB]    SFX stem(s) <RW>/audio/bijli_chali_gayi_sfx_<h>.wav (+ _fx /
                                                             _bed splits, _overview.png, _cues.json, _report.json)
    python3 bijli_chali_gayi_sfx.py rough [--hook A|B|AB]    rough mixes <RW>/audio/bijli_chali_gayi_rough_<h>_{full,dry}.wav
                                                             (VO stem + SFX stem + music_full.wav harmonium), -14 LUFS
    python3 bijli_chali_gayi_sfx.py verify                   faster-whisper: mohalla_cheer wordless; V1 readable in rough A
"""
import argparse
import json
import math
import os
import subprocess
import sys
from fractions import Fraction

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE ends up first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import audio as A  # noqa: E402
from audio import (SR, TWO_PI, _t, _n, _rng, _st, _ar, _fade, _taper, _thump, _click,  # noqa: E402
                   _crackle, _loop_mask_noise, _periodic_lfo, _unit, noise_band, modal, osc, lp, hp, bp, pan, undb,
                   db, reverb, reverb_circular)
import epic_sfx as ES  # noqa: E402  (shared, read-only)
import sfx_jawad as SJ  # noqa: E402  (shared, read-only: fit_under_vo, vo_activity)

MODULE = 'bijli_chali_gayi'
FPS, BPM, NF = 30, 90.0, 1040
DUR = NF / FPS                                 # 34.6667 s = 13 bars at 90 BPM (20 f / beat, 80 f / bar)
N = _n(DUR)
assert N == 1664000
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
AUDITION = os.path.join(AUD, 'audition')
VO_DIR = os.path.join(RW, 'vo')
MUSIC = os.path.join(RW, 'music', 'music_full.wav')
MUSIC_JSON = os.path.join(RW, 'music', 'music_full.json')
TARGET_LUFS, TP_CEILING = -18.0, -2.0          # SFX stem (BRIEF 0 / bible 4.1)
FINAL_LUFS, FINAL_TP, LIMIT_CEIL = -14.0, -2.0, -2.3
BED, BED_GAIN_DB = None, -30.0                 # see the docstring: never audio.mix / render.py's auto-build


def F(f):
    """Reel time of frame f (30 fps)."""
    return f / FPS


# ============================================================================================ picture constants (BRIEF 6.1-6.9)
POWER = ((0, 14, 1), (14, 240, 0), (240, 300, 1), (300, 400, 0), (400, 480, 1), (480, 560, 0), (560, 720, 1),
         (720, 880, 0), (880, 1040, 1))        # (f0, f1, on): ON f0-f13, OFF f14-f239, ...
DROP = (F(790), F(800))                        # the one drop-out, 26.333-26.667 s (half a beat before the payoff)
PRESSES = (580, 600, 620, 640, 650, 660, 670, 680, 690, 700, 710)   # Ctrl+S: quarters, then 8ths from f640
T_END = F(920)                                 # end card start (beat 46), EndCard dur 4.0
# key (MUSIC_bijli_chali_gayi.md): D major. glass_tap(seed 0) measured dominant partial 2096.3 Hz -> D7.
D7 = 2349.32
GLASS_PITCH = round(D7 / 2096.3, 4)            # 1.1207
CHEER_SRC = 'opengameart/crowd_shouting/crowd_shouting_0.ogg'   # CC0, starninjas (library/LICENSES.md)


# ============================================================================================ local sounds
def _cos_window(t, on, length, edge):
    """Raised-cosine gate: 0 before `on`, `edge` s ramps, flat for `length` s in total."""
    u = t - on
    a = np.clip(u / edge, 0, 1)
    b = np.clip((length - u) / edge, 0, 1)
    w = 0.5 - 0.5 * np.cos(np.pi * np.minimum(a, b))
    return np.where((u >= 0) & (u <= length), w, 0.0)


def _soft(x, drive):
    """Alias-safe tanh saturation (sfx_jawad.shape, 8x oversampled) at the buffer's own peak: lower crest factor, so
    the stem limiter does not have to flatten the transient (BRIEF 6.10: limiter GR < ~3 dB)."""
    pk = float(np.max(np.abs(x))) + 1e-12
    return SJ.shape(np.asarray(x, dtype=np.float64) / pk, drive) * pk


def backup_beep(seed=0, far=0):
    """The double backup-box beep (THE sound motif). hit = onset of pulse 1 (0.0)."""
    d = 0.42
    t = _t(d)
    x = np.zeros(len(t))
    for on in (0.0, 4.0 / FPS):                        # pulse 2 onset +0.1333 s (LED pulses f40-41 / f44-45)
        u = np.maximum(t - on, 0.0)
        x += _cos_window(t, on, 0.070, 0.004) * (np.sin(TWO_PI * D7 * u) + undb(-20) * np.sin(TWO_PI * 3 * D7 * u))
    y = _st(x)
    if far:                                            # downstairs, through a wall
        y = reverb(lp(y, 2600.0, 2), 'room', wet_db=-14)
    else:
        y = reverb(y, 'room', wet_db=-26)
    return SJ._done(y, 0.0, -8.0, 'backup_beep', keep_until=0.24)


def match_strike(seed=0):
    """Match strike: scratch, ignition (hit 0.06 s), flare, whoomp, sizzle."""
    r = _rng(seed, 'match_strike')
    ign = 0.060
    out = np.zeros((_n(1.0), 2))
    ls = _n(0.058)
    scratch = _crackle(0.058, r, 2600.0, 2000.0, 7000.0, env=lambda p: 0.35 + 0.65 * p, gdur=(0.0006, 0.003),
                       spread=0.3)
    grit = _unit(bp(r.standard_normal(ls), 2000.0, 7000.0)) * np.linspace(0.15, 0.6, ls) * 0.08
    A._add(out, scratch * 0.4 + _st(_fade(grit, 0.003, 0.004)), 0.002)
    A._add(out, _crackle(0.09, r, 1800.0, 1500.0, 9000.0, env=lambda p: np.exp(-4.0 * p), spread=0.5) * 1.2, ign)
    tt = _t(0.30)
    flare = noise_band(0.30, r, [(0.0, 900.0), (0.4, 2800.0), (1.0, 2200.0)], bw=0.7, width=0.4)
    A._add(out, flare * (_ar(tt, 0.004, 0.07) * 0.30)[:, None], ign)
    A._add(out, _st(_thump(0.14, 90.0, 40.0, 0.010, 0.040, r, attack=0.002, drive=1.6, noise=0.3)) * 0.45, ign)
    A._add(out, _crackle(0.5, r, 300.0, 2000.0, 8000.0, env=lambda p: (1.0 - p) ** 1.5, spread=0.6) * 0.5, ign + 0.03)
    return SJ._done(reverb(_soft(out, 4.0), 'room', wet_db=-18), ign, -6.0, 'match_strike', keep_until=ign + 0.5)


def relay_click(seed=0):
    """Backup box switching to battery: contact click + low body + a contact bounce. hit = 0.0."""
    r = _rng(seed, 'relay_click')
    d = 0.14
    x = _click(d, r, (2000.0, 6000.0), 0.0015, modes=[(2900.0, 0.004, 0.35), (4700.0, 0.003, 0.20)])
    x += 0.6 * _thump(d, 120.0, 40.0, 0.004, 0.015, r, attack=0.0008, drive=1.4, noise=0.2)
    A._add(x, _click(0.03, r, (2500.0, 7000.0), 0.0008) * 0.35, 0.006)
    return SJ._done(reverb(_st(x), 'room', wet_db=-22), 0.0, -10.0, 'relay_click', fin=0.0002)


def _mains(t, f0=100.0, amps=(1.0, 0.5, 0.25, 0.12, 0.06)):
    """Mains hum / choke buzz: 100 Hz (2 x 50 Hz mains) and its harmonics."""
    return sum(a * np.sin(TWO_PI * f0 * (k + 1) * t) for k, a in enumerate(amps))


def power_thunk(seed=0, on=1):
    """Mains coming back (on=1) or dying (on=0): breaker thump + contact click + hum. hit = 0.0."""
    r = _rng(seed, 'power_thunk')
    d = 1.0 if on else 0.6
    t = _t(d)
    x = np.zeros(len(t))
    body = _thump(0.35, 55.0, 35.0, 0.012, 0.05, r, attack=0.002, drive=2.0, noise=0.35)
    x[:len(body)] += body
    clk = _click(0.06, r, (1500.0, 5000.0), 0.002, modes=[(1900.0, 0.006, 0.4), (3300.0, 0.004, 0.25)])
    x[:len(clk)] += 0.45 * clk
    x = _soft(x, 3.0)
    if on:                                             # hum swells in over 0.15 s, settles -18 dB over ~0.6 s
        a = np.clip(t / 0.15, 0, 1)
        env = (0.5 - 0.5 * np.cos(np.pi * a)) * (undb(-18) + (1 - undb(-18)) * np.exp(-np.maximum(t - 0.15, 0) / 0.2))
        x += 0.30 * _mains(t, 100.0, (1.0, 0.6, 0.3)) * env
    else:                                              # hum falls 100 -> 60 Hz, dead in 0.25 s
        u = np.clip(t / 0.25, 0, 1)
        f = 100.0 - 40.0 * u
        x += 0.30 * (osc(f) + 0.5 * osc(2 * f)) * (1 - u) ** 2 * np.clip(t / 0.003, 0, 1)
    x = _taper(x, sec=0.25)
    return SJ._done(reverb(_st(x), 'room', wet_db=-20), 0.0, -4.0, 'power_thunk')


def crt_off(seed=0, whine=1):
    """CRT / monitor switching off: line whine (pre-roll 0.15 s, stops on the hit), "thoomp", static. hit = 0.15."""
    r = _rng(seed, 'crt_off')
    pre = 0.15
    d = pre + 0.7
    t = _t(d)
    x = np.zeros((len(t), 2))
    A._add(x, _st(_thump(0.30, 70.0, 50.0, 0.008, 0.06, r, attack=0.003, drive=1.8, noise=0.3)) * 0.8, pre)
    A._add(x, _crackle(0.12, r, 2500.0, 3000.0, 9000.0, env=lambda p: np.exp(-3.0 * p), spread=0.4) * 0.6, pre)
    x = _soft(x, 3.0)
    if whine:
        g = np.clip(t / 0.02, 0, 1) * np.clip((pre - t) / 0.002, 0, 1)    # 20 ms fade-in, 2 ms stop at the hit
        x += (undb(-30) * np.sin(TWO_PI * 15625.0 * t) * (0.5 - 0.5 * np.cos(np.pi * g)))[:, None]
    return SJ._done(reverb(x, 'room', wet_db=-20), pre, -6.0, 'crt_off', keep_until=pre + 0.3)


def crt_on(seed=0):
    """CRT switching on: degauss thunk + 50/100 Hz "bwong" + static "tsss" + line whine. hit = 0.0."""
    r = _rng(seed, 'crt_on')
    d = 0.9
    t = _t(d)
    x = np.zeros((len(t), 2))
    A._add(x, _st(_thump(0.25, 60.0, 30.0, 0.010, 0.040, r, attack=0.002, drive=1.6, noise=0.3)) * 0.8, 0.0)
    f = 50.0 * (1 + 0.04 * np.exp(-t / 0.1))
    bwong = (osc(f) + 0.7 * osc(2 * f)) * (1 + 0.35 * np.sin(TWO_PI * 7.0 * t)) * _ar(t, 0.01, 0.15)
    x += (0.45 * bwong)[:, None]
    tss = noise_band(0.35, r, 5000.0, bw=0.8, width=0.5)
    A._add(x, tss * (_ar(_t(0.35), 0.01, 0.12) * 0.10)[:, None], 0.0)
    wg = np.clip((t - 0.05) / 0.03, 0, 1)
    x += (undb(-30) * np.sin(TWO_PI * 15625.0 * t) * (0.5 - 0.5 * np.cos(np.pi * wg)))[:, None]
    x = _taper(x, sec=0.2)
    return SJ._done(reverb(x, 'room', wet_db=-20), 0.0, -8.0, 'crt_on')


def tube_light_on(seed=0, tinks=2, gap=0.18):
    """Tube light striking: `tinks` starter tinks before the hit, strike click + tink, choke buzz settling -20 dB."""
    r = _rng(seed, 'tube_light_on')
    pre = tinks * gap
    d = pre + 1.2
    t = _t(d)
    x = np.zeros(len(t))

    def tink(a):
        return modal(0.15, [2100.0, 2100.0 * 2.76, 5300.0], [0.020, 0.010, 0.006], [1.0, 0.3, 0.15], r,
                     contact=0.0003) * a
    for k in range(int(tinks)):
        A._add(x, tink(0.30), k * gap)
    A._add(x, _click(0.05, r, (1500.0, 6000.0), 0.002) * 0.6 + tink(0.45)[:_n(0.05)], pre)
    u = np.maximum(t - pre, 0)
    env = (t >= pre) * (undb(-20) + (1 - undb(-20)) * np.exp(-u / 0.25)) * np.clip(u / 0.004, 0, 1)
    env *= np.where(u < 0.10, 1 - 0.6 * (np.abs(np.sin(TWO_PI * 15.0 * u)) > 0.85), 1.0)   # two quick catches
    x += 0.35 * np.tanh(2.5 * _mains(t, 100.0, (1.0, 0.4, 0.3, 0.2, 0.1))) * A._smooth(env, 0.002)
    x = _taper(x, sec=0.25)
    return SJ._done(reverb(_st(x), 'room', wet_db=-18), pre, -10.0, 'tube_light_on', keep_until=pre + 1.0)


def tube_flicker(seed=0, n=3):
    """Brownout flicker: n x 25 ms buzz stutters, 40 ms apart. hit = 0.0 (first stutter)."""
    r = _rng(seed, 'tube_flicker')
    d = 0.04 * n + 0.15
    t = _t(d)
    x = np.zeros(len(t))
    amps = (1.0, 0.6, 0.85, 0.5)
    for k in range(int(n)):
        on = 0.04 * k
        x += _cos_window(t, on, 0.025, 0.003) * amps[k % 4] * np.tanh(2.0 * _mains(t, 100.0))
        A._add(x, _click(0.02, r, (1000.0, 4000.0), 0.001) * 0.15 * amps[k % 4], on)
    return SJ._done(reverb(_st(x), 'room', wet_db=-20), 0.0, -12.0, 'tube_flicker', fin=0.0005)


def fan_wind(seed=0, mode='down', duration=3.0, tau=None, rate=13.5, fc=450.0, hold=0.0, release=0.03, motor=1):
    """Fan air. mode 'down': full speed at the start, blade-pass rate decays exp(-t / tau) (default duration / 3),
    gone at `duration`. mode 'up': spins up 0 -> rate (out_cubic) over `duration`, holds `hold` s, `release` fade;
    motor hum (100 Hz) only while powered (up). hit = 0.0 (cue with align='start')."""
    r = _rng(seed, 'fan_wind')
    if mode == 'down':
        tau = duration / 3.0 if tau is None else float(tau)
        d = duration
        t = _t(d)
        rt = rate * np.exp(-t / tau)
        amp = (rt / rate) ** 1.5 * np.clip((d - t) / (0.25 * d), 0, 1) ** 2
    else:
        d = duration + hold + release
        t = _t(d)
        u = np.clip(t / duration, 0, 1)
        rt = rate * (1 - (1 - u) ** 3)
        amp = (rt / rate) ** 1.5 * np.clip((d - t) / max(release, 1e-3), 0, 1)
    ph = TWO_PI * np.cumsum(rt) / SR
    am = 0.55 + 0.45 * (0.5 + 0.5 * np.sin(ph)) ** 1.5
    pts = np.linspace(0, 1, 33)
    fcs = [(p, fc * (0.6 + 0.4 * float(np.interp(p * d, t, rt)) / rate)) for p in pts]
    air = noise_band(d, r, fcs, bw=0.9, width=0.5)
    x = air * (am * amp)[:, None]
    if mode != 'down' and motor:
        x += (undb(-24) * 2.0 * np.sin(TWO_PI * 100.0 * t) * np.clip(t / 0.02, 0, 1)
              * np.clip((d - t) / max(release, 1e-3), 0, 1))[:, None]
    return SJ._done(reverb(x, 'room', wet_db=-14), 0.0, -12.0, 'fan_wind', fin=0.02, keep_until=d)


def keycap_thock(seed=0, pitch=1.0, release=4.0 / FPS):
    """One mechanical keycap: press "thock" (hit 0.0) + release click `release` s later."""
    r = _rng(seed, 'keycap_thock')
    d = release + 0.25
    t = _t(d)
    f1 = 430.0 * r.uniform(0.97, 1.03)
    x = _unit(bp(r.standard_normal(len(t)), 2500.0, 8000.0)) * _ar(t, 0.0002, 0.0012) * 0.20
    x += 0.8 * modal(d, [f1, f1 * 2.35, f1 * 4.3], [0.020, 0.012, 0.007], [1.0, 0.45, 0.25], r, contact=0.0006)
    x += 0.45 * _thump(d, 160.0, 60.0, 0.004, 0.025, r, attack=0.0006, drive=1.5, noise=0.4, noise_lp=700.0)
    rel = (_unit(bp(r.standard_normal(_n(0.03)), 2000.0, 7000.0)) * _ar(_t(0.03), 0.0002, 0.001) * 0.20
           + modal(0.03, [f1 * 1.3], [0.008], [0.25], r))
    A._add(x, rel, release)
    y = reverb(_st(_soft(x, 2.5)), 'room', wet_db=-17)
    if abs(pitch - 1.0) > 1e-4:
        fr = Fraction(pitch).limit_denominator(64)
        y = signal.resample_poly(y, fr.denominator, fr.numerator, axis=0)
    return SJ._done(y, 0.0, -6.0, 'keycap_thock', fin=0.0002)


def pankhi_swing(seed=0, dur=0.55):
    """Hand fan (pankhi) swing: soft air whoosh peaking on the hit (0.22 s) with palm-leaf crackle riding the same
    swell. hit = the loudest pass."""
    r = _rng(seed, 'pankhi_swing')
    hit = 0.22
    t = _t(dur)
    env = A._swell(t, hit, 2.0, 0.07)
    air = noise_band(dur, r, [(0.0, 500.0), (hit / dur, 1300.0), (1.0, 700.0)], bw=0.9, width=0.4) * env[:, None]
    cr = _crackle(dur, r, 900.0, 1500.0, 7000.0, env=lambda p: np.interp(p, t / dur, env) ** 1.5, spread=0.4)
    return SJ._done(reverb(air * 0.5 + cr * 0.6, 'room', wet_db=-18), hit, -12.0, 'pankhi_swing', keep_until=dur)


_CHEER = {}


def _cheer_source():
    """The CC0 crowd recording (decoded by epic_sfx, cached) + the sample positions of its loud half."""
    if 'x' not in _CHEER:
        x = ES._decode(CHEER_SRC)
        if x is None:
            raise FileNotFoundError(os.path.join(ES.LIB, CHEER_SRC))
        m = np.square(x).mean(1)
        e = np.sqrt(uniform_filter1d(m, _n(0.1)))
        ok = np.nonzero(e > np.percentile(e, 50))[0]
        _CHEER['x'], _CHEER['ok'] = x, ok[(ok > _n(0.2)) & (ok < len(x) - _n(0.3))]
    return _CHEER['x'], _CHEER['ok']


def mohalla_cheer(seed=0, dur=2.0, cut=1):
    """Wordless neighbourhood cheer (granular, see docstring). hit = 0.03 (the eruption); `dur` = hit -> end;
    cut=1 stops dead at the end (12 ms) before the outdoor reverb, so only the space rings on."""
    r = _rng(seed, 'mohalla_cheer')
    src, ok = _cheer_source()
    h = 0.03
    tot = h + dur
    out = np.zeros((_n(tot + 0.15), 2))

    def env(tt):                                       # eruption, then a slow sag; natural decay when not cut
        e = np.clip((tt - 0.005) / (h + 0.04), 0, 1) ** 1.5 * (1.0 - 0.25 * np.clip((tt - h) / max(dur, 0.1), 0, 1))
        if not cut:
            e *= np.clip((tot - tt) / min(0.6, 0.4 * dur), 0, 1)
        return e
    for _ in range(int(80 * tot)):
        t0 = r.uniform(-0.06, tot)
        gl = r.uniform(0.06, 0.10)
        ratio = 2 ** (r.uniform(-1.5, 1.5) / 12.0)
        L = _n(gl)
        p0 = int(ok[r.integers(0, len(ok))])
        idx = p0 + np.arange(L) * ratio
        g = np.stack([np.interp(idx, np.arange(len(src)), src[:, c]) for c in range(2)], 1)[::-1]
        g = g * np.hanning(L)[:, None]
        g = pan(g, r.uniform(-0.6, 0.6))
        a = float(env(np.clip(t0 + gl / 2, 0, tot)))
        if a > 0:
            A._add(out, g * a, max(t0, 0.0))
    out = bp(out, 180.0, 6500.0, 2)
    if cut:
        k = _n(tot)
        out[k:] = 0.0
        w = np.clip((tot - np.arange(len(out)) / SR) / 0.012, 0, 1)
        out *= (0.5 - 0.5 * np.cos(np.pi * w))[:, None]
    out[:_n(0.004)] *= np.linspace(0, 1, _n(0.004))[:, None]
    return SJ._done(reverb(out, 'outdoor', wet_db=-10), h, -6.0, 'mohalla_cheer', keep_until=tot)


def room_mains(dur=8.0, seed=0):
    """Bed (seamless loop): the lit 2000s room - ceiling fan, motor and tube hum, CRT whine, room tone."""
    r = _rng(seed, 'room_mains')
    L = _n(dur)
    tl = np.arange(L) / SR
    rate = round(13.5 * dur) / dur                     # integer blade-pass cycles per loop (108 in 8 s)

    def mask(tl_, f):
        lf = np.log2(np.maximum(f, 8.0))[None, :]
        return (np.exp(-0.5 * ((lf - np.log2(450.0)) / 0.75) ** 2)
                + 0.08 * np.exp(-0.5 * ((lf - np.log2(1800.0)) / 0.8) ** 2)) * np.ones((len(tl_), 1))
    air = _unit(_loop_mask_noise(L, r, mask, corr=0.4))
    am = 0.6 + 0.4 * (0.5 + 0.5 * np.sin(TWO_PI * rate * tl + r.uniform(0, TWO_PI))) ** 1.5
    x = air * am[:, None]
    hum = undb(-24) * np.sin(TWO_PI * 100.0 * tl) + undb(-30) * np.tanh(2.0 * _mains(tl, 100.0)) / 1.2
    hum += undb(-42) * np.sin(TWO_PI * 15625.0 * tl)
    x += hum[:, None]
    rt = np.asarray(A.room_tone(dur=dur, seed=seed), dtype=np.float64)
    x += _unit(rt) * undb(-6)
    return SJ._bed_done(reverb_circular(x, 'room', wet_db=-10), 'room_mains')


def night_crickets(dur=DUR, seed=0):
    """Bed (seamless loop, default length = DUR): field crickets + night air."""
    r = _rng(seed, 'night_crickets')
    L = _n(dur)
    tl = np.arange(L) / SR
    out = np.zeros((L, 2))
    for v in range(6):
        f0 = r.uniform(4200.0, 4900.0)
        k = int(round(r.uniform(1.8, 3.0) * dur))
        period = dur / k
        npulse = int(r.choice([3, 4]))
        span = npulse * 0.030
        f = f0 * (1 + 0.004 * np.sin(TWO_PI * int(r.integers(1, 3)) * tl / dur + r.uniform(0, TWO_PI)))
        car = np.sin(TWO_PI * np.cumsum(f) / SR)
        gate = np.zeros(L)
        off = r.uniform(0.02, max(0.03, period - span - 0.03))
        for j in range(k):
            c0 = off + j * period + r.uniform(-0.008, 0.008)
            if c0 < 0.005 or c0 + span > dur - 0.02:   # no chirp straddles the loop seam
                continue
            for p in range(npulse):
                on = c0 + p * 0.030
                i0, i1 = _n(on), _n(on + 0.018)
                w = _cos_window(np.arange(i1 - i0 + 1) / SR, 0.0, 0.018, 0.003)
                gate[i0:i0 + len(w)] += w * (0.7 if p == 0 else 1.0)
        voice = lp(car * gate * r.uniform(0.35, 1.0), r.uniform(6000.0, 12000.0), 2)
        out += pan(voice, r.uniform(-0.7, 0.7))
    out = reverb_circular(out, 'outdoor', wet_db=-12)
    out *= undb(-20.0 - A.loudness(out))
    na = np.asarray(A.night_air(dur=dur, seed=seed), dtype=np.float64)
    na *= undb(-30.0 - A.loudness(na))
    return SJ._bed_done(out + na, 'night_crickets')


META = dict(   # name: (category, character, use, room send dB or None = category default)
    backup_beep=('ui', 'double piezo beep, D7 2349.32 Hz, pulses 0.133 s apart (far=1: through a wall)',
                 'C11 sound motif: the backup box LED (f40/f60 hook A, f0/f40 hook B, f310 far, f380)', -24.0),
    match_strike=('impact', 'match scratch, ignition, flare, sizzle', 'C11 splice f80: the match lights the candle', None),
    relay_click=('ui', 'relay contact click + bounce', 'C11 f14: the backup box switches to battery', None),
    power_thunk=('impact', 'breaker thump + mains hum swelling in (on=1) or dying (on=0)',
                 'C11 power events f240, f300, f400, f480, f880', None),
    crt_off=('impact', 'CRT switch-off: line whine stops, thoomp, static', 'C11 CRT / monitor collapse f12, f480', None),
    crt_on=('impact', 'CRT degauss thunk + bwong + static', 'C11 f883 CRT on', None),
    tube_light_on=('transition', 'tube light strike + choke buzz', 'C11 f243 distant tubes, f882 the room tube', None),
    tube_flicker=('transition', '100 Hz buzz stutters', 'C11 brownouts f10, f470; far window f220 (lp 250)', None),
    fan_wind=('transition', 'fan air at the blade-pass rate, winding down / spinning up',
              'C11 ceiling fan f14 / f881, rooftop fans f242 / f301, PC fans f481', None),
    keycap_thock=('ui', 'mechanical keycap press + release', 'C11 Ctrl+S presses f579-f710', None),
    pankhi_swing=('transition', 'hand-fan air swing + palm-leaf crackle', 'C11 S2 pankhi swings f100 / f120 / f140',
                  None),
    mohalla_cheer=('texture', 'wordless neighbourhood cheer (granular CC0 crowd)', 'C11 f241 AA GAYI!, f885', -18.0),
    room_mains=('bed', 'lit 2000s room: fan, mains hum, tube buzz, CRT whine', 'C11 power ON in the old room', None),
    night_crickets=('bed', 'field crickets + night air', 'C11 power cuts, rooftops', None),
)
LOCAL = tuple(META)


def register():
    """epic_sfx + sfx_jawad + this reel's sounds into audio.SOUNDS (idempotent)."""
    ES.register()
    SJ.register()
    for n, (cat, ch, use, send) in META.items():
        if n not in A.SOUNDS:
            A._register(cat, ch, use, send)(globals()[n])
    return list(META)


# ============================================================================================ cue sheet (BRIEF 6.10, r2)
def _c(f, name, gain, ev, ver='AB', align='hit', t=None, **kw):
    c = dict(t=round(F(f) if t is None else t, 6), f=round(F(f) * FPS if t is None else t * FPS, 2), name=name,
             gain_db=float(gain), align=align, ev=ev, ver=ver)
    c['params'] = kw.pop('params', {})
    c.update(kw)
    return c


def _plan_cues():
    """jawad_tx Plan cues (L7, L8, L4) and the end card's cues, computed by the shared modules."""
    import jawad_tx as X
    import endcard as E
    plan = X.Plan([('L7', F(320), dict(src=(540, -900), a0=-40, a1=40, width=2.2, haze=0.45, rays=0.0)),
                   ('L8', F(560), dict(n=7, black=0)), ('L4', F(880))])
    card = E.EndCard('COMMENT MEIN', 'batao', sub='Chhat ya candle?', monogram='JD', dur=4.0, y_mono=360.0,
                     y_key=730.0, y_sub=965.0, y_sig=1575.0)
    assert abs((DUR - card.dur) - T_END) < 1e-9
    return plan.cues(), card.cues(T_END, DUR)


def raw_cues(hook='A'):
    """The brief's cue list (r2) for hook 'A' or 'B', with this designer's measured changes (see SOUND.md 'Changes')."""
    assert hook in ('A', 'B')
    pc, cc = _plan_cues()
    L = {(c['tx'], c['name']): c for c in pc}
    C = []
    # ---- hook A (blackout)
    if hook == 'A':
        C += [_c(0, 'impact_soft', -8, 'f0 transient = the loop landing (release of the end-card swell)', 'A', lp=900,
                 sat=3.0),
              _c(10, 'tube_flicker', -12, 'brownout f10-f13 (mains x0.45, 0.80, 0.35, 0.15)', 'A', pan=-0.3),
              _c(12, 'crt_off', -8, 'CRT collapse (phase 1 f12-f14)', 'A', pan=-0.15),
              _c(14, 'relay_click', -10, 'mains 0: the backup box switches to battery', 'A', pan=0.4),
              _c(14, 'fan_wind', -14, 'ceiling fan winds down (tau 1.0 s, gone by f80)', 'A', align='start',
                 params=dict(mode='down', duration=round(F(80) - F(14), 4), tau=1.0)),
              _c(15, 'shimmer', -12, 'H1 "Bijli" glows (truncated so it is gone by f80)', 'A', hp=5500, dur=2.1),
              _c(20, 'mouse_click', -10, 'torch clicks on (beat 1)', 'A', pan=0.5),
              _c(40, 'backup_beep', -6, 'LED pulses f40 / f44 (beat 2)', 'A', pan=0.45, vo_exempt=True),
              _c(60, 'backup_beep', -6, 'LED pulses f60 / f64 (beat 3, cover frame)', 'A', pan=0.45)]
    else:
        C += [_c(0, 'backup_beep', -6, 'LED pulses f0 / f4 (the f0 transient)', 'B', pan=0.45),
              _c(40, 'backup_beep', -6, 'LED pulses f40 / f44', 'B', pan=0.45)]
    # ---- body (A and B share every cue from here)
    C += [_c(80, 'match_strike', -8, 'splice f80: the match ignites (flare = exposure push)'),
          _c(100, 'pankhi_swing', -12, 'pankhi swings in from the right', pan=0.3),
          _c(120, 'pankhi_swing', -12, 'pankhi swing', pan=0.3),
          _c(140, 'pankhi_swing', -12, 'pankhi swing (tilt starts)', pan=0.3),
          _c(160, 'whoosh_slow', -10, 'tilt through the ceiling: loudest pass on the f160 cut', lp=1100),
          _c(220, 'tube_flicker', -24, 'far window false start f220-f221 (hum blip only)', lp=250, pan=-0.4,
             params=dict(n=2)),
          _c(240, 'power_thunk', -4, 'power back: bulbs cascade f240-f245', hero=True, params=dict(on=1)),
          _c(240, 'impact_soft', -4, '"AA GAYI!" slams (SLAM spring)', hero=True, sat=3.0),
          _c(241, 'mohalla_cheer', -10, 'the street cheers (wordless), cut dead at f300', params=dict(
              dur=round(F(300) - F(241), 4), cut=1)),
          _c(242, 'fan_wind', -12, 'rooftop fans spin up (held until the f300 death)', align='start',
             params=dict(mode='up', duration=1.9, hold=round(F(300) - F(242) - 1.9, 4), release=0.03)),
          _c(243, 'tube_light_on', -12, 'distant tube lights / windows snap on', lp=2500, pan=-0.35,
             params=dict(tinks=0)),
          _c(300, 'power_thunk', -6, 'the gag: everything dies again (beat 15)', hero=True, params=dict(on=0)),
          _c(301, 'fan_wind', -14, 'rooftop fans wind down', align='start', params=dict(mode='down', duration=2.0)),
          _c(310, 'backup_beep', -8, 'a backup box beeps downstairs (far)', pan=-0.3, params=dict(far=1)),
          dict(L[('L7', 'whoosh_slow')], f=320.0, gain_db=-9.0, ev='L7 torch-beam sweep crosses frame centre (bar 4)',
               ver='AB'),
          dict(L[('L7', 'shimmer')], f=320.0, ev='L7 beam glints', ver='AB'),
          _c(380, 'backup_beep', -6, 'the box in the old room (between V5 and V6)', pan=0.45),
          _c(400, 'power_thunk', -6, 'lights on: the modern desk (on-word cut)', lp=1100, params=dict(on=1)),
          _c(440, 'ui_tick', -12, 'render 63 -> 64 %', pan=0.3),
          _c(470, 'tube_flicker', -14, 'brownout dip f470-f472 (desk lamp, monitor)', pan=-0.5, params=dict(n=2)),
          _c(480, 'power_thunk', -3, 're-hook 2: the power dies mid-render (sub_drop carries the sub)', hero=True, hp=80,
             params=dict(on=0)),
          _c(480, 'crt_off', -6, 'the monitor collapses (f480-f485)', params=dict(whine=0)),
          _c(480, 'sub_drop', -9, 're-hook weight', lp=120, sat=3.0)]
    C += [_c(481, 'fan_wind', -16, 'PC fans wind down', align='start', lp=1500,
             params=dict(mode='down', duration=1.5, rate=40.0, fc=700.0))]
    # HUD drains 64 -> 0 % over f486-f520, value = round(64 (1 - in_cubic(u))): one tick per 1/10 of the drain, so the
    # ticks accelerate with the in_cubic drain; the last one is the 0 % landing (f520).
    for k in range(1, 11):
        tk = F(486) + (F(520) - F(486)) * (k / 10.0) ** (1.0 / 3.0)
        C.append(_c(None, 'ui_tick', -16 if k < 10 else -13, 'HUD drains %d -> %d %%' % (round(64 * (1 - (k - 1) / 10)),
                                                                                       round(64 * (1 - k / 10))),
                    t=tk, hp=5500, pan=0.3, params=dict(pitch=round(1.0 - 0.015 * k, 3))))
    C += [dict(L[('L8', 'camera_shutter')], f=559.0, gain_db=-10.0, ev='L8 iris blades close (f551-f559)', ver='AB'),
          dict(L[('L8', 'ui_click')], f=561.0, gain_db=-14.0, ev='L8 iris opens on the keycaps', ver='AB'),
          dict(L[('L8', 'reverse_swell')], f=571.0, gain_db=-12.0, ev='L8 iris fully open (ends f571)', ver='AB')]
    for p in PRESSES:
        post = p >= 700                                # the presses after V8 ends (23.06 s): 4 dB under the rest so
        C += [_c(p - 1, 'keycap_thock', -14 if post else -10, 'Ctrl keycap down (leads S by 1 f)', pan=-0.3,  # the
                 params=dict(pitch=0.94)),                # rhythm does not jump when the VO duck releases
              _c(p, 'keycap_thock', -12 if post else -8, 'S keycap down (%s)' % ('quarter' if p < 640 else '8th'),
                 pan=0.25),
              _c(p + 2, 'ui_tick', -16, '"Saved" chip pops (x 780)', hp=5500, pan=0.3)]
    C += [_c(720, 'impact_soft', -10, 'cut to the candle macro (power off again)', lp=900),
          _c(800, 'impact_soft', -7, 'PAYOFF lockup lands (velvet hit, bar 10); starts on f800, after the drop-out',
             align='start', hero=True, sat=3.0),
          _c(800, 'heartbeat', -10, 'velvet hit (starts on f800)', align='start', params=dict(n=1)),
          _c(800, 'harmonium_swell', -6, 'the one desi voice: starts f800, peaks on "sabr" f820 (music_full.wav)',
             music=True, align='start', params=dict(duration=round(20 / 30 / 0.72, 6), notes=(50, 57, 62, 66),
                                                    seed=0)),
          _c(817, 'swish_small', -16, 'underline draws on (f817-f838)', align='start', hp=5500),
          _c(880, 'riser', -8, 'into the power return (starts f856, clear of V11)', params=dict(duration=0.8)),
          _c(880, 'power_thunk', 0, 'POWER RETURNS (loudest moment, bar 11; sub_drop carries the sub)', hero=True, hp=80,
             params=dict(on=1)),
          _c(880, 'sub_drop', -8, 'power return weight', lp=120, sat=3.0),
          dict(L[('L4', 'shimmer')], f=880.0, ev='L4 halation bloom-out peaks', ver='AB'),
          dict(L[('L4', 'reverse_swell')], f=880.0, ev='L4 bloom into the cut (ends f880)', ver='AB'),
          _c(881, 'impact_soft', -4, 'JD smiling in the lit room', sat=3.0),
          _c(881, 'fan_wind', -6, 'ceiling fan spins up 2.5 s (out_cubic), hands over to the room_mains bed',
             align='start', params=dict(mode='up', duration=2.5, hold=0.3, release=0.6)),
          _c(882, 'tube_light_on', -8, 'the tube light strikes', pan=-0.35, params=dict(tinks=0)),
          _c(883, 'crt_on', -8, 'CRT degauss behind his head'),
          _c(885, 'mohalla_cheer', -8, 'the neighbourhood cheers again (wordless)', params=dict(dur=1.6, cut=0))]
    for c in cc:                                       # the end card's own cues (EndCard.cues)
        c = dict(c, ver='AB')
        if c['name'] == 'swish_small':
            c.update(f=round(c['t'] * FPS, 2), ev='end card: JD monogram ring draws on')
        elif c['name'] == 'glass_tap':
            c.update(f=round(c['t'] * FPS, 2), ev='end card: monogram lands (glass tap tuned to D7)', seed=0,
                     params=dict(pitch=GLASS_PITCH))
        elif c['name'] == 'shimmer':
            c.update(f=round(c['t'] * FPS, 2), ev='end card: keyword "batao" rises')
        elif c['name'] == 'reverse_swell':             # 0.8 -> 0.5 s: starts after V12 ends (34.111 s VO activity)
            c.update(f=1040.0, ev='loop swell into frame 0 (ends on DUR)', params=dict(duration=0.5))
        C.append(c)
    for c in C:
        c.setdefault('hero', False)
    return C


# ============================================================================================ VO source + fit
def vo_source(hook='A'):
    if hook == 'A':
        return dict(words=os.path.join(VO_DIR, 'words.json'), wav=os.path.join(VO_DIR, 'vo_stem.wav'))
    return dict(words=os.path.join(VO_DIR, 'words_B.json'), wav=os.path.join(VO_DIR, 'vo_stem_B.wav'))


KEY_LP_UNDER_VO = 1800.0                       # keycaps under words: keep the thock, lose the 2-8 kHz click
TAIL_CARVE_DB, HERO_CARVE_DB, CARVE_BRIDGE, CARVE_RAMP = -6.0, -10.0, 1.0, 0.05


def _cue_span(c):
    x = A.sound(c['name'], **c['params'])
    rate = float(c.get('rate', 1.0))
    start = float(c['t']) - (x.hit / rate if c['align'] == 'hit' else 0.0)
    length = c['dur'] if c.get('dur') else len(x) / SR / rate
    return start, start + x.hit / rate, start + length


def cues(hook='A', report=False, include_music=False):
    """The rendered cue sheet: raw_cues -> fit_under_vo (bible 4.1: in VO windows -6 dB, MID -8, AIR hp 5500, DARK lp
    1100, spans -6 + lp 1100; HERO cues need 120 ms clear before and 300 ms after, else HeroOnWordError) -> keycaps under
    words lp 1800 (no clicks in 1-4 kHz under speech) -> tails carved TAIL_CARVE_DB (heroes HERO_CARVE_DB) under every
    speech window that starts after the hit."""
    register()
    src = vo_source(hook)
    raw = [c for c in raw_cues(hook) if include_music or not c.get('music')]
    out, rep = SJ.fit_under_vo(raw, src['words'], vo_audio=src['wav'], hero='raise', report=True)
    wins = rep['windows']
    rep['keycap_lp'], rep['carved'], rep['exempt'] = [], [], []
    raw_gain = {id(c0): float(c0['gain_db']) for c0 in raw}
    for c0, c in zip(raw, out):
        if c.get('vo_exempt') and c.get('vo'):
            # the 60 ms ducking pad caught a cue that sits in a real pause: restore it when its hit is >= 20 ms clear
            # of the UNPADDED speech (words + measured VO activity)
            hit = _cue_span(c)[1]
            if not any(a - 0.02 <= hit <= b + 0.02 for a, b in rep["hero_windows"]):
                c['gain_db'] = raw_gain[id(c0)]
                rep['exempt'].append(dict(name=c['name'], hit=round(hit, 3), was=c.pop('vo')))
    for c in out:
        if c.get('music'):
            continue
        start, hit, end = _cue_span(c)
        if c['name'] == 'keycap_thock' and any(a <= hit <= b for a, b in wins):
            c['lp'] = KEY_LP_UNDER_VO
            rep['keycap_lp'].append(round(hit, 3))
        later = []
        for a, b in wins:
            if a < hit + 0.05 or a >= end:
                continue
            if later and a - later[-1][1] < CARVE_BRIDGE:
                later[-1] = (later[-1][0], b)
            else:
                later.append((a, b))
        if later and end - hit > 0.3:
            d = HERO_CARVE_DB if c.get('hero') else TAIL_CARVE_DB
            c['carve'] = [(round(a, 4), round(b, 4), d) for a, b in later]
            rep['carved'].append(dict(name=c['name'], t=c['t'], windows=[(a, b) for a, b, _ in c['carve']], db=d))
    rep['vo'] = src
    return (out, rep) if report else out


# ============================================================================================ beds (BRIEF 6.10 bed table)
L_DROP = -44.0                                 # drop-out room tone (tuned so the rough mix holds RMS ~ -46.5 dBFS)


def _seg(t0, t1, lv, fin=0.004, fout=0.004):
    """Keys for one constant-level segment (lv = BED_GAIN_DB-style dB re the stem target: integrated loudness of the
    bed alone = target + lv + 8) with linear ramps of fin / fout seconds centred on t0 / t1."""
    return _steps([(t0, lv)], t1, fin, fout)


def _steps(points, t_end, fade=0.004, fout=None):
    """Keys for consecutive levels [(t, lv), ...] up to t_end (None = silent); every switch is a linear ramp of
    `fade` s centred on its time (`fout` for the final one), none at 0 or DUR (the loop runs through them)."""
    fout = fade if fout is None else fout
    k = []
    for i, (t, lv) in enumerate(points):
        t1 = points[i + 1][0] if i + 1 < len(points) else t_end
        if not k:
            k += [(0.0, lv)] if t <= 0 else [(t - fade / 2, None), (t + fade / 2, lv)]
        else:
            k.append((t + fade / 2, lv))
        last = i + 1 == len(points)
        k.append((DUR if t1 >= DUR else t1 - (fout if last else fade) / 2, lv))
    if t_end < DUR:
        k.append((t_end + fout / 2, None))
    return k


def beds(hook='A'):
    """Bed automation [dict(name, ref, keys, why)]: amplitude keys interpolated linearly, loop position = (t - ref)."""
    out = []
    if hook == 'A':
        # brownout factors f10-f13 = 0.45, 0.80, 0.35, 0.15 on the mains layers -> -24 + 20 log10(factor)
        lv = [-24.0] + [round(-24.0 + 20 * math.log10(fct), 1) for fct in (0.45, 0.80, 0.35, 0.15)]
        out.append(dict(name='room_mains', ref=0.0,
                        keys=_steps([(0.0, lv[0]), (F(10), lv[1]), (F(11), lv[2]), (F(12), lv[3]), (F(13), lv[4])],
                                    F(14)),
                        why='lit room f0-f13, brownout f10-f13 follows the picture factors, dead at f14'))
        crick = [(0.0, -38.0), (F(14), -32.0)]
    else:
        out.append(dict(name='room_tone', ref=0.0, keys=_steps([(0.0, -34.0)], F(80)),
                        why='hook B: torch-lit dead room'))
        crick = [(0.0, -32.0)]
    crick += [(F(80), -32.0), (F(160), -24.0), (F(320), -32.0), (F(400), None), (F(720), -32.0), (DROP[0], None),
              (DROP[1], -34.0), (F(880), -38.0)]
    out.append(dict(name='night_crickets', ref=0.0, keys=_steps(crick, DUR),
                    why='power cuts and rooftops; silent while the desk is lit (f400-f719) and in the drop-out'))
    out += [dict(name='room_tone', ref=0.0, keys=_seg(F(80), F(160), -34.0, 0.004, 0.05) + [], why='candle (S2)'),
            dict(name='night_air', ref=0.0, keys=_seg(F(160), F(320), -30.0, 0.05, 0.1), why='rooftops (S3)'),
            dict(name='room_tone', ref=0.0, keys=_seg(F(320), F(400), -34.0, 0.1, 0.004), why='old room by torch (S4)'),
            dict(name='edit_suite', ref=0.0, keys=_seg(F(400), F(480), -28.0), why='modern desk, power on (S5)'),
            dict(name='room_tone', ref=0.0, keys=_seg(F(480), F(560), -36.0), why='dead desk (re-hook 2)'),
            dict(name='edit_suite', ref=0.0, keys=_seg(F(560), F(720), -30.0, 0.05, 0.004), why='keycaps, power on'),
            dict(name='room_tone', ref=0.0,
                 keys=_steps([(F(720), -32.0), (DROP[0], L_DROP), (DROP[1], -32.0)], F(880)),
                 why='candle (S7); the drop-out holds only this room tone (held breath)'),
            dict(name='room_mains', ref=DUR,
                 keys=[(F(882) - 0.002, None), (F(882) + 0.002, -36.0), (F(881) + 2.5, -24.0), (DUR, -24.0)],
                 why='the lit room again: tube strike f882, fan reaches speed at f881 + 2.5 s; loop phase locked '
                     'to frame 0 (ref = DUR)')]
    return out          # hook B: f0 has crickets + room tone, no mains: its seam is the brief's deliberate hard cut


def _bed_bus(bed_list, target=TARGET_LUFS):
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    info = []
    for b in bed_list:
        loop = np.asarray(A.sound(b['name']), dtype=np.float64)
        ks = sorted(b['keys'], key=lambda k: k[0])
        tk = np.array([k[0] for k in ks])
        ak = np.array([0.0 if k[1] is None else float(undb(target + k[1] + A.BED_ANCHOR_DB - A.REF_LUFS)) for k in ks])
        i0, i1 = _n(max(0.0, tk[0])), min(N, _n(tk[-1]) + 1)
        g = np.interp(t[i0:i1], tk, ak)
        pos = (np.arange(i0, i1) - _n(b['ref'])) % len(loop)
        out[i0:i1] += loop[pos] * g[:, None]
        info.append(dict(name=b['name'], t0=round(float(tk[0]), 4), t1=round(float(tk[-1]), 4),
                         levels=sorted({k[1] for k in ks if k[1] is not None}), why=b.get('why', '')))
    return out, info


# ============================================================================================ circular mixer
def _circ(fn, x, pad=1.0):
    """Apply fn to x as a loop (pad both ends with the other end, process, crop)."""
    p = _n(pad)
    y = fn(np.concatenate([x[-p:], x, x[:p]], axis=0))
    return y[p:p + len(x)]


def _fold(buf, pre, n):
    out = np.zeros((n,) + buf.shape[1:])
    np.add.at(out, (np.arange(len(buf)) - pre) % n, buf)
    return out


def _timing(y, start, hit_abs, hop=96):
    """Isolated timing of one rendered cue (reel time): onset (first 2 ms bin within 20 dB of its peak bin), peak
    (loudest 30 ms window), end (last bin within 40 dB of the peak bin), level of the 30 ms window at the designed hit."""
    m = np.square(np.asarray(y, dtype=np.float64)).mean(1)
    nb = len(m) // hop
    p2 = m[:nb * hop].reshape(nb, hop).mean(1)
    e = 10 * np.log10(p2 + 1e-20)
    pk = float(e.max())
    on = int(np.argmax(e >= pk - 20.0))
    end = int(np.nonzero(e >= pk - 40.0)[0][-1]) + 1
    sm = np.convolve(p2, np.ones(15) / 15, 'same')
    k = int(np.clip(round((hit_abs - start) * SR / hop - 0.5), 0, len(sm) - 1))
    return dict(onset_abs=round(start + on * hop / SR, 4), peak_abs=round(start + (int(np.argmax(sm)) + 0.5) * hop / SR, 4),
                end_abs=round(start + end * hop / SR, 4),
                at_hit_db=round(float(10 * np.log10(sm[k] + 1e-20) - 10 * np.log10(sm.max() + 1e-20)), 2))


def _carve_gain(L, start, carve, ramp=CARVE_RAMP):
    t = start + np.arange(L) / SR
    g = np.zeros(L)
    for a, b, d in carve:
        up = np.clip((t - (a - ramp)) / ramp, 0, 1)
        dn = np.clip(((b + ramp) - t) / ramp, 0, 1)
        g = np.minimum(g, d * (0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn))))
    return undb(g)


def mix_loop(cue_list, bed_list, out_base=None, target=TARGET_LUFS, tp_ceiling=TP_CEILING, verbose=True):
    """audio.mix's chain on a loop (see the module docstring). Writes <out_base>.wav (the stem) and _fx / _bed splits
    (they sum to it). Returns a report (audio.mix keys + fx / bedbus arrays + per-cue timing)."""
    PRE, POST = _n(1.0), _n(10.0)
    cs = A.duck_under([A._norm_cue(c) for c in cue_list])
    L = PRE + N + POST
    bus = {k: np.zeros((L, 2)) for k in ('pre', 'post')}
    send = {k: np.zeros((L, 2)) for k in ('pre', 'post')}
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        y, hit = A._render_cue(c, counts[k] % 4)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        i = PRE + _n(start)
        assert 0 <= i and i + len(y) <= L, (c['name'], start)
        if c.get('sat'):                               # loudness-matched alias-safe saturation: same momentary
            z = _soft(y, float(c['sat']))              # loudness, lower crest (the limiter keeps the transient)
            y = z * undb(A.momentary_max(y) - A.momentary_max(z))
        tm = _timing(y, start, start + hit)
        if c.get('carve'):
            y = y * _carve_gain(len(y), start, c['carve'])[:, None]
        b = 'post' if start >= DROP[0] - 1e-6 else 'pre'
        bus[b][i:i + len(y)] += y
        meta = A.SOUNDS[c['name']]
        sdb = c.get('send_db', meta['send'] if meta['send'] is not None else A._CAT_SEND[meta['category']])
        if sdb is not None and sdb > -60:
            send[b][i:i + len(y)] += y * undb(sdb)
        placed.append(dict(t=float(c['t']), f=c.get('f'), name=c['name'], start=round(start, 4),
                           hit=round(start + hit, 4), len=round(len(y) / SR, 3), gain_db=round(float(c['gain_db']), 2),
                           duck_db=c.get('duck_db', 0.0), align=c['align'], params=c['params'], lp=c.get('lp'),
                           hp=c.get('hp'), pan=c.get('pan', 0.0), hero=bool(c.get('hero')), vo=c.get('vo', ''),
                           ev=c.get('ev', ''), ver=c.get('ver', ''), carve=c.get('carve'), bus=b, sat=c.get('sat'),
                           warn='tail wraps to t=0' if start + len(y) / SR > DUR else '', **tm))
    for b in bus:
        wet = A.reverb(send[b], 'studio', wet_db=0.0, dry=0.0)
        bus[b] += wet[:L]
        if len(wet) > L and np.max(np.abs(wet[L:])) > 1e-7:
            raise RuntimeError('room tail beyond the post-roll')
    # the drop-out: everything that started before it fades to 0 over the 30 ms before 26.333 s and stays silent
    tt = (np.arange(L) - PRE) / SR
    gate = np.clip((DROP[0] - tt) / 0.03, 0, 1)
    bus['pre'] *= (0.5 - 0.5 * np.cos(np.pi * gate))[:, None]
    fx = _fold(bus['pre'] + bus['post'], PRE, N)
    fx *= undb(target - A.loudness(fx))
    gr_comp = _circ(lambda z: A.compressor_gain(z, thresh_db=target + 8.0, ratio=2.0), fx)
    fx *= undb(gr_comp)[:, None]
    bed, bed_info = _bed_bus(bed_list, target)
    bed = _circ(lambda z: A.sidechain(z[:, :2], z[:, 2:], depth_db=5.0), np.concatenate([bed, fx], 1))
    pk_fx, pk_bed = _circ(A.tp_envelope, fx), _circ(A.tp_envelope, bed)
    G, ceil, best = 0.0, tp_ceiling - 0.2, None
    for attempt in range(4):
        best = None
        for it in range(40):
            gl = _circ(lambda z: A.limiter_gain(None, ceil, pk=z), pk_fx * undb(G) + pk_bed)
            y = (fx * undb(G) + bed) * gl[:, None]
            L1 = A.loudness(y)
            if best is None or abs(L1 - target) < abs(best[2] - target):
                best = (G, gl, L1, y)
            if abs(L1 - target) < 0.02:
                break
            G += float(np.clip(target - L1, -12, 12)) * 0.9
        G, gl, L1, y = best
        tp = A.true_peak(np.concatenate([y[-_n(0.05):], y, y[:_n(0.05)]]))
        if tp <= tp_ceiling - 0.05:
            break
        ceil -= tp - (tp_ceiling - 0.1)
    fx_out, bed_out = fx * (undb(G) * gl)[:, None], bed * gl[:, None]
    master = fx_out + bed_out
    tpc = A.true_peak(np.concatenate([master[-_n(0.05):], master, master[:_n(0.05)]]))
    rep = dict(dur=DUR, cues=len(cs), integrated_lufs=round(A.loudness(master), 2), true_peak_dbtp=round(tpc, 2),
               sample_peak_dbfs=round(float(db(np.max(np.abs(master)))), 2), lra_lu=round(A.loudness_range(master), 2),
               max_momentary_lufs=round(A.momentary_max(master), 2),
               max_short_term_lufs=round(A.momentary_max(master, 3.0), 2),
               limiter_max_gr_db=round(max(0.0, float(-db(np.min(gl)))), 2),
               limiter_max_gr_at=round(float(np.argmin(gl)) / SR, 3),
               limiter_pct_over_1db=round(100.0 * float(np.mean(gl < undb(-1.0))), 2),
               comp_max_gr_db=round(float(-np.min(gr_comp)), 2), fx_gain_db=round(G, 2), bed=bed_info,
               bed_lufs=round(A.loudness(bed_out), 2), fx_lufs=round(A.loudness(fx_out), 2), placed=placed, files={})
    if out_base:
        rep['files']['stem'] = A._write_wav(out_base + '.wav', master, 24)
        rep['files']['stem_fx'] = A._write_wav(out_base + '_fx.wav', fx_out, 24)
        rep['files']['stem_bed'] = A._write_wav(out_base + '_bed.wav', bed_out, 24)
    rep['audio'], rep['fx'], rep['bedbus'] = master.astype(np.float32), fx_out.astype(np.float32), bed_out.astype(np.float32)
    rep['gl'] = gl.astype(np.float32)
    if verbose:
        print('SFX loop mix %.3f s %d cues | I %.2f LUFS | TP %.2f dBTP (circular) | LRA %.1f | Mmax %.1f | limiter GR %.2f dB'
              ' @ %.3f s | glue GR %.2f dB | bed %.1f LUFS' % (DUR, rep['cues'], rep['integrated_lufs'], rep['true_peak_dbtp'],
                                                              rep['lra_lu'], rep['max_momentary_lufs'],
                                                              rep['limiter_max_gr_db'], rep['limiter_max_gr_at'],
                                                              rep['comp_max_gr_db'], rep['bed_lufs']))
    return rep


# ============================================================================================ measurement helpers
def _ebur128(path):
    import re
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))  # noqa: E731
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def _rms_db(x):
    return round(float(db(np.sqrt(np.mean(np.square(np.asarray(x, dtype=np.float64))) + 1e-30))), 2)


def _lufs_seg(x):
    """Ungated K-weighted loudness of a short segment (LUFS)."""
    k = A.kweight(np.asarray(x, dtype=np.float64))
    return round(float(-0.691 + 10 * np.log10(np.mean(np.square(k).sum(1)) + 1e-30)), 1)


def onsets(placed, music_events=()):
    """Measured perceptual onset of each sound: the first 2 ms bin of its isolated render within 20 dB of its own
    peak bin (mix_loop's `onset_abs`), so a quiet pre-roll (crt_off's whine, a riser's start) does not count but a
    transient does. Returns [(t, name)] sorted, incl. music events."""
    ev = [(p['onset_abs'], p['name']) for p in placed]
    ev += [(float(t), 'music:' + n) for t, n in music_events]
    return sorted(ev)


def starts_per_frame(placed, music_events=()):
    """'Sounds on one instant' = sounds whose perceptual onset falls in the same 30 fps frame. Also reports the sliding
    count of onsets within 25 ms of each other (fused attacks). Returns (max per frame, frames with 3+, max fused)."""
    ev = onsets(placed, music_events)
    per = {}
    for t, n in ev:
        per.setdefault(int(math.floor(round(t * FPS, 3))), []).append(n)
    worst = max(len(v) for v in per.values())
    busy = sorted((f, v) for f, v in per.items() if len(v) >= 3)
    fused = max(sum(1 for t2, _ in ev if abs(t2 - t) <= 0.025) for t, _ in ev)
    return worst, busy, fused


def _music_events():
    try:
        d = json.load(open(MUSIC_JSON))
    except Exception:
        return []
    return [(float(e['t']), 'harmonium start') for e in d.get('events', []) if 'starts' in str(e.get('what', ''))]


def overview(x, placed, path, title, words=None, extra=None):
    """PNG: spectrogram + loudness strip with bar lines, power state, VO words, the drop-out and cue ticks."""
    from PIL import Image, ImageDraw
    w = 1800
    im = A.spectro_image(A.Sfx(np.asarray(x, dtype=np.float32), 0, 'mix'), w, 420, None, title, extra or '')
    H = 170
    strip = Image.new('RGB', (w, H), (14, 10, 18))
    dr = ImageDraw.Draw(strip)
    X = lambda t: int(t / DUR * w)  # noqa: E731
    for f0, f1, on in POWER:
        dr.rectangle([X(F(f0)), 0, X(F(f1)) - 1, 7], fill=(255, 150, 40) if on else (40, 30, 60))
    dr.rectangle([X(DROP[0]), 0, X(DROP[1]), H], fill=(25, 40, 80))
    if words:
        for wd in words:
            dr.rectangle([X(wd[0]), 10, X(wd[1]), 18], fill=(230, 220, 210))
    for bar in range(14):
        dr.line([(X(bar * 80 / FPS), 0), (X(bar * 80 / FPS), H)], fill=(70, 60, 90))
        dr.text((X(bar * 80 / FPS) + 2, H - 12), str(bar), fill=(120, 110, 140))
    tt, lc = A.loudness_curve(np.asarray(x, dtype=np.float64))
    yv = lambda v: int(np.interp(v, [-60, -6], [H - 14, 24]))  # noqa: E731
    for lv in (-18, -30, -45):
        dr.line([(0, yv(lv)), (w, yv(lv))], fill=(60, 60, 80))
        dr.text((4, yv(lv) - 11), '%d' % lv, fill=(110, 110, 130))
    dr.line([(X(a), yv(b)) for a, b in zip(tt, lc)], fill=(255, 150, 80), width=2)
    for p in placed:
        col = (255, 60, 60) if p.get('hero') else (255, 120, 190)
        dr.line([(X(p['hit']), 20), (X(p['hit']), 30)], fill=col, width=2 if p.get('hero') else 1)
    out = Image.new('RGB', (w, 420 + H), (6, 4, 8))
    out.paste(im, (0, 0))
    out.paste(strip, (0, 420))
    out.save(path)
    return path


# ============================================================================================ build (SFX stem)
def _paths(hook):
    return os.path.join(AUD, '%s_sfx_%s' % (MODULE, hook))


def build(hook='A'):
    register()
    os.makedirs(AUD, exist_ok=True)
    base = _paths(hook)
    cl, frep = cues(hook, report=True)
    rep = mix_loop(cl, beds(hook), out_base=base)
    x = np.asarray(rep['audio'], dtype=np.float64)
    fx = np.asarray(rep['fx'], dtype=np.float64)
    bo = np.asarray(rep['bedbus'], dtype=np.float64)
    words = [(w['start'], w['end']) for w in json.load(open(frep['vo']['words']))]
    timing = []
    for p in rep['placed']:
        if p['name'] in SJ.SPAN or p['name'] == 'reverse_swell':
            kind, at, ref, tol = 'end', p['end_abs'], p['hit'], 1.0 / FPS
        elif p['align'] == 'start':
            kind, at, ref, tol = 'start', p['start'], p['t'], 1e-4
        elif p['hit'] - p['start'] < 0.05:
            kind, at, ref, tol = 'onset', p['onset_abs'], p['t'], 1.0 / FPS
        else:
            kind, at, ref, tol = 'peak', p['peak_abs'], p['hit'], 0.06
        off = at - ref
        ok = abs(off) <= tol + 1e-6 or (kind == 'peak' and p['at_hit_db'] >= -1.5)
        timing.append(dict(name=p['name'], t=p['t'], f=p['f'], kind=kind, ref=round(ref, 4), at=at,
                           off_ms=round(off * 1000, 1), off_frames=round(off * FPS, 2),
                           at_hit_db=p['at_hit_db'] if kind == 'peak' else None, flag='' if ok else 'CHECK'))
    a, b = _n(DROP[0]), _n(DROP[1])
    music_ev = _music_events()
    worst, busy, fused = starts_per_frame(rep['placed'], music_ev)
    hook_end = [dict(name=p['name'], end_40db=p['end_abs'], buffer_end=round(p['start'] + p['len'], 3))
                for p in rep['placed'] if p['ver'] in ('A', 'B')]
    in_drop = [p['name'] for p in rep['placed'] if DROP[0] - 1e-6 <= p['start'] < DROP[1] - 1e-6]
    seam = dict(last50_rms_db=_rms_db(x[-_n(0.05):]), first50_rms_db=_rms_db(x[:_n(0.05)]),
                step=round(float(np.abs(x[0] - x[-1]).max()), 6),
                median_step=round(float(np.median(np.abs(np.diff(x[-_n(0.05):], axis=0)).max(1))), 6))
    secs = [(0.05, 0.33), (0.6, 2.6), (2.75, 5.3), (5.4, 7.9), (8.1, 9.9), (10.1, 10.6), (10.7, 13.3), (13.4, 15.9),
            (16.5, 18.6), (18.7, 23.9), (24.1, 26.3), DROP, (26.7, 29.3), (29.4, 30.6), (32.0, 34.6)]
    meas = dict(
        hook=hook, vo=frep['vo'], hero_source=frep['hero_source'], heroes_ok=frep['heroes_ok'],
        violations=frep['violations'], ducked=frep['ducked'], spans=frep['spans'], keycap_lp=frep['keycap_lp'],
        carved=frep['carved'],
        stem=dict((k, rep[k]) for k in ('integrated_lufs', 'true_peak_dbtp', 'sample_peak_dbfs', 'lra_lu',
                                        'max_momentary_lufs', 'max_short_term_lufs', 'limiter_max_gr_db',
                                        'limiter_max_gr_at', 'limiter_pct_over_1db', 'comp_max_gr_db', 'bed_lufs',
                                        'fx_lufs', 'fx_gain_db')),
        ffmpeg=_ebur128(base + '.wav'),
        dropout=dict(fx_peak_dbfs=round(float(db(np.abs(fx[a:b]).max() + 1e-15)), 1), stem_rms_dbfs=_rms_db(x[a:b]),
                     stem_lufs=_lufs_seg(x[a:b]), starts_inside=in_drop),
        seam=seam, timing=timing, starts_per_frame=dict(max=worst, frames_3plus=busy, fused_25ms_max=fused),
        hook_only_cue_ends=hook_end, bed=rep['bed'],
        sections_lufs=[(round(s0, 3), round(s1, 3), _lufs_seg(x[_n(s0):_n(s1)]), _lufs_seg(bo[_n(s0):_n(s1)]))
                       for s0, s1 in secs])
    tt, lc = A.loudness_curve(x)
    meas['max_momentary_at'] = round(float(tt[np.argmax(lc)]), 3)
    overview(x, rep['placed'], base + '_overview.png', '%s SFX stem, hook %s (VO-fitted, loop-mixed)' % (MODULE, hook),
             words, 'I %.2f LUFS  TP %.2f dBTP  LRA %.1f  limiter GR %.2f dB   [amber = power on, white = VO words, blue = '
             'drop-out, red ticks = hero hits]' % (rep['integrated_lufs'], rep['true_peak_dbtp'], rep['lra_lu'],
                                                    rep['limiter_max_gr_db']))
    cj = dict(module=MODULE, hook=hook, dur=DUR, bpm=BPM, fps=FPS, vo=frep['vo'],
              cues=[dict((k, v) for k, v in p.items()) for p in rep['placed']])
    json.dump(cj, open(base + '_cues.json', 'w'), indent=1, default=str)
    json.dump(meas, open(base + '_report.json', 'w'), indent=1, default=str)
    show = ('stem', 'ffmpeg', 'max_momentary_at', 'dropout', 'seam', 'starts_per_frame', 'violations', 'keycap_lp',
            'sections_lufs')
    print(json.dumps(dict((k, meas[k]) for k in show), indent=1, default=str))
    for o in timing:
        if o['flag']:
            print('%5s %-15s t %7.3f (f%7.2f) %-5s ref %7.3f at %7.3f %+6.1f ms (%+.2f f)%s' % (
                o['flag'], o['name'], o['t'], o['f'] or 0, o['kind'], o['ref'], o['at'], o['off_ms'], o['off_frames'],
                '' if o['at_hit_db'] is None else '  level at the designed hit %.2f dB re peak' % o['at_hit_db']))
    print('timing CHECK flags:', sum(1 for o in timing if o['flag']), 'of', len(timing))
    print('hook-only cue ends (must be < %.3f):' % F(80), hook_end)
    return rep, meas


# ============================================================================================ rough mix (VO + SFX + harmonium)
def _mono_to_st(x):
    x = np.asarray(x, dtype=np.float64)
    return np.repeat(x, 2, axis=1) if x.ndim == 2 and x.shape[1] == 1 else _st(x)


def _load_fix(path):
    x, sr = A.read_wav(path)
    assert sr == SR, (path, sr)
    x = _mono_to_st(x)
    assert len(x) == N, (path, len(x), N)
    return x


def _master(bus, target=FINAL_LUFS, ceiling=LIMIT_CEIL, tp_max=FINAL_TP):
    """epic_mix.master on a loop: 2:1 glue from the 98th-percentile 10 ms level - 3 dB, then gain + 4x true-peak
    limiter to target LUFS, TP <= tp_max (circular)."""
    import epic_mix as M
    gr = _circ(lambda z: A.compressor_gain(z, thresh_db=M._level_pct(bus, 98) - 3.0, ratio=2.0, knee_db=6.0,
                                           attack=0.006, release=0.15, rms=0.008), bus)
    bus = bus * undb(gr)[:, None]
    pk = _circ(A.tp_envelope, bus)
    g, c = target - A.loudness(bus), ceiling
    for attempt in range(4):
        for _ in range(20):
            gl = _circ(lambda z: A.limiter_gain(None, c, pk=z), pk * undb(g))
            y = bus * undb(g) * gl[:, None]
            L1 = A.loudness(y)
            if abs(L1 - target) < 0.03:
                break
            g += target - L1
        tp = A.true_peak(np.concatenate([y[-_n(0.05):], y, y[:_n(0.05)]]))
        if tp <= tp_max - 0.05:
            break
        c -= tp - (tp_max - 0.1)
    return y, g, gl, float(-gr.min())


HARM_V11_MARGIN = 8.5                          # speech >= 8 LU over (harmonium + SFX) on V11's voiced frames, + 0.5


def rough(hook='A'):
    """Rough mixes: FULL = VO stem + SFX stem (VO-sidechained -4 dB, epic_mix SPEC) + music_full.wav (the harmonium,
    one static gain, no VO duck: it peaks on "sabr"); DRY = VO + SFX. Mastered on a loop to -14 LUFS, TP <= -2.0."""
    import epic_mix as M
    register()
    src = vo_source(hook)
    v = _load_fix(src['wav'])
    s = _load_fix(_paths(hook) + '.wav')
    s = s * undb(TARGET_LUFS - A.loudness(s))
    s = _circ(lambda z: A.sidechain(z[:, :2], z[:, 2:], depth_db=M.SPEC['sfx_duck_vo_db'], attack=0.03, release=0.3),
              np.concatenate([s, v], 1))
    have_music = os.path.exists(MUSIC)
    m0 = _load_fix(MUSIC) if have_music else np.zeros((N, 2))
    words = json.load(open(src['words']))
    v11 = [w for w in words if w.get('line') == 'V11']
    acts = SJ.vo_activity(src['wav'])
    tt, lv = A.loudness_curve(v)
    _, ls = A.loudness_curve(s)
    sp = M.speech_mask(v)
    idx = np.clip((tt * SR).astype(int), 0, N - 1)
    spk = sp[idx] & (lv > lv.max() - 15)
    g_h = None
    if have_music and v11:
        a0, b0 = v11[0]['start'], max(b for a, b in acts if a < v11[-1]['end'] + 0.2)
        sel = spk & (tt >= a0) & (tt <= b0)
        for gdb in np.arange(0.0, -30.01, -0.25):     # loudest static gain that keeps V11 >= margin over the bed
            _, lb = A.loudness_curve(s + m0 * undb(gdb))
            if np.median((lv - lb)[sel]) >= HARM_V11_MARGIN:
                g_h = float(gdb)
                break
    out = {}
    versions = [('full', True), ('dry', False)] if hook == 'A' else [('full', True)]
    for tag, full in versions:
        m = m0 * undb(g_h) if (full and g_h is not None) else np.zeros((N, 2))
        y, g, gl, glue_gr = _master(v + s + m)
        name = '%s_rough_%s_%s' % (MODULE, hook, tag)
        path = os.path.join(AUD, name + '.wav')
        A._write_wav(path, y, 24)
        k = undb(g) * gl[:, None]
        vv, ss, mm = v * k, s * k, m * k
        _, lvv = A.loudness_curve(vv)
        _, lss = A.loudness_curve(ss)
        _, lbb = A.loudness_curve(ss + mm)
        _, lmm = A.loudness_curve(mm) if np.any(mm) else (None, np.full_like(lvv, -120.0))
        ty, ly = A.loudness_curve(y)
        per_line = {}
        for ln in sorted({w['line'] for w in words}, key=lambda q: [w['line'] for w in words].index(q)):
            ws = [w for w in words if w['line'] == ln]
            a0, b0 = ws[0]['start'], ws[-1]['end']
            sel = spk & (tt >= a0) & (tt <= b0)
            if sel.any():
                per_line[ln] = dict(t=(round(a0, 2), round(b0, 2)),
                                    vo_over_bed_med=round(float(np.median((lvv - lbb)[sel])), 1),
                                    vo_over_sfx_med=round(float(np.median((lvv - lss)[sel])), 1),
                                    vo_over_sfx_p10=round(float(np.percentile((lvv - lss)[sel], 10)), 1))
        kmax = int(np.argmax(ly))
        a, b = _n(F(791)), _n(F(799))
        pk_t = None
        if np.any(mm):
            env = np.sqrt(uniform_filter1d(np.square(mm).mean(1), _n(0.01)))
            pk_t = round(float(np.argmax(env)) / SR, 4)
        rep = dict(file=path, hook=hook, version=tag, vo=src, harmonium_gain_db=g_h if (full and g_h is not None) else None,
                   lufs=round(A.loudness(y), 2), tp_dbtp=round(A.true_peak(np.concatenate([y[-_n(0.05):], y,
                                                                                            y[:_n(0.05)]])), 2),
                   lra=round(A.loudness_range(y), 1), master_gain_db=round(g, 2), glue_gr_db=round(glue_gr, 2),
                   limiter_max_gr_db=round(float(-db(gl.min())), 2), limiter_max_gr_at=round(float(np.argmin(gl)) / SR, 3),
                   ffmpeg=_ebur128(path),
                   vo_lufs_in_mix=round(A.loudness(vv), 2), sfx_lufs_in_mix=round(A.loudness(ss), 2),
                   music_lufs_in_mix=round(A.loudness(mm), 2) if np.any(mm) else None,
                   vo_over_bed_med_lu=round(float(np.median((lvv - lbb)[spk])), 1),
                   vo_over_bed_p10_lu=round(float(np.percentile((lvv - lbb)[spk], 10)), 1),
                   vo_over_music_med_lu=round(float(np.median((lvv - lmm)[spk])), 1) if np.any(mm) else None,
                   vo_over_sfx_p10_lu=round(float(np.percentile((lvv - lss)[spk], 10)), 1),
                   per_line=per_line,
                   max_momentary=dict(lufs=round(float(ly[kmax]), 2), centre=round(float(ty[kmax]), 3),
                                      frame=round(float(ty[kmax]) * FPS, 1)),
                   dropout=dict(window='f791-f798', rms_dbfs=_rms_db(y[a:b]), lufs=_lufs_seg(y[a:b]),
                                music_peak_dbfs=round(float(db(np.abs(mm[a:b]).max() + 1e-15)), 1)),
                   harmonium_peak_t=pk_t, harmonium_peak_frame=None if pk_t is None else round(pk_t * FPS, 2),
                   seam=dict(last50_rms_db=_rms_db(y[-_n(0.05):]), first50_rms_db=_rms_db(y[:_n(0.05)]),
                             step=round(float(np.abs(y[0] - y[-1]).max()), 6)))
        json.dump(rep, open(os.path.join(AUD, name + '.json'), 'w'), indent=1, default=str)
        overview(y, json.load(open(_paths(hook) + '_cues.json'))['cues'], os.path.join(AUD, name + '.png'),
                 '%s rough mix hook %s %s (VO + SFX%s)' % (MODULE, hook, tag.upper(), ' + harmonium' if full else ''),
                 [(w['start'], w['end']) for w in words],
                 'I %.2f LUFS  TP %.2f dBTP  LRA %.1f  VO over bed %.1f LU (median)' % (
                     rep['lufs'], rep['tp_dbtp'], rep['lra'], rep['vo_over_bed_med_lu']))
        print(json.dumps(dict((k2, rep[k2]) for k2 in rep if k2 not in ('per_line',)), indent=1, default=str))
        print(' per line:', json.dumps(per_line))
        out[tag] = rep
    return out


# ============================================================================================ audition + verify
AUDITION_SET = [('backup_beep', {}), ('backup_beep', dict(far=1)), ('match_strike', {}), ('relay_click', {}),
                ('power_thunk', dict(on=1)), ('power_thunk', dict(on=0)), ('crt_off', {}), ('crt_off', dict(whine=0)),
                ('crt_on', {}), ('tube_light_on', {}), ('tube_light_on', dict(tinks=0)), ('tube_flicker', {}),
                ('tube_flicker', dict(n=2)), ('fan_wind', dict(mode='down', duration=round(F(80) - F(14), 4), tau=1.0)),
                ('fan_wind', dict(mode='up', duration=2.5, hold=0.3, release=0.6)),
                ('fan_wind', dict(mode='down', duration=1.5, rate=40.0, fc=700.0)), ('keycap_thock', {}),
                ('keycap_thock', dict(pitch=0.94)), ('pankhi_swing', {}), ('mohalla_cheer', dict(dur=round(F(300) - F(241), 4), cut=1)),
                ('mohalla_cheer', dict(dur=1.6, cut=0)), ('room_mains', {}), ('night_crickets', {})]


def audition():
    register()
    os.makedirs(AUDITION, exist_ok=True)
    rows = []
    for name, prm in AUDITION_SET:
        x = A.sound(name, **prm)
        y = np.asarray(x, dtype=np.float64)
        tag = name + ''.join('_%s%s' % (k, v) for k, v in prm.items())
        bed = A.SOUNDS[name]['category'] == 'bed'
        if bed and len(y) > _n(12):
            y_img = y[:_n(12)]
        else:
            y_img = y
        A._write_wav(os.path.join(AUDITION, tag + '.wav'), y, 24)
        A.spectro_image(A.Sfx(y_img.astype(np.float32), x.hit, name), 1000, 420, x.hit, tag,
                        'hit %.3f s' % x.hit).save(os.path.join(AUDITION, tag + '.png'))
        m = SJ.measure(y, x.hit, bed=bed)
        q = A.qc(y.astype(np.float32), x.hit)
        if bed:
            q = [p for p in q if 'edge' not in p]
        rows.append(dict(name=tag, hit=round(x.hit, 4), dur=m['dur'], mmax=m['mmax_lufs'], i=m['i_lufs'],
                         tp=m['tp_dbtp'], centroid=m['centroid_hz'], sub=m['sub_pct'], low=m['low_pct'],
                         lowmid=m['lowmid_pct'], mid_1_4k=m['mid_pct'], high=m['high_pct'], mono_db=m['mono_db'],
                         seam=m.get('seam_ratio'), qc=q, sj=[p for p in m['problems'] if p not in q]))
        print('%-46s hit %.3f dur %5.2f Mmax %6.1f TP %6.2f 1-4k %5.1f%% sub %4.1f%% mono %5.2f %s %s %s' % (
            tag, x.hit, m['dur'], m['mmax_lufs'], m['tp_dbtp'], m['mid_pct'], m['sub_pct'], m['mono_db'],
            '' if m.get('seam_ratio') is None else 'seam %.2f' % m['seam_ratio'], 'qc OK' if not q else q,
            [p for p in m['problems'] if p not in q] or ''))
    json.dump(rows, open(os.path.join(AUDITION, 'qc.json'), 'w'), indent=1, default=str)
    return rows


def _whisper(x, model, lang):
    from faster_whisper import WhisperModel
    au = signal.resample_poly(np.asarray(x, dtype=np.float64).mean(1) if np.ndim(x) == 2 else x, 1, 3).astype(np.float32)
    wm = _whisper.cache.get(model) or WhisperModel(model, device='cpu', compute_type='int8', cpu_threads=2)
    _whisper.cache[model] = wm
    segs, info = wm.transcribe(au, language=lang, word_timestamps=True, vad_filter=False, beam_size=5)
    return [dict(w=w.word.strip(), s=round(w.start, 2), e=round(w.end, 2), p=round(float(w.probability), 2))
            for s in segs for w in (s.words or [])], info.language


_whisper.cache = {}


def verify():
    """faster-whisper checks: (1) both cheer renders are wordless (no word with p >= 0.5, any language);
    (2) GATE minor 9: in rough A FULL, V1 "बिजली चली गई" is heard inside 0-1.3 s (small, hi), every word p >= 0.5."""
    register()
    res = dict(cheer=[], v1=None)
    for prm in (dict(dur=round(F(300) - F(241), 4), cut=1), dict(dur=1.6, cut=0)):
        x = np.asarray(A.sound('mohalla_cheer', **prm), dtype=np.float64)
        for model in ('small', 'medium'):
            for lang in (None, 'hi', 'en'):
                ws, lg = _whisper(x, model, lang)
                bad = [w for w in ws if w['p'] >= 0.5 and any(ch.isalpha() for ch in w['w'])]
                res['cheer'].append(dict(params=prm, model=model, lang=lang, detected=lg, words=ws, words_p50=bad))
                print('cheer %s %-6s %-4s -> %s, words p>=0.5: %s' % (prm, model, lang, lg, bad))
    p = os.path.join(AUD, '%s_rough_A_full.wav' % MODULE)
    if os.path.exists(p):
        y = _load_fix(p)[:_n(1.40)]
        out = {}
        for model in ('small', 'medium'):
            ws, lg = _whisper(y, model, 'hi')
            out[model] = ws
            print('V1 in rough A full (%s, hi):' % model, ws)
        res['v1'] = out
    json.dump(res, open(os.path.join(AUD, MODULE + '_verify.json'), 'w'), indent=1, ensure_ascii=False)
    return res


def print_cues(hook='A'):
    cl, rep = cues(hook, report=True)
    for c in sorted(cl, key=lambda c: c['t']):
        print('%7.3f f%7.2f %-15s %6.1f dB %-5s %-28s %s %s' % (
            c['t'], c.get('f') or 0, c['name'], c['gain_db'], c['align'], json.dumps(c['params'])[:28],
            ('lp %d ' % c['lp'] if c.get('lp') else '') + ('hp %d ' % c['hp'] if c.get('hp') else '') + c.get('vo', ''),
            ('carve %s' % c['carve']) if c.get('carve') else ''))
    print('heroes ok:', rep['heroes_ok'])
    print('hero speech source:', rep['hero_source'])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('cues', 'audition', 'build', 'rough', 'verify'))
    ap.add_argument('--hook', default='A', choices=('A', 'B', 'AB'))
    a = ap.parse_args(argv)
    hooks = ['A', 'B'] if a.hook == 'AB' else [a.hook]
    if a.cmd == 'audition':
        audition()
    elif a.cmd == 'verify':
        verify()
    else:
        for h in hooks:
            {'cues': print_cues, 'build': build, 'rough': rough}[a.cmd](h)


if __name__ == '__main__':
    main()
