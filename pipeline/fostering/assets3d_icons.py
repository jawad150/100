"""assets3d_icons.py - glossy "SaaS 3D icon" library for the Organic Fostering reels (Blender/Cycles).

Renders premium candy-plastic / frosted-glass / polished-gold 3D icons as transparent RGBA PNG
sequences that the compositor loads through ``sprites3d.Asset3D``.

CLI
---
    python3 assets3d_icons.py <name> [<name> ...] [--preview] [--variant night|day] [--frames 0,24,48]
    python3 assets3d_icons.py all              # every asset, every variant (finals)
    python3 assets3d_icons.py sheet            # contact sheets of the finals -> out/selftest/
    python3 assets3d_icons.py selftest         # quick low-sample renders -> out/selftest/assets3d_icons_*.png

    --preview   16 spp, half resolution, 3 frames (first/mid/last); writes to
                workspace3/out/preview3d/<name>/<variant>/ (never touches the finals)
    env ICON_SAMPLES / ICON_THREADS override the sample count (default 80) / render threads (default 2).

Names (variants, mode)
----------------------
    heart (night, day; yaw)        puffy MAGENTA candy heart with a HOT_PINK subsurface glow
    house (night, day; yaw)        rounded toy house, ivory walls, MAGENTA roof, glowing ORANGE heart door
    coin_gbp (night; spin + yaw)   thick polished gold coin, embossed pound sign, reeded rim.
                                   'spin' is written to assets3d/coin_gbp/night_spin/ (72 frames, 1000 px),
                                   'yaw' to assets3d/coin_gbp/night/
    shield_check (night, day; yaw) MAGENTA shield, frosted-glass inner layer, white raised check
    grad_cap (night; yaw)          PLUM mortarboard with an ORANGE tassel
    chat_bubble (night; yaw)       frosted lavender glass speech bubble with three MAGENTA dots
    key_heart (night; yaw)         polished gold key with a heart bow
    check_tile (night, day; yaw)   LEAF-green rounded tile with a white raised check
    star_badge (night, day; yaw)   AMBER gold star on a MAGENTA rosette with ribbon tails
    orbs (night, day; static)      6 frames: MAGENTA, ORANGE, PEACH, LEAF spheres, glass torus, glossy capsule
    pin_phone (night; yaw)         ORANGE glossy phone handset with two call-signal arcs

Output (shared 3D asset spec)
-----------------------------
    workspace3/assets3d/<name>/<variant>/0000.png ...   RGBA 8-bit, straight alpha, sRGB ('Standard' view)
    workspace3/assets3d/<name>/<variant>/meta.json
        {name, variant, mode: 'yaw'|'spin'|'anim'|'static', frames, fps_hint, yaw_range: [-40, 40],
         size: [w, h], anchor: [x, y] (visual centre px), loop, notes,
         pivot: [x, y] (projected rotation axis px), bbox: [x0, y0, x1, y1] (union alpha bbox),
         ground_y (lowest opaque row, for contact shadows), axis ('z' for yaw/spin), labels (static)}
    yaw: frame i shows yaw = -40 + 80 * i / 48 degrees (49 frames). spin: frame i = 360 * i / 72 deg.

Python API (numpy-only parts import without Blender)
----------------------------------------------------
    import assets3d_icons as A
    A.ASSETS['heart']                       # -> AssetSpec(variants, modes, builder, size, notes)
    A.hexlin('#B7006E')                     # -> (0.474, 0.0, 0.156) linear RGB
    sd = A.sd_heart(width=2.0)              # 2D signed-distance callables (negative inside)
    F = A.inflate(sd, thick=0.4, edge=0.4)  # 3D implicit from a 2D shape
    V, Fq, N = A.mesh_sdf(F, bounds, res=200)  # surface-nets quads + analytic normals
    A.render_asset('heart', 'night', preview=True)   # needs bpy (Blender as a module)

Pixel/colour conventions: base colours are brand hex converted to linear; 'Standard' view transform
with a per-variant exposure so a key-lit brand face reads close to its hex. Lighting: big warm key
top-left-front, soft front-right fill, strong rims (night: HOT_PINK back-right + ORANGE back-left over
a dark plum world with two coloured soft-box reflections; day: warm PEACH/white rims, ivory world).
Camera 80 mm, 5 degrees above the subject, framed so the swept object fills ~80 % of the frame.
"""
import os
import sys
import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
WS = os.environ.get('FOSTER_WS', os.path.join(REPO, 'workspace3'))
OUT3D = os.path.join(WS, 'assets3d')
PREVIEW3D = os.path.join(WS, 'out', 'preview3d')
SELFTEST = os.path.join(WS, 'out', 'selftest')
FONTS = os.path.join(WS, 'fonts')

