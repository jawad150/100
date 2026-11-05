"""Glossy 3D pop-up tokens for Hulk Marketing "Anything but ordinary" (transparent PNGs, Hulk green / black / off-white).

Usage: python3 blender_hulk.py <token> [...]
Tokens: cup, eye, phone, browser, magnifier, heart, target, badge, chatbot, bell, asterisk
"""
import bpy, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
from blender_lo import lin, reset, mat, camera, look
from blender_sol import std, studio

OUT = os.path.abspath(os.path.join(HERE, '..', 'workspace_hulk', 'tokens'))
GREEN, LIME, INK, PAPER, GREY = '#60D417', '#9DEF69', '#101215', '#F3F5F0', '#8E949A'


def setup(res=(640, 640), samples=48):
    reset(res, samples=samples, transparent=True)
    std()
    studio(world_col='#E6EEE0', strength=0.55, key=950, rim=900)


def gloss(name, hexcol, rough=0.2, coat=0.8, metal=0.0, emit=None, estr=0.0):
    return mat(name, lin(hexcol), rough=rough, coat=coat, metal=metal, emit=lin(emit) if emit else None, estr=estr)


def shot(name, cam_loc=(0, -8.0, 0.6), target=(0, 0, 0), lens=50):
    cam = camera(lens=lens)
    cam.data.dof.use_dof = False
    look(cam, cam_loc, target)
    os.makedirs(OUT, exist_ok=True)
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, flush=True)


def sphere(r, loc, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=48, ring_count=24)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m)
    return o


def cyl(r, d, loc, m, rot=(0, 0, 0), v=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def rbox(size, loc, m, bevel=0.1, rot=(0, 0, 0), seg=5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = seg
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def torus(R, r, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=96, minor_segments=24)
    o = bpy.context.object
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def text3d(body, size, loc, m, rot=(90, 0, 0), extrude=0.08):
    bpy.ops.object.text_add(location=loc, rotation=tuple(math.radians(a) for a in rot))
    t = bpy.context.object
    t.data.body = body
    t.data.font = bpy.data.fonts.load(os.path.abspath(os.path.join(HERE, '..', 'workspace_hulk', 'fonts', 'Headline-900.ttf')), check_existing=True)
    t.data.size = size
    t.data.extrude = extrude
    t.data.bevel_depth = 0.01
    t.data.align_x = 'CENTER'
    t.data.align_y = 'CENTER'
    t.data.materials.append(m)
    return t


def spin_all(deg, axis=2):
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE', 'FONT') and o.parent is None:
            o.rotation_euler[axis] += math.radians(deg)


def cup():
    setup()
    c = gloss('cup', PAPER, rough=0.25)
    bpy.ops.mesh.primitive_cone_add(radius1=0.75, radius2=0.95, depth=1.7, location=(0, 0, -0.1), vertices=64)
    bpy.context.object.data.materials.append(c); bpy.ops.object.shade_smooth()
    cyl(0.99, 0.28, (0, 0, 0.85), gloss('lid', INK, rough=0.3))
    cyl(0.6, 0.18, (0, 0, 1.05), gloss('lid', INK))
    bpy.ops.mesh.primitive_cone_add(radius1=0.84, radius2=0.9, depth=0.6, location=(0, 0, -0.05), vertices=64)
    sl = bpy.context.object; sl.scale = (1.03, 1.03, 1); sl.data.materials.append(gloss('sleeve', GREEN, rough=0.35))
    for k in range(3):
        sphere(0.22 - k * 0.04, (0.15 * math.sin(k * 2), -0.2, 1.6 + k * 0.42), gloss('steam', '#FFFFFF', rough=0.6, coat=0.0), (1, 0.6, 1))
    shot('cup', (0.5, -7.6, 1.6), (0, 0, 0.2))


def eye():
    setup()
    sphere(1.0, (0, 0, 0), gloss('white', PAPER, rough=0.15))
    sphere(0.48, (0, -0.72, 0), gloss('iris', GREEN, rough=0.15), (1, 0.5, 1))
    sphere(0.24, (0, -0.95, 0), gloss('pupil', INK, rough=0.1), (1, 0.4, 1))
    sphere(0.08, (0.12, -1.05, 0.14), gloss('glint', '#FFFFFF', rough=0.05), (1, 0.5, 1))
    lid = sphere(1.06, (0, 0, 0.0), gloss('lid', GREY, rough=0.35), (1, 1, 1))
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, -1.25))
    cut = bpy.context.object; cut.hide_render = True
    lid.modifiers['Boolean'].object = cut
    lid.rotation_euler = (math.radians(-28), 0, 0)
    spin_all(14)
    shot('eye', (0.3, -7.2, 0.5), (0, 0, 0))


