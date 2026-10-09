"""assets3d_household.py - glossy household / everyday-essentials props for anim #4 ("£447.60: but what is it for?").

Same studio look as assets3d_icons.py (it is imported and reused: SDF toolkit, surface-nets mesher, candy /
gold materials, the 'day' ivory world, the key/fill/rim rig with reflection cards, the 80 mm camera 5 deg
above the subject, render loop and meta writer). Every prop is a soft rounded, generously bevelled,
clear-coated candy-plastic toy in the brand palette.

CLI
---
    python3 assets3d_household.py <name> [<name> ...] [--variant day|day_full] [--preview] [--frames 0,16,32]
                                  [--samples N] [--size N]
    python3 assets3d_household.py all            # every asset / variant (priority order)
    python3 assets3d_household.py sheet          # contact sheet of the finals (incl. the icons day set used
                                                 # by anim #4) -> out/selftest/assets3d_household_contact.png
    python3 assets3d_household.py previewsheet   # sheet of the --preview renders -> out/preview3d/household_preview.png

    --preview   16 spp, half resolution, frames first/mid/last -> workspace3/out/preview3d/<name>/<variant>/
    env HH_SAMPLES (default 64, adaptive + OpenImageDenoise, fixed seed), HH_THREADS (default 2),
    HH_SIZE (default 640), SKIP_EXISTING=1 resumes a sequence.

Assets (all 'day'; mode yaw, 33 frames, yaw -40..+40 deg; 640x640)
---------------------------------------------------------------
    basket        day        rounded ORANGE shopping basket (slotted walls, rolled rim), MAGENTA arch handle
                  day_full   the same basket (identical camera / pixels) filled with an apple, a bread loaf,
                             a LEAF-banded carton and a banana -> cross-fade day -> day_full for "fills up".
                             feature 'mouth' (centre of the basket opening, per frame) for items dropping in.
    apple         glossy red-orange apple, brown stem, LEAF-green leaf
    sandwich      triangle sandwich (crumb + golden crust), LEAF lettuce frill, red tomato slices
    plate         ivory plate with a MAGENTA rim line: golden drumstick, LEAF broccoli, ORANGE carrot coins
    bed           single bed: ivory frame, white mattress + pillow, MAGENTA duvet with a LAVENDER turn-down
    tshirt        MAGENTA tee with a ribbed collar and a small raised ORANGE heart print
    trainer       white sneaker with ORANGE toe cap, heel counter, pull tab, laces and outsole
    football      classic truncated-icosahedron ball: ivory hexagons, PLUM pentagons, soft seams
    paint_palette ivory palette with ORANGE / MAGENTA / LEAF / AMBER paint dabs and a PLUM brush (gold ferrule,
                  MAGENTA-dipped bristles)

    Some props are tilted towards the camera before the yaw sweep (a turntable seen from slightly above),
    so plates / baskets / beds show their tops: meta 'tilt_deg'. 'base_yaw_deg' is the resting 3/4 turn
    baked into yaw 0.

Output (shared 3D asset spec, see assets3d_icons.py)
----------------------------------------------------
    workspace3/assets3d/<name>/<variant>/0000.png ... 0032.png   RGBA 8-bit, straight alpha, sRGB 'Standard'
    workspace3/assets3d/<name>/<variant>/meta.json   written LAST, only once every frame is on disk:
        {name, variant, mode 'yaw', frames 33, fps_hint, yaw_range [-40, 40], size, anchor, bbox, ground_y,
         pivot, axis, loop false, notes, samples, tilt_deg, base_yaw_deg, features, features_per_frame}
    frame i shows yaw = -40 + 80 * i / 32 deg; positive yaw turns the front towards screen-right.

Load with sprites3d:  S3.get('basket', 'day_full'); S3.get('apple', 'day').at_yaw(0)
"""
import os
import sys
import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import assets3d_icons as I                                     # noqa: E402
from assets3d_icons import (hexlin, mixlin, sd_circle, sd_rbox, sd_segment, sd_polyline, sd_poly_exact,   # noqa: E402
                            op_union, op_sub, op_smin, op_offset, op_xform, Raster2D, sd_heart, inflate,
                            sd3_round_box, sd3_sphere, sd3_capsule, sd3_torus, extrude_axis, u_min, u_smin,
                            u_ssub, u_isect, u_sisect, u_xform, fn_sd, poly_sd, R)

OUT3D = I.OUT3D
PREVIEW3D = I.PREVIEW3D
SELFTEST = I.SELFTEST
SAMPLES = int(os.environ.get('HH_SAMPLES', '64'))
THREADS = int(os.environ.get('HH_THREADS', '2'))
SIZE = int(os.environ.get('HH_SIZE', '640'))
YAW_FRAMES = 33
YAW_RANGE = (-40.0, 40.0)
FILL = 0.80
RIM = 0.25            # day-variant fresnel rim glow strength (icons use 0.25-0.4 on day)


# ============================================================================= small helpers

def bc(f):
    """2D sd that broadcasts its arguments first (Raster2D samplers need equal shapes)."""
    return lambda a, b: f(*np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float)))


def smooth01(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def sstep(e0, e1, x):
    return smooth01((np.asarray(x, float) - e0) / (e1 - e0))


def rounded_extrude(d2, w, edge):
    """Combine an in-plane distance d2 and an out-of-plane slab distance w (|.| - half already applied,
    i.e. w = |h| - half) into a rounded-edge solid (edge radius `edge`)."""
    wx = d2 + edge
    wy = w + edge
    return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx, 0), np.maximum(wy, 0)) - edge


def sd3_ellipsoid(c, r):
    """Approximate ellipsoid distance (good near the surface)."""
    def F(x, y, z):
        px, py, pz = (x - c[0]) / r[0], (y - c[1]) / r[1], (z - c[2]) / r[2]
        k0 = np.sqrt(px * px + py * py + pz * pz)
        k1 = np.sqrt((px / r[0]) ** 2 + (py / r[1]) ** 2 + (pz / r[2]) ** 2)
        return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)
    return F


def sd3_round_cone(a, b, r1, r2):
    """Exact round cone between points a (radius r1) and b (radius r2) (Inigo Quilez)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ba = b - a
    l2 = float(ba @ ba)
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2

    def F(x, y, z):
        px, py, pz = x - a[0], y - a[1], z - a[2]
        yy = px * ba[0] + py * ba[1] + pz * ba[2]
        zz = yy - l2
        qx, qy, qz = px * l2 - ba[0] * yy, py * l2 - ba[1] * yy, pz * l2 - ba[2] * yy
        x2 = qx * qx + qy * qy + qz * qz
        y2 = yy * yy * l2
        z2 = zz * zz * l2
        k = np.sign(rr) * rr * rr * x2
        d_b = np.sqrt(x2 + z2) * il2 - r2
        d_a = np.sqrt(x2 + y2) * il2 - r1
        d_m = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + yy * rr) * il2 - r1
        return np.where(np.sign(zz) * a2 * z2 > k, d_b, np.where(np.sign(yy) * a2 * y2 < k, d_a, d_m))
    return F


def sd3_round_cyl(a, b, r, e):
    """Rounded cylinder from a to b, radius r, edge radius e."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    d = d / L

    def F(x, y, z):
        px, py, pz = x - a[0], y - a[1], z - a[2]
        h = px * d[0] + py * d[1] + pz * d[2]
        rad = np.sqrt(np.maximum(px * px + py * py + pz * pz - h * h, 0))
        return rounded_extrude(rad - r, np.abs(h - L / 2) - L / 2, e)
    return F


def blockwise(fn, block=150000):
    """Evaluate an implicit in blocks of points (for fields that build big per-point temporaries)."""
    def G(x, y, z):
        x, y, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float))
        shp = x.shape
        xf, yf, zf = x.ravel(), y.ravel(), z.ravel()
        out = np.empty(xf.shape)
        for i in range(0, len(xf), block):
            out[i:i + block] = fn(xf[i:i + block], yf[i:i + block], zf[i:i + block])
        return out.reshape(shp)
    return G


