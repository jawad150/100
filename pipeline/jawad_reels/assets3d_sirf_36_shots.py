"""assets3d_sirf_36_shots.py - photoreal Blender props for Bijli series #3 "Sirf 36 Shots" (@jawad_mp4).

Builds every asset of SHOTS.md section (A) (brand_reels/design/reels/sirf_36_shots/SHOTS.md) with bpy 5.2 / Cycles
CPU: threads 2, adaptive sampling 0.015, OpenImageDenoise with albedo + normal guides, fixed seed, light paths
max 8 / diffuse 3 / glossy 4 / transmission 8, caustics off, filter glossy 0.8, clamp indirect 8, view transform
Standard, look None. Real-world units (metres), sensor 36 mm fitted vertically, DOF from the camera f-stop on the
plates; sprites are rendered sharp (no DOF) and defocused in comp. No brand names, logos or trade dress anywhere,
no faces (the print images are landscapes, a cake, faceless blurred dummies and a blurry thumb).

    RWS = workspace/jawad_reels/sirf_36_shots
    RWS/assets3d/<name>/<pass>/0000.png ... + meta.json     (meta.json written LAST, one per pass folder)
    load: S3.Asset3D('counter_macro', 'tick', root=RWS + '/assets3d')

Output: PNG RGBA 8-bit straight alpha sRGB. Opaque plates are full 1080x1920 frames. Sprites are cropped to their
alpha bbox + 24 px; meta 'frame_xy' = the crop's top-left in that asset camera's full frame (for region renders
that drop onto a plate, e.g. counter_macro/tick and cam_hero/crank, frame_xy is the paste position on the plate).
meta 'features' are in the folder's own pixels (sprite px for cropped folders, frame px for plates);
'features_frame' are the same points in full-frame px. 'px_per_mm' gives the scale at the subject plane for the
top-down sprites, so the compositor can keep every paper prop at one consistent scale.

Assets / folders (see ASSETS.md for sizes, anchors and frame counts)
--------------------------------------------------------------------
    counter_macro  plate, tick (16 f, region, deduped poses), led                    100 mm f/4, behind-right 35 deg down
    cam_hero       lit, flash, glow, crank (8 f, region)                              70 mm f/4, front 3/4
    canister       spin (16 f, 360 deg about the long axis)                           85 mm sprite
    studio_counter day1, day2, night (plates), tin_day1, tin_day2, tin_night,        overhead 100 mm from 2.2 m
                   envelope_night (sprites in the plate camera + contact shadows)
    envelope       flap (6 f, f0 = closed), back, front                               top-down ortho sprite
    print_src      p1..p5 (textures for the prints, opaque)                          35 mm "compact" camera
    prints         p1..p5, back, negatives                                            top-down ortho sprites
    album_page     page (plate), sleeve (PVC reflection overlay)                     top-down
    drives         plate, emit (all LEDs + one frame per drive), labels_mask (4 f)    60 mm f/2.0, 12 deg up

CLI
---
    python3 assets3d_sirf_36_shots.py <name> [<name> ...] [--preview] [--samples N] [--only folder,folder]
    python3 assets3d_sirf_36_shots.py all [--preview]
    python3 assets3d_sirf_36_shots.py sheet | previewsheet      # contact sheets (full + 360 px) to RWS/out/sheets3d
    python3 assets3d_sirf_36_shots.py pack                      # optimised copy to brand_reels/assets/sirf_36_shots/assets3d
    python3 assets3d_sirf_36_shots.py restore                   # copy that archive back into RWS/assets3d (no render)
    python3 assets3d_sirf_36_shots.py selftest                  # textures + palette checks, no Cycles render

    --preview   16 spp, half resolution, sequences only first/mid/last frame, written to RWS/out/preview3d
    env S36_THREADS (default 2). Run every render through pipeline/jawad_reels/tools/heavy.sh.
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
import assets3d_hero as H                 # noqa: E402  reset / write_meta / fonts
import assets3d_bijli_chali_gayi as B     # noqa: E402  engine helpers only (G graph helper, mesh helpers, projection)

bpy = None
Vector = None
Matrix = None

REEL = 'sirf_36_shots'
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RWS = os.path.join(H.WS, REEL)
OUT = os.path.join(RWS, 'assets3d')
PREVIEW = os.path.join(RWS, 'out', 'preview3d')
SHEETS = os.path.join(RWS, 'out', 'sheets3d')
TEX = os.path.join(REPO, 'brand_reels', 'assets', REEL, 'tex3d')     # committed (fonts are not in git)
TEXW = os.path.join(RWS, 'out', 'tex3d')                                # derived textures (from renders)
TEX_FORCE = os.environ.get('S36_TEX_FORCE') == '1'
ARCHIVE = os.path.join(REPO, 'brand_reels', 'assets', REEL, 'assets3d')
THREADS = int(os.environ.get('S36_THREADS', '2'))
FONTS = H.FONTS
CROP_PAD = 24
MM = 0.001
W_PX, H_PX = 1080, 1920
BUILDER = 'pipeline/jawad_reels/assets3d_sirf_36_shots.py'

# ============================================================================= palette (sRGB hex; lin() converts)

TOK = dict(NIGHT_0='#070404', NIGHT_1='#170A07', FLAME='#FF6A1A', RED='#F2312B', EMBER='#B3120E', GOLD='#FF9F1C',
           AMBER='#FFB547', SMOKE='#2A1A15', IVORY='#FFF3E6', ASH='#A8978C')


def lin(c):
    if isinstance(c, str):
        h = TOK.get(c, c).lstrip('#')
        return tuple(H._s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return tuple(float(x) for x in c[:3])


def rgba(c):
    return tuple(lin(c)) + (1.0,)


# ============================================================================= bpy basics

def _bpy():
    global bpy, Vector, Matrix
    if bpy is None:
        B._bpy()
        import bpy as _b
        from mathutils import Vector as _V, Matrix as _M
        bpy, Vector, Matrix = _b, _V, _M
    return bpy


DEVICE = 'CPU'


def is_gpu():
    """True when assets3d_gpu picked a GPU backend for this process (FOSTER_GPU=1 on the RTX PC)."""
    return not DEVICE.startswith('CPU')


def reset(res, samples=64, transparent=False):
    """Empty Cycles scene with this reel's render spec. H.reset -> assets3d_gpu.set_device: CPU unless FOSTER_GPU=1
    finds a GPU (OPTIX > CUDA > HIP > METAL > ONEAPI). On the GPU the CPU only syncs the scene (threads AUTO), OIDN
    runs on the GPU and the adaptive threshold tightens to 0.01 (finals use each pass's gpu_spp)."""
    global DEVICE
    _bpy()
    import assets3d_gpu
    sc = H.reset(res, samples, 'night')
    DEVICE = assets3d_gpu.set_device(bpy, sc)       # idempotent; returns the device string for meta.json
    cy = sc.cycles
    if is_gpu():
        sc.render.threads_mode = 'AUTO'
        if hasattr(cy, 'denoising_use_gpu'):
            cy.denoising_use_gpu = True
    else:
        sc.render.threads_mode = 'FIXED'
        sc.render.threads = THREADS
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.01 if is_gpu() else 0.015
    cy.adaptive_min_samples = 0
    cy.seed = 36
    cy.use_animated_seed = False
    cy.use_light_tree = True
    cy.use_denoising = True
    cy.denoiser = 'OPENIMAGEDENOISE'
    cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    cy.denoising_prefilter = 'ACCURATE'
    cy.max_bounces = 8
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 16
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 0.8
    cy.sample_clamp_indirect = 8.0
    cy.sample_clamp_direct = 0.0
    sc.render.use_persistent_data = True
    sc.render.film_transparent = transparent
    sc.render.filter_size = 1.5
    sc.render.image_settings.compression = 60
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    w = bpy.data.worlds.new('W')
    sc.world = w
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0, 0, 0, 1)
    bg.inputs['Strength'].default_value = 0.0
    return sc


def world_color(c, strength):
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = rgba(c)
    bg.inputs['Strength'].default_value = strength


link = lambda o: B.link(o)  # noqa: E731


def look_at(o, target, roll=0.0):
    d = Vector(target) - o.location
    q = d.to_track_quat('-Z', 'Y')
    o.rotation_euler = q.to_euler()
    if roll:
        o.rotation_euler.rotate_axis('Z', math.radians(roll))


def lamp(name, kind, loc, energy, kelvin=None, color=None, target=None, size=(0.1, 0.1), soft=None, spot=30.0,
         blend=0.3, group='key', shape='RECTANGLE', glossy=True, spread=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    if kelvin:
        ld.use_temperature = True
        ld.temperature = kelvin
        ld.color = (1, 1, 1)
    elif color is not None:
        ld.color = B.hue(color)
    if kind == 'AREA':
        ld.shape = shape
        ld.size, ld.size_y = size
        if spread is not None:
            ld.spread = math.radians(spread)
    if soft is not None:
        ld.shadow_soft_size = soft
    if kind == 'SPOT':
        ld.spot_size = math.radians(spot)
        ld.spot_blend = blend
    o = link(bpy.data.objects.new(name, ld))
    o.location = loc
    if target is not None:
        look_at(o, target)
    o.visible_glossy = glossy
    o['group'] = group
    return o


def camera(name, lens, loc, target, fstop=None, focus=None, res=(W_PX, H_PX), shift=(0.0, 0.0), ortho=None, roll=0.0):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new(name)
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 36.0
    cd.sensor_width = 36.0
    cd.lens = lens
    cd.clip_start = 0.005
    cd.clip_end = 60.0
    cd.shift_x, cd.shift_y = shift
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho      # metres across the larger frame side (height)
    cam = link(bpy.data.objects.new(name, cd))
    cam.location = loc
    look_at(cam, target, roll)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 7
        cd.dof.aperture_rotation = math.radians(12)
        cd.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    sc.camera = cam
    return cam


def to_px(p):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    c = world_to_camera_view(sc, sc.camera, Vector(tuple(float(v) for v in p)))
    return (c.x * sc.render.resolution_x, (1 - c.y) * sc.render.resolution_y)


def px_per_mm_at(p, axis=(1, 0, 0)):
    a = np.array(to_px(p))
    b = np.array(to_px(np.asarray(p, float) + np.asarray(axis, float) * MM))
    return float(np.linalg.norm(b - a))


def place_on_screen(cam, target, want_px):
    """Lens shift so the world point `target` projects to `want_px` (x, y) in the full frame (shift units = the
    larger frame side; +shift_x moves the content left, +shift_y moves it down)."""
    sc = bpy.context.scene
    big = max(sc.render.resolution_x, sc.render.resolution_y)
    for _ in range(8):
        bpy.context.view_layer.update()
        x, y = to_px(target)
        cam.data.shift_x -= (want_px[0] - x) / big
        cam.data.shift_y += (want_px[1] - y) / big
    bpy.context.view_layer.update()
    return to_px(target)


def ray_hit_z(px, z):
    """World point where the camera ray through pixel px meets the plane z."""
    sc = bpy.context.scene
    cam = sc.camera
    a = Vector(screen_point(px, 1.0))
    o = cam.matrix_world.translation
    d = (a - o).normalized()
    t = (z - o.z) / d.z
    return tuple(o + d * t)


# ----------------------------------------------------------------------------- meshes

def smooth_obj(o, angle=35.0):
    me = o.data
    me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
    try:
        me.set_sharp_from_angle(angle=math.radians(angle))
    except Exception:
        pass
    return o


def bevel(o, width, seg=3, angle=35.0, harden=True, clamp=True):
    m = o.modifiers.new('bevel', 'BEVEL')
    m.width = width
    m.segments = seg
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = harden
    m.use_clamp_overlap = clamp
    smooth_obj(o, angle)
    return o


def cut(o, cutter, op='DIFFERENCE'):
    m = o.modifiers.new('bool_' + cutter.name, 'BOOLEAN')
    m.operation = op
    m.solver = 'EXACT'
    m.object = cutter
    cutter.hide_render = True
    cutter.hide_viewport = True
    cutter['role'] = 'cutter'
    return m


def order_mods(o, names_first):
    """Reorder modifiers so the named ones run first (bmesh-free: rebuild via modifier_move_to_index)."""
    for i, n in enumerate(names_first):
        if n in o.modifiers:
            with bpy.context.temp_override(object=o):
                bpy.ops.object.modifier_move_to_index(modifier=n, index=i)


def rrect(w, h, r, n=10):
    """Rounded rectangle outline (CCW), centre 0, as (N, 2)."""
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts)


def prism(name, outline, z0, z1, mat, plane='XY', at=(0, 0, 0), bev=0.0, seg=3, role='prop'):
    """Extrude a 2D outline (N, 2) from z0 to z1. plane: 'XY' (extrude Z), 'XZ' (extrude Y), 'YZ' (extrude X)."""
    import bmesh
    bm = bmesh.new()
    vs = [bm.verts.new((float(x), float(y), z0)) for x, y in outline]
    f = bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=[f])
    if f.normal.z > 0:
        f.normal_flip()
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z1 - z0), verts=nv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if plane == 'XZ':      # outline in (x, z); extrude along y from z0..z1
        for v in bm.verts:
            x, y, z = v.co
            v.co = (x, z, y)
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    elif plane == 'YZ':
        for v in bm.verts:
            x, y, z = v.co
            v.co = (z, x, y)
    bmesh.ops.translate(bm, vec=tuple(at), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = B.bm_obj(name, bm, mat, role=role)
    if bev > 0:
        bevel(o, bev, seg)
    return o


def lathe(name, prof, c, mat, seg=96, role='prop', axis='Z', smooth=True):
    o = B.lathe(name, prof, c, mat, seg=seg, role=role, axis=axis)
    if smooth:
        smooth_obj(o, 40)
    return o


def cylinder(name, c, r, h, mat, axis='Z', seg=64, bev=0.0, bseg=3, r2=None):
    o = B.cyl(name, c, r, h, mat, axis=axis, seg=seg, r2=r2, smooth=False)
    if bev > 0:
        bevel(o, bev, bseg)
    else:
        smooth_obj(o, 40)
    return o


def box(name, c, size, mat, bev=0.0, seg=3, rot=None):
    c = np.asarray(c, float)
    s = np.asarray(size, float) / 2
    o = B.cube(name, c - s, c + s, mat)
    if rot is not None:
        o.data.transform(Matrix.Translation(Vector(-c)))
        o.location = Vector(c)
        o.rotation_euler = tuple(math.radians(a) for a in rot)
    if bev > 0:
        bevel(o, bev, seg)
    return o


def grid_mesh(name, nu, nv, fn, mat, uv=True, smooth=True, role='prop'):
    """Parametric sheet: fn(U, V) -> (nu, nv, 3) world points for U, V in [0, 1] grids."""
    U, V = np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, 1, nv), indexing='ij')
    P = fn(U, V).reshape(-1, 3)
    F = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a = i * nv + j
            F.append((a, a + nv, a + nv + 1, a + 1))
    uvs = np.stack([U.ravel(), V.ravel()], -1) if uv else None
    return B.mesh_from(name, P, F, mat, uv=uvs, smooth=smooth, role=role)


def solidify(o, t, offset=0.0):
    m = o.modifiers.new('solid', 'SOLIDIFY')
    m.thickness = t
    m.offset = offset
    m.use_even_offset = True
    return m


# ============================================================================= shader helpers

def _img(path, noncolor=False):
    im = bpy.data.images.load(path, check_existing=True)
    if noncolor:
        im.colorspace_settings.name = 'Non-Color'
    return im


def tex(g, path, vec=None, noncolor=False, ext='CLIP', interp='Cubic'):
    n = g.n('ShaderNodeTexImage')
    n.image = _img(path, noncolor)
    n.extension = ext
    n.interpolation = interp
    if vec is not None:
        g.put(n.inputs['Vector'], vec)
    return n


def planar(g, co, axes, origin, size):
    """Map object coords to UV: u = (co[a0] - o0) / s0, v = (co[a1] - o1) / s1  (axes like ('x', 'y'))."""
    x, y, z = g.xyz(co)
    comp = dict(x=x, y=y, z=z)
    sign = []
    uu = []
    for k, (ax, o, s) in enumerate(zip(axes, origin, size)):
        neg = ax.startswith('-')
        v = comp[ax.lstrip('-')]
        if neg:
            v = g.m('MULTIPLY', v, -1.0)
        uu.append(g.m('DIVIDE', g.m('SUBTRACT', v, o), s))
        sign.append(neg)
    return g.comb(uu[0], uu[1], 0.0)


def rgb_node(g, c):
    n = g.n('ShaderNodeRGB')
    n.outputs[0].default_value = rgba(c)
    return n.outputs[0]


def mixc(g, fac, a, b):
    return g.mix(fac, a if not isinstance(a, str) else rgba(a), b if not isinstance(b, str) else rgba(b))


def wear_group():
    """S36_Wear: edge wear (bevel-normal mask x noise), cavity dust (AO), fingerprints, micro-scratches.
    In: Color, Roughness, Edge Color, Edge, Dust, Prints, Scratch, Seed, Scale.
    Out: Color, Roughness, Normal (scratch + print micro-normal), EdgeMask, DustMask."""
    ng = bpy.data.node_groups.get('S36_Wear')
    if ng is not None:
        return ng
    ng = bpy.data.node_groups.new('S36_Wear', 'ShaderNodeTree')
    I = ng.interface
    ins = [('Color', 'NodeSocketColor', (0.5, 0.5, 0.5, 1)), ('Roughness', 'NodeSocketFloat', 0.4),
           ('Edge Color', 'NodeSocketColor', (0.6, 0.6, 0.6, 1)), ('Edge', 'NodeSocketFloat', 0.0),
           ('Dust', 'NodeSocketFloat', 0.0), ('Prints', 'NodeSocketFloat', 0.0), ('Scratch', 'NodeSocketFloat', 0.0),
           ('Seed', 'NodeSocketFloat', 0.0), ('Scale', 'NodeSocketFloat', 1.0)]
    for nm, t, dv in ins:
        s = I.new_socket(nm, in_out='INPUT', socket_type=t)
        s.default_value = dv
    for nm, t in [('Color', 'NodeSocketColor'), ('Roughness', 'NodeSocketFloat'), ('Normal', 'NodeSocketVector'),
                  ('EdgeMask', 'NodeSocketFloat'), ('DustMask', 'NodeSocketFloat')]:
        I.new_socket(nm, in_out='OUTPUT', socket_type=t)
    g = B.G(ng)
    gi = g.n('NodeGroupInput')
    go = g.n('NodeGroupOutput')
    GI = {s.name: s for s in gi.outputs}
    GO = {s.name: s for s in go.inputs}
    tc = g.n('ShaderNodeTexCoord').outputs['Object']
    seedv = g.comb(GI['Seed'], g.m('MULTIPLY', GI['Seed'], 1.7), g.m('MULTIPLY', GI['Seed'], 0.6))
    va = g.n('ShaderNodeVectorMath', operation='ADD')
    g.put(va.inputs[0], tc)
    g.put(va.inputs[1], seedv)
    co = g.vscale(va.outputs[0], GI['Scale'])
    geo = g.n('ShaderNodeNewGeometry')
    # (1) edge wear: bevel normal vs shading normal
    bev = g.n('ShaderNodeBevel', samples=6)
    bev.inputs['Radius'].default_value = 0.0008
    dp = g.n('ShaderNodeVectorMath', operation='DOT_PRODUCT')
    g.put(dp.inputs[0], bev.outputs['Normal'])
    g.put(dp.inputs[1], geo.outputs['Normal'])
    e0 = g.mr(g.m('SUBTRACT', 1.0, dp.outputs['Value']), 0.004, 0.06, 0.0, 1.0, smooth=True)
    en = g.noise(co, 400.0, 6.0, 0.62)
    en2 = g.noise(co, 60.0, 3.0, 0.5)
    emask = g.m('MULTIPLY', e0, g.mr(g.m('ADD', g.m('MULTIPLY', en, 0.7), g.m('MULTIPLY', en2, 0.3)), 0.42, 0.62))
    emask = g.m('MINIMUM', g.m('MULTIPLY', emask, GI['Edge']), 1.0)
    # (2) cavity dust + specks + top-facing film
    ao = g.n('ShaderNodeAmbientOcclusion', samples=8, only_local=True)
    ao.inputs['Distance'].default_value = 0.002
    cav = g.mr(ao.outputs['AO'], 0.85, 0.35, 0.0, 1.0, smooth=True)
    specks = g.mr(g.noise(co, 3000.0, 2.0, 0.5), 0.66, 0.74, 0.0, 1.0)
    specks = g.m('MULTIPLY', specks, g.mr(g.noise(co, 80.0, 2.0, 0.5), 0.45, 0.7))
    _, _, nz = g.xyz(geo.outputs['Normal'])
    film = g.m('MULTIPLY', g.mr(nz, 0.5, 0.95), g.mr(g.noise(co, 25.0, 4.0, 0.6), 0.4, 0.75, 0.0, 0.35))
    dmask = g.m('MAXIMUM', g.m('MULTIPLY', cav, 0.85), g.m('MAXIMUM', g.m('MULTIPLY', specks, 0.9), film))
    dmask = g.m('MINIMUM', g.m('MULTIPLY', dmask, GI['Dust']), 1.0)
    # (3) fingerprints: ridged ovals in sparse voronoi cells
    sx, sy, sz = g.xyz(co)
    fco = g.comb(g.m('MULTIPLY', sx, 1.0), g.m('MULTIPLY', sy, 1.35), sz)
    vor = g.n('ShaderNodeTexVoronoi')
    vor.inputs['Scale'].default_value = 28.0
    g.put(vor.inputs['Vector'], fco)
    dcell = g.m('DIVIDE', vor.outputs['Distance'], 28.0)              # metres to the cell's feature point
    warp = g.m('MULTIPLY', g.noise(co, 900.0, 2.0, 0.5), 0.0006)
    ring = g.m('MULTIPLY_ADD', g.m('SINE', g.m('MULTIPLY', g.m('ADD', dcell, warp), 2 * math.pi / 0.00045)), 0.5, 0.5)
    sep = g.n('ShaderNodeSeparateColor')
    g.put(sep.inputs[0], vor.outputs['Color'])
    pick = g.mr(sep.outputs[0], 0.62, 0.66)
    oval = g.mr(dcell, 0.0075, 0.004, 0.0, 1.0, smooth=True)
    fp = g.m('MULTIPLY', g.m('MULTIPLY', oval, pick), g.m('MULTIPLY_ADD', ring, 0.7, 0.3))
    fp = g.m('MULTIPLY', fp, g.mr(g.noise(co, 150.0, 2.0, 0.5), 0.35, 0.6))   # partial, smudged prints
    # (4) micro-scratches: two stretched-noise iso-lines
    def scr(rot):
        x, y, z = g.xyz(co)
        c, s = math.cos(rot), math.sin(rot)
        u = g.m('ADD', g.m('MULTIPLY', x, c), g.m('MULTIPLY', y, s))
        v = g.m('SUBTRACT', g.m('MULTIPLY', y, c), g.m('MULTIPLY', x, s))
        n = g.noise(g.comb(g.m('MULTIPLY', u, 20.0), g.m('MULTIPLY', v, 2000.0), g.m('MULTIPLY', z, 400.0)), 1.0, 1.0, 0.5)
        line = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', n, 0.5)), 0.012, 0.0, 0.0, 1.0)
        return g.m('MULTIPLY', line, g.mr(g.noise(co, 30.0 + rot * 7, 2.0, 0.5), 0.5, 0.62))
    sc_ = g.m('MAXIMUM', scr(0.35), scr(2.1))
    sc_ = g.m('MULTIPLY', sc_, GI['Scratch'])
    # combine
    col = g.mix(emask, GI['Color'], GI['Edge Color'])
    col = g.mix(g.m('MULTIPLY', sc_, 0.35), col, GI['Edge Color'])
    col = g.mix(g.m('MULTIPLY', dmask, 0.8), col, (0.25, 0.22, 0.19, 1.0))
    r = GI['Roughness']
    r = g.m('MULTIPLY', r, g.m('SUBTRACT', 1.0, g.m('MULTIPLY', emask, 0.4)))
    r = g.m('ADD', r, g.m('MULTIPLY', fp, g.m('MULTIPLY', GI['Prints'], 0.15)))
    r = g.m('ADD', r, g.m('MULTIPLY', sc_, 0.18))
    r = g.m('ADD', g.m('MULTIPLY', r, g.m('SUBTRACT', 1.0, dmask)), g.m('MULTIPLY', dmask, 0.95))
    r = g.m('MINIMUM', g.m('MAXIMUM', r, 0.02), 1.0)
    bmp = g.bump(g.m('SUBTRACT', g.m('MULTIPLY', fp, g.m('ABSOLUTE', GI['Prints'])), sc_), 0.25, 0.00001)
    g.put(GO['Color'], col)
    g.put(GO['Roughness'], r)
    g.put(GO['Normal'], bmp)
    g.put(GO['EdgeMask'], emask)
    g.put(GO['DustMask'], dmask)
    return ng


def wear(g, b, color, rough, edge_color, edge=1.0, dust=0.5, prints=0.0, scratch=0.5, seed=0.0, scale=1.0,
         normal_into=None):
    """Insert S36_Wear in front of principled b. color/rough: values or sockets. Returns the group node."""
    wn = g.n('ShaderNodeGroup')
    wn.node_tree = wear_group()
    W = {s.name: s for s in wn.inputs}
    g.put(W['Color'], color if not isinstance(color, str) else rgba(color))
    g.put(W['Roughness'], rough)
    g.put(W['Edge Color'], edge_color if not isinstance(edge_color, str) else rgba(edge_color))
    g.put(W['Edge'], edge)
    g.put(W['Dust'], dust)
    g.put(W['Prints'], prints)
    g.put(W['Scratch'], scratch)
    g.put(W['Seed'], seed)
    g.put(W['Scale'], scale)
    g.put(b.inputs['Base Color'], wn.outputs['Color'])
    g.put(b.inputs['Roughness'], wn.outputs['Roughness'])
    if normal_into is None:
        g.put(b.inputs['Normal'], wn.outputs['Normal'])
    else:
        g.put(normal_into, wn.outputs['Normal'])
    return wn


def pbr(name, base, rough=0.5, metal=0.0, spec=0.5, coat=0.0, coat_rough=0.05, ior=1.5, sss=0.0,
        sss_radius=(1.0, 0.5, 0.3), sss_scale=0.002, sheen=0.0, aniso=0.0, transmission=0.0, thin_film=0.0):
    m, b, g = B.principled(name, base if not isinstance(base, str) else lin(base), rough, metal, spec, coat, coat_rough,
                           sss, sss_radius, sss_scale, sheen, ior, aniso)
    if transmission:
        b.inputs['Transmission Weight'].default_value = transmission
    if thin_film:
        b.inputs['Thin Film Thickness'].default_value = thin_film
        b.inputs['Thin Film IOR'].default_value = 1.38
    return m, b, g