def phone():
    setup((560, 720))
    rbox((1.7, 0.2, 3.3), (0, 0, 0), gloss('body', INK, rough=0.25), 0.22)
    rbox((1.5, 0.05, 3.05), (0, -0.11, 0), gloss('screen', GREEN, rough=0.15, emit=GREEN, estr=0.6), 0.16)
    torus(0.38, 0.07, (0, -0.16, 0.35), gloss('ring', INK))
    rbox((0.12, 0.05, 0.42), (0, -0.16, 0.35), gloss('ring', INK), 0.03, rot=(0, math.radians(45), 0))
    for i in range(3):
        rbox((0.9 - i * 0.2, 0.04, 0.1), (0, -0.16, -0.5 - i * 0.28), gloss('ln', PAPER), 0.04)
    spin_all(-18)
    shot('phone', (0.4, -8.6, 0.6), (0, 0, 0))


def browser():
    setup((760, 600))
    rbox((3.6, 0.18, 2.6), (0, 0, 0), gloss('win', PAPER, rough=0.25), 0.16)
    rbox((3.6, 0.2, 0.42), (0, -0.01, 1.1), gloss('bar', INK), 0.12)
    for i, col in enumerate(('#FF5F57', '#FEBC2E', GREEN)):
        cyl(0.08, 0.06, (-1.55 + i * 0.26, -0.13, 1.1), gloss(f'd{i}', col), rot=(math.radians(90), 0, 0))
    rbox((2.0, 0.06, 0.2), (0.35, -0.12, 1.1), gloss('url', '#2A2E33'), 0.08)
    rbox((3.2, 0.06, 1.0), (0, -0.11, 0.25), gloss('hero', GREEN, emit=GREEN, estr=0.3), 0.1)
    rbox((1.4, 0.05, 0.16), (-0.75, -0.15, 0.45), gloss('h1', INK), 0.06)
    rbox((1.0, 0.05, 0.12), (-0.95, -0.15, 0.15), gloss('h2', INK), 0.05)
    rbox((0.9, 0.07, 0.3), (-1.1, -0.13, -0.55), gloss('btn', INK), 0.12)
    for i in range(3):
        rbox((0.95, 0.06, 0.55), (-1.05 + i * 1.05, -0.11, -0.75 + 0.0), gloss('card', '#E3E7DF'), 0.08) if i else None
    rbox((0.3, 0.12, 0.3), (1.25, -0.2, -0.85), gloss('cursor', INK), 0.05, rot=(0, math.radians(30), 0))
    spin_all(-16)
    shot('browser', (0.6, -9.2, 1.2), (0, 0, 0))


def magnifier():
    setup()
    torus(0.95, 0.2, (-0.3, 0, 0.35), gloss('rim', GREEN), rot=(math.radians(90), 0, 0))
    glass = mat('glass', lin('#DFF7D0'), rough=0.02)
    glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 1.0
    cyl(0.92, 0.08, (-0.3, 0, 0.35), glass, rot=(math.radians(90), 0, 0))
    rbox((0.38, 0.38, 1.4), (0.92, 0, -0.87), gloss('handle', INK), 0.16, rot=(0, math.radians(-45), 0))
    t = text3d('#1', 0.95, (-0.3, -0.08, 0.3), gloss('one', INK), extrude=0.06)
    spin_all(-10)
    shot('magnifier', (0.4, -7.6, 0.8), (0, 0, 0))


def heart():
    setup()
    m = gloss('heart', GREEN)
    sphere(0.75, (-0.52, 0, 0.35), m)
    sphere(0.75, (0.52, 0, 0.35), m)
    bpy.ops.mesh.primitive_cone_add(radius1=1.05, radius2=0.0, depth=1.6, location=(0, 0, -0.6), rotation=(math.radians(180), 0, 0), vertices=64)
    bpy.context.object.data.materials.append(m); bpy.ops.object.shade_smooth()
    bpy.context.object.scale = (1.22, 0.62, 1)
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.data.materials and o.data.materials[0].name.startswith('heart'):
            o.scale.y *= 0.75
    sphere(0.16, (-0.65, -0.55, 0.65), gloss('hl', '#FFFFFF', rough=0.05), (1, 0.3, 0.7))
    spin_all(-14)
    shot('heart', (0.3, -7.0, 0.5), (0, 0, 0))


