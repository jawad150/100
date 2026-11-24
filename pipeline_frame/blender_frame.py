"""3D objects that break through the Instagram frame (Organic Fostering "A little care goes a long way").
Glossy clay in the OF palette: teddy, backpack, puzzle piece, two hands meeting, an open front door.

Run: blender -b -P blender_frame.py -- [draft] [name ...] -> workspace_frame/assets/<name>.png (RGBA 1000x1000)
"""
import bpy, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_frame/assets'
os.makedirs(B.OUT, exist_ok=True)
PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')
IVORY, BLUSH, INK, WHITE, WARM = hexc('#FCF8F5'), hexc('#F6EAF3'), hexc('#321F35'), hexc('#FFFFFF'), hexc('#FFC27A')
FUR, FUR_L, BRICK, SKIN, SKIN2 = hexc('#B07A4A'), hexc('#E3C29B'), hexc('#9C4A34'), hexc('#E2B48F'), hexc('#8D5B3E')


def teddy():
    f, fl = mat(FUR, 0.8, coat=0.0), mat(FUR_L, 0.8)
    sph(0.85, loc=(0, 0, 0), m=f, scale=(1, 0.9, 1.1))
    sph(0.5, loc=(0, -0.55, -0.05), m=fl, scale=(1, 0.5, 1.2))
    sph(0.62, loc=(0, 0, 1.25), m=f)
    sph(0.26, loc=(0, -0.5, 1.12), m=fl, scale=(1.1, 0.8, 0.85))
    sph(0.08, loc=(0, -0.72, 1.18), m=mat(INK, 0.3))
    for s in (-1, 1):
        sph(0.22, loc=(s * 0.48, 0, 1.75), m=f)
        sph(0.13, loc=(s * 0.48, -0.1, 1.75), m=fl)
        sph(0.07, loc=(s * 0.22, -0.55, 1.38), m=mat(INK, 0.2))
        sph(0.3, loc=(s * 0.85, -0.1, 0.25), m=f, scale=(0.8, 0.8, 1.4))
        sph(0.34, loc=(s * 0.45, -0.25, -0.95), m=f, scale=(0.9, 1.2, 0.8))
    torus(0.42, 0.07, loc=(0, -0.05, 0.75), m=mat(MAG, 0.4, coat=0.4), rot=(math.radians(10), 0, 0))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-14)))


def backpack():
    body = box((1.5, 0.8, 1.9), m=mat(MAG, 0.35, coat=0.5), bw=0.3)
    box((1.1, 0.25, 0.8), loc=(0, -0.48, -0.35), m=mat(PLUM, 0.35, coat=0.5), bw=0.15)
    box((0.9, 0.04, 0.05), loc=(0, -0.62, -0.05), m=mat(WHITE, 0.3), bw=0.01)
    curve_path([(-0.4, 0.1, 0.95), (0, 0.15, 1.45), (0.4, 0.1, 0.95)], 0.07, mat(PLUM, 0.4))
    for s in (-1, 1):
        curve_path([(s * 0.45, 0.42, 0.8), (s * 0.55, 0.65, 0.0), (s * 0.45, 0.42, -0.8)], 0.08, mat(PLUM, 0.4))
    box((0.55, 0.08, 0.3), loc=(0.35, -0.42, 0.55), m=mat(ORANGE, 0.4), bw=0.05)
    sph(0.1, loc=(-0.45, -0.45, 0.6), m=mat(GREEN, 0.3))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(math.radians(8), 0, math.radians(-24)))


def puzzle():
    """A chunky jigsaw piece: rounded square, two knobs out, two sockets in."""
    m = mat(PLUM, 0.3, coat=0.6)
    base = box((2.0, 2.0, 0.4), m=m, bw=0.12)
    k1 = cyl(0.34, 0.4, loc=(0, -1.22, 0), m=m, v=48, bw=0.1)
    k2 = cyl(0.34, 0.4, loc=(1.22, 0, 0), m=m, v=48, bw=0.1)
    for (x, y) in ((0, 0.8), (-0.8, 0)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.36, depth=1.0, location=(x, y, 0), vertices=48)
        cut = act()
        md = base.modifiers.new('b', 'BOOLEAN')
        md.object, md.operation = cut, 'DIFFERENCE'
        cut.hide_render = True
        cut.hide_viewport = True
    objs = [base, k1, k2]
    group(objs, rot=(math.radians(62), 0, math.radians(18)))


