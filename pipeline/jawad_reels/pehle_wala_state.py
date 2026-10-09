"""pehle_wala_state.py - the pure STATE CLOCK of reel C26 "Pehle Wala Hi Theek Tha" (owner: motion-timeline-builder).

Everything the frame under review does is a pure function of STATE TIME s (seconds):
    body (hook A, f0-f831)          s = t
    payoff / end-card world P(t)    s = t - DUR     (negative: v1, "Approved", no pins; frame 0's past)
    D9 rewind source                s = tau          (W_core(tau): every note un-happens on its own)
The ambient clock a (steam, glass yaw, glitter twinkle, bokeh) equals s everywhere except hook B's frozen head.

Sources: brand_reels/design/reels/pehle_wala/HANDOFF.md section 2 (frame-exact beat table, D2 drawer at f656) and
BRIEF.md r2 sections 5.2, 6.2, 6.3, 6.3.1 (pins, changes, the client's loop-tail marker), 7.

    import pehle_wala_state as S
    st = S.state(s)            # dict: counter, chip, logo, every ad change, shake, pins, thread, drawer, hover, dots
    S.pre1(s)                  # pin 1's loop-tail marker (x, y, opacity) of the disc centre for s in [-1.5, 5/30)
    S.counter_value(s)         # odometer value (4-frame roll ending on each change frame)
    S.yaw(a), S.steam_phase(s) # glass yaw (deg, Python float) / integrated steam clock
    S.LANDINGS                 # frames of every pin landing (post's pin ticks, QA)

Rules applied here: discrete switches use the frame-centre rule on(s, f) (every motion-blur sample of frame f is on
the new side, none of frame f - 1), continuous moves use the exact s; springs start from where the value was
(K.spring is 0 at d = 0); exits are in_cubic; nothing here allocates images.
"""
import bisect
import math

import jawad_kit                                   # noqa: F401  FIRST
from jawad_kit import K
import jawad_tx as X

FPS = 30
HALF = 0.5 / FPS
NF = 1024
DUR = NF / FPS                                    # 34.1333 s = 16 bars at 112.5 BPM (16 f / beat)


def F(n):
    """frames -> seconds"""
    return n / FPS


def on(s, f):
    """True on frame f and later for every motion-blur sample (frame-centre rule: s * 30 + 0.5 >= f)."""
    return s * FPS + 0.5 >= f


def since(s, f):
    return s - f / FPS


def ramp_f(s, f0, nf, ease='inout_sine'):
    """Eased 0..1 over frames [f0, f0 + nf] (state time)."""
    return K.ramp(s, f0 / FPS, (f0 + nf) / FPS, ease)


def spring(d, preset='POP'):
    return X.spring(max(0.0, d), preset)


def ease(name, u):
    return float(K.EASE[name](min(1.0, max(0.0, u))))


