#!/usr/bin/env python3
"""log_kya_kahenge_music.py: ORIGINAL score for Reel 5 · C15 "Log Kya Kahenge" (owner: music-supervisor).

Procedural and deterministic (fixed seeds, numpy/scipy only). Every sound is synthesised in this repo: the shared
instruments of workspace/brand_reels/sfx/epic_music.py (EM.kick, EM.hat, EM.pad_chord, EM.epiano) and two epic_sfx
textures (`dark_drone` seamless bed, `tension_drone`). No sample of any song, no AI model. Licence: original work
made for @jawad_mp4. Plan: brand_reels/design/reels/log_kya_kahenge/BRIEF.md §12; map: MUSIC_log_kya_kahenge.md.

D minor (Sa = D3 146.83 Hz, sub D1 36.71 Hz), 75 BPM (24 frames per beat at 30 fps), 11 bars = 35.2 s =
1,689,600 samples at 48 kHz. Bar n starts at n x 3.2 s; beat k at k x 0.8 s.

    bars 0-4.75 (0-15.2)   A beatless: dark_drone loop (read at loop position t mod 24 s) + tension_drone from 3.2
                             (align start, 12.0 s, root D1) whose crescendo peaks and stops dead on 15.2
    15.2-16.0                DROP-OUT: the whole music bus is gated after the reverb (true silence, 4 ms edges)
    bars 5-7 (16.0-25.6)   B pulse: felt kick (EM.kick punch 0.5, lp 160 Hz) on every beat 16.0 ... 24.8 (downbeats
                             accented), sub D1 + D2 (lp 120 Hz) to 25.2, dark pad (cutoff 700) Dm | Bb | Gm/D, closed
                             hat on the off-8ths 22.8 / 23.6 / 24.4; 25.2-25.6 pad only
    bars 8-10 (25.6-35.2)  C warm, no drums: pad (cutoff 1400) Bbmaj7 (on the clunk) | F/A | Dm(add9); EP motif
                             A4 26.4, F4 28.0, D4 30.4, C4 31.2, A3 32.8, D4 34.4 (-6 dB in the measured VO windows); the
                             tap at 29.6 stays empty; dark_drone fades back in 33.6-35.2 at loop position
                             (t - 35.2) mod 24 s, so the sample after 35.2 is the drone's sample at 0.0 (loop seam)

Bus (EM.render's chain without its end fade, made loop-safe): sidechain to the kick (5 dB, 5 ms / 160 ms), studio
reverb -18 dB by circular convolution (the tail wraps to the start = steady-state loop), drop-out gate, circular
level rider (amount 0.3), loudness -16 LUFS, 4x true-peak limiter at -3.3 dBFS (<= -3.0 dBTP). The stems are put
through the bus's own gain curves, so drums + bass + harmony + lead + fx == music_full.wav.

CLI (run from pipeline/jawad_reels; heavy work through tools/heavy.sh):
    python3 log_kya_kahenge_music.py build  [--out DIR]   -> DIR/music_full.wav (+ lkk_music.wav link), DIR/stems/,
                                                             DIR/music_full.json (map, events, render numbers)
    python3 log_kya_kahenge_music.py verify [--out DIR]   -> DIR/music_full.verify.json + spectrogram PNGs
    python3 log_kya_kahenge_music.py mix [--hook A|B]     -> delegates to log_kya_kahenge_mix.py (the final mix:
                                                             <RW>/audio/final/<name>_mix.wav, _vo_sfx.wav, stems)

EP duck windows (r2, 2026-10-09): measured from the VO stems (vo_windows(): V6 25.97-28.99, V7 31.43-35.08 today);
a note inside a window is -6 dB whole, the C4 at 31.2 that rings into V7 dips from 31.31 to -6 dB at 31.37.
"""
import argparse
import hashlib
import json
import os
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
from scipy.ndimage import uniform_filter1d, maximum_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as E  # noqa: E402
import epic_music as EM  # noqa: E402
from audio import SR, undb, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'log_kya_kahenge'
DUR, BPM, FPS = 35.2, 75.0, 30
BEAT = 60.0 / BPM                               # 0.8 s = 24 frames
BAR = 4 * BEAT                                  # 3.2 s = 96 frames
N = _n(DUR)                                     # 1,689,600 samples
assert N == 1689600
KEY, SEED = 'D', 15
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
OUT = os.path.join(RW, 'music')
TARGET_LUFS, TP_CEILING = -16.0, -3.0           # -16 LUFS (no-VO level; epic_mix re-levels to -18 under VO)
STEMS = ('drums', 'bass', 'harmony', 'lead', 'fx')


def T(bar, beat=0.0):
    """Reel time (s) of bar `bar`, beat `beat` (both from 0)."""
    return (bar * 4 + beat) * BEAT


DROP_OUT = (T(4, 3), T(5))                      # 15.2 -> 16.0 (beat 3 of bar 4 -> bar 5): the reveal's silence
LOOP_LEN = 24.0                                 # dark_drone loop length (s)
DRONE_BACK = (33.6, DUR)                        # dark_drone fades back in (bar 10 beat 2 -> end)
# EP duck windows (r2, 2026-10-09): MEASURED from the VO stems in <RW>/vo/ (vo_windows() below), no longer the BRIEF r2
# targets ((26.0, 28.667), (32.0, 35.133)). Fallback = the HANDOFF r3 measurements, used only when the stems are absent.
VO_DIR = os.path.join(RW, 'vo')
VO_WINDOWS_FALLBACK = ((25.970, 28.990), (31.443, 35.070))
VO_C_FROM = T(8)                                # only the C section's VO lines (V6, V7) carry EP notes
DUCK_PRE, DUCK_RAMP = 0.06, 0.06                # the -6 dB dip is fully down 60 ms before the first voiced sample
                                                # (raised-cosine ramp over the 60 ms before that); it never swells back
                                                # up inside a note (a note that starts in a window stays -6 dB to its end)


