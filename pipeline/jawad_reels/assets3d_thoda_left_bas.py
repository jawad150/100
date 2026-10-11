"""assets3d_thoda_left_bas.py - photoreal Blender props for Bijli series #2 "Thoda Left... Bas Bas!" (@jawad_mp4).

Builds the asset folders of SHOTS §a (brand_reels/design/reels/thoda_left_bas/SHOTS.md) with bpy 5.2 / Cycles
(OpenImageDenoise with albedo + normal guides, fixed seed, view transform Standard, look None) as RGBA 8-bit
straight-alpha sRGB PNGs in the shared 3D asset spec.

    Device: assets3d_gpu.set_device (called from reset()). CPU by default (the shared Linux box: tests / previews
    only, threads 2, adaptive 0.02); FOSTER_GPU=1 picks OPTIX > CUDA > HIP > METAL > ONEAPI (finals: RTX 4060 OptiX,
    8 GB) and switches every pass to its GPU sample count (gpu_spp in the @asset table, 256-512, adaptive 0.01, OIDN
    on the GPU). The device lands in the log line "[assets3d] Cycles device: ..." and in meta.json "device". Never
    mix CPU and GPU frames in one folder. SKIP_EXISTING=1 resumes an interrupted folder (raw frames are kept until
    the folder is complete; the crop + meta.json happen at the end). Paths are built with os.path (Windows-safe). STMaps are 16-bit RGBA PNGs
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

    --preview  16 spp, half resolution, into RWS/out/preview3d/ (finals untouched). env TLB_THREADS (default 2),
    TLB_OUT (default RWS/assets3d), FOSTER_GPU=1 (GPU finals), FOSTER_GPU_TYPE=CUDA, SKIP_EXISTING=1.
    On the shared Linux box every render goes through pipeline/jawad_reels/tools/heavy.sh; on the GPU PC run the
    python lines of brand_reels/design/reels/thoda_left_bas/RENDER_JOBS.md directly.

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

DEVICE = 'CPU'


def is_gpu():
    """True when assets3d_gpu picked a GPU backend for this process (FOSTER_GPU=1 on the RTX PC)."""
    return not DEVICE.startswith('CPU')


def reset(res, samples, transparent=True):
    """Empty Cycles scene (B.reset -> H.reset: factory settings, OIDN albedo + normal, RGBA 8-bit PNG) with this
    reel's settings. Device: assets3d_gpu.set_device -> CPU unless FOSTER_GPU=1 finds a GPU (OPTIX > CUDA > ...);
    on the GPU the CPU only syncs the scene (threads AUTO) and OIDN runs on the GPU."""
    global DEVICE
    import assets3d_gpu
    sc = B.reset(res, samples, transparent)
    DEVICE = assets3d_gpu.set_device(bpy, sc)      # idempotent (H.reset already set it); returns the device name
    if is_gpu():
        sc.render.threads_mode = 'AUTO'
        if hasattr(sc.cycles, 'denoising_use_gpu'):
            sc.cycles.denoising_use_gpu = True
    else:
        sc.render.threads_mode = 'FIXED'
        sc.render.threads = THREADS
    sc.cycles.seed = 7
    sc.cycles.use_animated_seed = False
    sc.cycles.adaptive_threshold = 0.01 if is_gpu() else 0.02
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    sc.cycles.denoising_prefilter = 'ACCURATE'
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
    spg_r = g.m('MULTIPLY_ADD', cr, 0.07, 0.40)
    spg_c = g.mix(cr, C('#8C8C87'), C('#9A9A94'))
    dull = g.mr(g.noise(co, 5.0, 3.0, 0.6), 0.35, 0.7, 0.0, 1.0)
    spg_c = g.mix(g.m('MULTIPLY', dull, 0.6), spg_c, C('#76746E'))
    wrust = g.mr(g.noise(co, 22.0, 4.0, 0.65), 0.55, 0.72, 0.0, 0.7, smooth=True)     # white rust (zinc oxide) film
    spg_c = g.mix(wrust, spg_c, C('#B4B0A6'))
    spg_r = g.m('ADD', spg_r, g.m('MULTIPLY', wrust, 0.35))
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
    metal = g.m('MAXIMUM', g.m('SUBTRACT', g.m('SUBTRACT', 1.0, rmask), g.m('MULTIPLY', wrust, 0.6)), 0.0)
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
        paint = g.mix(g.mr(g.noise(co, 300.0, 2.0, 0.6), 0.3, 0.8, 0.0, 1.0), C('#CBC2AC'), C('#A99E86'))
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
    rust_c = g.mix(g.mr(big, 0.62, 0.8, 0.0, 0.6), rust_c, C('#8E5128'))
    rust_c = g.mix(g.mr(g.noise(co, 70.0, 4.0, 0.7), 0.5, 0.75, 0.0, 0.8), rust_c, C('#2E1A10'))
    pn = g.noise(co, 55.0, 5.0, 0.7, dist=0.4)
    paint = g.mr(pn, 0.56, 0.585, 0.0, 1.0)
    paint_c = g.mix(g.mr(g.noise(co, 140.0, 2.0, 0.6), 0.3, 0.7, 0.0, 1.0), C('#5F6B5C'), C('#6E786A'))
    base = g.mix(paint, rust_c, paint_c)
    rough = g.m('ADD', g.m('MULTIPLY', paint, -0.3), 0.9)
    h = g.m('ADD', g.m('MULTIPLY', paint, 0.35), g.m('MULTIPLY', rn, 0.65))
    if mark is not None:
        c, hs = mark
        jit = g.n('ShaderNodeVectorMath', operation='ADD')
        g.put(jit.inputs[0], co)
        g.put(jit.inputs[1], vsc(g, g.m('SUBTRACT', g.noise(co, 260.0, 3.0, 0.7), 0.5), 0.004))
        mk = box_falloff(g, jit.outputs[0], c, hs, 0.0008)
        chip = g.mr(g.noise(co, 700.0, 3.0, 0.7), 0.60, 0.64, 1.0, 0.0)
        mk = g.m('MULTIPLY', mk, chip)
        base = g.mix(mk, base, g.mix(g.mr(g.noise(co, 400.0, 3.0, 0.6), 0.3, 0.8, 0.0, 1.0), C('#CFC6B0'), C('#A89C84')))
        rough = g.m('ADD', g.m('MULTIPLY', mk, -0.3), rough)
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


def asset(key, mode, labels=None, yaws=None, crop=False, notes='', gpu_spp=None):
    """Register an asset folder. The builder's setup(label) returns (kind, CPU spp); gpu_spp (int, or a dict
    label -> spp; 'yaw' for yaw folders) replaces that count when the GPU renders the finals (FOSTER_GPU=1)."""
    def deco(fn):
        ASSETS[key] = dict(key=key, mode=mode, labels=labels, yaws=yaws, crop=crop, notes=notes, build=fn,
                           gpu_spp=gpu_spp)
        return fn
    return deco


def final_spp(key, label, cpu_spp):
    """Final sample count for one pass: the GPU table on a GPU, the builder's CPU count otherwise."""
    g = ASSETS[key].get('gpu_spp')
    if not is_gpu() or g is None:
        return cpu_spp
    if isinstance(g, dict):
        return g.get(label, g.get('*', cpu_spp))
    return g


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
    skip = os.environ.get('SKIP_EXISTING') == '1' and not preview and not frames
    if os.path.exists(os.path.join(outdir, 'meta.json')):
        os.remove(os.path.join(outdir, 'meta.json'))          # meta.json is written last, never stale
    for f in os.listdir(outdir):
        if f.endswith('.png') and not (skip and f.startswith('_raw_')):
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
          f'{len(idx)} frames; device {DEVICE}' + ('' if is_gpu() else f' x{THREADS} threads'), flush=True)
    raws, times, fpf = [], {}, {}
    kinds, spp_used = {}, {}
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
        spp = final_spp(key, 'yaw' if typ == 'yaw' else label, spp)
        spp_used[label] = S_FLAT if kind == 'flat' else (S_PREVIEW if preview else (samples or spp))
        settings(sc, kind, S_PREVIEW if preview and kind != 'flat' else (samples if (samples and kind != 'flat') else spp))
        bpy.context.view_layer.update()
        p = os.path.join(outdir, f'_raw_{i:04d}.png')
        if skip and os.path.exists(p):
            print(f'  {key}/{label}: kept (SKIP_EXISTING)', flush=True)
        else:
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
                loop=False, notes=spec['notes'], preview=bool(preview), device=DEVICE,
                threads=None if is_gpu() else THREADS,
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
    meta['samples'] = dict(spp_used) if spec['mode'] != 'yaw' else (next(iter(spp_used.values())) if spp_used else None)
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


@asset('antenna/day_yaw', 'yaw', yaws=[float(v) for v in np.linspace(-45, 15, 61)], crop=True, gpu_spp={'yaw': 256},
       notes='Yagi on the GI mast, golden-hour sun back-left (el 14), RGBA over the sky; mast + coax turn with yaw')
def _a1(q, preview):
    return _antenna_asset('day', q, preview)


