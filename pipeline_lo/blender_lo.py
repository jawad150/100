"""3D scenes for Organic Fostering "Leave the Light On" (Blender Cycles, stylised clay-realism).

Usage: python3 blender_lo.py <scene> [...]
Scenes:
  street_hook  drone push down a rainy row of red-brick terraced houses at night; one porch light clicks on
  street_rise  from the glowing porch the camera rises into the rainy night sky (CTA)
  wellies      tiny pink wellies beside big slippers on a doormat by a warm radiator (payoff)
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo'))
OUT = S + '/assets'
FPS = 24


def lin(h):
    h = h.lstrip('#')

    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


def reset(res, samples=16, transparent=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.012, 0.02, 0.05, 1)
    bg.inputs['Strength'].default_value = 1.0
    return sc


def mat(name, col, rough=0.5, metal=0.0, emit=None, estr=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if emit is not None:
        b.inputs['Emission Color'].default_value = emit
        b.inputs['Emission Strength'].default_value = estr
    return m


def box(size, loc, m, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL')
        bv.width = bevel
        bv.segments = 3
    o.data.materials.append(m)
    return o


def prism(w, d, h, loc, m):
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (0, -d / 2, h),
                                    (-w / 2, d / 2, 0), (w / 2, d / 2, 0), (0, d / 2, h)]]
    for f in [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]:
        bm.faces.new([v[i] for i in f])
    me = bpy.data.meshes.new('pr')
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('pr', me)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.data.materials.append(m)
    return o


def camera(lens=32):
    bpy.ops.object.camera_add()
    c = bpy.context.object
    c.data.lens = lens
    c.data.dof.use_dof = True
    c.data.dof.aperture_fstop = 4.0
    bpy.context.scene.camera = c
    return c


def look(c, loc, target):
    c.location = loc
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.dof.focus_distance = d.length


def render_seq(name, n, update, start=0):
    d = f'{OUT}/{name}'
    os.makedirs(d, exist_ok=True)
    sc = bpy.context.scene
    n = int(os.environ.get('NF_' + name, n))
    for i in range(n):
        if os.path.exists(f'{d}/{i:03d}.png') and not os.environ.get('ONE'):
            continue
        update(i, n)
        sc.render.filepath = f'{d}/{i:03d}.png'
        bpy.ops.render.render(write_still=True)
        print('rendered', name, i, flush=True)
        if os.environ.get('ONE'):
            break


# ------------------------------------------------------------------ the street
BRICKS = ['#7E3A28', '#8B4330', '#73351F', '#86402C', '#7A3B2B', '#90472F']
HOUSE_W = 4.2
TARGET = 3                      # index of the house whose porch light clicks on


def street(porch_on_frame=None):
    sc = bpy.context.scene
    road = mat('road', lin('#101318'), rough=0.12, coat=0.3)
    box((80, 30, 0.1), (0, -9, -0.05), road)
    pave = mat('pave', lin('#3A3D44'), rough=0.35)
    box((80, 3.0, 0.24), (0, 1.5, 0.12), pave)
    box((80, 0.3, 0.3), (0, -0.05, 0.15), mat('curb', lin('#55585F'), rough=0.4))
    slate = mat('slate', lin('#1E2229'), rough=0.45)
    mort = mat('door', lin('#14161B'), rough=0.3, coat=0.6)
    glow = mat('win_on', lin('#FFB761'), rough=0.4, emit=lin('#FF9A3C'), estr=7.0)
    dark = mat('win_off', lin('#0E1A2C'), rough=0.08, coat=0.8)
    sill = mat('sill', lin('#D9D2C4'), rough=0.5)
    lit = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
    porch = None
    for i in range(-5, 7):
        x = i * HOUSE_W
        brick = mat(f'b{i}', lin(BRICKS[i % len(BRICKS)]), rough=0.85)
        box((HOUSE_W - 0.08, 6, 7.0), (x, 6.0, 3.5), brick)
        prism(HOUSE_W, 6.2, 2.4, (x, 6.0, 7.0), slate)
        box((0.6, 0.8, 1.4), (x + 1.2, 5.0, 8.6), brick)
        box((1.2, 0.12, 2.3), (x - 1.0, 2.98, 1.4), mort, bevel=0.03)
        box((1.5, 0.3, 0.6), (x - 1.0, 2.9, 2.85), sill)
        for (wx, wz, idx) in [(0.9, 1.6, 0), (-0.9, 4.6, 1), (0.9, 4.6, 2)]:
            on = lit[(i + idx) % len(lit)] and not (i == TARGET and idx == 0)
            box((1.2, 0.1, 1.6), (x + wx, 2.98, wz), glow if on else dark)
            box((1.4, 0.25, 0.14), (x + wx, 2.9, wz - 0.9), sill)
        if i == TARGET:
            lamp_m = mat('porch', lin('#FFC27A'), rough=0.3, emit=lin('#FF9A3C'), estr=0.0)
            box((0.26, 0.26, 0.4), (x - 0.15, 2.85, 2.3), lamp_m, bevel=0.04)
            bpy.ops.object.light_add(type='POINT', location=(x - 0.15, 2.5, 2.3))
            porch = bpy.context.object
            porch.data.color = (1.0, 0.62, 0.3)
            porch.data.energy = 0.0
            porch.data.shadow_soft_size = 0.2
            porch.data['lamp_m'] = lamp_m.name
    # street lamps (cool) along the far kerb
    for i in range(-4, 6, 2):
        x = i * HOUSE_W + 1.0
        box((0.12, 0.12, 4.6), (x, -0.6, 2.3), mat(f'pole{i}', lin('#2A2D33'), rough=0.4))
        bpy.ops.object.light_add(type='POINT', location=(x, -0.9, 4.5))
        l = bpy.context.object
        l.data.color = (0.75, 0.82, 1.0)
        l.data.energy = 120
        l.data.shadow_soft_size = 0.4
    # moonlight + sky fill
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55), 0, math.radians(-30)))
    s = bpy.context.object
    s.data.energy = 0.25
    s.data.color = (0.55, 0.65, 1.0)
    return porch


def set_porch(porch, k):
    porch.data.energy = 140 * k
    m = bpy.data.materials[porch.data['lamp_m']]
    m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 40 * k


def street_hook():
    reset((576, 1024), samples=12)
    porch = street()
    cam = camera(lens=30)
    tx = TARGET * HOUSE_W - 0.4
    on_f = int(2.0 * FPS)            # click at 2.0 s

    def upd(i, n):
        k = i / (n - 1)
        e = 1 - (1 - k) ** 2
        loc = (tx - 6 + 5.0 * e, -16 + 8.5 * e, 12 - 8.2 * e)
        tgt = (tx - 0.6, 3.0, 2.2 + 1.2 * (1 - e))
        look(cam, loc, tgt)
        kk = 0.0 if i < on_f else min(1.0, (i - on_f) / 3.0)
        set_porch(porch, kk)
    render_seq('street_hook', 3 * FPS, upd)


def street_rise():
    reset((576, 1024), samples=12)
    porch = street()
    set_porch(porch, 1.0)
    cam = camera(lens=30)
    tx = TARGET * HOUSE_W - 0.4

    def upd(i, n):
        k = i / (n - 1)
        e = k * k * (3 - 2 * k)
        loc = (tx - 0.5, -6 + 1.0 * e, 3.0 + 16 * e)
        tgt = (tx, 3.0 + 2 * e, 2.3 - 2.3 * e)
        look(cam, loc, tgt)
    render_seq('street_rise', 3 * FPS, upd)


def wellies():
    reset((720, 900), samples=24)
    sc = bpy.context.scene
    floor = mat('floor', lin('#3E2A1E'), rough=0.5)
    box((10, 10, 0.1), (0, 0, -0.05), floor)
    box((10, 0.2, 6), (0, 2.0, 3), mat('wall', lin('#E8D9C6'), rough=0.9))
    mat_m = mat('mat', lin('#A0703F'), rough=0.95)
    box((3.4, 2.0, 0.06), (0, 0.1, 0.03), mat_m, bevel=0.05)
    rad = mat('rad', lin('#F2EEE8'), rough=0.3, coat=0.5)
    for j in range(12):
        box((0.18, 0.22, 1.6), (-1.65 + j * 0.3, 1.75, 1.3), rad, bevel=0.06)
    box((3.6, 0.2, 0.12), (0, 1.75, 0.45), rad)
    box((3.6, 0.2, 0.12), (0, 1.75, 2.15), rad)
    pink = mat('pink', lin('#E0235F'), rough=0.18, coat=1.0)
    for sx in (-1.15, -0.55):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.75, location=(sx, 0.35, 0.45), vertices=48)
        o = bpy.context.object
        o.scale = (1, 0.9, 1)
        bv = o.modifiers.new('bv', 'BEVEL')
        bv.width = 0.05
        bv.segments = 4
        bpy.ops.object.shade_smooth()
        o.data.materials.append(pink)
        box((0.42, 0.62, 0.22), (sx, 0.18, 0.11), pink, bevel=0.1)
        box((0.44, 0.64, 0.05), (sx, 0.18, 0.025), mat('sole%d' % int(sx * 10), lin('#3A1A24'), rough=0.6), bevel=0.02)
    sl = mat('slip', lin('#CDB79E'), rough=0.95)
    for sx in (0.55, 1.15):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(sx, 0.05, 0.14), segments=48, ring_count=24)
        o = bpy.context.object
        o.scale = (0.5, 1.05, 0.3)
        bpy.ops.object.shade_smooth()
        o.data.materials.append(sl)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(sx, -0.12, 0.24), segments=32, ring_count=16)
        f = bpy.context.object
        f.scale = (0.75, 1.0, 0.4)
        bpy.ops.object.shade_smooth()
        f.data.materials.append(mat('fur%d' % int(sx * 10), lin('#EFE4D6'), rough=1.0))
    # droplets on the wellies
    drop = mat('drop', lin('#F07AA0'), rough=0.02, coat=1.0)
    import random
    random.seed(4)
    for _ in range(14):
        sx = random.choice((-1.15, -0.55)) + random.uniform(-0.12, 0.12)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.006, 0.014), location=(sx, 0.13, random.uniform(0.2, 0.8)))
        bpy.context.object.data.materials.append(drop)
    bpy.ops.object.light_add(type='AREA', location=(-2.5, -2.5, 3.5), rotation=(math.radians(55), 0, math.radians(-40)))
    k = bpy.context.object
    k.data.size = 3
    k.data.energy = 400
    k.data.color = (1.0, 0.78, 0.55)
    bpy.ops.object.light_add(type='POINT', location=(0, 1.2, 1.2))
    p = bpy.context.object
    p.data.energy = 60
    p.data.color = (1.0, 0.6, 0.35)
    bpy.ops.object.light_add(type='AREA', location=(2.5, -1.5, 1.0), rotation=(math.radians(80), 0, math.radians(60)))
    r = bpy.context.object
    r.data.energy = 120
    r.data.color = (0.55, 0.65, 1.0)
    cam = camera(lens=38)
    cam.data.dof.aperture_fstop = 2.4

    def upd(i, n):
        k = i / (n - 1)
        look(cam, (-0.35 + 0.7 * k, -4.9 + 0.35 * k, 0.95 - 0.1 * k), (0.0, 0.3, 0.42))
    render_seq('wellies', int(2.5 * FPS), upd)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
