"""log_kya_kahenge_sfx.py - SFX layer of Reel 5 / C15 "Log Kya Kahenge" (the cardboard stadium). Owner: sound-designer.

Binding plan: brand_reels/design/reels/log_kya_kahenge/BRIEF.md r2 section 11 (cue list, local sounds, beds), section 4
(sound rules), sections 5-6 (frame-exact beat table), SLATE section 3.5 (sound motif = the whisper wall; ONE floodlight clunk,
at 25.6 s) and section 5.1 (-14 LUFS, TP <= -2 dBTP, VO >= 8 LU over the bed, <= 3 sounds on one instant, one drop-out at
the reveal). Key from MUSIC_log_kya_kahenge.md: D minor (tonal SFX pitched to D or A). Cue sheet + measurements: SOUND.md
in the same design folder.

What this module owns
    register()          adds the 6 local sounds to audio.SOUNDS (idempotent) + epic_sfx and sfx_jawad
    raw_cues(hook)      the brief's cue list ('A' public hook, 'B' Trial hook), frame-exact, before the VO fit
    cues(hook)          raw_cues -> sfx_jawad.fit_under_vo against the VO word timings (+ the VO audio for the hero test)
    BEDS                exact bed automation (breakpoints, loop positions) for the circular mixer
    mix_loop(...)       a circular version of audio.mix (same chain: duck_under -> studio room send -> glue -> bed,
                        sidechained 5 dB under the SFX -> loudness to -18 LUFS + 4x true-peak limiter), with two
                        differences the brief needs: tails that run past DUR wrap onto t = 0 (the audio loops into frame 0
                        like the picture; no tail fade), and every bed segment sits at its exact level (audio.mix scales
                        the whole bed bus by one integrated measurement and fades every segment edge, which would put a
                        fade at the loop seam and a 0.6 s fade-in on frame 0).
    BED, BED_GAIN_DB    None / -30: audio.mix cannot reproduce these beds. The reel module's cues() stays [] (BRIEF 17.2);
                        render with --no-sfx-build --audio <RW>/audio/log_kya_kahenge_mix.wav (music-supervisor's mix).

Local sounds (each passes audio.qc == [] or, for beds, a seamless-loop check; spectrograms in <RW>/audio/audition/)
    lkk_whisper_wall    bed, 12 s seamless loop: the sound motif. CC0 crowd ambience (crowd_cheer_real's source,
                        OpenGameArt "crowd shouting/speaking ambience" by starninjas) + PD "Ohhh ahhh" (crowd_ahh_real's
                        source, Wikimedia/PDSounds), REVERSED, resampled 4:3 (pitch x0.75 = -4.98 st), band-pass 300-3000 Hz,
                        then granular resynthesis (60 ms Hann grains, 40 grains/s, random read positions, +-3 st) so no word
                        survives; a breath layer (noise band 4.5 kHz, 1 oct, random 5-9 Hz syllabic envelope, depth 0.7) at
                        -8 dB; circular hall reverb. QA: faster-whisper hears no word with probability >= 0.5 (verify).
                        Never crowd_ooh / crowd_ooh_real, never words.
    lkk_whisper_swell   0.6 s swell of the wall's material, hit = the peak at 65 % (0.39 s); its breath layer is lifted to
                        -3 dB so it still reads through the cue's hp 4500 (the VO band stays free).
    lkk_whisper_burst   0.5 s burst of the wall's material (denser grains), hit 0.1 s: one per judgement line.
    lkk_board_flex      cardboard creak, hit = start, 0.35 s: 20-40 stick-slip clicks (resonant 600-1800 Hz, Q 3,
                        spacing 8-25 ms) + a low flex thump (noise 150-400 Hz).
    lkk_ember_crackle   O6 burn (dur), hit = start: crackle (120 grains/s, 1.5-8 kHz) + lognormal pops 6/s + a low roar
                        (noise band 180 Hz, 1.4 oct) at -14 dB (bible 4.8 recipe).
    lkk_flood_hum       bed, 10 s seamless loop: the warm lamp after the clunk. Fundamental f0 = 110 Hz (A2, a chord tone of
                        Bbmaj7 / F/A / Dm(add9)) + 2-4 f0 at -6/-12/-18 dB, 0.3 Hz wobble. The brief's 100 Hz sits between
                        G2 and Ab2 and rubs the A2/Bb2 pads (music map); the agent rule is "pitch tonal SFX into the key".
    The clunk is a cue stack (ui_click + impact_soft + sub_drop), not a sound.

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
    python3 log_kya_kahenge_sfx.py cues [--hook A|B]      cue table after the VO fit (which VO was used)
    python3 log_kya_kahenge_sfx.py audition               local sounds -> <RW>/audio/audition/*.wav + .png + qc
    python3 log_kya_kahenge_sfx.py build [--hook A|B|AB]  SFX stem(s) -> <RW>/audio/log_kya_kahenge[_hookb]_sfx_stem.wav
                                                          (+ _sfx.wav, _sfx_stem_fx.wav / _bed.wav, _sfx_overview.png,
                                                          _cues.json, _sfx_report.json); -18 LUFS, TP <= -2.0 dBTP, loop-exact
    python3 log_kya_kahenge_sfx.py rough [--hook A|B|AB]  epic_mix (VO + SFX stem + music_full.wav) -> <RW>/audio/
                                                          log_kya_kahenge[_hookb]_rough_*.wav/.json/.png + measurements
    python3 log_kya_kahenge_sfx.py verify                 whisper-wall ASR test (faster-whisper small + medium)

VO source (cues / rough): the real stems <RW>/vo/lkk_vo_<A|B>.wav + .words.json (vo_stem.wav / words.json = A) when they
exist; else the labelled STAND-IN <RW>/audio/standin_vo/ (Kokoro hm_psi scratch reads assembled by log_kya_kahenge_vo.py:
NOT the VO, used only to prove the mix chain); else the brief's planned windows (section 9). Re-run build + rough when the
real VO lands: the cue ducking follows the measured words.
"""
import argparse
import functools
import json
import math
import os
import subprocess
import sys

import numpy as np
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE ends up first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import audio as A  # noqa: E402
from audio import (SR, _t, _n, _rng, _st, _ar, _fade, _taper, _finish, _bed_finish, _crackle,  # noqa: E402
                   _loop_mask_noise, _periodic_lfo, noise_band, lp, hp, bp, reson, pan, undb, db)
import epic_sfx as ES  # noqa: E402  (shared, read-only: braam + crowd sample registry)
import sfx_jawad as SJ  # noqa: E402  (shared, read-only: fit_under_vo, hero_slots)

MODULE = 'log_kya_kahenge'
DUR, BPM, FPS = 35.2, 75.0, 30
N = _n(DUR)
assert N == 1689600
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
VO_DIR = os.path.join(RW, 'vo')
STANDIN = os.path.join(AUD, 'standin_vo')
MUSIC = os.path.join(RW, 'music', 'music_full.wav')
MUSIC_JSON = os.path.join(RW, 'music', 'music_full.json')
LIB = os.path.join(SFXDIR, 'library')
SRC_CACHE = os.path.join(AUD, 'src')
HERO_CARVE_DB = -10.0                          # hero tails under later speech (VO-first: >= 6 LU under the words)
HERO_CARVE_BRIDGE = 1.0                        # ... held through pauses shorter than this (no tail pumping in a line)
TARGET_LUFS, TP_CEILING = -18.0, -2.0          # SFX stem (bible 4.1); the final mix is -14 / -2.0 (epic_mix)
BED, BED_GAIN_DB = None, -30.0                 # see module docstring: use `build`, never audio.mix, for this reel


def F(f):
    """Reel time of frame f (30 fps)."""
    return f / FPS


# ======================================================================================== key (MUSIC_log_kya_kahenge.md)
# measured dominant partials (bible 4.2 f0_of): glass_tap 2096.3 Hz (C7 +3c), ui_click 1653.6 Hz (G#6 -8c),
# ui_tick 3788.4 Hz (A#7 +27c). Targets: D7 2349.32 Hz, A5 880.00 Hz (ui_click slowed by `rate`, as the brief's 0.55),
# A7 3520.00 Hz.
GLASS_PITCH = round(2349.32 / 2096.3, 4)       # 1.1207 -> D7 (end-card glass tap)
CLICK_RATE = round(880.00 / 1653.6, 4)         # 0.5322 -> A5 (the clunk's transient; brief rate 0.55 = A5 +57c)
TICK_PITCH = round(3520.00 / 3788.4, 4)        # 0.9292 -> A7 (scroller taps)
HUM_F0 = 110.0                                 # A2 (see lkk_flood_hum)


# ======================================================================================== source samples (CC0 / PD)
SRC = dict(
    crowd_cheer=('opengameart/crowd_shouting/crowd_shouting_0.ogg',
                 'CC0 - "Crowd shouting/speaking ambience" by starninjas (OpenGameArt); = crowd_cheer_real source'),
    crowd_ahh=('wikimedia/crowd/Ohhh_ahhh.ogg',
               'public domain - "Ohhh ahhh" by starlite (PDSounds, Wikimedia Commons); = crowd_ahh_real source'),
)