def m_emit(name, color, strength, kelvin=None, light=False):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for nn in list(nt.nodes):
        nt.nodes.remove(nn)
    g = B.G(nt)
    e = g.n('ShaderNodeEmission')
    if kelvin:
        bb = g.n('ShaderNodeBlackbody')
        bb.inputs['Temperature'].default_value = kelvin
        g.put(e.inputs['Color'], bb.outputs[0])
    else:
        e.inputs['Color'].default_value = rgba(color)
    e.inputs['Strength'].default_value = strength
    out = g.n('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], out.inputs[0])
    m.cycles.emission_sampling = 'AUTO' if light else 'NONE'
    m['emit'] = e.name
    return m


def set_emit(m, strength):
    m.node_tree.nodes[m['emit']].inputs['Strength'].default_value = strength


def m_holdout():
    return B.m_holdout()


def m_catcher_dummy():
    return pbr('catcher', '#808080', 0.8)[0]


# ============================================================================= PIL textures

def font(name, px):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONTS, name), int(px))


def _save(im, name, folder=None):
    folder = folder or TEX
    os.makedirs(folder, exist_ok=True)
    p = os.path.join(folder, name)
    im.save(p, optimize=True)
    return p


def cached(name):
    """PIL texture cache: the generated PNG is committed under brand_reels/assets/sirf_36_shots/tex3d so the GPU PC
    needs no fonts / scipy. S36_TEX_FORCE=1 (or `textures`) regenerates."""
    def deco(fn):
        def w(*a, **k):
            p = os.path.join(TEX, name)
            if os.path.exists(p) and not TEX_FORCE:
                return p
            return fn(*a, **k)
        w.__name__ = fn.__name__
        w.tex_name = name
        TEXTURES.append(w)
        return w
    return deco


TEXTURES = []


@cached('dial.png')
def tex_dial(npos=38, size=2048, r_mm=17.5, dial_mm=42.0, digit_mm=2.45):
    """Black counter dial: S, 0..36 around the rim, digits' tops toward the centre, slightly misregistered white."""
    from PIL import Image, ImageDraw
    pxmm = size / dial_mm
    im = Image.new('RGBA', (size, size), (14, 13, 12, 255))
    d = ImageDraw.Draw(im)
    c = size / 2
    d.ellipse([c - 0.6 * pxmm, c - 0.6 * pxmm, c + 0.6 * pxmm, c + 0.6 * pxmm], fill=(60, 58, 55, 255))
    f = font('Poppins-SemiBold.ttf', digit_mm * pxmm * 1.32)
    labels = ['S'] + [str(i) for i in range(37)]
    for k, lab in enumerate(labels[:npos]):
        ang = 2 * math.pi * k / npos         # position k sits at angle ang (texture space, CCW from +y down)
        tw = int(5 * digit_mm * pxmm)
        tile = Image.new('L', (tw, tw), 0)
        td = ImageDraw.Draw(tile)
        bb = td.textbbox((0, 0), lab, font=f)
        tx = (tw - (bb[2] - bb[0])) / 2 - bb[0]
        ty = (tw - (bb[3] - bb[1])) / 2 - bb[1]
        td.text((tx, ty), lab, fill=255, font=f)
        tile = tile.resize((int(tw * 0.62), tw), Image.LANCZOS)    # condensed dial numerals
        col = (236, 230, 220, 255) if lab not in ('S',) else (255, 106, 26, 255)
        if lab in ('0', '36'):
            col = (236, 230, 220, 255)
        layer = Image.new('RGBA', tile.size, col)
        layer.putalpha(tile)
        # tops toward the centre: text upright when read from outside the rim (rotate so 'down' points outward)
        rot = layer.rotate(math.degrees(ang), resample=Image.BICUBIC, expand=True)
        x = c + r_mm * pxmm * math.sin(ang) + 0.04 * pxmm      # print misregistration ~0.04 mm
        y = c + r_mm * pxmm * math.cos(ang) - 0.03 * pxmm
        im.alpha_composite(rot, (int(x - rot.size[0] / 2), int(y - rot.size[1] / 2)))
        # odd/even tick marks between numbers
        a2 = 2 * math.pi * (k + 0.5) / npos
        r0, r1 = (r_mm + 1.45) * pxmm, (r_mm + 1.9) * pxmm
        d.line([(c + r0 * math.sin(a2), c + r0 * math.cos(a2)), (c + r1 * math.sin(a2), c + r1 * math.cos(a2))],
               fill=(150, 145, 138, 255), width=max(1, int(0.12 * pxmm)))
    return _save(im, 'dial.png')


@cached('bezel_ring.png')
def tex_bezel_ring(size=1024):
    """Lens bezel ring face: generic white legends around the ring (worn)."""
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c = size / 2
    rng = np.random.default_rng(3)

    def arc_text(text, r, a_mid, fsize, upright_top=True):
        f = font('Poppins-Medium.ttf', fsize)
        widths = [f.getlength(ch) for ch in text]
        total = sum(widths) * 1.08
        a = a_mid - (total / 2) / r * (1 if upright_top else -1)
        for ch, w in zip(text, widths):
            step = (w * 1.08) / r
            am = a + (step / 2) * (1 if upright_top else -1)
            t = Image.new('L', (int(fsize * 2), int(fsize * 2)), 0)
            ImageDraw.Draw(t).text((fsize * 0.5, fsize * 0.3), ch, fill=255, font=f)
            if upright_top:
                rot = t.rotate(-math.degrees(am), resample=Image.BICUBIC)
                x, y = c + r * math.sin(am), c - r * math.cos(am)
            else:
                rot = t.rotate(-math.degrees(am) + 180, resample=Image.BICUBIC)
                x, y = c + r * math.sin(am), c - r * math.cos(am)
            lay = Image.new('RGBA', rot.size, (232, 228, 220, 255))
            lay.putalpha(rot)
            im.alpha_composite(lay, (int(x - rot.size[0] / 2), int(y - rot.size[1] / 2)))
            a += step * (1 if upright_top else -1)
    arc_text('FOCUS FREE', size * 0.405, 0.0, int(size * 0.052), True)
    arc_text('35 mm  1:5.6', size * 0.37, math.pi, int(size * 0.048), False)
    a = np.array(im).astype(np.float32)
    wear_ = rng.random(a.shape[:2])
    from scipy.ndimage import gaussian_filter
    wear_ = gaussian_filter(wear_, 2.0)
    a[..., 3] *= np.clip((wear_ - 0.38) * 9, 0.25, 1.0)
    return _save(Image.fromarray(a.astype(np.uint8)), 'bezel_ring.png')


# ============================================================================= the camera (shared by counter_macro + cam_hero)
#  Body 118 x 38 x 64 mm. Camera frame: origin bottom centre, +X = the user's right (seen from behind), +Y = the
#  front (lens axis), +Z up. Back face at y = -19 mm, top at z = 64 mm. Upper 20 mm = silver painted top cover.

CAM = dict(L=118.0, D=38.0, Hb=64.0, split=44.0,
           window=(33.0, -9.0), win_r=4.5, dial_r=21.0, dial_txt_r=17.5, npos=38,
           wheel=(49.0, -15.0), wheel_r=8.0, wheel_h=5.0, wheel_z=(58.0, 63.0),
           shutter=(38.0, 9.0), crank=(-44.0, 2.0), led=(18.0, 57.0),
           lens=(-6.0, 27.0), flash=(20.0, 53.0), finder=(-34.0, 53.0))


def mats_camera():
    M = {}
    # black ABS body: stipple + wear (edges get shinier/lighter from handling)
    m, b, g = pbr('abs_black', '#0F0D0C', 0.42, spec=0.5)
    co = g.co('Object')
    stip = g.noise(co, 2600.0, 2.0, 0.6)
    wn = wear(g, b, '#0F0D0C', 0.42, '#3A3633', edge=1.4, dust=0.7, prints=0.4, scratch=0.5, seed=1.0,
              normal_into=None)
    bmp = g.bump(stip, 0.12, 0.00002)
    g.put(bmp.inputs['Normal'] if 'Normal' in bmp.node.inputs else None, None) if False else None
    nb = g.n('ShaderNodeBump')
    nb.inputs['Strength'].default_value = 0.15
    nb.inputs['Distance'].default_value = 0.00002
    g.put(nb.inputs['Height'], stip)
    g.put(nb.inputs['Normal'], wn.outputs['Normal'])
    g.put(b.inputs['Normal'], nb.outputs[0])
    # door seam groove on the back: dark line + dip
    x, y, z = g.xyz(co)
    back = g.mr(y, -0.0186, -0.0189)
    gx = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', g.m('ABSOLUTE', x), 0.0545)), 0.00025, 0.0001, 0.0, 1.0)
    gz = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', z, 0.0035)), 0.00025, 0.0001, 0.0, 1.0)
    gtop = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', z, 0.0425)), 0.0003, 0.0001, 0.0, 1.0)
    seam = g.m('MULTIPLY', back, g.m('MAXIMUM', g.m('MAXIMUM', gx, gz), gtop))
    g.put(b.inputs['Base Color'], g.mix(seam, wn.outputs['Color'], (0.002, 0.002, 0.002, 1)))
    M['abs'] = m
    # silver painted top cover; worn edges show the black plastic
    m, b, g = pbr('paint_silver', '#B8B2AA', 0.28, metal=0.6, coat=0.25, coat_rough=0.12)
    co = g.co('Object')
    flake = g.noise(co, 9000.0, 1.0, 0.5)
    base = g.mix(g.mr(flake, 0.3, 0.7, 0.0, 0.18), rgba('#B8B2AA'), rgba('#CFC9C0'))
    wn = wear(g, b, base, 0.28, '#151210', edge=1.6, dust=0.6, prints=1.0, scratch=1.0, seed=2.0)
    M['silver'] = m
    # leatherette: pebbled voronoi bump
    m, b, g = pbr('leatherette', '#121010', 0.6, spec=0.4, sheen=0.15)
    co = g.co('Object')
    vor = g.n('ShaderNodeTexVoronoi', feature='SMOOTH_F1')
    vor.inputs['Scale'].default_value = 1100.0
    g.put(vor.inputs['Vector'], co)
    wn = wear(g, b, '#121010', 0.6, '#2A2522', edge=0.8, dust=1.0, prints=-0.6, scratch=0.2, seed=3.0)
    nb = g.n('ShaderNodeBump')
    nb.inputs['Strength'].default_value = 0.6
    nb.inputs['Distance'].default_value = 0.00015
    g.put(nb.inputs['Height'], vor.outputs['Distance'])
    g.put(nb.inputs['Normal'], wn.outputs['Normal'])
    g.put(b.inputs['Normal'], nb.outputs[0])
    M['leather'] = m
    # chrome
    m, b, g = pbr('chrome', '#E9E6E1', 0.07, metal=1.0)
    wear(g, b, '#E9E6E1', 0.07, '#F4F2EE', edge=0.5, dust=0.6, prints=1.2, scratch=1.4, seed=4.0)
    M['chrome'] = m
    # brushed alu (crank lever, reflector)
    m, b, g = pbr('alu', '#C8C6C2', 0.2, metal=1.0, aniso=0.5)
    wear(g, b, '#C8C6C2', 0.2, '#DCDAD6', edge=0.6, dust=0.4, prints=0.6, scratch=1.0, seed=5.0)
    M['alu'] = m
    # rubber (eyepiece)
    m, b, g = pbr('rubber', '#0B0A0A', 0.78, spec=0.35, sheen=0.3)
    co = g.co('Object')
    wn = wear(g, b, '#0B0A0A', 0.78, '#1A1817', edge=0.6, dust=1.2, prints=-0.4, scratch=0.0, seed=6.0)
    M['rubber'] = m
    # matte black inner (baffles, slot interiors)
    m, b, g = pbr('black_matte', '#050404', 0.85, spec=0.3)
    M['inner'] = m
    # acrylic magnifier / windows (hairline scratches + dust in the rim)
    m, b, g = pbr('acrylic', '#FFFFFF', 0.03, ior=1.49, transmission=1.0)
    co = g.co('Object')
    wn = wear(g, b, '#FFFFFF', 0.03, '#FFFFFF', edge=0.0, dust=0.0, prints=0.35, scratch=0.7, seed=7.0)   # no AO dust inside glass
    M['acrylic'] = m
    # lens glass with a thin-film coating
    m, b, g = pbr('lens_glass', '#FFFFFF', 0.02, ior=1.52, transmission=1.0, thin_film=380.0)
    M['lens_glass'] = m
    # dial print
    p = tex_dial(CAM['npos'], 2048, CAM['dial_txt_r'], 2 * CAM['dial_r'])
    m, b, g = pbr('dial', '#101010', 0.45, spec=0.4)
    co = g.co('Object')
    R = CAM['dial_r'] * MM
    uv = planar(g, co, ('x', 'y'), (-R, -R), (2 * R, 2 * R))
    t = tex(g, p, uv)
    g.put(b.inputs['Base Color'], t.outputs['Color'])
    g.put(b.inputs['Roughness'], g.mr(g.noise(co, 900.0, 2.0, 0.5), 0.3, 0.7, 0.38, 0.5))
    M['dial'] = m
    # bezel ring legend (lens front ring)
    p = tex_bezel_ring()
    m, b, g = pbr('bezel_ring', '#0E0D0C', 0.35, spec=0.5)
    co = g.co('Object')
    Rr = 13.0 * MM
    uv = planar(g, co, ('-x', '-y'), (-Rr, -Rr), (2 * Rr, 2 * Rr))
    t = tex(g, p, uv)
    wn = wear(g, b, '#0E0D0C', 0.35, '#3A3633', edge=1.2, dust=0.8, prints=0.3, scratch=0.6, seed=8.0)
    g.put(b.inputs['Base Color'], g.mix(t.outputs['Alpha'], wn.outputs['Color'], t.outputs['Color']))
    M['bezel_ring'] = m
    # LED lens (orange transmissive) + its die
    m, b, g = pbr('led_lens', '#FF6A1A', 0.08, ior=1.5, transmission=0.85)
    b.inputs['Base Color'].default_value = rgba('#FF6A1A')
    M['led_lens'] = m
    M['led_die'] = m_emit('led_die', '#FF6A1A', 0.0)
    # orange index paint, white printed arrow
    M['index'] = pbr('index_paint', '#FF6A1A', 0.4)[0]
    M['white_print'] = pbr('white_print', '#E8E4DC', 0.45)[0]
    # flash: reflector, xenon tube, glow emitters
    M['reflector'] = pbr('reflector', '#E0E0E0', 0.12, metal=1.0)[0]
    M['xenon'] = pbr('xenon', '#FFFFFF', 0.02, ior=1.47, transmission=1.0)[0]
    M['flash_emit'] = m_emit('flash_emit', '#FFFFFF', 0.0, kelvin=5600)
    M['glow_emit'] = m_emit('glow_emit', '#FF6A1A', 0.0)
    m, b, g = pbr('fresnel', '#FFFFFF', 0.05, ior=1.49, transmission=1.0)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    ridges = g.m('FRACT', g.m('DIVIDE', z, 0.0006))
    nb = g.n('ShaderNodeBump')
    nb.inputs['Strength'].default_value = 0.9
    nb.inputs['Distance'].default_value = 0.0002
    g.put(nb.inputs['Height'], ridges)
    g.put(b.inputs['Normal'], nb.outputs[0])
    M['fresnel'] = m
    # wheel: ridge tops polished, grooves rougher + dust (radial distance in object space)
    m, b, g = pbr('wheel_abs', '#121010', 0.45, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    rr = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', y, y)))
    top = g.mr(rr, CAM['wheel_r'] * MM - 0.0004, CAM['wheel_r'] * MM - 0.00005)
    rgh = g.m('ADD', g.m('MULTIPLY', top, -0.28), 0.5)
    wn = wear(g, b, '#121010', rgh, '#4A4541', edge=1.2, dust=1.6, prints=0.6, scratch=0.6, seed=9.0)
    g.put(b.inputs['Base Color'], g.mix(g.m('MULTIPLY', top, 0.5), wn.outputs['Color'], rgba('#3A3532')))
    M['wheel'] = m
    return M


def knurl_wheel(name, R, h, n, depth, mat, c, seg_per=10):
    """Horizontal thumb wheel: knurled rim (n ridges), 0.5 mm chamfers, axis Z, centre c = bottom centre."""
    na = n * seg_per
    th = np.linspace(0, 2 * np.pi, na, endpoint=False)
    ph = (th * n / (2 * np.pi)) % 1.0
    prof = np.clip(np.abs(ph - 0.5) * 2.0, 0, 1)              # 0 at groove centre, 1 at ridge centre
    prof = np.clip((prof - 0.25) / 0.5, 0, 1)
    prof = prof * prof * (3 - 2 * prof)
    rr = R - depth * (1 - prof)
    ch = 0.5 * MM
    zs = [0.0, ch * 0.3, ch, h - ch, h - ch * 0.3, h]
    shrink = [ch, ch * 0.45, 0.0, 0.0, ch * 0.45, ch]
    V = []
    for z, s in zip(zs, shrink):
        rz = np.maximum(rr - s, R - depth - s)
        V.append(np.stack([rz * np.cos(th), rz * np.sin(th), np.full(na, z)], -1))
    V = np.concatenate(V)
    F = []
    nz = len(zs)
    for k in range(nz - 1):
        for i in range(na):
            a = k * na + i
            b_ = k * na + (i + 1) % na
            F.append((a, b_, b_ + na, a + na))
    # caps with a recessed hub (turned rings)
    ci = len(V)
    hub = []
    for z, sgn in ((0.0, -1), (h, 1)):
        ring_r = [R - depth - ch - 0.3 * MM, 5.0 * MM, 4.6 * MM, 2.2 * MM, 1.6 * MM, 0.0]
        dz = [0.0, 0.0, -0.25 * MM, -0.25 * MM, 0.15 * MM, 0.35 * MM]
        hub.append((z, sgn, ring_r, dz))
    Vl = list(V)
    for z, sgn, ring_r, dz in hub:
        base = len(Vl)
        rows = []
        for r_, d_ in zip(ring_r, dz):
            if r_ == 0.0:
                rows.append([len(Vl)])
                Vl.append((0.0, 0.0, z + sgn * d_))
            else:
                rows.append(list(range(len(Vl), len(Vl) + na)))
                for t in th:
                    Vl.append((r_ * math.cos(t), r_ * math.sin(t), z + sgn * d_))
        edge = (0 if sgn < 0 else (nz - 1) * na)
        first = [edge + i for i in range(na)]
        allrows = [first] + rows
        for r0, r1 in zip(allrows[:-1], allrows[1:]):
            for i in range(na):
                if len(r1) == 1:
                    f = (r0[i], r0[(i + 1) % na], r1[0])
                else:
                    f = (r0[i], r0[(i + 1) % na], r1[(i + 1) % na], r1[i])
                F.append(f if sgn > 0 else tuple(reversed(f)))
    o = B.mesh_from(name, np.array(Vl) + np.asarray(c), F, mat, smooth=True)
    o.data.transform(Matrix.Translation(Vector(tuple(-np.asarray(c)))))
    o.location = Vector(tuple(c))
    smooth_obj(o, 50)
    return o


def build_camera(M, q=1.0, crank_out=False):
    """Returns dict of parts; rotate parts['wheel'] / parts['dial'] about Z, parts['crank'] (an empty) about Z."""
    C = CAM
    m = lambda v: v * MM  # noqa: E731
    L, D, Hb, sp = C['L'], C['D'], C['Hb'], C['split']
    seg = max(6, int(12 * q))
    P = {}
    out = rrect(m(L), m(D), m(6.0), seg)
    body = prism('body', out, 0.0, m(sp), M['abs'], bev=0.0)
    top = prism('top_cover', out, m(sp), m(Hb), M['silver'], bev=0.0)
    # thumb-wheel pocket (open at the top and the back) + counter window hole + shutter collar hole
    wx, wy = C['wheel']
    pocket = cylinder('cut_pocket', (m(wx), m(wy), m(61.5)), m(C['wheel_r'] + 0.6), m(9.0), M['inner'], seg=64)
    cut(top, pocket)
    winx, winy = C['window']
    hole = cylinder('cut_win', (m(winx), m(winy), m(63.0)), m(5.65), m(6.0), M['inner'], seg=64)
    cut(top, hole)
    flx, flz = C['flash']
    fx2, fz2 = C['finder']
    for nm, (cx_, cz_), (w_, h_) in (('cut_flash', (flx, flz), (22.4, 12.4)), ('cut_finder', (fx2, fz2), (12.4, 9.4))):
        cut(top, box(nm, (m(cx_), m(D / 2 - 3.5), m(cz_)), (m(w_), m(9.0), m(h_)), M['inner']))
    ex_, ez_ = C['finder']
    cut(top, box('cut_eyepiece', (m(ex_), m(-D / 2 + 1.0), m(ez_)), (m(9.6), m(4.0), m(7.0)), M['inner']))
    # parting-line groove between cover and body: the split itself; bevel both
    bevel(body, m(0.9), 3)
    bevel(top, m(0.7), 3)
    P['body'], P['top'] = body, top
    # pocket floor + wall liner (dark plastic)
    cylinder('pocket_floor', (m(wx), m(wy), m(57.6)), m(C['wheel_r'] + 0.6), m(0.4), M['inner'], seg=64)
    # thumb wheel
    wz0, wz1 = C['wheel_z']
    wheel = knurl_wheel('wheel', m(C['wheel_r']), m(wz1 - wz0), 36, m(0.55), M['wheel'], (m(wx), m(wy), m(wz0)),
                        seg_per=max(6, int(10 * q)))
    P['wheel'] = wheel
    # wind-direction arrow printed on the top cover beside the wheel
    arrow = np.array([(0, 0), (2.2, 1.1), (1.4, 1.1), (1.4, 3.4), (0.8, 3.4), (0.8, 1.1), (0.0, 1.1)])
    arrow = np.array([(0, 0), (1.3, 1.3), (0.55, 1.3), (0.55, 3.2), (-0.55, 3.2), (-0.55, 1.3), (-1.3, 1.3)])
    ang = math.radians(-70)
    R2 = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    arr = (arrow @ R2.T) * 1.0 + np.array([wx - 13.5, wy + 4.5])
    prism('arrow', arr * MM, m(Hb), m(Hb + 0.012), M['white_print'])
    # counter window: dark collar + dial + domed magnifier + orange index
    collar = lathe('collar', [(m(4.3), m(60.2)), (m(4.3), m(64.4)), (m(4.6), m(64.75)), (m(5.35), m(64.75)),
                              (m(5.6), m(64.5)), (m(5.6), m(60.2))], (m(winx), m(winy), 0), M['abs'], seg=96)
    P['collar'] = collar
    dial_c = (m(winx), m(winy + C['dial_txt_r']), m(63.15))          # dial face 0.45 mm under the magnifier
    dial = cylinder('dial', (0, 0, 0), m(C['dial_r']), m(0.5), M['dial'], seg=192)
    dial.data.transform(Matrix.Translation((0, 0, -m(0.25))))
    dial.location = dial_c
    # the 38 mm disc is wider than the body is deep: clip it to the inside of the top cover (world-space boolean, so
    # it stays clipped while the dial turns)
    keep = prism('cut_dial_keep', rrect(m(L - 3.0), m(D - 3.0), m(4.5), seg), m(62.0), m(63.6), M['inner'])
    cut(dial, keep, 'INTERSECT')
    P['dial'] = dial
    P['dial_c'] = dial_c
    # dial well: dark floor so the hole reads deep
    cylinder('dial_well', (m(winx), m(winy), m(60.3)), m(4.4), m(0.2), M['inner'], seg=48)
    hd = 1.2            # low magnifier bump (a 2 mm dome total-internally-reflects at this viewing angle)
    rc = (C['win_r'] ** 2 + hd ** 2) / (2 * hd)
    prof = [(0.0, m(63.6))]
    for k in range(1, 17):
        r_ = C['win_r'] * k / 16
        prof.append((m(r_), m(63.6 + hd - (rc - math.sqrt(max(rc * rc - r_ * r_, 0))))))
    prof = [(0.0, m(63.6))] + [(m(C['win_r']), m(63.6))] + list(reversed(prof[1:])) + [(0.0, m(63.6 + hd))]
    prof = [(0.0, m(63.6)), (m(C['win_r']), m(63.6))]
    for k in range(16, -1, -1):
        r_ = C['win_r'] * k / 16
        prof.append((m(r_), m(63.6 + hd - (rc - math.sqrt(max(rc * rc - r_ * r_, 0))))))
    dome = lathe('dome', prof, (m(winx), m(winy), 0), M['acrylic'], seg=128)
    P['dome'] = dome
    tri = np.array([(0.0, 0.0), (0.75, -1.1), (-0.75, -1.1)]) + np.array([winx, winy - 4.75])
    tri = np.array([(0.0, 0.0), (0.55, -0.85), (-0.55, -0.85)]) + np.array([winx, winy - 4.65])
    prism('index', tri * MM, m(64.75), m(64.77), M['index'])
    # shutter button: black collar + chrome cap
    sx, sy = C['shutter']
    lathe('shutter_collar', [(m(4.0), m(63.9)), (m(6.2), m(63.9)), (m(6.2), m(64.6)), (m(5.6), m(65.2)),
                             (m(4.9), m(65.2))], (m(sx), m(sy), 0), M['abs'], seg=96)
    lathe('shutter', [(0.0, m(66.6)), (m(3.6), m(66.45)), (m(4.3), m(66.1)), (m(4.5), m(65.5)), (m(4.5), m(64.6))],
          (m(sx), m(sy), 0), M['chrome'], seg=96)
    # flash-ready LED on the back (below the cover's top edge)
    lx, lz = C['led']
    lathe('led_bezel', [(m(1.25), m(0.0)), (m(1.25), m(0.35)), (m(1.9), m(0.35)), (m(2.05), m(0.0))],
          (0, 0, 0), M['abs'], seg=48)
    led_b = bpy.data.objects['led_bezel']
    led_b.rotation_euler = (math.radians(90), 0, 0)
    led_b.location = (m(lx), m(-D / 2), m(lz))
    led = lathe('led_lens', [(0.0, m(0.95)), (m(0.6), m(0.85)), (m(1.1), m(0.5)), (m(1.25), m(0.0)), (0.0, m(0.0))],
                (0, 0, 0), M['led_lens'], seg=48)
    led.rotation_euler = (math.radians(90), 0, 0)
    led.location = (m(lx), m(-D / 2 - 0.02), m(lz))
    die = box('led_die', (m(lx), m(-D / 2 - 0.25), m(lz)), (m(0.5), m(0.2), m(0.5)), M['led_die'])
    P['led'] = (m(lx), m(-D / 2 - 0.9), m(lz))
    P['led_die'] = die
    # eyepiece (back-left): rubber surround + glass
    fx, fz = C['finder']
    ep = prism('eyepiece', rrect(m(16), m(12), m(3.0), seg), 0.0, m(3.0), M['rubber'], plane='XZ',
               at=(m(fx), m(-D / 2), m(fz)), bev=m(0.8))
    ep.location.y -= m(3.0)
    eg = prism('eyepiece_glass', rrect(m(9), m(6.5), m(1.2), seg), 0.0, m(0.4), M['lens_glass'], plane='XZ',
               at=(m(fx), m(-D / 2 - 2.0), m(fz)))
    box('eyepiece_dark', (m(fx), m(-D / 2 - 0.6), m(fz)), (m(9.5), m(1.0), m(7.0)), M['inner'])
    # front: leatherette panel (lens hole), grip, lens, windows
    lxx, lzz = C['lens']
    panel_out = rrect(m(92), m(36), m(2.0), seg)
    panel = prism('leather_panel', panel_out, 0.0, m(0.5), M['leather'], plane='XZ',
                  at=(m(-9.0), m(D / 2), m(23.0)), bev=m(0.2), seg=2)
    panel.location.y += m(0.0)
    hole2 = cylinder('cut_lenshole', (m(lxx), m(D / 2), m(lzz)), m(14.0), m(6.0), M['inner'], axis='Y', seg=96)
    cut(panel, hole2)
    order_mods(panel, ['bool_cut_lenshole'])
    grip = prism('grip', rrect(m(16), m(40), m(6.0), seg), 0.0, m(4.0), M['abs'], plane='XZ',
                 at=(m(47.0), m(D / 2), m(23.0)), bev=m(1.6), seg=4)
    # lens barrel: bezel ring (legend), barrel step, glass, inner baffles
    lens_c = (m(lxx), m(D / 2), m(lzz))
    lathe('lens_barrel', [(m(14.2), m(0.0)), (m(14.2), m(3.0)), (m(13.6), m(3.6)), (m(13.0), m(3.6)),
                          (m(13.0), m(8.0)), (m(12.6), m(8.4)), (m(9.0), m(8.4)), (m(8.6), m(7.6)), (m(8.0), m(7.6))],
          (0, 0, 0), M['abs'], seg=128).rotation_euler = (math.radians(-90), 0, 0)
    bpy.data.objects['lens_barrel'].location = lens_c
    ring = lathe('bezel_face', [(m(8.6), m(8.42)), (m(12.6), m(8.42))], (0, 0, 0), M['bezel_ring'], seg=128)
    ring.rotation_euler = (math.radians(-90), 0, 0)
    ring.location = lens_c
    # ring texture uses object x/z: bake rotation so object coords = world-aligned
    with bpy.context.temp_override(selected_editable_objects=[ring], active_object=ring, object=ring):
        pass
    baffle = lathe('lens_baffle', [(m(8.0), m(7.6)), (m(7.6), m(5.0)), (m(6.0), m(4.6)), (m(5.6), m(2.0)),
                                   (m(3.5), m(1.5))], (0, 0, 0), M['inner'], seg=96)
    baffle.rotation_euler = (math.radians(-90), 0, 0)
    baffle.location = lens_c
    hl = 1.2
    rc2 = (7.0 ** 2 + hl ** 2) / (2 * hl)
    gp = [(0.0, m(5.0))]
    gp = [(0.0, m(5.4)), (m(7.0), m(5.4))]
    for k in range(12, -1, -1):
        r_ = 7.0 * k / 12
        gp.append((m(r_), m(5.4 + hl - (rc2 - math.sqrt(rc2 * rc2 - r_ * r_)))))
    glass = lathe('lens_glass', gp, (0, 0, 0), M['lens_glass'], seg=128)
    glass.rotation_euler = (math.radians(-90), 0, 0)
    glass.location = lens_c
    P['lens_c'] = lens_c
    # flash window: reflector box + xenon tube + fresnel acrylic; glow / flash emitters behind the fresnel
    flx, flz = C['flash']
    prism('flash_frame', rrect(m(25), m(15), m(1.6), seg), 0.0, m(0.6), M['abs'], plane='XZ',
          at=(m(flx), m(D / 2), m(flz)), bev=m(0.25), seg=2)
    # open-fronted reflector trough (back wall + angled top / bottom wings) around the xenon tube
    box('flash_reflector', (m(flx), m(D / 2 - 4.2), m(flz)), (m(21), m(0.4), m(5)), M['reflector'])
    for sz in (1, -1):
        box(f'flash_wing{sz}', (m(flx), m(D / 2 - 3.0), m(flz + sz * 3.6)), (m(21), m(2.8), m(0.4)), M['reflector'],
            rot=(sz * 35, 0, 0))
    cylinder('xenon', (m(flx), m(D / 2 - 2.6), m(flz)), m(0.9), m(18), M['xenon'], axis='X', seg=32)
    fe = box('flash_emit', (m(flx), m(D / 2 - 2.6), m(flz)), (m(17), m(0.7), m(0.7)), M['flash_emit'])
    ge = box('glow_emit', (m(flx), m(D / 2 - 3.9), m(flz)), (m(19), m(0.2), m(4.5)), M['glow_emit'])
    fr = prism('flash_fresnel', rrect(m(22), m(12), m(1.0), seg), 0.0, m(1.2), M['fresnel'], plane='XZ',
               at=(m(flx), m(D / 2 - 0.2), m(flz)))
    P['flash_c'] = (m(flx), m(D / 2 + 1.0), m(flz))
    P['flash_emit'], P['glow_emit'] = fe, ge
    # viewfinder window (front)
    fx2, fz2 = C['finder']
    prism('finder_frame', rrect(m(14), m(11), m(1.4), seg), 0.0, m(0.6), M['abs'], plane='XZ',
          at=(m(fx2), m(D / 2), m(fz2)), bev=m(0.2), seg=2)
    prism('finder_glass', rrect(m(12), m(9), m(1.0), seg), 0.0, m(0.8), M['lens_glass'], plane='XZ',
          at=(m(fx2), m(D / 2 - 0.3), m(fz2)))
    box('finder_dark', (m(fx2), m(D / 2 - 2.0), m(fz2)), (m(12), m(2.0), m(9)), M['inner'])
    # strap lug on the +X end
    lug = cylinder('lug', (m(L / 2 + 0.8), m(-4.0), m(50.0)), m(2.2), m(3.0), M['abs'], axis='X', seg=32, bev=m(0.4))
    torus_o = B.torus('strap_ring', (m(L / 2 + 2.6), m(-4.0), m(47.5)), m(2.4), m(0.45), M['alu'], axis='Y')
    P['lug'] = (m(L / 2 + 2.6), m(-4.0), m(45.5))
    # rewind crank (empty pivot so it can spin)
    cx, cy = C['crank']
    piv = bpy.data.objects.new('crank_pivot', None)
    link(piv)
    piv.location = (m(cx), m(cy), m(Hb))
    lathe('crank_base', [(m(5.2), m(-0.1)), (m(7.6), m(-0.1)), (m(7.6), m(0.5)), (m(7.1), m(0.8))], (m(cx), m(cy), m(Hb)),
          M['abs'], seg=96)
    kn = knurl_wheel('crank_knob', m(7.0), m(3.4), 48, m(0.3), M['abs'], (0, 0, m(0.6)), seg_per=6)
    kn.parent = piv
    kn.location = (0, 0, m(0.6))
    # fold-out lever: flat alu bar hinged at the knob top, a short peg at its tip
    tilt = math.radians(28 if crank_out else 0)
    lev = box('crank_lever', (m(5.0), 0, 0), (m(11.0), m(3.2), m(0.9)), M['alu'], bev=m(0.3), seg=2)
    lev.location = (m(-0.5), 0, m(4.25))
    lev.rotation_euler = (0, -tilt, 0)
    lev.parent = piv
    peg = cylinder('crank_peg', (0, 0, 0), m(1.5), m(4.5 if crank_out else 1.2), M['abs'], seg=32, bev=m(0.3))
    peg.parent = lev
    peg.location = (m(9.6), 0, m(2.4 if crank_out else 0.9))
    hingepin = cylinder('crank_hinge', (0, 0, 0), m(0.8), m(4.0), M['chrome'], axis='Y', seg=24)
    hingepin.parent = piv
    hingepin.location = (m(-0.5), 0, m(4.25))
    P['crank'] = piv
    P['crank_c'] = (m(cx), m(cy), m(Hb + 4.0))
    P['window_c'] = (m(winx), m(winy), m(64.6))
    P['wheel_c'] = (m(wx), m(wy - C['wheel_r']), m(60.5))
    P['shutter_c'] = (m(sx), m(sy), m(66.0))
    P['body_c'] = (0.0, 0.0, m(Hb / 2))
    return P


def camera_parts_objs():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_render and o.get('role') == 'prop']


