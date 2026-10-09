#!/usr/bin/env python3
"""log_kya_kahenge_mix.py: deterministic FINAL MIX for Reel 5 · C15 "Log Kya Kahenge" (music-supervisor + sound-designer).

Nobody on the team can listen. Everything this module claims is measured (BS.1770 in numpy + ffmpeg ebur128, sample
steps, onset finders, spectrogram PNGs that a person or agent opens).

INPUTS (48 kHz, exactly 1,689,600 samples = 35.2 s, loop-exact; nothing else is read)
    VO     <RW>/vo/lkk_vo_A.wav | lkk_vo_B.wav          mono 24-bit, -16 LUFS (hook A | hook B, identical from 8.8 s)
           <RW>/vo/lkk_vo_A.words.json | _B.words.json  line spans for the per-line VO-over-bed check
    SFX    <RW>/audio/log_kya_kahenge_sfx_stem.wav | log_kya_kahenge_hookb_sfx_stem.wav   stereo, -18 LUFS
           <RW>/audio/log_kya_kahenge_cues.json | log_kya_kahenge_hookb_cues.json         hero cues (onset check)
    MUSIC  <RW>/music/music_full.wav                    stereo, -16 LUFS (log_kya_kahenge_music.py build; EP dips on
                                                        the measured VO windows)

OUTPUTS (<RW>/audio/final/, all 48 kHz 24-bit STEREO, exactly 1,689,600 samples, seamless at the loop seam)
    <name>_mix.wav          VERSION A: VO + SFX + music, -14.0 LUFS, true peak <= -2.0 dBTP
    <name>_vo_sfx.wav       VERSION B: VO + SFX only (same internal balance; for a song added in-app), same specs
    <name>_stem_vo.wav  _stem_sfx.wav  _stem_music.wav   at version A's exact gains: vo + sfx + music == A
    <name>_mix.json         every number below; <name>_mix.png / <name>_zooms.png spectrograms (viewed)
    name = log_kya_kahenge (hook A, public) | log_kya_kahenge_hookb (hook B, Trial)
    Convenience links at the HANDOFF paths <RW>/audio/<name>_mix.wav / <name>_vo_sfx.wav -> final/ (render.py --audio).

CHAIN (the series spec of epic_mix / brand_reels/research/sound_design.md §6, made loop-safe; local workarounds for
SHARED_REQUESTS R6a/b/c, shared modules imported read-only)
    0. load every input as stereo (a mono VO is copied to L = R: R6a) and pad it CIRCULARLY by PAD s on both sides, so
       every envelope (compressor, sidechains, glue, limiter) enters sample 0 in the state it has at the end of the
       reel: the output loops without a click (R6c). Everything is measured and normalised on the 35.2 s crop.
    1. VO: epic_mix.vo_chain (HPF 80, -2 dB @ 300, +2 dB @ 3.2k, +1.5 dB shelf @ 10k, 3:1), -16.0 LUFS.
    2. SFX stem: -18.0 LUFS, sidechain under the VO -4 dB (30 / 300 ms).
    3. Music: -18.0 LUFS (never renormalised after ducking), -3 dB under the SFX (10 / 250 ms), -9 dB under the VO
       (40 / 400 ms), -10 dB under the SFX reveal 15.99-16.33 (HERO_MUSIC_DUCK: the score's first pulse + D1 sub never
       stack on the braam's D1), then a per-LINE top-up duck so that every VO line sits >= LINE_TARGET LU over the bed
       (music + SFX, median of voiced 400 ms frames, the rough-mix method), measured AFTER the bus, iterated, capped.
    4. Bus glue 2:1 (threshold 3 dB under the crop's 98th-percentile 10 ms level, 6 / 150 ms), limited to
       PROTECT_GR_CAP = 1.5 dB inside the reveal window PROTECT (R6b: the VO-set threshold no longer flattens the hero
       hit; the 1.5 dB keeps the limiter <= ~3 dB there).
    5. Master gain + 4x-oversampled true-peak lookahead limiter at -2.3 dBFS, iterated to -14.00 +- 0.015 LUFS.
       Version B: the same VO + SFX (same internal balance), its own glue threshold, gain and limiter.
    6. Crop to 35.2 s. Stems = each processed input x the bus's own gain curves (glue x gain x limiter), so they sum
       to version A to within 24-bit rounding (epic_mix's stems leave the glue out).

CLI (run from pipeline/jawad_reels; heavy work through the semaphore)
    tools/heavy.sh python3 log_kya_kahenge_mix.py build  [--hook A|B|AB]  -> final/ wavs + <name>_mix.json
    tools/heavy.sh python3 log_kya_kahenge_mix.py verify [--hook A|B|AB]  -> ffmpeg ebur128, AAC 320k test encode,
                                                                            onsets, seam, grid, PNGs (into the json)
    tools/heavy.sh python3 log_kya_kahenge_mix.py all    [--hook A|B|AB]  -> build + verify
    tools/heavy.sh python3 log_kya_kahenge_mix.py determinism [--hook AB]  -> rebuilds into a scratch folder and
                                                                            compares every sha256 (then deletes it)
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE ends up first: `audio` is this project's toolkit copy
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import numpy as np  # noqa: E402
from scipy.ndimage import uniform_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_mix as M  # noqa: E402  (read-only: vo_chain, speech_mask, _level_pct, SPEC)
from audio import SR, undb, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'log_kya_kahenge'
DUR, BPM, FPS = 35.2, 75.0, 30
N = _n(DUR)
assert N == 1689600
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
VO_DIR, AUD = os.path.join(RW, 'vo'), os.path.join(RW, 'audio')
FINAL = os.path.join(AUD, 'final')
MUSIC = os.path.join(RW, 'music', 'music_full.wav')
HOOKS = {
    'A': dict(name=MODULE, vo='lkk_vo_A.wav', words='lkk_vo_A.words.json', sfx=MODULE + '_sfx_stem.wav',
              cues=MODULE + '_cues.json'),
    'B': dict(name=MODULE + '_hookb', vo='lkk_vo_B.wav', words='lkk_vo_B.words.json',
              sfx=MODULE + '_hookb_sfx_stem.wav', cues=MODULE + '_hookb_cues.json'),
}

PAD = 4.0                                       # circular pad (s) on each side: >> every release (0.4 s max)
VO_LUFS, SFX_LUFS, MUSIC_LUFS, FINAL_LUFS = -16.0, -18.0, -18.0, -14.0
SFX_DUCK_VO = (4.0, 0.03, 0.30)                 # dB, attack, release
MUSIC_DUCK_SFX = (3.0, 0.01, 0.25)
MUSIC_DUCK_VO = (9.0, 0.04, 0.40)
LINE_TARGET = 8.5                               # LU: every VO line >= 8.5 over music + SFX (spec 8.0, 0.5 margin)
LINE_EXTRA_MAX = 9.0                            # dB cap on the per-line top-up duck
LINE_PRE, LINE_POST = 0.10, 0.15                # top-up duck fully down 100 ms before the line, held 150 ms after it
LINE_ATTACK, LINE_RELEASE = 0.08, 0.35          # raised-cosine ramps into / out of the top-up duck
GLUE_RATIO, GLUE_BELOW_P98 = 2.0, 3.0
PROTECT = ((15.97, 16.40),)                     # reveal (impact_big 16.000 + braam 16.010; V3 at 16.357): no glue
PROTECT_RAMP = 0.03
PROTECT_GR_CAP = 1.5                            # dB of glue still allowed inside PROTECT: keeps the limiter <= ~3 dB
                                                # on the reveal (series check: GR > 3 dB only on hero hits, < 0.1 s)
LIMIT_CEIL, TP_SPEC, AAC_TP_SPEC = -2.3, -2.0, -1.5
REVEAL_T, CLUNK_T, DROP_OUT = 16.0, 25.6, (15.2, 16.0)
HERO_MUSIC_DUCK = (10.0, (15.99, 16.33), 0.005, 0.12)  # dB, window, attack, release: the score's first pulse and
                                                # sub (D1, the braam's root) under the SFX reveal; V3's ducks take over
GAP_TRIM = (0.0, 0.30)                          # dB, ramp: music in the no-VO stretches >= GAP_MIN s. OFF: measured,
                                                # LRA(A) 5.0+ needs 12 dB here (gutting the build's climax and the gag)
GAP_MIN, GAP_EDGE = 1.5, 0.25                   # gap = no voiced VO for >= 1.5 s; trimmed from 0.25 s after the
                                                # voice ends to 0.25 s before it returns


# ============================================================================================ helpers
def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def load_exact(path):
    """48 kHz wav -> float64 (N, 2). A mono file becomes L = R (R6a). The length must be exactly N (loop-exact
    stems); anything else is an error, never a silent pad."""
    x, sr = A.read_wav(path)
    if sr != SR:
        raise SystemExit('%s: %d Hz, expected %d' % (path, sr, SR))
    if len(x) != N:
        raise SystemExit('%s: %d samples, expected %d (35.2 s, loop-exact)' % (path, len(x), N))
    x = np.asarray(x, dtype=np.float64)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    return x[:, :2]


def cpad(x, p):
    """Circular pad: the reel's last p samples before it, its first p samples after it."""
    return np.concatenate([x[-p:], x, x[:p]])


