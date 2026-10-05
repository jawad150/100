"""Photoreal vertical b-roll shots for the reel's fast montages (Blender Cycles, 1080x1920).

Dark studio sets, glossy black floor, shallow depth of field, motion blur and background bokeh,
each a short camera move that cuts on a sound effect.

Usage: python3 gold_broll.py <name> [<name> ...]     (ONE=1 renders a single preview frame)
Names: br_bars br_crash br_coins br_dollar br_fed br_barrels br_barfall
"""
import os, sys, math, random
os.environ.setdefault('RES', '1.0')
import bpy, bmesh
from mathutils import Vector
import gold_assets as A

OUT = A.S + '/broll'


def setup(samples=14):
    sc = A.reset((864, 1536), samples)
    sc.render.film_transparent = False
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.010, 0.012, 1)
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.fps = 30
    return sc


def floor(z=0.0, rough=0.07):
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, z))
    p = bpy.context.object
    p.data.materials.append(A.mat('floor', (0.006, 0.007, 0.008, 1), rough=rough, coat=1.0))
    return p


def backdrop(y=14, color=(0.010, 0.030, 0.034, 1)):
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, y, 10), rotation=(math.radians(90), 0, 0))
    p = bpy.context.object
    p.data.materials.append(A.mat('back', color, rough=0.9))
    return p


def bokeh_lights(n=22, y=(16, 24), seed=3, color=(1.0, 0.62, 0.26), strength=3):
    rng = random.Random(seed)
    m = bpy.data.materials.new('bk')
    m.use_nodes = True
    nt = m.node_tree
    for k in list(nt.nodes):
        nt.nodes.remove(k)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = color + (1,)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    for _ in range(n):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rng.uniform(0.15, 0.32), segments=12, ring_count=8,
                                             location=(rng.uniform(-9, 9), rng.uniform(*y), rng.uniform(0.5, 12)))
        s = bpy.context.object
        s.data.materials.append(m)
        s.visible_shadow = False


def key_lights(warm=1.0):
    w = (1.0, 0.80, 0.55)
    A.softbox((-3.5, -2.5, 4.5), (math.radians(45), 0, math.radians(-40)), (2.5, 2.5), 1500 * warm, w)
    A.softbox((2.5, -5.0, 3.0), (math.radians(60), 0, math.radians(30)), (3, 2), 500, w)              # soft fill
    A.softbox((4.0, 3.0, 2.5), (math.radians(70), 0, math.radians(130)), (1.5, 5), 1400, (0.55, 0.85, 1.0))  # teal rim
    A.softbox((-4.0, 3.0, 2.0), (math.radians(80), 0, math.radians(-130)), (1.5, 5), 1100 * warm, w)        # gold rim
    A.panel((-2.6, -2.6, 3.4), (math.radians(50), 0, math.radians(-40)), (3.0, 0.4), 18)
    A.panel((3.0, 1.4, 0.8), (math.radians(80), 0, math.radians(120)), (0.45, 4.5), 22, w)
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.visible_camera = False


def cam(loc, target, lens=50, fstop=2.0, focus=None):
    c = A.camera(loc, target, lens)
    c.data.sensor_width = 24
    c.data.dof.use_dof = True
    c.data.dof.aperture_fstop = fstop
    c.data.dof.focus_distance = focus or (Vector(target) - Vector(loc)).length
    return c


def aim(c, loc, target):
    c.location = loc
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp3(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def bar_obj(loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, label=True):
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
    A.bevel(o, 0.045, 4)
    o.data.materials.append(A.gold(0.16))
    if label:
        t = A.text_obj('999.9', 'Cinzel-900.ttf', 0.30, 0.02, 0.006)
        t.location = (0, 0, 0.255)
        t.data.materials.append(A.gold(0.3))
        t.parent = o
        t2 = A.text_obj('FINE GOLD', 'Cinzel-900.ttf', 0.13, 0.015, 0.004)
        t2.location = (0, -0.22, 0.255)
        t2.data.materials.append(A.gold(0.3))
        t2.parent = o
    o.location = loc
    o.rotation_euler = rot
    o.scale = (scale, scale, scale)
    return o


def coin_obj(loc, rot, r=0.42):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=r * 0.16, vertices=64, location=loc, rotation=rot)
    c = bpy.context.object
    A.bevel(c, r * 0.04, 3)
    A.shade_smooth(c)
    c.data.materials.append(A.gold(0.14))
    return c


