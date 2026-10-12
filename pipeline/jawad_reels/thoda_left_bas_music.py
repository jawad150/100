#!/usr/bin/env python3
"""thoda_left_bas_music.py: original music bed + THE SIGNAL CLOCK of Bijli series #2 "Thoda Left... Bas Bas!"
(owner: sound designer / music supervisor). Binding plan: brand_reels/design/reels/thoda_left_bas/SHOTS.md section 0
(the two clocks) and section b (SOUND), BRIEF.md section 2 (the signal grammar) and 3 (grid). Notes: SOUND.md (same folder).

=====================================================================================================================
THE SIGNAL CLOCK (import this in the picture so picture and sound never drift)
=====================================================================================================================
    import thoda_left_bas_music as TM
    TM.yaw(f)        antenna yaw in degrees at frame f (float or array; SHOTS section 0 table, eases, wind wobble;
                     f >= 936 runs on the f - 1080 clock = the snowy pre-roll, so f1079 -> f0 is continuous)
    TM.sig(f)        0 = locked .. 1 = no signal: clamp(|yaw| / 12), 0 inside the |yaw| < 0.75 dead zone, smoothed by
                     a centred 3-frame box. Drives the CRT snow / ghost / roll and the tv_static bed gain (SFX).
    TM.sig_c(f)      the client clock: 1 on f540-f719 (viewer title ghost-double), else 0.
    TM.lofi(f, hook) THE MUSIC FILTER AMOUNT m (0 = full range, 1 = TV speaker). Built from sig / sig_c:
                       m = w_shot(f) * sig(f)            w_shot = 1.0 on CRT shots (S1, S3, S5, S13), 0.6 on roof shots
                                                         (S2, S4, S6, S12: we are outdoors, the music is "mid-fi")
                       m = max(m, 0.33) on f330-f377     not yet locked: the clamp macro steps the mark in but the
                                                         music only opens on the lock frame
                       m = 0.45 * sig_c(f) on f504-f791  edit world: the client's mood (4-frame ramps)
                       locks f90, f378, f720: m ramps linearly to 0 over the 4 frames before the lock frame, so the
                       lock frame itself (the picture snapping clean + tv_lock + the music downbeat) is full range
                       hook B: m = 0 on f0-f133, ramps to the roof value by f144 (with the static swell into the splice)
    TM.filter_hz(m)  -> (hp_hz, lp_hz): log interpolation 20 Hz / 20 kHz (m = 0, bypassed) ... 300 Hz / 2.5 kHz (m = 1),
                     4th-order Butterworth magnitudes, + a +2.5 dB x m TV-speaker bump at 1.1 kHz
                     with m also: wow +-8 cents x m (0.536 Hz = 18 cycles per loop), stereo width 1 - 0.75 m (the TV
                     speaker is mono), crackle at m. The edit world adds a chorus on the keys while sig_c = 1
                     (the ghost-double in sound).
    TM.curves(hook)  dict of per-frame arrays (frame, yaw, sig, sig_c, lofi, hp_hz, lp_hz, pocket, music_gain_db)
    `python3 thoda_left_bas_music.py curves` writes them to <RW>/audio/signal_curves_<hook>.json / .csv + a PNG.
    Frame convention: value at frame f is the state of the picture on frame f (time f / 30 s); audio interpolates
    linearly between frame starts.

=====================================================================================================================
THE MUSIC (original, procedural, numpy; licence: original work for @jawad_mp4; no samples of songs, no AI model)
=====================================================================================================================
100 BPM, 4/4, 18 f / beat, 72 f / bar, 15 bars = 1080 f = 36.000 s (VO-LED GRID, VO_TIMING.md: the r1 plan was 14 bars /
1008 f; the measured Vlad VO needs a 2-bar hook, so one bar is inserted at f72 and every r1 frame >= 72 moves +72, except
the clamp ticks, which compress to f342 / f351 with the marks aligning on the bar-5 downbeat f360). Key D minor (bars 0-10,
13-14), F major on the payoff (f828-f935). A 90s-Sunday-TV lo-fi: dholak kaharwa + light tabla, a detuned Casio-style
keyboard riff (2 bars, "thoda left... / thoda right..."), sitar answers, harmonium pads; the edit world (bars 7-10) plays
the SAME riff on clean Rhodes over an 808 + kick / clap / tight hats (same melody = same dialogue); the split (bar 9)
plays both.
    riff A (r1 even bars)  A4 D5 F5- E5 D5 C5-     riff B (r1 odd bars, and the inserted bar 1)  A4 D5 G5- F5 E5 D5-
    chords bars 0-1: Dm Dm · bars 2-10: C Bb Am Dm C Bb Am Dm C · bar 11 C7sus4 pad · payoff F (f828) F | C ·
    bars 13-14 Dm C -> bar 0 Dm
Events: f90 kick + tabla dha (lock A, on V2 "Bas"); f234 tape stop (music halts f234-f251, restarts on a dha f252);
f360 dha (marks align); f378 lock: kick + dha + harmonium swell + sitar run f387; f468-f504 dholak roll into M3; f504
edit world; f720 lock downbeat; f756-f788 clap roll with the export bar; f792 sunset pad; DROP-OUT f810-f827 (music
digital silence); f828 payoff: harmonium F major + dholak dha + F bass + sitar answers (the reverse cymbal / sub / dhol
are SFX, so the song-ready mix B keeps the hit); bars 13-14 riff band-limited under the outro (-4 dB f954-f1068, back to
0 dB by f1079), tails folded onto f0: the f1079 -> f0 seam is continuous. VO pocket: -3 dB bell at 2 kHz (1-4 kHz) on the
music during every MEASURED VO line (<RW>/vo/words.json from thoda_left_bas_vo.py; words joined across gaps < 0.35 s),
4-frame ramps. The VO is approved and recorded (Vlad): the final mixes (thoda_left_bas_sfx.py build) duck this bed 9 dB
under the VO plus the 8 LU per-word floor (LEAD_DECISIONS 1).

Bus: per stem (drums, bass, harmony, lead, fx) -> kick sidechain 4 dB (bass / harmony / lead) -> circular studio room
-> chorus (lead, sig_c) -> wow -> STFT lo-fi mask (m, pocket) -> width -> crackle (fx) -> outro gain -> one gain +
circular true-peak limiter to -16.0 LUFS / <= -3.0 dBTP. The stems sum to the mix.

CLI (run in pipeline/jawad_reels; heavy work through tools/heavy.sh)
    python3 thoda_left_bas_music.py build [--hook A|B|AB]   -> <RW>/audio/music.wav (hook A), music_hookB.wav, stems in
                                                              <RW>/audio/music_stems/<hook>/, music[_hookB].json, curves
    python3 thoda_left_bas_music.py curves                   -> signal_curves_{A,B}.json / .csv / signal_curves.png
    python3 thoda_left_bas_music.py verify [--hook A|B]      -> ebur128, beat grid, filter-vs-curve check at key frames,
                                                              seam, PNG overview (music[_hookB]_overview.png)
<RW> = workspace/jawad_reels/thoda_left_bas.
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SFXDIR = os.path.join(REPO, 'workspace', 'brand_reels', 'sfx')
for _p in (SFXDIR, HERE):                      # HERE ends up first: `audio` / `epic_sfx` are the committed kit
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

import numpy as np  # noqa: E402
from scipy.ndimage import uniform_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as ES  # noqa: E402
import epic_music as EM  # noqa: E402
from audio import SR, undb, db, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'thoda_left_bas'
FPS, BPM, NF = 30, 100.0, 1080                  # VO-led (VO_TIMING.md): 1008 -> 1080 f, one bar more in the hook
DUR = NF / FPS                                  # 36.000 s
BEAT = 60.0 / BPM                               # 0.6 s = 18 frames
BAR = 4 * BEAT                                  # 2.4 s = 72 frames
N = _n(DUR)
SPF = SR // FPS                                 # 1,600 samples per frame
assert N == NF * SPF == 1728000
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
AUD = os.path.join(RW, 'audio')
SCRIPT_JSON = os.path.join(REPO, 'brand_reels', 'design', 'reels', MODULE, 'script.json')
TARGET_LUFS, TP_CEILING = -16.0, -3.0           # music alone (music-supervisor kit); the final mix is epic_mix's
KEY = 'D minor (bars 0-10, 13-14), F major payoff f828-f935'
STEMS = ('drums', 'bass', 'harmony', 'lead', 'fx')
STEM_DB = dict(drums=0.0, bass=0.5, harmony=1.0, lead=-1.0, fx=-2.0)


def F(f):
    """Reel time (s) of frame f."""
    return f / FPS


def T(bar, beat=0.0):
    """Reel time (s) of bar / beat (both from 0)."""
    return (bar * 4 + beat) * BEAT


# ============================================================================================ the signal clock
PRE_YAW = -14.0                                 # pre-roll state (f <= 55, and the loop tail f936-f1079 on f - 1080)
LOOP_TAIL = 936
# (f0, f1, yaw reached at f1, ease); the yaw holds between moves (SHOTS section 0)
YAW_MOVES = (     # 1080-f grid, VO-led (VO_TIMING.md section 3); r1 frame + 72 after the hook unless noted
    (56, 66, 9.0, 'inout_cubic'),               # "right..." lands on the V1 word (f66; r1 f6-f16)
    (82, 90, 0.0, 'out_back'),                  # LOCK f90 on V2 "Bas" (out_back s 0.6: overshoots through 0, settles)
    (130, 136, -18.0, 'in_cubic'),              # slip during "theek hai!" (r1 f60-f66)
    (180, 185, -25.0, 'inout_cubic'),           # wrong way, on V3 "Nahi!"
    (190, 198, -32.0, 'inout_cubic'),           # after the regrip pause f186-f189
    (252, 269, -14.0, 'inout_cubic'),
    (288, 303, 6.0, 'inout_cubic'),             # passes 0 under "thoda aur...", overshoots to +6 = snow at f304
    (315, 330, -4.0, 'inout_cubic'),            # "nahi nahi, wapas!"
    (342, 346, -2.0, 'out_cubic'),              # clamp clicks on the 8ths (S4 from f342)
    (351, 355, -1.0, 'out_cubic'),
    (360, 364, 0.0, 'out_cubic'),               # chalk marks align on the bar-5 downbeat f360
    (418, 430, 11.0, 'in_cubic'),               # gust f414 -> slip
    (486, 503, -40.0, 'in_expo'),               # the swing that carries M3 f504
    (504, 504, -12.0, 'step'),                  # edit world f504-f647: antenna unseen (value unused by the picture)
    (648, 654, -6.0, 'inout_cubic'),            # split S10: moves on f648 / 666 / 684 / 702 (6 f each)
    (666, 672, 4.0, 'inout_cubic'),
    (684, 690, -6.0, 'inout_cubic'),
    (702, 708, -1.0, 'inout_cubic'),
    (792, 792, 0.0, 'step'),                    # sunset: locked
    (900, 905, 2.0, 'out_cubic'),               # the 2-degree nudge by itself (easter egg)
)
# wind wobble a * sin(2 pi hz t): (f0, f1, amp deg, hz); 3-frame raised-cosine ramps inside each window
WOBBLE = ((-10 ** 6, 56, 1.5, 1.3), (136, 179, 1.0, 1.3), (418, 485, 3.0, 0.8))
SIG_FULL_DEG, SIG_DEAD_DEG = 12.0, 0.75
LOCKS = (90, 378, 720)
SIG_C_ON = (540, 720)                           # client clock: sig_c = 1 on f540-f719
EDIT = (504, 792)                               # edit world (S7-S11)
# shots: (f0, f1, name, w_shot for the music filter)
SHOTS = ((0, 144, 'S1 CRT hook', 1.0), (144, 270, 'S2 roof day', 0.6), (270, 342, 'S3 CRT room', 1.0),
         (342, 378, 'S4 clamp macro (roof)', 0.6), (378, 450, 'S5 CRT lock', 1.0), (450, 504, 'S6 roof wind', 0.6),
         (504, 792, 'S7-S11 edit world', None), (792, 936, 'S12 roof sunset', 0.6), (936, 1080, 'S13 CRT loop', 1.0))
FLOOR = ((330, 378, 0.33),)                     # music not yet "locked" (see the docstring)
EDIT_M = 0.45                                   # m in the edit world while sig_c = 1
HOOKB_RAMP = (134, 144)
OUTRO_GAIN = ((954, 960, -4.0), (1068, 1079, 0.0))   # (ramp start, ramp end, dB reached): -4 dB under the card
GAPS = ((234, 252, 'tape stop: music halts for one beat'), (810, 828, 'drop-out: music digital silence'))
WOW_HZ = 18 / DUR                               # 0.5 Hz: a whole number of cycles per loop
WOW_CENTS = 8.0


def _ease(u, kind):
    u = np.clip(u, 0.0, 1.0)
    if kind == 'inout_cubic':
        return np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2)
    if kind == 'in_cubic':
        return u ** 3
    if kind == 'out_cubic':
        return 1 - (1 - u) ** 3
    if kind == 'out_back':
        s = 0.6
        return 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2
    if kind == 'in_expo':
        return np.where(u <= 0, 0.0, (2.0 ** (10 * u - 10) - 2.0 ** -10) / (1 - 2.0 ** -10))
    return (u >= 1).astype(float)               # step


def _yaw_base(f):
    f = np.asarray(f, dtype=np.float64)
    y = np.full(f.shape, PRE_YAW)
    v = PRE_YAW
    for f0, f1, v1, ease in YAW_MOVES:
        if f1 > f0:
            u = (f - f0) / (f1 - f0)
            seg = v + (v1 - v) * _ease(u, ease)
        else:
            seg = np.full(f.shape, v1)
        y = np.where(f >= f0, seg, y)
        v = v1
    return y


def _wobble(f):
    f = np.asarray(f, dtype=np.float64)
    out = np.zeros(f.shape)
    for f0, f1, a, hz in WOBBLE:
        r = 3.0
        up = np.clip((f - f0) / r, 0, 1) if f0 > -1e5 else np.ones(f.shape)
        dn = np.clip((f1 - f) / r, 0, 1)
        w = 0.5 - 0.5 * np.cos(np.pi * np.minimum(up, dn))
        out += np.where((f >= f0) & (f <= f1), w * a * np.sin(2 * np.pi * hz * f / FPS), 0.0)
    return out


def _clock(f):
    """Reel frame -> yaw clock frame (f >= LOOP_TAIL runs on f - NF)."""
    f = np.asarray(f, dtype=np.float64)
    return np.where(f >= LOOP_TAIL, f - NF, f)


def yaw(f):
    """Antenna yaw (deg) at frame f (scalar or array; floats allowed). f >= 936 -> the f - 1080 clock (pre-roll)."""
    g = _clock(f)
    y = _yaw_base(g) + _wobble(g)
    return float(y) if y.ndim == 0 else y


def _sig_raw_g(g):
    a = np.abs(_yaw_base(g) + _wobble(g))
    return np.where(a < SIG_DEAD_DEG, 0.0, np.clip(a / SIG_FULL_DEG, 0.0, 1.0))


def sig(f):
    """Signal loss 0 (locked) .. 1 (no signal) at frame f: clamp(|yaw| / 12), dead zone |yaw| < 0.75, centred 3-frame
    box smoothing on the yaw clock (so the M3 cut at f936 does not smear the sunset into the loop world). The picture
    reads the same function."""
    g = _clock(f)
    s = (_sig_raw_g(g - 1) + _sig_raw_g(g) + _sig_raw_g(g + 1)) / 3.0
    return float(s) if s.ndim == 0 else s


def sig_c(f):
    """Client clock: 1 on SIG_C_ON (f540-f719), else 0."""
    f = np.asarray(f, dtype=np.float64)
    s = ((f >= SIG_C_ON[0]) & (f < SIG_C_ON[1])).astype(float)
    return float(s) if s.ndim == 0 else s


def _shot_w(f):
    w = np.zeros(np.shape(f))
    for f0, f1, _, ws in SHOTS:
        w = np.where((f >= f0) & (f < f1), 0.0 if ws is None else ws, w)
    return w


def lofi(f, hook='A'):
    """Music filter amount m at frame f (0 full range .. 1 TV speaker); see the module docstring for the recipe."""
    f = np.asarray(f, dtype=np.float64)
    fi = np.floor(f)
    m = _shot_w(fi) * sig(fi)
    for f0, f1, fl in FLOOR:
        m = np.where((fi >= f0) & (fi < f1), np.maximum(m, fl), m)
    # edit world: EDIT_M x sig_c with 4-frame ramps (in at f540, the lock at f720 handled below)
    a, b = SIG_C_ON
    ed = EDIT_M * np.clip((fi - a + 1) / 4.0, 0, 1) * (fi < b)
    m = np.where((fi >= EDIT[0]) & (fi < EDIT[1]), ed, m)
    # locks: linear ramp to 0 over the 4 frames before the lock frame
    for L in LOCKS:
        mL = float(lofi_pre(L - 4, hook))
        ramp = mL * np.clip((L - fi) / 4.0, 0, 1)
        m = np.where((fi >= L - 4) & (fi <= L), np.minimum(m, ramp), m)
    if hook == 'B':
        r0, r1 = HOOKB_RAMP
        m_end = float(_shot_w(np.array(r1)) * sig(r1))
        hb = np.where(fi < r0, 0.0, m_end * np.clip((fi - r0 + 1) / (r1 - r0), 0, 1))
        m = np.where(fi < r1, hb, m)
    m = np.clip(m, 0.0, 1.0)
    return float(m) if m.ndim == 0 else m


def lofi_pre(f, hook='A'):
    """m before the lock ramps (used to start each lock ramp from the value the picture had 4 frames earlier)."""
    f = np.asarray(f, dtype=np.float64)
    m = _shot_w(f) * sig(f)
    for f0, f1, fl in FLOOR:
        m = np.where((f >= f0) & (f < f1), np.maximum(m, fl), m)
    if EDIT[0] <= float(f) < EDIT[1]:
        m = EDIT_M * sig_c(f)
    return m


def filter_hz(m):
    """(hp_hz, lp_hz) of the lo-fi mask at amount m (arrays ok)."""
    m = np.asarray(m, dtype=np.float64)
    return 20.0 * (300.0 / 20.0) ** m, 20000.0 * (2500.0 / 20000.0) ** m


def music_gain_db(f):
    """Bus gain automation (dB) at frame f: -4 dB under the outro card, back to 0 by f1079 (loop)."""
    f = np.asarray(f, dtype=np.float64)
    g = np.zeros(f.shape)
    (a0, a1, ga), (b0, b1, gb) = OUTRO_GAIN
    g = np.where(f >= a0, ga * np.clip((f - a0) / (a1 - a0), 0, 1), g)
    g = np.where(f >= b0, ga + (gb - ga) * np.clip((f - b0) / (b1 - b0), 0, 1), g)
    return g


def vo_windows(join=0.35, pad=0.06):
    """VO windows (f0, f1, line) in frames for the 1-4 kHz pocket: the MEASURED VO words (<RW>/vo/words.json, written
    by thoda_left_bas_vo.py), joined across gaps < `join` s and padded by `pad` s. Fallback (no VO yet): the script.json
    estimates, then the r1 values."""
    wp = os.path.join(RW, 'vo', 'words.json')
    if os.path.exists(wp):
        ws = sorted(json.load(open(wp, encoding='utf8')), key=lambda w: w['start'])
        out = []
        for w in ws:
            a, b = w['start'] - pad, w['end'] + pad
            if out and a - out[-1][1] < join:
                out[-1][1] = max(out[-1][1], b)
                out[-1][2] = out[-1][2] if w['line'] in out[-1][2] else out[-1][2] + '+' + w['line']
            else:
                out.append([a, b, w['line']])
        return [(round(max(a, 0.0) * FPS, 2), round(min(b, DUR) * FPS, 2), ln) for a, b, ln in out]
    try:
        d = json.load(open(SCRIPT_JSON))
        return [(int(l['f_in']), int(l['f_out']), l['id']) for l in d['vo']['lines']]
    except Exception:
        return [(3, 34, 'V1'), (38, 62, 'V2'), (74, 132, 'V3'), (163, 190, 'V4'), (200, 248, 'V5'), (254, 300, 'V6'),
                (308, 374, 'V7'), (380, 440, 'V8'), (438, 464, 'V9'), (470, 535, 'V10')]


def pocket(f):
    """VO pocket depth 0..1 at frame f (4-frame ramps at each line's ends)."""
    f = np.asarray(f, dtype=np.float64)
    p = np.zeros(f.shape)
    for a, b, _ in vo_windows():
        w = np.clip((f - (a - 4)) / 4.0, 0, 1) * np.clip(((b + 4) - f) / 4.0, 0, 1)
        p = np.maximum(p, w)
    return p


def curves(hook='A'):
    fr = np.arange(NF)
    m = lofi(fr, hook)
    hpz, lpz = filter_hz(m)
    return dict(frame=fr, yaw=yaw(fr), sig=sig(fr), sig_c=sig_c(fr), lofi=m, hp_hz=hpz, lp_hz=lpz,
                pocket=pocket(fr), music_gain_db=music_gain_db(fr))


def write_curves(out=AUD):
    os.makedirs(out, exist_ok=True)
    paths = []
    for hook in ('A', 'B'):
        c = curves(hook)
        js = {k: [round(float(v), 4) for v in c[k]] for k in c}
        js['frame'] = [int(v) for v in c['frame']]
        meta = dict(module=MODULE, hook=hook, fps=FPS, frames=NF,
                    note='per-frame state; import thoda_left_bas_music (yaw, sig, sig_c, lofi) instead of copying')
        p = os.path.join(out, 'signal_curves_%s.json' % hook)
        json.dump(dict(meta=meta, **js), open(p, 'w'))
        pc = os.path.join(out, 'signal_curves_%s.csv' % hook)
        with open(pc, 'w') as fh:
            keys = list(c)
            fh.write(','.join(keys) + '\n')
            for i in range(NF):
                fh.write(','.join('%d' % c[k][i] if k == 'frame' else '%.4f' % c[k][i] for k in keys) + '\n')
        paths += [p, pc]
    paths.append(curves_png(os.path.join(out, 'signal_curves.png')))
    return paths


def curves_png(path):
    from PIL import Image, ImageDraw
    W, H = 1800, 520
    im = Image.new('RGB', (W, H), (12, 9, 14))
    dr = ImageDraw.Draw(im)
    X = lambda f: int(f / NF * (W - 40)) + 20  # noqa: E731
    cA, cB = curves('A'), curves('B')
    rows = [('yaw (deg, +-45)', cA['yaw'], -45, 45, (255, 200, 120)), ('sig', cA['sig'], 0, 1, (240, 240, 240)),
            ('lofi m hook A', cA['lofi'], 0, 1, (255, 120, 40)), ('lofi m hook B', cB['lofi'], 0, 1, (120, 180, 255)),
            ('VO pocket', cA['pocket'], 0, 1, (160, 220, 140))]
    h = (H - 30) // len(rows)
    for i, (lab, v, lo, hi, col) in enumerate(rows):
        y0 = 20 + i * h
        dr.rectangle([20, y0, W - 20, y0 + h - 8], outline=(50, 44, 60))
        for bar in range(15):
            dr.line([(X(bar * 72), y0), (X(bar * 72), y0 + h - 8)], fill=(45, 40, 55))
        for L in LOCKS:
            dr.line([(X(L), y0), (X(L), y0 + h - 8)], fill=(255, 60, 60))
        Y = lambda q: y0 + h - 10 - int((q - lo) / (hi - lo) * (h - 14))  # noqa: E731
        dr.line([(X(f), Y(q)) for f, q in enumerate(v)], fill=col, width=2)
        dr.text((26, y0 + 2), lab, fill=col)
    for bar in range(14):
        dr.text((X(bar * 72) + 2, H - 12), 'bar %d' % bar, fill=(120, 110, 140))
    im.save(path)
    return path


# ============================================================================================ instruments
_CAL = {}


def _cal(name, fn):
    """Calibration gain (dB) bringing a reference render to REF_LUFS max momentary (EM.CAL convention)."""
    if name not in _CAL:
        x = fn()
        _CAL[name] = A.REF_LUFS - A.momentary_max(A._st(x))
    return _CAL[name]


def _env(n, attack, dur, release, decay=None, sus=1.0):
    t = np.arange(n) / SR
    e = np.clip(t / max(attack, 1e-4), 0, 1)
    if decay:
        e = e * (sus + (1 - sus) * np.exp(-np.maximum(t - attack, 0) / decay))
    u = np.clip((t - dur) / max(release, 1e-4), 0, 1)
    return e * (0.5 + 0.5 * np.cos(np.pi * u))


def casio_raw(f, dur, r, duty=0.25, detune=6.0, vib=9.0):
    """Detuned Casio-style keyboard: two band-limited pulse oscillators (+-6 cents, 25 % duty), delayed 5.5 Hz vibrato,
    fast attack, decay to 55 %, 60 ms release after dur, LP 3.8 kHz. Mono, dur + 0.06 s."""
    n = _n(dur + 0.06)
    t = np.arange(n) / SR
    vb = 1 + (2 ** (vib / 1200) - 1) * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.14) / 0.12, 0, 1)
    x = np.zeros(n)
    for c in (-detune, detune):
        fr = f * 2 ** (c / 1200) * vb
        ph = r.uniform(0, 1)
        x += ES.saw(fr, ph) - ES.saw(fr, (ph + duty) % 1.0)
    x = A.hp(x, 90.0, 2)
    x = A.lp(x, 3800.0, 2) * _env(n, 0.004, dur, 0.06, decay=0.25, sus=0.55)
    return x


