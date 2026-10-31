"""Photoreal still: a paper wall calendar on a warm peach kitchen wall, late-afternoon window light through blinds,
orange magnet, a pen hanging on a string, a sprig of eucalyptus in a jar on the worktop below. 1080x1350, Cycles.

Usage: python3 blender_cal.py [samples]
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

S = '/home/user/100/workspace_respite'
SAMPLES = int(sys.argv[1]) if len(sys.argv) > 1 else 160


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
sc.render.film_transparent = False
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.cycles.device = 'CPU'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#FBE3D3')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.55


def material(name, col, rough=0.5, metal=0.0, coat=0.0, tex=None, bump=None, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(tex)
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if bump:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bump[0]; n.inputs['Detail'].default_value = 12
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump[1]; bp.inputs['Distance'].default_value = 0.002
        nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def box(size, loc, m, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 4
    o.data.materials.append(m)
    return o


# wall (y=0 plane facing -y) and worktop
wall = material('wall', lin('#F7C9AE'), rough=0.85, bump=(180, 0.25))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
w = bpy.context.object; w.scale = (14, 14, 1); w.data.materials.append(wall)
top = material('top', lin('#E9DED2'), rough=0.35, bump=(60, 0.05))
box((14, 1.4, 0.12), (0, -0.7, -2.55), top, bevel=0.01)
box((14, 1.36, 2.0), (0, -0.66, -3.6), material('cab', lin('#FDFBF7'), rough=0.4))

# calendar: subdivided plane with a gentle curl at the bottom, image texture
CW, CH = 2.2, 2.787
me = bpy.data.meshes.new('cal'); bm = bmesh.new()
nx, ny = 24, 36
verts = []
for j in range(ny + 1):
    row = []
    for i in range(nx + 1):
        u, v = i / nx, j / ny
        x = (u - 0.5) * CW; z = (v - 0.5) * CH
        curl = (1 - v) ** 3 * 0.12 + max(0, u - 0.7) * (1 - v) ** 2 * 0.25
        row.append(bm.verts.new((x, -0.012 - curl, z)))
    verts.append(row)
uv = bm.loops.layers.uv.new()
for j in range(ny):
    for i in range(nx):
        f = bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
        for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
            lp[uv].uv = (a / nx, b / ny)
bm.to_mesh(me); bm.free()
cal = bpy.data.objects.new('cal', me); sc.collection.objects.link(cal)
cal.data.materials.append(material('paper', (1, 1, 1, 1), rough=0.75, tex=f'{S}/tex/calendar.png', bump=(400, 0.05)))
sol = cal.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.006
for p in me.polygons:
    p.use_smooth = True
cal.location = (0.1, 0, -0.35)
cal.rotation_euler = (0, math.radians(-2.2), 0)

# orange magnet at the top
bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.09, location=(0.14, -0.06, 1.08), rotation=(math.radians(90), 0, 0), vertices=64)
mg = bpy.context.object; mg.data.materials.append(material('mag', lin('#FF6411'), rough=0.25, coat=0.8))
bv = mg.modifiers.new('b', 'BEVEL'); bv.width = 0.03; bv.segments = 6
bpy.ops.object.shade_smooth()

# pen on a string, hanging right of the calendar
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.85, location=(1.52, -0.05, -0.55), rotation=(0, math.radians(4), 0), vertices=32)
pen = bpy.context.object; pen.data.materials.append(material('pen', lin('#5B174F'), rough=0.3, coat=0.5))
bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cone_add(radius1=0.035, radius2=0.004, depth=0.12, location=(1.5, -0.05, -1.03), rotation=(math.radians(180), 0, 0), vertices=32)
bpy.context.object.data.materials.append(material('tip', lin('#F2F0EE'), rough=0.4))
cd = bpy.data.curves.new('str', 'CURVE'); cd.dimensions = '3D'
sp = cd.splines.new('BEZIER'); sp.bezier_points.add(1)
sp.bezier_points[0].co = (1.25, -0.03, 1.2); sp.bezier_points[1].co = (1.55, -0.05, -0.12)
for bp in sp.bezier_points:
    bp.handle_left_type = bp.handle_right_type = 'AUTO'
cd.bevel_depth = 0.006
so = bpy.data.objects.new('str', cd); sc.collection.objects.link(so); so.data.materials.append(material('string', lin('#C9B8A6'), rough=0.8))
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.05, location=(1.25, -0.02, 1.22), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(material('pin', lin('#B9A27A'), metal=1.0, rough=0.3))

# jar with eucalyptus sprigs on the worktop (left)
glass = material('glass', (0.95, 0.97, 0.96, 1), rough=0.02)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1.0
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.7, location=(-1.75, -0.45, -2.14), vertices=64)
bpy.context.object.data.materials.append(glass); bpy.ops.object.shade_smooth()
leaf = material('leaf', lin('#7E9C86'), rough=0.6, sss=0.2)
stem = material('stem', lin('#6B7F5F'), rough=0.6)
import random
random.seed(4)
for s_ in range(5):
    ang = -0.5 + s_ * 0.25
    L = 1.4 + random.random() * 0.5
    x0, z0 = -1.75 + random.uniform(-0.08, 0.08), -2.3
    tip = (x0 + math.sin(ang) * L, -0.45 + random.uniform(-0.1, 0.1), z0 + math.cos(ang) * L)
    cd2 = bpy.data.curves.new('st', 'CURVE'); cd2.dimensions = '3D'; sp2 = cd2.splines.new('POLY'); sp2.points.add(1)
    sp2.points[0].co = (x0, -0.45, z0, 1); sp2.points[1].co = (*tip, 1); cd2.bevel_depth = 0.008
    o2 = bpy.data.objects.new('st', cd2); sc.collection.objects.link(o2); o2.data.materials.append(stem)
    for k in range(9):
        f = 0.25 + k * 0.085
        p = (x0 + (tip[0] - x0) * f, -0.45 + (tip[1] + 0.45) * f, z0 + (tip[2] - z0) * f)
        for side in (-1, 1):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1 - k * 0.006, location=(p[0] + side * 0.09, p[1], p[2]), segments=16, ring_count=8)
            lf = bpy.context.object; lf.scale = (1, 0.18, 0.75); lf.data.materials.append(leaf)
            lf.rotation_euler = (0, side * 0.6 + ang, random.uniform(-0.4, 0.4))

# mug on the worktop (right)
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.62, location=(1.65, -0.6, -2.18), vertices=64)
mug = bpy.context.object; mug.data.materials.append(material('mug', lin('#FFFDF9'), rough=0.2, coat=0.6)); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.045, location=(1.97, -0.6, -2.15), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(bpy.data.materials['mug'])

# window light through blinds: sun from the right, slats off-camera
sun_rot = (math.radians(58), 0, math.radians(62))
bpy.ops.object.light_add(type='SUN', rotation=sun_rot)
sun = bpy.context.object; sun.data.energy = 5.2; sun.data.color = (1.0, 0.78, 0.55); sun.data.angle = math.radians(1.6)
d = sun.matrix_world.to_quaternion() @ Vector((0, 0, -1))

bpy.ops.object.light_add(type='AREA', location=(-3.5, -6, 2.5))
fill = bpy.context.object; fill.data.energy = 350; fill.data.size = 6; fill.data.color = (1.0, 0.9, 0.85)
fill.rotation_euler = (math.radians(70), 0, math.radians(-30))

# camera
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.lens = 50
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = 7.9; cam_d.dof.aperture_fstop = 5.6
cam.location = (0.0, -7.9, -0.1)
look = Vector((0.12, 0, 0.12)) - cam.location
cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()

sc.render.filepath = f'{S}/tex/cal_render.png'
bpy.ops.render.render(write_still=True)
print('rendered')
