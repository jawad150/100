"""Render 3D sprite assets (transparent PNG sequences) for the reel.

Usage: python3 blender_assets.py <asset_name> [<asset_name> ...]
"""
import bpy, bmesh, math, os, sys, json, random
from mathutils import Vector

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
OUT = S + '/assets'

ORANGE = (1.0, 0.22, 0.01, 1)       # linear-ish vivid orange
ORANGE_HOT = (1.0, 0.42, 0.05, 1)
BLACK = (0.012, 0.011, 0.010, 1)
CREAM = (0.80, 0.74, 0.66, 1)
LIME = (0.63, 0.99, 0.009, 1)


def reset(res=(512, 512), samples=48):
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
    sc.cycles.transmission_bounces = 6
    # world: dark studio with faint warm tint (only affects reflections/ambient)
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.02, 0.012, 0.008, 1)
    bg.inputs['Strength'].default_value = 1.0
    return sc


def mat(name, color, rough=0.25, metal=0.0, coat=0.0, sss=0.0, transmission=0.0, emission=None, estr=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.05
    b.inputs['IOR'].default_value = ior
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.15)
        b.inputs['Subsurface Scale'].default_value = 0.15
    if transmission:
        b.inputs['Transmission Weight'].default_value = transmission
    if emission:
        b.inputs['Emission Color'].default_value = emission
        b.inputs['Emission Strength'].default_value = estr
    return m


def softbox(loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object
    l.data.shape = 'RECTANGLE'
    l.data.size = size[0]
    l.data.size_y = size[1]
    l.data.energy = energy
    l.data.color = color
    return l


def emissive_panel(loc, rot, size, color, strength):
    """Visible-only-in-reflections light panel (gives the glossy streak highlights)."""
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


def studio(key=900, rim=1400, rim_color=(1.0, 0.35, 0.05), fill=120):
    softbox((-3.2, -3.5, 4.0), (math.radians(50), 0, math.radians(-40)), (3, 3), key)
    softbox((3.8, 2.5, 1.8), (math.radians(70), 0, math.radians(125)), (2.5, 5), rim, rim_color)
    softbox((3.5, -3, -1.5), (math.radians(110), 0, math.radians(45)), (4, 4), fill, (1.0, 0.8, 0.7))
    emissive_panel((-2.5, -2.5, 3.5), (math.radians(50), 0, math.radians(-40)), (2.5, 0.35), (1, 1, 1), 18)
    emissive_panel((3.0, 1.5, 0.5), (math.radians(80), 0, math.radians(120)), (0.4, 4.0), (1.0, 0.45, 0.1), 25)


def camera(loc=(0, -6, 0), target=(0, 0, 0), lens=60):
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
    if os.environ.get('ONE'):
        nframes = 1
    for i in range(nframes):
        update(i, nframes)
        sc.render.filepath = f'{d}/{i:03d}.png'
        bpy.ops.render.render(write_still=True)
        print('rendered', name, i, flush=True)


def smooth(obj, level=2):
    m = obj.modifiers.new('sub', 'SUBSURF')
    m.levels = level
    m.render_levels = level
    bpy.ops.object.shade_smooth()


def add_eyes(parent, spacing=0.26, z=0.12, y=-0.93, size=0.085, color=BLACK, shine=True):
    eyes = []
    em = mat('eye', color, rough=0.08, coat=1.0)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(sx * spacing, y, z), segments=32, ring_count=16)
        e = bpy.context.object
        e.scale = (size * 0.8, size * 0.5, size * 1.25)
        e.data.materials.append(em)
        bpy.ops.object.shade_smooth()
        e.parent = parent
        eyes.append(e)
    return eyes


# ---------------------------------------------------------------- assets

