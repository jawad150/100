"""assets3d_everyday.py - "everyday life" 3D props for animated reels #1 (Day in the Life) and #4 (GBP 447.60).

Glossy candy-plastic toy props in the established studio look (assets3d_icons.py / assets3d_hero.py):
the same day world, key/fill/rim rig and reflection cards, Cycles CPU + OpenImageDenoise, 80 mm camera
5 degrees above the subject, and the same transparent RGBA PNG + meta.json output that sprites3d loads.
Geometry is procedural: implicit surfaces (assets3d_icons' numpy SDF toolkit, assets3d_hero's SDF2/Slab
for traced outlines), meshed with hero's surface nets with analytic normals, then rendered through
hero's Blender helpers (reset / world / rig / m_candy / frame_camera / write_meta).

CLI
---
    python3 assets3d_everyday.py <name> [<name> ...] [--mode yaw|static|side] [--preview] [--samples N]
    python3 assets3d_everyday.py all            # every asset, every mode, in priority order (finals)
    python3 assets3d_everyday.py previewsheet   # sheet of the --preview renders -> out/selftest/assets3d_everyday_preview.png
    python3 assets3d_everyday.py sheet          # finals contact sheet -> out/selftest/assets3d_everyday_contact.png
    python3 assets3d_everyday.py selftest       # numpy checks + tiny renders + finals sheet

    --preview  480 px, 16 spp, frames first/mid/last, written to workspace3/out/preview3d/ (finals untouched)
    env EVERYDAY_SAMPLES (final spp, default 64, OIDN), EVERYDAY_THREADS (default 2), SKIP_EXISTING=1 resumes.
    Run renders with `nice -n 5` on the shared box.

Assets ('day' variant only; folder under workspace3/assets3d/<name>/)
---------------------------------------------------------------------
    child_figure   day         yaw 33  720  the orange girl (with ponytail) from the logo emblem, traced with
                   day_static  static 1     cv2.findContours from brand/logo_mark.png, extruded thick with a
                                            round bevel and a soft dome; LOGO_ORANGE candy. static = front view
                                            (yaw 0) framed on its own (fills more of the frame).
    backpack       day         yaw 33  720  ORANGE body, MAGENTA front pocket, top handle and shoulder straps,
                                            ivory zips + pulls, a little LEAF charm on the pocket zip.
    school_bus     day         yaw 33  720  cute rounded toy bus, AMBER->ORANGE body, ivory windows, MAGENTA
                   day_side    static 1     stripe, chunky INK tyres with ivory hubs. yaw 0 = front of the bus
                                            facing the camera; side = yaw +90 exactly: the bus faces
                                            SCREEN-RIGHT (drives left -> right; mirror the sprite for the
                                            other direction). features: wheel_front, wheel_back, exhaust.
    book_pencil    day         yaw 33  720  open book (MAGENTA cover, ivory pages with faint ruled lines, ORANGE
                                            ribbon) lying on a desk seen from ~45 deg up, a yellow-orange pencil
                                            resting on the right page. features: pencil_tip (graphite point),
                                            page_l, page_r (page centres) - e.g. to draw the pencil's scribble.
    mixing_bowl    day         yaw 33  720  PEACH bowl (ivory inside, thin MAGENTA band), golden swirled batter,
                                            a silicone whisk (MAGENTA wires, ORANGE handle); seen from ~30 deg up.
                                            features: batter (centre of the batter surface), whisk_top.
    cupcake        day         yaw 33  720  ORANGE pleated liner, pink/MAGENTA frosting swirl, sprinkles, a
                                            glossy cherry on top. features: top.
    alarm_clock    day         yaw 33  720  ORANGE twin-bell clock, ivory face, hands at 8:15, MAGENTA feet.
                                            features: face (dial centre), bell_l, bell_r.
    family_figures day         yaw 33  720  two rounded pawn-style figures holding hands: a taller MAGENTA adult
                                            (left) and a smaller ORANGE child (right). features: hands.

    yaw: frame i shows yaw = -40 + 80 * i / 32 degrees (positive yaw turns the front towards screen-right).
    Every asset fills ~80 % of the frame over the whole sweep; static/side frames are framed on their own.

Output (shared 3D asset spec, see sprites3d.py)
-----------------------------------------------
    workspace3/assets3d/<name>/<folder>/0000.png ...  RGBA 8-bit, straight alpha, sRGB ('Standard' view)
    workspace3/assets3d/<name>/<folder>/meta.json     written LAST, only once every frame is on disk
        {name, variant (folder), mode: 'yaw'|'static', frames, fps_hint, yaw_range (yaw) | yaw (static),
         size, anchor (visual centre px), bbox (union alpha bbox), ground_y (lowest opaque row), pivot
         (projected rotation axis at the object's base), axis 'z', loop, notes, samples, preview,
         features {name: [x, y]} (yaw: at yaw 0), features_per_frame {name: [[x, y] per frame]} (yaw)}

    import sprites3d as S3
    bus = S3.get('school_bus', 'day', mode='side')     # -> folder day_side
    bag = S3.get('backpack', 'day'); img = bag.at_yaw(-12) ; tip = S3.get('book_pencil', 'day').feature('pencil_tip')

Python API (nothing runs at import; bpy is imported lazily through assets3d_hero)
---------------------------------------------------------------------------------
    import assets3d_everyday as E
    E.ASSETS['backpack']                      # dict(build, modes, size, notes, priority)
    E.girl_mask()                             # (coverage float32, bbox) of the logo girl, traced by findContours
    E.render_asset('cupcake', preview=True)   # build + render (needs bpy)
    E.contact_sheet()                         # finals sheet on ivory (first / middle / last frame)
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

import assets3d_hero as H      # noqa: E402  Blender side (rig, world, materials, camera, meta), SDF2 / Slab / mesher
import assets3d_icons as I     # noqa: E402  numpy implicit toolkit (2D sd_*, inflate, sd3_*, u_* combinators)

WS = H.WS
OUT3D = H.OUT3D
PREVIEW3D = H.PREVIEW3D
SELFTEST = H.SELFTEST
BRANDDIR = H.BRANDDIR

SAMPLES = int(os.environ.get('EVERYDAY_SAMPLES', '64'))
PREVIEW_SAMPLES = 16
THREADS = int(os.environ.get('EVERYDAY_THREADS', '2'))
VARIANT = 'day'
SIZE = (720, 720)
PREVIEW_SIZE = (480, 480)
YAW_RANGE = (-40.0, 40.0)
YAW_FRAMES = 33
FILL = 0.80

hexlin = H.hexlin
mixlin = H.mixlin
UP = (0.0, 0.0, 1.0)            # Blender object-space up (icon y) for material gradients


# ============================================================================= implicit helpers (icon frame)
# Icon frame: x right, y up, z towards the camera at yaw 0. Implicits are F(x, y, z) -> value (< 0 inside).

def field(F, lo, hi):
    """Wrap an icons-style implicit F(x, y, z) with explicit bounds for hero's mesher."""
    return H.FieldFn(lambda P: F(P[..., 0], P[..., 1], P[..., 2]), lo, hi)


def mesh_vqn(F, lo, hi, step, q=1.0):
    """(V, Q, N) of an implicit (icon frame) meshed at voxel `step / q` (no disk cache: geometry is
    still being tuned and meshing takes seconds)."""
    return H.mesh_field(field(F, lo, hi), step / q)


def mesh(name, F, lo, hi, step, mat, parent, q=1.0, shadow=True, key=None, attrs_fn=None):
    """Mesh an implicit (icon frame) at voxel `step / q` and add it under `parent`.
    attrs_fn(V_icon) -> {name: per-vertex float} for shader attributes."""
    V, Q, N = mesh_vqn(F, lo, hi, step, q)
    o = H.add_mesh(name, V, Q, N, mat, parent=parent, attrs=attrs_fn(V) if attrs_fn else None)
    o.visible_shadow = shadow
    return o


def xform_vn(V, N, R=None, t=(0.0, 0.0, 0.0)):
    """Rigidly move icon-frame vertices / normals: V @ R.T + t."""
    R = np.eye(3) if R is None else np.asarray(R, float)
    return np.asarray(V) @ R.T + np.asarray(t, float), np.asarray(N) @ R.T