def u_frame(F, origin, R3):
    """Place an implicit defined in a local frame: columns of R3 = local axes in parent space."""
    R3 = np.asarray(R3, float)
    o = np.asarray(origin, float)

    def G(x, y, z):
        px, py, pz = x - o[0], y - o[1], z - o[2]
        return F(R3[0, 0] * px + R3[1, 0] * py + R3[2, 0] * pz,
                 R3[0, 1] * px + R3[1, 1] * py + R3[2, 1] * pz,
                 R3[0, 2] * px + R3[1, 2] * py + R3[2, 2] * pz)
    return G


def rot3(rx=0.0, ry=0.0, rz=0.0):
    """Rz @ Ry @ Rx (radians) - same convention as u_xform."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def obj(name, F, bounds, res, mat, parent, icon=False, shadow=True):
    return I.sdf_object(name, F, bounds, res, mat, parent, icon_frame=icon, shadow=shadow)


def set_attr(o, name, fn, icon=False):
    """Per-vertex float attribute (0..1) from fn(x, y, z) in the implicit's own coordinates."""
    me = o.data
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get('co', co)
    V = co.reshape(-1, 3).astype(np.float64)
    if icon:      # blender (X, Y, Z) = (x, -z, y)
        x, y, z = V[:, 0], V[:, 2], -V[:, 1]
    else:
        x, y, z = V[:, 0], V[:, 1], V[:, 2]
    vals = np.clip(np.asarray(fn(x, y, z), np.float64), 0, 1).astype(np.float32)
    a = me.attributes.new(name, 'FLOAT', 'POINT')
    a.data.foreach_set('value', vals)
    return vals


def _lin(c):
    return hexlin(c) if isinstance(c, str) else tuple(c)


def m_layers(name, base, layers, **kw):
    """Candy material whose base colour is `base` overlaid by [(attribute_name, colour), ...] in order
    (each attribute is a 0..1 per-vertex mask written by set_attr)."""
    m = I.m_candy(name, base, **kw)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    prev = None
    for attr, col in layers:
        at = nt.nodes.new('ShaderNodeAttribute')
        at.attribute_type = 'GEOMETRY'
        at.attribute_name = attr
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        if prev is None:
            if b.inputs['Base Color'].is_linked:     # keep a gradient that m_candy built
                nt.links.new(b.inputs['Base Color'].links[0].from_socket, mix.inputs['A'])
            else:
                mix.inputs['A'].default_value = _lin(base) + (1,)
        else:
            nt.links.new(prev.outputs['Result'], mix.inputs['A'])
        mix.inputs['B'].default_value = _lin(col) + (1,)
        nt.links.new(at.outputs['Fac'], mix.inputs['Factor'])
        prev = mix
    if prev is not None:
        nt.links.new(prev.outputs['Result'], b.inputs['Base Color'])
    return m


def candy(name, color, rim=None, rim_str=RIM, **kw):
    kw.setdefault('rough', 0.28)
    kw.setdefault('coat_r', 0.035)
    return I.m_candy(name, color, rim_glow=rim, rim_str=rim_str if rim else 0.0, **kw)


def vesica(L, w):
    """2D leaf (intersection of two circles) from (0, 0) to (L, 0), half width w."""
    rho = (L * L / 4 + w * w) / (2 * w)
    c1 = sd_circle(L / 2, -(rho - w), rho)
    c2 = sd_circle(L / 2, rho - w, rho)
    return lambda x, y: np.maximum(c1(x, y), c2(x, y))


# ============================================================================= asset registry

ASSETS = {}


class Spec:
    def __init__(self, fn, variants, tilt, base_yaw, notes, size=None, priority=9):
        self.fn, self.variants, self.tilt, self.base_yaw = fn, tuple(variants), tilt, base_yaw
        self.notes, self.size, self.priority = notes, size, priority


def asset(name, variants=('day',), tilt=0.0, base_yaw=0.0, notes='', size=None, priority=9):
    def deco(fn):
        ASSETS[name] = Spec(fn, variants, tilt, base_yaw, notes, size, priority)
        return fn
    return deco


# ============================================================================= apple (also used in the basket)

def make_apple(parent, q, c=(0.0, 0.0, 0.0), s=1.0, rz=0.0, tag='apple', res=230):
    c = np.asarray(c, float)

    def body0(x, y, z):
        r = np.hypot(x, y)
        k = 1.0 + 0.10 * np.clip(z / 0.85, -1, 1)
        zz = z * 1.05
        return (np.sqrt((r / k) ** 2 + zz ** 2) - 0.85) * 0.96
    body = u_ssub(body0, sd3_sphere((0, 0, 0.93), 0.26), 0.17)
    body = u_ssub(body, sd3_sphere((0, 0, -0.92), 0.15), 0.11)
    pl = lambda F: u_xform(F, t=tuple(c), rz=rz, s=s)
    b = 1.0 * s
    bounds = (tuple(c - [1.25 * b, 1.25 * b, 0.95 * b]), tuple(c + [1.25 * b, 1.25 * b, 0.95 * b]))
    z0, z1 = c[2] - 0.8 * s, c[2] + 0.8 * s
    mat = candy(f'{tag}_skin', mixlin('#F24A1C', 'ORANGE', 0.72), rim='AMBER', rim_str=0.25, rough=0.24,
                coat_r=0.03, sss=0.12, sss_radius=(1.0, 0.3, 0.2), sss_scale=0.05, grad=('#E8382A', z0, z1))
    obj(f'{tag}_body', pl(body), bounds, R(q, res), mat, parent)
    stem = u_smin(sd3_capsule((0, 0, 0.62), (0.025, 0, 0.84), 0.045), sd3_capsule((0.025, 0, 0.84), (0.10, 0, 1.0), 0.04),
                  0.02)
    ms = candy(f'{tag}_stem', '#7A4322', rough=0.38)
    obj(f'{tag}_stem', pl(stem), (tuple(c + s * np.array([-0.4, -0.4, 0.5])), tuple(c + s * np.array([0.4, 0.4, 1.12]))),
        R(q, 90), ms, parent)
    L, w = 0.62, 0.17
    lf2 = fn_sd(vesica(L, w), (-0.05, -0.3, 0.7, 0.3), 700)
    P = lf2.poisson(200)
    leaf0 = inflate(lf2, thick=0.026, edge=0.024, dome=0.025, dome_field=P, dome_pow=0.6)
    bend = lambda u: 0.16 * (np.clip(u, 0, None) / L) ** 2          # tip curls up out of the plane
    leaf1 = lambda x, y, z: leaf0(x, y, z - bend(x))
    leaf = u_xform(leaf1, t=(0.04, 0.0, 0.83), rx=math.radians(80), ry=math.radians(-28), rz=math.radians(12))
    ml = candy(f'{tag}_leaf', 'LEAF', rim='LEAF_HI', rim_str=0.2, grad=('LEAF_HI', 0.75, 1.15))
    obj(f'{tag}_leaf', pl(leaf), (tuple(c + s * np.array([-0.45, -0.75, 0.45])), tuple(c + s * np.array([0.85, 0.75, 1.35]))),
        R(q, 160), ml, parent)


@asset('apple', tilt=6.0, notes='glossy red-orange apple, brown stem, LEAF-green leaf', priority=3)
def build_apple(root, variant, q):
    make_apple(root, q)
    return {'features': {'top': (0.0, 0.0, 0.85)}}


# ============================================================================= basket

BZ0, BZ1 = -0.55, 0.35          # basket floor / rim height
BHX, BHY = (0.80, 1.00), (0.46, 0.60)   # half sizes at the floor and at the rim
BRR = 0.26
BWALL = 0.075


def _plan_rr(x, y, hx, hy, rr):
    qx = np.abs(x) - hx + rr
    qy = np.abs(y) - hy + rr
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - rr


def _basket_solid(inset=0.0, floor=BZ0, tmax=1.0):
    def F(x, y, z):
        t = np.clip((z - BZ0) / (BZ1 - BZ0), 0, tmax)
        hx = BHX[0] + (BHX[1] - BHX[0]) * t - inset
        hy = BHY[0] + (BHY[1] - BHY[0]) * t - inset
        d2 = _plan_rr(x, y, hx, hy, BRR - 0.5 * inset)
        e = 0.14
        wx = d2 + e
        wy = (floor + e) - z
        return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx, 0), np.maximum(wy, 0)) - e
    return F


