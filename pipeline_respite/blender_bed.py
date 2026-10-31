"""Photoreal still: a child's bed made up and waiting for Friday. Handwritten tent card on the pillow ("Welcome back!
Pancakes tomorrow?"), a teddy, folded towels at the foot, a glowing bedside lamp with books, fairy lights on the wall,
late-afternoon window light. 1080x1350, Cycles.

Usage: python3 blender_bed.py [samples]
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

S = '/home/user/100/workspace_respite'
SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 160
random.seed(3)


def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#F6DCCB')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.24


def material(name, col, rough=0.5, metal=0.0, coat=0.0, tex=None, bump=None, sheen=0.0, emit=None, estr=0.0, trans=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Sheen Weight'].default_value = sheen
    b.inputs['Transmission Weight'].default_value = trans
    if emit:
        b.inputs['Emission Color'].default_value = emit; b.inputs['Emission Strength'].default_value = estr
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(tex)
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if bump:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bump[0]; n.inputs['Detail'].default_value = 10
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump[1]; bp.inputs['Distance'].default_value = 0.003
        nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def soft_box(size, loc, m, bevel=0.1, sub=2, disp=0.0, rot=(0, 0, 0), seed=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 5
    if sub:
        s = o.modifiers.new('ss', 'SUBSURF'); s.levels = sub; s.render_levels = sub
    if disp:
        t = bpy.data.textures.new('n%d' % seed, 'CLOUDS'); t.noise_scale = 0.35
        d = o.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = disp
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def sphere(r, loc, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


# room
wall = material('wall', lin('#F4C9B2'), rough=0.9, bump=(160, 0.2))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2.0, 0), rotation=(math.radians(90), 0, 0))
w = bpy.context.object; w.scale = (16, 10, 1); w.data.materials.append(wall)
floor = material('floor', lin('#C9A27E'), rough=0.45, bump=(25, 0.1))
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -1.2)); bpy.context.object.data.materials.append(floor)

soft_box((16, 0.06, 0.22), (0, 1.97, -1.09), material('skirt', lin('#FFFDF8'), rough=0.4), bevel=0.01, sub=0)
soft_box((0.9, 0.05, 0.7), (-2.25, 1.97, 0.45), material('frame', lin('#E8D3B8'), rough=0.4), bevel=0.02, sub=0)
soft_box((0.74, 0.03, 0.54), (-2.25, 1.94, 0.45), material('art', lin('#7FA6A0'), rough=0.6, bump=(12, 0.3)), bevel=0, sub=0)
# bed: wooden frame, headboard, mattress, duvet, turned-down sheet
wood = material('wood', lin('#E8D3B8'), rough=0.4, bump=(8, 0.05))
soft_box((2.3, 3.9, 0.35), (0, -0.05, -0.85), wood, bevel=0.04, sub=0)
soft_box((2.4, 0.14, 1.9), (0, 1.88, 0.05), wood, bevel=0.06, sub=0)
soft_box((2.16, 3.76, 0.42), (0, -0.05, -0.48), material('matt', lin('#FBF8F2'), rough=0.8), bevel=0.12, sub=2)
duvet_m = material('duvet', lin('#A9C3B0'), rough=0.85, sheen=0.4, bump=(90, 0.15))
_nt = duvet_m.node_tree; _b = _nt.nodes['Principled BSDF']
_wv = _nt.nodes.new('ShaderNodeTexWave'); _wv.inputs['Scale'].default_value = 13; _wv.wave_profile = 'SIN'
_mx = _nt.nodes.new('ShaderNodeMix'); _mx.data_type = 'RGBA'
_mx.inputs[6].default_value = lin('#9EBBA6'); _mx.inputs[7].default_value = lin('#EDEDE2')
_cr = _nt.nodes.new('ShaderNodeValToRGB'); _cr.color_ramp.elements[0].position = 0.84; _cr.color_ramp.elements[1].position = 0.9
_nt.links.new(_wv.outputs['Fac'], _cr.inputs['Fac']); _nt.links.new(_cr.outputs['Color'], _mx.inputs['Factor'])
_nt.links.new(_mx.outputs[2], _b.inputs['Base Color'])
dv = soft_box((2.34, 2.9, 0.3), (0, -0.5, -0.19), duvet_m, bevel=0.14, sub=4, disp=0.0, seed=1)
for _k, (_sc, _st) in enumerate(((0.22, 0.09), (0.08, 0.035))):
    _t = bpy.data.textures.new('dw%d' % _k, 'CLOUDS'); _t.noise_scale = _sc
    _d = dv.modifiers.new('d%d' % _k, 'DISPLACE'); _d.texture = _t; _d.strength = _st
sheet = material('sheet', lin('#FFFDF8'), rough=0.8, sheen=0.3, bump=(120, 0.1))
soft_box((2.4, 0.62, 0.24), (0, 0.66, -0.07), sheet, bevel=0.1, sub=3, disp=0.0, seed=2)
pillow_m = material('pillow', lin('#FFFFFF'), rough=0.8, sheen=0.35, bump=(110, 0.12))
pl = soft_box((1.5, 0.62, 0.34), (0, 1.38, 0.04), pillow_m, bevel=0.25, sub=3, disp=0.04, rot=(math.radians(-12), 0, 0), seed=3)

# tent card on the pillow
card = material('card', (1, 1, 1, 1), rough=0.6, tex=f'{S}/tex/note.png')
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.0, 1.16, 0.43), rotation=(math.radians(72), 0, math.radians(-4)))
cd = bpy.context.object; cd.scale = (0.66, 0.47, 1); cd.data.materials.append(card)
s_ = cd.modifiers.new('s', 'SOLIDIFY'); s_.thickness = 0.008
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.0, 1.34, 0.43), rotation=(math.radians(-72), 0, math.radians(-4)))
b2 = bpy.context.object; b2.scale = (0.66, 0.47, 1); b2.data.materials.append(material('cardback', lin('#FBF6EC'), rough=0.6))

# teddy bear leaning by the pillow
fur = material('fur', lin('#B07A4E'), rough=0.95, sheen=1.0, bump=(300, 0.4))
fur2 = material('fur2', lin('#E6CBA8'), rough=0.95, sheen=0.8, bump=(300, 0.3))
tx, ty, tz = -0.78, 1.15, 0.05
sphere(0.27, (tx, ty, tz), fur, (1, 0.85, 1.1))
sphere(0.2, (tx, ty - 0.03, tz + 0.38), fur)
for dx in (-0.14, 0.14):
    sphere(0.075, (tx + dx, ty + 0.02, tz + 0.55), fur)
    sphere(0.04, (tx + dx, ty - 0.03, tz + 0.55), fur2, (1, 0.5, 1))
sphere(0.085, (tx, ty - 0.18, tz + 0.33), fur2, (1, 0.8, 0.8))
sphere(0.025, (tx, ty - 0.255, tz + 0.36), material('nose', lin('#2A1B14'), rough=0.3, coat=0.5))
for dx in (-0.07, 0.07):
    sphere(0.022, (tx + dx, ty - 0.17, tz + 0.43), material('eye', lin('#1A1210'), rough=0.2, coat=0.8))
for dx in (-0.22, 0.22):
    sphere(0.1, (tx + dx, ty - 0.12, tz + 0.02), fur, (0.8, 0.8, 1.3))
    sphere(0.11, (tx + dx * 0.7, ty - 0.22, tz - 0.22), fur, (0.9, 1.2, 0.8))
sphere(0.06, (tx, ty - 0.2, tz + 0.18), material('bow', lin('#FF6411'), rough=0.4, sheen=0.3), (1.6, 0.5, 0.8))

# folded towels at the foot of the bed
for k, col in enumerate(('#FFD4BA', '#FFFFFF', '#F2A07B')):
    soft_box((0.62, 0.44, 0.085), (0.5, -0.75, 0.02 + k * 0.088), material('tw%d' % k, lin(col), rough=0.95, sheen=0.6, bump=(220, 0.3)),
             bevel=0.05, sub=2, rot=(0, 0, math.radians(8 - k * 4)))

# bedside table, lamp, books
soft_box((0.8, 0.7, 0.9), (1.75, 1.35, -0.75), material('bt', lin('#FFFDF7'), rough=0.4), bevel=0.03, sub=0)
for k, (col, h) in enumerate((('#5B174F', 0.07), ('#FF6411', 0.06), ('#64A60B', 0.08))):
    soft_box((0.46 - k * 0.04, 0.34, h), (1.6, 1.3, -0.28 + sum((0.07, 0.06, 0.08)[:k]) + h / 2), material('bk%d' % k, lin(col), rough=0.5),
             bevel=0.01, sub=0, rot=(0, 0, math.radians(6 * (k % 2 * 2 - 1))))
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.36, location=(1.95, 1.45, -0.12), vertices=48)
bpy.context.object.data.materials.append(material('lampbase', lin('#E9DCCB'), rough=0.3, coat=0.4))
bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0.2, depth=0.36, location=(1.95, 1.45, 0.25), vertices=64)
shade = bpy.context.object
shade.data.materials.append(material('shade', lin('#FFF1DC'), rough=0.8, emit=lin('#FFD9A0'), estr=2.5))
bpy.ops.object.light_add(type='POINT', location=(1.95, 1.4, 0.2))
lamp = bpy.context.object; lamp.data.energy = 120; lamp.data.color = (1.0, 0.75, 0.45); lamp.data.shadow_soft_size = 0.15

# fairy lights draped on the wall above the bed
cdv = bpy.data.curves.new('wire', 'CURVE'); cdv.dimensions = '3D'
spl = cdv.splines.new('POLY')
N = 60
spl.points.add(N - 1)
pts = []
for i in range(N):
    u = i / (N - 1)
    x = -2.4 + 4.8 * u
    z = 1.42 - 0.25 * math.sin(u * math.pi * 3) ** 2
    pts.append((x, 1.96, z))
    spl.points[i].co = (x, 1.96, z, 1)
cdv.bevel_depth = 0.006
wo = bpy.data.objects.new('wire', cdv); sc.collection.objects.link(wo); wo.data.materials.append(material('wiremat', lin('#8C7A68'), rough=0.6))
bulb = material('bulb', lin('#FFF4D6'), emit=lin('#FFC56E'), estr=12)
for i in range(2, N, 4):
    sphere(0.035, (pts[i][0], 1.93, pts[i][2] - 0.04), bulb)

# sun through the window (left) and fill
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(52), 0, math.radians(-50)))
sun = bpy.context.object; sun.data.energy = 4.5; sun.data.color = (1.0, 0.78, 0.55); sun.data.angle = math.radians(1.2)
_d = sun.matrix_world.to_quaternion() @ Vector((0, 0, -1))
_mm = material('mull', (1, 1, 1, 1))
for _x in (-0.9, 0.0, 0.9):
    _c = Vector((_x - 0.4, 1.9, 0.6)) - _d * 3.0
    _o = soft_box((0.09, 0.09, 8), (_c.x, _c.y, _c.z), _mm, bevel=0, sub=0); _o.visible_camera = False
for _z in (-0.6, 0.55, 1.7):
    _c = Vector((-0.4, 1.9, _z)) - _d * 3.0
    _o = soft_box((8, 0.09, 0.09), (_c.x, _c.y, _c.z), _mm, bevel=0, sub=0); _o.visible_camera = False
bpy.ops.object.light_add(type='AREA', location=(-2.5, -5.5, 2.5))
fl = bpy.context.object; fl.data.energy = 160; fl.data.size = 5; fl.data.color = (1.0, 0.92, 0.88)
fl.rotation_euler = (math.radians(65), 0, math.radians(-25))

# camera: from the foot of the bed, slightly left, a little above
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.lens = 42
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = 4.75; cam_d.dof.aperture_fstop = 2.2
cam.location = (-1.1, -3.4, 1.15)
target = Vector((0.1, 1.15, 0.55))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()

HIDE = os.environ.get('HIDE')
if HIDE:
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.data.materials and o.data.materials[0].name in HIDE.split(','):
            o.hide_render = True
sc.render.filepath = os.environ.get('OUTP', f'{S}/tex/bed_render.png')
bpy.ops.render.render(write_still=True)
print('rendered')