def casio(f, dur, r):
    g = _cal('casio', lambda: casio_raw(ES.midi_hz(74), 0.6, A._rng(0, 'cal')))
    return undb(g) * casio_raw(f, dur, r)


def harmonium_raw(notes, dur, r, attack=0.25, release=0.3, cutoff=3200.0):
    """Harmonium chord: two pulse reeds per note at +-2.5 cents (duty 0.3, additive to 4 kHz), bellows attack, release
    INSIDE dur (consecutive chords cross-fade on the bar line), 0.9 Hz pumping, LP 3.2 kHz. Stereo (dur, 2)."""
    n = _n(dur)
    attack, release = min(attack, dur / 3), min(release, dur / 3)
    t = np.arange(n) / SR
    st = np.zeros((n, 2))
    for m in notes:
        fc = ES.midi_hz(m)
        phi = r.uniform(0, 2 * np.pi)
        for side, cents in ((-1, -2.5), (1, 2.5)):
            fq = fc * 2 ** (cents / 1200)
            base = 2 * np.pi * fq * t + phi
            y = np.zeros(n)
            for k in range(1, int(4000.0 / fq) + 1):
                g = min(1.0, (4000.0 - k * fq) / 400.0)
                y += math.sin(math.pi * k * 0.3) / k * g * np.sin(k * base)
            st += A.pan(y, 0.25 * side)
    st /= max(1, len(notes))
    env = np.clip(t / attack, 0, 1) ** 1.3 * (0.5 + 0.5 * np.cos(np.pi * np.clip((t - (dur - release)) / release, 0, 1)))
    env *= 1.0 + 0.05 * np.sin(2 * np.pi * 0.9 * t)
    return A.lp(st * env[:, None], cutoff, 2)