def _voiced_runs(x, win=0.02, hop=0.01, rel_db=-45.0, close=0.5):
    """Voiced runs of a VO stem (HANDOFF / vo_chain convention: 20 ms RMS above peak - 45 dB), gaps < close merged."""
    m = A._st(x).mean(1)
    w, h = _n(win), _n(hop)
    c = np.concatenate([[0.0], np.cumsum(m * m)])
    st = np.arange(0, len(m) - w, h)
    lv = 10 * np.log10(np.maximum((c[st + w] - c[st]) / w, 1e-20))
    on = lv > lv.max() + rel_db
    runs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j + 1 < len(on) and on[j + 1]:
                j += 1
            runs.append([st[i] / SR, (st[j] + w) / SR])
            i = j + 1
        else:
            i += 1
    out = []
    for a, b in runs:
        if out and a - out[-1][1] < close:
            out[-1][1] = b
        else:
            out.append([a, b])
    return out


def vo_windows():
    """-> (windows, provenance). The C-section VO lines measured from BOTH hook stems (lkk_vo_A/B.wav, identical from
    8.8 s on): per line, onset = min(first word start, first voiced sample) and end = max(last word end, last voiced
    sample) over A and B. Deterministic; falls back to VO_WINDOWS_FALLBACK when a stem or its words file is missing."""
    import json as _json
    lines, prov = {}, {}
    for h in ('A', 'B'):
        wav = os.path.join(VO_DIR, 'lkk_vo_%s.wav' % h)
        wj = os.path.join(VO_DIR, 'lkk_vo_%s.words.json' % h)
        if not (os.path.exists(wav) and os.path.exists(wj)):
            return VO_WINDOWS_FALLBACK, dict(source='fallback (HANDOFF r3 measured values)', missing=[wav, wj])
        words = [w for w in _json.load(open(wj)) if w['start'] >= VO_C_FROM]
        x = A.read_wav(wav)[0]
        runs = [r for r in _voiced_runs(x) if r[1] > VO_C_FROM]
        for ln in sorted({w['line'] for w in words}):
            ws = [w for w in words if w['line'] == ln]
            a0, b0 = ws[0]['start'], ws[-1]['end']
            rr = [r for r in runs if r[0] < b0 + 0.3 and r[1] > a0 - 0.3]
            a1 = min([a0] + [r[0] for r in rr])
            b1 = max([b0] + [r[1] for r in rr])
            lo, hi = lines.get(ln, (a1, b1))
            lines[ln] = (min(lo, a1), max(hi, b1))
        prov['vo_%s_sha256' % h] = _sha(wav)
    win = tuple((round(a, 3), round(b, 3)) for _, (a, b) in sorted(lines.items(), key=lambda kv: kv[1][0]))
    prov.update(source='measured from %s/lkk_vo_{A,B}.wav + .words.json' % VO_DIR,
                lines={k: [round(a, 3), round(b, 3)] for k, (a, b) in lines.items()})
    return win, prov


_VOW = []


def windows_used():
    """The VO windows of this process (measured once, cached): (windows, provenance)."""
    if not _VOW:
        _VOW.append(vo_windows())
    return _VOW[0]


def ep_duck_plan(t, d, windows=None):
    """Gain plan of one EP note (onset t, length d) against the VO windows: (duck point s or None, mode).
    mode 'free' = 0 dB; 'whole' = the duck for the whole note (it starts inside, or within DUCK_RAMP of, a window's duck
    point); 'from' = 0 dB, then a DUCK_RAMP raised-cosine fall to the duck ending at the duck point, held to the end."""
    windows = windows_used()[0] if windows is None else windows
    for a, b in windows:
        dp = a - DUCK_PRE
        if t < b and t + d > dp - DUCK_RAMP:
            return (round(dp, 3), 'whole') if t >= dp - DUCK_RAMP else (round(dp, 3), 'from')
    return None, 'free'


def ep_gain_curve(t, n, duck_db, windows=None):
    """Per-sample linear gain (n samples) for one EP note at onset t, from ep_duck_plan."""
    dp, mode = ep_duck_plan(t, n / SR, windows)
    if mode == 'free':
        return np.ones(n)
    if mode == 'whole':
        return np.full(n, undb(duck_db))
    u = t + np.arange(n) / SR
    p = np.clip((u - (dp - DUCK_RAMP)) / DUCK_RAMP, 0, 1)
    return undb(duck_db * (0.5 - 0.5 * np.cos(np.pi * p)))

# midi notes (D3 = 50)
PADS = [  # (t0, t1, notes, cutoff, gain key, label): t0/t1 straddle the bar line so chords cross-fade on it
    (T(5) - 0.3, T(6) + 0.3, (50, 53, 57), 700, 'pad_dark', 'Dm (D3 F3 A3)'),           # 15.7 (gated to 16.0)
    (T(6) - 0.3, T(7) + 0.3, (46, 50, 53), 700, 'pad_dark', 'Bb (Bb2 D3 F3)'),
    (T(7) - 0.3, T(8), (50, 55, 58), 700, 'pad_dark', 'Gm/D (D3 G3 Bb3)'),                # releases into 25.6
    (T(8), T(9) + 0.3, (46, 50, 53, 57), 1400, 'pad_warm', 'Bbmaj7 (Bb2 D3 F3 A3)'),      # enters on the clunk
    (T(9) - 0.3, T(10) + 0.3, (45, 48, 53, 57), 1400, 'pad_warm', 'F/A (A2 C3 F3 A3)'),
    (T(10) - 0.3, DUR, (50, 53, 57, 64), 1400, 'pad_warm', 'Dm(add9) (D3 F3 A3 E4)'),     # released by 35.2
]
EP_MOTIF = [(26.4, 69, 1.5), (28.0, 65, 1.5), (30.4, 62, 0.75), (31.2, 60, 1.5), (32.8, 57, 1.5), (34.4, 62, 0.75)]
KICKS = [T(5) + k * BEAT for k in range(12)]    # 16.0 ... 24.8 (beats 20-31)
HATS = [T(7, 0.5), T(7, 1.5), T(7, 2.5)]        # off-8ths 22.8, 23.6, 24.4 (25.2-25.6 pad only)
SUB = (T(5), T(7, 3), 36.708, 73.416)           # D1 + D2, 16.0 -> 25.2