@asset('antenna/sunset_yaw', 'yaw', yaws=[float(v) for v in np.linspace(-3, 3, 7)], crop=True, gpu_spp={'yaw': 384},
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


@asset('roof/day', 'static', labels=['bg', 'fg_clamp'], gpu_spp={'bg': 512, 'fg_clamp': 256},
       notes='rooftop plate, golden hour: parapet, clamps, tank, clothesline, hazed rooftops; pipe NOT in the plate')
def _a3d(q, preview):
    return _roof_plate('day', q, preview)


@asset('roof/sunset', 'static', labels=['bg', 'fg_clamp'], gpu_spp={'bg': 512, 'fg_clamp': 256},
       notes='rooftop plate at sunset (sun disc el 3 right of the mast); pipe NOT in the plate')
def _a3s(q, preview):
    return _roof_plate('sunset', q, preview)


# ============================================================================= A4 clamp macro

SUN['clamp'] = dict(az=203.0, el=14.0, color='#FFD7A0', strength=4.2, angle=0.6,
                    zenith='#6F8CB0', mid='#C9C3B4', horizon='#F3CF9C', glow='#FFD9A0', ground='#6A5E52',
                    glow_k=(1.4, 0.55), sky_k=0.9, disc=0.0)
CLAMP_YAWS = [float(v) for v in np.linspace(-6.0, 2.0, 17)]


def cam_clamp(feats):
    """CAM_CLAMP: 100 mm at 0.5 m from the strap mark, 10 deg down, the frame centre a little right of the mark so the
    right ear + bolt read; f/2.8 focused on the strap mark (the pipe mark sits at the same depth at yaw 0)."""
    mk = np.asarray(feats['strap_mark'], float)
    a = math.radians(MARK_ANG)
    d = np.array([math.cos(a), math.sin(a), 0.0])           # outward from the pipe axis through the mark
    right = np.cross(-d, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    dist, down = 0.50, math.radians(10.0)
    loc = mk + d * dist * math.cos(down) + np.array([0, 0, dist * math.sin(down)]) + right * 0.012
    tgt = mk + right * 0.024 + np.array([0, 0, 0.012])
    return camera('CAM_CLAMP', tuple(loc), tuple(tgt), 100.0, fstop=2.8, focus=tuple(mk))


def _clamp_scene(q):
    world_sky('clamp')
    sun_lamp('clamp')
    objs = []
    clamps = [(MAST[0], z, 0.0) for z in CLAMP_Z]
    wall_m = mat_plaster('plaster_wall_macro', top=PARA_H, clamps=clamps, chip=None)
    cop_m = mat_plaster('plaster_coping_macro', top=TOP + 0.02, clamps=(), chip=None, base='#948A7E')
    o = B.cube('parapet', (-1.5, 0.0, 0.0), (1.5, PARA_T, PARA_H), wall_m, role='env')
    bevel_mod(o, 0.006, 2)
    objs.append(o)
    o = B.cube('coping', (-1.5, -0.03, PARA_H), (1.5, PARA_T + 0.03, TOP), cop_m, role='env')
    bevel_mod(o, 0.008, 3)
    objs.append(o)
    objs.append(B.cube('floor', (-1.5, -2.0, -0.15), (1.5, 0.0, 0.0), mat_concrete(), role='env'))
    # warm bounce from the sunlit roof floor below (soft card, not seen by the camera)
    B.light('BOUNCE_floor', 'AREA', (MAST[0], -0.45, 0.25), 6.0, '#FFC890', target=(MAST[0], -0.05, 0.72),
            size=(0.8, 0.5), group='bounce')
    steel = mat_rusty_steel('rusty_bolts', 0.85)
    feats = {}
    for k, z in enumerate(CLAMP_Z):
        parts, f = strap_clamp(f'strap{k}', z, strap_material(z, k == 0), steel, mark=(k == 0))
        for p_ in parts:
            p_['role'] = 'clamp'
        objs += parts
        if k == 0:
            feats.update(f)
    # the mast alone (same material + paint mark as the antenna asset), rotating about its axis
    root = empty('PIPE_ROOT', (MAST[0], MAST[1], 0.0))
    pipe_m = mat_gi_pipe('gi_pipe_mast', contacts=CLAMP_Z + (BOOM_Z + 0.04, BOOM_Z - 0.04), top=MAST_TOP,
                         mark=pipe_mark())
    seg = max(32, int(128 * q))
    mast = lathe_obj('mast', [(PIPE_R, 0.0), (PIPE_R, 1.6)], pipe_m, seg=seg, sharp=50)
    mast.parent = root
    mast['role'] = 'mast'
    # coax down the wall side of the mast with a tape wrap just under the upper clamp (turns with the pipe)
    a = math.radians(COAX_ANG)
    rr = PIPE_R + 0.0036
    cx_ = tube('coax', [(rr * math.cos(a), rr * math.sin(a), z_) for z_ in (1.6, 1.2, 0.9, 0.5, 0.1)], 0.0035,
               mat_coax(), res=3, order=2, parent=root)
    cx_['role'] = 'mast'
    objs += [mast, cx_]
    return objs, feats, root


def _clamp_asset(q, preview, which):
    objs, feats, root = _clamp_scene(q)
    cam = cam_clamp(feats)
    allo = all_objs()

    def set_yaw(y):
        root.rotation_euler = (0.0, 0.0, math.radians(YAW0 + y))

    set_yaw(0.0)

    def feat_pipe():
        bpy.context.view_layer.update()
        pm = pipe_mark()
        ang = math.radians(pm[0])
        zc = (pm[1] + pm[2]) / 2
        p = root.matrix_world @ Vector(((PIPE_R + 0.0002) * math.cos(ang), (PIPE_R + 0.0002) * math.sin(ang), zc))
        return {'pipe_mark': tuple(p), 'pipe_axis': tuple(root.matrix_world @ Vector((0, 0, CLAMP_Z[0])))}

    if which == 'macro':
        def setup(label):
            sc = bpy.context.scene
            set_yaw(0.0)
            if label == 'bg':
                sc.render.film_transparent = False
                set_roles(allo, {'mast': 'cam_off'})
                return 'beauty', 128
            sc.render.film_transparent = True
            set_roles(allo, {'env': 'cam_off', 'mast': 'holdout', 'clamp': 'normal'})
            return 'beauty', 128
        sf = dict(strap_mark=feats['strap_mark'], bolt_l=feats['bolt_l'], bolt_r=feats['bolt_r'])
        sf.update(feat_pipe())
        return dict(setup=setup, static_feats=sf, camera_meta=cam_meta(cam),
                    extra=dict(layers='bg (opaque, no pipe) -> clamp/pipe_yaw at_yaw(yaw) at its frame_xy -> fg (RGBA)'))

    def setup(label):
        bpy.context.scene.render.film_transparent = True
        set_roles(allo, {'env': 'cam_off', 'clamp': 'cam_off', 'mast': 'normal'})
        return 'beauty', 96
    return dict(set_yaw=set_yaw, setup=setup, feats=feat_pipe, crop_objs=[o for o in allo if o.get('role') == 'mast'],
                frame_yaws=[CLAMP_YAWS[0], CLAMP_YAWS[-1]], camera_meta=cam_meta(cam),
                extra=dict(layer='over clamp/macro bg, under clamp/macro fg', yaw0_world_azimuth=YAW0,
                           mark_note='pipe mark aligned with the strap mark at yaw 0 (S4 f288)'))


@asset('clamp/macro', 'static', labels=['bg', 'fg'], gpu_spp={'bg': 512, 'fg': 384},
       notes='upper strap clamp macro, raking sun: bg = plaster + clamp (pipe invisible, its shadow kept); '
             'fg = strap + bolts only (pipe holdout)')
def _a4m(q, preview):
    return _clamp_asset(q, preview, 'macro')


@asset('clamp/pipe_yaw', 'yaw', yaws=CLAMP_YAWS, crop=True, gpu_spp={'yaw': 256},
       notes='the GI pipe with its hand-painted mark turning in the clamp, 0.5 deg steps; RGBA strip, clamp shadows on it')
def _a4p(q, preview):
    return _clamp_asset(q, preview, 'pipe')


# ============================================================================= A5 / A6 CRT TV in the 90s room

def loft2(name, loops, mat, k=6, cap0=False, cap1=False, sharp=36.0, role='prop', parent=None, smooth=True):
    """Like loft() but every loop carries its own centre: loops = [(cx, cz, hx, hz, r, y), ...] (rounded rects in
    the XZ plane, depth along world y). Bezels, frames and tapered backs whose opening is off-centre."""
    V, F = [], []
    n = 4 * k
    for (cx, cz, hx, hz, r, y) in loops:
        for (a, b) in rrect_loop(hx, hz, r, k):
            V.append((cx + a, y, cz + b))
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
    o = _mesh(name, np.array(V), F, mat, smooth=smooth, role=role, parent=parent)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    if sharp is not None:
        o.data.set_sharp_from_angle(angle=math.radians(sharp))
    return o


def rrect_mask(g, u, v, w, h, r, soft=0.0006):
    """1 inside a rounded rectangle w x h (metres, corner r) centred on (0, 0) of the (u, v) metre coordinates."""
    dx = g.m('SUBTRACT', g.m('ABSOLUTE', u), w / 2 - r)
    dy = g.m('SUBTRACT', g.m('ABSOLUTE', v), h / 2 - r)
    ox = g.m('MAXIMUM', dx, 0.0)
    oy = g.m('MAXIMUM', dy, 0.0)
    outer = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', ox, ox), g.m('MULTIPLY', oy, oy)))
    inner = g.m('MINIMUM', g.m('MAXIMUM', dx, dy), 0.0)
    d = g.m('SUBTRACT', g.m('ADD', outer, inner), r)
    return g.mr(d, soft, -soft, 0.0, 1.0)


def _shader_mat(name):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for nn in list(nt.nodes):
        nt.nodes.remove(nn)
    return m, B.G(nt)


def mat_screen_uv(name, w, h, r, axes='xz', holes=()):
    """STMap material for a screen object whose object origin is the picture centre: emission (u, v, 0) with
    u = x / w + 0.5, v = (z or y) / h + 0.5 (linear, written with the Raw view), holdout outside the rounded picture
    (and inside `holes` = [(cx, cy, radius)], e.g. a punch-hole camera)."""
    m, g = _shader_mat(name)
    x, y, z = g.xyz(g.co('Object'))
    vv = z if axes == 'xz' else y
    u = g.m('ADD', g.m('DIVIDE', x, w), 0.5)
    v = g.m('ADD', g.m('DIVIDE', vv, h), 0.5)
    mask = rrect_mask(g, x, vv, w, h, r, soft=0.00025)
    for (hx_, hy_, hr) in holes:
        dx = g.m('SUBTRACT', x, hx_)
        dy = g.m('SUBTRACT', vv, hy_)
        dd = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy)))
        mask = g.m('MULTIPLY', mask, g.mr(dd, hr - 0.0002, hr + 0.0002, 0.0, 1.0))
    e = g.n('ShaderNodeEmission')
    g.put(e.inputs['Color'], g.comb(u, v, 0.0))
    e.inputs['Strength'].default_value = 1.0
    hd = g.n('ShaderNodeHoldout')
    mx = g.n('ShaderNodeMixShader')
    g.put(mx.inputs[0], mask)
    g.nt.links.new(hd.outputs[0], mx.inputs[1])
    g.nt.links.new(e.outputs[0], mx.inputs[2])
    out = g.n('ShaderNodeOutputMaterial')
    g.nt.links.new(mx.outputs[0], out.inputs[0])
    m.cycles.emission_sampling = 'NONE'
    return m


def mat_screen_spill(name, w, h, r, axes='xz', color='#EFE6D6', strength=2.0, base='#0B0D0C'):
    """'spill' pass screen: a uniform IVORY emitter over the picture (the screen lighting the set), dark glass around."""
    m, b, g = B.principled(name, base, rough=0.05, spec=0.5, coat=1.0, coat_rough=0.03)
    x, y, z = g.xyz(g.co('Object'))
    mask = rrect_mask(g, x, z if axes == 'xz' else y, w, h, r)
    g.put(b.inputs['Emission Color'], rgb(g, color))
    g.put(b.inputs['Emission Strength'], g.m('MULTIPLY', mask, strength))
    m.cycles.emission_sampling = 'FRONT'
    return m


def cam_holdout_wrap(exclude):
    """Make every material except `exclude` a holdout for CAMERA rays only (still seen by reflections, still lit
    and casting light): the 'refl' pass keeps only what the glass reflects. Returns an undo function."""
    undo = []
    for m in bpy.data.materials:
        if m in exclude or not m.use_nodes:
            continue
        nt = m.node_tree
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
        if out is None or not out.inputs['Surface'].links:
            continue
        src = out.inputs['Surface'].links[0].from_socket
        lp = nt.nodes.new('ShaderNodeLightPath')
        hd = nt.nodes.new('ShaderNodeHoldout')
        mx = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(lp.outputs['Is Camera Ray'], mx.inputs[0])
        nt.links.new(src, mx.inputs[1])
        nt.links.new(hd.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs['Surface'])
        undo.append((nt, out, src, (lp, hd, mx)))

    def restore():
        for nt, out, src, nodes in undo:
            nt.links.new(src, out.inputs['Surface'])
            for nn in nodes:
                nt.nodes.remove(nn)
    return restore


