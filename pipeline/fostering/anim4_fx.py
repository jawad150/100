"""anim4_fx.py: look-dev helpers for anim4.py (ANIM 4 "£447.60: BUT WHAT IS IT FOR?"): CLEAN LIGHT SaaS world.

All pure functions of their arguments (+ lru caches). Canvases follow core's convention (premultiplied linear
float32 RGBA, 1080 x 1920). World: x right, y down, z away; the stations live on the z = 0 plane.

    world_bg(t, cam, dots=1, glows=1) -> new opaque canvas: clean white (linear ~1.16 so it encodes ~252 after the
        to_srgb8 shoulder, i.e. a true white, never grey), soft lavender / peach depth glows on a far plane
        (parallax), and a faint plum dot grid on a plane behind the stations (z = DOT_Z) that parallaxes with the
        camera journey (sub-pixel anti-aliased dots drawn per frame, ~10 ms).
    Path(points, step=10) -> arc-length parametrised Catmull-Rom curve in world space: .at(s) -> (3,), .tan(s),
        .length, .s_of(i) (arc length at control point i), .seg(s0, s1) -> (N, 3) points + s values.
    draw_ribbon(cv, cam, path, s0, s1, t, width=34, opacity=1) -> the glowing gold light-trail ribbon (twisting
        band: gold face, deeper orange back, white-hot core, warm halo, soft plum drop shadow on the page, bright
        comet head at s1).
    coin_sprite(asset, ang, rate, n_samples) -> spin-blurred coin frame (horizontal blur by the arc swept during
        the shutter share, sharp face-on).
    draw_coin(cv, cam, asset, P, size, ang, rate, t, n_samples, opacity=1, rot=0, shadow=1) -> coin billboard
        with a soft plum page shadow; returns the screen centre or None.
    draw_prop(cv, cam, spr, P, width, opacity=1, rot=0, shadow=1, anchor=(.5, .5), blur=0) -> 3D prop sprite at a
        world point with a soft drop shadow cast on the page behind it (alpha-derived, 1/4 res).
    soft_shadow(spr) -> low-res plum shadow sprite (cached on identity for static frames).
    glass_chip(label, icon_spr, px=40) -> crisp white glass pill (airy glass, icon + Poppins SemiBold INK label).
    draw_lightline(cv, cam, path, s_head, length, offset=0, width=5, opacity=1) -> thin racing light streak along the
        path (fading tail, white-hot head, warm half-res glow).
    local_glow(cv, x, y, r, kind='gold'|'peach'|'lav'|'mag'|'hot', amount) -> soft local accent glow (a tinted radial
        'over', plus a small additive core for 'gold'): never a full-frame flash.
    far_coins(cv, cam, t, asset, n_samples, opacity, z=1700) -> defocused coins drifting on a far plane (world lattice).
    near_bokeh(cv, cam, items, t) -> soft lens bokeh discs near the camera (items: world P, kind, size, blur, opacity).
    unproject(cam, sx, sy, depth) -> world point seen at screen (sx, sy) at camera depth.
    particles_light(n, seed) -> core.Particles tuned for a light scene (gold + lavender motes).
    REC: dev-only box recorder (None = off); anim4.checks() sets it to a list to collect drawn coin / prop boxes.
"""
import functools
import math

import cv2
import numpy as np

import core as K

C = K.C
REC = None                             # dev only (anim4.checks): list that collects drawn boxes; None = off
WHITE_LIN = 1.16                       # page white (linear); to_srgb8 shoulder -> ~252
DOT_Z = 900.0                          # dot-grid plane depth (behind the z = 0 stations)
DOT_SP = 44.0                          # dot spacing (world units on that plane)
GLOW_Z = 2600.0                        # far plane of the soft colour glows


def lin(hexs):
    return K.hexlin(hexs)


GOLD_HI = lin('#FFF3D6')
GOLD = lin('#FFC46A')
AMBER = C['AMBER']
ORANGE = C['ORANGE']
PLUM = C['PLUM']
INK = C['INK']
LAV = lin('#D9CCF4')
LAV2 = lin('#E9E1FA')
PEACH = lin('#FFD9C2')


# ================================================================================================ background
@functools.lru_cache(maxsize=1)
def _base():
    g = K.gradient(K.W, K.H, [(0.0, lin('#FFFFFF') * WHITE_LIN), (0.55, lin('#FFFEFD') * WHITE_LIN),
                              (1.0, lin('#FFFBF8') * (WHITE_LIN - 0.02))], angle=-90)
    cv = np.ones((K.H, K.W, 4), np.float32)
    cv[..., :3] = g
    cv.setflags(write=False)
    return cv


@functools.lru_cache(maxsize=4)
def _glow_spr(kind):
    if kind == 'lav':
        return K.radial(384, LAV, power=1.7)
    if kind == 'lav2':
        return K.radial(384, lin('#CBB8F0'), power=2.2)
    if kind == 'peach':
        return K.radial(384, PEACH, power=1.7)
    if kind == 'pink':
        return K.radial(384, lin('#FBD3E6'), power=2.0)
    return K.radial(384, lin('#FFE6C8'), power=1.8)


