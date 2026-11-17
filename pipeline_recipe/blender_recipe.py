"""3D pop-up objects for Organic Fostering "The Recipe That Wasn't on the Menu" (glossy clay, brand palette).

Run: blender -b -P blender_recipe.py -- [name ...]  -> workspace_recipe/assets/<name>.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_recipe/assets'
os.makedirs(B.OUT, exist_ok=True)

PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')
IVORY, PEACH, BLUSH, LEAFT = hexc('#FCF8F5'), hexc('#FFD4BA'), hexc('#F6EAF3'), hexc('#E8F3D8')
STEEL, DARK, GOLD, SOIL, CREAM = hexc('#BFC3C9'), hexc('#2B2430'), hexc('#E2A93B'), hexc('#5A3A22'), hexc('#F3E6CC')


def pot():
    """The familiar pot (made a hundred times)."""
    body = cyl(1.0, 1.0, loc=(0, 0, 0), m=mat(ORANGE, 0.25, coat=0.6), v=96, bw=0.12)
    inside = cyl(0.9, 0.06, loc=(0, 0, 0.47), m=mat(hexc('#B5401C'), 0.15), v=96, bw=0)
    for k in range(5):
        a = k / 5 * 2 * math.pi
        sph(0.16, loc=(0.48 * math.cos(a), 0.48 * math.sin(a), 0.52), m=mat(hexc('#7A3B1E'), 0.4))
    rim = torus(1.0, 0.06, loc=(0, 0, 0.5), m=mat(hexc('#E0560E'), 0.25))
    for sx in (-1, 1):
        torus(0.2, 0.06, loc=(sx * 1.08, 0, 0.25), m=mat(PLUM, 0.3), rot=(math.radians(90), 0, 0))
    lid_handle = None
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(-8), 0, math.radians(-10)))


def recipecard():
    """A handwritten recipe card on a little stand (the reveal)."""
    card = box((2.2, 0.06, 1.5), m=mat(CREAM, 0.6, coat=0.1), bw=0.04)
    head = box((2.2, 0.065, 0.32), loc=(0, -0.002, 0.59), m=mat(PLUM, 0.4), bw=0.02)
    t = text('Recipe', 0.3, (-0.5, -0.05, 0.56), mat(IVORY, 0.4), ext=0.008, font='Caveat-700')
    for i in range(5):
        w = 1.6 - 0.25 * (i % 3)
        box((w, 0.02, 0.035), loc=(-0.85 + w / 2, -0.04, 0.22 - i * 0.2), m=mat(hexc('#B7A9A0'), 0.5), bw=0.005)
    for sx in (0.75, 0.89):
        sph(0.1, loc=(sx, -0.07, -0.47), m=mat(MAG, 0.3), scale=(1, 0.4, 1))
    bpy.ops.mesh.primitive_cone_add(radius1=0.16, depth=0.2, location=(0.82, -0.07, -0.6), rotation=(math.pi, 0, 0), vertices=32)
    hp = smooth(setm(act(), mat(MAG, 0.3)))
    hp.scale = (1, 0.4, 1)
    leaf = sph(0.13, loc=(0.82, -0.06, 0.2), m=mat(GREEN, 0.3), scale=(1, 0.3, 0.55))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'FONT')]
    group(objs, rot=(math.radians(-12), 0, math.radians(-14)))


def spicejar():
    """The different ingredient: a glass jar of orange spice with a cork."""
    glass = cyl(0.55, 1.4, loc=(0, 0, 0), m=mat(hexc('#FFFFFF'), 0.03, trans=1.0, coat=0), v=96, bw=0.1)
    spice = cyl(0.5, 0.95, loc=(0, 0, -0.2), m=mat(ORANGE, 0.85), v=96, bw=0.05)
    cork = cyl(0.42, 0.35, loc=(0, 0, 0.85), m=mat(hexc('#C49A6C'), 0.8), v=64, bw=0.05)
    label = cyl(0.56, 0.22, loc=(0, 0, 0.05), m=mat(IVORY, 0.6), v=96, bw=0)
    md = label.modifiers.new('s', 'SOLIDIFY')
    md.thickness = 0.01
    band = torus(0.56, 0.025, loc=(0, 0, 0.2), m=mat(PLUM, 0.4))
    group([glass, spice, cork, label, band], rot=(0, 0, math.radians(-14)))


def bowl():
    """A familiar flavour: a full serving bowl."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, segments=96, ring_count=48)
    b = act()
    bm = bmesh.new()
    bm.from_mesh(b.data)
    for v in [v for v in bm.verts if v.co.z > 0.25]:
        bm.verts.remove(v)
    bm.to_mesh(b.data)
    bm.free()
    s = b.modifiers.new('s', 'SOLIDIFY')
    s.thickness = 0.08
    smooth(setm(b, mat(MAG, 0.25, coat=0.7)))
    food = sph(1.05, loc=(0, 0, 0.1), m=mat(hexc('#E9A23B'), 0.6), scale=(1, 1, 0.25))
    for k in range(7):
        a = k / 7 * 2 * math.pi
        sph(0.14, loc=(0.6 * math.cos(a), 0.6 * math.sin(a), 0.32), m=mat(GREEN if k % 2 else ORANGE, 0.4))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(28), 0, 0))


