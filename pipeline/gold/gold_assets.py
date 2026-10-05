"""Render the black-and-gold 3D elements for the gold-market reel (transparent PNG sequences).

Every element maps to a line of the script. Gold is #E49F38 (sRGB) everywhere, rendered as metal.

Usage: python3 gold_assets.py <name> [<name> ...]      (ONE=1 renders a single preview frame)
Names: ingot coin_au dollar3d arrow_crash arrow_up candles3d fed bond barrel shield
       cal_28sep cal_30sep cal_oct num_<key> (see NUMBERS)
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

S = os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace')))
OUT = S + '/assets3d'
FONTS = S + '/fonts'


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


GOLD = tuple(srgb_to_lin(int('E49F38'[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1,)
BLACK = (0.006, 0.006, 0.006, 1)

NUMBERS = {
    '3': '3',
    '2007': '2007',
    '025': '0.25%',
    '6070': '60-70%',
    '4pct': '-4%',
    '4145': '$4,145',
    '40': '40%',
    '4200': '$4,200',
}


def reset(res=(600, 600), samples=32):
    samples = int(os.environ.get('SAMPLES', samples))
    k = float(os.environ.get('RES', '1.25'))
    res = (int(res[0] * k), int(res[1] * k))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.cycles.max_bounces = 6
    sc.cycles.glossy_bounces = 4
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.03, 0.022, 0.014, 1)
    bg.inputs['Strength'].default_value = 1.0
    return sc


def mat(name, color, rough=0.25, metal=0.0, coat=0.0, emission=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.04
    if emission:
        b.inputs['Emission Color'].default_value = emission
        b.inputs['Emission Strength'].default_value = estr
    return m


def gold(rough=0.2):
    return mat('gold', GOLD, rough=rough, metal=1.0)


def black():
    return mat('black', BLACK, rough=0.12, coat=1.0, metal=0.0)


def softbox(loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object
    l.data.shape = 'RECTANGLE'
    l.data.size, l.data.size_y = size
    l.data.energy = energy
    l.data.color = color
    return l


def panel(loc, rot, size, strength, color=(1, 1, 1)):
    """Emissive strip visible only in reflections: gives metals their bright streaks."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    p = bpy.context.object
    p.scale = (size[0], size[1], 1)
    m = bpy.data.materials.new('panel')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = color + (1,)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    p.data.materials.append(m)
    p.visible_camera = False
    p.visible_shadow = False
    return p


def studio(key=900, rim=1600, fill=150):
    warm = (1.0, 0.88, 0.72)
    softbox((-3.2, -3.6, 4.0), (math.radians(50), 0, math.radians(-40)), (3, 3), key)
    softbox((3.8, 2.4, 1.8), (math.radians(70), 0, math.radians(125)), (2.5, 5), rim, warm)
    softbox((-3.8, 2.0, -0.5), (math.radians(95), 0, math.radians(-120)), (2.0, 4), rim * 0.6, warm)
    softbox((3.5, -3, -1.5), (math.radians(110), 0, math.radians(45)), (4, 4), fill, warm)
    panel((-2.6, -2.6, 3.4), (math.radians(50), 0, math.radians(-40)), (3.0, 0.4), 22)
    panel((3.0, 1.4, 0.6), (math.radians(80), 0, math.radians(120)), (0.45, 4.5), 26, warm)
    panel((-3.0, 1.0, 0.0), (math.radians(90), 0, math.radians(-115)), (0.35, 4.0), 18, warm)
    panel((0.0, -4.0, -2.4), (math.radians(125), 0, 0), (5.0, 0.5), 10, warm)
    panel((0.0, -3.0, 3.6), (math.radians(35), 0, 0), (4.0, 1.2), 6)


def camera(loc=(0, -7, 0.6), target=(0, 0, 0), lens=60):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    bpy.context.scene.camera = c
    return c


def render_seq(name, nframes, update):
    d = f'{OUT}/{name}'
    os.makedirs(d, exist_ok=True)
    sc = bpy.context.scene
    frames = range(nframes)
    if os.environ.get('ONE'):
        frames = [int(os.environ.get('ONE_AT', nframes - 1))]
    for i in frames:
        update(i, nframes)
        sc.render.filepath = f'{d}/{i:03d}.png'
        if os.environ.get('SKIP_EXISTING') and os.path.exists(sc.render.filepath):
            continue
        bpy.ops.render.render(write_still=True)
        print('rendered', name, i, flush=True)


