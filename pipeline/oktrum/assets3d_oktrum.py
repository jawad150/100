"""assets3d_oktrum.py - 3D props for the Oktrum reels (Blender/Cycles, bpy as a module).

Premium glossy "SaaS 3D" props (glass, chrome, gold, emissive-blue beads with a soft cyan rim) rendered as
transparent RGBA PNG sequences in the shared 3D asset spec (see sprites3d.py / TOOLKIT.md section 7):

    <WS>/assets3d/<name>/<folder>/0000.png ... + meta.json      folder = <variant> (yaw) or <variant>_<mode>

Reuses the SDF mesher, materials and render loop helpers of assets3d_icons.py (imported as I); its brand table
is replaced IN THIS PROCESS ONLY by the Oktrum tokens below, and the world + light rig are Oktrum's own (cool
navy night with cyan / violet rims, ice-white #F3F6FF day).

CLI
---
    python3 assets3d_oktrum.py <name> [<name> ...] [--preview] [--variant V] [--mode M] [--frames 0,10,20]
                               [--samples N]
    python3 assets3d_oktrum.py sheet <name> [...]          finals contact sheet -> <WS>/out/selftest/okt3d_<name>.png
    python3 assets3d_oktrum.py previewsheet <name> [...]   same for the --preview renders
    python3 assets3d_oktrum.py fit                         re-derive the halftone lattice of brand/logo_mark.png
    env OKT_SAMPLES (final spp, default 16; adaptive + OpenImageDenoise, fixed seed), OKT_THREADS (default 2),
    SKIP_EXISTING=1 resumes an interrupted sequence. Previews: half size, 10 spp, first/mid/last frames,
    written to <WS>/out/preview3d/.

Assets (name: folders, mode, frames, size)
------------------------------------------
    okt_mark     night_spin   spin 72  1000   the halftone dot sphere logo in 3D: glossy emissive-BLUE domed beads
                 night_anim   anim 60         (cyan fresnel rim) on a sphere. The bead lattice (lat/long rows 4.8 deg
                                              apart, odd rows offset half a step, pole tilted up/towards the viewer)
                                              and the bead radius (linear in n.L, L right-front) are FITTED to
                                              brand/logo_mark.png, so spin frame 0 matches the logo dot for dot. The
                                              falloff stays fixed to the view while the lattice turns (a turning
                                              halftone globe); an invisible holdout core hides the back beads.
                                              anim: beads swirl in from a wider shell and settle while the lattice
                                              swings from yaw -50 to 0; last frame == spin frame 0 (the logo pose).
    shield_lock  day          yaw 49   900    thick violet->blue tinted glass shield, cyan edge glow, chrome padlock
                 day_anim     anim 48         shield pops in (overshoot), padlock drops, shackle clicks shut
                                              (meta click_frame); last frame == yaw 0.
    coin_btc     night_spin   spin 72  900    polished gold coin, Bitcoin sign both faces, reeded rim
    coin_usd     night_spin   spin 72  900    silver-chrome coin, dollar sign both faces
    gold_bar     night        yaw 49   720    gold bullion bar, "999.9" stamped on the face, tilted to the viewer
    candles3d    night        yaw 49   1000   6 glass candlesticks (UP green / DOWN red) on a rising trend, thin
                                              wicks, emissive cores; features c0..c5 (body tops)
    candle_red   day          yaw 49   1000   one tall DOWN-red glass candle with wicks
    chip         night        yaw 49   720    black glass processor chip, glowing blue-cyan core, gold pins

Load with sprites3d:
    S3.get('okt_mark', 'night', mode='spin'); S3.get('okt_mark', 'night', mode='anim')
    S3.get('shield_lock', 'day'); S3.get('shield_lock', 'day', mode='anim')   # meta click_frame
    S3.get('coin_btc', 'night', mode='spin'); S3.get('gold_bar', 'night'); S3.get('chip', 'night') ...
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
import assets3d_icons as I  # noqa: E402

WS = I.WS
OUT3D = os.path.join(WS, 'assets3d')
PREVIEW3D = os.path.join(WS, 'out', 'preview3d')
SELFTEST = os.path.join(WS, 'out', 'selftest')

OKT = {
    'BLUE': '#5170FF', 'VIOLET': '#8465F4', 'CYAN': '#81D4E6', 'NAVY': '#07091A', 'UP': '#34D399',
    'DOWN': '#F87171', 'IVORY': '#F3F6FF', 'AMBER': '#F2C46D', 'GOLD_DEEP': '#D99A3A', 'NAVY_HI': '#1B2466',
    'SILVER': '#E4E8F0', 'INK': '#0B0E24',
}
I.BRAND.update(OKT)            # this process only: I.hexlin / materials resolve Oktrum token names
SAMPLES = int(os.environ.get('OKT_SAMPLES', '16'))
I.THREADS = int(os.environ.get('OKT_THREADS', '2'))
PREVIEW_SAMPLES = 10
hexlin, mixlin = I.hexlin, I.mixlin
bpy = None
Vector = None


def _bpy():
    global bpy, Vector
    if bpy is None:
        I._bpy()
        bpy, Vector = I.bpy, I.Vector
    return bpy


def _c(c):
    return hexlin(c) if isinstance(c, str) else tuple(c)


def ease_out_cubic(t):
    t = np.clip(t, 0, 1)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.6):
    t = np.clip(t, 0, 1) - 1.0
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


# ============================================================================= world + rig

def world(variant):
    """night: navy dome, CYAN soft-box back-right, VIOLET back-left, cool top light.
    day: ice-white dome over a cool grey-blue floor, pale cyan / violet blobs, a dark flag behind the camera."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W_' + variant)
    sc.world = w
    w.use_nodes = True
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
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(nrm.outputs[0], sep.inputs[0])

    def blob(d, c0, c1, col, s):
        dot = nt.nodes.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = Vector(d).normalized()
        nt.links.new(nrm.outputs[0], dot.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.interpolation_type = 'SMOOTHERSTEP'
        mr.inputs['From Min'].default_value = c0
        mr.inputs['From Max'].default_value = c1
        mr.inputs['To Max'].default_value = s
        nt.links.new(dot.outputs['Value'], mr.inputs['Value'])
        mul = nt.nodes.new('ShaderNodeVectorMath')
        mul.operation = 'SCALE'
        mul.inputs[0].default_value = _c(col)
        nt.links.new(mr.outputs[0], mul.inputs['Scale'])
        return mul.outputs[0]

    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = -0.6
    mr.inputs['From Max'].default_value = 0.9
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(mr.outputs[0], mix.inputs['Factor'])
    if variant == 'night':
        lo, hi = _c('NAVY'), tuple(x * 0.7 for x in _c('NAVY_HI'))
        blobs = [blob((0.85, 0.75, 0.35), 0.55, 0.92, 'CYAN', 1.6),
                 blob((-0.9, 0.65, 0.1), 0.6, 0.93, 'VIOLET', 1.3),
                 blob((0.0, -0.4, 0.9), 0.75, 0.97, (0.86, 0.92, 1.0), 0.8)]
        strength = 1.0
    else:
        lo, hi = tuple(x * 0.55 for x in _c('#8E9CC4')), _c('IVORY')
        blobs = [blob((0.85, 0.7, 0.3), 0.55, 0.92, mixlin('IVORY', 'CYAN', 0.6), 0.7),
                 blob((-0.9, 0.6, 0.2), 0.6, 0.93, mixlin('IVORY', 'VIOLET', 0.5), 0.5),
                 blob((0.0, -0.4, 0.9), 0.75, 0.97, (1.0, 1.0, 1.0), 0.6),
                 blob((0.0, -1.0, 0.05), 0.2, 0.85, (-0.55, -0.52, -0.45), 1.0)]
        strength = 0.85
    mix.inputs['A'].default_value = lo + (1,)
    mix.inputs['B'].default_value = hi + (1,)
    acc = mix.outputs['Result']
    for b in blobs:
        add = nt.nodes.new('ShaderNodeVectorMath')
        add.operation = 'ADD'
        nt.links.new(acc, add.inputs[0])
        nt.links.new(b, add.inputs[1])
        acc = add.outputs[0]
    nt.links.new(acc, bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    return w


def rig(variant, s=1.0, key=1.0, metal=False, rims=1.0):
    """Key top-left-front + fill front-right (diffuse only), reflection cards for the highlights, coloured rims
    behind (night: CYAN right, VIOLET left; day: pale cyan / white). metal=True adds the soft-box wall and
    glint strips polished metal needs."""
    e = s * s
    cool = (0.96, 0.98, 1.0)
    k = key * (0.8 if variant == 'day' else 1.0)
    A, C = I.area, I.card
    A('key', (-3.4 * s, -4.4 * s, 4.4 * s), (4.0 * s, 4.0 * s), 520 * e * k, cool, glossy=False, shape='DISK')
    A('fill', (4.6 * s, -4.2 * s, 0.6 * s), (3.5 * s, 3.5 * s), 120 * e * k, (0.95, 0.97, 1.0), glossy=False,
      shape='DISK')
    C('kcard', (-3.0 * s, -4.0 * s, 4.0 * s), (3.4 * s, 2.4 * s), (1.0, 1.0, 1.0), 2.2, shape='oval', soft=0.35)
    C('kstrip', (-1.6 * s, -3.0 * s, 4.6 * s), (2.6 * s, 0.32 * s), (1.0, 1.0, 1.0), 6.0, soft=0.3)
    C('frontcard', (1.2 * s, -6.5 * s, 0.4 * s), (6.0 * s, 3.0 * s), (0.92, 0.95, 1.0), 0.22, shape='oval', soft=0.45)
    if metal:
        C('m_front', (0.0, -7.5 * s, -0.55 * s), (9.0 * s, 4.4 * s), (0.92, 0.95, 1.0), 1.3, shape='oval', soft=0.32)
        C('m_top', (0.0, -3.0 * s, 6.0 * s), (6.0 * s, 2.0 * s), (1.0, 1.0, 1.0), 2.4, soft=0.4)
        for j, (x, y) in enumerate(((-4.3, -6.2), (-7.0, -2.6), (4.3, -6.2), (7.0, -2.6))):
            C(f'm_glint{j}', (x * s, y * s, 0.2 * s), (0.9 * s, 6.0 * s), (0.95, 0.97, 1.0), 3.0, soft=0.3)
        C('m_low', (0.0, -5.0 * s, -3.5 * s), (6.0 * s, 1.2 * s), _c('CYAN'), 0.9, soft=0.4)
    if variant == 'night':
        A('rim_cyan', (4.2 * s, 3.4 * s, 1.6 * s), (1.4 * s, 4.5 * s), 1300 * e * rims, 'CYAN')
        A('rim_violet', (-4.4 * s, 3.0 * s, 0.2 * s), (1.4 * s, 4.5 * s), 1000 * e * rims, 'VIOLET')
        A('top', (0.4 * s, 1.8 * s, 5.2 * s), (3.0 * s, 1.2 * s), 200 * e, (0.86, 0.92, 1.0))
    else:
        A('rim_cyan', (4.2 * s, 3.4 * s, 1.6 * s), (1.4 * s, 4.5 * s), 900 * e * rims, mixlin('IVORY', 'CYAN', 0.55))
        A('rim_white', (-4.4 * s, 3.0 * s, 0.6 * s), (1.4 * s, 4.5 * s), 700 * e * rims, (0.95, 0.96, 1.0))
        A('top', (0.4 * s, 1.8 * s, 5.2 * s), (3.0 * s, 1.2 * s), 200 * e, (1.0, 1.0, 1.0))


# ============================================================================= materials

def _nodes(m):
    return m.node_tree.nodes, m.node_tree.links


def m_holdout(name='holdout'):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    h = nt.nodes.new('ShaderNodeHoldout')
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(h.outputs[0], o.inputs['Surface'])
    return m


def m_chrome(name, tint='SILVER', rough=0.07):
    m, b, nt = I._principled(name)
    b.inputs['Base Color'].default_value = _c(tint) + (1,)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    return m


def m_tinted_glass(name, c_lo, c_hi, z0, z1, rough=0.06, ior=1.45, edge=None, edge_str=0.0, axis='Z',
                   emit=None, emit_str=0.0):
    """Clear glass whose tint ramps from c_lo to c_hi along an object axis (object coords), with an optional
    fresnel edge glow (emission at grazing angles)."""
    m, b, nt = I._principled(name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sp.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value = z0
    mr.inputs['From Max'].default_value = z1
    nt.links.new(sp.outputs[axis], mr.inputs['Value'])
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.inputs['A'].default_value = _c(c_lo) + (1,)
    mx.inputs['B'].default_value = _c(c_hi) + (1,)
    nt.links.new(mr.outputs[0], mx.inputs['Factor'])
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['IOR'].default_value = ior
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Coat Roughness'].default_value = 0.02
    if edge:
        lw = nt.nodes.new('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.4
        r2 = nt.nodes.new('ShaderNodeMapRange')
        r2.inputs['From Min'].default_value = 0.3
        r2.inputs['From Max'].default_value = 1.0
        r2.inputs['To Max'].default_value = edge_str
        nt.links.new(lw.outputs['Facing'], r2.inputs['Value'])
        b.inputs['Emission Color'].default_value = _c(edge) + (1,)
        nt.links.new(r2.outputs['Result'], b.inputs['Emission Strength'])
    elif emit:
        b.inputs['Emission Color'].default_value = _c(emit) + (1,)
        b.inputs['Emission Strength'].default_value = emit_str
    return m


# ============================================================================= mesh helpers

def mesh_obj(name, V, F, mat=None, parent=None, smooth=True):
    """Plain mesh from numpy verts (Blender coords) + quad faces."""
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set('co', np.asarray(V, np.float32).ravel())
    F = np.asarray(F, np.int32)
    me.loops.add(F.size)
    me.loops.foreach_set('vertex_index', F.ravel())
    me.polygons.add(len(F))
    me.polygons.foreach_set('loop_start', np.arange(0, F.size, F.shape[1], dtype=np.int32))
    me.update(calc_edges=True)
    me.polygons.foreach_set('use_smooth', np.full(len(F), smooth))
    if mat is not None:
        me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    return o


def cube_sphere(k=4):
    """Unit quad-sphere (subdivided cube projected to the sphere): verts (n, 3), quads (m, 4)."""
    idx = {}
    V, F = [], []

    def vid(p):
        key = tuple(np.round(p, 6))
        if key not in idx:
            idx[key] = len(V)
            V.append(p)
        return idx[key]
    t = np.linspace(-1, 1, k + 1)
    for ax in range(3):
        for sgn in (-1, 1):
            u_ax, v_ax = [a for a in range(3) if a != ax]
            for i in range(k):
                for j in range(k):
                    q = []
                    for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                        p = np.zeros(3)
                        p[ax] = sgn
                        p[u_ax] = t[i + di]
                        p[v_ax] = t[j + dj]
                        q.append(vid(tuple(p / np.linalg.norm(p))))
                    n = np.cross(np.array(V[q[1]]) - V[q[0]], np.array(V[q[2]]) - V[q[0]])
                    if np.dot(n, V[q[0]]) < 0:
                        q = q[::-1]
                    F.append(q)
    return np.array(V, float), np.array(F, int)


def ico_to_bl(P):
    """icon frame (x right, y up, z to viewer) -> Blender (X right, Y away from camera, Z up)."""
    P = np.asarray(P, float)
    return np.stack([P[..., 0], -P[..., 2], P[..., 1]], -1)


def sdf(name, F, bounds, res, mat, parent, shadow=True, q=1.0):
    return I.sdf_object(name, F, bounds, max(48, int(res * q)), mat, parent, icon_frame=True, shadow=shadow)


# ============================================================================= camera

def frame_points(allp, res, fill=0.8, elev=5.0, lens=80.0):
    """80 mm camera `elev` degrees above, aimed so the point cloud (world coords, all poses) fills `fill` of
    the frame with its bbox centred (lens shift). Same maths as assets3d_icons.frame_camera."""
    sc = bpy.context.scene
    aspect = res[0] / res[1]
    cam_d = bpy.data.cameras.new('cam')
    cam_d.lens = lens
    cam_d.sensor_fit = 'AUTO'
    cam_d.sensor_width = 36.0
    cam = bpy.data.objects.new('cam', cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    c = (allp.min(0) + allp.max(0)) / 2
    el = math.radians(elev)
    fov_half = math.atan(18.0 / lens)
    tz = c[2]
    dist = 6.0
    shift = np.zeros(2)
    for _ in range(8):
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
        span = max((x1 - x0) / (1 if aspect >= 1 else 1), (y1 - y0)) / 2
        shift = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        dist *= span / fill
    cam.location = Vector(cam_pos.tolist())
    I._aim(cam, (c[0], 0, tz))
    cam_d.shift_x = shift[0] / 2 * (1 if aspect >= 1 else aspect)
    cam_d.shift_y = shift[1] / 2 / (aspect if aspect >= 1 else 1)
    cam_d.clip_start = 0.05
    cam_d.clip_end = 200
    return cam


def scene_points(root, max_pts=60000):
    bpy.context.view_layer.update()
    pts = []
    for o in [root] + list(root.children_recursive):
        if o.type != 'MESH' or o.hide_render or o.get('noframe'):
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


# ============================================================================= registry + render loop

ASSETS = {}
YAW_RANGE = (-40.0, 40.0)


def asset(name, folders, size, notes='', samples=1.0):
    """folders: list of (variant, mode, frames)."""
    def deco(fn):
        ASSETS[name] = dict(build=fn, folders=folders, size=size, notes=notes, spp=samples)
        return fn
    return deco


def yaw_of(i, n):
    return YAW_RANGE[0] + (YAW_RANGE[1] - YAW_RANGE[0]) * i / max(n - 1, 1)


def _folder(variant, mode):
    return variant if mode == 'yaw' else f'{variant}_{mode}'


def render_asset(name, variant, mode, preview=False, frames=None, samples=None):
    _bpy()
    spec = ASSETS[name]
    fl = [f for f in spec['folders'] if f[0] == variant and f[1] == mode]
    if not fl:
        raise SystemExit(f'{name}: no folder {variant}/{mode}; has {spec["folders"]}')
    n = fl[0][2]
    size = tuple(spec['size'])
    if preview:
        size = (size[0] // 2, size[1] // 2)
    spp = samples or (PREVIEW_SAMPLES if preview else int(round(SAMPLES * spec['spp'])))
    sc = I.reset(size, spp, variant)
    root = I.empty('root')
    q = 0.6 if preview else 1.0
    opts = spec['build'](root, variant, q) or {}
    world(variant)
    rig(variant, opts.get('rig_scale', 1.0), opts.get('key', 1.0), metal=opts.get('metal', False),
        rims=opts.get('rims', 1.0))
    if opts.get('glass'):
        sc.cycles.max_bounces = 12
        sc.cycles.transmission_bounces = 12
        sc.cycles.glossy_bounces = 4
    anim = opts.get('anim')            # callable(i, n) setting the anim pose (frame n-1 == the rest pose)
    rest = opts.get('rest')            # callable() setting the rest pose for yaw / spin

    # one camera per asset: frame the union of every mode's poses
    pts = []
    for (_, m, nn) in spec['folders']:
        if opts.get('frame_modes') and m not in opts['frame_modes']:
            continue
        if m == 'anim' and anim:
            for i in range(0, nn, 3):
                root.rotation_euler = (0, 0, 0)
                anim(i, nn)
                pts.append(scene_points(root, 20000))
        else:
            if rest:
                rest()
            angs = np.linspace(*YAW_RANGE, 9) if m == 'yaw' else np.arange(0, 360, 15)
            for a in angs:
                root.rotation_euler = (0, 0, math.radians(a))
                pts.append(scene_points(root, 20000))
    if rest:
        rest()
    root.rotation_euler = (0, 0, 0)
    frame_points(np.concatenate(pts), size, fill=opts.get('fill', 0.8), elev=opts.get('elev', 5.0))

    folder = _folder(variant, mode)
    outdir = os.path.join(PREVIEW3D if preview else OUT3D, name, folder)
    os.makedirs(outdir, exist_ok=True)
    if not preview and frames is None and not os.environ.get('SKIP_EXISTING'):
        for f in os.listdir(outdir):
            os.remove(os.path.join(outdir, f))
    mp = os.path.join(outdir, 'meta.json')
    if os.path.exists(mp):
        os.remove(mp)
    if mode == 'yaw':
        def upd(i, nn):
            root.rotation_euler = (0, 0, math.radians(yaw_of(i, nn)))
            if opts.get('on_yaw'):
                opts['on_yaw'](i, nn)
    elif mode == 'spin' and opts.get('spin'):
        upd = opts['spin']
    elif mode == 'spin':
        def upd(i, nn):
            root.rotation_euler = (0, 0, math.radians(360.0 * i / nn))
        if opts.get('sym180') and frames is None and not preview:
            frames = list(range(n // 2))
    else:
        def upd(i, nn):
            root.rotation_euler = (0, 0, 0)
            anim(i, nn)
    if preview and frames is None:
        frames = sorted({0, n // 2, n - 1})
    t0 = time.time()
    I.render_frames(outdir, n, upd, frames, prefix=f'{name}/{folder}')
    took = time.time() - t0
    if mode == 'spin' and opts.get('sym180') and frames == list(range(n // 2)):
        for i in range(n // 2):
            shutil.copyfile(os.path.join(outdir, f'{i:04d}.png'), os.path.join(outdir, f'{i + n // 2:04d}.png'))
        frames = None
    # features: projected at the rest pose (yaw 0 / spin 0) or the anim's last frame
    if mode == 'anim':
        anim(n - 1, n)
    elif rest:
        rest()
    root.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    feats = {k: [round(v, 1) for v in I.project_px(fn())] for k, fn in opts.get('features', {}).items()}
    pivot = I.project_px(tuple(root.matrix_world.translation))
    meta = dict(name=name, variant=variant, mode=mode, frames=n, fps_hint=30, size=list(size),
                loop=mode == 'spin', notes=opts.get('notes', spec['notes']),
                pivot=[round(pivot[0], 1), round(pivot[1], 1)], axis='z', samples=spp, preview=preview,
                features=feats, device='CPU', render_s=round(took, 1))
    if mode == 'yaw':
        meta['yaw_range'] = list(YAW_RANGE)
        meta['notes'] += '; yaw sweep -40..+40 deg, frame i = -40 + 80*i/(n-1)'
    elif mode == 'spin':
        meta['notes'] += f'; full 360 deg turn about the vertical axis, frame i = {360 / n:g}*i deg, loops'
    else:
        meta.update(opts.get('anim_meta', {}))
        meta['notes'] += '; anim, last frame == yaw 0 / spin frame 0 pose'
    if frames is not None and len(frames) < n:
        meta['partial'] = sorted(frames)
    I.write_meta(outdir, **meta)
    print(f'done {name}/{folder} in {took:.0f}s ({took / max(1, len(frames or range(n))):.1f}s/frame) -> {outdir}',
          flush=True)
    return outdir


# ============================================================================= okt_mark: halftone sphere

# Lattice + falloff fitted to brand/logo_mark.png (python3 assets3d_oktrum.py fit): sphere centre (cx, cy) and
# radius R in logo px; pole polar/azimuth angles (rad, logo frame x right / y up / z to viewer); latitude step
# and phase (deg); longitude step and phase (deg; odd rows offset by half a step); bead radius / R =
# c0 + c . n (n = unit normal), i.e. linear in n.L with L ~ (0.56, 0.05, 0.83).
HALFTONE = dict(pa=1.28953, pb=1.59191, dlat=4.79596, cx=103.24325, cy=146.78219, R=145.21927,
                lat0=0.74768, dlon=9.7109, lon0=0.2496, c0=0.00309, c=(0.02141, 0.00187, 0.03188))


def fit_halftone(path=None):
    """Re-derive HALFTONE from the logo: dot centres (local maxima of the blurred alpha), dot areas (alpha mass
    of each Voronoi cell), back-projection onto a sphere, then (1) the pole + latitude step that make the dot
    latitudes most periodic, (2) the diamond longitude step / phase, (3) a linear radius model."""
    import cv2
    from scipy.optimize import minimize
    from scipy.spatial import cKDTree
    im = cv2.imread(path or os.path.join(WS, 'brand', 'logo_mark.png'), cv2.IMREAD_UNCHANGED)
    a = im[:, :, 3].astype(np.float32)
    b = cv2.GaussianBlur(a, (0, 0), 1.0)
    pk = np.argwhere((b >= cv2.dilate(b, np.ones((5, 5), np.uint8))) & (b > 35))[:, ::-1].astype(float)
    ys, xs = np.nonzero(a > 0)
    _, ii = cKDTree(pk).query(np.c_[xs, ys])
    r = np.sqrt(np.bincount(ii, weights=a[ys, xs] / 255., minlength=len(pk)) / np.pi)
    x, y = pk.T

    def normals(cx, cy, R):
        nx, ny = (x - cx) / R, -(y - cy) / R
        qq = nx ** 2 + ny ** 2
        return np.c_[nx, ny, np.sqrt(np.clip(1 - qq, 0, 1))], qq < 0.8

    def pole(pa, pb):
        return np.array([np.sin(pa) * np.cos(pb), np.sin(pa) * np.sin(pb), np.cos(pa)])

    def score(p):
        N, ok = normals(*p[3:6])
        lat = np.arcsin(np.clip(N[ok] @ pole(*p[:2]), -1, 1))
        return -np.abs(np.exp(2j * np.pi * lat / np.radians(p[2])).mean())
    h = HALFTONE
    best = min((minimize(score, [h['pa'], h['pb'], h['dlat'], cx, h['cy'], R], method='Nelder-Mead',
                         options=dict(maxiter=3000)) for cx in (98, 104, 110) for R in (140, 146, 152)),
               key=lambda o: o.fun)
    pa, pb, dlat, cx, cy, R = best.x
    N, ok = normals(cx, cy, R)
    pz, e1, e2 = _pole_frame(pa, pb)
    lat = np.degrees(np.arcsin(np.clip(N @ pz, -1, 1)))
    lon = np.degrees(np.arctan2(N @ e2, N @ e1))
    lat0 = np.angle(np.exp(2j * np.pi * lat / dlat)[ok].mean()) / (2 * np.pi) * dlat
    row = np.round((lat - lat0) / dlat)
    sc2 = lambda p: -np.abs(np.exp(2j * np.pi * ((lon - p[1]) / p[0] - row / 2))[ok].mean())
    o2 = min((minimize(sc2, [d, 0], method='Nelder-Mead') for d in np.arange(9.0, 10.4, 0.2)), key=lambda o: o.fun)
    dlon = o2.x[0]
    lon0 = o2.x[1] + np.angle(np.exp(2j * np.pi * ((lon - o2.x[1]) / dlon - row / 2))[ok].mean()) / (2 * np.pi) * dlon
    rt = r / np.sqrt(np.clip(N[:, 2], 0.25, 1)) / R
    m = ok & (N[:, 2] > 0.3)
    cc = np.linalg.lstsq(np.c_[np.ones(m.sum()), N[m]], rt[m], rcond=None)[0]
    out = dict(pa=pa, pb=pb, dlat=dlat, cx=cx, cy=cy, R=R, lat0=lat0, dlon=dlon, lon0=lon0, c0=cc[0],
               c=tuple(cc[1:]))
    print('lat coherence', -best.fun, 'lon coherence', -o2.fun)
    print({k: (round(v, 5) if np.isscalar(v) else tuple(round(float(u), 5) for u in v)) for k, v in out.items()})
    return out


def _pole_frame(pa, pb):
    pz = np.array([np.sin(pa) * np.cos(pb), np.sin(pa) * np.sin(pb), np.cos(pa)])
    e1 = np.cross(pz, [0, 0, 1.0])
    e1 /= np.linalg.norm(e1)
    return pz, e1, np.cross(pz, e1)


def halftone_lattice(h=HALFTONE):
    """Unit normals (icon frame) of the whole bead lattice (lat/long rows, odd rows offset half a step) and the
    per-bead radius cap that keeps neighbours from touching where the rows converge on the pole."""
    pz, e1, e2 = _pole_frame(h['pa'], h['pb'])
    N, cap = [], []
    dlat, dlon = math.radians(h['dlat']), math.radians(h['dlon'])
    for k in range(-40, 41):
        lat = math.radians(h['lat0']) + k * dlat
        if abs(lat) >= math.pi / 2 - 0.5 * dlat:
            continue
        cl = math.cos(lat)
        js = np.arange(-60, 61)
        lon = math.radians(h['lon0']) + (js + (k % 2) / 2.0) * dlon
        lon = lon[(lon > -math.pi) & (lon <= math.pi)]
        N.append(cl * (np.cos(lon)[:, None] * e1 + np.sin(lon)[:, None] * e2) + math.sin(lat) * pz)
        cap.append(np.full(len(lon), 0.47 * min(dlat, dlon * cl)))
    return np.concatenate(N), np.concatenate(cap)


BEAD_GLOW = float(os.environ.get('OKT_BEAD_GLOW', '0.25'))
BEAD_SCALE = 1.2      # the logo's soft dots read ~20 % larger than their alpha mass; beads match that look


def halftone_radius(Nc, cap, h=HALFTONE):
    """Bead radius (sphere radius 1) for normals Nc in CAMERA space: the logo's falloff stays fixed to the view
    (lit right-front) while the lattice turns underneath, like the 2D halftone shading of a turning globe."""
    rt = (h['c0'] + Nc @ np.array(h['c'])) * BEAD_SCALE
    rt = np.minimum(rt, cap)
    return np.maximum(rt, 0) * smooth((rt - 0.0015) / 0.004)


def rot_y(P, ang):
    """Yaw (icon frame, about the vertical): positive turns the front towards screen-right."""
    c, s = np.cos(ang), np.sin(ang)
    return np.stack([c * P[:, 0] + s * P[:, 2], P[:, 1], -s * P[:, 0] + c * P[:, 2]], 1)


@asset('okt_mark', [('night', 'spin', 72), ('night', 'anim', 60)], (1000, 1000),
       notes='Oktrum halftone dot sphere: glossy emissive BLUE domed beads, lattice + falloff fitted to the logo',
       samples=1.0)
def build_okt_mark(root, variant, q=1.0):
    Nn, cap = halftone_lattice()
    B = len(Nn)
    TV, TF = cube_sphere(3 if q < 1 else 4)
    TV = TV * np.array([1.0, 1.0, 0.5])                     # domed disc: half-height along the normal
    nv = len(TV)
    F = (TF[None] + (np.arange(B) * nv)[:, None, None]).reshape(-1, 4)

    def verts(cen, nrm, r):
        up = np.where(np.abs(nrm[:, 1:2]) < 0.9, np.array([[0, 1.0, 0]]), np.array([[1.0, 0, 0]]))
        t1 = np.cross(up, nrm)
        t1 /= np.linalg.norm(t1, axis=1, keepdims=True)
        t2 = np.cross(nrm, t1)
        M = np.stack([t1, t2, nrm], 1)                     # (B, 3, 3) rows = local axes
        P = cen[:, None, :] + r[:, None, None] * np.einsum('vk,bkj->bvj', TV, M)
        return ico_to_bl(P.reshape(-1, 3))
    mat = I.m_candy('bead', 'BLUE', rough=0.22, coat_r=0.03, emit='BLUE', emit_str=BEAD_GLOW)
    nt = mat.node_tree                                      # cyan fresnel rim on top of the blue glow
    b = nt.nodes['Principled BSDF']
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.35
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.35
    mr.inputs['From Max'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.75
    nt.links.new(lw.outputs['Facing'], mr.inputs['Value'])
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.inputs['A'].default_value = _c('BLUE') + (1,)
    mx.inputs['B'].default_value = _c('CYAN') + (1,)
    nt.links.new(mr.outputs[0], mx.inputs['Factor'])
    nt.links.new(mx.outputs['Result'], b.inputs['Emission Color'])
    obj = mesh_obj('beads', verts(Nn, Nn, halftone_radius(Nn, cap)), F, mat, root)
    CV, CF = cube_sphere(14)
    core = mesh_obj('core', ico_to_bl(CV * 0.975), CF, m_holdout(), root)   # hides the back beads
    core['noframe'] = 1
    for attr in ('visible_glossy', 'visible_diffuse', 'visible_transmission', 'visible_shadow',
                 'visible_volume_scatter'):
        setattr(core, attr, False)

    def set_beads(cen, nrm, r):
        obj.data.vertices.foreach_set('co', verts(cen, nrm, np.maximum(r, 1e-5)).astype(np.float32).ravel())
        obj.data.update()

    def spin(i, n):
        root.rotation_euler = (0, 0, 0)
        Nc = rot_y(Nn, math.radians(360.0 * i / n))
        set_beads(Nc, Nc, halftone_radius(Nc, cap))

    # ---- assemble: beads swirl in from a wider shell (big lit beads first) while the ball swings -50 -> 0
    rng = np.random.default_rng(11)
    r_end = halftone_radius(Nn, cap)
    order = 1.0 - r_end / r_end.max()
    delay = 3 + 24 * (0.7 * order + 0.3 * rng.random(B))
    dur = 20.0
    swirl = np.radians(rng.uniform(40, 100, B)) * rng.choice([-1, 1], B)
    r0 = rng.uniform(1.08, 1.16, B)
    tilt = rng.uniform(-0.2, 0.2, B)

    def anim(i, n):
        root.rotation_euler = (0, 0, 0)
        if i >= n - 1:                                      # exact rest pose (== spin frame 0)
            set_beads(Nn, Nn, r_end)
            return
        f = float(i)
        yaw = math.radians(-50.0 * (1 - float(ease_out_cubic(f / 50.0))))
        Nc = rot_y(Nn, yaw)
        u = np.clip((f - delay) / dur, 0, 1)
        e = ease_out_cubic(u)
        d = rot_y(Nc, swirl * (1 - e))
        d[:, 1] += tilt * (1 - e)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        rr = 1.0 + (r0 - 1.0) * (1 - ease_out_back(u, 1.2))
        s = smooth(u / 0.45) * halftone_radius(Nc, cap)
        set_beads(d * rr[:, None], d, s)

    def rest():
        set_beads(Nn, Nn, r_end)

    L = np.array(HALFTONE['c']) / np.linalg.norm(HALFTONE['c'])
    return dict(rest=rest, anim=anim, spin=spin, elev=0.0, frame_modes=('spin',),
                features={'centre': lambda: (0, 0, 0), 'highlight': lambda: tuple(ico_to_bl(L * 1.03))},
                anim_meta=dict(settle_frame=50,
                               anim_notes='beads swirl in from a 1.08-1.16 shell (big lit beads first, frames 3-47) '
                                          'while the lattice swings yaw -50 -> 0; last frame == spin frame 0'),
                notes=f'{B}-bead lat/long lattice fitted to the logo; glossy emissive BLUE domed beads with a cyan '
                      f'fresnel rim; the halftone falloff stays lit from the right-front while the lattice turns '
                      f'(spin frame 0 == the logo); invisible holdout core hides the back beads')


# ============================================================================= shield_lock

def _grp(name, parent, loc=(0, 0, 0)):
    o = I.empty(name, parent)
    o.location = tuple(ico_to_bl(np.array(loc, float)))
    return o


LOCK_C = (0.0, -0.16, 0.50)       # padlock body centre (icon frame); the shield front face sits at z ~0.31


@asset('shield_lock', [('day', 'yaw', 49), ('day', 'anim', 48)], (900, 900),
       notes='thick violet->blue tinted glass shield with a cyan edge glow and a chrome padlock', samples=1.5)
def build_shield_lock(root, variant, q=1.0):
    gs = _grp('g_shield', root)
    gl = _grp('g_lock', root, LOCK_C)
    P = I.shield_outline()
    sd = I.poly_sd([P], res=1400).rounded(0.20, 0.0).blurred(1.0)
    body = I.inflate(sd, thick=0.24, edge=0.20, dome=0.07, dome_field=sd.poisson(), dome_pow=0.6)
    mg = m_tinted_glass('shield_glass', 'VIOLET', 'BLUE', -1.0, 0.85, rough=0.05, ior=1.45, edge='CYAN',
                        edge_str=1.6 if variant == 'day' else 1.0)
    sdf('shield', body, ((-1.05, -1.15, -0.45), (1.05, 1.05, 0.45)), 230, mg, gs, shadow=False, q=q)
    # frosted inner bevel plate: a thinner, lighter glass layer that gives the thick glass a visible inner edge
    inner = I.Raster2D(sd.g + 0.13, sd.b).blurred(0.5)
    plate = I.inflate(inner, thick=0.05, edge=0.045, zc=0.27)
    mp = m_tinted_glass('shield_inner', mixlin('VIOLET', 'IVORY', 0.35), mixlin('BLUE', 'IVORY', 0.35), -0.9, 0.8,
                        rough=0.18, edge='CYAN', edge_str=0.5)
    sdf('shield_inner', plate, ((-0.9, -0.95, 0.15), (0.9, 0.9, 0.4)), 190, mp, gs, shadow=False, q=q)
    # chrome padlock, built around its own centre (g_lock)
    chrome = m_chrome('chrome', 'SILVER', rough=0.07)
    lock = I.sd3_round_box((0, 0, 0), (0.34, 0.27, 0.12), 0.09)
    hole = lambda x, y: np.minimum(np.hypot(x, y - 0.045) - 0.062,
                                   I.sd_rbox(0, -0.06, 0.026, 0.09, 0.02)(x, y))
    key_cut = I.extrude_axis(hole, 'z', 0.2, 0.012, center=0.12)
    sdf('lock_body', I.u_sub(lock, key_cut), ((-0.4, -0.33, -0.18), (0.4, 0.33, 0.18)), 200, chrome, gl, q=q)
    ink = I.m_candy('keyhole', 'INK', rough=0.4, coat_r=0.2)
    sdf('keyhole', I.extrude_axis(lambda x, y: hole(x, y) + 0.004, 'z', 0.05, 0.006, center=0.06),
        ((-0.12, -0.2, -0.02), (0.12, 0.14, 0.14)), 120, ink, gl, q=q)
    gsh = _grp('g_shackle', gl)
    ys = 0.20
    tor = I.sd3_torus((0, ys, 0), 0.215, 0.052, axis='z')
    arch = lambda x, y, z: np.maximum(tor(x, y, z), ys - y)
    legs = I.u_min(I.sd3_capsule((-0.215, ys, 0), (-0.215, 0.0, 0), 0.052),
                   I.sd3_capsule((0.215, ys, 0), (0.215, 0.0, 0), 0.052))
    sdf('shackle', I.u_min(arch, legs), ((-0.3, -0.08, -0.08), (0.3, 0.5, 0.08)), 160, chrome, gsh, q=q)

    OPEN = 0.17
    CLICK, LAND = 30, 22

    def pose(t_shield=1.0, lock_dy=0.0, lock_s=1.0, sh=0.0, yaw=0.0):
        gs.scale = (t_shield,) * 3
        gl.location = tuple(ico_to_bl(np.array(LOCK_C) + np.array([0, lock_dy, 0])))
        gl.scale = (lock_s,) * 3
        gsh.location = tuple(ico_to_bl(np.array([0, sh, 0])))
        root.rotation_euler = (0, 0, math.radians(yaw))

    def anim(i, n):
        f = float(i)
        s = float(ease_out_back(f / 14.0, 2.2)) if f < 14 else 1.0
        yaw = -28.0 * (1 - float(ease_out_cubic(f / 26.0)))
        # padlock: pops in high (frames 9-14), falls (ease-in) to land at LAND, bounces, shackle clicks at CLICK
        ls = float(smooth((f - 9) / 5.0))
        if f < LAND:
            dy = 0.62 * (1 - ((f - 9) / (LAND - 9)) ** 2) if f >= 9 else 0.62
        else:
            dy = 0.045 * math.exp(-(f - LAND) / 2.5) * abs(math.sin((f - LAND) * math.pi / 5.0))
        if f < CLICK - 3:
            sh = OPEN
        elif f < CLICK:
            sh = OPEN * (1 - ((f - (CLICK - 3)) / 3.0) ** 2)
        else:
            sh = -0.012 * math.exp(-(f - CLICK) / 2.0) * math.cos((f - CLICK) * 1.3)
            dy -= 0.02 * math.exp(-(f - CLICK) / 2.5) * math.sin((f - CLICK + 1) * 1.1)
        if i >= n - 1:
            pose()
            return
        pose(s, dy, ls, sh, yaw)

    def rest():
        pose()
    lc = np.array(LOCK_C)
    return dict(rest=rest, anim=anim, metal=True, glass=True,
                features={'lock': lambda: tuple(ico_to_bl(lc + [0, 0, 0.12])),
                          'keyhole': lambda: tuple(ico_to_bl(lc + [0, 0.0, 0.13])),
                          'shield_top': lambda: tuple(ico_to_bl(np.array([0, 0.9, 0.3]))),
                          'shield_tip': lambda: tuple(ico_to_bl(np.array([0, -1.0, 0.0])))},
                anim_meta=dict(click_frame=CLICK, land_frame=LAND, shield_settle_frame=14,
                               anim_notes='shield pops in with overshoot (0-14) while swinging yaw -28 -> 0 (0-26); '
                                          f'padlock pops in high (9-14), drops and lands at {LAND}, shackle snaps '
                                          f'shut at click_frame {CLICK}; last frame == yaw 0'))


# ============================================================================= coins

def _coin(root, glyph, mat, font='InterTight-Black.ttf', gh=1.0, q=1.0):
    Rr, T, reeds = 1.0, 0.155, 120

    def disc2(x, y):
        r = np.hypot(x, y)
        return r - (Rr - 0.009 * (0.5 + 0.5 * np.cos(reeds * np.arctan2(y, x))))
    D = I.fn_sd(disc2, (-1.05, -1.05, 1.05, 1.05), 1600)
    coin = I.extrude_axis(D, 'z', T, 0.045)
    lip_f = I.extrude_axis(lambda x, y: np.abs(np.hypot(x, y) - 0.905) - 0.06, 'z', T + 0.032, 0.03)

    def beads(x, y, z):
        r = np.hypot(x, y)
        per = 2 * np.pi / 48
        tl = np.mod(np.arctan2(y, x) + per / 2, per) - per / 2
        lx, ly = r * np.cos(tl) - 0.78, r * np.sin(tl)
        return np.sqrt(lx * lx + ly * ly + (np.abs(z) - T + 0.005) ** 2) - 0.026
    G = I.glyph_sd(glyph, font, gh, 1100).rounded(concave=0.02 * gh).blurred(0.8)
    Gm = lambda x, y: G(-x, y)            # back face mirrored: the coin is 180-degree symmetric

    def emb(x, y, z):
        return np.minimum(I.inflate(G, thick=0.04, edge=0.028, zc=T - 0.005)(x, y, z),
                          I.inflate(Gm, thick=0.04, edge=0.028, zc=-(T - 0.005))(x, y, z))
    F = I.u_smin(I.u_smin(I.u_smin(coin, lip_f, 0.012), beads, 0.008), emb, 0.012)
    sdf('coin', F, ((-1.04, -1.04, -0.23), (1.04, 1.04, 0.23)), 420, mat, root, q=q)


@asset('coin_btc', [('night', 'spin', 72)], (900, 900), notes='polished gold coin, Bitcoin sign on both faces')
def build_coin_btc(root, variant, q=1.0):
    T = 0.155
    mg = I.m_gold('gold', base='AMBER', edge='GOLD_DEEP', rough=0.15, relief=('Y', T + 0.004, T + 0.02, 0.34))
    _coin(root, '₿', mg, gh=1.08, q=q)
    return dict(metal=True, sym180=True, features={'centre': lambda: (0, 0, 0)},
                notes='polished gold coin (AMBER face, deep-gold edge tint), Bitcoin sign both faces, reeded rim')


@asset('coin_usd', [('night', 'spin', 72)], (900, 900), notes='silver-chrome coin, dollar sign on both faces')
def build_coin_usd(root, variant, q=1.0):
    T = 0.155
    ms = I.m_gold('silver', base='SILVER', edge=(1.0, 1.0, 1.0), rough=0.12, relief=('Y', T + 0.004, T + 0.02, 0.32))
    _coin(root, '$', ms, gh=1.08, q=q)
    return dict(metal=True, sym180=True, features={'centre': lambda: (0, 0, 0)},
                notes='silver-chrome coin, dollar sign both faces, reeded rim')


# ============================================================================= gold_bar

def _smax(ds, k):
    m = np.maximum.reduce(ds)
    return m + k * np.log(sum(np.exp((d - m) / k) for d in ds))


@asset('gold_bar', [('night', 'yaw', 49)], (720, 720), notes='gold bullion bar with a generic 999.9 stamp')
def build_gold_bar(root, variant, q=1.0):
    tilt = _grp('g_tilt', root)
    tilt.rotation_euler = (math.radians(-24), 0, 0)
    fx, fy, bx, by, hz = 0.88, 0.40, 1.0, 0.52, 0.24        # front (stamped) face half sizes, back face, half depth

    def planes(x, y, z):
        t = (z + hz) / (2 * hz)                              # 0 back .. 1 front
        ax = bx + (fx - bx) * t
        ay = by + (fy - by) * t
        kx = math.hypot(1, (bx - fx) / (2 * hz))
        ky = math.hypot(1, (by - fy) / (2 * hz))
        return [(np.abs(x) - ax) / kx, (np.abs(y) - ay) / ky, z - hz, -z - hz]
    bar = lambda x, y, z: _smax(planes(x, y, z), 0.022)
    txt = I.glyph_sd('999.9', 'JetBrainsMono-Bold.ttf', 0.26, 1300).blurred(0.6)
    ring = lambda x, y: np.abs(I.sd_rbox(0, 0, 0.66, 0.24, 0.07)(x, y)) - 0.014
    stamp = lambda x, y: np.minimum(txt(x, y), ring(x, y))
    cut = I.extrude_axis(stamp, 'z', 0.035, 0.008, center=hz)
    F = I.u_sub(bar, cut)
    mg = I.m_gold('gold', base='AMBER', edge='GOLD_DEEP', rough=0.13)
    sdf('bar', F, ((-1.08, -0.6, -0.3), (1.08, 0.6, 0.3)), 380, mg, tilt, q=q)
    return dict(metal=True, features={'stamp': lambda: tuple(np.array(tilt.matrix_world) @ np.r_[0, -hz, 0, 1])[:3]},
                notes='polished gold bullion bar (AMBER, deep-gold edge tint), engraved "999.9" in a rounded '
                      'cartouche on the front face, tilted 24 deg back so the stamp faces the viewer')


# ============================================================================= candles

def _candle(name, parent, x, body, wick, col, w=0.13, emit_col=None, glass_col=None, q=1.0, res=170):
    """Glass candlestick: rounded glass body (y0..y1), an emissive core inside, thin wick rods above/below."""
    y0, y1 = body
    cy, hy = (y0 + y1) / 2, (y1 - y0) / 2
    g = m_tinted_glass(name + '_glass', glass_col or col, glass_col or col, y0, y1, rough=0.07, edge=col, edge_str=1.2)
    sdf(name, I.sd3_round_box((x, cy, 0), (w, hy, w), min(0.06, w * 0.45)),
        ((x - w - 0.03, y0 - 0.03, -w - 0.03), (x + w + 0.03, y1 + 0.03, w + 0.03)), res, g, parent,
        shadow=False, q=q)
    core = I.m_emit(name + '_core', emit_col or col, 3.0)
    cw = w * 0.42
    sdf(name + '_core', I.sd3_round_box((x, cy, 0), (cw, max(hy - w * 0.45, 0.02), cw), cw * 0.8),
        ((x - cw - 0.02, y0, -cw - 0.02), (x + cw + 0.02, y1, cw + 0.02)), int(res * 0.6), core, parent, q=q)
    wm = I.m_candy(name + '_wick', col, rough=0.25, coat_r=0.05, emit=emit_col or col, emit_str=1.5)
    rw = max(0.016, w * 0.12)
    wick_f = I.u_min(I.sd3_capsule((x, wick[0], 0), (x, y0 + 0.02, 0), rw),
                     I.sd3_capsule((x, y1 - 0.02, 0), (x, wick[1], 0), rw))
    sdf(name + '_wick', wick_f, ((x - rw - 0.02, wick[0] - rw - 0.02, -rw - 0.02),
                                 (x + rw + 0.02, wick[1] + rw + 0.02, rw + 0.02)), int(res * 0.9), wm, parent, q=q)


CANDLES = [  # (up?, open/close body y0..y1, wick low..high): a slight rising trend
    (True, (0.00, 0.48), (-0.16, 0.66)),
    (False, (0.26, 0.46), (0.14, 0.62)),
    (True, (0.30, 0.86), (0.20, 1.00)),
    (True, (0.74, 1.18), (0.60, 1.34)),
    (False, (0.92, 1.12), (0.80, 1.30)),
    (True, (1.00, 1.58), (0.90, 1.78)),
]


@asset('candles3d', [('night', 'yaw', 49)], (1000, 1000),
       notes='6 glass candlesticks (UP green / DOWN red), emissive cores, thin wicks, rising trend', samples=1.5)
def build_candles(root, variant, q=1.0):
    feats = {}
    for k, (up, body, wick) in enumerate(CANDLES):
        x = (k - 2.5) * 0.42
        b = (body[0] - 0.8, body[1] - 0.8)
        w_ = (wick[0] - 0.8, wick[1] - 0.8)
        col = 'UP' if up else 'DOWN'
        _candle(f'c{k}', root, x, b, w_, col, q=q)
        feats[f'c{k}'] = (lambda x=x, y=b[1]: tuple(ico_to_bl(np.array([x, y, 0.0]))))
        feats[f'c{k}_wick'] = (lambda x=x, y=w_[1]: tuple(ico_to_bl(np.array([x, y, 0.0]))))
    return dict(glass=True, features=feats, rig_scale=1.15,
                notes='6 glass candlesticks G R G G R G on a slight rising trend (UP #34D399 / DOWN #F87171 glass, '
                      'emissive cores, thin emissive wicks); features c<k> = body top centre, c<k>_wick = wick tip')


@asset('candle_red', [('day', 'yaw', 49)], (1000, 1000), notes='one tall red glass candle', samples=1.5)
def build_candle_red(root, variant, q=1.0):
    deep = mixlin('DOWN', '#B91C1C', 0.45)
    _candle('candle', root, 0.0, (-0.72, 0.80), (-1.08, 1.12), 'DOWN', w=0.30, emit_col=mixlin('DOWN', '#FF3B3B', 0.3),
            glass_col=deep, q=q, res=260)
    return dict(glass=True, features={'top': lambda: tuple(ico_to_bl(np.array([0, 0.80, 0.0]))),
                                      'bottom': lambda: tuple(ico_to_bl(np.array([0, -0.72, 0.0])))},
                notes='one tall DOWN-red glass candle (deep red glass, glowing core, wicks above and below)')


# ============================================================================= chip

@asset('chip', [('night', 'yaw', 49)], (720, 720), notes='black glass processor chip, glowing core, gold pins',
       samples=1.25)
def build_chip(root, variant, q=1.0):
    tilt = _grp('g_tilt', root)
    tilt.rotation_euler = (math.radians(-38), 0, 0)
    H = 0.80
    pkg = I.sd3_round_box((0, 0, 0), (H, H, 0.09), 0.06)
    m_pkg = I._principled('chip_pkg')[0]
    b = m_pkg.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = _c('INK') + (1,)
    b.inputs['Roughness'].default_value = 0.06
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Coat Roughness'].default_value = 0.02
    b.inputs['Specular IOR Level'].default_value = 0.7
    # recess for the core window
    win = I.sd3_round_box((0, 0, 0.09), (0.44, 0.44, 0.035), 0.03)
    sdf('package', I.u_sub(pkg, win), ((-0.84, -0.84, -0.12), (0.84, 0.84, 0.12)), 300, m_pkg, tilt, q=q)
    # glowing core: emissive plate with a radial BLUE -> CYAN ramp, under a clear glass lid
    core_m = bpy.data.materials.new('core')
    core_m.use_nodes = True
    nt = core_m.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sp.inputs[0])
    ln = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(sp.outputs['X'], ln.inputs['X'])
    nt.links.new(sp.outputs['Z'], ln.inputs['Y'])
    vl = nt.nodes.new('ShaderNodeVectorMath')
    vl.operation = 'LENGTH'
    nt.links.new(ln.outputs[0], vl.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.05
    mr.inputs['From Max'].default_value = 0.5
    nt.links.new(vl.outputs['Value'], mr.inputs['Value'])
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.inputs['A'].default_value = mixlin('CYAN', (1, 1, 1), 0.25) + (1,)
    mx.inputs['B'].default_value = _c('BLUE') + (1,)
    nt.links.new(mr.outputs[0], mx.inputs['Factor'])
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 3.2
    nt.links.new(mx.outputs['Result'], em.inputs['Color'])
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    plate = I.sd3_round_box((0, 0, 0.065), (0.40, 0.40, 0.012), 0.01)
    sdf('core', plate, ((-0.43, -0.43, 0.04), (0.43, 0.43, 0.09)), 160, core_m, tilt, q=q)
    lid = m_tinted_glass('lid', mixlin('CYAN', (1, 1, 1), 0.6), mixlin('CYAN', (1, 1, 1), 0.6), -1, 1, rough=0.03,
                         edge='CYAN', edge_str=0.8)
    sdf('lid', I.sd3_round_box((0, 0, 0.1), (0.415, 0.415, 0.025), 0.02), ((-0.45, -0.45, 0.06), (0.45, 0.45, 0.14)),
        180, lid, tilt, shadow=False, q=q)
    # gold pins: 9 per side, repeated by domain repetition, bent down at the tip
    sp_ = 0.15

    def side(u, v, z):                    # u: outward coordinate (>0), v: along the side
        vv = v - sp_ * np.clip(np.round(v / sp_), -4, 4)
        a = I.sd3_round_box((0.86, 0, -0.02), (0.08, 0.035, 0.016), 0.012)(u, vv, z)
        bnd = I.sd3_round_box((0.93, 0, -0.07), (0.016, 0.035, 0.06), 0.012)(u, vv, z)
        return np.minimum(a, bnd)
    pins = lambda x, y, z: np.minimum(side(np.abs(x), y, z), side(np.abs(y), x, z))
    mgp = I.m_gold('pins', base='AMBER', edge='GOLD_DEEP', rough=0.18)
    sdf('pins', pins, ((-0.98, -0.98, -0.15), (0.98, 0.98, 0.02)), 340, mgp, tilt, q=q)
    return dict(metal=True, glass=True,
                features={'core': lambda: tuple(np.array(tilt.matrix_world) @ np.r_[0, -0.1, 0, 1])[:3]},
                notes='black glass processor chip tilted 38 deg back: glossy INK package, BLUE->CYAN glowing core '
                      'under a clear lid, 36 gold pins; no markings')


# ============================================================================= contact sheets

def _bg(h, w, kind):
    if kind == 'night':
        return np.broadcast_to(np.array(hexlin('NAVY'), np.float32), (h, w, 3)).copy()
    return np.broadcast_to(np.array(hexlin('IVORY'), np.float32), (h, w, 3)).copy()


def _tile(p, cell, kind):
    import cv2
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    rgb = (im[:, :, 2::-1].astype(np.float32) / 255.0) ** 2.2
    a = im[:, :, 3:4].astype(np.float32) / 255.0
    s = cell / max(im.shape[:2])
    rgb = cv2.resize(rgb * a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    a = cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)[..., None]
    t = _bg(cell, cell, kind)
    h, w = rgb.shape[:2]
    y0, x0 = (cell - h) // 2, (cell - w) // 2
    t[y0:y0 + h, x0:x0 + w] = rgb + t[y0:y0 + h, x0:x0 + w] * (1 - a)
    return t


def sheet(names, preview=False, cell=200, per=6):
    import cv2
    root = PREVIEW3D if preview else OUT3D
    os.makedirs(SELFTEST, exist_ok=True)
    for name in names:
        rows = []
        for (v, m, n) in ASSETS[name]['folders']:
            d = os.path.join(root, name, _folder(v, m))
            if not os.path.isdir(d):
                continue
            pngs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
            if not pngs:
                continue
            pick = [pngs[int(round(k * (len(pngs) - 1) / (per - 1)))] for k in range(per)]
            for kind in ('night', 'day'):
                row = np.concatenate([_tile(os.path.join(d, p), cell, kind) for p in pick], 1)
                lab = (np.clip(row, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)[:, :, ::-1].copy()
                cv2.putText(lab, f'{_folder(v, m)} {",".join(p[:4] for p in pick)}', (6, 16),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (128, 128, 128), 1, cv2.LINE_AA)
                rows.append(lab)
        if rows:
            out = os.path.join(SELFTEST, f'okt3d_{name}{"_preview" if preview else ""}.png')
            cv2.imwrite(out, np.concatenate(rows, 0))
            print('sheet ->', out)


# ============================================================================= CLI

def main(argv):
    if not argv:
        print(__doc__)
        return
    if argv[0] == 'fit':
        fit_halftone()
        return
    if argv[0] in ('sheet', 'previewsheet'):
        sheet(argv[1:] or list(ASSETS), preview=argv[0] == 'previewsheet')
        return
    names, preview, variant, mode, frames, samples = [], False, None, None, None, None
    it = iter(argv)
    for a in it:
        if a == '--preview':
            preview = True
        elif a == '--variant':
            variant = next(it)
        elif a == '--mode':
            mode = next(it)
        elif a == '--frames':
            frames = [int(x) for x in next(it).split(',')]
        elif a == '--samples':
            samples = int(next(it))
        elif a == 'all':
            names += list(ASSETS)
        else:
            names.append(a)
    for name in names:
        for (v, m, n) in ASSETS[name]['folders']:
            if (variant and v != variant) or (mode and m != mode):
                continue
            render_asset(name, v, m, preview=preview, frames=frames, samples=samples)


if __name__ == '__main__':
    main(sys.argv[1:])
