#!/usr/bin/env python3
"""epic_sfx.py: the epic / cinematic / desi sound kit of the @jawad_mp4 reels (brand_reels/research/sound_design.md
section 3): 29 procedural sounds + 11 CC0 / public-domain sample sounds, registered into audio.py's catalog at runtime
(audio.py is never edited), plus the shared helpers the reel and music modules call (midi_hz, saw, tape_stop_fx,
_decode, _loopify, _cycles, LIB).

Rebuilt 2026-10-09 as COMMITTED code in pipeline/jawad_reels/: the first copy lived in the git-ignored
workspace/brand_reels/sfx/ and was lost. The reel modules still put that folder on sys.path AFTER pipeline/jawad_reels, so
this file wins (tools/fetch_sfx_library.py also links workspace/brand_reels/sfx/epic_sfx.py here). Numbers measured on the
old kit (cue gains, LUFS in the design docs) must be re-measured, not trusted.

USE (inside a <module>_sfx.py / <module>_music.py)
    import audio as A, epic_sfx as ES
    ES.register()                         # idempotent; register(samples=False) skips the *_real sample sounds
    c = [dict(t=14.911, name='braam', align='start', params=dict(dur=2.0)),
         dict(t=26.4, name='dhol_hit', params=dict(pitch=1.2658))]
    x = A.sound('harmonium_swell', duration=4.8, notes=(50, 57, 62))      # cached Sfx, x.hit = 0.72 * 4.8
    y = ES.tape_stop_fx(stem, 26.1333, 0.4)                                # tape stop on a real bed / stem

CONVENTIONS (audio.py's): 48 kHz stereo float32 Sfx with .hit; seed=0 everywhere (seeds 1-3 vary the sound, never its
level or tuning); levels pre-balanced: max momentary loudness = REF_LUFS (-20) + level, i.e. the Mmax column below, so
gain_db=0 is the starting point; 'dur' and 'duration' are interchangeable in A.sound(). Every sound is finished by
sfx_jawad._done (elliptic guard low-pass 19 / 20.5 kHz, DC / subsonic high-pass, click-free edges, loudness calibration,
sample peak <= -1 dBFS and true peak <= -1.0 dBTP); waveshapers, FM and varispeed reads run oversampled (sfx_jawad.shape /
benhance / fm_bell_os / varread), oscillators are band-limited (saw = PolyBLEP, harm = additive with a top fade). Beds are
seamless loops at -20 LUFS integrated (every periodic part has a whole number of cycles per loop, nonlinear stages run on
a circular pad, reverb is circular). Deterministic: identical output on every run.
    hit = the transient for impacts / clicks; the END for risers and reverse sounds (they land on t); the end of the motion
    for motion-tracking textures (laptop_fan, projector_start: cue align='start' at the motion start); timeline_scrub
    hit 0 (align='start'); harmonium_swell hit = its peak at 0.72 x duration (the swell itself starts at sample 0).

CATALOG (default params; dur = rendered length; Mmax = max momentary LUFS)            name: params -> use
  IMPACT
    braam            hit 0.04   6.9 s  -17  root=36.71 (D1), dur=4.8, growl=1, bright=1   brass stack on D1 + 8ve, 5th, 2x8ve;
                     energy from t = 0, onset thump on the hit, blat (filter + growl) peaks ~0.13 s, hold ~0.45 x dur,
                     hall tail -> title slam / reveal / cut to black (cue align='start' to lead with its blat)
    cinematic_boom   hit 0.003 10.4 s  -16  tail=1          sub sweep + punch + crack, 9-10 s thunder roll (rolling LFO),
                     canyon echoes 0.43 / 0.97 / 1.62 / 2.41 s -> the one hero slam per reel
    trailer_hit      hit 0.003  4.5 s  -17  pitch=1         taiko body 62 Hz x pitch (skin drops 90 -> 62 Hz), shell modes,
                     stick slap, anvil ring 1.2-5.4 kHz, hall -> word slams on the beat, montage hits
    dhol_hit         hit 0.003  3.8 s  -18  pitch=1         stick crack at t = 0 (3 ms ahead of the hit), dagga 58 Hz x pitch
                     falling, shell modes 173.8 / 232.0 / 413.4 Hz x pitch -> desi energy cut, drops
    heartbeat_build  hit END    5.3 s  -21  duration=4, bpm0=60, bpm1=120   lub-dubs accelerating bpm0 -> bpm1, first lub at
                     0, LAST lub on the hit (= duration), crescendo -9 -> 0 dB, dark room -> suspense into a reveal
    bell_impact_real hit onset  1.5 s  -26  (sample)        Kenney impactBell_heavy_000 (CC0) -> deadline bell
  TRANSITION
    shepard_riser    hit END    5.7 s  -21  duration=4, octaves_per_s=0.5   Shepard-Risset glissando (octave voices under a
                     raised-cosine window, + a fifth layer), rising noise sweep, accelerating tremolo, crescendo, plate
                     tail after the hit -> endless-rise tension into the drop
    reverse_cymbal   hit END    2.0 s  -22  duration=2      synthetic crash (140 modes 0.7-16.5 kHz + wash) through a hall,
                     reversed, crescendo -> suck into a slam (ends exactly on the hit, nothing after it)
    glitch_corrupt   hit 0      1.4 s  -24  dur=1, intensity=1   data corruption: tear / stutter / bit-crush (oversampled)
                     / sample-and-hold / drop-outs over digital blips -> ERROR card, corrupt-timeline cuts
    tape_stop        hit 0      1.0 s  -24  dur=0.6, tone=1  a held D-minor groove slows to a halt + capstan clunk (tone =
                     its pitch) -> the "music dies" beat (tape_stop_fx() stops a real bed)
    vinyl_rewind     hit END    1.1 s  -23  dur=1           backspin: a groove spun back (+1 -> -3.5x), needle friction, dead
                     stop on the hit -> "ruko... rewind" flashback cut
    dholak_roll      hit END    2.5 s  -22  n=12, bpm=100   n dholak strokes on the 16th grid, crescendo, ending on an
                     accented 'dha' ON the hit (n 16ths after the first stroke) -> desi fill into a hit
  UI
    notif_ping       hit 0/0.40 2.6 s  -24  pitch=1, buzz=0  flick + bell (1567.98 Hz x pitch = G6, the dominant partial)
                     + shimmer, plate; buzz=1: two 165 Hz haptic pulses (0.13 s each, 0.2 s apart, from 0.002 s, ~10 dB under
                     the ping) and the ping starts at 0.40 (its flick, bell, shimmer and plate never sound before 0.400)
    keyboard_burst   hit 0.001  1.7 s  -29  n=12, cps=10    mechanical thock keys with release clicks, human timing
    mouse_click      hit 0.001  0.4 s  -31  double=0        micro-switch press + release (double=1: second click 0.15 s on)
    render_complete  hit 0.001  4.0 s  -22  pitch=1         D-major arpeggio D5 F#5 A5 D6 (pitch 0.7937 = Bb major) + sparkle
    timeline_scrub   hit 0      1.8 s  -31  duration=1.5, speed=2   NLE audio-scrub chatter (39 ms grains per 30 fps frame,
                     reversed when dragged back), drag friction, mouse-up at duration -> playhead drag (align='start')
    clock_tick       hit 0.001  5.8 s  -29  n=6, bpm=60, accel=1   escapement tick / tock; every interval / accel (1.05-1.1)
    clock_real, typing_modelm_real  hit onset  6 / 5 s  -29 / -30  (samples, Wikimedia Commons PD / CC0)
  TEXTURE
    tension_drone    hit END    8.8 s  -26  duration=8, root=36.71   beating harmonic stack on the root (D / A only),
                     creeping whine, rising air band, crescendo to the hit (= duration exactly), 0.8 s release
    laptop_fan       hit END    4.1 s  -30  duration=3.5    fan spinning up 900 -> 5200 rpm (blade tone, motor, air) to full
                     speed on the hit, 0.4 s fade (align='start' at the render start)
    projector_start  hit END    2.9 s  -29  duration=2.5    switch, motor + claw clatter spinning up to 24 fps on the hit,
                     0.25 s run-out (align='start')
    tabla_hit        hit 0.002  1.5 s  -23  stroke='na' (na tin ta ge ke dha dhin), pitch=1   Sa = D4 293.66 Hz x pitch;
                     dayan modes 1-5 x Sa, bayan glide 88 -> 130 Hz (ge); dha = na + ge, dhin = tin + ge
    sitar_pluck      hit 0.002  4.4 s  -24  note=62, meend=0, dur=4   jawari buzz (brightness peak sweeping 6 -> 1.2 kHz in
                     0.5 s), meend = bend in semitones (0.15-0.45 s), taraf on Sa / Pa ringing in sympathy
    harmonium_swell  hit peak   3.5 s  -26  duration=2.5, notes=(50, 57, 62)   two pulse reeds per note at +-2.5 cents
                     (equal, phase-aligned at the peak), bellows (t / tp)^1.6 to the peak at tp = 0.72 x duration, -6 dB
                     by duration, 0.6 s release, 0.9 Hz pumping, 3.2 kHz low-pass, reed air; room
    crowd_ooh        hit 0.08   4.4 s  -24  n=24            synthetic crowd "ooh" (fallback only; prefer the real samples)
    applause_real, applause_build_real, crowd_cheer_real, crowd_ahh_real, crowd_ooh_real   hit onset  -25/-25/-26/-26/-26
                     (samples; crowd_cheer_real contains English speech, "Oh my God, look at that!": never use it where
                     the brief needs a wordless crowd)
  BED (seamless loops, -20 LUFS integrated, hit 0)
    dark_drone 24 s (D1 D2 A2 D3 + faint Eb3 F3 A3, dark air) · rain_city_night 20 s (rain wash + droplets 1-12 kHz,
    distant city, car swishes) · desi_city 24 s (traffic, horns 0.4-1.2 kHz, a 2-stroke rickshaw pass, wordless
    murmur; no azaan, no music) · edit_suite 16 s (PC fans, 50 Hz mains hum, AC air, coil whine) · projector_loop 8 s
    (fps=24) · rain_real 20 s, rain_thunder_real 16 s, traffic_real 16 s (samples)

SAMPLES (CC0 / PD only, tools/fetch_sfx_library.py; per-file licences in <LIB>/LICENSES.md)
    LIB = $EPIC_SFX_LIB or <repo>/workspace/brand_reels/sfx/library. A *_real sound registers only when its file exists.
    Files are untrusted data: _decode() runs ffmpeg only (demuxer forced by extension, file protocol only) into
    <repo>/workspace/brand_reels/sfx/samples48/<relpath>.wav (48 kHz stereo float32 + a .json stamp); nothing in them is
    imported or executed, and Python never parses a downloaded file itself.

HELPERS
    midi_hz(m)                    MIDI -> Hz (A4 = 69 = 440 Hz)
    saw(f, phase=0.0, n=None)     band-limited (PolyBLEP) saw -1..1 from a per-sample frequency array (phase in cycles)
    tape_stop_fx(x, t0, dur=0.8, curve=1.6)   alias-safe tape stop applied to a real buffer: untouched before t0, slowing
                                  to a halt over dur, silence after; linear in x (= sfx_jawad.tape_stop_fx)
    _decode(relpath)              library file -> float32 (N, 2) at 48 kHz (None when missing), cached
    _loopify(x, L, xf)            seamless L-sample loop from x (len >= L + xf): equal-power crossfade of the head into x[L:]
    _cycles(f0, dur)              the frequency nearest f0 with a whole number of cycles in dur (loop-safe periodic parts)
    register(samples=True)        idempotent; returns the registered names
    CONTRACT                      every (sound, params) the five reels' modules pass (python3 epic_sfx.py contract)

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
    python3 epic_sfx.py check [names]          stats + qc + table check (hit, Mmax +-1.5 LU, TP <= -1 dBTP, loop seams)
                                               -> <sfx>/out/epic_check.txt / .json + spectrogram sheets epic_sheet_N.png
                                               (all sounds: also epic_catalog.wav + _index.json); exit 1 on a failure
    python3 epic_sfx.py play <name> '<json params>' out.wav   -> wav + spectrogram png
    python3 epic_sfx.py contract               renders every CONTRACT entry (qc, TP, hit)
    python3 epic_sfx.py alias [names]          aliasing residual vs a 32x reference render (sfx_jawad's method)
    python3 epic_sfx.py catalog                names, categories, hits, params
"""
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))


def _toolkit_dir():
    """The toolkit (audio.py): pipeline/jawad_reels first, then the plugin's copy."""
    repo = os.path.abspath(os.path.join(HERE, '..', '..'))
    for d in (HERE, os.path.join(repo, 'pipeline', 'jawad_reels'), os.path.join(repo, 'plugins', 'reels-studio', 'toolkit')):
        if os.path.isfile(os.path.join(d, 'audio.py')) and os.path.isfile(os.path.join(d, 'sfx_jawad.py')):
            return d
    return HERE


_TK = _toolkit_dir()
if _TK not in sys.path:                       # also under python3 -I (no script dir on sys.path)
    sys.path.insert(0, _TK)

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402

import audio as A  # noqa: E402
import sfx_jawad as SJ  # noqa: E402
from audio import (SR, TWO_PI, _t, _n, _rng, _st, _ar, _fade, _taper, _unit, _thump, _click, _grains,  # noqa: E402
                   _loop_mask_noise, _periodic_lfo, _spec_filter, modal, noise_band, colored, osc, lp, hp, bp, reson,
                   pan, decorrelate, undb, reverb_circular)
from sfx_jawad import (shape, benhance, varread, fm_bell_os, harm, tvf, lp_mask, _done, _bed_done, _add_wrap,  # noqa: E402
                       _pad, _gate, _smoothstep, _mono_safe, reverb, _add)

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFX_DIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
LIB = os.path.abspath(os.environ.get('EPIC_SFX_LIB') or os.path.join(SFX_DIR, 'library'))
SAMPLES48 = os.path.abspath(os.environ.get('EPIC_SFX_SAMPLES48') or os.path.join(os.path.dirname(LIB), 'samples48'))
OUT = os.path.join(SFX_DIR, 'out')
REF = A.REF_LUFS


# =============================================================================================== shared helpers
def midi_hz(m):
    """MIDI note number -> Hz (A4 = 69 = 440 Hz). Scalars give a float, arrays an array."""
    v = 440.0 * 2.0 ** ((np.asarray(m, dtype=np.float64) - 69.0) / 12.0)
    return float(v) if v.ndim == 0 else v


def saw(f, phase=0.0, n=None):
    """Band-limited sawtooth (PolyBLEP), amplitude -1..1, rising ramp. f: frequency in Hz per sample (array), or a
    scalar together with n samples; phase: start phase in cycles (0..1). Returns float64 (n,)."""
    f = np.asarray(f, dtype=np.float64)
    if f.ndim == 0:
        if n is None:
            raise ValueError('saw(): a scalar frequency needs n')
        f = np.full(int(n), float(f))
    if len(f) == 0:
        return np.zeros(0)
    dt = np.clip(np.abs(f) / SR, 0.0, 0.5)
    ph = (float(phase) + np.concatenate([[0.0], np.cumsum(dt[:-1])])) % 1.0
    y = 2.0 * ph - 1.0
    m = ph < dt
    if m.any():
        u = ph[m] / dt[m]
        y[m] -= 2.0 * u - u * u - 1.0
    m = ph > 1.0 - dt
    if m.any():
        u = (ph[m] - 1.0) / dt[m]
        y[m] -= u * u + 2.0 * u + 1.0
    return y


def tape_stop_fx(x, t0, dur=0.8, curve=1.6):
    """Tape stop on a real buffer (a music bed, a stem, an SFX bus) at t0 s: untouched before t0, slowing to a halt over
    dur (rate = (1 - u)^curve, level ~ rate^0.55, highs closing 19 kHz -> 150 Hz), silence after t0 + dur. Alias-safe (8x
    cubic varispeed) and linear in x, so it can run per stem. Mono or stereo; returns a new float64 array of x's shape.
    (= sfx_jawad.tape_stop_fx; callers that need a click-free entry crossfade the first 10 ms themselves.)"""
    return SJ.tape_stop_fx(x, float(t0), float(dur), float(curve))


