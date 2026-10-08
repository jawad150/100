"""assets3d_icons.py - glossy "SaaS 3D icon" library for the Organic Fostering reels (Blender/Cycles).

Builds every icon procedurally from signed-distance fields (numpy) -> surface-nets quad meshes with
analytic normals -> Blender (bpy as a module, Cycles CPU, OIDN), and renders premium candy-plastic /
frosted-glass / polished-gold icons as transparent RGBA PNG sequences for sprites3d.Asset3D.

CLI
---
    python3 assets3d_icons.py <name> [<name> ...] [--variant night|day] [--mode yaw|spin|static]
                              [--frames 0,24,48] [--samples N] [--preview] [--yaw-frames N] [--spin-frames N]
    python3 assets3d_icons.py all        # every asset, every variant and mode (finals)
    python3 assets3d_icons.py sheet      # contact sheets of the finals -> out/selftest/assets3d_icons_contact_*.png
    python3 assets3d_icons.py selftest   # mesher checks + shape sheet + tiny renders + final sheets

    --preview   16 spp, half resolution, first/mid/last frame, written to workspace3/out/preview3d/
                (never touches the finals).
    env ICON_SAMPLES (default 8; x1.34 for the glass assets; OIDN-denoised, fixed seed so the residual
    noise does not boil between frames), ICON_THREADS (default 2), SKIP_EXISTING=1 resumes a sequence.
    --yaw-frames / --spin-frames (env ICON_YAW_FRAMES / ICON_SPIN_FRAMES) change the frame counts
    (defaults 49 / 72; the anims #1/#4 day set uses 33 / 48). meta.json records the count used.

Assets (variants; mode; render size)
------------------------------------
    heart         night, day; yaw; 720   puffy MAGENTA candy heart, HOT_PINK random-walk subsurface glow
    house         night, day; yaw; 720   toy house: ivory walls, MAGENTA roof + chimney, glowing ORANGE door
                                         with a heart cut-out, glowing windows, a LEAF bush
    coin_gbp      night, day; yaw (720) + spin (1000)  thick polished gold coin, embossed pound sign on both
                                         faces (satin field, polished relief), bead ring, reeded rim.
                                         yaw -> assets3d/coin_gbp/<variant>/, spin -> <variant>_spin/;
                                         day uses a slightly yellower gold so it does not read copper on ivory
    shield_check  night, day; yaw; 720   MAGENTA shield, frosted-glass inner panel, white raised check
    check_tile    night, day; yaw; 720   LEAF-green squircle tile with a white raised check ("done")
    orbs          night, day; static; 720  6 frames: 0 magenta, 1 orange, 2 peach, 3 leaf sphere,
                                         4 glass torus, 5 magenta/orange capsule (meta 'labels')
    star_badge    night, day; yaw; 560   AMBER gold star on a MAGENTA rosette with ribbon tails (generic award)
    grad_cap      night; yaw; 560        PLUM mortarboard with an ORANGE tassel
    chat_bubble   night; yaw; 560        frosted LAVENDER glass speech bubble, three MAGENTA dots
    key_heart     night; yaw; 560        polished gold key with a heart bow
    pin_phone     night; yaw; 560        ORANGE phone handset ("call us") with two MAGENTA signal arcs
    (560 px for the small tile icons keeps all 49 frames inside the render budget; they display <= 300 px)

Output (shared 3D asset spec)
-----------------------------
    workspace3/assets3d/<name>/<variant>/0000.png ...   RGBA 8-bit, straight alpha, sRGB ('Standard' view)
    workspace3/assets3d/<name>/<variant>/meta.json
        {name, variant, mode: 'yaw'|'spin'|'static', frames, fps_hint, yaw_range: [-40, 40] (yaw),
         size: [w, h], anchor: [x, y] (visual centre = centre of the union alpha bbox, px), loop, notes,
         pivot: [x, y] (projected rotation axis), bbox: [x0, y0, x1, y1] (union alpha bbox over all
         frames), ground_y (lowest opaque row, for contact shadows), axis: 'z', labels (static only)}
    yaw : frame i shows yaw = -40 + 80 * i / 48 deg (49 frames); positive yaw turns the front towards
          screen-right. The object fills ~80 % of the frame over the whole sweep.
    spin: frame i = 5 * i deg about the vertical axis (72 frames, loops); the coin is 180-degree
          symmetric, so frames 36..71 are exact copies of 0..35.

Look
----
    Brand hex -> linear base colours, 'Standard' view transform, exposure 0: a key-lit MAGENTA face
    renders ~(190, 3, 100) vs #B7006E. Key: big warm disc area top-left-front; fill: soft front-right;
    lights stay out of glossy rays, reflections come from soft-edged emissive cards (oval key highlight,
    crisp top strip, faint front sheen; metals get a warm wall behind the camera + glint strips).
    night: HOT_PINK rim back-right + ORANGE kicker back-left, dark plum world with HOT_PINK / ORANGE
    soft-box blobs (warmer for gold so the metal stays amber). day: PEACH / white rims, ivory world
    with a darker warm 'flag' behind the camera so front faces stay saturated. No ground plane.
    Camera 80 mm, 5 deg above the subject, lens-shifted so the swept bbox is centred.

Python API (the numpy toolkit imports without Blender; bpy is imported lazily)
------------------------------------------------------------------------------
    import assets3d_icons as A
    A.ASSETS['heart']                         # AssetSpec(builder, variants, modes, size, notes)
    A.hexlin('MAGENTA')                       # (0.474, 0.0, 0.156) linear RGB (token or '#hex')
    sd = A.sd_heart(2.0)                      # 2D signed distance (Raster2D; negative inside)
    sd = A.poly_sd([A.shield_outline()]).rounded(0.2, 0.0)   # polygons -> SDF, morphological rounding
    F = A.inflate(sd, thick=0.2, edge=0.18, dome=0.07, dome_field=sd.poisson())  # crease-free pillow
    V, Q, N = A.mesh_sdf(F, ((-1, -1, -.5), (1, 1, .5)), res=200)  # surface nets + Newton projection
    A.render_asset('heart', 'night', preview=True)                 # build + render (needs bpy)
    A.finals_sheet()                          # contact sheets of the rendered finals
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

    def poisson(self, res=360, power=None):
        """Smooth 'balloon' field: solution of lap(u) = -1 inside the shape, u = 0 outside,
        normalised to max 1 (returned as a Raster2D sampled with cubic splines). Unlike the distance
        field it has no medial-axis creases, so (u ** 0.5) inflates any outline into a smooth pillow."""
        import cv2
        from scipy.sparse import coo_matrix
        from scipy.sparse.linalg import spsolve
        w = res
        h = max(8, int(round(res * self.h / self.w)))
        m = cv2.resize((self.g < 0).astype(np.uint8), (w, h), interpolation=cv2.INTER_AREA) > 0
        m[0, :] = m[-1, :] = False
        m[:, 0] = m[:, -1] = False
        idx = -np.ones(m.shape, np.int64)
        n = int(m.sum())
        idx[m] = np.arange(n)
        ys, xs = np.nonzero(m)
        rows, cols, vals = [np.arange(n)], [np.arange(n)], [np.full(n, 4.0)]
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nb = idx[ys + dy, xs + dx]
            ok = nb >= 0
            rows.append(np.arange(n)[ok])
            cols.append(nb[ok])
            vals.append(np.full(ok.sum(), -1.0))
        A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()
        u = spsolve(A, np.ones(n))
        U = np.zeros(m.shape)
        U[m] = u / u.max()
        r = Raster2D(U, self.b)
        r.order = 3
        return r

    def __call__(self, x, y):
        from scipy.ndimage import map_coordinates, spline_filter
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        u = (x - self.b[0]) * self.sx
        v = (y - self.b[1]) * self.sy
        order = getattr(self, 'order', 1)
        if order == 3:
            if getattr(self, '_coef', None) is None:
                self._coef = spline_filter(self.g.astype(np.float64), order=3, mode='nearest')
            out = map_coordinates(self._coef, [v.ravel(), u.ravel()], order=3, mode='nearest',
                                  prefilter=False).reshape(x.shape)
        else:
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


def heart_cones(width=2.0, lobe=0.52, sep=0.48, cy=0.22, tip=-0.92, n=256):
    """Chubby heart = union of two convex hulls (lobe circle + tip point). Returns 2 polygons (union)."""
    import cv2
    k = width / 2.0 / (sep + lobe)
    polys = []
    for sx in (-1, 1):
        a = np.linspace(0, 2 * np.pi, n, endpoint=False)
        pts = np.stack([sx * sep + lobe * np.cos(a), cy + lobe * np.sin(a)], 1)
        pts = np.concatenate([pts, [[0.0, tip]]])
        hull = cv2.convexHull((pts * 10000).astype(np.int64).astype(np.float32))[:, 0, :] / 10000.0
        polys.append(hull * k)
    return polys


def sd_heart(width=2.0, convex=0.10, concave=0.08, res=1400, **kw):
    """Rounded chubby heart sd (Raster2D, negative inside), centred on the origin."""
    import cv2
    polys = heart_cones(width, **kw)
    allp = np.concatenate(polys)
    c = (allp.min(0) + allp.max(0)) / 2
    polys = [p - c for p in polys]
    m = width * 0.62
    b = (-m * 1.05, -m * 1.05, m * 1.05, m * 1.05)
    w = res
    mask = np.zeros((w, w), np.uint8)
    for p in polys:
        q = np.stack([(p[:, 0] - b[0]) / (b[2] - b[0]) * (w - 1), (p[:, 1] - b[1]) / (b[3] - b[1]) * (w - 1)], 1)
        cv2.fillPoly(mask, [np.round(q * 16).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=4)
    r = Raster2D.from_mask(mask.astype(bool), b)
    return r.rounded(convex * width / 2, concave * width / 2).blurred(1.0)


def glyph_polys(char, font='Nunito-Black.ttf', height=1.0, steps=10):
    """Flattened outline polygons of a glyph (cap-height normalised, centred on its bbox).
    Note: poly_sd() fills even-odd, so glyphs with overlapping/self-intersecting outlines get holes at
    the joins; use glyph_sd() (FreeType, non-zero) for solid glyph shapes."""
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

def balloon(sd2, field, height=0.4, power=0.5, zc=0.0, back=None, flat=0.0):
    """Smooth inflated 'balloon' of a 2D shape: half-thickness = height * u**power, where u is the
    normalised Poisson field of the outline (Raster2D.poisson()). power 0.5 -> round like a sphere;
    lower powers give a flatter pillow. `back` scales the back half (default symmetric)."""
    back = 1.0 if back is None else back

    def F(x, y, z):
        u = np.clip(field(x, y), 0, 1)
        H = height * (u ** power) * (1 - flat) + height * flat * np.clip(u * 6, 0, 1) ** 0.5
        zz = z - zc
        Hz = np.where(zz >= 0, H, H * back)
        d = sd2(x, y)
        return np.abs(zz) - Hz + np.maximum(d, 0)
    return F


def inflate(sd2, thick=0.3, edge=None, dome=0.0, dome_r=0.5, zc=0.0, back=None, zscale=1.0, dome_field=None,
            dome_pow=0.6):
    """Puffy extrusion of a 2D shape (in the x/y plane) along z.

    thick : half thickness at the rim (front at zc + thick, back at zc - back)
    edge  : rim rounding radius (defaults to thick -> a fully round rim)
    dome  : extra bulge added towards the inside (pillow look), reached over `dome_r` inward distance,
            or shaped by `dome_field` (a Poisson field, crease-free) ** dome_pow
    back  : back half-thickness (defaults to thick)
    """
    edge = thick if edge is None else edge
    back = thick if back is None else back

    def F(x, y, z):
        d = sd2(x, y)                          # negative inside
        if dome_field is not None:             # crease-free dome from a Poisson field
            bulge = dome * np.clip(dome_field(x, y), 0, 1) ** dome_pow
        else:
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


def u_sisect(a, b, k):
    """Smooth intersection (rounded crease of radius ~k)."""
    def F(x, y, z):
        da, db = a(x, y, z), b(x, y, z)
        h = np.clip(0.5 - 0.5 * (db - da) / k, 0, 1)
        return db * (1 - h) + da * h + k * h * (1 - h)
    return F


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


# ============================================================================= Blender side
# bpy is imported lazily so the numpy toolkit above stays importable without Blender.

bpy = None
Vector = None
Matrix = None

SAMPLES = int(os.environ.get('ICON_SAMPLES', '8'))
THREADS = int(os.environ.get('ICON_THREADS', '2'))
LENS = 80.0
ELEV_DEG = 5.0
FILL = 0.80
YAW_RANGE = (-40.0, 40.0)
YAW_FRAMES = int(os.environ.get('ICON_YAW_FRAMES', '49'))      # CLI --yaw-frames N overrides
SPIN_FRAMES = int(os.environ.get('ICON_SPIN_FRAMES', '72'))    # CLI --spin-frames N overrides

# exposure (stops) per variant, tuned so a key-lit brand face reads close to its hex
EXPOSURE = {'night': 0.0, 'day': 0.0}


def _bpy():
    global bpy, Vector, Matrix
    if bpy is None:
        import bpy as _b
        from mathutils import Vector as _V, Matrix as _M
        bpy, Vector, Matrix = _b, _V, _M
    return bpy


def reset(res=(720, 720), samples=None, variant='night'):
    _bpy()
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    import assets3d_gpu
    assets3d_gpu.set_device(bpy, sc)          # CPU unless FOSTER_GPU=1 finds a GPU
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    sc.cycles.samples = samples or SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.adaptive_min_samples = 0
    sc.cycles.seed = 7                      # fixed noise pattern -> no denoiser boiling between frames
    sc.cycles.use_animated_seed = False
    sc.cycles.use_light_tree = False        # few lights: plain sampling is ~20 % faster here
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    sc.cycles.denoising_prefilter = 'FAST'
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 1
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 6
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.volume_bounces = 0
    sc.cycles.sample_clamp_indirect = 6.0
    sc.cycles.blur_glossy = 0.6
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.filter_size = 1.2
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '8'
    sc.render.image_settings.compression = 40
    sc.display_settings.display_device = 'sRGB'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = EXPOSURE.get(variant, 0.0)
    sc.view_settings.gamma = 1.0
    return sc


# ----------------------------------------------------------------------------- materials

def _principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes['Principled BSDF'], m.node_tree


def m_candy(name, color, rough=0.28, coat_r=0.04, sss=0.0, sss_radius=(1.0, 0.35, 0.5), sss_scale=0.06,
            spec=0.5, sheen=0.0, emit=None, emit_str=0.0, rim_glow=None, rim_str=0.0, random_walk=False,
            grad=None):
    """Candy plastic: brand base colour, clear coat, optional subsurface (Burley; random_walk=True for
    the hero look), optional fresnel rim glow (cheap 'light inside the candy' look) and an optional
    vertical gradient grad=(top_colour, z_bottom, z_top) in object space."""
    m, b, nt = _principled(name)
    col = hexlin(color) if isinstance(color, str) else tuple(color)
    b.inputs['Base Color'].default_value = col + (1,)
    b.subsurface_method = 'RANDOM_WALK' if random_walk else 'BURLEY'
    if grad:
        top, z0, z1 = grad
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.interpolation_type = 'SMOOTHSTEP'
        mr.inputs['From Min'].default_value = z0
        mr.inputs['From Max'].default_value = z1
        nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.inputs['A'].default_value = col + (1,)
        mix.inputs['B'].default_value = (hexlin(top) if isinstance(top, str) else tuple(top)) + (1,)
        nt.links.new(mr.outputs[0], mix.inputs['Factor'])
        nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Coat Roughness'].default_value = coat_r
    b.inputs['Coat IOR'].default_value = 1.5
    b.inputs['Specular IOR Level'].default_value = spec
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = sss_radius
        b.inputs['Subsurface Scale'].default_value = sss_scale
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
        b.inputs['Sheen Tint'].default_value = (1, 1, 1, 1)
    if emit:
        b.inputs['Emission Color'].default_value = (hexlin(emit) if isinstance(emit, str) else emit) + (1,)
        b.inputs['Emission Strength'].default_value = emit_str
    if rim_glow:
        # emission driven by facing ratio: glows at grazing angles like light scattering inside candy
        lw = nt.nodes.new('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.35
        ramp = nt.nodes.new('ShaderNodeMapRange')
        ramp.inputs['From Min'].default_value = 0.25
        ramp.inputs['From Max'].default_value = 1.0
        ramp.inputs['To Min'].default_value = 0.0
        ramp.inputs['To Max'].default_value = rim_str
        nt.links.new(lw.outputs['Facing'], ramp.inputs['Value'])
        b.inputs['Emission Color'].default_value = (hexlin(rim_glow) if isinstance(rim_glow, str) else rim_glow) + (1,)
        nt.links.new(ramp.outputs['Result'], b.inputs['Emission Strength'])
    return m


def m_gold(name, base='AMBER', edge='ORANGE', rough=0.18, coat=0.0, aniso=0.0, relief=None):
    """Polished gold: metallic, AMBER face colour with an ORANGE edge tint.

    relief=(axis, h0, h1, rough_field): roughness ramps from rough_field (|coord| <= h0, the coin field)
    to `rough` (|coord| >= h1, the raised relief) along an object-space axis ('X'|'Y'|'Z')."""
    m, b, nt = _principled(name)
    if relief:
        ax, h0, h1, rf = relief
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        ab = nt.nodes.new('ShaderNodeMath')
        ab.operation = 'ABSOLUTE'
        nt.links.new(sep.outputs[ax], ab.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = h0
        mr.inputs['From Max'].default_value = h1
        mr.inputs['To Min'].default_value = rf
        mr.inputs['To Max'].default_value = rough
        nt.links.new(ab.outputs[0], mr.inputs['Value'])
        nt.links.new(mr.outputs[0], b.inputs['Roughness'])
    b.inputs['Base Color'].default_value = (hexlin(base) if isinstance(base, str) else base) + (1,)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular Tint'].default_value = (hexlin(edge) if isinstance(edge, str) else edge) + (1,)
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.05
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    return m


def m_glass(name, tint='LAVENDER', rough=0.22, ior=1.45, coat_r=0.03, sss=0.0, frost_color=None, frost=0.0,
            thin=False, trans=1.0):
    """Frosted / clear glass. frost>0 mixes in a milky subsurface layer (pricey); the cheap frosted
    look is thin=True (thin-wall transmission, no refraction offset) with trans<1 so a little diffuse
    tint scatters light like frosted acrylic."""
    m, b, nt = _principled(name)
    col = hexlin(tint) if isinstance(tint, str) else tuple(tint)
    b.inputs['Base Color'].default_value = col + (1,)
    b.inputs['Roughness'].default_value = rough
    b.inputs['IOR'].default_value = ior
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['Thin Wall'].default_value = bool(thin)
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Coat Roughness'].default_value = coat_r
    if frost:
        b2 = nt.nodes.new('ShaderNodeBsdfPrincipled')
        fc = frost_color or col
        fc = hexlin(fc) if isinstance(fc, str) else fc
        b2.inputs['Base Color'].default_value = tuple(fc) + (1,)
        b2.inputs['Roughness'].default_value = 0.3
        b2.inputs['Subsurface Weight'].default_value = 1.0
        b2.inputs['Subsurface Radius'].default_value = (1.0, 0.8, 1.0)
        b2.inputs['Subsurface Scale'].default_value = 0.3
        b2.inputs['Coat Weight'].default_value = 1.0
        b2.inputs['Coat Roughness'].default_value = coat_r
        mix = nt.nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = frost
        out = nt.nodes['Material Output']
        nt.links.new(b.outputs['BSDF'], mix.inputs[1])
        nt.links.new(b2.outputs['BSDF'], mix.inputs[2])
        nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m


def m_emit(name, color, strength=4.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (hexlin(color) if isinstance(color, str) else tuple(color)) + (1,)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


# ----------------------------------------------------------------------------- lighting rigs

def _aim(obj, target=(0, 0, 0)):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0), spread=180.0, shape='RECTANGLE',
         glossy=True, diffuse=True):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.shape = shape
    ld.size = size[0]
    ld.size_y = size[1]
    ld.energy = energy
    ld.color = hexlin(color) if isinstance(color, str) else color
    ld.spread = math.radians(spread)
    o = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    _aim(o, target)
    o.visible_glossy = glossy
    o.visible_diffuse = diffuse
    return o


def card(name, loc, size, color, strength, target=(0, 0, 0), shape='rect', soft=0.22):
    """Emissive soft-box card seen only in reflections (soft-edged highlight shapes on the coat).

    shape 'rect' fades `soft` of the way in from each edge; 'oval' is an elliptical soft dot."""
    _bpy()
    me = bpy.data.meshes.new(name)
    w, h = size[0] / 2, size[1] / 2
    me.from_pydata([(-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    _aim(o, target)
    mat = bpy.data.materials.new(name + '_m')
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    if shape == 'oval':
        sub = nt.nodes.new('ShaderNodeVectorMath')
        sub.operation = 'SUBTRACT'
        sub.inputs[1].default_value = (0.5, 0.5, 0.0)
        nt.links.new(tc.outputs['Generated'], sub.inputs[0])
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(sub.outputs[0], sep.inputs[0])
        comb = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(sep.outputs['X'], comb.inputs['X'])
        nt.links.new(sep.outputs['Y'], comb.inputs['Y'])
        ln = nt.nodes.new('ShaderNodeVectorMath')
        ln.operation = 'LENGTH'
        nt.links.new(comb.outputs[0], ln.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.interpolation_type = 'SMOOTHSTEP'
        mr.inputs['From Min'].default_value = 0.5
        mr.inputs['From Max'].default_value = 0.5 * (1 - 2 * soft)
        nt.links.new(ln.outputs['Value'], mr.inputs['Value'])
        prod = mr
    else:
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        prod = None
        for ax in ('X', 'Y'):
            mr = nt.nodes.new('ShaderNodeMapRange')
            mr.interpolation_type = 'SMOOTHSTEP'
            nt.links.new(sep.outputs[ax], mr.inputs['Value'])
            mr.inputs['From Min'].default_value = 0.0
            mr.inputs['From Max'].default_value = soft
            mr2 = nt.nodes.new('ShaderNodeMapRange')
            mr2.interpolation_type = 'SMOOTHSTEP'
            nt.links.new(sep.outputs[ax], mr2.inputs['Value'])
            mr2.inputs['From Min'].default_value = 1.0
            mr2.inputs['From Max'].default_value = 1.0 - soft
            mul = nt.nodes.new('ShaderNodeMath')
            mul.operation = 'MULTIPLY'
            nt.links.new(mr.outputs[0], mul.inputs[0])
            nt.links.new(mr2.outputs[0], mul.inputs[1])
            if prod is None:
                prod = mul
            else:
                m2 = nt.nodes.new('ShaderNodeMath')
                m2.operation = 'MULTIPLY'
                nt.links.new(prod.outputs[0], m2.inputs[0])
                nt.links.new(mul.outputs[0], m2.inputs[1])
                prod = m2
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (hexlin(color) if isinstance(color, str) else tuple(color)) + (1,)
    e.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')       # transparent outside the glow: never occludes the world
    nt.links.new(prod.outputs[0], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(e.outputs[0], mix.inputs[2])
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(mix.outputs[0], out.inputs[0])
    me.materials.append(mat)
    mat.cycles.emission_sampling = 'NONE'
    o.visible_camera = False
    o.visible_shadow = False
    o.visible_diffuse = False
    o.visible_transmission = True
    o.visible_volume_scatter = False
    return o


def world(variant, metal=False):
    """Night: dark plum dome + HOT_PINK (back-right) and ORANGE (back-left) soft-box blobs.
    Day: bright ivory dome, warm peach horizon, soft lavender/peach blobs."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W_' + variant)
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nrm = nt.nodes.new('ShaderNodeVectorMath')
    nrm.operation = 'NORMALIZE'
    nt.links.new(tc.outputs['Generated'], nrm.inputs[0])
    sepz = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(nrm.outputs[0], sepz.inputs[0])

    def blob(direction, cos0, cos1, color, strength):
        d = Vector(direction).normalized()
        dot = nt.nodes.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = d
        nt.links.new(nrm.outputs[0], dot.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.interpolation_type = 'SMOOTHERSTEP'
        mr.inputs['From Min'].default_value = cos0
        mr.inputs['From Max'].default_value = cos1
        mr.inputs['To Max'].default_value = strength
        nt.links.new(dot.outputs['Value'], mr.inputs['Value'])
        mul = nt.nodes.new('ShaderNodeVectorMath')
        mul.operation = 'SCALE'
        mul.inputs[0].default_value = hexlin(color) if isinstance(color, str) else color
        nt.links.new(mr.outputs[0], mul.inputs['Scale'])
        return mul

    def vgrad(c_lo, c_hi, s_lo, s_hi):
        # vertical gradient on z of the direction
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = -0.6
        mr.inputs['From Max'].default_value = 0.9
        nt.links.new(sepz.outputs['Z'], mr.inputs['Value'])
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        nt.links.new(mr.outputs[0], mix.inputs['Factor'])
        mix.inputs['A'].default_value = tuple(x * s_lo for x in (hexlin(c_lo) if isinstance(c_lo, str) else c_lo)) + (1,)
        mix.inputs['B'].default_value = tuple(x * s_hi for x in (hexlin(c_hi) if isinstance(c_hi, str) else c_hi)) + (1,)
        return mix

    if variant == 'night':
        base = vgrad('NIGHT_0', 'PLUM', 1.0, 0.55)
        pink = mixlin('HOT_PINK', 'AMBER', 0.55) if metal else 'HOT_PINK'
        blobs = [blob((0.85, 0.75, 0.35), 0.55, 0.92, pink, 1.4 if metal else 2.2),
                 blob((-0.9, 0.65, 0.1), 0.6, 0.93, 'ORANGE', 1.6),
                 blob((0.0, -0.4, 0.9), 0.75, 0.97, (1.0, 0.86, 0.80), 0.9)]
    else:
        base = vgrad((0.30, 0.22, 0.20), 'IVORY', 1.0, 0.9)
        blobs = [blob((0.85, 0.7, 0.3), 0.55, 0.92, 'PEACH', 0.7),
                 blob((-0.9, 0.6, 0.2), 0.6, 0.93, (1.0, 0.72, 0.78), 0.5),
                 blob((0.0, -0.4, 0.9), 0.75, 0.97, (1.0, 1.0, 1.0), 0.6),
                 # negative 'flag' behind the camera: front faces reflect a deeper warm tone
                 blob((0.0, -1.0, 0.05), 0.2, 0.85, (-0.55, -0.50, -0.48), 1.0)]
    acc = base.outputs['Result']
    for bl in blobs:
        add = nt.nodes.new('ShaderNodeVectorMath')
        add.operation = 'ADD'
        nt.links.new(acc, add.inputs[0])
        nt.links.new(bl.outputs[0], add.inputs[1])
        acc = add.outputs[0]
    nt.links.new(acc, bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0 if variant == 'night' else 0.8
    return w


def rig(variant, scale=1.0, key=1.0, cards=1.0, metal=False, soft_top=False):
    """Key / fill / rims + reflection cards. `scale` widens the rig for larger objects, `key` scales
    the key+fill energy, `cards` the strength of the reflection soft-boxes."""
    s = scale
    e = s * s
    warm = (1.0, 0.95, 0.89)
    k = key * (0.78 if variant == 'day' else 1.0)
    # illumination (kept out of glossy rays: reflections come from the soft cards below)
    area('key', (-3.4 * s, -4.4 * s, 4.4 * s), (4.0 * s, 4.0 * s), 520 * e * k, warm, glossy=False, shape='DISK')
    area('fill', (4.6 * s, -4.2 * s, 0.6 * s), (3.5 * s, 3.5 * s), 110 * e * k, (1.0, 0.96, 0.95), glossy=False,
         shape='DISK')
    # reflections: big soft oval key highlight, a crisp thin top-left strip, a faint broad front sheen
    card('kcard', (-3.0 * s, -4.0 * s, 4.0 * s), (3.4 * s, 2.4 * s), (1.0, 0.97, 0.93), 2.2 * cards, shape='oval',
         soft=0.35)
    card('kstrip', (-1.6 * s, -3.0 * s, 4.6 * s), (2.6 * s, 0.32 * s), (1.0, 1.0, 1.0), 6.0 * cards, soft=0.3)
    card('frontcard', (1.2 * s, -6.5 * s, 0.4 * s), (6.0 * s, 3.0 * s), (1.0, 0.95, 0.92), 0.22 * cards,
         shape='oval', soft=0.45)
    if soft_top:   # flat tops (mortarboard) would mirror the hard-edged top light: use a soft card instead
        card('tcard', (0.4 * s, 1.8 * s, 5.2 * s), (4.0 * s, 2.0 * s), (1.0, 0.86, 0.88), 0.9, shape='oval', soft=0.45)
    if metal:
        # polished metal only shows its environment: a warm soft-box wall behind the camera plus
        # glint strips left/right so faces sweep through highlights as they turn
        card('m_front', (0.0, -7.5 * s, -0.55 * s), (9.0 * s, 4.4 * s), (1.0, 0.90, 0.74), 1.5, shape='oval', soft=0.32)
        card('m_top', (0.0, -3.0 * s, 6.0 * s), (6.0 * s, 2.0 * s), (1.0, 0.95, 0.85), 2.4, soft=0.4)
        for k, (x, y) in enumerate(((-4.3, -6.2), (-7.0, -2.6), (4.3, -6.2), (7.0, -2.6))):
            card(f'm_glint{k}', (x * s, y * s, 0.2 * s), (0.9 * s, 6.0 * s), (1.0, 0.93, 0.80), 3.2, soft=0.3)
        card('m_low', (0.0, -5.0 * s, -3.5 * s), (6.0 * s, 1.2 * s), (1.0, 0.6, 0.3), 0.8, soft=0.4)
    if variant == 'night':
        area('rim_pink', (4.2 * s, 3.4 * s, 1.6 * s), (1.4 * s, 4.5 * s), 1300 * e,
             mixlin('HOT_PINK', 'AMBER', 0.5) if metal else 'HOT_PINK')
        area('rim_orange', (-4.4 * s, 3.0 * s, 0.2 * s), (1.4 * s, 4.5 * s), 1100 * e, 'ORANGE')
        area('top', (0.4 * s, 1.8 * s, 5.2 * s), (3.0 * s, 1.2 * s), 200 * e, (1.0, 0.82, 0.86), glossy=not soft_top)
    else:
        area('rim_peach', (4.2 * s, 3.4 * s, 1.6 * s), (1.4 * s, 4.5 * s), 900 * e, 'PEACH')
        area('rim_white', (-4.4 * s, 3.0 * s, 0.6 * s), (1.4 * s, 4.5 * s), 700 * e, (1.0, 0.95, 0.9))
        area('top', (0.4 * s, 1.8 * s, 5.2 * s), (3.0 * s, 1.2 * s), 200 * e, (1.0, 0.97, 0.93), glossy=not soft_top)


# ----------------------------------------------------------------------------- meshes in the scene

def add_mesh(name, V, Q, N, mat=None, icon_frame=True, parent=None):
    """Create a smooth-shaded mesh object from surface-nets output.

    icon_frame=True maps implicit coords (x right, y up, z towards the viewer) to Blender
    (X right, Z up, -Y towards the camera)."""
    _bpy()
    V = np.asarray(V, np.float64)
    N = np.asarray(N, np.float64)
    if icon_frame:
        V = np.stack([V[:, 0], -V[:, 2], V[:, 1]], 1)
        N = np.stack([N[:, 0], -N[:, 2], N[:, 1]], 1)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set('co', V.astype(np.float32).ravel())
    me.loops.add(len(Q) * 4)
    me.loops.foreach_set('vertex_index', Q.astype(np.int32).ravel())
    me.polygons.add(len(Q))
    me.polygons.foreach_set('loop_start', np.arange(0, 4 * len(Q), 4, dtype=np.int32))
    me.update(calc_edges=True)
    me.polygons.foreach_set('use_smooth', np.ones(len(Q), bool))
    me.normals_split_custom_set_from_vertices([tuple(n) for n in N.astype(np.float32)])
    if mat is not None:
        me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    return o


def sdf_object(name, F, bounds, res, mat, parent=None, icon_frame=True, shadow=True):
    """Mesh an implicit and add it to the scene. shadow=False for glass (caustics are off, so glass
    would otherwise cast a black shadow on whatever sits behind it)."""
    t = time.time()
    V, Q, N = mesh_sdf(F, bounds, res)
    o = add_mesh(name, V, Q, N, mat, icon_frame, parent)
    o.visible_shadow = shadow
    print(f'  mesh {name}: {len(V)} verts {len(Q)} quads in {time.time() - t:.1f}s', flush=True)
    return o


def empty(name='root', parent=None):
    _bpy()
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    return o


# ----------------------------------------------------------------------------- camera + framing

def _all_mesh_points(root, max_pts=60000):
    """World-space (at root identity) points of every mesh under root."""
    pts = []
    for o in root.children_recursive:
        if o.type != 'MESH' or o.hide_render:
            continue
        me = o.data
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        if len(co) > max_pts // 4:
            co = co[np.random.default_rng(0).choice(len(co), max_pts // 4, replace=False)]
        M = np.array(o.matrix_world)
        pts.append(co @ M[:3, :3].T + M[:3, 3])
    return np.concatenate(pts)


def frame_camera(root, angles, axis='z', fill=FILL, aspect=1.0, target=None):
    """Place an 80 mm camera 5 deg above the subject so the object, over every rotation in `angles`
    (degrees about the root's `axis`), fills `fill` of the frame and its union bbox is centred."""
    sc = bpy.context.scene
    cam_d = bpy.data.cameras.new('cam')
    cam_d.lens = LENS
    cam_d.sensor_fit = 'AUTO'
    cam_d.sensor_width = 36.0
    cam = bpy.data.objects.new('cam', cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    bpy.context.view_layer.update()
    P0 = _all_mesh_points(root)
    c = (P0.min(0) + P0.max(0)) / 2 if target is None else np.asarray(target, float)
    root_m = np.array(root.matrix_world)
    rots = []
    for a in angles:
        r = math.radians(a)
        cs, sn = math.cos(r), math.sin(r)
        if axis == 'z':
            R = np.array([[cs, -sn, 0], [sn, cs, 0], [0, 0, 1]])
        else:
            R = np.array([[1, 0, 0], [0, cs, -sn], [0, sn, cs]])
        rots.append(R)
    piv = root_m[:3, 3]
    allp = np.concatenate([(P0 - piv) @ R.T + piv for R in rots])
    el = math.radians(ELEV_DEG)
    fov_half = math.atan(18.0 / LENS)
    tz = c[2]
    dist = 6.0
    shift = np.zeros(2)
    for _ in range(6):
        cam_pos = np.array([c[0], -dist * math.cos(el), tz + dist * math.sin(el)])
        fwd = np.array([c[0], 0, tz]) - cam_pos
        fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0, 0, 1])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        rel = allp - cam_pos
        zc = rel @ fwd
        xs = (rel @ right) / zc / math.tan(fov_half)
        ys = (rel @ up) / zc / math.tan(fov_half)
        if aspect >= 1:
            ys = ys * aspect
        else:
            xs = xs / aspect
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        span = max(x1 - x0, y1 - y0) / 2      # in half-frame units
        shift = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        dist *= span / fill
    cam.location = Vector(cam_pos.tolist())
    _aim(cam, (c[0], 0, tz))
    # lens shift centres the swept bbox (shift is in units of the larger sensor dimension)
    cam_d.shift_x = shift[0] / 2 * (1 if aspect >= 1 else aspect)
    cam_d.shift_y = shift[1] / 2 / (aspect if aspect >= 1 else 1)
    cam_d.clip_start = 0.05
    cam_d.clip_end = 100
    return cam


def project_px(pt):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    co = world_to_camera_view(sc, sc.camera, Vector(pt))
    return [float(co.x * sc.render.resolution_x), float((1 - co.y) * sc.render.resolution_y)]


# ----------------------------------------------------------------------------- render loop + meta

def _alpha_stats(paths):
    import cv2
    bb = None
    ground = 0
    for p in paths:
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if im is None or im.ndim < 3 or im.shape[2] < 4:
            continue
        a = im[:, :, 3]
        ys, xs = np.nonzero(a > 8)
        if len(xs) == 0:
            continue
        b = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
        ys2 = np.nonzero((a > 128).any(1))[0]
        if len(ys2):
            ground = max(ground, int(ys2.max()))
    return bb, ground


def render_frames(outdir, n, update, frames=None, prefix=''):
    sc = bpy.context.scene
    os.makedirs(outdir, exist_ok=True)
    idx = list(range(n)) if frames is None else [f for f in frames if 0 <= f < n]
    paths = []
    t0 = time.time()
    for k, i in enumerate(idx):
        update(i, n)
        p = os.path.join(outdir, f'{i:04d}.png')
        sc.render.filepath = p
        if os.environ.get('SKIP_EXISTING') and os.path.exists(p):
            paths.append(p)
            continue
        bpy.ops.render.render(write_still=True)
        paths.append(p)
        el = time.time() - t0
        print(f'  {prefix} frame {i} ({k + 1}/{len(idx)}) {el / (k + 1):.1f}s/frame', flush=True)
    return paths


def write_meta(outdir, **kw):
    paths = sorted(os.path.join(outdir, f) for f in os.listdir(outdir) if f.endswith('.png'))
    bb, ground = _alpha_stats(paths)
    if bb is not None:
        kw.setdefault('anchor', [round((bb[0] + bb[2]) / 2, 1), round((bb[1] + bb[3]) / 2, 1)])
        kw['bbox'] = bb
        kw['ground_y'] = ground
    kw['rendered'] = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.join(outdir, 'meta.json'), 'w') as f:
        json.dump(kw, f, indent=1)
    return kw


# ============================================================================= assets
# Each builder(root, variant, q) creates meshes under `root` (an empty at the origin; the renderer
# yaws/spins the root) and returns a dict of options: rig_scale, key, notes, labels, per-frame hooks.
# q is a quality factor for mesh resolution (1.0 finals, ~0.6 previews).

class AssetSpec:
    def __init__(self, builder, variants, modes=('yaw',), size=(720, 720), notes='', spin_size=(1000, 1000)):
        self.builder, self.variants, self.modes = builder, tuple(variants), tuple(modes)
        self.size, self.notes, self.spin_size = size, notes, spin_size


ASSETS = {}


def asset(name, variants, modes=('yaw',), size=(720, 720), notes=''):
    def deco(fn):
        ASSETS[name] = AssetSpec(fn, variants, modes, size, notes)
        return fn
    return deco


def R(q, base):
    return max(48, int(base * q))


@asset('heart', ('night', 'day'), notes='puffy MAGENTA candy heart, HOT_PINK subsurface glow')
def build_heart(root, variant, q=1.0):
    sd = sd_heart(2.0, convex=0.14, concave=0.16)
    F = inflate(sd, thick=0.16, edge=0.16, dome=0.30, dome_field=sd.poisson(), dome_pow=0.55)
    mat = m_candy('heart', 'MAGENTA', rough=0.28, coat_r=0.035, sss=0.35, sss_radius=(1.0, 0.2, 0.6),
                  sss_scale=0.18, rim_glow='HOT_PINK', rim_str=0.9 if variant == 'night' else 0.4,
                  random_walk=True)
    sdf_object('heart', F, ((-1.1, -1.0, -0.65), (1.1, 1.0, 0.65)), R(q, 230), mat, root)
    return {}




def poly_sd(polys, pad=0.25, res=1400):
    """Raster2D sd of polygon(s) (even-odd) with automatic bounds."""
    allp = np.concatenate([np.asarray(p, float) for p in polys])
    lo, hi = allp.min(0) - pad, allp.max(0) + pad
    c = (lo + hi) / 2
    h = (hi - lo).max() / 2
    return Raster2D.from_polys(polys, (c[0] - h, c[1] - h, c[0] + h, c[1] + h), res)


def fn_sd(fn, bounds, res=1200):
    """Raster2D of an analytic sd (cheap resampling, enables .poisson())."""
    return Raster2D.from_fn(fn, bounds, res)


def bez2(p0, p1, p2, n=40):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = (np.asarray(p, float) for p in (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2


def shield_outline(w=0.86, top=0.80, arch=0.10, side_end=0.08, tip=-1.02, ctrl=(0.80, -0.60)):
    xs = np.linspace(-w, w, 60)
    topc = np.stack([xs, top + arch * (1 - (xs / w) ** 2)], 1)
    right = np.stack([np.full(12, w), np.linspace(top, side_end, 12)], 1)
    rb = bez2((w, side_end), ctrl, (0.0, tip), 50)
    lb = bez2((0.0, tip), (-ctrl[0], ctrl[1]), (-w, side_end), 50)
    left = np.stack([np.full(12, -w), np.linspace(side_end, top, 12)], 1)
    P = np.concatenate([topc, right[1:], rb[1:], lb[1:], left[1:-1]])
    return P


def squircle(r=0.9, n=4.6, k=400):
    a = np.linspace(0, 2 * np.pi, k, endpoint=False)
    c, s_ = np.cos(a), np.sin(a)
    return np.stack([r * np.sign(c) * np.abs(c) ** (2 / n), r * np.sign(s_) * np.abs(s_) ** (2 / n)], 1)


def star_outline(outer=0.5, inner=0.23, pts=5, rot=np.pi / 2):
    a = rot + np.arange(2 * pts) * np.pi / pts
    r = np.where(np.arange(2 * pts) % 2 == 0, outer, inner)
    return np.stack([r * np.cos(a), r * np.sin(a)], 1)


CHECK_PTS = [(-0.40, 0.02), (-0.11, -0.28), (0.43, 0.30)]


@asset('shield_check', ('night', 'day'), notes='MAGENTA shield, frosted-glass inner layer, white raised check')
def build_shield(root, variant, q=1.0):
    P = shield_outline()
    sd = poly_sd([P], res=1400).rounded(0.20, 0.0).blurred(1.0)
    body = inflate(sd, thick=0.20, edge=0.18, dome=0.07, dome_field=sd.poisson(), dome_pow=0.6)
    mb = m_candy('shield', 'MAGENTA', rough=0.28, coat_r=0.035, rim_glow='HOT_PINK',
                 rim_str=0.8 if variant == 'night' else 0.35)
    sdf_object('shield', body, ((-1.05, -1.15, -0.45), (1.05, 1.05, 0.45)), R(q, 220), mb, root)
    gl = Raster2D(sd.g + 0.15, sd.b).blurred(0.5)
    glass = inflate(gl, thick=0.065, edge=0.06, zc=0.355)
    if variant == 'night':
        mg = m_glass('shield_glass', (0.99, 0.90, 0.96), rough=0.30, ior=1.45, thin=True, trans=0.78)
    else:   # day: a vivid light-pink frosted pane (the ivory world would otherwise read it as mauve)
        mg = m_glass('shield_glass', (1.0, 0.50, 0.74), rough=0.27, ior=1.45, thin=True, trans=0.80)
    sdf_object('shield_glass', glass, ((-0.9, -0.95, 0.2), (0.9, 0.9, 0.5)), R(q, 200), mg, root, shadow=False)
    ck = fn_sd(sd_polyline([(x * 0.95, y * 0.95 + 0.0) for x, y in CHECK_PTS], 0.095), (-0.7, -0.6, 0.7, 0.6), 900)
    chk = inflate(ck, thick=0.06, edge=0.058, dome=0.035, dome_field=ck.poisson(240), zc=0.425)
    mw = m_candy('check_w', (0.93, 0.92, 0.94), rough=0.25, coat_r=0.03)
    sdf_object('check', chk, ((-0.62, -0.5, 0.33), (0.62, 0.5, 0.55)), R(q, 200), mw, root)
    return {'glass': True}


@asset('check_tile', ('night', 'day'), notes='LEAF-green rounded tile with a white raised check')
def build_check_tile(root, variant, q=1.0):
    sd = poly_sd([squircle(0.92, 4.4)], res=1400).blurred(1.0)
    body = inflate(sd, thick=0.24, edge=0.21, dome=0.05, dome_field=sd.poisson(), dome_pow=0.6)
    mb = m_candy('tile', 'LEAF', rough=0.28, coat_r=0.035, grad=(mixlin('LEAF', 'LEAF_HI', 0.45), -0.9, 1.3),
                 rim_glow='LEAF_HI', rim_str=0.35 if variant == 'night' else 0.15)
    sdf_object('tile', body, ((-1.0, -1.0, -0.36), (1.0, 1.0, 0.36)), R(q, 220), mb, root)
    ck = fn_sd(sd_polyline([(x * 1.05, y * 1.05) for x, y in CHECK_PTS], 0.12), (-0.7, -0.6, 0.7, 0.6), 900)
    chk = inflate(ck, thick=0.075, edge=0.072, dome=0.04, dome_field=ck.poisson(240), zc=0.30)
    mw = m_candy('check_w', (0.93, 0.92, 0.94), rough=0.25, coat_r=0.03)
    sdf_object('check', chk, ((-0.68, -0.55, 0.18), (0.68, 0.55, 0.45)), R(q, 200), mw, root)
    return {}


@asset('house', ('night', 'day'), notes='rounded toy house: ivory walls, MAGENTA roof, glowing ORANGE heart door')
def build_house(root, variant, q=1.0):
    W = dict(icon_frame=False)
    # walls + gable (ivory) with recesses for the door and windows
    walls = sd3_round_box((0, 0, -0.43), (0.70, 0.56, 0.50), 0.13)
    gable2 = op_offset(sd_poly_exact([(-0.70, 0.02), (0.70, 0.02), (0.0, 0.70)]), 0.05)
    gable = extrude_axis(gable2, 'y', 0.53, 0.06)
    body = u_smin(walls, gable, 0.06)
    door2 = sd_rbox(0.0, -0.60, 0.20, 0.30, 0.19)
    door_cut = extrude_axis(door2, 'y', 0.07, 0.02, center=-0.58)
    win2 = sd_circle(0.0, 0.30, 0.15)
    win_cut = extrude_axis(win2, 'y', 0.06, 0.02, center=-0.54)
    side2 = sd_rbox(0.0, -0.40, 0.17, 0.17, 0.07)          # (y, z) on the side walls
    side_cut_r = extrude_axis(side2, 'x', 0.07, 0.02, center=0.70)
    side_cut_l = extrude_axis(side2, 'x', 0.07, 0.02, center=-0.70)
    body = u_ssub(u_ssub(u_ssub(u_ssub(body, door_cut, 0.015), win_cut, 0.015), side_cut_r, 0.015), side_cut_l, 0.015)
    ivory = m_candy('walls', 'IVORY', rough=0.32, coat_r=0.05, sss=0.15, sss_radius=(1.0, 0.7, 0.5), sss_scale=0.05,
                    grad=((1.0, 0.97, 0.95), -0.9, 0.6))
    sdf_object('walls', body, ((-0.8, -0.66, -1.0), (0.8, 0.66, 0.82)), R(q, 230), ivory, root, **W)
    # roof: a thick rounded chevron
    roof2 = op_union(sd_segment(0.0, 0.86, -0.98, 0.06, 0.115), sd_segment(0.0, 0.86, 0.98, 0.06, 0.115))
    roof = extrude_axis(roof2, 'y', 0.70, 0.10)
    chim = sd3_round_box((0.50, 0.18, 0.66), (0.12, 0.12, 0.24), 0.06)
    chim_cap = sd3_round_box((0.50, 0.18, 0.90), (0.16, 0.16, 0.05), 0.045)
    roofc = u_smin(roof, u_min(chim, chim_cap), 0.04)
    mag = m_candy('roof', 'MAGENTA', rough=0.28, coat_r=0.035, rim_glow='HOT_PINK',
                  rim_str=0.6 if variant == 'night' else 0.25)
    sdf_object('roof', roofc, ((-1.15, -0.82, -0.12), (1.15, 0.82, 1.02)), R(q, 240), mag, root, **W)
    # door: orange glossy slab with a heart cut-out, glowing interior behind it
    hs = sd_heart(0.17, convex=0.14, concave=0.16, res=500)
    heart_cut = op_xform(hs, 0.0, -0.52)
    door_s = op_sub(op_offset(door2, -0.035), heart_cut)
    door = extrude_axis(door_s, 'y', 0.022, 0.018, center=-0.545)
    mdoor = m_candy('door', 'ORANGE', rough=0.25, coat_r=0.03, emit='ORANGE', emit_str=0.9,
                    rim_glow='AMBER', rim_str=0.6)
    sdf_object('door', door, ((-0.24, -0.6, -0.95), (0.24, -0.49, -0.25)), R(q, 160), mdoor, root, **W)
    knob = sd3_sphere((0.12, -0.575, -0.68), 0.028)
    mknob = m_gold('knob', rough=0.2)
    sdf_object('knob', knob, ((0.08, -0.62, -0.72), (0.16, -0.53, -0.64)), 40, mknob, root, **W)
    glow = m_emit('glow', (1.0, 0.55, 0.16), 9.0)
    back = sd3_round_box((0.0, -0.51, -0.60), (0.19, 0.012, 0.29), 0.01)
    sdf_object('door_glow', back, ((-0.22, -0.54, -0.92), (0.22, -0.48, -0.28)), R(q, 100), glow, root, **W)
    # gable round window + side windows: glowing panes with ivory muntins
    pane = m_emit('pane', (1.0, 0.50, 0.12), 6.0)
    wpane = sd3_round_box((0.0, -0.515, 0.30), (0.15, 0.01, 0.15), 0.01)
    sdf_object('win_pane', u_isect(wpane, extrude_axis(sd_circle(0.0, 0.30, 0.15), 'y', 0.2, 0.0, center=-0.515)),
               ((-0.17, -0.54, 0.12), (0.17, -0.49, 0.48)), R(q, 90), pane, root, **W)
    bars = u_min(extrude_axis(sd_segment(-0.16, 0.30, 0.16, 0.30, 0.018), 'y', 0.02, 0.012, center=-0.535),
                 extrude_axis(sd_segment(0.0, 0.14, 0.0, 0.46, 0.018), 'y', 0.02, 0.012, center=-0.535))
    sdf_object('win_bars', bars, ((-0.18, -0.57, 0.12), (0.18, -0.5, 0.48)), R(q, 110), ivory, root, **W)
    for sx in (-1, 1):
        sp = sd3_round_box((sx * 0.655, 0.0, -0.40), (0.01, 0.17, 0.17), 0.01)
        sdf_object(f'side_pane{sx}', sp, ((sx * 0.655 - 0.03, -0.2, -0.6), (sx * 0.655 + 0.03, 0.2, -0.2)), R(q, 80),
                   pane, root, **W)
        sb = u_min(extrude_axis(sd_segment(-0.17, -0.40, 0.17, -0.40, 0.017), 'x', 0.02, 0.012, center=sx * 0.672),
                   extrude_axis(sd_segment(0.0, -0.57, 0.0, -0.23, 0.017), 'x', 0.02, 0.012, center=sx * 0.672))
        sdf_object(f'side_bars{sx}', sb, ((sx * 0.672 - 0.04, -0.2, -0.6), (sx * 0.672 + 0.04, 0.2, -0.2)),
                   R(q, 110), ivory, root, **W)
    # a little leaf bush at the front-left corner
    bush = u_smin(u_smin(sd3_sphere((-0.74, -0.50, -0.80), 0.21), sd3_sphere((-0.52, -0.62, -0.88), 0.14), 0.06),
                  sd3_sphere((-0.88, -0.30, -0.86), 0.15), 0.06)
    mleaf = m_candy('bush', 'LEAF', rough=0.3, coat_r=0.04, grad=('LEAF_HI', -1.0, -0.55), rim_glow='LEAF_HI',
                    rim_str=0.3)
    sdf_object('bush', bush, ((-1.08, -0.8, -1.05), (-0.36, -0.12, -0.56)), R(q, 120), mleaf, root, **W)
    return {}


def glyph_sd(char, font='Nunito-Black.ttf', height=1.0, res=1100, pad=0.15):
    """2D SDF of a glyph rasterised by FreeType (non-zero winding, so fonts whose outlines overlap or
    self-intersect at stroke joins stay solid), cap-height normalised to `height`, centred on its bbox."""
    from PIL import Image, ImageDraw, ImageFont
    fnt = ImageFont.truetype(os.path.join(FONTS, font), 900)
    l, t, r, b = fnt.getbbox(char)
    gw, gh = r - l, b - t
    side_units = max(gw, gh) / gh * height + 2 * pad
    px_per_unit = res / side_units
    k = px_per_unit * height / gh                     # glyph px -> raster px
    fnt = ImageFont.truetype(os.path.join(FONTS, font), max(8, int(round(900 * k))))
    l, t, r, b = fnt.getbbox(char)
    img = Image.new('L', (res, res), 0)
    ImageDraw.Draw(img).text((res / 2 - (l + r) / 2, res / 2 - (t + b) / 2), char, font=fnt, fill=255)
    mask = np.flipud(np.asarray(img) > 127)          # raster row 0 = bottom (y up)
    h = side_units / 2
    return Raster2D.from_mask(mask.copy(), (-h, -h, h, h))


def pound_sd(height=1.0, res=1100):
    """Pound sign SDF. FreeType fill + a small closing, so the joins stay solid (the even-odd polygon
    fill of the raw outline leaves notches where Nunito's strokes meet) and inner corners soften."""
    return glyph_sd('£', 'Nunito-Black.ttf', height, res).rounded(concave=0.02 * height).blurred(0.8)


@asset('coin_gbp', ('night', 'day'), modes=('yaw', 'spin'), notes='thick polished gold coin, embossed pound sign, reeded rim')
def build_coin(root, variant, q=1.0):
    Rr, T = 1.0, 0.155
    reeds = 120

    def disc2(x, y):
        r = np.hypot(x, y)
        th = np.arctan2(y, x)
        return r - (Rr - 0.009 * (0.5 + 0.5 * np.cos(reeds * th)))
    D = fn_sd(disc2, (-1.05, -1.05, 1.05, 1.05), 1600)
    coin = extrude_axis(D, 'z', T, 0.045)
    lip2 = lambda x, y: np.abs(np.hypot(x, y) - 0.905) - 0.06
    lip_f = extrude_axis(lip2, 'z', T + 0.032, 0.03)

    def beads(x, y, z):                    # ring of 48 small domes, both faces
        r = np.hypot(x, y)
        th = np.arctan2(y, x)
        per = 2 * np.pi / 48
        tl = np.mod(th + per / 2, per) - per / 2
        lx, ly = r * np.cos(tl) - 0.78, r * np.sin(tl)
        return np.sqrt(lx * lx + ly * ly + (np.abs(z) - T + 0.005) ** 2) - 0.026
    P = pound_sd(1.02)
    Pm = lambda x, y: P(-x, y)             # back face: mirrored so the coin is 180 deg symmetric

    def emb(x, y, z):
        front = inflate(P, thick=0.04, edge=0.028, zc=T - 0.005)(x, y, z)
        backf = inflate(Pm, thick=0.04, edge=0.028, zc=-(T - 0.005))(x, y, z)
        return np.minimum(front, backf)
    F = u_smin(u_smin(u_smin(coin, lip_f, 0.012), beads, 0.008), emb, 0.012)
    if variant == 'day':   # the ivory world reads AMBER as copper: lift it towards a yellow gold
        mg = m_gold('gold', base=mixlin('AMBER', '#FFD27A', 0.45), edge=mixlin('ORANGE', 'AMBER', 0.35), rough=0.15,
                    relief=('Y', T + 0.004, T + 0.02, 0.34))
    else:
        mg = m_gold('gold', rough=0.15, relief=('Y', T + 0.004, T + 0.02, 0.34))
    sdf_object('coin', F, ((-1.04, -1.04, -0.23), (1.04, 1.04, 0.23)), R(q, 420), mg, root)
    return {'metal': True, 'sym180': True, 'notes': 'polished gold coin, pound sign both faces'}


@asset('orbs', ('night', 'day'), modes=('static',),
       notes='ambient depth objects: 0 magenta, 1 orange, 2 peach, 3 leaf spheres, 4 glass torus, 5 capsule')
def build_orbs(root, variant, q=1.0):
    objs = []
    for k, col in enumerate(('MAGENTA', 'ORANGE', 'PEACH', 'LEAF')):
        e = empty(f'o{k}', root)
        m = m_candy(f'orb{k}', col, rough=0.26, coat_r=0.03, sss=0.25 if col != 'PEACH' else 0.4,
                    sss_radius=(1.0, 0.5, 0.4), sss_scale=0.15,
                    rim_glow={'MAGENTA': 'HOT_PINK', 'ORANGE': 'AMBER', 'PEACH': 'IVORY', 'LEAF': 'LEAF_HI'}[col],
                    rim_str=0.6 if variant == 'night' else 0.25)
        sdf_object(f'sphere{k}', sd3_sphere((0, 0, 0), 0.92), ((-1, -1, -1), (1, 1, 1)), R(q, 150), m, e, False)
        objs.append(e)
    e = empty('o4', root)
    tor = u_xform(sd3_torus((0, 0, 0), 0.66, 0.27, 'y'), rx=math.radians(-62), rz=math.radians(28))
    mg = m_glass('torus_glass', (0.98, 0.93, 0.98), rough=0.06, ior=1.45)
    sdf_object('torus', tor, ((-1, -1, -1), (1, 1, 1)), R(q, 200), mg, e, False, shadow=False)
    objs.append(e)
    e = empty('o5', root)
    a, b = np.array([-0.52, 0, -0.52]), np.array([0.52, 0, 0.52])
    cap = sd3_capsule(a, b, 0.36)
    half = lambda x, y, z: (x + z) / math.sqrt(2)   # split plane across the capsule axis
    m1 = m_candy('cap_m', 'MAGENTA', rough=0.24, coat_r=0.03, rim_glow='HOT_PINK', rim_str=0.6)
    m2 = m_candy('cap_o', 'ORANGE', rough=0.24, coat_r=0.03, rim_glow='AMBER', rim_str=0.6)
    sdf_object('cap_a', u_sisect(cap, lambda x, y, z: half(x, y, z) + 0.006, 0.05), ((-1, -0.5, -1), (0.42, 0.5, 0.42)),
               R(q, 170), m1, e, False)
    sdf_object('cap_b', u_sisect(cap, lambda x, y, z: -half(x, y, z) + 0.006, 0.05), ((-0.42, -0.5, -0.42), (1, 0.5, 1)),
               R(q, 170), m2, e, False)
    objs.append(e)
    return {'objects': objs, 'labels': ['sphere_magenta', 'sphere_orange', 'sphere_peach', 'sphere_leaf',
                                        'torus_glass', 'capsule_magenta_orange'], 'glass': True}


@asset('grad_cap', ('night',), size=(560, 560), notes='PLUM glossy mortarboard with an ORANGE tassel')
def build_grad_cap(root, variant, q=1.0):
    W = dict(icon_frame=False)
    tilt = math.radians(30)
    t = empty('tilt', root)
    t.rotation_euler = (tilt, 0, 0)
    # skull cap: a rounded, slightly flared cylinder with a band
    def skull_f(x, y, z):
        r = np.hypot(x, y)
        rad = 0.60 + 0.06 * np.clip((z + 0.45) / 0.6, 0, 1)
        d2 = r - rad
        wx = d2 + 0.12
        wy = np.abs(z + 0.16) - (0.38 - 0.12)
        return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx, 0), np.maximum(wy, 0)) - 0.12
    board = u_xform(sd3_round_box((0, 0, 0), (0.98, 0.98, 0.09), 0.07), t=(0, 0, 0.28), rz=math.pi / 4)
    mp = m_candy('plum', 'PLUM', rough=0.26, coat_r=0.035, rim_glow='MAGENTA', rim_str=0.5)
    sdf_object('skull', skull_f, ((-0.8, -0.8, -0.7), (0.8, 0.8, 0.25)), R(q, 170), mp, t, **W)
    sdf_object('board', board, ((-1.45, -1.45, 0.15), (1.45, 1.45, 0.38)), R(q, 320), mp, t, **W)
    mo = m_candy('tassel', 'ORANGE', rough=0.28, coat_r=0.04, rim_glow='AMBER', rim_str=0.6)
    btn = u_smin(sd3_sphere((0, 0, 0.40), 0.09), extrude_axis(sd_circle(0, 0, 0.11), 'z', 0.025, 0.018, center=0.37), 0.025)
    sdf_object('button', btn, ((-0.15, -0.15, 0.3), (0.15, 0.15, 0.52)), 70, mo, t, **W)
    corner_local = np.array([0.98 * math.sqrt(2) - 0.08, 0.0, 0.385])
    cord1 = u_smin(sd3_capsule((0.05, 0, 0.40), corner_local, 0.032), sd3_sphere(corner_local, 0.05), 0.02)
    sdf_object('cord1', cord1, ((-0.05, -0.1, 0.28), (1.45, 0.1, 0.50)), R(q, 260), mo, t, **W)
    c, sn = math.cos(tilt), math.sin(tilt)
    cw = np.array([corner_local[0], corner_local[1] * c - corner_local[2] * sn, corner_local[1] * sn + corner_local[2] * c])
    knot = cw + np.array([0, 0, -0.50])
    hang = u_smin(sd3_capsule(cw, knot, 0.032), sd3_sphere(knot, 0.085), 0.03)

    def fringe(x, y, z):
        d = np.full(np.broadcast(x, y, z).shape, 10.0)
        for k in range(16):
            a = 2 * np.pi * k / 16
            tip = knot + np.array([0.10 * math.cos(a), 0.10 * math.sin(a), -0.40])
            d = np.minimum(d, sd3_capsule(knot + np.array([0.04 * math.cos(a), 0.04 * math.sin(a), -0.05]), tip,
                                          0.026)(x, y, z))
        return d
    tas = u_smin(hang, fringe, 0.04)
    tas = u_smin(tas, sd3_capsule(knot + np.array([0, 0, -0.02]), knot + np.array([0, 0, -0.14]), 0.09), 0.03)
    lo = np.minimum(cw, knot) - np.array([0.2, 0.2, 0.5])
    hi = np.maximum(cw, knot) + np.array([0.2, 0.2, 0.1])
    sdf_object('tassel', tas, (tuple(lo), tuple(hi)), R(q, 220), mo, root, **W)
    return {'soft_top': True}


@asset('chat_bubble', ('night',), size=(560, 560), notes='frosted lavender glass speech bubble with three MAGENTA dots')
def build_chat(root, variant, q=1.0):
    body2 = sd_rbox(0.0, 0.14, 0.98, 0.70, 0.60)
    tail2 = op_offset(sd_poly_exact([(-0.58, -0.26), (-0.20, -0.40), (-0.78, -0.86)]), 0.05)
    sd = fn_sd(op_smin(body2, tail2, 0.16), (-1.15, -1.15, 1.15, 1.15), 1200)
    F = inflate(sd, thick=0.16, edge=0.16, dome=0.16, dome_field=sd.poisson(), dome_pow=0.55)
    mg = m_glass('bubble', (0.90, 0.85, 0.99), rough=0.30, ior=1.42, thin=True, trans=0.72)
    sdf_object('bubble', F, ((-1.1, -1.05, -0.4), (1.1, 0.95, 0.4)), R(q, 230), mg, root, shadow=False)
    md = m_candy('dots', 'MAGENTA', rough=0.24, coat_r=0.03, rim_glow='HOT_PINK', rim_str=0.7)
    dots = lambda x, y, z: np.minimum.reduce([
        inflate(lambda u, v, cx=cx: np.hypot(u - cx, v - 0.14) - 0.135, thick=0.07, edge=0.07, dome=0.05,
                dome_r=0.13, zc=0.30)(x, y, z) for cx in (-0.42, 0.0, 0.42)])
    sdf_object('dots', dots, ((-0.6, -0.05, 0.18), (0.6, 0.33, 0.45)), R(q, 200), md, root)
    return {'glass': True}


@asset('key_heart', ('night',), size=(560, 560), notes='polished gold key with a heart-shaped bow')
def build_key(root, variant, q=1.0):
    bow = op_xform(sd_heart(1.10, convex=0.14, concave=0.18, res=900), 0.0, 0.52)
    hole = op_xform(sd_heart(0.40, convex=0.14, concave=0.2, res=500), 0.0, 0.56)
    ring = op_sub(bow, hole)
    shaft = sd_rbox(0.0, -0.46, 0.105, 0.62, 0.09)
    collar = sd_rbox(0.0, 0.00, 0.19, 0.06, 0.055)
    t1 = sd_rbox(0.17, -0.90, 0.14, 0.07, 0.045)
    t2 = sd_rbox(0.15, -0.66, 0.11, 0.055, 0.04)
    shape = op_smin(op_smin(op_smin(op_smin(ring, shaft, 0.06), collar, 0.04), t1, 0.04), t2, 0.04)
    shape = op_xform(shape, 0.0, 0.10, rot=math.radians(32))
    sd = fn_sd(shape, (-1.2, -1.2, 1.2, 1.2), 1300)
    F = inflate(sd, thick=0.10, edge=0.095, dome=0.07, dome_field=sd.poisson(), dome_pow=0.5)
    mg = m_gold('keygold', rough=0.17)
    sdf_object('key', F, ((-1.15, -1.15, -0.3), (1.15, 1.15, 0.3)), R(q, 300), mg, root)
    return {'metal': True}


@asset('star_badge', ('night', 'day'), size=(560, 560), notes='AMBER gold star on a MAGENTA rosette with ribbon tails (generic award)')
def build_star(root, variant, q=1.0):
    cy = 0.24
    a = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    rr = 0.74 + 0.04 * np.cos(20 * a)
    ros = poly_sd([np.stack([rr * np.cos(a), cy + rr * np.sin(a)], 1)], res=1300).blurred(1.5)
    disc = inflate(ros, thick=0.13, edge=0.11, dome=0.04, dome_field=ros.poisson(), dome_pow=0.6)
    mm = m_candy('rosette', 'MAGENTA', rough=0.28, coat_r=0.035, rim_glow='HOT_PINK',
                 rim_str=0.7 if variant == 'night' else 0.3)
    sdf_object('rosette', disc, ((-0.9, cy - 0.9, -0.3), (0.9, cy + 0.9, 0.3)), R(q, 220), mm, root)
    tails = []
    for sx in (-1, 1):
        x0, x1 = sx * 0.16, sx * 0.52
        poly = [(x0 - 0.20 * sx, -0.05), (x0 + 0.14 * sx, -0.05), (x1 + 0.17 * sx, -1.00), (x1, -0.86),
                (x1 - 0.17 * sx, -1.00)]
        tails.append(op_offset(sd_poly_exact(poly), 0.035))
    tl = fn_sd(op_union(*tails), (-1.0, -1.15, 1.0, 0.25), 900)
    tf = inflate(tl, thick=0.05, edge=0.045, zc=-0.10)
    mt = m_candy('ribbon', mixlin('MAGENTA', 'PLUM', 0.35), rough=0.3, coat_r=0.04, rim_glow='HOT_PINK', rim_str=0.4)
    sdf_object('ribbon', tf, ((-0.85, -1.1, -0.2), (0.85, 0.1, 0.0)), R(q, 180), mt, root)
    ring = lambda x, y, z: inflate(lambda u, v: np.abs(np.hypot(u, v - cy) - 0.58) - 0.028, thick=0.03, edge=0.028,
                                   zc=0.15)(x, y, z)
    mgold = m_gold('stargold', rough=0.2)
    sdf_object('ring', ring, ((-0.66, cy - 0.66, 0.08), (0.66, cy + 0.66, 0.22)), R(q, 240), mgold, root)
    st = poly_sd([star_outline(0.50, 0.235) + np.array([0, cy])], res=1100).rounded(0.07, 0.035).blurred(1.0)
    star = inflate(st, thick=0.06, edge=0.06, dome=0.11, dome_field=st.poisson(), dome_pow=0.55, zc=0.15)
    sdf_object('star', star, ((-0.6, cy - 0.6, 0.0), (0.6, cy + 0.6, 0.38)), R(q, 220), mgold, root)
    return {'metal': True}


@asset('pin_phone', ('night',), size=(560, 560), notes='ORANGE glossy phone handset ("call us") with two MAGENTA signal arcs')
def build_phone(root, variant, q=1.0):
    c = np.array([0.50, 0.50])
    rad = 1.02
    a0, a1 = math.radians(158), math.radians(292)
    arc = [(c[0] + rad * math.cos(t), c[1] + rad * math.sin(t)) for t in np.linspace(a0 + 0.15, a1 - 0.15, 40)]
    handle = sd_polyline(arc, 0.16)
    parts = [handle]
    for t, sgn in ((a0, -1), (a1, 1)):
        u = -np.array([math.cos(t), math.sin(t)])            # towards the arc centre (inner side)
        v = np.array([-math.sin(t), math.cos(t)]) * sgn       # along the arc, outwards past the end
        pc = c - u * rad + u * 0.11 + v * 0.02
        ang = math.atan2(v[1], v[0])
        parts.append(op_xform(sd_rbox(0, 0, 0.29, 0.215, 0.15), pc[0], pc[1], rot=ang))
    shape = op_smin(op_smin(parts[0], parts[1], 0.09), parts[2], 0.09)
    sd = fn_sd(shape, (-1.0, -1.0, 1.3, 1.3), 1200)
    F = inflate(sd, thick=0.17, edge=0.16, dome=0.08, dome_field=sd.poisson(), dome_pow=0.55)
    mo = m_candy('phone', 'ORANGE', rough=0.27, coat_r=0.035, rim_glow='AMBER', rim_str=0.6,
                 grad=((1.0, 0.25, 0.04), -0.8, 0.9))
    sdf_object('phone', F, ((-1.0, -1.0, -0.38), (1.3, 1.3, 0.38)), R(q, 260), mo, root)
    arcs = []
    for r_ in (0.42, 0.70):
        pts = [(0.42 + r_ * math.cos(t), 0.42 + r_ * math.sin(t)) for t in np.linspace(math.radians(10), math.radians(80), 24)]
        arcs.append(sd_polyline(pts, 0.065))
    ar = fn_sd(op_union(*arcs), (0.3, 0.3, 1.35, 1.35), 700)
    af = inflate(ar, thick=0.065, edge=0.062, zc=0.0)
    ma = m_candy('signal', 'MAGENTA', rough=0.26, coat_r=0.035, rim_glow='HOT_PINK', rim_str=0.7)
    sdf_object('signal', af, ((0.3, 0.3, -0.15), (1.3, 1.3, 0.15)), R(q, 200), ma, root)
    return {}

# ----------------------------------------------------------------------------- contact sheets (no bpy)

def _read_rgba_lin(p):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None:
        return None
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    rgb = im[:, :, 2::-1].astype(np.float32) / 255.0
    a = im[:, :, 3:4].astype(np.float32) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return np.concatenate([lin * a, a], 2)


def _bg(h, w, kind):
    yy = np.linspace(0, 1, h)[:, None, None]
    if kind == 'night':
        a, b = np.array(hexlin('NIGHT_1')), np.array(hexlin('NIGHT_0'))
    else:
        a, b = np.array(hexlin('IVORY')), np.array(hexlin('LAVENDER')) * 0.97
    img = a * (1 - yy) + b * yy
    return np.broadcast_to(img, (h, w, 3)).copy()


def contact_sheet(entries, out_path, cell=300, bgs=('night', 'day'), label=True):
    """entries: [(label, [png paths...]), ...] -> a sheet with one row per entry and per background.

    Each row shows the given frames composited (premultiplied, linear) over a NIGHT gradient and an
    IVORY gradient side by side."""
    import cv2
    rows = []
    for lab, paths in entries:
        for kind in bgs:
            tiles = []
            for p in paths:
                im = _read_rgba_lin(p)
                tile = _bg(cell, cell, kind)
                if im is not None:
                    im = cv2.resize(im, (cell, cell), interpolation=cv2.INTER_AREA)
                    tile = im[:, :, :3] + tile * (1 - im[:, :, 3:4])
                tiles.append(tile)
            row = np.concatenate(tiles, 1)
            srgb = np.where(row <= 0.0031308, row * 12.92, 1.055 * np.power(np.clip(row, 0, None), 1 / 2.4) - 0.055)
            row8 = np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8)[:, :, ::-1].copy()
            if label:
                col = (230, 220, 235) if kind == 'night' else (60, 30, 50)
                cv2.putText(row8, f'{lab} [{kind} bg]', (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1, cv2.LINE_AA)
            rows.append(row8)
    wmax = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in rows]
    sheet = np.concatenate(rows, 0)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cv2.imwrite(out_path, sheet)
    return out_path


def frames_of(d, picks=('first', 'mid', 'last')):
    fs = sorted(f for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []
    if not fs:
        return []
    sel = {'first': fs[0], 'mid': fs[len(fs) // 2], 'last': fs[-1]}
    return [os.path.join(d, sel[p]) for p in picks] if len(fs) >= 3 else [os.path.join(d, f) for f in fs]


def finals_sheet(out_dir=None, cell=200):
    """Contact sheets of every final asset/variant (first, middle, last frame; static: all frames)
    on a dark plum backdrop and on an ivory backdrop. Writes assets3d_icons_contact_<k>.png."""
    import cv2
    out_dir = out_dir or SELFTEST
    rows = []
    for name in ASSETS:
        base = os.path.join(OUT3D, name)
        if not os.path.isdir(base):
            continue
        for v in sorted(os.listdir(base)):
            d = os.path.join(base, v)
            fs = sorted(f for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []
            if not fs:
                continue
            groups = [[fs[0], fs[len(fs) // 2], fs[-1]]] if len(fs) > 6 else [fs[0::2], fs[1::2]] if len(fs) > 3 else [fs]
            if len(fs) == SPIN_FRAMES and v.endswith('spin'):   # 0 / 180 / 355 deg all look face-on
                groups = [[fs[0], fs[len(fs) // 8], fs[len(fs) * 5 // 24]]]
            for g in groups:
                tiles = []
                for kind in ('night', 'day'):
                    for f in g:
                        im = _read_rgba_lin(os.path.join(d, f))
                        tile = _plum_bg(cell, cell) if kind == 'night' else _bg(cell, cell, 'day')
                        im = cv2.resize(im, (cell, cell), interpolation=cv2.INTER_AREA)
                        tiles.append(im[:, :, :3] + tile * (1 - im[:, :, 3:4]))
                row = np.concatenate(tiles, 1)
                srgb = np.where(row <= 0.0031308, row * 12.92, 1.055 * np.power(np.clip(row, 0, None), 1 / 2.4) - 0.055)
                row8 = np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8)[:, :, ::-1].copy()
                meta = {}
                try:
                    meta = json.load(open(os.path.join(d, 'meta.json')))
                except Exception:
                    pass
                lab = f"{name}/{v}  {meta.get('mode', '?')} {meta.get('frames', len(fs))}f {meta.get('size', ['?'])[0]}px"
                cv2.putText(row8, lab, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (235, 225, 240), 1, cv2.LINE_AA)
                rows.append(row8)
    if not rows:
        return []
    wmax = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in rows]
    outs = []
    per = 11
    for k in range(0, len(rows), per):
        p = os.path.join(out_dir, f'assets3d_icons_contact_{k // per}.png')
        os.makedirs(out_dir, exist_ok=True)
        cv2.imwrite(p, np.concatenate(rows[k:k + per], 0))
        outs.append(p)
    return outs


def _plum_bg(h, w):
    yy = np.linspace(0, 1, h)[:, None, None]
    xx = np.linspace(-1, 1, w)[None, :, None]
    base = np.array(hexlin('NIGHT_1')) * (1 - yy) + np.array(hexlin('NIGHT_0')) * yy
    glow = np.exp(-((xx - 0.2) ** 2 + (yy - 0.35) ** 2 * 2.5) * 2.0) * 0.6
    img = base + glow * (np.array(hexlin('PLUM')) - base)
    return np.broadcast_to(img, (h, w, 3)).copy()


def selftest():
    """1) numpy: mesher sanity (closed manifold, residual) + a sheet of the 2D shape library;
    2) Blender: tiny low-sample renders of three assets into out/selftest (finals untouched);
    3) contact sheets of the finals, if rendered."""
    import cv2
    os.makedirs(SELFTEST, exist_ok=True)
    t0 = time.time()
    V, Q, N = mesh_sdf(sd3_sphere((0, 0, 0), 0.8), ((-1, -1, -1), (1, 1, 1)), 60)
    edges = {}
    for q in Q:
        for a, b in zip(q, np.roll(q, -1)):
            k = (min(a, b), max(a, b))
            edges[k] = edges.get(k, 0) + 1
    assert all(c == 2 for c in edges.values()), 'mesh is not closed/manifold'
    assert len(V) - len(edges) + len(Q) == 2, 'sphere must have Euler characteristic 2'
    r = np.linalg.norm(V, axis=1)
    assert np.abs(r - 0.8).max() < 2e-3, 'projection residual too large'
    assert (np.einsum('ij,ij->i', N, V / r[:, None]) > 0.999).all(), 'normals must point outwards'
    print(f'mesher ok ({len(V)} verts) {time.time() - t0:.1f}s')
    # 2D library sheet
    shapes = [('heart', sd_heart(2.0, convex=0.14, concave=0.16)),
              ('shield', poly_sd([shield_outline()]).rounded(0.20, 0.0)),
              ('squircle', poly_sd([squircle(0.92, 4.4)])),
              ('star', poly_sd([star_outline(0.9, 0.42)]).rounded(0.1, 0.05)),
              ('pound', pound_sd(1.8)),
              ('check', fn_sd(sd_polyline([(x * 1.8, y * 1.8) for x, y in CHECK_PTS], 0.2), (-1.2, -1.2, 1.2, 1.2), 600))]
    tiles = []
    X, Y = np.meshgrid(np.linspace(-1.15, 1.15, 220), np.linspace(1.15, -1.15, 220))
    for nm, sd in shapes:
        d = sd(X, Y)
        img = np.zeros((220, 220, 3), np.uint8)
        img[:] = (40, 12, 30)
        band = (np.abs(np.mod(d, 0.1) - 0.05) < 0.006) & (d > 0)
        img[d < 0] = (110, 0, 183)
        img[band] = (90, 60, 90)
        img[np.abs(d) < 0.01] = (245, 248, 252)
        cv2.putText(img, nm, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 230, 240), 1, cv2.LINE_AA)
        tiles.append(img)
    cv2.imwrite(os.path.join(SELFTEST, 'assets3d_icons_shapes.png'), np.concatenate(tiles, 1))
    # tiny renders (do not touch finals)
    global OUT3D
    try:
        _bpy()
        keep = OUT3D
        OUT3D = os.path.join(SELFTEST, '_assets3d_icons_tmp')
        entries = []
        for nm, v in (('heart', 'night'), ('coin_gbp', 'night'), ('check_tile', 'day')):
            spec = ASSETS[nm]
            old = spec.size
            spec.size = (256, 256)
            try:
                d = render_asset(nm, v, 'yaw', preview=False, frames=[8, 24, 40], samples=8)
            finally:
                spec.size = old
            entries.append((f'{nm}/{v} (selftest 256px 8spp)', [os.path.join(d, f'{i:04d}.png') for i in (8, 24, 40)]))
        contact_sheet(entries, os.path.join(SELFTEST, 'assets3d_icons_render.png'), cell=256)
        OUT3D = keep
        import shutil
        shutil.rmtree(os.path.join(SELFTEST, '_assets3d_icons_tmp'), ignore_errors=True)
    except ImportError:
        print('bpy not available: skipped render test')
    outs = finals_sheet()
    print('selftest ok', outs)

# ----------------------------------------------------------------------------- driver

def opts_spp_scale(name):
    """Glass needs a few more samples than candy plastic to denoise cleanly."""
    return 1.34 if name in ('shield_check', 'chat_bubble', 'orbs') else 1.0


def _yaw_of(i, n):
    return YAW_RANGE[0] + (YAW_RANGE[1] - YAW_RANGE[0]) * i / max(n - 1, 1)


def render_asset(name, variant, mode=None, preview=False, frames=None, samples=None):
    """Build + render one asset/variant/mode. Returns the output directory."""
    _bpy()
    spec = ASSETS[name]
    mode = mode or spec.modes[0]
    size = spec.spin_size if mode == 'spin' else spec.size
    if preview:
        size = (size[0] // 2, size[1] // 2)
    spp = samples or (16 if preview else int(SAMPLES * opts_spp_scale(name)))
    sc = reset(size, spp, variant)
    root = empty('root')
    q = 0.6 if preview else 1.0
    opts = spec.builder(root, variant, q) or {}
    world(variant, metal=opts.get('metal', False))
    rig(variant, opts.get('rig_scale', 1.0), opts.get('key', 1.0), metal=opts.get('metal', False),
        soft_top=opts.get('soft_top', False))
    if opts.get('glass'):
        sc.cycles.max_bounces = 10
        sc.cycles.transmission_bounces = 10
        sc.cycles.glossy_bounces = 4
    axis = opts.get('axis', 'z')
    folder = variant if mode == spec.modes[0] else f'{variant}_{mode}'
    outdir = os.path.join(PREVIEW3D if preview else OUT3D, name, folder)
    if mode == 'yaw':
        n = YAW_FRAMES
        frame_camera(root, np.linspace(YAW_RANGE[0], YAW_RANGE[1], 9), axis, aspect=size[0] / size[1])

        def upd(i, nn):
            root.rotation_euler = (0, 0, math.radians(_yaw_of(i, nn)))
            if opts.get('update'):
                opts['update'](i, nn)
    elif mode == 'spin':
        n = SPIN_FRAMES
        frame_camera(root, np.arange(0, 360, 10), axis, aspect=size[0] / size[1])

        def upd(i, nn):
            a = math.radians(360.0 * i / nn)
            root.rotation_euler = (0, 0, a) if axis == 'z' else (a, 0, 0)
        if opts.get('sym180') and frames is None and not preview:
            frames = list(range(n // 2))       # second half is identical: copied after rendering
    elif mode == 'static':
        objs = opts['objects']
        n = len(objs)
        frame_camera(root, [0.0], axis, aspect=size[0] / size[1], target=(0, 0, 0))

        def upd(i, nn):
            for k, o in enumerate(objs):
                for ob in [o] + list(o.children_recursive):
                    ob.hide_render = (k != i)
    else:
        n = opts['frames']
        frame_camera(root, opts.get('frame_angles', [0.0]), axis, aspect=size[0] / size[1])
        upd = opts['update']
    if preview and frames is None:
        frames = sorted({0, n // 2, n - 1})
    t0 = time.time()
    render_frames(outdir, n, upd, frames, prefix=f'{name}/{folder}')
    if mode == 'spin' and opts.get('sym180') and frames == list(range(n // 2)):
        import shutil
        for i in range(n // 2):
            shutil.copyfile(os.path.join(outdir, f'{i:04d}.png'), os.path.join(outdir, f'{i + n // 2:04d}.png'))
        frames = None
    pivot = project_px(tuple(root.matrix_world.translation))
    meta = dict(name=name, variant=variant, mode=mode, frames=n,
                fps_hint=opts.get('fps_hint', 30), size=list(size), loop=mode in ('spin', 'anim') and opts.get('loop', True),
                notes=opts.get('notes', spec.notes), pivot=[round(pivot[0], 1), round(pivot[1], 1)], axis=axis)
    if mode == 'yaw':
        meta['yaw_range'] = list(YAW_RANGE)
        meta['loop'] = False
        meta['notes'] += '; yaw sweep -40..+40 deg, ping-pong for floating rotation'
    if mode == 'spin':
        meta['notes'] += f'; full 360 deg turn about {axis}, frame i = {360 / n:g}*i deg'
    if 'labels' in opts:
        meta['labels'] = opts['labels']
    if frames is None or len(frames) >= n:
        write_meta(outdir, **meta)
    else:
        write_meta(outdir, **dict(meta, partial=sorted(frames)))
    print(f'done {name}/{folder} in {time.time() - t0:.0f}s -> {outdir}', flush=True)
    return outdir


def _parse(argv):
    names, opts = [], {'preview': False, 'variant': None, 'frames': None, 'samples': None, 'mode': None}
    it = iter(argv)
    for a in it:
        if a == '--preview':
            opts['preview'] = True
        elif a == '--variant':
            opts['variant'] = next(it)
        elif a == '--mode':
            opts['mode'] = next(it)
        elif a == '--frames':
            opts['frames'] = [int(x) for x in next(it).split(',')]
        elif a == '--samples':
            opts['samples'] = int(next(it))
        elif a in ('--yaw-frames', '--spin-frames'):      # frame-count overrides (defaults 49 / 72)
            global YAW_FRAMES, SPIN_FRAMES
            if a == '--yaw-frames':
                YAW_FRAMES = int(next(it))
            else:
                SPIN_FRAMES = int(next(it))
        else:
            names.append(a)
    return names, opts


def main(argv):
    names, o = _parse(argv)
    if names == ['selftest']:
        return selftest()
    if names == ['sheet']:
        print(finals_sheet())
        return
    if names == ['all']:
        names = list(ASSETS)
    for name in names:
        spec = ASSETS[name]
        for v in ([o['variant']] if o['variant'] else spec.variants):
            if v not in spec.variants:
                continue
            for md in ([o['mode']] if o['mode'] else spec.modes):
                render_asset(name, v, md, o['preview'], o['frames'], o['samples'])


if __name__ == '__main__':
    main(sys.argv[1:])