def crop(x, p):
    return x[p:p + N]


def window_curve(n, t0, wins, ramp_in, ramp_out=None, depth=1.0):
    """0..depth curve over a padded timeline that starts at reel time t0: depth inside each window (a, b), raised-cosine
    ramps of ramp_in before a and ramp_out after b; overlapping windows combine by max."""
    ramp_out = ramp_in if ramp_out is None else ramp_out
    t = t0 + np.arange(n) / SR
    w = np.zeros(n)
    for a, b in wins:
        for k in (-1, 0, 1):                       # the circular copies of each window (pads wrap the reel)
            aa, bb = a + k * DUR, b + k * DUR
            up = np.clip((t - (aa - ramp_in)) / ramp_in, 0, 1)
            dn = np.clip(((bb + ramp_out) - t) / ramp_out, 0, 1)
            c = np.minimum(up, dn)
            w = np.maximum(w, 0.5 - 0.5 * np.cos(np.pi * c))
    return w * depth


def no_vo_gaps(v):
    """No-VO stretches of the (cropped) VO >= GAP_MIN s, shrunk by GAP_EDGE on both sides (circular: the gap across the
    loop seam counts once). Voiced = epic_mix.speech_mask without its hold."""
    sp = M.speech_mask(v, hold=0.02)
    on = np.flatnonzero(np.diff(np.concatenate([[0], sp.astype(np.int8), [0]])))
    runs = [(a / SR, b / SR) for a, b in zip(on[::2], on[1::2])]
    gaps = []
    for (a0, b0), (a1, b1) in zip(runs, runs[1:] + [(runs[0][0] + DUR, runs[0][1] + DUR)]):
        if a1 - b0 >= GAP_MIN:
            gaps.append((round(b0 + GAP_EDGE, 3), round(a1 - GAP_EDGE, 3)))
    return gaps


