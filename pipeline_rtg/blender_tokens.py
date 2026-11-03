"""Glossy 3D pop-up tokens for "Room to Grow" (transparent PNGs, brand palette).

Usage: python3 blender_tokens.py <token> [...]
Tokens: seedling, globe, lantern, rings, fingerprint, puzzle, frame, doortag, bedmini, lampmini
"""
import bpy, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_cf as C
from blender_cf import setup, gloss, sphere, PURPLE, ORANGE, PLUM, IVORY, LAV, PEACH, LEAF
from blender_lo import lin, mat

C.OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_rtg', 'tokens'))
shot = C.shot


def cyl(r, d, loc, m, rot=(0, 0, 0), v=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def rbox(size, loc, m, bevel=0.1, rot=(0, 0, 0), seg=5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def curve_obj(pts, m, depth=0.06, cyclic=False, name='c'):
    cd = bpy.data.curves.new(name, 'CURVE'); cd.dimensions = '3D'
    s = cd.splines.new('POLY'); s.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        s.points[i].co = (*p, 1)
    s.use_cyclic_u = cyclic
    cd.bevel_depth = depth; cd.bevel_resolution = 6
    o = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    return o


def shape_obj(pts, m, extrude=0.25, bevel=0.06, name='s'):
    """Filled 2D outline in the XZ plane (facing -Y), extruded."""
    cd = bpy.data.curves.new(name, 'CURVE'); cd.dimensions = '2D'; cd.fill_mode = 'BOTH'
    s = cd.splines.new('POLY'); s.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        s.points[i].co = (p[0], p[1], 0, 1)
    s.use_cyclic_u = True
    cd.extrude = extrude; cd.bevel_depth = bevel; cd.bevel_resolution = 4
    o = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(m)
    return o


def seedling():
    setup()
    pot = gloss('pot', ORANGE, rough=0.3)
    bpy.ops.mesh.primitive_cone_add(radius1=0.62, radius2=0.85, depth=1.05, location=(0, 0, -0.9), vertices=64)
    bpy.context.object.data.materials.append(pot); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.86, minor_radius=0.1, location=(0, 0, -0.38), major_segments=96)
    bpy.context.object.data.materials.append(pot); bpy.ops.object.shade_smooth()
    cyl(0.8, 0.06, (0, 0, -0.42), mat('soil', lin('#5B3A2E'), rough=0.9))
    g = gloss('leaf', LEAF, rough=0.3)
    pts = [(0.0, 0, -0.4), (0.03, 0, 0.0), (-0.04, 0, 0.4), (0.02, 0, 0.8), (0.0, 0, 1.0)]
    curve_obj(pts, g, 0.06, name='stem')
    for side, z, s in ((-1, 0.75, 1.0), (1, 0.95, 0.9)):
        o = sphere(0.42 * s, (side * 0.42 * s, 0, z), g, (1.0, 0.18, 0.5))
        o.rotation_euler = (0, side * math.radians(-25), 0)
    shot('seedling', (0.8, -7.5, 1.4), (0, 0, 0.1))


def globe():
    setup()
    sea = gloss('sea', '#7A3BB0', rough=0.25)
    land = gloss('land', LEAF, rough=0.35)
    sphere(1.0, (0, 0, 0.25), sea)
    import random
    random.seed(5)
    for k in range(26):
        th = random.uniform(-0.9, 0.9); ph = random.uniform(-2.2, 0.6)
        n = (math.cos(th) * math.sin(ph), -math.cos(th) * math.cos(ph), math.sin(th))
        o = sphere(random.uniform(0.18, 0.32), (n[0] * 0.93, n[1] * 0.93, 0.25 + n[2] * 0.93), land, (1, 1, 0.35))
        o.rotation_euler = n[2] * 1.2, 0, ph
        o.rotation_mode = 'XYZ'
        q = (bpy.context.object.matrix_world.to_translation() - bpy.context.object.matrix_world.to_translation())
    # stand
    bpy.ops.mesh.primitive_torus_add(major_radius=1.18, minor_radius=0.05, location=(0, 0, 0.25), rotation=(math.radians(90), math.radians(23), 0), major_segments=96)
    bpy.context.object.data.materials.append(gloss('stand', ORANGE))
    cyl(0.06, 0.6, (0, 0, -1.05), gloss('stand', ORANGE))
    cyl(0.55, 0.14, (0, 0, -1.35), gloss('base', PURPLE))
    shot('globe', (0.4, -7.6, 1.2), (0, 0, -0.1))


def lantern():
    setup()
    frame = gloss('lframe', PLUM, rough=0.3)
    glow = mat('lglow', lin('#FFD9A0'), rough=0.2, emit=lin('#FFB45A'), estr=6.0)
    rbox((1.0, 1.0, 1.4), (0, 0, 0), glow, bevel=0.06)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rbox((0.14, 0.14, 1.55), (sx * 0.52, sy * 0.52, 0), frame, bevel=0.04)
    rbox((1.3, 1.3, 0.16), (0, 0, -0.82), frame, bevel=0.05)
    rbox((1.25, 1.25, 0.14), (0, 0, 0.8), frame, bevel=0.05)
    bpy.ops.mesh.primitive_cone_add(radius1=0.9, radius2=0.12, depth=0.55, location=(0, 0, 1.12), vertices=4, rotation=(0, 0, math.radians(45)))
    bpy.context.object.data.materials.append(gloss('lroof', PURPLE))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.06, location=(0, 0, 1.6), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(gloss('lring', ORANGE))
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0)); bpy.context.object.data.energy = 120
    bpy.context.object.data.color = (1.0, 0.75, 0.45)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.rotation_euler[2] += math.radians(28)
    shot('lantern', (0.8, -8.0, 1.6), (0, 0, 0.3))


