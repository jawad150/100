"""sfx_jawad.py: Jawad's (@jawad_mp4) signature cinematic SFX library, built on the toolkit's audio.py.

Everything is synthesised procedurally in numpy/scipy (no samples, no downloads): 48 kHz stereo float32, seeded
variation (seed=0..n), pre-balanced levels, click-free edges, designed hit offsets. register() adds every sound to
audio.SOUNDS at runtime, so audio.mix() / audio.sound() / cue sheets use them like built-ins. audio.py is never
edited. Spec: brand_reels/research/transitions_sound_music_bible.md (sections 4.1-4.9).

USE (inside pipeline/jawad_reels/<module>_sfx.py)
    import audio as A, sfx_jawad as J
    def cues():
        J.register()                                     # idempotent; call it first
        c = J.ember_slam(12.0, bpm=90)                   # bible hit stack -> list of cue dicts
        c += [dict(t=3.20, name='jd_whip', pan=-0.3), dict(t=8.0, name='jd_riser', params=dict(bars=2, bpm=90))]
        return J.fit_under_vo(c, '<WS>/vo/reel1_final.words.json', offset=0.3)   # ducks/carves; hero on a word raises
    BED, BED_GAIN_DB = 'jd_room_night_home', -30

CONVENTIONS (same as audio.py)
    sound(name, **params) -> Sfx float32 (N, 2) at 48 kHz with .hit = seconds from start to the designed hit.
    align='hit' puts that hit on the cue time. Hit = transient for impacts/clicks, loudest pass for whooshes, END
    for risers / reverse swells / rolls / whisper wall / power_up, end of motion for timeline_scrub (cue that one
    with align='start'). Levels: max momentary loudness = REF_LUFS (-20) + level (column 'lvl'), so gain_db=0 is the
    starting point. Beds are seamless loops at -20 LUFS integrated (BED_GAIN_DB -30 = felt).
    Quality guarantees (checked by the self-test and by `render`): audio.qc() clean, true peak <= -1.0 dBTP, no
    flat-topped (clipped) runs, nothing above 20.5 kHz (elliptic guard filter, 90 dB), (L+R)/2 mono fold-down loses
    <= 1.5 dB of max momentary loudness (beds <= 2.5 dB), and no aliasing: this module's waveshapers, FM operators
    and varispeed reads run oversampled (8x, cubic interpolation); the toolkit's own saturators (audio._sat / _asat
    inside audio._thump, audio.bass_enhance and the toolkit layers of the stacks) run at 1x. Every render that
    contains any of these stages is measured against a 32x reference render of ALL of them (residual must stay
    below -60 dB; measured -109 to -158 dB). Oscillators are band-limited by construction.

CATALOG  (name: category, hit, lvl, params -> use)            seed=0 everywhere; 'dur'/'duration' interchangeable
  HIT STACKS (bible 4.2): cue builders return cue lists; jd_stack_* render the same stack into one sound
    ember_slam(t0, bpm, riser_beats=4, gap_beats=0)  riser -> flash_hit (-3 ms) + impact_big + sub_drop  EPIC reveal
    velvet_hit(t0, pitch=1)    heartbeat(n=1) + impact_soft + glass_tap (+20 ms, in key)          INTIMATE landing
    glass_truth(t0, pitch=1)   ui_click (-2 ms) + glass_tap + sub_drop(0.8) + jd_sparkle (+30 ms) TECH / UI reveal
    dha_hit(t0, sa_hz, bpm)    jd_tabla_roll (ends on t0) + jd_tabla_dha + sub_drop + jd_ghungroo  DESI reveal
    (glass_truth uses jd_sparkle, an alias-free rebuild of audio.sparkle whose FM sidebands can fold back.)
    jd_stack_ember_slam   impact     riser+hit  +4   bpm, riser_beats, gap_beats
    jd_stack_velvet_hit   impact     0.006      -3   pitch
    jd_stack_glass_truth  ui         0.010      -2   pitch
    jd_stack_dha_hit      impact     roll+hit   +1   sa, bpm
  IMPACT
    jd_hit_hero           0.003  +4  tail     5-layer ember slam: crack, punch, sub, anvil ring, hall + spark crackle
    jd_hit_soft           0.006  -3  -        warm felt thump + wood knock + air puff (soft landings)
    jd_sub_drop           0.008  -2  dur=1.6  92 -> 29 Hz pitch dive with phone harmonics (smash cuts)
    jd_heartbeat          0.006  -3  n=1, bpm=60   deep cinematic lub-dub (intimate beats, held-breath silence)
    jd_floodlight_clunk   0.003   0  -        stadium contactor clunk + ballast hum swell + stand echoes
    jd_tabla_dha          0.0    -2  sa       tabla "dha" (na + ge) tuned to Sa
  TRANSITION
    jd_whoosh_short       0.28   -3  direction  warm air rush + ember sizzle trail
    jd_whoosh_long        0.58*d -5  dur=2.4, direction  big flanged swell, hall, ember crackle trail
    jd_whip               0.16   -3  direction  bright whip pan with a cloth-snap crack on the pass
    jd_riser              END    -4  bars=4 (1|2|4|8), bpm=90 (60-120; use 75 for 150 half-time)
                                     noise sweep + Shepard glide + grid pulses (1/4 -> 1/8 -> 1/16 -> 1/32, all four
                                     stages at every length) + reverse cymbal; exactly bars*240/bpm s long, pulses on
                                     the beat grid, the sweep gated by the same grid so every stage stays audible
    jd_reverse_swell      END    -4  duration=1.5   reversed hall bloom + accelerating ember crackle (mono-safe)
    jd_tape_stop          0.0    -4  dur=0.8    a held D-minor groove slowing to a halt + pinch-roller clunk
    jd_power_down         0.001  -4  dur=1.6    relay clack, 100 Hz hum + coil whine winding down, fan spin-down
    jd_power_up           END    -4  dur=1.4    relay, whine + hum spinning up, "on" thoom at the hit
    jd_crt_collapse       0.001  -4  -        CRT switch-off: click, 15.625 kHz flyback whine dies, "thwup", static
    jd_revolving_door     0.5*d  -5  duration=2.0, wings=3, direction   wing whooshes + seal brush, world muffles
    jd_tabla_roll         END    -6  n=8, bpm=90, sa   "ti-ra-ki-ta" 32nds crescendo, hit = the downbeat after
  UI / FOLEY
    jd_ui_click           0.0005 -9  pitch    dark-glass click with warm body
    jd_ui_tick            0.0003 -13 pitch    tiny glassy tick
    jd_ui_pop             0.001  -9  pitch    round "bloop"
    jd_keyboard           0.002  -11 n=10, cps=10, style='laptop'|'mech'   human-timed typing with releases
    jd_mouse_click        0.0005 -12 double=0  micro-switch press + release (double=1: double click)
    jd_timeline_scrub     END    -12 duration=1.0, speed=2.0   NLE audio-scrub chatter (align='start')
    jd_glass_slide        END    -8  dur=0.5   glass on glass friction (stops 45-50 ms early), glassy "tunk" landing
                                               on the hit = the loudest moment (>= 6 dB over the 30 ms before)
    jd_glass_clink        0.001  -8  pitch    two glasses touching, beating modes + micro bounce
    jd_ups_beep           0.001  -12 n=3, period=1.2, pitch, relay=1  load-shedding UPS: relay tak + piezo beeps
    jd_vn_blip            0.001  -12 pitch    voice-note mic blip
    jd_vn_record          0.001  -12 duration=1.5  voice-note record start: two rising pips + open-mic air
    jd_vn_send            0.0005 -10 -        voice-note send: tap, upward swish, landing pop
  TEXTURE
    jd_projector          spinup -8  duration=2.5, spinup=0.9  film projector spinning up to 24 fps (hit = at speed)
    jd_fluoro_flicker     0.55*d -9  dur=2.2  tube light: starter ticks, buzzing flickers, catches into a hum
    jd_crowd_whisper      END    -8  duration=3.0, voices=32   whisper wall that grows and is cut on the hit
    jd_tabla_na / jd_tabla_tin / jd_tabla_ge  0.0  -4 / -8 / -6  (sa)  single tabla strokes (bible recipes)
    jd_ghungroo           0.0005 -10 -        ankle-bell shake (desi sparkle)
    jd_sparkle            0.002  -11 -        FM twinkles, oversampled (alias-free sparkle)
  BED (seamless loops, -20 LUFS integrated)
    jd_room_night_home    24 s   ceiling fan (blade-pass air, 50 Hz motor hum), distant crickets, far traffic
    jd_room_stadium       24 s   empty stadium: gusting wind, floodlight ballast hum, halyard tinks, huge space
    jd_room_studio        16 s   treated studio: PC fan + blade tone, split-AC hum + airflow, faint hiss
    jd_projector_loop      8 s   projector running at 24 fps (fps), claw clatter + motor + fan
  Bible names also resolve (aliases): tabla_na, tabla_tin, tabla_ge, tabla_dha, tabla_roll, ghungroo.

CUE HELPERS
    stack(name, t0, **kw) -> cues   (STACKS = ember_slam, velvet_hit, glass_truth, dha_hit)
    vo_windows(words, pad=0.06, offset=0.0) -> merged speech windows [(t0, t1)]; words = .words.json path, word dicts
        ({'start', 'end'}) or (t0, t1) tuples
    fit_under_vo(cues, words, depth_db=-6, hero='raise'|'drop'|'warn', offset=0.0, report=False) -> new cues:
        HERO cues (impact_big, flash_hit, logo_sting, jd_hit_hero, jd_floodlight_clunk, rendered hero stacks, any
        cue with hero=True) need 120 ms of no speech before the hit and 300 ms after (150 ms for non-impacts),
        net of the speech itself (bible 4.1: a pause of >= 0.42 s of real silence holds a hero, >= 0.27 s a
        non-impact one). Speech = the UNPADDED words + the VO audio's activity (10 ms RMS above median speech
        - 30 dB) whenever the audio is there (vo_audio='auto' finds the vo_chain '<stem>.wav' next to a
        '<stem>.words.json' path; whisper word ends run up to 160 ms early on TTS). Otherwise HeroOnWordError
        (names the nearest legal hit time) or dropped/flagged. Other cues whose hit
        lies in a word window (words padded 60 ms for ducking) get depth_db; AIR sounds also get 'hp' 5500, DARK
        sounds 'lp' 1100; MID sounds (the bible's MID set + every jd_* sound with band 'mid' in `catalog`: clicks,
        keys, glass, whip, tabla, vn_* ...) are not filtered, only ducked a further -2 dB (-8 dB in all). Risers / swells / rolls / the whisper wall (SPAN) whose body
        overlaps speech get depth_db and 'lp' 1100.
    hero_slots(words, offset=0.0, pre=0.12, post=0.30, dur=None, vo_audio='auto') -> legal hit intervals for hero
        cues (same speech as fit_under_vo, rounded inward to whole ms); vo_activity(wav) -> measured speech windows
    tape_stop_fx(x, t0, dur=0.8, curve=1.6) -> buffer with an alias-safe tape stop at t0 (for real beds/stems)

CLI (run in pipeline/jawad_reels; heavy runs: nice -n 10, OMP/OPENBLAS threads 2)
    python3 sfx_jawad.py --selftest          checks everything, exits 1 on failure (<WS>/out/selftest/sfx_jawad_*)
    python3 sfx_jawad.py render [--out DIR]  every sound + variants -> <WS>/sfx_library/*.wav, QC.md/qc.csv/qc.json,
                                             contact_sheet*.png (default DIR = <WS>/sfx_library)
    python3 sfx_jawad.py catalog             names, categories, hits, params
    python3 sfx_jawad.py play jd_riser '{"bars": 8, "bpm": 75}' out.wav   -> wav + spectrogram png
"""
import contextlib
import csv
import functools
import json
import math
import os
import sys
import time

import numpy as np
from scipy import signal

import audio as A
from audio import (SR, TWO_PI, _t, _n, _rng, _st, _ar, _taper, _fade, _unit, _thump, _click, _grains,
                   _crackle, _loop_mask_noise, _periodic_lfo, modal, noise_band, colored, osc, lp, hp, bp, reson,
                   reverb_circular, pan, width, decorrelate, undb)

HERE = os.path.dirname(os.path.abspath(__file__))
LIBRARY = os.path.join(A.WS, 'sfx_library')
TP_CEIL = -1.0                     # every rendered sound: true peak <= -1.0 dBTP
REF = A.REF_LUFS

# =============================================================================================== alias-safe DSP
# Normal renders oversample nonlinear / FM / varispeed stages 8x; reference renders (QC) use 32x. The same
# absolute-frequency FIR (pass <= 17.6 kHz, -6 dB at 20 kHz, <= -100 dB from 22.4 kHz) is used at every factor,
# so a normal-vs-reference difference isolates aliasing.
_STATE = {'os': 8, 'os_calls': 0, 'audit': None}
TAIL_DB = -50.0                    # a buffer may end (or be cropped) only below this level re its own peak
MONO_LOSS = 1.5                    # (L+R)/2 fold-down may lose at most this much max momentary loudness (dB) ...
MONO_LOSS_BED = 2.5                # ... and a bed this much (diffuse ambience loops, felt at -24..-36 dB)


@contextlib.contextmanager
def tail_audit():
    """Collect 'still sounding at a buffer edge' events (a component cut before it decayed: the abrupt stop that
    reverb()'s 4 ms input fade or a cropped _add() would make) while rendering inside this block."""
    old = _STATE['audit']
    _STATE['audit'] = log = []
    try:
        yield log
    finally:
        _STATE['audit'] = old


def _audit_tail(x, what, depth=2):
    if _STATE['audit'] is None:
        return
    x = np.asarray(x, dtype=np.float64)
    pk = float(np.max(np.abs(x))) if x.size else 0.0
    if pk <= 0:
        return
    lvl = 20 * math.log10(max(float(np.max(np.abs(x[-_n(0.002):]))), 1e-12) / pk)
    if lvl > TAIL_DB:
        f = sys._getframe(depth)
        _STATE['audit'].append('%s still at %.0f dB at its end (%s line %d)' % (what, lvl, f.f_code.co_name,
                                                                                 f.f_lineno))


def reverb(x, preset='room', wet_db=-12.0, dry=1.0, send_hp=None, hard_end=False, **kw):
    """audio.reverb with the tail audit (hard_end=True marks a designed hard stop, e.g. a riser's end)."""
    if not hard_end:
        _audit_tail(x, 'reverb input')
    return A.reverb(x, preset, wet_db, dry, send_hp, **kw)


def _add(buf, sig, t0):
    """audio._add with the audit: content cropped off either end of buf must already be silent."""
    if _STATE['audit'] is not None:
        s = np.asarray(sig)
        i = int(round(t0 * SR))
        pk = float(np.max(np.abs(s))) if s.size else 0.0
        lost = []
        if i < 0:
            lost.append(s[:min(len(s), -i)])
        if i + len(s) > len(buf):
            lost.append(s[max(0, len(buf) - i):])
        for seg in lost:
            if pk > 0 and seg.size and np.max(np.abs(seg)) > pk * 10 ** (TAIL_DB / 20):
                f = sys._getframe(1)
                _STATE['audit'].append('_add cropped audible content (%s line %d)' % (f.f_code.co_name, f.f_lineno))
    return A._add(buf, sig, t0)


@contextlib.contextmanager
def reference_quality():
    """Render inside this block at 32x oversampling (the alias reference used by the QC)."""
    old = _STATE['os']
    _STATE['os'] = 32
    try:
        yield
    finally:
        _STATE['os'] = old


@functools.lru_cache(maxsize=8)
def _os_fir(L):
    return signal.firwin(64 * L + 1, 20000.0, fs=L * SR, window=('kaiser', 10.0))


def _up(x, L):
    return signal.resample_poly(np.asarray(x, dtype=np.float64), L, 1, axis=0, window=_os_fir(L))


def _down(y, L, n):
    return signal.resample_poly(y, 1, L, axis=0, window=_os_fir(L))[:n]


def shape(x, drive=2.0, bias=0.0):
    """Alias-safe tanh waveshaper (bias > 0 adds even harmonics). Unity small-signal slope is not kept; peak of
    a unit input maps to ~1. Oversampled (8x normal, 32x reference)."""
    L = _STATE['os']
    _STATE['os_calls'] += 1
    x = np.asarray(x, dtype=np.float64)
    if not np.any(x):
        return x.copy()
    y = np.tanh(drive * (_up(x, L) + bias)) - math.tanh(drive * bias)
    y /= (math.tanh(drive * (1.0 + bias)) - math.tanh(drive * bias))
    return _down(y, L, len(x))


def benhance(x, amount=0.8, fc=110.0, band=(120.0, 650.0), drive=3.5):
    """audio.bass_enhance with the harmonic generator oversampled (phone-speaker translation of sub layers)."""
    lo = lp(lp(x, fc, 2), fc, 2)
    env = lp(np.abs(signal.hilbert(lo, axis=0)), 40.0, 2)
    floor = np.max(np.abs(env)) * 1e-3 + 1e-12
    u = lo / np.maximum(env, floor)
    u = 1.5 * math.tanh(1.0) * shape(u / 1.5, 1.0)            # = 1.5 tanh(u / 1.5), soft limit, oversampled
    h = shape(u, drive, 0.25) * env
    h = bp(h - np.mean(h, axis=0), band[0], band[1], 2)
    h = lp(h, band[1], 2)
    return x + amount * h


def varread(src, pos):
    """Read src (mono or stereo) at fractional sample positions pos (varispeed, |rate| <= 1 safe): the source is
    oversampled and read with 4-point cubic (Catmull-Rom) interpolation. Pre-low-pass src for |rate| > 1."""
    L = _STATE['os']
    _STATE['os_calls'] += 1
    src = np.asarray(src, dtype=np.float64)
    up = _up(np.concatenate([np.zeros((2,) + src.shape[1:]), src, np.zeros((4,) + src.shape[1:])]), L)
    q = np.clip((np.asarray(pos, dtype=np.float64) + 2.0) * L, 1, len(up) - 3)
    i = np.floor(q).astype(np.int64)
    x = q - i
    if up.ndim == 2:
        x = x[:, None]
    p0, p1, p2, p3 = up[i - 1], up[i], up[i + 1], up[i + 2]
    return p1 + 0.5 * x * (p2 - p0 + x * (2 * p0 - 5 * p1 + 4 * p2 - p3 + x * (3 * (p1 - p2) + p3 - p0)))


def fm_bell_os(d, fc, ratio=1.4, index=2.0, tau=1.0, tau_index=0.25, attack=0.002, t0=0.0):
    """audio.fm_bell computed at 8x (32x reference) and decimated: sidebands above Nyquist never fold back."""
    L = _STATE['os']
    _STATE['os_calls'] += 1
    n = _n(d)
    tt = np.arange(n * L) / (SR * L)
    u = np.maximum(tt - t0, 0.0)
    a = max(attack, 1e-5)
    env = np.where(u < a, 0.5 - 0.5 * np.cos(np.pi * np.clip(u / a, 0, 1)), 1.0) * np.exp(-np.maximum(u - a, 0) / tau)
    y = np.sin(TWO_PI * fc * u + index * np.exp(-u / tau_index) * np.sin(TWO_PI * fc * ratio * u)) * env * (tt >= t0)
    return _taper(_down(y, L, n), 0.25)


def harm(f0, amps, fmax=16000.0, rng=None):
    """Band-limited additive harmonic tone on an f0 track (Hz per sample): partial k fades out smoothly between
    0.9*fmax and fmax, so nothing ever crosses Nyquist. amps[k-1] = amplitude of harmonic k."""
    f0 = np.asarray(f0, dtype=np.float64)
    base = TWO_PI * np.cumsum(f0) / SR
    out = np.zeros(len(f0))
    fmin = float(np.min(f0)) if len(f0) else 0.0
    for k, a in enumerate(amps, 1):
        if k * fmin >= fmax:
            break
        if a == 0:
            continue
        g = np.clip((fmax - k * f0) / (0.1 * fmax), 0.0, 1.0)
        ph = rng.uniform(0, TWO_PI) if rng is not None else 0.0
        out += a * g * np.sin(k * base + ph)
    return out


def tvf(x, fn):
    """Time-varying STFT filter: fn(p (T,), f (F,)) -> (T, F) gain with p = t/len in 0..1. Mono or stereo."""
    x = np.asarray(x, dtype=np.float64)
    X = x[:, None] if x.ndim == 1 else x
    N = len(X)
    T = N // A._HOP + 1
    p = A._frame_p(T, N / SR)
    f = np.fft.rfftfreq(A._NFFT, 1.0 / SR)
    m = fn(p, f)
    out = np.stack([A._istft(A._stft(X[:, c]) * m, N) for c in range(X.shape[1])], 1)
    return out[:, 0] if x.ndim == 1 else out


def lp_mask(fc_of_p, order=2.0):
    """tvf() gain for a time-varying low-pass: fc_of_p(p) -> Hz (array)."""
    return lambda p, f: 1.0 / np.sqrt(1.0 + (f[None, :] / np.maximum(fc_of_p(p), 20.0)[:, None]) ** (2 * order))


# ------------------------------------------------------------------------------------------------ finishing
_GUARD = signal.iirdesign(19000.0, 20500.0, 0.05, 90.0, ftype='ellip', fs=SR, output='sos')


def _guard_gain(f):
    return np.where(f <= 19000.0, 1.0, np.where(f >= 20500.0, 0.0, 0.5 + 0.5 * np.cos(np.pi * (f - 19000.0) / 1500.0)))


def _hf_db(x, f_lo=20500.0):
    m = np.asarray(x, dtype=np.float64)
    m = m.mean(1) if m.ndim == 2 else m
    P = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1.0 / SR)
    return float(10 * np.log10(P[f >= f_lo].sum() / (P.sum() + 1e-30) + 1e-30))


def _tp_cap(y):
    tp = A.true_peak(y)
    if tp > TP_CEIL - 0.02:
        y = y * undb(TP_CEIL - 0.05 - tp)
    return y