@mat_cache
def mat_wood_vinyl(name='wood_vinyl'):
    """90s TV cabinet wood-grain vinyl: printed walnut-ish grain #5B3A22 -> #7A5232 (object x along the grain),
    satin print with a slight coat, scuffs, edge wear to the pale substrate on corners (pointiness), dust on top."""
    m, b, g = B.principled(name, '#6A4529', rough=0.42, spec=0.5, coat=0.25, coat_rough=0.25)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    gc = g.comb(g.m('MULTIPLY', x, 0.15), g.m('MULTIPLY', y, 1.0), g.m('MULTIPLY', z, 1.0))
    grain = g.wave(gc, 7.0, 9.0, 4.0, bands='Y')
    fine = g.noise(g.comb(g.m('MULTIPLY', x, 0.05), g.m('MULTIPLY', y, 4.0), g.m('MULTIPLY', z, 4.0)), 90.0, 3.0, 0.6)
    t = g.m('ADD', g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.0, 1.0), 0.7), g.m('MULTIPLY', fine, 0.3))
    c = g.mix(t, C('#5B3A22'), C('#7A5232'))
    c = g.mix(g.mr(g.noise(co, 2.5, 3.0, 0.6), 0.4, 0.7, 0.0, 0.35), c, C('#4A2E1B'))      # sun-faded patches
    pt = g.n('ShaderNodeNewGeometry').outputs['Pointiness']
    wear = g.m('MULTIPLY', g.mr(pt, 0.52, 0.60, 0.0, 1.0, smooth=True), g.mr(g.noise(co, 60.0, 3.0, 0.6), 0.35, 0.6, 0.0, 1.0))
    c = g.mix(wear, c, C('#B9A68A'))
    up = up_mask(g, 0.2, 0.95)
    dust = g.m('MULTIPLY', up, g.mr(g.noise(co, 25.0, 4.0, 0.6), 0.45, 0.75, 0.15, 0.45))
    c = g.mix(dust, c, C('#9A8E7C'))
    scr = g.mr(g.noise(stretch(g, co, 1800.0, 60.0, 60.0), 1.0, 2.0, 0.5), 0.74, 0.8, 0.0, 1.0)
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('ADD', g.m('MULTIPLY', dust, 0.4), g.m('MULTIPLY', wear, 0.3)), 0.40))
    g.put(b.inputs['Coat Weight'], g.m('SUBTRACT', 0.25, g.m('MULTIPLY', dust, 0.25)))
    add_bumps(g, b, (fine, 0.05, 0.0003), (scr, 0.08, 0.0001), (g.noise(co, 900.0, 2.0, 0.6), 0.04, 0.0001))
    return m


@mat_cache
def mat_bezel(name='bezel_plastic', base='#2B2927', worn=None):
    """Dark grey textured (stippled) plastic: fine stipple bump, dust in cavities, shiny worn patch round the
    controls `worn` = (x, z, radius) in object coordinates."""
    m, b, g = B.principled(name, base, rough=0.55, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    stip = vor(g, co, 2200.0, out='Distance')
    c = vsc(g, rgb(g, base), g.m('MULTIPLY_ADD', g.noise(co, 30.0, 3.0, 0.6), 0.25, 0.88))
    cav = g.m('MULTIPLY', g.mr(ao(g, 0.006), 0.4, 0.95, 1.0, 0.0), 0.8)
    up = up_mask(g, 0.3, 0.95)
    dust = g.m('MAXIMUM', cav, g.m('MULTIPLY', up, g.mr(g.noise(co, 40.0, 3.0, 0.6), 0.4, 0.75, 0.2, 0.7)))
    c = g.mix(dust, c, C('#6C6458'))
    rough = g.m('ADD', g.m('MULTIPLY', dust, 0.3), 0.55)
    if worn is not None:
        wx, wz, wr = worn
        dx = g.m('SUBTRACT', x, wx)
        dz = g.m('SUBTRACT', z, wz)
        dd = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dz, dz)))
        wm = g.m('MULTIPLY', g.mr(dd, wr, wr * 0.3, 0.0, 1.0, smooth=True), g.mr(g.noise(co, 80.0, 3.0, 0.6), 0.3, 0.6, 0.4, 1.0))
        rough = g.m('SUBTRACT', rough, g.m('MULTIPLY', wm, 0.3))
        stip = g.m('MULTIPLY', stip, g.m('SUBTRACT', 1.0, g.m('MULTIPLY', wm, 0.7)))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], rough)
    add_bumps(g, b, (stip, 0.25, 0.0002), (g.noise(co, 1500.0, 2.0, 0.6), 0.05, 0.0001))
    return m