def make_basket(parent, q):
    outer = u_sisect(_basket_solid(), lambda x, y, z: z - BZ1, 0.02)
    inner = _basket_solid(BWALL, BZ0 + BWALL, tmax=1.6)
    shell = u_ssub(outer, inner, 0.025)
    rim = lambda x, y, z: np.hypot(_plan_rr(x, y, BHX[1] - BWALL / 2, BHY[1] - BWALL / 2, BRR), z - BZ1) - 0.072
    body = u_smin(shell, rim, 0.02)
    fr = op_union(*[sd_rbox(cx, -0.11, 0.068, 0.20, 0.066) for cx in (-0.48, -0.24, 0.0, 0.24, 0.48)])
    sd_ = op_union(*[sd_rbox(cy, -0.11, 0.052, 0.20, 0.05) for cy in (-0.15, 0.0, 0.15)])
    body = u_ssub(body, extrude_axis(fr, 'y', 1.0, 0.0), 0.022)
    body = u_ssub(body, extrude_axis(sd_, 'x', 1.2, 0.0), 0.022)
    mb = candy('basket', 'ORANGE', rim='AMBER', rim_str=0.25, grad=(mixlin('ORANGE', 'AMBER', 0.22), BZ0, BZ1 + 0.1))
    obj('basket', body, ((-1.12, -0.72, BZ0 - 0.05), (1.12, 0.72, BZ1 + 0.1)), R(q, 300), mb, parent)
    # MAGENTA arch handle on two pivot hubs
    a, hgt = 1.035, 0.86
    th = np.linspace(0.0, math.pi, 64)
    arc = [(a * math.cos(t), BZ1 - 0.12 + (hgt + 0.12) * math.sin(t) ** 0.9) for t in th]
    h2 = sd_polyline(arc, 0.07)
    handle = extrude_axis(h2, 'y', 0.095, 0.055)
    hubs = u_min(*[sd3_round_cyl((sx * 0.975, 0, BZ1 - 0.12), (sx * 1.075, 0, BZ1 - 0.12), 0.115, 0.035) for sx in (-1, 1)])
    hh = u_smin(handle, hubs, 0.03)
    mh = candy('handle', 'MAGENTA', rim='HOT_PINK', rim_str=0.25)
    obj('handle', hh, ((-1.15, -0.2, BZ1 - 0.3), (1.15, 0.2, BZ1 + hgt + 0.1)), R(q, 280), mh, parent)


def make_loaf(parent, q, c, rx=0.0, rz=0.0, tag='bread'):
    """Golden bloomer loaf: rounded base, domed top with three cream score marks."""
    base = sd3_round_box((0, 0, 0), (0.29, 0.175, 0.10), 0.09)
    dome = sd3_ellipsoid((0, 0, 0.05), (0.30, 0.185, 0.18))
    F0 = u_smin(base, dome, 0.07)
    cuts = u_min(*[sd3_capsule((x - 0.055, -0.13, 0.235), (x + 0.055, 0.13, 0.235), 0.03) for x in (-0.15, 0.0, 0.15)])
    F1 = u_ssub(F0, cuts, 0.025)
    pl = lambda F: u_xform(F, t=tuple(c), rx=rx, rz=rz)
    cc = np.asarray(c, float)
    o = obj(tag, pl(F1), (tuple(cc - 0.42), tuple(cc + 0.42)), R(q, 200), None, parent)
    G = pl(cuts)
    set_attr(o, 'score', lambda x, y, z: sstep(0.04, 0.005, G(x, y, z)))
    m = m_layers(tag, '#D27A2E', [('score', '#FBE3B0')], rough=0.34, coat_r=0.06, spec=0.4,
                 rim_glow='AMBER', rim_str=0.15, grad=('#E59A45', cc[2] - 0.15, cc[2] + 0.2))
    o.data.materials.append(m)
    return o


def make_carton(parent, q, c, rz, tag='carton'):
    zb, zt, zg = -0.36, 0.60, 0.80
    hx, hy = 0.17, 0.15
    body = sd3_round_box((0, 0, (zb + zt) / 2), (hx, hy, (zt - zb) / 2), 0.04)
    tri = op_offset(sd_poly_exact([(-hx + 0.03, zt - 0.02), (hx - 0.03, zt - 0.02), (0.0, zg - 0.03)]), 0.03)
    gable = extrude_axis(tri, 'y', hy - 0.005, 0.03)
    fin = sd3_round_box((0, 0, zg + 0.015), (0.022, hy - 0.01, 0.05), 0.018)
    F0 = u_smin(u_smin(body, gable, 0.02), fin, 0.015)
    F = u_xform(F0, t=tuple(c), rz=rz)
    o = obj(tag, F, (tuple(np.asarray(c) + [-0.3, -0.3, zb - 0.05]), tuple(np.asarray(c) + [0.3, 0.3, zg + 0.1])),
            R(q, 200), None, parent)
    cz = c[2]
    set_attr(o, 'band', lambda x, y, z: np.maximum(sstep(0.0, 0.02, z - cz - 0.02) * sstep(0.0, 0.02, cz + 0.36 - z),
                                                   sstep(0.0, 0.02, z - cz - zt + 0.01)))
    m = m_layers(tag, (0.95, 0.94, 0.93), [('band', 'LEAF')], rough=0.3, coat_r=0.04)
    o.data.materials.append(m)
    return o


def make_banana(parent, q, c, R3, scale=1.0, tag='banana'):
    Rc = 0.62
    th0, th1 = math.radians(205), math.radians(335)

    def F(x, y, z):
        th = np.arctan2(z - Rc, x)
        th = np.where(th < 0, th + 2 * np.pi, th)
        thc = np.clip(th, th0, th1)
        t = (thc - th0) / (th1 - th0)
        px, pz = Rc * np.cos(thc), Rc + Rc * np.sin(thc)
        r = 0.035 + 0.115 * np.sin(np.pi * t) ** 0.55
        # five soft ridges around the curved axis
        tx, tz = -np.sin(thc), np.cos(thc)
        ox, oz = x - px, z - pz
        rad_x = ox - (ox * tx + oz * tz) * tx
        rad_z = oz - (ox * tx + oz * tz) * tz
        phi = np.arctan2(y, rad_x * np.cos(thc) + rad_z * np.sin(thc))
        r = r * (1 + 0.035 * np.cos(5 * phi))
        return np.sqrt((x - px) ** 2 + y ** 2 + (z - pz) ** 2) - r
    G = u_frame(lambda x, y, z: F(x / scale, y / scale, z / scale) * scale, c, R3)
    o = obj(tag, G, (tuple(np.asarray(c) - 0.75 * scale), tuple(np.asarray(c) + 0.75 * scale)), R(q, 200), None, parent)

    def tips(x, y, z):
        Ri = np.asarray(R3, float)
        px, py, pz = x - c[0], y - c[1], z - c[2]
        lx = (Ri[0, 0] * px + Ri[1, 0] * py + Ri[2, 0] * pz) / scale
        lz = (Ri[0, 2] * px + Ri[1, 2] * py + Ri[2, 2] * pz) / scale
        th = np.arctan2(lz - Rc, lx)
        th = np.where(th < 0, th + 2 * np.pi, th)
        return np.maximum(sstep(th0 + 0.07, th0 - 0.02, th), sstep(th1 - 0.10, th1 + 0.0, th))
    set_attr(o, 'tips', tips)
    m = m_layers(tag, '#FFD23C', [('tips', '#6B4424')], rough=0.3, coat_r=0.04, rim_glow='AMBER', rim_str=0.2,
                 grad=('#FFE27A', c[2] - 0.2 * scale, c[2] + 0.3 * scale))
    o.data.materials.append(m)
    return o


@asset('basket', variants=('day', 'day_full'), tilt=16.0, base_yaw=0.0, priority=1,
       notes='ORANGE shopping basket, MAGENTA handle; day = empty, day_full = apple, bread loaf, carton, banana '
             '(both folders share one camera: cross-fade to fill)')
