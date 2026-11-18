"""Organic Fostering "The letter you never received": a photoreal 3D still-life in the editorial flash-photo style of the
reference (satin ribbons, velvet curtain, lace cloth, vintage china), recoloured to the brand (plum velvet, magenta
satin, ivory damask). The letter (reasons, crossed out) lies on the table; the plum card with the turn-around line is
tied with a magenta satin bow; an envelope "To: you", a teacup, a candle.

Run: blender -b -P blender_letter.py -- A|B [draft|final]
  A = angled still-life (curtain behind)   B = top-down flat lay
-> workspace_letter/render/<layout>_<quality>.png (1080x1350, 4:5)
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TEX = f'{ROOT}/workspace_letter/tex'
OUT = f'{ROOT}/workspace_letter/render'
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
LAYOUT = argv[0] if argv else 'A'
Q = argv[1] if len(argv) > 1 else 'draft'


def lin(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (a,)


PLUM, MAG, ORANGE, GREEN = lin('#5B174F'), lin('#B7006E'), lin('#FF6411'), lin('#61A80A')
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 48 if Q == 'draft' else 384
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.render.resolution_percentage = 50 if Q == 'draft' else 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = lin('#2A0C26')
w.node_tree.nodes['Background'].inputs[1].default_value = 0.4


def mat(name, col, rough=0.5, metal=0.0, coat=0.0, sheen=0.0, aniso=0.0, trans=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
        b.inputs['Sheen Roughness'].default_value = 0.35
        b.inputs['Sheen Tint'].default_value = (1.0, 0.75, 0.9, 1)
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    return m


def img_mat(name, path, rough=0.8, repeat=1.0, bump=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path)
    if repeat != 1.0:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (repeat, repeat, 1)
        nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if bump:
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 400
        bp_ = nt.nodes.new('ShaderNodeBump')
        bp_.inputs['Strength'].default_value = bump
        nt.links.new(nz.outputs['Fac'], bp_.inputs['Height'])
        nt.links.new(bp_.outputs['Normal'], b.inputs['Normal'])
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


def sheet(w, h, loc, rotz, m, thick=0.004, bend=0.0, sub=24):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=(0, 0, math.radians(rotz)))
    o = act()
    o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=sub)
    bpy.ops.object.mode_set(mode='OBJECT')
    if bend:
        for v in o.data.vertices:
            u = v.co.y / (h / 2)
            v.co.z += bend * (u ** 2) * 0.5 + bend * 0.12 * (v.co.x / (w / 2)) ** 2
    s = o.modifiers.new('s', 'SOLIDIFY')
    s.thickness = thick
    smooth(o)
    return setm(o, m)


def ribbon(pts, width, m, tilt=None):
    """Satin ribbon: a flat strip swept along a bezier path, given a little thickness."""
    cu = bpy.data.curves.new('rib', 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for i, (p, q) in enumerate(zip(sp.bezier_points, pts)):
        p.co = q
        p.handle_left_type = p.handle_right_type = 'AUTO'
        if tilt:
            p.tilt = tilt[i]
    cu.extrude = width / 2
    cu.resolution_u = 24
    o = bpy.data.objects.new('rib', cu)
    sc.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o = act()
    s = o.modifiers.new('s', 'SOLIDIFY')
    s.thickness = 0.006
    smooth(o)
    o.select_set(False)
    return setm(o, m)


def bow(cx, cy, cz, s, m, rot=0.0):
    """A satin bow: two loops and two tails."""
    c, sn = math.cos(rot), math.sin(rot)
    def R(x, y, z):
        return (cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s, cz + z * s)
    for side in (-1, 1):
        ribbon([R(0, 0, 0.02), R(0.35 * side, 0.2, 0.18), R(0.66 * side, 0.06, 0.14), R(0.48 * side, -0.16, 0.06), R(0.02, 0, 0.02)],
               0.24 * s, m, tilt=[0, 0.4 * side, 0.9 * side, 0.4 * side, 0])
        ribbon([R(0.02 * side, 0, 0.0), R(0.18 * side, -0.35, 0.0), R(0.28 * side, -0.75, -0.02), R(0.45 * side, -1.05, -0.02)],
               0.22 * s, m, tilt=[0, 0.3, -0.3, 0.2])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08 * s, location=R(0, 0, 0.04))
    k = smooth(act())
    k.scale = (1.2, 0.9, 0.7)
    setm(k, m)


# ------------------------------------------------------------------ materials
satin = mat('satin', MAG, 0.18, coat=0.4, aniso=0.85, sheen=0.4)
velvet = mat('velvet', lin('#4A1040'), 0.85, sheen=1.0)
porcelain = mat('porc', lin('#FBF6F0'), 0.12, coat=1.0)
silver = mat('silver', lin('#D9DCE0'), 0.15, metal=1.0)
wax = mat('wax', lin('#FFFDF8'), 0.4)
flame = bpy.data.materials.new('flame')
flame.use_nodes = True
fl = flame.node_tree.nodes['Principled BSDF']
fl.inputs['Emission Color'].default_value = (1.0, 0.6, 0.2, 1)
fl.inputs['Emission Strength'].default_value = 40
letter_m = img_mat('letter', f'{TEX}/letter.png', 0.75, bump=0.04)
card_m = img_mat('card', f'{TEX}/card.png', 0.55, bump=0.03)
env_m = img_mat('env', f'{TEX}/envelope.png', 0.8, bump=0.04)
cloth_m = img_mat('cloth', f'{TEX}/damask.png', 0.7, repeat=4.0, bump=0.08)

# ------------------------------------------------------------------ table + curtain
bpy.ops.mesh.primitive_plane_add(size=16, location=(0, 0, 0))
t = act()
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=60)
bpy.ops.object.mode_set(mode='OBJECT')
d = t.modifiers.new('d', 'DISPLACE')
tx = bpy.data.textures.new('wr', 'CLOUDS')
tx.noise_scale = 1.4
d.texture = tx
d.strength = 0.05
smooth(t)
setm(t, cloth_m)
if LAYOUT == 'A':
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 3.6, 3.0), rotation=(math.radians(90), 0, 0))
    cur = act()
    cur.scale = (14, 7, 1)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=120)
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in cur.data.vertices:
        x = v.co.x
        v.co.z += 0.34 * math.sin(x * 3.1) + 0.12 * math.sin(x * 7.3 + 1.3) + 0.05 * math.sin(x * 15)
    smooth(cur)
    setm(cur, velvet)

# ------------------------------------------------------------------ the letter, envelope, card
env = sheet(2.5, 1.66, (-1.15, 0.85, 0.01), 14, env_m, bend=0.02)
let = sheet(2.2, 2.85, (0.0, -0.05, 0.03), -6, letter_m, thick=0.003, bend=0.05)
card = sheet(2.1, 1.0, (0.55, -1.25, 0.09), 9, card_m, thick=0.012, bend=0.0, sub=4)
# ribbon tied round the card (two bands) and the bow
cx, cy = 0.55, -1.25
c9, s9 = math.cos(math.radians(9)), math.sin(math.radians(9))
def onc(x, y, z):
    return (cx + x * c9 - y * s9, cy + x * s9 + y * c9, z)
ribbon([onc(0.84, -0.62, 0.0), onc(0.84, -0.5, 0.11), onc(0.85, 0.0, 0.112), onc(0.84, 0.5, 0.11), onc(0.84, 0.62, 0.0)], 0.24, satin)
bow(*onc(0.84, 0.6, 0.12), 0.62, satin, rot=0.0)
# loose ribbons trailing across the cloth
ribbon([(-2.6, -1.6, 0.012), (-1.6, -2.1, 0.05), (-0.6, -2.5, 0.012), (0.6, -2.8, 0.06), (2.0, -2.6, 0.012)], 0.3, satin,
       tilt=[0, 1.2, 2.6, 3.4, 4.2])
ribbon([(1.6, 0.3, 0.012), (2.0, -0.3, 0.05), (2.6, -0.7, 0.015), (3.3, -0.4, 0.04)], 0.28, satin, tilt=[0, 1.5, 2.4, 3.0])

# ------------------------------------------------------------------ teacup + saucer, candle
def teacup(x, y):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.62, depth=0.06, location=(x, y, 0.03), vertices=96)
    smooth(setm(act(), porcelain))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.025, location=(x, y, 0.065))
    smooth(setm(act(), satin))
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.42, depth=0.5, location=(x, y, 0.31), vertices=96)
    cup = act()
    s = cup.modifiers.new('s', 'SOLIDIFY')
    s.thickness = 0.025
    bm = bmesh.new()
    bm.from_mesh(cup.data)
    top = [f for f in bm.faces if f.normal.z > 0.9 and f.calc_center_median().z > 0.2]
    bmesh.ops.delete(bm, geom=top, context='FACES')
    bm.to_mesh(cup.data)
    bm.free()
    smooth(setm(cup, porcelain))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.415, minor_radius=0.03, location=(x, y, 0.49))
    smooth(setm(act(), satin))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.02, location=(x, y, 0.44), vertices=64)
    setm(act(), mat('tea', lin('#7A3A1C'), 0.05))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.035, location=(x + 0.45, y, 0.32), rotation=(math.radians(90), 0, 0))
    smooth(setm(act(), porcelain))


def candle(x, y, h=1.6):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.06, location=(x, y, 0.03), vertices=64)
    smooth(setm(act(), silver))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=h * 0.55, location=(x, y, h * 0.3), vertices=32)
    smooth(setm(act(), silver))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.1, location=(x, y, h * 0.6), vertices=48)
    smooth(setm(act(), silver))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=h * 0.6, location=(x, y, h * 0.6 + h * 0.3), vertices=48)
    smooth(setm(act(), wax))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(x, y, h * 1.25))
    f = act()
    f.scale = (0.7, 0.7, 1.9)
    setm(f, flame)
    L = bpy.data.objects.new('cl', bpy.data.lights.new('cl', 'POINT'))
    L.data.energy, L.data.color, L.data.shadow_soft_size = 25, (1.0, 0.62, 0.3), 0.05
    L.location = (x, y, h * 1.27)
    sc.collection.objects.link(L)
    ribbon([(x + 0.06, y, h * 0.62), (x + 0.3, y - 0.1, h * 0.45), (x + 0.42, y - 0.25, h * 0.2), (x + 0.55, y - 0.4, 0.02)], 0.2, satin,
           tilt=[0, 0.8, 1.6, 2.2])


teacup(2.15, 1.05)
candle(-2.0, 1.95 if LAYOUT == 'A' else 2.4, 1.7)

# a sprig: three little leaves on a stem (brand leaf, green)
leafm = mat('leaf', GREEN, 0.4)
for i, (lx, ly, r) in enumerate(((-1.85, -0.9, 30), (-1.65, -1.1, -20), (-2.05, -1.15, 70))):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(lx, ly, 0.03))
    lf = act()
    lf.scale = (1.0, 0.42, 0.12)
    lf.rotation_euler = (0, 0, math.radians(r))
    smooth(setm(lf, leafm))

# ------------------------------------------------------------------ light ("on-camera flash" + warm fill) and camera
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'
if LAYOUT == 'A':
    cam.data.lens = 46
    cam.location = (0.2, -7.6, 5.4)
    target = Vector((0.1, -0.35, 0.3))
else:
    cam.data.lens = 50
    cam.location = (0.15, -0.4, 10.2)
    target = Vector((0.15, -0.35, 0))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (target - cam.location).length
cam.data.dof.aperture_fstop = 3.2 if LAYOUT == 'A' else 8.0

flash = bpy.data.objects.new('flash', bpy.data.lights.new('flash', 'AREA'))
flash.data.energy, flash.data.size = 900, 0.6
flash.location = cam.location + Vector((0.4, 0.0, 0.5))
flash.rotation_euler = (target - flash.location).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(flash)
fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'AREA'))
fill.data.energy, fill.data.size, fill.data.color = 180, 4, (1.0, 0.82, 0.7)
fill.location = (-5, -2, 6)
fill.rotation_euler = (Vector((0, 0, 0)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(fill)
graze = bpy.data.objects.new('graze', bpy.data.lights.new('graze', 'SPOT'))
graze.data.energy, graze.data.spot_size, graze.data.color = 2500, math.radians(50), (1.0, 0.8, 0.85)
graze.location = (-7, 2.0, 4.5)
graze.rotation_euler = (Vector((0, 3.5, 3.0)) - graze.location).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(graze)

sc.render.filepath = f'{OUT}/{LAYOUT}_{Q}.png'
bpy.ops.render.render(write_still=True)
print('rendered', LAYOUT, Q)
