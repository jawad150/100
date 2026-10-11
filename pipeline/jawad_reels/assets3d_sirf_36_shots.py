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
TEX = os.path.join(RWS, 'out', 'tex3d')
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


def reset(res, samples=64, transparent=False):
    _bpy()
    sc = H.reset(res, samples, 'night')
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    cy = sc.cycles
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.015
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


def _save(im, name):
    os.makedirs(TEX, exist_ok=True)
    p = os.path.join(TEX, name)
    im.save(p)
    return p


def tex_dial(npos=38, size=2048, r_mm=13.0, dial_mm=30.0, digit_mm=1.85):
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
        tile = tile.resize((int(tw * 0.80), tw), Image.LANCZOS)    # condensed dial numerals
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
           window=(33.0, -9.0), win_r=4.5, dial_r=15.0, dial_txt_r=13.0, npos=38,
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
    wn = wear(g, b, '#FFFFFF', 0.03, '#FFFFFF', edge=0.0, dust=0.25, prints=0.5, scratch=0.9, seed=7.0)
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
    dial_c = (m(winx), m(winy + C['dial_txt_r']), m(61.0))
    dial = cylinder('dial', (0, 0, 0), m(C['dial_r']), m(0.5), M['dial'], seg=192)
    dial.data.transform(Matrix.Translation((0, 0, -m(0.25))))
    dial.location = dial_c
    P['dial'] = dial
    P['dial_c'] = dial_c
    # dial well: dark floor so the hole reads deep
    cylinder('dial_well', (m(winx), m(winy), m(60.3)), m(4.4), m(0.2), M['inner'], seg=48)
    hd = 2.1
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
    box('flash_reflector', (m(flx), m(D / 2 - 2.6), m(flz)), (m(21), m(3.6), m(11)), M['reflector'])
    cylinder('xenon', (m(flx), m(D / 2 - 1.2), m(flz)), m(0.9), m(18), M['xenon'], axis='X', seg=32)
    fe = box('flash_emit', (m(flx), m(D / 2 - 1.2), m(flz)), (m(17), m(0.9), m(0.9)), M['flash_emit'])
    ge = box('glow_emit', (m(flx), m(D / 2 - 2.0), m(flz)), (m(19), m(0.5), m(9)), M['glow_emit'])
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


