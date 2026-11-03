"""Organic Fostering "Room to Grow" — the hero 3D set: a cutaway miniature of one UK spare room (dollhouse diorama).

States (each a transparent PNG of the diorama, composited in 2D):
  s1 clutter   morning, boxes, folded airer, bare bulb, tired walls
  s2 clear     morning, empty, fresh walls, sun patch on the boards
  s3 bed       + single bed with lavender bedding, rug, plant
  s4 lamp      + bedside table and lamp switched on (warm afternoon)
  s5 spaces    + empty frame, empty shelf, bare pinboard, blank card on the door
  s6 dusk      same as s5, blue window, the lamp is the main light
Extra cameras:
  frame        close-up on the empty frame (soft focus), s5 light
  landing      from the dark landing: the door ajar, warm light spilling out

Usage: python3 blender_room.py <state|frame|landing> [samples] [scale%]
"""
import bpy, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_rtg', 'room'))
MODE = sys.argv[1] if len(sys.argv) > 1 else 's1'
SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 96
PCT = int(sys.argv[3]) if len(sys.argv) > 3 else 100

ORDER = ['s1', 's2', 's3', 's4', 's5', 's6']
LIGHT = {'frame': 's5', 'landing': 's6'}.get(MODE, MODE)
LV = ORDER.index(LIGHT)


def has(state):
    return LV >= ORDER.index(state)


def lin(h):
    h = h.lstrip('#')

    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.use_adaptive_sampling = True
sc.cycles.max_bounces = 8
sc.render.film_transparent = MODE not in ('frame', 'landing')
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.resolution_percentage = PCT
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']
dusk = LIGHT == 's6'
bg.inputs['Color'].default_value = lin('#3A3F6E') if dusk else lin('#F3E6EE')
bg.inputs['Strength'].default_value = 0.25 if dusk else 0.55
if MODE == 'landing':
    bg.inputs['Strength'].default_value = 0.02

MATS = {}


