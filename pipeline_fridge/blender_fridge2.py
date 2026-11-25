"""OF "Can we put it on the fridge?" v2 - the fridge itself as a 3D object (glossy clay, 3/4 view, transparent bg):
a rounded retro ivory fridge with plum handles, the child's crayon drawing held by a plum magnet and a magenta heart
magnet, its bottom-right corner curling off the door; letter magnets in brand colours on the freezer door.

Run: blender -b -P blender_fridge2.py -- [draft]  -> workspace_fridge/render2/fridge.png (RGBA)
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, box, cyl, sph, hexc

ROOT = os.path.abspath(os.path.join(HERE, '..'))
TEX = f'{ROOT}/workspace_fridge/tex'
OUT = f'{ROOT}/workspace_fridge/render2'
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
DRAFT = 'draft' in argv
PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48 if DRAFT else 160
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = (700, 900) if DRAFT else (1400, 1800)
sc.render.film_transparent = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.95, 0.92, 0.9, 1)
w.node_tree.nodes['Background'].inputs[1].default_value = 0.45


def img_mat(path, rough=0.8):
    m = bpy.data.materials.new('img')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    return m


def rbox(size, loc, m, bw):
    o = box(size, loc=loc, m=m, bw=bw)
    for md in o.modifiers:
        if md.type == 'BEVEL':
            md.segments = 12
    bpy.ops.object.shade_smooth()
    return o


# ------------------------------------------------------------------ the fridge
IV = mat(hexc('#F1E5D5'), 0.22, coat=0.8)
FY = -1.1                                                        # front face plane
rbox((2.5, 2.2, 4.5), (0, 0, 2.45), IV, 0.42)                    # body
rbox((2.42, 0.08, 1.28), (0, FY - 0.02, 3.95), IV, 0.06)         # freezer door
rbox((2.42, 0.08, 3.02), (0, FY - 0.02, 1.78), IV, 0.06)         # main door
seam = mat(hexc('#8C7F75'), 0.6, coat=0.0)
box((2.3, 0.05, 0.03), loc=(0, FY + 0.02, 3.3), m=seam, bw=0.0)
handle = mat(PLUM, 0.18, 0.35, coat=1.0)
for z0, z1 in ((3.55, 4.35), (2.0, 3.05)):                       # chunky plum handles on the left edge
    cyl(0.075, z1 - z0, loc=(-0.95, FY - 0.32, (z0 + z1) / 2), m=handle, bw=0.03)
    for z in (z0 + 0.06, z1 - 0.06):
        cyl(0.05, 0.28, loc=(-0.95, FY - 0.18, z), m=handle, rot=(math.radians(90), 0, 0), bw=0.01)
dark = mat(hexc('#3A3236'), 0.5, coat=0.2)
rbox((2.0, 0.06, 0.22), (0, FY + 0.06, 0.38), dark, 0.05)        # kick-plate grille
for i in range(7):
    box((1.7, 0.02, 0.018), loc=(0, FY + 0.02, 0.3 + i * 0.026), m=mat(hexc('#22191E'), 0.5), bw=0.0)
for x in (-0.9, 0.9):
    for y in (-0.8, 0.8):
        cyl(0.11, 0.2, loc=(x, y, 0.1), m=dark, bw=0.03)

# ------------------------------------------------------------------ the drawing, its bottom-right corner curling off
DC, DW, DH, DROT = Vector((0.14, FY - 0.075, 1.8)), 1.98, 1.485, -5.0
bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=45, size=1)
pap = act()
me = pap.data
bm = bmesh.new()
bm.from_mesh(me)
a = math.radians(DROT)
for v in bm.verts:
    u, ww = v.co.x + 0.5, v.co.y + 0.5
    x, z = (u - 0.5) * DW, (ww - 0.5) * DH
    k = max(0.0, (u - 0.55) / 0.45) * max(0.0, (0.55 - ww) / 0.55)
    lift = 0.75 * k ** 1.5
    xr, zr = x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)
    v.co = DC + Vector((xr + 0.12 * k ** 2, -lift, zr + 0.05 * k))
bm.to_mesh(me)
bm.free()
bpy.ops.object.shade_smooth()
s = pap.modifiers.new('s', 'SOLIDIFY')
s.thickness = 0.004
setm(pap, img_mat(f'{TEX}/drawing.png'))


def magnet(c, col, r=0.13, d=0.09):
    cyl(r, d, loc=c, m=mat(col, 0.2, coat=1.0), rot=(math.radians(90), 0, 0), bw=0.03)


magnet(DC + Vector((-0.84, -0.05, 0.68)), PLUM)                   # plum magnet holds the top-left corner
# a magenta heart magnet holds the top-right (two lobes + a point, melted together)
hc = DC + Vector((0.86, -0.07, 0.62))
parts = []
for dx in (-0.075, 0.075):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=hc + Vector((dx, 0, 0.03)))
    o = act()
    o.scale = (1, 0.45, 1)
    parts.append(o)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.15, depth=0.08, location=hc + Vector((0, 0, -0.08)), rotation=(math.radians(90), 0, 0))
o = act()
o.scale = (1.0, 1.0, 1)
parts.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
heart = act()
r = heart.modifiers.new('r', 'REMESH')
r.mode, r.voxel_size = 'VOXEL', 0.008
sm = heart.modifiers.new('s', 'SMOOTH')
sm.factor, sm.iterations = 0.8, 8
bpy.ops.object.shade_smooth()
setm(heart, mat(MAG, 0.2, coat=1.0))
heart.rotation_euler = (0, math.radians(-8), 0)

for ch, col, x, z, rt in (('A', ORANGE, -0.55, 3.85, 8), ('b', GREEN, -0.05, 3.75, -7), ('c', MAG, 0.4, 3.9, 10), ('d', ORANGE, 0.78, 3.72, -5)):
    bpy.ops.object.text_add(location=(x, FY - 0.07, z), rotation=(math.radians(90), math.radians(rt), 0))
    t = act()
    t.data.body = ch
    t.data.size = 0.42
    t.data.extrude = 0.035
    t.data.bevel_depth = 0.012
    t.data.align_x = t.data.align_y = 'CENTER'
    setm(t, mat(col, 0.2, coat=0.9))

# ------------------------------------------------------------------ floor shadow, camera, light
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
fl = act()
fl.is_shadow_catcher = True
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 70
cam.location = (5.2, -12.0, 4.4)
tgt = Vector((0.15, 0, 2.3))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
for loc, en, sz, col in (((-6, -7, 8), 1700, 5, (1.0, 0.95, 0.9)), ((7, 4, 7), 900, 4, (0.95, 0.9, 1.0)),
                         ((3, -9, 1.5), 380, 6, (1.0, 0.97, 0.95)), ((0, 2, 9), 300, 4, (1, 1, 1))):
    L = bpy.data.objects.new('L', bpy.data.lights.new('L', 'AREA'))
    L.data.energy, L.data.size, L.data.color = en, sz, col
    L.location = loc
    L.rotation_euler = (Vector((0, 0, 2.2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(L)
sc.render.filepath = f'{OUT}/fridge.png'
bpy.ops.render.render(write_still=True)
print('rendered fridge', flush=True)