def bevel(o, width=0.04, seg=4):
    m = o.modifiers.new('bv', 'BEVEL')
    m.width = width
    m.segments = seg
    m.limit_method = 'ANGLE'
    return m


def shade_smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def text_obj(body, fontfile, size=1.0, extrude=0.1, bev=0.015, align='CENTER'):
    cu = bpy.data.curves.new('txt', 'FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load(f'{FONTS}/{fontfile}')
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bev
    cu.bevel_resolution = 3
    cu.align_x = align
    cu.align_y = 'CENTER'
    o = bpy.data.objects.new('txt', cu)
    bpy.context.scene.collection.objects.link(o)
    return o


def fit_width(o, maxw):
    bpy.context.view_layer.update()
    w = o.dimensions.x
    if w > maxw:
        k = maxw / w
        o.scale = (k, k, k)


def poly_curve(pts, extrude=0.1, bev=0.02, name='poly'):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = extrude
    cu.bevel_depth = bev
    cu.bevel_resolution = 4
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0], q[1], 0, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    return o


def tube(pts, radius=0.06, name='tube'):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0], q[1], q[2], 1)
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    return o


def empty_root():
    bpy.ops.object.empty_add(location=(0, 0, 0))
    return bpy.context.object


def ease_out_back(x, s=1.4):
    x = min(max(x, 0.0), 1.0)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_out_cubic(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- elements

def ingot():
    """Gold bar (Sona). Loops a slow tumble."""
    reset((700, 700), 40)
    studio()
    camera((0, -5.6, 1.5), (0, 0, 0), 55)
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        v.co.x *= 2.0
        v.co.y *= 1.0
        v.co.z *= 0.5
        if v.co.z > 0:
            v.co.x *= 0.84
            v.co.y *= 0.76
    bm.to_mesh(o.data)
    bm.free()
    bevel(o, 0.045, 4)
    o.data.materials.append(gold(0.17))
    t = text_obj('999.9', 'Cinzel-900.ttf', 0.30, 0.02, 0.006)
    t.location = (0, 0, 0.255)
    t.data.materials.append(gold(0.28))
    t.parent = o
    t2 = text_obj('GOLD', 'Cinzel-900.ttf', 0.18, 0.015, 0.004)
    t2.location = (0, -0.2, 0.255)
    t2.data.materials.append(gold(0.28))
    t2.parent = o

    def upd(i, n):
        ph = i / n * 2 * math.pi
        o.rotation_euler = (math.radians(28) + 0.18 * math.sin(ph), 0.12 * math.sin(ph * 2), ph)
    render_seq('ingot', 36, upd)


def coin_au():
    """Gold coin with 'Au' - 'Gold koi interest nahi deta'."""
    reset((520, 520), 40)
    studio()
    camera((0, -7, 0.4), (0, 0, 0), 60)
    root = empty_root()
    bpy.ops.mesh.primitive_cylinder_add(radius=1.25, depth=0.2, vertices=128, rotation=(math.radians(90), 0, 0))
    c = bpy.context.object
    bevel(c, 0.04, 4)
    shade_smooth(c)
    c.data.materials.append(gold(0.16))
    c.parent = root
    for sy in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.12, minor_radius=0.045, major_segments=128, minor_segments=16,
                                         location=(0, sy * 0.1, 0), rotation=(math.radians(90), 0, 0))
        r = bpy.context.object
        shade_smooth(r)
        r.data.materials.append(gold(0.12))
        r.parent = root
        t = text_obj('Au', 'Cinzel-900.ttf', 1.0, 0.03, 0.01)
        t.rotation_euler = (math.radians(90), 0, 0 if sy < 0 else math.pi)
        t.location = (0, sy * 0.1 + sy * 0.0, -0.05)
        t.data.materials.append(gold(0.3))
        t.parent = root

    def upd(i, n):
        ph = i / n * 2 * math.pi
        root.rotation_euler = (math.radians(8), 0, ph)
    render_seq('coin_au', 36, upd)


def dollar3d():
    """3D dollar sign - 'US Dollar strong hua'."""
    reset((520, 620), 40)
    studio()
    camera((0, -7, 0.3), (0, 0, 0), 58)
    t = text_obj('$', 'Cinzel-900.ttf', 3.0, 0.24, 0.03)
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(gold(0.15))

    def upd(i, n):
        ph = i / n * 2 * math.pi
        t.rotation_euler = (math.radians(90), 0, math.radians(38) * math.sin(ph))
    render_seq('dollar3d', 36, upd)


