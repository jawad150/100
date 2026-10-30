"""3D props for Organic Fostering "You Are Here" (glossy toy style, brand palette).

Usage: python3 blender_yah.py <prop> [...]
Props: pin, clipboard, shield, books, badge, key, phone, calendar
"""
import bpy, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_cf as C
from blender_cf import setup, gloss, sphere, PURPLE, ORANGE, PLUM, IVORY, LAV, PEACH, LEAF, FONT
from blender_lo import lin, mat, box, camera, look
from blender_sol import text_obj

C.OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_yah', 'assets'))
shot = C.shot


def cyl(r, d, loc, m, rot=(0, 0, 0), v=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def pin():
    setup()
    m = gloss('pin', PURPLE)
    sphere(1.0, (0, 0, 0.9), m)
    bpy.ops.mesh.primitive_cone_add(radius1=0.86, radius2=0.0, depth=1.7, location=(0, 0, -0.35), rotation=(math.radians(180), 0, 0), vertices=64)
    bpy.context.object.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    sphere(0.42, (0, -0.72, 1.0), gloss('w', '#FFFFFF', rough=0.3), (1, 0.4, 1))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.06, location=(0, 0, -1.25), major_segments=96)
    bpy.context.object.data.materials.append(gloss('o', ORANGE))
    shot('pin', (0.6, -7.2, 1.6), (0, 0, 0.2))


def clipboard():
    setup()
    board = gloss('board', ORANGE, rough=0.35, coat=0.5)
    paper = mat('paper', lin('#FFFFFF'), rough=0.6)
    clip = gloss('clip', PURPLE)
    box((2.2, 0.16, 2.9), (0, 0, 0), board, bevel=0.12)
    box((1.85, 0.05, 2.4), (0, -0.1, -0.12), paper, bevel=0.02)
    box((0.9, 0.22, 0.35), (0, -0.12, 1.42), clip, bevel=0.08)
    for k in range(4):
        box((1.25 if k else 0.9, 0.03, 0.09), (-0.15 if k else -0.33, -0.14, 0.75 - k * 0.42), mat('ln%d' % k, lin('#D9C7D4'), rough=0.6))
    cyl(0.17, 0.05, (0.62, -0.15, -0.95), gloss('ck', LEAF), rot=(math.radians(90), 0, 0))
    o = bpy.data.objects
    for ob in list(o):
        if ob.type == 'MESH':
            ob.rotation_euler[2] += math.radians(-14)
    shot('clipboard', (1.0, -7.6, 1.0), (0, 0, 0))