GAINS = dict(          # dB, relative to each instrument's calibrated level (EM.CAL / A.REF_LUFS)
    drone=-3.0,        # dark_drone bed (-20 LUFS loop)
    drone_yield=-8.0,  # the bed recedes over 11.2 -> 15.2 (dB-linear) so its own loop swell (loop pos 12-15 s)
                       # never tops the build; the tension_drone takes over and peaks on 15.2
    tension=11.0,      # tension_drone (max momentary -26 LUFS at 0 dB, peak on 15.2) ...
    tension_ramp=-9.0, # ... plus a crescendo ramp_db = -9 x (1 - p^2), p = 0 at 3.2 -> 1 at 15.2 (steepest at the
                       # end, so the build is still rising when the gate cuts it)
    kick=6.0, kick_off=-2.5,   # felt pulse; beats 2-4 sit 2.5 dB under the downbeat
    hat=-12.0,
    sub=-24.0,         # sub peak ~ -21 dBFS before the bus (felt on headphones, kept off the limiter)
    pad_dark=3.0, pad_warm=1.5,   # C sits ~3 LU under the B pulse after the rider
    ep=3.0, ep_vo=-6.0,   # the motif sits ~3 dB over one pad voice; -6 dB inside the VO windows (BRIEF §12)
)
STEM_DB = dict(drums=0.0, bass=0.0, harmony=0.0, lead=0.0, fx=0.0)
SECTIONS = [  # (name, t0, t1, bars, music)
    ('A hook', 0.0, T(1), '0', 'dark_drone bed (beatless), loop position 0 at frame 0'),
    ('A build', T(1), DROP_OUT[0], '1-4.75', 'dark_drone + tension_drone crescendo 3.2 -> 15.2, stops dead'),
    ('drop-out', DROP_OUT[0], DROP_OUT[1], '4.75-5', 'music bus gated: silence'),
    ('B pulse', T(5), T(8), '5-7', 'felt kick every beat, sub D1+D2, dark pad Dm | Bb | Gm/D, off-8th hats bar 7'),
    ('C warm', T(8), DUR, '8-10', 'warm pad Bbmaj7 | F/A | Dm(add9), EP motif, dark_drone back 33.6 -> loop'),
]