def _src(key):
    """Decode a library file (untrusted data: ffmpeg only) to a cached 48 kHz stereo 24-bit wav -> float64 (N, 2)."""
    rel = SRC[key][0]
    src = os.path.join(LIB, rel)
    dst = os.path.join(SRC_CACHE, key + '.wav')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        os.makedirs(SRC_CACHE, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_s24le', dst],
                       check=True)
    return _st(A.read_wav(dst)[0])


@functools.lru_cache(maxsize=1)
def _wall_material():
    """The processed whisper-wall sources: reversed, pitch x0.75 (resample 4:3), band-pass 300-3000 Hz, unit RMS over
    their active part. Returns (cheer, ahh) float64 (N, 2), read-only."""
    out = []
    for key in ('crowd_cheer', 'crowd_ahh'):
        x = _src(key)
        x = x - x.mean(0)
        x = x[::-1].copy()                                  # reversed
        x = signal.resample_poly(x, 4, 3, axis=0)           # 4/3 longer at SR: pitch x0.75 (-4.98 semitones)
        x = bp(x, 300.0, 3000.0, 2)                         # band-pass 300-3000 Hz
        a = np.abs(x).max(1)
        act = a > 0.05 * a.max()
        x = x / (np.sqrt(np.mean(np.square(x[act]))) + 1e-12)
        x.setflags(write=False)
        out.append(x)
    return tuple(out)


def _grain_cloud(d, r, rate, glen=0.06, semis=3.0, circular=True, share_ahh=0.25, spread=0.7, amp=None):
    """Granular resynthesis of the wall material: `rate` grains/s of `glen` s (Hann), random read positions, each grain
    pitched by a random +-`semis` semitones (resampled read), random pan. circular=True wraps grains around the end (a
    seamless loop of length d). amp(p) -> per-grain gain by position p = t/d (for swells and bursts)."""
    cheer, ahh = _wall_material()
    L = _n(d)
    G = _n(glen)
    out = np.zeros((L, 2))
    win = np.hanning(G)
    n = int(round(rate * d))
    for k in range(n):
        src = ahh if r.random() < share_ahh else cheer
        ratio = 2.0 ** (r.uniform(-semis, semis) / 12.0)
        need = int(math.ceil(G * ratio)) + 2
        p0 = int(r.integers(0, len(src) - need - 1))
        pos = p0 + np.arange(G) * ratio
        i = pos.astype(int)
        fr = (pos - i)[:, None]
        g = (src[i] * (1 - fr) + src[i + 1] * fr) * win[:, None]
        g = pan(g.mean(1), r.uniform(-spread, spread)) * r.uniform(0.5, 1.0)
        t0 = int(r.integers(0, L)) if circular else int(r.integers(0, max(1, L - G)))
        if amp is not None:
            g = g * amp((t0 + G / 2) / L)
        if circular:
            idx = (t0 + np.arange(G)) % L
            np.add.at(out, idx, g)
        else:
            out[t0:t0 + G] += g[:min(G, L - t0)]
    return out


def _syllabic(L, r, lo=5.0, hi=9.0, depth=0.7, circular=True):
    """Random syllabic envelope: back-to-back sin^2 pulses of 1/U(lo, hi) s with random heights; 1 - depth .. 1."""
    env = np.zeros(L)
    t = 0
    while t < L + _n(0.3):
        d = _n(1.0 / r.uniform(lo, hi))
        h = r.uniform(0.25, 1.0)
        pulse = h * np.sin(np.pi * np.arange(d) / d) ** 2
        idx = (t + np.arange(d))
        if circular:
            np.add.at(env, idx % L, pulse)
        else:
            m = idx < L
            env[idx[m]] += pulse[m]
        t += d
    env = np.minimum(env, 1.0)
    return (1.0 - depth) + depth * env


def _breath(d, r, circular=True):
    """Breath / sibilance layer: noise band fc 4500 Hz, 1 octave, with the syllabic envelope (unit RMS before env)."""
    L = _n(d)
    if circular:
        def mask(tl, f):
            return np.exp(-0.5 * (np.log2(np.maximum(f, 20.0) / 4500.0) / 1.0) ** 2)[None, :] * np.ones((len(tl), 1))
        x = _loop_mask_noise(L, r, mask, chans=2, corr=0.3)
    else:
        x = _st(noise_band(d, r, 4500.0, 1.0, width=0.7))
    x = x / (np.sqrt(np.mean(np.square(x))) + 1e-12)
    return x * _syllabic(L, r, circular=circular)[:, None]


def _rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-30))


# ======================================================================================== local sounds
def lkk_whisper_wall(seed=0, dur=12.0):
    """The whisper wall: seamless `dur` s loop (see module docstring). Bed: -20 LUFS integrated, hit 0."""
    r = _rng(seed, 'lkk_whisper_wall')
    L = _n(dur)
    gran = _grain_cloud(dur, r, 40.0, circular=True)                # 60 ms grains, 40/s, +-3 st
    cheer = _wall_material()[0]
    i0 = _n(4.0)
    cont = ES._loopify(cheer[i0:i0 + L + _n(1.0)], L, _n(1.0))      # continuous reversed layer, 1 s loop crossfade
    body = 0.8 * gran / (_rms(gran) + 1e-12) + 0.45 * cont / (_rms(cont) + 1e-12)
    br = _breath(dur, r, circular=True)
    x = body + br * undb(-8.0) * _rms(body)
    tl = np.arange(L) / SR
    x *= (1.0 + 0.15 * _periodic_lfo(tl, dur, r, 3))[:, None]       # slow breathing of the crowd (periodic)
    x = A.reverb_circular(x, 'hall', wet_db=-8.0)                    # the amphitheatre (tail wraps: loop-safe)
    return _bed_finish(x, 'lkk_whisper_wall')


def _wall_hit(name, seed, dur, hit, rate, breath_db, env_fn, level, tail=0.6):
    """Shared builder for the swell and the burst: grains of the wall material + breath under an envelope, short hall."""
    r = _rng(seed, name)
    L = _n(dur)
    tt = np.arange(L) / SR
    env = env_fn(tt)
    gran = _grain_cloud(dur, r, rate, circular=False, amp=lambda p: env[min(L - 1, int(p * L))])
    br = _breath(dur, r, circular=False) * env[:, None]
    x = gran / (_rms(gran) + 1e-12) + br / (_rms(br) + 1e-12) * undb(breath_db)
    x = x * env[:, None] / (np.max(env) + 1e-12)
    x = _fade(x, 0.002, 0.02)
    x = x / (np.max(np.abs(x)) + 1e-12)
    x = x * A.limiter_gain(x, -5.0, release=0.04)[:, None]   # grain-sum spikes: peak-to-loudness down by <= 5 dB
    x = np.concatenate([x, np.zeros((_n(tail), 2))])
    x = A.reverb(x, 'hall', wet_db=-10.0)[:len(x)]
    x = _fade(x, 0.0, 0.08)
    return _finish(x, hit, level, name, keep_until=dur + tail * 0.5)


def lkk_whisper_swell(seed=0, dur=0.6):
    """Whisper swell: power rise to the peak at 65 % of dur (the hit), fast fall. Breath layer at -3 dB (reads in hp 4500)."""
    hp_ = 0.65 * dur

    def env(t):
        u = np.clip(t / hp_, 0, 1)
        return np.where(t < hp_, u ** 2.2, np.exp(-(t - hp_) / (0.33 * (dur - hp_))))
    return _wall_hit('lkk_whisper_swell', seed, dur, hp_, 90.0, -3.0, env, -4.0)


def lkk_whisper_burst(seed=0, dur=0.5):
    """Whisper burst: a crowd of whispers rising in 0.1 s (hit) and falling over the rest of dur."""
    h = 0.1

    def env(t):
        rise = 0.5 - 0.5 * np.cos(np.pi * np.clip(t / h, 0, 1))
        return np.where(t < h, rise, np.exp(-(t - h) / (0.35 * (dur - h))))
    return _wall_hit('lkk_whisper_burst', seed, dur, h, 140.0, -6.0, env, -2.0)


def lkk_board_flex(seed=0, dur=0.35):
    """Cardboard creak (hit = start): stick-slip clicks through resonances 600-1800 Hz (Q 3) + a low flex thump."""
    r = _rng(seed, 'lkk_board_flex')
    D = dur + 0.3
    L = _n(D)
    x = np.zeros(L)
    t, k, nmax = 0.0, 0, int(r.integers(20, 41))
    while t < dur * 0.97 and k < nmax:
        p = t / dur
        a = (np.sin(np.pi * min(p * 1.15, 1.0)) ** 0.6 + 0.15) * r.lognormal(0.0, 0.35)
        kl = int(r.integers(12, 40))                                  # 0.25-0.8 ms of rough contact
        imp = np.zeros(_n(0.03))
        imp[:kl] = r.standard_normal(kl) * np.hanning(kl)
        y = reson(imp, r.uniform(600.0, 1800.0), 3.0) + 0.35 * reson(imp, r.uniform(2200.0, 3200.0), 6.0)
        i = _n(t)
        m = min(len(y), L - i)
        x[i:i + m] += a * y[:m]
        t += r.uniform(0.008, 0.025)
        k += 1
    tt = _t(D)
    thump = bp(r.standard_normal(L), 150.0, 400.0, 2) * _ar(tt, 0.018, 0.11)
    x = x / (np.max(np.abs(x)) + 1e-12) + 0.55 * thump / (np.max(np.abs(thump)) + 1e-12)
    st = np.stack([x, 0.85 * x + 0.15 * np.roll(x, 37)], 1)
    st = A.reverb(_taper(st, 0.25), 'room', wet_db=-16.0)
    return _finish(st, 0.0, -6.0, 'lkk_board_flex')