def _zig(up):
    pts = [(-1.6, 0.9), (-1.0, 0.35), (-0.55, 0.6), (0.0, -0.15), (0.35, 0.1), (1.0, -0.85)]
    if up:
        pts = [(-1.6, -0.6), (-1.05, -0.15), (-0.6, -0.4), (0.0, 0.25), (0.4, 0.05), (1.0, 0.85)]
    return pts


def arrow(up):
    """Zig-zag chart arrow. Down = 'sharply neeche', up = 'Gold wapis $4,200'."""
    name = 'arrow_up' if up else 'arrow_crash'
    reset((720, 640), 40)
    studio()
    camera((0, -6.4, 0.3), (0, 0, 0), 55)
    pts2 = _zig(up)
    pts = [(x, 0, y) for x, y in pts2]
    tb = tube(pts, 0.15)
    tb.data.materials.append(gold(0.16))
    bpy.ops.mesh.primitive_cone_add(radius1=0.4, radius2=0, depth=0.72, vertices=64)
    head = bpy.context.object
    shade_smooth(head)
    head.data.materials.append(gold(0.16))
    a, b = Vector(pts[-2]), Vector(pts[-1])
    d = (b - a).normalized()
    head.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    # dots at the joints
    for p in pts[1:-1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=p, segments=48, ring_count=24)
        s = bpy.context.object
        shade_smooth(s)
        s.data.materials.append(gold(0.12))
    segs = [(Vector(pts[k]) - Vector(pts[k + 1])).length for k in range(len(pts) - 1)]
    total = sum(segs)

    def upd(i, n):
        grow = ease_out_cubic(i / (n * 0.6))
        tb.data.bevel_factor_end = max(grow, 0.001)
        # place head at the tip of the grown tube
        L = grow * total
        acc = 0
        for k, sl in enumerate(segs):
            if acc + sl >= L - 1e-6:
                u = (L - acc) / sl
                tip = Vector(pts[k]).lerp(Vector(pts[k + 1]), u)
                dd = (Vector(pts[k + 1]) - Vector(pts[k])).normalized()
                break
            acc += sl
        head.location = tip + dd * 0.25
        head.rotation_euler = dd.to_track_quat('Z', 'Y').to_euler()
        hs = ease_out_back(i / (n * 0.6) * 1.2)
        head.scale = (hs, hs, hs)
        sway = math.sin(i / n * 2 * math.pi)
        bpy.context.scene.camera.location = (math.sin(sway * 0.15) * 1.2, -6.4, 0.3 + 0.2 * sway)
        cam = bpy.context.scene.camera
        cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    render_seq(name, 45, upd)


def candles3d():
    """Gold/black 3D candlestick chart: rally, sharp retracement, small rebound."""
    reset((820, 620), 40)
    studio()
    root = empty_root()
    # (open, close, low, high)
    data = [(0.0, 0.5, -0.15, 0.65), (0.45, 1.0, 0.3, 1.15), (0.95, 1.6, 0.8, 1.8), (1.55, 2.1, 1.4, 2.3),
            (2.05, 1.3, 1.15, 2.2), (1.35, 0.55, 0.4, 1.45), (0.6, 0.15, -0.05, 0.7), (0.2, 0.75, 0.05, 0.9),
            (0.7, 1.05, 0.6, 1.2)]
    gm, bm_ = gold(0.18), black()
    bodies = []
    for k, (o_, c_, lo, hi) in enumerate(data):
        x = (k - (len(data) - 1) / 2) * 0.62
        up = c_ >= o_
        bpy.ops.mesh.primitive_cube_add(size=1)
        b = bpy.context.object
        h = max(abs(c_ - o_), 0.06)
        b.scale = (0.38, 0.38, h)
        b.location = (x, 0, (o_ + c_) / 2 - 1.0)
        bevel(b, 0.03, 3)
        b.data.materials.append(gm if up else bm_)
        b.parent = root
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=hi - lo, vertices=24, location=(x, 0, (hi + lo) / 2 - 1.0))
        wk = bpy.context.object
        wk.data.materials.append(gm)
        wk.parent = root
        bodies.append((b, wk, b.location.z, b.scale.z, wk.location.z, wk.scale.z, k))
    # thin gold baseline
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -1.25))
    base = bpy.context.object
    base.scale = (len(data) * 0.62 + 0.4, 0.5, 0.04)
    bevel(base, 0.015, 2)
    base.data.materials.append(bm_)
    base.parent = root
    camera((0, -8.6, 1.6), (0, 0, -0.05), 50)

    def upd(i, n):
        for b, wk, bz, bh, wz, wh, k in bodies:
            g = ease_out_back((i - k * 2.2) / 10.0, 1.2)
            g = max(g, 0.001)
            b.scale.z = bh * g
            wk.scale.z = wh * min(1, max(g, 0.001))
        root.rotation_euler = (0, 0, math.radians(-18 + 26 * (i / n)))
    render_seq('candles3d', 36, upd)