def harmonium(notes, dur, r, attack=0.25, release=0.3):
    g = _cal('harmonium', lambda: harmonium_raw((50, 53, 57), 2.0, A._rng(0, 'cal')))
    return undb(g) * harmonium_raw(notes, dur, r, attack, release)


def dholak(kind, r):
    g = _cal('dholak', lambda: ES._dholak_stroke('dha', A._rng(0, 'cal')))
    return undb(g) * ES._dholak_stroke(kind, r)


def soft_bass(notes, n):
    """Lo-fi round bass for the 90s sections: the 808 voice with little drive, LP 420 Hz."""
    return A.lp(EM.bass808(notes, n, drive=1.15), 420.0, 2)


# ============================================================================================ score
RIFF = {'A': ((0, 69, 1), (1, 74, 1), (2, 77, 2), (4, 76, 1), (5, 74, 1), (6, 72, 2)),     # thoda LEFT...
        'B': ((0, 69, 1), (1, 74, 1), (2, 79, 2), (4, 77, 1), (5, 76, 1), (6, 74, 2))}     # thoda RIGHT...
CHORDS = dict(Dm=(50, 53, 57, 62), C=(48, 52, 55, 60), Bb=(46, 50, 53, 58), Am=(45, 48, 52, 57),
              F=(53, 57, 60, 65), C7sus4=(48, 53, 55, 58))