# ============================================================================================ the notes (BRIEF 6.3)
# (n, version after the note, land frame, reviewer, text lines, marker tip, card centre (client) or rect (Mummy))
PINS = [
    (1, 2, 8, 'C', ('Logo thora bara?',), (470, 506), (712, 540)),
    (2, 3, 64, 'C', ('Aur bara.',), (560, 612), (760, 540)),
    (3, 4, 96, 'C', ('Thora left.',), (560, 600), (300, 680)),
    (4, 5, 128, 'C', ('Thora aur pop karo',), (515, 1000), (440, 880)),
    (5, 6, 192, 'C', ('Background white kar do,', 'clean lagega'), (250, 1120), (450, 970)),
    (6, 7, 224, 'C', ('Bhaap nazar nahi aa rahi',), (515, 690), (600, 570)),
    (7, 8, 256, 'C', ('Music thora energetic',), (540, 800), (540, 680)),
    (8, 9, 288, 'C', ('Glass thora chamkao',), (600, 980), (430, 860)),
    (9, 10, 320, 'C', ('Font fun wala karo',), (700, 1130), (440, 1000)),
    (10, 11, 352, 'C', ('Har cheez pe shadow daalo',), (810, 800), (520, 640)),
    (11, 12, 384, 'M', ('Mujhe pasand nahi aaya.',), (150, 600), (180, 560, 805, 678)),
    (12, 13, 400, 'M', ('Background wapas dark karo',), None, (180, 686, 897, 770)),
    (13, 14, 416, 'M', ('Aur glitter.',), None, (180, 778, 470, 862)),
    (14, 15, 432, 'M', ('Logo bhi bara.',), None, (180, 870, 553, 954)),
    (15, 16, 448, 'C', ('Thora cinematic',), (515, 790), (640, 640)),
    (16, 17, 480, 'C', ('Price bhi daal do',), (840, 720), (640, 560)),
    (17, 18, 496, 'C', ('Bhaap aur zyada',), (515, 690), (680, 900)),
    (18, 19, 512, 'C', ('Sab kuch thora bara',), (540, 848), (560, 600)),
    (19, 20, 544, 'C', ('Call now bhi likho',), (540, 1100), (540, 940)),
    (20, 21, 576, 'C', ('Aur pop.',), (260, 880), (490, 760)),
    (21, 22, 592, 'C', ('Logo aur bara.',), (400, 600), (600, 680)),
    (22, 23, 608, 'C', ('Shadow kam karo',), (800, 1180), (560, 950)),
    (23, 24, 624, 'C', ('Shadow wapas.',), (800, 1180), (560, 950)),
    (24, 25, 640, 'C', ('Aur energetic',), (540, 800), (540, 640)),
    (25, 26, 656, 'C', ('Thora left.',), (400, 600), (560, 660)),
    (26, 27, 672, 'C', ('Thora right.',), (400, 600), (600, 660)),
]
PAYOFF = (27, None, 768, 'C', ('Pehle wala hi theek tha.',), (515, 900), (540, 760))
F_HOVER, F_FREEZE, F_PAYOFF = 704, 752, 768
CHANGE_FRAMES = [32] + [p[2] for p in PINS[1:]]        # v2 .. v27 (pin 1 lands at f8, its change is f32)
assert len(CHANGE_FRAMES) == 26
LANDINGS = [p[2] for p in PINS] + [F_PAYOFF]
CLIENT = [p for p in PINS if p[3] == 'C']
THREAD = [p for p in PINS if p[3] == 'M']
MUMMY_TIP = (150, 600)
DISC_UP = 34.0                                         # disc centre = tip + (0, -34)
FALL = 48.0                                            # px of the L-3 .. L fall


def next_land(i):
    """Land frame that collapses pin i's card (BRIEF 6.3: (next L) - 2 .. (next L) + 4); the thread uses f448."""
    p = PINS[i]
    if p[3] == 'M':
        return 448
    for q in PINS[i + 1:]:
        if q[3] == 'C' or q[0] == 11:
            return q[2]
    return F_HOVER


# ============================================================================================ counter (UI5)
def counter_value(s):
    """v1 .. v27 with a 4-frame odometer roll that ENDS on each change frame (inout_cubic)."""
    f = s * FPS
    i = bisect.bisect_right(CHANGE_FRAMES, f + 1e-9)          # changes already reached
    v = 1 + i
    if i < len(CHANGE_FRAMES):
        c = CHANGE_FRAMES[i]
        if f > c - 4:
            v += ease('inout_cubic', (f - (c - 4)) / 4.0)
    return float(v)


def version(s):
    """Integer version on screen (frame-centre rule)."""
    return 1 + sum(1 for c in CHANGE_FRAMES if on(s, c))


# ============================================================================================ ambient: yaw + steam
YAW_AMP, YAW_PERIOD = 5.0, 4 * 64 / FPS              # 4 bars = 8.5333 s, so yaw(a - DUR) == yaw(a)


def yaw(a):
    """Glass yaw in degrees as a PYTHON float (np.float64 crashes Asset3D._flow_interp, SHARED_REQUESTS #12)."""
    return float(YAW_AMP * math.sin(2.0 * math.pi * float(a) / YAW_PERIOD))