def fed():
    """Classical bank building with 'FED' - 'Fed ke rate hike'."""
    reset((640, 600), 40)
    studio()
    root = empty_root()
    gm, bm_ = gold(0.2), black()
    for k, (w, d, h, z) in enumerate([(3.2, 1.7, 0.14, -1.25), (2.95, 1.5, 0.14, -1.11), (2.7, 1.3, 0.14, -0.97)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
        s = bpy.context.object
        s.scale = (w, d, h)
        bevel(s, 0.02, 2)
        s.data.materials.append(gm if k == 2 else bm_)
        s.parent = root
    for k in range(6):
        x = (k - 2.5) * 0.46
        for y in (-0.42, 0.42):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.5, vertices=32, location=(x, y, -0.15))
            c = bpy.context.object
            shade_smooth(c)
            c.data.materials.append(gm)
            c.parent = root
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.63))
            cap = bpy.context.object
            cap.scale = (0.32, 0.32, 0.08)
            bevel(cap, 0.015, 2)
            cap.data.materials.append(gm)
            cap.parent = root
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.82))
    arch = bpy.context.object
    arch.scale = (2.85, 1.3, 0.3)
    bevel(arch, 0.02, 2)
    arch.data.materials.append(bm_)
    arch.parent = root
    ped = poly_curve([(-1.5, 0), (1.5, 0), (0, 0.62)], extrude=0.62, bev=0.02, name='ped')
    ped.rotation_euler = (math.radians(90), 0, 0)
    ped.location = (0, 0, 0.97)
    ped.data.materials.append(gm)
    ped.parent = root
    t = text_obj('FED', 'Cinzel-900.ttf', 0.26, 0.02, 0.006)
    t.rotation_euler = (math.radians(90), 0, 0)
    t.location = (0, -0.67, 0.82)
    t.data.materials.append(gm)
    t.parent = root
    camera((0, -7.0, 1.0), (0, 0, -0.15), 52)

    def upd(i, n):
        root.rotation_euler = (0, 0, math.radians(24) * math.sin(i / n * 2 * math.pi) - math.radians(10))
    render_seq('fed', 36, upd)


def bond():
    """US Treasury 10Y bond certificate with a rising yield line."""
    reset((700, 560), 40)
    studio()
    root = empty_root()
    gm, bm_ = gold(0.2), black()
    bpy.ops.mesh.primitive_cube_add(size=1)
    card = bpy.context.object
    card.scale = (2.6, 0.08, 1.7)
    bevel(card, 0.04, 4)
    card.data.materials.append(bm_)
    card.parent = root
    fr = [(-1.18, -0.73), (1.18, -0.73), (1.18, 0.73), (-1.18, 0.73)]
    frame_o = tube([(x, -0.05, y) for x, y in fr + [fr[0]]], 0.022, 'frame')
    frame_o.data.materials.append(gm)
    frame_o.parent = root
    for body, size, z, font in (('US TREASURY', 0.18, 0.5, 'Cinzel-900.ttf'), ('10Y', 0.56, 0.05, 'Cinzel-900.ttf'),
                                ('YIELD', 0.15, -0.38, 'Cinzel-700.ttf')):
        t = text_obj(body, font, size, 0.02, 0.005)
        fit_width(t, 1.3)
        t.rotation_euler = (math.radians(90), 0, 0)
        t.location = (-0.45, -0.06, z)
        t.data.materials.append(gm)
        t.parent = root
    line = tube([(0.25, -0.07, -0.5), (0.48, -0.07, -0.3), (0.62, -0.07, -0.38), (0.8, -0.07, -0.05),
                 (0.92, -0.07, -0.12), (1.05, -0.07, 0.45)], 0.03, 'yl')
    line.data.materials.append(gm)
    line.parent = root
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0, depth=0.18, vertices=32, location=(1.08, -0.07, 0.55))
    hd = bpy.context.object
    hd.rotation_euler = (0, math.radians(12), 0)
    hd.data.materials.append(gm)
    hd.parent = root
    camera((0, -6.6, 0.6), (0, 0, 0), 55)

    def upd(i, n):
        ph = i / n * 2 * math.pi
        root.rotation_euler = (math.radians(6) * math.sin(ph), 0, math.radians(-16) + math.radians(14) * math.sin(ph))
        line.data.bevel_factor_end = max(ease_out_cubic(i / (n * 0.5)), 0.001)
    render_seq('bond', 36, upd)