def set_counter(P, dial_value, wheel_deg):
    """dial_value 35.0 -> 36.0 rotates the dial one position; wheel_deg rotates the thumb wheel."""
    step = 2 * math.pi / CAM['npos']
    # texture position k sits at angle 2*pi*k/npos measured from +y (texture v down) ; window is at -y of the dial
    # centre, i.e. texture angle pi. Number n has index k = n + 1 ('S' = 0).
    k = dial_value + 1.0
    P['dial'].rotation_euler = (0, 0, -k * step)
    P['wheel'].rotation_euler = (0, 0, math.radians(wheel_deg))


# ============================================================================= home set (R_HOME): sheesham table, doily, dark room, practicals

@cached('doily_alpha.png')
def tex_doily(size=2048, seed=4):
    """Crochet doily: alpha = cotton thread coverage (open-work rings of arches, petals and chain holes)."""
    from PIL import Image
    from scipy.ndimage import gaussian_filter
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    c = (n - 1) / 2
    x, y = (xx - c) / c, (yy - c) / c
    r = np.hypot(x, y)
    a = np.arctan2(y, x)
    cov = np.zeros((n, n), np.float32)
    # centre rosette
    cov += (r < 0.10) * (0.6 + 0.4 * (np.cos(a * 12) > -0.4))
    # rings of thread (concentric chains)
    for r0, w in ((0.11, 0.008), (0.24, 0.010), (0.40, 0.010), (0.58, 0.010), (0.78, 0.012), (0.97, 0.016)):
        cov = np.maximum(cov, np.exp(-((r - r0) / w) ** 2))
    # spokes between rings 0.11-0.24 (24 spokes)
    sp = np.abs(np.sin(a * 12)) < 0.10 * (0.2 / np.maximum(r, 0.05))
    cov = np.maximum(cov, ((r > 0.11) & (r < 0.24) & sp).astype(np.float32))
    # petals ring 0.24-0.40 (16 solid petals)
    pet = ((r - 0.32) / 0.075) ** 2 + (np.sin((a * 16) / 2) / 0.55) ** 2 < 1.0
    cov = np.maximum(cov, pet.astype(np.float32) * 0.95)
    # arches 0.40-0.58 (32 arches)
    t = (a * 32 / (2 * np.pi)) % 1.0
    arch_r = 0.40 + 0.16 * np.sin(np.pi * t)
    cov = np.maximum(cov, np.exp(-((r - arch_r) / 0.008) ** 2) * (r > 0.40))
    # mesh 0.58-0.78: diamond net
    u = (a * 48 / (2 * np.pi)) % 1.0
    v = ((r - 0.58) / 0.05) % 1.0
    net = (np.abs(u - v) < 0.07) | (np.abs(u + v - 1) < 0.07)
    cov = np.maximum(cov, (net & (r > 0.58) & (r < 0.78)).astype(np.float32))
    # scalloped edge 0.78-1.0 (40 shells with picots)
    t2 = (a * 40 / (2 * np.pi)) % 1.0
    shell = (r > 0.78) & (r < 0.80 + 0.17 * np.sin(np.pi * t2))
    holes = ((((t2 - 0.5) / 0.12) ** 2 + ((r - 0.87) / 0.035) ** 2) < 1.0)
    cov = np.maximum(cov, (shell & ~holes).astype(np.float32) * 0.92)
    cov = np.where(r > 1.0, 0.0, cov)
    rng = np.random.default_rng(seed)
    fuzz = gaussian_filter(rng.random((n, n)).astype(np.float32), 1.0)
    cov = gaussian_filter(cov, 1.2)
    alpha = np.clip(cov * 1.25 + (fuzz - 0.5) * 0.35, 0, 1)
    alpha = np.where(alpha < 0.2, 0, alpha)
    im = Image.fromarray((alpha * 255).astype(np.uint8), 'L')
    return _save(im, 'doily_alpha.png')


def mat_sheesham():
    base = '#3A2216'
    m, b, g = pbr('sheesham', base, 0.3, coat=0.65, coat_rough=0.16, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    grain = g.wave(g.comb(g.m('MULTIPLY', x, 0.15), y, g.m('MULTIPLY', z, 1.0)), 6.0, 9.0, 4.0, bands='Y')
    streak = g.noise(g.comb(g.m('MULTIPLY', x, 0.05), g.m('MULTIPLY', y, 2.5), z), 9.0, 5.0, 0.65)
    fine = g.noise(g.comb(g.m('MULTIPLY', x, 0.05), g.m('MULTIPLY', y, 6.0), z), 160.0, 2.0, 0.6)
    k = g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.62, 1.12), g.mr(streak, 0.3, 0.7, 0.55, 1.25))
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', fine, 0.3, 0.85))
    # tea ring
    dx = g.m('SUBTRACT', x, -0.16)
    dy = g.m('SUBTRACT', y, 0.10)
    d = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy)))
    ring = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', d, 0.036)), 0.0025, 0.0004, 0.0, 1.0, smooth=True)
    ring = g.m('MULTIPLY', ring, g.mr(g.noise(co, 40.0, 3.0, 0.5), 0.3, 0.6, 0.4, 1.0))
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', ring, 0.45, 1.0))
    col = g.vscale(rgb_node(g, base), k)
    wn = wear(g, b, col, 0.3, '#5A3A26', edge=0.0, dust=0.35, prints=0.6, scratch=1.2, seed=11.0)
    g.put(b.inputs['Coat Roughness'], g.m('ADD', g.m('MULTIPLY', ring, 0.35), g.mr(fine, 0.3, 0.7, 0.10, 0.22)))
    return m


def mat_doily():
    p = tex_doily()
    m, b, g = pbr('doily', '#E8DCC4', 0.85, spec=0.3, sheen=0.6, sss=0.2, sss_radius=(1.0, 0.9, 0.7), sss_scale=0.001)
    co = g.co('Object')
    R = 0.15
    uv = planar(g, co, ('x', 'y'), (-R, -R), (2 * R, 2 * R))
    t = tex(g, p, uv, noncolor=True, interp='Linear')
    fib = g.noise(co, 1800.0, 4.0, 0.7)
    col = g.vscale(rgb_node(g, '#E8DCC4'), g.mr(fib, 0.3, 0.7, 0.82, 1.04))
    dirt = g.mr(g.noise(co, 18.0, 3.0, 0.6), 0.45, 0.75, 1.0, 0.86)
    col = g.vscale(col, dirt)
    g.put(b.inputs['Base Color'], col)
    g.put(b.inputs['Alpha'], g.mr(t.outputs['Color'] if False else t.outputs['Alpha'] if False else t.outputs[0], 0.25, 0.6))
    nb = g.n('ShaderNodeBump')
    nb.inputs['Strength'].default_value = 0.8
    nb.inputs['Distance'].default_value = 0.0006
    g.put(nb.inputs['Height'], g.m('ADD', t.outputs[0], g.m('MULTIPLY', fib, 0.3)))
    g.put(b.inputs['Normal'], nb.outputs[0])
    return m


def mat_wall_dark():
    m, b, g = pbr('wall_dark', '#2A1A15', 0.9, spec=0.3)
    co = g.co('Object')
    g.put(b.inputs['Base Color'], g.vscale(rgb_node(g, '#2A1A15'), g.mr(g.noise(co, 2.0, 4.0, 0.6), 0.3, 0.7, 0.6, 1.1)))
    return m


def home_set(table_far=0.45, doily=True, table_near=0.6):
    """Table top at z = 0 (sheesham, 1.6 m wide), doily under the origin, back wall 2.6 m away (+Y), floor."""
    S = {}
    tm = mat_sheesham()
    S['table'] = box('table', (0, (table_far - table_near) / 2, -0.0158), (1.6, table_far + table_near, 0.03), tm,
                     bev=0.003)
    if doily:
        d = cylinder('doily', (0, 0, -0.0004), 0.15, 0.0008, mat_doily(), seg=128)
        S['doily'] = d
    wm = mat_wall_dark()
    box('wall', (0, 2.6, 0.6), (6.0, 0.05, 4.0), wm)
    box('floor', (0, 0.8, -0.76), (6.0, 6.0, 0.02), wm)
    return S


def practical(name, loc, radius=0.03, strength=6.0):
    o = B.mesh_from(name, *_uv_sphere(radius), m_emit(name + '_m', None, strength, kelvin=2700, light=True))
    o.location = loc
    o.visible_shadow = False
    return o


def _uv_sphere(r, nu=32, nv=16):
    V = []
    for j in range(nv + 1):
        th = math.pi * j / nv
        for i in range(nu):
            ph = 2 * math.pi * i / nu
            V.append((r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph), r * math.cos(th)))
    F = []
    for j in range(nv):
        for i in range(nu):
            a = j * nu + i
            b_ = j * nu + (i + 1) % nu
            F.append((a, b_, b_ + nu, a + nu))
    return np.array(V), F


def rig_point(subject, cam_loc, az, el, dist):
    """Point at distance `dist` from subject; az 0 = toward the camera, +90 = camera-right, 180 = behind."""
    s = Vector(subject)
    f = (s - Vector(cam_loc))
    f.z = 0
    f.normalize()
    r = Vector((f.y, -f.x, 0.0))          # camera-right on the ground plane
    toward = -f
    a = math.radians(az)
    hdir = toward * math.cos(a) + r * math.sin(a)
    e = math.radians(el)
    return tuple(s + (hdir * math.cos(e) + Vector((0, 0, 1)) * math.sin(e)) * dist)


def r_home(subject, cam_loc, key=40.0, scale=1.0, kelvin=3000):
    """R_HOME: 40 cm key camera-left 45 deg up (tungsten; 3000 K so the silver still reads silver under the Standard
    view), 1 m window fill camera-right at 16 % (4300 K), 2000 K rim strip behind-right (the FLAME edge)."""
    L = []
    L.append(lamp('key', 'AREA', rig_point(subject, cam_loc, -55, 45, 1.1), key, kelvin=kelvin, target=subject,
                  size=(0.4, 0.4), group='key'))
    L.append(lamp('fill', 'AREA', rig_point(subject, cam_loc, 65, 15, 1.4), key * 0.08 * 2.0, kelvin=4300,
                  target=subject, size=(1.0, 1.0), group='key'))
    L.append(lamp('rim', 'AREA', rig_point(subject, cam_loc, 155, 22, 0.8), key * 0.55, kelvin=2000,
                  target=subject, size=(0.1, 0.6), group='key'))
    return L


def screen_point(px, dist):
    """World point at `dist` metres from the scene camera along the ray through pixel px (full-frame px)."""
    sc = bpy.context.scene
    cam = sc.camera
    bpy.context.view_layer.update()
    fr = cam.data.view_frame(scene=sc)          # tr, br, bl, tl in camera space (z = -d)
    tr, br, bl, tl = [Vector(v) for v in fr]
    u = px[0] / sc.render.resolution_x
    v = px[1] / sc.render.resolution_y
    top = tl.lerp(tr, u)
    bot = bl.lerp(br, u)
    p = top.lerp(bot, v)
    d = (cam.matrix_world.to_3x3() @ p).normalized()
    return tuple(cam.matrix_world.translation + d * dist)


# ============================================================================= asset registry + runner

ASSETS = {}


def asset(name, notes=''):
    def deco(fn):
        ASSETS[name] = dict(name=name, build=fn, notes=notes)
        return fn
    return deco


class Pass:
    """One output folder. setup(i) poses frame i; kind 'lit' (denoised, adaptive) or 'flat' (no denoise: masks).
    spp = CPU final samples, gpu_spp = samples when the GPU renders the finals (FOSTER_GPU=1). aux(i) poses an extra
    render of the same frame whose image is handed to post(ims, k, aux) (used to isolate a prop's own contact shadow
    from the room's shadows on a shadow catcher). crop: alpha bbox + 24 px. region: border render (x0, y0, x1, y1)."""

    def __init__(self, folder, n=1, setup=None, kind='lit', spp=64, region=None, crop=False, key=None, labels=None,
                 post=None, transparent=False, mode=None, loop=False, notes='', feats=None, extra=None, seq_preview=None,
                 gpu_spp=None, aux=None):
        self.folder, self.n, self.setup, self.kind, self.spp = folder, n, setup, kind, spp
        self.region, self.crop, self.key, self.labels, self.post = region, crop, key, labels, post
        self.transparent, self.mode, self.loop, self.notes = transparent, mode, loop, notes
        self.feats, self.extra, self.seq_preview = feats, extra or {}, seq_preview
        self.gpu_spp, self.aux = gpu_spp, aux


class Ctx:
    def __init__(self, preview, q):
        self.preview, self.q = preview, q


S_PREVIEW = 16


def pass_spp(P, preview, samples):
    """Samples for one pass: 16 in previews; --samples N overrides lit passes; the GPU table on a GPU; else CPU spp."""
    if P.kind == 'flat':
        return min(P.spp, S_PREVIEW) if preview else (P.gpu_spp if (is_gpu() and P.gpu_spp) else P.spp)
    if preview:
        return S_PREVIEW
    if samples:
        return samples
    if is_gpu() and P.gpu_spp:
        return P.gpu_spp
    return P.spp


def settings(sc, kind, spp):
    cy = sc.cycles
    cy.samples = spp
    if kind == 'flat':
        cy.use_denoising = False
        cy.use_adaptive_sampling = False
    else:
        cy.use_denoising = True
        cy.use_adaptive_sampling = True


def _alpha_bbox(ims, thr=2):
    bb = None
    for im in ims:
        a = im[:, :, 3]
        ys, xs = np.nonzero(a > thr)
        if len(xs) == 0:
            continue
        b = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
    return bb


def cam_meta():
    c = bpy.context.scene.camera
    d = c.data
    out = dict(lens=round(d.lens, 2), type=d.type, sensor_fit=d.sensor_fit, location=[round(v, 5) for v in c.location],
               rotation_deg=[round(math.degrees(v), 3) for v in c.rotation_euler],
               shift=[round(d.shift_x, 5), round(d.shift_y, 5)])
    if d.type == 'ORTHO':
        out['ortho_scale_m'] = round(d.ortho_scale, 5)
    if d.dof.use_dof:
        out['fstop'] = d.dof.aperture_fstop
        out['focus_m'] = round(d.dof.focus_distance, 5)
    return out


def _read4(p):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im.ndim == 2:
        im = np.dstack([im, im, im])
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    return im


def _render(sc, path, skip):
    if skip and os.path.exists(path):
        return None
    t1 = time.time()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return round(time.time() - t1, 1)