# steam speed (x real time) as a piecewise-linear function of state time: slow-mo from v16, near-freeze in the drop-out
_SPEED = [(F(448), 1.0), (F(456), 0.3), (F(752), 0.3), (F(755), 0.06)]


def steam_speed(x):
    if x <= _SPEED[0][0]:
        return 1.0
    for (x0, v0), (x1, v1) in zip(_SPEED, _SPEED[1:]):
        if x <= x1:
            return v0 + (v1 - v0) * (x - x0) / (x1 - x0)
    return _SPEED[-1][1]


def steam_phase(x):
    """Integral of steam_speed from 0 to x (the steam's own clock; runs backwards inside the rewind)."""
    x = float(x)
    if x <= _SPEED[0][0]:
        return x
    p = _SPEED[0][0]
    for (x0, v0), (x1, v1) in zip(_SPEED, _SPEED[1:]):
        if x <= x1:
            vx = v0 + (v1 - v0) * (x - x0) / (x1 - x0)
            return p + 0.5 * (v0 + vx) * (x - x0)
        p += 0.5 * (v0 + v1) * (x1 - x0)
    return p + _SPEED[-1][1] * (x - _SPEED[-1][0])


def steam_clock(s, a):
    """Steam time for state s and ambient a (a == s except in hook B's frozen head)."""
    if a is None or a == s:
        return steam_phase(s)
    return steam_phase(s) + steam_speed(s) * (a - s)


# ============================================================================================ shake (v8 / v25)
_SHAKE_BEATS = [f for f in range(256, 752, 16) if f not in (384, 400) and not (448 < f < 512 and f != 480)]


def shake(s):
    """Player-layer judder (dx, dy) px: damped sin on every drum beat from v8 (peak 5 px), 8 px from v25, fading
    to 0 over 23.467-24.0; no hits in the 2 drum-less Mummy beats, half-time in the 'cinematic' bar 7."""
    if not on(s, 256):
        return 0.0, 0.0
    f = s * FPS
    j = bisect.bisect_right(_SHAKE_BEATS, f) - 1
    if j < 0:
        return 0.0, 0.0
    b = _SHAKE_BEATS[j]
    amp = 8.0 if b >= 640 else 5.0
    amp *= 1.0 - K.ramp(s, 23.4667, 24.0, 'inout_sine')
    if amp <= 1e-4:
        return 0.0, 0.0
    d = s - b / FPS
    if d < 0:
        return 0.0, 0.0
    e = math.exp(-14.0 * d) / 0.7003                    # normalised: the first peak equals amp
    return amp * math.sin(2 * math.pi * 9.0 * d) * e, 0.6 * amp * math.sin(2 * math.pi * 7.0 * d) * e


# ============================================================================================ pin 1's loop-tail marker
HOVER_C = (850.0, 560.0)
GLIDE_PTS = ((715.0, 500.0), (600.0, 436.0), (470.0, 424.0))
S_GLIDE0, S_GLIDE_K, S_PIN1 = -0.36, -0.10, 5.0 / FPS


def _pre1_hover(s):
    e = ease('out_cubic', (s + 1.5) / 0.3)
    x, y = 784.0 + 66.0 * e, 196.0 + 364.0 * e
    if s >= -1.3:
        u = s + 1.3
        a = ease('inout_sine', u / 0.4)
        x += a * 30.0 * math.sin(2 * math.pi * 0.45 * u)
        y += a * 15.0 * math.sin(2 * math.pi * 0.70 * u)
    return x, y


