"""OF "Can we put it on the fridge?" - 3D scene: a cream fridge door in morning window light, a child's hand pressing a
crayon drawing to it (its top-right corner curling off towards the camera), a carer's hand in a plum cardigan holding
out a magnet. Lived-in details: a swimming letter, a snapshot, letter magnets in brand colours.

Run: blender -b -P blender_fridge.py -- [draft]  -> workspace_fridge/render/beauty.png + drawing.png (drawing only, RGBA)
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, box, cyl, sph, hexc

ROOT = os.path.abspath(os.path.join(HERE, '..'))
TEX = f'{ROOT}/workspace_fridge/tex'
OUT = f'{ROOT}/workspace_fridge/render'
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
DRAFT = 'draft' in argv

PLUM, MAG, ORANGE, GREEN = hexc('#5B174F'), hexc('#B7006E'), hexc('#FF6411'), hexc('#61A80A')
SKIN_C, SKIN_A = hexc('#B97A57'), hexc('#8D5A3E')


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 48 if DRAFT else 160
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = (700, 800) if DRAFT else (1400, 1600)
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.95, 0.9, 0.85, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.35
    return sc


def img_mat(path, rough=0.75, sss=0.0):
    m = bpy.data.materials.new('img')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
    return m


def skin(col):
    m = mat(col, 0.45, coat=0.15)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Subsurface Weight'].default_value = 0.35
    b.inputs['Subsurface Radius'].default_value = (0.9, 0.45, 0.3)
    b.inputs['Subsurface Scale'].default_value = 0.08
    return m


def knit(col, scale=60.0):
    """Soft knit: rough fabric with fine ribs as a bump."""
    m = mat(col, 0.9, coat=0.0)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Sheen Weight'].default_value = 0.6
    nt = m.node_tree
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.inputs['Scale'].default_value = scale
    wv.inputs['Distortion'].default_value = 2.0
    bm = nt.nodes.new('ShaderNodeBump')
    bm.inputs['Strength'].default_value = 0.35
    nt.links.new(wv.outputs['Fac'], bm.inputs['Height'])
    nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def capsule(p0, p1, r0, r1=None):
    """Tapered capsule between two points (cone + two spheres)."""
    r1 = r0 if r1 is None else r1
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    objs = []
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r0, radius2=r1, depth=d.length, location=(p0 + p1) / 2)
    o = act()
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.to_track_quat('Z', 'Y')
    objs.append(o)
    for p, r in ((p0, r0), (p1, r1)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=r, location=p)
        objs.append(act())
    return objs


def ellipsoid(c, s, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=c)
    o = act()
    o.scale = s
    o.rotation_euler = rot
    return [o]


def blend(objs, m, voxel=0.012, smooth_it=12):
    """Join the parts and melt them into one soft clay-like form (voxel remesh + smoothing)."""
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = act()
    r = o.modifiers.new('r', 'REMESH')
    r.mode, r.voxel_size = 'VOXEL', voxel
    s = o.modifiers.new('s', 'SMOOTH')
    s.factor, s.iterations = 0.9, smooth_it
    bpy.ops.object.shade_smooth()
    return setm(o, m)


def rot2(v, ang):
    """Rotate a vector in the x-z plane (the fridge face) by ang degrees."""
    a = math.radians(ang)
    return Vector((v.x * math.cos(a) - v.z * math.sin(a), v.y, v.x * math.sin(a) + v.z * math.cos(a)))


# ------------------------------------------------------------------ scene
sc = reset()
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 58
cam.location = (0.45, -8.6, 0.8)
cam.rotation_euler = (math.radians(90), 0, math.radians(2))
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 8.5
cam.data.dof.aperture_fstop = 5.6

# fridge door (front face at y = 0), freezer split, handle
door = mat(hexc('#EEE7DD'), 0.32, coat=0.5)
box((8.0, 0.6, 10.0), loc=(-0.2, 0.3, 0.2), m=door, bw=0.12)
box((8.1, 0.05, 0.05), loc=(-0.2, -0.01, 3.55), m=mat(hexc('#6E655C'), 0.6, coat=0.0), bw=0.01)
steel = mat(hexc('#B9B6B0'), 0.25, 0.9)
cyl(0.09, 4.2, loc=(-3.35, -0.42, 0.9), m=steel, bw=0.02)
for z in (2.8, -1.0):
    cyl(0.07, 0.42, loc=(-3.35, -0.2, z), m=steel, rot=(math.radians(90), 0, 0), bw=0.01)

# the drawing: subdivided paper, slightly bowed, its top-right corner peeling up towards the camera
DC, DW, DH, DROT = Vector((0.45, -0.03, 0.75)), 2.9, 2.175, 7.0
bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=45, size=1)
pap = act()
pap.name = 'drawing'
me = pap.data
bm = bmesh.new()
bm.from_mesh(me)
for v in bm.verts:
    u, w = v.co.x + 0.5, v.co.y + 0.5                       # 0..1 across, 0..1 up
    x, z = (u - 0.5) * DW, (w - 0.5) * DH
    k = max(0.0, (u - 0.58) / 0.42) * max(0.0, (0.5 - w) / 0.5)
    lift = 1.15 * k ** 1.5 + 0.02 * math.sin(u * math.pi * 2)
    p = rot2(Vector((x, 0, z)), DROT) + DC + Vector((0, -lift, 0))
    v.co = p
bm.to_mesh(me)
bm.free()
uv = me.uv_layers.new() if not me.uv_layers else me.uv_layers[0]
bpy.ops.object.shade_smooth()
sol = pap.modifiers.new('s', 'SOLIDIFY')
sol.thickness = 0.004
setm(pap, img_mat(f'{TEX}/drawing.png', 0.8, sss=0.05))

# lived-in fridge: swimming letter + snapshot with magnets, letter magnets in brand colours
def flat(path, w, h, c, ang, name):
    bpy.ops.mesh.primitive_plane_add(size=1, location=c)
    o = act()
    o.name = name
    o.scale = (w, h, 1)
    o.rotation_euler = (math.radians(90), math.radians(ang), 0)
    s = o.modifiers.new('s', 'SOLIDIFY')
    s.thickness = 0.004
    return setm(o, img_mat(path, 0.7))


flat(f'{TEX}/letter.png', 1.5, 2.06, (2.65, -0.012, -1.55), -4, 'letter')
flat(f'{TEX}/snapshot.png', 1.25, 1.41, (-2.15, -0.012, 2.4), 6, 'snap')


def magnet(c, col, r=0.16, d=0.1):
    cyl(r, d, loc=c, m=mat(col, 0.22, coat=0.8), rot=(math.radians(90), 0, 0), bw=0.035)


magnet((2.65, -0.07, -0.55), ORANGE)
magnet((-2.15, -0.07, 3.0), GREEN, 0.13)
for ch, col, x, z, r in (('A', ORANGE, -2.6, -1.4, 8), ('b', GREEN, -2.05, -1.55, -6), ('c', MAG, -1.55, -1.35, 10), ('O', PLUM, 3.0, 2.6, -8)):
    bpy.ops.object.text_add(location=(x, -0.02, z), rotation=(math.radians(90), math.radians(r), 0))
    t = act()
    t.data.body = ch
    t.data.size = 0.62
    t.data.extrude = 0.05
    t.data.bevel_depth = 0.02
    t.data.align_x = t.data.align_y = 'CENTER'
    setm(t, mat(col, 0.2, coat=0.9))

# ------------------------------------------------------------------ the child's hand: pressing the drawing's lower-left
P = rot2(Vector((-1.0, 0, -0.42)), DROT) + DC + Vector((0, -0.17, 0))
u = rot2(Vector((0.35, 0, 0.94)), DROT).normalized()       # wrist -> fingers
v = Vector((u.z, 0, -u.x))                                   # across the hand (towards the pinky)
parts = ellipsoid(P, (0.19, 0.07, 0.21), (0, math.atan2(u.x, u.z), 0))
for s, L, spread in ((-0.13, 0.3, -16), (-0.045, 0.35, -5), (0.045, 0.33, 6), (0.13, 0.25, 17)):
    base = P + u * 0.18 + v * s
    dvec = rot2(u, spread)
    mid = base + dvec * L * 0.55 + Vector((0, 0.03, 0))
    tip = base + dvec * L + Vector((0, 0.1, 0))
    parts += capsule(base, mid, 0.043, 0.04) + capsule(mid, tip, 0.04, 0.036)
tb = P - u * 0.04 - v * 0.17
tdir = rot2(u, -58)
parts += capsule(tb, tb + tdir * 0.15 + Vector((0, 0.03, 0)), 0.06, 0.055) + capsule(tb + tdir * 0.15 + Vector((0, 0.03, 0)), tb + tdir * 0.27 + Vector((0, 0.08, 0)), 0.055, 0.048)
parts += capsule(P - u * 0.12, P - u * 0.9 - Vector((0, 0.35, 0)), 0.11, 0.13)          # wrist + forearm
blend(parts, skin(SKIN_C), voxel=0.007, smooth_it=5)
sleeve = capsule(P - u * 0.42 - Vector((0, 0.12, 0)), P - u * 3.2 - Vector((0, 1.0, 0)), 0.2, 0.26)
blend(sleeve, knit(hexc('#6E9C3A'), 80), voxel=0.02, smooth_it=6)
bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.05, location=P - u * 0.44 - Vector((0, 0.13, 0)))
cuff = act()
cuff.rotation_mode = 'QUATERNION'
cuff.rotation_quaternion = (-u - Vector((0, 0.35, 0))).to_track_quat('Z', 'Y')
setm(cuff, knit(hexc('#5D8A2E'), 140))

# ------------------------------------------------------------------ the carer's hand: holding a plum magnet out
M = rot2(Vector((0.55, 0, 1.0)), DROT) + DC + Vector((0, -0.55, 0))
magnet(M, PLUM, 0.19, 0.12)
A = M + Vector((0.62, -0.28, 0.02))
ua = Vector((-0.96, 0.12, -0.12)).normalized()               # wrist -> fingers (pointing left)
parts = ellipsoid(A, (0.26, 0.1, 0.24), (0, math.radians(8), math.radians(-6)))
it = M + Vector((0.06, -0.02, 0.2))                           # index fingertip on the magnet's top edge
ib = A + ua * 0.22 + Vector((0, 0, 0.13))
parts += capsule(ib, (ib + it) / 2 + Vector((0, -0.03, 0.06)), 0.072, 0.066) + capsule((ib + it) / 2 + Vector((0, -0.03, 0.06)), it, 0.066, 0.058)
th = M + Vector((0.07, -0.05, -0.2))                          # thumb tip on the bottom edge
tb2 = A + Vector((-0.1, -0.06, -0.17))
parts += capsule(tb2, (tb2 + th) / 2 + Vector((0, -0.04, -0.05)), 0.085, 0.072) + capsule((tb2 + th) / 2 + Vector((0, -0.04, -0.05)), th, 0.072, 0.062)
for dz, L in ((0.03, 0.2), (-0.06, 0.18), (-0.14, 0.15)):     # middle, ring and little fingers curled under
    kb = A + ua * 0.2 + Vector((0, 0.02, dz))
    k1 = kb + ua * L + Vector((0, 0.06, -0.03))
    k2 = k1 + Vector((0.1, 0.07, -0.08))
    parts += capsule(kb, k1, 0.07, 0.064) + capsule(k1, k2, 0.064, 0.056)
parts += capsule(A - ua * 0.15, A - ua * 1.0 + Vector((0, -0.15, -0.1)), 0.13, 0.15)
blend(parts, skin(SKIN_A), voxel=0.008, smooth_it=6)
sleeve = capsule(A - ua * 0.5, A - ua * 3.6 + Vector((0, -0.4, -0.6)), 0.24, 0.3)
blend(sleeve, knit(hexc('#5B174F'), 70), voxel=0.02, smooth_it=6)

# ------------------------------------------------------------------ morning window light (with mullion shadows) + fill
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
sun.data.energy = 4.2
sun.data.angle = math.radians(2.5)
sun.data.color = (1.0, 0.9, 0.78)
sd = Vector((-0.75, 0.45, -0.5)).normalized()                  # light travels down-left onto the door
sun.rotation_euler = sd.to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(sun)
win = mat(hexc('#333333'), 0.9)
o = Vector((0.6, 0.1, 0.9)) - sd * 6.0                         # window frame sits up-right, out of shot
for off, size in ((Vector((0, 0, 0)), (0.12, 0.12, 9)), (Vector((0, 0, 0.3)), (9, 0.12, 0.12)), (Vector((-2.6, 0, 0)), (0.3, 0.3, 9)),
                  (Vector((2.6, 0, 0)), (0.3, 0.3, 9)), (Vector((0, 0, 2.9)), (9, 0.3, 0.3)), (Vector((0, 0, -2.6)), (9, 0.3, 0.3))):
    b = box(size, loc=o + off, m=win, bw=0.0)
    b.visible_camera = False
fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'AREA'))
fill.data.energy, fill.data.size = 420, 7
fill.data.color = (0.95, 0.93, 1.0)
fill.location = (-4, -7, 2)
fill.rotation_euler = (Vector((0, 0, 0.6)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
sc.collection.objects.link(fill)

sc.render.film_transparent = False
sc.render.filepath = f'{OUT}/beauty.png'
bpy.ops.render.render(write_still=True)
print('rendered beauty', flush=True)

# drawing-only pass (everything else held out) for the frame-break composite
for ob in sc.objects:
    if ob.type in ('MESH', 'FONT', 'CURVE') and ob.name != 'drawing':
        ob.is_holdout = True
sc.render.film_transparent = True
sc.render.filepath = f'{OUT}/drawing.png'
sc.cycles.samples = 32 if DRAFT else 64
bpy.ops.render.render(write_still=True)
print('rendered drawing', flush=True)
