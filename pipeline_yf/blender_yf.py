"""3D clay icons for "Your Year in Fostering" (reuses the Fostering Flow clay toolkit).

Usage: python3 blender_yf.py <asset> [...]
Assets: pizza books gift year
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_yf'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ff'))
import bpy
import blender_ff as F
from blender_ff import clay, setup, root, rbox, sphere, cyl, sway, lin, mat, PLUM, MAGENTA, ORANGE, GREEN, IVORY, PEACH, LILAC

CRUST = lin('#E39B4D')
CHEESE = lin('#FFCF5A')
PEPPER = lin('#C8263C')


def pizza():
    setup(cam=(0, -6.0, 3.2))
    e = root()
    cyl(1.25, 0.26, (0, 0, 0), clay('crust', CRUST), parent=e, bevel=0.12, verts=96)
    cyl(1.08, 0.12, (0, 0, 0.12), clay('cheese', CHEESE, rough=0.35), parent=e, bevel=0.05, verts=96)
    pm = clay('pep', PEPPER, coat=0.6)
    for (x, y) in [(-0.5, 0.3), (0.35, 0.5), (0.55, -0.25), (-0.2, -0.45), (0.0, 0.05), (-0.65, -0.25), (0.15, 0.85)]:
        cyl(0.2, 0.06, (x, y, 0.2), pm, parent=e, bevel=0.03)
    g = clay('basil', GREEN)
    for (x, y, a) in [(-0.3, 0.65, 30), (0.65, 0.2, -40), (-0.45, -0.7, 70)]:
        sphere(0.12, (x, y, 0.22), g, parent=e, scale=(1.6, 0.8, 0.3))
    sway(e, 'pizza', amp=20, tilt=8, base=(28, 0, 0))


def books():
    setup(cam=(1.2, -6.2, 1.8))
    e = root()
    page = clay('page', IVORY, rough=0.55)
    z = -0.9
    for j, (col, w, d, h, rot) in enumerate([(MAGENTA, 2.0, 1.4, 0.36, 4), (ORANGE, 1.8, 1.3, 0.3, -6),
                                             (GREEN, 1.9, 1.35, 0.34, 8), (PLUM, 1.6, 1.2, 0.3, -3)]):
        z += h / 2
        b = rbox((w, d, h), (0, 0, z), clay('cv%d' % j, col), bevel=0.06, parent=e,
                 rot=(0, 0, math.radians(rot)))
        rbox((w - 0.1, d - 0.12, h - 0.1), (0.06, 0, z), page, bevel=0.03, parent=e,
             rot=(0, 0, math.radians(rot)))
        z += h / 2 + 0.01
    sway(e, 'books', amp=18)


def gift():
    setup(cam=(1.0, -6.3, 1.9))
    e = root()
    rbox((1.6, 1.6, 1.3), (0, 0, -0.35), clay('box', MAGENTA), bevel=0.1, parent=e)
    rbox((1.8, 1.8, 0.36), (0, 0, 0.42), clay('lid', ORANGE), bevel=0.1, parent=e)
    rib = clay('rib', GREEN, coat=0.6)
    rbox((0.3, 1.84, 1.75), (0, 0, -0.12), rib, bevel=0.04, parent=e)
    rbox((1.84, 0.3, 1.75), (0, 0, -0.12), rib, bevel=0.04, parent=e)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.1, location=(sx * 0.3, 0, 0.82),
                                         rotation=(math.radians(90), math.radians(sx * 35), 0))
        t = bpy.context.object
        bpy.ops.object.shade_smooth()
        t.data.materials.append(rib)
        t.parent = e
    sphere(0.14, (0, 0, 0.7), rib, parent=e)
    sway(e, 'gift', amp=22)


def year():
    reset_res = (620, 360)
    F.B.reset(reset_res, samples=20)
    F.studio_clay()
    F.camera((0, -5.2, 0.3), (0, 0, 0), lens=55)
    e = root()
    bpy.ops.object.text_add()
    t = bpy.context.object
    t.data.body = '2027'
    t.data.font = bpy.data.fonts.load(os.environ['REEL_WORKDIR'] + '/fonts/Poppins-Black.ttf')
    t.data.size = 1.9
    t.data.align_x = 'CENTER'
    t.data.align_y = 'CENTER'
    t.data.extrude = 0.18
    t.data.bevel_depth = 0.05
    t.data.bevel_resolution = 5
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(clay('yr', MAGENTA, coat=0.7))
    t.parent = e
    sway(e, 'year', amp=16, tilt=5)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
