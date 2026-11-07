"""Glossy 3D tokens for "One Weekend" (brand palette): weekend bag, bucket & spade, crescent moon, heart-house.
Usage: python3 blender_owtok.py [bag bucket moon]
"""
import bpy, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_cf as C
from blender_cf import setup, gloss, sphere, PURPLE, ORANGE, PLUM, IVORY, LAV, PEACH, LEAF
from blender_lo import lin, mat

C.OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_ow', 'assets'))
shot = C.shot


def rbox(size, loc, m, bevel=0.1, rot=(0, 0, 0), seg=6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg; bv.limit_method = 'NONE'
    o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def torus(R, r, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=64, minor_segments=20)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return o


def spin(deg):
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE') and o.parent is None:
            o.rotation_euler[2] += math.radians(deg)


def bag():
    setup()
    body = gloss('bag', PURPLE, rough=0.35, coat=0.5)
    b = rbox((2.4, 1.1, 1.2), (0, 0, 0), body, 0.45, seg=10)
    sub = b.modifiers.new('s', 'SUBSURF'); sub.levels = 2; sub.render_levels = 2
    rbox((2.42, 1.12, 0.12), (0, 0, 0.32), gloss('zip', ORANGE, rough=0.3), 0.05)
    for x in (-0.55, 0.55):
        torus(0.42, 0.07, (x, 0, 0.62), gloss('handle', PLUM), rot=(math.radians(90), 0, 0))
    rbox((0.9, 0.06, 0.5), (0.5, -0.56, -0.12), gloss('pocket', '#D2006F', rough=0.35), 0.08)
    rbox((0.5, 0.05, 0.32), (-0.6, -0.57, -0.1), gloss('tag', IVORY, rough=0.4), 0.06)
    spin(-18)
    shot('bag', (0.6, -7.4, 1.6), (0, 0, 0.1))


def bucket():
    setup()
    bpy.ops.mesh.primitive_cone_add(radius1=0.7, radius2=0.95, depth=1.3, location=(0, 0, -0.2), vertices=64, end_fill_type='NGON')
    bk = bpy.context.object; bk.data.materials.append(gloss('bucket', ORANGE, rough=0.25)); bpy.ops.object.shade_smooth()
    sol = bk.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.06
    torus(0.96, 0.06, (0, 0, 0.45), gloss('rim', '#FF8A3D'))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.035, location=(0, 0, 0.45), rotation=(math.radians(90), 0, 0), major_segments=64)
    h = bpy.context.object; h.data.materials.append(gloss('handle', PLUM)); bpy.ops.object.shade_smooth()
    h.scale = (1, 1, 0.8)
    rbox((0.16, 0.08, 1.7), (0.85, -0.25, 0.5), gloss('spade', PURPLE), 0.06, rot=(0, math.radians(18), 0))
    rbox((0.5, 0.1, 0.6), (1.1, -0.25, -0.35), gloss('blade', PURPLE), 0.12, rot=(0, math.radians(18), 0))
    sphere(0.45, (0, 0, 0.45), gloss('sand', '#F2C98A', rough=0.8, coat=0.0), (1, 1, 0.35))
    spin(-14)
    shot('bucket', (0.6, -7.6, 1.8), (0.2, 0, 0.1))


def moon():
    setup()
    m = gloss('moon', '#FFD27A', rough=0.3, coat=0.6)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.15, depth=0.36, location=(0, 0, 0), rotation=(math.radians(90), 0, 0), vertices=128)
    disc = bpy.context.object; disc.data.materials.append(m)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.98, depth=1.0, location=(0.52, 0, 0.22), rotation=(math.radians(90), 0, 0), vertices=128)
    cut = bpy.context.object; cut.hide_render = True
    bo = disc.modifiers.new('b', 'BOOLEAN'); bo.object = cut; bo.solver = 'EXACT'
    bv = disc.modifiers.new('bv', 'BEVEL'); bv.width = 0.1; bv.segments = 8; bv.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = disc
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(45))
    disc.rotation_euler[1] = math.radians(-18)
    for x, z, rr in ((1.2, 0.95, 0.11), (1.4, -0.55, 0.08), (-1.3, 1.15, 0.07)):
        sphere(rr, (x, 0, z), gloss('star', IVORY, rough=0.2))
    shot('moon', (0.4, -7.2, 0.3), (0, 0, 0))


ALL = dict(bag=bag, bucket=bucket, moon=moon)
if __name__ == '__main__':
    for n in (sys.argv[1:] or list(ALL)):
        ALL[n]()
