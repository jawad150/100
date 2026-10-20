"""Shared Blender (bpy) kit for the Floret films: the modelled iPhone 16 Pro, the floating quote cards,
materials fed by the UI atlas (ui_atlas.html, one JPEG per frame), lights and the render loop.

    import phone_kit as kit
    kit.init()                                   # fresh scene, render settings, materials, lights
    phone = kit.build_iphone('iPhone', kit.M['screen'], kit.SCREEN_REGION)
    cards = kit.make_cards(phone)
    kit.run(set_frame)                           # CLI: still <f,f,...> | render <a> <b>
"""
import json, math, os, sys, time
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', os.path.join(HERE, 'out'))
ATLAS = os.path.join(OUT, 'atlas')

# ---------------------------------------------------------------- dimensions (1 unit = 10 mm)
# iPhone 16 Pro: 71.5 x 149.6 x 8.25 mm; 6.3" display 1206 x 2622 px @ 460 ppi -> 66.6 x 144.8 mm
BW, BH, BT = 7.15, 14.96, 0.825
BR = 1.20
DW, DH = 6.66, 14.48
DR = BR - (BW - DW) / 2
SCREEN_PX = (776, 1688)
K = DW / SCREEN_PX[0]                       # atlas CSS px -> units on the display
ATLAS_SIZE, AS = (4050, 2550), 1.5
CARD_W, CARD_H, CARD_R = 1100, 166, 44
CARD_X, CARD_STEP_ATLAS, BACK_X = 820, 180, 1920
SCREEN_REGION = (0, 0, *SCREEN_PX)
BACK_REGION = (BACK_X, 0, *SCREEN_PX)

# quote list: rows lie in the screen, then pop out into evenly spaced floating cards (same size, tilt, left edge)
ROW_BOTTOM_0, ROW_STEP = 470, 240           # bottom edges of the rows (screen px), same flat and raised
FLAT = dict(left=14, scale=0.68, tilt=0.0, tilt_y=0.0, hinge=0.0)      # lying in the screen
RAISED = dict(left=-30, scale=0.90, tilt=27.0, tilt_y=6.0, hinge=40.0)  # floating

sc = M = img = None
FPS = FRAMES = None


# ---------------------------------------------------------------- easing
def lerp(a, b, k):
    return a + (b - a) * k


def clamp(x, a=0.0, b=1.0):
    return min(b, max(a, x))


def ease(x):
    x = clamp(x)
    return -(math.cos(math.pi * x) - 1) / 2


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x, p=3):
    return 1 - (1 - clamp(x)) ** p


def ease_out_back(x, overshoot=1.3):
    x = clamp(x)
    return 1 + (overshoot + 1) * (x - 1) ** 3 + overshoot * (x - 1) ** 2