def mat(name, col, rough=0.5, metal=0.0, coat=0.0, emit=None, estr=0.0, bump=None, sss=0.0, trans=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    if emit is not None:
        b.inputs['Emission Color'].default_value = emit
        b.inputs['Emission Strength'].default_value = estr
    if bump:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bump[0]; n.inputs['Detail'].default_value = 10
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump[1]; bp.inputs['Distance'].default_value = 0.003
        nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    MATS[name] = m
    return m


def box(x0, x1, y0, y1, z0, z1, m, bevel=0.0, seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg
    o.data.materials.append(m)
    return o


def cyl(r, d, loc, m, rot=(0, 0, 0), v=48, smooth=True):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object
    o.data.materials.append(m)
    if smooth:
        bpy.ops.object.shade_smooth()
    return o


# ------------------------------------------------------------------ materials
WALL = mat('wall', lin('#E7DDD2') if LIGHT == 's1' else lin('#F6EEE6'), rough=0.9, bump=(90, 0.12))
SECTION = mat('section', lin('#5B174F'), rough=0.6)
TRIM = mat('trim', lin('#FBF8F3'), rough=0.35, coat=0.2)
CARD = mat('cardboard', lin('#B88757'), rough=0.85, bump=(140, 0.2))
TAPE = mat('tape', lin('#D9BE93'), rough=0.4, coat=0.3)
WOOD_L = mat('woodl', lin('#C99A6B'), rough=0.45, coat=0.15, bump=(40, 0.05))

R0, R1 = -1.6, 1.6          # room x
D0, D1 = -1.5, 1.5          # room y
HT = 2.6
T = 0.15

# floor slab + boards
box(R0 - T, R1, D0, D1 + T, -0.22, -0.02, SECTION)
random.seed(3)
x = R0 - T
k = 0
while x < R1 - 1e-6:
    w = min(0.2, R1 - x)
    tone = random.uniform(-0.06, 0.05)
    base = (0.70 + tone, 0.50 + tone * 0.9, 0.33 + tone * 0.7)
    col = tuple(((c + 0.055) / 1.055) ** 2.4 for c in base) + (1,)
    box(x + 0.004, x + w - 0.004, D0, D1 + T, -0.02, 0.0, mat(f'board{k % 6}', col, rough=0.42, coat=0.2, bump=(60, 0.06)), bevel=0.004, seg=2)
    x += w; k += 1

# back wall with window opening (x 0.25..1.25, z 0.9..2.15)
WX0, WX1, WZ0, WZ1 = 0.25, 1.25, 0.9, 2.15
box(R0 - T, WX0, D1, D1 + T, 0, HT, WALL)
box(WX1, R1, D1, D1 + T, 0, HT, WALL)
box(WX0, WX1, D1, D1 + T, 0, WZ0, WALL)
box(WX0, WX1, D1, D1 + T, WZ1, HT, WALL)
# left wall with door opening (y -1.28..-0.42, z 0..2.05)
DY0, DY1, DZ = -1.28, -0.42, 2.05
box(R0 - T, R0, D0, DY0, 0, HT, WALL)
box(R0 - T, R0, DY1, D1 + T, 0, HT, WALL)
box(R0 - T, R0, DY0, DY1, DZ, HT, WALL)
if MODE == 'landing':
    box(R0 - T, R0, D0 - 1.2, D0, 0, HT, WALL)
# section caps (plum cut edges)
if MODE == 'landing':
    box(R1, R1 + T, D0, D1, 0, HT, WALL)
if MODE != 'landing':
  box(R0 - T - 0.003, R1 + 0.003, D1 - 0.003, D1 + T + 0.003, HT, HT + 0.012, SECTION)
  box(R0 - T - 0.003, R0 + 0.003, D0 - 0.003, D1 + T, HT, HT + 0.012, SECTION)
  box(R1, R1 + 0.012, D1, D1 + T, 0, HT, SECTION)
  box(R0 - T, R0, D0 - 0.012, D0, 0, HT, SECTION)
# skirting
box(R0, R1, D1 - 0.025, D1, 0, 0.12, TRIM, bevel=0.006)
box(R0, R0 + 0.025, D0, DY0, 0, 0.12, TRIM, bevel=0.006)
box(R0, R0 + 0.025, DY1, D1, 0, 0.12, TRIM, bevel=0.006)

# window: frame, sash bars, sill, sky card behind
f = 0.06
for (a, b, c, d) in ((WX0 - f, WX0, WZ0, WZ1), (WX1, WX1 + f, WZ0, WZ1)):
    box(a, b, D1 - 0.03, D1 + 0.05, c, d, TRIM, bevel=0.008)
box(WX0 - f, WX1 + f, D1 - 0.03, D1 + 0.05, WZ1, WZ1 + f, TRIM, bevel=0.008)
box(WX0 - 0.1, WX1 + 0.1, D1 - 0.14, D1 + 0.02, WZ0 - 0.05, WZ0, TRIM, bevel=0.01)
mid = (WZ0 + WZ1) / 2
box(WX0, WX1, D1 + 0.02, D1 + 0.06, mid - 0.025, mid + 0.025, TRIM)
box((WX0 + WX1) / 2 - 0.018, (WX0 + WX1) / 2 + 0.018, D1 + 0.03, D1 + 0.06, WZ0, WZ1, TRIM)
sky_top, sky_bot = (lin('#1E2A5E'), lin('#E07A5F')) if dusk else (lin('#8EC1E8'), lin('#FBE7CF'))
bpy.ops.mesh.primitive_plane_add(size=1, location=((WX0 + WX1) / 2, D1 + 0.3, mid), rotation=(math.radians(90), 0, 0))
sky = bpy.context.object; sky.scale = (1.4, 1.7, 1)
sm = bpy.data.materials.new('sky'); sm.use_nodes = True
nt = sm.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
outn = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Y'], ramp.inputs['Fac'])
ramp.color_ramp.elements[0].color = sky_bot; ramp.color_ramp.elements[1].color = sky_top
ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.75
nt.links.new(ramp.outputs['Color'], em.inputs['Color']); em.inputs['Strength'].default_value = 1.4 if dusk else 2.2
nt.links.new(em.outputs[0], outn.inputs['Surface'])
sky.data.materials.append(sm)
sky.visible_shadow = False
# tree silhouettes on the sky card (soft green blobs, morning only reads)
for tx, tz, tr in ((0.35, 1.1, 0.28), (0.6, 0.98, 0.22), (1.05, 1.05, 0.3)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=tr, location=(tx, D1 + 0.27, tz), segments=24, ring_count=12)
    t = bpy.context.object; t.scale = (1, 0.3, 1)
    t.data.materials.append(mat('tree', lin('#3E4A63') if dusk else lin('#7FA37A'), rough=0.9))
    t.visible_shadow = False

# door (opens into the room, hinged at the y=DY1 side), architrave
for (a, b) in ((DY0 - 0.07, DY0), (DY1, DY1 + 0.07)):
    box(R0, R0 + 0.025, a, b, 0, DZ + 0.07, TRIM, bevel=0.006)
box(R0, R0 + 0.025, DY0 - 0.07, DY1 + 0.07, DZ, DZ + 0.07, TRIM, bevel=0.006)
DW = DY1 - DY0 - 0.02
bpy.ops.object.empty_add(location=(0, 0, 0))
hinge = bpy.context.object
DM = mat('door', lin('#F2EEE8'), rough=0.4, coat=0.2)
parts = [box(0, 0.045, -DW, 0, 0.01, DZ - 0.01, DM, bevel=0.008)]
for zz in ((0.25, 0.95), (1.1, 1.85)):
    parts.append(box(0.044, 0.054, -DW + 0.1, -0.1, zz[0], zz[1], mat('doorp', lin('#E9E3DB'), rough=0.45), bevel=0.004))
parts.append(cyl(0.035, 0.07, (0.08, -DW + 0.08, 1.0), mat('brass', lin('#C9A45C'), metal=1, rough=0.3), rot=(0, math.radians(90), 0)))
if has('s5'):
    parts.append(box(0.054, 0.06, -DW / 2 - 0.15, -DW / 2 + 0.15, 1.42, 1.62, mat('namecard', lin('#FFFFFF'), rough=0.6), bevel=0.004))
    parts.append(box(-0.016, -0.01, -DW / 2 - 0.15, -DW / 2 + 0.15, 1.42, 1.62, mat('namecard', None), bevel=0.004))
    parts.append(cyl(0.012, 0.02, (-0.022, -DW / 2, 1.6), mat('pinp', lin('#B7006E'), rough=0.3, coat=0.6), rot=(0, math.radians(90), 0)))
    parts.append(cyl(0.012, 0.02, (0.066, -DW / 2, 1.6), mat('pinp', lin('#B7006E'), rough=0.3, coat=0.6), rot=(0, math.radians(90), 0)))
for o in parts:
    o.parent = hinge
hinge.location = (R0, DY1 - 0.01, 0)
hinge.rotation_euler = (0, 0, math.radians(72 if MODE != 'landing' else 58))

# landing behind the door (dim hallway)
LAND = mat('landwall', lin('#D8CFC6') if MODE == 'landing' else lin('#7A6A62'), rough=0.9)
if MODE != 'landing':
    box(R0 - T - 0.12, R0 - T, DY0 - 0.02, DY1 + 0.02, -0.22, 0.0, mat('landfloor', lin('#8A6646'), rough=0.5, coat=0.15))
    box(R0 - T - 0.12, R0 - T - 0.08, DY0 - 0.02, DY1 + 0.02, 0, DZ + 0.02, LAND)
if MODE == 'landing':
    box(R0 - 3.2, R0 - T, D0 - 1.35, D0 - 1.2, 0, HT, LAND)
    box(R0 - 3.2, R0 - T, D1, D1 + 0.15, 0, HT, LAND)
    box(R0 - 3.2, R0 - T, D0 - 1.35, D1 + 0.15, HT, HT + 0.1, LAND)
    box(R0 - 3.2, R0 - T, D0 - 1.2, D1, -0.22, 0.0, mat('landfloor', lin('#8A6646'), rough=0.62, coat=0.05, bump=(30, 0.05)))
    box(R0, R1, D0, D1, HT, HT + 0.1, WALL)       # room ceiling so the spill is contained
    box(R0, R1, D0 - 0.15, D0, 0, HT, WALL)       # room front wall
    # stair banister hint
    for i in range(7):
        box(R0 - 2.9 + i * 0.12, R0 - 2.87 + i * 0.12, D0 - 1.1, D0 - 1.07, 0, 0.95, TRIM)
    box(R0 - 3.0, R0 - 2.0, D0 - 1.12, D0 - 1.04, 0.95, 1.0, WOOD_L, bevel=0.01)

# ------------------------------------------------------------------ state content
if LIGHT == 's1':
    random.seed(7)
    stacks = [(0.6, -0.2, 3), (1.05, 0.4, 2), (0.15, 0.6, 2), (-0.5, 0.9, 3), (0.9, -0.85, 1), (-0.9, -0.2, 1), (-0.3, -0.6, 2)]
    for sx, sy, n in stacks:
        z = 0
        for i in range(n):
            w = random.uniform(0.42, 0.6); d = random.uniform(0.38, 0.55); h = random.uniform(0.3, 0.42)
            ang = random.uniform(-0.25, 0.25)
            o = box(-w / 2, w / 2, -d / 2, d / 2, 0, h, CARD, bevel=0.012)
            o.location = (sx + random.uniform(-0.04, 0.04), sy + random.uniform(-0.04, 0.04), z)
            o.rotation_euler = (0, 0, ang)
            t = box(-w / 2 - 0.002, w / 2 + 0.002, -0.035, 0.035, h - 0.001, h + 0.003, TAPE)
            t.parent = o
            z += h
    # folded clothes airer leaning on the left wall
    AIR = mat('airer', lin('#E9E9EC'), metal=0.6, rough=0.3)
    for i in range(9):
        yy = 0.15 + i * 0.07
        cyl(0.008, 1.25, (R0 + 0.22, yy, 0.62), AIR, rot=(0, math.radians(-12), 0), v=12)
    for zz in (0.08, 1.2):
        cyl(0.012, 0.6, (R0 + 0.22 + (0.62 - zz) * math.tan(math.radians(12)), 0.43, zz), AIR, rot=(math.radians(90), 0, 0), v=12)
    # bare bulb on a flex
    cyl(0.006, 0.55, (0.0, 0.1, HT - 0.27), mat('flex', lin('#F2F2F2'), rough=0.5), v=8)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(0.0, 0.1, HT - 0.6), segments=24, ring_count=12)
    bpy.context.object.data.materials.append(mat('bulbglass', lin('#FFFFFF'), rough=0.05, trans=0.9))
    # an old lamp, a bin bag, a rolled rug
    cyl(0.09, 1.0, (1.25, 1.2, 0.5), mat('rolled', lin('#8C7B6B'), rough=0.9), rot=(0, math.radians(90), math.radians(20)))

if has('s3'):
    BED = mat('bedwood', lin('#D9B48B'), rough=0.45, coat=0.2, bump=(40, 0.04))
    BX0, BX1, BY0, BY1 = -1.22, -0.25, -0.55, 1.47
    box(BX0, BX1, BY0, BY1, 0.08, 0.32, BED, bevel=0.02)
    for (a, b) in ((BX0, BX0 + 0.06), (BX1 - 0.06, BX1)):
        box(a, b, BY0, BY0 + 0.06, 0, 0.1, BED)
        box(a, b, BY1 - 0.06, BY1, 0, 0.1, BED)
    box(BX0 - 0.02, BX1 + 0.02, BY1 - 0.07, BY1, 0.08, 1.05, BED, bevel=0.03)          # headboard
    box(BX0 + 0.03, BX1 - 0.03, BY0 + 0.03, BY1 - 0.08, 0.32, 0.5, mat('mattress', lin('#FBFAF7'), rough=0.8), bevel=0.05, seg=5)
    duv = box(BX0 + 0.0, BX1 - 0.0, BY0 - 0.01, BY1 - 0.55, 0.36, 0.56, mat('duvet', lin('#C7B2DD'), rough=0.85, sss=0.05, bump=(25, 0.15)), bevel=0.07, seg=6)
    sub = duv.modifiers.new('s', 'SUBSURF'); sub.levels = 2; sub.render_levels = 2
    fold = box(BX0 - 0.005, BX1 + 0.005, BY1 - 0.62, BY1 - 0.48, 0.42, 0.6, mat('duvetfold', lin('#F4EFF8'), rough=0.85), bevel=0.05, seg=5)
    pil = box(BX0 + 0.1, BX1 - 0.1, BY1 - 0.42, BY1 - 0.12, 0.5, 0.66, mat('pillow', lin('#FFFFFF'), rough=0.8), bevel=0.07, seg=6)
    pil.rotation_euler = (math.radians(-10), 0, 0); pil.location.z += 0.05
    sub = pil.modifiers.new('s', 'SUBSURF'); sub.levels = 2; sub.render_levels = 2
    box(BX0 - 0.03, BX1 + 0.03, BY0 + 0.05, BY0 + 0.45, 0.555, 0.585, mat('throw', lin('#FF8A4C'), rough=0.9, bump=(200, 0.2)), bevel=0.015)
    for i in range(6):
        box(BX0 - 0.03, BX0 - 0.02, BY0 + 0.07 + i * 0.065, BY0 + 0.1 + i * 0.065, 0.42, 0.585, mat('fringe', lin('#FF8A4C'), rough=0.9))
    # rug
    box(-0.15, 1.3, -1.25, 0.35, 0.0, 0.018, mat('rug', lin('#F3DCCB'), rough=0.95, bump=(300, 0.25)), bevel=0.008)
    box(-0.05, 1.2, -1.15, 0.25, 0.018, 0.021, mat('rugin', lin('#E7B6A0'), rough=0.95))
    box(0.05, 1.1, -1.05, 0.15, 0.021, 0.024, mat('rug', None))
    # plant on the sill
    cyl(0.07, 0.13, (1.0, D1 - 0.07, WZ0 + 0.065), mat('pot', lin('#E9DCCB'), rough=0.4, coat=0.4))
    LEAFM = mat('leaf', lin('#5E8C55'), rough=0.5, sss=0.1)
    for i in range(7):
        a = i / 7 * math.tau
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(1.0 + math.cos(a) * 0.05, D1 - 0.07 + math.sin(a) * 0.04, WZ0 + 0.2 + (i % 3) * 0.03), segments=16, ring_count=8)
        lf = bpy.context.object; lf.scale = (0.5, 1.0, 0.18); lf.rotation_euler = (0.5, 0.3, a); lf.data.materials.append(LEAFM)