def _cycles(f0, dur):
    """The frequency nearest f0 that has a whole number (>= 1) of cycles in dur s: periodic parts of a seamless loop."""
    dur = float(dur)
    return max(1, int(round(float(f0) * dur))) / dur


def _loopify(x, L, xf):
    """Seamless loop of L samples cut from x (len(x) >= L + xf): the first xf samples are an equal-power crossfade of
    x's head with its continuation x[L:L + xf], so the loop's last sample runs into its first exactly as x[L-1] runs into
    x[L]. Mono or stereo; returns float64 (L, ...)."""
    x = np.asarray(x, dtype=np.float64)
    L, xf = int(L), int(max(0, xf))
    if len(x) < L:
        raise ValueError('_loopify: x has %d samples, the loop needs %d' % (len(x), L))
    xf = min(xf, len(x) - L, L)
    y = x[:L].copy()
    if xf > 0:
        u = (np.arange(xf) + 0.5) / xf
        a, b = np.sin(0.5 * np.pi * u), np.cos(0.5 * np.pi * u)
        if y.ndim == 2:
            a, b = a[:, None], b[:, None]
        y[:xf] = x[:xf] * a + x[L:L + xf] * b
    return y


def _circ(fn, x, pad):
    """fn applied to a loop with `pad` samples of its other end on each side (loop-safe filters / shapers)."""
    p = int(min(max(1, pad), len(x)))
    xx = np.concatenate([x[-p:], x, x[:p]], axis=0)
    return fn(xx)[p:p + len(x)]


def _accel_times(D, b0, b1):
    """Beat times from 0 to D (first beat at 0, last ON D) of a pulse accelerating from b0 to b1 BPM: floor(beats in a
    linear tempo ramp) intervals, each proportional to 60 / bpm at its middle, scaled to fill D exactly."""
    nb = max(1, int(math.floor(D * (b0 + b1) / 120.0 + 1e-9)))
    bpm = b0 + (b1 - b0) * (np.arange(nb) + 0.5) / nb
    iv = 60.0 / bpm
    iv *= D / iv.sum()
    return np.concatenate([[0.0], np.cumsum(iv)])


def _onset(x, rel_db=-20.0, win=0.005):
    """Seconds to the first point where the `win` RMS envelope reaches its maximum + rel_db."""
    m = np.square(np.asarray(x, dtype=np.float64)).mean(axis=1) if np.ndim(x) == 2 else np.square(x)
    e = np.sqrt(np.maximum(A._smooth(m, win), 0.0))
    if not np.any(e > 0):
        return 0.0
    return float(np.argmax(e >= e.max() * undb(rel_db)) / SR)


# =============================================================================================== registry
SYNTH = {}            # name -> dict(fn, category, hit, dur, mmax, character, use, send)


def _synth(category, hit, dur, mmax, character, use, send=None):
    """Register a procedural sound in this module's table (hit: seconds | 'end' | 'peak' | 'loop'; dur / mmax: the
    sound_design.md section 3 numbers at default params)."""
    def deco(fn):
        SYNTH[fn.__name__] = dict(fn=fn, category=category, hit=hit, dur=dur, mmax=mmax, character=character, use=use,
                                  send=send)
        return fn
    return deco


def _lvl(name):
    return SYNTH[name]['mmax'] - REF if name in SYNTH else SAMPLES[name]['mmax'] - REF


# =============================================================================================== IMPACTS
@_synth('impact', 0.04, 6.9, -17.0, 'trailer braam: detuned brass stack on the root (D1) + 8ve, 5th and 2 x 8ve, energy '
        'from t = 0, onset thump on the hit, a blat (filter + 41 Hz growl) peaking ~0.13 s, sub sine, hall tail',
        'title slam / "AI video ad" reveal / cut to black (cue align=start to lead with the blat)', send=-28)
def braam(seed=0, root=36.71, dur=4.8, growl=1.0, bright=1.0):
    """Braam (dur s of brass + hall). hit = 0.04 s (the onset thump). The energy starts at t = 0 (3 ms attack), the blat
    peaks ~0.13 s, the body holds to ~0.45 x dur and decays to zero at dur, then the hall rings ~3 s."""
    r = _rng(seed, 'braam')
    D = max(0.5, float(dur))
    f0 = max(20.0, float(root))
    gr = max(0.0, float(growl))
    br = max(0.1, float(bright))
    hit = 0.04
    d = D + 0.06
    t = _t(d)
    N = len(t)
    att = 0.5 - 0.5 * np.cos(np.pi * np.clip(t / 0.003, 0, 1))
    rel0 = 0.45 * D
    dec = np.where(t < rel0, 1.0, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - rel0) / (D - rel0), 0, 1)))
    blat = 1.0 + 0.5 * np.exp(-0.5 * ((t - 0.13) / 0.05) ** 2)
    env = att * blat * dec * (0.8 + 0.2 * np.exp(-t / 0.7))
    scoop = 1.0 - 0.03 * np.exp(-t / 0.035)                       # the lip scoop into pitch
    flutter = 1.0 + 0.004 * gr * np.sin(TWO_PI * 5.3 * t + r.uniform(0, TWO_PI))
    st = np.zeros((N, 2))
    for mult, amp in ((1, 1.0), (2, 0.85), (3, 0.55), (4, 0.45), (6, 0.18)):
        for k, cents in enumerate((-9.0, 0.0, 8.0)):
            f = f0 * mult * 2.0 ** (cents / 1200.0) * scoop * flutter
            st += pan(saw(f, r.uniform(0, 1)) * amp, (k - 1) * 0.45)
    st /= 4.5
    g = 1.0 + 0.35 * gr * np.sin(TWO_PI * 41.0 * t + r.uniform(0, TWO_PI)) * np.clip(t / 0.05, 0, 1)
    st = st * (env * g)[:, None]
    st = shape(st * (1.1 + 0.6 * gr), 1.6 + 1.2 * gr)

    def fc(p):
        tt = p * d
        body = 750.0 * np.clip(tt / 0.1, 0, 1) * np.clip(1.0 - (tt - rel0) / (D - rel0), 0.15, 1.0)
        return br * (380.0 + 2300.0 * np.exp(-0.5 * ((tt - 0.12) / 0.07) ** 2) + body)
    st = tvf(st, lp_mask(fc, 2.0))
    sub = np.sin(TWO_PI * f0 * t) * att * dec * np.exp(-t / (0.8 * D)) * 0.5
    th = np.zeros(N)
    _add(th, _thump(0.5, max(40.0, 1.3 * f0), 70.0, 0.02, 0.11, r, attack=0.003, drive=2.0, noise=0.4,
                    noise_lp=500.0), hit - 0.003)
    low = benhance(sub + 0.55 * th, 0.8, fc=100.0, band=(150.0, 700.0), drive=5.0)
    st = _taper(st + _st(low), sec=0.03)
    out = reverb(st, 'hall', wet_db=-7.0, send_hp=110.0)
    return _done(out, hit, _lvl('braam'), 'braam')


@_synth('impact', 0.003, 10.4, -16.0, 'deep cinematic boom: 30 Hz sub sweep, kick punch, crack, a 9-10 s thunder roll '
        'with a rolling LFO, canyon echoes at 0.43 / 0.97 / 1.62 / 2.41 s, hall', 'the one hero slam per reel (black '
        'frame, keyword lands)', send=-30)
def cinematic_boom(seed=0, tail=1.0):
    """Cinematic boom (~10.4 s). hit = 0.003 s. tail scales the roll and the hall."""
    r = _rng(seed, 'cinematic_boom')
    T = min(2.0, max(0.25, float(tail)))
    d = 1.5 + 7.2 * T
    t = _t(d)
    N = len(t)
    sub = osc(30.0 + 80.0 * np.exp(-t / 0.06)) * _ar(t, 0.002, 1.4 * T, 0.001)
    punch = osc(52.0 + 150.0 * np.exp(-t / 0.018)) * _ar(t, 0.0012, 0.18, 0.0015)
    body = _unit(lp(colored(N, r, -6.0), 560.0, 2)) * _ar(t, 0.001, 0.1, 0.0015)
    crack = _unit(bp(r.standard_normal(N), 1300.0, 7000.0)) * _ar(t, 0.0002, 0.012, 0.002)
    low = shape(0.9 * sub + 0.55 * punch + 0.3 * body, 1.8)
    low = benhance(low, 0.9, fc=100.0, band=(170.0, 800.0), drive=6.0)
    lfo = 1.0 + 0.4 * (np.sin(TWO_PI * r.uniform(0.35, 0.55) * t + r.uniform(0, TWO_PI))
                       * np.sin(TWO_PI * r.uniform(0.9, 1.3) * t + r.uniform(0, TWO_PI)))
    roll = noise_band(d, r, [(0, 140.0), (0.3, 90.0), (1, 55.0)], bw=1.2, width=0.7)
    roll = roll * ((1 - np.exp(-t / 0.15)) * np.exp(-t / (3.3 * T)) * lfo)[:, None]
    grit = noise_band(d, r, [(0, 900.0), (1, 300.0)], bw=1.0, width=0.8)
    grit = grit * ((1 - np.exp(-t / 0.05)) * np.exp(-t / (1.1 * T)) * lfo)[:, None]
    st = _st(low + 0.2 * crack) + 0.30 * roll + 0.05 * grit
    strike = hp(0.55 * punch + 0.3 * body + 0.25 * crack, 70.0, 2)
    for dly, gdb, fcut, pn in ((0.43, -10.0, 2400.0, -0.6), (0.97, -14.0, 1600.0, 0.55), (1.62, -18.0, 1100.0, -0.4),
                               (2.41, -23.0, 800.0, 0.35)):
        e = _taper(lp(strike, fcut, 2), sec=0.8)
        _add(st, pan(e[:N - _n(dly)], pn) * undb(gdb), dly)
    st = _taper(st, sec=1.5)
    out = reverb(st, 'hall', wet_db=-5.0, send_hp=90.0, rt60=3.2)
    return _done(out, 0.003, _lvl('cinematic_boom'), 'cinematic_boom')


@_synth('impact', 0.003, 4.5, -17.0, 'trailer hit: taiko body 62 Hz x pitch (skin drops 90 -> 62 Hz, shell modes), '
        'stick slap, anvil ring 1.2-5.4 kHz, hall', 'word slams on the beat, montage hits, felt taiko (lp 1500)', send=-24)
def trailer_hit(seed=0, pitch=1.0):
    """Taiko / anvil trailer hit (~4.5 s). hit = 0.003 s. pitch scales every mode (the drum fundamental is 62 Hz x pitch)."""
    r = _rng(seed, 'trailer_hit')
    p = max(0.25, float(pitch))
    d = 3.0
    t = _t(d)
    N = len(t)
    t0 = 0.002
    f0 = 62.0 * p
    u = np.maximum(t - t0, 0.0)
    skin = osc(f0 * (1.0 + 0.45 * np.exp(-u / 0.025))) * _ar(t, 0.0015, 0.38, t0)
    shell = modal(d, [f0 * k for k in (1.59, 2.14, 2.30, 2.65, 2.92, 3.50)], [0.22, 0.16, 0.13, 0.10, 0.08, 0.06],
                  [0.45, 0.35, 0.28, 0.2, 0.15, 0.1], r, contact=0.0012, t0=t0)
    slap = _unit(bp(r.standard_normal(N), 260.0 * p, 3600.0)) * _ar(t, 0.0004, 0.010, t0)
    anvil = modal(d, [f * p for f in (1180.0, 1730.0, 2440.0, 3190.0, 4120.0, 5390.0)],
                  [1.1, 0.85, 0.62, 0.44, 0.31, 0.21], [1.0, 0.75, 0.55, 0.4, 0.28, 0.18], r, split=2.2,
                  contact=0.0003, t0=t0 + 0.001)
    mono = shape((0.95 * skin + 0.5 * shell + 0.35 * slap) * 0.9, 2.2)
    mono = benhance(mono, 0.9, fc=110.0, band=(160.0, 750.0), drive=5.0) + 0.10 * anvil
    st = _taper(decorrelate(mono, r, 0.25), sec=0.8)
    out = reverb(st, 'hall', wet_db=-8.0, send_hp=110.0, rt60=3.2)
    return _done(out, 0.003, _lvl('trailer_hit'), 'trailer_hit')


@_synth('impact', 0.003, 3.8, -18.0, 'dhol: stick crack on the treble head 3 ms ahead of the hit, dagga (bass head) 58 Hz '
        'x pitch falling from +32 %, shell modes 173.8 / 232.0 / 413.4 Hz x pitch, slap, hall',
        'desi energy cut, "bas!" moments, drops and chaal strokes', send=-22)
def dhol_hit(seed=0, pitch=1.0):
    """Dhol hit (~3.8 s). hit = 0.003 s (the dagga); the stick crack is at t = 0. pitch scales the heads and the shell."""
    r = _rng(seed, 'dhol_hit')
    p = max(0.25, float(pitch))
    d = 2.5
    t = _t(d)
    N = len(t)
    th = 0.003
    u = np.maximum(t - th, 0.0)
    dagga = osc(58.0 * p * (1.0 + 0.32 * np.exp(-u / 0.045))) * _ar(t, 0.0018, 0.42, th)
    shell = modal(d, [173.8 * p, 232.0 * p, 413.4 * p, 612.0 * p], [0.24, 0.17, 0.11, 0.07], [0.55, 0.42, 0.3, 0.14],
                  r, contact=0.0009, t0=th)
    crack = _unit(bp(r.standard_normal(N), 1500.0, 8500.0)) * _ar(t, 0.0002, 0.005, 0.0)
    slap = _unit(bp(r.standard_normal(N), 380.0, 2600.0)) * _ar(t, 0.0005, 0.025, 0.0008)
    mono = shape((0.95 * dagga + 0.55 * shell + 0.30 * slap) * 0.9, 1.9)
    mono = benhance(mono, 1.0, fc=110.0, band=(150.0, 700.0), drive=5.0) + 0.22 * crack
    st = _taper(decorrelate(mono, r, 0.2), sec=0.6)
    out = reverb(st, 'hall', wet_db=-11.0, send_hp=110.0)
    return _done(out, 0.003, _lvl('dhol_hit'), 'dhol_hit')


@_synth('impact', 'end', 5.3, -21.0, 'heartbeat build: lub-dubs accelerating from bpm0 to bpm1, first lub at 0, the LAST '
        'lub on the hit, crescendo -9 -> 0 dB, dark room', 'suspense before a reveal (lands on the reveal frame)',
        send=-26)
def heartbeat_build(seed=0, duration=4.0, bpm0=60.0, bpm1=120.0):
    """Accelerating heartbeat (duration s + ~1.3 s dub and tail). hit = duration (the last lub's transient)."""
    r = _rng(seed, 'heartbeat_build')
    D = max(0.2, float(duration))
    b0, b1 = max(20.0, float(bpm0)), max(20.0, float(bpm1))
    beats = _accel_times(D, b0, b1)
    nb = len(beats)
    x = np.zeros(_n(D + 1.3))
    for k, tb in enumerate(beats):
        bpm_here = b0 + (b1 - b0) * tb / D
        gap = 0.29 * math.sqrt(62.0 / bpm_here)
        g = undb(-9.0 * (1.0 - (k / (nb - 1)) ** 1.3)) if nb > 1 else 1.0
        for off, amp, fe in ((0.0, 1.0, 46.0), (gap, 0.62, 54.0)):
            th = _thump(0.55, fe * r.uniform(0.97, 1.03), 42.0, 0.022, 0.08, r, attack=0.004, drive=2.6, noise=0.55,
                        noise_lp=220.0, click=0.18, click_band=(250.0, 1100.0))
            _add(x, th * amp * g * r.uniform(0.95, 1.0), max(0.0, tb + off - 0.004))
    x = benhance(x, 1.6, fc=120.0, band=(170.0, 600.0), drive=6.0)
    st = reverb(_st(lp(x, 1100.0, 2)), 'dark', wet_db=-15.0)
    return _done(st, D, _lvl('heartbeat_build'), 'heartbeat_build', keep_until=D)


