"""assets3d_hero.py - hero 3D assets for the Organic Fostering reels (Blender/Cycles, bpy as a module).

Renders premium glossy "SaaS 3D icon" hero objects as transparent RGBA PNG sequences that the
compositor loads through ``sprites3d.Asset3D`` (same folder/meta layout as assets3d_icons.py, same
lighting family: big warm key top-left-front, soft front-right fill, strong rims; 'night' = HOT_PINK
rim back-right + ORANGE kicker back-left over a dark plum world with two coloured soft-box reflections,
'day' = warm PEACH/white rims over a bright ivory world).

CLI
---
    python3 assets3d_hero.py <name> [<name> ...] [--preview] [--variant night|day] [--mode yaw|anim|spin|sway|glow]
                             [--frames 0,30,59] [--samples N]
    python3 assets3d_hero.py all [--preview]      # every asset / variant / mode (priority order)
    python3 assets3d_hero.py sheet                # contact sheets of the finals -> out/selftest/assets3d_hero_contact_*.png
    python3 assets3d_hero.py previewsheet         # contact sheet of the --preview renders
    python3 assets3d_hero.py selftest             # numpy mesher checks + tiny renders -> out/selftest/assets3d_hero_*.png

    --preview   12 spp, half resolution, first/mid/last frames only, written to
                workspace3/out/preview3d/<name>/<folder>/ (never touches the finals)
    env HERO_SAMPLES (final spp, default 16: adaptive sampling + OpenImageDenoise with albedo/normal guides;
    the render-time budget of the shared 4-core box rules out 64+), HERO_THREADS (default 2),
    SKIP_EXISTING=1 resumes an interrupted sequence.

Assets (folder under workspace3/assets3d/<name>/, mode, frames, size)
---------------------------------------------------------------------
    logo_mark3d   night, day          yaw  49  1200x1000  layered extrusion of the real OF emblem (vectorised
                  night_anim, day_anim anim 60            from brand/logo_mark.png): MAGENTA ring + F deepest,
                                                          ORANGE children + heart proud, LEAF leaves raised and
                                                          tilted. anim = swing-in yaw -75 -> 0 with overshoot
                                                          settle and a specular sweep; its last frame == yaw 0.
    question      night               yaw  49  1000x1000  Nunito-Black "?" (text object, extrude + bevel),
                  night_spin          spin 72             MAGENTA->ORANGE 35-degree gradient candy.
    pound_glyph   night               yaw  49  1000x1000  Nunito-Black "£" in polished AMBER/ORANGE gold.
    sprout        day                 anim 120 900x1200   grows from the soil point: S-curve stem, 2 then 4
                                                          leaves unfold; the top pair ends echoing the logo leaves.
                  day_sway            anim 48 (loop)      idle sway; frame 0 == the grow anim's last frame.
    leaf          day, night          spin 48  600x600    one glossy logo leaf (LEAF + LEAF_HI vein) tumbling on
                                                          two axes (falling-leaf particles); loops.
    seed          day                 static 1 600x600    warm translucent PEACH/AMBER orb with an inner glow.
                  day_glow            anim 24 (loop)      the same seed with a pulsing inner glow.
    puzzle_pair   day                 yaw  49  1000x800   the connected MAGENTA + ORANGE jigsaw pair.
                  day_anim            anim 48             the two pieces slide together and click (overshoot).
    blocks        day                 yaw  49  800x800    three stacked rounded toy blocks (MAGENTA heart,
                                                          ORANGE star, LEAF leaf; raised ivory symbols).

Load them with sprites3d:
    from sprites3d import Asset3D
    logo_in = Asset3D('logo_mark3d', 'night', mode='anim')   # -> folder night_anim
    logo    = Asset3D('logo_mark3d', 'night')                # yaw sweep; at_yaw(0) == last anim frame
    q_spin  = Asset3D('question', 'night', mode='spin')      # -> night_spin
    grow    = Asset3D('sprout', 'day')                       # anim 120; at_time(t, loop=False)
    sway    = Asset3D('sprout', 'day', mode='sway')          # -> day_sway (loops)
    click   = Asset3D('puzzle_pair', 'day', mode='anim')     # -> day_anim

Output (shared 3D asset spec)
-----------------------------
    workspace3/assets3d/<name>/<folder>/0000.png ...   RGBA 8-bit, straight alpha, sRGB ('Standard' view)
    workspace3/assets3d/<name>/<folder>/meta.json
        {name, variant, mode: 'yaw'|'spin'|'anim'|'static', frames, fps_hint, yaw_range (yaw), size: [w, h],
         anchor: [x, y] (visual centre px), loop, notes, bbox (union alpha bbox), ground_y (lowest opaque row),
         pivot (projected rotation axis / sprout soil point px), axis, samples, preview,
         features: {name: [x, y] px} projected points of interest (yaw: at yaw 0; anim/spin: last frame),
         features_per_frame: {frame: {name: [x, y]}} (anim/spin only)}
        logo_mark3d features: heart, girl, boy (front-face centres), leaf_l, leaf_r, leaf_top (blade middles)
        sprout features: base (soil/seed point), tip, leaf_low_l, leaf_low_r, leaf_top_l, leaf_top_r (blade
                         centres) - e.g. to fly the sprout's top leaves into the logo's leaf_l / leaf_r.
        puzzle_pair/day_anim: click_frame (25).
    yaw: frame i shows yaw = -40 + 80 * i / 48 degrees (positive yaw turns the front to screen-right).
    spin: frame i = 360 * i / n degrees (loops).

Python API (the numpy parts import without Blender; nothing runs at import time)
------------------------------------------------------------------------------
    import assets3d_hero as H
    H.ASSETS['logo_mark3d']                 # -> dict(variants, size, modes, notes, build)
    H.hexlin('#B7006E')                     # linear RGB tuple
    sd = H.SDF2.from_mask(mask, px=0.002)   # 2D signed distance image (world units, negative inside)
    f = H.Slab(sd, h=0.05, r=0.02)          # rounded extrusion (bevel radius r, optional dome / groove)
    V, Q, N = H.mesh_field(f, step=0.004)   # surface nets + Newton projection; analytic normals
    pieces = H.logo_pieces()                # per-colour components of the logo mark (masks, colours, px->world)
    H.render_asset('leaf', 'day', preview=True)    # needs bpy
    H.contact_sheets()                      # finals -> out/selftest/assets3d_hero_contact_*.png
"""
import os
import sys
import json
import math
import time
import hashlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
WS = os.environ.get('FOSTER_WS', os.path.join(REPO, 'workspace3'))
OUT3D = os.path.join(WS, 'assets3d')
PREVIEW3D = os.path.join(WS, 'out', 'preview3d')
SELFTEST = os.path.join(WS, 'out', 'selftest')
CACHE = os.path.join(WS, 'out', 'cache3d_hero')
FONTS = os.path.join(WS, 'fonts')
BRANDDIR = os.path.join(WS, 'brand')

# ============================================================================= colour

BRAND = {
    'MAGENTA': '#B7006E', 'HOT_PINK': '#FF3D9A', 'ORANGE': '#FF6411', 'AMBER': '#FFB15C',
    'LEAF': '#64A60B', 'LEAF_HI': '#A8E04A', 'PLUM': '#5B174F', 'INK': '#321F35',
    'NIGHT_0': '#0B0310', 'NIGHT_1': '#1C0822', 'IVORY': '#FCF8F5', 'PEACH': '#FFD4BA',
    'LAVENDER': '#F6EAF3',
    # exact logo inks (the 3D logo uses these so it matches the 2D mark)
    'LOGO_MAGENTA': '#A6055E', 'LOGO_ORANGE': '#F46308', 'LOGO_LEAF': '#64A60C',
}


