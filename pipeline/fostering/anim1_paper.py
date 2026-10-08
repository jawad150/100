"""anim1_paper.py: procedural crumpled-paper sheet for ANIM 1 "DAY IN THE LIFE", relit every frame.

The sheet is a multi-scale crumple HEIGHT FIELD (long soft folds + a network of sharp creases at three scales
+ paper tooth), turned once into a normal map and an albedo (warm cream with fibre mottling) and cached on disk
(workspace3/textures/anim1_paper_<seed>.npz, ~0.2 s to load; ~20 s to build the first time).

Per frame, `shade()` relights it with a moving key light (azimuth / elevation / colour follow the time of day),
a cool or warm sky fill, and a soft window-light pool, so a morning -> afternoon -> evening light sweep plays
across the creases. INK (type, doodles) is composited into the albedo BEFORE lighting and debossed into the
paper (its alpha becomes a shallow dent in the height field), so the type is lit by the same light, catches
the light on one edge and stays razor sharp.

API
    sheet(variant=0) -> Sheet: .albedo (H, W, 3) linear, .nx .ny .nz (H, W) float32 (read-only, cached).
        variant 0..3 = the base texture flipped / rotated (different-looking sheets for slides and flips).
    Light(az, el, key, sky, contrast, pool=(cx, cy, rx, ry, angle, gain), vign, warm_edge) - per-frame lighting.
    light_at(t) -> Light for the reel time t (morning -> golden afternoon -> evening).
    shade(sheet, light, ink=None, deboss=1.0, spec_band=None, region=None) -> (H, W, 4) opaque linear canvas.
        ink: premultiplied linear RGBA canvas (H, W, 4) of things printed ON the paper (type, scribbles).
        spec_band: (u, angle, width, gain) diagonal glossy-ink light sweep (ink only, additive).
    Self-test: python3 anim1_paper.py selftest -> workspace3/out/selftest/anim1_paper_*.png
"""
import functools
import math
import os
import sys
import time

import cv2
import numpy as np

import core as K

W, H = K.W, K.H
TEX_DIR = os.path.join(K.WS, 'textures')
VERSION = 6


