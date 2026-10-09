#!/usr/bin/env python3
"""bijli_chali_gayi_music.py: the music layer of Reel 2 · C11 "Bijli Chali Gayi" (owner: music-supervisor).

C11 HAS NO MUSIC BED, and that is binding: SLATE §3.2 says "No beat bed (this keeps C11's sound world apart from the
four scored reels)", SLATE §5.2 sets the C11 bed to "diegetic appliances + harmonium", BRIEF §0 and §6.11 say "Style: none.
No epic_music style, no score.py bed, no beat bed", packet.yaml says "No music bed and no score", and the QA list (BRIEF §8)
fails "a music bed". The 90-BPM grid is carried by the sound-designer's diegetic cues: the backup beeps (beats 2-3 of bar 0),
the keycap thocks (quarters in bar 7, 8ths in bar 8) and the fan's blade pass.

The reel's only music is its one desi voice (BRIEF §6.11): the epic_sfx `harmonium_swell` chord D3 A3 D4 F#4 (D major,
Sa = D3 146.83 Hz). It is placed so the swell starts at the end of the drop-out (f800, 26.667 s, the bar-10 downbeat)
and peaks on f820 (27.333 s, beat 41), where the VO says "sabr". This file renders that layer in reel time, so the
harmonium can be placed, measured and mixed (FULL vs DRY) separately from the SFX.

Procedural and deterministic: the one sound comes from workspace/brand_reels/sfx/epic_sfx.py (pure numpy/scipy synthesis,
seed 0, built on the toolkit's audio.py). It uses no samples, no song, no AI model and no epic_music style. Licence:
original work for @jawad_mp4.

    duration = 20 frames / 0.72 = 0.925926 s (BRIEF's "0.926", taken exactly so that start = f800 and peak = f820 to the
               sample; harmonium_swell peaks at 0.72 x duration)
    start    = sample 1,280,000 (f800)   peak = sample 1,312,000 (f820)   tail ends 28.554 s (1.887 s sound)
    silence  = everything else, including the drop-out f790-f799 and the loop seam (34.667 s -> 0.0)
    level    = -16.0 LUFS integrated (BS.1770 gated, i.e. the sting's own loudness), true peak <= -2.0 dBTP, no limiter
    format   = 48 kHz, 24-bit PCM, stereo, exactly 1,664,000 samples (DUR = 1040 / 30 = 34.667 s, 13 bars at 90 BPM)

CLI (run from pipeline/jawad_reels; route the work through tools/heavy.sh as the brief requires):
    python3 bijli_chali_gayi_music.py build  [--out DIR]   -> DIR/music_full.wav, DIR/stems/music_stem_harmonium.wav,
                                                              DIR/music_full.json (map, events, render numbers, hashes)
    python3 bijli_chali_gayi_music.py verify [--out DIR]   -> DIR/music_full.verify.json + DIR/music_full_spectrogram.png,
                                                              DIR/music_zoom_payoff.png (re-renders in memory and checks
                                                              that the file is bit-identical)
    python3 bijli_chali_gayi_music.py grid WAV [--t0 S --t1 S] -> spectral-flux 90-BPM grid fit of any wav (for run 2:
                                                              the SFX stem or the mixes; default window = keycap bars
                                                              7-8, 18.667-24.0 s)
DIR defaults to workspace/jawad_reels/bijli_chali_gayi/music.
"""
import argparse
import hashlib
import json
import os
import re
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
from scipy import signal  # noqa: E402
from scipy.ndimage import uniform_filter1d, maximum_filter1d, median_filter  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as E  # noqa: E402
from audio import SR, undb, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'bijli_chali_gayi'
FPS, BPM = 30, 90.0
DUR = 1040 / FPS                                # 34.667 s = 1,040 frames = 13 bars
BEAT = 60.0 / BPM                               # 0.6667 s = 20 frames
BAR = 4 * BEAT                                  # 2.6667 s = 80 frames
N = _n(DUR)
assert N == 1664000 and N == 1040 * SR // FPS
SPF = SR // FPS                                 # 1,600 samples per frame
OUT = os.path.join(A.WS, MODULE, 'music')
TARGET_LUFS, TP_CEILING = -16.0, -2.0
KEY = 'D major (Sa = D3 146.83 Hz)'

