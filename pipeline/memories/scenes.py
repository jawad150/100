"""Blender (Cycles) plates for the 'Yaadein' reel: orange/black cinematic environments with a posable
mannequin built from metaball capsules on a simple skeleton (backlit, reads as a human silhouette).

Usage: python3 scenes.py <scene> [<scene> ...]      scenes: room_stand room_sit memory burial road room_empty
Env:   RES (scale of 1080x1920, default 1.2 for camera push room), SAMPLES (default 48), PREVIEW=1 (fast)
"""
import os, sys, math, random
import bpy
from mathutils import Vector

W = os.environ.get('MEM_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                                                              'workspace2')))
OUT = W + '/plates'
ORANGE = (1.0, 0.42, 0.08)
EMBER = (1.0, 0.30, 0.04)


def reset(samples=48):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    k = float(os.environ.get('RES', '1.2'))
    if os.environ.get('PREVIEW'):
        k, samples = 0.35, 8
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = int(os.environ.get('SAMPLES', samples))
    sc.cycles.use_denoising = True
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.max_bounces = 4
    sc.cycles.volume_bounces = 1
    sc.cycles.volume_step_rate = 4.0
    sc.render.resolution_x, sc.render.resolution_y = int(1080 * k), int(1920 * k)
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - High Contrast'
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.003, 0.002, 0.002, 1)
    return sc


def mat(name, color, rough=0.5, metal=0.0, emission=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color + (1,) if len(color) == 3 else color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emission:
        b.inputs['Emission Color'].default_value = emission + (1,)
        b.inputs['Emission Strength'].default_value = estr
    return m


def emit_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = color + (1,)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def sky_mat(c_low, c_high, strength=1.0, z0=0.0, z1=1.0):
    """Emissive vertical gradient for a big backdrop plane (generated coords)."""
    m = bpy.data.materials.new('sky')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = z0
    mr.inputs['From Max'].default_value = z1
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = c_low + (1,)
    ramp.color_ramp.elements[1].color = c_high + (1,)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], e.inputs['Color'])
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def sky_plane(size, loc, mat_):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=(math.radians(90), 0, 0))
    p = bpy.context.object
    p.data.materials.append(mat_)
    p.visible_shadow = False
    p.visible_diffuse = False                  # light comes from the sun lamp, not the backdrop
    return p


def fog_box(size, loc, density, color=(1, 1, 1), anis=0.55):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    b = bpy.context.object
    b.scale = size
    m = bpy.data.materials.new('fog')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    v = nt.nodes.new('ShaderNodeVolumeScatter')
    v.inputs['Density'].default_value = density
    v.inputs['Anisotropy'].default_value = anis
    v.inputs['Color'].default_value = color + (1,)
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(v.outputs[0], o.inputs['Volume'])
    b.data.materials.append(m)
    b.visible_shadow = False
    return b


def camera(loc, target, lens=35, fstop=None, focus=None):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    c.data.sensor_width = 24
    bpy.context.scene.camera = c
    if fstop:
        c.data.dof.use_dof = True
        c.data.dof.aperture_fstop = fstop
        c.data.dof.focus_distance = focus or d.length
    return c

# ---------------------------------------------------------------- mannequin


