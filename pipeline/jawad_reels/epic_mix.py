#!/usr/bin/env python3
"""epic_mix.py: VO-reel mix + master for the @jawad_mp4 reels (shared sound kit; owner: music-supervisor).

Rebuilt 2026-10-09 as COMMITTED code (the first copy lived in the git-ignored workspace/brand_reels/sfx/ and was lost).
Spec: brand_reels/research/sound_design.md section 6. Contract: every call site in the five reels' modules
(pehle_wala, bijli_chali_gayi, ek_frame_ki_keemat, beta_tum_karte_kya_ho, log_kya_kahenge *_sfx.py / *_music.py /
log_kya_kahenge_mix.py) works unchanged, and their local workarounds for the old kit's bugs stay harmless.
Nobody on the team can listen: everything this module claims is measured (BS.1770 in numpy, ffmpeg ebur128, PNGs).

CHAIN (mix_reel; 48 kHz stereo float64, deterministic: no randomness anywhere)
  0. Inputs: a wav path (16/24/32-bit PCM via audio.read_wav; float / other formats are decoded by ffmpeg, never
     executed) or an array; mono (N,), (N, 1) or stereo; any length (zero-padded or cut to dur). A mono input becomes
     L = R and every stem is re-levelled by loudness afterwards, so the +3.01 LU of a duplicated mono file never
     reaches the mix (fixes SHARED_REQUESTS R7 / R6a / #11 / bijli 5). vo_offset (default 0.0: the reels' VO stems are
     already placed on the reel timeline) shifts the VO; a raw take goes at the spec's 0.3 s (SPEC['vo_place_s']).
  1. VO chain (vo_chain): HPF 80 Hz (12 dB/oct), -2 dB @ 300 Hz (Q 1.0), +2 dB @ 3.2 kHz (Q 0.9), +1.5 dB high shelf
     @ 10 kHz, 3:1 compressor (soft knee 6 dB, 8 / 120 ms, threshold 4 dB under the 90th-percentile 10 ms level,
     ~4-6 dB GR on peaks), -16.0 LUFS integrated (VO alone).
  2. SFX: a finished stem (sfx=) or a cue list (sfx_cues=) mixed by audio.mix (auto-duck, room send, glue, -18 LUFS,
     TP <= -2.0, split stems; bed= / bed_gain_db= / tail_fade= pass through: R3). In the mix the stem is placed by its
     integrated loudness at -18.0 LUFS and sidechained 4 dB under the VO (30 / 300 ms). bed= with a stem file adds the
     bed the way audio.mix anchors it (target + bed_gain_db + 8 LUFS, ducked 5 dB under the SFX).
  3. Music: -18.0 LUFS alone (-16.0 without VO), ducked 3 dB under the SFX (10 / 250 ms) and 9 dB under the VO
     (40 / 400 ms). Never renormalised after ducking. Opt-in (word_floor_lu=8.0 with words=): a gentle extra duck
     under each word that still sits under 8 LU over the bed (LEAD_DECISIONS 1); off by default (the spec's chain).
  4. Bus A = VO + SFX + music: glue 2:1 (soft knee 6 dB, 6 / 150 ms, RMS 8 ms; threshold 3 dB under the bus's
     98th-percentile 10 ms level), `protect=[(t0, t1)]` caps the glue at protect_cap_db inside hero windows (R6b),
     then gain + 4x-oversampled true-peak lookahead limiter at -2.3 dBFS, the gain iterated to -14.0 LUFS (+-0.02),
     true peak <= -2.0 dBTP (the ceiling steps down if a measurement says otherwise).
  5. Version B = VO + SFX with the same internal balance, mastered on its own (own glue threshold, gain, limiter).
  6. Stems = each processed input x version A's WHOLE bus curve (glue x gain x limiter), so vo + sfx + music == A to
     24-bit rounding (R6d: the old stems left the glue out).
  7. Checks (rep['checks']): A / B -14 +-0.1 LUFS and <= -2.0 dBTP; speech >= 8 LU over the ducked music and >= 10 LU
     over the SFX (medians over speech frames: momentary 400 ms / 50 ms hop, speech_mask at the window centre, VO
     within 15 LU of its loudest frame: the reels' rough-mix method); LRA 2.0-9 LU (LEAD_DECISIONS 1, over the spec's
     2-8); limiter GR > 3 dB for < 0.1 s in total and only on hero hits when their times are known; with words= also
     every word's K-weighted VO level over the music and over music + SFX (>= 8 LU, 7 LU tolerated on one-syllable
     words: LEAD_DECISIONS 1); stems-sum residual of the written files.
  loop=True (R6c): every input is padded circularly (pad s each side), the whole chain (VO chain, sidechains, glue,
     limiter) runs on the padded signals and is measured / normalised / cropped on the reel span, so every envelope
     enters sample 0 in its end-of-reel state; rep reports the continuity error at the seam. With sfx_cues the cues
     are rendered on an extended timeline and folded back (tails past dur land on t = 0, pre-laps before 0 on the
     end) and a bed becomes an exact-length seamless loop.

API
  rep = mix_reel(name, dur, vo=None, music=None, sfx_cues=None, bed=None, bed_gain_db=-30, out_dir=AUDIO,
                 vo_offset=0.0, sfx=None, *, words=None, tail_fade=0.4, loop=False, pad=4.0, protect=(),
                 protect_cap_db=0.0, glue=True, hero_times=None, music_gain_db=0.0, word_floor_lu=None,
                 word_floor_max_db=9.0, spec=None, png=True, write_report=True, verbose=True)
      writes <out_dir>/<name>_mix.wav (A), _vo_sfx.wav (B), _stem_vo.wav, _stem_sfx.wav, _stem_music.wav (always, silent
      when that input is absent), 48 kHz 24-bit stereo, plain files only (callers delete their scratch out_dir with
      os.remove); + <name>_mix.png (overview) and <name>_mix.json (this report); with sfx_cues also _sfx_stem.wav
      (+ _fx / _bed). rep is JSON-safe (no arrays): files{mix, vo_sfx, stem_vo, stem_sfx, stem_music, ...}, A_full,
      B_vo_sfx (lufs, tp_dbtp, lra, max_momentary, master_gain_db, glue_threshold_db, glue_max_gr_db, limiter_max_gr_db,
      limiter_gr_over_1db_s / _3db_s, limiter_gr_over_3db_spans, ...), vo_lufs_in_mix, sfx_lufs_in_mix,
      music_lufs_in_mix (None without music), vo_over_music_lu, vo_over_sfx_lu, vo_over_bed_lu, margins, words, checks,
      vo_chain, sfx, music, spec, inputs, warnings, integrated_lufs / true_peak_dbtp / lra_lu (= A).
  res = mux(video, wav, out)   two-pass ffmpeg loudnorm (pass 1 measures; pass 2 linear=true with the measured values,
      I=-14, TP=-1.5), AAC 320k 48 kHz stereo, -movflags +faststart, video stream copied (video=None -> audio-only
      .m4a), audio padded / cut to the video's duration; then re-measured with ebur128 -> res['ebur128'], res['pass'].
  load(path_or_array, dur=None) -> float64 (N, 2) (mono -> L = R; padded / cut to dur)
  vo_chain(x, lufs=-16.0, *, loop=False, crop=None, report=None) -> processed array, same length
  speech_mask(v, hold=0.25) -> bool per sample (10 ms RMS above median speech - 30 dB, held 0.25 s)
  _level_pct(x, pct=98) -> dB: percentile of the 10 ms level (louder channel's power, audio.compressor_gain's detector)
  glue_gain(bus, ...) -> (linear gain (N,), info);  glue(x, ...) -> glued x
  master(bus, *, glue=True, protect=(), loop=False, ...) -> (y, curve, info): glue + gain + limiter to -14 LUFS
  vo_margins(vo, music, sfx) / word_margins(vo, music, sfx, words) -> the checks above;  ebur128(path) -> dict(I, LRA,
  TP, LRA_low, LRA_high, threshold);  write_wav(path, x) (24-bit, exact inverse of audio.read_wav: R5);
  _overview(mix, vo, music, sfx, path, title) -> PNG (spectrogram + stem level curves + VO margin strip);
  cpad(x, p) / SPEC (every number above; SPEC['vo_lufs'], SPEC['sfx_duck_vo_db'] ... are read by the reels).

CLI (run in pipeline/jawad_reels; heavy runs through tools/heavy.sh)
  python3 epic_mix.py selftest [--out DIR] [--slug pehle_wala]   the mixtest (real VO, audio.py cues, synthetic bed)
  python3 epic_mix.py mix NAME DUR [--vo W] [--sfx W] [--music W] [--out-dir D] [--vo-offset S] [--loop] [--words J]
  python3 epic_mix.py mux VIDEO|- WAV OUT        python3 epic_mix.py ebur128 FILE
"""
import hashlib
import importlib
import json
import math
import os
import re
import subprocess
import sys
import time
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:                     # python3 -I drops the script's directory: audio.py lives next to this file
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.ndimage import maximum_filter1d, uniform_filter1d  # noqa: E402

import audio as A  # noqa: E402
from audio import SR, _n, undb, db  # noqa: E402

VERSION = '2.0.0 (rebuilt 2026-10-09)'
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

SPEC = dict(
    sr=SR, bits=24,
    # 1. VO
    vo_place_s=0.3,                      # where a RAW take goes (pass vo_offset=0.3); placed reel stems use 0.0
    vo_hpf_hz=80.0, vo_hpf_order=2,      # 12 dB/oct
    vo_eq=(('peak', 300.0, 1.0, -2.0), ('peak', 3200.0, 0.9, 2.0), ('hs', 10000.0, 0.7, 1.5)),
    vo_comp_ratio=3.0, vo_comp_knee_db=6.0, vo_comp_attack=0.008, vo_comp_release=0.12, vo_comp_below_p90_db=4.0,
    vo_comp_rms=0.010, vo_lufs=-16.0,
    # 2. SFX
    sfx_lufs=-18.0, sfx_tp_dbtp=-2.0, sfx_duck_vo_db=4.0, sfx_duck_vo_attack=0.03, sfx_duck_vo_release=0.30,
    bed_gain_db=-30.0, bed_duck_sfx_db=5.0, bed_anchor_db=float(A.BED_ANCHOR_DB),
    # 3. music
    music_lufs=-18.0, music_lufs_no_vo=-16.0,
    music_duck_sfx_db=3.0, music_duck_sfx_attack=0.01, music_duck_sfx_release=0.25,
    music_duck_vo_db=9.0, music_duck_vo_attack=0.04, music_duck_vo_release=0.40,
    # 4. bus
    glue_ratio=2.0, glue_below_p98_db=3.0, glue_knee_db=6.0, glue_attack=0.006, glue_release=0.15, glue_rms=0.008,
    protect_ramp_s=0.03,
    master_lufs=-14.0, master_tol_lu=0.1, master_iter_tol_lu=0.02,
    limiter_ceiling_dbfs=-2.3, limiter_lookahead_s=0.0015, limiter_release_s=0.08, limiter_knee_db=1.5,
    tp_max_dbtp=-2.0, loop_pad_s=4.0,
    # 7. checks
    check_vo_over_music_lu=8.0, check_vo_over_sfx_lu=10.0, check_word_lu=8.0, check_word_one_syllable_lu=7.0,
    check_lra_lu=(2.0, 9.0), check_limiter_gr_db=3.0, check_limiter_gr_max_s=0.1, check_hero_window_s=0.25,
    speech_top_lu=15.0, speech_hold_s=0.25, speech_thresh_db=-30.0,
    # export (mux)
    aac_lufs=-14.0, aac_tp_dbtp=-1.5, aac_lra=20.0, aac_bitrate='320k', aac_sr=48000, aac_tol_lu=0.5,
)
STEM_KEYS = ('mix', 'vo_sfx', 'stem_vo', 'stem_sfx', 'stem_music')
HERO_NAMES = {'impact_big', 'flash_hit', 'logo_sting', 'braam', 'glass_shatter', 'cinematic_boom', 'trailer_hit',
              'dhol_hit', 'jd_hit_hero', 'jd_floodlight_clunk', 'jd_stack_ember_slam', 'jd_stack_dha_hit'}