if has('s4'):
    TB = mat('tablew', lin('#E7C9A4'), rough=0.45, coat=0.2)
    box(-0.15, 0.22, 1.1, 1.47, 0.0, 0.5, TB, bevel=0.015)
    box(-0.13, 0.2, 1.08, 1.1, 0.27, 0.45, mat('drawer', lin('#DDBD95'), rough=0.45), bevel=0.01)
    cyl(0.018, 0.03, (0.035, 1.07, 0.36), mat('brass', None), rot=(math.radians(90), 0, 0))
    cyl(0.07, 0.03, (0.03, 1.28, 0.515), mat('lampbase', lin('#B7006E'), rough=0.25, coat=0.8))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, location=(0.03, 1.28, 0.6), segments=32, ring_count=16)
    bpy.context.object.data.materials.append(mat('lampbase', None)); bpy.ops.object.shade_smooth()
    cyl(0.01, 0.2, (0.03, 1.28, 0.75), mat('brass', None), v=12)
    bpy.ops.mesh.primitive_cone_add(radius1=0.19, radius2=0.12, depth=0.22, location=(0.03, 1.28, 0.9), vertices=48, end_fill_type='NOTHING')
    sh = bpy.context.object
    sol = sh.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.006
    on = LIGHT in ('s4', 's5', 's6')
    sh.data.materials.append(mat('shade', lin('#F6E7D3'), rough=0.8, sss=0.0, trans=0.25,
                                 emit=lin('#FFC27A'), estr=(6.0 if dusk else 3.0) if on else 0.0))
    bpy.ops.object.light_add(type='POINT', location=(0.03, 1.28, 0.86))
    lamp = bpy.context.object
    lamp.data.energy = 140 if dusk else 60
    lamp.data.color = (1.0, 0.72, 0.42)
    lamp.data.shadow_soft_size = 0.06
    # a mug and a folded towel on the bed end, a little welcome
    cyl(0.04, 0.09, (0.12, 1.36, 0.545), mat('mug', lin('#FF6411'), rough=0.25, coat=0.7))