def lines_of(words_path):
    lines = {}
    for w in json.load(open(words_path)):
        if isinstance(w, dict) and w.get('line'):
            a = lines.setdefault(w['line'], [w['start'], w['end']])
            a[0], a[1] = min(a[0], w['start']), max(a[1], w['end'])
    return dict(sorted(lines.items(), key=lambda kv: kv[1][0]))


def margins(v, m, s, lines):
    """VO over the bed, the rough-mix method (log_kya_kahenge_sfx.rough): momentary 400 ms / 50 ms hop; voiced frames
    = epic_mix.speech_mask(VO) & VO within 15 LU of its loudest frame; medians of the per-frame differences."""
    tt, lv = A.loudness_curve(v)
    _, lm = A.loudness_curve(m) if np.any(m) else (None, np.full_like(lv, -200.0))
    _, ls = A.loudness_curve(s)
    _, lb = A.loudness_curve(s + m)
    sp = M.speech_mask(v)
    idx = np.clip((tt * SR).astype(int), 0, len(v) - 1)
    spk = sp[idx] & (lv > lv.max() - 15)
    med = lambda d, sel: round(float(np.median(d[sel])), 2) if sel.any() else None
    out = dict(overall=dict(vo_over_bed=med(lv - lb, spk), vo_over_music=med(lv - lm, spk), vo_over_sfx=med(lv - ls, spk),
                            vo_over_bed_p10=round(float(np.percentile((lv - lb)[spk], 10)), 2)), lines={})
    for ln, (a0, b0) in lines.items():
        sel = spk & (tt >= a0) & (tt <= b0)
        out['lines'][ln] = dict(t=[round(a0, 3), round(b0, 3)], vo_over_bed=med(lv - lb, sel),
                                vo_over_music=med(lv - lm, sel), vo_over_sfx=med(lv - ls, sel))
    return out


def glue_gain(bus_p, p, protect=None):
    """epic_mix.glue (2:1, soft knee 6 dB, 6 / 150 ms, RMS 8 ms; threshold = crop's 98th-pct 10 ms level - 3 dB)
    as a dB curve, released to 0 dB inside the protect windows (R6b). Returns (linear gain, threshold, max GR)."""
    protect = PROTECT if protect is None else protect
    thr = M._level_pct(crop(bus_p, p), 98) - GLUE_BELOW_P98
    gr = A.compressor_gain(bus_p, thresh_db=thr, ratio=GLUE_RATIO, knee_db=6.0, attack=0.006, release=0.15, rms=0.008)
    if protect:                                    # inside the window the glue may take at most PROTECT_GR_CAP dB
        w = window_curve(len(bus_p), -PAD, protect, PROTECT_RAMP)
        gr = gr * (1.0 - w) + np.maximum(gr, -PROTECT_GR_CAP) * w
    return undb(gr), thr, float(-crop(gr[:, None], p).min())


def master(bus_p, p, target=FINAL_LUFS, ceiling=LIMIT_CEIL):
    """Gain + true-peak limiter on the padded bus, iterated until the CROP is at target (+-0.015 LU)."""
    pk = A.tp_envelope(bus_p)
    g = target - A.loudness(crop(bus_p, p))
    for _ in range(24):
        gl = A.limiter_gain(bus_p * undb(g), ceiling, pk=pk * undb(g))
        L = A.loudness(crop(bus_p, p) * undb(g) * crop(gl[:, None], p))
        if abs(L - target) < 0.015:
            break
        g += (target - L) * 1.1                    # limiter GR grows with g: a slight over-step converges faster
    return g, gl


def seam(y, z=None, p=None):
    """Loop-seam numbers for a cropped output y (and, when given, the padded processed signal z it was cropped from):
    step = |y[0] - y[-1]| (max over channels) against the local median / p99 step of the looped 100 ms around the
    seam; last vs first 50 ms RMS; continuity error = how far the processed audio that follows the reel's end differs
    from the cropped start (0 = the crop is exactly the steady-state loop)."""
    w = _n(0.05)
    lp = np.concatenate([y[-w:], y[:w]])
    d = np.abs(np.diff(lp, axis=0)).max(1)
    step = float(np.abs(y[0] - y[-1]).max())
    rms = lambda x: float(A.db(np.sqrt(np.mean(np.square(x))) + 1e-15))
    hf = uniform_filter1d(np.square(A.hp(np.concatenate([y[-_n(1.0):], y[:_n(1.0)]]), 6000.0, 4)).mean(1), _n(0.005))
    c = _n(1.0)
    hf_db = float(10 * np.log10(max(hf[c - _n(0.01):c + _n(0.01)].max(), 1e-30) / max(np.median(hf), 1e-30)))
    o = dict(step=round(step, 6), local_median_step=round(float(np.median(d)), 6),
             local_p99_step=round(float(np.percentile(d, 99)), 6),
             step_over_median=round(step / max(float(np.median(d)), 1e-12), 2),
             last50_rms_dbfs=round(rms(y[-w:]), 2), first50_rms_dbfs=round(rms(y[:w]), 2),
             first_minus_last_50ms_db=round(rms(y[:w]) - rms(y[-w:]), 2), hf6k_at_seam_vs_median_db=round(hf_db, 2))
    if z is not None:
        k = _n(1.0)
        o['continuity_error_dbfs'] = round(float(A.db(np.abs(z[p + N:p + N + k] - z[p:p + k]).max() + 1e-15)), 1)
    return o


