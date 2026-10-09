"""assets3d_pehle_wala.py - Blender props for reel C26 "Pehle Wala Hi Theek Tha" (slot 1, look `inferno`).

One prop (BRIEF.md section 13): `pw_chai_glass`, a cutting-chai glass with milky chai, the hero product of the
fictional "Ubaal Chai" ad that the reel keeps revising. It is composited by `pehle_wala.py` on the 2D ad plate
(ember backlight, contact shadow and floor reflection are drawn there; no ground plane here).

Geometry (centimetres, 1 Blender unit = 1 cm, Z up, camera on -Y, base centre at the origin)
--------------------------------------------------------------------------------------------
    small tapered tumbler, height 9.0, rim (lip) diameter 6.6, base diameter 5.2, solid base 1.2 thick,
    wall 3.5 mm (2.5 mm at a facet centre), 12 shallow vertical flats on the outside (ridges softened, the
    flats fade into a smooth band between z 6.2 and 7.0), slight rim flare, fire-polished round lip;
    milky chai filled to 78 % of the inner depth (surface z 7.284), meniscus 1.3 mm, a thin irregular
    cream-foam ring hugging the wall. Built as exact lathe meshes in numpy (closed, manifold), not voxels.

Look (BRIEF section 13; brand tokens are this builder's own table, TOKENS)
-------------------------------------------------------------------------
    glass  Principled: transmission 1, IOR 1.50, roughness 0.04, base colour GLASS_TINT (see below),
           casts no shadow (so the key and rims reach the chai, the usual product-glass setting);
    chai   roughness 0.25, subsurface 0.3 random walk, radius (1.0, 0.5, 0.25) cm, IOR 1.34; albedo CHAI_ALBEDO
           (#A68867, a milky-tea tan) calibrated so the key-lit chai RENDERS the brief's #A0582A (measured
           #9C5729 at 960x1280; the literal #A0582A albedo under the 3200 K key rendered #96370D);
    foam   roughness 0.6, fine bump, albedo FOAM_ALBEDO calibrated the same way (renders ~#D89A64 vs #D9A06A).
    Light: key = 3200 K soft box 30x60 cm front-left, 13 deg up (irradiance ratio 1.0), fill front-right (0.15),
    rims behind left FLAME and right RED (2.5), a top strip (0.35, lifts the chai top and the foam); area lights
    reach diffuse/subsurface only (never glossy/transmission).
    What the glass shows comes from soft-edged emissive cards (camera-invisible): an oval key card, a faint
    fill card, two tall rim strips (FLAME left, RED right) that draw the glass edges, and a top strip for the
    lip line. World #170A07 at 0.02. Cycles CPU, threads 2, adaptive + OpenImageDenoise (albedo + normal),
    fixed seed, `use_animated_seed = False`. Film transparent with `film_transparent_glass = True`, so the
    2D plate (dark ember plate or the cream gag) shows through the empty top of the glass.

    GLASS_TINT: the brief asks for a "barely warm" #FFF1E2 glass. Cycles applies a Principled transmission
    colour at every surface crossing; a ray through the tumbler crosses 4 surfaces, so #FFF1E2 per crossing
    compounds to a brown smoked glass (and film_transparent_glass turns the tint into a grey veil over the
    plate). The per-crossing colour is therefore #FFF1E2 ** (1/4) in linear (#FFFBF7), which makes the whole
    tumbler transmit #FFF1E2: the intended barely-warm glass. Set PW3D_GLASS_TINT=raw for the literal value.

Camera: 85 mm lens, 7 degrees above the rim plane (optical axis aimed at the rim centre, pitched down 7 deg),
0.90 m from the rim centre (a real 85 mm lens's close-focus product distance), framed as a crop (vertical
sensor fit, lens shift) so the union of all yaw poses fills 80 % of the frame height. At 0.9 m the rim reads as
a thin ellipse (~0.12) and the base as ~0.22, which matches the plate's 2D contact shadow; one fixed camera
for every frame.

CLI
---
    python3 assets3d_pehle_wala.py pw_chai_glass [--preview] [--variant inferno] [--mode yaw]
                                   [--frames 0,6,12] [--samples N]
    python3 assets3d_pehle_wala.py all [--preview]   # every asset (just pw_chai_glass)
    python3 assets3d_pehle_wala.py sheet             # finals: tiles over black / FLAME / v1 plate / cream +
                                                     # the 440 px composites -> props/sheets/
    python3 assets3d_pehle_wala.py previewsheet      # the same for the --preview renders
    python3 assets3d_pehle_wala.py selftest          # numpy geometry checks (+ finals checks when present)
    Run the renders through pipeline/jawad_reels/tools/heavy.sh (shared 2-slot semaphore, nice 10).

    --preview  480x640, 16 spp, frames 0, 6, 12 -> props/_preview/<name>/<folder>/ (finals untouched)
    --full     a final-quality test (960x1280, final spp) written to the preview folder
    env PW3D_SAMPLES (final spp, default 64), PW3D_THREADS (default 2), SKIP_EXISTING=1 resumes a sequence.

Output (shared 3D asset spec; this reel's workspace, WS = workspace/jawad_reels)
------------------------------------------------------------------------------
    <WS>/pehle_wala/props/pw_chai_glass/inferno_yaw/0000.png ... 0012.png + meta.json (written LAST)
    <WS>/pehle_wala/assets3d/pw_chai_glass -> ../props/pw_chai_glass (symlink: the brief's load root)
    13 frames, mode 'yaw', yaw -6 ... +6 deg (1 deg step), 960x1280 RGBA 8-bit straight alpha, sRGB
    (Standard view, look None, gamma 1). Positive yaw turns the front to screen-right.
    PNG encoding: Cycles writes a float EXR (premultiplied); the PNG keeps highlight energy on the clear
    glass by storing alpha = max(alpha, max(rgb)) before un-premultiplying (an 8-bit straight-alpha PNG
    otherwise clips a 0.25 reflection over 0.04 alpha down to 0.04). Over a dark plate it composites exactly;
    over cream a highlight darkens the cream behind it by at most its own value.
    meta.json: anchor = feature 'base' (base centre), features base, rim (rim centre), surface (chai surface
    centre), rim_front, rim_back, rim_left, rim_right, base_front; pivot = base; plus px_per_cm,
    glass_height_px (base centre to the top of the alpha bbox), camera notes.

Load (BRIEF section 13):
    S3.Asset3D('pw_chai_glass', 'inferno', mode='yaw',
               root='/home/user/100/workspace/jawad_reels/pehle_wala/assets3d').at_yaw(yaw(t), interp='flow')
"""
import os
import sys
import json
import math
import time