def _lerp(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def pose(kind):
    """Joint positions (metres, z up, facing -y) for a few poses."""
    if kind == 'stand':
        J = dict(pelvis=(0, 0, 0.95), chest=(0, 0, 1.38), neck=(0, 0, 1.55), head=(0, 0, 1.70),
                 sh_l=(-0.19, 0, 1.45), sh_r=(0.19, 0, 1.45), el_l=(-0.23, 0.02, 1.17), el_r=(0.23, 0.02, 1.17),
                 wr_l=(-0.24, -0.02, 0.92), wr_r=(0.24, -0.02, 0.92), hip_l=(-0.1, 0, 0.92), hip_r=(0.1, 0, 0.92),
                 kn_l=(-0.11, -0.01, 0.50), kn_r=(0.11, -0.01, 0.50), an_l=(-0.11, 0.02, 0.08), an_r=(0.11, 0.02, 0.08),
                 to_l=(-0.11, -0.14, 0.03), to_r=(0.11, -0.14, 0.03))
    elif kind == 'walk':                                 # walking away from camera (camera behind, +y)
        J = dict(pelvis=(0, 0, 0.94), chest=(0, 0.02, 1.37), neck=(0, 0.02, 1.54), head=(0, 0.01, 1.69),
                 sh_l=(-0.19, 0.02, 1.44), sh_r=(0.19, 0.02, 1.44), el_l=(-0.22, 0.14, 1.18), el_r=(0.22, -0.12, 1.18),
                 wr_l=(-0.22, 0.20, 0.94), wr_r=(0.23, -0.20, 0.95), hip_l=(-0.1, 0, 0.91), hip_r=(0.1, 0, 0.91),
                 kn_l=(-0.11, -0.16, 0.53), kn_r=(0.11, 0.12, 0.51), an_l=(-0.11, -0.22, 0.10), an_r=(0.11, 0.30, 0.16),
                 to_l=(-0.11, -0.36, 0.03), to_r=(0.11, 0.24, 0.03))
    elif kind == 'sit':                                  # on the floor, knees up, arms on knees, head bowed
        J = dict(pelvis=(0, 0, 0.14), chest=(0, -0.10, 0.55), neck=(0, -0.16, 0.70), head=(0, -0.24, 0.80),
                 sh_l=(-0.19, -0.10, 0.62), sh_r=(0.19, -0.10, 0.62), el_l=(-0.22, -0.34, 0.50), el_r=(0.22, -0.34, 0.50),
                 wr_l=(-0.10, -0.50, 0.42), wr_r=(0.10, -0.50, 0.42), hip_l=(-0.1, 0, 0.12), hip_r=(0.1, 0, 0.12),
                 kn_l=(-0.13, -0.40, 0.48), kn_r=(0.13, -0.40, 0.48), an_l=(-0.12, -0.62, 0.08), an_r=(0.12, -0.62, 0.08),
                 to_l=(-0.12, -0.76, 0.03), to_r=(0.12, -0.76, 0.03))
    elif kind == 'kneel':                                # one knee down, leaning forward over the ground
        J = dict(pelvis=(0, 0, 0.52), chest=(0, -0.20, 0.88), neck=(0, -0.28, 1.02), head=(0, -0.36, 1.12),
                 sh_l=(-0.19, -0.22, 0.95), sh_r=(0.19, -0.22, 0.95), el_l=(-0.20, -0.42, 0.72), el_r=(0.20, -0.44, 0.70),
                 wr_l=(-0.12, -0.58, 0.48), wr_r=(0.12, -0.60, 0.46), hip_l=(-0.1, 0, 0.50), hip_r=(0.1, 0, 0.50),
                 kn_l=(-0.12, -0.42, 0.50), kn_r=(0.12, 0.16, 0.06), an_l=(-0.12, -0.40, 0.08), an_r=(0.12, 0.50, 0.06),
                 to_l=(-0.12, -0.54, 0.03), to_r=(0.12, 0.62, 0.03))
    elif kind == 'child':                                # small standing figure (memory scene)
        J = {k: v for k, v in pose('stand').items()}
    else:
        raise ValueError(kind)
    return J


def mannequin(kind, loc=(0, 0, 0), rot_z=0.0, scale=1.0, name='man', hand_up=None):
    J = pose(kind)
    if hand_up:                                          # raise one hand (e.g. holding a photo / a hand)
        side, target = hand_up
        J['el_' + side] = _lerp(J['sh_' + side], target, 0.5)
        J['wr_' + side] = target
    mb = bpy.data.metaballs.new(name)
    mb.resolution = 0.02
    mb.render_resolution = 0.012
    ob = bpy.data.objects.new(name, mb)
    bpy.context.collection.objects.link(ob)

    def cap(a, b, r):
        a, b = Vector(a), Vector(b)
        e = mb.elements.new()
        e.type = 'CAPSULE'
        e.co = (a + b) / 2
        d = b - a
        e.size_x = max(d.length / 2, 0.001)
        e.radius = r
        e.rotation = d.to_track_quat('X', 'Z')
        e.stiffness = 2.0

    def ball(c, r, sz=(1, 1, 1)):
        e = mb.elements.new()
        e.type = 'ELLIPSOID'
        e.co = Vector(c)
        e.radius = r
        e.size_x, e.size_y, e.size_z = sz
        e.stiffness = 2.0
    ball(J['head'], 0.16, (0.82, 0.92, 1.05))
    cap(J['neck'], J['head'], 0.08)
    cap(J['pelvis'], J['chest'], 0.22)
    ball(_lerp(J['chest'], J['neck'], 0.2), 0.26, (1.2, 0.72, 0.85))      # shoulders / jacket
    ball(_lerp(J['pelvis'], J['chest'], 0.35), 0.22, (1.0, 0.75, 1.0))
    for s in ('l', 'r'):
        cap(J['chest'], J['sh_' + s], 0.12)
        cap(J['sh_' + s], J['el_' + s], 0.095)
        cap(J['el_' + s], J['wr_' + s], 0.075)
        ball(J['wr_' + s], 0.07, (0.9, 0.7, 1.3))
        cap(J['pelvis'], J['hip_' + s], 0.15)
        cap(J['hip_' + s], J['kn_' + s], 0.125)
        cap(J['kn_' + s], J['an_' + s], 0.09)
        cap(J['an_' + s], J['to_' + s], 0.07)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    m = bpy.context.object
    m.name = name
    bpy.ops.object.shade_smooth()
    m.data.materials.append(mat('cloth', (0.012, 0.010, 0.010), rough=0.75))
    m.location = loc
    m.rotation_euler = (0, 0, rot_z)
    m.scale = (scale, scale, scale)
    return m


# ---------------------------------------------------------------- environments


def room(window_w=1.5, window_h=3.2):
    """Dark concrete room, one tall window in the back wall (y = 6), sun streaming in."""
    concrete = mat('concrete', (0.05, 0.045, 0.042), rough=0.85)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.context.object.data.materials.append(mat('floor', (0.03, 0.026, 0.024), rough=0.35))
    y = 6.0
    for (sx, sz, cx, cz) in ((9.0, 0.3, 0, 0.6), (9.0, 6.0, 0, 3.8 + window_h / 2 + 0.2),
                             ((18 - window_w) / 2, 12, -(window_w / 2 + (18 - window_w) / 4), 3),
                             ((18 - window_w) / 2, 12, (window_w / 2 + (18 - window_w) / 4), 3)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, y, cz))
        b = bpy.context.object
        b.scale = (sx, 0.4, sz)
        b.data.materials.append(concrete)
    # window bars
    for k in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(k * window_w / 6, y, 0.75 + window_h / 2))
        b = bpy.context.object
        b.scale = (0.05, 0.42, window_h)
        b.data.materials.append(concrete)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, 0.75 + window_h * 0.62))
    b = bpy.context.object
    b.scale = (window_w, 0.42, 0.05)
    b.data.materials.append(concrete)
    # side walls + ceiling (enclose the light)
    for x in (-5, 5):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 4))
        b = bpy.context.object
        b.scale = (0.3, 14, 8)
        b.data.materials.append(concrete)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 8))
    b = bpy.context.object
    b.scale = (10, 14, 0.3)
    b.data.materials.append(concrete)
    # outside: glowing sky + low sun
    sky_plane(30, (0, 14, 3), sky_mat((1.0, 0.38, 0.06), (0.45, 0.10, 0.02), 6.0))
    bpy.ops.object.light_add(type='SUN', location=(0, 20, 6))
    sun = bpy.context.object
    sun.data.energy = 18
    sun.data.color = ORANGE
    sun.data.angle = math.radians(1.2)
    sun.rotation_euler = (Vector((0, -1, -0.32))).to_track_quat('-Z', 'Y').to_euler()
    fog_box((9.6, 12, 7.6), (0, 0, 3.9), 0.06, (1.0, 0.85, 0.7))
    return sun


