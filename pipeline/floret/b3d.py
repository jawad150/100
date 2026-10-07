"""Blender (Cycles) 3D elements for the Floret Capitals spot, rendered as transparent RGBA PNG sequences
(30 fps) that the compositor places into the SaaS scenes:

  logo     - the Floret logo extruded: gold metal bars rise one by one, the silver arrow grows, slow turn
  goldbar  - gold bullion bar, slow turn            silverbar - silver bar
  barrel   - black lacquer crude-oil barrel with gold rims
  coin     - gold coin with the Floret bars embossed, tumbling
  shield   - gold shield with a silver check (Built on Trust)

python3 b3d.py <job> [still]   -> workspace4/b3d/<job>/0001.png ...
"""
import math
import os
import sys

import bpy
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'workspace4'))
GOLD = (1.0, 0.70, 0.28)
SILVER = (0.93, 0.94, 0.96)


# ------------------------------------------------------------------ scene
def reset(res, frames, samples=40):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = int(os.environ.get('SAMPLES', samples))
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.fps = 30
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    studio_world(w)
    studio()
    return sc


def metal(name, color, rough=0.22, metal_=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color + (1,)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal_
    return m


def emitter(name, loc, rot, size, strength, color=(1, 0.93, 0.85)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1)
    m = bpy.data.materials.new(name + 'M')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = color + (1,)
    e.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], out.inputs[0])
    o.data.materials.append(m)
    o.visible_camera = False
    return o


def area(name, loc, target, size, energy, color=(1, 0.9, 0.78)):
    d = bpy.data.lights.new(name, 'AREA')
    d.size = size
    d.energy = energy
    d.color = color
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    v = np.subtract(target, loc)
    o.rotation_euler = (math.atan2(math.hypot(v[0], v[1]), -v[2]), 0, math.atan2(v[1], v[0]) + math.pi / 2)
    return o


def studio_world(w):
    """Procedural softbox environment for reflections: bright top, warm band near the horizon, dark floor."""
    nt = w.node_tree
    bg = nt.nodes['Background']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = -1.0, 1.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.0, (0.01, 0.009, 0.008, 1)
    cr.elements[1].position, cr.elements[1].color = 1.0, (2.2, 2.1, 2.0, 1)
    for pos, col in ((0.42, (0.03, 0.025, 0.02, 1)), (0.5, (1.1, 0.75, 0.4, 1)), (0.56, (0.05, 0.045, 0.04, 1)),
                     (0.8, (0.15, 0.14, 0.13, 1))):
        e = cr.elements.new(pos)
        e.color = col
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.7


def studio():
    """Softbox studio for metal: big reflection cards (invisible to camera) + key / rims."""
    emitter('top', (0, -1.5, 5), (0.35, 0, 0), (7, 3), 3.0)
    emitter('left', (-5, -2, 1), (0, -1.2, 0.3), (2.2, 6), 2.2, (1, 0.86, 0.66))
    emitter('right', (5, -1, 1.5), (0, 1.2, -0.3), (1.2, 6), 4.0)
    emitter('front', (0, -6, -1.2), (1.75, 0, 0), (6, 1.0), 1.4)
    area('key', (-3, -5, 4), (0, 0, 0), 4, 900)
    area('rimL', (-4, 4, 2), (0, 0, 0.3), 2, 700, (1, 0.75, 0.45))
    area('rimR', (4, 4, 3), (0, 0, 0.3), 2, 900)


def camera(loc, target, lens=70):
    c = bpy.data.cameras.new('Cam')
    c.lens = lens
    o = bpy.data.objects.new('Cam', c)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    v = np.subtract(target, loc)
    o.rotation_euler = (math.atan2(math.hypot(v[0], v[1]), -v[2]), 0, math.atan2(v[1], v[0]) - math.pi / 2)
    bpy.context.scene.camera = o
    return o


def prism(name, poly, depth, mat, bevel=0.02, y0=0.0):
    """Extrude a 2D polygon (x, z) along +y."""
    n = len(poly)
    verts = [(x, y0 - depth / 2, z) for x, z in poly] + [(x, y0 + depth / 2, z) for x, z in poly]
    faces = [list(range(n))[::-1], list(range(n, 2 * n))]
    faces += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL')
        b.width = bevel
        b.segments = 3
        b.limit_method = 'ANGLE'
    o.modifiers.new('tri', 'TRIANGULATE')
    for p in o.data.polygons:
        p.use_smooth = False
    return o


def set_origin(o, pt):
    """Move object origin to pt (world) without moving the mesh."""
    off = np.subtract(o.location, pt)
    for v in o.data.vertices:
        v.co = tuple(np.add(v.co, off))
    o.location = pt