# ============================================================================================ I/O
def _stereo(x):
    """Any audio array -> float64 (N, 2): (N,) and (N, 1) become L = R, (1|2, N) is transposed, (N, >2) keeps L / R."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        return np.stack([x, x], 1)
    if x.ndim != 2:
        raise ValueError('epic_mix: audio must be (N,) or (N, channels), got shape %s' % (x.shape,))
    if x.shape[1] == 2:
        return x
    if x.shape[1] == 1:
        return np.repeat(x, 2, axis=1)
    if x.shape[0] in (1, 2) and x.shape[1] > 2:
        return _stereo(x.T)
    return x[:, :2].copy()


def _fit(x, n):
    """Cut or zero-pad (N, 2) to exactly n samples."""
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros((n - len(x), x.shape[1]))])


def _decode_ffmpeg(path):
    """Decode any audio file to float64 (N, 2) at 48 kHz with ffmpeg (data only: nothing in the file is executed)."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-map', '0:a:0', '-f', 'f32le',
                        '-acodec', 'pcm_f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True)
    if r.returncode != 0:
        raise IOError('epic_mix.load: ffmpeg could not decode %s: %s' % (path, r.stderr.decode(errors='replace')[-400:]))
    return np.frombuffer(r.stdout, '<f4').astype(np.float64).reshape(-1, 2)


def load(path, dur=None, warn=None):
    """wav path (or array / Sfx) -> float64 (N, 2) at 48 kHz. Mono (N,), (N, 1) or a mono file -> L = R (R7). PCM wavs
    via audio.read_wav, anything else (float wav, flac, mp3, m4a) decoded by ffmpeg; other sample rates resampled.
    dur: cut / zero-pad to exactly round(dur * 48000) samples. warn: optional list that collects notes."""
    if path is None:
        return None
    if isinstance(path, (str, os.PathLike)):
        p = os.fspath(path)
        if not os.path.exists(p):
            raise FileNotFoundError('epic_mix.load: %s' % p)
        try:
            x, sr = A.read_wav(p)
        except (wave.Error, EOFError, ValueError):
            x, sr = _decode_ffmpeg(p), SR
        if sr != SR:
            from fractions import Fraction
            fr = Fraction(SR, int(sr)).limit_denominator(1000)
            x = signal.resample_poly(np.asarray(x, dtype=np.float64), fr.numerator, fr.denominator, axis=0)
            if warn is not None:
                warn.append('%s: %d Hz resampled to %d Hz' % (os.path.basename(p), sr, SR))
        x = _stereo(x)
    else:
        x = _stereo(path)
    if dur is not None:
        n = _n(dur)
        if warn is not None and len(x) != n:
            lost = x[n:]
            if len(x) > n and np.any(lost):
                warn.append('%s: %.3f s past dur cut (max %.1f dBFS)' % (
                    os.path.basename(os.fspath(path)) if isinstance(path, (str, os.PathLike)) else 'array',
                    (len(x) - n) / SR, float(db(np.abs(lost).max()))))
        x = _fit(x, n)
    return x


def write_wav(path, x, bits=24):
    """48 kHz stereo wav. 24-bit uses the exact inverse of audio.read_wav's scaling (x * 2^23, clipped to the 24-bit
    range), so read -> write -> read is lossless (SHARED_REQUESTS ek_frame R5). Written to a temp name, then renamed."""
    x = _stereo(x)
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    tmp = path + '.part'
    if bits == 24:
        q = np.clip(np.round(x * 8388608.0), -8388608, 8388607).astype('<i4')
        raw = q.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
        with wave.open(tmp, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(3)
            w.setframerate(SR)
            w.writeframes(raw)
    else:
        A._write_wav(tmp, x, bits)
    os.replace(tmp, path)
    return path


def _sha(path, k=16):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:k]


def cpad(x, p):
    """Circular pad: the last p samples before x, the first p after it (any p, wraps for p > len(x))."""
    n = len(x)
    if p <= 0:
        return x
    return x[np.arange(-p, n + p) % n]


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return [_jsonable(v) for v in o.tolist()] if o.size <= 64 else '<array %s>' % (o.shape,)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (float, np.floating)):
        v = float(o)
        return v if math.isfinite(v) else None
    return o


def _r(x, k=2):
    return None if x is None else round(float(x), k)


# ============================================================================================ levels / analysis
def _level_curve(x, win=0.01):
    """10 ms level (dB) per sample: moving mean of the louder channel's power (audio.compressor_gain's detector)."""
    p = np.square(_stereo(x)).max(1)
    return 10 * np.log10(np.maximum(uniform_filter1d(p, max(1, _n(win))), 1e-20))


def _level_pct(x, pct=98.0, win=0.01, floor_db=45.0):
    """pct-th percentile (dB) of the 10 ms level over the samples within floor_db of the loudest one (silence and
    near-silence do not count). The glue threshold is _level_pct(bus, 98) - 3, the VO compressor's _level_pct(vo, 90) - 4."""
    lv = _level_curve(x, win)
    if not len(lv) or lv.max() <= -199.0:
        return -200.0
    return float(np.percentile(lv[lv > lv.max() - floor_db], pct))


def speech_mask(v, hold=0.25, thresh_db=-30.0, win=0.01, floor_db=40.0):
    """Per-sample speech activity of a VO stem (bool array, len(v)): the 10 ms RMS of the channel mean above the
    median speech level + thresh_db (-30 dB: a word's decaying tail stays speech until it is 30 dB under the voice; the
    median is taken over the samples within floor_db of the loudest one), held `hold` s after each active sample so
    the gaps between syllables count as speech. hold=0.02 gives the voiced runs themselves."""
    x = _stereo(v).mean(1)
    if not len(x):
        return np.zeros(0, bool)
    lv = 10 * np.log10(np.maximum(uniform_filter1d(x * x, max(1, _n(win))), 1e-20))
    if lv.max() < -150.0:
        return np.zeros(len(x), bool)
    ref = float(np.median(lv[lv > lv.max() - floor_db]))
    act = lv > ref + thresh_db
    h = _n(hold) if hold else 0
    if h > 0:
        act = maximum_filter1d(act.astype(np.uint8), size=h + 1, origin=h // 2, mode='constant',
                              cval=0) > 0                     # out[i] = any(act[i-h .. i]), nothing before 0
    return act


def _spans(mask, min_s=0.0):
    """[(t0, t1)] seconds of the True runs of a per-sample mask."""
    m = np.asarray(mask, bool)
    if not m.any():
        return []
    d = np.diff(np.concatenate([[0], m.astype(np.int8), [0]]))
    a, b = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return [(round(i / SR, 4), round(j / SR, 4)) for i, j in zip(a, b) if (j - i) / SR >= min_s]


def _tp(y, loop=False):
    """True peak (dBTP) of a crop; loop=True measures it across the seam too (the reel plays in a loop)."""
    if loop and len(y) > _n(0.1):
        k = _n(0.05)
        y = np.concatenate([y[-k:], y, y[:k]])
    return A.true_peak(y)


def _speech_frames(vo, speech=None, top_lu=None):
    """(frame times, VO momentary loudness, speech-frame mask): 400 ms / 50 ms hop windows whose centre is speech
    (speech_mask) and whose VO loudness is within top_lu (15) of the VO's loudest frame."""
    top_lu = SPEC['speech_top_lu'] if top_lu is None else top_lu
    tt, lv = A.loudness_curve(vo)
    sp = speech_mask(vo, SPEC['speech_hold_s'], SPEC['speech_thresh_db']) if speech is None else speech
    idx = np.clip((tt * SR).astype(int), 0, len(vo) - 1)
    return tt, lv, sp[idx] & (lv > lv.max() - top_lu)


def vo_margins(vo, music=None, sfx=None, speech=None):
    """Speech-frame margins (LU) of the VO over the music, the SFX and both together (the reels' rough-mix method):
    momentary loudness of each stem at mix gain on the speech frames of _speech_frames; another stem is floored at
    -70 LUFS (the absolute gate), so a frame with no music counts as 'far under the VO', not as infinity."""
    vo = _stereo(vo)
    if not np.any(vo):
        return dict(speech_frames=0, vo_over_music=None, vo_over_sfx=None, vo_over_bed=None)
    tt, lv, spk = _speech_frames(vo, speech)
    out = dict(speech_frames=int(spk.sum()))

    def stat(o):
        if o is None or not np.any(o) or not spk.any():
            return None
        _, lo = A.loudness_curve(o)
        d = (lv - np.maximum(lo, -70.0))[spk]
        k = int(np.argmin(d))
        return dict(median=_r(np.median(d)), p10=_r(np.percentile(d, 10)), min=_r(d[k]),
                    min_at_s=_r(tt[spk][k], 3))
    has_m = music is not None and np.any(music)
    has_s = sfx is not None and np.any(sfx)
    out['vo_over_music'] = stat(music if has_m else None)
    out['vo_over_sfx'] = stat(sfx if has_s else None)
    bed = (music if has_m else 0.0) + (sfx if has_s else 0.0)
    out['vo_over_bed'] = stat(bed if (has_m or has_s) else None)
    return out


def _load_words(words, offset=0.0):
    if words is None:
        return []
    if isinstance(words, (str, os.PathLike)):
        with open(words) as fh:
            words = json.load(fh)
        if isinstance(words, dict):
            words = words.get('words', [])
    out = []
    for w in words:
        if isinstance(w, dict):
            if w.get('start') is None or w.get('end') is None:
                continue
            out.append(dict(word=str(w.get('word', w.get('rom', ''))), line=w.get('line'),
                            start=float(w['start']) + offset, end=float(w['end']) + offset))
        else:
            out.append(dict(word=str(w[2]) if len(w) > 2 else '', line=None, start=float(w[0]) + offset,
                            end=float(w[1]) + offset))
    return out


def _syllables(word):
    """Rough syllable count of a Roman Hinglish word (vowel groups; 'y' counts as a vowel)."""
    return max(1, len(re.findall(r'[aeiouy]+', re.sub(r'[^a-z]', '', word.lower()))))


def word_margins(vo, music=None, sfx=None, words=None, offset=0.0, req=None, req_one=None):
    """Per-word VO level over the music and over the bed (music + SFX): K-weighted energy over each word's own span
    (no 400 ms smear). LEAD_DECISIONS 1: >= 8 LU on every word, 7 LU tolerated on one-syllable words."""
    req = SPEC['check_word_lu'] if req is None else req
    req_one = SPEC['check_word_one_syllable_lu'] if req_one is None else req_one
    ws = [w for w in _load_words(words, offset) if w['end'] - w['start'] >= 0.04]
    if not ws:
        return None
    vo = _stereo(vo)
    kv = np.square(A.kweight(vo)).sum(1)
    km = np.square(A.kweight(_stereo(music))).sum(1) if music is not None and np.any(music) else np.zeros(len(vo))
    ks = np.square(A.kweight(_stereo(sfx))).sum(1) if sfx is not None and np.any(sfx) else np.zeros(len(vo))
    rows = []
    for w in ws:
        i0, i1 = max(0, _n(w['start'])), min(len(vo), _n(w['end']))
        if i1 - i0 < 8:
            continue
        ev = 10 * np.log10(kv[i0:i1].mean() + 1e-20)
        em = 10 * np.log10(km[i0:i1].mean() + 1e-20)
        eb = 10 * np.log10(km[i0:i1].mean() + ks[i0:i1].mean() + 1e-20)
        one = _syllables(w['word']) <= 1
        need = req_one if one else req
        rows.append(dict(word=w['word'], line=w['line'], start=round(w['start'], 3), end=round(w['end'], 3),
                         over_music=round(min(ev - em, 99.0), 1), over_bed=round(min(ev - eb, 99.0), 1),
                         one_syllable=one, need=need))
    if not rows:
        return None
    om = np.array([r['over_music'] for r in rows])
    ob = np.array([r['over_bed'] for r in rows])
    below_m = [r for r in rows if r['over_music'] < r['need']]
    below_b = [r for r in rows if r['over_bed'] < r['need']]
    return dict(n=len(rows), over_music=dict(median=_r(np.median(om), 1), min=_r(om.min(), 1)),
                over_bed=dict(median=_r(np.median(ob), 1), min=_r(ob.min(), 1)),
                below_over_music=below_m, below_over_bed=below_b,
                worst5_over_bed=sorted(rows, key=lambda r: r['over_bed'])[:5],
                pass_music=not below_m, pass_bed=not below_b)


