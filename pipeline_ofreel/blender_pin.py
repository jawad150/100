"""Giant 3D map pin for the OF reel (FOOH beat): glossy plum pin, white face disc for the OF emblem (added in 2D).
Run: blender -b -P blender_pin.py -- [draft] -> workspace_ofreel/assets/pin.png (+ pin_face.json: face centre/radius)"""
import bpy, sys, os, math, json
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, cyl, sph, hexc

ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_ofreel/assets'
os.makedirs(OUT, exist_ok=True)
DRAFT = 'draft' in sys.argv

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 32 if DRAFT else 160
sc.cycles.use_denoising = True
RX, RY = 1000, 1300
sc.render.resolution_x, sc.render.resolution_y = RX, RY
sc.render.film_transparent = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (1.0, 0.9, 0.8, 1)                # warm golden-hour fill
w.node_tree.nodes['Background'].inputs[1].default_value = 0.5

plum = mat(hexc('#5B174F'), 0.18, coat=1.0)
head = sph(1.0, loc=(0, 0, 3.0), m=plum)
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.86, radius2=0.0, depth=2.6, location=(0, 0, 1.55), rotation=(math.radians(180), 0, 0))
cone = act()
setm(cone, plum)
bpy.ops.object.select_all(action='DESELECT')
head.select_set(True)
cone.select_set(True)
bpy.context.view_layer.objects.active = head
bpy.ops.object.join()
pin = act()
r = pin.modifiers.new('r', 'REMESH')
r.mode, r.voxel_size = 'VOXEL', 0.03
s = pin.modifiers.new('s', 'SMOOTH')
s.factor, s.iterations = 0.8, 6
bpy.ops.object.shade_smooth()
face = cyl(0.62, 0.08, loc=(0, -0.96, 3.0), m=mat(hexc('#FCF8F5'), 0.35, coat=0.6), rot=(math.radians(90), 0, 0), bw=0.03)

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 60
cam.location = (0.0, -14.0, 2.4)
cam.rotation_euler = (Vector((0, 0, 2.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
sun.data.energy, sun.data.color, sun.data.angle = 3.0, (1.0, 0.82, 0.6), math.radians(4)
sun.rotation_euler = (Vector((0, 0, 0)) - Vector((6, -3, 2.5))).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(sun)
for loc, en, sz in (((-6, -6, 6), 500, 5), ((4, 6, 5), 600, 4)):
    L = bpy.data.objects.new('L', bpy.data.lights.new('L', 'AREA'))
    L.data.energy, L.data.size = en, sz
    L.location = loc
    L.rotation_euler = (Vector((0, 0, 2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(L)
sc.render.filepath = f'{OUT}/pin.png'
bpy.ops.render.render(write_still=True)

# where the face disc lands in the image (for the emblem decal)
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
c = world_to_camera_view(sc, cam, Vector((0, -1.0, 3.0)))
e = world_to_camera_view(sc, cam, Vector((0.62, -1.0, 3.0)))
json.dump({'cx': c.x * RX, 'cy': (1 - c.y) * RY, 'r': abs(e.x - c.x) * RX}, open(f'{OUT}/pin_face.json', 'w'))
print('rendered pin', flush=True)
