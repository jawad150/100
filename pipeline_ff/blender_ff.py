"""3D clay icons for "The Fostering Flow", as transparent PNG sequences (Blender Cycles).

Usage: python3 blender_ff.py <asset> [...]
Assets: chat house calendar pin doc cap person badge cursor phone
Each icon sways gently (36 frames, loops) so it can idle on screen after it pops in.
"""
import bpy, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
os.environ.setdefault('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_ff')))
import blender_of as B
from blender_of import lin, reset, mat, camera, render_seq, curve_obj, to_mesh, PLUM, MAGENTA, ORANGE, GREEN, IVORY, PEACH

S = os.environ['REEL_WORKDIR']
B.OUT = S + '/assets'
FONT = S + '/fonts/Poppins-Black.ttf'
LILAC = lin('#E7C6E0')
WARM = lin('#FFB45E')
NF = 36


def clay(name, col, rough=0.42, coat=0.35):
    return mat(name, col, rough=rough, coat=coat, sss=0.12)


def studio_clay():
    """Soft clay light: big warm key, magenta rim, peach fill, a glossy strip."""
    B.area((-3.0, -4.0, 4.2), (math.radians(48), 0, math.radians(-36)), (4.5, 4.5), 900, (1.0, 0.92, 0.84))
    B.area((3.8, 2.6, 2.0), (math.radians(70), 0, math.radians(125)), (2.5, 5), 1300, (1.0, 0.4, 0.7))
    B.area((3.6, -3.4, -1.2), (math.radians(110), 0, math.radians(45)), (4, 4), 260, (1.0, 0.82, 0.7))
    B.panel((-2.6, -2.6, 3.4), (math.radians(50), 0, math.radians(-40)), (2.6, 0.4), (1, 0.97, 0.92), 10)


def rbox(size, loc, m, bevel=0.2, seg=8, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new('bv', 'BEVEL')
    bv.width = bevel
    bv.segments = seg
    bv.limit_method = 'NONE'
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def sphere(r, loc, m, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cyl(r, depth, loc, m, rot=(0, 0, 0), parent=None, verts=64, bevel=0.06):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL')
        bv.width = bevel
        bv.segments = 6
        bv.limit_method = 'ANGLE'
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def root():
    bpy.ops.object.empty_add(location=(0, 0, 0))
    e = bpy.context.object
    e.rotation_mode = 'XYZ'
    return e


def setup(res=360, samples=20, cam=(0, -6.6, 1.1), lens=66):
    reset((res, res), samples=samples)
    studio_clay()
    camera(cam, (0, 0, 0), lens=lens)


def sway(e, name, amp=26, tilt=6, base=(0, 0, 0)):
    def upd(i, n):
        ph = i / n * 2 * math.pi
        e.rotation_euler = (math.radians(base[0] + tilt * math.cos(ph)), math.radians(base[1]),
                            math.radians(base[2] + amp * math.sin(ph)))
    render_seq(name, NF, upd)


# ---------------------------------------------------------------- icons

def chat():
    setup()
    e = root()
    rbox((2.3, 0.6, 1.5), (0, 0, 0.15), clay('b', MAGENTA), bevel=0.28, parent=e)
    # tail
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, depth=0.62, location=(-0.62, 0, -0.72), rotation=(0, math.radians(200), 0))
    t = bpy.context.object
    bpy.ops.object.shade_smooth()
    t.data.materials.append(clay('t', MAGENTA))
    t.parent = e
    w = clay('w', IVORY, rough=0.3)
    for x in (-0.55, 0, 0.55):
        sphere(0.17, (x, -0.32, 0.15), w, parent=e, scale=(1, 0.6, 1))
    sway(e, 'chat')


def house():
    setup(cam=(2.0, -6.3, 1.7))
    e = root()
    body = rbox((1.6, 1.4, 1.2), (0, 0, -0.45), clay('body', PEACH), bevel=0.14, parent=e)
    import bmesh
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in [(-1.05, -0.9, 0.12), (1.05, -0.9, 0.12), (0, -0.9, 1.05),
                                    (-1.05, 0.9, 0.12), (1.05, 0.9, 0.12), (0, 0.9, 1.05)]]
    for f in [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]:
        bm.faces.new([v[i] for i in f])
    me = bpy.data.meshes.new('roof')
    bm.to_mesh(me)
    bm.free()
    roof = bpy.data.objects.new('roof', me)
    bpy.context.scene.collection.objects.link(roof)
    bv = roof.modifiers.new('bv', 'BEVEL')
    bv.width = 0.12
    bv.segments = 8
    roof.data.materials.append(clay('roof', PLUM))
    roof.parent = e
    rbox((0.24, 0.24, 0.5), (0.55, 0.3, 0.85), clay('ch', MAGENTA), bevel=0.06, parent=e)
    rbox((0.42, 0.12, 0.68), (-0.3, -0.7, -0.72), clay('door', ORANGE), bevel=0.08, parent=e)
    rbox((0.36, 0.1, 0.36), (0.38, -0.7, -0.35), mat('win', lin('#FFD39A'), rough=0.3, emission=WARM, estr=2.5),
         bevel=0.05, parent=e)
    sphere(0.05, (-0.18, -0.78, -0.72), clay('k', IVORY), parent=e)
    sway(e, 'house', amp=22)