def blob(kind):
    sc = reset((400, 400), samples=26)
    studio()
    camera((0, -6.2, 0.5), (0, 0, 0.05), lens=78)
    if kind == 'drop':      # orange drop-shaped blob
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=64, ring_count=32)
        o = bpy.context.object
        bm = bmesh.new(); bm.from_mesh(o.data)
        for v in bm.verts:
            t = (v.co.z + 1) / 2
            k = 1.0 - 0.45 * t ** 1.6
            v.co.x *= k; v.co.y *= k
            v.co.z *= 1.08
        bm.to_mesh(o.data); bm.free()
        o.data.materials.append(mat('b', ORANGE, rough=0.28, coat=0.6, sss=0.25))
        eyes = add_eyes(o, spacing=0.27, z=-0.08, y=-0.88, size=0.12)
    elif kind == 'bear':    # glossy black blob with ears + orange eyes
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=64, ring_count=32)
        o = bpy.context.object
        o.scale = (1.05, 0.95, 0.92)
        bpy.ops.object.transform_apply(scale=True)
        blk = mat('b', BLACK, rough=0.18, coat=1.0)
        o.data.materials.append(blk)
        for sx in (-1, 1):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, location=(sx * 0.62, 0.05, 0.78), segments=32, ring_count=16)
            ear = bpy.context.object
            ear.data.materials.append(blk)
            bpy.ops.object.shade_smooth()
            ear.parent = o
        eyes = add_eyes(o, spacing=0.32, z=0.05, y=-0.84, size=0.13,
                        color=(1.0, 0.3, 0.02, 1))
        for e in eyes:
            e.data.materials[0] = mat('eo', ORANGE_HOT, rough=0.2, emission=(1, 0.35, 0.03, 1), estr=4.0)
    elif kind == 'flower':  # orange flower blob (metaballs)
        mb = bpy.data.metaballs.new('mb')
        mb.resolution = 0.04; mb.render_resolution = 0.02
        o = bpy.data.objects.new('flower', mb)
        sc.collection.objects.link(o)
        el = mb.elements.new(); el.co = (0, 0, 0); el.radius = 0.9
        for i in range(5):
            a = i / 5 * 2 * math.pi + math.pi / 2
            el = mb.elements.new(); el.co = (math.cos(a) * 0.62, 0, math.sin(a) * 0.62); el.radius = 0.62
        o.data.materials.append(mat('b', (1.0, 0.3, 0.02, 1), rough=0.3, coat=0.5, sss=0.2))
        eyes = add_eyes(o, spacing=0.25, z=0.02, y=-0.74, size=0.115)
    elif kind == 'cube':    # cream rounded cube
        bpy.ops.mesh.primitive_cube_add(size=1.6)
        o = bpy.context.object
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.35; bv.segments = 8
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat('b', CREAM, rough=0.35, coat=0.3))
        eyes = add_eyes(o, spacing=0.26, z=0.05, y=-0.84, size=0.12)
    if kind != 'flower':
        smooth(o, 1 if kind == 'cube' else 1)

    def upd(i, n):
        ph = i / n * 2 * math.pi
        sq = 1 + 0.06 * math.sin(ph * 2)
        o.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
        o.rotation_euler = (math.radians(4 * math.sin(ph)), 0, math.radians(18 * math.sin(ph)))
        o.location.z = 0.08 * math.sin(ph)
        blink = 1.0
        if 0.62 < i / n < 0.70:
            blink = 0.12
        for e in eyes:
            e.scale.z = e.scale.x * 1.55 * blink
    render_seq('blob_' + kind, 24, upd)


def spinner(kind):
    sc = reset((460, 460), samples=30)
    studio(key=800, rim=1800)
    camera((0, -7, 1.0), (0, 0, 0), lens=68)
    if kind == 'torus':
        bpy.ops.mesh.primitive_torus_add(major_radius=1.15, minor_radius=0.42, major_segments=96, minor_segments=48)
        o = bpy.context.object
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat('t', ORANGE, rough=0.16, coat=1.0, metal=0.15))
        base = (math.radians(65), math.radians(20), 0)
    elif kind == 'capsule':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, segments=64, ring_count=32)
        o = bpy.context.object
        bm = bmesh.new(); bm.from_mesh(o.data)
        for v in bm.verts:
            v.co.z += 0.75 if v.co.z > 0 else -0.75
        bm.to_mesh(o.data); bm.free()
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat('c', (1.0, 0.45, 0.12, 1), rough=0.05, transmission=1.0, ior=1.5))
        # inner glowing core
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, segments=32, ring_count=16)
        core = bpy.context.object
        core.data.materials.append(mat('core', ORANGE, emission=(1, 0.3, 0.02, 1), estr=12))
        core.parent = o
        base = (math.radians(35), math.radians(-30), 0)
    elif kind == 'rcube':
        bpy.ops.mesh.primitive_cube_add(size=1.7)
        o = bpy.context.object
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.28; bv.segments = 6
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat('k', BLACK, rough=0.12, coat=1.0, metal=0.3))
        base = (math.radians(30), math.radians(40), 0)
    elif kind == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, segments=96, ring_count=48)
        o = bpy.context.object
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat('s', (0.02, 0.02, 0.02, 1), rough=0.06, metal=1.0))
        base = (0, 0, 0)
    elif kind == 'ring':
        bpy.ops.mesh.primitive_torus_add(major_radius=1.3, minor_radius=0.09, major_segments=128, minor_segments=24)
        o = bpy.context.object
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat('r', (0.9, 0.9, 0.9, 1), rough=0.08, metal=1.0))
        base = (math.radians(70), 0, 0)

    n = 1 if kind == 'sphere' else 32

    def upd(i, nn):
        ph = i / nn * 2 * math.pi
        o.rotation_euler = (base[0] + 0.25 * math.sin(ph), base[1] + ph if kind in ('capsule', 'rcube') else base[1],
                            base[2] + (ph if kind in ('torus', 'ring') else 0))
    render_seq(kind, n, upd)