# ----------------------------------------------------------------------------- colour

BRAND = {
    'MAGENTA': '#B7006E', 'HOT_PINK': '#FF3D9A', 'ORANGE': '#FF6411', 'AMBER': '#FFB15C',
    'LEAF': '#64A60B', 'LEAF_HI': '#A8E04A', 'PLUM': '#5B174F', 'INK': '#321F35',
    'NIGHT_0': '#0B0310', 'NIGHT_1': '#1C0822', 'IVORY': '#FCF8F5', 'PEACH': '#FFD4BA',
    'LAVENDER': '#F6EAF3',
}


def _s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexlin(h):
    """'#RRGGBB' (or a BRAND token name) -> linear RGB tuple."""
    h = BRAND.get(h, h).lstrip('#')
    return tuple(_s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def hexlin4(h):
    return hexlin(h) + (1.0,)


def mixlin(a, b, t):
    a, b = hexlin(a) if isinstance(a, str) else a, hexlin(b) if isinstance(b, str) else b
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


# ----------------------------------------------------------------------------- 2D SDF toolkit
# Every 2D shape is a callable sd(x, y) -> signed distance (negative inside), vectorised over arrays.

def sd_circle(cx, cy, r):
    return lambda x, y: np.hypot(x - cx, y - cy) - r


def sd_ellipse_approx(cx, cy, rx, ry):
    # first-order ellipse distance (good enough close to the boundary)
    def f(x, y):
        px, py = (x - cx) / rx, (y - cy) / ry
        k0 = np.hypot(px, py)
        k1 = np.hypot(px / rx, py / ry)
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)
    return f


def sd_rbox(cx, cy, hw, hh, r):
    """Rounded box centred at (cx, cy), half sizes hw, hh, corner radius r."""
    def f(x, y):
        qx = np.abs(x - cx) - hw + r
        qy = np.abs(y - cy) - hh + r
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    return f


def sd_segment(ax, ay, bx, by, r):
    def f(x, y):
        pax, pay = x - ax, y - ay
        bax, bay = bx - ax, by - ay
        h = np.clip((pax * bax + pay * bay) / (bax * bax + bay * bay), 0, 1)
        return np.hypot(pax - bax * h, pay - bay * h) - r
    return f


def sd_polyline(pts, r):
    """Round-capped stroke of radius r along a polyline [(x, y), ...]."""
    segs = [sd_segment(*pts[i], *pts[i + 1], r) for i in range(len(pts) - 1)]
    return lambda x, y: np.minimum.reduce([s(x, y) for s in segs])


