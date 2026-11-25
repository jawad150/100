"""OF "Can I add a page?" - overhead 3D assets, soft window light from the left (shadows fall right, as the brief asks):
an open book spread (blank ivory pages, plum cloth cover), a sky-blue knitted football scarf, a pen, a phone, a football.

Run: blender -b -P blender_page.py -- [draft] [names...] -> workspace_page/assets/<name>.png (RGBA, overhead)
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, box, cyl, sph, torus, hexc

ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_page/assets'
os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
DRAFT = 'draft' in argv
NAMES = [a for a in argv if a != 'draft']
PLUM, SKY, IVORY, CHAR = hexc('#5B174F'), hexc('#4E9BD6'), hexc('#FBF7F0'), hexc('#2B2B2B')


def reset(res=(1000, 1000)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 32 if DRAFT else 160
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Base Contrast'
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.96, 0.95, 0.93, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.5
    # window light from the left, a little above: shadows fall to the right
    L = bpy.data.objects.new('key', bpy.data.lights.new('key', 'AREA'))
    L.data.energy, L.data.size = 2600, 6
    L.data.color = (1.0, 0.96, 0.9)
    L.location = (-9, 1.5, 7)
    L.rotation_euler = (Vector((0, 0, 0)) - L.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(L)
    F = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'AREA'))
    F.data.energy, F.data.size = 500, 8
    F.location = (6, -3, 8)
    F.rotation_euler = (Vector((0, 0, 0)) - F.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(F)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    act().is_shadow_catcher = True
    return sc


def top_camera(lo, hi, margin=1.08):
    sc = bpy.context.scene
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = 'ORTHO'
    w, h = (hi[0] - lo[0]) * margin, (hi[1] - lo[1]) * margin
    rx, ry = sc.render.resolution_x, sc.render.resolution_y
    cam.data.ortho_scale = max(w, h * rx / ry) if rx >= ry else max(h, w * ry / rx)
    cam.location = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 20)
    cam.rotation_euler = (0, 0, 0)


def render(name):
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


def bounds():
    bpy.context.view_layer.update()
    pts = []
    for o in bpy.context.scene.objects:
        if o.type in ('MESH', 'CURVE', 'FONT') and not o.is_shadow_catcher:
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return lo, hi


def paper_mat():
    m = mat(IVORY, 0.85, coat=0.0)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Subsurface Weight'].default_value = 0.05
    nt = m.node_tree
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 400
    bm_ = nt.nodes.new('ShaderNodeBump')
    bm_.inputs['Strength'].default_value = 0.04
    nt.links.new(nz.outputs['Fac'], bm_.inputs['Height'])
    nt.links.new(bm_.outputs['Normal'], b.inputs['Normal'])
    return m


# ------------------------------------------------------------------ book: spread of 2 x (4 x 5.6), spine along y at x = 0
PW, PH = 4.0, 5.6


def page_surface(side, lift=0.0, name='page'):
    """One page as a gently curved sheet rising from the spine; side -1 = left, +1 = right."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=80, y_subdivisions=8, size=1)
    o = act()
    o.name = name
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        u, w = v.co.x + 0.5, v.co.y + 0.5
        x = side * u * PW
        z = 0.32 + 0.42 * (1 - math.exp(-u / 0.09)) - 0.06 * u + lift
        v.co = Vector((x, (w - 0.5) * PH, z))
    bm.to_mesh(o.data)
    bm.free()
    bpy.ops.object.shade_smooth()
    return setm(o, paper_mat())


def book():
    cover = mat(PLUM, 0.75, coat=0.05)
    box((2 * PW + 0.36, PH + 0.36, 0.14), loc=(0, 0, 0.07), m=cover, bw=0.05)
    edge = mat(hexc('#EFE8DC'), 0.9, coat=0.0)
    for side in (-1, 1):                                       # page block (stacked edges show at the outside)
        box((PW - 0.05, PH - 0.05, 0.5), loc=(side * (PW / 2 + 0.02), 0, 0.38), m=edge, bw=0.03)
        page_surface(side, name=f'page{side}')
    cyl(0.04, PH + 0.3, loc=(0, 0, 0.25), m=cover, rot=(math.radians(90), 0, 0))
    # a ribbon marker
    rb = mat(hexc('#B7006E'), 0.4, coat=0.2)
    box((0.12, 1.6, 0.01), loc=(0.35, -PH / 2 - 0.55, 0.16), m=rb, bw=0.0)