# =============================================================================================== TRANSITIONS
@_synth('transition', 'end', 5.7, -21.0, 'Shepard-Risset riser: octave-spaced voices gliding up under a raised-cosine '
        'window (+ a fifth layer), rising noise sweep, accelerating tremolo, crescendo into the hit, plate tail after it',
        'endless-rise tension into the drop', send=-20)
def shepard_riser(seed=0, duration=4.0, octaves_per_s=0.5):
    """Shepard riser (duration s, then the plate tail). hit = duration (it lands on the drop)."""
    r = _rng(seed, 'shepard_riser')
    D = max(0.2, float(duration))
    rate = float(octaves_per_s)
    t = _t(D)
    N = len(t)
    p = t / D
    nv, lo = 8, 40.0
    tone = np.zeros(N)
    for layer, (mult, amp) in enumerate(((1.0, 1.0), (1.5, 0.35))):
        ph0 = r.uniform(0, 1)
        for k in range(nv):
            u = ((k + ph0 + rate * t) % nv) / nv
            f = lo * mult * 2.0 ** (u * nv)
            w = 0.5 - 0.5 * np.cos(TWO_PI * u)
            ph = TWO_PI * np.cumsum(f) / SR + r.uniform(0, TWO_PI)
            g2 = np.clip((18000.0 - 2.0 * f) / 3000.0, 0.0, 1.0)
            tone += amp * w * (np.sin(ph) + 0.22 * g2 * np.sin(2.0 * ph + 0.4))
    trem = 0.72 + 0.28 * np.sin(TWO_PI * np.cumsum(4.0 + 14.0 * p ** 2) / SR)
    env = (0.12 + 0.88 * p ** 1.7) * np.clip(t / 0.03, 0, 1)
    st = decorrelate(tone * trem * env * 0.12, r, 0.5)
    nz = noise_band(D, r, lambda q: 400.0 * (7000.0 / 400.0) ** (q ** 1.4), lambda q: 1.1 - 0.5 * q,
                    width=lambda q: 0.3 + 0.6 * q)
    st = st + 0.55 * _pad(nz, N) * (env * p ** 1.2)[:, None]
    st = _fade(st, 0.01, 0.006)
    out = reverb(st, 'plate', wet_db=-9.0, hard_end=True)
    return _done(out, D, _lvl('shepard_riser'), 'shepard_riser', keep_until=D)


@_synth('transition', 'end', 2.0, -22.0, 'reverse cymbal: a synthetic crash (140 modes 0.7-16.5 kHz, bright tilt, wash) '
        'through a hall, reversed, crescendo; ends exactly on the hit with 3-15 kHz energy', 'suck into a slam (pair with '
        'braam / boom)', send=-24)
def reverse_cymbal(seed=0, duration=2.0):
    """Reverse cymbal (exactly duration s). hit = duration (the END)."""
    r = _rng(seed, 'reverse_cymbal')
    D = max(0.15, float(duration))
    sd = max(1.2, 1.25 * D + 0.4)
    t = _t(sd)
    N = len(t)
    nm = 140
    fr = np.exp(r.uniform(math.log(700.0), math.log(16500.0), nm))
    taus = 2.2 * (fr / 700.0) ** -0.42 * r.uniform(0.7, 1.3, nm)
    amps = (fr / 700.0) ** 0.15 * r.uniform(0.3, 1.0, nm)
    crash = modal(sd, fr, taus, amps, r, contact=0.0002, rand_phase=True)
    wash = _unit(bp(r.standard_normal(N), 3000.0, 15000.0, 2)) * np.exp(-t / 0.9) * 0.6
    stick = _unit(hp(r.standard_normal(N), 2500.0)) * _ar(t, 0.0002, 0.004)
    mono = crash / (np.max(np.abs(crash)) + 1e-12) + wash + 0.5 * stick
    wet = reverb(decorrelate(mono, r, 0.6), 'hall', wet_db=-4.0, rt60=max(1.6, D * 1.2), predelay=0.0, build=0.005)
    y = _pad(wet, _n(D))[::-1].copy()
    y *= (np.linspace(0.0, 1.0, len(y)) ** 1.6)[:, None]
    y = _mono_safe(y)
    fin = min(0.02, 0.1 * D)
    y = _fade(y, fin, 0.003)
    return _done(y, D, _lvl('reverse_cymbal'), 'reverse_cymbal', trim=False, fin=fin, fout=0.003)


def _data_source(d, r):
    """'Data' to corrupt: back-to-back 6-50 ms bits of FM blips (oversampled), band-limited square buzz, noise bursts and a
    digital whine. Mono, peak 1."""
    M = _n(d)
    src = np.zeros(M)
    tt = 0.0
    while tt < d - 0.02:
        L = r.uniform(0.006, 0.05)
        n = _n(L)
        kind = int(r.integers(0, 4))
        if kind == 0:
            g = fm_bell_os(L, r.uniform(300.0, 2400.0), ratio=float(r.choice([0.5, 1.5, 2.0, 3.0])),
                           index=r.uniform(1.0, 3.5), tau=L, tau_index=10.0, attack=0.0005)
        elif kind == 1:
            g = harm(np.full(n, r.uniform(110.0, 440.0)), [1, 0, 1 / 3., 0, 1 / 5., 0, 1 / 7., 0, 1 / 9.], fmax=12000.0,
                     rng=r)
        elif kind == 2:
            lo_ = r.uniform(600.0, 3000.0)
            g = _unit(bp(r.standard_normal(n), lo_, min(16000.0, lo_ * r.uniform(2.0, 5.0))))
        else:
            g = harm(np.full(n, r.uniform(2500.0, 6500.0)), [1.0, 0.3], fmax=16000.0, rng=r)
        g = _pad(g, n) * _gate(np.arange(n) / SR, 0.0, L, 0.0004) * r.uniform(0.4, 1.0)
        _add(src, g, tt)
        tt += L + (r.uniform(0.0, 0.015) if r.random() < 0.4 else 0.0)
    return src / (np.max(np.abs(src)) + 1e-12)


@_synth('transition', 0.0, 1.4, -24.0, 'data corruption: digital blips torn (pitch jumps), stuttered (a slice x3-8), '
        'bit-crushed (oversampled), sample-and-held and dropped out; low tear thud at the onset', '"ERROR / can\'t delete '
        'this memory" device, corrupt-timeline transitions', send=-18)