def render_asset(name, preview=False, samples=None, only=None, frames=None):
    """Build the asset scene once and render every pass folder. Finals: meta.json is deleted first and written LAST
    per folder (only when every frame is on disk). SKIP_EXISTING=1 keeps the raw frames of an interrupted run
    (same device!) and renders only the missing ones. --frames renders raw frames only (no meta, folder unfinished)."""
    import cv2
    _bpy()
    spec = ASSETS[name]
    q = 0.6 if preview else 1.0
    t0 = time.time()
    S = spec['build'](Ctx(preview, q))
    sc = bpy.context.scene
    glass_no_shadow()
    full = S['res']
    div = int(os.environ.get('S36_PREVIEW_DIV', '2'))          # quick looks: S36_PREVIEW_DIV=4
    res = (full[0] // div, full[1] // div) if preview else tuple(full)
    sc.render.resolution_x, sc.render.resolution_y = res
    bpy.context.view_layer.update()
    k = res[0] / full[0]
    root = PREVIEW if preview else OUT
    skip = os.environ.get('SKIP_EXISTING') == '1' and not preview
    feats_w = S.get('feats', {})
    print(f'[{name}] scene built in {time.time() - t0:.1f}s; {res[0]}x{res[1]}; device {DEVICE}'
          + ('' if is_gpu() else f' x{THREADS} threads'), flush=True)
    results = {}
    for P in S['passes']:
        if only and P.folder not in only:
            continue
        outdir = os.path.join(root, name, P.folder)
        os.makedirs(outdir, exist_ok=True)
        if os.path.exists(os.path.join(outdir, 'meta.json')):
            os.remove(os.path.join(outdir, 'meta.json'))
        for f in os.listdir(outdir):
            if f.endswith('.png') and not (skip and f.startswith('_')):
                os.remove(os.path.join(outdir, f))
        if P.region:
            x0, y0, x1, y1 = [int(round(v * k)) for v in P.region]
            B.set_border(sc, (x0, y0, x1, y1), res)
        else:
            sc.render.use_border = False
            sc.render.use_crop_to_border = False
        idx = list(range(P.n))
        if preview and P.n > 3:
            idx = P.seq_preview if P.seq_preview is not None else sorted({0, P.n // 2, P.n - 1})
        if frames:
            idx = [i for i in idx if i in frames]
        raws, auxs, times, done = {}, {}, {}, {}
        spp = pass_spp(P, preview, samples)
        for i in idx:
            kk = P.key(i) if P.key else i
            if kk in done:
                raws[i], auxs[i] = done[kk]
                continue
            p = os.path.join(outdir, f'_raw_{i:04d}.png')
            pa = os.path.join(outdir, f'_aux_{i:04d}.png') if P.aux else None
            sc.render.film_transparent = P.transparent
            if P.setup:
                P.setup(i)
            settings(sc, P.kind, spp)
            bpy.context.view_layer.update()
            t = _render(sc, p, skip)
            print(f'  {name}/{P.folder}[{i}]: ' + (f'{t}s ({P.kind}, {spp} spp)' if t is not None else 'kept (SKIP_EXISTING)'),
                  flush=True)
            times[i] = t or 0.0
            if P.aux:
                P.aux(i)
                bpy.context.view_layer.update()
                ta = _render(sc, pa, skip)
                times[i] += ta or 0.0
            raws[i], auxs[i] = p, pa
            done[kk] = (p, pa)
        if frames and not preview:
            print(f'  {name}/{P.folder}: raw frames {idx} rendered; folder NOT finished (rerun without --frames, '
                  f'SKIP_EXISTING=1)', flush=True)
            continue
        ims = {i: _read4(p) for i, p in raws.items()}
        aux_ims = {i: _read4(p) for i, p in auxs.items() if p}
        if P.post:
            ims = P.post(ims, k, aux_ims) or ims
        off = [0, 0]
        if P.region:
            off = [int(round(P.region[0] * k)), int(round(P.region[1] * k))]
        if P.crop:
            bb = _alpha_bbox(list(ims.values()))
            pad = int(round(CROP_PAD * k))
            h0, w0 = next(iter(ims.values())).shape[:2]
            cr = [max(0, bb[0] - pad), max(0, bb[1] - pad), min(w0, bb[2] + pad), min(h0, bb[3] + pad)]
            for i in ims:
                ims[i] = ims[i][cr[1]:cr[3], cr[0]:cr[2]]
            off = [off[0] + cr[0], off[1] + cr[1]]
        order = sorted(ims)
        for j, i in enumerate(order):
            cv2.imwrite(os.path.join(outdir, f'{(i if not preview else j):04d}.png'), ims[i],
                        [cv2.IMWRITE_PNG_COMPRESSION, 6])
        for p in set(list(raws.values()) + [a for a in auxs.values() if a]):
            if os.path.exists(p):
                os.remove(p)
        fw = dict(feats_w)
        if P.feats:
            fw.update(P.feats)
        fframe = {kk: [round(v[0] / k, 1), round(v[1] / k, 1)] for kk, v in ((kk, to_px(p)) for kk, p in fw.items())}
        flocal = {kk: [round(v[0] - off[0] / k, 1), round(v[1] - off[1] / k, 1)] for kk, v in fframe.items()}
        size = list(next(iter(ims.values())).shape[1::-1])
        meta = dict(name=name, variant=P.folder, mode=P.mode or ('static' if P.n == 1 else 'anim'), frames=P.n,
                    fps_hint=30, size=size, loop=P.loop, labels=P.labels or [], notes=P.notes or spec['notes'],
                    features=flocal, features_frame=fframe, frame_xy=[round(off[0] / k, 1), round(off[1] / k, 1)],
                    frame_size=list(full), samples=spp, kind=P.kind, transparent=P.transparent,
                    preview=bool(preview), render_seconds=times, device=DEVICE,
                    threads=None if is_gpu() else THREADS, camera=cam_meta(), builder=BUILDER,
                    unique_renders=len(set(raws.values())))
        if preview:
            meta['preview_frames'] = idx
        meta.update(S.get('extra', {}))
        meta.update(P.extra)
        H.write_meta(outdir, **meta)          # LAST: the compositor swaps its stand-in when this appears
        results[P.folder] = meta
        print(f'  -> {outdir} {size} ({len(order)} files) {sum(times.values()):.0f}s', flush=True)
    print(f'[{name}] total {time.time() - t0:.0f}s', flush=True)
    return results


# ----------------------------------------------------------------------------- pass helpers

def glass_no_shadow():
    """Refractive parts (magnifier dome, lens / finder glass, fresnel, PVC, pen barrel...) cast no shadow rays:
    with refractive caustics off Cycles would otherwise leave everything behind glass unlit (the dial under the
    counter magnifier rendered black)."""
    for o in bpy.context.scene.objects:
        if o.type != 'MESH':
            continue
        for slot in o.material_slots:
            m = slot.material
            if m is None or not m.node_tree:
                continue
            for n_ in m.node_tree.nodes:
                if n_.type == 'BSDF_PRINCIPLED' and n_.inputs['Transmission Weight'].default_value > 0.5:
                    o.visible_shadow = False



def scene_meshes():
    return [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE') and o.get('role') != 'cutter']


def scene_lights():
    return [o for o in bpy.context.scene.objects if o.type == 'LIGHT']


def only_visible(keep, hide_others=True, holdout_others=False):
    """Camera sees only `keep` (others still shadow / reflect unless hide_others hides them from render)."""
    keep = set(o.name for o in keep)
    for o in scene_meshes():
        if o.name in keep:
            o.visible_camera = True
            o.is_holdout = False
            o.hide_render = False
        elif holdout_others:
            o.is_holdout = True
        else:
            o.visible_camera = not hide_others


def restore_visibility(state):
    for o in scene_meshes():
        if o.name in state:
            o.visible_camera, o.is_holdout, o.hide_render, o.is_shadow_catcher = state[o.name]


def save_visibility():
    return {o.name: (o.visible_camera, o.is_holdout, o.hide_render, o.is_shadow_catcher) for o in scene_meshes()}


def lights_on(names_or_objs, on=True):
    for o in names_or_objs:
        o = bpy.data.objects[o] if isinstance(o, str) else o
        o.hide_render = not on


def isolate_shadow(ims, k, aux):
    """Prop sprite over a shadow catcher: frame i = prop + every shadow, aux i = the same without the prop. The
    prop's own contact shadow = 1 - (1 - s_with) / (1 - s_without); room shadows (grille, other props) cancel."""
    out = {}
    for i, im in ims.items():
        a1 = im[:, :, 3].astype(np.float32) / 255.0
        a0 = aux[i][:, :, 3].astype(np.float32) / 255.0
        s = np.clip(1.0 - (1.0 - a1) / np.maximum(1.0 - a0, 0.02), 0.0, 1.0)
        s = np.where(a0 > 0.9, 0.0, s)        # already in full shadow: the prop adds nothing measurable
        prop = (im[:, :, 3] >= 250) | (im[:, :, :3].max(2) > 6)      # catcher shadows are pure black
        a = np.where(prop, a1, s)
        rgb = np.where(prop[..., None], im[:, :, :3], np.zeros_like(im[:, :, :3]))
        o = np.dstack([rgb, np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)])
        o[(a < 0.012)] = 0
        out[i] = o
    return out


def projected_bbox(objs, steps=None):
    """Union screen bbox (full-frame px) of objects' evaluated vertices; steps = list of setup callables."""
    dg = bpy.context.evaluated_depsgraph_get()
    bb = None
    for st in (steps or [None]):
        if st:
            st()
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
        for o in objs:
            oe = o.evaluated_get(dg)
            try:
                me = oe.to_mesh()
            except Exception:
                continue
            mw = oe.matrix_world
            step = max(1, len(me.vertices) // 1500)
            pts = [to_px(mw @ v.co) for j, v in enumerate(me.vertices) if j % step == 0]
            oe.to_mesh_clear()
            if not pts:
                continue
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            b = [min(xs), min(ys), max(xs), max(ys)]
            bb = b if bb is None else [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
    return bb


# ============================================================================= counter_macro (S1, S10, S11, cover)

TICK_STEPS = (0, 4, 8, 11)          # ratchet step start frames (SFX clicks)


def tick_pose(i):
    """Frame i of the 16-frame tick: (dial value, wheel degrees). Each step: the wheel turns 90 deg over 3 frames
    (ease-out) after its start frame, then holds; dial follows the wheel gear (35 -> 36); detent overshoot f14."""
    ease = (0.0, 0.42, 0.84, 1.0)
    turn = 0.0
    for s, f0 in enumerate(TICK_STEPS):
        if i >= f0:
            j = min(i - f0, 3)
            turn = 90.0 * (s + ease[j])
    p = turn / 360.0
    dial = 35.0 + p
    if i == 14:
        dial = 36.0 + 0.07
    if i == 13:
        dial = 35.0 + 0.97
    return round(dial, 4), round(turn, 3)


def home_room(practicals):
    for k, (loc, rad, st) in enumerate(practicals):
        practical(f'bulb{k}', loc, rad, st)


def move_led_to(P, px):
    """Slide the flash-ready LED (bezel, lens, die) across the back face so it lands on screen at px."""
    D = CAM['D']
    cam = bpy.context.scene.camera
    a = Vector(screen_point(px, 1.0))
    o = cam.matrix_world.translation
    d = (a - o).normalized()
    yb = -D / 2 * MM
    t = (yb - o.y) / d.y
    hit = o + d * t
    x = min(max(hit.x, -0.050), 0.050)
    z = min(max(hit.z, 0.047), 0.0605)
    dx, dz = x - P['led'][0], z - P['led'][2]
    for nm in ('led_bezel', 'led_lens', 'led_die'):
        ob = bpy.data.objects[nm]
        ob.location.x += dx
        ob.location.z += dz
    P['led'] = (x, P['led'][1], z)
    return P['led']


@asset('counter_macro', 'Top-rear macro of the frame counter: dial 35 in the domed window, the knurled thumb wheel at the '
                        'back-right, flash-ready LED on the back. tick = region render that drops onto the plate.')
def build_counter_macro(ctx):
    sc = reset((W_PX, H_PX), 128)
    M = mats_camera()
    home_set(table_far=0.42, table_near=0.5)
    P = build_camera(M, ctx.q)
    win = Vector(P['window_c'])
    # 35 deg down from behind-right (az 28 deg toward +X from straight behind); 100 mm macro, f/2.8 on the numerals
    el, az, dist = math.radians(35), math.radians(28), 0.172
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam = camera('CAM_MACRO', 100.0, tuple(win + d * dist), tuple(win), fstop=2.8, focus=dist + 0.0012)
    place_on_screen(cam, tuple(win - Vector((0, 0, 0.0017))), (540, 1120))
    bpy.context.view_layer.update()
    move_led_to(P, (250, 1380))
    # R_HOME at macro scale: small soft key (40 cm softbox at 1.1 m), window fill, 2000 K rim behind-right
    L = r_home(tuple(win), cam.location, key=7.0, kelvin=3100)
    L[0].data.spread = math.radians(40)          # low-key: the far end of the top plate falls off into shadow
    L[1].data.energy *= 0.5
    # far practicals: at f/2.8 macro they melt into a soft warm gradient (no distinct balls)
    home_room([(screen_point((180, 260), 1.6), 0.03, 2.5), (screen_point((960, 120), 2.2), 0.03, 2.0)])
    world_color('#170A07', 0.18)
    set_counter(P, 35.0, 0.0)
    led_m = bpy.data.materials['led_die']
    vis0 = save_visibility()

    def plate(i):
        restore_visibility(vis0)
        lights_on(L + [o for o in sc.objects if o.name.startswith('bulb')], True)
        world_color('#170A07', 0.12)
        set_counter(P, 35.0, 0.0)
        set_emit(led_m, 0.0)

    def tick(i):
        plate(i)
        dv, wd = tick_pose(i)
        set_counter(P, dv, wd)

    def tick15(i):
        plate(i)
        set_counter(P, 36.0, 360.0)

    def led(i):
        plate(i)
        for o in scene_meshes():
            if o.name not in ('led_die', 'led_lens'):
                o.is_holdout = True
        lights_on(L + [o for o in sc.objects if o.name.startswith('bulb')], False)
        world_color('#000000', 0.0)
        set_emit(led_m, 40.0)

    feats = dict(window_centre=tuple(win), led=P['led'], wheel_edge=P['wheel_c'], shutter=P['shutter_c'],
                 dial_centre=P['dial_c'])
    passes = [Pass('plate', 1, plate, 'lit', 128, gpu_spp=512, notes='opaque plate, dial at 35, LED off'),
              Pass('tick', 16, tick, 'lit', 96, gpu_spp=384, region=(360, 880, 1080, 1400), key=tick_pose, mode='anim',
                   labels=[f'dial {tick_pose(i)[0]:.2f} wheel {tick_pose(i)[1]:.0f}' for i in range(16)],
                   notes='region x360-1080 y880-1400 of the plate camera (paste at frame_xy); f0 = plate pose; '
                         'ratchet steps start f0/4/8/11, dial lands 36 on f15; held frames are copies',
                   seq_preview=[0, 6, 15]),
              Pass('tick15', 1, tick15, 'lit', 128, gpu_spp=512,
                   notes='full opaque plate with the dial at 36 (cover still; identical to plate except the dial/wheel)'),
              Pass('led', 1, led, 'flat', 16, gpu_spp=64, transparent=True, crop=True,
                   notes='LED emission only (straight alpha), paste at frame_xy, ADD, brightness 0.3-1.0')]
    return dict(res=(W_PX, H_PX), passes=passes, feats=feats,
                extra=dict(px_per_mm_window=round(px_per_mm_at(tuple(win)), 2)))


# ============================================================================= cam_hero (S2, hook B)

@cached('strap_weave.png')
def tex_strap(size=512):
    """Nylon webbing weave height map (tileable)."""
    from PIL import Image
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    n = 32
    u = (xx / size * n) % 1.0
    v = (yy / size * n * 2) % 1.0
    row = (np.floor(yy / size * n * 2) % 2)
    over = np.where(row > 0, np.sin(np.pi * u), np.cos(np.pi * u) ** 2)
    h = 0.55 * over + 0.45 * np.sin(np.pi * v) ** 0.5
    return _save(Image.fromarray((np.clip(h, 0, 1) * 255).astype(np.uint8), 'L'), 'strap_weave.png')


def mat_strap():
    p = tex_strap()
    m, b, g = pbr('strap', '#0E0D0D', 0.62, spec=0.45, sheen=0.12)
    uv = g.uv()
    t = tex(g, p, g.vscale(uv, (1.0, 6.0, 1.0)), noncolor=True, ext='REPEAT', interp='Linear')
    fray = g.mr(g.noise(g.co('Object'), 600.0, 3.0, 0.6), 0.55, 0.8)
    col = g.mix(fray, rgba('#0E0D0D'), rgba('#2B2725'))
    g.put(b.inputs['Base Color'], col)
    g.put(b.inputs['Normal'], g.bump(t.outputs[0], 0.7, 0.0003))
    return m


def strap_ribbon(name, path_pts, width, mat, twist=None):
    """Flat webbing ribbon along a polyline (N, 3) lying with its width roughly horizontal."""
    pts = np.asarray(path_pts, float)
    from scipy.interpolate import splprep, splev
    tck, _ = splprep(pts.T, s=0, k=min(3, len(pts) - 1))
    uu = np.linspace(0, 1, 140)
    c = np.array(splev(uu, tck)).T
    tg = np.gradient(c, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True)
    up = np.array([0, 0, 1.0])
    side = np.cross(tg, up)
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
    if twist is not None:
        nrm = np.cross(side, tg)
        a = np.interp(uu, np.linspace(0, 1, len(twist)), twist)[:, None]
        side = side * np.cos(a) + nrm * np.sin(a)

    def fn(U, V):
        i = np.clip((U * (len(c) - 1)).astype(int), 0, len(c) - 1)
        return c[i] + side[i] * ((V - 0.5) * width)[..., None]
    o = grid_mesh(name, 140, 4, fn, mat)
    solidify(o, 0.0012, 0.0)
    smooth_obj(o, 60)
    return o


@asset('cam_hero', 'The same compact camera, front 3/4 on a crochet doily on the sheesham table; flash / glow passes are '
                   'additive light passes; crank = region sequence of the rewind crank spinning.')
def build_cam_hero(ctx):
    sc = reset((W_PX, H_PX), 128)
    M = mats_camera()
    home_set(table_far=0.6, table_near=0.6)
    P = build_camera(M, ctx.q)
    body = Vector(P['body_c'])
    # camera body sits on the doily, rotated so the lens looks 30 deg off our axis
    yaw = math.radians(30)
    rig = [o for o in sc.objects if o.type in ('MESH', 'EMPTY') and o.name not in ('table', 'doily', 'wall', 'floor')
           and o.parent is None]          # every camera part incl. the boolean cutters (they must turn with it)
    piv = bpy.data.objects.new('cam_root', None)
    link(piv)
    for o in rig:
        o.parent = piv
    piv.rotation_euler = (0, 0, yaw)
    bpy.context.view_layer.update()
    # strap: from the lug out over the doily, frayed end trailing to the table
    lug = piv.matrix_world @ Vector(P['lug'])
    pts = [lug, lug + Vector((0.012, -0.004, -0.02)), lug + Vector((0.03, -0.03, -0.043)),
           Vector((lug.x + 0.07, lug.y - 0.07, 0.0016)), Vector((lug.x + 0.12, lug.y - 0.09, 0.0012)),
           Vector((lug.x + 0.17, lug.y - 0.075, 0.0009))]
    strap_ribbon('strap', [tuple(p) for p in pts], 0.0095, mat_strap(), twist=[1.4, 1.0, 0.3, 0.0, 0.05, 0.0])
    # 70 mm, 10 deg above, f/4 on the lens ring; body centre at (540, 1180), ~760 px wide
    lens_w = piv.matrix_world @ Vector(P['lens_c'])
    body_w = piv.matrix_world @ body
    dist = 0.57
    e = math.radians(10)
    cam_loc = body_w + Vector((0.0, math.cos(e), math.sin(e))) * dist         # in front of the lens side (+Y)
    cam = camera('CAM_HERO', 70.0, tuple(cam_loc), tuple(body_w), fstop=4.0,
                 focus=(lens_w + Vector((0, 0.0084, 0)) - cam_loc).length)
    place_on_screen(cam, tuple(body_w), (540, 1180))
    bpy.context.view_layer.update()
    L = r_home(tuple(body_w), cam.location, key=11.0)
    bulbs = [practical('bulb0', screen_point((190, 420), 2.4), 0.03, 5.0),
             practical('bulb1', screen_point((870, 300), 2.9), 0.03, 4.0),
             practical('bulb2', screen_point((620, 560), 3.4), 0.025, 2.5)]
    world_color('#170A07', 0.25)
    # R_FLASH: 22 x 12 mm area at the flash window, 5600 K, pointing out of the lens side (+Y of the body)
    fl_c = piv.matrix_world @ Vector(P['flash_c'])
    fwd = (piv.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    flash = lamp('flash', 'AREA', tuple(fl_c + fwd * 0.006), 2.2, kelvin=5600, target=tuple(fl_c + fwd * 1.0 + Vector((0, 0, -0.25))),
                 size=(0.022, 0.012), group='flash', spread=80)
    flash.hide_render = True
    fe_m, ge_m = bpy.data.materials['flash_emit'], bpy.data.materials['glow_emit']
    vis0 = save_visibility()
    crank_piv = P['crank']

    def lit(i):
        restore_visibility(vis0)
        lights_on(L + bulbs, True)
        flash.hide_render = True
        world_color('#170A07', 0.25)
        set_emit(fe_m, 0.0)
        set_emit(ge_m, 0.0)
        crank_piv.rotation_euler = (0, 0, 0)

    def flash_pass(i):
        lit(i)
        lights_on(L + bulbs, False)
        world_color('#000000', 0.0)
        flash.hide_render = False
        set_emit(fe_m, 400.0)

    def glow(i):
        lit(i)
        lights_on(L + bulbs, False)
        world_color('#000000', 0.0)
        set_emit(ge_m, 30.0)

    def crank(i):
        lit(i)
        crank_piv.rotation_euler = (0, 0, math.radians(-45.0 * i))

    crank_parts = [o for o in sc.objects if o.name.startswith('crank_')]
    bb = projected_bbox(crank_parts, [lambda a=a: setattr(crank_piv, 'rotation_euler', (0, 0, math.radians(a)))
                                      for a in range(0, 360, 45)])
    crank_piv.rotation_euler = (0, 0, 0)
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    w2, h2 = max(160, (bb[2] - bb[0]) / 2 + 40), max(130, (bb[3] - bb[1]) / 2 + 40)
    region = (int(max(0, cx - w2)), int(max(0, cy - h2)), int(min(W_PX, cx + w2)), int(min(H_PX, cy + h2)))
    region = tuple(v - v % 2 for v in region)
    feats = dict(body_centre=tuple(body_w), lens_centre=tuple(lens_w + fwd * 0.0084), flash_window=tuple(fl_c),
                 crank=tuple(piv.matrix_world @ Vector(P['crank_c'])), shutter=tuple(piv.matrix_world @ Vector(P['shutter_c'])))
    passes = [Pass('lit', 1, lit, 'lit', 128, gpu_spp=512, notes='opaque plate (R_HOME), flash off'),
              Pass('flash', 1, flash_pass, 'lit', 64, gpu_spp=256,
                   notes='R_FLASH only (xenon window lit, spill on doily / table), opaque black; ADD x (1 -> 0, tau 0.12 s)'),
              Pass('glow', 1, glow, 'lit', 32, gpu_spp=128,
                   notes='orange charge glow behind the fresnel only (+ its spill), opaque black; ADD x 0.1-0.6'),
              Pass('crank', 8, crank, 'lit', 64, gpu_spp=256, region=region, mode='anim', loop=True,
                   labels=[f'crank {-45 * i} deg' for i in range(8)],
                   notes=f'region {region} of the lit plate (paste at frame_xy); 45 deg per frame, seamless loop')]
    return dict(res=(W_PX, H_PX), passes=passes, feats=feats,
                extra=dict(px_per_mm_body=round(px_per_mm_at(tuple(body_w)), 2), crank_region=list(region)))


# ============================================================================= canister (S3, S4)
#  135 cartridge, axis +Z, origin at the shell centre. Shell r 12.4 mm, z -21..21; crimped steel caps to +-22;
#  spool end +6 mm top (slot), +4 mm bottom; light-trap spout toward +X on the -Y side with black velvet lips;
#  leader tongue 30 mm out of the slot.

CAN = dict(r=12.4, h=42.0, cap_r=12.95, spout_x=16.4, slot_y=(-11.4, -7.4))


@cached('canister_label.png')
def tex_canister_label(w=2048, h=1104):
    """Printed tinplate wrap (u = angle, v = z). RGBA: alpha 0 = bare tin (DX contacts, scuffs come from the wear
    mask). Own generic layout: yellow field, black bands, a big '36', '135-36', 'ISO 200', no brand."""
    from PIL import Image, ImageDraw
    pxmm = h / CAN['h']
    im = Image.new('RGBA', (w, h), (242, 183, 5, 255))
    d = ImageDraw.Draw(im)
    band = int(5.2 * pxmm)
    d.rectangle([0, 0, w, band], fill=(16, 14, 12, 255))
    d.rectangle([0, h - band, w, h], fill=(16, 14, 12, 255))
    # thin red pinstripes inside the bands' edges + a diagonal orange stripe block on the back
    for yy in (band + int(0.8 * pxmm), h - band - int(1.2 * pxmm)):
        d.rectangle([0, yy, w, yy + int(0.45 * pxmm)], fill=(200, 40, 24, 255))
    for k in range(7):
        x0 = int(w * 0.80) + k * int(3.2 * pxmm)
        d.polygon([(x0, band), (x0 + int(1.6 * pxmm), band), (x0 + int(1.6 * pxmm) - int(9 * pxmm), h - band),
                   (x0 - int(9 * pxmm), h - band)], fill=(236, 110, 20, 255))

    def text_up(txt, fnt, px, cx, cy, col, rot=90, sx=1.0):
        f = font(fnt, px)
        bb = d.textbbox((0, 0), txt, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        t = Image.new('L', (tw + 20, th + 20), 0)
        ImageDraw.Draw(t).text((10 - bb[0], 10 - bb[1]), txt, fill=255, font=f)
        if sx != 1.0:
            t = t.resize((int(t.size[0] * sx), t.size[1]), Image.LANCZOS)
        t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
        lay = Image.new('RGBA', t.size, col)
        lay.putalpha(t)
        im.alpha_composite(lay, (int(cx - t.size[0] / 2), int(cy - t.size[1] / 2)))
    # front face (u ~ 0.25): the big 36 reads along the axis (upright when the cartridge stands)
    text_up('36', 'Poppins-Black.ttf', int(15 * pxmm), w * 0.24, h * 0.47, (16, 14, 12, 255), rot=0, sx=0.9)
    text_up('EXP', 'Poppins-Bold.ttf', int(3.0 * pxmm), w * 0.24, h * 0.47 - 9.8 * pxmm, (16, 14, 12, 255), rot=0)
    text_up('135-36', 'Poppins-Bold.ttf', int(3.2 * pxmm), w * 0.24, h * 0.47 + 9.6 * pxmm, (16, 14, 12, 255), rot=0)
    text_up('ISO 200', 'Poppins-SemiBold.ttf', int(2.8 * pxmm), w * 0.24, h * 0.47 + 13.4 * pxmm, (200, 40, 24, 255), rot=0)
    text_up('COLOR PRINT FILM', 'Poppins-Medium.ttf', int(2.0 * pxmm), w * 0.44, h * 0.5, (16, 14, 12, 255), rot=90)
    text_up('135-36', 'Poppins-Bold.ttf', int(2.6 * pxmm), w * 0.06, h * 0.5, (16, 14, 12, 255), rot=90)
    # band text (white, small)
    text_up('36 EXP  .  ISO 200  .  36 EXP  .  ISO 200', 'Poppins-SemiBold.ttf', int(2.2 * pxmm), w * 0.42, band / 2,
            (240, 236, 228, 255), rot=0)
    # fine-print block (unreadable at this size: 0.7 mm caps)
    rng = np.random.default_rng(5)
    for r_ in range(9):
        y = int(h * 0.30 + r_ * 1.1 * pxmm)
        x = int(w * 0.555)
        while x < w * 0.66:
            ln = int(rng.uniform(0.6, 2.4) * pxmm)
            d.rectangle([x, y, x + ln, y + int(0.55 * pxmm)], fill=(30, 26, 20, 255))
            x += ln + int(0.45 * pxmm)
    # DX contact field: 2 x 12 cells, bare tin (alpha 0) vs black paint
    a = np.array(im)
    x0, x1 = int(w * 0.68), int(w * 0.68 + 7.0 * pxmm)
    y0, y1 = int(band + 1.6 * pxmm), int(h - band - 1.6 * pxmm)
    a[y0:y1, x0:x1, 3] = 0
    pattern = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0]
    cw = (x1 - x0) // 2
    ch = (y1 - y0) // 12
    for k, bit in enumerate(pattern):
        cx_, cy_ = k % 2, k // 2
        if bit:
            a[y0 + cy_ * ch + 2:y0 + (cy_ + 1) * ch - 2, x0 + cx_ * cw + 2:x0 + (cx_ + 1) * cw - 2] = (14, 12, 10, 255)
    return _save(Image.fromarray(a), 'canister_label.png')


@cached('leader_alpha.png')
def tex_leader(w=1280, h=1400):
    """Film leader alpha (u = along the film 0..32 mm from the slot, v = across 35 mm): full width for 9 mm, then the
    tongue (lower 55 %) with a rounded end; KS perforations 2.0 x 2.8 mm, pitch 4.75 mm."""
    from PIL import Image, ImageDraw
    Lmm, Wmm = 32.0, 35.0
    sx, sy = w / Lmm, h / Wmm
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, int(9 * sx), h], fill=255)
    tongue_top = int(Wmm * 0.45 * sy)
    d.rectangle([0, tongue_top, int((Lmm - 6) * sx), h], fill=255)
    d.ellipse([int((Lmm - 12) * sx), tongue_top, int(Lmm * sx), h], fill=255)
    d.polygon([(int(9 * sx), 0), (int(15 * sx), tongue_top), (int(9 * sx), tongue_top)], fill=255)
    x = 1.2
    while x < Lmm - 3:
        for yc in (2.0, Wmm - 2.0):
            if yc < Wmm * 0.45 + 2 and x > 9.5:
                continue
            d.rounded_rectangle([int(x * sx), int((yc - 1.4) * sy), int((x + 2.0) * sx), int((yc + 1.4) * sy)],
                                radius=int(0.5 * sx), fill=0)
        x += 4.75
    return _save(im, 'leader_alpha.png')


def mats_canister():
    M = {}
    p = tex_canister_label()
    m, b, g = pbr('can_label', '#F2B705', 0.32, metal=0.0, coat=0.6, coat_rough=0.15)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    ang = g.n('ShaderNodeMath', operation='ARCTAN2')
    g.put(ang.inputs[0], y)
    g.put(ang.inputs[1], x)
    u = g.m('ADD', g.m('DIVIDE', ang.outputs[0], 2 * math.pi), 0.5)
    v = g.m('DIVIDE', g.m('ADD', z, CAN['h'] / 2 * MM), CAN['h'] * MM)
    t = tex(g, p, g.comb(u, v, 0.0), ext='EXTEND')
    tin = rgba('#C9C6C0')
    # dent by the lip: a shallow dimple (bump) + crushed varnish
    dx = g.m('SUBTRACT', u, 0.93)
    dz = g.m('SUBTRACT', v, 0.72)
    dd = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', g.m('MULTIPLY', dz, 0.55), g.m('MULTIPLY', dz, 0.55))))
    dent = g.mr(dd, 0.035, 0.0, 0.0, 1.0, smooth=True)
    wn = wear(g, b, t.outputs['Color'], 0.32, tin, edge=2.2, dust=0.5, prints=0.8, scratch=1.2, seed=21.0)
    bare = g.m('MAXIMUM', g.m('SUBTRACT', 1.0, t.outputs['Alpha']), wn.outputs['EdgeMask'])
    g.put(b.inputs['Base Color'], g.mix(bare, wn.outputs['Color'], tin))
    g.put(b.inputs['Metallic'], bare)
    g.put(b.inputs['Coat Weight'], g.m('MULTIPLY', g.m('SUBTRACT', 1.0, bare), 0.6))
    g.put(b.inputs['Roughness'], g.m('ADD', wn.outputs['Roughness'], g.m('MULTIPLY', dent, 0.15)))
    g.put(b.inputs['Normal'], g.bump(g.m('SUBTRACT', g.noise(co, 2500.0, 2.0, 0.5), g.m('MULTIPLY', dent, 6.0)), 0.15,
                                     0.0002, wn.outputs['Normal']))
    M['label'] = m
    m, b, g = pbr('can_steel', '#C9C6C0', 0.22, metal=1.0, aniso=0.6)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    rr = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', y, y)))
    rings = g.m('MULTIPLY_ADD', g.m('SINE', g.m('MULTIPLY', rr, 2 * math.pi / 0.00018)), 0.5, 0.5)
    wn = wear(g, b, '#C9C6C0', 0.22, '#E2E0DC', edge=1.0, dust=0.8, prints=1.0, scratch=1.4, seed=22.0)
    g.put(b.inputs['Normal'], g.bump(rings, 0.08, 0.00002, wn.outputs['Normal']))
    tg = g.n('ShaderNodeTangent', direction_type='RADIAL', axis='Z')
    g.put(b.inputs['Tangent'], tg.outputs[0])
    M['steel'] = m
    m, b, g = pbr('spool', '#151313', 0.4, spec=0.5)
    wear(g, b, '#151313', 0.4, '#3A3633', edge=1.0, dust=1.0, prints=0.3, scratch=0.5, seed=23.0)
    M['spool'] = m
    m, b, g = pbr('velvet', '#060505', 1.0, spec=0.2, sheen=1.0)
    b.inputs['Sheen Roughness'].default_value = 0.35
    b.inputs['Sheen Tint'].default_value = rgba('#2A2420')
    M['velvet'] = m
    # film base: translucent grey-brown, glossy emulsion side
    pa = tex_leader()
    m, b, g = pbr('film_base', '#4B3A2E', 0.12, spec=0.6, transmission=0.3, coat=0.4, coat_rough=0.05)
    uv = g.uv()
    t = tex(g, pa, uv, noncolor=True)
    mt = m.node_tree
    tr = g.n('ShaderNodeBsdfTransparent')
    mx = g.n('ShaderNodeMixShader')
    out = [n_ for n_ in mt.nodes if n_.type == 'OUTPUT_MATERIAL'][0]
    g.put(mx.inputs[0], g.mr(t.outputs[0], 0.4, 0.6))
    mt.links.new(tr.outputs[0], mx.inputs[1])
    mt.links.new(b.outputs[0], mx.inputs[2])
    mt.links.new(mx.outputs[0], out.inputs[0])
    M['film'] = m
    M['lint'] = pbr('lint', '#D8D2C8', 0.9, sheen=0.8)[0]
    return M


def build_canister(M, q=1.0, leader_curl=1.0, lie=False):
    """Returns (root empty, parts). root at the shell centre; spin = root.rotation_euler.z."""
    m = lambda v: v * MM  # noqa: E731
    C = CAN
    r, hh = C['r'], C['h'] / 2
    root = bpy.data.objects.new('can_root', None)
    link(root)
    seg = max(48, int(128 * q))
    # shell outline: circle + tangential spout to +X along the -Y side
    th = np.linspace(-math.pi / 2, 3 * math.pi / 2, seg, endpoint=False)
    circ = [(r * math.cos(t), r * math.sin(t)) for t in th]
    outline = [(0.0, -r), (C['spout_x'] - 1.2, -r), (C['spout_x'], -r + 1.2), (C['spout_x'], C['slot_y'][1] + 0.9),
               (C['spout_x'] - 1.6, C['slot_y'][1] + 2.4)]
    # join: from the spout top back onto the circle at the tangent angle
    a_join = math.atan2(C['slot_y'][1] + 2.4, C['spout_x'] - 1.6)
    cpts = [(r * math.cos(t), r * math.sin(t)) for t in np.linspace(max(a_join, -0.2), 3 * math.pi / 2 - 0.02, seg)]
    outline = np.array(outline + cpts) * MM
    shell = prism('can_shell', outline, m(-hh), m(hh), M['label'], bev=m(0.35), seg=3)
    # slot: velvet lips in the spout mouth (two strips) + a dark gap
    sy0, sy1 = C['slot_y']
    box('can_velvet_a', (m(C['spout_x'] - 2.5), m(sy0 + 0.55), 0), (m(5.2), m(1.1), m(2 * hh - 1.0)), M['velvet'])
    box('can_velvet_b', (m(C['spout_x'] - 2.5), m(sy1 - 0.55), 0), (m(5.2), m(1.1), m(2 * hh - 1.0)), M['velvet'])
    cutter = box('cut_slot', (m(C['spout_x'] - 2.0), m((sy0 + sy1) / 2), 0), (m(6.0), m(sy1 - sy0), m(2 * hh - 0.8)),
                 M['spool'])
    cut(shell, cutter)
    order_mods(shell, ['bool_cut_slot'])
    # crimped steel caps (cover the spout too: a lathe for the round part + a flat plate for the spout)
    for sgn in (1, -1):
        z0 = sgn * hh
        prof = [(0.0, z0 + sgn * m(0.55)), (m(4.6), z0 + sgn * m(0.55)), (m(5.0), z0 + sgn * m(0.85)),
                (m(10.6), z0 + sgn * m(0.85)), (m(11.6), z0 + sgn * m(0.65)), (m(12.6), z0 + sgn * m(1.0)),
                (m(C['cap_r']), z0 + sgn * m(0.45)), (m(C['cap_r']), z0 - sgn * m(0.6)), (m(r + 0.08), z0 - sgn * m(0.75))]
        if sgn < 0:
            prof = prof[::-1]
        lathe(f'can_cap{"T" if sgn > 0 else "B"}', prof, (0, 0, 0), M['steel'], seg=seg)
        pl = np.array([(m(4.0), -m(r + 0.5)), (m(C['spout_x'] + 0.3), -m(r + 0.5)), (m(C['spout_x'] + 0.3), m(sy1 + 2.6)),
                       (m(8.0), m(sy1 + 4.0))])
        prism(f'can_capplate{"T" if sgn > 0 else "B"}', pl, z0 - m(0.3) if sgn > 0 else z0 - m(0.55),
              z0 + m(0.55) if sgn > 0 else z0 + m(0.3), M['steel'], bev=m(0.25), seg=2)
    # spool ends: top knob with the rewind slot, bottom stub
    top = cylinder('can_spoolT', (0, 0, m(hh + 0.85 + 3.0)), m(3.7), m(6.0), M['spool'], seg=64, bev=m(0.35))
    cut(top, box('cut_spoolslot', (0, 0, m(hh + 0.85 + 6.0)), (m(8.0), m(1.3), m(2.4)), M['spool']))
    order_mods(top, ['bool_cut_spoolslot'])
    cylinder('can_spoolB', (0, 0, -m(hh + 0.85 + 2.0)), m(3.7), m(4.0), M['spool'], seg=64, bev=m(0.35))
    # leader: emerges from the slot along +X and curls away (film base 0.13 mm)
    ys = (sy0 + sy1) / 2

    def fn(U, V):
        s = U * 32.0
        curl = leader_curl * (0.012 * s * s + 0.0009 * s ** 3)
        x = C['spout_x'] - 2.0 + s
        y = ys - curl
        z = (V - 0.5) * 35.0
        return np.stack([x * MM, y * MM, z * MM], -1)
    lead = grid_mesh('can_leader', 48, 12, fn, M['film'])
    solidify(lead, 0.00013, 0.0)
    # a curl of lint on the velvet
    lint_pts = [(C['spout_x'] - 0.2, sy1 - 0.3, 6.0), (C['spout_x'] + 0.6, sy1 + 0.2, 6.8), (C['spout_x'] + 0.3, sy1 + 0.6, 8.0),
                (C['spout_x'] + 1.0, sy1 + 0.4, 9.1)]
    cu = bpy.data.curves.new('lint', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.00004
    sp = cu.splines.new('POLY')
    sp.points.add(len(lint_pts) - 1)
    for k_, pnt in enumerate(lint_pts):
        sp.points[k_].co = (pnt[0] * MM, pnt[1] * MM, pnt[2] * MM, 1.0)
    lo = link(bpy.data.objects.new('can_lint', cu))
    lo.data.materials.append(M['lint'])
    lo['role'] = 'prop'
    parts = [o for o in bpy.context.scene.objects if o.name.startswith(('can_', 'cut_slot', 'cut_spoolslot', 'cut_dial'))
             and o.parent is None and o is not root and o.name.startswith(('can_', 'cut_slot', 'cut_spoolslot'))]
    for o in parts:
        o.parent = root
    return root, parts


@asset('canister', '135 film cartridge sprite: 16-frame 360 deg spin about its long axis (axis tilted 15 deg toward '
                   'camera), light fixed so label highlights travel. Sharp (no DOF); defocus in comp.')
def build_canister_asset(ctx):
    sc = reset((1080, 1200), 64, transparent=True)
    M = mats_canister()
    root, parts = build_canister(M, ctx.q)
    tilt = bpy.data.objects.new('can_tilt', None)
    link(tilt)
    root.parent = tilt
    tilt.rotation_euler = (math.radians(-15), math.radians(8), 0)
    bpy.context.view_layer.update()
    cam_loc = (0.0, -0.36, 0.012)
    cam = camera('CAM_CAN', 85.0, cam_loc, (0.0, 0.0, 0.0), res=(1080, 1200))
    L = r_home((0, 0, 0), cam_loc, key=30.0)
    world_color('#170A07', 0.4)

    def spin(i):
        root.rotation_euler = (0, 0, 2 * math.pi * i / 16)
    feats = dict(centre=(0.0, 0.0, 0.0))
    passes = [Pass('spin', 16, spin, 'lit', 64, gpu_spp=256, transparent=True, crop=True, mode='spin', loop=True,
                   labels=[f'{22.5 * i:.1f} deg' for i in range(16)],
                   notes='frame i = 22.5 * i deg about the long axis (loops); crop = union bbox + 24 px; '
                         'pivot = features.centre')]
    return dict(res=(1080, 1200), passes=passes, feats=feats,
                extra=dict(px_per_mm=round(px_per_mm_at((0, 0, 0)), 2), pivot_note='features.centre = shell centre'))


# ============================================================================= envelope geometry (studio_counter + envelope)
#  Photo-print envelope 130 x 185 mm, flap side up. Local frame: x right, y up (mouth / flap hinge at +y), z up.
#  bottom panel (z 0) carries the flap; top panel (the face we see, printed) ends 4 mm below the mouth with a thumb
#  notch; prints live between the two.

ENV = dict(w=130.0, h=185.0, flap=45.0, flap_tip=96.0, top_gap=4.0, notch_r=11.0)


@cached('envelope_print.png')
def tex_envelope_print(pxmm=8):
    """Red-ink generic studio box on the top panel + blue ballpoint '36' in the No. box (RGBA overlay)."""
    from PIL import Image, ImageDraw
    w, h = int(ENV['w'] * pxmm), int(ENV['h'] * pxmm)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    red = (170, 34, 28, 255)
    bx0, by0, bx1, by1 = int(17 * pxmm), int(70 * pxmm), int(113 * pxmm), int(150 * pxmm)
    lw = int(0.5 * pxmm)
    d.rectangle([bx0, by0, bx1, by1], outline=red, width=lw)
    d.rectangle([bx0 + int(1.2 * pxmm), by0 + int(1.2 * pxmm), bx1 - int(1.2 * pxmm), by1 - int(1.2 * pxmm)], outline=red,
                width=max(1, lw // 2))

    def ctext(txt, fnt, px, cy, col=red):
        f = font(fnt, px)
        tw = d.textlength(txt, font=f)
        d.text(((w - tw) / 2, cy), txt, fill=col, font=f)
    ctext('PHOTO STUDIO', 'Poppins-Bold.ttf', int(8.5 * pxmm), by0 + int(6 * pxmm))
    ctext('PRINTS  .  NEGATIVES  .  ENLARGEMENTS', 'Poppins-SemiBold.ttf', int(3.2 * pxmm), by0 + int(19 * pxmm))
    d.line([(bx0 + int(4 * pxmm), by0 + int(26 * pxmm)), (bx1 - int(4 * pxmm), by0 + int(26 * pxmm))], fill=red, width=lw)
    f = font('Poppins-SemiBold.ttf', int(4.6 * pxmm))
    for k, lab in enumerate(['No.', 'Name', 'Date']):
        y = by0 + int((33 + k * 15) * pxmm)
        d.text((bx0 + int(5 * pxmm), y), lab, fill=red, font=f)
        d.line([(bx0 + int(24 * pxmm), y + int(5.6 * pxmm)), (bx1 - int(6 * pxmm), y + int(5.6 * pxmm))], fill=red,
               width=max(2, lw // 2))
    ctext('Please check your prints before leaving', 'Poppins-Medium.ttf', int(2.6 * pxmm), by1 + int(4 * pxmm))
    a = np.array(im).astype(np.float32)
    rng = np.random.default_rng(8)
    from scipy.ndimage import gaussian_filter
    wear_ = gaussian_filter(rng.random(a.shape[:2]).astype(np.float32), 3.0)
    wear_ = (wear_ - wear_.mean()) / (wear_.std() + 1e-6)
    a[..., 3] *= np.clip(0.92 + 0.25 * wear_, 0.35, 1.0)
    im = Image.fromarray(a.astype(np.uint8))
    # handwritten blue ballpoint "36" on the No. line, a little tilted, plus a scribbled tick in Name
    pen = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pen)
    fh = font('Caveat-Bold.ttf', int(15 * pxmm))
    pd.text((bx0 + int(34 * pxmm), by0 + int(25 * pxmm)), '36', fill=(28, 44, 140, 235), font=fh)
    pts = [(bx0 + int((30 + 3 * k) * pxmm), by0 + int((48 + 1.6 * math.sin(k * 1.7)) * pxmm)) for k in range(14)]
    pd.line(pts, fill=(28, 44, 140, 210), width=int(0.45 * pxmm), joint='curve')
    pen = pen.rotate(-4, resample=Image.BICUBIC, center=(w / 2, by0 + 40 * pxmm))
    im.alpha_composite(pen)
    return _save(im, 'envelope_print.png')


def mat_kraft(name='kraft', base='#A8794A', inner=False, overlay=None, gum=False):
    m, b, g = pbr(name, base, 0.85, spec=0.35, sheen=0.25)
    co = g.co('Object')
    uv = g.uv()
    fib = g.noise(g.vscale(co, (1.0, 3.0, 1.0)), 1500.0, 4.0, 0.7)
    blot = g.noise(co, 30.0, 4.0, 0.6)
    k = g.m('MULTIPLY', g.mr(fib, 0.3, 0.7, 0.86, 1.08), g.mr(blot, 0.3, 0.7, 0.92, 1.06))
    col = g.vscale(rgb_node(g, base if not inner else '#8E6238'), k)
    if overlay:
        t = tex(g, overlay, uv)
        col = g.mix(t.outputs['Alpha'], col, t.outputs['Color'])
    rough = 0.85
    if gum:
        _, vv, _ = g.xyz(uv)
        gm = g.mr(vv, 0.72, 0.76)
        col = g.mix(g.m('MULTIPLY', gm, 0.6), col, rgba('#C2A060'))
        rough = g.m('SUBTRACT', 0.85, g.m('MULTIPLY', gm, 0.5))
    wn = wear(g, b, col, rough, '#C49A6A', edge=0.6, dust=0.3, prints=0.5, scratch=0.2, seed=31.0 + (5 if inner else 0))
    g.put(b.inputs['Normal'], g.bump(g.m('ADD', fib, g.m('MULTIPLY', blot, 0.3)), 0.35, 0.00004, wn.outputs['Normal']))
    return m


def build_envelope(flap_deg=0.0, prints_inside=True, name='env', q=1.0):
    """Returns (root, parts dict: bottom, top, flap). flap_deg 0 = closed over the top panel, 180 = open flat."""
    E = ENV
    w, h = E['w'] * MM, E['h'] * MM
    root = bpy.data.objects.new(name + '_root', None)
    link(root)
    m_out = mat_kraft(name + '_kraft_out')
    m_in = mat_kraft(name + '_kraft_in', inner=True)
    m_top = mat_kraft(name + '_kraft_top', overlay=tex_envelope_print())
    nu, nv = max(16, int(40 * q)), max(20, int(56 * q))

    def bottom_fn(U, V):
        x = (U - 0.5) * w
        y = (V - 0.5) * h
        z = 0.00015 * np.sin(U * 9.0 + V * 5.0)
        return np.stack([x, y, z], -1)
    bot = grid_mesh(name + '_bottom', nu, nv, bottom_fn, m_in)
    th = (E['h'] - E['top_gap']) * MM
    bulge = 0.0013 if prints_inside else 0.0004

    def top_fn(U, V):
        x = (U - 0.5) * w
        y = -h / 2 + V * th
        bx = np.sin(np.pi * np.clip(U, 0, 1)) ** 0.6
        by = np.sin(np.pi * np.clip(V, 0, 1)) ** 0.5
        z = 0.00025 + bulge * bx * by
        # dog-ear: bottom-right corner lifted and curled
        cu_ = np.clip((U - 0.86) / 0.14, 0, 1) * np.clip((0.10 - V) / 0.10, 0, 1)
        z = z + 0.004 * cu_ ** 2
        # thumb notch dip at the mouth
        return np.stack([x, y, z], -1)
    top = grid_mesh(name + '_top', nu, nv, top_fn, m_top)
    # thumb notch: cut a half-disc out of the top panel's mouth edge
    notch = cylinder('cut_' + name + '_notch', (0, -h / 2 + th, 0.0), E['notch_r'] * MM, 0.02, m_in, seg=48)
    cut(top, notch)
    fl_out = mat_kraft(name + '_flap_out')
    fl_in = mat_kraft(name + '_flap_in', inner=True, gum=True)
    # flap: trapezoid hinged at y = +h/2 on the bottom panel. Two-sided paper: grid faces (normal = inner side) get
    # the inner kraft + gum strip, the solidify shell (material offset 1) the outer kraft.
    fd = E['flap'] * MM
    ang = math.radians(flap_deg)

    def flap_fn(U, V):
        half = (w / 2) - (w - E['flap_tip'] * MM) / 2 * V
        x = (U - 0.5) * 2 * half
        # rounded tip corners: pull the last rows' outer columns inward
        x = x * (1.0 - 0.10 * np.clip((V - 0.82) / 0.18, 0, 1) ** 2 * np.abs(2 * U - 1) ** 4)
        bend = math.sin(ang) * 0.55
        steps = 24
        yy = np.zeros_like(V)
        zz = np.zeros_like(V)
        for s_ in range(steps):
            t = (s_ + 0.5) / steps * V
            a = ang + bend * (t ** 1.5)
            yy = yy + (-np.cos(a)) * (V / steps) * fd
            zz = zz + np.sin(a) * (V / steps) * fd
        y = h / 2 + yy
        vt = np.clip((y + h / 2) / th, 0, 1)
        ut = np.clip(x / w + 0.5, 0, 1)
        rest = 0.00025 + bulge * np.sin(np.pi * ut) ** 0.6 * np.sin(np.pi * vt) ** 0.5 + 0.00035
        kk = max(0.0, math.cos(ang))
        z = zz + rest * kk * np.clip(V * 6, 0, 1) + 0.0002
        return np.stack([x, y, z], -1)
    flap = grid_mesh(name + '_flap', nu, 18, flap_fn, fl_in)
    flap.data.materials.append(fl_out)
    sm = solidify(flap, 0.00012, 0.0)
    sm.material_offset = 1
    sm.material_offset_rim = 1
    for o in (bot, top):
        solidify(o, 0.00012, 0.0)
    parts = dict(bottom=bot, top=top, flap=flap)
    for o in (bot, top, flap, notch):
        o.parent = root
    return root, parts


# ============================================================================= studio_counter (S4)

@cached('receipt.png')
def tex_receipt(pxmm=8):
    """Carbon-copy receipt book top sheet: ruled form in blue, carbon handwriting scribbles, smudges. Nothing legible."""
    from PIL import Image, ImageDraw, ImageFilter
    w, h = 100 * pxmm, 150 * pxmm
    im = Image.new('RGB', (w, h), (233, 226, 210))
    d = ImageDraw.Draw(im)
    blue = (70, 92, 160)
    d.rectangle([6 * pxmm, 6 * pxmm, w - 6 * pxmm, 20 * pxmm], outline=blue, width=3)
    for k in range(5):
        x = int((10 + k * 17) * pxmm)
        d.rectangle([x, 9 * pxmm, x + int(11 * pxmm), 11 * pxmm], fill=blue)     # header "type" as bars
    for k in range(13):
        y = int((28 + k * 8.5) * pxmm)
        d.line([(6 * pxmm, y), (w - 6 * pxmm, y)], fill=(150, 160, 200), width=2)
    d.line([(70 * pxmm, 24 * pxmm), (70 * pxmm, 136 * pxmm)], fill=(150, 160, 200), width=2)
    rng = np.random.default_rng(12)
    ink = Image.new('L', (w, h), 0)
    di = ImageDraw.Draw(ink)
    for row in range(9):
        y0 = (34 + row * 8.5) * pxmm
        x = 9 * pxmm
        x_end = rng.uniform(35, 66) * pxmm
        pts = []
        while x < x_end:
            pts.append((x, y0 + rng.uniform(-1.6, 1.0) * pxmm))
            x += rng.uniform(0.5, 1.4) * pxmm
            if rng.random() < 0.12:
                di.line(pts, fill=255, width=int(0.35 * pxmm), joint='curve') if len(pts) > 1 else None
                pts = []
                x += rng.uniform(1.5, 3) * pxmm
        if len(pts) > 1:
            di.line(pts, fill=255, width=int(0.35 * pxmm), joint='curve')
        xn = 74 * pxmm
        pts = [(xn + k * 1.2 * pxmm, y0 + rng.uniform(-1.2, 0.8) * pxmm) for k in range(int(rng.uniform(5, 14)))]
        di.line(pts, fill=255, width=int(0.35 * pxmm), joint='curve')
    ink = ink.filter(ImageFilter.GaussianBlur(1.2))
    a = np.array(im).astype(np.float32)
    k_ = np.array(ink).astype(np.float32)[..., None] / 255.0
    a = a * (1 - k_ * 0.8) + np.array([40, 60, 150], np.float32) * k_ * 0.8
    from scipy.ndimage import gaussian_filter
    sm = gaussian_filter(rng.random((h // 8, w // 8)).astype(np.float32), 3)
    sm = np.kron(sm, np.ones((8, 8), np.float32))[:h, :w]
    sm = np.clip((sm - 0.55) * 4, 0, 0.35)[..., None]
    a = a * (1 - sm) + np.array([90, 105, 175], np.float32) * sm
    return _save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), 'receipt.png')


def mat_laminate():
    base = '#6A4329'
    m, b, g = pbr('laminate', base, 0.35, spec=0.5, coat=0.35, coat_rough=0.2)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    grain = g.wave(g.comb(g.m('MULTIPLY', x, 1.0), g.m('MULTIPLY', y, 0.08), z), 9.0, 7.0, 4.0, bands='X')
    fine = g.noise(g.comb(g.m('MULTIPLY', x, 8.0), g.m('MULTIPLY', y, 0.25), z), 90.0, 3.0, 0.6)
    k = g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.72, 1.12), g.m('MULTIPLY_ADD', fine, 0.3, 0.85))
    rings = 0.0
    for cx_, cy_, r_ in ((0.10, 0.18, 0.034), (-0.05, -0.12, 0.036)):
        dx, dy = g.m('SUBTRACT', x, cx_), g.m('SUBTRACT', y, cy_)
        d = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy)))
        ring = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', d, r_)), 0.003, 0.0005, 0.0, 1.0, smooth=True)
        ring = g.m('MULTIPLY', ring, g.mr(g.noise(co, 30.0, 3.0, 0.5), 0.3, 0.65, 0.15, 0.6))
        rings = ring if rings == 0.0 else g.m('MAXIMUM', rings, ring)
    k = g.m('MULTIPLY', k, g.m('SUBTRACT', 1.0, g.m('MULTIPLY', rings, 0.35)))
    col = g.vscale(rgb_node(g, base), k)
    wn = wear(g, b, col, 0.35, '#8A6040', edge=0.5, dust=0.6, prints=0.8, scratch=1.6, seed=41.0)
    g.put(b.inputs['Coat Roughness'], g.m('ADD', 0.18, g.m('MULTIPLY', rings, 0.3)))
    return m


def build_counter_set(q=1.0):
    S = {}
    top = box('counter', (0.0, 0.0, -0.015), (0.70, 1.20, 0.03), mat_laminate(), bev=0.0015)
    groove = cylinder('cut_groove', (-0.170, 0.0, 0.0035), 0.0075, 1.3, mat_laminate(), axis='Y', seg=48)
    cut(top, groove)
    order_mods(top, ['bool_cut_groove'])
    S['counter'] = top
    # cheap ballpoint in the groove: clear hex barrel, blue ink tube, blue cap
    pen_root = bpy.data.objects.new('pen_root', None)
    link(pen_root)
    acr = pbr('pen_barrel', '#FFFFFF', 0.08, ior=1.49, transmission=1.0)[0]
    capm, cb, cg = pbr('pen_cap', '#1D3FA8', 0.3, spec=0.5)
    wear(cg, cb, '#1D3FA8', 0.3, '#5070C0', edge=1.0, dust=0.5, prints=0.5, scratch=0.8, seed=42.0)
    inkm = pbr('pen_ink', '#1A2A80', 0.4)[0]
    for o in (cylinder('pen_barrel', (0, 0, 0), 0.0036, 0.128, acr, axis='Y', seg=6, bev=0.0004),
              cylinder('pen_ink', (0, 0.004, 0), 0.0011, 0.12, inkm, axis='Y', seg=16),
              cylinder('pen_cap', (0, 0.064, 0), 0.0042, 0.032, capm, axis='Y', seg=24, bev=0.0006),
              cylinder('pen_tip', (0, -0.068, 0), 0.0016, 0.01, pbr('pen_tipm', '#C8C6C0', 0.2, metal=1.0)[0], axis='Y',
                       seg=16, r2=0.0005)):
        o.parent = pen_root
    pen_root.location = (-0.170, 0.12, 0.0004)
    pen_root.rotation_euler = (0, 0, math.radians(1.5))
    # receipt book (top-left): pad + top sheet with a lifted corner + blue carbon sheet peeking out
    paper = pbr('paper_edge', '#E4DCC8', 0.85, spec=0.3)[0]
    rm, rb, rg = pbr('receipt', '#E9E2D2', 0.8, spec=0.3)
    t = tex(rg, tex_receipt(), rg.uv())
    wear(rg, rb, t.outputs['Color'], 0.8, '#F2ECDD', edge=0.0, dust=0.3, prints=0.6, scratch=0.1, seed=43.0)
    carb = pbr('carbon', '#1F2F7A', 0.45, spec=0.5)[0]
    bk_root = bpy.data.objects.new('book_root', None)
    link(bk_root)
    pad = box('book_pad', (0, 0, 0.0035), (0.1, 0.15, 0.007), paper, bev=0.0006)
    cover = box('book_cover', (0, 0, 0.0002), (0.104, 0.154, 0.0006), pbr('book_cover', '#3C4A2A', 0.6)[0], bev=0.0002)
    car = box('book_carbon', (0.004, -0.004, 0.0071), (0.1, 0.15, 0.0001), carb)

    def sheet_fn(U, V):
        x = (U - 0.5) * 0.1
        y = (V - 0.5) * 0.15
        lift = np.clip((U - 0.7) / 0.3, 0, 1) * np.clip((0.3 - V) / 0.3, 0, 1)
        z = 0.0073 + 0.009 * lift ** 2
        return np.stack([x, y, z], -1)
    sh = grid_mesh('book_sheet', 24, 32, sheet_fn, rm)
    solidify(sh, 0.0001)
    for o in (pad, cover, car, sh):
        o.parent = bk_root
    bk_root.location = (-0.105, 0.255, 0.0)
    bk_root.rotation_euler = (0, 0, math.radians(7))
    # stamp pad tin (bottom-right): base with violet felt, open lid hinged behind it
    tinm, tb, tg = pbr('stamp_tin', '#8C8A84', 0.3, metal=1.0)
    wear(tg, tb, '#8C8A84', 0.3, '#B8B6B0', edge=1.4, dust=0.6, prints=0.8, scratch=1.5, seed=44.0)
    feltm, fb, fg = pbr('felt', '#4B2A6B', 0.75, spec=0.4, sheen=0.4)
    fco = fg.co('Object')
    wet = fg.mr(fg.noise(fco, 40.0, 3.0, 0.6), 0.45, 0.7)
    fg.put(fb.inputs['Base Color'], fg.mix(wet, rgba('#4B2A6B'), rgba('#2A1240')))
    fg.put(fb.inputs['Roughness'], fg.mr(wet, 0.0, 1.0, 0.8, 0.35))
    fg.put(fb.inputs['Normal'], fg.bump(fg.noise(fco, 1500.0, 3.0, 0.7), 0.4, 0.0002))
    sp_root = bpy.data.objects.new('stamp_root', None)
    link(sp_root)
    base_ = prism('stamp_base', rrect(0.11, 0.07, 0.006, 8), 0.0, 0.011, tinm, bev=0.0008)
    inner = prism('cut_stamp_in', rrect(0.104, 0.064, 0.005, 8), 0.004, 0.02, tinm)
    cut(base_, inner)
    order_mods(base_, ['bool_cut_stamp_in'])
    felt = prism('stamp_felt', rrect(0.102, 0.062, 0.0045, 8), 0.004, 0.0085, feltm, bev=0.0008)
    lid = prism('stamp_lid', rrect(0.112, 0.072, 0.0065, 8), 0.0, 0.006, tinm, bev=0.0008)
    lidcut = prism('cut_stamp_lid', rrect(0.106, 0.066, 0.0055, 8), 0.0008, 0.02, tinm)
    cut(lid, lidcut)
    order_mods(lid, ['bool_cut_stamp_lid'])
    lid.location = (0.0, 0.0725, 0.0)
    for o in (base_, inner, felt, lid, lidcut):
        o.parent = sp_root
    sp_root.location = (0.13, -0.315, 0.0)
    sp_root.rotation_euler = (0, 0, math.radians(-12))
    return S


@asset('studio_counter', 'Overhead plate of the photo-studio counter (laminate, pen groove, receipt book, stamp pad) in '
                         'three light states + the lying canister and the envelope as shadow-catcher sprites in the '
                         'same camera.')
def build_studio_counter(ctx):
    sc = reset((W_PX, H_PX), 64)
    S = build_counter_set(ctx.q)
    cam = camera('CAM_COUNTER', 100.0, (0.0, 0.0, 2.2), (0.0, 0.0, 0.0), fstop=8.0, focus=2.2)
    bpy.context.view_layer.update()
    # props that land: canister (380, 1180) on its side, leader out; envelope (620, 1210), rot -8 deg
    Mc = mats_canister()
    can_root, can_parts = build_canister(Mc, ctx.q)
    lie = bpy.data.objects.new('can_lie', None)
    link(lie)
    can_root.parent = lie
    tin_xy = ray_hit_z((380, 1180), 0.0)
    lie.location = (tin_xy[0], tin_xy[1], CAN['cap_r'] * MM)
    lie.rotation_euler = (math.radians(90), 0, math.radians(28))
    lead = bpy.data.objects['can_leader']
    best = None
    for a in range(0, 360, 10):
        can_root.rotation_euler = (0, 0, math.radians(a))
        bpy.context.view_layer.update()
        zmin = min((lead.matrix_world @ v.co).z for v in lead.data.vertices)
        if zmin >= 0.0002 and (best is None or zmin < best[1]):
            best = (a, zmin)
    can_root.rotation_euler = (0, 0, math.radians(best[0] if best else 0))
    env_xy = ray_hit_z((620, 1210), 0.0)
    env_root, env_parts = build_envelope(0.0, True, 'cenv', ctx.q)
    env_root.location = (env_xy[0], env_xy[1], 0.0002)
    env_root.rotation_euler = (0, 0, math.radians(-8))
    bpy.context.view_layer.update()
    can_objs = [o for o in sc.objects if o.name.startswith('can_') and o.type in ('MESH', 'CURVE')]
    env_objs = [o for o in env_parts.values()]
    # R_COUNTER: day1 sun through a window grille from the left, day2 low sun through a door from the right,
    # night = one darkroom safelight
    wallm = pbr('room_wall', '#CFC4B0', 0.9)[0]
    barm = pbr('grille', '#1E1A16', 0.5, metal=0.6)[0]
    wx = -0.62
    for c, s_ in (((wx, 0.0, 0.12), (0.06, 3.0, 0.24)), ((wx, 0.0, 1.55), (0.06, 3.0, 0.9)),
                  ((wx, 1.05, 0.65), (0.06, 1.5, 1.2)), ((wx, -1.12, 0.65), (0.06, 1.5, 1.2))):
        box('wallL', c, s_, wallm)
    for k in range(6):
        box(f'barV{k}', (wx, -0.33 + k * 0.105, 0.65), (0.014, 0.014, 0.85), barm)
    for zz in (0.42, 0.82):
        box(f'barH{zz}', (wx, -0.05, zz), (0.014, 0.75, 0.014), barm)
    dx = 0.80
    for c, s_ in (((dx, 0.85, 1.0), (0.06, 1.2, 2.4)), ((dx, -0.95, 1.0), (0.06, 1.2, 2.4)), ((dx, 0.0, 2.15), (0.06, 1.0, 0.3))):
        box('wallR', c, s_, wallm)
    def sun_dir(az, el):          # unit vector from the counter toward the sun; az from +X (screen right), CCW
        return Vector((math.cos(math.radians(el)) * math.cos(math.radians(az)),
                       math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))))
    sun1 = lamp('sun_day1', 'SUN', tuple(sun_dir(166, 35) * 3.0), 2.6, kelvin=4800)      # from the left, window grille
    look_at(sun1, (0.0, 0.0, 0.0))
    sun1.data.angle = math.radians(1.5)
    sun2 = lamp('sun_day2', 'SUN', tuple(sun_dir(-8, 14) * 3.0), 3.0, kelvin=3200)       # low, from the right (door)
    look_at(sun2, (0.0, 0.0, 0.0))
    sun2.data.angle = math.radians(1.0)
    bounce = lamp('bounce', 'AREA', (0.0, 0.0, 1.7), 30.0, kelvin=3000, target=(0, 0, 0), size=(1.4, 1.4), glossy=False)
    safe = lamp('safelight', 'POINT', (0.42, 0.30, 0.80), 9.0, color=TOK['EMBER'], soft=0.10)
    safe.data.color = lin('#B3120E')
    states = dict(day1=([sun1, bounce], 0.30, '#C9B79C'), day2=([sun2, bounce], 0.22, '#D8B48A'),
                  night=([safe], 0.008, '#B3120E'))
    all_l = [sun1, sun2, bounce, safe]
    vis0 = save_visibility()
    counter = S['counter']

    def light_state(st):
        ls, wst, wc = states[st]
        lights_on(all_l, False)
        lights_on(ls, True)
        bounce.data.energy = 16.0 if st == 'day1' else 12.0
        world_color(wc, wst)

    def plate(st):
        def f(i):
            restore_visibility(vis0)
            for o in can_objs + env_objs:
                o.hide_render = True
            counter.is_shadow_catcher = False
            light_state(st)
        return f

    def sprite(st, objs):
        def f(i):
            restore_visibility(vis0)
            for o in can_objs + env_objs:
                o.hide_render = o not in objs
            for o in scene_meshes():
                if o not in objs and o is not counter:
                    o.visible_camera = False
                    if not o.name.startswith(('wall', 'bar')):
                        o.hide_render = True      # other props off: only the room (walls, grille) shapes the light
            counter.is_shadow_catcher = True
            light_state(st)

        def aux(i):
            for o in objs:
                o.hide_render = True
        return f, aux

    passes = []
    for st, nm in (('day1', 'sun shaft through the window grille from the left (4800 K, el 35)'),
                   ('day2', 'low warm sun from the right through the door (3200 K, el 14), long shadows'),
                   ('night', 'one deep-red darkroom safelight above-right, everything else dark')):
        passes.append(Pass(st, 1, plate(st), 'lit', 64, gpu_spp=512, notes=f'opaque plate: {nm}'))
    for st in ('day1', 'day2', 'night'):
        f, a = sprite(st, can_objs)
        passes.append(Pass(f'tin_{st}', 1, f, 'lit', 64, gpu_spp=384, transparent=True, crop=True, aux=a,
                           post=isolate_shadow, notes=f'canister lying (leader out) + its own contact shadow, {st} light; '
                                                      'paste at frame_xy over the plate'))
    f, a = sprite('night', env_objs)
    passes.append(Pass('envelope_night', 1, f, 'lit', 64, gpu_spp=384, transparent=True, crop=True, aux=a,
                       post=isolate_shadow, notes='closed envelope (rot -8 deg) + its own shadow under the safelight'))
    feats = dict(tin=(tin_xy[0], tin_xy[1], 0.0), envelope=(env_xy[0], env_xy[1], 0.0))
    return dict(res=(W_PX, H_PX), passes=passes, feats=feats,
                extra=dict(px_per_mm=round(px_per_mm_at((0, 0, 0)), 3)))


# ============================================================================= R_TABLE (top-down paper props)

def r_table(subject=(0, 0, 0), key=60.0, streak_rot=35.0, streak=6.0, streak_pos=(0.0, 0.0), kelvin=3200):
    s = Vector(subject)
    L = [lamp('table_key', 'AREA', tuple(s + Vector((-0.5, 0.18, 0.87))), key, kelvin=kelvin, target=tuple(s), size=(0.6, 0.6))]
    card = B.mesh_from('bounce_card', np.array([(-0.2, -0.4, 0), (0.2, -0.4, 0), (0.2, 0.4, 0), (-0.2, 0.4, 0)]),
                       [(0, 1, 2, 3)], m_emit('bounce_card_m', '#F3EADB', 0.25, light=True))
    card.location = tuple(s + Vector((0.42, 0.0, 0.25)))
    card.rotation_euler = (0, math.radians(-65), 0)
    card.visible_camera = False
    sm = m_emit('streak_m', '#FFF4E6', streak, light=False)
    st = B.mesh_from('streak_card', np.array([(-0.012, -0.5, 0), (0.012, -0.5, 0), (0.012, 0.5, 0), (-0.012, 0.5, 0)]),
                     [(0, 1, 2, 3)], sm)
    st.location = tuple(s + Vector((streak_pos[0], streak_pos[1], 0.45)))
    st.rotation_euler = (0, 0, math.radians(streak_rot))
    st.visible_camera = False
    st.visible_shadow = False
    st.visible_diffuse = False
    return L, card, st


def topdown_camera(name, res, ortho_m, centre=(0.0, 0.0)):
    return camera(name, 50.0, (centre[0], centre[1], 1.0), (centre[0], centre[1], 0.0), res=res, ortho=ortho_m)


# ============================================================================= envelope (S4, S5)

ENV_FLAP = (0.0, 22.0, 62.0, 112.0, 156.0, 180.0)


@asset('envelope', 'Top-down kraft photo envelope (flap side up), orthographic; flap opens 0 -> 180 deg over 6 frames; '
                   'back (bottom panel + open flap) and front (printed top panel) layers so prints slide out between.')
def build_envelope_asset(ctx):
    res = (760, 1400)
    sc = reset(res, 64, transparent=True)
    pxmm = 760 / 130.0
    cy = 22.5 * MM
    cam = topdown_camera('CAM_ENV', res, res[1] / pxmm * MM, (0.0, cy))
    table = box('table_catch', (0, 0, -0.0006), (0.6, 0.8, 0.001), pbr('tc', '#3A2216', 0.6)[0])
    table.is_shadow_catcher = True
    table.visible_camera = True
    r_table((0, 0, 0), key=13.0, streak=0.6, streak_rot=20.0)
    world_color('#2A1A15', 0.25)
    roots = {}
    for k, a in enumerate(ENV_FLAP):
        r_, parts = build_envelope(a, True, f'env{k}', ctx.q)
        roots[k] = (r_, parts)
    allp = [o for k in roots for o in roots[k][1].values()]

    def show(k):
        for o in allp:
            o.hide_render = True
        for o in roots[k][1].values():
            o.hide_render = False
            o.visible_camera = True
        table.hide_render = True

    def flap(i):
        show(i)

    def back(i):
        show(len(ENV_FLAP) - 1)
        roots[len(ENV_FLAP) - 1][1]['top'].visible_camera = False

    def front(i):
        show(len(ENV_FLAP) - 1)
        for nm in ('bottom', 'flap'):
            roots[len(ENV_FLAP) - 1][1][nm].visible_camera = False
    E = ENV
    feats = dict(mouth_centre=(0.0, (E['h'] / 2 - E['top_gap']) * MM, 0.0), hinge_centre=(0.0, E['h'] / 2 * MM, 0.0),
                 envelope_centre=(0.0, 0.0, 0.0), corner_tl=(-E['w'] / 2 * MM, E['h'] / 2 * MM, 0.0),
                 corner_br=(E['w'] / 2 * MM, -E['h'] / 2 * MM, 0.0))
    passes = [Pass('flap', len(ENV_FLAP), flap, 'lit', 64, gpu_spp=256, transparent=True, mode='anim',
                   labels=[f'flap {a:.0f} deg' for a in ENV_FLAP],
                   notes='full envelope, flap 0 (closed) -> 180 deg (open flat, gum strip up); f300-f315 in SHOTS'),
              Pass('back', 1, back, 'lit', 64, gpu_spp=256, transparent=True,
                   notes='bottom panel inside + open flap (the layer UNDER the sliding prints); top panel casts its '
                         'shadow but is invisible'),
              Pass('front', 1, front, 'lit', 64, gpu_spp=256, transparent=True,
                   notes='printed top panel only (the layer OVER the sliding prints); mouth edge = features.mouth_centre')]
    return dict(res=res, passes=passes, feats=feats, extra=dict(px_per_mm=round(pxmm, 4)))


# ============================================================================= print_src (textures for the prints)

def _mannequin(name, loc, h, mat):
    """Faceless dummy: tapered torso, short neck, smooth egg head, hanging capsule arms. No facial features."""
    parts = []
    x, y = loc
    parts.append(cylinder(name + '_legs', (x, y, h * 0.24), h * 0.11, h * 0.48, mat, seg=32, r2=h * 0.12, bev=h * 0.03))
    parts.append(cylinder(name + '_torso', (x, y, h * 0.62), h * 0.12, h * 0.30, mat, seg=32, r2=h * 0.15, bev=h * 0.05))
    parts.append(cylinder(name + '_neck', (x, y, h * 0.80), h * 0.035, h * 0.06, mat, seg=24))
    V, F = _uv_sphere(1.0, 32, 16)
    V = V * np.array([h * 0.058, h * 0.066, h * 0.078]) + np.array([x, y, h * 0.89])
    parts.append(B.mesh_from(name + '_head', V, F, mat))
    for sx in (-1, 1):
        parts.append(cylinder(name + f'_arm{sx}', (x + sx * h * 0.175, y, h * 0.60), h * 0.035, h * 0.34, mat, seg=20,
                              bev=h * 0.03))
    return parts


@asset('print_src', 'Five "90s compact camera" photos rendered as textures for the prints (no faces, no brands): '
                    'p1 tilted landscape, p2 blurred faceless dummies with hard flash, p3 birthday cake, p4 the cake '
                    'room + an out-of-focus thumb, p5 mirror with a flash flare.')
def build_print_src(ctx):
    res = (800, 1200)
    sc = reset(res, 32)
    sc.cycles.blur_glossy = 1.0
    wt = sc.world.node_tree
    nodes = wt.nodes
    bg = nodes['Background']
    sky = nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'NISHITA' if 'NISHITA' in [e.identifier for e in sky.bl_rna.properties['sky_type'].enum_items] else sky.sky_type
    try:
        sky.sun_elevation = math.radians(8)
        sky.sun_rotation = math.radians(214)
        sky.air_density = 1.4
        sky.dust_density = 4.0
        sky.altitude = 50.0
    except Exception:
        pass
    mixc_ = nodes.new('ShaderNodeMix')
    mixc_.data_type = 'RGBA'
    ins = {s.identifier: s for s in mixc_.inputs}
    ins['A_Color'].default_value = rgba('#1A120E')
    wt.links.new(sky.outputs['Color'], ins['B_Color'])
    wt.links.new([s for s in mixc_.outputs if s.identifier == 'Result_Color'][0], bg.inputs['Color'])
    fac = ins['Factor_Float']
    O = {}
    # --- P1: low hills + sky (at x = 0)
    grass = pbr('grass', '#5B6B2E', 0.85, spec=0.3)
    gm, gb, gg = grass
    gco = gg.co('Object')
    gg.put(gb.inputs['Base Color'], gg.mix(gg.mr(gg.noise(gco, 0.08, 4.0, 0.6), 0.35, 0.7), rgba('#6B6A30'), rgba('#3E5226')))
    rng = np.random.default_rng(3)

    def hills(U, V):
        X = (U - 0.5) * 600.0
        Y = V * 900.0 + 5.0
        Z = 1.2 * np.sin(X / 40.0 + 1.3) * np.sin(Y / 60.0) + 34.0 * np.exp(-((X - 60) / 140) ** 2) * np.clip((Y - 300) / 300, 0, 1) \
            + 4.0 * np.sin(X / 23.0) * np.clip((Y - 80) / 200, 0, 1) - 1.5
        return np.stack([X, Y, Z], -1)
    O['p1'] = [grid_mesh('p1_hills', 120, 120, hills, gm)]
    trees = pbr('tree', '#1E2A14', 0.9)[0]
    tm_, tb_, tg_ = pbr('tree2', '#2A3A1A', 0.85)
    tg_.put(tb_.inputs['Normal'], tg_.bump(tg_.noise(tg_.co('Object'), 3.0, 4.0, 0.7), 0.8, 0.5))
    for k in range(70):
        if k < 50:
            tx = rng.uniform(-200, 200)
            ty = 170 + 30 * math.sin(tx / 60.0) + rng.uniform(-15, 15)
        else:
            tx, ty = rng.uniform(-90, 90), rng.uniform(60, 160)
        zg = 1.2 * math.sin(tx / 40 + 1.3) * math.sin(ty / 60) - 1.5
        for j in range(4):
            V, F = _uv_sphere(1.0, 12, 8)
            r_ = rng.uniform(2.5, 5.0)
            V = V * np.array([r_, r_, r_ * 1.2]) + np.array([tx + rng.uniform(-3, 3), ty + rng.uniform(-3, 3), zg + r_ + rng.uniform(0, 3)])
            O['p1'].append(B.mesh_from(f'p1_tree{k}_{j}', V, F, tm_ if j % 2 else trees))
    cam1 = camera('CAM_P1', 35.0, (0.0, 0.0, 2.2), (0.0, 200.0, 6.0), res=res, roll=6.0)
    sun = lamp('p1_sun', 'SUN', (0, 0, 10), 6.0, kelvin=3300)
    sun.location = (-60.0, -90.0, 15.0)        # low sun behind-left of the photographer: warm light on the tree line
    look_at(sun, (0.0, 0.0, 0.0))
    sun.data.angle = math.radians(0.6)
    # --- P2: four faceless dummies against a pale wall (at x = 20), direct flash, defocus + shake
    ox = 20.0
    wall2 = box('p2_wall', (ox, 3.2, 1.5), (8.0, 0.1, 3.0), pbr('p2_wallm', '#D9CFC0', 0.85)[0])
    floor2 = box('p2_floor', (ox, 0.0, -0.01), (8.0, 8.0, 0.02), pbr('p2_floorm', '#6A5A48', 0.7)[0])
    dummies = []
    clothes = ['#7A2E2A', '#2E4A6A', '#C9B48A', '#3A3A3A']
    for k in range(4):
        mm = pbr(f'p2_dummy{k}', clothes[k], 0.55, sss=0.0)[0]
        dummies += _mannequin(f'p2_d{k}', (ox - 0.9 + k * 0.6, 2.3 + 0.1 * (k % 2)), 1.65 + 0.05 * (k % 3), mm)
    O['p2'] = [wall2, floor2] + dummies
    cam2 = camera('CAM_P2', 35.0, (ox + 0.05, -1.4, 1.45), (ox, 2.3, 1.25), fstop=2.0, focus=1.1, res=res, roll=-3.0)
    fl2 = lamp('p2_flash', 'AREA', (ox + 0.08, -1.35, 1.52), 200.0, kelvin=5600, target=(ox, 2.3, 1.3), size=(0.03, 0.02))
    # --- P3 / P4: birthday cake on a table (at x = 40), steel plates, 5 candles, flash shadow on the wall
    ox3 = 40.0
    wall3 = box('p3_wall', (ox3, 0.9, 1.2), (4.0, 0.1, 2.4), pbr('p3_wallm', '#B9A98E', 0.85)[0])
    cloth_m, cb, cg = pbr('p3_cloth', '#D8D0C0', 0.85, sheen=0.4)
    cco = cg.co('Object')
    cx_, cy_, _ = cg.xyz(cco)
    check = cg.m('MULTIPLY', cg.m('SINE', cg.m('MULTIPLY', cx_, 60.0)), cg.m('SINE', cg.m('MULTIPLY', cy_, 60.0)))
    cg.put(cb.inputs['Base Color'], cg.mix(cg.mr(check, -0.05, 0.05), rgba('#D8D0C0'), rgba('#B0423A')))
    table3 = box('p3_table', (ox3, 0.2, 0.74), (1.4, 0.9, 0.02), cloth_m)
    steel = pbr('p3_steel', '#C8C6C2', 0.18, metal=1.0)[0]
    plate_ = cylinder('p3_plate', (ox3, 0.15, 0.755), 0.15, 0.01, steel, seg=64, bev=0.003)
    sponge = pbr('p3_sponge', '#E8C9A0', 0.6, sss=0.3, sss_radius=(1.0, 0.7, 0.4), sss_scale=0.01)[0]
    cream_m = pbr('p3_cream', '#F4EDE2', 0.35, sss=0.5, sss_radius=(1.0, 0.9, 0.8), sss_scale=0.005, coat=0.2)[0]
    cake = cylinder('p3_cake', (ox3, 0.15, 0.80), 0.11, 0.08, cream_m, seg=96, bev=0.01)
    beads = []
    for k in range(36):
        a = 2 * math.pi * k / 36
        V, F = _uv_sphere(1.0, 12, 8)
        V = V * np.array([0.011, 0.011, 0.009]) + np.array([ox3 + 0.10 * math.cos(a), 0.15 + 0.10 * math.sin(a), 0.84])
        beads.append(B.mesh_from(f'p3_bead{k}', V, F, cream_m))
    rose = pbr('p3_rose', '#D2486A', 0.4, sss=0.3, sss_scale=0.004)[0]
    roses = []
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        V, F = _uv_sphere(1.0, 12, 8)
        V = V * np.array([0.014, 0.014, 0.01]) + np.array([ox3 + 0.05 * math.cos(a), 0.15 + 0.05 * math.sin(a), 0.845])
        roses.append(B.mesh_from(f'p3_rose{k}', V, F, rose))
    candle_m = pbr('p3_candle', '#E8B33A', 0.4, sss=0.4, sss_scale=0.004)[0]
    flame_m = m_emit('p3_flame', None, 18.0, kelvin=1900, light=True)
    candles = []
    for k in range(5):
        a = 2 * math.pi * k / 5
        x_, y_ = ox3 + 0.075 * math.cos(a), 0.15 + 0.075 * math.sin(a)
        candles.append(cylinder(f'p3_candle{k}', (x_, y_, 0.87), 0.0035, 0.055, candle_m, seg=16))
        V, F = _uv_sphere(1.0, 12, 8)
        V = V * np.array([0.0035, 0.0035, 0.009]) + np.array([x_, y_, 0.907])
        candles.append(B.mesh_from(f'p3_flame{k}', V, F, flame_m))
    plates2 = [cylinder(f'p3_side{k}', (ox3 + sx, 0.05 + 0.1 * k, 0.752), 0.09, 0.006, steel, seg=48, bev=0.002)
               for k, sx in enumerate((-0.38, 0.4))]
    O['p3'] = [wall3, table3, plate_, cake] + beads + roses + candles + plates2
    cam3 = camera('CAM_P3', 35.0, (ox3 + 0.03, -0.75, 1.18), (ox3, 0.2, 0.83), fstop=2.8, focus=0.98, res=res, roll=2.0)
    fl3 = lamp('p3_flash', 'AREA', (ox3 + 0.09, -0.72, 1.24), 9.0, kelvin=5600, target=(ox3, 0.2, 0.85), size=(0.03, 0.02))
    skin = m_emit('p4_skin', '#C98A6E', 0.85)        # a thumb 2 cm from the lens: a warm translucent glow, never lit by the flash
    skin.cycles.emission_sampling = 'NONE'
    thumb = cylinder('p4_thumb', (0, 0, 0), 0.016, 0.09, skin, seg=32, bev=0.014)
    nail = box('p4_nail', (0, 0.0, 0.029), (0.014, 0.004, 0.016), m_emit('p4_nailm', '#E2B4A0', 0.6), bev=0.0015)
    nail.parent = thumb
    nail.location = (0.0, 0.0095, 0.029)
    cam4 = camera('CAM_P4', 35.0, (ox3 + 0.03, -0.75, 1.18), (ox3, 0.2, 0.83), fstop=2.8, focus=1.6, res=res, roll=-4.0)
    thumb.parent = cam4
    thumb.location = (-0.016, 0.014, -0.03)
    thumb.rotation_euler = (math.radians(70), math.radians(-35), 0)
    # --- P5: dressing-table mirror (at x = 60), flash flare
    ox5 = 60.0
    wood = mat_sheesham()
    mirror_m = pbr('p5_mirror', '#E8E8E8', 0.02, metal=1.0)[0]
    frame5 = prism('p5_frame', rrect(0.62, 0.92, 0.12, 12), 0.0, 0.03, wood, plane='XZ', at=(ox5, 1.0, 1.25), bev=0.006)
    glass5 = prism('p5_glass', rrect(0.54, 0.84, 0.1, 12), 0.0, 0.004, mirror_m, plane='XZ', at=(ox5, 0.996, 1.25))
    dtab = box('p5_table', (ox5, 0.8, 0.74), (1.1, 0.45, 0.03), wood, bev=0.004)
    room5 = box('p5_wall', (ox5, 1.04, 1.4), (3.0, 0.05, 2.8), pbr('p5_wallm', '#5A4636', 0.9)[0])
    bottles = [cylinder(f'p5_bottle{k}', (ox5 - 0.3 + 0.12 * k, 0.75, 0.80), 0.022, 0.1, pbr(f'p5_b{k}', ['#C9A24A', '#7A3A5A', '#3A6A7A', '#E0D8C8'][k], 0.1,
                                                                                             transmission=0.6)[0], seg=32, bev=0.004)
               for k in range(4)]
    O['p5'] = [frame5, glass5, dtab, room5] + bottles
    cam5 = camera('CAM_P5', 35.0, (ox5 + 0.18, -0.6, 1.3), (ox5 + 0.05, 1.0, 1.25), res=res, roll=1.5)
    fl5 = lamp('p5_flash', 'AREA', (ox5 + 0.2, -0.58, 1.36), 30.0, kelvin=5600, target=(ox5, 1.0, 1.25), size=(0.03, 0.02))
    room_fill = lamp('p5_fill', 'POINT', (ox5 - 0.8, 0.0, 2.0), 8.0, kelvin=2700, soft=0.2)
    back5 = box('p5_backwall', (ox5, -1.6, 1.4), (3.0, 0.05, 2.8), pbr('p5_backm', '#7A6450', 0.85)[0])
    door5 = box('p5_door', (ox5 - 0.5, -1.56, 1.0), (0.8, 0.04, 2.0), mat_sheesham(), bev=0.01)
    ceil5 = box('p5_ceil', (ox5, -0.3, 2.8), (3.0, 3.0, 0.05), pbr('p5_ceilm', '#D8D0C0', 0.9)[0])
    O['p5'] += [back5, door5, ceil5]
    cams = dict(p1=cam1, p2=cam2, p3=cam3, p4=cam4, p5=cam5)
    lights = dict(p1=[sun], p2=[fl2], p3=[fl3] , p4=[fl3], p5=[fl5, room_fill])
    all_l = [sun, fl2, fl3, fl5, room_fill]
    # camera shake for P2 (motion blur over the shutter)
    sc.render.use_motion_blur = False
    cam2.keyframe_insert('rotation_euler', frame=1)
    r0 = cam2.rotation_euler.copy()
    cam2.rotation_euler = (r0.x + math.radians(0.9), r0.y, r0.z + math.radians(1.6))
    cam2.keyframe_insert('rotation_euler', frame=2)
    cam2.rotation_euler = r0
    sc.frame_set(1)
    keys = ['p1', 'p2', 'p3', 'p4', 'p5']

    def setup(i):
        k = keys[i]
        sc.camera = cams[k]
        lights_on(all_l, False)
        lights_on(lights[k], True)
        thumb.hide_render = k != 'p4'
        nail.hide_render = k != 'p4'
        fac.default_value = 1.0 if k == 'p1' else 0.0
        bg.inputs['Strength'].default_value = 0.14 if k == 'p1' else 0.6
        sc.render.use_motion_blur = k == 'p2'
        sc.render.motion_blur_shutter = 1.0
        sc.frame_set(1)
    passes = [Pass('src', 5, setup, 'lit', 32, gpu_spp=128, mode='static', labels=keys, seq_preview=list(range(5)),
                   notes='opaque photo textures 800x1200 (portrait, as a 35 mm compact frames them); the lab cast, '
                         'date stamp and corner radius are added when the prints are built')]
    sc.camera = cam1
    return dict(res=res, passes=passes, feats={}, extra=dict(sources=keys))


# ============================================================================= prints (S5, S6)

PRINT_W, PRINT_H = 102.0, 152.0
PRINT_PXMM = 6.6667            # 680 px across a 4R print inside the 720 x 1080 sprite


def _print_src_path(key):
    for root in (OUT, PREVIEW):
        d = os.path.join(root, 'print_src', 'src')
        if not os.path.exists(os.path.join(d, 'meta.json')):
            continue
        labels = json.load(open(os.path.join(d, 'meta.json'))).get('labels') or []
        fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
        if root == PREVIEW:
            pf = json.load(open(os.path.join(d, 'meta.json'))).get('preview_frames') or list(range(len(fs)))
            labels = [labels[i] for i in pf]
        if key in labels and labels.index(key) < len(fs):
            return os.path.join(d, fs[labels.index(key)]), root == PREVIEW
    raise FileNotFoundError(f'print_src/{key} not rendered yet: run `print_src` before `prints`')


def _seg7(draw, x, y, ch, s, col):
    """Minilab-style 7-segment glyph at (x, y) top-left, digit height 2 s."""
    segs = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc',
            '8': 'abcdefg', '9': 'abcfgd'}
    t = max(2, int(s * 0.22))
    P = dict(a=((x + t, y), (x + s - t, y)), b=((x + s, y + t), (x + s, y + s - t)), c=((x + s, y + s + t), (x + s, y + 2 * s - t)),
             d=((x + t, y + 2 * s), (x + s - t, y + 2 * s)), e=((x, y + s + t), (x, y + 2 * s - t)), f=((x, y + t), (x, y + s - t)),
             g=((x + t, y + s), (x + s - t, y + s)))
    if ch == "'":
        draw.line([(x + s * 0.3, y), (x + s * 0.15, y + s * 0.5)], fill=col, width=t)
        return s * 0.5
    if ch == ' ':
        return s * 0.6
    for k in segs.get(ch, ''):
        draw.line(P[k], fill=col, width=t)
    return s * 1.45


def make_print_texture(key, seed=0):
    """print_src frame -> lab print: warm / magenta cast, lifted blacks (#1A1412), soft contrast, fine grain, orange
    7-seg date stamp '98 10 11 bottom-right, 1 mm corner radius in alpha. Written to RWS/out/tex3d/print_<key>.png."""
    from PIL import Image, ImageDraw, ImageFilter
    src, prev = _print_src_path(key)
    im = Image.open(src).convert('RGB').resize((int(PRINT_W * 10), int(PRINT_H * 10)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    if key == 'p5':      # on-camera flash in the mirror: halation bloom around the hot spot
        lum = a.mean(2)
        hot = np.clip((lum - 0.85) * 6.0, 0, 1)
        from scipy.ndimage import gaussian_filter
        bloom = sum(gaussian_filter(hot, s_) * w_ for s_, w_ in ((8, 1.2), (30, 0.9), (90, 0.7)))
        a = 1 - (1 - a) * (1 - np.clip(bloom[..., None] * np.array([1.0, 0.95, 0.85]), 0, 1))
    a = a ** 0.95
    a = a * np.array([1.07, 0.95, 1.01]) + np.array([0.012, -0.004, 0.018])
    lift = np.array([0x1A, 0x14, 0x12]) / 255.0
    a = lift + (1 - lift) * np.clip(a, 0, 1)
    a = 0.5 + (a - 0.5) * 0.93
    rng = np.random.default_rng(100 + seed)
    a = a + rng.normal(0, 0.012, a.shape[:2])[..., None]
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    # date stamp
    st = Image.new('RGBA', out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    s_ = 22
    x, y = out.size[0] - 330, out.size[1] - 120
    for ch in "'98 10 11":
        x += _seg7(d, x, y, ch, s_, (255, 122, 26, 255))
    glow = st.filter(ImageFilter.GaussianBlur(6))
    out = out.convert('RGBA')
    out.alpha_composite(glow)
    out.alpha_composite(st.filter(ImageFilter.GaussianBlur(0.8)))
    # corner radius 1 mm
    w_, h_ = out.size
    mask = Image.new('L', (w_, h_), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w_ - 1, h_ - 1], radius=10, fill=255)
    out.putalpha(mask)
    return _save(out, f'print_{key}.png', TEXW), prev


@cached('print_back.png')
def tex_print_back(w=1020, h=1520):
    """Back of a lab print: off-white with a faint repeating grey diagonal line pattern (no words)."""
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), (237, 231, 220, 255))
    d = ImageDraw.Draw(im)
    for k in range(-h, w, 46):
        d.line([(k, 0), (k + h * 0.55, h)], fill=(214, 208, 199, 255), width=3)
    for k in range(0, h, 180):
        d.rectangle([60, k + 70, 160, k + 78], fill=(205, 199, 190, 255))
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=255)
    im.putalpha(mask)
    return _save(im, 'print_back.png')


