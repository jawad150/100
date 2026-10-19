"""Blender (bpy) scene: a modelled iPhone 16 Pro with the animated MT5 UI on its display and the
quote cards as real 3D glass slabs floating above it, plus a second iPhone behind.

Textures come from `node floret/render.js atlas 30 12` (one atlas JPEG per frame + cards.json).

    python3 floret/blender_phone.py still 1,180,360        # quick preview stills
    python3 floret/blender_phone.py render 1 360           # RGBA frames -> $OUT/blender/####.png
"""
import json, math, os, sys
import bpy, bmesh
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', os.path.join(HERE, 'out'))
ATLAS = os.path.join(OUT, 'atlas')
STATE = json.load(open(os.path.join(ATLAS, 'cards.json')))
FPS, FRAMES = STATE['fps'], STATE['frames']
DUR = FRAMES / FPS

# ---------------------------------------------------------------- dimensions (1 unit = 10 mm)
# iPhone 16 Pro: 71.5 x 149.6 x 8.25 mm; 6.3" display 1206 x 2622 px @ 460 ppi -> 66.6 x 144.8 mm
BW, BH, BT = 7.15, 14.96, 0.825
BR = 1.20                       # body corner radius
DW, DH = 6.66, 14.48            # display
DR = BR - (BW - DW) / 2         # concentric display corners
SCREEN_PX = (776, 1688)         # atlas screen size in CSS px
K = DW / SCREEN_PX[0]           # CSS px -> units on the display
ATLAS_SIZE = (3750, 2550)       # atlas JPEG size (CSS px * 1.5)
AS = 1.5
CARD_W, CARD_H, CARD_R = 860, 140, 34
ATLAS_CARD_X, ATLAS_CARD_STEP, ATLAS_BACK_X = 800, 150, 1700


def rounded_rect(w, h, r, n=24):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def prism(name, outline, z0, z1, bevel=0.0, bevel_segments=6):
    """Extrude a 2D outline between z0 and z1, optionally rounding the top and bottom rims."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in outline]
    top = [bm.verts.new((x, y, z1)) for x, y in outline]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bm.normal_update()
    if bevel > 0:
        rim = [e for e in bm.edges if all(abs(v.co.z - e.verts[0].co.z) < 1e-6 for v in e.verts) and len(e.link_faces) == 2
               and any(abs(f.normal.z) > 0.99 for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=rim, offset=bevel, segments=bevel_segments, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = abs(p.normal.z) < 0.99
    return ob


def assign_by_normal(ob, top_mat, side_mat, bottom_mat):
    me = ob.data
    for m in (top_mat, side_mat, bottom_mat):
        me.materials.append(m)
    for p in me.polygons:
        p.material_index = 0 if p.normal.z > 0.99 else 2 if p.normal.z < -0.99 else 1


def uv_planar(ob, region):
    """Map each vertex's (x, y) linearly onto an atlas region (x0, y0, w, h in CSS px), y down."""
    x0, y0, w, h = region
    me = ob.data
    uv = me.uv_layers.new(name='UV')
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        px = x0 + (co.x - minx) / (maxx - minx) * w
        py = y0 + (maxy - co.y) / (maxy - miny) * h
        uv.data[loop.index].uv = (px * AS / ATLAS_SIZE[0], 1 - py * AS / ATLAS_SIZE[1])


