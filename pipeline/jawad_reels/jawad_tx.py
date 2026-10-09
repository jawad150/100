"""jawad_tx.py - Jawad's shared transition kit: the foundations of the transitions bible (section 2: frame grid,
eases, springs, the cut rule, finish) and its 43-transition catalogue (section 3), with code for the 10 premium
(C2 C3 M1 M6 Y1 Y5 L1 L4 L7 O6), the 5 editor-signature (D1 D2 D3 D4 D9), every family-allocation signature
(Y3 O4) and glue (L3), plus extras (C1 C6 C8 M2 M3 Y2 L2 L5 L8 D7 D8 O1 O2): 31 of 43; the other 12 are spec rows.
Spec: brand_reels/research/transitions_sound_music_bible.md.

    import jawad_kit                                  # FIRST (looks, house type)
    import jawad_tx as X

SCENES AND TIME
    A scene is a PURE function S(t) -> NEW canvas (linear premultiplied float32 (H, W, 4)); a transition may draw
    into what the scene returns. Both scenes run on the reel's global clock ("B is already running"): a
    transition only ever asks a scene for some t, so time tricks (scrub, rewind, speed ramp) cost nothing.
    The cut rule (bible 2.4): frame k relative to the cut c is floor((t - c) * 30 + 0.5); with render.py's
    180-degree shutter every sub-sample of frame k lands on the same side, so motion blur never crosses a cut:
    side_b(t, c) = t + HALF >= c  (HALF = 0.5 / 30)  -> frame c is all B, frame c - 1 all A.

TRANSITIONS  (TX[id] -> Tx; every Tx is a pure function of t)
    tx = X.TX['L1']                         # or X.tx('L1')
    cv = tx(t, c, A, B, **opts)             # A before the window, B after it, the transition inside it
    tx.pre, tx.post                         # default window in FRAMES at 30 fps before / after the cut c
    tx.window(c, **opts) -> (t0, t1)        # [t0, t1) in seconds; frames(c) -> list of frame times
    tx.samples_at(t, c, default=3, **opts)  # motion-blur sub-samples for this frame (7 on whips / zooms ...);
                                            # a policy callable is s(k, w) or s(k, w, opts) (D1 reads pull=)
    tx.cues(c, **opts) -> [cue dicts]       # paired SFX on audio.py catalog names (hit-aligned); each carries
                                            # 'tx' and, where the bible wants a custom jawad_sfx sound, 'alt'
    tx.post_kw(t, c, **opts) -> dict        # finish() overrides: push (exposure push), bloomout, rgb_split
    tx.ease, tx.family, tx.flag ('premium' | 'editor' | 'glue' | ''), tx.frames_range (bible), tx.implemented
    X.catalogue() -> rows for all 43 (spec-only rows have fn None; calling them raises NotImplementedError)
    Window options every Tx takes: pre=, post= (frames).  Per-transition options: see each _tx_* docstring
    (e.g. X.TX['C3'](t, c, A, B, center=(540, 700), r0=220)).
    WINDOW EDGES: frames outside a window are the plain scenes, so every envelope reaches its end value ON the
    first / last window frame (Win.u / ua1 / ub / env_in / env_out, see Win): nothing pops in or vanishes at a
    window edge. What the TIMELINE draws outside a window: Y1 / Y2 the word on A, M6 the carrier at rest
    (X.carrier() at path[0] / path[-1]), M3 the object on X.motion_track(c)(t).

CONTINUITY QA
    X.edge_steps('O6', c=1.0, pre=10, post=5) -> {'entry': (mean, frac), 'exit': ..., 'base_a', 'base_b'}: the step
    from the plain neighbour into the first window frame and from the last window frame out, against the
    plain-scene step (X.frame_step(a8, b8) = mean |diff| of two sRGB8 frames, share of px changing > 25 levels;
    post_kw=True adds each frame's finish overrides). The self-test fails an edge over 1.5x the plain step.
    X.window_steps('Y5') -> {'steps': {k: (mean, frac)} for EVERY frame of the window, 'entry', 'exit', 'base_a',
    'base_b', 'spikes'}: X.window_spikes flags a step > 3x the plain step and > 2x BOTH neighbouring steps (mean, or
    share of px > 25 with a 2 % floor), skipping the cut (k = -1, 0), EDGE_CUTS and X.designed_steps(tid, w, **o)
    (SNAPS: C8 punch, Y3 slams, L8 re-open, D3 stepped track, D1 scrub). The self-test fails any spike and writes
    the whole table to <WS>/out/selftest/jawad_tx_window_steps.log. X.y5_handover() = Y5's underline ROI luma
    per frame at 5 samples (the hand-over check: no step > 1.5x both neighbours on k = -16 .. -10).

PLAN (timeline glue: several transitions between consecutive scenes)
    plan = X.Plan([('C3', 2.0, dict(center=(540, 720), r0=200)), ('L1', 4.0), ('D9', 6.2)])
    draw(t)    = plan.draw(t, [S0, S1, S2, S3])     # scene i runs between cut i-1 and cut i
    samples(t) = plan.samples(t)                    # 3 outside windows, the transition's policy inside
    post(cv,t) = X.finish(cv, t, LOOK, **plan.post_kw(t))      # exposure pushes etc. (the ONLY post call)
    cues()     = plan.cues()                        # paired SFX for every transition
    Windows must not overlap (ValueError). plan.cuts, plan.windows(), plan.segment(t),
    plan.windows_of('L1', 'L4') -> [(t0, t1)] (caption clear windows: SC.Captions(..., clear=plan)).

FOUNDATIONS
    FPS, HALF, q(t) quantise to a frame, fidx(t, c=0) frame index, side_b(t, c), f(n) frames -> s
    Grid(bpm, offset=0): .fpb .fpbar .locked .B(n) .BAR(n) .at(bar, beat=0, sub=0) (frame-quantised s)
    TEMPOS {bpm: (frames/beat, frames/bar, use)} (bible 2.1);  SPRINGS {SLAM POP SETTLE SNAP JELLY: (freq, damp)}
    spring(t, 'POP') = K.spring(t, *SPRINGS['POP']);  EMBERS() -> (FLAME, RED, AMBER) linear
    mix_mask(a, b, m) a*(1-m) + b*m in place on a; up(m) 1/4-res -> full; up2(m) 1/2-res -> full
    grid4() / grid2() read-only full-res px coordinates of each 1/4 (1/2) res pixel centre
    zoom_canvas(cv, s, center=(CX, CY), border='reflect'|'wrap'|'constant'|'night'); shift_canvas(cv, dx, dy, border)
    affine_canvas(cv, M, border) any 2x3 affine; fbm(seed, scale, octaves) static 1/4-res noise 0..1 (read-only)
    sweep_mask(u, angle=35, soft=0.06) mask matching K.light_leak(sweep=u, angle) (1 = swept -> show B)
    push_at(t, cuts, decay=16) exposure-push envelope (cuts: floats or (c, gain)); windows_samples(t, windows)
    finish(cv, t, look, cuts=(), push=0, bloomout=0, rgb_split=0, **post_overrides) -> K.post with the bible's
        exposure push (exposure += 1.4 p, bloom *= 1 + 0.9 p; multiplicative: blacks never lift), the L4
        bloom-out and the D7 channel split. Never use K.flash / K.fade / post(flash=) (they lift the blacks).
    raw_log(cv) a flat 'LOG' version of a frame (D3 before-state);  hue_bridge(cv, k) (M2);  desat(cv, k)
    full_frame_alpha(ts, x, y, anchor, scale) alpha of a TextSprite placed on the canvas
    dolly_cam(t, t0, t1, D0, D1, subj_z) the bible's C2 camera; warp(t, c, w, peak) D8 speed-ramp clock
    leak_coverage(...) fraction of the frame an L1 leak covers at its peak (QA: >= 0.70 for an invisible cut)
    SFX names: every 'name' is in audio.names(); X.check_cues(cues) -> unknown names.

CHOOSING (bible 3.0): one family per reel, no two reels share a family or signature device; at most 4 feature
transitions per reel (at most 2 premium), never two features within 2 bars; the rest are beat cuts + L3 push.
Y5 as a full wipe in ONE reel only. L1 sparingly (Jawad disliked light-leak washes on cuts).

COST (measured by the self-test: shared 4-core box, warm caches, one sample, scenes excluded, median per frame):
C1 21, C2 110-140 (the L1 leak recipe since fix round 1), C3 33, C6 17, C8 44, M1 10, M2 72, M6 32, Y1 186, Y2 115,
Y3 340 (hit frame ~40; ~1.1 s on the 1-2 frames after each hit: 24-sub-sample smear), Y5 38, L1 104, L2 64, L5 31,
L7 72, L8 72, D1 35 (+ ~40 on pull / push frames: zoom smear), D2 60, D3 22, D4 134, O1 121, O2 107, O4 20 (+ shard build once), O6 68 ms; L3 L4 D7 D8
M3 D9 cost nothing here (their work is in finish() or the scene clock). Inside a window both scenes render and
samples rise to 5-7: budget 2-4x a normal frame there.
Self-test: python3 jawad_tx.py selftest  (or --selftest) -> <WS>/out/selftest/jawad_tx_*.png, exits 1 on failure.
"""
import functools
import math
import os
import sys
import time

import cv2
import numpy as np

import jawad_kit
from jawad_kit import K, T, ui, J

FPS = K.FPS
HALF = 0.5 / FPS
W, H = K.W, K.H
W4, H4 = W // 4, H // 4
W2, H2 = W // 2, H // 2


# =============================================================================================== grid + timing
def q(t):
    """Quantise a time to the frame grid.  q(1.01) -> 1.0"""
    return round(t * FPS) / FPS


def f(n):
    """Frames -> seconds.  f(8) -> 0.2667"""
    return n / FPS


def fidx(t, c=0.0):
    """Frame index of t relative to c (sub-samples of a frame map to that frame).  fidx(c - 1/30, c) -> -1"""
    return int(math.floor((t - c) * FPS + 0.5))


def side_b(t, c):
    """True on the incoming side of a cut at c (bible 2.4: t + HALF >= c).  side_b(c, c) -> True"""
    return t + HALF >= c


# frame-locked tempos (bible 2.1): bpm -> (frames per beat, frames per bar, use)
TEMPOS = {72: (25, 100, 'grief, intimate confession'), 75: (24, 96, 'emotional; fully locked to 16ths'),
          80: (22.5, 90, 'warm nostalgia'), 90: (20, 80, 'storytelling (default); fully locked'),
          96: (18.75, 75, 'lofi-hop storytelling'), 100: (18, 72, 'cinematic drive, aspiration'),
          112.5: (16, 64, 'montage, craft reveal; fully locked'), 120: (15, 60, 'upbeat, SaaS'),
          150: (12, 48, 'hype; same grid as 75')}


class Grid:
    """Beat grid on whole frames (bible 2.1).  g = X.Grid(90); g.at(2, 1) -> start of bar 2 beat 1 (s, on a frame)
    g.fpb (frames per beat), g.fpbar, g.locked (beats land on whole frames), g.B(n), g.BAR(n), g.q(t)."""

    def __init__(self, bpm, offset=0.0):
        self.bpm, self.offset = float(bpm), float(offset)
        self.fpb = FPS * 60.0 / self.bpm
        self.fpbar = 4 * self.fpb
        self.locked = abs(self.fpb - round(self.fpb)) < 1e-9

    def B(self, n):
        """Beat n -> s (not quantised)."""
        return self.offset + n * 60.0 / self.bpm

    def BAR(self, n):
        return self.B(4 * n)

    def at(self, bar, beat=0, sub=0.0):
        """'bar.beat(+sub beats)' -> seconds, quantised to a frame."""
        return q(self.BAR(bar) + (beat + sub) * 60.0 / self.bpm)

    q = staticmethod(q)

    def bars_for(self, dur_s):
        return dur_s * self.bpm / 240.0


SPRINGS = {'SLAM': (3.2, 0.45), 'POP': (2.6, 0.50), 'SETTLE': (1.6, 0.70), 'SNAP': (3.0, 0.55), 'JELLY': (4.0, 0.30)}


def spring(t, preset='POP'):
    """Bible 2.3 spring presets: X.spring(t - t0, 'SLAM') -> 0..1 with overshoot (JELLY never on brand type)."""
    fr, dz = SPRINGS[preset]
    return K.spring(t, fr, dz)


def EMBERS():
    """Leak / flare colours (linear): FLAME, RED, AMBER."""
    return (K.C['FLAME'], K.C['RED'], K.C['AMBER'])


def LEAK_COLS():
    """L1 burn colours (deeper than EMBERS so the peak reads ember, not white): FLAME, RED, EMBER."""
    return (K.C['FLAME'], K.C['RED'], K.C['EMBER'])


# =============================================================================================== pixel helpers
def mix_mask(a, b, m):
    """a * (1 - m) + b * m, IN PLACE on a (premultiplied, so masks never fringe). m (H, W) or (H, W, 1)."""
    mm = m[..., None] if m.ndim == 2 else m
    b = np.asarray(b, np.float32)
    a += (b - a) * mm
    return a


def up(m):
    """1/4-res mask -> full res (bilinear)."""
    return cv2.resize(np.ascontiguousarray(m, np.float32), (W, H), interpolation=cv2.INTER_LINEAR)


def up2(m):
    """1/2-res mask -> full res (bilinear)."""
    return cv2.resize(np.ascontiguousarray(m, np.float32), (W, H), interpolation=cv2.INTER_LINEAR)


@functools.lru_cache(maxsize=1)
def grid4():
    """Full-res px coordinates (X, Y) of each 1/4-res pixel centre (cached, read-only)."""
    xs = (np.arange(W4, dtype=np.float32) + 0.5) * 4 - 0.5
    ys = (np.arange(H4, dtype=np.float32) + 0.5) * 4 - 0.5
    X, Y = np.meshgrid(xs, ys)
    X.flags.writeable = False
    Y.flags.writeable = False
    return X, Y


@functools.lru_cache(maxsize=1)
def grid2():
    """Full-res px coordinates (X, Y) of each 1/2-res pixel centre (cached, read-only)."""
    xs = (np.arange(W2, dtype=np.float32) + 0.5) * 2 - 0.5
    ys = (np.arange(H2, dtype=np.float32) + 0.5) * 2 - 0.5
    X, Y = np.meshgrid(xs, ys)
    X.flags.writeable = False
    Y.flags.writeable = False
    return X, Y


_BORDERS = {'reflect': cv2.BORDER_REFLECT101, 'wrap': cv2.BORDER_WRAP, 'constant': cv2.BORDER_CONSTANT,
            'night': cv2.BORDER_CONSTANT}


def affine_canvas(cv, M, border='reflect'):
    """Warp a full canvas by a 2x3 affine (dst = M @ src). border 'night' fills with opaque NIGHT_0."""
    val = 0
    if border == 'night':
        n = K.C['NIGHT_0']
        val = (float(n[0]), float(n[1]), float(n[2]), 1.0)
    return cv2.warpAffine(cv, np.float32(M), (cv.shape[1], cv.shape[0]), flags=cv2.INTER_LINEAR,
                          borderMode=_BORDERS[border], borderValue=val)


def zoom_canvas(cv, s, center=(K.CX, K.CY), border='reflect'):
    """Scale a finished canvas by s about a screen point.  X.zoom_canvas(cv, 1.08)"""
    if abs(s - 1) < 1e-6:
        return cv
    M = [[s, 0, (1 - s) * center[0]], [0, s, (1 - s) * center[1]]]
    return affine_canvas(cv, M, border)


def shift_canvas(cv, dx, dy=0.0, border='wrap'):
    """Translate a canvas (sub-pixel).  X.shift_canvas(cv, -300) (wrap keeps a plate continuous, no mirroring)"""
    if abs(dx) < 1e-3 and abs(dy) < 1e-3:
        return cv
    return affine_canvas(cv, [[1, 0, dx], [0, 1, dy]], border)


@functools.lru_cache(maxsize=16)
def fbm(seed=0, scale=6.0, octaves=4):
    """Static 1/4-res fractal noise in 0..1 (cached, read-only).  n = X.up(X.fbm(11, scale=5))"""
    rng = np.random.default_rng(seed)
    acc = np.zeros((H4, W4), np.float32)
    a = 1.0
    for o in range(octaves):
        n = rng.standard_normal((int(H4 / scale * 2 ** o) + 2, int(W4 / scale * 2 ** o) + 2)).astype(np.float32)
        acc += a * cv2.resize(n, (W4, H4), interpolation=cv2.INTER_CUBIC)
        a *= 0.5
    acc = (acc - acc.min()) / max(1e-6, float(acc.max() - acc.min()))
    acc.flags.writeable = False
    return acc


def sweep_mask(u, angle=35.0, soft=0.06):
    """Full-res mask of a band position identical to K.light_leak(sweep=u, angle): 1 = already swept (B)."""
    X, Y = grid4()
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    proj = (X - K.CX) * dx + (Y - K.CY) * dy
    ext = abs(K.CX * dx) + abs(K.CY * dy)
    pos = (u * 2.6 - 1.3) * ext
    return up(np.clip((pos - proj) / (soft * ext * 2) + 0.5, 0, 1))


def push_at(t, cuts, decay=16.0):
    """Exposure-push envelope: sum of K.impulse peaking on each cut (cuts: floats or (c, gain))."""
    p = 0.0
    for c in cuts or ():
        g = 1.0
        if isinstance(c, (tuple, list)):
            c, g = c[0], c[1]
        p += g * K.impulse(t, c - 0.02, decay)
    return p


def windows_samples(t, windows, default=3):
    """max n over [(a, b, n)] windows containing t (bible 2.4)."""
    return max([n for a, b, n in windows if a <= t <= b], default=default)


def desat(cv, k):
    """Desaturate towards luminance by k (in place)."""
    if k <= 0:
        return cv
    L = K.lum(cv[..., :3])[..., None]
    cv[..., :3] += (L - cv[..., :3]) * np.float32(k)
    return cv


def raw_log(cv, desat_k=0.7, pivot=0.20, contrast=0.45, lift=0.035):
    """A flat 'LOG / ungraded' version of a frame (the D3 before-state), in place: desaturated, low contrast."""
    desat(cv, desat_k)
    rgb = cv[..., :3]
    rgb -= pivot
    rgb *= contrast
    rgb += pivot
    np.maximum(rgb, lift, out=rgb)
    return cv


def hue_bridge(cv, k, gain=1.6):
    """M2 colour bridge: blend the frame towards FLAME-tinted luminance by k (in place)."""
    if k <= 0:
        return cv
    L = K.lum(cv[..., :3])[..., None]
    cv[..., :3] += (L * (K.C['FLAME'] * gain) - cv[..., :3]) * np.float32(k)
    return cv


def _rgb_split(cv, amount):
    """D7: shift R by +k px and B by -k px (RGB only, premultiplied-safe), scale 1 + 0.03 * amount."""
    k = 18.0 * amount
    if k < 0.3:
        return cv
    s = 1.0 + 0.03 * amount
    for ch, dx in ((0, k), (2, -k)):
        M = np.float32([[s, 0, (1 - s) * K.CX + dx], [0, s, (1 - s) * K.CY]])
        cv[..., ch] = cv2.warpAffine(np.ascontiguousarray(cv[..., ch]), M, (W, H), flags=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_REFLECT101)
    return cv