ROOT = dict(Dm=38, C=36, Bb=34, Am=33, F=41, C7sus4=36)
PROG = ('Dm', 'C', 'Bb', 'Am')
KAHARWA_DHOLAK = (('dha', 0.0), ('ge', -4.0), ('na', -2.0), ('ta', -4.0),
                  ('na', -2.0), ('ke', -5.0), ('dha', -2.5), ('na', -3.0))
TABLA_LIGHT = ((0.0, 'dha', -6.0), (1.0, 'tin', -11.0), (1.5, 'na', -13.0), (2.0, 'na', -8.0), (3.0, 'tin', -11.0),
               (3.5, 'na', -13.0))


def _r1(bar):
    """NEW bar (1080-f grid) -> the r1 bar it replays: bar 1 is the inserted hook bar (replays bar 0's harmony, riff B),
    bars >= 2 are r1 bars 1-13."""
    return bar - 1 if bar >= 1 else 0


def chord_of(bar):
    if bar <= 1:
        return 'Dm'
    ob = bar - 1
    if ob <= 9:
        return PROG[ob % 4]
    return {12: 'Dm', 13: 'C'}.get(ob, 'F')


def part_of(bar):
    """Riff part of NEW bar: the r1 parity (A on even r1 bars), bar 1 = B: ... B(14) -> A(0) keeps the loop seam."""
    return 'B' if bar == 1 else ('A' if (bar - 1 if bar >= 2 else bar) % 2 == 0 else 'B')