@mat_cache
def mat_knob(name='knob_worn'):
    """ABS knob #1A1817, grip ridges come from the mesh; fingertip shine on the rim, dust in the ridges."""
    m, b, g = B.principled(name, '#1A1817', rough=0.45, spec=0.5)
    co = g.co('Object')
    cav = g.mr(ao(g, 0.003), 0.4, 0.95, 1.0, 0.0)
    c = g.mix(g.m('MULTIPLY', cav, 0.7), C('#1A1817'), C('#5E574E'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', cav, 0.35), 0.32))
    add_bumps(g, b, (g.noise(co, 1200.0, 2.0, 0.6), 0.06, 0.0001))
    return m


@mat_cache
def mat_chrome_insert(name='chrome_insert'):
    """Brushed chrome cap #C9C7C2 with concentric brushing and a white index line worn half off (object +y = line)."""
    m, b, g = B.principled(name, '#C9C7C2', rough=0.25, metal=1.0)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    rr = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', y, y)))
    brush = g.noise(g.comb(g.m('MULTIPLY', rr, 4000.0), g.m('ARCTAN2', y, x), 0.0), 1.0, 2.0, 0.5)
    line = g.m('MULTIPLY', g.mr(g.m('ABSOLUTE', x), 0.0007, 0.0004, 0.0, 1.0), g.mr(y, 0.0015, 0.0025, 0.0, 1.0))
    line = g.m('MULTIPLY', line, g.mr(g.noise(co, 900.0, 2.0, 0.7), 0.45, 0.55, 0.0, 1.0))
    c = g.mix(line, C('#C9C7C2'), C('#E8E4DA'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Metallic'], g.m('SUBTRACT', 1.0, line))
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', brush, 0.12), g.m('ADD', 0.18, g.m('MULTIPLY', line, 0.3))))
    add_bumps(g, b, (brush, 0.15, 0.00005))
    return m


@mat_cache
def mat_crt_glass(name='crt_glass', w=0.406, h=0.305, base='#161A17', phosphor=True):
    """CRT faceplate: glossy dielectric IOR 1.52, coat 1, dark grey-green phosphor (screen off); fingerprint smudges
    (roughness +0.1 noise) and a thin dust film towards the bezel. Object origin = the picture centre (x, z)."""
    m, b, g = B.principled(name, base if phosphor else '#000000', rough=0.04, spec=0.5, ior=1.52, coat=1.0,
                           coat_rough=0.02)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    smudge = g.mr(g.noise(co, 18.0, 4.0, 0.65, dist=0.6), 0.55, 0.75, 0.0, 1.0, smooth=True)
    prints = g.mr(vor(g, stretch(g, co, 1.0, 1.0, 1.4), 60.0, out='Distance'), 0.0, 0.25, 1.0, 0.0)
    prints = g.m('MULTIPLY', prints, g.mr(g.noise(co, 6.0, 2.0, 0.5), 0.55, 0.7, 0.0, 1.0))
    edge = g.m('SUBTRACT', 1.0, rrect_mask(g, x, z, w * 0.93, h * 0.90, 0.05, soft=0.03))
    dust = g.m('MAXIMUM', g.m('MULTIPLY', edge, g.mr(g.noise(co, 400.0, 3.0, 0.6), 0.3, 0.7, 0.15, 0.4)),
               g.m('MULTIPLY', g.mr(g.noise(co, 9.0, 3.0, 0.6), 0.55, 0.8, 0.0, 1.0), 0.12))
    g.put(b.inputs['Coat Roughness'], g.m('ADD', g.m('ADD', g.m('MULTIPLY', smudge, 0.10), g.m('MULTIPLY', prints, 0.08)),
                                         g.m('ADD', 0.02, g.m('MULTIPLY', dust, 0.25))))
    g.put(b.inputs['Roughness'], g.m('ADD', 0.05, g.m('MULTIPLY', dust, 0.4)))
    if phosphor:
        c = g.mix(g.m('MULTIPLY', dust, 0.35), C(base), C('#4A463E'))
        g.put(b.inputs['Base Color'], c)
    else:
        g.put(b.inputs['Base Color'], vsc(g, rgb(g, '#4A463E'), g.m('MULTIPLY', dust, 0.25)))
    return m


@mat_cache
def mat_grille(name='grille'):
    """Speaker grille plate: the bezel plastic with an 8 x 10 grid of 2.6 mm holes (dark, bumped in)."""
    m, b, g = B.principled(name, '#262422', rough=0.55, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    px, pz = 0.0065, 0.0072
    fx = g.m('SUBTRACT', g.m('FRACT', g.m('DIVIDE', g.m('ADD', x, px * 4), px)), 0.5)
    fz = g.m('SUBTRACT', g.m('FRACT', g.m('DIVIDE', g.m('ADD', z, pz * 5), pz)), 0.5)
    dd = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', g.m('MULTIPLY', fx, px), g.m('MULTIPLY', fx, px)),
                         g.m('MULTIPLY', g.m('MULTIPLY', fz, pz), g.m('MULTIPLY', fz, pz))))
    inside = g.m('MULTIPLY', g.mr(g.m('ABSOLUTE', x), px * 4, px * 4 - 0.0005, 0.0, 1.0),
                 g.mr(g.m('ABSOLUTE', z), pz * 5, pz * 5 - 0.0005, 0.0, 1.0))
    hole = g.m('MULTIPLY', g.mr(dd, 0.0014, 0.0011, 0.0, 1.0), inside)
    dust = g.mr(ao(g, 0.004), 0.4, 0.95, 0.6, 0.0)
    c = g.mix(hole, g.mix(dust, C('#262422'), C('#5E574E')), C('#030303'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', hole, 0.4), 0.55))
    add_bumps(g, b, (g.m('SUBTRACT', 1.0, hole), 0.6, 0.0012), (vor(g, co, 2200.0), 0.2, 0.0002))
    return m


@mat_cache
def mat_led(name='led_off'):
    m, b, g = B.principled(name, '#3A0705', rough=0.12, spec=0.6, coat=1.0, coat_rough=0.05)
    return m


@mat_cache
def mat_lace(name='lace_doily', mode='polar', r_px=1.0):
    """Crocheted cotton, aged and yellowed #E9DFC8: alpha-cut lace from UV (polar: u = radius 0..1, v = angle 0..1;
    rect: u, v metres), thread bump, sheen 0.3, a faint tea / dust stain."""
    m, b, g = B.principled(name, '#E3D7BC', rough=0.85, spec=0.3, sheen=0.3)
    uv = g.uv()
    u, v, _ = g.xyz(uv)
    co = g.co('Object')
    if mode == 'polar':
        th = g.m('MULTIPLY', v, 2 * math.pi)
        rings = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', g.m('FRACT', g.m('MULTIPLY', u, 9.0)), 0.5)), 0.42, 0.34, 0.0, 1.0)
        spk = g.mr(g.m('ABSOLUTE', g.m('SINE', g.m('MULTIPLY', th, 24.0))), 0.18, 0.08, 0.0, 1.0)
        petal_r = g.m('ADD', 0.30, g.m('MULTIPLY', g.m('ABSOLUTE', g.m('SINE', g.m('MULTIPLY', th, 4.0))), 0.12))
        petal = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', u, petal_r)), 0.035, 0.02, 0.0, 1.0)
        mesh_ = g.mr(g.m('MULTIPLY', g.m('SINE', g.m('MULTIPLY', u, 120.0)), g.m('SINE', g.m('MULTIPLY', th, 90.0))), 0.15, 0.35, 0.0, 1.0)
        centre = g.mr(u, 0.10, 0.09, 0.0, 1.0)
        solid = g.m('MAXIMUM', g.m('MAXIMUM', rings, spk), g.m('MAXIMUM', petal, centre))
        solid = g.m('MAXIMUM', solid, g.m('MULTIPLY', mesh_, g.mr(u, 0.55, 0.6, 0.0, 1.0)))
        scallop = g.m('SUBTRACT', 0.965, g.m('MULTIPLY', g.m('ABSOLUTE', g.m('SINE', g.m('MULTIPLY', th, 18.0))), 0.05))
        solid = g.m('MAXIMUM', solid, g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', u, g.m('SUBTRACT', scallop, 0.015))), 0.012, 0.006, 0.0, 1.0))
        alpha = g.m('MULTIPLY', solid, g.mr(g.m('SUBTRACT', scallop, u), 0.0, 0.004, 0.0, 1.0))
    else:
        sx = g.m('MULTIPLY', u, 1.0 / 0.006)
        sy = g.m('MULTIPLY', v, 1.0 / 0.006)
        cell = g.m('MAXIMUM', g.m('ABSOLUTE', g.m('SUBTRACT', g.m('FRACT', sx), 0.5)),
                   g.m('ABSOLUTE', g.m('SUBTRACT', g.m('FRACT', sy), 0.5)))
        grid = g.mr(cell, 0.36, 0.44, 0.0, 1.0)
        dia = g.mr(g.m('ABSOLUTE', g.m('SINE', g.m('MULTIPLY', g.m('ADD', sx, sy), math.pi / 2))), 0.12, 0.05, 0.0, 1.0)
        flower = g.mr(g.m('SQRT', g.m('ADD', g.m('MULTIPLY', g.m('SUBTRACT', g.m('FRACT', g.m('MULTIPLY', sx, 0.25)), 0.5),
                                                          g.m('SUBTRACT', g.m('FRACT', g.m('MULTIPLY', sx, 0.25)), 0.5)),
                                              g.m('MULTIPLY', g.m('SUBTRACT', g.m('FRACT', g.m('MULTIPLY', sy, 0.25)), 0.5),
                                                  g.m('SUBTRACT', g.m('FRACT', g.m('MULTIPLY', sy, 0.25)), 0.5)))), 0.22, 0.18, 0.0, 1.0)
        ring = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', flower, 0.5)), 0.5, 0.3, 0.0, 1.0)
        alpha = g.m('MAXIMUM', g.m('MULTIPLY', g.m('MAXIMUM', grid, dia), 0.9), ring)
    fibre = g.noise(co, 2500.0, 2.0, 0.6)
    alpha = g.m('MULTIPLY', alpha, g.mr(fibre, 0.2, 0.3, 0.6, 1.0))
    c = g.mix(g.mr(g.noise(co, 8.0, 3.0, 0.6), 0.45, 0.75, 0.0, 0.6), C('#ECE3CE'), C('#CDBB94'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Alpha'], alpha)
    add_bumps(g, b, (fibre, 0.4, 0.0003))
    return m


@mat_cache
def mat_distemper(name='distemper_wall', smudge_z=(0.85, 1.35)):
    """90s distemper wall #C8B48E: blotchy, chalky (rough 0.95), a darker hand-height smudge band, faint seepage."""
    m, b, g = B.principled(name, '#C8B48E', rough=0.95, spec=0.3)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', g.noise(co, 1.4, 5.0, 0.62), 0.5), 0.22, 1.0)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', g.noise(co, 40.0, 3.0, 0.6), 0.10, 0.95))
    band = g.m('MULTIPLY', g.m('MULTIPLY', g.mr(z, smudge_z[0] - 0.1, smudge_z[0] + 0.05, 0.0, 1.0, smooth=True),
                                   g.mr(z, smudge_z[1] + 0.1, smudge_z[1] - 0.05, 0.0, 1.0, smooth=True)),
               g.mr(g.noise(co, 5.0, 4.0, 0.6), 0.35, 0.7, 0.2, 1.0))
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', band, -0.16, 1.0))
    seep = g.m('MULTIPLY', streaks(g, co, 7.0, 0.8, 1.0, 0.5, 0.72), g.mr(z, 2.1, 2.7, 0.0, 1.0, smooth=True))
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', seep, -0.25, 1.0))
    g.put(b.inputs['Base Color'], vsc(g, rgb(g, '#C8B48E'), k))
    add_bumps(g, b, (g.noise(co, 180.0, 4.0, 0.6), 0.3, 0.0015))
    return m


@mat_cache
def mat_teak_table(name='teak_table', rings=()):
    """Teak / sheesham side table: grain along object x, polish (coat), wear, cup rings at `rings` [(x, y, r)]."""
    m, b, g = B.principled(name, '#5E3A1F', rough=0.35, spec=0.5, coat=0.5, coat_rough=0.15)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    grain = g.wave(g.comb(g.m('MULTIPLY', x, 0.12), y, z), 9.0, 7.0, 3.0, bands='Y')
    fine = g.noise(g.comb(g.m('MULTIPLY', x, 0.08), g.m('MULTIPLY', y, 3.0), z), 120.0, 2.0, 0.6)
    k = g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.70, 1.18), g.m('MULTIPLY_ADD', fine, 0.25, 0.88))
    ring_k = None
    for (rx, ry, R) in rings:
        ddx = g.m('SUBTRACT', x, rx)
        ddy = g.m('SUBTRACT', y, ry)
        d = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', ddx, ddx), g.m('MULTIPLY', ddy, ddy)))
        ring = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', d, R)), 0.0035, 0.0006, 0.0, 1.0, smooth=True)
        ring_k = ring if ring_k is None else g.m('MAXIMUM', ring_k, ring)
    scr = g.mr(g.noise(stretch(g, co, 30.0, 1500.0, 1500.0), 1.0, 2.0, 0.5), 0.74, 0.8, 0.0, 1.0)
    if ring_k is not None:
        k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', ring_k, -0.35, 1.0))
    g.put(b.inputs['Base Color'], vsc(g, rgb(g, '#5E3A1F'), k))
    cr = g.m('ADD', g.m('MULTIPLY', scr, 0.25), 0.14)
    if ring_k is not None:
        cr = g.m('ADD', cr, g.m('MULTIPLY', ring_k, 0.3))
    g.put(b.inputs['Coat Roughness'], cr)
    add_bumps(g, b, (fine, 0.08, 0.0005), (scr, 0.1, 0.0001))
    return m


@mat_cache
def mat_cream_plastic(name='switch_plastic', base='#E6DCC4'):
    """Yellowed cream switchboard plastic (glossy-ish), grime round the switches."""
    m, b, g = B.principled(name, base, rough=0.3, spec=0.5)
    co = g.co('Object')
    cav = g.mr(ao(g, 0.006), 0.4, 0.95, 1.0, 0.0)
    c = g.mix(g.mr(g.noise(co, 20.0, 3.0, 0.6), 0.3, 0.7, 0.0, 0.5), C(base), C('#D2C29C'))
    c = g.mix(g.m('MULTIPLY', cav, 0.8), c, C('#7C6F58'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', cav, 0.4), 0.28))
    add_bumps(g, b, (g.noise(co, 900.0, 2.0, 0.6), 0.05, 0.0001))
    return m


@mat_cache
def mat_terrazzo(name='terrazzo'):
    """Grey terrazzo floor tiles (30 cm) with marble chips, worn polish."""
    m, b, g = B.principled(name, '#8E8A82', rough=0.3, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    chips = vor(g, co, 140.0, out='Color')
    cr, cg, _ = g.xyz(chips)
    chipm = g.mr(vor(g, co, 140.0, out='Distance'), 0.25, 0.18, 0.0, 1.0)
    c = g.mix(chipm, C('#8A867E'), g.mix(cr, C('#E6E0D2'), g.mix(cg, C('#3E3A36'), C('#A67A5A'))))
    gx = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', g.m('FRACT', g.m('DIVIDE', x, 0.3)), 0.5)), 0.497, 0.490, 0.0, 1.0)
    gy = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', g.m('FRACT', g.m('DIVIDE', y, 0.3)), 0.5)), 0.497, 0.490, 0.0, 1.0)
    grout = g.m('MAXIMUM', gx, gy)
    c = g.mix(grout, c, C('#4A4640'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', g.noise(co, 3.0, 3.0, 0.6), 0.3), 0.18))
    add_bumps(g, b, (g.m('SUBTRACT', 1.0, grout), 0.3, 0.001))
    return m


@mat_cache
def mat_window_paint(name='window_paint', base='#3F5E52'):
    """Old oil-painted wooden window frame (desi blue-green), chipped to grey wood at the edges."""
    m, b, g = B.principled(name, base, rough=0.45, spec=0.5)
    co = g.co('Object')
    pt = g.n('ShaderNodeNewGeometry').outputs['Pointiness']
    chip = g.m('MULTIPLY', g.mr(pt, 0.52, 0.58, 0.0, 1.0), g.mr(g.noise(co, 50.0, 4.0, 0.7), 0.5, 0.6, 0.0, 1.0))
    c = g.mix(chip, C(base), C('#8C8170'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', chip, 0.4), 0.42))
    add_bumps(g, b, (g.noise(co, 300.0, 3.0, 0.6), 0.15, 0.0003))
    return m


TV = dict(T0=0.65, X=0.0, YF=-0.24, W=0.56, H=0.47, D=0.48, SX=-0.050, SZ=0.912, PW=0.406, PH=0.305, PR=0.030,
          SAG=0.018)
TV['Z0'] = TV['T0'] + 0.012
TV['Z1'] = TV['Z0'] + TV['H']
TV['ZC'] = (TV['Z0'] + TV['Z1']) / 2
CRT_R = (0.254 ** 2 + TV['SAG'] ** 2) / (2 * TV['SAG'])        # faceplate sphere radius (~1.8 m)
GLASS_APEX = TV['YF'] + 0.010                                  # glass apex 10 mm behind the bezel front face
CTRL_X = 0.236                                                 # right column: speaker grille
CTRL_Z = 0.6965                                                # bottom strip under the picture: knobs, LED, keys
KNOB_CH = (0.150, TV['YF'], CTRL_Z)
KNOB_VOL = (0.100, TV['YF'], CTRL_Z)
LED_XZ = (0.058, CTRL_Z + 0.004)
WIN = dict(x=-1.6, y0=-1.75, y1=-0.55, z0=0.85, z1=2.05)
ROOM = dict(x0=-1.6, x1=1.8, y0=-3.3, y1=0.42, zc=2.9)


def glass_y(x, z):
    """Faceplate surface y at picture-local (x, z) (spherical bulge towards the camera)."""
    r2 = x * x + z * z
    return GLASS_APEX + (CRT_R - math.sqrt(CRT_R * CRT_R - r2))


def build_crt(q=1.0):
    """21-inch CRT TV: wood-grain vinyl shell, stippled dark bezel (off-centre opening with a sloped inner lip),
    spherical faceplate (sagitta 18 mm) with a black inner mask, right column: perforated speaker grille; bottom strip
    under the picture (so the knobs read bottom-right in CAM_TV_MACRO): channel + volume knobs (ridged, chrome
    inserts), 4 push buttons, red standby LED (off); tapered back cover, rubber feet."""
    T = TV
    objs = []
    E = lambda o, role='tv': (o.__setitem__('role', role), objs.append(o), o)[2]  # noqa: E731
    k = max(5, int(8 * q))
    vinyl = mat_wood_vinyl()
    bez = mat_bezel('bezel_plastic', worn=(0.125, CTRL_Z, 0.06))
    hx, hz = T['W'] / 2, T['H'] / 2
    # wood shell (front 15 mm behind the bezel face, to the start of the back taper)
    E(rbox('tv_shell', (0.0, -0.0425, T['ZC']), (hx - 0.002, 0.1475, hz - 0.002), 0.010, 0.006, vinyl, axis='Y', k=k))
    # back cover: black plastic taper
    E(loft2('tv_back', [(0.0, T['ZC'], hx - 0.012, hz - 0.012, 0.012, 0.10), (0.0, T['ZC'] - 0.01, 0.20, 0.17, 0.03, 0.24),
                        (0.0, T['ZC'] - 0.02, 0.15, 0.13, 0.03, 0.30)], mat_bezel('back_plastic', '#1E1C1B'), k=k,
              cap1=True))
    # bezel: outer edge (cabinet centred) -> front face -> opening (picture centred) -> sloped lip over the glass
    sx, sz = T['SX'], T['SZ']
    yf = T['YF']
    loops = [(0.0, T['ZC'], hx + 0.001, hz + 0.001, 0.016, yf + 0.060),
             (0.0, T['ZC'], hx + 0.001, hz + 0.001, 0.016, yf + 0.008),
             (0.0, T['ZC'], hx - 0.002, hz - 0.002, 0.013, yf + 0.0015),
             (0.0, T['ZC'], hx - 0.006, hz - 0.006, 0.010, yf),
             (sx, sz, 0.233, 0.182, 0.040, yf),
             (sx, sz, 0.228, 0.177, 0.037, yf + 0.0025),
             (sx, sz, 0.214, 0.164, 0.031, yf + 0.016),
             (sx, sz, 0.2115, 0.1615, 0.030, yf + 0.019),
             (sx, sz, 0.2115, 0.1615, 0.030, yf + 0.040)]
    E(loft2('tv_bezel', loops, bez, k=k))
    # faceplate glass (object origin = picture centre) + the black mask band behind its edge
    n = max(24, int(64 * q))
    gw, gh = 0.436, 0.338
    V, F = [], []
    for i in range(n + 1):
        for j in range(n + 1):
            x = -gw / 2 + gw * i / n
            z = -gh / 2 + gh * j / n
            V.append((x, glass_y(x, z) - yf - 0.0, z))
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            F.append((a, a + 1, a + n + 2, a + n + 1))
    glass = _mesh('crt_glass', V, F, mat_crt_glass(), smooth=True, role='glass')
    glass.location = (sx, yf, sz)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(glass.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f_ in bm.faces:                 # normals towards the camera (-y)
        if f_.normal.y > 0:
            f_.normal_flip()
    bm.to_mesh(glass.data)
    bm.free()
    E(glass, 'glass')
    # glass thickness edge + tube behind (dark), so grazing rays never see through
    E(B.cube('tube_dark', (sx - 0.22, yf + 0.032, sz - 0.17), (sx + 0.22, yf + 0.10, sz + 0.17), mat_bezel('tube_black', '#050505'),
             role='tv'))
    # right column: grille, knobs, buttons, LED
    cx = CTRL_X
    gr = rbox('tv_grille', (cx, yf - 0.0008, 0.93), (0.031, 0.0012, 0.078), 0.004, 0.0008, mat_grille(), axis='Y', k=4)
    E(gr)
    kn_m, ch_m = mat_knob(), mat_chrome_insert()
    feats = {}
    for nm, (kx, ky, kz), rot in (('knob_ch', KNOB_CH, 23.0), ('knob_vol', KNOB_VOL, -61.0)):
        def ripple(th, z_):
            r_ = np.clip(np.cos(th * 12.0), 0.0, 1.0) ** 3
            return 1.0 + 0.045 * r_ * ((z_ > 0.003) & (z_ < 0.0165))
        prof = [(0.0158, 0.0), (0.0158, 0.0022), (0.0142, 0.0030), (0.0140, 0.0040), (0.0136, 0.0150), (0.0131, 0.0170),
                (0.0122, 0.0180), (0.0100, 0.0181), (1e-5, 0.0181)]
        kb = lathe_obj(nm, prof, kn_m, seg=max(48, int(96 * q)), ripple=ripple, sharp=60)
        kb.rotation_euler = (math.radians(90), 0.0, math.radians(rot))
        kb.location = (kx, ky, kz)
        E(kb)
        ins = lathe_obj(nm + '_insert', [(1e-5, 0.0018), (0.0085, 0.0016), (0.0094, 0.0008), (0.0095, 0.0)], ch_m, seg=48)
        ins.parent = kb
        ins.location = (0, 0, 0.0177)
        E(ins)
        feats[nm] = (kx, ky - 0.019, kz)
    bt_m = mat_bezel('button_plastic', '#1C1B1A')
    for i in range(4):
        E(rbox(f'tv_btn{i}', (-0.040 + i * 0.016, yf - 0.0025, CTRL_Z), (0.0052, 0.003, 0.0034), 0.0012, 0.001, bt_m,
               axis='Y', k=4))
    led = lathe_obj('tv_led', [(1e-5, 0.0022), (0.0016, 0.0019), (0.0024, 0.001), (0.0026, 0.0)], mat_led(), seg=24)
    led.rotation_euler = (math.radians(90), 0, 0)
    led.location = (LED_XZ[0], yf, LED_XZ[1])
    E(led)
    feats['led_xy'] = (LED_XZ[0], yf - 0.002, LED_XZ[1])
    feats['knob_ch'] = feats.pop('knob_ch')
    feats.pop('knob_vol', None)
    feats['knob_vol'] = (KNOB_VOL[0], KNOB_VOL[1] - 0.019, KNOB_VOL[2])
    # rubber feet
    for i, (fx, fy) in enumerate(((-0.24, -0.20), (0.24, -0.20), (-0.24, 0.06), (0.24, 0.06))):
        E(B.cyl(f'tv_foot{i}', (fx, fy, T['T0'] + 0.006), 0.012, 0.012, mat_abs('rubber', '#111010', '#2A2826', 0.8), seg=20))
    # picture corners on the curved glass, TL TR BR BL (world)
    pw, ph = T['PW'], T['PH']
    quad = []
    for (qx, qz) in ((-pw / 2, ph / 2), (pw / 2, ph / 2), (pw / 2, -ph / 2), (-pw / 2, -ph / 2)):
        quad.append((sx + qx, glass_y(qx, qz), sz + qz))
    return objs, feats, quad, glass


def build_doily(q=1.0):
    """Oval crocheted doily on the cabinet top, its front 4 cm hanging over the bezel edge (draped analytically)."""
    T = TV
    nu, nv = max(24, int(48 * q)), max(64, int(160 * q))
    rx, ry, cy = 0.20, 0.155, -0.115
    top = T['Z1'] + 0.0012
    edge = T['YF'] - 0.0005

    def fn(u, v):
        th = 2 * math.pi * v
        x = rx * u * math.cos(th) + 0.02
        y = cy + ry * u * math.sin(th)
        sag = 0.0012 * math.sin(7 * th) * u
        if y >= edge + 0.004:
            return (x, y, top + sag)
        d = (edge + 0.004) - y
        R = 0.004
        if d < R * math.pi / 2:
            a = d / R
            return (x, edge + 0.004 - R * math.sin(a) - 0.0006, top - R * (1 - math.cos(a)))
        return (x, edge - 0.0006 - 0.0004 * (d - R * math.pi / 2) / 0.04, top - R - (d - R * math.pi / 2))
    o = grid_mesh('doily', fn, nu, nv, mat_lace('lace_doily', 'polar'), role='tv')
    o.data.polygons.foreach_set('use_smooth', np.ones(len(o.data.polygons), bool))
    sol = o.modifiers.new('solid', 'SOLIDIFY')
    sol.thickness = 0.0008
    return o


def build_room(q=1.0):
    """The 90s room: distemper walls, terrazzo floor, ceiling; teak side table with a lace runner; window with
    iron bars (blue-green frame) in the left wall and the bright afternoon outside; coax from a hole high on the
    wall, nail-clipped down to the TV; cream switchboard (2 rockers + socket). Roles: 'room', 'sky', 'tv'."""
    R = ROOM
    W = WIN
    objs = []
    E = lambda o, role='room': (o.__setitem__('role', role), objs.append(o), o)[2]  # noqa: E731
    wall = mat_distemper()
    th = 0.12
    E(B.cube('wall_back', (R['x0'] - th, R['y1'], -0.05), (R['x1'] + th, R['y1'] + th, R['zc'])
             , wall))
    E(B.cube('wall_right', (R['x1'], R['y0'], -0.05), (R['x1'] + th, R['y1'], R['zc']), wall))
    E(B.cube('wall_front', (R['x0'] - th, R['y0'] - th, -0.05), (R['x1'] + th, R['y0'], R['zc']), wall))
    # left wall with the window opening (4 boxes round it)
    x0 = R['x0'] - th
    E(B.cube('wall_left_a', (x0, R['y0'], -0.05), (R['x0'], W['y0'], R['zc']), wall))
    E(B.cube('wall_left_b', (x0, W['y1'], -0.05), (R['x0'], R['y1'], R['zc']), wall))
    E(B.cube('wall_left_c', (x0, W['y0'], -0.05), (R['x0'], W['y1'], W['z0']), wall))
    E(B.cube('wall_left_d', (x0, W['y0'], W['z1']), (R['x0'], W['y1'], R['zc']), wall))
    E(B.cube('floor', (R['x0'] - th, R['y0'] - th, -0.05), (R['x1'] + th, R['y1'] + th, 0.0), mat_terrazzo()))
    E(B.cube('ceiling', (R['x0'] - th, R['y0'] - th, R['zc']), (R['x1'] + th, R['y1'] + th, R['zc'] + 0.1),
             mat_distemper('ceiling_white', (5.0, 5.1))))
    # skirting band of darker paint
    E(B.cube('skirting', (R['x0'], R['y1'] - 0.004, 0.0), (R['x1'], R['y1'], 0.10), mat_window_paint('skirting', '#6E5A44')))
    # window frame + bars + sill
    wp = mat_window_paint()
    fw = 0.05
    xf = W['x'] - 0.02
    for nm, c0, c1 in (('win_top', (xf - 0.04, W['y0'], W['z1'] - fw), (xf + 0.04, W['y1'], W['z1'])),
                       ('win_bot', (xf - 0.04, W['y0'], W['z0']), (xf + 0.04, W['y1'], W['z0'] + fw)),
                       ('win_l', (xf - 0.04, W['y0'], W['z0']), (xf + 0.04, W['y0'] + fw, W['z1'])),
                       ('win_r', (xf - 0.04, W['y1'] - fw, W['z0']), (xf + 0.04, W['y1'], W['z1'])),
                       ('win_mid', (xf - 0.03, (W['y0'] + W['y1']) / 2 - 0.02, W['z0']), (xf + 0.03, (W['y0'] + W['y1']) / 2 + 0.02, W['z1']))):
        o = E(B.cube(nm, c0, c1, wp))
        bevel_mod(o, 0.004, 2)
    o = E(B.cube('win_sill', (W['x'] - 0.06, W['y0'] - 0.05, W['z0'] - 0.03), (W['x'] + 0.08, W['y1'] + 0.05, W['z0']),
                 mat_plaster('sill_plaster', top=W['z0'], base='#A89C88')))
    bevel_mod(o, 0.006, 2)
    bar_m = mat_paint_steel('window_bars', '#2C3A34')
    for i in range(7):
        y_ = W['y0'] + 0.10 + i * (W['y1'] - W['y0'] - 0.2) / 6
        E(rod(f'win_bar{i}', (W['x'] - 0.07, y_, W['z0']), (W['x'] - 0.07, y_, W['z1']), 0.006, bar_m, seg=12, cap='flat'))
    # the bright afternoon outside (emissive, seen through the window and in the glass; plausible daylight source)
    out_m = B.m_emit('outside_day', '#FFEBD2', 2.0, light=True)
    o = B.cube('outside', (W['x'] - 2.6, W['y0'] - 2.5, -1.0), (W['x'] - 2.5, W['y1'] + 2.5, 4.0), out_m, role='sky')
    E(o, 'sky')
    # teak side table 0.65 m with a lace runner
    tt = mat_teak_table('teak_table', rings=((0.30, -0.27, 0.032),))
    o = E(B.cube('table_top', (-0.40, -0.33, TV['T0'] - 0.03), (0.40, 0.30, TV['T0']), tt))
    bevel_mod(o, 0.004, 3)
    for i, (lx, ly) in enumerate(((-0.36, -0.29), (0.36, -0.29), (-0.36, 0.26), (0.36, 0.26))):
        o = E(B.cube(f'table_leg{i}', (lx - 0.022, ly - 0.022, 0.0), (lx + 0.022, ly + 0.022, TV['T0'] - 0.03), tt))
        bevel_mod(o, 0.003, 2)
    o = E(B.cube('table_apron', (-0.38, -0.31, TV['T0'] - 0.11), (0.38, -0.29, TV['T0'] - 0.03), tt))
    bevel_mod(o, 0.003, 2)
    o = E(B.cube('table_shelf', (-0.36, -0.29, 0.16), (0.36, 0.26, 0.18), tt))
    bevel_mod(o, 0.003, 2)

    def runner(u, v):
        x = -0.36 + 0.72 * u
        yy = 0.20 - 0.62 * v          # back -> front, then hangs over the front edge (y = -0.33)
        top = TV['T0'] + 0.0008
        if yy >= -0.326:
            return (x, yy, top)
        d = -0.326 - yy
        R_ = 0.006
        if d < R_ * math.pi / 2:
            a = d / R_
            return (x, -0.326 - R_ * math.sin(a), top - R_ * (1 - math.cos(a)))
        fold = 0.004 * math.sin(x * 70.0) * min(1.0, (d - R_ * math.pi / 2) / 0.05)
        return (x, -0.326 - R_ - 0.0005 - fold, top - R_ - (d - R_ * math.pi / 2))
    o = grid_mesh('lace_runner', runner, 120, 64, mat_lace('lace_runner', 'rect'), role='room')
    uv = o.data.uv_layers[0]
    uvs = np.zeros(len(uv.data) * 2, np.float32)
    uv.data.foreach_get('uv', uvs)
    uvs = uvs.reshape(-1, 2)
    uvs[:, 0] *= 0.72
    uvs[:, 1] *= 0.62
    uv.data.foreach_set('uv', uvs.ravel())
    o.modifiers.new('solid', 'SOLIDIFY').thickness = 0.0008
    E(o)
    # coax: from a hole high on the back wall, nail-clipped down, then behind the TV
    hole = (0.52, R['y1'], 2.05)
    o = E(B.cyl('coax_hole', (hole[0], R['y1'] - 0.001, hole[2]), 0.012, 0.004, mat_bezel('hole_dark', '#0A0807'), axis='Y', seg=24))
    pts = [(hole[0], R['y1'] + 0.02, hole[2]), (hole[0], R['y1'] - 0.004, hole[2]), (hole[0] + 0.01, R['y1'] - 0.006, 1.85),
           (hole[0] + 0.005, R['y1'] - 0.006, 1.55), (hole[0], R['y1'] - 0.006, 1.25), (hole[0] - 0.02, R['y1'] - 0.008, 1.02),
           (0.30, R['y1'] - 0.05, 0.86), (0.12, 0.33, 0.80), (0.0, 0.31, 0.82)]
    E(tube('coax_wall', pts, 0.0035, mat_coax('coax_wall'), res=3, order=3))
    clip_m = mat_abs('nail_clip_room', base='#D8D2C4', faded='#E8E2D6', rough=0.4)
    for i, z_ in enumerate((1.92, 1.68, 1.42, 1.16)):
        E(rbox(f'coax_clip{i}', (hole[0] + 0.006 - 0.002 * i, R['y1'] - 0.006, z_), (0.0045, 0.006, 0.007), 0.002, 0.0012,
               clip_m))
    # switchboard (cream, yellowed): plate, 2 rockers, 3-pin socket
    sb = (0.86, R['y1'], 1.22)
    cp = mat_cream_plastic()
    E(rbox('switchboard', (sb[0], sb[1] - 0.008, sb[2]), (0.11, 0.008, 0.065), 0.006, 0.003, cp, axis='Y', k=5))
    for i in range(2):
        r_ = rbox(f'rocker{i}', (sb[0] - 0.075 + i * 0.035, sb[1] - 0.018, sb[2] + 0.01), (0.011, 0.004, 0.018), 0.003, 0.0015,
                  mat_cream_plastic('rocker_plastic', '#EDE5D0'), axis='Y', k=4)
        r_.rotation_euler = (math.radians(7 if i == 0 else -7), 0, 0)
        E(r_)
    for i, (dx, dz, rr) in enumerate(((0.045, 0.022, 0.004), (0.035, -0.012, 0.0028), (0.055, -0.012, 0.0028))):
        E(B.cyl(f'socket_hole{i}', (sb[0] + dx, sb[1] - 0.0165, sb[2] + dz), rr, 0.002, mat_bezel('socket_dark', '#0C0B0A'),
                axis='Y', seg=16))
    return objs


def _crt_lights():
    """Afternoon sun through the window (sun lamp, the iron bars and frame cast the patch), the bright outside as
    an emissive plane (fill), a faint warm floor bounce card."""
    W = WIN
    patch = np.array([-0.42, ROOM['y1'], 1.25])      # where the window's sun patch lands: the wall left of the TV
    win_c = np.array([W['x'], (W['y0'] + W['y1']) / 2, (W['z0'] + W['z1']) / 2])
    d = win_c - patch
    d /= np.linalg.norm(d)
    ld = bpy.data.lights.new('SUN_window', 'SUN')
    ld.energy = 5.5
    ld.color = hue('#FFD9A8')
    ld.angle = math.radians(0.8)
    o = B.link(bpy.data.objects.new('SUN_window', ld))
    o.rotation_euler = Vector(tuple(-d)).to_track_quat('-Z', 'Y').to_euler()
    o['group'] = 'sun'
    B.light('BOUNCE_floor', 'AREA', (-0.4, -0.9, 0.05), 25.0, '#E8C49A', target=(-0.1, -0.2, 0.9), size=(1.0, 0.6),
            group='bounce', glossy=False)
    # the window itself as a soft 1.2 x 1.0 m area source (sky light through the opening), warm
    B.light('WINDOW_area', 'AREA', (W['x'] + 0.02, (W['y0'] + W['y1']) / 2, (W['z0'] + W['z1']) / 2), 70.0, '#FFE2C0',
            target=(0.0, -0.25, 0.85), size=(1.2, 1.0), group='sun')
    w = bpy.data.worlds.new('W_room')
    bpy.context.scene.world = w
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = tuple(C('#3A3026')) + (1,)
    bg.inputs['Strength'].default_value = 0.2


def cam_tv_macro():
    """CAM_TV_MACRO: 50 mm, 8 deg below the picture centre, framed so the picture spans x 110-970 / y 640-1330
    (SHOTS layout); f/4 on the glass."""
    T = TV
    dist = 1.27
    a = math.radians(8.0)
    tgt = np.array([T['SX'] + 0.0, GLASS_APEX, T['SZ'] + 0.010])
    loc = (T['SX'], GLASS_APEX - dist * math.cos(a), T['SZ'] - dist * math.sin(a))
    return camera('CAM_TV_MACRO', loc, tuple(tgt), 50.0, fstop=4.0, focus=(T['SX'], GLASS_APEX, T['SZ']))


def cam_tv_room():
    """CAM_TV_ROOM: 35 mm, 2.3 m from the TV front, 1.0 m high, the TV centred at y ~1050; f/5.6."""
    T = TV
    loc = (T['X'] - 0.12, T['YF'] - 2.3, 1.0)
    tgt = (T['X'] - 0.10, T['YF'], T['ZC'] + 0.12)
    return camera('CAM_TV_ROOM', loc, tgt, 35.0, fstop=5.6, focus=(T['X'], T['YF'], T['ZC']))


def _crt_asset(q, preview, which):
    tv_objs, feats, quad, glass = build_crt(q)
    doily = build_doily(q)
    doily['role'] = 'tv'
    build_room(q)
    _crt_lights()
    cam = cam_tv_macro() if which == 'macro' else cam_tv_room()
    allo = all_objs()
    T = TV
    beauty_m = glass.data.materials[0]
    refl_m = mat_crt_glass('crt_glass_refl', phosphor=False)
    uv_m = mat_screen_uv('crt_stmap', T['PW'], T['PH'], T['PR'], 'xz')
    spill_m = mat_screen_spill('crt_spill', T['PW'], T['PH'], T['PR'], 'xz')
    state = {'undo': None}

    def glass_mat(m):
        glass.data.materials[0] = m

    def setup(label):
        sc = bpy.context.scene
        if state['undo']:
            state['undo']()
            state['undo'] = None
        lights_on(('sun', 'bounce'))
        world_strength(0.2)
        set_roles(allo, {})
        if label == 'room':
            glass_mat(beauty_m)
            sc.render.film_transparent = False
            return 'beauty', 128
        if label == 'refl':
            glass_mat(refl_m)
            sc.render.film_transparent = True
            state['undo'] = cam_holdout_wrap({refl_m})
            return 'beauty', 96
        if label == 'spill':
            glass_mat(spill_m)
            lights_on(())
            world_strength(0.0)
            set_roles(allo, {'sky': 'hidden'})
            sc.render.film_transparent = False
            return 'beauty', 96
        glass_mat(uv_m)                       # stmap
        set_roles(allo, {'room': 'holdout', 'tv': 'holdout', 'sky': 'hidden'})
        sc.render.film_transparent = True
        return 'flat', S_FLAT
    sf = dict(feats)
    sf['screen_centre'] = (T['SX'], GLASS_APEX, T['SZ'])
    return dict(setup=setup, static_feats=sf, camera_meta=cam_meta(cam),
                extra=dict(quad=quad, picture_mm=[406, 305], picture_corner_r_mm=30,
                           passes='room = beauty, screen off (opaque); refl = glass reflections only, ADD (RGBA); '
                                  'spill = screen as uniform ivory emitter strength 2, other lights off (opaque, '
                                  'multiply by the picture mean luma and ADD); stmap = 16-bit linear R=u G=v A=mask'))


@asset('crt/macro', 'static', labels=['room', 'refl', 'spill', 'stmap'],
       gpu_spp={'room': 512, 'refl': 256, 'spill': 256}, notes='21-inch CRT close-up (S1, S5, S13): screen off in room; '
       'snow / picture comped through stmap; refl added on top; spill for the screen light on bezel + doily')
def _a5(q, preview):
    return _crt_asset(q, preview, 'macro')


@asset('crt/room', 'static', labels=['room', 'refl', 'spill', 'stmap'],
       gpu_spp={'room': 512, 'refl': 256, 'spill': 256}, notes='the CRT on the teak table in the 90s room (S3): window '
       'light, coax down the wall from the ceiling hole, switchboard; same passes as crt/macro')
def _a6(q, preview):
    return _crt_asset(q, preview, 'room')


# ============================================================================= A7 phone on the desk

PH = dict(W=0.075, L=0.162, T=0.0083, R=0.0105, SW=0.0702, SL=0.1562, SR=0.0085, YAW=-12.0, X=0.0, Y=0.0)
DESK_Z = 0.75
TEA = (-0.088, 0.118)          # tea glass position (desk xy), top-left of frame, out of focus
KB = (0.035, 0.128)            # keyboard corner (front-left corner of the keyboard)


@mat_cache
def mat_walnut(name='walnut_desk', rings=()):
    """Walnut veneer desk: grain along x (wave + fine pores), satin lacquer rough 0.35-0.5, light scratches, a tea
    ring stain at each `rings` (x, y, r) (object = world coords)."""
    m, b, g = B.principled(name, '#4E3221', rough=0.4, spec=0.5, coat=0.35, coat_rough=0.22)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    warp = g.noise(g.comb(g.m('MULTIPLY', x, 0.5), g.m('MULTIPLY', y, 6.0), z), 3.0, 3.0, 0.6)
    gy = g.m('ADD', y, g.m('MULTIPLY', warp, 0.02))
    grain = g.mr(g.noise(g.comb(g.m('MULTIPLY', x, 0.04), g.m('MULTIPLY', gy, 1.0), z), 140.0, 6.0, 0.62), 0.3, 0.7, 0.0, 1.0)
    figure = g.noise(g.comb(g.m('MULTIPLY', x, 0.3), g.m('MULTIPLY', y, 8.0), z), 4.0, 5.0, 0.7)
    grain = g.m('ADD', g.m('MULTIPLY', grain, 0.6), g.m('MULTIPLY', figure, 0.4))
    pores = g.noise(g.comb(g.m('MULTIPLY', x, 0.04), g.m('MULTIPLY', y, 2.5), z), 300.0, 2.0, 0.6)
    t = g.m('ADD', g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.0, 1.0), 0.75), g.m('MULTIPLY', pores, 0.25))
    c = g.mix(t, C('#3A2316'), C('#6B4A32'))
    c = g.mix(g.mr(g.noise(co, 1.5, 3.0, 0.6), 0.35, 0.7, 0.0, 0.3), c, C('#7A5A40'))
    scr = g.m('MAXIMUM', g.mr(g.noise(stretch(g, co, 25.0, 1800.0, 25.0), 1.0, 2.0, 0.5), 0.76, 0.81, 0.0, 1.0),
              g.mr(g.noise(stretch(g, g.co('Object'), 1500.0, 40.0, 25.0), 1.0, 2.0, 0.5), 0.78, 0.82, 0.0, 0.7))
    rough = g.m('ADD', g.m('MULTIPLY', g.noise(co, 6.0, 3.0, 0.6), 0.15), 0.33)
    ring_k = None
    for (rx, ry, R) in rings:
        dx = g.m('SUBTRACT', x, rx)
        dy = g.m('SUBTRACT', y, ry)
        d = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy)))
        d = g.m('ADD', d, g.m('MULTIPLY', g.m('SUBTRACT', g.noise(co, 90.0, 3.0, 0.6), 0.5), 0.003))
        ring = g.m('MAXIMUM', g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', d, R)), 0.0022, 0.0004, 0.0, 1.0, smooth=True),
                   g.m('MULTIPLY', g.mr(d, R, R - 0.004, 0.0, 0.25), g.mr(g.noise(co, 40.0, 3.0, 0.6), 0.4, 0.7, 0.3, 1.0)))
        ring_k = ring if ring_k is None else g.m('MAXIMUM', ring_k, ring)
    if ring_k is not None:
        c = g.mix(g.m('MULTIPLY', ring_k, 0.7), c, C('#2A170C'))
        rough = g.m('ADD', rough, g.m('MULTIPLY', ring_k, 0.2))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Roughness'], rough)
    g.put(b.inputs['Coat Roughness'], g.m('ADD', g.m('MULTIPLY', scr, 0.35), 0.2))
    add_bumps(g, b, (pores, 0.12, 0.0003), (scr, 0.12, 0.0001))
    return m


@mat_cache
def mat_phone_glass(name='phone_glass', w=0.0702, l=0.1562):
    """Black cover glass IOR 1.5 rough 0.02 over an off OLED (#040506); fingerprints + a thumb smear (roughness
    noise) concentrated on the lower half, a few hairline scratches. Object origin = the picture centre (x, y)."""
    m, b, g = B.principled(name, '#040506', rough=0.02, spec=0.5, ior=1.5, coat=1.0, coat_rough=0.015)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    prints = g.mr(vor(g, stretch(g, co, 1.0, 1.3, 1.0), 220.0, out='Distance'), 0.0, 0.3, 1.0, 0.0)
    prints = g.m('MULTIPLY', prints, g.mr(g.noise(co, 30.0, 2.0, 0.5), 0.5, 0.68, 0.0, 1.0))
    lower = g.mr(y, 0.02, -0.06, 0.2, 1.0, smooth=True)
    smear = g.m('MULTIPLY', g.mr(g.noise(stretch(g, co, 0.6, 1.6, 1.0), 40.0, 3.0, 0.6, dist=0.8), 0.55, 0.7, 0.0, 1.0), lower)
    scr = g.mr(g.noise(stretch(g, co, 3000.0, 30.0, 30.0), 1.0, 2.0, 0.5), 0.8, 0.83, 0.0, 1.0)
    cr = g.m('ADD', g.m('ADD', g.m('MULTIPLY', g.m('MULTIPLY', prints, lower), 0.18), g.m('MULTIPLY', smear, 0.12)), 0.012)
    g.put(b.inputs['Coat Roughness'], cr)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', smear, 0.1), 0.03))
    add_bumps(g, b, (scr, 0.05, 0.00003))
    return m


@mat_cache
def mat_phone_alu(name='phone_alu', base='#3A3A3C'):
    """Bead-blasted anodised aluminium frame: fine isotropic grain, rough 0.35, edge chamfers polished (pointiness),
    two plastic antenna lines across the frame."""
    m, b, g = B.principled(name, base, rough=0.35, metal=1.0)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    pt = g.n('ShaderNodeNewGeometry').outputs['Pointiness']
    shine = g.mr(pt, 0.52, 0.58, 0.0, 1.0)
    band = g.m('MAXIMUM', g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', y, 0.068)), 0.0007, 0.0005, 0.0, 1.0),
               g.mr(g.m('ABSOLUTE', g.m('ADD', y, 0.068)), 0.0007, 0.0005, 0.0, 1.0))
    c = g.mix(band, C(base), C('#2C2C2E'))
    g.put(b.inputs['Base Color'], c)
    g.put(b.inputs['Metallic'], g.m('SUBTRACT', 1.0, band))
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('SUBTRACT', 0.36, g.m('MULTIPLY', shine, 0.2)), g.m('MULTIPLY', band, 0.1)))
    add_bumps(g, b, (g.noise(co, 4000.0, 2.0, 0.6), 0.08, 0.00003))
    return m


@mat_cache
def mat_sapphire(name='lens_cover'):
    m, b, g = B.principled(name, '#05070A', rough=0.01, spec=0.6, ior=1.77, coat=1.0, coat_rough=0.01)
    return m


@mat_cache
def mat_tea_glass(name='tea_glass'):
    m, b, g = B.principled(name, '#FFFFFF', rough=0.02, spec=0.5, ior=1.5)
    b.inputs['Transmission Weight'].default_value = 1.0
    co = g.co('Object')
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY', g.mr(g.noise(co, 60.0, 3.0, 0.6), 0.55, 0.8, 0.0, 1.0), 0.12), 0.01))
    return m


@mat_cache
def mat_chai(name='chai'):
    """Milky chai: warm brown, strong subsurface (milk), a slightly darker skin on top."""
    m, b, g = B.principled(name, '#7A4A22', rough=0.12, spec=0.5, sss=0.35, sss_radius=(1.0, 0.5, 0.25), sss_scale=0.002)
    return m


@mat_cache
def mat_tea_film(name='tea_film'):
    """Dried tea residue on the inner wall above the tea line (#7A4A1E, alpha 0.6 at the line fading upward)."""
    m, b, g = B.principled(name, '#7A4A1E', rough=0.4, spec=0.4)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    a = g.m('MULTIPLY', g.mr(z, 0.056, 0.075, 0.6, 0.0), g.mr(g.noise(co, 120.0, 3.0, 0.6), 0.35, 0.7, 0.2, 1.0))
    g.put(b.inputs['Alpha'], a)
    return m


@mat_cache
def mat_keycap(name='keycap'):
    m, b, g = B.principled(name, '#1F1F21', rough=0.5, spec=0.5)
    co = g.co('Object')
    up = up_mask(g, 0.5, 0.98)
    g.put(b.inputs['Roughness'], g.m('SUBTRACT', 0.52, g.m('MULTIPLY', up, g.mr(g.noise(co, 80.0, 2.0, 0.6), 0.4, 0.7, 0.0, 0.2))))
    add_bumps(g, b, (g.noise(co, 2500.0, 2.0, 0.6), 0.08, 0.00005))
    return m


def build_phone(q=1.0):
    """Modern phone 162 x 75 x 8.3 mm face up: alu frame with rounded edges, side keys, cover glass (picture area
    156.2 x 70.2 mm, corner r 8.5 mm, punch-hole camera), back glass with a 3-lens camera bump (no logo)."""
    P = PH
    k = max(6, int(10 * q))
    root = empty('PHONE_ROOT', (P['X'], P['Y'], DESK_Z))
    root.rotation_euler = (0, 0, math.radians(P['YAW']))
    objs = []
    hx, hy = P['W'] / 2, P['L'] / 2
    alu = mat_phone_alu()
    # frame: rounded slab, flat sides, 1.2 mm edge rounds
    fr = loft('phone_frame', round_box_loops(hx, hy, P['R'], 0.0004, P['T'] - 0.0006, 0.0012, n=4), alu, k=k, axis='Z',
              cap0=True, cap1=True, sharp=50, parent=root)
    objs.append(fr)
    # cover glass: slightly proud, 2.5D edge
    gl = loft('phone_glass', round_box_loops(hx - 0.0004, hy - 0.0004, P['R'] - 0.0004, -0.0006, 0.0, 0.0005, n=3),
              mat_phone_glass(), k=k, axis='Z', cap0=True, cap1=True, sharp=50, parent=root)
    gl.location = (0, 0, P['T'])
    gl['role'] = 'glass'
    objs.append(gl)
    # thin black display border under the glass edge is part of the off-display colour; speaker slot
    slot = rbox('phone_speaker', (0.0, hy - 0.0016, P['T'] + 0.00005), (0.006, 0.00028, 0.00006), 0.00027, 0.00002,
                mat_bezel('speaker_slot', '#020202'), parent=root)
    objs.append(slot)
    # side keys (right side: power + volume rocker)
    for nm, y0, L in (('key_power', 0.020, 0.012), ('key_vol', 0.045, 0.024)):
        kk = rbox(nm, (hx + 0.0004, y0, P['T'] / 2), (0.0006, L / 2, 0.0013), 0.0005, 0.0004, alu, parent=root)
        objs.append(kk)
    # back: camera bump with 3 sapphire lens covers (underside, faces the desk)
    bump = rbox('cam_bump', (-hx + 0.019, hy - 0.020, -0.0006), (0.015, 0.015, 0.0012), 0.006, 0.0008, alu, parent=root)
    objs.append(bump)
    for i, (dx, dy) in enumerate(((-0.006, 0.006), (0.006, 0.006), (-0.006, -0.006))):
        ln = lathe_obj(f'lens{i}', [(1e-5, -0.0006), (0.0042, -0.0006), (0.0046, 0.0)], mat_sapphire(), seg=32)
        ln.parent = root
        ln.location = (-hx + 0.019 + dx, hy - 0.020 + dy, -0.0018)
        objs.append(ln)
    for o in objs:
        if o.get('role') in (None, 'prop'):
            o['role'] = 'phone'
    # picture corners (world): TL TR BR BL; picture centre = glass origin
    bpy.context.view_layer.update()
    M = gl.matrix_world
    sw, sl = P['SW'] / 2, P['SL'] / 2
    quad = [tuple(M @ Vector(p)) for p in ((-sw, sl, 0.00001), (sw, sl, 0.00001), (sw, -sl, 0.00001), (-sw, -sl, 0.00001))]
    feats = {'punch_hole': tuple(M @ Vector((0.0, sl - 0.0052, 0.0))), 'phone_centre': tuple(M @ Vector((0, 0, 0)))}
    return root, objs, gl, quad, feats


def build_desk(q=1.0):
    objs = []
    E = lambda o, role='desk': (o.__setitem__('role', role), objs.append(o), o)[2]  # noqa: E731
    o = E(B.cube('desk', (-1.2, -0.6, DESK_Z - 0.03), (1.2, 0.7, DESK_Z), mat_walnut('walnut_desk', rings=((TEA[0], TEA[1], 0.0255),
                                                                                                         (0.16, -0.05, 0.03)))))
    bevel_mod(o, 0.003, 3)
    # keyboard corner: dark aluminium tray + keycaps, no legends
    kx, ky = KB
    tray = rbox('kb_tray', (kx + 0.20, ky + 0.07, DESK_Z + 0.006), (0.20, 0.07, 0.006), 0.008, 0.004,
                mat_phone_alu('kb_alu', '#2A2A2C'))
    E(tray)
    kc = mat_keycap()
    for r_ in range(6):
        for c_ in range(10):
            x_ = kx + 0.014 + c_ * 0.019 + (0.005 if r_ == 1 else 0.0)
            y_ = ky + 0.012 + r_ * 0.019
            E(rbox(f'key{r_}_{c_}', (x_, y_, DESK_Z + 0.0145), (0.0075, 0.0075, 0.0035), 0.0022, 0.0016, kc, k=4))
    # tea glass, chai, residue film
    tx, ty = TEA
    def flutes(th, z_):
        return 1.0 + 0.07 * (np.abs(np.cos(th * 6.0)) ** 0.5) * ((z_ > 0.012) & (z_ < 0.074))
    wall_o = [(0.0245 + (0.0310 - 0.0245) * t, 0.008 + 0.075 * t) for t in np.linspace(0, 1, 16)]
    wall_i = [(0.0292 - (0.0292 - 0.0228) * t, 0.0835 - 0.0735 * t) for t in np.linspace(0, 1, 16)]
    outer = [(1e-5, 0.0), (0.0225, 0.0), (0.0240, 0.002)] + wall_o + [(0.0318, 0.0855), (0.0305, 0.0858)] + wall_i + \
        [(0.0200, 0.0075), (1e-5, 0.0072)]
    gl = lathe_obj('tea_glass', outer, mat_tea_glass(), seg=max(48, int(96 * q)), ripple=flutes, sharp=70)
    gl.location = (tx, ty, DESK_Z)
    E(gl)
    lvl = 0.057
    ch = lathe_obj('chai', [(1e-5, 0.0074), (0.0199, 0.0076), (0.0226, 0.010), (0.0226 + (0.0291 - 0.0228) * (lvl - 0.010) / 0.0735, lvl),
                            (1e-5, lvl)], mat_chai(), seg=64)
    ch.location = (tx, ty, DESK_Z)
    E(ch)
    film = lathe_obj('tea_film', [(0.0226 + 0.0063 * (lvl - 0.010) / 0.0735 - 0.0002, lvl),
                                  (0.0228 + 0.0063 * (0.078 - 0.010) / 0.0735 - 0.0002, 0.078)], mat_tea_film(), seg=64)
    film.location = (tx, ty, DESK_Z)
    E(film)
    return objs


def cam_phone(quad):
    """CAM_PHONE: 100 mm, ~0.55 m, 30 deg off the top-down view (from the front), the phone diagonal, the picture
    filling x 220-860 / y 520-1500; f/2.0 focused on the glass."""
    c = np.mean(np.asarray(quad), 0)
    tilt = math.radians(30.0)
    dist = 0.84
    loc = c + np.array([0.0, -dist * math.sin(tilt), dist * math.cos(tilt)])
    return camera('CAM_PHONE', tuple(loc), tuple(c + np.array([0.0, 0.004, 0.0])), 100.0, fstop=2.0, focus=tuple(c))


def _phone_lights():
    """Warm desk lamp (0.3 m area, top-left), cool-neutral monitor fill from behind-top (dim), dim warm room world."""
    B.light('LAMP_desk', 'AREA', (-0.32, 0.30, DESK_Z + 0.42), 20.0, '#FFC88A', target=(0.0, 0.0, DESK_Z), size=(0.3, 0.3),
            group='lamp')
    B.light('FILL_monitor', 'AREA', (0.05, 0.48, DESK_Z + 0.62), 3.0, '#E8E4DC', target=(0.0, 0.0, DESK_Z),
            size=(0.5, 0.06), group='lamp')
    w = bpy.data.worlds.new('W_desk')
    bpy.context.scene.world = w
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = tuple(C('#2A231C')) + (1,)
    bg.inputs['Strength'].default_value = 0.35


@asset('phone/desk', 'static', labels=['lit', 'spill', 'stmap'], gpu_spp={'lit': 512, 'spill': 256},
       notes='phone face up on the walnut desk (S8): lit = screen off; spill = the screen as an ivory emitter; '
             'stmap = picture UV + mask (punch hole excluded); keyboard corner + cutting-chai glass out of focus')
def _a7(q, preview):
    root, pobjs, gl, quad, feats = build_phone(q)
    build_desk(q)
    _phone_lights()
    cam = cam_phone(quad)
    allo = all_objs()
    P = PH
    beauty_m = gl.data.materials[0]
    hole = [(0.0, P['SL'] / 2 - 0.0052, 0.0016)]
    uv_m = mat_screen_uv('phone_stmap', P['SW'], P['SL'], P['SR'], 'xy', holes=hole)
    spill_m = mat_screen_spill('phone_spill', P['SW'], P['SL'], P['SR'], 'xy', strength=2.0, base='#040506')

    def setup(label):
        sc = bpy.context.scene
        lights_on(('lamp',))
        world_strength(0.35)
        set_roles(allo, {})
        if label == 'lit':
            gl.data.materials[0] = beauty_m
            sc.render.film_transparent = False
            return 'beauty', 128
        if label == 'spill':
            gl.data.materials[0] = spill_m
            lights_on(())
            world_strength(0.0)
            sc.render.film_transparent = False
            return 'beauty', 64
        gl.data.materials[0] = uv_m
        set_roles(allo, {'desk': 'holdout', 'phone': 'holdout'})
        sc.render.film_transparent = True
        return 'flat', S_FLAT
    return dict(setup=setup, static_feats=feats, camera_meta=cam_meta(cam),
                extra=dict(quad=quad, picture_mm=[70.2, 156.2], picture_corner_r_mm=8.5,
                           passes='lit = beauty, screen off (opaque); spill = screen as ivory emitter, lamps off '
                                  '(opaque, multiply by the UI mean luma and ADD); stmap = 16-bit linear R=u G=v A=mask'))


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
    only = [a for a in sys.argv[2:] if not a.startswith('--')]
    for variant in (('day', 'sunset') if not only else ()):
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
    for key in (only or ('clamp/macro', 'crt/macro', 'crt/room', 'phone/desk')):
        if key in LAYOUT:
            print(LAYOUT[key]())
    return rep


def layout_static(key):
    """Build a static asset's scene at the final resolution (no render) and report its camera, screen quad and
    feature points in frame px against the SHOTS targets."""
    _bpy()
    _late()
    reset((W_PX, H_PX), 16)
    S = ASSETS[key]['build'](0.5, True)
    bpy.context.view_layer.update()
    lines = [f'== {key}  camera {S.get("camera_meta", {}).get("name")}  lens {S.get("camera_meta", {}).get("lens_mm")} mm '
             f'loc {S.get("camera_meta", {}).get("location")}']
    q = (S.get('extra') or {}).get('quad')
    if q is not None:
        qp = proj_px(q)
        bb = [round(float(qp[:, 0].min())), round(float(qp[:, 1].min())), round(float(qp[:, 0].max())),
              round(float(qp[:, 1].max()))]
        lines.append(f'   screen quad TL,TR,BR,BL {[[round(float(a)), round(float(b))] for a, b in qp]}  bbox {bb}')
        t = TARGETS.get(key, {}).get('screen')
        if t:
            lines.append(f'   target x {t[0]}-{t[2]} / y {t[1]}-{t[3]}')
    for k, v in S.get('static_feats', {}).items():
        lines.append(f'   {k}: {[round(float(x)) for x in proj_px([v])[0]]}')
    if 'set_yaw' in S:
        for y in (CLAMP_YAWS[0], 0.0, CLAMP_YAWS[-1]):
            S['set_yaw'](y)
            f = S['feats']()
            lines.append(f'   yaw {y:+.1f}: ' + ', '.join(f'{k} {[round(float(x)) for x in proj_px([v])[0]]}' for k, v in f.items()))
    return '\n'.join(lines)


LAYOUT = {k: (lambda k=k: layout_static(k)) for k in ('clamp/macro', 'crt/macro', 'crt/room', 'phone/desk')}


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


def archive(quality=92):
    """Compressed restore copies into brand_reels/assets/thoda_left_bas/assets3d (git, kept < 58 MB): opaque 8-bit
    frames as JPEG (alpha 255), 8-bit RGBA frames as a JPEG colour plate + a PNG alpha plate ('<n>.a.png'), 16-bit
    STMaps as max-compressed PNG, meta.json as is. Lowers the JPEG quality by itself if the folder would pass 58 MB.
    `restore` rebuilds the PNG spec folders (meta.json last)."""
    import cv2
    if os.path.isdir(ARCHIVE):
        shutil.rmtree(ARCHIVE)
    os.makedirs(ARCHIVE)
    index = {}
    for name in sorted(os.listdir(OUT)):
        if not os.path.isdir(os.path.join(OUT, name)):
            continue
        for variant in sorted(os.listdir(os.path.join(OUT, name))):
            d = os.path.join(OUT, name, variant)
            if not os.path.exists(os.path.join(d, 'meta.json')):
                print('  skip (no meta.json):', d)
                continue
            od = os.path.join(ARCHIVE, name, variant)
            os.makedirs(od)
            for f in sorted(os.listdir(d)):
                src = os.path.join(d, f)
                if f == 'meta.json':
                    shutil.copy2(src, od)
                    continue
                if not (f.endswith('.png') and f[:-4].isdigit()):
                    continue
                im = cv2.imread(src, cv2.IMREAD_UNCHANGED)
                key = f'{name}/{variant}/{f}'
                if im.dtype != np.uint8:
                    cv2.imwrite(os.path.join(od, f), im, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                    index[key] = 'png'
                elif im.shape[2] == 4 and im[:, :, 3].min() == 255:
                    cv2.imwrite(os.path.join(od, f[:-4] + '.jpg'), im[:, :, :3], [cv2.IMWRITE_JPEG_QUALITY, quality])
                    index[key] = 'jpg'
                else:
                    a = im[:, :, 3]
                    rgb_ = im[:, :, :3].copy()
                    if a.max() > 0:      # bleed colour into transparent pixels so JPEG blocks do not darken edges
                        m = (a > 0).astype(np.uint8)
                        dil = cv2.dilate(rgb_, np.ones((5, 5), np.uint8))
                        rgb_ = np.where(m[..., None] > 0, rgb_, dil)
                    cv2.imwrite(os.path.join(od, f[:-4] + '.jpg'), rgb_, [cv2.IMWRITE_JPEG_QUALITY, quality])
                    cv2.imwrite(os.path.join(od, f[:-4] + '.a.png'), a, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                    index[key] = 'jpg+a'
    with open(os.path.join(ARCHIVE, 'archive.json'), 'w') as fh:
        json.dump(dict(note='restore with: python pipeline/jawad_reels/assets3d_thoda_left_bas.py restore',
                       jpeg_quality=quality, files=index), fh, indent=1)
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(ARCHIVE) for f in fs)
    print(f'  archive {ARCHIVE}: {tot / 1e6:.1f} MB (JPEG q{quality})')
    if tot > 58e6 and quality > 70:
        return archive(quality - 6)
    return tot


def restore():
    """Rebuild RWS/assets3d/<name>/<variant>/ from the archive (frames first, meta.json last per folder)."""
    import cv2
    idx = json.load(open(os.path.join(ARCHIVE, 'archive.json')))['files']
    folders = set()
    for rel, kind in idx.items():
        dst = os.path.join(OUT, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        folders.add(os.path.dirname(rel))
        base = os.path.join(ARCHIVE, *rel.split('/'))[:-4]
        if kind == 'png':
            shutil.copy2(base + '.png', dst)
            continue
        im = cv2.imread(base + '.jpg', cv2.IMREAD_COLOR)
        a = cv2.imread(base + '.a.png', cv2.IMREAD_UNCHANGED) if kind == 'jpg+a' else np.full(im.shape[:2], 255, np.uint8)
        cv2.imwrite(dst, np.dstack([im, a]))
    for rel in sorted(folders):
        src = os.path.join(ARCHIVE, *rel.split('/'), 'meta.json')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, *rel.split('/'), 'meta.json'))
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
