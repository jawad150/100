"""Floating 3D props for the OF fridge poster: crayons, a star magnet, a heart magnet, letter magnets (brand colours).
Run: blender -b -P blender_props.py  -> workspace_fridge/props/<name>.png (RGBA)
"""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, cyl, sph, hexc, reset, group

B.OUT = os.path.join(HERE, '..', 'workspace_fridge', 'props')
os.makedirs(B.OUT, exist_ok=True)
PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')


def crayon(col):
    m = mat(col, 0.35, coat=0.3)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.28, depth=2.6, location=(0, 0, 0))
    setm(act(), m)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.28, radius2=0.08, depth=0.55, location=(0, 0, 1.575))
    setm(act(), m)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.295, depth=1.7, location=(0, 0, -0.25))
    setm(act(), mat(hexc('#F4ECE0'), 0.6, coat=0.0))                 # paper wrapper
    for z in (-0.95, 0.45):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.3, depth=0.1, location=(0, 0, z))
        setm(act(), m)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(18), math.radians(55), math.radians(12)))


def star():
    bpy.ops.curve.primitive_bezier_circle_add(radius=1)
    bpy.ops.object.delete()
    import bmesh
    me = bpy.data.meshes.new('star')
    bm = bmesh.new()
    pts = []
    for i in range(10):
        r = 1.0 if i % 2 == 0 else 0.45
        a = math.pi / 2 + i * math.pi / 5
        pts.append(bm.verts.new((r * math.cos(a), r * math.sin(a), 0)))
    bm.faces.new(pts)
    bm.to_mesh(me)
    o = bpy.data.objects.new('star', me)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    sol = o.modifiers.new('s', 'SOLIDIFY')
    sol.thickness = 0.3
    bv = o.modifiers.new('b', 'BEVEL')
    bv.width, bv.segments = 0.09, 6
    setm(o, mat(ORANGE, 0.2, coat=1.0))
    group([o], rot=(math.radians(70), math.radians(15), math.radians(-20)))


def heart():
    import bmesh
    me = bpy.data.meshes.new('heart')
    bm = bmesh.new()
    vs = []
    for t in [i * 2 * math.pi / 64 for i in range(64)]:
        x = 16 * math.sin(t) ** 3 / 16
        z = (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16
        vs.append(bm.verts.new((x, 0, z)))
    bm.faces.new(vs)
    bm.to_mesh(me)
    o = bpy.data.objects.new('heart', me)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    sol = o.modifiers.new('s', 'SOLIDIFY')
    sol.thickness = 0.35
    bv = o.modifiers.new('b', 'BEVEL')
    bv.width, bv.segments = 0.14, 8
    bpy.ops.object.shade_smooth()
    setm(o, mat(MAG, 0.18, coat=1.0))
    group([o], rot=(0, math.radians(-14), math.radians(22)))


def letter(ch, col):
    bpy.ops.object.text_add()
    t = act()
    t.data.body = ch
    t.data.size = 2.0
    t.data.extrude = 0.18
    t.data.bevel_depth = 0.06
    t.data.align_x = t.data.align_y = 'CENTER'
    setm(t, mat(col, 0.2, coat=0.9))
    bpy.ops.object.convert(target='MESH')
    group([act()], rot=(math.radians(75), math.radians(10), math.radians(-25)))


import sys as _s
ONLY = _s.argv[_s.argv.index('--') + 1:] if '--' in _s.argv else []
JOBS = {'crayon_orange': lambda: crayon(ORANGE), 'crayon_green': lambda: crayon(GREEN), 'crayon_magenta': lambda: crayon(MAG),
        'star': star, 'heart': heart, 'letter_b': lambda: letter('b', GREEN), 'letter_o': lambda: letter('O', PLUM)}
for name, fn in JOBS.items():
    if ONLY and name not in ONLY:
        continue
    reset()
    sc = bpy.context.scene
    sc.cycles.samples = 64
    sc.render.resolution_x = sc.render.resolution_y = 700
    fn()
    B.render(name)