class Score:
    """Bar grid -> per-segment raw stems. The music has two hard cuts (GAPS): events whose time falls inside a gap are
    dropped; segment 0 (before f234) is tape-stopped at f234, segment 1 (f252-f809) is gated to silence on f810,
    segment 2 (f828 on) plays out. Buffers run from -PRE to DUR + POST and are folded circularly onto the loop."""
    PRE, POST = 1.0, 6.0

    def __init__(self, hook='A', seed=0):
        self.hook, self.seed = hook, seed
        self.r = A._rng(seed, 'thoda_left_bas_music:%s' % hook)
        self.L = _n(self.PRE + DUR + self.POST)
        self.bounds = [0.0, F(GAPS[0][0]), F(GAPS[0][1]), F(GAPS[1][0]), F(GAPS[1][1])]
        self.seg = [{k: np.zeros((self.L, 2)) for k in STEMS} for _ in range(3)]
        self.kick_key = np.zeros(self.L)
        self.events, self.dropped = [], []

    def segment(self, t):
        for f0, f1, why in GAPS:
            if F(f0) - 1e-9 <= t < F(f1) - 1e-9:
                return None
        if t < F(GAPS[0][0]):
            return 0
        if t < F(GAPS[1][0]):
            return 1
        return 2

    def put(self, stem, x, t, gain_db=0.0, pan=0.0, hit=0.0, what=''):
        k = self.segment(t)
        if k is None:
            self.dropped.append(dict(t=round(t, 4), f=round(t * FPS, 2), stem=stem, what=what))
            return False
        x = np.asarray(x, dtype=np.float64)
        x = A.pan(x, pan) if pan else A._st(x)
        A._add(self.seg[k][stem], x * undb(gain_db), self.PRE + t - hit)
        if what:
            self.events.append(dict(t=round(t, 4), f=round(t * FPS, 2), stem=stem, what=what))
        return True

    def sound(self, stem, name, t, gain_db=0.0, pan=0.0, align='hit', what='', **params):
        s = A.sound(name, **params)
        return self.put(stem, np.asarray(s, dtype=np.float64), t, gain_db, pan, s.hit if align == 'hit' else 0.0, what)

    def kick(self, t, punch=0.5, gain_db=0.0, lp=None, what=''):
        x = EM.kick(self.r, punch)
        if lp:
            x = A.lp(x, lp, 2)
        if self.put('drums', x, t, gain_db, what=what):
            A._add(self.kick_key, x * undb(gain_db), self.PRE + t)

    # ---- phrases
    def riff(self, bar, voice, gain, part=None, octave=0, pan=0.0, beat0=0.0):
        part = part or part_of(bar)
        for slot, m, ln in RIFF[part]:
            t = T(bar, beat0 + slot * 0.5)
            d = ln * 0.5 * BEAT * 0.9
            mm = m + 12 * octave
            acc = 1.0 if slot in (0, 2) else 0.0
            if voice == 'casio':
                x = casio(ES.midi_hz(mm), d, self.r)
            else:
                x = EM.epiano(ES.midi_hz(mm), d + 0.18, self.r, 0.55)
            self.put('lead', x, t, gain + acc, pan, what='riff %s %s' % (part, voice) if slot == 0 else '')

    def pad(self, bar, chord, gain, beats=4.0, beat0=0.0, attack=0.25):
        x = harmonium(CHORDS[chord], beats * BEAT + 0.25, self.r, attack=attack, release=0.3)
        self.put('harmony', x, T(bar, beat0) - 0.12, gain, what='harmonium %s' % chord)

    def kaharwa(self, bar, gain, swing=0.06, skip=()):
        for i, (st, g) in enumerate(KAHARWA_DHOLAK):
            if i in skip:
                continue
            t = T(bar, i * 0.5) + (swing * BEAT if i % 2 else 0.0)
            self.put('drums', dholak(st, self.r) * self.r.uniform(0.9, 1.0), t, gain + g, 0.1 * (-1) ** i)

    def tabla_light(self, bar, gain, accent=None):
        for b, st, g in TABLA_LIGHT:
            if accent is not None and abs(b - accent) < 1e-9:
                continue
            self.sound('drums', 'tabla_hit', T(bar, b), gain + g, 0.12, stroke=st, seed=int(b * 2) % 4)

    def bass(self, bar, chord, gain, soft=True, beats=((0.0, 2.3), (2.5, 1.4)), glide=None):
        for b, ln in beats:
            n = _n(ln * BEAT + 0.1)
            notes = [(0.0, ln * BEAT, ROOT[chord], glide if (glide is not None and b == beats[-1][0]) else None)]
            x = soft_bass(notes, n) if soft else EM.bass808(notes, n, drive=2.2)
            self.put('bass', x, T(bar, b), gain)

    def rhodes_comp(self, bar, chord, gain):
        for b, ln in ((0.0, 1.6), (2.5, 1.2)):
            for k, m in enumerate(CHORDS[chord][1:]):
                self.put('harmony', EM.epiano(ES.midi_hz(m + 12), ln * BEAT, self.r, 0.4), T(bar, b) + 0.006 * k,
                         gain, 0.25 * (-1) ** k)

    def hats(self, bar, gain, step=0.5, open_on=None):
        k = int(round(4 / step))
        for i in range(k):
            b = i * step
            op = open_on is not None and abs(b - open_on) < 1e-9
            self.put('drums', EM.hat(self.r, open=op), T(bar, b), gain + (1.5 if i % 2 else 0.0) - (3 if op else 0),
                     0.25)


