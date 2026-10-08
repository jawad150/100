"""audio.py: procedural SFX library (NO MUSIC), cue-sheet mixer, BS.1770 loudness and stem export for the
Organic Fostering reels. Everything is synthesised in numpy/scipy at 48 kHz stereo float, deterministic (seeded).
Importing has no side effects (no files, no rendering); sounds render lazily and are cached.

CONVENTIONS
    SR = 48000. A sound is an Sfx: a float32 (N, 2) ndarray with .hit (seconds from its start to the designed
    hit/peak), .name and .dur. Hit means: impacts/clicks = the transient; whooshes = the loudest point (the pass);
    risers / reverse swells = the END (they land on the hit); swells that track a motion (bar_grow, slider_drag,
    grow_swell, slot_tick) = the end of the motion (cue those with align='start' at the motion start).
    LEVELS ARE PRE-BALANCED: each sound is calibrated so its max momentary loudness (400 ms, K-weighted) equals
    REF_LUFS (-20) + a designed per-sound offset (impacts loud, UI quiet; see Mmax in the catalog), peaks <= -1
    dBFS. So gain_db=0 is the right starting point everywhere; nudge +-3 dB. The final mix is normalised anyway.
    Every sound: DC/subsonic high-pass, click-free edges (raised-cosine fades, generators taper to exactly 0),
    trailing silence trimmed. Low-end sounds carry psychoacoustic harmonics (bass_enhance) so they still read on
    phone speakers (<= 7 dB loss through a 250 Hz high-pass, measured).

LIBRARY (all keyword params optional; seed=0 for every sound; 'dur' and 'duration' are interchangeable)
    sound(name, **params) -> cached read-only Sfx (copy before editing)      e.g. sound('riser', duration=1.6)
    heartbeat(n=2, bpm=62) ... any catalog name is also a plain function returning a fresh Sfx
    hit_offset(name, **params) -> seconds;  names(category=None) -> list;  params_of(name) -> {param: default}
    resolve(name) -> library name (ALIASES: whoosh, boom, impact, hit, click, tick, ding, chime, coin, kaching,
        swell, flash, drop, glitch, swish, slide, snap, plip, grow, sting, zoom, shutter, rustle, by, heart, ...)
    SOUNDS[name] -> dict(fn, category, character, use, send)   categories: impact transition ui money texture bed

MIXER
    rep = mix(cues, dur, out_wav=None, stem_wav=None, bed=None, bed_gain_db=-30, *, target_lufs=-18,
              tp_ceiling=-1.5, auto_duck=True, room_send=True, glue=True, vary=True, bits=24, split_stems=False,
              tail_fade=0.4, verbose=True)
      cue = {'t': 2.45, 'name': 'impact_big', 'gain_db': 0, 'pan': 0, 'align': 'hit' | 'start', 'params': {},
             optional: 'seed', 'rate' (speed/pitch x, hit scales), 'lp'/'hp' (Hz), 'width' (0 mono..1..2 wide),
             'dur' (truncate s, faded), 'send_db' (room-reverb send override)}; tuples (t, name, gain_db, pan) ok.
      align='hit' (default) puts the sound's designed hit exactly on t (risers END on t, whooshes PEAK on t);
      align='start' starts the sound at t. Repeats of a sound get seeds 0..3 in turn (vary) so they never sound
      machine-gunned. Chain: duck_under (cluster auto-gain) -> shared 'studio' room send (per-category level)
      -> gentle bus glue (2:1, soft knee, ~2 dB on the biggest hits) -> bed (anchored, sidechain-ducked 5 dB under
      the SFX) -> loudness normalisation to target_lufs (BS.1770-4, gated) + 4x-oversampled true-peak lookahead
      limiter (soft knee), iterated until |I - target| < 0.05 LU and TP <= tp_ceiling - 0.05.
      Writes out_wav (48 kHz, 24-bit, or bits=16 TPDF-dithered) for muxing and stem_wav (48 kHz 24-bit, same
      audio); split_stems=True also writes <stem>_fx.wav and <stem>_bed.wav (same gain curve, they sum to the mix).
      bed: None | 'room_tone' | {'name', 't0', 't1', 'gain_db' (relative to bed_gain_db), 'fade', 'offset',
           'params'} | list of those. bed_gain_db=-30 puts the bed at about -40 LUFS in the master (target + gain
           + 8), i.e. felt more than heard; -24 = present, -36 = subliminal.
      rep: integrated_lufs, true_peak_dbtp, sample_peak_dbfs, lra_lu, max_momentary_lufs, max_short_term_lufs,
           limiter_max_gr_db, limiter_pct_over_1db, comp_max_gr_db, bed_lufs, placed (per-cue start/hit/gain/
           duck_db/warn: 'hit before 0 s' | 'tail cut at end'), files, audio (float32 master). Printed by
           report_text(rep).
    duck_under(cues, window=0.09, strength=0.75, max_cut_db=8, under_impact_db=1.5) -> new cues with gain_db
        reduced where several cues hit within +-window (priority impact > transition > money > texture > ui;
        one equal neighbour -2.3 dB, three -4.5 dB) and smaller cues just after an impact -1.5 dB. mix() applies it.
    sidechain(x, key, depth_db=4, attack=0.03, release=0.45) -> x ducked under key (used for the bed)
    on_beats(name, bpm, beats, offset=0, **cue) -> cues on the BPM grid; callables get the beat index
    build_reel('reel1') -> mixes pipeline/fostering/reel1.py: DUR, cues() and optional BED / BED_GAIN_DB; writes
        AUDIO/reel1_sfx.wav (render.py muxes this automatically) and AUDIO/reel1_sfx_stem.wav (24-bit stem).
    mix_overview(rep, 'x.png', title) -> PNG: spectrogram, waveform, momentary-loudness curve, cue hit ticks.

ANALYSIS / DSP (public helpers)
    loudness(x) integrated LUFS (BS.1770-4 K-weighting + gates, verified against ffmpeg ebur128 to 0.1 LU);
    true_peak(x) dBTP (4x); momentary_max(x, win=0.4); loudness_curve(x); loudness_range(x) LRA;
    stats(x, hit) -> dur/peak/rms/crest/Mmax/dc/edges/corr;  qc(x, hit) -> list of problems (empty = clean)
    reverb(x, preset, wet_db, dry=1) with generated stereo IRs: make_ir(rt60, predelay, damp, er, lo_cut, ...),
        presets REVERBS: room, studio, dark, plate, hall, air, outdoor;  reverb_circular() for loops
    noise_band(d, rng, fc, bw, width, comb) time-varying spectral band noise; modal(); fm_bell(); osc(); pan();
    width(); decorrelate(); transient(); bass_enhance(); lp/hp/bp/reson/eq; kweight(); read_wav(path)
    spectro_image(x, w, h, hit, title, sub) -> PIL image; catalog_sheets(items, 'path_%d.png')

CATALOG  (dur = rendered length incl. tail at default params, hit = hit offset s, Mmax = max momentary LUFS)
 name            dur    hit    Mmax  character -> best use
 IMPACT
 heartbeat      2.36  0.006   -23   lub-dub, muffled sub thump + felt click, phone harmonics (n, bpm) -> R1 cold
                                    open, emotional beats; heartbeat(n=1) for a single beat
 impact_big     6.17  0.003   -16   deep cinematic boom: 33 Hz sub sweep, kick punch, crack, hall bloom, rumble
                                    tail (tail=1 scales) -> the question slam, title slams (pair with riser)
 impact_soft    1.27  0.006   -23   gentle felt thump, soft air puff, short room -> soft landings, R3 hits
 sub_drop       2.40  0.010   -22   sub pitch-drop 90 -> 28 Hz with audible harmonics (dur) -> under smash cuts
 flash_hit      2.01  0.100   -19   0.1 s reverse hiss suck -> crack, thump, metallic zing, plate bloom -> flash
                                    frames / montage cuts on the beat
 logo_sting     9.54  0.420   -20   0.42 s airy swell -> soft impact + shimmer + warm bell bloom + 4.6 s air
                                    tail (tone=1 pitch) -> every end-card logo resolve
 TRANSITION
 whip           0.78  0.210   -23   very fast bright "fwip" 600 Hz -> 5.2 kHz + faint zip (direction +-1) ->
                                    whip pans, smash cuts, hook montage
 whoosh_fast    1.17  0.420   -23   quick airy rush with low body and sizzle, panning -> cards flying in, windows
 whoosh_slow    4.27  1.200   -25   big soft swell of air, jet-flanged, hall tail -> slow reveals, camera moves
 whoosh_by      1.53  0.770   -24   physically modelled doppler pass (dur, speed m/s, dist m, direction): per-ear
                                    delay, air absorption, whistle bands drop in pitch -> R2 card tunnel, orbits
 swish_small    0.66  0.140   -31   small soft high swish -> chips, tags, cursor moves
 air_zoom       1.53  0.620   -22   zoom-through air rush, jet flange, pressure swell, wide at the hit -> R3 zoom
                                    through the letter U, iris transitions
 riser          2.00  2.000   -24   noise sweep 250 Hz -> 9 kHz + rising tremolo tone + air rush; ENDS on the hit
                                    (duration) -> into end cards / the question / any slam
 reverse_swell  1.50  1.500   -24   reversed hall bloom of a soft hit + bright air; ENDS on the hit (duration)
 downlifter     4.08  0.010   -25   falling sweep 7 kHz -> 150 Hz + descending tone + soft boom (dur) -> exits
 UI
 glitch_short   0.60  0.000   -28   tasteful micro-grain stutter, stereo scattered -> data flickers, glitch cuts
 ui_click       0.50  0.001   -29   crisp soft glassy click + low tock (pitch) -> cursor clicks, button presses
 ui_tick        0.40  0.000   -33   tiny high glassy tick (pitch) -> list items, progress ticks
 ui_hover       1.78  0.120   -35   soft airy breath + faint rising glint -> hover/focus, tile enlarge
 typing         1.36  0.002   -32   n soft laptop keys, human timing (n, cps) -> type-on text
 pop            0.60  0.002   -28   round "bloop" pop (pitch) -> chips/tags/icons popping in
 bubble_pop     0.59  0.001   -29   liquid Minnaert bubble (pitch) -> playful pops, R3 chips
 check_ding     2.67  0.002   -27   soft two-note glassy confirmation E6 -> B6 (pitch) -> checklist ticks
 toggle_on      0.56  0.001   -30   two-stage switch + rising glint -> toggles, chip selection
 toast_chime    3.02  0.002   -27   warm rounded two-tone G5 -> D6 + air lift (pitch) -> toasts, success
 glass_tap      1.84  0.001   -30   tap on a glass pane, beating glass modes (pitch) -> glass cards landing
 card_slide     0.94  0.361   -30   friction slide then soft "thup" (dur) -> carousel tiles docking
 puzzle_click   0.61  0.060   -26   satisfying plastic snap + latch + low thock -> R3 puzzle pieces
 camera_shutter 0.56  0.001   -28   mirror click, whirr, shutter close -> photo cards, freeze frames
 slider_drag    1.55  1.000   -32   detent ticks rising with the value + friction + stop click (duration,
                                    detents); hit = stop -> R2 weeks slider (align='start')
 bar_grow       2.55  0.800   -30   rising soft tonal glide + air, wooden tock at full height (duration, pitch:
                                    map bar height -> pitch); hit = end -> R2 bars, progress rings (align='start')
 MONEY
 coin_flip      2.66  0.001   -27   metallic thumb flick then spinning shimmer slowing down -> R2 coin flips
 coin_ring      3.35  0.000   -28   bright gold coin strike, beating plate modes (pitch) -> coin lands, £ figure
 coins_burst    2.42  0.001   -25   cascade of ~26 coins thinning out, wide (n) -> money bursts
 cash_kaching   3.92  0.120   -24   lever "ka", bright bell "ching" (hit), soft drawer + coins -> R2 total lands
 slot_tick      1.75  1.200   -30   n rolling-digit ticks decelerating to a landing click (n, dur, ease 'out' |
                                    'linear'); hit = landing -> R2 counters (align='start' at roll start)
 TEXTURE
 shimmer        3.07  0.020   -30   sparkling 3 - 11 kHz grain cloud + plate wash (dur) -> light sweeps, glints
 sparkle        2.01  0.002   -31   a few bright FM twinkles -> stars, badges, check icons glowing
 ripple         5.77  0.030   -30   airy circular shimmer: moving comb + rotating pan + soft pings (dur) -> R3
                                    ripple ring, iris/ring wipes
 seed_plip      1.81  0.002   -27   water-drop plip (rising chirp) + soft thud + splash -> R3 seed landing
 grow_swell     4.22  2.500   -28   organic rising swell: breathy air, woody resonances gliding up, rustle
                                    building, peaks at the end (duration) -> R3 sprout growth (align='start')
 leaf_rustle    1.64  0.300   -33   crinkly leaf grains under a soft swell (dur) -> leaves unfolding/drifting
 BED (seamless loops, tiled by mix(bed=...); normalised to integrated -20 LUFS; hit 0)
 room_tone     16.00  -        warm interior: soft low-mid air, HVAC-like body, slow breathing (dur) -> R1/R2
 night_air     20.00  -        dark airy hum: noise drone bands at 62/124 Hz (no mains tone), distant wind,
                                    faint high air (dur) -> very subtle floor for the dark reels
 outdoor_birds 24.00  -        breeze gusts + sparse synthesised birdsong (chirps, trills, two-note whistles)
                                    at various distances (dur, birds level) -> R3

EXAMPLE (reel module)
    import audio as A
    DUR, BPM = 26.0, 120
    BED, BED_GAIN_DB = 'room_tone', -30
    def cues():
        c = [dict(t=0.02, name='heartbeat', params=dict(n=1)),
             dict(t=0.45, name='reverse_swell', params=dict(duration=0.45)), dict(t=0.45, name='flash_hit')]
        c += A.on_beats('whip', BPM * 2, range(1, 9), offset=0.45 - 0.25, gain_db=-3,
                        params=dict(direction=1), pan=lambda b: 0.4 * (-1) ** b)
        c += [dict(t=2.45, name='riser', params=dict(duration=1.6)), dict(t=2.45, name='impact_big'),
              dict(t=2.45, name='sub_drop'), dict(t=21.0, name='riser', params=dict(duration=2.0)),
              dict(t=21.0, name='logo_sting'), dict(t=5.6, name='slot_tick', align='start', params=dict(n=12))]
        return c
    # python3 audio.py reel reel1   -> workspace3/audio/reel1_sfx.wav (+ _stem.wav), report printed
    rep = A.mix(cues(), DUR, 'mix.wav', 'stem.wav', bed=BED); A.mix_overview(rep, 'mix.png', 'reel1')

CLI
    python3 audio.py selftest              -> out/selftest/audio_sheet_{1,2,3}.png (spectrogram grids),
        audio_catalog.wav (every sound in sequence + the beds), audio_demo_r1.wav/.png (reel-1 style cue sheet),
        loudness report incl. an ffmpeg ebur128 cross-check
    python3 audio.py reel reel1            -> AUDIO/reel1_sfx.wav + AUDIO/reel1_sfx_stem.wav
    python3 audio.py mix cues.json 26 out.wav [stem.wav] [bed]
    python3 audio.py play riser '{"duration": 1.5}' [out.wav]   -> wav + spectrogram png
    python3 audio.py catalog               -> printed catalog
"""
import functools
import json
import math
import os
import sys
import wave
import zlib

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

# ============================================================================================ paths / constants
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import wsconf  # noqa: E402
WS = wsconf.workspace()
AUDIO = os.path.join(WS, 'audio')
OUT = os.path.join(WS, 'out')
SELFTEST = os.path.join(OUT, 'selftest')
FONTS = os.path.join(WS, 'fonts')

SR = 48000
REF_LUFS = -20.0           # a cue at level 0 / gain_db 0 peaks at this momentary loudness (400 ms, K-weighted)
PEAK_CAP_DB = -1.0         # no single rendered sound exceeds this sample peak
TWO_PI = 2.0 * np.pi


# ============================================================================================ small helpers
def _t(d):
    return np.arange(int(round(d * SR))) / SR


def _n(d):
    return int(round(d * SR))


def _rng(seed, salt):
    return np.random.default_rng([int(seed) & 0xFFFFFFFF, zlib.crc32(salt.encode()) & 0xFFFFFFFF])


def db(x):
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-12))


def undb(g):
    return 10.0 ** (np.asarray(g, dtype=np.float64) / 20.0)


def _st(x):
    """mono (N,) -> stereo (N, 2); stereo passes through."""
    x = np.asarray(x, dtype=np.float64)
    return np.stack([x, x], 1) if x.ndim == 1 else x


def _mono(x):
    x = np.asarray(x)
    return x if x.ndim == 1 else x.mean(1)


def _add(buf, sig, t0):
    """Add sig into buf starting at time t0 (s); clips at both ends. Mono into stereo is duplicated."""
    i = int(round(t0 * SR))
    if sig.ndim == 1 and buf.ndim == 2:
        sig = _st(sig)
    if i < 0:
        sig, i = sig[-i:], 0
    m = min(len(sig), len(buf) - i)
    if m > 0:
        buf[i:i + m] += sig[:m]
    return buf


def _rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-30))


def _unit(x):
    return x / (_rms(x) + 1e-12)


def _peaknorm(x, peak=1.0):
    return x * (peak / (np.max(np.abs(x)) + 1e-12))


def _smooth(env, sec):
    k = max(1, int(sec * SR))
    return uniform_filter1d(env, k, mode='nearest') if k > 1 else env


def _sat(x, drive=2.0):
    """Soft saturation (tanh) normalised so |x|<=1 maps to <=1; adds odd harmonics (phone translation)."""
    return np.tanh(drive * x) / np.tanh(drive)


def _asat(x, drive=2.0, bias=0.15):
    """Asymmetric saturation: adds even harmonics too (warmer); DC is removed by _finish."""
    y = np.tanh(drive * (x + bias)) - np.tanh(drive * bias)
    return y / (np.tanh(drive * (1 + bias)) - np.tanh(drive * bias))


# ------------------------------------------------------------------------------------------- envelopes
def _ar(t, attack, tau, t0=0.0):
    """Raised-cosine attack of `attack` s starting at t0, then exponential decay with time constant tau."""
    u = t - t0
    a = max(attack, 1e-5)
    rise = np.where(u < a, 0.5 - 0.5 * np.cos(np.pi * np.clip(u / a, 0, 1)), 1.0)
    dec = np.exp(-np.maximum(u - a, 0.0) / tau)
    return np.where(u < 0, 0.0, rise * dec)


def _swell(t, tp, k=2.0, tau=0.08, t0=0.0, smooth=0.003):
    """Power-law rise from t0 to the peak at tp, exponential decay afterwards (whoosh-like)."""
    u = np.clip((t - t0) / max(tp - t0, 1e-6), 0, None)
    e = np.where(t < tp, u ** k, np.exp(-(t - tp) / tau))
    e = np.where(t < t0, 0.0, e)
    return _smooth(e, smooth)