def sd_poly_exact(pts):
    """Exact signed distance to a closed polygon (pts: (N, 2)). O(N) per point - keep N small."""
    P = np.asarray(pts, float)

    def f(x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        d = np.full(x.shape, np.inf)
        s = np.ones(x.shape)
        n = len(P)
        for i in range(n):
            ax, ay = P[i - 1]
            bx, by = P[i]
            ex, ey = bx - ax, by - ay
            wx, wy = x - ax, y - ay
            h = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
            d = np.minimum(d, (wx - ex * h) ** 2 + (wy - ey * h) ** 2)
            c1 = y >= ay
            c2 = y < by
            c3 = ex * wy > ey * wx
            flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
            s = np.where(flip, -s, s)
        return s * np.sqrt(d)
    return f


def op_union(*fs):
    return lambda x, y: np.minimum.reduce([f(x, y) for f in fs])


def op_sub(a, b):
    return lambda x, y: np.maximum(a(x, y), -b(x, y))


def op_isect(a, b):
    return lambda x, y: np.maximum(a(x, y), b(x, y))


def op_smin(a, b, k):
    """Polynomial smooth union (fillet radius ~k)."""
    def f(x, y):
        da, db = a(x, y), b(x, y)
        h = np.clip(0.5 + 0.5 * (db - da) / k, 0, 1)
        return db * (1 - h) + da * h - k * h * (1 - h)
    return f


def op_offset(a, r):
    return lambda x, y: a(x, y) - r


def op_xform(a, tx=0.0, ty=0.0, rot=0.0, scale=1.0):
    """Shape moved by (tx, ty), rotated by rot (radians) and uniformly scaled."""
    c, s = math.cos(rot), math.sin(rot)

    def f(x, y):
        px, py = (x - tx) / scale, (y - ty) / scale
        return a(c * px + s * py, -s * px + c * py) * scale
    return f


class Raster2D:
    """Bake a 2D sd callable (or polygons) onto a grid and resample it bilinearly (fast, smooth).

    Raster2D.from_fn(sd, bounds=(x0, y0, x1, y1), res=1024)
    Raster2D.from_polys([poly, ...], bounds, res)       # even-odd fill + exact Euclidean distance
    r.rounded(convex=0.05, concave=0.05)                 # morphological rounding of corners
    r(x, y)                                              # sample
    """

    def __init__(self, grid, bounds):
        self.g = grid.astype(np.float32)
        self.b = bounds
        self.h, self.w = grid.shape
        self.sx = (self.w - 1) / (bounds[2] - bounds[0])
        self.sy = (self.h - 1) / (bounds[3] - bounds[1])

    @classmethod
    def from_fn(cls, fn, bounds, res=1024):
        x0, y0, x1, y1 = bounds
        w = res
        h = max(8, int(round(res * (y1 - y0) / (x1 - x0))))
        X, Y = np.meshgrid(np.linspace(x0, x1, w), np.linspace(y0, y1, h))
        return cls(fn(X, Y), bounds)

    @classmethod
    def from_mask(cls, mask, bounds):
        from scipy.ndimage import distance_transform_edt
        px = (bounds[2] - bounds[0]) / (mask.shape[1] - 1)
        inside = distance_transform_edt(mask)
        outside = distance_transform_edt(~mask)
        sd = (outside - inside) * px
        sd = np.where(mask, sd + 0.5 * px, sd - 0.5 * px)
        return cls(sd, bounds)

    @classmethod
    def from_polys(cls, polys, bounds, res=2048):
        import cv2
        x0, y0, x1, y1 = bounds
        w = res
        h = max(8, int(round(res * (y1 - y0) / (x1 - x0))))
        mask = np.zeros((h, w), np.uint8)
        k = 16
        pts = []
        for p in polys:
            p = np.asarray(p, float)
            q = np.stack([(p[:, 0] - x0) / (x1 - x0) * (w - 1), (p[:, 1] - y0) / (y1 - y0) * (h - 1)], 1)
            pts.append(np.round(q * k).astype(np.int32))
        # even-odd: xor each filled contour
        for q in pts:
            m = np.zeros_like(mask)
            cv2.fillPoly(m, [q], 1, lineType=cv2.LINE_8, shift=4)
            mask ^= m
        return cls.from_mask(mask.astype(bool), bounds)

    def mask(self):
        return self.g < 0

    def rounded(self, convex=0.0, concave=0.0):
        """Round convex corners (opening) and concave corners (closing) by re-distancing."""
        r = self
        if concave > 0:   # closing: dilate then erode
            r = Raster2D.from_mask(r.g < concave, r.b)
            r = Raster2D(r.g + concave, r.b)
        if convex > 0:    # opening: erode then dilate
            r = Raster2D.from_mask(r.g < -convex, r.b)
            r = Raster2D(r.g - convex, r.b)
        return r

    def blurred(self, sigma_px=1.0):
        from scipy.ndimage import gaussian_filter
        return Raster2D(gaussian_filter(self.g, sigma_px), self.b)

    def __call__(self, x, y):
        from scipy.ndimage import map_coordinates
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        u = (x - self.b[0]) * self.sx
        v = (y - self.b[1]) * self.sy
        out = map_coordinates(self.g, [v.ravel(), u.ravel()], order=1, mode='nearest').reshape(x.shape)
        # outside the raster keep growing the distance
        du = np.maximum(np.maximum(-u, u - (self.w - 1)), 0) / self.sx
        dv = np.maximum(np.maximum(-v, v - (self.h - 1)), 0) / self.sy
        return out + np.hypot(du, dv)


# ----------------------------------------------------------------------------- named 2D shapes

def heart_outline(n=720, width=2.0, chub=0.0):
    """Classic parametric heart, centred on its bbox, scaled to `width`."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    if chub:
        x = x * (1 + chub * (y > 0) * (y / 12.0))
    x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
    s = width / (x1 - x0)
    return np.stack([(x - (x0 + x1) / 2) * s, (y - (y0 + y1) / 2) * s], 1)


def sd_heart(width=2.0, convex=0.10, concave=0.08, res=1400):
    P = heart_outline(width=width)
    m = width * 0.62
    b = (-m * 1.05, -m * 1.05, m * 1.05, m * 1.05)
    return Raster2D.from_polys([P], b, res).rounded(convex * width / 2, concave * width / 2).blurred(1.0)


def glyph_polys(char, font='Nunito-Black.ttf', height=1.0, steps=10):
    """Flattened outline polygons of a glyph (cap-height normalised, centred on its bbox)."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.basePen import BasePen

    class Flat(BasePen):
        def __init__(self, gs):
            super().__init__(gs)
            self.polys, self.cur = [], []

        def _moveTo(self, p):
            self.cur = [p]

        def _lineTo(self, p):
            self.cur.append(p)

        def _curveToOne(self, p1, p2, p3):
            p0 = self.cur[-1]
            for i in range(1, steps + 1):
                t = i / steps
                mt = 1 - t
                self.cur.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                                 mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))

        def _qCurveToOne(self, p1, p2):
            p0 = self.cur[-1]
            for i in range(1, steps + 1):
                t = i / steps
                mt = 1 - t
                self.cur.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                                 mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))

        def _closePath(self):
            if len(self.cur) > 2:
                self.polys.append(np.array(self.cur, float))
            self.cur = []

        _endPath = _closePath

    f = TTFont(os.path.join(FONTS, font))
    gs = f.getGlyphSet()
    name = f.getBestCmap()[ord(char)]
    pen = Flat(gs)
    gs[name].draw(pen)
    allp = np.concatenate(pen.polys)
    x0, y0 = allp.min(0)
    x1, y1 = allp.max(0)
    s = height / (y1 - y0)
    c = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
    return [(p - c) * s for p in pen.polys]