def render(name, n, upd):
    A.OUT = OUT
    A.render_seq(name, n, upd)

# ---------------------------------------------------------------- shots


def br_bars():
    """Pyramid of gold bars, low macro dolly with shallow focus ('Sona')."""
    setup()
    floor()
    backdrop()
    bokeh_lights()
    key_lights()
    for row, n in enumerate((4, 3, 2, 1)):                       # stacked pyramid, rows touching
        for k in range(n):
            bar_obj(((k - (n - 1) / 2) * 1.75, 0.0, 0.25 + row * 0.5), (0, 0, 0), 1.0, label=(row == 3))
    c = cam((-3.0, -8.0, 3.0), (0, 0, 1.0), 35, 1.4)

    def upd(i, n):
        u = ease(i / (n - 1))
        loc = lerp3((-2.6, -9.6, 2.2), (0.4, -8.0, 2.9), u)
        aim(c, loc, (0, 0, 1.1))
        c.data.dof.focus_distance = (Vector((0, -0.4, 1.6)) - Vector(loc)).length
    render('br_bars', 15, upd)


def br_crash():
    """3D candlestick chart crashing: camera races along the red sell-off ('crash')."""
    setup()
    floor()
    backdrop(color=(0.012, 0.008, 0.008, 1))
    bokeh_lights(color=(1.0, 0.25, 0.15), seed=5)
    key_lights(0.8)
    red = A.mat('red', (0.35, 0.015, 0.01, 1), rough=0.22, coat=1.0, emission=(1.0, 0.06, 0.03, 1), estr=0.25)
    gld = A.gold(0.2)
    rng = random.Random(9)
    price, pts = 3.6, []
    for k in range(18):
        up = k < 6
        d = rng.uniform(0.25, 0.5) * (1 if up else -1.25)
        o_, c_ = price, max(0.4, price + d)
        lo, hi = min(o_, c_), max(o_, c_)
        x = k * 0.75 - 4.5
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, (lo + hi) / 2))
        b = bpy.context.object
        b.scale = (0.42, 0.42, max(hi - lo, 0.08))
        A.bevel(b, 0.03, 3)
        b.data.materials.append(gld if up else red)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=hi - lo + 0.6, location=(x, 0, (lo + hi) / 2))
        w = bpy.context.object
        w.data.materials.append(gld if up else red)
        pts.append((x, -0.5, c_ + 0.15))
        price = c_
    t = A.tube(pts, 0.04, 'line')
    t.data.materials.append(A.mat('lr', (1, 0.2, 0.1, 1), emission=(1.0, 0.15, 0.05, 1), estr=8))
    c = cam((-5, -6, 4), (-3, 0, 3), 30, 1.6)
    xs = [q[0] for q in pts]
    zs = [q[2] for q in pts]

    def line_z(x):
        for j in range(len(xs) - 1):
            if xs[j] <= x <= xs[j + 1]:
                f = (x - xs[j]) / (xs[j + 1] - xs[j])
                return zs[j] + (zs[j + 1] - zs[j]) * f
        return zs[0] if x < xs[0] else zs[-1]

    def upd(i, n):
        u = ease(i / (n - 1))
        tx = xs[3] + (xs[-2] - xs[3]) * u
        tz = line_z(tx)
        loc = (tx - 2.6, -5.6 + 0.8 * u, tz + 1.4)
        aim(c, loc, (tx + 0.8, 0, tz - 0.6))
        c.rotation_euler.y = math.radians(-8 + 14 * u)
        c.data.dof.focus_distance = (Vector((tx, 0, tz)) - Vector(loc)).length
    render('br_crash', 15, upd)