def lkk_ember_crackle(seed=0, dur=1.6):
    """O6 ember crackle (hit = start; cue align='start' with dur = the burn): crackle + lognormal pops 6/s + low roar."""
    r = _rng(seed, 'lkk_ember_crackle')
    L = _n(dur)
    tt = np.arange(L) / SR

    def shape(p):                                     # the burn builds to the erosion's end (0.75 of the window), dies
        return np.clip(p / 0.02, 0, 1) ** 1.5 * np.where(p < 0.75, 0.55 + 0.45 * p / 0.75,
                                                       np.exp(-(p - 0.75) / 0.12))
    cr = A._crackle(dur, r, 120.0, lo=1500.0, hi=8000.0, env=shape, gdur=(0.0005, 0.003))
    pops = np.zeros((L, 2))
    n = int(r.poisson(6.0 * dur))
    for _ in range(n):
        t0 = r.uniform(0.0, dur * 0.9)
        gl = r.uniform(0.002, 0.006)
        seg = _t(gl * 4)
        e = _ar(seg, 0.0003, gl)
        y = bp(r.standard_normal(len(seg)), 800.0, 5000.0, 2) * e * r.lognormal(0.0, 0.7)
        y = _taper(y, 0.3)
        A._add(pops, pan(y, r.uniform(-0.6, 0.6)), t0)
    pops *= shape(tt / dur)[:, None]
    roar = _st(noise_band(dur, r, 180.0, 1.4, width=0.5)) * shape(tt / dur)[:, None]
    x = cr / (_rms(cr) + 1e-12) + 0.8 * pops / (_rms(pops) + 1e-12) + undb(-14.0) * roar / (_rms(roar) + 1e-12)
    x = _fade(x, 0.003, 0.25)
    x = A.reverb(x, 'room', wet_db=-14.0)
    return _finish(x, 0.0, -10.0, 'lkk_ember_crackle', fin=0.003)


def lkk_flood_hum(seed=0, dur=10.0, f0=HUM_F0):
    """The warm lamp: seamless `dur` s loop, hum at f0 (integer cycles) + 2/3/4 f0 at -6/-12/-18 dB, 0.3 Hz wobble."""
    r = _rng(seed, 'lkk_flood_hum')
    L = _n(dur)
    t = np.arange(L) / SR
    f = ES._cycles(f0, dur)
    fw = ES._cycles(0.3, dur)
    ph = 2 * np.pi * f * t + 0.5 * np.sin(2 * np.pi * fw * t + r.uniform(0, 6.28))       # periodic pitch wobble
    x = sum(undb(g) * np.sin(k * ph + r.uniform(0, 6.28)) for k, g in ((1, 0.0), (2, -6.0), (3, -12.0), (4, -18.0)))
    x *= 1.0 + 0.10 * np.sin(2 * np.pi * fw * t + r.uniform(0, 6.28))
    st = np.stack([x, x], 1)

    def mask(tl, ff):
        return (np.exp(-0.5 * (np.log2(np.maximum(ff, 20.0) / 2600.0) / 0.6) ** 2))[None, :] * np.ones((len(tl), 1))
    buzz = _loop_mask_noise(L, r, mask, chans=2, corr=0.6)
    st = st + undb(-30.0) * buzz / (_rms(buzz) + 1e-12) * _rms(st)
    st = A.reverb_circular(st, 'room', wet_db=-14.0)
    return _bed_finish(st, 'lkk_flood_hum')


META = dict(   # name: (category, character, use)
    lkk_whisper_wall=('bed', 'wordless whisper wall: reversed, pitched-down, band-passed CC0/PD crowd, granular, breath',
                      'C15 sound motif (the judging crowd), seamless 12 s loop'),
    lkk_whisper_swell=('texture', 'whisper-wall swell, peak at 65 %', 'C15 head-snap wave'),
    lkk_whisper_burst=('texture', 'whisper-wall burst, 0.1 s rise', 'C15 judgement lines'),
    lkk_board_flex=('impact', 'cardboard creak: stick-slip clicks 600-1800 Hz + low flex thump', 'C15 cards flexing'),
    lkk_ember_crackle=('texture', 'ember crackle + pops + low roar (align start)', 'C15 O6 burn of the card layer'),
    lkk_flood_hum=('bed', 'floodlight ballast hum at A2 + harmonics, 0.3 Hz wobble', 'C15 warm lamp after the clunk'),
)
LOCAL = tuple(META)


def register():
    """Register epic_sfx (braam, crowd samples), sfx_jawad (fit_under_vo needs it) and this reel's sounds. Idempotent."""
    ES.register()
    SJ.register()
    changed = False
    for n, (cat, ch, use) in META.items():
        fn = globals()[n]
        cur = A.SOUNDS.get(n)
        if cur is not None and cur['fn'] is fn:
            continue
        A._register(cat, ch, use)(fn)
        changed = True
    if changed:
        A._sound_cached.cache_clear()
    return list(META)


