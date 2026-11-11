"""Organic Fostering "No Qualification Needed": a photoreal top-spiral notepad on a warm wooden desk (mug of tea, pencil,
sticky notes), seen almost top-down for 9:16. The page is blank: its content is drawn in the edit and mapped onto the
page with the projected corners written to pad_proj.json. A second pass renders only the wire spiral (alpha) so flipping
pages can pass under it.

Run: blender -b -P blender_nq.py   -> workspace_nq/tex/desk.png, rings.png, pad_proj.json
"""
import bpy, bmesh, os, sys, math, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = f'{ROOT}/workspace_nq/tex'
os.makedirs(OUT, exist_ok=True)


def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 16 if os.environ.get('TEST') else 140
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = 25 if os.environ.get('TEST') else 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.95, 0.9, 0.85, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.35


def mat(name, col, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    return m


def wood():
    """Poly Haven 'wood_table_001' (CC0): colour, normal and roughness maps."""
    D = f'{ROOT}/workspace_nq/dl'
    m = bpy.data.materials.new('wood')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.5, 1.5, 1.0)
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(90))
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    def img(name, non_color=False):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(f'{D}/{name}')
        if non_color:
            n.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n
    d = img('wood_diff.jpg')
    nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
    r = img('wood_rough.jpg', True)
    nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    nm = nt.nodes.new('ShaderNodeNormalMap')
    n = img('wood_nor_gl.jpg', True)
    nt.links.new(n.outputs['Color'], nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Coat Weight'].default_value = 0.2
    return m


def paper(col='#FBF7EF'):
    m = mat('paper', lin(col), 0.85)
    nt = m.node_tree
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 300
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.04
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
    return m


def add(o, m=None):
    if m:
        o.data.materials.append(m)
    return o


def box(size, loc, m, bev=0.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bev:
        md = o.modifiers.new('b', 'BEVEL')
        md.width, md.segments = bev, 3
    return add(o, m)


# ------------------------------------------------------------------ desk
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
add(bpy.context.active_object, wood())

# ------------------------------------------------------------------ notepad (portrait, spiral along the top edge)
PW, PH = 1.0, 1.36
T0 = 0.045                                                   # pad thickness
back = box((PW + 0.02, PH + 0.03, 0.012), (0, -0.01, 0.006), mat('board', lin('#5B174F'), 0.6), bev=0.006)   # plum cover board
stack = box((PW, PH, T0 - 0.012), (0, 0, 0.012 + (T0 - 0.012) / 2), paper('#F1EADF'), bev=0.002)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, T0 + 0.0008))
page = bpy.context.active_object
page.scale = (PW, PH, 1)
bpy.ops.object.transform_apply(scale=True)
add(page, paper())

# wire spiral: loops through holes along the top edge
ringm = mat('wire', lin('#C9CCD1'), 0.25, 1.0)
rings = []
N = 19
for i in range(N):
    x = -PW / 2 + 0.06 + i * (PW - 0.12) / (N - 1)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.034, minor_radius=0.0055, location=(x, PH / 2 - 0.025, T0 * 0.6),
                                     rotation=(0, math.radians(90), 0), major_segments=48, minor_segments=12)
    r = bpy.context.active_object
    add(r, ringm)
    rings.append(r)
holem = mat('hole', lin('#2A2024'), 0.8)
for i in range(N):
    x = -PW / 2 + 0.06 + i * (PW - 0.12) / (N - 1)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.004, location=(x, PH / 2 - 0.025, T0 + 0.0012), vertices=16)
    add(bpy.context.active_object, holem)