# ============================================================================================ composition
def compose(seed=SEED, ep_duck=True):
    """-> (EM.Song with raw stems in s.st and the sidechain key in s.kick_key, event list)."""
    E.register()
    s = EM.Song(DUR, BPM, KEY, seed)
    r, G = s.r, GAINS
    ev = []

    # ---- A: dark_drone loop under 0-15.2, read at loop position t mod 24 s
    loop = np.asarray(A.sound('dark_drone'), dtype=np.float64)
    L = len(loop)
    assert L == _n(LOOP_LEN)
    i1 = _n(DROP_OUT[0])
    tt = np.arange(i1) / SR
    yield_db = G['drone_yield'] * np.clip((tt - T(3, 2)) / (DROP_OUT[0] - T(3, 2)), 0, 1)     # 11.2 -> 15.2
    s.st['fx'][:i1] += loop[np.arange(i1) % L] * undb(G['drone'] + yield_db)[:, None]
    ev.append(dict(t=0.0, what='dark_drone loop position 0 (bed, beatless)', stem='fx'))
    # ---- tension_drone: align start at 3.2, its designed hit (loudest, last moment) lands on 15.2; cut there
    td = np.asarray(A.sound('tension_drone', duration=12.0, root=36.71), dtype=np.float64)
    hit = A.hit_offset('tension_drone', duration=12.0, root=36.71)
    assert abs(T(1) + hit - DROP_OUT[0]) < 1e-9, hit
    td = td[:_n(hit)]
    ramp = G['tension_ramp'] * (1 - (np.arange(len(td)) / (len(td) - 1)) ** 2)                # -9 -> 0 dB
    s.put('fx', td * undb(ramp)[:, None], T(1), G['tension'])
    ev.append(dict(t=T(1), what='tension_drone starts (12.0 s crescendo, root D1)', stem='fx'))
    ev.append(dict(t=T(3, 2), what='dark_drone starts to yield (-8 dB by 15.2) to the tension_drone', stem='fx'))
    ev.append(dict(t=DROP_OUT[0], what='drones stop dead; drop-out begins', stem='all'))

    # ---- B: felt pulse on every beat, downbeats accented
    for k, t in enumerate(KICKS):
        kk = EM.kick(r, 0.5)
        g = G['kick'] + (0.0 if k % 4 == 0 else G['kick_off'])
        s.put('drums', A.lp(kk, 160.0, 2), t, g)
        A._add(s.kick_key, kk * undb(g), t)
        ev.append(dict(t=t, what='kick (felt pulse)%s' % (', downbeat' if k % 4 == 0 else ''), stem='drums'))
    for t in HATS:
        s.put('drums', EM.hat(r), t, G['hat'], 0.25)
        ev.append(dict(t=t, what='closed hat (off-8th)', stem='drums'))
    # sub D1 + D2, sustained 16.0 -> 25.2 (12 ms attack, 200 ms raised-cosine release), lp 120 Hz
    t0, t1, f1, f2 = SUB
    u = np.arange(_n(t1 - t0)) / SR
    env = np.clip(u / 0.012, 0, 1)
    rel = _n(0.2)
    env[-rel:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(1, rel + 1) / rel)
    sub = (np.sin(2 * np.pi * f1 * u) + 0.6 * np.sin(2 * np.pi * f2 * u)) * env
    s.put('bass', A.lp(sub, 120.0, 2), t0, G['sub'])
    ev.append(dict(t=t0, what='sub D1 + D2 enters (to 25.2)', stem='bass'))

    # ---- pads (B dark, C warm)
    for a, b, notes, fc, gk, label in PADS:
        s.put('harmony', EM.pad_chord(list(notes), b - a, r, fc), a, G[gk])
        ev.append(dict(t=max(a, T(5)), what='pad %s, cutoff %d Hz, %.2f-%.2f s' % (label, fc, a, b), stem='harmony'))

    # ---- C: EP motif (bright 0.6, lp 2200 Hz), -6 dB under the MEASURED VO windows (ep_duck_plan / ep_gain_curve):
    # a note that starts inside a window is -6 dB whole; one that rings into a window (C4 31.2 under V7) dips from
    # 60 ms before the first voiced sample and stays down to its end
    for t, m, d in EP_MOTIF:
        x = A.lp(EM.epiano(E.midi_hz(m), d, r, 0.6), 2200.0, 2)
        dp, mode = ep_duck_plan(t, d)
        if ep_duck and mode != 'free':
            x = np.asarray(x, dtype=np.float64)
            gc = ep_gain_curve(t, len(x), G['ep_vo'])
            x = x * (gc if x.ndim == 1 else gc[:, None])
        s.put('lead', x, t, G['ep'], 0.1)
        how = {'free': '', 'whole': ', under VO %+g dB (whole note)' % G['ep_vo'],
               'from': ', under VO %+g dB from %.3f s (ramp %.0f ms)' % (G['ep_vo'], dp or 0, DUCK_RAMP * 1000)}[mode]
        ev.append(dict(t=t, what='EP %s (%.2f s)%s' % (_name(m), d, how if ep_duck else ''), stem='lead',
                       duck_mode=mode if ep_duck else 'off', duck_point=dp))

    # ---- dark_drone back in 33.6 -> 35.2 at loop position (t - 35.2) mod 24 (seamless into frame 0)
    j0 = _n(DRONE_BACK[0])
    idx = np.arange(j0, N)
    w = (idx - j0 + 1) / (N - j0)                                  # last sample -> 1 (full level, as at t = 0)
    w = 0.5 - 0.5 * np.cos(np.pi * w)
    s.st['fx'][j0:] += loop[(idx - N) % L] * (undb(G['drone']) * w)[:, None]
    ev.append(dict(t=DRONE_BACK[0], what='dark_drone fades back in (loop phase of frame 0)', stem='fx'))
    for e in ev:
        e['f'] = round(e['t'] * FPS, 2)
        e['bar_beat'] = '%d.%g' % (int(e['t'] // BAR), round((e['t'] % BAR) / BEAT, 3))
    ev.sort(key=lambda e: e['t'])
    return s, ev


def _name(m):
    return ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'][m % 12] + str(m // 12 - 1)


# ============================================================================================ bus
def gate_curve():
    """1 outside the drop-out, 0 inside [15.2, 16.0 - 4 ms]; 4 ms raised-cosine edges (out ends at 15.2,
    in ends at 16.0 so the first pulse lands at full level)."""
    g = np.ones(N)
    a, b, f = _n(DROP_OUT[0]), _n(DROP_OUT[1]), _n(0.004)
    g[a - f:a] = 0.5 + 0.5 * np.cos(np.pi * np.arange(1, f + 1) / f)
    g[a:b - f] = 0.0
    g[b - f:b] = 0.5 - 0.5 * np.cos(np.pi * np.arange(1, f + 1) / f)
    return g


def rider_gain(x, valid, amount=0.3, win=1.5, max_db=9.0):
    """EM.level_rider made loop-safe: windows wrap around the loop seam, and the gated drop-out is left out of
    the level estimate (it is not 'quiet music'). Returns a linear gain curve."""
    p = np.square(A.kweight(A._st(x))).mean(1)
    w = valid.astype(np.float64)
    num = uniform_filter1d(p * w, _n(win), mode='wrap')
    den = uniform_filter1d(w, _n(win), mode='wrap')
    lv = 10 * np.log10(np.maximum(num / np.maximum(den, 1e-9), 1e-12))
    act = (lv > lv.max() - 40) & valid
    med = np.median(lv[act])
    g = np.clip(-amount * (lv - med), -max_db, max_db) * act
    g = uniform_filter1d(g, _n(1.0), mode='wrap')
    return undb(g)


def bus(s):
    """Raw stems -> (mix, stems, info). Every stage is a gain curve or a linear filter applied per stem."""
    st = {k: np.array(s.st[k]) * undb(STEM_DB[k]) for k in STEMS}
    sc = A.sidechain(np.ones((N, 2)), s.kick_key, depth_db=5.0, attack=0.005, release=0.16)[:, 0]
    for k in ('bass', 'harmony', 'lead', 'fx'):
        st[k] *= sc[:, None]
    for k in STEMS:                                              # circular: the tail wraps onto the start
        st[k] = A.reverb_circular(st[k], 'studio', wet_db=-18.0)
    gate = gate_curve()
    for k in STEMS:
        st[k] *= gate[:, None]
    pre = sum(st.values())
    ride = rider_gain(pre, gate > 0.999)
    pre = pre * ride[:, None]
    g = TARGET_LUFS - A.loudness(pre)
    for _ in range(12):
        gl = A.limiter_gain(pre * undb(g), TP_CEILING - 0.3)
        y = pre * undb(g) * gl[:, None]
        L = A.loudness(y)
        if abs(L - TARGET_LUFS) < 0.03:
            break
        g += TARGET_LUFS - L
    curve = ride * undb(g) * gl
    stems = {k: v * curve[:, None] for k, v in st.items()}
    mix = sum(stems.values())
    info = dict(lufs=round(A.loudness(mix), 3), true_peak_dbtp=round(A.true_peak(mix), 3),
                lra=round(A.loudness_range(mix), 2), master_gain_db=round(float(g), 2),
                limiter_max_gr_db=round(float(-A.db(gl.min())), 3),
                limiter_gr_over_0p5db_s=round(float(np.sum(gl < undb(-0.5)) / SR), 4),
                rider_db_range=[round(float(A.db(ride.min())), 2), round(float(A.db(ride.max())), 2)],
                sidechain_max_db=round(float(A.db(sc.min())), 2))
    return mix, stems, info


# ============================================================================================ build
def build(out=OUT, seed=SEED):
    s, ev = compose(seed)
    mix, stems, info = bus(s)
    assert mix.shape == (N, 2)
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    full = os.path.join(out, 'music_full.wav')
    A._write_wav(full, mix, 24)
    paths = {}
    for k in STEMS:
        paths[k] = os.path.join(out, 'stems', 'music_stem_%s.wav' % k)
        A._write_wav(paths[k], stems[k], 24)
    link = os.path.join(out, 'lkk_music.wav')                      # the name BRIEF §12 uses
    if os.path.islink(link) or os.path.exists(link):
        os.remove(link)
    os.symlink('music_full.wav', link)
    meta = dict(module=MODULE, file=full, stems=paths, brief_alias=link, dur=DUR, samples=N, sr=SR, bits=24,
                bpm=BPM, beat_s=BEAT, bar_s=BAR, frames_per_beat=round(BEAT * FPS, 6),
                key='D minor (Sa = D3 146.83 Hz)',
                seed=seed, source='procedural numpy score (original; epic_music instruments + epic_sfx drones)',
                licence='original work for @jawad_mp4; no samples of songs, no AI generation',
                drop_out=list(DROP_OUT), loop_seam='35.2 -> 0.0: dark_drone at loop position 0, pads released',
                gains_db=GAINS, sections=[dict(name=a, t0=b, t1=c, bars=d, music=e) for a, b, c, d, e in SECTIONS],
                vo_windows=dict(windows=windows_used()[0], provenance=windows_used()[1], duck_pre_s=DUCK_PRE,
                                duck_ramp_s=DUCK_RAMP, ep_duck_db=GAINS['ep_vo'],
                                ep_plan=[dict(t=t, note=_name(m), d=d, mode=ep_duck_plan(t, d)[1],
                                              duck_point=ep_duck_plan(t, d)[0]) for t, m, d in EP_MOTIF]),
                events=ev, render=info, sha256=_sha(full),
                deps_sha256={os.path.basename(m.__file__): _sha(m.__file__) for m in (A, EM, E)})
    json.dump(meta, open(os.path.join(out, 'music_full.json'), 'w'), indent=1)
    print(json.dumps(dict(file=full, **info, sha256=meta['sha256'], vo_windows=meta['vo_windows']['windows'],
                          ep_plan=meta['vo_windows']['ep_plan']), indent=1))
    return meta


def _rms_(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ============================================================================================ verify
def _ffprobe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,'
                        'bits_per_sample,duration_ts,duration', '-of', 'json', p], capture_output=True, text=True)
    return json.loads(r.stdout)['streams'][0]


def _ebur128(p):
    import re
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    s = r[r.rfind('Summary'):]
    get = lambda k: float(re.search(k + r':\s+(-?[\d.]+)', s).group(1))
    return dict(I_lufs=get('I'), LRA_lu=get('LRA'), true_peak_dbfs=get('Peak'), threshold=get('Threshold'))


def onsets(x, hop=120, nfft=1024, band=None, k=1.5, min_gap=0.08):
    """Blind onset detector: log-magnitude spectral flux (2.5 ms hop), adaptive threshold (moving median + k x MAD
    over 1 s), local maxima >= min_gap apart. Returns (times, strengths). The STFT pads the file edges with zeros,
    so the first and last ~25 ms always show a splatter 'onset' (an analysis artefact; the seam test below runs on
    the looped signal instead)."""
    from scipy.ndimage import median_filter
    m = A._st(x).mean(1)
    f, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop, boundary='zeros', padded=True)
    M = np.log1p(np.abs(Z) * 1000.0)
    if band:
        M = M[(f >= band[0]) & (f <= band[1])]
    fl = np.concatenate([[0.0], np.maximum(np.diff(M, axis=1), 0).sum(0)])
    w = int(1.0 * SR / hop)
    med = median_filter(fl, w, mode='nearest')
    mad = median_filter(np.abs(fl - med), w, mode='nearest')
    thr = med + k * np.maximum(mad, 1e-9) + 0.02 * fl.max()
    g = int(min_gap * SR / hop)
    i = np.nonzero((fl == maximum_filter1d(fl, 2 * g + 1)) & (fl > thr))[0]
    return tt[i] - hop / SR / 2, fl[i]