# ======================================================================================== the cue list (BRIEF r2 section 11)
def raw_cues(hook='A'):
    """Cue list before the VO fit. Every time is a frame of the brief's beat table (t = f / 30) unless the brief gives a
    sub-frame lead (the clunk transient 3 ms early). Extra keys: ev (the visual event), hero (VO-clearance check)."""
    c = []

    def add(t, name, gain_db, ev, **kw):
        c.append(dict(t=round(float(t), 4), name=name, gain_db=float(gain_db), ev=ev, **kw))

    # 1 frame 0 (shared by both hooks): the loop landing; the end card's reverse swell ends on it (DUR == 0.0)
    add(0.0, 'impact_soft', -6, 'f0: loop landing, frame-0 transient', lp=1100)
    if hook == 'A':                                                    # 2-4 hook A head-snap (section 6.1)
        add(F(9), 'swish_small', -14, 'f9: head-snap wave (air)', hp=5500)
        add(F(12), 'lkk_whisper_swell', -8, 'f12: whisper swell peaks on the snap', hp=4500)
        add(F(18), 'shimmer', -12, 'f18: wave complete, hook text readable', hp=5500)
    else:                                                              # hook B (section 6.2, Trial, frames 0-89)
        add(F(6), 'swish_small', -14, 'f6: head-snap wave starts (135 mm rows)', hp=5500)
        add(F(12), 'lkk_whisper_swell', -8, 'f12: whisper swell peaks (last heads start)', hp=4500)
        add(F(18), 'shimmer', -12, 'f18: wave complete', hp=5500)
        add(F(72), 'whoosh_slow', -12, 'f72: O2 smoke wipe c (135 mm -> wide)', lp=1100)
        add(F(84), 'impact_soft', -10, 'f84: O2 clears to the wide')
    # 5-6 judgement lines, accelerating (r2): bursts on the line starts, whoosh_by 2 f before each hold depth
    for k, (fs, fp, g, d) in enumerate(zip((96, 144, 180, 216), (104, 150, 184, 220), (-10, -8, -6, -4),
                                           (0.6, 0.5, 0.4, 0.4))):
        add(F(fs), 'lkk_whisper_burst', g, 'f%d: J%d flies out of the crowd' % (fs, k + 1), sat=2.0)
        add(F(fp), 'whoosh_by', -12, 'f%d: J%d fly-in pass (hold depth f%d)' % (fp, k + 1, fp + 2), lp=4000,
            params=dict(dur=d, direction=1))
    add(F(288), 'whoosh_slow', -12, 'f288: O2 smoke wipe c (S2 -> S3, under V2)', lp=1100)          # 7
    add(F(306), 'impact_soft', -16, 'f306: O2 clears (JD alone)', lp=1100)                          # 8
    add(F(384), 'lkk_board_flex', -14, 'f384: heads tilt 9 deg in sync (first cardboard hint)', lp=1100,
        align='start')                                                                              # 9
    add(F(384), 'impact_soft', -16, 'f384: L3 cut to the 135 mm rows', lp=1100)                     # 10
    add(F(456), 'reverse_swell', -8, 'f456: the suck into the drop-out (ends here)', lp=1100,
        params=dict(duration=round(11 / FPS, 5)), send_db=-120.0)                                   # 11 (no room tail)
    add(F(468), 'heartbeat', -12, 'f468: held breath in the drop-out: lub f468, dub f474 (16th grid)', lp=900,
        params=dict(n=1, bpm=130.4))    # 12: bpm only sets the lub-dub gap (0.29 * sqrt(62 / bpm) = 0.200 s); at the
    #                                     default 62 the dub fell at 15.90-15.96, a 40-100 ms flam before the reveal
    # 13-14 the reveal (brief: braam 0 / impact_big -2 on f480). Measured changes, all for VO-first and the limiter:
    #   impact_big: transient ON f480; tail 0.6 (shorter hall/rumble) + 'sat' 4 (loudness-matched, alias-safe
    #     saturation: peak-to-loudness 9.9 -> ~3 dB; with tail 0.6 its 0.4-3 s decay stays within ~2 dB of the raw sound)
    #   braam: align START 10 ms after the transient (bible 4.2: the transient leads, the body follows; its own hit
    #     0.04 would open f479 and its onset thump stacked on the impact's punch), dur 1.6 (brief 3.2: a 1.4 s full-level
    #     hold sat ~1 LU under V3's first words and moved the reel's max momentary to 16.9-17.7 s), 'sat' 4
    #   both tails are carved -6 dB under later speech (cues(): HERO_CARVE_DB). Stem limiter max GR 8.2 dB -> ~2.8 dB
    #   (+10 ms keeps the braam's blat peak, its designed hit at +40 ms, >= 300 ms clear of V3 at 16.367: fit_under_vo).
    add(F(480), 'impact_big', -2, 'f480: REVEAL transient + body + hall tail (loudest moment)', hero=True, sat=4.0,
        params=dict(tail=0.6))
    add(F(480) + 0.010, 'braam', 0, 'f480: REVEAL braam (+10 ms), orbit already moving', hero=True, align='start',
        sat=4.0, params=dict(root=36.71, dur=1.0))
    add(F(528), 'lkk_board_flex', -16, 'f528: cards flexing mid-orbit (backs, tape, struts)', lp=1100,
        align='start')                                                                              # 15
    add(F(576), 'whoosh_slow', -12, 'f576: edge-on pass, the single image', lp=1100)                # 16
    for fr in (648, 654, 660):                                                                      # 17
        add(F(fr), 'ui_tick', -20, 'f%d: scroller tap (screen x ~600)' % fr, hp=5500, pan=0.1,
            params=dict(pitch=TICK_PITCH))
    add(F(672), 'lkk_ember_crackle', -12, 'f672: O6 erosion starts (card layer, btt)', hp=5000, align='start',
        params=dict(dur=1.6))                                                                       # 18
    add(F(690), 'whoosh_slow', -14, 'f690: O6 midpoint', lp=1100)                                   # 19
    add(F(708), 'impact_soft', -8, 'f708: O6 complete (inside V5 pause)', lp=1100)                  # 20
    add(F(708), 'sub_drop', -10, 'f708: O6 complete, sub', lp=120, params=dict(dur=1.0))            # 21
    add(F(768), 'reverse_swell', -10, 'f768: into the payoff (ends here)', lp=1100,
        params=dict(duration=0.2))                                                                  # 22
    add(F(768) - 0.003, 'ui_click', -6, 'f768: THE floodlight clunk, transient (leads 3 ms)', hero=True,
        rate=CLICK_RATE)                                                                            # 23
    add(F(768), 'impact_soft', 0, 'f768: clunk body, warm light on', lp=2500, hero=True)            # 24
    add(F(768), 'sub_drop', -6, 'f768: clunk sub (the one clunk)', lp=120, hero=True,
        params=dict(dur=1.0))                                                                       # 25
    add(F(775), 'shimmer', -12, 'f775: keyword busy rises', hp=5500)                                # 26
    add(F(785), 'swish_small', -16, 'f785: underline draws (under V6)', hp=5500, align='start')     # 27
    add(F(864), 'impact_soft', -12, 'f864: L3 cut to the warm wide', lp=1100)                       # 28
    add(F(876), 'swish_small', -16, 'f876: the last card starts to fall (screen x ~820)', hp=5500, align='start',
        pan=0.35)                                                                                   # 29
    add(F(888), 'card_slide', -8, 'f888: THE TAP, the last card lands', hero=True, pan=0.35)        # 30
    add(F(888), 'impact_soft', -14, 'f888: tap body', lp=900, hero=True, pan=0.35)                  # 31
    for cc in _endcard_cues():                                                                      # 32
        c.append(cc)
    for fr, rows in zip((967, 982, 996, 1011), ('0-1', '3-4', '6-7', '9')):                         # 33
        add(F(fr), 'card_slide', -22, 'f%d: flaps rise, rows %s land' % (fr, rows), lp=2000)
    return c


@functools.lru_cache(maxsize=1)
def _endcard_cues_raw():
    import endcard as E                                   # lazy: endcard imports jawad_kit (fonts)
    card = E.EndCard('US DOST KO', 'bhejo', sub="jise 'log' ka darr rokta hai", monogram='JD', dur=4.0)
    return json.dumps(card.cues(31.2, DUR))


def _endcard_cues():
    """card.cues(31.2, DUR) from the shared EndCard (+ the glass tap pitched to D7, air sounds hp 5500 under V7)."""
    ev = {'swish_small': 'f939: end card, monogram ring draws', 'glass_tap': 'f958: monogram lands',
          'shimmer': 'f953: CTA keyword bhejo rises', 'reverse_swell': 'f1056 = f0: audio loop swell into frame 0'}
    out = []
    for c in json.loads(_endcard_cues_raw()):
        c = dict(c)
        c['ev'] = ev.get(c['name'], 'end card')
        if c['name'] == 'glass_tap':
            c['params'] = dict(c.get('params', {}), pitch=GLASS_PITCH)
        out.append(c)
    return out


# ======================================================================================== beds (exact automation)
# Levels in the brief's BED_GAIN_DB scale (-30 = felt): a bed segment at level L sits at TARGET + L + 8 LUFS in the stem
# (audio.mix's anchor), i.e. its loop (-20 LUFS) plays at gain L + 10 dB. keys = [(t, level | None)] breakpoints,
# linear amplitude between them, silent outside; loop position = (t - loop_ref) mod loop length.
WALL_LOOP = 12.0
BEDS = [
    dict(name='lkk_whisper_wall', loop_ref=0.0,
         keys=[(0.0, -24), (3.05, -24), (3.35, -20), (5.85, -20), (6.15, -18), (8.65, -18), (8.95, -26),
               (F(456) - 0.004, -26), (F(456), None)],
         why='the judging crowd: steps up with J1 (3.2) and J3 (6.0), under V2 at -26, cut dead at 15.2 (drop-out)'),
    dict(name='room_tone', loop_ref=0.0,
         keys=[(F(456) - 0.004, None), (F(456), -40), (15.95, -40), (16.0, -34), (33.6, -34), (DUR, None)],
         why='drop-out floor at -40 (15.2-16.0), then the open stadium at -34; hands back to the wall over 33.6-35.2'),
    dict(name='lkk_flood_hum', loop_ref=25.65,
         keys=[(25.65, None), (25.9, -30), (33.6, -30), (35.0, None)],
         why='the warm lamp after the clunk (fade in 0.25 s, out 1.4 s from 33.6)'),
    dict(name='lkk_whisper_wall', loop_ref=DUR,
         keys=[(33.6, None), (DUR, -24)],
         why='the wall returns for the loop: loop position 0 at 35.2 = frame 0 (equal level and sample at the seam)'),
]


def _bed_bus(beds=BEDS, dur=DUR, target=TARGET_LUFS):
    Nn = _n(dur)
    t = np.arange(Nn) / SR
    out = np.zeros((Nn, 2))
    info = []
    for b in beds:
        loop = np.asarray(A.sound(b['name']), dtype=np.float64)
        ks = b['keys']
        tk = np.array([k[0] for k in ks])
        ak = np.array([0.0 if k[1] is None else float(undb(target + k[1] + 8.0 - A.REF_LUFS)) for k in ks])
        i0, i1 = _n(max(0.0, tk[0])), min(Nn, _n(tk[-1]) + 1)
        g = np.interp(t[i0:i1], tk, ak, left=0.0, right=0.0)
        pos = (np.arange(i0, i1) - _n(b['loop_ref'])) % len(loop)
        out[i0:i1] += loop[pos] * g[:, None]
        info.append(dict(name=b['name'], t0=float(tk[0]), t1=float(tk[-1]),
                         levels=[k[1] for k in ks if k[1] is not None], why=b.get('why', '')))
    return out, info


# ======================================================================================== VO source + fit
PLANNED = {   # BRIEF r2 section 9 windows (fallback only when no VO stem exists)
    'A': [(0.100, 2.700), (8.800, 14.833), (16.367, 17.900), (18.200, 19.133), (19.333, 22.300), (22.400, 23.467),
          (23.667, 25.400), (26.000, 29.100), (31.600, 35.100)],
}
PLANNED['B'] = PLANNED['A']


