#!/usr/bin/env python3
"""beta_tum_karte_kya_ho_music.py: ORIGINAL music bed for Reel 4 · C02 "Beta, tum karte kya ho?" (owner:
music-supervisor). Plan: brand_reels/design/reels/beta_tum_karte_kya_ho/BRIEF.md §6.13; map and verification:
MUSIC.md in the same folder.

Procedural and deterministic (fixed seeds, numpy/scipy only). Every sound is synthesised in this repo: the
epic_music building blocks (EM.epiano, EM.kick, EM.clap, EM.bass808), epic_sfx's tabla_hit (Sa = D4) and the
toolkit's crackle grains. No sample of any song, no AI model, nothing trending. Licence: original work made for
@jawad_mp4. Style: `lofi_desi` RE-ARRANGED per the brief (not EM.render('lofi_desi'): no harmonium, no sitar, no
end tape stop, no end fade). One desi voice: the tabla.

Key D minor (Sa = D), 600/7 = 85.714 BPM = 0.7 s = 21 frames per beat, 13 bars of 2.8 s = 36.4 s =
1,747,200 samples at 48 kHz. Bar n starts at 2.8 n s, beat k (0-based) at 0.7 k s; off-8ths swing by 0.06 beat.

    bar 0      0.0-2.8    Dm9      tabla kaharwa theka + EP; frame 0 = EP chord + tabla 'dha'; 'dha' accent 1.4 s
    bars 1-3   2.8-11.2   Bbmaj7, Gm9, A7b9   + soft kick on beat 0 and the swung 2.5 (lp 1800, -4 dB); EP stab
    bar 4      11.2-12.6  Dm9      groove; tape stop 12.15 -> 12.6 (music dies INTO the killer line)
    -          12.6-14.0  silence (room tone comes from the SFX bed)
    bars 5-6   14.0-19.6  Bbmaj7 | Gm9 (2 beats) A7b9 (2 beats)   EP only, lp 1500, -6 dB; one tabla 'tin' 16.8
    bars 7-9   19.6-27.3  Dm9, Bbmaj7, Gm9   full: tabla + kick + clap (beats 1, 3) + 808 root + EP
    -          27.3-28.0  drop-out: gated after the reverbs, 4 ms edge (true digital silence)
    bar 10     28.0-30.8  D add9 (D2 / D3 F#3 A3 E4)   warm EP + soft pad struck at 28.0, held; tabla -6 dB 29.4
    bar 11     30.8-33.6  Bbmaj7   tabla + EP, no kick
    bar 12     33.6-36.4  A7b9     tabla + EP, thinning to EP + one 'tin' at 35.7; resolves into bar 0's Dm9

Bus: six stems (tabla, kit = kick + clap, bass = 808, keys = EP, pad, fx = vinyl crackle) -> tabla slap tamer
(fast 2:1 above +9 dB) -> keys, pad and fx sidechained 4 dB to the kick, the 808 6 dB -> 'studio' reverb -18 dB
per stem (tails kept) -> 24 Hz subsonic high-pass -> section groups made separately (bars 0-4: tape stop, silent
from 12.6; bars 5-9: drop-out gate at 27.3; bars 10-12: their overhang past 36.4 s folded onto the head =
circular, loop-friendly) -> loop-safe level rider (amount 0.3) -> bus glue (epic_mix's 2:1) -> -16.0 LUFS
integrated -> 4x true-peak limiter at -3.3 dBFS (<= -3.0 dBTP). Every bus stage is a linear filter or a gain curve
shared by all stems (the tamer and the two sidechains act per stem before the sum), so the six stems sum exactly
to music_full.wav.

CLI (run from pipeline/jawad_reels; heavy work through tools/heavy.sh):
    tools/heavy.sh python3 beta_tum_karte_kya_ho_music.py build    -> <reel ws>/music/music_full.wav, stems/,
                                                                       music_full.json (map, events, numbers)
    tools/heavy.sh python3 beta_tum_karte_kya_ho_music.py verify   -> music_full.verify.json + spectrogram PNGs
    (no argument = build + verify)
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
from scipy.ndimage import uniform_filter1d  # noqa: E402
import audio as A  # noqa: E402
import epic_sfx as E  # noqa: E402
import epic_music as EM  # noqa: E402
from audio import SR, undb, _n  # noqa: E402

# ============================================================================================ constants
MODULE = 'beta_tum_karte_kya_ho'
BPM = 600 / 7                                   # 85.714 BPM, frame-locked: 21 frames per beat at 30 fps
FPS = 30
BEAT = 0.7                                      # s (= 60 / BPM, kept exact)
BAR = 4 * BEAT                                  # 2.8 s = 84 frames
BARS = 13
DUR = BARS * BAR                                # 36.4 s
N = _n(DUR)
assert N == 1747200 and abs(60.0 / BPM - BEAT) < 1e-12
SWING = 0.06 * BEAT                             # off-8ths land 42 ms late (lo-fi swing, epic_music lofi value)
SEED = 402                                      # slot 4 / C02
OVER = 2.0                                      # s rendered past DUR, then folded onto the head (circular)
MARGIN = 1.2                                    # s more, only to prove nothing is lost past DUR + OVER
NT = _n(DUR + OVER + MARGIN)
RW = os.path.join(REPO, 'workspace', 'jawad_reels', MODULE)
OUT = os.path.join(RW, 'music')
TARGET_LUFS, TP_CEILING = -16.0, -3.0           # music alone; epic_mix re-levels the bed to -18 LUFS under VO
STEMS = ('tabla', 'kit', 'bass', 'keys', 'pad', 'fx')
STEM_DB = dict(tabla=-1.5, kit=0.0, bass=-1.0, keys=-0.5, pad=-0.5, fx=-3.0)
TAME = dict(tabla=(9.0, 2.0, 0.001, 0.08))      # tabla slap tamer: (over_db, ratio, attack s, release s)

SUBSONIC_HZ = 24.0
BASS_DUCK_DB = 6.0                              # 808 sidechained to the kick
GLUE = dict(ratio=2.0, below_p98_db=3.0, attack=0.006, release=0.15)   # gentle bus glue before the limiter
TAPE_STOP = (12.15, 0.45)                       # music dies into the killer line: silent from 12.6
SILENCE_1 = (12.6, 14.0)
DROP_OUT = (27.3, 28.0)                         # 1 beat, gated after the reverbs
GATE_EDGE = 0.004
GROUPS = dict(A=(0.0, SILENCE_1[0]), B=(SILENCE_1[1], DROP_OUT[0]), C=(DROP_OUT[1], DUR))


def T(bar, beat=0.0):
    """Reel time (s) of bar `bar`, beat `beat` (both 0-based)."""
    return round((bar * 4 + beat) * BEAT, 9)


def group_of(t):
    for g, (a, b) in GROUPS.items():
        if a <= t < b:
            return g
    raise ValueError('event at %.4f s falls in a silence' % t)


# Chords: EP left-hand root + right-hand voicing (MIDI). Voice-led so the top line runs E4 D4 D4 E4 -> E4.
CHORDS = {
    'Dm9':    (50, (53, 57, 60, 64)),          # D3 | F3 A3 C4 E4
    'Bbmaj7': (46, (53, 57, 62)),              # Bb2 | F3 A3 D4
    'Gm9':    (43, (53, 57, 58, 62)),          # G2 | F3 A3 Bb3 D4
    'A7b9':   (45, (55, 58, 61, 64)),          # A2 | G3 Bb3 C#4 E4
    'Dadd9':  (38, (50, 54, 57, 64)),          # D2 | D3 F#3 A3 E4 (the payoff, voicing from the brief)
}
BASS808 = {'Dm9': 38, 'Bbmaj7': 34, 'Gm9': 31}  # D2, Bb1, G1 (808 roots, full-groove bars only)
KAHARWA = EM.KAHARWA                            # dha ge na tin | na ke dhin na  (8ths)

# bar -> (chord changes [(beat, chord)], section, layers)
PLAN = {
    0: ([(0, 'Dm9')], 'hook', 'tabla theka + EP'),
    1: ([(0, 'Bbmaj7')], 'comedy', 'tabla + EP + soft kick'),
    2: ([(0, 'Gm9')], 'comedy', 'tabla + EP + soft kick'),
    3: ([(0, 'A7b9')], 'comedy', 'tabla + EP + soft kick'),
    4: ([(0, 'Dm9')], 'comedy_stop', 'groove; tape stop 12.15-12.6'),
    5: ([(0, 'Bbmaj7')], 'sad', 'EP only (lp 1500, -6 dB)'),
    6: ([(0, 'Gm9'), (2, 'A7b9')], 'sad', "EP only + one tabla 'tin' at 16.8"),
    7: ([(0, 'Dm9')], 'flood', 'full: tabla + kick + clap + 808 + EP'),
    8: ([(0, 'Bbmaj7')], 'flood', 'full: tabla + kick + clap + 808 + EP'),
    9: ([(0, 'Gm9')], 'flood', 'full, gated at 27.3 (drop-out)'),
    10: ([(0, 'Dadd9')], 'payoff', 'warm EP + soft pad struck at 28.0, held; tabla -6 dB from 29.4'),
    11: ([(0, 'Bbmaj7')], 'endcard', 'tabla + EP, no kick'),
    12: ([(0, 'A7b9')], 'loop', "tabla + EP, thins to EP + one 'tin' at 35.7"),
}

GAIN = dict(                                     # dB, per event (before STEM_DB and the bus)
    ep=-7.0, ep_stab=-13.0, ep_sad=-13.0, ep_payoff=-7.0, ep_end=-8.5, ep_turn=-12.0,
    pad=6.5,
    tabla_strong=0.0, tabla_weak=-3.0, tabla_hook_accent=0.0, tabla_payoff=-6.0, tabla_end=-3.0, tin_sad=-4.0,
    tin_loop=-3.0,
    kick=-3.5, kick_comedy=-7.5, clap=-5.0, bass808=-7.0, crackle=0.0,
)


def _name(m):
    return ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'][m % 12] + str(m // 12 - 1)


# ============================================================================================ composition
def compose():
    """-> list of events: dict(t, stem, inst, args, gain_db, pan, group, what). Pure data (the score)."""
    rv = np.random.default_rng(SEED)           # tiny deterministic velocity variation (never timing on beats)
    ev = []

    def add(t, stem, inst, what, gain_db=0.0, pan=0.0, **args):
        t = round(float(t), 6)
        ev.append(dict(t=t, stem=stem, inst=inst, args=args, gain_db=round(float(gain_db), 3), pan=pan,
                       group=group_of(t), what=what))

    def chord(t, name, gain, dur, bright=0.6, lp=None, strum=0.009, upper_only=False, label=''):
        root, up = CHORDS[name]
        notes = list(up) if upper_only else [root] + list(up)
        for k, m in enumerate(notes):           # the lowest note sits exactly on the beat, the rest strum up
            add(t + k * strum, 'keys', 'ep', 'EP %s %s%s' % (name, _name(m), label), gain + rv.uniform(-0.6, 0.6),
                0.3 * (1 if k % 2 else -1) * (0 if k == 0 and not upper_only else 1), midi=m, dur=dur,
                bright=bright, lp=lp, first=(k == 0))

    def theka(bar, idx, level_strong, level_weak, label=''):
        for i in idx:
            st, _ = KAHARWA[i]
            t = T(bar, i * 0.5) + (SWING if i % 2 else 0.0)
            g = (level_strong if i in (0, 6) else level_weak) + rv.uniform(-0.8, 0.8)
            add(t, 'tabla', 'tabla', "tabla '%s'%s" % (st, label), g, 0.1, stroke=st, seed=(bar * 8 + i) % 4)

    def kick(t, g, label=''):
        add(t, 'kit', 'kick', 'kick' + label, g, 0.0, lp=1800.0)

    # ---- bar 0: hook. Frame 0 = EP Dm9 + tabla 'dha'; the 'dha' accent on beat 2 (1.4 s) answers the keyword flare
    chord(T(0), 'Dm9', GAIN['ep'], BAR + 0.5)
    theka(0, [0, 1, 2, 3, 5, 6, 7], GAIN['tabla_strong'], GAIN['tabla_weak'])
    add(T(0, 2), 'tabla', 'tabla', "tabla 'dha' accent (keyword halo flare)", GAIN['tabla_hook_accent'], 0.1,
        stroke='dha', seed=1)
    # ---- bars 1-4: comedy groove (soft kick on 0 and the swung 2.5, EP stab on the swung 2.5)
    for bar in (1, 2, 3, 4):
        name = PLAN[bar][0][0][1]
        chord(T(bar), name, GAIN['ep'], BAR + 0.5)
        # bar 2's 'dhin' at 7.7 rests: the punch-in's SFX tabla 'ge' (comic bass bend) owns that instant, and the
        # same Sa-tuned stroke in the bed would stack on it coherently
        theka(bar, [i for i in (range(8) if bar < 4 else range(4)) if not (bar == 2 and i == 6)],
              GAIN['tabla_strong'], GAIN['tabla_weak'])
        kick(T(bar), GAIN['kick_comedy'], ' (soft, comedy)')
        if bar < 4:                             # bar 4's 2.5 lands after the tape stop's last read sample
            kick(T(bar, 2.5) + SWING, GAIN['kick_comedy'], ' (soft, comedy)')
            chord(T(bar, 2.5) + SWING, name, GAIN['ep_stab'], 1.0, upper_only=True, label=' stab')
    # ---- bars 5-6: sad-comic, EP only (lp 1500, -6 dB) + one 'tin' at 16.8
    chord(T(5), 'Bbmaj7', GAIN['ep_sad'], BAR + 0.4, lp=1500.0)
    chord(T(6), 'Gm9', GAIN['ep_sad'], 2 * BEAT + 0.3, lp=1500.0)
    chord(T(6, 2), 'A7b9', GAIN['ep_sad'], 2 * BEAT + 0.6, lp=1500.0)
    add(T(6), 'tabla', 'tabla', "tabla 'tin' (single)", GAIN['tin_sad'], 0.1, stroke='tin', seed=2)
    # ---- bars 7-9: the family group floods (full groove); bar 9 stops at the drop-out (27.3)
    for bar in (7, 8, 9):
        name = PLAN[bar][0][0][1]
        chord(T(bar), name, GAIN['ep'], BAR + 0.5)
        chord(T(bar, 2.5) + SWING, name, GAIN['ep_stab'], 1.0, upper_only=True, label=' stab')
        theka(bar, range(8) if bar < 9 else range(6), GAIN['tabla_strong'], GAIN['tabla_weak'])
        kick(T(bar), GAIN['kick'])
        kick(T(bar, 2.5) + SWING, GAIN['kick'])
        for b in (1, 3):
            if T(bar, b) < DROP_OUT[0]:
                add(T(bar, b), 'kit', 'clap', 'clap', GAIN['clap'], 0.0, lp=4000.0)
        add(T(bar), 'bass', 'bass808', '808 %s' % _name(BASS808[name]), GAIN['bass808'], 0.0,
            midi=BASS808[name], dur=3.5 * BEAT, drive=1.4)
    # ---- bar 10: the payoff. One warm chord + soft pad struck at 28.0 and held; tabla back at -6 dB on 29.4
    chord(T(10), 'Dadd9', GAIN['ep_payoff'], BAR + 0.6, bright=0.7, strum=0.008, label=' (payoff)')
    add(T(10), 'pad', 'pad', 'pad D add9 (payoff, held)', GAIN['pad'], 0.0, midis=(50, 54, 57, 62, 64),
        dur=BAR - 0.2, attack=0.06, release=0.5, cutoff=1400.0)
    theka(10, [4, 5, 6, 7], GAIN['tabla_payoff'], GAIN['tabla_payoff'] - 3.0, ' (re-entry -6 dB)')
    # ---- bar 11: end card, tabla + EP, no kick
    chord(T(11), 'Bbmaj7', GAIN['ep_end'], BAR + 0.5)
    theka(11, range(8), GAIN['tabla_end'], GAIN['tabla_end'] - 3.0)
    # ---- bar 12: dominant turnaround into bar 0's Dm9 (loop). Theka thins out after beat 1.5
    chord(T(12), 'A7b9', GAIN['ep'], BAR + 0.5)
    chord(T(12, 2), 'A7b9', GAIN['ep_turn'], 2 * BEAT + 0.9, upper_only=True, label=' (turnaround re-strike)')
    theka(12, [0, 1, 2, 3], GAIN['tabla_end'], GAIN['tabla_end'] - 3.0)
    add(T(12, 3), 'tabla', 'tabla', "tabla 'tin' (single, into the loop)", GAIN['tin_loop'], 0.1, stroke='tin',
        seed=3)
    ev.sort(key=lambda e: (e['t'], e['stem'], e['what']))
    for e in ev:
        e['frame'] = round(e['t'] * FPS, 2)
        e['bar_beat'] = '%d.%s' % (int(e['t'] // BAR + 1e-9), ('%.3f' % ((e['t'] % BAR) / BEAT)).rstrip('0').rstrip('.'))
    return ev


# ============================================================================================ instruments
def warm_pad(midis, dur, attack, release, cutoff, seed, decay=3.0):
    """Soft detuned-saw pad (struck, not swelled): attack `attack` s, held `dur` while sinking with time
    constant `decay` s (-8 dB over a 2.8 s bar at 3.0), then a raised-cosine release."""
    r = A._rng(seed, 'c02_pad')
    n = _n(dur + release)
    t = np.arange(n) / SR
    x = np.zeros((n, 2))
    for m in midis:
        for c in (-1, 1):
            v = E.saw(np.full(n, E.midi_hz(m) * (1 + c * 0.0032)), r.uniform(0, 1))
            A._add(x, A.pan(v, 0.55 * c), 0.0)
    env = np.clip(t / attack, 0, 1) * np.exp(-t / decay)
    rel = np.clip((t - dur) / release, 0, 1)
    env *= np.where(t < dur, 1.0, 0.5 + 0.5 * np.cos(np.pi * rel))
    return undb(EM.CAL['pad']) * A.lp(x, cutoff, 2) * env[:, None] / max(len(midis), 1)


def render_event(e, i):
    a = e['args']
    r = A._rng(SEED, 'ev%d' % i)
    hit = 0.0
    if e['inst'] == 'ep':
        x = EM.epiano(E.midi_hz(a['midi']), a['dur'], r, a['bright'])
        if a.get('lp'):
            x = A.lp(x, a['lp'], 2)
    elif e['inst'] == 'pad':
        x = warm_pad(a['midis'], a['dur'], a['attack'], a['release'], a['cutoff'], SEED)
    elif e['inst'] == 'tabla':
        s = A.sound('tabla_hit', stroke=a['stroke'], pitch=1.0, seed=a['seed'])
        x, hit = np.asarray(s, dtype=np.float64), s.hit
    elif e['inst'] == 'kick':
        x = A.lp(EM.kick(r, 0.6), a['lp'], 2)
    elif e['inst'] == 'clap':
        x = A.lp(EM.clap(r), a['lp'], 2)
    elif e['inst'] == 'bass808':
        x = EM.bass808([(0.0, a['dur'], a['midi'], None)], _n(a['dur'] + 0.05), a['drive'])
    else:
        raise ValueError(e['inst'])
    x = A.pan(x, e['pan']) if e['pan'] else A._st(x)
    return x * undb(e['gain_db']), hit


def render_groups(ev):
    """-> raw[group][stem] (NT, 2) and the mono kick key (NT,)."""
    raw = {g: {k: np.zeros((NT, 2)) for k in STEMS} for g in GROUPS}
    key = np.zeros(NT)
    for i, e in enumerate(ev):
        x, hit = render_event(e, i)
        A._add(raw[e['group']][e['stem']], x, e['t'] - hit)
        if e['inst'] == 'kick':
            A._add(key, x.mean(1), e['t'])
    # vinyl crackle (epic_music lofi level 0.02), one continuous take, masked to each group's span (4 ms edges)
    cr = A._crackle(DUR, A._rng(SEED, 'c02_crackle'), 60, 1500, 9000, spread=0.6) * 0.02 * undb(GAIN['crackle'])
    tt = np.arange(N) / SR
    for g, (a, b) in GROUPS.items():
        m = np.clip((tt - a) / GATE_EDGE, 0, 1) * np.clip((b - tt) / GATE_EDGE, 0, 1)
        raw[g]['fx'][:N] += cr[:N] * m[:, None]
    return raw, key


# ============================================================================================ bus
def tape_stop(x):
    """epic_sfx.tape_stop_fx at 12.15 s over 0.45 s (silent from 12.6), entered with a 10 ms crossfade so the
    STFT low-pass of the stop segment never clicks. Linear in x (fixed curves), so it can run per stem."""
    t0, d = TAPE_STOP
    y = E.tape_stop_fx(x, t0, d)
    i0, xf = _n(t0), _n(0.010)
    w = (0.5 - 0.5 * np.cos(np.pi * np.arange(xf) / xf))[:, None]
    y[i0:i0 + xf] = x[i0:i0 + xf] * (1 - w) + y[i0:i0 + xf] * w
    y[_n(t0 + d):] = 0.0
    return y


def gate_closed_from(t, n):
    """1 before t - 4 ms, raised-cosine to 0 at t, 0 after (the drop-out gate, applied after the reverbs)."""
    g = np.ones(n)
    a, f = _n(t), _n(GATE_EDGE)
    g[a - f:a] = 0.5 + 0.5 * np.cos(np.pi * np.arange(1, f + 1) / f)
    g[a:] = 0.0
    return g


def rider_gain(x, amount=0.3, win=1.5, max_db=9.0):
    """EM.level_rider made loop-safe (windows wrap around the seam) and blind to the gated silences (they are
    not 'quiet music'; their gain is bridged from the neighbours). Returns a linear gain curve."""
    p = np.square(A.kweight(A._st(x))).mean(1)
    valid = np.abs(x).max(1) > 0
    w = valid.astype(np.float64)
    num = uniform_filter1d(p * w, _n(win), mode='wrap')
    den = uniform_filter1d(w, _n(win), mode='wrap')
    lv = 10 * np.log10(np.maximum(num / np.maximum(den, 1e-9), 1e-12))
    act = (lv > lv[valid].max() - 40) & valid & (den > 0.2)
    med = np.median(lv[act])
    g = np.clip(-amount * (lv - med), -max_db, max_db)
    idx = np.arange(len(g))
    g = np.interp(idx, idx[act], g[act], period=len(g))
    g = uniform_filter1d(g, _n(1.0), mode='wrap')
    return undb(g)


def glue_gain(x):
    """epic_mix.glue's bus compressor (2:1 soft knee, 6 ms / 150 ms, threshold 3 dB under the 98th-percentile
    10 ms level), computed on the loop ([tail | x | head]) so the seam is continuous. Linear gain curve."""
    p = _n(0.5)
    xx = np.concatenate([x[-p:], x, x[:p]])
    lv = 10 * np.log10(np.maximum(uniform_filter1d(np.square(xx).max(1), _n(0.01)), 1e-20))
    act = lv > lv.max() - 45
    thr = float(np.percentile(lv[act], 98)) - GLUE['below_p98_db']
    gr = A.compressor_gain(xx, thresh_db=thr, ratio=GLUE['ratio'], knee_db=6.0, attack=GLUE['attack'],
                           release=GLUE['release'], rms=0.008)
    return undb(gr)[p:-p]


def limiter_circular(x, ceiling_db):
    """A.limiter_gain on the loop: computed on [tail | x | head] so lookahead and release see across the seam."""
    p = _n(0.25)
    xx = np.concatenate([x[-p:], x, x[:p]])
    return A.limiter_gain(xx, ceiling_db)[p:-p]


def tamer_gain(x, over_db, ratio, attack, release):
    """Fast soft-knee compressor gain (linear) for one whole stem: threshold = the stem's active RMS (10 ms
    windows, top 40 dB) + over_db. Shaves the strum / slap peaks so the bus limiter only touches rare hits."""
    p = np.square(A._st(x)).max(1)
    lv = 10 * np.log10(np.maximum(uniform_filter1d(p, _n(0.01)), 1e-20))
    act = lv > lv.max() - 40
    thr = 10 * np.log10(np.mean(p[act])) + over_db
    return undb(A.compressor_gain(x, thresh_db=thr, ratio=ratio, knee_db=6.0, attack=attack, release=release,
                                  rms=0.002))


def bus(raw, key):
    """Raw groups -> (mix, stems, info). Each stage is a linear filter or one gain curve shared by all stems."""
    sc = A.sidechain(np.ones(NT), key, depth_db=4.0, attack=0.005, release=0.16)[:, 0]
    sc_bass = A.sidechain(np.ones(NT), key, depth_db=BASS_DUCK_DB, attack=0.002, release=0.12)[:, 0]
    tame = {k: tamer_gain(sum(raw[g][k] for g in GROUPS), *TAME[k]) for k in TAME}
    st = {k: np.zeros((NT, 2)) for k in STEMS}
    for g in GROUPS:
        for k in STEMS:
            x = raw[g][k] * undb(STEM_DB[k])
            if not np.any(x):
                continue
            if k in tame:
                x = x * tame[k][:, None]
            if k in ('keys', 'pad', 'fx'):
                x = x * sc[:, None]
            elif k == 'bass':                    # the 808 ducks under the kick (no low-end pile-up on the one)
                x = x * sc_bass[:, None]
            x = A.reverb(x, 'studio', wet_db=-18.0)[:NT]
            # subsonic clean-up (kick / bayan / 808 DC, the tape stop's sweep to 0 Hz): 2nd-order high-pass at
            # 24 Hz, applied BEFORE each group's silence is made, so the silences stay digital zero
            if g == 'A':
                x = A.hp(tape_stop(x), SUBSONIC_HZ, 2) * gate_closed_from(SILENCE_1[0], NT)[:, None]
            elif g == 'B':
                x = A.hp(x, SUBSONIC_HZ, 2) * gate_closed_from(DROP_OUT[0], NT)[:, None]
            else:
                x = A.hp(x, SUBSONIC_HZ, 2)
            st[k] += x
    lost = max(float(np.abs(v[_n(DUR + OVER):]).max()) for v in st.values())
    pre_peak = max(float(np.abs(v).max()) for v in st.values())
    folded = {}
    for k in STEMS:                              # circular: the overhang past DUR wraps onto the head
        y = st[k][:N].copy()
        y[:_n(OVER)] += st[k][N:N + _n(OVER)]
        folded[k] = y
    pre = sum(folded.values())
    ride = rider_gain(pre)
    pre = pre * ride[:, None]
    glue = glue_gain(pre)                        # 2:1 above (98th-pct 10 ms level - 3 dB): shaves the stacked
    pre = pre * glue[:, None]                    # downbeats so the true-peak limiter only touches rare peaks
    ride = ride * glue
    g = TARGET_LUFS - A.loudness(pre)
    for _ in range(12):
        gl = limiter_circular(pre * undb(g), TP_CEILING - 0.3)
        y = pre * undb(g) * gl[:, None]
        L = A.loudness(y)
        if abs(L - TARGET_LUFS) < 0.02:
            break
        g += TARGET_LUFS - L
    curve = ride * undb(g) * gl
    stems = {k: v * curve[:, None] for k, v in folded.items()}
    mix = sum(stems.values())
    info = dict(lufs=round(A.loudness(mix), 3), true_peak_dbtp=round(A.true_peak(mix), 3),
                lra=round(A.loudness_range(mix), 2), master_gain_db=round(float(g), 2),
                limiter_max_gr_db=round(float(-A.db(gl.min())), 3),
                limiter_gr_over_0p5db_s=round(float(np.sum(gl < undb(-0.5)) / SR), 4),
                rider_x_glue_db_range=[round(float(A.db(ride.min())), 2), round(float(A.db(ride.max())), 2)],
                glue_max_gr_db=round(float(-A.db(glue.min())), 2),
                sidechain_max_db=round(float(A.db(sc.min())), 2),
                tamer_max_db={k: round(float(A.db(v.min())), 2) for k, v in tame.items()},
                overhang_lost_dbfs_rel=round(float(A.db(lost / (pre_peak + 1e-12))), 1))
    return mix, stems, info


# ============================================================================================ build
def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def build(out=OUT):
    E.register(samples=False)
    ev = compose()
    raw, key = render_groups(ev)
    mix, stems, info = bus(raw, key)
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    full = os.path.join(out, 'music_full.wav')
    A._write_wav(full, mix, 24)
    paths = {}
    for k in STEMS:
        paths[k] = os.path.join(out, 'stems', 'music_stem_%s.wav' % k)
        A._write_wav(paths[k], stems[k], 24)
    sections = [dict(bar=b, t0=T(b), t1=T(b + 1), frames=[int(round(T(b) * FPS)), int(round(T(b + 1) * FPS))],
                     chords=[c for _, c in PLAN[b][0]], section=PLAN[b][1], layers=PLAN[b][2]) for b in range(BARS)]
    meta = dict(module=MODULE, file=full, sha256=_sha(full), stems={k: dict(path=p, sha256=_sha(p))
                                                                  for k, p in paths.items()},
                dur=DUR, samples=N, sr=SR, bits=24, bpm=BPM, beat_s=BEAT, bar_s=BAR, key='D minor (Sa = D)',
                seed=SEED, swing_s=SWING, tape_stop=TAPE_STOP, silence=SILENCE_1, drop_out=DROP_OUT,
                fold_overhang_s=OVER, target_lufs=TARGET_LUFS, tp_ceiling=TP_CEILING, sections=sections,
                bus=info, events=ev, source='procedural numpy (this file + epic_music/epic_sfx/audio building '
                                            'blocks); original, owned, no samples of songs, no AI model')
    json.dump(meta, open(os.path.join(out, 'music_full.json'), 'w'), indent=1)
    print(json.dumps(dict(file=full, sha256=meta['sha256'], **info), indent=1))
    return meta


# ============================================================================================ verify
def _ffprobe(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,'
                        'bits_per_raw_sample,bits_per_sample,duration_ts,duration', '-of', 'json', p],
                       capture_output=True, text=True, check=True)
    return json.loads(o.stdout)['streams'][0]


def _ebur128(p):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    tail = o.stderr[o.stderr.rfind('Summary:'):]
    def grab(label):
        import re
        m = re.search(label + r':\s+(-?[\d.]+|-inf)', tail)
        return float(m.group(1)) if m and m.group(1) != '-inf' else None
    return dict(I_lufs=grab('I'), LRA_lu=grab('LRA'), TP_dbfs=grab('Peak'))


def _rms_db(x, a, b):
    s = x[_n(a):_n(b)]
    return round(float(A.db(np.sqrt(np.mean(np.square(s))) + 1e-15)), 1) if len(s) else None


def _peak_db(x, a, b):
    s = x[_n(a):_n(b)]
    return round(float(A.db(np.abs(s).max() + 1e-15)), 1)


def mf_lag(sig, tmpl, p0, search=0.03, L=0.08):
    """Matched filter: lag (s) and normalised correlation of the first L s of `tmpl` (mono or stereo) against
    `sig` around sample p0 (where tmpl's first sample is scheduled), +-search s, circular (loop) indexing."""
    s = A._mono(sig)
    w = A._mono(tmpl)[:_n(L)]
    S = _n(search)
    seg = s[np.arange(p0 - S, p0 + S + len(w)) % len(s)]
    c = signal.correlate(seg, w, mode='valid')
    e = np.sqrt(np.convolve(seg ** 2, np.ones(len(w)), mode='valid') * np.sum(w ** 2)) + 1e-20
    nc = c / e
    j = int(np.argmax(nc))
    return (j - S) / SR, float(nc[j])


def tine_band(midi, rel=0.025):
    f = 14 * E.midi_hz(midi)                     # EM.epiano's tine ping: 1 ms attack, 20 ms decay at 14 x f0
    return f * (1 - rel), f * (1 + rel)


def grid_fit(x, bpm, rel_span=0.003, rel_step=0.00005, phase_step=0.0005, hop=48, nfft=1024):
    """EM.beatgrid's spectral-flux grid score with 1 ms flux frames (EM: 5 ms) and a fine search (tempo step
    0.005 %, phase step 0.5 ms, flux interpolated between frames). Returns tempo, phase (s, in (-B/2, B/2]) and
    strength. Its phase carries the STFT's attack-shape bias, so it is read against a click-grid reference."""
    m = A._mono(np.asarray(x, dtype=np.float64))
    _, tt, Z = signal.stft(m, SR, nperseg=nfft, noverlap=nfft - hop)
    fl = np.maximum(np.diff(np.log1p(np.abs(Z) * 100), axis=1), 0).sum(0)
    h = hop / SR
    best = (-1, None, None)
    for b in bpm * (1 + np.arange(-rel_span, rel_span + 1e-12, rel_step)):
        per = 60.0 / b
        offs = np.arange(0, per, phase_step)
        k = np.arange(int(tt[-1] / per) + 1)
        pos = (offs[:, None] + k[None, :] * per) / h
        ok = pos < len(fl) - 1
        sc = np.where(ok, np.interp(pos, np.arange(len(fl)), fl), 0).sum(1) / ok.sum(1)
        j = int(np.argmax(sc))
        if sc[j] > best[0]:
            best = (sc[j], b, offs[j])
    s, b, off = best
    per = 60.0 / b
    off = (off + per / 2) % per - per / 2
    return dict(tempo=round(float(b), 4), phase_s=round(float(off), 5), strength=round(float(s / fl.mean()), 2))


def match(det, exp, tol):
    det, exp = np.asarray(det), np.asarray(exp)
    dev = [float(d - exp[np.argmin(np.abs(exp - d))]) for d in det] if len(exp) else []
    hit = [any(abs(d - e) <= tol for d in det) for e in exp]
    return dict(n_detected=len(det), n_expected=len(exp),
                detected_on_score=int(sum(abs(v) <= tol for v in dev)),
                expected_found=int(sum(hit)),
                extra=[round(float(d), 4) for d, v in zip(det, dev) if abs(v) > tol],
                missed=[round(float(e), 4) for e, h in zip(exp, hit) if not h],
                max_abs_dev_ms=round(max((abs(v) for v in dev if abs(v) <= tol), default=0.0) * 1000, 2),
                mean_dev_ms=round(float(np.mean([v for v in dev if abs(v) <= tol] or [0.0])) * 1000, 2))


def click_reference(times):
    """Synthetic reference: 1 ms band-limited clicks exactly at `times` (calibrates EM.beatgrid's STFT bias)."""
    x = np.zeros(N)
    c = A.bp(np.r_[np.zeros(64), np.ones(48), np.zeros(4000)], 300, 8000, 2)
    for t in times:
        A._add(x, c, t - 64 / SR)
    return x


def chroma(x, a, b, lo=120.0, hi=1100.0):
    s = A._mono(x)[_n(a):_n(b)]
    S = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    f = np.fft.rfftfreq(len(s), 1.0 / SR)
    m = (f >= lo) & (f <= hi)
    pc = np.round(12 * np.log2(f[m] / 440.0) + 69).astype(int) % 12
    c = np.bincount(pc, weights=S[m], minlength=12)
    return c / (c.max() + 1e-20)


PCN = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def verify(out=OUT):
    full = os.path.join(out, 'music_full.wav')
    meta = json.load(open(os.path.join(out, 'music_full.json')))
    ev = meta['events']
    x, sr = A.read_wav(full)
    rep = dict(file=full, sha256=_sha(full), sha256_matches_build=_sha(full) == meta['sha256'])
    pr = _ffprobe(full)
    rep['ffprobe'] = pr
    rep['format_ok'] = (sr == SR and x.shape == (N, 2) and pr['codec_name'] == 'pcm_s24le'
                        and int(pr['sample_rate']) == 48000 and int(pr['channels']) == 2)
    rep['samples'], rep['dur_s'] = int(x.shape[0]), x.shape[0] / SR
    # ---- loudness
    rep['lufs_integrated'] = round(A.loudness(x), 2)
    rep['true_peak_dbtp'] = round(A.true_peak(x), 2)
    rep['lra_lu'] = round(A.loudness_range(x), 2)
    rep['ebur128'] = _ebur128(full)
    # ---- stems
    st = {k: A.read_wav(os.path.join(out, 'stems', 'music_stem_%s.wav' % k))[0] for k in STEMS}
    rep['stems_format_ok'] = all(v.shape == x.shape for v in st.values())
    resid = np.abs(sum(st.values()) - x).max()
    rep['stems_sum_residual_dbfs'] = round(float(A.db(resid + 1e-15)), 1)
    rep['stems_lufs'] = {k: (round(A.loudness(v), 2) if np.any(v) else None) for k, v in st.items()}
    rep['stems_tp_dbtp'] = {k: round(A.true_peak(v), 2) for k, v in st.items()}
    # ---- silences, tape stop, drop-out, seam
    rep['silence_12p62_13p98'] = dict(peak_dbfs=_peak_db(x, 12.62, 13.98), rms_dbfs=_rms_db(x, 12.62, 13.98))
    rep['silence_exact_12p6_14p0_peak_dbfs'] = _peak_db(x, 12.6, 14.0)
    rep['dropout_27p31_27p99'] = dict(peak_dbfs=_peak_db(x, 27.31, 27.99), rms_dbfs=_rms_db(x, 27.31, 27.99))
    rep['dropout_exact_27p3_28p0_peak_dbfs'] = _peak_db(x, 27.3, 28.0)
    r1210, r1262 = _rms_db(x, 12.075, 12.125), _rms_db(x, 12.595, 12.645)
    rep['tape_stop'] = dict(rms_12p10_dbfs=r1210, rms_12p62_dbfs=r1262,
                            drop_db=round(r1210 - max(r1262, -150.0), 1),
                            rms_by_50ms=[(round(a, 3), _rms_db(x, a - 0.025, a + 0.025))
                                         for a in np.arange(12.0, 12.66, 0.05)])
    rep['seam'] = dict(last_frame_rms_dbfs=_rms_db(x, DUR - 1 / FPS, DUR), first_frame_rms_dbfs=_rms_db(x, 0, 1 / FPS),
                       last_sample=[round(float(v), 6) for v in x[-1]], first_sample=[round(float(v), 6) for v in x[0]],
                       step_at_seam=round(float(np.abs(x[0] - x[-1]).max()), 6),
                       median_abs_step=round(float(np.median(np.abs(np.diff(x[-4800:], axis=0)))), 6),
                       max_abs_step_last_0p1s=round(float(np.abs(np.diff(x[-4800:], axis=0)).max()), 6))
    # ---- momentary loudness by section; payoff vs groove
    tt, lc = A.loudness_curve(x, 0.4, 0.01)                     # tt = window centres

    def mmax(a, b, centre=False):
        m = ((tt >= a) & (tt <= b)) if centre else ((tt - 0.2 >= a) & (tt + 0.2 <= b))
        return round(float(lc[m].max()), 2), round(float(tt[m][np.argmax(lc[m])]), 2)
    rep['momentary_max'] = {'%s %.1f-%.1f' % (k, a, b): mmax(a, b) for k, a, b in (
        ('hook', 0.0, 2.8), ('comedy', 2.8, 12.15), ('sad', 14.0, 19.6), ('flood', 19.6, 27.3),
        ('payoff_bar', 28.0, 30.8), ('endcard', 30.8, 33.6), ('loop_bar', 33.6, 36.4))}
    rep['momentary_max']['payoff (window centre 28.0-28.4)'] = mmax(28.0, 28.4, True)
    rep['momentary_note'] = 'value = (max momentary LUFS, window centre s); windows inside each span'
    rep['momentary_max_overall'] = dict(lufs=round(float(lc.max()), 2), window_centre_s=round(float(tt[np.argmax(lc)]), 2))
    # ---- sub check (no build-up): 20-60 Hz share per bar
    sub = A.lp(A.hp(A._mono(x), 20, 2), 60, 4)
    rep['sub_20_60hz_rms_dbfs_by_bar'] = [_rms_db(sub, T(b), T(b + 1)) for b in range(BARS)]
    rep['full_rms_dbfs_by_bar'] = [_rms_db(A._mono(x), T(b), T(b + 1)) for b in range(BARS)]
    # ---- tempo / beat phase: (1) EM.beatgrid as the brief names it (5 ms phase steps) and a fine version of the
    #      same spectral-flux grid fit; both calibrated on an exact click grid at the same beats (STFT bias)
    stopped = lambda t: TAPE_STOP[0] <= t < SILENCE_1[0]          # events the tape stop slows (not on time)
    beats_played = sorted({round(e['t'], 6) for e in ev
                           if abs(e['t'] / BEAT - round(e['t'] / BEAT)) < 1e-6 and not stopped(e['t'])})
    ref = click_reference(beats_played)
    rep['beatgrid_EM'] = EM.beatgrid(x, BPM)
    rep['beatgrid_EM_click_reference'] = EM.beatgrid(ref, BPM)
    rep['beatgrid_EM_phase_bias_corrected_s'] = round(rep['beatgrid_EM']['phase_s']
                                                      - rep['beatgrid_EM_click_reference']['phase_s'], 4)
    rep['grid_fit_fine'] = grid_fit(x, BPM)
    rep['grid_fit_fine_click_reference'] = grid_fit(ref, BPM)
    rep['grid_fit_fine_phase_bias_corrected_s'] = round(rep['grid_fit_fine']['phase_s']
                                                        - rep['grid_fit_fine_click_reference']['phase_s'], 5)
    # ---- (2) onset analysis by matched filtering (the score is known, so every event's own waveform is the
    #      optimal detector): each scored event is located in its clean stem (+-30 ms search, sample resolution;
    #      the bus's fast gain moves - kick sidechain, glue - can shift a waveform match by < 1 ms);
    #      EP notes through their tine band (same causal band-pass on template and stem; a match exactly one tine
    #      cycle off is listed: where the kick sidechain or the glue reshapes the 20 ms tine, the pure tone can
    #      match a neighbouring cycle); the pad by its first sample above -60 dBFS (it follows the
    #      drop-out). Then each on-beat moment is located in the MIX with the sum of everything scored there.
    E.register(samples=False)
    rev = compose()
    assert [(e['t'], e['what']) for e in rev] == [(e['t'], e['what']) for e in ev], 'score changed since build'
    rep['event_onsets'] = {}
    slips = []                                    # EP matches exactly one tine cycle off (a pure tone's ambiguity)
    for k in STEMS:
        if k == 'fx':
            continue
        res = []
        for i, e in enumerate(rev):
            if e['stem'] != k or stopped(e['t']):
                continue
            tm, hit = render_event(e, i)
            p0 = _n(e['t'] - hit)
            if e['inst'] == 'pad':
                a = np.nonzero(np.abs(st[k][_n(e['t'] - 0.1):]).max(1) > undb(-60))[0]
                lag, nc = (a[0] / SR - 0.1 if len(a) else None), 1.0
            elif e['inst'] == 'ep':
                lo, hi = tine_band(e['args']['midi'])
                lag, nc = mf_lag(A.bp(A._mono(st[k]), lo, hi, 2), A.bp(A._mono(tm), lo, hi, 2), p0, L=0.06)
                per = 1.0 / (14 * E.midi_hz(e['args']['midi']))
                if abs(lag) > 0.0002 and abs(abs(lag) - per) < 0.00005:
                    slips.append((e['t'], e['what'], round(lag * 1000, 3), round(per * 1000, 3)))
            else:                                 # template through the stem's own linear chain (reverb + 24 Hz HP)
                tr = A.hp(A.reverb(tm, 'studio', wet_db=-18.0), SUBSONIC_HZ, 2)
                lag, nc = mf_lag(st[k], tr, p0)
            res.append((e['t'], lag, nc, e['what']))
        lg = np.array([r[1] for r in res if r[1] is not None]) * 1000
        rep['event_onsets'][k] = dict(n_events=len(res), lag_ms_min=round(float(lg.min()), 3),
                                      lag_ms_max=round(float(lg.max()), 3),
                                      exact=int(np.sum(np.abs(lg) < 0.5 * 1000 / SR + 1e-9)),
                                      ncc_min=round(min(r[2] for r in res), 3),
                                      off_by_more_than_1ms=[(r[0], round(r[1] * 1000, 3), round(r[2], 3), r[3])
                                                            for r in res if r[1] is None or abs(r[1]) > 0.001],
                                      tape_stopped_not_checked=sorted({e['t'] for e in rev if e['stem'] == k
                                                                       and stopped(e['t'])}))
    rep['event_onsets']['keys']['one_tine_cycle_matches'] = slips
    devs = []
    xh = A.bp(A._mono(x), 1000.0, 14000.0, 2)     # transients dominate here; tones would correlate at +-1 period
    for tb in beats_played:                       # all events starting within 40 ms (a strum) of the beat
        tm = np.zeros((_n(0.2), 2))
        for i, e in enumerate(rev):
            if tb - 1e-9 <= e['t'] < tb + 0.04:
                y, hit = render_event(e, i)
                A._add(tm, y * undb(STEM_DB[e['stem']]), e['t'] - hit - tb + 0.01)
        lag, nc = mf_lag(xh, A.bp(A._mono(tm), 1000.0, 14000.0, 2), _n(tb - 0.01), L=0.12)
        devs.append((tb, tb + lag, nc))
    fit = [d for d in devs if d[2] >= 0.5]       # the line goes through reliable detections only
    tb = np.array([d[0] for d in fit])
    to = np.array([d[1] for d in fit])
    kk = np.round(tb / BEAT)
    slope, icpt = np.polyfit(kk, to, 1)
    rep['onset_fit'] = dict(method='matched filter on the mix (1-14 kHz, same causal band-pass on both): each '
                                   'on-beat moment = the sum of its scored events',
                            n_beats=len(devs), n_fitted=len(fit), tempo_bpm=round(60.0 / slope, 4),
                            phase_s=round(float(icpt), 6),
                            max_abs_dev_ms=round(float(np.abs(to - tb).max() * 1000), 3),
                            ncc_min=round(min(d[2] for d in devs), 3),
                            residual_rms_ms=round(float(np.sqrt(np.mean((to - (icpt + slope * kk)) ** 2)) * 1000), 4))
    rep['downbeats'] = [dict(bar=b, t=T(b), onset=round(o, 6), dev_ms=round((o - T(b)) * 1000, 3), ncc=round(c, 3))
                        for b in range(BARS) for (t_, o, c) in devs if abs(t_ - T(b)) < 1e-6]
    rep['beats_detail'] = [dict(t=t_, dev_ms=round((o - t_) * 1000, 3), ncc=round(c, 3)) for t_, o, c in devs]
    # ---- (3) nothing sounds where the score is silent: matched-onset probes on a 1/16 grid in both silences
    rep['onsets_in_silences'] = {k: [round(t, 4) for t in np.arange(SILENCE_1[0] + 0.03, SILENCE_1[1] - 0.03, BEAT / 4)
                                     .tolist() + np.arange(DROP_OUT[0] + 0.03, DROP_OUT[1] - 0.03, BEAT / 8).tolist()
                                     if np.abs(v[_n(t - 0.02):_n(t + 0.02)]).max() > 0]
                                 for k, v in list(st.items()) + [('mix', x)]}
    # ---- harmony: chroma per chord span (bass + EP register) vs the planned chord
    hz = []
    for b in range(BARS):
        ch = PLAN[b][0]
        for j, (beat, name) in enumerate(ch):
            a = T(b, beat) + 0.05
            e_ = T(b, ch[j + 1][0]) if j + 1 < len(ch) else T(b + 1)
            if SILENCE_1[0] <= a < SILENCE_1[1]:
                continue
            e_ = min(e_, DROP_OUT[0]) if b == 9 else (min(e_, TAPE_STOP[0]) if b == 4 else e_)
            c = chroma(st['keys'] + st['pad'], a, e_)
            cm = chroma(x, a, e_)
            want = sorted({m % 12 for m in [CHORDS[name][0]] + list(CHORDS[name][1])})
            top = [int(i) for i in np.argsort(c)[::-1][:3]]
            share = float(sum(c[i] for i in want) / c.sum())
            hz.append(dict(bar=b, beat=beat, chord=name, span=[round(a, 3), round(e_, 3)],
                           expected=[PCN[i] for i in want], top3=[PCN[i] for i in top],
                           chord_tone_share=round(share, 3), match=bool(set(top) <= set(want) and share >= 0.7),
                           out_of_key_energy=round(float(sum(c[i] for i in (3, 8, 11)) / c.sum()), 3),
                           mix_top3=[PCN[int(i)] for i in np.argsort(cm)[::-1][:3]],
                           mix_chord_tone_share=round(float(sum(cm[i] for i in want) / cm.sum()), 3)))
    rep['harmony'] = hz
    # ---- pass/fail summary
    P = {}
    P['format 48k/24-bit/stereo, 1,747,200 samples'] = rep['format_ok'] and rep['samples'] == N
    P['-16 LUFS +-0.2 (python)'] = abs(rep['lufs_integrated'] + 16) <= 0.2
    P['-16 LUFS +-0.2 (ffmpeg)'] = abs(rep['ebur128']['I_lufs'] + 16) <= 0.2
    P['TP <= -3.0 dBTP (python)'] = rep['true_peak_dbtp'] <= -3.0
    P['TP <= -2.0 dBTP (ffmpeg)'] = rep['ebur128']['TP_dbfs'] <= -2.0
    P['stems sum to the mix (< -90 dBFS residual)'] = rep['stems_sum_residual_dbfs'] < -90
    P['silence 12.62-13.98 <= -60 dBFS'] = rep['silence_12p62_13p98']['peak_dbfs'] <= -60
    P['drop-out 27.31-27.99 <= -60 dBFS'] = rep['dropout_27p31_27p99']['peak_dbfs'] <= -60
    P['tape stop: RMS drops >= 30 dB 12.10 -> 12.62'] = rep['tape_stop']['drop_db'] >= 30
    P['onset fit (mix, matched filter) tempo 85.714 +-0.1'] = abs(rep['onset_fit']['tempo_bpm'] - BPM) <= 0.1
    P['onset fit (mix, matched filter) |phase| <= 5 ms'] = abs(rep['onset_fit']['phase_s']) <= 0.005
    rel = [d for d in rep['beats_detail'] if d['ncc'] >= 0.5]
    rep['onset_fit']['reliable_beats_ncc_ge_0p5'] = len(rel)
    rep['onset_fit']['reliable_max_abs_dev_ms'] = max(abs(d['dev_ms']) for d in rel)
    rep['onset_fit']['masked_in_mix'] = [d for d in rep['beats_detail'] if d['ncc'] < 0.5]
    P['every on-beat moment found in the mix (ncc >= 0.5) is within 1 ms of the grid'] = (
        rep['onset_fit']['reliable_max_abs_dev_ms'] <= 1.0 and len(rel) >= len(rep['beats_detail']) - 2)
    P['every scored event found in its stem within 1 ms of its time (matched filter)'] = all(
        not v['off_by_more_than_1ms'] for v in rep['event_onsets'].values())
    P['fine grid fit (1 ms flux, blind): tempo 85.714 +-0.01, |phase| <= 5 ms after its click-grid bias'] = (
        abs(rep['grid_fit_fine']['tempo'] - BPM) <= 0.01 and abs(rep['grid_fit_fine_phase_bias_corrected_s']) <= 0.005)
    P['EM.beatgrid tempo 85.71 +-0.1'] = abs(rep['beatgrid_EM']['tempo'] - 85.71) <= 0.1
    P['EM.beatgrid |phase| <= 5 ms after its click-grid bias'] = abs(rep['beatgrid_EM_phase_bias_corrected_s']) <= 0.005
    P['no onsets inside the silences'] = not any(rep['onsets_in_silences'].values())
    P['seam: no gap (>= -40 dBFS RMS on f1091 and f0)'] = (rep['seam']['last_frame_rms_dbfs'] >= -40
                                                          and rep['seam']['first_frame_rms_dbfs'] >= -40)
    P['harmony (keys + pad stems): top-3 pitch classes are chord tones, >= 70 % chord-tone energy'] = all(
        h['match'] for h in hz)
    rep['pass'] = P = {k: bool(v) for k, v in P.items()}
    rep['all_pass'] = all(P.values())
    _spectro(x, os.path.join(out, 'music_full_spectrogram.png'), rep)
    _zooms(x, os.path.join(out, 'music_full_zooms.png'))
    json.dump(rep, open(os.path.join(out, 'music_full.verify.json'), 'w'), indent=1, default=float)
    print(json.dumps(dict(pass_=P, lufs=rep['lufs_integrated'], tp=rep['true_peak_dbtp'], ebur128=rep['ebur128'],
                          onset_fit=rep['onset_fit'], beatgrid_EM=rep['beatgrid_EM'],
                          beatgrid_ref=rep['beatgrid_EM_click_reference'],
                          momentary=rep['momentary_max'], seam=rep['seam']), indent=1, default=float))
    return rep


def _spectro(x, path, rep):
    from PIL import ImageDraw
    W, H = 1820, 720
    img = A.spectro_image(x, W, H, None, '%s  music_full.wav  85.714 BPM  D minor  36.4 s  (bar lines orange, '
                          'silences cyan)' % MODULE,
                          '%.2f LUFS  %.2f dBTP  LRA %.1f LU   onset fit %.3f BPM, phase %+.2f ms' % (
                              rep['lufs_integrated'], rep['true_peak_dbtp'], rep['lra_lu'],
                              rep['onset_fit']['tempo_bpm'], rep['onset_fit']['phase_s'] * 1000), tmax=DUR)
    dr = ImageDraw.Draw(img)
    for b in range(BARS + 1):
        xx = int(T(b) / DUR * (W - 1))
        dr.line([(xx, 44), (xx, H - 18)], fill=(255, 140, 40), width=1)
        if b < BARS:
            dr.text((xx + 3, 46), '%d %s' % (b, '/'.join(c for _, c in PLAN[b][0])), fill=(255, 200, 120))
    for a, b in (SILENCE_1, DROP_OUT):
        for t in (a, b):
            xx = int(t / DUR * (W - 1))
            dr.line([(xx, 60), (xx, H - 18)], fill=(80, 230, 255), width=1)
    img.save(path)


def _zooms(x, path):
    from PIL import Image, ImageDraw
    spans = [('hook 0-2.8 (frame-0 hit, accent 1.4)', 0.0, 2.8), ('tape stop + silence 11.6-14.6', 11.6, 14.6),
             ('drop-out + payoff 26.6-29.6', 26.6, 29.6),
             ('loop seam: 35.4-36.4 | 0-1.0', None, None)]
    W, H = 900, 360
    sheet = Image.new('RGB', (W * 2, H * 2), (0, 0, 0))
    for k, (lab, a, b) in enumerate(spans):
        if a is None:
            seg = np.concatenate([x[_n(DUR - 1.0):], x[:_n(1.0)]])
            off = DUR - 1.0
        else:
            seg, off = x[_n(a):_n(b)], a
        im = A.spectro_image(seg, W, H, 1.0 if a is None else None, lab,
                             't0 = %.2f s; orange ticks = beats%s' % (off, '; cyan = loop seam' if a is None else ''))
        dr = ImageDraw.Draw(im)
        dur = len(seg) / SR
        if a is None:                            # beats at 35.7 (local 0.3), 36.4 = 0 (local 1.0), 0.7 (local 1.7)
            ticks = [k * BEAT - (DUR - 1.0) for k in range(BARS * 4 + 1) if k * BEAT >= DUR - 1.0] + \
                    [1.0 + k * BEAT for k in range(2) if k * BEAT <= 1.0]
        else:
            ticks = [k * BEAT - a for k in range(BARS * 4 + 1) if a <= k * BEAT <= b]
        for tb in ticks:                         # dashed orange beat lines through waveform + spectrogram
            xx = int(min(tb / dur, 1.0) * (W - 1))
            for yy in range(44, H - 18, 8):
                dr.line([(xx, yy), (xx, min(yy + 3, H - 18))], fill=(255, 150, 50), width=1)
        sheet.paste(im, ((k % 2) * W, (k // 2) * H))
    sheet.save(path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', nargs='?', default='all', choices=['build', 'verify', 'all'])
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args()
    if a.cmd in ('build', 'all'):
        build(a.out)
    if a.cmd in ('verify', 'all'):
        verify(a.out)
