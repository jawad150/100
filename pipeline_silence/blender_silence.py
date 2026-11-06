"""Hulk Marketing "Silence Looks Like Guilt": photoreal night scene for the static post (1080x1350).

A dark restaurant after close: a walnut table, a phone lying face up with an unanswered 2-star review notification glowing
on its screen (a generic card, not any platform's UI), lime light spilling onto the table, a candle in glass, a coffee cup,
and the blurred, warm lights of the empty room behind.

Usage: python3 blender_silence.py screen          (draw the phone screen texture)
       python3 blender_silence.py render [samples] [pct]
"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_silence'
FD = f'{ROOT}/workspace_sol/fonts'


def draw_screen():
    from PIL import Image, ImageDraw, ImageFont
    W_, H_ = 900, 1900
    im = Image.new('RGB', (W_, H_), (14, 20, 17))
    d = ImageDraw.Draw(im)
    F = lambda n, s: ImageFont.truetype(f'{FD}/{n}.ttf', s)
    d.text((W_ / 2, 230), '23:47', font=F('Headline-700', 170), fill=(235, 240, 232), anchor='mm')
    d.text((W_ / 2, 360), 'Friday 6 November', font=F('Hanken-500', 46), fill=(170, 180, 172), anchor='mm')
    # notification card
    x0, y0, x1, y1 = 50, 520, W_ - 50, 900
    d.rounded_rectangle([x0, y0, x1, y1], 44, fill=(36, 44, 40))
    d.rounded_rectangle([x0 + 34, y0 + 34, x0 + 120, y0 + 120], 22, fill=(157, 239, 105))
    d.text((x0 + 77, y0 + 77), 'M', font=F('Headline-900', 54), fill=(18, 28, 23), anchor='mm')
    d.text((x0 + 150, y0 + 58), 'MAPLE KITCHEN · REVIEWS', font=F('Hanken-700', 30), fill=(170, 180, 172), anchor='lm')
    d.text((x1 - 40, y0 + 58), '9d', font=F('Hanken-500', 30), fill=(170, 180, 172), anchor='rm')
    d.text((x0 + 150, y0 + 118), 'New review: 2 out of 5', font=F('Headline-800', 44), fill=(240, 244, 238), anchor='lm')
    for i in range(5):
        cx = x0 + 168 + i * 56
        col = (240, 244, 238) if i < 2 else (80, 92, 86)
        star(d, cx, y0 + 196, 24, col)
    d.text((x0 + 40, y0 + 270), '"Waited 40 minutes past my booking…"', font=F('Hanken-500', 38), fill=(205, 212, 206), anchor='lm')
    d.rounded_rectangle([x0 + 40, y0 + 312, x0 + 330, y0 + 360], 24, fill=(120, 34, 34))
    d.text((x0 + 185, y0 + 336), 'No reply yet', font=F('Hanken-700', 30), fill=(255, 210, 210), anchor='mm')
    # faint older notifications
    for k in range(2):
        yy = 960 + k * 200
        d.rounded_rectangle([x0, yy, x1, yy + 170], 40, fill=(26, 33, 30))
        d.rounded_rectangle([x0 + 40, yy + 50, x0 + 500 - k * 120, yy + 76], 12, fill=(52, 62, 57))
        d.rounded_rectangle([x0 + 40, yy + 100, x0 + 360 - k * 60, yy + 122], 11, fill=(44, 53, 49))
    d.rounded_rectangle([W_ / 2 - 150, H_ - 60, W_ / 2 + 150, H_ - 46], 7, fill=(120, 130, 124))
    os.makedirs(f'{S}/tex', exist_ok=True)
    im.save(f'{S}/tex/screen.png')
    print('screen')


def star(d, cx, cy, r, col):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=col)


if len(sys.argv) > 1 and sys.argv[1] == 'screen':
    draw_screen()
    sys.exit(0)

import bpy
from mathutils import Vector

SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 128
PCT = int(sys.argv[3]) if len(sys.argv) > 3 else 100


def lin(h):
    h = h.lstrip('#')

    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True; sc.cycles.max_bounces = 8
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.render.resolution_percentage = PCT
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - High Contrast'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#0B120E')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3


def mat(name, col, rough=0.4, metal=0.0, coat=0.0, emit=None, estr=0.0, trans=0.0, ior=1.45, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin(col) if isinstance(col, str) else col
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat; b.inputs['IOR'].default_value = ior
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
    if emit:
        b.inputs['Emission Color'].default_value = lin(emit); b.inputs['Emission Strength'].default_value = estr
    return m


def rbox(size, loc, m, bevel=0.02, rot=(0, 0, 0), seg=5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg; bv.limit_method = 'NONE'
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def cyl(r, d, loc, m, rot=(0, 0, 0), v=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object; o.data.materials.append(m)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    return o


# walnut table
wood = bpy.data.materials.new('walnut'); wood.use_nodes = True
nt = wood.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Roughness'].default_value = 0.28; b.inputs['Coat Weight'].default_value = 0.5
wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 1.6; wv.inputs['Distortion'].default_value = 7; wv.inputs['Detail'].default_value = 8
tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.35, 4, 1)
nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
cr = nt.nodes.new('ShaderNodeValToRGB')
cr.color_ramp.elements[0].color = lin('#1E1309'); cr.color_ramp.elements[1].color = lin('#4A2E18')
nt.links.new(wv.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
rbox((14, 16, 0.1), (0, 5.0, -0.05), wood, 0.01)

# the phone, face up, angled
body = mat('phone', '#0E1110', rough=0.25, metal=0.6, coat=0.8)
ph = rbox((0.98, 2.04, 0.06), (0, 0, 0.03), body, 0.09)
scr = bpy.data.materials.new('screen'); scr.use_nodes = True
st = scr.node_tree
for n_ in list(st.nodes):
    st.nodes.remove(n_)
o_ = st.nodes.new('ShaderNodeOutputMaterial'); em = st.nodes.new('ShaderNodeEmission'); tx = st.nodes.new('ShaderNodeTexImage')
mx = st.nodes.new('ShaderNodeMixShader'); gl = st.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.05
fr = st.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.5
tx.image = bpy.data.images.load(f'{S}/tex/screen.png')
st.links.new(tx.outputs['Color'], em.inputs['Color']); em.inputs['Strength'].default_value = 2.2
st.links.new(fr.outputs[0], mx.inputs['Fac']); st.links.new(em.outputs[0], mx.inputs[1]); st.links.new(gl.outputs[0], mx.inputs[2])
st.links.new(mx.outputs[0], o_.inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0605))
sp = bpy.context.object; sp.scale = (0.92, 1.96, 1); sp.data.materials.append(scr)
bpy.ops.object.empty_add(location=(0, 0, 0))
phone = bpy.context.object
for o in (ph, sp):
    o.parent = phone
phone.location = (0.72, 0.15, 0.0)
phone.rotation_euler = (0, 0, math.radians(-24))
# a soft lime light spilling from the phone (brand), plus the screen's own light
bpy.ops.object.light_add(type='POINT', location=(0.72, 0.15, 0.7))
pl = bpy.context.object; pl.data.energy = 14; pl.data.color = (0.62, 0.94, 0.42); pl.data.shadow_soft_size = 0.8

# candle in a glass, coffee cup and saucer
glass = mat('glass', '#FFFFFF', rough=0.04, trans=1.0, ior=1.45)
cyl(0.26, 0.5, (-1.35, 0.7, 0.25), glass)
cyl(0.2, 0.3, (-1.35, 0.7, 0.15), mat('wax', '#F2E8D8', rough=0.5, sss=0.3))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(-1.35, 0.7, 0.36), segments=16, ring_count=8)
fl = bpy.context.object; fl.scale = (0.7, 0.7, 1.6); fl.data.materials.append(mat('flame', '#FFB55A', emit='#FFB04A', estr=40))
bpy.ops.object.light_add(type='POINT', location=(-1.35, 0.7, 0.45))
cl = bpy.context.object; cl.data.energy = 30; cl.data.color = (1.0, 0.68, 0.36); cl.data.shadow_soft_size = 0.05
cyl(0.42, 0.04, (-0.55, -0.85, 0.02), mat('saucer', '#1F3A2C', rough=0.18, coat=0.8))
cup = cyl(0.27, 0.36, (-0.55, -0.85, 0.22), mat('cup', '#1F3A2C', rough=0.18, coat=0.8))
bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.03, location=(-0.27, -0.85, 0.24), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(bpy.data.materials['cup'])
cyl(0.24, 0.01, (-0.55, -0.85, 0.37), mat('coffee', '#2B160B', rough=0.1, coat=1.0))

# the empty room behind: bokeh lights, chair silhouettes, a window strip
rng = random.Random(4)
warm = [mat(f'bk{k}', '#FFB866', emit=c, estr=e) for k, (c, e) in enumerate((('#FFB866', 25), ('#FFD08A', 18), ('#FF9A4A', 22)))]
lime = mat('bkl', '#9DEF69', emit='#9DEF69', estr=10)
for k in range(46):
    x, y, z = rng.uniform(-6, 6), rng.uniform(8, 12), rng.uniform(0.8, 4.5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rng.uniform(0.06, 0.16), location=(x, y, z), segments=16, ring_count=8)
    bpy.context.object.data.materials.append(lime if k % 9 == 0 else warm[k % 3])
dark = mat('chairs', '#0C0F0D', rough=0.6)
for k in range(6):
    x = -4 + k * 1.6 + rng.uniform(-0.3, 0.3)
    rbox((0.5, 0.5, 0.06), (x, 7.2, 0.45), dark, 0.02)
    rbox((0.5, 0.06, 0.8), (x, 7.45, 0.85), dark, 0.02)
    for dx in (-0.22, 0.22):
        rbox((0.04, 0.04, 0.45), (x + dx, 7.2, 0.22), dark, 0)
rbox((20, 0.1, 8), (0, 13, 2.5), mat('backwall', '#101814', rough=0.8), 0)

# fill lights
bpy.ops.object.light_add(type='AREA', location=(-2.5, -2.5, 3.5))
k1 = bpy.context.object; k1.data.size = 4; k1.data.energy = 60; k1.data.color = (1.0, 0.8, 0.6)
k1.rotation_euler = (Vector((0, 0.3, 0)) - k1.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.light_add(type='AREA', location=(3.0, 3.0, 2.0))
k2 = bpy.context.object; k2.data.size = 3; k2.data.energy = 45; k2.data.color = (0.55, 0.9, 0.45)
k2.rotation_euler = (Vector((0.5, 0.3, 0)) - k2.location).to_track_quat('-Z', 'Y').to_euler()

cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.lens = 42
cam.location = (0.05, -4.3, 3.3)
target = Vector((-0.05, 0.05, 0.0))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.use_dof = True; cd.dof.aperture_fstop = 1.6
cd.dof.focus_distance = (Vector((0.72, 0.15, 0.06)) - cam.location).length
sc.render.filepath = f'{S}/render.png'
bpy.ops.render.render(write_still=True)
print('rendered', flush=True)