def build_basket(root, variant, q):
    make_basket(root, q)
    cont = I.empty('contents', root)
    make_carton(cont, q, (0.40, 0.16, 0.0), math.radians(-16))
    make_loaf(cont, q, (-0.50, 0.17, 0.40), rx=math.radians(30), rz=math.radians(18))
    Rb = rot3(rx=math.radians(-12), ry=math.radians(8), rz=math.radians(-6))
    make_banana(cont, q, (0.36, -0.24, 0.30), Rb, scale=0.80)
    make_apple(cont, q, c=(-0.20, -0.30, 0.36), s=0.32, rz=math.radians(20), tag='b_apple', res=160)
    hide = [] if variant == 'day_full' else [cont] + list(cont.children_recursive)
    return {'hide': hide, 'features': {'mouth': (0.0, 0.0, BZ1)}}


# ============================================================================= sandwich

TRI = [(-0.80, -0.33), (0.80, -0.33), (0.0, 0.47)]
TRI_R = 0.12


@asset('sandwich', tilt=30.0, base_yaw=0.0, priority=4, notes='triangle sandwich: crumb + golden crust, lettuce, tomato')
def build_sandwich(root, variant, q):
    tri0 = sd_poly_exact(TRI)
    tri = fn_sd(op_offset(tri0, TRI_R), (-1.15, -0.75, 1.15, 0.85), 1100)
    P = tri.poisson(260)
    top = inflate(tri, thick=0.095, edge=0.085, dome=0.06, dome_field=P, dome_pow=0.6, zc=0.125, back=0.095)
    bot = inflate(tri, thick=0.095, edge=0.085, dome=0.025, dome_field=P, dome_pow=0.6, zc=-0.20)
    legs = op_union(sd_segment(*TRI[0], *TRI[2], 0.0), sd_segment(*TRI[1], *TRI[2], 0.0))
    hyp = sd_segment(*TRI[0], *TRI[1], 0.0)

    def crust(x, y, z):
        s_ = tri0(x, y)
        dl, dh = legs(x, y), hyp(x, y)
        return sstep(-0.075, -0.035, s_) * sstep(0.0, 0.02, dh - dl)
    for nm, F, zc in (('bread_top', top, 0.125), ('bread_bot', bot, -0.20)):
        o = obj(nm, F, ((-1.1, -0.65, zc - 0.16), (1.1, 0.75, zc + 0.2)), R(q, 280), None, root)
        set_attr(o, 'crust', crust)
        o.data.materials.append(m_layers(nm, '#F7E0B2', [('crust', '#CF7C30')], rough=0.4, coat_r=0.07, spec=0.4,
                                         sss=0.08, sss_radius=(1.0, 0.7, 0.4), sss_scale=0.04))
    # lettuce: frilly sheet sticking out all round
    cen = np.array([0.0, -0.06])

    def lettuce(x, y, z):
        th = np.arctan2(y - cen[1], x - cen[0])
        d = tri0(x, y) - TRI_R - 0.085 - 0.035 * np.sin(17 * th)
        edge_w = sstep(-0.30, 0.05, tri0(x, y) - TRI_R)
        zc = -0.005 + 0.038 * np.sin(23 * th + 0.5) * edge_w
        return rounded_extrude(d, np.abs(z - zc) - 0.026, 0.022)
    ml = candy('lettuce', 'LEAF', rim='LEAF_HI', rim_str=0.25, grad=('LEAF_HI', -0.3, 0.3), rough=0.3)
    obj('lettuce', lettuce, ((-1.2, -0.8, -0.1), (1.2, 0.9, 0.1)), R(q, 300), ml, root)
    # tomato slices peeking out of the cut face
    toms = [(-0.40, -0.36, 0.27), (0.38, -0.34, 0.27), (0.0, 0.20, 0.24)]
    tF = u_min(*[extrude_axis(sd_circle(cx, cy, r), 'z', 0.034, 0.03, center=-0.075) for cx, cy, r in toms])
    o = obj('tomato', tF, ((-0.75, -0.7, -0.13), (0.75, 0.5, -0.02)), R(q, 220), None, root)

    def flesh(x, y, z):
        v = np.zeros_like(x)
        for cx, cy, r in toms:
            rr = np.hypot(x - cx, y - cy) / r
            th = np.arctan2(y - cy, x - cx)
            lob = sstep(0.0, 0.25, np.cos(3 * th + 0.4) + 0.35)
            v = np.maximum(v, sstep(0.80, 0.70, rr) * sstep(0.12, 0.25, rr) * lob)
        return v
    set_attr(o, 'flesh', flesh)
    o.data.materials.append(m_layers('tomato', '#E2302A', [('flesh', '#FF7A55')], rough=0.22, coat_r=0.025,
                                     rim_glow='ORANGE', rim_str=0.2))
    return {}


# ============================================================================= plate

@asset('plate', tilt=46.0, base_yaw=0.0, priority=5, notes='ivory plate, MAGENTA rim line; drumstick, broccoli, carrots')
def build_plate(root, variant, q):
    prof = sd_polyline([(0.0, -0.10), (0.56, -0.10), (0.74, -0.04), (0.99, 0.075)], 0.042)
    foot = lambda r, z: np.hypot(r - 0.40, z + 0.155) - 0.035
    plate = lambda x, y, z: np.minimum(prof(np.hypot(x, y), z), foot(np.hypot(x, y), z))
    o = obj('plate', plate, ((-1.06, -1.06, -0.22), (1.06, 1.06, 0.15)), R(q, 320), None, root)
    set_attr(o, 'line', lambda x, y, z: sstep(0.84, 0.855, np.hypot(x, y)) * sstep(0.905, 0.89, np.hypot(x, y))
             * sstep(0.0, 0.02, z - 0.0))
    o.data.materials.append(m_layers('plate', (0.97, 0.94, 0.91), [('line', 'MAGENTA')], rough=0.22, coat_r=0.03,
                                     grad=((1.0, 0.98, 0.96), -0.1, 0.1)))
    zs = -0.055          # top of the well
    # drumstick: golden meat + ivory bone
    meat = u_smin(u_smin(sd3_ellipsoid((-0.16, 0.10, zs + 0.12), (0.27, 0.22, 0.15)),
                         sd3_ellipsoid((0.06, 0.20, zs + 0.09), (0.16, 0.13, 0.11)), 0.10),
                  sd3_capsule((0.06, 0.20, zs + 0.08), (0.20, 0.27, zs + 0.07), 0.07), 0.06)
    mm = candy('meat', '#B65E1E', rim='AMBER', rim_str=0.25, rough=0.26, coat_r=0.04,
               grad=('#E08A36', zs, zs + 0.28))
    obj('meat', meat, ((-0.5, -0.2, zs - 0.05), (0.32, 0.45, zs + 0.3)), R(q, 200), mm, root)
    bone = u_smin(sd3_capsule((0.16, 0.25, zs + 0.07), (0.42, 0.38, zs + 0.07), 0.042),
                  u_min(sd3_sphere((0.45, 0.34, zs + 0.07), 0.058), sd3_sphere((0.41, 0.43, zs + 0.07), 0.058)), 0.03)
    mbone = candy('bone', (0.96, 0.93, 0.88), rough=0.3)
    obj('bone', bone, ((0.1, 0.18, zs - 0.02), (0.53, 0.52, zs + 0.16)), R(q, 140), mbone, root)
    # broccoli florets
    heads = []
    stalks = []
    for (bx, by, s) in ((0.36, -0.16, 1.0), (0.08, -0.40, 0.82)):
        stalks.append(sd3_round_cone((bx, by + 0.05 * s, zs + 0.02), (bx, by, zs + 0.17 * s), 0.065 * s, 0.05 * s))
        cl = [sd3_sphere((bx, by, zs + 0.26 * s), 0.095 * s)]
        for k in range(7):
            a = 2 * math.pi * k / 7 + 0.3
            cl.append(sd3_sphere((bx + 0.115 * s * math.cos(a), by + 0.115 * s * math.sin(a), zs + 0.20 * s), 0.068 * s))
        for k in range(4):
            a = 2 * math.pi * k / 4 + 0.9
            cl.append(sd3_sphere((bx + 0.06 * s * math.cos(a), by + 0.06 * s * math.sin(a), zs + 0.28 * s), 0.06 * s))
        h = cl[0]
        for c_ in cl[1:]:
            h = u_smin(h, c_, 0.035 * s)
        heads.append(h)
    ms = candy('stalk', mixlin('LEAF_HI', 'IVORY', 0.35), rough=0.32)
    obj('stalks', u_min(*stalks), ((-0.15, -0.6, zs - 0.03), (0.5, 0.0, zs + 0.25)), R(q, 140), ms, root)
    mhd = candy('broccoli', 'LEAF', rim='LEAF_HI', rim_str=0.25, grad=('LEAF_HI', zs + 0.12, zs + 0.38), rough=0.34)
    obj('broccoli', u_min(*heads), ((-0.15, -0.62, zs + 0.05), (0.55, 0.05, zs + 0.42)), R(q, 220), mhd, root)
    # carrot coins
    coins = [(-0.44, -0.24, 0.0), (-0.24, -0.44, 0.35), (-0.58, -0.02, -0.3)]
    cF = []
    for cx, cy, tl in coins:
        cF.append(u_xform(extrude_axis(sd_circle(0, 0, 0.115), 'z', 0.032, 0.026), t=(cx, cy, zs + 0.035),
                          rx=math.radians(10 * tl), ry=math.radians(12 * tl)))
    o = obj('carrots', u_min(*cF), ((-0.8, -0.65, zs - 0.08), (-0.05, 0.18, zs + 0.15)), R(q, 200), None, root)

    def ring(x, y, z):
        v = np.zeros_like(x)
        for cx, cy, _ in coins:
            r = np.hypot(x - cx, y - cy)
            v = np.maximum(v, sstep(0.035, 0.05, r) * sstep(0.075, 0.06, r))
        return v * 0.8
    set_attr(o, 'ring', ring)
    o.data.materials.append(m_layers('carrot', 'ORANGE', [('ring', 'AMBER')], rough=0.26, coat_r=0.03,
                                     rim_glow='AMBER', rim_str=0.25))
    return {}


