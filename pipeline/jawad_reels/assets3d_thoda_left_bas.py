"""assets3d_thoda_left_bas.py - photoreal Blender props for Bijli series #2 "Thoda Left... Bas Bas!" (@jawad_mp4).

Builds the asset folders of SHOTS §a (brand_reels/design/reels/thoda_left_bas/SHOTS.md) with bpy 5.2 / Cycles CPU
(threads 2, adaptive threshold 0.02, OpenImageDenoise with albedo + normal guides, fixed seed, view transform
Standard, look None) as RGBA 8-bit straight-alpha sRGB PNGs in the shared 3D asset spec. STMaps are 16-bit RGBA PNGs
written with the 'Raw' view transform (linear values, no denoise). Notes for the compositor: ASSETS.md next to SHOTS.

    RWS = workspace/jawad_reels/thoda_left_bas
    RWS/assets3d/<name>/<variant>/0000.png ... + meta.json            (meta.json is written LAST)
    load: S3.Asset3D(name, variant, root=RWS + '/assets3d')   .at_yaw(deg) (yaw folders) / .by_label('bg') (static)

Assets (folder: mode, labels / frames)
--------------------------------------
    antenna/day_yaw      yaw [-45, 15], 61 frames (1 deg)   CAM_ROOF   RGBA, cropped   features_per_frame rod_tip,
                                                                                         mast_top, dipole_box, mast_axis
    antenna/sunset_yaw   yaw [-3, 3], 7 frames (1 deg)      CAM_SUNSET RGBA, cropped   (same features)
    roof/day             static: bg, fg_clamp               CAM_ROOF   1080x1920       mast_xy (pipe axis at the coping)
    roof/sunset          static: bg, fg_clamp               CAM_SUNSET 1080x1920       mast_xy, sun_xy
    clamp/macro          static: bg, fg                     CAM_CLAMP  1080x1920       strap_mark, bolt_l, bolt_r
    clamp/pipe_yaw       yaw [-6, 2], 17 frames (0.5 deg)   CAM_CLAMP  RGBA, cropped strip   pipe_mark per frame
    crt/macro            static: room, refl, spill, stmap   CAM_TV_MACRO 1080x1920     screen_quad, knob_ch, led_xy
    crt/room             static: room, refl, spill, stmap   CAM_TV_ROOM  1080x1920     screen_quad, knob_ch, led_xy
    phone/desk           static: lit, spill, stmap          CAM_PHONE    1080x1920     screen_quad

    Layering (bottom -> top): roof/<v> bg  ->  antenna/<v>_yaw at_yaw(yaw)  ->  roof/<v> fg_clamp.
                              clamp/macro bg  ->  clamp/pipe_yaw at_yaw(yaw) at meta frame_xy  ->  clamp/macro fg.
    yaw: degrees about the mast axis, + = counter-clockwise seen from above, 0 = locked on the transmitter
    (SHOTS §0). Every yaw folder is rendered on one fixed camera; frames are cropped to the union alpha bbox + 24 px
    and meta 'frame_xy' is the crop's top-left in the 1080x1920 frame (features are in sprite px; add frame_xy).
    CRT / phone passes: 'room'/'lit' = beauty with the screen dark; 'refl' = the screen glass reflections only, an
    ADDITIVE layer (RGB on black, alpha = visible glass); 'spill' = only the screen lighting the set (screen = uniform
    IVORY emitter, every other light off; multiply by the picture's mean luma and add); 'stmap' = 16-bit linear,
    R = u (0 left -> 1 right of the picture), G = v (0 bottom -> 1 top), B = 0, A = visible picture mask (rounded
    corners, occluded by the bezel lip). meta 'screen_quad' = the picture's 4 corners [TL, TR, BR, BL] in frame px.

CLI
---
    python3 assets3d_thoda_left_bas.py <name/variant> [...] [--preview] [--samples N] [--frames 0,30,60]
    python3 assets3d_thoda_left_bas.py all [--preview]        # A5 -> A1 -> A3 -> A4 -> A6 -> A7 -> A2 order
    python3 assets3d_thoda_left_bas.py targets                # camera layout vs the SHOTS screen targets (no render)
    python3 assets3d_thoda_left_bas.py sheet | previewsheet   # contact sheets + layered composites to look at
    python3 assets3d_thoda_left_bas.py archive                # optimised copies -> brand_reels/assets/thoda_left_bas/assets3d
    python3 assets3d_thoda_left_bas.py restore                # archive -> RWS/assets3d (fresh container, no re-render)
    python3 assets3d_thoda_left_bas.py selftest

    --preview  16 spp, half resolution, into RWS/out/preview3d/ (finals untouched). env TLB_THREADS (default 2).
    Run every render through pipeline/jawad_reels/tools/heavy.sh.

No text, logo or brand mark on any prop: the only marks are the hand-painted white index marks on the pipe and the
strap and blank faded stickers. Real-world dimensions in metres. The Bijli builder is imported for engine helpers
only (reset, principled / shader-graph helper, mesh helpers, projection, border crop, meta writer).
"""
import os
import sys
import json
import math
import time
import shutil

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assets3d_hero as H                # noqa: E402  (write_meta, WS)
import assets3d_bijli_chali_gayi as B    # noqa: E402  (engine helpers only)

bpy = None
Vector = None

REEL = 'thoda_left_bas'
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RWS = os.path.join(H.WS, REEL)
OUT = os.environ.get('TLB_OUT', os.path.join(RWS, 'assets3d'))
PREVIEW = os.path.join(RWS, 'out', 'preview3d')
SHEETS = os.path.join(RWS, 'out', 'sheets3d')
ARCHIVE = os.path.join(REPO, 'brand_reels', 'assets', REEL, 'assets3d')
THREADS = int(os.environ.get('TLB_THREADS', '2'))
S_PREVIEW, S_FLAT = 16, 16
CROP_PAD = 24
W_PX, H_PX = 1080, 1920
BUILDER = 'pipeline/jawad_reels/assets3d_thoda_left_bas.py'

lin, mixl, mul, hue = B.lin, B.mixl, B.mul, B.hue


def _bpy():
    global bpy, Vector
    if bpy is None:
        B._bpy()
        bpy = B.bpy
        Vector = B.Vector
    return bpy


def C(h):
    """'#RRGGBB' -> linear RGB tuple."""
    return lin(h)


# ============================================================================= scene / render engine

def reset(res, samples, transparent=True):
    sc = B.reset(res, samples, transparent)
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    sc.cycles.seed = 7
    sc.cycles.use_animated_seed = False
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.max_bounces = 12
    sc.cycles.sample_clamp_indirect = 6.0
    sc.cycles.blur_glossy = 0.3
    sc.cycles.use_light_tree = True
    sc.render.use_persistent_data = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.render.filter_size = 1.2
    return sc


link = None


def _late():
    """Bind helpers that need bpy loaded."""
    global link
    link = B.link


set_vis = B.set_vis


def vis_only(o, camera=None, **kw):
    """Toggle ray visibility flags keeping the others."""
    if camera is not None:
        o.visible_camera = camera
    for k, v in kw.items():
        setattr(o, 'visible_' + k, v)


def camera(name, loc, target, lens, fstop=None, focus=None, roll=0.0, shift=(0.0, 0.0), sensor=36.0, blades=7):
    """Camera with the 36 mm sensor fitted VERTICALLY (1920 px), aimed at `target`; DOF if fstop is given
    (focus = distance in metres or a world point)."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = sensor
    cd.sensor_width = sensor
    cd.shift_x, cd.shift_y = shift
    cd.clip_start = 0.01
    cd.clip_end = 400.0
    cam = B.link(bpy.data.objects.new(name, cd))
    cam.location = loc
    d = Vector(target) - Vector(loc)
    q = d.to_track_quat('-Z', 'Y')
    cam.rotation_euler = q.to_euler()
    if roll:
        from mathutils import Matrix
        cam.matrix_world = cam.matrix_world @ Matrix.Rotation(math.radians(roll), 4, 'Z')
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = blades
        cd.dof.aperture_rotation = math.radians(12)
        if focus is None:
            focus = d.length
        elif not isinstance(focus, (int, float)):
            focus = (Vector(focus) - Vector(loc)).dot(d.normalized())
        cd.dof.focus_distance = float(focus)
    sc.camera = cam
    return cam


def render_to(sc, path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ============================================================================= geometry primitives (metres)

def _mesh(name, V, F, mat=None, smooth=True, sharp=None, uv=None, role='prop', parent=None):
    o = B.mesh_from(name, np.asarray(V, float), F, mat, uv=uv, smooth=smooth, role=role)
    if sharp is not None:
        o.data.set_sharp_from_angle(angle=math.radians(sharp))
    if parent is not None:
        o.parent = parent
    return o


def bevel_mod(o, width, seg=3, angle=35.0, harden=True):
    m = o.modifiers.new('bevel', 'BEVEL')
    m.width = width
    m.segments = seg
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = harden
    m.miter_outer = 'MITER_ARC'
    return m


def rrect_loop(hx, hy, r, k=6):
    """Rounded rectangle (half sizes hx, hy, corner radius r) as 4k points, CCW from the +x+y corner arc."""
    r = max(min(r, hx - 1e-5, hy - 1e-5), 1e-5)
    pts = []
    for ci, (sx, sy, a0) in enumerate(((1, 1, 0.0), (-1, 1, 90.0), (-1, -1, 180.0), (1, -1, 270.0))):
        cx, cy = sx * (hx - r), sy * (hy - r)
        for j in range(k):
            a = math.radians(a0 + 90.0 * j / (k - 1))
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def loft(name, loops, mat, k=6, axis='Z', center=(0, 0, 0), cap0=False, cap1=False, smooth=True, sharp=32.0,
         role='prop', parent=None, uvmode=None):
    """Stack of rounded-rect loops [(hx, hy, r, h), ...] bridged with quads. axis 'Z': loop in XY, h along Z;
    'Y': loop in XZ (hy -> z), h along Y; 'X': loop in YZ, h along X. Caps close the first / last loop."""
    V, F = [], []
    n = 4 * k
    for (hx, hy, r, h) in loops:
        for (a, b) in rrect_loop(hx, hy, r, k):
            if axis == 'Z':
                V.append((a, b, h))
            elif axis == 'Y':
                V.append((a, h, b))
            else:
                V.append((h, a, b))
    for i in range(len(loops) - 1):
        for j in range(n):
            a0 = i * n + j
            b0 = i * n + (j + 1) % n
            F.append((a0, b0, b0 + n, a0 + n))
    if cap0:
        F.append(tuple(range(n - 1, -1, -1)))
    if cap1:
        base = (len(loops) - 1) * n
        F.append(tuple(base + j for j in range(n)))
    V = np.array(V) + np.asarray(center, float)
    o = _mesh(name, V, F, mat, smooth=smooth, sharp=sharp, role=role, parent=parent)
    # consistent outward normals
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    if sharp is not None:
        o.data.set_sharp_from_angle(angle=math.radians(sharp))
    return o


def round_box_loops(hx, hy, r, h0, h1, e, n=4, inset_back=0.0):
    """Loops for a rounded box between h0 and h1 with edge radius e on both ends (caps added by loft)."""
    L = []
    for j in range(n + 1):
        a = math.radians(90.0 * j / n)
        ins = e * (1 - math.sin(a))
        L.append((hx - ins, hy - ins, max(r - ins, 1e-4), h0 + e * (1 - math.cos(a))))
    for j in range(n + 1):
        a = math.radians(90.0 * j / n)
        ins = e * (1 - math.cos(a))
        L.append((hx - ins - inset_back, hy - ins - inset_back, max(r - ins, 1e-4), h1 - e + e * math.sin(a)))
    return L


def rbox(name, c, half, r, e, mat, axis='Z', k=6, n=3, parent=None, role='prop'):
    """Rounded box: footprint rounded-rect (corner r) and edge round e on the two faces normal to `axis`."""
    hx, hy, hz = half
    if axis == 'Z':
        L = round_box_loops(hx, hy, r, -hz, hz, e, n)
    elif axis == 'Y':
        L = round_box_loops(hx, hz, r, -hy, hy, e, n)
    else:
        L = round_box_loops(hy, hz, r, -hx, hx, e, n)
    return loft(name, L, mat, k=k, axis=axis, center=c, cap0=True, cap1=True, parent=parent, role=role)


def rod(name, p0, p1, r, mat, seg=20, cap='round', parent=None, role='prop', r1=None):
    """Cylinder from p0 to p1; object origin at p0 and local +Z along the rod (so object-coordinate textures can
    stretch along the axis). cap: 'round' (domed ends), 'flat' or None (open tube)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    r1 = r if r1 is None else r1
    prof = []
    if cap == 'round':
        hc, hc1 = 0.5 * r, 0.5 * r1
        prof = [(max(r * math.sin(math.radians(30 * j)), 1e-5), hc * (1 - math.cos(math.radians(30 * j)))) for j in range(4)]
        prof += [(max(r1 * math.sin(math.radians(30 * j)), 1e-5), L - hc1 * (1 - math.cos(math.radians(30 * j))))
                 for j in range(3, -1, -1)]
    elif cap == 'flat':
        prof = [(1e-5, 0.0), (r * 0.85, 0.0), (r, 0.0006), (r1, L - 0.0006), (r1 * 0.85, L), (1e-5, L)]
    else:
        prof = [(r, 0.0), (r1, L)]
    o = lathe_obj(name, prof, mat, seg=seg, role=role)
    z = (p1 - p0) / max(L, 1e-9)
    from mathutils import Vector as V_
    q = V_(tuple(z)).to_track_quat('Z', 'Y')
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = q
    o.location = tuple(p0)
    if parent is not None:
        o.parent = parent
    return o


