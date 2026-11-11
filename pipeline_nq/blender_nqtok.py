"""3D pop-up objects for Organic Fostering "No Qualification Needed" (glossy clay, Organic Fostering palette).

Run: blender -b -P blender_nqtok.py -- [name ...]  -> workspace_nq/assets/<name>.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_nq/assets'
os.makedirs(B.OUT, exist_ok=True)

PURPLE, ORANGE, PLUM, LEAF = hexc('#B7006E'), hexc('#FF6411'), hexc('#5B174F'), hexc('#64A60B')
PEACH, LAV, IVORY, WHITE = hexc('#FFD4BA'), hexc('#F3DDEB'), hexc('#FCF8F5'), hexc('#F7F7F5')
GOLD, TEAL, SKY = hexc('#E2A93B'), hexc('#1E9AA0'), hexc('#7CC6E8')


def umbrella():
    """Why children enter care: shelter."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.3, location=(0, 0, 0), segments=8, ring_count=16)
    can = act()
    bm = bmesh.new()
    bm.from_mesh(can.data)
    for v in [v for v in bm.verts if v.co.z < 0.15]:
        bm.verts.remove(v)
    for v in bm.verts:
        v.co.z = (v.co.z - 0.15) * 0.62 + 0.15
    bm.to_mesh(can.data)
    bm.free()
    sol = can.modifiers.new('s', 'SOLIDIFY')
    sol.thickness = 0.04
    sub = can.modifiers.new('ss', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    smooth(setm(can, mat(PURPLE, 0.3)))
    pole = cyl(0.045, 1.25, loc=(0, 0, -0.35), m=mat(PLUM, 0.3), bw=0)
    hnd = curve_path([(0, 0, -0.95), (0, 0, -1.1), (0.18, 0, -1.18), (0.32, 0, -1.05)], 0.06, mat(ORANGE, 0.3))
    tip = sph(0.07, loc=(0, 0, 0.9), m=mat(ORANGE, 0.3))
    heart = B.heart if False else None
    group([can, pole, hnd, tip], rot=(math.radians(-8), math.radians(-10), math.radians(-14)))


def shield():
    """Safeguarding and professional boundaries."""
    bm = bmesh.new()
    pts = []
    for i in range(60):
        t = i / 59
        x = -1 + 2 * t
        if abs(x) < 1:
            pass
    outline = []
    for i in range(41):
        a = -1 + i / 20
        outline.append((a * 1.0, 0, 1.0 - 0.08 * a * a))
    for i in range(1, 40):
        u = i / 40
        x = 1.0 - u * 1.0
        z = 1.0 - 0.08 - (u ** 1.6) * 2.3 if False else None
    # simple heater shield: top edge, two curved sides meeting at the bottom point
    side = []
    for i in range(31):
        u = i / 30
        side.append((1.0 * (1 - u ** 2.6), 0, 0.92 - 2.0 * u))
    loop = outline + side[1:] + [(-x, y, z) for (x, y, z) in reversed(side[1:-1])]
    vs = [bm.verts.new(p) for p in loop]
    bm.faces.new(vs)
    me = bpy.data.meshes.new('sh')
    bm.to_mesh(me)
    o = bpy.data.objects.new('sh', me)
    bpy.context.scene.collection.objects.link(o)
    s = o.modifiers.new('s', 'SOLIDIFY')
    s.thickness, s.offset = 0.35, 0
    b = o.modifiers.new('b', 'BEVEL')
    b.width, b.segments = 0.1, 6
    setm(o, mat(PURPLE, 0.25))
    smooth(o)
    tick = curve_path([(-0.42, -0.2, -0.1), (-0.1, -0.2, -0.45), (0.48, -0.2, 0.32)], 0.1, mat(WHITE, 0.3))
    group([o, tick], rot=(0, 0, math.radians(-14)))


def tree():
    """Working with birth families: a family tree."""
    trunk = cyl(0.16, 1.2, loc=(0, 0, -0.6), m=mat(hexc('#8A5A36'), 0.5), bw=0.04)
    br1 = cyl(0.07, 0.7, loc=(-0.25, 0, 0.0), m=mat(hexc('#8A5A36'), 0.5), rot=(0, math.radians(-40), 0), bw=0.02)
    br2 = cyl(0.07, 0.7, loc=(0.25, 0, 0.05), m=mat(hexc('#8A5A36'), 0.5), rot=(0, math.radians(40), 0), bw=0.02)
    objs = [trunk, br1, br2]
    for (x, z, r, col) in ((0, 0.75, 0.62, LEAF), (-0.62, 0.35, 0.48, hexc('#7BBF2A')), (0.62, 0.38, 0.48, hexc('#7BBF2A')),
                           (-0.3, 1.15, 0.4, hexc('#8ACB3B')), (0.35, 1.12, 0.42, hexc('#8ACB3B'))):
        objs.append(sph(r, loc=(x, 0, z), m=mat(col, 0.35)))
    for (x, z, col) in ((-0.55, 0.5, PURPLE), (0.5, 0.55, ORANGE), (0.05, 1.0, PURPLE), (-0.2, 0.65, ORANGE)):
        objs.append(sph(0.11, loc=(x, -0.55, z), m=mat(col, 0.3)))
    group(objs, rot=(0, 0, math.radians(-10)))


def heartplaster():
    """How trauma can influence behaviour: a heart with a plaster on it."""
    B.heart()
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            setm(o, mat(PURPLE, 0.22))
    p = box((1.3, 0.1, 0.38), loc=(0.05, -0.4, 0.25), m=mat(PEACH, 0.5), bw=0.16, rot=(0, math.radians(32), 0))
    pad = box((0.42, 0.04, 0.26), loc=(0.05, -0.46, 0.25), m=mat(hexc('#F2B79A'), 0.6), bw=0.05, rot=(0, math.radians(32), 0))


def padlock():
    """Recording, confidentiality and teamwork."""
    body = box((1.5, 0.7, 1.2), loc=(0, 0, -0.3), m=mat(ORANGE, 0.28), bw=0.22)
    shackle = torus(0.48, 0.12, loc=(0, 0, 0.32), m=mat(hexc('#C9CCD1'), 0.25, 1.0), rot=(math.radians(90), 0, 0))
    bm_cut = box((1.2, 1.2, 0.6), loc=(0, 0, -0.05), m=None, bw=0)
    md = shackle.modifiers.new('cut', 'BOOLEAN')
    md.object = bm_cut
    md.operation = 'DIFFERENCE'
    bm_cut.hide_render = True
    legs = [cyl(0.12, 0.35, loc=(sx, 0, 0.32), m=mat(hexc('#C9CCD1'), 0.25, 1.0), bw=0) for sx in (-0.48, 0.48)]
    hole = cyl(0.13, 0.1, loc=(0, -0.36, -0.2), m=mat(PLUM, 0.3), rot=(math.radians(90), 0, 0), bw=0.02)
    slot = box((0.1, 0.1, 0.3), loc=(0, -0.36, -0.42), m=mat(PLUM, 0.3), bw=0.02)
    group([body, shackle, hole, slot] + legs, rot=(0, 0, math.radians(-16)))


def books():
    """Before you can foster, you'll need to study…"""
    cols = (PLUM, ORANGE, PURPLE)
    objs = []
    for i, col in enumerate(cols):
        b_ = box((2.0 - i * 0.15, 1.3, 0.34), loc=(0.05 * (i % 2), 0, i * 0.36), m=mat(col, 0.35), bw=0.05,
                 rot=(0, 0, math.radians((-6, 5, -3)[i])))
        pg = box((1.9 - i * 0.15, 1.22, 0.26), loc=(0.05 * (i % 2) + 0.06, 0, i * 0.36), m=mat(IVORY, 0.7), bw=0.01,
                 rot=(0, 0, math.radians((-6, 5, -3)[i])))
        objs += [b_, pg]
    group(objs, rot=(math.radians(-18), 0, math.radians(-20)))


def certificate():
    """A rolled certificate with a ribbon (a qualification)."""
    roll = cyl(0.32, 2.2, m=mat(IVORY, 0.5), rot=(0, math.radians(90), 0), bw=0.05)
    ribbon = torus(0.34, 0.06, m=mat(PURPLE, 0.3), rot=(0, math.radians(90), 0))
    bow1 = curve_path([(0, -0.3, -0.1), (0.15, -0.5, -0.5), (0.05, -0.55, -0.8)], 0.06, mat(PURPLE, 0.3))
    bow2 = curve_path([(0, -0.3, -0.1), (-0.15, -0.5, -0.5), (-0.1, -0.55, -0.8)], 0.06, mat(PURPLE, 0.3))
    seal = cyl(0.2, 0.06, loc=(0, -0.36, -0.08), m=mat(GOLD, 0.25, 0.9), rot=(math.radians(90), 0, 0), bw=0.02)
    group([roll, ribbon, bow1, bow2, seal], rot=(0, 0, math.radians(-18)))


def laptop():
    """Online learning."""
    base = box((2.2, 1.5, 0.1), loc=(0, 0, 0), m=mat(hexc('#B9B6BF'), 0.3, 0.8), bw=0.04)
    keys = box((1.8, 0.8, 0.02), loc=(0, 0.15, 0.06), m=mat(hexc('#3A3540'), 0.5), bw=0.01)
    lid = box((2.2, 0.08, 1.45), loc=(0, 0.78, 0.72), m=mat(hexc('#B9B6BF'), 0.3, 0.8), bw=0.04, rot=(math.radians(-12), 0, 0))
    scr = box((2.0, 0.02, 1.25), loc=(0, 0.72, 0.72), m=mat(hexc('#FFF4F9'), 0.2, emit=(hexc('#FFF4F9'), 0.6)), bw=0.01, rot=(math.radians(-12), 0, 0))
    play = sph(0.24, loc=(0, 0.68, 0.74), m=mat(PURPLE, 0.3, emit=(PURPLE, 0.3)), scale=(1, 0.3, 1))
    group([base, keys, lid, scr, play], rot=(math.radians(10), 0, math.radians(-22)))


def bubbles():
    """Group discussion: three chat bubbles."""
    objs = []
    for (x, z, s_, col) in ((-0.6, 0.45, 1.0, PURPLE), (0.75, 0.15, 0.8, ORANGE), (-0.05, -0.65, 0.75, LEAF)):
        objs.append(box((1.5 * s_, 0.45 * s_, 0.95 * s_), loc=(x, 0, z), m=mat(col, 0.28), bw=0.35 * s_))
        for k in range(3):
            objs.append(sph(0.09 * s_, loc=(x + (k - 1) * 0.32 * s_, -0.24 * s_, z), m=mat(WHITE, 0.3)))
    group(objs, rot=(0, 0, math.radians(-10)))


def workshop():
    """Live workshops: a little easel board with a chart."""
    m = mat(hexc('#8A5A36'), 0.5)
    legs = [cyl(0.05, 2.4, loc=(sx, 0.1, -0.2), m=m, rot=(math.radians(8), math.radians(-sx * 12), 0), bw=0) for sx in (-0.7, 0.7)]
    back = cyl(0.05, 2.3, loc=(0, 0.55, -0.25), m=m, rot=(math.radians(-18), 0, 0), bw=0)
    board = box((1.9, 0.08, 1.4), loc=(0, -0.05, 0.35), m=mat(WHITE, 0.4), bw=0.04)
    bars = [box((0.25, 0.04, h), loc=(-0.5 + i * 0.4, -0.12, 0.05 + h / 2), m=mat(c, 0.35), bw=0.02)
            for i, (h, c) in enumerate(((0.35, LAV), (0.6, PURPLE), (0.85, ORANGE)))]
    group(legs + [back, board] + bars, rot=(0, 0, math.radians(-14)))


TOK = dict(umbrella=umbrella, shield=shield, tree=tree, heartplaster=heartplaster, padlock=padlock, books=books,
           certificate=certificate, laptop=laptop, bubbles=bubbles, workshop=workshop)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for n in (argv or list(TOK)):
        reset()
        TOK[n]()
        B.render(n)
