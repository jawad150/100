"""Realistic building blocks for the Yaadein Blender plates: HDRI worlds, PBR materials from the
Poly Haven downloads, glTF props, a procedural night skyline, rain-wet surfaces and volumetric haze."""
import math
import os
import random

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace2'))
PH = ROOT + '/assets/ph'
RED = (1.0, 0.035, 0.03)
BLUE = (0.05, 0.22, 1.0)
CYAN = (0.25, 0.55, 1.0)


def reset(samples=64, res=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
    except Exception:
        pass
    sc = bpy.context.scene
    k = float(os.environ.get('RES', res or 1.3334))
    if os.environ.get('PREVIEW'):
        k, samples = 0.4, 12
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = int(os.environ.get('SAMPLES', samples))
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 6
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.volume_bounces = 1
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = int(1080 * k) // 2 * 2, int(1920 * k) // 2 * 2
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '16'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.threads_mode = 'AUTO'
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.002, 0.003, 0.006, 1)
    sc.view_layers[0].use_pass_z = True
    sc.view_layers[0].use_pass_mist = True
    random.seed(7)
    return sc


def world_hdri(name, strength=1.0, rot_z=0.0, tint=(1, 1, 1), bg_strength=None, bg_tint=None):
    """HDRI lighting; the camera can see a separately tinted/scaled version (bg_strength)."""
    w = bpy.context.scene.world
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(rot_z))
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(f'{PH}/hdri/{name}.hdr', check_existing=True)
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])

    def tinted(t, s):
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1.0
        nt.links.new(env.outputs['Color'], mix.inputs['A'])
        mix.inputs['B'].default_value = (*t, 1)
        bg = nt.nodes.new('ShaderNodeBackground')
        bg.inputs['Strength'].default_value = s
        nt.links.new(mix.outputs['Result'], bg.inputs['Color'])
        return bg
    light = tinted(tint, strength)
    cam = tinted(bg_tint or tint, strength if bg_strength is None else bg_strength)
    lp = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    nt.links.new(light.outputs[0], mix.inputs[1])
    nt.links.new(cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return w


def pbr(name, tex, scale=1.0, rough_mul=1.0, tint=(1, 1, 1), wet=0.0, bump=0.6, coords='Object', disp_scale=0.0):
    """PBR material from workspace2/assets/ph/tex/<tex>; wet>0 adds glossy puddles from a noise mask."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / scale,) * 3
    nt.links.new(tc.outputs[coords], mp.inputs['Vector'])
    d = f'{PH}/tex/{tex}/'

    def img(fn, non_color=True):
        p = d + fn
        if not os.path.exists(p):
            return None
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(p, check_existing=True)
        if non_color:
            t.image.colorspace_settings.name = 'Non-Color'
        t.projection = 'BOX'
        t.projection_blend = 0.25
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t
    dif = img('Diffuse.jpg', False)
    if dif:
        mul = nt.nodes.new('ShaderNodeMix')
        mul.data_type = 'RGBA'
        mul.blend_type = 'MULTIPLY'
        mul.inputs['Factor'].default_value = 1.0
        mul.inputs['B'].default_value = (*tint, 1)
        nt.links.new(dif.outputs['Color'], mul.inputs['A'])
        col = mul.outputs['Result']
    rough = img('Rough.jpg')
    rsock = None
    if rough:
        mr = nt.nodes.new('ShaderNodeMath')
        mr.operation = 'MULTIPLY'
        mr.inputs[1].default_value = rough_mul
        nt.links.new(rough.outputs['Color'], mr.inputs[0])
        rsock = mr.outputs[0]
    nor = img('nor_gl.jpg')
    if nor:
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = bump
        nt.links.new(nor.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if wet > 0:
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 0.35
        nz.inputs['Detail'].default_value = 6
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeMapRange')
        ramp.inputs['From Min'].default_value = 0.5 - 0.08 * wet
        ramp.inputs['From Max'].default_value = 0.5 + 0.02
        nt.links.new(nz.outputs['Fac'], ramp.inputs['Value'])
        puddle = ramp.outputs['Result']                     # 0 = puddle, 1 = dry
        if rsock is not None:
            mx = nt.nodes.new('ShaderNodeMath')
            mx.operation = 'MULTIPLY'
            nt.links.new(rsock, mx.inputs[0])
            nt.links.new(puddle, mx.inputs[1])
            mn = nt.nodes.new('ShaderNodeMath')
            mn.operation = 'MAXIMUM'
            mn.inputs[1].default_value = 0.035
            nt.links.new(mx.outputs[0], mn.inputs[0])
            rsock = mn.outputs[0]
        if dif:                                             # wet surfaces darken
            dk = nt.nodes.new('ShaderNodeMix')
            dk.data_type = 'RGBA'
            dk.blend_type = 'MULTIPLY'
            inv = nt.nodes.new('ShaderNodeMapRange')
            inv.inputs['To Min'].default_value = 0.55
            inv.inputs['To Max'].default_value = 0.8
            nt.links.new(puddle, inv.inputs['Value'])
            nt.links.new(inv.outputs['Result'], dk.inputs['Factor'])
            nt.links.new(col, dk.inputs['A'])
            dk.inputs['B'].default_value = (0.25, 0.25, 0.25, 1)
            col = dk.outputs['Result']
    if dif:
        nt.links.new(col, b.inputs['Base Color'])
    if rsock is not None:
        nt.links.new(rsock, b.inputs['Roughness'])
    return m


def glass_mat(name='glass', rough=0.05):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    b.inputs['IOR'].default_value = 1.45
    return m


def emit(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color, 1)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def plain(name, color, rough=0.6, metal=0.0, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m


def box(size, loc, mat=None, name='box', rot_z=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, math.radians(rot_z)))
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new('bev', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    if mat:
        o.data.materials.append(mat)
    return o


def plane(size, loc, mat=None, rot=(0, 0, 0), name='plane'):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=tuple(math.radians(r) for r in rot))
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    if mat:
        o.data.materials.append(mat)
    return o


def prop(asset, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, name=None):
    """Import a Poly Haven glTF prop; returns a parent empty."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f'{PH}/model/{asset}/{asset}.gltf')
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name or asset, None)
    bpy.context.scene.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    root.location = loc
    root.rotation_euler = tuple(math.radians(r) for r in rot)
    root.scale = (scale,) * 3
    bpy.context.view_layer.update()
    return root


