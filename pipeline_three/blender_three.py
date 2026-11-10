"""3D sticker objects for Organic Fostering "Three of Me". Glossy clay in the Organic Fostering palette; the white die-cut
sticker border is added in the edit.

Run: blender -b -P blender_three.py -- [name ...]  -> workspace_three/assets/<name>.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = OUT = f'{ROOT}/workspace_three/assets'
os.makedirs(OUT, exist_ok=True)

PURPLE, ORANGE, PLUM, LEAF = hexc('#B7006E'), hexc('#FF6411'), hexc('#5B174F'), hexc('#64A60B')
PEACH, LAV, IVORY, WHITE = hexc('#FFD4BA'), hexc('#F3DDEB'), hexc('#FCF8F5'), hexc('#F7F7F5')
GREY, NAVY, YELLOW, GOLD = hexc('#8E8A93'), hexc('#3A2A4F'), hexc('#FFC93C'), hexc('#E2A93B')


def clock():
    body = cyl(1.0, 0.38, m=mat(PURPLE, 0.28), rot=(math.radians(90), 0, 0), v=96, bw=0.12)
    face = cyl(0.84, 0.05, loc=(0, -0.2, 0), m=mat(IVORY, 0.35), rot=(math.radians(90), 0, 0), v=96, bw=0.01)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        sph(0.05 if i % 3 else 0.075, loc=(0.68 * math.sin(a), -0.24, 0.68 * math.cos(a)), m=mat(PLUM, 0.4))
    box((0.09, 0.04, 0.5), loc=(0, -0.26, 0.22), m=mat(PLUM, 0.35), bw=0.02)
    box((0.07, 0.04, 0.62), loc=(0.27, -0.27, -0.08), m=mat(ORANGE, 0.35), bw=0.02, rot=(0, math.radians(-120), 0))
    sph(0.08, loc=(0, -0.29, 0), m=mat(ORANGE, 0.3))
    for sx in (-0.62, 0.62):
        sph(0.24, loc=(sx, 0, 0.95), m=mat(ORANGE, 0.28))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-16)))


def briefcase():
    body = box((2.4, 0.8, 1.6), m=mat(PLUM, 0.32), bw=0.18)
    flap = box((2.42, 0.82, 0.12), loc=(0, 0, 0.35), m=mat(hexc('#4A1240'), 0.35), bw=0.04)
    lock = box((0.4, 0.12, 0.28), loc=(0, -0.44, 0.35), m=mat(GOLD, 0.25, 0.9), bw=0.04)
    hnd = curve_path([(-0.45, 0, 0.8), (-0.35, 0, 1.15), (0.35, 0, 1.15), (0.45, 0, 0.8)], 0.08, mat(ORANGE, 0.3))
    group([body, flap, lock, hnd], rot=(0, 0, math.radians(-18)))


def house():
    walls = box((1.8, 1.6, 1.4), m=mat(IVORY, 0.4), bw=0.06)
    bpy.ops.mesh.primitive_cone_add(radius1=1.55, depth=1.0, vertices=4, location=(0, 0, 1.2), rotation=(0, 0, math.radians(45)))
    roof = act()
    roof.scale = (1.0, 0.9, 1)
    bpy.ops.object.transform_apply(scale=True)
    bevel(roof, 0.06)
    setm(roof, mat(PURPLE, 0.3))
    door = box((0.45, 0.1, 0.8), loc=(0.35, -0.8, -0.3), m=mat(ORANGE, 0.3), bw=0.04)
    win = box((0.45, 0.1, 0.42), loc=(-0.4, -0.8, 0.1), m=mat(hexc('#FFD27A'), 0.3, emit=(hexc('#FFC45A'), 1.2)), bw=0.03)
    hb = text('♥', 0.5, (-0.4, -0.86, 0.1), mat(PURPLE, 0.3), ext=0.03, font='Nunito-900') if False else None
    group([walls, roof, door, win], rot=(0, 0, math.radians(-22)))


def nostamp():
    base = box((2.3, 0.5, 1.25), m=mat(hexc('#E23B4B'), 0.3), bw=0.3)
    t = text('NO', 0.95, (0, -0.32, -0.02), mat(WHITE, 0.3), ext=0.06, font='Nunito-900')
    group([base, t], rot=(0, 0, math.radians(-10)))


def question():
    t = text('?', 2.4, (0, 0, 0), mat(ORANGE, 0.25), ext=0.28, font='Nunito-900')
    t.data.bevel_depth = 0.05
    group([t], rot=(0, 0, math.radians(-14)))


def possibly():
    """A balanced see-saw (possibly: it depends)."""
    m = mat(PURPLE, 0.28)
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, depth=0.8, vertices=3, location=(0, 0, -0.4), rotation=(math.radians(90), 0, 0))
    tri = smooth(setm(act(), mat(PLUM, 0.3)))
    bevel(tri, 0.06)
    beam = box((3.0, 0.5, 0.16), loc=(0, 0, 0.05), m=mat(ORANGE, 0.3), bw=0.06, rot=(0, math.radians(-6), 0))
    a = box((0.6, 0.6, 0.6), loc=(-1.1, 0, 0.5), m=m, bw=0.12, rot=(0, math.radians(-6), 0))
    b = sph(0.36, loc=(1.15, 0, 0.42), m=mat(LEAF, 0.3))
    group([tri, beam, a, b], rot=(0, 0, math.radians(-12)))


def calendar():
    body = box((2.0, 0.3, 2.0), m=mat(IVORY, 0.4), bw=0.12)
    head = box((2.02, 0.32, 0.5), loc=(0, 0, 0.78), m=mat(PURPLE, 0.3), bw=0.1)
    for sx in (-0.5, 0.5):
        torus(0.14, 0.05, loc=(sx, 0, 1.05), m=mat(GOLD, 0.25, 0.9), rot=(0, math.radians(90), 0))
    for r in range(3):
        for k in range(4):
            col = ORANGE if (r, k) == (1, 2) else LAV
            box((0.32, 0.06, 0.26), loc=(-0.6 + k * 0.4, -0.17, 0.25 - r * 0.38), m=mat(col, 0.4), bw=0.03)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-14)))


def network():
    """Three little people linked by a ring (a support network)."""
    cols = (PURPLE, ORANGE, LEAF)
    objs = []
    pos = [(-1.15, -0.2, 0), (1.15, -0.2, 0), (0, 0.5, 0.25)]
    for (x, y, z), col in zip(pos, cols):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.8, location=(x, y, z - 0.35), vertices=48)
        bdy = act()
        sub = bdy.modifiers.new('s', 'SUBSURF')
        sub.levels = sub.render_levels = 2
        smooth(setm(bdy, mat(col, 0.3)))
        objs += [bdy, sph(0.3, loc=(x, y, z + 0.38), m=mat(col, 0.3))]
    ring = torus(1.25, 0.06, loc=(0, 0.15, -0.6), m=mat(GOLD, 0.2, 0.9), rot=(math.radians(-8), 0, 0))
    group(objs + [ring], rot=(0, 0, math.radians(-10)))


def heart():
    B.heart()
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            setm(o, mat(PURPLE, 0.22))


def gradcap():
    m = mat(PLUM, 0.3)
    top = box((2.2, 2.2, 0.12), loc=(0, 0, 0.5), m=m, bw=0.03, rot=(0, 0, math.radians(45)))
    base = cyl(0.75, 0.6, loc=(0, 0, 0.15), m=m, bw=0.05)
    btn = sph(0.1, loc=(0, 0, 0.6), m=mat(ORANGE, 0.3))
    tas = curve_path([(0, 0, 0.6), (0.7, -0.4, 0.58), (1.05, -0.55, 0.2)], 0.035, mat(ORANGE, 0.3))
    knob = sph(0.12, loc=(1.05, -0.55, 0.15), m=mat(ORANGE, 0.3))
    group([top, base, btn, tas, knob], rot=(math.radians(14), 0, math.radians(-10)))


def backpack():
    body = box((1.6, 0.9, 2.0), m=mat(ORANGE, 0.3), bw=0.4)
    pocket = box((1.1, 0.25, 0.8), loc=(0, -0.5, -0.4), m=mat(PURPLE, 0.3), bw=0.15)
    flap = box((1.62, 0.92, 0.6), loc=(0, -0.02, 0.62), m=mat(hexc('#E0520A'), 0.3), bw=0.25)
    hnd = torus(0.25, 0.06, loc=(0, 0, 1.08), m=mat(PLUM, 0.35), rot=(math.radians(90), 0, 0))
    group([body, pocket, flap, hnd], rot=(0, 0, math.radians(-20)))


def clipboard():
    board = box((1.8, 0.14, 2.4), m=mat(hexc('#B07A4A'), 0.45), bw=0.1)
    paper = box((1.5, 0.04, 2.0), loc=(0, -0.09, -0.08), m=mat(WHITE, 0.5), bw=0.01)
    clip = box((0.8, 0.22, 0.3), loc=(0, -0.05, 1.12), m=mat(hexc('#C9CCCC'), 0.3, 1.0), bw=0.06)
    objs = [board, paper, clip]
    for i in range(4):
        tick_ = box((0.18, 0.04, 0.18), loc=(-0.5, -0.12, 0.5 - i * 0.4), m=mat(LEAF if i < 3 else LAV, 0.4), bw=0.03)
        line = box((0.8, 0.03, 0.07), loc=(0.15, -0.12, 0.5 - i * 0.4), m=mat(hexc('#A7A0AA'), 0.5), bw=0.01)
        objs += [tick_, line]
    group(objs, rot=(math.radians(-8), 0, math.radians(-14)))


def magnifier():
    rim = torus(0.75, 0.13, m=mat(PURPLE, 0.25), rot=(math.radians(90), 0, 0))
    glass = cyl(0.68, 0.06, m=mat(hexc('#DDEFFF', 0.4), 0.02, trans=1.0, coat=0), rot=(math.radians(90), 0, 0), bw=0)
    hnd = cyl(0.16, 1.2, loc=(0.92, 0, -0.92), m=mat(ORANGE, 0.3), rot=(0, math.radians(-45), 0), bw=0.06)
    group([rim, glass, hnd], rot=(0, 0, math.radians(-14)))


def mug():
    cup = cyl(0.7, 1.3, loc=(0, 0, 0.6), m=mat(GREY, 0.35), v=96, bw=0.08)
    liquid = cyl(0.62, 0.05, loc=(0, 0, 1.2), m=mat(hexc('#5A3016'), 0.15), bw=0)
    handle = torus(0.38, 0.1, loc=(0.78, 0, 0.62), m=mat(GREY, 0.35), rot=(math.radians(90), 0, 0))
    band = torus(0.705, 0.04, loc=(0, 0, 0.35), m=mat(hexc('#6E6876'), 0.35))
    group([cup, liquid, handle, band], rot=(0, 0, math.radians(-30)))


def sun():
    core = sph(0.8, m=mat(YELLOW, 0.25, emit=(YELLOW, 0.3)), scale=(1, 0.6, 1))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        bpy.ops.mesh.primitive_cone_add(radius1=0.18, depth=0.5, location=(1.15 * math.sin(a), 0, 1.15 * math.cos(a)),
                                        rotation=(0, a, 0), vertices=24)
        smooth(setm(act(), mat(ORANGE, 0.3)))
    for sx in (-0.28, 0.28):
        sph(0.08, loc=(sx, -0.47, 0.15), m=mat(PLUM, 0.3))
    curve_path([(-0.3, -0.48, -0.15), (0, -0.5, -0.32), (0.3, -0.48, -0.15)], 0.04, mat(PLUM, 0.3))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(0, 0, math.radians(-8)))


def phone():
    body = box((1.25, 0.16, 2.4), m=mat(PLUM, 0.3), bw=0.18)
    scr = box((1.08, 0.04, 2.15), loc=(0, -0.08, 0), m=mat(hexc('#FFF6FA'), 0.2, emit=(hexc('#FFF6FA'), 0.4)), bw=0.12)
    b1 = box((0.75, 0.04, 0.3), loc=(-0.1, -0.11, 0.55), m=mat(LAV, 0.3), bw=0.12)
    b2 = box((0.75, 0.04, 0.3), loc=(0.1, -0.11, 0.1), m=mat(PURPLE, 0.3, emit=(PURPLE, 0.3)), bw=0.12)
    b3 = box((0.55, 0.04, 0.3), loc=(-0.2, -0.11, -0.35), m=mat(LAV, 0.3), bw=0.12)
    btn = box((0.85, 0.04, 0.24), loc=(0, -0.11, -0.8), m=mat(ORANGE, 0.3, emit=(ORANGE, 0.4)), bw=0.1)
    group([body, scr, b1, b2, b3, btn], rot=(math.radians(-6), 0, math.radians(-18)))


TOK = dict(clock=clock, briefcase=briefcase, house=house, nostamp=nostamp, question=question, possibly=possibly, calendar=calendar,
           network=network, heart=heart, gradcap=gradcap, backpack=backpack, clipboard=clipboard, magnifier=magnifier, mug=mug,
           sun=sun, phone=phone)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for n in (argv or list(TOK)):
        reset()
        TOK[n]()
        B.render(n)
