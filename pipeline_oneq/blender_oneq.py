"""3D objects for Organic Fostering "One question is enough" (glossy clay; deep plum, warm ivory, magenta accent).

Run: blender -b -P blender_oneq.py -- [draft] [name ...]  -> workspace_oneq/assets/<name>.png (RGBA 900x900)
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_oneq/assets'
os.makedirs(B.OUT, exist_ok=True)

PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')
IVORY, BLUSH, INK, WHITE = hexc('#FCF8F5'), hexc('#F6EAF3'), hexc('#321F35'), hexc('#FFFFFF')
BRASS, LILAC, WARM = hexc('#E2A93B'), hexc('#CDB8D6'), hexc('#FFC27A')


def key():
    """'Can I foster if I rent?': a brass house key with a heart-shaped bow and an ivory house fob."""
    br = mat(BRASS, 0.22, 0.95)
    for s in (-1, 1):
        sph(0.42, loc=(s * 0.3, 0, 1.55), m=br, scale=(1, 0.35, 1))
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0, depth=0.8, location=(0, 0, 1.05), rotation=(math.pi, 0, 0), vertices=4)
    o = act()
    o.scale = (1, 0.24, 1)
    bpy.ops.object.transform_apply(scale=True)
    setm(o, br)
    torus(0.16, 0.06, loc=(0, -0.02, 1.55), m=mat(PLUM, 0.3), rot=(math.radians(90), 0, 0))
    cyl(0.1, 2.0, loc=(0, 0, -0.05), m=br, bw=0.02)
    for z, w in ((-0.6, 0.38), (-0.85, 0.28), (-1.0, 0.42)):
        box((w, 0.16, 0.14), loc=(w / 2, 0, z), m=br, bw=0.02)
    # house fob on a ring
    torus(0.28, 0.04, loc=(-0.55, 0, 2.05), m=mat(hexc('#BFC3C9'), 0.2, 1.0), rot=(math.radians(90), 0, math.radians(20)))
    hb = box((0.7, 0.22, 0.55), loc=(-1.0, 0, 2.55), m=mat(IVORY, 0.35, coat=0.4), bw=0.06)
    for s in (-1, 1):
        box((0.52, 0.26, 0.09), loc=(-1.0 + s * 0.2, 0, 2.97), m=mat(MAG, 0.3, coat=0.5), bw=0.03, rot=(0, s * math.radians(38), 0))
    box((0.16, 0.24, 0.26), loc=(-1.0, -0.02, 2.4), m=mat(PLUM, 0.3), bw=0.02)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-12)))


def calendar():
    """'How would fostering fit around work?': a desk calendar with a week planner and a small clock."""
    base = box((2.5, 0.45, 2.1), loc=(0, 0.1, 0), m=mat(IVORY, 0.45, coat=0.3), bw=0.1, rot=(math.radians(-10), 0, 0))
    box((2.52, 0.47, 0.5), loc=(0, 0.02, 0.95), m=mat(PLUM, 0.3, coat=0.6), bw=0.1, rot=(math.radians(-10), 0, 0))
    for k in range(4):
        torus(0.1, 0.035, loc=(-0.9 + k * 0.6, -0.1, 1.2), m=mat(BRASS, 0.2, 0.9), rot=(0, math.radians(90), 0))
    cols = (LILAC, LILAC, MAG, LILAC, GREEN, LILAC, LILAC, LILAC, ORANGE, LILAC, LILAC, LILAC)
    for i in range(12):
        x = -0.85 + (i % 4) * 0.57
        z = 0.45 - (i // 4) * 0.45
        box((0.42, 0.06, 0.3), loc=(x, -0.18 - 0.08 * (0.45 - z), z), m=mat(cols[i], 0.4, emit=(cols[i], 0.2) if cols[i] != LILAC else None),
            bw=0.04, rot=(math.radians(-10), 0, 0))
    cl = cyl(0.42, 0.22, loc=(1.15, -0.55, -0.85), m=mat(MAG, 0.28, coat=0.6), rot=(math.radians(80), 0, 0), v=64, bw=0.05)
    cyl(0.34, 0.05, loc=(1.15, -0.67, -0.83), m=mat(IVORY, 0.3), rot=(math.radians(80), 0, 0), v=64, bw=0)
    box((0.04, 0.03, 0.22), loc=(1.15, -0.71, -0.75), m=mat(INK, 0.3), bw=0)
    box((0.16, 0.03, 0.04), loc=(1.22, -0.71, -0.84), m=mat(INK, 0.3), bw=0)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-16)))


def phone():
    """'Who can I call if I need support?': a phone with a call bubble and a heart."""
    body = box((1.5, 0.16, 3.0), m=mat(PLUM, 0.25, coat=0.7), bw=0.2)
    box((1.34, 0.05, 2.8), loc=(0, -0.08, 0), m=mat(INK, 0.15, coat=0.8), bw=0.15)
    # call screen
    cyl(0.32, 0.04, loc=(0, -0.12, 0.6), m=mat(BLUSH, 0.3, emit=(BLUSH, 0.4)), rot=(math.radians(90), 0, 0), v=64, bw=0)
    for s, col in ((-1, MAG), (1, GREEN)):
        cyl(0.16, 0.05, loc=(s * 0.38, -0.12, -0.95), m=mat(col, 0.3, emit=(col, 0.8)), rot=(math.radians(90), 0, 0), v=48, bw=0)
    for k in range(3):
        torus(0.42 + k * 0.22, 0.03, loc=(0.95, -0.1, 1.25), m=mat(MAG, 0.3, emit=(MAG, 0.6)), rot=(math.radians(90), 0, 0))
    # heart
    hm = mat(MAG, 0.25, coat=0.6)
    for s in (-1, 1):
        sph(0.22, loc=(s * 0.16, -0.25, 0.62), m=hm, scale=(1, 0.6, 1))
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0, depth=0.42, location=(0, -0.25, 0.42), rotation=(math.pi, 0, 0), vertices=32)
    o = act()
    o.scale = (1, 0.45, 1)
    bpy.ops.object.transform_apply(scale=True)
    smooth(setm(o, hm))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(6), 0, math.radians(-18)))


def bubble():
    """The speech bubble all three questions slide into (ivory, magenta accent)."""
    b = box((3.0, 0.6, 2.0), loc=(0, 0, 0), m=mat(IVORY, 0.35, coat=0.6), bw=0.55)
    bpy.ops.mesh.primitive_cone_add(radius1=0.42, radius2=0, depth=0.8, location=(-0.85, 0, -1.25), rotation=(0, math.radians(200), 0), vertices=32)
    smooth(setm(act(), mat(IVORY, 0.35, coat=0.6)))
    box((3.04, 0.62, 0.16), loc=(0, 0, -0.55), m=mat(MAG, 0.3, coat=0.5), bw=0.06)
    t = text('?', 1.15, (0.0, -0.32, 0.2), mat(PLUM, 0.3), ext=0.08, font='Nunito-900')
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'FONT')]
    group(objs, rot=(0, 0, math.radians(-14)))


def magnifier():
    """The magnifying glass that reads the headline."""
    torus(0.85, 0.12, loc=(0, 0, 0.6), m=mat(PLUM, 0.25, coat=0.7), rot=(math.radians(90), 0, 0))
    box((0.3, 0.3, 1.5), loc=(0.95, 0, -0.75), m=mat(MAG, 0.3, coat=0.6), bw=0.12, rot=(0, math.radians(-38), 0))
    torus(0.16, 0.05, loc=(0.58, 0, -0.25), m=mat(BRASS, 0.2, 0.9), rot=(0, math.radians(52), 0))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-10)))


def qmark():
    """A chunky question mark."""
    text('?', 3.0, (0, 0, 0), mat(MAG, 0.28, coat=0.6), rot=(math.radians(90), 0, 0), ext=0.25, font='Nunito-900')
    objs = [o for o in bpy.context.scene.objects if o.type == 'FONT']
    group(objs, rot=(0, 0, math.radians(-18)))


ALL = ['key', 'calendar', 'phone', 'bubble', 'magnifier', 'qmark']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        bpy.context.scene.cycles.samples = 24 if draft else 96
        globals()[n]()
        B.render(n)