def glitch_corrupt(seed=0, dur=1.0, intensity=1.0):
    """Glitch corruption (dur s + room). hit = 0 (abrupt onset). intensity 0..2 = how much of it is corrupted."""
    r = _rng(seed, 'glitch_corrupt')
    D = max(0.15, float(dur))
    I = float(np.clip(intensity, 0.0, 2.0))
    sd = D + 0.6
    src = _data_source(sd, r)
    src_lp = lp(lp(src, 8500.0, 2), 8500.0, 2)                    # read at up to 2x
    out = np.zeros((_n(D + 0.05), 2))
    ops = ('play', 'tear', 'stutter', 'crush', 'hold', 'drop')
    w = np.array([1.0, 1.2 * I, 1.2 * I, 0.8 * I, 0.8 * I, 0.6 * I]) + 1e-9
    w /= w.sum()
    pos, spos, first = 0.0, r.uniform(0.0, 0.2), True
    while pos < D:
        L = r.uniform(0.012, 0.045)
        n = _n(L)
        op = 'tear' if first else str(r.choice(ops, p=w))
        first = False
        i0 = int(_n(spos)) % max(1, len(src) - n - 1)
        seg = src[i0:i0 + n].copy()
        if op == 'tear':
            rate = float(r.choice([0.5, 0.71, 1.41, 2.0]))
            seg = varread(src_lp, i0 + np.arange(n) * rate)
        elif op == 'stutter':
            k = int(r.integers(3, 9))
            m = max(16, n // k)
            sl = src[i0:i0 + m] * _gate(np.arange(m) / SR, 0.0, m / SR, 0.0003)
            seg = np.tile(sl, k + 1)[:n]
        elif op == 'crush':
            q = 2.0 ** (int(r.integers(3, 7)) - 1)
            seg = SJ._down(np.round(SJ._up(seg, 8) * q) / q, 8, n)
        elif op == 'hold':
            hold = SR / r.uniform(1500.0, 6000.0)
            idx = np.minimum((np.floor(np.arange(n) / hold) * hold).astype(int), n - 1)
            seg = lp(seg[idx], 15000.0, 2)
        elif op == 'drop':
            seg = np.zeros(n)
        seg = _pad(seg, n) * _gate(np.arange(n) / SR, 0.0, L, 0.0003) * r.uniform(0.6, 1.0) * (1.0 - 0.35 * pos / D)
        _add(out, pan(seg, r.uniform(-0.7, 0.7)), pos)
        pos += L
        spos += L * r.uniform(0.3, 2.5)
    tt = _t(0.12)
    _add(out, _st(shape(osc(80.0 + 180.0 * np.exp(-tt / 0.012)) * _ar(tt, 0.0005, 0.03), 2.0) * 0.3), 0.0)
    out = _fade(out, 0.0002, 0.03)
    out = reverb(out, 'room', wet_db=-17.0)
    return _done(out, 0.0, _lvl('glitch_corrupt'), 'glitch_corrupt', fin=0.0002)


def _groove(tau, r, tone=1.0, bpm=90.0):
    """A held D-minor groove evaluated analytically at tape time tau (s): pad chord D3 F3 A3 D4 + bass D2 (6 harmonics
    each, band-limited), kick on the beat. tone scales the pitch."""
    out = np.zeros_like(tau)
    for f, a in ((146.83, .5), (174.61, .35), (220.0, .35), (293.66, .25), (73.42, .55)):
        f = f * tone
        for k in range(1, 7):
            if f * k < 9000.0:
                out += a * k ** -1.3 * np.sin(TWO_PI * f * k * tau + r.uniform(0, TWO_PI))
    out *= 0.25
    beat = 60.0 / bpm
    for kb in range(int(np.max(tau) / beat) + 2):
        uu = tau - kb * beat
        m = uu > 0
        uu = np.where(m, uu, 0.0)
        phs = TWO_PI * (48.0 * tone ** 0.5 * uu + 110.0 * 0.03 * (1 - np.exp(-uu / 0.03)))
        out += 0.9 * np.where(m, np.sin(phs) * np.exp(-uu / 0.15) * (1 - np.exp(-uu / 0.002)), 0.0)
    return out


@_synth('transition', 0.0, 1.0, -24.0, 'tape stop: a held D-minor groove slows to a halt (pitch and speed -> 0, level and '
        'highs falling) + capstan clunk; tone = the groove pitch', '"music dies" beat before a punchline (tape_stop_fx() '
        'stops the real bed)', send=-20)
def tape_stop(seed=0, dur=0.6, tone=1.0):
    """Tape stop (dur s + clunk). hit = 0 (the stop starts)."""
    r = _rng(seed, 'tape_stop')
    D = max(0.2, float(dur))
    tn = max(0.25, float(tone))
    d = D + 0.32
    t = _t(d)
    rate = np.where(t < D, (1 - np.clip(t / D, 0, 1)) ** 1.6, 0.0)
    tau0 = 0.37
    tau = tau0 + np.cumsum(rate) / SR - rate[0] / SR
    hat_buf = np.zeros(_n(tau0 + D + 0.5))
    hb = _t(0.05)
    for kh in range(int((tau0 + D + 0.4) / (60.0 / 180.0)) + 1):
        _add(hat_buf, _unit(bp(r.standard_normal(len(hb)), 6000, 15000)) * _ar(hb, 0.0005, 0.012) * 0.22,
             kh * 60.0 / 180.0)
    y = (_groove(tau, r, tn) + varread(hat_buf, tau * SR)) * rate ** 0.55
    y = tvf(y, lp_mask(lambda q: 150.0 + 15000.0 * np.interp(q * d, t, rate) ** 1.5, 1.5))
    y += osc(600.0 * tn * rate ** 1.5 + 1e-3) * rate * 0.02
    _add(y, _thump(0.3, 70.0, 40.0, 0.015, 0.05, r, attack=0.002, drive=1.5, noise=0.4, noise_lp=900.0, click=0.4,
                   click_band=(900.0, 4000.0)) * 0.18, D)
    st = reverb(decorrelate(y, r, 0.3), 'room', wet_db=-18.0)
    return _done(st, 0.0, _lvl('tape_stop'), 'tape_stop', fin=0.004)


@_synth('transition', 'end', 1.1, -23.0, 'vinyl rewind: a groove spun backwards (+1 -> -3.5x), needle friction rising '
        'with the speed, dead stop on the hit', '"ruko... rewind" flashback cut (ends on the cut)', send=-20)
def vinyl_rewind(seed=0, dur=1.0):
    """DJ backspin (dur s + 0.12 s of room). hit = dur (the END: the cut)."""
    r = _rng(seed, 'vinyl_rewind')
    D = max(0.2, float(dur))
    sd = 3.2
    ts = _t(sd)
    hats = np.zeros(len(ts))
    hb = _t(0.05)
    for kh in range(int(sd / (60.0 / 180.0)) + 1):
        _add(hats, _unit(bp(r.standard_normal(len(hb)), 5000, 12000)) * _ar(hb, 0.0005, 0.012) * 0.2, kh * 60.0 / 180.0)
    src = lp(lp(_groove(ts, r) + hats, 4500.0, 2), 4500.0, 2)    # read at up to 3.5x: stays under 16 kHz
    t = _t(D)
    v = 1.0 - 4.5 * _smoothstep(t / D) ** 0.8
    pos = np.clip(2.4 + np.cumsum(v) / SR, 0.05, sd - 0.05)
    y = varread(src, pos * SR) * (0.55 + 0.45 * np.abs(v) / 3.5)
    y = y + _unit(bp(r.standard_normal(len(t)), 1200.0, 6000.0)) * (np.abs(v) / 3.5) ** 1.2 * 0.08
    y = _fade(y, 0.004, 0.003)
    st = decorrelate(y, r, 0.25)
    out = np.zeros((_n(D + 0.12), 2))
    out[:len(st)] = st
    wet = reverb(st, 'room', wet_db=-20.0, dry=0.0)[:len(out)]
    out += _fade(_pad(wet, len(out)), 0.0, 0.06)
    return _done(out, D, _lvl('vinyl_rewind'), 'vinyl_rewind', trim=False, fin=0.004, fout=0.04)


def _dholak_stroke(kind, r):
    """One dholak stroke (mono, ~0.5 s): treble head na / ta (modes on A4 440 Hz), slap ke, bass ge (A2 110 -> D3 147 Hz
    pressure glide), dha = na + ge."""
    d = 0.5
    t = _t(d)
    N = len(t)
    sa = 440.0 * r.uniform(0.997, 1.003)

    def treble(damp, slap):
        x = modal(d, [sa * k for k in (1.0, 1.59, 2.14, 2.30, 2.65)], [0.12 * damp, 0.08 * damp, 0.06 * damp,
                                                                        0.05 * damp, 0.04 * damp],
                  [1.0, 0.6, 0.45, 0.35, 0.2], r, contact=0.0004)
        return x + _unit(bp(r.standard_normal(N), 800.0, 5000.0)) * _ar(t, 0.0002, 0.003) * slap

    def bass():
        f = 110.0 + 37.0 * (1.0 - np.exp(-t / 0.06))
        x = np.sin(TWO_PI * np.cumsum(f) / SR) * _ar(t, 0.002, 0.22)
        x = x + _unit(lp(r.standard_normal(N), 400.0, 2)) * _ar(t, 0.001, 0.02) * 0.3
        return x
    if kind == 'na':
        return treble(1.0, 0.3)
    if kind == 'ta':
        return treble(0.35, 0.5)
    if kind == 'ke':
        return (_unit(bp(r.standard_normal(N), 300.0, 2000.0)) * _ar(t, 0.0005, 0.012) * 0.6
                + np.sin(TWO_PI * 150.0 * t) * _ar(t, 0.001, 0.02) * 0.5)
    if kind == 'ge':
        return bass()
    return 0.6 * treble(1.0, 0.3) + 0.7 * bass()              # dha


@_synth('transition', 'end', 2.5, -22.0, 'dholak roll: n strokes on the 16th grid of bpm (ge ta na ta ...), crescendo '
        '-14 -> -2 dB, ending on an accented dha ON the hit', 'desi fill into a hit / section', send=-18)
def dholak_roll(seed=0, n=12, bpm=100.0):
    """Dholak fill (~2.5 s). hit = 0.002 + n 16ths (the closing 'dha')."""
    r = _rng(seed, 'dholak_roll')
    n = max(1, int(n))
    step = 60.0 / max(30.0, float(bpm)) / 4.0
    hit = 0.002 + n * step
    x = np.zeros(_n(hit + 0.6))
    pattern = ('ge', 'ta', 'na', 'ta')
    for k in range(n):
        g = undb(-14.0 + 12.0 * (k / max(1, n - 1)) ** 1.2)
        tk = 0.002 + k * step + (r.uniform(-0.004, 0.004) if k else 0.0)
        _add(x, _dholak_stroke(pattern[k % 4], r) * g * r.uniform(0.9, 1.0), tk)
    _add(x, _dholak_stroke('dha', r) * undb(1.0), hit)
    x = shape(x / (np.max(np.abs(x)) + 1e-12) * 0.9, 1.4)
    st = reverb(decorrelate(x, r, 0.2), 'room', wet_db=-16.0)
    return _done(st, hit, _lvl('dholak_roll'), 'dholak_roll', keep_until=hit, fin=0.0002)


# =============================================================================================== UI
@_synth('ui', 0.0, 2.6, -24.0, 'phone notification: soft flick + bell on G6 (1567.98 Hz x pitch, its dominant partial) + '
        'faint shimmer, plate; buzz=1: two 165 Hz haptic pulses (0.13 s, 0.2 s apart) first, the ping at 0.40 s',
        'client DMs / "new message" pops (buzz=1: the phone buzzing on a table)', send=-20)
def notif_ping(seed=0, pitch=1.0, buzz=0):
    """Notification ping (~2.6 s). hit = 0 (buzz=0) or 0.40 s (buzz=1: the haptic pulses start at 0.002 s; the ping's
    flick, bell, shimmer and their plate all start at 0.400, so x[:0.385 s] holds the haptic alone)."""
    r = _rng(seed, 'notif_ping')
    p = max(0.05, float(pitch))
    bz = 1 if int(buzz) else 0
    tp = 0.40 if bz else 0.0
    d = tp + 1.3
    t = _t(d)
    N = len(t)
    f = 1567.98 * p
    u = np.maximum(t - tp, 0.0)
    bell = modal(d, [f, 2.0 * f, 3.0 * f, 4.17 * f], [0.5, 0.18, 0.1, 0.05], [1.0, 0.16, 0.07, 0.04], r,
                 contact=0.0007, t0=tp)
    flick = osc(f * (0.5 + 0.5 * np.clip(u / 0.012, 0, 1))) * _ar(t, 0.0008, 0.010, tp) * 0.35
    ping = _st(bell + flick)
    _add(ping, _grains(0.7, r, 14, 5000.0, 10000.0, 0.01, 0.05, density=lambda q: np.exp(-q * 5.0)) * 0.035, tp)
    st = ping
    if bz:
        hap = np.zeros(N)
        tt = _t(0.13)
        for t0 in (0.002, 0.202):
            pulse = harm(np.full(len(tt), 165.0), [1.0, 0.45, 0.25, 0.12], fmax=4000.0) * _gate(tt, 0.0, 0.13, 0.006)
            _add(hap, pulse, t0)
        hap = _st(hap)
        hap *= undb(A.momentary_max(ping) - 10.0 - A.momentary_max(hap))    # the buzz sits 10 dB under its ping
        st = ping + hap
    st = reverb(st, 'plate', wet_db=-17.0, send_hp=250.0)
    return _done(st, tp, _lvl('notif_ping'), 'notif_ping', fin=0.0002)


def _mech_key(r, space=False):
    """One mechanical key: bottom-out thock (keycap + plate), spring ping, upstroke click ~75-120 ms later."""
    f1 = r.uniform(380.0, 520.0) * (0.8 if space else 1.0)
    press = _click(0.12, r, (1500, 7500), 0.0011, [(f1, 0.022, 0.6), (f1 * 2.31, 0.012, 0.3),
                                                   (r.uniform(2100.0, 2700.0), 0.006, 0.25)],
                   low=(170.0 if space else 210.0, 0.02, 0.6))
    press = press + modal(0.12, [r.uniform(4300.0, 5200.0), r.uniform(6400.0, 7100.0)], [0.03, 0.02], [0.05, 0.03], r)
    if space:
        press = press + _pad(_click(0.05, r, (1200, 5000), 0.002, [(r.uniform(900.0, 1200.0), 0.01, 0.2)]) * 0.5,
                             len(press))
    rel = _click(0.05, r, (2500, 9000), 0.0009, [(f1 * 3.1, 0.006, 0.25)]) * 0.4
    return press, rel, r.uniform(0.075, 0.12)


@_synth('ui', 0.001, 1.7, -29.0, 'mechanical keyboard burst: n thocky keys (bottom-out, spring ping, upstroke click), '
        'human timing, a spacebar every ~6 keys', 'prompt typing, editor at work', send=-18)
def keyboard_burst(seed=0, n=12, cps=10.0):
    """Mechanical typing (n keys at ~cps). hit = 0.001 s (the first key)."""
    r = _rng(seed, 'keyboard_burst')
    n = max(1, int(n))
    cps = max(1.0, float(cps))
    d = n / cps * 1.7 + 0.5
    out = np.zeros((_n(d), 2))
    t0 = 0.001
    for k in range(n):
        space = (k % 6 == 5) and r.random() < 0.8
        x, rel, rdt = _mech_key(r, space)
        g = 1.0 if k == 0 else r.uniform(0.7, 0.95)
        pk = 0.0 if space else r.uniform(-0.3, 0.3)
        _add(out, pan(x * g, pk), t0)
        _add(out, pan(rel * g, pk), t0 + rdt)
        t0 += (1.0 / cps) * float(np.clip(r.lognormal(0.0, 0.3), 0.55, 1.8)) * (1.5 if space else 1.0)
        if t0 > d - 0.35:
            break
    st = reverb(out, 'room', wet_db=-19.0)
    return _done(st, 0.001, _lvl('keyboard_burst'), 'keyboard_burst', fin=0.0002)


@_synth('ui', 0.001, 0.4, -31.0, 'mouse micro-switch: sharp press + plastic body + low tock, softer release 70-95 ms '
        'later; double=1 adds a second click 0.14-0.18 s on', 'cursor clicks in the NLE UI', send=-18)
def mouse_click(seed=0, double=0):
    """Mouse click (~0.4 s). hit = 0.001 s."""
    r = _rng(seed, 'mouse_click')
    dbl = 1 if int(double) else 0
    d = 0.5 if dbl else 0.26
    out = np.zeros(_n(d))

    def press(t0, g):
        x = _click(0.06, r, (2200, 9500), 0.0006, [(2050.0 * r.uniform(0.97, 1.03), 0.006, 0.45), (3610.0, 0.004, 0.3),
                                                   (6100.0, 0.002, 0.15)], low=(240.0, 0.007, 0.4))
        _add(out, x * g, t0)
        rel = _click(0.04, r, (3000, 10000), 0.0005, [(2850.0, 0.004, 0.3), (6600.0, 0.002, 0.15)]) * 0.5
        _add(out, rel * g, t0 + r.uniform(0.07, 0.095))
    press(0.001, 1.0)
    if dbl:
        press(0.001 + r.uniform(0.14, 0.18), 0.92)
    st = reverb(decorrelate(out, r, 0.1), 'room', wet_db=-23.0)
    return _done(st, 0.001, _lvl('mouse_click'), 'mouse_click', fin=0.0002)


@_synth('ui', 0.001, 4.0, -22.0, 'render complete: a rising D-major arpeggio D5 F#5 A5 D6 of soft FM bells (75 ms apart, '
        'the last one long) + sparkle, plate; pitch transposes (0.7937 = Bb major)', 'render bar hits 100 %', send=-20)
def render_complete(seed=0, pitch=1.0):
    """Render-complete ding (~4 s). hit = 0.001 s (the first note)."""
    r = _rng(seed, 'render_complete')
    p = max(0.1, float(pitch))
    d = 2.7
    out = np.zeros((_n(d), 2))
    for k, (t0, m, a) in enumerate(((0.001, 74, 0.8), (0.076, 78, 0.75), (0.151, 81, 0.8), (0.226, 86, 1.0))):
        f = midi_hz(m) * p
        L = d - t0
        x = fm_bell_os(L, f, ratio=2.0, index=0.9, tau=1.5 if k == 3 else 0.5, tau_index=0.05, attack=0.002)
        x = x + 0.25 * fm_bell_os(L, 2.0 * f, ratio=1.0, index=0.3, tau=0.25, tau_index=0.05, attack=0.002)
        _add(out, pan(x * a, -0.3 + 0.2 * k), t0)
    _add(out, _grains(1.4, r, 40, 3500.0, 11000.0, 0.02, 0.15, density=lambda q: np.exp(-q * 3.0)) * 0.06, 0.23)
    st = reverb(out, 'plate', wet_db=-11.0, send_hp=300.0)
    return _done(st, 0.001, _lvl('render_complete'), 'render_complete', fin=0.0002)


_VOW = dict(a=(730, 1090, 2440), e=(530, 1840, 2480), i=(270, 2290, 3010), o=(570, 840, 2410), u=(300, 870, 2240))


def _scrub_source(d, r):
    """'Edit content' under the playhead: a voice-like formant babble (band-limited glottal harmonics, ~5 syllables / s,
    fricatives) over a soft D-minor beat. Mono, peak 1, low-passed at 6 kHz."""
    N = _n(d)
    t = np.arange(N) / SR
    fr = np.arange(0.0, d + 0.01, 0.005)
    f0 = 124.0 * (1 + 0.1 * np.sin(TWO_PI * 0.8 * fr + r.uniform(0, TWO_PI))) * (1 - 0.05 * fr / max(d, 1e-3))
    F = np.zeros((len(fr), 3))
    voiced = np.zeros(len(fr))
    fric = np.zeros(len(fr))
    tt = 0.04
    while tt < d:
        cl, vl = r.uniform(0.03, 0.07), r.uniform(0.08, 0.17)
        vw = _VOW['aeiou'[int(r.integers(0, 5))]]
        a, b, c = np.searchsorted(fr, [tt, tt + cl, tt + cl + vl])
        if r.random() < 0.45:
            fric[a:b] = r.uniform(0.4, 1.0)
        voiced[b:c] = 1.0
        F[a:c] = vw
        tt += cl + vl + (r.uniform(0.15, 0.35) if r.random() < 0.15 else r.uniform(0.0, 0.04))
    F[F[:, 0] == 0] = _VOW['a']
    voiced = np.convolve(voiced, np.ones(3) / 3, mode='same')
    base = TWO_PI * np.cumsum(np.interp(t, fr, f0)) / SR
    voice = np.zeros(N)
    for k in range(1, 40):
        fk = k * f0
        e = np.zeros(len(fr))
        for j, bw in enumerate((80.0, 100.0, 140.0)):
            e += (1.0, 0.7, 0.4)[j] * np.exp(-0.5 * ((fk - F[:, j]) / bw) ** 2)
        e = (e + 0.03) * k ** -0.6 * voiced * np.clip((4800.0 - fk) / 500.0, 0, 1)
        if e.max() > 0:
            voice += np.interp(t, fr, e) * np.sin(k * base)
    sss = _unit(bp(r.standard_normal(N), 3500, 7000)) * np.interp(t, fr, fric) * 0.25
    music = (harm(np.full(N, 146.83), [1, .4, .2, .1], fmax=3000.0) + harm(np.full(N, 174.61), [.7, .3, .15], fmax=3000.0)
             + harm(np.full(N, 220.0), [.6, .25, .1], fmax=3000.0)) * 0.1
    beat = 60.0 / 90.0
    for kb in range(int(max(0.0, d - 0.3) / beat) + 1):
        _add(music, _thump(0.3, 50.0, 90.0, 0.02, 0.09, r, drive=2.0, noise=0.2) * 0.5, kb * beat)
    x = voice / (np.max(np.abs(voice)) + 1e-9) + sss + music
    return lp(x / (np.max(np.abs(x)) + 1e-9), 6000.0, 4)


@_synth('ui', 0.0, 1.8, -31.0, 'NLE audio-scrub chatter: the playhead dragged (content ~speed x, a short backward flick), '
        'one 39 ms grain of the clip per 30 fps frame (reversed when moving back), drag friction, mouse-up at duration',
        'playhead scrub / J-K-L shuttle (cue align=start at the drag start)', send=-18)
def timeline_scrub(seed=0, duration=1.5, speed=2.0):
    """Timeline scrub (duration s + 0.3 s). hit = 0 (the drag starts: cue it with align='start')."""
    r = _rng(seed, 'timeline_scrub')
    D = max(0.2, float(duration))
    sp = max(0.2, float(speed))
    fps = 30.0
    nfr = int(math.ceil(D * fps))
    kn = 6
    knots = r.uniform(0.35, 1.0, kn) * sp
    knots[int(r.integers(2, kn))] *= -0.5
    pf = np.linspace(0, 1, nfr)
    vel = np.interp(pf, np.linspace(0, 1, kn), knots) * np.sin(0.5 * np.pi * np.clip(pf / 0.12, 0.02, 1))
    pos = 0.6 + np.cumsum(vel / fps)
    pos -= min(0.0, pos.min() - 0.1)
    content = _scrub_source(float(pos.max()) + 0.4, r)
    gl = 1.0 / fps + 0.006
    ng = _n(gl)
    win = _gate(np.arange(ng) / SR, 0.0, gl, 0.003)
    out = np.zeros(_n(D + 0.15))
    for i in range(nfr):
        if abs(vel[i]) < 0.05:
            continue
        a = _n(pos[i])
        g = _pad(content[a:a + ng], ng) if vel[i] > 0 else _pad(content[max(0, a - ng):a][::-1], ng)
        _add(out, g * win * min(1.0, abs(vel[i]) / 0.5) ** 0.5, i / fps)
    t = np.arange(len(out)) / SR
    out += (_unit(bp(r.standard_normal(len(out)), 600, 3000)) * np.interp(t, np.arange(nfr) / fps, np.abs(vel))
            * _gate(t, 0.0, D, 0.03) * 0.01)
    _add(out, _click(0.04, r, (2800, 10000), 0.0005, [(2900, 0.004, 0.3)]) * 0.3, D)
    st = reverb(decorrelate(out, r, 0.2), 'room', wet_db=-20.0)
    return _done(st, 0.0, _lvl('timeline_scrub'), 'timeline_scrub', keep_until=D, fin=0.001)


def _clock_tick1(r, tock=False):
    k = 0.84 if tock else 1.0
    x = _click(0.08, r, (2200, 9500), 0.0006, [(2450.0 * k, 0.010, 0.5), (3870.0 * k, 0.007, 0.35),
                                               (5610.0 * k, 0.004, 0.2)], low=(620.0 * k, 0.012, 0.25))
    return x + modal(0.08, [1150.0 * k, 1720.0 * k], [0.012, 0.008], [0.2, 0.1], r)


@_synth('ui', 0.001, 5.8, -29.0, 'clock ticking: escapement tick / tock (metal modes + wooden case), n ticks at bpm; '
        'accel > 1 shortens every interval by that factor', 'deadline pressure (accel 1.05-1.1), held breath (n=1)',
        send=-18)
def clock_tick(seed=0, n=6, bpm=60.0, accel=1.0):
    """Clock ticks (~5.8 s at the defaults). hit = 0.001 s (the first tick)."""
    r = _rng(seed, 'clock_tick')
    n = max(1, int(n))
    iv = 60.0 / max(1.0, float(bpm))
    ac = max(0.5, float(accel))
    times = [0.001]
    for k in range(1, n):
        times.append(times[-1] + iv / ac ** k)
    x = np.zeros(_n(times[-1] + 0.8))
    for k, tk in enumerate(times):
        _add(x, _clock_tick1(r, k % 2 == 1) * r.uniform(0.9, 1.0), tk)
    st = reverb(decorrelate(x, r, 0.15), 'studio', wet_db=-15.0)
    return _done(st, 0.001, _lvl('clock_tick'), 'clock_tick', fin=0.0002)


# =============================================================================================== TEXTURES
@_synth('texture', 'end', 8.8, -26.0, 'tension drone: a slowly beating harmonic stack on the root (1, 2, 3, 4, 6, 8, 12 x: '
        'D and A only), a creeping whine two octaves up, a rising air band, crescendo to the hit, 0.8 s release',
        'under the problem / setup section (align start, its END on the turn)', send=-24)
def tension_drone(seed=0, duration=8.0, root=36.71):
    """Tension drone (duration s + 0.8 s release). hit = duration exactly (the crescendo's peak, the last moment)."""
    r = _rng(seed, 'tension_drone')
    D = max(0.5, float(duration))
    f0 = max(20.0, float(root))
    d = D + 0.8
    t = _t(d)
    N = len(t)
    p = np.clip(t / D, 0, 1)
    after = np.where(t <= D, 1.0, np.exp(-(t - D) / 0.18))
    cres = (0.15 + 0.85 * p ** 1.8) * after
    st = np.zeros((N, 2))
    for k, a in ((1, 1.0), (2, 0.8), (3, 0.55), (4, 0.45), (6, 0.28), (8, 0.16), (12, 0.08)):
        if f0 * k > 16000.0:
            continue
        for side, det in ((-1, -0.11), (1, 0.13)):
            st += pan(np.sin(TWO_PI * (f0 * k + det * k ** 0.5) * t + r.uniform(0, TWO_PI)) * a, 0.35 * side)
    st *= 0.18
    st += _st(osc(f0 * 16.0 * 2.0 ** (0.5 / 12.0 * p ** 2)) * 0.02 * p ** 2.5)
    nz = noise_band(d, r, lambda q: 200.0 * (2500.0 / 200.0) ** (np.clip(q * d / D, 0, 1) ** 2), 1.0, width=0.6)
    st = (st + 0.25 * _pad(nz, N) * (p ** 2.2)[:, None]) * cres[:, None]
    st = shape(st / (np.max(np.abs(st)) + 1e-12) * 0.9, 1.4)
    st = benhance(st, 0.5, fc=95.0, band=(150.0, 600.0), drive=4.0)
    st = reverb(_taper(st, sec=0.2), 'dark', wet_db=-9.0, send_hp=80.0)[:_n(d)]
    st = _fade(st, 0.0, 0.25)
    return _done(st, D, _lvl('tension_drone'), 'tension_drone', keep_until=D)


@_synth('texture', 'end', 4.1, -30.0, 'laptop fan spinning up under load: 37-blade tone rising 555 Hz -> 3.2 kHz, motor '
        'hum, air rising, coil whine; full speed on the hit, then a 0.4 s fade', '"render shuru": the machine working '
        'hard (cue align=start at the render start)', send=-20)
def laptop_fan(seed=0, duration=3.5):
    """Fan spin-up (duration s + 0.45 s). hit = duration (full speed: the END of the motion)."""
    r = _rng(seed, 'laptop_fan')
    D = max(0.3, float(duration))
    d = D + 0.45
    t = _t(d)
    N = len(t)
    u = np.clip(t / D, 0, 1)
    spin = 1.0 - (1.0 - u) ** 2.2
    after = np.where(t <= D, 1.0, np.clip(1.0 - (t - D) / 0.4, 0, 1) ** 1.5)
    rpm = 900.0 + 4300.0 * spin
    tone = harm(37.0 * rpm / 60.0, [1.0, 0.35, 0.15], fmax=14000.0, rng=r) * 0.05 * spin ** 1.5
    motor = harm(4.0 * rpm / 60.0, [1.0, 0.4], fmax=3000.0, rng=r) * 0.02 * spin
    whine = osc(9000.0 + 1500.0 * spin) * 0.004 * spin
    air = noise_band(d, r, lambda q: 300.0 + 3500.0 * (1.0 - (1.0 - np.clip(q * d / D, 0, 1)) ** 2.2), 1.2, width=0.5)
    st = (_pad(air, N) * (0.04 + 0.30 * spin ** 2)[:, None] + _st(tone + motor + whine)) * after[:, None]
    st = reverb(st, 'room', wet_db=-16.0)
    return _done(st, D, _lvl('laptop_fan'), 'laptop_fan', keep_until=D)


def _proj_click(r, accent):
    x = _click(0.03, r, (1800, 7000), 0.0013, [(1850.0 * r.uniform(0.96, 1.04), 0.006, 0.4), (3250.0, 0.004, 0.25)],
               low=(150.0, 0.006, 0.3 if accent else 0.18))
    return x * (1.0 if accent else 0.6)


@_synth('texture', 'end', 2.9, -29.0, 'film projector start: switch click, motor + claw / shutter clatter spinning up to '
        '24 fps (2 events per frame), hum, belt whine, fan; at speed on the hit, 0.25 s run-out', 'flashback / "film" '
        'opener (cue align=start)', send=-18)
def projector_start(seed=0, duration=2.5):
    """Projector spin-up (duration s + 0.3 s). hit = duration (24 fps reached: the END of the spin-up)."""
    r = _rng(seed, 'projector_start')
    D = max(0.3, float(duration))
    d = D + 0.3
    t = _t(d)
    N = len(t)
    s = _smoothstep(np.clip(t / D, 0, 1)) ** 0.8
    ev = np.cumsum(48.0 * s) / SR
    idx = np.nonzero(np.diff(np.floor(ev)) > 0)[0] + 1
    x = np.zeros(N)
    for j, i in enumerate(idx):
        if t[i] > D + 0.25:
            break
        _add(x, _proj_click(r, j % 2 == 0) * (0.35 + 0.65 * s[i]) * r.uniform(0.85, 1.0), t[i])
    x += harm(48.0 * s + 1e-3, [1, 0.6, 0.35, 0.2, 0.12], fmax=8000.0, rng=r) * 0.1 * s
    x += osc(880.0 * s + 1e-3) * 0.02 * s ** 2
    x += tvf(_unit(lp(colored(N, r, -2.0), 3000, 2)), lp_mask(lambda q: 300.0 + 1700.0 * np.interp(q * d, t, s))) * 0.05 * s
    _add(x, _click(0.05, r, (1500, 7000), 0.002, [(1200, 0.01, 0.4)], low=(150.0, 0.01, 0.5)) * 0.8, 0.001)
    x *= np.where(t <= D, 1.0, np.clip(1 - (t - D) / 0.25, 0, 1) ** 2)
    st = reverb(decorrelate(x, r, 0.3), 'room', wet_db=-18.0)
    return _done(st, D, _lvl('projector_start'), 'projector_start', keep_until=D)


TABLA_STROKES = ('na', 'tin', 'ta', 'ge', 'ke', 'dha', 'dhin')
_STROKE_DB = dict(na=0.0, tin=-2.0, ta=-1.0, ge=-1.0, ke=-3.0, dha=1.0, dhin=0.0)   # natural balance re Mmax -23


def _dayan(r, sa, kind):
    d = 0.8
    t = _t(d)
    N = len(t)
    v = r.uniform(0.88, 1.12)
    if kind == 'tin':
        x = modal(d, [sa * k for k in (1, 2, 3, 4)], [.45 * v, .2 * v, .12 * v, .08 * v],
                  list(np.array([1, .3, .18, .08]) * r.uniform(0.85, 1.15, 4)), r, contact=0.0006)
        return x + _unit(hp(r.standard_normal(N), 3000)) * _ar(t, 0.0002, 0.002) * 0.12
    damp = 0.3 if kind == 'ta' else 1.0
    x = modal(d, [sa * k for k in (1, 2, 3, 4, 5, 2.95)], [.30 * v * damp, .20 * v * damp, .14 * v * damp,
                                                           .09 * v * damp, .06 * v * damp, .02],
              list(np.array([1, .62, .46, .30, .16, .12]) * r.uniform(0.85, 1.15, 6)), r, contact=0.0003)
    x = x + _unit(hp(r.standard_normal(N), 3000)) * _ar(t, 0.0002, 0.0025) * 0.3
    if kind == 'ta':
        x = x + _unit(bp(r.standard_normal(N), 600.0, 4000.0)) * _ar(t, 0.0003, 0.006) * 0.45
    return x


def _bayan(r, p, kind):
    d = 1.2
    t = _t(d)
    N = len(t)
    if kind == 'ke':
        return (_unit(bp(r.standard_normal(N), 200.0, 1500.0)) * _ar(t, 0.0005, 0.015) * 0.5
                + np.sin(TWO_PI * 120.0 * p * t) * _ar(t, 0.001, 0.025) * 0.4)
    f = (88.0 * r.uniform(0.97, 1.03) + 42.0 * r.uniform(0.85, 1.15) * (1 - np.exp(-t / (0.07 * r.uniform(0.85, 1.15))))) * p
    ph = TWO_PI * np.cumsum(f) / SR
    x = _taper((np.sin(ph) + 0.18 * np.sin(2 * ph)) * _ar(t, 0.002, 0.30 * r.uniform(0.85, 1.15)), 0.35)
    x = benhance(shape(x * 0.8, 1.5), 0.8, fc=140.0, band=(180.0, 700.0), drive=4.0)
    return x + _unit(hp(r.standard_normal(N), 700)) * _ar(t, 0.0003, 0.004) * 0.25


@_synth('texture', 0.002, 1.5, -23.0, 'tabla stroke na / tin / ta / ge / ke / dha / dhin: dayan modes 1-5 x Sa (D4 x '
        'pitch) + rim click, bayan 88 -> 130 Hz wrist glide (ge), dha = na + ge, dhin = tin + ge', 'desi accents on beats, '
        'tonal payoff hits', send=-18)
def tabla_hit(seed=0, stroke='na', pitch=1.0):
    """One tabla stroke (~1.5 s). hit = 0.002 s. Sa = 293.66 Hz x pitch (the bayan moves with pitch too)."""
    s = str(stroke).lower()
    if s not in TABLA_STROKES:
        raise ValueError('tabla_hit stroke must be one of %s (got %r)' % (', '.join(TABLA_STROKES), stroke))
    r = _rng(seed, 'tabla_hit_' + s)
    p = max(0.25, float(pitch))
    sa = 293.66 * p * r.uniform(0.998, 1.002)
    h = 0.002
    x = np.zeros(_n(1.25))
    if s in ('na', 'tin', 'ta'):
        _add(x, _dayan(r, sa, s), h)
    elif s in ('ge', 'ke'):
        _add(x, _bayan(r, p, s), h)
    else:
        _add(x, 0.6 * _dayan(r, sa, 'na' if s == 'dha' else 'tin'), h)
        _add(x, 0.55 * _bayan(r, p, 'ge'), h)
    st = reverb(_st(x), 'studio', wet_db=-17.0)
    return _done(st, h, _lvl('tabla_hit') + _STROKE_DB[s], 'tabla_hit', fin=0.0002)


TARAF = (62, 69, 74, 81, 86)                    # sympathetic strings on Sa / Pa: D4 A4 D5 A5 D6


@_synth('texture', 0.002, 4.4, -24.0, 'sitar pluck: band-limited harmonic string with the jawari buzz (a brightness peak '
        'sweeping ~6 -> 1.2 kHz over the first 0.5 s), meend (pitch bend in semitones, 0.15-0.45 s), taraf strings on '
        'Sa / Pa ringing in sympathy', 'a one-note tonal sting in key (note=62 = D4)', send=-18)
def sitar_pluck(seed=0, note=62, meend=0.0, dur=4.0):
    """Sitar pluck (dur s + room). hit = 0.002 s (the mizrab)."""
    r = _rng(seed, 'sitar_pluck')
    D = max(0.3, float(dur))
    f0 = midi_hz(float(note))
    mb = float(meend)
    t = _t(D)
    N = len(t)
    h = 0.002
    f = f0 * 2.0 ** (mb / 12.0 * _smoothstep((t - 0.15) / 0.3))
    base = TWO_PI * np.cumsum(f) / SR
    fj = 1200.0 + 4800.0 * np.exp(-t / 0.18)
    tau0 = 1.6
    out = np.zeros(N)
    for k in range(1, int(11000.0 / f0) + 1):
        fk = k * f
        a = k ** -0.85 * np.exp(-t * (1.0 + 0.12 * k) / tau0)
        jaw = 1.0 + 2.5 * np.exp(-0.5 * (np.log2(np.maximum(fk, 1.0) / fj) / 0.55) ** 2)
        out += a * jaw * np.clip((15000.0 - fk) / 2000.0, 0, 1) * np.sin(k * base)
    out *= _ar(t, 0.0015, 1e9, h)
    out += _unit(bp(r.standard_normal(N), 1500.0, 7000.0)) * _ar(t, 0.0003, 0.006, h) * 0.3
    out = shape(out / (np.max(np.abs(out)) + 1e-12) * 0.9, 1.3)
    st = pan(out, -0.15)
    for j, m in enumerate(TARAF):
        ft = midi_hz(m)
        exc = sum(math.exp(-0.5 * (1200.0 * math.log2(k * f0 / ft) / 25.0) ** 2) for k in range(1, 11))
        if exc < 0.05:
            continue
        ring = (np.sin(TWO_PI * ft * t + r.uniform(0, TWO_PI)) + np.sin(TWO_PI * ft * 1.0012 * t + r.uniform(0, TWO_PI)))
        ring *= (1.0 - np.exp(-np.maximum(t - h, 0) / 0.12)) * np.exp(-t / 1.8) * min(1.0, exc) * 0.06
        st += pan(ring, 0.7 * (-1) ** j)
    st = _taper(st, sec=min(0.4, 0.2 * D))
    st = reverb(st, 'studio', wet_db=-14.0)
    return _done(st, h, _lvl('sitar_pluck'), 'sitar_pluck', fin=0.0002)


@_synth('texture', 'peak', 3.5, -26.0, 'harmonium swell: two pulse reeds per note at +-2.5 cents (equal, phase-aligned at '
        'the peak), bellows (t / tp)^1.6 up to the peak at 0.72 x duration, -6 dB by duration, 0.6 s release, 0.9 Hz '
        'pumping, 3.2 kHz low-pass, reed air; room', 'emotional desi swell (yaadein / younger-self moods), drones',
        send=-20)
def harmonium_swell(seed=0, duration=2.5, notes=(50, 57, 62)):
    """Harmonium swell (duration s + 0.6 s release + room). hit = 0.72 x duration (the bellows peak; the swell starts
    at sample 0 and its 10 ms RMS is at its maximum on the hit). notes: MIDI numbers (any chord; default Sa-Pa-Sa D3 A3 D4)."""
    r = _rng(seed, 'harmonium_swell')
    D = max(0.2, float(duration))
    if np.ndim(notes) == 0:
        notes = (notes,)
    ns = [float(m) for m in notes] or [62.0]
    tp = 0.72 * D
    rel = 0.6
    t = _t(D + rel)
    N = len(t)
    fall_tau = (D - tp) / math.log(2.0)
    env = np.where(t <= tp, np.clip(t / tp, 0, 1) ** 1.6, np.exp(-np.maximum(t - tp, 0) / fall_tau))
    env *= np.where(t <= D, 1.0, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - D) / rel, 0, 1)))
    env *= 1.0 + 0.06 * np.cos(TWO_PI * 0.9 * (t - tp))
    duty = 0.3
    st = np.zeros((N, 2))
    for j, m in enumerate(ns):
        fc = midi_hz(m)
        phi = r.uniform(0, TWO_PI)
        for side, cents in ((-1, -2.5), (1, 2.5)):
            f = fc * 2.0 ** (cents / 1200.0)
            base = TWO_PI * f * (t - tp) + phi                  # both reeds of a note in phase at the peak
            y = np.zeros(N)
            for k in range(1, int(4000.0 / f) + 1):
                g = min(1.0, (4000.0 - k * f) / 400.0)
                y += math.sin(math.pi * k * duty) / k * g * np.sin(k * base)
            st += pan(y, 0.25 * side)
    st /= max(1, len(ns))
    st = lp(st * env[:, None], 3200.0, 2)
    air = noise_band(D + rel, r, 6000.0, 1.2, width=0.6)
    st = st + 0.006 * _pad(air, N) * env[:, None]
    st = reverb(st, 'room', wet_db=-14.0)
    return _done(st, tp, _lvl('harmonium_swell'), 'harmonium_swell', keep_until=D)