def _fade(x, fin=0.0004, fout=0.01):
    x = np.array(x, dtype=np.float64, copy=True)
    a, b = int(fin * SR), int(fout * SR)
    if a > 1:
        w = 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
        x[:a] *= w[:, None] if x.ndim == 2 else w
    if b > 1 and b < len(x):
        w = 0.5 + 0.5 * np.cos(np.pi * np.arange(1, b + 1) / b)
        x[-b:] *= w[:, None] if x.ndim == 2 else w
    return x


def _taper(x, frac=0.25, sec=None):
    """Raised-cosine fade over the last `frac` of x (or `sec` seconds): buffers end at exactly zero."""
    n = len(x)
    m = int(min(n * frac, sec * SR) if sec else n * frac)
    if m < 2:
        return x
    x = np.array(x, dtype=np.float64, copy=True)
    w = 0.5 + 0.5 * np.cos(np.pi * np.arange(1, m + 1) / m)
    x[-m:] *= w[:, None] if x.ndim == 2 else w
    return x


def _curve(spec, p, log=True):
    """spec: scalar | callable(p) | [(p0, v0), (p1, v1), ...] breakpoints (log-interpolated if log)."""
    p = np.asarray(p, dtype=np.float64)
    if callable(spec):
        return np.broadcast_to(np.asarray(spec(p), dtype=np.float64), p.shape).copy()
    if np.isscalar(spec):
        return np.full(p.shape, float(spec))
    pts = np.asarray(spec, dtype=np.float64)
    if log:
        return 2.0 ** np.interp(p, pts[:, 0], np.log2(pts[:, 1]))
    return np.interp(p, pts[:, 0], pts[:, 1])


# ------------------------------------------------------------------------------------------- filters
@functools.lru_cache(maxsize=512)
def _butter(kind, f, order):
    nyq = SR / 2.0
    if kind in ('bandpass', 'bandstop'):
        wn = [max(f[0], 5.0) / nyq, min(f[1], nyq * 0.97) / nyq]
    else:
        wn = min(max(f, 5.0), nyq * 0.97) / nyq
    return signal.butter(order, wn, btype=kind, output='sos')


def lp(x, f, order=2):
    return signal.sosfilt(_butter('lowpass', float(f), order), x, axis=0)


def hp(x, f, order=2):
    return signal.sosfilt(_butter('highpass', float(f), order), x, axis=0)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(_butter('bandpass', (float(lo), float(hi)), order), x, axis=0)


@functools.lru_cache(maxsize=1024)
def _rbj(kind, f, q, gain_db=0.0):
    w0 = TWO_PI * min(f, SR * 0.48) / SR
    cw, sw = math.cos(w0), math.sin(w0)
    al = sw / (2 * q)
    A = 10 ** (gain_db / 40.0)
    if kind == 'bp':
        b, a = [al, 0.0, -al], [1 + al, -2 * cw, 1 - al]
    elif kind == 'peak':
        b, a = [1 + al * A, -2 * cw, 1 - al * A], [1 + al / A, -2 * cw, 1 - al / A]
    elif kind in ('ls', 'hs'):
        sa = 2 * math.sqrt(A) * al
        if kind == 'ls':
            b = [A * ((A + 1) - (A - 1) * cw + sa), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sa)]
            a = [(A + 1) + (A - 1) * cw + sa, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sa]
        else:
            b = [A * ((A + 1) + (A - 1) * cw + sa), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sa)]
            a = [(A + 1) - (A - 1) * cw + sa, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sa]
    else:
        raise ValueError(kind)
    b, a = np.array(b), np.array(a)
    return b / a[0], a / a[0]


def reson(x, f, q=8.0):
    """Constant-peak (0 dB) resonant band-pass."""
    b, a = _rbj('bp', float(f), float(q))
    return signal.lfilter(b, a, x, axis=0)


def eq(x, kind, f, q=0.7, gain_db=0.0):
    """RBJ biquad EQ: kind 'peak' | 'ls' (low shelf) | 'hs' (high shelf)."""
    b, a = _rbj(kind, float(f), float(q), float(gain_db))
    return signal.lfilter(b, a, x, axis=0)


# ------------------------------------------------------------------------------------------- STFT tools
_NFFT, _HOP = 1024, 256


@functools.lru_cache(maxsize=8)
def _win(n):
    return 0.5 - 0.5 * np.cos(TWO_PI * np.arange(n) / n)       # periodic Hann


def _stft(x, n=_NFFT, hop=_HOP):
    """Centred STFT: frame k is centred on sample k*hop. Returns (T, n//2+1) complex."""
    pad = n // 2
    T = len(x) // hop + 1
    xp = np.pad(x, (pad, pad + n + hop))
    idx = hop * np.arange(T)[:, None] + np.arange(n)[None, :]
    return np.fft.rfft(xp[idx] * _win(n), axis=1)


def _istft(S, length, n=_NFFT, hop=_HOP):
    w = _win(n)
    fr = np.fft.irfft(S, n=n, axis=1) * w
    T = fr.shape[0]
    tot = (T + n // hop + 1) * hop + n
    out = np.zeros(tot)
    ws = np.zeros(tot)
    r = n // hop
    for k in range(r):
        blk = fr[k::r]
        if len(blk) == 0:
            continue
        o = k * hop
        out[o:o + blk.size] += blk.reshape(-1)
        ws[o:o + blk.size] += np.tile(w * w, len(blk))
    pad = n // 2
    out, ws = out[pad:pad + length], ws[pad:pad + length]
    return out / np.maximum(ws, 1e-3)


def _frame_p(T, d, hop=_HOP):
    return np.clip(np.arange(T) * hop / SR / max(d, 1e-9), 0, 1)


def _band_mask(freqs, fc, bw, energy_norm=True):
    """Gaussian band in log-frequency: fc (T,), bw octaves (T,) -> (T, F)."""
    lf = np.log2(np.maximum(freqs, 8.0))[None, :]
    m = np.exp(-0.5 * ((lf - np.log2(fc)[:, None]) / np.maximum(bw, 0.03)[:, None]) ** 2)
    if energy_norm:
        m /= np.sqrt(np.mean(m * m, axis=1, keepdims=True)) + 1e-12
    return m


def _stereo_white(N, rng, width):
    """White noise pair whose L/R correlation falls as width (scalar or (N,) array 0..1) rises."""
    w0 = rng.standard_normal(N)
    if np.isscalar(width) and width <= 0:
        return w0[:, None]
    a = np.asarray(width, dtype=np.float64) * (np.pi / 2) * 0.5
    wl, wr = rng.standard_normal(N), rng.standard_normal(N)
    return np.stack([np.cos(a) * w0 + np.sin(a) * wl, np.cos(a) * w0 + np.sin(a) * wr], 1)


def noise_band(d, rng, fc, bw=1.0, width=0.0, comb=None, tilt=0.0, extra=None, n=_NFFT, hop=_HOP):
    """Noise through a time-varying Gaussian (log-frequency) band-pass, built in the STFT domain.
    fc: Hz curve, bw: octaves (std) curve; both scalar | callable(p) | [(p, v), ...] with p = t/d in 0..1.
    width: stereo decorrelation 0..1 (scalar or curve; 0 -> mono (N,)). comb=(tau_curve_s, depth): moving
    comb (flanger/jet) notches. tilt: dB/octave around 1 kHz. extra: callable(p (T,), f (F,)) -> (T, F) gain.
    Output has ~unit RMS (per-frame energy normalised) so the caller's envelope sets the level."""
    N = _n(d)
    wcurve = None if (np.isscalar(width) and width <= 0) else _curve(width, np.arange(N) / max(N, 1), log=False)
    wn = _stereo_white(N, rng, 0.0 if wcurve is None else wcurve)
    T = N // hop + 1
    p = _frame_p(T, d, hop)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    m = _band_mask(f, _curve(fc, p), _curve(bw, p, log=False), energy_norm=False)
    if tilt:
        m *= (np.maximum(f, 20.0) / 1000.0) ** (tilt / 6.02)
    if comb is not None:
        tau = _curve(comb[0], p, log=True)
        m *= (1.0 - comb[1] / 2) + (comb[1] / 2) * np.cos(TWO_PI * f[None, :] * tau[:, None])
    if extra is not None:
        m *= extra(p, f)
    m /= np.sqrt(np.mean(m * m, axis=1, keepdims=True)) + 1e-12
    out = np.stack([_istft(_stft(wn[:, c], n, hop) * m, N, n, hop) for c in range(wn.shape[1])], 1)
    return out[:, 0] if out.shape[1] == 1 else out


def colored(N, rng, slope_db_oct=-3.0, lo=20.0, hi=20000.0):
    """Coloured noise by spectral shaping (pink = -3, brown = -6 dB/oct), unit RMS. Circular (loopable)."""
    X = np.fft.rfft(rng.standard_normal(N))
    f = np.fft.rfftfreq(N, 1.0 / SR)
    g = (np.maximum(f, lo) / 1000.0) ** (slope_db_oct / 6.02)
    g *= 1.0 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4) / np.sqrt(1 + (f / hi) ** 4)
    return _unit(np.fft.irfft(X * g, n=N))


# ------------------------------------------------------------------------------------------- oscillators
def osc(f, phase=0.0):
    """Sine with a (possibly time-varying) frequency array (Hz) via phase accumulation."""
    return np.sin(phase + TWO_PI * np.cumsum(f) / SR)


def modal(d, freqs, taus, amps, rng=None, split=0.0, contact=0.0004, t0=0.0, split_mix=0.4, rand_phase=False):
    """Modal resonator bank: sum of exponentially decaying sines (struck glass, metal, plastic). Modes start
    at zero phase (velocity excitation: no onset step) unless rand_phase.
    split (Hz): each mode becomes a doublet split by ~split (slow partial beating, like real coins and bells);
    split_mix = level of the second component (0.4 -> about +-40 % beating depth, never a full tremolo).
    contact: raised-cosine onset of the mallet/contact time (softer = longer = duller)."""
    t = _t(d)
    u = np.maximum(t - t0, 0.0)
    fr = np.asarray(freqs, dtype=np.float64)
    tau = np.asarray(taus, dtype=np.float64)
    am = np.asarray(amps, dtype=np.float64)
    keep = fr < SR * 0.45
    fr, tau, am = fr[keep], tau[keep], am[keep]
    ph = rng.uniform(0, TWO_PI, len(fr)) if (rng is not None and rand_phase) else np.zeros(len(fr))
    x = np.zeros(len(t))
    for f, ta, a, p0 in zip(fr, tau, am, ph):
        e = np.exp(-u / ta)
        if split:
            s = split * (0.6 + 0.8 * (rng.random() if rng is not None else 0.5))
            x += a * e * (np.sin(TWO_PI * f * u + p0) + split_mix * np.sin(TWO_PI * (f + s) * u + p0)) / (1 + split_mix)
        else:
            x += a * e * np.sin(TWO_PI * f * u + p0)
    on = _ar(t, contact, 1e9, t0)
    return _taper(x * on, 0.3)


def fm_bell(d, fc, ratio=1.4, index=2.0, tau=1.0, tau_index=0.25, attack=0.002, t0=0.0):
    """Two-operator FM: carrier fc, modulator fc*ratio, index decaying with tau_index (bright -> pure)."""
    t = _t(d)
    u = np.maximum(t - t0, 0.0)
    I = index * np.exp(-u / tau_index)
    y = np.sin(TWO_PI * fc * u + I * np.sin(TWO_PI * fc * ratio * u))
    return _taper(y * _ar(t, attack, tau, t0), 0.25)


# ------------------------------------------------------------------------------------------- stereo
def pan(x, p):
    """Equal-power pan (mono) / balance (stereo). p in [-1, 1], scalar or per-sample array; centre = unity."""
    x = _st(x)
    th = (np.clip(np.asarray(p, dtype=np.float64), -1, 1) + 1) * (np.pi / 4)
    gl, gr = np.sqrt(2) * np.cos(th), np.sqrt(2) * np.sin(th)
    return np.stack([x[:, 0] * gl, x[:, 1] * gr], 1)


def width(x, w):
    """Mid/side width: 0 mono, 1 unchanged, >1 wider."""
    x = _st(x)
    m, s = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2 * w
    return np.stack([m + s, m - s], 1)


def decorrelate(x, rng, amount=0.5, ms=12.0):
    """Mono/stereo -> wider stereo by convolving each side with a short, different, decaying-noise filter."""
    x = _st(x)
    L = max(16, int(ms / 1000 * SR))
    e = np.exp(-np.arange(L) / (L / 4.0))
    out = np.empty_like(x)
    for c in range(2):
        h = rng.standard_normal(L) * e
        h /= np.sqrt(np.sum(h * h))
        wet = signal.fftconvolve(x[:, c], h)[:len(x)]
        out[:, c] = x[:, c] * math.sqrt(1 - amount * 0.5) + wet * math.sqrt(amount * 0.5) * (1 if c == 0 else -1)
    return out


def bass_enhance(x, amount=0.8, fc=110.0, band=(120.0, 650.0), drive=3.5):
    """Psychoacoustic bass (phone-speaker translation): harmonics of the sub band (< fc) generated by
    asymmetric saturation, band-limited to `band` and mixed in, so small speakers imply the missing
    fundamental. Harmonics track the sub envelope (they fade with it)."""
    lo = lp(lp(x, fc, 2), fc, 2)
    env = np.abs(signal.hilbert(lo, axis=0))
    env = lp(env, 40.0, 2)
    floor = np.max(env) * 1e-3
    u = np.clip(lo / np.maximum(env, floor), -1.5, 1.5)          # ~unit-amplitude sub waveform
    h = _asat(u, drive, 0.25) * env                             # fixed harmonic spectrum, linear in level
    h = bp(h - np.mean(h, axis=0), band[0], band[1], 2)
    h = lp(h, band[1], 2)
    return x + amount * h


# ------------------------------------------------------------------------------------------- dynamics bits
def transient(x, amount_db=4.0, fast=0.0015, slow=0.04):
    """Transient shaper: boosts onsets (amount_db > 0) or softens them (< 0)."""
    x = _st(x)
    a = np.abs(x).max(1)
    cf, cs = math.exp(-1 / (fast * SR)), math.exp(-1 / (slow * SR))
    ef = signal.lfilter([1 - cf], [1, -cf], a)
    es = signal.lfilter([1 - cs], [1, -cs], a)
    r = np.clip(np.log2((ef + 1e-9) / (es + 1e-9)), 0, 1.5) / 1.5
    g = undb(amount_db * _smooth(r, 0.001))
    return x * g[:, None]


# ============================================================================================ loudness (BS.1770-4)
_K_SHELF = (np.array([1.53512485958697, -2.69169618940638, 1.19839281085285]),
            np.array([1.0, -1.69065929318241, 0.73248077421585]))
_K_RLB = (np.array([1.0, -2.0, 1.0]), np.array([1.0, -1.99004745483398, 0.99007225036621]))


def kweight(x):
    """ITU-R BS.1770 K-weighting (48 kHz coefficients from the standard)."""
    y = signal.lfilter(*_K_SHELF, x, axis=0)
    return signal.lfilter(*_K_RLB, y, axis=0)


def _block_powers(x, win=0.4, hop=0.1):
    z = kweight(_st(x))
    p = np.square(z).sum(1)
    c = np.concatenate([[0.0], np.cumsum(p)])
    nw, nh = int(win * SR), int(hop * SR)
    if len(p) < nw:
        return np.array([c[-1] / nw])
    starts = np.arange(0, len(p) - nw + 1, nh)
    return (c[starts + nw] - c[starts]) / nw


def loudness(x):
    """Integrated loudness (LUFS), BS.1770-4: 400 ms blocks, 75 % overlap, -70 LUFS absolute and -10 LU
    relative gates."""
    pw = _block_powers(x)
    lk = -0.691 + 10 * np.log10(pw + 1e-30)
    g1 = pw[lk > -70.0]
    if len(g1) == 0:
        return -120.0
    rel = -0.691 + 10 * np.log10(np.mean(g1)) - 10.0
    g2 = pw[(lk > -70.0) & (lk > rel)]
    return float(-0.691 + 10 * np.log10(np.mean(g2) + 1e-30))


def momentary_max(x, win=0.4):
    """Maximum momentary loudness (LUFS over a sliding `win` window). Short sounds are zero-padded."""
    z = kweight(np.pad(_st(x), ((int(win * SR), int(win * SR)), (0, 0))))
    p = np.square(z).sum(1)
    c = np.concatenate([[0.0], np.cumsum(p)])
    nw = int(win * SR)
    st = np.arange(0, len(p) - nw + 1, max(1, int(0.005 * SR)))
    return float(-0.691 + 10 * np.log10(np.max((c[st + nw] - c[st]) / nw) + 1e-30))


def loudness_curve(x, win=0.4, hop=0.05):
    """(times, LUFS) momentary loudness curve (window centred)."""
    pw = _block_powers(x, win, hop)
    tt = np.arange(len(pw)) * hop + win / 2
    return tt, -0.691 + 10 * np.log10(pw + 1e-30)


def loudness_range(x):
    """EBU R128 LRA (LU): 3 s short-term blocks, 10th..95th percentile after gating."""
    pw = _block_powers(x, 3.0, 0.1)
    lk = -0.691 + 10 * np.log10(pw + 1e-30)
    g = pw[lk > -70]
    if len(g) < 2:
        return 0.0
    rel = -0.691 + 10 * np.log10(np.mean(g)) - 20
    l2 = lk[(lk > -70) & (lk > rel)]
    return float(np.percentile(l2, 95) - np.percentile(l2, 10)) if len(l2) > 1 else 0.0


def true_peak(x):
    """True peak (dBTP) with 4x polyphase oversampling."""
    x = _st(x)
    y = signal.resample_poly(x, 4, 1, axis=0)
    return float(db(max(np.max(np.abs(y)), np.max(np.abs(x)))))


def stats(x, hit=None):
    """Objective QC numbers for a sound or mix."""
    x = _st(x)
    pk = np.max(np.abs(x))
    a = np.abs(x).max(1)
    act = a > pk * 10 ** (-40 / 20)
    rms_act = _rms(x[act]) if act.any() else 1e-12
    d0 = max(np.max(np.abs(x[0])), np.max(np.abs(np.diff(x[:4], axis=0)))) / (pk + 1e-12)
    d1 = max(np.max(np.abs(x[-1])), np.max(np.abs(np.diff(x[-4:], axis=0)))) / (pk + 1e-12)
    env = _smooth(a, 0.004)
    out = dict(dur=len(x) / SR, peak_db=float(db(pk)), rms_db=float(db(_rms(x))), rms_active_db=float(db(rms_act)),
               crest_db=float(db(pk) - db(rms_act)), mmax_lufs=momentary_max(x), dc=float(np.abs(x.mean(0)).max()),
               edge_start=float(d0), edge_end=float(d1), env_peak_t=float(np.argmax(env) / SR),
               corr=float(np.corrcoef(x[:, 0], x[:, 1])[0, 1]) if np.std(x[:, 0]) > 0 and np.std(x[:, 1]) > 0 else 1.0)
    if hit is not None:
        out['hit'] = float(hit)
    return out


