"""3D cutouts for the reference-style cut of OF "Can I add a page?" (shown black-and-white in the reel):
a 3/4 open book, a twin-bell alarm clock (face without hands - the hands are animated in 2D), a push pin, and the dark
chrome crescents that sit in the corners (as in the reference).

Run: blender -b -P blender_ref.py -- [draft] [names...] -> workspace_page/assets/<name>.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, box, cyl, sph, torus, hexc

ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_page/assets'
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
DRAFT = 'draft' in argv
NAMES = [a for a in argv if a != 'draft']
PLUM, IVORY = hexc('#5B174F'), hexc('#F6F1E9')


def reset(res=(1200, 1200)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 32 if DRAFT else 128
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.92, 0.92, 0.92, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.5
    for loc, en, sz in (((-6, -6, 8), 1800, 5), ((6, -2, 5), 500, 4), ((0, 6, 6), 700, 4)):
        L = bpy.data.objects.new('L', bpy.data.lights.new('L', 'AREA'))
        L.data.energy, L.data.size = en, sz
        L.location = loc
        L.rotation_euler = (Vector((0, 0, 0.5)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(L)
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    act().is_shadow_catcher = True
    return sc


def camera(loc, tgt, lens=60):
    sc = bpy.context.scene
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


def render(name):
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


def paper_mat():
    return mat(IVORY, 0.85, coat=0.0)


def book3q():
    PW, PH = 4.0, 5.6
    cover = mat(PLUM, 0.7, coat=0.1)
    box((2 * PW + 0.36, PH + 0.36, 0.14), loc=(0, 0, 0.07), m=cover, bw=0.05)
    edge = mat(hexc('#EEE7DA'), 0.9, coat=0.0)
    for side in (-1, 1):
        box((PW - 0.05, PH - 0.05, 0.45), loc=(side * (PW / 2 + 0.02), 0, 0.36), m=edge, bw=0.03)
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=80, y_subdivisions=8, size=1)
        o = act()
        bm = bmesh.new()
        bm.from_mesh(o.data)
        for v in bm.verts:
            u, w = v.co.x + 0.5, v.co.y + 0.5
            v.co = Vector((side * u * PW, (w - 0.5) * PH, 0.3 + 0.5 * (1 - math.exp(-u / 0.1)) - 0.05 * u))
        bm.to_mesh(o.data)
        bm.free()
        bpy.ops.object.shade_smooth()
        setm(o, paper_mat())
    box((0.12, 1.6, 0.01), loc=(0.35, -PH / 2 - 0.55, 0.16), m=mat(hexc('#B7006E'), 0.4), bw=0.0)
    camera((0, -13.5, 11.0), (0, 0.3, 0), 55)


def clock():
    body = mat(hexc('#B9B4AD'), 0.22, 0.9, coat=0.6)
    cyl(1.5, 0.75, loc=(0, 0, 2.2), m=body, rot=(math.radians(90), 0, 0), bw=0.12)       # case
    face = mat(hexc('#F4F1EA'), 0.5, coat=0.2)
    cyl(1.33, 0.02, loc=(0, -0.38, 2.2), m=face, rot=(math.radians(90), 0, 0), bw=0.0)
    ink = mat(hexc('#222222'), 0.4)
    for i in range(12):                                                                # hour marks
        a = math.radians(90 - i * 30)
        r = 1.12
        L = 0.22 if i % 3 == 0 else 0.12
        box((0.05 if i % 3 else 0.08, 0.02, L), loc=(r * math.cos(a), -0.4, 2.2 + r * math.sin(a)), m=ink, bw=0.0,
            rot=(0, math.radians(-(90 - i * 30) + 90), 0))
    torus(1.45, 0.07, loc=(0, -0.38, 2.2), m=body, rot=(math.radians(90), 0, 0))         # bezel
    for s in (-1, 1):                                                                  # twin bells + hammers + legs
        sph(0.55, loc=(s * 1.0, 0.05, 3.55), m=body, scale=(1, 1, 0.75))
        cyl(0.06, 0.5, loc=(s * 0.45, 0.05, 3.55), m=body, rot=(0, math.radians(s * 60), 0))
        cyl(0.08, 0.7, loc=(s * 0.95, 0.0, 0.6), m=body, rot=(0, math.radians(s * 25), 0))
    sph(0.12, loc=(0, 0.05, 3.85), m=body)
    torus(0.32, 0.05, loc=(0, 0.05, 3.95), m=body, rot=(math.radians(90), 0, 0))
    camera((0, -11, 2.6), (0, 0, 2.2), 70)


def pin():
    m = mat(PLUM, 0.2, coat=1.0)
    cyl(0.55, 0.25, loc=(0, 0, 2.6), m=m, bw=0.08)
    cyl(0.25, 0.9, loc=(0, 0, 2.0), m=m, bw=0.05)
    cyl(0.5, 0.18, loc=(0, 0, 1.5), m=m, bw=0.06)
    bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.01, depth=1.2, location=(0, 0, 0.8))
    setm(act(), mat(hexc('#C8C8C8'), 0.2, 1.0))
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and not o.is_shadow_catcher:
            o.rotation_euler = (math.radians(-18), math.radians(12), 0)
    camera((0, -9, 2.0), (0, 0, 1.6), 70)


def crescent():
    """Dark chrome crescent (the reference's corner ornament)."""
    bpy.ops.curve.primitive_bezier_curve_add()
    cu = act()
    sp = cu.data.splines[0]
    pts = [(-2.2, 0, 0), (0, 1.4, 0), (2.2, 0, 0)]
    sp.bezier_points.add(1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.data.bevel_depth = 0.32
    cu.data.bevel_resolution = 8
    cu.data.resolution_u = 32
    taper = bpy.data.curves.new('tp', 'CURVE')
    taper.dimensions = '2D'
    s2 = taper.splines.new('BEZIER')
    s2.bezier_points.add(2)
    for bp, p in zip(s2.bezier_points, [(0, 0.15, 0), (0.5, 1.0, 0), (1.0, 0.15, 0)]):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    to = bpy.data.objects.new('tp', taper)
    bpy.context.scene.collection.objects.link(to)
    cu.data.taper_object = to
    cu.location = (0, 0, 1.0)
    cu.rotation_euler = (math.radians(70), 0, 0)
    setm(cu, mat(hexc('#5B174F'), 0.12, 0.85, coat=1.0))
    camera((0, -10, 2.5), (0, 0, 1.4), 60)


def one_house(x, y, s, m, roof, win, rot=0.0):
    objs = []
    objs.append(box((1.6 * s, 1.4 * s, 1.2 * s), loc=(x, y, 0.6 * s), m=m, bw=0.04 * s))
    me = bpy.data.meshes.new('roof')
    w_, d_, h0, h1 = 0.95 * s, 0.85 * s, 1.2 * s, 2.15 * s
    vs = [(-w_, -d_, h0), (w_, -d_, h0), (w_, d_, h0), (-w_, d_, h0), (-w_, 0, h1), (w_, 0, h1)]
    fs = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    me.from_pydata([(x + a, y + b, c) for a, b, c in vs], [], fs)
    r = bpy.data.objects.new('roof', me)
    bpy.context.scene.collection.objects.link(r)
    setm(r, roof)
    objs.append(r)
    objs.append(box((0.32 * s, 0.05 * s, 0.6 * s), loc=(x, y - 0.71 * s, 0.3 * s), m=roof, bw=0.01))
    for dx in (-0.48, 0.48):
        objs.append(box((0.34 * s, 0.05 * s, 0.32 * s), loc=(x + dx * s, y - 0.71 * s, 0.78 * s), m=win, bw=0.01))
    objs.append(box((0.22 * s, 0.22 * s, 0.6 * s), loc=(x + 0.45 * s, y + 0.2 * s, 2.0 * s), m=m, bw=0.02))
    e = bpy.data.objects.new('h', None)
    bpy.context.scene.collection.objects.link(e)
    e.location = (x, y, 0)
    for o in objs:
        o.location = (o.location.x - x, o.location.y - y, o.location.z) if o.name.startswith('roof') is False else o.location
        o.parent = e
    for o in objs:
        if o.name.startswith('roof'):
            o.location = (-x, -y, 0)
    e.rotation_euler = (0, 0, math.radians(rot))
    return objs


def houses():
    m = mat(hexc('#EFE9E1'), 0.45, coat=0.3)
    roof = mat(hexc('#6B5A63'), 0.5, coat=0.2)
    dim = mat(hexc('#3A3238'), 0.4)
    lit = mat(hexc('#FFD9A0'), 0.4, emit=(hexc('#FFC878'), 6.0))
    import random
    rnd = random.Random(4)
    for row in range(5):
        for k in range(-7, 8):
            if row == 0 and abs(k) < 2:
                continue
            x = k * 2.3 + rnd.uniform(-0.4, 0.4) + (1.1 if row % 2 else 0)
            y = 2.5 + row * 3.0 + rnd.uniform(-0.3, 0.3)
            one_house(x, y, 0.55 + rnd.uniform(-0.05, 0.05), m, roof, dim, rnd.uniform(-25, 25))
    one_house(0, -1.2, 1.6, m, roof, lit, -12)
    camera((0, -16, 4.2), (0, 3, 0.8), 45)


def house():
    m = mat(hexc('#EFE9E1'), 0.45, coat=0.3)
    one_house(0, 0, 1.6, m, mat(hexc('#6B5A63'), 0.5, coat=0.2), mat(hexc('#3A3238'), 0.4), -25)
    camera((0, -10, 3.6), (0, 0, 1.6), 55)


JOBS = {'houses': ((1400, 900), houses), 'house': ((900, 900), house), 'book3q': ((1600, 1200), book3q), 'clock': ((1000, 1100), clock), 'pin': ((500, 700), pin), 'crescent': ((900, 600), crescent)}
for name, (res, fn) in JOBS.items():
    if NAMES and name not in NAMES:
        continue
    reset(res)
    fn()
    render(name)