def key(o, path, frame, value, idx=None):
    if idx is None:
        setattr(o, path, value)
        o.keyframe_insert(path, frame=frame)
    else:
        getattr(o, path)[idx] = value
        o.keyframe_insert(path, index=idx, frame=frame)


def ease_all():
    for a in bpy.data.actions:
        try:
            curves = a.fcurves
        except AttributeError:                                # Blender 5: layered actions
            curves = [c for l in a.layers for s in l.strips for cb in s.channelbags for c in cb.fcurves]
        for c in curves:
            for k in c.keyframe_points:
                k.interpolation = 'BEZIER'
                k.easing = 'AUTO'


# ------------------------------------------------------------------ logo polygons
def logo_polys(width=2.2):
    im = cv2.imread(ROOT + '/assets/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3]
    rgb = im[..., 2::-1]
    sat = rgb.max(2) - rgb.min(2)
    ys, xs = np.where(a > 0.02)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    k = width / (x1 - x0)

    def polys(mask):
        cs, _ = cv2.findContours((mask > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        out = []
        for c in sorted(cs, key=lambda c: cv2.boundingRect(c)[0]):
            if cv2.contourArea(c) < 200:
                continue
            c = cv2.approxPolyDP(c, 1.2, True)[:, 0]
            out.append([((x - (x0 + x1) / 2) * k, ((y0 + y1) / 2 - y) * k) for x, y in c])
        return out
    return polys(a * (sat > 0.2)), polys(a * (sat <= 0.2))


# ------------------------------------------------------------------ jobs
def job_logo():
    sc = reset(960, 120)
    gold, silver = metal('gold', GOLD, 0.2), metal('silver', SILVER, 0.16)
    bars, arrows = logo_polys(2.2)
    root = bpy.data.objects.new('root', None)
    sc.collection.objects.link(root)
    for i, pl in enumerate(bars):
        o = prism(f'bar{i}', pl, 0.32, gold, 0.018)
        zb = min(z for _, z in pl)
        xc = sum(x for x, _ in pl) / len(pl)
        set_origin(o, (xc, 0, zb))
        o.parent = root
        f0 = 6 + 6 * i
        key(o, 'scale', 1, 0.001, 2)
        key(o, 'scale', f0, 0.001, 2)
        key(o, 'scale', f0 + 14, 1.08, 2)
        key(o, 'scale', f0 + 20, 1.0, 2)
    for j, pl in enumerate(arrows):
        o = prism(f'arrow{j}', pl, 0.2, silver, 0.015, y0=-0.05)
        xs = [x for x, _ in pl]
        zs = [z for _, z in pl]
        set_origin(o, (min(xs), 0, zs[int(np.argmin(xs))]))
        o.parent = root
        for ax in (0, 2):
            key(o, 'scale', 1, 0.001, ax)
            key(o, 'scale', 30, 0.001, ax)
            key(o, 'scale', 48, 1.0, ax)
    key(root, 'rotation_euler', 1, math.radians(-30), 2)
    key(root, 'rotation_euler', 120, math.radians(14), 2)
    key(root, 'location', 1, -0.25, 1)
    key(root, 'location', 120, 0.0, 1)
    ease_all()
    camera((0, -9, 0.5), (0, 0, 0.05), 78)
    return sc


def bar_poly(w=1.6, h=0.55, top=1.2):
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (top / 2, h / 2), (-top / 2, h / 2)]


def job_bar(kind):
    sc = reset(640, 96)
    m = metal(kind, GOLD if kind == 'gold' else SILVER, 0.2 if kind == 'gold' else 0.15)
    o = prism('bar', [(x, z) for x, z in bar_poly()], 0.8, m, 0.04)
    o.rotation_euler = (0, 0, 0)
    key(o, 'rotation_euler', 1, math.radians(-35), 2)
    key(o, 'rotation_euler', 96, math.radians(55), 2)
    key(o, 'rotation_euler', 1, math.radians(8), 0)
    key(o, 'rotation_euler', 96, math.radians(-4), 0)
    ease_all()
    camera((0, -5.2, 2.6), (0, 0, -0.05), 72)
    return sc


def job_barrel():
    sc = reset(640, 96)
    paint = metal('paint', (0.02, 0.018, 0.016), 0.28, 0.0)
    paint.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 1.0
    gold = metal('gold', GOLD, 0.25)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.62, depth=1.75)
    body = bpy.context.object
    body.data.materials.append(paint)
    b = body.modifiers.new('bev', 'BEVEL')
    b.width, b.segments = 0.03, 3
    for z in (-0.48, 0.0, 0.48):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.63, minor_radius=0.028 if z else 0.022, location=(0, 0, z),
                                         major_segments=96, minor_segments=16)
        r = bpy.context.object
        r.data.materials.append(gold)
        r.parent = body
    for z in (-0.875, 0.875):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.6, minor_radius=0.035, location=(0, 0, z), major_segments=96)
        r = bpy.context.object
        r.data.materials.append(gold)
        r.parent = body
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.09, depth=0.05, location=(0.3, 0.1, 0.885))
    cap = bpy.context.object
    cap.data.materials.append(gold)
    cap.parent = body
    for p in body.data.polygons:
        p.use_smooth = True
    key(body, 'rotation_euler', 1, math.radians(0), 2)
    key(body, 'rotation_euler', 96, math.radians(80), 2)
    key(body, 'rotation_euler', 1, math.radians(6), 0)
    key(body, 'rotation_euler', 96, math.radians(-3), 0)
    ease_all()
    camera((0, -5.4, 1.9), (0, 0, 0.02), 58)
    return sc