# ============================================================================================ reverb
REVERBS = {
    # name: rt60 (s), predelay (s), damp (Hz, HF decays faster above), er (early reflection level),
    #       lo_cut (Hz high-pass on the IR), width (stereo), density build-up (s)
    'room':   dict(rt60=0.55, predelay=0.006, damp=6500.0, er=0.55, lo_cut=150.0, width=1.0, build=0.008),
    'studio': dict(rt60=0.95, predelay=0.014, damp=7000.0, er=0.40, lo_cut=180.0, width=1.0, build=0.015),
    'dark':   dict(rt60=0.9, predelay=0.010, damp=1800.0, er=0.40, lo_cut=60.0, width=0.8, build=0.012),
    'plate':  dict(rt60=1.7, predelay=0.016, damp=11000.0, er=0.10, lo_cut=250.0, width=1.0, build=0.004),
    'hall':   dict(rt60=2.6, predelay=0.024, damp=4800.0, er=0.35, lo_cut=110.0, width=1.0, build=0.03),
    'air':    dict(rt60=4.6, predelay=0.035, damp=7500.0, er=0.15, lo_cut=200.0, width=1.0, build=0.06),
    'outdoor': dict(rt60=1.1, predelay=0.030, damp=3800.0, er=0.25, lo_cut=200.0, width=1.0, build=0.05),
}


@functools.lru_cache(maxsize=16)
def make_ir(rt60=1.2, predelay=0.012, damp=6000.0, er=0.4, lo_cut=120.0, width=1.0, build=0.02, seed=7):
    """Generated stereo convolution IR (wet only): sparse early reflections + exponentially decaying
    noise tail whose high frequencies decay faster (rt60(f) = rt60 / sqrt(1 + (f/damp)^2)); L and R
    use different noise (decorrelated). Unit energy per channel. Returns read-only (N, 2) float64."""
    rng = _rng(seed, 'ir%.3f' % rt60)
    L = _n(predelay + min(rt60 * 1.15, 7.0))
    f = np.fft.rfftfreq(_NFFT, 1.0 / SR)
    rtf = rt60 / np.sqrt(1 + (f / damp) ** 2)
    rtf = np.where(f < 200, rtf * 1.08, rtf)
    T = L // _HOP + 1
    tf = np.arange(T) * _HOP / SR - predelay
    env = np.exp(-6.91 * np.maximum(tf, 0)[:, None] / rtf[None, :])
    env *= (1 - np.exp(-np.maximum(tf, 0) / max(build, 1e-3)))[:, None] * (tf >= 0)[:, None]
    ir = np.zeros((L, 2))
    for c in range(2):
        tail = _istft(_stft(rng.standard_normal(L)) * env, L)
        tail /= np.sqrt(np.sum(tail ** 2)) + 1e-12
        e = np.zeros(L)
        nt = 18
        times = predelay * 0.45 + np.sort(rng.uniform(0.0015, 0.07, nt))
        for k, tt in enumerate(times):
            i = int(tt * SR)
            if i < L:
                e[i] += rng.choice([-1, 1]) * rng.uniform(0.45, 1.0) * math.exp(-(tt - times[0]) / 0.035)
        e = lp(e, min(damp * 1.6, 16000), 1)
        if np.any(e):
            e *= er / (np.sqrt(np.sum(e ** 2)) + 1e-12)
        ir[:, c] = tail + e
    ir = hp(ir, lo_cut, 2)
    if width != 1.0:
        ir = width_fn(ir, width)
    ir = _fade(ir, 0.0, min(0.25, rt60 * 0.2))
    ir /= np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True)) + 1e-12
    ir.setflags(write=False)
    return ir


width_fn = width


def reverb(x, preset='room', wet_db=-12.0, dry=1.0, send_hp=None, **kw):
    """Convolution reverb with a generated IR (see REVERBS / make_ir). Returns stereo of length
    len(x) + len(ir) - 1 (the tail is kept). wet_db: wet level relative to dry for a sustained signal."""
    x = _st(x)
    prm = dict(REVERBS[preset]) if isinstance(preset, str) else {}
    prm.update(kw)
    ir = make_ir(**prm)
    x = _fade(x, 0.0, 0.004)
    src = hp(x, send_hp) if send_hp else x
    out = np.zeros((len(x) + len(ir) - 1, 2))
    out[:len(x)] = x * dry
    g = undb(wet_db)
    m = (src[:, 0] + src[:, 1]) * 0.5
    for c in range(2):
        out[:, c] += g * signal.fftconvolve(0.75 * src[:, c] + 0.25 * m, ir[:, c])
    return out


def reverb_circular(x, preset='room', wet_db=-12.0, **kw):
    """Loop-safe reverb: circular convolution (the tail wraps to the start; the loop stays seamless)."""
    x = _st(x)
    prm = dict(REVERBS[preset])
    prm.update(kw)
    ir = make_ir(**prm)
    N = len(x)
    out = x.copy()
    g = undb(wet_db)
    for c in range(2):
        h = np.zeros(N)
        m = min(N, len(ir))
        h[:m] = ir[:m, c]
        out[:, c] += g * np.fft.irfft(np.fft.rfft(x[:, c]) * np.fft.rfft(h), n=N)
    return out


# ============================================================================================ Sfx container
class Sfx(np.ndarray):
    """float32 (N, 2) stereo array at 48 kHz carrying .hit (seconds from the start to the designed hit/peak)
    and .name. Behaves exactly like an ndarray otherwise."""

    def __new__(cls, arr, hit=0.0, name=''):
        obj = np.asarray(arr, dtype=np.float32).view(cls)
        obj.hit = float(hit)
        obj.name = name
        return obj

    def __array_finalize__(self, obj):
        self.hit = getattr(obj, 'hit', 0.0)
        self.name = getattr(obj, 'name', '')

    @property
    def dur(self):
        return self.shape[0] / SR


def _finish(x, hit, level, name, fin=0.0004, fout=0.012, trim=True, hp_hz=18.0, keep_until=None):
    """Common finishing: stereo, DC/subsonic high-pass, trailing-silence trim, click-free edge fades,
    loudness calibration (max momentary = REF_LUFS + level) with a sample-peak cap."""
    x = _st(np.nan_to_num(np.asarray(x, dtype=np.float64)))
    x = hp(x, hp_hz, 2)
    if trim:
        a = np.abs(x).max(1)
        pk = a.max() + 1e-12
        idx = np.nonzero(a > pk * 10 ** (-78 / 20))[0]
        last = idx[-1] if len(idx) else len(x) - 1
        lo = int(((keep_until if keep_until is not None else hit) + 0.03) * SR)
        x = x[:min(len(x), max(last + int(0.012 * SR), lo))]
    x = _fade(x, fin, fout)
    g = undb(REF_LUFS + level - momentary_max(x))
    pk = np.max(np.abs(x)) * g
    if pk > undb(PEAK_CAP_DB):
        g *= undb(PEAK_CAP_DB) / pk
    return Sfx(x * g, hit, name)


# ============================================================================================ building blocks
def _thump(d, f_end, f_drop, tau_pitch, tau, rng, attack=0.003, drive=2.0, noise=0.35, noise_lp=300.0,
           click=0.0, click_band=(600.0, 3000.0)):
    """Pitched body thump (kick-drum-like sine sweep, saturated for phone-speaker harmonics) + noise body
    + optional contact click. Mono, peak ~1."""
    t = _t(d)
    f = f_end + f_drop * np.exp(-t / tau_pitch)
    body = _sat(osc(f) * _ar(t, attack, tau), drive)
    nz = _unit(lp(rng.standard_normal(len(t)), noise_lp, 2)) * _ar(t, attack * 0.7, tau * 0.45) * 0.3
    x = body + noise * nz
    if click:
        x += click * _unit(bp(rng.standard_normal(len(t)), *click_band)) * _ar(t, 0.0003, 0.004) * 0.25
    return _taper(x, 0.15)


def _click(d, rng, band=(2000.0, 9000.0), tau=0.002, modes=None, low=None):
    """Crisp UI click: band-passed noise transient + optional modal body (list of (f, tau, amp)) + low tock."""
    t = _t(d)
    x = _unit(bp(rng.standard_normal(len(t)), *band)) * _ar(t, 0.0002, tau) * 0.35
    if modes:
        fr, ta, am = zip(*modes)
        x += modal(d, fr, ta, am, rng, contact=0.0003)
    if low:
        x += low[2] * osc(np.full(len(t), low[0])) * _ar(t, 0.0006, low[1])
    return x


def _grains(d, rng, n, f_lo, f_hi, g_lo=0.02, g_hi=0.12, density=None, amp=None, decay=True, spread=0.9,
            harm=0.0):
    """Cloud of short sine grains (sparkle/shimmer). density(p) -> relative probability over time.
    Returns stereo."""
    N = _n(d)
    out = np.zeros((N, 2))
    pp = np.linspace(0, 1, 512)
    w = density(pp) if density is not None else np.ones_like(pp)
    cdf = np.cumsum(w)
    cdf /= cdf[-1]
    for k in range(n):
        t0 = np.interp(rng.random(), cdf, pp) * d
        f = math.exp(rng.uniform(math.log(f_lo), math.log(f_hi)))
        gl = rng.uniform(g_lo, g_hi)
        tt = _t(gl * (4.0 if decay else 1.0))
        if decay:
            e = _ar(tt, min(0.004, gl * 0.1), gl)
        else:
            e = np.sin(np.pi * np.clip(tt / gl, 0, 1)) ** 2
        s = np.sin(TWO_PI * f * tt + rng.uniform(0, TWO_PI))
        if harm:
            s += harm * np.sin(TWO_PI * f * 2.01 * tt)
        a = amp(t0 / d) if amp is not None else 1.0
        g = _taper(s * e * a * rng.uniform(0.35, 1.0), 0.35)
        _add(out, pan(g, rng.uniform(-spread, spread)), t0)
    return out


def _crackle(d, rng, rate, lo=2500.0, hi=11000.0, env=None, gdur=(0.0008, 0.005), spread=0.8):
    """Leaf/paper crinkle: many tiny band-passed noise grains. rate = grains per second (peak), env(p)."""
    N = _n(d)
    out = np.zeros((N, 2))
    nz = bp(rng.standard_normal(N + SR), lo, hi, 2)
    pp = np.linspace(0, 1, 512)
    w = env(pp) if env is not None else np.ones_like(pp)
    cdf = np.cumsum(w) / np.sum(w)
    count = int(rate * d * np.mean(w))
    for k in range(count):
        t0 = np.interp(rng.random(), cdf, pp) * d
        gl = rng.uniform(*gdur)
        tt = _t(gl * 2.5)
        e = _ar(tt, gl * 0.15, gl * 0.5)
        i = rng.integers(0, SR)
        g = _taper(nz[i:i + len(tt)] * e * rng.lognormal(0, 0.6), 0.3)
        _add(out, pan(g, rng.uniform(-spread, spread)), t0)
    return out


# ============================================================================================ THE LIBRARY
# Each public sound: f(**params, seed=0) -> Sfx (float32 (N, 2), .hit seconds). Registered in SOUNDS with
# metadata (category, level, character, use) used by the mixer, the catalog and the self-test.
SOUNDS = {}


def _register(category, character, use, send=None):
    def deco(fn):
        SOUNDS[fn.__name__] = dict(fn=fn, category=category, character=character, use=use, send=send)
        return fn
    return deco


# ------------------------------------------------------------------------------------------- hits / body
@_register('impact', 'two-part lub-dub, muffled sub thump with felt click; saturated so it reads on phones',
           'cold opens, emotional beats (R1 0.0 s)')
def heartbeat(n=2, bpm=62.0, seed=0):
    """Heartbeat: n lub-dub beats at bpm. hit = first 'lub' (0.006 s)."""
    r = _rng(seed, 'heartbeat')
    period = 60.0 / bpm
    gap = 0.29 * math.sqrt(62.0 / bpm)
    d = (n - 1) * period + gap + 0.9
    x = np.zeros(_n(d))
    for k in range(n):
        for off, amp, fe in ((0.0, 1.0, 46.0), (gap, 0.62, 54.0)):
            th = _thump(0.5, fe * r.uniform(0.97, 1.03), 42.0, 0.022, 0.075, r, attack=0.004, drive=2.6,
                        noise=0.55, noise_lp=220.0, click=0.18, click_band=(250.0, 1100.0))
            _add(x, th * amp * r.uniform(0.94, 1.0), k * period + off + 0.002)
    x = bass_enhance(x, 1.8, fc=120.0, band=(170.0, 600.0), drive=7.0)
    x = lp(x, 1100, 2)
    st = reverb(x, 'dark', wet_db=-15)
    return _finish(st, 0.006, -3.0, 'heartbeat')


@_register('impact', 'deep cinematic boom: 34 Hz sub sweep, kick punch, crack, hall bloom, rumble tail',
           'the big question slam, title slams, logo lands (pair with riser / reverse_swell)', send=-24)
def impact_big(seed=0, tail=1.0):
    """Big cinematic impact with a long tail (~5 s). hit = 0.003 s. tail scales the rumble/reverb tail."""
    r = _rng(seed, 'impact_big')
    d = 5.0
    t = _t(d)
    sub = _sat(osc(33.0 + 78.0 * np.exp(-t / 0.055)) * _ar(t, 0.002, 1.05 * tail), 1.7)
    punch = _sat(osc(58.0 + 140.0 * np.exp(-t / 0.018)) * _ar(t, 0.0012, 0.17), 2.8)
    body = _unit(lp(colored(len(t), r, -6.0), 520, 2)) * _ar(t, 0.001, 0.085)
    thoom = _unit(reson(r.standard_normal(len(t)), 120.0, 2.5)) * _ar(t, 0.003, 0.32)
    crack = _unit(bp(r.standard_normal(len(t)), 1400, 7500)) * _ar(t, 0.0002, 0.011)
    tick = _unit(hp(r.standard_normal(len(t)), 5000)) * _ar(t, 0.0001, 0.0025)
    air = noise_band(d, r, [(0, 2600), (0.15, 900), (1, 500)], bw=1.4, width=0.9) * _ar(t, 0.004, 0.45)[:, None]
    rum = noise_band(d, r, [(0, 140), (1, 80)], bw=1.1, width=0.7)
    am = 1 + 0.25 * np.sin(TWO_PI * 1.3 * t + 1.0) * np.sin(TWO_PI * 0.55 * t)
    rum = rum * (_ar(t, 0.06, 1.25 * tail) * am)[:, None]
    mono = 0.95 * sub + 0.55 * punch + 0.30 * body + 0.22 * thoom + 0.20 * crack + 0.08 * tick
    mono = bass_enhance(mono, 0.9, fc=100.0, band=(170.0, 800.0), drive=7.0)
    st = _st(mono) + 0.08 * air + 0.16 * rum
    st = _taper(transient(st, 3.0), sec=1.6)
    wet = reverb(lp(hp(st, 140), 5500, 2) * 0.9, 'hall', wet_db=-3.0 + 2 * (tail - 1), dry=0.0)
    out = np.zeros((len(wet), 2))
    out[:len(st)] += st
    out += wet
    return _finish(out, 0.003, 4.0, 'impact_big')


@_register('impact', 'gentle felt thump with soft air puff and short room', 'soft landings, card settles, UI scene '
           'changes, R3 hits', send=-18)
def impact_soft(seed=0):
    """Soft impact (~1.5 s). hit = 0.006 s."""
    r = _rng(seed, 'impact_soft')
    d = 1.6
    t = _t(d)
    th = _thump(d, 62.0, 48.0, 0.03, 0.12, r, attack=0.006, drive=2.0, noise=0.45, noise_lp=500.0)
    felt = _unit(bp(r.standard_normal(len(t)), 180, 900)) * _ar(t, 0.003, 0.035) * 0.25
    puff = noise_band(d, r, [(0, 1600), (1, 700)], bw=1.2, width=0.6) * _ar(t, 0.006, 0.07)[:, None] * 0.12
    st = _st(bass_enhance(th, 1.1, fc=110.0, band=(170.0, 700.0), drive=6.0) + felt) + puff
    st = reverb(st, 'studio', wet_db=-11, send_hp=150)
    return _finish(st, 0.006, -3.0, 'impact_soft')


@_register('impact', 'long sub pitch-drop 90 -> 28 Hz with harmonic edge (audible on phones) and air puff',
           'under the question smash-cut, before end cards', send=-30)
def sub_drop(seed=0, dur=2.4):
    """Sub drop (~dur s). hit = 0.01 s."""
    r = _rng(seed, 'sub_drop')
    t = _t(dur)
    f = 28.0 + 64.0 * np.exp(-t / 0.42)
    env = _ar(t, 0.008, 0.75 * dur / 2.4) * (1 - _ar(t, 0.0, 1e9, dur - 0.25) * np.clip((t - dur + 0.25) / 0.25, 0, 1))
    s = osc(f) * env
    x = 0.85 * _sat(s, 2.2) + 0.25 * _asat(s, 3.0, 0.2)
    x = bass_enhance(x, 1.3, fc=100.0, band=(150.0, 600.0), drive=8.0)
    puff = _unit(lp(r.standard_normal(len(t)), 380, 2)) * _ar(t, 0.003, 0.05) * 0.18
    st = _st(x + puff)
    return _finish(st, 0.01, -2.0, 'sub_drop')


@_register('impact', 'reverse hiss suck into a bright crack, thump, metallic zing and plate bloom',
           'flash frames / montage cuts (R1 hook every beat)', send=-20)
def flash_hit(seed=0):
    """Flash hit (~1.8 s): 0.10 s reverse suck then the hit. hit = 0.10 s."""
    r = _rng(seed, 'flash_hit')
    pre, d = 0.10, 1.8
    t = _t(d)
    suck_env = np.where(t < pre, (t / pre) ** 3, np.exp(-(t - pre) / 0.004))
    suck = noise_band(d, r, [(0, 2500), (pre / d, 9000), (1, 9000)], bw=1.0, width=0.6) * suck_env[:, None] * 0.35
    crack = _unit(hp(r.standard_normal(len(t)), 1300)) * _ar(t, 0.0002, 0.007, pre) * 0.55
    th = np.zeros(len(t))
    _add(th, _thump(1.0, 52.0, 110.0, 0.018, 0.10, r, attack=0.0015, drive=2.6, noise=0.4), pre)
    zing = modal(d, [2310, 3720, 5130, 7940, 9620], [0.30, 0.20, 0.14, 0.09, 0.06], [1, 0.7, 0.5, 0.3, 0.2],
                 r, split=3.0, t0=pre) * 0.10
    fssh = noise_band(d, r, [(0, 5200), (pre / d, 4800), (0.5, 1400), (1, 1000)], bw=1.2, width=0.9)
    fssh = fssh * _ar(t, 0.002, 0.2, pre)[:, None] * 0.22
    st = suck + _st(0.75 * th + crack + zing) + fssh
    st = reverb(st, 'plate', wet_db=-10, send_hp=300)
    return _finish(st, pre, 1.0, 'flash_hit')


@_register('impact', 'soft impact + airy reverse swell intro + shimmer + warm bell bloom + 4.6 s air tail',
           'logo resolve on the end card (all reels)', send=-30)
