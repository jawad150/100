"""3D pop-up tokens for BMHC "Tuned In" (Heritage Radio). Glossy soft-clay look in the BMHC palette.

Run: blender -b -P blender_tuned.py -- [name ...]  -> workspace_tuned/assets/<name>.png (RGBA, 900x900)
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = f'{ROOT}/workspace_tuned/assets'
os.makedirs(OUT, exist_ok=True)


def hexc(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (a,)


TEAL, MAG, ORANGE, GREEN, GOLD = hexc('#09999C'), hexc('#DB225E'), hexc('#F26721'), hexc('#76BF43'), hexc('#DDA54A')
DGREEN, IVORY, RED, WHITE, DARK = hexc('#16403A'), hexc('#F4EFE4'), hexc('#E8332A'), hexc('#F7F7F5'), hexc('#1D2423')
WOOD = hexc('#8A5A36')


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 900
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.9, 0.92, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.55
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 85
    cam.location = (0, -9.5, 3.4)
    cam.rotation_euler = (math.radians(71), 0, 0)
    for loc, en, sz in (((-4, -5, 6), 900, 4), ((5, -3, 3), 300, 3), ((0, 5, 4), 500, 3)):
        L = bpy.data.objects.new('L', bpy.data.lights.new('L', 'AREA'))
        L.data.energy, L.data.size = en, sz
        L.location = loc
        L.rotation_euler = (Vector((0, 0, 0.6)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(L)


def mat(col, rough=0.32, metal=0.0, emit=None, coat=0.4, trans=0.0):
    m = bpy.data.materials.new('m')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    if emit:
        b.inputs['Emission Color'].default_value = emit[0]
        b.inputs['Emission Strength'].default_value = emit[1]
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def act():
    return bpy.context.active_object


def bevel(o, w=0.06, seg=5):
    md = o.modifiers.new('b', 'BEVEL')
    md.width, md.segments = w, seg
    md.limit_method = 'ANGLE'
    return o


def smooth(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    except Exception:
        bpy.ops.object.shade_smooth()
    o.select_set(False)
    return o


def box(size, loc=(0, 0, 0), m=None, bw=0.08, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = act()
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel(o, bw)
    smooth(o)
    return setm(o, m) if m else o


def cyl(r, d, loc=(0, 0, 0), m=None, rot=(0, 0, 0), v=64, bw=0.04):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = act()
    if bw:
        bevel(o, bw)
    smooth(o)
    return setm(o, m) if m else o


def sph(r, loc=(0, 0, 0), m=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=64, ring_count=32)
    o = act()
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(o)
    return setm(o, m) if m else o


def torus(R, r, loc=(0, 0, 0), m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=96, minor_segments=24)
    o = act()
    smooth(o)
    return setm(o, m) if m else o


def text(s, size, loc, m, rot=(math.radians(90), 0, 0), ext=0.03, font='Poppins-Bold'):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = act()
    o.data.body = s
    fp = f'{ROOT}/workspace_sol/fonts/{font}.ttf'
    if os.path.exists(fp):
        o.data.font = bpy.data.fonts.load(fp)
    o.data.size = size
    o.data.extrude = ext
    o.data.bevel_depth = 0.008
    o.data.align_x, o.data.align_y = 'CENTER', 'CENTER'
    return setm(o, m)


def curve_path(pts, r, m, closed=False):
    cu = bpy.data.curves.new('c', 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for p, q in zip(sp.bezier_points, pts):
        p.co = q
        p.handle_left_type = p.handle_right_type = 'AUTO'
    sp.use_cyclic_u = closed
    cu.bevel_depth, cu.bevel_resolution = r, 6
    o = bpy.data.objects.new('c', cu)
    bpy.context.scene.collection.objects.link(o)
    cu.materials.append(m)
    return o


def group(objs, rot=(0, 0, 0), loc=(0, 0, 0), s=1.0):
    e = bpy.data.objects.new('g', None)
    bpy.context.scene.collection.objects.link(e)
    for o in objs:
        o.parent = e
    e.rotation_euler = rot
    e.location = loc
    e.scale = (s, s, s)
    return e


def frame_all():
    """Fit the camera to the object bounds."""
    bpy.context.view_layer.update()
    cam = bpy.context.scene.camera
    for o in bpy.context.scene.objects:
        o.select_set(o.type in ('MESH', 'CURVE', 'FONT'))
    bpy.ops.view3d.camera_to_view_selected() if False else None
    pts = []
    for o in bpy.context.scene.objects:
        if o.type in ('MESH', 'CURVE', 'FONT'):
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (lo + hi) / 2
    rad = (hi - lo).length / 2
    d = rad / math.tan(cam.data.angle / 2) * 1.12
    fwd = Vector((0, math.sin(math.radians(71)), -math.cos(math.radians(71))))
    cam.location = ctr - fwd * d


def render(name):
    frame_all()
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


# ------------------------------------------------------------------ tokens
def onair():
    body = box((2.6, 0.7, 1.1), m=mat(DARK, 0.4))
    face = box((2.3, 0.1, 0.82), loc=(0, -0.36, 0), m=mat(RED, 0.25, emit=(RED, 0.8)), bw=0.04)
    t = text('ON AIR', 0.4, (0, -0.47, -0.02), mat(WHITE, 0.3, emit=(WHITE, 1.2)), ext=0.03)
    br = cyl(0.12, 0.6, loc=(0, 0, 0.8), m=mat(DARK, 0.4))
    group([body, face, t, br], rot=(0, 0, math.radians(-14)))


def mic():
    g = mat(GOLD, 0.22, 0.95)
    head = sph(0.62, loc=(0, 0, 1.4), m=mat(hexc('#C9CCCC'), 0.38, 1.0), scale=(1, 1, 1.25))
    band = torus(0.63, 0.06, loc=(0, 0, 1.38), m=g)
    stem = cyl(0.22, 1.2, loc=(0, 0, 0.35), m=g)
    yoke = torus(0.75, 0.06, loc=(0, 0, 1.25), m=g, rot=(math.radians(90), 0, 0))
    base = cyl(0.55, 0.16, loc=(0, 0, -0.3), m=mat(TEAL, 0.3))
    group([head, band, stem, yoke, base], rot=(math.radians(-10), 0, math.radians(18)))


def pin():
    m = mat(MAG, 0.25)
    top = sph(0.75, loc=(0, 0, 1.2), m=m)
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0.0, depth=1.25, location=(0, 0, 0.38), rotation=(math.pi, 0, 0), vertices=64)
    cone = smooth(setm(act(), m))
    dot = sph(0.3, loc=(0, -0.55, 1.25), m=mat(WHITE, 0.3))
    ring = torus(0.9, 0.05, loc=(0, 0, -0.25), m=mat(GOLD, 0.2, 0.9))
    group([top, cone, dot, ring], rot=(0, 0, math.radians(-10)))


def radio():
    body = box((2.8, 1.1, 1.7), m=mat(TEAL, 0.3), bw=0.22)
    grille = box((1.25, 0.1, 1.15), loc=(-0.55, -0.55, -0.05), m=mat(GOLD, 0.3, 0.9), bw=0.05)
    for i in range(7):
        box((1.1, 0.06, 0.05), loc=(-0.55, -0.62, 0.38 - i * 0.14), m=mat(hexc('#8C6A2C'), 0.4, 0.8), bw=0.01)
    disp = box((0.95, 0.08, 0.38), loc=(0.72, -0.56, 0.25), m=mat(hexc('#F6D58A'), 0.3, emit=(hexc('#F6C25A'), 1.0)), bw=0.03)
    k1 = cyl(0.19, 0.18, loc=(0.48, -0.6, -0.33), m=mat(IVORY, 0.3), rot=(math.radians(90), 0, 0))
    k2 = cyl(0.19, 0.18, loc=(0.98, -0.6, -0.33), m=mat(IVORY, 0.3), rot=(math.radians(90), 0, 0))
    hnd = curve_path([(-1.0, 0, 0.85), (0, 0, 1.45), (1.0, 0, 0.85)], 0.07, mat(DARK, 0.4))
    ant = cyl(0.03, 1.6, loc=(1.15, 0.2, 1.5), m=mat(GOLD, 0.2, 1.0), rot=(0, math.radians(25), 0), bw=0)
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(0, 0, math.radians(-16)))


def tea():
    glassm = mat(hexc('#FFFFFF'), 0.05, trans=1.0, coat=0)
    cup = cyl(0.62, 1.15, loc=(0, 0, 0.55), m=mat(WHITE, 0.25), v=96, bw=0.06)
    liquid = cyl(0.56, 0.05, loc=(0, 0, 1.08), m=mat(hexc('#7A3A16'), 0.15), bw=0)
    band = torus(0.625, 0.045, loc=(0, 0, 0.75), m=mat(TEAL, 0.3))
    handle = torus(0.33, 0.08, loc=(0.7, 0, 0.6), m=mat(WHITE, 0.25), rot=(math.radians(90), 0, 0))
    saucer = cyl(1.05, 0.1, loc=(0, 0, -0.05), m=mat(ORANGE, 0.3), v=96)
    group([cup, liquid, band, handle, saucer], rot=(0, 0, math.radians(-30)))


def news():
    p = mat(IVORY, 0.55, coat=0.1)
    a = box((1.8, 0.06, 2.3), loc=(-0.05, 0, 0), m=p, bw=0.02, rot=(0, 0, math.radians(8)))
    b = box((1.8, 0.06, 2.3), loc=(0.05, -0.1, 0), m=p, bw=0.02, rot=(0, 0, math.radians(-6)))
    hd = box((1.5, 0.02, 0.32), loc=(0.06, -0.15, 0.85), m=mat(MAG, 0.4), bw=0.01, rot=(0, 0, math.radians(-6)))
    img = box((0.7, 0.02, 0.6), loc=(-0.3, -0.16, 0.25), m=mat(TEAL, 0.4), bw=0.01, rot=(0, 0, math.radians(-6)))
    for i in range(6):
        box((0.6 if i < 3 else 1.4, 0.02, 0.07), loc=(0.42 if i < 3 else 0.06, -0.16, 0.42 - i * 0.2 - (0.12 if i >= 3 else 0)),
            m=mat(hexc('#9A9A90'), 0.5), bw=0.005, rot=(0, 0, math.radians(-6)))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(-12), 0, math.radians(-14)))


def heart():
    bm = bmesh.new()
    pts = []
    for i in range(120):
        t = i / 120 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        z = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append(bm.verts.new((x / 14, 0, z / 14)))
    f = bm.faces.new(pts)
    me = bpy.data.meshes.new('h')
    bm.to_mesh(me)
    o = bpy.data.objects.new('h', me)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    sol = o.modifiers.new('s', 'SOLIDIFY')
    sol.thickness, sol.offset = 0.7, 0
    bv = o.modifiers.new('b', 'BEVEL')
    bv.width, bv.segments = 0.3, 8
    sub = o.modifiers.new('ss', 'SUBSURF')
    sub.levels = sub.render_levels = 2
    smooth(o)
    setm(o, mat(MAG, 0.22))
    group([o], rot=(0, 0, math.radians(-14)))


def bubbles():
    def bub(col, loc, s, flip=1):
        b = box((2.0 * s, 0.5 * s, 1.3 * s), loc=loc, m=mat(col, 0.28), bw=0.5 * s)
        bpy.ops.mesh.primitive_cone_add(radius1=0.28 * s, depth=0.6 * s, location=(loc[0] - 0.55 * s * flip, loc[1], loc[2] - 0.75 * s),
                                        rotation=(0, math.radians(180 + 25 * flip), 0), vertices=32)
        t = smooth(setm(act(), mat(col, 0.28)))
        dots = [sph(0.13 * s, loc=(loc[0] + (k - 1) * 0.45 * s, loc[1] - 0.27 * s, loc[2]), m=mat(WHITE, 0.3)) for k in range(3)]
        return [b, t] + dots
    o = bub(TEAL, (-0.5, 0, 0.5), 1.0) + bub(GREEN, (0.9, 0.5, -0.5), 0.8, -1)
    group(o, rot=(0, 0, math.radians(-12)))


def family():
    """A little house with a heart window (family conversations)."""
    walls = box((1.8, 1.6, 1.4), loc=(0, 0, 0), m=mat(IVORY, 0.4), bw=0.06)
    bpy.ops.mesh.primitive_cone_add(radius1=1.55, depth=1.0, vertices=4, location=(0, 0, 1.2), rotation=(0, 0, math.radians(45)))
    roof = act()
    roof.scale = (1.0, 0.9, 1)
    bpy.ops.object.transform_apply(scale=True)
    bevel(roof, 0.06)
    setm(roof, mat(GREEN, 0.3))
    door = box((0.45, 0.1, 0.8), loc=(0.35, -0.8, -0.3), m=mat(ORANGE, 0.3), bw=0.04)
    win = box((0.45, 0.1, 0.42), loc=(-0.4, -0.8, 0.1), m=mat(hexc('#FFD27A'), 0.3, emit=(hexc('#FFC45A'), 1.5)), bw=0.03)
    group([walls, roof, door, win], rot=(0, 0, math.radians(-22)))


def earbuds():
    w = mat(WHITE, 0.18, coat=0.8)
    objs = []
    for sx, rz in ((-0.55, 20), (0.55, -20)):
        b = sph(0.48, loc=(sx, 0, 0.5), m=w, scale=(1, 0.9, 1))
        st = cyl(0.16, 1.1, loc=(sx + 0.05 * (1 if sx > 0 else -1), 0, -0.25), m=w, rot=(0, math.radians(8 if sx > 0 else -8), 0))
        tip = sph(0.24, loc=(sx, -0.35, 0.55), m=mat(hexc('#D8D8D8'), 0.5), scale=(1, 0.8, 1))
        g = group([b, st, tip], rot=(0, 0, math.radians(rz)))
        objs.append(g)
    case = box((1.9, 0.9, 0.5), loc=(0, 0.2, -1.0), m=w, bw=0.25)
    led = sph(0.05, loc=(0, -0.26, -1.0), m=mat(GREEN, 0.3, emit=(GREEN, 4)))


def speaker():
    body = cyl(0.85, 1.6, loc=(0, 0, 0.8), m=mat(hexc('#3A4442'), 0.75, coat=0.1), v=96, bw=0.12)
    top = cyl(0.8, 0.05, loc=(0, 0, 1.62), m=mat(DARK, 0.3), v=96, bw=0)
    ring = torus(0.68, 0.06, loc=(0, 0, 1.66), m=mat(TEAL, 0.2, emit=(hexc('#2AD4D4'), 1.5)))
    group([body, top, ring])


def headphones():
    m = mat(TEAL, 0.28)
    band = curve_path([(-1.05, 0, 0.2), (-0.85, 0, 1.25), (0, 0, 1.7), (0.85, 0, 1.25), (1.05, 0, 0.2)], 0.14, m)
    cups = []
    for sx in (-1.05, 1.05):
        cups.append(cyl(0.55, 0.42, loc=(sx, 0, 0), m=mat(DARK, 0.45), rot=(0, math.radians(90), 0), bw=0.12))
        cups.append(cyl(0.45, 0.1, loc=(sx * 0.82, 0, 0), m=mat(GOLD, 0.25, 0.9), rot=(0, math.radians(90), 0), bw=0.03))
    group([band] + cups, rot=(0, 0, math.radians(-28)))


def play():
    body = cyl(1.0, 0.45, loc=(0, 0, 0), m=mat(ORANGE, 0.25), rot=(math.radians(90), 0, 0), v=96, bw=0.12)
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in ((-0.3, -0.24, 0.45), (-0.3, -0.24, -0.45), (0.48, -0.24, 0))]
    bm.faces.new(vs)
    me = bpy.data.meshes.new('t')
    bm.to_mesh(me)
    t = bpy.data.objects.new('t', me)
    bpy.context.scene.collection.objects.link(t)
    s = t.modifiers.new('s', 'SOLIDIFY')
    s.thickness = 0.12
    b = t.modifiers.new('b', 'BEVEL')
    b.width, b.segments = 0.05, 4
    setm(t, mat(WHITE, 0.3))
    group([body, t], rot=(0, 0, math.radians(-14)))


def arrow():
    """Rising arrow (elevate)."""
    m = mat(GOLD, 0.2, 0.9)
    shaft = box((0.55, 0.5, 1.6), loc=(0, 0, -0.2), m=m, bw=0.08)
    bpy.ops.mesh.primitive_cone_add(radius1=0.85, depth=0.9, vertices=4, location=(0, 0, 1.05), rotation=(0, 0, math.radians(45)))
    hd = act()
    hd.scale = (1, 0.42, 1)
    bpy.ops.object.transform_apply(scale=True)
    bevel(hd, 0.06)
    setm(hd, m)
    group([shaft, hd], rot=(0, math.radians(-12), math.radians(-18)))


def bulb():
    """Lightbulb (inform)."""
    glass = sph(0.8, loc=(0, 0, 0.6), m=mat(hexc('#FFE7A8'), 0.1, emit=(hexc('#FFD36A'), 2.5), coat=0.8))
    neck = cyl(0.38, 0.5, loc=(0, 0, -0.2), m=mat(GOLD, 0.25, 0.9))
    for i in range(3):
        torus(0.39, 0.04, loc=(0, 0, -0.08 - i * 0.13), m=mat(GOLD, 0.25, 0.9))
    tip = sph(0.2, loc=(0, 0, -0.5), m=mat(DARK, 0.4))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, math.radians(10), 0))


def star():
    """Eight-pointed star (inspire), gold."""
    bm = bmesh.new()
    pts = []
    for i in range(16):
        a = i / 16 * 2 * math.pi
        r = 1.0 if i % 2 == 0 else 0.62
        pts.append(bm.verts.new((r * math.sin(a), 0, r * math.cos(a))))
    bm.faces.new(pts)
    me = bpy.data.meshes.new('s')
    bm.to_mesh(me)
    o = bpy.data.objects.new('s', me)
    bpy.context.scene.collection.objects.link(o)
    s = o.modifiers.new('s', 'SOLIDIFY')
    s.thickness, s.offset = 0.32, 0
    b = o.modifiers.new('b', 'BEVEL')
    b.width, b.segments = 0.08, 4
    setm(o, mat(GOLD, 0.2, 0.95))
    c = sph(0.3, loc=(0, -0.2, 0), m=mat(TEAL, 0.25), scale=(1, 0.5, 1))
    group([o, c], rot=(0, 0, math.radians(-16)))


def phone():
    body = box((1.25, 0.16, 2.4), m=mat(DGREEN, 0.3), bw=0.18)
    scr = box((1.08, 0.04, 2.15), loc=(0, -0.08, 0), m=mat(hexc('#0F2A26'), 0.15, emit=(hexc('#0F2A26'), 0.3)), bw=0.12)
    disc = cyl(0.36, 0.04, loc=(0, -0.11, 0.35), m=mat(GOLD, 0.25, 0.8, emit=(GOLD, 0.6)), rot=(math.radians(90), 0, 0), bw=0.01)
    btn = box((0.8, 0.04, 0.22), loc=(0, -0.11, -0.7), m=mat(MAG, 0.3, emit=(MAG, 0.8)), bw=0.1)
    group([body, scr, disc, btn], rot=(math.radians(-6), 0, math.radians(-18)))


def mast():
    """A little radio mast with gold rings (the signal)."""
    m = mat(IVORY, 0.35)
    legs = [cyl(0.05, 2.6, loc=(x * 0.35, 0, 0), m=m, rot=(0, math.radians(-x * 7.5), 0), bw=0) for x in (-1, 1)]
    for i in range(5):
        z = -1.0 + i * 0.45
        w = 0.35 * (1 - (z + 1.3) / 2.6) + 0.02
        box((2 * w + 0.06, 0.06, 0.06), loc=(0, 0, z), m=m, bw=0.01)
    top = sph(0.16, loc=(0, 0, 1.36), m=mat(RED, 0.3, emit=(RED, 4)))
    for i, r in enumerate((0.45, 0.75, 1.05)):
        torus(r, 0.035, loc=(0, 0, 1.36), m=mat(GOLD, 0.2, 0.9), rot=(math.radians(90), 0, 0))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs)


TOK = dict(onair=onair, mic=mic, pin=pin, radio=radio, tea=tea, news=news, heart=heart, bubbles=bubbles, family=family,
           earbuds=earbuds, speaker=speaker, headphones=headphones, play=play, arrow=arrow, bulb=bulb, star=star, phone=phone, mast=mast)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for n in (argv or list(TOK)):
        reset()
        TOK[n]()
        render(n)