def fog(size, loc, density, color=(1, 1, 1), anis=0.4, emission=None, noise=0.0, name='fog'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    b = bpy.context.object
    b.name = name
    b.scale = size
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Color'].default_value = (*color, 1)
    v.inputs['Anisotropy'].default_value = anis
    if noise > 0:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 0.08
        nz.inputs['Detail'].default_value = 3
        nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.35
        mr.inputs['From Max'].default_value = 0.75
        mr.inputs['To Min'].default_value = density * (1 - noise)
        mr.inputs['To Max'].default_value = density * (1 + noise)
        nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
        nt.links.new(mr.outputs['Result'], v.inputs['Density'])
    else:
        v.inputs['Density'].default_value = density
    if emission:
        v.inputs['Emission Color'].default_value = (*emission[0], 1)
        v.inputs['Emission Strength'].default_value = emission[1]
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(v.outputs[0], o.inputs['Volume'])
    b.data.materials.append(m)
    b.visible_shadow = False
    return b


def area(loc, target, color, energy, size=1.0, size_y=None, name='area', spread=180):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA'))
    bpy.context.scene.collection.objects.link(l)
    l.location = loc
    l.data.color = color
    l.data.energy = energy
    l.data.spread = math.radians(spread)
    if size_y:
        l.data.shape = 'RECTANGLE'
        l.data.size, l.data.size_y = size, size_y
    else:
        l.data.size = size
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return l


def spot(loc, target, color, energy, angle=30, blend=0.4, radius=0.05, name='spot'):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SPOT'))
    bpy.context.scene.collection.objects.link(l)
    l.location = loc
    l.data.color = color
    l.data.energy = energy
    l.data.spot_size = math.radians(angle)
    l.data.spot_blend = blend
    l.data.shadow_soft_size = radius
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return l


def point(loc, color, energy, radius=0.05, name='pt'):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'POINT'))
    bpy.context.scene.collection.objects.link(l)
    l.location = loc
    l.data.color = color
    l.data.energy = energy
    l.data.shadow_soft_size = radius
    return l


def sun(rot, color, strength, angle=1.0, name='sun'):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN'))
    bpy.context.scene.collection.objects.link(l)
    l.rotation_euler = tuple(math.radians(r) for r in rot)
    l.data.color = color
    l.data.energy = strength
    l.data.angle = math.radians(angle)
    return l