os.environ.setdefault('OPENCV_IO_ENABLE_OPENEXR', '1')   # before any cv2 import (EXR -> PNG conversion)

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import assets3d_hero as H  # noqa: E402  (reset, card, area, project_px, write_meta, _bpy)

REEL = 'pehle_wala'
WS_REEL = os.path.join(H.WS, REEL)
PROPS = os.path.join(WS_REEL, 'props')
ASSETS_ROOT = os.path.join(WS_REEL, 'assets3d')          # the brief's S3 load root (symlinks into PROPS)
PREVIEW = os.path.join(PROPS, '_preview')
SHEETS = os.path.join(PROPS, 'sheets')
TMP = os.path.join(PROPS, '_tmp')

SAMPLES = int(os.environ.get('PW3D_SAMPLES', '64'))
THREADS = int(os.environ.get('PW3D_THREADS', '2'))
PREVIEW_SAMPLES = 16

# ============================================================================= brand tokens (own table)

TOKENS = {
    'NIGHT_0': '#070404', 'NIGHT_1': '#170A07', 'SMOKE': '#2A1A15', 'PLUM': '#4A0E08',
    'FLAME': '#FF6A1A', 'RED': '#F2312B', 'EMBER': '#B3120E', 'GOLD': '#FF9F1C', 'AMBER': '#FFB547',
    'IVORY': '#FFF3E6', 'ASH': '#A8978C', 'INK': '#0B0706',
    # prop materials (BRIEF section 13)
    'GLASS': '#FFF1E2', 'CHAI': '#A0582A', 'FOAM': '#D9A06A',
}


