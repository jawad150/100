"""3D objects for the BMHC "Everything under one roof" bento post (glossy clay, BMHC colours, transparent PNGs):
lantern (daily prayers), rehal + open book (Qur'an classes - blank pages, no text), ball (youth & sport),
speech bubbles (Imam counselling), retro radio (Heritage Radio), map pin on a folded map (heritage tours), rings (Nikah).

Run: blender -b -P blender_bento.py -- [draft] [names] -> workspace_bmhc_posts/assets/<name>.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, box, cyl, sph, torus, hexc, group

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_bmhc_posts/assets'
os.makedirs(B.OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
DRAFT = 'draft' in argv
NAMES = [a for a in argv if a != 'draft']
MAG, TEAL, ORANGE, LIME = hexc('#E60585'), hexc('#2DC892'), hexc('#FF4200'), hexc('#69FF00')
WHITE, INK, GOLD = hexc('#F4F2EE'), hexc('#1F1F1F'), hexc('#E2B04A')


def reset():
    B.reset()
    sc = bpy.context.scene
    sc.cycles.samples = 32 if DRAFT else 128
    sc.render.resolution_x = sc.render.resolution_y = 800 if DRAFT else 1000
    w = sc.world.node_tree.nodes['Background']
    w.inputs[0].default_value = (0.85, 0.86, 0.9, 1)
    w.inputs[1].default_value = 0.45


def lantern():
    frame = mat(TEAL, 0.25, 0.6, coat=0.8)
    glass = mat(hexc('#FFD27A'), 0.1, emit=(hexc('#FFB648'), 4.0), trans=0.3)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.62, depth=1.3, location=(0, 0, 1.0))
    setm(act(), glass)
    for i in range(6):                                                   # frame ribs
        a = i * math.pi / 3
        cyl(0.05, 1.4, loc=(0.63 * math.cos(a), 0.63 * math.sin(a), 1.0), m=frame, bw=0.01)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.78, depth=0.16, location=(0, 0, 0.32))
    setm(act(), frame)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.78, depth=0.12, location=(0, 0, 1.7))
    setm(act(), frame)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.72, radius2=0.12, depth=0.7, location=(0, 0, 2.1))
    setm(act(), frame)
    sph(0.12, loc=(0, 0, 2.5), m=frame)
    torus(0.2, 0.05, loc=(0, 0, 2.72), m=frame, rot=(math.radians(90), 0, 0))
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.5, depth=0.2, location=(0, 0, 0.14))
    setm(act(), frame)
    for i in range(6):                                                   # little arch windows (ink) on each face
        a = i * math.pi / 3 + math.pi / 6
        b = box((0.18, 0.02, 0.5), loc=(0.55 * math.cos(a), 0.55 * math.sin(a), 1.0), m=mat(INK, 0.4), bw=0.0)
        b.rotation_euler.z = a + math.pi / 2
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(0, 0, math.radians(10)))


def rehal():
    wood = mat(WHITE, 0.3, coat=0.6)
    for s_ in (-1, 1):                                                   # the crossed stand (legs splay left/right)
        b = box((0.1, 1.1, 1.7), loc=(0, 0, 0.75), m=wood, bw=0.04)
        b.rotation_euler = (0, s_ * math.radians(38), 0)
    cover = mat(LIME, 0.3, coat=0.7)
    page = mat(hexc('#FBF7EE'), 0.65, coat=0.0)
    for s_ in (-1, 1):                                                   # an open book: curved pages rising from the spine
        for layer, (m, th, lift) in enumerate(((cover, 0.05, 0.0), (page, 0.03, 0.05))):
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=4, size=1)
            o = act()
            bm = bmesh.new()
            bm.from_mesh(o.data)
            for v in bm.verts:
                u, w = v.co.x + 0.5, v.co.y + 0.5
                x = s_ * u * (1.15 - 0.05 * layer)
                z = 1.45 + lift + 0.55 * math.sin(min(1, u * 1.6) * math.pi / 2) - 0.25 * u
                v.co = Vector((x, (w - 0.5) * (1.5 - 0.08 * layer), z))
            bm.to_mesh(o.data)
            bm.free()
            sol = o.modifiers.new('s', 'SOLIDIFY')
            sol.thickness = th
            bpy.ops.object.shade_smooth()
            setm(o, m)
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(math.radians(-8), 0, math.radians(-14)))


def ball():
    sph(1.0, loc=(0, 0, 1.0), m=mat(ORANGE, 0.35, coat=0.6))
    seam = mat(INK, 0.4)
    torus(1.0, 0.035, loc=(0, 0, 1.0), m=seam, rot=(math.radians(90), 0, 0))
    torus(1.0, 0.035, loc=(0, 0, 1.0), m=seam, rot=(0, math.radians(90), 0))
    torus(0.75, 0.035, loc=(0.62, 0, 1.0), m=seam, rot=(0, math.radians(90), 0))
    torus(0.75, 0.035, loc=(-0.62, 0, 1.0), m=seam, rot=(0, math.radians(90), 0))
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(math.radians(20), math.radians(25), 0))


def bubble(cx, cz, w, h, m, tail_left, y=0.0):
    b = box((w, 0.35, h), loc=(cx, y, cz), m=m, bw=min(w, h) * 0.45)
    for md in b.modifiers:
        if md.type == 'BEVEL':
            md.segments = 10
    tx = cx + (-w * 0.25 if tail_left else w * 0.25)
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.22, depth=0.35, location=(tx + (-0.08 if tail_left else 0.08), y, cz - h / 2 - 0.08),
                                    rotation=(math.radians(90), 0, math.radians(180)))
    t = act()
    t.rotation_euler = (math.radians(90), math.radians(30 if tail_left else -30), 0)
    setm(t, m)
    for i in range(3):                                                   # three dots
        sph(0.09, loc=(cx - 0.3 + i * 0.3, y - 0.2, cz), m=mat(MAG if m.name != 'mag' else WHITE, 0.3, coat=0.6))


def bubbles():
    bubble(-0.35, 1.35, 1.7, 0.95, mat(WHITE, 0.25, coat=0.8), True, 0.25)
    m2 = mat(INK, 0.25, coat=0.8)
    bubble(0.45, 0.35, 1.5, 0.85, m2, False, -0.25)
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(0, 0, math.radians(-12)))


def radio():
    body = mat(ORANGE, 0.3, coat=0.7)
    box((2.4, 0.9, 1.5), loc=(0, 0, 0.85), m=body, bw=0.25)
    grille = mat(INK, 0.5)
    cyl(0.5, 0.06, loc=(-0.55, -0.46, 0.85), m=grille, rot=(math.radians(90), 0, 0), bw=0.01)
    for r in (0.15, 0.27, 0.39):
        torus(r, 0.025, loc=(-0.55, -0.5, 0.85), m=mat(hexc('#3A3A3A'), 0.4), rot=(math.radians(90), 0, 0))
    box((0.85, 0.06, 0.3), loc=(0.5, -0.46, 1.1), m=mat(hexc('#FFF3D6'), 0.2, emit=(hexc('#FFE3A0'), 1.5)), bw=0.02)
    for x in (0.25, 0.75):
        cyl(0.13, 0.12, loc=(x, -0.48, 0.55), m=mat(WHITE, 0.25, coat=0.8), rot=(math.radians(90), 0, 0), bw=0.03)
    ant = cyl(0.04, 1.8, loc=(0.85, 0, 2.2), m=mat(hexc('#C9C9C9'), 0.2, 1.0), rot=(0, math.radians(-25), 0))
    bpy.context.view_layer.update()
    tip = ant.matrix_world @ Vector((0, 0, 0.9))
    sph(0.07, loc=tuple(tip), m=mat(hexc('#C9C9C9'), 0.2, 1.0))
    torus(0.55, 0.07, loc=(0, 0, 1.6), m=mat(INK, 0.4), rot=(math.radians(90), 0, 0))
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(0, 0, math.radians(18)))


def mappin():
    paper = mat(WHITE, 0.5, coat=0.2)
    for i in range(4):                                                   # folded map: zig-zag panels
        b = box((0.8, 2.0, 0.03), loc=(-1.2 + i * 0.78, 0, 0.12), m=paper, bw=0.01)
        b.rotation_euler = (0, math.radians(12 if i % 2 else -12), 0)
    for i in range(3):
        box((0.04, 1.6, 0.012), loc=(-1.0 + i * 0.8, 0.0, 0.17), m=mat(TEAL, 0.4), bw=0.0).rotation_euler = (0, 0, math.radians(20 * (i - 1)))
    pinm = mat(MAG, 0.22, coat=0.9)
    sph(0.55, loc=(0.2, 0, 1.75), m=pinm)
    bpy.ops.mesh.primitive_cone_add(radius1=0.48, radius2=0.02, depth=1.1, location=(0.2, 0, 0.95), rotation=(math.radians(180), 0, 0))
    setm(act(), pinm)
    sph(0.22, loc=(0.2, -0.42, 1.8), m=mat(WHITE, 0.3, coat=0.8), scale=(1, 0.5, 1))
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(0, 0, math.radians(-20)))


def rings():
    g = mat(GOLD, 0.18, 1.0, coat=0.4)
    torus(0.75, 0.13, loc=(-0.35, 0, 1.0), m=g, rot=(math.radians(80), math.radians(15), 0))
    torus(0.75, 0.13, loc=(0.35, 0, 1.05), m=g, rot=(math.radians(80), math.radians(-35), math.radians(40)))
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.22, radius2=0.0, depth=0.3, location=(-0.35, 0, 1.92))
    setm(act(), mat(hexc('#EAF6FF'), 0.02, trans=0.9))
    group([o for o in bpy.context.scene.objects if o.type == 'MESH'], rot=(0, 0, 0))


JOBS = {'lantern': lantern, 'rehal': rehal, 'ball': ball, 'bubbles': bubbles, 'radio': radio, 'mappin': mappin, 'rings': rings}
for name, fn in JOBS.items():
    if NAMES and name not in NAMES:
        continue
    reset()
    fn()
    B.render(name)