def _done(x, hit, level, name, **kw):
    """Finish a one-shot: guard low-pass (19 / 20.5 kHz elliptic, 90 dB), audio._finish (DC/subsonic HP, trim,
    click-free fades, loudness calibration, -1 dBFS sample cap), then a -1.0 dBTP true-peak cap."""
    x = _st(np.nan_to_num(np.asarray(x, dtype=np.float64)))
    if kw.get('trim', True):
        _audit_tail(x, name + ' final buffer')
    raw_hf = _hf_db(x)
    x = signal.sosfilt(_GUARD, x, axis=0)
    s = A._finish(x, hit, level, name, **kw)
    out = A.Sfx(_tp_cap(np.asarray(s, dtype=np.float64)), s.hit, name)
    out.raw_hf_db = raw_hf
    return out


def _bed_done(x, name, level=0.0):
    """Finish a seamless loop: circular guard filter (loop-safe), DC removal, integrated loudness REF + level."""
    x = _st(np.nan_to_num(np.asarray(x, dtype=np.float64)))
    raw_hf = _hf_db(x)
    x = A._spec_filter(x, _guard_gain)
    s = A._bed_finish(x, name, level)
    out = A.Sfx(_tp_cap(np.asarray(s, dtype=np.float64)), 0.0, name)
    out.raw_hf_db = raw_hf
    return out


def _add_wrap(buf, sig, t0):
    """Add sig into a loop buffer at t0 (s), wrapping around the end (seamless beds)."""
    sig = np.asarray(sig, dtype=np.float64)
    if sig.ndim == 1 and buf.ndim == 2:
        sig = _st(sig)
    N = len(buf)
    idx = (int(round(t0 * SR)) + np.arange(len(sig))) % N
    np.add.at(buf, idx, sig)
    return buf


def _pad(x, n):
    x = np.asarray(x, dtype=np.float64)
    if len(x) >= n:
        return x[:n]
    return np.pad(x, ((0, n - len(x)),) + ((0, 0),) * (x.ndim - 1))


def _mono_safe(st, lo=250.0, side_max=0.45, sm=0.05):
    """Mono fold-down safety for a one-shot (phone speakers play (L+R)/2): mid/side, the side channel high-passed
    at lo (LR4: everything below ~lo becomes mono) and its 50 ms energy capped at side_max x the mid's (side_max 0.45
    = side >= 7 dB under mid, so the fold-down loses <= ~1 dB instead of 3 dB for uncorrelated channels)."""
    st = _st(st)
    m, sd = 0.5 * (st[:, 0] + st[:, 1]), 0.5 * (st[:, 0] - st[:, 1])
    if lo:
        sd = hp(hp(sd, lo, 2), lo, 2)
    if side_max:
        g = np.minimum(1.0, side_max * np.sqrt((A._smooth(m * m, sm) + 1e-12) / (A._smooth(sd * sd, sm) + 1e-12)))
        sd = sd * A._smooth(g, sm)
    return np.stack([m + sd, m - sd], 1)


