"""Organic Fostering "Two Toothbrushes": 3D renders for three static-post options.

  shelf   A · photoreal close-up (the PDF's photo): two child-sized brushes, magenta + orange, leaning together in a
              lavender cup on a white bathroom shelf, pale tiles, soft morning light from the top left, shallow DOF.
  shadow  B · same objects, frontal; low morning sun throws their shadows on the tiles as a little house
              (the two leaning brushes = the roof, the cup = the walls).
  clay    C · soft clay miniature: a house-shaped toothbrush holder, the two brushes through its roof, soap bubbles,
              on a lavender studio backdrop.

Usage: python3 blender_tb.py <shelf|shadow|clay> [samples] [pct]
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_tb', 'renders'))
MODE = sys.argv[1] if len(sys.argv) > 1 else 'shelf'
SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 128
PCT = int(sys.argv[3]) if len(sys.argv) > 3 else 100
CLAY = MODE == 'clay'


def lin(h):
    h = h.lstrip('#')

    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True; sc.cycles.max_bounces = 10
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.resolution_percentage = PCT
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#F3EEF2')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35


def mat(name, col, rough=0.4, coat=0.0, metal=0.0, sss=0.0, trans=0.0, ior=1.45, bump=None, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin(col) if isinstance(col, str) else col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Metallic'].default_value = metal
    b.inputs['IOR'].default_value = ior
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.3, 0.2, 0.15)
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    if emit:
        b.inputs['Emission Color'].default_value = lin(emit); b.inputs['Emission Strength'].default_value = estr
    if bump:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bump[0]; n.inputs['Detail'].default_value = 8
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump[1]; bp.inputs['Distance'].default_value = 0.002
        nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def rbox(size, loc, m, bevel=0.02, seg=4, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg; bv.limit_method = 'NONE'
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def empty(loc=(0, 0, 0)):
    bpy.ops.object.empty_add(location=loc)
    return bpy.context.object


def parent(objs, e):
    bpy.context.view_layer.update()
    inv = e.matrix_world.inverted()
    for o in objs:
        o.parent = e
        o.matrix_parent_inverse = inv


# ------------------------------------------------------------------ the toothbrush (child-sized, chunky grip)
def toothbrush(col, bristle_tip, seed=0):
    """Built standing up from z=0 (handle end) to the head at the top; bristles face -y. Returns its root empty."""
    plastic = mat(f'pl{seed}', col, rough=0.18 if not CLAY else 0.45, coat=0.6 if not CLAY else 0.1, sss=0.0 if not CLAY else 0.15)
    grip = mat(f'gr{seed}', '#FFFFFF' if not CLAY else '#FFF4F8', rough=0.5, sss=0.1)
    objs = []
    # handle: a lathed profile (bulb at the bottom, waist, neck)
    bm = bmesh.new()
    prof = [(0.0, 0.0), (0.075, 0.0), (0.095, 0.05), (0.1, 0.18), (0.088, 0.38), (0.07, 0.62), (0.062, 0.8), (0.05, 0.98),
            (0.04, 1.12), (0.038, 1.2)]
    ring = 40
    rings = []
    for r, z in prof:
        rings.append([bm.verts.new((math.cos(a) * r * 1.25, math.sin(a) * r, z)) for a in (i / ring * 2 * math.pi for i in range(ring))])
    for a, b in zip(rings, rings[1:]):
        for i in range(ring):
            bm.faces.new((a[i], a[(i + 1) % ring], b[(i + 1) % ring], b[i]))
    bm.faces.new(rings[0][::-1])
    me = bpy.data.meshes.new('h'); bm.to_mesh(me); bm.free()
    h = bpy.data.objects.new('handle', me); sc.collection.objects.link(h)
    h.data.materials.append(plastic)
    for p in me.polygons:
        p.use_smooth = True
    sub = h.modifiers.new('s', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    objs.append(h)
    # soft grip pad on the front
    objs.append(rbox((0.13, 0.04, 0.32), (0, -0.085, 0.3), grip, 0.018))
    # head
    objs.append(rbox((0.11, 0.07, 0.3), (0, 0.0, 1.33), plastic, 0.03))
    # bristle tufts (child-sized head: 3 x 7)
    white = mat(f'br{seed}', '#F7F7F7' if not CLAY else '#FFFFFF', rough=0.55, sss=0.05)
    tip = mat(f'bt{seed}', bristle_tip, rough=0.5)
    rng = random.Random(seed)
    for ix in range(3):
        for iz in range(7):
            x = (ix - 1) * 0.032
            z = 1.215 + iz * 0.037
            L = 0.11 + 0.012 * math.sin(iz * 0.9) + rng.uniform(-0.004, 0.004)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.0135, depth=L, location=(x, -0.035 - L / 2, z), rotation=(math.radians(90), 0, 0), vertices=10)
            t = bpy.context.object
            t.data.materials.append(tip if (iz in (1, 5) and ix != 1) else white)
            bv = t.modifiers.new('b', 'BEVEL'); bv.width = 0.005; bv.segments = 2
            objs.append(t)
    root = empty()
    parent(objs, root)
    return root


def cup(col, loc, r=0.36, depth=0.78, clay=False):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=(loc[0], loc[1], loc[2] + depth / 2), vertices=96)
    c = bpy.context.object
    bm = bmesh.new(); bm.from_mesh(c.data)
    top = [f for f in bm.faces if f.normal.z > 0.9]
    bmesh.ops.delete(bm, geom=top, context='FACES')
    for v in bm.verts:   # gentle taper and a rounded base
        k = (v.co.z + depth / 2) / depth
        s = 0.9 + 0.1 * k
        v.co.x *= s; v.co.y *= s
    bm.to_mesh(c.data); bm.free()
    sol = c.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.035; sol.offset = -1
    bv = c.modifiers.new('b', 'BEVEL'); bv.width = 0.012; bv.segments = 4; bv.limit_method = 'ANGLE'
    sub = c.modifiers.new('ss', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    c.data.materials.append(mat('cup', col, rough=0.22 if not clay else 0.5, coat=0.7 if not clay else 0.1, sss=0.02 if not clay else 0.12))
    bpy.ops.object.shade_smooth()
    return c


def place_brush(root, base, lean_deg, twist_deg=0, lean_axis='x'):
    root.location = base
    root.rotation_euler = (0, math.radians(lean_deg), math.radians(twist_deg))


def camera(loc, target, lens, res, fstop=None, focus=None):
    cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = loc
    dv = Vector(target) - Vector(loc)
    cam.rotation_euler = dv.to_track_quat('-Z', 'Y').to_euler()
    cd.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop; cd.dof.focus_distance = focus or dv.length
    return cam


def sun(direction, energy, col=(1.0, 0.9, 0.78), angle=2.0):
    bpy.ops.object.light_add(type='SUN')
    s = bpy.context.object
    s.rotation_euler = (-Vector(direction)).to_track_quat('Z', 'Y').to_euler()
    s.data.energy = energy; s.data.color = col; s.data.angle = math.radians(angle)
    return s


def area(loc, target, size, energy, col=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc)
    a = bpy.context.object
    a.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    a.data.size = size; a.data.energy = energy; a.data.color = col
    return a


def tiled_wall(y=0.9, col='#F2EFEA', tile=0.62, grout='#D9D4CC'):
    m = bpy.data.materials.new('tiles'); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.18; b.inputs['Coat Weight'].default_value = 0.4
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.0; br.squash = 1.0
    br.inputs['Color1'].default_value = lin(col); br.inputs['Color2'].default_value = lin(col)
    br.inputs['Mortar'].default_value = lin(grout)
    br.inputs['Scale'].default_value = 1.0 / tile; br.inputs['Mortar Size'].default_value = 0.012
    br.inputs['Brick Width'].default_value = 1.0; br.inputs['Row Height'].default_value = 1.0
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); com = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs[0])
    nt.links.new(sep.outputs['X'], com.inputs['X']); nt.links.new(sep.outputs['Z'], com.inputs['Y'])
    nt.links.new(com.outputs[0], br.inputs['Vector'])
    nt.links.new(br.outputs['Color'], b.inputs['Base Color'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.004
    nt.links.new(br.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y, 1.5), rotation=(math.radians(90), 0, 0))
    w = bpy.context.object; w.scale = (12, 8, 1); w.data.materials.append(m)
    return w


MAG, ORA, LAVCUP = '#B7006E', '#FF6411', '#E7D5EC'
os.makedirs(OUT, exist_ok=True)

if MODE in ('shelf', 'shadow'):
    shelf_m = mat('shelf', '#FBFAF8', rough=0.25, coat=0.3)
    rbox((8, 1.3, 0.12), (0, 0.0, -0.06), shelf_m, 0.02)
    tiled_wall(1.25 if MODE == 'shadow' else 0.9)
    c = cup(LAVCUP, (0, 0.1 if MODE == 'shadow' else 0.2, 0.0), r=0.52 if MODE == 'shadow' else 0.36, depth=0.7 if MODE == 'shadow' else 0.78)
    b1 = toothbrush(MAG, '#7FC8F8', 1)
    b2 = toothbrush(ORA, '#9BE07A', 2)
    if MODE == 'shelf':
        place_brush(b1, (-0.12, 0.22, 0.08), 16, -14)
        place_brush(b2, (0.12, 0.18, 0.08), -15, 18)
        # a little toothpaste-free realism: a folded face cloth and a soap at the edge, out of focus
        rbox((0.9, 0.7, 0.16), (1.55, 0.25, 0.08), mat('cloth', '#F6EAF3', rough=0.9, sss=0.05, bump=(60, 0.4)), 0.06)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(-1.4, 0.3, 0.1), segments=48, ring_count=24)
        so = bpy.context.object; so.scale = (1.3, 0.85, 0.42); so.data.materials.append(mat('soap', '#FFFFFF', rough=0.3, sss=0.3)); bpy.ops.object.shade_smooth()
        area((-3.5, -2.2, 3.4), (0, 0.2, 0.9), 3.5, 900, (1.0, 0.93, 0.85))           # window, top left
        area((2.8, -2.5, 1.6), (0, 0.2, 0.8), 3, 140, (0.95, 0.95, 1.0))              # soft fill
        sun((0.55, 0.45, -0.7), 1.6, (1.0, 0.86, 0.68), 4)
        camera((0.55, -3.3, 1.35), (0.0, 0.2, 0.92), 70, (1080, 760), fstop=2.2, focus=3.55)
    else:
        # brushes cross near their heads: their shadows make the roof; the cup's shadow is the house
        a = math.atan2(-0.62, 0.74)
        u = (math.cos(a), math.sin(a))
        d = 0.3
        place_brush(b1, (-d * u[0], 0.1 - d * u[1], 0.12), 11.8, math.degrees(a))
        place_brush(b2, (d * u[0], 0.1 + d * u[1], 0.12), -11.8, math.degrees(a))
        sun((0.62, 0.74, -0.18), 5.0, (1.0, 0.84, 0.62), 0.5)                          # low morning sun from the left
        area((-3.0, -2.5, 3.0), (0, 0.2, 1.0), 4, 120, (1.0, 0.95, 0.9))
        camera((0.45, -4.3, 1.25), (0.5, 0.6, 1.05), 50, (1080, 1350), fstop=7.0, focus=4.6)

if MODE == 'clay':
    world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#F6EAF3')
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
    # studio sweep
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    bpy.context.object.data.materials.append(mat('floor', '#F3E3EE', rough=0.7))
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(mat('back', '#EED9E8', rough=0.8))
    clay = mat('house', '#F6EAF3', rough=0.55, sss=0.15)
    roofm = mat('roof', '#5B174F', rough=0.45, sss=0.08)
    rbox((1.3, 1.0, 0.95), (0, 0.3, 0.475), clay, 0.12, 6)
    # roof: two slabs
    for s in (-1, 1):
        rbox((0.9, 1.2, 0.14), (s * 0.34, 0.3, 1.1), roofm, 0.06, 5, rot=(0, math.radians(s * 38), 0))
    rbox((0.36, 0.06, 0.46), (0, -0.21, 0.3), mat('door', '#FF6411', rough=0.45, sss=0.1), 0.07, 5)
    for x in (-0.4, 0.4):
        rbox((0.24, 0.06, 0.24), (x, -0.21, 0.62), mat('win', '#FFE7C2', rough=0.3, emit='#FFD08A', estr=0.6), 0.05, 5)
    b1 = toothbrush(MAG, '#7FC8F8', 1)
    b2 = toothbrush(ORA, '#9BE07A', 2)
    place_brush(b1, (-0.32, 0.32, 0.4), 12.5, -10)
    place_brush(b2, (0.32, 0.28, 0.4), -12.5, 12)
    glass = mat('bubble', '#FFFFFF', rough=0.0, trans=1.0, ior=1.33)
    rng = random.Random(4)
    for k in range(9):
        r = rng.uniform(0.05, 0.16)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(rng.uniform(-1.3, 1.3), rng.uniform(-0.4, 0.6), rng.uniform(1.0, 2.6)), segments=48, ring_count=24)
        bpy.context.object.data.materials.append(glass); bpy.ops.object.shade_smooth()
    area((-3, -3, 4), (0, 0.3, 0.8), 5, 900, (1.0, 0.96, 0.92))
    area((3, -2, 2), (0, 0.3, 0.8), 4, 300, (1.0, 0.9, 0.95))
    area((0, 2, 5), (0, 0.3, 1.0), 4, 250, (1.0, 0.95, 1.0))
    camera((0.0, -5.0, 1.6), (0.0, 0.3, 1.12), 50, (1080, 1350), fstop=4.0, focus=5.2)

sc.render.filepath = f'{OUT}/{MODE}.png'
bpy.ops.render.render(write_still=True)
print('rendered', MODE, flush=True)