F_START, F_PEAK = 800, 820                      # swell starts on the bar-10 downbeat, peaks on beat 41 ("sabr")
DROP_OUT_F = (790, 800)                         # f790-f799: the reveal's drop-out (room tone only, from the SFX stem)
HARM = dict(duration=(F_PEAK - F_START) / FPS / 0.72, notes=(50, 57, 62, 66), seed=0)   # 0.925926 s, D3 A3 D4 F#4
NOTE_HZ = {E_name: E.midi_hz(m) for E_name, m in (('D3', 50), ('A3', 57), ('D4', 62), ('F#4', 66))}
STEMS = ('harmonium',)

SECTIONS = [  # (bars, t0, t1, edit events (BRIEF §6.1), music events)
    ('0', 0, 1, 'HOOK (A blackout / B torch-lit); beeps f40, f60; splice f80', 'none (mains hum -> silence -> crickets)'),
    ('1-2', 1, 3, 'candle, pankhi, homework; tilt up f140-f159; rooftops', 'none (crickets, night air)'),
    ('3', 3, 4, 're-hook 1 f240: power back, AA GAYI!, cheer; dies again f300', 'none (appliance chorus, cheer)'),
    ('4', 4, 5, 'L7 torch beam into the old room f320', 'none (room tone)'),
    ('5', 5, 6, 'lights on f400: modern edit desk, render 63 %', 'none (edit-suite hum)'),
    ('6', 6, 7, 're-hook 2 f480: power dies mid-render', 'none (dead room)'),
    ('7-8', 7, 9, 'L8 iris f560; Ctrl+S keycaps on quarters, then 8ths from f640', 'none (keycap thocks = the percussion)'),
    ('9', 9, 10, 'candle macro, JD profile by candlelight; drop-out f790-f799', 'none; silence through the drop-out'),
    ('10', 10, 11, 'PAYOFF f800: BIJLI NE SIKHAAYA / sabr; "sabr" f820', 'harmonium swell D3 A3 D4 F#4: starts f800, '
     'peaks f820, tail out by 28.554 s'),
    ('11', 11, 12, 'power returns f880 (loudest, L4); end card f920', 'none (riser + appliance chorus are SFX)'),
    ('12', 12, 13, 'end card hold; loop into frame 0 at f1040', 'none: silent seam (mains hum bed carries the loop)'),
]


def T(bar, beat=0.0):
    """Reel time (s) of bar `bar`, beat `beat` (both from 0)."""
    return (bar * 4 + beat) * BEAT