@_synth('texture', 0.08, 4.4, -24.0, 'synthetic crowd "ooh": n voices (band-limited glottal saws through /u/-/o/ '
        'formants, vibrato, a pitch rise and fall), onsets in the first 60 ms, hall; a fallback only',
        'reaction beats when no real crowd sample fits (prefer crowd_ahh_real / crowd_ooh_real)', send=-16)
def crowd_ooh(seed=0, n=24):
    """Synthetic crowd ooh (~4.4 s). hit = 0.08 s (the swell)."""
    r = _rng(seed, 'crowd_ooh')
    V = max(1, int(n))
    d = 2.8
    t = _t(d)
    N = len(t)
    out = np.zeros((N, 2))
    for v in range(V):
        f0 = r.uniform(105.0, 250.0)
        on = r.uniform(0.0, 0.06)
        pk = on + r.uniform(0.06, 0.22)
        tail = r.uniform(0.7, 1.4)
        vib = 1.0 + 0.012 * np.sin(TWO_PI * r.uniform(4.5, 6.5) * t + r.uniform(0, TWO_PI))
        contour = 1.0 + 0.10 * np.exp(-0.5 * ((t - pk - 0.25) / 0.35) ** 2) - 0.05 * np.clip((t - pk) / tail, 0, 1)
        src = saw(f0 * vib * contour, r.uniform(0, 1))
        vw = r.uniform(0, 1)
        F1, F2, F3 = 320.0 + 200.0 * vw, 820.0 + 40.0 * vw, 2300.0 + 100.0 * vw
        y = reson(src, F1, 5.0) + 0.5 * reson(src, F2, 6.0) + 0.12 * reson(src, F3, 8.0)
        y = y + _unit(bp(r.standard_normal(N), 300.0, 3000.0)) * 0.05
        e = np.where(t < pk, 0.5 - 0.5 * np.cos(np.pi * np.clip((t - on) / max(pk - on, 1e-3), 0, 1)),
                     np.exp(-(t - pk) / tail))
        out += pan(_taper(y * e, 0.15), r.uniform(-0.8, 0.8)) * r.uniform(0.5, 1.0)
    out = reverb(out / V, 'hall', wet_db=-9.0, rt60=1.8)
    return _done(out, 0.08, _lvl('crowd_ooh'), 'crowd_ooh')


