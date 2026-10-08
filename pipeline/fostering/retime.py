"""retime.py - voiceover versions of finished reels: slow the holds, keep the motion, lay the VO on top.

A VO module (pipeline/fostering/<reel>_vo.py) wraps a finished timeline module with a piecewise-linear time warp
(output time -> source time) built from SLOTS, one per voiceover beat:

    import retime
    import anim1 as M
    SLOTS = [
        dict(lines=['what_does'], at=0.0, delay=0.1, hold=(1.8, 2.3)),
        dict(lines=['often_found'], at=2.35, hold=(3.4, 5.0), tail=0.6),
        ...
        dict(lines=['make_room', 'start_enquiry'], at=18.9, hold=(19.4, 21.0), tail=1.6),   # end card
    ]
    retime.wrap(globals(), M, 'anim1', SLOTS)        # defines DUR, LOOK, BPM, BED, draw, post, samples, cues, ...

Slot keys (all times are SOURCE seconds of the wrapped module):
    lines       VO line ids from <WS>/vo/<piece>/lines.json (vo_tools.py split), spoken back to back (gap s apart)
    at          the on-screen event the VO belongs to (text lands / prop appears); VO starts at out(at) + delay
    hold        (a, b): span that may be slowed (rate >= min_rate) so the VO + tail ends before out(b). Holds are
                spans where the picture is (nearly) settled: slowing them reads as calm, not as slow motion.
    tail        settle/read time after the VO ends, before out(b) (default 0.45 s)
    min_hold    minimum OUTPUT length of the hold (reading time for copy the VO doesn't read), default 0
    min_rate    floor on the source speed inside the hold (default 0.12; ~0.5 where footage plays)
    gap         pause between consecutive lines inside the slot (default 0.18 s)
Everything outside the holds runs at rate 1, so slams, whips, cuts, tumbles and camera moves keep their timing.
Each hold's extension is rounded UP to whole beats (60 / BPM), so every source event moves by whole beats and the
edit stays on the module's BPM grid (music at the same tempo still locks).

Audio (python3 retime.py audio <reel>_vo): the module's SFX cues are re-mixed at their warped times (rhythmic
'interval' params scaled by the local slow-down) at -18 LUFS, ducked ~7 dB under the voice, the VO lines are placed
(each levelled to -16 LUFS), and the sum is mastered to -14 LUFS integrated, <= -2.0 dBTP:
    <WS>/audio/<reel>_vo_mix.wav       render with: python3 render.py <reel>_vo --audio <that wav> --workers 4
    <WS>/audio/<reel>_vo_vo_stem.wav   voice only (post master gain)   |  <reel>_vo_sfx_stem.wav  ducked SFX only
    <WS>/out/<reel>_vo/vo_cues.json    every line's out-time start/end and text (for QA)

    python3 retime.py plan  <reel>_vo     # warp table, holds (src -> out, rate), VO placement, warnings
    python3 retime.py audio <reel>_vo     # the mix + stems above
Film grain follows OUTPUT time (core.grain is clocked from post), so slowed holds keep live grain.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wsconf  # noqa: E402

WS = wsconf.workspace()


# ============================================================================================ warp
class Warp:
    """Strictly increasing map between output time and source time, built from (out, src) knots. smooth > 0 eases
    the speed changes at the knots over `smooth` seconds (raised-cosine on the rate, a speed ramp instead of a jolt);
    away from the knots (> smooth / 2) the mapping is exactly the piecewise-linear one.
    Warp([(0, 0), (2, 1), (3, 2)]).src(1.0) -> 0.5 ;  .out(1.5) -> 2.5 ;  .rate_out(1.0) -> 0.5"""

    def __init__(self, knots, smooth=0.0, step=0.001):
        k = np.asarray(sorted(knots), np.float64)
        if np.any(np.diff(k[:, 0]) <= 0) or np.any(np.diff(k[:, 1]) <= 0):
            raise ValueError('warp knots must be strictly increasing in both times')
        if smooth > 0 and len(k) > 2:
            to = np.arange(k[0, 0], k[-1, 0] + step / 2, step)
            seg = np.clip(np.searchsorted(k[:, 0], to, 'right') - 1, 0, len(k) - 2)
            rate = (k[seg + 1, 1] - k[seg, 1]) / (k[seg + 1, 0] - k[seg, 0])
            n = max(3, int(round(smooth / step)) | 1)
            ker = 0.5 - 0.5 * np.cos(2 * np.pi * (np.arange(n) + 0.5) / n)
            ker /= ker.sum()
            pad = n // 2
            r = np.convolve(np.pad(rate, pad, mode='edge'), ker, 'valid')
            src = k[0, 1] + np.concatenate([[0.0], np.cumsum(0.5 * (r[1:] + r[:-1]) * step)])
            src *= (k[-1, 1] - k[0, 1]) / (src[-1] - k[0, 1]) if src[-1] > k[0, 1] else 1.0
            k = np.stack([to, src], 1)
        self.o, self.s = k[:, 0], k[:, 1]

    def src(self, t):
        t = float(t)
        if t >= self.o[-1]:
            return float(self.s[-1] + (t - self.o[-1]))
        if t <= self.o[0]:
            return float(self.s[0] + (t - self.o[0]))
        return float(np.interp(t, self.o, self.s))

    def out(self, s):
        s = float(s)
        if s >= self.s[-1]:
            return float(self.o[-1] + (s - self.s[-1]))
        if s <= self.s[0]:
            return float(self.o[0] + (s - self.s[0]))
        return float(np.interp(s, self.s, self.o))

    def rate_out(self, t):
        """d(source)/d(output) at output time t."""
        i = int(np.clip(np.searchsorted(self.o, t, 'right') - 1, 0, len(self.o) - 2))
        return float((self.s[i + 1] - self.s[i]) / (self.o[i + 1] - self.o[i]))

    def rate_src(self, s):
        return self.rate_out(self.out(s))


# ============================================================================================ VO lines
def load_lines(piece):
    p = os.path.join(WS, 'vo', piece, 'lines.json')
    if not os.path.exists(p):
        raise FileNotFoundError('%s missing: run  <python with faster-whisper> vo_tools.py split %s' % (p, piece))
    return json.load(open(p))


def solve(slots, lines, src_dur, bpm=None, quantize=True, first_gap=0.15, smooth=0.24):
    """SLOTS + line durations -> (Warp, placed VO list, report rows). See the module docstring."""
    beat = 60.0 / bpm if (bpm and quantize) else None
    knots = [(0.0, 0.0)]
    cur_s = cur_o = 0.0
    prev_end = -1e9
    placed, rows = [], []

    def out_of(s):                      # out time for a source time already mapped (s <= cur_s)
        return Warp(knots + [(cur_o + 1e-9, cur_s + 1e-9)]).out(s) if s < cur_s else cur_o + (s - cur_s)

    for k, sl in enumerate(slots):
        a, b = map(float, sl['hold'])
        at = float(sl['at'])
        if a < cur_s - 1e-6 or b <= a:
            raise ValueError('slot %d: hold %s overlaps the previous hold or is empty' % (k, sl['hold']))
        if at > b:
            raise ValueError('slot %d: anchor %.3f after its hold end %.3f' % (k, at, b))
        if a > cur_s:                    # motion at rate 1 up to the hold
            cur_o += a - cur_s
            cur_s = a
            knots.append((cur_o, cur_s))
        ids = sl['lines'] if isinstance(sl['lines'], (list, tuple)) else [sl['lines']]
        gap = float(sl.get('gap', 0.18))
        durs = [float(lines[i]['dur']) for i in ids]
        D = sum(durs) + gap * (len(ids) - 1)
        d = float(sl.get('delay', 0.0))
        tail = float(sl.get('tail', 0.45))
        L, x = b - a, max(0.0, at - a)
        C = cur_o
        o_at_fixed = out_of(at) if at <= a else None
        P = prev_end + first_gap
        # stretch factor k >= 1: hold end out(b) = C + L*k must clear VO start + D + tail
        need = [1.0]
        if o_at_fixed is not None:
            vo0 = max(o_at_fixed + d, P)
            need.append((vo0 + D + tail - C) / L)
        else:
            if L - x > 1e-6:
                need.append((d + D + tail) / (L - x))
            need.append((P + D + tail - C) / L)
        if sl.get('min_hold'):
            need.append(float(sl['min_hold']) / L)
        kf = max(need)
        if beat:                         # round the extension up to whole beats
            ext = L * (kf - 1.0)
            if ext > 1e-6:
                kf = 1.0 + math.ceil(ext / beat - 1e-6) * beat / L
        kmax = 1.0 / float(sl.get('min_rate', 0.12))
        warn = ''
        if kf > kmax + 1e-9:
            warn = 'needs rate %.2f < min_rate %.2f: VO runs %.2fs past the hold' % (1 / kf, 1 / kmax, (kf - kmax) * L)
            kf = kmax if not beat else 1.0 + math.floor(L * (kmax - 1) / beat) * beat / L
        o_at = o_at_fixed if o_at_fixed is not None else C + x * kf
        vo0 = max(o_at + d, P)
        t = vo0
        for i, du in zip(ids, durs):
            placed.append(dict(line=i, text=lines[i]['text'], start=round(t, 3), end=round(t + du, 3),
                               file=lines[i]['file'], lufs=lines[i]['lufs']))
            t += du + gap
        prev_end = t - gap
        cur_o = C + L * kf
        cur_s = b
        knots.append((cur_o, cur_s))
        rows.append(dict(slot=k, lines=ids, src=(a, b), out=(round(C, 3), round(cur_o, 3)), rate=round(1 / kf, 3),
                         ext=round(L * (kf - 1), 3), vo=(round(vo0, 3), round(prev_end, 3)), warn=warn))
    if src_dur > cur_s:
        cur_o += src_dur - cur_s
        knots.append((cur_o, src_dur))
    if prev_end > cur_o - 0.5:
        rows.append(dict(slot='end', warn='last VO ends %.2fs before the end' % (cur_o - prev_end)))
    return Warp(knots, smooth=smooth), placed, rows


# ============================================================================================ wrapper
_CLOCK = {'t': None}


def _install_grain_clock():
    import core as K
    if getattr(K.grain, '_retime', False):
        return
    orig = K.grain

    def grain(canvas, t, amount=0.018, size=1.3):
        return orig(canvas, _CLOCK['t'] if _CLOCK['t'] is not None else t, amount, size)
    grain._retime = True
    K.grain = grain


def _warp_cue(c, warp):
    c = json.loads(json.dumps(c))
    s = float(c['t'])
    c['t'] = round(warp.out(s), 4)
    r = warp.rate_src(s)
    if r < 0.999:
        for d in (c, c.get('params') if isinstance(c.get('params'), dict) else None):
            if d is not None and 'interval' in d:
                d['interval'] = float(d['interval']) / r
    return c


def wrap(ns, M, piece, slots, quantize=True, **solve_kw):
    """Fill a VO module's namespace `ns` (pass globals()) from the wrapped module M."""
    import core as K
    lines = load_lines(piece)
    warp, placed, rows = solve(slots, lines, float(M.DUR), getattr(M, 'BPM', None), quantize, **solve_kw)
    _install_grain_clock()
    src_post = getattr(M, 'post', None)
    look = getattr(M, 'LOOK', 'neon')

    def draw(t):
        return M.draw(warp.src(t))

    def post(cv, t):
        _CLOCK['t'] = t
        s = warp.src(t)
        return src_post(cv, s) if src_post else K.post(cv, look, s)

    def samples(t):
        return M.samples(warp.src(t)) if hasattr(M, 'samples') else 3

    def cues():
        out = []
        for c in (M.cues() if hasattr(M, 'cues') else []):
            pr = c.get('params') if isinstance(c.get('params'), dict) else c
            if 'n' in pr and 'interval' in pr and int(pr['n']) > 1:     # rhythmic multi-hit cue -> one cue per hit
                n, iv = int(pr['n']), float(pr['interval'])
                for i in range(n):
                    ci = json.loads(json.dumps(c))
                    pi = ci['params'] if isinstance(ci.get('params'), dict) else ci
                    pi['n'] = 1
                    ci['t'] = float(c['t']) + i * iv
                    out.append(_warp_cue(ci, warp))
            else:
                out.append(_warp_cue(c, warp))
        return out

    def prewarm():
        if hasattr(M, 'prewarm'):
            M.prewarm()

    def vo_cues():
        return placed

    ns.update(DUR=round(warp.o[-1], 4), LOOK=look, BPM=getattr(M, 'BPM', None), BED=getattr(M, 'BED', None),
              BED_GAIN_DB=getattr(M, 'BED_GAIN_DB', -30.0), WARP=warp, VO=placed, PLAN=rows, SRC=M, PIECE=piece,
              draw=draw, post=post, samples=samples, cues=cues, prewarm=prewarm, vo_cues=vo_cues,
              src_time=warp.src, out_time=warp.out)
    return warp


