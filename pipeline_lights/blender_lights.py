"""3D props for BMHC "Lights On" (glossy, BMHC palette: deep green, gold, teal, ivory, magenta).

Usage: python3 blender_lights.py <prop> [...]
Props: switch_off, switch_on, bulb, rehal, belt, mic, tea, compass, clock, dice
"""
import bpy, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_cf as C
from blender_cf import setup, gloss, sphere
from blender_lo import lin, mat, box
from blender_sol import text_obj

C.OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_lights', 'assets'))
shot = C.shot
GREEN_D, IVORY, TEAL, GOLD, MAG, ORANGE, GREEN = '#122F2A', '#EFEEEA', '#09999C', '#DD9933', '#DB225E', '#F26721', '#76BF43'
FONT = os.path.abspath(os.path.join(HERE, '..', 'workspace_bmhc', 'fonts', 'Poppins-Bold.ttf'))


def cyl(r, d, loc, m, rot=(0, 0, 0), v=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def _switch(on):
    setup()
    plate = gloss('plate', IVORY, rough=0.3, coat=0.6)
    box((2.2, 0.25, 3.0), (0, 0, 0), plate, bevel=0.2)
    box((0.9, 0.12, 1.5), (0, -0.16, 0), gloss('well', '#D9D6CF', rough=0.4), bevel=0.12)
    rock = gloss('rock', GOLD if on else '#BFB9AE', rough=0.25)
    t = box((0.78, 0.3, 1.3), (0, 0, 0), rock, bevel=0.14)
    t.location = (0, -0.3, 0)
    t.rotation_euler = (math.radians(-14 if on else 14), 0, 0)
    for z in (1.15, -1.15):
        cyl(0.11, 0.05, (0, -0.14, z), gloss('scr%d' % (z > 0), '#A69F93', rough=0.3, coat=0.2), rot=(math.radians(90), 0, 0))
    if on:
        sphere(0.12, (0.62, -0.2, 0.95), mat('led', lin(GOLD), emit=lin('#FFD27A'), estr=8))
    shot('switch_on' if on else 'switch_off', (0.9, -7.4, 0.6), (0, 0, 0))


def switch_off():
    _switch(False)


def switch_on():
    _switch(True)


def bulb():
    setup()
    glass = mat('glass', lin('#FFF4D6'), emit=lin('#FFD27A'), estr=6, rough=0.1)
    sphere(1.1, (0, 0, 0.55), glass, (1, 1, 1.1))
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0.42, depth=0.7, location=(0, 0, -0.55), vertices=48)
    bpy.context.object.data.materials.append(glass)
    for k in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.44, minor_radius=0.07, location=(0, 0, -1.0 - k * 0.16), major_segments=48)
        bpy.context.object.data.materials.append(gloss('base%d' % k, GOLD, rough=0.25, coat=0.3))
    sphere(0.2, (0, 0, -1.68), gloss('tip', GREEN_D))
    bpy.ops.object.light_add(type='POINT', location=(0, -1.5, 0.5))
    bpy.context.object.data.energy = 300
    bpy.context.object.data.color = (1.0, 0.85, 0.55)
    shot('bulb', (0, -7.6, 0.2), (0, 0, -0.1))


def rehal():
    """A wooden folding stand holding a closed book wrapped in plain green cloth (no script)."""
    setup()
    wood = mat('wood', lin('#9A6A3A'), rough=0.45, coat=0.3)
    cloth = mat('cloth', lin('#1F6B4F'), rough=0.85)
    for s in (-1, 1):
        o = box((2.0, 0.12, 1.9), (0, 0, 0), wood, bevel=0.05)
        o.rotation_euler = (math.radians(s * 32), 0, 0)
        o.location = (0, s * 0.55, 0)
        cut = box((0.7, 0.2, 0.5), (0, 0, 0), wood)
        cut.location = (0, s * 0.55, -0.35)
        cut.rotation_euler = (math.radians(s * 32), 0, 0)
        cut.hide_render = True
    book = box((1.7, 1.5, 0.32), (0, 0, 0), cloth, bevel=0.12)
    book.location = (0, -0.28, 0.42)
    book.rotation_euler = (math.radians(58), 0, 0)
    knot = sphere(0.16, (0, -0.95, 0.85), gloss('knot', '#2E8B67', rough=0.6, coat=0.1))
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.rotation_euler[2] += math.radians(-24)
    shot('rehal', (2.2, -6.8, 2.2), (0, 0, 0.2))


def belt():
    """Taekwondo belts hanging on a gold peg."""
    setup()
    peg = gloss('peg', GOLD, rough=0.25)
    cyl(0.14, 1.2, (0, -0.4, 1.4), peg, rot=(math.radians(90), 0, 0))
    sphere(0.22, (0, -1.0, 1.4), peg)
    for k, (col, dx) in enumerate((('#151515', 0.0), (MAG, 0.55), (TEAL, -0.55))):
        m = mat('b%d' % k, lin(col), rough=0.6, coat=0.2)
        y = -0.15 - k * 0.08
        bpy.ops.mesh.primitive_torus_add(major_radius=0.36, minor_radius=0.09, location=(dx * 0.25, y, 1.3), rotation=(0, 0, 0), major_segments=48)
        t = bpy.context.object; t.scale = (1, 0.35, 1); t.data.materials.append(m)
        for side in (-1, 1):
            o = box((0.34, 0.08, 2.6 - k * 0.35), (0, 0, 0), m, bevel=0.03)
            o.location = (dx * 0.25 + side * 0.33, y, 1.3 - (2.6 - k * 0.35) / 2)
            o.rotation_euler = (0, math.radians(side * -4), 0)
    box((0.36, 0.1, 0.25), (0.33, -0.2, -1.15), gloss('tip', GOLD), bevel=0.03)
    shot('belt', (0.6, -7.6, 0.4), (0, 0, 0.1))


