"""New 3D for "Leave the Light On" v2 (Blender Cycles), in the key visual's palette.

Usage: python3 blender_lo2.py <scene> [...]
Scenes:
  switch     macro of a real wall light switch flicking on; warm lamp light floods the plaster wall (opener)
  house      cut-away dollhouse on a plinth: bedroom, nightlight room, kitchen and hallway light up one by one,
             then the whole house glows and gently turns (ready montage + payoff), transparent
  home_text  extruded 3D word "HOME"; the camera flies through the O (transition into the arrival), transparent
  heart      glossy magenta 3D heart turntable for the end card, transparent
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_lo as B
from blender_lo import lin, reset, mat, box, prism, camera, look, FPS


def render_seq(name, n, update, start=0):
    """Like blender_lo.render_seq, plus ONLY=a,b,c renders just those frames (to a preview folder)."""
    if os.environ.get('PROJ'):
        return project_rooms(name, n, update)
    only = os.environ.get('ONLY')
    if not only:
        return B.render_seq(name, n, update, start)
    d = f'{B.OUT}/preview'
    os.makedirs(d, exist_ok=True)
    sc = bpy.context.scene
    for i in [int(x) for x in only.split(',')]:
        update(i, n)
        sc.render.filepath = f'{d}/{name}_{i:03d}.png'
        bpy.ops.render.render(write_still=True)
        print('preview', name, i, flush=True)

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo2'))
B.OUT = S + '/assets3d'
FONT = S + '/fonts/Poppins-ExtraBold.ttf'

CREAM = '#F7F0E5'
MAG = '#C90663'
ORA = '#FF6A0D'
GRN = '#92C31F'


def smooth(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    o.select_set(False)


def sphere(r, loc, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cyl(r, d, loc, m, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def shadow_catcher(size=30, z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    p = bpy.context.object
    p.is_shadow_catcher = True
    return p


def world(col, strength):
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = col
    bg.inputs['Strength'].default_value = strength


def area(loc, rot, size, energy, col):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=tuple(math.radians(a) for a in rot))
    l = bpy.context.object
    l.data.size = size
    l.data.energy = energy
    l.data.color = col
    return l


def ease(k):
    return k * k * (3 - 2 * k)


def project_rooms(name, n, update):
    """Write each room's on-screen centre per frame (pixels) so the compositor can dive into the right room."""
    import json
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    root = bpy.data.objects['root']
    rx, ry = sc.render.resolution_x, sc.render.resolution_y
    out = []
    for i in range(n):
        update(i, n)
        bpy.context.view_layer.update()
        fr = []
        for (x, z, _) in ROOMS:
            w = root.matrix_world @ Vector((x, 0.3, z + 0.45))
            v = world_to_camera_view(sc, sc.camera, w)
            fr.append((v.x * rx, (1 - v.y) * ry))
        out.append(fr)
    json.dump(out, open(f'{B.OUT}/{name}_rooms.json', 'w'))
    print('projected', name, n)


# ------------------------------------------------------------------ 1. light switch macro
def switch():
    reset((720, 1280), samples=20)
    world(lin('#0A0C14'), 0.4)
    wall = mat('plaster', lin('#E9DFD0'), rough=0.92)
    box((12, 0.2, 16), (0, 0.1, 0), wall)
    plate = mat('plate', lin('#F6F3EE'), rough=0.25, coat=0.6)
    box((1.7, 0.16, 1.7), (0, -0.08, 0), plate, bevel=0.12)
    box((1.25, 0.06, 1.25), (0, -0.17, 0), mat('recess', lin('#E4DED6'), rough=0.4), bevel=0.04)
    for sx in (-0.62, 0.62):                     # screws
        s = cyl(0.06, 0.04, (0, -0.17, sx), mat('screw', lin('#BFB6A8'), rough=0.3, metal=0.9), rot=(math.radians(90), 0, 0))
    rocker_m = mat('rocker', lin('#FBF9F6'), rough=0.2, coat=0.8)
    bpy.ops.object.empty_add(location=(0, -0.18, 0))
    pivot = bpy.context.object
    r = box((0.7, 0.2, 1.05), (0, -0.25, 0), rocker_m, bevel=0.08)
    r.parent = pivot
    led = mat('led', lin('#FF9A3C'), rough=0.3, emit=lin('#FF8A2A'), estr=0.0)
    d = box((0.08, 0.03, 0.08), (0, -0.36, -0.38), led, bevel=0.02)
    d.parent = pivot
    # moonlight from a side window (cool), and the warm ceiling lamp that comes on
    area((-5, -6, 4), (60, 0, -40), 4, 120, (0.55, 0.66, 1.0))
    lamp = area((1.5, -4.5, 6), (50, 0, 20), 5, 0, (1.0, 0.72, 0.45))
    fill = area((3, -3, -2), (110, 0, 40), 3, 0, (1.0, 0.55, 0.3))
    cam = camera(lens=60)
    cam.data.dof.aperture_fstop = 2.0
    flip = 14

    def upd(i, n):
        k = i / (n - 1)
        look(cam, (-1.2 + 0.9 * k, -7.5 + 1.8 * ease(k), 0.6 - 0.4 * k), (0, 0, 0))
        f = min(1.0, max(0.0, (i - flip + 2) / 2.0))
        pivot.rotation_euler = (math.radians(lerp(-11, 11, f)), 0, 0)
        on = min(1.0, max(0.0, (i - flip) / 4.0))
        lamp.data.energy = 900 * ease(on)
        fill.data.energy = 220 * ease(on)
        led.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 20 * on
        world(lin('#0A0C14') if on < 0.5 else lin('#2A1A12'), 0.4 + 0.6 * on)
    render_seq('switch', 30, upd)