def lathe_obj(name, prof, mat, seg=48, role='prop', smooth=True, sharp=40.0, ripple=None):
    """Surface of revolution about local Z: prof = [(r, z), ...]. ripple(theta, z) -> radius factor (flutes)."""
    prof = np.asarray(prof, float)
    a = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    R = np.outer(np.ones(seg), prof[:, 0])
    if ripple is not None:
        R = R * ripple(a[:, None], prof[None, :, 1])
    V = np.stack([np.cos(a)[:, None] * R, np.sin(a)[:, None] * R, np.tile(prof[:, 1], (seg, 1))], -1).reshape(-1, 3)
    n = len(prof)
    F = []
    for i in range(seg):
        for j in range(n - 1):
            a0 = i * n + j
            b0 = ((i + 1) % seg) * n + j
            F.append((a0, a0 + 1, b0 + 1, b0))
    o = _mesh(name, V, F, mat, smooth=smooth, sharp=sharp, role=role)
    m = o.modifiers.new('weld', 'WELD')
    m.merge_threshold = 1e-6
    return o


def hexprism(name, c, af, h, mat, axis='Z', parent=None, bevel=0.0006, role='prop'):
    """Hex nut / bolt head: across-flats af, height h, chamfered."""
    R = af / math.sqrt(3.0)
    prof = [(1e-5, -h / 2), (R * 0.86, -h / 2), (R, -h / 2 + h * 0.18), (R, h / 2 - h * 0.18), (R * 0.86, h / 2),
            (1e-5, h / 2)]
    o = lathe_obj(name, prof, mat, seg=6, smooth=False, role=role)
    o.data.polygons.foreach_set('use_smooth', np.zeros(len(o.data.polygons), bool))
    o.rotation_mode = 'XYZ'
    o.rotation_euler = {'Z': (0, 0, math.radians(30)), 'Y': (math.radians(90), 0, 0), 'X': (0, math.radians(90), 0)}[axis]
    o.location = c
    if parent is not None:
        o.parent = parent
    return o