def mic():
    setup()
    body = gloss('mic', '#1B1D22', rough=0.35, coat=0.3)
    grille = mat('grille', lin('#3A3D44'), rough=0.5, metal=0.8)
    cyl(0.5, 1.9, (0, 0, 0.3), body, rot=(0, math.radians(-12), 0))
    sphere(0.52, (-0.2, 0, 1.25), grille)
    box((0.15, 0.15, 1.8), (0.6, 0, -1.3), gloss('arm', '#2B2E35', rough=0.3), bevel=0.05).rotation_euler = (0, math.radians(30), 0)
    lamp = mat('lamp', lin('#FF3B30'), emit=lin('#FF2D20'), estr=9, rough=0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.22, location=(1.1, 0.2, 1.75), rotation=(math.radians(90), 0, 0), vertices=48)
    bpy.context.object.data.materials.append(lamp)
    cyl(0.48, 0.12, (1.1, 0.34, 1.75), gloss('rim', '#2B2E35'), rot=(math.radians(90), 0, 0))
    shot('mic', (0.6, -7.6, 0.6), (0.3, 0, 0.2))


def tea():
    setup()
    glass = mat('tg', lin('#F7EDE0'), rough=0.05)
    glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1.0
    tea_m = mat('tea', lin('#B4521C'), rough=0.1, emit=lin('#C85A1E'), estr=0.6)
    for x, sc in ((-0.75, 1.0), (0.55, 0.85)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5 * sc, depth=1.4 * sc, location=(x, 0.3, 0.1), vertices=64)
        g = bpy.context.object; g.data.materials.append(glass); g.scale = (1, 1, 1)
        bpy.ops.object.shade_smooth()
        cyl(0.44 * sc, 1.0 * sc, (x, 0.3, 0.0), tea_m)
    plate = gloss('plate', TEAL, rough=0.25)
    cyl(1.2, 0.12, (0.1, -0.55, -0.72), plate, v=96)
    date = mat('date', lin('#5A2A12'), rough=0.35, coat=0.6)
    for k, (x, y) in enumerate(((-0.4, -0.7), (0.05, -0.95), (0.5, -0.65), (0.15, -0.35), (-0.3, -0.3))):
        o = sphere(0.22, (x, y, -0.5), date, (1.0, 0.62, 0.62))
        o.rotation_euler = (0, 0, k * 0.9)
    shot('tea', (0.6, -6.8, 2.4), (0, 0, -0.2))


def compass():
    setup()
    brass = mat('brass', lin(GOLD), rough=0.25, metal=1.0)
    face = mat('face', lin(IVORY), rough=0.4)
    cyl(1.4, 0.35, (0, 0, 0), brass, rot=(math.radians(90), 0, 0), v=96)
    cyl(1.2, 0.36, (0, -0.02, 0), face, rot=(math.radians(90), 0, 0), v=96)
    import bmesh
    for col, rot in ((MAG, 0), ('#2B2E35', 180)):
        me = bpy.data.meshes.new('n'); bm = bmesh.new()
        v = [bm.verts.new(p) for p in ((0, -0.22, 1.0), (0.18, -0.22, 0), (0, -0.22, -0.05), (-0.18, -0.22, 0))]
        bm.faces.new(v); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new('n', me); bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(gloss('nd%d' % rot, col)); ob.rotation_euler = (0, math.radians(rot + 25), 0)
        s = ob.modifiers.new('s', 'SOLIDIFY'); s.thickness = 0.06
    sphere(0.12, (0, -0.28, 0), brass)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.08, location=(0, 0, 1.55), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(brass)
    shot('compass', (0.8, -7.4, 0.6), (0, 0, 0.1))


def clock():
    setup()
    ring = gloss('ring', TEAL, rough=0.25)
    cyl(1.45, 0.4, (0, 0, 0), ring, rot=(math.radians(90), 0, 0), v=96)
    cyl(1.25, 0.42, (0, -0.02, 0), mat('cf', lin('#FFFFFF'), rough=0.4), rot=(math.radians(90), 0, 0), v=96)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        box((0.08, 0.05, 0.22 if k % 3 else 0.32), (1.02 * math.sin(a), -0.24, 1.02 * math.cos(a)), gloss('t%d' % k, '#122F2A', rough=0.4)).rotation_euler = (0, a, 0)
    text_obj('24', 0.8, (0, -0.26, -0.15), (90, 0, 0), gloss('n', MAG), font=FONT, extrude=0.06, bevel=0.01)
    h = box((0.09, 0.05, 0.6), (0, -0.27, 0.28), gloss('h', '#122F2A'))
    shot('clock', (0.8, -7.4, 0.6), (0, 0, 0))


def dice():
    setup()
    for k, (x, col, rz) in enumerate(((-0.75, MAG, 20), (0.85, TEAL, -30))):
        d = box((1.3, 1.3, 1.3), (0, 0, 0), gloss('d%d' % k, col, rough=0.25), bevel=0.22)
        for j, (px, pz) in enumerate(((0, 0), (-0.32, 0.32), (0.32, -0.32))):
            p = sphere(0.13, (px, -0.62, pz), mat('pip%d%d' % (k, j), (1, 1, 1, 1), rough=0.3), (1, 0.5, 1))
            p.parent = d
        d.location = (x, 0, 0)
        d.rotation_euler = (math.radians(12 * (k * 2 - 1)), math.radians(10), math.radians(rz))
    shot('dice', (0.6, -7.6, 1.6), (0, 0, 0))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