def vo_source(hook='A'):
    """The VO used for the fit and the rough mix: dict(words, wav, kind = real | standin | planned)."""
    cand = []
    if hook == 'A':
        cand.append((os.path.join(VO_DIR, 'words.json'), os.path.join(VO_DIR, 'vo_stem.wav'), 'real'))
    cand.append((os.path.join(VO_DIR, 'lkk_vo_%s.words.json' % hook), os.path.join(VO_DIR, 'lkk_vo_%s.wav' % hook),
                 'real'))
    cand.append((os.path.join(STANDIN, 'lkk_vo_%s.words.json' % hook), os.path.join(STANDIN, 'lkk_vo_%s.wav' % hook),
                 'standin'))
    for w, a, kind in cand:
        if os.path.exists(w) and os.path.exists(a):
            return dict(words=w, wav=a, kind=kind)
    return dict(words=PLANNED[hook], wav=None, kind='planned')


def cues(hook='A', vo=None, report=False):
    """The cue sheet after sfx_jawad.fit_under_vo (bible 4.1): detail cues on a word -6 dB (air hp 5500, dark lp 1100,
    mid -8 dB), spans over speech -6 dB + lp 1100; HERO cues (braam, impact_big, the clunk stack, the tap) must have
    120 ms of no speech before and 300 ms after (150 ms for non-impacts), else HeroOnWordError."""
    register()
    src = vo or vo_source(hook)
    out, rep = SJ.fit_under_vo(raw_cues(hook), src['words'], vo_audio=src['wav'], hero='raise', report=True)
    # hero tails: the hit is clear of speech (checked above), but braam / impact_big / the clunk ring on for seconds;
    # carve HERO_CARVE_DB out of each hero cue while later speech is active (word windows padded 60 ms)
    rep['carved'] = []
    for c in out:
        if c.get('hero'):
            x = A.sound(c['name'], **c['params'])
            rate = float(c.get('rate', 1.0))
            start = float(c['t']) - (x.hit / rate if c['align'] == 'hit' else 0.0)
            hit, end = start + x.hit / rate, start + len(x) / SR / rate
            wins = []                                       # speech windows that START after the hit (+50 ms) ...
            for a, b in rep['windows']:
                if a < hit + 0.05 or a >= end:
                    continue
                if wins and a - wins[-1][1] < HERO_CARVE_BRIDGE:  # ... bridged across short pauses
                    wins[-1] = (wins[-1][0], b)
                else:
                    wins.append((a, b))
            w = [(a, b, HERO_CARVE_DB) for a, b in wins]
            if w:
                c['carve'] = w
                rep['carved'].append(dict(name=c['name'], t=c['t'], windows=[(a, b) for a, b, _ in w]))
    rep['vo'] = dict(kind=src['kind'], words=src['words'] if isinstance(src['words'], str) else 'planned windows',
                     wav=src['wav'])
    return (out, rep) if report else out


# ======================================================================================== circular mixer
def _circ_pad(x, p):
    return np.concatenate([x[-p:], x, x[:p]], axis=0)


def _circ(fn, x, pad=1.0):
    """Apply fn to x as a loop (pad both ends with the other end, process, crop)."""
    p = _n(pad)
    y = fn(_circ_pad(x, p))
    return y[p:p + len(x)]


def _fold(buf, pre, Nn):
    """buf covers [-pre, Nn + post): fold everything outside [0, Nn) back into the loop (mod Nn)."""
    out = np.zeros((Nn,) + buf.shape[1:])
    idx = (np.arange(len(buf)) - pre) % Nn
    np.add.at(out, idx, buf)
    return out


def _timing(y, start, hit_abs=None, hop=96):
    """Isolated timing of one rendered cue (reel time): onset = first 2 ms bin within 20 dB of the cue's own peak bin,
    peak = centre of the loudest 30 ms RMS window (whooshes and swells peak broadly), end = the last 2 ms bin within
    40 dB of the peak bin."""
    m = np.square(np.asarray(y, dtype=np.float64)).mean(1)
    nb = len(m) // hop
    p2 = m[:nb * hop].reshape(nb, hop).mean(1)
    e = 10 * np.log10(p2 + 1e-20)
    pk = float(e.max())
    on = int(np.argmax(e >= pk - 20.0))
    end = int(np.nonzero(e >= pk - 40.0)[0][-1]) + 1
    sm = np.convolve(p2, np.ones(15) / 15, 'same')                  # 15 x 2 ms = 30 ms
    out = dict(onset_abs=round(start + on * hop / SR, 4), peak_abs=round(start + (int(np.argmax(sm)) + 0.5) * hop / SR, 4),
               end_abs=round(start + end * hop / SR, 4))
    if hit_abs is not None:                                          # level of the 30 ms window AT the designed hit
        k = int(np.clip(round((hit_abs - start) * SR / hop - 0.5), 0, len(sm) - 1))
        out['at_hit_db'] = round(float(10 * np.log10(sm[k] + 1e-20) - 10 * np.log10(sm.max() + 1e-20)), 2)
    return out


def _sat_matched(y, drive):
    """Alias-safe tanh saturation (sfx_jawad.shape, 8x oversampled) of one cue, peak-normalised into the curve, then
    scaled back to the cue's own max momentary loudness: same loudness, lower peak-to-loudness ratio ("saturation
    helps the hit cut through", bible 4.2), so the bus limiter has less to shave off the reveal."""
    y = np.asarray(y, dtype=np.float64)
    pk = float(np.max(np.abs(y))) + 1e-12
    z = SJ.shape(y / pk, drive)
    return z * undb(A.momentary_max(y) - A.momentary_max(z))


def _carve_gain(L, start, carve, ramp=0.05):
    """Gain curve for one cue: depth_db inside each (t0, t1, depth_db) window (reel time), 50 ms raised-cosine ramps."""
    t = start + np.arange(L) / SR
    g_db = np.zeros(L)
    for a, b, d in carve:
        up = np.clip((t - (a - ramp)) / ramp, 0, 1)
        dn = np.clip(((b + ramp) - t) / ramp, 0, 1)
        w = 0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn))
        g_db = np.minimum(g_db, d * w)
    return undb(g_db)


