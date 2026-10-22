"""3D clay-gloss icons for the IC London "No law degree?" reel, in the brand navy / red (from the logo) + white + gold.

Usage: python3 blender_ic.py <asset> [...]
Assets: cap exam gavel briefcase shield scales pin
Reuses the clay toolkit from pipeline_ff/blender_ff.py; each icon sways on a 36-frame loop.
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_ic'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ff'))
import bpy
import blender_ff as F
from blender_ff import setup, root, rbox, sphere, cyl, sway, lin, mat

NAVY = lin('#00247D')
NAVY_L = lin('#2A4FB8')
RED = lin('#CF142B')
WHITE = lin('#F4F6FB')
GOLD = lin('#D9A83E')
PAPER = lin('#FFFFFF')


def gloss(name, col, rough=0.28, coat=0.8):
    return mat(name, col, rough=rough, coat=coat, sss=0.04)


def studio_navy():
    """Cool key + red rim so the navy reads as glossy, not black."""
    F.B.area((-3.0, -4.0, 4.2), (math.radians(48), 0, math.radians(-36)), (4.5, 4.5), 1100, (0.95, 0.97, 1.0))
    F.B.area((3.8, 2.6, 2.0), (math.radians(70), 0, math.radians(125)), (2.5, 5), 1200, (1.0, 0.35, 0.4))
    F.B.area((3.6, -3.4, -1.2), (math.radians(110), 0, math.radians(45)), (4, 4), 320, (0.8, 0.85, 1.0))
    F.B.panel((-2.6, -2.6, 3.4), (math.radians(50), 0, math.radians(-40)), (2.6, 0.4), (1, 1, 1), 12)


def setup_ic(cam=(0, -6.6, 1.1), lens=66, res=360):
    F.B.reset((res, res), samples=20)
    studio_navy()
    F.B.camera(cam, (0, 0, 0), lens=lens)


def cap():
    setup_ic(cam=(0, -6.4, 2.4))
    e = root()
    m = gloss('cap', NAVY)
    rbox((1.9, 1.9, 0.14), (0, 0, 0.35), m, bevel=0.05, parent=e, rot=(0, 0, math.radians(45)))
    cyl(0.68, 0.6, (0, 0, -0.05), m, parent=e)
    r = gloss('tas', RED)
    sphere(0.12, (0, 0, 0.47), r, parent=e)
    cyl(0.04, 0.9, (0.66, -0.66, 0.05), r, parent=e, bevel=0)
    sphere(0.13, (0.66, -0.66, -0.42), r, parent=e, scale=(1, 1, 1.5))
    sway(e, 'cap', amp=24)


def exam():
    setup_ic()
    e = root()
    rbox((1.6, 0.12, 2.1), (0, 0, 0), gloss('paper', PAPER, rough=0.5, coat=0.2), bevel=0.06, parent=e)
    rbox((1.6, 0.16, 0.36), (0, -0.01, 0.9), gloss('hdr', NAVY), bevel=0.06, parent=e)
    ln = gloss('ln', lin('#C9D2EA'), rough=0.5, coat=0.1)
    tick = gloss('tick', RED)
    for j in range(4):
        z = 0.45 - j * 0.38
        cyl(0.1, 0.08, (-0.52, -0.08, z), tick if j < 3 else ln, rot=(math.radians(90), 0, 0), parent=e, bevel=0.02)
        rbox((0.9, 0.06, 0.1), (0.15, -0.08, z), ln, bevel=0.03, parent=e)
    # pencil
    p = gloss('pen', lin('#FFC845'))
    cyl(0.09, 1.6, (0.55, -0.3, -0.25), p, rot=(0, math.radians(-35), 0), parent=e, bevel=0.02, verts=6)
    bpy.ops.mesh.primitive_cone_add(radius1=0.09, depth=0.25, location=(0.08, -0.3, -0.92), rotation=(0, math.radians(145), 0))
    c = bpy.context.object
    c.data.materials.append(gloss('tip', lin('#E9C9A0')))
    c.parent = e
    sway(e, 'exam', amp=22)


def gavel():
    setup_ic(cam=(0.6, -6.4, 1.6))
    e = root()
    wood = gloss('wood', lin('#7A3E1E'), rough=0.35, coat=0.9)
    head = cyl(0.36, 1.25, (0, 0, 0.35), wood, rot=(0, math.radians(90), math.radians(-25)), parent=e, bevel=0.06)
    for sx in (-1, 1):
        cyl(0.4, 0.14, (sx * 0.58 * math.cos(math.radians(25)), sx * 0.58 * math.sin(math.radians(25)) * -1, 0.35),
            gloss('band%d' % sx, GOLD, rough=0.2), rot=(0, math.radians(90), math.radians(-25)), parent=e, bevel=0.03)
    cyl(0.1, 1.25, (0, 0, -0.3), wood, parent=e, bevel=0.03)          # handle straight down into the block
    cyl(0.75, 0.22, (0, 0, -0.95), gloss('block', NAVY), parent=e, bevel=0.06)
    sway(e, 'gavel', amp=20)


def briefcase():
    setup_ic()
    e = root()
    rbox((2.1, 0.8, 1.45), (0, 0, -0.2), gloss('case', NAVY), bevel=0.14, parent=e)
    rbox((2.14, 0.84, 0.12), (0, 0, 0.18), gloss('band', RED), bevel=0.04, parent=e)
    rbox((0.3, 0.1, 0.22), (0, -0.44, 0.18), gloss('clasp', GOLD, rough=0.2), bevel=0.04, parent=e)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.36, minor_radius=0.08, location=(0, 0, 0.6), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    bpy.ops.object.shade_smooth()
    t.data.materials.append(gloss('handle', NAVY_L))
    t.parent = e
    sway(e, 'briefcase', amp=24)


def shield():
    setup_ic()
    e = root()
    pts = []
    for i in range(64):
        u = i / 63
        x = -1 + 2 * u
        pts.append((x, 1.0 - 0.12 * (1 - x * x)))
    for i in range(1, 64):
        u = i / 63
        x = 1 - 2 * u
        pts.append((x * (1 - 0.0), -0.3 - 0.95 * (1 - abs(x)) ** 0.9 if abs(x) < 1 else -0.3))
    pts = [(x * 0.95, y) for x, y in pts]
    o = F.curve_obj('sh', [pts[:64] + [(0.95, -0.2), (0.0, -1.3), (-0.95, -0.2)]], extrude=0.18, bevel=0.08, res=6)
    o = F.to_mesh(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(gloss('sh', NAVY))
    o.parent = e
    chk = F.curve_obj('chk', [[(-0.42, 0.02), (-0.14, -0.28), (0.44, 0.32), (0.32, 0.44), (-0.14, -0.02), (-0.30, 0.16)]],
                      extrude=0.08, bevel=0.05, res=4)
    chk = F.to_mesh(chk)
    chk.rotation_euler = (math.radians(90), 0, 0)
    chk.location = (0, -0.3, 0.05)
    chk.data.materials.append(gloss('chk', WHITE, rough=0.3))
    chk.parent = e
    rbox((2.0, 0.1, 0.16), (0, -0.22, 0.62), gloss('stripe', RED), bevel=0.04, parent=e)
    sway(e, 'shield', amp=24)


def scales():
    setup_ic(cam=(0, -6.6, 1.0))
    e = root()
    g = gloss('gold', GOLD, rough=0.2, coat=1.0)
    cyl(0.07, 1.9, (0, 0, -0.05), g, parent=e, bevel=0)
    cyl(0.55, 0.14, (0, 0, -1.0), gloss('base', NAVY), parent=e, bevel=0.05)
    cyl(0.05, 2.2, (0, 0, 0.85), g, rot=(0, math.radians(90), 0), parent=e, bevel=0)
    sphere(0.13, (0, 0, 0.95), gloss('top', RED), parent=e)
    for sx in (-1, 1):
        for dx in (-0.22, 0.22):
            cyl(0.015, 0.75, (sx * 1.0 + dx * 0.5, 0, 0.5), g, rot=(0, math.radians(dx * 60), 0), parent=e, bevel=0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(sx * 1.0, 0, 0.12), segments=48, ring_count=24)
        b = bpy.context.object
        b.scale = (1, 1, 0.38)
        bpy.ops.object.shade_smooth()
        b.data.materials.append(g)
        b.parent = e
    sway(e, 'scales', amp=20)


def pin():
    setup_ic()
    e = root()
    m = gloss('pin', RED)
    sphere(0.82, (0, 0, 0.45), m, parent=e)
    bpy.ops.mesh.primitive_cone_add(radius1=0.72, depth=1.25, location=(0, 0, -0.5), rotation=(math.pi, 0, 0), vertices=64)
    c = bpy.context.object
    bpy.ops.object.shade_smooth()
    c.data.materials.append(m)
    c.parent = e
    sphere(0.32, (0, -0.62, 0.48), gloss('hole', WHITE), parent=e, scale=(1, 0.5, 1))
    cyl(0.55, 0.08, (0, 0, -1.15), gloss('base', NAVY_L), parent=e)
    sway(e, 'pin', amp=30)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