def rotm(rx=0.0, ry=0.0, rz=0.0):
    """Icon-frame rotation matrix R = Rz Ry Rx (radians), the same convention as icons.u_xform."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def tilted_root(tilt_deg):
    """A fixed 'view tilt' empty (top of the object leaning towards the camera by tilt_deg, i.e. the
    turntable seen from higher up) with the yaw root under it. Returns (tilt, root)."""
    tilt = H.empty('tilt')
    tilt.rotation_euler = (math.radians(tilt_deg), 0.0, 0.0)
    root = H.empty('root', parent=tilt)
    return tilt, root


def rot2(x, y, ang):
    c, s = math.cos(ang), math.sin(ang)
    return c * x - s * y, s * x + c * y


def height_map(F, x0, y0, x1, y1, res=256, zlo=-0.2, zhi=1.5, iters=22):
    """Front surface height z(x, y) of an implicit (largest z with F < 0), as a bilinear sampler.
    Outside the shape the height falls back to the nearest inside value (so decals never fly off)."""
    from scipy.ndimage import map_coordinates, distance_transform_edt
    nx = res
    ny = max(8, int(round(res * (y1 - y0) / (x1 - x0))))
    X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    inside = F(X, Y, np.full_like(X, zlo)) < 0
    a = np.full_like(X, zlo)
    b = np.full_like(X, zhi)
    for _ in range(iters):
        m = (a + b) / 2
        ins = F(X, Y, m) < 0
        a = np.where(ins, m, a)
        b = np.where(ins, b, m)
    Z = np.where(inside, a, np.nan)
    if (~inside).any() and inside.any():
        _, (iy, ix) = distance_transform_edt(~inside, return_indices=True)
        Z = Z[iy, ix]
    Z = np.nan_to_num(Z, nan=zlo)
    sx = (nx - 1) / (x1 - x0)
    sy = (ny - 1) / (y1 - y0)

    def zb(x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        u = np.clip((x - x0) * sx, 0, nx - 1)
        v = np.clip((y - y0) * sy, 0, ny - 1)
        shp = np.broadcast(u, v).shape
        out = map_coordinates(Z, [np.broadcast_to(v, shp).ravel(), np.broadcast_to(u, shp).ravel()], order=1,
                              mode='nearest')
        return out.reshape(shp)
    return zb


def decal(sd2, zb, thick, edge=None, embed=0.02, dome=0.0, dome_field=None):
    """A rounded slab of 2D shape `sd2` that hugs a front surface z = zb(x, y): its back sits `embed`
    below the surface and it rises `thick` above it (pockets, straps, zips, stripes)."""
    half = (thick + embed) / 2
    edge = min(half, edge if edge is not None else half)
    flat = I.inflate(sd2, thick=half, edge=edge, dome=dome, dome_field=dome_field)

    def F(x, y, z):
        return flat(x, y, z - (zb(x, y) - embed + half))
    return F


def round_cyl(axis, c, r, half, edge):
    """Rounded cylinder (radius r, half length `half`, edge radius `edge`) along axis 'x' | 'y' | 'z'."""
    def F(x, y, z):
        px, py, pz = x - c[0], y - c[1], z - c[2]
        if axis == 'x':
            rad, ax = np.hypot(py, pz), px
        elif axis == 'y':
            rad, ax = np.hypot(px, pz), py
        else:
            rad, ax = np.hypot(px, py), pz
        wx = rad - r + edge
        wy = np.abs(ax) - half + edge
        return np.minimum(np.maximum(wx, wy), 0) + np.hypot(np.maximum(wx, 0), np.maximum(wy, 0)) - edge
    return F


def revolve(profile_sd, c=(0.0, 0.0, 0.0)):
    """Solid of revolution about the vertical (y) axis through c: profile_sd(r, y) is a 2D sd in the
    (radius, height) half plane."""
    def F(x, y, z):
        return profile_sd(np.hypot(x - c[0], z - c[2]), y - c[1])
    return F


def capsule_chain(pts, r):
    """Union of capsules along a 3D polyline (thin tubes: wires, handles, stems). r may be a list."""
    pts = [np.asarray(p, float) for p in pts]
    rs = r if isinstance(r, (list, tuple, np.ndarray)) else [r] * len(pts)

    def F(x, y, z):
        d = None
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            ba = b - a
            bb = max(float(ba @ ba), 1e-12)
            px, py, pz = x - a[0], y - a[1], z - a[2]
            h = np.clip((px * ba[0] + py * ba[1] + pz * ba[2]) / bb, 0, 1)
            rr = rs[k] + (rs[k + 1] - rs[k]) * h
            dk = np.sqrt((px - ba[0] * h) ** 2 + (py - ba[1] * h) ** 2 + (pz - ba[2] * h) ** 2) - rr
            d = dk if d is None else np.minimum(d, dk)
        return d
    return F


def bounds_of_pts(pts, pad):
    P = np.asarray(pts, float)
    return tuple(P.min(0) - pad), tuple(P.max(0) + pad)


# ============================================================================= materials (studio family)

def candy(name, color, rim=None, rim_str=0.25, rough=0.27, coat_r=0.035, grad=None, **kw):
    """The family candy plastic (hero m_candy) with a fresnel 'inner light' rim instead of costly SSS.
    grad=(color_b, z_lo, z_hi): vertical (object space) gradient towards color_b."""
    g = None
    if grad:
        cb, lo, hi = grad
        g = (cb, UP, lo, hi)
    return H.m_candy(name, color, rough=rough, coat_r=coat_r, sss=0.0, rim=rim, rim_str=rim_str, grad=g, **kw)


def mat_orange(name='orange', **kw):
    return candy(name, 'ORANGE', rim='AMBER', rim_str=0.28, **kw)


def mat_magenta(name='magenta', **kw):
    return candy(name, 'MAGENTA', rim='HOT_PINK', rim_str=0.25, **kw)


def mat_ivory(name='ivory', **kw):
    kw.setdefault('rough', 0.3)
    return candy(name, 'IVORY', rim=None, **kw)


def mat_ink(name='ink', **kw):
    kw.setdefault('rough', 0.32)
    return candy(name, mixlin('INK', 'PLUM', 0.25), rim='PLUM', rim_str=0.35, **kw)


def mat_leaf(name='leaf', **kw):
    return H.m_candy(name, 'LOGO_LEAF', rough=0.27, coat_r=0.04, sss=0.0, rim='LEAF_HI', rim_str=0.25, **kw)


def m_metal(name, base=(0.86, 0.84, 0.83), edge=(1.0, 0.98, 0.96), rough=0.16):
    """Polished silver-ish metal (whisk wires): reflects the warm ivory day world."""
    m, b, nt = H._principled(name)
    b.inputs['Base Color'].default_value = tuple(base) + (1.0,)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular Tint'].default_value = tuple(edge) + (1.0,)
    return m


def _math(nt, op, a, b=None, clamp=False):
    n = nt.nodes.new('ShaderNodeMath')
    n.operation = op
    n.use_clamp = clamp
    for k, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[k].default_value = float(v)
        else:
            nt.links.new(v, n.inputs[k])
    return n.outputs[0]


def m_pages(name, spacing=0.075, line_col=None, strength=0.8):
    """Ivory paper with faint ruled lines: lines where frac(pv / spacing) ~ 0.5 (per-vertex attribute 'pv'
    = the page's own 'down the page' coordinate, exact under interpolation), masked by the per-vertex
    'ptop' attribute (top face, inside the margins)."""
    m, b, nt = H._principled(name)
    col = tuple(0.84 * c for c in mixlin('IVORY', 'PEACH', 0.12)) + (1.0,)     # up-facing paper: keep out of clip
    lc = H._col4(line_col or mixlin('LAVENDER', 'PLUM', 0.42))
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = 0.42
    b.inputs['Coat Weight'].default_value = 0.6
    b.inputs['Coat Roughness'].default_value = 0.08
    av = nt.nodes.new('ShaderNodeAttribute')
    av.attribute_name = 'pv'
    at = nt.nodes.new('ShaderNodeAttribute')
    at.attribute_name = 'ptop'
    t = _math(nt, 'DIVIDE', av.outputs['Fac'], spacing)
    f = _math(nt, 'FRACT', t)
    f = _math(nt, 'SUBTRACT', f, 0.5)
    f = _math(nt, 'ABSOLUTE', f)
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = 0.05
    mr.inputs['From Max'].default_value = 0.10
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    nt.links.new(f, mr.inputs['Value'])
    k = _math(nt, 'MULTIPLY', mr.outputs[0], at.outputs['Fac'])
    k = _math(nt, 'MULTIPLY', k, strength)
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = col
    mix.inputs['B'].default_value = lc
    nt.links.new(k, mix.inputs['Factor'])
    nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    return m


def m_two_tone(name, outer, inner, rough=0.27, rim=None, rim_str=0.2, band=None):
    """Candy plastic whose colour depends on the side of a bowl wall: `outer` where the object-space
    normal points away from the vertical axis, `inner` where it points towards it (one mesh, no seam).
    band=(color, z0, z1): an outside decorative band between object-space heights z0..z1."""
    m = H.m_candy(name, outer, rough=rough, coat_r=0.035, sss=0.0, rim=rim, rim_str=rim_str)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    sn = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sp.inputs[0])
    nt.links.new(tc.outputs['Normal'], sn.inputs[0])
    d = _math(nt, 'ADD', _math(nt, 'MULTIPLY', sp.outputs['X'], sn.outputs['X']),
              _math(nt, 'MULTIPLY', sp.outputs['Y'], sn.outputs['Y']))
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = -0.04
    mr.inputs['From Max'].default_value = 0.04
    nt.links.new(d, mr.inputs['Value'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = H._col4(inner)
    mix.inputs['B'].default_value = H._col4(outer)
    nt.links.new(mr.outputs[0], mix.inputs['Factor'])
    res = mix.outputs['Result']
    if band:
        bc, z0, z1 = band
        lo = nt.nodes.new('ShaderNodeMapRange')
        lo.interpolation_type = 'SMOOTHSTEP'
        lo.inputs['From Min'].default_value = z0 - 0.006
        lo.inputs['From Max'].default_value = z0 + 0.006
        nt.links.new(sp.outputs['Z'], lo.inputs['Value'])
        hi = nt.nodes.new('ShaderNodeMapRange')
        hi.interpolation_type = 'SMOOTHSTEP'
        hi.inputs['From Min'].default_value = z1 + 0.006
        hi.inputs['From Max'].default_value = z1 - 0.006
        nt.links.new(sp.outputs['Z'], hi.inputs['Value'])
        k = _math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', lo.outputs[0], hi.outputs[0]), mr.outputs[0])
        mix2 = nt.nodes.new('ShaderNodeMix')
        mix2.data_type = 'RGBA'
        nt.links.new(res, mix2.inputs['A'])
        mix2.inputs['B'].default_value = H._col4(bc)
        nt.links.new(k, mix2.inputs['Factor'])
        res = mix2.outputs['Result']
    nt.links.new(res, b.inputs['Base Color'])
    return m


# ============================================================================= registry

ASSETS = {}


def asset(name, modes=('yaw',), size=SIZE, notes='', priority=9, fill=FILL):
    def deco(fn):
        ASSETS[name] = dict(name=name, build=fn, modes=tuple(modes), size=tuple(size), notes=notes,
                            priority=priority, fill=fill)
        return fn
    return deco


MODE_POSES = {
    'yaw': dict(folder='day', frames=YAW_FRAMES, frame_yaws=list(np.linspace(*YAW_RANGE, 9))),
    'static': dict(folder='day_static', frames=1, yaw=0.0, frame_yaws=[0.0]),
    'side': dict(folder='day_side', frames=1, yaw=90.0, frame_yaws=[90.0]),
}


def yaw_of(i, n=YAW_FRAMES):
    return YAW_RANGE[0] + (YAW_RANGE[1] - YAW_RANGE[0]) * i / (n - 1)


# ============================================================================= 2. child_figure

LOGO_INKS = {'magenta': '#A6055E', 'orange': '#F46308', 'leaf': '#64A60C'}


def girl_mask():
    """Trace the orange girl (with the ponytail) in brand/logo_mark.png: label every opaque pixel by its
    nearest logo ink, cv2.findContours on the orange mask, keep the two tall child figures and take the
    left one (the girl). Returns (coverage float32 (h, w) cropped to her bbox + 24 px, (x, y, w, h) bbox
    of the crop in logo px)."""
    import cv2
    im = cv2.imread(os.path.join(BRANDDIR, 'logo_mark.png'), cv2.IMREAD_UNCHANGED)
    a = im[:, :, 3].astype(np.float32) / 255.0
    rgb = im[:, :, 2::-1].astype(np.float32)
    refs = np.stack([np.linalg.norm(rgb - np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32), axis=2)
                     for h in LOGO_INKS.values()], 0)
    lab = refs.argmin(0)
    orange = (lab == 1) & (a > 0.5)
    cnts, _ = cv2.findContours(orange.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    figs = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if cv2.contourArea(c) > 5000 and h > 300:       # the two children (the heart is short and wide)
            figs.append((x + w / 2.0, c, (x, y, w, h)))
    assert len(figs) >= 2, f'expected two child figures in the logo, found {len(figs)}'
    figs.sort(key=lambda f: f[0])
    _, girl, (x, y, w, h) = figs[0]
    region = np.zeros(a.shape, np.uint8)
    cv2.drawContours(region, [girl], -1, 1, -1)
    region = cv2.dilate(region, np.ones((5, 5), np.uint8))
    cov = np.where(lab == 1, a, 0.0).astype(np.float32) * region
    pad = 24
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(a.shape[1], x + w + pad), min(a.shape[0], y + h + pad)
    return cov[y0:y1, x0:x1].copy(), (x0, y0, x1 - x0, y1 - y0)


@asset('child_figure', ('yaw', 'static'), priority=2,
       notes='The orange girl with the ponytail from the logo emblem (traced from logo_mark.png with '
             'cv2.findContours), extruded thick with a round bevel and soft dome; LOGO_ORANGE candy.')
def build_child(q):
    root = H.empty('root')
    cov, _ = girl_mask()
    ys, xs = np.nonzero(cov > 0.5)
    height = 2.0
    px = height / (ys.max() - ys.min() + 1)
    cx, cy = (xs.min() + xs.max()) / 2.0, (ys.min() + ys.max()) / 2.0
    origin = (-cx * px, cy * px)
    sd = H.SDF2.from_mask(cov, px, origin=origin, up=2, blur=0.8)
    dsd = H.SDF2.from_mask(cov, px, origin=origin, up=1, blur=10.0)
    f = H.Slab(sd, h=0.15, r=0.068, rz=0.10, dome=0.08, dome_w=0.16, dome_sd=dsd)
    V, Q, N = H.mesh_field(f, 0.0055 / q, cache_key=f'everyday:girl:v1:{q:.2f}')
    mat = H.m_candy('girl', 'LOGO_ORANGE', rough=0.27, coat_r=0.035, sss=0.0, rim='AMBER', rim_str=0.28,
                    grad=(mixlin('LOGO_ORANGE', 'AMBER', 0.22), UP, -0.6, 1.1))
    H.add_mesh('girl', V, Q, N, mat, parent=root)
    foot = float(V[:, 1].min())
    return {'root': root, 'rig_scale': 1.15, 'pivot': (0.0, 0.0, foot)}


# ============================================================================= 3. backpack

@asset('backpack', priority=3,
       notes='Toy backpack: ORANGE body, MAGENTA front pocket + top handle + shoulder straps, ivory zips and '
             'pulls, a small LEAF charm on the pocket zip.')
def build_backpack(q):
    root = H.empty('root')
    # ---- body: a tombstone outline (x, y) inflated into a puffy pillow
    shape = I.op_smin(I.sd_rbox(0.0, -0.22, 0.76, 0.74, 0.34), I.sd_ellipse_approx(0.0, 0.18, 0.76, 0.78), 0.12)
    sd = I.fn_sd(shape, (-1.0, -1.15, 1.0, 1.15), 900)
    dfield = sd.poisson()
    Fb = I.inflate(sd, thick=0.27, edge=0.24, dome=0.17, dome_field=dfield, dome_pow=0.6)
    mo = mat_orange('bag_orange', grad=(mixlin('ORANGE', 'AMBER', 0.18), -0.9, 1.0))
    mesh('body', Fb, (-0.85, -1.05, -0.5), (0.85, 1.05, 0.5), 0.008, mo, root, q, key='bag_body:v1')
    zb = height_map(Fb, -0.85, -1.05, 0.85, 1.05, res=300)
    # ---- front pocket (MAGENTA), hugging the body front
    pk = I.fn_sd(I.sd_rbox(0.0, -0.46, 0.53, 0.37, 0.2), (-0.7, -0.95, 0.7, 0.0), 500)
    Fp = decal(pk, zb, thick=0.11, edge=0.07, embed=0.03, dome=0.04, dome_field=pk.poisson())
    mm = mat_magenta('bag_magenta')
    mesh('pocket', Fp, (-0.62, -0.88, -0.1), (0.62, -0.04, 0.6), 0.005, mm, root, q, key='bag_pocket:v1')
    zp = height_map(lambda x, y, z: np.minimum(Fb(x, y, z), Fp(x, y, z)), -0.85, -1.05, 0.85, 1.05, res=300)
    # ---- zips (ivory): main compartment arc + pocket top line
    mi = mat_ivory('bag_ivory')
    zip_main = I.fn_sd(lambda x, y: np.maximum(np.abs(shape(x, y) + 0.15) - 0.022, -0.02 - y),
                       (-1.0, -0.4, 1.0, 1.15), 900)
    mesh('zip_main', decal(zip_main, zb, thick=0.03, edge=0.015), (-0.8, -0.15, -0.1), (0.8, 1.0, 0.65), 0.004,
         mi, root, q, key='bag_zip_main:v1')
    zip_pk = I.fn_sd(I.sd_segment(-0.40, -0.17, 0.40, -0.17, 0.02), (-0.6, -0.3, 0.6, -0.05), 400)
    mesh('zip_pocket', decal(zip_pk, zp, thick=0.025, edge=0.012), (-0.5, -0.24, 0.0), (0.5, -0.1, 0.7), 0.003,
         mi, root, q, key='bag_zip_pk:v1')
    # zip pulls: rounded tabs hanging from the zip ends
    pulls = []
    for (px_, py_, ang) in ((0.40, -0.17, -0.05), (-0.70, 0.02, 0.35), (0.70, 0.02, -0.35)):
        z0 = float(zp(px_, py_)) if py_ < -0.1 else float(zb(px_ * 0.97, py_))
        tab = I.sd3_round_box((0, -0.075, 0), (0.035, 0.075, 0.014), 0.013)
        ring = I.sd3_torus((0, 0.005, 0), 0.03, 0.009, axis='z')
        Ft = I.u_xform(I.u_smin(tab, ring, 0.01), t=(px_, py_, z0 + 0.03), rz=ang, rx=-0.25)
        pulls.append(Ft)
    mesh('zip_pulls', I.u_min(*pulls), (-0.85, -0.45, -0.1), (0.85, 0.15, 0.75), 0.0025, mi, root, q,
         key='bag_pulls:v1')
    # ---- top handle (MAGENTA loop) and shoulder straps (behind, peeking out at the sides)
    ytop = 0.96
    handle = I.u_isect(I.sd3_torus((0.0, ytop - 0.06, -0.02), 0.22, 0.055, axis='z'),
                       lambda x, y, z: (ytop - 0.02) - y)
    mesh('handle', handle, (-0.32, ytop - 0.1, -0.12), (0.32, ytop + 0.25, 0.1), 0.004, mm, root, q,
         key='bag_handle:v1')
    straps = []
    for sx in (-1, 1):
        pts2 = [(0.56, -0.22), (0.70, -0.40), (0.52, -0.58), (0.0, -0.62), (-0.55, -0.52), (-0.86, -0.32)]
        s2 = I.sd_polyline(pts2, 0.04)                      # (y, z) side profile of the strap loop
        F = I.extrude_axis(lambda y, z, s2=s2: s2(y, z), 'x', 0.105, 0.04)
        straps.append(I.u_xform(F, t=(sx * 0.40, 0.0, 0.0), rz=sx * math.radians(9)))
    mesh('straps', I.u_min(*straps), (-0.75, -1.0, -0.72), (0.75, 1.0, -0.12), 0.006, mm, root, q,
         key='bag_straps:v1')
    # ---- leaf charm hanging from the pocket pull
    V, Q, N, vein, ln = H.leaf_mesh('leaf_top', length=0.36, h=0.024, cup=0.35, curl=0.25, q=q)
    ang = math.radians(-160)
    c, s = math.cos(ang), math.sin(ang)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    T = np.array([0.40 + 0.03, -0.17 - 0.155, float(zp(0.40, -0.17)) + 0.05])
    V2 = V @ R.T + T
    N2 = N @ R.T
    H.add_mesh('charm', V2, Q, N2, H.m_candy('charm', 'LOGO_LEAF', rough=0.27, coat_r=0.04, sss=0.0,
                                             attr_mix=('vein', 'LEAF_HI'), rim='LEAF_HI', rim_str=0.25),
               parent=root, attrs={'vein': vein})
    return {'root': root, 'rig_scale': 1.15, 'pivot': (0.0, 0.0, -1.0)}


def smin(a, b, k):
    """Polynomial smooth union of two distance arrays (fillet ~k)."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    """Polynomial smooth intersection of two distance arrays (rounded crease ~k)."""
    h = np.clip(0.5 - 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h + k * h * (1 - h)


def tube_mesh(pts, r, sides=10, closed=False, up=None):
    """Swept circular tube along a polyline (wires): returns (V, Q, N) in the same frame as pts. For a
    planar curve pass up = the plane normal (twist-free frames, seamless when closed)."""
    P = np.asarray(pts, float)
    n = len(P)
    if closed:
        T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    else:
        T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    if up is not None:
        up = np.asarray(up, float) / np.linalg.norm(up)
        Nr = np.cross(T, up)
    else:
        Nr = np.zeros_like(T)
        a = np.array([0.0, 0.0, 1.0]) if abs(T[0, 2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        v = np.cross(T[0], a)
        for i in range(n):
            v = v - (v @ T[i]) * T[i]
            v /= np.linalg.norm(v)
            Nr[i] = v
    Nr /= np.maximum(np.linalg.norm(Nr, axis=1, keepdims=True), 1e-12)
    Bn = np.cross(T, Nr)
    ang = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    D = np.cos(ang)[None, :, None] * Nr[:, None, :] + np.sin(ang)[None, :, None] * Bn[:, None, :]
    V = (P[:, None, :] + r * D).reshape(-1, 3)
    N = D.reshape(-1, 3)
    rows = n if closed else n - 1
    i = np.arange(rows)[:, None]
    j = np.arange(sides)[None, :]
    i1, j1 = (i + 1) % n, (j + 1) % sides
    Q = np.stack([i * sides + j, i * sides + j1, i1 * sides + j1, i1 * sides + j], -1).reshape(-1, 4)
    # outward winding check on the first quad
    a, b, c = V[Q[0, 0]], V[Q[0, 1]], V[Q[0, 2]]
    if np.cross(b - a, c - a) @ N[Q[0, 0]] < 0:
        Q = Q[:, ::-1]
    return V, Q, N


def merge_meshes(parts):
    """Concatenate [(V, Q, N), ...] into one (V, Q, N)."""
    Vs, Qs, Ns, off = [], [], [], 0
    for V, Q, N in parts:
        Vs.append(V)
        Ns.append(N)
        Qs.append(np.asarray(Q) + off)
        off += len(V)
    return np.concatenate(Vs), np.concatenate(Qs), np.concatenate(Ns)


def ib(p):
    """Icon-frame point -> Blender (root-local) point, for features / pivots."""
    return (float(p[0]), float(-p[2]), float(p[1]))


def sd_hex(r_in, round_r=0.0):
    """2D regular hexagon (flat sides at +-r_in along the first axis' normal), rounded by round_r."""
    kx, ky, kz = -0.8660254, 0.5, 0.57735027
    r = r_in - round_r

    def f(x, y):
        px, py = np.abs(x), np.abs(y)
        d = np.minimum(kx * px + ky * py, 0.0)
        px, py = px - 2 * d * kx, py - 2 * d * ky
        cx = np.clip(px, -kz * r, kz * r)
        qx, qy = px - cx, py - r
        return np.hypot(qx, qy) * np.sign(qy) - round_r
    return f


def scatter_on(V, N, n, mask, min_dist, seed=3):
    """Pick up to n well-spaced vertices (greedy, random order) where mask is True."""
    rng = np.random.default_rng(seed)
    idx = np.nonzero(mask)[0]
    rng.shuffle(idx)
    out = []
    for i in idx:
        p = V[i]
        if all(np.linalg.norm(p - V[j]) >= min_dist for j in out):
            out.append(i)
            if len(out) >= n:
                break
    return out


def frame_from_normal(n, ang):
    """Rotation whose x axis is a tangent at angle `ang` in the plane normal to n (z = n)."""
    n = n / np.linalg.norm(n)
    a = np.array([0.0, 1.0, 0.0]) if abs(n[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    t1 = np.cross(a, n)
    t1 /= np.linalg.norm(t1)
    t2 = np.cross(n, t1)
    x = math.cos(ang) * t1 + math.sin(ang) * t2
    y = np.cross(n, x)
    return np.stack([x, y, n], 1)


# ============================================================================= 4. school_bus

BUS = dict(L=1.12, W=0.60, yb=-0.47, yt=0.80, r=0.22, wy=-0.50, wr=0.30, wz=(0.70, -0.68), wx=0.50, whw=0.13)


@asset('school_bus', ('yaw', 'side'), priority=4,
       notes='Cute rounded toy bus: AMBER->ORANGE body, ivory windows / windscreen / door, MAGENTA stripe, chunky INK '
             'tyres with ivory hubs, ivory headlights, MAGENTA roof lights.')
def build_bus(q):
    tilt, root = tilted_root(8.0)
    B = BUS
    L, Wd, yb, yt = B['L'], B['W'], B['yb'], B['yt']
    yc, hh = (yb + yt) / 2, (yt - yb) / 2
    body0 = I.sd3_round_box((0, yc, 0), (Wd, hh, L), B['r'])
    for wz in B['wz']:
        body0 = I.u_ssub(body0, round_cyl('x', (0, B['wy'], wz), 0.37, 0.9, 0.03), 0.05)
    # windows: side panes (y, z) on both sides, the door on the camera-left (-x) side, windscreen, rear window
    side_w = [I.sd_rbox(0.40, zc, 0.17, 0.15, 0.07) for zc in (-0.76, -0.38, 0.0, 0.38)]
    win_px = I.op_union(*(side_w + [I.sd_rbox(0.40, 0.76, 0.17, 0.15, 0.07)]))    # +x side: + driver window
    win_nx = I.op_union(*side_w)
    door2 = I.sd_rbox(0.12, 0.79, 0.43, 0.15, 0.07)                                 # (y, z), -x side
    ws2 = I.sd_rbox(0.0, 0.40, 0.45, 0.19, 0.09)                                    # (x, y) front
    rw2 = I.sd_rbox(0.0, 0.42, 0.40, 0.15, 0.08)                                    # (x, y) back
    dep = 0.05
    cuts = [I.extrude_axis(win_px, 'x', dep, 0.015, center=Wd), I.extrude_axis(win_nx, 'x', dep, 0.015, center=-Wd),
            I.extrude_axis(door2, 'x', dep, 0.015, center=-Wd), I.extrude_axis(ws2, 'z', dep, 0.015, center=L),
            I.extrude_axis(rw2, 'z', dep, 0.015, center=-L)]
    body = body0
    for c in cuts:
        body = I.u_ssub(body, c, 0.018)
    mb = candy('bus_body', 'ORANGE', rim='AMBER', rim_str=0.25, grad=(mixlin('AMBER', '#FFC93C', 0.3), -0.38, 0.32))
    lo, hi = (-0.72, yb - 0.1, -1.25), (0.72, yt + 0.06, 1.25)
    mesh('body', body, lo, hi, 0.0085, mb, root, q)
    # MAGENTA stripe hugging the body below the windows (not over the door)
    band = lambda x, y, z: np.abs(y - 0.105) - 0.05
    stripe = I.u_sisect(lambda x, y, z: body0(x, y, z) - 0.016, band, 0.012)
    stripe = I.u_ssub(stripe, I.extrude_axis(I.op_offset(door2, 0.02), 'x', 0.1, 0.02, center=-Wd), 0.01)
    mesh('stripe', stripe, (-0.66, 0.0, -1.2), (0.66, 0.21, 1.2), 0.006, mat_magenta('bus_stripe'), root, q)
    # ivory panes inset in the recesses
    mi = H.m_candy('bus_glass', 'IVORY', rough=0.2, coat_r=0.03, sss=0.0, emit='IVORY', emit_str=0.22)
    panes = [I.extrude_axis(win_px, 'x', 0.02, 0.012, center=Wd - 0.035),
             I.extrude_axis(win_nx, 'x', 0.02, 0.012, center=-Wd + 0.035),
             I.extrude_axis(ws2, 'z', 0.02, 0.012, center=L - 0.035),
             I.extrude_axis(rw2, 'z', 0.02, 0.012, center=-L + 0.035)]
    door_pane = I.extrude_axis(I.op_sub(I.op_offset(door2, -0.035), I.sd_rbox(0.12, 0.79, 0.5, 0.012, 0.0)), 'x',
                               0.02, 0.012, center=-Wd + 0.035)
    mesh('panes', I.u_min(*panes, door_pane), (-0.66, 0.15, -1.2), (0.66, 0.66, 1.2), 0.005, mi, root, q)
    # bumpers + wheels (INK), hubs (ivory), caps (MAGENTA), headlights, roof lights
    mk = mat_ink('bus_ink')
    bump = I.u_min(I.sd3_round_box((0, -0.36, L + 0.01), (0.56, 0.075, 0.075), 0.07),
                   I.sd3_round_box((0, -0.36, -L - 0.01), (0.56, 0.075, 0.075), 0.07))
    tyres, hubs, caps = [], [], []
    for wz in B['wz']:
        for sx in (-1, 1):
            tyres.append(round_cyl('x', (sx * B['wx'], B['wy'], wz), B['wr'], B['whw'], 0.10))
            hubs.append(round_cyl('x', (sx * (B['wx'] + 0.10), B['wy'], wz), 0.155, 0.045, 0.035))
            caps.append(I.sd3_sphere((sx * (B['wx'] + 0.135), B['wy'], wz), 0.06))
    mesh('ink', I.u_min(bump, *tyres), (-0.70, -0.85, -1.25), (0.70, -0.18, 1.25), 0.006, mk, root, q)
    mesh('hubs', I.u_min(*hubs), (-0.70, -0.70, -1.05), (0.70, -0.30, 1.05), 0.004, mat_ivory('bus_hub'), root, q)
    mm = mat_magenta('bus_magenta')
    roofl = [I.sd3_sphere((sx * 0.36, yt - 0.03, L - 0.16), 0.075) for sx in (-1, 1)]
    mesh('caps', I.u_min(*caps, *roofl), (-0.72, -0.6, -1.0), (0.72, yt + 0.08, 1.05), 0.004, mm, root, q)
    lamps = [I.u_sisect(I.sd3_sphere((sx * 0.34, -0.14, L - 0.02), 0.11),
                        lambda x, y, z: (L - 0.02) - z, 0.01) for sx in (-1, 1)]
    mlamp = H.m_candy('bus_lamp', 'IVORY', rough=0.12, coat_r=0.02, sss=0.0, emit=mixlin('AMBER', 'IVORY', 0.4),
                      emit_str=0.6)
    mesh('lamps', I.u_min(*lamps), (-0.5, -0.3, L - 0.1), (0.5, 0.0, L + 0.15), 0.003, mlamp, root, q)
    gy = -0.80
    return {'root': root, 'tilt': tilt, 'rig_scale': 1.2, 'pivot': ib((0, gy, 0)),
            'features': {'wheel_front': ib((-B['wx'] - 0.13, B['wy'], B['wz'][0])),
                         'wheel_back': ib((-B['wx'] - 0.13, B['wy'], B['wz'][1])),
                         'exhaust': ib((-0.35, -0.40, -L - 0.08))},
            'notes_side': 'Side view: yaw +90, the bus faces screen-right (drives left -> right); door side visible.'}


# ============================================================================= 5. book_pencil

def page_h(u):
    return 0.04 + 0.16 * (1 - np.exp(-np.maximum(u, 0) / 0.13)) - 0.05 * u


@asset('book_pencil', priority=5,
       notes='Open book (MAGENTA hardcover, ivory pages with faint ruled lines, ORANGE ribbon) lying on a desk seen '
             'from above, with a yellow-orange pencil resting on the right page.')
def build_book(q):
    tilt, root = tilted_root(40.0)
    Wp, Hp, fan = 0.92, 0.64, math.radians(12)
    prof = I.fn_sd(lambda u, w: np.maximum.reduce([0.03 - u, u - Wp, -w, w - page_h(u)]),
                   (-0.1, -0.12, 1.05, 0.36), 800).rounded(0.014, 0.0)
    mp = m_pages('pages')
    feats = {}
    for side in (1, -1):
        Fh = I.extrude_axis(lambda x, y, s=side: prof(s * x, y), 'z', Hp, 0.014)
        R = rotm(rz=side * fan)
        Vh, Qh, Nh = mesh_vqn(Fh, (min(0.0, side * 1.0), -0.05, -0.7), (max(0.0, side * 1.0), 0.28, 0.7), 0.0042, q)
        u = side * Vh[:, 0]
        v = -Vh[:, 2]
        top = H.smoothstep(0.55, 0.85, Nh[:, 1]) * H.smoothstep(0.10, 0.16, u) * H.smoothstep(Wp - 0.04, Wp - 0.10, u) \
            * H.smoothstep(Hp - 0.04, Hp - 0.10, np.abs(v))
        V2, N2 = xform_vn(Vh, Nh, R)
        H.add_mesh(f'pages_{side}', V2, Qh, N2, mp, parent=root, attrs={'pv': v, 'ptop': top})
        feats['page_r' if side > 0 else 'page_l'] = ib(R @ np.array([side * 0.5, float(page_h(0.5)), 0.0]))
    # hard cover: two boards following the page fan + a rounded spine
    boards = []
    for side in (1, -1):
        bd = I.sd3_round_box((side * 0.51, -0.04, 0), (0.52, 0.04, Hp + 0.075), 0.035)
        boards.append(I.u_xform(bd, rz=side * fan))
    spine = round_cyl('z', (0, -0.05, 0), 0.085, Hp + 0.075, 0.04)
    cover = I.u_smin(I.u_min(*boards), spine, 0.03)
    mesh('cover', cover, (-1.12, -0.2, -0.78), (1.12, 0.25, 0.78), 0.006, mat_magenta('book_cover'), root, q)
    # ribbon bookmark (ORANGE) from the gutter over the near edge
    rib2 = I.sd_polyline([(0.075, 0.20), (0.06, 0.52), (0.04, Hp + 0.02), (-0.10, Hp + 0.08), (-0.30, Hp + 0.12)],
                         0.012)
    rib = I.extrude_axis(lambda y, z: rib2(y, z), 'x', 0.036, 0.012, center=0.05)
    mesh('ribbon', rib, (-0.05, -0.4, 0.1), (0.15, 0.15, 0.85), 0.003, mat_orange('book_ribbon'), root, q)
    # pencil along local +x (tip at +x), hexagonal yellow-orange body
    rp = 0.062
    hexf = sd_hex(rp * 0.92, 0.012)
    body = lambda x, y, z: np.maximum(hexf(y, z), np.abs(x + 0.10) - 0.46)
    def cone(x, y, z):                         # sharpened wood: a cone clipped by the hexagonal prism
        t = np.clip((x - 0.33) / 0.20, 0, 1)
        rr = 0.072 * (1 - t) + 0.0225 * t
        return np.maximum(np.hypot(y, z) - rr, np.maximum(0.33 - x, x - 0.53))
    wood = I.u_sisect(cone, lambda x, y, z: hexf(y, z) - 0.002, 0.004)
    def tip(x, y, z):                          # graphite point
        t = np.clip((x - 0.52) / 0.10, 0, 1)
        rr = 0.0235 * (1 - t) + 0.004
        return np.maximum(np.hypot(y, z) - rr, np.maximum(0.49 - x, x - 0.625))
    ferr = I.u_min(round_cyl('x', (-0.60, 0, 0), rp + 0.004, 0.055, 0.012),
                   round_cyl('x', (-0.585, 0, 0), rp + 0.012, 0.012, 0.008),
                   round_cyl('x', (-0.625, 0, 0), rp + 0.012, 0.012, 0.008))
    eraser = round_cyl('x', (-0.70, 0, 0), rp - 0.004, 0.065, 0.04)
    a_ = np.array([0.86, 0.0, -0.40])          # eraser end (u, ., z) on the right page
    b_ = np.array([0.24, 0.0, 0.42])           # tip end
    d = b_ - a_
    phi = math.atan2(-d[2], d[0])
    mid = (a_ + b_) / 2
    yrest = float(page_h(0.55)) + rp - 0.004
    Rp = rotm(rz=fan) @ rotm(ry=phi, rx=math.radians(30))
    T = rotm(rz=fan) @ np.array([mid[0], yrest, mid[2]])
    lo, hi = (-0.8, -0.09, -0.09), (0.66, 0.09, 0.09)
    pcol = mixlin('AMBER', '#FFC93C', 0.55)
    for nm, F, m_ in (('pencil_body', body, candy('pencil', pcol, rim='AMBER', rim_str=0.25)),
                      ('pencil_wood', wood, candy('wood', 'PEACH', rough=0.45, rim=None)),
                      ('pencil_lead', tip, mat_ink('lead', rough=0.25)),
                      ('pencil_ferrule', ferr, H.m_gold('ferrule', rough=0.2)),
                      ('pencil_eraser', eraser, candy('eraser', mixlin('HOT_PINK', 'PEACH', 0.35), rim='HOT_PINK',
                                                      rim_str=0.2, rough=0.4))):
        Vp, Qp, Np = mesh_vqn(F, lo, hi, 0.0035, q)
        V2, N2 = xform_vn(Vp, Np, Rp, T)
        H.add_mesh(nm, V2, Qp, N2, m_, parent=root)
    feats['pencil_tip'] = ib(Rp @ np.array([0.62, 0, 0]) + T)
    return {'root': root, 'tilt': tilt, 'rig_scale': 1.2, 'pivot': ib((0, -0.06, 0)), 'features': feats}


# ============================================================================= 6. mixing_bowl

@asset('mixing_bowl', priority=6,
       notes='PEACH mixing bowl (ivory inside, a thin MAGENTA band), golden batter with a swirl, a silicone whisk '
             '(MAGENTA wires, ORANGE handle) standing in the batter; seen from slightly above.')
def build_bowl(q):
    tilt, root = tilted_root(24.0)
    Rc, Ro, th, rim_y = 1.0, 1.0, 0.075, 0.80

    def shell2(r, y):
        d = np.abs(np.hypot(r, y - Rc) - (Ro - th / 2)) - th / 2
        return d
    rim_r = math.sqrt(Ro ** 2 - (Rc - rim_y) ** 2) - th / 2
    def bowl2(r, y):
        d = smax(shell2(r, y), y - rim_y, 0.03)                               # wall cut at the rim
        d = smin(d, np.hypot(r - rim_r, y - rim_y) - 0.052, 0.03)              # rolled lip
        foot = np.hypot(np.maximum(np.abs(r) - 0.40, 0), np.maximum(np.abs(y) - 0.05, 0)) - 0.03
        return smin(d, foot, 0.06)
    Fb = revolve(bowl2)
    mb = m_two_tone('bowl', mixlin('PEACH', 'ORANGE', 0.22), 'IVORY', rough=0.26, rim='AMBER', rim_str=0.15,
                    band=('MAGENTA', 0.56, 0.62))
    mesh('bowl', Fb, (-1.08, -0.12, -1.08), (1.08, 0.88, 1.08), 0.0075, mb, root, q)
    # batter: the inner cavity up to a softly swirled surface
    lev = 0.60
    def batter(x, y, z):
        r = np.hypot(x, z)
        th_ = np.arctan2(z, x)
        top = lev + 0.034 * np.sin(2 * th_ - 16 * r) * H.smoothstep(0.04, 0.30, r) * H.smoothstep(0.95, 0.55, r) \
            + 0.08 * np.exp(-(r / 0.20) ** 2)
        cav = np.hypot(r, y - Rc) - (Ro - th + 0.012)
        return np.maximum(cav, y - top)
    mbat = candy('batter', mixlin('AMBER', '#FFC93C', 0.35), rim='AMBER', rim_str=0.15, rough=0.18)
    mesh('batter', batter, (-0.95, 0.0, -0.95), (0.95, 0.72, 0.95), 0.0065, mbat, root, q)
    # whisk: local frame axis +y, tip at the origin; wires 0..Lw, handle Lw..Lw+0.62
    Lw, Wd, nl = 0.95, 0.19, 4
    us = np.linspace(0, 1, 90) ** 1.6
    prof = Wd * 2.38 * np.sqrt(us) * (1 - us) ** 0.8 + 0.035 * us
    wire_parts = []
    for k in range(nl):
        a = math.pi * k / nl
        e = np.array([math.cos(a), 0, math.sin(a)])
        br = [e * t + np.array([0, u * Lw, 0]) for u, t in zip(us, prof)]
        bl = [-e * t + np.array([0, u * Lw, 0]) for u, t in zip(us, prof)]
        loop = bl[::-1] + br[1:-1]
        wire_parts.append(tube_mesh(loop, 0.019, sides=12, closed=True, up=np.cross(e, [0, 1.0, 0])))
    handle = I.u_smin(round_cyl('y', (0, Lw + 0.33, 0), 0.068, 0.30, 0.06),
                      round_cyl('y', (0, Lw + 0.04, 0), 0.05, 0.06, 0.03), 0.03)
    ring = I.sd3_torus((0, Lw + 0.70, 0), 0.06, 0.016, axis='z')
    A = np.array([-0.06, 0.40, 0.10])
    dirv = np.array([0.50, 1.0, -0.16])
    dirv /= np.linalg.norm(dirv)
    # rotation taking +y to dirv
    yv = np.array([0, 1.0, 0])
    ax = np.cross(yv, dirv)
    s_, c_ = np.linalg.norm(ax), float(yv @ dirv)
    ax /= s_
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    Rw = np.eye(3) + s_ * K + (1 - c_) * K @ K
    mw = mat_magenta('whisk_wire')
    Vw, Qw, Nw = merge_meshes(wire_parts)
    V2, N2 = xform_vn(Vw, Nw, Rw, A)
    H.add_mesh('whisk_wires', V2, Qw, N2, mw, parent=root)
    Vh, Qh, Nh = mesh_vqn(I.u_min(handle, ring), (-0.1, Lw - 0.05, -0.1), (0.1, Lw + 0.8, 0.1), 0.004, q)
    V2, N2 = xform_vn(Vh, Nh, Rw, A)
    H.add_mesh('whisk_handle', V2, Qh, N2, mat_orange('whisk_handle'), parent=root)
    return {'root': root, 'tilt': tilt, 'rig_scale': 1.25, 'pivot': ib((0, -0.05, 0)),
            'features': {'batter': ib((0, lev + 0.05, 0)), 'whisk_top': ib(Rw @ np.array([0, Lw + 0.75, 0]) + A)}}


# ============================================================================= 7. cupcake

@asset('cupcake', priority=7,
       notes='Cupcake: ORANGE pleated liner, pink->MAGENTA frosting swirl with sprinkles, a glossy cherry on top.')
def build_cupcake(q):
    tilt, root = tilted_root(10.0)
    yl = 0.62
    def liner(x, y, z):
        r = np.hypot(x, z)
        th_ = np.arctan2(z, x)
        base = 0.52 + 0.18 * np.clip(y / yl, 0, 1)
        rr = base + 0.022 * np.cos(20 * th_)
        return smax(r - rr, np.maximum(-y, y - yl), 0.035)
    mesh('liner', liner, (-0.8, -0.05, -0.8), (0.8, yl + 0.05, 0.8), 0.0055,
         mat_orange('liner', grad=(mixlin('ORANGE', 'AMBER', 0.3), 0.0, yl)), root, q)
    # frosting: a tapering conical helix tube + core + tip
    T, y0, y1, R0 = 2.6, 0.80, 1.40, 0.50

    def hel(t):
        u = np.clip(t / T, 0, 1)
        return (R0 * (1 - u) ** 0.9 + 0.03, y0 + (y1 - y0) * u ** 0.95, 0.215 - 0.095 * u)

    def frost(x, y, z):
        r = np.hypot(x, z)
        fr = (np.arctan2(z, x) / (2 * np.pi)) % 1.0
        d = None
        for k in range(-1, int(math.ceil(T)) + 1):
            t = np.clip(fr + k, 0, T)
            R, Y, rt = hel(t)
            dk = np.hypot(r - R, y - Y) - rt
            d = dk if d is None else np.minimum(d, dk)
        core = np.maximum(r - 0.40 * np.clip((y1 + 0.05 - y) / (y1 - y0), 0, 1) - 0.06, np.maximum(0.66 - y, y - 1.45))
        return smin(d, core, 0.06)
    mf = candy('frosting', 'MAGENTA', rim='HOT_PINK', rim_str=0.3, rough=0.24,
               grad=(mixlin('HOT_PINK', 'IVORY', 0.28), 0.7, 1.45))
    Vf, Qf, Nf = mesh_vqn(frost, (-0.85, 0.5, -0.85), (0.85, 1.6, 0.85), 0.0055, q)
    H.add_mesh('frosting', Vf, Qf, Nf, mf, parent=root)
    # cherry + stem
    cc = np.array([0.02, 1.64, 0.03])
    cherry = I.u_ssub(I.sd3_sphere(tuple(cc), 0.155), I.sd3_sphere(tuple(cc + [0, 0.19, 0]), 0.06), 0.03)
    mesh('cherry', cherry, tuple(cc - 0.2), tuple(cc + 0.2), 0.003,
         H.m_candy('cherry', mixlin('MAGENTA', '#E4002B', 0.6), rough=0.16, coat_r=0.02, sss=0.0, rim='HOT_PINK',
                   rim_str=0.3), root, q)
    stem = capsule_chain([cc + [0, 0.11, 0], cc + [0.03, 0.24, 0], cc + [0.10, 0.36, -0.02], cc + [0.19, 0.42, -0.04]],
                         [0.022, 0.02, 0.017, 0.015])
    mesh('stem', stem, tuple(cc + [-0.06, 0.05, -0.1]), tuple(cc + [0.26, 0.48, 0.06]), 0.0025, mat_leaf('stem'), root, q)
    # sprinkles on the frosting (four colours), avoiding the cherry
    m = (Nf[:, 1] > 0.05) & (Vf[:, 1] > 0.78) & (np.linalg.norm(Vf - cc, axis=1) > 0.26)
    picks = scatter_on(Vf, Nf, 34, m, 0.13, seed=5)
    cap = lambda x, y, z: I.sd3_capsule((-0.04, 0, 0), (0.04, 0, 0), 0.021)(x, y, z)
    V0, Q0, N0 = mesh_vqn(cap, (-0.07, -0.03, -0.03), (0.07, 0.03, 0.03), 0.0022, q)
    cols = ['IVORY', mixlin('AMBER', '#FFC93C', 0.5), 'LEAF_HI', 'ORANGE']
    rng = np.random.default_rng(11)
    groups = {c: ([], [], []) for c in range(len(cols))}
    for j, i in enumerate(picks):
        R = frame_from_normal(Nf[i], rng.uniform(0, 2 * np.pi))
        V2, N2 = xform_vn(V0, N0, R, Vf[i] + Nf[i] * 0.004)
        g = groups[j % len(cols)]
        g[0].append(V2)
        g[2].append(N2)
        g[1].append(Q0 + sum(len(v) for v in g[0][:-1]))
    for c, (Vs, Qs, Ns) in groups.items():
        if Vs:
            H.add_mesh(f'sprinkles{c}', np.concatenate(Vs), np.concatenate(Qs), np.concatenate(Ns),
                       candy(f'sprinkle{c}', cols[c], rim=None, rough=0.25), parent=root)
    return {'root': root, 'tilt': tilt, 'rig_scale': 1.1, 'pivot': ib((0, 0, 0)),
            'features': {'top': ib(cc + [0, 0.16, 0])}}


# ============================================================================= 8. alarm_clock

@asset('alarm_clock', priority=8,
       notes='ORANGE twin-bell alarm clock: ivory face with PLUM ticks, hands at 8:15, MAGENTA centre cap, knobs '
             'and feet, gold hammer.')
def build_clock(q):
    tilt, root = tilted_root(6.0)
    zf = 0.30
    drum = round_cyl('z', (0, 0, 0), 0.80, zf, 0.17)
    bez = I.sd3_torus((0, 0, zf - 0.025), 0.69, 0.075, axis='z')
    body = I.u_smin(drum, bez, 0.04)
    body = I.u_ssub(body, round_cyl('z', (0, 0, zf + 0.14), 0.625, 0.22, 0.02), 0.025)
    # bells (as part of the orange body family, slightly lighter) + stems
    bells, knobs = [], []
    for sx in (-1, 1):
        b = np.array([sx * math.sin(math.radians(38)), math.cos(math.radians(38)), 0.0])
        c = b * 0.93
        dome = I.u_sisect(I.sd3_sphere(tuple(c), 0.31), lambda x, y, z, b=b, c=c:
                          -((x - c[0]) * b[0] + (y - c[1]) * b[1] + (z - c[2]) * b[2]) - 0.02, 0.04)
        lip = I.u_xform(I.sd3_torus((0, 0, 0), 0.29, 0.035, axis='y'), t=tuple(c - b * 0.02),
                        rz=-sx * math.radians(38))
        stem = I.sd3_capsule(tuple(b * 0.70), tuple(c), 0.06)
        bells.append(I.u_smin(I.u_smin(dome, lip, 0.02), stem, 0.03))
        knobs.append(I.sd3_sphere(tuple(c + b * 0.33), 0.065))
    mo = mat_orange('clock_body', grad=(mixlin('ORANGE', 'AMBER', 0.25), -0.6, 0.8))
    mesh('body', body, (-0.86, -0.86, -0.36), (0.86, 0.86, 0.42), 0.0065, mo, root, q)
    mesh('bells', I.u_min(*bells), (-1.0, 0.35, -0.36), (1.0, 1.15, 0.36), 0.0055,
         mat_orange('clock_bells', grad=(mixlin('ORANGE', 'AMBER', 0.45), 0.5, 1.1)), root, q)
    # face, ticks, hands, cap
    face = round_cyl('z', (0, 0, zf - 0.08), 0.64, 0.028, 0.02)
    mface = H.m_candy('clock_face', 'IVORY', rough=0.22, coat_r=0.03, sss=0.0, emit='IVORY', emit_str=0.12)
    mesh('face', face, (-0.66, -0.66, zf - 0.13), (0.66, 0.66, zf - 0.03), 0.004, mface,
         root, q)
    zt = zf - 0.052
    ticks = []
    for k in range(12):
        a = 2 * math.pi * k / 12
        dx, dy = math.sin(a), math.cos(a)
        if k % 3 == 0:
            s2 = I.sd_segment(dx * 0.44, dy * 0.44, dx * 0.54, dy * 0.54, 0.028)
        else:
            s2 = I.sd_circle(dx * 0.51, dy * 0.51, 0.026)
        ticks.append(s2)
    tick2 = I.op_union(*ticks)
    tk = I.extrude_axis(tick2, 'z', 0.016, 0.012, center=zt)
    ph, pm = math.radians(247.5), math.radians(90.0)
    hour = I.extrude_axis(I.op_smin(I.sd_segment(-0.07 * math.sin(ph), -0.07 * math.cos(ph), 0.29 * math.sin(ph),
                                                 0.29 * math.cos(ph), 0.036), I.sd_circle(0, 0, 0.05), 0.02),
                          'z', 0.014, 0.011, center=zt + 0.012)
    minute = I.extrude_axis(I.op_smin(I.sd_segment(-0.09 * math.sin(pm), -0.09 * math.cos(pm), 0.45 * math.sin(pm),
                                                   0.45 * math.cos(pm), 0.026), I.sd_circle(0, 0, 0.045), 0.02),
                            'z', 0.012, 0.010, center=zt + 0.040)
    mesh('ticks_hands', I.u_min(tk, hour, minute), (-0.6, -0.6, zt - 0.04), (0.6, 0.6, zt + 0.07), 0.003,
         mat_ink('clock_ink'), root, q)
    capc = round_cyl('z', (0, 0, zt + 0.065), 0.06, 0.022, 0.018)
    feet = []
    for sx in (-1, 1):
        a0 = np.array([sx * 0.42, -0.62, 0.0])
        a1 = np.array([sx * 0.62, -0.95, 0.0])
        feet.append(I.u_smin(I.sd3_capsule(tuple(a0), tuple(a1), 0.06), I.sd3_sphere(tuple(a1), 0.095), 0.03))
    mesh('magenta', I.u_min(capc, *knobs, *feet), (-0.85, -1.1, -0.3), (0.85, 1.32, 0.42), 0.004,
         mat_magenta('clock_magenta'), root, q)
    hammer = I.u_min(I.sd3_capsule((0, 0.76, 0), (0, 1.04, 0), 0.03), I.sd3_sphere((0, 1.07, 0), 0.07))
    mesh('hammer', hammer, (-0.12, 0.7, -0.12), (0.12, 1.16, 0.12), 0.003, H.m_gold('hammer', rough=0.2), root, q)
    return {'root': root, 'tilt': tilt, 'rig_scale': 1.15, 'pivot': ib((0, -1.04, 0)),
            'features': {'face': ib((0, 0, zt)), 'bell_l': ib((-0.88, 0.96, 0)), 'bell_r': ib((0.88, 0.96, 0))}}


# ============================================================================= 9. family_figures

def pawn(cx, s):
    """A rounded pawn-style toy figure (height ~1.65 * s) standing at x = cx on y = 0."""
    prof = I.fn_sd(lambda r, y: I.sd_poly_exact([(-0.1, 0.10), (0.37, 0.10), (0.16, 0.96), (-0.1, 0.96)])(r, y),
                   (-0.2, -0.1, 0.7, 1.2), 600).rounded(0.07, 0.03)
    def F(x, y, z):
        xs, ys, zs = (x - cx) / s, y / s, z / s
        r = np.hypot(xs, zs)
        body = prof(r, ys)
        base = np.hypot(np.maximum(r - 0.36, 0), np.maximum(np.abs(ys - 0.065) - 0.03, 0)) - 0.04
        collar = np.hypot(r - 0.16, ys - 0.99) - 0.07
        head = np.sqrt(r ** 2 + (ys - 1.30) ** 2) - 0.30
        d = smin(smin(smin(body, base, 0.06), collar, 0.04), head, 0.05)
        return d * s
    return F


@asset('family_figures', priority=9,
       notes='Two rounded pawn-style toy figures holding hands: a taller MAGENTA adult (left) and a smaller ORANGE '
             'child (right).')
def build_family(q):
    root = H.empty('root')
    sa, sc = 1.0, 0.70
    xa, xc = -0.43, 0.40
    M = np.array([-0.01, 0.56, 0.06])
    adult = pawn(xa, sa)
    child = pawn(xc, sc)
    sh_a = [np.array([xa + 0.17, 0.86, 0.0]), np.array([xa - 0.17, 0.86, 0.0])]
    sh_c = [np.array([xc - 0.17 * sc, 0.86 * sc, 0.0]), np.array([xc + 0.17 * sc, 0.86 * sc, 0.0])]
    arm_a = I.u_smin(I.sd3_capsule(tuple(sh_a[0]), tuple(M + [-0.05, 0.0, 0.0]), 0.068),
                     I.sd3_capsule(tuple(sh_a[1]), (xa - 0.33, 0.50, 0.04), 0.068), 0.01)
    hand_a = I.u_min(I.sd3_sphere(tuple(M + [-0.055, 0.0, 0.0]), 0.085), I.sd3_sphere((xa - 0.34, 0.48, 0.04), 0.085))
    arm_c = I.u_smin(I.sd3_capsule(tuple(sh_c[0]), tuple(M + [0.05, 0.0, 0.0]), 0.055),
                     I.sd3_capsule(tuple(sh_c[1]), (xc + 0.25, 0.36, 0.04), 0.055), 0.01)
    hand_c = I.u_min(I.sd3_sphere(tuple(M + [0.05, 0.0, 0.0]), 0.07), I.sd3_sphere((xc + 0.26, 0.34, 0.04), 0.07))
    Fa = I.u_smin(adult, I.u_smin(arm_a, hand_a, 0.03), 0.05)
    Fc = I.u_smin(child, I.u_smin(arm_c, hand_c, 0.025), 0.04)
    mesh('adult', Fa, (xa - 0.5, -0.02, -0.45), (0.12, 1.7, 0.45), 0.0065, mat_magenta('adult'), root, q)
    mesh('child', Fc, (-0.12, -0.02, -0.35), (xc + 0.42, 1.2, 0.35), 0.0055,
         mat_orange('child', grad=(mixlin('ORANGE', 'AMBER', 0.2), 0.0, 1.2)), root, q)
    return {'root': root, 'rig_scale': 1.15, 'pivot': ib((0, 0, 0)), 'features': {'hands': ib(M)}}


# ============================================================================= Blender driver

def _remove_cameras():
    bpy = H.bpy
    for o in [o for o in bpy.context.scene.objects if o.type == 'CAMERA']:
        bpy.data.objects.remove(o, do_unlink=True)


def _set_yaw(root, deg):
    root.rotation_euler = (0.0, 0.0, math.radians(deg))


def _feature_points(S, root):
    """{name: world point} for the builder's features (root-local Blender points)."""
    out = {}
    M = np.array(root.matrix_world)
    for k, p in (S.get('features') or {}).items():
        out[k] = (M @ np.append(np.asarray(p, float), 1.0))[:3]
    return out


def render_asset(name, preview=False, modes=None, frames=None, samples=None, q=None, size=None):
    """Build one asset and render each of its modes ('yaw', 'static', 'side'). Returns {folder: meta}.
    Finals: meta.json is removed before and written after all frames exist (other agents poll it)."""
    H._bpy()
    bpy = H.bpy
    spec = ASSETS[name]
    W, Hh = size or (PREVIEW_SIZE if preview else spec['size'])
    spp = samples or (PREVIEW_SAMPLES if preview else SAMPLES)
    q = q if q is not None else (0.6 if preview else 1.0)
    t0 = time.time()
    H.THREADS = THREADS
    sc = H.reset((W, Hh), spp, VARIANT)
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    H.world(VARIANT)
    S = spec['build'](q)
    root = S['root']
    H.rig(VARIANT, scale=S.get('rig_scale', 1.0), key=S.get('key', 1.0), cards=S.get('cards', 1.0))
    if S.get('setup'):
        S['setup'](sc)
    vl = bpy.context.view_layer
    print(f'[{name}] scene built in {time.time() - t0:.1f}s, {spp} spp, {W}x{Hh}', flush=True)
    out = {}
    for mode in spec['modes']:
        if modes and mode not in modes:
            continue
        P = MODE_POSES[mode]
        n = P['frames']
        _remove_cameras()
        pts = []
        for a in P['frame_yaws']:
            _set_yaw(root, a)
            vl.update()
            pts.append(H._mesh_points(H.scene_meshes()))
        H.frame_camera(np.concatenate(pts), (W, Hh), fill=S.get('fill_' + mode, S.get('fill', spec['fill'])),
                       elev=S.get('elev', H.ELEV_DEG))
        outdir = os.path.join(PREVIEW3D if preview else OUT3D, name, P['folder'])
        os.makedirs(outdir, exist_ok=True)
        meta_p = os.path.join(outdir, 'meta.json')
        if not preview and os.path.exists(meta_p) and not frames:
            os.remove(meta_p)                      # a re-render: the sequence is incomplete until the end
        idx = list(frames) if frames else ([0, n // 2, n - 1] if (preview and n > 3) else list(range(n)))
        idx = sorted({i for i in idx if 0 <= i < n})
        yaws = [yaw_of(i, n) for i in range(n)] if mode == 'yaw' else [P['yaw']]
        feats = {}
        t1 = time.time()
        for k, i in enumerate(idx):
            _set_yaw(root, yaws[i])
            vl.update()
            feats[i] = {kk: H.project_px(v) for kk, v in _feature_points(S, root).items()}
            p = os.path.join(outdir, f'{i:04d}.png')
            if os.environ.get('SKIP_EXISTING') and os.path.exists(p) and not preview:
                continue
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            print(f'  {name}/{P["folder"]} frame {i} ({k + 1}/{len(idx)}) {(time.time() - t1) / (k + 1):.1f}s/frame',
                  flush=True)
        # feature tracks for every frame (cheap: no render)
        if mode == 'yaw' and S.get('features'):
            for i in range(n):
                if i not in feats:
                    _set_yaw(root, yaws[i])
                    vl.update()
                    feats[i] = {kk: H.project_px(v) for kk, v in _feature_points(S, root).items()}
        _set_yaw(root, 0.0 if mode != 'side' else 90.0)
        vl.update()
        piv = S.get('pivot', (0.0, 0.0, 0.0))
        pivot = H.project_px(tuple(np.array(root.matrix_world) @ np.append(np.asarray(piv, float), 1.0))[:3])
        complete = all(os.path.exists(os.path.join(outdir, f'{i:04d}.png')) for i in range(n))
        if not complete and not preview:
            print(f'  {name}/{P["folder"]}: partial render ({len(idx)}/{n}); meta.json NOT written', flush=True)
            continue
        meta = dict(name=name, variant=P['folder'], mode='yaw' if mode == 'yaw' else 'static', frames=n,
                    fps_hint=30, size=[W, Hh], loop=False, axis='z', samples=spp, preview=bool(preview),
                    notes=spec['notes'] + (' ' + S.get('notes_' + mode, '') if S.get('notes_' + mode) else ''),
                    pivot=pivot)
        if mode == 'yaw':
            meta['yaw_range'] = list(YAW_RANGE)
            meta['notes'] += '; yaw sweep -40..+40 deg (frame i = -40 + 80 i / 32), ping-pong for floating rotation'
        else:
            meta['yaw'] = P['yaw']
            meta['notes'] += f'; single frame at yaw {P["yaw"]:g} deg'
        if feats:
            mid = feats.get((n - 1) // 2) or feats[min(feats)]
            meta['features'] = mid
            if mode == 'yaw' and len(feats) == n:
                meta['features_per_frame'] = {kk: [feats[i][kk] for i in range(n)] for kk in mid}
        for k_, v_ in (S.get('meta') or {}).items():
            meta[k_] = v_
        out[P['folder']] = H.write_meta(outdir, **meta)      # LAST: every frame is on disk
        print(f'  -> {outdir} ({len(idx)} frames, {time.time() - t1:.0f}s)', flush=True)
    return out


# ============================================================================= contact sheets (no bpy)

def _ivory_tile(path, cell):
    import cv2
    im = H._read_rgba_lin(path)
    yy = np.linspace(0, 1, cell)[:, None, None]
    bg = np.array(hexlin('IVORY')) * (1 - yy) + np.array(hexlin('PEACH')) * 0.25 * yy + \
        np.array(hexlin('IVORY')) * 0.75 * yy
    bg = np.broadcast_to(bg, (cell, cell, 3)).astype(np.float32).copy()
    if im is None:
        return bg
    im = cv2.resize(im, (cell, cell), interpolation=cv2.INTER_AREA)
    return im[:, :, :3] + bg * (1 - im[:, :, 3:4])


def contact_sheet(root=None, out_path=None, cell=240, names=None, include_hero=True):
    """Every final asset folder (first, middle and last frame; static: its frame) on ivory, one row per
    folder with a label. Default output: out/selftest/assets3d_everyday_contact.png."""
    import cv2
    root = root or OUT3D
    out_path = out_path or os.path.join(SELFTEST, 'assets3d_everyday_contact.png')
    names = names or sorted(ASSETS, key=lambda k: ASSETS[k]['priority'])
    if include_hero and root == OUT3D:
        names = ['question'] + list(names) + ['blocks', 'leaf', 'logo_mark3d']
    rows = []
    for nm in names:
        base = os.path.join(root, nm)
        if not os.path.isdir(base):
            continue
        for folder in sorted(os.listdir(base)):
            if root == OUT3D and not folder.startswith('day'):
                continue
            d = os.path.join(base, folder)
            fs = sorted(f for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []
            if not fs:
                continue
            pick = [fs[0], fs[len(fs) // 2], fs[-1]] if len(fs) >= 3 else fs
            tiles = [_ivory_tile(os.path.join(d, f), cell) for f in pick]
            while len(tiles) < 3:
                tiles.append(_ivory_tile(None, cell))
            row = H._to8(np.concatenate(tiles, 1))
            meta = {}
            try:
                with open(os.path.join(d, 'meta.json')) as fh:
                    meta = json.load(fh)
            except Exception:
                pass
            ok = 'meta ok' if meta else 'NO META'
            lab = (f"{nm}/{folder}  {meta.get('mode', '?')} {meta.get('frames', len(fs))}f "
                   f"{'x'.join(str(v) for v in meta.get('size', []))}  [{', '.join(f[:-4] for f in pick)}]  {ok}")
            cv2.putText(row, lab, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 30, 55), 1, cv2.LINE_AA)
            rows.append(row)
    if not rows:
        return None
    wmax = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 3), (0, wmax - r.shape[1]), (0, 0)), constant_values=200) for r in rows]
    # two columns of rows so the sheet stays readable
    half = (len(rows) + 1) // 2
    colA, colB = rows[:half], rows[half:]
    hA = sum(r.shape[0] for r in colA)
    hB = sum(r.shape[0] for r in colB)
    if colB:
        A = np.concatenate(colA, 0)
        B = np.concatenate(colB, 0)
        B = np.pad(B, ((0, hA - hB), (0, 0), (0, 0)), constant_values=245)
        sheet = np.concatenate([A, np.full((A.shape[0], 8, 3), 200, np.uint8), B], 1)
    else:
        sheet = np.concatenate(colA, 0)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, sheet)
    return out_path


def preview_sheet(names=None, cell=300):
    return contact_sheet(root=PREVIEW3D, out_path=os.path.join(SELFTEST, 'assets3d_everyday_preview.png'),
                         cell=cell, names=names, include_hero=False)


# ============================================================================= selftest + CLI

def selftest():
    """numpy checks (girl trace, decal height map) + tiny renders of two assets into a temp folder."""
    import tempfile
    import shutil
    os.makedirs(SELFTEST, exist_ok=True)
    cov, bb = girl_mask()
    assert cov.shape[0] > 400 and cov.max() > 0.9, 'girl trace failed'
    F = I.sd3_sphere((0, 0, 0), 0.5)
    zb = height_map(F, -0.6, -0.6, 0.6, 0.6, res=64)
    assert abs(float(zb(0.0, 0.0)) - 0.5) < 0.01, 'height map'
    print('selftest: numpy ok', bb)
    global OUT3D, PREVIEW3D
    keep = (OUT3D, PREVIEW3D)
    tmp = tempfile.mkdtemp(prefix='everyday3d_')
    try:
        OUT3D = PREVIEW3D = tmp
        for nm in ('child_figure', 'cupcake'):
            if nm in ASSETS:
                render_asset(nm, preview=True, samples=6, q=0.45, size=(160, 160))
        contact_sheet(root=tmp, out_path=os.path.join(SELFTEST, 'assets3d_everyday_selftest.png'), cell=160,
                      include_hero=False)
    finally:
        OUT3D, PREVIEW3D = keep
        shutil.rmtree(tmp, ignore_errors=True)
    print('finals sheet:', contact_sheet())
    return 0


def _parse(argv):
    o = {'names': [], 'preview': False, 'mode': None, 'frames': None, 'samples': None, 'q': None}
    it = iter(argv)
    for a in it:
        if a == '--preview':
            o['preview'] = True
        elif a == '--mode':
            o['mode'] = next(it)
        elif a == '--frames':
            o['frames'] = [int(x) for x in next(it).split(',')]
        elif a == '--samples':
            o['samples'] = int(next(it))
        elif a == '--q':
            o['q'] = float(next(it))
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
        print(contact_sheet())
        return 0
    if names == ['previewsheet']:
        print(preview_sheet())
        return 0
    if names == ['all']:
        names = sorted(ASSETS, key=lambda k: ASSETS[k]['priority'])
    for nm in names:
        render_asset(nm, preview=o['preview'], modes=[o['mode']] if o['mode'] else None, frames=o['frames'],
                     samples=o['samples'], q=o['q'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