def mix_loop(cue_list, dur=DUR, beds=BEDS, out_stem=None, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING,
             room_send=True, glue=True, vary=True, verbose=True):
    """audio.mix's chain on a LOOP (see module docstring). Returns a report dict compatible with audio.mix_overview
    (+ fx / bed arrays). Writes <out_stem>.wav (= the stem), <out_stem>_fx.wav and <out_stem>_bed.wav (they sum to it)."""
    Nn = _n(dur)
    PRE, POST = _n(1.0), _n(9.0)
    cs = A.duck_under([A._norm_cue(c) for c in cue_list])
    fxb = np.zeros((PRE + Nn + POST, 2))
    send = np.zeros_like(fxb)
    placed, counts = [], {}
    for c in sorted(cs, key=lambda c: float(c['t'])):
        k = (c['name'], A._key(c['params']))
        counts[k] = counts.get(k, -1) + 1
        y, hit = A._render_cue(c, (counts[k] % 4) if vary else None)
        start = float(c['t']) - (hit if c['align'] == 'hit' else 0.0)
        i = PRE + _n(start)
        assert 0 <= i and i + len(y) <= len(fxb), (c['name'], start)
        if c.get('sat'):                                           # hero saturation, loudness-matched (bible 4.2)
            y = _sat_matched(y, float(c['sat']))
        tm = _timing(y, start, start + hit)                        # isolated onset / peak / end (before the carve)
        if c.get('carve'):                                         # a hero's tail under later speech (VO-first)
            y = y * _carve_gain(len(y), start, c['carve'])[:, None]
        fxb[i:i + len(y)] += y
        cat = A.SOUNDS[c['name']]['category']
        sdb = c.get('send_db', A.SOUNDS[c['name']]['send'] if A.SOUNDS[c['name']]['send'] is not None
                    else A._CAT_SEND[cat])
        if room_send and sdb is not None and sdb > -60:
            send[i:i + len(y)] += y * undb(sdb)
        warn = 'wraps to the loop end' if start < 0 else ('tail wraps to t=0' if start + len(y) / SR > dur else '')
        placed.append(dict(t=float(c['t']), name=c['name'], start=round(start, 4), hit=round(start + hit, 4),
                           len=round(len(y) / SR, 3), gain_db=round(float(c['gain_db']), 2),
                           duck_db=c.get('duck_db', 0.0), align=c['align'], params=c['params'],
                           lp=c.get('lp'), hp=c.get('hp'), rate=c.get('rate'), pan=c.get('pan', 0.0),
                           hero=bool(c.get('hero')), vo=c.get('vo', ''), ev=c.get('ev', ''), warn=warn,
                           carve=c.get('carve'), **tm))
    if room_send:
        wet = A.reverb(send, 'studio', wet_db=0.0, dry=0.0)
        fxb += wet[:len(fxb)]
        rest = wet[len(fxb):]
        if len(rest) and np.max(np.abs(rest)) > 1e-7:
            raise RuntimeError('room tail beyond the post-roll')
    fx = _fold(fxb, PRE, Nn)                                       # tails past DUR land on t = 0 (the loop)
    fx *= undb(target_lufs - A.loudness(fx))
    gr_comp = np.zeros(Nn)
    if glue:
        gr_comp = _circ(lambda z: A.compressor_gain(z, thresh_db=target_lufs + 8.0, ratio=2.0), fx)
        fx *= undb(gr_comp)[:, None]
    bed, bed_info = _bed_bus(beds, dur, target_lufs)
    p = _n(1.0)
    fx_pad = _circ_pad(fx, p)
    bed = A.sidechain(_circ_pad(bed, p), fx_pad, depth_db=5.0)[p:p + Nn]
    pk_fx = _circ(A.tp_envelope, fx)
    pk_bed = _circ(A.tp_envelope, bed)
    G, ceil = 0.0, tp_ceiling - 0.2
    best = None
    for attempt in range(4):
        for it in range(40):
            gl = _circ(lambda z: A.limiter_gain(None, ceil, pk=z), pk_fx * undb(G) + pk_bed)
            y = (fx * undb(G) + bed) * gl[:, None]
            L1 = A.loudness(y)
            if best is None or abs(L1 - target_lufs) < abs(best[2] - target_lufs):
                best = (G, gl, L1, y)
            if abs(L1 - target_lufs) < 0.02:
                break
            G += float(np.clip(target_lufs - L1, -12, 12)) * 0.9
        G, gl, L1, y = best
        tp = A.true_peak(_circ_pad(y, _n(0.05)))
        if tp <= tp_ceiling - 0.05:
            break
        ceil -= tp - (tp_ceiling - 0.1)
        best = None
    fx_out = fx * (undb(G) * gl)[:, None]
    bed_out = bed * gl[:, None]
    master = fx_out + bed_out
    tpc = A.true_peak(_circ_pad(master, _n(0.05)))
    rep = dict(dur=dur, cues=len(cs), integrated_lufs=round(A.loudness(master), 2), true_peak_dbtp=round(tpc, 2),
               sample_peak_dbfs=round(float(db(np.max(np.abs(master)))), 2),
               lra_lu=round(A.loudness_range(master), 2), max_momentary_lufs=round(A.momentary_max(master), 2),
               max_short_term_lufs=round(A.momentary_max(master, 3.0), 2),
               limiter_max_gr_db=round(max(0.0, float(-db(np.min(gl)))), 2),
               limiter_max_gr_at=round(float(np.argmin(gl)) / SR, 3),
               limiter_pct_over_1db=round(100.0 * float(np.mean(gl < undb(-1.0))), 2),
               comp_max_gr_db=round(float(-np.min(gr_comp)), 2), fx_gain_db=round(G, 2),
               bed=bed_info, bed_lufs=round(A.loudness(bed_out), 2), fx_lufs=round(A.loudness(fx_out), 2),
               placed=placed, files={})
    if out_stem:
        rep['files']['stem'] = A._write_wav(out_stem + '.wav', master, 24)
        rep['files']['stem_fx'] = A._write_wav(out_stem + '_fx.wav', fx_out, 24)
        rep['files']['stem_bed'] = A._write_wav(out_stem + '_bed.wav', bed_out, 24)
    rep['audio'] = master.astype(np.float32)
    rep['fx'] = fx_out.astype(np.float32)
    rep['bedbus'] = bed_out.astype(np.float32)
    if verbose:
        print('SFX loop mix %.2fs %d cues | I %.2f LUFS | TP %.2f dBTP (circular) | LRA %.1f | Mmax %.1f | limiter GR '
              '%.2f dB | glue GR %.2f dB | bed %.1f LUFS' % (dur, rep['cues'], rep['integrated_lufs'],
                                                             rep['true_peak_dbtp'], rep['lra_lu'],
                                                             rep['max_momentary_lufs'], rep['limiter_max_gr_db'],
                                                             rep['comp_max_gr_db'], rep['bed_lufs']))
    return rep


# ======================================================================================== measurement helpers
def _ebur128(path):
    import re
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def _onset_near(x, t, win=0.06, hop=240):
    """qa_measure.py `cues` algorithm on an array: the 5 ms-energy rise nearest t within +-win -> (offset s, rise dB)."""
    m = np.asarray(x, dtype=np.float64)
    m = m.mean(1) if m.ndim == 2 else m
    e = np.sqrt(np.convolve(m * m, np.ones(hop) / hop, 'same')[::hop] + 1e-12)
    d = 20 * np.log10(e)
    on = np.maximum(np.diff(d, prepend=d[0]), 0)
    rate = SR / hop
    i0, i1 = max(0, int((t - win) * rate)), min(len(on) - 1, int((t + win) * rate))
    k = i0 + int(np.argmax(on[i0:i1]))
    return k / rate - t, float(on[k])


def starts_per_instant(placed, music_events=(), tol=1.0 / FPS):
    """Sounds STARTING within one frame of each other (bible 4.2: a riser / swell that ENDS there does not count, so
    neither does a sound whose designed hit sits >= 50 ms after its start, nor the score's 0.6 s pad fade-ins). SFX: one
    entry per cue (onset = the hit for transient sounds, t for align='start'). Score: its transient events (kick, hat,
    EP note, sub entry) at one instant count as ONE sound (the score is one bus: "the score's first pulse", BRIEF 11).
    Returns (max_count, clusters with >= 3 sources)."""
    ev = []
    for p in placed:
        if p['align'] == 'start':
            ev.append((p['start'], 'sfx:' + p['name']))
        elif p['hit'] - p['start'] < 0.05:
            ev.append((p['hit'], 'sfx:' + p['name']))
    ev += [(float(t), 'music:' + n) for t, n in music_events]
    ev.sort()
    worst, clusters = 0, []
    for t, n in ev:
        grp = [e for e in ev if abs(e[0] - t) <= tol]
        src = [e[1] for e in grp if e[1].startswith('sfx:')]
        mus = sorted({e[1] for e in grp if e[1].startswith('music:')})
        count = len(src) + (1 if mus else 0)
        worst = max(worst, count)
        item = (round(t, 3), count, src + (['music(' + ' + '.join(m[6:] for m in mus) + ')'] if mus else []))
        if count >= 3 and item[2] not in [c[2] for c in clusters]:
            clusters.append(item)
    return worst, clusters


def _music_events():
    """The score's transient onsets from music_full.json (kick, hat, EP notes, the sub entry); pads and drones fade."""
    try:
        d = json.load(open(MUSIC_JSON))
    except Exception:
        return []
    out = []
    for e in d.get('events', []):
        w = str(e.get('what', ''))
        if any(k in w for k in ('kick', 'hat', 'EP ', 'sub D1')):
            out.append((float(e['t']), w.split(' (')[0]))
    return out


# ======================================================================================== CLI
def _paths(hook):
    name = MODULE if hook == 'A' else MODULE + '_hookb'
    return name, os.path.join(AUD, name)