def _centripetal(pts, n=400):
    """Dense samples of a centripetal Catmull-Rom spline through pts (phantom end points by reflection)."""
    import numpy as np
    P = [np.asarray(p, float) for p in pts]
    P = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + max(1e-6, float(np.linalg.norm(p1 - p0)) ** 0.5)
        t2 = t1 + max(1e-6, float(np.linalg.norm(p2 - p1)) ** 0.5)
        t3 = t2 + max(1e-6, float(np.linalg.norm(p3 - p2)) ** 0.5)
        for tt in np.linspace(t1, t2, n, endpoint=(i == len(P) - 3)):
            a1 = (t1 - tt) / (t1 - t0) * p0 + (tt - t0) / (t1 - t0) * p1
            a2 = (t2 - tt) / (t2 - t1) * p1 + (tt - t1) / (t2 - t1) * p2
            a3 = (t3 - tt) / (t3 - t2) * p2 + (tt - t2) / (t3 - t2) * p3
            b1 = (t2 - tt) / (t2 - t0) * a1 + (tt - t0) / (t2 - t0) * a2
            b2 = (t3 - tt) / (t3 - t1) * a2 + (tt - t1) / (t3 - t1) * a3
            out.append((t2 - tt) / (t2 - t1) * b1 + (tt - t1) / (t2 - t1) * b2)
    return np.array(out)


_GLIDE = {}


def _glide_path():
    if 'p' not in _GLIDE:
        import numpy as np
        pts = (_pre1_hover(S_GLIDE0),) + GLIDE_PTS
        c = _centripetal(pts)
        seg = np.linalg.norm(np.diff(c, axis=0), axis=1)
        L = np.concatenate([[0.0], np.cumsum(seg)])
        _GLIDE['p'] = (c, L / L[-1])
    return _GLIDE['p']


def _hermite(x, x0, y0, m0, x1, y1, m1):
    h = x1 - x0
    u = (x - x0) / h
    u2, u3 = u * u, u * u * u
    return ((2 * u3 - 3 * u2 + 1) * y0 + (u3 - 2 * u2 + u) * h * m0 + (-2 * u3 + 3 * u2) * y1 +
            (u3 - u2) * h * m1)


def _glide_w(s):
    """Arc-length fraction of the glide: monotone cubic Hermite (-0.36, 0, 0) -> (-0.1, 0.373, 1.782) -> (5/30, 1, 0)."""
    if s <= S_GLIDE0:
        return 0.0
    if s <= S_GLIDE_K:
        return _hermite(s, S_GLIDE0, 0.0, 0.0, S_GLIDE_K, 0.373, 1.782)
    if s < S_PIN1:
        return _hermite(s, S_GLIDE_K, 0.373, 1.782, S_PIN1, 1.0, 0.0)
    return 1.0


def pre1(s):
    """Pin 1's marker before its own fall (BRIEF 6.3.1): disc centre (x, y) and opacity for s in [-1.5, 5/30), else
    None. entry 32.633-32.933 from (784, 196), hover about (850, 560) (+-30 / +-15 px at 0.45 / 0.70 Hz), glide
    from the card exit (33.773) through (715, 500), (600, 436) to (470, 424) on f5 (arc-length, Hermite time warp)."""
    if s < -1.5 or s >= S_PIN1:
        return None
    import numpy as np
    op = ease('inout_sine', (s + 1.5) / 0.1)
    x, y = _pre1_hover(s)
    if s > S_GLIDE0:
        c, L = _glide_path()
        w = _glide_w(s)
        px = float(np.interp(w, L, c[:, 0]))
        py = float(np.interp(w, L, c[:, 1]))
        b = ease('inout_sine', (s - S_GLIDE0) / 0.26)
        x, y = x + (px - x) * b, y + (py - y) * b
    return x, y, op


# ============================================================================================ pins: draw states
def _marker_fall(s, f_land, tip, appear=True):
    """Marker state during the L-3 .. L fall and after: (tip_x, tip_y, opacity, sx, sy) or None before."""
    d = since(s, f_land)
    if appear:
        if not on(s, f_land - 3):
            return None
        u = (s - F(f_land - 3)) / F(3)
        op = ease('inout_sine', (s - F(f_land - 3)) / F(1))
    else:                                              # pin 1: arrives at its L-3 point via pre1 (f5)
        if s < S_PIN1:
            return None
        u = (s - S_PIN1) / F(3)
        op = 1.0
    if d < 0:
        y = tip[1] - FALL * (1.0 - ease('in_cubic', u))
        st = 0.06 * ease('in_cubic', u)                # a little stretch into the contact (squash eases in)
        return tip[0], y, op, 1.0 - st, 1.0 + st
    k = math.exp(-10.0 * d) * math.sin(2 * math.pi * 3.2 * d) / 0.62
    st = 0.06 * max(0.0, 1.0 - d / F(2))             # the approach stretch hands over to the squash
    sq = 0.25 * k
    return tip[0], tip[1], 1.0, 1.0 + sq - st, 1.0 - 0.8 * sq + st


