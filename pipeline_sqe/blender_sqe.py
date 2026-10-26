"""3D props for IC London "What Is the SQE?" (Blender Cycles stills, transparent).

Usage: python3 blender_sqe.py <prop> [...]
Props: knot, letters, arch1, arch2, papers, speech, lectern, magnifier, pen, calendar, door
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_sol as BS
import blender_lo as B
from blender_lo import lin, reset, mat, box, prism, camera, look
from blender_sol import std, studio, catcher, text_obj

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_sqe'))
OUT = S + '/assets'
FONT_B = S + '/fonts/Inter-900.ttf'
FONT_S = S + '/fonts/Inter-800.ttf'
NAVY, RED, WHITE, GOLD, ICE = '#00247D', '#CF142B', '#F7F8FC', '#E3B24A', '#EEF2FB'


def setup(res, samples=48):
    reset(res, samples=samples, transparent=True)
    std()
    studio(key=900, rim=1000)


def shot(name):
    os.makedirs(OUT, exist_ok=True)
    sc = bpy.context.scene
    sc.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


def tube_curve(pts, radius, m, name='tube'):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    sp = cu.splines.new('NURBS')
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (c[0], c[1], c[2], 1)
    sp.use_endpoint_u = True
    sp.order_u = 4
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    return o


# ------------------------------------------------------------------ 1. the tangled knot of jargon
def knot():
    setup((900, 900))
    random.seed(7)
    navy = mat('navy', lin(NAVY), rough=0.3, coat=0.5)
    red = mat('red', lin(RED), rough=0.3, coat=0.5)
    white = mat('white', lin(WHITE), rough=0.35)
    for j, m in enumerate([navy, red, navy, white, red]):
        pts = []
        for i in range(26):
            a = i * 0.9 + j * 1.3
            r = 1.0 + 0.5 * random.random()
            pts.append((r * math.cos(a) * math.cos(i * 0.37 + j), r * math.sin(i * 0.5 + j * 0.7), r * math.sin(a) * 0.9))
        tube_curve(pts, 0.05, m, 'k%d' % j)
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0.4, -7.5, 1.2), (0, 0, 0))
    shot('knot')


# ------------------------------------------------------------------ 2. S Q E letters on the route line
def letters():
    setup((1000, 760))
    catcher(0.0)
    navy = mat('navy', lin(NAVY), rough=0.3, coat=0.5)
    red = mat('red', lin(RED), rough=0.3, coat=0.5)
    for j, (ch, m) in enumerate([('S', navy), ('Q', red), ('E', navy)]):
        t = text_obj(ch, 2.6, (-2.3 + j * 2.3, 0, 0), (90, 0, 0), m, font=FONT_B, extrude=0.35, bevel=0.04)
        t.data.align_y = 'BOTTOM'
        t.rotation_euler.z = math.radians([8, -4, 6][j])
    line = mat('line', lin('#FFFFFF'), rough=0.3, emit=lin('#BFD2FF'), estr=3.0)
    box((9.0, 0.12, 0.05), (0, 0, 0.025), line)
    cam = camera(lens=45)
    cam.data.dof.use_dof = False
    look(cam, (1.2, -10.5, 3.2), (0, 0, 1.1))
    shot('letters')


# ------------------------------------------------------------------ 3/4. checkpoint arches
def arch(label, name, accent):
    setup((900, 1000))
    catcher(0.0)
    navy = mat('navy', lin(NAVY), rough=0.3, coat=0.5)
    red = mat('red', lin(RED), rough=0.3, coat=0.5)
    whitem = mat('white', lin(WHITE), rough=0.3)
    acc = red if accent == 'red' else navy
    for sx in (-1.9, 1.9):
        box((0.5, 0.5, 4.2), (sx, 0, 2.1), navy, bevel=0.06)
        box((0.8, 0.8, 0.25), (sx, 0, 0.125), navy, bevel=0.05)
    beam = box((4.8, 0.6, 1.2), (0, 0, 4.6), acc, bevel=0.08)
    t = text_obj(label, 0.85, (0, -0.31, 4.6), (90, 0, 0), whitem, font=FONT_B, extrude=0.03)
    glow = mat('glow', lin('#FFFFFF'), emit=lin('#9CC0FF'), estr=6.0)
    box((3.2, 0.05, 0.04), (0, 0, 0.02), glow)
    box((0.04, 6.0, 0.04), (0, -2.0, 0.02), glow)
    cam = camera(lens=40)
    cam.data.dof.use_dof = False
    look(cam, (2.6, -10.0, 3.0), (0, 0, 2.6))
    shot(name)


def arch1():
    arch('SQE1', 'arch1', 'red')


def arch2():
    arch('SQE2', 'arch2', 'navy')


# ------------------------------------------------------------------ 5. FLK1 / FLK2 exam papers
def papers():
    setup((900, 900))
    paper = mat('paper', lin('#FBFAF6'), rough=0.8)
    navy = mat('navy', lin(NAVY), rough=0.4)
    red = mat('red', lin(RED), rough=0.4)
    grey = mat('grey', lin('#C9D1E6'), rough=0.6)
    for j, (title, dx, rz) in enumerate([('FLK1', -1.25, 8), ('FLK2', 1.25, -8)]):
        root = bpy.data.objects.new('p%d' % j, None)
        bpy.context.scene.collection.objects.link(root)
        parts = [box((2.1, 0.03, 2.9), (0, 0, 0), paper, bevel=0.01)]
        parts.append(box((2.1, 0.035, 0.42), (0, -0.002, 1.24), navy))
        parts.append(text_obj(title, 0.3, (0, -0.03, 1.24), (90, 0, 0), mat('wt%d' % j, lin(WHITE)), font=FONT_B, extrude=0.002))
        for r in range(5):
            z = 0.75 - r * 0.42
            parts.append(box((1.1, 0.032, 0.06), (0.25, -0.006, z + 0.08), grey))
            for q in range(5):
                bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.02, location=(-0.75 + q * 0.2, -0.03, z - 0.08),
                                                    rotation=(math.radians(90), 0, 0), vertices=24)
                c = bpy.context.object
                c.data.materials.append(red if q == (r * 2 + j) % 5 else grey)
                parts.append(c)
        for p_ in parts:
            p_.parent = root
        root.location = (dx, 0.2 * j, 0.1 * j)
        root.rotation_euler = (math.radians(-6), 0, math.radians(rz))
    cam = camera(lens=45)
    cam.data.dof.use_dof = False
    look(cam, (0.0, -8.2, 1.0), (0, 0, 0))
    shot('papers')


# ------------------------------------------------------------------ 6. skill icons
def icon_scene(name, build, cam_loc=(0, -6.5, 1.2), target=(0, 0, 0)):
    setup((560, 560))
    build()
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, cam_loc, target)
    shot(name)


def speech():
    def b():
        m = mat('red', lin(RED), rough=0.3, coat=0.5)
        o = box((2.4, 0.5, 1.6), (0, 0, 0.2), m, bevel=0.35)
        t = prism(0.6, 0.5, 0.6, (-0.5, 0, -0.6), m)
        t.rotation_euler = (0, math.radians(180), 0)
        w = mat('w', lin(WHITE), rough=0.3)
        for k in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(-0.6 + k * 0.6, -0.28, 0.2))
            bpy.context.object.data.materials.append(w)
    icon_scene('speech', b)


def lectern():
    def b():
        n = mat('navy', lin(NAVY), rough=0.35, coat=0.4)
        w = mat('wood', lin('#8A5A32'), rough=0.5)
        box((1.2, 0.8, 2.0), (0, 0, -0.6), n, bevel=0.05)
        top = box((1.8, 1.2, 0.12), (0, 0, 0), w, bevel=0.03)
        top.location = (0, -0.1, 0.55)
        top.rotation_euler = (math.radians(-22), 0, 0)
        box((1.6, 1.0, 0.1), (0, 0, -1.65), n, bevel=0.03)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.8, location=(0.5, 0.1, 0.95), rotation=(math.radians(-30), 0, 0))
        bpy.context.object.data.materials.append(mat('mic', lin('#2A2E38'), rough=0.3, metal=0.8))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0.5, -0.1, 1.3))
        bpy.context.object.data.materials.append(mat('red', lin(RED), rough=0.4))
    icon_scene('lectern', b, cam_loc=(1.5, -6.5, 1.6), target=(0, 0, -0.2))


def magnifier():
    def b():
        n = mat('navy', lin(NAVY), rough=0.3, coat=0.5)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.13, location=(-0.25, 0, 0.3), rotation=(math.radians(90), 0, 0))
        bpy.context.object.data.materials.append(n)
        g = mat('glass', lin('#CFE0FF'), rough=0.05, coat=1.0, emit=lin('#8FB4FF'), estr=0.35)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.06, location=(-0.25, 0, 0.3), rotation=(math.radians(90), 0, 0), vertices=64)
        bpy.context.object.data.materials.append(g)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=1.3, location=(0.75, 0, -0.75), rotation=(0, math.radians(-45), 0))
        bpy.context.object.data.materials.append(mat('red', lin(RED), rough=0.3, coat=0.5))
    icon_scene('magnifier', b)


def pen():
    def b():
        n = mat('navy', lin(NAVY), rough=0.25, coat=0.8)
        gold = mat('gold', lin(GOLD), rough=0.25, metal=1.0)
        root = bpy.data.objects.new('pen', None)
        bpy.context.scene.collection.objects.link(root)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=2.6, location=(0, 0, 0.2), vertices=48)
        a = bpy.context.object
        a.data.materials.append(n)
        bpy.ops.mesh.primitive_cone_add(radius1=0.16, radius2=0.02, depth=0.5, location=(0, 0, -1.35), vertices=48)
        c = bpy.context.object
        c.data.materials.append(gold)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.12, location=(0, 0, -0.85), vertices=48)
        d = bpy.context.object
        d.data.materials.append(gold)
        box((0.05, 0.06, 1.0), (0.2, 0, 0.9), gold).parent = root
        for o in (a, c, d):
            o.parent = root
        root.rotation_euler = (0, math.radians(-40), 0)
        paper = mat('paper', lin('#FBFAF6'), rough=0.8)
        sheet = box((2.2, 0.03, 2.8), (0, 0, 0), paper)
        sheet.location = (-0.5, 0.6, -0.1)
        for k in range(5):
            l_ = box((1.5, 0.035, 0.05), (0, 0, 0), mat('ln%d' % k, lin('#9AA6C8')))
            l_.location = (-0.6, 0.57, 0.9 - k * 0.35)
    icon_scene('pen', b, cam_loc=(0, -7.0, 0.8))


# ------------------------------------------------------------------ 7. QWE calendar
def calendar():
    setup((640, 640))
    navy = mat('navy', lin(NAVY), rough=0.35, coat=0.4)
    red = mat('red', lin(RED), rough=0.35, coat=0.4)
    paper = mat('paper', lin('#FBFAF6'), rough=0.8)
    box((2.6, 0.3, 2.9), (0, 0.15, 0), navy, bevel=0.06)
    box((2.4, 0.06, 2.3), (0, -0.04, -0.2), paper, bevel=0.02)
    box((2.4, 0.08, 0.55), (0, -0.05, 1.05), red, bevel=0.03)
    for sx in (-0.7, 0.7):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.04, location=(sx, -0.05, 1.45), rotation=(0, math.radians(90), 0))
        bpy.context.object.data.materials.append(mat('ring', lin('#C9CFDB'), rough=0.2, metal=1.0))
    text_obj('QWE', 0.32, (0, -0.1, 1.05), (90, 0, 0), mat('w', lin(WHITE)), font=FONT_B, extrude=0.003)
    text_obj('24', 1.0, (0, -0.08, -0.05), (90, 0, 0), navy, font=FONT_B, extrude=0.01)
    text_obj('MONTHS', 0.28, (0, -0.08, -0.85), (90, 0, 0), red, font=FONT_S, extrude=0.003)
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (1.2, -7.2, 1.0), (0, 0, 0))
    shot('calendar')


# ------------------------------------------------------------------ 8. door with a SOLICITOR nameplate
def door():
    setup((760, 1000))
    catcher(0.0)
    navy = mat('navy', lin(NAVY), rough=0.35, coat=0.6)
    frame = mat('frame', lin('#E9ECF4'), rough=0.4)
    gold = mat('gold', lin(GOLD), rough=0.2, metal=1.0)
    box((3.0, 0.3, 4.8), (0, 0.1, 2.4), frame, bevel=0.03)
    box((2.4, 0.2, 4.4), (0, -0.05, 2.25), navy, bevel=0.03)
    for zz in (1.2, 3.1):
        box((1.8, 0.04, 1.3), (0, -0.16, zz), mat('panel%d' % int(zz), lin('#0A2C88'), rough=0.35), bevel=0.04)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.9, -0.22, 2.1))
    bpy.context.object.data.materials.append(gold)
    box((1.6, 0.05, 0.42), (0, -0.2, 3.9), gold, bevel=0.02)
    text_obj('SOLICITOR', 0.22, (0, -0.235, 3.9), (90, 0, 0), navy, font=FONT_B, extrude=0.003)
    glow = mat('glow', lin('#FFF4DA'), emit=lin('#FFE6B0'), estr=4.0)
    box((2.45, 0.05, 0.05), (0, -0.1, 0.02), glow)
    cam = camera(lens=40)
    cam.data.dof.use_dof = False
    look(cam, (1.6, -9.0, 2.6), (0, 0, 2.3))
    shot('door')


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