# ============================================================================================ height field
def _crease_pass(hgt, rng, n, L, R, amp, pad=200):
    """Add n tapered creases (sharp V in the middle, smooth shoulders) of length L, half-width R."""
    h, w = hgt.shape
    for _ in range(n):
        cx = rng.uniform(-pad, w + pad)
        cy = rng.uniform(-pad, h + pad)
        th = rng.uniform(0, math.pi)
        ln = rng.uniform(*L)
        r = rng.uniform(*R)
        a = rng.normal(0, 1) * amp * r
        c, s = math.cos(th), math.sin(th)
        ex, ey = abs(c) * ln / 2 + r, abs(s) * ln / 2 + r
        x0, x1 = int(max(0, cx - ex)), int(min(w, cx + ex + 1))
        y0, y1 = int(max(0, cy - ey)), int(min(h, cy + ey + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        xs = np.arange(x0, x1, dtype=np.float32) - cx
        ys = np.arange(y0, y1, dtype=np.float32)[:, None] - cy
        u = xs[None, :] * c + ys * s
        v = -xs[None, :] * s + ys * c
        av = np.abs(v) / r
        prof = np.clip(1.0 - av, 0, 1) ** 2
        ta = np.clip((ln / 2 - np.abs(u)) / (0.35 * ln), 0, 1)
        ta = ta * ta * (3 - 2 * ta)
        # a little bend: creases are not perfectly straight
        hgt[y0:y1, x0:x1] += (a * prof * ta).astype(np.float32)


def _noise(h, w, sigma, rng):
    n = rng.normal(0, 1, (h, w)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), sigma)
    return n / (n.std() + 1e-8)


def _worley_edge(w, h, n, wx, wy, cap, rng):
    """Distance to the nearest Voronoi border (F2 - F1) / 2 at warped coords, capped: 0 on the borders,
    rising linearly into each cell -> a continuous surface whose slope flips at every border (a crease)."""
    from scipy.spatial import cKDTree
    pts = np.stack([rng.uniform(-80, w + 80, n), rng.uniform(-80, h + 80, n)], 1)
    d, _ = cKDTree(pts).query(np.stack([wx.ravel(), wy.ravel()], 1), k=2, workers=1)
    e = ((d[:, 1] - d[:, 0]) * 0.5).reshape(h, w).astype(np.float32)
    return np.minimum(e, cap)


def build_height(w, h, seed=7):
    """Crumpled sheet: two warped Voronoi crease networks (ridges + valleys), short sharp wrinkles, soft folds."""
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    hgt = 8.0 * _noise(h, w, 200, rng)
    hgt += 2.0 * _noise(h, w, 60, rng)
    wx = xs + 18.0 * _noise(h, w, 36, rng)
    wy = ys + 18.0 * _noise(h, w, 36, rng)
    hgt += 0.042 * _worley_edge(w, h, 560, wx, wy, 48.0, rng)
    wx = xs + 8.0 * _noise(h, w, 16, rng)
    wy = ys + 8.0 * _noise(h, w, 16, rng)
    hgt -= 0.028 * _worley_edge(w, h, 2400, wx, wy, 18.0, rng)
    _crease_pass(hgt, rng, 1100, (80, 320), (8, 28), 0.022)
    # paper tooth (fibres)
    hgt += 0.030 * _noise(h, w, 0.9, rng)
    hgt += 0.045 * _noise(h, w, 2.4, rng)
    return hgt


def build_albedo(w, h, seed=7):
    rng = np.random.default_rng(seed + 101)
    base = K.hexlin('#F4ECDF')
    m = 0.020 * _noise(h, w, 90, rng) + 0.012 * _noise(h, w, 18, rng) + 0.010 * _noise(h, w, 1.1, rng)
    # sparse fibre flecks
    f = _noise(h, w, 0.7, rng)
    m -= 0.025 * np.clip(f - 2.6, 0, None)
    alb = base[None, None, :] * (1.0 + m[..., None])
    warm = np.float32([1.0, 0.985, 0.955])
    alb = alb * (1.0 + 0.03 * _noise(h, w, 260, rng)[..., None] * (warm - 1.0) * 10)
    return np.clip(alb, 0, 1).astype(np.float32)


def _normals(hgt, k=1.0, extra=None):
    gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    if extra is not None:
        gx = gx + extra[0]
        gy = gy + extra[1]
    nx, ny = -k * gx, -k * gy
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + 1.0)
    return (nx * inv).astype(np.float32), (ny * inv).astype(np.float32), inv.astype(np.float32)


def _cache_path(seed):
    return os.path.join(TEX_DIR, 'anim1_paper_v%d_s%d.npz' % (VERSION, seed))


@functools.lru_cache(maxsize=2)
def _base(seed=7):
    p = _cache_path(seed)
    if os.path.exists(p):
        try:
            d = np.load(p)
            return (d['albedo'].astype(np.float32), d['nx'].astype(np.float32), d['ny'].astype(np.float32),
                    d['nz'].astype(np.float32))
        except Exception:
            pass
    t0 = time.time()
    hgt = build_height(W, H, seed)
    alb = build_albedo(W, H, seed)
    nx, ny, nz = _normals(hgt, 1.0)
    os.makedirs(TEX_DIR, exist_ok=True)
    tmp = p + '.tmp.npz'
    np.savez(tmp, albedo=alb.astype(np.float16), nx=nx.astype(np.float16), ny=ny.astype(np.float16),
             nz=nz.astype(np.float16))
    os.replace(tmp, p)
    print('anim1_paper: built crumple texture in %.1fs -> %s' % (time.time() - t0, p), file=sys.stderr)
    return alb, nx, ny, nz


class Sheet:
    def __init__(self, albedo, nx, ny, nz):
        self.albedo, self.nx, self.ny, self.nz = albedo, nx, ny, nz
        for a in (albedo, nx, ny, nz):
            a.setflags(write=False)