def bar_beat(t):
    b = t / BEAT
    return '%d:%g' % (int(b // 4), round(b % 4, 3))          # bar:beat, both from 0


# ============================================================================================ build
def compose():
    """-> (stems dict of float64 (N, 2) arrays at their raw epic_sfx level, event list, placement info)."""
    E.register()
    h = np.asarray(A.sound('harmonium_swell', **HARM), dtype=np.float64)
    hit = A.hit_offset('harmonium_swell', **HARM)
    i_hit = F_PEAK * SPF                                           # 1,312,000
    i0 = i_hit - int(round(hit * SR))
    assert abs(hit * SR - round(hit * SR)) < 1e-6, hit
    assert i0 == F_START * SPF, (i0, F_START * SPF)                # starts exactly on f800 (sample 1,280,000)
    assert i0 + len(h) <= N
    harm = np.zeros((N, 2))
    harm[i0:i0 + len(h)] = h
    t_end = (i0 + len(h)) / SR
    ev = [dict(t=i0 / SR, what='harmonium swell starts (D3 A3 D4 F#4), end of the drop-out', stem='harmonium'),
          dict(t=i_hit / SR, what='harmonium peak ("sabr")', stem='harmonium'),
          dict(t=t_end, what='harmonium tail ends (room reverb included)', stem='harmonium')]
    for e in ev:
        e['f'] = round(e['t'] * FPS, 3)
        e['bar_beat'] = bar_beat(e['t'])
    info = dict(sound='epic_sfx.harmonium_swell', params=dict(HARM, notes=list(HARM['notes'])),
                hit_offset_s=hit, start_sample=i0, peak_sample=i_hit, end_sample=i0 + len(h),
                sound_len_s=len(h) / SR, raw_lufs=A.loudness(harm), raw_true_peak_dbtp=A.true_peak(harm))
    return dict(harmonium=harm), ev, info


def level(stems):
    """Bus: one static gain to TARGET_LUFS (no limiter unless the true peak would pass the ceiling - 0.3 dB)."""
    pre = sum(stems.values())
    g = TARGET_LUFS - A.loudness(pre)
    gl = np.ones(N)
    if A.true_peak(pre * undb(g)) > TP_CEILING - 0.3:              # not expected for this sting; kept as a guard
        for _ in range(12):
            gl = A.limiter_gain(pre * undb(g), TP_CEILING - 0.3)
            L = A.loudness(pre * undb(g) * gl[:, None])
            if abs(L - TARGET_LUFS) < 0.03:
                break
            g += TARGET_LUFS - L
    curve = undb(g) * gl
    out = {k: v * curve[:, None] for k, v in stems.items()}
    mix = sum(out.values())
    info = dict(lufs=round(A.loudness(mix), 3), true_peak_dbtp=round(A.true_peak(mix), 3),
                sample_peak_dbfs=round(float(A.db(np.abs(mix).max())), 3), lra=round(A.loudness_range(mix), 2),
                momentary_max_lufs=round(A.momentary_max(mix), 2), gain_db=round(float(g), 3),
                limiter_max_gr_db=round(float(-A.db(gl.min())), 3))
    return mix, out, info


def _q24(x):
    """The exact int24 values audio._write_wav stores."""
    return np.clip(np.round(A._st(x) * 8388607.0), -8388608, 8388607).astype(np.int32)


def build(out=OUT):
    stems, ev, place = compose()
    mix, st, info = level(stems)
    assert mix.shape == (N, 2)
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    full = os.path.join(out, 'music_full.wav')
    A._write_wav(full, mix, 24)
    paths = {}
    for k in STEMS:
        paths[k] = os.path.join(out, 'stems', 'music_stem_%s.wav' % k)
        A._write_wav(paths[k], st[k], 24)
    meta = dict(module=MODULE, file=full, stems=paths, dur=DUR, frames=1040, samples=N, sr=SR, bits=24, channels=2,
                bpm=BPM, beat_s=BEAT, bar_s=BAR, frames_per_beat=20, key=KEY,
                policy='no music bed (SLATE §3.2 / §5.2, BRIEF §0 / §6.11 / §8): the only music is the one desi voice, '
                       'a harmonium swell peaking on "sabr"',
                source='procedural: epic_sfx.harmonium_swell (numpy/scipy synthesis, seed 0); no samples, no song, '
                       'no AI model, no epic_music style',
                licence='original work for @jawad_mp4',
                drop_out=dict(frames=list(DROP_OUT_F), t=[DROP_OUT_F[0] / FPS, DROP_OUT_F[1] / FPS],
                              music='silent (exact zeros)'),
                loop_seam='silent on both sides (the music ends at %.3f s; the SFX mains-hum bed carries the loop)'
                          % (place['end_sample'] / SR),
                placement=place, events=ev,
                sections=[dict(bars=a, t0=T(b), t1=T(c), f0=round(T(b) * FPS), f1=round(T(c) * FPS), edit=d, music=e)
                          for a, b, c, d, e in SECTIONS],
                render=info, sha256=_sha(full), stem_sha256={k: _sha(p) for k, p in paths.items()},
                deps_sha256={os.path.basename(m.__file__): _sha(m.__file__) for m in (A, E)})
    json.dump(meta, open(os.path.join(out, 'music_full.json'), 'w'), indent=1)
    print(json.dumps(dict(file=full, **info, sha256=meta['sha256']), indent=1))
    return meta


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ============================================================================================ measurement helpers
def _ffprobe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,'
                        'bits_per_sample,duration_ts,duration', '-of', 'json', p], capture_output=True, text=True)
    return json.loads(r.stdout)['streams'][0]


def _ebur128(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    get = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I_lufs=get('I'), LRA_lu=get('LRA'), true_peak_dbfs=get('Peak'), threshold=get('Threshold'))


def _dbfs(x):
    x = np.asarray(x, dtype=np.float64)
    if not np.any(x):
        return dict(rms_dbfs=None, peak_dbfs=None, note='digital silence (all samples 0)')
    return dict(rms_dbfs=round(float(A.db(np.sqrt(np.mean(np.square(x))))), 2),
                peak_dbfs=round(float(A.db(np.abs(x).max())), 2))


