"""Organic Fostering "Asked the internet? Ask us." 3D static post: an overhead view of a round wooden table at dusk with
a search interface projected onto it as light; out of the result card's photo slot a little 3D home rises, glowing
windows, softly lit by the projection. Tea, a plant and a notebook around the edge.

Run: blender -b -P blender_search.py -- [draft|final] -> workspace_search/render/<q>.png (1080x1350)
"""
import bpy, sys, os, math
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TEX = f'{ROOT}/workspace_search/tex'
WOOD = f'{ROOT}/workspace_nq/dl'
OUT = f'{ROOT}/workspace_search/render'
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
Q = argv[0] if argv else 'draft'


def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48 if Q == 'draft' else 256
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.render.resolution_percentage = 50 if Q == 'draft' else 100
MODE = os.environ.get('MODE', '')           # '' full scene | 'plate_on' / 'plate_off' (no UI, no house) | 'house' (house anim only)
if MODE:
    sc.render.resolution_percentage = 150
    sc.cycles.samples = int(os.environ.get('SAMPLES', '128'))
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = lin('#1A0F18')
w.node_tree.nodes['Background'].inputs[1].default_value = 0.25


def mat(name, col, rough=0.5, metal=0.0, coat=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = emit[0]
        b.inputs['Emission Strength'].default_value = emit[1]
    return m


def act():
    return bpy.context.active_object


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def bevel(o, wdt=0.03, seg=3):
    md = o.modifiers.new('b', 'BEVEL')
    md.width, md.segments = wdt, seg
    return o


def box(size, loc, m, bw=0.03, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = act()
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bevel(o, bw)
    return setm(smooth(o), m)


# ------------------------------------------------------------------ table (Poly Haven wood, CC0) and floor
wood = bpy.data.materials.new('wood')
wood.use_nodes = True
nt = wood.node_tree
b = nt.nodes['Principled BSDF']
tc = nt.nodes.new('ShaderNodeTexCoord')
mp = nt.nodes.new('ShaderNodeMapping')
mp.inputs['Scale'].default_value = (0.35, 0.35, 1)
nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
for key, slot, nc in (('wood_diff.jpg', 'Base Color', False), ('wood_rough.jpg', 'Roughness', True)):
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(f'{WOOD}/{key}')
    if nc:
        t.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
    nt.links.new(t.outputs['Color'], b.inputs[slot])
nm = nt.nodes.new('ShaderNodeNormalMap')
tn = nt.nodes.new('ShaderNodeTexImage')
tn.image = bpy.data.images.load(f'{WOOD}/wood_nor_gl.jpg')
tn.image.colorspace_settings.name = 'Non-Color'
nt.links.new(mp.outputs['Vector'], tn.inputs['Vector'])
nt.links.new(tn.outputs['Color'], nm.inputs['Color'])
nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
b.inputs['Coat Weight'].default_value = 0.35
bpy.ops.mesh.primitive_cylinder_add(radius=6.0, depth=0.3, location=(0, 0, -0.15), vertices=192)
setm(bevel(smooth(act()), 0.05), wood)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -2.5))
setm(act(), mat('floor', lin('#2A1B24'), 0.8))

# ------------------------------------------------------------------ projected UI: emissive light on the wood
ui = bpy.data.materials.new('ui')
ui.use_nodes = True
nt = ui.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
tex = nt.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(f'{TEX}/ui.png')
em = nt.nodes.new('ShaderNodeEmission')
em.inputs['Strength'].default_value = 1.8
tr = nt.nodes.new('ShaderNodeBsdfTransparent')
mix = nt.nodes.new('ShaderNodeMixShader')
add = nt.nodes.new('ShaderNodeAddShader')
nt.links.new(tex.outputs['Color'], em.inputs['Color'])
nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
nt.links.new(tr.outputs[0], mix.inputs[1])
nt.links.new(em.outputs[0], add.inputs[0])
nt.links.new(tr.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs['Surface'])
ui.blend_method = 'BLEND'
UIW, UIH = 6.4, 8.0
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.004))
p = act()
p.hide_render = bool(MODE)
p.scale = (UIW, UIH, 1)
bpy.ops.object.transform_apply(scale=True)
setm(p, ui)
# the projector's glow on the wood (a soft magenta-white area light hanging above)
proj = bpy.data.objects.new('proj', bpy.data.lights.new('proj', 'AREA'))
proj.data.shape, proj.data.size, proj.data.size_y = 'RECTANGLE', UIW, UIH
proj.data.energy, proj.data.color = 25, (1.0, 0.82, 0.95)
proj.location = (0, 0, 0.6)
sc.collection.objects.link(proj)
if MODE == 'plate_off':
    proj.data.energy = 0.0

