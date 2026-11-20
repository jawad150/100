"""3D pop-up objects for Organic Fostering "The Question in the Notes App" (glossy clay, OF palette).

Run: blender -b -P blender_notes.py -- [draft] [name ...]  -> workspace_notes/assets/<name>.png (RGBA 900x900)
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_notes/assets'
TEX = f'{ROOT}/workspace_notes/tex'
os.makedirs(B.OUT, exist_ok=True)

PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')
IVORY, BLUSH, PEACH, LEAF, INK = hexc('#FCF8F5'), hexc('#F6EAF3'), hexc('#FFD4BA'), hexc('#E8F3D8'), hexc('#321F35')
WHITE, GREY, LILAC, GOLD, TEA = hexc('#FFFFFF'), hexc('#B9AEBB'), hexc('#CDB8D6'), hexc('#E2A93B'), hexc('#7A3A16')
WARM = hexc('#FFC27A')


def img_mat(path, emit=0.0, rough=0.35):
    m = bpy.data.materials.new('img')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if emit:
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = emit
    return m


def plane(w, h, loc, rot, m):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = act()
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return setm(o, m)


def phone_notes():
    """The phone with the Notes app open on the question."""
    body = box((1.7, 0.16, 3.4), m=mat(PLUM, 0.25, coat=0.7), bw=0.22)
    plane(1.52, 3.2, (0, -0.085, 0), (math.radians(90), 0, 0), img_mat(f'{TEX}/notes_screen.png', emit=0.9, rough=0.2))
    cam = cyl(0.07, 0.04, loc=(0, -0.09, 1.52), m=mat(INK, 0.2), rot=(math.radians(90), 0, 0), bw=0)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(8), 0, math.radians(-16)))


def drafts():
    """Three drafts of the same question, stacked like layers (Mon, Wed, Fri)."""
    for i, (day, rot) in enumerate((('mon', 10), ('wed', -4), ('fri', -16))):
        o = plane(1.5, 1.9, (i * 0.25 - 0.25, -i * 0.25, i * 0.08), (math.radians(90), math.radians(rot), 0),
                  img_mat(f'{TEX}/draft_{day}.png', emit=0.15, rough=0.5))
        sol = o.modifiers.new('s', 'SOLIDIFY')
        sol.thickness = 0.03
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-14)))


def calendar():
    """That week: a desk calendar, three evenings circled."""
    base = box((2.6, 0.5, 2.0), loc=(0, 0.1, -0.1), m=mat(IVORY, 0.45, coat=0.2), bw=0.1, rot=(math.radians(-12), 0, 0))
    head = box((2.62, 0.52, 0.45), loc=(0, 0.02, 0.85), m=mat(PLUM, 0.3, coat=0.5), bw=0.1, rot=(math.radians(-12), 0, 0))
    for k in range(4):
        torus(0.1, 0.035, loc=(-0.9 + k * 0.6, -0.1, 1.08), m=mat(GOLD, 0.2, 0.9), rot=(0, math.radians(90), 0))
    for i in range(7):
        x = -1.08 + i * 0.36
        on = i in (0, 2, 4)
        c = cyl(0.13, 0.04, loc=(x, -0.21, 0.15), m=mat(MAG if on else LILAC, 0.3, emit=(MAG, 0.4) if on else None),
                rot=(math.radians(78), 0, 0), bw=0.01)
        if on:
            torus(0.17, 0.025, loc=(x, -0.25, 0.15), m=mat(MAG, 0.3), rot=(math.radians(78), 0, 0))
    t = text('THAT WEEK', 0.22, (0, -0.2, 0.55), mat(PLUM, 0.4), rot=(math.radians(78), 0, 0), ext=0.02, font='Nunito-900')
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'FONT')]
    group(objs, rot=(0, 0, math.radians(-18)))


def mug():
    """The mug they keep turning in their hands."""
    body = cyl(0.8, 1.4, loc=(0, 0, 0.7), m=mat(PLUM, 0.28, coat=0.7), v=96, bw=0.08)
    inner = cyl(0.7, 0.05, loc=(0, 0, 1.33), m=mat(TEA, 0.1), v=96, bw=0)
    for i, c in enumerate((MAG, ORANGE, GREEN)):
        torus(0.805, 0.035, loc=(0, 0, 0.35 + i * 0.12), m=mat(c, 0.3))
    torus(0.38, 0.11, loc=(0.92, 0, 0.75), m=mat(PLUM, 0.28, coat=0.7), rot=(math.radians(90), 0, 0))
    for k in range(3):
        curve_path([(-0.25 + k * 0.25, 0, 1.5), (-0.1 + k * 0.25, 0, 1.9), (-0.3 + k * 0.25, 0, 2.3), (-0.12 + k * 0.25, 0, 2.7)],
                   0.035, mat(WHITE, 0.3, emit=(WHITE, 0.6), trans=0.2))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(0, 0, math.radians(-24)))


def cloud():
    """'Struggling': a small rain cloud."""
    m = mat(LILAC, 0.45, coat=0.3)
    for x, z, r in ((-0.8, 0, 0.6), (0, 0.3, 0.85), (0.8, 0.05, 0.62), (0.35, -0.25, 0.55), (-0.35, -0.2, 0.55)):
        sph(r, loc=(x, 0, z), m=m)
    d = mat(hexc('#7FA8D9'), 0.1, coat=0.6, trans=0.3)
    for i, (x, z) in enumerate(((-0.6, -1.0), (-0.1, -1.3), (0.4, -1.05), (0.85, -1.4), (0.15, -1.75))):
        sph(0.1, loc=(x, 0, z), m=d, scale=(1, 1, 1.6))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs)


def home_door():
    """'A child comes to live with me': a home with its door open, warm light, a small rucksack on the step."""
    wall = box((2.2, 1.8, 1.7), loc=(0, 0, 0.85), m=mat(IVORY, 0.45, coat=0.2), bw=0.08)
    for s in (-1, 1):
        box((1.6, 2.1, 0.14), loc=(s * 0.6, 0, 2.22), m=mat(PLUM, 0.3, coat=0.5), bw=0.05, rot=(0, s * math.radians(38), 0))
    box((0.62, 0.06, 1.05), loc=(0.25, -0.91, 0.53), m=mat(WARM, 0.3, emit=(WARM, 4.0)), bw=0.01)
    door = box((0.6, 0.08, 1.05), loc=(-0.12, -1.13, 0.53), m=mat(MAG, 0.3, coat=0.4), bw=0.03, rot=(0, 0, math.radians(-62)))
    box((0.5, 0.06, 0.45), loc=(-0.6, -0.91, 1.05), m=mat(WARM, 0.3, emit=(WARM, 2.5)), bw=0.01)
    box((2.6, 2.4, 0.12), loc=(0, -0.2, -0.06), m=mat(LEAF, 0.6), bw=0.05)
    bag = box((0.36, 0.22, 0.42), loc=(0.75, -1.25, 0.2), m=mat(ORANGE, 0.35, coat=0.4), bw=0.08)
    torus(0.12, 0.025, loc=(0.75, -1.25, 0.45), m=mat(ORANGE, 0.35), rot=(math.radians(90), 0, 0))
    L = bpy.data.objects.new('pl', bpy.data.lights.new('pl', 'POINT'))
    L.data.energy, L.data.color = 60, (1.0, 0.75, 0.45)
    L.location = (0.25, -1.2, 0.6)
    bpy.context.scene.collection.objects.link(L)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-20)))


def badge():
    """'A supervising social worker': a lanyard ID badge."""
    card = box((1.7, 0.08, 2.3), loc=(0, 0, 0), m=mat(WHITE, 0.35, coat=0.4), bw=0.08)
    plane(1.62, 2.22, (0, -0.045, 0), (math.radians(90), 0, 0), img_mat(f'{TEX}/badge.png', emit=0.25, rough=0.4))
    box((0.5, 0.1, 0.16), loc=(0, 0, 1.25), m=mat(INK, 0.3), bw=0.03)
    curve_path([(-0.18, 0, 1.3), (-0.6, 0.1, 2.2), (0, 0.15, 3.0), (0.6, 0.1, 2.2), (0.18, 0, 1.3)], 0.06, mat(MAG, 0.4))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(0, 0, math.radians(14)))


def night_clock():
    """'Who to call outside normal hours': an alarm clock at night with a crescent moon."""
    body = cyl(1.0, 0.5, loc=(0, 0, 0), m=mat(PLUM, 0.28, coat=0.7), rot=(math.radians(90), 0, 0), v=96, bw=0.1)
    face = cyl(0.84, 0.05, loc=(0, -0.26, 0), m=mat(IVORY, 0.3, emit=(PEACH, 0.4)), rot=(math.radians(90), 0, 0), v=96, bw=0)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        box((0.05, 0.03, 0.14 if k % 3 == 0 else 0.08), loc=(0.68 * math.sin(a), -0.3, 0.68 * math.cos(a)), m=mat(PLUM, 0.4), bw=0, rot=(0, a, 0))
    box((0.07, 0.03, 0.42), loc=(-0.1, -0.33, 0.17), m=mat(INK, 0.3), bw=0.01, rot=(0, math.radians(-30), 0))
    box((0.05, 0.03, 0.6), loc=(0.0, -0.34, 0.29), m=mat(MAG, 0.3), bw=0.01, rot=(0, math.radians(0), 0))
    sph(0.07, loc=(0, -0.36, 0), m=mat(INK, 0.3))
    for s in (-1, 1):
        sph(0.32, loc=(s * 0.62, 0, 0.92), m=mat(MAG, 0.3, coat=0.6), scale=(1, 0.7, 0.55))
        box((0.08, 0.08, 0.4), loc=(s * 0.55, 0, -1.0), m=mat(PLUM, 0.3), bw=0.02, rot=(0, s * math.radians(25), 0))
    # crescent moon
    import bmesh
    for x, z in ((-1.2, 1.4), (-0.9, 1.9), (1.6, 0.5)):
        sph(0.06, loc=(x, 0, z), m=mat(WHITE, 0.3, emit=(WHITE, 3.0)))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_render]
    group(objs, rot=(0, 0, math.radians(-14)))


def cap():
    """'Training': a graduation cap resting on two books."""
    box((2.2, 1.5, 0.32), loc=(0, 0, 0), m=mat(GREEN, 0.35, coat=0.4), bw=0.05)
    box((2.1, 1.4, 0.28), loc=(0.08, 0, 0.32), m=mat(ORANGE, 0.35, coat=0.4), bw=0.05, rot=(0, 0, math.radians(8)))
    box((2.0, 1.32, 0.02), loc=(0.1, -0.04, 0.17), m=mat(IVORY, 0.6), bw=0)
    cyl(0.62, 0.42, loc=(0, 0, 0.72), m=mat(PLUM, 0.3, coat=0.5), v=64, bw=0.04)
    box((1.9, 1.9, 0.08), loc=(0, 0, 0.98), m=mat(PLUM, 0.3, coat=0.5), bw=0.03, rot=(0, 0, math.radians(45)))
    sph(0.09, loc=(0, 0, 1.04), m=mat(GOLD, 0.2, 0.9))
    curve_path([(0, 0, 1.05), (0.6, -0.3, 1.04), (0.95, -0.5, 0.95), (1.0, -0.55, 0.5)], 0.03, mat(GOLD, 0.2, 0.9))
    cyl(0.07, 0.3, loc=(1.0, -0.55, 0.38), m=mat(GOLD, 0.3, 0.9), bw=0)
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(math.radians(6), 0, math.radians(-20)))


def chat():
    """'We can talk you through it': two speech bubbles."""
    a = box((2.1, 0.5, 1.1), loc=(-0.5, 0, 0.6), m=mat(MAG, 0.28, coat=0.6), bw=0.4)
    t1 = text('?', 0.75, (-0.5, -0.27, 0.6), mat(WHITE, 0.3), ext=0.05, font='Nunito-900')
    b = box((1.9, 0.5, 1.0), loc=(0.6, -0.4, -0.6), m=mat(IVORY, 0.35, coat=0.6), bw=0.4)
    for k in range(3):
        sph(0.11, loc=(0.25 + k * 0.33, -0.67, -0.6), m=mat(PLUM, 0.3))
    for (x, z, s, m) in ((-1.1, -0.05, 1, mat(MAG, 0.28, coat=0.6)), (1.2, -1.15, -1, mat(IVORY, 0.35, coat=0.6))):
        bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0, depth=0.5, location=(x, -0.2 if s > 0 else -0.4, z),
                                        rotation=(0, math.radians(180 + s * 25), 0), vertices=32)
        smooth(setm(act(), m))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'FONT')]
    group(objs, rot=(0, 0, math.radians(-12)))


ALL = ['phone_notes', 'drafts', 'calendar', 'mug', 'cloud', 'home_door', 'badge', 'night_clock', 'cap', 'chat']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        bpy.context.scene.cycles.samples = 24 if draft else 96
        globals()[n]()
        B.render(n)