@functools.lru_cache(maxsize=4)
def sheet(variant=0, seed=7):
    alb, nx, ny, nz = _base(seed)
    if variant == 1:        # rotated 180
        alb, nx, ny, nz = alb[::-1, ::-1], -nx[::-1, ::-1], -ny[::-1, ::-1], nz[::-1, ::-1]
    elif variant == 2:      # flipped left-right
        alb, nx, ny, nz = alb[:, ::-1], -nx[:, ::-1], ny[:, ::-1], nz[:, ::-1]
    elif variant == 3:      # flipped top-bottom
        alb, nx, ny, nz = alb[::-1], nx[::-1], -ny[::-1], nz[::-1]
    return Sheet(*(np.ascontiguousarray(a) for a in (alb, nx, ny, nz)))


def zoomed(sh, M):
    """Sheet seen through a 2x3 affine M (sheet px -> screen px), e.g. a camera push: albedo + normals warped
    (camera moves do not change surface normals)."""
    def wp(a):
        return cv2.warpAffine(np.ascontiguousarray(a), M, (W, H), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)
    return Sheet(wp(sh.albedo), wp(sh.nx), wp(sh.ny), wp(sh.nz))


# ============================================================================================ lighting
class Light:
    """az: direction TOWARD the light in screen degrees (0 = from the right, 90 = from below, 180 = from the left,
    270 = from the top); el: elevation deg; key / sky: linear RGB; contrast: crease relief 0..1.5;
    pool: (cx, cy, rx, ry, angle_deg, gain) soft elliptical sun patch on the sheet (gain = extra key light);
    vign: edge darkening 0..1; warm_edge: rgb multiplier at the edges (evening glow);
    streak: (u, angle, width, gain, (r, g, b)) a soft band of sunlight sweeping across the sheet (u 0..1);
    glow: (cx, cy, radius, gain, (r, g, b)) local warm light falling on the paper (a lit window)."""

    def __init__(self, az=210, el=24, key=(1.0, 0.96, 0.9), sky=(0.55, 0.58, 0.64), contrast=1.0,
                 pool=None, vign=0.15, warm_edge=(1.0, 1.0, 1.0), streak=None, glow=None):
        self.az, self.el = float(az), float(el)
        self.key, self.sky = np.float32(key), np.float32(sky)
        self.contrast = float(contrast)
        self.pool = pool
        self.vign = float(vign)
        self.warm_edge = np.float32(warm_edge)
        self.streak = streak
        self.glow = glow

    def vec(self):
        a, e = math.radians(self.az), math.radians(self.el)
        return math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)

    def shadow_dir(self):
        """Unit screen direction a shadow falls in (away from the light) and a length factor (low sun = long)."""
        a = math.radians(self.az)
        return (-math.cos(a), -math.sin(a)), 1.0 / max(math.tan(math.radians(self.el)), 0.25)

    def mean_rgb(self):
        """Approximate light colour on flat paper at the frame centre (to tint pre-lit props)."""
        return self.key * 0.62 * (1 + (self.pool[5] if self.pool else 0) * 0.5) + self.sky * 0.42


def _lerp_light(a, b, u):
    u = float(np.clip(u, 0, 1))
    L = lambda x, y: x + (y - x) * u
    d = ((b.az - a.az + 180) % 360) - 180          # azimuth along the short arc
    if a.pool is not None and b.pool is not None:
        pool = tuple(L(p, q) for p, q in zip(a.pool, b.pool))
    else:
        pool = a.pool if u < 0.5 else b.pool
    return Light(a.az + d * u, L(a.el, b.el), L(a.key, b.key), L(a.sky, b.sky), L(a.contrast, b.contrast), pool,
                 L(a.vign, b.vign), L(a.warm_edge, b.warm_edge))


# time-of-day keys (reel seconds): morning raking light from the upper left, cool sky -> golden afternoon from the
# top right -> warm low evening light from the right with a darker, glowing edge.
_TOD = [
    (0.0, Light(az=200, el=19, key=(1.10, 1.05, 0.97), sky=(0.52, 0.56, 0.62), contrast=1.15,
                pool=(330, 620, 900, 520, -28, 0.22), vign=0.12, warm_edge=(1.0, 1.0, 1.0))),
    (5.4, Light(az=222, el=25, key=(1.12, 1.04, 0.92), sky=(0.52, 0.54, 0.58), contrast=1.05,
                pool=(470, 760, 980, 600, -24, 0.20), vign=0.12, warm_edge=(1.0, 0.99, 0.97))),
    (10.2, Light(az=285, el=33, key=(1.16, 1.02, 0.82), sky=(0.53, 0.51, 0.50), contrast=0.85,
                 pool=(650, 900, 1000, 650, -10, 0.18), vign=0.13, warm_edge=(1.0, 0.97, 0.92))),
    (15.6, Light(az=338, el=18, key=(1.18, 0.90, 0.64), sky=(0.47, 0.41, 0.43), contrast=0.85,
                 pool=(820, 980, 900, 760, 18, 0.20), vign=0.22, warm_edge=(1.0, 0.86, 0.70))),
    (21.0, Light(az=350, el=14, key=(1.18, 0.86, 0.58), sky=(0.45, 0.38, 0.41), contrast=0.85,
                 pool=(860, 1000, 880, 760, 22, 0.20), vign=0.24, warm_edge=(1.0, 0.84, 0.66))),
]


