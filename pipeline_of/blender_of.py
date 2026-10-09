"""Organic Fostering 3D elements, rendered as transparent PNG sequences with Blender Cycles.

Usage: python3 blender_of.py <asset> [<asset> ...]
Assets: leaf_magenta leaf_orange leaf_green leaf_plum coin heart sun moon house
        text_money text_extra
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_of')))
OUT = S + '/assets'
FONT = S + '/fonts/Nunito-900.ttf'


def lin(h):
    h = h.lstrip('#')
    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


PLUM = lin('#5B174F')
MAGENTA = lin('#B7006E')
ORANGE = lin('#FF6411')
GREEN = lin('#61A80A')
IVORY = lin('#FCF8F5')
PEACH = lin('#FFD4BA')
BLUSH = lin('#F6EAF3')


def reset(res=(480, 480), samples=40):
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
    sc.cycles.max_bounces = 8
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.09, 0.06, 0.07, 1)
    bg.inputs['Strength'].default_value = 0.6
    return sc


def mat(name, color, rough=0.25, metal=0.0, coat=0.0, sss=0.0, transmission=0.0, emission=None, estr=0.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.04
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (1.0, 0.4, 0.3)
        b.inputs['Subsurface Scale'].default_value = 0.12
    if transmission:
        b.inputs['Transmission Weight'].default_value = transmission
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
    if emission:
        b.inputs['Emission Color'].default_value = emission
        b.inputs['Emission Strength'].default_value = estr
    return m


def area(loc, rot, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object
    l.data.shape = 'RECTANGLE'
    l.data.size, l.data.size_y = size
    l.data.energy = energy
    l.data.color = color
    return l


def panel(loc, rot, size, color, strength):
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


def studio(key=850, rim=1500, rim_color=(1.0, 0.35, 0.6), fill=160):
    """Warm golden key, magenta rim, soft peach fill + emissive strips for glossy highlights."""
    area((-3.2, -3.6, 4.0), (math.radians(50), 0, math.radians(-40)), (3, 3), key, (1.0, 0.9, 0.78))
    area((3.8, 2.5, 1.8), (math.radians(70), 0, math.radians(125)), (2.5, 5), rim, rim_color)
    area((3.5, -3, -1.5), (math.radians(110), 0, math.radians(45)), (4, 4), fill, (1.0, 0.85, 0.75))
    panel((-2.5, -2.5, 3.5), (math.radians(50), 0, math.radians(-40)), (2.6, 0.35), (1, 0.97, 0.92), 16)
    panel((3.0, 1.5, 0.5), (math.radians(80), 0, math.radians(120)), (0.4, 4.0), (1.0, 0.55, 0.8), 18)


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
    nframes = int(os.environ.get('NF_' + name, nframes))
    maxf = int(os.environ.get('MAX_' + name, nframes))
    for i in range(min(nframes, maxf)):
        if os.path.exists(f'{d}/{i:03d}.png') and not os.environ.get('ONE'):
            continue
        update(i, nframes)
        sc.render.filepath = f'{d}/{i:03d}.png'
        bpy.ops.render.render(write_still=True)
        print('rendered', name, i, flush=True)


def curve_obj(name, outline, extrude=0.12, bevel=0.06, res=6):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = res
    for loop in outline:
        sp = cu.splines.new('POLY')
        sp.points.add(len(loop) - 1)
        for p, q in zip(sp.points, loop):
            p.co = (q[0], q[1], 0, 1)
        sp.use_cyclic_u = True
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    return o


def to_mesh(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.shade_smooth()
    return bpy.context.object


# ---------------------------------------------------------------- assets

def leaf_outline(n=60):
    """Brand pillar leaf: a lens made of two arcs (one fuller), pointed at both ends."""
    pts = []
    for k, (bulge, sgn) in enumerate(((0.62, 1), (0.30, -1))):
        for i in range(n):
            u = i / n if k == 0 else 1 - i / n
            x = -1 + 2 * u
            y = sgn * bulge * (1 - x * x) ** 0.85 * (1 - 0.18 * x)
            pts.append((x, y))
    return [pts]


def leaf(color_name):
    col = {'magenta': MAGENTA, 'orange': ORANGE, 'green': GREEN, 'plum': PLUM}[color_name]
    reset((360, 360), samples=16)
    studio()
    camera((0, -6.4, 0.6), (0, 0, 0), lens=74)
    o = curve_obj('leaf', leaf_outline(), extrude=0.04, bevel=0.06, res=6)
    o = to_mesh(o)
    # gentle bend so it reads as a real leaf
    bd = o.modifiers.new('bend', 'SIMPLE_DEFORM')
    bd.deform_method = 'BEND'
    bd.angle = math.radians(38)
    bd.deform_axis = 'Y'
    sub = o.modifiers.new('sub', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    o.data.materials.append(mat('leaf', col, rough=0.22, coat=0.9, sss=0.15))
    o.rotation_mode = 'XYZ'

    def upd(i, n):
        ph = i / n * 2 * math.pi
        o.rotation_euler = (math.radians(90 + 25 * math.sin(ph)), math.radians(360 * i / n),
                            math.radians(-30 + 12 * math.cos(ph)))
    render_seq('leaf_' + color_name, 48, upd)


def coin():
    reset((520, 520), samples=18)
    studio(key=900, rim=1800)
    camera((0, -7.0, 0.4), (0, 0, 0), lens=78)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.25, depth=0.32, vertices=128, rotation=(math.radians(90), 0, 0))
    disc = bpy.context.object
    bv = disc.modifiers.new('bv', 'BEVEL')
    bv.width = 0.12
    bv.segments = 10
    bpy.ops.object.shade_smooth()
    disc.data.materials.append(mat('disc', MAGENTA, rough=0.18, coat=1.0, sss=0.1))
    # rings + pound sign on both faces (local coords: disc's local +Z faces the camera)
    font = bpy.data.fonts.load(FONT)
    rmat = mat('ring', PEACH, rough=0.2, coat=1.0)
    pmat = mat('pound', IVORY, rough=0.15, coat=1.0)
    for side in (1, -1):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.045, major_segments=128, minor_segments=24)
        ring = bpy.context.object
        bpy.ops.object.shade_smooth()
        ring.data.materials.append(rmat)
        ring.parent = disc
        ring.location = (0, 0, side * 0.2)
        bpy.ops.object.text_add()
        t = bpy.context.object
        t.data.body = '£'
        t.data.font = font
        t.data.size = 1.5
        t.data.align_x = 'CENTER'
        t.data.align_y = 'CENTER'
        t.data.extrude = 0.05
        t.data.bevel_depth = 0.022
        t.data.bevel_resolution = 4
        t.data.materials.append(pmat)
        t.parent = disc
        t.location = (0.02, -0.06, side * 0.2)
        t.rotation_euler = (0, 0 if side > 0 else math.pi, 0)

    def upd(i, n):
        ph = i / n * 2 * math.pi
        disc.rotation_euler = (math.radians(90 + 10 * math.sin(ph)), 0, ph)
    render_seq('coin', 48, upd)


def heart():
    sc = reset((320, 320), samples=16)
    studio()
    camera((0, -6.5, 0.3), (0, 0, 0), lens=76)
    mb = bpy.data.metaballs.new('hm')
    mb.resolution = 0.03
    mb.render_resolution = 0.015
    o = bpy.data.objects.new('heart', mb)
    sc.collection.objects.link(o)
    for sx in (-1, 1):
        el = mb.elements.new(); el.co = (sx * 0.44, 0, 0.32); el.radius = 0.62
        for k in range(1, 7):
            u = k / 7
            el = mb.elements.new()
            el.co = (sx * 0.44 * (1 - u) + sx * 0.02 * u, 0, 0.32 * (1 - u) - 0.95 * u)
            el.radius = 0.6 * (1 - u) + 0.16 * u
    el = mb.elements.new(); el.co = (0, 0, 0.0); el.radius = 0.55
    o.data.materials.append(mat('heart', ORANGE, rough=0.2, coat=1.0, sss=0.2))

    def upd(i, n):
        ph = i / n * 2 * math.pi
        o.rotation_euler = (math.radians(8 * math.sin(ph)), 0, math.radians(28 * math.sin(ph)))
        s_ = 1 + 0.05 * max(0, math.sin(ph * 2)) ** 4
        o.scale = (s_, s_ * 0.55, s_)
    render_seq('heart', 48, upd)


def sun():
    reset((320, 320), samples=16)
    studio(rim_color=(1.0, 0.6, 0.3))
    camera((0, -7, 0.3), (0, 0, 0), lens=70)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.72, segments=64, ring_count=32)
    core = bpy.context.object
    bpy.ops.object.shade_smooth()
    core.data.materials.append(mat('sun', ORANGE, rough=0.2, coat=1.0, emission=ORANGE, estr=0.6))
    rm = mat('ray', lin('#FFA24D'), rough=0.2, coat=1.0)
    for k in range(10):
        a = k / 10 * 2 * math.pi
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, segments=32, ring_count=16,
                                             location=(math.cos(a) * 1.12, 0, math.sin(a) * 1.12))
        r = bpy.context.object
        r.scale = (1.0, 0.7, 1.9)
        r.rotation_euler = (0, -a + math.pi / 2, 0)
        bpy.ops.object.shade_smooth()
        r.data.materials.append(rm)
        r.parent = core

    def upd(i, n):
        core.rotation_euler = (math.radians(12), math.radians(360 / 10 * i / n), 0)
    render_seq('sun', 48, upd)


def moon():
    reset((320, 320), samples=16)
    studio(rim_color=(0.75, 0.55, 1.0))
    camera((0, -7, 0.2), (0, 0, 0), lens=70)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.42, vertices=160, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    bpy.ops.mesh.primitive_cylinder_add(radius=0.86, depth=1.2, vertices=160, location=(0.48, 0, 0.26),
                                        rotation=(math.radians(90), 0, 0))
    cut = bpy.context.object
    cut.hide_render = True
    bo = o.modifiers.new('bool', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cut
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.12; bv.segments = 10; bv.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat('moon', lin('#FFE7C9'), rough=0.25, coat=0.9, emission=lin('#FFD49A'), estr=0.25))
    star_pts = []
    for k in range(10):
        a = k / 10 * 2 * math.pi + math.pi / 2
        r = 0.3 if k % 2 == 0 else 0.13
        star_pts.append((math.cos(a) * r, math.sin(a) * r))
    st = curve_obj('star', [star_pts], extrude=0.05, bevel=0.05, res=4)
    st = to_mesh(st)
    st.data.materials.append(mat('star', lin('#FFC56B'), rough=0.2, coat=1.0, emission=lin('#FFB040'), estr=1.5))
    st.location = (0.62, -0.1, 0.62)
    st.rotation_euler = (math.radians(90), 0, 0)
    root = bpy.data.objects.new('root', None)
    bpy.context.scene.collection.objects.link(root)
    o.parent = root
    st.parent = root
    cut.parent = root

    def upd(i, n):
        ph = i / n * 2 * math.pi
        root.rotation_euler = (math.radians(6 * math.sin(ph)), 0, math.radians(26 * math.sin(ph)))
    render_seq('moon', 48, upd)


def house():
    reset((320, 320), samples=16)
    studio()
    camera((2.2, -6.2, 1.6), (0, 0, 0.1), lens=72)
    bpy.ops.mesh.primitive_cube_add(size=1.5, location=(0, 0, -0.35))
    body = bpy.context.object
    bv = body.modifiers.new('bv', 'BEVEL'); bv.width = 0.12; bv.segments = 8
    bpy.ops.object.shade_smooth()
    body.data.materials.append(mat('body', IVORY, rough=0.3, coat=0.6, sss=0.05))
    # roof: triangular prism
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in [(-1.0, -0.95, 0.38), (1.0, -0.95, 0.38), (0, -0.95, 1.25),
                                    (-1.0, 0.95, 0.38), (1.0, 0.95, 0.38), (0, 0.95, 1.25)]]
    for f in [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]:
        bm.faces.new([v[i] for i in f])
    me = bpy.data.meshes.new('roof'); bm.to_mesh(me); bm.free()
    roof = bpy.data.objects.new('roof', me)
    bpy.context.scene.collection.objects.link(roof)
    bpy.context.view_layer.objects.active = roof
    bv = roof.modifiers.new('bv', 'BEVEL'); bv.width = 0.09; bv.segments = 6
    roof.data.materials.append(mat('roof', PLUM, rough=0.2, coat=1.0))
    roof.parent = body
    roof.location = (0, 0, 0.35)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0, -0.76, -0.62))
    door = bpy.context.object
    door.scale = (0.38, 0.06, 0.62)
    bv = door.modifiers.new('bv', 'BEVEL'); bv.width = 0.06; bv.segments = 6
    door.data.materials.append(mat('door', MAGENTA, rough=0.2, coat=1.0))
    door.parent = body
    # warm glowing window
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.48, -0.76, -0.12))
    win = bpy.context.object
    win.scale = (0.26, 0.05, 0.26)
    bv = win.modifiers.new('bv', 'BEVEL'); bv.width = 0.05; bv.segments = 4
    win.data.materials.append(mat('win', lin('#FFC27A'), rough=0.3, emission=lin('#FFB45E'), estr=3.0))
    win.parent = body
    # small heart above door
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, -0.95, 0.75))
    h = bpy.context.object
    h.data.materials.append(mat('h', ORANGE, rough=0.2, coat=1.0, emission=ORANGE, estr=1.0))
    h.parent = body

    def upd(i, n):
        ph = i / n * 2 * math.pi
        body.rotation_euler = (0, 0, math.radians(-12 + 22 * math.sin(ph)))
        body.location.z = 0.06 * math.sin(ph * 2)
    render_seq('house', 48, upd)


def text3d(name, body, color, res, size=1.0, frames=48, extrude=0.14, rim_color=(1.0, 0.35, 0.6), mode='sway'):
    reset(res, samples=16)
    studio(key=900, rim=2000, rim_color=rim_color, fill=200)
    bpy.ops.object.text_add(location=(0, 0, 0))
    t = bpy.context.object
    t.data.body = body
    t.data.font = bpy.data.fonts.load(FONT)
    t.data.size = size
    t.data.align_x = 'CENTER'
    t.data.align_y = 'CENTER'
    t.data.extrude = extrude
    t.data.bevel_depth = 0.025
    t.data.bevel_resolution = 5
    t.data.space_character = 0.96
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(mat('face', color, rough=0.16, coat=1.0, sss=0.08))
    w = res[0] / res[1]
    camera((0, -10.0, 0.0), (0, 0, 0), lens=70)
    # frame the text width
    bpy.context.view_layer.update()
    dims = t.dimensions
    cam = bpy.context.scene.camera
    cam.data.sensor_fit = 'HORIZONTAL'
    cam.location.y = -max(dims.x * 1.18, dims.y * 1.2 * w) * cam.data.lens / cam.data.sensor_width

    def upd(i, n):
        ph = i / n * 2 * math.pi
        if mode == 'sway':
            t.rotation_euler = (math.radians(90 + 7 * math.sin(ph)), 0, math.radians(14 * math.sin(ph + 0.6)))
        else:  # spin-in: edge-on -> face-on with overshoot (0..60%) then idle sway
            u = i / max(n - 1, 1) if n > 1 else 1.0
            e = 1 - (1 - min(u / 0.6, 1)) ** 3
            ang = (1 - e) * 88 + 5 * math.sin(u * math.pi * 2) * e
            t.rotation_euler = (math.radians(90 + (1 - e) * 20), 0, math.radians(ang))
    render_seq(name, frames, upd)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('leaf_'):
            leaf(a[5:])
        elif a == 'text_money':
            text3d('text_money', '£447.60', IVORY, (1400, 460), frames=48, mode='spin')
        elif a == 'text_extra':
            text3d('text_extra', 'extraordinary', IVORY, (1500, 400), frames=48, rim_color=(1.0, 0.25, 0.55))
        else:
            globals()[a]()