# ----------------------------------------------------------------------------- 3D implicits
# A 3D implicit is a callable F(x, y, z) -> value, negative inside (close to a distance near the surface).

def inflate(sd2, thick=0.3, edge=None, dome=0.0, dome_r=0.5, zc=0.0, back=None, zscale=1.0):
    """Puffy extrusion of a 2D shape (in the x/y plane) along z.

    thick : half thickness at the rim (front at zc + thick, back at zc - back)
    edge  : rim rounding radius (defaults to thick -> a fully round rim)
    dome  : extra bulge added towards the inside (pillow look), reached over `dome_r` inward distance
    back  : back half-thickness (defaults to thick)
    """
    edge = thick if edge is None else edge
    back = thick if back is None else back

    def F(x, y, z):
        d = sd2(x, y)                          # negative inside
        inner = np.clip(-d / dome_r, 0, 1)
        bulge = dome * (1 - (1 - inner) ** 2)  # ease-out dome
        zz = z - zc
        h = np.where(zz >= 0, thick + bulge, back + bulge * (back / max(thick, 1e-6)))
        wx = d + edge
        wy = (np.abs(zz) * zscale) - (h - edge)
        return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx, 0), np.maximum(wy, 0)) - edge
    return F


def sd3_round_box(c, hs, r):
    cx, cy, cz = c
    hx, hy, hz = hs

    def F(x, y, z):
        qx = np.abs(x - cx) - hx + r
        qy = np.abs(y - cy) - hy + r
        qz = np.abs(z - cz) - hz + r
        return (np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
                + np.minimum(np.maximum(qx, np.maximum(qy, qz)), 0) - r)
    return F


