"""Photoreal still life: a family photo book on a light oak table with a cream linen runner, soft morning light.

Modes: open_top (overhead flat lay), open_angle (low 3/4 close-up on page one), closed (closed book, prints spilling out)
Usage: python3 blender_fb.py <mode> [samples]
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

S = '/home/user/100/workspace_fb'
T = f'{S}/tex'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'open_top'
SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 128


def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#FFF3E6')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6


def material(name, col=(1, 1, 1, 1), rough=0.5, tex=None, bump=0.0, coat=0.0, metal=0.0, alpha_tex=False, trans=0.0, scale=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Metallic'].default_value = metal
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(tex)
        if scale:
            mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord')
            mp.inputs['Scale'].default_value = scale
            nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if bump:
            bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.003
            nt.links.new(t.outputs['Color'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def plane(w, h, loc, mat, rot_z=0.0, thick=0.0, name='p', bend=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.name = name
    o.scale = (w, h, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler = (0, 0, math.radians(rot_z))
    if bend:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=12); bpy.ops.object.mode_set(mode='OBJECT')
        for v in o.data.vertices:
            v.co.z += bend * (abs(v.co.x) / (w / 2)) ** 2
    if thick:
        s = o.modifiers.new('s', 'SOLIDIFY'); s.thickness = thick; s.offset = 1
    o.data.materials.append(mat)
    return o


def box(size, loc, mat, rot_z=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler = (0, 0, math.radians(rot_z))
    if bevel:
        bv = o.modifiers.new('b', 'BEVEL'); bv.width = bevel; bv.segments = 4
    o.data.materials.append(mat)
    return o


def rotp(x, y, ang, cx=0, cy=0):
    a = math.radians(ang)
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


# table + linen runner
plane(9, 11, (0, 0, 0), material('oak', tex=f'{T}/oak.png', rough=0.42, bump=0.12, coat=0.15, scale=(1.6, 1.3, 1)), name='table')
runner = plane(9, 1.9, (0, 1.75, 0.004), material('linen', tex=f'{T}/linen.png', rough=0.9, bump=0.4), name='runner', thick=0.01)

TAPE_O = material('tapeO', lin('#FF6411'), rough=0.6); TAPE_P = material('tapeP', lin('#FFC8A8'), rough=0.6)
for m in (TAPE_O, TAPE_P):
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Alpha'].default_value = 0.82


def print_(name, w, loc, rot, tape=True, lift=0.0):
    img = bpy.data.images.load(f'{T}/print_{name}.png')
    ar = img.size[0] / img.size[1]
    m = material('pr_' + name, rough=0.35, coat=0.25)
    t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img
    m.node_tree.links.new(t.outputs['Color'], m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    o = plane(w, w / ar, loc, m, rot_z=rot, thick=0.006, name='print_' + name)
    o.location.z += lift
    if tape:
        for sx, sy, tr in ((-0.42, 0.5, 35), (0.42, 0.5, -30)):
            x, y = rotp(sx * w, sy * w / ar, rot, loc[0], loc[1])
            plane(w * 0.26, w * 0.075, (x, y, loc[2] + lift + 0.009), TAPE_O if name in ('room', 'pizza') else TAPE_P, rot_z=rot + tr, name='tape')
    return o


def page_block(w, h, loc, rot, tex, side, curl=0.06):
    me = bpy.data.meshes.new('pg'); bm = bmesh.new(); nx, ny = 30, 6
    vs = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            x = (u - 0.5) * w; y = (v - 0.5) * h
            dist = (1 - u) if side == 'r' else u
            z = 0.075 - curl * math.exp(-dist * 9) + 0.012 * math.sin(u * math.pi)
            row.append(bm.verts.new((x, y, z)))
        vs.append(row)
    uv = bm.loops.layers.uv.new()
    for j in range(ny):
        for i in range(nx):
            f = bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uv].uv = (a / nx, b / ny)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('page', me); sc.collection.objects.link(o)
    for p in me.polygons:
        p.use_smooth = True
    o.data.materials.append(material('page' + side, tex=tex, rough=0.8, bump=0.05))
    sl = o.modifiers.new('s', 'SOLIDIFY'); sl.thickness = 0.06; sl.offset = -1
    o.location = loc; o.rotation_euler = (0, 0, math.radians(rot))
    return o


SAGE = material('sage', tex=f'{T}/sage_linen.png', rough=0.85, bump=0.3)
BX, BY, BR = 0.0, -0.42, -3.0       # open book centre and rotation
PW_, PH_ = 1.68, 2.2

if MODE in ('open_top', 'open_angle'):
    for side, dx in (('l', -1), ('r', 1)):
        x, y = rotp(dx * (PW_ / 2 + 0.04), 0, BR, BX, BY)
        box((PW_ + 0.1, PH_ + 0.12, 0.05), (x, y, 0.03), SAGE, rot_z=BR, bevel=0.02)
        page_block(PW_, PH_, (x, y, 0.0), BR, f'{T}/page_left.png' if side == 'l' else f'{T}/page_right.png', side)
    sx, sy = rotp(0, 0, BR, BX, BY)
    box((0.12, PH_ + 0.12, 0.06), (sx, sy, 0.025), SAGE, rot_z=BR, bevel=0.03)
    # prints on the right page (relative to book centre, page coords)
    def onpage(px, py):
        return rotp(px, py, BR, BX, BY)
    x, y = onpage(-0.55, 0.0 - 0.66 + 0.0)
    x, y = onpage(-0.95 + 0.0, -0.55)   # kitchen print on the left page, lower half
    print_('kitchen', 1.06, (x, y, 0.105), BR + 3)
    x, y = onpage(0.62, 0.42); print_('room', 0.92, (x, y, 0.1), BR - 4)
    x, y = onpage(1.36, 0.58); print_('dog', 0.56, (x, y, 0.118), BR + 5)
    x, y = onpage(0.86, -0.6); print_('park', 1.12, (x, y, 0.1), BR + 2)
    nm = material('note', tex=f'{T}/note_pizza.png', rough=0.8)
    x, y = rotp(1.42, -0.92, BR, BX, BY)
    o = plane(0.92, 0.6, (x, y, 0.13), nm, rot_z=BR + 9, thick=0.004, name='note')
    plane(0.26, 0.075, (x - 0.05, y + 0.3, 0.14), TAPE_O, rot_z=BR + 14, name='tape')
else:
    # closed book, slightly turned, prints spilling out from under it
    bx, by, br = -0.2, -0.45, 9
    box((PW_ + 0.12, PH_ + 0.14, 0.32), (bx, by, 0.16), SAGE, rot_z=br, bevel=0.03)
    box((PW_ + 0.02, PH_ + 0.06, 0.28), (bx + 0.05, by, 0.16), material('pages', lin('#F8F2E4'), rough=0.85), rot_z=br, bevel=0.01)
    lm = material('label', tex=f'{T}/cover_label.png', rough=0.8)
    lx, ly = rotp(0, 0.35, br, bx, by)
    plane(1.08, 0.62, (lx, ly, 0.325), lm, rot_z=br, thick=0.003, name='label')
    prints = [('dog', 0.66, (1.25, 0.2), -14), ('room', 0.95, (1.45, -0.75), 8), ('park', 1.15, (-1.25, -1.75), -9),
              ('kitchen', 1.05, (0.75, -1.85), 5), ('pizza', 0.62, (-1.55, 0.35), 16)]
    for k, (n, w, (x, y), r) in enumerate(prints):
        print_(n, w, (x, y, 0.012 + k * 0.004), r, tape=False)
    nm = material('note', tex=f'{T}/note_pizza.png', rough=0.8)
    plane(0.92, 0.6, (1.35, -0.25 + 0.0, 0.03), nm, rot_z=-6, thick=0.004, name='note')

# mug of tea, right edge
mug = material('mug', lin('#FFFDF8'), rough=0.18, coat=0.6)
bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.62, location=(2.05, 0.55, 0.31), vertices=96)
o = bpy.context.object; o.data.materials.append(mug); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_cylinder_add(radius=0.36, depth=0.01, location=(2.05, 0.55, 0.625), vertices=96)
bpy.context.object.data.materials.append(material('tea', lin('#8A4A22'), rough=0.05, coat=1.0))
bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.05, location=(1.6, 0.55, 0.33), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(mug)
# pencil
if MODE != 'open_angle':
  pen = material('pencil', lin('#5B174F'), rough=0.35, coat=0.4)
  bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.25, location=(-1.75, 0.95, 0.04), rotation=(0, math.radians(90), math.radians(-24)), vertices=6)
  bpy.context.object.data.materials.append(pen)
# light: soft morning sun from the upper left + window fill
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(38), math.radians(-22), math.radians(-35)))
sun = bpy.context.object; sun.data.energy = 3.6; sun.data.color = (1.0, 0.9, 0.76); sun.data.angle = math.radians(6)
bpy.ops.object.light_add(type='AREA', location=(-5, 4, 6))
a = bpy.context.object; a.data.energy = 900; a.data.size = 6; a.data.color = (0.95, 0.96, 1.0)
a.rotation_euler = (math.radians(40), math.radians(-35), math.radians(-40))

cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
if MODE in ('open_top', 'closed'):
    cam_d.lens = 102
    cam.location = (0.0, -0.05, 14.6)
    cam.rotation_euler = (0, 0, 0)
    cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36
else:
    cam_d.lens = 75
    cam_d.dof.use_dof = True
    tgt = Vector(rotp(-0.9, -0.15, BR, BX, BY) + (0.1,))
    cam.location = tgt + Vector((0.4, -4.6, 3.6))
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_d.dof.focus_distance = (tgt - cam.location).length
    cam_d.dof.aperture_fstop = 2.2
    cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36

sc.render.filepath = f'{S}/tex/render_{MODE}.png'
for o in bpy.data.objects:
    if o.name.startswith('tape'):
        print('TAPE', o.name, tuple(round(v, 2) for v in o.location))
bpy.ops.render.render(write_still=True)
print('rendered', MODE)