def calendar():
    setup()
    e = root()
    rbox((2.0, 0.34, 2.0), (0, 0, -0.1), clay('page', IVORY, rough=0.5), bevel=0.2, parent=e)
    rbox((2.0, 0.4, 0.56), (0, -0.01, 0.68), clay('top', MAGENTA), bevel=0.2, parent=e)
    ring = clay('ring', PLUM, rough=0.25, coat=0.8)
    for x in (-0.5, 0.5):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.055, location=(x, -0.05, 1.0),
                                         rotation=(0, math.radians(90), 0))
        r = bpy.context.object
        bpy.ops.object.shade_smooth()
        r.data.materials.append(ring)
        r.parent = e
    dot = clay('dot', LILAC)
    hi = clay('hi', ORANGE)
    for j in range(3):
        for i in range(3):
            m = hi if (i, j) == (1, 1) else dot
            rbox((0.36, 0.14, 0.3), (-0.5 + i * 0.5, -0.2, 0.15 - j * 0.42), m, bevel=0.06, parent=e)
    sway(e, 'calendar')


def pin():
    setup()
    e = root()
    m = clay('pin', MAGENTA)
    sphere(0.82, (0, 0, 0.45), m, parent=e)
    bpy.ops.mesh.primitive_cone_add(radius1=0.72, depth=1.25, location=(0, 0, -0.5), rotation=(math.pi, 0, 0), vertices=64)
    c = bpy.context.object
    bpy.ops.object.shade_smooth()
    c.data.materials.append(m)
    c.parent = e
    sphere(0.32, (0, -0.62, 0.48), clay('hole', IVORY), parent=e, scale=(1, 0.5, 1))
    # base disc shadow-catcher look
    cyl(0.55, 0.08, (0, 0, -1.15), clay('base', LILAC), parent=e)
    sway(e, 'pin', amp=30)


def doc():
    setup()
    e = root()
    rbox((1.7, 0.22, 2.2), (0, 0.1, 0), clay('board', PLUM), bevel=0.16, parent=e)
    rbox((1.45, 0.1, 1.9), (0, -0.04, -0.06), clay('paper', IVORY, rough=0.55), bevel=0.06, parent=e)
    rbox((0.7, 0.26, 0.3), (0, -0.02, 1.0), clay('clip', ORANGE), bevel=0.1, parent=e)
    ln = clay('ln', LILAC)
    for j, w in enumerate((1.0, 0.8, 0.95, 0.6)):
        rbox((w, 0.08, 0.13), (-0.1 - (1.0 - w) / 2 + 0.05, -0.12, 0.5 - j * 0.36), ln, bevel=0.04, parent=e)
    g = clay('g', GREEN)
    sphere(0.3, (0.5, -0.2, -0.75), g, parent=e, scale=(1, 0.5, 1))
    sway(e, 'doc')