# ------------------------------------------------------------------ the little home rising from the result card's photo slot
def u2w(px, py):
    return ((px / 1600 - 0.5) * UIW, (0.5 - py / 2000) * UIH)


hx, hy = u2w(140 + 40 + 240, 680 + 430)
S_ = 1.2
_before = set(sc.objects)
walls = box((1.25 * S_, 1.0 * S_, 0.95 * S_), (hx, hy, 0.5 * S_), mat('wall', lin('#FCF8F5'), 0.35, coat=0.3), bw=0.06)
bpy.ops.mesh.primitive_cone_add(radius1=1.0 * S_, depth=0.7 * S_, vertices=4, location=(hx, hy, 1.32 * S_), rotation=(0, 0, math.radians(45)))
r = act()
r.scale = (1.0, 0.82, 1)
bpy.ops.object.transform_apply(scale=True)
setm(bevel(smooth(r), 0.05), mat('roof', lin('#B7006E'), 0.28, coat=0.5))
box((0.28 * S_, 0.06, 0.45 * S_), (hx + 0.25 * S_, hy - 0.5 * S_, 0.26 * S_), mat('door', lin('#FF6411'), 0.3), bw=0.03)
warmwin = mat('win', lin('#FFD27A'), 0.3, emit=(lin('#FFC45A'), 6.0))
for wx in (-0.3, 0.3):
    box((0.24 * S_, 0.06, 0.24 * S_), (hx + wx * S_, hy - 0.5 * S_, 0.72 * S_), warmwin, bw=0.02)
box((0.2 * S_, 0.2 * S_, 0.35 * S_), (hx + 0.32 * S_, hy + 0.15 * S_, 1.55 * S_), mat('chim', lin('#5B174F'), 0.3), bw=0.02)
HOUSE_OBJS = [o for o in sc.objects if o not in _before and o.type == 'MESH']
gl = bpy.data.objects.new('homeglow', bpy.data.lights.new('homeglow', 'POINT'))
gl.data.energy, gl.data.color, gl.data.shadow_soft_size = 60, (1.0, 0.75, 0.45), 0.3
gl.location = (hx, hy - 1.1, 1.0)
sc.collection.objects.link(gl)

# ------------------------------------------------------------------ props round the edge
bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=1.0, location=(4.3, 3.4, 0.5), vertices=96)
mug = act()
s_ = mug.modifiers.new('s', 'SOLIDIFY')
s_.thickness = 0.04
setm(smooth(mug), mat('mug', lin('#5B174F'), 0.25, coat=0.8))
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.02, location=(4.3, 3.4, 0.86), vertices=64)
setm(act(), mat('tea', lin('#6B3A1A'), 0.05))
bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.07, location=(4.88, 3.4, 0.5), rotation=(math.radians(90), 0, 0))
setm(smooth(act()), mat('mug2', lin('#5B174F'), 0.25, coat=0.8))
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.9, location=(-4.4, 3.5, 0.45), vertices=64)
setm(smooth(act()), mat('pot', lin('#E8DCCB'), 0.6))
leafm = mat('leaf', lin('#61A80A'), 0.4, coat=0.3)
import random
random.seed(3)
for k in range(14):
    a = k / 14 * 2 * math.pi
    rr = random.uniform(0.3, 0.9)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(-4.4 + rr * math.cos(a), 3.5 + rr * math.sin(a), 1.0 + random.uniform(0, 0.35)))
    lf = act()
    lf.scale = (1.0, 0.4, 0.12)
    lf.rotation_euler = (random.uniform(-0.4, 0.4), random.uniform(-0.3, 0.3), a)
    setm(smooth(lf), leafm)
box((2.4, 3.2, 0.18), (-4.3, -3.6, 0.09), mat('book', lin('#B7006E'), 0.5), bw=0.03, rot=(0, 0, math.radians(18)))
box((2.3, 3.1, 0.06), (-4.25, -3.55, 0.2), mat('pages', lin('#FCF8F5'), 0.7), bw=0.01, rot=(0, 0, math.radians(18)))
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.6, location=(4.1, -3.2, 0.06), rotation=(math.radians(90), 0, math.radians(-30)))
setm(smooth(act()), mat('pen', lin('#FF6411'), 0.3))