def dust_specks(n=0):
    pass


def scene_room(variant):
    reset(56)
    room()
    if variant == 'stand':
        mannequin('stand', loc=(0, 2.2, 0), rot_z=math.pi)          # facing the window, back to camera
        camera((0.6, -4.2, 1.0), (0, 3.0, 2.0), 30, 2.8, 6.4)
    elif variant == 'sit':
        mannequin('sit', loc=(0.3, 1.2, 0), rot_z=math.pi + 0.5, hand_up=('r', (0.05, -0.62, 0.55)))
        camera((-1.6, -2.6, 0.55), (0.2, 1.4, 0.8), 40, 2.2, 4.4)
    elif variant == 'empty':
        camera((0.6, -4.2, 1.0), (0, 3.0, 2.0), 30, 2.8, 6.4)
    elif variant == 'hero':                                         # hook: low wide, him small in the beam
        mannequin('stand', loc=(0, 2.6, 0), rot_z=math.pi)
        camera((0.0, -6.5, 0.35), (0, 3.0, 2.4), 24, 4.0, 9.0)
    return 'room_' + variant


def scene_memory():
    """Warm flashback: a father and child silhouetted against a huge sunset, golden haze."""
    reset(48)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    bpy.context.object.data.materials.append(mat('field', (0.035, 0.018, 0.008), rough=0.9))
    sky_plane(300, (0, 90, 40), sky_mat((1.0, 0.50, 0.12), (0.16, 0.04, 0.02), 1.3, 0.45, 0.70))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=7, location=(3, 85, 7))
    bpy.context.object.data.materials.append(emit_mat('sun', (1.0, 0.70, 0.36), 12))
    bpy.context.object.visible_shadow = False
    bpy.ops.object.light_add(type='SUN', location=(0, 20, 5))
    s = bpy.context.object
    s.data.energy = 5
    s.data.color = ORANGE
    s.rotation_euler = (Vector((0, -1, -0.12))).to_track_quat('-Z', 'Y').to_euler()
    mannequin('stand', loc=(-0.35, 4, 0), hand_up=('r', (0.30, 0.0, 0.86)))
    mannequin('child', loc=(0.35, 4, 0), scale=0.62, name='child', hand_up=('l', (-0.54, 0.0, 1.30)))
    fog_box((60, 120, 6), (0, 40, 3), 0.012, (1.0, 0.8, 0.6))
    camera((0.3, -6.5, 1.0), (0, 10, 1.5), 50, 2.2, 10.5)
    return 'memory'