def barrel():
    """Oil barrel - 'Middle East oil risk'."""
    reset((520, 600), 40)
    studio()
    root = empty_root()
    gm, bm_ = gold(0.2), black()
    bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=2.6, vertices=96)
    b = bpy.context.object
    bevel(b, 0.06, 4)
    shade_smooth(b)
    b.data.materials.append(bm_)
    b.parent = root
    for z in (-0.8, 0.8, -1.25, 1.25):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.97, minor_radius=0.05, major_segments=96, minor_segments=16,
                                         location=(0, 0, z))
        r = bpy.context.object
        shade_smooth(r)
        r.data.materials.append(gm)
        r.parent = root
    drop = [(0.0, 0.46)] + [(0.26 * math.cos(t), -0.08 + 0.26 * math.sin(t)) for t in
                            [math.radians(30 - 240 * k / 47) for k in range(48)]]
    dr = poly_curve(drop, extrude=0.05, bev=0.012, name='drop')
    dr.rotation_euler = (math.radians(90), 0, 0)
    dr.location = (0, -0.98, 0.0)
    dr.data.materials.append(gm)
    dr.parent = root
    camera((0, -7.2, 1.6), (0, 0, 0), 55)

    def upd(i, n):
        root.rotation_euler = (0, 0, math.radians(20) * math.sin(i / n * 2 * math.pi))
    render_seq('barrel', 36, upd)


def shield():
    """Gold shield with check - 'risk manage kar sakte hain'."""
    reset((520, 600), 40)
    studio()
    root = empty_root()
    def qb(p0, p1, p2, n):
        return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
                 (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in [k / n for k in range(n)]]
    out = [(-1 + 2 * k / 30, 1.0 + 0.08 * math.sin(math.pi * k / 30)) for k in range(31)]
    out += [(1.0, 1.0 - 0.75 * k / 10) for k in range(1, 10)]
    out += qb((1.0, 0.25), (0.95, -0.75), (0.0, -1.3), 24)
    out += qb((0.0, -1.3), (-0.95, -0.75), (-1.0, 0.25), 24)
    out += [(-1.0, 0.25 + 0.75 * k / 10) for k in range(10)]
    s1 = poly_curve(out, extrude=0.16, bev=0.05, name='sh')
    s1.rotation_euler = (math.radians(90), 0, 0)
    s1.data.materials.append(gold(0.16))
    s1.parent = root
    inner = [(x * 0.8, y * 0.8 + 0.02) for x, y in out]
    s2 = poly_curve(inner, extrude=0.05, bev=0.02, name='shi')
    s2.rotation_euler = (math.radians(90), 0, 0)
    s2.location = (0, -0.18, 0)
    s2.data.materials.append(black())
    s2.parent = root
    ck = tube([(-0.38, -0.27, 0.1), (-0.1, -0.27, -0.2), (0.42, -0.27, 0.42)], 0.09, 'ck')
    ck.data.materials.append(gold(0.14))
    ck.parent = root
    camera((0, -7.0, 0.4), (0, 0, 0), 55)

    def upd(i, n):
        root.rotation_euler = (0, 0, math.radians(26) * math.sin(i / n * 2 * math.pi))
        ck.data.bevel_factor_end = max(ease_out_cubic((i - 6) / 18), 0.001)
    render_seq('shield', 36, upd)