# ------------------------------------------------------------------ lights + camera (slightly off overhead, so the home stands up)
key = bpy.data.objects.new('key', bpy.data.lights.new('key', 'AREA'))
key.data.energy, key.data.size, key.data.color = 450, 6, (1.0, 0.85, 0.7)
key.location = (-6, -5, 9)
key.rotation_euler = (Vector((0, 0, 0)) - key.location).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(key)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'
cam.data.lens = 42
cam.location = (0.0, -9.0, 13.4)
target = Vector((0, -0.1, 0.3))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
from bpy_extras.object_utils import world_to_camera_view
import json
bpy.context.view_layer.update()
RW, RH = int(1080 * sc.render.resolution_percentage / 100), int(1350 * sc.render.resolution_percentage / 100)
def P(pt):
    v = world_to_camera_view(sc, cam, Vector(pt))
    return [v.x * RW, (1 - v.y) * RH]
HOUSE = HOUSE_OBJS
if MODE:
    json.dump({'res': [RW, RH], 'ui': [P((-UIW / 2, UIH / 2, 0.004)), P((UIW / 2, UIH / 2, 0.004)), P((UIW / 2, -UIH / 2, 0.004)), P((-UIW / 2, -UIH / 2, 0.004))],
               'house_base': P((hx, hy, 0)), 'house_top': P((hx, hy, 1.7 * S_)), 'window': P((hx - 0.3 * S_, hy - 0.5 * S_, 0.72 * S_))},
              open(f'{OUT}/proj.json', 'w'), indent=1)
if MODE in ('plate_on', 'plate_off'):
    for o in HOUSE + [o for o in sc.objects if o.name.startswith('homeglow')]:
        o.hide_render = True
    sc.render.filepath = f'{OUT}/{MODE}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', MODE)
elif MODE == 'house':
    keep = set(HOUSE) | {o for o in sc.objects if o.type in ('LIGHT', 'CAMERA')}
    for o in sc.objects:
        if o not in keep and o.type == 'MESH':
            o.hide_render = True
    bpy.ops.mesh.primitive_plane_add(size=6, location=(hx, hy, 0.0))
    catcher = act()
    catcher.is_shadow_catcher = True
    sc.render.film_transparent = True
    pivot = bpy.data.objects.new('pivot', None)
    sc.collection.objects.link(pivot)
    pivot.location = (hx, hy, 0)
    bpy.context.view_layer.update()
    for o in HOUSE:
        mw = o.matrix_world.copy()
        o.parent = pivot
        o.matrix_world = mw
    xs = [P((hx + dx, hy + dy, dz))[0] for dx in (-1.6, 1.6) for dy in (-1.6, 1.6) for dz in (0, 2.4 * S_)]
    ys = [P((hx + dx, hy + dy, dz))[1] for dx in (-1.6, 1.6) for dy in (-1.6, 1.6) for dz in (0, 2.4 * S_)]
    sc.render.use_border, sc.render.use_crop_to_border = True, True
    bx0, bx1 = max(0, min(xs)) / RW, min(RW, max(xs)) / RW
    by0, by1 = 1 - min(RH, max(ys)) / RH, 1 - max(0, min(ys)) / RH
    sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = bx0, bx1, by0, by1
    json.dump({'box': [bx0 * RW, (1 - by1) * RH, bx1 * RW, (1 - by0) * RH]}, open(f'{OUT}/house_box.json', 'w'))
    NF = 24
    os.makedirs(f'{OUT}/house', exist_ok=True)
    for i in range(NF + 1):
        k = i / NF
        e = 1 - (1 - k) ** 3
        over = 1 + 0.12 * math.sin(math.pi * min(1, k * 1.3)) * (1 - k)
        pivot.scale = (0.6 + 0.4 * e, 0.6 + 0.4 * e, max(0.001, e * over))
        pivot.rotation_euler = (0, 0, math.radians(-25 * (1 - e)))
        bpy.context.view_layer.update()
        sc.render.filepath = f'{OUT}/house/{i:03d}.png'
        bpy.ops.render.render(write_still=True)
    print('rendered house')
else:
    sc.render.filepath = f'{OUT}/{Q}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', Q)