# ============================================================================= bed

@asset('bed', tilt=20.0, base_yaw=-22.0, priority=6,
       notes='single bed: ivory frame, white mattress + pillow, MAGENTA duvet with a LAVENDER turn-down')
def build_bed(root, variant, q):
    ivory = candy('frame', 'IVORY', rough=0.3, coat_r=0.05, grad=((1.0, 0.97, 0.94), -0.5, 0.7),
                  sss=0.12, sss_radius=(1.0, 0.7, 0.5), sss_scale=0.05)
    head = extrude_axis(sd_rbox(0.0, 0.07, 0.52, 0.57, 0.26), 'x', 0.075, 0.055, center=-1.0)
    foot = extrude_axis(sd_rbox(0.0, -0.17, 0.52, 0.33, 0.17), 'x', 0.065, 0.05, center=1.0)
    base = sd3_round_box((0.0, 0.0, -0.25), (0.98, 0.48, 0.10), 0.06)
    frame = u_smin(u_smin(head, foot, 0.03), base, 0.03)
    # small round knobs on the posts read as 'furniture'
    obj('frame', frame, ((-1.12, -0.6, -0.55), (1.12, 0.6, 0.7)), R(q, 300), ivory, root)
    white = candy('mattress', (0.95, 0.94, 0.95), rough=0.32, coat_r=0.05)
    mat = sd3_round_box((-0.02, 0.0, -0.065), (0.93, 0.455, 0.09), 0.075)
    obj('mattress', mat, ((-1.0, -0.52, -0.2), (0.96, 0.52, 0.06)), R(q, 240), white, root)
    pl2 = fn_sd(sd_rbox(0.0, 0.0, 0.19, 0.36, 0.15), (-0.45, -0.45, 0.45, 0.45), 700)
    pillow0 = inflate(pl2, thick=0.04, edge=0.04, dome=0.075, dome_field=pl2.poisson(200), dome_pow=0.55)
    pillow = u_xform(pillow0, t=(-0.70, 0.0, 0.10), ry=math.radians(28))
    obj('pillow', pillow, ((-1.0, -0.45, -0.15), (-0.4, 0.45, 0.4)), R(q, 200),
        candy('pillow', (0.98, 0.97, 0.98), rough=0.34, coat_r=0.05), root)
    box = sd3_round_box((0.26, 0.0, -0.025), (0.67, 0.505, 0.125), 0.10)
    puff = sd3_ellipsoid((0.25, 0.0, 0.07), (0.67, 0.47, 0.09))
    roll = sd3_capsule((-0.34, -0.50, 0.11), (-0.34, 0.50, 0.11), 0.08)
    duvet = u_smin(u_smin(box, puff, 0.08), roll, 0.11)
    grooves = u_min(*[sd3_capsule((gx, -0.7, 0.17), (gx, 0.7, 0.17), 0.03) for gx in (0.12, 0.52)])
    duvet = u_ssub(duvet, grooves, 0.035)
    o = obj('duvet', duvet, ((-0.55, -0.62, -0.2), (1.05, 0.62, 0.2)), R(q, 300), None, root)
    set_attr(o, 'fold', lambda x, y, z: sstep(-0.13, -0.17, x))
    o.data.materials.append(m_layers('duvet', 'MAGENTA', [('fold', mixlin('LAVENDER', 'HOT_PINK', 0.22))],
                                     rough=0.32, coat_r=0.11, rim_glow='HOT_PINK', rim_str=0.25))
    return {}


# ============================================================================= t-shirt (icon frame: x right, y up, z to viewer)

def tee_outline():
    R_ = [(0.0, 0.64), (0.12, 0.665), (0.22, 0.73), (0.28, 0.82), (0.60, 0.76), (1.03, 0.43), (0.84, 0.13),
          (0.63, 0.29), (0.63, -0.90), (0.0, -0.90)]
    L_ = [(-x, y) for x, y in R_[::-1]][1:-1]
    return np.array(R_ + L_)


@asset('tshirt', tilt=4.0, base_yaw=0.0, priority=7, notes='MAGENTA tee, ribbed collar, small raised ORANGE heart print')
def build_tshirt(root, variant, q):
    sd = poly_sd([tee_outline()], res=1400).rounded(0.07, 0.06).blurred(1.0)
    P = sd.poisson()
    thick, dome, dp = 0.09, 0.13, 0.5
    body = inflate(sd, thick=thick, edge=0.088, dome=dome, dome_field=P, dome_pow=dp)
    front = lambda x, y: thick + dome * np.clip(P(x, y), 0, 1) ** dp
    # seam grooves: sleeve hems + bottom hem
    seams2 = op_union(sd_segment(0.90, 0.47, 0.735, 0.215, 0.0), sd_segment(-0.90, 0.47, -0.735, 0.215, 0.0),
                      sd_segment(-0.58, -0.77, 0.58, -0.77, 0.0))
    seam = lambda x, y, z: np.hypot(seams2(x, y), z - front(x, y) - 0.004) - 0.016
    body = u_ssub(body, seam, 0.012)
    mm = candy('tee', 'MAGENTA', rim='HOT_PINK', rim_str=0.25, sheen=0.25, rough=0.3)
    obj('tee', body, ((-1.15, -1.0, -0.3), (1.15, 0.95, 0.3)), R(q, 320), mm, root, icon=True)
    # inside back of the neck + ribbed collar
    back2 = op_sub(sd_ellipse(0.0, 0.80, 0.29, 0.17), sd_rbox(0.0, 1.2, 0.6, 0.30, 0.0))
    back = inflate(back2, thick=0.02, edge=0.018, zc=-0.03)
    obj('tee_back', back, ((-0.4, 0.55, -0.1), (0.4, 0.95, 0.05)), R(q, 140),
        candy('tee_in', mixlin('MAGENTA', 'PLUM', 0.55), rough=0.35), root, icon=True)
    neck = [(0.29 * math.sin(t), 0.82 - 0.175 * math.cos(t) ** 1.0) for t in np.linspace(-math.pi / 2, math.pi / 2, 40)]
    neck2 = sd_polyline(neck, 0.0)
    collar = lambda x, y, z: np.hypot(neck2(x, y), z - 0.035) - 0.055
    obj('collar', collar, ((-0.42, 0.55, -0.1), (0.42, 0.92, 0.15)), R(q, 160),
        candy('collar', mixlin('MAGENTA', 'HOT_PINK', 0.25), rim='HOT_PINK', rim_str=0.25, rough=0.3), root, icon=True)
    hs = sd_heart(0.50, convex=0.14, concave=0.16, res=600)
    hc = (0.0, 0.10)
    heart2 = op_xform(hs, hc[0], hc[1])
    heart = lambda x, y, z: rounded_extrude(heart2(x, y), np.abs(z - front(x, y) - 0.006) - 0.032, 0.026)
    obj('heart', heart, ((-0.34, -0.22, 0.05), (0.34, 0.40, 0.32)), R(q, 200),
        candy('heart', 'ORANGE', rim='AMBER', rim_str=0.3, rough=0.24, sss=0.15, sss_radius=(1.0, 0.4, 0.2),
              sss_scale=0.05), root, icon=True)
    return {}