@cached('neg_edge.png')
def tex_neg_edge(w=350, h=1500):
    """Edge print + perforations for the 35 x 150 mm negative strip (10 px/mm): white-ish latent edge numbers
    '33 34 35 36' with arrows, KS perfs as alpha 0 (alpha channel), frame windows transparent black (to be filled)."""
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font('Poppins-SemiBold.ttf', 26)
    for k, n in enumerate((33, 34, 35, 36)):
        y = 18 + k * 375
        lab = Image.new('L', (160, 40), 0)
        ImageDraw.Draw(lab).text((4, 2), f'{n}  >', fill=255, font=f)
        lab = lab.rotate(90, expand=True)
        im.paste(Image.new('RGBA', lab.size, (255, 214, 150, 230)), (2, y + 190), lab)
        lab2 = Image.new('L', (160, 40), 0)
        ImageDraw.Draw(lab2).text((4, 2), f'{n}A', fill=255, font=f)
        lab2 = lab2.rotate(90, expand=True)
        im.paste(Image.new('RGBA', lab2.size, (255, 214, 150, 230)), (w - 32, y + 30), lab2)
    return _save(im, 'neg_edge.png')


def make_negative_texture():
    """Orange-masked colour negative strip, 4 frames (inverted print_src p1 p2 p3 p4), perfs in alpha."""
    from PIL import Image, ImageDraw
    w, h = 350, 1500
    base = np.zeros((h, w, 4), np.float32)
    base[..., :3] = np.array([0xB8, 0x5A, 0x28]) / 255.0
    base[..., 3] = 0.82
    for k, key in enumerate(('p1', 'p2', 'p3', 'p4')):
        src, _ = _print_src_path(key)
        im = Image.open(src).convert('RGB').resize((240, 355), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32) / 255.0
        neg = (1 - a) * np.array([0.85, 0.55, 0.33]) + np.array([0.10, 0.04, 0.0])
        y0 = 8 + k * 375
        base[y0:y0 + 355, 55:295, :3] = neg
        base[y0:y0 + 355, 55:295, 3] = 0.78
    # perforations (KS 2.0 x 2.8 mm at 10 px/mm, pitch 4.75 mm), both edges
    yy = 8.0
    while yy < h / 10 - 3:
        for x0 in (8, w - 8 - 28):
            base[int(yy * 10):int(yy * 10) + 20, x0:x0 + 28, 3] = 0.0
        yy += 4.75
    edge = np.asarray(Image.open(tex_neg_edge()).convert('RGBA')).astype(np.float32) / 255.0
    ea = edge[..., 3:4]
    base[..., :3] = base[..., :3] * (1 - ea) + edge[..., :3] * ea
    out = Image.fromarray(np.clip(base * 255, 0, 255).astype(np.uint8), 'RGBA')
    return _save(out, 'negatives.png', TEXW)