def pin_states(s):
    """List of drawable pin states, oldest first:
    dict(i, n, who, tip, marker=(x, y, op, sx, sy) | None, dot=opacity, card=(cx, cy, scale, op) | None, lines, thread)."""
    out = []
    for i, p in enumerate(PINS):
        n, v, fl, who, lines, tip, card = p
        if who == 'M' and n > 11:
            continue                                   # follow-up cards are handled with the thread
        if n == 1:
            m = _marker_fall(s, fl, tip, appear=False)
        else:
            m = _marker_fall(s, fl, tip)
        if m is None:
            continue
        nl = next_land(i)
        cu = ease('in_cubic', (s - F(nl - 2)) / F(6))  # collapse 0..1 over (next L) - 2 .. + 4
        dot = 0.0
        if cu > 0:
            sc = 1.0 + (0.318 - 1.0) * cu
            m = (m[0], m[1], m[2] * (1.0 - cu), m[3] * sc, m[4] * sc)
            dot = cu
        cs = None
        if who == 'C' and on(s, fl - 1):
            d = since(s, fl)
            op = ease('inout_sine', (s - F(fl - 1)) / F(3)) * (1.0 - cu)
            sc = 0.86 + 0.14 * spring(d + F(1), 'POP')
            if cu > 0:
                sc *= 1.0 - 0.5 * cu
            cx, cy = card
            if cu > 0:
                mx, my = tip[0], tip[1] - DISC_UP
                cx, cy = cx + (mx - cx) * cu * 0.6, cy + (my - cy) * cu * 0.6
            if op > 1e-3:
                cs = (cx, cy, sc, op)
        out.append(dict(i=i, n=n, who=who, tip=tip, marker=m if (m[2] > 1e-3) else None, dot=dot, card=cs,
                        lines=lines, collapse=cu))
    return out


def thread_states(s):
    """Owner ki Mummy's stacked thread (v12-v15): [(rect, lines, scale, opacity, name_line)] + the collapse 0..1."""
    if not on(s, 383):
        return [], 0.0
    cu = ease('in_cubic', (s - F(446)) / F(6))
    out = []
    for p in THREAD:
        n, v, fl, who, lines, tip, rect = p
        if not on(s, fl - 1):
            continue
        d = since(s, fl)
        op = ease('inout_sine', (s - F(fl - 1)) / F(3)) * (1.0 - cu)
        sc = (0.86 + 0.14 * spring(d + F(1), 'POP')) * (1.0 - 0.5 * cu)
        if op > 1e-3:
            out.append((rect, lines, sc, op, n == 11))
    return out, cu


def hover_state(s):
    """The last client marker (f701-f767): appears and drops 48 px onto the hover path start, hovers
    (540 + 180 sin(2 pi 0.45 u), 820 + 90 sin(2 pi 0.7 u)) with an amplitude ramp, freezes from f752 and
    swoops onto the glass (tip (515, 900)) over f764-f768 (in_cubic). Returns (tip_x, tip_y, op, sx, sy) or None."""
    if not on(s, F_HOVER - 3) or on(s, F_PAYOFF):
        return None
    u = min(s, F(F_FREEZE)) - F(F_HOVER)
    a = ease('inout_sine', u / 0.4) if u > 0 else 0.0
    x = 540.0 + a * 180.0 * math.sin(2 * math.pi * 0.45 * max(u, 0.0))
    y = 820.0 + a * 90.0 * math.sin(2 * math.pi * 0.70 * max(u, 0.0))
    op = ease('inout_sine', (s - F(F_HOVER - 3)) / F(2))
    if s < F(F_HOVER):
        y -= FALL * (1.0 - ease('in_cubic', (s - F(F_HOVER - 3)) / F(3)))
    tx, ty = x, y + DISC_UP
    w = ease('in_cubic', (s - F(F_PAYOFF - 4)) / F(4))
    if w > 0:
        tx, ty = tx + (PAYOFF[5][0] - tx) * w, ty + (PAYOFF[5][1] - ty) * w
    return tx, ty, op, 1.0, 1.0