def finish(cv, t, look, cuts=(), push=0.0, bloomout=0.0, rgb_split=0.0, push_decay=16.0, bloom_scale=1.0, **kw):
    """The ONLY post call in a reel module (bible 2.5): K.post(cv, look, t) with
    exposure push p = push + push_at(t, cuts): exposure += 1.4 p, bloom *= 1 + 0.9 p (multiplicative, blacks stay);
    bloomout k (L4): bloom -> 2.8, threshold -> 0.12, halation -> 0.9, exposure +0.6 k, vignette +0.17 k;
    rgb_split (D7): channel offset + radial chroma; bloom_scale multiplies the look's bloom (L1 halves it at
    its peak so the leak does not bloom into a full-frame wash).  Other kw go to K.post.
        def post(cv, t): return X.finish(cv, t, LOOK, cuts=CUTS, **plan.post_kw(t))"""
    cfg = K.LOOKS.get(look, {})
    p = float(push) + push_at(t, cuts, push_decay)
    b = float(kw.pop('bloom', cfg.get('bloom', 0.55))) * float(bloom_scale)
    e = float(kw.pop('exposure', cfg.get('exposure', 0.0)) or 0.0)
    if bloomout > 0:
        k = float(min(1.0, bloomout))
        kw.setdefault('bloom_threshold', K.lerp(cfg.get('bloom_threshold', 0.45), 0.12, k))
        kw.setdefault('halation', K.lerp(cfg.get('halation', 0.16), 0.9, k))
        kw.setdefault('vignette', cfg.get('vignette', 0.45) + 0.17 * k)
        b = K.lerp(b, 2.8, k)
        e += 0.6 * k
    if rgb_split > 0:
        _rgb_split(cv, float(rgb_split))
        kw['chroma'] = kw.get('chroma', cfg.get('chroma', 1.2)) + 14.0 * float(rgb_split)
    return K.post(cv, look, t, exposure=e + 1.4 * p, bloom=b * (1 + 0.9 * p), **kw)


def full_frame_alpha(ts, x, y, anchor=(0.5, 0.5), scale=1.0):
    """(H, W) alpha of a TextSprite drawn at (x, y) (only its 'front' layers)."""
    tmp = np.zeros((H, W, 4), np.float32)
    ts.draw(tmp, x, y, anchor=anchor, scale=scale, parts=('front',))
    return tmp[..., 3]


def dolly_cam(t, t0, t1, D0=1500.0, D1=640.0, subj_z=0.0, ap=(18.0, 46.0)):
    """Bible C2 camera: dolly D0 -> D1 with focal = 1500 * D / D0 (subject size constant), easy_ease."""
    u = K.EASE['easy_ease'](K.ramp(t, t0, t1, 'linear'))
    D = K.lerp(D0, D1, u)
    return K.Cam(pos=(0, 0, subj_z - D), focal=1500.0 * D / D0, focus_dist=D, aperture=K.lerp(ap[0], ap[1], u))


def _speed_extra(t, c, w, peak, n=96):
    if t <= c - w:
        return 0.0
    ts = np.linspace(c - w, min(t, c + w), n)
    u = (ts - (c - w)) / w
    sp = np.array([K.EASE['in_expo'](x) if x < 1 else 1 - K.EASE['out_expo'](x - 1) for x in u])
    return float(np.trapezoid((peak - 1) * sp, ts)) if hasattr(np, 'trapezoid') else float(np.trapz((peak - 1) * sp, ts))


def warp(t, c, w=0.25, peak=6.0):
    """D8 scene clock with a speed bump centred on c (1x -> peak (in_expo) -> 1x (out_expo)); continuous and
    pure. A(warp(t, c)) before the cut; B uses warp(t, c) - X.warp_total(c, w, peak) (continuous after it)."""
    return t + _speed_extra(t, c, w, peak)


def warp_total(c, w=0.25, peak=6.0):
    return _speed_extra(c + w, c, w, peak)


def _src(name, a=0.0):
    return np.float32(K.C[name]) * np.float32(a) if a else np.float32(K.C[name])


def _gl(m, sigmas, weights):
    """Sum of gaussian blurs of a 2D mask (glow profile)."""
    acc = None
    for s, wgt in zip(sigmas, weights):
        g = cv2.GaussianBlur(m, (0, 0), s) * np.float32(wgt)
        acc = g if acc is None else acc + g
    return acc


def _add_rgb(cv, m, col, gain=1.0):
    """cv.rgb += m (H, W) * col * gain (emissive, alpha untouched)."""
    cv[..., :3] += m[..., None] * (np.asarray(col, np.float32) * np.float32(gain))
    return cv


def _emit(cv, m, col, gain=1.0, f=4, thr=1e-4, off=(0, 0)):
    """Add an emissive low-res mask (1/f res, placed at low-res offset `off`) to the canvas, upsampling only its
    non-zero bounding box."""
    rows = np.nonzero(m.max(1) > thr)[0]
    if len(rows) == 0 or gain == 0:
        return cv
    cols = np.nonzero(m.max(0) > thr)[0]
    y0, y1 = max(0, rows[0] - 2), min(m.shape[0], rows[-1] + 3)
    x0, x1 = max(0, cols[0] - 2), min(m.shape[1], cols[-1] + 3)
    sub = np.ascontiguousarray(m[y0:y1, x0:x1], np.float32)
    big = cv2.resize(sub, ((x1 - x0) * f, (y1 - y0) * f), interpolation=cv2.INTER_LINEAR)
    Y0, X0 = (y0 + int(off[1])) * f, (x0 + int(off[0])) * f
    if Y0 < 0 or X0 < 0:
        big = big[max(0, -Y0):, max(0, -X0):]
        Y0, X0 = max(0, Y0), max(0, X0)
    hh, ww = min(big.shape[0], cv.shape[0] - Y0), min(big.shape[1], cv.shape[1] - X0)
    reg = cv[Y0:Y0 + hh, X0:X0 + ww, :3]
    reg += big[:hh, :ww, None] * (np.asarray(col, np.float32) * np.float32(gain))
    return cv


def _over_affine(cv, spr, M):
    """Premultiplied 'over' of a sprite warped by a 2x3 affine (no sprite cache churn; bbox-limited)."""
    h, w = spr.shape[:2]
    M = np.asarray(M, np.float64)
    corners = np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], np.float64) @ M.T
    x0, y0 = np.floor(corners.min(0)).astype(int) - 1
    x1, y1 = np.ceil(corners.max(0)).astype(int) + 1
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(cv.shape[1], x1), min(cv.shape[0], y1)
    if x1 <= x0 or y1 <= y0:
        return None
    M2 = M.copy()
    M2[0, 2] -= x0
    M2[1, 2] -= y0
    out = cv2.warpAffine(spr, np.float32(M2), (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    reg = cv[y0:y1, x0:x1]
    reg *= (1.0 - out[..., 3:4])
    reg += out
    return (x0, y0, x1, y1)


@functools.lru_cache(maxsize=2)
def _frozen(scene, t):
    """A scene frame held still (impact frames for O4, the source of O6 particles). Cached, read-only."""
    cv = scene(t)
    cv.flags.writeable = False
    return cv


def wide_band(cv, u, angle=35.0, strength=0.25, width=3.2, power=4.0):
    """A broad, soft ember wash travelling with K.light_leak(sweep=u, angle) (same band position, `width` x
    wider, screen blend, sin(pi u) ** power envelope: it only blooms for the 2-4 frames around the cut): widens
    L1's cover to >= 70 % of the frame at the cut without washing the whole window."""
    if strength <= 0:
        return cv
    lw, lh = W // 8, H // 8
    xs = (np.arange(lw, dtype=np.float32) + 0.5) * 8
    ys = (np.arange(lh, dtype=np.float32) + 0.5) * 8
    X, Y = np.meshgrid(xs, ys)
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    proj = (X - K.CX) * dx + (Y - K.CY) * dy
    ext = abs(K.CX * dx) + abs(K.CY * dy)
    pos = (u * 2.6 - 1.3) * ext
    d = (proj - pos) / (ext * 0.42 * width)
    env = math.sin(math.pi * K.clamp(u)) ** power * strength
    if env < 0.003:
        return cv
    g = np.exp(-d * d * 2.0) * env
    col = np.float32(K.C['EMBER']) * 0.5 + np.float32(K.C['FLAME']) * 0.9
    upm = cv2.resize(g.astype(np.float32), (cv.shape[1], cv.shape[0]), interpolation=cv2.INTER_CUBIC)
    np.maximum(upm, 0, out=upm)
    rgb = cv[..., :3]
    rgb += upm[..., None] * col * (1.0 - np.clip(rgb, 0, 1))
    return cv


def leak_coverage(seed=0, angle=35.0, strength=0.6, wide=0.25, thr=0.06):
    """QA for L1: fraction of a black frame the ember leak (+ its wide band) lifts above `thr` (linear, 0.06 ~
    sRGB 70/255, several times the ember void) at its peak (u = 0.5). The bible asks >= 0.70 for an invisible cut;
    the defaults give ~0.80 without washing the frame out (Jawad disliked leak washes)."""
    cv = np.zeros((H, W, 4), np.float32)
    cv[..., 3] = 1
    K.light_leak(cv, 0.0, colors=LEAK_COLS(), strength=strength, seed=seed, sweep=0.5, angle=angle)
    wide_band(cv, 0.5, angle, wide)
    return float((K.lum(cv[..., :3]) > thr).mean())


# =============================================================================================== Tx + catalogue
CUE_KEYS = ('lp', 'hp', 'rate', 'width')                 # mixer-level keys (audio._render_cue), not sound params


def cue(t, name, gain_db=0.0, align='hit', pan=0.0, alt=None, **params):
    """One SFX cue dict on an audio.py catalog name.  X.cue(2.0, 'whip', -3, direction=1); lp= / hp= / rate= /
    width= become mixer-level cue keys."""
    extra = {k: params.pop(k) for k in CUE_KEYS if k in params}
    d = dict(t=round(float(t), 4), name=name, gain_db=float(gain_db), align=align, pan=float(pan), params=params,
             **extra)
    if alt:
        d['alt'] = alt
    return d


class Win:
    """Window geometry of one transition: c (cut, s), pre / post (frames), t0 (first window frame), t1 (first
    frame AFTER the window), last (= t1 - 1/FPS, the last rendered window frame), d (s).
    Envelopes are frame-normalised so they reach their end values ON the first / last rendered frames (the
    frames outside a window are the plain scenes, so anything still visible on the last window frame pops):
        w.u(t)   0 on the first window frame -> 1 on the last one      (sin(pi u) is 0 on both edge frames)
        w.ua(t)  0 on the first frame -> 1 AT the cut (A-side motion that continues through the cut)
        w.ua1(t) 0 on the first frame -> 1 on the last pre frame (k = -1: A-side fades that must be gone)
        w.ub(t)  0 at the cut -> 1 on the last window frame (B-side settles)
        w.env_in(t, n=4)  0 on the first frame -> 1 after n frames (overlay fade-in, inout_sine)
        w.env_out(t, n=4) 1 -> 0 over the last n frames, 0 ON the last window frame (overlay fade-out)
    e.g. op = w.env_in(t) * w.env_out(t)."""

    def __init__(self, c, pre, post):
        self.c, self.pre, self.post = float(c), int(pre), int(post)
        self.t0, self.t1 = self.c - self.pre / FPS, self.c + self.post / FPS
        self.last = self.t1 - 1.0 / FPS
        self.d = (self.pre + self.post) / FPS

    def u(self, t):
        """0..1 across the whole window: 0 on the first rendered frame, 1 on the last one."""
        n = self.pre + self.post - 1
        return K.clamp((t - self.t0) / (n / FPS)) if n > 0 else 1.0

    def ua(self, t):
        """0..1 across the pre part (1 at the cut, i.e. one frame after the last A-side frame)."""
        return K.clamp((t - self.t0) / (self.pre / FPS)) if self.pre > 0 else 1.0

    def ua1(self, t):
        """0..1 across the pre part, 1 on the last pre frame (k = -1)."""
        n = self.pre - 1
        return K.clamp((t - self.t0) / (n / FPS)) if n > 0 else 1.0

    def ub(self, t):
        """0..1 across the post part: 0 at the cut, 1 on the last window frame (k = post - 1)."""
        n = self.post - 1
        return K.clamp((t - self.c) / (n / FPS)) if n > 0 else 1.0

    def env_in(self, t, n=4, ease='inout_sine'):
        """Overlay fade-in: 0 on the first window frame, 1 from frame n on."""
        return K.ramp(t, self.t0, self.t0 + n / FPS, ease)

    def env_out(self, t, n=4, ease='inout_sine'):
        """Overlay fade-out: 1 until n frames before the end, 0 on the last window frame."""
        return 1.0 - K.ramp(t, self.last - n / FPS, self.last, ease)

    def k(self, t):
        return fidx(t, self.c)

    def inside(self, t):
        k = self.k(t)
        return -self.pre <= k < self.post


class Tx:
    """One catalogue transition (see module docstring).  X.TX['C3'](t, c, A, B, center=(540, 700))"""

    def __init__(self, id, name, family, pre, post, ease, samples, sfx, fn=None, flag='', frames_range='',
                 post_fn=None, note=''):
        self.id, self.name, self.family = id, name, family
        self.pre, self.post = int(pre), int(post)
        self.ease, self._samples, self._sfx = ease, samples, sfx
        self.fn, self.flag, self.frames_range, self._post_fn, self.note = fn, flag, frames_range, post_fn, note
        self._samples_o = callable(samples) and _nargs(samples) >= 3      # policy s(k, w, o) gets the options

    @property
    def implemented(self):
        return self.fn is not None

    @property
    def frames(self):
        return self.pre + self.post

    def win(self, c, **o):
        if self.id == 'Y3' and 'pre' not in o:
            o = _fit_y3(dict(o))
        return Win(c, o.get('pre', self.pre), o.get('post', self.post))

    def window(self, c, **o):
        w = self.win(c, **o)
        return w.t0, w.t1

    def frame_times(self, c, **o):
        w = self.win(c, **o)
        return [c + k / FPS for k in range(-w.pre, w.post)]

    def __call__(self, t, c, A, B, **o):
        if self.fn is None:
            raise NotImplementedError('%s (%s) is spec-only in jawad_tx; see the bible section 3' % (self.id, self.name))
        w = self.win(c, **o)
        o = {k: v for k, v in o.items() if k not in ('pre', 'post')}
        if not w.inside(t):
            return (B if side_b(t, w.c) else A)(t)
        return self.fn(t, w, A, B, **o)

    def samples_at(self, t, c, default=3, **o):
        """Motion-blur sub-samples for the frame at t: `default` outside the window, else the policy (an int,
        s(k, w) or s(k, w, opts) where opts are the transition options, e.g. D1's pull=)."""
        w = self.win(c, **o)
        if not w.inside(t):
            return default
        s = self._samples
        if not callable(s):
            return int(s)
        if self._samples_o:
            return int(s(w.k(t), w, {k: v for k, v in o.items() if k not in ('pre', 'post')}))
        return int(s(w.k(t), w))

    def cues(self, c, **o):
        w = self.win(c, **o)
        out = self._sfx(w, o) if self._sfx else []
        for d in out:
            d['tx'] = self.id
        return out

    def post_kw(self, t, c, **o):
        if self._post_fn is None:
            return {}
        w = self.win(c, **o)
        if not (-w.pre - 2 <= w.k(t) < w.post + 6):          # pushes decay a few frames past the window
            return {}
        return self._post_fn(t, w, o)

    def __repr__(self):
        return 'Tx(%s %s, %s, %d+%d f%s)' % (self.id, self.name, self.family, self.pre, self.post,
                                            ', ' + self.flag if self.flag else '')


TX = {}


def _nargs(fn):
    """Number of positional parameters of a callable (sample policies: 2 = s(k, w), 3 = s(k, w, o))."""
    import inspect
    try:
        ps = inspect.signature(fn).parameters.values()
    except (TypeError, ValueError):
        return 2
    return sum(p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in ps)


def _reg(id, name, family, pre, post, ease, samples, sfx, fn=None, flag='', frames_range='', post_fn=None, note=''):
    TX[id] = Tx(id, name, family, pre, post, ease, samples, sfx, fn, flag, frames_range, post_fn, note)
    return TX[id]


def tx(id):
    """X.tx('L1') -> Tx"""
    return TX[id]


def catalogue():
    """Rows for all 43 transitions: (id, name, family, frames, cut frame, ease, flag, implemented)."""
    return [(x.id, x.name, x.family, x.frames, x.pre, x.ease, x.flag, x.implemented) for x in TX.values()]


def check_cues(cues):
    """Names not in the audio.py catalog (should be [])."""
    import audio as A
    names = set(A.names())
    return sorted({c['name'] for c in cues if c['name'] not in names})


def _push_post(gain, decay=16.0):
    def fn(t, w, o):
        return {'push': o.get('push_gain', gain) * K.impulse(t, w.c - 0.02, decay)}
    return fn


# =============================================================================================== CAMERA
def _tx_whip(t, w, A, B, deg=32.0, axis='x', sign=1, mode='2d', dist=1.4):
    """C1 whip pan. 2d (default): the plates slide by dist * W (wrap border, no mirroring) with whip_blur;
    mode='3d': scenes take yaw= / pitch= (degrees) and build their own camera. axis 'x' | 'y' (swipe-whip)."""
    c = w.c

    def off(tt):
        uu = w.u(tt)                     # frame-normalised: 0 on the first, 1 on the last window frame
        return sign * (K.EASE['inout_expo'](uu) - (1.0 if side_b(tt, c) else 0.0))

    o = off(t)
    S = B if side_b(t, c) else A
    if mode == '3d':
        cv = S(t, **{('yaw' if axis == 'x' else 'pitch'): -deg * o})
        v = abs(off(t + 1 / FPS) - o) * math.radians(deg) * 1500
    else:
        span = dist * (W if axis == 'x' else H)
        cv = S(t)
        cv = shift_canvas(cv, -o * span if axis == 'x' else 0.0, -o * span if axis == 'y' else 0.0, 'wrap')
        o2 = off(t + 1 / FPS)
        v = abs(o2 - o) * span if side_b(t + 1 / FPS, c) == side_b(t, c) else abs(o) * span * 2
    K.whip_blur(cv, min(0.5 * v, 900.0), 0.0 if axis == 'x' else 90.0)
    return cv


def _c2_sweep(t, w, leak_frames=8):
    """C2 leak band position: 0 -> 0.5 over the last `leak_frames` A frames, 0.5 at c, -> 1 on the last window
    frame (light_leak / wide_band envelopes are sin(pi sweep): 0 at both ends, peak on the cut)."""
    if side_b(t, w.c):
        return 0.5 + 0.5 * K.EASE['out_sine'](w.ub(t))      # eases out: the burn fades softly into plain B
    a = max(w.t0, w.c - leak_frames / FPS)
    return 0.5 * K.ramp(t, a, w.c, 'linear')


def _tx_dolly(t, w, A, B, subject=None, center=(K.CX, 900.0), s1=1.55, leak=0.6, mode='2d', D0=1500.0,
              D1=640.0, subj_z=0.0, seed=0, wide=0.25, leak_frames=8):
    """C2 dolly-zoom (Vertigo). The cut c sits at the END of the stretch (u = 1, peak stretch): A stretches
    over the pre frames, B takes over at c under a small exposure push (post_kw push_gain=0.3) and the L1
    ember recipe peaking at c: LEAK_COLS leak at `leak` strength + a wide_band (`wide`), with the look's bloom
    halved at the peak (post_kw bloom_scale), so the swap hides in a warm burn that never goes white (<= 2 %
    near-white px at the cut; the bible's EMBERS 0.9 leak burnt 13 % of the frame white). leak=0: an
    L3-push-only cut. 2d: the world (A) scales 1 -> s1 about `center` with a radial zoom smear while
    subject(cv, t) (the constant-size cut-out, drawn by you) stays put; 3d: scenes take cam= (X.dolly_cam) and
    draw the subject."""
    if side_b(t, w.c):
        cv = B(t, cam=dolly_cam(w.c, w.t0, w.c, D0, D1, subj_z)) if mode == '3d' else B(t)
        if subject is not None:
            subject(cv, t)
        if leak > 0:
            sw = _c2_sweep(t, w, leak_frames)
            wide_band(cv, sw, 35.0, wide)
            K.light_leak(cv, t, colors=LEAK_COLS(), strength=leak, seed=seed, sweep=sw, angle=35)
        return cv
    u = w.ua(t)
    if mode == '3d':
        cv = A(t, cam=dolly_cam(t, w.t0, w.c, D0, D1, subj_z))
    else:
        e = K.EASE['easy_ease'](u)
        cv = zoom_canvas(A(t), K.lerp(1.0, s1, e), center, 'night')
        de = K.EASE['easy_ease'](K.clamp(u + 1 / max(w.pre, 1))) - e
        K.zoom_blur(cv, min(0.06, abs(de) * (s1 - 1) * 1.8), center=center)
    if subject is not None:
        subject(cv, t)
    if leak > 0:
        sw = _c2_sweep(t, w, leak_frames)
        if sw > 0:
            wide_band(cv, sw, 35.0, wide)
            K.light_leak(cv, t, colors=LEAK_COLS(), strength=leak, seed=seed, sweep=sw, angle=35)
    return cv


def _c2_post(t, w, o):
    """C2 finish overrides: a small exposure push on c and the look's bloom halved while the leak peaks."""
    d = {'push': o.get('push_gain', 0.3) * K.impulse(t, w.c - 0.02, 16.0)}
    if o.get('leak', 0.6) > 0 and w.inside(t):
        d['bloom_scale'] = 1.0 - 0.55 * math.sin(math.pi * _c2_sweep(t, w, o.get('leak_frames', 8)))
    return d


def _portal_scale(center, r0):
    far = max(math.hypot(center[0] - x, center[1] - y) for x in (0, W) for y in (0, H))
    return far * 1.06 / r0


@functools.lru_cache(maxsize=8)
def _ring_spr(r, width, glow):
    spr = K.ring(r, width, K.C['AMBER'] * 1.6, glow=0)
    return K.glow(spr, K.C['FLAME'], sigmas=(3, 9, 24), strength=1.2, weights=(1.0, 0.6, 0.35))


def _tx_portal(t, w, A, B, center=(K.CX, 760.0), r0=220.0, rim=True, b_scale=1.08, blur=0.10, iris=5):
    """C3 push-in through an object (portal). The aperture (radius r0 at `center`: the lens / ring / screen of
    a prop in A) irises open over the first `iris` frames (radius 0 -> r0 and opacity 0 -> 1, inout_sine, so
    the first window frame is plain A), then A zooms exponentially (in_expo) into it while the aperture glides
    to frame centre; B is screen-locked inside it (at b_scale), fills the frame at c, then settles
    b_scale -> 1 (out_expo, exactly 1 on the last window frame). rim=True draws the kit's glowing ring on the
    aperture edge (it fades in with the iris); pass rim=False when A already draws its own prop ring there."""
    if side_b(t, w.c):
        return zoom_canvas(B(t), K.lerp(b_scale, 1.0, K.EASE['out_expo'](w.ub(t))), (K.CX, K.CY), 'night')
    u = w.ua(t)
    e = K.EASE['in_expo'](u)
    sfull = _portal_scale((K.CX, K.CY), r0) * 1.02
    s = sfull ** e
    em = (s - 1.0) / max(1e-6, sfull - 1.0)            # the aperture glides to centre as it zooms: A always
    px, py = K.lerp(center[0], K.CX, em), K.lerp(center[1], K.CY, em)       # covers the frame (no mirrored edges)
    M = [[s, 0, px - s * center[0]], [0, s, py - s * center[1]]]
    cv = affine_canvas(A(t), M, 'night')
    io = w.env_in(t, max(1, min(int(iris), w.pre - 1))) if iris else 1.0     # iris open: 0 on the first frame
    if io <= 0:
        return cv
    R = r0 * s * io
    X, Y = grid4()
    m = up(np.clip((R - np.hypot(X - px, Y - py)) / 3.0 + 0.5, 0, 1) * np.float32(io))
    mix_mask(cv, zoom_canvas(B(t), b_scale, (K.CX, K.CY), 'night'), m)
    if rim and 4.0 < R < 1400:
        rr = int(min(1200, max(8, round(R / 8) * 8)))           # quantised radius: a handful of cached rings
        spr = _ring_spr(rr, max(3.0, rr * 0.02), 0)
        K.draw(cv, spr, px, py, scale=R / rr, opacity=io * (1.0 - K.ramp(u, 0.75, 1.0, 'inout_sine')), mode='over')
    amt = blur * K.EASE['in_cubic'](u) * (1 - K.ramp(u, 0.9, 1.0, 'linear'))
    K.zoom_blur(cv, amt, center=(px, py))
    return cv


def _tx_blurswap(t, w, A, B, radius=46.0):
    """C6 blur-swap (rack everything soft, swap at maximum defocus, rack back): an invisible cut."""
    S = B if side_b(t, w.c) else A
    cv = S(t)
    k = math.sin(math.pi * w.u(t)) ** 1.5
    r = radius * k
    if r > 0.6:
        cv[...] = K.disc_blur(cv, r)
    return cv


def _tx_crash(t, w, A, B, center=(K.CX, K.CY), s1=1.35, b0=1.2):
    """C8 crash / snap zoom: A punches 1 -> s1 (out_expo) about `center` (the face), hard cut to B which
    settles b0 -> 1 over the post frames."""
    if side_b(t, w.c):
        cv = zoom_canvas(B(t), K.lerp(b0, 1.0, K.EASE['out_expo'](w.ub(t))), center, 'reflect')
        K.zoom_blur(cv, 0.05 * K.impulse(t, w.c, 12) * (1.0 - w.ub(t)), center=center)
        return cv
    cv = zoom_canvas(A(t), K.lerp(1.0, s1, K.EASE['out_expo'](w.ua(t))), center, 'reflect')
    K.zoom_blur(cv, 0.05 * K.impulse(t, w.t0, 12), center=center)
    return cv


# =============================================================================================== MATCH
def _pose(p, t):
    return p(t) if callable(p) else p


def _match_M(src, dst, e):
    """Affine taking circle src (x, y, r) towards dst by fraction e (log-scale lerp)."""
    s = math.exp(K.lerp(0.0, math.log(dst[2] / src[2]), e))
    cx, cy = K.lerp(src[0], dst[0], e), K.lerp(src[1], dst[1], e)
    return [[s, 0, cx - s * src[0]], [0, s, cy - s * src[1]]]


MATCH = (540.0, 820.0, 250.0)


def _tx_shape_match(t, w, A, B, a=(540.0, 820.0, 200.0), b=(540.0, 820.0, 300.0), match=MATCH):
    """M1 shape match cut (circles). a / b: (x, y, r) of the circle in A / B at their natural framing (or a
    callable t -> pose). A is pushed so its circle reaches `match` exactly on the frame before c (in_cubic);
    B starts with its circle on `match` at c and pulls back to its own framing (out_expo). Hard cut + push."""
    if side_b(t, w.c):
        e = 1.0 - K.EASE['out_expo'](w.ub(t))
        M = _match_M(_pose(b, t), match, e)
        return affine_canvas(B(t), M, 'night')
    e = K.EASE['in_cubic'](K.clamp((t - w.t0) / max(1e-6, (w.pre - 1) / FPS)))
    M = _match_M(_pose(a, t), match, e)
    return affine_canvas(A(t), M, 'night')


def _tx_hue(t, w, A, B, gain=1.6):
    """M2 colour match / hue bridge: k = sin^2(pi u) tints both sides to FLAME luminance, cut at u = 0.5."""
    cv = (B if side_b(t, w.c) else A)(t)
    hue_bridge(cv, math.sin(math.pi * w.u(t)) ** 2, gain)
    return cv


def motion_track(c, pre=9, post=9, a=(140, 900), m=(540, 900), b=(940, 900)):
    """M3's default shared K.Track: a -> m (in_cubic, at the cut c) -> b (out_cubic, on the last window frame);
    it holds a before / b after the window, so scenes call S(t, move=X.motion_track(c)(t)) outside it too.
    X.motion_track(4.0)(4.0) -> (540, 900)"""
    w = Win(c, pre, post)
    return K.Track([(w.t0, a, 'in_cubic'), (w.c, m, 'out_cubic'), (w.last, b)])


def _tx_motion_match(t, w, A, B, move=None):
    """M3 motion match: hard cut at max velocity; both scenes get move=(x, y) from the shared K.Track
    (default X.motion_track: 140 -> 540 -> 940 px at y 900, continuous velocity). Scenes take move= and must
    draw the object at the same track outside the window too (move=X.motion_track(c)(t)), or it pops."""
    if move is None:
        move = motion_track(w.c, w.pre, w.post)
    return (B if side_b(t, w.c) else A)(t, move=tuple(move(t)))


@functools.lru_cache(maxsize=4)
def _spark(r=10.0):
    d = K.disc(r, K.C['AMBER'] * 3.0)
    return K.glow(d, K.C['FLAME'], sigmas=(6, 18, 50), strength=1.3)


@functools.lru_cache(maxsize=2)
def _spark_light(size=700):
    return K.radial(size, K.C['FLAME'] * 0.25)


def _path_at(pts, p):
    pts = np.asarray(pts, np.float64)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.r_[0, np.cumsum(seg)]
    s = K.clamp(p) * cum[-1]
    return float(np.interp(s, cum, pts[:, 0])), float(np.interp(s, cum, pts[:, 1]))


def _catmull(pts, n=64):
    P = np.asarray(pts, np.float64)
    if len(P) < 3:
        return P
    P = np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in np.linspace(0, 1, n, endpoint=False):
            s2, s3 = s * s, s * s * s
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3))
    out.append(P[-2])
    return np.array(out)