def arrange(s):
    """The score (see the module docstring), on the VO-led 1080-f grid: 2-bar hook (lock f90), then the r1 bars + 1.
    s: Score."""
    hook = s.hook
    # ---------------------------------------------------------------- bars 0-1: hook (lock f90 = bar 1 beat 1)
    if hook == 'A':
        for bar in (0, 1):
            s.riff(bar, 'casio', -2.0)
            s.pad(bar, 'Dm', -11.0)
        s.tabla_light(0, -1.0)
        s.tabla_light(1, -1.0, accent=1.0)
        s.kick(F(90), 0.65, -1.0, what='LOCK f90: kick')
        s.sound('drums', 'tabla_hit', F(90), -2.0, 0.0, stroke='dha', seed=1, what='LOCK f90: tabla dha')
    else:                                       # hook B: the modern client world first (clean Rhodes + 808)
        for bar in (0, 1):
            s.riff(bar, 'rhodes', -1.0)
            s.rhodes_comp(bar, 'Dm', -12.0)
            s.bass(bar, 'Dm', -5.0, soft=False, beats=((0.0, 3.8),))
            s.kick(T(bar), 0.5, -4.0, what='hook B downbeat' if bar == 0 else '')
            s.kick(T(bar, 2.5), 0.4, -7.0)
            s.hats(bar, -15.0)
    # ---------------------------------------------------------------- bars 2-3: roof (tape stop f234-f251)
    for bar in (2, 3):
        ch = chord_of(bar)
        s.riff(bar, 'casio', -2.0)
        s.pad(bar, ch, -12.0)
        s.kaharwa(bar, -3.0)
        s.bass(bar, ch, -6.0)
    s.kick(T(2), 0.45, -6.0, lp=1800.0, what='roof downbeat')
    s.kick(F(252), 0.5, -4.0, lp=1800.0, what='music restarts f252 (after the tape stop)')
    s.put('drums', dholak('dha', s.r), F(252), 0.0, what='restart dha f252')
    # ---------------------------------------------------------------- bar 4: CRT room -> clamp macro (f342), builds
    s.riff(4, 'casio', -2.0)
    s.pad(4, chord_of(4), -12.0)
    s.kaharwa(4, -2.5)
    s.bass(4, chord_of(4), -6.0)
    for i in range(4):                          # tabla 16ths from beat 3 (f342, the first clamp click), crescendo
        s.sound('drums', 'tabla_hit', T(4, 3.0 + i * 0.25), -15.0 + 1.5 * i, -0.15, stroke='tin' if i % 2 else 'na',
                seed=i % 4)
    # ---------------------------------------------------------------- bar 5: f360 marks align, f378 LOCK, f414 gust
    s.put('drums', dholak('dha', s.r), F(360), 1.0, what='f360 marks align: dha')
    s.kick(F(360), 0.5, -4.0, lp=2200.0)
    s.kick(F(378), 0.75, 0.0, what='LOCK f378: kick')
    s.put('drums', dholak('dha', s.r), F(378), 1.0, what='LOCK f378: dha')
    s.pad(5, 'Dm', -5.0, beats=3.0, beat0=1.0, attack=0.5)       # the harmonium swell of "the film starts"
    s.riff(5, 'casio', -2.0)
    s.kaharwa(5, -2.0, skip=(0, 2))
    s.bass(5, 'Dm', -5.0, beats=((1.0, 1.4), (2.5, 1.4)))
    for k, m in enumerate((74, 76, 77, 79)):    # sitar run on 16ths from f387, landing A5 on f405
        s.sound('lead', 'sitar_pluck', F(387) + k * BEAT / 4, -7.0, 0.2, align='start', note=m, dur=0.8, seed=k,
                what='sitar run f387' if k == 0 else '')
    s.sound('lead', 'sitar_pluck', F(405), -5.0, 0.2, align='start', note=81, dur=2.0, seed=3, what='sitar A5 f405')
    # ---------------------------------------------------------------- bar 6: band-limited again, roll into M3 f504
    s.riff(6, 'casio', -2.0)
    s.pad(6, chord_of(6), -11.0)
    s.kaharwa(6, -2.5, skip=(6, 7))
    s.bass(6, chord_of(6), -6.0)
    s.sound('drums', 'dholak_roll', F(504), -2.0, 0.0, n=8, bpm=BPM, what='dholak roll f468 -> dha on f504 (M3)')
    # ---------------------------------------------------------------- bars 7-10: the edit world (same riff, Rhodes)
    for bar in (7, 8, 9, 10):
        ch = chord_of(bar)
        s.riff(bar, 'rhodes', -1.0)
        s.rhodes_comp(bar, ch, -12.0)
        s.bass(bar, ch, -3.0, soft=False, beats=((0.0, 3.8),), glide=(ROOT[chord_of(bar + 1)] if bar == 8 else None))
        if bar != 10:
            s.kick(T(bar), 0.6, -1.0, what='edit world bar %d' % bar)
            s.kick(T(bar, 2.5), 0.45, -4.0)
            s.put('drums', EM.clap(s.r), T(bar, 2), -5.0)
            s.hats(bar, -13.0, open_on=3.5 if (bar - 1) % 2 else None)
    s.put('drums', dholak('dha', s.r), F(504), -3.0)
    s.riff(9, 'casio', -9.0, octave=1, pan=-0.2)                  # TAB / AB split: both eras play the dialogue
    s.kaharwa(9, -9.0)
    # bar 10: LOCK f720 downbeat, then the export build f756-f788
    s.kick(F(720), 0.8, 0.0, what='LOCK f720: kick')
    s.put('drums', EM.clap(s.r), F(720), -3.0)
    s.kick(T(10, 2), 0.55, -3.0)
    s.hats(10, -13.0, step=0.25)
    for i, b in enumerate((2.0, 2.5, 3.0, 3.25, 3.5, 3.75)):     # clap roll f756 -> last 16th f787.5
        s.put('drums', A.lp(EM.clap(s.r), 6000.0, 2), T(10, b), -14.0 + 2.0 * i, 0.15 * (-1) ** i,
              what='export roll f756' if i == 0 else '')
    # ---------------------------------------------------------------- bar 11: sunset pad, drop-out, PAYOFF f828
    s.pad(11, 'C7sus4', -7.0, beats=1.0, attack=0.12)            # f792-f809 (gated to silence on f810)
    s.put('harmony', harmonium(CHORDS['F'], 2.2, s.r, attack=0.015, release=0.5), F(828), -1.0,
          what='PAYOFF f828: harmonium F major')
    s.put('drums', dholak('dha', s.r), F(828), 1.0, what='PAYOFF f828: dholak dha')
    s.put('bass', soft_bass([(0.0, 2.0, ROOT['F'], None)], _n(2.2)), F(828), -3.0, what='PAYOFF f828: F bass')
    for k, (b, m) in enumerate(((47.0, 69), (47.5, 72), (48.0, 77))):   # sitar answers A4 C5 F5 (f846, f855, f864)
        s.sound('lead', 'sitar_pluck', b * BEAT, -7.0, 0.25, align='start', note=m, dur=1.6, seed=k)
    # bar 12: the riff returns warm and full range (F | C)
    s.riff(12, 'rhodes', -2.0)
    s.riff(12, 'casio', -9.0)
    s.pad(12, 'F', -10.0, beats=2.0)
    s.pad(12, 'C', -10.0, beats=2.0, beat0=2.0)
    s.kaharwa(12, -6.0)
    s.bass(12, 'F', -6.0, beats=((0.0, 1.8),))
    s.bass(12, 'C', -6.0, beats=((2.0, 1.8),))
    # ---------------------------------------------------------------- bars 13-14: CRT loop under the outro -> bar 0
    for bar in (13, 14):
        s.riff(bar, 'casio', -2.0)
        s.pad(bar, chord_of(bar), -11.0)
        s.tabla_light(bar, -1.0)


def render_stems(hook='A'):
    """-> (stems dict (N, 2) folded onto the loop, kick key (N,), Score)."""
    ES.register()
    s = Score(hook)
    arrange(s)
    P = _n(s.PRE)
    out = {k: np.zeros((s.L, 2)) for k in STEMS}
    t_stop = s.PRE + F(GAPS[0][0])
    t_gate = s.PRE + F(GAPS[1][0])
    tt = (np.arange(s.L) / SR)
    gate = np.clip((t_gate - tt) / 0.03, 0, 1)
    gate = (0.5 - 0.5 * np.cos(np.pi * gate))[:, None]
    for k in STEMS:
        a = ES.tape_stop_fx(s.seg[0][k], t_stop, 0.35)
        a[_n(t_stop + 0.36):] = 0.0
        out[k] = a + s.seg[1][k] * gate + s.seg[2][k]
    kk = s.kick_key.copy()
    kk[_n(t_stop):_n(s.PRE + F(GAPS[0][1]))] = 0
    kk[_n(t_gate):_n(s.PRE + F(GAPS[1][1]))] = 0

    def fold(x):
        y = np.zeros((N,) + x.shape[1:])
        np.add.at(y, (np.arange(len(x)) - P) % N, x)
        return y
    stems = {k: fold(out[k]) * undb(STEM_DB[k]) for k in STEMS}
    return stems, fold(kk), s