def sd_ellipse(cx, cy, rx, ry):
    return I.sd_ellipse_approx(cx, cy, rx, ry)


# ============================================================================= trainer

TR_UPPER = [(-0.97, -0.30), (-1.00, 0.04), (-0.96, 0.33), (-0.87, 0.43), (-0.74, 0.43), (-0.56, 0.31),
            (-0.42, 0.31), (-0.30, 0.48), (-0.19, 0.51), (0.04, 0.36), (0.38, 0.17), (0.68, 0.03), (0.90, -0.08),
            (0.99, -0.20), (0.97, -0.30)]
TR_SOLE = [(-1.00, -0.25), (-1.03, -0.40), (-0.96, -0.52), (0.80, -0.52), (1.00, -0.45), (1.09, -0.31),
           (1.04, -0.22), (-0.95, -0.22)]


@asset('trainer', tilt=14.0, base_yaw=-24.0, priority=8,
       notes='white sneaker: ORANGE toe cap, heel counter, pull tab, laces and outsole')
def build_trainer(root, variant, q):
    up2 = bc(poly_sd([np.array(TR_UPPER)], res=1300).rounded(0.10, 0.06).blurred(1.0))

    def hw(x, z):
        return (0.345 - 0.15 * np.clip((z + 0.28) / 0.80, 0, 1) ** 1.3 - 0.10 * np.clip((x - 0.50) / 0.50, 0, 1) ** 2
                - 0.05 * np.clip((-x - 0.70) / 0.30, 0, 1))

    def upper0(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z)
        return rounded_extrude(up2(x, z), np.abs(y) - hw(x, z), 0.17)
    ankle = sd3_ellipsoid((-0.60, 0.0, 0.47), (0.29, 0.20, 0.22))
    tongue = u_xform(sd3_round_box((0, 0, 0), (0.07, 0.125, 0.11), 0.065), t=(-0.25, 0.0, 0.49), ry=math.radians(-24))
    upper = u_ssub(u_smin(upper0, tongue, 0.05), ankle, 0.04)
    white = candy('upper', (0.95, 0.94, 0.95), rough=0.3, coat_r=0.045)
    o = obj('upper', upper, ((-1.12, -0.45, -0.4), (1.1, 0.45, 0.74)), R(q, 300), None, root)
    set_attr(o, 'lining', lambda x, y, z: sstep(0.05, 0.012, ankle(x, y, z)) * sstep(0.12, 0.2, z))
    o.data.materials.append(m_layers('upper', (0.95, 0.94, 0.95), [('lining', 'ORANGE')], rough=0.3, coat_r=0.045))
    orange = candy('accent', 'ORANGE', rim='AMBER', rim_str=0.25, rough=0.26)
    cap = u_sisect(u_sisect(lambda x, y, z: upper0(x, y, z) - 0.018,
                            lambda x, y, z: (0.50 + 0.32 * np.clip((z + 0.28) / 0.45, 0, 1) ** 1.5) - x, 0.03),
                   lambda x, y, z: z - 0.25, 0.03)
    obj('toecap', cap, ((0.3, -0.45, -0.4), (1.15, 0.45, 0.3)), R(q, 220), orange, root)
    heel = u_sisect(u_sisect(lambda x, y, z: upper0(x, y, z) - 0.018,
                             lambda x, y, z: x - (-0.64 - 0.24 * np.clip((z + 0.28) / 0.58, 0, 1) ** 2), 0.03),
                    lambda x, y, z: z - 0.30, 0.03)
    tab = u_xform(sd3_round_box((0, 0, 0), (0.035, 0.075, 0.11), 0.03), t=(-0.95, 0.0, 0.44), ry=math.radians(-14))
    obj('heel', u_smin(heel, tab, 0.03), ((-1.15, -0.45, -0.4), (-0.5, 0.45, 0.62)), R(q, 220), orange, root)
    # laces across the tongue slope
    A_, B_ = np.array([-0.17, 0.51]), np.array([0.36, 0.18])
    nrm = np.array([B_[1] - A_[1], -(B_[0] - A_[0])])
    nrm = -nrm / np.linalg.norm(nrm)
    bars = []
    for t in (0.16, 0.40, 0.64, 0.88):
        p = A_ + (B_ - A_) * t + nrm * 0.0
        bars.append(sd3_capsule((p[0], -0.135, p[1] - 0.01), (p[0], 0.135, p[1] - 0.01), 0.034))
    obj('laces', u_min(*bars), ((-0.3, -0.25, 0.05), (0.5, 0.25, 0.62)), R(q, 160), orange, root)
    so2 = bc(poly_sd([np.array(TR_SOLE)], res=1300).rounded(0.07, 0.03).blurred(1.0))

    def sole(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z)
        return rounded_extrude(so2(x, z), np.abs(y) - (0.365 - 0.05 * np.clip((x - 0.6) / 0.5, 0, 1) ** 2), 0.09)
    o = obj('sole', sole, ((-1.12, -0.45, -0.58), (1.15, 0.45, -0.15)), R(q, 280), None, root)
    set_attr(o, 'out', lambda x, y, z: sstep(-0.435, -0.455, z))
    o.data.materials.append(m_layers('sole', (0.97, 0.96, 0.96), [('out', 'ORANGE')], rough=0.32, coat_r=0.05))
    return {}


# ============================================================================= football

PHI = (1 + 5 ** 0.5) / 2


def _ico_dirs():
    v = []
    for a in (-1, 1):
        for b in (-PHI, PHI):
            v += [(0, a, b), (a, b, 0), (b, 0, a)]
    v = np.array(v, float)
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    faces = []
    n = len(v)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if v[i] @ v[j] > 0.4 and v[j] @ v[k] > 0.4 and v[i] @ v[k] > 0.4:
                    faces.append((i, j, k))
    hexd = np.array([v[list(f)].sum(0) for f in faces])
    hexd /= np.linalg.norm(hexd, axis=1, keepdims=True)
    return v, hexd


