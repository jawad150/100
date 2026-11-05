"""Organic Fostering "Two Toothbrushes" — Option B, the premium version: "Shadow House".

Low morning sun through a real window frame lays a bright window-shaped patch on white subway tiles. Inside it, the two
leaning brushes and their cup cast the shadow of a little house; a small four-pane window cut through the lavender cup
lets the sun through, so the shadow house has a glowing window. Oak shelf, water droplets, eucalyptus out of focus.

Usage: python3 blender_tb2.py [samples] [pct] [cam]
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [sys.argv[0], 'shadow'] + sys.argv[1:]
SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 160
PCT = int(sys.argv[3]) if len(sys.argv) > 3 else 100
# reuse the toothbrush / cup / material builders from the first script (it renders nothing until its end, so import pieces)
src = open(os.path.join(HERE, 'blender_tb.py')).read()
src = src.split("MAG, ORA, LAVCUP = ")[0]
ns = {'__file__': os.path.join(HERE, 'blender_tb.py'), '__name__': 'tbbase'}
exec(compile(src, 'blender_tb_base', 'exec'), ns)
lin, mat, rbox, toothbrush, cup, place_brush, camera, area, empty, parent = (ns[k] for k in (
    'lin', 'mat', 'rbox', 'toothbrush', 'cup', 'place_brush', 'camera', 'area', 'empty', 'parent'))
sc = bpy.context.scene
sc.cycles.samples = SAMPLES
sc.render.resolution_percentage = PCT
sc.view_settings.look = 'AgX - High Contrast'
OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_tb', 'renders'))
world = sc.world
world.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#C9D3E6')     # cool morning skylight
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.22

MAG, ORA, LAVCUP = '#B7006E', '#FF6411', '#E3CFEA'
D = Vector((0.62, 0.74, -0.2)).normalized()          # sunlight travel direction (from front-left, low)
WALL_Y = 1.25


# ------------------------------------------------------------------ set
def subway_wall():
    m = bpy.data.materials.new('subway'); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.12; b.inputs['Coat Weight'].default_value = 0.6
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.5; br.offset_frequency = 2
    br.inputs['Color1'].default_value = lin('#F7F5F1'); br.inputs['Color2'].default_value = lin('#EFECE6')
    br.inputs['Mortar'].default_value = lin('#D6D0C6')
    br.inputs['Scale'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.008
    br.inputs['Mortar Smooth'].default_value = 0.6
    br.inputs['Brick Width'].default_value = 0.42; br.inputs['Row Height'].default_value = 0.21
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); com = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(geo.outputs['Position'], sep.inputs[0])
    nt.links.new(sep.outputs['X'], com.inputs['X']); nt.links.new(sep.outputs['Z'], com.inputs['Y'])
    nt.links.new(com.outputs[0], br.inputs['Vector'])
    nt.links.new(br.outputs['Color'], b.inputs['Base Color'])
    # bevelled tile edges: invert the mortar mask into a soft bump
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6; bp.inputs['Distance'].default_value = 0.006
    nt.links.new(br.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, WALL_Y, 1.5), rotation=(math.radians(90), 0, 0))
    w = bpy.context.object; w.scale = (14, 8, 1); w.data.materials.append(m)


def oak():
    m = bpy.data.materials.new('oak'); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.32; b.inputs['Coat Weight'].default_value = 0.35
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 2.2; wv.inputs['Distortion'].default_value = 6
    wv.inputs['Detail'].default_value = 6; wv.bands_direction = 'X'
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.4, 6, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].color = lin('#B98455'); cr.color_ramp.elements[1].color = lin('#DDB283')
    nt.links.new(wv.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    return m


subway_wall()
rbox((9, 1.5, 0.16), (0, 0.45, -0.08), oak(), 0.02)

# window frame between the sun and the set (invisible to the camera)
target = Vector((0.95, WALL_Y, 0.78))
wc = target - D * 4.2
fr = empty((0, 0, 0))
pieces = []
Ow, Oh, bar = 2.3, 2.7, 0.07
blk = mat('occ', '#222222', rough=0.9)
for (x, z, w, h) in ((-(Ow / 2 + 3), 0, 6, 14), ((Ow / 2 + 3), 0, 6, 14), (0, (Oh / 2 + 3), Ow, 6), (0, -(Oh / 2 + 3), Ow, 6),
                     (-0.62, 0, bar, Oh), (0, 0.95, Ow, bar)):
    pieces.append(rbox((w, 0.05, h), (x, 0, z), blk, 0))
parent(pieces, fr)
fr.location = wc
fr.rotation_euler = D.to_track_quat('Y', 'Z').to_euler()
for p in pieces:
    p.visible_camera = False
    p.visible_glossy = False

# cup with a four-pane window cut straight through along the sunlight
c = cup(LAVCUP, (0, 0.1, 0.0), r=0.52, depth=0.7)
cut_root = empty((0, 0.1, 0.43))
cuts = []
pw = 0.075
for dx in (-1, 1):
    for dz in (-1, 1):
        cuts.append(rbox((pw, 3.0, pw), (dx * (pw / 2 + 0.012), 0.1, 0.43 + dz * (pw / 2 + 0.012)), mat('cutm', '#000000'), 0))
parent(cuts, cut_root)
cut_root.rotation_euler = D.to_track_quat('Y', 'Z').to_euler()
bpy.context.view_layer.update()
for k in cuts:
    k.hide_render = True
    bo = c.modifiers.new('cut', 'BOOLEAN'); bo.object = k; bo.operation = 'DIFFERENCE'; bo.solver = 'EXACT'
# keep the bevel/subsurf after the cuts
for name in ('b', 'ss'):
    if name in c.modifiers:
        bpy.ops.object.select_all(action='DESELECT'); c.select_set(True); bpy.context.view_layer.objects.active = c
        while c.modifiers.find(name) < len(c.modifiers) - 1:
            bpy.ops.object.modifier_move_down(modifier=name)

b1 = toothbrush(MAG, '#7FC8F8', 1)
b2 = toothbrush(ORA, '#9BE07A', 2)
a = math.atan2(-0.62, 0.74)
u = (math.cos(a), math.sin(a))
d = 0.3
place_brush(b1, (-d * u[0], 0.1 - d * u[1], 0.12), 11.8, math.degrees(a))
place_brush(b2, (d * u[0], 0.1 + d * u[1], 0.12), -11.8, math.degrees(a))

# water droplets on the oak and the cup
glass = mat('water', '#FFFFFF', rough=0.02, trans=1.0, ior=1.33)
rng = random.Random(11)
for k in range(14):
    r = rng.uniform(0.012, 0.035)
    x, y = rng.uniform(-0.9, 0.7), rng.uniform(-0.45, 0.2)
    if math.hypot(x, y - 0.1) < 0.6:
        continue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, 0.0), segments=24, ring_count=12)
    o = bpy.context.object; o.scale = (1, 1, 0.55); o.data.materials.append(glass); bpy.ops.object.shade_smooth()

# (no foreground plant: keep the eye on the shadow house)

# ------------------------------------------------------------------ light
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.object
sun.rotation_euler = (-D).to_track_quat('Z', 'Y').to_euler()
sun.data.energy = 6.5; sun.data.color = (1.0, 0.82, 0.58); sun.data.angle = math.radians(0.45)
area((-2.5, -3.0, 2.6), (0.2, 0.4, 0.8), 4, 70, (0.82, 0.88, 1.0))        # cool skylight bounce
area((2.5, -2.0, 0.5), (0.4, 0.6, 0.6), 3, 25, (1.0, 0.9, 0.85))

cam_mode = sys.argv[4] if len(sys.argv) > 4 else 'main'
camera((0.5, -4.2, 1.12), (0.55, 0.6, 0.84), 45, (1080, 1350), fstop=2.8, focus=4.25)
sc.render.filepath = f'{OUT}/shadow2.png'
bpy.ops.render.render(write_still=True)
print('rendered shadow2', flush=True)