def carrier(r=10.0):
    """M6's default carrier sprite (an ember spark, emissive): draw it at rest in A before the window and in B
    after it, at the path ends:  K.draw(cv, X.carrier(), *path[0], mode='add')"""
    return _spark(r)


def _tx_carry(t, w, A, B, path=((120, 1300), (460, 980), (760, 760), (980, 520)), sprite=None, scale=1.0,
              light=True, trail=6):
    """M6 object carry-over: one ember spark (or any emissive sprite) travels a Catmull-Rom path in screen space
    (inout_cubic: at rest on path[0] on the first window frame, fastest at c, at rest on path[-1] on the last)
    over BOTH scenes; the background cuts under it at c; its light falls on both worlds (radial FLAME light,
    fading in / out over 4 frames) and a comet tail follows it in proportion to its speed. Draw the same
    carrier at rest in A before (path[0]) / B after (path[-1]) the window yourself (X.carrier())."""
    cv = (B if side_b(t, w.c) else A)(t)
    curve = _catmull(path)
    p = K.EASE['inout_cubic'](w.u(t))
    x, y = _path_at(curve, p)
    if light:                                           # the carrier's light fades in / out with the window
        K.draw(cv, _spark_light(), x, y, opacity=w.env_in(t, 4) * w.env_out(t, 4), mode='add')
    spr = _spark() if sprite is None else sprite
    # a short comet tail along the path (reads in stills); it scales with the carrier's speed, so it is
    # gone at both rest ends (inout_cubic) and the window edges match a carrier drawn at rest by the scenes
    sp = K.clamp(abs(K.EASE['inout_cubic'](w.u(t + 0.5 / FPS)) - K.EASE['inout_cubic'](w.u(t - 0.5 / FPS)))
                 * max(1, w.pre + w.post - 1) / 1.5)
    for i in range(trail, 0, -1):
        pp = K.EASE['inout_cubic'](K.clamp(w.u(t - i * 0.25 / FPS)))
        xx, yy = _path_at(curve, pp)
        if sp > 0.01:
            K.draw(cv, spr, xx, yy, scale=scale * (1 - 0.06 * i), opacity=0.5 * sp * (1 - i / (trail + 1)),
                   mode='add')
    K.draw(cv, spr, x, y, scale=scale, mode='add')
    return cv