def logo3d():
    sc = reset((1400, 520), samples=56)
    studio(key=700, rim=2400, rim_color=(1.0, 0.38, 0.05), fill=80)
    data = json.load(open(S + '/logo_contours.json'))
    cu = bpy.data.curves.new('logo', 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = 0.06
    cu.bevel_depth = 0.012
    cu.bevel_resolution = 4
    for c in data['contours']:
        sp = cu.splines.new('POLY')
        pts = c['pts']
        sp.points.add(len(pts) - 1)
        for p, q in zip(sp.points, pts):
            p.co = (q[0], q[1], 0, 1)
        sp.use_cyclic_u = True
    o = bpy.data.objects.new('logo', cu)
    sc.collection.objects.link(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat('lime', LIME, rough=0.22, coat=1.0, sss=0.1))
    camera((0, -10.8, 0.0), (0, 0, 0), lens=70)

    def upd(i, n):
        t = i / max(n - 1, 1)
        # rotate in from edge-on to face-on with an overshoot settle, then idle sway
        e = 1 - (1 - min(t / 0.55, 1)) ** 3
        ang = (1 - e) * 80 + 6 * math.sin(t * math.pi * 1.5) * (0.4 + 0.6 * e)
        o.rotation_euler = (math.radians(90 + (1 - e) * 25), 0, math.radians(ang))
    render_seq('logo3d', 60, upd)


def cursor3d():
    sc = reset((300, 300), samples=48)
    studio(key=700, rim=1500)
    camera((0, 0, 6), (0, 0, 0), lens=60)
    pts = [(0, 0), (0, -1.0), (0.26, -0.76), (0.46, -1.16), (0.62, -1.08), (0.42, -0.69), (0.75, -0.69)]
    cu = bpy.data.curves.new('cur', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = 0.07; cu.bevel_depth = 0.03; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0] - 0.35, q[1] + 0.55, 0, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new('cursor', cu); sc.collection.objects.link(o)
    o.data.materials.append(mat('w', (0.95, 0.95, 0.95, 1), rough=0.15, coat=1.0))
    o.rotation_euler = (math.radians(-18), math.radians(22), 0)
    render_seq('cursor3d', 1, lambda i, n: None)


def arrow3d():
    sc = reset((360, 360), samples=48)
    studio(key=800, rim=1800)
    camera((0, -6, 0.8), (0, 0, 0), lens=55)
    pts = [(-0.28, 0.9), (0.28, 0.9), (0.28, 0.0), (0.7, 0.0), (0, -0.85), (-0.7, 0.0), (-0.28, 0.0)]
    cu = bpy.data.curves.new('ar', 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = 0.18; cu.bevel_depth = 0.08; cu.bevel_resolution = 6
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0], q[1], 0, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new('arrow', cu); sc.collection.objects.link(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat('a', ORANGE, rough=0.18, coat=1.0))

    def upd(i, n):
        o.rotation_euler = (math.radians(90), 0, math.radians(35 * math.sin(i / n * 2 * math.pi)))
    render_seq('arrow3d', 16, upd)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('blob_'):
            blob(a[5:])
        elif a in ('torus', 'capsule', 'rcube', 'sphere', 'ring'):
            spinner(a)
        elif a == 'logo3d':
            logo3d()
        elif a == 'cursor3d':
            cursor3d()
        elif a == 'arrow3d':
            arrow3d()