def env_onset(x, t_exp, band, pre=0.12, post=0.12, frac=0.5):
    """Attack time of one event in a mix: the band-passed amplitude envelope (1 ms smoothing) first rises above
    base + frac x (peak - base), where base = the 20th percentile of the envelope over [t - pre, t - 30 ms] (the
    sustained bed under the event) and peak = its max over [t - pre, t + post]. Returns (t_onset, rise_db)."""
    a, b = _n(max(t_exp - pre, 0)), min(len(x), _n(t_exp + post))
    y = A._st(x).mean(1)
    lo, hi = max(a - _n(0.25), 0), min(len(y), b + _n(0.25))       # filter + Hilbert on a padded span, then slice
    full = A.bp(y[lo:hi], band[0], band[1], 2) * signal.windows.tukey(hi - lo, 0.2)
    e = uniform_filter1d(np.abs(signal.hilbert(full)), _n(0.001))[a - lo:b - lo]
    base = np.percentile(e[:max(1, _n(pre - 0.03))], 20)
    pk = e.max()
    i = int(np.argmax(e > base + frac * (pk - base)))
    return (a + i) / SR, float(A.db(pk / max(base, 1e-12)))


def note_onset(x, t_exp, f0, win=0.08, hop=120):
    """Onset of one pitched note inside a mix: log-magnitude flux summed over the bins of its first 3 harmonics
    (+-1 bin, 2048-point STFT, 2.5 ms hop); the time of the largest flux peak within +-win of t_exp. A long window
    sees the attack early, so compare against the same measurement on the isolated stem (constant bias)."""
    a, b = _n(max(t_exp - 0.3, 0)), min(len(x), _n(t_exp + 0.3))
    m = A._st(x).mean(1)[a:b]
    f, tt, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - hop)
    df = f[1] - f[0]
    sel = np.zeros(len(f), bool)
    for h in (1, 2, 3):
        k = int(round(h * f0 / df))
        sel[max(k - 1, 0):k + 2] = True
    M = np.log1p(np.abs(Z[sel]) * 1000.0)
    fl = np.concatenate([[0.0], np.maximum(np.diff(M, axis=1), 0).sum(0)])
    tt = tt + a / SR
    i = np.nonzero(np.abs(tt - t_exp) <= win)[0]
    return float(tt[i[np.argmax(fl[i])]])


def grid_fit(x, bpm, band=None, span=0.01, step=0.0005, t0=0.0):
    """The music-supervisor's spectral-flux grid fit (EM.beatgrid) with an optional band and a finer tempo step:
    tempo (BPM), beat phase (s, folded to +-half a beat, relative to t0) and on-grid strength (> 2 = on a grid)."""
    m = A._st(x).mean(1)
    f, tt, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - 240)
    M = np.log1p(np.abs(Z) * 100)
    if band:
        M = M[(f >= band[0]) & (f <= band[1])]
    fl = np.maximum(np.diff(M, axis=1), 0).sum(0)
    hop = 240 / SR

    def sc(b, off):
        i = np.round((off + np.arange(0, tt[-1] - off, 60 / b)) / hop).astype(int)
        return fl[i[i < len(fl)]].mean()
    best = max((sc(b, o), b, o) for b in bpm * np.arange(1 - span, 1 + span + 1e-9, step)
               for o in np.arange(0, 60 / b, 0.0025))
    s_, b, off = best
    off = (off + 30 / b) % (60 / b) - 30 / b
    return dict(tempo=round(float(b), 3), phase_ms=round(float(off) * 1000, 1),
                strength=round(float(s_ / fl.mean()), 2),
                band=band or 'full', rel_to_s=t0)