def camera(loc, target, lens=35, fstop=None, focus=None, sensor=36, shift=(0, 0), roll=0.0):
    cd = bpy.data.cameras.new('cam')
    c = bpy.data.objects.new('cam', cd)
    bpy.context.scene.collection.objects.link(c)
    c.location = loc
    d = Vector(target) - Vector(loc)
    q = d.to_track_quat('-Z', 'Y')
    c.rotation_euler = q.to_euler()
    if roll:
        c.rotation_euler.rotate_axis('Z', math.radians(roll))
    cd.lens = lens
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = sensor * 1.0
    cd.sensor_width = sensor
    cd.shift_x, cd.shift_y = shift
    cd.clip_start, cd.clip_end = 0.05, 5000
    bpy.context.scene.camera = c
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 7
        cd.dof.aperture_ratio = 1.0
        cd.dof.focus_distance = focus or d.length
    bpy.context.scene.world.mist_settings.start = 0.5
    bpy.context.scene.world.mist_settings.depth = 80
    return c


def window_mat(name='bldg', lit=0.32, warm=0.5, strength=5.0, facade=(0.012, 0.013, 0.016), floor_h=3.4,
               win_w=2.6, seed=0):
    """Dark facade with a grid of randomly lit windows (object coordinates = metres)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*facade, 1)
    b.inputs['Roughness'].default_value = 0.35
    b.inputs['Metallic'].default_value = 0.2
    tc = nt.nodes.new('ShaderNodeTexCoord')
    oi = nt.nodes.new('ShaderNodeAttribute')
    oi.attribute_name = 'bid'
    # window grid: x/y along facade + z for floors. use brick texture on two projections
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    nt.links.new(sep.outputs['X'], add.inputs[0])
    nt.links.new(sep.outputs['Y'], add.inputs[1])
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(add.outputs[0], comb.inputs['X'])
    nt.links.new(sep.outputs['Z'], comb.inputs['Y'])
    # per-object offset so buildings differ
    off = nt.nodes.new('ShaderNodeVectorMath')
    off.operation = 'ADD'
    nt.links.new(comb.outputs[0], off.inputs[0])
    sc = nt.nodes.new('ShaderNodeVectorMath')
    sc.operation = 'SCALE'
    nt.links.new(oi.outputs['Fac'], sc.inputs['Scale'])
    sc.inputs[0].default_value = (137.0, 0, 0)
    nt.links.new(sc.outputs[0], off.inputs[1])
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.0
    br.squash = 1.0
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.55
    br.inputs['Mortar Smooth'].default_value = 0.05
    br.inputs['Bias'].default_value = 0.0
    br.inputs['Brick Width'].default_value = win_w
    br.inputs['Row Height'].default_value = floor_h
    br.inputs['Color1'].default_value = (0, 0, 0, 1)
    br.inputs['Color2'].default_value = (1, 1, 1, 1)
    br.inputs['Mortar'].default_value = (0, 0, 0, 1)
    nt.links.new(off.outputs[0], br.inputs['Vector'])
    # random per window -> lit?
    rgb2bw = nt.nodes.new('ShaderNodeRGBToBW')
    nt.links.new(br.outputs['Color'], rgb2bw.inputs[0])
    thr = nt.nodes.new('ShaderNodeMath')
    thr.operation = 'GREATER_THAN'
    thr.inputs[1].default_value = 1.0 - lit
    nt.links.new(rgb2bw.outputs[0], thr.inputs[0])
    inside = nt.nodes.new('ShaderNodeMath')
    inside.operation = 'SUBTRACT'
    inside.inputs[0].default_value = 1.0
    nt.links.new(br.outputs['Fac'], inside.inputs[1])
    lit_mask = nt.nodes.new('ShaderNodeMath')
    lit_mask.operation = 'MULTIPLY'
    nt.links.new(thr.outputs[0], lit_mask.inputs[0])
    nt.links.new(inside.outputs[0], lit_mask.inputs[1])
    # only on vertical faces
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sepn = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Normal'], sepn.inputs[0])
    vert = nt.nodes.new('ShaderNodeMath')
    vert.operation = 'LESS_THAN'
    vert.inputs[1].default_value = 0.5
    absn = nt.nodes.new('ShaderNodeMath')
    absn.operation = 'ABSOLUTE'
    nt.links.new(sepn.outputs['Z'], absn.inputs[0])
    nt.links.new(absn.outputs[0], vert.inputs[0])
    lm2 = nt.nodes.new('ShaderNodeMath')
    lm2.operation = 'MULTIPLY'
    nt.links.new(lit_mask.outputs[0], lm2.inputs[0])
    nt.links.new(vert.outputs[0], lm2.inputs[1])
    # window colour: warm / cool by brick value
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (1.0, 0.72, 0.45, 1)
    ramp.color_ramp.elements[1].color = (0.62, 0.78, 1.0, 1)
    ramp.color_ramp.elements[0].position = 1.0 - lit
    ramp.color_ramp.elements[1].position = 1.0 - lit * (1 - warm)
    nt.links.new(rgb2bw.outputs[0], ramp.inputs['Fac'])
    st = nt.nodes.new('ShaderNodeMath')
    st.operation = 'MULTIPLY'
    st.inputs[1].default_value = strength
    nt.links.new(lm2.outputs[0], st.inputs[0])
    nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color'])
    nt.links.new(st.outputs[0], b.inputs['Emission Strength'])
    return m


def skyline(region, street_z, seed=3, hmin=15, hmax=230, avoid=None, lit=0.3, strength=5.0,
            spacing=(34, 34), red_tops=True, name='city'):
    """Towers on a jittered grid in region=(x0,x1,y0,y1), built as ONE mesh (fast). avoid: area kept empty.
    Each tower gets a random 'bid' face attribute that shuffles its lit windows."""
    import bmesh
    rnd = random.Random(seed)
    bm = bmesh.new()
    bid = bm.faces.layers.float.new('bid')
    tops = []

    def add_box(cx, cy, z0, w_, d_, h, r):
        vs = [bm.verts.new((cx + sx * w_ / 2, cy + sy * d_ / 2, z0 + sz * h))
              for sz in (0, 1) for sy in (-1, 1) for sx in (-1, 1)]
        for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            face = bm.faces.new([vs[i] for i in f])
            face[bid] = r
    x0, x1, y0, y1 = region
    y = y0
    while y < y1:
        x = x0
        dy = spacing[1] * rnd.uniform(0.8, 1.3)
        while x < x1:
            dx = spacing[0] * rnd.uniform(0.8, 1.3)
            cx, cy = x + dx / 2, y + dy / 2
            x += dx
            if avoid and avoid[0] < cx < avoid[1] and avoid[2] < cy < avoid[3]:
                continue
            far = (cy - y0) / max(1, (y1 - y0))
            h = math.exp(rnd.uniform(math.log(hmin), math.log(hmax * (0.7 + 0.6 * far))))
            if rnd.random() < 0.06:
                h *= 1.6
            w_, d_ = dx * rnd.uniform(0.5, 0.82), dy * rnd.uniform(0.5, 0.82)
            r = rnd.random()
            add_box(cx, cy, street_z, w_, d_, h, r)
            if rnd.random() < 0.35:
                h2 = h * rnd.uniform(0.08, 0.25)
                add_box(cx, cy, street_z + h, w_ * 0.65, d_ * 0.65, h2, r)
                h += h2
            if red_tops and h > 70 and rnd.random() < 0.55:
                tops.append((cx, cy, street_z + h + 1.2))
        y += dy
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(window_mat(name + '_win', lit=lit, strength=strength))
    if tops:
        bm = bmesh.new()
        for p in tops:
            bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=4, radius=0.7,
                                      matrix=__import__('mathutils').Matrix.Translation(p))
        me2 = bpy.data.meshes.new(name + '_beacons')
        bm.to_mesh(me2)
        bm.free()
        b = bpy.data.objects.new(name + '_beacons', me2)
        bpy.context.scene.collection.objects.link(b)
        me2.materials.append(emit('beacon', RED, 80))
    return o


def neon_sign(size, loc, color, strength, rot_z=0.0, name='neon'):
    o = plane(size, loc, emit(name, color, strength), rot=(90, 0, rot_z), name=name)
    return o


def streets(region, street_z, color=(1.0, 0.25, 0.1), strength=2.0, pitch=34):
    """Glowing street grid far below (traffic + lamps) as thin emissive strips in one mesh."""
    import bmesh
    x0, x1, y0, y1 = region
    bm = bmesh.new()

    def quad(xa, xb, ya, yb):
        z = street_z + 0.2
        bm.faces.new([bm.verts.new(p) for p in ((xa, ya, z), (xb, ya, z), (xb, yb, z), (xa, yb, z))])
    for i in range(int((y1 - y0) / pitch)):
        yc = y0 + i * pitch + pitch / 2
        quad(x0, x1, yc - 1.5, yc + 1.5)
    for i in range(int((x1 - x0) / pitch)):
        xc = x0 + i * pitch + pitch / 2
        quad(xc - 1.5, xc + 1.5, y0, y1)
    me = bpy.data.meshes.new('streets')
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('streets', me)
    bpy.context.scene.collection.objects.link(o)
    me.materials.append(emit('streetglow', color, strength))
    return o


def render(path):
    sc = bpy.context.scene
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
