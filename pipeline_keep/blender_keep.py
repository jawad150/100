"""3D keepsakes for BMHC "What did you keep?" (rendered in colour; the reel shows them as black-and-white collage
cut-outs with a magenta accent): recipe card, cardamom pods, a little brass spoon, an envelope, an old photograph, a drawer.

Run: blender -b -P blender_keep.py -- [draft] [name ...] -> workspace_keep/assets/<name>.png (RGBA 1000x1000)
"""
import bpy, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_keep/assets'
TEX = f'{ROOT}/workspace_keep/tex'
os.makedirs(B.OUT, exist_ok=True)
PAPER, BRASS, WOOD, WOOD_D, GREENP = hexc('#F2E8D5'), hexc('#C9A04A'), hexc('#8A5A36'), hexc('#5E3B22'), hexc('#7E9A52')


def img_mat(path, rough=0.7):
    m = bpy.data.materials.new('img')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    return m


def plane(w, h, m, loc=(0, 0, 0), rot=(math.radians(90), 0, 0), thick=0.01):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = act()
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.location, o.rotation_euler = loc, rot
    s = o.modifiers.new('s', 'SOLIDIFY')
    s.thickness = thick
    return setm(o, m)


def recipe():
    p = plane(2.25, 3.0, img_mat(f'{TEX}/recipe.png'))
    sb = p.modifiers.new('b', 'SIMPLE_DEFORM')
    sb.deform_method, sb.angle, sb.deform_axis = 'BEND', math.radians(8), 'Z'
    group([p], rot=(0, math.radians(4), math.radians(-12)))


def cardamom():
    m = mat(GREENP, 0.6, coat=0.1)
    objs = []
    for i, (x, z, r) in enumerate(((-0.5, 0, 30), (0.2, 0.35, -20), (0.55, -0.25, 60))):
        o = sph(0.32, loc=(x, 0, z), m=m, scale=(0.75, 0.75, 1.35))
        o.rotation_euler = (0, math.radians(r), 0)
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0, depth=0.2, location=(x + 0.4 * math.sin(math.radians(r)), 0, z + 0.45 * math.cos(math.radians(r))),
                                        rotation=(0, math.radians(r), 0))
        setm(act(), m)
        for k in range(4):
            torus(0.31 - 0.04 * abs(k - 1.5), 0.012, loc=(x, 0, z), m=mat(hexc('#5E7A3A'), 0.7), rot=(0, math.radians(r), math.radians(k * 45)))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(20), 0, math.radians(-10)))


def spoon():
    m = mat(BRASS, 0.25, 0.95)
    sph(0.45, loc=(0, 0, 0.9), m=m, scale=(0.75, 0.25, 1.0))
    cyl(0.06, 2.0, loc=(0, 0.05, -0.4), m=m, bw=0.02, rot=(math.radians(6), 0, 0))
    sph(0.12, loc=(0, 0.1, -1.4), m=m)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(14), math.radians(28), math.radians(-30)))


def envelope():
    p = mat(PAPER, 0.7)
    box((2.6, 0.05, 1.7), m=p, bw=0.02)
    for s in (-1, 1):
        bpy.ops.mesh.primitive_plane_add(size=1)
        o = act()
        o.scale = (1.5, 1.0, 1)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.location = (s * 0.65, -0.04, 0.2)
        o.rotation_euler = (math.radians(90), 0, s * math.radians(-30))
        setm(o, mat(hexc('#E7DCC5'), 0.75))
    sph(0.18, loc=(0, -0.08, 0.05), m=mat(hexc('#B7006E'), 0.4, coat=0.5), scale=(1, 0.35, 1))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-10)))


def photo():
    box((2.2, 0.04, 2.6), m=mat(hexc('#F4F0E6'), 0.6), bw=0.02)
    plane(1.9, 1.9, img_mat(f'{TEX}/photo.png', 0.6), loc=(0, -0.03, 0.18), thick=0.002)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(8)))


def drawer():
    w = mat(WOOD, 0.55, coat=0.2)
    wd = mat(WOOD_D, 0.6)
    box((3.4, 2.4, 1.3), loc=(0, 0.7, 0.3), m=wd, bw=0.05)            # cabinet
    box((3.0, 2.0, 0.08), loc=(0, -0.6, 0.0), m=w, bw=0.02)           # drawer base (pulled out)
    for s in (-1, 1):
        box((0.08, 2.0, 0.7), loc=(s * 1.46, -0.6, 0.33), m=w, bw=0.02)
    box((3.0, 0.08, 0.7), loc=(0, 0.38, 0.33), m=w, bw=0.02)
    box((3.2, 0.12, 0.9), loc=(0, -1.62, 0.33), m=w, bw=0.05)          # front
    torus(0.18, 0.04, loc=(0, -1.72, 0.45), m=mat(BRASS, 0.25, 0.95), rot=(math.radians(90), 0, 0))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(-8), 0, math.radians(-22)))


ALL = ['recipe', 'cardamom', 'spoon', 'envelope', 'photo', 'drawer']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        sc = bpy.context.scene
        sc.cycles.samples = 24 if draft else 96
        sc.render.resolution_x = sc.render.resolution_y = 1000
        globals()[n]()
        B.render(n)