def env(x, win):
    """RMS envelope (centred moving window of `win` s) of the channel mean power."""
    p = np.square(A._st(x)).mean(1)
    return np.sqrt(uniform_filter1d(p, max(1, _n(win)), mode='constant'))


def onsets(x, hop=120, nfft=1024, k=1.5, min_gap=0.08):
    """Blind onset detector: log-magnitude spectral flux (2.5 ms hop), adaptive threshold (moving median + k x MAD over
    1 s, plus 2 % of the max), local maxima >= min_gap apart. Returns (times, strengths)."""
    m = A._st(x).mean(1)
    f, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop, boundary='zeros', padded=True)
    M = np.log1p(np.abs(Z) * 1000.0)
    fl = np.concatenate([[0.0], np.maximum(np.diff(M, axis=1), 0).sum(0)])
    w = int(1.0 * SR / hop)
    med = median_filter(fl, w, mode='nearest')
    mad = median_filter(np.abs(fl - med), w, mode='nearest')
    thr = med + k * np.maximum(mad, 1e-9) + 0.02 * fl.max()
    g = int(min_gap * SR / hop)
    i = np.nonzero((fl == maximum_filter1d(fl, 2 * g + 1)) & (fl > thr))[0]
    return tt[i] - hop / SR / 2, fl[i]


def _grid_raw(x, bpm, t0, t1, span=0.03, step=0.0025):
    """The music-supervisor's beatgrid snippet (spectral flux, 2048-point STFT, 5 ms hop) on [t0, t1] -> (tempo, phase s
    against the reel's beat 0 folded to +-half a beat, on-grid strength)."""
    m = A._st(x).mean(1)[_n(t0):_n(t1)]
    _, tt, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - 240)
    fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 100), axis=1), 0).sum(0)
    hop = 240 / SR

    def sc(b, off):
        i = np.round((off + np.arange(0, tt[-1] - off, 60 / b)) / hop).astype(int)
        return fl[i[i < len(fl)]].mean()
    s_, b, off = max((sc(b, o), b, o) for b in bpm * np.arange(1 - span, 1 + span + 1e-9, step)
                     for o in np.arange(0, 60 / b, 0.001))
    off = ((off + t0) + 30 / b) % (60 / b) - 30 / b
    return float(b), float(off), float(s_ / max(fl.mean(), 1e-12))


def grid_fit(x, bpm=BPM, t0=0.0, t1=None):
    """Tempo, beat phase and on-grid strength (> 2 = on a grid) of x on [t0, t1]. The 2048-point flux lights up while
    an onset enters the window's leading half, so the raw phase reads early; the method bias is measured on a
    reference click track exactly on the reel grid (same window, same code) and subtracted."""
    t1 = DUR if t1 is None else t1
    b, off, s_ = _grid_raw(x, bpm, t0, t1)
    ref = np.random.default_rng(0).standard_normal((_n(DUR), 2)) * 1e-4
    u = np.arange(_n(0.05)) / SR
    clk = (np.sin(2 * np.pi * 160 * u) * np.exp(-u * 60) + np.random.default_rng(1).standard_normal(len(u))
           * np.exp(-u * 400) * 0.5)
    for k in range(int(np.ceil(t0 / BEAT)), int(t1 / BEAT) + 1):
        i = int(round(k * BEAT * SR))
        if i + len(u) <= len(ref):
            ref[i:i + len(u)] += clk[:, None] * 0.5
    _, bias, _ = _grid_raw(ref, bpm, t0, t1)
    return dict(window_s=[round(t0, 3), round(t1, 3)], tempo_bpm=round(b, 3), phase_ms=round((off - bias) * 1000, 1),
                phase_raw_ms=round(off * 1000, 1), method_bias_ms=round(bias * 1000, 1), strength=round(s_, 2),
                ok=bool(abs(b - bpm) <= 0.2 and abs(off - bias) <= 0.015 and s_ > 2))