def payoff_state(s):
    """The payoff pin (f768): (marker, card) like a client pin, bigger squash, no collapse."""
    if not on(s, F_PAYOFF):
        return None
    d = since(s, F_PAYOFF)
    k = math.exp(-9.0 * max(d, 0.0)) * math.sin(2 * math.pi * 3.0 * max(d, 0.0)) / 0.62
    sq = 0.32 * k
    m = (PAYOFF[5][0], PAYOFF[5][1], 1.0, 1.0 + sq, 1.0 - 0.8 * sq)
    op = ease('inout_sine', (s - F(F_PAYOFF - 1)) / F(3))
    sc = 0.86 + 0.14 * spring(d + F(1), 'POP')
    return dict(marker=m, card=(PAYOFF[6][0], PAYOFF[6][1], sc, op), lines=PAYOFF[4])


def dots(s):
    """Collapsed markers left on the frame: [(x, y, who, opacity)] (FLAME client / GOLD Mummy)."""
    out = []
    for i, p in enumerate(PINS):
        n, v, fl, who, lines, tip, card = p
        if who == 'M' and n > 11:
            continue
        nl = next_land(i)
        cu = ease('in_cubic', (s - F(nl - 2)) / F(6))
        if cu > 0:
            out.append((tip[0], tip[1], who, cu))
    return out


# ============================================================================================ the ad's changes
def _pop_in(s, f, k0=0.5, preset='POP'):
    """(scale, opacity) of an element popping in at frame f (solid from frame f)."""
    if not on(s, f):
        return 0.0, 0.0
    d = max(0.0, since(s, f) + HALF)
    return k0 + (1 - k0) * spring(d, preset), ease('inout_sine', d / F(2))


def _slam_in(s, f, s0=1.4):
    """(scale, opacity) of a SLAM (scale s0 -> 1 on the SLAM spring, solid on frame f)."""
    if not on(s, f):
        return 0.0, 0.0
    d = max(0.0, since(s, f) + HALF * 0.5)
    return 1.0 + (s0 - 1.0) * (1.0 - spring(d, 'SLAM')), 1.0