def sd3_sphere(c, r):
    return lambda x, y, z: np.sqrt((x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2) - r


def sd3_capsule(a, b, r):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ba = b - a
    bb = float(ba @ ba)

    def F(x, y, z):
        px, py, pz = x - a[0], y - a[1], z - a[2]
        h = np.clip((px * ba[0] + py * ba[1] + pz * ba[2]) / bb, 0, 1)
        return np.sqrt((px - ba[0] * h) ** 2 + (py - ba[1] * h) ** 2 + (pz - ba[2] * h) ** 2) - r
    return F


def sd3_torus(c, R, r, axis='z'):
    def F(x, y, z):
        px, py, pz = x - c[0], y - c[1], z - c[2]
        if axis == 'z':
            q = np.hypot(px, py) - R
            return np.hypot(q, pz) - r
        if axis == 'y':
            q = np.hypot(px, pz) - R
            return np.hypot(q, py) - r
        q = np.hypot(py, pz) - R
        return np.hypot(q, px) - r
    return F


def extrude_axis(sd2, axis, half, edge, center=0.0):
    """Rounded extrusion of a 2D shape along an arbitrary axis.

    axis 'y': the 2D shape lives in (x, z) and is extruded along y (depth), etc.
    """
    def F(x, y, z):
        if axis == 'y':
            d, w = sd2(x, z), y - center
        elif axis == 'x':
            d, w = sd2(y, z), x - center
        else:
            d, w = sd2(x, y), z - center
        wx = d + edge
        wy = np.abs(w) - (half - edge)
        return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx, 0), np.maximum(wy, 0)) - edge
    return F


def u_min(*Fs):
    return lambda x, y, z: np.minimum.reduce([F(x, y, z) for F in Fs])


def u_smin(a, b, k):
    def F(x, y, z):
        da, db = a(x, y, z), b(x, y, z)
        h = np.clip(0.5 + 0.5 * (db - da) / k, 0, 1)
        return db * (1 - h) + da * h - k * h * (1 - h)
    return F


def u_sub(a, b):
    return lambda x, y, z: np.maximum(a(x, y, z), -b(x, y, z))


def u_ssub(a, b, k):
    """Smooth subtraction a - b with fillet k."""
    def F(x, y, z):
        da, db = a(x, y, z), -b(x, y, z)
        h = np.clip(0.5 - 0.5 * (db - da) / k, 0, 1)
        return db * (1 - h) + da * h + k * h * (1 - h)
    return F


def u_isect(a, b):
    return lambda x, y, z: np.maximum(a(x, y, z), b(x, y, z))


def u_xform(F, t=(0, 0, 0), rx=0.0, ry=0.0, rz=0.0, s=1.0):
    """Move/rotate (XYZ euler, radians, applied x then y then z) / scale an implicit."""
    def rot(a):
        c, sn = math.cos(a), math.sin(a)
        return c, sn
    cx, sx = rot(rx)
    cy, sy = rot(ry)
    cz, sz = rot(rz)
    # forward R = Rz Ry Rx ; inverse applied to points = Rx^T Ry^T Rz^T
    R = (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
         @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))
    Ri = R.T

    def G(x, y, z):
        px, py, pz = (x - t[0]) / s, (y - t[1]) / s, (z - t[2]) / s
        qx = Ri[0, 0] * px + Ri[0, 1] * py + Ri[0, 2] * pz
        qy = Ri[1, 0] * px + Ri[1, 1] * py + Ri[1, 2] * pz
        qz = Ri[2, 0] * px + Ri[2, 1] * py + Ri[2, 2] * pz
        return F(qx, qy, qz) * s
    return G


# ----------------------------------------------------------------------------- surface nets mesher