def onset_near(x, t, win=0.06, hop=240):
    """qa_measure.py `cues` on an array (mono fold-down, 5 ms RMS, the largest dB rise within +-win)."""
    m = np.asarray(x, dtype=np.float64).mean(1)
    e = np.sqrt(np.convolve(m * m, np.ones(hop) / hop, 'same')[::hop] + 1e-12)
    d = 20 * np.log10(e)
    on = np.maximum(np.diff(d, prepend=d[0]), 0)
    rate = SR / hop
    i0, i1 = max(0, int((t - win) * rate)), min(len(on) - 1, int((t + win) * rate))
    k = i0 + int(np.argmax(on[i0:i1]))
    return k / rate - t, float(on[k])


def ebur128(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'), LRA_low=g('LRA low'), LRA_high=g('LRA high'))


def ffprobe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,'
                        'bits_per_sample,duration_ts', '-of', 'json', path], capture_output=True, text=True)
    return json.loads(r.stdout)['streams'][0]


# ============================================================================================ the mix
def mix(hook='A', out=FINAL, write=True, verbose=True):
    h = HOOKS[hook]
    name = h['name']
    paths = dict(vo=os.path.join(VO_DIR, h['vo']), words=os.path.join(VO_DIR, h['words']),
                 sfx=os.path.join(AUD, h['sfx']), music=MUSIC)
    miss = [q for q in paths.values() if not os.path.exists(q)]
    if miss:
        raise SystemExit('mix: missing input(s): %s' % ', '.join(miss))
    p = _n(PAD)
    lines = lines_of(paths['words'])
    vo_in, sfx_in, mus_in = load_exact(paths['vo']), load_exact(paths['sfx']), load_exact(paths['music'])

    # 1. VO (series VO polish on the circular copy), -16 LUFS on the crop
    v = M.vo_chain(cpad(vo_in, p))
    v *= undb(VO_LUFS - A.loudness(crop(v, p)))
    # 2. SFX -18, -4 dB under the VO
    s = cpad(sfx_in, p)
    s *= undb(SFX_LUFS - A.loudness(crop(s, p)))
    s = A.sidechain(s, v, depth_db=SFX_DUCK_VO[0], attack=SFX_DUCK_VO[1], release=SFX_DUCK_VO[2])
    # 3. music -18, -3 under SFX, -9 under VO (+ the optional hero / gap stages), then the per-line top-up
    m0 = cpad(mus_in, p)
    m0 *= undb(MUSIC_LUFS - A.loudness(crop(m0, p)))
    m0 = A.sidechain(m0, s, depth_db=MUSIC_DUCK_SFX[0], attack=MUSIC_DUCK_SFX[1], release=MUSIC_DUCK_SFX[2])
    m0 = A.sidechain(m0, v, depth_db=MUSIC_DUCK_VO[0], attack=MUSIC_DUCK_VO[1], release=MUSIC_DUCK_VO[2])
    if HERO_MUSIC_DUCK[0] > 0:                     # the score's first pulse never stacks on the SFX reveal
        db_, win_, ra_, rr_ = HERO_MUSIC_DUCK
        m0 = m0 * undb(-window_curve(len(m0), -PAD, [win_], ra_, rr_, db_))[:, None]
    gaps = no_vo_gaps(crop(v, p)) if GAP_TRIM[0] > 0 else []
    if gaps:
        m0 = m0 * undb(-window_curve(len(m0), -PAD, gaps, GAP_TRIM[1], GAP_TRIM[1], GAP_TRIM[0]))[:, None]
    extra = {ln: 0.0 for ln in lines}
    hist = []
    for it in range(10):                           # margins measured AFTER the bus (glue / limiter act within frames)
        dcurve = np.zeros(len(m0))
        for ln, (a0, b0) in lines.items():
            if extra[ln] > 0:
                dcurve = np.maximum(dcurve, window_curve(len(m0), -PAD, [(a0 - LINE_PRE, b0 + LINE_POST)],
                                                         LINE_ATTACK, LINE_RELEASE, extra[ln]))
        m = m0 * undb(-dcurve)[:, None]
        # 4-5. version A bus: glue (reveal protected) + master
        busA = v + s + m
        glA, thrA, grA = glue_gain(busA, p)
        gA, limA = master(busA * glA[:, None], p)
        curveA = glA * undb(gA) * limA
        cA = crop(curveA[:, None], p)
        mg = margins(crop(v, p) * cA, crop(m, p) * cA, crop(s, p) * cA, lines)
        hist.append(dict(it=it, extra_db={k: round(x, 2) for k, x in extra.items()},
                         bed={k: o['vo_over_bed'] for k, o in mg['lines'].items()}))
        short = {ln: LINE_TARGET - o['vo_over_bed'] for ln, o in mg['lines'].items()
                 if o['vo_over_bed'] is not None and o['vo_over_bed'] < LINE_TARGET - 0.02 and extra[ln] < LINE_EXTRA_MAX}
        if not short:
            break
        for ln, d in short.items():
            extra[ln] = min(LINE_EXTRA_MAX, extra[ln] + d + 0.15)
    zA = busA * curveA[:, None]
    # version B: VO + SFX, same internal balance, its own glue / gain / limiter
    busB = v + s
    glB, thrB, grB = glue_gain(busB, p)
    gB, limB = master(busB * glB[:, None], p)
    curveB = glB * undb(gB) * limB
    zB = busB * curveB[:, None]
    # 6. crops: outputs + stems at A's gains
    yA, yB = crop(zA, p), crop(zB, p)
    stems = dict(vo=crop(v, p) * cA, sfx=crop(s, p) * cA, music=crop(m, p) * cA)
    lim_db = lambda g: crop(A.db(np.maximum(g, 1e-12)), p)
    lA, lB = lim_db(limA), lim_db(limB)
    rep = dict(
        module=MODULE, hook=hook, name=name, dur=DUR, samples=N, sr=SR, bits=24, channels=2,
        inputs={k: dict(path=q, sha256=_sha(q)) for k, q in paths.items()},
        chain=dict(pad_s=PAD, vo_lufs=VO_LUFS, sfx_lufs=SFX_LUFS, music_lufs=MUSIC_LUFS, final_lufs=FINAL_LUFS,
                   sfx_duck_vo=SFX_DUCK_VO, music_duck_sfx=MUSIC_DUCK_SFX, music_duck_vo=MUSIC_DUCK_VO,
                   line_target_lu=LINE_TARGET, line_extra_max_db=LINE_EXTRA_MAX, line_pre_post=(LINE_PRE, LINE_POST),
                   line_ramps=(LINE_ATTACK, LINE_RELEASE), glue=dict(ratio=GLUE_RATIO, below_p98_db=GLUE_BELOW_P98,
                                                                    protect=PROTECT, protect_ramp=PROTECT_RAMP,
                                                                    protect_gr_cap_db=PROTECT_GR_CAP),
                   limiter_ceiling_dbfs=LIMIT_CEIL, hero_music_duck=HERO_MUSIC_DUCK, gap_trim=GAP_TRIM,
                   gaps=no_vo_gaps(crop(v, p)) if GAP_TRIM[0] > 0 else []),
        line_topup_db={k: round(x, 2) for k, x in extra.items()}, line_topup_iterations=hist,
        A_full=dict(lufs=round(A.loudness(yA), 3), tp_dbtp=round(A.true_peak(yA), 3), lra=round(A.loudness_range(yA), 2),
                    max_momentary=round(A.momentary_max(yA), 2), master_gain_db=round(float(gA), 3),
                    glue_threshold_db=round(thrA, 2), glue_max_gr_db=round(grA, 2),
                    limiter_max_gr_db=round(float(-lA.min()), 2),
                    limiter_gr_over_1db_s=round(float(np.sum(lA < -1.0) / SR), 3),
                    limiter_gr_over_3db_s=round(float(np.sum(lA < -3.0) / SR), 3),
                    limiter_max_gr_at_s=round(float(np.argmin(lA) / SR), 3), limiter_gr_over_3db_spans=_spans(lA < -3.0)),
        B_vo_sfx=dict(lufs=round(A.loudness(yB), 3), tp_dbtp=round(A.true_peak(yB), 3), lra=round(A.loudness_range(yB), 2),
                      max_momentary=round(A.momentary_max(yB), 2), master_gain_db=round(float(gB), 3),
                      glue_threshold_db=round(thrB, 2), glue_max_gr_db=round(grB, 2),
                      limiter_max_gr_db=round(float(-lB.min()), 2),
                      limiter_gr_over_1db_s=round(float(np.sum(lB < -1.0) / SR), 3),
                      limiter_gr_over_3db_s=round(float(np.sum(lB < -3.0) / SR), 3),
                      limiter_max_gr_at_s=round(float(np.argmin(lB) / SR), 3), limiter_gr_over_3db_spans=_spans(lB < -3.0)),
        stems_lufs={k: round(A.loudness(x), 2) for k, x in stems.items()},
        stems_sum_residual_dbfs=round(float(A.db(np.abs(sum(stems.values()) - yA).max() + 1e-15)), 1),
        vo_over_bed_A=margins(stems['vo'], stems['music'], stems['sfx'], lines),
        vo_over_bed_B=margins(stems['vo'], np.zeros_like(yA), stems['sfx'], lines),
        seam=dict(A=seam(yA, zA, p), B=seam(yB, zB, p), stem_vo=seam(stems['vo']), stem_sfx=seam(stems['sfx']),
                  stem_music=seam(stems['music'])),
    )
    rep.update(_section_checks(yA, yB, stems))
    files = {}
    if write:
        os.makedirs(out, exist_ok=True)
        for key, x in (('mix', yA), ('vo_sfx', yB), ('stem_vo', stems['vo']), ('stem_sfx', stems['sfx']),
                       ('stem_music', stems['music'])):
            files[key] = os.path.join(out, '%s_%s.wav' % (name, key))
            A._write_wav(files[key], x, 24)
        rep['files'] = files
        rep['sha256'] = {k: _sha(q) for k, q in files.items()}
        json.dump(rep, open(os.path.join(out, name + '_mix.json'), 'w'), indent=1, default=float)
        if out == FINAL:
            rep['links'] = _links(name, files)
            json.dump(rep, open(os.path.join(out, name + '_mix.json'), 'w'), indent=1, default=float)
    if verbose:
        keys = ('line_topup_db', 'A_full', 'B_vo_sfx', 'stems_lufs', 'stems_sum_residual_dbfs', 'vo_over_bed_A',
                'reveal', 'clunk', 'dropout', 'seam', 'sha256')
        print(json.dumps({k: rep.get(k) for k in keys}, indent=1, default=float))
    return rep, dict(A=yA, B=yB, **stems)


