"""3D props for the IC London "Three CV mistakes" reel: a red marker, a magnifier and a paperclip.

Usage: python3 blender_cv.py <asset> [...]
Reuses the navy/red gloss look from pipeline_ic/blender_ic.py.
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_cv'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ic'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ff'))
import bpy
import blender_ic as I
from blender_ic import setup_ic, gloss, NAVY, NAVY_L, RED, WHITE, GOLD
from blender_ff import root, rbox, sphere, cyl, sway, lin

I.F.B.OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_cv')) + '/assets'   # blender_ic points at workspace_ic


def marker():
    setup_ic(cam=(0, -6.6, 0.6))
    e = root()
    body = cyl(0.32, 2.2, (0, 0, 0), gloss('body', RED), parent=e, bevel=0.08)
    cyl(0.34, 0.7, (0, 0, 1.25), gloss('cap', NAVY), parent=e, bevel=0.1)
    cyl(0.08, 0.5, (0.36, 0, 1.25), gloss('clip', NAVY_L), parent=e, bevel=0.03)
    cyl(0.34, 0.08, (0, 0, 0.6), gloss('band', WHITE), parent=e, bevel=0.02)
    bpy.ops.mesh.primitive_cone_add(radius1=0.26, radius2=0.08, depth=0.45, location=(0, 0, -1.32),
                                    rotation=(math.pi, 0, 0), vertices=48)
    c = bpy.context.object
    bpy.ops.object.shade_smooth()
    c.data.materials.append(gloss('nib', lin('#E21A33'), rough=0.5))
    c.parent = e
    sway(e, 'marker', amp=16, tilt=6, base=(0, 35, 0))


def magnifier():
    setup_ic()
    e = root()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.13, location=(0, 0, 0.35),
                                     rotation=(math.radians(90), 0, 0), major_segments=96)
    t = bpy.context.object
    bpy.ops.object.shade_smooth()
    t.data.materials.append(gloss('rim', NAVY))
    t.parent = e
    g = I.mat('glass', (0.72, 0.84, 1.0, 1), rough=0.04, coat=1.0, emission=(0.6, 0.75, 1.0, 1), estr=0.35)
    cyl(0.8, 0.06, (0, 0, 0.35), g, rot=(math.radians(90), 0, 0), parent=e, bevel=0.02)
    cyl(0.15, 1.2, (0.95, 0, -0.7), gloss('handle', RED), rot=(0, math.radians(-40), 0), parent=e, bevel=0.06)
    sway(e, 'magnifier', amp=22)


def paperclip():
    setup_ic(cam=(0, -6.6, 0.4))
    e = root()
    pts = []
    for (cx, r, a0, a1) in [(0.0, 0.42, 0, 180), (0.0, 0.3, 180, 360), (0.0, 0.2, 0, 180)]:
        pass
    import bmesh
    cu = bpy.data.curves.new('clip', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.06
    cu.bevel_resolution = 6
    sp = cu.splines.new('POLY')
    path = [(0.3, -1.0), (0.3, 0.9)]
    for k in range(13):
        a = math.pi * k / 12
        path.append((0.3 * math.cos(a) * 1.0 + 0.0, 0.9 + 0.3 * math.sin(a)))
    path += [(-0.3, -1.25)]
    for k in range(13):
        a = math.pi + math.pi * k / 12
        path.append((0.2 * math.cos(a) * -1.0 - 0.1 + 0.0, -1.25 + 0.2 * math.sin(a)))
    path += [(0.1, 0.55)]
    sp.points.add(len(path) - 1)
    for p, (x, z) in zip(sp.points, path):
        p.co = (x, 0, z, 1)
    o = bpy.data.objects.new('clip', cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(I.mat('steel', (0.75, 0.78, 0.85, 1), rough=0.15, metal=1.0))
    o.parent = e
    sway(e, 'paperclip', amp=20, tilt=6, base=(0, 20, 0))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
