"""3D paper aeroplane (OF orange, folded paper, glossy-clay light) for the OF "Safe place to land" carousel.
Pointing right (+x in the image) so the carousel can turn it along its flight path.
Run: blender -b -P blender_land.py -- [draft] -> workspace_land/assets/plane.png"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, hexc

ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_land/assets'
os.makedirs(OUT, exist_ok=True)
DRAFT = 'draft' in sys.argv

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32 if DRAFT else 160
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.render.film_transparent = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.95, 0.95, 0.97, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.3

# a classic dart: nose at +x, two wings folding down from the spine, a keel underneath
L, S, K = 3.0, 1.15, 0.35
verts = [(L, 0, 0),                      # 0 nose
         (-L * 0.55, 0, 0),              # 1 spine tail
         (-L * 0.62, S, 0.18),           # 2 left wing tip (tail)
         (-L * 0.62, -S, 0.18),          # 3 right wing tip
         (-L * 0.5, 0, -K),              # 4 keel bottom tail
         (L * 0.35, 0, -K * 0.25)]       # 5 keel bottom front
faces = [(0, 1, 2), (0, 3, 1), (0, 5, 4, 1)]
me = bpy.data.meshes.new('plane')
me.from_pydata(verts, [], faces)
o = bpy.data.objects.new('plane', me)
sc.collection.objects.link(o)
sol = o.modifiers.new('s', 'SOLIDIFY')
sol.thickness = 0.03
bv = o.modifiers.new('b', 'BEVEL')
bv.width, bv.segments = 0.015, 2
paper = mat(hexc('#FF6411'), 0.45, coat=0.25)
b = paper.node_tree.nodes['Principled BSDF']
b.inputs['Subsurface Weight'].default_value = 0.1
setm(o, paper)
# a fold crease line on each wing (slightly darker strip)
for s in (1, -1):
    me2 = bpy.data.meshes.new('crease')
    me2.from_pydata([(L * 0.95, 0.0, 0.003), (-L * 0.6, s * 0.55, 0.1), (-L * 0.6, s * 0.6, 0.11)], [], [(0, 1, 2)])
    c = bpy.data.objects.new('crease', me2)
    sc.collection.objects.link(c)
    setm(c, mat(hexc('#E04E05'), 0.5))
o.rotation_euler = (math.radians(-10), math.radians(-6), math.radians(-22))
for cobj in [x for x in sc.objects if x.name.startswith('crease')]:
    cobj.parent = o

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 55
cam.location = (0.6, -10.5, 9.0)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
for loc, en, sz in (((-5, -6, 8), 650, 5), ((6, -3, 4), 220, 4), ((0, 6, 6), 300, 4)):
    Lt = bpy.data.objects.new('L', bpy.data.lights.new('L', 'AREA'))
    Lt.data.energy, Lt.data.size = en, sz
    Lt.location = loc
    Lt.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(Lt)
sc.render.filepath = f'{OUT}/plane.png'
bpy.ops.render.render(write_still=True)
print('rendered plane', flush=True)