def mat_print(name, img_path, back_path, seed=0.0):
    """Glossy print: image base (rough 0.25) under a clear coat (1.0, rough 0.04) with a fingerprint and hairline
    scratches in the coat; corner radius from the image alpha."""
    m, b, g = pbr(name, '#FFFFFF', 0.25, spec=0.5, coat=1.0, coat_rough=0.04, ior=1.5)
    uv = g.uv()
    t = tex(g, img_path, uv)
    g.put(b.inputs['Base Color'], t.outputs['Color'])
    g.put(b.inputs['Alpha'], t.outputs['Alpha'])
    wn = g.n('ShaderNodeGroup')
    wn.node_tree = wear_group()
    W_ = {s.name: s for s in wn.inputs}
    g.put(W_['Color'], (1, 1, 1, 1))
    g.put(W_['Roughness'], 0.04)
    g.put(W_['Prints'], 1.6)
    g.put(W_['Scratch'], 1.2)
    g.put(W_['Seed'], 50.0 + seed)
    g.put(W_['Scale'], 1.0)
    g.put(b.inputs['Coat Roughness'], wn.outputs['Roughness'])
    g.put(b.inputs['Coat Normal'], wn.outputs['Normal'])
    mb, bb_, gb = pbr(name + '_back', '#EDE7DC', 0.7, spec=0.35)
    tb = tex(gb, back_path, gb.uv())
    gb.put(bb_.inputs['Base Color'], tb.outputs['Color'])
    gb.put(bb_.inputs['Alpha'], tb.outputs['Alpha'])
    return m, mb