def _smoothstep(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def _gate(t, t0, t1, edge=0.004):
    """Raised-cosine gate: 0 before t0, 1 between, 0 after t1 (edges of `edge` s)."""
    a = np.clip((t - t0) / edge, 0, 1)
    b = np.clip((t1 - t) / edge, 0, 1)
    return (0.5 - 0.5 * np.cos(np.pi * a)) * (0.5 - 0.5 * np.cos(np.pi * b))


def _stadium(x, r, wet_db=-9.0, echoes=((0.23, -8.0, 2600.0, -0.5), (0.47, -13.0, 1800.0, 0.45),
                                         (0.74, -19.0, 1200.0, -0.3))):
    """Big open stadium: discrete slap-back echoes off the stands (delay, dB, low-pass, pan) + a long hall."""
    x = _st(x)
    n_tail = _n(max(e[0] for e in echoes) + 0.05)
    out = np.zeros((len(x) + n_tail, 2))
    out[:len(x)] += x
    for dly, g, fc, pn in echoes:
        e = pan(lp(hp(x.mean(1), 180, 2), fc, 2), pn) * undb(g)
        _add(out, e, dly)
    return reverb(out, 'hall', wet_db=wet_db, rt60=3.0, predelay=0.04)


def _jwhoosh(d, hit, r, fc, bw, k_rise, tau, pan_from, pan_to, body=0.35, body_fc=(160, 380), hiss=0.18,
             wid=0.5, zip_amp=0.0, zip_f=(380, 1500), comb=None, verb=('room', -16), taper=0.25):
    """audio._whoosh (air band + body + hiss, panned) with the dry pass tapered to exactly 0 inside d, so the
    reverb never receives a cut-off tail."""
    t = _t(d)
    ph = hit / d
    env = A._swell(t, hit, k_rise, tau)
    air = noise_band(d, r, fc, bw, width=wid, comb=comb) * env[:, None]
    bfc = [(0, body_fc[0]), (ph, body_fc[1]), (1, body_fc[0])]
    lo = noise_band(d, r, bfc, 0.8, width=0.3) * A._swell(t, hit, k_rise * 0.8, tau * 1.4)[:, None] * body
    hs = noise_band(d, r, [(0, 6000), (ph, 9500), (1, 7000)], 0.6, width=0.9)
    hs = hs * (A._swell(t, hit, k_rise * 1.6, tau * 0.6) ** 1.5)[:, None] * hiss
    st = air + lo + hs
    if zip_amp:
        u = np.clip((t - (hit - 0.12)) / 0.16, 0, 1)
        fz = zip_f[0] * (zip_f[1] / zip_f[0]) ** (u * u * (3 - 2 * u))
        st += _st(osc(fz) * np.exp(-0.5 * ((t - hit) / 0.035) ** 2) * zip_amp)
    pw = pan_from + (pan_to - pan_from) * np.clip((t - hit * 0.45) / (d - hit * 0.45), 0, 1) ** 0.8
    st = _taper(pan(st, np.clip(pw, -1, 1)), taper)
    if verb:
        st = reverb(st, verb[0], wet_db=verb[1])
    return st


# =============================================================================================== IMPACTS
def jd_hit_hero(seed=0, tail=1.0):
    """Hero impact (~5.5 s + hall). hit = 0.003 s. Crack + punch + 31 Hz sub + anvil ring + hall bloom + rumble,
    then a tail of dying ember sparks (the signature)."""
    r = _rng(seed, 'jd_hit_hero')
    v = r.uniform(0.97, 1.03)
    d = 5.5
    t = _t(d)
    N = len(t)
    sub = osc(31.0 * v + 72.0 * np.exp(-t / 0.06)) * _ar(t, 0.002, 0.95 * tail)
    punch = osc(60.0 * v + 150.0 * np.exp(-t / 0.016)) * _ar(t, 0.0012, 0.16)
    body = _unit(lp(colored(N, r, -6.0), 600, 2)) * _ar(t, 0.001, 0.09)
    thoom = _unit(reson(r.standard_normal(N), 140.0 * v, 2.2)) * _ar(t, 0.003, 0.28)
    low = 0.95 * sub + 0.6 * punch + 0.3 * body + 0.22 * thoom
    low = shape(lp(low, 2500, 2) * 0.9, 2.0)
    low = benhance(low, 0.9, fc=100.0, band=(170.0, 800.0), drive=6.0)
    crack = _unit(bp(r.standard_normal(N), 1800, 9000)) * _ar(t, 0.0003, 0.007)
    snap = _unit(hp(r.standard_normal(N), 5000)) * _ar(t, 0.0001, 0.0022)
    ring = modal(d, [196 * v, 311 * v, 467 * v, 742 * v, 1130 * v], [0.9, 0.6, 0.4, 0.22, 0.12],
                 [1, .7, .5, .3, .15], r, split=1.2)
    st = _st(low + 0.2 * crack + 0.07 * snap + 0.05 * ring)
    air = noise_band(d, r, [(0, 3000), (0.1, 900), (1, 450)], bw=1.4, width=0.9) * _ar(t, 0.003, 0.4)[:, None]
    am = 1 + 0.25 * np.sin(TWO_PI * 1.1 * t + 0.7) * np.sin(TWO_PI * 0.45 * t)
    rum = noise_band(d, r, [(0, 150), (1, 70)], 1.1, width=0.7) * (_ar(t, 0.05, 1.3 * tail) * am)[:, None]
    sparks = np.zeros((N, 2))
    _add(sparks, _crackle(2.6, r, 150, 2500, 9000, env=lambda p: np.exp(-p * 3.0) * (p > 0.02),
                          gdur=(0.0006, 0.004)), 0.04)
    st = st + 0.08 * air + 0.15 * rum + 0.10 * sparks
    st = _taper(A.transient(st, 3.0), sec=1.8)
    wet = reverb(lp(hp(st, 140), 5500, 2) * 0.9, 'hall', wet_db=-3.0 + 2 * (tail - 1), dry=0.0)
    out = np.zeros((len(wet), 2))
    out[:N] += st
    out += wet
    return _done(out, 0.003, 4.0, 'jd_hit_hero')


def jd_hit_soft(seed=0):
    """Soft impact (~1.6 s): warm felt thump, small wood knock, air puff, studio room. hit = 0.006 s."""
    r = _rng(seed, 'jd_hit_soft')
    v = r.uniform(0.96, 1.04)
    d = 1.6
    t = _t(d)
    N = len(t)
    th = _thump(d, 62.0 * v, 46.0, 0.03, 0.12, r, attack=0.006, drive=1.8, noise=0.45, noise_lp=500.0)
    felt = _unit(bp(r.standard_normal(N), 180, 900)) * _ar(t, 0.003, 0.035) * 0.22
    knock = modal(d, [235 * v, 590 * v, 1170 * v], [0.05, 0.03, 0.016], [1, .5, .25], r, contact=0.0012) * 0.10
    mono = benhance(th, 1.1, fc=110.0, band=(170.0, 700.0), drive=6.0) + felt + knock
    puff = noise_band(d, r, [(0, 1600), (1, 700)], bw=1.2, width=0.6) * _ar(t, 0.006, 0.07)[:, None] * 0.12
    st = reverb(_st(mono) + puff, 'studio', wet_db=-11, send_hp=150)
    return _done(st, 0.006, -3.0, 'jd_hit_soft')


def jd_sub_drop(seed=0, dur=1.6):
    """Sub pitch dive 92 -> 29 Hz (dur s) with oversampled saturation harmonics for phones. hit = 0.008 s."""
    r = _rng(seed, 'jd_sub_drop')
    v = r.uniform(0.97, 1.03)
    dur = max(0.4, float(dur))
    t = _t(dur)
    k = dur / 1.6
    f = 29.0 * v + 63.0 * np.exp(-t / (0.28 * k))
    rel = np.clip((dur - t) / min(0.3, 0.3 * dur), 0, 1)
    env = _ar(t, 0.008, 0.55 * k) * (0.5 - 0.5 * np.cos(np.pi * rel))
    s = osc(f) * env
    x = 0.85 * shape(s, 2.2) + 0.22 * shape(s, 3.0, 0.2)
    x = benhance(x, 1.3, fc=100.0, band=(150.0, 600.0), drive=8.0)
    puff = _unit(lp(r.standard_normal(len(t)), 380, 2)) * _ar(t, 0.003, 0.05) * 0.16
    return _done(_st(x + puff), 0.008, -2.0, 'jd_sub_drop')


def jd_heartbeat(seed=0, n=1, bpm=60.0):
    """Deep cinematic heartbeat: n lub-dubs at bpm with chest resonance. hit = first lub (0.006 s)."""
    r = _rng(seed, 'jd_heartbeat')
    n = max(1, int(n))
    period = 60.0 / float(bpm)
    gap = 0.30 * math.sqrt(60.0 / float(bpm))
    d = (n - 1) * period + gap + 1.0
    x = np.zeros(_n(d))
    for k in range(n):
        j = r.uniform(-0.004, 0.004) if k else 0.0
        for off, amp, fe in ((0.0, 1.0, 42.0), (gap, 0.58, 50.0)):
            th = _thump(0.55, fe * r.uniform(0.97, 1.03), 40.0, 0.024, 0.085, r, attack=0.005, drive=2.4,
                        noise=0.5, noise_lp=200.0, click=0.12, click_band=(220.0, 900.0))
            _add(x, th * amp * r.uniform(0.93, 1.0), 0.002 + k * period + off + j)
    x = x + 0.35 * reson(x, 92.0, 3.0)
    x = benhance(x, 1.6, fc=120.0, band=(170.0, 600.0), drive=7.0)
    st = reverb(lp(x, 950, 2), 'dark', wet_db=-14)
    return _done(st, 0.006, -3.0, 'jd_heartbeat')


def jd_floodlight_clunk(seed=0):
    """Stadium floodlight contactor (~6 s with the stand echoes and hall): heavy clunk + anvil ring + spring rattle + contact zap, then the
    ballast hum swells (3 lamps), echoing off the stands. hit = 0.003 s."""
    r = _rng(seed, 'jd_floodlight_clunk')
    v = r.uniform(0.97, 1.03)
    d = 4.8
    t = _t(d)
    N = len(t)
    cl = np.zeros(_n(1.6))
    tc = _t(1.6)
    _add(cl, _thump(0.8, 68.0 * v, 70.0, 0.02, 0.13, r, attack=0.0015, drive=2.2, noise=0.5, noise_lp=700.0,
                    click=0.3, click_band=(800.0, 4000.0)) * 0.9, 0.0)
    cl += modal(1.6, [182 * v, 409 * v, 688 * v, 1043 * v, 1529 * v, 2230 * v], [0.32, 0.22, 0.16, 0.11, 0.08, 0.05],
                [1, .8, .6, .45, .3, .2], r, split=2.0, contact=0.0008) * 0.22
    cl += _unit(bp(r.standard_normal(len(tc)), 2000, 8000)) * _ar(tc, 0.0002, 0.003) * 0.25
    for k in range(7):
        tk = 0.008 + k * 0.006 + r.uniform(0, 0.003)
        _add(cl, _click(0.02, r, (2000, 8000), 0.0006, [(3100 * r.uniform(0.9, 1.1), 0.004, 0.3)])
             * 0.25 * math.exp(-k / 3.0), tk)
    cl = shape(lp(cl, 6000, 2), 1.6)
    hum = np.zeros(N)
    swell = _smoothstep((t - 0.05) / 1.25) * np.where(t < 2.4, 1.0, np.exp(-(t - 2.4) / 0.8))
    for lamp in range(3):
        f0 = 100.0 * (1 + r.uniform(-0.002, 0.002))
        hum += harm(np.full(N, f0), [1, .45, .3, .2, .14, .1, .07, .05], fmax=5000, rng=r) * (0.8 + 0.2 * lamp / 2)
    hum *= swell * 0.05
    mono = np.zeros(N)
    _add(mono, cl, 0.0015)
    mono = _taper(mono + hum, sec=0.9)
    st = _stadium(mono, r, wet_db=-9.0)
    return _done(st, 0.003, 0.0, 'jd_floodlight_clunk')


# =============================================================================================== TRANSITIONS
def jd_whoosh_short(seed=0, direction=1):
    """Short warm whoosh (~0.56 s + room) with an ember sizzle trail. hit = 0.28 s (the pass)."""
    r = _rng(seed, 'jd_whoosh_short')
    d, hit = 0.56, 0.28
    ph = hit / d
    st = _jwhoosh(d, hit, r, [(0, 300), (ph, 2400), (1, 900)], [(0, 1.3), (ph, 0.95), (1, 1.4)], 2.4, 0.08,
                   -0.55 * direction, 0.6 * direction, body=0.5, body_fc=(120, 300), hiss=0.12, wid=0.55,
                   verb=('room', -15))
    out = _pad(st, len(st) + _n(0.5))
    trail = _crackle(0.45, r, 240, 3000, 9000, env=lambda p: np.exp(-p * 4.0), gdur=(0.0005, 0.003))
    _add(out, pan(trail, 0.6 * direction) * 0.08, hit)
    return _done(out, hit, -3.0, 'jd_whoosh_short')


def jd_whoosh_long(seed=0, dur=2.4, direction=1):
    """Long cinematic whoosh (dur s + hall): flanged swell, deep body, ember crackle trail. hit = 0.58 * dur."""
    r = _rng(seed, 'jd_whoosh_long')
    d = max(1.0, float(dur))
    hit = 0.58 * d
    ph = hit / d
    st = _jwhoosh(d, hit, r, [(0, 150), (ph, 1500), (1, 420)], [(0, 1.4), (ph, 1.0), (1, 1.5)], 1.7,
                   0.26 * d / 2.4, -0.5 * direction, 0.5 * direction, body=0.55, body_fc=(80, 220), hiss=0.09,
                   wid=0.75, comb=([(0, 0.005), (ph, 0.0011), (1, 0.0032)], 0.4), verb=('hall', -10))
    out = _pad(st, max(len(st), _n(hit + 1.4)))
    trail = _crackle(1.3, r, 120, 2500, 8500, env=lambda p: np.exp(-p * 3.0), gdur=(0.0005, 0.004))
    _add(out, pan(trail, 0.5 * direction) * 0.07, hit * 0.98)
    return _done(out, hit, -5.0, 'jd_whoosh_long')


def jd_whip(seed=0, direction=1):
    """Whip pan (~0.34 s + room): bright fast sweep 700 Hz -> 6 kHz, zip, cloth-snap crack on the pass.
    hit = 0.16 s."""
    r = _rng(seed, 'jd_whip')
    d, hit = 0.34, 0.16
    ph = hit / d
    st = _jwhoosh(d, hit, r, [(0, 700), (ph * 0.7, 1700), (ph, 6000), (1, 3000)], [(0, 1.0), (ph, 0.7), (1, 1.1)],
                   3.6, 0.03, -0.7 * direction, 0.75 * direction, body=0.35, body_fc=(200, 480), hiss=0.25,
                   wid=0.35, zip_amp=0.05, zip_f=(500, 2000), verb=('room', -17))
    tt = _t(d)
    crack = _unit(bp(r.standard_normal(len(tt)), 1500, 7000)) * _ar(tt, 0.0004, 0.003, hit - 0.001) * 0.35
    st[:len(tt)] += pan(crack, 0.3 * direction)
    return _done(st, hit, -3.0, 'jd_whip')


RISER_BARS = (1, 2, 4, 8)


def riser_len(bars, bpm):
    """Length (s) of jd_riser(bars, bpm): bars of 4/4 at bpm."""
    return int(bars) * 4 * 60.0 / float(bpm)


def _riser_grid(B):
    """Pulse grid [(beat, step)] for a B-beat riser: 1/4 notes over the first half, 1/8 over the third quarter,
    1/16 up to the last beat and 1/32 in the last beat. A 1-bar riser (B=4) compresses the end: 1/16 over the
    first half of the last beat, 1/32 over its second half (so every riser has all four stages)."""
    out, b = [], 0.0
    while b < B - 1e-9:
        rem = B - b
        step = 1.0 if rem > B / 2 else (0.5 if rem > B / 4 else (0.25 if rem > min(1.0, B / 8) else 0.125))
        out.append((b, step))
        b += step
    return out


def jd_riser(seed=0, bars=4, bpm=90.0):
    """Bar-locked riser: exactly bars * 4 beats at bpm (bars 1|2|4|8, bpm 60-120). Noise sweep 200 Hz -> 9.5 kHz,
    Shepard glide (endless rise), grid pulses accelerating 1/4 -> 1/8 -> 1/16 -> 1/32 on the beat grid
    (_riser_grid), sub swell and a reverse cymbal into the end. hit = the END (lands on the downbeat after the last
    bar). The noise sweep is gated by the same grid (depth 30 %, rising to 60 % between 58 % and 85 % of the length):
    it crosses the pulse band (1.2-4.5 kHz) in the second half and would otherwise mask the 1/16 stage. Measured
    (selftest): every pulse onset after the first is >= 3 dB above the 15 ms before it (800 Hz-12 kHz), and every
    stage with >= 8 pulses shows envelope modulation at its pulse rate >= 10 dB above the neighbouring rates."""
    bars = int(bars)
    bpm = float(bpm)
    if bars not in RISER_BARS:
        raise ValueError('jd_riser bars must be one of %s (got %r)' % (RISER_BARS, bars))
    if not 60.0 <= bpm <= 120.0:
        raise ValueError('jd_riser bpm must be 60-120 (got %r); for 150 BPM use 75 (same grid, half-time)' % bpm)
    r = _rng(seed, 'jd_riser')
    D = riser_len(bars, bpm)
    N = int(round(D * SR))
    D = N / SR
    t = np.arange(N) / SR
    p = t / D
    beat = 60.0 / bpm
    B = bars * 4
    lvl = undb(-32.0 * (1 - p) ** 1.4) * np.clip(t / 0.3, 0, 1)
    nz = noise_band(D, r, lambda q: 200.0 * (9500.0 / 200.0) ** (q ** 1.6), lambda q: 1.1 - 0.45 * q,
                    width=lambda q: 0.2 + 0.8 * q)
    nz = _pad(nz, N) * lvl[:, None]
    # Shepard glide: 7 octave-spaced partials rising, raised-cosine weight over the octave stack
    K, f_lo = 7, 55.0
    octs = 0.75 * math.sqrt(bars)
    shep = np.zeros(N)
    pr = p ** 1.3
    for k in range(K):
        pos = np.mod(k + octs * pr + r.uniform(0, 0.02), K)
        f = f_lo * 2.0 ** pos
        w = np.sin(np.pi * pos / K) ** 2
        shep += w * np.sin(TWO_PI * np.cumsum(f) / SR)
    shep *= 0.35 * lvl
    # grid pulses
    src = noise_band(D, r, lambda q: 1200.0 * (4500.0 / 1200.0) ** q, 0.6)
    src = _pad(src, N)
    penv = np.zeros(N)
    gsh = np.ones(N)                                  # per-step gate shape: 3 ms rise, decay over the step
    for b, step in _riser_grid(B):
        i0 = int(round(b * beat * SR))
        seg = min(N - i0, int(round(step * beat * SR)))
        if seg <= 2:
            continue
        tt = np.arange(seg) / SR
        e = _ar(tt, 0.002, 0.35 * step * beat) * _taper(np.ones(seg), sec=min(0.004, seg / SR / 3))
        penv[i0:i0 + seg] += e * (1.15 if (step == 1.0 or b % 1 == 0) else 1.0)
        gsh[i0:i0 + seg] = _ar(tt, 0.003, 0.45 * step * beat)
    pulses = src * penv * lvl
    # grid gate on the noise sweep (keeps the 1/16 and 1/32 stages audible where the sweep crosses the pulse band)
    depth = np.maximum(0.35, 0.6 * _smoothstep((p - 0.3) / 0.55))    # 35 %, rising to 60 % by 85 % of D
    nz = nz * (1.0 - depth * (1.0 - gsh))[:, None]
    # reverse cymbal into the end
    rc_len = beat * (1.0 if bars < 4 else 1.5)
    nrc = _n(rc_len)
    rc = noise_band(rc_len, r, [(0, 4000), (1, 9000)], 0.9, width=0.8)
    rc = _pad(rc, nrc) * (np.linspace(0, 1, nrc) ** 3)[:, None]
    # sub swell over the last 2 beats
    ns = min(N, _n(2 * beat))
    ts = np.arange(ns) / SR
    sub = osc(38.0 + 24.0 * ts / ts[-1]) * (ts / ts[-1]) ** 2
    st = 0.75 * nz + 0.22 * decorrelate(shep, r, 0.5) + _st(0.30 * pulses)
    st[N - nrc:] += 0.42 * rc[-min(nrc, N):]
    st[N - ns:] += _st(0.18 * sub)
    st = reverb(st, 'plate', wet_db=-12, hard_end=True)[:N]
    st = _fade(st, 0.01, 0.004)
    return _done(st, D, -4.0, 'jd_riser', trim=False, fin=0.01, fout=0.004)


def jd_reverse_swell(seed=0, duration=1.5):
    """Reverse swell (duration s): reversed hall bloom of a soft hit + crash, with an ember crackle that
    accelerates into the hit. hit = the END. Mono-safe (_mono_safe: lows mono below 250 Hz, side <= 0.45 x mid):
    the (L+R)/2 fold-down loses ~1 dB instead of 2.5-3.7 dB."""
    r = _rng(seed, 'jd_reverse_swell')
    d = max(0.3, float(duration))
    src_d = 0.5
    ts = _t(src_d)
    M = len(ts)
    src = _thump(src_d, 66.0, 60.0, 0.02, 0.08, r, drive=1.5, noise=0.5) * 0.55
    src += _unit(hp(r.standard_normal(M), 2800)) * _ar(ts, 0.001, 0.07) * 0.6
    src += modal(src_d, [1650, 2780, 4300, 6500, 8900], [0.25, 0.18, 0.12, 0.08, 0.05], [1, .7, .5, .3, .2], r) * 0.22
    wet = reverb(src, 'hall', wet_db=0.0, dry=0.0, rt60=max(1.8, d * 1.3), predelay=0.0, build=0.005)
    env = A._smooth(np.abs(wet).max(1), 0.01)
    wet = wet[int(np.argmax(env[:_n(0.2)])):]
    n = _n(d)
    st = _pad(wet, n)[::-1].copy() * (np.linspace(0, 1, n) ** 1.3)[:, None]
    ck = _crackle(min(d, 1.2), r, 260, 2500, 9500, env=lambda q: np.exp(-q * 4.0), gdur=(0.0005, 0.003))[::-1]
    _add(st, ck * 0.06, d - len(ck) / SR)
    st = _mono_safe(st)        # the reversed wet-only hall is near-uncorrelated / anti-correlated: phone mono
    st = _fade(st, 0.02, 0.003)
    return _done(st, d, -4.0, 'jd_reverse_swell', trim=False, fin=0.02, fout=0.003)


def _groove_at(tau, r, hats):
    """A short D-minor groove evaluated analytically at tape time tau (s): chord + bass + kick; hats are read
    from a noise buffer (varispeed). Used by jd_tape_stop."""
    out = np.zeros_like(tau)
    for f, a in ((146.83, .5), (174.61, .35), (220.0, .35), (293.66, .25), (73.42, .55)):
        for k in range(1, 7):
            out += a * k ** -1.3 * np.sin(TWO_PI * f * k * tau + r.uniform(0, TWO_PI))
    out *= 0.25
    beat = 60.0 / 90.0
    for kb in range(int(np.max(tau) / beat) + 2):
        u = tau - kb * beat
        m = u > 0
        uu = np.where(m, u, 0.0)
        phs = TWO_PI * (48.0 * uu + 110.0 * 0.03 * (1 - np.exp(-uu / 0.03)))
        out += 0.9 * np.where(m, np.sin(phs) * np.exp(-uu / 0.15) * (1 - np.exp(-uu / 0.002)), 0.0)
    return out + hats


def jd_tape_stop(seed=0, dur=0.8):
    """Tape stop (dur s + clunk): a held D-minor groove slows to a halt (pitch and speed -> 0, level and highs
    falling), then the pinch roller releases. hit = 0.0 (the moment the stop starts)."""
    r = _rng(seed, 'jd_tape_stop')
    D = max(0.25, float(dur))
    d = D + 0.35
    t = _t(d)
    N = len(t)
    rate = np.where(t < D, (1 - np.clip(t / D, 0, 1)) ** 1.6, 0.0)
    tau0 = 0.37
    tau = tau0 + np.cumsum(rate) / SR - rate[0] / SR
    hat_buf = np.zeros(_n(tau0 + D + 0.5))
    hb = _t(0.05)
    for kh in range(int((tau0 + D + 0.4) / (60.0 / 180.0)) + 1):
        _add(hat_buf, _unit(bp(r.standard_normal(len(hb)), 6000, 15000)) * _ar(hb, 0.0005, 0.012) * 0.25,
             kh * 60.0 / 180.0)
    hats = varread(hat_buf, tau * SR)
    y = _groove_at(tau, r, hats) * rate ** 0.55
    y = tvf(y, lp_mask(lambda p: 150.0 + 16000.0 * np.interp(p * d, t, rate) ** 1.5, 1.5))
    y += osc(600.0 * rate ** 1.5 + 1e-3) * rate * 0.02
    clunk = _thump(0.3, 70.0, 40.0, 0.015, 0.05, r, attack=0.002, drive=1.5, noise=0.4, noise_lp=900.0,
                   click=0.4, click_band=(900.0, 4000.0)) * 0.18
    _add(y, clunk, D)
    st = reverb(decorrelate(y, r, 0.3), 'room', wet_db=-18)
    return _done(st, 0.0, -4.0, 'jd_tape_stop', fin=0.004)


def tape_stop_fx(x, t0, dur=0.8, curve=1.6):
    """Apply a tape stop to a real buffer (e.g. a music bed or stem) at t0 s: untouched before t0, slowing to a
    halt over dur (rate = (1 - u)^curve, level ~ rate^0.55, highs closing), silence after. Alias-safe (8x cubic
    varispeed). Returns a new float64 array of the same shape."""
    x = np.asarray(x, dtype=np.float64)
    i0 = _n(t0)
    n = _n(dur)
    y = x.copy()
    y[i0:] = 0.0
    if i0 >= len(x):
        return y
    u = np.arange(n) / n
    rate = (1 - u) ** curve
    pos = np.cumsum(rate) - rate[0]
    seg = _pad(x[i0:i0 + int(pos[-1]) + 64], int(pos[-1]) + 64)
    s = varread(seg, pos)
    amp = rate ** 0.55
    s = s * (amp[:, None] if s.ndim == 2 else amp)
    s = tvf(s, lp_mask(lambda p: 150.0 + 19000.0 * np.interp(p, u, rate) ** 1.5, 1.5))
    s = _fade(s, 0.0, 0.004)
    m = min(n, len(y) - i0)
    y[i0:i0 + m] = s[:m]
    return y


def jd_power_down(seed=0, dur=1.6):
    """Power cut (dur s + tail): relay clack, 100 Hz hum and a coil whine winding down, fan spinning down.
    hit = 0.001 s (the clack)."""
    r = _rng(seed, 'jd_power_down')
    D = max(0.4, float(dur))
    d = D + 0.6
    t = _t(d)
    N = len(t)
    u = np.clip(t / D, 0, 1)
    v = r.uniform(0.97, 1.03)
    hum = harm(28.0 + 72.0 * (1 - u) ** 1.8, [1, .55, .42, .3, .22, .16, .12, .09, .07, .05], fmax=3000, rng=r)
    hum *= (1 - u) ** 1.2 * 0.35
    whine = osc(280.0 + 2100.0 * v * (1 - u) ** 2.2) * (1 - u) ** 1.6 * 0.06
    fan = noise_band(d, r, lambda q: 180.0 + 1200.0 * (1 - np.clip(q * d / D, 0, 1)) ** 1.5, 0.9, width=0.5)
    fan = _pad(fan, N) * (((1 - u) ** 1.3) * 0.08)[:, None]
    mono = (hum + whine) * _ar(t, 0.003, 1e9)
    clack = _click(0.08, r, (1500, 7000), 0.0012, [(1100 * v, 0.010, 0.5), (2700 * v, 0.006, 0.3)],
                   low=(140.0, 0.015, 0.6))
    _add(mono, clack * 0.9, 0.0005)
    tick = _click(0.03, r, (3000, 9000), 0.0006, [(5200, 0.004, 0.2)]) * 0.12
    _add(mono, tick, D * 0.92)
    st = reverb(_st(mono) + fan, 'room', wet_db=-16)
    return _done(st, 0.001, -4.0, 'jd_power_down', fin=0.0002)


def jd_power_up(seed=0, dur=1.4):
    """Power up (dur s + tail): relay thunk, coil whine and hum spinning up, fan rising, then the "on" thoom
    + zap at the hit. hit = dur (the END of the spin-up: cue it on the frame the lights/screen come alive)."""
    r = _rng(seed, 'jd_power_up')
    D = max(0.4, float(dur))
    d = D + 1.0
    t = _t(d)
    N = len(t)
    u = np.clip(t / D, 0, 1)
    ramp = (1 - np.exp(-3.0 * u)) / (1 - math.exp(-3.0))
    after = np.where(t <= D, 1.0, np.exp(-(t - D) / 0.35))
    v = r.uniform(0.94, 1.06)
    whine = osc((300.0 + 2900.0 * ramp) * v) * (u ** 1.2) * after * 0.05
    hum = harm((30.0 + 70.0 * u ** 0.7) * r.uniform(0.99, 1.01), [1, .5, .38, .27, .2, .14, .1, .07], fmax=3000, rng=r)
    hum *= u ** 1.5 * after * 0.3
    fan = noise_band(d, r, lambda q: 200.0 + 1300.0 * np.clip(q * d / D, 0, 1) ** 1.2, 0.9, width=0.5)
    fan = _pad(fan, N) * ((u ** 1.3) * after * 0.07)[:, None]
    mono = whine + hum
    _add(mono, _click(0.08, r, (1500, 7000), 0.0012, [(1050, 0.010, 0.5), (2600, 0.006, 0.3)],
                      low=(130.0, 0.015, 0.6)) * 0.7, 0.001)
    th = _thump(0.7, 55.0 * v, 60.0 * r.uniform(0.85, 1.15), 0.03, 0.18, r, attack=0.002, drive=1.8, noise=0.35)
    tz = _t(0.3)
    zap = _unit(bp(r.standard_normal(len(tz)), 2000, 8000)) * _ar(tz, 0.0005, 0.025) * 0.25
    ping = modal(0.6, [3100, 4700, 6900], [0.12, 0.08, 0.05], [1, .5, .3], r) * 0.08
    _add(mono, benhance(th, 1.0, fc=110.0, band=(160.0, 700.0), drive=5.0), D)
    _add(mono, zap, D)
    _add(mono, ping, D)
    st = reverb(_taper(_st(mono) + fan, sec=0.35), 'room', wet_db=-15)
    return _done(st, D, -4.0, 'jd_power_up', keep_until=D + 0.5)


def jd_crt_collapse(seed=0):
    """CRT switch-off (~1.6 s): power switch, the 15.625 kHz (PAL) flyback whine dies, the picture collapses with a
    falling "thwup" (900 -> 40 Hz) and a yoke thump, then high-voltage static crackle. hit = 0.001 s."""
    r = _rng(seed, 'jd_crt_collapse')
    d = 1.6
    t = _t(d)
    N = len(t)
    wf = 15625.0 * (1 - r.uniform(0.015, 0.03) * np.clip(t / 0.25, 0, 1))
    mono = osc(wf) * np.exp(-t / 0.09) * 0.05 * np.clip(t / 0.001, 0, 1)
    tc = r.uniform(0.012, 0.018)
    uu = np.clip((t - tc) / (0.2 * r.uniform(0.85, 1.15)), 0, 1)
    mono += osc(40.0 + 860.0 * r.uniform(0.85, 1.15) * (1 - uu) ** 2.5) * _ar(t, 0.002, 0.09, tc) * 0.5
    _add(mono, _thump(0.5, 48.0, 40.0, 0.03, 0.12, r, drive=1.8) * 0.6, tc)
    _add(mono, _click(0.06, r, (1500, 8000), 0.0012, [(1300, 0.01, 0.4), (2500, 0.006, 0.25)],
                      low=(170.0, 0.012, 0.5)) * 0.8, 0.0005)
    st = _st(mono)
    st += noise_band(d, r, 6000.0, 0.6, width=0.5) * _ar(t, 0.003, 0.25, 0.02)[:, None] * 0.04
    _add(st, _crackle(1.2, r, 380, 1500, 9500, env=lambda q: np.exp(-q * 3.5), gdur=(0.0004, 0.003)) * 0.25, 0.03)
    st = reverb(st, 'room', wet_db=-18)
    return _done(st, 0.001, -4.0, 'jd_crt_collapse', fin=0.0002)


def jd_revolving_door(seed=0, duration=2.0, wings=3, direction=1):
    """Revolving door (duration s): one air whoosh per wing pass (the middle pass is the loudest), rubber seals
    brushing the drum, the turning mass, and the outside world muffling as you pass through.
    hit = 0.5 * duration (the middle pass)."""
    r = _rng(seed, 'jd_revolving_door')
    D = max(0.8, float(duration))
    W = max(1, int(wings))
    d = D + 0.6
    t = _t(d)
    N = len(t)
    hit = 0.5 * D
    spacing = min(D / (W + 0.5), 0.9)
    passes = [hit + (k - W // 2) * spacing for k in range(W)]
    st = np.zeros((N, 2))
    near = np.zeros(N)
    for k, tp in enumerate(passes):
        mid = (k == W // 2)
        g = 1.0 if mid else r.uniform(0.5, 0.7)
        wd = 0.6
        wh = _jwhoosh(wd, 0.3, r, [(0, 260), (0.5, 1250), (1, 420)], [(0, 1.3), (0.5, 1.0), (1, 1.3)], 2.0, 0.09,
                       -0.6 * direction, 0.6 * direction, body=0.45, body_fc=(90, 240), hiss=0.08, wid=0.5,
                       verb=None)
        _add(st, wh * g, tp - 0.3)
        near += np.exp(-0.5 * ((t - tp) / 0.12) ** 2) * g
    seal = _unit(bp(r.standard_normal(N), 1000, 6000)) * (0.15 + near) * 0.05
    rum = _unit(lp(r.standard_normal(N), 120, 2)) * 0.04
    amb = _unit(lp(colored(N, r, -4.0), 1200, 2)) * 0.06
    amb = tvf(amb, lp_mask(lambda p: np.where(p * d < hit - 0.12, 3000.0,
                                              np.where(p * d > hit + 0.12, 350.0,
                                                       3000.0 * (350.0 / 3000.0) ** ((p * d - hit + 0.12) / 0.24))), 2))
    amb *= np.where(t < hit, 1.0, 0.55)
    st += _st(seal + rum + amb)
    st *= _gate(t, 0.0, D + 0.25, 0.08)[:, None]
    st = reverb(st, 'room', wet_db=-15)
    return _done(st, hit, -5.0, 'jd_revolving_door')


# ---------------------------------------------------------------------------------------------- desi (bible 4.8)
def _na_raw(r, sa, damp=1.0):
    d = 0.6
    t = _t(d)
    dv = damp * r.uniform(0.88, 1.12)                       # stroke-to-stroke variation (finger, pressure)
    am = r.uniform(0.85, 1.15, 6)
    x = modal(d, [sa * k for k in (1, 2, 3, 4, 5, 2.95)], [.30 * dv, .20 * dv, .14 * dv, .09 * dv, .06 * dv, .02],
              list(np.array([1, .62, .46, .30, .16, .12]) * am), r)
    return x + _unit(hp(r.standard_normal(len(t)), 3000)) * _ar(t, 0.0002, 0.0025) * 0.3


def _tin_raw(r, sa):
    d = 0.8
    t = _t(d)
    dv = r.uniform(0.88, 1.12)
    x = modal(d, [sa * k for k in (1, 2, 3, 4)], [.45 * dv, .2 * dv, .12 * dv, .08 * dv],
              list(np.array([1, .3, .18, .08]) * r.uniform(0.85, 1.15, 4)), r)
    return x + _unit(hp(r.standard_normal(len(t)), 3000)) * _ar(t, 0.0002, 0.002) * 0.15


def _ge_raw(r):
    d = 1.6
    t = _t(d)
    f = 88.0 * r.uniform(0.96, 1.04) + 42.0 * r.uniform(0.8, 1.2) * (1 - np.exp(-t / (0.07 * r.uniform(0.8, 1.2))))
    ph = TWO_PI * np.cumsum(f) / SR
    x = _taper((np.sin(ph) + 0.18 * np.sin(2 * ph)) * _ar(t, 0.002, 0.3 * r.uniform(0.85, 1.15)), 0.35)
    x = shape(x * 0.8, 1.5)
    x = benhance(x, 0.8, fc=140.0, band=(180.0, 700.0), drive=4.0)
    return x + _unit(hp(r.standard_normal(len(t)), 700)) * _ar(t, 0.0003, 0.004) * 0.25


def _ke_raw(r):
    d = 0.2
    t = _t(d)
    return (_unit(bp(r.standard_normal(len(t)), 200, 1500)) * _ar(t, 0.0005, 0.015) * 0.5
            + np.sin(TWO_PI * 120.0 * t) * _ar(t, 0.001, 0.025) * 0.4)


def jd_tabla_na(seed=0, sa=293.66):
    """Tabla 'na' (dayan rim stroke) tuned to Sa: harmonic modes 1-5 + 2.95 + click. hit = 0.0."""
    r = _rng(seed, 'jd_tabla_na')
    st = reverb(_st(_na_raw(r, sa * r.uniform(0.997, 1.003))), 'room', wet_db=-18)
    return _done(st, 0.0, -4.0, 'jd_tabla_na', fin=0.0002)


def jd_tabla_tin(seed=0, sa=293.66):
    """Tabla 'tin' (soft open dayan stroke) tuned to Sa. hit = 0.0."""
    r = _rng(seed, 'jd_tabla_tin')
    st = reverb(_st(_tin_raw(r, sa * r.uniform(0.997, 1.003))), 'room', wet_db=-18)
    return _done(st, 0.0, -8.0, 'jd_tabla_tin', fin=0.0002)


def jd_tabla_ge(seed=0):
    """Tabla 'ge' (bayan bass stroke) with the upward wrist-press 'wah' 88 -> 130 Hz. hit = 0.0."""
    r = _rng(seed, 'jd_tabla_ge')
    st = reverb(_st(_ge_raw(r)), 'room', wet_db=-18)
    return _done(st, 0.0, -6.0, 'jd_tabla_ge', fin=0.0002)


def jd_tabla_dha(seed=0, sa=293.66):
    """Tabla 'dha' = na + ge together (the desi hit). hit = 0.0."""
    r = _rng(seed, 'jd_tabla_dha')
    na = _na_raw(r, sa * r.uniform(0.997, 1.003))
    ge = _ge_raw(r)
    x = np.zeros(max(len(na), len(ge)))
    x[:len(na)] += 0.6 * na
    x[:len(ge)] += 0.55 * ge
    st = reverb(_st(x), 'room', wet_db=-18)
    return _done(st, 0.0, -2.0, 'jd_tabla_dha', fin=0.0002)


def jd_tabla_roll(seed=0, n=8, bpm=90.0, sa=293.66):
    """Tabla 'ti-ra-ki-ta' roll: n strokes in 32nds at bpm, crescendo -12 -> 0 dB. hit = one 32nd after the last
    stroke (the downbeat it lands on)."""
    r = _rng(seed, 'jd_tabla_roll')
    n = max(2, int(n))
    step = 60.0 / float(bpm) / 8.0
    hit = 0.002 + n * step
    x = np.zeros(_n(hit + 0.8))
    for k in range(n):
        kind = ('tin', 'na_damp', 'ke', 'na')[k % 4]
        g = undb(-12.0 + 12.0 * k / (n - 1))
        tk = 0.002 + k * step + (r.uniform(-0.003, 0.003) if k else 0.0)
        if kind == 'tin':
            s = _tin_raw(r, sa)
        elif kind == 'na':
            s = _na_raw(r, sa)
        elif kind == 'na_damp':
            s = _na_raw(r, sa, damp=0.4) * 0.8
        else:
            s = _ke_raw(r)
        _add(x, s * g, tk)
    st = reverb(_st(x), 'room', wet_db=-18)
    return _done(st, hit, -6.0, 'jd_tabla_roll', fin=0.0002)


def jd_ghungroo(seed=0):
    """Ghungroo (ankle bells) shake: 24-40 small brass bells over ~0.3 s + pellet rattle. hit = 0.0005 s."""
    r = _rng(seed, 'jd_ghungroo')
    d = 1.0
    out = np.zeros((_n(d), 2))
    nb = int(r.integers(24, 40))
    for k in range(nb):
        t0 = 0.0005 if k == 0 else 0.0005 + (r.random() ** 1.8) * 0.28
        f = math.exp(r.uniform(math.log(4200), math.log(7600)))
        bell = modal(0.25, [f, f * 1.47, f * 2.09, f * 2.56], [0.06, 0.045, 0.03, 0.02], [1, .5, .3, .2], r,
                     contact=0.0002)
        bell += _unit(hp(r.standard_normal(len(bell)), 5000)) * _ar(_t(0.25), 0.0001, 0.0006) * 0.2
        g = (1.0 if k == 0 else r.uniform(0.3, 0.9)) * math.exp(-(t0 / 0.25))
        _add(out, pan(bell * g, r.uniform(-0.6, 0.6)), t0)
    out += _grains(d, r, 40, 4500, 9500, 0.01, 0.05, density=lambda p: np.exp(-p * 6), harm=0.3) * 0.3
    st = reverb(out, 'room', wet_db=-16)
    return _done(st, 0.0005, -10.0, 'jd_ghungroo', fin=0.0002)


def jd_sparkle(seed=0):
    """FM twinkles (same recipe as audio.sparkle) computed oversampled, so no sideband folds back. hit = 0.002 s."""
    r = _rng(seed, 'jd_sparkle')
    d = 1.2
    out = np.zeros((_n(d), 2))
    t0 = 0.0
    for k in range(int(r.integers(7, 11))):
        f = math.exp(r.uniform(math.log(3400), math.log(8200)))
        x = fm_bell_os(0.5, f, ratio=1.41, index=1.2, tau=r.uniform(0.06, 0.16), tau_index=0.02, attack=0.0015)
        _add(out, pan(x * r.uniform(0.4, 1.0) * math.exp(-t0 / 0.25), r.uniform(-0.8, 0.8)), t0)
        t0 += r.uniform(0.015, 0.06)
    st = reverb(out, 'plate', wet_db=-8)
    return _done(st, 0.002, -11.0, 'jd_sparkle')


# =============================================================================================== UI / FOLEY
def jd_ui_click(seed=0, pitch=1.0):
    """Dark-glass UI click: soft transient + warm 1.45/2.9/4.7 kHz body + low tock. hit = 0.0005 s."""
    r = _rng(seed, 'jd_ui_click')
    p = float(pitch) * r.uniform(0.985, 1.015)
    x = _click(0.16, r, (1800, 8000), 0.0016, [(1450 * p, 0.016, 0.5), (2900 * p, 0.008, 0.3), (4700 * p, 0.004, 0.15)],
               low=(320.0 * p, 0.014, 0.45))
    st = reverb(decorrelate(x, r, 0.12), 'room', wet_db=-20)
    return _done(st, 0.0005, -9.0, 'jd_ui_click', fin=0.0002)


def jd_ui_tick(seed=0, pitch=1.0):
    """Tiny glassy tick (3.3 / 5.6 kHz). hit = 0.0003 s."""
    r = _rng(seed, 'jd_ui_tick')
    p = float(pitch) * r.uniform(0.985, 1.015)
    x = _click(0.09, r, (3500, 11000), 0.0008, [(3300 * p, 0.006, 0.55), (5600 * p, 0.004, 0.3)])
    st = reverb(x, 'room', wet_db=-22)
    return _done(st, 0.0003, -13.0, 'jd_ui_tick', fin=0.0003)


def jd_ui_pop(seed=0, pitch=1.0):
    """Round 'bloop' pop: sine gliding 380 -> 720 Hz in ~15 ms + soft 2nd harmonic + click. hit = 0.001 s."""
    r = _rng(seed, 'jd_ui_pop')
    p = float(pitch) * r.uniform(0.98, 1.02)
    d = 0.4
    t = _t(d)
    f = (380.0 + 340.0 * (1 - np.exp(-t / 0.012))) * p
    x = osc(f) * _ar(t, 0.0015, 0.045) + osc(2 * f) * _ar(t, 0.001, 0.02) * 0.18
    x += _unit(bp(r.standard_normal(len(t)), 2000, 7000)) * _ar(t, 0.0002, 0.0012) * 0.12
    st = reverb(decorrelate(x, r, 0.1), 'room', wet_db=-19)
    return _done(st, 0.001, -9.0, 'jd_ui_pop', fin=0.0002)


def _key_press(r, style, space=False):
    if style == 'mech':
        f1 = r.uniform(1700, 2300) * (0.75 if space else 1.0)
        x = _click(0.09, r, (1200, 7000), 0.0018, [(f1, 0.010, 0.45), (f1 * 1.61, 0.006, 0.25),
                                                    (430.0 if space else 520.0, 0.02, 0.35)],
                   low=(180.0 if space else 230.0, 0.018, 0.55))
        x = x + modal(0.09, [4100 * r.uniform(0.95, 1.05), 6350], [0.03, 0.02], [0.05, 0.03], r)
        rel = _click(0.05, r, (2500, 9000), 0.0012, [(f1 * 1.3, 0.006, 0.3)]) * 0.45
        return x, rel, r.uniform(0.07, 0.11)
    f1 = r.uniform(950, 1450) * (0.7 if space else 1.0)
    x = _click(0.07, r, (1400, 6500), 0.0025, [(f1, 0.012, 0.45), (f1 * 2.37, 0.006, 0.25)],
               low=(240.0 if space else 300.0, 0.010, 0.45 if space else 0.3))
    rel = _click(0.04, r, (2500, 8000), 0.0012, [(f1 * 1.8, 0.004, 0.2)]) * 0.35
    return x, rel, r.uniform(0.05, 0.085)


def jd_keyboard(seed=0, n=10, cps=10.0, style='laptop'):
    """Typing: n keys at ~cps with human timing, key releases, spacebar every ~6 keys. style 'laptop' (scissor
    keys) or 'mech' (thocky mechanical with spring ping). hit = first key (0.002 s)."""
    if style not in ('laptop', 'mech'):
        raise ValueError("jd_keyboard style must be 'laptop' or 'mech'")
    r = _rng(seed, 'jd_keyboard_' + style)
    n = max(1, int(n))
    d = n / float(cps) * 1.6 + 0.45
    out = np.zeros((_n(d), 2))
    t0 = 0.002
    for k in range(n):
        space = (k % 6 == 5) and r.random() < 0.8
        x, rel, rdt = _key_press(r, style, space)
        g = 1.0 if k == 0 else r.uniform(0.7, 0.95)
        pk = 0.0 if space else r.uniform(-0.3, 0.3)
        _add(out, pan(x * g, pk), t0)
        _add(out, pan(rel * g, pk), t0 + rdt)
        t0 += (1.0 / float(cps)) * r.uniform(0.6, 1.45) * (1.6 if space else 1.0)
        if t0 > d - 0.3:
            break
    st = reverb(out, 'room', wet_db=-19)
    return _done(st, 0.002, -11.0, 'jd_keyboard', fin=0.0002)


def jd_mouse_click(seed=0, double=0):
    """Mouse micro-switch: sharp press + plastic body + low tock, softer release 70-95 ms later; double=1 adds a
    second click 0.14-0.18 s later. hit = 0.0005 s."""
    r = _rng(seed, 'jd_mouse_click')
    d = 0.5 if double else 0.3
    out = np.zeros(_n(d))

    def press(t0, g):
        x = _click(0.06, r, (2000, 9000), 0.0007, [(2150 * r.uniform(0.97, 1.03), 0.006, 0.45), (3480, 0.004, 0.3),
                                                    (5900, 0.002, 0.15)], low=(260.0, 0.008, 0.4))
        _add(out, x * g, t0)
        rel = _click(0.04, r, (2800, 10000), 0.0005, [(2900, 0.004, 0.3), (6400, 0.002, 0.15)]) * 0.55
        _add(out, rel * g, t0 + r.uniform(0.07, 0.095))
    press(0.0005, 1.0)
    if double:
        press(0.0005 + r.uniform(0.14, 0.18), 0.92)
    st = reverb(decorrelate(out, r, 0.1), 'room', wet_db=-21)
    return _done(st, 0.0005, -12.0, 'jd_mouse_click', fin=0.0002)


_VOWELS = dict(a=(730, 1090, 2440), e=(530, 1840, 2480), i=(270, 2290, 3010), o=(570, 840, 2410), u=(300, 870, 2240))


def _scrub_content(d, r):
    """'Edit content' to scrub through: a male voice-like formant babble (band-limited additive glottal harmonics,
    ~5 syllables/s, fricative bursts) over a soft D-minor beat. Mono, peak ~1, low-passed at 6 kHz."""
    N = _n(d)
    t = np.arange(N) / SR
    fr = np.arange(0, d + 0.01, 0.005)
    f0 = 118.0 * (1 + 0.12 * np.sin(TWO_PI * 0.7 * fr + r.uniform(0, TWO_PI))) * (1 - 0.05 * fr / d)
    F = np.zeros((len(fr), 3))
    voiced = np.zeros(len(fr))
    fric = np.zeros(len(fr))
    tt = 0.05
    while tt < d:
        cl = r.uniform(0.03, 0.07)
        vl = r.uniform(0.08, 0.17)
        vw = _VOWELS['aeiou'[int(r.integers(0, 5))]]
        a, b, c = np.searchsorted(fr, [tt, tt + cl, tt + cl + vl])
        if r.random() < 0.45:
            fric[a:b] = r.uniform(0.4, 1.0)
        voiced[b:c] = 1.0
        F[a:c] = vw
        tt += cl + vl + (r.uniform(0.15, 0.35) if r.random() < 0.15 else r.uniform(0.0, 0.04))
    F[F[:, 0] == 0] = _VOWELS['a']
    voiced = np.convolve(voiced, np.ones(3) / 3, mode='same')
    f0s = np.interp(t, fr, f0)
    base = TWO_PI * np.cumsum(f0s) / SR
    voice = np.zeros(N)
    for k in range(1, int(5000 / 100) + 1):
        fk = k * f0
        e = np.zeros(len(fr))
        for j, bw in enumerate((80.0, 100.0, 140.0)):
            e += (1.0, 0.7, 0.4)[j] * np.exp(-0.5 * ((fk - F[:, j]) / bw) ** 2)
        e = (e + 0.03) * k ** -0.6 * voiced * np.clip((5000 - fk) / 500, 0, 1)
        voice += np.interp(t, fr, e) * np.sin(k * base)
    sss = _unit(bp(r.standard_normal(N), 3500, 7000)) * np.interp(t, fr, fric) * 0.25
    beat = 60.0 / 90.0
    music = harm(np.full(N, 146.83), [1, .4, .2, .1], fmax=3000) + harm(np.full(N, 174.61), [.7, .3, .15], fmax=3000)
    music *= 0.12
    for kb in range(int(max(0.0, d - 0.3) / beat) + 1):
        _add(music, _thump(0.3, 50.0, 90.0, 0.02, 0.09, r, drive=2.0, noise=0.2) * 0.5, kb * beat)
    x = voice / (np.max(np.abs(voice)) + 1e-9) + sss + music
    return lp(x / (np.max(np.abs(x)) + 1e-9), 6000, 4)


def jd_timeline_scrub(seed=0, duration=1.0, speed=2.0):
    """NLE audio scrub (duration s): the playhead is dragged (content speed ~speed x, with a short backward
    flick) and every video frame (30 fps) plays a 39 ms grain of the clip under it, reversed when moving
    backwards (the "chk-chk" chatter); faint drag friction, mouse-up at the end. hit = duration (end of the
    motion): cue it with align='start' at the drag start."""
    r = _rng(seed, 'jd_timeline_scrub')
    D = max(0.2, float(duration))
    fps = 30.0
    nfr = int(math.ceil(D * fps))
    kn = 6
    knots = r.uniform(0.35, 1.0, kn) * float(speed)
    knots[int(r.integers(2, kn))] *= -0.5
    pf = np.linspace(0, 1, nfr)
    vel = np.interp(pf, np.linspace(0, 1, kn), knots) * np.sin(np.pi / 2 * np.clip(pf / 0.12, 0, 1))
    pos = 0.6 + np.cumsum(vel / fps)
    pos -= min(0.0, pos.min() - 0.1)
    content = _scrub_content(float(pos.max()) + 0.4, r)
    gl = 1.0 / fps + 0.006
    ng = _n(gl)
    win = _gate(np.arange(ng) / SR, 0.0, gl, 0.003)
    out = np.zeros(_n(D + 0.2))
    for i in range(nfr):
        if abs(vel[i]) < 0.05:
            continue
        a = _n(pos[i])
        g = _pad(content[a:a + ng], ng) if vel[i] > 0 else _pad(content[max(0, a - ng):a][::-1], ng)
        _add(out, g * win * min(1.0, abs(vel[i]) / 0.5) ** 0.5, i / fps)
    t = np.arange(len(out)) / SR
    out += _unit(bp(r.standard_normal(len(out)), 600, 3000)) * np.interp(t, np.arange(nfr) / fps, np.abs(vel)) \
        * _gate(t, 0.0, D, 0.03) * 0.01
    _add(out, _click(0.04, r, (2800, 10000), 0.0005, [(2900, 0.004, 0.3)]) * 0.3, D)
    st = reverb(decorrelate(out, r, 0.2), 'room', wet_db=-20)
    return _done(st, D, -12.0, 'jd_timeline_scrub', keep_until=D)


def jd_glass_slide(seed=0, dur=0.5):
    """Glass sliding on glass (dur s): friction noise + stick-slip micro-impulses ringing the glass, moving
    left -> right; the friction stops 45-50 ms before dur, then a glassy 'tunk' lands on the hit. hit = dur (the
    landing; its first 20 ms are >= 6 dB above the 30 ms before it, and it is the loudest moment of the sound)."""
    r = _rng(seed, 'jd_glass_slide')
    dur = max(0.15, float(dur))
    v = r.uniform(0.97, 1.03)
    tail = 0.9
    d = dur + tail
    t = _t(d)
    N = len(t)
    stop = dur - min(0.05, max(0.045, 0.15 * dur))       # the glass comes to rest just before it lands
    u = np.clip(t / stop, 0, 1)
    speed = np.sin(np.pi * u ** 0.8) ** 0.7 * (t < stop)
    fr = _unit(bp(r.standard_normal(N), 900, 7000)) * speed * 0.25
    imp = np.zeros(N)
    tt = 0.002
    while tt < stop:
        s = float(np.interp(tt, t, speed))
        if s > 0.05:
            imp[int(tt * SR)] += s * r.uniform(0.5, 1.0) * (1 if r.random() < 0.5 else -1)
            tt += 1.0 / (250.0 + 900.0 * s) * r.uniform(0.7, 1.3)
        else:
            tt += 0.004
    gf = [1180 * v, 2730 * v, 4610 * v, 7050 * v, 9800 * v]
    ir = modal(0.35, gf, [0.09, 0.06, 0.04, 0.025, 0.015], [1, .7, .45, .25, .12], r, contact=0.0002)
    body = signal.fftconvolve(fr + imp * 0.6, ir)[:N] * 0.5 + fr * 0.4
    land = np.zeros(_n(tail))
    _add(land, modal(tail, [gf[0] * 0.62, gf[1] * 0.62, gf[2] * 0.62, 310 * v], [0.25, 0.14, 0.08, 0.06],
                     [0.7, .45, .25, 0.6], r, split=1.5, contact=0.0006) * 0.5, 0.0)
    _add(land, _thump(0.4, 95.0, 50.0, 0.015, 0.05, r, attack=0.002, drive=1.6, noise=0.3, noise_lp=600.0) * 0.35,
         0.0)
    # landing level is set against the friction (the convolved friction is ~30 dB hotter than a raw modal hit):
    # first 20 ms of the landing = the loudest 30 ms of friction + 4 dB
    fr30 = math.sqrt(float(A._smooth(body ** 2, 0.03).max()))
    l20 = math.sqrt(float(np.mean(land[:_n(0.02)] ** 2)))
    _add(body, land * (fr30 / l20 * undb(4.0)), dur)
    st = pan(body, np.clip(-0.4 + 0.6 * np.clip(t / dur, 0, 1), -1, 1))
    st = reverb(st, 'room', wet_db=-18)
    return _done(st, dur, -8.0, 'jd_glass_slide', keep_until=dur)


def jd_glass_clink(seed=0, pitch=1.0):
    """Two glasses clinking: inharmonic goblet modes (1, 2.32, 4.25, 6.63, 9.48) of two slightly different
    glasses beating, contact click, a micro-bounce 25-40 ms later. hit = 0.001 s."""
    r = _rng(seed, 'jd_glass_clink')
    d = 2.6
    t = _t(d)
    rat = [1.0, 2.32, 4.25, 6.63, 9.48]
    fa = 1320.0 * float(pitch) * r.uniform(0.98, 1.02)
    fb = fa * r.uniform(1.09, 1.15)
    b = r.uniform(0.025, 0.04)

    def glasses(t0, g):
        ga = modal(d, [fa * k for k in rat], [1.3, 0.7, 0.36, 0.2, 0.1], [1, .6, .38, .2, .1], r, split=2.6,
                   contact=0.00025, t0=t0)
        gb = modal(d, [fb * k for k in rat], [1.1, 0.6, 0.3, 0.17, 0.09], [0.8, .5, .3, .16, .08], r, split=3.1,
                   contact=0.00025, t0=t0)
        return (pan(ga, -0.25) + pan(gb, 0.25)) * g
    st = glasses(0.001, 1.0) + glasses(0.001 + b, 0.18)
    st += _st(_unit(bp(r.standard_normal(len(t)), 3000, 11000)) * _ar(t, 0.0001, 0.0008, 0.0005) * 0.25)
    st = reverb(st, 'plate', wet_db=-20, send_hp=500)
    return _done(st, 0.001, -8.0, 'jd_glass_clink', fin=0.0002)


def jd_ups_beep(seed=0, n=3, period=1.2, pitch=1.0, relay=1):
    """Load-shedding UPS: relay switch-over 'tak-tak' + inverter buzz (relay=1), then n piezo beeps (2.95 kHz,
    band-limited square) every period s. hit = the relay (0.001 s), or the first beep when relay=0."""
    r = _rng(seed, 'jd_ups_beep')
    n = max(1, int(n))
    f0 = 2950.0 * float(pitch) * r.uniform(0.99, 1.01)
    bl = 0.2
    t1 = 0.16 if relay else 0.001
    d = t1 + (n - 1) * float(period) + bl + 0.45
    x = np.zeros(_n(d))
    tb = _t(bl + 0.01)
    for k in range(n):
        tone = harm(np.full(len(tb), f0), [1, 0, 1 / 3., 0, 1 / 5., 0, 1 / 7.], fmax=16000)
        tone = 0.7 * tone + 0.3 * reson(tone, f0, 6.0)
        _add(x, tone * _gate(tb, 0.0, bl, 0.003) * 0.5, t1 + k * float(period))
    if relay:
        for dt, g in ((0.0005, 1.0), (0.0125, 0.6)):
            _add(x, _click(0.05, r, (1500, 7000), 0.0010, [(1250, 0.008, 0.45), (2650, 0.005, 0.25)],
                           low=(150.0, 0.012, 0.5)) * g, dt)
        tz = _t(0.35)
        _add(x, _taper(harm(np.full(len(tz), 100.0), [1, .5, .35, .25, .18, .12, .08], fmax=4000)
                       * _ar(tz, 0.005, 0.12), 0.3) * 0.05, 0.002)
    st = reverb(_st(x), 'room', wet_db=-18)
    return _done(st, 0.001 if relay else t1, -12.0, 'jd_ups_beep', fin=0.0002)


def jd_vn_blip(seed=0, pitch=1.0):
    """Voice-note mic blip: soft 1.32 kHz 'bip' gliding up 3 semitones + low button tock. hit = 0.001 s."""
    r = _rng(seed, 'jd_vn_blip')
    p = float(pitch) * r.uniform(0.99, 1.01)
    d = 0.35
    t = _t(d)
    f = 1320.0 * p * 2.0 ** (3.0 / 12.0 * np.clip(t / 0.015, 0, 1))
    x = osc(f) * _ar(t, 0.002, 0.03) + osc(2 * f) * _ar(t, 0.002, 0.015) * 0.12
    x += osc(np.full(len(t), 300.0)) * _ar(t, 0.0008, 0.008) * 0.3
    st = reverb(decorrelate(x, r, 0.1), 'room', wet_db=-20)
    return _done(st, 0.001, -12.0, 'jd_vn_blip', fin=0.0002)


def jd_vn_record(seed=0, duration=1.5):
    """Voice-note record start: two rising pips (A5 -> D6) then open-mic air for duration, soft tick at the end.
    hit = 0.001 s (record starts)."""
    r = _rng(seed, 'jd_vn_record')
    D = max(0.3, float(duration))
    d = D + 0.3
    t = _t(d)
    x = np.zeros(len(t))
    p = r.uniform(0.985, 1.015)
    for t0, f, ln in ((0.001, 880.0 * p, 0.06 * r.uniform(0.9, 1.1)), (0.075, 1174.66 * p, 0.08 * r.uniform(0.9, 1.1))):
        tt = _t(ln + 0.05)
        _add(x, (osc(np.full(len(tt), f)) + 0.08 * osc(np.full(len(tt), 3 * f))) * _gate(tt, 0.0, ln, 0.003)
             * np.exp(-tt / 0.08), t0)
    st = _st(x * 0.5)
    air = noise_band(d, r, 2500.0, 1.5, width=0.4) * (_gate(t, 0.12, D, 0.08) * 0.012)[:, None]
    st += air
    _add(st, _st(_click(0.03, r, (3000, 9000), 0.0006, [(4200, 0.004, 0.2)]) * 0.15), D)
    st = reverb(st, 'room', wet_db=-20)
    return _done(st, 0.001, -12.0, 'jd_vn_record', fin=0.0002, keep_until=D)


def jd_vn_send(seed=0):
    """Voice-note send: tap, quick upward swish + glide, small landing pop at ~0.27 s. hit = 0.0005 s (the tap)."""
    r = _rng(seed, 'jd_vn_send')
    d = 0.7
    t = _t(d)
    st = np.zeros((len(t), 2))
    _add(st, _st(_click(0.05, r, (2200, 8000), 0.0009, [(1700, 0.008, 0.4)], low=(300.0, 0.008, 0.3))), 0.0005)
    sw_d = 0.22
    sw = noise_band(sw_d, r, [(0, 1500), (1, 6500)], 0.6, width=0.6)
    tw = _t(sw_d)
    sw = _pad(sw, len(tw)) * (np.sin(np.pi * np.clip(tw / sw_d, 0, 1)) ** 2 * 0.35)[:, None]
    sw += _st(osc(600.0 + 1200.0 * np.clip(tw / 0.12, 0, 1)) * _gate(tw, 0.0, 0.14, 0.01) * 0.08)
    _add(st, pan(sw, 0.3), 0.02)
    tp = _t(0.3)
    pp = osc((500.0 + 450.0 * (1 - np.exp(-tp / 0.01)))) * _ar(tp, 0.0015, 0.03) * 0.5
    _add(st, _st(pp), 0.27)
    st = reverb(st, 'room', wet_db=-20)
    return _done(st, 0.0005, -10.0, 'jd_vn_send', fin=0.0002)


# =============================================================================================== TEXTURES
def _proj_tick(r, accent):
    x = _click(0.03, r, (1800, 7000), 0.0014, [(1900 * r.uniform(0.96, 1.04), 0.006, 0.4), (3300, 0.004, 0.25)],
               low=(160.0, 0.006, 0.3 if accent else 0.18))
    return x * (1.0 if accent else 0.6)


def jd_projector(seed=0, duration=2.5, spinup=0.9):
    """Film projector start (duration s): switch, motor spinning up to 24 fps (claw + shutter clatter, motor
    hum, belt whine, fan), running, then fading. hit = spinup (the moment it reaches 24 fps)."""
    r = _rng(seed, 'jd_projector')
    su = max(0.2, float(spinup))
    D = max(float(duration), su + 0.3)
    d = D + 0.35
    t = _t(d)
    N = len(t)
    s = _smoothstep(t / su)
    ev = np.cumsum(24.0 * s) / SR * 2.0
    idx = np.nonzero(np.diff(np.floor(ev)) > 0)[0] + 1
    x = np.zeros(N)
    for j, i in enumerate(idx):
        if t[i] > D:
            break
        _add(x, _proj_tick(r, j % 2 == 0) * (0.4 + 0.6 * s[i]) * r.uniform(0.85, 1.0), t[i])
    x += harm(48.0 * s + 1e-3, [1, 0.6, 0.35, 0.2, 0.12, 0.08], fmax=8000, rng=r) * 0.10 * s
    x += osc(880.0 * s + 1e-3) * 0.02 * s ** 2
    fan = tvf(_unit(lp(colored(N, r, -2.0), 3000, 2)), lp_mask(lambda p: 300.0 + 1700.0 * np.interp(p * d, t, s)))
    x += fan * 0.05 * s
    _add(x, _click(0.05, r, (1500, 7000), 0.002, [(1200, 0.01, 0.4)], low=(150.0, 0.01, 0.5)) * 0.8, 0.001)
    x *= np.where(t <= D, 1.0, np.clip(1 - (t - D) / 0.3, 0, 1) ** 2)
    st = reverb(decorrelate(x, r, 0.3), 'room', wet_db=-18)
    return _done(st, su, -8.0, 'jd_projector', keep_until=D)


def jd_fluoro_flicker(seed=0, dur=2.2):
    """Fluorescent tube starting (dur s): starter ticks, buzzing 100 Hz flickers (50 Hz mains), then it catches
    into a steady hum with settling arc sizzle. hit = 0.55 * dur (the moment it catches)."""
    r = _rng(seed, 'jd_fluoro_flicker')
    D = max(0.8, float(dur))
    tc = 0.55 * D
    d = D + 0.1
    t = _t(d)
    N = len(t)
    buzz = harm(np.full(N, 100.0), [1, .7, .5, .42, .33, .27, .2, .16, .13, .1, .08, .06, .05, .04], fmax=6000, rng=r)
    sizz = _unit(hp(r.standard_normal(N), 2500)) * (0.5 + 0.5 * np.sin(TWO_PI * 100.0 * t)) ** 4 * 0.15
    gate = np.zeros(N)
    ticks = np.zeros(N)
    for tb in sorted(r.uniform(0.05, tc - 0.12, int(r.integers(3, 6)))):
        ln = r.uniform(0.03, 0.09)
        gate += _gate(t, tb, tb + ln, 0.004) * r.uniform(0.5, 1.0)
        _add(ticks, _click(0.03, r, (2500, 9000), 0.0008, [(4200, 0.01, 0.3), (6100, 0.006, 0.2)]) * 0.3,
             max(0.0, tb - 0.01))
        _add(ticks, modal(0.1, [2600, 5100], [0.02, 0.012], [1, .5], r) * 0.1, tb)
    gate = np.clip(gate, 0, 1)
    on = _smoothstep((t - tc) / 0.03) * np.clip((D - t) / 0.35, 0, 1) ** 1.5
    settle = 0.35 + 0.65 * np.exp(-np.maximum(t - tc, 0) / 0.6)
    x = buzz * (gate + on) * 0.4 + sizz * (gate + on * settle) + ticks
    x += harm(np.full(N, 100.0), [1, .3], fmax=6000) * on * 0.25
    st = reverb(decorrelate(x, r, 0.25), 'room', wet_db=-16)
    return _done(st, tc, -9.0, 'jd_fluoro_flicker', keep_until=D)


def jd_crowd_whisper(seed=0, duration=3.0, voices=32):
    """Whisper wall (duration s): voices whispering syllables (noise through moving formants, s/sh/f/h/k/t
    consonants) join over the first 65 %, spread across the stereo field in a hall, growing, then all cut on the
    hit. hit = the END (where the whispers stop)."""
    r = _rng(seed, 'jd_crowd_whisper')
    D = max(0.8, float(duration))
    V = max(1, int(voices))
    N = _n(D)
    T = N // A._HOP + 1
    tf = np.arange(T) * A._HOP / SR
    f = np.fft.rfftfreq(A._NFFT, 1.0 / SR)
    lf = np.log2(np.maximum(f, 20.0))
    t = np.arange(N) / SR
    out = np.zeros((N, 2))

    def band(fc, bw):
        return np.exp(-0.5 * ((lf - math.log2(fc)) / bw) ** 2)
    fric = dict(s=band(6500, 0.35) * 1.2, sh=band(3200, 0.45), f=np.clip((lf - math.log2(1500)) / 1.0, 0, 1)
                * np.clip((math.log2(9000) - lf) / 0.5, 0, 1) * 0.35)
    burst = np.clip((lf - math.log2(1500)) / 0.5, 0, 1) * np.clip((math.log2(8000) - lf) / 0.5, 0, 1) * 0.9
    for vi in range(V):
        sc = r.uniform(0.9, 1.18)
        t_on = D * 0.65 * r.random()
        dist = r.random()
        gain = r.uniform(0.4, 1.0) * (1 - 0.5 * dist)
        mask = np.zeros((T, len(f)))
        tt = t_on
        while tt < D:
            cons = ('s', 'sh', 'h', 'k', 't', 'f', '')[int(r.integers(0, 7))]
            cl = r.uniform(0.04, 0.09) if cons else 0.0
            vl = r.uniform(0.09, 0.2)
            F = [x * sc for x in _VOWELS['aeiou'[int(r.integers(0, 5))]]]
            vow = band(F[0], 0.16) + 0.7 * band(F[1], 0.16) + 0.4 * band(F[2], 0.16) + 0.05 * band(2000, 1.2)
            a, b, c = np.searchsorted(tf, [tt, tt + cl, tt + cl + vl])
            if cons in fric:
                mask[a:b] += fric[cons]
            elif cons == 'h':
                mask[a:b] += 0.5 * vow
            elif cons in ('k', 't'):
                mask[a:min(b, a + 2)] += burst
                mask[min(b, a + 2):b] += 0.4 * vow
            mask[b:c] += vow * (1 + 0.6 * f / 4000.0)
            tt += cl + vl + r.uniform(0.0, 0.05)
            if r.random() < 0.12:
                tt += r.uniform(0.15, 0.4)
        mask = signal.lfilter([1 / 3.0] * 3, [1.0], mask, axis=0)
        lpg = 1.0 / np.sqrt(1 + (f / (9000.0 - 5000.0 * dist)) ** 4)
        y = A._istft(A._stft(r.standard_normal(N)) * mask * lpg[None, :], N)
        y *= np.clip((t - t_on) / 0.3, 0, 1) * gain
        out += pan(y / 30.0, r.uniform(-0.9, 0.9))
    out *= (0.25 + 0.75 * (t / D) ** 0.7)[:, None]
    out = reverb(out, 'hall', wet_db=-12, hard_end=True)[:N]
    out = _fade(out, 0.15, 0.006)
    return _done(out, D, -8.0, 'jd_crowd_whisper', trim=False, fin=0.15, fout=0.006)


# =============================================================================================== BEDS (loops)
def jd_room_night_home(seed=0, dur=24.0):
    """Night at home, seamless loop: ceiling fan air with blade-pass flutter (3 blades ~325 rpm) and a faint
    50 Hz motor hum, two distant crickets, far traffic rumble, small room."""
    r = _rng(seed, 'jd_room_night_home')
    dur = float(dur)
    L = _n(dur)
    tl = np.arange(L) / SR
    air = np.stack([colored(L, r, -3.0, 120, 2500), colored(L, r, -3.0, 120, 2500)], 1)
    air[:, 1] = 0.6 * air[:, 0] + 0.8 * air[:, 1]
    air = A._spec_filter(air, lambda f: np.exp(-0.5 * (np.log2(np.maximum(f, 20.0) / 520.0) / 1.0) ** 2))
    fb = round(16.25 * dur) / dur
    frot = round(fb / 3.0 * dur) / dur
    am = 1 + 0.32 * np.sin(TWO_PI * fb * tl) + 0.10 * np.sin(TWO_PI * frot * tl + 1.1)
    air = _unit(air) * am[:, None] * 0.5
    hum = (0.05 * np.sin(TWO_PI * 100.0 * tl) + 0.02 * np.sin(TWO_PI * 200.0 * tl + 0.4)
           + 0.012 * np.sin(TWO_PI * 50.0 * tl)) * 0.6
    crick = np.zeros((L, 2))
    for c in range(2):
        fc = r.uniform(4100, 4700)
        prate = r.uniform(28, 34)
        pn = (-0.7, 0.6)[c]
        amp = (0.035, 0.022)[c]
        t0 = r.uniform(0, dur)
        span_on = r.uniform(0.5, 0.7) * dur
        tt = 0.0
        while tt < span_on:
            np_ = int(r.integers(3, 6))
            ln = np_ / prate + 0.02
            tp = _t(ln)
            ch = np.sin(TWO_PI * fc * tp) * sum(_gate(tp, k / prate, k / prate + 0.012, 0.003) for k in range(np_))
            _add_wrap(crick, pan(ch * amp * r.uniform(0.7, 1.0), pn), t0 + tt)
            tt += r.uniform(0.45, 0.7)
    crick = A._spec_filter(crick, lambda f: 1.0 / np.sqrt(1 + (f / 7000.0) ** 4))
    traffic = colored(L, r, -6.0, 25, 600) * (1 + 0.3 * _periodic_lfo(tl, dur, r, 3)) * 0.25
    mix = air + _st(hum + traffic) + crick
    mix = reverb_circular(mix, 'room', wet_db=-9)
    return _bed_done(mix, 'jd_room_night_home', 0.0)


def jd_room_stadium(seed=0, dur=24.0):
    """Empty stadium at night, seamless loop: gusting wind with structure whistles, floodlight ballast hum (3
    lamps), distant city, a halyard tinking on a flagpole with echoes off the stands, huge space."""
    r = _rng(seed, 'jd_room_stadium')
    dur = float(dur)
    L = _n(dur)
    tl = np.arange(L) / SR
    ks = [(k, r.uniform(0.3, 1.0) / k, r.uniform(0, TWO_PI)) for k in (1, 2, 3, 5)]

    def gust(tt):
        g = sum(a * np.sin(TWO_PI * k * tt / dur + ph) for k, a, ph in ks)
        return 0.5 + 0.5 * g / sum(a for _, a, _ in ks)

    def mask(tt, f):
        g = gust(tt)[:, None]
        lf = np.log2(np.maximum(f, 8.0))[None, :]
        wind = np.exp(-0.5 * ((lf - (math.log2(380.0) + 0.35 * (g - 0.5))) / 1.0) ** 2) * (0.3 + 0.7 * g)
        whis = (np.exp(-0.5 * ((lf - math.log2(620.0)) / 0.05) ** 2)
                + 0.7 * np.exp(-0.5 * ((lf - math.log2(1150.0)) / 0.05) ** 2)) * 0.12 * g ** 2
        hi = 0.015 * np.exp(-0.5 * ((lf - math.log2(6000.0)) / 1.0) ** 2)
        return wind + whis + hi
    wind = _unit(_loop_mask_noise(L, r, mask, corr=0.4))
    hum = np.zeros(L)
    for k in range(3):
        f0 = 100.0 + k / dur
        hum += harm(np.full(L, f0), [1, .45, .3, .2, .14, .1, .07], fmax=5000, rng=r)
    city = colored(L, r, -6.0, 25, 500)
    tinks = np.zeros((L, 2))
    for k in range(3):
        tk = (k + r.uniform(0.15, 0.85)) * dur / 3.0
        v = r.uniform(0.97, 1.03)
        ping = modal(0.7, [2150 * v, 3420 * v, 5600 * v, 7900 * v], [.25, .18, .1, .06], [1, .6, .35, .2], r,
                     contact=0.0003) * r.uniform(0.6, 1.0)
        for dly, g in ((0.0, 1.0), (0.31, 0.35), (0.62, 0.15)):
            _add_wrap(tinks, pan(ping * g, (0.5, -0.4, 0.3)[int(dly / 0.3)]), tk + dly)
    tinks = A._spec_filter(tinks, lambda f: 1.0 / np.sqrt(1 + (f / 6000.0) ** 4))
    mix = wind * 0.5 + _st(hum * 0.012 + city * 0.12) + tinks * 0.05
    mix = reverb_circular(mix, 'hall', wet_db=-6, rt60=3.4, predelay=0.05)
    return _bed_done(mix, 'jd_room_stadium', 0.0)


def jd_room_studio(seed=0, dur=16.0):
    """Treated studio / edit suite, seamless loop: PC fan broadband + blade tone, split-AC compressor hum and
    airflow, faint monitor hiss, small dead room."""
    r = _rng(seed, 'jd_room_studio')
    dur = float(dur)
    L = _n(dur)
    tl = np.arange(L) / SR
    fan = np.stack([colored(L, r, -2.5, 150, 6000), colored(L, r, -2.5, 150, 6000)], 1)
    fan[:, 1] = 0.7 * fan[:, 0] + 0.71 * fan[:, 1]
    fan = A._spec_filter(fan, lambda f: 0.4 + np.exp(-0.5 * (np.log2(np.maximum(f, 20.0) / 900.0) / 0.9) ** 2))
    fb = round(140.0 * dur) / dur
    blade = harm(np.full(L, fb), [1, .35, .15], fmax=6000, rng=r) * (1 + 0.2 * _periodic_lfo(tl, dur, r, 2))
    ac = harm(np.full(L, 100.0), [1, .3], fmax=6000, rng=r)
    flow = colored(L, r, -5.0, 60, 1200)
    hiss = colored(L, r, 0.0, 4000, 16000)
    mix = _unit(fan) * 0.35 + _st(blade * 0.012 + ac * 0.015 + flow * 0.22 + hiss * 0.012)
    mix = reverb_circular(mix, 'room', wet_db=-12)
    return _bed_done(mix, 'jd_room_studio', 0.0)


def jd_projector_loop(seed=0, dur=8.0, fps=24.0):
    """Film projector running, seamless loop: claw + shutter clatter at 2 x fps (alternating accents), motor
    hum, belt whine, fan. dur is rounded so the loop holds a whole number of frames."""
    r = _rng(seed, 'jd_projector_loop')
    n_ev = max(2, int(round(2 * float(fps) * float(dur))))
    dur = n_ev / (2.0 * float(fps))
    L = _n(dur)
    tl = np.arange(L) / SR
    x = np.zeros(L)
    per = dur / n_ev
    for j in range(n_ev):
        _add_wrap(x, _proj_tick(r, j % 2 == 0) * r.uniform(0.85, 1.0), j * per + r.uniform(0, 0.0008))
    motor = harm(np.full(L, 2.0 * float(fps)), [1, 0.6, 0.35, 0.2, 0.12, 0.08], fmax=8000, rng=r) * 0.10
    fw = round(880.0 * dur) / dur
    whine = np.sin(TWO_PI * fw * tl) * 0.02
    fan = A._spec_filter(colored(L, r, -2.0, 150, 3000), lambda f: 1.0 / np.sqrt(1 + (f / 2000.0) ** 4)) * 0.05
    mix = decorrelate(x + motor + whine + fan, r, 0.3)
    mix = reverb_circular(mix, 'room', wet_db=-12)
    return _bed_done(mix, 'jd_projector_loop', 0.0)


# =============================================================================================== HIT STACKS
def ember_slam(t0, bpm=90.0, riser_beats=4, gap_beats=0.0):
    """EPIC hero reveal / title slam (bible 4.2): riser (riser_beats long, ends gap_beats before t0: gap > 0 is
    the drop-out), flash_hit transient 3 ms early, impact_big body + hall, sub_drop (lp 120)."""
    beat = 60.0 / float(bpm)
    r_end = t0 - float(gap_beats) * beat
    return [dict(t=r_end, name='riser', params=dict(duration=round(float(riser_beats) * beat, 4)), gain_db=-4,
                 stack='ember_slam'),
            dict(t=t0 - 0.003, name='flash_hit', gain_db=-3, stack='ember_slam'),
            dict(t=t0, name='impact_big', gain_db=0, stack='ember_slam', hero=True),
            dict(t=t0, name='sub_drop', gain_db=-4, lp=120, params=dict(dur=1.6), stack='ember_slam')]


def velvet_hit(t0, pitch=1.0):
    """INTIMATE heartbeat-sized landing (bible 4.2): heartbeat(n=1) + impact_soft + glass_tap 20 ms later."""
    return [dict(t=t0, name='heartbeat', params=dict(n=1), gain_db=-6, stack='velvet_hit'),
            dict(t=t0, name='impact_soft', gain_db=0, stack='velvet_hit'),
            dict(t=t0 + 0.02, name='glass_tap', params=dict(pitch=float(pitch)), gain_db=-10, stack='velvet_hit')]


def glass_truth(t0, pitch=1.0):
    """TECH / UI reveal (bible 4.2): ui_click 2 ms early, glass_tap, short sub_drop, jd_sparkle 30 ms later
    (jd_sparkle = alias-free audio.sparkle)."""
    return [dict(t=t0 - 0.002, name='ui_click', gain_db=-6, stack='glass_truth'),
            dict(t=t0, name='glass_tap', params=dict(pitch=float(pitch)), gain_db=0, stack='glass_truth'),
            dict(t=t0, name='sub_drop', params=dict(dur=0.8), gain_db=-10, lp=120, stack='glass_truth'),
            dict(t=t0 + 0.03, name='jd_sparkle', gain_db=-10, stack='glass_truth')]


def dha_hit(t0, sa_hz=293.66, bpm=90.0):
    """DESI reveal (bible 4.2): tabla roll ending on t0, tabla dha on t0 (the hero), sub_drop, ghungroo +50 ms."""
    return [dict(t=t0, name='jd_tabla_roll', params=dict(n=8, bpm=float(bpm), sa=float(sa_hz)), gain_db=-6,
                 stack='dha_hit'),
            dict(t=t0, name='jd_tabla_dha', params=dict(sa=float(sa_hz)), gain_db=0, stack='dha_hit', hero=True),
            dict(t=t0, name='sub_drop', gain_db=-6, lp=120, stack='dha_hit'),
            dict(t=t0 + 0.05, name='jd_ghungroo', gain_db=-12, stack='dha_hit')]


STACKS = dict(ember_slam=ember_slam, velvet_hit=velvet_hit, glass_truth=glass_truth, dha_hit=dha_hit)


def stack(name, t0, **kw):
    """Cue list of a named hit stack: stack('ember_slam', 12.0, bpm=90)."""
    if name not in STACKS:
        raise KeyError('unknown stack %r; known: %s' % (name, ', '.join(STACKS)))
    return STACKS[name](t0, **kw)


def _snd(name, **params):
    """Render a sound: this module's sounds are called directly (uncached, so the QC reference mode reaches
    them); audio.py sounds come from its cache."""
    if name in META:
        return globals()[name](**params)
    return A.sound(name, **params)


def _cue_fx(y, hit, c):
    """The per-cue processing of audio._render_cue (rate, lp, hp, width, dur, pan, gain), for stack renders."""
    rate = float(c.get('rate', 1.0))
    if abs(rate - 1.0) > 1e-4:
        from fractions import Fraction
        fr = Fraction(rate).limit_denominator(64)
        y = signal.resample_poly(y, fr.denominator, fr.numerator, axis=0)
        hit = hit / rate
    if c.get('lp'):
        y = lp(y, c['lp'], 2)
    if c.get('hp'):
        y = hp(y, c['hp'], 2)
    if c.get('width') is not None:
        y = width(y, float(c['width']))
    if c.get('dur'):
        y = _fade(y[:_n(c['dur'])], 0.0, min(0.05, c['dur'] * 0.2))
    if c['pan']:
        y = pan(width(y, 1 - 0.5 * abs(c['pan'])), c['pan'])
    return y * undb(c['gain_db']), hit


def render_cues(cues, seed=0):
    """Render a short cue list into one stereo buffer -> (buffer, t0_in_buffer) where cue time 0 sits at
    t0_in_buffer seconds. Same alignment rules as audio.mix (no ducking, no room send, no normalisation)."""
    register()
    parts = []
    for c in cues:
        c = A._norm_cue(c)
        p = dict(c['params'])
        p['seed'] = c.get('seed', p.get('seed', seed))
        x = _snd(c['name'], **p)
        y, hit = _cue_fx(np.asarray(x, dtype=np.float64), x.hit, c)
        parts.append((float(c['t']) - (hit if c['align'] == 'hit' else 0.0), y))
    s0 = min(s for s, _ in parts)
    out = np.zeros((max(_n(s - s0) + len(y) for s, y in parts) + 1, 2))
    for s, y in parts:
        _add(out, y, s - s0)
    return out, -s0


def jd_stack_ember_slam(seed=0, bpm=90.0, riser_beats=4, gap_beats=0.0):
    """ember_slam rendered as one sound (riser first). hit = the slam."""
    out, h = render_cues(ember_slam(0.0, bpm, riser_beats, gap_beats), seed)
    return _done(out, h, 4.0, 'jd_stack_ember_slam')


def jd_stack_velvet_hit(seed=0, pitch=1.0):
    """velvet_hit rendered as one sound. hit = the landing."""
    out, h = render_cues(velvet_hit(0.0, pitch), seed)
    return _done(out, h, -3.0, 'jd_stack_velvet_hit')


def jd_stack_glass_truth(seed=0, pitch=1.0):
    """glass_truth rendered as one sound. hit = the glass tap."""
    out, h = render_cues(glass_truth(0.0, pitch), seed)
    return _done(out, h, -2.0, 'jd_stack_glass_truth')


def jd_stack_dha_hit(seed=0, sa=293.66, bpm=90.0):
    """dha_hit rendered as one sound (the roll first). hit = the dha."""
    out, h = render_cues(dha_hit(0.0, sa, bpm), seed)
    return _done(out, h, 1.0, 'jd_stack_dha_hit')


# =============================================================================================== registry
# name: (category, band for the VO helper, level dB re REF, send dB or None, character, use)
META = {
    'jd_hit_hero': ('impact', 'hero', 4.0, -24, 'ember slam: crack, punch, 31 Hz sub, anvil ring, hall, dying sparks',
                    'the one hero reveal per reel, title slams'),
    'jd_hit_soft': ('impact', 'dark', -3.0, -18, 'warm felt thump, wood knock, air puff', 'soft landings, card settles'),
    'jd_sub_drop': ('impact', 'dark', -2.0, -30, 'sub dive 92 -> 29 Hz with phone harmonics', 'under smash cuts'),
    'jd_heartbeat': ('impact', 'dark', -3.0, -26, 'deep lub-dub with chest resonance', 'intimate beats, held breath'),
    'jd_floodlight_clunk': ('impact', 'hero', 0.0, None, 'contactor clunk, ballast hum swell, stand echoes',
                            'stadium lights slam on'),
    'jd_tabla_dha': ('impact', 'mid', -2.0, -18, 'tabla dha (na + ge)', 'desi hit on a reveal'),
    'jd_tabla_na': ('texture', 'mid', -4.0, -18, 'tabla na, tuned to Sa', 'desi accents'),
    'jd_tabla_tin': ('texture', 'mid', -8.0, -18, 'tabla tin, tuned to Sa', 'soft desi pulse'),
    'jd_tabla_ge': ('texture', 'dark', -6.0, -18, 'tabla ge with upward wah', 'desi bass accent'),
    'jd_whoosh_short': ('transition', 'dark', -3.0, -16, 'warm air rush + ember sizzle', 'cuts, cards, windows'),
    'jd_whoosh_long': ('transition', 'dark', -5.0, -14, 'big flanged swell, hall, crackle trail', 'slow reveals'),
    'jd_whip': ('transition', 'mid', -3.0, -18, 'bright whip with cloth-snap crack', 'whip pans, smash cuts'),
    'jd_riser': ('transition', 'span', -4.0, -18, 'bar-locked riser: sweep, Shepard, grid pulses, reverse cymbal',
                 'into reveals (ends on the hit)'),
    'jd_reverse_swell': ('transition', 'span', -4.0, -22, 'reversed bloom + accelerating crackle', 'suck into hits'),
    'jd_tape_stop': ('transition', 'mid', -4.0, -18, 'groove slowing to a halt + pinch-roller clunk',
                     'the "music dies" beat'),
    'jd_power_down': ('transition', 'dark', -4.0, -18, 'relay, hum and whine winding down', 'blackout, load shedding'),
    'jd_power_up': ('transition', 'span', -4.0, -18, 'whine + hum spinning up, "on" thoom', 'lights / screen alive'),
    'jd_crt_collapse': ('transition', 'mid', -4.0, -18, 'CRT off: whine dies, thwup, static', 'TV-off cut, flashback'),
    'jd_revolving_door': ('transition', 'dark', -5.0, -18, 'wing whooshes, seal brush, world muffles',
                          'enter a new world (office, hotel, studio)'),
    'jd_tabla_roll': ('transition', 'span', -6.0, -18, 'ti-ra-ki-ta 32nds crescendo', 'desi fill into a hit'),
    'jd_ui_click': ('ui', 'mid', -9.0, -18, 'dark-glass click, warm body', 'cursor clicks, buttons'),
    'jd_ui_tick': ('ui', 'air', -13.0, -18, 'tiny glassy tick', 'list items, counters, progress'),
    'jd_ui_pop': ('ui', 'mid', -9.0, -18, 'round bloop', 'chips, icons popping in'),
    'jd_keyboard': ('ui', 'mid', -11.0, -18, 'typing with releases (laptop | mech)', 'prompts, search, captions'),
    'jd_mouse_click': ('ui', 'mid', -12.0, -18, 'micro-switch press + release', 'NLE clicks'),
    'jd_timeline_scrub': ('ui', 'mid', -12.0, -18, 'audio-scrub chatter per frame', 'playhead drags (align start)'),
    'jd_glass_slide': ('ui', 'mid', -8.0, -16, 'glass on glass, glassy tunk landing', 'glass panels sliding in'),
    'jd_glass_clink': ('ui', 'mid', -8.0, -16, 'two glasses clinking, beating modes', 'toasts, glass UI accents'),
    'jd_ups_beep': ('ui', 'mid', -12.0, -18, 'UPS relay + piezo beeps', 'load shedding, deadline panic'),
    'jd_vn_blip': ('ui', 'mid', -12.0, -18, 'voice-note mic blip', 'voice-note UI'),
    'jd_vn_record': ('ui', 'mid', -12.0, -18, 'record pips + open-mic air', 'voice-note record'),
    'jd_vn_send': ('ui', 'mid', -10.0, -18, 'tap, upward swish, landing pop', 'voice-note sent'),
    'jd_projector': ('texture', 'mid', -8.0, -18, 'projector spin-up to 24 fps', 'flashback / film opener'),
    'jd_fluoro_flicker': ('texture', 'mid', -9.0, -16, 'tube light flicker then hum', 'lights on in a dark room'),
    'jd_crowd_whisper': ('texture', 'span', -8.0, -16, 'whisper wall growing, cut on the hit',
                         '"log kya kahenge" pressure, doubt'),
    'jd_ghungroo': ('texture', 'air', -10.0, -14, 'ankle-bell shake', 'desi sparkle'),
    'jd_sparkle': ('texture', 'air', -11.0, -12, 'FM twinkles, alias-free', 'glints, glass_truth tail'),
    'jd_room_night_home': ('bed', 'bed', 0.0, None, 'ceiling fan, crickets, far traffic', 'night home floor'),
    'jd_room_stadium': ('bed', 'bed', 0.0, None, 'wind, ballast hum, halyard tinks, huge space', 'empty stadium'),
    'jd_room_studio': ('bed', 'bed', 0.0, None, 'PC fan, AC hum, faint hiss', 'studio / edit suite'),
    'jd_projector_loop': ('bed', 'bed', 0.0, None, 'projector running at 24 fps', 'cinema / flashback bed'),
    'jd_stack_ember_slam': ('impact', 'hero', 4.0, -26, 'bible ember_slam rendered', 'audition / one-cue slam'),
    'jd_stack_velvet_hit': ('impact', 'dark', -3.0, -20, 'bible velvet_hit rendered', 'audition / intimate landing'),
    'jd_stack_glass_truth': ('ui', 'mid', -2.0, -18, 'bible glass_truth rendered', 'audition / UI reveal'),
    'jd_stack_dha_hit': ('impact', 'hero', 1.0, -22, 'bible dha_hit rendered', 'audition / desi reveal'),
}
ALIASES = dict(tabla_na='jd_tabla_na', tabla_tin='jd_tabla_tin', tabla_ge='jd_tabla_ge', tabla_dha='jd_tabla_dha',
               tabla_roll='jd_tabla_roll', ghungroo='jd_ghungroo')


def register():
    """Add every jd_* sound to audio.SOUNDS (idempotent; a module reload replaces its own entries and clears the
    render cache). Raises if another module already owns one of the names. Also maps the bible names
    (tabla_dha, ghungroo, ...) to the jd_* sounds when nothing else uses them. Returns the registered names."""
    me = __name__
    changed = False
    for name, (cat, band, level, send, ch, use) in META.items():
        fn = globals()[name]
        cur = A.SOUNDS.get(name)
        if cur is not None:
            if cur['fn'] is fn:
                continue
            if getattr(cur['fn'], '__module__', None) not in (me, 'sfx_jawad', '__main__'):
                raise RuntimeError('sound name %r already registered by %s' % (name, cur['fn'].__module__))
        A._register(cat, ch, use, send)(fn)
        changed = True
    if changed:
        A._sound_cached.cache_clear()
    for a, n in ALIASES.items():
        if a not in A.SOUNDS and a not in A.ALIASES:
            A.ALIASES[a] = n
    return list(META)


# =============================================================================================== VO helper
HERO = {'impact_big', 'flash_hit', 'logo_sting', 'braam', 'glass_shatter', 'cinematic_boom', 'trailer_hit', 'dhol_hit'}
AIR = {'shimmer', 'sparkle', 'ripple', 'swish_small', 'ui_tick', 'ui_hover'}
DARK = {'whoosh_fast', 'whoosh_slow', 'whoosh_by', 'impact_soft', 'sub_drop', 'card_slide', 'heartbeat', 'air_zoom',
        'downlifter'}
MID = {'glass_tap', 'check_ding', 'toast_chime', 'ui_click', 'typing', 'pop', 'camera_shutter', 'whip', 'riser',
       'bubble_pop', 'toggle_on', 'puzzle_click', 'glitch_short'}
SPAN = {'riser', 'reverse_swell', 'shepard_riser', 'reverse_cymbal', 'heartbeat_build', 'dholak_roll',
        'vinyl_rewind'}


VO_SELFTEST_WORDS = os.path.join(A.WS, 'vo', 'selftest', 'vlad_v4_r1_DEV_final.words.json')
_VO_EXCERPT = [dict(word='karna', start=2.982, end=3.327), dict(word='hai...', start=3.327, end=3.491),
               dict(word='aur', start=4.018, end=4.218), dict(word='nahi', start=14.155, end=14.391),
               dict(word='hue!', start=14.391, end=14.609), dict(word='Lekin', start=15.11, end=15.618)]


class HeroOnWordError(ValueError):
    """A hero hit lands on (or too close to) a spoken word."""


def _load_words(words, offset=0.0):
    if isinstance(words, str):
        with open(words) as fh:
            words = json.load(fh)
        if isinstance(words, dict):
            words = words.get('words', [])
    out = []
    for w in words or []:
        if isinstance(w, dict):
            if w.get('start') is None or w.get('end') is None:
                continue
            a, b = float(w['start']), float(w['end'])
        else:
            a, b = float(w[0]), float(w[1])
        out.append((a + offset, max(b, a) + offset))
    return sorted(out)


def vo_windows(words, pad=0.06, merge=0.12, offset=0.0):
    """Merged speech windows [(t0, t1)] in reel time: each word padded by pad, gaps <= merge joined."""
    out = []
    for a, b in _load_words(words, offset):
        a, b = a - pad, b + pad
        if out and a <= out[-1][1] + merge:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return [(round(a, 4), round(b, 4)) for a, b in out]


VO_ACTIVE_DB = -30.0               # VO audio is "speech" while its 10 ms RMS is above median speech level + this


def _vo_audio_source(words, vo_audio):
    """The VO audio for the hero test: an explicit wav path or (samples, sr), None (words only), or 'auto' = the
    vo_chain wav next to a '<stem>.words.json' path ('<stem>.wav'), when that file exists."""
    if isinstance(vo_audio, str) and vo_audio == 'auto':
        if isinstance(words, str) and words.endswith('.words.json'):
            p = words[:-len('.words.json')] + '.wav'
            return p if os.path.exists(p) else None
        return None
    return vo_audio


def _activity(x, sr, thresh_db, merge):
    x = np.asarray(x, dtype=np.float64)
    x = x.mean(1) if x.ndim == 2 else x
    k = max(1, int(round(0.01 * sr)))
    db = 20 * np.log10(np.sqrt(np.convolve(x * x, np.ones(k) / k, 'same')) + 1e-12)
    if not x.size or db.max() < -150:
        return ()
    ref = float(np.median(db[db > db.max() - 40.0]))
    d = np.diff(np.concatenate([[0], (db > ref + thresh_db).astype(np.int8), [0]]))
    out = []
    for a, b in zip(np.nonzero(d == 1)[0] / sr, np.nonzero(d == -1)[0] / sr):
        if out and a - out[-1][1] <= merge:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return tuple((round(float(a), 4), round(float(b), 4)) for a, b in out)


@functools.lru_cache(maxsize=16)
def _activity_file(path, mtime_ns, size, thresh_db, merge):
    x, sr = A.read_wav(path)
    return _activity(x, sr, thresh_db, merge)


def vo_activity(vo, thresh_db=VO_ACTIVE_DB, merge=0.04):
    """Speech activity [(t0, t1)] (VO time, s) measured on the VO AUDIO: 10 ms RMS above the median speech level
    + thresh_db (-30 dB: a word's decaying tail is speech until it is 30 dB under the voice), gaps <= merge joined.
    vo: wav path or (samples, sr). Whisper word 'end' times run early on TTS (up to 160 ms on the Vlad DEV take),
    so the hero test uses this whenever the audio is available."""
    if isinstance(vo, str):
        st = os.stat(vo)
        return list(_activity_file(vo, st.st_mtime_ns, st.st_size, float(thresh_db), float(merge)))
    x, sr = vo
    return list(_activity(x, int(sr), float(thresh_db), float(merge)))


def hero_windows(words, offset=0.0, pad=0.0, vo_audio='auto', vo_thresh_db=VO_ACTIVE_DB):
    """(windows, source): what a hero hit must keep clear of, in reel time: the words (padded by pad, default 0)
    united with the VO audio's speech activity when the audio is available (source 'words+audio'), else the words
    alone (source 'words')."""
    w = vo_windows(words, pad, offset=offset)
    src = _vo_audio_source(words, vo_audio)
    if src is None:
        return w, 'words'
    out = []
    for a, b in sorted(w + [(a + offset, b + offset) for a, b in vo_activity(src, vo_thresh_db)]):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return [(round(a, 4), round(b, 4)) for a, b in out], 'words+audio'


def hero_slots(words, offset=0.0, pre=0.12, post=0.30, dur=None, pad=0.0, vo_audio='auto',
               vo_thresh_db=VO_ACTIVE_DB):
    """Intervals [(t0, t1)] where a hero hit may land (bible 4.1): no speech within [hit - pre, hit + post], i.e.
    120 ms clear before the transient and 300 ms after it, so a pause of >= pre + post (0.42 s) of real silence holds
    a hero. Speech = the UNPADDED words (pad=0; the 60 ms ducking pad is not stacked on the clearance) united with
    the VO audio's activity (vo_activity) when the audio is available: vo_audio='auto' finds the vo_chain wav next to
    a '<stem>.words.json' path; pass a wav path / (samples, sr), or None for words only."""
    bad = [(a - post, b + pre) for a, b in hero_windows(words, offset, pad, vo_audio, vo_thresh_db)[0]]
    out, cur = [], 0.0
    end = float(dur) if dur is not None else (max([b for _, b in bad], default=0.0) + 60.0)
    for a, b in bad:
        if a > cur:
            out.append((cur, min(a, end)))
        cur = max(cur, b)
    if cur < end:
        out.append((cur, end))
    # rounded INWARD to whole ms (start up, end down), so every reported time is itself legal
    out = [(math.ceil(a * 1000.0 - 1e-6) / 1000.0, math.floor(b * 1000.0 + 1e-6) / 1000.0) for a, b in out]
    return [(a, b) for a, b in out if b >= a]


def band_of(name, cue=None):
    """VO-helper band of a sound: hero | span | air | dark | mid | bed."""
    if cue is not None and cue.get('hero'):
        return 'hero'
    n = A.resolve(name)
    if n in META:
        return META[n][1]
    for b, s in (('hero', HERO), ('span', SPAN), ('air', AIR), ('dark', DARK), ('mid', MID)):
        if n in s:
            return b
    return dict(impact='dark', transition='dark', ui='mid', money='mid', texture='air', bed='bed')[A.SOUNDS[n]['category']]


def fit_under_vo(cues, words, depth_db=-6.0, hero='raise', offset=0.0, pad=0.06, mid_extra_db=-2.0, air_hp=5500.0,
                 dark_lp=1100.0, hero_pre=0.12, hero_post=0.30, hero_post_small=0.15, hero_pad=0.0, vo_audio='auto',
                 vo_thresh_db=VO_ACTIVE_DB, report=False):
    """Duck and carve a cue sheet around the voice-over (bible 4.1). Returns NEW cues (inputs untouched), or
    (cues, report) with report=True.
      * HERO cues need hero_pre s of silence before the hit and hero_post s after it (hero_post_small for
        non-impact heroes): the bible's 120 / 300 ms are the net clearance from the speech itself, so any pause of
        >= 0.42 s of real silence holds a hero (0.27 s for a non-impact hero). Speech = the words padded by hero_pad
        (default 0) united with the VO audio's activity (vo_activity, above median speech - 30 dB) whenever the
        audio is available (vo_audio='auto': the vo_chain '<stem>.wav' next to a '<stem>.words.json' path; or a
        wav path / (samples, sr); None = words only). A violation raises HeroOnWordError (hero='raise', the
        default; the message lists the nearest legal hit time), is removed (hero='drop') or only reported
        (hero='warn'). report['hero_source'] says which speech was used.
      * pad (0.06 s) widens the words only for the ducking and carving below.
      * Any other cue whose hit lies inside a speech window: gain + depth_db; AIR -> 'hp' air_hp, DARK -> 'lp'
        dark_lp, MID -> another mid_extra_db (it competes with consonants).
      * SPAN cues (risers, swells, rolls, whisper wall) whose body [start, hit] overlaps speech: + depth_db and
        'lp' dark_lp (plus mid_extra_db for MID ones such as 'riser').
    words: .words.json path (vo_chain), word dicts {'start', 'end'} or (t0, t1) tuples, in VO time; offset = the
    VO start in the reel."""
    register()
    wins = vo_windows(words, pad, offset=offset)
    hwins, hsrc = hero_windows(words, offset, hero_pad, vo_audio, vo_thresh_db)
    rep = dict(windows=[(round(a, 3), round(b, 3)) for a, b in wins], ducked=[], spans=[], heroes_ok=[],
               violations=[], dropped=[], hero_windows=[(round(a, 3), round(b, 3)) for a, b in hwins],
               hero_source=hsrc)
    out, bad_idx = [], []
    for c0 in cues:
        c = A._norm_cue(c0)
        x = A.sound(c['name'], **c['params'])
        rate = float(c.get('rate', 1.0))
        hit_off = x.hit / rate
        length = (c['dur'] if c.get('dur') else len(x) / SR / rate)
        start = float(c['t']) - (hit_off if c['align'] == 'hit' else 0.0)
        hit = start + hit_off
        b = band_of(c['name'], c)
        if b == 'bed':
            out.append(c)
            continue
        if b == 'hero':
            post = hero_post if A.SOUNDS[c['name']]['category'] == 'impact' else hero_post_small
            hits = [w for w in hwins if w[0] < hit + post - 1e-6 and w[1] > hit - hero_pre + 1e-6]
            if hits:
                slots = hero_slots(words, offset, hero_pre, post, pad=hero_pad, vo_audio=vo_audio,
                                   vo_thresh_db=vo_thresh_db)
                cand = [min(max(hit, a), b2) for a, b2 in slots]
                near = min(cand, key=lambda v: abs(v - hit)) if cand else None
                rep['violations'].append(dict(name=c['name'], t=round(float(c['t']), 3), hit=round(hit, 3),
                                              words=[(round(a, 3), round(b2, 3)) for a, b2 in hits],
                                              nearest_legal_hit=None if near is None else round(near, 3)))
                bad_idx.append(len(out))
            else:
                rep['heroes_ok'].append(dict(name=c['name'], hit=round(hit, 3)))
            out.append(c)
            continue
        note = []
        if b == 'span':
            if any(a < hit and b2 > start for a, b2 in wins):
                c['gain_db'] = float(c['gain_db']) + depth_db + (mid_extra_db if c['name'] in MID else 0.0)
                c.setdefault('lp', dark_lp)
                note = ['span %+.1f dB, lp %d' % (c['gain_db'] - float(A._norm_cue(c0)['gain_db']), c['lp'])]
                rep['spans'].append(dict(name=c['name'], start=round(start, 3), hit=round(hit, 3), note=note[0]))
        elif any(a <= hit <= b2 for a, b2 in wins):
            g = depth_db + (mid_extra_db if b == 'mid' else 0.0)
            c['gain_db'] = float(c['gain_db']) + g
            if b == 'air':
                c.setdefault('hp', air_hp)
            if b == 'dark':
                c.setdefault('lp', dark_lp)
            note = ['%+.1f dB%s' % (g, ', hp %d' % c['hp'] if b == 'air' else (', lp %d' % c['lp'] if b == 'dark'
                                                                              else ''))]
            rep['ducked'].append(dict(name=c['name'], hit=round(hit, 3), band=b, note=note[0]))
        if note:
            c['vo'] = note[0]
        out.append(c)
    if rep['violations']:
        if hero == 'raise':
            msg = '; '.join('%s hit %.3f s overlaps speech %s (nearest legal hit %s)' % (
                v['name'], v['hit'], v['words'], v['nearest_legal_hit']) for v in rep['violations'])
            raise HeroOnWordError('hero cue on a word: ' + msg)
        if hero == 'drop':
            rep['dropped'] = [dict(name=out[i]['name'], t=out[i]['t']) for i in bad_idx]
            out = [c for i, c in enumerate(out) if i not in set(bad_idx)]
        elif hero != 'warn':
            raise ValueError("hero must be 'raise', 'drop' or 'warn'")
    return (out, rep) if report else out


# =============================================================================================== QC
def measure(x, hit, bed=False):
    """Objective numbers for one rendered sound (see QC.md columns)."""
    x = np.asarray(x, dtype=np.float64)
    st = A.stats(x, hit)
    m = x.mean(1)
    P = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1.0 / SR)
    tot = P.sum() + 1e-30

    def frac(lo, hi):
        return float(P[(f >= lo) & (f < hi)].sum() / tot)
    cum = np.cumsum(P) / tot
    runs = 0
    pk = np.max(np.abs(x))
    for c in range(x.shape[1]):
        hot = np.abs(x[:, c]) >= pk * (1 - 1e-6)
        if hot.any():
            d = np.diff(np.concatenate([[0], hot.astype(np.int8), [0]]))
            runs = max(runs, int(np.max(np.nonzero(d == -1)[0] - np.nonzero(d == 1)[0])))
    out = dict(dur=round(len(x) / SR, 4), hit=round(float(hit), 4), mmax_lufs=round(st['mmax_lufs'], 2),
               i_lufs=round(A.loudness(x), 2), peak_dbfs=round(st['peak_db'], 2), tp_dbtp=round(A.true_peak(x), 2),
               crest_db=round(st['crest_db'], 1), dc=float(st['dc']), centroid_hz=int(float((f * P).sum() / tot)),
               rolloff85_hz=int(f[min(len(f) - 1, int(np.searchsorted(cum, 0.85)))]),
               sub_pct=round(100 * frac(0, 60), 1), low_pct=round(100 * frac(60, 250), 1),
               lowmid_pct=round(100 * frac(250, 1000), 1), mid_pct=round(100 * frac(1000, 4000), 1),
               high_pct=round(100 * frac(4000, 12000), 1), air_pct=round(100 * frac(12000, 24001), 2),
               nyq_db=round(_hf_db(x), 1), clip_run=runs, corr=round(st['corr'], 3),
               mono_db=round(A.momentary_max(np.stack([m, m], 1)) - st['mmax_lufs'], 2))
    probs = A.qc(x.astype(np.float32), hit)
    if bed:
        seam = np.abs(x[0] - x[-1]).max()
        typ = np.percentile(np.abs(np.diff(x, axis=0)), 99.9)
        out['seam_ratio'] = round(float(seam / (typ + 1e-12)), 3)
        probs = [p for p in probs if 'edge' not in p]
        if out['seam_ratio'] > 1.5:
            probs.append('loop seam %.2f' % out['seam_ratio'])
        if abs(out['i_lufs'] - REF) > 0.3 and out['tp_dbtp'] < TP_CEIL - 0.1:
            probs.append('bed loudness %.2f LUFS' % out['i_lufs'])
    if out['tp_dbtp'] > TP_CEIL + 0.005:
        probs.append('true peak %.2f dBTP' % out['tp_dbtp'])
    if runs > 3:
        probs.append('flat-topped run %d samples (clipping)' % runs)
    if out['nyq_db'] > -60:
        probs.append('energy above 20.5 kHz %.1f dB' % out['nyq_db'])
    if out['mono_db'] < -(MONO_LOSS_BED if bed else MONO_LOSS):
        probs.append('mono fold-down loses %.2f dB' % -out['mono_db'])
    out['problems'] = probs
    return out


@contextlib.contextmanager
def toolkit_saturators(mode='count'):
    """Instrument audio.py's own waveshapers (_sat / _asat: used by audio._thump, audio.bass_enhance and toolkit
    layers such as impact_big, sub_drop, flash_hit, riser), which run at 1x in normal renders. mode='count'
    only counts their calls; mode='ref' computes them at 32x (same FIR as shape()) for the alias reference.
    Yields [n_calls]. audio's render cache is cleared on entry and exit so nothing instrumented is kept."""
    o_sat, o_asat = A._sat, A._asat
    n = [0]
    if mode == 'ref':
        def f_sat(x, drive=2.0):
            n[0] += 1
            x = np.asarray(x, dtype=np.float64)
            return _down(o_sat(_up(x, 32), drive), 32, len(x))

        def f_asat(x, drive=2.0, bias=0.15):
            n[0] += 1
            x = np.asarray(x, dtype=np.float64)
            return _down(o_asat(_up(x, 32), drive, bias), 32, len(x))
    elif mode == 'count':
        def f_sat(x, drive=2.0):
            n[0] += 1
            return o_sat(x, drive)

        def f_asat(x, drive=2.0, bias=0.15):
            n[0] += 1
            return o_asat(x, drive, bias)
    else:
        raise ValueError("mode must be 'count' or 'ref'")
    A._sat, A._asat = f_sat, f_asat
    A._sound_cached.cache_clear()
    try:
        yield n
    finally:
        A._sat, A._asat = o_sat, o_asat
        A._sound_cached.cache_clear()


def alias_residual(name, params):
    """Aliasing estimate (dB): renders name(**params) normally (this module's nonlinear / FM / varispeed stages at
    8x, the toolkit's _sat / _asat at 1x) and as a reference with ALL of them at 32x, and returns the gain-matched
    residual energy relative to the reference; None when the render has none of those stages (band-limited
    oscillators and linear filters only: nothing that can alias)."""
    fn = globals()[name]
    c0 = _STATE['os_calls']
    with toolkit_saturators('count') as nsat:
        a = np.asarray(fn(**params), dtype=np.float64)
    if _STATE['os_calls'] == c0 and not nsat[0]:
        return None
    with reference_quality(), toolkit_saturators('ref'):
        b = np.asarray(fn(**params), dtype=np.float64)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    g = float((a * b).sum() / ((b * b).sum() + 1e-30))
    return round(float(10 * np.log10(((a - g * b) ** 2).sum() / ((b * b).sum() + 1e-30) + 1e-30)), 1)


def _variants():
    """(file stem, sound, params) for the library render."""
    v = [('jd_stack_ember_slam', 'jd_stack_ember_slam', {}),
         ('jd_stack_ember_slam_gap', 'jd_stack_ember_slam', dict(gap_beats=0.5)),
         ('jd_stack_velvet_hit', 'jd_stack_velvet_hit', {}), ('jd_stack_glass_truth', 'jd_stack_glass_truth', {}),
         ('jd_stack_dha_hit', 'jd_stack_dha_hit', {}),
         ('jd_whoosh_short', 'jd_whoosh_short', {}), ('jd_whoosh_long', 'jd_whoosh_long', {}),
         ('jd_whip', 'jd_whip', {})]
    for bars in (2, 4, 8):
        for bpm in (60, 75, 90, 100, 112.5, 120):
            v.append(('jd_riser_%dbar_%sbpm' % (bars, ('%g' % bpm).replace('.', 'p')), 'jd_riser',
                      dict(bars=bars, bpm=bpm)))
    v += [('jd_sub_drop_short', 'jd_sub_drop', dict(dur=0.8)), ('jd_sub_drop', 'jd_sub_drop', {}),
          ('jd_sub_drop_long', 'jd_sub_drop', dict(dur=3.2)),
          ('jd_hit_soft', 'jd_hit_soft', {}), ('jd_hit_hero', 'jd_hit_hero', {}),
          ('jd_reverse_swell_short', 'jd_reverse_swell', dict(duration=0.75)),
          ('jd_reverse_swell', 'jd_reverse_swell', {}),
          ('jd_reverse_swell_long', 'jd_reverse_swell', dict(duration=3.0)),
          ('jd_glass_slide', 'jd_glass_slide', {}), ('jd_glass_clink', 'jd_glass_clink', {}),
          ('jd_ui_click', 'jd_ui_click', {}), ('jd_ui_tick', 'jd_ui_tick', {}), ('jd_ui_pop', 'jd_ui_pop', {}),
          ('jd_keyboard_laptop', 'jd_keyboard', dict(style='laptop')),
          ('jd_keyboard_mech', 'jd_keyboard', dict(style='mech')),
          ('jd_mouse_click', 'jd_mouse_click', {}), ('jd_mouse_double', 'jd_mouse_click', dict(double=1)),
          ('jd_timeline_scrub', 'jd_timeline_scrub', {}),
          ('jd_projector', 'jd_projector', {}), ('jd_projector_loop', 'jd_projector_loop', {}),
          ('jd_tape_stop', 'jd_tape_stop', {}),
          ('jd_power_down', 'jd_power_down', {}), ('jd_power_up', 'jd_power_up', {}),
          ('jd_crt_collapse', 'jd_crt_collapse', {}), ('jd_ups_beep', 'jd_ups_beep', {}),
          ('jd_fluoro_flicker', 'jd_fluoro_flicker', {}), ('jd_floodlight_clunk', 'jd_floodlight_clunk', {}),
          ('jd_crowd_whisper', 'jd_crowd_whisper', {}), ('jd_crowd_whisper_long', 'jd_crowd_whisper',
                                                        dict(duration=6.0, voices=48)),
          ('jd_vn_blip', 'jd_vn_blip', {}), ('jd_vn_record', 'jd_vn_record', {}), ('jd_vn_send', 'jd_vn_send', {}),
          ('jd_revolving_door', 'jd_revolving_door', {}), ('jd_heartbeat', 'jd_heartbeat', {}),
          ('jd_heartbeat_x4', 'jd_heartbeat', dict(n=4, bpm=72)),
          ('jd_room_night_home', 'jd_room_night_home', {}), ('jd_room_stadium', 'jd_room_stadium', {}),
          ('jd_room_studio', 'jd_room_studio', {}),
          ('jd_tabla_na', 'jd_tabla_na', {}), ('jd_tabla_tin', 'jd_tabla_tin', {}), ('jd_tabla_ge', 'jd_tabla_ge', {}),
          ('jd_tabla_dha', 'jd_tabla_dha', {}), ('jd_tabla_roll', 'jd_tabla_roll', {}),
          ('jd_ghungroo', 'jd_ghungroo', {}), ('jd_sparkle', 'jd_sparkle', {})]
    return v


def riser_pulse_report(x, bars, bpm):
    """Audibility of jd_riser's grid stages -> {step_beats: (onset_db, mod_db, n_pulses)} in 800 Hz-12 kHz.
    onset_db: median over the stage's pulse onsets (the riser's first pulse excluded) of the energy in the
    min(15 ms, 0.3 step) after the onset re the same length before it. mod_db: envelope (2 ms RMS, dB, detrended)
    spectrum at the pulse rate re the median at 0.60-0.85x and 1.15-1.40x that rate (meaningful from ~8 pulses)."""
    y = signal.sosfiltfilt(signal.butter(4, [800.0, 12000.0], 'bandpass', fs=SR, output='sos'),
                           np.asarray(x, dtype=np.float64).mean(1))
    env = np.sqrt(np.convolve(y * y, np.ones(96) / 96.0, 'same'))[::48]           # 1 kHz envelope
    beat = 60.0 / float(bpm)
    grid = _riser_grid(int(bars) * 4)
    on, span = {}, {}
    for k, (b, st) in enumerate(grid):
        span.setdefault(st, [b, b + st])[1] = b + st
        if k == 0:
            continue
        i = int(round(b * beat * SR))
        w = max(8, int(min(0.015, 0.3 * st * beat) * SR))
        on.setdefault(st, []).append(10 * math.log10(float(np.mean(y[i:i + w] ** 2)) /
                                                     (float(np.mean(y[i - w:i] ** 2)) + 1e-30) + 1e-30))
    out = {}
    for st, (b0, b1) in span.items():
        fp = 1.0 / (st * beat)
        seg = 20 * np.log10(env[int(b0 * beat * 1000):int(b1 * beat * 1000)] + 1e-9)
        n = np.arange(len(seg))
        seg = seg - np.polyval(np.polyfit(n, seg, 1), n)
        S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 8192))
        f = np.fft.rfftfreq(8192, 1e-3)
        nb = S[((f > 0.6 * fp) & (f < 0.85 * fp)) | ((f > 1.15 * fp) & (f < 1.4 * fp))]
        mod = 20 * math.log10(float(S[(f > 0.97 * fp) & (f < 1.03 * fp)].max()) / (float(np.median(nb)) + 1e-30))
        out[st] = (round(float(np.median(on[st])), 2) if on.get(st) else None, round(mod, 1),
                   int(round((b1 - b0) / st)))
    return out


def seed_variation(name, params, seeds=(0, 1, 2, 3)):
    """(max |corr| between seed renders, Mmax spread LU): proof that seeds vary the sound but not its level."""
    xs = [np.asarray(globals()[name](seed=s, **params), dtype=np.float64) for s in seeds]
    mm = [A.momentary_max(x) for x in xs]
    cmax = 0.0
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            n = min(len(xs[i]), len(xs[j]))
            a, b = xs[i][:n].mean(1), xs[j][:n].mean(1)
            cmax = max(cmax, abs(float(np.corrcoef(a, b)[0, 1])))
    return round(cmax, 4), round(max(mm) - min(mm), 2)


def _sheet(items, path, cols, w, h):
    from PIL import Image
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w + (cols + 1) * 6, rows * h + (rows + 1) * 6), (7, 4, 4))
    for k, (title, x, hit, sub) in enumerate(items):
        im = A.spectro_image(x, w, h, hit, title, sub)
        sheet.paste(im, (6 + (k % cols) * (w + 6), 6 + (k // cols) * (h + 6)))
    sheet.save(path)
    return path


def render_library(out_dir=None, only=None, alias=True, verbose=True):
    """Render every variant to out_dir/*.wav (48 kHz 24-bit stereo) + QC.md / qc.csv / qc.json + spectrogram
    contact sheets. Returns the QC rows."""
    register()
    out_dir = out_dir or LIBRARY
    os.makedirs(out_dir, exist_ok=True)
    rows, items = [], []
    seen = set()
    t_all = time.time()
    for stem, name, params in _variants():
        if only and stem not in only and name not in only:
            continue
        ts = time.time()
        c0 = _STATE['os_calls']
        with tail_audit() as tlog, toolkit_saturators('count') as nsat:
            x = globals()[name](**params)
        uses_os = _STATE['os_calls'] > c0 or nsat[0] > 0
        el = time.time() - ts
        a = np.asarray(x, dtype=np.float64)
        bed = META[name][0] == 'bed'
        q = measure(a, x.hit, bed=bed)
        q['problems'] += sorted(set(tlog))
        q['alias_db'] = alias_residual(name, params) if (alias and uses_os) else None
        if q['alias_db'] is not None and q['alias_db'] > -60:
            q['problems'].append('alias residual %.1f dB' % q['alias_db'])
        if name not in seen:
            seen.add(name)
            q['seed_corr'], q['seed_mmax_spread'] = seed_variation(name, params)
            if q['seed_corr'] > 0.995:
                q['problems'].append('seeds do not vary (corr %.4f)' % q['seed_corr'])
        path = os.path.join(out_dir, stem + '.wav')
        A._write_wav(path, a, 24)
        back, sr = A.read_wav(path)
        q['wav_err'] = float(np.max(np.abs(back - a)))
        if sr != SR or back.shape != a.shape or q['wav_err'] > 1.5 / 8388608.0:
            q['problems'].append('wav round trip error %.2e' % q['wav_err'])
        q.update(file=os.path.basename(path), sound=name, params=params, category=META[name][0],
                 level=META[name][2], raw_hf_db=round(getattr(x, 'raw_hf_db', float('nan')), 1),
                 render_s=round(el, 2), status='PASS' if not q['problems'] else 'FAIL')
        rows.append(q)
        sub = '%.2fs hit %.3f | Mmax %.1f LUFS | TP %.1f dBTP | %s' % (q['dur'], q['hit'], q['mmax_lufs'], q['tp_dbtp'],
                                                                     q['status'])
        items.append((stem, a, x.hit, sub))
        if verbose:
            print('%-30s %6.2fs hit %7.3f  Mmax %6.1f  I %6.1f  TP %5.1f  nyq %6.1f  alias %6s  mono %+5.2f  %s %s' % (
                stem, q['dur'], q['hit'], q['mmax_lufs'], q['i_lufs'], q['tp_dbtp'], q['nyq_db'],
                '-' if q['alias_db'] is None else '%.1f' % q['alias_db'], q['mono_db'], q['status'],
                '; '.join(q['problems'])))
            sys.stdout.flush()
    if not only:
        pages = [_sheet(items, os.path.join(out_dir, 'contact_sheet.png'), 6, 360, 210)]
        for k in range(0, len(items), 15):
            pages.append(_sheet(items[k:k + 15], os.path.join(out_dir, 'contact_sheet_p%d.png' % (k // 15 + 1)),
                                3, 620, 300))
        _write_qc(rows, out_dir, time.time() - t_all)
        if verbose:
            print('contact sheets:', ', '.join(pages))
    return rows


def _write_qc(rows, out_dir, el):
    cols = ['file', 'sound', 'category', 'dur', 'hit', 'level', 'mmax_lufs', 'i_lufs', 'peak_dbfs', 'tp_dbtp',
            'crest_db', 'centroid_hz', 'rolloff85_hz', 'sub_pct', 'low_pct', 'lowmid_pct', 'mid_pct', 'high_pct',
            'air_pct', 'nyq_db', 'raw_hf_db', 'alias_db', 'clip_run', 'seam_ratio', 'seed_corr', 'seed_mmax_spread',
            'corr', 'mono_db', 'status', 'problems', 'params']
    with open(os.path.join(out_dir, 'qc.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for q in rows:
            w.writerow([json.dumps(q.get(c)) if c in ('params', 'problems') else q.get(c, '') for c in cols])
    with open(os.path.join(out_dir, 'qc.json'), 'w') as fh:
        json.dump(rows, fh, indent=1)
    npass = sum(q['status'] == 'PASS' for q in rows)
    L = ['# jawad SFX library QC (%s)' % time.strftime('%Y-%m-%d %H:%M'), '',
         'Generated by `python3 sfx_jawad.py render` (pipeline/jawad_reels). %d files, %d PASS, %d FAIL, %.0f s.' % (
             len(rows), npass, len(rows) - npass, el), '',
         'All files: 48 kHz, 24-bit PCM, stereo. Mmax = max momentary loudness (400 ms, BS.1770); I = integrated '
         '(beds: the loop level). TP = true peak (4x). nyq = energy above 20.5 kHz re total (after the guard filter); '
         'raw_hf = the same before it. alias = gain-matched residual of the normal render vs a reference render '
         'in which every waveshaper, FM operator and varispeed read is computed at 32x: this module\'s own stages '
         '(8x in normal renders) and the toolkit\'s audio._sat / _asat (1x in normal renders; inside audio._thump, '
         'audio.bass_enhance and the toolkit layers of the stacks). "-" = none of those stages (band-limited '
         'oscillators and linear filters only, nothing that can alias). clip = longest flat-topped run (samples). '
         'Bands = % of energy: sub < 60 Hz, low 60-250, lmid 250-1k, mid 1-4k, high 4-12k, air > 12k. '
         'seed = max |corr| between seeds 0-3 (variation) / their Mmax spread (LU). mono = Mmax of the (L+R)/2 '
         'fold-down minus Mmax of the stereo file (dB; phone speakers).', '',
         'Pass rules: audio.qc() clean (edges, DC, -1 dBFS cap), TP <= -1.0 dBTP, clip <= 3, nyq <= -60 dB, '
         'alias <= -60 dB, mono >= -%.1f dB (beds >= -%.1f dB), beds: seam ratio <= 1.5, I = -20 +-0.3 LUFS, '
         '24-bit round trip exact.' % (MONO_LOSS, MONO_LOSS_BED), '',
         '| file | dur s | hit s | Mmax | I | TP dBTP | crest | centroid Hz | roll85 Hz | sub/low/lmid/mid/high/air % '
         '| nyq dB | alias dB | mono dB | clip | seed corr/spread | status |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for q in rows:
        L.append('| %s | %.2f | %.3f | %.1f | %.1f | %.2f | %.1f | %d | %d | %s/%s/%s/%s/%s/%s | %.0f | %s | %+.2f | %d '
                 '| %s | %s |' % (
            q['file'][:-4], q['dur'], q['hit'], q['mmax_lufs'], q['i_lufs'], q['tp_dbtp'], q['crest_db'],
            q['centroid_hz'], q['rolloff85_hz'], q['sub_pct'], q['low_pct'], q['lowmid_pct'], q['mid_pct'],
            q['high_pct'], q['air_pct'], q['nyq_db'], '-' if q['alias_db'] is None else '%.1f' % q['alias_db'],
            q['mono_db'], q['clip_run'], '-' if 'seed_corr' not in q else '%.3f/%.2f' % (q['seed_corr'], q['seed_mmax_spread']),
            q['status'] + ('' if not q['problems'] else ' (' + '; '.join(q['problems']) + ')')))
    with open(os.path.join(out_dir, 'QC.md'), 'w') as fh:
        fh.write('\n'.join(L) + '\n')


# =============================================================================================== self-test
def selftest():
    """Every sound at default params: qc, true peak, clipping, guard band, alias residual (when it has an
    oversampled stage), level calibration, seed variation; riser grid maths; bed seams; stack structure and hit
    alignment; the VO helper (hero blocking, ducking, carving, mixing); registration; primitive alias tests."""
    os.makedirs(A.SELFTEST, exist_ok=True)
    fails = []
    t_all = time.time()

    def check(ok, msg):
        if not ok:
            fails.append(msg)
            print('  FAIL', msg)
        return ok
    names = register()
    check(register() == names, 'register() not idempotent')
    for n in names:
        check(A.resolve(n, fuzzy=False) == n, 'resolve %s' % n)
    for a, n in ALIASES.items():
        check(A.resolve(a, fuzzy=False) == n, 'alias %s -> %s' % (a, n))
    # primitives: alias-safe shaper vs naive tanh, varispeed accuracy
    tt = np.arange(SR) / SR

    def inharm(y, f0):
        Y = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2
        f = np.fft.rfftfreq(len(y), 1.0 / SR)
        m = (f < 19000) & np.all([np.abs(f - k * f0) > 30 for k in range(1, 8)], axis=0)
        return 10 * np.log10(Y[m].sum() / Y.sum())
    xs = np.sin(TWO_PI * 7000.0 * tt)
    e_os, e_naive = inharm(shape(xs, 4.0), 7000.0), inharm(np.tanh(4.0 * xs), 7000.0)
    print('shape(): inharmonic (alias) energy %.1f dB vs naive tanh %.1f dB' % (e_os, e_naive))
    check(e_os < -80 and e_naive > -40, 'shape alias test %.1f / %.1f' % (e_os, e_naive))
    src = np.sin(TWO_PI * 5000.0 * np.arange(2 * SR) / SR)
    pos = np.cumsum(np.linspace(1, 0.05, SR)) + 100
    ref = np.sin(TWO_PI * 5000.0 * pos / SR)
    e_vr = 10 * np.log10(((varread(src, pos) - ref)[1000:-1000] ** 2).sum() / (ref[1000:-1000] ** 2).sum())
    print('varread(): error %.1f dB' % e_vr)
    check(e_vr < -90, 'varread error %.1f dB' % e_vr)
    fb = fm_bell_os(0.5, 8000.0, 1.41, 1.2, 0.1, 0.02)
    check(_hf_db(fb, 20500.0) < -80, 'fm_bell_os energy above 20.5 kHz')
    # riser grid maths
    for bars, bpm in ((2, 60), (4, 112.5), (8, 120), (1, 90)):
        x = jd_riser(bars=bars, bpm=bpm)
        L = int(round(riser_len(bars, bpm) * SR))
        check(len(x) == L and abs(x.hit - L / SR) < 1e-9, 'riser %d bar %g bpm length %d != %d' % (bars, bpm, len(x), L))
    for bad in (dict(bars=3), dict(bpm=150), dict(bpm=55)):
        try:
            jd_riser(**bad)
            check(False, 'riser accepted %s' % bad)
        except ValueError:
            pass
    g = _riser_grid(16)
    check(g[0] == (0.0, 1.0) and g[-1] == (15.875, 0.125) and abs(sum(s for _, s in g) - 16) < 1e-9, 'riser grid')
    check(_riser_grid(4) == [(0.0, 1.0), (1.0, 1.0), (2.0, 0.5), (2.5, 0.5), (3.0, 0.25), (3.25, 0.25), (3.5, 0.125),
                             (3.625, 0.125), (3.75, 0.125), (3.875, 0.125)], 'riser grid 1 bar %s' % _riser_grid(4))
    check([st for _, st in _riser_grid(8)] == [1.0] * 4 + [0.5] * 4 + [0.25] * 4 + [0.125] * 8, 'riser grid 2 bars')
    # every sound
    items = []
    print('%-22s %6s %7s %6s %6s %6s %7s %6s %6s %s' % ('sound', 'dur', 'hit', 'Mmax', 'TP', 'nyq', 'alias', 'mono', 'seed',
                                                         'qc'))
    for name in names:
        ts = time.time()
        c0 = _STATE['os_calls']
        with tail_audit() as tlog, toolkit_saturators('count') as nsat:
            x = globals()[name]()
        uses = _STATE['os_calls'] > c0 or nsat[0] > 0
        bed = META[name][0] == 'bed'
        q = measure(np.asarray(x), x.hit, bed=bed)
        q['problems'] += sorted(set(tlog))
        al = alias_residual(name, {}) if uses else None
        x1 = globals()[name](seed=1)
        n = min(len(x), len(x1))
        cs = abs(float(np.corrcoef(np.asarray(x[:n]).mean(1), np.asarray(x1[:n]).mean(1))[0, 1]))
        print('%-22s %6.2f %7.3f %6.1f %6.2f %6.1f %7s %+6.2f %6.3f %s  (%.1fs)' % (
            name, q['dur'], q['hit'], q['mmax_lufs'], q['tp_dbtp'], q['nyq_db'], '-' if al is None else '%.1f' % al,
            q['mono_db'], cs, '; '.join(q['problems']) or 'ok', time.time() - ts))
        sys.stdout.flush()
        check(isinstance(x, A.Sfx) and x.dtype == np.float32 and x.ndim == 2 and x.shape[1] == 2, name + ' format')
        check(not q['problems'], '%s qc: %s' % (name, q['problems']))
        check(al is None or al <= -60, '%s alias residual %s dB' % (name, al))
        check(cs < 0.995, '%s seed 0/1 identical (corr %.4f)' % (name, cs))
        check(0 <= x.hit <= len(x) / SR, '%s hit %.3f outside the sound' % (name, x.hit))
        if not bed:
            target = REF + META[name][2]
            capped = q['peak_dbfs'] > A.PEAK_CAP_DB - 0.05 or q['tp_dbtp'] > TP_CEIL - 0.1
            check(abs(q['mmax_lufs'] - target) < 0.15 or (capped and q['mmax_lufs'] < target),
                  '%s Mmax %.2f vs level target %.2f' % (name, q['mmax_lufs'], target))
        items.append((name, np.asarray(x), x.hit, '%.2fs hit %.3f Mmax %.1f TP %.1f' % (
            q['dur'], q['hit'], q['mmax_lufs'], q['tp_dbtp'])))
    _sheet(items, os.path.join(A.SELFTEST, 'sfx_jawad_sheet.png'), 5, 420, 230)
    # designed accents (QA round 1). jd_glass_slide: the landing is the accent at the hit
    for d_ in (0.15, 0.3, 0.5, 0.8):
        for s_ in (0, 1, 2):
            g_ = jd_glass_slide(seed=s_, dur=d_)
            m_, h_ = np.asarray(g_, dtype=np.float64).mean(1), _n(g_.hit)
            c_ = 10 * math.log10(float(np.mean(m_[h_:h_ + _n(0.02)] ** 2)) / float(np.mean(m_[h_ - _n(0.03):h_] ** 2)))
            check(c_ >= 6.0, 'jd_glass_slide dur %.2f seed %d: first 20 ms of the landing only %+.1f dB over the '
                             '30 ms before' % (d_, s_, c_))
    # jd_riser: every grid stage audible (onset contrast; modulation where the stage has >= 8 pulses)
    for bars, bpm in ((1, 90), (2, 75), (4, 90), (8, 120)):
        rp = riser_pulse_report(jd_riser(bars=bars, bpm=bpm), bars, bpm)
        print('jd_riser %d bar %g bpm: %s' % (bars, bpm, ', '.join('1/%d onset %+.1f dB mod %+.1f dB (%d)' % (
            round(4 / st), v[0], v[1], v[2]) for st, v in sorted(rp.items(), reverse=True))))
        check(sorted(rp) == [0.125, 0.25, 0.5, 1.0], 'jd_riser %d bar: stages %s' % (bars, sorted(rp)))
        for st, (o_, md, npl) in rp.items():
            check(o_ is not None and o_ >= 2.5, 'jd_riser %d bar %g bpm 1/%d onsets %s dB' % (bars, bpm, round(4 / st), o_))
            check(npl < 8 or md >= 10.0, 'jd_riser %d bar %g bpm 1/%d modulation %+.1f dB' % (bars, bpm, round(4 / st), md))
    # jd_reverse_swell: mono fold-down (phone speakers) over lengths and seeds
    for d_ in (0.75, 1.5, 3.0):
        for s_ in (0, 1, 2):
            q_ = measure(np.asarray(jd_reverse_swell(seed=s_, duration=d_)), d_)
            check(q_['mono_db'] >= -MONO_LOSS, 'jd_reverse_swell %.2f s seed %d mono %+.2f dB' % (d_, s_, q_['mono_db']))
    # stacks: bible structure + rendered hit alignment
    es = ember_slam(10.0, bpm=90, riser_beats=4, gap_beats=0.5)
    check([c['name'] for c in es] == ['riser', 'flash_hit', 'impact_big', 'sub_drop'], 'ember_slam names')
    check(abs(es[0]['t'] - (10.0 - 0.5 * 60 / 90)) < 1e-9 and abs(es[0]['params']['duration'] - 4 * 60 / 90) < 1e-3
          and abs(es[1]['t'] - 9.997) < 1e-9 and es[3]['lp'] == 120, 'ember_slam timing')
    check([c['name'] for c in velvet_hit(5.0)] == ['heartbeat', 'impact_soft', 'glass_tap'], 'velvet_hit names')
    check([c['name'] for c in glass_truth(5.0)] == ['ui_click', 'glass_tap', 'sub_drop', 'jd_sparkle'], 'glass_truth')
    check([c['name'] for c in dha_hit(5.0)] == ['jd_tabla_roll', 'jd_tabla_dha', 'sub_drop', 'jd_ghungroo'], 'dha_hit')
    for sname in ('jd_stack_ember_slam', 'jd_stack_dha_hit', 'jd_stack_glass_truth'):
        x = np.asarray(globals()[sname](), dtype=np.float64)
        h = globals()[sname]().hit
        env = np.abs(x).max(1)
        i0, i1 = _n(h - 0.004), _n(h + 0.012)
        pre = env[max(0, _n(h - 0.06)):i0].max() if i0 > max(0, _n(h - 0.06)) else 1e-9
        on = i0 + int(np.argmax(env[i0:i1] > 0.5 * env[i0:i1].max()))
        check(abs(on / SR - h) < 0.006 and env[i0:i1].max() > 1.5 * pre,
              '%s transient at %.4f s vs hit %.4f s' % (sname, on / SR, h))
    # VO helper
    words = [dict(word='ek', start=0.5, end=1.2), dict(word='do', start=1.3, end=2.0), dict(word='teen', start=3.0,
                                                                                              end=3.6)]
    try:
        fit_under_vo([dict(t=1.0, name='impact_big')], words)
        check(False, 'hero on a word not blocked')
    except HeroOnWordError as e:
        check('nearest legal hit' in str(e), 'HeroOnWordError message')
    # bible 4.1 clearance from the unpadded word edges: 120 ms after a word end, 300 ms before the next word
    for t_, ok_, why in ((2.15, True, '0.15 s after "do" ends, 0.85 s before "teen"'),
                         (2.12, True, 'exactly 0.12 s after "do" ends'),
                         (2.70, True, 'exactly 0.30 s before "teen" starts'),
                         (2.10, False, 'only 0.10 s after "do" ends'),
                         (2.75, False, 'only 0.25 s before "teen" starts')):
        try:
            fit_under_vo([dict(t=t_, name='jd_hit_hero')], words)
            check(ok_, 'hero at %.2f (%s) not blocked' % (t_, why))
        except HeroOnWordError as e:
            check(not ok_, 'hero at %.2f (%s) blocked: %s' % (t_, why, e))
    try:                                                      # non-impact hero: 150 ms after is enough
        fit_under_vo([dict(t=2.80, name='jd_ui_pop', hero=True)], words)
    except HeroOnWordError as e:
        check(False, 'non-impact hero 0.20 s before a word blocked: %s' % e)
    try:
        fit_under_vo(dha_hit(1.6), words)
        check(False, 'dha_hit on a word not blocked')
    except HeroOnWordError:
        pass
    cues = [dict(t=2.5, name='impact_big'), dict(t=1.5, name='ui_click'), dict(t=1.6, name='shimmer'),
            dict(t=0.8, name='jd_whoosh_short'), dict(t=2.9, name='jd_riser', params=dict(bars=1, bpm=90)),
            dict(t=4.5, name='jd_ui_tick')]
    out, rep = fit_under_vo(cues, words, report=True)
    by = {c['name']: c for c in out}
    check(by['impact_big']['gain_db'] == 0 and 'lp' not in by['impact_big'], 'hero in a gap untouched')
    check(by['ui_click']['gain_db'] == -8.0, 'mid duck -8 (got %s)' % by['ui_click']['gain_db'])
    check(by['shimmer']['gain_db'] == -6.0 and by['shimmer']['hp'] == 5500, 'air duck + hp')
    check(by['jd_whoosh_short']['gain_db'] == -6.0 and by['jd_whoosh_short']['lp'] == 1100, 'dark duck + lp')
    check(by['jd_riser']['gain_db'] == -6.0 and by['jd_riser']['lp'] == 1100 and rep['spans'], 'span carve')
    check(by['jd_ui_tick']['gain_db'] == 0, 'cue outside speech untouched')
    check(cues[1].get('gain_db', 0) == 0 and 'vo' not in cues[1], 'input cues mutated')
    kept = fit_under_vo([dict(t=1.0, name='impact_big'), dict(t=4.5, name='jd_hit_hero')], words, hero='drop')
    check([c['name'] for c in kept] == ['jd_hit_hero'], 'hero drop')
    sl = hero_slots(words, dur=6.0)
    check(sl == [(0.0, 0.2), (2.12, 2.7), (3.72, 6.0)], 'hero_slots %s' % sl)
    # real vo_chain word timings. (1) Frozen excerpt of the Vlad v4 DEV take (QA round 1, VO at 0.3 s): the
    # dramatic 0.527 s pause after "hai..." and the 0.501 s pause after "hue!" are bible-legal hero gaps.
    ex = _VO_EXCERPT
    sl = hero_slots(ex, offset=0.3, dur=25.0)
    check((3.911, 4.018) in sl and (15.029, 15.11) in sl, 'hero slots after "hai..." / "hue!": %s' % sl)
    for cue in (dict(t=3.920, name='jd_hit_hero'), dict(t=15.059, name='impact_big')):
        try:
            fit_under_vo([cue], ex, offset=0.3)
        except HeroOnWordError as e:
            check(False, 'bible-legal %s at %.3f raised: %s' % (cue['name'], cue['t'], e))
    try:
        fit_under_vo([dict(t=3.85, name='impact_big')], ex, offset=0.3)
        check(False, 'impact_big 0.059 s after "hai..." not blocked')
    except HeroOnWordError as e:
        check('nearest legal hit 3.911' in str(e), 'nearest legal hit after "hai...": %s' % e)
    # (2) synthetic VO audio whose word "do" rings on 100 ms past its timestamp (whisper ends run early on TTS):
    # words alone allow a hero 0.15 s after the timestamp, the audio (on by default for vo_chain paths) does not
    tt_ = np.arange(_n(4.0)) / SR
    vo_ = np.zeros(len(tt_))
    rg_ = np.random.default_rng(5)
    for a_, b_, lv_ in ((0.5, 1.2, 1.0), (1.3, 2.0, 1.0), (2.0, 2.1, 0.3), (3.0, 3.6, 1.0)):
        m_ = (tt_ >= a_) & (tt_ < b_)
        vo_[m_] = rg_.standard_normal(int(m_.sum())) * 0.1 * lv_
    for t_, aud_, ok_ in ((2.15, None, True), (2.15, (vo_, SR), False), (2.24, (vo_, SR), True)):
        try:
            fit_under_vo([dict(t=t_, name='jd_hit_hero')], words, vo_audio=aud_)
            check(ok_, 'hero at %.2f on the audible tail not blocked (vo_audio %s)' % (t_, aud_ is not None))
        except HeroOnWordError as e:
            check(not ok_, 'hero at %.2f blocked (vo_audio %s): %s' % (t_, aud_ is not None, e))
    # (3) the live vo_chain selftest output, when present (it is regenerated, so only properties are checked)
    if os.path.exists(VO_SELFTEST_WORDS):
        wl = _load_words(VO_SELFTEST_WORDS, 0.3)
        ends = np.maximum.accumulate([b for _, b in wl])
        gaps = [(float(e), a2) for e, (a2, _) in zip(ends, wl[1:]) if a2 - e >= 0.42 - 1e-3]
        T_ = wl[-1][1] + 5.0

        def inside(a, b, g):
            return g[0] + 0.12 - 1e-3 <= a and b <= g[1] - 0.30 + 1e-3

        def interior(sl):
            return [(a, b) for a, b in sl if wl[0][0] < a and b < wl[-1][1]]
        # (3a) words only: every word gap >= 0.42 s holds a hero slot, every interior slot lies in such a gap
        sw = interior(hero_slots(VO_SELFTEST_WORDS, offset=0.3, dur=T_, vo_audio=None))
        check(all(any(inside(a, b, g) for a, b in sw) for g in gaps if g[1] - g[0] >= 0.422)
              and all(any(inside(a, b, g) for g in gaps) for a, b in sw),
              'live VO (words only): gaps %s vs hero slots %s' % (gaps, sw))
        # (3b) words + the VO audio (default for a vo_chain path): slots only shrink, stay clear of the measured
        # speech, and the dramatic pause after "hai..." holds one whenever its real silence is >= 0.43 s
        hw_, src_ = hero_windows(VO_SELFTEST_WORDS, 0.3)
        sa = interior(hero_slots(VO_SELFTEST_WORDS, offset=0.3, dur=T_))
        check(src_ == 'words+audio', 'live VO: audio not used (%s)' % src_)
        check(all(any(c <= a and b <= d for c, d in sw) for a, b in sa), 'live VO: audio slots %s outside %s' % (sa, sw))
        check(all(not any(c < h + 0.30 - 1e-6 and d > h - 0.12 + 1e-6 for c, d in hw_) for a, b in sa for h in (a, b)),
              'live VO: an audio-checked hero slot touches speech')
        raw = json.load(open(VO_SELFTEST_WORDS))
        raw = raw.get('words', []) if isinstance(raw, dict) else raw
        hai = [w for w in raw if str(w.get('word', '')).startswith('hai') and w.get('end') is not None]
        print('VO helper on %s: word gaps >= 0.42 s %d, hero slots words-only %s, words+audio %s' % (
            VO_SELFTEST_WORDS, len(gaps), sw, sa))
        if hai:
            he = float(hai[0]['end']) + 0.3
            w0 = [w for w in hw_ if w[0] <= he + 1e-6 and w[1] >= he - 1e-6]
            w1 = [w for w in hw_ if w[0] > he]
            if w0 and w1 and w1[0][0] - w0[0][1] >= 0.43:
                check(any(a >= w0[0][1] + 0.12 - 1e-3 and b <= w1[0][0] - 0.30 + 1e-3 for a, b in sa),
                      'live VO: no hero slot in the %.3f s silence after "hai..."' % (w1[0][0] - w0[0][1]))
    mixc = out + ember_slam(5.0, 90, gap_beats=0.5) + glass_truth(4.4) + velvet_hit(5.9)
    rep_m = A.mix(mixc, 7.5, os.path.join(A.SELFTEST, 'sfx_jawad_mix.wav'), bed='jd_room_studio', bed_gain_db=-30,
                  tp_ceiling=-2.0, verbose=False)
    check(abs(rep_m['integrated_lufs'] + 18.0) < 0.15 and rep_m['true_peak_dbtp'] <= -2.0,
          'mix %.2f LUFS / %.2f dBTP' % (rep_m['integrated_lufs'], rep_m['true_peak_dbtp']))
    A.mix_overview(rep_m, os.path.join(A.SELFTEST, 'sfx_jawad_mix.png'), 'sfx_jawad selftest mix')
    # tape_stop_fx on a real buffer: untouched before t0, silent after, no alias
    bed = np.asarray(A.sound('jd_room_studio'), dtype=np.float64)[:_n(3.0)]
    ts_ = tape_stop_fx(bed, 1.0, 0.8)
    check(np.array_equal(ts_[:_n(1.0)], bed[:_n(1.0)]) and not np.any(ts_[_n(1.8) + 1:]), 'tape_stop_fx window')
    check(abs(ts_[_n(1.0)] - bed[_n(1.0)]).max() < 0.05 * np.abs(bed).max(), 'tape_stop_fx continuity')
    # wav round trip
    p = os.path.join(A.SELFTEST, 'sfx_jawad_roundtrip.wav')
    x = np.asarray(A.sound('jd_hit_hero'), dtype=np.float64)
    A._write_wav(p, x, 24)
    back, sr = A.read_wav(p)
    check(sr == SR and back.shape == x.shape and np.max(np.abs(back - x)) < 1.5 / 8388608.0, 'wav round trip')
    print('sfx_jawad selftest: %d sounds, %d failures, %.0f s' % (len(names), len(fails), time.time() - t_all))
    if fails:
        print('FAILURES:\n  ' + '\n  '.join(fails))
    else:
        print('sfx_jawad selftest OK')
    return not fails


def catalog():
    register()
    for name, (cat, band, level, send, ch, use) in META.items():
        print('%-22s %-10s %-5s %+5.1f  %-40s %s' % (name, cat, band, level, json.dumps(A.params_of(name)), ch))


def main(argv):
    if len(argv) > 1 and argv[1] in ('selftest', '--selftest'):
        return 0 if selftest() else 1
    if len(argv) > 1 and argv[1] == 'render':
        out = argv[argv.index('--out') + 1] if '--out' in argv else None
        only = argv[argv.index('--only') + 1].split(',') if '--only' in argv else None
        rows = render_library(out, only, alias='--no-alias' not in argv)
        return 0 if all(q['status'] == 'PASS' for q in rows) else 1
    if len(argv) > 1 and argv[1] == 'catalog':
        catalog()
        return 0
    if len(argv) > 2 and argv[1] == 'play':
        register()
        params = json.loads(argv[3]) if len(argv) > 3 and argv[3].startswith('{') else {}
        out = [a for a in argv[3:] if a.endswith('.wav')]
        out = out[0] if out else os.path.join(A.OUT, 'audition', argv[2] + '.wav')
        x = globals()[argv[2]](**params)
        A._write_wav(out, x, 24)
        q = measure(np.asarray(x), x.hit, bed=META[argv[2]][0] == 'bed')
        A.spectro_image(x, 1000, 420, x.hit, argv[2], json.dumps(params)).save(out[:-4] + '.png')
        print(json.dumps(q, indent=1))
        print(out, out[:-4] + '.png')
        return 0
    print(__doc__)
    return 0


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    import sfx_jawad as _M          # run inside the importable module so registry checks see one module name
    sys.exit(_M.main(sys.argv))