def shield():
    setup()
    import bmesh
    m = gloss('sh', LEAF, rough=0.25)
    pts = [(0, 1.7), (1.4, 1.25), (1.35, 0.1), (0.9, -1.0), (0, -1.75), (-0.9, -1.0), (-1.35, 0.1), (-1.4, 1.25)]
    me = bpy.data.meshes.new('sh')
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('sh', me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    s = ob.modifiers.new('s', 'SOLIDIFY'); s.thickness = 0.45; s.offset = 1.0
    b = ob.modifiers.new('b', 'BEVEL'); b.width = 0.12; b.segments = 6
    sub = ob.modifiers.new('ss', 'SUBSURF'); sub.levels = 2
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    w = gloss('wck', '#FFFFFF', rough=0.3)
    for (x0, z0, x1, z1) in ((-0.6, 0.05, -0.15, -0.45), (-0.15, -0.45, 0.7, 0.6)):
        L = math.hypot(x1 - x0, z1 - z0)
        o = box((L + 0.22, 0.2, 0.26), (0, 0, 0), w, bevel=0.1)
        o.location = ((x0 + x1) / 2, -0.62, (z0 + z1) / 2)
        o.rotation_euler = (0, -math.atan2(z1 - z0, x1 - x0), 0)
    shot('shield', (0.8, -7.4, 0.8), (0, 0, 0))


def books():
    setup()
    cols = [PURPLE, ORANGE, '#D9A8CF', LEAF]
    for k, c in enumerate(cols):
        o = box((2.4 - 0.15 * k, 1.6, 0.42), (0, 0, -0.9 + k * 0.45), gloss('b%d' % k, c, rough=0.3), bevel=0.06)
        o.rotation_euler = (0, 0, math.radians(8 * (k % 2 * 2 - 1)))
        box((2.25 - 0.15 * k, 1.5, 0.36), (0.06, 0, -0.9 + k * 0.45), mat('pg%d' % k, lin('#FFF8F0'), rough=0.7)).rotation_euler = (0, 0, math.radians(8 * (k % 2 * 2 - 1)))
    cap = gloss('cap', PLUM)
    box((2.0, 2.0, 0.1), (0, 0, 1.25), cap, bevel=0.03).rotation_euler = (0, 0, math.radians(45))
    cyl(0.62, 0.45, (0, 0, 1.0), cap)
    cyl(0.04, 0.9, (0.75, -0.45, 0.85), gloss('tas', ORANGE))
    shot('books', (2.6, -7.0, 2.6), (0, 0, 0.1))


def badge():
    setup()
    m = gloss('bd', LEAF, rough=0.25)
    for k in range(12):
        o = box((2.05, 0.3, 2.05), (0, 0, 0), m, bevel=0.15)
        o.rotation_euler = (0, math.radians(k * 7.5), 0)
    cyl(1.25, 0.42, (0, -0.05, 0), gloss('in', '#FFFFFF', rough=0.3), rot=(math.radians(90), 0, 0))
    w = gloss('ck', LEAF)
    for (x0, z0, x1, z1) in ((-0.55, 0.0, -0.12, -0.42), (-0.12, -0.42, 0.62, 0.45)):
        L = math.hypot(x1 - x0, z1 - z0)
        o = box((L + 0.2, 0.2, 0.24), (0, 0, 0), w, bevel=0.1)
        o.location = ((x0 + x1) / 2, -0.32, (z0 + z1) / 2)
        o.rotation_euler = (0, -math.atan2(z1 - z0, x1 - x0), 0)
    shot('badge', (0.8, -7.6, 0.8), (0, 0, 0))


def key():
    setup()
    m = gloss('k', ORANGE, rough=0.22)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.26, location=(-1.2, 0, 0.4), rotation=(math.radians(90), 0, 0), major_segments=96, minor_segments=32)
    bpy.context.object.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    box((2.4, 0.3, 0.36), (0.75, 0, 0.4), m, bevel=0.1)
    box((0.3, 0.3, 0.55), (1.55, 0, 0.02), m, bevel=0.08)
    box((0.3, 0.3, 0.4), (1.1, 0, 0.08), m, bevel=0.08)
    sphere(0.42, (-1.2, -0.05, 0.4), gloss('h', PURPLE), (1, 0.5, 1))
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.rotation_euler[1] += math.radians(-25)
    shot('key', (0.6, -7.6, 0.6), (0, 0, 0.2))


def phone():
    setup()
    body = gloss('ph', PLUM, rough=0.25)
    box((1.7, 0.22, 3.2), (0, 0, 0), body, bevel=0.22)
    scr = mat('scr', lin('#FCF8F5'), emit=lin('#FCEFF4'), estr=0.6)
    box((1.48, 0.05, 2.9), (0, -0.12, 0), scr, bevel=0.15)
    for k, (c, x, z, w) in enumerate(((PURPLE, -0.15, 0.85, 0.9), ('#D9A8CF', 0.15, 0.25, 0.9), (PURPLE, -0.1, -0.35, 1.0))):
        box((w, 0.06, 0.38), (x, -0.16, z), gloss('bub%d' % k, c, rough=0.3), bevel=0.15)
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.rotation_euler[2] += math.radians(-16)
            ob.rotation_euler[1] += math.radians(8)
    shot('phone', (0.8, -7.8, 0.6), (0, 0, 0))


def calendar():
    setup()
    body = mat('cal', lin('#FFFFFF'), rough=0.5)
    top = gloss('top', PURPLE)
    box((2.6, 0.3, 2.6), (0, 0, -0.2), body, bevel=0.15)
    box((2.6, 0.32, 0.75), (0, 0, 1.15), top, bevel=0.15)
    for x in (-0.7, 0.7):
        cyl(0.11, 0.6, (x, 0, 1.6), gloss('r', ORANGE))
    t = text_obj('8', 1.5, (0, -0.2, -0.45), (90, 0, 0), gloss('n', ORANGE), font=FONT, extrude=0.12, bevel=0.03)
    shot('calendar', (0.9, -7.6, 0.9), (0, 0, 0.1))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