def lerp(a, b, k):
    return a + (b - a) * k


# ------------------------------------------------------------------ 2. cut-away dollhouse
ROOMS = [(-1.1, 1.0, 'bed'), (1.1, 3.4, 'night'), (1.1, 1.0, 'kitchen'), (-1.1, 3.4, 'hall')]
ON_FRAMES = [8, 32, 56, 80]                         # matches the four ready shots (~1.95 s apart at 24 fps)


def house():
    reset((800, 800), samples=18, transparent=True)
    world(lin('#F3E6D6'), 0.55)
    sc = bpy.context.scene
    shadow_catcher(40, 0.0)
    root = bpy.data.objects.new('root', None)
    sc.collection.objects.link(root)
    objs = []

    def keep(o):
        o.parent = root
        objs.append(o)
        return o
    plinth = mat('plinth', lin(GRN), rough=0.6)
    keep(box((5.6, 3.6, 0.4), (0, 0, 0.2), plinth, bevel=0.15))
    wallm = mat('walls', lin(CREAM), rough=0.85)
    inner = mat('inner', lin('#F2D9C4'), rough=0.9)
    floor_m = mat('wood', lin('#C9773E'), rough=0.55)
    roof_m = mat('roof', lin(MAG), rough=0.35, coat=0.6)
    # shell: back wall, side walls, floor, mid floor, centre wall (front cut away)
    keep(box((4.6, 0.2, 4.8), (0, 1.3, 2.8), inner))
    keep(box((0.2, 2.8, 4.8), (-2.3, 0, 2.8), wallm))
    keep(box((0.2, 2.8, 4.8), (2.3, 0, 2.8), wallm))
    keep(box((4.6, 2.8, 0.15), (0, 0, 0.47), floor_m))
    keep(box((4.6, 2.8, 0.18), (0, 0, 2.4), wallm))
    keep(box((4.6, 2.8, 0.15), (0, 0, 2.55), floor_m))
    keep(box((0.12, 2.8, 4.8), (0, 0, 2.8), wallm))
    keep(box((4.8, 3.0, 0.18), (0, 0, 5.25), wallm))
    r = prism(5.2, 3.4, 2.0, (0, 0, 5.3), roof_m)
    keep(r)
    keep(box((0.5, 0.5, 1.2), (1.4, 0.4, 6.4), mat('chim', lin(ORA), rough=0.6)))
    # windows on the back wall of every room (night sky outside)
    sky = mat('sky', lin('#1B2340'), rough=0.1, emit=lin('#24305A'), estr=0.6)
    for (x, z, _) in ROOMS:
        keep(box((0.8, 0.05, 0.8), (x + 0.3, 1.19, z + 0.95), sky, bevel=0.02))
        keep(box((0.95, 0.08, 0.1), (x + 0.3, 1.16, z + 0.5), wallm))
    pink = mat('pink', lin('#E0457E'), rough=0.6)
    white = mat('linen', lin('#FFFFFF'), rough=0.8)
    # bedroom: bed, fresh sheets, pillow
    x, z, _ = ROOMS[0]
    keep(box((1.5, 1.1, 0.35), (x, 0.3, z - 0.3), mat('bedframe', lin('#8A5530'), rough=0.6), bevel=0.05))
    keep(box((1.45, 1.05, 0.2), (x, 0.3, z - 0.05), white, bevel=0.08))
    keep(box((0.9, 1.08, 0.08), (x + 0.25, 0.3, z + 0.08), pink, bevel=0.04))
    keep(box((0.4, 0.7, 0.16), (x - 0.5, 0.3, z + 0.12), white, bevel=0.07))
    # nightlight room: small bed, teddy, glowing moon nightlight
    x, z, _ = ROOMS[1]
    keep(box((1.1, 0.9, 0.3), (x - 0.3, 0.4, z - 0.3), mat('bed2', lin(ORA), rough=0.5), bevel=0.05))
    keep(box((1.05, 0.85, 0.16), (x - 0.3, 0.4, z - 0.08), white, bevel=0.06))
    ted = mat('teddy', lin('#B07A4A'), rough=1.0)
    keep(sphere(0.2, (x + 0.6, 0.2, z - 0.25), ted, (1, 0.9, 1.1)))
    keep(sphere(0.14, (x + 0.6, 0.2, z + 0.05), ted))
    keep(sphere(0.05, (x + 0.5, 0.2, z + 0.17), ted))
    keep(sphere(0.05, (x + 0.7, 0.2, z + 0.17), ted))
    nl_m = mat('nightlight', lin('#FFE3A0'), rough=0.3, emit=lin('#FFC560'), estr=0.0)
    keep(sphere(0.14, (x + 0.8, 0.9, z - 0.35), nl_m))
    # kitchen: counter, toaster, mug, plate
    x, z, _ = ROOMS[2]
    keep(box((1.8, 0.7, 0.9), (x, 0.85, z - 0.0), mat('counter', lin('#F2EEE8'), rough=0.4), bevel=0.04))
    keep(box((1.85, 0.75, 0.08), (x, 0.85, z + 0.48), mat('top', lin('#3A3532'), rough=0.3)))
    keep(box((0.4, 0.25, 0.28), (x - 0.4, 0.8, z + 0.66), mat('toaster', lin('#D9D9DE'), rough=0.15, metal=0.9), bevel=0.05))
    keep(cyl(0.09, 0.18, (x + 0.3, 0.75, z + 0.61), mat('mug', lin(MAG), rough=0.3, coat=0.8)))
    keep(cyl(0.2, 0.03, (x + 0.65, 0.75, z + 0.53), white))
    # hallway: front door, coat hook, small wellies
    x, z, _ = ROOMS[3]
    keep(box((0.7, 0.08, 1.6), (x - 0.4, 1.17, z + 0.3), mat('fdoor', lin(GRN), rough=0.4, coat=0.5), bevel=0.03))
    keep(sphere(0.04, (x - 0.15, 1.1, z + 0.3), mat('knob', lin('#D4AF37'), rough=0.2, metal=1.0)))
    keep(box((1.0, 0.4, 0.06), (x + 0.2, 0.3, z - 0.47), mat('doormat', lin('#A0703F'), rough=1.0)))
    for sx in (0.05, 0.35):
        keep(cyl(0.08, 0.3, (x + sx, 0.4, z - 0.29), mat('welly%d' % int(sx * 100), lin('#E0235F'), rough=0.2, coat=1.0)))
    # room lights (warm), each switched on at its frame
    lights = []
    for (x, z, name) in ROOMS:
        bpy.ops.object.light_add(type='POINT', location=(x, 0.0, z + 0.9))
        l = bpy.context.object
        l.data.color = (1.0, 0.7, 0.42)
        l.data.energy = 0
        l.data.shadow_soft_size = 0.3
        l.parent = root
        lights.append(l)
    # key + rim for the clay look
    area((-6, -8, 9), (55, 0, -35), 8, 1400, (1.0, 0.93, 0.85))
    area((7, 4, 5), (70, 0, 120), 5, 500, (1.0, 0.7, 0.8))
    cam = camera(lens=42)
    cam.data.dof.use_dof = False

    def upd(i, n):
        k = i / (n - 1)
        root.rotation_euler = (0, 0, math.radians(-24 + 30 * ease(k)))
        look(cam, (0.0, -15.5 + 1.5 * ease(k), 6.2 - 0.6 * k), (0, 0, 3.0))
        for j, l in enumerate(lights):
            kk = min(1.0, max(0.0, (i - ON_FRAMES[j]) / 4.0))
            l.data.energy = 170 * kk
        nlk = min(1.0, max(0.0, (i - ON_FRAMES[1]) / 4.0))
        nl_m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 25 * nlk
    render_seq('house', 132, upd)