@asset('football', tilt=0.0, base_yaw=0.0, priority=9, notes='classic football: ivory hexagons, PLUM pentagons')
def build_football(root, variant, q):
    pent, hexd = _ico_dirs()
    # orient: one pentagon faces the camera (-Y), turned a little so the pattern reads as a ball
    n0 = pent[np.argmax(pent @ np.array([0.0, -0.3, 1.0]))]
    tgt = np.array([0.0, -1.0, 0.0])
    ax = np.cross(n0, tgt)
    s_ = np.linalg.norm(ax)
    c_ = float(n0 @ tgt)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    Rm = np.eye(3) + K + K @ K * ((1 - c_) / max(s_ * s_, 1e-12))
    Rm = rot3(rx=math.radians(-24), rz=math.radians(14)) @ Rm
    pent = pent @ Rm.T
    hexd = hexd @ Rm.T
    dP, dH = 1.02653, 1.0               # relative plane distances of the truncated icosahedron faces
    N = np.concatenate([pent / dP, hexd / dH])

    def scores(x, y, z):
        r = np.sqrt(x * x + y * y + z * z) + 1e-9
        u = np.stack([x / r, y / r, z / r], -1)
        s = u @ N.T
        s.sort(-1)
        return s[..., -1], s[..., -2], r, u

    def F(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z)
        b1, b2, r, _ = scores(x, y, z)
        g = (b1 - b2) / np.maximum(b1, 1e-6)
        groove = 0.030 * (1 - sstep(0.0, 0.030, g))
        puff = 0.012 * sstep(0.0, 0.10, g)
        return r - (0.97 - groove + puff)
    o = obj('ball', blockwise(F), ((-1.05, -1.05, -1.05), (1.05, 1.05, 1.05)), R(q, 300), None, root)

    def is_pent(x, y, z):
        r = np.sqrt(x * x + y * y + z * z) + 1e-9
        u = np.stack([x / r, y / r, z / r], -1)
        sp = (u @ pent.T).max(-1) / dP
        sh = (u @ hexd.T).max(-1) / dH
        return sstep(-0.004, 0.004, sp - sh)
    set_attr(o, 'pent', blockwise(is_pent))
    o.data.materials.append(m_layers('ball', (0.97, 0.95, 0.92), [('pent', 'PLUM')], rough=0.26, coat_r=0.03,
                                     sss=0.06, sss_radius=(1.0, 0.8, 0.6), sss_scale=0.03))
    return {}


# ============================================================================= paint palette (icon frame)

def palette_sd():
    base = I.sd_ellipse_approx(0.04, 0.0, 1.0, 0.76)
    notch = sd_circle(-0.78, -0.66, 0.34)
    hole = sd_circle(-0.40, -0.26, 0.125)
    s = op_sub(op_sub(base, notch), hole)
    return fn_sd(s, (-1.15, -1.0, 1.2, 1.0), 1300).rounded(0.05, 0.08).blurred(1.0)


DABS = [(-0.50, 0.32, 'MAGENTA', 'HOT_PINK', 0.0), (-0.01, 0.48, 'ORANGE', 'AMBER', 1.3),
        (0.47, 0.37, 'LEAF', 'LEAF_HI', 2.2), (0.74, -0.04, 'AMBER', (1.0, 0.85, 0.55), 3.9)]


@asset('paint_palette', tilt=14.0, base_yaw=0.0, priority=10,
       notes='ivory palette, ORANGE / MAGENTA / LEAF / AMBER paint dabs, PLUM brush with a gold ferrule')
def build_palette(root, variant, q):
    sd = palette_sd()
    P = sd.poisson()
    th, dome = 0.07, 0.03
    pal = inflate(sd, thick=th, edge=0.062, dome=dome, dome_field=P, dome_pow=0.6)
    front = lambda x, y: th + dome * np.clip(P(x, y), 0, 1) ** 0.6
    mp = candy('palette', (0.98, 0.94, 0.89), rough=0.3, coat_r=0.04, grad=((1.0, 0.98, 0.95), -0.8, 0.8),
               sss=0.1, sss_radius=(1.0, 0.7, 0.5), sss_scale=0.05)
    obj('palette', pal, ((-1.15, -0.95, -0.2), (1.15, 0.95, 0.2)), R(q, 320), mp, root, icon=True)
    for k, (dx, dy, col, hi, ph) in enumerate(DABS):
        r0 = 0.165

        def blob(x, y, dx=dx, dy=dy, ph=ph):
            th_ = np.arctan2(y - dy, x - dx)
            return np.hypot(x - dx, y - dy) - r0 * (1 + 0.10 * np.sin(3 * th_ + ph) + 0.05 * np.sin(5 * th_ + 2 * ph))
        bs = fn_sd(blob, (dx - 0.3, dy - 0.3, dx + 0.3, dy + 0.3), 400)
        zc = float(front(np.array([dx]), np.array([dy]))[0]) - 0.01
        F = inflate(bs, thick=0.03, edge=0.03, dome=0.10, dome_field=bs.poisson(160), dome_pow=0.7, zc=zc)
        md = candy(f'paint{k}', col, rim=hi, rim_str=0.3, rough=0.16, coat_r=0.02, grad=(hi, dy - 0.2, dy + 0.25) if k != 3 else None)
        obj(f'paint{k}', F, ((dx - 0.3, dy - 0.3, zc - 0.06), (dx + 0.3, dy + 0.3, zc + 0.2)), R(q, 150), md, root, icon=True)
    # brush lying across the palette, bristles lifted towards the viewer
    E = np.array([1.02, -0.80, 0.15])
    T = np.array([0.02, 0.02, 0.36])
    d = T - E
    pt = lambda t: E + d * t
    handle = sd3_round_cone(pt(0.0), pt(0.60), 0.045, 0.062)
    obj('brush_handle', handle, (tuple(np.minimum(E, pt(0.6)) - 0.1), tuple(np.maximum(E, pt(0.6)) + 0.1)), R(q, 200),
        candy('brush', 'PLUM', rim='MAGENTA', rim_str=0.3, rough=0.24), root, icon=True)
    fer = sd3_round_cyl(pt(0.59), pt(0.75), 0.068, 0.022)
    obj('ferrule', fer, (tuple(np.minimum(pt(0.59), pt(0.75)) - 0.1), tuple(np.maximum(pt(0.59), pt(0.75)) + 0.1)),
        R(q, 140), I.m_gold('ferrule', rough=0.2), root, icon=True)
    bri = u_smin(sd3_round_cone(pt(0.74), pt(1.0), 0.072, 0.012), sd3_sphere(pt(0.80), 0.076), 0.05)
    o = obj('bristles', bri, (tuple(np.minimum(pt(0.72), T) - 0.12), tuple(np.maximum(pt(0.72), T) + 0.12)), R(q, 160),
            None, root, icon=True)
    L2 = float(d @ d)
    set_attr(o, 'dip', lambda x, y, z: sstep(0.86, 0.90, ((x - E[0]) * d[0] + (y - E[1]) * d[1] + (z - E[2]) * d[2]) / L2),
             icon=True)
    o.data.materials.append(m_layers('bristles', '#EAC99A', [('dip', 'MAGENTA')], rough=0.34, coat_r=0.06))
    return {}


# ============================================================================= driver

def _points(root, max_pts=60000, include_hidden=True):
    pts = []
    for o in root.children_recursive:
        if o.type != 'MESH' or (o.hide_render and not include_hidden):
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