def light_at(t):
    for (t0, a), (t1, b) in zip(_TOD, _TOD[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return _lerp_light(a, b, K.EASE['inout_sine'](u))
    return _TOD[-1][1]


@functools.lru_cache(maxsize=1)
def _grid_small():
    sw, sh = W // 4, H // 4
    ys, xs = np.mgrid[0:sh, 0:sw].astype(np.float32)
    return (xs + 0.5) * 4, (ys + 0.5) * 4


def _band(u, angle, width):
    """Low-res diagonal band (0..1) travelling along `angle` (deg CCW from +x); u 0..1 enters -> leaves."""
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    ext = abs(W / 2 * dx) + abs(H / 2 * dy)
    pos = (u * 2 - 1) * (1 + width * 3)
    X, Y = _grid_small()
    p = ((X - W / 2) * dx + (Y - H / 2) * dy) / ext
    return np.exp(-((p - pos) / width) ** 2)


def _lowres_terms(light):
    """(A, B) at 1/4 res: light_rgb = s * A + B, s = crease relief (1 on flat paper)."""
    X, Y = _grid_small()
    pool = np.ones_like(X)
    if light.pool is not None:
        cx, cy, rx, ry, ang, gain = light.pool
        a = math.radians(ang)
        c, s = math.cos(a), math.sin(a)
        u = ((X - cx) * c + (Y - cy) * s) / rx
        v = (-(X - cx) * s + (Y - cy) * c) / ry
        pool = pool + gain * np.exp(-1.6 * (u * u + v * v))
    nxv = (X / W - 0.5) * 2.0
    nyv = (Y / H - 0.5) * 2.0
    r2 = np.clip((nxv * nxv) * 0.8 + (nyv * nyv) * 0.65, 0, 1.6)
    vig = 1.0 - light.vign * r2 ** 1.4
    q = 0.55 + 0.45 * pool
    key = light.key * 0.62
    sky = light.sky * 0.42
    A = key[None, None, :] * (pool * vig)[..., None] + sky[None, None, :] * (0.5 * q * vig)[..., None]
    B = sky[None, None, :] * (0.5 * q * vig)[..., None]
    if light.streak is not None:
        su, sang, sw_, sg, scol = light.streak
        if 0 < su < 1 and sg > 0:
            A = A + _band(su, sang, sw_)[..., None] * (np.float32(scol) * sg)[None, None, :]
    if light.glow is not None:
        gx, gy, gr, gg, gcol = light.glow
        if gg > 0:
            d2 = ((X - gx) ** 2 + (Y - gy) ** 2) / (gr * gr)
            f = (1.0 / (1.0 + 3.0 * d2)) * np.exp(-0.35 * d2)
            A = A + f[..., None] * (np.float32(gcol) * gg)[None, None, :]
    if np.any(light.warm_edge != 1.0):
        r = (np.clip(r2, 0, 1.3) ** 1.2)[..., None]
        e = 1.0 + (light.warm_edge[None, None, :] - 1.0) * r
        A, B = A * e, B * e
    return A.astype(np.float32), B.astype(np.float32)


def _up(a):
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)


_LIT = {}


def _lit(sh, light, key):
    """Paper lit without ink, cached per key (one entry per frame: motion-blur sub-samples share it)."""
    k = (id(sh), key)
    if key is not None and k in _LIT:
        return _LIT[k]
    lx, ly, lz = light.vec()
    flat = max(lz, 0.05)
    kk = light.contrast / flat
    s = sh.nx * (lx * kk) + sh.ny * (ly * kk) + sh.nz * (lz * kk) + (1.0 - light.contrast)
    np.clip(s, 0.05, 2.4, out=s)
    A, B = _lowres_terms(light)
    Au, Bu = _up(A), _up(B)
    lit = s[..., None] * Au
    lit += Bu
    lit *= sh.albedo
    ent = (s, Au, Bu, lit, kk, (lx, ly))
    if key is not None:
        while len(_LIT) >= 3:
            _LIT.pop(next(iter(_LIT)))
        _LIT[k] = ent
    return ent


def light_rgb_at(light, x, y):
    """Light colour falling on flat paper at screen point (x, y) (for tinting things drawn after lighting)."""
    A, B = _lowres_terms(light)
    i = int(np.clip(y / 4, 0, A.shape[0] - 1))
    j = int(np.clip(x / 4, 0, A.shape[1] - 1))
    return A[i, j] + B[i, j]


def shade(sh, light, ink=None, bbox=None, deboss=1.0, sweep=None, key=None):
    """Relight a sheet with optional ink printed on it -> opaque (H, W, 4) linear canvas.
    ink: (H, W, 4) premultiplied linear, only its bbox (x0, y0, x1, y1) region is processed (None = whole frame).
    sweep: (u, angle, width, gain, colour) glossy light band on the ink only. key: cache key for the inkless
    lit paper (e.g. the frame index): sub-samples of one frame then share the paper lighting."""
    s, Au, Bu, lit, kk, (lx, ly) = _lit(sh, light, key)
    out = np.empty((H, W, 4), np.float32)
    out[..., :3] = lit
    out[..., 3] = 1.0
    if ink is None:
        return out
    if bbox is None:
        bbox = (0, 0, W, H)
    x0, y0, x1, y1 = bbox
    x0, y0 = max(0, int(x0) - 6), max(0, int(y0) - 6)
    x1, y1 = min(W, int(math.ceil(x1)) + 6), min(H, int(math.ceil(y1)) + 6)
    if x1 <= x0 or y1 <= y0:
        return out
    r = (slice(y0, y1), slice(x0, x1))
    ia = ink[r + (3,)]
    if not np.any(ia > 1e-4):
        return out
    alb = sh.albedo[r] * (1.0 - ia[..., None]) + ink[r + (slice(0, 3),)]
    sr = s[r]
    if deboss > 0:
        hd = cv2.GaussianBlur(ia, (0, 0), 1.3)
        g = deboss * 0.42 * kk
        sr = sr + (cv2.Sobel(hd, cv2.CV_32F, 1, 0, ksize=3) * (lx * g) +
                   cv2.Sobel(hd, cv2.CV_32F, 0, 1, ksize=3) * (ly * g))
        np.clip(sr, 0.05, 2.4, out=sr)
    lr = sr[..., None] * Au[r]
    lr += Bu[r]
    o = out[r]
    np.multiply(alb, lr, out=o[..., :3])
    if sweep is not None:
        u, ang, wd, gain, col = sweep
        if 0 < u < 1 and gain > 0:
            band = _up(_band(u, ang, wd))[r]
            o[..., :3] += (band * ia)[..., None] * (np.float32(col) * gain)
    return out


# ============================================================================================ self-test
def selftest():
    import type3d as T
    os.makedirs(K.SELFTEST, exist_ok=True)
    t0 = time.time()
    sh = sheet(0)
    print('sheet load/build %.2fs' % (time.time() - t0))
    ink = np.zeros((H, W, 4), np.float32)
    ts = T.render('FOSTERING', 'flat', font='display', px=150, fill='#5B174F')
    bb = ts.draw(ink, 540, 900)
    for t in (0.5, 8.0, 13.0, 19.5):
        t1 = time.time()
        cv = shade(sh, light_at(t), ink, bb)
        dt = time.time() - t1
        cv = K.post(cv, 'airy', t)
        K.save_png(os.path.join(K.SELFTEST, 'anim1_paper_%04.1f.png' % t), K.to_srgb8(cv, t))
        print('t=%.1f shade %.0f ms' % (t, dt * 1000))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