# ------------------------------------------------------------------ 3. 3D word HOME fly-through
def letter(ch, x, m, extrude=0.35):
    bpy.ops.object.text_add(location=(x, 0, 0), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.data.body = ch
    t.data.font = bpy.data.fonts.load(FONT, check_existing=True)
    t.data.size = 3.0
    t.data.extrude = extrude
    t.data.bevel_depth = 0.06
    t.data.bevel_resolution = 4
    t.data.align_x = 'CENTER'
    t.data.align_y = 'CENTER'
    t.data.materials.append(m)
    return t


def home_text():
    reset((720, 1280), samples=16, transparent=True)
    world(lin('#2A1A20'), 0.6)
    cols = [MAG, ORA, MAG, ORA]
    lets = []
    x = 0.0
    for j, ch in enumerate('HOME'):
        t = letter(ch, 0.0, mat('l%d' % j, lin(cols[j]), rough=0.3, coat=0.8))
        bpy.context.view_layer.update()
        w = t.dimensions.x
        t.location.x = x + w / 2
        x += w + 0.12
        lets.append(t)
    for t in lets:
        t.location.x -= x / 2
    bpy.context.view_layer.update()
    o = lets[1]
    # centre of the O's counter (hole) in world space
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    oc = Vector((sum(v.x for v in bb) / 8, 0.0, sum(v.z for v in bb) / 8))
    area((-4, -8, 6), (60, 0, -25), 8, 900, (1.0, 0.9, 0.8))
    area((5, -4, -3), (110, 0, 50), 5, 400, (1.0, 0.45, 0.6))
    bpy.ops.object.light_add(type='POINT', location=(oc.x, 2.0, oc.z))          # warm glow through the O
    g = bpy.context.object
    g.data.energy = 600
    g.data.color = (1.0, 0.65, 0.35)
    cam = camera(lens=35)
    cam.data.dof.use_dof = False

    def upd(i, n):
        k = i / (n - 1)
        e = k ** 2.4
        y = lerp(-12.5, 1.0, e)
        x = lerp(oc.x - 0.6, oc.x, min(1, e * 1.4))
        look(cam, (x, y, oc.z + 0.3 * (1 - e)), (oc.x, 5.0, oc.z))
        cam.rotation_euler.y = math.radians(8 * (1 - ease(k)))
    render_seq('home_text', 24, upd)


# ------------------------------------------------------------------ 4. glossy 3D heart
def heart():
    reset((640, 640), samples=20, transparent=True)
    world(lin('#F3E6D6'), 0.7)
    bm = bmesh.new()
    vs = []
    for i in range(96):
        a = i / 96 * 2 * math.pi
        x = 16 * math.sin(a) ** 3 / 17
        z = (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 17
        vs.append(bm.verts.new((x, 0, z)))
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += 0.75
    me = bpy.data.meshes.new('heart')
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('heart', me)
    bpy.context.scene.collection.objects.link(o)
    o.location = (0, -0.375, 0)
    bv = o.modifiers.new('bv', 'BEVEL')
    bv.width = 0.34
    bv.segments = 8
    bv.limit_method = 'NONE'
    o.modifiers.new('sub', 'SUBSURF').levels = 2
    o.data.materials.append(mat('heart', lin('#A8004F'), rough=0.12, coat=1.0))
    smooth(o)
    bpy.ops.object.empty_add(location=(0, 0, 0))
    piv = bpy.context.object
    o.parent = piv
    area((-3, -5, 4), (55, 0, -30), 4, 500, (1.0, 0.92, 0.85))
    area((3, 3, 1), (80, 0, 135), 3, 300, (1.0, 0.55, 0.3))
    area((0, -3, -3), (130, 0, 0), 3, 120, (1.0, 0.75, 0.85))
    cam = camera(lens=55)
    cam.data.dof.use_dof = False
    look(cam, (0, -6.8, 0.2), (0, 0, 0.05))

    def upd(i, n):
        k = i / n
        piv.rotation_euler = (math.radians(6 * math.sin(k * 2 * math.pi)), 0, math.radians(32 * math.sin(k * 2 * math.pi)))
        piv.location.z = 0.06 * math.sin(k * 4 * math.pi)
    render_seq('heart', 48, upd)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