def hand(m, flip=1, loc=(0, 0, 0), sleeve_col=None):
    """A clay hand reaching along +Z (flip=-1 reaches down): fuller palm, fingers together and gently curved."""
    parts = [box((1.0, 0.42, 1.05), loc=(0, 0, 0), m=m, bw=0.2)]
    for x, L in ((-0.36, 0.72), (-0.12, 0.86), (0.12, 0.82), (0.35, 0.64)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=L, location=(x, -0.04, 0.5 + L / 2), vertices=32,
                                            rotation=(math.radians(-10), 0, 0))
        f_ = act()
        bevel(f_, 0.11, 5)
        smooth(setm(f_, m))
        parts.append(f_)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.7, location=(0.6, -0.08, 0.15), rotation=(math.radians(-15), math.radians(-40), 0), vertices=32)
    t = act()
    bevel(t, 0.13, 5)
    smooth(setm(t, m))
    parts.append(t)
    parts.append(cyl(0.5, 1.1, loc=(0, 0, -1.0), m=mat(sleeve_col or PLUM, 0.45, coat=0.3), v=48, bw=0.1))
    return group(parts, rot=(0, 0, 0) if flip > 0 else (math.pi, 0, math.pi), loc=loc)


def hands():
    """'Someone to count on': one hand reaches down, one reaches up; their fingertips meet."""
    hand(mat(SKIN, 0.55, coat=0.1), 1, (0.0, 0, -1.55), MAG)
    hand(mat(SKIN2, 0.55, coat=0.1), -1, (0.05, 0.18, 1.6), PLUM)
    root = [o for o in bpy.context.scene.objects if o.type == 'EMPTY']
    group(root, rot=(0, math.radians(6), math.radians(-28)))


def door():
    """'Could you make room for fostering?': a Manchester terrace front door, open, warm light inside."""
    brick = mat(BRICK, 0.85)
    for x0, x1 in ((-2.2, -0.75), (0.75, 2.2)):
        box((x1 - x0, 0.4, 4.2), loc=((x0 + x1) / 2, 0, 2.1), m=brick, bw=0.02)
    box((1.5, 0.4, 0.9), loc=(0, 0, 3.75), m=brick, bw=0.02)
    for z in range(0, 42, 3):
        box((4.42, 0.01, 0.012), loc=(0, -0.205, z / 10), m=mat(hexc('#7E3A2A'), 0.95), bw=0)
    box((1.6, 0.45, 0.18), loc=(0, 0, 3.3), m=mat(IVORY, 0.4), bw=0.03)          # lintel
    box((1.4, 0.04, 0.45), loc=(0, -0.2, 3.03), m=mat(WARM, 0.2, emit=(WARM, 3.0)), bw=0.01)   # fanlight
    box((1.4, 0.05, 2.75), loc=(0, 0.15, 1.38), m=mat(WARM, 0.3, emit=(WARM, 4.5)), bw=0.01)   # warm hallway
    d = box((1.35, 0.1, 2.7), loc=(-0.25, -0.65, 1.38), m=mat(PLUM, 0.3, coat=0.6), bw=0.04, rot=(0, 0, math.radians(-68)))
    sph(0.06, loc=(-0.05, -1.25, 1.35), m=mat(hexc('#E2A93B'), 0.2, 0.9))
    box((1.9, 0.9, 0.2), loc=(0, -0.55, -0.1), m=mat(IVORY, 0.5), bw=0.04)       # step
    box((0.5, 0.06, 0.12), loc=(0.5, -0.24, 2.0), m=mat(hexc('#E2A93B'), 0.2, 0.9), bw=0.02)   # letterbox
    L = bpy.data.objects.new('pl', bpy.data.lights.new('pl', 'POINT'))
    L.data.energy, L.data.color = 220, (1.0, 0.75, 0.45)
    L.location = (0, -0.6, 1.5)
    bpy.context.scene.collection.objects.link(L)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(14)))


ALL = ['teddy', 'backpack', 'puzzle', 'hands', 'door']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        sc = bpy.context.scene
        sc.cycles.samples = 24 if draft else 128
        sc.render.resolution_x = sc.render.resolution_y = 1000
        globals()[n]()
        B.render(n)