def build(hook='A'):
    register()
    name, base = _paths(hook)
    cl, frep = cues(hook, report=True)
    rep = mix_loop(cl, out_stem=base + '_sfx_stem')
    A._write_wav(base + '_sfx.wav', rep['audio'], 24)                  # same audio, the name render.py would mux
    rep['files']['mix'] = base + '_sfx.wav'
    A.mix_overview(rep, base + '_sfx_overview.png', '%s SFX stem (hook %s, VO fit: %s)' % (name, hook,
                                                                                          frep['vo']['kind']))
    # measurements
    x = np.asarray(rep['audio'], dtype=np.float64)
    fx = np.asarray(rep['fx'], dtype=np.float64)
    tt, lc = A.loudness_curve(x)
    # cue timing, isolated render of each cue (what its sound does relative to its event frame):
    #   transient sounds (designed hit < 50 ms after the start) and align='start' cues -> onset vs the cue time
    #   swells / whooshes / bursts (hit = their loudest point) -> peak vs the cue time
    #   spans (reverse_swell: hit = END) -> end vs the cue time
    #   (an align='start' sound with a designed pass > 50 ms in, e.g. swish_small, is a peak at t + its hit offset)
    timing = []
    for p in rep['placed']:
        if p['name'] in SJ.SPAN or p['name'] == 'reverse_swell':
            kind, at, ref, tol = 'end', p['end_abs'], p['t'], 1.0 / FPS
        elif p['hit'] - p['start'] < 0.05:
            kind, at, ref, tol = 'onset', p['onset_abs'], p['t'], 1.0 / FPS
        else:
            kind, at, ref, tol = 'peak', p['peak_abs'], p['hit'], 0.06
        off = at - ref
        ok = abs(off) <= tol + 1e-6 or (kind == 'peak' and p.get('at_hit_db', -99) >= -1.5)   # broad peak: <= 1.5 dB
        timing.append(dict(name=p['name'], t=p['t'], f=round(p['t'] * FPS, 2), kind=kind, ref=round(ref, 4), at=at,
                           off_ms=round(off * 1000, 1), off_frames=round(off * FPS, 2),
                           at_hit_db=p.get('at_hit_db') if kind == 'peak' else None, flag='' if ok else 'CHECK'))
    # what qa_measure.py `cues` will print on the master for the hero cues (5 ms argmax-of-rise in the whole stem)
    onsets = []
    for p in rep['placed']:
        if p['hero']:
            tq = p['start'] if p['align'] == 'start' else p['hit']
            off, rise = _onset_near(fx, tq)
            onsets.append(dict(name=p['name'], t=p['t'], qa_off_ms=round(off * 1000, 1), qa_rise_db=round(rise, 1)))
    a, b = _n(F(456)), _n(F(480))
    seam = dict(last50_rms_db=round(float(db(_rms(x[-_n(0.05):]))), 2), first50_rms_db=round(float(db(_rms(x[:_n(0.05)]))), 2),
                step=round(float(np.abs(x[0] - x[-1]).max()), 6),
                median_step=round(float(np.median(np.abs(np.diff(x[-_n(0.05):], axis=0)).max(1))), 6))
    meas = dict(
        vo_fit=frep['vo'], ducked=frep['ducked'], spans=frep['spans'], heroes_ok=frep['heroes_ok'],
        violations=frep['violations'],
        stem=dict((k, rep[k]) for k in ('integrated_lufs', 'true_peak_dbtp', 'sample_peak_dbfs', 'lra_lu',
                                        'max_momentary_lufs', 'max_short_term_lufs', 'limiter_max_gr_db',
                                        'limiter_pct_over_1db', 'comp_max_gr_db', 'bed_lufs', 'fx_lufs', 'fx_gain_db')),
        ffmpeg=_ebur128(base + '_sfx_stem.wav'),
        max_momentary_at=round(float(tt[np.argmax(lc)]), 3),
        dropout=dict(fx_max_dbfs=round(float(db(np.abs(fx[a:b]).max() + 1e-15)), 1),
                     wall_max_dbfs=None, stem_rms_dbfs=round(float(db(_rms(x[a:b]))), 1),
                     digital_silence_frames=int(sum(np.abs(x[a + _n(F(k)):a + _n(F(k + 1))]).max() < 2 ** -23
                                                    for k in range(24)))),
        seam=seam, timing=timing, qa_onsets=onsets, carved=frep['carved'],
        starts_per_instant=starts_per_instant(rep['placed'], _music_events()),
        bed=rep['bed'])
    # whisper wall alone in the drop-out (it must be cut dead at 15.2)
    wall_only = [b2 for b2 in BEDS if b2['name'] == 'lkk_whisper_wall']
    wb, _ = _bed_bus(wall_only)
    meas['dropout']['wall_max_dbfs'] = round(float(db(np.abs(wb[a:b]).max() + 1e-15)), 1)
    # bed sections in the stem (short-term over each section's interior)
    bo = np.asarray(rep['bedbus'], dtype=np.float64)
    secs = [(0.2, 3.0), (3.4, 5.8), (6.2, 8.6), (9.0, 15.1), (15.25, 15.95), (16.1, 25.5), (26.0, 33.5), (34.6, 35.2)]
    meas['bed_sections_lufs'] = [(s0, s1, round(A.loudness(bo[_n(s0):_n(s1)]), 1)) for s0, s1 in secs]
    cj = dict(module=MODULE, hook=hook, dur=DUR, bpm=BPM, fps=FPS, vo=frep['vo'],
              cues=[dict((k, v) for k, v in p.items()) for p in rep['placed']])
    json.dump(cj, open(base + '_cues.json', 'w'), indent=1)
    json.dump(meas, open(base + '_sfx_report.json', 'w'), indent=1, default=str)
    print(json.dumps(dict((k, meas[k]) for k in ('vo_fit', 'stem', 'ffmpeg', 'max_momentary_at', 'dropout', 'seam',
                                                 'starts_per_instant', 'bed_sections_lufs')), indent=1, default=str))
    for o in timing:
        print('%5s %-18s t %7.3f (f%7.2f) %-5s ref %7.3f at %7.3f  %+6.1f ms (%+.2f f)%s' % (
            o['flag'], o['name'], o['t'], o['f'], o['kind'], o['ref'], o['at'], o['off_ms'], o['off_frames'],
            '' if o['at_hit_db'] is None else '  level at the designed hit %.2f dB re peak' % o['at_hit_db']))
    for o in onsets:
        print('  qa_measure-style %-12s t %7.3f  argmax-rise %+6.1f ms, %.1f dB' % (o['name'], o['t'], o['qa_off_ms'],
                                                                                   o['qa_rise_db']))
    print('limiter max GR %.2f dB at %.3f s' % (rep['limiter_max_gr_db'], rep['limiter_max_gr_at']))
    print('carved:', json.dumps(frep['carved']))
    return rep, meas


def rough(hook='A'):
    """Rough mix with the music-supervisor's chain (epic_mix.mix_reel): VO -16, SFX stem -18 (-4 dB under the VO),
    music -18 (-3 under SFX hits, -9 under the VO), master -14 LUFS / limiter -2.3 dBFS TP."""
    import epic_mix as M
    register()
    name, base = _paths(hook)
    src = vo_source(hook)
    if src['wav'] is None:
        sys.exit('rough: no VO stem (real or stand-in) for hook %s' % hook)
    sfx = base + '_sfx_stem.wav'
    music = MUSIC if os.path.exists(MUSIC) else None
    rname = name + '_rough'
    vo_wav, tmp = src['wav'], None
    xv, srv = A.read_wav(vo_wav)
    if xv.shape[1] == 1:          # epic_mix.load keeps a mono wav as (N, 1) and mix_reel's concatenate then fails
        tmp = os.path.join(AUD, '_tmp_%s_vo_stereo.wav' % rname)   # (SHARED_REQUESTS R4): feed a stereo copy
        A._write_wav(tmp, np.repeat(xv, 2, axis=1), 24)
        vo_wav = tmp
    try:
        rep = M.mix_reel(rname, DUR, vo=vo_wav, sfx=sfx, music=music, out_dir=AUD, vo_offset=0.0)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    f = rep['files']
    rep['vo_kind'] = src['kind']
    rep['ffmpeg_A'] = _ebur128(f['mix'])
    rep['ffmpeg_B'] = _ebur128(f['vo_sfx'])
    y = A.read_wav(f['mix'])[0]
    v = A.read_wav(f['stem_vo'])[0]
    s = A.read_wav(f['stem_sfx'])[0]
    m = A.read_wav(f['stem_music'])[0]
    tt, ly = A.loudness_curve(y)
    _, lv = A.loudness_curve(v)
    _, lb = A.loudness_curve(s + m)
    _, ls = A.loudness_curve(s)
    sp = M.speech_mask(v)
    idx = np.clip((tt * SR).astype(int), 0, len(v) - 1)
    spk = sp[idx] & (lv > lv.max() - 15)
    rep['vo_over_bed_lu'] = round(float(np.median((lv - lb)[spk])), 1)        # bed = music + SFX together
    rep['vo_over_bed_p10_lu'] = round(float(np.percentile((lv - lb)[spk], 10)), 1)
    rep['vo_over_sfx_p10_lu'] = round(float(np.percentile((lv - ls)[spk], 10)), 1)
    lines = {}
    for w in (json.load(open(src['words'])) if isinstance(src['words'], str) else []):
        if isinstance(w, dict) and w.get('line'):
            lines.setdefault(w['line'], [w['start'], w['end']])[1] = w['end']
    _, lm_ = A.loudness_curve(m)
    rep['per_line'] = {}
    for ln, (a0, b0) in lines.items():
        sel = spk & (tt >= a0) & (tt <= b0)
        if sel.any():
            rep['per_line'][ln] = dict(t=(round(a0, 2), round(b0, 2)),
                                       vo_over_bed_med=round(float(np.median((lv - lb)[sel])), 1),
                                       vo_over_music_med=round(float(np.median((lv - lm_)[sel])), 1),
                                       vo_over_sfx_med=round(float(np.median((lv - ls)[sel])), 1),
                                       vo_over_sfx_p10=round(float(np.percentile((lv - ls)[sel], 10)), 1))
    k = int(np.argmax(ly))
    rep['max_momentary'] = dict(lufs=round(float(ly[k]), 2), window=(round(tt[k] - 0.2, 3), round(tt[k] + 0.2, 3)),
                                centre=round(float(tt[k]), 3))
    sel = (tt > 25.4) & (tt < 26.2)
    kc = int(np.argmax(np.where(sel, ly, -200)))
    rep['clunk_momentary'] = dict(lufs=round(float(ly[kc]), 2), centre=round(float(tt[kc]), 3),
                                  below_reveal_lu=round(float(ly[k] - ly[kc]), 2))
    a, b = _n(F(456)), _n(F(480))
    st_t, st_l = A.loudness_curve(y, 3.0, 0.05)
    rep['dropout'] = dict(music_max_dbfs=round(float(db(np.abs(m[a:b]).max() + 1e-15)), 1),
                          mix_rms_dbfs=round(float(db(_rms(y[a:b]))), 1),
                          mix_momentary_lufs=round(float(A.loudness_curve(y[a:b], 0.4, 0.05)[1].mean()), 1),
                          mix_dropout_lufs=round(float(-0.691 + 10 * np.log10(np.mean(np.square(A.kweight(y[a:b])).sum(1))
                                                                                + 1e-30)), 1),
                          digital_silence_frames=int(sum(np.abs(y[a + _n(F(j)):a + _n(F(j + 1))]).max() < 2 ** -23
                                                         for j in range(24))))
    rep['seam'] = dict(last50_rms_db=round(float(db(_rms(y[-_n(0.05):]))), 2),
                       first50_rms_db=round(float(db(_rms(y[:_n(0.05)]))), 2),
                       step=round(float(np.abs(y[0] - y[-1]).max()), 6),
                       median_step=round(float(np.median(np.abs(np.diff(y[-_n(0.05):], axis=0)).max(1))), 6))
    # hero hits clear of words: speech activity around each hero hit in the VO stem actually used
    acts = SJ.vo_activity(src['wav'])
    words = SJ._load_words(src['words']) if isinstance(src['words'], str) else src['words']
    cj = json.load(open(base + '_cues.json'))
    heroes = []
    for p in cj['cues']:
        if p['hero']:
            h = p['hit']
            before = [w for w in words + acts if w[0] < h and w[1] > h - 0.12]
            after = [w for w in words + acts if w[0] < h + 0.30 and w[1] > h]
            prev_end = max([w[1] for w in words + acts if w[1] <= h] or [None]) if any(w[1] <= h for w in words + acts) else None
            next_on = min([w[0] for w in words + acts if w[0] >= h] or [None]) if any(w[0] >= h for w in words + acts) else None
            heroes.append(dict(name=p['name'], hit=h, speech_end_before=prev_end, speech_start_after=next_on,
                               clear=not before and not after))
    rep['heroes_vs_speech'] = heroes
    json.dump(rep, open(os.path.join(AUD, rname + '_mix.json'), 'w'), indent=1, default=str)
    keys = ('vo_kind', 'A_full', 'B_vo_sfx', 'ffmpeg_A', 'ffmpeg_B', 'vo_over_music_lu', 'vo_over_sfx_lu',
            'vo_over_bed_lu', 'vo_over_bed_p10_lu', 'vo_over_sfx_p10_lu', 'vo_lufs_in_mix', 'music_lufs_in_mix',
            'sfx_lufs_in_mix', 'per_line', 'max_momentary', 'clunk_momentary', 'dropout', 'seam', 'heroes_vs_speech', 'files')
    print(json.dumps(dict((k2, rep[k2]) for k2 in keys), indent=1, default=str))
    return rep


