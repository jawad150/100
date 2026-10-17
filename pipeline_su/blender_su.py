"""Extra 3D clay icons for "Support Update Available" (reuses the Fostering Flow clay toolkit).

Usage: python3 blender_su.py <asset> [...]
Assets: clock book group sync
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_su'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ff'))
import bpy
import blender_ff as F
from blender_ff import clay, setup, root, rbox, sphere, cyl, sway, lin, PLUM, MAGENTA, ORANGE, GREEN, IVORY, PEACH, LILAC


def clock():
    setup()
    e = root()
    cyl(1.05, 0.36, (0, 0, 0), clay('rim', MAGENTA), rot=(math.radians(90), 0, 0), parent=e, bevel=0.12)
    cyl(0.86, 0.12, (0, -0.16, 0), clay('face', IVORY, rough=0.5), rot=(math.radians(90), 0, 0), parent=e, bevel=0.03)
    tick = clay('tick', LILAC)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        rbox((0.06, 0.06, 0.16 if k % 3 == 0 else 0.09), (0.68 * math.sin(a), -0.24, 0.68 * math.cos(a)), tick,
             bevel=0.02, parent=e, rot=(0, a, 0))
    hand = clay('hand', PLUM)
    rbox((0.09, 0.07, 0.5), (0.0, -0.3, 0.22), hand, bevel=0.03, parent=e)
    rbox((0.08, 0.07, 0.62), (0.25, -0.32, -0.12), hand, bevel=0.03, parent=e, rot=(0, math.radians(-120), 0))
    sphere(0.09, (0, -0.34, 0), clay('pin', ORANGE), parent=e)
    for sx in (-1, 1):   # little alarm bells
        sphere(0.26, (sx * 0.7, 0.05, 0.92), clay('bell', ORANGE), parent=e, scale=(1, 1, 0.7))
    sway(e, 'clock')


def book():
    setup(cam=(0, -6.4, 1.8))
    e = root()
    for sx, col in ((-1, MAGENTA), (1, ORANGE)):
        cover = rbox((1.15, 0.1, 1.6), (sx * 0.58, 0.1, 0), clay('cv%d' % sx, col), bevel=0.06, parent=e,
                     rot=(0, 0, math.radians(sx * 14)))
        rbox((1.05, 0.12, 1.48), (sx * 0.55, -0.02, 0), clay('pg%d' % sx, IVORY, rough=0.55), bevel=0.04, parent=e,
             rot=(0, 0, math.radians(sx * 12)))
        ln = clay('ln%d' % sx, LILAC)
        for j in range(4):
            rbox((0.7, 0.03, 0.07), (sx * 0.56, -0.1 - sx * 0.04, 0.45 - j * 0.28), ln, bevel=0.02, parent=e,
                 rot=(0, 0, math.radians(sx * 12)))
    cyl(0.07, 1.62, (0, 0.16, 0), clay('spine', PLUM), parent=e, bevel=0)
    sway(e, 'book', amp=22, base=(0, 0, 0))


def group():
    setup()
    e = root()
    for x, z, s, col in ((-0.75, -0.05, 0.82, ORANGE), (0.75, -0.05, 0.82, GREEN), (0, 0.12, 1.0, MAGENTA)):
        y = 0.25 if s < 1 else -0.1
        sphere(0.42 * s, (x, y, z + 0.62 * s), clay('h%.1f' % x, PEACH), parent=e)
        sphere(0.7 * s, (x, y, z - 0.42 * s), clay('b%.1f' % x, col), parent=e, scale=(1.05, 0.72, 0.62))
    sway(e, 'group', amp=22)


def sync():
    """Circular 'update' arrows (two curved arrows chasing each other)."""
    setup()
    e = root()
    m = clay('arw', ORANGE, coat=0.6)
    for k in range(2):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.17, major_segments=96, minor_segments=24,
                                         rotation=(math.radians(90), 0, 0))
        t = bpy.context.object
        bpy.ops.object.shade_smooth()
        # keep a 140-degree arc of each torus
        bpy.ops.object.mode_set(mode='EDIT')
        import bmesh
        bm = bmesh.from_edit_mesh(t.data)
        a0 = k * math.pi
        dele = [v for v in bm.verts if not (0.15 < ((math.atan2(v.co.z, v.co.x) - a0) % (2 * math.pi)) < 2.6)]
        bmesh.ops.delete(bm, geom=dele, context='VERTS')
        bmesh.update_edit_mesh(t.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        t.data.materials.append(m)
        t.parent = e
        a = a0 + 2.6
        bpy.ops.mesh.primitive_cone_add(radius1=0.36, depth=0.5, location=(0.85 * math.cos(a), 0, 0.85 * math.sin(a)),
                                        rotation=(0, -a, 0), vertices=48)
        c = bpy.context.object
        bpy.ops.object.shade_smooth()
        c.data.materials.append(m)
        c.parent = e
    sphere(0.3, (0, 0, 0), clay('core', MAGENTA), parent=e)
    sway(e, 'sync', amp=18)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