def br_coins():
    """Gold coins tumbling through frame in slow motion onto the glossy floor ('opportunity')."""
    setup()
    floor()
    backdrop()
    bokeh_lights(seed=11)
    key_lights()
    rng = random.Random(4)
    coins = []
    for k in range(26):
        loc0 = (rng.uniform(-1.6, 1.6), rng.uniform(-1.5, 2.5), rng.uniform(1.5, 8.5))
        rot0 = (rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28))
        spin = (rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(-1, 1))
        coins.append((coin_obj(loc0, rot0), loc0, rot0, spin, rng.uniform(1.6, 2.6)))
    for k in range(9):
        coin_obj((rng.uniform(-1.5, 1.5), rng.uniform(-1, 2), 0.035), (0, 0, rng.uniform(0, 6)))
    c = cam((0, -7.0, 1.4), (0, 0, 2.4), 50, 2.0, focus=7.2)

    def upd(i, n):
        t = i / 30.0
        for o, l0, r0, sp, v in coins:
            o.location = (l0[0], l0[1], max(0.04, l0[2] - v * t - 1.5 * t * t))
            o.rotation_euler = (r0[0] + sp[0] * t, r0[1] + sp[1] * t, r0[2] + sp[2] * t)
        aim(c, (0.25 * t * 6, -7.0 + 0.6 * t * 3, 1.4 + 0.3 * t), (0, 0, 2.6 - 0.8 * t))
    render('br_coins', 14, upd)


def br_dollar():
    """Heavy gold dollar sign, slow orbit with teal rim ('US Dollar strong')."""
    setup()
    floor()
    backdrop()
    bokeh_lights(seed=21, color=(0.6, 0.95, 0.8))
    key_lights()
    d = A.text_obj('$', 'Cinzel-900.ttf', 3.6, 0.45, 0.04)
    d.rotation_euler = (math.radians(90), 0, 0)
    d.location = (0, 0, 0.15)
    d.data.materials.append(A.gold(0.14))
    c = cam((0, -7, 2), (0, 0, 1.6), 45, 1.6)

    def upd(i, n):
        u = ease(i / (n - 1))
        a = math.radians(-32 + 40 * u)
        r = 7.2 - 1.2 * u
        loc = (r * math.sin(a), -r * math.cos(a), 1.0 + 0.6 * u)
        aim(c, loc, (0, 0, 1.25))
        c.data.dof.focus_distance = (Vector((0, 0, 1.5)) - Vector(loc)).length
    render('br_dollar', 15, upd)


def br_fed():
    """Federal Reserve facade from a low angle, slow push and tilt ('Fed rate hike')."""
    setup(16)
    floor(0, 0.4)
    backdrop(y=20, color=(0.02, 0.035, 0.045, 1))
    marble = A.mat('marble', (0.72, 0.68, 0.60, 1), rough=0.38)
    A.softbox((-6, -4, 9), (math.radians(40), 0, math.radians(-35)), (3, 3), 2600, (1.0, 0.85, 0.65))
    A.softbox((6, 2, 6), (math.radians(60), 0, math.radians(120)), (2, 6), 900, (0.5, 0.8, 1.0))
    for k in range(3):                                           # steps
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.6 - k * 0.45, 0.15 + k * 0.0))
        s = bpy.context.object
        s.scale = (9.0 + k * 0.6, 1.0 + k * 0.9, 0.3 * (3 - k))
        s.data.materials.append(marble)
    for k in range(6):
        x = (k - 2.5) * 1.45
        bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=5.2, vertices=24, location=(x, 0, 3.5))
        col = bpy.context.object
        A.shade_smooth(col)
        col.data.materials.append(marble)
        for zz in (0.95, 6.05):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, zz))
            cap = bpy.context.object
            cap.scale = (0.85, 0.85, 0.22)
            cap.data.materials.append(marble)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 6.6))
    ent = bpy.context.object
    ent.scale = (9.4, 1.4, 0.9)
    ent.data.materials.append(marble)
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=5.4, depth=1.4, location=(0, 0, 7.6),
                                    rotation=(math.radians(90), 0, 0))
    ped = bpy.context.object
    ped.scale = (1.0, 0.45, 1.0)
    ped.data.materials.append(marble)
    t = A.text_obj('FEDERAL  RESERVE', 'Cinzel-900.ttf', 0.48, 0.05, 0.01)
    t.rotation_euler = (math.radians(90), 0, 0)
    t.location = (0, -0.72, 6.45)
    t.data.materials.append(A.mat('ink', (0.25, 0.22, 0.18, 1), rough=0.5))
    bokeh_lights(n=18, y=(16, 19), seed=8)
    c = cam((0, -12, 0.6), (0, 0, 5), 32, 4.0)

    def upd(i, n):
        u = ease(i / (n - 1))
        loc = (-1.2 + 1.6 * u, -12.5 + 2.5 * u, 0.5 + 0.2 * u)
        aim(c, loc, (0, 0, 4.6 + 0.6 * u))
        c.data.dof.focus_distance = (Vector((0, 0, 4.5)) - Vector(loc)).length
    render('br_fed', 15, upd)