# ---------------------------------------------------------------- materials
def mat_principled(name, color, metallic=0.0, rough=0.3, coat=0.0, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Specular IOR Level'].default_value = spec
    return m


def atlas_image():
    img = bpy.data.images.load(os.path.join(ATLAS, '0001.jpg'))
    img.source = 'SEQUENCE'
    img.colorspace_settings.name = 'sRGB'
    return img


def card_alpha(nt, bsdf):
    """Cards fade with the object's alpha; reflections see them fade much faster (op^8),
    so a half-faded card never shows its face through its underside in the display glass."""
    info = nt.nodes.new('ShaderNodeObjectInfo')
    lp = nt.nodes.new('ShaderNodeLightPath')
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 8
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'FLOAT'
    nt.links.new(info.outputs['Alpha'], pw.inputs[0])
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Factor'])
    nt.links.new(pw.outputs[0], mix.inputs['A'])
    nt.links.new(info.outputs['Alpha'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], bsdf.inputs['Alpha'])


def mat_screen(name, img, strength=1.0, fade=False):
    """Display glass: the UI as emission under a glossy cover glass. fade=True uses object alpha."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0, 0, 0, 1)
    b.inputs['Roughness'].default_value = 0.06
    b.inputs['Specular IOR Level'].default_value = 0.25
    b.inputs['Emission Strength'].default_value = strength
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Linear'
    tex.image_user.frame_duration = FRAMES
    tex.image_user.frame_start = 1
    tex.image_user.use_auto_refresh = True
    nt.links.new(tex.outputs['Color'], b.inputs['Emission Color'])
    if fade:
        card_alpha(nt, b)
    return m


img = atlas_image()
M = dict(
    titanium=mat_principled('Black Titanium', (0.075, 0.075, 0.08), metallic=1.0, rough=0.24),
    front_glass=mat_principled('Front Glass', (0.004, 0.004, 0.005), rough=0.05, spec=0.6),
    back_glass=mat_principled('Back Glass', (0.02, 0.02, 0.022), rough=0.35),
    button=mat_principled('Button', (0.09, 0.09, 0.095), metallic=1.0, rough=0.2),
    sapphire=mat_principled('Camera Control', (0.01, 0.01, 0.012), rough=0.08, spec=0.8),
    band=mat_principled('Antenna Band', (0.03, 0.03, 0.032), rough=0.5),
    hole=mat_principled('Port', (0.0, 0.0, 0.0), rough=0.9, spec=0.0),
    card_edge=mat_principled('Card Edge', (0.06, 0.06, 0.075), metallic=0.4, rough=0.12, coat=1.0),
    card_back=mat_principled('Card Back', (0.02, 0.02, 0.025), rough=0.4),
    screen=mat_screen('Display', img),
    back_screen=mat_screen('Back Display', img, strength=0.55),
    card_face=mat_screen('Card Face', img, fade=True),
)
for k in ('card_edge', 'card_back'):
    card_alpha(M[k].node_tree, M[k].node_tree.nodes['Principled BSDF'])


# ---------------------------------------------------------------- iPhone 16 Pro
def stadium_x(name, x, y_top, length, height, depth, mat, side):
    """A pill-shaped button on the left (side=-1) or right (side=+1) frame, measured in mm from the top."""
    yc = BH / 2 - (y_top + length / 2) / 10
    L, Hh = length / 10, height
    pts = [(p[0], p[1]) for p in rounded_rect(L, Hh, Hh / 2 - 1e-4, 12)]
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    inner = [bm.verts.new((x, yc + a, b)) for a, b in pts]
    outer = [bm.verts.new((x + side * depth, yc + a, b)) for a, b in pts]
    bm.faces.new(outer if side > 0 else list(reversed(outer)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        f = (inner[i], inner[j], outer[j], outer[i])
        bm.faces.new(f if side > 0 else tuple(reversed(f)))
    bm.normal_update()
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    return ob


def build_iphone(name, screen_mat, region):
    parts = []
    body = prism(name + ' Body', rounded_rect(BW, BH, BR, 32), -BT / 2, BT / 2, bevel=0.07)
    assign_by_normal(body, M['front_glass'], M['titanium'], M['back_glass'])
    parts.append(body)
    disp = prism(name + ' Display', rounded_rect(DW, DH, DR, 32), BT / 2 - 0.01, BT / 2 + 0.0015)
    disp.data.materials.append(screen_mat)
    disp.data.materials.append(M['front_glass'])
    for p in disp.data.polygons:
        p.material_index = 0 if p.normal.z > 0.99 else 1
    uv_planar(disp, region)
    parts.append(disp)
    zb = 0.0
    # left: Action button, volume up, volume down; right: side button, Camera Control
    parts.append(stadium_x(name + ' Action', -BW / 2 + 0.01, 26, 7.5, 0.26, 0.05, M['button'], -1))
    parts.append(stadium_x(name + ' Vol+', -BW / 2 + 0.01, 41, 11, 0.26, 0.05, M['button'], -1))
    parts.append(stadium_x(name + ' Vol-', -BW / 2 + 0.01, 56, 11, 0.26, 0.05, M['button'], -1))
    parts.append(stadium_x(name + ' Side', BW / 2 - 0.01, 44, 17, 0.26, 0.05, M['button'], 1))
    parts.append(stadium_x(name + ' CamCtl', BW / 2 - 0.01, 96, 11, 0.24, 0.012, M['sapphire'], 1))
    # antenna bands across the frame
    for sx in (-1, 1):
        for yy in (BH / 2 - 1.55, -BH / 2 + 1.55):
            band = prism(name + ' Band', [(-0.012, -0.36), (0.012, -0.36), (0.012, 0.36), (-0.012, 0.36)], 0, 0.002)
            band.rotation_euler = (0, math.radians(90 * sx), 0)
            band.location = (sx * (BW / 2 + 0.0005), yy, 0)
            band.data.materials.append(M['band'])
            parts.append(band)
    # bottom edge: USB-C port and speaker / mic holes
    port = prism(name + ' USB-C', rounded_rect(0.89, 0.26, 0.129, 10), 0, 0.004)
    port.rotation_euler = (math.radians(90), 0, 0)
    port.location = (0, -BH / 2 - 0.001, zb)
    port.data.materials.append(M['hole'])
    parts.append(port)
    for sx in (-1, 1):
        for i in range(6 if sx > 0 else 4):
            h = prism(name + ' Hole', rounded_rect(0.08, 0.08, 0.0399, 6), 0, 0.004)
            h.rotation_euler = (math.radians(90), 0, 0)
            h.location = (sx * (0.95 + i * 0.17), -BH / 2 - 0.001, zb)
            h.data.materials.append(M['hole'])
            parts.append(h)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for p in parts:
        p.parent = root
    return root




# ---------------------------------------------------------------- render setup
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
if os.environ.get('THREADS'):
    sc.render.threads_mode, sc.render.threads = 'FIXED', int(os.environ['THREADS'])
sc.cycles.samples = int(os.environ.get('SAMPLES', 12))
sc.cycles.adaptive_threshold = 0.03
sc.cycles.use_denoising = os.environ.get('DENOISE', '1') == '1'
sc.cycles.max_bounces, sc.cycles.glossy_bounces, sc.cycles.diffuse_bounces = 4, 2, 1
sc.cycles.transmission_bounces, sc.cycles.volume_bounces = 2, 0
sc.cycles.transparent_max_bounces = 16
sc.cycles.sample_clamp_direct, sc.cycles.sample_clamp_indirect = 6.0, 0.6
sc.cycles.denoising_prefilter = 'FAST'
sc.cycles.denoising_quality = os.environ.get('DQ', 'BALANCED')
sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = int(os.environ.get('PCT', 100))
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, FRAMES
sc.render.film_transparent = True
sc.render.use_persistent_data = True
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'

world = bpy.data.worlds.new('World')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.010, 0.009, 0.026, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
sc.world = world

# ---------------------------------------------------------------- camera that reproduces the CSS 3D view
# CSS: perspective 2300px, perspective-origin 50% 42%, the phone body 820px wide.
U = BW / 820                        # CSS px -> world units
D = 2300 * U
cam_data = bpy.data.cameras.new('Camera')
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.sensor_width = 36
cam_data.lens = 18 / (540 / 2300)
cam_data.shift_y = -(960 - 0.42 * 1920) / 1920
cam_data.clip_start, cam_data.clip_end = 0.1, 200
cam = bpy.data.objects.new('Camera', cam_data)
cam.location = (0, (960 - 0.42 * 1920) * U, D)
sc.collection.objects.link(cam)
sc.camera = cam

# ---------------------------------------------------------------- lights
def area(name, loc, size, power, color=(1, 1, 1), shape='RECTANGLE', size_y=None):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.color, d.shape, d.size = power, color, shape, size
    if size_y:
        d.size_y = size_y
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
    sc.collection.objects.link(ob)
    ob.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob

area('Key', (-14, 16, 18), 10, 9000, (0.85, 0.88, 1.0))
area('Rim', (16, -8, 6), 24, 6000, (0.75, 0.7, 1.0), shape='RECTANGLE', size_y=1.5)
area('Fill', (2, -18, 10), 14, 2500, (0.55, 0.5, 1.0))

# soft sheen card that only the glass sees, drifting slowly across the display
sheen_me = bpy.data.meshes.new('Sheen')
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1)
bm.to_mesh(sheen_me); bm.free()
sheen = bpy.data.objects.new('Sheen', sheen_me)
sc.collection.objects.link(sheen)
sm = bpy.data.materials.new('Sheen')
sm.use_nodes = True
nt = sm.node_tree
nt.nodes.remove(nt.nodes['Principled BSDF'])
em = nt.nodes.new('ShaderNodeEmission')
em.inputs['Color'].default_value = (0.75, 0.75, 1.0, 1)
em.inputs['Strength'].default_value = 0.35
nt.links.new(em.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
sheen_me.materials.append(sm)
sheen.scale = (4, 30, 1)
sheen.visible_camera = sheen.visible_diffuse = sheen.visible_shadow = sheen.visible_transmission = False

# ---------------------------------------------------------------- objects
def empty(name, parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent
    e.rotation_mode = 'ZYX'
    return e

rig, rig_back = empty('Rig'), empty('RigBack')
front = build_iphone('iPhone', M['screen'], (0, 0, *SCREEN_PX))
front.parent = rig
back = build_iphone('iPhone Back', M['back_screen'], (ATLAS_BACK_X, 0, *SCREEN_PX))
back.parent = rig_back

cards = []
for i in range(len(STATE['cards'][0])):
    c = prism(f'Card {i}', rounded_rect(CARD_W * K, CARD_H * K, CARD_R * K, 16), -0.025, 0.025, bevel=0.012, bevel_segments=3)
    assign_by_normal(c, M['card_face'], M['card_edge'], M['card_back'])
    uv_planar(c, (ATLAS_CARD_X, i * ATLAS_CARD_STEP, CARD_W, CARD_H))
    c.parent = front
    cards.append(c)


def lerp(a, b, k):
    return a + (b - a) * k


def ease(x):
    x = min(1, max(0, x))
    return -(math.cos(math.pi * x) - 1) / 2


def set_frame(f):
    """Same camera move as the CSS version: one slow, continuous glide."""
    t = (f - 1) / FPS
    k = ease(t / DUR)
    rz, rx, ry = lerp(-35, -30.5, k), lerp(46, 42.5, k), lerp(-7.5, -4.5, k)
    tx, ty, s = lerp(120, 60, k), lerp(-235, -280, k), lerp(0.93, 1.01, k)
    rig.location = (tx * U, -ty * U, 0)
    rig.rotation_euler = (math.radians(-rx), math.radians(ry), math.radians(-rz))
    rig.scale = (s, s, s)
    rig_back.location = (lerp(-480, -520, k) * U, -lerp(230, 180, k) * U, -520 * U)
    rig_back.rotation_euler = (math.radians(-(rx - 2)), math.radians(ry), math.radians(-(rz + 1)))
    rig_back.scale = (s, s, s)
    sheen.location = (lerp(-14, 10, t / DUR), 4, 22)
    sheen.rotation_euler = (math.radians(-20), 0, math.radians(-25))
    for c, st in zip(cards, STATE['cards'][f - 1]):
        c.location = ((24 + CARD_W / 2 - SCREEN_PX[0] / 2) * K,
                      (SCREEN_PX[1] / 2 - (st['y'] + CARD_H / 2)) * K,
                      BT / 2 + 0.03 + st['z'] * K)
        c.scale = (st['sc'], st['sc'], 1)
        c.color = (1, 1, 1, max(0.0, min(1.0, st['op'])))
        c.hide_render = st['op'] < 0.003


def keyframe_all():
    for f in range(1, FRAMES + 1):
        set_frame(f)
        for ob in (rig, rig_back, sheen):
            ob.keyframe_insert('location', frame=f)
            ob.keyframe_insert('rotation_euler', frame=f)
            ob.keyframe_insert('scale', frame=f)
        for c in cards:
            c.keyframe_insert('location', frame=f)
            c.keyframe_insert('scale', frame=f)
            c.keyframe_insert('color', frame=f)
            c.keyframe_insert('hide_render', frame=f)


keyframe_all()

mode = sys.argv[1] if len(sys.argv) > 1 else 'still'
dst = os.path.join(OUT, 'blender' if mode == 'render' else 'blender_stills')
os.makedirs(dst, exist_ok=True)
if mode == 'save':
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'iphone_scene.blend'))
elif mode == 'still':
    for f in [int(x) for x in sys.argv[2].split(',')]:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(dst, f'{f:04d}.png')
        import time; t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print('wrote', sc.render.filepath, round(time.time() - t0, 1), 's', flush=True)
else:
    a, b = int(sys.argv[2]), int(sys.argv[3])
    for f in range(a, b + 1):
        out = os.path.join(dst, f'{f:04d}.png')
        if os.path.exists(out):
            continue
        sc.frame_set(f)
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print('frame', f, flush=True)