def s2l(c):
    c = np.asarray(c, np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def l2s(c):
    c = np.clip(np.asarray(c, np.float64), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lin(h):
    """'#RRGGBB' or a TOKENS key -> linear RGB tuple.  e.g. lin('FLAME') -> (1.0, 0.144, 0.0103)"""
    if not isinstance(h, str):
        return tuple(float(x) for x in h[:3])
    h = TOKENS.get(h, h).lstrip('#')
    return tuple(float(v) for v in s2l([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]))


def hexs(rgb_lin):
    s = l2s(rgb_lin)
    return '#' + ''.join(f'{int(round(v * 255)):02X}' for v in s)


def glass_tint():
    """Per-crossing transmission colour so that the 4 crossings of the tumbler give TOKENS['GLASS']."""
    if os.environ.get('PW3D_GLASS_TINT', '') == 'raw':
        return lin('GLASS')
    return tuple(v ** 0.25 for v in lin('GLASS'))


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ============================================================================= geometry (numpy, cm)

GEO = dict(
    height=9.0, rim_d=6.6, base_d=5.2, base_t=1.2, wall=0.35, facets=12, fill=0.78,
    flare_z0=7.6, flare=0.10,              # rim flare: +1 mm of radius over the top 1.4 cm (quadratic)
    facet_fade=(6.2, 7.0),                 # flats run from the foot to z 6.2, fading out by z 7.0
    facet_soft=0.004,                      # smooth-min softness of the ridges (relative radius)
    foot_r=0.25, inner_fillet=0.45, punt=0.05,
    overlap=0.012,                         # chai pushed 0.12 mm into the glass (no air film at the wall)
    meniscus=(0.13, 0.16),                 # height, decay length (cm)
    foam_w=(0.40, 0.12),                   # ring width, irregularity (cm)
)
THETA0 = -math.pi / 2                      # a flat faces the camera (-Y) at yaw 0


class Profile:
    """The glass's radial profile r(z): outer (ridge/circumradius) wall, inner wall, lip bead, foot and inner
    fillets. The taper slope is solved so the outermost lip diameter is exactly GEO['rim_d']."""

    def __init__(self, g=GEO):
        self.g = g
        self.rb = g['base_d'] / 2
        lo, hi = 0.0, 0.2
        for _ in range(60):                     # bisection on the taper slope k
            self.k = (lo + hi) / 2
            self._bead()
            if self.lip_r > g['rim_d'] / 2:
                hi = self.k
            else:
                lo = self.k
        self._bead()
        self.z_inner = g['base_t']
        self.z_surface = g['base_t'] + g['fill'] * (g['height'] - g['base_t'])

    def r_out(self, z):
        g = self.g
        z = np.asarray(z, np.float64)
        u = np.clip((z - g['flare_z0']) / (g['height'] - g['flare_z0']), 0, None)
        return self.rb + self.k * z + g['flare'] * u * u

    def slope(self, z):
        g = self.g
        u = np.clip((np.asarray(z, np.float64) - g['flare_z0']) / (g['height'] - g['flare_z0']), 0, None)
        return self.k + 2 * g['flare'] * u / (g['height'] - g['flare_z0'])

    def r_in(self, z):
        return self.r_out(z) - self.g['wall']

    def _bead(self):
        """Round lip tangent to both walls: semicircle of radius rho = wall/2 * cos(beta), top at height."""
        g = self.g
        zc = g['height'] - g['wall'] / 2
        for _ in range(6):
            beta = math.atan(float(self.slope(zc)))
            rho = g['wall'] / 2 * math.cos(beta)
            zc = g['height'] - rho
        zj = zc - rho * math.sin(beta)                         # outer junction height
        rc = float(self.r_out(zj)) - rho * math.cos(beta)
        self.bead = (rc, zc, rho, beta)
        self.lip_r = rc + rho                                  # outermost lip radius (angle 0 on the arc)

    # ------------------------------------------------------------------ sampled profile
    def glass(self, q=1.0):
        """(r, z, w) arrays from the underside centre (excluded) round to the inner-bottom centre (excluded);
        w = facet weight (1 on the faceted outer wall, 0 on the smooth band, lip and inside)."""
        g = self.g
        n = lambda k: max(4, int(round(k * q)))                # noqa: E731
        R, Z, W = [], [], []

        def add(r, z, w):
            R.extend(np.atleast_1d(r).tolist()); Z.extend(np.atleast_1d(z).tolist())
            W.extend(np.broadcast_to(np.atleast_1d(w), np.atleast_1d(r).shape).tolist())

        # foot fillet centre (tangent to the underside and to the tapered wall)
        fr = g['foot_r']
        b0 = math.atan(self.k)
        cr = float(self.r_out(fr - fr * math.sin(b0))) - fr * math.cos(b0)
        # underside with a shallow punt, r in (0, cr]
        t = np.linspace(0, 1, n(36) + 1)[1:]
        ru = cr * (1 - (1 - t) ** 1.6)                         # denser towards the foot
        zu = g['punt'] * (1 - (ru / cr) ** 2) ** 2
        add(ru, zu, 1.0)
        # foot fillet: -90 deg -> -b0
        ph = np.linspace(-math.pi / 2, -b0, n(18) + 1)[1:]
        add(cr + fr * np.cos(ph), fr + fr * np.sin(ph), 1.0)
        # outer wall up to the lip junction
        rc, zc, rho, beta = self.bead
        z0, z1 = fr - fr * math.sin(b0), zc - rho * math.sin(beta)
        s = np.linspace(0, 1, n(150) + 1)[1:]
        zs = z0 + (z1 - z0) * s
        f0, f1 = g['facet_fade']
        add(self.r_out(zs), zs, 1.0 - smoothstep(f0, f1, zs))
        # lip bead: -beta -> pi - beta (over the top)
        ph = np.linspace(-beta, math.pi - beta, n(40) + 1)[1:]
        add(rc + rho * np.cos(ph), zc + rho * np.sin(ph), 0.0)
        # inner wall down to the inner fillet
        ri = g['inner_fillet']
        bi = math.atan(float(self.slope(self.z_inner + ri)))
        czi = self.z_inner + ri
        zj_in = czi - ri * math.sin(bi)
        cri = float(self.r_in(zj_in)) - ri * math.cos(bi)
        ztop = zc + rho * math.sin(beta)
        s = np.linspace(0, 1, n(130) + 1)[1:]
        zs = ztop + (zj_in - ztop) * s
        add(self.r_in(zs), zs, 0.0)
        # inner fillet: -bi -> -90 deg
        ph = np.linspace(-bi, -math.pi / 2, n(18) + 1)[1:]
        add(cri + ri * np.cos(ph), czi + ri * np.sin(ph), 0.0)
        # inner bottom, r cri -> 0 (excluded)
        t = np.linspace(0, 1, n(30) + 1)[1:-1]
        add(cri * (1 - t), np.full_like(t, self.z_inner), 0.0)
        self.inner_fillet = (cri, czi, ri, bi)
        self.foot = (cr, fr, b0)
        return np.array(R), np.array(Z), np.array(W)

    def liquid(self, q=1.0):
        """Chai solid: bottom centre (excluded) -> out -> inner fillet -> up the wall -> meniscus -> top centre
        (excluded). Offset `overlap` into the glass. Returns r, z and the meniscus/top-surface helpers."""
        g = self.g
        ov = g['overlap']
        n = lambda k: max(4, int(round(k * q)))                # noqa: E731
        self.glass(q)                                          # sets inner_fillet
        cri, czi, ri, bi = self.inner_fillet
        m, lam = g['meniscus']
        zs = self.z_surface
        ztop = zs + m
        Rw = float(self.r_in(ztop)) + ov
        R, Z = [], []
        t = np.linspace(0, 1, n(30) + 1)[1:]
        R += (cri * t).tolist(); Z += [self.z_inner - ov] * len(t)
        ph = np.linspace(-math.pi / 2, -bi, n(18) + 1)[1:]
        R += (cri + (ri + ov) * np.cos(ph)).tolist(); Z += (czi + (ri + ov) * np.sin(ph)).tolist()
        z0 = czi - (ri + ov) * math.sin(bi)
        s = np.linspace(0, 1, n(110) + 1)[1:]
        zz = z0 + (ztop - z0) * s
        R += (self.r_in(zz) + ov).tolist(); Z += zz.tolist()
        # free surface: rho from Rw -> 0 (excluded), dense near the wall
        u = np.linspace(0, 1, n(60) + 1)[1:-1]
        rho = Rw * (1 - u ** 1.7)
        R += rho.tolist(); Z += self.surface_z(rho, Rw).tolist()
        self.Rw = Rw
        return np.array(R), np.array(Z)

    def surface_z(self, rho, Rw=None):
        m, lam = self.g['meniscus']
        Rw = self.Rw if Rw is None else Rw
        return self.z_surface + m * np.exp(-(Rw - np.asarray(rho, np.float64)) / lam)


def facet_factor(theta, n=None, soft=None):
    """Radius factor of 12 flats (circumradius 1; flats at cos(15 deg)) with smooth-min softened ridges.
    e.g. facet_factor(np.array([-pi/2])) -> [0.9659] (flat centre faces the camera)"""
    n = n or GEO['facets']
    soft = GEO['facet_soft'] if soft is None else soft
    per = 2 * math.pi / n
    d = np.mod(np.asarray(theta, np.float64) - THETA0 + per / 2, per) - per / 2
    c = math.cos(per / 2)
    ra = c / np.cos(d)
    rb = c / np.cos(per - np.abs(d))
    mn = np.minimum(ra, rb)
    return mn - soft * np.log(np.exp(-(ra - mn) / soft) + np.exp(-(rb - mn) / soft))


def lathe(R, Z, nseg, theta=None, start_pole=None, end_pole=None):
    """Surface of revolution. R, Z: (nprof,) or (nprof, nseg). Poles (z) close the ends with triangle fans.
    Returns V (N, 3) float64 and a list of faces (quads + triangles) with outward normals (profile traversed
    with the solid on its left, as Profile does)."""
    th = THETA0 + 2 * math.pi * np.arange(nseg) / nseg if theta is None else theta
    R = np.asarray(R, np.float64)
    Z = np.asarray(Z, np.float64)
    if R.ndim == 1:
        R = np.repeat(R[:, None], nseg, 1)
    if Z.ndim == 1:
        Z = np.repeat(Z[:, None], nseg, 1)
    npf = R.shape[0]
    V = np.stack([R * np.cos(th)[None], R * np.sin(th)[None], Z], -1).reshape(-1, 3)
    idx = np.arange(npf * nseg).reshape(npf, nseg)
    j1 = np.roll(np.arange(nseg), -1)
    a, b = idx[:-1], idx[:-1][:, j1]
    c, d = idx[1:][:, j1], idx[1:]
    quads = np.stack([a, b, c, d], -1).reshape(-1, 4)
    faces = [tuple(q) for q in quads.tolist()]
    extra = []
    if start_pole is not None:
        p = len(V) + len(extra)
        extra.append((0.0, 0.0, float(start_pole)))
        faces += [(p, int(idx[0, (j + 1) % nseg]), int(idx[0, j])) for j in range(nseg)]
    if end_pole is not None:
        p = len(V) + len(extra)
        extra.append((0.0, 0.0, float(end_pole)))
        faces += [(int(idx[-1, j]), int(idx[-1, (j + 1) % nseg]), p) for j in range(nseg)]
    if extra:
        V = np.concatenate([V, np.array(extra)])
    return V, faces


def mesh_stats(V, faces):
    """Closed-manifold check and signed volume (divergence theorem, fan triangulation)."""
    from collections import Counter
    cnt = Counter()
    vol = 0.0
    for f in faces:
        for i in range(len(f)):
            e = (f[i], f[(i + 1) % len(f)])
            cnt[(min(e), max(e))] += 1
        p0 = V[f[0]]
        for i in range(1, len(f) - 1):
            vol += np.dot(p0, np.cross(V[f[i]], V[f[i + 1]])) / 6.0
    bad = sum(1 for v in cnt.values() if v != 2)
    return dict(edges=len(cnt), non_manifold=bad, volume=vol)


def glass_mesh(q=1.0, nseg=None):
    P = Profile()
    R, Z, W = P.glass(q)
    nseg = nseg or int(round(720 * min(1.0, q * 1.25)) // 12 * 12)
    th = THETA0 + 2 * math.pi * np.arange(nseg) / nseg
    F = facet_factor(th)
    R2 = R[:, None] * (1 - W[:, None] * (1 - F[None, :]))
    V, faces = lathe(R2, Z, nseg, th, start_pole=GEO['punt'], end_pole=P.z_inner)
    return P, V, faces


def liquid_mesh(q=1.0, nseg=None):
    P = Profile()
    R, Z = P.liquid(q)
    nseg = nseg or int(round(360 * min(1.0, q * 1.25)))
    V, faces = lathe(R, Z, nseg, start_pole=P.z_inner - GEO['overlap'], end_pole=P.z_surface)
    return P, V, faces


def _smooth_noise(x, seed, freqs=(3, 5, 8, 13, 21)):
    """Periodic smooth noise in [-1, 1] over x in radians."""
    rng = np.random.default_rng(seed)
    acc = np.zeros_like(np.asarray(x, np.float64))
    tot = 0.0
    for f in freqs:
        a = 1.0 / math.sqrt(f)
        acc += a * np.sin(f * x + rng.uniform(0, 2 * math.pi))
        tot += a
    return acc / tot


def foam_mesh(q=1.0, nseg=None):
    """Irregular foam bank on the chai surface against the wall. Rows from the wall (u=0) to the inner
    edge (u=1); normals face up; the inner edge dips 0.12 mm under the chai surface (clean intersection)."""
    P = Profile()
    P.liquid(q)
    nseg = nseg or int(round(720 * min(1.0, q * 1.25)))
    th = THETA0 + 2 * math.pi * np.arange(nseg) / nseg
    w0, wn = GEO['foam_w']
    rho_e = P.Rw - (w0 + wn * _smooth_noise(th, 26))
    nu = max(8, int(round(28 * q)))
    u = np.linspace(0, 1, nu)[:, None]
    rho = P.Rw - u * (P.Rw - rho_e[None, :])
    v = 1 - u                                                # 0 at the inner edge, 1 at the wall
    bumps = 0.006 * _smooth_noise(th * 3 + 0.0, 7, freqs=(17, 29, 43))[None, :] * np.sin(np.pi * v) ** 2
    t = -0.012 + 0.066 * (1 - (1 - v) ** 3) + bumps
    Zf = P.surface_z(rho) + t
    V, faces = lathe(rho, Zf, nseg, th)
    return P, V, faces


# ============================================================================= Blender side

def _setup_scene(res, spp):
    bpy = H._bpy()
    sc = H.reset(res, spp, 'night')
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    c = sc.cycles
    c.film_transparent_glass = True
    c.film_transparent_roughness = 0.1
    c.max_bounces = 16
    c.diffuse_bounces = 3
    c.glossy_bounces = 8
    c.transmission_bounces = 16
    c.transparent_max_bounces = 16
    c.adaptive_threshold = 0.02
    c.sample_clamp_indirect = 6.0
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.seed = 26
    c.use_animated_seed = False
    im = sc.render.image_settings
    im.file_format = 'OPEN_EXR'
    im.color_mode = 'RGBA'
    im.color_depth = '32'
    im.exr_codec = 'ZIP'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    # world: #170A07 at 0.02
    w = bpy.data.worlds.new('W_inferno')
    sc.world = w
    nt = w.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    bg = nt.nodes.new('ShaderNodeBackground')
    wo = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(bg.outputs[0], wo.inputs['Surface'])
    bg.inputs['Color'].default_value = lin('NIGHT_1') + (1.0,)
    bg.inputs['Strength'].default_value = 0.02
    return sc


def _principled(name):
    bpy = H._bpy()
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    return m, nt.nodes['Principled BSDF'], nt


def m_glass():
    m, b, nt = _principled('pw_glass')
    b.inputs['Base Color'].default_value = glass_tint() + (1.0,)
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['IOR'].default_value = 1.50
    b.inputs['Roughness'].default_value = 0.04
    return m


CHAI_ALBEDO = (0.3791, 0.2476, 0.1368)   # linear, sRGB #A68867: calibrated (2 preview passes, frame 6, chai
# front-centre patch) so the 3200 K key-lit chai renders TOKENS["CHAI"] #A0582A (measured #A5582A -> #A0582A).
# A milky-tea albedo; the literal #A0582A under a 3200 K key renders #96370D (orange juice, not chai).


def chai_albedo():
    env = os.environ.get('PW3D_CHAI_ALBEDO')
    if env:
        return tuple(float(v) for v in env.split(','))
    return tuple(CHAI_ALBEDO) if CHAI_ALBEDO else lin('CHAI')


def m_chai():
    m, b, nt = _principled('pw_chai')
    b.inputs['Base Color'].default_value = chai_albedo() + (1.0,)
    b.inputs['Roughness'].default_value = 0.25
    b.inputs['IOR'].default_value = 1.34
    b.subsurface_method = 'RANDOM_WALK'
    b.inputs['Subsurface Weight'].default_value = 0.3
    b.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.25)    # cm (1 BU = 1 cm)
    b.inputs['Subsurface Scale'].default_value = 1.0
    return m


FOAM_ALBEDO = (0.70, 0.66, 0.44)   # linear, sRGB #DAD5B0 (cream milk foam): the literal #D9A06A under the warm
# key/top light rendered #D8743B (orange, no ring read); this albedo renders the ring close to TOKENS['FOAM'].


def m_foam():
    m, b, nt = _principled('pw_foam')
    b.inputs['Base Color'].default_value = tuple(FOAM_ALBEDO) + (1.0,)
    b.inputs['Roughness'].default_value = 0.6
    b.subsurface_method = 'RANDOM_WALK'
    b.inputs['Subsurface Weight'].default_value = 0.15
    b.inputs['Subsurface Radius'].default_value = (0.2, 0.12, 0.08)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 9.0
    nz.inputs['Detail'].default_value = 4.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.02
    nt.links.new(nz.outputs[0], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def add_mesh(name, V, faces, mat, parent):
    bpy = H._bpy()
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V.tolist()], [], faces)
    me.validate(verbose=False)
    me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    return o


def light(name, loc, size, irradiance, color, target, shape='DISK', temperature=None):
    """Area light for diffuse / subsurface only (never seen in glossy or transmission rays). `irradiance`
    in units of pi: a white Lambertian surface facing it renders `irradiance` (linear). Power = E * pi * d^2."""
    d = float(np.linalg.norm(np.asarray(loc) - np.asarray(target)))
    o = H.area(name, loc, size, irradiance * math.pi * math.pi * d * d, color, target=target, shape=shape,
               glossy=False, diffuse=True)
    o.visible_transmission = False
    o.visible_camera = False
    o.visible_volume_scatter = False
    if temperature:
        o.data.use_temperature = True
        o.data.temperature = temperature
    return o


def temp_rgb(kelvin):
    bpy = H._bpy()
    ld = bpy.data.lights.new('_tmp_t', 'AREA')
    ld.use_temperature = True
    ld.temperature = kelvin
    c = np.array(ld.temperature_color[:3], np.float64)
    bpy.data.lights.remove(ld)
    return tuple((c / c.max()).tolist())


RIG = dict(
    target=(0.0, 0.0, 4.5),
    # key: a tall soft box front-left (its lower half is what the near-vertical glass walls reflect)
    key=dict(dir=(-0.62, -0.62, 0.22), dist=45.0, size=(30.0, 60.0), E=1.0, kelvin=3200, card=10.0),
    fill=dict(dir=(0.78, -0.60, 0.10), dist=50.0, size=(26.0, 50.0), E=0.15, card=2.5, color=(1.0, 0.86, 0.72)),
    rim_l=dict(dir=(-0.86, 0.48, 0.16), dist=40.0, size=(9.0, 34.0), E=2.5, color='FLAME', card=1.6),
    rim_r=dict(dir=(0.86, 0.48, 0.16), dist=40.0, size=(9.0, 34.0), E=2.5, color='RED', card=1.6),
    top=dict(loc=(0.0, 1.5, 34.0), size=(30.0, 4.5), card=3.0, E=0.35),   # strip: lip line + lifts the chai top
)


def build_rig():
    tg = RIG['target']
    t = np.asarray(tg)

    def pos(d):
        v = np.asarray(d['dir'], np.float64)
        return tuple((t + v / np.linalg.norm(v) * d['dist']).tolist())

    L = {}
    k = RIG['key']
    warm = temp_rgb(k['kelvin'])
    L['key'] = light('key', pos(k), k['size'], k['E'], (1, 1, 1), tg, shape='RECTANGLE', temperature=k['kelvin'])
    L['key_card'] = H.card('key_card', pos(k), k['size'], warm, k['card'], target=tg, soft=0.22)
    f = RIG['fill']
    L['fill'] = light('fill', pos(f), f['size'], f['E'], f['color'], tg, shape='RECTANGLE')
    L['fill_card'] = H.card('fill_card', pos(f), f['size'], f['color'], f['card'], target=tg, soft=0.3)
    for side in ('rim_l', 'rim_r'):
        r = RIG[side]
        col = lin(r['color'])
        L[side] = light(side, pos(r), r['size'], r['E'], col, tg, shape='RECTANGLE')
        L[side + '_card'] = H.card(side + '_card', pos(r), r['size'], col, r['card'], target=tg, soft=0.3)
    tp = RIG['top']
    L['top_card'] = H.card('top_card', tp['loc'], tp['size'], (1.0, 0.93, 0.84), tp['card'],
                           target=(0.0, 0.0, 9.0), soft=0.35)
    L['top'] = light('top', tp['loc'], tp['size'], tp['E'], (1.0, 0.93, 0.84), (0.0, 0.0, 7.3), shape='RECTANGLE')
    return L


# ----------------------------------------------------------------------------- camera

CAM = dict(lens=85.0, elev=7.0, dist=90.0, fill=0.80, aim=(0.0, 0.0, 9.0))


def make_camera(points, res, cam=CAM):
    """85 mm, `elev` deg above the rim plane: the optical axis aims at the rim centre from `dist` cm; the
    sensor (vertical fit) and lens shift crop the frame so `points` fill `fill` of the height, centred."""
    bpy = H._bpy()
    from mathutils import Vector
    sc = bpy.context.scene
    W, Hh = res
    el = math.radians(cam['elev'])
    aim = np.asarray(cam['aim'], np.float64)
    cpos = aim + cam['dist'] * np.array([0.0, -math.cos(el), math.sin(el)])
    fwd = (aim - cpos) / np.linalg.norm(aim - cpos)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    rel = points - cpos
    zc = rel @ fwd
    xs, ys = (rel @ right) / zc, (rel @ up) / zc               # tan-space
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    aspect = W / Hh
    th_needed = max((y1 - y0) / cam['fill'], (x1 - x0) / (0.92 * aspect))   # full frame height, tan units
    sensor_h = th_needed * cam['lens']
    cd = bpy.data.cameras.new('pw_cam')
    cd.lens = cam['lens']
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = sensor_h
    cd.sensor_width = sensor_h * aspect
    # lens shift is in units of the fitted (vertical) frame dimension
    cd.shift_x = float((x0 + x1) / 2 / th_needed)
    cd.shift_y = float((y0 + y1) / 2 / th_needed)
    cd.clip_start = 1.0
    cd.clip_end = 1000.0
    o = bpy.data.objects.new('pw_cam', cd)
    sc.collection.objects.link(o)
    o.location = Vector(cpos.tolist())
    o.rotation_euler = Vector(fwd.tolist()).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o
    return o, dict(sensor_h_mm=round(sensor_h, 3), distance_cm=cam['dist'], lens_mm=cam['lens'],
                   elev_deg=cam['elev'], position_cm=[round(v, 3) for v in cpos.tolist()])


# ----------------------------------------------------------------------------- EXR -> PNG

def exr_to_png(exr, png):
    """Premultiplied linear float RGBA -> 8-bit straight-alpha sRGB PNG (Standard view: clip at 1).
    alpha' = max(alpha, max(rgb)) keeps glass highlights that are brighter than their coverage."""
    import cv2
    im = cv2.imread(exr, cv2.IMREAD_UNCHANGED)
    if im is None or im.ndim != 3 or im.shape[2] != 4:
        raise RuntimeError(f'bad EXR {exr}')
    p = np.clip(im[:, :, :3].astype(np.float64), 0.0, 1.0)      # BGR, premultiplied
    a = np.clip(im[:, :, 3].astype(np.float64), 0.0, 1.0)
    a2 = np.maximum(a, p.max(-1))
    s = np.where(a2[..., None] > 1e-6, p / np.maximum(a2[..., None], 1e-6), 0.0)
    out = np.dstack([l2s(np.clip(s, 0, 1)) * 255 + 0.5, a2[..., None] * 255 + 0.5]).clip(0, 255).astype(np.uint8)
    out[out[:, :, 3] == 0, :3] = 0
    if not cv2.imwrite(png, out, [cv2.IMWRITE_PNG_COMPRESSION, 6]):
        raise RuntimeError(f'could not write {png}')
    return dict(alpha_raised=float((a2 - a).max()), clipped=float((im[:, :, :3] > 1.0).mean()))


# ============================================================================= asset registry

YAW_RANGE = (-6.0, 6.0)
YAW_N = 13


def yaw_of(i, n=YAW_N):
    return YAW_RANGE[0] + (YAW_RANGE[1] - YAW_RANGE[0]) * i / (n - 1)


ASSETS = {
    'pw_chai_glass': dict(variants=('inferno',), modes=('yaw',), size=(960, 1280), frames=YAW_N,
                          notes='cutting-chai glass with milky chai (Ubaal Chai ad hero, reel C26 pehle_wala); '
                                'transparent glass (film_transparent_glass), 12 flats, foam ring; inferno rig: '
                                '3200 K key top-left-front, FLAME rim left, RED rim right; 85 mm, 7 deg above '
                                'the rim plane, 0.9 m'),
}


def folder_of(variant, mode):
    return f'{variant}_{mode}'


def _ensure_link(name):
    """<WS>/pehle_wala/assets3d/<name> -> ../props/<name> (the brief's S3 root; one copy on disk)."""
    os.makedirs(ASSETS_ROOT, exist_ok=True)
    link = os.path.join(ASSETS_ROOT, name)
    tgt = os.path.join('..', 'props', name)
    if os.path.islink(link):
        if os.readlink(link) != tgt:
            os.remove(link)
            os.symlink(tgt, link)
    elif not os.path.exists(link):
        os.symlink(tgt, link)
    else:
        print(f'[pw3d] WARNING {link} is a real folder; S3 root {ASSETS_ROOT} will not see the props/ finals')


def render_glass(variant='inferno', mode='yaw', preview=False, frames=None, samples=None, full=False):
    """full=True with preview=True: final resolution / samples / mesh quality, written to the preview folder
    (a look or timing test that never touches the finals)."""
    bpy = H._bpy()
    spec = ASSETS['pw_chai_glass']
    W, Hh = spec['size']
    lo = preview and not full
    res = (W // 2, Hh // 2) if lo else (W, Hh)
    spp = samples or (PREVIEW_SAMPLES if lo else SAMPLES)
    q = 0.6 if lo else 1.0
    t0 = time.time()
    sc = _setup_scene(res, spp)
    root = H.empty('pw_root')
    Pg, Vg, Fg = glass_mesh(q)
    _, Vl, Fl = liquid_mesh(q)
    _, Vf, Ff = foam_mesh(q)
    og = add_mesh('pw_glass', Vg, Fg, m_glass(), root)
    og.visible_shadow = False
    add_mesh('pw_chai', Vl, Fl, m_chai(), root)
    add_mesh('pw_foam', Vf, Ff, m_foam(), root)
    build_rig()
    # one camera for the union of every yaw pose
    pts = []
    sub = Vg[::7]
    for i in range(YAW_N):
        a = math.radians(yaw_of(i))
        Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        pts.append(sub @ Rz.T)
    cam, caminfo = make_camera(np.concatenate(pts), res)
    vl = bpy.context.view_layer
    vl.update()
    print(f'[pw_chai_glass/{variant}] scene built in {time.time() - t0:.1f}s, {spp} spp, {res[0]}x{res[1]}, '
          f'glass {len(Vg)} v, chai {len(Vl)} v, foam {len(Vf)} v, device {sc.cycles.device}, '
          f'threads {sc.render.threads}', flush=True)
    folder = folder_of(variant, mode)
    outdir = os.path.join(PREVIEW if preview else PROPS, 'pw_chai_glass', folder)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    meta_p = os.path.join(outdir, 'meta.json')
    if os.path.exists(meta_p):
        os.remove(meta_p)                        # meta.json is written LAST
    if not preview:
        _ensure_link('pw_chai_glass')
    n = YAW_N
    idx = list(frames) if frames else ([0, n // 2, n - 1] if preview else list(range(n)))
    idx = [i for i in idx if 0 <= i < n]
    t1 = time.time()
    conv = {}
    for k, i in enumerate(idx):
        root.rotation_euler = (0.0, 0.0, math.radians(yaw_of(i)))
        vl.update()
        p = os.path.join(outdir, f'{i:04d}.png')
        if os.environ.get('SKIP_EXISTING') and os.path.exists(p) and not preview:
            continue
        exr = os.path.join(TMP, f'pw_chai_glass_{folder}_{i:04d}{"_pv" if preview else ""}.exr')
        sc.render.filepath = exr
        bpy.ops.render.render(write_still=True)
        conv[i] = exr_to_png(exr, p)
        os.remove(exr)
        el = time.time() - t1
        print(f'  pw_chai_glass/{folder} frame {i} yaw {yaw_of(i):+.1f} ({k + 1}/{len(idx)}) '
              f'{el / (k + 1):.1f}s/frame  alpha_raise {conv[i]["alpha_raised"]:.3f}', flush=True)
    # features (on the rotation axis or the lip circle; yaw-invariant up to the facets)
    rc, zc, rho, beta = Pg.bead
    zt = GEO['height']
    feats_w = {
        'base': (0.0, 0.0, 0.0), 'rim': (0.0, 0.0, zt), 'surface': (0.0, 0.0, Pg.z_surface),
        'rim_front': (0.0, -rc, zt), 'rim_back': (0.0, rc, zt), 'rim_left': (-Pg.lip_r, 0.0, zc),
        'rim_right': (Pg.lip_r, 0.0, zc), 'base_front': (0.0, -Pg.rb, 0.0),
    }
    root.rotation_euler = (0.0, 0.0, 0.0)
    vl.update()
    feats = {kk: H.project_px(v) for kk, v in feats_w.items()}
    px_cm = (H.project_px((0.0, 0.0, zt))[1] - H.project_px((0.0, 0.0, zt - 1.0))[1]) * -1
    pngs = [os.path.join(outdir, f'{i:04d}.png') for i in range(n)]
    complete = all(os.path.exists(p) for p in pngs)
    if preview or complete:
        bb, _ = H._alpha_stats([p for p in pngs if os.path.exists(p)])
        meta = dict(name='pw_chai_glass', variant=folder, mode=mode, frames=n, fps_hint=30,
                    yaw_range=list(YAW_RANGE), size=[res[0], res[1]], loop=False, axis='z',
                    notes=spec['notes'], samples=spp, preview=bool(preview),
                    anchor=feats['base'], pivot=feats['base'], features=feats,
                    px_per_cm_at_axis=round(abs(px_cm), 2),
                    glass_height_px=round(feats['base'][1] - (bb[1] if bb else 0), 1),
                    camera=caminfo, units='cm', reel=REEL, device=sc.cycles.device,
                    alpha_encoding='straight; alpha = max(alpha, max(rgb)) from the premultiplied EXR',
                    glass_tint=hexs(glass_tint()), geometry={kk: v for kk, v in GEO.items()})
        if not preview:
            meta['render_seconds'] = round(time.time() - t1, 1)
        meta = H.write_meta(outdir, **meta)
        print(f'  -> {outdir} ({len(idx)} frames, {time.time() - t1:.0f}s) meta written', flush=True)
    else:
        print(f'  -> {outdir}: incomplete ({sum(map(os.path.exists, pngs))}/{n}); meta.json NOT written',
              flush=True)
    return outdir


# ============================================================================= sheets and checks

def _bg(h, w, kind):
    if kind == 'black':
        img = np.zeros((h, w, 3), np.float32)
    elif kind == 'flame':
        img = np.broadcast_to(np.array(lin('FLAME'), np.float32), (h, w, 3)).copy()
    elif kind == 'cream':
        img = np.broadcast_to(np.array(lin('IVORY'), np.float32) * 0.8, (h, w, 3)).copy()
    else:                                                     # 'plate': the v1 ad plate (BRIEF 5.2), 840x760
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        img = np.array(lin('NIGHT_1'), np.float32) * (1 - yy) + np.array(lin('NIGHT_0'), np.float32) * yy
        img = np.broadcast_to(img, (h, w, 3)).copy()
    return img


def _radial_add(img, cx, cy, size, color, power=2.0):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (size / 2)
    a = np.clip(1 - r, 0, 1) ** power
    img += a[..., None] * np.asarray(color, np.float32)
    return img


def ad_plate(kind='plate'):
    """840x760 ad canvas (ad-local = screen - (120, 468)) as in BRIEF 5.2: v1 plate or cream gag (v6-v12),
    ember backlight at screen (515, 980), contact shadow 300x40 at (515, 1212) x0.6."""
    h, w = 760, 840
    img = _bg(h, w, 'plate' if kind == 'plate' else 'cream')
    if kind == 'plate':
        _radial_add(img, 515 - 120, 980 - 468, 900, np.array(lin('EMBER')) * 0.9)
        _radial_add(img, 515 - 120, 980 - 468, 420, np.array(lin('FLAME')) * 0.6)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    e = ((xx - (515 - 120)) / 150) ** 2 + ((yy - (1212 - 468)) / 20) ** 2
    sh = np.clip(1 - e, 0, 1) ** 1.5 * 0.6
    img *= (1 - sh)[..., None]
    return img


def composite_in_ad(png, kind='plate', height_px=440, meta=None):
    """Place the sprite like pehle_wala.py will: base centre at screen (515, 1210), 440 px from base centre
    to the top of the glass. Returns the 840x760 ad canvas as sRGB uint8."""
    import cv2
    sys.path.insert(0, HERE)
    import sprites3d as S3
    spr = S3.decode_png(png)
    meta = meta or {}
    base = meta.get('features', {}).get('base', [spr.shape[1] / 2, spr.shape[0]])
    gh = meta.get('glass_height_px') or spr.shape[0]
    k = height_px / gh
    spr_s = cv2.resize(spr, (int(round(spr.shape[1] * k)), int(round(spr.shape[0] * k))),
                       interpolation=cv2.INTER_AREA)
    img = ad_plate(kind)
    dst = np.dstack([img, np.ones(img.shape[:2] + (1,), np.float32)])
    S3.over(dst, spr_s, 515 - 120, 1210 - 468, anchor=(base[0] * k, base[1] * k))
    return S3.to_srgb8(dst)


def _label(img, text):
    import cv2
    cv2.putText(img, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(img, text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 1, cv2.LINE_AA)
    return img


def make_sheets(preview=False):
    """Sheets (sRGB jpg/png) in props/sheets/: frames over black and FLAME; mid frame full size over black and
    FLAME; 440 px composites on the v1 plate and the cream gag."""
    import cv2
    sys.path.insert(0, HERE)
    import sprites3d as S3
    root = os.path.join(PREVIEW if preview else PROPS, 'pw_chai_glass', 'inferno_yaw')
    tag = 'preview' if preview else 'final'
    os.makedirs(SHEETS, exist_ok=True)
    pngs = sorted(f for f in os.listdir(root) if f.endswith('.png'))
    meta = json.load(open(os.path.join(root, 'meta.json'))) if os.path.exists(os.path.join(root, 'meta.json')) else {}
    out = []
    # 1. every frame over black / FLAME (cells 240 wide)
    rows = []
    for kind in ('black', 'flame'):
        cells = []
        for f in pngs:
            spr = S3.decode_png(os.path.join(root, f))
            h, w = spr.shape[:2]
            bg = np.dstack([_bg(h, w, kind), np.ones((h, w, 1), np.float32)])
            S3.over(bg, spr, 0, 0)
            c = cv2.resize(S3.to_srgb8(bg), (240, int(240 * h / w)), interpolation=cv2.INTER_AREA)
            cells.append(_label(c[:, :, ::-1].copy(), f'{f[:4]} {kind}'))
        rows.append(np.concatenate(cells, 1))
    p = os.path.join(SHEETS, f'pw_chai_glass_{tag}_frames.jpg')
    cv2.imwrite(p, np.concatenate(rows, 0), [cv2.IMWRITE_JPEG_QUALITY, 92])
    out.append(p)
    # 2. mid frame full size over black and FLAME
    mid = pngs[len(pngs) // 2]
    spr = S3.decode_png(os.path.join(root, mid))
    h, w = spr.shape[:2]
    pair = []
    for kind in ('black', 'flame'):
        bg = np.dstack([_bg(h, w, kind), np.ones((h, w, 1), np.float32)])
        S3.over(bg, spr, 0, 0)
        pair.append(S3.to_srgb8(bg)[:, :, ::-1])
    p = os.path.join(SHEETS, f'pw_chai_glass_{tag}_mid_black_flame.png')
    cv2.imwrite(p, np.concatenate(pair, 1))
    out.append(p)
    # 3. 440 px composites in the ad (v1 plate, cream gag), frames first / mid / last
    comps = []
    for kind in ('plate', 'cream'):
        row = [composite_in_ad(os.path.join(root, f), kind, meta=meta)[:, :, ::-1] for f in
               (pngs[0], mid, pngs[-1])]
        comps.append(np.concatenate(row, 1))
    p = os.path.join(SHEETS, f'pw_chai_glass_{tag}_ad440.jpg')
    cv2.imwrite(p, np.concatenate(comps, 0), [cv2.IMWRITE_JPEG_QUALITY, 92])
    out.append(p)
    for q in out:
        print(q)
    return out


# ----------------------------------------------------------------------------- selftest

def selftest():
    ok = True

    def check(name, cond, val=''):
        nonlocal ok
        ok &= bool(cond)
        print(f'  [{"ok" if cond else "FAIL"}] {name} {val}')

    P = Profile()
    R, Z, W = P.glass(1.0)
    check('height 9.0 cm', abs(Z.max() - 9.0) < 1e-3, f'{Z.max():.4f}')
    check('lip diameter 6.6 cm', abs(2 * P.lip_r - 6.6) < 1e-3, f'{2 * P.lip_r:.4f}')
    check('base diameter 5.2 cm (wall extrapolated to z 0)', abs(2 * float(P.r_out(0)) - 5.2) < 1e-6,
          f'{2 * float(P.r_out(0)):.4f}')
    check('inner bottom at 1.2 cm', abs(P.z_inner - 1.2) < 1e-9)
    zt = np.linspace(2, 8, 7)
    wall = P.r_out(zt) - P.r_in(zt)
    check('wall 3.5 mm (smooth band / ridge)', np.allclose(wall, 0.35), f'{wall.min():.3f}')
    th = THETA0 + 2 * math.pi * np.arange(1440) / 1440
    F = facet_factor(th)
    mins = np.sum((F < np.roll(F, 1)) & (F <= np.roll(F, -1)))
    check('12 flats (flat centres = local minima)', mins == 12, f'{mins}')
    maxs = np.sum((F > np.roll(F, 1)) & (F >= np.roll(F, -1)))
    check('12 ridges', maxs == 12, f'{maxs}')
    flat_wall = float(P.r_out(3.0)) * F.min() - float(P.r_in(3.0))
    check('wall at a flat centre >= 2.4 mm', flat_wall >= 0.24, f'{flat_wall * 10:.2f} mm')
    check('fill 78 %', abs((P.z_surface - 1.2) / 7.8 - 0.78) < 1e-9, f'surface z {P.z_surface:.3f}')
    check('flat faces the camera at yaw 0', abs(facet_factor(np.array([THETA0]))[0] - math.cos(math.pi / 12)) < 1e-3)
    for nm, fn in (('glass', glass_mesh), ('chai', liquid_mesh)):
        _, V, Fc = fn(0.5)
        st = mesh_stats(V, Fc)
        check(f'{nm} mesh closed manifold', st['non_manifold'] == 0, f"{st['edges']} edges")
        check(f'{nm} volume positive (outward normals)', st['volume'] > 0, f"{st['volume']:.2f} cm3")
    _, Vl, _ = liquid_mesh(0.5)
    rl = np.hypot(Vl[:, 0], Vl[:, 1])
    lim = P.r_in(np.clip(Vl[:, 2], 1.2, 9)) + GEO['overlap']
    exc = float((rl - lim).max())
    check('chai stays inside the cavity (+overlap, 1 um tolerance)', exc < 1e-4, f'max excess {exc * 1e4:.2f} um')
    check('chai volume (ml)', True, f"{mesh_stats(*liquid_mesh(1.0)[1:])['volume']:.1f}")
    # finals, when present
    root = os.path.join(PROPS, 'pw_chai_glass', 'inferno_yaw')
    if os.path.isdir(root):
        import cv2
        pngs = sorted(f for f in os.listdir(root) if f.endswith('.png'))
        check('13 frames', len(pngs) == 13, f'{len(pngs)}')
        for f in pngs:
            im = cv2.imread(os.path.join(root, f), cv2.IMREAD_UNCHANGED)
            check(f'{f} uint8 RGBA 960x1280', im is not None and im.dtype == np.uint8 and im.shape == (1280, 960, 4))
        mp = os.path.join(root, 'meta.json')
        check('meta.json present', os.path.exists(mp))
        if os.path.exists(mp):
            m = json.load(open(mp))
            check('meta yaw_range [-6, 6], 13 frames, mode yaw',
                  m.get('yaw_range') == [-6.0, 6.0] and m.get('frames') == 13 and m.get('mode') == 'yaw')
            check('anchor == features.base', m.get('anchor') == m.get('features', {}).get('base'))
        try:
            sys.path.insert(0, HERE)
            import sprites3d as S3
            a = S3.Asset3D('pw_chai_glass', 'inferno', mode='yaw', root=ASSETS_ROOT)
            check('S3.Asset3D loads via the brief root', a.n == 13 and a.folder == 'inferno_yaw',
                  f'{a.folder} n={a.n}')
            img = a.at_yaw(2.5, interp='flow')
            check('at_yaw(2.5, flow) shape', img.shape == (1280, 960, 4))
        except Exception as e:  # noqa: BLE001
            check('S3.Asset3D load', False, repr(e))
    print('selftest', 'PASSED' if ok else 'FAILED')
    return ok


# ============================================================================= CLI

def _parse(argv):
    a = dict(names=[], preview=False, variant='inferno', mode='yaw', frames=None, samples=None, full=False)
    i = 0
    while i < len(argv):
        x = argv[i]
        if x == '--preview':
            a['preview'] = True
        elif x == '--full':
            a['full'] = True
        elif x == '--variant':
            a['variant'] = argv[i + 1]; i += 1
        elif x == '--mode':
            a['mode'] = argv[i + 1]; i += 1
        elif x == '--frames':
            a['frames'] = [int(v) for v in argv[i + 1].split(',') if v.strip()]; i += 1
        elif x == '--samples':
            a['samples'] = int(argv[i + 1]); i += 1
        else:
            a['names'].append(x)
        i += 1
    return a


def main(argv):
    a = _parse(argv)
    if not a['names']:
        print(__doc__)
        return 0
    cmd = a['names'][0]
    if cmd == 'selftest':
        return 0 if selftest() else 1
    if cmd == 'sheet':
        make_sheets(False)
        return 0
    if cmd == 'previewsheet':
        make_sheets(True)
        return 0
    names = list(ASSETS) if cmd == 'all' else a['names']
    for nm in names:
        if nm not in ASSETS:
            raise SystemExit(f'unknown asset {nm!r}; have {list(ASSETS)}')
        if a['variant'] not in ASSETS[nm]['variants'] or a['mode'] not in ASSETS[nm]['modes']:
            raise SystemExit(f'{nm}: variant/mode must be {ASSETS[nm]["variants"]} / {ASSETS[nm]["modes"]}')
        render_glass(a['variant'], a['mode'], preview=a['preview'] or a['full'], frames=a['frames'],
                     samples=a['samples'], full=a['full'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