# =============================================================================================== TYPE
@functools.lru_cache(maxsize=8)
def _counter_word(word, px, style):
    """Word sprite + 4x counter masks of every glyph (block coords). Returns (ts, holes[(area, (bx, by), mask4,
    box_block)]) sorted biggest first."""
    ts = T.render(word, style, px=px)
    flat = T.render(word, 'flat', px=px * 4, font=T.STYLES[style].font, tracking=T.STYLES[style].tracking,
                    fill='WHITE')
    L = [l for l in flat.layers if l.part == 'front'][0]
    a = L.spr[..., 3]
    ink = (a > 0.5).astype(np.uint8)
    h, w = ink.shape
    ff = np.pad(1 - ink, 1, constant_values=1)
    msk = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, msk, (0, 0), 2)
    holes = (ff[1:-1, 1:-1] == 1).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(holes)
    out = []
    for i in range(1, n):
        if st[i, 4] < 40:
            continue
        comp = (lab == i)
        grow = cv2.dilate(comp.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        m4 = np.where(grow, 1.0 - a, 0.0).astype(np.float32)
        dt = cv2.distanceTransform(comp.astype(np.uint8), cv2.DIST_L2, 5)
        iy, ix = np.unravel_index(np.argmax(dt), dt.shape)
        # sprite px (4x) -> block coords (1x)
        bx = (L.box[0] + (ix + 0.5) / L.res) / 4.0
        by = (L.box[1] + (iy + 0.5) / L.res) / 4.0
        r_in = float(dt.max()) / L.res / 4.0                          # inscribed radius, block px
        out.append((float(st[i, 4]), (bx, by), m4, tuple(v / 4.0 for v in L.box), r_in))
    out.sort(key=lambda r: -r[0])
    return ts, out


def _tx_counter(t, w, A, B, word='sapna', x=K.CX, y=900.0, px=230, style='jw_key', hole=0, s1=None, blur=0.12):
    """Y1 zoom through a serif counter: the brand keyword sits on A; B lives inside the counter (bowl) of one
    of its letters (hole 0 = the biggest). The word zooms in_expo 1 -> s1 about that counter while it glides
    to frame centre; at c the counter covers the frame and B is full (screen-locked). s1=None picks the end
    scale so the counter's inscribed circle covers the frame on the last pre frame, where the word's rim and
    the zoom smear have faded out (that frame is all B, like the cut). Draw the settled word on A yourself
    before the window: X.counter_word(word, px)[0].draw(cv, x, y)."""
    if side_b(t, w.c):
        return B(t)
    ts, holes = _counter_word(word, px, style)
    if not holes:
        raise ValueError('no closed counter in %r' % word)
    area, zp, m4, box, r_in = holes[min(hole, len(holes) - 1)]
    u = w.ua(t)
    e = K.EASE['in_expo'](u)
    if s1 is None:                       # the counter's inscribed circle covers the frame on the last pre frame
        e_last = K.EASE['in_expo']((w.pre - 1) / max(1, w.pre))
        s1 = (math.hypot(K.CX, K.CY) * 1.08 / max(r_in, 1.0)) ** (1.0 / max(e_last, 0.05))
    s = s1 ** e
    em = K.EASE['inout_cubic'](u)
    ax, ay = ts.w * 0.5, ts.h * 0.5
    p0 = (x + (zp[0] - ax), y + (zp[1] - ay))
    px_, py_ = K.lerp(p0[0], K.CX, em), K.lerp(p0[1], K.CY, em)
    anchor = (zp[0] / ts.w, zp[1] / ts.h)
    u1 = w.ua1(t)                        # 1 on the last pre frame: the word and the smear are gone there
    cv = A(t)
    ts.draw(cv, px_, py_, anchor=anchor, scale=s, opacity=1.0 - K.ramp(u1, 0.8, 1.0, 'inout_sine'))
    # counter mask: block coords -> canvas through the same similarity transform
    M = np.array([[s, 0, px_ - s * zp[0]], [0, s, py_ - s * zp[1]]], np.float64)
    bx0, by0, bx1, by1 = box
    hh, ww = m4.shape
    Ms = M @ np.array([[(bx1 - bx0) / ww, 0, bx0], [0, (by1 - by0) / hh, by0], [0, 0, 1]], np.float64)
    m = cv2.warpAffine(m4, np.float32(Ms), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    mix_mask(cv, B(t), m)
    K.zoom_blur(cv, blur * K.EASE['in_cubic'](u) * (1 - K.ramp(u1, 0.85, 1.0, 'inout_sine')), center=(K.CX, K.CY))
    return cv


def counter_word(word, px=230, style='jw_key'):
    """(TextSprite, holes) used by Y1; holes[i] = (area, zoom point (block px), mask4, box, inscribed radius)."""
    return _counter_word(word, px, style)


def _tx_slams(t, w, A, B, words=('HOOK.', 'STORY.', 'EDIT.'), beat=20, style='jw_caps_bold', px=170, y=900.0,
              plates=None, seed=0):
    """Y3 kinetic slam cuts: one word per beat (beat frames), each slam (SLAM spring) hard-cuts the plate
    (A / B alternating, the last slam lands on B at c), with an exposure push per slam (post_kw). Set
    pre = (len(words) - 1) * beat (Plan / tx do it from words= and beat=).
    The word lands ON its hit frame (fix round 2): the slam starts HALF before the hit with no opacity ramp, so
    every sub-sample of the hit frame shows the word at ~s0 (no smear on that frame: render.py's samples blur
    it), and from the next frame the smear only integrates time since the hit (it used to average sub-samples
    from before t0, so the word read one frame after its cut and cue)."""
    n = len(words)
    slams = [w.c - (n - 1 - i) * beat / FPS for i in range(n)]
    i = max([j for j in range(n) if side_b(t, slams[j])], default=-1)
    if i < 0:
        return A(t)
    pl = tuple(plates) if plates else (B, A)          # counted back from the last slam, which is always B
    S = B if i == n - 1 else pl[(n - 1 - i) % len(pl)]
    cv = S(t)
    g = _glyphs(words[i], style, px)
    op = w.env_out(t, 5) if i == n - 1 else 1.0          # the last word is gone ON the last window frame
    fr, dz = SPRINGS['SLAM']
    ts = slams[i] - HALF - 0.001                         # every t that side_b gives to this word has tt > 0
    el = t - slams[i]                                    # < HALF on every sub-sample of the hit frame
    g.slam(cv, t, K.CX, y, t0=ts, s0=1.6, dur=0.45, freq=fr, damping=dz, opacity=op, fade=0.0,
           smear=HALF <= el < 0.45, mspan=min(2.2 / FPS, max(t - ts, 1e-4)))
    return cv


@functools.lru_cache(maxsize=32)
def _glyphs(word, style, px):
    return T.Glyphs(word, style, px=px)


def _seg_dist(X, Y, p0, p1):
    vx, vy = p1[0] - p0[0], p1[1] - p0[1]
    L2 = max(vx * vx + vy * vy, 1e-9)
    s = np.clip(((X - p0[0]) * vx + (Y - p0[1]) * vy) / L2, 0, 1)
    return np.hypot(X - (p0[0] + s * vx), Y - (p0[1] + s * vy))


def _tx_underline(t, w, A, B, x0=170.0, y=1090.0, length=740, draw=10, rise=300.0, rot1=-30.0, hand=0.4):
    """Y5 underline-stroke wipe (the house mark becomes the transition): J.underline draws on under the keyword
    (draw frames, out_cubic), then the stroke thickens (7 -> 2600 px, inout_expo), rotates -4 -> rot1 degrees
    and rises `rise` px; B is inside the capsule, its edge is an emissive amber/flame band. Full cover at c.
    Hand-over (fix round 2): over the first `hand` of the wipe (0.4 = ~6 frames) the band fades in (inout_sine)
    and widens from about the stroke's own glow (Gaussian 6 -> 14 px, glow 0.5x -> 1x) while the drawn stroke
    fades out (over the first 60 % of it, before the capsule turns), so the thin stroke grows into the glowing bar instead of turning into it in one frame (it used
    to jump 3.1x in ROI luma on k=-14). Window: pre = draw + wipe frames (default 10 + 14)."""
    if side_b(t, w.c):
        return B(t)
    cv = A(t)
    t_draw_end = w.t0 + draw / FPS
    ul = J.underline(int(length), thick=6.0)
    if t < t_draw_end:
        def uu(tt):
            return K.ramp(tt, w.t0, t_draw_end, 'out_cubic')
        speed = (uu(t + 0.004) - uu(t - 0.004)) / 0.008 * length
        ul.draw(cv, x0, y, u=uu(t), smear=speed * 0.25 / FPS)
        return cv
    u2 = K.clamp((t - t_draw_end) / max(1e-6, w.c - t_draw_end))
    e = K.EASE['inout_expo'](u2)
    width = K.lerp(7.0, 2600.0, e)
    ang = math.radians(K.lerp(-4.0, rot1, K.EASE['inout_cubic'](u2)))
    cx, cy = x0 + length / 2, y - rise * K.EASE['inout_cubic'](u2)
    half = K.lerp(length / 2, 1500.0, K.EASE['in_cubic'](u2))
    dx, dy = math.cos(ang) * half, math.sin(ang) * half
    X, Y = grid4()
    d = _seg_dist(X, Y, (cx - dx, cy - dy), (cx + dx, cy + dy))
    inside = np.clip((width / 2 - d) / 4.0 + 0.5, 0, 1)
    if u2 > 0.9:                                         # guarantee full cover by the cut
        inside = np.maximum(inside, K.ramp(u2, 0.9, 1.0, 'linear'))
    ho = K.ramp(u2, 0.0, hand, 'inout_sine') if hand > 0 else 1.0     # 0 on the first wipe frame -> 1
    sb, sg = K.lerp(6.0, 14.0, ho), K.lerp(0.5, 1.0, ho)                # the band starts near the stroke's glow
    band = np.exp(-((d - width / 2) / sb) ** 2) * (1.0 - 0.6 * e) * (1.0 - K.ramp(u2, 0.7, 0.95, 'inout_sine'))
    mix_mask(cv, B(t), up(inside))
    if ho > 0:
        g = up(_gl((band * ho).astype(np.float32), (2 * sg, 6 * sg, 15 * sg), (1.0, 0.6, 0.35)))
        hot = np.float32(K.C['AMBER']) * 0.5 + np.float32(K.C['FLAME']) * 2.5
        _add_rgb(cv, g, hot, 1.0)
    so = 1.0 - K.ramp(u2, 0.0, 0.6 * hand, 'inout_sine') if hand > 0 else 0.0
    if so > 0:                                           # the drawn stroke hands over to the growing band (it stays
        ul.draw(cv, x0, y, u=1.0, opacity=so)            # put, so it is gone before the capsule turns and rises)
    return cv


def _tx_textwipe(t, w, A, B, word=None, x=K.CX, y=900.0, style='jw_caps', px=110, angle=-32.0, split=0.4):
    """Y2 light-sweep text-wipe: the sweep runs over the word for the first `split` of the window, then the
    same band (K.light_leak sweep) crosses the frame and B is revealed behind it (sweep_mask); the band is
    gone and B complete on the last window frame. The word sits on A: draw it yourself before the window
    (T.render(word, style, px=px).draw(cv, x, y))."""
    u = w.u(t)
    cv = A(t)
    if word:
        ts = T.render(word, style, px=px)
        u1 = K.clamp(u / split)
        ts.draw(cv, x, y, sweep=u1 if 0 < u1 < 1 else None,
                sweep_kw=dict(color='AMBER', width=0.09, angle=angle), opacity=1.0 - K.ramp(u, 0.7, 0.95, 'inout_sine'))
    u2 = K.EASE['inout_sine'](K.clamp((u - split * 0.5) / (1 - split * 0.5)))      # the band lands softly
    if u2 > 0:
        mix_mask(cv, B(t), sweep_mask(u2, angle=angle, soft=0.08))
        K.light_leak(cv, t, colors=EMBERS(), strength=1.1, sweep=u2, angle=angle)
    return cv


# =============================================================================================== LIGHT / FILM
def _tx_leak(t, w, A, B, strength=0.6, seed=0, angle=35.0, wide=0.25):
    """L1 light-leak burn (ember): K.light_leak sweep 0 -> 1 across the window (its sin envelope peaks at the
    cut, u = 0.5) plus a wide soft ember band (wide_band) so >= 70 % of the frame is covered at the cut, hard
    cut under it, and an L3 push at c (post_kw). Use sparingly (Jawad disliked leak washes on every cut)."""
    cv = (B if side_b(t, w.c) else A)(t)
    u = w.u(t)
    wide_band(cv, u, angle, wide)
    K.light_leak(cv, t, colors=LEAK_COLS(), strength=strength, seed=seed, sweep=u, angle=angle)
    return cv


def _tx_burn(t, w, A, B, hot=(620.0, 760.0), seed=11):
    """L2 film burn: a noisy hole burns A to BLACK (multiplicative) from `hot` with a white-hot rim (in_cubic to
    60 %, in_expo to full at c); B emerges from black out of the centre over the post frames."""
    X, Y = grid4()
    n = fbm(seed, 5.0)
    d = np.hypot(X - hot[0], Y - hot[1]) / H + 0.35 * n
    if not side_b(t, w.c):
        u = w.ua(t)
        r = 0.6 * K.EASE['in_cubic'](K.clamp(u / 0.7)) + 1.0 * K.EASE['in_expo'](K.clamp((u - 0.7) / 0.3))
        m = np.clip((r - d) / 0.01, 0, 1)
        ring = np.exp(-((d - r) / 0.012) ** 2)
        cv = A(t)
        cv *= (1.0 - up(m))[..., None]
        cv[..., 3] = 1.0
        rg = up(ring)
        _add_rgb(cv, rg, K.C['FLAME'], 3.0)
        _add_rgb(cv, rg * rg, np.float32([1.0, 0.85, 0.6]), 2.0)
        return cv
    ub = K.EASE['out_cubic'](w.ub(t))
    cv = B(t)
    mb = np.clip((ub * 1.4 - (np.hypot(X - K.CX, Y - K.CY) / H + 0.25 * n)) / 0.08, 0, 1)
    cv[..., :3] *= up(mb)[..., None]
    return cv


def _tx_cut(t, w, A, B):
    """Hard cut at c (HALF rule) - the base of L3 / L4 / D7 whose work happens in finish() (post_kw)."""
    return (B if side_b(t, w.c) else A)(t)


def _l4_post(t, w, o):
    return {'bloomout': math.sin(math.pi * w.u(t)) ** 2 if w.inside(t) else 0.0}


def _l3_post(t, w, o):
    return {'push': o.get('push_gain', 1.0) * K.impulse(t, w.c - 0.02, 16.0)}


def _d7_post(t, w, o):
    return {'rgb_split': K.impulse(t, w.c - 0.02, 20.0)}


@functools.lru_cache(maxsize=4)
def _flare(w_=2600, h_=90):
    return K.streak(w_, h_, K.C['FLAME'] * 3.0, K.C['AMBER'] * 4.0)


def _tx_flare(t, w, A, B, y=900.0, feather=120.0):
    """L5 anamorphic flare wipe: a FLAME streak crosses x -300 -> 1380 (inout_cubic, intensity
    sin(pi inout_sine(u)): 0 with zero slope on both edge frames); the scene swaps behind its saturated core
    (soft vertical mask following x(t))."""
    u = w.u(t)
    x = K.lerp(-300.0, 1380.0, K.EASE['inout_cubic'](u))
    I = math.sin(math.pi * K.EASE['inout_sine'](u))
    cv = A(t)
    X, Y = grid4()
    mix_mask(cv, B(t), up(np.clip((x - X) / feather + 0.5, 0, 1)))
    K.draw(cv, _flare(), x, y, opacity=I, mode='add')
    return cv


def _look_val(o, key, default=0.0):
    """A finish key of the look a transition's post_kw adds to (o['look'], default 'ember')."""
    v = K.LOOKS.get(o.get('look', 'ember'), {}).get(key, default)
    return float(default if v is None else v)


def _l5_post(t, w, o):
    """L5: the look's anamorphic streaks + 0.9 sin(pi u) (back to the look's own value on the edge frames)."""
    return ({'anamorphic': _look_val(o, 'anamorphic') + 0.9 * math.sin(math.pi * K.EASE['inout_sine'](w.u(t)))}
            if w.inside(t) else {})


def _tx_beam(t, w, A, B, src=(K.CX, -900.0), a0=-40.0, a1=40.0, width=2.2, haze=0.45, rays=0.0):
    """L7 light-beam (god-ray) sweep: a volumetric amber/flame beam from a source above the frame swings
    a0 -> a1 degrees (inout_sine; it crosses frame centre at c), intensity sin(pi u) * 1.2; the scene swaps
    under the beam core (B on the side it has passed); rays > 0 adds K.god_rays (it also smears the scene's own
    highlights, so keep it for scenes without hard bright rims)."""
    u = w.u(t)
    th = K.lerp(a0, a1, K.EASE['inout_sine'](u))
    I = 1.2 * math.sin(math.pi * u)
    X, Y = grid4()
    ang = np.degrees(np.arctan2(X - src[0], Y - src[1]))
    dang = ang - th
    cv = A(t)
    mix_mask(cv, B(t), up(np.clip((-dang) / (width * 0.9) + 0.5, 0, 1)))
    dist = np.hypot(X - src[0], Y - src[1])
    fall = np.clip(1.25 - (dist - 900.0) / 2600.0, 0.15, 1.0)
    core = np.exp(-(dang / width) ** 2)
    soft = np.exp(-(dang / (width * 3.0)) ** 2) * 0.2
    vol = (0.55 + haze * fbm(23, 4.0))
    beam = ((core + soft) * fall * vol).astype(np.float32)
    if I > 0.01:
        col = np.float32(K.C['AMBER']) * 0.45 + np.float32(K.C['FLAME']) * 0.7
        _add_rgb(cv, up(beam), col, I)
        if rays > 0:
            K.god_rays(cv, (float(src[0]), 0.0), strength=rays * I, threshold=0.45, length=0.45,
                       tint=K.C['AMBER'])
    return cv


@functools.lru_cache(maxsize=64)
def _iris_poly(r, rot, n=7, cx=K.CX, cy=K.CY):
    a = np.radians(rot) + np.arange(n) * 2 * math.pi / n
    return np.c_[cx + r * np.cos(a), cy + r * np.sin(a)]


def _tx_iris(t, w, A, B, n=7, black=2):
    """L8 aperture iris close/open: a 7-blade heptagon closes on A (in_cubic), `black` frames of black around
    c, opens on B (out_back); blade edges are rim-lit FLAME."""
    Rmax = math.hypot(K.CX, K.CY) * 1.15
    kb = black / 2.0
    k = (t - w.c) * FPS
    if k < -kb:
        u = K.clamp((t - w.t0) / max(1e-6, (w.pre - kb) / FPS))
        r = Rmax * (1 - K.EASE['in_cubic'](u))
        rot = 25.0 * u
        S = A
    elif k >= kb:
        u = K.clamp((t - (w.c + kb / FPS)) / max(1e-6, (w.post - kb) / FPS))
        r = Rmax * float(K.EASE['out_back'](u))
        rot = 25.0 * (1 - u)
        S = B
    else:
        cv = np.zeros((H, W, 4), np.float32)
        cv[..., :3] = K.C['NIGHT_0']
        cv[..., 3] = 1
        return cv
    cv = S(t)
    poly = _iris_poly(round(r, 1), round(rot, 2), n)
    m = ui.fill_mask([(poly / 4.0, True)], W4, H4, ss=2)
    edge = ui.stroke_mask([(poly / 4.0, True)], W4, H4, 1.2)
    night = np.float32(K.C['NIGHT_0'])
    mm = up(m)
    cv[..., :3] = cv[..., :3] * mm[..., None] + night * (1 - mm[..., None])
    g = up(_gl(edge, (1.0, 4.0), (1.0, 0.5)))
    _add_rgb(cv, g, K.C['FLAME'], 1.6)
    return cv


# =============================================================================================== DIGITAL / EDITOR
_NLE_MON = (540.0, 700.0, 0.46)                   # monitor centre x, y and scale when pulled back
_NLE_TL = (90, 1205, 900, 270)                    # timeline panel x, y, w, h (safe zone: y <= 1480)


@functools.lru_cache(maxsize=1)
def _nle_bg():
    """Full-frame dark NLE workspace (read-only): warm-black gradient, faint grid, monitor + timeline panels."""
    cv = K.new_canvas(K.C['NIGHT_0'])
    g = K.gradient(W, H, [K.C['NIGHT_1'], K.C['NIGHT_0']], angle=-90)
    cv[..., :3] = g
    s = ui.Surf(W, H, cv)
    mx, my, ms = _NLE_MON
    mw, mh = W * ms, H * ms
    s.rrect(mx - mw / 2 - 14, my - mh / 2 - 14, mw + 28, mh + 28, 18, K.C['SMOKE'] * 0.55)
    x, y, w_, h_ = _NLE_TL
    s.rrect(x, y, w_, h_, 22, K.C['SMOKE'] * 0.7)
    s.stroke_rrect(x, y, w_, h_, 22, 1.5, K.C['FLAME'] * 0.35)
    cv.flags.writeable = False
    return cv


@functools.lru_cache(maxsize=1)
def _nle_timeline():
    """Timeline lanes sprite (W x H canvas-sized overlay, emissive + body): V2 / V1 / A1 lanes, clips, labels."""
    x, y, w_, h_ = _NLE_TL
    s = ui.Surf(W, H)
    lanes = (('V2', y + 40, K.C['EMBER']), ('V1', y + 120, K.C['FLAME']), ('A1', y + 200, K.C['GOLD']))
    rng = np.random.default_rng(5)
    for name, ly, col in lanes:
        T.render(name, 'jw_mono', px=34).draw(s.img, x + 26, ly, anchor=(0, 0.5))
        if name == 'A1':
            xs = np.arange(x + 110, x + w_ - 24, 4)
            amp = (np.abs(np.sin(xs * 0.031) * np.sin(xs * 0.0071 + 1.3)) * 0.8 + 0.2 * rng.random(len(xs))) * 26
            for xx, a in zip(xs, amp):
                s.rrect(xx, ly - a, 2.5, 2 * a, 1.2, col * 0.8)
        else:
            cx_ = x + 110
            while cx_ < x + w_ - 40:
                cw = float(rng.uniform(110, 230))
                cw = min(cw, x + w_ - 24 - cx_)
                s.rrect(cx_, ly - 26, cw - 6, 52, 8, col * (0.55 if name == 'V1' else 0.4))
                s.stroke_rrect(cx_, ly - 26, cw - 6, 52, 8, 1.2, col * 1.2)
                cx_ += cw
    img = s.img
    img.flags.writeable = False
    return img


def _timecode(sec):
    fr = int(round(sec * FPS))
    return '00:00:%02d:%02d' % ((fr // FPS) % 60, fr % FPS)


def _d1_p(t, w, pull, ease):
    """D1 pull-back amount p (0 = monitor full-frame, 1 = pulled back into the NLE): `ease` over the pull
    frames (1 on the last pull frame), 1 while scrubbing, back to 0 over the post frames (0 on the last one)."""
    t_pull = w.t0 + pull / FPS
    if t < t_pull:
        return K.EASE[ease](K.clamp((t - w.t0) / max(1e-6, (pull - 1) / FPS)))
    if t < w.c:
        return 1.0
    return 1.0 - K.EASE[ease](w.ub(t))


def _d1_samples(k, w, o=None):
    """D1 sample policy: 9 on the fastest pull / push frames, 7 on the rest of them, 3 while scrubbing. Reads the
    transition's pull= (default 10) from o (Tx.samples_at passes the options)."""
    pull = int((o or {}).get('pull', 10))
    if k >= 0:
        j, n = k, w.post
    elif k < -w.pre + pull:
        j, n = k + w.pre, pull
    else:
        return 3
    return 9 if abs(j - (n - 1) / 2.0) <= 1.5 else 7


def _tx_scrub(t, w, A, B, pull=10, push=10, span_a=1.0, span_b=1.0, label=True, ease='inout_sine', smear=0.12):
    """D1 timeline playhead scrub (editor-native): pull back into a generic NLE (pull frames, `ease`
    inout_sine: starts from rest, at most 17 % of the move per frame; the bible's out_expo moved 54 % of the
    scale in the first frame), the
    playhead scrubs across the V1 cut (inout_expo, monitor updates at 12 Hz like real scrubbing) and lands
    on the B marker at c with the SNAP spring, then the monitor pushes back in (post frames, same ease) so B is
    full-frame on the last window frame. The moving monitor gets a zoom smear (K.zoom_blur, `smear` x its
    relative scale change per frame) on top of the 7-9 samples of the pull / push frames. Monitor shows A at
    fast-forwarded source time, then B; the timecode is the timeline time under the playhead. The NLE chrome
    (panels, lanes, playhead, timecode) sits UNDER the monitor, so the moving picture is never overdrawn; only
    the monitor's own rim is on top. Default window pre = pull + 20 (scrub), post = 10 (the push runs over the
    post frames: change it with post=; when you pass pull= also pass pre=pull + 20). The sample policy reads
    pull= (9 / 7 samples on the pull frames it implies).  X.TX['D1'](t, c, A, B, pull=12, pre=32)"""
    t_pull = w.t0 + pull / FPS
    t_push0 = w.c
    mx, my, ms = _NLE_MON
    p = _d1_p(t, w, pull, ease)
    if t < t_pull:
        content = A(t)
    elif t < t_push0:
        e = K.EASE['inout_expo'](K.clamp((t - t_pull) / max(1e-6, (t_push0 - t_pull))))
        if e < 0.5:
            src = t_pull + span_a * (e / 0.5)
            content = A(math.floor(src * 12) / 12)
        else:
            src = w.c - span_b * (1 - (e - 0.5) / 0.5)
            content = B(math.floor(src * 12) / 12)
    else:
        content = B(t)
    s = K.lerp(1.0, ms, p)
    cyy = K.lerp(K.CY, my, p)
    cxx = K.lerp(K.CX, mx, p)
    if p <= 1e-4:
        return content
    cv = np.array(_nle_bg(), copy=True)
    tl = _nle_timeline()
    M = np.float32([[s, 0, cxx - s * K.CX], [0, s, cyy - s * K.CY]])
    mon = cv2.warpAffine(content, M, (W, H), flags=cv2.INTER_AREA if s < 0.7 else cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if smear > 0 and (t < t_pull or t >= w.c):       # radial smear about the monitor's fixed point while it moves
        ds = abs(K.lerp(1.0, ms, _d1_p(t + 0.5 / FPS, w, pull, ease)) - K.lerp(1.0, ms, _d1_p(t - 0.5 / FPS, w, pull, ease)))
        fy = K.CY + (my - K.CY) / (1.0 - ms)          # content point that stays put as s and cyy move together
        K.zoom_blur(mon, min(0.04, smear * ds / max(s, 1e-3)), center=(cxx, cyy + s * (fy - K.CY)))
    # the whole workspace fades in with the pull (the monitor itself is always opaque)
    a = np.float32(K.clamp(p * 1.4))
    cv *= a
    cv += tl * a
    # playhead + timecode: chrome, so it goes UNDER the monitor (fix round 2: while the monitor pulls back / pushes
    # in it still covers the timeline area, and the playhead / timecode used to draw over its picture)
    x, y, w_, h_ = _NLE_TL
    xa, xb = x + 160.0, x + w_ - 140.0
    if t < t_pull:
        ph, src_t = xa, t
    elif t < t_push0:
        uu = K.clamp((t - t_pull) / max(1e-6, (t_push0 - t_pull - 4 / FPS)))
        ph = K.lerp(xa, xb, K.EASE['inout_expo'](uu))
        sn = spring(t - (t_push0 - 4 / FPS), 'SNAP') if t > t_push0 - 4 / FPS else 0.0
        ph = ph + (xb - ph) * sn if sn > 0 else ph
        src_t = K.lerp(t_pull, w.c, (ph - xa) / (xb - xa))          # timeline time under the playhead
    else:
        ph, src_t = xb, t
    line = np.zeros((H4, W4), np.float32)
    cv2.line(line, (int(ph / 4), int((y + 8) / 4)), (int(ph / 4), int((y + h_ - 8) / 4)), 1.0, 1, cv2.LINE_AA)
    _emit(cv, _gl(line, (0.7, 3.0), (1.0, 0.5)), K.C['RED'], 2.2 * float(a))
    K.draw(cv, _spark(5.0), ph, y + 6, opacity=float(a), mode='add')
    if label:
        T.render(_timecode(src_t), 'jw_mono', px=38).draw(cv, x + 26, y - 34, anchor=(0, 0.5), opacity=float(a))
    cv *= (1.0 - mon[..., 3:4])
    cv += mon
    # monitor rim (emissive FLAME hairline) on top
    mw, mh = W * s, H * s
    rim = np.zeros((H4, W4), np.float32)
    cv2.rectangle(rim, (int((cxx - mw / 2) / 4), int((cyy - mh / 2) / 4)), (int((cxx + mw / 2) / 4), int((cyy + mh / 2) / 4)),
                  1.0, 1, cv2.LINE_AA)
    _emit(cv, _gl(rim, (0.8, 3.0), (0.9, 0.5)), K.C['FLAME'], 0.9 * float(a))
    return cv


@functools.lru_cache(maxsize=2)
def _razor_icon(size=96):
    """Generic razor-blade cursor (IVORY with a FLAME glow): own geometry, no NLE trade dress."""
    sc = size / 24.0
    body = [(3, 8), (21, 8), (21, 16), (3, 16)]
    slot = [(8, 11.2), (16, 11.2), (16, 12.8), (8, 12.8)]
    edge = [(3, 16), (21, 16), (21, 17.4), (3, 17.4)]
    n = size + 32
    off = (16, 16)
    a = ui.fill_mask([(np.array(body) * sc, True), (np.array(slot) * sc, True)], n, n, offset=off)
    e = ui.fill_mask([(np.array(edge) * sc, True)], n, n, offset=off)
    spr = np.zeros((n, n, 4), np.float32)
    col = np.float32(K.C['IVORY'])
    spr[..., :3] = a[..., None] * col + e[..., None] * np.float32(K.C['AMBER']) * 1.5
    spr[..., 3] = np.clip(a + e, 0, 1)
    return K.glow(spr, K.C['FLAME'], sigmas=(3, 9), strength=0.8)


def _tx_razor(t, w, A, B, x_c=540.0, cursor_from=(860.0, 1420.0), cursor_y=1040.0, gap=60.0, fly=True):
    """D2 razor-tool cut: a razor cursor glides to x_c (pre frames), clicks at c: a full-height emissive FLAME
    cut line, A splits at x_c into two halves that separate (out_expo, 60 px, +-2 deg) and fly off (in_expo)
    revealing B behind (post frames)."""
    if not side_b(t, w.c):
        cv = A(t)
        u = K.EASE['out_cubic'](w.ua(t))
        cx_, cy_ = K.lerp(cursor_from[0], x_c, u), K.lerp(cursor_from[1], cursor_y, u)
        K.draw(cv, _razor_icon(), cx_, cy_, rot=-35.0, opacity=K.ramp(t, w.t0, w.t0 + 3 / FPS, 'inout_sine'))
        return cv
    ub = w.ub(t)
    cv = B(t)
    a = A(t)
    xi = int(round(x_c))
    sep = gap * K.EASE['out_expo'](K.clamp(ub / 0.35))
    off = (1500.0 * K.EASE['in_expo'](K.clamp((ub - 0.35) / 0.65))) if fly else 0.0
    rot = 2.0 * K.EASE['out_cubic'](K.clamp(ub / 0.35))
    for side in (-1, 1):
        half = np.zeros_like(a)
        if side < 0:
            half[:, :xi] = a[:, :xi]
        else:
            half[:, xi:] = a[:, xi:]
        pivot = (x_c, K.CY)
        r = math.radians(rot * side)
        cs, sn = math.cos(r), math.sin(r)
        dx = side * (sep + off)
        M = [[cs, -sn, pivot[0] - cs * pivot[0] + sn * pivot[1] + dx], [sn, cs, pivot[1] - sn * pivot[0] - cs * pivot[1]]]
        # soft drop shadow on B along the inner edge
        sh = np.zeros((H4, W4), np.float32)
        ex = (x_c + dx) / 4
        cv2.line(sh, (int(ex), 0), (int(ex), H4), 1.0, 6)
        shm = up(cv2.GaussianBlur(sh, (0, 0), 6))
        cv[..., :3] *= (1 - 0.6 * shm)[..., None]
        _over_affine(cv, half, M)
    k = 1.0 - K.ramp(t, w.c, w.c + 6 / FPS, 'in_cubic')
    if k > 0:
        line = np.zeros((H4, W4), np.float32)
        cv2.line(line, (int(x_c / 4), 0), (int(x_c / 4), H4), 1.0, 1, cv2.LINE_AA)
        _emit(cv, _gl(line, (0.6, 3.0, 10.0), (1.4, 0.7, 0.35)), K.C['FLAME'], 2.4 * k)
    return cv


def _render_track(t0):
    return K.Track([(t0, 0.0, 'out_cubic'), (t0 + .35, .22, 'hold'), (t0 + .55, .22, 'inout_cubic'),
                    (t0 + 1.0, .64, 'hold'), (t0 + 1.15, .64, 'out_expo'), (t0 + 1.6, 1.0)])


@functools.lru_cache(maxsize=1)
def _pill_body(w_=600, h_=96):
    s = ui.Surf(w_ + 64, h_ + 64)
    s.rrect(32, 32, w_, h_, h_ / 2, K.C['SMOKE'] * 0.9, opacity=0.92)
    s.stroke_rrect(32, 32, w_, h_, h_ / 2, 1.6, K.C['FLAME'] * 0.9)
    img = s.img
    img.flags.writeable = False
    return img


def _tx_render(t, w, A, B, raw=None, y_pill=1395.0, done_text='Render complete'):
    """D3 render-progress-bar wipe (editor-native): a realistic stalled progress p(t) (X._render_track) wipes
    B up from the bottom over its 'LOG / raw' before-state (raw_log(B(t)) unless A is given: pass A=None or
    raw=True), with a 2 px emissive FLAME edge and a progress pill 'Rendering... 63%' (jw_mono); at 100 %
    (c) the pill reads done_text and pulses. Default window pre 48 (the track spans 1.6 s), post 8."""
    tr = _render_track(w.t0)
    span = tr.end - w.t0
    p = tr(w.t0 + (t - w.t0) * span / max(1e-6, w.c - w.t0)) if t < w.c else 1.0
    if raw or A is None:
        before = raw_log(B(t))
    else:
        before = A(t)
    after = B(t)
    X, Y = grid4()
    edge_y = K.lerp(H + 24.0, -24.0, p)        # the soft edge starts / ends fully off-frame
    fin = w.env_in(t, 4)                       # pill + edge line fade in from the first window frame ...
    op = fin * w.env_out(t, 4)                 # ... and are gone ON the last one
    if p < 1.0:
        m = np.clip((Y - edge_y) / 24.0 + 0.5, 0, 1)
        cv = mix_mask(before, after, up(m))
        line = np.exp(-((Y - edge_y) / 2.0) ** 2).astype(np.float32)
        _emit(cv, _gl(line, (0.6, 4.0), (1.0, 0.5)), K.C['FLAME'], 1.8 * fin)
    else:
        cv = after
    # progress pill
    if op > 0:
        body = _pill_body()
        pop = 1.0 + (0.05 * spring(t - w.c, 'POP') * (1 - K.ramp(t, w.c, w.t1, 'linear')) if t >= w.c else 0.0)
        K.draw(cv, body, K.CX, y_pill, scale=pop, opacity=op)
        bw = 600 - 24
        fill = ui.Surf(bw + 8, 20)
        fill.rrect(4, 4, max(1.0, bw * p), 12, 6, K.C['FLAME'] * 1.2)
        K.draw(cv, fill.img, K.CX - bw / 2 - 4, y_pill + 26, anchor=(0, 0.5), opacity=op, mode='over')
        txt = done_text if p >= 1.0 else 'Rendering… %d%%' % int(p * 100)
        T.render(txt, 'jw_mono', px=36).draw(cv, K.CX, y_pill - 12, opacity=op)
    return cv


EASE_SHOW = K.bezier(0.7, 0.0, 0.2, 1.0)


@functools.lru_cache(maxsize=4)
def _steep_v(x1=0.7, y1=0.0, x2=0.2, y2=1.0):
    e = K.bezier(x1, y1, x2, y2)
    v = np.linspace(0, 1, 2001)
    y = np.array([e(x) for x in v])
    return float(v[np.argmax(np.gradient(y, v))])


@functools.lru_cache(maxsize=2)
def _graph_panel(pw=820, ph=560):
    s = ui.Surf(pw + 64, ph + 64)
    s.rrect(32, 32, pw, ph, 28, K.C['SMOKE'] * 0.85)
    s.stroke_rrect(32, 32, pw, ph, 28, 1.4, K.C['FLAME'] * 0.6)
    for i in range(1, 6):
        gx = 32 + 60 + (pw - 120) * i / 6
        s.rrect(gx, 32 + 60, 1.2, ph - 120, 0.6, K.C['ASH'] * 0.12)
    for j in range(1, 4):
        gy = 32 + 60 + (ph - 140) * j / 4
        s.rrect(32 + 60, gy, pw - 120, 1.2, 0.6, K.C['ASH'] * 0.12)
    img = s.img
    img.flags.writeable = False
    return img


def _tx_graph(t, w, A, B, x=K.CX, y=760.0, pw=820, ph=560, draw=10, travel=18, label=True):
    """D4 keyframe-graph swoosh (editor-native): a value graph of EASE_SHOW = bezier(0.7, 0, 0.2, 1) draws on
    (draw frames), keyframe diamonds pop (POP spring), a glowing dot rides the curve (travel frames) and the
    background whips A -> B (C1, 8 frames) exactly at the curve's steepest point (= c). One curve drives the
    display and the motion. Default window: pre = draw + steep frame, post = rest of travel."""
    vs = _steep_v()
    t_tr = w.t0 + draw / FPS
    t_end = t_tr + travel / FPS
    c = w.c
    # background whip centred on c
    whip_w = Win(c, 4, 4)
    if whip_w.inside(t):
        cv = _tx_whip(t, whip_w, A, B)
    else:
        cv = (B if side_b(t, c) else A)(t)
    op = w.env_in(t, 4) * w.env_out(t, 5)            # the whole overlay: 0 on the first and last window frame
    if op <= 0:
        return cv
    panel = _graph_panel(pw, ph)
    K.draw(cv, panel, x, y, opacity=op)
    gx0, gy0 = x - pw / 2 + 60, y + ph / 2 - 80          # graph origin (value 0 at the bottom)
    gw, gh = pw - 120, ph - 140
    v = np.linspace(0, 1, 120)
    pts = np.c_[gx0 + v * gw, gy0 - np.array([EASE_SHOW(q_) for q_ in v]) * gh]
    dr = K.ramp(t, w.t0, t_tr, 'out_cubic')
    if dr > 0:
        ox, oy = int((x - pw / 2 - 20) / 2), int((y - ph / 2 - 20) / 2)        # panel-local half-res region
        rw, rh = int(pw / 2 + 20), int(ph / 2 + 20)
        part = ui.trim_polyline(pts, 0.0, dr)
        m = ui.stroke_mask([(part / 2.0 - (ox, oy), False)], rw, rh, 2.2)
        _emit(cv, _gl(m, (1.0, 4.0, 10.0), (1.0, 0.6, 0.3)), np.float32(K.C['AMBER']) * 0.5 + np.float32(K.C['FLAME']) * 1.2,
              op, f=2, off=(ox, oy))
        # bezier handles
        hs = [((gx0, gy0), (gx0 + 0.7 * gw, gy0)), ((gx0 + gw, gy0 - gh), (gx0 + 0.2 * gw, gy0 - gh))]
        for (p0, p1) in hs:
            hm = ui.stroke_mask([(np.array([p0, p1]) / 2.0 - (ox, oy), False)], rw, rh, 1.0)
            _emit(cv, hm, K.C['ASH'], 0.5 * op * dr, f=2, off=(ox, oy))
    # keyframe diamonds pop on 8ths of the draw-on
    for i, (px_, py_) in enumerate(((gx0, gy0), (gx0 + gw, gy0 - gh), (gx0 + 0.7 * gw, gy0), (gx0 + 0.2 * gw, gy0 - gh))):
        tk = w.t0 + i * 2.5 / FPS
        sp = spring(t - tk, 'POP') if t > tk else 0.0
        if sp > 0:
            sz = 12 if i < 2 else 8
            poly = np.array([(22, 22 - sz), (22 + sz, 22), (22, 22 + sz), (22 - sz, 22)])
            dm = ui.fill_mask([(poly, True)], 44, 44)
            spr = np.zeros((44, 44, 4), np.float32)
            spr[..., :3] = dm[..., None] * (np.float32(K.C['AMBER']) * (1.4 if i < 2 else 0.9))
            spr[..., 3] = dm
            K.draw(cv, spr, px_, py_, scale=sp, opacity=op)
    if t >= t_tr:
        vv = K.clamp((t - t_tr) / (travel / FPS))
        K.draw(cv, _spark(7.0), gx0 + vv * gw, gy0 - EASE_SHOW(vv) * gh, opacity=op, mode='add')
    if label:
        T.render('EASE  0.70  0.00  0.20  1.00', 'jw_mono', px=34).draw(cv, x, y - ph / 2 + 44, opacity=op * 0.9)
    return cv


def _tx_undo(t, w, A, B, press=6, R=1.5, keys_y=1330.0):
    """D9 undo / Ctrl+Z rewind: 'Ctrl' + 'Z' keycaps fade in (3 frames), press on frames 2 and 5, then A rewinds
    R seconds accelerating from where it is (tau = t_r - R * in_cubic(u), t_r = t0 + press frames) desaturated
    30 % with a slight zoom smear, hard stop at c with an L3 push (post_kw). The keys fade out (inout_sine)
    over frames press + 8 .. press + 14. B defaults to A resuming from the restore point t_r - R (B=None)."""
    t_r = w.t0 + press / FPS
    if B is None:
        restore = t_r - R
        B = (lambda tt, _A=A, _o=w.c - restore: _A(tt - _o))
    if side_b(t, w.c):
        return B(t)
    if t < t_r:
        cv = A(t)
    else:
        u = K.clamp((t - t_r) / max(1e-6, w.c - t_r))
        tau = t_r - R * K.EASE['in_cubic'](u)
        cv = A(tau)
        desat(cv, 0.3 * min(1.0, u * 4))
        K.zoom_blur(cv, 0.02 * min(1.0, u * 4))
    op = w.env_in(t, 3) * (1.0 - K.ramp(t, w.t0 + (press + 8) / FPS, w.t0 + (press + 14) / FPS, 'inout_sine'))
    if op > 0:
        for i, (lab, kx) in enumerate((('Ctrl', K.CX - 100), ('Z', K.CX + 95))):
            tk = w.t0 + (2 + i * 3) / FPS
            sel = K.ramp(t, tk, tk + 2 / FPS, 'out_cubic')
            sc = 1.0 - 0.08 * K.impulse(t, tk, 14)
            K.draw(cv, ui.chip(lab, sel=sel, look='ember', size=54, h=112, pad_x=40), kx, keys_y, scale=sc, opacity=op)
    return cv


def _tx_velocity(t, w, A, B, peak=6.0):
    """D8 speed-ramp (velocity) cut: scene time runs 1x -> peak (in_expo) into c and back (out_expo) after;
    A(warp(t)) before, B(warp(t) - total) after (both continuous with their own clocks)."""
    half = max(w.pre, w.post) / FPS
    if side_b(t, w.c):
        return B(warp(t, w.c, half, peak) - warp_total(w.c, half, peak))
    return A(warp(t, w.c, half, peak))


# =============================================================================================== ORGANIC
def _ink_mask(t, w, p0, seed, soft=0.05):
    X, Y = grid4()
    d = np.hypot(X - p0[0], Y - p0[1]) / H + 0.25 * fbm(seed, 6.0)
    r = K.lerp(-0.04, 0.9, K.EASE['inout_sine'](w.u(t)))
    return d, r


def _tx_ink(t, w, A, B, p0=(540.0, 900.0), seed=7):
    """O1 ink bleed (deep red ink): B is revealed through a domain-warped ink bloom from p0 (inout_sine); the
    edge band darkens A (ink never glows)."""
    d, r = _ink_mask(t, w, p0, seed)
    m = np.clip((r - d) / 0.05, 0, 1)
    edge = np.exp(-((d - r) / 0.03) ** 2)
    cv = A(t)
    ink = np.float32(K.C['EMBER']) * 0.25
    E = up(edge)[..., None]
    cv[..., :3] = cv[..., :3] * (1 - E) + cv[..., :3] * ink * E
    return mix_mask(cv, B(t), up(m))


def _tx_smoke(t, w, A, B, seed=31, rise=260.0):
    """O2 smoke wipe: an upward-advected fbm smoke density covers A, lit from below by FLAME, and clears to B
    (threshold inout_sine)."""
    u = w.u(t)
    n = fbm(seed, 18.0, 3)
    n2 = fbm(seed + 1, 7.0, 3)
    sh = int(rise * u / 4) % H4
    dens = np.clip((np.roll(n, -sh, axis=0) * 0.75 + np.roll(n2, -2 * sh, axis=0) * 0.25 - 0.2) * 1.6, 0, 1)
    X, Y = grid4()
    vert = (Y / H)
    thr_a = K.EASE['inout_sine'](K.clamp(u / 0.55))
    thr_b = K.EASE['inout_sine'](K.clamp((u - 0.45) / 0.55))
    cover = np.clip((thr_a * 1.6 - (dens * 0.7 + (1 - vert) * 0.3)) / 0.12, 0, 1) * \
        (1 - np.clip((thr_b * 1.6 - (dens * 0.7 + vert * 0.3)) / 0.12, 0, 1))
    cv = (B if u >= 0.5 else A)(t)
    C = up(cover)[..., None] * np.float32(0.88)          # smoke stays slightly translucent
    lit = up((dens * vert ** 2).astype(np.float32))[..., None]
    smoke = np.float32(K.C['SMOKE']) * (0.5 + 0.6 * up(dens)[..., None]) + np.float32(K.C['FLAME']) * 0.45 * lit
    cv[..., :3] = cv[..., :3] * (1 - C) + smoke * C
    return cv


@functools.lru_cache(maxsize=4)
def _shards(n, seed, impact):
    """Voronoi shards (polygons) denser near the impact + ballistic params (cached)."""
    from scipy.spatial import Voronoi
    rng = np.random.default_rng(seed)
    k = int(n * 0.55)
    near = np.c_[rng.normal(impact[0], 220, k), rng.normal(impact[1], 260, k)]
    far = np.c_[rng.uniform(0, W, n - k), rng.uniform(0, H, n - k)]
    pts = np.vstack([near, far])
    pts[:, 0] = np.clip(pts[:, 0], 1, W - 1)
    pts[:, 1] = np.clip(pts[:, 1], 1, H - 1)
    mirror = np.vstack([pts, pts * [-1, 1], pts * [1, -1], [2 * W, 0] + pts * [-1, 1], [0, 2 * H] + pts * [1, -1]])
    vor = Voronoi(mirror)
    out = []
    for i in range(len(pts)):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or not reg:
            continue
        poly = np.clip(vor.vertices[reg], [0, 0], [W, H])
        cxy = poly.mean(0)
        d = cxy - impact
        dist = np.hypot(*d) + 1e-3
        dirv = d / dist
        speed = float(rng.uniform(500, 1300) * (1.4 - min(1.0, dist / 1400)))
        out.append(dict(poly=poly, c=cxy, v=dirv * speed, vz=float(-rng.uniform(600, 2200) * (1.3 - min(1.0, dist / 1600))),
                        spin=rng.uniform(-260, 260, 3) * np.array([1.0, 1.0, 0.6])))
    return out


@functools.lru_cache(maxsize=1)
def _shard_sprites(scene, c, n, seed, impact):
    """Cropped shard sprites of the frozen impact frame, with a thin AMBER specular edge (cached per (A, c))."""
    frame = _frozen(scene, c)
    out = []
    for sd in _shards(n, seed, impact):
        poly = sd['poly']
        x0, y0 = np.floor(poly.min(0)).astype(int)
        x1, y1 = np.ceil(poly.max(0)).astype(int)
        x0, y0, x1, y1 = max(0, x0 - 2), max(0, y0 - 2), min(W, x1 + 2), min(H, y1 + 2)
        if x1 - x0 < 3 or y1 - y0 < 3:
            continue
        loc = poly - [x0, y0]
        m = ui.fill_mask([(loc, True)], x1 - x0, y1 - y0, ss=2)
        e = ui.stroke_mask([(loc, True)], x1 - x0, y1 - y0, 1.6)
        spr = np.array(frame[y0:y1, x0:x1], copy=True)
        spr *= m[..., None]
        spr[..., :3] += (e * m)[..., None] * (np.float32(K.C['AMBER']) * 1.4)
        spr.flags.writeable = False
        out.append((spr, ((x0 + x1) / 2.0, (y0 + y1) / 2.0), sd))
    return out


def _tx_shatter(t, w, A, B, impact=(540.0, 900.0), n=56, seed=3, gravity=900.0, slowmo=1.0):
    """O4 shatter (glass): crack lines flash on A for the pre frames, then at c the frozen frame A(c) breaks
    into ~n Voronoi shards (denser at `impact`) that fly out and toward the lens (ballistic, spin, gravity,
    perspective via K.draw_plane, near-plane clipped), B behind. slowmo < 1 stretches the flight."""
    impact = (float(impact[0]), float(impact[1]))
    if not side_b(t, w.c):
        cv = A(t)
        k = K.ramp(t, w.t0, w.c, 'linear')
        lines = np.zeros((H2, W2), np.float32)
        for sd in _shards(n, seed, impact)[:24]:
            P = sd['poly'] / 2.0
            if np.hypot(*(sd['c'] - impact)) < 260 + 500 * k:
                cv2.polylines(lines, [np.int32(P * 16)], True, 1.0, 1, cv2.LINE_AA, shift=4)
        _emit(cv, _gl(lines, (0.6, 2.5), (1.0, 0.4)), np.float32(K.C['AMBER']) * 0.8, 1.2 * (0.4 + 0.6 * k), f=2)
        return cv
    cv = B(t)
    tau = (t - w.c) * slowmo
    cam = K.Cam()
    fade = w.env_out(t, 6)                              # 0 on the last window frame
    for spr, ctr, sd in _shard_sprites(A, w.c, n, seed, impact):
        px = ctr[0] + sd['v'][0] * tau
        py = ctr[1] + sd['v'][1] * tau + 0.5 * gravity * tau * tau
        pz = sd['vz'] * tau
        rot = tuple(float(a) for a in sd['spin'] * tau)
        K.draw_plane(cv, spr, cam, (px - K.CX, py - K.CY, pz), spr.shape[1], rot=rot, dof=False, opacity=fade)
    return cv


def _inv_inout_sine(y):
    return np.arccos(np.clip(1 - 2 * y, -1, 1)) / math.pi


@functools.lru_cache(maxsize=2)
def _ember_seed(scene, t0, n, seed):
    """Particle spawn points sampled from A's luminance at the window start (cached per (A, t0))."""
    fr = _frozen(scene, t0)
    small = cv2.resize(np.ascontiguousarray(fr[..., :3]), (W2, H2), interpolation=cv2.INTER_AREA)
    L = K.lum(small).ravel().astype(np.float64)
    p = np.clip(L, 0, 4) ** 1.5 + 0.0015
    p /= p.sum()
    rng = np.random.default_rng(seed)
    idx = rng.choice(L.size, n, p=p)
    y, x = np.divmod(idx, W2)
    pts = np.c_[(x + rng.random(n)) * 2.0, (y + rng.random(n)) * 2.0]
    return pts, rng.uniform(0, 1, n), rng.normal(0, 1, (n, 2)), L[idx]


def _ember_ramp(k):
    """white-hot -> FLAME -> RED -> EMBER -> dark over k in 0..1 (vectorised, linear rgb x energy)."""
    stops = np.array([0.0, 0.07, 0.32, 0.72, 1.0])
    cols = np.stack([np.float32([1.0, 0.85, 0.6]) * 3.0, np.float32(K.C['FLAME']) * 2.4,
                     np.float32(K.C['RED']) * 1.4, np.float32(K.C['EMBER']) * 0.7, np.zeros(3, np.float32)])
    out = np.empty((len(k), 3), np.float32)
    for ch in range(3):
        out[:, ch] = np.interp(k, stops, cols[:, ch])
    return out


def _tx_embers(t, w, A, B, direction='ltr', point=None, n=4000, seed=5, life=1.2, band=20.0, noise=120.0):
    """O6 ember disintegration (the most on-brand transition): an erosion front sweeps across A (inout_sine;
    'ltr' | 'rtl' | 'btt' | radial from point=(x, y)), its 20 px edge burns FLAME, and A's pixels lift off as
    ember particles (sampled from A's luminance) that rise at -46 px/s, wiggle and cool white-hot -> FLAME ->
    RED -> EMBER -> dark over `life` s (shortened per ember so that every ember is dark on the last window
    frame: nothing vanishes at the window end); B is revealed behind. c = erosion complete; the post frames
    let the last embers rise and cool over B."""
    X, Y = grid4()
    nz = fbm(seed + 40, 7.0)

    def coord(x, y):
        if point is not None:
            return np.hypot(x - point[0], y - point[1])
        return {'ltr': x, 'rtl': W - x, 'btt': H - y}.get(direction, x)

    corners = [coord(x, y) for x in (0, W) for y in (0, H)]
    if point is not None:
        corners.append(0.0)
    dmin, dmax = min(corners) - noise - band, max(corners) + noise * 0.2 + band
    xn = coord(X, Y) + noise * (nz - 0.5) * 2
    u = w.ua(t)
    front = K.lerp(dmin, dmax, K.EASE['inout_sine'](u))
    if not side_b(t, w.c):
        cv = A(t)
        mA = np.clip((xn - front) / 6.0, 0, 1)
        mix_mask(cv, B(t), up(1.0 - mA))
        edge = np.exp(-((xn - front - band * 0.3) / (band * 0.35)) ** 2).astype(np.float32)
        _emit(cv, _gl(edge, (0.6, 2.5), (1.0, 0.35)), np.float32(K.C['FLAME']) * 1.4 + np.float32(K.C['AMBER']) * 0.3)
    else:
        cv = B(t)
    # particles
    pts, rnd, nrm, lumv = _ember_seed(A, w.t0, n, seed)
    if point is not None:
        pc = np.hypot(pts[:, 0] - point[0], pts[:, 1] - point[1])
    else:
        pc = {'ltr': pts[:, 0], 'rtl': W - pts[:, 0], 'btt': H - pts[:, 1]}.get(direction, pts[:, 0])
    ix = np.clip((pts[:, 0] / 4).astype(int), 0, W4 - 1)
    iy = np.clip((pts[:, 1] / 4).astype(int), 0, H4 - 1)
    pc = pc + noise * (nz[iy, ix] - 0.5) * 2
    ts_ = w.t0 + _inv_inout_sine((pc - dmin) / (dmax - dmin)) * (w.pre / FPS)
    tau = t - ts_
    # every ember has cooled to dark ON the last window frame (w.last): the next frame is plain B, so an
    # ember still glowing there would vanish in one frame. Late embers cool faster (life_i <= life).
    life_i = np.minimum(life, w.last - ts_)
    alive = (tau >= 0) & (tau < life_i)
    if alive.any():
        a = tau[alive]
        P = pts[alive]
        nv = nrm[alive]
        dirx = 1.0 if direction != 'rtl' else -1.0
        vx = (30 + 50 * rnd[alive]) * dirx + 18 * nv[:, 0]
        vy = -46.0 - 40 * rnd[alive] + 14 * nv[:, 1]
        drag = (1 - np.exp(-2.2 * a)) / 2.2
        x = P[:, 0] + vx * drag * 2.0 + 6 * np.sin(a * 7 + rnd[alive] * 40)
        y = P[:, 1] + vy * a - 30 * a * a
        k = a / life_i[alive]
        col = _ember_ramp(k) * (0.25 + 1.1 * np.clip(lumv[alive] * 3, 0, 1))[:, None]
        buf = np.zeros((H2, W2, 3), np.float32)
        xi = (x / 2).astype(int)
        yi = (y / 2).astype(int)
        ok = (xi >= 0) & (xi < W2) & (yi >= 0) & (yi < H2)
        np.add.at(buf, (yi[ok], xi[ok]), col[ok])
        glow = cv2.GaussianBlur(buf, (0, 0), 1.5) * 2.2 + cv2.GaussianBlur(buf, (0, 0), 5.0) * 1.2
        cv[..., :3] += cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR)
    return cv


# =============================================================================================== registry
def _samples_last(n_hi, last, base=3):
    return lambda k, w: n_hi if k >= -last else base


def _s_c1(w, o):
    s = o.get('sign', 1)
    return [cue(w.c, 'whip', -3, pan=0.4 * s, direction=s)]


def _s_c2(w, o):
    return [cue(w.c - 6 / FPS, 'whoosh_slow', -6), cue(w.c, 'reverse_swell', -4, duration=round(w.pre / FPS, 3)),
            cue(w.c, 'sub_drop', -3)]


def _s_c3(w, o):
    """C3 sound: the reverse swell sucks in over the push and ends 2 frames BEFORE the cut (a dip), the air
    zoom passes through under it (-6 dB) and the soft impact lands on c at -1 dB, so the cut has an audible
    transient (with the swell and the air zoom at full level on c the impact used to be masked)."""
    return [cue(w.c - 2 / FPS, 'reverse_swell', -3, duration=round(max(0.1, (w.pre - 2) / FPS), 3)),
            cue(w.c, 'air_zoom', -6), cue(w.c, 'impact_soft', -1)]


_s = cue
_reg('C1', 'whip pan (h/v)', 'camera', 4, 4, 'inout_expo', 7, _s_c1, _tx_whip, '', '8 (10-12 at 75 BPM)')
_reg('C2', 'dolly-zoom (Vertigo)', 'camera', 40, 6, 'easy_ease', _samples_last(5, 12), _s_c2, _tx_dolly, 'premium',
     '36-60', _c2_post)
_reg('C3', 'push-in through object (portal)', 'camera', 24, 8, 'in_expo -> out_expo', _samples_last(7, 10), _s_c3,
     _tx_portal, 'premium', '18-30 + 8 settle')
_reg('C4', '3D fly-through (z-space tunnel)', 'camera', 24, 10, 'surge + exp brake', 7,
     lambda w, o: [cue(w.c - 8 / FPS, 'whoosh_by', -6, dur=1.4, direction=1), cue(w.c, 'reverse_swell', -4, duration=0.8),
                   cue(w.c, 'impact_soft', 0)], None, '', '18-30 per surge')
_reg('C5', 'orbit reveal', 'camera', 20, 18, 'glide', 6,
     lambda w, o: [cue(w.c, 'whoosh_slow', -4), cue(w.c, 'glass_tap', -8), cue(w.t1, 'shimmer', -6)], None, '', '30-45')
_reg('C6', 'rack-focus hand-off / blur-swap', 'camera', 9, 9, 'inout_cubic', 3,
     lambda w, o: [cue(w.c, 'ui_hover', -12)], _tx_blurswap, '', '12-24 (blur-swap 8-10 + 8-10)')
_reg('C7', 'parallax push + foreground wipe', 'camera', 10, 10, 'inout_cubic', 5,
     lambda w, o: [cue(w.c, 'whoosh_fast', -4)], None, '', '15-24')
_reg('C8', 'crash / snap zoom', 'camera', 4, 6, 'out_expo', 5,
     lambda w, o: [cue(w.c - 1 / FPS, 'whip', -6, direction=1), cue(w.c, 'impact_soft', 0)], _tx_crash, '',
     '3-4 + 6 settle', _push_post(0.4))
_reg('M1', 'shape match cut (circle)', 'match', 15, 15, 'in_cubic / out_expo', 5,
     lambda w, o: [cue(w.c, 'glass_tap', 0, alt='tabla_na'), cue(w.c, 'impact_soft', -8)], _tx_shape_match, 'premium',
     '0 (12-18 each side)', _push_post(0.5, 20.0))
_reg('M2', 'colour match / hue bridge', 'match', 6, 6, 'sin^2 bridge', 3,
     lambda w, o: [cue(w.c, 'reverse_swell', -6, duration=0.3), cue(w.c, 'shimmer', -10)], _tx_hue, '', '8-16',
     lambda t, w, o: {'exposure': _look_val(o, 'exposure') + 0.4 * math.sin(math.pi * w.u(t)) ** 2}
     if w.inside(t) else {})
_reg('M3', 'motion match (momentum cut)', 'match', 9, 9, 'in_cubic -> out_cubic', _samples_last(7, 3),
     lambda w, o: [cue(w.c, 'whoosh_fast', -3), cue(w.t1, 'card_slide', -8)], _tx_motion_match, '', '0 (6-10 each side)')
_reg('M4', 'frame-in-frame (rectangle) match', 'match', 21, 6, 'in_expo -> out_expo', _samples_last(7, 8),
     lambda w, o: [cue(w.t0, 'glass_tap', -8), cue(w.c, 'air_zoom', 0)], None, '', '18-24')
_reg('M5', 'morph cut (shape morph)', 'match', 8, 8, 'inout_cubic + POP', 4,
     lambda w, o: [cue(w.t0, 'shimmer', -8), cue(w.c, 'swish_small', -10, alt='sitar_meend')], None, '', '12-20')
_reg('M6', 'object carry-over (ember / crystal / cursor)', 'match', 12, 12, 'inout_cubic path',
     lambda k, w: 7 if -4 <= k < 4 else 5,
     lambda w, o: [cue(w.c, 'whoosh_by', -4, pan=0.3, dur=0.8, direction=1, alt='ember_crackle (trail, -12)'),
                   cue(w.t1, 'sparkle', -8)], _tx_carry, 'premium', '12-30')
_reg('Y1', 'zoom through a serif counter', 'type', 21, 0, 'in_expo (vt.zoom)', 7,
     lambda w, o: [cue(w.c, 'reverse_swell', -3, duration=round(w.pre / FPS, 3)), cue(w.c, 'air_zoom', 0),
                   cue(w.c, 'sub_drop', -6)], _tx_counter, 'premium', '18-24')
_reg('Y2', 'light-sweep text-wipe', 'type', 9, 9, 'inout_sine', 4,
     lambda w, o: [cue(w.t0, 'shimmer', -6), cue(w.c, 'whoosh_fast', -6)], _tx_textwipe, '', '14-24')
_reg('Y3', 'kinetic slam cuts', 'type', 40, 12, 'SLAM spring', 3,
     lambda w, o: ([cue(w.c - (len(o.get('words', ('HOOK.', 'STORY.', 'EDIT.'))) - 1 - i) * o.get('beat', 20) / FPS,
                        'impact_soft', 0, pan=0.15 * (-1) ** i)
                    for i in range(len(o.get('words', ('HOOK.', 'STORY.', 'EDIT.')))) if
                    i < len(o.get('words', ('HOOK.', 'STORY.', 'EDIT.'))) - 1]
                   + [cue(w.c, 'riser', -4, duration=0.8), cue(w.c, 'impact_big', 0), cue(w.c, 'sub_drop', -4)]),
     _tx_slams, 'signature', '6-20 per word',
     lambda t, w, o: {'push': 0.6 * sum(K.impulse(t, w.c - j * o.get('beat', 20) / FPS - 0.02, 16.0)
                                        for j in range(len(o.get('words', ('HOOK.', 'STORY.', 'EDIT.')))))})
_reg('Y4', 'glyph-mask bloom reveal', 'type', 28, 0, 'out_cubic', 3,
     lambda w, o: [cue(w.t0, 'shimmer', -6), cue((w.t0 + w.c) / 2, 'whoosh_slow', -6), cue(w.c, 'impact_soft', -8)],
     None, '', '20-36')
_reg('Y5', 'underline-stroke wipe (house mark)', 'type', 24, 0, 'out_cubic -> inout_expo', 5,
     lambda w, o: [cue(w.t0, 'swish_small', -6, align='start', alt='ember_stroke'),
                   cue(w.t0 + (o.get('draw', 10) + (w.pre - o.get('draw', 10)) / 2) / FPS, 'whoosh_fast', -4),
                   cue(w.c, 'impact_soft', -8)], _tx_underline, 'premium', '10 draw-on + 12-16 wipe')
_reg('Y6', 'scramble-decode cut', 'type', 9, 9, 'stepped (scramble)', 3,
     lambda w, o: [cue(w.t0, 'typing', -8, n=8, cps=16), cue(w.c, 'glitch_short', -6), cue(w.t1, 'check_ding', -8)],
     None, '', '15-21')
_reg('L1', 'light-leak burn (ember)', 'light', 8, 8, 'built-in sin envelope', 3,
     lambda w, o: [cue(w.c, 'reverse_swell', -4, duration=round(w.pre / FPS, 3)), cue(w.c, 'shimmer', -8)],
     _tx_leak, 'premium', '12-20 (24-36 dreamy)',
     lambda t, w, o: {'push': o.get('push_gain', 0.2) * K.impulse(t, w.c - 0.02, 16.0),
                      'bloom_scale': 1.0 - 0.6 * math.sin(math.pi * w.u(t)) if w.inside(t) else 1.0})
_reg('L2', 'film burn', 'light', 14, 10, 'in_cubic -> in_expo', 3,
     lambda w, o: [cue(w.c, 'reverse_swell', -3, duration=round(w.pre / FPS, 3), alt='film_burn'),
                   cue(w.c, 'downlifter', -8)], _tx_burn, '', '18-30',
     lambda t, w, o: {'grain': K.lerp(_look_val(o, 'grain', 0.0), 0.035, min(w.env_in(t, 4), w.env_out(t, 4)))}
     if w.inside(t) else {})
_reg('L3', 'exposure-push flash frame', 'light', 0, 4, 'impulse decay 16', 3,
     lambda w, o: [cue(w.c, 'flash_hit', 0)], _tx_cut, 'glue', '2-4', _l3_post)
_reg('L4', 'halation bloom-out wipe', 'light', 10, 10, 'sin^2', 3,
     lambda w, o: [cue(w.c, 'shimmer', -8), cue(w.c, 'reverse_swell', -6, duration=round(w.pre / FPS, 3))],
     _tx_cut, 'premium', '16-24', _l4_post)
_reg('L5', 'anamorphic flare wipe', 'light', 6, 6, 'inout_cubic', 5,
     lambda w, o: [cue(w.c, 'whoosh_fast', -4), cue(w.c, 'shimmer', -8), cue(w.c, 'sparkle', -12)], _tx_flare, '',
     '10-16', _l5_post)
_reg('L6', 'projector / film-gate slip', 'light', 4, 4, 'step (24 fps cadence)', 1,
     lambda w, o: [cue(w.c, 'camera_shutter', -8, alt='projector_rattle (bed, -18)')], None, '', '6-10 + 1 bar judder')
_reg('L7', 'light-beam (god-ray) sweep', 'light', 12, 12, 'inout_sine', 4,
     lambda w, o: [cue(w.c, 'whoosh_slow', -6), cue(w.c, 'shimmer', -8, alt='harmonium_swell')], _tx_beam, 'premium',
     '18-30')
_reg('L8', 'aperture iris close/open', 'light', 9, 11, 'in_cubic / out_back', 3,
     lambda w, o: [cue(w.c - 1 / FPS, 'camera_shutter', 0), cue(w.c + 1 / FPS, 'ui_click', -8),
                   cue(w.t1, 'reverse_swell', -8, duration=0.3)], _tx_iris, '', '8 + 2 + 10')
_reg('D1', 'timeline playhead scrub', 'editor', 30, 10, 'inout_sine pull + inout_expo scrub + SNAP', _d1_samples,
     lambda w, o: [cue(w.t0 + o.get('pull', 10) / FPS, 'slider_drag', -8, align='start',
                       duration=round(w.c - w.t0 - o.get('pull', 10) / FPS, 3), alt='scrub (granular mix re-read)'),
                   cue(w.t0 + (o.get('pull', 10) + 10) / FPS, 'ui_tick', -12), cue(w.c, 'ui_click', 0),
                   cue(w.t1, 'impact_soft', -4)], _tx_scrub, 'editor', '36-60')
_reg('D2', 'razor-tool cut', 'editor', 8, 14, 'out_expo', 5,
     lambda w, o: [cue(w.c, 'ui_click', 0, alt='razor_snip'), cue(w.c + 2 / FPS, 'card_slide', -8)], _tx_razor, 'editor',
     '6-10 + 1 + 8-12')
_reg('D3', 'render-progress-bar wipe', 'editor', 48, 8, 'stepped Track, out_expo tail', 3,
     lambda w, o: [cue(w.t0, 'bar_grow', -8, align='start', duration=round(w.pre / FPS, 3)),
                   cue(w.t0 + 0.55 * w.pre / 48 * 30 / FPS, 'ui_tick', -14), cue(w.t0 + 1.15 * w.pre / 48 * 30 / FPS, 'ui_tick', -14),
                   cue(w.c, 'toast_chime', -4), cue(w.c, 'impact_soft', -6)], _tx_render, 'editor', '30-60 + 8')
_reg('D4', 'keyframe-graph swoosh', 'editor', 10 + int(round(_steep_v() * 18)), 18 - int(round(_steep_v() * 18)),
     'the displayed bezier', lambda k, w: 7 if -4 <= k < 4 else 5,
     lambda w, o: [cue(w.t0 + i * 2.5 / FPS, 'pop', -8, pitch=1.2, alt='keyframe_pop') for i in range(4)]
     + [cue(w.c - 3 / FPS, 'swish_small', -10), cue(w.c, 'whip', -4, direction=1)], _tx_graph, 'editor', '10 + 14-20')
_reg('D5', 'UI window swap (SaaS)', 'editor', 6, 10, 'in_cubic exit / POP enter', 5,
     lambda w, o: [cue(w.c, 'whoosh_fast', -6), cue(w.t1 - 4 / FPS, 'card_slide', 0), cue(w.t1, 'glass_tap', -10)],
     None, '', '12-18')
_reg('D6', 'glitch / datamosh-lite', 'editor', 4, 6, 'stepped (hold 2 f)', 1,
     lambda w, o: [cue(w.t0, 'glitch_short', 0, alt='data_crunch')], None, '', '6-12')
_reg('D7', 'RGB-split chroma shock', 'editor', 0, 3, 'impulse decay 20', 3,
     lambda w, o: [cue(w.c, 'glitch_short', -6), cue(w.c, 'whip', -8, direction=1)], _tx_cut, '', '2-4', _d7_post)
_reg('D8', 'speed-ramp (velocity) cut', 'editor', 7, 7, 'in_expo / out_expo time-warp', 7,
     lambda w, o: [cue(w.c, 'whoosh_fast', -4), cue(w.c, 'riser', -8, duration=0.35), cue(w.c, 'impact_soft', 0)],
     _tx_velocity, '', '10-16')
_reg('D9', 'undo / Ctrl+Z rewind', 'editor', 30, 2, 'in_cubic (reverse)', 5,
     lambda w, o: [cue(w.t0 + 2 / FPS, 'typing', -6, n=2, cps=10),
                   cue(w.c, 'reverse_swell', -6, duration=round(w.pre / FPS - 0.2, 3), lp=3000, alt='tape_rewind'),
                   cue(w.c, 'impact_soft', 0)], _tx_undo, 'editor', '6 + 18-30 + 2', _push_post(0.6))
_reg('O1', 'ink bleed (deep red ink)', 'organic', 36, 0, 'inout_sine radius', 3,
     lambda w, o: [cue(w.t0, 'reverse_swell', -4, duration=0.4, lp=800, alt='ink_bloom'),
                   cue(w.t0 + 0.2, 'whoosh_slow', -10)], _tx_ink, '', '30-45')
_reg('O2', 'smoke wipe', 'organic', 15, 15, 'inout_sine', 3,
     lambda w, o: [cue(w.c, 'whoosh_slow', -6), cue(w.t1, 'impact_soft', -10)], _tx_smoke, '', '24-36')
_reg('O3', 'page tear (black paper)', 'organic', 8, 8, 'in_cubic / out_expo', 5,
     lambda w, o: [cue(w.t0, 'card_slide', -10, alt='paper_tear')], None, '', '12-20')
_reg('O4', 'shatter (glass)', 'organic', 2, 22, 'ballistic', 7,
     lambda w, o: [cue(w.c, 'impact_big', 0, alt='glass_shatter'), cue(w.c, 'sub_drop', -4),
                   cue(w.c, 'glitch_short', -12), cue(w.c + 0.15, 'sparkle', -6)], _tx_shatter, 'signature',
     '15-24 (+10 slow-mo)', _push_post(0.8))
_reg('O5', 'molten pour (ember liquid)', 'organic', 30, 0, 'in_cubic + exp cool', 4,
     lambda w, o: [cue(w.t0, 'whoosh_slow', -6, align='start', alt='molten_pour'), cue(w.c, 'impact_soft', -6)],
     None, '', '24-36')
_reg('O6', 'ember disintegration', 'organic', 36, 12, 'inout_sine front', lambda k, w: 5 if k < 0 else 4,
     lambda w, o: [cue(w.t0, 'sparkle', -12, alt='ember_crackle (align start, -4)'),
                   cue((w.t0 + w.c) / 2, 'whoosh_slow', -8), cue(w.c, 'impact_big', 0), cue(w.c, 'sub_drop', -6)],
     _tx_embers, 'premium', '30-45', _push_post(0.5))

# bible flags: 10 premium (star), 5 editor-signature (scissors), family-allocation signatures, glue
PREMIUM = ('C2', 'C3', 'M1', 'M6', 'Y1', 'Y5', 'L1', 'L4', 'L7', 'O6')
EDITOR = ('D1', 'D2', 'D3', 'D4', 'D9')
ALLOCATION = {'light & film': ('L4', 'L1'), 'digital / editor': ('D1', 'D9'), 'type': ('Y1', 'Y3'),
              'camera + match': ('C3', 'M1'), 'organic + morph': ('O6', 'O4')}
GLUE = ('L3',)
for _k in PREMIUM:
    TX[_k].flag = 'premium'
for _k in EDITOR:
    TX[_k].flag = 'editor'


def _fit_y3(o):
    words = o.get('words', ('HOOK.', 'STORY.', 'EDIT.'))
    o.setdefault('pre', (len(words) - 1) * o.get('beat', 20))
    return o


# =============================================================================================== Plan
class Plan:
    """Transitions between consecutive scenes on one clock (see module docstring).
        plan = X.Plan([('L1', 2.0), ('C3', 4.0, dict(center=(540, 700), r0=200))])
        cv = plan.draw(t, [S0, S1, S2])"""

    def __init__(self, steps):
        st = []
        for s in steps:
            tid, c = s[0], float(s[1])
            o = dict(s[2]) if len(s) > 2 and s[2] else {}
            if tid == 'Y3':
                o = _fit_y3(o)
            st.append((TX[tid], c, o))
        st.sort(key=lambda r: r[1])
        self.steps = st
        self.cuts = [c for _, c, _ in st]
        wins = self.windows()
        for (a0, a1, ia), (b0, b1, ib) in zip(wins, wins[1:]):
            if b0 < a1 - 1e-9:
                raise ValueError('transition windows overlap: %s [%.3f, %.3f) and %s [%.3f, %.3f)' % (ia, a0, a1, ib, b0, b1))

    def windows(self):
        return [(*x.window(c, **o), x.id) for x, c, o in self.steps]

    def windows_of(self, *ids):
        """[(t0, t1)] of the transitions with these ids (all when none are given), e.g. caption quiet zones:
        SC.Captions(words, clear=plan.windows_of('L1', 'L4'))"""
        return [(a, b) for a, b, i in self.windows() if not ids or i in ids]

    def segment(self, t):
        """Index of the scene that owns t outside the windows (HALF rule at each cut)."""
        return sum(1 for c in self.cuts if side_b(t, c))

    def draw(self, t, scenes):
        if len(scenes) != len(self.steps) + 1:
            raise ValueError('need %d scenes for %d transitions' % (len(self.steps) + 1, len(self.steps)))
        for i, (x, c, o) in enumerate(self.steps):
            if x.win(c, **o).inside(t):
                return x(t, c, scenes[i], scenes[i + 1], **o)
        return scenes[self.segment(t)](t)

    def samples(self, t, default=3):
        for x, c, o in self.steps:
            if x.win(c, **o).inside(t):
                return x.samples_at(t, c, default, **o)
        return default

    def post_kw(self, t):
        out = {}
        for x, c, o in self.steps:
            d = x.post_kw(t, c, **o)
            for k, v in d.items():
                if k == 'push':
                    out['push'] = out.get('push', 0.0) + v
                elif k == 'bloom_scale':
                    out[k] = out.get(k, 1.0) * v
                else:
                    out[k] = v
        return out

    def cues(self):
        out = []
        for x, c, o in self.steps:
            out += x.cues(c, **o)
        return sorted(out, key=lambda d: d['t'])


# =============================================================================================== continuity QA
def _u8(cv, t, look='ember', pk=None):
    """Finished sRGB8 frame of a linear canvas (a copy is finished; pk = finish() overrides)."""
    return K.to_srgb8(finish(np.array(cv, copy=True), t, look, **(pk or {})), t)


def frame_step(a, b, thr=25):
    """(mean |a - b| over all channels, fraction of px whose largest channel change > thr) of two sRGB8 frames."""
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return float(d.mean()), float((d.max(-1) > thr).mean())


def edge_scenes(tid, A, B, c=1.0, **o):
    """Wrap two test scenes so they draw what a transition expects the timeline to draw OUTSIDE its window
    (Y1 / Y2: the word on A; M6: the carrier at rest on the path ends; M3: the object on the shared track)."""
    x = TX[tid]
    w = x.win(c, **o)
    before = lambda t: fidx(t, c) < -w.pre
    after = lambda t: fidx(t, c) >= w.post
    if tid == 'Y1':
        ts = counter_word(o.get('word', 'sapna'), o.get('px', 230), o.get('style', 'jw_key'))[0]

        def A2(t, **kw):
            cv = A(t, **kw)
            if before(t):
                ts.draw(cv, o.get('x', K.CX), o.get('y', 900.0))
            return cv
        return A2, B
    if tid == 'Y2' and o.get('word'):
        ts = T.render(o['word'], o.get('style', 'jw_caps'), px=o.get('px', 110))

        def A2(t, **kw):
            cv = A(t, **kw)
            if before(t):
                ts.draw(cv, o.get('x', K.CX), o.get('y', 900.0))
            return cv
        return A2, B
    if tid == 'M6':
        path = o.get('path', ((120, 1300), (460, 980), (760, 760), (980, 520)))
        spr = o.get('sprite') or carrier()

        def A2(t, **kw):
            cv = A(t, **kw)
            if before(t):
                K.draw(cv, spr, path[0][0], path[0][1], scale=o.get('scale', 1.0), mode='add')
            return cv

        def B2(t, **kw):
            cv = B(t, **kw)
            if after(t):
                K.draw(cv, spr, path[-1][0], path[-1][1], scale=o.get('scale', 1.0), mode='add')
            return cv
        return A2, B2
    if tid == 'M3':
        tr = o.get('move') or motion_track(c, w.pre, w.post)
        return (lambda t, move=None, **kw: A(t, move=move if move is not None else tuple(tr(t)), **kw),
                lambda t, move=None, **kw: B(t, move=move if move is not None else tuple(tr(t)), **kw))
    return A, B


# window edges that are designed cuts (not pops): the window opens ON a hit
EDGE_CUTS = {'Y3': 'entry: the first slam hard-cuts the plate on the beat',
             'O4': 'entry: the cracks flash in on the impact frame'}


def edge_steps(tid, c=1.0, A=None, B=None, look='ember', post_kw=False, **o):
    """Continuity at a transition's window edges, measured like the QA frame-step check (finished sRGB8
    frames, one sample): entry = frame -pre-1 (plain A) -> -pre, exit = frame post-1 -> post (plain B), plus
    the plain-scene steps of A and B at the same times as the baseline. Returns {'entry': (mean, frac>25),
    'exit': ..., 'base_a': ..., 'base_b': ...}. post_kw=True applies each frame's own finish overrides
    (exposure pushes ...); False isolates what the transition draws.  X.edge_steps('O6', pre=10, post=5)"""
    x = TX[tid]
    if A is None or B is None:
        A, B = _demo_scenes()
    A0, B0 = A, B
    A, B = edge_scenes(tid, A, B, c, **o)
    w = x.win(c, **o)

    def fr(k, S=None):
        t = c + k / FPS
        if S is not None:                                   # plain scene (baseline): no transition overrides
            return _u8(S(t), t, look)
        pk = dict(x.post_kw(t, c, **o)) if post_kw else {}
        return _u8(x(t, c, A, B, **o), t, look, pk)
    xa = fr(w.post)
    return {'entry': frame_step(fr(-w.pre - 1), fr(-w.pre)), 'exit': frame_step(fr(w.post - 1), xa),
            'after': frame_step(xa, fr(w.post + 1)),          # the next step: pushes / splits keep decaying
            'base_a': frame_step(fr(-w.pre - 1, A0), fr(-w.pre, A0)),
            'base_b': frame_step(fr(w.post - 1, B0), fr(w.post, B0))}


# designed snaps inside a window (not pops): the whole-window spike test skips these steps
SNAPS = {'C8': 'the crash zoom punches in on the 2nd window frame (out_expo)',
         'Y3': 'each slam hard-cuts the plate on its beat',
         'L8': 'the iris re-opens on the first frame after the black frames',
         'D3': 'the stepped render track leaving a hold',
         'D1': 'the scrub monitor switching from A to B at the scrub midpoint'}


def designed_steps(tid, w, **o):
    """Steps k (frame k-1 -> k) of transition tid's window w that are designed snaps (see SNAPS).
    X.designed_steps('Y3', X.TX['Y3'].win(1.0, beat=8), words=('A', 'B', 'C'), beat=8) -> {-16, -8, 0}"""
    if tid == 'C8':
        return {-w.pre + 1}
    if tid == 'Y3':
        n, b = len(o.get('words', ('HOOK.', 'STORY.', 'EDIT.'))), int(o.get('beat', 20))
        return {-(n - 1 - i) * b for i in range(n)}
    if tid == 'L8':
        return {int(math.ceil(o.get('black', 2) / 2.0)) + 1}
    if tid == 'D3':                                      # the track leaves a hold (0 s, 0.55 s, 1.15 s of 1.6 s)
        span = _render_track(0.0).end
        return {-w.pre + 1} | {int(math.floor(-w.pre + th / span * w.pre + d)) for th in (0.55, 1.15) for d in (0, 1)}
    if tid == 'D1':                                      # the monitor's source switches A -> B mid-scrub
        pull = int(o.get('pull', 10))
        t_pull = w.t0 + pull / FPS
        for k in range(-w.pre + pull, 0):
            if K.EASE['inout_expo'](K.clamp((w.c + k / FPS - t_pull) / max(1e-6, w.c - t_pull))) >= 0.5:
                return {k}
    return set()


def window_steps(tid, c=1.0, A=None, B=None, look='ember', **o):
    """Every frame step across a window, measured like edge_steps (finished sRGB8 frames, one sample, no finish
    overrides): {'steps': {k: (mean, frac>25)} for k = -pre-1 .. post+1 (step k = frame k-1 -> k), 'entry',
    'exit', 'after', 'base_a', 'base_b' (as edge_steps), 'spikes': window_spikes(...)}.
    X.window_steps('Y5')['spikes'] == []"""
    x = TX[tid]
    if A is None or B is None:
        A, B = _demo_scenes()
    A0, B0 = A, B
    A, B = edge_scenes(tid, A, B, c, **o)
    w = x.win(c, **o)
    steps, prev = {}, None
    for k in range(-w.pre - 2, w.post + 2):
        t = c + k / FPS
        cur = _u8(x(t, c, A, B, **o), t, look)
        if prev is not None:
            steps[k] = frame_step(prev, cur)
        prev = cur

    def plain(S, ka, kb):
        return frame_step(_u8(S(c + ka / FPS), c + ka / FPS, look), _u8(S(c + kb / FPS), c + kb / FPS, look))
    out = {'steps': steps, 'entry': steps[-w.pre], 'exit': steps[w.post], 'after': steps[w.post + 1],
           'base_a': plain(A0, -w.pre - 1, -w.pre), 'base_b': plain(B0, w.post - 1, w.post)}
    out['spikes'] = window_spikes(tid, out, w, **o)
    return out


def window_spikes(tid, ws, w, k_base=3.0, k_nb=2.0, frac_floor=0.02, **o):
    """Pops INSIDE a window: steps k (frame k-1 -> k) more than k_base x the plain-scene step AND more than k_nb x
    BOTH neighbouring steps, in mean or in share of px > 25 levels (share floor 2 %). Skips the cut (k = -1, 0),
    EDGE_CUTS entries and designed_steps(). ws = window_steps(...) -> [(k, mean, frac)] (should be [])."""
    st = ws['steps']
    ks = sorted(st)
    base = (max(ws['base_a'][0], ws['base_b'][0]), max(ws['base_a'][1], ws['base_b'][1]))
    skip = {-1, 0} | designed_steps(tid, w, **o) | ({-w.pre} if tid in EDGE_CUTS else set())
    out = []
    for a, k, b in zip(ks, ks[1:], ks[2:]):
        if k in skip:
            continue
        m, f = st[k]
        if (m > k_base * base[0] and m > k_nb * st[a][0] and m > k_nb * st[b][0]) or \
                (f > max(k_base * base[1], frac_floor) and f > k_nb * st[a][1] and f > k_nb * st[b][1]):
            out.append((k, round(m, 2), round(f, 4)))
    return out


def y5_handover(c=1.0, A=None, B=None, look='ember', samples=5, ks=range(-17, -8), roi=(150, 1040, 930, 1140), **o):
    """Y5 stroke -> band hand-over measured like render.py (K.render_frame, `samples`, finish, sRGB8): mean
    Rec.709 luma of the underline ROI per frame k -> (ks, luma, steps). A one-frame pop shows as a step more
    than 1.5x both of its neighbours (the QA criterion for k = -16 .. -10)."""
    x = TX['Y5']
    if A is None or B is None:
        A, B = _demo_scenes()
    x0, y0, x1, y1 = roi
    lum = []
    for k in ks:
        t = c + k / FPS
        cv = K.render_frame(lambda tt: x(tt, c, A, B, **o), t, samples=samples)
        r = _u8(cv, t, look, x.post_kw(t, c, **o))[y0:y1, x0:x1].astype(np.float32)
        lum.append(float((r[..., 0] * 0.2126 + r[..., 1] * 0.7152 + r[..., 2] * 0.0722).mean()))
    return list(ks), lum, [b - a for a, b in zip(lum, lum[1:])]


def _post_edge_jumps(tid, c=1.0, look='ember', **o):
    """finish() overrides (other than the decaying push / rgb_split impulses) that differ between the last
    window frame and the first frame after it (or the frame before the window and the first one)."""
    x = TX[tid]
    w = x.win(c, **o)
    dflt = {'bloom_scale': 1.0, 'bloomout': 0.0}
    out = []
    for ka, kb in ((-w.pre - 1, -w.pre), (w.post - 1, w.post)):
        pa, pb = x.post_kw(c + ka / FPS, c, **o), x.post_kw(c + kb / FPS, c, **o)
        for key in set(pa) | set(pb):
            if key in ('push', 'rgb_split'):
                continue
            va = pa.get(key, dflt.get(key, _look_val({'look': look}, key)))
            vb = pb.get(key, dflt.get(key, _look_val({'look': look}, key)))
            if abs(float(va) - float(vb)) > 0.02 * (1 + abs(float(vb))):
                out.append('%s %s %.3f -> %.3f at k=%d' % (tid, key, va, vb, kb))
    return out


# =============================================================================================== selftest
def _demo_scenes(clock=None):
    """Two cheap, clearly different scenes for tests: A = ember + 'A' plate, B = noir_ember + 'B' plate.
    They accept move=(x, y) (M3) and record their own cost in clock (a list) when given."""
    def mk(look, word, col):
        ring = K.ring(200, 10, K.C[col] * 1.5)

        def S(t, move=None, **kw):
            t0 = time.perf_counter()
            cv = K.background(look, t, bokeh=0.6)
            T.render(word, 'jw_caps_bold', px=320).draw(cv, K.CX + 60 * math.sin(t * 2.0), 900)
            K.draw(cv, ring, K.CX, 1300, mode='add')
            if move is not None:
                K.draw(cv, _spark(14.0), move[0], move[1], mode='add')
            if clock is not None:
                clock.append(time.perf_counter() - t0)
            return cv
        return S
    return mk('ember', 'A', 'FLAME'), mk('noir_ember', 'B', 'GOLD')


def _edge_ok(st, base, k_mean=1.5, floor=0.003):
    """A window-edge step is continuous when it is within 1.5x the plain-scene step (mean) and changes few
    pixels by > 25 levels (<= max(3x the plain step's share, 0.3 %))."""
    return st[0] <= k_mean * base[0] + 1e-6 and st[1] <= max(3.0 * base[1], floor)


def selftest():
    """Checks every implemented transition (frames outside the window are the plain scenes, CONTINUITY at
    both window edges: the first / last window frame vs the plain neighbour within 1.5x the plain-scene step,
    finish() overrides back to the look's values on the edge frames, the HALF rule, purity, finite pixels,
    catalog SFX names, frame counts, C2's cut <= 2 % near-white, D1's pull <= 0.2 of its move per frame),
    measures cost and writes contact sheets."""
    os.makedirs(K.SELFTEST, exist_ok=True)
    clock = []
    A, B = _demo_scenes(clock)
    fails = []
    c = 1.0
    th = (135, 240)
    rows = []
    timings = {}
    edges = {}
    wsteps = {}
    opts = {'Y1': dict(word='sapna'), 'Y2': dict(word='EDIT'), 'Y3': dict(words=('HOOK.', 'STORY.', 'EDIT.'), beat=8),
            'C2': dict(center=(540, 900)), 'M1': dict(a=(540, 1300, 200), b=(540, 1300, 200))}
    assert len(TX) == 43, len(TX)
    for need in PREMIUM + EDITOR + ('Y3', 'O4', 'L3'):
        if not TX[need].implemented:
            fails.append('%s not implemented' % need)
    for tid, x in TX.items():
        cs = x.cues(c, **opts.get(tid, {}))
        bad = check_cues(cs)
        if bad:
            fails.append('%s unknown sfx %s' % (tid, bad))
        if not x.implemented:
            continue
        o = dict(opts.get(tid, {}))
        if tid == 'Y3':
            o = _fit_y3(o)
        w = x.win(c, **o)
        # outside the window: the frame before it is plain A, the frame after it plain B (B: L3/D7 own post)
        ta, tb = w.t0 - 1 / FPS, w.t1
        da = float(np.abs(x(ta, c, A, B, **o) - A(ta)).max())
        db = float(np.abs(x(tb, c, A, B, **o) - B(tb)).max())
        if da > 1e-5 or db > 1e-5:
            fails.append('%s outside-window mismatch A %.3g B %.3g' % (tid, da, db))
        # continuity: the first / last WINDOW frame against its plain neighbour (what the eye sees as a pop), and
        # every step INSIDE the window (fix round 2: a pop one frame inside a window, e.g. Y5's band at k=-14,
        # passed the edge check by construction)
        es = window_steps(tid, c, A, B, **o)
        ep = edge_steps(tid, c, A, B, post_kw=True, **o)
        edges[tid] = (es, ep, w)
        wsteps[tid] = (es, w)
        if es['spikes']:
            fails.append('%s pop inside the window (k, mean step, share px > 25): %s (plain %.2f / %.2f %%)'
                         % (tid, es['spikes'], max(es['base_a'][0], es['base_b'][0]),
                            100 * max(es['base_a'][1], es['base_b'][1])))
        if w.pre > 0 and tid not in EDGE_CUTS and not _edge_ok(es['entry'], es['base_a']):
            fails.append('%s entry pop: step %.2f / %.2f %% px > 25 (plain %.2f / %.2f %%)'
                         % (tid, es['entry'][0], 100 * es['entry'][1], es['base_a'][0], 100 * es['base_a'][1]))
        if not _edge_ok(es['exit'], es['base_b']):
            fails.append('%s exit pop: step %.2f / %.2f %% px > 25 (plain %.2f / %.2f %%)'
                         % (tid, es['exit'][0], 100 * es['exit'][1], es['base_b'][0], 100 * es['base_b'][1]))
        # with the finish overrides: exposure pushes / the D7 split decay smoothly past the window, so the exit
        # step is judged against the next (outside) step; the entry against the plain step
        if ep['exit'][1] > max(2.0 * ep['after'][1], 0.005) or \
                (w.pre > 0 and tid not in EDGE_CUTS and ep['entry'][1] > max(3.0 * es['base_a'][1], 0.005)):
            fails.append('%s edge pop with finish overrides: entry %.2f %%, exit %.2f %% px > 25 (next step %.2f %%)'
                         % (tid, 100 * ep['entry'][1], 100 * ep['exit'][1], 100 * ep['after'][1]))
        fails += _post_edge_jumps(tid, c, **o)
        # sheet columns: early in the window, the last A frame, the cut, mid-settle (the edge frames themselves
        # equal the plain scenes now)
        ks = [-w.pre + max(1, w.pre // 3), -1, 0, (w.post - 1) // 2] if w.pre > 0 else [0, 1, 2, w.post - 1]
        if tid in ('Y1', 'O1', 'O5'):
            ks = [-w.pre, -w.pre // 2, -2, -1]
        thumbs = []
        for k in ks:
            tt = c + k / FPS
            x(tt, c, A, B, **o)                                  # warm caches
            del clock[:]
            t0 = time.perf_counter()
            cv = x(tt, c, A, B, **o)
            dt = (time.perf_counter() - t0 - sum(clock)) * 1e3     # the transition's own cost (scenes excluded)
            timings.setdefault(tid, []).append(dt)
            cv2_ = x(tt, c, A, B, **o)
            if not np.array_equal(cv, cv2_):
                fails.append('%s impure at k=%d' % (tid, k))
            if not np.isfinite(cv).all() or cv.shape != (H, W, 4):
                fails.append('%s bad pixels at k=%d' % (tid, k))
            pk = x.post_kw(tt, c, **o)
            out = finish(cv, tt, 'ember', **pk)
            u8 = K.to_srgb8(out, tt)
            thumbs.append(cv2.resize(u8, th, interpolation=cv2.INTER_AREA))
        rows.append((tid, thumbs, x))
    # HALF rule: sub-samples of frame c-1 / c stay on their side
    for s_ in (-1 / 120, 0.0, 1 / 120):
        if side_b(c - 1 / FPS + s_, c) or not side_b(c + s_, c):
            fails.append('HALF rule broken at %.4f' % s_)
    # Plan: overlapping windows refused, segments right, samples policy
    try:
        Plan([('L1', 1.0), ('C3', 1.2)])
        fails.append('Plan accepted overlapping windows')
    except ValueError:
        pass
    pl = Plan([('L1', 1.0), ('C3', 3.0)])
    if pl.segment(0.5) != 0 or pl.segment(2.0) != 1 or pl.segment(3.5) != 2:
        fails.append('Plan.segment')
    if pl.samples(3.0 - 2 / FPS) != 7 or pl.samples(2.0) != 3:
        fails.append('Plan.samples %s %s' % (pl.samples(3.0 - 2 / FPS), pl.samples(2.0)))
    if not pl.post_kw(1.0).get('push', 0) > 0.15 or not pl.post_kw(1.0).get('bloom_scale', 1) < 0.6:
        fails.append('Plan.post_kw push')
    # every suggested cue renders with its params (catalog name + valid parameters)
    import audio as SFXA
    seen = set()
    for tid, x in TX.items():
        for cu in x.cues(c, **opts.get(tid, {})):
            key = (cu['name'], tuple(sorted(cu['params'].items())))
            if key in seen:
                continue
            seen.add(key)
            try:
                snd = SFXA.sound(cu['name'], **cu['params'])
                if not np.isfinite(np.asarray(snd)).all():
                    fails.append('%s cue %s not finite' % (tid, cu['name']))
            except Exception as e:                                   # noqa: BLE001 - report every bad cue
                fails.append('%s cue %s%s: %r' % (tid, cu['name'], cu['params'], e))
    cov = leak_coverage()
    if cov < 0.70:
        fails.append('L1 leak coverage %.2f' % cov)
    # the demo's short windows (C3 12+3, O6 10+5, L1 6+6) stay continuous too
    for tid, o in (('C3', dict(pre=12, post=3, center=(540.0, 760.0), r0=200.0)), ('O6', dict(pre=10, post=5)),
                   ('L1', dict(pre=6, post=6, seed=4)), ('O6', dict(pre=36, post=4))):
        es = window_steps(tid, c, A, B, **o)
        lab = '%s %d+%d' % (tid, o['pre'], o['post'])
        edges[lab] = (es, edge_steps(tid, c, A, B, post_kw=True, **o), TX[tid].win(c, **o))
        wsteps[lab] = (es, TX[tid].win(c, **o))
        for side, base in (('entry', 'base_a'), ('exit', 'base_b')):
            if not _edge_ok(es[side], es[base]):
                fails.append('%s %s pop: step %.2f / %.2f %% px > 25' % (lab, side, es[side][0], 100 * es[side][1]))
        if es['spikes']:
            fails.append('%s pop inside the window: %s' % (lab, es['spikes']))
    # Y5 hand-over (fix round 2), measured like render.py (5 samples): the stroke grows into the band with no
    # one-frame step above 1.5x both of its neighbours on k = -16 .. -10 (it used to jump 3.1x in one frame)
    y5k, y5l, y5s = y5_handover(c, A, B)
    y5bad = [(y5k[i + 1], round(y5s[i], 1)) for i in range(1, len(y5s) - 1)
             if -16 <= y5k[i + 1] <= -10 and abs(y5s[i]) > 2.0
             and abs(y5s[i]) > 1.5 * max(abs(y5s[i - 1]), abs(y5s[i + 1]))]
    if y5bad:
        fails.append('Y5 hand-over pop (k, luma step): %s' % y5bad)
    # Y3: every word is on screen ON its hit frame (3 samples), not one frame later
    o3 = _fit_y3(dict(opts['Y3']))
    w3 = TX['Y3'].win(c, **o3)
    y3hit = []
    for k in sorted(designed_steps('Y3', w3, **o3)):
        tt = c + k / FPS
        cvw = K.render_frame(lambda t_: TX['Y3'](t_, c, A, B, **o3), tt, samples=3)
        plate = B if k == 0 else (B, A)[(-k // o3['beat']) % 2]
        cvp = K.render_frame(plate, tt, samples=3)
        y3hit.append(round(float(np.abs(cvw[700:1100, 140:940, :3] - cvp[700:1100, 140:940, :3]).mean()), 4))
    if min(y3hit) < 0.05:
        fails.append('Y3 word missing on its hit frame: mean |word - plate| %s' % y3hit)
    # D1: the sample policy follows pull=, and the chrome (timecode) never draws over the moving monitor
    o1 = dict(pull=16, pre=36)
    w1b = TX['D1'].win(c, **o1)
    s16 = [TX['D1'].samples_at(c + k / FPS, c, **o1) for k in range(-w1b.pre, -w1b.pre + 16)]
    if min(s16) < 7 or TX['D1'].samples_at(c + (-w1b.pre + 16) / FPS, c, **o1) != 3:
        fails.append('D1 pull=16 samples %s' % s16)
    d1over = []
    for k in (-27, -26, -25, 3, 4, 5):
        tt = c + k / FPS
        dl = np.abs(TX['D1'](tt, c, A, B) - TX['D1'](tt, c, A, B, label=False))[..., :3].max(-1)
        p_ = _d1_p(tt, TX['D1'].win(c), 10, 'inout_sine')
        s_, cy_ = K.lerp(1.0, _NLE_MON[2], p_), K.lerp(K.CY, _NLE_MON[1], p_)
        cx_ = K.lerp(K.CX, _NLE_MON[0], p_)
        y0_, y1_ = int(cy_ - H * s_ / 2) + 24, int(cy_ + H * s_ / 2) - 24
        x0_, x1_ = max(0, int(cx_ - W * s_ / 2) + 24), min(W, int(cx_ + W * s_ / 2) - 24)
        d1over.append(float(dl[max(0, y0_):min(H, y1_), x0_:x1_].max()))
    if max(d1over) > 1e-4:
        fails.append('D1 timecode drawn over the monitor: %s' % [round(v, 4) for v in d1over])
    # C2: the swap hides in a warm burn, never a white wash (<= 2 % of px with every channel > 200 at the cut)
    nw = []
    for k in (0, 1):
        tt = c + k / FPS
        u8 = _u8(TX['C2'](tt, c, A, B, **opts['C2']), tt, 'ember', TX['C2'].post_kw(tt, c, **opts['C2']))
        nw.append(float((u8.min(-1) > 200).mean()))
    if max(nw) > 0.02:
        fails.append('C2 cut near-white %.1f %%' % (100 * max(nw)))
    # D1: the pull-back never moves more than 20 % of its travel in one frame (the bible's out_expo moved 54 %)
    w1 = TX['D1'].win(c)
    pv = [_d1_p(c + k / FPS, w1, 10, 'inout_sine') for k in range(-w1.pre, w1.post)]
    dmax = max(abs(b_ - a_) for a_, b_ in zip(pv, pv[1:]))
    if dmax > 0.2:
        fails.append('D1 pull-back moves %.2f of its travel in one frame' % dmax)
    # contact sheets (two pages)
    import PIL.Image as Im
    import PIL.ImageDraw as Dr
    from PIL import ImageFont
    fnt = ImageFont.truetype(os.path.join(K.FONTS, 'JetBrainsMono-Medium.ttf'), 18)
    paths = []
    per = 13
    for pg in range(0, len(rows), per):
        chunk = rows[pg:pg + per]
        sheet = Im.new('RGB', (360 + 4 * (th[0] + 6), len(chunk) * (th[1] + 8) + 8), (12, 8, 8))
        dr = Dr.Draw(sheet)
        for r, (tid, thumbs, x) in enumerate(chunk):
            y0 = 8 + r * (th[1] + 8)
            ms = np.median(timings[tid])
            dr.text((10, y0 + 10), '%s %s' % (tid, x.flag), fill=(255, 140, 60), font=fnt)
            for li, line in enumerate((x.name[:30], x.name[30:60], '%d+%d f, ease %s' % (x.pre, x.post, x.ease[:14]),
                                       'samples %s  %.0f ms' % (x.samples_at(c - 1 / FPS, c), ms))):
                dr.text((10, y0 + 40 + 24 * li), line, fill=(230, 220, 210), font=fnt)
            for i, tb in enumerate(thumbs):
                sheet.paste(Im.fromarray(tb), (360 + i * (th[0] + 6), y0))
        p = os.path.join(K.SELFTEST, 'jawad_tx_sheet%d.png' % (pg // per + 1))
        sheet.save(p)
        paths.append(p)
    print('transitions implemented: %d / %d' % (sum(x.implemented for x in TX.values()), len(TX)))
    print('median ms per transition frame, scenes excluded:',
          {k: round(float(np.median(v)), 0) for k, v in timings.items()})
    print('L1 leak coverage at peak: %.2f;  cues rendered: %d distinct' % (cov, len(seen)))
    print('C2 near-white px at the cut (k=0, 1): %.2f %%, %.2f %%;  D1 largest pull step per frame: %.3f of the move'
          % (100 * nw[0], 100 * nw[1], dmax))
    print('window-edge continuity (mean step / % px > 25; drawn | with finish overrides; plain-scene step in [ ]):')
    for lab, (es, ep, w) in edges.items():
        print('  %-9s %2d+%-2d entry %5.2f/%5.2f%% | %5.2f/%5.2f%% [%4.2f/%4.2f%%]   exit %5.2f/%5.2f%% | %5.2f/%5.2f%% '
              '[%4.2f/%4.2f%%]%s' % (lab, w.pre, w.post, es['entry'][0], 100 * es['entry'][1], ep['entry'][0],
                                    100 * ep['entry'][1], es['base_a'][0], 100 * es['base_a'][1], es['exit'][0],
                                    100 * es['exit'][1], ep['exit'][0], 100 * ep['exit'][1], es['base_b'][0],
                                    100 * es['base_b'][1], ('   (' + EDGE_CUTS[lab] + ')') if lab in EDGE_CUTS else ''))
    print('Y5 hand-over, ROI mean luma at k=%d..%d (5 samples): %s' % (y5k[0], y5k[-1], [round(v, 1) for v in y5l]))
    print('Y3 word on its hit frames (mean |word - plate| in the word box, 3 samples): %s' % y3hit)
    print('D1 pull=16 samples on the pull frames: %s; timecode diff inside the moving monitor: %.1e'
          % (s16, max(d1over)))
    lp = os.path.join(K.SELFTEST, 'jawad_tx_window_steps.log')
    with open(lp, 'w') as fh:
        for lab, (es, w) in wsteps.items():
            fh.write('%s %d+%d %s  spikes=%s\n' % (lab.replace(' ', '_'), w.pre, w.post, ' '.join(
                '%d:%.1f/%.1f' % (k, m, 100 * f_) for k, (m, f_) in sorted(es['steps'].items())), es['spikes']))
    print('whole-window steps (every frame of every window; spikes = steps > 3x plain and > 2x both neighbours, '
          'cut / designed snaps skipped):', sum(len(es['spikes']) for es, _ in wsteps.values()), 'spikes ->', lp)
    for p in paths:
        print('->', p)
    if fails:
        print('FAIL:', *fails, sep='\n  ')
        return False
    print('jawad_tx selftest OK')
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('selftest', '--selftest'):
        sys.exit(0 if selftest() else 1)
    print(__doc__)