def print_mesh(name, mat_front, mat_back, w_mm, h_mm, bow_mm=2.5, seed=0, flip=False):
    rng = np.random.default_rng(seed)
    tw = rng.uniform(-0.6, 0.6)

    def fn(U, V):
        x = (U - 0.5) * w_mm * MM
        y = (V - 0.5) * h_mm * MM
        z = bow_mm * MM * (2 * U - 1) ** 2 + 0.4 * MM * tw * (2 * U - 1) * (2 * V - 1) + 0.25 * MM * (2 * V - 1) ** 2
        return np.stack([x, y, z], -1)
    o = grid_mesh(name, 36, 52, fn, mat_front)
    o.data.materials.append(mat_back)
    sm = solidify(o, 0.00025, 0.0)
    sm.material_offset = 1
    sm.material_offset_rim = 1
    if flip:
        o.rotation_euler = (0, math.radians(180), 0)
    return o


PRINT_KEYS = ('p1', 'p2', 'p3', 'p4', 'p5')


@asset('prints', 'Top-down glossy 4R prints (102 x 152 mm, bowed 2.5 mm) from the print_src photos with a lab cast and '
                 'date stamp; one soft specular streak each; plus a print back and the negatives strip.')
def build_prints(ctx):
    res = (720, 1080)
    sc = reset(res, 64, transparent=True)
    cam = topdown_camera('CAM_PRINT', res, res[1] / PRINT_PXMM * MM)
    L, card, streak = r_table((0, 0, 0), key=9.0, streak=1.4, kelvin=4000)
    world_color('#2A1A15', 0.2)
    back_p = tex_print_back()
    objs = {}
    prev_any = False
    for k, key in enumerate(PRINT_KEYS):
        p, prev = make_print_texture(key, k)
        prev_any |= prev
        mf, mb = mat_print(f'print_{key}', p, back_p, k)
        objs[key] = print_mesh(f'print_{key}', mf, mb, PRINT_W, PRINT_H, 2.5, seed=k)
    mf, mb = mat_print('print_back', make_print_texture('p1', 9)[0], back_p, 9)
    objs['back'] = print_mesh('print_backside', mf, mb, PRINT_W, PRINT_H, 2.2, seed=9, flip=True)
    neg_p = make_negative_texture()
    nm, nb, ng = pbr('negatives', '#B85A28', 0.15, spec=0.5, transmission=0.3, coat=0.3, coat_rough=0.06)
    t = tex(ng, neg_p, ng.uv())
    ng.put(nb.inputs['Base Color'], t.outputs['Color'])
    ng.put(nb.inputs['Alpha'], t.outputs['Alpha'])
    objs['negatives'] = print_mesh('negatives', nm, nm, 35.0, 150.0, 0.8, seed=12)
    keys = list(PRINT_KEYS) + ['back']
    streaks = [(35, -0.02), (-25, 0.03), (55, 0.0), (15, -0.03), (-40, 0.02), (30, 0.0)]

    def setup_one(key, si):
        def f(i):
            for o in objs.values():
                o.hide_render = True
            objs[key].hide_render = False
            rot, off = streaks[si % len(streaks)]
            streak.rotation_euler = (0, 0, math.radians(rot))
            streak.location = (off, off * 0.5, 0.45)
        return f
    passes = []
    for si, key in enumerate(keys):
        passes.append(Pass(key, 1, setup_one(key, si), 'lit', 64, gpu_spp=256, transparent=True,
                           notes=('print back (grey line pattern)' if key == 'back' else f'4R print {key}') +
                           f'; {PRINT_PXMM:.3f} px/mm, centred in the 720 x 1080 sprite; contact shadow in comp'))
    neg_cam = [None]

    def neg(i):
        for o in objs.values():
            o.hide_render = True
        objs['negatives'].hide_render = False
        streak.rotation_euler = (0, 0, math.radians(10))
        streak.location = (0.0, 0.0, 0.45)
    passes.append(Pass('negatives', 1, neg, 'lit', 64, gpu_spp=256, transparent=True, crop=True,
                       notes='35 x 150 mm orange-masked negative strip, frames 33-36 (inverted p1-p4), perfs open; '
                             'base alpha ~0.8 (translucent)'))
    del neg_cam
    return dict(res=res, passes=passes, feats=dict(centre=(0.0, 0.0, 0.0)),
                extra=dict(px_per_mm=PRINT_PXMM, print_src_from_preview=prev_any))


# ============================================================================= album_page (S6)

@cached('album_border.png')
def tex_album_border(pxmm=6):
    """Gold-foil border print for a 240 x 320 mm magnetic album page (alpha = foil)."""
    from PIL import Image, ImageDraw
    w, h = 240 * pxmm, 320 * pxmm
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    for inset, lw in ((7, 6), (10, 2)):
        d.rounded_rectangle([inset * pxmm, inset * pxmm, w - inset * pxmm, h - inset * pxmm], radius=int(4 * pxmm),
                            outline=255, width=lw)
    for cx, cy, sx, sy in ((14, 14, 1, 1), (226, 14, -1, 1), (14, 306, 1, -1), (226, 306, -1, -1)):
        x, y = cx * pxmm, cy * pxmm
        for r_ in (5, 9):
            d.arc([x - r_ * pxmm, y - r_ * pxmm, x + r_ * pxmm, y + r_ * pxmm], 0, 360, fill=255, width=3)
        d.line([(x + sx * 9 * pxmm, y), (x + sx * 40 * pxmm, y)], fill=255, width=3)
        d.line([(x, y + sy * 9 * pxmm), (x, y + sy * 40 * pxmm)], fill=255, width=3)
        for k in range(4):
            px_, py_ = x + sx * (14 + 6 * k) * pxmm, y + sy * 3 * pxmm
            d.ellipse([px_ - 4, py_ - 4, px_ + 4, py_ + 4], fill=255)
    return _save(im, 'album_border.png')


@asset('album_page', 'Top-down magnetic photo-album page (adhesive ridges, worn gold-foil border) in its maroon vinyl '
                     'album on the sheesham table; sleeve = the clear PVC film as a reflection-only overlay.')