# world glow lattice: (x, y, size, kind, opacity, drift phase); repeats every 3200 in y
_GLOWS = [(-820.0, -900.0, 2600.0, 'lav', 0.62, 0.0), (900.0, -150.0, 2200.0, 'peach', 0.55, 1.1),
          (-600.0, 700.0, 2000.0, 'lav2', 0.30, 2.3), (1000.0, 1250.0, 2500.0, 'lav', 0.55, 0.7),
          (-900.0, 1800.0, 2300.0, 'peach', 0.50, 2.9), (300.0, 2400.0, 1900.0, 'pink', 0.28, 1.7),
          (1100.0, 2350.0, 1700.0, 'amber', 0.30, 0.4)]


@functools.lru_cache(maxsize=1)
def _base_small():
    q = cv2.resize(_base(), (K.W // 4, K.H // 4), interpolation=cv2.INTER_AREA)
    q.setflags(write=False)
    return q


def world_bg(t, cam, dots=1.0, glows=1.0, glow_gain=1.0):
    """White page + far colour glows (composited at 1/4 res: they are soft) + optional dot grid."""
    if glows > 0:
        sm = _base_small().copy()
        q = 0.25
        # colour glows live on a far plane: they parallax slowly with the journey (depth layer 1)
        for rep in range(-1, 5):
            for (x, y, sz, kind, op, ph) in _GLOWS:
                P = np.array([x + 120.0 * math.sin(0.21 * t + ph), y + 3200.0 * rep + 90.0 * math.sin(0.17 * t + 2 * ph),
                              GLOW_Z])
                xy, d = cam.project(P[None])
                if not np.isfinite(xy).all():
                    continue
                k = cam.focal / d[0]
                w = sz * k
                sx, sy = xy[0]
                if sx + w / 2 < -50 or sx - w / 2 > K.W + 50 or sy + w / 2 < -50 or sy - w / 2 > K.H + 50:
                    continue
                spr = _glow_spr(kind)
                K.draw(sm, spr, sx * q, sy * q, scale=w * q / spr.shape[1], opacity=op * glows * glow_gain)
        cv = cv2.resize(sm, (K.W, K.H), interpolation=cv2.INTER_LINEAR)
    else:
        cv = _base().copy()
    if dots > 0:
        dot_grid(cv, cam, t, dots)
    return cv


def _plane_affine(cam, z):
    """Screen affine of the fronto-parallel plane at world z: returns (o (2,), ex (2,), ey (2,)) = screen of the
    plane point under the camera axis and the screen vectors of +1 world unit in x / y (perspective ignored:
    the camera stays within a few degrees of front-on)."""
    f = cam.forward
    if abs(f[2]) < 1e-6:
        return None
    lam = (z - cam.pos[2]) / f[2]
    O = cam.pos + f * lam
    pts = np.array([O, O + (100.0, 0.0, 0.0), O + (0.0, 100.0, 0.0)])
    xy, d = cam.project(pts)
    if not np.isfinite(xy).all():
        return None
    return O, xy[0], (xy[1] - xy[0]) / 100.0, (xy[2] - xy[0]) / 100.0


def dot_grid(cv, cam, t, amount=1.0, z=DOT_Z, sp=DOT_SP, radius=1.9):
    """Faint plum dots on the plane z (anti-aliased, sub-pixel); fades with a soft world-space noise so the grid
    breathes in patches rather than tiling uniformly."""
    aff = _plane_affine(cam, z)
    if aff is None:
        return cv
    O, o, ex, ey = aff
    spx = math.hypot(*ex) * sp
    if spx < 6:
        return cv
    # plane coords of the screen corners -> lattice range
    M = np.array([[ex[0], ey[0]], [ex[1], ey[1]]])
    Mi = np.linalg.inv(M)
    corners = np.array([[0, 0], [K.W, 0], [0, K.H], [K.W, K.H]], np.float64) - o
    q = corners @ Mi.T + O[:2]
    i0, i1 = int(math.floor(q[:, 0].min() / sp)) - 1, int(math.ceil(q[:, 0].max() / sp)) + 1
    j0, j1 = int(math.floor(q[:, 1].min() / sp)) - 1, int(math.ceil(q[:, 1].max() / sp)) + 1
    gi, gj = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
    X = gi.ravel() * sp
    Y = gj.ravel() * sp
    sx = o[0] + (X - O[0]) * ex[0] + (Y - O[1]) * ey[0]
    sy = o[1] + (X - O[0]) * ex[1] + (Y - O[1]) * ey[1]
    ok = (sx > -4) & (sx < K.W + 4) & (sy > -4) & (sy < K.H + 4)
    sx, sy, X, Y = sx[ok], sy[ok], X[ok], Y[ok]
    # patchy visibility (world-space, slow drift)
    v = 0.55 + 0.45 * np.sin(X * 0.0021 + 0.7 * np.sin(Y * 0.0013) + 0.15 * t) * np.cos(Y * 0.0017 - X * 0.0007)
    v = np.clip(v, 0.25, 1.0)
    rr = radius * min(1.0, spx / 28.0) ** 0.5
    # sparse anti-aliased discs: each dot touches a 7 x 7 patch (vectorised; dots never overlap)
    ix = np.floor(sx).astype(np.int32)
    iy = np.floor(sy).astype(np.int32)
    o = np.arange(-3, 4, dtype=np.int32)
    PX = np.broadcast_to(ix[:, None, None] + o[None, None, :], (len(ix), 7, 7))
    PY = np.broadcast_to(iy[:, None, None] + o[None, :, None], (len(ix), 7, 7))
    d = np.sqrt((PX + 0.5 - sx[:, None, None]) ** 2 + (PY + 0.5 - sy[:, None, None]) ** 2)
    al = np.clip(rr - d + 0.5, 0.0, 1.0) * v[:, None, None]
    ok = (PX >= 0) & (PX < K.W) & (PY >= 0) & (PY < K.H) & (al > 0)
    a = np.zeros((K.H, K.W), np.float32)
    a[PY[ok], PX[ok]] = al[ok]
    a *= np.float32(0.30 * amount)
    col = K.mix(PLUM, LAV, 0.25).astype(np.float32)
    rgb = cv[..., :3]
    rgb *= (1.0 - a)[..., None]
    rgb += a[..., None] * col
    return cv


def page_shift(cam, P, z_page=DOT_Z):
    """Screen offset (dx, dy) of a soft 'drop shadow' cast by a floating object at world P onto the page plane
    behind it: a light up-left, so the shadow falls down-right, growing with the gap."""
    gap = max(0.0, z_page - P[2]) / max(cam.depth(P), 1.0) * cam.focal
    return 0.045 * gap, 0.075 * gap


# ================================================================================================ path
class Path:
    """Arc-length parametrised centripetal Catmull-Rom curve through world points (x, y[, z])."""

    def __init__(self, pts, step=8.0):
        P = np.array([(p[0], p[1], p[2] if len(p) > 2 else 0.0) for p in pts], np.float64)
        dense = []
        idx = [0]
        for i in range(len(P) - 1):
            p0 = P[i - 1] if i > 0 else 2 * P[0] - P[1]
            p1, p2 = P[i], P[i + 1]
            p3 = P[i + 2] if i + 2 < len(P) else 2 * P[-1] - P[-2]
            n = max(4, int(np.linalg.norm(p2 - p1) / step))
            u = np.linspace(0, 1, n, endpoint=False)[:, None]
            # centripetal CR via Barry-Goldman
            def tj(ti, a, b):
                return ti + max(np.linalg.norm(b - a), 1e-6) ** 0.5
            t0 = 0.0
            t1 = tj(t0, p0, p1)
            t2 = tj(t1, p1, p2)
            t3 = tj(t2, p2, p3)
            tt = t1 + u * (t2 - t1)
            A1 = (t1 - tt) / (t1 - t0) * p0 + (tt - t0) / (t1 - t0) * p1
            A2 = (t2 - tt) / (t2 - t1) * p1 + (tt - t1) / (t2 - t1) * p2
            A3 = (t3 - tt) / (t3 - t2) * p2 + (tt - t2) / (t3 - t2) * p3
            B1 = (t2 - tt) / (t2 - t0) * A1 + (tt - t0) / (t2 - t0) * A2
            B2 = (t3 - tt) / (t3 - t1) * A2 + (tt - t1) / (t3 - t1) * A3
            Cc = (t2 - tt) / (t2 - t1) * B1 + (tt - t1) / (t2 - t1) * B2
            dense.append(Cc)
            idx.append(sum(len(d) for d in dense))
        dense.append(P[-1:])
        D = np.concatenate(dense, 0)
        seg = np.linalg.norm(np.diff(D, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        self.D = D
        self.length = float(self.s[-1])
        self.ctrl_s = [float(self.s[min(i, len(D) - 1)]) for i in idx]
        # resample uniformly in arc length (fast lookups)
        self.du = 4.0
        su = np.arange(0.0, self.length + self.du, self.du)
        self.U = np.stack([np.interp(su, self.s, D[:, k]) for k in range(3)], 1)
        self.su = su

    def s_of(self, i):
        return self.ctrl_s[i]

    def at(self, s):
        s = np.clip(np.asarray(s, np.float64), 0.0, self.length)
        f = s / self.du
        i = np.minimum(np.floor(f).astype(int), len(self.U) - 2)
        w = (f - i)[..., None]
        return self.U[i] * (1 - w) + self.U[i + 1] * w

    def tan(self, s, h=12.0):
        a, b = self.at(s - h), self.at(s + h)
        v = b - a
        n = np.linalg.norm(v, axis=-1, keepdims=True)
        return v / np.maximum(n, 1e-9)

    def seg(self, s0, s1, step=10.0):
        s0, s1 = max(0.0, s0), min(self.length, s1)
        if s1 <= s0:
            return np.zeros((0, 3)), np.zeros(0)
        n = max(2, int((s1 - s0) / step) + 1)
        ss = np.linspace(s0, s1, n)
        return self.at(ss), ss

    def nearest_s(self, P):
        d = np.linalg.norm(self.U[:, :2] - np.asarray(P, np.float64)[:2], axis=1)
        return float(self.su[int(np.argmin(d))])


# ================================================================================================ ribbon
def _strip_polys(xy, half):
    """Quads (N-1, 4, 2) of a variable-width strip along screen polyline xy with half-widths `half`."""
    d = np.gradient(xy, axis=0)
    n = np.stack([-d[:, 1], d[:, 0]], 1)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-6)
    L = xy + n * half[:, None]
    R = xy - n * half[:, None]
    return np.stack([L[:-1], L[1:], R[1:], R[:-1]], 1)


def draw_ribbon(cv, cam, path, s0, s1, t, width=34.0, opacity=1.0, head=1.0, tail_fade=2600.0, step=9.0,
                shadow=1.0, twist_len=420.0):
    """Glowing gold light-trail ribbon along path between arc lengths s0..s1 (s1 = the head, where the money is).
    A twisting band (face gold -> back deep orange), white-hot core line, warm halo, soft plum shadow on the page
    and a comet head. Drawn into a local layer (bbox), composited 'over' the canvas."""
    if s1 - s0 < 4 or opacity <= 0.01:
        return cv
    pts, ss = path.seg(s0, s1, step)
    if len(pts) < 2:
        return cv
    xy, d = cam.project(pts)
    ok = np.isfinite(xy).all(1) & (d > 30)
    if ok.sum() < 2:
        return cv
    xy, d, ss = xy[ok], d[ok], ss[ok]
    k = cam.focal / d
    tw = np.cos((ss / twist_len - t * 0.9) * math.pi)          # twist phase: +-1 face / back, 0 = edge-on
    half = 0.5 * width * k * (0.30 + 0.70 * np.abs(tw))
    fade = np.clip((ss - (s1 - tail_fade)) / 900.0 + 1.0, 0.0, 1.0) if tail_fade else np.ones_like(ss)
    fade = np.minimum(fade, np.clip((ss - s0) / 120.0, 0, 1))
    m = int(min(260.0, 90.0 + (7.5 * width * k[-1] if head > 0 else 0.0)))
    x0, y0 = int(max(0, np.floor(xy[:, 0].min()) - m)), int(max(0, np.floor(xy[:, 1].min()) - m))
    x1, y1 = int(min(K.W, np.ceil(xy[:, 0].max()) + m)), int(min(K.H, np.ceil(xy[:, 1].max()) + m))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return cv
    hh, ww = y1 - y0, x1 - x0
    S = 16
    lxy = (xy - (x0, y0))
    quads = _strip_polys(lxy, half)
    body_a = np.zeros((hh, ww), np.uint8)
    col = np.zeros((hh, ww, 3), np.uint8)
    # per-segment colour: gold face <-> deep orange back, slight AMBER->ORANGE drift along the path
    face = np.array([255, 205, 120], np.float32)
    back = np.array([238, 112, 24], np.float32)
    for i in range(len(quads)):
        a = 0.5 + 0.5 * tw[i]
        c = back + (face - back) * a
        q = np.round(quads[i] * S).astype(np.int32)
        lv = int(255 * fade[i])
        if lv <= 2:
            continue
        cv2.fillConvexPoly(body_a, q, lv, cv2.LINE_AA, 4)
        cv2.fillConvexPoly(col, q, tuple(int(v) for v in c[::-1]), cv2.LINE_AA, 4)
    if body_a.max() == 0:
        return cv
    A = body_a.astype(np.float32) / 255.0
    rgbs = col[..., ::-1].astype(np.float32) / 255.0
    rgb = K.to_lin(rgbs) if hasattr(K, 'to_lin') else rgbs ** 2.2
    # core line (white-hot), only where the band faces us
    core = np.zeros((hh, ww), np.uint8)
    pl = np.round(lxy * S).astype(np.int32)
    for i in range(len(pl) - 1):
        lv = int(255 * fade[i] * (0.35 + 0.65 * abs(tw[i])))
        th = max(1, int(round(0.18 * width * k[i] * (0.4 + 0.6 * abs(tw[i])))))
        cv2.line(core, tuple(pl[i]), tuple(pl[i + 1]), lv, th, cv2.LINE_AA, 4)
    Cc = core.astype(np.float32) / 255.0
    # filament: a thin light line spiralling round the band (light-trail richness)
    fil = np.zeros((hh, ww), np.uint8)
    nrm = np.gradient(lxy, axis=0)
    nrm = np.stack([-nrm[:, 1], nrm[:, 0]], 1)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
    off = lxy + nrm * (0.95 * width * k * np.sin(ss / 170.0 - t * 2.6))[:, None]
    po = np.round(off * S).astype(np.int32)
    for i in range(len(po) - 1):
        lv = int(235 * fade[i])
        if lv > 2:
            cv2.line(fil, tuple(po[i]), tuple(po[i + 1]), lv, max(1, int(round(0.07 * width * k[i]))), cv2.LINE_AA, 4)
    Fi = fil.astype(np.float32) / 255.0
    op = np.float32(opacity)
    # ---- soft layers (page shadow, warm halo, comet glow) at half resolution, one composite
    h2, w2 = max(2, hh // 2), max(2, ww // 2)
    Ah = cv2.resize(A, (w2, h2), interpolation=cv2.INTER_AREA)
    Fh = cv2.resize(Fi, (w2, h2), interpolation=cv2.INTER_AREA)
    soft = np.zeros((h2, w2, 4), np.float32)
    if shadow > 0:
        dx, dy = page_shift(cam, pts[len(pts) // 2])
        sh = K.gblur(Ah, (9.0 + 0.02 * dy) / 2, border='constant')
        sh = cv2.warpAffine(sh, np.float32([[1, 0, dx / 2], [0, 1, dy / 2]]), (w2, h2),
                            borderMode=cv2.BORDER_CONSTANT)
        sa = sh * np.float32(0.20 * shadow)
        soft[..., :3] = sa[..., None] * K.mix(PLUM, LAV, 0.2)
        soft[..., 3] = sa
    halo = K.gblur(Ah, 5.0, border='constant') * 0.9 + K.gblur(Ah, 15.0, border='constant') * 1.7 + \
        K.gblur(Fh, 3.0, border='constant') * 0.8
    _over_a(soft, np.clip(halo, 0, 0.62), lin('#FFCB86') * 1.08)
    if head > 0:
        hx, hy = lxy[-1] / 2
        r = max(4.0, 1.2 * width * k[-1])
        yy, xx = np.ogrid[0:h2, 0:w2]
        d2 = ((xx - hx) ** 2 + (yy - hy) ** 2).astype(np.float32)
        g2 = np.exp(-d2 / np.float32(2 * (r * 2.2) ** 2)) * np.float32(head)
        _over_a(soft, np.clip(g2 * 0.35, 0, 1), K.mix(AMBER, PEACH, 0.5) * 1.15)
        g = np.exp(-d2 / np.float32(2 * r * r)) * np.float32(head)
        _over_a(soft, np.clip(g * 0.85, 0, 1), GOLD_HI * 1.4)
    soft = cv2.resize(soft, (ww, hh), interpolation=cv2.INTER_LINEAR)
    if opacity < 1:
        soft *= op
    dst = cv[y0:y1, x0:x1]
    dst *= 1 - soft[..., 3:4]
    dst += soft
    # ---- sharp layers (filament, body, core): composited only where they have coverage
    cg = K.gblur(Cc, 1.2, border='constant')
    fa = np.clip(Fi * 0.9, 0, 1)
    iy, ix = np.nonzero((A > 0.002) | (fa > 0.002) | (cg > 0.002))
    if len(iy):
        D = dst[iy, ix]
        for a_, c_ in ((fa[iy, ix], lin('#FFE2A6') * 1.3), (A[iy, ix], rgb[iy, ix] * 1.05),
                       (np.clip(cg[iy, ix] * 0.95, 0, 1), GOLD_HI * 1.7)):
            a_ = (a_ * op)[:, None]
            D *= 1 - a_
            D[:, :3] += a_ * np.asarray(c_, np.float32)
            D[:, 3:] += a_
        dst[iy, ix] = D
    return cv


def _over_a(layer, a, color):
    """Composite a flat colour with coverage a (h, w) over a premultiplied layer, in place."""
    a = a.astype(np.float32)
    layer *= (1 - a)[..., None]
    layer[..., :3] += a[..., None] * np.asarray(color, np.float32)
    layer[..., 3] += a


# ================================================================================================ coins / props
def coin_sprite(asset, ang, rate, n_samples=3):
    """Spin-blurred coin frame (see reel2._spin_spr): the coin spins about its vertical axis, so the screen motion
    is horizontal with speed ~ R |sin(angle)|; blur by the arc swept in this sub-sample's share of a 180 deg
    shutter (at least the asset's angular step while spinning): sharp face-on, smeared edge-on."""
    spr = asset.at_yaw(ang % 360.0)
    step = 360.0 / max(asset.n, 1) if getattr(asset, 'mode', 'spin') == 'spin' else 5.0
    span = abs(rate) * (0.5 / K.FPS) / max(1, n_samples)
    span = max(span, step * min(1.0, abs(rate) / 150.0))
    kx = 0.42 * spr.shape[1] * abs(math.sin(math.radians(ang))) * math.radians(span)
    if kx < 1.5:
        return spr
    ks = int(round(kx)) | 1
    return cv2.blur(spr, (ks, 1), borderType=cv2.BORDER_CONSTANT)


@functools.lru_cache(maxsize=4)
def _coin_shadow():
    return K.radial(128, K.mix(PLUM, LAV, 0.15), power=1.5)


def draw_coin(cv, cam, asset, P, size, ang, rate, n_samples=3, opacity=1.0, rot=0.0, shadow=1.0, blur=0.0):
    """Coin billboard (world size = diameter-ish width) with a soft page shadow. Returns (sx, sy, px_size)."""
    xy, d = cam.project(np.asarray(P, np.float64)[None])
    if not np.isfinite(xy).all() or d[0] < 60:
        return None
    k = cam.focal / d[0]
    w = size * k
    sx, sy = xy[0]
    if sx < -w or sx > K.W + w or sy < -w or sy > K.H + w:
        return None
    spr = coin_sprite(asset, ang, rate, n_samples)
    sig = blur + (0.5 * cam.coc(d[0]) if cam.aperture > 0 else 0.0)
    if REC is not None and shadow > 0:
        REC.append(('coin', (sx - 0.4 * w, sy - 0.4 * w, sx + 0.4 * w, sy + 0.4 * w), opacity))
    if shadow > 0:
        dx, dy = page_shift(cam, P)
        sh = _coin_shadow()
        K.draw(cv, sh, sx + dx, sy + dy, scale=(w * 0.95 / sh.shape[1], w * 0.80 / sh.shape[0]),
               opacity=0.30 * shadow * opacity, blur=sig + 0.06 * w)
    K.draw(cv, spr, sx, sy, scale=w / spr.shape[1], rot=rot, opacity=opacity, blur=sig)
    return sx, sy, w


_SHADOW_CACHE = {}


def soft_shadow(spr, key=None):
    """Low-res soft plum shadow of a sprite's alpha (1/4 res, blurred). Cached on an explicit `key` only."""
    kk = key      # (no id()-keyed caching: an evicted cache frame's id can be reused by a different array)
    if kk is not None and kk in _SHADOW_CACHE:
        return _SHADOW_CACHE[kk]
    h, w = spr.shape[:2]
    a = cv2.resize(spr[..., 3], (max(2, w // 4), max(2, h // 4)), interpolation=cv2.INTER_AREA)
    a = np.pad(a, 8)
    a = cv2.GaussianBlur(a, (0, 0), 3.0)
    col = K.mix(PLUM, LAV, 0.15).astype(np.float32)
    out = np.dstack([a[..., None] * col, a]).astype(np.float32)
    if kk is not None:
        if len(_SHADOW_CACHE) > 64:
            _SHADOW_CACHE.clear()
        _SHADOW_CACHE[kk] = out
    return out


def draw_prop(cv, cam, spr, P, width, opacity=1.0, rot=0.0, shadow=1.0, anchor=(0.5, 0.5), blur=0.0,
              shadow_key=None, scale_xy=(1.0, 1.0)):
    """3D prop sprite at world point P (anchor fraction lands there), `width` world units wide, with a soft drop
    shadow on the page behind. Returns (sx, sy, screen width) or None."""
    if spr is None or opacity <= 0.003:
        return None
    xy, d = cam.project(np.asarray(P, np.float64)[None])
    if not np.isfinite(xy).all() or d[0] < 60:
        return None
    k = cam.focal / d[0]
    w = width * k
    sx, sy = xy[0]
    h = w * spr.shape[0] / spr.shape[1]
    if sx + w < 0 or sx - w > K.W or sy + h < 0 or sy - h > K.H:
        return None
    sc = w / spr.shape[1]
    sig = blur + (0.5 * cam.coc(d[0]) if cam.aperture > 0 else 0.0)
    if REC is not None and opacity > 0.05:
        bb = K.alpha_bbox(spr, 0.05)
        if bb is not None:
            x0_ = sx + (bb[0] - anchor[0] * spr.shape[1]) * sc * scale_xy[0]
            y0_ = sy + (bb[1] - anchor[1] * spr.shape[0]) * sc * scale_xy[1]
            x1_ = sx + (bb[2] - anchor[0] * spr.shape[1]) * sc * scale_xy[0]
            y1_ = sy + (bb[3] - anchor[1] * spr.shape[0]) * sc * scale_xy[1]
            REC.append(('prop', (x0_, y0_, x1_, y1_), opacity))
    if shadow > 0:
        sh = soft_shadow(spr, shadow_key)
        dx, dy = page_shift(cam, P)
        # shadow sprite is 1/4 res + 8 px pad (low-res units): same anchor maps to the padded centre
        ax = (anchor[0] * spr.shape[1] / 4.0 + 8) / sh.shape[1]
        ay = (anchor[1] * spr.shape[0] / 4.0 + 8) / sh.shape[0]
        K.draw(cv, sh, sx + dx, sy + dy, scale=(sc * 4 * scale_xy[0], sc * 4 * scale_xy[1]), rot=rot,
               anchor=(ax, ay), opacity=0.34 * shadow * opacity, blur=sig + 0.012 * w)
    K.draw(cv, spr, sx, sy, scale=(sc * scale_xy[0], sc * scale_xy[1]), rot=rot, anchor=anchor, opacity=opacity,
           blur=sig)
    return sx, sy, w


# ================================================================================================ glows / particles
@functools.lru_cache(maxsize=8)
def _soft(kind):
    if kind == 'gold':
        return K.radial(256, K.mix(AMBER, GOLD_HI, 0.4), power=2.2)
    if kind == 'hot':
        return K.radial(256, GOLD_HI * 1.5, power=3.0)
    if kind == 'lav':
        return K.radial(256, LAV, power=1.8)
    if kind == 'peach':
        return K.radial(256, PEACH, power=1.8)
    if kind == 'mag':
        return K.radial(256, lin('#FF9CCB'), power=2.0)
    return K.radial(256, lin('#FFFFFF'), power=2.0)


def local_glow(cv, x, y, r, kind='gold', amount=1.0):
    """Soft local glow (a coloured radial 'over' + a little emissive core): on a white page this reads as a warm
    light bloom without lifting the whole frame (accents on pops / landings, never full-frame flashes)."""
    if amount <= 0.003:
        return cv
    s = _soft(kind)
    K.draw(cv, s, x, y, scale=2 * r / s.shape[1], opacity=min(1.0, 0.85 * amount))
    if kind == 'gold':
        h = _soft('hot')
        K.draw(cv, h, x, y, scale=0.9 * r / h.shape[1], opacity=min(1.0, 0.6 * amount), mode='add')
    return cv


def particles_light(n=110, seed=7):
    """Gold + lavender motes for the light world (in focus near the stations, bokeh when defocused)."""
    return K.Particles(n, seed=seed, bright=0.75, size=(1.4, 3.8), colors=[AMBER, GOLD, lin('#B79BEA'), PEACH],
                       vel=(0, -16, 0), box=((-1600, -2600, -900), (1600, 2600, 2400)))


# ================================================================================================ depth layers
def unproject(cam, sx, sy, depth):
    pc = np.array([(sx - K.CX) * depth / cam.focal, (sy - K.CY) * depth / cam.focal, depth])
    return cam.R @ pc + cam.pos


@functools.lru_cache(maxsize=8)
def _bokeh(kind):
    col = dict(lav=lin('#CDB9F2'), peach=lin('#FFC9A8'), gold=lin('#FFC873'), pink=lin('#FBB8D6'),
               white=lin('#FFFFFF') * 1.2)[kind]
    a = K.disc(120, col, soft=10.0)
    # soft-edged bokeh disc with a slightly brighter rim (lens look)
    r = K.ring(112, 6.0, col * 1.08)
    p = (a.shape[0] - r.shape[0]) // 2
    if p > 0:
        r = np.pad(r, ((p, a.shape[0] - r.shape[0] - p), (p, a.shape[1] - r.shape[1] - p), (0, 0)))
    out = a * 0.85 + r[:a.shape[0], :a.shape[1]] * 0.25
    return np.ascontiguousarray(out.astype(np.float32))


def far_coins(cv, cam, t, asset, n_samples=3, opacity=0.5, z=1700.0, sp=(760.0, 820.0), seed=3):
    """Defocused coins drifting on a far plane (depth layer behind the dot grid), world lattice -> parallax."""
    aff = _plane_affine(cam, z)
    if aff is None:
        return cv
    O = aff[0]
    i0, i1 = int(math.floor((O[0] - 1800) / sp[0])), int(math.ceil((O[0] + 1800) / sp[0]))
    j0, j1 = int(math.floor((O[1] - 3000) / sp[1])), int(math.ceil((O[1] + 3000) / sp[1]))
    for i in range(i0, i1 + 1):
        for j in range(j0, j1 + 1):
            h = (i * 73856093 ^ j * 19349663 ^ seed) & 0xFFFF
            if h % 4:
                continue
            jx = ((h >> 4) % 100) / 100.0 - 0.5
            jy = ((h >> 9) % 100) / 100.0 - 0.5
            P = np.array([i * sp[0] + jx * 500 + 40 * math.sin(t * 0.5 + h), j * sp[1] + jy * 500 - 22.0 * t, z])
            rate = 60.0 + (h % 90)
            draw_coin(cv, cam, asset, P, 200.0, t * rate + h, rate, n_samples, opacity=opacity, shadow=0.0,
                      blur=4.5, rot=(h % 40) - 20)
    return cv


def near_bokeh(cv, cam, items, t, opacity=1.0):
    """items: [(world P, kind, world size, extra blur px, opacity)] -> soft defocused discs near the lens."""
    for (Pw, kind, size, bl, op) in items:
        P = np.array([Pw[0] + 30 * math.sin(t * 0.37 + Pw[0] * 0.01), Pw[1] + 24 * math.sin(t * 0.29 + Pw[1] * 0.01),
                      Pw[2]])
        xy, d = cam.project(P[None])
        if not np.isfinite(xy).all() or d[0] < 80:
            continue
        k = cam.focal / d[0]
        w = size * k
        sx, sy = xy[0]
        if sx + w < 0 or sx - w > K.W or sy + w < 0 or sy - w > K.H:
            continue
        spr = _bokeh(kind)
        K.draw(cv, spr, sx, sy, scale=w / spr.shape[1], opacity=op * opacity, blur=bl + 0.04 * w)
    return cv


def draw_lightline(cv, cam, path, s_head, length, offset=0.0, width=5.0, opacity=1.0, step=12.0):
    """A thin racing light streak along the path (head at s_head, fading tail of `length`), offset sideways by
    `offset` world units: warm gold line with a white-hot head and a soft glow (half-res), 'over' the canvas."""
    if opacity <= 0.01:
        return cv
    pts, ss = path.seg(s_head - length, s_head, step)
    if len(pts) < 3:
        return cv
    tg = np.gradient(pts, axis=0)
    nrm = np.stack([-tg[:, 1], tg[:, 0], np.zeros(len(tg))], 1)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
    pts = pts + nrm * offset
    xy, d = cam.project(pts)
    ok = np.isfinite(xy).all(1) & (d > 30)
    if ok.sum() < 3:
        return cv
    xy, d, ss = xy[ok], d[ok], ss[ok]
    k = cam.focal / d
    m = 40
    x0, y0 = int(max(0, xy[:, 0].min() - m)), int(max(0, xy[:, 1].min() - m))
    x1, y1 = int(min(K.W, xy[:, 0].max() + m)), int(min(K.H, xy[:, 1].max() + m))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return cv
    hh, ww = y1 - y0, x1 - x0
    S = 16
    lay = np.zeros((hh, ww), np.uint8)
    p = np.round((xy - (x0, y0)) * S).astype(np.int32)
    u = (ss - ss[0]) / max(ss[-1] - ss[0], 1e-6)              # 0 tail .. 1 head
    for i in range(len(p) - 1):
        lv = int(255 * u[i] ** 1.6)
        th = max(1, int(round(width * k[i] * (0.35 + 0.65 * u[i]))))
        if lv > 2:
            cv2.line(lay, tuple(p[i]), tuple(p[i + 1]), lv, th, cv2.LINE_AA, 4)
    a = lay.astype(np.float32) / 255.0
    h2, w2 = max(2, hh // 2), max(2, ww // 2)
    ah = cv2.resize(a, (w2, h2), interpolation=cv2.INTER_AREA)
    gl = np.clip(K.gblur(ah, 4.0, border='constant') * 1.6, 0, 0.55)
    soft = np.zeros((h2, w2, 4), np.float32)
    _over_a(soft, gl, lin('#FFC27A') * 1.05)
    soft = cv2.resize(soft, (ww, hh), interpolation=cv2.INTER_LINEAR) * np.float32(opacity)
    dst = cv[y0:y1, x0:x1]
    dst *= 1 - soft[..., 3:4]
    dst += soft
    iy, ix = np.nonzero(a > 0.002)
    if len(iy):
        D = dst[iy, ix]
        aa = (a[iy, ix] * opacity)[:, None]
        D *= 1 - aa
        D[:, :3] += aa * (lin('#FFE6B0') * 1.5)
        D[:, 3:] += aa
        dst[iy, ix] = D
    return cv


def draw_coin_swept(cv, cam, asset, P0, P1, size, ang, rate, n_samples=3, opacity=1.0, rot=0.0, shadow=1.0,
                    blur=0.0, step_px=2.5, max_sub=10):
    """Coin moving from world P0 to P1 within this render sample's share of the shutter: drawn as m sub-steps
    accumulated additively in a local layer (a continuous smear, not the stepped ghost copies a fast object gets
    from a handful of whole-frame samples), then composited 'over'. Falls back to draw_coin when slow."""
    P0 = np.asarray(P0, np.float64)
    P1 = np.asarray(P1, np.float64)
    xy, d = cam.project(np.stack([P0, P1]))
    if not np.isfinite(xy).all() or (d < 60).any():
        return draw_coin(cv, cam, asset, (P0 + P1) / 2, size, ang, rate, n_samples, opacity, rot, shadow, blur)
    disp = float(np.hypot(*(xy[1] - xy[0])))
    m = int(min(max_sub, max(1, math.ceil(disp / step_px))))
    if m <= 1:
        return draw_coin(cv, cam, asset, (P0 + P1) / 2, size, ang, rate, n_samples, opacity, rot, shadow, blur)
    Pm = (P0 + P1) / 2
    k0, k1 = cam.focal / d[0], cam.focal / d[1]
    w = size * max(k0, k1)
    x0 = int(max(0, math.floor(xy[:, 0].min() - w)))
    y0 = int(max(0, math.floor(xy[:, 1].min() - w)))
    x1 = int(min(K.W, math.ceil(xy[:, 0].max() + w)))
    y1 = int(min(K.H, math.ceil(xy[:, 1].max() + w)))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    spr = coin_sprite(asset, ang, rate, n_samples)
    dm = cam.depth(Pm)
    sig = blur + (0.5 * cam.coc(dm) if cam.aperture > 0 else 0.0)
    if shadow > 0:
        xm, ym = (xy[0] + xy[1]) / 2
        wm = size * cam.focal / dm
        dx, dy = page_shift(cam, Pm)
        sh = _coin_shadow()
        K.draw(cv, sh, xm + dx, ym + dy, scale=(wm * 0.95 / sh.shape[1], wm * 0.80 / sh.shape[0]),
               opacity=0.30 * shadow * opacity, blur=sig + 0.06 * wm + 0.3 * disp)
        if REC is not None:
            REC.append(('coin', (min(xy[:, 0]) - 0.4 * wm, min(xy[:, 1]) - 0.4 * wm, max(xy[:, 0]) + 0.4 * wm,
                                 max(xy[:, 1]) + 0.4 * wm), opacity))
    layer = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
    for j in range(m):
        u = (j + 0.5) / m
        x = xy[0][0] + (xy[1][0] - xy[0][0]) * u
        y = xy[0][1] + (xy[1][1] - xy[0][1]) * u
        kk = k0 + (k1 - k0) * u
        K.draw(layer, spr, x - x0, y - y0, scale=size * kk / spr.shape[1], rot=rot, opacity=opacity / m, mode='add',
               blur=sig)
    dst = cv[y0:y1, x0:x1]
    dst *= 1 - np.clip(layer[..., 3:4], 0, 1)
    dst += layer
    return float(xy[:, 0].mean()), float(xy[:, 1].mean()), w


@functools.lru_cache(maxsize=12)
def glossy_orb(kind='peach', size=256):
    """Procedural glossy candy sphere (fallback for the 'orbs' day asset): lit from the top-left, soft specular
    highlight, coloured rim, gentle fresnel; 'glass' is a translucent lavender bubble."""
    cols = dict(sphere_peach='#FFB98F', sphere_magenta='#D62E8C', sphere_orange='#FF7A2E', sphere_leaf='#7FBF2E',
                torus_glass='#CDBDF0', capsule_magenta_orange='#F0507A')
    base = lin(cols.get(kind, '#FFB98F'))
    s = size
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    c = (s - 1) / 2.0
    r = s * 0.46
    nx, ny = (xx - c) / r, (yy - c) / r
    d2 = nx * nx + ny * ny
    inside = d2 < 1.0
    nz = np.sqrt(np.clip(1.0 - d2, 0, 1))
    L = np.array([-0.45, -0.6, 0.66], np.float32)
    L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    H = L + np.array([0, 0, 1.0], np.float32)
    H /= np.linalg.norm(H)
    spec = np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1) ** 60
    fres = (1 - nz) ** 2.5
    rgb = base[None, None] * (0.42 + 0.68 * diff)[..., None]
    rgb += fres[..., None] * (lin('#FFE6F2') * 0.55)
    rgb += spec[..., None] * 1.6
    a = np.clip((1.0 - np.sqrt(d2)) * r + 0.5, 0, 1)
    if kind == 'torus_glass':
        a = a * np.clip(0.35 + 0.65 * fres + 0.9 * spec, 0, 1)
    out = np.dstack([rgb * a[..., None], a]).astype(np.float32)
    out[~inside & (a <= 0)] = 0
    out.setflags(write=False)
    return out