if has('s5'):
    FR = mat('frame', lin('#B98A5B'), rough=0.4, coat=0.3)
    MOUNT = mat('mount', lin('#FFFFFF'), rough=0.7)
    fx, fz, fw, fh = -0.73, 1.62, 0.56, 0.44
    yb = D1
    box(fx - fw / 2, fx + fw / 2, yb - 0.035, yb, fz - fh / 2, fz + fh / 2, FR, bevel=0.008)
    box(fx - fw / 2 + 0.05, fx + fw / 2 - 0.05, yb - 0.04, yb - 0.03, fz - fh / 2 + 0.05, fz + fh / 2 - 0.05, MOUNT)
    box(fx - fw / 2 + 0.11, fx + fw / 2 - 0.11, yb - 0.043, yb - 0.039, fz - fh / 2 + 0.11, fz + fh / 2 - 0.11, mat('emptypane', lin('#F1ECE6'), rough=0.6))
    # empty wall shelf on the left wall
    box(R0, R0 + 0.22, 0.4, 1.3, 1.66, 1.695, WOOD_L, bevel=0.006)
    for yy in (0.55, 1.2):
        box(R0, R0 + 0.16, yy - 0.012, yy + 0.012, 1.56, 1.66, mat('bracket', lin('#2B2B2B'), metal=0.8, rough=0.4))
    # bare cork pinboard on the left wall
    box(R0, R0 + 0.03, 0.42, 1.08, 0.9, 1.36, WOOD_L, bevel=0.006)
    box(R0 + 0.025, R0 + 0.035, 0.45, 1.05, 0.93, 1.33, mat('cork', lin('#C59A68'), rough=0.9, bump=(400, 0.4)))
    for py, pz, pc in ((0.52, 1.27, '#B7006E'), (0.95, 1.0, '#FF6411'), (0.75, 1.22, '#64A60B')):
        cyl(0.012, 0.02, (R0 + 0.045, py, pz), mat('pin' + pc, lin(pc), rough=0.3, coat=0.6), rot=(0, math.radians(90), 0), v=16)