def rings():
    setup()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.22, location=(-0.5, 0, 0), rotation=(math.radians(80), 0, math.radians(-15)), major_segments=96, minor_segments=32)
    bpy.context.object.data.materials.append(gloss('r1', PURPLE)); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.22, location=(0.5, 0, 0), rotation=(math.radians(10), math.radians(70), 0), major_segments=96, minor_segments=32)
    bpy.context.object.data.materials.append(gloss('r2', ORANGE)); bpy.ops.object.shade_smooth()
    shot('rings', (0.5, -7.0, 1.0), (0, 0, 0))


def fingerprint():
    setup()
    cyl(1.15, 0.22, (0, 0, 0), gloss('disc', PURPLE, rough=0.25), rot=(math.radians(90), 0, 0))
    ridge = gloss('ridge', '#FFF4EC', rough=0.3, coat=0.3)
    for i in range(6):
        r = 0.16 + i * 0.15
        a0 = math.radians(-60 + i * 9); a1 = math.radians(240 - i * 6)
        pts = []
        for k in range(60):
            a = a0 + (a1 - a0) * k / 59
            pts.append((math.cos(a) * r * 0.82, -0.13, math.sin(a) * r + 0.05))
        curve_obj(pts, ridge, 0.035, name=f'fp{i}')
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE'):
            o.rotation_euler[2] += math.radians(-18)
    shot('fingerprint', (0.6, -7.2, 0.9), (0, 0, 0))


def puzzle_pts(cx, cz, s, tab_r=(1, 0), tab_t=(1, 0)):
    """Square piece with a round tab on the right (+x) and a slot on the left (-x)."""
    pts = []
    h = s / 2
    r = s * 0.17

    def arc(c, start, end, n=20, rr=r):
        for k in range(n + 1):
            a = start + (end - start) * k / n
            pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr))
    pts.append((cx - h, cz - h)); pts.append((cx + h, cz - h)); pts.append((cx + h, cz - r * 0.7))
    arc((cx + h + r * 0.9, cz), math.radians(-140), math.radians(140))
    pts.append((cx + h, cz + r * 0.7)); pts.append((cx + h, cz + h)); pts.append((cx - h, cz + h)); pts.append((cx - h, cz + r * 0.7))
    arc((cx - h + r * 0.9, cz), math.radians(140), math.radians(-140) + 0, n=20)
    pts[-21:] = [(cx - h + r * 0.9 + math.cos(math.radians(180 - a)) * r, cz + math.sin(math.radians(180 - a)) * r)
                 for a in [40 + k * (280 / 20) for k in range(21)]]
    pts.append((cx - h, cz - r * 0.7))
    return pts


def puzzle():
    setup((720, 560))
    a = shape_obj(puzzle_pts(-0.62, 0, 1.25), gloss('pz1', PURPLE), 0.2, 0.06, 'pa')
    b = shape_obj(puzzle_pts(0.62 + 0.03, 0, 1.25), gloss('pz2', ORANGE), 0.2, 0.06, 'pb')
    b.location = (0.06, -0.12, 0.08)
    b.rotation_euler = (math.radians(90), math.radians(6), 0)
    for o in (a, b):
        o.rotation_euler[2] += math.radians(-16)
    shot('puzzle', (0.4, -7.4, 1.6), (0, 0, 0))


def frame():
    setup((600, 680))
    wood = gloss('fw', '#C08A55', rough=0.35, coat=0.6)
    W_, H_, t = 1.7, 2.1, 0.26
    rbox((W_, 0.22, t), (0, 0, H_ / 2 - t / 2), wood, 0.05)
    rbox((W_, 0.22, t), (0, 0, -H_ / 2 + t / 2), wood, 0.05)
    rbox((t, 0.22, H_), (W_ / 2 - t / 2, 0, 0), wood, 0.05)
    rbox((t, 0.22, H_), (-W_ / 2 + t / 2, 0, 0), wood, 0.05)
    rbox((W_ - 0.4, 0.06, H_ - 0.4), (0, 0.03, 0), mat('mt', lin('#FFFFFF'), rough=0.6), 0.01)
    rbox((W_ - 0.8, 0.04, H_ - 0.8), (0, 0.0, 0), mat('in', lin('#F6E9F1'), rough=0.6), 0.01)
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.rotation_euler = (0, math.radians(-6), math.radians(-18))
    shot('frame', (0.3, -7.6, 0.6), (0, 0, 0))


def doortag():
    setup((560, 720))
    card = gloss('tag', '#FFFFFF', rough=0.35, coat=0.4)
    rbox((1.4, 0.12, 2.0), (0, 0, -0.35), card, 0.12)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.12, location=(0, 0, 1.05), rotation=(math.radians(90), 0, 0), major_segments=64)
    bpy.context.object.data.materials.append(card); bpy.ops.object.shade_smooth()
    rbox((1.0, 0.03, 0.08), (0, -0.07, -0.2), gloss('line', '#E9C6DA'), 0.03)
    rbox((0.7, 0.03, 0.08), (0, -0.07, -0.55), gloss('line', '#E9C6DA'), 0.03)
    sphere(0.12, (0, -0.06, 1.48), gloss('pin', ORANGE))
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.rotation_euler[2] += math.radians(-20)
    shot('doortag', (0.4, -7.4, 0.8), (0, 0, 0.1))


ALL = dict(seedling=seedling, globe=globe, lantern=lantern, rings=rings, fingerprint=fingerprint, puzzle=puzzle,
           frame=frame, doortag=doortag)

if __name__ == '__main__':
    for n in (sys.argv[1:] or list(ALL)):
        ALL[n]()