PC = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
CHORDS = [  # (bar, label, expected pitch classes)
    (0, 'drone (D1 D2 A2 D3 + faint F3 Eb3)', {'D', 'A'}), (2, 'drone + tension_drone', {'D', 'A'}),
    (5, 'Dm', {'D', 'F', 'A'}), (6, 'Bb', {'Bb', 'D', 'F'}), (7, 'Gm/D', {'D', 'G', 'Bb'}),
    (8, 'Bbmaj7', {'Bb', 'D', 'F', 'A'}), (9, 'F/A', {'A', 'C', 'F'}), (10, 'Dm(add9)', {'D', 'F', 'A', 'E'})]


def chroma_bar(x, bar, lo=100.0, hi=400.0):
    """Pitch-class energy over the middle of a bar ([bar + 1 beat, bar + 3 beats]) from fundamentals in lo-hi Hz.
    Returns (classes sorted by energy, normalised energies)."""
    m = A._st(x).mean(1)[_n(T(bar, 1)):_n(T(bar, 3))]
    f, _, Z = signal.stft(m, SR, nperseg=16384, noverlap=16384 - 2048)
    P = (np.abs(Z) ** 2).mean(1)
    sel = (f >= lo) & (f <= hi)
    midi = 69 + 12 * np.log2(f[sel] / 440.0)
    c = np.zeros(12)
    np.add.at(c, np.round(midi).astype(int) % 12, P[sel])
    o = np.argsort(c)[::-1]
    return [PC[i] for i in o], c[o] / c.max()