def scarf():
    """Knitted bar scarf: sky blue with white bars, ribbed, a soft wave, fringed ends."""
    L_, Wd = 7.0, 1.0
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=220, y_subdivisions=24, size=1)
    o = act()
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        u, w = v.co.x + 0.5, v.co.y + 0.5
        x = (u - 0.5) * L_
        y = (w - 0.5) * Wd + 0.35 * math.sin(u * math.pi * 1.6)
        z = 0.12 + 0.07 * math.sin(u * math.pi * 5.0) ** 2 + 0.03 * math.cos((w - 0.5) * math.pi)
        v.co = Vector((x, y, z))
    bm.to_mesh(o.data)
    bm.free()
    sol = o.modifiers.new('s', 'SOLIDIFY')
    sol.thickness = 0.1
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new('knit')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.95
    b.inputs['Sheen Weight'].default_value = 0.8
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    # bars: white stripes across the length
    mth = nt.nodes.new('ShaderNodeMath')
    mth.operation = 'SINE'
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 3.2
    nt.links.new(sep.outputs['X'], mul.inputs[0])
    nt.links.new(mul.outputs[0], mth.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = SKY
    ramp.color_ramp.elements[1].position = 0.86
    ramp.color_ramp.elements[1].color = (0.92, 0.93, 0.94, 1)
    mp = nt.nodes.new('ShaderNodeMapRange')
    mp.inputs['From Min'].default_value = -1
    nt.links.new(mth.outputs[0], mp.inputs['Value'])
    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    # knit ribs as bump (fine waves along the length)
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.wave_type = 'BANDS'
    wv.bands_direction = 'Y'
    wv.inputs['Scale'].default_value = 9.0
    wv.inputs['Distortion'].default_value = 1.5
    wv.inputs['Detail'].default_value = 4
    bm2 = nt.nodes.new('ShaderNodeBump')
    bm2.inputs['Strength'].default_value = 0.55
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    nt.links.new(wv.outputs['Fac'], bm2.inputs['Height'])
    nt.links.new(bm2.outputs['Normal'], b.inputs['Normal'])
    setm(o, m)
    fr = mat(SKY, 0.95, coat=0.0)
    for side in (-1, 1):                                      # fringe tassels at both ends
        xe = side * L_ / 2
        ye = 0.35 * math.sin((0.0 if side < 0 else 1.0) * math.pi * 1.6)
        for k in range(9):
            y = ye + (k / 8 - 0.5) * Wd * 0.92
            cyl(0.035, 0.45, loc=(xe + side * 0.22, y, 0.12), m=fr, rot=(0, math.radians(90), math.radians(side * (k - 4) * 2)), bw=0.0)


def pen():
    body = mat(PLUM, 0.25, coat=0.9)
    cyl(0.11, 2.6, loc=(0, 0, 0.12), m=body, rot=(0, math.radians(90), 0), bw=0.03)
    bpy.ops.mesh.primitive_cone_add(radius1=0.11, radius2=0.025, depth=0.45, location=(-1.52, 0, 0.12), rotation=(0, math.radians(-90), 0))
    setm(act(), mat(hexc('#C9C4BC'), 0.25, 0.9))
    sph(0.03, loc=(-1.76, 0, 0.12), m=mat(CHAR, 0.3))
    box((1.0, 0.05, 0.06), loc=(0.6, 0.12, 0.24), m=mat(hexc('#C9C4BC'), 0.25, 0.9), bw=0.02)   # clip
    cyl(0.115, 0.2, loc=(1.32, 0, 0.12), m=mat(hexc('#3A3A3A'), 0.3), rot=(0, math.radians(90), 0), bw=0.03)


def phone():
    box((1.5, 3.0, 0.16), loc=(0, 0, 0.08), m=mat(hexc('#26232A'), 0.3, coat=0.8), bw=0.18)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.165))
    s = act()
    s.scale = (1.36, 2.84, 1)
    m = mat(hexc('#101014'), 0.08, coat=1.0, emit=(hexc('#6CABDD'), 0.35))
    setm(s, m)
    box((0.4, 0.06, 0.02), loc=(0, 1.3, 0.17), m=mat(hexc('#000000'), 0.4), bw=0.01)


def football():
    ball = sph(1.0, loc=(0, 0, 1.0), m=mat(hexc('#F7F7F5'), 0.35, coat=0.4))
    dark = mat(hexc('#1F1F22'), 0.35, coat=0.4)
    # pentagon patches: icosahedron vertex directions
    phi = (1 + 5 ** 0.5) / 2
    vs = [(-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0), (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
          (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)]
    for v in vs:
        d = Vector(v).normalized()
        bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.34, depth=0.02, location=Vector((0, 0, 1.0)) + d * 1.05)
        o = act()
        o.rotation_mode = 'QUATERNION'
        o.rotation_quaternion = d.to_track_quat('Z', 'Y')
        sub = o.modifiers.new('sub', 'SUBSURF')
        sub.levels = sub.render_levels = 3
        sw = o.modifiers.new('w', 'SHRINKWRAP')
        sw.target, sw.offset = ball, 0.004
        bpy.ops.object.shade_smooth()
        setm(o, dark)


JOBS = {'book': ((2600, 1900), book), 'scarf': ((1600, 800), scarf), 'pen': ((1000, 400), pen), 'phone': ((600, 1000), phone),
        'football': ((700, 700), football)}
for name, (res, fn) in JOBS.items():
    if NAMES and name not in NAMES:
        continue
    reset(res)
    fn()
    lo, hi = bounds()
    top_camera(lo, hi, 1.1)
    render(name)