# ============================================================================================ audio
def _env(active, sr, attack=0.06, release=0.35):
    """0..1 smoothed activity envelope from a boolean sample mask (one-pole attack / release)."""
    from scipy.signal import lfilter
    x = active.astype(np.float64)
    ka, kr = 1 - math.exp(-1 / (attack * sr)), 1 - math.exp(-1 / (release * sr))
    up = lfilter([ka], [1, -(1 - ka)], x)                 # fast rise
    env = np.maximum(up, 0)
    # release: running max decayed with kr
    out = np.empty_like(env)
    v = 0.0
    step = 64
    for i in range(0, len(env), step):
        blk = env[i:i + step]
        v = max(float(blk.max()), v * (1 - kr) ** step)
        out[i:i + step] = v
    return np.clip(out, 0, 1)


def build_audio(name, target_lufs=-14.0, tp_ceiling=-2.0, vo_lufs=-16.0, duck_db=-7.0, sfx_tp=-2.3, verbose=True):
    import importlib
    import audio as A
    from scipy.io import wavfile
    mod = importlib.import_module(name)
    sr = A.SR
    dur = float(mod.DUR)
    N = int(round(dur * sr))
    os.makedirs(A.AUDIO, exist_ok=True)
    out_dir = os.path.join(A.OUT, name)
    os.makedirs(out_dir, exist_ok=True)
    # ---- SFX at warped times (custom sounds register when the wrapped module's cues() / sfx module import)
    rep = A.mix(mod.cues(), dur, os.path.join(A.AUDIO, name + '_sfxonly.wav'), None, bed=mod.BED,
                bed_gain_db=mod.BED_GAIN_DB, tp_ceiling=sfx_tp, verbose=False)
    sfx = A._st(np.asarray(rep['audio'], np.float64))[:N]
    sfx = np.pad(sfx, ((0, N - len(sfx)), (0, 0)))
    # ---- VO bus
    vo = np.zeros((N, 2))
    active = np.zeros(N, bool)
    for p in mod.VO:
        fsr, y = wavfile.read(p['file'])
        y = y.astype(np.float64)
        if y.ndim > 1:
            y = y.mean(1)
        if fsr != sr:
            from scipy.signal import resample_poly
            y = resample_poly(y, sr, fsr)
        g = A.undb(float(np.clip(vo_lufs - p['lufs'], -9, 9)))
        i0 = int(round(p['start'] * sr))
        n = min(len(y), N - i0)
        if n <= 0:
            continue
        vo[i0:i0 + n] += (y[:n] * g)[:, None]
        rms = np.sqrt(np.convolve(y[:n] ** 2, np.ones(480) / 480, 'same'))
        active[i0:i0 + n] |= rms > 10 ** (-45 / 20)
    env = _env(active, sr)
    sfx_d = sfx * (1 - (1 - A.undb(duck_db)) * env)[:, None]
    # ---- master: gain G, true-peak limiter, iterate
    mix = vo + sfx_d
    G = target_lufs - A.loudness(mix)
    ceil = tp_ceiling - 0.3
    for _ in range(6):
        pk = A.tp_envelope(mix * A.undb(G))
        gl = A.limiter_gain(None, ceil, pk=pk)
        y = mix * A.undb(G) * gl[:, None]
        L, tp = A.loudness(y), A.true_peak(y)
        if abs(L - target_lufs) < 0.05 and tp <= tp_ceiling - 0.05:
            break
        G += target_lufs - L
        if tp > tp_ceiling - 0.05:
            ceil -= tp - (tp_ceiling - 0.1)
    vo_out = vo * A.undb(G) * gl[:, None]
    sfx_out = sfx_d * A.undb(G) * gl[:, None]
    fade = np.ones(N)
    nf = int(0.25 * sr)
    fade[-nf:] = np.linspace(1, 0, nf) ** 2
    y, vo_out, sfx_out = y * fade[:, None], vo_out * fade[:, None], sfx_out * fade[:, None]
    files = {}
    for key, arr in (('mix', y), ('vo_stem', vo_out), ('sfx_stem', sfx_out)):
        files[key] = A._write_wav(os.path.join(A.AUDIO, '%s_%s.wav' % (name, key)), arr, 24)
    vo_act = active
    rep2 = dict(name=name, dur=dur, integrated_lufs=round(A.loudness(y), 2), true_peak_dbtp=round(A.true_peak(y), 2),
                lra_lu=round(A.loudness_range(y), 2), vo_lufs=round(A.loudness(vo_out), 2),
                sfx_lufs_under_vo=round(A.loudness(sfx_out[vo_act]) if vo_act.any() else -120, 2),
                sfx_lufs_gaps=round(A.loudness(sfx_out[~vo_act]) if (~vo_act).any() else -120, 2),
                limiter_max_gr_db=round(float(-A.db(np.min(gl))), 2), files=files, vo=mod.VO)
    json.dump(dict(name=name, dur=dur, lines=mod.VO), open(os.path.join(out_dir, 'vo_cues.json'), 'w'), indent=1)
    if verbose:
        print('%s: %.2f LUFS  %.2f dBTP  LRA %.1f  | VO %.1f LUFS, SFX under VO %.1f, SFX in gaps %.1f  | limiter %.1f dB'
              % (name, rep2['integrated_lufs'], rep2['true_peak_dbtp'], rep2['lra_lu'], rep2['vo_lufs'],
                 rep2['sfx_lufs_under_vo'], rep2['sfx_lufs_gaps'], rep2['limiter_max_gr_db']))
        for k, v in files.items():
            print('   %-9s %s' % (k, v))
    return rep2


def plan(name):
    import importlib
    mod = importlib.import_module(name)
    print('%s: source %.2fs -> %.2fs (x%.2f), BPM %s' % (name, mod.SRC.DUR, mod.DUR, mod.DUR / mod.SRC.DUR, mod.BPM))
    for r in mod.PLAN:
        if r.get('slot') == 'end':
            print('  END  %s' % r['warn'])
            continue
        print('  slot %2d  src %6.2f-%6.2f -> out %6.2f-%6.2f  rate %.2f  +%.2fs | VO %6.2f-%6.2f %s %s' % (
            r['slot'], r['src'][0], r['src'][1], r['out'][0], r['out'][1], r['rate'], r['ext'], r['vo'][0], r['vo'][1],
            ','.join(r['lines']), ('  !! ' + r['warn']) if r['warn'] else ''))
    return mod.PLAN


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'plan':
        plan(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == 'audio':
        build_audio(sys.argv[2])
    else:
        print(__doc__)