def audition():
    register()
    d = os.path.join(AUD, 'audition')
    os.makedirs(d, exist_ok=True)
    rows = []
    for n in LOCAL:
        x = A.sound(n)
        arr = np.asarray(x, dtype=np.float64)
        st = A.stats(arr, x.hit)
        if A.SOUNDS[n]['category'] == 'bed':
            two = np.concatenate([arr, arr])                         # seam check: the loop played twice
            j = len(arr)
            step = float(np.abs(two[j] - two[j - 1]).max())
            med = float(np.median(np.abs(np.diff(arr, axis=0)).max(1)))
            q = [] if step < 4 * med + 1e-4 else ['loop seam step %.5f vs median %.5f' % (step, med)]
            q += [p for p in A.qc(arr, x.hit) if not p.startswith('start edge') and not p.startswith('end edge')]
            mono = A.momentary_max(arr) - A.momentary_max(arr.mean(1, keepdims=True).repeat(2, 1))
            extra = dict(seam_step=round(step, 6), median_step=round(med, 6), lufs=round(A.loudness(arr), 2),
                         mono_loss_db=round(mono, 2))
        else:
            q = A.qc(arr, x.hit)
            mono = A.momentary_max(arr) - A.momentary_max(arr.mean(1, keepdims=True).repeat(2, 1))
            extra = dict(mono_loss_db=round(mono, 2))
        A._write_wav(os.path.join(d, n + '.wav'), arr, 24)
        A.spectro_image(arr, 1000, 420, x.hit, n, json.dumps(dict(st, **extra))[:160]).save(os.path.join(d, n + '.png'))
        rows.append(dict(name=n, hit=round(x.hit, 4), dur=round(len(arr) / SR, 3), qc=q,
                         stats=dict((k, (round(v, 3) if isinstance(v, float) else v)) for k, v in st.items()), **extra))
        print('%-18s hit %.3f dur %6.2f qc %s %s' % (n, x.hit, len(arr) / SR, q or 'clean', extra))
    # tonal checks (bible 4.2 f0_of) after the pitch moves
    def f0_of(name, rate=1.0, **p):
        y = np.asarray(A.sound(name, **p), float).mean(1)
        X = np.abs(np.fft.rfft(y * np.hanning(len(y))))
        f = np.fft.rfftfreq(len(y), 1 / SR)
        return float(f[np.argmax(X * (f > 150))]) * rate
    def note(f):
        m = 69 + 12 * math.log2(f / 440.0)
        return '%s%d %+.0fc' % (['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][int(round(m)) % 12],
                                int(round(m)) // 12 - 1, (m - round(m)) * 100)
    ton = dict(glass_tap=f0_of('glass_tap', pitch=GLASS_PITCH), ui_click=f0_of('ui_click', rate=CLICK_RATE),
               ui_tick=f0_of('ui_tick', pitch=TICK_PITCH))
    hum = np.asarray(A.sound('lkk_flood_hum'), float).mean(1)
    Xh = np.abs(np.fft.rfft(hum))
    fh = np.fft.rfftfreq(len(hum), 1 / SR)
    ton['lkk_flood_hum'] = float(fh[np.argmax(Xh * (fh > 50))])
    tonal = dict((k, dict(hz=round(v, 1), note=note(v))) for k, v in ton.items())
    print(json.dumps(tonal, indent=1))
    json.dump(dict(sounds=rows, tonal=tonal), open(os.path.join(d, 'audition.json'), 'w'), indent=1)
    return rows


def verify_wall(models=('small', 'medium')):
    """faster-whisper on the whisper wall alone (24 s = the loop twice, + the bed stem's wall section): no word with
    probability >= 0.5 in hi / en / auto-detected language."""
    from faster_whisper import WhisperModel
    register()
    wd = os.path.join(REPO, 'workspace', 'brand_reels', 'tts', 'models', 'whisper')
    x = np.asarray(A.sound('lkk_whisper_wall'), dtype=np.float64)
    tests = dict(wall_loop_x2=np.concatenate([x, x]).mean(1))
    bp_ = os.path.join(AUD, MODULE + '_sfx_stem_bed.wav')
    if os.path.exists(bp_):
        bb = A.read_wav(bp_)[0].mean(1)
        tests['stem_bed_0_15.2'] = bb[:_n(15.2)]
    out = {}
    for mname in models:
        mp = os.path.join(wd, 'faster-whisper-%s' % mname)
        model = WhisperModel(mp if os.path.isdir(mp) else mname, device='cpu', compute_type='int8', cpu_threads=2)
        for tn, sig in tests.items():
            y16 = signal.resample_poly(sig, 1, 3).astype(np.float32)
            y16 = y16 / (np.max(np.abs(y16)) + 1e-9) * 0.5          # loud enough for ASR (worst case)
            for lang in ('hi', 'en', None):
                segs, info = model.transcribe(y16, language=lang, word_timestamps=True, vad_filter=False,
                                              beam_size=5, condition_on_previous_text=False)
                words = [(round(w.start, 2), w.word, round(w.probability, 3)) for s in segs for w in (s.words or [])]
                hi_p = [w for w in words if w[2] >= 0.5]
                key = '%s|%s|%s' % (mname, tn, lang or 'auto:%s' % info.language)
                out[key] = dict(n_words=len(words), max_p=max([w[2] for w in words] or [0.0]), words_p_ge_05=hi_p,
                                sample=words[:8])
                print(key, len(words), 'words, max p %.3f' % out[key]['max_p'], 'p>=0.5:', hi_p)
    ok = all(not v['words_p_ge_05'] for v in out.values())
    out['PASS'] = ok
    json.dump(out, open(os.path.join(AUD, 'whisper_wall_asr.json'), 'w'), indent=1, ensure_ascii=False)
    print('PASS' if ok else 'FAIL')
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('cues', 'audition', 'build', 'rough', 'verify'))
    ap.add_argument('--hook', default='A', choices=('A', 'B', 'AB'))
    a = ap.parse_args(argv)
    hooks = ['A', 'B'] if a.hook == 'AB' else [a.hook]
    os.makedirs(AUD, exist_ok=True)
    if a.cmd == 'cues':
        for h in hooks:
            cl, rep = cues(h, report=True)
            print('hook %s | VO: %s' % (h, rep['vo']))
            for c in cl:
                print('%7.3f f%7.2f %-18s %6.1f dB %-5s %s %s' % (c['t'], c['t'] * FPS, c['name'], c['gain_db'],
                                                              c['align'], c.get('vo', ''), c.get('ev', '')))
    elif a.cmd == 'audition':
        audition()
    elif a.cmd == 'build':
        for h in hooks:
            build(h)
    elif a.cmd == 'rough':
        for h in hooks:
            rough(h)
    else:
        verify_wall()


if __name__ == '__main__':
    main(sys.argv[1:])