def state(s):
    """The ad + UI state at state time s (see the module docstring). Pure; cheap (no images)."""
    st = {'s': s}
    st['v'] = version(s)
    st['counter'] = counter_value(s)
    # status chip: Approved f0-f11, Changes requested from f12 (POP 1.08 -> 1)
    if on(s, 12):
        st['chip'] = ('Changes requested', 1.0 + 0.08 * (1.0 - spring(since(s, 12) + HALF, 'POP')))
    else:
        st['chip'] = ('Approved', 1.0)
    # ---- logo: x2 f32, x3 f64, x1.25 f432 (x3.75), v19 x1.2 (all elements), x1.2 f592 (x5.4); x -72/-72/+72
    k = 1.0
    for f, k1 in ((32, 2.0), (64, 3.0), (432, 3.75), (592, 4.5)):
        if s > F(f):
            k = k + (k1 - k) * spring(since(s, f), 'POP')
    st['e19'] = 1.0 + 0.2 * spring(since(s, 512), 'POP')
    st['logo_k'] = k
    st['logo_dx'] = sum(dx * ease('out_cubic', since(s, f) / F(6)) for f, dx in ((96, -72.0), (656, -72.0), (672, 72.0)))
    # ---- product push (plate + glass + steam + reflection about (515, 990)); held after the payoff
    st['z'] = 1.0 + 0.02 * max(0.0, min(s, 25.6) + 0.4) / 2.1333
    # ---- v5 pop: saturation x1.45 + exposure +0.2 (6 f); v21 +10 %
    st['sat'] = 1.0 + 0.45 * ramp_f(s, 128, 6) + 0.145 * ramp_f(s, 576, 6)
    st['expo'] = 0.2 * ramp_f(s, 128, 6)
    st['burst1'] = _pop_in(s, 130)
    st['burst2'] = _pop_in(s, 576)
    st['ribbon'] = _slam_in(s, 480)
    st['pill'] = _slam_in(s, 544)
    # ---- v6 cream fill from the pin point (12 f), v13 dark returns from Mummy's marker (12 f)
    st['cream_in'] = ramp_f(s, 192, 12)
    st['cream_out'] = ramp_f(s, 400, 12)
    st['outline'] = ramp_f(s, 224, 4)
    # ---- v9 sparkles (staggered POPs), v10 parody font, v11 shadows (0.85, 0.42 at v23, back at v24)
    st['sparkles'] = [_pop_in(s, 288 + 2 * j, k0=0.0) for j in range(4)]
    st['parody'] = ramp_f(s, 320, 3)
    st['parody_pop'] = 0.85 + 0.15 * spring(since(s, 320), 'POP') if s > F(320) else 0.85
    st['shadow'] = 0.85 * ramp_f(s, 352, 3) - 0.43 * ramp_f(s, 608, 6) + 0.43 * ramp_f(s, 624, 6)
    # ---- v12 glitter (sprinkles in over 6 f), v14 band 36 px + stars, v19 band x1.2
    st['glitter'] = (ramp_f(s, 384, 6), ramp_f(s, 416, 6), st['e19'])
    # ---- v16 letterbox + flares (8 f out_cubic); v18 steam x3
    st['letterbox'] = ramp_f(s, 448, 8, 'out_cubic')
    st['flares'] = ramp_f(s, 448, 8)
    st['dense'] = ramp_f(s, 496, 8)
    st['steam_top'] = 560.0 - 80.0 * st['dense']
    # ---- shake (player layer)
    st['shake'] = shake(s)
    # ---- clock chip (f576 POP, exit f696-f704), drawer (f656, row v27 f672, exit f696-f704)
    ex = ease('in_cubic', (s - F(696)) / F(8))
    if on(s, 576) and ex < 1:
        k_, o_ = _pop_in(s, 576, k0=0.86)
        st['clock'] = (k_, o_ * (1 - ex), 40.0 * ex)
    else:
        st['clock'] = None
    if on(s, 655) and ex < 1:
        d = since(s, 656)
        o_ = ease('inout_sine', (s - F(655)) / F(4)) * (1 - ex)
        sp = spring(d + F(1), 'POP')
        r4 = ease('out_cubic', (s - F(672)) / F(6)) if on(s, 672) else 0.0
        r4o = ease('inout_sine', (s - F(671)) / F(3)) if on(s, 671) else 0.0
        st['drawer'] = dict(op=o_, dy=40.0 * (1 - sp) + 40.0 * ex, k=0.94 + 0.06 * sp, r4=r4, r4o=r4o)
    else:
        st['drawer'] = None
    st['pins'] = pin_states(s)
    st['thread'] = thread_states(s)
    st['hover'] = hover_state(s)
    st['payoff'] = payoff_state(s)
    st['dots'] = dots(s)
    return st


def landings_tick():
    """Landings that get the quarter-strength chroma tick in post (all except the full D7s and the clean payoff)."""
    return [f for f in LANDINGS if f not in (384, 640, 768)]


if __name__ == '__main__':
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'pre1':
        for f in (979, 980, 981, 982, 984, 1000, 1013, 1019, 1021, 1022, 1023):
            print(f, [round(v, 1) for v in pre1(F(f) - DUR)])
        for f in range(0, 5):
            print(f, [round(v, 1) for v in pre1(F(f))])
        sys.exit(0)
    print(json.dumps({'versions': [(f, version(F(f))) for f in (0, 31, 32, 63, 64, 672, 783)],
                      'counter': [(f, round(counter_value(F(f)), 3)) for f in (27, 28, 29, 30, 31, 32, 668, 671, 672)],
                      'shake_beats': _SHAKE_BEATS}, indent=0))