# ------------------------------------------------------------------ props
# mug of tea (top right, half out of frame)
bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.36, location=(0.62, 1.16, 0.18), vertices=96)
mug = bpy.context.active_object
md = mug.modifiers.new('s', 'SOLIDIFY')
md.thickness = 0.012
md2 = mug.modifiers.new('b', 'BEVEL')
md2.width, md2.segments = 0.008, 3
add(mug, mat('mug', lin('#F4EFE9'), 0.25, coat=0.6))
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.01, location=(0.62, 1.16, 0.33), vertices=96)
add(bpy.context.active_object, mat('tea', lin('#6B3A1A'), 0.08))
bpy.ops.mesh.primitive_torus_add(major_radius=0.075, minor_radius=0.018, location=(0.8, 1.16, 0.2), rotation=(math.radians(90), 0, 0))
add(bpy.context.active_object, mat('mug2', lin('#F4EFE9'), 0.25, coat=0.6))
bpy.ops.mesh.primitive_torus_add(major_radius=0.162, minor_radius=0.006, location=(0.62, 1.16, 0.24))
add(bpy.context.active_object, mat('band', lin('#B7006E'), 0.35))

# pencil (right side, diagonal)
pm = mat('pencil', lin('#FF6411'), 0.45)
bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.62, location=(-0.1, 1.0, 0.014), rotation=(math.radians(90), 0, math.radians(84)), vertices=6)
add(bpy.context.active_object, pm)
bpy.ops.mesh.primitive_cone_add(radius1=0.014, depth=0.05, location=(0.66 - 0.31 * math.sin(math.radians(14)) * -1 * 0 + 0.075, -0.25 - 0.325, 0.014),
                                rotation=(math.radians(90), 0, math.radians(14)), vertices=6)
tip = bpy.context.active_object
tip.location = (-0.1 + 0.33 * math.sin(math.radians(84)), 1.0 - 0.33 * math.cos(math.radians(84)), 0.014)
tip.rotation_euler = (math.radians(-90), 0, math.radians(84))
add(tip, mat('wood2', lin('#E8C9A0'), 0.6))

# sticky notes (left)
for (x, y, r, col) in ((-0.68, 1.08, 8, '#FFD4BA'), (-0.42, 1.2, -6, '#F3DDEB')):
    box((0.26, 0.26, 0.004), (x, y, 0.003 + (0.002 if col == '#F3DDEB' else 0)), paper(col), bev=0, rot=(0, 0, math.radians(r)))

# ------------------------------------------------------------------ light + camera
L = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
L.data.energy = 4.2
L.data.angle = math.radians(6)
L.data.color = (1.0, 0.93, 0.84)
L.rotation_euler = (math.radians(32), math.radians(-18), math.radians(-30))
sc.collection.objects.link(L)
A = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'AREA'))
A.data.energy, A.data.size = 260, 4
A.location = (1.5, -2, 3)
A.rotation_euler = (Vector((0, 0, 0)) - A.location).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(A)

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 50
cam.data.sensor_fit = 'VERTICAL'
cam.location = (0, -0.62, 4.35)
cam.rotation_euler = (math.radians(9.5), 0, 0)

# ------------------------------------------------------------------ project the page corners + spiral line
bpy.context.view_layer.update()
def proj(p):
    v = world_to_camera_view(sc, cam, Vector(p))
    return [v.x * 1080, (1 - v.y) * 1920]
z = T0 + 0.0008
corners = {'tl': proj((-PW / 2, PH / 2, z)), 'tr': proj((PW / 2, PH / 2, z)), 'bl': proj((-PW / 2, -PH / 2, z)),
           'br': proj((PW / 2, -PH / 2, z)),
           'spine_l': proj((-PW / 2, PH / 2 - 0.025, z)), 'spine_r': proj((PW / 2, PH / 2 - 0.025, z)),
           'page_wh': [PW, PH]}
json.dump(corners, open(f'{OUT}/pad_proj.json', 'w'), indent=1)
print('corners', corners)

sc.render.filepath = f'{OUT}/desk.png'
bpy.ops.render.render(write_still=True)

# spiral-only pass (alpha), for pages flipping under the wire
sc.render.film_transparent = True
for o in sc.objects:
    if o.type == 'MESH' and o not in rings:
        o.is_holdout = True
sc.render.filepath = f'{OUT}/rings.png'
bpy.ops.render.render(write_still=True)
print('done')
