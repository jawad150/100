"""3D touchpoints for "Same Business?" (soft rounded 3D with soft contact shadows, transparent PNGs).

Each touchpoint has a BEFORE and an AFTER state rendered from the same camera, so the snap/morph lines up.
Usage: python3 blender_sb.py <name> [...]   names: van sign card web insta invoice (each renders _before and _after),
       mark swatches aa
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
TEX = f'{ROOT}/workspace_hulk/sb_tex'
OUT = f'{ROOT}/workspace_hulk/sb_3d'
FONT = f'{ROOT}/workspace_hulk/fonts/Headline-900.ttf'


def lin(h):
    h = h.lstrip('#')

    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


NAVY, AMBER, OFF, SLATE = '#1E2A4A', '#F5A524', '#F3F5F0', '#606C80'


def reset(res=(900, 900), samples=64):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples
    sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#F0F2EE')
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.75
    for loc, rot, size, e in (((-4, -6, 7), (50, 0, -30), 6, 900), ((5, -3, 3), (70, 0, 55), 4, 300), ((0, 5, 4), (-60, 0, 180), 5, 250)):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=tuple(math.radians(a) for a in rot))
        l = bpy.context.object; l.data.size = size; l.data.energy = e
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.context.object.is_shadow_catcher = True
    return sc


def mat(name, col, rough=0.45, coat=0.25, metal=0.0, tex=None, alpha_tex=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin(col) if isinstance(col, str) else col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Metallic'].default_value = metal
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(tex); t.interpolation = 'Cubic'
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if alpha_tex:
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    return m


def rbox(size, loc, m, bevel=0.06, rot=(0, 0, 0), seg=6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def plane(w, h, loc, m, rot=(90, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object
    o.scale = (w, h, 1)
    o.data.materials.append(m)
    return o


def cyl(r, d, loc, m, rot=(0, 0, 0), v=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=tuple(math.radians(a) for a in rot), vertices=v)
    o = bpy.context.object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = min(r, d) * 0.15; bv.segments = 3
    return o


def group(objs, pivot=(0, 0, 0)):
    bpy.ops.object.empty_add(location=pivot)
    e = bpy.context.object
    bpy.context.view_layer.update()
    inv = e.matrix_world.inverted()
    for o in objs:
        o.parent = e
        o.matrix_parent_inverse = inv
    return e


def shot(name, loc, target, lens=50):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    os.makedirs(OUT, exist_ok=True)
    sc.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


# ------------------------------------------------------------------ touchpoints
def van(state):
    reset((1000, 760))
    body_col = '#D6403A' if state == 'before' else NAVY
    body = mat('body', body_col, rough=0.3, coat=0.6)
    glass = mat('glass', '#2A3340', rough=0.1, coat=0.8)
    tyre = mat('tyre', '#202226', rough=0.7, coat=0.0)
    hub = mat('hub', '#C9CED6', rough=0.3, metal=0.6)
    objs = [rbox((3.2, 1.5, 1.45), (0.2, 0, 1.12), body, 0.18)]
    objs.append(rbox((1.0, 1.46, 0.95), (-1.75, 0, 0.88), body, 0.22))
    objs.append(rbox((0.08, 1.2, 0.5), (-2.2, 0, 1.25), glass, 0.06, rot=(0, math.radians(-28), 0)))
    objs.append(rbox((0.62, 0.02, 0.42), (-1.62, -0.735, 1.18), glass, 0.04))
    for x in (-1.4, 1.1):
        objs.append(cyl(0.38, 0.32, (x, -0.62, 0.38), tyre, rot=(90, 0, 0)))
        objs.append(cyl(0.2, 0.34, (x, -0.63, 0.38), hub, rot=(90, 0, 0)))
    objs.append(rbox((0.2, 0.3, 0.12), (-2.25, -0.55, 0.7), mat('lamp', '#FFF3C4', rough=0.1), 0.04))
    deco = mat('decal', '#FFFFFF', rough=0.4, tex=f'{TEX}/van_{state}.png', alpha_tex=True)
    objs.append(plane(2.9, 2.9 * 600 / 1600, (0.25, -0.757, 1.2), deco))
    g = group(objs)
    g.rotation_euler = (0, 0, math.radians(-14))
    shot(f'van_{state}', (2.4, -8.2, 2.6), (-0.1, 0, 0.95), lens=50)


def sign(state):
    reset((1000, 620))
    m = mat('panel', '#2E8B3E' if state == 'before' else NAVY, rough=0.35, coat=0.5)
    objs = [rbox((3.0, 0.16, 1.1), (0, 0, 1.6), m, 0.06)]
    objs.append(plane(2.86, 2.86 * 500 / 1400, (0, -0.085, 1.6), mat('face', '#FFFFFF', rough=0.45, tex=f'{TEX}/sign_{state}.png')))
    br = mat('br', '#2B2D31', rough=0.4, metal=0.6)
    for x in (-1.1, 1.1):
        objs.append(rbox((0.06, 0.6, 0.06), (x, 0.32, 2.3), br, 0.02))
        objs.append(rbox((0.06, 0.06, 0.6), (x, 0.0, 2.02), br, 0.02))
    g = group(objs, (0, 0, 1.6))
    g.rotation_euler = (0, 0, math.radians(-16))
    shot(f'sign_{state}', (1.8, -7.5, 2.2), (0, 0, 1.65), lens=55)


def card(state):
    reset((900, 700))
    base = '#6B3FA0' if state == 'before' else NAVY
    m = mat('card', base, rough=0.35, coat=0.4)
    objs = [rbox((1.75, 1.0, 0.025), (0.08, 0.06, 0.03), mat('card2', base, rough=0.4), 0.015)]
    objs[0].rotation_euler = (0, 0, math.radians(9))
    top = rbox((1.75, 1.0, 0.025), (0, 0, 0.07), m, 0.015)
    face = plane(1.73, 0.988, (0, 0, 0.0835), mat('face', '#FFFFFF', rough=0.35, tex=f'{TEX}/card_{state}.png'), rot=(0, 0, 0))
    g = group([top, face], (0, 0, 0.07))
    g.rotation_euler = (0, 0, math.radians(-8))
    shot(f'card_{state}', (0.5, -3.1, 3.0), (0, 0, 0), lens=50)


def web(state):
    reset((1000, 820))
    alu = mat('alu', '#C8CCD2', rough=0.3, metal=0.7)
    dark = mat('bez', '#1C1E22', rough=0.3)
    objs = [rbox((2.8, 1.9, 0.08), (0, 0, 0.04), alu, 0.05)]
    objs.append(rbox((2.5, 1.0, 0.01), (0, -0.25, 0.085), mat('keys', '#9EA3AA', rough=0.5), 0.01))
    lid = rbox((2.8, 0.06, 1.85), (0, 0.95, 0.95), dark, 0.05)
    scr = plane(2.62, 1.64, (0, 0.915, 0.96), mat('scr', '#FFFFFF', rough=0.25, tex=f'{TEX}/web_{state}.png'))
    lg = group([lid, scr], (0, 0.95, 0.04))
    lg.rotation_euler = (math.radians(-12), 0, 0)
    g = group(objs + [lg])
    g.rotation_euler = (0, 0, math.radians(-18))
    shot(f'web_{state}', (1.6, -6.0, 2.6), (0, 0.4, 0.75), lens=50)


def insta(state):
    reset((700, 1000))
    body = mat('ph', '#16181C', rough=0.25, coat=0.8)
    objs = [rbox((1.0, 0.1, 2.02), (0, 0, 1.2), body, 0.12)]
    objs.append(plane(0.9, 1.8, (0, -0.052, 1.2), mat('scr', '#FFFFFF', rough=0.2, tex=f'{TEX}/insta_{state}.png')))
    g = group(objs, (0, 0, 1.2))
    g.rotation_euler = (math.radians(-6), 0, math.radians(-14))
    shot(f'insta_{state}', (0.8, -5.6, 1.6), (0, 0, 1.2), lens=50)


def invoice(state):
    reset((760, 1000))
    me = bpy.data.meshes.new('pap'); bm = bmesh.new()
    nx, ny = 20, 26
    W_, H_ = 1.5, 2.0
    vs = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            curl = (max(0, u - 0.75) ** 2) * 0.6 * (1 - v) + 0.02 * math.sin(u * 3)
            row.append(bm.verts.new(((u - 0.5) * W_, -curl, (v - 0.5) * H_)))
        vs.append(row)
    uvl = bm.loops.layers.uv.new()
    for j in range(ny):
        for i in range(nx):
            f = bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uvl].uv = (a / nx, b / ny)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('pap', me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat('paper', '#FFFFFF', rough=0.7, coat=0.0, tex=f'{TEX}/invoice_{state}.png'))
    for p in me.polygons:
        p.use_smooth = True
    sol = o.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.008
    o.location = (0, 0, 1.15)
    o.rotation_euler = (math.radians(-8), math.radians(5), math.radians(-10))
    shot(f'invoice_{state}', (0.6, -5.2, 1.5), (0, 0, 1.12), lens=50)


# ------------------------------------------------------------------ the system pieces
def mark():
    reset((800, 800))
    am = mat('amber', AMBER, rough=0.25, coat=0.8)
    cd = bpy.data.curves.new('c', 'CURVE'); cd.dimensions = '3D'
    sp = cd.splines.new('POLY'); n = 64
    sp.points.add(n - 1)
    for i in range(n):
        a = math.radians(40 + 280 * i / (n - 1))
        sp.points[i].co = (math.cos(a) * 1.0, 0, math.sin(a) * 1.0, 1)
    cd.bevel_depth = 0.22; cd.bevel_resolution = 8; cd.use_fill_caps = True
    o = bpy.data.objects.new('pipe', cd); bpy.context.scene.collection.objects.link(o); o.data.materials.append(am)
    for a in (40, 320):
        x, z = math.cos(math.radians(a)), math.sin(math.radians(a))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(x, 0, z), segments=48, ring_count=24)
        bpy.context.object.data.materials.append(am); bpy.ops.object.shade_smooth()
    nv = mat('navy', NAVY, rough=0.2, coat=0.9)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0.55, 0, -0.12), segments=48, ring_count=24)
    bpy.context.object.data.materials.append(nv); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cone_add(radius1=0.285, radius2=0.0, depth=0.55, location=(0.55, 0, 0.22), vertices=48)
    bpy.context.object.data.materials.append(nv); bpy.ops.object.shade_smooth()
    for ob in list(bpy.data.objects):
        if ob.type in ('MESH', 'CURVE') and ob.name not in ('Plane',) and not ob.is_shadow_catcher:
            ob.location.z += 1.4
    shot('mark', (0.6, -6.0, 1.9), (0, 0, 1.4), lens=50)


def swatches():
    reset((900, 700))
    for i, col in enumerate((NAVY, AMBER, OFF, SLATE)):
        o = rbox((0.75, 1.15, 0.05), (-0.9 + i * 0.6, 0.0, 0.05 + i * 0.03), mat(f's{i}', col, rough=0.35, coat=0.5), 0.04)
        o.rotation_euler = (0, 0, math.radians(-14 + i * 9))
    shot('swatches', (0.3, -3.2, 3.4), (0, 0, 0), lens=50)


def aa():
    reset((800, 700))
    bpy.ops.object.text_add(location=(0, 0, 0.9), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.data.body = 'Aa'; t.data.font = bpy.data.fonts.load(FONT); t.data.size = 1.6
    t.data.extrude = 0.12; t.data.bevel_depth = 0.02; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    t.data.materials.append(mat('aa', NAVY, rough=0.25, coat=0.8))
    t.rotation_euler[2] = math.radians(-12)
    shot('aa', (0.6, -6.0, 1.6), (0, 0, 0.9), lens=50)


if __name__ == '__main__':
    for n in sys.argv[1:]:
        if n in ('van', 'sign', 'card', 'web', 'insta', 'invoice'):
            for st in ('before', 'after'):
                globals()[n](st)
        else:
            globals()[n]()
