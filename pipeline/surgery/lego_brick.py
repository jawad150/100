"""Render a glossy blue 2x4 toy brick (like the client's reference photo) with a
transparent background -> $WS/src/lego_brick.png

Usage: python3 lego_brick.py
"""
import math, os
import bpy
from common import WS

U = 1.0            # stud pitch
BH = 1.2 * U       # brick height
SR = 0.3 * U       # stud radius
SH = 0.22 * U      # stud height

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

mat = bpy.data.materials.new('blue_plastic')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.0, 0.09, 0.52, 1)
bsdf.inputs['Roughness'].default_value = 0.16
bsdf.inputs['Coat Weight'].default_value = 0.35
bsdf.inputs['Coat Roughness'].default_value = 0.08


def bevel(obj, w, seg=4):
    m = obj.modifiers.new('bev', 'BEVEL')
    m.width, m.segments, m.limit_method = w, seg, 'ANGLE'
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True


bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, BH / 2))
body = bpy.context.object
body.scale = (4 * U, 2 * U, BH)
bpy.ops.object.transform_apply(scale=True)
bevel(body, 0.035)
for i in range(4):
    for j in range(2):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=SR, depth=SH,
                                            location=((i - 1.5) * U, (j - 0.5) * U, BH + SH / 2))
        bevel(bpy.context.object, 0.03)

# camera: 3/4 view from the front-right and above, like the reference photo
cam = bpy.data.cameras.new('cam')
cam.lens = 85
co = bpy.data.objects.new('cam', cam)
sc.collection.objects.link(co)
co.location = (6.2, -9.5, 7.6)
tgt = bpy.data.objects.new('target', None)
tgt.location = (0, 0, 0.6)
sc.collection.objects.link(tgt)
tc = co.constraints.new('TRACK_TO')
tc.target, tc.track_axis, tc.up_axis = tgt, 'TRACK_NEGATIVE_Z', 'UP_Y'
sc.camera = co


def area(name, loc, size, energy, rot):
    l = bpy.data.lights.new(name, 'AREA')
    l.size, l.energy = size, energy
    o = bpy.data.objects.new(name, l)
    o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o)


area('key', (-4, -6, 9), 6, 1400, (math.radians(35), 0, math.radians(-30)))
area('fill', (8, -3, 4), 5, 500, (math.radians(70), 0, math.radians(65)))
area('rim', (0, 7, 6), 4, 700, (math.radians(-50), 0, 0))
world = bpy.data.worlds.new('w')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.82, 0.85, 0.9, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
sc.world = world

sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = 1000, 760
sc.view_settings.view_transform = 'Standard'
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
os.makedirs(f'{WS}/src', exist_ok=True)
sc.render.filepath = f'{WS}/src/lego_brick.png'
bpy.ops.render.render(write_still=True)
print('wrote', sc.render.filepath)