# ---------------------------------------------------------------- geometry
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
        rim = [e for e in bm.edges if len(e.link_faces) == 2 and any(abs(f.normal.z) > 0.99 for f in e.link_faces)]
        bmesh.ops.bevel(bm, geom=rim, offset=bevel, segments=bevel_segments, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
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


def empty(name, parent=None, mode='YXZ'):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.parent = parent
    e.rotation_mode = mode          # YXZ: roll about the long axis, then tilt, then in-plane angle
    return e


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


def mat_screen(name, strength=1.0, fade=False, occlusion=False, tint=False):
    """Display / card face: the UI as emission under glossy cover glass.
    occlusion=True darkens the display under raised cards (ambient occlusion within 16 mm);
    tint=True multiplies the UI by the object's colour (used to dim cards out of focus)."""
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
    color = tex.outputs['Color']

    def multiply(a, b_):
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
        mul.inputs['Factor'].default_value = 1.0
        nt.links.new(a, mul.inputs['A'])
        nt.links.new(b_, mul.inputs['B'])
        return mul.outputs['Result']

    if occlusion:
        ao = nt.nodes.new('ShaderNodeAmbientOcclusion')
        ao.inputs['Distance'].default_value = 1.6
        ao.samples = 8
        shade = nt.nodes.new('ShaderNodeMapRange')
        shade.inputs['To Min'].default_value = 0.22
        nt.links.new(ao.outputs['AO'], shade.inputs['Value'])
        color = multiply(color, shade.outputs['Result'])
    if tint:
        color = multiply(color, nt.nodes.new('ShaderNodeObjectInfo').outputs['Color'])
    nt.links.new(color, b.inputs['Emission Color'])
    if fade:
        card_alpha(nt, b)
    return m


# ---------------------------------------------------------------- iPhone 16 Pro
def stadium_x(name, x, y_top, length, height, depth, mat, side):
    """A pill-shaped button on the left (side=-1) or right (side=+1) frame, positioned in mm from the top."""
    yc = BH / 2 - (y_top + length / 2) / 10
    pts = rounded_rect(length / 10, height, height / 2 - 1e-4, 12)
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
    sc.collection.objects.link(ob)
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
    # left: Action button, volume up, volume down; right: side button, Camera Control
    parts.append(stadium_x(name + ' Action', -BW / 2 + 0.01, 26, 7.5, 0.26, 0.05, M['button'], -1))
    parts.append(stadium_x(name + ' Vol+', -BW / 2 + 0.01, 41, 11, 0.26, 0.05, M['button'], -1))
    parts.append(stadium_x(name + ' Vol-', -BW / 2 + 0.01, 56, 11, 0.26, 0.05, M['button'], -1))
    parts.append(stadium_x(name + ' Side', BW / 2 - 0.01, 44, 17, 0.26, 0.05, M['button'], 1))
    parts.append(stadium_x(name + ' CamCtl', BW / 2 - 0.01, 96, 11, 0.24, 0.012, M['sapphire'], 1))
    for sx in (-1, 1):
        for yy in (BH / 2 - 1.55, -BH / 2 + 1.55):
            band = prism(name + ' Band', [(-0.012, -0.36), (0.012, -0.36), (0.012, 0.36), (-0.012, 0.36)], 0, 0.002)
            band.rotation_euler = (0, math.radians(90 * sx), 0)
            band.location = (sx * (BW / 2 + 0.0005), yy, 0)
            band.data.materials.append(M['band'])
            parts.append(band)
    port = prism(name + ' USB-C', rounded_rect(0.89, 0.26, 0.129, 10), 0, 0.004)
    port.rotation_euler = (math.radians(90), 0, 0)
    port.location = (0, -BH / 2 - 0.001, 0)
    port.data.materials.append(M['hole'])
    parts.append(port)
    for sx in (-1, 1):
        for i in range(6 if sx > 0 else 4):
            h = prism(name + ' Hole', rounded_rect(0.08, 0.08, 0.0399, 6), 0, 0.004)
            h.rotation_euler = (math.radians(90), 0, 0)
            h.location = (sx * (0.95 + i * 0.17), -BH / 2 - 0.001, 0)
            h.data.materials.append(M['hole'])
            parts.append(h)
    root = empty(name)
    for p in parts:
        p.parent = root
    return root


# ---------------------------------------------------------------- quote cards
def make_cards(phone, n=5):
    cards = []
    for i in range(n):
        c = prism(f'Card {i}', rounded_rect(CARD_W * K, CARD_H * K, CARD_R * K, 16), -0.03, 0.03, bevel=0.015, bevel_segments=3)
        assign_by_normal(c, M['card_face'], M['card_edge'], M['card_back'])
        uv_planar(c, (CARD_X, i * CARD_STEP_ATLAS, CARD_W, CARD_H))
        c.parent = phone
        cards.append(c)
    return cards


def pop_pose(i, t, start, stagger=0.2, duration=0.85):
    """Row i popping out of the screen: (left px, bottom-edge y px, hinge lift px, scale, tilt X, tilt Y)."""
    p = (t - start - stagger * i) / duration
    grow = ease_out(p)                          # size and position settle smoothly
    lift = ease_out_back(p)                     # lift and tilt overshoot a touch, then settle
    mix = lambda k, e: lerp(FLAT[k], RAISED[k], e)
    return (mix('left', grow), ROW_BOTTOM_0 + ROW_STEP * i, max(0.0, mix('hinge', lift)), mix('scale', grow),
            mix('tilt', lift), mix('tilt_y', lift))


def place_card(c, pose, opacity=1.0, tint=1.0):
    """Put a card (child of its phone) at a pose; it is hinged at its bottom edge and tilted up."""
    left, bottom, hinge, s, ax, ay = pose
    w, h = CARD_W * s, CARD_H * s
    a = math.radians(ax)
    cy = bottom - h / 2 * math.cos(a)
    cz = hinge + h / 2 * math.sin(a)
    c.location = ((left + w / 2 - SCREEN_PX[0] / 2) * K, (SCREEN_PX[1] / 2 - cy) * K, BT / 2 + 0.06 + cz * K)
    c.rotation_euler = (a, math.radians(ay), 0)
    c.scale = (s, s, 1)
    c.color = (tint, tint, tint, opacity)
    c.hide_render = opacity < 0.003


# ---------------------------------------------------------------- lights
def area(name, loc, size, power, color=(1, 1, 1), size_y=None, target=(0, 0, 0)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.color, d.size = power, color, size
    if size_y:
        d.shape, d.size_y = 'RECTANGLE', size_y
    ob = bpy.data.objects.new(name, d)
    ob.location = loc
    sc.collection.objects.link(ob)
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def reflector(name, loc, size, strength, target=(0, 0, 0)):
    """A soft light panel seen only in reflections (not by the camera, no direct light on diffuse)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    sc.collection.objects.link(ob)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    me.materials.append(m)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    ob.visible_camera = ob.visible_diffuse = ob.visible_shadow = ob.visible_transmission = False
    return ob


# ---------------------------------------------------------------- scene setup
def init():
    """Fresh scene with render settings, world, materials (fed by the atlas) and a camera."""
    global sc, M, img, FPS, FRAMES
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    meta = json.load(open(os.path.join(ATLAS, 'atlas.json')))
    FPS, FRAMES = meta['fps'], meta['frames']

    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    if os.environ.get('THREADS'):
        sc.render.threads_mode, sc.render.threads = 'FIXED', int(os.environ['THREADS'])
    sc.cycles.samples = int(os.environ.get('SAMPLES', 6))
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = os.environ.get('DENOISE', '1') == '1'
    sc.cycles.denoising_prefilter = 'FAST'
    sc.cycles.denoising_quality = os.environ.get('DQ', 'FAST')
    sc.cycles.max_bounces, sc.cycles.glossy_bounces, sc.cycles.diffuse_bounces = 4, 2, 1
    sc.cycles.transmission_bounces, sc.cycles.volume_bounces = 2, 0
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.sample_clamp_direct, sc.cycles.sample_clamp_indirect = 6.0, 0.6
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
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.03, 0.028, 0.06, 1)
    sc.world = world

    img = bpy.data.images.load(os.path.join(ATLAS, '0001.jpg'))
    img.source = 'SEQUENCE'
    M = dict(
        titanium=mat_principled('Natural Titanium', (0.80, 0.79, 0.77), metallic=1.0, rough=0.22),
        front_glass=mat_principled('Front Glass', (0.004, 0.004, 0.005), rough=0.05, spec=0.6),
        back_glass=mat_principled('Back Glass', (0.55, 0.54, 0.52), rough=0.45),
        button=mat_principled('Button', (0.75, 0.74, 0.72), metallic=1.0, rough=0.18),
        sapphire=mat_principled('Camera Control', (0.02, 0.02, 0.022), rough=0.08, spec=0.8),
        band=mat_principled('Antenna Band', (0.22, 0.22, 0.22), rough=0.5),
        hole=mat_principled('Port', (0.0, 0.0, 0.0), rough=0.9, spec=0.0),
        card_edge=mat_principled('Card Edge', (0.16, 0.16, 0.18), metallic=0.3, rough=0.35),
        card_back=mat_principled('Card Back', (0.02, 0.02, 0.025), rough=0.4),
        screen=mat_screen('Display', occlusion=True),
        back_screen=mat_screen('Back Display', strength=0.5),
        card_face=mat_screen('Card Face', fade=True, tint=True),
    )
    for k in ('card_edge', 'card_back'):
        card_alpha(M[k].node_tree, M[k].node_tree.nodes['Principled BSDF'])
    return sc


def camera(lens=85.0):
    cam_data = bpy.data.cameras.new('Camera')
    cam_data.sensor_fit = 'VERTICAL'
    cam_data.sensor_height = 36
    cam_data.lens = lens
    cam_data.clip_start, cam_data.clip_end = 0.05, 500
    cam = bpy.data.objects.new('Camera', cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def look_at(ob, eye, target, roll=0.0):
    """Place a camera at eye looking at target, rolled by `roll` degrees."""
    ob.location = Vector(eye)
    q = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y')
    ob.rotation_mode = 'QUATERNION'
    from mathutils import Quaternion
    ob.rotation_quaternion = q @ Quaternion((0, 0, 1), math.radians(roll))


# ---------------------------------------------------------------- CLI render loop
def run(set_frame):
    """still <f,f,...> -> $OUT/blender_stills, render <a> <b> -> $OUT/blender (skips frames already on disk)."""
    mode = sys.argv[1] if len(sys.argv) > 1 else 'still'
    if mode == 'save':
        set_frame(1)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'scene.blend'))
        return
    dst = os.path.join(OUT, 'blender' if mode == 'render' else 'blender_stills')
    os.makedirs(dst, exist_ok=True)
    frames = [int(x) for x in sys.argv[2].split(',')] if mode == 'still' else range(int(sys.argv[2]), int(sys.argv[3]) + 1)
    for f in frames:
        out = os.path.join(dst, f'{f:04d}.png')
        if mode == 'render' and os.path.exists(out):
            continue
        sc.frame_set(f)
        set_frame(f)
        sc.render.filepath = out
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print('frame', f, round(time.time() - t0, 1), 's', flush=True)