# ============================================================================================ VO chain
def vo_chain(x, lufs=SPEC['vo_lufs'], *, loop=False, crop=None, report=None):
    """Series VO polish: HPF 80 Hz (12 dB/oct) -> -2 dB @ 300 Hz (Q 1.0) -> +2 dB @ 3.2 kHz (Q 0.9) -> +1.5 dB high
    shelf @ 10 kHz -> 3:1 compressor (soft knee 6 dB, 8 / 120 ms, RMS 10 ms, threshold 4 dB under the 90th-percentile
    10 ms level) -> lufs (-16.0) integrated (None: no normalisation). Returns an array of the input's length (stereo).
    crop: slice of the reel inside an already padded x (statistics and loudness from it); loop=True pads circularly
    itself (2 s) so the filters and the compressor are in their loop state at sample 0. report: dict filled with the
    measured numbers (threshold, GR, loudness)."""
    x = _stereo(x)
    n = len(x)
    if loop and crop is None:
        p = _n(2.0)
        xp, sl, own = cpad(x, p), slice(p, p + n), True
    else:
        xp, sl, own = x, (crop if crop is not None else slice(0, n)), False
    if not np.any(xp[sl]):
        if report is not None:
            report.update(silent=True)
        return np.zeros((n, 2)) if own else np.zeros_like(xp)
    S = SPEC
    y = A.hp(xp, S['vo_hpf_hz'], S['vo_hpf_order'])
    for kind, f, q, g in S['vo_eq']:
        y = A.eq(y, kind, f, q, g)
    thr = _level_pct(y[sl], 90.0) - S['vo_comp_below_p90_db']
    gr = A.compressor_gain(y, thresh_db=thr, ratio=S['vo_comp_ratio'], knee_db=S['vo_comp_knee_db'],
                           attack=S['vo_comp_attack'], release=S['vo_comp_release'], rms=S['vo_comp_rms'])
    y = y * undb(gr)[:, None]
    l_pre = A.loudness(y[sl])
    if lufs is not None:
        y = y * undb(lufs - l_pre)
    if report is not None:
        g = gr[sl]
        act = _level_curve(xp[sl]) > _level_pct(xp[sl], 50.0) - 20.0
        report.update(input_lufs=_r(A.loudness(xp[sl])), comp_threshold_dbfs=_r(thr),
                      comp_max_gr_db=_r(-g.min()), comp_gr_p99_db=_r(-np.percentile(g[act], 1)) if act.any() else None,
                      comp_gr_median_db=_r(-np.median(g[act])) if act.any() else None,
                      lufs=_r(A.loudness(y[sl])), tp_dbtp=_r(_tp(y[sl], own)))
    return y[sl] if own else y


# ============================================================================================ glue / master
def _window_curve(n, t0, wins, ramp, period=None):
    """0..1 curve over a timeline whose first sample is reel time t0: 1 inside each (a, b), raised-cosine ramps of
    `ramp` s outside; period (loop length) adds the circular copies of each window."""
    t = t0 + np.arange(n) / SR
    w = np.zeros(n)
    for a, b in wins or ():
        for k in ((-1, 0, 1) if period else (0,)):
            aa, bb = float(a) + k * (period or 0.0), float(b) + k * (period or 0.0)
            up = np.clip((t - (aa - ramp)) / ramp, 0, 1)
            dn = np.clip(((bb + ramp) - t) / ramp, 0, 1)
            w = np.maximum(w, 0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn)))
    return w


def glue_gain(bus, *, crop=None, protect=(), protect_cap_db=0.0, t0=0.0, period=None, ratio=None,
              below_p98_db=None, knee_db=None, attack=None, release=None, rms=None, threshold_db=None):
    """Bus glue: 2:1, soft knee 6 dB, 6 / 150 ms, RMS 8 ms, threshold 3 dB under the 98th-percentile 10 ms level of
    the bus (of bus[crop] for a padded bus). protect=[(t0, t1)] (reel seconds): inside those windows (30 ms raised-
    cosine ramps) the glue may take at most protect_cap_db (0 = none; log_kya_kahenge found 1.5 dB keeps the limiter
    <= ~3 dB on its reveal). Returns (linear gain curve (N,), info)."""
    S = SPEC
    ratio = S['glue_ratio'] if ratio is None else ratio
    below = S['glue_below_p98_db'] if below_p98_db is None else below_p98_db
    bus = _stereo(bus)
    sl = crop if crop is not None else slice(0, len(bus))
    thr = (_level_pct(bus[sl], 98.0) - below) if threshold_db is None else float(threshold_db)
    gr = A.compressor_gain(bus, thresh_db=thr, ratio=ratio, knee_db=S['glue_knee_db'] if knee_db is None else knee_db,
                           attack=S['glue_attack'] if attack is None else attack,
                           release=S['glue_release'] if release is None else release,
                           rms=S['glue_rms'] if rms is None else rms)
    raw_max = float(-gr[sl].min()) if len(gr[sl]) else 0.0
    prot = [(float(a), float(b)) for a, b in (protect or ())]
    if prot:
        w = _window_curve(len(bus), t0, prot, S['protect_ramp_s'], period)
        gr = gr * (1.0 - w) + np.maximum(gr, -abs(protect_cap_db)) * w
    info = dict(threshold_db=_r(thr), ratio=ratio, max_gr_db=_r(-gr[sl].min()) if len(gr[sl]) else 0.0,
                max_gr_unprotected_db=_r(raw_max), protect=prot, protect_cap_db=abs(protect_cap_db) if prot else None)
    return undb(gr), info


def glue(x, **kw):
    """The bus glue applied: returns x * glue_gain(x, **kw)[0] (stereo)."""
    g, _ = glue_gain(x, **kw)
    return _stereo(x) * g[:, None]


def _solve_gain(x, sl, target, ceiling, tol, S):
    """Master gain g (dB) so that loudness((x * g * limiter)[sl]) == target; the limiter (audio.limiter_gain: 4x true-peak
    detection, lookahead, soft knee) is recomputed for every g. Bracketed regula falsi with bisection steps."""
    pk = A.tp_envelope(x)
    xc = x[sl]
    g = target - A.loudness(xc)
    lo = hi = best = None
    for it in range(40):
        gl = A.limiter_gain(None, ceiling, lookahead=S['limiter_lookahead_s'], release=S['limiter_release_s'],
                            knee_db=S['limiter_knee_db'], pk=pk * undb(g))
        L = A.loudness(xc * (undb(g) * gl[sl])[:, None])
        if best is None or abs(L - target) < abs(best[2] - target):
            best = (g, gl, L, it + 1)
        if abs(L - target) < tol:
            break
        if L < target:
            lo = (g, L)
        else:
            hi = (g, L)
        if lo and hi:
            span = hi[0] - lo[0]
            if span < 1e-4:
                break
            gn = lo[0] + (target - lo[1]) * span / max(hi[1] - lo[1], 1e-9)
            g = gn if (lo[0] + 0.05 * span < gn < hi[0] - 0.05 * span and it % 3 != 2) else 0.5 * (lo[0] + hi[0])
        else:
            g += float(np.clip((target - L) * 1.1, -30.0, 30.0))
    return best


def _master(bus, sl, *, glue=True, protect=(), protect_cap_db=0.0, t0=0.0, period=None, loop=False, S=SPEC):
    """Glue + gain + limiter on a (possibly padded) bus, measured on bus[sl]. Returns (y, curve, info)."""
    n = len(bus)
    if not np.any(bus[sl]):
        return np.zeros((n, 2)), np.zeros(n), dict(silent=True)
    if glue:
        gg, ginfo = glue_gain(bus, crop=sl, protect=protect, protect_cap_db=protect_cap_db, t0=t0, period=period,
                              **(glue if isinstance(glue, dict) else {}))
    else:
        gg, ginfo = np.ones(n), None
    x = bus * gg[:, None]
    target, tpmax = S['master_lufs'], S['tp_max_dbtp']
    ceiling = S['limiter_ceiling_dbfs']
    for attempt in range(6):
        g, gl, L, its = _solve_gain(x, sl, target, ceiling, S['master_iter_tol_lu'], S)
        y = x * (undb(g) * gl)[:, None]
        tp = _tp(y[sl], loop)
        if tp <= tpmax - 0.05:
            break
        ceiling -= tp - (tpmax - 0.1)
    curve = gg * undb(g) * gl
    yc = y[sl]
    lim = db(np.maximum(gl[sl], 1e-12))
    over3 = lim < -S['check_limiter_gr_db']
    info = dict(lufs=_r(A.loudness(yc), 3), tp_dbtp=_r(tp, 3), lra=_r(A.loudness_range(yc)),
                max_momentary=_r(A.momentary_max(yc)), max_short_term=_r(A.momentary_max(yc, 3.0)),
                master_gain_db=_r(g, 3), limiter_ceiling_dbfs=_r(ceiling, 3), iterations=its,
                glue_threshold_db=ginfo['threshold_db'] if ginfo else None,
                glue_max_gr_db=ginfo['max_gr_db'] if ginfo else 0.0, glue=ginfo,
                limiter_max_gr_db=_r(-lim.min()), limiter_max_gr_at_s=_r(np.argmin(lim) / SR, 3),
                limiter_gr_over_1db_s=_r(np.sum(lim < -1.0) / SR, 3), limiter_gr_over_2db_s=_r(np.sum(lim < -2.0) / SR, 3),
                limiter_gr_over_3db_s=_r(np.sum(over3) / SR, 3), limiter_gr_over_3db_spans=_spans(over3))
    return y, curve, info


def master(bus, *, glue=True, protect=(), protect_cap_db=0.0, loop=False, pad=None, target=None, ceiling=None,
           tp_max=None):
    """Bus glue (2:1, protect windows) + gain + 4x true-peak limiter at -2.3 dBFS iterated to -14.0 LUFS, TP <= -2.0.
    loop=True runs on a circularly padded copy (pad s, default 4) and crops. Returns (y, curve, info): curve = the
    whole per-sample linear gain (glue x gain x limiter); multiply any stem of the bus by it."""
    S = dict(SPEC)
    for k, v in (('master_lufs', target), ('limiter_ceiling_dbfs', ceiling), ('tp_max_dbtp', tp_max)):
        if v is not None:
            S[k] = float(v)
    bus = _stereo(bus)
    n = len(bus)
    if loop:
        p = _n(S['loop_pad_s'] if pad is None else pad)
        y, curve, info = _master(cpad(bus, p), slice(p, p + n), glue=glue, protect=protect,
                                 protect_cap_db=protect_cap_db, t0=-p / SR, period=n / SR, loop=True, S=S)
        return y[p:p + n], curve[p:p + n], info
    return _master(bus, slice(0, n), glue=glue, protect=protect, protect_cap_db=protect_cap_db, S=S)


# ============================================================================================ SFX stem from cues / beds
def _known(name):
    try:
        A.resolve(name, fuzzy=False)
        return True
    except KeyError:
        return False


def _ensure_sounds(names):
    """Every cue / bed name must resolve exactly (audio.resolve's fuzzy fallback would silently swap a sound): register
    sfx_jawad and epic_sfx when a name is unknown, then raise KeyError for whatever is still missing."""
    names = sorted({n for n in names if n})
    missing = [n for n in names if not _known(n)]
    notes = []
    if missing:
        for mod in ('sfx_jawad', 'epic_sfx'):
            try:
                importlib.import_module(mod).register()
            except Exception as e:                    # noqa: BLE001  (a kit module that is not there yet)
                notes.append('%s: %s' % (mod, e))
        missing = [n for n in names if not _known(n)]
    if missing:
        raise KeyError('epic_mix: unknown sound(s) %s (register them first: epic_sfx.register(), sfx_jawad.register()'
                       ' or the reel module\'s register()); %s' % (missing, '; '.join(notes)))


def _cue_name(c):
    if isinstance(c, (list, tuple)):
        return c[1]
    return c.get('name', c.get('sfx'))


def _bed_names(bed):
    if bed is None:
        return []
    specs = bed if isinstance(bed, (list, tuple)) else [bed]
    return [s if isinstance(s, str) else s['name'] for s in specs]


def _fold(y, p0, n):
    """Fold an extended render (reel sample 0 at y[p0]) onto a loop of n samples: y[i] lands on (i - p0) mod n."""
    out = np.zeros((n, y.shape[1]))
    i = 0
    while i < len(y):
        r = (i - p0) % n
        m = min(n - r, len(y) - i)
        out[r:r + m] += y[i:i + m]
        i += m
    return out


