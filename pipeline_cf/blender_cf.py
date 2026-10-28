"""3D props for Organic Fostering "Can I Foster If…?" (Blender Cycles stills, transparent, glossy toy style).

Usage: python3 blender_cf.py <prop> [...]
Props: paw, infinity, speech, plane, qmark, magnifier, house
"""
import bpy, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
from blender_lo import lin, reset, mat, box, camera, look
from blender_sol import std, studio, text_obj

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_cf'))
OUT = S + '/assets'
FONT = os.path.abspath(os.path.join(HERE, '..', 'workspace_of', 'fonts', 'Nunito-900.ttf'))
PURPLE, ORANGE, PLUM, IVORY, LAV, PEACH, LEAF = '#B7006E', '#FF6411', '#5B174F', '#FCF8F5', '#F6EAF3', '#FFD4BA', '#64A60B'


def setup(res=(640, 640), samples=48):
    reset(res, samples=samples, transparent=True)
    std()
    studio(world_col='#F4E6EE', strength=0.55, key=950, rim=800)


def gloss(name, hexcol, rough=0.22, coat=0.8):
    return mat(name, lin(hexcol), rough=rough, coat=coat)


def shot(name, cam_loc=(0, -8.0, 0.6), target=(0, 0, 0), lens=50):
    cam = camera(lens=lens)
    cam.data.dof.use_dof = False
    look(cam, cam_loc, target)
    os.makedirs(OUT, exist_ok=True)
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


def sphere(r, loc, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def paw():
    setup()
    m = gloss('purple', PURPLE)
    sphere(1.0, (0, 0, -0.45), m, (1.15, 0.45, 0.95))
    for x, z, r in ((-1.15, 0.65, 0.42), (-0.42, 1.2, 0.46), (0.42, 1.2, 0.46), (1.15, 0.65, 0.42)):
        sphere(r, (x, 0, z), m, (1, 0.5, 1.15))
    shot('paw', (1.5, -7.5, 1.2), (0, 0, 0.3))


def infinity():
    setup((720, 520))
    m = gloss('orange', ORANGE)
    bpy.ops.curve.primitive_bezier_circle_add(radius=1.0)
    cu = bpy.context.object
    sp = cu.data.splines[0]
    pts = sp.bezier_points
    sp.bezier_points.add(0)
    # lemniscate as a poly curve
    bpy.data.objects.remove(cu)
    cd = bpy.data.curves.new('inf', 'CURVE')
    cd.dimensions = '3D'
    s = cd.splines.new('POLY')
    n = 160
    s.points.add(n - 1)
    for i in range(n):
        t = i / n * 2 * math.pi
        d = 1 + math.sin(t) ** 2
        s.points[i].co = (2.0 * math.cos(t) / d, 0.25 * math.sin(2 * t), 2.0 * math.sin(t) * math.cos(t) / d, 1)
    s.use_cyclic_u = True
    cd.bevel_depth = 0.26
    cd.bevel_resolution = 8
    o = bpy.data.objects.new('inf', cd)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    o.rotation_euler = (math.radians(8), 0, math.radians(-12))
    shot('infinity', (0, -8.5, 1.4), (0, 0, 0))


def speech():
    setup()
    m = gloss('lav', '#D9A8CF', rough=0.25)
    dot = gloss('plum', PLUM)
    b = sphere(1.0, (0, 0, 0.2), m, (1.6, 0.55, 1.15))
    bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0.0, depth=0.9, location=(-0.85, 0, -0.95),
                                    rotation=(0, math.radians(200), 0), vertices=32)
    bpy.context.object.data.materials.append(m)
    bpy.context.object.scale = (1, 0.5, 1)
    for x in (-0.6, 0, 0.6):
        sphere(0.2, (x, -0.55, 0.2), dot)
    shot('speech', (1.0, -7.6, 1.0), (0, 0, 0))


def plane():
    setup()
    m = gloss('purple', PURPLE, rough=0.3, coat=0.5)
    m2 = gloss('orange', ORANGE, rough=0.3, coat=0.5)
    import bmesh
    me = bpy.data.meshes.new('plane')
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((2.2, 0, 0), (-1.4, -1.5, 0.05), (-0.9, 0, -0.1), (-1.4, 1.5, 0.05), (-1.1, 0, -0.75))]
    bm.faces.new((v[0], v[1], v[2]))
    bm.faces.new((v[0], v[2], v[3]))
    f1 = bm.faces.new((v[0], v[4], v[2]))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('plane', me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    o.data.materials.append(m2)
    o.data.polygons[2].material_index = 1
    sol = o.modifiers.new('s', 'SOLIDIFY')
    sol.thickness = 0.06
    o.rotation_euler = (math.radians(-60), math.radians(10), math.radians(25))
    shot('plane', (0, -7.5, 1.0), (0, 0, 0))


def qmark():
    setup()
    m = gloss('purple', PURPLE)
    t = text_obj('?', 3.6, (0, 0, -0.1), (90, 0, 12), m, font=FONT, extrude=0.35, bevel=0.07)
    shot('qmark', (0.8, -7.4, 0.6), (0, 0, 0.0))


def magnifier():
    setup()
    m = gloss('purple', PURPLE)
    h = gloss('orange', ORANGE)
    glass = mat('glass', (0.95, 0.9, 1.0, 1), rough=0.02)
    glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1.0
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.18, location=(0.3, 0, 0.5), rotation=(math.radians(90), 0, 0),
                                     major_segments=96, minor_segments=24)
    bpy.context.object.data.materials.append(m)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=0.08, location=(0.3, 0, 0.5), rotation=(math.radians(90), 0, 0), vertices=96)
    bpy.context.object.data.materials.append(glass)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=1.5, location=(-0.75, 0, -0.55), rotation=(0, math.radians(45), 0), vertices=32)
    bpy.context.object.data.materials.append(h)
    shot('magnifier', (0.5, -7.6, 0.6), (0, 0, 0))


def house():
    setup()
    wall = gloss('ivory', IVORY, rough=0.35, coat=0.4)
    roof = gloss('purple', PURPLE)
    door = gloss('orange', ORANGE)
    win = mat('win', (1, 0.85, 0.5, 1), emit=(1.0, 0.75, 0.35, 1), estr=4.0)
    box((2.2, 1.8, 1.6), (0, 0, 0), wall, bevel=0.08)
    bpy.ops.mesh.primitive_cone_add(radius1=1.75, radius2=0, depth=1.2, location=(0, 0, 1.35), vertices=4, rotation=(0, 0, math.radians(45)))
    r = bpy.context.object
    r.scale = (1.0, 0.85, 1)
    r.data.materials.append(roof)
    box((0.5, 0.06, 0.85), (0.45, -0.92, -0.37), door, bevel=0.03)
    box((0.5, 0.06, 0.45), (-0.5, -0.92, 0.15), win, bevel=0.03)
    shot('house', (2.5, -7.0, 2.0), (0, 0, 0.2))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