def target():
    setup()
    for i, (r, col) in enumerate(((1.4, PAPER), (1.08, GREEN), (0.76, PAPER), (0.44, GREEN))):
        cyl(r, 0.24 + i * 0.05, (0, -i * 0.025, 0), gloss(f't{i}', col), rot=(math.radians(90), 0, 0))
    rbox((0.09, 2.2, 0.09), (0.35, -1.0, 0.3), gloss('shaft', INK), 0.03, rot=(math.radians(10), 0, math.radians(-25)))
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0.0, depth=0.5, location=(0.8, -1.95, 0.48), rotation=(math.radians(80), 0, math.radians(-25)), vertices=4)
    bpy.context.object.data.materials.append(gloss('fl', LIME))
    spin_all(-20)
    shot('target', (1.2, -7.2, 1.0), (0, 0, 0))


def badge():
    setup()
    bpy.ops.mesh.primitive_cylinder_add(radius=1.25, depth=0.3, vertices=12, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    b = bpy.context.object; b.data.materials.append(gloss('badge', GREEN))
    bv = b.modifiers.new('bv', 'BEVEL'); bv.width = 0.06; bv.segments = 4
    cyl(0.98, 0.34, (0, -0.02, 0), gloss('in', INK), rot=(math.radians(90), 0, 0))
    for k in range(3):
        rbox((0.2, 0.12, 1.2), (0, -0.24, 0), gloss('star', LIME), 0.08, rot=(0, k * math.pi / 3, 0))
    for sx in (-1, 1):
        rbox((0.4, 0.12, 1.0), (sx * 0.45, 0.1, -1.3), gloss('rib', INK), 0.05, rot=(0, math.radians(sx * 18), 0))
    spin_all(-14)
    shot('badge', (0.4, -7.6, 0.4), (0, 0, -0.2))


def chatbot():
    setup()
    m = gloss('bub', PAPER)
    rbox((2.4, 0.5, 1.6), (0, 0, 0.2), m, 0.45, seg=8)
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0.0, depth=0.7, location=(-0.7, 0, -0.75), rotation=(math.radians(200), 0, 0), vertices=32)
    bpy.context.object.data.materials.append(m)
    for i in range(3):
        sphere(0.17, (-0.55 + i * 0.55, -0.28, 0.2), gloss('dot', GREEN, emit=GREEN, estr=0.4))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(1.25, 0.2, 1.25), segments=48, ring_count=24)
    moon = bpy.context.object; moon.data.materials.append(gloss('moon', LIME, emit=LIME, estr=0.3)); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(1.5, 0.0, 1.45))
    cut = bpy.context.object; cut.hide_render = True
    bo = moon.modifiers.new('b', 'BOOLEAN'); bo.object = cut
    spin_all(-12)
    shot('chatbot', (0.3, -7.6, 0.9), (0.2, 0, 0.3))


def bell():
    setup()
    m = gloss('bell', GREEN, metal=0.3, rough=0.2)
    bpy.ops.mesh.primitive_cone_add(radius1=1.1, radius2=0.45, depth=1.3, location=(0, 0, 0), vertices=64, end_fill_type='NOTHING')
    b = bpy.context.object; b.data.materials.append(m); bpy.ops.object.shade_smooth()
    sol = b.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.08
    sub = b.modifiers.new('sub', 'SUBSURF'); sub.levels = 2; sub.render_levels = 2
    sphere(0.48, (0, 0, 0.62), m, (1, 1, 0.6))
    torus(1.1, 0.1, (0, 0, -0.66), m)
    sphere(0.22, (0.1, -0.2, -0.8), gloss('clap', INK))
    torus(0.18, 0.05, (0, 0, 1.0), gloss('top', INK), rot=(math.radians(90), 0, 0))
    spin_all(-8, axis=1)
    shot('bell', (0.3, -7.4, 0.6), (0, 0, 0))


def asterisk():
    setup()
    m = gloss('ast', GREEN)
    for k in range(6):
        a = k * math.pi / 3
        rbox((0.36, 0.36, 2.5), (0, 0, 0), m, 0.16, rot=(0, a, 0))
    spin_all(18, axis=0)
    spin_all(-20)
    shot('asterisk', (0.4, -7.2, 0.5), (0, 0, 0))


ALL = dict(cup=cup, eye=eye, phone=phone, browser=browser, magnifier=magnifier, heart=heart, target=target, badge=badge,
           chatbot=chatbot, bell=bell, asterisk=asterisk)

if __name__ == '__main__':
    for n in (sys.argv[1:] or list(ALL)):
        ALL[n]()