def _section_checks(yA, yB, stems):
    """BRIEF §18 / HANDOFF §13 sound items that depend on the mix: the reveal is the loudest momentary (+-0.2 s of
    16.0) and by how much; the clunk >= 2 LU below it; the drop-out."""
    o = {}
    tt, lyA = A.loudness_curve(yA)
    _, lyB = A.loudness_curve(yB)
    rv = (tt >= REVEAL_T - 0.2 - 1e-6) & (tt <= REVEAL_T + 0.2 + 1e-6)
    away = (tt < REVEAL_T - 0.4) | (tt > REVEAL_T + 0.8)
    o['reveal'] = {}
    for key, lc in (('A', lyA), ('B', lyB)):
        kr, ko, km = int(np.argmax(np.where(rv, lc, -200))), int(np.argmax(np.where(away, lc, -200))), int(np.argmax(lc))
        o['reveal'][key] = dict(reveal_lufs=round(float(lc[kr]), 2), reveal_centre=round(float(tt[kr]), 3),
                                rest_max_lufs=round(float(lc[ko]), 2), rest_centre=round(float(tt[ko]), 3),
                                margin_lu=round(float(lc[kr] - lc[ko]), 2),
                                global_max_centre=round(float(tt[km]), 3),
                                global_max_is_reveal=bool(rv[km]))
    sel = (tt >= 25.4 - 1e-6) & (tt <= 25.77 + 1e-6)          # window centres holding the clunk, no V6 onset (25.97)
    kc = int(np.argmax(np.where(sel, lyA, -200)))
    o['clunk'] = dict(lufs=round(float(lyA[kc]), 2), centre=round(float(tt[kc]), 3),
                      below_reveal_lu=round(o['reveal']['A']['reveal_lufs'] - float(lyA[kc]), 2))
    a, b4, b = _n(DROP_OUT[0]), _n(DROP_OUT[1] - 0.004), _n(DROP_OUT[1])
    m = stems['music']
    o['dropout'] = dict(music_stem_max_dbfs=round(float(A.db(np.abs(m[a:b4]).max() + 1e-15)), 1),
                        music_stem_max_dbfs_incl_4ms_edge=round(float(A.db(np.abs(m[a:b]).max() + 1e-15)), 1),
                        mix_digital_silence_frames=int(sum(np.abs(yA[a + _n(j / FPS):a + _n((j + 1) / FPS)]).max()
                                                           < 2 ** -23 for j in range(24))),
                        mix_momentary_lufs_by_window_centre={str(c): round(float(lyA[np.argmin(np.abs(tt - c))]), 1)
                                                             for c in (15.4, 15.5, 15.6, 15.7, 15.8)},
                        programme_minus_loudest_dropout_momentary_lu=round(
                            A.loudness(yA) - float(np.max(lyA[(tt >= 15.4 - 1e-6) & (tt <= 15.8 + 1e-6)])), 1))
    return o