def _s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexlin(h):
    """'#RRGGBB' or a BRAND token -> linear RGB tuple (tuples pass through)."""
    if not isinstance(h, str):
        return tuple(float(x) for x in h[:3])
    h = BRAND.get(h, h).lstrip('#')
    return tuple(_s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def mixlin(a, b, t):
    a, b = hexlin(a), hexlin(b)
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease_out_cubic(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out_back(t, s=1.4):
    t = min(max(t, 0.0), 1.0) - 1.0
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def spring(t, freq=1.6, damp=4.5):
    """Damped spring step response 0 -> 1 (t in seconds-ish units); overshoots once or twice."""
    if t <= 0:
        return 0.0
    w = 2 * math.pi * freq
    return 1 - math.exp(-damp * t) * (math.cos(w * t) + damp / w * math.sin(w * t))


# ============================================================================= 2D signed distance images

class SDF2:
    """A 2D signed distance image in world units (negative inside).

    Pixel (row r, col c) sits at world x = x0 + c * px, y = y0 - r * px (y up).
        sd = SDF2.from_mask(mask_bool, px=0.002, origin=(x0, y0))
        d = sd(x, y)                      # bilinear (order=1) or cubic B-spline (order=3)
    """

    def __init__(self, img, x0, y0, px):
        self.img = np.ascontiguousarray(img, np.float32)
        self.x0, self.y0, self.px = float(x0), float(y0), float(px)
        self._coef = None

    @property
    def shape(self):
        return self.img.shape

    def bounds(self):
        h, w = self.img.shape
        return (self.x0, self.y0 - (h - 1) * self.px, self.x0 + (w - 1) * self.px, self.y0)

    def inside_bounds(self, pad=0.0):
        """Tight (x0, y0, x1, y1) bounds of the inside region (+ pad)."""
        ys, xs = np.nonzero(self.img < 0)
        return (self.x0 + xs.min() * self.px - pad, self.y0 - ys.max() * self.px - pad,
                self.x0 + xs.max() * self.px + pad, self.y0 - ys.min() * self.px + pad)

    @classmethod
    def from_mask(cls, mask, px, origin=(0.0, 0.0), up=2, blur=0.8, pad=24):
        """mask: (h, w) bool or float coverage in [0, 1] (anti-aliased edges are honoured).
        px: world size of one mask pixel; origin: world coords of mask pixel (0, 0).
        The mask is upsampled `up` x, re-thresholded and distance transformed (exact L2), then lightly
        blurred so gradients (normals) are smooth."""
        import cv2
        m = np.asarray(mask, np.float32)
        m = np.pad(m, pad)
        if up > 1:
            m = cv2.resize(m, (m.shape[1] * up, m.shape[0] * up), interpolation=cv2.INTER_LINEAR)
            m = cv2.GaussianBlur(m, (0, 0), 0.35 * up)
        inside = (m >= 0.5).astype(np.uint8)
        din = cv2.distanceTransform(inside, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        dout = cv2.distanceTransform(1 - inside, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        # sub-pixel edge from coverage: within one pixel of the boundary use (0.5 - m)
        sd = np.where(inside > 0, -din + 0.5, dout - 0.5)
        edge = np.abs(sd) < 1.0
        sd[edge] = (0.5 - m[edge]) * 1.0
        if blur:
            sd = cv2.GaussianBlur(sd, (0, 0), blur * up)
        pxu = px / up
        x0 = origin[0] - pad * px + 0.5 * pxu - 0.5 * px
        y0 = origin[1] + pad * px - 0.5 * pxu + 0.5 * px
        return cls(sd * pxu, x0, y0, pxu)

    @classmethod
    def from_polys(cls, polys, px, pad_world=0.2, **kw):
        """Closed polygons [(N, 2) world coords, ...] filled with even-odd rule -> SDF2."""
        import cv2
        allp = np.concatenate([np.asarray(p, float) for p in polys])
        x0, y0 = allp.min(0) - pad_world
        x1, y1 = allp.max(0) + pad_world
        w = int(math.ceil((x1 - x0) / px)) + 1
        h = int(math.ceil((y1 - y0) / px)) + 1
        img = np.zeros((h, w), np.uint8)
        sh = 4
        pts = [np.round(np.stack([(np.asarray(p)[:, 0] - x0) / px, (y1 - np.asarray(p)[:, 1]) / px], 1)
                        * (1 << sh)).astype(np.int32) for p in polys]
        cv2.fillPoly(img, pts, 255, cv2.LINE_AA, shift=sh)
        return cls.from_mask(img.astype(np.float32) / 255.0, px, origin=(x0, y1), pad=4, **kw)

    def _coefs(self):
        if self._coef is None:
            from scipy.ndimage import spline_filter
            self._coef = spline_filter(self.img.astype(np.float64), order=3, mode='nearest')
        return self._coef

    def __call__(self, x, y, order=3):
        from scipy.ndimage import map_coordinates
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        c = (x - self.x0) / self.px
        r = (self.y0 - y) / self.px
        shp = np.broadcast(c, r).shape
        c = np.broadcast_to(c, shp).ravel()
        r = np.broadcast_to(r, shp).ravel()
        if order == 3:
            v = map_coordinates(self._coefs(), [r, c], order=3, mode='nearest', prefilter=False)
        else:
            v = map_coordinates(self.img, [r, c], order=1, mode='nearest')
        # outside the image: keep growing with distance so the field stays sane
        h, w = self.img.shape
        ox = np.maximum(np.maximum(-c, c - (w - 1)), 0) * self.px
        oy = np.maximum(np.maximum(-r, r - (h - 1)), 0) * self.px
        v = v + np.hypot(ox, oy)
        return v.reshape(shp)

    def grid(self, xs, ys):
        """Bilinear samples on a grid: returns (len(xs), len(ys)) array (x-major)."""
        X, Y = np.meshgrid(xs, ys, indexing='ij')
        return self(X, Y, order=1)

    def union(self, other):
        """Pointwise min with another SDF2 resampled onto this grid."""
        h, w = self.img.shape
        xs = self.x0 + np.arange(w) * self.px
        ys = self.y0 - np.arange(h) * self.px
        o = other.grid(xs, ys).T
        return SDF2(np.minimum(self.img, o), self.x0, self.y0, self.px)

    def offset(self, r):
        return SDF2(self.img - r, self.x0, self.y0, self.px)


def text_mask(ch, font='Nunito-Black.ttf', size=900):
    """Render one glyph to a float coverage mask (PIL). Returns (mask, (ox, oy)) where (ox, oy) is the
    pen origin in mask px (baseline-left)."""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(os.path.join(FONTS, font), size)
    l, t, r, b = f.getbbox(ch)
    pad = size // 6
    im = Image.new('L', (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), ch, font=f, fill=255)
    return np.asarray(im, np.float32) / 255.0, (pad - l, pad - t)


# ============================================================================= 3D fields

class Slab:
    """Rounded extrusion of a 2D SDF along local z ("icon frame": x right, y up, z towards the viewer).

        f = Slab(sd2, h=0.05, r=0.02, rz=None, zc=0.0, dome=0.0, dome_w=0.1, groove=None)

    h: half thickness of the flat part, r: bevel radius in the plane, rz: bevel height (defaults to r;
    rz > r gives a taller elliptical bevel), dome: extra height that rises (smoothly, zero slope at the
    bevel) to the middle of wide areas, groove=(sd_line, depth, width): a soft engraved channel in both
    faces where sd_line(x, y) ~ 0 (used for leaf veins). Values are not exact distances but the zero
    set and the gradient direction are what the mesher needs."""

    def __init__(self, sd2, h, r, rz=None, zc=0.0, dome=0.0, dome_w=0.1, groove=None, back=None, dome_sd=None):
        self.sd2, self.h, self.r = sd2, float(h), float(r)
        self.dome_sd = dome_sd      # optional smoother SDF2 for the dome (no crease along the medial axis)
        self.rz = float(rz if rz is not None else r)
        self.zc, self.dome, self.dome_w = float(zc), float(dome), float(dome_w)
        self.groove = groove
        self.back = back            # optional different half-thickness for the back face (None = same)

    def bounds(self, pad=None):
        pad = pad if pad is not None else max(self.r, 0.01) * 0.5 + 0.01
        x0, y0, x1, y1 = self.sd2.inside_bounds(pad)
        hz = self.h + self.dome + pad
        hb = (self.back if self.back is not None else self.h) + self.dome + pad
        return (x0, y0, self.zc - hb), (x1, y1, self.zc + hz)

    def _H(self, d, x=None, y=None, order=3):
        H = np.full(np.shape(d), self.h)
        if self.dome:
            dd = d if (self.dome_sd is None or x is None) else self.dome_sd(x, y, order=order)
            u = np.maximum(-(dd + self.r), 0.0) / self.dome_w
            H = H + self.dome * (u * u / (1.0 + u * u))
        if self.groove is not None and x is not None:
            gsd, depth, width = self.groove
            g = gsd(x, y)
            H = H - depth * np.exp(-(g / width) ** 2) * smoothstep(0.0, self.r * 1.2, -d)
        return H

    def _combine(self, d, z, H, Hb):
        k = self.r / self.rz
        dz = z - self.zc
        Hs = np.where(dz >= 0, H, Hb)
        qx = d + self.r
        qz = (np.abs(dz) - Hs) * k + self.r
        return np.hypot(np.maximum(qx, 0), np.maximum(qz, 0)) + np.minimum(np.maximum(qx, qz), 0) - self.r

    def value(self, P):
        x, y, z = P[..., 0], P[..., 1], P[..., 2]
        d = self.sd2(x, y, order=3)
        H = self._H(d, x, y)
        Hb = H if self.back is None else H - self.h + self.back
        return self._combine(d, z, H, Hb)

    def grid(self, xs, ys, zs):
        d = self.sd2.grid(xs, ys)
        X, Y = np.meshgrid(xs, ys, indexing='ij')
        H = self._H(d, X, Y, order=1)
        Hb = H if self.back is None else H - self.h + self.back
        out = np.empty((len(xs), len(ys), len(zs)), np.float32)
        for k, z in enumerate(zs):
            out[:, :, k] = self._combine(d, z, H, Hb)
        return out


class FieldFn:
    """Generic implicit from a vectorised callable f(P[..., 3]) -> values, with explicit bounds."""

    def __init__(self, fn, lo, hi):
        self.fn, self.lo, self.hi = fn, tuple(lo), tuple(hi)

    def bounds(self, pad=None):
        return self.lo, self.hi

    def value(self, P):
        return self.fn(P)

    def grid(self, xs, ys, zs):
        X, Y = np.meshgrid(xs, ys, indexing='ij')
        out = np.empty((len(xs), len(ys), len(zs)), np.float32)
        for k, z in enumerate(zs):
            P = np.stack([X, Y, np.full_like(X, z)], -1)
            out[:, :, k] = self.fn(P)
        return out


def sd3_round_box(P, half, r):
    q = np.abs(P) - (np.asarray(half) - r)
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(q.max(-1), 0) - r


def sd3_ellipsoid(P, radii):
    """Approximate ellipsoid distance (Inigo Quilez' bound)."""
    R = np.asarray(radii, float)
    k0 = np.linalg.norm(P / R, axis=-1)
    k1 = np.linalg.norm(P / (R * R), axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


# ============================================================================= surface nets mesher

_CORNERS = np.array([(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)])
_EDGES = [(a, b) for a in range(8) for b in range(a + 1, 8) if np.abs(_CORNERS[a] - _CORNERS[b]).sum() == 1]


def surface_nets(vol, origin, step):
    """Naive surface nets on a sampled field (negative inside). Returns (V (N, 3), Q (M, 4)) with quads
    wound counter-clockwise seen from outside."""
    nx, ny, nz = vol.shape
    s = vol < 0
    cs = (nx - 1, ny - 1, nz - 1)
    anyin = np.zeros(cs, bool)
    allin = np.ones(cs, bool)
    for (i, j, k) in _CORNERS:
        v = s[i:nx - 1 + i, j:ny - 1 + j, k:nz - 1 + k]
        anyin |= v
        allin &= v
    act = anyin & ~allin
    del anyin, allin
    cid = np.flatnonzero(act)
    del act
    ci, cj, ck = np.unravel_index(cid, cs)
    vals = np.stack([vol[ci + i, cj + j, ck + k] for (i, j, k) in _CORNERS], 1).astype(np.float64)
    acc = np.zeros((len(cid), 3))
    cnt = np.zeros(len(cid))
    for a, b in _EDGES:
        va, vb = vals[:, a], vals[:, b]
        m = (va < 0) != (vb < 0)
        t = va[m] / (va[m] - vb[m])
        acc[m] += _CORNERS[a] + t[:, None] * (_CORNERS[b] - _CORNERS[a])
        cnt[m] += 1
    V = (np.stack([ci, cj, ck], 1) + acc / np.maximum(cnt, 1)[:, None]) * step + np.asarray(origin, float)
    quads = []
    for ax in range(3):
        sl0 = [slice(None)] * 3
        sl1 = [slice(None)] * 3
        sl0[ax] = slice(0, -1)
        sl1[ax] = slice(1, None)
        ch = s[tuple(sl0)] != s[tuple(sl1)]
        idx = list(np.nonzero(ch))
        ins = s[tuple(sl0)][tuple(idx)]
        o1, o2 = [a for a in range(3) if a != ax]
        ok = (idx[o1] >= 1) & (idx[o1] < cs[o1]) & (idx[o2] >= 1) & (idx[o2] < cs[o2])
        idx = [a[ok] for a in idx]
        ins = ins[ok]
        cyc = []
        for d1, d2 in ((1, 1), (0, 1), (0, 0), (1, 0)):
            c = [a.copy() for a in idx]
            c[o1] -= d1
            c[o2] -= d2
            lin = np.ravel_multi_index(c, cs)
            cyc.append(np.searchsorted(cid, lin))
        Qa = np.stack(cyc, 1)
        # CCW order in the (o1, o2) plane gives a normal along +ax when (o1, o2, ax) is right-handed
        right = (o1, o2, ax) in ((0, 1, 2), (1, 2, 0), (2, 0, 1))
        flip = ins != right
        Qa[flip] = Qa[flip][:, ::-1]
        quads.append(Qa)
    Q = np.concatenate(quads).astype(np.int64)
    return V, Q


def _grad(field, P, h):
    G = np.empty_like(P)
    for a in range(3):
        e = np.zeros(3)
        e[a] = h
        G[:, a] = (field.value(P + e) - field.value(P - e)) / (2 * h)
    return G


def mesh_field(field, step, iters=3, cache_key=None, verbose=True):
    """Polygonise a field (Slab / FieldFn) with surface nets at voxel `step`, Newton-project the
    vertices onto the zero set and return (V, Q, N) with analytic (gradient) normals.
    cache_key: str -> results cached as .npz under out/cache3d_hero/."""
    if cache_key:
        os.makedirs(CACHE, exist_ok=True)
        cp = os.path.join(CACHE, hashlib.md5(cache_key.encode()).hexdigest()[:16] + '.npz')
        if os.path.exists(cp):
            z = np.load(cp)
            return z['V'], z['Q'], z['N']
    t0 = time.time()
    lo, hi = field.bounds()
    lo = np.asarray(lo, float) - 2 * step
    hi = np.asarray(hi, float) + 2 * step
    n = np.ceil((hi - lo) / step).astype(int) + 1
    xs, ys, zs = (lo[a] + np.arange(n[a]) * step for a in range(3))
    vol = field.grid(xs, ys, zs)
    V, Q = surface_nets(vol, lo, step)
    del vol
    for _ in range(iters):
        f = field.value(V)
        g = _grad(field, V, step * 0.3)
        g2 = np.maximum((g * g).sum(1), 1e-12)
        dv = -(f / g2)[:, None] * g
        ln = np.linalg.norm(dv, axis=1)
        lim = step * 0.75
        dv *= np.minimum(1.0, lim / np.maximum(ln, 1e-12))[:, None]
        V = V + dv
    g = _grad(field, V, step * 0.3)
    N = g / np.maximum(np.linalg.norm(g, axis=1), 1e-12)[:, None]
    if verbose:
        print(f'    mesh: grid {tuple(n)} -> {len(V)} verts {len(Q)} quads in {time.time() - t0:.1f}s', flush=True)
    if cache_key:
        np.savez(cp, V=V.astype(np.float32), Q=Q.astype(np.int32), N=N.astype(np.float32))
    return V, Q, N


# ============================================================================= the logo mark, vectorised

LOGO_W = 2.4          # world width of the logo mark (1746 px)


def logo_pieces():
    """Split brand/logo_mark.png into per-colour connected components.

    Returns dict with 'px' (world size of one source px), 'center' (source px of the world origin) and
    'parts': list of dicts {name, kind: ring|child|heart|leaf, color (logo hex), mask (full-size float
    coverage), bbox (x, y, w, h px), centroid (px), attach (px, leaves: stem point touching the ring)}."""
    import cv2
    im = cv2.imread(os.path.join(BRANDDIR, 'logo_mark.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
    a = im[:, :, 3] / 255.0
    rgb = im[:, :, 2::-1]
    inks = {'ring': '#A6055E', 'child': '#F46308', 'leaf': '#64A60C'}
    refs = np.stack([np.linalg.norm(rgb - np.array([int(inks[k][i:i + 2], 16) for i in (1, 3, 5)]), axis=2)
                     for k in inks], 0)
    lab = refs.argmin(0)
    H, W = a.shape
    px = LOGO_W / W
    ys, xs = np.nonzero(a > 0.5)
    center = ((xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0)
    ring_all = ((lab == 0) & (a > 0.5)).astype(np.uint8)
    parts = []
    for k, kind in enumerate(inks):
        cov = np.where(lab == k, a, 0.0).astype(np.float32)
        hard = (cov > 0.5).astype(np.uint8)
        n, cc, st, cen = cv2.connectedComponentsWithStats(hard, 8)
        comps = [i for i in range(1, n) if st[i, 4] > 2000]
        for i in comps:
            reg = cv2.dilate((cc == i).astype(np.uint8), np.ones((5, 5), np.uint8))
            m = cov * reg
            if kind == 'leaf':
                # fill the white vein cut so the leaf is one solid blade (the vein comes back as a groove):
                # blade = leaf without its thin stem; everything inside the blade's convex hull that is not
                # leaf is the vein crescent (+ tiny edge slivers, filled too: leaf blades are convex)
                hard_i = (m > 0.5).astype(np.uint8)
                blade = cv2.morphologyEx(hard_i, cv2.MORPH_OPEN,
                                         cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
                cnts, _ = cv2.findContours(blade, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                cnts = [max(cnts, key=cv2.contourArea)]
                hull = np.zeros_like(hard_i)
                cv2.fillPoly(hull, [cv2.convexHull(cnts[0])], 1)
                fill = (hull > 0) & (hard_i == 0)
                n2, cc2, st2, _ = cv2.connectedComponentsWithStats(fill.astype(np.uint8), 8)
                vein = np.zeros_like(fill)
                if n2 > 1:
                    j2 = 1 + int(np.argmax(st2[1:, 4]))
                    vein = cc2 == j2
                solid = (hard_i > 0) | fill
                m = np.clip(np.maximum(m, fill.astype(np.float32)), 0, 1)
                d_ring = cv2.distanceTransform(1 - ring_all, cv2.DIST_L2, 5)
                yy, xx = np.nonzero(solid)
                j = np.argmin(d_ring[yy, xx])
                attach = (float(xx[j]), float(yy[j]))
                name = {0: 'leaf_top', 1: 'leaf_r', 2: 'leaf_l'}[len([p for p in parts if p['kind'] == 'leaf'])]
            else:
                vein = None
                attach = None
                if kind == 'ring':
                    name = 'ring_o' if cen[i][0] < 900 else 'ring_f'
                else:
                    x, y, w, h = st[i, :4]
                    name = 'heart' if h < 250 else ('girl' if cen[i][0] < 600 else 'boy')
            x, y, w, h = [int(v) for v in st[i, :4]]
            kind2 = 'heart' if (kind == 'child' and name == 'heart') else kind
            parts.append(dict(name=name, kind=kind2, color=inks[kind], mask=m, bbox=(x, y, w, h),
                              centroid=(float(cen[i][0]), float(cen[i][1])), attach=attach, vein=vein))
    # stable names for leaves by position
    leaves = [p for p in parts if p['kind'] == 'leaf']
    for p in leaves:
        cx, cy = p['centroid']
        p['name'] = 'leaf_top' if cy < 400 else ('leaf_l' if cx < 600 else 'leaf_r')
    return dict(px=px, center=center, parts=parts, size=(W, H))


def px_to_world(pt, L):
    return ((pt[0] - L['center'][0]) * L['px'], (L['center'][1] - pt[1]) * L['px'])


def part_sdf(p, L, crop_pad=30, up=2, blur=0.8):
    """SDF2 (world units, logo frame) of one logo part, cropped to its bbox."""
    x, y, w, h = p['bbox']
    H, W = p['mask'].shape
    x0, y0 = max(0, x - crop_pad), max(0, y - crop_pad)
    x1, y1 = min(W, x + w + crop_pad), min(H, y + h + crop_pad)
    m = p['mask'][y0:y1, x0:x1]
    ox, oy = px_to_world((x0, y0), L)
    return SDF2.from_mask(m, L['px'], origin=(ox, oy), up=up, blur=blur)


def vein_sdf(p, L, crop_pad=30):
    """Distance (world units, unsigned-ish, ~0 on the vein centre line) to a leaf's vein cut."""
    import cv2
    x, y, w, h = p['bbox']
    H, W = p['mask'].shape
    x0, y0 = max(0, x - crop_pad), max(0, y - crop_pad)
    x1, y1 = min(W, x + w + crop_pad), min(H, y + h + crop_pad)
    v = p['vein'][y0:y1, x0:x1].astype(np.uint8)
    # thin the cut to its centre line, then distance to it
    sk = v.copy()
    try:
        sk = cv2.ximgproc.thinning(v * 255) > 0
    except Exception:
        er = v.copy()
        while True:
            e2 = cv2.erode(er, cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)))
            if e2.sum() < 0.35 * er.sum() or e2.sum() == 0:
                break
            er = e2
        sk = er > 0
    d = cv2.distanceTransform((~sk).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    d = cv2.GaussianBlur(d, (0, 0), 1.0)
    ox, oy = px_to_world((x0, y0), L)
    return SDF2(d * L['px'], ox + 0.0, oy, L['px'])


# ============================================================================= Blender side
# bpy is imported lazily so everything above stays importable (and testable) without Blender.

bpy = None
Vector = None
Matrix = None

SAMPLES = int(os.environ.get('HERO_SAMPLES', '16'))
THREADS = int(os.environ.get('HERO_THREADS', '2'))
PREVIEW_SAMPLES = 12
LENS = 80.0
ELEV_DEG = 5.0
FILL = 0.80
YAW_RANGE = (-40.0, 40.0)
YAW_FRAMES = 49
EXPOSURE = {'night': 0.0, 'day': 0.0}


def _bpy():
    global bpy, Vector, Matrix
    if bpy is None:
        import bpy as _b
        from mathutils import Vector as _V, Matrix as _M
        bpy, Vector, Matrix = _b, _V, _M
    return bpy


def reset(res=(720, 720), samples=None, variant='night'):
    """Empty Cycles CPU scene: transparent film, Standard view, OIDN, fixed seed (no denoiser boil)."""
    _bpy()
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    sc.cycles.samples = samples or SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.04
    sc.cycles.adaptive_min_samples = 0
    sc.cycles.seed = 11
    sc.cycles.use_animated_seed = False
    sc.cycles.use_light_tree = False
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    sc.cycles.denoising_prefilter = 'FAST'
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 8
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.volume_bounces = 0
    sc.cycles.sample_clamp_indirect = 8.0
    sc.cycles.blur_glossy = 0.5
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
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    return m, nt.nodes['Principled BSDF'], nt


def _col4(c):
    return tuple(hexlin(c)) + (1.0,)


def _objcoord_axis(nt, axis_vec):
    """Shader nodes: dot(object coords, axis_vec) -> socket."""
    tc = nt.nodes.new('ShaderNodeTexCoord')
    dot = nt.nodes.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = axis_vec
    nt.links.new(tc.outputs['Object'], dot.inputs[0])
    return dot.outputs['Value']


def m_candy(name, color, rough=0.28, coat_r=0.045, sss=0.12, sss_radius=(1.0, 0.4, 0.3), sss_scale=0.04,
            grad=None, attr_mix=None, rim=None, rim_str=0.0, emit=None, emit_str=0.0, spec=0.5):
    """Glossy candy plastic: brand base colour, clear coat (weight 1), a touch of subsurface.

    grad=(color_b, axis_vec, lo, hi): base colour ramps (smoothstep) from `color` to color_b along
    dot(object coords, axis_vec) in [lo, hi] (e.g. the 35-degree MAGENTA->ORANGE brand gradient).
    attr_mix=(attr_name, color_b): mix towards color_b by a per-vertex float attribute (leaf veins).
    rim=(color): fresnel-driven emission at grazing angles ('light inside the candy')."""
    m, b, nt = _principled(name)
    col = _col4(color)
    b.inputs['Base Color'].default_value = col
    src = None
    if grad:
        cb, axis, lo, hi = grad
        v = _objcoord_axis(nt, axis)
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.interpolation_type = 'SMOOTHSTEP'
        mr.inputs['From Min'].default_value = lo
        mr.inputs['From Max'].default_value = hi
        nt.links.new(v, mr.inputs['Value'])
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.inputs['A'].default_value = col
        mix.inputs['B'].default_value = _col4(cb)
        nt.links.new(mr.outputs[0], mix.inputs['Factor'])
        src = mix.outputs['Result']
    if attr_mix:
        an, cb = attr_mix
        at = nt.nodes.new('ShaderNodeAttribute')
        at.attribute_name = an
        mix2 = nt.nodes.new('ShaderNodeMix')
        mix2.data_type = 'RGBA'
        if src is not None:
            nt.links.new(src, mix2.inputs['A'])
        else:
            mix2.inputs['A'].default_value = col
        mix2.inputs['B'].default_value = _col4(cb)
        nt.links.new(at.outputs['Fac'], mix2.inputs['Factor'])
        src = mix2.outputs['Result']
    if src is not None:
        nt.links.new(src, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Coat Roughness'].default_value = coat_r
    b.inputs['Coat IOR'].default_value = 1.5
    b.inputs['Specular IOR Level'].default_value = spec
    if sss:
        b.subsurface_method = 'BURLEY'
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = sss_radius
        b.inputs['Subsurface Scale'].default_value = sss_scale
    if rim or emit:
        try:   # the glow is for the camera only: never sample these (dense) meshes as lights
            m.cycles.emission_sampling = 'NONE'
        except Exception:
            pass
    if rim:
        lw = nt.nodes.new('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.35
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.3
        mr.inputs['From Max'].default_value = 1.0
        mr.inputs['To Max'].default_value = rim_str
        nt.links.new(lw.outputs['Facing'], mr.inputs['Value'])
        b.inputs['Emission Color'].default_value = _col4(rim)
        nt.links.new(mr.outputs['Result'], b.inputs['Emission Strength'])
    elif emit:
        b.inputs['Emission Color'].default_value = _col4(emit)
        b.inputs['Emission Strength'].default_value = emit_str
    return m


def m_gold(name, base='AMBER', edge='ORANGE', rough=0.18, coat=0.0):
    """Polished gold: metallic AMBER base with an ORANGE edge tint (Principled 'Specular Tint' = F82 tint)."""
    m, b, nt = _principled(name)
    b.inputs['Base Color'].default_value = _col4(base)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular Tint'].default_value = _col4(edge)
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.04
    return m


def m_seed(name, glow=1.0):
    """Warm translucent orb: PEACH/AMBER random-walk subsurface, glossy coat, and an inner glow (emission
    strongest where the surface faces the camera, ORANGE towards the rim) that reads as a lit core."""
    m, b, nt = _principled(name)
    b.inputs['Base Color'].default_value = _col4(mixlin('AMBER', 'ORANGE', 0.25))
    b.subsurface_method = 'RANDOM_WALK'
    b.inputs['Subsurface Weight'].default_value = 1.0
    b.inputs['Subsurface Radius'].default_value = (1.0, 0.45, 0.18)
    b.inputs['Subsurface Scale'].default_value = 0.25
    b.inputs['Roughness'].default_value = 0.3
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Coat Roughness'].default_value = 0.04
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.5
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = 0.05
    mr.inputs['From Max'].default_value = 0.9
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    nt.links.new(lw.outputs['Facing'], mr.inputs['Value'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = _col4(mixlin('ORANGE', 'MAGENTA', 0.35))
    mix.inputs['B'].default_value = _col4(mixlin('AMBER', (1.0, 0.86, 0.6), 0.25))
    nt.links.new(mr.outputs[0], mix.inputs['Factor'])
    nt.links.new(mix.outputs['Result'], b.inputs['Emission Color'])
    pw = nt.nodes.new('ShaderNodeMath')
    pw.operation = 'POWER'
    pw.inputs[1].default_value = 2.2
    nt.links.new(mr.outputs[0], pw.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 1.1 * glow
    nt.links.new(pw.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], b.inputs['Emission Strength'])
    m['glow_node'] = mul.name
    try:
        m.cycles.emission_sampling = 'NONE'
    except Exception:
        pass
    return m


# ----------------------------------------------------------------------------- lights, cards, world

def _aim(obj, target=(0, 0, 0)):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def area(name, loc, size, energy, color=(1, 1, 1), target=(0, 0, 0), shape='RECTANGLE', glossy=True,
         diffuse=True, spread=180.0):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.shape = shape
    ld.size = size[0]
    ld.size_y = size[1]
    ld.energy = energy
    ld.color = hexlin(color)
    ld.spread = math.radians(spread)
    o = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    _aim(o, target)
    o.visible_glossy = glossy
    o.visible_diffuse = diffuse
    return o


def card(name, loc, size, color, strength, target=(0, 0, 0), shape='rect', soft=0.25):
    """Emissive soft-box seen only in reflections/refractions (soft-edged highlight shapes on the coat).
    shape 'rect' fades `soft` of the way in from each edge; 'oval' is an elliptical soft spot."""
    me = bpy.data.meshes.new(name)
    w, h = size[0] / 2, size[1] / 2
    me.from_pydata([(-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    _aim(o, target)
    mat = bpy.data.materials.new(name + '_m')
    try:
        mat.use_nodes = True
    except Exception:
        pass
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
            m1 = nt.nodes.new('ShaderNodeMapRange')
            m1.interpolation_type = 'SMOOTHSTEP'
            nt.links.new(sep.outputs[ax], m1.inputs['Value'])
            m1.inputs['From Min'].default_value = 0.0
            m1.inputs['From Max'].default_value = soft
            m2 = nt.nodes.new('ShaderNodeMapRange')
            m2.interpolation_type = 'SMOOTHSTEP'
            nt.links.new(sep.outputs[ax], m2.inputs['Value'])
            m2.inputs['From Min'].default_value = 1.0
            m2.inputs['From Max'].default_value = 1.0 - soft
            mul = nt.nodes.new('ShaderNodeMath')
            mul.operation = 'MULTIPLY'
            nt.links.new(m1.outputs[0], mul.inputs[0])
            nt.links.new(m2.outputs[0], mul.inputs[1])
            if prod is None:
                prod = mul
            else:
                m3 = nt.nodes.new('ShaderNodeMath')
                m3.operation = 'MULTIPLY'
                nt.links.new(prod.outputs[0], m3.inputs[0])
                nt.links.new(mul.outputs[0], m3.inputs[1])
                prod = m3
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = _col4(color)
    e.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(prod.outputs[0], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(e.outputs[0], mix.inputs[2])
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(mix.outputs[0], out.inputs[0])
    me.materials.append(mat)
    try:
        mat.cycles.emission_sampling = 'NONE'
    except Exception:
        pass
    o.visible_camera = False
    o.visible_shadow = False
    o.visible_diffuse = False
    o.visible_volume_scatter = False
    o['strength_node'] = e.name
    return o


def card_strength(o, s):
    mat = o.data.materials[0]
    mat.node_tree.nodes[o['strength_node']].inputs['Strength'].default_value = s


def world(variant, metal=False):
    """Night: dark plum dome + HOT_PINK (back-right) and ORANGE (back-left) soft-box blobs.
    Day: bright ivory dome, warm peach / pink blobs."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W_' + variant)
    sc.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
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
        mul.inputs[0].default_value = hexlin(color)
        nt.links.new(mr.outputs[0], mul.inputs['Scale'])
        return mul

    def vgrad(c_lo, c_hi, s_lo, s_hi):
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = -0.6
        mr.inputs['From Max'].default_value = 0.9
        nt.links.new(sepz.outputs['Z'], mr.inputs['Value'])
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        nt.links.new(mr.outputs[0], mix.inputs['Factor'])
        mix.inputs['A'].default_value = tuple(x * s_lo for x in hexlin(c_lo)) + (1,)
        mix.inputs['B'].default_value = tuple(x * s_hi for x in hexlin(c_hi)) + (1,)
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


def rig(variant, scale=1.0, key=1.0, cards=1.0, metal=False, rims=1.0):
    """Key / fill / rims + reflection cards (the shared family rig). `scale` widens the rig for bigger
    objects, `key` scales key+fill energy, `cards` the reflection soft-boxes, `rims` the rim lights."""
    s = scale
    e = s * s
    warm = (1.0, 0.95, 0.89)
    k = key * (0.78 if variant == 'day' else 1.0)
    L = {}
    L['key'] = area('key', (-3.4 * s, -4.4 * s, 4.4 * s), (4.0 * s, 4.0 * s), 520 * e * k, warm, glossy=False,
                    shape='DISK')
    L['fill'] = area('fill', (4.6 * s, -4.2 * s, 0.6 * s), (3.5 * s, 3.5 * s), 110 * e * k, (1.0, 0.96, 0.95),
                     glossy=False, shape='DISK')
    L['kcard'] = card('kcard', (-3.0 * s, -4.0 * s, 4.0 * s), (3.4 * s, 2.4 * s), (1.0, 0.97, 0.93), 2.2 * cards,
                      shape='oval', soft=0.35)
    L['kstrip'] = card('kstrip', (-1.6 * s, -3.0 * s, 4.6 * s), (2.6 * s, 0.32 * s), (1.0, 1.0, 1.0), 6.0 * cards,
                       soft=0.3)
    L['frontcard'] = card('frontcard', (1.2 * s, -6.5 * s, 0.4 * s), (6.0 * s, 3.0 * s), (1.0, 0.95, 0.92),
                          0.22 * cards, shape='oval', soft=0.45)
    if metal:
        card('m_front', (0.0, -7.5 * s, -0.55 * s), (9.0 * s, 4.4 * s), (1.0, 0.90, 0.74), 1.5, shape='oval', soft=0.32)
        card('m_top', (0.0, -3.0 * s, 6.0 * s), (6.0 * s, 2.0 * s), (1.0, 0.95, 0.85), 2.4, soft=0.4)
        for i, (x, y) in enumerate(((-4.3, -6.2), (-7.0, -2.6), (4.3, -6.2), (7.0, -2.6))):
            card(f'm_glint{i}', (x * s, y * s, 0.2 * s), (0.9 * s, 6.0 * s), (1.0, 0.93, 0.80), 3.2, soft=0.3)
        card('m_low', (0.0, -5.0 * s, -3.5 * s), (6.0 * s, 1.2 * s), (1.0, 0.6, 0.3), 0.8, soft=0.4)
    if variant == 'night':
        L['rim_a'] = area('rim_pink', (4.2 * s, 3.4 * s, 1.6 * s), (1.4 * s, 4.5 * s), 1300 * e * rims,
                          mixlin('HOT_PINK', 'AMBER', 0.5) if metal else 'HOT_PINK')
        L['rim_b'] = area('rim_orange', (-4.4 * s, 3.0 * s, 0.2 * s), (1.4 * s, 4.5 * s), 1100 * e * rims, 'ORANGE')
        L['top'] = area('top', (0.4 * s, 1.8 * s, 5.2 * s), (3.0 * s, 1.2 * s), 200 * e, (1.0, 0.82, 0.86))
    else:
        L['rim_a'] = area('rim_peach', (4.2 * s, 3.4 * s, 1.6 * s), (1.4 * s, 4.5 * s), 900 * e * rims, 'PEACH')
        L['rim_b'] = area('rim_white', (-4.4 * s, 3.0 * s, 0.6 * s), (1.4 * s, 4.5 * s), 700 * e * rims,
                          (1.0, 0.95, 0.9))
        L['top'] = area('top', (0.4 * s, 1.8 * s, 5.2 * s), (3.0 * s, 1.2 * s), 200 * e, (1.0, 0.97, 0.93))
    return L


# ----------------------------------------------------------------------------- objects

def empty(name='root', parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    if parent is not None:
        o.parent = parent
    return o


def icon_to_blender(V):
    """Icon frame (x right, y up, z towards the viewer) -> Blender (X right, Z up, camera at -Y)."""
    V = np.asarray(V, np.float64)
    return np.stack([V[:, 0], -V[:, 2], V[:, 1]], 1)


def add_mesh(name, V, Q, N=None, mat=None, parent=None, icon_frame=True, attrs=None, loc=None):
    """Smooth-shaded mesh object from (V, Q[, N]). N (custom normals) optional. attrs: {name: per-vertex
    float array} stored as POINT float attributes (read in shaders by an Attribute node)."""
    V = np.asarray(V, np.float64)
    if icon_frame:
        V = icon_to_blender(V)
        if N is not None:
            N = icon_to_blender(N)
    if loc is not None:
        V = V - np.asarray(loc, float)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set('co', V.astype(np.float32).ravel())
    Q = np.asarray(Q)
    nv = Q.shape[1]
    me.loops.add(len(Q) * nv)
    me.loops.foreach_set('vertex_index', Q.astype(np.int32).ravel())
    me.polygons.add(len(Q))
    me.polygons.foreach_set('loop_start', np.arange(0, nv * len(Q), nv, dtype=np.int32))
    me.update(calc_edges=True)
    me.polygons.foreach_set('use_smooth', np.ones(len(Q), bool))
    if N is not None:
        me.normals_split_custom_set_from_vertices([tuple(n) for n in np.asarray(N, np.float32)])
    if attrs:
        for an, vals in attrs.items():
            at = me.attributes.new(an, 'FLOAT', 'POINT')
            at.data.foreach_set('value', np.asarray(vals, np.float32))
    if mat is not None:
        me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    if loc is not None:
        o.location = tuple(float(x) for x in loc)
    return o


def field_object(name, field, step, mat, parent=None, cache_key=None, attrs_fn=None, pivot=None):
    """Mesh a field (icon frame) and add it. pivot: icon-frame point that becomes the object origin."""
    V, Q, N = mesh_field(field, step, cache_key=cache_key)
    attrs = attrs_fn(V) if attrs_fn else None
    loc = None
    if pivot is not None:
        loc = icon_to_blender(np.asarray([pivot], float))[0]
    return add_mesh(name, V, Q, N, mat, parent=parent, attrs=attrs, loc=loc)


def text_object(name, ch, size=2.0, extrude=0.12, bevel=0.06, bevel_res=8, offset=None, font='Nunito-Black.ttf',
                smooth_angle=50.0):
    """Blender text object -> mesh (extrude + round bevel), centred on its bounds, smooth by angle."""
    cu = bpy.data.curves.new(name + '_cu', 'FONT')
    cu.body = ch
    cu.font = bpy.data.fonts.load(os.path.join(FONTS, font))
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = bevel_res
    cu.offset = -bevel if offset is None else offset
    cu.resolution_u = 24
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    ob = bpy.data.objects.new(name + '_txt', cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90), 0, 0)      # text faces -Y (towards the camera)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.transform(ob.matrix_world)
    bpy.data.objects.remove(ob)
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    c = (co.min(0) + co.max(0)) / 2
    me.transform(Matrix.Translation(Vector((-c[0], -c[1], -c[2]))))
    me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
    try:
        me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    except Exception:
        pass
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


# ----------------------------------------------------------------------------- camera + framing

def _mesh_points(objs, max_per=4000):
    pts = []
    rng = np.random.default_rng(0)
    for o in objs:
        if o.type != 'MESH' or o.hide_render:
            continue
        me = o.data
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        if len(co) > max_per:
            co = co[rng.choice(len(co), max_per, replace=False)]
        M = np.array(o.matrix_world)
        pts.append(co @ M[:3, :3].T + M[:3, 3])
    return np.concatenate(pts) if pts else np.zeros((0, 3))


def scene_meshes():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.visible_camera and not o.hide_render]


def frame_camera(points, res, fill=FILL, lens=LENS, elev=ELEV_DEG, target=None, margin_px=None):
    """80 mm camera `elev` degrees above the subject; distance and lens shift chosen so the union of
    `points` (world, (N, 3)) fills `fill` of the frame (longest relative extent) and is centred."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('cam')
    cd.lens = lens
    cd.sensor_fit = 'AUTO'
    cd.sensor_width = 36.0
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    W, Hh = res
    aspect = W / Hh
    c = (points.min(0) + points.max(0)) / 2 if target is None else np.asarray(target, float)
    el = math.radians(elev)
    th = math.atan(18.0 / lens)           # half fov of the larger sensor dimension
    dist = 6.0
    shift = np.zeros(2)
    for _ in range(8):
        cam_pos = np.array([c[0], c[1] - dist * math.cos(el), c[2] + dist * math.sin(el)])
        fwd = c - cam_pos
        fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, [0, 0, 1])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        rel = points - cam_pos
        zc = rel @ fwd
        xs = (rel @ right) / zc / math.tan(th)       # in units of the half larger dimension
        ys = (rel @ up) / zc / math.tan(th)
        hx, hy = (1.0, 1.0 / aspect) if aspect >= 1 else (aspect, 1.0)    # half extents in those units
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        span = max((x1 - x0) / 2 / hx, (y1 - y0) / 2 / hy)
        shift = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        dist *= span / fill
    cam.location = Vector(cam_pos.tolist())
    _aim(cam, tuple(c))
    cd.shift_x = float(shift[0] / 2)
    cd.shift_y = float(shift[1] / 2)
    cd.clip_start = 0.05
    cd.clip_end = 200
    return cam


def project_px(pt):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    co = world_to_camera_view(sc, sc.camera, Vector(tuple(float(v) for v in pt)))
    return [round(float(co.x * sc.render.resolution_x), 1), round(float((1 - co.y) * sc.render.resolution_y), 1)]


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
        rows = np.nonzero((a > 128).any(1))[0]
        if len(rows):
            ground = max(ground, int(rows.max()))
    return bb, ground


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


# ============================================================================= asset registry
# A builder(variant, q) creates the objects (+ rig) and returns a dict:
#   {'modes': {mode: {'n', 'update': fn(i), 'primary': bool, 'loop', 'fps', 'meta': {...}}},
#    'frame_on': [(mode, i), ...]   poses whose union is framed (all modes share one camera),
#    'features': fn() -> {name: world point}   (optional, projected per frame into meta),
#    'pivot': world point of the rotation axis (optional), 'fill': framing fill (optional)}
# q is a mesh-quality factor (1 finals, ~0.6 previews).

ASSETS = {}


def asset(name, variants, size, modes, notes='', priority=9, metal=False, fill=FILL):
    def deco(fn):
        ASSETS[name] = dict(name=name, variants=tuple(variants), size=tuple(size), modes=tuple(modes),
                            notes=notes, build=fn, priority=priority, metal=metal, fill=fill)
        return fn
    return deco


def yaw_of(i, n=YAW_FRAMES):
    return YAW_RANGE[0] + (YAW_RANGE[1] - YAW_RANGE[0]) * i / (n - 1)


def yaw_mode(root, extra=None, n=YAW_FRAMES):
    """Standard 'yaw' mode: root yaw sweeps YAW_RANGE over n frames (rotation about Blender Z)."""
    def upd(i):
        root.rotation_euler = (0.0, 0.0, math.radians(yaw_of(i, n)))
        if extra:
            extra(i)
    return {'n': n, 'update': upd, 'primary': True, 'loop': False, 'fps': 30,
            'meta': {'yaw_range': list(YAW_RANGE), 'axis': 'z'}}


def _folder(variant, mode, m):
    return variant if m.get('primary') else f'{variant}_{mode}'


def render_asset(name, variant, modes=None, preview=False, frames=None, samples=None, q=None):
    """Render one asset variant (all of its modes unless `modes` is given). Returns {folder: meta}."""
    _bpy()
    spec = ASSETS[name]
    W, Hh = spec['size']
    res = (W // 2, Hh // 2) if preview else (W, Hh)
    spp = samples or (PREVIEW_SAMPLES if preview else SAMPLES)
    q = q if q is not None else (0.6 if preview else 1.0)
    t0 = time.time()
    sc = reset(res, spp, variant)
    world(variant, metal=spec['metal'])
    S = spec['build'](variant, q)
    vl = bpy.context.view_layer
    pts = []
    for (mode, i) in S['frame_on']:
        S['modes'][mode]['update'](i)
        vl.update()
        pts.append(_mesh_points(scene_meshes()))
    frame_camera(np.concatenate(pts), res, fill=S.get('fill', spec['fill']), elev=S.get('elev', ELEV_DEG),
                 target=S.get('target'))
    print(f'[{name}/{variant}] scene built in {time.time() - t0:.1f}s, {spp} spp, {res[0]}x{res[1]}', flush=True)
    out = {}
    for mode, m in S['modes'].items():
        if modes and mode not in modes:
            continue
        folder = _folder(variant, mode, m)
        outdir = os.path.join(PREVIEW3D if preview else OUT3D, name, folder)
        os.makedirs(outdir, exist_ok=True)
        n = m['n']
        idx = list(frames) if frames else ([0, n // 2, n - 1] if (preview and n > 3) else list(range(n)))
        idx = [i for i in idx if 0 <= i < n]
        feats = {}
        t1 = time.time()
        for k, i in enumerate(idx):
            m['update'](i)
            vl.update()
            if S.get('features'):
                feats[i] = {kk: project_px(v) for kk, v in S['features']().items()}
            p = os.path.join(outdir, f'{i:04d}.png')
            if os.environ.get('SKIP_EXISTING') and os.path.exists(p) and not preview:
                continue
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            el = time.time() - t1
            print(f'  {name}/{folder} frame {i} ({k + 1}/{len(idx)}) {el / (k + 1):.1f}s/frame', flush=True)
        meta = dict(name=name, variant=folder, mode=m.get('meta_mode', 'yaw' if mode == 'yaw' else
                                                            ('spin' if mode == 'spin' else
                                                             ('static' if mode == 'static' else 'anim'))),
                    frames=n, fps_hint=m.get('fps', 30), size=[res[0], res[1]], loop=bool(m.get('loop')),
                    notes=spec['notes'] + (' ' + m['notes'] if m.get('notes') else ''),
                    samples=spp, preview=bool(preview))
        meta.update(m.get('meta', {}))
        if S.get('pivot') is not None:
            meta['pivot'] = project_px(S['pivot'])
        if feats:
            last = feats[max(feats)]
            meta['features'] = last if m.get('meta_mode', mode) != 'anim' else feats[max(feats)]
            if meta['mode'] in ('anim', 'spin'):
                meta['features_per_frame'] = {str(i): f for i, f in sorted(feats.items())}
            elif meta['mode'] == 'yaw' and (n - 1) // 2 in feats:
                meta['features'] = feats[(n - 1) // 2]
        out[folder] = write_meta(outdir, **meta)
        print(f'  -> {outdir} ({len(idx)} frames, {time.time() - t1:.0f}s)', flush=True)
    return out


# ----------------------------------------------------------------------------- 1. logo_mark3d

LOGO_LAYERS = {
    # kind: (zc, half thickness, bevel r, bevel height rz, dome, dome_w, voxel)
    'ring': (0.0, 0.050, 0.030, 0.040, 0.014, 0.040, 0.0030),
    'child': (0.050, 0.034, 0.013, 0.020, 0.008, 0.030, 0.0020),
    'heart': (0.050, 0.036, 0.016, 0.022, 0.012, 0.030, 0.0020),
    'leaf': (0.060, 0.020, 0.013, 0.016, 0.006, 0.030, 0.0020),
}
LEAF_TILT = {'leaf_l': (16.0, -10.0), 'leaf_r': (16.0, 10.0), 'leaf_top': (14.0, 8.0)}   # (lift, twist) deg


def _rot_axis(axis, ang):
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s = math.cos(ang), math.sin(ang)
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def leaf_frame(p, L):
    """(attach world xy, unit direction attach->tip in the logo plane, tip world xy) for a logo leaf."""
    ys, xs = np.nonzero(p['mask'] > 0.5)
    if p['name'] == 'leaf_top':
        j = np.argmin(xs - ys)                       # lower-left end is the stem
        att = (float(xs[j]), float(ys[j]))
    else:
        att = p['attach']
    d2 = (xs - att[0]) ** 2 + (ys - att[1]) ** 2
    j = np.argmax(d2)
    tip = (float(xs[j]), float(ys[j]))
    a = np.array(px_to_world(att, L))
    t = np.array(px_to_world(tip, L))
    u = (t - a) / np.linalg.norm(t - a)
    return a, u, t


def leaf_rotation(u, lift, twist):
    """Rotation (icon frame) that lifts a leaf lying along in-plane direction u towards the viewer by
    `lift` degrees and twists it `twist` degrees about its own axis."""
    u3 = np.array([u[0], u[1], 0.0])
    k = np.array([-u[1], u[0], 0.0])
    R1 = _rot_axis(k, math.radians(lift))
    if (R1 @ u3)[2] < 0:
        R1 = _rot_axis(k, -math.radians(lift))
    R2 = _rot_axis(R1 @ u3, math.radians(twist))
    return R2 @ R1


def _icon_R_to_blender(R):
    P = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)     # icon -> blender basis change
    return P @ R @ P.T


def build_logo_meshes(q=1.0, parent=None, mats=None, tag=''):
    """Add the layered logo pieces under `parent`. Returns {part name: object} plus '_feat' world points."""
    L = logo_pieces()
    objs = {}
    feat = {}
    for p in L['parts']:
        kind = p['kind']
        zc, h, r, rz, dome, dw, step = LOGO_LAYERS[kind]
        step = step / q
        sd = part_sdf(p, L)
        sdd = part_sdf(p, L, blur=7.0)
        key = f'logo{tag}:v3:{p["name"]}:{LOGO_LAYERS[kind]}:{step:.5f}'
        if kind == 'leaf':
            vs = vein_sdf(p, L)
            f = Slab(sd, h, r, rz, zc=zc, dome=dome, dome_w=dw, groove=(vs, 0.010, 0.0075), dome_sd=sdd)

            def attrs(V, vs=vs):
                dv = vs(V[:, 0], V[:, 1], order=1)
                return {'vein': np.exp(-(dv / 0.0085) ** 2)}
            a, u, t = leaf_frame(p, L)
            pivot = (a[0], a[1], zc)
            o = field_object(p['name'], f, step, mats[kind], parent=parent, cache_key=key, attrs_fn=attrs,
                             pivot=pivot)
            lift, tw = LEAF_TILT[p['name']]
            R = leaf_rotation(u, lift, tw)
            Rb = _icon_R_to_blender(R)
            M = Matrix([list(Rb[0]) + [0], list(Rb[1]) + [0], list(Rb[2]) + [0], [0, 0, 0, 1]])
            loc = o.location.copy()
            o.matrix_local = Matrix.Translation(loc) @ M
            mid = (a + t) / 2
            feat[p['name']] = (o, icon_to_blender(np.array([[mid[0], mid[1], zc]]))[0])
        else:
            f = Slab(sd, h, r, rz, zc=zc, dome=dome, dome_w=dw, dome_sd=sdd)
            o = field_object(p['name'], f, step, mats[kind], parent=parent, cache_key=key)
            if kind == 'heart' or kind == 'child':
                cx, cy = px_to_world(p['centroid'], L)
                feat[p['name']] = (o, icon_to_blender(np.array([[cx, cy, zc + h]]))[0])
        objs[p['name']] = o
    objs['_feat'] = feat
    return objs


def logo_materials(variant):
    return {
        # (subsurface is replaced by a cheap fresnel 'inner light' rim: SSS cost ~15 % render time)
        'ring': m_candy('logo_magenta', 'LOGO_MAGENTA', rough=0.28, coat_r=0.04, sss=0.0,
                        rim='HOT_PINK', rim_str=0.25),
        'child': m_candy('logo_orange', 'LOGO_ORANGE', rough=0.28, coat_r=0.04, sss=0.0,
                         rim='AMBER', rim_str=0.25),
        'heart': m_candy('logo_heart', 'LOGO_ORANGE', rough=0.26, coat_r=0.035, sss=0.0,
                         rim='AMBER', rim_str=0.35),
        'leaf': m_candy('logo_leaf', 'LOGO_LEAF', rough=0.28, coat_r=0.04, sss=0.0,
                        attr_mix=('vein', 'LEAF_HI'), rim='LEAF_HI', rim_str=0.2),
    }


def _feat_fn(feat):
    """feat: {name: (object, world point at rest)} -> fn() giving the points under the current transforms."""
    rest = {}

    def f():
        out = {}
        for k, (o, pw) in feat.items():
            M = np.array(o.matrix_world)
            if k not in rest:
                rest[k] = np.linalg.inv(M)
            p = np.append(np.asarray(pw, float), 1.0)
            out[k] = (M @ (rest[k] @ p))[:3]
        return out
    return f


@asset('logo_mark3d', ('night', 'day'), (1200, 1000), ('yaw', 'anim'), priority=1,
       notes='Layered 3D extrusion of the Organic Fostering OF emblem (vectorised logo_mark.png): MAGENTA '
             'ring+F deepest, ORANGE children+heart proud, LEAF leaves raised and tilted, LEAF_HI veins.')
def build_logo(variant, q):
    root = empty('root')
    mats = logo_materials(variant)
    objs = build_logo_meshes(q, parent=root, mats=mats)
    feat = objs.pop('_feat')
    bpy.context.view_layer.update()
    ff = _feat_fn(feat)
    ff()                                                       # snapshot rest transforms
    rig(variant, scale=1.25, key=1.0, cards=1.0)
    sweep = card('sweep', (-9.0, -6.0, 1.2), (0.9, 9.0), (1.0, 0.97, 0.92), 0.0, soft=0.35)
    T = 60
    fps = 30.0

    def yaw_t(i):
        t = i / fps
        w = 2 * math.pi * 0.62
        z = 2.7
        def sp(tt):
            return 1 - math.exp(-z * tt) * (math.cos(w * tt) + z / w * math.sin(w * tt))
        y = -75.0 * (1 - sp(t))
        yT = -75.0 * (1 - sp((T - 1) / fps))
        return y - yT * (i / (T - 1)) ** 4

    def pitch_t(i):
        t = i / fps
        w = 2 * math.pi * 0.7
        z = 3.2
        s_ = 1 - math.exp(-z * t) * (math.cos(w * t) + z / w * math.sin(w * t))
        sT = 1 - math.exp(-z * (T - 1) / fps) * (math.cos(w * (T - 1) / fps) + z / w * math.sin(w * (T - 1) / fps))
        return 9.0 * (1 - s_) - 9.0 * (1 - sT) * (i / (T - 1)) ** 4

    def anim_upd(i):
        root.rotation_euler = (math.radians(pitch_t(i)), 0.0, math.radians(yaw_t(i)))
        # specular sweep: a tall soft strip travels left -> right across the coat
        u = smoothstep(14, 50, i)
        sweep.location = (-9.0 + 18.0 * float(u), -6.0, 1.2)
        _aim(sweep, (0.0, 0.0, 0.0))
        card_strength(sweep, float(9.0 * math.sin(math.pi * float(u)) ** 1.5))

    def yaw_extra(i):
        card_strength(sweep, 0.0)

    modes = {
        'yaw': yaw_mode(root, yaw_extra),
        'anim': {'n': T, 'update': anim_upd, 'primary': False, 'loop': False, 'fps': 30,
                 'notes': 'Swing-in: yaw -75 -> 0 (spring overshoot ~+7 deg, settles), pitch 9 -> 0, a specular '
                          'strip sweeps left->right (frames 14-50). Last frame == yaw frame 24 (yaw 0).',
                 'meta': {'yaw_start': -75.0, 'axis': 'z'}},
    }
    frame_on = [('anim', i) for i in (0, 8, 16, 24, 32, 59)] + [('yaw', i) for i in (0, 12, 24, 36, 48)]
    return {'modes': modes, 'frame_on': frame_on, 'features': ff, 'pivot': (0.0, 0.0, 0.0)}



# ----------------------------------------------------------------------------- 2. question / 3. pound_glyph

GRAD35 = (math.cos(math.radians(35)), 0.0, math.sin(math.radians(35)))    # signature gradient axis (X right, Z up)


def spin_mode(root, n=72, axis='z', extra=None):
    """'spin': a full 360-degree turn about `axis` over n frames (loops)."""
    def upd(i):
        a = 2 * math.pi * i / n
        root.rotation_euler = (a, 0.0, 0.0) if axis == 'x' else (0.0, 0.0, a)
        if extra:
            extra(i)
    return {'n': n, 'update': upd, 'primary': False, 'loop': True, 'fps': 30, 'meta': {'axis': axis}}


@asset('question', ('night',), (1000, 1000), ('yaw', 'spin'), priority=2,
       notes='Nunito-Black "?" (text object, extrude + round bevel), MAGENTA->ORANGE 35-degree gradient candy.')
def build_question(variant, q):
    root = empty('root')
    o = text_object('qmark', '?', size=2.6, extrude=0.17, bevel=0.10, bevel_res=10 if q >= 1 else 5)
    o.parent = root
    co = np.empty(len(o.data.vertices) * 3, np.float32)
    o.data.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    proj = co @ np.array(GRAD35)
    mat = m_candy('q_grad', 'MAGENTA', rough=0.26, coat_r=0.035, sss=0.0,
                  grad=('ORANGE', GRAD35, float(proj.min()) * 0.75, float(proj.max()) * 0.75),
                  rim='HOT_PINK', rim_str=0.35)
    o.data.materials.append(mat)
    rig(variant, scale=1.0)
    modes = {'yaw': yaw_mode(root), 'spin': spin_mode(root, 72)}
    frame_on = [('spin', i) for i in range(0, 72, 6)] + [('yaw', i) for i in (0, 24, 48)]
    return {'modes': modes, 'frame_on': frame_on, 'pivot': (0.0, 0.0, 0.0)}


@asset('pound_glyph', ('night',), (1000, 1000), ('yaw',), priority=6, metal=True,
       notes='Nunito-Black "£" in polished gold (metallic AMBER base, ORANGE edge tint, roughness 0.18).')
def build_pound(variant, q):
    # The glyph's overlapping contours (crossbar over the stem) break Blender's curve fill + bevel, so the
    # "£" is built as a rounded extrusion of its rasterised SDF instead (same Nunito-Black outline).
    root = empty('root')
    f = glyph_slab('\u00a3', height=2.0, h=0.15, r=0.085, rz=0.10, dome=0.02, dome_w=0.12)
    o = field_object('pound', f, 0.007 / q, m_gold('gold', 'AMBER', 'ORANGE', rough=0.18), parent=root,
                     cache_key=f'pound:v1:{q:.2f}')
    rig(variant, scale=1.0, metal=True)
    modes = {'yaw': yaw_mode(root)}
    return {'modes': modes, 'frame_on': [('yaw', i) for i in (0, 12, 24, 36, 48)], 'pivot': (0.0, 0.0, 0.0)}


def glyph_slab(ch, height=2.0, font='Nunito-Black.ttf', **kw):
    """Rounded extrusion (Slab) of one font glyph, `height` world units tall, centred on its bbox."""
    m, _ = text_mask(ch, font, 1000)
    ys, xs = np.nonzero(m > 0.5)
    px = height / (ys.max() - ys.min() + 1)
    cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    sd = SDF2.from_mask(m, px, origin=(-cx * px, cy * px), up=1, blur=1.0)
    dsd = SDF2.from_mask(m, px, origin=(-cx * px, cy * px), up=1, blur=8.0)
    return Slab(sd, dome_sd=dsd, **kw)


# ----------------------------------------------------------------------------- leaves (shared by leaf / sprout)

def leaf_local_mask(name='leaf_top', length_px=900):
    """The logo leaf `name` rotated/scaled into its own frame: stem base at the bottom centre, tip up.
    Returns (mask float (h, w), base (col, row) px, tip_row, px_per_leaf_length)."""
    import cv2
    L = logo_pieces()
    p = [pp for pp in L['parts'] if pp['name'] == name][0]
    a, u, t = leaf_frame(p, L)
    ua = np.array([u[0], -u[1]])                      # direction in image coords (y down)
    A = np.array(px_to_world((0, 0), L))
    att = np.array([(a[0] - A[0]) / L['px'], (A[1] - a[1]) / L['px']])
    tip = np.array([(t[0] - A[0]) / L['px'], (A[1] - t[1]) / L['px']])
    ln = float(np.linalg.norm(tip - att))
    k = length_px / ln
    ang = math.degrees(math.atan2(ua[1], ua[0])) + 90.0   # rotate so ua points up (-y)
    W = H = int(length_px * 1.5)
    M = cv2.getRotationMatrix2D((float(att[0]), float(att[1])), ang, k)
    M[:, 2] += np.array([W / 2.0, H - length_px * 0.2]) - att
    m = cv2.warpAffine(p['mask'], M, (W, H), flags=cv2.INTER_LINEAR)
    base = (W / 2.0, H - length_px * 0.2)
    return np.clip(m, 0, 1), base, base[1] - length_px, length_px


def leaf_mesh(name='leaf_top', length=2.0, h=0.05, cup=0.10, curl=0.06, q=1.0, vein_w=(0.040, 0.010)):
    """A logo-shaped leaf as a standalone mesh: stem base at the origin, tip along +y, front facing +z
    (icon frame), `length` units long. A tapered midrib groove runs from the base to ~85 % of the length
    (per-vertex 'vein' attribute for the LEAF_HI colour). The blade is cupped (edges raised by `cup` per
    unit^2 across) and curled (`curl` along the length). Returns (V, Q, N, vein, length)."""
    import cv2
    LP = 900
    m, base, tip_row, _ = leaf_local_mask(name, LP)
    px = length / LP
    sd = SDF2.from_mask(m, px, origin=(-base[0] * px, base[1] * px), up=1, blur=1.2)
    dsd = SDF2.from_mask(m, px, origin=(-base[0] * px, base[1] * px), up=1, blur=10.0)
    # midrib: per-row midpoint of the blade, smoothed, from the base up to 85 % of the length
    rows = np.arange(m.shape[0])
    mids = np.full(len(rows), np.nan)
    for r_ in rows:
        xs = np.nonzero(m[r_] > 0.5)[0]
        if len(xs):
            mids[r_] = (xs.min() + xs.max()) / 2.0
    r0, r1 = int(base[1]), int(base[1] - 0.86 * LP)
    rr = np.arange(r1, r0 + 1)
    mm = mids[rr]
    ok = ~np.isnan(mm)
    mm = np.interp(rr, rr[ok], mm[ok])
    from scipy.ndimage import gaussian_filter1d
    mm = gaussian_filter1d(mm, 25)
    mm[-40:] = np.linspace(mm[-40], base[0], 40)           # end exactly in the stem
    # distance to the midrib normalised by a tapered width (so a constant-width groove tapers)
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]].astype(np.float32)
    pts = np.stack([mm, rr], 1).astype(np.float32)
    canvas = np.zeros(m.shape, np.uint8)
    cv2.polylines(canvas, [np.round(pts * 16).astype(np.int32)], False, 255, 1, cv2.LINE_AA, shift=4)
    dist = cv2.distanceTransform((canvas < 128).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    frac = np.clip((base[1] - yy) / (0.86 * LP), 0, 1)
    wpx = (vein_w[0] + (vein_w[1] - vein_w[0]) * frac) / px
    g = dist / wpx * vein_w[0]
    g = np.where(yy < r1 - 4, 1e3, g)                      # nothing beyond the vein's end
    g = cv2.GaussianBlur(g.astype(np.float32), (0, 0), 1.5)
    gsd = SDF2(g, -base[0] * px, base[1] * px, px)
    zc, _, r, rz, dome, dw, step = LOGO_LAYERS['leaf']
    k = 2.0 / length
    f = Slab(sd, h, 0.045 / k, 0.055 / k, zc=0.0, dome=0.03 / k, dome_w=0.25 / k, dome_sd=dsd,
             groove=(gsd, 0.38 * h, vein_w[0] * 0.55))
    V, Q, N = mesh_field(f, 0.0075 / q * length / 2.0, cache_key=f'leafmesh:v5:{name}:{h:.4f}:{length:.3f}:{q:.2f}')
    gv = gsd(V[:, 0], V[:, 1], order=1)
    vein = np.exp(-(gv / (vein_w[0] * 0.6)) ** 2) * smoothstep(0.3, 0.8, np.abs(N[:, 2]))
    X, Y, Z = V[:, 0], V[:, 1], V[:, 2]
    # cup + curl:  z += cup * x^2 + curl * y^2   (normals: n' = n - grad(dz) * n_z)
    gx = 2 * cup * X
    gy = 2 * curl * Y
    Z = Z + cup * X * X + curl * Y * Y
    Nn = np.stack([N[:, 0] - gx * N[:, 2], N[:, 1] - gy * N[:, 2], N[:, 2]], 1)
    Nn /= np.linalg.norm(Nn, axis=1, keepdims=True)
    return np.stack([X, Y, Z], 1), Q, Nn, vein, length


def leaf_material(name='leaf'):
    return m_candy(name, 'LOGO_LEAF', rough=0.27, coat_r=0.04, sss=0.0, attr_mix=('vein', 'LEAF_HI'),
                   rim='LEAF_HI', rim_str=0.25)


@asset('leaf', ('day', 'night'), (600, 600), ('spin',), priority=4,
       notes='One glossy logo leaf (LEAF, LEAF_HI vein groove) tumbling on two axes for falling-leaf particles.')
def build_leaf(variant, q):
    root = empty('root')
    V, Q, N, vein, ln = leaf_mesh('leaf_top', length=2.0, h=0.05, cup=0.10, curl=0.05, q=q)
    V = V - np.array([0.0, ln * 0.5, 0.0])       # rotate about the leaf's middle
    add_mesh('leaf', V, Q, N, leaf_material(), parent=root, attrs={'vein': vein})
    rig(variant, scale=1.0)
    n = 48

    def upd(i):
        a = 2 * math.pi * i / n
        # end-over-end flip about X plus a full turn about Z (both integer turns -> seamless loop),
        # on top of a fixed 25-degree base tilt so no frame is exactly edge-on for long
        root.rotation_mode = 'XYZ'
        root.rotation_euler = (a + math.radians(25), math.radians(20) * math.sin(a), a)
    modes = {'spin': {'n': n, 'update': upd, 'primary': True, 'loop': True, 'fps': 30,
                      'meta': {'axis': 'xz', 'tumble': 'rot_x = t + 25deg, rot_y = 20deg sin t, rot_z = t; '
                                                       't = 360 * i / 48'}}}
    return {'modes': modes, 'frame_on': [('spin', i) for i in range(0, n, 2)], 'pivot': (0.0, 0.0, 0.0)}


# ----------------------------------------------------------------------------- 6. seed

@asset('seed', ('day',), (600, 600), ('static', 'glow'), priority=7,
       notes='Warm glowing seed/orb: PEACH random-walk subsurface, glossy coat, AMBER->ORANGE inner glow.')
def build_seed(variant, q):
    root = empty('root')
    radii = (0.80, 0.95, 0.80)          # icon frame: taller along y (up)
    f = FieldFn(lambda P: sd3_ellipsoid(P, radii), (-0.9, -1.05, -0.9), (0.9, 1.05, 0.9))
    V, Q, N = mesh_field(f, 0.012 / q, cache_key=f'seed:{radii}:{q:.2f}')
    mat = m_seed('seed', glow=1.0)
    add_mesh('seed', V, Q, N, mat, parent=root)
    root.rotation_euler = (0.0, math.radians(-18), 0.0)
    rig(variant, scale=0.9, key=0.25, cards=0.7, rims=0.6)
    glow = mat.node_tree.nodes[mat['glow_node']]
    n = 24

    g0 = glow.inputs[1].default_value

    def st(i):
        glow.inputs[1].default_value = g0

    def gl(i):
        glow.inputs[1].default_value = g0 * (1.0 + 0.45 * math.sin(2 * math.pi * i / n))
    modes = {'static': {'n': 1, 'update': st, 'primary': True, 'loop': False, 'fps': 30,
                        'meta_mode': 'static', 'meta': {'labels': ['seed']}},
             'glow': {'n': n, 'update': gl, 'primary': False, 'loop': True, 'fps': 30, 'meta_mode': 'anim',
                      'notes': 'Inner glow pulses 1.0 -> 1.45 -> 0.55 -> 1.0 (sine, 24 frames, loops).'}}
    return {'modes': modes, 'frame_on': [('static', 0)], 'fill': 0.62, 'pivot': (0.0, 0.0, 0.0)}



# ----------------------------------------------------------------------------- 4. sprout

def _rotm(axis, ang):
    return _rot_axis(axis, ang)


def _align_z(t):
    """Rotation taking +Z onto unit vector t."""
    z = np.array([0.0, 0.0, 1.0])
    t = np.asarray(t, float) / np.linalg.norm(t)
    v = np.cross(z, t)
    c = float(z @ t)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3)
    return _rot_axis(v, math.acos(max(-1.0, min(1.0, c))))


class Sprout:
    """Procedural sprout (Blender coords, base at the origin, growing up +Z).

    spine(g, amp) -> polyline of the visible stem for growth fraction g; leaves are logo-leaf meshes
    deformed per frame (fold about the midrib, scale) and placed with object matrices."""

    HEIGHT = 2.30
    NR = 150            # rings along the stem
    NS = 28             # segments around

    def __init__(self, q=1.0):
        self.q = q
        self.leaf_src = {}
        for nm, ln in (('leaf_l', 0.98), ('leaf_r', 0.98)):
            V, Q, N, vein, _ = leaf_mesh(nm, length=ln, h=0.030, cup=0.20, curl=0.10, q=q * 0.8,
                                         vein_w=(0.024, 0.006))
            self.leaf_src[nm] = (icon_to_blender(V), Q, icon_to_blender(N), vein)
        # final opening angles from the logo (base -> tip direction)
        L = logo_pieces()
        self.logo_ang = {}
        for p in L['parts']:
            if p['name'] in ('leaf_l', 'leaf_r'):
                a, u, t = leaf_frame(p, L)
                self.logo_ang[p['name']] = math.degrees(math.atan2(u[0], u[1]))   # + = towards +X (right)

    # -- stem -----------------------------------------------------------------------------------
    def spine_pt(self, s, amp=1.0, sway=0.0, sway_y=0.0):
        """Point and tangent at arc fraction s of the FINAL stem (s in [0, 1]), shape amplitude amp."""
        H = self.HEIGHT
        s = np.asarray(s, float)
        x = amp * (0.15 * np.sin(2 * np.pi * 0.92 * s - 0.15) + 0.02) * smoothstep(0.0, 0.25, s) \
            + sway * s * s
        y = amp * 0.08 * np.sin(np.pi * s) + sway_y * s * s
        z = H * s
        return np.stack([x, y, z], -1)

    def radius(self, s, g):
        """Stem radius at arc fraction s when grown to g (tip cap is rounded)."""
        r = 0.058 * (1 - 0.40 * s) + 0.012 * np.exp(-s / 0.04)
        # young stems are thinner
        r = r * (0.55 + 0.45 * min(1.0, g * 1.6))
        return r

    def stem_mesh(self, g, amp, sway=0.0, sway_y=0.0):
        NR, NS = self.NR, self.NS
        sv = np.linspace(0.0, g, NR)
        P = self.spine_pt(sv, amp, sway, sway_y)
        T = np.gradient(P, axis=0)
        T /= np.linalg.norm(T, axis=1, keepdims=True)
        # parallel-transport frames
        Nf = np.zeros_like(P)
        ref = np.array([1.0, 0.0, 0.0])
        n0 = ref - T[0] * (T[0] @ ref)
        Nf[0] = n0 / np.linalg.norm(n0)
        for i in range(1, NR):
            n = Nf[i - 1] - T[i] * (T[i] @ Nf[i - 1])
            Nf[i] = n / np.linalg.norm(n)
        B = np.cross(T, Nf)
        r = self.radius(sv, g)
        # rounded tip: shrink the last rings onto a hemisphere of radius r_tip
        Lseg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        arc = np.concatenate([[0], np.cumsum(Lseg)])
        tot = arc[-1]
        rt = r[-1]
        d_end = tot - arc
        cap = d_end < rt
        r = np.where(cap, np.sqrt(np.maximum(rt * rt - (rt - d_end) ** 2, 0.0)) * 1.0, r)
        r[-1] = 0.0
        ang = np.linspace(0, 2 * np.pi, NS, endpoint=False)
        ca, sa = np.cos(ang), np.sin(ang)
        rad = ca[None, :, None] * Nf[:, None, :] + sa[None, :, None] * B[:, None, :]
        V = P[:, None, :] + r[:, None, None] * rad
        # normals: radial tilted by the radius slope
        dr = np.gradient(r) / np.maximum(np.gradient(arc), 1e-6)
        Nn = rad - dr[:, None, None] * T[:, None, :]
        Nn[-1] = T[-1]
        Nn /= np.linalg.norm(Nn, axis=2, keepdims=True)
        V = V.reshape(-1, 3)
        Nn = Nn.reshape(-1, 3)
        # bottom cap centre
        V = np.vstack([V, P[0] - T[0] * 0.0])
        Nn = np.vstack([Nn, -T[0]])
        return V, Nn

    def stem_faces(self):
        NR, NS = self.NR, self.NS
        Q = []
        for i in range(NR - 1):
            for j in range(NS):
                a = i * NS + j
                b = i * NS + (j + 1) % NS
                Q.append((a, b, b + NS, a + NS))
        return np.array(Q)

    # -- leaves ---------------------------------------------------------------------------------
    def leaf_deform(self, nm, fold):
        """Fold the blade halves up about the midrib (Blender leaf local: axis +Z, front -Y, across X)."""
        V, Q, N, vein = self.leaf_src[nm]
        x = V[:, 0]
        eps = 0.02
        sa = np.sqrt(x * x + eps * eps) - eps
        dsa = x / np.sqrt(x * x + eps * eps)
        c, s_ = math.cos(fold), math.sin(fold)
        V2 = V.copy()
        V2[:, 0] = x * c
        V2[:, 1] = V[:, 1] - sa * s_                 # halves rise towards the viewer (-Y)
        # normal transform: J = [[c,0,0],[0,1,0]...] in (x, y) with y' = y - sa(x) s
        N2 = N.copy()
        N2[:, 0] = N[:, 0] / c + dsa * s_ / c * N[:, 1]
        N2 /= np.linalg.norm(N2, axis=1, keepdims=True)
        return V2, N2


@asset('sprout', ('day',), (900, 1200), ('grow', 'sway'), priority=3,
       notes='Procedural sprout: glowing seed at the soil point, S-curve stem, two then four glossy leaves '
             'unfold; the top pair ends in the logo leaves\' pose (logo leaf_l / leaf_r shapes and angles).')
def build_sprout(variant, q):
    S = Sprout(q)
    # materials
    stem_m = m_candy('stem', mixlin('LEAF', 'LEAF_HI', 0.15), rough=0.3, coat_r=0.05, sss=0.0,
                     grad=(mixlin('LEAF', 'LEAF_HI', 0.55), (0.0, 0.0, 1.0), 0.0, S.HEIGHT),
                     rim='LEAF_HI', rim_str=0.2)
    leaf_m = leaf_material('sprout_leaf')
    seed_m = m_seed('sprout_seed', glow=0.22)
    # seed at the soil point
    f = FieldFn(lambda P: sd3_ellipsoid(P, (0.15, 0.13, 0.13)), (-0.17, -0.15, -0.15), (0.17, 0.15, 0.15))
    Vs, Qs, Ns = mesh_field(f, 0.006 / q, cache_key=f'sproutseed:{q:.2f}')
    seed = add_mesh('seed', Vs, Qs, Ns, seed_m, loc=None)
    seed.location = (0.0, 0.0, -0.02)
    seed.rotation_euler = (0.0, math.radians(14), 0.0)
    # stem (constant topology, vertices updated per frame)
    V0, N0 = S.stem_mesh(0.5, 1.0)
    Qst = S.stem_faces()
    stem = add_mesh('stem', V0, Qst, N0, stem_m, icon_frame=False)
    # leaves: (name, src shape, node s or 'tip', final angle, final scale, twist, tilt, unfold window)
    aL, aR = S.logo_ang['leaf_l'], S.logo_ang['leaf_r']
    leaves = [
        dict(name='low_l', src='leaf_l', node=0.42, ang=aL - 24, scale=0.62, twist=-28, tilt=-18, win=(20, 64)),
        dict(name='low_r', src='leaf_r', node=0.42, ang=aR + 24, scale=0.62, twist=28, tilt=-18, win=(24, 68)),
        dict(name='top_l', src='leaf_l', node='tip', ang=aL, scale=1.0, twist=-12, tilt=-10, win=(62, 112)),
        dict(name='top_r', src='leaf_r', node='tip', ang=aR, scale=1.0, twist=12, tilt=-10, win=(66, 116)),
    ]
    for L_ in leaves:
        V, Q, N, vein = S.leaf_src[L_['src']]
        L_['obj'] = add_mesh(L_['name'], V, Q, N, leaf_m, icon_frame=False, attrs={'vein': vein})
    rig(variant, scale=1.15, key=1.0)
    T = 120

    def g_of(i):
        u = min(1.0, max(0.0, i / 92.0))
        return 0.035 + 0.965 * (1 - (1 - u) ** 2.3)

    state = {}

    def pose(i, sway_t=None):
        if sway_t is None:
            g = g_of(i)
            amp = 0.35 + 0.65 * smoothstep(0.1, 1.0, g)
            sw = 0.04 * math.sin(i / 14.0) * (1 - smoothstep(60, 110, i))      # searching tip while growing
            swy = 0.0
            lf = i
        else:
            g, amp = 1.0, 1.0
            ph = 2 * math.pi * sway_t / 48.0
            sw = 0.045 * math.sin(ph)
            swy = 0.03 * math.sin(ph + 1.1)
            lf = T + 10
        Vst, Nst = S.stem_mesh(g, amp, sw, swy)
        me = stem.data
        me.vertices.foreach_set('co', Vst.astype(np.float32).ravel())
        me.normals_split_custom_set_from_vertices(Nst.astype(np.float32))
        me.update()
        feats = {'base': np.array([0.0, 0.0, 0.0])}
        for L_ in leaves:
            if L_['node'] == 'tip':
                s_node = g
                show = True
            else:
                s_node = L_['node']
                show = g > s_node + 0.03
            P = S.spine_pt(np.array([s_node - 0.004, s_node]), amp, sw, swy)
            tang = P[1] - P[0]
            pos = P[1]
            w0, w1 = L_['win']
            u = (lf - w0) / float(w1 - w0)
            if L_['node'] == 'tip':
                # sink the (tiny-petioled) bud into the rounded stem tip; it rises out as it opens
                pos = pos - tang / np.linalg.norm(tang) * (0.012 + 0.05 * (1 - min(max(u, 0.0), 1.0)))
            e = ease_out_back(u, 1.15) if u > 0 else 0.0
            e_lin = min(max(u, 0.0), 1.0)
            if L_['node'] == 'tip':
                sc = 0.30 + 0.70 * e + 0.06 * float(smoothstep(0, 40, lf)) * (1 - e_lin)
            else:
                sc = (0.08 + 0.92 * e) * float(smoothstep(0, 6, (g - s_node - 0.03) * 200))
            ang = math.radians(L_['ang'] * e + (6 if L_['ang'] > 0 else -6) * (1 - e_lin))
            fold = math.radians((62 if L_['node'] == 'tip' else 74) * (1 - ease_out_cubic(u)) + 10)
            twist = math.radians(L_['twist'] * e_lin)
            tilt = math.radians(L_['tilt'] * e_lin)
            if sway_t is not None:
                ph = 2 * math.pi * sway_t / 48.0 + (0.6 if 'r' in L_['name'][-1] else 0.0) + \
                    (0.0 if 'top' in L_['name'] else 1.7)
                ang += math.radians(3.0 * math.sin(ph))
                tilt += math.radians(2.5 * math.sin(ph + 0.8))
            Vd, Nd = S.leaf_deform(L_['src'], fold)
            o = L_['obj']
            o.data.vertices.foreach_set('co', Vd.astype(np.float32).ravel())
            o.data.normals_split_custom_set_from_vertices(Nd.astype(np.float32))
            o.data.update()
            R = _align_z(tang) @ _rotm((0, 1, 0), ang) @ _rotm((1, 0, 0), tilt) @ _rotm((0, 0, 1), twist)
            M = np.eye(4)
            M[:3, :3] = R * max(sc, 1e-3)
            M[:3, 3] = pos
            o.matrix_world = Matrix([list(r) for r in M])
            sc = float(sc)
            o.hide_render = bool((not show) or sc < 0.02)
            # feature: centre of the blade
            ctr = R @ np.array([0.0, 0.0, 0.5 * 0.98]) * sc + pos
            feats['leaf_' + L_['name']] = ctr
        tip = S.spine_pt(np.array([g]), amp, sw, swy)[0]
        feats['tip'] = tip
        state['feats'] = feats

    modes = {
        'grow': {'n': T, 'update': lambda i: pose(i), 'primary': True, 'loop': False, 'fps': 30,
                 'meta_mode': 'anim',
                 'notes': 'Grow: frames 0-92 stem rises (S-curve develops), lower pair unfolds 20-68, top pair '
                          '62-116 (ease-out-back), holds to 119. Frame 119 == day_sway frame 0.'},
        'sway': {'n': 48, 'update': lambda i: pose(None, sway_t=i), 'primary': False, 'loop': True, 'fps': 30,
                 'meta_mode': 'anim', 'notes': 'Idle sway loop (48 frames), starts and ends at the rest pose.'},
    }
    frame_on = [('grow', i) for i in (0, 40, 80, 119)] + [('sway', i) for i in (0, 12, 24, 36)]
    return {'modes': modes, 'frame_on': frame_on, 'features': lambda: state['feats'], 'fill': 0.86,
            'pivot': (0.0, 0.0, 0.0)}



# ----------------------------------------------------------------------------- 2D shape helpers (puzzle / blocks)

class Canvas2D:
    """Tiny anti-aliased raster canvas in world units for building 2D shapes -> SDF2.

        c = Canvas2D((-1, -1, 1, 1), px=0.002)
        c.rbox(0, 0, 0.5, 0.5, 0.1); c.circle(0.6, 0, 0.15); c.circle(-0.3, 0, 0.1, erase=True)
        sd = c.sdf()                     # -> SDF2 (negative inside)
    """

    def __init__(self, bounds, px=0.002, ss=4):
        self.x0, self.y0, self.x1, self.y1 = bounds
        self.px = px
        self.ss = ss
        self.w = int(math.ceil((self.x1 - self.x0) / px)) + 1
        self.h = int(math.ceil((self.y1 - self.y0) / px)) + 1
        self.m = np.zeros((self.h * ss, self.w * ss), np.uint8)

    def _xy(self, x, y):
        k = self.ss / self.px
        return (x - self.x0) * k, (self.y1 - y) * k

    def circle(self, x, y, r, erase=False):
        import cv2
        cx, cy = self._xy(x, y)
        cv2.circle(self.m, (int(round(cx * 16)), int(round(cy * 16))), int(round(r * self.ss / self.px * 16)),
                   0 if erase else 255, -1, cv2.LINE_8, shift=4)

    def poly(self, pts, erase=False):
        import cv2
        P = np.array([self._xy(x, y) for x, y in pts])
        cv2.fillPoly(self.m, [np.round(P * 16).astype(np.int32)], 0 if erase else 255, cv2.LINE_8, shift=4)

    def rbox(self, cx, cy, hw, hh, r, erase=False):
        self.poly([(cx - hw + r, cy - hh), (cx + hw - r, cy - hh), (cx + hw - r, cy + hh), (cx - hw + r, cy + hh)],
                  erase)
        self.poly([(cx - hw, cy - hh + r), (cx + hw, cy - hh + r), (cx + hw, cy + hh - r), (cx - hw, cy + hh - r)],
                  erase)
        for sx in (-1, 1):
            for sy in (-1, 1):
                self.circle(cx + sx * (hw - r), cy + sy * (hh - r), r, erase)

    def round(self, r_open=0.0, r_close=0.0):
        """Round convex (open) and concave (close) corners with radius in world units."""
        import cv2
        for rr, op in ((r_close, cv2.MORPH_CLOSE), (r_open, cv2.MORPH_OPEN)):
            if rr > 0:
                k = int(round(rr * self.ss / self.px)) * 2 + 1
                self.m = cv2.morphologyEx(self.m, op, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))

    def coverage(self):
        import cv2
        return cv2.resize(self.m.astype(np.float32) / 255.0, (self.w, self.h), interpolation=cv2.INTER_AREA)

    def sdf(self, blur=0.8, up=1):
        return SDF2.from_mask(self.coverage(), self.px, origin=(self.x0, self.y1), up=up, blur=blur, pad=8)


def heart_pts(w=1.0, n=400):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    x, y = x / 32.0 * w, y / 32.0 * w
    y = y - (y.max() + y.min()) / 2
    return list(zip(x, y))


def star_pts(r_out=0.5, r_in=0.24, n=5):
    pts = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = math.pi / 2 + k * math.pi / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


# ----------------------------------------------------------------------------- 7. puzzle_pair

PZ_TAB = dict(neck=0.105, reach=0.17, knob=0.155)


def puzzle_sdf(sides, px=0.0025):
    """One jigsaw piece (body 1 x 1 centred at the origin). sides: dict side -> 'tab'|'blank'|'flat' for
    'r', 'l', 't', 'b'. Returns (SDF2, dome SDF2)."""
    c = Canvas2D((-0.95, -0.95, 0.95, 0.95), px)
    c.rbox(0, 0, 0.5, 0.5, 0.13)
    dirs = {'r': (1, 0), 'l': (-1, 0), 't': (0, 1), 'b': (0, -1)}
    nk, rc, kr = PZ_TAB['neck'], PZ_TAB['reach'], PZ_TAB['knob']
    for sd_, kind in sides.items():
        dx, dy = dirs[sd_]
        if kind == 'tab':
            c.circle(dx * (0.5 + rc), dy * (0.5 + rc), kr)
            a, b = 0.40, 0.5 + rc
            c.poly([(dx * a - dy * nk, dy * a - dx * nk), (dx * b - dy * nk, dy * b - dx * nk),
                    (dx * b + dy * nk, dy * b + dx * nk), (dx * a + dy * nk, dy * a + dx * nk)])
    for sd_, kind in sides.items():
        dx, dy = dirs[sd_]
        if kind == 'blank':
            cl = 0.014
            c.circle(dx * (0.5 - rc), dy * (0.5 - rc), kr + cl, erase=True)
            a, b = 0.5 - rc, 0.62
            n2 = nk + cl
            c.poly([(dx * a - dy * n2, dy * a - dx * n2), (dx * b - dy * n2, dy * b - dx * n2),
                    (dx * b + dy * n2, dy * b + dx * n2), (dx * a + dy * n2, dy * a + dx * n2)], erase=True)
    c.round(r_open=0.03, r_close=0.045)
    return c.sdf(blur=1.0), c.sdf(blur=14.0)


@asset('puzzle_pair', ('day',), (1000, 800), ('yaw', 'anim'), priority=5,
       notes='Two chunky rounded candy jigsaw pieces (MAGENTA left with a tab, ORANGE right with the blank).')
def build_puzzle(variant, q):
    root = empty('root')
    pieces = {}
    specs = {'mag': ({'r': 'tab', 't': 'tab', 'b': 'blank', 'l': 'flat'}, 'MAGENTA', -0.5, 'HOT_PINK'),
             'ora': ({'l': 'blank', 't': 'blank', 'b': 'tab', 'r': 'flat'}, 'ORANGE', 0.5, 'AMBER')}
    for k, (sides, col, x, rimc) in specs.items():
        sd, dsd = puzzle_sdf(sides)
        f = Slab(sd, 0.12, 0.075, 0.09, dome=0.04, dome_w=0.30, dome_sd=dsd)
        mat = m_candy('pz_' + k, col, rough=0.27, coat_r=0.035, sss=0.0, rim=rimc, rim_str=0.3)
        V, Q, N = mesh_field(f, 0.006 / q, cache_key=f'puzzle:v1:{k}:{q:.2f}')
        o = add_mesh('pz_' + k, V, Q, N, mat, parent=root)
        pieces[k] = (o, x)
    rig(variant, scale=1.1)
    T = 48
    t_hit = 25.0

    def anim(i):
        u = min(1.0, max(0.0, (i - 1) / (t_hit - 1)))
        e = u * u * (3 - 2 * u) * 0.35 + (1 - (1 - u) ** 3) * 0.65          # eased slide, still moving at contact
        for k, (o, x) in pieces.items():
            sgn = -1 if x < 0 else 1
            d = 1 - e
            o.location = (x + sgn * 0.42 * d, -0.30 * d * (1 - d) * 2.2, 0.10 * d * (1 if sgn < 0 else -1))
            o.rotation_euler = (math.radians(10 * d), math.radians(-sgn * 14 * d), math.radians(sgn * 22 * d))
        f = max(0.0, i - t_hit)
        fade = 1 - float(smoothstep(40, 47, i))
        pulse = 0.055 * math.exp(-f / 5.5) * math.sin(f * 0.62) * fade if i >= t_hit else 0.0
        wob = math.radians(3.5) * math.exp(-f / 6.5) * math.sin(f * 0.55 + 0.4) * fade if i >= t_hit else 0.0
        root.scale = (1 + pulse, 1 + pulse, 1 + pulse)
        root.rotation_euler = (0.0, wob, 0.0)

    def yaw_extra(i):
        for k, (o, x) in pieces.items():
            o.location = (x, 0.0, 0.0)
            o.rotation_euler = (0.0, 0.0, 0.0)
        root.scale = (1, 1, 1)

    ym = yaw_mode(root, yaw_extra)
    _yu = ym['update']

    def yaw_upd(i):
        yaw_extra(i)
        _yu(i)
    ym['update'] = yaw_upd
    modes = {'yaw': ym,
             'anim': {'n': T, 'update': anim, 'primary': False, 'loop': False, 'fps': 30,
                      'notes': 'Pieces slide in from the sides (lifted, tilted) and meet at frame 25 (click), '
                               'then a damped scale pulse + roll wobble settles by frame 47 (== yaw frame 24).',
                      'meta': {'click_frame': 25}}}
    frame_on = [('anim', i) for i in (0, 6, 12, 18, 25, 30)] + [('yaw', i) for i in (0, 12, 24, 36, 48)]
    return {'modes': modes, 'frame_on': frame_on, 'pivot': (0.0, 0.0, 0.0), 'fill': 0.86}


# ----------------------------------------------------------------------------- 8. blocks

@asset('blocks', ('day',), (800, 800), ('yaw',), priority=8,
       notes='Three stacked rounded toy blocks: MAGENTA (heart), ORANGE (star), LEAF (leaf), raised ivory symbols '
             'on all four sides.')
def build_blocks(variant, q):
    root = empty('root')
    hs = 0.45
    fb = FieldFn(lambda P: sd3_round_box(P, (hs, hs, hs), 0.11), (-0.47, -0.47, -0.47), (0.47, 0.47, 0.47))
    Vb, Qb, Nb = mesh_field(fb, 0.008 / q, cache_key=f'block:{q:.2f}')
    # symbols (icon frame, front face at z = hs)
    c = Canvas2D((-0.4, -0.4, 0.4, 0.4), 0.0016)
    c.poly(heart_pts(0.58))
    heart = c.sdf()
    c = Canvas2D((-0.4, -0.4, 0.4, 0.4), 0.0016)
    c.poly(star_pts(0.31, 0.15))
    c.round(r_open=0.035)
    star = c.sdf()
    lm, base, tip_row, LP = leaf_local_mask('leaf_top', 600)
    lpx = 0.56 / LP
    ys, xs = np.nonzero(lm > 0.5)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    import cv2
    Mrot = cv2.getRotationMatrix2D((float(cx), float(cy)), -35, 1.0)
    lm = cv2.warpAffine(lm, Mrot, (lm.shape[1], lm.shape[0]), flags=cv2.INTER_LINEAR)
    leaf = SDF2.from_mask(lm, lpx, origin=(-cx * lpx, cy * lpx), up=1, blur=1.0)
    sym = {}
    for nm, sd in (('heart', heart), ('star', star), ('leaf', leaf)):
        f = Slab(sd, 0.03, 0.024, 0.03, zc=hs - 0.012, dome=0.012, dome_w=0.06)
        sym[nm] = mesh_field(f, 0.0035 / q, cache_key=f'blocksym:v1:{nm}:{q:.2f}')
    ivory = m_candy('sym_ivory', 'IVORY', rough=0.25, coat_r=0.035, sss=0.0)
    stack = [('MAGENTA', 'heart', 0.0, -8.0, 'HOT_PINK'), ('ORANGE', 'star', 0.96, 9.0, 'AMBER'),
             ('LEAF', 'leaf', 1.92, -4.0, 'LEAF_HI')]
    for k, (col, sy, z, rot, rimc) in enumerate(stack):
        b = empty(f'block{k}', parent=root)
        b.location = (0.04 * (k - 1) * (1 if k != 1 else -1), 0.0, z)
        b.rotation_euler = (0.0, 0.0, math.radians(rot))
        add_mesh(f'cube{k}', Vb, Qb, Nb, m_candy(f'blk{k}', col, rough=0.28, coat_r=0.04, sss=0.0, rim=rimc,
                                                  rim_str=0.25), parent=b)
        V, Q, N = sym[sy]
        for j in range(4):
            ang = j * math.pi / 2
            R = _rot_axis((0, 1, 0), ang)                       # icon frame: about y (up)
            add_mesh(f'sym{k}_{j}', V @ R.T, Q, N @ R.T, ivory, parent=b)
    rig(variant, scale=1.3)
    modes = {'yaw': yaw_mode(root)}
    return {'modes': modes, 'frame_on': [('yaw', i) for i in (0, 6, 12, 18, 24, 30, 36, 42, 48)],
            'pivot': (0.0, 0.0, 0.0)}



# ============================================================================= contact sheets + selftest (no bpy needed)

def _read_rgba_lin(p):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None:
        return None
    if im.ndim == 2:
        im = np.dstack([im] * 3)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    rgb = im[:, :, 2::-1].astype(np.float32) / 255.0
    a = im[:, :, 3:4].astype(np.float32) / 255.0
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return np.concatenate([lin * a, a], 2)


def _backdrop(h, w, kind):
    yy = np.linspace(0, 1, h)[:, None, None]
    xx = np.linspace(-1, 1, w)[None, :, None]
    if kind == 'night':
        base = np.array(hexlin('NIGHT_1')) * (1 - yy) + np.array(hexlin('NIGHT_0')) * yy
        glow = np.exp(-((xx - 0.2) ** 2 + (yy - 0.35) ** 2 * 2.5) * 2.0) * 0.55
        img = base + glow * (np.array(hexlin('PLUM')) - base)
    else:
        img = np.array(hexlin('IVORY')) * (1 - yy) + np.array(hexlin('LAVENDER')) * yy
    return np.broadcast_to(img, (h, w, 3)).astype(np.float32).copy()


def _to8(x):
    x = np.clip(x, 0, 1)
    s_ = np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    return np.clip(s_ * 255 + 0.5, 0, 255).astype(np.uint8)[:, :, ::-1].copy()


def _tile(path, cell, kind):
    import cv2
    im = _read_rgba_lin(path)
    h = cell
    if im is None:
        return _backdrop(h, cell, kind)
    w = max(1, int(round(im.shape[1] * h / im.shape[0])))
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    bg = _backdrop(h, w, kind)
    return im[:, :, :3] + bg * (1 - im[:, :, 3:4])


def contact_sheets(root=None, tag='contact', cell=220, names=None, per_sheet=8):
    """For every asset of this module rendered under `root` (default the finals in assets3d/): one row per
    folder with its first, middle and last frame over a dark plum backdrop and then over an ivory backdrop.
    Writes out/selftest/assets3d_hero_<tag>_<k>.png and returns the paths."""
    import cv2
    root = root or OUT3D
    rows = []
    for nm in (names or sorted(ASSETS, key=lambda k: ASSETS[k]['priority'])):
        base = os.path.join(root, nm)
        if not os.path.isdir(base):
            continue
        for folder in sorted(os.listdir(base)):
            d = os.path.join(base, folder)
            fs = sorted(f for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []
            if not fs:
                continue
            pick = [fs[0], fs[len(fs) // 2], fs[-1]] if len(fs) >= 3 else fs
            tiles = [_tile(os.path.join(d, f), cell, kind) for kind in ('night', 'day') for f in pick]
            row = _to8(np.concatenate(tiles, 1))
            meta = {}
            try:
                with open(os.path.join(d, 'meta.json')) as fh:
                    meta = json.load(fh)
            except Exception:
                pass
            lab = (f"{nm}/{folder}  {meta.get('mode', '?')} {meta.get('frames', len(fs))}f "
                   f"{'x'.join(str(v) for v in meta.get('size', []))}  frames {', '.join(f[:-4] for f in pick)}")
            cv2.rectangle(row, (0, 0), (len(lab) * 9 + 12, 22), (30, 12, 34), -1)
            cv2.putText(row, lab, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (235, 225, 240), 1, cv2.LINE_AA)
            rows.append(row)
    if not rows:
        return []
    os.makedirs(SELFTEST, exist_ok=True)
    outs = []
    for k in range(0, len(rows), per_sheet):
        chunk = rows[k:k + per_sheet]
        wmax = max(r.shape[1] for r in chunk)
        chunk = [np.pad(r, ((0, 4), (0, wmax - r.shape[1]), (0, 0)), constant_values=255) for r in chunk]
        pth = os.path.join(SELFTEST, f'assets3d_hero_{tag}_{k // per_sheet}.png')
        cv2.imwrite(pth, np.concatenate(chunk, 0))
        outs.append(pth)
    return outs


def selftest():
    """1) numpy: mesher checks (closed, residual, outward normals) + logo vectorisation sanity;
    2) a sheet of the 2D shapes (logo parts, leaf + midrib, jigsaw pieces, symbols);
    3) Blender: tiny low-sample renders of every asset into a temp folder (finals untouched) -> sheet;
    4) contact sheets of the finals if they exist."""
    import cv2
    import tempfile
    os.makedirs(SELFTEST, exist_ok=True)
    t0 = time.time()
    f = FieldFn(lambda P: np.linalg.norm(P, axis=-1) - 0.8, (-0.85, -0.85, -0.85), (0.85, 0.85, 0.85))
    V, Q, N = mesh_field(f, 0.03, verbose=False)
    E = {}
    for qd in Q:
        for a_, b_ in zip(qd, np.roll(qd, -1)):
            k = (min(a_, b_), max(a_, b_))
            E[k] = E.get(k, 0) + 1
    assert all(c == 2 for c in E.values()), 'sphere mesh must be closed and manifold'
    assert len(V) - len(E) + len(Q) == 2, 'sphere must have Euler characteristic 2'
    r = np.linalg.norm(V, axis=1)
    assert np.abs(r - 0.8).max() < 1e-3, 'Newton projection residual too large'
    assert (np.einsum('ij,ij->i', N, V / r[:, None]) > 0.999).all(), 'normals must point outwards'
    # face winding agrees with the analytic normals
    fn = np.cross(V[Q[:, 1]] - V[Q[:, 0]], V[Q[:, 2]] - V[Q[:, 0]])
    assert (np.einsum('ij,ij->i', fn, V[Q[:, 0]]) > 0).mean() > 0.99, 'faces must wind outwards'
    L = logo_pieces()
    names = sorted(p['name'] for p in L['parts'])
    assert names == sorted(['ring_o', 'ring_f', 'heart', 'girl', 'boy', 'leaf_l', 'leaf_r', 'leaf_top']), names
    print(f'selftest: mesher + logo parts ok ({time.time() - t0:.1f}s)')
    # 2) shape sheet
    tiles = []

    def show(sd, title, lo=-1.0, hi=1.0, extra=None, n=260):
        xs = np.linspace(lo, hi, n)
        X, Y = np.meshgrid(xs, xs[::-1])
        d = sd(X, Y, order=1)
        img = np.zeros((n, n, 3), np.uint8)
        img[:] = (40, 12, 30)
        img[d < 0] = (110, 0, 183)
        band = (np.abs(np.mod(d, 0.05) - 0.025) < 0.003) & (d > 0)
        img[band] = (90, 60, 90)
        img[np.abs(d) < (hi - lo) / n] = (245, 248, 252)
        if extra is not None:
            img[extra(X, Y)] = (74, 224, 168)
        cv2.putText(img, title, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 230, 240), 1, cv2.LINE_AA)
        tiles.append(img)
    show(part_sdf([p for p in L['parts'] if p['name'] == 'ring_o'][0], L), 'logo ring_o', -1.25, 0.35)
    show(part_sdf([p for p in L['parts'] if p['name'] == 'girl'][0], L), 'logo girl', -0.85, 0.05)
    lm, base, _, LP = leaf_local_mask('leaf_top', 400)
    px = 2.0 / LP
    show(SDF2.from_mask(lm, px, origin=(-base[0] * px, base[1] * px), up=1), 'leaf (local frame)', -1.2, 2.2)
    sdm, _ = puzzle_sdf({'r': 'tab', 't': 'tab', 'b': 'blank', 'l': 'flat'})
    show(sdm, 'jigsaw magenta', -0.9, 0.9)
    c = Canvas2D((-0.4, -0.4, 0.4, 0.4), 0.002)
    c.poly(star_pts(0.31, 0.15))
    c.round(r_open=0.035)
    show(c.sdf(), 'star symbol', -0.45, 0.45)
    cv2.imwrite(os.path.join(SELFTEST, 'assets3d_hero_shapes.png'), np.concatenate(tiles, 1))
    # 3) tiny renders into a temp dir
    global OUT3D, PREVIEW3D
    keep = (OUT3D, PREVIEW3D)
    tmp = tempfile.mkdtemp(prefix='hero3d_')
    try:
        OUT3D = PREVIEW3D = tmp
        for nm in sorted(ASSETS, key=lambda k: ASSETS[k]['priority']):
            spec = ASSETS[nm]
            W, Hh = spec['size']
            ASSETS[nm]['size'] = (max(64, W // 5) * 2, max(64, Hh // 5) * 2)     # preview halves again
            try:
                render_asset(nm, spec['variants'][0], preview=True, samples=6, q=0.45)
            finally:
                ASSETS[nm]['size'] = (W, Hh)
        rows = contact_sheets(root=tmp, tag='selftest_renders', cell=150)
        print('selftest renders:', rows)
    finally:
        OUT3D, PREVIEW3D = keep
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    outs = contact_sheets()
    print('finals contact sheets:', outs)
    return 0


# ============================================================================= CLI

def _parse(argv):
    o = {'names': [], 'preview': False, 'variant': None, 'mode': None, 'frames': None, 'samples': None}
    it = iter(argv)
    for a in it:
        if a == '--preview':
            o['preview'] = True
        elif a == '--variant':
            o['variant'] = next(it)
        elif a == '--mode':
            o['mode'] = next(it)
        elif a == '--frames':
            o['frames'] = [int(x) for x in next(it).split(',')]
        elif a == '--samples':
            o['samples'] = int(next(it))
        else:
            o['names'].append(a)
    return o


def main(argv):
    o = _parse(argv)
    names = o['names']
    if not names:
        print(__doc__)
        return 0
    if names == ['selftest']:
        return selftest()
    if names == ['sheet']:
        print(contact_sheets())
        return 0
    if names == ['previewsheet']:
        print(contact_sheets(root=PREVIEW3D, tag='preview'))
        return 0
    if names == ['all']:
        names = sorted(ASSETS, key=lambda k: ASSETS[k]['priority'])
    for nm in names:
        spec = ASSETS[nm]
        for v in spec['variants']:
            if o['variant'] and v != o['variant']:
                continue
            render_asset(nm, v, modes=[o['mode']] if o['mode'] else None, preview=o['preview'],
                         frames=o['frames'], samples=o['samples'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