def job_coin():
    sc = reset(640, 96)
    gold = metal('gold', GOLD, 0.18)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.9, depth=0.14, rotation=(math.pi / 2, 0, 0))
    coin = bpy.context.object
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    coin.data.materials.append(gold)
    b = coin.modifiers.new('bev', 'BEVEL')
    b.width, b.segments = 0.03, 4
    bpy.ops.mesh.primitive_torus_add(major_radius=0.78, minor_radius=0.02, rotation=(math.pi / 2, 0, 0), location=(0, -0.07, 0))
    rim = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    rim.data.materials.append(gold)
    rim.parent = coin
    bars, arrows = logo_polys(0.95)
    for i, pl in enumerate(bars + arrows):
        o = prism(f'emb{i}', [(x, z - 0.05) for x, z in pl], 0.05, gold, 0.006, y0=-0.08)
        o.parent = coin
        o2 = prism(f'embb{i}', [(-x, z - 0.05) for x, z in pl], 0.05, gold, 0.006, y0=0.08)
        o2.parent = coin
    for p in coin.data.polygons:
        p.use_smooth = True
    key(coin, 'rotation_euler', 1, 0.0, 2)
    key(coin, 'rotation_euler', 96, math.radians(330), 2)
    key(coin, 'rotation_euler', 1, math.radians(12), 0)
    key(coin, 'rotation_euler', 96, math.radians(-10), 0)
    ease_all()
    camera((0, -5.0, 0.6), (0, 0, 0), 68)
    return sc


def job_shield():
    sc = reset(640, 96)
    gold = metal('gold', GOLD, 0.2)
    silver = metal('silver', SILVER, 0.14)
    pts = []
    for i in range(41):                                       # shield outline: flat top, curved sides to a point
        t = i / 40
        x = 0.9 * (1 - t ** 2.2)
        z = 0.85 - 2.0 * t
        pts.append((x, z))
    top = [(0.0, 1.02), (0.45, 0.92), (0.9, 0.85)]
    right = top + pts[1:]
    outline = right + [(-x, z) for x, z in reversed(right[:-1])]
    sh = prism('shield', outline, 0.3, gold, 0.05)
    inner = [(x * 0.82, z * 0.82 + 0.03) for x, z in outline]
    ins = prism('inner', inner, 0.06, metal('dark', (0.03, 0.025, 0.02), 0.3, 0.0), 0.02, y0=-0.17)
    ins.parent = sh
    # check mark: thick polyline as prisms
    def bar(a, b, w=0.13):
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        nx, nz = -dz / L * w / 2, dx / L * w / 2
        return [(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]
    for i, (a, b) in enumerate((((-0.36, 0.0), (-0.08, -0.3)), ((-0.12, -0.3), (0.42, 0.32)))):
        c = prism(f'chk{i}', bar(a, b), 0.12, silver, 0.025, y0=-0.24)
        c.parent = sh
    key(sh, 'rotation_euler', 1, math.radians(-28), 2)
    key(sh, 'rotation_euler', 96, math.radians(22), 2)
    ease_all()
    camera((0, -6.2, 0.4), (0, 0, -0.08), 62)
    return sc


JOBS = dict(logo=job_logo, goldbar=lambda: job_bar('gold'), silverbar=lambda: job_bar('silver'), barrel=job_barrel,
            coin=job_coin, shield=job_shield)

if __name__ == '__main__':
    name = sys.argv[1]
    sc = JOBS[name]()
    out = f'{ROOT}/b3d/{name}/'
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[2] == 'still':
        f = int(sys.argv[3]) if len(sys.argv) > 3 else sc.frame_end
        sc.frame_set(f)
        sc.render.filepath = f'{ROOT}/b3d/preview_{name}.png'
        bpy.ops.render.render(write_still=True)
    else:
        step = int(os.environ.get('STEP', 1))
        for f in range(sc.frame_start, sc.frame_end + 1, step):
            p = f'{out}{f:04d}.png'
            if os.path.exists(p):
                continue
            sc.frame_set(f)
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
