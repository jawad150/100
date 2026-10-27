"""3D props for BMHC "The First Word" (Blender Cycles stills, transparent), in BMHC's palette.

Usage: python3 blender_bmhc.py <prop> [...]
Props: quill, book, astrolabe, arch, star
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_lo as B
from blender_lo import lin, reset, mat, box, prism, camera, look
from blender_sol import std, studio, catcher, text_obj

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_bmhc'))
OUT = S + '/assets'
GREEN_D, IVORY, TEAL, GOLD, MAG, ORANGE, GREEN = '#122F2A', '#EFEEEA', '#09999C', '#DD9933', '#DB225E', '#F26721', '#76BF43'


def setup(res, samples=48):
    reset(res, samples=samples, transparent=True)
    std()
    studio(world_col='#2A3B36', strength=0.4, key=900, rim=900)


def shot(name):
    os.makedirs(OUT, exist_ok=True)
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


def gold_mat(name='gold'):
    return mat(name, lin(GOLD), rough=0.22, metal=1.0)


# ------------------------------------------------------------------ gold quill pen
def quill():
    setup((640, 640))
    gold = gold_mat()
    ivory = mat('feather', lin('#F4EFE4'), rough=0.6)
    root = bpy.data.objects.new('quill', None)
    bpy.context.scene.collection.objects.link(root)
    # feather vane: a flattened, tapered shape from a scaled sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0.6), segments=48, ring_count=24)
    v = bpy.context.object
    v.scale = (0.38, 0.05, 1.7)
    bpy.ops.object.shade_smooth()
    v.data.materials.append(ivory)
    v.parent = root
    for k in range(9):                                       # barbs as gold lines
        z = -0.6 + k * 0.32
        box((0.6 - abs(k - 4) * 0.05, 0.06, 0.012), (0, -0.04, z), gold).parent = root
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=3.8, location=(0, -0.05, 0.25), vertices=24)
    sh = bpy.context.object
    sh.data.materials.append(gold)
    sh.parent = root
    bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.0, depth=0.45, location=(0, -0.05, -1.85), rotation=(math.radians(180), 0, 0), vertices=24)
    nib = bpy.context.object
    nib.data.materials.append(gold)
    nib.parent = root
    root.rotation_euler = (math.radians(8), math.radians(-35), math.radians(18))
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0, -9.0, 0.3), (0, 0, 0.1))
    shot('quill')


# ------------------------------------------------------------------ open book with light rising from it
def book():
    setup((760, 640))
    cover = mat('cover', lin(GREEN_D), rough=0.45, coat=0.4)
    pages = mat('pages', lin('#F7F2E6'), rough=0.85)
    gold = gold_mat()
    glow = mat('glow', lin('#FFF6DE'), emit=lin('#FFE9B0'), estr=3.0)
    for side in (-1, 1):
        bm = bmesh.new()
        n = 24
        verts_top, verts_bot = [], []
        for i in range(n + 1):
            u = i / n
            x = side * (0.05 + 1.8 * u)
            z = 0.25 * math.sin(math.pi * u * 0.9) * (1 - u * 0.3) + 0.05
            verts_top.append(bm.verts.new((x, -1.2, z)))
            verts_bot.append(bm.verts.new((x, 1.2, z)))
        for i in range(n):
            f = [verts_top[i], verts_top[i + 1], verts_bot[i + 1], verts_bot[i]]
            bm.faces.new(f if side > 0 else f[::-1])
        me = bpy.data.meshes.new('page%d' % side)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new('page%d' % side, me)
        bpy.context.scene.collection.objects.link(o)
        sol = o.modifiers.new('sol', 'SOLIDIFY')
        sol.thickness = 0.16
        o.data.materials.append(pages)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.shade_smooth()
        o.select_set(False)
        box((1.95, 2.6, 0.05), (side * 0.98, 0, -0.05), cover, bevel=0.02)
        for k in range(7):
            l_ = box((1.1, 0.04, 0.008), (0, 0, 0), mat('ln%d%d' % (side, k), lin('#C9BFA8')))
            l_.location = (side * 1.0, -0.8 + k * 0.26, 0.24 + 0.05 * math.sin(k))
    box((0.08, 2.62, 0.1), (0, 0, -0.03), gold)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.8))
    l = bpy.context.object
    l.data.energy = 250
    l.data.color = (1.0, 0.85, 0.55)
    cam = camera(lens=45)
    cam.data.dof.use_dof = False
    look(cam, (0, -6.6, 4.0), (0, 0, 0.4))
    shot('book')


# ------------------------------------------------------------------ brass astrolabe
def astrolabe():
    setup((640, 640))
    brass = mat('brass', lin('#C8962F'), rough=0.3, metal=1.0)
    dark = mat('dark', lin('#7A5A1E'), rough=0.4, metal=1.0)
    teal = mat('teal', lin(TEAL), rough=0.3, metal=0.6)
    root = bpy.data.objects.new('astro', None)
    bpy.context.scene.collection.objects.link(root)

    def ring(r, w, m, loc=(0, 0, 0)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=w, location=loc, rotation=(math.radians(90), 0, 0),
                                         major_segments=96, minor_segments=12)
        o = bpy.context.object
        o.data.materials.append(m)
        o.parent = root
        return o
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=0.1, location=(0, 0.05, 0), rotation=(math.radians(90), 0, 0), vertices=96)
    p = bpy.context.object
    p.data.materials.append(dark)
    p.parent = root
    ring(1.65, 0.07, brass)
    ring(1.25, 0.03, brass, (0, -0.02, 0))
    ring(0.8, 0.03, teal, (0, -0.04, 0.25))
    for k in range(24):
        a = k / 24 * 2 * math.pi
        t = box((0.03, 0.04, 0.18 if k % 2 else 0.28), (0, 0, 0), brass)
        t.location = (1.45 * math.cos(a), -0.06, 1.45 * math.sin(a))
        t.rotation_euler = (0, -a + math.pi / 2, 0)
        t.parent = root
    rule = box((3.0, 0.05, 0.08), (0, 0, 0), brass, bevel=0.01)
    rule.location = (0, -0.1, 0)
    rule.rotation_euler = (0, math.radians(30), 0)
    rule.parent = root
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.05, location=(0, 0, 1.9), rotation=(0, 0, 0))
    h = bpy.context.object
    h.data.materials.append(brass)
    h.parent = root
    root.rotation_euler = (math.radians(10), 0, math.radians(-22))
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0, -8.6, 0.6), (0, 0, 0.2))
    shot('astrolabe')


# ------------------------------------------------------------------ horseshoe arch (al-Qarawiyyin)
def arch():
    setup((640, 760))
    catcher(0.0)
    ivory = mat('ivory', lin('#EDE6D6'), rough=0.6)
    teal = mat('teal', lin(TEAL), rough=0.4)
    gold = gold_mat()
    # wall with a horseshoe opening: boolean a cylinder + box out of a slab
    wall = box((3.6, 0.5, 4.6), (0, 0, 2.3), ivory, bevel=0.02)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.05, depth=1.2, location=(0, 0, 2.7), rotation=(math.radians(90), 0, 0), vertices=96)
    cut1 = bpy.context.object
    cut2 = box((1.6, 1.2, 2.2), (0, 0, 1.1), ivory)
    for cut in (cut1, cut2):
        m = wall.modifiers.new('b', 'BOOLEAN')
        m.object = cut
        m.operation = 'DIFFERENCE'
        cut.hide_render = True
    bpy.ops.mesh.primitive_torus_add(major_radius=1.1, minor_radius=0.07, location=(0, -0.28, 2.7), rotation=(math.radians(90), 0, 0), major_segments=96)
    bpy.context.object.data.materials.append(teal)
    box((3.8, 0.6, 0.2), (0, 0, 4.7), teal, bevel=0.03)
    for k in range(7):
        box((0.3, 0.62, 0.3), (-1.65 + k * 0.55, 0, 4.95), gold, bevel=0.04)
    glow = mat('glow', lin('#FFF4DA'), emit=lin('#FFE3A6'), estr=2.0)
    box((1.6, 0.05, 2.2), (0, 0.3, 1.1), glow)
    cam = camera(lens=42)
    cam.data.dof.use_dof = False
    look(cam, (1.8, -9.0, 2.6), (0, 0, 2.4))
    shot('arch')


# ------------------------------------------------------------------ eight-pointed star (two overlapped squares)
def star():
    setup((760, 760))
    gold = gold_mat()
    teal = mat('teal', lin(TEAL), rough=0.3, coat=0.6)
    green = mat('green', lin(GREEN_D), rough=0.4, coat=0.4)
    for rz, m in ((0, gold), (45, gold)):
        o = box((2.6, 0.18, 2.6), (0, 0, 0), m, bevel=0.06)
        o.rotation_euler = (0, math.radians(rz), 0)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.05, depth=0.26, location=(0, -0.02, 0), rotation=(math.radians(90), 0, 0), vertices=96)
    bpy.context.object.data.materials.append(mat('green2', lin('#1E5A50'), rough=0.3, coat=0.6))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.05, location=(0, -0.17, 0), rotation=(math.radians(90), 0, 0), major_segments=96)
    bpy.context.object.data.materials.append(teal)
    for k in range(8):                                       # glowing points: four lit (teal), four waiting (soft)
        a = k / 8 * 2 * math.pi + math.pi / 8
        lit = k % 2 == 0
        m = mat('pt%d' % k, lin('#FFFFFF' if lit else '#9AA8A4'), emit=lin('#7FE6E8' if lit else '#3A4A47'), estr=6.0 if lit else 0.6)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(1.62 * math.cos(a), -0.2, 1.62 * math.sin(a)))
        bpy.context.object.data.materials.append(m)
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (1.2, -8.4, 1.6), (0, 0, 0))
    shot('star')


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