def logo_sting(seed=0, tone=1.0):
    """Logo sting (~6 s). 0.42 s airy swell, then the hit. hit = 0.42 s. tone scales the bell pitch."""
    r = _rng(seed, 'logo_sting')
    pre, d = 0.42, 8.0
    t = _t(d)
    sw_env = np.where(t < pre, (t / pre) ** 2.4, np.exp(-(t - pre) / 0.05))
    swell = noise_band(d, r, [(0, 900), (pre / d, 6000), (1, 6000)], bw=1.1, width=0.8) * sw_env[:, None] * 0.3
    th = np.zeros(len(t))
    _add(th, bass_enhance(_thump(2.5, 40.0, 60.0, 0.04, 0.45, r, attack=0.005, drive=1.6, noise=0.35,
                                 noise_lp=400), 0.7), pre)
    # bell bloom: warm consonant partial set (single stinger, not a chord pad) with slow bloom and chorus
    f0 = 523.25 * tone
    parts = [(0.5, 0.35, 2.4), (1.0, 1.0, 2.2), (2.0, 0.42, 1.6), (2.76, 0.16, 1.1), (3.0, 0.20, 1.2),
             (4.07, 0.08, 0.7), (5.40, 0.05, 0.5)]
    bell = np.zeros((len(t), 2))
    u = np.maximum(t - pre, 0)
    for ratio, amp, tau in parts:
        for v, det in enumerate((-0.0016, 0.0, 0.0019)):
            f = f0 * ratio * (1 + det)
            ph = r.uniform(0, TWO_PI)
            drift = 1 + 0.0007 * np.sin(TWO_PI * r.uniform(0.2, 0.5) * t)
            s = np.sin(ph + TWO_PI * np.cumsum(np.full(len(t), f) * drift) / SR)
            e = (1 - np.exp(-u / 0.09)) * np.exp(-u / tau) * (t >= pre)
            _add(bell, pan(s * e * amp / 3, (v - 1) * 0.55), 0.0)
    strike = modal(d, [f0 * 2, f0 * 2.76, f0 * 5.4], [0.25, 0.15, 0.08], [0.3, 0.2, 0.1], r, t0=pre) * 0.5
    shim = _grains(d, r, 70, 2800, 10000, 0.03, 0.22, density=lambda p: np.exp(-np.maximum(p - pre / d, 0) * 6)
                   * (p >= pre / d * 0.9), spread=0.95) * 0.11
    st = _taper(swell + _st(0.85 * th + strike) + 0.30 * bell + shim, sec=2.5)
    st = reverb(st, 'air', wet_db=-6, send_hp=200)
    return _finish(st, pre, 0.0, 'logo_sting')


# ------------------------------------------------------------------------------------------- whooshes
def _whoosh(d, hit, r, fc, bw, k_rise, tau, pan_from, pan_to, body=0.35, body_fc=(160, 380), hiss=0.18,
            width=0.5, zip_amp=0.0, zip_f=(380, 1500), comb=None, verb=('room', -16)):
    t = _t(d)
    ph = hit / d
    env = _swell(t, hit, k_rise, tau)
    air = noise_band(d, r, fc, bw, width=width, comb=comb) * env[:, None]
    bfc = [(0, body_fc[0]), (ph, body_fc[1]), (1, body_fc[0])]
    lo = noise_band(d, r, bfc, 0.8, width=0.3) * _swell(t, hit, k_rise * 0.8, tau * 1.4)[:, None] * body
    hs = noise_band(d, r, [(0, 6000), (ph, 9500), (1, 7000)], 0.6, width=0.9)
    hs = hs * (_swell(t, hit, k_rise * 1.6, tau * 0.6) ** 1.5)[:, None] * hiss
    st = air + lo + hs
    if zip_amp:
        u = np.clip((t - (hit - 0.12)) / 0.16, 0, 1)
        fz = zip_f[0] * (zip_f[1] / zip_f[0]) ** (u * u * (3 - 2 * u))
        st += _st(osc(fz) * np.exp(-0.5 * ((t - hit) / 0.035) ** 2) * zip_amp)
    pw = pan_from + (pan_to - pan_from) * np.clip((t - hit * 0.45) / (d - hit * 0.45), 0, 1) ** 0.8
    st = pan(st, np.clip(pw, -1, 1))
    if verb:
        st = reverb(st, verb[0], wet_db=verb[1])
    return st


@_register('transition', 'very fast bright "fwip": band sweep 600 -> 5.2 kHz, low body, faint zip, L -> R',
           'whip pans, smash cuts, hook montage transitions', send=-18)
def whip(seed=0, direction=1):
    """Whip (~0.75 s incl. room). hit = 0.21 s (peak). direction -1 pans R -> L."""
    r = _rng(seed, 'whip')
    d, hit = 0.42, 0.21
    ph = hit / d
    st = _whoosh(d, hit, r, [(0, 650), (ph * 0.7, 1500), (ph, 5200), (1, 2600)],
                 [(0, 1.1), (ph, 0.75), (1, 1.2)], 3.2, 0.038, -0.65 * direction, 0.7 * direction, body=0.45,
                 body_fc=(170, 420), hiss=0.22, width=0.35, zip_amp=0.07, zip_f=(420, 1700), verb=('room', -17))
    return _finish(st, hit, -3.0, 'whip')


@_register('transition', 'quick airy rush 350 Hz -> 2.8 kHz with low body and top sizzle, panning',
           'cards flying in, UI windows arriving, camera whips', send=-16)
def whoosh_fast(seed=0, direction=1):
    """Fast whoosh (~0.8 s). hit = 0.42 s (peak)."""
    r = _rng(seed, 'whoosh_fast')
    d, hit = 0.82, 0.42
    ph = hit / d
    st = _whoosh(d, hit, r, [(0, 330), (ph, 2800), (1, 1100)], [(0, 1.3), (ph, 1.0), (1, 1.4)], 2.2, 0.09,
                 -0.55 * direction, 0.6 * direction, body=0.4, body_fc=(140, 330), hiss=0.16, width=0.55,
                 verb=('room', -15))
    return _finish(st, hit, -3.0, 'whoosh_fast')


@_register('transition', 'big soft swell of air, deep body, slow sweep with hall tail',
           'slow camera moves, scene reveals, glows blooming', send=-14)
def whoosh_slow(seed=0, direction=1):
    """Slow whoosh (~2.6 s incl. tail). hit = 1.20 s (peak)."""
    r = _rng(seed, 'whoosh_slow')
    d, hit = 2.0, 1.2
    ph = hit / d
    st = _whoosh(d, hit, r, [(0, 170), (ph, 1700), (1, 520)], [(0, 1.4), (ph, 1.0), (1, 1.5)], 1.8, 0.28,
                 -0.5 * direction, 0.5 * direction, body=0.5, body_fc=(90, 230), hiss=0.1, width=0.7,
                 comb=([(0, 0.004), (ph, 0.0012), (1, 0.003)], 0.35), verb=('hall', -11))
    return _finish(st, hit, -5.0, 'whoosh_slow')


@_register('transition', 'physically modelled doppler pass-by: airy whistle bands drop in pitch as it passes, '
           'per-ear delay/level and air absorption', 'cards rushing past camera (R2 tunnel), orbit passes',
           send=-18)
def whoosh_by(seed=0, dur=1.4, speed=62.0, dist=1.6, direction=1):
    """Doppler pass-by (~dur s). hit = moment of closest approach (~0.55*dur)."""
    r = _rng(seed, 'whoosh_by')
    c = 343.0
    t_close = 0.55 * dur - dist / c
    N = _n(dur)
    margin = 0.4
    Ns = _n(dur + 2 * margin)
    # source: air rush + two resonant whistle bands + soft low rumble (emission-time axis)
    src = _unit(bp(colored(Ns, r, -3.0), 120, 12000)) * 0.6
    for fz, q, a in ((820.0, 9.0, 0.9), (1650.0, 11.0, 0.7), (3300.0, 8.0, 0.35)):
        src += _unit(reson(r.standard_normal(Ns), fz * r.uniform(0.95, 1.05), q)) * a * 0.35
    src += _unit(lp(r.standard_normal(Ns), 160, 2)) * 0.25
    te_grid = np.arange(Ns) / SR - margin
    t_out = np.arange(N) / SR
    out = np.zeros((N, 2))
    fr = np.fft.rfftfreq(_NFFT, 1.0 / SR)
    for ch, ear in enumerate((-0.09, 0.09)):
        xs = direction * speed * (te_grid - t_close)
        rr = np.sqrt((xs - ear) ** 2 + dist ** 2)
        trcv = te_grid + rr / c
        te = np.interp(t_out, trcv, te_grid)
        s = np.interp(te, te_grid, src)
        x_at = direction * speed * (te - t_close)
        r_at = np.sqrt((x_at - ear) ** 2 + dist ** 2)
        g = (dist / r_at) ** 1.15
        # air absorption + head shadow (far ear duller), applied as a time-varying low-pass
        az = (x_at / r_at) * (1 if ear > 0 else -1)
        T = N // _HOP + 1
        tf = np.minimum(np.arange(T) * _HOP, N - 1)
        fc = 16000 * (dist / r_at[tf]) ** 0.9 * (0.55 + 0.45 * (0.5 + 0.5 * az[tf]))
        m = 1.0 / np.sqrt(1 + (fr[None, :] / np.maximum(fc, 400)[:, None]) ** 4)
        out[:, ch] = _istft(_stft(s * g) * m, N)
    # envelope: fade the far ends so the pass emerges from and recedes into silence
    p = t_out / dur
    out *= (np.clip(p / 0.15, 0, 1) ** 2 * np.clip((1 - p) / 0.2, 0, 1) ** 1.5)[:, None]
    out = reverb(out, 'room', wet_db=-16)
    return _finish(out, 0.55 * dur, -4.0, 'whoosh_by')


@_register('transition', 'small soft high swish (2 - 6 kHz), quick', 'chips, tags, small UI elements sliding in, '
           'cursor moves', send=-16)
def swish_small(seed=0, direction=1):
    """Small swish (~0.3 s). hit = 0.14 s."""
    r = _rng(seed, 'swish_small')
    d, hit = 0.30, 0.14
    ph = hit / d
    st = _whoosh(d, hit, r, [(0, 1900), (ph, 5600), (1, 3600)], 0.75, 2.0, 0.05, -0.3 * direction,
                 0.3 * direction, body=0.12, body_fc=(500, 900), hiss=0.12, width=0.5, verb=('room', -18))
    return _finish(st, hit, -11.0, 'swish_small')


@_register('transition', 'zoom-through air rush with jet-flange, low pressure swell, wide at the hit then '
           'collapses', 'zoom-throughs (R3 into the letter U), iris transitions', send=-16)
def air_zoom(seed=0):
    """Air zoom (~1.2 s). hit = 0.62 s (the pass-through point)."""
    r = _rng(seed, 'air_zoom')
    d, hit = 1.25, 0.62
    ph = hit / d
    t = _t(d)
    env = _swell(t, hit, 2.6, 0.11)
    rush = noise_band(d, r, [(0, 240), (ph * 0.8, 2600), (ph, 5600), (1, 900)], [(0, 1.5), (ph, 1.1), (1, 1.6)],
                      width=[(0, 0.2), (ph, 1.0), (1, 0.3)], comb=([(0, 0.006), (ph, 0.0004), (1, 0.002)], 0.55))
    rush = rush * env[:, None]
    low = noise_band(d, r, [(0, 60), (ph, 140), (1, 60)], 0.9, width=0.3) * _swell(t, hit, 2.0, 0.2)[:, None] * 0.5
    st = rush + low
    st = reverb(st, 'room', wet_db=-14)
    return _finish(st, hit, -2.0, 'air_zoom')


@_register('transition', 'tension build: noise sweep 250 Hz -> 9 kHz, rising inharmonic tone with '
           'accelerating tremolo, reverse-air rush; ends exactly at the hit', 'into end cards, into the '
           'question, before any big slam (pair with impact_big at the same t)', send=-18)
def riser(duration=2.0, seed=0):
    """Riser (duration s). hit = duration (the sound ends on the hit)."""
    r = _rng(seed, 'riser')
    d = float(duration)
    t = _t(d)
    p = t / d
    nz = noise_band(d, r, lambda q: 250 * (9000 / 250) ** (q ** 1.5), lambda q: 1.0 - 0.4 * q,
                    width=lambda q: 0.2 + 0.8 * q) * (p ** 2.4)[:, None]
    f = 140.0 * 2 ** (3.0 * p ** 1.7)
    trem = 0.6 + 0.4 * np.sin(TWO_PI * np.cumsum(3.0 + 21.0 * p ** 2) / SR)
    tone = (np.sin(TWO_PI * np.cumsum(f) / SR) + 0.45 * np.sin(TWO_PI * np.cumsum(f * 1.498) / SR)
            + 0.25 * np.sin(TWO_PI * np.cumsum(f * 2.01) / SR))
    tone = _sat(tone * 0.5, 1.5) * trem * p ** 3.0
    tone = decorrelate(tone, r, 0.6)
    rush = noise_band(d, r, [(0, 6000), (1, 12000)], 0.7, width=0.9) * (p ** 6)[:, None]
    st = 0.75 * nz + 0.20 * tone + 0.45 * rush
    st = reverb(st, 'plate', wet_db=-12)[:len(t)]
    st = _fade(st, 0.01, 0.004)
    return _finish(st, d, -4.0, 'riser', trim=False, fout=0.004)


@_register('transition', 'reversed hall bloom of a soft hit + bright air + shimmer: sucks into the hit',
           'into slams, flash frames, logo reveals, iris openings', send=-22)
def reverse_swell(duration=1.5, seed=0):
    """Reverse swell (duration s). hit = duration (ends on the hit)."""
    r = _rng(seed, 'reverse_swell')
    d = float(duration)
    src_d = 0.5
    t = _t(src_d)
    src = _thump(src_d, 70.0, 60.0, 0.02, 0.08, r, drive=1.5, noise=0.5) * 0.6
    src += _unit(hp(r.standard_normal(len(t)), 2500)) * _ar(t, 0.001, 0.06) * 0.6
    src += modal(src_d, [1800, 2950, 4400, 6600], [0.2, 0.15, 0.1, 0.07], [1, .7, .5, .3], r) * 0.25
    wet = reverb(src, 'hall', wet_db=0.0, dry=0.0, rt60=max(1.6, d * 1.3), predelay=0.0, build=0.005)
    n = _n(d)
    env = _smooth(np.abs(wet).max(1), 0.01)
    i0 = int(np.argmax(env[:_n(0.2)]))
    wet = wet[i0:]
    seg = wet[:n] if len(wet) >= n else np.pad(wet, ((0, n - len(wet)), (0, 0)))
    st = seg[::-1].copy()
    st *= (np.linspace(0, 1, n) ** 1.3)[:, None]
    st = _fade(st, 0.02, 0.003)
    return _finish(st, d, -4.0, 'reverse_swell', trim=False, fout=0.003)


@_register('transition', 'falling noise sweep 7 kHz -> 150 Hz with descending tone and soft boom',
           'after a hit, scene exits, settling to a calm section', send=-16)
def downlifter(seed=0, dur=2.0):
    """Downlifter (~dur s). hit = 0.01 s (the start; it falls away from the hit)."""
    r = _rng(seed, 'downlifter')
    t = _t(dur)
    p = t / dur
    nz = noise_band(dur, r, lambda q: 150 * (7000 / 150) ** ((1 - q) ** 1.6), 0.9, width=0.7)
    nz = nz * (_ar(t, 0.01, dur * 0.35))[:, None]
    tone = osc(60 + 840 * (1 - p) ** 2.2) * _ar(t, 0.01, dur * 0.25) * 0.12
    boom = _thump(1.0, 45.0, 50.0, 0.04, 0.3, r, drive=1.5)
    st = 0.6 * nz + _st(tone)
    _add(st, _st(boom * 0.45), 0.0)
    st = reverb(st, 'hall', wet_db=-10)
    return _finish(st, 0.01, -5.0, 'downlifter')


# ------------------------------------------------------------------------------------------- digital / UI
@_register('ui', 'tasteful digital stutter: 6-9 micro-grains (band noise, FM blips, repeats), randomly placed '
           'in the stereo field', 'glitch transitions, data/number flickers, chromatic-aberration hits',
           send=-18)