def ground_dirt():
    m = bpy.data.materials.new('dirt')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.05, 0.03, 0.02, 1)
    b.inputs['Roughness'].default_value = 0.95
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 40
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def scene_burial():
    """Dawn: he kneels by a fresh mound, a wooden box of memories half buried, a shovel in the earth."""
    reset(56)
    dirt = ground_dirt()
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    bpy.context.object.data.materials.append(dirt)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0.55, -0.1, -0.55), segments=48, ring_count=24)
    mound = bpy.context.object
    mound.scale = (1.3, 0.9, 1.0)
    tex = bpy.data.textures.new('dn', 'CLOUDS')
    tex.noise_scale = 0.35
    d = mound.modifiers.new('d', 'DISPLACE')
    d.texture = tex
    d.strength = 0.12
    bpy.ops.object.shade_smooth()
    mound.data.materials.append(dirt)
    wood = mat('wood', (0.16, 0.07, 0.03), rough=0.7)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.55, -0.25, 0.42), rotation=(0.15, 0.1, 0.35))
    box = bpy.context.object
    box.scale = (0.55, 0.38, 0.32)
    bev = box.modifiers.new('b', 'BEVEL')
    bev.width = 0.02
    box.data.materials.append(wood)
    # shovel stuck in the ground
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=1.3, location=(1.55, 0.35, 0.75), rotation=(0.15, -0.22, 0))
    bpy.context.object.data.materials.append(wood)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(1.42, 0.25, 0.08), rotation=(0.15, -0.22, 0))
    blade = bpy.context.object
    blade.scale = (0.24, 0.02, 0.32)
    blade.data.materials.append(mat('steel', (0.2, 0.2, 0.21), rough=0.35, metal=1.0))
    mannequin('kneel', loc=(-0.45, 0.15, 0), rot_z=-1.25)
    sky_plane(400, (0, 120, 30), sky_mat((1.0, 0.42, 0.08), (0.03, 0.012, 0.01), 1.4, 0.44, 0.58))
    bpy.ops.object.light_add(type='SUN', location=(0, 20, 5))
    s = bpy.context.object
    s.data.energy = 6
    s.data.color = ORANGE
    s.rotation_euler = (Vector((0.3, -1, -0.10))).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.light_add(type='AREA', location=(-3, -3, 3))
    f = bpy.context.object
    f.data.energy = 60
    f.data.color = (0.5, 0.6, 0.8)
    f.data.size = 4
    f.rotation_euler = (Vector((3, 3, -3))).to_track_quat('-Z', 'Y').to_euler()
    fog_box((80, 200, 1.6), (0, 60, 0.8), 0.02, (1.0, 0.8, 0.65))
    camera((-1.2, -6.2, 1.1), (0.3, 0.4, 0.6), 38, 2.6, 6.6)
    return 'burial'