def r_home(subject, cam_loc, key=40.0, scale=1.0):
    L = []
    L.append(lamp('key', 'AREA', rig_point(subject, cam_loc, -55, 45, 1.1), key, kelvin=2700, target=subject,
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
    def __init__(self, folder, n=1, setup=None, kind='lit', spp=64, region=None, crop=False, key=None, labels=None,
                 post=None, transparent=False, mode=None, loop=False, notes='', feats=None, extra=None, seq_preview=None):
        self.folder, self.n, self.setup, self.kind, self.spp = folder, n, setup, kind, spp
        self.region, self.crop, self.key, self.labels, self.post = region, crop, key, labels, post
        self.transparent, self.mode, self.loop, self.notes = transparent, mode, loop, notes
        self.feats, self.extra, self.seq_preview = feats, extra or {}, seq_preview


class Ctx:
    def __init__(self, preview, q):
        self.preview, self.q = preview, q


def settings(sc, kind, spp):
    cy = sc.cycles
    if kind == 'flat':
        cy.samples = spp
        cy.use_denoising = False
        cy.use_adaptive_sampling = False
    else:
        cy.samples = spp
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


def render_asset(name, preview=False, samples=None, only=None):
    import cv2
    _bpy()
    spec = ASSETS[name]
    q = 0.6 if preview else 1.0
    t0 = time.time()
    S = spec['build'](Ctx(preview, q))
    sc = bpy.context.scene
    full = S['res']
    res = (full[0] // 2, full[1] // 2) if preview else tuple(full)
    sc.render.resolution_x, sc.render.resolution_y = res
    bpy.context.view_layer.update()
    k = res[0] / full[0]
    root = PREVIEW if preview else OUT
    feats_w = S.get('feats', {})
    print(f'[{name}] scene built in {time.time() - t0:.1f}s; {res[0]}x{res[1]}', flush=True)
    results = {}
    for P in S['passes']:
        if only and P.folder not in only:
            continue
        outdir = os.path.join(root, name, P.folder)
        os.makedirs(outdir, exist_ok=True)
        for f in os.listdir(outdir):
            if f.endswith('.png') or f == 'meta.json':
                os.remove(os.path.join(outdir, f))
        sc.render.film_transparent = P.transparent
        if P.region:
            x0, y0, x1, y1 = [int(round(v * k)) for v in P.region]
            B.set_border(sc, (x0, y0, x1, y1), res)
        else:
            sc.render.use_border = False
            sc.render.use_crop_to_border = False
        frames = list(range(P.n))
        if preview and P.n > 3:
            frames = P.seq_preview if P.seq_preview is not None else sorted({0, P.n // 2, P.n - 1})
        raws, times, done = {}, {}, {}
        for i in frames:
            kk = P.key(i) if P.key else i
            if kk in done:
                raws[i] = done[kk]
                continue
            if P.setup:
                P.setup(i)
            spp = (16 if preview else (samples if (samples and P.kind != 'flat') else P.spp))
            if preview and P.kind == 'flat':
                spp = min(P.spp, 16)
            settings(sc, P.kind, spp)
            p = os.path.join(outdir, f'_raw_{i:04d}.png')
            t1 = time.time()
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            times[i] = round(time.time() - t1, 1)
            print(f'  {name}/{P.folder}[{i}]: {times[i]}s ({P.kind}, {spp} spp)', flush=True)
            raws[i] = p
            done[kk] = p
        ims = {i: cv2.imread(p, cv2.IMREAD_UNCHANGED) for i, p in raws.items()}
        for i in ims:
            if ims[i].shape[2] == 3:
                ims[i] = np.dstack([ims[i], np.full(ims[i].shape[:2], 255, np.uint8)])
        if P.post:
            ims = P.post(ims, k) or ims
        off = [0, 0]
        if P.region:
            off = [int(round(P.region[0] * k)), int(round(P.region[1] * k))]
        crop_rect = None
        if P.crop:
            bb = _alpha_bbox(list(ims.values()))
            pad = int(round(CROP_PAD * k))
            h0, w0 = next(iter(ims.values())).shape[:2]
            crop_rect = [max(0, bb[0] - pad), max(0, bb[1] - pad), min(w0, bb[2] + pad), min(h0, bb[3] + pad)]
            for i in ims:
                ims[i] = ims[i][crop_rect[1]:crop_rect[3], crop_rect[0]:crop_rect[2]]
            off = [off[0] + crop_rect[0], off[1] + crop_rect[1]]
        if isinstance(ims, dict) and P.labels and len(ims) != P.n and not preview:
            pass
        outs = []
        order = sorted(ims)
        for j, i in enumerate(order):
            fn = os.path.join(outdir, f'{(i if not preview else j):04d}.png')
            cv2.imwrite(fn, ims[i], [cv2.IMWRITE_PNG_COMPRESSION, 6])
            outs.append(fn)
        for p in set(raws.values()):
            if os.path.exists(p):
                os.remove(p)
        fw = dict(feats_w)
        if P.feats:
            fw.update(P.feats)
        fframe = {kk: [round(v[0] / k, 1), round(v[1] / k, 1)] for kk, v in
                  ((kk, to_px(p)) for kk, p in fw.items())}
        flocal = {kk: [round(v[0] - off[0] / k, 1), round(v[1] - off[1] / k, 1)] for kk, v in fframe.items()}
        size = list(next(iter(ims.values())).shape[1::-1])
        meta = dict(name=name, variant=P.folder, mode=P.mode or ('static' if P.n == 1 else 'anim'), frames=P.n,
                    fps_hint=30, size=size, loop=P.loop, labels=P.labels or [], notes=P.notes or spec['notes'],
                    features=flocal, features_frame=fframe, frame_xy=[off[0] / k, off[1] / k],
                    frame_size=list(full), samples=(16 if preview else (samples or P.spp)), kind=P.kind,
                    preview=bool(preview), render_seconds=times, device='CPU', threads=THREADS, camera=cam_meta(),
                    builder=BUILDER, unique_renders=len(set(raws.values())))
        if preview:
            meta['preview_frames'] = frames
        meta.update(S.get('extra', {}))
        meta.update(P.extra)
        H.write_meta(outdir, **meta)
        results[P.folder] = meta
        print(f'  -> {outdir} {size} ({len(outs)} files) {sum(times.values()):.0f}s', flush=True)
    print(f'[{name}] total {time.time() - t0:.0f}s', flush=True)
    return results


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


@asset('counter_macro', 'Top-rear macro of the frame counter: dial 35 in the domed window, the thumb wheel at the '
                        'back-right, flash-ready LED on the back. tick = region render that drops onto the plate.')
def build_counter_macro(ctx):
    sc = reset((W_PX, H_PX), 128)
    M = mats_camera()
    S = home_set(table_far=0.42, table_near=0.5)
    P = build_camera(M, ctx.q)
    win = Vector(P['window_c'])
    # 35 deg down from behind-right (az 28 deg toward +X from straight behind)
    el, az, dist = math.radians(35), math.radians(28), 0.172
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam = camera('CAM_MACRO', 100.0, tuple(win + d * dist), tuple(win), fstop=4.0, focus=dist)
    place_on_screen(cam, tuple(win - Vector((0, 0, 0.0017))), (540, 1120))
    bpy.context.view_layer.update()
    r_home(tuple(win), cam.location, key=18.0)
    home_room([(ray_hit_z((200, 330), 0.012), 0.012, 6.0), (ray_hit_z((930, 170), 0.012), 0.012, 6.0)])
    world_color('#170A07', 0.25)
    set_counter(P, 35.0, 0.0)
    led_m = bpy.data.materials['led_die']

    def plate(i):
        set_counter(P, 35.0, 0.0)
        set_emit(led_m, 0.0)

    def tick(i):
        dv, wd = tick_pose(i)
        set_counter(P, dv, wd)
        set_emit(led_m, 0.0)

    holdouts = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name not in ('led_die', 'led_lens')]
    lights = [o for o in bpy.context.scene.objects if o.type == 'LIGHT']
    bulbs = [o for o in bpy.context.scene.objects if o.name.startswith('bulb')]

    def led(i):
        set_counter(P, 35.0, 0.0)
        for o in holdouts:
            o.is_holdout = True
        for o in lights + bulbs:
            o.hide_render = True
        world_color('#000000', 0.0)
        set_emit(led_m, 60.0)

    feats = dict(window_centre=tuple(win), led=P['led'], wheel_edge=P['wheel_c'], shutter=P['shutter_c'],
                 dial_centre=P['dial_c'])
    passes = [Pass('plate', 1, plate, 'lit', 128, notes='opaque plate, dial at 35, LED off'),
              Pass('tick', 16, tick, 'lit', 96, region=(360, 880, 1080, 1400), key=tick_pose, mode='anim',
                   labels=[f'dial {tick_pose(i)[0]:.2f} wheel {tick_pose(i)[1]:.0f}' for i in range(16)],
                   notes='region x360-1080 y880-1400 of the plate camera (paste at frame_xy); f0 = plate pose; '
                         'ratchet steps start f0/4/8/11, dial lands 36 on f15; held frames are copies',
                   seq_preview=[0, 6, 15]),
              Pass('led', 1, led, 'flat', 16, transparent=True, crop=True,
                   notes='LED emission only (straight alpha), paste at frame_xy, scale brightness 0.3-1.0')]
    return dict(res=(W_PX, H_PX), passes=passes, feats=feats,
                extra=dict(px_per_mm_window=round(px_per_mm_at(tuple(win)), 2)))


# ============================================================================= sheets, archive, selftest

def _checker(h, w, c=24):
    yy, xx = np.mgrid[0:h, 0:w]
    v = (((yy // c) + (xx // c)) % 2) * 30 + 40
    return np.dstack([v, v, v]).astype(np.float32) / 255.0


def contact_sheets(root=None, tag='finals', cell=360):
    """One sheet per asset (every pass folder, sequences as first/mid/last) over a checker, plus a 360-px-wide
    phone-size sheet of the plates. Written to RWS/out/sheets3d/<tag>_<asset>.jpg."""
    import cv2
    root = root or OUT
    os.makedirs(SHEETS, exist_ok=True)
    made = []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        tiles = []
        for folder in sorted(os.listdir(os.path.join(root, name))):
            d = os.path.join(root, name, folder)
            fs = sorted(f for f in os.listdir(d) if f.endswith('.png') and f[:-4].isdigit())
            if not fs:
                continue
            pick = fs if len(fs) <= 3 else [fs[0], fs[len(fs) // 2], fs[-1]]
            for f in pick:
                im = cv2.imread(os.path.join(d, f), cv2.IMREAD_UNCHANGED)
                if im.shape[2] == 3:
                    im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
                hh, ww = im.shape[:2]
                sc_ = min(cell / ww, cell * 1.78 / hh)
                im = cv2.resize(im, (max(1, int(ww * sc_)), max(1, int(hh * sc_))), interpolation=cv2.INTER_AREA)
                a = im[:, :, 3:4].astype(np.float32) / 255.0
                bg = _checker(im.shape[0], im.shape[1])
                rgb = im[:, :, :3].astype(np.float32) / 255.0 * a + bg * (1 - a)
                t = np.zeros((int(cell * 1.78) + 28, cell, 3), np.float32) + 0.08
                t[:rgb.shape[0], :rgb.shape[1]] = rgb
                t = (t * 255).astype(np.uint8)
                cv2.putText(t, f'{folder}/{f[:-4]}', (6, t.shape[0] - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (220, 220, 220), 1, cv2.LINE_AA)
                tiles.append(t)
        if not tiles:
            continue
        cols = min(6, len(tiles))
        rows = (len(tiles) + cols - 1) // cols
        th, tw = tiles[0].shape[:2]
        sheet = np.zeros((rows * th, cols * tw, 3), np.uint8)
        for i, t in enumerate(tiles):
            r_, c_ = divmod(i, cols)
            sheet[r_ * th:(r_ + 1) * th, c_ * tw:(c_ + 1) * tw] = t
        p = os.path.join(SHEETS, f'{tag}_{name}.jpg')
        cv2.imwrite(p, sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
        made.append(p)
        print(p)
    return made


def pack():
    """Copy the finals to brand_reels/assets/sirf_36_shots/assets3d (PNG, max compression; opaque plates are
    re-encoded without the alpha channel) so a fresh container can restore without re-rendering."""
    import cv2
    if os.path.isdir(ARCHIVE):
        shutil.rmtree(ARCHIVE)
    total = 0
    for name in sorted(os.listdir(OUT)):
        for folder in sorted(os.listdir(os.path.join(OUT, name))):
            src = os.path.join(OUT, name, folder)
            if not os.path.exists(os.path.join(src, 'meta.json')):
                print('skip (no meta.json):', src)
                continue
            dst = os.path.join(ARCHIVE, name, folder)
            os.makedirs(dst, exist_ok=True)
            for f in sorted(os.listdir(src)):
                sp, dp = os.path.join(src, f), os.path.join(dst, f)
                if f.endswith('.png'):
                    im = cv2.imread(sp, cv2.IMREAD_UNCHANGED)
                    if im.ndim == 3 and im.shape[2] == 4 and im[:, :, 3].min() == 255:
                        im = im[:, :, :3]
                    cv2.imwrite(dp, im, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                else:
                    shutil.copy2(sp, dp)
                total += os.path.getsize(dp)
    print(f'archive {ARCHIVE}: {total / 1e6:.1f} MB')
    return total


def restore():
    """Archive -> RWS/assets3d (opaque plates come back as RGBA so every folder is uniform)."""
    import cv2
    n = 0
    for name in sorted(os.listdir(ARCHIVE)):
        for folder in sorted(os.listdir(os.path.join(ARCHIVE, name))):
            src = os.path.join(ARCHIVE, name, folder)
            dst = os.path.join(OUT, name, folder)
            os.makedirs(dst, exist_ok=True)
            fs = sorted(os.listdir(src))
            for f in fs:
                if f.endswith('.png'):
                    im = cv2.imread(os.path.join(src, f), cv2.IMREAD_UNCHANGED)
                    if im.shape[2] == 3:
                        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
                    cv2.imwrite(os.path.join(dst, f), im, [cv2.IMWRITE_PNG_COMPRESSION, 4])
                    n += 1
            shutil.copy2(os.path.join(src, 'meta.json'), os.path.join(dst, 'meta.json'))   # meta last
    print(f'restored {n} PNGs into {OUT}')


def selftest():
    """Builds the PIL textures (no Cycles) and checks the tick table + palette."""
    _bpy()
    for i in range(16):
        print(i, tick_pose(i))
    assert tick_pose(0) == (35.0, 0.0) and tick_pose(15)[0] == 36.0
    print('textures:', [os.path.basename(f()) for f in (tex_dial, tex_bezel_ring, tex_doily)])
    print('selftest ok')


# ============================================================================= CLI

def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    preview = '--preview' in argv
    samples = None
    only = None
    for i, a in enumerate(argv):
        if a == '--samples':
            samples = int(argv[i + 1])
        if a == '--only':
            only = argv[i + 1].split(',')
    args = [a for a in args if not a.isdigit() and (only is None or a not in [','.join(only)])]
    if not args:
        print(__doc__)
        return
    cmd = args[0]
    if cmd == 'sheet':
        return contact_sheets(OUT, 'finals')
    if cmd == 'previewsheet':
        return contact_sheets(PREVIEW, 'preview')
    if cmd == 'pack':
        return pack()
    if cmd == 'restore':
        return restore()
    if cmd == 'selftest':
        return selftest()
    names = list(ASSETS) if cmd == 'all' else args
    for n in names:
        render_asset(n, preview=preview, samples=samples, only=only)


if __name__ == '__main__':
    main(sys.argv[1:])