def glitch_short(seed=0):
    """Short glitch (~0.3 s). hit = 0.0 s."""
    r = _rng(seed, 'glitch_short')
    d = 0.34
    out = np.zeros((_n(d), 2))
    t0 = 0.0
    prev = None
    for k in range(r.integers(6, 10)):
        gl = r.uniform(0.008, 0.03)
        tt = _t(gl)
        mode = r.integers(0, 3) if prev is not None else r.integers(0, 2)
        if mode == 0:
            g = _unit(bp(r.standard_normal(len(tt)), *sorted([r.uniform(900, 4000), r.uniform(5000, 11000)])))
        elif mode == 1:
            fc = r.uniform(500, 2600)
            g = np.sin(TWO_PI * fc * tt + 3.0 * np.sin(TWO_PI * fc * r.choice([0.5, 1.5, 2.0]) * tt))
        else:
            g = prev[:len(tt)] if len(prev) >= len(tt) else np.pad(prev, (0, len(tt) - len(prev)))
        e = np.ones(len(tt))
        m = min(len(tt) // 3, int(0.0006 * SR))
        e[:m] = np.linspace(0, 1, m)
        e[-m:] = np.linspace(1, 0, m)
        g = g * e * r.uniform(0.4, 1.0) * (0.85 ** k)
        _add(out, pan(g, r.uniform(-0.8, 0.8)), t0)
        prev = g
        t0 += gl + (r.uniform(0.0, 0.025) if r.random() < 0.6 else 0.0)
        if t0 > d - 0.04:
            break
    tt = _t(0.08)
    _add(out, _st(_sat(osc(90 + 200 * np.exp(-tt / 0.01)) * _ar(tt, 0.0005, 0.02), 2) * 0.35), 0.0)
    out = reverb(out, 'room', wet_db=-18)
    return _finish(out, 0.0, -8.0, 'glitch_short', fin=0.0002)


@_register('ui', 'crisp soft glassy click: 2-9 kHz transient + 1.65/3.4 kHz modal body + tiny low tock',
           'cursor clicks, button presses, checklist ticks', send=-18)
def ui_click(seed=0, pitch=1.0):
    """UI click (~0.12 s). hit = 0.0005 s."""
    r = _rng(seed, 'ui_click')
    d = 0.14
    x = _click(d, r, (2200, 9000), 0.0018, [(1650 * pitch * r.uniform(.98, 1.02), 0.018, 0.5),
                                              (3420 * pitch, 0.009, 0.35), (5200 * pitch, 0.004, 0.2)],
               low=(380.0 * pitch, 0.012, 0.35))
    st = reverb(decorrelate(x, r, 0.15), 'room', wet_db=-20)
    return _finish(st, 0.0005, -9.0, 'ui_click', fin=0.0002)


@_register('ui', 'tiny high glassy tick (3.8 kHz)', 'slot digits, list items appearing, dot grids, progress '
           'ticks', send=-18)
def ui_tick(seed=0, pitch=1.0):
    """UI tick (~0.07 s). hit = 0.0003 s."""
    r = _rng(seed, 'ui_tick')
    d = 0.08
    x = _click(d, r, (4000, 12000), 0.0009, [(3800 * pitch, 0.007, 0.6), (6100 * pitch, 0.004, 0.3)])
    st = reverb(x, 'room', wet_db=-22)
    return _finish(st, 0.0003, -13.0, 'ui_tick', fin=0.0004)


@_register('ui', 'soft airy breath with a faint rising sine glint', 'hover states, focus changes, tile '
           'enlarge (R1 support dock)', send=-14)
def ui_hover(seed=0):
    """UI hover (~0.35 s). hit = 0.12 s (peak)."""
    r = _rng(seed, 'ui_hover')
    d, hit = 0.34, 0.12
    t = _t(d)
    env = np.where(t < hit, np.sin(np.pi / 2 * t / hit) ** 2, np.exp(-(t - hit) / 0.06))
    air = noise_band(d, r, [(0, 1700), (hit / d, 3400), (1, 3000)], 0.7, width=0.5) * env[:, None]
    glint = osc(1100 + 450 * np.clip(t / hit, 0, 1)) * env * 0.08
    st = _taper(air * 0.5 + _st(glint), 0.3)
    st = reverb(st, 'plate', wet_db=-15)
    return _finish(st, hit, -15.0, 'ui_hover')


@_register('ui', 'n soft laptop key presses with release clicks, human timing, occasional spacebar',
           'type-on text, search fields, form filling', send=-18)
def typing(n=12, cps=11.0, seed=0):
    """Typing (~n/cps s). hit = first key (0.002 s)."""
    r = _rng(seed, 'typing')
    d = n / cps + 0.35
    out = np.zeros((_n(d), 2))
    t0 = 0.002
    for k in range(int(n)):
        space = (k % 6 == 5) and r.random() < 0.8
        f1 = r.uniform(900, 1400) * (0.7 if space else 1)
        press = _click(0.07, r, (1400, 6500), 0.0025, [(f1, 0.012, 0.45), (f1 * 2.37, 0.006, 0.25)],
                       low=(240 if space else 300, 0.010, 0.45 if space else 0.3))
        rel = _click(0.05, r, (2000, 8000), 0.0015, [(f1 * 1.3, 0.006, 0.25)])
        g = undb(r.uniform(-2.5, 0.5))
        p = r.uniform(-0.25, 0.25)
        _add(out, pan(press * g, p), t0)
        _add(out, pan(rel * g * 0.35, p), t0 + r.uniform(0.06, 0.1))
        t0 += max(0.035, (1 / cps) * r.lognormal(0, 0.25))
    out = out[:_n(t0 + 0.2)]
    out = reverb(out, 'room', wet_db=-18)
    return _finish(out, 0.002, -12.0, 'typing', fin=0.0002, keep_until=t0)


@_register('ui', 'round soft "bloop" pop: upward pitch flick 420 -> 1100 Hz with tiny click', 'chips, tags, '
           'icons and bubbles popping in (spring overshoot)', send=-16)
def pop(seed=0, pitch=1.0):
    """Pop (~0.22 s). hit = 0.002 s."""
    r = _rng(seed, 'pop')
    d = 0.24
    t = _t(d)
    f = (420 + 680 * (1 - np.exp(-t / 0.012))) * pitch * r.uniform(0.97, 1.03)
    s = osc(f) * _ar(t, 0.0015, 0.034) + 0.18 * osc(f * 2.01) * _ar(t, 0.001, 0.018)
    s += _unit(bp(r.standard_normal(len(t)), 2000, 8000)) * _ar(t, 0.0002, 0.0015) * 0.08
    st = reverb(_st(s), 'room', wet_db=-17)
    return _finish(st, 0.002, -8.0, 'pop', fin=0.0003)


@_register('ui', 'liquid bubble: Minnaert chirp rising 900 -> 1.6 kHz, wet and small', 'bubbles, soft '
           'notifications, playful pops (R3 chips)', send=-16)
def bubble_pop(seed=0, pitch=1.0):
    """Bubble pop (~0.15 s). hit = 0.001 s."""
    r = _rng(seed, 'bubble_pop')
    d = 0.18
    t = _t(d)
    f0 = 880 * pitch * r.uniform(0.95, 1.05)
    f = f0 * (1 + 0.9 * (1 - np.exp(-t / 0.03)))
    s = osc(f) * _ar(t, 0.0006, 0.028)
    s += _unit(hp(r.standard_normal(len(t)), 3000)) * _ar(t, 0.0001, 0.0012) * 0.06
    st = reverb(_st(s), 'room', wet_db=-15)
    return _finish(st, 0.001, -9.0, 'bubble_pop', fin=0.0003)


@_register('ui', 'soft two-note glassy confirmation (E6 then B6, 85 ms apart) with plate shimmer',
           'checklist rows ticking, success states, eligibility checks', send=-14)
def check_ding(seed=0, pitch=1.0):
    """Check ding (~1.6 s). hit = 0.0015 s (first note; the second follows 0.085 s later)."""
    r = _rng(seed, 'check_ding')
    d = 1.6
    out = np.zeros(_n(d))
    for k, (f, a, off) in enumerate(((1318.5, 0.8, 0.0), (1975.5, 1.0, 0.085))):
        f *= pitch
        x = modal(d - off, [f, f * 2.0, f * 2.76, f * 5.4], [0.42, 0.22, 0.12, 0.05],
                  [1.0, 0.16, 0.10, 0.04], r, split=1.6, contact=0.0012)
        _add(out, x * a, off)
    st = decorrelate(out, r, 0.25)
    st = reverb(st, 'plate', wet_db=-10)
    return _finish(st, 0.0015, -7.0, 'check_ding')


@_register('ui', 'two-stage switch click with a soft rising glint', 'toggles, chips selecting, settings '
           'switching on', send=-18)
def toggle_on(seed=0):
    """Toggle on (~0.2 s). hit = 0.0005 s (first click; second click at 0.045 s)."""
    r = _rng(seed, 'toggle_on')
    d = 0.22
    out = np.zeros(_n(d))
    _add(out, _click(0.08, r, (1800, 7000), 0.002, [(1200, 0.010, 0.5), (2900, 0.006, 0.3)], low=(320, .01, .3)),
         0.0)
    _add(out, _click(0.08, r, (2500, 9000), 0.0015, [(1600, 0.008, 0.4), (3600, 0.005, 0.25)]) * 0.7, 0.045)
    tt = _t(0.12)
    _add(out, osc(700 + 360 * (1 - np.exp(-tt / 0.02))) * _ar(tt, 0.002, 0.035) * 0.14, 0.045)
    st = reverb(_st(out), 'room', wet_db=-19)
    return _finish(st, 0.0005, -10.0, 'toggle_on', fin=0.0002)


@_register('ui', 'warm rounded two-tone notification (G5 -> D6, marimba-like FM) with a short air lift',
           'toasts, success banners ("You could be a great fit"), totals revealed', send=-14)
def toast_chime(seed=0, pitch=1.0):
    """Toast chime (~2 s). hit = 0.002 s (first note; second at 0.11 s)."""
    r = _rng(seed, 'toast_chime')
    d = 2.0
    out = np.zeros(_n(d))
    for f, a, off in ((784.0, 0.8, 0.0), (1174.7, 1.0, 0.11)):
        f *= pitch
        x = fm_bell(d - off, f, ratio=4.0, index=1.1, tau=0.55, tau_index=0.03, attack=0.003)
        x += 0.12 * modal(d - off, [f * 3.93], [0.08], [1.0], r)
        x += 0.25 * np.sin(TWO_PI * f * 0.5 * _t(d - off)) * _ar(_t(d - off), 0.01, 0.25)
        _add(out, x * a, off)
    st = decorrelate(out, r, 0.3)
    air = noise_band(0.3, r, [(0, 2500), (1, 6000)], 0.8, width=0.7) * _swell(_t(0.3), 0.1, 2, 0.08)[:, None]
    _add(st, air * 0.05, 0.0)
    st = reverb(st, 'plate', wet_db=-11)
    return _finish(st, 0.002, -7.0, 'toast_chime')


@_register('ui', 'clear tap on a glass pane: inharmonic glass modes with slow beating', 'glass cards '
           'landing, frosted panels, taps on the glass UI', send=-14)
def glass_tap(seed=0, pitch=1.0):
    """Glass tap (~1.1 s). hit = 0.0005 s."""
    r = _rng(seed, 'glass_tap')
    d = 1.8
    f0 = 2150 * pitch * r.uniform(0.97, 1.03)
    rat = [1.0, 2.07, 3.42, 5.10, 7.12]
    x = modal(d, [f0 * k for k in rat], [0.45, 0.26, 0.15, 0.08, 0.05], [1, .55, .35, .2, .12], r, split=2.2)
    x += _click(d, r, (3000, 12000), 0.0008) * 0.5
    st = reverb(decorrelate(x, r, 0.25), 'room', wet_db=-14)
    return _finish(st, 0.0005, -10.0, 'glass_tap', fin=0.0002)


@_register('ui', 'card sliding on a surface (friction) then a soft "thup" landing', 'cards/tiles sliding into '
           'place (carousel), panels docking', send=-16)
def card_slide(seed=0, dur=0.42):
    """Card slide (~dur + 0.15 s). hit = landing at dur*0.86."""
    r = _rng(seed, 'card_slide')
    land = dur * 0.86
    d = dur + 0.25
    t = _t(d)
    am = 0.75 + 0.25 * _unit(lp(r.standard_normal(len(t)), 40, 2))
    env = np.clip(t / (land * 0.6), 0, 1) ** 1.5 * np.where(t < land, 1, np.exp(-(t - land) / 0.015))
    fr = noise_band(d, r, [(0, 1400), (land / d, 2700), (1, 2000)], 0.9, width=0.4) * (env * am)[:, None]
    th = np.zeros(len(t))
    _add(th, _thump(0.2, 105.0, 70.0, 0.012, 0.03, r, attack=0.001, drive=1.5, noise=0.6, noise_lp=1200,
                    click=0.3), land)
    st = 0.35 * fr + pan(th, 0.0) * 0.8
    st = pan(st, np.linspace(-0.25, 0.1, len(st)))
    st = reverb(st, 'room', wet_db=-16)
    return _finish(st, land, -10.0, 'card_slide')


@_register('ui', 'satisfying plastic snap: short slide-in, sharp latch, plastic modes, low thock',
           'puzzle pieces locking (R3 matching), components snapping together', send=-16)
def puzzle_click(seed=0):
    """Puzzle click (~0.35 s). hit = 0.06 s (the snap)."""
    r = _rng(seed, 'puzzle_click')
    hit, d = 0.06, 0.38
    t = _t(d)
    slide = noise_band(d, r, [(0, 1800), (1, 3500)], 0.8) * (np.clip(t / hit, 0, 1) ** 2 * (t < hit))
    x = 0.08 * slide
    snap = _click(0.25, r, (2000, 10000), 0.0012, [(1450, 0.02, 0.5), (2380, 0.012, 0.4), (3720, 0.008, 0.3),
                                                    (5200, 0.005, 0.2)], low=(190, 0.018, 0.6))
    _add(x, snap, hit)
    _add(x, _click(0.06, r, (3000, 9000), 0.001, [(2900, 0.005, 0.3)]) * 0.35, hit + 0.013)
    st = reverb(decorrelate(x, r, 0.15), 'room', wet_db=-16)
    return _finish(st, hit, -6.0, 'puzzle_click', fin=0.0005)


@_register('ui', 'mechanical camera shutter: mirror click, short whirr, shutter close', 'photo cards '
           'appearing, snapshots, freeze frames', send=-18)
def camera_shutter(seed=0):
    """Camera shutter (~0.35 s). hit = 0.0005 s (first click; second at 0.075 s)."""
    r = _rng(seed, 'camera_shutter')
    d = 0.36
    t = _t(d)
    x = np.zeros(len(t))
    c1 = _click(0.12, r, (1200, 8000), 0.002, [(3100, 0.012, 0.4), (4700, 0.009, 0.3), (6900, 0.006, 0.2)],
                low=(420, 0.008, 0.4))
    c2 = _click(0.12, r, (1500, 9000), 0.0015, [(2700, 0.010, 0.4), (5300, 0.007, 0.25)], low=(380, .007, .35))
    _add(x, c1, 0.0)
    _add(x, c2 * 0.8, 0.075)
    wh = _unit(bp(r.standard_normal(len(t)), 2000, 5000)) * (0.6 + 0.4 * np.sin(TWO_PI * 180 * t))
    x += wh * np.exp(-0.5 * ((t - 0.04) / 0.015) ** 2) * 0.05
    st = reverb(decorrelate(x, r, 0.2), 'room', wet_db=-18)
    return _finish(st, 0.0005, -8.0, 'camera_shutter', fin=0.0002)


# ------------------------------------------------------------------------------------------- money
_COIN = [1.0, 1.73, 2.33, 3.91, 4.11, 6.30]          # free circular plate mode ratios (Chladni)


def _coin_ring(d, r, f0, tau0=0.7, hard=1.0, split=3.5):
    taus = [tau0, tau0 * 0.6, tau0 * 0.45, tau0 * 0.22, tau0 * 0.2, tau0 * 0.1]
    amps = np.array([1.0, 0.8, 0.6, 0.35, 0.3, 0.15]) * np.exp(-np.array(_COIN) * f0 / (9000 * hard))
    x = modal(d, [f0 * k * r.uniform(0.995, 1.005) for k in _COIN], taus, amps, r, split=split, contact=0.0002)
    x += _click(d, r, (4000, 14000), 0.0007) * 0.25 * hard
    return x


@_register('money', 'metallic thumb flick (ping) then a spinning shimmer whose rotation AM slows down',
           'coin flips (R2 hook, R2 end-card coin -> logo)', send=-14)
def coin_flip(seed=0):
    """Coin flip (~1.4 s). hit = 0.0005 s (the flick)."""
    r = _rng(seed, 'coin_flip')
    d = 2.2
    t = _t(d)
    ping = _coin_ring(d, r, 3050, tau0=0.5, hard=1.2)
    rate = 34 * np.exp(-t / 1.2) + 8
    rot = 0.5 + 0.5 * np.cos(TWO_PI * np.cumsum(rate) / SR)
    spin = _coin_ring(d, r, 3050, tau0=0.9, hard=0.8, split=6.0) * (0.25 + 0.75 * rot ** 2) * 0.6
    flutter = noise_band(d, r, [(0, 5000), (1, 3500)], 0.6) * (rot * _ar(t, 0.03, 0.4)) * 0.05
    flutter = _taper(flutter, 0.3)
    x = ping * _ar(t, 0.0002, 0.08) + spin * np.clip(t / 0.03, 0, 1) + flutter
    st = pan(decorrelate(x, r, 0.3), np.sin(TWO_PI * np.cumsum(rate * 0.12) / SR) * 0.35)
    st = reverb(st, 'plate', wet_db=-14)
    return _finish(st, 0.0005, -7.0, 'coin_flip', fin=0.0002)


@_register('money', 'bright gold coin strike: plate modes as beating doublets, long ring', 'coin landing, '
           'the £ number appearing, coin orbit accents', send=-14)
def coin_ring(seed=0, pitch=1.0):
    """Coin ring (~2 s). hit = 0.0003 s."""
    r = _rng(seed, 'coin_ring')
    d = 3.0
    x = _coin_ring(d, r, 2750 * pitch * r.uniform(0.98, 1.02), tau0=0.75, hard=1.0)
    st = reverb(decorrelate(x, r, 0.3), 'plate', wet_db=-13)
    return _finish(st, 0.0004, -8.0, 'coin_ring', fin=0.0004)


@_register('money', 'cascade of ~26 coins: dense clatter that thins out, panned wide', 'money bursts, totals '
           'landing, coins exploding from the £ coin', send=-14)
def coins_burst(seed=0, n=26):
    """Coins burst (~2 s). hit = 0.0005 s (first coin; density peaks in the first 150 ms)."""
    r = _rng(seed, 'coins_burst')
    d = 2.0
    out = np.zeros((_n(d), 2))
    for k in range(int(n)):
        t0 = 0.0 if k == 0 else min(d - 0.6, r.exponential(0.16))
        f0 = math.exp(r.uniform(math.log(2300), math.log(4800)))
        x = _coin_ring(1.5, r, f0, tau0=r.uniform(0.12, 0.45), hard=r.uniform(0.8, 1.3), split=r.uniform(2, 8))
        g = r.uniform(0.25, 1.0) * math.exp(-t0 / 0.5)
        _add(out, pan(x * g, r.uniform(-0.85, 0.85)), t0)
    out = reverb(out, 'plate', wet_db=-12)
    return _finish(out, 0.0005, -5.0, 'coins_burst', fin=0.0002)


@_register('money', 'register "ka" lever, bright beating bell "ching", soft drawer slide and thunk with a few '
           'coin jingles', 'the £23,275.20 total landing (R2), cash moments', send=-14)
def cash_kaching(seed=0):
    """Cash ka-ching (~2.2 s). hit = 0.12 s (the bell)."""
    r = _rng(seed, 'cash_kaching')
    hit, d = 0.12, 3.2
    t = _t(d)
    x = np.zeros((len(t), 2))
    ka = _click(0.12, r, (1000, 6000), 0.004, [(620, 0.02, 0.6), (1130, 0.015, 0.4), (2400, 0.008, 0.2)],
                low=(210, 0.02, 0.5))
    _add(x, _st(ka) * 0.55, 0.0)
    for k in range(3):
        _add(x, _st(_click(0.03, r, (2500, 8000), 0.001, [(2800 + 300 * k, 0.004, 0.3)]) * 0.18), 0.03 + 0.016 * k)
    f0 = 2350.0
    bell = modal(d - hit, [f0, f0 * 2.01, f0 * 2.74, f0 * 3.98, f0 * 5.41],
                 [0.95, 0.55, 0.38, 0.22, 0.13], [1.0, 0.45, 0.35, 0.18, 0.1], r, split=2.2, split_mix=0.3,
                 contact=0.0003)
    tb = _t(d - hit)
    bell += _unit(hp(r.standard_normal(len(tb)), 5000)) * _ar(tb, 0.0002, 0.005) * 0.12      # the "ch"
    _add(x, decorrelate(bell, r, 0.3), hit)
    sl = noise_band(0.26, r, [(0, 600), (1, 1800)], 1.0, width=0.4) * _swell(_t(0.26), 0.2, 1.5, 0.02)[:, None]
    _add(x, sl * 0.10, 0.26)
    _add(x, _st(_thump(0.2, 110.0, 60.0, 0.01, 0.035, r, drive=1.5, noise=0.6, noise_lp=900, click=0.3) * 0.35),
         0.47)
    for k in range(3):
        _add(x, pan(_coin_ring(0.6, r, r.uniform(3200, 4800), tau0=0.15) * 0.12, r.uniform(-.5, .5)),
             0.48 + 0.03 * k + r.uniform(0, 0.02))
    st = reverb(x, 'plate', wet_db=-12)
    return _finish(st, hit, -4.0, 'cash_kaching', fin=0.0002)


@_register('money', 'n rolling-digit ticks that decelerate (ease-out) and land on a firmer click with a glint',
           'slot-machine digit rolls, counters (R2 £0 -> £447.60)', send=-18)
def slot_tick(n=16, dur=1.2, ease='out', seed=0):
    """Slot ticks over dur s. ease 'out' (fast -> slow, like an out_cubic counter) or 'linear'.
    hit = dur (the landing click). Cue it with align='start' at the roll start or align='hit' at the landing."""
    r = _rng(seed, 'slot_tick')
    n = max(2, int(n))
    D = dur + 0.5
    out = np.zeros((_n(D), 2))
    if ease == 'out':                       # gaps grow geometrically: the last gap is 4x the first
        rr = 4.0 ** (1.0 / max(n - 2, 1))
        gaps = rr ** np.arange(n - 1)
        times = np.concatenate([[0.0], np.cumsum(gaps)]) * (dur / np.sum(gaps))
    else:
        times = np.linspace(0, dur, n)
    for k in range(n):
        u = k / (n - 1)
        tk = times[k]
        last = k == n - 1
        f = 2600 + 900 * u + r.uniform(-60, 60)
        x = _click(0.06, r, (3000, 10000), 0.0008, [(f, 0.006, 0.6), (f * 1.62, 0.004, 0.3)])
        if last:
            x = _click(0.3, r, (2000, 9000), 0.0015, [(1500, 0.02, 0.5), (3200, 0.012, 0.35)], low=(300, .015, .5))
            x += modal(0.3, [4200, 6300], [0.12, 0.07], [0.12, 0.06], r)
        _add(out, pan(x * (1.6 if last else r.uniform(0.6, 0.9)), r.uniform(-0.15, 0.15)), tk)
    out = reverb(out, 'room', wet_db=-18)
    return _finish(out, dur, -10.0, 'slot_tick', fin=0.0002)


@_register('ui', 'slider drag: fine detent ticks rising in pitch with the value, soft friction, end stop click',
           'weeks-of-care slider (R2), scrubbers, range inputs', send=-18)
def slider_drag(duration=1.0, seed=0, detents=28):
    """Slider drag over duration s (knob eases in-out). hit = duration (stop click); usually align='start'."""
    r = _rng(seed, 'slider_drag')
    d = duration + 0.3
    t = _t(d)
    out = np.zeros((len(t), 2))
    u = np.clip(t / duration, 0, 1)
    pos = u * u * (3 - 2 * u)
    speed = np.gradient(pos) * SR * duration / 1.5
    for k in range(1, int(detents)):
        tk = np.interp(k / detents, pos[t <= duration], t[t <= duration])
        f = 2200 + 1500 * k / detents
        x = _click(0.03, r, (3000, 9000), 0.0006, [(f, 0.004, 0.5)])
        _add(out, _st(x * r.uniform(0.45, 0.7)), tk)
    fr = noise_band(d, r, 3200, 0.9, width=0.3) * (np.clip(speed, 0, 1.5) * (t < duration))[:, None] * 0.05
    glide = osc(500 + 450 * pos) * np.clip(speed, 0, 1.5) * (t < duration) * 0.04
    out += fr + _st(glide)
    _add(out, _st(_click(0.1, r, (2000, 8000), 0.0015, [(1500, 0.012, 0.5)], low=(320, .01, .4))), duration)
    out = pan(out, np.linspace(-0.3, 0.3, len(out)))
    out = reverb(out, 'room', wet_db=-18)
    return _finish(out, duration, -12.0, 'slider_drag', fin=0.001)


@_register('ui', 'rising soft tonal swell (one glide up ~an octave + air), settles with a tiny wooden tock',
           'bar charts growing, progress rings filling, counters climbing', send=-15)
def bar_grow(duration=0.8, pitch=1.0, seed=0):
    """Bar grow over duration s. pitch scales the glide (map bar height -> pitch). hit = duration (the bar
    reaches full height). Usually align='start' at the grow start."""
    r = _rng(seed, 'bar_grow')
    d = duration + 0.45
    t = _t(d)
    u = np.clip(t / duration, 0, 1)
    ue = 1 - (1 - u) ** 2.2
    f = 230.0 * pitch * 2 ** (1.05 * ue)
    env = np.where(t < duration, u ** 1.3, np.exp(-(t - duration) / 0.09))
    env = _smooth(env, 0.004)
    tone = (osc(f) + 0.35 * osc(f * 2.0) + 0.12 * osc(f * 3.0)) * env
    air = noise_band(d, r, [(0, 600), (duration / d, 3200), (1, 2400)], 0.9, width=0.5) * env[:, None]
    tock = np.zeros(len(t))
    _add(tock, _click(0.1, r, (1500, 6000), 0.002, [(880 * pitch, 0.02, 0.6), (2350 * pitch, 0.008, 0.25)]),
         duration)
    st = _taper(_st(0.14 * tone + 0.5 * tock) + 0.12 * air, sec=0.2)
    st = reverb(decorrelate(st, r, 0.2), 'plate', wet_db=-14)
    return _finish(st, duration, -10.0, 'bar_grow')


# ------------------------------------------------------------------------------------------- sparkle / organic
@_register('texture', 'sparkling high cloud: ~60 sine grains 3 - 11 kHz with decaying density, plate wash',
           'light sweeps across type, glows blooming, logo glints', send=-12)
def shimmer(seed=0, dur=2.0):
    """Shimmer (~dur + tail). hit = 0.02 s (onset; density peaks immediately)."""
    r = _rng(seed, 'shimmer')
    g = _grains(dur, r, int(60 * dur / 2), 3000, 11000, 0.03, 0.18, density=lambda p: np.exp(-p * 3.5),
                amp=lambda p: math.exp(-p * 1.5), spread=0.95, harm=0.15)
    air = noise_band(dur, r, 9000, 0.5, width=1.0) * _ar(_t(dur), 0.02, dur * 0.3)[:, None] * 0.025
    st = reverb(g + air, 'plate', wet_db=-7)
    return _finish(st, 0.02, -10.0, 'shimmer')


@_register('texture', 'a few bright FM twinkles in quick succession', 'small glints, stars, badges, check '
           'icons glowing', send=-12)
def sparkle(seed=0):
    """Sparkle (~1.2 s). hit = 0.002 s."""
    r = _rng(seed, 'sparkle')
    d = 1.2
    out = np.zeros((_n(d), 2))
    t0 = 0.0
    for k in range(r.integers(7, 11)):
        f = math.exp(r.uniform(math.log(3400), math.log(8200)))
        x = fm_bell(0.5, f, ratio=1.41, index=1.2, tau=r.uniform(0.06, 0.16), tau_index=0.02, attack=0.0015)
        _add(out, pan(x * r.uniform(0.4, 1.0) * math.exp(-t0 / 0.25), r.uniform(-0.8, 0.8)), t0)
        t0 += r.uniform(0.015, 0.06)
    st = reverb(out, 'plate', wet_db=-8)
    return _finish(st, 0.002, -11.0, 'sparkle')


@_register('texture', 'airy circular shimmer: band noise through a moving comb (phasing ring) with rotating '
           'pan and soft high pings', 'ripple rings (R3 seed impact), iris/ring wipes, radial reveals',
           send=-12)
def ripple(seed=0, dur=2.2):
    """Ripple (~dur + tail). hit = 0.03 s (onset)."""
    r = _rng(seed, 'ripple')
    t = _t(dur)
    env = _ar(t, 0.03, dur * 0.32)
    nz = noise_band(dur, r, [(0, 2600), (1, 5200)], 0.6, width=0.6,
                    comb=([(0, 0.0007), (0.5, 0.0024), (1, 0.0038)], 0.8))
    ang = TWO_PI * 1.6 * (1 - np.exp(-t / (dur * 0.5)))
    st = pan(nz * env[:, None], 0.75 * np.sin(ang))
    pings = _grains(dur, r, 9, 2400, 6500, 0.15, 0.4, density=lambda p: np.exp(-p * 4), spread=0.7)
    st = 0.28 * st + 0.18 * pings
    st = reverb(st, 'air', wet_db=-9)
    return _finish(st, 0.03, -10.0, 'ripple')


@_register('texture', 'water-drop plip (rising bubble chirp) + soft felt thud + tiny splash', 'the seed '
           'landing (R3 0.0 - 1.0 s), drops, gentle arrivals', send=-12)
def seed_plip(seed=0):
    """Seed plip (~1.2 s). hit = 0.002 s."""
    r = _rng(seed, 'seed_plip')
    d = 1.2
    t = _t(d)
    f = 720 * (1 + 1.4 * (1 - np.exp(-t / 0.022)))
    plip = osc(f) * _ar(t, 0.0008, 0.032)
    plip += 0.25 * osc(f * 2.02) * _ar(t, 0.0005, 0.012)
    thud = _thump(0.4, 66.0, 50.0, 0.02, 0.07, r, attack=0.003, drive=1.6, noise=0.5, noise_lp=450)
    spl = _unit(bp(r.standard_normal(len(t)), 2000, 7000)) * _ar(t, 0.0004, 0.014)
    x = 0.8 * plip + spl * 0.07
    _add(x, bass_enhance(thud, 0.8) * 0.55, 0.004)
    st = reverb(decorrelate(x, r, 0.2), 'plate', wet_db=-12)
    st = reverb(st, 'outdoor', wet_db=-16)
    return _finish(st, 0.002, -7.0, 'seed_plip', fin=0.0003)


@_register('texture', 'organic rising swell: breathy resonant air rising, woody inharmonic resonances gliding '
           'up, leaf rustle building; peaks at the end', 'sprout growth (R3 2.0 - 5.5 s), things growing',
           send=-14)
def grow_swell(duration=2.5, seed=0):
    """Grow swell over duration s (+0.6 s release). hit = duration (the peak). Usually align='start'."""
    r = _rng(seed, 'grow_swell')
    d = duration + 0.6
    t = _t(d)
    pk = duration / d
    env = np.where(t < duration, (t / duration) ** 1.7, np.exp(-(t - duration) / 0.2))
    env = _smooth(env, 0.01)
    air = noise_band(d, r, [(0, 280), (pk, 3800), (1, 2200)], [(0, 1.2), (pk, 0.85), (1, 1.1)],
                     width=[(0, 0.3), (pk, 0.9), (1, 0.8)])

    def woody(p, f):
        g = np.zeros((len(p), len(f)))
        base = 150 * 2 ** (0.55 * np.clip(p / pk, 0, 1))
        for k, a in ((1.0, 1.0), (1.47, 0.7), (2.13, 0.5), (3.05, 0.3), (4.4, 0.15)):
            g += a * np.exp(-0.5 * (np.log2(np.maximum(f, 8)[None, :] / (base[:, None] * k)) / 0.022) ** 2)
        return 0.04 + g
    body = noise_band(d, r, [(0, 260), (pk, 520), (1, 460)], 1.0, width=0.4, extra=woody)
    rust = _crackle(d, r, 900, 2200, 9000, env=lambda p: np.clip(p / pk, 0, 1) ** 1.5 * (p < pk * 1.05))
    st = (0.45 * air + 0.55 * body) * env[:, None] + 0.5 * rust
    st = reverb(st, 'plate', wet_db=-13)
    return _finish(st, duration, -8.0, 'grow_swell', keep_until=duration + 0.3)


@_register('texture', 'crinkly leaf rustle: hundreds of tiny noise grains under a soft swell', 'leaves '
           'unfolding/drifting, foliage motifs, paper', send=-14)
def leaf_rustle(seed=0, dur=1.0):
    """Leaf rustle (~dur s). hit = 0.3*dur (peak)."""
    r = _rng(seed, 'leaf_rustle')
    hit = 0.3 * dur
    t = _t(dur)
    env = _swell(t, hit, 1.5, dur * 0.22)
    cr = _crackle(dur, r, 1400, 2400, 11000,
                  env=lambda p: np.where(p < 0.3, (p / 0.3) ** 1.5, np.exp(-(p - 0.3) / 0.22)))
    body = noise_band(dur, r, 3000, 1.0, width=0.8) * env[:, None] * 0.12
    st = reverb(cr + body, 'outdoor', wet_db=-14)
    return _finish(st, hit, -13.0, 'leaf_rustle')


# ============================================================================================ ambience beds (loops)
def _loop_mask_noise(L, rng, mask_fn, chans=2, corr=0.3):
    """Seamless loop of noise shaped by a time-varying spectral mask that is periodic over the loop:
    process three copies and keep the middle one."""
    common = rng.standard_normal(L)
    out = np.zeros((L, chans))
    for c in range(chans):
        w = math.sqrt(corr) * common + math.sqrt(1 - corr) * rng.standard_normal(L)
        x3 = np.tile(w, 3)
        S = _stft(x3)
        T = S.shape[0]
        tl = (np.arange(T) * _HOP / SR) % (L / SR)
        f = np.fft.rfftfreq(_NFFT, 1.0 / SR)
        y = _istft(S * mask_fn(tl, f), 3 * L)
        out[:, c] = y[L:2 * L]
    return out


def _spec_filter(x, gain_fn):
    """Zero-phase circular FFT filter (loop-safe): gain_fn(f) -> magnitude."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    g = gain_fn(f)
    return np.fft.irfft(X * (g[:, None] if X.ndim == 2 else g), n=len(x), axis=0)


def _periodic_lfo(tl, L, rng, k_max=4, amp=1.0):
    """Smooth random LFO periodic over L seconds (integer cycles)."""
    v = np.zeros_like(tl)
    for k in range(1, k_max + 1):
        v += rng.uniform(0.3, 1.0) / k * np.sin(TWO_PI * k * tl / L + rng.uniform(0, TWO_PI))
    return amp * v / (np.max(np.abs(v)) + 1e-9)


def _bed_finish(x, name, level=0.0):
    x = _st(x)
    x = x - x.mean(0)
    g = undb(REF_LUFS + level - loudness(x))
    return Sfx(x * g, 0.0, name)


@_register('bed', 'warm interior room tone: soft low-mid air, gentle HVAC-like body, faint presence, slow '
           'breathing; seamless loop', 'under R1 (and R2 light) as the "warm room" floor')
def room_tone(dur=16.0, seed=0):
    """Seamless room-tone loop (dur s). Loop it by tiling; hit = 0."""
    r = _rng(seed, 'room_tone')
    L = _n(dur)
    x = np.stack([colored(L, r, -4.5, 30, 9000), colored(L, r, -4.5, 30, 9000)], 1)
    x[:, 1] = 0.45 * x[:, 0] + math.sqrt(1 - 0.45 ** 2) * x[:, 1]

    def g(f):
        lpm = 1 / np.sqrt(1 + (f / 650.0) ** 4)
        hum = 1 + 1.2 * np.exp(-0.5 * (np.log2(np.maximum(f, 8) / 140.0) / 0.25) ** 2)
        pres = 0.12 * np.exp(-0.5 * (np.log2(np.maximum(f, 8) / 1800.0) / 0.6) ** 2)
        sub = 1 / np.sqrt(1 + (45.0 / np.maximum(f, 1)) ** 4)
        return (lpm * hum + pres) * sub
    x = _spec_filter(x, g)
    tl = np.arange(L) / SR
    x *= (1 + 0.12 * _periodic_lfo(tl, dur, r, 3))[:, None]
    x = reverb_circular(x, 'room', wet_db=-6)
    return _bed_finish(x, 'room_tone')


@_register('bed', 'dark airy hum: very low resonant drone (62/124 Hz bands of noise, no mains tone), slow '
           'distant wind breathing, faint high air; seamless loop', 'very subtle floor for the dark reels')
def night_air(dur=20.0, seed=0):
    """Seamless night-air loop (dur s). hit = 0."""
    r = _rng(seed, 'night_air')
    L = _n(dur)
    lfo1 = (r.uniform(0, TWO_PI), r.uniform(0, TWO_PI))

    def mask(tl, f):
        lf = np.log2(np.maximum(f, 8))[None, :]
        a = 0.5 + 0.5 * np.sin(TWO_PI * 2 * tl / dur + lfo1[0])[:, None]
        b = 0.5 + 0.5 * np.sin(TWO_PI * 3 * tl / dur + lfo1[1])[:, None]
        drone = 1.0 * np.exp(-0.5 * ((lf - np.log2(62)) / 0.07) ** 2) + 0.55 * np.exp(-0.5 * ((lf - np.log2(124))
                                                                                            / 0.06) ** 2)
        floor = 0.35 * np.exp(-0.5 * ((lf - np.log2(90)) / 0.9) ** 2)
        wind_c = np.log2(420) + 0.5 * (a - 0.5)
        wind = (0.18 + 0.22 * b) * np.exp(-0.5 * ((lf - wind_c) / 0.7) ** 2)
        hi = 0.025 * np.exp(-0.5 * ((lf - np.log2(6500)) / 0.6) ** 2)
        return drone + floor + wind + hi
    x = _loop_mask_noise(L, r, mask, corr=0.5)
    x = reverb_circular(x, 'hall', wet_db=-8)
    return _bed_finish(x, 'night_air')


def _bird_call(kind, r):
    if kind == 'chirp':                       # quick up/down FM chirps (songbird)
        out = []
        for k in range(r.integers(3, 7)):
            d = r.uniform(0.03, 0.06)
            t = _t(d)
            f0, f1 = r.uniform(3200, 4200), r.uniform(4800, 6200)
            if r.random() < 0.5:
                f0, f1 = f1, f0
            f = f0 + (f1 - f0) * (t / d) ** 0.7
            s = (osc(f) + 0.12 * osc(2 * f)) * np.sin(np.pi * t / d) ** 2
            out.append(s)
            out.append(np.zeros(_n(r.uniform(0.04, 0.09))))
        return np.concatenate(out)
    if kind == 'trill':                       # warbling trill
        d = r.uniform(0.35, 0.7)
        t = _t(d)
        fc = r.uniform(3300, 4200)
        f = fc + r.uniform(300, 600) * np.sin(TWO_PI * r.uniform(22, 32) * t) + 300 * (t / d)
        am = 0.55 + 0.45 * np.sin(TWO_PI * r.uniform(22, 32) * t + 1.0)
        return (osc(f) + 0.1 * osc(2 * f)) * am * np.sin(np.pi * t / d) ** 1.2
    # 'whistle': two-note "tea-cher" call repeated
    out = []
    a, b = r.uniform(4000, 4600), r.uniform(3200, 3600)
    for k in range(r.integers(2, 4)):
        for f, dd in ((a, 0.11), (b, 0.13)):
            t = _t(dd)
            fr = f * (1 + 0.03 * np.sin(np.pi * t / dd))
            out.append((osc(fr) + 0.08 * osc(2 * fr)) * np.sin(np.pi * t / dd) ** 1.5)
            out.append(np.zeros(_n(0.035)))
        out.append(np.zeros(_n(0.09)))
    return np.concatenate(out)


@_register('bed', 'gentle outdoor bed: breeze gusts through soft foliage + sparse synthesised birdsong '
           '(chirps, trills, two-note whistles) at various distances; seamless loop', 'R3 light reel ambience')
def outdoor_birds(dur=24.0, seed=0, birds=1.0):
    """Seamless outdoor loop (dur s) with birdsong. birds scales the bird level. hit = 0."""
    r = _rng(seed, 'outdoor_birds')
    L = _n(dur)
    ph = r.uniform(0, TWO_PI, 3)

    def mask(tl, f):
        lf = np.log2(np.maximum(f, 8))[None, :]
        gust = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(TWO_PI * 2 * tl / dur + ph[0]) * np.sin(TWO_PI * 3 * tl / dur
                                                                                        + ph[1])) ** 1.5
        c = np.log2(420) + 0.7 * (gust[:, None] - 0.5)
        breeze = gust[:, None] * np.exp(-0.5 * ((lf - c) / 0.8) ** 2)
        leaves = 0.05 * gust[:, None] ** 2 * np.exp(-0.5 * ((lf - np.log2(3500)) / 0.5) ** 2)
        low = 0.3 * np.exp(-0.5 * ((lf - np.log2(140)) / 0.7) ** 2)
        return breeze + leaves + low
    x = _loop_mask_noise(L, r, mask, corr=0.25)
    x = _unit(x) * 0.22
    birds_buf = np.zeros((L, 2))
    t0 = r.uniform(0.2, 1.0)
    while t0 < dur - 0.2:
        kind = r.choice(['chirp', 'chirp', 'trill', 'whistle'])
        call = _bird_call(kind, r)
        dist = r.uniform(0.0, 1.0) ** 0.8
        call = lp(call, 12000 - 6000 * dist, 2) * (1.0 - 0.6 * dist) * r.uniform(0.6, 1.0)
        st = pan(call, r.uniform(-0.85, 0.85))
        i = int(t0 * SR)
        idx = (i + np.arange(len(st))) % L
        np.add.at(birds_buf, idx, st)
        t0 += r.uniform(0.7, 2.4)
    birds_buf = reverb_circular(birds_buf, 'outdoor', wet_db=-4)
    x = x + birds_buf * 0.45 * birds
    return _bed_finish(x, 'outdoor_birds')


BEDS = ('room_tone', 'night_air', 'outdoor_birds')

# default level offsets (dB re REF_LUFS) are the `level` passed to _finish inside each function;
# send = default shared-room reverb send (dB) by category when the sound does not override it
_CAT_SEND = dict(impact=-22.0, transition=-16.0, ui=-17.0, money=-15.0, texture=-13.0, bed=None)
_PRIORITY = dict(impact=4, transition=3, money=2, texture=1.5, ui=1, bed=0)


# ============================================================================================ cached access
ALIASES = dict(whoosh='whoosh_fast', boom='impact_big', impact='impact_big', hit='impact_soft', thud='impact_soft',
               click='ui_click', tick='ui_tick', hover='ui_hover', ding='check_ding', check='check_ding',
               chime='toast_chime', toast='toast_chime', coin='coin_ring', kaching='cash_kaching',
               swell='reverse_swell', reverse='reverse_swell', shutter='camera_shutter', rustle='leaf_rustle',
               zoom='air_zoom', flash='flash_hit', drop='sub_drop', glitch='glitch_short', swish='swish_small',
               slide='card_slide', snap='puzzle_click', plip='seed_plip', grow='grow_swell', sting='logo_sting',
               bubble='bubble_pop', toggle='toggle_on', slider='slider_drag', slot='slot_tick', bar='bar_grow',
               by='whoosh_by', passby='whoosh_by', heart='heartbeat')


_WARNED = set()


def resolve(name, fuzzy=True):
    """Library name for a sound name or alias. With fuzzy, an unknown 'word_word' name falls back to its first
    or last word as a name/alias (e.g. 'whoosh_in' -> whoosh_fast, 'impact_glass' -> impact_big) with a printed
    warning; otherwise KeyError listing the valid names."""
    if name in SOUNDS:
        return name
    if name in ALIASES:
        return ALIASES[name]
    if fuzzy and isinstance(name, str):
        parts = name.lower().replace('-', '_').split('_')
        for cand in (parts[0], parts[-1], '_'.join(parts[:2])):
            if cand in SOUNDS or cand in ALIASES:
                got = cand if cand in SOUNDS else ALIASES[cand]
                if name not in _WARNED:
                    print('audio: unknown sound %r -> using %r' % (name, got))
                    _WARNED.add(name)
                return got
    raise KeyError('unknown sound %r; known: %s (aliases: %s)' % (name, ', '.join(SOUNDS), ', '.join(ALIASES)))


def params_of(name):
    """Parameter names (and defaults) accepted by a sound."""
    import inspect
    sig = inspect.signature(SOUNDS[resolve(name)]['fn'])
    return {k: v.default for k, v in sig.parameters.items()}


def _key(params):
    return tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in (params or {}).items()))


@functools.lru_cache(maxsize=160)
def _sound_cached(name, key):
    x = SOUNDS[name]['fn'](**dict(key))
    x.setflags(write=False)
    return x


def sound(name, **params):
    """Cached render of a library sound -> read-only Sfx (float32 (N, 2), .hit). Copy before editing."""
    name = resolve(name)
    acc = params_of(name)
    for a, b in (('dur', 'duration'), ('duration', 'dur')):        # either spelling works everywhere
        if a in params and a not in acc and b in acc:
            params[b] = params.pop(a)
    bad = set(params) - set(acc)
    if bad:
        raise TypeError('%s() got unknown params %s; accepted: %s' % (name, sorted(bad), params_of(name)))
    return _sound_cached(name, _key(params))


def hit_offset(name, **params):
    """Seconds from the start of `name` to its designed hit/peak."""
    return sound(name, **params).hit


def names(category=None):
    return [k for k, v in SOUNDS.items() if category is None or v['category'] == category]


# ============================================================================================ mixer
def _norm_cue(c):
    if isinstance(c, (list, tuple)):
        c = dict(zip(('t', 'name', 'gain_db', 'pan'), c))
    c = dict(c)
    if 'name' not in c and 'sfx' in c:
        c['name'] = c.pop('sfx')
    c.setdefault('gain_db', 0.0)
    c.setdefault('pan', 0.0)
    c.setdefault('align', 'hit')
    c.setdefault('params', {})
    c['name'] = resolve(c['name'])
    return c


def on_beats(name, bpm, beats, offset=0.0, **cue):
    """Cues on a BPM grid: on_beats('whip', 120, range(1, 9), offset=0.45, gain_db=-3) -> list of cue dicts
    with t = offset + beat * 60 / bpm (hit-aligned by default). Extra keys (gain_db, pan, params...) copy into
    every cue; a callable value is called with the beat index (e.g. pan=lambda b: 0.4 * (-1) ** b)."""
    out = []
    for b in beats:
        c = {k: (v(b) if callable(v) else v) for k, v in cue.items()}
        c.update(t=offset + b * 60.0 / bpm, name=name)
        out.append(c)
    return out


def duck_under(cues, window=0.09, strength=0.75, max_cut_db=8.0, under_impact_db=1.5, impact_window=0.35):
    """Auto-gain for dense clusters (returns a NEW cue list; 'duck_db' records the cut applied).
    For each cue, every other cue of equal or higher priority (impact > transition > money > texture > ui)
    whose hit lies within +-window counts as a competitor (weighted by closeness); the cue is cut by
    strength * 10*log10(1 + n) dB (default 0.75: one equal neighbour -> -2.3 dB, three -> -4.5 dB), capped at
    max_cut_db.
    Lower-priority cues whose hit falls within impact_window after an impact's hit lose a further
    under_impact_db so the boom keeps its punch."""
    cs = [_norm_cue(c) for c in cues]
    hits = np.array([float(c['t']) if c['align'] == 'hit' else float(c['t']) + hit_offset(c['name'], **c['params'])
                     for c in cs])
    pr = np.array([_PRIORITY[SOUNDS[c['name']]['category']] for c in cs])
    out = []
    for i, c in enumerate(cs):
        dt = np.abs(hits - hits[i])
        w = np.clip(1 - dt / window, 0, 1)
        w[i] = 0
        n = float(np.sum(w * (pr >= pr[i])))
        cut = min(max_cut_db, strength * 10 * math.log10(1 + n))
        imp = (pr == _PRIORITY['impact']) & (hits <= hits[i]) & (hits[i] - hits <= impact_window)
        imp[i] = False
        if pr[i] < _PRIORITY['impact'] and imp.any():
            cut += under_impact_db
        c2 = dict(c)
        c2['duck_db'] = round(cut, 2)
        c2['gain_db'] = float(c['gain_db']) - cut
        out.append(c2)
    return out


def sidechain(x, key, depth_db=4.0, attack=0.03, release=0.45, thresh_rel_db=-26.0):
    """Duck x under key: gain reduction up to depth_db as the key's 50 ms level rises from
    (key max + thresh_rel_db) to (key max - 6 dB). Smooth attack/release (control-rate one-pole)."""
    k = _mono(np.abs(_st(key)))
    lvl = db(np.sqrt(np.maximum(uniform_filter1d(k ** 2, int(0.05 * SR)), 1e-20)))
    top = np.max(lvl)
    amt = np.clip((lvl - (top + thresh_rel_db)) / (-6.0 - thresh_rel_db), 0, 1)
    gr = _ballistics(-depth_db * amt, attack, release)
    return _st(x) * undb(gr)[:, None]


def _ballistics(target_db, attack, release, block=32):
    """Attack/release smoothing of a gain-reduction curve (dB, <= 0) at a control rate, back to audio rate."""
    n = len(target_db)
    m = (n + block - 1) // block
    tb = np.pad(target_db, (0, m * block - n), mode='edge').reshape(m, block).min(1)
    ca = math.exp(-block / (attack * SR))
    cr = math.exp(-block / (release * SR))
    y = np.empty(m)
    g = 0.0
    for i in range(m):
        v = tb[i]
        g = ca * g + (1 - ca) * v if v < g else cr * g + (1 - cr) * v
        y[i] = g
    xs = (np.arange(m) + 0.5) * block
    return np.interp(np.arange(n), xs, y)


def compressor_gain(x, thresh_db=-16.0, ratio=2.2, knee_db=8.0, attack=0.012, release=0.18, rms=0.012):
    """Gentle bus-glue compressor -> gain curve in dB (<= 0). Feed-forward RMS detector, soft knee."""
    p = np.square(_st(x)).max(1)
    lvl = 10 * np.log10(np.maximum(uniform_filter1d(p, max(1, int(rms * SR))), 1e-20))
    over = lvl - thresh_db
    gr = np.where(over <= -knee_db / 2, 0.0,
                  np.where(over >= knee_db / 2, -(over * (1 - 1 / ratio)),
                           -((1 - 1 / ratio) * (over + knee_db / 2) ** 2 / (2 * knee_db))))
    return _ballistics(gr, attack, release)


def tp_envelope(x):
    """Per-sample true-peak envelope (max |x| over the 4x oversampled neighbourhood of each sample)."""
    x = _st(x)
    n = len(x)
    os_ = np.abs(signal.resample_poly(x, 4, 1, axis=0)).max(1)
    os_ = maximum_filter1d(os_, 9)
    return np.maximum(os_[::4][:n], np.abs(x).max(1))


def limiter_gain(x, ceiling_db=-1.5, lookahead=0.0015, release=0.08, knee_db=1.5, pk=None):
    """True-peak lookahead limiter -> linear gain curve (<= 1). Peaks are detected on the 4x oversampled
    signal (or pass pk = tp_envelope(x) precomputed); soft knee; the gain ramps down over the lookahead so it
    is fully reduced at every peak."""
    if pk is None:
        pk = tp_envelope(x)
    over = db(pk) - ceiling_db
    k = knee_db
    gr = np.where(over <= -k / 2, 0.0, np.where(over >= k / 2, -over, -((over + k / 2) ** 2) / (2 * k)))
    g = undb(gr)
    L = max(2, int(lookahead * SR))
    m = minimum_filter1d(g, L, origin=-(L // 2))          # window [i, i+L-1]: forward-looking min
    s = uniform_filter1d(m, L, origin=(L - 1) // 2)       # backward box: [i-L+1, i]
    s = np.minimum(s, m)
    rel = _ballistics(db(s), 1e-4, release, block=16)
    return np.minimum(s, undb(rel))


def _write_wav(path, x, bits=24):
    x = _st(x)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if bits == 16:
        rng = np.random.default_rng(1)
        tpdf = (rng.random(x.shape) - rng.random(x.shape)) / 32768.0
        q = np.clip(np.round((x + tpdf) * 32767.0), -32768, 32767).astype('<i2')
        raw = q.tobytes()
    else:
        q = np.clip(np.round(x * 8388607.0), -8388608, 8388607).astype('<i4')
        raw = q.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(bits // 8)
        w.setframerate(SR)
        w.writeframes(raw)
    return path


def read_wav(path):
    """Read a 16/24/32-bit PCM WAV -> float64 (N, ch), sample rate."""
    with wave.open(path, 'rb') as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v >= 1 << 23, v - (1 << 24), v)
        x = v / 8388608.0
    elif sw == 2:
        x = np.frombuffer(raw, '<i2') / 32768.0
    else:
        x = np.frombuffer(raw, '<i4') / 2147483648.0
    return x.reshape(-1, ch), sr


def _render_cue(c, rng_vary):
    params = dict(c['params'])
    if 'seed' in c:
        params['seed'] = c['seed']
    elif rng_vary is not None and 'seed' not in params:
        params['seed'] = rng_vary
    x = sound(c['name'], **params)
    hit = x.hit
    y = np.asarray(x, dtype=np.float64)
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


def _beds(bed, dur, N):
    """Build the bed bus at unit reference (each segment at its own loudness REF_LUFS * gain)."""
    if bed is None:
        return None, []
    specs = bed if isinstance(bed, (list, tuple)) else [bed]
    out = np.zeros((N, 2))
    info = []
    for s in specs:
        if isinstance(s, str):
            s = dict(name=s)
        s = dict(s)
        nm = s['name']
        t0, t1 = float(s.get('t0', 0.0)), float(s.get('t1', dur))
        fade = float(s.get('fade', 0.6))
        loop = np.asarray(sound(nm, **s.get('params', {})), dtype=np.float64)
        i0, i1 = _n(max(t0, 0)), min(N, _n(t1))
        if i1 <= i0:
            continue
        off = _n(float(s.get('offset', 0.0))) % len(loop)
        idx = (off + np.arange(i1 - i0)) % len(loop)
        seg = loop[idx] * undb(float(s.get('gain_db', 0.0)))
        seg = _fade(seg, fade if t0 > 0 else min(fade, 0.3), fade)
        out[i0:i1] += seg
        info.append(dict(name=nm, t0=t0, t1=t1, rel_gain_db=float(s.get('gain_db', 0.0))))
    return out, info


def mix(cues, dur, out_wav=None, stem_wav=None, bed=None, bed_gain_db=-30.0, *, target_lufs=-18.0,
        tp_ceiling=-1.5, auto_duck=True, room_send=True, glue=True, vary=True, bits=24, split_stems=False,
        tail_fade=0.4, verbose=True):
    """Mix a cue sheet into a mastered SFX track. Returns a report dict (see module docstring)."""
    N = _n(dur)
    cs = [_norm_cue(c) for c in cues]
    if auto_duck and cs:
        cs = duck_under(cs)
    fx = np.zeros((N, 2))
    send = np.zeros((N, 2))
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], _key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        y, hit = _render_cue(c, (counts[k] % 4) if vary else None)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        _add(fx, y, start)
        cat = SOUNDS[c['name']]['category']
        sdb = c.get('send_db', SOUNDS[c['name']]['send'] if SOUNDS[c['name']]['send'] is not None
                    else _CAT_SEND[cat])
        if room_send and sdb is not None and sdb > -60:
            _add(send, y * undb(sdb), start)
        warn = ''
        if start < -1e-3 and start + hit < 0:
            warn = 'hit before 0 s'
        elif start + len(y) / SR > dur + 0.01:
            warn = 'tail cut at end'
        placed.append(dict(t=float(c['t']), name=c['name'], start=round(start, 4), hit=round(start + hit, 4),
                           len=round(len(y) / SR, 3), gain_db=round(c['gain_db'], 2),
                           duck_db=c.get('duck_db', 0.0), warn=warn))
    if room_send:
        wet = reverb(send, 'studio', wet_db=0.0, dry=0.0)[:N]
        fx += wet
    bedbus, bed_info = _beds(bed, dur, N)
    if tail_fade:
        fx = _fade(fx, 0.003, tail_fade)
    # ---- gain staging: fx to ~target first, bed anchored relative to the target
    g_fx = undb(target_lufs - loudness(fx)) if np.any(fx) else 1.0
    fx *= g_fx
    gr_comp = np.zeros(N)
    if glue and np.any(fx):
        gr_comp = compressor_gain(fx, thresh_db=target_lufs + 8.0, ratio=2.0)
        fx *= undb(gr_comp)[:, None]
    if bedbus is not None:
        if np.any(fx):
            bedbus = sidechain(bedbus, fx, depth_db=5.0)
        if tail_fade:
            bedbus = _fade(bedbus, 0.003, tail_fade)
        bed_ref = loudness(bedbus) if np.any(bedbus) else -120
        bedbus *= undb(target_lufs + bed_gain_db + BED_ANCHOR_DB - bed_ref)
    # ---- loudness normalisation + true-peak limiting. Only the SFX bus gain G is solved (secant iteration) so
    # the bed stays at its anchor; the limiter (gain gl) acts on the sum and is applied to both buses.
    bed0 = bedbus if bedbus is not None else np.zeros_like(fx)
    pk_fx = tp_envelope(fx)
    pk_bed = tp_envelope(bed0) if bedbus is not None else 0.0
    G = 0.0
    ceil = tp_ceiling - 0.2
    def _eval(g, c):
        gl_ = limiter_gain(None, c, pk=pk_fx * undb(g) + pk_bed)
        y_ = (fx * undb(g) + bed0) * gl_[:, None]
        return y_, gl_, loudness(y_)

    for attempt in range(4):
        lo = hi = best = None                       # bracketed regula falsi / bisection on G (loudness is
        for it in range(28):                        # monotonic in G but steps where gated blocks flip)
            y, gl, L1 = _eval(G, ceil)
            if best is None or abs(L1 - target_lufs) < abs(best[2] - target_lufs):
                best = (G, gl, L1, y)
            if abs(L1 - target_lufs) < 0.03 or not np.any(fx):
                break
            if L1 < target_lufs:
                lo = (G, L1)
            else:
                hi = (G, L1)
            if lo and hi:
                if hi[0] - lo[0] < 1e-3:
                    break
                Gn = lo[0] + (target_lufs - lo[1]) * (hi[0] - lo[0]) / max(hi[1] - lo[1], 1e-6)
                G = Gn if (lo[0] + 0.05 * (hi[0] - lo[0]) < Gn < hi[0] - 0.05 * (hi[0] - lo[0]) and it % 3 != 2) \
                    else 0.5 * (lo[0] + hi[0])
            else:
                G += float(np.clip(target_lufs - L1, -24, 24))
        G, gl, L1, y = best
        tp = true_peak(y)
        if tp <= tp_ceiling - 0.05:
            break
        ceil -= tp - (tp_ceiling - 0.1)
    fx_out = fx * (undb(G) * gl)[:, None]
    bed_out = bedbus * gl[:, None] if bedbus is not None else None
    master = fx_out + (bed_out if bed_out is not None else 0.0)
    rep = dict(dur=dur, cues=len(cs), integrated_lufs=round(loudness(master), 2), true_peak_dbtp=round(true_peak(master), 2),
               sample_peak_dbfs=round(float(db(np.max(np.abs(master)))), 2), lra_lu=round(loudness_range(master), 2),
               max_momentary_lufs=round(momentary_max(master), 2), max_short_term_lufs=round(momentary_max(master, 3.0), 2),
               limiter_max_gr_db=round(max(0.0, float(-db(np.min(gl)))), 2), comp_max_gr_db=round(float(-np.min(gr_comp)), 2),
               limiter_pct_over_1db=round(100.0 * float(np.mean(gl < undb(-1.0))), 2),
               bed=bed_info, bed_lufs=round(loudness(bed_out), 2) if bed_out is not None else None,
               placed=placed, files={})
    if out_wav:
        rep['files']['mix'] = _write_wav(out_wav, master, bits)
    if stem_wav:
        rep['files']['stem'] = _write_wav(stem_wav, master, 24)
        if split_stems:
            base = os.path.splitext(stem_wav)[0]
            rep['files']['stem_fx'] = _write_wav(base + '_fx.wav', fx_out, 24)
            if bed_out is not None:
                rep['files']['stem_bed'] = _write_wav(base + '_bed.wav', bed_out, 24)
    rep['audio'] = master.astype(np.float32)
    if verbose:
        print(report_text(rep))
    return rep


BED_ANCHOR_DB = 8.0          # bed integrated loudness in the master = target_lufs + bed_gain_db + 8 (-30 -> -40 LUFS)


def report_text(rep):
    s = ['SFX mix  %.2fs  %d cues' % (rep['dur'], rep['cues']),
         '  integrated %.2f LUFS | true peak %.2f dBTP | sample peak %.2f dBFS | LRA %.1f LU' % (
             rep['integrated_lufs'], rep['true_peak_dbtp'], rep['sample_peak_dbfs'], rep['lra_lu']),
         '  max momentary %.1f LUFS | max short-term %.1f LUFS | limiter max GR %.1f dB (>1 dB for %.2f %% of the '
         'time) | glue max GR %.1f dB' % (rep['max_momentary_lufs'], rep['max_short_term_lufs'], rep['limiter_max_gr_db'],
                                          rep['limiter_pct_over_1db'], rep['comp_max_gr_db'])]
    if rep.get('bed'):
        s.append('  bed: %s  (%.1f LUFS in master)' % (', '.join(b['name'] for b in rep['bed']), rep['bed_lufs']))
    w = [p for p in rep['placed'] if p['warn']]
    for p in w:
        s.append('  WARN %-14s t=%.2f: %s' % (p['name'], p['t'], p['warn']))
    for k, v in rep['files'].items():
        s.append('  %s -> %s' % (k, v))
    return '\n'.join(s)


def build_reel(reel, out_dir=None, **kw):
    """Import pipeline/fostering/<reel>.py and mix its cues(): reads DUR, cues() and optional BED /
    BED_GAIN_DB attributes. Writes AUDIO/<reel>_sfx.wav (muxed by render.py) and AUDIO/<reel>_sfx_stem.wav."""
    import importlib
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    mod = importlib.import_module(reel)
    out_dir = out_dir or AUDIO
    cues = mod.cues()
    bed = kw.pop('bed', getattr(mod, 'BED', None))
    kw.setdefault('bed_gain_db', getattr(mod, 'BED_GAIN_DB', -30.0))
    return mix(cues, float(mod.DUR), os.path.join(out_dir, '%s_sfx.wav' % reel),
               os.path.join(out_dir, '%s_sfx_stem.wav' % reel), bed=bed, **kw)


# ============================================================================================ plotting
_CMAP = np.array([(0, 0, 4), (22, 11, 57), (66, 10, 104), (106, 23, 110), (147, 38, 103), (188, 55, 84),
                  (221, 81, 58), (243, 120, 25), (252, 165, 10), (246, 215, 70), (252, 255, 164)], np.float64)


def _cmap(v):
    v = np.clip(v, 0, 1) * (len(_CMAP) - 1)
    i = np.minimum(v.astype(int), len(_CMAP) - 2)
    f = (v - i)[..., None]
    return (_CMAP[i] * (1 - f) + _CMAP[i + 1] * f).astype(np.uint8)


def _font(size, bold=False):
    from PIL import ImageFont
    for nm in (('Poppins-SemiBold.ttf' if bold else 'Poppins-Regular.ttf'), 'DejaVuSans.ttf'):
        p = os.path.join(FONTS, nm)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def spectro_image(x, w=640, h=300, hit=None, title='', sub='', fmin=30.0, fmax=20000.0, dyn=72.0, tmax=None):
    """PIL image: title, stereo waveform (L up / R down, with RMS) and a log-frequency spectrogram (dB),
    hit marker in cyan. tmax fixes the time axis (s) for side-by-side comparison."""
    from PIL import Image, ImageDraw
    x = _st(np.asarray(x, dtype=np.float64))
    dur = len(x) / SR
    tmax = tmax or dur
    top, wav_h = 44, int(h * 0.26)
    sp_h = h - top - wav_h - 18
    img = Image.new('RGB', (w, h), (14, 10, 18))
    dr = ImageDraw.Draw(img)
    dr.text((8, 4), title, fill=(250, 245, 240), font=_font(17, True))
    dr.text((8, 25), sub, fill=(170, 160, 185), font=_font(12))
    # waveform
    cols = np.minimum((np.arange(len(x)) / SR / tmax * w).astype(int), w - 1)
    x_disp = x / (np.max(np.abs(x)) + 1e-12)
    y0 = top + wav_h // 2
    for c, (sgn, col) in enumerate(((-1, (255, 100, 170)), (1, (255, 150, 80)))):
        a = np.abs(x_disp[:, c])
        mx = np.zeros(w)
        np.maximum.at(mx, cols, a)
        ss = np.zeros(w)
        cnt = np.zeros(w)
        np.add.at(ss, cols, a * a)
        np.add.at(cnt, cols, 1)
        rm = np.sqrt(ss / np.maximum(cnt, 1))
        for i in range(w):
            if mx[i] > 0:
                dr.line([(i, y0), (i, y0 + sgn * mx[i] * (wav_h // 2 - 1))], fill=tuple(int(v * 0.55) for v in col))
                dr.line([(i, y0), (i, y0 + sgn * rm[i] * (wav_h // 2 - 1))], fill=col)
    dr.line([(0, y0), (w, y0)], fill=(60, 50, 70))
    # spectrogram
    m = x.mean(1)
    S = np.abs(_stft(m, 2048, 256)) / 512.0
    T = S.shape[0]
    fr = np.fft.rfftfreq(2048, 1.0 / SR)
    rows = np.exp(np.linspace(math.log(fmax), math.log(fmin), sp_h))
    Sd = 20 * np.log10(S + 1e-9)
    ref = Sd.max()
    Sl = np.empty((T, sp_h))
    for i in range(T):
        Sl[i] = np.interp(rows, fr, Sd[i])
    tcols = np.clip((np.arange(w) / w * tmax * SR / 256).astype(int), 0, None)
    valid = tcols < T
    grid = np.full((sp_h, w), -200.0)
    grid[:, valid] = Sl[tcols[valid]].T
    rgb = _cmap((grid - (ref - dyn)) / dyn)
    sp_top = top + wav_h + 4
    img.paste(Image.fromarray(rgb), (0, sp_top))
    for f in (100, 1000, 10000):
        yy = sp_top + int(np.interp(math.log(f), [math.log(fmin), math.log(fmax)], [sp_h, 0]))
        dr.line([(0, yy), (w, yy)], fill=(90, 90, 110))
        dr.text((3, yy - 13), {100: '100', 1000: '1k', 10000: '10k'}[f], fill=(200, 200, 220), font=_font(10))
    # time ticks
    step = 0.1 if tmax <= 1 else (0.5 if tmax <= 4 else (1.0 if tmax <= 12 else 5.0))
    for k in range(int(tmax / step) + 1):
        xx = int(k * step / tmax * w)
        dr.line([(xx, h - 16), (xx, h - 12)], fill=(150, 150, 170))
        if k % 2 == 0:
            dr.text((xx + 2, h - 15), ('%.1f' % (k * step)).rstrip('0').rstrip('.') + 's', fill=(150, 150, 170),
                    font=_font(10))
    if hit is not None:
        xx = int(hit / tmax * w)
        dr.line([(xx, top), (xx, h - 18)], fill=(80, 230, 255), width=1)
    return img


def catalog_sheets(items, path_fmt, cols=3, per_sheet=15, w=620, h=300):
    """Grid sheets of spectrograms. items: list of (name, Sfx). Returns paths."""
    from PIL import Image
    paths = []
    for s0 in range(0, len(items), per_sheet):
        chunk = items[s0:s0 + per_sheet]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * w + (cols + 1) * 8, rows * h + (rows + 1) * 8), (6, 4, 8))
        for k, (nm, x) in enumerate(chunk):
            st = stats(x, x.hit)
            sub = '%.2fs  pk %.1f dBFS  rms %.1f  crest %.1f dB  Mmax %.1f LUFS  hit %.3fs' % (
                st['dur'], st['peak_db'], st['rms_active_db'], st['crest_db'], st['mmax_lufs'], x.hit)
            im = spectro_image(x, w, h, x.hit, nm + '  [' + SOUNDS[nm]['category'] + ']', sub)
            sheet.paste(im, (8 + (k % cols) * (w + 8), 8 + (k // cols) * (h + 8)))
        p = path_fmt % (s0 // per_sheet + 1)
        sheet.save(p)
        paths.append(p)
    return paths


# ============================================================================================ self-test
_DEMO_PARAMS = {'riser': dict(duration=2.0), 'reverse_swell': dict(duration=1.5), 'typing': dict(n=10),
                'slot_tick': dict(n=16, dur=1.2), 'slider_drag': dict(duration=1.0), 'bar_grow': dict(duration=0.8),
                'grow_swell': dict(duration=2.5), 'room_tone': dict(dur=16.0), 'night_air': dict(dur=20.0),
                'outdoor_birds': dict(dur=24.0)}


def qc(x, hit):
    """Return a list of problems found in a rendered sound (empty = clean)."""
    st = stats(x, hit)
    pr = []
    if not np.all(np.isfinite(x)):
        pr.append('non-finite samples')
    if st['peak_db'] > PEAK_CAP_DB + 0.01:
        pr.append('peak %.2f dBFS above cap' % st['peak_db'])
    if st['edge_start'] > 0.02:
        pr.append('start edge %.3f of peak' % st['edge_start'])
    if st['edge_end'] > 0.002:
        pr.append('end edge %.4f of peak' % st['edge_end'])
    if st['dc'] > 1e-3:
        pr.append('DC %.4f' % st['dc'])
    if hit > st['dur'] + 1e-6:
        pr.append('hit beyond end')
    return pr


def selftest():
    import time
    os.makedirs(SELFTEST, exist_ok=True)
    t0 = time.time()
    items, rows = [], []
    for nm in SOUNDS:
        ts = time.time()
        x = sound(nm, **_DEMO_PARAMS.get(nm, {}))
        el = time.time() - ts
        st = stats(x, x.hit)
        problems = qc(x, x.hit)
        if SOUNDS[nm]['category'] == 'bed':
            # seam check: the jump across the loop boundary vs typical sample-to-sample steps
            a = np.asarray(x, dtype=np.float64)
            seam = np.abs(a[0] - a[-1]).max()
            typ = np.percentile(np.abs(np.diff(a, axis=0)), 99.9)
            st['seam_ratio'] = float(seam / (typ + 1e-12))
            problems = [p for p in problems if 'edge' not in p]
            if st['seam_ratio'] > 1.5:
                problems.append('loop seam %.2f' % st['seam_ratio'])
        items.append((nm, x))
        rows.append((nm, st, problems, el))
    print('%-15s %6s %6s %7s %7s %6s %7s %6s %6s  %s' % ('sound', 'dur', 'hit', 'peak', 'rmsAct', 'crest', 'Mmax',
                                                         'corr', 'ms', 'qc'))
    for nm, st, pr, el in rows:
        print('%-15s %6.2f %6.3f %7.1f %7.1f %6.1f %7.1f %6.2f %6.0f  %s' % (
            nm, st['dur'], st['hit'], st['peak_db'], st['rms_active_db'], st['crest_db'], st['mmax_lufs'],
            st['corr'], el * 1000, ('; '.join(pr) or 'ok') + ('  seam %.2f' % st['seam_ratio']
                                                               if 'seam_ratio' in st else '')))
    sheets = catalog_sheets(items, os.path.join(SELFTEST, 'audio_sheet_%d.png'))
    # catalog demo: every sound in sequence (beds 5 s each, lifted so they can be heard)
    cues, t = [], 0.5
    for nm, x in items:
        if SOUNDS[nm]['category'] == 'bed':
            continue
        cues.append(dict(t=t, name=nm, align='start', params=_DEMO_PARAMS.get(nm, {})))
        t += min(x.dur, 2.6) + 0.55
    beds = []
    for nm in BEDS:
        beds.append(dict(name=nm, t0=t, t1=t + 5.0, gain_db=0.0, params=_DEMO_PARAMS.get(nm, {})))
        t += 5.4
    dur = t + 0.5
    rep = mix(cues, dur, os.path.join(SELFTEST, 'audio_catalog.wav'), os.path.join(SELFTEST, 'audio_catalog_stem.wav'),
              bed=beds, bed_gain_db=-14.0, auto_duck=False, vary=False)
    # demo cue sheet in the style of reel 1's opening (exercise align='hit', ducking and the room bed)
    demo = [dict(t=0.02, name='heartbeat', params=dict(n=1)), dict(t=0.45, name='reverse_swell', params=dict(duration=0.45)),
            dict(t=0.45, name='flash_hit')]
    demo += on_beats('whip', 240, range(1, 9), offset=0.2, gain_db=-3, pan=lambda b: 0.4 * (-1) ** b,
                     params=lambda b: dict(direction=(-1) ** b))
    demo += on_beats('flash_hit', 120, range(1, 4), offset=0.45, gain_db=-4)
    demo += [dict(t=2.45, name='riser', params=dict(duration=1.6)), dict(t=2.45, name='impact_big'),
             dict(t=2.45, name='sub_drop'), dict(t=3.2, name='whoosh_slow'), dict(t=4.0, name='shimmer', gain_db=-2)]
    for k in range(5):
        demo += [dict(t=5.6 + 0.75 * k, name='ui_click'), dict(t=5.62 + 0.75 * k, name='check_ding', gain_db=-2)]
    demo += [dict(t=9.6, name='toast_chime'), dict(t=10.6, name='whoosh_by'), dict(t=12.0, name='riser',
                                                                                     params=dict(duration=2.0)),
             dict(t=12.0, name='logo_sting')]
    rep2 = mix(demo, 18.0, os.path.join(SELFTEST, 'audio_demo_r1.wav'), bed='room_tone', bed_gain_db=-30)
    # cross-check loudness with ffmpeg's ebur128 when available
    ff = _ffmpeg_ebur128(os.path.join(SELFTEST, 'audio_demo_r1.wav'))
    if ff:
        print('ffmpeg ebur128 cross-check (demo): I = %.1f LUFS, true peak = %.1f dBTP' % ff)
    ff2 = _ffmpeg_ebur128(os.path.join(SELFTEST, 'audio_catalog.wav'))
    if ff2:
        print('ffmpeg ebur128 cross-check (catalog): I = %.1f LUFS, true peak = %.1f dBTP' % ff2)
    _mix_overview(rep2, os.path.join(SELFTEST, 'audio_demo_r1.png'), 'demo cue sheet (reel-1 style opening)')
    _mix_overview(rep, os.path.join(SELFTEST, 'audio_catalog.png'), 'audio_catalog.wav (every sound in sequence)')
    bad = [(nm, pr) for nm, st, pr, el in rows if pr]
    print('sheets:', ', '.join(sheets))
    print('QC problems:', bad or 'none', '| %.1fs total' % (time.time() - t0))
    return rep, rep2


def _ffmpeg_ebur128(path):
    import re
    import subprocess
    try:
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null',
                            '-'], capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    txt = r.stderr
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', txt)
    p = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', txt)
    if not i:
        return None
    return float(i[-1]), float(p[-1]) if p else float('nan')


def mix_overview(rep, path, title=''):
    """PNG of a mix() report: spectrogram + waveform + momentary loudness curve (-18 line) + cue hit ticks."""
    return _mix_overview(rep, path, title)


def _mix_overview(rep, path, title):
    from PIL import Image, ImageDraw
    x = rep['audio']
    w = 1600
    im = spectro_image(x, w, 420, None, title, 'I %.2f LUFS  TP %.2f dBTP  LRA %.1f LU  limiter GR %.1f dB' % (
        rep['integrated_lufs'], rep['true_peak_dbtp'], rep['lra_lu'], rep['limiter_max_gr_db']))
    # loudness curve strip
    tt, lc = loudness_curve(x)
    strip = Image.new('RGB', (w, 120), (14, 10, 18))
    dr = ImageDraw.Draw(strip)
    dur = len(x) / SR
    def yv(v):
        return int(np.interp(v, [-60, -6], [115, 5]))
    for lv, col in ((-18, (80, 230, 255)), (-30, (90, 90, 110)), (-45, (60, 60, 80))):
        dr.line([(0, yv(lv)), (w, yv(lv))], fill=col)
        dr.text((4, yv(lv) - 12), '%d' % lv, fill=col, font=_font(10))
    pts = [(int(a / dur * w), yv(b)) for a, b in zip(tt, lc)]
    dr.line(pts, fill=(255, 150, 80), width=2)
    for p in rep['placed']:
        xx = int(p['hit'] / dur * w)
        dr.line([(xx, 0), (xx, 6)], fill=(255, 100, 170))
    out = Image.new('RGB', (w, 540), (6, 4, 8))
    out.paste(im, (0, 0))
    out.paste(strip, (0, 420))
    out.save(path)
    return path


# ============================================================================================ docstring / catalog
def _catalog_rows():
    rows = []
    for nm, meta in SOUNDS.items():
        x = sound(nm, **_DEMO_PARAMS.get(nm, {}))
        rows.append((nm, x.dur, x.hit, meta['category'], meta['character'], meta['use']))
    return rows


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'selftest':
        selftest()
    elif a[0] == 'reel':
        build_reel(a[1])
    elif a[0] == 'mix':
        cues = json.load(open(a[1]))
        mix(cues, float(a[2]), a[3], a[4] if len(a) > 4 else None, bed=(a[5] if len(a) > 5 else None))
    elif a[0] == 'play':
        prm = json.loads(a[2]) if len(a) > 2 else {}
        x = sound(a[1], **prm)
        p = a[3] if len(a) > 3 else os.path.join(SELFTEST, 'audio_%s.wav' % a[1])
        _write_wav(p, x, 24)
        spectro_image(x, 1000, 420, x.hit, a[1], json.dumps(stats(x, x.hit))[:150]).save(p[:-4] + '.png')
        print(p)
    elif a[0] == 'catalog':
        for r in _catalog_rows():
            print('%-15s %5.2fs hit %.3fs  [%s] %s | %s' % r)