def scene_road():
    """Tomorrow: a long road to a huge rising sun, he walks away from camera."""
    reset(48)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    bpy.context.object.data.materials.append(mat('land', (0.02, 0.012, 0.008), rough=0.9))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 100, 0.005))
    r = bpy.context.object
    r.scale = (3.2, 200, 1)
    r.data.materials.append(mat('asphalt', (0.03, 0.028, 0.027), rough=0.4))
    for k in range(60):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2 + k * 3.2, 0.01))
        dsh = bpy.context.object
        dsh.scale = (0.08, 1.4, 1)
        dsh.data.materials.append(mat('paint', (0.6, 0.55, 0.5), rough=0.6))
    sky_plane(600, (0, 260, 60), sky_mat((1.0, 0.46, 0.10), (0.05, 0.015, 0.01), 1.3, 0.42, 0.58))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=22, location=(0, 250, 14))
    bpy.context.object.data.materials.append(emit_mat('sun', (1.0, 0.70, 0.38), 10))
    bpy.context.object.visible_shadow = False
    bpy.ops.object.light_add(type='SUN', location=(0, 20, 5))
    s = bpy.context.object
    s.data.energy = 5
    s.data.color = ORANGE
    s.rotation_euler = (Vector((0, -1, -0.08))).to_track_quat('-Z', 'Y').to_euler()
    mannequin('walk', loc=(0.2, 11, 0), rot_z=math.pi)
    fog_box((80, 260, 8), (0, 120, 4), 0.005, (1.0, 0.85, 0.7))
    camera((0.0, -1.0, 1.25), (0, 30, 2.6), 35, 2.8, 8.0)
    return 'road'


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for a in sys.argv[1:]:
        if a.startswith('room_'):
            name = scene_room(a[5:])
        else:
            name = {'memory': scene_memory, 'burial': scene_burial, 'road': scene_road}[a]()
        sc = bpy.context.scene
        sc.render.filepath = f'{OUT}/{name}' + ('_preview' if os.environ.get('PREVIEW') else '') + '.png'
        bpy.ops.render.render(write_still=True)
        print('rendered', name, flush=True)