def _centroid_cents(seg, f0, rel=0.012):
    """Power-weighted mean frequency within +-1.2 % (+-20 cents) of f0, in cents from f0. Each note is a pair of reeds at
    +-2.5 cents that beat (0.85 Hz at D4) inside a < 2 s sound, which biases a peak pick by up to ~8 cents; the power
    centroid of a symmetric pair sits on its centre frequency whatever the beat phase."""
    nf = 1 << 21
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), nf)) ** 2
    fr = np.fft.rfftfreq(nf, 1 / SR)
    sel = (fr > f0 * (1 - rel)) & (fr < f0 * (1 + rel))
    fc = float((S[sel] * fr[sel]).sum() / S[sel].sum())
    return fc, 1200 * np.log2(fc / f0), float(10 * np.log10(S[sel].sum() + 1e-30))


def pitch_check(x, t0, t1):
    """Tuning of the chord over [t0, t1] (the whole sting): power centroid per note (see _centroid_cents), plus the same
    measurement on a solo render of each note (separates the source tuning from chord overlap: D3's 2nd harmonic lies
    on D4's two reed frequencies). Also the pitch-class energy share (100 Hz-4 kHz) to show which notes the spectrum
    holds (pulse reeds carry every harmonic, so E = 9th harmonic of D and C#/G# = upper harmonics appear faintly)."""
    m = A._st(x).mean(1)[_n(t0):_n(t1)]
    notes, lv = {}, {}
    for (nm, f0), midi in zip(NOTE_HZ.items(), HARM['notes']):
        fc, c, lv[nm] = _centroid_cents(m, f0)
        solo = np.asarray(A.sound('harmonium_swell', duration=HARM['duration'], notes=(midi,), seed=HARM['seed']),
                          dtype=np.float64).mean(1)
        _, cs, _ = _centroid_cents(solo, f0)
        notes[nm] = dict(expected_hz=round(f0, 3), chord_centroid_hz=round(fc, 3), chord_cents=round(float(c), 2),
                         solo_render_cents=round(float(cs), 2))
    top = max(lv.values())
    for nm in notes:
        notes[nm]['level_db_rel'] = round(lv[nm] - top, 1)
    nf = 1 << 21
    S = np.abs(np.fft.rfft(m * np.hanning(len(m)), nf)) ** 2
    fr = np.fft.rfftfreq(nf, 1 / SR)
    pc = np.zeros(12)
    sel = (fr >= 100) & (fr <= 4000)
    midi = np.round(69 + 12 * np.log2(fr[sel] / 440.0)).astype(int) % 12
    np.add.at(pc, midi, S[sel])
    pc /= pc.sum()
    names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    order = np.argsort(pc)[::-1]
    return dict(window_s=[round(t0, 3), round(t1, 3)], method='power centroid +-20 c (Hann, 2^21-point FFT)',
                notes=notes, chord_tone_share=round(float(pc[2] + pc[6] + pc[9]), 4),
                top_pitch_classes=[(names[i], round(float(pc[i]), 4)) for i in order[:6]],
                ok=all(abs(v['solo_render_cents']) <= 2.0 and abs(v['chord_cents']) <= 5.0 for v in notes.values()))


def band_shares(x, t0, t1):
    """Energy share per band over [t0, t1] (for the VO-pocket check: 1-4 kHz is where the words live)."""
    m = A._st(x).mean(1)[_n(t0):_n(t1)]
    S = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2
    fr = np.fft.rfftfreq(len(m), 1 / SR)
    tot = S.sum()
    bands = [(0, 120), (120, 250), (250, 1000), (1000, 4000), (4000, 24000)]
    return {'%d-%d Hz' % b: round(float(S[(fr >= b[0]) & (fr < b[1])].sum() / tot), 4) for b in bands}