def frame_camera(root, yaws, fill=FILL, aspect=1.0):
    """assets3d_icons.frame_camera, but the swept points come from the real (tilted) rotations and
    hidden meshes count too (day / day_full share one camera)."""
    bpy = I.bpy
    from mathutils import Vector
    sc = bpy.context.scene
    cam_d = bpy.data.cameras.new('cam')
    cam_d.lens = I.LENS
    cam_d.sensor_fit = 'AUTO'
    cam_d.sensor_width = 36.0
    cam = bpy.data.objects.new('cam', cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sweep = []
    for a in yaws:
        root.rotation_euler = (0, 0, math.radians(a))
        bpy.context.view_layer.update()
        sweep.append(_points(root))
    root.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    P0 = _points(root)
    c = (P0.min(0) + P0.max(0)) / 2
    allp = np.concatenate(sweep)
    el = math.radians(I.ELEV_DEG)
    fov_half = math.atan(18.0 / I.LENS)
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
        span = max(x1 - x0, y1 - y0) / 2
        shift = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        dist *= span / fill
    cam.location = Vector(cam_pos.tolist())
    I._aim(cam, (c[0], 0, tz))
    cam_d.shift_x = shift[0] / 2 * (1 if aspect >= 1 else aspect)
    cam_d.shift_y = shift[1] / 2 / (aspect if aspect >= 1 else 1)
    cam_d.clip_start = 0.05
    cam_d.clip_end = 100
    return cam


def yaw_of(i, n=YAW_FRAMES):
    return YAW_RANGE[0] + (YAW_RANGE[1] - YAW_RANGE[0]) * i / max(n - 1, 1)


def render_asset(name, variant='day', preview=False, frames=None, samples=None, size=None):
    """Build + render one asset / variant (yaw sweep). meta.json is written only after all frames exist."""
    I._bpy()
    bpy = I.bpy
    from mathutils import Vector
    spec = ASSETS[name]
    assert variant in spec.variants, f'{name} has variants {spec.variants}'
    sz = size or spec.size or SIZE
    res = (sz, sz)
    if preview:
        res = (sz // 2, sz // 2)
    spp = samples or (16 if preview else SAMPLES)
    sc = I.reset(res, spp, 'day')
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    tilt = I.empty('tilt')
    tilt.rotation_euler = (math.radians(spec.tilt), 0, 0)
    root = I.empty('root', tilt)
    turn = I.empty('turn', root)
    turn.rotation_euler = (0, 0, math.radians(spec.base_yaw))
    q = 0.6 if preview else 1.0
    t0 = time.time()
    opts = spec.fn(turn, variant, q) or {}
    I.world('day', metal=opts.get('metal', False))
    I.rig('day', opts.get('rig_scale', 1.0), opts.get('key', 1.0), soft_top=opts.get('soft_top', False))
    bpy.context.view_layer.update()
    frame_camera(root, np.linspace(YAW_RANGE[0], YAW_RANGE[1], 9), aspect=1.0)
    for o in opts.get('hide', []):
        o.hide_render = True
    n = YAW_FRAMES
    feats = opts.get('features', {})
    fpf = {k: [None] * n for k in feats}

    def upd(i, nn):
        root.rotation_euler = (0, 0, math.radians(yaw_of(i, nn)))
        bpy.context.view_layer.update()
        for k, p in feats.items():
            w = turn.matrix_world @ Vector(p)
            fpf[k][i] = [round(v, 1) for v in I.project_px(tuple(w))]
    outdir = os.path.join(PREVIEW3D if preview else OUT3D, name, variant)
    os.makedirs(outdir, exist_ok=True)
    meta_p = os.path.join(outdir, 'meta.json')
    if os.path.exists(meta_p) and not preview:
        os.remove(meta_p)        # a re-render: pollers must not see a stale 'complete' marker
    if preview and frames is None:
        frames = [0, n // 2, n - 1]
    print(f'{name}/{variant}: built in {time.time() - t0:.0f}s; rendering {res[0]}px {spp}spp', flush=True)
    t1 = time.time()
    I.render_frames(outdir, n, upd, frames, prefix=f'{name}/{variant}')
    have = all(os.path.exists(os.path.join(outdir, f'{i:04d}.png')) for i in range(n))
    root.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    pivot = I.project_px(tuple(root.matrix_world.translation))
    meta = dict(name=name, variant=variant, mode='yaw', frames=n, fps_hint=30, size=list(res), loop=False,
                yaw_range=list(YAW_RANGE), axis='z', pivot=[round(pivot[0], 1), round(pivot[1], 1)],
                notes=spec.notes + f'; yaw sweep -40..+40 deg in {n} frames (frame i = -40 + 80*i/{n - 1} deg)',
                samples=spp, preview=bool(preview), tilt_deg=spec.tilt, base_yaw_deg=spec.base_yaw,
                source='assets3d_household.py')
    if feats:
        meta['features'] = {k: v[n // 2] for k, v in fpf.items() if v[n // 2] is not None}
        if all(all(p is not None for p in v) for v in fpf.values()):
            meta['features_per_frame'] = fpf
    if have:
        I.write_meta(outdir, **meta)        # LAST: every frame is on disk
    print(f'done {name}/{variant} in {time.time() - t1:.0f}s -> {outdir}' + ('' if have else ' (partial: no meta)'),
          flush=True)
    return outdir


# ============================================================================= contact sheets

ICON_DAY_SET = [('coin_gbp', 'day'), ('coin_gbp', 'day_spin'), ('house', 'day'), ('heart', 'day'),
                ('orbs', 'day'), ('check_tile', 'day')]


def _tile(path, cell):
    import cv2
    im = I._read_rgba_lin(path)
    tile = I._bg(cell, cell, 'day')
    if im is None:
        return tile
    im = cv2.resize(im, (cell, cell), interpolation=cv2.INTER_AREA)
    return im[:, :, :3] + tile * (1 - im[:, :, 3:4])


def _to8(row):
    srgb = np.where(row <= 0.0031308, row * 12.92, 1.055 * np.power(np.clip(row, 0, None), 1 / 2.4) - 0.055)
    return np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8)[:, :, ::-1].copy()


def sheet(root_dir=None, out=None, cell=220, names=None, per_row=2):
    """Every rendered asset/variant: first, middle and last frame (static: all frames) on ivory, labelled."""
    import cv2
    root_dir = root_dir or OUT3D
    out = out or os.path.join(SELFTEST, 'assets3d_household_contact.png')
    entries = []
    order = (names or ([f'{a}/{v}' for a, v in ICON_DAY_SET] + [f'{n}/{v}' for n in sorted(ASSETS, key=lambda k: ASSETS[k].priority)
                                                                for v in ASSETS[n].variants]))
    for key in order:
        d = os.path.join(root_dir, key)
        fs = sorted(f for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []
        if not fs:
            continue
        pick = fs if len(fs) <= 6 else [fs[0], fs[len(fs) // 2], fs[-1]]
        if key.endswith('spin') and len(fs) > 6:    # 0 / 180 / 352 deg all face the camera: add a turning frame
            pick = [fs[0], fs[len(fs) // 8], fs[len(fs) // 2], fs[-1]]
        meta = {}
        try:
            meta = json.load(open(os.path.join(d, 'meta.json')))
        except Exception:
            pass
        tiles = [_tile(os.path.join(d, f), cell) for f in pick]
        row = _to8(np.concatenate(tiles, 1))
        lab = f"{key}  {meta.get('mode', '?')} {meta.get('frames', len(fs))}f {meta.get('size', ['?'])[0]}px" + \
              ('' if meta else '  (NO META)')
        cv2.putText(row, lab, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 30, 50), 1, cv2.LINE_AA)
        entries.append(row)
    if not entries:
        return None
    w = max(r.shape[1] for r in entries)
    entries = [np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0)), constant_values=255) for r in entries]
    rows = []
    for k in range(0, len(entries), per_row):
        grp = entries[k:k + per_row]
        while len(grp) < per_row:
            grp.append(np.full_like(entries[0], 255))
        rows.append(np.concatenate([np.pad(g, ((0, 4), (0, 6), (0, 0)), constant_values=255) for g in grp], 1))
    img = np.concatenate(rows, 0)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cv2.imwrite(out, img)
    return out


# ============================================================================= CLI

def _parse(argv):
    names, o = [], {'preview': False, 'variant': None, 'frames': None, 'samples': None, 'size': None}
    it = iter(argv)
    for a in it:
        if a == '--preview':
            o['preview'] = True
        elif a == '--variant':
            o['variant'] = next(it)
        elif a == '--frames':
            o['frames'] = [int(x) for x in next(it).split(',')]
        elif a == '--samples':
            o['samples'] = int(next(it))
        elif a == '--size':
            o['size'] = int(next(it))
        else:
            names.append(a)
    return names, o


def main(argv):
    names, o = _parse(argv)
    if names == ['sheet']:
        print(sheet())
        return
    if names == ['previewsheet']:
        print(sheet(PREVIEW3D, os.path.join(PREVIEW3D, 'household_preview.png'), cell=200, per_row=2,
                    names=[f'{n}/{v}' for n in ASSETS for v in ASSETS[n].variants]))
        return
    if names == ['all']:
        names = sorted(ASSETS, key=lambda k: ASSETS[k].priority)
    for name in names:
        for v in ([o['variant']] if o['variant'] else ASSETS[name].variants):
            render_asset(name, v, o['preview'], o['frames'], o['samples'], o['size'])


if __name__ == '__main__':
    main(sys.argv[1:])