def mesh_sdf(F, bounds, res=200, project_iters=4, chunk=2_000_000):
    """Polygonise an implicit with naive surface nets + Newton projection onto F = 0.

    bounds: ((x0, y0, z0), (x1, y1, z1)); res = cells along the longest axis.
    Returns (verts (N, 3) float64, quads (M, 4) int, normals (N, 3)), normals from the analytic gradient,
    faces wound so that their normals point outwards.
    """
    lo = np.asarray(bounds[0], float)
    hi = np.asarray(bounds[1], float)
    step = (hi - lo).max() / res
    n = np.maximum(np.ceil((hi - lo) / step).astype(int) + 1, 3)
    xs = lo[0] + np.arange(n[0]) * step
    ys = lo[1] + np.arange(n[1]) * step
    zs = lo[2] + np.arange(n[2]) * step
    # evaluate in z-slabs to bound memory
    G = np.empty((n[0], n[1], n[2]), np.float32)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    per = max(1, chunk // (n[0] * n[1]))
    for k0 in range(0, n[2], per):
        kz = zs[k0:k0 + per]
        G[:, :, k0:k0 + per] = F(X[:, :, None], Y[:, :, None], kz[None, None, :])
    inside = G < 0
    cell_shape = (n[0] - 1, n[1] - 1, n[2] - 1)
    ncell = int(np.prod(cell_shape))
    acc = np.zeros((ncell, 3))
    cnt = np.zeros(ncell)

    def cid(i, j, k):
        return (i * cell_shape[1] + j) * cell_shape[2] + k

    edges = []
    for ax in range(3):
        sl0 = [slice(None)] * 3
        sl1 = [slice(None)] * 3
        sl0[ax] = slice(0, -1)
        sl1[ax] = slice(1, None)
        g0, g1 = G[tuple(sl0)], G[tuple(sl1)]
        m = inside[tuple(sl0)] != inside[tuple(sl1)]
        idx = np.nonzero(m)
        t = g0[idx] / (g0[idx] - g1[idx])
        P = np.stack([xs[idx[0]], ys[idx[1]], zs[idx[2]]], 1)
        P[:, ax] += t * step
        i, j, k = idx
        o = [a for a in range(3) if a != ax]
        # the 4 cells sharing this edge
        for da in (0, 1):
            for db in (0, 1):
                c = [i.copy(), j.copy(), k.copy()]
                c[o[0]] = c[o[0]] - da
                c[o[1]] = c[o[1]] - db
                ok = (c[o[0]] >= 0) & (c[o[0]] < cell_shape[o[0]]) & (c[o[1]] >= 0) & (c[o[1]] < cell_shape[o[1]]) \
                    & (c[ax] < cell_shape[ax])
                ids = cid(c[0][ok], c[1][ok], c[2][ok])
                for d in range(3):
                    acc[:, d] += np.bincount(ids, P[ok, d], ncell)
                cnt += np.bincount(ids, None, ncell)
        edges.append((ax, idx, inside[tuple(sl0)][idx]))
    active = cnt > 0
    vid = -np.ones(ncell, np.int64)
    vid[active] = np.arange(active.sum())
    V = acc[active] / cnt[active, None]
    quads = []
    for ax, idx, ins in edges:
        i, j, k = idx
        o = [a for a in range(3) if a != ax]
        c = [i, j, k]
        ok = (c[o[0]] >= 1) & (c[o[0]] < cell_shape[o[0]]) & (c[o[1]] >= 1) & (c[o[1]] < cell_shape[o[1]]) \
            & (c[ax] < cell_shape[ax])
        cc = [a[ok] for a in c]
        insk = ins[ok]
        corners = []
        for da, db in ((1, 1), (0, 1), (0, 0), (1, 0)):
            q = [a.copy() for a in cc]
            q[o[0]] = q[o[0]] - da
            q[o[1]] = q[o[1]] - db
            corners.append(vid[cid(*q)])
        Q = np.stack(corners, 1)
        Q[~insk] = Q[~insk][:, ::-1]
        quads.append(Q)
    Q = np.concatenate(quads)
    Q = Q[(Q >= 0).all(1)]

    def grad(P, h=step * 0.25):
        gx = F(P[:, 0] + h, P[:, 1], P[:, 2]) - F(P[:, 0] - h, P[:, 1], P[:, 2])
        gy = F(P[:, 0], P[:, 1] + h, P[:, 2]) - F(P[:, 0], P[:, 1] - h, P[:, 2])
        gz = F(P[:, 0], P[:, 1], P[:, 2] + h) - F(P[:, 0], P[:, 1], P[:, 2] - h)
        return np.stack([gx, gy, gz], 1) / (2 * h)

    for _ in range(project_iters):
        f = F(V[:, 0], V[:, 1], V[:, 2])
        g = grad(V)
        gg = np.maximum((g * g).sum(1), 1e-12)
        d = -(f / gg)[:, None] * g
        dl = np.linalg.norm(d, axis=1)
        lim = step * 0.75
        d *= np.minimum(1.0, lim / np.maximum(dl, 1e-12))[:, None]
        V = V + d
    N = grad(V)
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    # fix winding so face normals agree with the gradient
    a, b, c = V[Q[:, 0]], V[Q[:, 1]], V[Q[:, 2]]
    fn = np.cross(b - a, c - a) + np.cross(c - a, V[Q[:, 3]] - a)
    gn = N[Q].sum(1)
    flip = (fn * gn).sum(1) < 0
    Q[flip] = Q[flip][:, ::-1]
    return V, Q, N


def mesh_bounds_of(V):
    return V.min(0), V.max(0)