def _loop_bed(bed, dur, n):
    """Exact-length seamless bed loop (n samples): every full-length segment is tiled from its sound and its head is
    crossfaded (equal power, 0.5 s) with the samples that follow sample n-1, so the seam continues the loop; partial
    segments (t0 > 0 or t1 < dur) fade in / out like audio.mix's beds. Returns (bus at unit level, info)."""
    out = np.zeros((n, 2))
    info = []
    for s in (bed if isinstance(bed, (list, tuple)) else [bed]):
        s = dict(name=s) if isinstance(s, str) else dict(s)
        loop = np.asarray(A.sound(s['name'], **s.get('params', {})), dtype=np.float64)
        L = len(loop)
        t0, t1 = float(s.get('t0', 0.0)), float(s.get('t1', dur))
        fade = float(s.get('fade', 0.6))
        off = _n(float(s.get('offset', 0.0))) % L
        g = undb(float(s.get('gain_db', 0.0)))
        if t0 <= 0.0 and t1 >= dur:
            X = max(2, min(_n(0.5), L // 4, n // 4))
            seg = loop[(off + np.arange(n + X)) % L]
            y = seg[:n].copy()
            th = (0.5 * np.pi * (np.arange(X) + 0.5) / X)[:, None]
            y[:X] = seg[:X] * np.sin(th) + seg[n:n + X] * np.cos(th)
            out += y * g
        else:
            i0, i1 = _n(max(t0, 0.0)), min(n, _n(t1))
            if i1 > i0:
                seg = loop[(off + np.arange(i1 - i0)) % L]
                out[i0:i1] += A._fade(seg, fade if t0 > 0 else 0.0, fade if t1 < dur else 0.0) * g
        info.append(dict(name=s['name'], t0=t0, t1=t1, rel_gain_db=float(s.get('gain_db', 0.0)), seamless=True))
    return out, info


def _sfx_from_cues(cues, dur, n, bed, bed_gain_db, tail_fade, loop, S, out_dir, name):
    """SFX stem from a cue list with audio.mix (auto-duck, room send, glue, -18 LUFS, TP <= -2.0, split stems).
    loop=True renders the cues on an extended timeline and folds it back onto the reel (no tail fade), with an
    exact-length seamless bed. Returns (stem (n, 2), info, files)."""
    _ensure_sounds([_cue_name(c) for c in cues] + _bed_names(bed))
    stem_path = os.path.join(out_dir, '%s_sfx_stem.wav' % name)
    files = {}
    if not loop:
        rep = A.mix(list(cues), dur, None, stem_path, bed=bed, bed_gain_db=bed_gain_db, target_lufs=S['sfx_lufs'],
                    tp_ceiling=S['sfx_tp_dbtp'], auto_duck=True, room_send=True, glue=True, split_stems=True,
                    tail_fade=tail_fade, verbose=False)
        x = _fit(_stereo(rep['audio']), n)
        for k, k2 in (('stem', 'sfx_stem'), ('stem_fx', 'sfx_stem_fx'), ('stem_bed', 'sfx_stem_bed')):
            if k in rep['files']:
                files[k2] = rep['files'][k]
        placed, shift = rep['placed'], 0.0
    else:
        cs = [A._norm_cue(c) for c in cues]
        starts, ends = [0.0], [dur]
        for c in cs:
            snd = A.sound(c['name'], **dict(c['params']))
            rate = float(c.get('rate', 1.0))
            ln = len(snd) / SR / rate
            if c.get('dur'):
                ln = min(ln, float(c['dur']))
            st = float(c['t']) - (snd.hit / rate if c['align'] == 'hit' else 0.0)
            starts.append(st)
            ends.append(st + ln)
        pre = max(0.0, -min(starts)) + 0.05
        post = max(0.0, max(ends) - dur) + 2.0         # + the 'studio' room send's tail
        shifted = [dict(c, t=float(c['t']) + pre) for c in cs]
        rep = A.mix(shifted, dur + pre + post, bed=None, target_lufs=S['sfx_lufs'], tp_ceiling=S['sfx_tp_dbtp'],
                    auto_duck=True, room_send=True, glue=True, tail_fade=0.0, verbose=False)
        fx = _fold(_stereo(rep['audio']), _n(pre), n)
        x = fx
        bed_out = None
        if bed is not None and np.any(fx):
            bb, _ = _loop_bed(bed, dur, n)
            p = _n(2.0)
            bb = A.sidechain(cpad(bb, p), cpad(fx, p), depth_db=S['bed_duck_sfx_db'])[p:p + n]
            bed_out = bb * undb(S['sfx_lufs'] + bed_gain_db + S['bed_anchor_db'] - A.loudness(bb))
            g = 0.0
            for _ in range(6):                          # SFX bus gain so that SFX + anchored bed sit at -18 LUFS
                L = A.loudness(fx * undb(g) + bed_out)
                if abs(L - S['sfx_lufs']) < 0.02:
                    break
                g += S['sfx_lufs'] - L
            x = fx * undb(g) + bed_out
            files['sfx_stem_fx'] = write_wav(os.path.join(out_dir, '%s_sfx_stem_fx.wav' % name), fx * undb(g))
            files['sfx_stem_bed'] = write_wav(os.path.join(out_dir, '%s_sfx_stem_bed.wav' % name), bed_out)
        files['sfx_stem'] = write_wav(stem_path, x)
        placed, shift = rep['placed'], pre
    info = dict(source='sfx_cues', cues=len(cues), loop=bool(loop), stem_lufs=_r(A.loudness(x)),
                stem_tp_dbtp=_r(A.true_peak(x)), limiter_max_gr_db=rep.get('limiter_max_gr_db'),
                comp_max_gr_db=rep.get('comp_max_gr_db'), bed=_bed_names(bed), bed_gain_db=bed_gain_db if bed else None,
                bed_lufs=rep.get('bed_lufs'), tail_fade=0.0 if loop else tail_fade,
                placed=[dict(p, t=round(p['t'] - shift, 4), start=round(p['start'] - shift, 4),
                             hit=round(p['hit'] - shift, 4)) for p in placed])
    info['warnings'] = [p for p in info['placed'] if p.get('warn')]
    return x, info, files


def _bed_for_stem(bed, dur, n, s, bed_gain_db, loop, S):
    """A bed added to a finished SFX stem the way audio.mix anchors it: integrated sfx_lufs + bed_gain_db + 8 LUFS,
    sidechained 5 dB under the SFX."""
    _ensure_sounds(_bed_names(bed))
    if loop:
        bb, info = _loop_bed(bed, dur, n)
    else:
        bb, info = A._beds(bed, dur, n)
    if np.any(s):
        p = _n(2.0) if loop else 0
        bb = A.sidechain(cpad(bb, p), cpad(s, p), depth_db=S['bed_duck_sfx_db'])[p:p + n]
    if np.any(bb):
        bb = bb * undb(S['sfx_lufs'] + bed_gain_db + S['bed_anchor_db'] - A.loudness(bb))
    return bb, info


def _word_topup(v, s, m, sl, words, offset, floor, max_db, t0, period, S, curve=None):
    """Opt-in 'gentle level ride' of the music under weak words (LEAD_DECISIONS 1): every word whose K-weighted VO
    level over the bed (music + SFX, over the word's own span) is under `floor` (floor - 1 on one-syllable words) gets
    an extra music duck, fully down from 100 ms before the word to 150 ms after it, raised-cosine ramps of 80 ms in and
    350 ms out, deep enough to reach the floor + 0.25 LU, capped at max_db; iterated (neighbours' ducks overlap).
    The SFX is never touched (a word masked by the SFX alone stays short and is reported). curve = the bus's per-sample
    gain (glue x limiter) on the same timeline: the levels are weighted by it, because the glue takes more off the VO's
    peaks than off the music between them (measured: ~1 LU on short words). Returns (music, info)."""
    ws = [w for w in _load_words(words, offset) if w['end'] - w['start'] >= 0.04]
    if not ws or not np.any(m[sl]):
        return m, None
    n = len(m)
    c2 = np.square(curve[sl]) if curve is not None else np.ones(sl.stop - sl.start)
    kv = np.square(A.kweight(v[sl])).sum(1) * c2
    ks = np.square(A.kweight(s[sl])).sum(1) * c2
    km = np.square(A.kweight(m[sl])).sum(1) * c2
    spans = [(max(0, _n(w['start'])), min(len(kv), _n(w['end']))) for w in ws]

    def lev(k, g2=None):
        return np.array([10 * np.log10((k[a:b] * (g2[a:b] if g2 is not None else 1.0)).mean() + 1e-20) if b > a
                         else -200.0 for a, b in spans])
    ev, es = lev(kv), lev(ks)
    need = np.array([floor - (S['check_word_lu'] - S['check_word_one_syllable_lu']) if _syllables(w['word']) <= 1
                     else floor for w in ws])
    extra = np.zeros(len(ws))
    pre, post, r_in, r_out = 0.10, 0.15, 0.08, 0.35
    copies = (-1, 0, 1) if period else (0,)

    def duck_curve():
        dc = np.zeros(n)
        for i, w in enumerate(ws):
            if extra[i] <= 0:
                continue
            for k in copies:
                a = w['start'] - pre + k * (period or 0.0)
                b = w['end'] + post + k * (period or 0.0)
                j0, j1 = max(0, _n(a - r_in - t0)), min(n, _n(b + r_out - t0))
                if j1 <= j0:
                    continue
                tt = t0 + np.arange(j0, j1) / SR
                c = np.minimum(np.clip((tt - (a - r_in)) / r_in, 0, 1), np.clip(((b + r_out) - tt) / r_out, 0, 1))
                dc[j0:j1] = np.maximum(dc[j0:j1], extra[i] * (0.5 - 0.5 * np.cos(np.pi * c)))
        return dc
    dc = np.zeros(n)
    for it in range(8):
        em = lev(km, np.square(undb(-dc[sl])) if extra.any() else None)
        margin = ev - 10 * np.log10(10 ** (em / 10) + 10 ** (es / 10))
        short = (margin < need - 0.02) & (extra < max_db - 1e-6) & (ev > -100)
        if not short.any():
            break
        for i in np.flatnonzero(short):
            allowed = 10 * np.log10(max(10 ** ((ev[i] - need[i] - 0.25) / 10) - 10 ** (es[i] / 10), 1e-20))
            extra[i] = min(max_db, extra[i] + max(em[i] - allowed, 0.25))
        dc = duck_curve()
    info = dict(floor_lu=floor, max_db=max_db, iterations=it + 1, bus_weighted=curve is not None,
                topped=[dict(word=w['word'], start=round(w['start'], 3), extra_db=round(float(e), 2))
                        for w, e in zip(ws, extra) if e > 0],
                still_short=[dict(word=w['word'], start=round(w['start'], 3), margin=round(float(g), 1),
                                  need=float(q), sfx_alone_over=round(float(ev_ - es_), 1))
                             for w, g, q, ev_, es_ in zip(ws, margin, need, ev, es) if g < q - 0.05])
    return (m * undb(-dc)[:, None] if extra.any() else m), info


# ============================================================================================ mix_reel
def _place(x, offset, n, loop, warn, what):
    """Put x (already stereo) on an n-sample reel timeline starting at `offset` s (negative: its head is cut).
    loop=True wraps whatever runs past the end onto the start."""
    out = np.zeros((n, 2))
    if x is None:
        return out
    i = _n(offset)
    if loop:
        return _fold(x, -i, n)                       # x[j] lands on (j + i) mod n: a loop rotates, nothing is lost
    src = x[max(-i, 0):]
    i = max(i, 0)
    m = max(0, min(len(src), n - i))
    out[i:i + m] = src[:m]
    lost = src[m:]
    if len(lost) and np.any(np.abs(lost) > 2.0 ** -23):
        warn.append('%s: %.3f s past dur cut (max %.1f dBFS)' % (what, len(lost) / SR, float(db(np.abs(lost).max()))))
    return out


def _desc(x):
    if x is None:
        return None
    if isinstance(x, (str, os.PathLike)):
        p = os.fspath(x)
        return dict(path=p, sha256=_sha(p) if os.path.exists(p) else None)
    a = np.asarray(x)
    return dict(array=list(a.shape))


def mix_reel(name, dur, vo=None, music=None, sfx_cues=None, bed=None, bed_gain_db=-30.0, out_dir=None, vo_offset=0.0,
             sfx=None, *, words=None, tail_fade=0.4, loop=False, pad=None, protect=(), protect_cap_db=0.0, glue=True,
             hero_times=None, music_gain_db=0.0, word_floor_lu=None, word_floor_max_db=9.0, spec=None, png=True,
             write_report=True, verbose=True):
    """Mix + master one reel: version A (VO + SFX + music), version B (VO + SFX, mastered on its own) and stems at A's
    exact gains (they sum to A). See the module docstring for the chain, the files and the report keys.
      vo / music / sfx : wav path or array (mono or stereo, any length), or None.  sfx_cues : cue list for audio.mix
      (instead of sfx); bed / bed_gain_db : SFX bed (with sfx_cues or a stem); tail_fade : audio.mix's SFX tail fade.
      vo_offset : seconds the VO is shifted on the reel (0.0 for placed stems, 0.3 for a raw take).
      words : .words.json path / list (reel time before vo_offset) for the per-word check; hero_times : hero hit times
      (s) for the limiter check (taken from sfx_cues when not given). protect / protect_cap_db : glue windows (R6b).
      loop : loop-safe chain (R6c), pad : its circular pad (s, default 4). glue : False | True | dict of glue_gain
      options. music_gain_db : static trim after the -18 LUFS levelling. spec : dict of SPEC overrides for this call.
      word_floor_lu (opt-in, needs words=): extra music duck under each word whose VO-over-bed margin is under it
      (one-syllable words: 1 LU less), capped at word_floor_max_db (_word_topup); None (default) = the spec's chain."""
    t_start = time.time()
    S = dict(SPEC)
    S.update(spec or {})
    dur = float(dur)
    N = _n(dur)
    out_dir = os.path.abspath(out_dir or A.AUDIO)
    os.makedirs(out_dir, exist_ok=True)
    warn = []
    if sfx is not None and sfx_cues is not None:
        raise ValueError('mix_reel: pass sfx= (a stem) or sfx_cues= (a cue list), not both')
    files = {}
    # ---- 0. inputs on the reel timeline
    v0 = _place(load(vo, warn=warn), vo_offset, N, loop, warn, 'VO') if vo is not None else np.zeros((N, 2))
    if sfx_cues is not None:
        s0, sfx_info, f = _sfx_from_cues(sfx_cues, dur, N, bed, bed_gain_db, tail_fade, loop, S, out_dir, name)
        files.update(f)
    elif sfx is not None:
        s0 = load(sfx, dur, warn)
        sfx_info = dict(source='stem', stem_lufs=_r(A.loudness(s0)) if np.any(s0) else None,
                        stem_tp_dbtp=_r(A.true_peak(s0)) if np.any(s0) else None)
        if bed is not None:
            bb, binfo = _bed_for_stem(bed, dur, N, s0, bed_gain_db, loop, S)
            s0 = s0 + bb
            sfx_info.update(bed=binfo, bed_gain_db=bed_gain_db, bed_lufs=_r(A.loudness(bb)) if np.any(bb) else None)
    else:
        s0 = np.zeros((N, 2))
        sfx_info = None
        if bed is not None:
            s0, binfo = _bed_for_stem(bed, dur, N, s0, bed_gain_db, loop, S)
            sfx_info = dict(source='bed only', bed=binfo)
    m0 = load(music, dur, warn) if music is not None else np.zeros((N, 2))
    has_v, has_s, has_m = bool(np.any(v0)), bool(np.any(s0)), bool(np.any(m0))
    if not (has_v or has_s or has_m):
        raise ValueError('mix_reel(%r): every input is silent or missing' % name)
    for what, given, has in (('vo', vo is not None, has_v), ('music', music is not None, has_m),
                             ('sfx', sfx is not None or sfx_cues is not None, has_s)):
        if given and not has:
            warn.append('%s input is digital silence' % what)
    # ---- padded working timeline (loop: circular pads; the reel is the slice sl)
    P = _n(S['loop_pad_s'] if pad is None else pad) if loop else 0
    sl = slice(P, P + N)
    t0, period = -P / SR, (dur if loop else None)

    def cp(x):
        return cpad(x, P) if P else x.copy()
    # ---- 1. VO
    vinfo = {}
    v = vo_chain(cp(v0), S['vo_lufs'], crop=sl, report=vinfo) if has_v else cp(v0)
    # ---- 2. SFX: -18 LUFS by integrated loudness, -4 dB under the VO
    s = cp(s0)
    if has_s:
        s *= undb(S['sfx_lufs'] - A.loudness(s[sl]))
        if has_v:
            s = A.sidechain(s, v, depth_db=S['sfx_duck_vo_db'], attack=S['sfx_duck_vo_attack'],
                            release=S['sfx_duck_vo_release'])
    # ---- 3. music: -18 (-16 without VO), -3 under the SFX, -9 under the VO, never renormalised after
    m = cp(m0)
    minfo = None
    if has_m:
        mt = S['music_lufs'] if has_v else S['music_lufs_no_vo']
        lm_in = A.loudness(m[sl])
        m *= undb(mt + music_gain_db - lm_in)
        pre_duck = m.copy()
        if has_s:
            m = A.sidechain(m, s, depth_db=S['music_duck_sfx_db'], attack=S['music_duck_sfx_attack'],
                            release=S['music_duck_sfx_release'])
        if has_v:
            m = A.sidechain(m, v, depth_db=S['music_duck_vo_db'], attack=S['music_duck_vo_attack'],
                            release=S['music_duck_vo_release'])
        with np.errstate(divide='ignore', invalid='ignore'):
            dk = db(np.abs(m[sl]).max(1) + 1e-30) - db(np.abs(pre_duck[sl]).max(1) + 1e-30)
        live = np.abs(pre_duck[sl]).max(1) > 1e-6
        minfo = dict(input_lufs=_r(lm_in), level_lufs=_r(mt + music_gain_db), music_gain_db=music_gain_db,
                     lufs_after_duck=_r(A.loudness(m[sl])), duck_max_db=_r(-dk[live].min()) if live.any() else 0.0,
                     duck_median_db=_r(-np.median(dk[live])) if live.any() else 0.0, word_topup=None)
        del pre_duck
    # ---- 4/5. version A and version B (each its own glue threshold, gain and limiter)
    kw = dict(glue=glue, protect=protect, protect_cap_db=protect_cap_db, t0=t0, period=period, loop=loop, S=S)
    if word_floor_lu is not None and has_v and has_m and words:
        # opt-in word ride: pre-bus estimate -> master -> re-solve weighted by that bus curve -> final master
        m_spec = m
        m, _ = _word_topup(v, s, m_spec, sl, words, vo_offset, float(word_floor_lu), float(word_floor_max_db),
                           t0, period, S)
        _, curve0, _ = _master(v + s + m, sl, **kw)
        m, topup = _word_topup(v, s, m_spec, sl, words, vo_offset, float(word_floor_lu), float(word_floor_max_db),
                               t0, period, S, curve=curve0 / max(float(curve0[sl].max()), 1e-12))
        minfo['word_topup'] = topup
        minfo['lufs_after_ride'] = _r(A.loudness(m[sl]))
        del m_spec, curve0
    zA, curveA, infoA = _master(v + s + m, sl, **kw)
    if has_v or has_s:
        zB, curveB, infoB = _master(v + s, sl, **kw)
    else:
        zB, curveB, infoB = np.zeros_like(zA), np.zeros(len(zA)), dict(silent=True)
    # ---- 6. crops, stems at A's whole bus curve
    cA = curveA[sl][:, None]
    yA, yB = zA[sl], zB[sl]
    stems = dict(stem_vo=v[sl] * cA, stem_sfx=s[sl] * cA, stem_music=m[sl] * cA)
    if loop:
        k = _n(1.0)
        for key, z, info in (('A', zA, infoA), ('B', zB, infoB)):
            if not info.get('silent'):
                info['loop_continuity_error_dbfs'] = _r(db(np.abs(z[P + N:P + N + k] - z[P:P + k]).max() + 1e-15), 1)
    for key, y, info in (('A', yA, infoA), ('B', yB, infoB)):
        if not info.get('silent'):
            w = _n(0.05)
            lp_ = np.concatenate([y[-w:], y[:w]])
            d = np.abs(np.diff(lp_, axis=0)).max(1)
            info['seam'] = dict(step=_r(np.abs(y[0] - y[-1]).max(), 6), local_median_step=_r(np.median(d), 6),
                                step_over_median=_r(np.abs(y[0] - y[-1]).max() / max(float(np.median(d)), 1e-12)))
    # ---- write
    paths = {k: os.path.join(out_dir, '%s_%s.wav' % (name, k)) for k in STEM_KEYS}
    write_wav(paths['mix'], yA)
    write_wav(paths['vo_sfx'], yB)
    for k in ('stem_vo', 'stem_sfx', 'stem_music'):
        write_wav(paths[k], stems[k])
    files.update(paths)
    back = {k: load(paths[k]) for k in STEM_KEYS}
    resid = back['stem_vo'] + back['stem_sfx'] + back['stem_music'] - back['mix']
    resid_dbfs = float(db(np.abs(resid).max() + 1e-15))
    del back, resid
    # ---- 7. checks
    sv, ss, sm = stems['stem_vo'], stems['stem_sfx'], stems['stem_music']
    sp = speech_mask(sv, S['speech_hold_s'], S['speech_thresh_db']) if has_v else None
    mg = vo_margins(sv, sm if has_m else None, ss if has_s else None, speech=sp) if has_v else None
    wm = word_margins(sv, sm if has_m else None, ss if has_s else None, words, vo_offset) if (has_v and words) else None
    if hero_times is None and sfx_info and sfx_info.get('placed'):
        hero_times = sorted({p['hit'] for p in sfx_info['placed'] if p['name'] in HERO_NAMES})
    checks = _checks(S, infoA, infoB, mg, wm, hero_times, resid_dbfs, has_v, has_m, has_s)
    rep = dict(
        name=name, version=VERSION, dur=dur, samples=N, sr=SR, bits=24, channels=2, loop=bool(loop),
        pad_s=P / SR if loop else 0.0, vo_offset=float(vo_offset), spec=S,
        inputs=dict(vo=_desc(vo), music=_desc(music), sfx=_desc(sfx), sfx_cues=len(sfx_cues) if sfx_cues else None,
                    bed=_bed_names(bed) or None, words=os.fspath(words) if isinstance(words, (str, os.PathLike)) else
                    (len(words) if words else None)),
        vo_chain=vinfo if has_v else None, sfx=sfx_info, music=minfo,
        A_full=infoA, B_vo_sfx=infoB,
        integrated_lufs=infoA.get('lufs'), true_peak_dbtp=infoA.get('tp_dbtp'), lra_lu=infoA.get('lra'),
        limiter_max_gr_db=infoA.get('limiter_max_gr_db'),
        vo_lufs_in_mix=_r(A.loudness(sv)) if has_v else None, sfx_lufs_in_mix=_r(A.loudness(ss)) if has_s else None,
        music_lufs_in_mix=_r(A.loudness(sm)) if has_m else None,
        vo_over_music_lu=(mg['vo_over_music'] or {}).get('median') if mg else None,
        vo_over_sfx_lu=(mg['vo_over_sfx'] or {}).get('median') if mg else None,
        vo_over_bed_lu=(mg['vo_over_bed'] or {}).get('median') if mg else None,
        margins=mg, words=wm, hero_times=[round(float(h), 4) for h in hero_times] if hero_times else None,
        stems_sum_residual_dbfs=_r(resid_dbfs, 1), checks=checks, warnings=warn, files=files)
    if png:
        files['png'] = _overview(yA, sv, sm, ss, os.path.join(out_dir, '%s_mix.png' % name),
                                 '%s  A %.2f LUFS %.2f dBTP | B %.2f LUFS %.2f dBTP | VO over music %s LU' % (
                                     name, infoA.get('lufs', float('nan')), infoA.get('tp_dbtp', float('nan')),
                                     infoB.get('lufs') if infoB.get('lufs') is not None else float('nan'),
                                     infoB.get('tp_dbtp') if infoB.get('tp_dbtp') is not None else float('nan'),
                                     rep['vo_over_music_lu']), speech=sp, gr_db=db(np.maximum(curveA[sl], 1e-12)) -
                                 float(infoA.get('master_gain_db') or 0.0), hero_times=hero_times)
    rep['seconds'] = round(time.time() - t_start, 1)
    rep = _jsonable(rep)
    if write_report:
        files['report'] = os.path.join(out_dir, '%s_mix.json' % name)
        rep['files'] = _jsonable(files)
        with open(files['report'], 'w') as fh:
            json.dump(rep, fh, indent=1)
    rep['files'] = _jsonable(files)
    if verbose:
        print(report_text(rep))
    return rep


def _checks(S, infoA, infoB, mg, wm, hero_times, resid_dbfs, has_v, has_m, has_s):
    c = {}
    for key, info in (('A', infoA), ('B', infoB)):
        if info.get('silent'):
            continue
        c[key + '_lufs'] = dict(value=info['lufs'], target=S['master_lufs'], tol=S['master_tol_lu'],
                                ok=abs(info['lufs'] - S['master_lufs']) <= S['master_tol_lu'])
        c[key + '_tp'] = dict(value=info['tp_dbtp'], max=S['tp_max_dbtp'], ok=info['tp_dbtp'] <= S['tp_max_dbtp'])
        lo, hi = S['check_lra_lu']
        c[key + '_lra'] = dict(value=info['lra'], range=[lo, hi], ok=lo <= info['lra'] <= hi,
                               note='LEAD_DECISIONS 1 (2.0-9 LU) over sound_design.md 6 (2-8)')
        spans = info['limiter_gr_over_3db_spans']
        off = [sp for sp in spans if hero_times is not None and not any(
            sp[0] - S['check_hero_window_s'] <= h <= sp[1] + S['check_hero_window_s'] for h in hero_times)]
        c[key + '_limiter'] = dict(max_gr_db=info['limiter_max_gr_db'], over_3db_s=info['limiter_gr_over_3db_s'],
                                   spans=spans, off_hero_spans=off if hero_times is not None else None,
                                   ok=info['limiter_gr_over_3db_s'] < S['check_limiter_gr_max_s'] and not off)
    if mg and has_m and mg.get('vo_over_music'):
        c['vo_over_music'] = dict(median=mg['vo_over_music']['median'], need=S['check_vo_over_music_lu'],
                                  ok=mg['vo_over_music']['median'] >= S['check_vo_over_music_lu'])
    if mg and has_s and mg.get('vo_over_sfx'):
        c['vo_over_sfx'] = dict(median=mg['vo_over_sfx']['median'], need=S['check_vo_over_sfx_lu'],
                                ok=mg['vo_over_sfx']['median'] >= S['check_vo_over_sfx_lu'])
    if wm:
        c['words'] = dict(n=wm['n'], below_over_music=len(wm['below_over_music']), below_over_bed=len(wm['below_over_bed']),
                          need=S['check_word_lu'], need_one_syllable=S['check_word_one_syllable_lu'],
                          ok=wm['pass_bed'], note='LEAD_DECISIONS 1: VO >= 8 LU over the bed (music + SFX) on every word')
    c['stems_sum'] = dict(residual_dbfs=_r(resid_dbfs, 1), ok=resid_dbfs <= -90.0)
    c['ok'] = all(v['ok'] for v in c.values() if isinstance(v, dict))
    return c


def report_text(rep):
    a, b = rep.get('A_full') or {}, rep.get('B_vo_sfx') or {}
    s = ['epic_mix %s  %.3f s  (%s)%s' % (rep['name'], rep['dur'], rep['version'], '  LOOP' if rep.get('loop') else '')]
    for lab, i in (('A full  ', a), ('B vo+sfx', b)):
        if i.get('silent'):
            s.append('  %s: silent' % lab)
            continue
        s.append('  %s: %.2f LUFS  %.2f dBTP  LRA %.1f  max mom %.1f  gain %+.2f dB  glue thr %s GR %.1f dB  '
                 'limiter GR %.2f dB (> 3 dB %.3f s)' % (lab, i['lufs'], i['tp_dbtp'], i['lra'], i['max_momentary'],
                                                       i['master_gain_db'], i['glue_threshold_db'], i['glue_max_gr_db'],
                                                       i['limiter_max_gr_db'], i['limiter_gr_over_3db_s']))
    s.append('  stems in mix: VO %s  SFX %s  music %s LUFS | VO over music %s, over SFX %s, over bed %s LU | '
             'stems-sum residual %s dBFS' % (rep['vo_lufs_in_mix'], rep['sfx_lufs_in_mix'], rep['music_lufs_in_mix'],
                                             rep['vo_over_music_lu'], rep['vo_over_sfx_lu'], rep['vo_over_bed_lu'],
                                             rep['stems_sum_residual_dbfs']))
    if rep.get('vo_chain'):
        v = rep['vo_chain']
        s.append('  VO chain: comp thr %s dBFS, GR max %s / p99 %s dB, %s LUFS' % (
            v.get('comp_threshold_dbfs'), v.get('comp_max_gr_db'), v.get('comp_gr_p99_db'), v.get('lufs')))
    if rep.get('words'):
        w = rep['words']
        s.append('  words: %d, over bed median %s min %s, below need: %d (bed) / %d (music)' % (
            w['n'], w['over_bed']['median'], w['over_bed']['min'], len(w['below_over_bed']), len(w['below_over_music'])))
    bad = [k for k, v in rep['checks'].items() if isinstance(v, dict) and not v.get('ok')]
    s.append('  checks: %s' % ('all OK' if not bad else 'FAIL ' + ', '.join(bad)))
    for w in rep.get('warnings') or []:
        s.append('  WARN ' + w)
    s.append('  -> ' + ', '.join('%s %s' % (k, os.path.basename(v)) for k, v in rep['files'].items()))
    return '\n'.join(s)


# ============================================================================================ overview PNG
_C = dict(bg=(10, 6, 6), panel=(23, 12, 9), grid=(64, 44, 38), text=(255, 243, 230), ash=(168, 151, 140),
          flame=(255, 106, 26), red=(242, 49, 43), gold=(255, 181, 71), ivory=(255, 243, 230), plum=(74, 14, 8),
          cyan=(80, 220, 255))


def _overview(mix, vo, music, sfx, path, title='', *, speech=None, gr_db=None, hero_times=None, marks=None):
    """PNG: mix spectrogram + waveform (audio.spectro_image), then the momentary loudness (400 ms) of the mix and of
    each stem at mix gain with speech frames shaded, the VO-minus-music margin on speech frames (8 LU line) and, when
    gr_db is given, the master's gain reduction (3 dB line). Callers: _overview(yA, vo, music, sfx, path, title)."""
    from PIL import Image, ImageDraw
    mix = _stereo(mix)
    n = len(mix)
    dur = n / SR
    vo = _stereo(vo) if vo is not None else np.zeros_like(mix)
    music = _stereo(music) if music is not None else np.zeros_like(mix)
    sfx = _stereo(sfx) if sfx is not None else np.zeros_like(mix)
    W = 1600
    I, TP, LRA = A.loudness(mix), A.true_peak(mix), A.loudness_range(mix)
    spec = A.spectro_image(mix, W, 420, None, title or os.path.basename(path),
                           'mix A: I %.2f LUFS  TP %.2f dBTP  LRA %.1f LU  max momentary %.1f LUFS' % (
                               I, TP, LRA, A.momentary_max(mix)))
    tt, lmix = A.loudness_curve(mix)
    curves = [('mix', lmix, _C['ivory'], 2)]
    for lab, x, col in (('VO', vo, _C['flame']), ('music', music, _C['gold']), ('SFX', sfx, _C['red'])):
        if np.any(x):
            curves.append((lab, A.loudness_curve(x)[1], col, 1))
    sp = speech if speech is not None else (speech_mask(vo) if np.any(vo) else np.zeros(n, bool))
    idx = np.clip((tt * SR).astype(int), 0, n - 1)
    lv = A.loudness_curve(vo)[1] if np.any(vo) else np.full(len(tt), -200.0)
    spk = sp[idx] & (lv > lv.max() - SPEC['speech_top_lu'])
    H1, H2, H3 = 260, 120, (110 if gr_db is not None else 0)
    img = Image.new('RGB', (W, 420 + H1 + H2 + H3 + 24), _C['bg'])
    img.paste(spec, (0, 0))
    dr = ImageDraw.Draw(img)
    f10, f12 = A._font(11), A._font(12, True)
    X = lambda t: int(np.clip(t / dur * (W - 1), 0, W - 1))  # noqa: E731
    # ---- level strip
    y0 = 420
    dr.rectangle([0, y0, W, y0 + H1], fill=_C['panel'])
    Y = lambda v: int(np.interp(v, [-60.0, -4.0], [y0 + H1 - 4, y0 + 4]))  # noqa: E731
    for i in np.flatnonzero(np.diff(np.concatenate([[0], spk.astype(np.int8), [0]])) != 0).reshape(-1, 2):
        dr.rectangle([X(tt[i[0]] - 0.025), y0, X(tt[min(i[1], len(tt) - 1)] - 0.025), y0 + H1], fill=(44, 22, 16))
    for lvl in (-14, -18, -30, -45):
        dr.line([(0, Y(lvl)), (W, Y(lvl))], fill=_C['grid'])
        dr.text((4, Y(lvl) - 13), '%d LUFS' % lvl, fill=_C['ash'], font=f10)
    for lab, lc, col, wd in curves:
        pts = [(X(a), Y(max(b, -60.0))) for a, b in zip(tt, lc)]
        dr.line(pts, fill=col, width=wd)
    lx = W - 360
    for k, (lab, lc, col, wd) in enumerate(curves):
        dr.rectangle([lx + k * 88, y0 + 8, lx + k * 88 + 14, y0 + 18], fill=col)
        dr.text((lx + k * 88 + 18, y0 + 5), lab, fill=_C['text'], font=f12)
    dr.text((90, y0 + 5), 'momentary loudness 400 ms; speech frames shaded', fill=_C['ash'], font=f10)
    for h in hero_times or ():
        dr.line([(X(h), y0), (X(h), y0 + 8)], fill=_C['cyan'], width=2)
    for t, lab in marks or ():
        dr.line([(X(t), y0), (X(t), y0 + H1)], fill=_C['cyan'])
        dr.text((X(t) + 3, y0 + H1 - 16), str(lab), fill=_C['cyan'], font=f10)
    # ---- VO margin strip
    y1 = y0 + H1
    dr.rectangle([0, y1, W, y1 + H2], fill=(16, 9, 8))
    if np.any(music) and np.any(vo):
        lm = A.loudness_curve(music)[1]
        d = lv - np.maximum(lm, -70.0)
        Yd = lambda v: int(np.interp(v, [0.0, 24.0], [y1 + H2 - 4, y1 + 4]))  # noqa: E731
        dr.line([(0, Yd(8.0)), (W, Yd(8.0))], fill=_C['gold'])
        dr.text((4, Yd(8.0) - 13), '8 LU', fill=_C['gold'], font=f10)
        for a, b, ok in zip(tt[spk], d[spk], d[spk] >= 8.0):
            dr.ellipse([X(a) - 1, Yd(min(b, 24.0)) - 1, X(a) + 1, Yd(min(b, 24.0)) + 1],
                       fill=_C['ivory'] if ok else _C['red'])
        dr.text((60, y1 + 4), 'VO minus music on speech frames (LU; red < 8): median %.1f' % (
            float(np.median(d[spk])) if spk.any() else float('nan')), fill=_C['text'], font=f10)
    else:
        dr.text((60, y1 + 4), 'VO minus music: n/a (no %s)' % ('music' if not np.any(music) else 'VO'),
                fill=_C['ash'], font=f10)
    # ---- limiter strip
    if gr_db is not None:
        y2 = y1 + H2
        dr.rectangle([0, y2, W, y2 + H3], fill=_C['panel'])
        g = np.asarray(gr_db, dtype=np.float64)
        cols = np.minimum((np.arange(len(g)) / len(g) * W).astype(int), W - 1)
        mn = np.zeros(W)
        np.minimum.at(mn, cols, np.minimum(g, 0.0))
        Yg = lambda v: int(np.interp(v, [-8.0, 0.0], [y2 + H3 - 4, y2 + 4]))  # noqa: E731
        for lvl in (-1, -3, -6):
            dr.line([(0, Yg(lvl)), (W, Yg(lvl))], fill=_C['grid'] if lvl != -3 else _C['red'])
            dr.text((4, Yg(lvl) - 12), '%d dB' % lvl, fill=_C['ash'], font=f10)
        for i in range(W):
            if mn[i] < -0.01:
                dr.line([(i, Yg(0.0)), (i, Yg(max(mn[i], -8.0)))], fill=_C['flame'])
        dr.text((60, y2 + 4), 'bus gain reduction (glue x limiter, master gain removed): max %.2f dB' % (-g.min()),
                fill=_C['text'], font=f10)
    yb = img.height - 22
    step = 1.0 if dur <= 12 else (2.0 if dur <= 40 else 5.0)
    for k in range(int(dur / step) + 1):
        dr.line([(X(k * step), yb), (X(k * step), yb + 5)], fill=_C['ash'])
        dr.text((X(k * step) + 2, yb + 5), '%gs' % (k * step), fill=_C['ash'], font=f10)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img.save(path)
    return path


# ============================================================================================ ffmpeg: measure / mux
def ebur128(path):
    """ffmpeg ebur128 (peak=true) on a file -> dict(I, LRA, TP, LRA_low, LRA_high, threshold) (LUFS / LU / dBTP)."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-nostats', '-i', path, '-vn', '-sn', '-dn',
                        '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    s = r.stderr[r.stderr.rfind('Summary:'):]
    if r.returncode != 0 or 'Summary:' not in r.stderr:
        raise RuntimeError('epic_mix.ebur128 failed on %s: %s' % (path, r.stderr[-400:]))

    def g(k):
        m = re.search(k + r':\s+(-?[\d.]+|-inf)', s)
        return None if m is None or m.group(1) == '-inf' else float(m.group(1))
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'), LRA_low=g('LRA low'), LRA_high=g('LRA high'),
                threshold=g('Threshold'))


def _loudnorm_json(stderr):
    i, j = stderr.rfind('{'), stderr.rfind('}')
    if i < 0 or j < i:
        raise RuntimeError('loudnorm printed no JSON: %s' % stderr[-400:])
    return json.loads(stderr[i:j + 1])


def _probe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=index,codec_type,codec_name,sample_rate,'
                        'channels,bit_rate,duration:format=duration', '-of', 'json', path], capture_output=True,
                       text=True)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {}


def mux(video, wav, out, *, lufs=None, tp=None, lra=None, bitrate=None, sr=None, dur=None, verbose=False):
    """Final audio onto the master: two-pass ffmpeg loudnorm (pass 1 measures the wav; pass 2 linear=true with the
    measured values: I -14, TP -1.5 for the AAC overshoot), AAC 320k 48 kHz stereo, -movflags +faststart. The video
    stream is copied, the audio padded / cut to the video's duration (or dur); video=None (or '-') writes audio only
    (.m4a). Then the output is re-measured with ebur128. Returns dict(file, pass1, pass2, ebur128, checks, pass)."""
    S = SPEC
    I = S['aac_lufs'] if lufs is None else float(lufs)
    TP = S['aac_tp_dbtp'] if tp is None else float(tp)
    LRA = S['aac_lra'] if lra is None else float(lra)
    br = bitrate or S['aac_bitrate']
    sr = int(sr or S['aac_sr'])
    video = None if video in (None, '', '-') else video
    for p in ([video] if video else []) + [wav]:
        if not os.path.exists(p):
            raise FileNotFoundError('epic_mix.mux: %s' % p)
    base = 'loudnorm=I=%g:TP=%g:LRA=%g' % (I, TP, LRA)
    r1 = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-nostats', '-i', wav, '-af',
                         base + ':print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    if r1.returncode != 0:
        raise RuntimeError('mux pass 1 failed: %s' % r1.stderr[-400:])
    m1 = _loudnorm_json(r1.stderr)
    af = (base + ':measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true:'
          'print_format=json' % (m1['input_i'], m1['input_tp'], m1['input_lra'], m1['input_thresh'],
                                 m1['target_offset']))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cmd = ['ffmpeg', '-hide_banner', '-nostdin', '-nostats', '-y']
    if video:
        vd = dur
        if vd is None:
            pr = _probe(video)
            vs = [s for s in pr.get('streams', []) if s.get('codec_type') == 'video']
            vd = float((vs[0].get('duration') if vs and vs[0].get('duration') else None) or pr['format']['duration'])
        cmd += ['-i', video, '-i', wav, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-af', af + ',apad',
                '-t', '%.6f' % vd]
    else:
        cmd += ['-i', wav, '-map', '0:a:0', '-vn', '-af', af] + (['-t', '%.6f' % dur] if dur else [])
    cmd += ['-c:a', 'aac', '-b:a', br, '-ar', str(sr), '-ac', '2', '-movflags', '+faststart', out]
    r2 = subprocess.run(cmd, capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError('mux pass 2 failed: %s' % r2.stderr[-600:])
    m2 = _loudnorm_json(r2.stderr)
    e = ebur128(out)
    pr = _probe(out)
    a_st = [s for s in pr.get('streams', []) if s.get('codec_type') == 'audio']
    res = dict(file=out, video=video, wav=wav, target=dict(I=I, TP=TP, LRA=LRA, bitrate=br, sr=sr),
               pass1={k: m1.get(k) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')},
               pass2={k: m2.get(k) for k in ('normalization_type', 'output_i', 'output_tp', 'output_lra',
                                            'target_offset')},
               ebur128=e, audio_stream=a_st[0] if a_st else None,
               duration=float(pr.get('format', {}).get('duration', 'nan')))
    res['checks'] = dict(lufs=dict(value=e['I'], target=I, tol=S['aac_tol_lu'], ok=e['I'] is not None and
                                   abs(e['I'] - I) <= S['aac_tol_lu']),
                         tp=dict(value=e['TP'], max=TP, ok=e['TP'] is not None and e['TP'] <= TP),
                         linear=dict(value=m2.get('normalization_type'), ok=m2.get('normalization_type') == 'linear'))
    res['pass'] = all(v['ok'] for v in res['checks'].values())
    if verbose:
        print('mux %s: I %.1f LUFS  TP %.1f dBTP  LRA %.1f LU  (%s)  %s' % (
            os.path.basename(out), e['I'], e['TP'], e['LRA'], m2.get('normalization_type'),
            'OK' if res['pass'] else 'FAIL'))
    return res


# ============================================================================================ self-test (mixtest)
def _test_bed(dur, bpm=112.5, seed=7):
    """Synthetic music bed for the mixtest (D minor, i-VI-III-VII one chord per bar): a detuned band-limited saw pad
    (sfx_jawad.harm), a sub bass through the oversampled waveshaper (sfx_jawad.shape), kick on the beat and hats on
    the 8ths from bar 4, a riser into bar 12, a drop-out on bar 11 beat 3 (digital silence) and the drop on bar 12;
    pad + bass sidechained to the kick, hall on the pad; -16 LUFS, TP <= -3 dBTP. Deterministic (seeded)."""
    import sfx_jawad as J
    N = _n(dur)
    beat = 60.0 / bpm
    bar = 4 * beat
    rng = np.random.default_rng(seed)
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12.0)  # noqa: E731
    prog = [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)]
    saw = [1.0 / k for k in range(1, 11)]
    pad, bass = np.zeros((N, 2)), np.zeros(N)
    kick, hat, riser = np.zeros(N), np.zeros((N, 2)), np.zeros(N)
    tl = np.arange(N) / SR
    nb = int(math.ceil(dur / bar))
    for i in range(nb):
        i0 = _n(i * bar)
        L = min(N, _n((i + 1) * bar) + _n(0.3)) - i0
        if L <= 0:
            continue
        u = np.arange(L) / SR
        env = np.clip(u / 0.25, 0, 1) ** 2 * np.clip((bar + 0.3 - u) / 0.3, 0, 1)
        for ch, det in ((0, -0.004), (1, 0.004)):
            for mn in prog[i % 4]:
                pad[i0:i0 + L, ch] += J.harm(np.full(L, hz(mn) * (1 + det)), saw, fmax=9000.0, rng=rng) * env
        if i >= 4:
            root = prog[i % 4][0] - 12
            benv = np.clip(u / 0.01, 0, 1) * np.clip((bar - 0.02 - u) / 0.05, 0, 1)
            bass[i0:i0 + L] += J.harm(np.full(L, hz(root)), [1.0, 0.25, 0.08]) * benv
    pad = A.lp(pad, 1800.0, 2)
    bass = J.shape(bass, 1.6)
    ku = np.arange(_n(0.35)) / SR
    kx = np.sin(2 * np.pi * np.cumsum(45.0 + 70.0 * np.exp(-ku / 0.03)) / SR) * np.exp(-ku / 0.12)
    kx *= np.clip(ku / 0.001, 0, 1)
    hu = np.arange(_n(0.08)) / SR
    for b in range(int(dur / beat * 2) + 1):
        t = b * beat / 2
        if t < 4 * bar or t >= dur - 0.4:
            continue
        i = _n(t)
        if b % 2 == 0:
            m = min(len(kx), N - i)
            kick[i:i + m] += kx[:m]
        hx = A.hp(rng.standard_normal(len(hu)), 7000.0, 4) * np.exp(-hu / 0.025) * (0.6 if b % 2 else 1.0)
        m = min(len(hx), N - i)
        hat[i:i + m] += A.pan(np.stack([hx, hx], 1), 0.3 * (-1) ** b)[:m]
    d0, d1 = 11 * bar + 3 * beat, 12 * bar
    rr = (tl > 10 * bar) & (tl < d0)
    if rr.sum() > 16:                              # a bed shorter than bar 11 has no riser (and no drop-out / drop)
        riser[rr] = A.bp(rng.standard_normal(int(rr.sum())), 600.0, 7000.0, 2) * ((tl[rr] - 10 * bar) /
                                                                                  (d0 - 10 * bar)) ** 2
    pad = A.reverb(pad, 'hall', wet_db=-12.0)[:N]
    duck = A.sidechain(np.ones(N), kick, depth_db=4.0, attack=0.005, release=0.16)[:, 0]
    mus = 0.30 * pad * duck[:, None] + _stereo(0.45 * bass * duck + 0.9 * kick + 0.08 * riser) + 0.12 * hat
    gate = np.clip((d0 - tl) / 0.004, 0, 1) + np.clip((tl - d1) / 0.004, 0, 1)
    mus = A.hp(mus * np.clip(gate, 0, 1)[:, None], 25.0, 2) * np.clip(gate, 0, 1)[:, None]
    mus *= undb(-16.0 - A.loudness(mus))
    mus *= A.limiter_gain(mus, -3.3)[:, None]
    return mus, dict(bpm=bpm, drop_out=(round(d0, 4), round(d1, 4)), drop=round(d1, 4), bars=nb)


def _test_cues():
    """A short procedural cue list of audio.py sounds for the pehle_wala VO A: hero hits in its measured VO gaps (2.27-3.27,
    21.68-23.50, 24.93-28.13, 31.99-32.60 s), their tails truncated ('dur') before the next word, UI / foley under or
    between words at -6..-10 dB, busy high-mid cues low-passed (sound_design.md section 4). The selftest then runs
    sfx_jawad.fit_under_vo on it, as the reels do."""
    return [dict(t=0.02, name='impact_soft', gain_db=-4.0),
            dict(t=2.45, name='riser', gain_db=-8.0, params=dict(duration=1.2), lp=4000),
            dict(t=2.45, name='impact_big', gain_db=0.0, dur=0.8), dict(t=2.45, name='sub_drop', gain_db=-4.0, dur=0.8),
            dict(t=6.3, name='ui_click', gain_db=-8.0, pan=-0.3), dict(t=6.5, name='ui_click', gain_db=-8.0, pan=0.3),
            dict(t=8.0, name='whoosh_fast', gain_db=-6.0), dict(t=10.2, name='camera_shutter', gain_db=-6.0),
            dict(t=12.2, name='glitch_short', gain_db=-4.0),
            dict(t=13.5, name='typing', gain_db=-10.0, lp=3500, align='start', params=dict(n=8)),
            dict(t=16.8, name='whip', gain_db=-3.0), dict(t=17.0, name='impact_soft', gain_db=-2.0),
            dict(t=17.2, name='shimmer', gain_db=-8.0),
            dict(t=22.6, name='reverse_swell', gain_db=-6.0, params=dict(duration=0.9)),
            dict(t=22.6, name='flash_hit', gain_db=-3.0, dur=0.95),
            dict(t=25.6, name='impact_big', gain_db=0.0, dur=2.4), dict(t=25.6, name='sub_drop', gain_db=-4.0),
            dict(t=26.6, name='downlifter', gain_db=-10.0, dur=1.4), dict(t=32.2, name='logo_sting', gain_db=-2.0,
                                                                          dur=0.74)]


def selftest(out_dir=None, slug='pehle_wala'):
    """The mixtest (sound_design.md section 6) on a real VO stem + audio.py cues + a synthetic bed, plus contract
    checks (mono / stereo inputs, caller call patterns, loop mode, protect windows, tail_fade, determinism, mux).
    Writes everything to out_dir and <out_dir>/selftest.json; returns (ok, report)."""
    t0 = time.time()
    out_dir = os.path.abspath(out_dir or os.path.join(REPO, 'workspace', 'brand_reels', 'wf', 'kitcheck', 'mixtest'))
    os.makedirs(out_dir, exist_ok=True)
    rw = os.path.join(REPO, 'workspace', 'jawad_reels', slug, 'vo')
    vo_path = os.path.join(rw, '%s_vo_A.wav' % slug)
    words = os.path.join(rw, '%s_vo_A.words.json' % slug)
    if not os.path.exists(vo_path):
        vo_path, words = os.path.join(rw, 'vo_stem.wav'), os.path.join(rw, 'words.json')
    vx, vsr = A.read_wav(vo_path)
    dur = len(vx) / vsr
    res, P = {}, {}
    # ---- inputs
    bed, binfo = _test_bed(dur)
    bed_path = write_wav(os.path.join(out_dir, 'mixtest_bed.wav'), bed)
    res['bed'] = dict(binfo, lufs=_r(A.loudness(bed)), tp_dbtp=_r(A.true_peak(bed)), file=bed_path)
    res['vo_input'] = dict(path=vo_path, shape=list(vx.shape), lufs=_r(A.loudness(vx)), dur=round(dur, 4))
    import sfx_jawad as SJ
    cues, frep = SJ.fit_under_vo(_test_cues(), words, hero='warn', report=True)
    res['fit_under_vo'] = dict(violations=frep['violations'], ducked=frep['ducked'], spans=frep['spans'],
                               hero_source=frep['hero_source'])
    # ---- 1. the mixtest proper: mono VO path (R7), cue list -> audio.mix, bed room_tone -30, music array
    rep = mix_reel('mixtest', dur, vo=vo_path, music=bed, sfx_cues=cues, bed='room_tone', bed_gain_db=-30.0,
                   out_dir=out_dir, vo_offset=0.0, words=words)
    res['mixtest'] = {k: rep[k] for k in ('A_full', 'B_vo_sfx', 'vo_lufs_in_mix', 'sfx_lufs_in_mix', 'music_lufs_in_mix',
                                          'vo_over_music_lu', 'vo_over_sfx_lu', 'vo_over_bed_lu', 'vo_chain', 'music',
                                          'words', 'hero_times', 'stems_sum_residual_dbfs', 'checks', 'warnings',
                                          'files', 'seconds')}
    res['mixtest']['ebur128'] = {k: ebur128(rep['files'][k]) for k in ('mix', 'vo_sfx')}
    a, b = rep['A_full'], rep['B_vo_sfx']
    P['A -14 +-0.1 LUFS'] = abs(a['lufs'] + 14) <= 0.1
    P['A <= -2.0 dBTP'] = a['tp_dbtp'] <= -2.0
    P['B -14 +-0.1 LUFS'] = abs(b['lufs'] + 14) <= 0.1
    P['B <= -2.0 dBTP'] = b['tp_dbtp'] <= -2.0
    P['VO >= 8 LU over the ducked bed (music)'] = rep['vo_over_music_lu'] >= 8.0
    P['VO >= 10 LU over SFX'] = rep['vo_over_sfx_lu'] >= 10.0
    P['ffmpeg A within 0.15 LU of numpy'] = abs(res['mixtest']['ebur128']['mix']['I'] - a['lufs']) <= 0.15
    P['ffmpeg A TP <= -2.0'] = res['mixtest']['ebur128']['mix']['TP'] <= -2.0
    P['stems sum to A (<= -90 dBFS)'] = rep['stems_sum_residual_dbfs'] <= -90.0
    P['report JSON-safe'] = bool(json.dumps(rep))
    P['files exist'] = all(os.path.exists(rep['files'][k]) for k in STEM_KEYS + ('png', 'report', 'sfx_stem'))
    # ---- 2. mux: AAC after two-pass loudnorm (video and audio-only)
    vid = os.path.join(out_dir, 'mixtest_black.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=0x070404:s=270x480:r=30:d=%.6f' % dur,
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', vid], check=True)
    mxA = mux(vid, rep['files']['mix'], os.path.join(out_dir, 'mixtest_mix.mp4'), verbose=True)
    mxB = mux(None, rep['files']['vo_sfx'], os.path.join(out_dir, 'mixtest_vo_sfx.m4a'), verbose=True)
    res['mux'] = dict(A=mxA, B=mxB)
    P['AAC A -14 +-0.5 LUFS, <= -1.5 dBTP, linear'] = mxA['pass']
    P['AAC B -14 +-0.5 LUFS, <= -1.5 dBTP, linear'] = mxB['pass']
    P['AAC A duration = video'] = abs(mxA['duration'] - dur) < 0.05
    # ---- 3. callers' patterns: stereo copy of the mono VO (bit-identical result), sfx= stem path, music=None, dur=
    vo2 = write_wav(os.path.join(out_dir, '_tmp_vo_stereo.wav'), np.repeat(vx, 2, axis=1))
    r1 = mix_reel('mixtest_mono', dur=dur, vo=vo_path, sfx=rep['files']['sfx_stem'], music=bed_path, out_dir=out_dir,
                  vo_offset=0.0, png=False, verbose=False)
    r2 = mix_reel('mixtest_st', dur=dur, vo=vo2, sfx=rep['files']['sfx_stem'], music=bed_path, out_dir=out_dir,
                  vo_offset=0.0, png=False, verbose=False)
    yA1, yA2 = load(r1['files']['mix']), load(r2['files']['mix'])
    P['mono VO == dual-mono stereo VO (bit-identical A)'] = bool(np.array_equal(yA1, yA2))
    P['sfx= stem file path: A -14 +-0.1, <= -2.0 dBTP'] = abs(r1['A_full']['lufs'] + 14) <= 0.1 and \
        r1['A_full']['tp_dbtp'] <= -2.0
    r3 = mix_reel('mixtest_nomusic', dur=dur, vo=vo_path, sfx=rep['files']['sfx_stem'], music=None, out_dir=out_dir,
                  vo_offset=0.0, png=False, verbose=False)
    m3 = load(r3['files']['stem_music'])
    P['music=None: stem_music written, silent; music_lufs None'] = (not np.any(m3)) and r3['music_lufs_in_mix'] is None
    P['music=None: A == B'] = abs(r3['A_full']['lufs'] - r3['B_vo_sfx']['lufs']) < 0.03
    os.remove(vo2)
    res['callers'] = dict(stereo_copy=dict(A=r2['A_full']['lufs'], sha_A=_sha(r2['files']['mix'])),
                          sha_A_mono=_sha(rep['files']['mix']), no_music=dict(A=r3['A_full'], B=r3['B_vo_sfx']))
    L = load(vo_path, dur)
    P['load(mono, dur) -> (N, 2), L == R'] = L.shape == (_n(dur), 2) and np.array_equal(L[:, 0], L[:, 1])
    P['load pads / cuts'] = load(vo_path, dur + 1.0).shape[0] == _n(dur + 1.0) and load(vo_path, 1.0).shape[0] == SR
    P['load (N, 1) array'] = load(np.zeros((100, 1))).shape == (100, 2)
    # ---- 4. determinism: the same call again -> identical bytes
    r4 = mix_reel('mixtest_again', dur, vo=vo_path, music=bed, sfx_cues=cues, bed='room_tone', bed_gain_db=-30.0,
                  out_dir=out_dir, vo_offset=0.0, png=False, verbose=False)
    P['deterministic (A, B, stems: same sha256)'] = all(_sha(r4['files'][k]) == _sha(rep['files'][k]) for k in STEM_KEYS)
    for k in STEM_KEYS + ('sfx_stem', 'sfx_stem_fx', 'sfx_stem_bed', 'report'):
        if k in r4['files'] and os.path.exists(r4['files'][k]):
            os.remove(r4['files'][k])
    # ---- 5. loop mode: continuity across the seam
    r5 = mix_reel('mixtest_loop', dur, vo=vo_path, music=bed, sfx=rep['files']['sfx_stem'], out_dir=out_dir,
                  loop=True, png=False, verbose=False)
    res['loop'] = dict(A=r5['A_full'], B=r5['B_vo_sfx'])
    P['loop: A continuity at the seam <= -100 dBFS'] = r5['A_full']['loop_continuity_error_dbfs'] <= -100.0
    P['loop: B continuity at the seam <= -100 dBFS'] = r5['B_vo_sfx']['loop_continuity_error_dbfs'] <= -100.0
    P['loop: A -14 +-0.1, <= -2.0 dBTP (seam incl.)'] = abs(r5['A_full']['lufs'] + 14) <= 0.1 and \
        r5['A_full']['tp_dbtp'] <= -2.0
    # ---- 6. loop with sfx_cues (fold) + bed (seamless); protect window caps the glue
    r6 = mix_reel('mixtest_loopcues', dur, vo=vo_path, music=bed, sfx_cues=cues, bed='room_tone', out_dir=out_dir,
                  loop=True, protect=[(25.55, 25.95)], protect_cap_db=0.0, png=False, verbose=False)
    res['loop_cues'] = dict(A=r6['A_full'], sfx=dict((k, r6['sfx'][k]) for k in ('stem_lufs', 'stem_tp_dbtp', 'loop')))
    sst = load(r6['files']['sfx_stem'])
    P['loop cues: SFX stem seam continuous (step < 5x local median)'] = (
        np.abs(sst[0] - sst[-1]).max() < 5 * max(np.median(np.abs(np.diff(np.concatenate([sst[-2400:], sst[:2400]]),
                                                                          axis=0)).max(1)), 1e-6))
    P['loop cues: A -14 +-0.1, <= -2.0 dBTP'] = abs(r6['A_full']['lufs'] + 14) <= 0.1 and r6['A_full']['tp_dbtp'] <= -2.0
    bus = load(rep['files']['mix'])
    g0, i0 = glue_gain(bus)
    gp, ip = glue_gain(bus, protect=[(25.55, 25.95)], protect_cap_db=0.0)
    w = slice(_n(25.55), _n(25.95))
    P['protect: no glue inside the window'] = float(db(gp[w]).min()) > -1e-6 and float(db(g0[w]).min()) < -0.05
    res['protect'] = dict(glue_gr_in_window_unprotected_db=_r(-db(g0[w]).min()), protected_db=_r(-db(gp[w]).min()))
    # ---- 7. tail_fade pass-through (R3): a riser ending on dur keeps its level with tail_fade=0
    tc = [dict(t=4.0, name='riser', params=dict(duration=2.0))]
    r7a = mix_reel('mixtest_tf04', 4.0, sfx_cues=tc, out_dir=out_dir, tail_fade=0.4, png=False, verbose=False)
    r7b = mix_reel('mixtest_tf00', 4.0, sfx_cues=tc, out_dir=out_dir, tail_fade=0.0, png=False, verbose=False)
    e_a = float(db(np.sqrt(np.mean(load(r7a['files']['sfx_stem'])[-_n(0.1):] ** 2)) + 1e-12))
    e_b = float(db(np.sqrt(np.mean(load(r7b['files']['sfx_stem'])[-_n(0.1):] ** 2)) + 1e-12))
    P['tail_fade=0 keeps the last 100 ms (>= 6 dB over tail_fade=0.4)'] = e_b - e_a >= 6.0
    res['tail_fade'] = dict(last100ms_rms_dbfs_tf04=_r(e_a), tf00=_r(e_b))
    for r in (r7a, r7b, r1, r2, r3, r6):
        for k, f in r['files'].items():
            if os.path.exists(f) and os.path.basename(f).startswith(('mixtest_tf', 'mixtest_st', 'mixtest_nomusic',
                                                                       'mixtest_loopcues', 'mixtest_mono')):
                os.remove(f)
    # ---- 8b. opt-in per-word level ride (LEAD_DECISIONS 1: VO >= 8 LU over the bed on every word)
    r9 = mix_reel('mixtest_ride', dur, vo=vo_path, music=bed_path, sfx=rep['files']['sfx_stem'], out_dir=out_dir,
                  words=words, word_floor_lu=8.0, png=True, verbose=True)
    ride = r9['music']['word_topup']
    res['word_ride'] = dict(words=r9['words'], topup=ride, A=r9['A_full'], B=r9['B_vo_sfx'],
                            vo_over_music_lu=r9['vo_over_music_lu'])
    P['word ride: every word >= 8 LU over the bed (7 one-syllable) unless the SFX alone masks it'] = all(
        w['sfx_alone_over'] < w['need'] + 0.5 for w in ride['still_short']) and len(
        r9['words']['below_over_bed']) <= len(ride['still_short'])
    P['word ride: A / B still -14 +-0.1, <= -2.0 dBTP'] = all(abs(i['lufs'] + 14) <= 0.1 and i['tp_dbtp'] <= -2.0
                                                            for i in (r9['A_full'], r9['B_vo_sfx']))
    # ---- 8. speech_mask hold semantics
    tv = np.zeros(SR)
    tv[_n(0.2):_n(0.3)] = np.sin(2 * np.pi * 200 * np.arange(_n(0.1)) / SR)
    mk = speech_mask(tv, hold=0.25)
    on = np.flatnonzero(mk)
    P['speech_mask: onset ~0.2 s, held ~0.25 s past 0.3 s'] = bool(on.size) and abs(on[0] / SR - 0.2) < 0.01 and \
        abs(on[-1] / SR - 0.55) < 0.02
    res['checks'] = P
    res['ok'] = all(P.values())
    res['seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(out_dir, 'selftest.json'), 'w') as fh:
        json.dump(_jsonable(res), fh, indent=1)
    for k, v in P.items():
        print('%-4s %s' % ('OK' if v else 'FAIL', k))
    print('selftest %s in %.1f s -> %s' % ('PASSED' if res['ok'] else 'FAILED', res['seconds'],
                                           os.path.join(out_dir, 'selftest.json')))
    return res['ok'], res


# ============================================================================================ CLI
def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s1 = sub.add_parser('selftest')
    s1.add_argument('--out')
    s1.add_argument('--slug', default='pehle_wala')
    s2 = sub.add_parser('mix')
    s2.add_argument('name')
    s2.add_argument('dur', type=float)
    for k in ('--vo', '--sfx', '--music', '--out-dir', '--words'):
        s2.add_argument(k)
    s2.add_argument('--vo-offset', type=float, default=0.0)
    s2.add_argument('--loop', action='store_true')
    s3 = sub.add_parser('mux')
    s3.add_argument('video')
    s3.add_argument('wav')
    s3.add_argument('out')
    s4 = sub.add_parser('ebur128')
    s4.add_argument('file')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        ok, _ = selftest(a.out, a.slug)
        return 0 if ok else 1
    if a.cmd == 'mix':
        rep = mix_reel(a.name, a.dur, vo=a.vo, music=a.music, sfx=a.sfx, out_dir=a.out_dir, vo_offset=a.vo_offset,
                       loop=a.loop, words=a.words)
        return 0 if rep['checks']['ok'] else 1
    if a.cmd == 'mux':
        r = mux(a.video, a.wav, a.out, verbose=True)
        print(json.dumps(r, indent=1))
        return 0 if r['pass'] else 1
    print(json.dumps(ebur128(a.file)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