def tube(name, pts, r, mat, res=4, order=3, parent=None, role='prop', caps=True, twist='MINIMUM'):
    """Curve tube through pts (NURBS, endpoint-clamped) with circular bevel radius r."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_mode = 'ROUND'
    cu.bevel_depth = r
    cu.bevel_resolution = res
    cu.use_fill_caps = caps
    cu.twist_mode = twist
    cu.resolution_u = 12
    sp = cu.splines.new('NURBS')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (float(q[0]), float(q[1]), float(q[2]), 1.0)
    sp.order_u = min(order, len(pts))
    sp.use_endpoint_u = True
    cu.materials.append(mat)
    o = B.link(bpy.data.objects.new(name, cu))
    o['role'] = role
    if parent is not None:
        o.parent = parent
    return o


def grid_mesh(name, fn, nu, nv, mat, uvs=True, role='prop', smooth=True, parent=None):
    """Parametric sheet: fn(u, v) -> (x, y, z) for u, v in [0, 1]; UV = (u, v)."""
    us = np.linspace(0, 1, nu)
    vs = np.linspace(0, 1, nv)
    V, UV = [], []
    for u in us:
        for v in vs:
            V.append(fn(u, v))
            UV.append((u, v))
    F = [(i * nv + j, (i + 1) * nv + j, (i + 1) * nv + j + 1, i * nv + j + 1) for i in range(nu - 1) for j in range(nv - 1)]
    return _mesh(name, np.array(V), F, mat, smooth=smooth, uv=np.array(UV) if uvs else None, role=role, parent=parent)


def empty(name, loc=(0, 0, 0), parent=None):
    o = B.link(bpy.data.objects.new(name, None))
    o.location = loc
    if parent is not None:
        o.parent = parent
    return o


# ============================================================================= shader helpers (on top of B.G)

def rgb(g, c):
    n = g.n('ShaderNodeRGB')
    n.outputs[0].default_value = tuple(C(c) if isinstance(c, str) else c) + (1.0,)
    return n.outputs[0]


def vsc(g, v, s):
    """Vector / colour times a scalar (float or socket)."""
    n = g.n('ShaderNodeVectorMath', operation='SCALE')
    g.put(n.inputs[0], v)
    g.put(n.inputs['Scale'], s)
    return n.outputs[0]


def col(g, c):
    return C(c) if isinstance(c, str) else c


def mixc(g, fac, a, b):
    return g.mix(fac, col(g, a) if not hasattr(a, 'links') else a, col(g, b) if not hasattr(b, 'links') else b)


def geo(g, out='Normal'):
    return g.n('ShaderNodeNewGeometry').outputs[out]


def up_mask(g, lo=-0.1, hi=0.85):
    """World-normal z remapped: 0 facing down/sideways -> 1 facing up."""
    _, _, nz = g.xyz(geo(g, 'Normal'))
    return g.mr(nz, lo, hi, 0.0, 1.0, smooth=True)


def ao(g, dist=0.01, inside=False, samples=6):
    n = g.n('ShaderNodeAmbientOcclusion', samples=samples, inside=inside, only_local=True)
    n.inputs['Distance'].default_value = dist
    return n.outputs['AO']


def vor(g, vec, scale, feature='F1', out='Distance', rand=1.0, metric='EUCLIDEAN', dims='3D'):
    n = g.n('ShaderNodeTexVoronoi', feature=feature, distance=metric, voronoi_dimensions=dims)
    if vec is not None:
        g.put(n.inputs['Vector'], vec)
    n.inputs['Scale'].default_value = scale
    n.inputs['Randomness'].default_value = rand
    return n.outputs[out]


def stretch(g, co, sx, sy, sz):
    x, y, z = g.xyz(co)
    return g.comb(g.m('MULTIPLY', x, sx), g.m('MULTIPLY', y, sy), g.m('MULTIPLY', z, sz))


def add_bumps(g, b, *hs):
    """Chain several (height, strength, distance) bumps into the BSDF normal."""
    nrm = None
    for (h, s, d) in hs:
        bn = g.n('ShaderNodeBump')
        g.put(bn.inputs['Strength'], s)
        bn.inputs['Distance'].default_value = d
        g.put(bn.inputs['Height'], h)
        if nrm is not None:
            g.put(bn.inputs['Normal'], nrm)
        nrm = bn.outputs[0]
    g.put(b.inputs['Normal'], nrm)
    return nrm


def clamp01(g, v):
    return g.m('MULTIPLY', v, 1.0, clamp=True)


def streaks(g, co, sx, sz, scale=1.0, lo=0.55, hi=0.75, detail=3.0):
    """Vertical streak mask (drips): noise stretched along world/object z."""
    return g.mr(g.noise(stretch(g, co, sx, sx, sz), scale, detail, 0.55), lo, hi, 0.0, 1.0, smooth=True)


def box_falloff(g, co, c, half, soft):
    """1 inside an axis box around c (half sizes), soft edge `soft` (metres)."""
    x, y, z = g.xyz(co)
    k = None
    for v, cc, hh in ((x, c[0], half[0]), (y, c[1], half[1]), (z, c[2], half[2])):
        if hh is None:
            continue
        d = g.m('ABSOLUTE', g.m('SUBTRACT', v, cc))
        m_ = g.mr(d, hh + soft, hh, 0.0, 1.0, smooth=True)
        k = m_ if k is None else g.m('MULTIPLY', k, m_)
    return k


def mat_cache(fn):
    cache = {}

    def wrap(*a, **kw):
        key = repr((fn.__name__, a, sorted(kw.items())))
        m = cache.get(key)
        try:
            if m is not None and m.name in bpy.data.materials:
                return m
        except ReferenceError:
            pass
        m = fn(*a, **kw)
        cache[key] = m
        return m
    wrap.cache = cache
    return wrap


# ============================================================================= material library (SHOTS §a)

@mat_cache
def mat_alu(name='alu_oxidised', seed=0.0):
    """Weathered aluminium tube: metal #B9B6B0, roughness 0.38-0.62 by noise, chalky white oxidation patches on
    up-facing sides, fine longitudinal brushing (object z = the tube axis), grime in cavities."""
    m, b, g = B.principled(name, '#B9B6B0', rough=0.45, metal=1.0)
    co = g.n('ShaderNodeVectorMath', operation='ADD')
    g.put(co.inputs[0], g.co('Object'))
    co.inputs[1].default_value = (seed * 3.1, seed * 1.7, seed * 2.3)
    co = co.outputs[0]
    rough = g.mr(g.noise(co, 40.0, 3.0, 0.55), 0.3, 0.7, 0.38, 0.62)
    brushed = g.noise(stretch(g, co, 900.0, 900.0, 14.0), 1.0, 3.0, 0.6)
    patch = g.mr(g.noise(co, 7.0, 4.0, 0.62), 0.50, 0.64, 0.0, 1.0, smooth=True)
    speck = g.mr(g.noise(co, 260.0, 2.0, 0.6), 0.55, 0.75, 0.0, 1.0)
    up = up_mask(g, -0.3, 0.9)
    ox = clamp01(g, g.m('MULTIPLY', g.m('ADD', g.m('MULTIPLY', patch, 0.9), g.m('MULTIPLY', speck, 0.35)),
                       g.m('ADD', g.m('MULTIPLY', up, 0.8), 0.2)))
    grime = g.mr(ao(g, 0.012), 0.35, 1.0, 1.0, 0.0)
    metal_c = g.mix(g.mr(brushed, 0.3, 0.7, 0.0, 1.0), C('#AEABA5'), C('#C4C1BB'))
    base = g.mix(ox, metal_c, C('#D8D4CC'))
    base = g.mix(g.m('MULTIPLY', grime, 0.8), base, C('#2E2A25'))
    g.put(b.inputs['Base Color'], base)
    g.put(b.inputs['Metallic'], g.m('SUBTRACT', 1.0, g.m('MULTIPLY', ox, 0.95)))
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', ox, g.m('SUBTRACT', 0.88, rough)), rough))
    add_bumps(g, b, (brushed, 0.18, 0.00015), (g.noise(co, 500.0, 2.0, 0.6), g.m('MULTIPLY', ox, 0.35), 0.0002))
    return m


@mat_cache
def mat_gi_pipe(name='gi_pipe', contacts=(), top=None, mark=None, rust=1.0):
    """Galvanised iron pipe (object coords: z up the pipe, xy across). Zinc spangle, rust bands at the clamp
    contacts `contacts` (object z), drip lines below them, rusty threads near `top`; optional hand-painted white
    index mark `mark` = (angle_deg, z0, z1, width_m) in object coords (rotates with the pipe)."""
    m, b, g = B.principled(name, '#9A9A94', rough=0.34, metal=1.0)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    cell = vor(g, co, 260.0, out='Color')
    cr, _, _ = g.xyz(cell)
    spg_r = g.m('MULTIPLY_ADD', cr, 0.16, 0.26)
    spg_c = g.mix(cr, C('#8E8E89'), C('#A6A6A0'))
    dull = g.mr(g.noise(co, 5.0, 3.0, 0.6), 0.35, 0.7, 0.0, 1.0)
    spg_c = g.mix(g.m('MULTIPLY', dull, 0.5), spg_c, C('#7E7C76'))
    rmask = g.m('MULTIPLY', g.mr(g.noise(co, 9.0, 4.0, 0.65), 0.60, 0.74, 0.0, 1.0, smooth=True), 0.6)
    drip = streaks(g, co, 140.0, 3.0, 1.0, 0.52, 0.72)
    for zc in contacts:
        dz = g.m('SUBTRACT', z, zc)
        band = g.m('MULTIPLY', g.mr(g.m('ABSOLUTE', dz), 0.045, 0.006, 0.0, 1.0, smooth=True),
                   g.mr(g.noise(co, 60.0, 3.0, 0.6), 0.3, 0.6, 0.4, 1.0))
        below = g.m('MULTIPLY', g.mr(dz, -0.45, -0.02, 0.0, 1.0, smooth=True), g.mr(dz, 0.0, -0.02, 0.0, 1.0))
        rmask = g.m('MAXIMUM', rmask, g.m('MAXIMUM', band, g.m('MULTIPLY', below, drip)))
    if top is not None:
        dz = g.m('SUBTRACT', top, z)
        tz = g.m('MULTIPLY', g.mr(dz, 0.10, 0.0, 0.0, 1.0, smooth=True), g.mr(g.noise(co, 40.0, 3.0, 0.6), 0.3, 0.55, 0.5, 1.0))
        below = g.m('MULTIPLY', g.mr(dz, 0.6, 0.05, 0.0, 1.0, smooth=True), drip)
        rmask = g.m('MAXIMUM', rmask, g.m('MAXIMUM', tz, below))
        thread = g.m('MULTIPLY', g.m('SINE', g.m('MULTIPLY', z, 2 * math.pi / 0.00231)), g.mr(dz, 0.026, 0.022, 0.0, 1.0))
    rmask = clamp01(g, g.m('MULTIPLY', rmask, rust))
    rn = g.noise(co, 180.0, 4.0, 0.65)
    rust_c = g.mix(g.mr(rn, 0.35, 0.7, 0.0, 1.0), C('#5E3219'), C('#A0522D'))
    rust_c = g.mix(g.mr(g.noise(co, 30.0, 3.0, 0.6), 0.5, 0.8, 0.0, 1.0), rust_c, C('#3E2414'))
    base = g.mix(rmask, spg_c, rust_c)
    metal = g.m('SUBTRACT', 1.0, rmask)
    rough = g.m('ADD', g.m('MULTIPLY', rmask, g.m('SUBTRACT', 0.9, spg_r)), spg_r)
    if mark is not None:
        ang, z0, z1, wid = mark
        th = g.m('ARCTAN2', y, x)
        d = g.m('ABSOLUTE', g.m('SUBTRACT', th, math.radians(ang)))
        d = g.m('MINIMUM', d, g.m('SUBTRACT', 2 * math.pi, d))
        jit = g.m('MULTIPLY', g.m('SUBTRACT', g.noise(stretch(g, co, 1.0, 1.0, 1.0), 900.0, 3.0, 0.6), 0.5), 0.05)
        half = (wid / 2) / 0.021
        mk = g.mr(g.m('ADD', d, jit), half + 0.02, half - 0.02, 0.0, 1.0, smooth=True)
        zz = g.m('ADD', z, g.m('MULTIPLY', g.m('SUBTRACT', g.noise(co, 700.0, 2.0, 0.6), 0.5), 0.003))
        mk = g.m('MULTIPLY', mk, g.m('MULTIPLY', g.mr(zz, z0 - 0.001, z0 + 0.001, 0.0, 1.0), g.mr(zz, z1 + 0.002, z1 - 0.002, 0.0, 1.0)))
        chip = g.mr(g.noise(co, 1400.0, 2.0, 0.7), 0.62, 0.66, 1.0, 0.0)
        mk = g.m('MULTIPLY', mk, chip)
        paint = g.mix(g.mr(g.noise(co, 300.0, 2.0, 0.6), 0.3, 0.8, 0.0, 1.0), C('#E8E2D2'), C('#D6CDB8'))
        base = g.mix(mk, base, paint)
        metal = g.m('MULTIPLY', metal, g.m('SUBTRACT', 1.0, mk))
        rough = g.m('ADD', g.m('MULTIPLY', mk, g.m('SUBTRACT', 0.5, rough)), rough)
    g.put(b.inputs['Base Color'], base)
    g.put(b.inputs['Metallic'], metal)
    g.put(b.inputs['Roughness'], rough)
    bumps = [(g.m('MULTIPLY', rn, rmask), 0.5, 0.0006), (g.noise(co, 900.0, 2.0, 0.6), 0.06, 0.0001)]
    if top is not None:
        bumps.append((thread, 0.6, 0.0004))
    add_bumps(g, b, *bumps)
    return m


@mat_cache
def mat_strap(name='steel_strap', mark=None):
    """Mild-steel strap: mostly rust (#5A2E16 / #8B4513), flaking green-grey paint remnants (~30 %), pitting bump;
    optional white paint index mark `mark` = (centre xyz, half sizes xyz) in object coords."""
    m, b, g = B.principled(name, '#5A2E16', rough=0.88)
    co = g.co('Object')
    rn = g.noise(co, 220.0, 5.0, 0.65)
    big = g.noise(co, 30.0, 3.0, 0.6)
    rust_c = g.mix(g.mr(rn, 0.3, 0.7, 0.0, 1.0), C('#4A2412'), C('#8B4513'))
    rust_c = g.mix(g.mr(big, 0.55, 0.75, 0.0, 1.0), rust_c, C('#A35A26'))
    pn = g.noise(co, 55.0, 5.0, 0.7, dist=0.4)
    paint = g.mr(pn, 0.54, 0.565, 0.0, 1.0)
    paint_c = g.mix(g.mr(g.noise(co, 140.0, 2.0, 0.6), 0.3, 0.7, 0.0, 1.0), C('#5F6B5C'), C('#6E786A'))
    base = g.mix(paint, rust_c, paint_c)
    rough = g.m('ADD', g.m('MULTIPLY', paint, -0.3), 0.9)
    h = g.m('ADD', g.m('MULTIPLY', paint, 0.35), g.m('MULTIPLY', rn, 0.65))
    if mark is not None:
        c, hs = mark
        jit = g.n('ShaderNodeVectorMath', operation='ADD')
        g.put(jit.inputs[0], co)
        g.put(jit.inputs[1], vsc(g, g.noise(co, 500.0, 2.0, 0.6, color=True), 0.0012))
        mk = box_falloff(g, jit.outputs[0], c, hs, 0.0008)
        chip = g.mr(g.noise(co, 1100.0, 2.0, 0.7), 0.64, 0.67, 1.0, 0.0)
        mk = g.m('MULTIPLY', mk, chip)
        base = g.mix(mk, base, C('#E5DECD'))
        rough = g.m('ADD', g.m('MULTIPLY', mk, -0.4), rough)
        h = g.m('ADD', h, g.m('MULTIPLY', mk, 0.4))
    g.put(b.inputs['Base Color'], base)
    g.put(b.inputs['Roughness'], rough)
    add_bumps(g, b, (h, 0.55, 0.0005))
    return m


@mat_cache
def mat_rusty_steel(name='rusty_steel', amount=0.7):
    """Bolts, nuts, U-bolts, clamp plate: zinc-plated steel going to rust bloom."""
    m, b, g = B.principled(name, '#8E8C86', rough=0.4, metal=1.0)
    co = g.co('Object')
    rn = g.noise(co, 300.0, 4.0, 0.65)
    rm = clamp01(g, g.m('MULTIPLY', g.mr(g.noise(co, 60.0, 4.0, 0.65), 0.62 - 0.25 * amount, 0.72 - 0.2 * amount, 0.0, 1.0, smooth=True), 1.0))
    cav = g.mr(ao(g, 0.004), 0.3, 0.95, 1.0, 0.0)
    rm = clamp01(g, g.m('ADD', rm, g.m('MULTIPLY', cav, amount)))
    rust_c = g.mix(g.mr(rn, 0.3, 0.7, 0.0, 1.0), C('#4E2713'), C('#9A4E22'))
    g.put(b.inputs['Base Color'], g.mix(rm, C('#8A8882'), rust_c))
    g.put(b.inputs['Metallic'], g.m('SUBTRACT', 1.0, rm))
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', rm, 0.5), 0.38))
    add_bumps(g, b, (g.m('MULTIPLY', rn, rm), 0.6, 0.0004))
    return m


@mat_cache
def mat_abs(name='plastic_abs_aged', base='#151312', faded='#3A3632', rough=0.45):
    """Black ABS: sun-faded grey on up-facing faces, micro-scratches, dust in edges/cavities."""
    m, b, g = B.principled(name, base, rough=rough, spec=0.5)
    co = g.co('Object')
    up = up_mask(g, 0.0, 0.9)
    fade = g.m('MULTIPLY', up, g.mr(g.noise(co, 25.0, 3.0, 0.6), 0.3, 0.7, 0.6, 1.0))
    c = g.mix(fade, C(base), C(faded))
    dust = g.m('MULTIPLY', g.mr(ao(g, 0.006), 0.3, 0.9, 1.0, 0.0), 0.7)
    dust = g.m('MAXIMUM', dust, g.m('MULTIPLY', up, g.mr(g.noise(co, 120.0, 3.0, 0.6), 0.5, 0.8, 0.0, 0.35)))
    c = g.mix(dust, c, C('#6E655B'))
    scr = g.mr(g.noise(stretch(g, co, 2400.0, 60.0, 2400.0), 1.0, 2.0, 0.5), 0.72, 0.8, 0.0, 1.0)
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('ADD', g.m('MULTIPLY', fade, 0.18), g.m('MULTIPLY', dust, 0.3)), rough))
    add_bumps(g, b, (scr, 0.12, 0.0001), (g.noise(co, 1500.0, 2.0, 0.6), 0.05, 0.0001))
    return m


@mat_cache
def mat_coax(name='coax_pvc'):
    m, b, g = B.principled(name, '#1C1A19', rough=0.6, spec=0.45)
    co = g.co('Object')
    up = up_mask(g, 0.0, 0.9)
    c = g.mix(g.m('MULTIPLY', up, 0.85), C('#1C1A19'), C('#3B3734'))
    dust = g.mr(g.noise(co, 90.0, 3.0, 0.6), 0.55, 0.8, 0.0, 0.4)
    c = g.mix(g.m('MULTIPLY', dust, up), c, C('#6A6158'))
    g.put(b.inputs['Base Color'], c)
    add_bumps(g, b, (g.noise(co, 700.0, 2.0, 0.6), 0.08, 0.0002))
    return m


@mat_cache
def mat_tape(name='pvc_tape'):
    m, b, g = B.principled(name, '#0E0D0D', rough=0.35, spec=0.55, coat=0.2, coat_rough=0.2)
    co = g.co('Object')
    c = g.mix(g.m('MULTIPLY', up_mask(g), 0.6), C('#0E0D0D'), C('#2A2826'))
    g.put(b.inputs['Base Color'], c)
    add_bumps(g, b, (g.noise(co, 400.0, 3.0, 0.6), 0.15, 0.0002))
    return m


@mat_cache
def mat_plaster(name='plaster_weathered', top=0.90, clamps=(), chip=None, base='#8E8478'):
    """Cement-plastered brick parapet (object coords = world: objects built at the origin). Mottling, water stains
    running down from the coping, black algae streaks, rust streaks under the clamps [(x, z, y_face)], hairline
    cracks, an optional chipped corner exposing brick `chip` = (centre xyz, radius)."""
    m, b, g = B.principled(name, base, rough=0.9, spec=0.35)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    mott = g.noise(co, 3.0, 5.0, 0.62)
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', mott, 0.5), 0.35, 1.0)
    fine = g.noise(co, 80.0, 4.0, 0.6)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', fine, 0.16, 0.92))
    c = vsc(g, rgb(g, base), k)
    dtop = g.m('SUBTRACT', top, z)
    wst = g.m('MULTIPLY', streaks(g, co, 9.0, 0.7, 1.0, 0.45, 0.68), g.mr(dtop, 0.75, 0.02, 0.0, 1.0, smooth=True))
    c = g.mix(g.m('MULTIPLY', wst, 0.75), c, C('#5D5248'))
    alg = g.m('MULTIPLY', streaks(g, co, 14.0, 1.4, 1.3, 0.6, 0.75), g.mr(dtop, 0.5, 0.0, 0.0, 1.0, smooth=True))
    alg = g.m('MAXIMUM', alg, g.m('MULTIPLY', g.mr(z, 0.18, 0.0, 0.0, 0.8, smooth=True), g.mr(g.noise(co, 6.0, 4.0, 0.6), 0.45, 0.7, 0.0, 1.0)))
    c = g.mix(g.m('MULTIPLY', alg, 0.8), c, C('#24221D'))
    for (cx, cz, _yf) in clamps:
        dx = g.m('ABSOLUTE', g.m('SUBTRACT', x, cx))
        dzc = g.m('SUBTRACT', cz, z)
        wx = g.mr(dx, 0.10, 0.02, 0.0, 1.0, smooth=True)
        wz = g.m('MULTIPLY', g.mr(dzc, -0.01, 0.02, 0.0, 1.0), g.mr(dzc, 0.45, 0.05, 0.0, 1.0, smooth=True))
        rs = g.m('MULTIPLY', g.m('MULTIPLY', wx, wz), streaks(g, co, 160.0, 4.0, 1.0, 0.42, 0.66))
        halo = g.m('MULTIPLY', g.mr(dx, 0.12, 0.05, 0.0, 1.0, smooth=True), g.mr(g.m('ABSOLUTE', dzc), 0.05, 0.0, 0.0, 0.6, smooth=True))
        rs = g.m('MAXIMUM', rs, halo)
        c = g.mix(g.m('MULTIPLY', rs, 0.85), c, C('#8B4A22'))
    crk = vor(g, stretch(g, co, 1.0, 1.0, 1.6), 5.0, feature='DISTANCE_TO_EDGE')
    nd = g.noise(co, 30.0, 3.0, 0.6)
    crk = g.m('ADD', crk, g.m('MULTIPLY', g.m('SUBTRACT', nd, 0.5), 0.06))
    cmask = g.m('MULTIPLY', g.mr(crk, 0.004, 0.0, 0.0, 1.0), g.mr(g.noise(co, 2.0, 2.0, 0.5), 0.5, 0.62, 0.0, 1.0))
    c = g.mix(g.m('MULTIPLY', cmask, 0.9), c, C('#3A332C'))
    h = g.m('ADD', g.m('MULTIPLY', fine, 0.6), g.m('MULTIPLY', g.noise(co, 400.0, 3.0, 0.6), 0.4))
    h = g.m('SUBTRACT', h, g.m('MULTIPLY', cmask, 0.8))
    if chip is not None:
        (ccx, ccy, ccz), rr = chip
        dx = g.m('SUBTRACT', x, ccx)
        dy = g.m('SUBTRACT', y, ccy)
        dz = g.m('SUBTRACT', z, ccz)
        dd = g.m('SQRT', g.m('ADD', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy)), g.m('MULTIPLY', dz, dz)))
        dd = g.m('ADD', dd, g.m('MULTIPLY', g.m('SUBTRACT', g.noise(co, 25.0, 4.0, 0.7), 0.5), rr * 0.8))
        chm = g.mr(dd, rr, rr * 0.9, 0.0, 1.0)
        # brick + mortar courses (75 mm + 10 mm) under the plaster
        mort = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', g.m('FRACT', g.m('DIVIDE', z, 0.085)), 0.5)), 0.44, 0.40, 0.0, 1.0)
        brick = g.mix(mort, g.mix(g.mr(g.noise(co, 40.0, 3.0, 0.6), 0.3, 0.7, 0.0, 1.0), C('#7A3E28'), C('#9A5537')), C('#8C857A'))
        c = g.mix(chm, c, brick)
        h = g.m('SUBTRACT', h, g.m('MULTIPLY', chm, 1.2))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', g.m('MAXIMUM', wst, alg), 0.05), 0.88))
    add_bumps(g, b, (h, 0.35, 0.0012))
    return m


@mat_cache
def mat_concrete(name='roof_screed'):
    m, b, g = B.principled(name, '#857C71', rough=0.93, spec=0.35)
    co = g.co('Object')
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', g.noise(co, 1.5, 5.0, 0.62), 0.5), 0.4, 1.0)
    c = vsc(g, rgb(g, '#857C71'), k)
    stain = g.mr(g.noise(co, 0.6, 3.0, 0.6), 0.5, 0.7, 0.0, 1.0)
    c = g.mix(g.m('MULTIPLY', stain, 0.5), c, C('#4E463E'))
    g.put(b.inputs['Base Color'], c)
    add_bumps(g, b, (g.noise(co, 300.0, 3.0, 0.6), 0.3, 0.001))
    return m


@mat_cache
def mat_hdpe(name='hdpe_tank'):
    m, b, g = B.principled(name, '#121212', rough=0.55, spec=0.5)
    co = g.co('Object')
    up = up_mask(g, 0.0, 0.9)
    c = g.mix(g.m('MULTIPLY', up, g.mr(g.noise(co, 4.0, 3.0, 0.6), 0.3, 0.7, 0.6, 1.0)), C('#121212'), C('#3A3836'))
    dust = g.mr(g.noise(co, 20.0, 4.0, 0.6), 0.55, 0.8, 0.0, 0.5)
    c = g.mix(g.m('MULTIPLY', dust, g.m('ADD', up, 0.3)), c, C('#6B6156'))
    st = streaks(g, co, 12.0, 0.8, 1.0, 0.55, 0.72)
    c = g.mix(g.m('MULTIPLY', st, 0.35), c, C('#5A5148'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', up, 0.2), 0.5))
    add_bumps(g, b, (g.noise(co, 200.0, 3.0, 0.6), 0.1, 0.0005))
    return m


@mat_cache
def mat_paint_steel(name='painted_steel', base='#5F6B5C'):
    m, b, g = B.principled(name, base, rough=0.6)
    co = g.co('Object')
    rn = g.noise(co, 150.0, 4.0, 0.6)
    rm = g.mr(g.noise(co, 25.0, 4.0, 0.65), 0.58, 0.68, 0.0, 1.0, smooth=True)
    c = g.mix(rm, C(base), g.mix(rn, C('#4A2412'), C('#8B4513')))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', rm, 0.3), 0.58))
    add_bumps(g, b, (g.m('MULTIPLY', rn, rm), 0.4, 0.0005))
    return m


@mat_cache
def mat_wood_peg(name='wood_peg'):
    m, b, g = B.principled(name, '#9C7A52', rough=0.7)
    co = g.co('Object')
    gr = g.wave(stretch(g, co, 1.0, 1.0, 0.1), 300.0, 4.0, 3.0, bands='Z')
    c = g.mix(g.mr(gr, 0.0, 1.0, 0.0, 1.0), C('#8A6A45'), C('#A9895F'))
    c = g.mix(g.m('MULTIPLY', up_mask(g), 0.5), c, C('#8E8A80'))
    g.put(b.inputs['Base Color'], c)
    return m


@mat_cache
def mat_far(name='far_building', base='#8C8276', haze='#E8C9A0', dist0=6.0, dist1=60.0, emit=0.6):
    """Distant rooftops: plaster variation faded into the sky haze with view distance (aerial perspective)."""
    m, b, g = B.principled(name, base, rough=0.9)
    co = g.co('Object')
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', g.noise(co, 0.8, 4.0, 0.6), 0.5), 0.5, 1.0)
    c = vsc(g, rgb(g, base), k)
    st = streaks(g, co, 4.0, 0.4, 1.0, 0.5, 0.7)
    c = g.mix(g.m('MULTIPLY', st, 0.6), c, C('#4A4038'))
    cam = g.n('ShaderNodeCameraData').outputs['View Distance']
    f = g.mr(cam, dist0, dist1, 0.12, 0.8)
    g.put(b.inputs['Base Color'], g.mix(f, c, C(haze)))
    g.put(b.inputs['Emission Color'], rgb(g, haze))
    g.put(b.inputs['Emission Strength'], g.m('MULTIPLY', f, emit))
    return m


# ============================================================================= sky + sun (plausible sources only)

SUN = {   # direction TO the sun: azimuth from +X towards +Y (deg), elevation (deg); colour; sun strength (W/m^2)
    'day': dict(az=130.0, el=14.0, color='#FFD7A0', strength=4.0, angle=0.6,
                zenith='#6F8CB0', mid='#C9C3B4', horizon='#F3CF9C', glow='#FFD9A0', ground='#6A5E52',
                glow_k=(1.4, 0.55), sky_k=1.0, disc=0.0),
    'sunset': dict(az=81.0, el=3.0, color='#FFB45A', strength=3.0, angle=0.6,
                   zenith='#46557E', mid='#B5806F', horizon='#FF9F55', glow='#FFB866', ground='#3A2C26',
                   glow_k=(3.2, 1.0), sky_k=0.95, disc=60.0),
    'room': None,
}


def sun_vec(az, el):
    a, e = math.radians(az), math.radians(el)
    return (math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))


def world_sky(variant):
    """Analytic golden-hour sky: zenith -> mid -> horizon gradient, a two-lobe glow around the sun, an optional
    visible sun disc (sunset), a dim ground below the horizon. Lights the scene as fill; the key is a real Sun lamp."""
    P = SUN[variant]
    w = bpy.data.worlds.new('W_sky_' + variant)
    bpy.context.scene.world = w
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    g = B.G(nt)
    d = g.n('ShaderNodeVectorMath', operation='NORMALIZE')
    g.put(d.inputs[0], g.n('ShaderNodeTexCoord').outputs['Generated'])
    d = d.outputs[0]
    _, _, ez = g.xyz(d)
    sv = sun_vec(P['az'], P['el'])
    dot = g.n('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.put(dot.inputs[0], d)
    dot.inputs[1].default_value = sv
    cosang = dot.outputs['Value']
    t_hi = g.m('POWER', g.mr(ez, 0.0, 1.0, 0.0, 1.0), 0.55)
    c = g.mix(g.mr(t_hi, 0.0, 0.35, 0.0, 1.0, smooth=True), C(P['horizon']), C(P['mid']))
    c = g.mix(g.mr(t_hi, 0.3, 1.0, 0.0, 1.0, smooth=True), c, C(P['zenith']))
    one_m = g.m('SUBTRACT', 1.0, cosang)
    lobe1 = g.m('EXPONENT', g.m('MULTIPLY', g.m('DIVIDE', one_m, 0.012), -1.0))
    lobe2 = g.m('EXPONENT', g.m('MULTIPLY', g.m('DIVIDE', one_m, 0.22), -1.0))
    glow = g.m('ADD', g.m('MULTIPLY', lobe1, P['glow_k'][0]), g.m('MULTIPLY', lobe2, P['glow_k'][1]))
    glow = g.m('MULTIPLY', glow, g.mr(ez, -0.03, 0.02, 0.0, 1.0, smooth=True))
    gl = vsc(g, rgb(g, P['glow']), glow)
    ca = g.n('ShaderNodeVectorMath', operation='ADD')
    g.put(ca.inputs[0], c)
    g.put(ca.inputs[1], gl)
    c = ca.outputs[0]
    if P['disc']:
        cosd = math.cos(math.radians(0.55 / 2))
        disc = g.mr(cosang, cosd - 0.000012, cosd + 0.000004, 0.0, P['disc'], smooth=True)
        disc = g.m('MULTIPLY', disc, g.mr(ez, -0.002, 0.004, 0.0, 1.0))
        da = g.n('ShaderNodeVectorMath', operation='ADD')
        g.put(da.inputs[0], c)
        g.put(da.inputs[1], vsc(g, rgb(g, '#FFE6B8'), disc))
        c = da.outputs[0]
    c = g.mix(g.mr(ez, 0.0, -0.04, 0.0, 1.0, smooth=True), c, C(P['ground']))
    bg = g.n('ShaderNodeBackground')
    g.put(bg.inputs['Color'], c)
    bg.inputs['Strength'].default_value = P['sky_k']
    out = g.n('ShaderNodeOutputWorld')
    nt.links.new(bg.outputs[0], out.inputs[0])
    return w


def sun_lamp(variant, energy_k=1.0):
    P = SUN[variant]
    ld = bpy.data.lights.new('SUN_' + variant, 'SUN')
    ld.energy = P['strength'] * energy_k
    ld.color = hue(P['color'])
    ld.angle = math.radians(P['angle'])
    o = B.link(bpy.data.objects.new('SUN_' + variant, ld))
    sv = Vector(sun_vec(P['az'], P['el']))
    o.rotation_euler = (-sv).to_track_quat('-Z', 'Y').to_euler()
    o['group'] = 'sun'
    return o


# ============================================================================= roof scene (A1, A2, A3)

PIPE_R = 0.021                      # 42 mm OD GI pipe
MAST = (0.0, -0.032)                # pipe axis (x, y); parapet inside face is the plane y = 0
PARA_T, PARA_H, COPING = 0.23, 0.84, 0.06
TOP = PARA_H + COPING               # 0.90 m
CLAMP_Z = (0.72, 0.36)
STRAP_W, STRAP_T = 0.025, 0.003
BOOM_Z, MAST_TOP = 2.98, 3.10
YAW0 = 60.0                          # world azimuth of the boom (directors) at yaw 0: right and away from CAM_ROOF
BOOM_Y = -(PIPE_R + 0.005 + 0.0095)  # boom axis offset from the mast axis (antenna-local y)
REFL_X, DIP_X = -0.30, -0.12
DIR_X = (0.07, 0.24, 0.41, 0.59, 0.77, 0.96, 1.15)
DIR_L = tuple(float(v) for v in np.linspace(0.58, 0.48, 7))
BOOM_X0, BOOM_X1 = -0.32, 1.18
EL_R = 0.00475                       # 9.5 mm rods
EL_Z = BOOM_Z + 0.0095 + 0.0105      # element axis height (on top saddles)
MARK_ANG = 252.0                     # world angle of the aligned paint marks (strap + pipe at yaw 0)
COAX_ANG = 90.0 - (YAW0 - 15.0)      # antenna-local angle of the coax run on the mast (wall side at mid yaw)


def strap_clamp(name, z, mat, bolt_mat, mark=False, parent=None):
    """Flat strap 25 x 3 mm wrapped round the front of the pipe, two ears on the wall with M8 bolts + washers."""
    cx, cy = MAST
    R = PIPE_R + STRAP_T / 2 + 0.0004
    yw = -STRAP_T / 2
    ex0, ex1 = 0.034, 0.088

    def tang(ax, ay, side):
        d = math.hypot(ax - cx, ay - cy)
        a = math.atan2(ay - cy, ax - cx)
        b_ = math.acos(R / d)
        cands = [a + b_, a - b_]
        pts = [(cx + R * math.cos(t), cy + R * math.sin(t), t) for t in cands]
        return min(pts, key=lambda p: p[1])
    L = tang(-ex0, yw, -1)
    Rt = tang(ex0, yw, 1)
    path = [(-ex1, yw), (-ex0 - 0.006, yw)]
    # small bend from the ear into the straight run
    path += [(-ex0, yw - 0.0004)]
    n_s = 6
    for i in range(1, n_s):
        t = i / n_s
        path.append((-ex0 + (L[0] + ex0) * t, yw + (L[1] - yw) * t))
    t0, t1 = L[2], Rt[2]
    if t1 < t0:
        t1 += 2 * math.pi
    for i in range(41):
        t = t0 + (t1 - t0) * i / 40
        path.append((cx + R * math.cos(t), cy + R * math.sin(t)))
    for i in range(1, n_s):
        t = i / n_s
        path.append((Rt[0] + (ex0 - Rt[0]) * t, Rt[1] + (yw - Rt[1]) * t))
    path += [(ex0, yw - 0.0004), (ex0 + 0.006, yw), (ex1, yw)]
    P = np.array(path)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    N = np.stack([T[:, 1], -T[:, 0]], 1)       # right-hand normal in xy
    # make N point away from the pipe/wall side consistently (outward = towards -y at the front)
    if N[len(N) // 2, 1] > 0:
        N = -N
    V, F = [], []
    hw, ht = STRAP_W / 2, STRAP_T / 2
    corners = [(-ht, -hw), (ht, -hw), (ht, hw), (-ht, hw)]
    for p, nn in zip(P, N):
        for (o, zz) in corners:
            V.append((p[0] + nn[0] * o, p[1] + nn[1] * o, z + zz))
    m = len(P)
    for i in range(m - 1):
        for j in range(4):
            a = i * 4 + j
            b_ = i * 4 + (j + 1) % 4
            F.append((a, b_, b_ + 4, a + 4))
    F.append((3, 2, 1, 0))
    F.append(tuple((m - 1) * 4 + j for j in range(4)))
    o = _mesh(name, V, F, mat, smooth=True, sharp=40.0, parent=parent)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    o.data.set_sharp_from_angle(angle=math.radians(40))
    bevel_mod(o, 0.0006, 2, 40)
    parts = [o]
    for k, sx in enumerate((-1, 1)):
        bx = sx * 0.061
        wsh = lathe_obj(f'{name}_washer{k}', [(0.0042, 0.0), (0.008, 0.0), (0.008, 0.0016), (0.0042, 0.0016)], bolt_mat,
                        seg=40, sharp=50)
        wsh.rotation_euler = (math.radians(90), 0, 0)
        wsh.location = (bx, -STRAP_T, z)
        hd = hexprism(f'{name}_bolt{k}', (bx, -STRAP_T - 0.0016 - 0.00265, z), 0.013, 0.0053, bolt_mat, axis='Y')
        hd.rotation_euler = (math.radians(90), math.radians(17 + 23 * k), 0)
        tip = lathe_obj(f'{name}_thread{k}', [(0.0039, 0.0), (0.0039, 0.004), (0.0033, 0.0048), (1e-5, 0.0048)], bolt_mat, seg=24)
        tip.rotation_euler = (math.radians(90), 0, 0)
        tip.location = (bx, -STRAP_T - 0.0016 - 0.0053, z)
        parts += [wsh, hd, tip]
    for p_ in parts:
        p_['role'] = 'clamp'
    feats = {'bolt_l': (-0.061, -STRAP_T - 0.0069, z), 'bolt_r': (0.061, -STRAP_T - 0.0069, z)}
    a = math.radians(MARK_ANG)
    feats['strap_mark'] = (cx + (R + 0.0016) * math.cos(a), cy + (R + 0.0016) * math.sin(a), z + hw - 0.006)
    return parts, feats


def strap_material(z, mark):
    if not mark:
        return mat_strap('steel_strap')
    cx, cy = MAST
    R = PIPE_R + STRAP_T + 0.0004
    a = math.radians(MARK_ANG)
    c = (cx + R * math.cos(a), cy + R * math.sin(a), z + STRAP_W / 2 - 0.0055)
    return mat_strap('steel_strap_marked', mark=(c, (0.0042, 0.0042, 0.0065)))


def pipe_mark():
    """Hand-painted vertical stroke 6 x 40 mm on the pipe just above the upper strap, aligned with the strap mark at
    yaw 0 (pipe-local angle; the pipe object carries rotation YAW0 + yaw)."""
    z0 = CLAMP_Z[0] + STRAP_W / 2 + 0.002
    return (MARK_ANG - YAW0, z0, z0 + 0.040, 0.006)


def build_antenna(q=1.0):
    """Yagi VHF/UHF combo on the GI mast. Returns (root, objs, feature_fn). The root sits on the mast axis; its
    rotation z = YAW0 + yaw (everything above, the mast and the coax turn together)."""
    root = empty('ANT_ROOT', (MAST[0], MAST[1], 0.0))
    alu = mat_alu('alu_oxidised', seed=0.0)
    alu2 = mat_alu('alu_oxidised_b', seed=1.0)
    abs_ = mat_abs()
    steel = mat_rusty_steel('rusty_steel', 0.75)
    pipe_m = mat_gi_pipe('gi_pipe_mast', contacts=CLAMP_Z + (BOOM_Z + 0.04, BOOM_Z - 0.04), top=MAST_TOP,
                         mark=pipe_mark())
    seg = max(16, int(48 * q))
    objs = []
    # mast: 42 mm pipe from the floor to MAST_TOP (open top, wall 3 mm)
    mast = lathe_obj('mast', [(PIPE_R, 0.0), (PIPE_R, MAST_TOP - 0.002), (PIPE_R - 0.0008, MAST_TOP), (PIPE_R - 0.003, MAST_TOP),
                              (PIPE_R - 0.003, MAST_TOP - 0.03)], pipe_m, seg=seg * 2, sharp=50)
    mast.parent = root
    mast['role'] = 'mast'
    objs.append(mast)
    # boom: 19 mm square aluminium tube, 1 mm wall; front end capped (black ABS), rear cap missing (open end)
    Lb = BOOM_X1 - BOOM_X0
    hb = 0.0095
    boom = loft('boom', [(hb, hb, 0.0016, 0.0), (hb, hb, 0.0016, Lb), (hb - 0.001, hb - 0.001, 0.0008, Lb),
                         (hb - 0.001, hb - 0.001, 0.0008, Lb - 0.06)], alu, k=4, axis='Z', cap0=True, cap1=True, parent=root)
    # local +Z -> antenna -X: closed end (under the front cap) at BOOM_X1, open hollow end (cap missing) at BOOM_X0
    boom.rotation_euler = (0.0, math.radians(-90.0), 0.0)
    boom.location = (BOOM_X1, BOOM_Y, BOOM_Z)
    objs.append(boom)
    cap = rbox('boom_cap', (BOOM_X1 + 0.006, BOOM_Y, BOOM_Z), (0.009, 0.0103, 0.0103), 0.002, 0.0015, abs_, axis='X',
               parent=root)
    objs.append(cap)
    # elements on top saddles (black ABS) with a rivet each
    def element(nm, x, L, bend=0.0, mat=alu):
        y0, y1 = BOOM_Y - L / 2, BOOM_Y + L / 2
        res = []
        if bend:
            mid = (x, BOOM_Y, EL_Z)
            res.append(rod(nm + '_a', (x, y0, EL_Z), mid, EL_R, mat, seg=14, parent=root))
            dy = L / 2 * math.cos(math.radians(bend))
            dz = -L / 2 * math.sin(math.radians(bend))
            res.append(rod(nm + '_b', mid, (x + 0.004, BOOM_Y + dy, EL_Z + dz), EL_R, mat, seg=14, parent=root))
        else:
            res.append(rod(nm, (x, y0, EL_Z), (x, y1, EL_Z), EL_R, mat, seg=14, parent=root))
        sd = rbox(nm + '_saddle', (x, BOOM_Y, BOOM_Z + hb + 0.008), (0.015, 0.012, 0.008), 0.003, 0.002, abs_, parent=root)
        rv = lathe_obj(nm + '_rivet', [(1e-5, 0.0028), (0.0026, 0.0018), (0.0038, 0.0), (0.0038, -0.0005)], steel, seg=16)
        rv.parent = root
        rv.location = (x + 0.009, BOOM_Y, BOOM_Z + hb + 0.016)
        res += [sd, rv]
        for r_ in res:
            r_['role'] = 'antenna'
        return res, (x, y1, EL_Z) if not bend else (x + 0.004, BOOM_Y + L / 2 * math.cos(math.radians(bend)),
                                                    EL_Z - L / 2 * math.sin(math.radians(bend)))
    r_, _ = element('reflector', REFL_X, 0.72, mat=alu2)
    objs += r_
    tips = {}
    for i, (x, L) in enumerate(zip(DIR_X, DIR_L)):
        r_, tip = element(f'dir{i + 1}', x, L, bend=4.0 if i == 2 else 0.0, mat=alu if i % 2 else alu2)
        objs += r_
        tips[i + 1] = tip
    # folded dipole loop (12 mm tube) in the element plane, gap at the rear tube into the terminal box
    Rl, half, sp = 0.025, 0.32, 0.05
    xf, xr = DIP_X + sp / 2, DIP_X - sp / 2
    yc = BOOM_Y
    P = []
    P.append((xr, yc - 0.03, EL_Z))
    for i in range(0, 13):
        t = math.pi * i / 12
        P.append((DIP_X - Rl * math.cos(t), yc - half + Rl - Rl * math.sin(t), EL_Z))
    for i in range(0, 13):
        t = math.pi * i / 12
        P.append((DIP_X + Rl * math.cos(t), yc + half - Rl + Rl * math.sin(t), EL_Z))
    P.append((xr, yc + 0.03, EL_Z))
    dip = tube('dipole', P, 0.006, alu, res=3, order=2, parent=root)
    dip['role'] = 'antenna'
    objs.append(dip)
    for k, sy in enumerate((-1, 1)):
        sd = rbox(f'dip_saddle{k}', (DIP_X, yc + sy * 0.10, BOOM_Z + hb + 0.008), (0.040, 0.012, 0.008), 0.003, 0.002,
                  abs_, parent=root)
        objs.append(sd)
    # terminal box 80 x 50 x 30 (ABS), two lid screws, blank faded sticker
    tb_c = (DIP_X, yc, BOOM_Z + hb + 0.016 + 0.015)
    tb = rbox('term_box', tb_c, (0.025, 0.040, 0.015), 0.004, 0.003, abs_, parent=root)
    objs.append(tb)
    lid_seam = rbox('term_lid', (tb_c[0], tb_c[1], tb_c[2] + 0.0105), (0.0255, 0.0405, 0.0045), 0.004, 0.0015, abs_,
                    parent=root)
    objs.append(lid_seam)
    for k, sy in enumerate((-0.028, 0.028)):
        sc_ = lathe_obj(f'term_screw{k}', [(1e-5, 0.0016), (0.0022, 0.0012), (0.0026, 0.0), (0.0026, -0.0004)], steel, seg=16)
        sc_.parent = root
        sc_.location = (tb_c[0], tb_c[1] + sy, tb_c[2] + 0.015)
        objs.append(sc_)
    stk = rbox('term_sticker', (tb_c[0], tb_c[1], tb_c[2] + 0.0152), (0.016, 0.020, 0.00025), 0.002, 0.0001,
               mat_sticker(), parent=root)
    objs.append(stk)
    # boom-to-mast clamp plate (galvanised, rusty) + U-bolts + nuts
    py = -(PIPE_R + 0.0025)
    plate = rbox('clamp_plate', (0.0, py, BOOM_Z), (0.042, 0.0025, 0.058), 0.006, 0.0008, steel, axis='Y', parent=root)
    objs.append(plate)
    ub_r = 0.004
    for k, zz in enumerate((BOOM_Z + 0.040, BOOM_Z - 0.040)):         # mast U-bolts (horizontal U round the mast)
        Rm = PIPE_R + ub_r
        pts_ = [(-Rm, py - 0.016, zz), (-Rm, 0.0, zz)] + \
            [(-Rm * math.cos(math.pi * i / 12), Rm * math.sin(math.pi * i / 12), zz) for i in range(1, 12)] + \
            [(Rm, 0.0, zz), (Rm, py - 0.016, zz)]
        ub = tube(f'ubolt_mast{k}', pts_, ub_r, steel, res=2, order=2, parent=root)
        objs.append(ub)
        for j, sx in enumerate((-Rm, Rm)):
            nt_ = hexprism(f'nut_m{k}{j}', (sx, py - 0.0025 - 0.0035, zz), 0.013, 0.0065, steel, axis='Y', parent=root)
            objs.append(nt_)
    for k, xx in enumerate((-0.030, 0.030)):                         # boom U-bolts (vertical U round the boom)
        Rb = hb + ub_r + 0.0005
        yb = BOOM_Y
        pts_ = [(xx, py + 0.016, BOOM_Z - Rb), (xx, yb, BOOM_Z - Rb)] + \
            [(xx, yb - Rb * math.sin(math.pi * i / 12), BOOM_Z - Rb * math.cos(math.pi * i / 12)) for i in range(1, 12)] + \
            [(xx, yb, BOOM_Z + Rb), (xx, py + 0.016, BOOM_Z + Rb)]
        ub = tube(f'ubolt_boom{k}', pts_, ub_r, steel, res=2, order=2, parent=root)
        objs.append(ub)
        for j, zz in enumerate((BOOM_Z - Rb, BOOM_Z + Rb)):
            nt_ = hexprism(f'nut_b{k}{j}', (xx, py + 0.0025 + 0.0035, zz), 0.013, 0.0065, steel, axis='Y', parent=root)
            objs.append(nt_)
    # coax RG-6 from the terminal box, a drip loop, then down the mast (wall side) with 3 tape wraps
    coax = mat_coax()
    a = math.radians(COAX_ANG)
    rr = PIPE_R + 0.0036
    mx, my = rr * math.cos(a), rr * math.sin(a)
    cpts = [(DIP_X + 0.026, yc, tb_c[2] - 0.004), (DIP_X + 0.05, yc + 0.012, BOOM_Z - 0.03),
            (DIP_X + 0.04, yc + 0.03, BOOM_Z - 0.20), (DIP_X * 0.3, my * 0.8, BOOM_Z - 0.34),
            (mx, my, BOOM_Z - 0.40), (mx, my, BOOM_Z - 0.60)]
    cpts += [(mx, my, z_) for z_ in np.linspace(BOOM_Z - 0.8, 0.10, 8)]
    cx_ = tube('coax', cpts, 0.0035, coax, res=3, order=3, parent=root)
    objs.append(cx_)
    tape = mat_tape()
    for k, zt in enumerate((2.55, 1.95, 1.35)):
        def ripple(th, z_, a=a):
            dth = np.angle(np.exp(1j * (th - a)))
            return 1.0 + (0.0078 / 0.0222) * np.exp(-(dth / 0.42) ** 2)
        tp = lathe_obj(f'tape{k}', [(0.0222, -0.016), (0.0226, -0.0155), (0.0226, 0.0155), (0.0222, 0.016)], tape, seg=48,
                       ripple=ripple)
        tp.parent = root
        tp.location = (0, 0, zt)
        tp.rotation_euler = (0, 0, 0)
        objs.append(tp)
    for o in objs:
        if o.get('role') in (None, 'prop'):
            o['role'] = 'antenna'

    def features():
        bpy.context.view_layer.update()
        M = root.matrix_world
        f = {'rod_tip': M @ Vector(tips[7]), 'mast_top': M @ Vector((0, 0, MAST_TOP)),
             'dipole_box': M @ Vector(tb_c), 'mast_axis': M @ Vector((0, 0, BOOM_Z)),
             'mast_coping': M @ Vector((0, 0, TOP))}
        return {k: tuple(v) for k, v in f.items()}
    return root, objs, features


@mat_cache
def mat_sticker(name='sticker_faded'):
    """Blank paper sticker, sun-bleached, curling at a corner (no text)."""
    m, b, g = B.principled(name, '#D9D2BF', rough=0.75, spec=0.3)
    co = g.co('Object')
    c = g.mix(g.mr(g.noise(co, 200.0, 4.0, 0.6), 0.3, 0.75, 0.0, 1.0), C('#CFC6AE'), C('#E6DFCB'))
    dirt = g.mr(g.noise(co, 60.0, 3.0, 0.6), 0.55, 0.8, 0.0, 0.6)
    c = g.mix(dirt, c, C('#8C8170'))
    g.put(b.inputs['Base Color'], c)
    add_bumps(g, b, (g.noise(co, 800.0, 3.0, 0.6), 0.2, 0.0002))
    return m


def build_roof(variant, q=1.0, with_clamps=True):
    """Parapet + coping (weathered plaster, rust streaks under the clamps, chipped coping corner), roof screed, two
    strap clamps, an old coax over the coping, black HDPE tank on a brick stand, clothesline with pegs, hazed
    neighbouring rooftops with their own tanks and antennas. Object roles: 'env', 'clamp', 'far'."""
    objs = []
    E = lambda o, role='env': (o.__setitem__('role', role), objs.append(o), o)[2]  # noqa: E731
    clamps = [(MAST[0], z, 0.0) for z in CLAMP_Z]
    chip = ((0.62, -0.03, TOP - 0.012), 0.035)
    wall_m = mat_plaster('plaster_wall', top=PARA_H, clamps=clamps, chip=None)
    cop_m = mat_plaster('plaster_coping', top=TOP + 0.02, clamps=(), chip=chip, base='#948A7E')
    X0, X1 = -14.0, 3.4
    E(B.cube('floor', (X0, -14.0, -0.15), (X1 + 2, 0.0, 0.0), mat_concrete(), role='env'))
    o = E(B.cube('parapet', (X0, 0.0, 0.0), (X1, PARA_T, PARA_H), wall_m, role='env'))
    bevel_mod(o, 0.006, 2)
    o = E(B.cube('coping', (X0, -0.03, PARA_H), (X1 + 0.03, PARA_T + 0.03, TOP), cop_m, role='env'))
    bevel_mod(o, 0.008, 3)
    o = E(B.cube('parapet_side', (X1 - PARA_T, -14.0, 0.0), (X1, 0.0, PARA_H), wall_m, role='env'))
    bevel_mod(o, 0.006, 2)
    o = E(B.cube('coping_side', (X1 - PARA_T - 0.03, -14.0, PARA_H), (X1 + 0.03, 0.0, TOP), cop_m, role='env'))
    bevel_mod(o, 0.008, 3)
    # the strap clamps (upper one carries the white index mark)
    feats = {}
    if with_clamps:
        steel = mat_rusty_steel('rusty_bolts', 0.85)
        for k, z in enumerate(CLAMP_Z):
            parts, f = strap_clamp(f'strap{k}', z, strap_material(z, k == 0), steel, mark=(k == 0))
            for p_ in parts:
                p_['role'] = 'clamp'
                objs.append(p_)
            if k == 0:
                feats.update(f)
    # an older, disused coax looped over the coping (nail-clipped to the face)
    cx = mat_coax('coax_old')
    pts = [(-0.80, -0.30, 0.0), (-0.78, -0.03, 0.02), (-0.77, -0.006, 0.30), (-0.765, -0.006, 0.62),
           (-0.76, -0.03, PARA_H + 0.01), (-0.75, -0.035, TOP + 0.004), (-0.74, 0.08, TOP + 0.0036),
           (-0.73, 0.20, TOP + 0.004), (-0.72, PARA_T + 0.04, TOP - 0.03), (-0.70, PARA_T + 0.006, 0.5)]
    E(tube('coax_old', pts, 0.0035, cx, res=3, order=3))
    clip_m = mat_abs('nail_clip', base='#CFC8BA', faded='#E8E2D6', rough=0.4)
    for k, z in enumerate((0.25, 0.55)):
        E(rbox(f'coax_clip{k}', (-0.768 + 0.001 * k, -0.0045, z), (0.007, 0.0045, 0.004), 0.002, 0.0012, clip_m))
    # black HDPE tank on a plastered brick stand, inlet pipe
    tx, ty, tz = -1.15, 1.55, 0.95       # on the raised stand just behind our parapet (neighbouring mumty roof)
    E(B.cube('tank_stand', (tx - 0.68, ty - 0.68, -0.5), (tx + 0.68, ty + 0.68, tz), wall_m, role='env'))
    prof = []
    Rt, Ht = 0.55, 1.30
    zs = np.linspace(0.0, Ht - 0.12, 60)
    for z_ in zs:
        rib = 0.010 * (0.5 + 0.5 * math.cos(2 * math.pi * z_ / 0.13)) ** 4
        prof.append((Rt - 0.012 + rib, z_))
    for j in range(1, 9):
        a = math.radians(90 * j / 8)
        prof.append((0.21 + (Rt - 0.012 - 0.21) * math.cos(a), Ht - 0.12 + 0.12 * math.sin(a)))
    prof = [(1e-4, 0.0)] + prof
    tank = lathe_obj('tank', prof, mat_hdpe(), seg=int(72 * q) + 24, sharp=60)
    tank.location = (tx, ty, tz)
    E(tank)
    lid = lathe_obj('tank_lid', [(1e-4, 0.05), (0.17, 0.048), (0.205, 0.04), (0.21, 0.0), (0.2, -0.01)], mat_hdpe('hdpe_lid'),
                    seg=48, ripple=lambda th, z_: 1.0 + 0.02 * (np.cos(th * 36) > 0.6) * (z_ < 0.045))
    lid.location = (tx, ty, tz + Ht - 0.005)
    E(lid)
    gi = mat_gi_pipe('gi_pipe_misc', contacts=(0.6,), top=None, mark=None, rust=1.4)
    E(rod('tank_inlet', (tx + 0.5, ty - 0.2, tz - 0.6), (tx + 0.5, ty - 0.2, tz + 0.12), 0.0105, gi, seg=16, cap='flat'))
    E(rod('tank_inlet2', (tx + 0.5, ty - 0.2, tz + 0.12), (tx + 0.47, ty - 0.15, tz + 0.12), 0.0105, gi, seg=16, cap='flat'))
    # clothesline: two GI poles, 3 mm steel wire with a sag, three wooden pegs
    p1, p2 = (0.95, -1.35, 0.0), (3.05, -0.25, 0.0)
    for k, p in enumerate((p1, p2)):
        E(rod(f'line_pole{k}', p, (p[0], p[1], 1.95), 0.0135, gi, seg=16, cap='flat'))
    wire_m = mat_rusty_steel('wire_steel', 0.5)
    wpts = []
    for i in range(13):
        t = i / 12
        x_ = p1[0] + (p2[0] - p1[0]) * t
        y_ = p1[1] + (p2[1] - p1[1]) * t
        wpts.append((x_, y_, 1.90 - 0.10 * 4 * t * (1 - t)))
    E(tube('clothesline', wpts, 0.0015, wire_m, res=2, order=3))
    peg_m = mat_wood_peg()
    for k, t in enumerate((0.33, 0.47, 0.71)):
        x_ = p1[0] + (p2[0] - p1[0]) * t
        y_ = p1[1] + (p2[1] - p1[1]) * t
        z_ = 1.90 - 0.10 * 4 * t * (1 - t)
        pg = rbox(f'peg{k}', (x_, y_, z_ - 0.03), (0.005, 0.0045, 0.036), 0.002, 0.0012, peg_m)
        pg.rotation_euler = (0.0, math.radians(8 * (k - 1)), math.radians(45))
        E(pg)
    # neighbouring rooftops (hazed by distance), their tanks and antennas
    rng = np.random.default_rng(4)
    haze = SUN['day']['horizon'] if variant == 'day' else '#E59A62'
    far_m = mat_far('far_' + variant, haze=haze, emit=0.7 if variant == 'day' else 0.9)
    tankf = mat_far('far_tank_' + variant, base='#1A1A1A', haze=haze, emit=0.7 if variant == 'day' else 0.9)
    alu_far = mat_far('far_alu_' + variant, base='#9A968E', haze=haze, emit=0.5)
    for i in range(26):
        y_ = float(rng.uniform(6.0, 70.0))
        x_ = float(rng.uniform(-30.0, 30.0)) + (y_ - 6) * 0.2
        w_, d_ = float(rng.uniform(3.0, 9.0)), float(rng.uniform(4.0, 10.0))
        top = float(rng.uniform(-2.5, 1.0)) + (y_ / 70.0) * 2.0
        E(B.cube(f'bld{i}', (x_ - w_ / 2, y_, -12.0), (x_ + w_ / 2, y_ + d_, top), far_m, role='far'))
        E(B.cube(f'bld{i}_para', (x_ - w_ / 2, y_, top), (x_ + w_ / 2, y_ + 0.23, top + 0.9), far_m, role='far'))
        if rng.random() < 0.6:
            mx_ = x_ + float(rng.uniform(-w_ / 3, w_ / 3))
            E(B.cube(f'bld{i}_mumty', (mx_ - 1.2, y_ + 1.0, top), (mx_ + 1.2, y_ + 3.6, top + 2.4), far_m, role='far'))
        if rng.random() < 0.7:
            E(B.cyl(f'bld{i}_tank', (x_ + float(rng.uniform(-w_ / 3, w_ / 3)), y_ + 2.0, top + 0.65 + 0.4), 0.55, 1.3,
                    tankf, role='far', seg=24))
        if rng.random() < 0.8:
            ax_, ay_ = x_ + float(rng.uniform(-w_ / 2.5, w_ / 2.5)), y_ + 0.6
            h_ = float(rng.uniform(2.6, 4.5))
            E(rod(f'bld{i}_mast', (ax_, ay_, top), (ax_, ay_, top + h_), 0.025, alu_far, seg=8, cap='flat'))
            yaw_ = float(rng.uniform(0, 180))
            dx, dy = math.cos(math.radians(yaw_)), math.sin(math.radians(yaw_))
            E(rod(f'bld{i}_boom', (ax_ - dx * 0.4, ay_ - dy * 0.4, top + h_ - 0.1), (ax_ + dx * 1.1, ay_ + dy * 1.1, top + h_ - 0.1),
                  0.015, alu_far, seg=6, cap='flat'))
            for j in range(6):
                t = -0.35 + j * 0.28
                L_ = 0.7 - j * 0.04
                cx_, cy_ = ax_ + dx * t, ay_ + dy * t
                E(rod(f'bld{i}_el{j}', (cx_ + dy * L_ / 2, cy_ - dx * L_ / 2, top + h_ - 0.08),
                      (cx_ - dy * L_ / 2, cy_ + dx * L_ / 2, top + h_ - 0.08), 0.008, alu_far, seg=6, cap='flat'))
    feats['mast_coping'] = (MAST[0], MAST[1], TOP)
    return objs, feats


# ============================================================================= cameras

def cam_roof():
    """CAM_ROOF: 35 mm, standing on the roof 1.2 m up, looking up at the mast against the gold sky (sun back-left)."""
    return camera('CAM_ROOF', CAMS['roof']['loc'], CAMS['roof']['target'], 35.0, fstop=5.6,
                  focus=(MAST[0], MAST[1], BOOM_Z - 0.1))


def cam_sunset():
    return camera('CAM_SUNSET', CAMS['sunset']['loc'], CAMS['sunset']['target'], 50.0, fstop=4.0,
                  focus=(MAST[0], MAST[1], BOOM_Z))


CAMS = {
    'roof': dict(loc=(0.45, -3.5, 1.2), target=(0.45, 0.0, 1.2 + 3.5 * math.tan(math.radians(13.0)))),
    'sunset': dict(loc=(-0.45, -6.2, 1.05), target=(-0.20, 0.0, 1.95)),
}


# ============================================================================= pass engine

def set_roles(objs, rules, default='normal'):
    """rules: role -> 'normal' | 'cam_off' (invisible to camera only) | 'holdout' | 'hidden' | 'shadow_off'."""
    for o in objs:
        r = rules.get(o.get('role', 'prop'), default)
        o.hide_render = (r == 'hidden')
        o.is_holdout = (r == 'holdout')
        o.visible_camera = r not in ('cam_off',)
        o.visible_shadow = r not in ('shadow_off',)
        for ch in o.children_recursive:
            pass


def all_objs():
    return [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]


def lights_on(groups):
    for o in bpy.context.scene.objects:
        if o.type == 'LIGHT':
            o.hide_render = o.get('group', '') not in groups


def world_strength(k):
    w = bpy.context.scene.world
    for n in w.node_tree.nodes:
        if n.type == 'BACKGROUND':
            n.inputs['Strength'].default_value = k


def settings(sc, kind, samples):
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.color_depth = '8'
    if kind == 'flat':
        sc.cycles.samples = S_FLAT
        sc.cycles.use_denoising = False
        sc.cycles.use_adaptive_sampling = False
        sc.cycles.max_bounces = 0
        sc.view_settings.view_transform = 'Raw'
        sc.render.image_settings.color_depth = '16'
    else:
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.max_bounces = 12


def proj_px(pts):
    return B.proj(np.asarray(pts, float))


def objs_bbox_px(objs, n=2500):
    p = proj_px(B.mesh_points(objs, n))
    return [float(p[:, 0].min()), float(p[:, 1].min()), float(p[:, 0].max()), float(p[:, 1].max())]


ASSETS = {}
ORDER = ['crt/macro', 'antenna/day_yaw', 'roof/day', 'clamp/macro', 'clamp/pipe_yaw', 'crt/room', 'phone/desk',
         'antenna/sunset_yaw', 'roof/sunset']


def asset(key, mode, labels=None, yaws=None, crop=False, notes=''):
    def deco(fn):
        ASSETS[key] = dict(key=key, mode=mode, labels=labels, yaws=yaws, crop=crop, notes=notes, build=fn)
        return fn
    return deco


def _alpha_bbox(paths, thr=2):
    import cv2
    bb = None
    for p in paths:
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        a = im[:, :, 3] if im.ndim == 3 and im.shape[2] == 4 else np.full(im.shape[:2], 255, np.uint8)
        if a.dtype != np.uint8:
            a = (a / 257).astype(np.uint8)
        ys, xs = np.nonzero(a > thr)
        if len(xs) == 0:
            continue
        b = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
    return bb


def render_folder(key, preview=False, samples=None, frames=None):
    """Build the scene for asset `key` ('name/variant'), render every label / yaw frame, crop if asked, write
    meta.json last. Returns the meta dict."""
    import cv2
    _bpy()
    _late()
    spec = ASSETS[key]
    name, variant = key.split('/')
    res = (W_PX // 2, H_PX // 2) if preview else (W_PX, H_PX)
    sk = res[0] / W_PX
    q = 0.6 if preview else 1.0
    t0 = time.time()
    sc = reset(res, samples or 64, transparent=True)
    S = spec['build'](q, preview)
    bpy.context.view_layer.update()
    outdir = os.path.join(PREVIEW if preview else OUT, name, variant)
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.endswith('.png') or f == 'meta.json':
            os.remove(os.path.join(outdir, f))
    if spec['mode'] == 'yaw':
        items = [('yaw', y) for y in spec['yaws']]
    else:
        items = [('label', lab) for lab in spec['labels']]
    idx = list(range(len(items)))
    if frames:
        idx = [i for i in idx if i in frames]
    border = None
    if spec['crop']:
        bb = None
        for yv in S.get('frame_yaws', [None]):
            if yv is not None:
                S['set_yaw'](yv)
                bpy.context.view_layer.update()
            b_ = objs_bbox_px(S['crop_objs'])
            bb = b_ if bb is None else [min(bb[0], b_[0]), min(bb[1], b_[1]), max(bb[2], b_[2]), max(bb[3], b_[3])]
        mg = int(70 * sk)
        border = [max(0, int(bb[0]) - mg), max(0, int(bb[1]) - mg), min(res[0], int(math.ceil(bb[2])) + mg),
                  min(res[1], int(math.ceil(bb[3])) + mg)]
        B.set_border(sc, border, res)
    print(f'[{key}] scene built in {time.time() - t0:.1f}s; {res[0]}x{res[1]}; border {border}; '
          f'{len(idx)} frames', flush=True)
    raws, times, fpf = [], {}, {}
    kinds = {}
    for i in idx:
        typ, val = items[i]
        if typ == 'yaw':
            S['set_yaw'](val)
            kind, spp = S['setup']('yaw')
            label = f'yaw{val:+.1f}'
        else:
            kind, spp = S['setup'](val)
            label = val
        kinds[label] = kind
        settings(sc, kind, S_PREVIEW if preview and kind != 'flat' else (samples if (samples and kind != 'flat') else spp))
        bpy.context.view_layer.update()
        p = os.path.join(outdir, f'_raw_{i:04d}.png')
        t1 = time.time()
        B.render_to(sc, p)
        times[label] = round(time.time() - t1, 1)
        print(f'  {key}/{label}: {times[label]}s ({kind}, {sc.cycles.samples} spp)', flush=True)
        raws.append((i, p))
        if typ == 'yaw':
            for fk, fp in S['feats']().items():
                fpf.setdefault(fk, []).append([float(v) for v in proj_px([fp])[0]])
    feats_static = {k: [float(v) for v in proj_px([p])[0]] for k, p in S.get('static_feats', {}).items()}
    meta_extra = dict(S.get('extra', {}))
    quad_w = meta_extra.pop('quad', None)
    post = S.get('post')
    if post:
        post({items[i][1] if items[i][0] == 'label' else i: p for i, p in raws})
    frame_xy = [0, 0]
    paths = [p for _, p in raws]
    if border is not None:
        bb = _alpha_bbox(paths, thr=2)
        ims = [cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in paths]
        bh, bw = ims[0].shape[:2]
        pad = int(round(CROP_PAD * sk))
        cx0, cy0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
        cx1, cy1 = min(bw, bb[2] + pad), min(bh, bb[3] + pad)
        edge = []
        for p, im in zip(paths, ims):
            a = im[:, :, 3]
            for side, sl, at in (('left', a[:, 0], border[0] == 0), ('top', a[0, :], border[1] == 0),
                                 ('right', a[:, -1], border[2] == res[0]), ('bottom', a[-1, :], border[3] == res[1])):
                if sl.max() > 2 and not at:
                    edge.append((os.path.basename(p), side))
        if edge:
            print(f'  WARNING {key}: alpha touches the render border: {edge[:6]}', flush=True)
        frame_xy = [border[0] + cx0, border[1] + cy0]
        for (i, p), im in zip(raws, ims):
            cv2.imwrite(os.path.join(outdir, f'{i:04d}.png'), im[cy0:cy1, cx0:cx1], [cv2.IMWRITE_PNG_COMPRESSION, 6])
            os.remove(p)
    else:
        for i, p in raws:
            os.replace(p, os.path.join(outdir, f'{i:04d}.png'))
    rel = lambda v: [round((v[0] - frame_xy[0]) / sk, 1) if False else round(v[0] - frame_xy[0], 1),  # noqa: E731
                     round(v[1] - frame_xy[1], 1)]
    features = {k: rel(v) for k, v in feats_static.items()}
    meta = dict(name=name, variant=variant, mode=spec['mode'], frames=len(items), fps_hint=30,
                loop=False, notes=spec['notes'], preview=bool(preview), device='CPU', threads=THREADS,
                render_seconds=times, builder=BUILDER, scale_to_final=round(1.0 / sk, 3))
    if spec['mode'] == 'yaw':
        meta['yaw_range'] = [spec['yaws'][0], spec['yaws'][-1]]
        meta['yaw_step'] = round(spec['yaws'][1] - spec['yaws'][0], 3)
        meta['axis'] = 'z (mast axis), + = counter-clockwise seen from above'
        meta['features_per_frame'] = {k: [rel(v) for v in seq] for k, seq in fpf.items()}
        if fpf:
            mid = len(next(iter(fpf.values()))) // 2
            for k, seq in meta['features_per_frame'].items():
                features.setdefault(k, seq[mid])
    else:
        meta['labels'] = list(spec['labels'])
        meta['pass_kind'] = kinds
    features['frame_xy'] = [float(frame_xy[0]), float(frame_xy[1])]
    meta['features'] = features
    meta['frame_xy'] = frame_xy
    if border is not None:
        im0 = cv2.imread(os.path.join(outdir, f'{idx[0]:04d}.png'), cv2.IMREAD_UNCHANGED)
        meta['crop_rect_frame'] = [frame_xy[0], frame_xy[1], frame_xy[0] + im0.shape[1], frame_xy[1] + im0.shape[0]]
    if quad_w is not None:
        qp = proj_px(quad_w)
        meta['screen_quad'] = [[round(x, 1), round(y, 1)] for x, y in qp]
        meta['screen_quad_order'] = 'TL, TR, BR, BL (frame px, picture corners on the curved glass)'
    if 'pivot' in features:
        meta['pivot'] = features['pivot']
    meta['camera'] = S.get('camera_meta', {})
    meta['samples'] = {k: (S_FLAT if v == 'flat' else (S_PREVIEW if preview else (samples or S.get('spp', {}).get(k, 0))))
                       for k, v in kinds.items()} if spec['mode'] != 'yaw' else (S_PREVIEW if preview else (samples or S.get('spp_yaw')))
    meta.update(meta_extra)
    sz = cv2.imread(os.path.join(outdir, f'{idx[0]:04d}.png'), cv2.IMREAD_UNCHANGED).shape
    meta['size'] = [int(sz[1]), int(sz[0])]
    if frames and len(idx) != len(items):
        meta['partial_frames'] = idx
        print(f'  partial render ({len(idx)}/{len(items)} frames): meta.json NOT written', flush=True)
        with open(os.path.join(outdir, 'meta_partial.json'), 'w') as fh:
            json.dump(meta, fh, indent=1)
        return meta
    out = H.write_meta(outdir, **meta)
    print(f'  -> {outdir}  size {meta["size"]}  total {time.time() - t0:.0f}s', flush=True)
    return out


def cam_meta(cam):
    cd = cam.data
    return dict(name=cam.name, lens_mm=cd.lens, sensor_mm=cd.sensor_height, sensor_fit='VERTICAL',
                location=[round(v, 4) for v in cam.location],
                rotation_deg=[round(math.degrees(v), 3) for v in cam.rotation_euler],
                fstop=cd.dof.aperture_fstop if cd.dof.use_dof else None,
                focus_m=round(cd.dof.focus_distance, 4) if cd.dof.use_dof else None)


# ============================================================================= A1 / A2 antenna, A3 roof plates

def _roof_scene(variant, q, with_antenna=True):
    world_sky(variant)
    sun_lamp(variant)
    env, rf = build_roof(variant, q)
    ant = None
    if with_antenna:
        ant = build_antenna(q)
    cam = cam_roof() if variant == 'day' else cam_sunset()
    return env, rf, ant, cam


def _antenna_asset(variant, q, preview):
    env, rf, (root, objs, feat_fn), cam = _roof_scene(variant, q)
    allo = all_objs()

    def set_yaw(y):
        root.rotation_euler = (0.0, 0.0, math.radians(YAW0 + y))

    def setup(label):
        bpy.context.scene.render.film_transparent = True
        set_roles(allo, {'env': 'cam_off', 'far': 'cam_off', 'clamp': 'cam_off', 'antenna': 'normal', 'mast': 'normal'})
        return 'beauty', 48 if variant == 'day' else 64
    yaws = ASSETS[f'antenna/{variant}_yaw']['yaws']
    return dict(set_yaw=set_yaw, setup=setup, feats=feat_fn, crop_objs=objs,
                frame_yaws=[yaws[0], yaws[len(yaws) // 2], yaws[-1]] + list(yaws[::5]),
                camera_meta=cam_meta(cam), spp_yaw=48 if variant == 'day' else 64,
                extra=dict(layer='over roof/%s bg, under roof/%s fg_clamp' % (variant, variant), yaw0_world_azimuth=YAW0))


@asset('antenna/day_yaw', 'yaw', yaws=[float(v) for v in np.linspace(-45, 15, 61)], crop=True,
       notes='Yagi on the GI mast, golden-hour sun back-left (el 14), RGBA over the sky; mast + coax turn with yaw')
def _a1(q, preview):
    return _antenna_asset('day', q, preview)


@asset('antenna/sunset_yaw', 'yaw', yaws=[float(v) for v in np.linspace(-3, 3, 7)], crop=True,
       notes='the antenna backlit by the low sun (el 3) at sunset: dark silhouette, hot rim lines; RGBA')
def _a2(q, preview):
    return _antenna_asset('sunset', q, preview)


def _roof_plate(variant, q, preview):
    env, rf, (root, objs, feat_fn), cam = _roof_scene(variant, q)
    root.rotation_euler = (0, 0, math.radians(YAW0))
    allo = all_objs()

    def setup(label):
        sc = bpy.context.scene
        if label == 'bg':
            sc.render.film_transparent = False
            set_roles(allo, {'antenna': 'cam_off', 'mast': 'cam_off'})
            return 'beauty', 128
        sc.render.film_transparent = True
        set_roles(allo, {'env': 'cam_off', 'far': 'cam_off', 'antenna': 'cam_off', 'mast': 'holdout', 'clamp': 'normal'})
        return 'beauty', 96
    sf = {'mast_xy': rf['mast_coping'], 'strap_mark': rf['strap_mark'], 'bolt_l': rf['bolt_l'], 'bolt_r': rf['bolt_r']}
    if variant == 'sunset':
        sv = sun_vec(SUN['sunset']['az'], SUN['sunset']['el'])
        sf['sun_xy'] = tuple(np.asarray(cam.location) + 300.0 * np.asarray(sv))
    return dict(setup=setup, static_feats=sf, camera_meta=cam_meta(cam), spp={'bg': 128, 'fg_clamp': 96},
                extra=dict(layers='bg (opaque) -> antenna/%s_yaw -> fg_clamp (RGBA)' % variant))


@asset('roof/day', 'static', labels=['bg', 'fg_clamp'],
       notes='rooftop plate, golden hour: parapet, clamps, tank, clothesline, hazed rooftops; pipe NOT in the plate')
def _a3d(q, preview):
    return _roof_plate('day', q, preview)


@asset('roof/sunset', 'static', labels=['bg', 'fg_clamp'],
       notes='rooftop plate at sunset (sun disc el 3 right of the mast); pipe NOT in the plate')
def _a3s(q, preview):
    return _roof_plate('sunset', q, preview)


# ============================================================================= layout check (no render)

TARGETS = {
    'crt/macro': {'screen': (110, 640, 970, 1330)},
    'antenna/day_yaw': {'dipole_box_y': (280, 1000), 'tip_margin': 60},
    'phone/desk': {'screen': (220, 520, 860, 1500)},
}


def targets_report():
    _bpy()
    _late()
    rep = {}
    for variant in ('day', 'sunset'):
        reset((W_PX, H_PX), 16)
        env, rf, (root, objs, ff), cam = _roof_scene(variant, 0.5)
        rows = []
        yaws = (-45, -30, -15, 0, 15) if variant == 'day' else (-3, 0, 3)
        union = None
        for y in yaws:
            root.rotation_euler = (0, 0, math.radians(YAW0 + y))
            bpy.context.view_layer.update()
            bb = objs_bbox_px(objs)
            f = {k: [round(v, 0) for v in proj_px([p])[0]] for k, p in ff().items()}
            union = bb if union is None else [min(union[0], bb[0]), min(union[1], bb[1]), max(union[2], bb[2]), max(union[3], bb[3])]
            rows.append((y, [round(v) for v in bb], f['dipole_box'], f['rod_tip'], f['mast_top']))
        cop = [round(v) for v in proj_px([rf['mast_coping']])[0]]
        para = objs_bbox_px([o for o in env if o.name in ('parapet',)])
        print(f'== CAM_{variant.upper()}  loc {CAMS[variant if variant == "sunset" else "roof"]["loc"]}')
        for r in rows:
            print(f'   yaw {r[0]:+4d}: bbox {r[1]}  dipole_box {r[2]}  rod_tip {r[3]}  mast_top {r[4]}')
        print(f'   union bbox {[round(v) for v in union]} (frame 1080x1920; tips need >= 60 px margin)')
        print(f'   mast at the coping {cop}; parapet bbox {[round(v) for v in para]}')
        if variant == 'sunset':
            sv = sun_vec(SUN['sunset']['az'], SUN['sunset']['el'])
            print(f'   sun disc at {[round(v) for v in proj_px([tuple(np.asarray(cam.location) + 300 * np.asarray(sv))])[0]]}')
        rep[variant] = dict(union=union, rows=rows)
    for key in ('clamp/macro', 'crt/macro', 'crt/room', 'phone/desk'):
        if key in LAYOUT:
            print(LAYOUT[key]())
    return rep


LAYOUT = {}


# ============================================================================= sheets / archive / CLI

def _read_rgba(p):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im.dtype == np.uint16:
        im = (im / 257).astype(np.uint8)
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    return im


def _over(dst, src, x, y):
    """Straight-alpha src (BGRA uint8) over dst (BGR float 0-1) at x, y (sRGB-space blend, good enough for sheets)."""
    h, w = src.shape[:2]
    H_, W_ = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W_, x + w), min(H_, y + h)
    if x1 <= x0 or y1 <= y0:
        return dst
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) / 255.0
    a = s[:, :, 3:4]
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + s[:, :, :3] * a
    return dst


def composites(root, tag):
    """Layered checks: roof plate + antenna + fg clamp; clamp bg + pipe + fg; CRT room with a test picture via
    the stmap; phone with a test card. Written to SHEETS/<tag>_*.jpg."""
    import cv2
    os.makedirs(SHEETS, exist_ok=True)
    outs = []

    def load(name, variant):
        d = os.path.join(root, name, variant)
        mp = os.path.join(d, 'meta.json')
        if not os.path.exists(mp):
            mp = os.path.join(d, 'meta_partial.json')
            if not os.path.exists(mp):
                return None, None
        meta = json.load(open(mp))
        files = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
        return meta, [os.path.join(d, f) for f in files]
    for v in ('day', 'sunset'):
        mb, fb = load('roof', v)
        ma, fa = load('antenna', v + '_yaw')
        if not mb or not fb:
            continue
        bg = _read_rgba(fb[0])[:, :, :3].astype(np.float32) / 255.0
        cells = []
        picks = [0, len(fa) // 2, len(fa) - 1] if fa else [None]
        for i in picks:
            im = bg.copy()
            if fa and i is not None:
                fx, fy = ma['frame_xy']
                k = bg.shape[1] / 1080.0 if not ma.get('preview') or mb.get('preview') else 1.0
                im = _over(im, _read_rgba(fa[i]), int(fx), int(fy))
            if len(fb) > 1:
                im = _over(im, _read_rgba(fb[1]), 0, 0)
            cells.append(im)
        sheet = np.concatenate(cells, 1)
        p = os.path.join(SHEETS, f'{tag}_roof_{v}.jpg')
        cv2.imwrite(p, np.clip(sheet * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
        outs.append(p)
    mb, fb = load('clamp', 'macro')
    mp_, fp_ = load('clamp', 'pipe_yaw')
    if mb and fb:
        bg = _read_rgba(fb[0])[:, :, :3].astype(np.float32) / 255.0
        cells = []
        for i in ([0, len(fp_) // 2, len(fp_) - 1] if fp_ else [None]):
            im = bg.copy()
            if fp_ and i is not None:
                im = _over(im, _read_rgba(fp_[i]), int(mp_['frame_xy'][0]), int(mp_['frame_xy'][1]))
            if len(fb) > 1:
                im = _over(im, _read_rgba(fb[1]), 0, 0)
            cells.append(im)
        p = os.path.join(SHEETS, f'{tag}_clamp.jpg')
        cv2.imwrite(p, np.clip(np.concatenate(cells, 1) * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
        outs.append(p)
    for nm, vv, labs in (('crt', 'macro', 4), ('crt', 'room', 4), ('phone', 'desk', 3)):
        m, f = load(nm, vv)
        if not m or not f:
            continue
        ims = [_read_rgba(x) for x in f]
        base = ims[0][:, :, :3].astype(np.float32) / 255.0
        st = cv2.imread(f[-1], cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0
        u, v_, a = st[:, :, 2], st[:, :, 1], st[:, :, 3]
        # test picture: warm snow-free card with a grid, warped through the stmap
        Hc, Wc = 810, 1080
        yy, xx = np.mgrid[0:Hc, 0:Wc]
        card = np.dstack([0.25 + 0.5 * (yy / Hc), 0.12 + 0.2 * (xx / Wc), 0.08 + 0.1 * (yy / Hc)])
        card[(xx % 90) < 4] = 0.9
        card[(yy % 90) < 4] = 0.9
        mx = np.clip(u * (Wc - 1), 0, Wc - 1).astype(np.float32)
        my = np.clip((1 - v_) * (Hc - 1), 0, Hc - 1).astype(np.float32)
        pic = cv2.remap(card.astype(np.float32), mx, my, cv2.INTER_LINEAR)
        comp = base * (1 - a[..., None]) + pic * a[..., None]
        if len(ims) == 4:
            r = ims[1].astype(np.float32) / 255.0
            comp = np.clip(comp + r[:, :, :3] * r[:, :, 3:4], 0, 1)
        sp = ims[-2][:, :, :3].astype(np.float32) / 255.0
        comp = np.clip(comp + sp * 0.35, 0, 1)
        if m.get('screen_quad'):
            k = base.shape[1] / 1080.0 if m.get('preview') else 1.0
            pts = np.array(m['screen_quad'], np.float32)
            cv2.polylines(comp, [pts.astype(np.int32)], True, (0, 1, 0), 1)
        cells = [base, comp] + [im[:, :, :3].astype(np.float32) / 255.0 for im in ims[1:-1]]
        p = os.path.join(SHEETS, f'{tag}_{nm}_{vv}.jpg')
        cv2.imwrite(p, np.clip(np.concatenate(cells, 1) * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
        outs.append(p)
    for p in outs:
        print('  sheet', p)
    return outs


def yaw_sheet(root, tag, key, n=6):
    import cv2
    name, variant = key.split('/')
    d = os.path.join(root, name, variant)
    if not os.path.isdir(d):
        return None
    files = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
    if not files:
        return None
    pick = [files[int(round(i * (len(files) - 1) / max(n - 1, 1)))] for i in range(min(n, len(files)))]
    cells = []
    for f in pick:
        im = _read_rgba(os.path.join(d, f)).astype(np.float32) / 255.0
        bgc = np.zeros_like(im[:, :, :3]) + np.array([0.35, 0.55, 0.75])[None, None, ::-1] * 0.8
        cells.append(bgc * (1 - im[:, :, 3:4]) + im[:, :, :3] * im[:, :, 3:4])
    p = os.path.join(SHEETS, f'{tag}_{name}_{variant}.jpg')
    os.makedirs(SHEETS, exist_ok=True)
    cv2.imwrite(p, np.clip(np.concatenate(cells, 1) * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print('  sheet', p)
    return p


def archive():
    """Optimised copies into brand_reels/assets/thoda_left_bas/assets3d (git, < 60 MB): opaque 8-bit plates as
    high-quality JPG (+ the PNG name recorded in archive.json), RGBA PNGs re-compressed, 16-bit STMaps kept as PNG."""
    import cv2
    os.makedirs(ARCHIVE, exist_ok=True)
    index = {}
    for name in sorted(os.listdir(OUT)):
        for variant in sorted(os.listdir(os.path.join(OUT, name))):
            d = os.path.join(OUT, name, variant)
            if not os.path.exists(os.path.join(d, 'meta.json')):
                print('  skip (no meta.json):', d)
                continue
            od = os.path.join(ARCHIVE, name, variant)
            if os.path.isdir(od):
                shutil.rmtree(od)
            os.makedirs(od)
            for f in sorted(os.listdir(d)):
                src = os.path.join(d, f)
                if f == 'meta.json':
                    shutil.copy2(src, od)
                    continue
                if not f.endswith('.png'):
                    continue
                im = cv2.imread(src, cv2.IMREAD_UNCHANGED)
                if im.dtype == np.uint8 and im.shape[2] == 4 and im[:, :, 3].min() == 255:
                    cv2.imwrite(os.path.join(od, f[:-4] + '.jpg'), im[:, :, :3], [cv2.IMWRITE_JPEG_QUALITY, 93])
                    index[f'{name}/{variant}/{f}'] = 'jpg'
                else:
                    cv2.imwrite(os.path.join(od, f), im, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                    index[f'{name}/{variant}/{f}'] = 'png'
    with open(os.path.join(ARCHIVE, 'archive.json'), 'w') as fh:
        json.dump(dict(note='restore with: python3 pipeline/jawad_reels/assets3d_thoda_left_bas.py restore', files=index), fh,
                  indent=1)
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(ARCHIVE) for f in fs)
    print(f'  archive {ARCHIVE}: {tot / 1e6:.1f} MB')
    return tot


def restore():
    import cv2
    idx = json.load(open(os.path.join(ARCHIVE, 'archive.json')))['files']
    for rel, kind in idx.items():
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        src = os.path.join(ARCHIVE, rel if kind == 'png' else rel[:-4] + '.jpg')
        if kind == 'jpg':
            im = cv2.imread(src, cv2.IMREAD_COLOR)
            im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
            cv2.imwrite(dst, im)
        else:
            shutil.copy2(src, dst)
    for dp, _, fs in os.walk(ARCHIVE):
        for f in fs:
            if f == 'meta.json':
                rel = os.path.relpath(os.path.join(dp, f), ARCHIVE)
                shutil.copy2(os.path.join(dp, f), os.path.join(OUT, rel))
    print('  restored into', OUT)


def selftest():
    ok = True
    for key in ORDER:
        name, variant = key.split('/')
        d = os.path.join(OUT, name, variant)
        mp = os.path.join(d, 'meta.json')
        if not os.path.exists(mp):
            print(f'  MISSING {key}')
            ok = False
            continue
        meta = json.load(open(mp))
        n = len([f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit()])
        good = n == meta['frames']
        print(f'  {"ok " if good else "BAD"} {key}: {n}/{meta["frames"]} frames, size {meta["size"]}, preview={meta["preview"]}')
        ok &= good
    sys.path.insert(0, HERE)
    try:
        import sprites3d as S3
        a = S3.Asset3D('antenna', 'day_yaw', root=OUT)
        fr = a.at_yaw(-14.0)
        print('  S3 load antenna/day_yaw at_yaw(-14):', fr.shape, a.mode, a.yaw_range)
    except Exception as e:  # noqa: BLE001
        print('  S3 load failed:', e)
        ok = False
    print('selftest', 'PASS' if ok else 'FAIL')
    return ok


def main(argv):
    preview = '--preview' in argv
    samples = None
    frames = None
    names = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--samples':
            samples = int(argv[i + 1])
            i += 2
            continue
        if a == '--frames':
            frames = [int(v) for v in argv[i + 1].split(',')]
            i += 2
            continue
        if not a.startswith('--'):
            names.append(a)
        i += 1
    if not names:
        print(__doc__)
        return
    cmd = names[0]
    if cmd == 'targets':
        targets_report()
        return
    if cmd in ('sheet', 'previewsheet'):
        root = OUT if cmd == 'sheet' else PREVIEW
        tag = 'finals' if cmd == 'sheet' else 'preview'
        composites(root, tag)
        for key in ('antenna/day_yaw', 'antenna/sunset_yaw', 'clamp/pipe_yaw'):
            yaw_sheet(root, tag, key)
        return
    if cmd == 'archive':
        archive()
        return
    if cmd == 'restore':
        restore()
        return
    if cmd == 'selftest':
        sys.exit(0 if selftest() else 1)
    keys = ORDER if cmd == 'all' else names
    for k in keys:
        if k not in ASSETS:
            print('unknown asset', k, 'known:', list(ASSETS))
            continue
        render_folder(k, preview=preview, samples=samples, frames=frames)


if __name__ == '__main__':
    main(sys.argv[1:])