def calendar(key, top, big):
    """Calendar block for the dates in the script."""
    reset((520, 560), 40)
    studio()
    root = empty_root()
    gm, bm_ = gold(0.2), black()
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.object
    body.scale = (2.0, 0.35, 2.1)
    bevel(body, 0.12, 6)
    body.data.materials.append(bm_)
    body.parent = root
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.8))
    hdr = bpy.context.object
    hdr.scale = (2.02, 0.37, 0.55)
    bevel(hdr, 0.1, 6)
    hdr.data.materials.append(gm)
    hdr.parent = root
    for x in (-0.55, 0.55):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.045, location=(x, 0, 1.08),
                                         rotation=(0, math.radians(90), 0))
        r = bpy.context.object
        r.data.materials.append(gm)
        r.parent = root
    t1 = text_obj(top, 'Cinzel-900.ttf', 0.30, 0.02, 0.004)
    fit_width(t1, 1.7)
    t1.rotation_euler = (math.radians(90), 0, 0)
    t1.location = (0, -0.19, 0.78)
    t1.data.materials.append(bm_)
    t1.parent = root
    t2 = text_obj(big, 'Cinzel-900.ttf', 1.05, 0.06, 0.01)
    fit_width(t2, 1.65)
    t2.rotation_euler = (math.radians(90), 0, 0)
    t2.location = (0, -0.2, -0.28)
    t2.data.materials.append(gm)
    t2.parent = root
    camera((0, -7.0, 0.8), (0, 0, 0), 55)

    def upd(i, n):
        root.rotation_euler = (math.radians(4), 0, math.radians(-22) * math.sin(i / n * 2 * math.pi))
    render_seq('cal_' + key, 36, upd)


def number(key):
    """3D extruded gold number that swings in from edge-on and settles (then the compositor holds it)."""
    txt = NUMBERS[key]
    n_ch = len(txt)
    w = int(min(1500, 300 + 190 * n_ch))
    reset((w, 520), 40)
    studio(key=800, rim=2000)
    t = text_obj(txt, 'Cinzel-900.ttf', 2.4, 0.3, 0.035)
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(gold(0.16))
    bpy.context.view_layer.update()
    half_fov = math.atan(18 / 62)
    dist = max(10.5, t.dimensions.x / 2 * 1.2 / math.tan(half_fov))
    camera((0, -dist, 0.0), (0, 0, 0), 62)

    def upd(i, n):
        x = i / (n - 1)
        e = ease_out_back(x / 0.7, 1.3)
        ang = (1 - e) * 85
        t.rotation_euler = (math.radians(90 + (1 - min(e, 1)) * 18), 0, math.radians(ang))
    render_seq('num_' + key, 30, upd)


def ring3d():
    """Ambient gimbal of two thin gold rings (seamless loop) - floats in the empty side of frame."""
    reset((520, 520), 40)
    studio()
    camera((0, -7, 0.4), (0, 0, 0), 60)
    outer, inner = empty_root(), empty_root()
    inner.parent = outer
    for o, R, r in ((outer, 1.55, 0.07), (inner, 1.18, 0.05)):
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=160, minor_segments=24)
        t = bpy.context.object
        shade_smooth(t)
        t.data.materials.append(gold(0.12))
        t.parent = o

    def upd(i, n):
        ph = i / n * 2 * math.pi
        outer.rotation_euler = (math.radians(62) + 0.25 * math.sin(ph), 0, ph)
        inner.rotation_euler = (ph, 0, 0)
    render_seq('ring3d', 48, upd)


def orb3d():
    """Small polished gold sphere for ambient depth."""
    reset((300, 300), 48)
    studio()
    camera((0, -7, 0.4), (0, 0, 0), 60)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.6, segments=96, ring_count=48)
    o = bpy.context.object
    shade_smooth(o)
    o.data.materials.append(gold(0.32))
    render_seq('orb3d', 1, lambda i, n: None)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a == 'ingot':
            ingot()
        elif a == 'coin_au':
            coin_au()
        elif a == 'dollar3d':
            dollar3d()
        elif a == 'arrow_crash':
            arrow(False)
        elif a == 'arrow_up':
            arrow(True)
        elif a == 'candles3d':
            candles3d()
        elif a == 'fed':
            fed()
        elif a == 'bond':
            bond()
        elif a == 'barrel':
            barrel()
        elif a == 'shield':
            shield()
        elif a == 'cal_28sep':
            calendar('28sep', 'SEPTEMBER', '28')
        elif a == 'cal_30sep':
            calendar('30sep', 'SEPTEMBER', '30')
        elif a == 'cal_oct':
            calendar('oct', 'OCTOBER', '25bp')
        elif a == 'ring3d':
            ring3d()
        elif a == 'orb3d':
            orb3d()
        elif a.startswith('num_'):
            number(a[4:])
        else:
            print('unknown asset', a)