# ============================================================================================ bus
def _circ(fn, x, pad):
    p = _n(pad)
    y = fn(np.concatenate([x[-p:], x, x[:p]], axis=0))
    return y[p:p + len(x)]


def _frame_curve(vals, t):
    """Per-frame values -> value at reel times t (s), linear between frame starts, circular over the loop."""
    fr = (np.asarray(t) * FPS) % NF
    ext = np.concatenate([vals, vals[:1]])
    return np.interp(fr, np.arange(NF + 1), ext)


def lofi_stem(x, m_fr, p_fr, nfft=2048, hop=512, pad=1.0):
    """Time-varying lo-fi mask on one stem (circular): wow, STFT magnitude mask (HP / LP / TV bump / VO pocket),
    width. Linear in x."""
    P = _n(pad)
    xp = np.concatenate([x[-P:], x, x[:P]], axis=0)
    L = len(xp)
    ts = (np.arange(L) - P) / SR
    m_s = _frame_curve(m_fr, ts)
    # wow: delay d(t) = m * A * (1 - cos(2 pi f t)) -> pitch deviation +-WOW_CENTS * m
    Aw = (2 ** (WOW_CENTS / 1200) - 1) / (2 * np.pi * WOW_HZ)
    d = m_s * Aw * (1 - np.cos(2 * np.pi * WOW_HZ * ts)) * SR
    idx = np.arange(L) - d
    if np.any(d > 0):
        xp = np.stack([np.interp(idx, np.arange(L), xp[:, c]) for c in range(2)], 1)
    # STFT mask
    f = np.fft.rfftfreq(nfft, 1.0 / SR)
    fs = np.maximum(f, 1.0)
    out = np.zeros_like(xp)
    S0 = [A._stft(xp[:, c], nfft, hop) for c in range(2)]
    Tn = S0[0].shape[0]
    tk = (np.arange(Tn) * hop - P) / SR
    mk = _frame_curve(m_fr, tk)[:, None]
    pk = _frame_curve(p_fr, tk)[:, None]
    hpz, lpz = filter_hz(mk)
    H = 1.0 / np.sqrt(1 + (hpz / fs[None, :]) ** 8) / np.sqrt(1 + (fs[None, :] / lpz) ** 8)
    H *= 1 + (undb(2.5 * mk) - 1) * np.exp(-0.5 * (np.log2(fs[None, :] / 1100.0) / 0.6) ** 2)
    H = 1 + (H - 1) * np.clip(mk / 0.05, 0, 1)
    H *= undb(-3.0 * pk * np.exp(-0.5 * (np.log2(fs[None, :] / 2000.0) / 0.7) ** 2))
    for c in range(2):
        out[:, c] = A._istft(S0[c] * H, L, nfft, hop)
    # width (TV speaker is mono)
    wv = (1 - 0.75 * m_s)[:, None]
    mid, side = (out[:, :1] + out[:, 1:]) / 2, (out[:, :1] - out[:, 1:]) / 2
    out = np.concatenate([mid + side * wv, mid - side * wv], 1)
    return out[P:P + len(x)]


def chorus(x, amount):
    """Ghost-double chorus: x + 0.5 x delayed 11 ms +- 3 ms at 0.8 Hz (whole cycles per loop), scaled by amount (N,)."""
    n = len(x)
    t = np.arange(n) / SR
    hz = round(0.8 * DUR) / DUR
    out = x.copy()
    for c, ph in ((0, 0.0), (1, np.pi / 2)):
        d = (0.011 + 0.003 * np.sin(2 * np.pi * hz * t + ph)) * SR
        idx = (np.arange(n) - d) % n
        y = np.interp(idx, np.arange(n + 1), np.concatenate([x[:, c], x[:1, c]]))
        out[:, c] += 0.5 * amount * y
    return out


def gap_gate():
    """Final gate (N,): exact zeros inside the gaps after every process that could leak into them (room tails, STFT,
    wow): f234 + 0.36 s .. f252 (after the tape stop has halted) and f810 .. f828 (the drop-out; the 30 ms fade-out
    before f810 is already in the score). Opens hard on f252 / f828, where the restart / payoff attacks start."""
    g = np.ones(N)
    g[_n(F(GAPS[0][0]) + 0.36):GAPS[0][1] * SPF] = 0.0
    g[GAPS[1][0] * SPF:GAPS[1][1] * SPF] = 0.0
    return g


def bus(stems, kick_key, hook='A'):
    """Mix chain (module docstring). Returns (mix, stems_out, info)."""
    fr = np.arange(NF)
    m_fr, p_fr = lofi(fr, hook), pocket(fr)
    t = np.arange(N) / SR
    sc = _circ(lambda z: A.sidechain(np.ones(len(z)), z, depth_db=4.0, attack=0.005, release=0.16)[:, 0], kick_key, 1.0)
    st = {}
    for k, v in stems.items():
        v = v * sc[:, None] if k in ('bass', 'harmony', 'lead') else v
        v = A.reverb_circular(v, 'studio', wet_db=-17.0)[:N]
        if k == 'lead':
            v = chorus(v, _frame_curve(sig_c(fr), t))
        st[k] = lofi_stem(v, m_fr, p_fr)
    cr = EM.crackle(N, A._rng(1, 'tlb_crackle'), level=0.05)
    st['fx'] = st['fx'] + cr * _frame_curve(m_fr, t)[:, None]
    g_auto = undb(_frame_curve(music_gain_db(fr), t)) * gap_gate()
    st = {k: v * g_auto[:, None] for k, v in st.items()}
    mix = sum(st.values())
    g = TARGET_LUFS - A.loudness(mix)
    pk = _circ(A.tp_envelope, mix, 0.2)
    ceil = TP_CEILING - 0.3
    for _ in range(16):
        gl = A.limiter_gain(None, ceil, pk=pk * undb(g))
        y = mix * (undb(g) * gl)[:, None]
        L1 = A.loudness(y)
        if abs(L1 - TARGET_LUFS) < 0.02:
            break
        g += TARGET_LUFS - L1
    tp = A.true_peak(np.concatenate([y[-2400:], y, y[:2400]]))
    if tp > TP_CEILING:                          # never expected; guard
        y *= undb(TP_CEILING - 0.05 - tp)
        gl *= undb(TP_CEILING - 0.05 - tp)
    curve = undb(g) * gl
    st = {k: v * curve[:, None] for k, v in st.items()}
    y = sum(st.values())
    info = dict(lufs=round(A.loudness(y), 3), true_peak_dbtp=round(A.true_peak(np.concatenate([y[-2400:], y, y[:2400]])), 3),
                lra=round(A.loudness_range(y), 2), max_momentary_lufs=round(A.momentary_max(y), 2),
                bus_gain_db=round(float(g), 2), limiter_max_gr_db=round(float(-db(gl.min())), 2),
                limiter_pct_over_1db=round(100 * float(np.mean(gl < undb(-1))), 2),
                stem_lufs={k: (round(A.loudness(v), 2) if np.any(v) else None) for k, v in st.items()})
    return y, st, info