# =============================================================================================== BEDS (seamless loops)
def _bed_out(x, name, ceiling=-1.4):
    """Finish a seamless loop: normalised to REF LUFS integrated; when its true peak would pass the -1 dBTP cap (thunder
    cracks, droplets), a circular 4x true-peak lookahead limiter shaves the peaks first, so the loop keeps its -20 LUFS
    and stays seamless. Then sfx_jawad._bed_done (circular guard filter, DC, loudness, TP cap)."""
    x = np.asarray(x, dtype=np.float64)
    for _ in range(5):
        x = x * undb(REF - A.loudness(x))
        if A.true_peak(x) <= ceiling + 0.25:
            break
        x = x * _circ(lambda z: A.limiter_gain(z, ceiling, release=0.05), x, _n(0.25))[:, None]
    return _bed_done(x, name, 0.0)


@_synth('bed', 'loop', 24.0, -20.0, 'dark storytelling floor: drone on D1 D2 A2 D3 (+ faint Eb3, F3, A3 breathing in '
        'and out), slow beating, dark air, hall; seamless loop', 'dark storytelling floor under hooks and builds')
def dark_drone(seed=0, dur=24.0):
    """Seamless dark drone loop (dur s), -20 LUFS integrated. hit = 0."""
    r = _rng(seed, 'dark_drone')
    dur = max(2.0, float(dur))
    L = _n(dur)
    tl = np.arange(L) / SR
    x = np.zeros((L, 2))
    for f, a in ((36.71, 1.0), (73.42, 0.75), (110.0, 0.55), (146.83, 0.5), (155.56, 0.05), (174.61, 0.07),
                 (220.0, 0.12)):
        for c, det in ((0, -0.07), (1, 0.09)):
            fq = _cycles(f + det, dur)
            lfo = 1.0 + (0.45 if a < 0.1 else 0.2) * _periodic_lfo(tl, dur, r, 3)
            x[:, c] += a * np.sin(TWO_PI * fq * tl + r.uniform(0, TWO_PI)) * lfo

    def mask(tl_, f):
        lf = np.log2(np.maximum(f, 8.0))[None, :]
        b = 0.5 + 0.5 * np.sin(TWO_PI * 2 * tl_ / dur + 1.3)[:, None]
        low = np.exp(-0.5 * ((lf - np.log2(110.0)) / 0.9) ** 2)
        air = 0.05 * (0.6 + 0.4 * b) * np.exp(-0.5 * ((lf - np.log2(4200.0)) / 0.6) ** 2)
        return low + air
    nz = _loop_mask_noise(L, r, mask, corr=0.5)
    x = x / (A._rms(x) + 1e-12) * 0.25 + nz / (A._rms(nz) + 1e-12) * 0.05
    x = _circ(lambda z: shape(z, 1.3), x, _n(0.05))
    x = reverb_circular(x, 'hall', wet_db=-8.0)
    return _bed_out(x, 'dark_drone')


def _impulse_bed(L, r, rate, kernel, spread=0.7):
    """Seamless bed of random impulses (rate per second, lognormal sizes, random pans) convolved circularly with a short
    kernel (droplets, distant ticks)."""
    n = int(rate * L / SR)
    out = np.zeros((L, 2))
    pos = r.integers(0, L, n)
    amp = np.minimum(r.lognormal(0.0, 0.45, n), 3.0)
    pn = r.uniform(-spread, spread, n)
    th = (pn + 1) * (np.pi / 4)
    np.add.at(out[:, 0], pos, amp * np.sqrt(2) * np.cos(th))
    np.add.at(out[:, 1], pos, amp * np.sqrt(2) * np.sin(th))
    K = np.zeros(L)
    K[:len(kernel)] = kernel
    Kf = np.fft.rfft(K)
    return np.stack([np.fft.irfft(np.fft.rfft(out[:, c]) * Kf, n=L) for c in range(2)], 1)


@_synth('bed', 'loop', 20.0, -20.0, 'night rain on a city: rain wash + droplets dominating 1-12 kHz, gutter drips, distant '
        'traffic rumble and car swishes, outdoor space; seamless loop', 'night edit-suite mood, monsoon window')