def _spans(mask, join=0.02):
    """Boolean per-sample mask -> [(t0, t1), ...] spans (s), gaps < join merged."""
    on = np.flatnonzero(np.diff(np.concatenate([[0], mask.astype(np.int8), [0]])))
    out = []
    for a, b in zip(on[::2] / SR, on[1::2] / SR):
        if out and a - out[-1][1] < join:
            out[-1][1] = round(float(b), 3)
        else:
            out.append([round(float(a), 3), round(float(b), 3)])
    return out


def _links(name, files):
    """HANDOFF §4 / §10 paths -> final/ (relative symlinks) so `render.py --audio <RW>/audio/<name>_mix.wav` works.
    A regular file at a link path is never overwritten."""
    made = {}
    for key in ('mix', 'vo_sfx'):
        lk = os.path.join(AUD, '%s_%s.wav' % (name, key))
        if os.path.exists(lk) and not os.path.islink(lk):
            made[key] = 'kept existing file %s (not a link)' % lk
            continue
        if os.path.islink(lk):
            os.remove(lk)
        os.symlink(os.path.relpath(files[key], AUD), lk)
        made[key] = lk
    return made


# ============================================================================================ verify
def verify(hook='A', out=FINAL):
    """Measure the WRITTEN files: ffprobe format, ffmpeg ebur128 (A, B, stems), an AAC 320k encode exactly as render.py
    muxes (-c:a aac -b:a 320k -ar 48000, no loudnorm) -> its true peak, hero onsets (qa_measure method), the grid, the
    loop seam on the files, and the PNGs."""
    h = HOOKS[hook]
    name = h['name']
    jp = os.path.join(out, name + '_mix.json')
    rep = json.load(open(jp))
    f = rep['files']
    ver = dict(format={k: ffprobe(q) for k, q in f.items()})
    ver['format_ok'] = all(int(d['duration_ts']) == N and d['codec_name'] == 'pcm_s24le' and int(d['sample_rate']) == SR
                           and int(d['channels']) == 2 for d in ver['format'].values())
    ver['ebur128'] = {k: ebur128(q) for k, q in f.items()}
    aac = {}
    for key in ('mix', 'vo_sfx'):
        tmp = os.path.join(out, '_aactest_%s_%s.m4a' % (name, key))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f[key], '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
                        tmp], check=True)
        aac[key] = ebur128(tmp)
        os.remove(tmp)
    ver['aac320k_render_py_path'] = aac
    yA, yB = A.read_wav(f['mix'])[0], A.read_wav(f['vo_sfx'])[0]
    st = {k: A.read_wav(f['stem_' + k])[0] for k in ('vo', 'sfx', 'music')}
    ver['files_stems_sum_residual_dbfs'] = round(float(A.db(np.abs(sum(st.values()) - yA).max() + 1e-15)), 1)
    ver['files_seam'] = dict(A=seam(yA), B=seam(yB))
    cj = json.load(open(os.path.join(AUD, h['cues'])))['cues']
    ons = []
    for key, y in (('A', yA), ('B', yB)):
        for c in cj:
            if c.get('hero'):
                off, rise = onset_near(y, c['t'])
                ons.append(dict(mix=key, name=c['name'], t=c['t'], off_ms=round(off * 1000, 1),
                                off_frames=round(off * FPS, 2), rise_db=round(rise, 1),
                                ok=bool(abs(off) <= 1.0 / FPS + 1e-9)))
    ver['hero_onsets'] = ons
    import log_kya_kahenge_music as LM
    b0, b1 = _n(16.0), _n(25.6)
    ver['grid'] = {'mix A, B section 16.0-25.6, 20-250 Hz': LM.grid_fit(yA[b0:b1], BPM, (20, 250), t0=16.0),
                   'music stem, B section 16.0-25.6, 20-250 Hz': LM.grid_fit(st['music'][b0:b1], BPM, (20, 250),
                                                                            t0=16.0),
                   'music stem, B section, full band (EM.beatgrid)': __import__('epic_music').beatgrid(
                       st['music'][b0:b1], BPM)}
    # kick onsets in the final music stem (LM.env_onset; its detector bias on exact-grid reference kicks is +4.5 to
    # +4.8 ms, music_full.verify.json). The stem carries the mix's duck automation: a duck releasing inside a kick's
    # 120 ms base window reads as an early "onset", so kicks more than 20 ms from the median are listed, not fitted.
    kicks = np.array([16.0 + 0.8 * k for k in range(12)])
    off = np.array([LM.env_onset(st['music'], t, (25, 200))[0] - t for t in kicks])
    ok = np.abs(off - np.median(off)) <= 0.020
    beats = np.round(kicks / 0.8)
    slope, icpt = np.polyfit(beats[ok], (kicks + off)[ok], 1)
    ver['grid']['kick envelope onsets in the final music stem'] = dict(
        offsets_ms=[round(float(o) * 1000, 1) for o in off], fitted=int(ok.sum()),
        excluded_s=[float(t) for t in kicks[~ok]], bpm=round(60.0 / slope, 4), phase_ms=round(icpt * 1000, 2),
        residual_ms_max=round(float(np.abs((kicks + off)[ok] - (slope * beats[ok] + icpt)).max() * 1000), 2),
        detector_bias_ms='+4.5..+4.8 (music_full.verify.json)')
    ver['png'] = _pngs(name, yA, yB, st, rep)
    rep['verify'] = ver
    json.dump(rep, open(jp, 'w'), indent=1, default=float)
    print(json.dumps(ver, indent=1, default=float))
    return rep