def build_album_page(ctx):
    res = (W_PX, H_PX)
    sc = reset(res, 64)
    pxmm = 1920 / 360.0
    cam = topdown_camera('CAM_ALBUM', res, 0.36)
    home_set(table_far=0.6, table_near=0.6, doily=False)
    vinyl, vb, vg = pbr('vinyl', '#4A1A16', 0.55, spec=0.45, coat=0.2, coat_rough=0.3)
    vco = vg.co('Object')
    vor = vg.n('ShaderNodeTexVoronoi')
    vor.inputs['Scale'].default_value = 900.0
    vg.put(vor.inputs['Vector'], vco)
    wn = wear(vg, vb, '#4A1A16', 0.55, '#7A3A30', edge=1.2, dust=0.5, prints=0.6, scratch=0.6, seed=61.0)
    vg.put(vb.inputs['Normal'], vg.bump(vor.outputs['Distance'], 0.3, 0.0002, wn.outputs['Normal']))
    album = box('album', (0.0, 0.0, -0.006), (0.30, 0.37, 0.012), vinyl, bev=0.004)
    # page board: ridges every 3 mm (adhesive lines, slightly glossy), gold foil border
    pm, pb, pg = pbr('page_board', '#E9DFC8', 0.75, spec=0.4)
    pco = pg.co('Object')
    x, y, z = pg.xyz(pco)
    ridge = pg.m('MULTIPLY_ADD', pg.m('SINE', pg.m('MULTIPLY', y, 2 * math.pi / 0.003)), 0.5, 0.5)
    ridge = pg.m('POWER', ridge, 3.0)
    foil_t = tex(pg, tex_album_border(), planar(pg, pco, ('x', 'y'), (-0.12, -0.16), (0.24, 0.32)), noncolor=True)
    foil = pg.m('MULTIPLY', foil_t.outputs[0], pg.mr(pg.noise(pco, 300.0, 3.0, 0.6), 0.3, 0.55, 0.0, 1.0))
    yel = pg.mr(pg.noise(pco, 8.0, 3.0, 0.6), 0.35, 0.75, 0.0, 0.12)
    base = pg.mix(yel, rgba('#E9DFC8'), rgba('#D6C49A'))
    wn = wear(pg, pb, base, 0.75, '#F2EBDA', edge=0.3, dust=0.7, prints=0.4, scratch=0.2, seed=62.0)
    pg.put(pb.inputs['Base Color'], pg.mix(foil, wn.outputs['Color'], rgba('#C9A24A')))
    pg.put(pb.inputs['Metallic'], foil)
    pg.put(pb.inputs['Roughness'], pg.mix(foil, pg.m('SUBTRACT', wn.outputs['Roughness'], pg.m('MULTIPLY', ridge, 0.35)), (0.3, 0.3, 0.3, 1)))
    pg.put(pb.inputs['Normal'], pg.bump(pg.m('ADD', ridge, pg.m('MULTIPLY', foil, 0.4)), 0.25, 0.00015, wn.outputs['Normal']))
    page = box('page', (0.0, 0.0, 0.0006), (0.24, 0.32, 0.0012), pm, bev=0.0004)
    # PVC sleeve: wrinkles 0.2 mm, top-right corner lifted
    rng = np.random.default_rng(6)
    ph = rng.uniform(0, 6.28, 6)

    def sleeve_fn(U, V):
        x = (U - 0.5) * 0.24
        y = (V - 0.5) * 0.32
        wr = sum(0.00006 * np.sin(x * f1 + y * f2 + p) for f1, f2, p in zip((180, 260, 90, 400, 140, 330),
                                                                              (60, -150, 300, 90, -260, 210), ph))
        lift = np.clip((U - 0.78) / 0.22, 0, 1) * np.clip((V - 0.82) / 0.18, 0, 1)
        z = 0.0016 + wr + 0.005 * lift ** 2
        return np.stack([x, y, z], -1)
    pvc_plate = pbr('pvc', '#FFFFFF', 0.06, ior=1.54, transmission=1.0)[0]
    sleeve = grid_mesh('sleeve', 120, 160, sleeve_fn, pvc_plate)
    # sleeve-pass material: reflections only (transparent + glossy by fresnel), page held out
    sm = bpy.data.materials.new('pvc_refl')
    nt = sm.node_tree
    for n_ in list(nt.nodes):
        nt.nodes.remove(n_)
    g = B.G(nt)
    fr = g.n('ShaderNodeFresnel')
    fr.inputs['IOR'].default_value = 1.54
    gl = g.n('ShaderNodeBsdfGlossy')
    gl.inputs['Roughness'].default_value = 0.06
    tr = g.n('ShaderNodeBsdfTransparent')
    mx = g.n('ShaderNodeMixShader')
    out = g.n('ShaderNodeOutputMaterial')
    nt.links.new(fr.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    L, card, streak = r_table((0, 0, 0), key=11.0, streak=2.0, streak_rot=38.0)
    world_color('#2A1A15', 0.3)
    vis0 = save_visibility()

    def page_pass(i):
        restore_visibility(vis0)
        sleeve.hide_render = True
        sc.render.film_transparent = False

    def sleeve_pass(i):
        restore_visibility(vis0)
        sleeve.hide_render = False
        sleeve.data.materials[0] = sm
        for o in scene_meshes():
            if o is not sleeve and o.visible_camera:
                o.is_holdout = True

    feats = dict(page_centre=(0.0, 0.0, 0.0), page_tl=(-0.12, 0.16, 0.0), page_br=(0.12, -0.16, 0.0))
    passes = [Pass('page', 1, page_pass, 'lit', 64, gpu_spp=512, notes='opaque plate: empty album page (prints are '
                                                                        'composited), maroon album border, table'),
              Pass('sleeve', 1, sleeve_pass, 'lit', 64, gpu_spp=256, transparent=True,
                   notes='PVC sleeve reflections only (straight alpha): slide it down f430-f450, sweep its glare streak')]
    return dict(res=res, passes=passes, feats=feats, extra=dict(px_per_mm=round(pxmm, 4)))


# ============================================================================= drives (S7, S8-S9 bg)

@cached('tape_labels.png')
def tex_tape_labels(pxmm=20):
    """Four masking-tape labels (60 x 18 mm each, stacked vertically in one texture): hand-lettered black marker
    'CAM A'..'CAM D' + '2 TB', ink bleed, torn fibre ends (alpha)."""
    from PIL import Image, ImageDraw, ImageFilter
    w, h1 = 60 * pxmm, 18 * pxmm
    im = Image.new('RGBA', (w, h1 * 4), (0, 0, 0, 0))
    rng = np.random.default_rng(14)
    fbig = font('Caveat-Bold.ttf', int(12.5 * pxmm))
    fsm = font('Caveat-Bold.ttf', int(7.5 * pxmm))
    for k, lab in enumerate('ABCD'):
        tape = Image.new('L', (w, h1), 0)
        td = ImageDraw.Draw(tape)
        # torn ends: jagged polygon
        left = [(int(rng.uniform(0, 1.6) * pxmm), int(y)) for y in np.linspace(0, h1, 14)]
        right = [(w - int(rng.uniform(0, 1.6) * pxmm), int(y)) for y in np.linspace(h1, 0, 14)]
        td.polygon(left + right, fill=255)
        ink = Image.new('L', (w, h1), 0)
        idr = ImageDraw.Draw(ink)
        idr.text((int(4 * pxmm), int(-1.5 * pxmm)), f'CAM {lab}', fill=255, font=fbig)
        idr.text((int(42 * pxmm), int(5.5 * pxmm)), '2 TB', fill=255, font=fsm)
        ink = ink.rotate(rng.uniform(-2.5, 2.5), resample=Image.BICUBIC, center=(w / 2, h1 / 2))
        bleed = ink.filter(ImageFilter.GaussianBlur(2.2))
        ink_a = np.maximum(np.asarray(ink).astype(np.float32), np.asarray(bleed).astype(np.float32) * 0.45)
        t = np.asarray(tape).astype(np.float32) / 255.0
        base = np.array([230, 217, 181], np.float32)
        tone = 1.0 + rng.normal(0, 0.03, (h1, w)).astype(np.float32)[..., None]
        rgb = base * tone
        ka = (ink_a / 255.0)[..., None] * 0.92
        rgb = rgb * (1 - ka) + np.array([18, 16, 14], np.float32) * ka
        tile = np.dstack([np.clip(rgb, 0, 255), t * 255]).astype(np.uint8)
        im.paste(Image.fromarray(tile, 'RGBA'), (0, k * h1))
    return _save(im, 'tape_labels.png')


def mats_drives():
    M = {}
    m, b, g = pbr('anodised', '#2E2C2A', 0.38, metal=1.0, aniso=0.3)
    co = g.co('Object')
    blast = g.noise(co, 9000.0, 2.0, 0.6)
    wn = wear(g, b, '#2E2C2A', 0.38, '#6A6660', edge=2.0, dust=0.8, prints=1.2, scratch=0.9, seed=71.0)
    g.put(b.inputs['Roughness'], g.m('SUBTRACT', wn.outputs['Roughness'], g.m('MULTIPLY', wn.outputs['EdgeMask'], 0.23)))
    g.put(b.inputs['Normal'], g.bump(blast, 0.12, 0.00002, wn.outputs['Normal']))
    M['alu'] = m
    m, b, g = pbr('drive_abs', '#0C0B0B', 0.45, spec=0.5)
    wear(g, b, '#0C0B0B', 0.45, '#35312E', edge=1.2, dust=1.0, prints=0.5, scratch=0.6, seed=72.0)
    M['abs'] = m
    M['port'] = pbr('port', '#050505', 0.6)[0]
    M['port_metal'] = pbr('port_metal', '#B8B6B0', 0.25, metal=1.0)[0]
    M['led'] = m_emit('drive_led', '#FF9F1C', 0.0)
    M['led_lens'] = pbr('drive_led_lens', '#FFFFFF', 0.15, ior=1.5, transmission=0.6)[0]
    p = tex_tape_labels()
    M['tape'] = []
    for k in range(4):
        m, b, g = pbr(f'tape{k}', '#E6D9B5', 0.8, spec=0.3, sss=0.15, sss_scale=0.0005)
        uv = g.uv()
        u_, v_, _ = g.xyz(uv)
        vv = g.m('ADD', g.m('MULTIPLY', v_, 0.25), k * 0.25)      # drive k (bottom->top) wears label 'DCBA'[k]
        t = tex(g, p, g.comb(u_, vv, 0.0))
        fib = g.noise(g.co('Object'), 2500.0, 3.0, 0.7)
        g.put(b.inputs['Base Color'], t.outputs['Color'])
        g.put(b.inputs['Alpha'], t.outputs['Alpha'])
        g.put(b.inputs['Normal'], g.bump(fib, 0.25, 0.00005))
        M['tape'].append(m)
    M['tape_mask'] = m_emit('tape_mask', '#FFFFFF', 1.0)
    m, b, g = pbr('braid', '#151414', 0.55, spec=0.4, sheen=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    br = g.m('MULTIPLY', g.m('SINE', g.m('MULTIPLY', g.m('ADD', x, y), 2500.0)), g.m('SINE', g.m('MULTIPLY', g.m('SUBTRACT', x, y), 2500.0)))
    g.put(b.inputs['Base Color'], g.mix(g.mr(br, -0.3, 0.6), rgba('#0C0B0B'), rgba('#2E2B29')))
    g.put(b.inputs['Normal'], g.bump(br, 0.5, 0.0002))
    M['braid'] = m
    return M


def mat_walnut():
    base = '#2A1A12'
    m, b, g = pbr('walnut', base, 0.32, coat=0.5, coat_rough=0.22, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    grain = g.wave(g.comb(g.m('MULTIPLY', x, 0.12), y, z), 7.0, 8.0, 4.0, bands='Y')
    pores = g.mr(g.noise(g.comb(g.m('MULTIPLY', x, 0.2), g.m('MULTIPLY', y, 8.0), z), 300.0, 2.0, 0.5), 0.62, 0.72)
    k = g.m('MULTIPLY', g.mr(grain, 0.0, 1.0, 0.65, 1.25), g.m('SUBTRACT', 1.0, g.m('MULTIPLY', pores, 0.35)))
    dx, dy = g.m('SUBTRACT', x, 0.16), g.m('SUBTRACT', y, 0.12)
    d = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', dx, dx), g.m('MULTIPLY', dy, dy)))
    ring = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', d, 0.042)), 0.0025, 0.0004, 0.0, 1.0, smooth=True)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', ring, 0.5, 1.0))
    col = g.vscale(rgb_node(g, base), k)
    wn = wear(g, b, col, 0.32, '#4A3020', edge=0.0, dust=0.7, prints=0.8, scratch=1.4, seed=73.0)
    g.put(b.inputs['Coat Roughness'], g.m('ADD', 0.2, g.m('MULTIPLY', ring, 0.3)))
    return m


def build_drive(M, k, c, yaw, q=1.0):
    """One 120 x 78 x 19 mm portable drive centred at c (bottom centre), long side facing -Y (camera)."""
    m = lambda v: v * MM  # noqa: E731
    root = bpy.data.objects.new(f'drive{k}', None)
    link(root)
    seg = max(6, int(10 * q))
    shell = prism(f'drv{k}_shell', rrect(m(114), m(78), m(2.0), seg), 0.0, m(19), M['alu'], bev=m(1.5), seg=1)
    caps = []
    for sx in (-1, 1):
        cap = prism(f'drv{k}_cap{sx}', rrect(m(3.2), m(78), m(1.2), 4), 0.0, m(19), M['abs'], at=(sx * m(58.6), 0, 0),
                    bev=m(1.0), seg=3)
        caps.append(cap)
    port = prism(f'drv{k}_port', rrect(m(8.4), m(2.6), m(1.2), 6), 0.0, m(1.2), M['port'], plane='YZ',
                 at=(m(60.0), m(0.0), m(9.5)))
    port.rotation_euler = (0, 0, 0)
    tongue = box(f'drv{k}_tongue', (m(59.6), m(0.0), m(9.5)), (m(1.0), m(6.6), m(0.7)), M['port_metal'])
    led = box(f'drv{k}_led', (m(45.0), m(-39.05), m(9.5)), (m(6.0), m(0.2), m(1.0)), M['led'])
    lens = box(f'drv{k}_ledlens', (m(45.0), m(-39.1), m(9.5)), (m(6.4), m(0.15), m(1.3)), M['led_lens'])
    # masking tape on the front face, one corner lifted
    rng = np.random.default_rng(80 + k)
    tilt = rng.uniform(-2.0, 2.0)

    def tape_fn(U, V):
        x = (U - 0.5) * m(60)
        z = (V - 0.5) * m(18)
        a = math.radians(tilt)
        xr, zr = x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)
        lift = np.clip((U - 0.9) / 0.1, 0, 1) * np.clip((V - 0.55) / 0.45, 0, 1)
        y = -m(39.12) - m(1.6) * lift ** 2
        return np.stack([xr - m(18), y, zr + m(9.5)], -1)
    tape = grid_mesh(f'drv{k}_tape', 30, 10, tape_fn, M['tape'][k])
    parts = [shell, port, tongue, led, lens, tape] + caps
    for o in parts:
        o.parent = root
    root.location = c
    root.rotation_euler = (0, 0, math.radians(yaw))
    return root, dict(shell=shell, led=led, tape=tape, parts=parts)


@asset('drives', 'Stack of four portable drives (anodised aluminium, masking-tape labels CAM A-D, braided cables) on a '
                 'walnut desk, 60 mm f/2 12 deg above, focus on CAM B; monitor glow out of focus at the top.')
def build_drives(ctx):
    sc = reset((W_PX, H_PX), 128)
    M = mats_drives()
    desk = box('desk', (0.0, 0.3, -0.015), (1.6, 1.2, 0.03), mat_walnut(), bev=0.003)
    wall = box('wall', (0.0, 1.1, 0.6), (3.0, 0.05, 1.6), mat_wall_dark())
    drives = []
    offs = [(0.0, 0.0, 1.5), (-3.0, 2.0, -1.0), (2.5, -1.5, 2.2), (-1.5, 1.0, -2.6)]      # bottom -> top (D, C, B, A)
    for k, (dx, dy, yaw) in enumerate(offs):
        r_, P = build_drive(M, k, (dx * MM, dy * MM, k * 19.2 * MM), yaw, ctx.q)
        drives.append(P)
    # braided cables from the right-hand ports coiling on the desk
    rng = np.random.default_rng(9)
    for k in range(4):
        pts = []
        x0, z0 = 0.061 + offs[k][0] * MM, k * 0.0192 + 0.0095
        pts.append((x0, offs[k][1] * MM, z0))
        pts.append((x0 + 0.02, offs[k][1] * MM - 0.002, z0))
        for t in np.linspace(0, 1, 9):
            a = t * 3.6 + k * 0.7
            r_ = 0.05 + 0.02 * k + 0.02 * t
            pts.append((0.15 + 0.03 * k + r_ * math.cos(a) * 0.7, 0.04 + r_ * math.sin(a), max(0.0025, z0 * (1 - t) ** 2 + 0.0025)))
        cu = bpy.data.curves.new(f'cable{k}', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.0022
        cu.bevel_resolution = 4
        sp = cu.splines.new('NURBS')
        sp.points.add(len(pts) - 1)
        for j, p in enumerate(pts):
            sp.points[j].co = (p[0], p[1], p[2], 1.0)
        sp.use_endpoint_u = True
        sp.order_u = 4
        o = link(bpy.data.objects.new(f'cable{k}', cu))
        o.data.materials.append(M['braid'])
        o['role'] = 'prop'
        plug = box(f'plug{k}', (x0 + 0.008, offs[k][1] * MM, z0), (0.014, 0.009, 0.0045), M['abs'], bev=0.0012)
    # monitor (out of focus at the top of frame) + lights
    mon = B.mesh_from('monitor', np.array([(-0.3, 0, 0), (0.3, 0, 0), (0.3, 0, 0.35), (-0.3, 0, 0.35)]), [(0, 1, 2, 3)],
                      m_emit('monitor_m', None, 1.2, kelvin=6500, light=False))
    mon.location = (0.12, 0.75, 0.16)
    cam_t = Vector((0.0, 0.0, 0.040))
    e = math.radians(12)
    dist = 0.50
    cam_loc = cam_t + Vector((0.0, -math.cos(e), math.sin(e))) * dist
    focus_pt = Vector(((offs[2][0] - 18) * MM, -0.0392, 2 * 0.0192 + 0.0095))       # CAM B label (third from bottom)
    cam = camera('CAM_DRIVES', 60.0, tuple(cam_loc), tuple(cam_t), fstop=2.0, focus=(focus_pt - cam_loc).length)
    place_on_screen(cam, (0.0, -0.039, 0.0384), (540, 1250))
    bpy.context.view_layer.update()
    glow = lamp('monitor_glow', 'AREA', (0.0, -0.55, 0.45), 9.0, kelvin=6500, target=(0, 0, 0.04), size=(0.6, 0.35))
    lamp_l = lamp('desk_lamp', 'AREA', (-0.55, -0.25, 0.12), 14.0, kelvin=2700, target=(0, 0, 0.04), size=(0.2, 0.2))
    rim = lamp('rim', 'AREA', (0.45, 0.45, 0.25), 18.0, kelvin=2000, target=(0, 0, 0.04), size=(0.1, 0.6))
    world_color('#170A07', 0.15)
    L = [glow, lamp_l, rim]
    led_m = M['led']
    vis0 = save_visibility()

    def plate(i):
        restore_visibility(vis0)
        lights_on(L, True)
        set_emit(led_m, 0.0)
        set_emit(bpy.data.materials['monitor_m'], 1.2)
        world_color('#170A07', 0.15)

    def emit(i):
        plate(i)
        lights_on(L, False)
        world_color('#000000', 0.0)
        set_emit(bpy.data.materials['monitor_m'], 0.0)
        for k, P in enumerate(drives):
            P['led'].hide_render = not (i == 0 or i - 1 == 3 - k)
        set_emit(led_m, 25.0)

    def emit_done():
        for P in drives:
            P['led'].hide_render = False

    def mask(i):
        plate(i)
        emit_done()
        lights_on(L, False)
        world_color('#000000', 0.0)
        set_emit(bpy.data.materials['monitor_m'], 0.0)
        k_draw = 3 - i                      # frame 0 = CAM A (top drive) ... frame 3 = CAM D (bottom)
        for o in scene_meshes():
            o.is_holdout = True
        tp = drives[k_draw]['tape']
        tp.is_holdout = False
        tp.data.materials[0] = M['tape_mask']

    def mask_restore():
        for k, P in enumerate(drives):
            P['tape'].data.materials[0] = M['tape'][k]
    orig_plate = plate

    def plate2(i):
        mask_restore()
        emit_done()
        orig_plate(i)
    feats = {}
    for k, P in enumerate(drives):
        lab = 'ABCD'[3 - k]
        tp = P['tape']
        bpy.context.view_layer.update()
        vs = [tp.matrix_world @ v.co for v in tp.data.vertices]
        c = sum(vs, Vector()) / len(vs)
        feats[f'label_{lab}'] = tuple(c)
        feats[f'led_{lab}'] = tuple(P['led'].matrix_world @ Vector(P['led'].data.vertices[0].co))
    passes = [Pass('plate', 1, plate2, 'lit', 128, gpu_spp=512, notes='opaque plate, LEDs off, monitor glow at the top'),
              Pass('emit', 5, lambda i: (mask_restore(), emit(i)), 'lit', 32, gpu_spp=128, mode='static',
                   labels=['all', 'CAM A', 'CAM B', 'CAM C', 'CAM D'],
                   notes='LED emission + spill only on black (opaque): frame 0 all four, 1-4 one drive each; ADD, flicker '
                         'per drive on 8ths'),
              Pass('labels_mask', 4, lambda i: (mask_restore(), mask(i)), 'flat', 16, gpu_spp=64, transparent=True,
                   mode='static', labels=['CAM A', 'CAM B', 'CAM C', 'CAM D'],
                   notes='alpha = one tape label (with the plate DOF): x warm glow +0.8 stop at f570/574/578/582')]
    return dict(res=(W_PX, H_PX), passes=passes, feats=feats)


# ============================================================================= sheets, archive, selftest

ORDER = ['counter_macro', 'cam_hero', 'canister', 'studio_counter', 'envelope', 'print_src', 'prints', 'album_page',
         'drives']        # print_src before prints (the prints use its frames as textures)


def _checker(h, w, c=24):
    yy, xx = np.mgrid[0:h, 0:w]
    v = (((yy // c) + (xx // c)) % 2) * 30 + 40
    return np.dstack([v, v, v]).astype(np.float32) / 255.0


def contact_sheets(root=None, tag='finals', cell=360):
    """One sheet per asset (every pass folder, sequences as first/mid/last) over a checker, written to
    RWS/out/sheets3d/<tag>_<asset>.jpg; plus <tag>_all.jpg with every folder's first frame."""
    import cv2
    root = root or OUT
    os.makedirs(SHEETS, exist_ok=True)
    made = []
    firsts = []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        tiles = []
        if not os.path.isdir(os.path.join(root, name)):
            continue
        for folder in sorted(os.listdir(os.path.join(root, name))):
            d = os.path.join(root, name, folder)
            if not os.path.isdir(d):
                continue
            fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
            if not fs:
                continue
            pick = fs if len(fs) <= 3 else [fs[0], fs[len(fs) // 2], fs[-1]]
            for f in pick:
                im = _read4(os.path.join(d, f))
                hh, ww = im.shape[:2]
                sc_ = min(cell / ww, cell * 1.78 / hh)
                im = cv2.resize(im, (max(1, int(ww * sc_)), max(1, int(hh * sc_))), interpolation=cv2.INTER_AREA)
                a = im[:, :, 3:4].astype(np.float32) / 255.0
                bg = _checker(im.shape[0], im.shape[1])
                rgb = im[:, :, :3].astype(np.float32) / 255.0 * a + bg * (1 - a)
                t = np.zeros((int(cell * 1.78) + 28, cell, 3), np.float32) + 0.08
                t[:rgb.shape[0], :rgb.shape[1]] = rgb
                t = (t * 255).astype(np.uint8)
                cv2.putText(t, f'{name[:10]}/{folder}/{f[:-4]}', (6, t.shape[0] - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                            (220, 220, 220), 1, cv2.LINE_AA)
                tiles.append(t)
                if f == pick[0]:
                    firsts.append(t)
        if not tiles:
            continue
        p = os.path.join(SHEETS, f'{tag}_{name}.jpg')
        cv2.imwrite(p, _grid(tiles), [cv2.IMWRITE_JPEG_QUALITY, 88])
        made.append(p)
        print(p)
    if firsts:
        p = os.path.join(SHEETS, f'{tag}_all.jpg')
        cv2.imwrite(p, _grid(firsts, 8), [cv2.IMWRITE_JPEG_QUALITY, 85])
        made.append(p)
        print(p)
    return made


def _grid(tiles, maxcols=6):
    cols = min(maxcols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    th, tw = tiles[0].shape[:2]
    sheet = np.zeros((rows * th, cols * tw, 3), np.uint8)
    for i, t in enumerate(tiles):
        r_, c_ = divmod(i, cols)
        sheet[r_ * th:(r_ + 1) * th, c_ * tw:(c_ + 1) * tw] = t
    return sheet


def archive(quality=92):
    """Compressed restore copies into brand_reels/assets/sirf_36_shots/assets3d (git, kept < 58 MB): opaque frames
    as JPEG, RGBA frames as a JPEG colour plate + a PNG alpha plate ('<n>.a.png'), meta.json as is; folders without
    meta.json (unfinished) are skipped. Lowers the JPEG quality by itself if the pack would pass 58 MB."""
    import cv2
    if os.path.isdir(ARCHIVE):
        shutil.rmtree(ARCHIVE)
    os.makedirs(ARCHIVE)
    index = {}
    for name in sorted(os.listdir(OUT)):
        if not os.path.isdir(os.path.join(OUT, name)):
            continue
        for folder in sorted(os.listdir(os.path.join(OUT, name))):
            d = os.path.join(OUT, name, folder)
            if not os.path.exists(os.path.join(d, 'meta.json')):
                print('  skip (no meta.json):', d)
                continue
            od = os.path.join(ARCHIVE, name, folder)
            os.makedirs(od)
            for f in sorted(os.listdir(d)):
                src = os.path.join(d, f)
                if f == 'meta.json':
                    shutil.copy2(src, od)
                    continue
                if not (f.endswith('.png') and f[:-4].isdigit()):
                    continue
                im = _read4(src)
                key = f'{name}/{folder}/{f}'
                if im[:, :, 3].min() == 255:
                    cv2.imwrite(os.path.join(od, f[:-4] + '.jpg'), im[:, :, :3], [cv2.IMWRITE_JPEG_QUALITY, quality])
                    index[key] = 'jpg'
                else:
                    a = im[:, :, 3]
                    rgb_ = im[:, :, :3].copy()
                    if a.max() > 0:      # bleed colour into transparent pixels so JPEG blocks do not darken edges
                        dil = cv2.dilate(rgb_, np.ones((5, 5), np.uint8))
                        rgb_ = np.where((a > 0)[..., None], rgb_, dil)
                    cv2.imwrite(os.path.join(od, f[:-4] + '.jpg'), rgb_, [cv2.IMWRITE_JPEG_QUALITY, quality])
                    cv2.imwrite(os.path.join(od, f[:-4] + '.a.png'), a, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                    index[key] = 'jpg+a'
    with open(os.path.join(ARCHIVE, 'archive.json'), 'w') as fh:
        json.dump(dict(note='restore with: python pipeline/jawad_reels/assets3d_sirf_36_shots.py restore',
                       jpeg_quality=quality, files=index), fh, indent=1)
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(ARCHIVE) for f in fs)
    print(f'  archive {ARCHIVE}: {tot / 1e6:.1f} MB (JPEG q{quality}, {len(index)} frames)')
    if tot > 58e6 and quality > 70:
        return archive(quality - 6)
    return tot


def restore():
    """Rebuild RWS/assets3d/<name>/<pass>/ from the archive (frames first, meta.json last per folder)."""
    import cv2
    idx = json.load(open(os.path.join(ARCHIVE, 'archive.json')))['files']
    folders = set()
    for rel, kind in idx.items():
        dst = os.path.join(OUT, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        mp = os.path.join(os.path.dirname(dst), 'meta.json')
        if os.path.exists(mp):
            os.remove(mp)
        folders.add(os.path.dirname(rel))
        base = os.path.join(ARCHIVE, *rel.split('/'))[:-4]
        im = cv2.imread(base + '.jpg', cv2.IMREAD_COLOR)
        a = cv2.imread(base + '.a.png', cv2.IMREAD_UNCHANGED) if kind == 'jpg+a' else np.full(im.shape[:2], 255, np.uint8)
        cv2.imwrite(dst, np.dstack([im, a]))
    for rel in sorted(folders):
        src = os.path.join(ARCHIVE, *rel.split('/'), 'meta.json')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(OUT, *rel.split('/'), 'meta.json'))
    print(f'  restored {len(idx)} frames into', OUT)


EXPECT = dict(counter_macro=dict(plate=1, tick=16, tick15=1, led=1), cam_hero=dict(lit=1, flash=1, glow=1, crank=8),
              canister=dict(spin=16), studio_counter=dict(day1=1, day2=1, night=1, tin_day1=1, tin_day2=1, tin_night=1,
                                                          envelope_night=1),
              envelope=dict(flap=6, back=1, front=1), print_src=dict(src=5),
              prints=dict(p1=1, p2=1, p3=1, p4=1, p5=1, back=1, negatives=1), album_page=dict(page=1, sleeve=1),
              drives=dict(plate=1, emit=5, labels_mask=4))


def selftest(root=None):
    """Every expected folder has meta.json (finals), the right frame count, 8-bit RGBA PNGs, and loads in sprites3d."""
    import cv2
    root = root or OUT
    ok = True
    for name, folders in EXPECT.items():
        for folder, n in folders.items():
            d = os.path.join(root, name, folder)
            mp = os.path.join(d, 'meta.json')
            if not os.path.exists(mp):
                print(f'  MISSING {name}/{folder}')
                ok = False
                continue
            meta = json.load(open(mp))
            fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
            im = cv2.imread(os.path.join(d, fs[0]), cv2.IMREAD_UNCHANGED)
            good = len(fs) == n == meta['frames'] and im.dtype == np.uint8 and im.ndim == 3 and im.shape[2] == 4
            print(f'  {"ok " if good else "BAD"} {name}/{folder}: {len(fs)}/{n} frames, {im.shape[1]}x{im.shape[0]}, '
                  f'{im.dtype}, device {meta.get("device")}, preview={meta.get("preview")}')
            ok &= good
    try:
        import sprites3d as S3
        a = S3.Asset3D('canister', 'spin', root=root)
        print('  S3 load canister/spin:', a.mode, a.n, a.size)
    except Exception as e:  # noqa: BLE001
        print('  S3 load failed:', e)
        ok = False
    print('selftest', 'PASS' if ok else 'FAIL')
    return ok


def textures():
    """Regenerate every PIL texture into brand_reels/assets/sirf_36_shots/tex3d (needs the house fonts + scipy)."""
    global TEX_FORCE
    TEX_FORCE = True
    for fn in TEXTURES:
        print(' ', fn.tex_name, '->', fn())
    TEX_FORCE = False
    for i in range(16):
        print(i, tick_pose(i))
    assert tick_pose(0) == (35.0, 0.0) and tick_pose(15)[0] == 36.0


# ============================================================================= CLI

def main(argv):
    preview = '--preview' in argv
    samples, only, frames = None, None, None
    args = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--samples':
            samples = int(argv[i + 1])
            i += 2
            continue
        if a == '--only':
            only = argv[i + 1].split(',')
            i += 2
            continue
        if a == '--frames':
            frames = [int(v) for v in argv[i + 1].split(',')]
            i += 2
            continue
        if not a.startswith('--'):
            args.append(a)
        i += 1
    if not args:
        print(__doc__)
        return
    cmd = args[0]
    if cmd == 'sheet':
        return contact_sheets(OUT, 'finals')
    if cmd == 'previewsheet':
        return contact_sheets(PREVIEW, 'preview')
    if cmd in ('archive', 'pack'):
        return archive()
    if cmd == 'restore':
        return restore()
    if cmd == 'selftest':
        return selftest(PREVIEW if preview else OUT)
    if cmd == 'textures':
        return textures()
    names = ORDER if cmd == 'all' else args
    for n in names:
        if n not in ASSETS:
            raise SystemExit(f'unknown asset {n!r}; one of {ORDER}')
    for n in names:
        render_asset(n, preview=preview, samples=samples, only=only, frames=frames)


if __name__ == '__main__':
    main(sys.argv[1:])