def rain_city_night(seed=0, dur=20.0):
    """Seamless rain-on-the-city loop (dur s), -20 LUFS integrated. hit = 0."""
    r = _rng(seed, 'rain_city_night')
    dur = max(2.0, float(dur))
    L = _n(dur)
    ph = r.uniform(0, TWO_PI, 2)

    def mask(tl_, f):
        lf = np.log2(np.maximum(f, 20.0))[None, :]
        inten = 0.8 + 0.2 * np.sin(TWO_PI * 2 * tl_ / dur + ph[0])[:, None]
        wash = np.exp(-0.5 * ((lf - np.log2(4500.0)) / 1.3) ** 2)
        low = 0.4 * np.exp(-0.5 * ((lf - np.log2(450.0)) / 1.0) ** 2)
        return inten * (wash + low)
    rain = _loop_mask_noise(L, r, mask, corr=0.2)
    rain = rain / (A._rms(rain) + 1e-12)
    tk = _t(0.004)
    k1 = _unit(bp(r.standard_normal(len(tk)), 2000.0, 9000.0)) * _ar(tk, 0.0001, 0.0007)
    drops = _impulse_bed(L, r, 1100.0, k1, 0.9)
    tk2 = _t(0.06)
    k2 = modal(0.06, [r.uniform(1400.0, 2400.0)], [0.018], [1.0], r, contact=0.0002)
    drips = _impulse_bed(L, r, 0.8, k2, 0.6)
    city = _spec_filter(colored(L, r, -6.0, 30.0, 400.0), lambda f: 1.0 / np.sqrt(1 + (45.0 / np.maximum(f, 1.0)) ** 4))
    city = np.stack([city, np.roll(city, L // 3)], 1)
    cars = np.zeros((L, 2))
    for k in range(max(1, int(round(dur / 7.0)))):
        cd = r.uniform(3.0, 5.0)
        tc = _t(cd)
        sw = noise_band(cd, r, [(0, 500.0), (0.5, 1100.0), (1, 450.0)], 0.9, width=0.4)
        sw = sw * (np.sin(np.pi * tc / cd) ** 2)[:, None]
        _add_wrap(cars, pan(sw, r.uniform(-0.6, 0.6)), r.uniform(0, dur))
    mix = (0.62 * rain + 0.30 * drops / (A._rms(drops) + 1e-12) + 0.10 * drips / (A._rms(drips) + 1e-12)
           + 0.06 * city / (A._rms(city) + 1e-12) + 0.07 * cars / (A._rms(cars) + 1e-12))
    mix = reverb_circular(mix, 'outdoor', wet_db=-10.0)
    return _bed_out(mix, 'rain_city_night')


@_synth('bed', 'loop', 24.0, -20.0, 'desi street: traffic rumble, distant two-tone horns (0.4-1.2 kHz bursts), a 2-stroke '
        'rickshaw passing L -> R, a wordless crowd murmur; no azaan, no music; seamless loop',
        'street / "Karachi-Mumbai" texture through a window')
def desi_city(seed=0, dur=24.0):
    """Seamless desi-street loop (dur s, any length), -20 LUFS integrated. hit = 0."""
    r = _rng(seed, 'desi_city')
    dur = max(4.0, float(dur))
    L = _n(dur)
    tl = np.arange(L) / SR
    ph = r.uniform(0, TWO_PI, 3)

    def tmask(tl_, f):
        lf = np.log2(np.maximum(f, 20.0))[None, :]
        sw = (0.75 + 0.25 * np.sin(TWO_PI * 3 * tl_ / dur + ph[0]) * np.sin(TWO_PI * 2 * tl_ / dur + ph[1]))[:, None]
        rumble = np.exp(-0.5 * ((lf - np.log2(180.0)) / 1.2) ** 2)
        hiss = 0.12 * np.exp(-0.5 * ((lf - np.log2(2200.0)) / 0.8) ** 2)
        return sw * (rumble + hiss)
    traffic = _loop_mask_noise(L, r, tmask, corr=0.4)
    traffic = traffic / (A._rms(traffic) + 1e-12)
    horns = np.zeros((L, 2))
    for k in range(max(2, int(round(dur * 0.42)))):
        f1 = r.uniform(380.0, 1150.0)
        two = r.random() < 0.5
        t0 = r.uniform(0, dur)
        dist = r.uniform(0.2, 1.0)
        for j in range(int(r.integers(1, 4))):
            hd = r.uniform(0.12, 0.5)
            tt = _t(hd)
            f = np.full(len(tt), f1 * (1.26 if (two and j % 2) else 1.0))
            y = harm(f, [1, .6, .45, .3, .2, .12], fmax=9000.0, rng=r) * _gate(tt, 0.0, hd, 0.012)
            y = lp(y, 6000.0 - 4000.0 * dist, 2) * (1.0 - 0.7 * dist)
            _add_wrap(horns, pan(y, r.uniform(-0.8, 0.8)), t0)
            t0 += hd + r.uniform(0.06, 0.2)
    rick = np.zeros((L, 2))
    for k in range(max(1, int(round(dur / 24.0)))):
        rd = r.uniform(4.5, 6.0)
        tt = _t(rd)
        u = tt / rd
        dop = 1.0 + 0.035 * np.cos(np.pi * u)                      # approaching (sharp) -> receding (flat)
        fire = 44.0 * r.uniform(0.95, 1.05) * dop
        eng = hp(harm(fire, [.25, .5, .8, 1.0, .9, .8, .6, .5, .4, .3, .22, .16, .12, .09], fmax=6000.0, rng=r), 90.0, 2)
        putt = _unit(bp(r.standard_normal(len(tt)), 300.0, 2500.0)) * (0.5 + 0.5 * np.sin(TWO_PI * np.cumsum(fire) / SR))
        y = (eng + 0.35 * putt) * np.sin(np.pi * u) ** 2
        y = tvf(y, lp_mask(lambda q: 900.0 + 3500.0 * np.sin(np.pi * q) ** 2))
        _add_wrap(rick, pan(y, np.clip(-0.8 + 1.6 * u, -1, 1)), r.uniform(0, dur))
    mur = np.zeros((L, 2))
    for v in range(12):
        w = _spec_filter(r.standard_normal(L), lambda f: np.exp(-0.5 * (np.log2(np.maximum(f, 20.0) / r.uniform(500.0, 1100.0)) / 0.7) ** 2))
        syl = np.zeros(L)
        for k in range(1, 6):
            syl += r.uniform(0.2, 1.0) * np.sin(TWO_PI * _cycles(r.uniform(2.5, 5.5), dur) * tl + r.uniform(0, TWO_PI))
        syl = np.maximum(syl / (np.max(np.abs(syl)) + 1e-12), 0.0) ** 1.5
        mur += pan(w * syl, r.uniform(-0.9, 0.9)) * r.uniform(0.5, 1.0)
    mix = (0.60 * traffic + 0.10 * horns / (A._rms(horns) + 1e-12) + 0.16 * rick / (A._rms(rick) + 1e-12)
           + 0.12 * mur / (A._rms(mur) + 1e-12))
    mix = reverb_circular(mix, 'outdoor', wet_db=-8.0)
    return _bed_out(mix, 'desi_city')


@_synth('bed', 'loop', 16.0, -20.0, "editor's room: two PC fans (broadband + blade tones), 50 Hz mains hum (100 / 200 / "
        '300 Hz), AC airflow, a faint coil whine, slow breathing; seamless loop', "editor's room floor under the NLE world")
def edit_suite(seed=0, dur=16.0):
    """Seamless edit-suite loop (dur s), -20 LUFS integrated. hit = 0."""
    r = _rng(seed, 'edit_suite')
    dur = max(2.0, float(dur))
    L = _n(dur)
    tl = np.arange(L) / SR
    fan = np.stack([colored(L, r, -2.5, 150.0, 6000.0), colored(L, r, -2.5, 150.0, 6000.0)], 1)
    fan[:, 1] = 0.65 * fan[:, 0] + 0.76 * fan[:, 1]
    fan = _spec_filter(fan, lambda f: 0.35 + np.exp(-0.5 * (np.log2(np.maximum(f, 20.0) / 1100.0) / 0.9) ** 2))
    fan = _unit(fan) * (1.0 + 0.08 * _periodic_lfo(tl, dur, r, 2))[:, None]
    blades = np.zeros(L)
    for fb, a in ((118.0, 1.0), (143.3, 0.7)):
        for k, ak in enumerate((1.0, 0.4, 0.2), 1):
            blades += a * ak * np.sin(TWO_PI * _cycles(fb * k, dur) * tl + r.uniform(0, TWO_PI))
    hum = sum(a * np.sin(TWO_PI * fh * tl + r.uniform(0, TWO_PI)) for fh, a in ((100.0, 1.0), (200.0, 0.4), (300.0, 0.25)))
    whine = np.sin(TWO_PI * _cycles(11800.0, dur) * tl)
    flow = _spec_filter(colored(L, r, -5.0, 60.0, 1200.0), lambda f: 1.0 / np.sqrt(1 + (55.0 / np.maximum(f, 1.0)) ** 4))
    mix = (0.32 * fan + _st(0.010 * blades + 0.010 * hum + 0.0015 * whine)
           + 0.20 * np.stack([flow, np.roll(flow, L // 2)], 1))
    mix = reverb_circular(mix, 'room', wet_db=-12.0)
    return _bed_out(mix, 'edit_suite')


@_synth('bed', 'loop', 8.0, -20.0, 'film projector running: claw + shutter clatter at 2 x fps (alternating accents), '
        'motor hum, belt whine, fan; the loop holds a whole number of frames; seamless', 'cinema / flashback bed')
def projector_loop(seed=0, dur=8.0, fps=24.0):
    """Seamless projector loop (~dur s, rounded to whole frames), -20 LUFS integrated. hit = 0."""
    r = _rng(seed, 'projector_loop')
    fps = max(4.0, float(fps))
    n_ev = max(2, int(round(2 * fps * max(1.0, float(dur)))))
    dur = n_ev / (2.0 * fps)
    L = _n(dur)
    tl = np.arange(L) / SR
    x = np.zeros(L)
    per = dur / n_ev
    for j in range(n_ev):
        _add_wrap(x, _proj_click(r, j % 2 == 0) * r.uniform(0.85, 1.0), j * per + r.uniform(0, 0.0008))
    motor = harm(np.full(L, 2.0 * fps), [1, 0.6, 0.35, 0.2, 0.12, 0.08], fmax=8000.0, rng=r) * 0.10
    whine = np.sin(TWO_PI * _cycles(880.0, dur) * tl) * 0.02
    fan = _spec_filter(colored(L, r, -2.0, 150.0, 3000.0), lambda f: 1.0 / np.sqrt(1 + (f / 2000.0) ** 4)) * 0.05
    mix = _circ(lambda z: decorrelate(z, r, 0.3), x + motor + whine + fan, _n(0.1))
    mix = reverb_circular(mix, 'room', wet_db=-12.0)
    return _bed_out(mix, 'projector_loop')


# =============================================================================================== SAMPLES (CC0 / PD)
_FMT = {'.ogg': 'ogg', '.oga': 'ogg', '.wav': 'wav', '.flac': 'flac', '.mp3': 'mp3'}
_DEC = {}


def _lib_file(relpath):
    """Absolute path of a library file, or None when missing or when it would resolve outside LIB."""
    if not relpath or os.path.isabs(relpath) or '..' in relpath.replace('\\', '/').split('/'):
        return None
    root = os.path.realpath(LIB)
    p = os.path.realpath(os.path.join(root, relpath))
    if not (p == root or p.startswith(root + os.sep)) or not os.path.isfile(p):
        return None
    return p


def _read_f32_wav(path):
    from scipy.io import wavfile
    sr, x = wavfile.read(path)
    if sr != SR or x.dtype != np.float32 or x.ndim != 2 or x.shape[1] != 2:
        raise ValueError('%s: unexpected decode (%s Hz, %s, %s)' % (path, sr, x.dtype, x.shape))
    return x


def _decode(relpath):
    """Library file (path relative to LIB) -> float32 (N, 2) at 48 kHz, or None when it is missing / not decodable.
    The file is untrusted data: only ffmpeg reads it (demuxer forced by the extension, file protocol only); the decoded
    copy is cached in SAMPLES48/<relpath>.wav (float32) with a .json stamp (source size + mtime), and in memory.
    Returns a fresh copy (callers may edit it)."""
    src = _lib_file(relpath)
    if src is None:
        return None
    fmt = _FMT.get(os.path.splitext(src)[1].lower())
    if fmt is None:
        return None
    stv = os.stat(src)
    stamp = dict(src=relpath, bytes=stv.st_size, mtime_ns=stv.st_mtime_ns, sr=SR, channels=2, sample='f32')
    key = (relpath, stv.st_size, stv.st_mtime_ns)
    if key in _DEC:
        return _DEC[key].copy()
    cache = os.path.join(SAMPLES48, relpath + '.wav')
    x = None
    try:
        with open(cache + '.json') as fh:
            if json.load(fh) == stamp:
                x = _read_f32_wav(cache)
    except Exception:  # noqa: BLE001  (no cache yet, or a stale / foreign one)
        x = None
    if x is None:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        tmp = '%s.%d.part.wav' % (cache, os.getpid())
        cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-y', '-protocol_whitelist', 'file', '-f', fmt,
               '-i', src, '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', '-f', 'wav', tmp]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=300)
            if res.returncode != 0:
                print('epic_sfx: ffmpeg could not decode %s: %s' % (relpath, res.stderr.decode('utf-8', 'replace')[-300:]))
                return None
            x = _read_f32_wav(tmp)
            os.replace(tmp, cache)
            with open(cache + '.json.part', 'w') as fh:
                json.dump(stamp, fh)
            os.replace(cache + '.json.part', cache + '.json')
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    x = np.ascontiguousarray(x, dtype=np.float32)
    x.setflags(write=False)
    _DEC[key] = x
    return x.copy()


# name: src (candidates, first present wins; Commons originals may be replaced by their MP3 transcode), category,
# kind (oneshot | bed), seg (start s, length s or None = to the end), loop / xfade (beds), fade_out (s), mmax, hit0,
# character, use. Licences: <LIB>/LICENSES.md (written by tools/fetch_sfx_library.py).
SAMPLES = dict(
    rain_real=dict(src=('opengameart/rain_loopable/1.ogg',), category='bed', kind='bed', seg=(2.0, None), loop=20.0,
                   xfade=1.5, mmax=-20.0, character='real rain (CC0, "Rain (loopable)" by Ylmir, OpenGameArt), seamless '
                   '20 s loop', use='night rain, windows, monsoon edit-suite'),
    rain_thunder_real=dict(src=('wikimedia/rain/Rain_and_thunder.ogg', 'wikimedia/rain/Rain_and_thunder.ogg.mp3'),
                           category='bed', kind='bed', seg=(0.5, None), loop=16.0, xfade=1.5, mmax=-20.0,
                           character='real rain with thunder (public domain, Wikimedia Commons), seamless loop',
                           use='storm night, dramatic weather'),
    traffic_real=dict(src=('opengameart/traffic_road/gatve_Varniu.ogg',), category='bed', kind='bed', seg=(8.0, None),
                      loop=16.0, xfade=1.2, mmax=-20.0, character='real high-traffic road (CC0, IgnasD, OpenGameArt), '
                      'mono source widened by a half-loop offset, seamless loop', use='city day, outside the window'),
    applause_real=dict(src=('opengameart/applause_church/applause-clapping-church-crowd-immersive.wav',),
                       category='texture', kind='oneshot', seg=(2.0, 10.0), fade_out=2.0, mmax=-25.0,
                       character='real applause in a large hall (CC0, eXpl0it3r, OpenGameArt)',
                       use='win, "you made it", social proof'),
    applause_build_real=dict(src=('wikimedia/crowd/Slow_starting_applause.ogg',
                                  'wikimedia/crowd/Slow_starting_applause.ogg.mp3'), category='texture', kind='oneshot',
                             seg=(0.0, 12.0), fade_out=2.0, mmax=-25.0,
                             character='real applause that starts slowly and builds (public domain, Wikimedia Commons)',
                             use='the room comes round to you, a build into a win'),
    crowd_cheer_real=dict(src=('opengameart/crowd_shouting/crowd_shouting_0.ogg',), category='texture', kind='oneshot',
                          seg=('loudest', 5.0), fade_out=0.8, mmax=-26.0,
                          character='real crowd shouting / cheering (CC0, StarNinjas, OpenGameArt). CONTAINS ENGLISH '
                          'SPEECH (faster-whisper: "Oh my God, look at that!"): not wordless',
                          use='only where audible English shouting is wanted (a wordless cheer: bijli_chali_gayi_sfx.'
                              'mohalla_cheer re-synthesises this file)'),
    crowd_ahh_real=dict(src=('wikimedia/crowd/Ohhh_ahhh.ogg',), category='texture', kind='oneshot', seg=(0.0, None),
                        fade_out=0.4, mmax=-26.0, character='a few people going "ohhh" / "ahhh" (public domain, starlite, '
                        'PDSounds via Wikimedia Commons)', use='reaction beats, awe'),
    crowd_ooh_real=dict(src=('opengameart/crowd_ooo/oooooooooo.ogg',), category='texture', kind='oneshot', seg=(0.0, None),
                        fade_out=0.3, mmax=-26.0, character='real crowd "ooo" (CC0, Nocturnal_Vanguard, OpenGameArt)',
                        use='a quick crowd reaction'),
    clock_real=dict(src=('wikimedia/clock/Clock_ticking.ogg', 'wikimedia/clock/Clock_ticking.ogg.mp3'), category='ui',
                    kind='oneshot', seg=(0.0, 6.0), fade_out=0.5, mmax=-29.0,
                    character='a real clock ticking (public domain, Wikimedia Commons)', use='real ticks, deadline'),
    typing_modelm_real=dict(src=('wikimedia/typing/Typing_-_Model_M_1986.ogg',
                                 'wikimedia/typing/Typing_-_Model_M_1986.ogg.mp3'), category='ui', kind='oneshot',
                            seg=(0.0, 5.0), fade_out=0.4, mmax=-30.0,
                            character='typing on a 1986 IBM Model M (public domain, Wikimedia Commons): clacky buckling '
                            'springs', use='vintage / clacky typing'),
    bell_impact_real=dict(src=('kenney/impact-sounds/Audio/impactBell_heavy_000.ogg',), category='impact', kind='oneshot',
                          seg=(0.0, None), fade_out=0.15, mmax=-26.0, hit0=True,
                          character='heavy bell impact (CC0, Kenney impact-sounds)', use='deadline bell, alarm hit'),
)


def _sample_src(name):
    """The first present candidate file of a sample sound (relative to LIB), or None."""
    for rel in SAMPLES[name]['src']:
        if _lib_file(rel) is not None:
            return rel
    return None


def _segment(x, seg, seed):
    """Cut seg = (start s | 'loudest', length s | None) from x; seed > 0 shifts the window by 1.37 s per seed (wrapping
    inside the file) so repeats of a cue are different takes."""
    start, length = seg
    n = len(x)
    L = n if length is None else min(n, _n(length))
    if start == 'loudest':
        m = np.square(np.asarray(x, dtype=np.float64)).mean(1)
        c = np.concatenate([[0.0], np.cumsum(m)])
        hop = _n(0.05)
        starts = np.arange(0, max(1, n - L + 1), hop)
        i0 = int(starts[int(np.argmax(c[starts + L] - c[starts]))]) if n > L else 0
    else:
        i0 = min(_n(float(start)), max(0, n - L))
    if seed and n > L:
        i0 = (i0 + int(seed) * _n(1.37)) % (n - L + 1)
    return np.asarray(x[i0:i0 + L], dtype=np.float64)


def _sample_sound(name, seed=0):
    s = SAMPLES[name]
    rel = _sample_src(name)
    x = _decode(rel) if rel else None
    if x is None:
        raise FileNotFoundError('%s: none of %s is in %s (run tools/fetch_sfx_library.py)' % (name, list(s['src']), LIB))
    if s['kind'] == 'bed':
        L, xf = _n(s['loop']), _n(s['xfade'])
        if len(x) < L + xf:                                           # never tile: a short file gets a shorter loop
            L = max(_n(1.0), len(x) - xf)
        start = min(_n(s['seg'][0]), len(x) - L - xf)
        if seed:
            start = (start + int(seed) * _n(1.37)) % max(1, len(x) - L - xf + 1)
        y = _loopify(x[start:start + L + xf], L, xf)
        y = y - y.mean(0)
        if np.corrcoef(y[:, 0], y[:, 1])[0, 1] > 0.98:                # a mono source: widen it, loop-safe
            y = np.stack([y[:, 0], 0.6 * y[:, 0] + 0.8 * np.roll(y[:, 1], L // 2)], 1)
        else:                                                         # a wide stereo source: side -2 dB (fold-down)
            m_, s_ = 0.5 * (y[:, 0] + y[:, 1]), 0.5 * (y[:, 0] - y[:, 1]) * 0.8
            y = np.stack([m_ + s_, m_ - s_], 1)
        return _bed_out(y, name)
    y = _segment(x, s['seg'], seed)
    y = y - y.mean(0)
    on = 0.0 if s.get('hit0') else _onset(y, -30.0, 0.005)
    i0 = max(0, _n(on) - _n(0.010))                                 # keep 10 ms before the onset
    y = y[i0:]
    fo = min(float(s.get('fade_out', 0.3)), 0.4 * len(y) / SR)
    y = _fade(y, 0.002 if i0 > 0 or s['seg'][0] not in (0, 0.0) else 0.0005, fo)
    hit = 0.0 if s.get('hit0') else _onset(y, -20.0, 0.005)
    return _done(y, hit, s['mmax'] - REF, name, fin=0.002)


def _make_sample_fn(name):
    def fn(seed=0):
        return _sample_sound(name, seed)
    fn.__name__ = name
    fn.__qualname__ = name
    fn.__module__ = __name__
    fn.__doc__ = '%s (sample sound): %s. hit = %s.' % (name, SAMPLES[name]['character'],
                                                       '0' if SAMPLES[name].get('hit0') else
                                                       ('loop' if SAMPLES[name]['kind'] == 'bed' else 'the onset'))
    return fn


for _nm in SAMPLES:
    SAMPLES[_nm]['fn'] = _make_sample_fn(_nm)
    globals()[_nm] = SAMPLES[_nm]['fn']


# =============================================================================================== register
_MINE = {__name__, 'epic_sfx', '__main__'}


def _reg_one(name, fn, category, character, use, send):
    cur = A.SOUNDS.get(name)
    if cur is not None:
        if cur['fn'] is fn:
            return False
        if getattr(cur['fn'], '__module__', None) not in _MINE:
            raise RuntimeError('epic_sfx: sound name %r is already registered by %s' % (name, cur['fn'].__module__))
    A._register(category, character, use, send)(fn)
    return True


def register(samples=True):
    """Add the 29 procedural sounds to audio.SOUNDS, and (samples=True) every *_real sample sound whose file exists under
    LIB. Idempotent (a re-import replaces this module's own entries and clears audio's render cache); raises if another
    module already owns one of the names. Returns the names registered by this call's scope."""
    changed = False
    names = []
    for name, m in SYNTH.items():
        changed |= _reg_one(name, m['fn'], m['category'], m['character'], m['use'], m['send'])
        names.append(name)
    if samples:
        for name, s in SAMPLES.items():
            if _sample_src(name) is None:
                continue
            changed |= _reg_one(name, s['fn'], s['category'], s['character'], s['use'],
                                s.get('send', None if s['kind'] == 'bed' else -20.0))
            names.append(name)
    if changed:
        A._sound_cached.cache_clear()
    return names


def missing_samples():
    """{sample sound: [candidate files]} for every *_real sound whose file is not in LIB (they do not register)."""
    return {n: list(s['src']) for n, s in SAMPLES.items() if _sample_src(n) is None}


# =============================================================================================== the reels' contract
_DHOL_D2 = midi_hz(38) / 58.0                   # ek_frame_ki_keemat_music: dagga 58 Hz -> D2
CONTRACT = (    # (sound, params, where) - every epic sound / params the five reels' modules pass (2026-10-09 grep)
    [('braam', dict(dur=2.0), 'pehle_wala_sfx f448 (align start)'),
     ('braam', dict(root=36.71, dur=1.0), 'log_kya_kahenge_sfx f480 reveal (align start, sat 12)'),
     ('trailer_hit', dict(), 'pehle_wala_sfx hook B f0'),
     ('trailer_hit', dict(pitch=1.0, seed=109), 'pehle_wala_music bar 8 beat 1'),
     ('trailer_hit', dict(pitch=1.0, seed=110), 'pehle_wala_music bar 8 beat 3')]
    + [('trailer_hit', dict(pitch=55.0 / 62.0, seed=k), 'ek_frame_ki_keemat_music taiko (lp 1500)') for k in range(6)]
    + [('dhol_hit', dict(pitch=_DHOL_D2, seed=100), 'ek_frame_ki_keemat_music drop')]
    + [('dhol_hit', dict(pitch=_DHOL_D2, seed=10 * b + j), 'ek_frame_ki_keemat_music chaal') for b in (11, 12)
       for j in (0, 1, 2, 3) if not (b == 11 and j == 0)]
    + [('heartbeat_build', dict(duration=1.2, bpm0=100.0, bpm1=160.0), 'pehle_wala_sfx f740 (lp 1200)'),
       ('shepard_riser', dict(duration=1.7), 'pehle_wala_sfx f704'),
       ('shepard_riser', dict(duration=2.2), 'ek_frame_ki_keemat_music into the drop'),
       ('reverse_cymbal', dict(duration=1.2), 'ek_frame_ki_keemat_music into the drop'),
       ('reverse_cymbal', dict(duration=2.4), 'ek_frame_ki_keemat_music loop bar (ends on DUR)'),
       ('timeline_scrub', dict(duration=0.667, speed=2.5), 'pehle_wala_sfx hook B D1 scrub (align start)'),
       ('clock_tick', dict(n=7, bpm=225.0), 'pehle_wala_sfx f584 (hp 4500)'),
       ('clock_tick', dict(n=1, bpm=60.0), 'pehle_wala_sfx drop-out tick'),
       ('mouse_click', dict(), 'bijli_chali_gayi_sfx f20 torch click'),
       ('tension_drone', dict(duration=12.0, root=36.71), 'log_kya_kahenge_music 3.2 -> 15.2 (hit must be 12.0)'),
       ('dark_drone', dict(), 'log_kya_kahenge_music bed (loop must be 24.0 s)'),
       ('edit_suite', dict(), 'pehle_wala_sfx / bijli_chali_gayi_sfx bed'),
       ('desi_city', dict(dur=36.4), 'beta_tum_karte_kya_ho_sfx bed (a DUR-long loop)')]
    + [('notif_ping', dict(pitch=pt, seed=k), 'beta_tum_karte_kya_ho_sfx pings') for pt in (1.1225, 1.4142, 1.4983)
       for k in range(4)]
    + [('notif_ping', dict(pitch=1.1225, buzz=1, seed=k), 'beta_tum_karte_kya_ho_sfx btk_haptic source') for k in range(4)]
    + [('tabla_hit', dict(stroke=st, pitch=1.0, seed=k), 'beta_tum_karte_kya_ho_music theka / sfx')
       for st in ('dha', 'ge', 'na', 'tin', 'ke', 'dhin', 'ta') for k in range(4)]
    + [('harmonium_swell', dict(duration=20 / 30 / 0.72, notes=(50, 57, 62, 66), seed=0), 'bijli_chali_gayi_music sabr')]
    + [('harmonium_swell', dict(duration=20 / 30 / 0.72, notes=(m,), seed=0), 'bijli_chali_gayi_music pitch check')
       for m in (50, 57, 62, 66)]
    + [('harmonium_swell', dict(duration=4.8, notes=(50, 57, 62), seed=k), 'ek_frame_ki_keemat_music swells')
       for k in range(7)]
    + [('harmonium_swell', dict(duration=6.0, notes=(50, 57, 62), seed=7), 'ek_frame_ki_keemat_music seam swell')])


# =============================================================================================== QC / CLI
def table():
    """Every sound of the kit (registered or not): name -> dict(category, hit, dur, mmax, kind, registered)."""
    out = {}
    for n, m in SYNTH.items():
        out[n] = dict(category=m['category'], hit=m['hit'], dur=m['dur'], mmax=m['mmax'], kind='synth',
                      registered=n in A.SOUNDS)
    for n, s in SAMPLES.items():
        out[n] = dict(category=s['category'], hit='loop' if s['kind'] == 'bed' else ('0' if s.get('hit0') else 'onset'),
                      dur=s.get('loop') or (s['seg'][1] if s['seg'][1] else None), mmax=s['mmax'], kind='sample',
                      registered=n in A.SOUNDS, src=_sample_src(n))
    return out


def _defaults(name):
    import inspect
    fn = SYNTH[name]['fn'] if name in SYNTH else SAMPLES[name]['fn']
    return {k: v.default for k, v in inspect.signature(fn).parameters.items()}


def expected_hit(name, params=None):
    """The documented hit (s) for a sound at params (defaults otherwise), or None for beds / sample onsets."""
    p = dict(_defaults(name))
    p.update(params or {})
    if name in SAMPLES:
        return 0.0 if SAMPLES[name].get('hit0') else None
    h = SYNTH[name]['hit']
    if h == 'loop':
        return 0.0
    if h == 'peak':
        return 0.72 * float(p['duration'])
    if h == 'end':
        if name == 'dholak_roll':
            return 0.002 + int(p['n']) * 60.0 / float(p['bpm']) / 4.0
        return float(p.get('duration', p.get('dur')))
    if name == 'notif_ping' and int(p.get('buzz', 0)):
        return 0.40
    return float(h)


def check_sound(name, params=None, tol_lu=1.5):
    """Render one sound and measure it against the kit table. Returns a row dict (problems = [] when it passes)."""
    p = dict(params or {})
    t0 = time.time()
    x = A.sound(name, **p)
    el = time.time() - t0
    xa = np.asarray(x, dtype=np.float64)
    is_bed = A.SOUNDS[name]['category'] == 'bed'
    m = SJ.measure(xa, x.hit, bed=is_bed)
    probs = list(m['problems'])
    eh = expected_hit(name, p)
    if eh is not None and abs(x.hit - eh) > 1e-6:
        probs.append('hit %.4f s, documented %.4f s' % (x.hit, eh))
    want = (SYNTH[name]['mmax'] if name in SYNTH else SAMPLES[name]['mmax'])
    got = m['i_lufs'] if is_bed else m['mmax_lufs']
    if not p or name in SAMPLES:
        if abs(got - want) > tol_lu:
            probs.append('%s %.2f LUFS, table %.1f (+-%.1f)' % ('integrated' if is_bed else 'Mmax', got, want, tol_lu))
    if m['tp_dbtp'] > -1.0 + 1e-6:
        probs.append('true peak %.2f dBTP > -1.0' % m['tp_dbtp'])
    if is_bed and name in SYNTH:
        if not p and abs(len(xa) / SR - float(_defaults(name)['dur'])) > 0.06 and name != 'projector_loop':
            probs.append('loop %.3f s, table %.1f' % (len(xa) / SR, _defaults(name)['dur']))
    tab_dur = SYNTH[name]['dur'] if name in SYNTH else None
    return dict(name=name, params=p, cat=A.SOUNDS[name]['category'], dur=round(len(xa) / SR, 3), table_dur=tab_dur,
                hit=round(float(x.hit), 4), hit_doc=None if eh is None else round(eh, 4), mmax=m['mmax_lufs'],
                i_lufs=m['i_lufs'], table_mmax=want, tp=m['tp_dbtp'], peak=m['peak_dbfs'], crest=m['crest_db'],
                mono_db=m['mono_db'], nyq_db=m['nyq_db'], seam=m.get('seam_ratio'), centroid=m['centroid_hz'],
                ms=round(el * 1000), qc=[q for q in A.qc(xa.astype(np.float32), x.hit) if not (is_bed and 'edge' in q)],
                problems=probs)


def _fmt_row(r):
    return '%-20s %-10s %6.2f %6s %7.4f %7s %6.1f %6.1f %5s %6.2f %5.1f %6s %5d  %s' % (
        r['name'], r['cat'], r['dur'], '' if r['table_dur'] is None else '%.1f' % r['table_dur'], r['hit'],
        '' if r['hit_doc'] is None else '%.4f' % r['hit_doc'], r['i_lufs'] if r['cat'] == 'bed' else r['mmax'],
        r['table_mmax'], '', r['tp'], r['crest'], '' if r['seam'] is None else '%.2f' % r['seam'], r['ms'],
        '; '.join(r['problems']) or 'ok')


def check(names=None, sheets=True, catalog_wav=True):
    """python3 epic_sfx.py check [names]: render every kit sound (default params), measure, compare with the table,
    write OUT/epic_check.txt / .json and spectrogram sheets. Returns (rows, failures)."""
    register()
    os.makedirs(OUT, exist_ok=True)
    allnames = list(SYNTH) + [n for n in SAMPLES]
    todo = names or allnames
    rows, items, skipped = [], [], []
    for n in todo:
        if n not in A.SOUNDS:
            if n in SAMPLES:
                skipped.append((n, 'sample file missing: %s' % ', '.join(SAMPLES[n]['src'])))
                continue
            raise KeyError('epic_sfx: unknown sound %r' % n)
        rows.append(check_sound(n))
        items.append((n, A.sound(n)))
    hdr = '%-20s %-10s %6s %6s %7s %7s %6s %6s %5s %6s %5s %6s %5s  %s' % (
        'sound', 'cat', 'dur', 'tab', 'hit', 'doc', 'Mmax*', 'tab', '', 'TP', 'crest', 'seam', 'ms', 'problems')
    lines = [hdr] + [_fmt_row(r) for r in rows]
    lines.append('(* beds: integrated LUFS; the table column is the sound_design.md section 3 value)')
    for n, why in skipped:
        lines.append('NOT REGISTERED %-20s %s' % (n, why))
    fails = [r for r in rows if r['problems'] or r['qc']]
    lines.append('%d sounds checked, %d problems, %d sample sounds not registered' % (len(rows), len(fails), len(skipped)))
    txt = '\n'.join(lines)
    print(txt)
    tag = 'epic_check' if names is None else 'epic_check_sel'
    with open(os.path.join(OUT, tag + '.txt'), 'w') as fh:
        fh.write(txt + '\n')
    with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
        json.dump(dict(rows=rows, skipped=skipped, lib=LIB), fh, indent=1, default=float)
    if sheets and items:
        prefix = 'epic_sheet_' if names is None else 'epic_sheet_sel_'
        paths = A.catalog_sheets(items, os.path.join(OUT, prefix + '%d.png'), cols=3, per_sheet=12)
        print('sheets:', ', '.join(paths))
    if catalog_wav and names is None:
        cues, idx, t = [], [], 0.5
        for n, x in items:
            if A.SOUNDS[n]['category'] == 'bed':
                continue
            cues.append(dict(t=t, name=n, align='start'))
            idx.append(dict(t=round(t, 3), name=n, hit=round(t + x.hit, 3), dur=round(x.dur, 3)))
            t += min(x.dur, 3.0) + 0.6
        rep = A.mix(cues, t + 0.5, os.path.join(OUT, 'epic_catalog.wav'), None, auto_duck=False, vary=False,
                    tp_ceiling=-2.0, verbose=False)
        with open(os.path.join(OUT, 'epic_catalog_index.json'), 'w') as fh:
            json.dump(dict(file=rep['files'].get('mix'), integrated_lufs=rep['integrated_lufs'],
                           true_peak_dbtp=rep['true_peak_dbtp'], cues=idx), fh, indent=1)
        print('catalog: %s (%.1f s, %.2f LUFS, %.2f dBTP)' % (rep['files'].get('mix'), t + 0.5, rep['integrated_lufs'],
                                                             rep['true_peak_dbtp']))
    return rows, fails


def alias_residual(name, params=None):
    """Aliasing estimate (dB) of a procedural sound, as sfx_jawad.alias_residual: the normal render (sfx_jawad's
    oversampled stages at 8x, the toolkit's _sat / _asat at 1x) against a reference with all of them at 32x; the
    gain-matched residual relative to the reference. None when the sound has no such stage."""
    fn = SYNTH[name]['fn']
    p = dict(params or {})
    c0 = SJ._STATE['os_calls']
    with SJ.toolkit_saturators('count') as nsat:
        a = np.asarray(fn(**p), dtype=np.float64)
    if SJ._STATE['os_calls'] == c0 and not nsat[0]:
        return None
    with SJ.reference_quality(), SJ.toolkit_saturators('ref'):
        b = np.asarray(fn(**p), dtype=np.float64)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    g = float((a * b).sum() / ((b * b).sum() + 1e-30))
    return round(float(10 * np.log10(((a - g * b) ** 2).sum() / ((b * b).sum() + 1e-30) + 1e-30)), 1)


def contract():
    """Render every CONTRACT entry with the exact params the reel modules pass: qc, true peak, hit vs documented."""
    register()
    bad = []
    for name, params, where in CONTRACT:
        if name not in A.SOUNDS:
            bad.append((name, params, 'not registered'))
            print('MISSING %-16s %s  (%s)' % (name, params, where))
            continue
        r = check_sound(name, params)
        hx = float(A.sound(name, **params).hit)                       # exact, not the rounded table value
        extra = []
        if name == 'tension_drone' and abs(hx - float(params['duration'])) > 1e-9:
            extra.append('hit %r != duration' % hx)
        if name == 'dark_drone' and len(A.sound(name, **params)) != _n(24.0):
            extra.append('loop length %d != %d' % (len(A.sound(name, **params)), _n(24.0)))
        if name == 'desi_city' and len(A.sound(name, **params)) != _n(params['dur']):
            extra.append('loop length != dur')
        if name == 'harmonium_swell':
            hs = hx * SR
            if abs(hs - round(hs)) > 1e-6:
                extra.append('hit %.9f s is not a whole sample' % hx)
        pr = r['problems'] + r['qc'] + extra
        if pr:
            bad.append((name, params, pr))
        print('%-16s %-48s dur %6.2f hit %7.4f Mmax %6.1f TP %6.2f  %s  (%s)' % (
            name, json.dumps(params, default=float)[:48], r['dur'], r['hit'], r['mmax'], r['tp'], '; '.join(pr) or 'ok',
            where))
    print('%d contract renders, %d with problems' % (len(CONTRACT), len(bad)))
    return bad


def main(argv):
    a = list(argv)
    cmd = a[0] if a else 'check'
    if cmd == 'check':
        rows, fails = check(a[1:] or None)
        miss = missing_samples()
        if miss:
            print('sample sounds not registered (files missing in %s): %s' % (LIB, ', '.join(sorted(miss))))
        return 1 if fails else 0
    if cmd == 'play':
        register()
        name = a[1]
        prm = json.loads(a[2]) if len(a) > 2 else {}
        x = A.sound(name, **prm)
        path = a[3] if len(a) > 3 else os.path.join(OUT, 'audition', '%s.wav' % name)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        A._write_wav(path, x, 24)
        st = SJ.measure(np.asarray(x, dtype=np.float64), x.hit, bed=A.SOUNDS[name]['category'] == 'bed')
        sub = 'hit %.4f  dur %.2f  Mmax %.1f  I %.1f  TP %.2f  crest %.1f  %s' % (
            x.hit, x.dur, st['mmax_lufs'], st['i_lufs'], st['tp_dbtp'], st['crest_db'], '; '.join(st['problems']) or 'qc ok')
        A.spectro_image(x, 1000, 420, x.hit, '%s %s' % (name, json.dumps(prm, default=float)), sub).save(path[:-4] + '.png')
        print(path)
        print(sub)
        return 0
    if cmd == 'contract':
        return 1 if contract() else 0
    if cmd == 'alias':
        worst = None
        for n in (a[1:] or list(SYNTH)):
            t0 = time.time()
            v = alias_residual(n)
            print('%-18s alias residual %s dB  (%.1f s)' % (n, '-' if v is None else '%.1f' % v, time.time() - t0),
                  flush=True)
            if v is not None:
                worst = v if worst is None else max(worst, v)
        print('worst alias residual: %s dB (sfx_jawad accepts <= -60)' % worst)
        return 1 if (worst is not None and worst > -60.0) else 0
    if cmd == 'catalog':
        register()
        for n, d in table().items():
            print('%-20s %-10s hit %-6s dur %-5s Mmax %-6s %-6s %s' % (n, d['category'], d['hit'], d['dur'], d['mmax'],
                                                                      'yes' if d['registered'] else 'NO', _defaults(n)))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