def cutter():
    """'Become like you': a cookie cutter (the same shape every time)."""
    pts = []
    for i in range(10):
        a = i / 10 * 2 * math.pi
        r = 1.0 if i % 2 == 0 else 0.5
        pts.append((r * math.sin(a), r * math.cos(a), 0))
    cu = bpy.data.curves.new('c', 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (q[0], q[1], q[2], 1)
    sp.use_cyclic_u = True
    cu.extrude = 0.25
    cu.bevel_depth = 0.035
    o = bpy.data.objects.new('cut', cu)
    bpy.context.scene.collection.objects.link(o)
    cu.materials.append(mat(STEEL, 0.2, 1.0))
    group([o], rot=(math.radians(62), 0, math.radians(-10)))


def seedling():
    """Room to grow, roots to keep: a sprout above a crumbly soil clump, fine roots fanning beneath."""
    sm = mat(SOIL, 0.95)
    nt = sm.node_tree
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 14
    bmp = nt.nodes.new('ShaderNodeBump')
    bmp.inputs['Strength'].default_value = 0.6
    nt.links.new(nz.outputs['Fac'], bmp.inputs['Height'])
    nt.links.new(bmp.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
    soil = sph(0.8, loc=(0, 0, -0.45), m=sm, scale=(1.25, 1.25, 0.55))
    for k in range(9):
        a = k / 9 * 2 * math.pi
        sph(0.2, loc=(0.85 * math.cos(a), 0.85 * math.sin(a), -0.55), m=sm, scale=(1, 1, 0.6))
    rm = mat(hexc('#EAD7B8'), 0.6)
    import random
    random.seed(4)
    for k in range(14):
        a = k / 14 * 2 * math.pi
        L = random.uniform(0.9, 1.6)
        pts = [(0.3 * math.cos(a), 0.3 * math.sin(a), -0.7)]
        for j in range(1, 5):
            u = j / 4
            pts.append((math.cos(a + 0.3 * math.sin(j)) * (0.3 + 0.55 * u), math.sin(a + 0.3 * math.sin(j)) * (0.3 + 0.55 * u), -0.7 - L * u))
        curve_path(pts, 0.016 + 0.01 * (k % 2), rm)
    stem = curve_path([(0, 0, -0.2), (0.06, 0, 0.45), (-0.03, 0, 1.0)], 0.06, mat(GREEN, 0.4))
    lm = mat(GREEN, 0.3)
    for sx in (-1, 1):
        l = sph(0.42, loc=(sx * 0.42, 0, 1.12), m=lm, scale=(1, 0.16, 0.48))
        l.rotation_euler = (0, math.radians(sx * -40), 0)
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(math.radians(-6), 0, math.radians(-10)))


def lantern():
    """Faith (any faith): a warm glowing lantern."""
    gm = mat(GOLD, 0.25, 0.9)
    base = cyl(0.6, 0.15, loc=(0, 0, -0.9), m=gm, bw=0.04, v=8)
    top = cyl(0.62, 0.15, loc=(0, 0, 0.75), m=gm, bw=0.04, v=8)
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, depth=0.6, location=(0, 0, 1.12), vertices=8)
    roof = setm(act(), gm)
    glass = cyl(0.52, 1.5, loc=(0, 0, -0.08), m=mat(hexc('#FFD27A'), 0.1, emit=(hexc('#FFB43A'), 3.0)), bw=0.02, v=8)
    for k in range(8):
        a = k / 8 * 2 * math.pi + math.pi / 8
        cyl(0.03, 1.55, loc=(0.56 * math.cos(a), 0.56 * math.sin(a), -0.08), m=gm, bw=0)
    ring = torus(0.18, 0.04, loc=(0, 0, 1.5), m=gm, rot=(math.radians(90), 0, 0))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-10)))


def culture():
    """Culture: a patterned plate with a geometric border."""
    plate = cyl(1.2, 0.12, m=mat(IVORY, 0.25, coat=0.8), v=96, bw=0.06)
    for i, (r, col) in enumerate(((1.05, PLUM), (0.75, ORANGE), (0.45, MAG))):
        torus(r, 0.04, loc=(0, 0, 0.07), m=mat(col, 0.35))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        sph(0.07, loc=(0.9 * math.cos(a), 0.9 * math.sin(a), 0.08), m=mat(GREEN if k % 2 else MAG, 0.35), scale=(1, 1, 0.5))
        sph(0.06, loc=(0.6 * math.cos(a + 0.26), 0.6 * math.sin(a + 0.26), 0.08), m=mat(PLUM, 0.35), scale=(1, 1, 0.5))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(58), 0, 0))


def identity():
    """Identity: a heart with a fingerprint swirl."""
    B.heart()
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            setm(o, mat(MAG, 0.22))
    for i in range(5):
        r = 0.12 + i * 0.1
        curve_path([(r * math.cos(a), -0.38, 0.05 + r * 0.8 * math.sin(a)) for a in [math.radians(d) for d in range(20, 340, 40)]],
                   0.018, mat(IVORY, 0.4))


TOK = dict(pot=pot, recipecard=recipecard, spicejar=spicejar, bowl=bowl, cutter=cutter, seedling=seedling, lantern=lantern,
           culture=culture, identity=identity)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for n in (argv or list(TOK)):
        reset()
        TOK[n]()
        B.render(n)
