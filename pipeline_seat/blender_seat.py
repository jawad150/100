"""3D BMHC hall chair (red velvet seat, gold frame - like the chairs in BMHC's own iftar footage) for the carousel
"I saved you a seat." Two angles: 'chair_note' (3/4 view, pulled out, paper note on the seat) and 'chair_back'
(reverse angle, from inside the circle).

Run: blender -b -P blender_seat.py -- [draft] [name ...] -> workspace_seat/assets/<name>.png (RGBA 1100x1100)
"""
import bpy, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_seat/assets'
TEX = f'{ROOT}/workspace_seat/tex'
os.makedirs(B.OUT, exist_ok=True)
RED, RED_D, GOLD = hexc('#7A0D22'), hexc('#5A0A19'), hexc('#D4A53C')


def velvet(col):
    m = mat(col, 0.75, coat=0.0)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Sheen Weight'].default_value = 0.35
    b.inputs['Sheen Tint'].default_value = (1.0, 0.6, 0.7, 1)
    return m


def img_mat(path):
    m = bpy.data.materials.new('img')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.7
    return m


def chair(note=True):
    g = mat(GOLD, 0.22, 0.95)
    seat = box((1.6, 1.5, 0.28), loc=(0, 0, 1.55), m=velvet(RED), bw=0.12)
    box((1.66, 1.56, 0.08), loc=(0, 0, 1.39), m=g, bw=0.03)
    for x in (-0.74, 0.74):
        for y in (-0.68, 0.68):
            cyl(0.05, 1.4, loc=(x, y, 0.68), m=g, bw=0.01, rot=(math.radians(-3 if y < 0 else 3), math.radians(3 if x > 0 else -3), 0))
    for x in (-0.74, 0.74):                                     # back uprights
        cyl(0.05, 1.9, loc=(x, 0.74, 2.45), m=g, bw=0.01, rot=(math.radians(-8), 0, 0))
    bk = box((1.36, 0.22, 1.25), loc=(0, 0.82, 2.6), m=velvet(RED), bw=0.12, rot=(math.radians(-8), 0, 0))
    curve_path([(-0.74, 0.86, 3.3), (0, 0.9, 3.55), (0.74, 0.86, 3.3)], 0.055, g)
    for y in (-0.68, 0.68):
        cyl(0.03, 1.48, loc=(0, y, 0.42), m=g, bw=0, rot=(0, math.radians(90), 0))
    if note:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        p = act()
        p.scale = (0.98, 0.64, 1)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        p.location = (0.04, -0.12, 1.705)
        p.rotation_euler = (0, 0, math.radians(-10))
        sol = p.modifiers.new('s', 'SOLIDIFY')
        sol.thickness = 0.008
        setm(p, img_mat(f'{TEX}/note.png'))
    return [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]


def chair_note():
    objs = chair(True)
    group(objs, rot=(0, 0, math.radians(-28)))
    cam = bpy.context.scene.camera
    B.frame_all()
    # look down a little more at the seat so the note reads
    cam.rotation_euler = (math.radians(58), 0, 0)


def chair_back():
    objs = chair(False)
    group(objs, rot=(0, 0, math.radians(180 - 24)))


ALL = ['chair_note', 'chair_back']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        sc = bpy.context.scene
        sc.cycles.samples = 24 if draft else 128
        sc.render.resolution_x = sc.render.resolution_y = 1100
        globals()[n]()
        if n == 'chair_note':
            from mathutils import Vector
            bpy.context.view_layer.update()
            cam = sc.camera
            # re-fit distance for the steeper angle
            pts = [o.matrix_world @ Vector(c) for o in sc.objects if o.type in ('MESH', 'CURVE') for c in o.bound_box]
            lo = Vector([min(p[i] for p in pts) for i in range(3)])
            hi = Vector([max(p[i] for p in pts) for i in range(3)])
            ctr = (lo + hi) / 2
            rad = (hi - lo).length / 2
            d = rad / math.tan(cam.data.angle / 2) * 1.08
            fwd = Vector((0, math.sin(math.radians(58)), -math.cos(math.radians(58))))
            cam.location = ctr - fwd * d
            sc.render.filepath = f'{B.OUT}/{n}.png'
            bpy.ops.render.render(write_still=True)
            print('rendered', n, flush=True)
        else:
            B.render(n)