# ============================================================================================ build
def _paths(hook):
    sfx = '' if hook == 'A' else '_hookB'
    return dict(wav=os.path.join(AUD, 'music%s.wav' % sfx), json=os.path.join(AUD, 'music%s.json' % sfx),
                stems=os.path.join(AUD, 'music_stems', hook), png=os.path.join(AUD, 'music%s_overview.png' % sfx))


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def build(hook='A'):
    t0 = time.time()
    os.makedirs(AUD, exist_ok=True)
    stems, kk, s = render_stems(hook)
    y, st, info = bus(stems, kk, hook)
    p = _paths(hook)
    A._write_wav(p['wav'], y, 24)
    os.makedirs(p['stems'], exist_ok=True)
    for k, v in st.items():
        A._write_wav(os.path.join(p['stems'], '%s.wav' % k), v, 24)
    bg = EM.beatgrid(y[_n(T(7)):_n(T(11))], BPM)            # the drum-led edit world, bars 7-10
    meta = dict(module=MODULE, hook=hook, file=p['wav'], dur=DUR, frames=NF, samples=N, sr=SR, bits=24, bpm=BPM,
                key=KEY, source='procedural numpy (this file + epic_music / epic_sfx / audio.py instruments); original, '
                'no samples of songs, no AI model', licence='original work for @jawad_mp4',
                gaps=[dict(f0=a, f1=b, why=w) for a, b, w in GAPS], render=info, beatgrid_bars7_10=bg,
                vo_windows=vo_windows(), events=s.events, dropped_in_gaps=s.dropped,
                calibration_db={k: round(v, 2) for k, v in _CAL.items()}, seconds=round(time.time() - t0, 1),
                sha256=_sha(p['wav']))
    json.dump(meta, open(p['json'], 'w'), indent=1)
    print(json.dumps(dict(file=p['wav'], **info, beatgrid=bg, dropped=len(s.dropped), seconds=meta['seconds']),
                     indent=1))
    return meta


# ============================================================================================ verify
def ebur128(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))  # noqa: E731
    return dict(I=g('I'), LRA=g('LRA'), TP=g('Peak'))


def band_edges(x, f0, f1):
    """Measured spectral edges of x over frames [f0, f1): 2 % and 98 % cumulative-energy frequencies + the share of
    energy under 250 Hz."""
    seg = A._st(x)[f0 * SPF:f1 * SPF].mean(1)
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    fq = np.fft.rfftfreq(len(seg), 1 / SR)
    c = np.cumsum(S) / max(S.sum(), 1e-30)
    return dict(f_lo2=round(float(fq[np.searchsorted(c, 0.02)]), 1), f_hi98=round(float(fq[np.searchsorted(c, 0.98)]), 1),
                low250_share=round(float(S[fq < 250].sum() / max(S.sum(), 1e-30)), 4),
                rms_dbfs=round(float(db(np.sqrt(np.mean(seg ** 2)) + 1e-30)), 1))


def verify(hook='A'):
    p = _paths(hook)
    x, sr = A.read_wav(p['wav'])
    assert sr == SR and len(x) == N
    rep = dict(file=p['wav'], ebur128=ebur128(p['wav']), toolkit_lufs=round(A.loudness(x), 2),
               toolkit_tp_circular=round(A.true_peak(np.concatenate([x[-2400:], x, x[:2400]])), 2))
    rep['loudness_ok'] = abs(rep['ebur128']['I'] - TARGET_LUFS) <= 0.3 and rep['ebur128']['TP'] <= TP_CEILING + 0.05
    bg = EM.beatgrid(x[_n(T(7)):_n(T(11))], BPM)
    rep['beatgrid_bars7_10'] = dict(bg, ok=abs(bg['tempo'] - BPM) <= 0.2 and abs(bg['phase_s']) <= 0.015
                                   and bg['strength'] > 2)
    bgr = EM.beatgrid(x[_n(T(2)):_n(F(234))], BPM)
    rep['beatgrid_roof_bars2_3'] = bgr
    m = lofi(np.arange(NF), hook)
    win = [('hook snow', 20, 40), ('lock f90', 91, 101), ('slip f136+', 138, 144), ('roof', 152, 172),
           ('clamp floor', 342, 358), ('lock f378', 379, 392), ('edit clean f504', 512, 537),
           ('edit client f540+', 552, 572), ('lock f720', 722, 742), ('payoff f828', 832, 862),
           ('outro CRT', 972, 1002)]
    rep['filter_check'] = [dict(label=l, frames=[a, b], lofi_mean=round(float(m[a:b].mean()), 3),
                                expected_hp_lp=[round(float(v), 0) for v in filter_hz(float(m[a:b].mean()))],
                                **band_edges(x, a, b)) for l, a, b in win]
    g = []
    for a, b, why in GAPS:
        seg = x[(a + 1) * SPF:(b - 1) * SPF]
        g.append(dict(frames=[a, b], why=why, peak_dbfs=round(float(db(np.abs(seg).max() + 1e-30)), 1)))
    rep['gaps'] = g
    k = _n(0.01)
    rep['seam'] = dict(step=round(float(np.abs(x[0] - x[-1]).max()), 6),
                       median_local_step=round(float(np.median(np.abs(np.diff(np.concatenate([x[-k:], x[:k]]), axis=0)))), 6),
                       rms_last_100ms_db=round(float(db(np.sqrt(np.mean(x[-4800:] ** 2)))), 1),
                       rms_first_100ms_db=round(float(db(np.sqrt(np.mean(x[:4800] ** 2)))), 1))
    rep['png'] = overview(x, p['png'], 'music hook %s  %.1f LUFS  %.1f dBTP' % (hook, rep['ebur128']['I'],
                                                                           rep['ebur128']['TP']), hook)
    json.dump(rep, open(p['json'].replace('.json', '.verify.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


def overview(x, path, title, hook='A', extra=None):
    from PIL import Image, ImageDraw
    w = 1800
    im = A.spectro_image(A.Sfx(np.asarray(x, dtype=np.float32), 0, 'music'), w, 420, None, title, extra or '')
    H = 150
    strip = Image.new('RGB', (w, H), (14, 10, 18))
    dr = ImageDraw.Draw(strip)
    X = lambda t: int(t / DUR * w)  # noqa: E731
    fr = np.arange(NF)
    m = lofi(fr, hook)
    dr.line([(X(F(f)), 10 + int((1 - m[f]) * 50)) for f in fr], fill=(255, 140, 40), width=2)
    dr.text((4, 2), 'lofi m (top = 1)', fill=(255, 140, 40))
    for a, b, _ in GAPS:
        dr.rectangle([X(F(a)), 64, X(F(b)), H], fill=(25, 40, 80))
    for bar in range(16):
        dr.line([(X(T(bar)), 64), (X(T(bar)), H)], fill=(70, 60, 90))
        dr.text((X(T(bar)) + 2, H - 12), str(bar), fill=(120, 110, 140))
    tt, lc = A.loudness_curve(np.asarray(x, dtype=np.float64))
    yv = lambda v: int(np.interp(v, [-60, -6], [H - 14, 66]))  # noqa: E731
    dr.line([(X(a), yv(b)) for a, b in zip(tt, lc)], fill=(240, 240, 240), width=1)
    for L in LOCKS + (828,):
        dr.line([(X(F(L)), 0), (X(F(L)), H)], fill=(255, 60, 60))
    out = Image.new('RGB', (w, 420 + H), (6, 4, 8))
    out.paste(im, (0, 0))
    out.paste(strip, (0, 420))
    out.save(path)
    return path


# ============================================================================================ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for c in ('build', 'verify'):
        q = sub.add_parser(c)
        q.add_argument('--hook', default='AB' if c == 'build' else 'A')
    sub.add_parser('curves')
    a = ap.parse_args(argv)
    if a.cmd == 'curves':
        print('\n'.join(write_curves()))
        return 0
    if a.cmd == 'build':
        write_curves()
        for h in a.hook:
            build(h)
        return 0
    ok = True
    for h in a.hook:
        r = verify(h)
        ok &= r['loudness_ok']
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