def br_barrels():
    """Oil barrels backlit by a fiery glow ('Middle East oil risk')."""
    setup()
    floor()
    backdrop(color=(0.02, 0.01, 0.005, 1))
    bokeh_lights(seed=31, color=(1.0, 0.5, 0.15), strength=40)
    key_lights(1.2)
    A.panel((0, 6, 2), (math.radians(90), 0, 0), (12, 5), 6, (1.0, 0.45, 0.12))
    steel = A.mat('steel', (0.012, 0.02, 0.03, 1), rough=0.32, metal=0.85, coat=0.3)
    for k, (x, y) in enumerate(((-1.35, 0.4), (1.3, 0.6), (0.0, -0.4))):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=2.8, vertices=64, location=(x, y, 1.4))
        b = bpy.context.object
        A.bevel(b, 0.05, 3)
        A.shade_smooth(b)
        b.data.materials.append(steel)
        for zz in (0.95, 1.85):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.96, minor_radius=0.045, location=(x, y, zz))
            r = bpy.context.object
            A.shade_smooth(r)
            r.data.materials.append(A.gold(0.2))
    c = cam((-2, -9, 1.0), (0, 0, 1.4), 32, 1.6)

    def upd(i, n):
        u = ease(i / (n - 1))
        loc = (-2.4 + 3.4 * u, -10.0 + 1.2 * u, 1.0 + 0.6 * u)
        aim(c, loc, (0, 0, 1.5))
        c.data.dof.focus_distance = (Vector((0, -0.4, 1.4)) - Vector(loc)).length
    render('br_barrels', 14, upd)


def br_barfall():
    """A gold bar slams down onto the glossy floor ('4% gira' / 'per ounce')."""
    setup()
    floor()
    backdrop()
    bokeh_lights(seed=41)
    key_lights()
    b = bar_obj((0, 0, 4), (0, 0, 0), 1.0)
    for k in range(2):
        bar_obj((-2.3 + k * 4.6, 1.8, 0.25), (0, 0, math.radians(-12 + 24 * k)), 1.0, label=False)
    c = cam((0.6, -6.2, 0.6), (0, 0, 0.9), 40, 1.6)

    def upd(i, n):
        t = i / 30.0
        tc = 0.24
        if t < tc:
            z = 4.0 - 3.75 * (t / tc) ** 2
            rx = math.radians(14 * (1 - t / tc))
        else:
            q = t - tc
            z = 0.25 + max(0.0, 0.35 * math.sin(q * 18) * math.exp(-q * 14))
            rx = math.radians(2 * math.sin(q * 30) * math.exp(-q * 12))
        b.location = (0, 0, z)
        b.rotation_euler = (rx, 0, math.radians(8))
        shake = 0.04 * math.exp(-max(0, t - tc) * 18) * (1 if t >= tc else 0)
        aim(c, (0.6 + shake * math.sin(i * 7), -6.2 + 0.6 * t, 0.6 + shake * math.cos(i * 9)), (0, 0, 0.9))
    render('br_barfall', 15, upd)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