# ============================================================================================ pictures
def spec_png(x, t0, t1, path, title, sub, w=1600, h=460, marks=(), bars=True, shade=None):
    """audio.spectro_image of [t0, t1] with bar lines (dim), beat ticks and labelled markers [(t, label, rgb)]."""
    from PIL import Image, ImageDraw
    seg = A._st(x)[_n(t0):_n(t1)]
    im = A.spectro_image(A.Sfx(seg, 0, 'music'), w, h, None, title, sub, fmin=30.0, fmax=20000.0, dyn=80.0)
    X = lambda t: int(round((t - t0) / (t1 - t0) * w))
    top, bot = 44, h - 18
    if shade:                                                      # translucent blue band (content stays visible)
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
        do = ImageDraw.Draw(ov)
        for a, b in shade:
            do.rectangle([max(X(a), 0), top, min(X(b), w) - 1, bot], fill=(60, 120, 200, 70))
        im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    dr = ImageDraw.Draw(im)
    if bars:
        k0, k1 = int(np.ceil(t0 / BEAT - 1e-9)), int(np.floor(t1 / BEAT + 1e-9))
        for k in range(k0, k1 + 1):
            xx = X(k * BEAT)
            if k % 4 == 0:
                dr.line([(xx, top), (xx, bot)], fill=(110, 100, 130))
                dr.text((xx + 3, top + 2), 'bar %d' % (k // 4), fill=(200, 190, 215), font=A._font(11))
            elif (t1 - t0) < 8:
                dr.line([(xx, bot - 8), (xx, bot)], fill=(150, 140, 170))
    for i, (t, label, col) in enumerate(marks):
        xx = X(t)
        dr.line([(xx, top), (xx, bot)], fill=col, width=1)
        dr.text((xx + 3, top + 16 + 14 * (i % 3)), label, fill=col, font=A._font(11))
    im.save(path)
    return path


# ============================================================================================ verify
def verify(out=OUT):
    full = os.path.join(out, 'music_full.wav')
    meta = json.load(open(os.path.join(out, 'music_full.json')))
    x, sr = A.read_wav(full)
    assert sr == SR
    rep = dict(file=full, sha256=_sha(full), sha256_matches_build=_sha(full) == meta['sha256'])
    pr = _ffprobe(full)
    rep['format'] = dict(pr, ok=(pr['codec_name'] == 'pcm_s24le' and int(pr['sample_rate']) == SR
                                 and int(pr['channels']) == 2 and int(pr['duration_ts']) == N))
    eb = _ebur128(full)
    rep['loudness'] = dict(ffmpeg_ebur128=eb, toolkit_lufs=round(A.loudness(x), 3),
                           toolkit_true_peak_dbtp=round(A.true_peak(x), 3),
                           momentary_max_lufs=round(A.momentary_max(x), 2),
                           ok=(abs(eb['I_lufs'] - TARGET_LUFS) <= 0.1 and eb['true_peak_dbfs'] <= TP_CEILING
                               and A.true_peak(x) <= TP_CEILING))
    # determinism: a fresh in-memory render must equal the file sample for sample
    stems, _, _ = compose()
    mix, _, _ = level(stems)
    q = _q24(mix)
    fq = np.round(x * 8388608.0).astype(np.int32)
    rep['deterministic'] = dict(int24_samples_differing=int(np.count_nonzero(q != fq)),
                                ok=bool(np.array_equal(q, fq)))
    # stems sum to the mix
    st = {k: A.read_wav(p)[0] for k, p in meta['stems'].items()}
    rep['stems_sum'] = dict(max_abs_diff=float(np.abs(sum(st.values()) - x).max()),
                            ok=bool(np.abs(sum(st.values()) - x).max() <= 2.0 / 8388608))
    # silence, drop-out, seam
    nz = np.nonzero(np.abs(x).max(1) > 0)[0]
    first, last = int(nz[0]), int(nz[-1])
    d0, d1 = DROP_OUT_F
    rep['silence'] = dict(
        first_nonzero_sample=first, first_nonzero_s=round(first / SR, 6),
        first_nonzero_after_f800_ms=round((first - F_START * SPF) / SR * 1000, 3),
        last_nonzero_sample=last, last_nonzero_s=round(last / SR, 4),
        zeros_before_f800=bool(not np.any(x[:F_START * SPF])),
        dropout_f791_f798=_dbfs(x[(d0 + 1) * SPF:(d1 - 1) * SPF]), dropout_f790_f799=_dbfs(x[d0 * SPF:d1 * SPF]),
        first_0p5s=_dbfs(x[:_n(0.5)]), last_0p5s=_dbfs(x[-_n(0.5):]),
        silent_after_s=round((last + 1) / SR, 4),
        ok=bool(not np.any(x[:F_START * SPF]) and not np.any(x[-_n(0.5):]) and first >= F_START * SPF))
    # placement on the grid
    e5, e10 = env(x, 0.005), env(x, 0.010)
    pk10 = int(np.argmax(e10))
    lc_t, lc = A.loudness_curve(x, 0.4, 0.005)
    a40 = int(np.argmax(e5 > e5.max() * undb(-40)))
    a20 = int(np.argmax(e5 > e5.max() * undb(-20)))
    ons, strg = onsets(x)
    rep['placement'] = dict(
        start_digital=dict(t=round(first / SR, 4), f=round(first / SPF, 3), beat=round(first / SR / BEAT, 4)),
        start_minus40db=dict(t=round(a40 / SR, 4), f=round(a40 / SPF, 3), note='5 ms RMS envelope crosses -40 dB rel. '
                             'its max (a swell from zero: (t/0.667)^1.6 reaches -40 dB 37 ms in)'),
        start_minus20db=dict(t=round(a20 / SR, 4), f=round(a20 / SPF, 3)),
        peak_rms10ms=dict(t=round(pk10 / SR, 4), f=round(pk10 / SPF, 3), beat=round(pk10 / SR / BEAT, 4),
                          err_ms_vs_f820=round((pk10 - F_PEAK * SPF) / SR * 1000, 2)),
        peak_momentary400ms_centre=dict(t=round(float(lc_t[np.argmax(lc)]), 3), lufs=round(float(lc.max()), 2)),
        spectral_flux_onsets=[dict(t=round(float(t), 4), f=round(float(t) * FPS, 2), strength=round(float(s), 1))
                              for t, s in zip(ons, strg)],
        ok=bool(first >= F_START * SPF and (first - F_START * SPF) < _n(0.001)
                and abs(pk10 - F_PEAK * SPF) <= SPF))
    rep['tempo'] = ('not estimable from this file by design: the music layer is one sustained swell (no beat bed, '
                    'BRIEF §6.11); the 90-BPM grid lives in the SFX stem (beeps, keycap thocks). Placement on the grid '
                    'is measured above: start = beat 40 (bar 10 downbeat), peak = beat 41. Run `grid` on the SFX stem '
                    'or the mixes in run 2.')
    rep['pitch'] = pitch_check(x, F_START / FPS, (last + 1) / SR)
    rep['band_shares_sting'] = band_shares(x, F_START / FPS, (last + 1) / SR)
    rep['ok'] = all(rep[k]['ok'] for k in ('format', 'loudness', 'deterministic', 'stems_sum', 'silence', 'placement',
                                           'pitch'))
    # pictures
    gold, cyan, red, ivory = (255, 181, 71), (80, 230, 255), (242, 49, 43), (255, 243, 230)
    marks = [(F_START / FPS, 'f800 start', gold), (F_PEAK / FPS, 'f820 peak "sabr"', ivory),
             (880 / FPS, 'f880 power returns (SFX)', red)]
    rep['png'] = [
        spec_png(x, 0.0, DUR, os.path.join(out, 'music_full_spectrogram.png'),
                 'C11 Bijli Chali Gayi · music layer (harmonium only, no bed) · 34.667 s',
                 '%.2f LUFS · %.2f dBTP · bars of 90 BPM · blue = drop-out f790-f799' % (
                     eb['I_lufs'], eb['true_peak_dbfs']), marks=marks, shade=[(d0 / FPS, d1 / FPS)]),
        spec_png(x, T(9, 2), T(11, 1), os.path.join(out, 'music_zoom_payoff.png'),
                 'zoom 25.333-30.000 s (bar 9 beat 2 -> bar 11 beat 1): drop-out, harmonium, power return',
                 'ticks = beats (20 f); blue = drop-out f790-f799; markers from the brief', w=1400,
                 marks=[(d0 / FPS, 'f790 drop-out', cyan)] + marks, shade=[(d0 / FPS, d1 / FPS)])]
    json.dump(rep, open(os.path.join(out, 'music_full.verify.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


# ============================================================================================ CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for c in ('build', 'verify'):
        p = sub.add_parser(c)
        p.add_argument('--out', default=OUT)
    p = sub.add_parser('grid')
    p.add_argument('wav')
    p.add_argument('--t0', type=float, default=T(7))
    p.add_argument('--t1', type=float, default=T(9))
    a = ap.parse_args()
    if a.cmd == 'build':
        build(a.out)
    elif a.cmd == 'verify':
        r = verify(a.out)
        sys.exit(0 if r['ok'] else 1)
    else:
        x, sr = A.read_wav(a.wav)
        assert sr == SR, sr
        print(json.dumps(grid_fit(x, BPM, a.t0, a.t1), indent=1))


if __name__ == '__main__':
    main()