def verify(out=OUT):
    full = os.path.join(out, 'music_full.wav')
    x, sr = A.read_wav(full)
    rep = dict(file=full, sha256=_sha(full))
    rep['format'] = _ffprobe(full)
    rep['format_ok'] = bool(sr == SR and x.shape == (N, 2) and rep['format']['codec_name'] == 'pcm_s24le'
                            and int(rep['format']['duration_ts']) == N)
    rep['ebur128_ffmpeg'] = _ebur128(full)
    rep['bs1770_numpy'] = dict(I_lufs=round(A.loudness(x), 3), true_peak_dbtp=round(A.true_peak(x), 3),
                               lra=round(A.loudness_range(x), 2), max_momentary=round(A.momentary_max(x), 2))
    st = {k: A.read_wav(os.path.join(out, 'stems', 'music_stem_%s.wav' % k))[0] for k in STEMS}
    rep['stems_format_ok'] = all(v.shape == x.shape for v in st.values())
    rep['stems_sum_residual_dbfs'] = round(float(A.db(np.abs(sum(st.values()) - x).max() + 1e-15)), 1)
    rep['stems_lufs'] = {k: (round(A.loudness(v), 2) if np.any(v) else None) for k, v in st.items()}

    # ---- tempo and beat phase (spectral-flux grid fits)
    xb = x[_n(T(5)):_n(T(8))]
    rep['grid_fit'] = {
        'B 16.0-25.6, full band (beatgrid as in the agent spec)': EM.beatgrid(xb, BPM),
        'B 16.0-25.6, 20-250 Hz (the felt kick)': grid_fit(xb, BPM, (20, 250), t0=T(5)),
        'B bars 5-6 16.0-22.4, full band (before the hats)': grid_fit(x[_n(T(5)):_n(T(7))], BPM, t0=T(5)),
        'B bar 7 22.4-25.6, 6-16 kHz (hats: expect +-400 ms = off-8ths)': grid_fit(x[_n(T(7)):_n(T(8))], BPM,
                                                                                    (6000, 16000), t0=T(7)),
        'whole file, full band (A is beatless by design)': grid_fit(x, BPM)}
    ref = np.zeros((_n(T(3)), 2))
    for k in range(12):
        A._add(ref, A._st(A.lp(EM.kick(np.random.default_rng(k), 0.5), 160.0, 2)), k * BEAT)
    rep['grid_fit']['method bias: reference kicks placed exactly on the grid, 20-250 Hz'] = grid_fit(
        ref, BPM, (20, 250))
    rep['kick_envelope_method_bias_ms'] = [round((env_onset(ref, k * BEAT, (25, 200))[0] - k * BEAT) * 1000, 1)
                                           for k in range(1, 4)]
    # ---- event onsets in the MIX (bed-relative envelope rise) and in the stems (clean reference)
    def table(sig, times, band, pre=0.12, post=0.12):
        r = [env_onset(sig, t, band, pre, post) for t in times]
        return [round((a - t) * 1000, 1) for (a, _), t in zip(r, times)], [round(v, 1) for _, v in r]
    kerr, krise = table(x, KICKS, (25, 200))
    kerr_s, _ = table(st['drums'], KICKS, (25, 200))
    kt = np.array(KICKS) + np.array(kerr) / 1000
    beats = np.round(np.array(KICKS) / BEAT)
    slope, icpt = np.polyfit(beats, kt, 1)
    kpk = [float(A.db(np.abs(st['drums'][_n(t):_n(t + 0.1)]).max())) for t in KICKS]
    rep['kicks'] = dict(expected_s=KICKS, mix_error_ms=kerr, mix_rise_db=krise, stem_error_ms=kerr_s,
                        fit_bpm=round(60.0 / slope, 4), fit_phase_ms=round(icpt * 1000, 2),
                        fit_residual_ms_max=round(float(np.abs(kt - (slope * beats + icpt)).max() * 1000), 2),
                        stem_peak_dbfs=[round(v, 1) for v in kpk],
                        downbeat_is_loudest_kick_of_its_bar=[bool(kpk[i] > max(kpk[i + 1:i + 4])) for i in (0, 4, 8)])
    herr, hrise = table(x, HATS, (6000, 16000))
    rep['hats'] = dict(expected_s=HATS, mix_error_ms=herr, mix_rise_db=hrise)
    et = [t for t, _, _ in EP_MOTIF]
    eerr_s, erise_s = table(st['lead'], et, (250, 2200), pre=0.1, post=0.1)
    nm_ = [note_onset(x, t, E.midi_hz(m)) for t, m, _ in EP_MOTIF]        # the pad's beating envelope masks a
    ns_ = [note_onset(st['lead'], t, E.midi_hz(m)) for t, m, _ in EP_MOTIF]  # band envelope, so the mix check is
    rep['ep_notes'] = dict(expected_s=et, notes=[_name(m) for _, m, _ in EP_MOTIF],   # harmonic-bin flux vs stem
                           mix_note_flux_onset_ms=[round((a - t) * 1000, 1) for a, t in zip(nm_, et)],
                           stem_note_flux_onset_ms=[round((a - t) * 1000, 1) for a, t in zip(ns_, et)],
                           mix_minus_stem_ms=[round((a - b) * 1000, 1) for a, b in zip(nm_, ns_)],
                           stem_envelope_onset_ms=eerr_s, stem_rise_db=erise_s)
    # ---- blind onsets over the whole file vs the 8th-note grid (edges excluded, see onsets())
    ot, os_ = onsets(x)
    keep = (ot > 0.025) & (ot < DUR - 0.025)
    ot, os_ = ot[keep], os_[keep]
    strong = os_ >= 0.15 * os_.max()
    dev8 = (ot + 0.2) % 0.4 - 0.2
    rep['blind_onsets'] = dict(
        n=int(len(ot)), n_strong=int(strong.sum()),
        strong=[dict(t=round(float(t), 3), bar_beat='%d.%g' % (int(t // BAR), round((t % BAR) / BEAT, 2)),
                     dev_from_8th_ms=round(float(d) * 1000, 1), strength=round(float(s_), 1))
                for t, d, s_ in zip(ot[strong], dev8[strong], os_[strong])],
        strong_in_metered_part_off_8th_gt_15ms=int(np.sum((np.abs(dev8) > 0.015) & strong & (ot >= T(5) - 0.01))))
    # ---- harmony: pitch classes per bar
    ch = []
    for bar, label, exp in CHORDS:
        src = st['fx'] if bar < 5 else st['harmony']                 # the chord layer alone
        order, en = chroma_bar(src, bar)
        morder, men = chroma_bar(x, bar)
        ch.append(dict(bar=bar, t='%.1f-%.1f' % (T(bar, 1), T(bar, 3)), chord=label, expected=sorted(exp),
                       stem='fx' if bar < 5 else 'harmony', top=order[:len(exp) + 2],
                       top_energy=[round(float(v), 2) for v in en[:len(exp) + 2]], match=set(order[:len(exp)]) == exp,
                       mix_top=morder[:len(exp) + 1], mix_top_energy=[round(float(v), 2) for v in men[:len(exp) + 1]]))
    rep['harmony'] = ch
    # ---- EP dips under the MEASURED VO windows: the lead stem with the dips vs the same score composed without them
    # (raw stems, before the bus), plus the bussed lead stem's level step across the C4's duck point
    wins, prov = windows_used()
    s_d, _ = compose(ep_duck=True)
    s_0, _ = compose(ep_duck=False)
    ld, l0 = A._st(s_d.st['lead']), A._st(s_0.st['lead'])
    seg_db = lambda a, b: round(float(A.db(_rms_(ld[_n(a):_n(b)]) / max(_rms_(l0[_n(a):_n(b)]), 1e-15))), 2)
    notes = []
    for t, m, d in EP_MOTIF:
        dp, mode = ep_duck_plan(t, d)
        o = dict(t=t, note=_name(m), d=d, mode=mode, duck_point=dp, head_db=seg_db(t + 0.01, t + 0.11))
        if mode == 'from':
            o['before_ramp_db'] = seg_db(dp - DUCK_RAMP - 0.1, dp - DUCK_RAMP)
            o['after_duck_point_db'] = seg_db(dp, min(t + d, dp + 0.3))
        notes.append(o)
    lead_file = st['lead']
    c4 = [(t, d) for t, m, d in EP_MOTIF if ep_duck_plan(t, d)[1] == 'from']
    bussed = []
    for t, d in c4:
        dp = ep_duck_plan(t, d)[0]
        pre, post = (dp - DUCK_RAMP - 0.08, dp - DUCK_RAMP), (dp + 0.02, dp + 0.10)
        r = lambda x, ab: _rms_(x[_n(ab[0]):_n(ab[1])])
        bussed.append(dict(t=t, step_db_file=round(float(A.db(r(lead_file, post) / r(lead_file, pre))), 2),
                           natural_decay_db_raw_undipped=round(float(A.db(r(l0, post) / r(l0, pre))), 2)))
    rep['ep_duck'] = dict(windows=wins, provenance=prov, duck_db=GAINS['ep_vo'], pre_s=DUCK_PRE, ramp_s=DUCK_RAMP,
                          notes_raw=notes, bussed_lead_step=bussed)
    # ---- drop-out, sections, loudness curve
    a, b = _n(DROP_OUT[0]), _n(DROP_OUT[1] - 0.004)
    rep['drop_out'] = dict(window_s=[DROP_OUT[0], DROP_OUT[1] - 0.004],
                           max_abs_dbfs=round(float(A.db(np.abs(x[a:b]).max() + 1e-15)), 1),
                           last_200ms_before_rms_dbfs=round(float(A.db(np.sqrt(np.mean(x[a - _n(0.2):a] ** 2)))), 1),
                           first_200ms_after_rms_dbfs=round(float(A.db(np.sqrt(np.mean(
                               x[_n(16.0):_n(16.2)] ** 2)))), 1))
    secs = []
    for nm, t0, t1, bars, _ in SECTIONS:
        if nm != 'drop-out':
            y = x[_n(t0):_n(t1)]
            secs.append(dict(section=nm, t=[t0, round(t1, 3)], lufs=round(A.loudness(y), 2),
                             max_momentary=round(A.momentary_max(y), 2)))
    rep['sections'] = secs
    tm, lm = A.loudness_curve(x)
    rep['momentary_lufs_every_0p8s'] = {('%.1f' % t): round(float(np.interp(t, tm, lm)), 1)
                                        for t in np.arange(0.4, DUR, 0.8)}
    rep['max_momentary_at_s'] = round(float(tm[np.argmax(lm)]), 2)
    # ---- loop seam: the looped signal (last 1.2 s + first 1.2 s) must show no onset, step or HF burst at the seam
    rms = lambda y: float(A.db(np.sqrt(np.mean(y ** 2)) + 1e-15))
    w50, c = _n(0.05), _n(1.2)
    loopd = np.concatenate([x[-c:], x[:c]])
    sot, sos = onsets(loopd)
    inner = (sot > 0.1) & (sot < 2.3)
    sot, sos = sot[inner] - 1.2, sos[inner]
    hfe = uniform_filter1d(np.square(A.hp(loopd, 6000.0, 4)).mean(1), _n(0.005))
    d1 = np.abs(np.diff(loopd[c - _n(0.05):c + _n(0.05)], axis=0)).max(1)
    rep['loop_seam'] = dict(
        last50ms_rms_dbfs=round(rms(x[-w50:]), 2), first50ms_rms_dbfs=round(rms(x[:w50]), 2),
        delta_db=round(rms(x[-w50:]) - rms(x[:w50]), 2),
        sample_step_at_seam=round(float(np.abs(x[0] - x[-1]).max()), 6),
        max_sample_step_within_50ms=round(float(d1.max()), 6),
        median_sample_step_within_50ms=round(float(np.median(d1)), 6),
        hf_6k_energy_at_seam_vs_median_db=round(float(10 * np.log10(hfe[c - _n(0.01):c + _n(0.01)].max()
                                                                   / np.median(hfe[_n(0.1):-_n(0.1)]))), 2),
        onsets_within_100ms_of_seam=[dict(t=round(float(t), 3), strength=round(float(v), 1))
                                     for t, v in zip(sot, sos) if abs(t) < 0.1],
        onset_strength_median_in_excerpt=round(float(np.median(sos)), 1) if len(sos) else None,
        onset_strength_max_in_excerpt=round(float(np.max(sos)), 1) if len(sos) else None,
        last_1s_vs_first_1s_lu=round(A.loudness(x[-_n(1.0):]) - A.loudness(x[:_n(1.0)]), 2))
    _spectro(x, os.path.join(out, 'music_full_spectrogram.png'), rep)
    _zooms(x, os.path.join(out, 'music_zoom_dropout_seam.png'))
    json.dump(rep, open(os.path.join(out, 'music_full.verify.json'), 'w'), indent=1)
    print(json.dumps(rep, indent=1))
    return rep


def _spectro(x, path, rep):
    from PIL import ImageDraw
    W, H = 1760, 640
    e = rep['ebur128_ffmpeg']
    k = rep['kicks']
    img = A.spectro_image(x, W, H, None, 'log_kya_kahenge  music_full.wav  75 BPM  D minor  35.2 s',
                          'ffmpeg ebur128: I %.1f LUFS  TP %.1f dBTP  LRA %.1f LU  |  kicks: %.3f BPM, phase %+.1f ms'
                          '  |  bar lines orange, drop-out red, sections labelled' % (
                              e['I_lufs'], e['true_peak_dbfs'], e['LRA_lu'], k['fit_bpm'], k['fit_phase_ms']),
                          tmax=DUR)
    dr = ImageDraw.Draw(img)
    top, wav_h = 44, int(H * 0.26)
    xs = lambda t: int(round(t / DUR * W))
    for b in range(12):
        dr.line([(xs(b * BAR), top), (xs(b * BAR), H - 18)], fill=(255, 140, 40), width=1)
        dr.text((xs(b * BAR) + 3, top + 2), 'bar %d' % b, fill=(255, 190, 120), font=A._font(11))
    for t in DROP_OUT:
        dr.line([(xs(t), top), (xs(t), H - 18)], fill=(255, 40, 40), width=2)
    for nm, t0, t1, _, _ in SECTIONS:
        if nm == 'drop-out':
            dr.text((xs(t0) - 18, top + 16), 'drop-out', fill=(255, 90, 80), font=A._font(12, True))
        else:
            dr.text((xs(t0) + 4, top + wav_h - 16), nm, fill=(255, 243, 230), font=A._font(12, True))
    img.save(path)


def _zooms(x, path):
    from PIL import Image, ImageDraw
    p1 = A.spectro_image(x[_n(14.4):_n(16.8)], 860, 420, 0.8, 'drop-out zoom 14.4-16.8 s',
                         'cyan = 15.2 (gate closes); silence to 16.0; first pulse on 16.0 (x = 1.6 s)')
    seam = np.concatenate([x[-_n(1.2):], x[:_n(1.2)]])
    p2 = A.spectro_image(seam, 860, 420, 1.2, 'loop seam zoom: 34.0-35.2 s | 0.0-1.2 s',
                         'cyan = the seam (35.2 -> 0.0); no click, no level step expected')
    img = Image.new('RGB', (1720, 420))
    img.paste(p1, (0, 0))
    img.paste(p2, (860, 0))
    ImageDraw.Draw(img).line([(860, 0), (860, 420)], fill=(255, 255, 255), width=2)
    img.save(path)


# ============================================================================================ final mix (run 2)
def mix(hook='A', vo=None, sfx=None, music=None, out_dir=None):
    """The final mix now lives in log_kya_kahenge_mix.py (loop-safe, mono-VO-safe, measured duck windows; the old
    epic_mix.mix_reel call crashed on the mono VO stem and clicked at the loop seam: SHARED_REQUESTS R6a / R6c).
    `mix` delegates to it; the --vo / --sfx / --music / --out-dir overrides are no longer supported."""
    if any((vo, sfx, music, out_dir)):
        sys.exit('mix: path overrides are not supported; run log_kya_kahenge_mix.py (inputs are fixed, see its docstring)')
    import log_kya_kahenge_mix as LX
    rep, _ = LX.mix(hook)
    LX.verify(hook)
    return rep


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=('build', 'verify', 'mix'))
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--seed', type=int, default=SEED)
    ap.add_argument('--hook', choices=('A', 'B'), default='A')
    ap.add_argument('--vo')
    ap.add_argument('--sfx')
    ap.add_argument('--music')
    ap.add_argument('--out-dir')
    a = ap.parse_args()
    if a.cmd == 'build':
        build(a.out, a.seed)
    elif a.cmd == 'verify':
        verify(a.out)
    else:
        mix(a.hook, a.vo, a.sfx, a.music, a.out_dir)