def cap():
    setup(cam=(0, -6.4, 2.4))
    e = root()
    m = clay('cap', PLUM)
    rbox((1.9, 1.9, 0.14), (0, 0, 0.35), m, bevel=0.05, parent=e, rot=(0, 0, math.radians(45)))
    cyl(0.68, 0.6, (0, 0, -0.05), m, parent=e)
    o = clay('tas', ORANGE)
    sphere(0.12, (0, 0, 0.47), o, parent=e)
    cyl(0.04, 0.9, (0.66, -0.66, 0.05), o, parent=e, bevel=0)
    sphere(0.13, (0.66, -0.66, -0.42), o, parent=e, scale=(1, 1, 1.5))
    sway(e, 'cap', amp=24, base=(0, 0, 0))


def person():
    setup()
    e = root()
    sphere(0.56, (0, 0, 0.55), clay('head', PEACH), parent=e)
    sphere(0.6, (0, 0.1, 0.72), clay('hair', PLUM), parent=e, scale=(1.02, 1.0, 0.82))
    sphere(0.95, (0, 0, -0.72), clay('body', GREEN), parent=e, scale=(1.08, 0.72, 0.6))
    sway(e, 'person', amp=24)


def badge():
    setup()
    e = root()
    # scalloped rosette: star-ish outline
    pts = []
    for i in range(96):
        a = i / 96 * 2 * math.pi
        r = 1.0 + 0.07 * math.cos(16 * a)
        pts.append((r * math.cos(a), r * math.sin(a)))
    o = curve_obj('ros', [pts], extrude=0.12, bevel=0.07, res=6)
    o = to_mesh(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(clay('ros', GREEN))
    o.parent = e
    cyl(0.72, 0.34, (0, -0.06, 0), clay('in', lin('#7CC223')), rot=(math.radians(90), 0, 0), parent=e)
    chk = curve_obj('chk', [[(-0.42, 0.02), (-0.14, -0.28), (0.44, 0.32), (0.32, 0.44), (-0.14, -0.02), (-0.30, 0.16)]],
                    extrude=0.08, bevel=0.05, res=4)
    chk = to_mesh(chk)
    chk.rotation_euler = (math.radians(90), 0, 0)
    chk.location = (0, -0.26, 0)
    chk.data.materials.append(clay('chk', IVORY, rough=0.3))
    chk.parent = e
    rib = clay('rib', MAGENTA)
    for sx in (-1, 1):
        rbox((0.34, 0.08, 0.9), (sx * 0.38, 0.12, -1.0), rib, bevel=0.06, parent=e, rot=(0, math.radians(sx * 18), 0))
    sway(e, 'badge', amp=26)


def cursor():
    setup(res=300, cam=(0, -6.6, 0.4))
    e = root()
    out = [(0, 0), (0, -1.55), (0.36, -1.2), (0.62, -1.78), (0.86, -1.67), (0.6, -1.1), (1.08, -1.1)]
    o = curve_obj('cur', [out], extrude=0.1, bevel=0.06, res=5)
    o = to_mesh(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.location = (-0.5, 0, 0.85)
    o.data.materials.append(mat('cur', IVORY, rough=0.2, coat=1.0))
    o.parent = e
    sway(e, 'cursor', amp=14, tilt=4)


def phone():
    setup()
    e = root()
    rbox((1.15, 0.24, 2.1), (0, 0, 0), clay('ph', PLUM), bevel=0.2, parent=e)
    rbox((0.95, 0.1, 1.75), (0, -0.1, 0.02), mat('scr', lin('#FFD4BA'), rough=0.2, emission=lin('#FF9A6A'), estr=0.6),
         bevel=0.08, parent=e)
    sphere(0.12, (0, -0.2, 0.25), clay('h', MAGENTA), parent=e)
    sway(e, 'phone')


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