# ------------------------------------------------------------------ light
if not dusk and MODE != 'landing':
    d = Vector((-0.38, -0.78, -0.5)).normalized()
    bpy.ops.object.light_add(type='SUN')
    sun = bpy.context.object
    sun.rotation_euler = (-d).to_track_quat('Z', 'Y').to_euler()
    sun.data.energy = {'s1': 3.6, 's2': 4.4, 's3': 4.4, 's4': 3.6, 's5': 3.6}.get(LIGHT, 3.6)
    sun.data.color = (1.0, 0.86, 0.68) if LIGHT in ('s1', 's2', 's3') else (1.0, 0.78, 0.55)
    sun.data.angle = math.radians(2.5)
# soft key from the open (camera) side so the miniature reads
bpy.ops.object.light_add(type='AREA', location=(4.5, -5.0, 5.5))
key = bpy.context.object
key.data.size = 5
key.data.energy = 520 if not dusk else 70
key.data.color = (1.0, 0.95, 0.92) if not dusk else (0.55, 0.62, 1.0)
key.rotation_euler = (Vector((-0.2, 0.2, 0.9)) - key.location).to_track_quat('-Z', 'Y').to_euler()
if MODE == 'landing':
    key.data.energy = 0
    sc.view_settings.exposure = 0.0
    bpy.ops.object.light_add(type='AREA', location=(R0 + 1.3, (DY0 + DY1) / 2 + 0.6, 1.7))
    sp = bpy.context.object; sp.data.size = 1.0; sp.data.energy = 120; sp.data.color = (1.0, 0.7, 0.42)
    sp.rotation_euler = (Vector((R0 - 1.5, (DY0 + DY1) / 2, 0.2)) - sp.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.light_add(type='AREA', location=(R0 - 2.4, D0 - 0.6, HT - 0.1))
    fl = bpy.context.object; fl.data.size = 1.5; fl.data.energy = 14; fl.data.color = (0.6, 0.7, 1.0)
if LIGHT == 's1':
    bpy.ops.object.light_add(type='POINT', location=(0.0, 0.1, HT - 0.6))
    bpy.context.object.data.energy = 0.0

# ------------------------------------------------------------------ camera + render
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam


def aim(loc, target, lens, res, fstop=None, focus=None):
    cam.location = loc
    dv = Vector(target) - Vector(loc)
    cam.rotation_euler = dv.to_track_quat('-Z', 'Y').to_euler()
    cam_d.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    if fstop:
        cam_d.dof.use_dof = True
        cam_d.dof.aperture_fstop = fstop
        cam_d.dof.focus_distance = focus or dv.length


os.makedirs(OUT, exist_ok=True)
if MODE == 'frame':
    aim((-0.3, -0.25, 1.3), (-0.62, 1.45, 1.32), 32, (1080, 1920), fstop=2.0, focus=1.75)
elif MODE == 'landing':
    aim((R0 - 2.95, DY0 - 0.25, 1.45), (R0, (DY0 + DY1) / 2 - 0.1, 0.95), 26, (1080, 1920), fstop=4, focus=2.9)
else:
    aim((5.2, -6.4, 5.2), (-0.15, 0.2, 0.85), 38, (1200, 1400))
sc.render.filepath = f'{OUT}/{MODE}.png'
bpy.ops.render.render(write_still=True)
print('rendered', MODE, flush=True)