def _pngs(name, yA, yB, st, rep):
    """<name>_mix.png: A's spectrogram with bar lines, VO line spans and events, the momentary loudness lanes (VO, music,
    SFX, mix), B's spectrogram. <name>_zooms.png: the reveal, the clunk, the drop-out and the loop seam (spectrogram +
    a +-12 ms sample-level waveform across the seam for A and B)."""
    from PIL import Image, ImageDraw
    W = 1800
    xs = lambda t: int(round(t / DUR * W))
    title = '%s  version A  |  I %.2f LUFS  TP %.2f dBTP  LRA %.1f LU  |  VO over bed %.1f LU' % (
        name, rep['A_full']['lufs'], rep['A_full']['tp_dbtp'], rep['A_full']['lra'],
        rep['vo_over_bed_A']['overall']['vo_over_bed'])
    pa = A.spectro_image(yA, W, 520, None, title, 'orange = bar lines (75 BPM, 3.2 s); red = drop-out 15.2-16.0; cyan = '
                         'reveal 16.0 / clunk 25.6 / tap 29.6; ivory bars = VO lines (words.json)', tmax=DUR)
    dr = ImageDraw.Draw(pa)
    for b in range(12):
        dr.line([(xs(b * 3.2), 44), (xs(b * 3.2), 502)], fill=(255, 140, 40), width=1)
    for t in DROP_OUT:
        dr.line([(xs(t), 44), (xs(t), 502)], fill=(255, 40, 40), width=2)
    for t in (REVEAL_T, CLUNK_T, 29.6):
        dr.line([(xs(t), 44), (xs(t), 502)], fill=(80, 230, 255), width=1)
    for ln, o in rep['vo_over_bed_A']['lines'].items():
        a0, b0 = o['t']
        dr.rectangle([xs(a0), 40, xs(b0), 43], fill=(255, 243, 230))
        dr.text((xs(a0) + 2, 46), ln, fill=(255, 243, 230), font=A._font(11, True))
    H = 230
    lanes = Image.new('RGB', (W, H), (14, 10, 18))
    dl = ImageDraw.Draw(lanes)
    lo, hi = -50.0, -4.0
    yy = lambda l: int((hi - np.clip(l, lo, hi)) / (hi - lo) * (H - 20)) + 10
    for ref in (-14, -16, -18, -26, -40):
        dl.line([(0, yy(ref)), (W, yy(ref))], fill=(60, 50, 70))
        dl.text((4, yy(ref) - 12), '%d' % ref, fill=(140, 130, 150), font=A._font(10))
    for x, col in ((yA, (150, 150, 150)), (st['music'], (255, 120, 40)), (st['sfx'], (240, 50, 45)),
                   (st['vo'], (255, 243, 230))):
        tt, lv = A.loudness_curve(x)
        dl.line([(xs(t), yy(l)) for t, l in zip(tt, lv)], fill=col, width=2)
    dl.text((W - 520, 4), 'momentary LUFS (400 ms): VO ivory, music orange, SFX red, mix A grey', fill=(200, 190, 210),
            font=A._font(12))
    pb = A.spectro_image(yB, W, 360, None, '%s  version B (VO + SFX)  |  I %.2f LUFS  TP %.2f dBTP  LRA %.1f LU' % (
        name, rep['B_vo_sfx']['lufs'], rep['B_vo_sfx']['tp_dbtp'], rep['B_vo_sfx']['lra']), '', tmax=DUR)
    img = Image.new('RGB', (W, 520 + H + 360), (14, 10, 18))
    img.paste(pa, (0, 0))
    img.paste(lanes, (0, 520))
    img.paste(pb, (0, 520 + H))
    p1 = os.path.join(FINAL, name + '_mix.png')
    img.save(p1)
    # zooms
    Z = 590
    tiles = [A.spectro_image(yA[_n(14.6):_n(17.4)], Z, 380, 1.4, 'A: drop-out + reveal 14.6-17.4 s',
                             'cyan = 16.0 (reveal); silence 15.2-16.0 except the SFX floor', tmax=2.8),
             A.spectro_image(yA[_n(25.0):_n(27.0)], Z, 380, 0.6, 'A: the clunk 25.0-27.0 s', 'cyan = 25.6', tmax=2.0),
             A.spectro_image(np.concatenate([yA[-_n(1.2):], yA[:_n(1.2)]]), Z, 380, 1.2,
                             'A: loop seam 34.0-35.2 | 0.0-1.2 s', 'cyan = the seam', tmax=2.4)]
    wv = []
    for key, y in (('A', yA), ('B', yB)):
        k = _n(0.012)
        seg = np.concatenate([y[-k:], y[:k]])
        im = Image.new('RGB', (Z, 300), (14, 10, 18))
        d2 = ImageDraw.Draw(im)
        d2.text((8, 4), '%s: samples across the seam (+-12 ms), L orange / R pink' % key, fill=(250, 245, 240),
                font=A._font(14, True))
        sc = 110 / max(np.abs(seg).max(), 1e-9)
        for c, col in ((0, (255, 150, 80)), (1, (255, 100, 170))):
            pts = [(int(i / (2 * k) * Z), 170 - int(seg[i, c] * sc)) for i in range(2 * k)]
            d2.line(pts, fill=col, width=1)
        d2.line([(Z // 2, 30), (Z // 2, 296)], fill=(80, 230, 255))
        d2.text((8, 280), 'step %.5f vs local median %.5f' % (rep['seam'][key]['step'], rep['seam'][key]['local_median_step']),
                fill=(200, 190, 210), font=A._font(12))
        wv.append(im)
    tiles.append(A.spectro_image(np.concatenate([yB[-_n(1.2):], yB[:_n(1.2)]]), Z, 380, 1.2,
                                 'B: loop seam 34.0-35.2 | 0.0-1.2 s', 'cyan = the seam', tmax=2.4))
    zi = Image.new('RGB', (3 * Z + 20, 380 * 2 + 300 + 20), (14, 10, 18))
    for i, t in enumerate(tiles[:3]):
        zi.paste(t, (i * (Z + 10), 0))
    zi.paste(tiles[3], (0, 390))
    zi.paste(wv[0], (Z + 10, 390))
    zi.paste(wv[1], (2 * (Z + 10), 390))
    p2 = os.path.join(FINAL, name + '_zooms.png')
    zi.save(p2)
    return [p1, p2]


def determinism(hooks='AB'):
    """Rebuild each hook into a scratch folder and compare every output's sha256 with final/ (then delete it)."""
    res = {}
    for hk in hooks:
        name = HOOKS[hk]['name']
        ref = json.load(open(os.path.join(FINAL, name + '_mix.json')))['sha256']
        tmp = os.path.join(AUD, '_detcheck_' + hk)
        try:
            rep, _ = mix(hk, out=tmp, verbose=False)
            res[name] = {k: rep['sha256'][k] == ref[k] for k in ref}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps(dict(identical=res, all=all(all(d.values()) for d in res.values())), indent=1))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('build', 'verify', 'all', 'determinism'))
    ap.add_argument('--hook', choices=('A', 'B', 'AB'), default='AB')
    a = ap.parse_args(argv)
    if a.cmd == 'determinism':
        return determinism(a.hook)
    for hk in a.hook:
        if a.cmd in ('build', 'all'):
            mix(hk)
        if a.cmd in ('verify', 'all'):
            verify(hk)


if __name__ == '__main__':
    main()
