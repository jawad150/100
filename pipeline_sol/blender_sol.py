"""3D for IC London "Why do you want to be a solicitor?" (Blender Cycles), built from the IC London emblem.

The emblem is a stack of three pieces (navy spire, red block with a white circle, navy base). In the film they are the
three parts of a strong answer: the red target block = motivation, the navy base = experience (your foundation), the
navy spire = long-term goals (pointing up). They float apart, star in their own sections, then snap into the emblem.

Usage: python3 blender_sol.py <scene> [...]   (ONLY=a,b,c renders preview frames)
Scenes: pieces_float, emblem_build, piece_motiv (motiv_hero), piece_goal (goal_hero), foundation, qmark, bulb, cap
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_lo'))
import blender_lo as B
from blender_lo import lin, reset, mat, box, prism, camera, look, FPS

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_sol'))
B.OUT = S + '/assets'
FONT_B = S + '/fonts/Inter-900.ttf'
FONT_S = S + '/fonts/Inter-800.ttf'
FONT_SERIF = S + '/fonts/Cardo-700.ttf'
NAVY, RED, WHITE, GOLD = '#00247D', '#CF142B', '#F7F8FC', '#E3B24A'


def render_seq(name, n, update):
    only = os.environ.get('ONLY')
    if not only:
        return B.render_seq(name, n, update)
    d = f'{B.OUT}/preview2'
    os.makedirs(d, exist_ok=True)
    for i in [int(x) for x in only.split(',')]:
        update(i, n)
        bpy.context.scene.render.filepath = f'{d}/{name}_{i:03d}.png'
        bpy.ops.render.render(write_still=True)
        print('preview', name, i, flush=True)


def ease(k):
    k = min(1.0, max(0.0, k))
    return k * k * (3 - 2 * k)


def out_back(k, s=1.6):
    k = min(1.0, max(0.0, k)) - 1
    return 1 + (s + 1) * k ** 3 + s * k ** 2


def lerp(a, b, k):
    return a + (b - a) * k


def studio(world_col='#1B2A55', strength=0.35, key=750, rim=1100):
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = lin(world_col)
    bg.inputs['Strength'].default_value = strength
    for loc, rot, size, e, col in [((-5, -7, 7), (55, 0, -35), 7, key, (1.0, 0.96, 0.92)),
                                    ((6, 3, 4), (75, 0, 120), 5, rim, (0.75, 0.82, 1.0)),
                                    ((2, -6, -1), (100, 0, 20), 4, key * 0.25, (1.0, 0.9, 0.9))]:
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=tuple(math.radians(a) for a in rot))
        l = bpy.context.object
        l.data.size, l.data.energy, l.data.color = size, e, col


def catcher(z=0.0, size=60):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    bpy.context.object.is_shadow_catcher = True


def text_obj(body, size, loc, rot, m, font=FONT_B, extrude=0.0, align='CENTER', bevel=0.0):
    bpy.ops.object.text_add(location=loc, rotation=tuple(math.radians(a) for a in rot))
    t = bpy.context.object
    t.data.body = body
    t.data.font = bpy.data.fonts.load(font, check_existing=True)
    t.data.size = size
    t.data.extrude = extrude
    t.data.bevel_depth = bevel
    t.data.bevel_resolution = 3
    t.data.align_x = align
    t.data.align_y = 'CENTER'
    t.data.materials.append(m)
    return t


# ------------------------------------------------------------------ emblem pieces (proportions measured from the logo)
EW, ED = 2.0, 0.62                 # emblem width, depth
BASE_H, BLOCK_H, SPIRE_H, GAP = 2.06, 2.08, 1.84, 0.2


def emblem_mats():
    return (mat('navy', lin(NAVY), rough=0.3, coat=0.35), mat('red', lin(RED), rough=0.3, coat=0.4),
            mat('white', lin(WHITE), rough=0.25, coat=0.3))


def make_base(navy):
    root = bpy.data.objects.new('base', None)
    bpy.context.scene.collection.objects.link(root)
    b = box((EW, ED, BASE_H), (0, 0, 0), navy, bevel=0.05)
    b.parent = root
    return root


def make_block(red, white):
    root = bpy.data.objects.new('block', None)
    bpy.context.scene.collection.objects.link(root)
    b = box((EW, ED, BLOCK_H), (0, 0, 0), red, bevel=0.05)
    b.parent = root
    for y in (-ED / 2 - 0.012, ED / 2 + 0.012):          # white circle inlaid on both faces
        bpy.ops.mesh.primitive_cylinder_add(radius=0.67, depth=0.05, location=(0, y, 0),
                                            rotation=(math.radians(90), 0, 0), vertices=96)
        c = bpy.context.object
        bv = c.modifiers.new('bv', 'BEVEL')
        bv.width, bv.segments = 0.015, 3
        bpy.ops.object.shade_smooth()
        c.data.materials.append(white)
        c.parent = root
    return root


def make_spire(navy):
    root = bpy.data.objects.new('spire', None)
    bpy.context.scene.collection.objects.link(root)
    p = prism(EW, ED, SPIRE_H, (0, 0, -SPIRE_H / 2), navy)
    bv = p.modifiers.new('bv', 'BEVEL')
    bv.width, bv.segments = 0.04, 3
    p.parent = root
    return root


def assembled_z():
    zb = BASE_H / 2
    zr = BASE_H + GAP + BLOCK_H / 2
    zs = BASE_H + GAP + BLOCK_H + GAP + SPIRE_H / 2
    return zb, zr, zs


def std():
    v = bpy.context.scene.view_settings
    v.view_transform = 'Standard'
    v.look = 'None'


def emblem_scene(res):
    reset(res, samples=14, transparent=True)
    std()
    studio()
    catcher(-0.02)
    navy, red, white = emblem_mats()
    return make_base(navy), make_block(red, white), make_spire(navy)


def pieces_float():
    base, block, spire = emblem_scene((720, 1280))
    zb, zr, zs = assembled_z()
    spread = [(base, zb, 0.0), (block, zr, 0.9), (spire, zs, 1.85)]
    cam = camera(lens=50)
    cam.data.dof.use_dof = False

    def upd(i, n):
        t = i / FPS
        look(cam, (0.6, -18.5, 4.6), (0, 0, zr + 0.7))
        for j, (o, z0, dz) in enumerate(spread):
            k = out_back((i - 4 - 7 * j) / 16.0, 1.3)
            fly = [(-9, 0, -4), (9, 0, 0), (0, 0, 9)][j]
            z = z0 + dz + 0.08 * math.sin(t * 2.2 + j * 1.7)
            o.location = (lerp(fly[0], 0, k), lerp(fly[1], 0, k), lerp(z + fly[2], z, k))
            o.rotation_euler = (math.radians(6 * math.sin(t * 1.5 + j)), 0,
                                math.radians(lerp(160 * (1 if j % 2 else -1), 0, k) + 14 * math.sin(t * 1.3 + j * 2)))
    render_seq('pieces_float', 60, upd)


def emblem_build():
    base, block, spire = emblem_scene((720, 1280))
    zb, zr, zs = assembled_z()
    spread = [(base, zb, 0.0), (block, zr, 0.9), (spire, zs, 1.85)]
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    t_end = 60 / FPS

    def upd(i, n):
        t = (60 + i) / FPS                     # continue the float's phase from pieces_float's last frame
        look(cam, (lerp(0.6, 0.0, ease(i / 40)), lerp(-18.5, -15.5, ease(i / 50)), lerp(4.6, 3.8, ease(i / 50))),
             (0, 0, lerp(zr + 0.7, zr + 0.3, ease(i / 50))))
        for j, (o, z0, dz) in enumerate(spread):
            k = ease((i - 6 - 9 * j) / 14.0)
            snap = out_back((i - 6 - 9 * j) / 14.0, 2.2)
            z_float = z0 + dz + 0.08 * math.sin(t * 2.2 + j * 1.7)
            o.location = (0, 0, lerp(z_float, z0, snap))
            ry = 6 * math.sin(t * 1.5 + j) * (1 - k)
            rz = 14 * math.sin(t * 1.3 + j * 2) * (1 - k)
            o.rotation_euler = (math.radians(ry), 0, math.radians(rz))
    render_seq('emblem_build', 60, upd)


def piece_turntable(name, which):
    reset((640, 640), samples=14, transparent=True)
    std()
    studio()
    navy, red, white = emblem_mats()
    o = {'base': lambda: make_base(navy), 'block': lambda: make_block(red, white), 'spire': lambda: make_spire(navy)}[which]()
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0, -7.2, 1.0), (0, 0, 0))

    def upd(i, n):
        k = i / n
        o.rotation_euler = (math.radians(5 * math.sin(k * 2 * math.pi)), 0, math.radians(28 * math.sin(k * 2 * math.pi)))
        o.location = (0, 0, 0.08 * math.sin(k * 4 * math.pi))
    render_seq(name, 48, upd)


def piece_motiv():
    piece_turntable('motiv_hero', 'block')


def piece_goal():
    piece_turntable('goal_hero', 'spire')


# ------------------------------------------------------------------ the foundation, laid course by course (experience)
COURSES = 4


def foundation():
    reset((640, 800), samples=14, transparent=True)
    std()
    studio()
    catcher(0.0)
    tones = ['#00247D', '#0A2C88', '#00247D', '#0A2C88']
    ch = (BASE_H - 0.03 * (COURSES - 1)) / COURSES
    slabs = []
    for k in range(COURSES):
        m = mat('course%d' % k, lin(tones[k]), rough=0.3, coat=0.35)
        slabs.append(box((EW, ED, ch), (0, 0, 0), m, bevel=0.03))   # box() bakes its location into the mesh
    cam = camera(lens=50)
    cam.data.dof.use_dof = False

    def upd(i, n):
        a = math.radians(lerp(-18, 12, ease(i / n)))
        look(cam, (7.6 * math.sin(a), -7.6 * math.cos(a), 2.4), (0, 0, 1.05))
        for k, o in enumerate(slabs):
            kk = (i - (8 + 18 * k)) / 9.0
            z_rest = ch / 2 + k * (ch + 0.03)
            if kk <= 0:
                o.location = (0, 0, 30)
                continue
            d = min(1.0, kk)
            bounce = 0.05 * math.exp(-(kk - 1) * 3) * abs(math.sin((kk - 1) * 9)) if kk > 1 else 0
            o.location = (0, 0, lerp(z_rest + 3.5, z_rest, d ** 2) + bounce)
            o.rotation_euler = (0, 0, math.radians((1 - d) * (20 if k % 2 else -20)))
    render_seq('foundation', 96, upd)


# ------------------------------------------------------------------ props from the brief: question mark, idea bulb, cap
def qmark():
    reset((640, 640), samples=16, transparent=True)
    std()
    studio(key=1000)
    red = mat('red', lin(RED), rough=0.25, coat=0.5)
    t = text_obj('?', 3.6, (0, 0, 0), (90, 0, 0), red, font=FONT_B, extrude=0.32, bevel=0.06)
    bpy.ops.object.empty_add(location=(0, 0, 0))
    piv = bpy.context.object
    t.parent = piv
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0, -7.0, 0.4), (0, 0, 0.05))

    def upd(i, n):
        k = out_back(i / 14.0, 2.0)
        piv.scale = (max(0.01, k),) * 3
        piv.rotation_euler = (0, math.radians(8 * math.sin(i / 10)), math.radians(lerp(-120, 0, ease(i / 16)) + 14 * math.sin(i / 9)))
    render_seq('qmark', 72, upd)


def bulb():
    reset((640, 640), samples=24, transparent=True)
    std()
    studio(key=700)
    glass = bpy.data.materials.new('glass')
    glass.use_nodes = True
    g = glass.node_tree.nodes['Principled BSDF']
    g.inputs['Base Color'].default_value = (1, 1, 1, 1)
    g.inputs['Roughness'].default_value = 0.05
    g.inputs['Transmission Weight'].default_value = 1.0
    g.inputs['IOR'].default_value = 1.2
    g.inputs['Emission Color'].default_value = lin('#FFD58A')
    g.inputs['Emission Strength'].default_value = 0.0
    root = bpy.data.objects.new('bulb', None)
    bpy.context.scene.collection.objects.link(root)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0.6), segments=64, ring_count=32)
    sph = bpy.context.object
    bpy.ops.object.shade_smooth()
    sph.data.materials.append(glass)
    bpy.ops.mesh.primitive_cone_add(radius1=0.72, radius2=0.42, depth=0.7, location=(0, 0, -0.55), vertices=64)
    neck = bpy.context.object
    bpy.ops.object.shade_smooth()
    neck.data.materials.append(glass)
    metal = mat('metal', lin('#B8BEC9'), rough=0.25, metal=1.0)
    parts = [sph, neck]
    for k in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.07, location=(0, 0, -0.95 - k * 0.15))
        o = bpy.context.object
        o.data.materials.append(metal)
        parts.append(o)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.6, location=(0, 0, -1.2), vertices=48)
    o = bpy.context.object
    o.data.materials.append(metal)
    parts.append(o)
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.08, depth=0.2, location=(0, 0, -1.6), vertices=32)
    o = bpy.context.object
    o.data.materials.append(mat('tip', lin('#2A2E38'), rough=0.4))
    parts.append(o)
    fil = mat('filament', lin('#FFC864'), rough=0.4, emit=lin('#FFB443'), estr=0.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.025, location=(0, 0, 0.55), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.data.materials.append(fil)
    parts.append(o)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.6))
    lamp = bpy.context.object
    lamp.data.color = (1.0, 0.8, 0.5)
    lamp.data.energy = 0
    lamp.data.shadow_soft_size = 0.3
    parts.append(lamp)
    for p_ in parts:
        p_.parent = root
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0, -9.0, 0.6), (0, 0, -0.1))

    def upd(i, n):
        k = out_back(i / 12.0, 1.8)
        root.scale = (max(0.01, k),) * 3
        root.rotation_euler = (0, math.radians(10 * math.sin(i / 8)), math.radians(lerp(-60, 0, ease(i / 14))))
        on = ease((i - 14) / 6.0)
        flick = 1.0 if i > 22 else (0.6 + 0.4 * (i % 2))
        fil.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 35 * on * flick
        g.inputs['Emission Strength'].default_value = 0.22 * on * flick
        lamp.data.energy = 90 * on * flick
    render_seq('bulb', 48, upd)


def cap():
    reset((640, 640), samples=16, transparent=True)
    std()
    studio(key=900)
    navy = mat('capnavy', lin('#0A1A4A'), rough=0.55)
    gold = mat('gold', lin('#D9A93A'), rough=0.3, metal=0.8)
    red = mat('capred', lin(RED), rough=0.4)
    root = bpy.data.objects.new('cap', None)
    bpy.context.scene.collection.objects.link(root)
    board = box((2.8, 2.8, 0.1), (0, 0, 0.45), navy, bevel=0.02)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=0.75, location=(0, 0, 0.0), vertices=64)
    skull = bpy.context.object
    bpy.ops.object.shade_smooth()
    skull.data.materials.append(navy)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0, 0.53))
    btn = bpy.context.object
    btn.data.materials.append(red)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=1.75, location=(0.62, -0.62, 0.52), rotation=(0, math.radians(90), math.radians(-45)))
    cord = bpy.context.object
    cord.data.materials.append(red)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.6, location=(1.25, -1.25, 0.15), vertices=24)
    tas = bpy.context.object
    tas.data.materials.append(red)
    for p_ in (board, skull, btn, cord, tas):
        p_.parent = root
    cam = camera(lens=50)
    cam.data.dof.use_dof = False
    look(cam, (0, -9.5, 3.2), (0, 0, 0.1))

    def upd(i, n):
        k = i / n
        root.rotation_euler = (math.radians(14 + 6 * math.sin(k * 2 * math.pi)), math.radians(-8 + 5 * math.cos(k * 2 * math.pi)),
                               math.radians(25 + 20 * math.sin(k * 2 * math.pi)))
        root.location = (0, 0, 0.12 * math.sin(k * 4 * math.pi))
    render_seq('cap', 48, upd)


# ------------------------------------------------------------------ storyboard scenes: paper into the bin, law books, signpost
def paper_bin():
    reset((720, 960), samples=14, transparent=True)
    std()
    studio(key=1000)
    catcher(0.0)
    paper = mat('paper', lin('#F4F1EA'), rough=0.85)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.42)
    ball = bpy.context.object
    tex = bpy.data.textures.new('crumple', 'VORONOI')
    tex.noise_scale = 0.18
    d = ball.modifiers.new('disp', 'DISPLACE')
    d.texture, d.strength = tex, 0.18
    ball.data.materials.append(paper)
    metal = mat('bin', lin('#8C95A8'), rough=0.3, metal=1.0)
    parts = []
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.95, radius2=1.2, depth=2.2, end_fill_type='NOTHING', location=(0, 0, 1.1))
    b_ = bpy.context.object
    b_.modifiers.new('sol', 'SOLIDIFY').thickness = 0.05
    bpy.ops.object.shade_smooth()
    b_.data.materials.append(metal)
    parts.append(b_)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.95, depth=0.05, location=(0, 0, 0.03))
    bpy.context.object.data.materials.append(metal)
    parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.2, minor_radius=0.045, location=(0, 0, 2.2))
    bpy.context.object.data.materials.append(mat('rim', lin(RED), rough=0.3, coat=0.5))
    parts.append(bpy.context.object)
    bpy.ops.object.empty_add(location=(0.9, 0, 0))
    piv = bpy.context.object
    for o in parts:
        o.parent = piv
    cam = camera(lens=38)
    cam.data.dof.use_dof = False
    look(cam, (-0.4, -9.5, 3.4), (-0.2, 0, 1.7))
    land = 24

    def upd(i, n):
        if i <= land:
            k = i / land
            ball.location = (lerp(-3.0, 0.9, k), 0, max(0.45, 1.6 + 2.0 * 4 * k * (1 - k) - 1.2 * k ** 2))
            ball.rotation_euler = (k * 7, k * 4, k * 3)
            ball.hide_render = False
        else:
            ball.location = (0.9, 0, 0.45)
            ball.hide_render = i > land + 1
        w = max(0, i - land)
        piv.rotation_euler = (0, math.radians(7 * math.exp(-w / 6) * math.sin(w * 0.9)) if w else 0, 0)
    render_seq('paper_bin', 40, upd)


BOOKS = [('WORK EXPERIENCE', NAVY), ('VOLUNTEERING', '#8E1020'), ('ACADEMIC PROJECTS', '#0B2C8F'), ('TRANSFERABLE SKILLS', RED)]


def books():
    reset((900, 900), samples=14, transparent=True)
    std()
    studio(key=1000)
    catcher(0.0)
    gold = mat('gold', lin(GOLD), rough=0.25, metal=1.0)
    pages = mat('pages', lin('#EFE6D2'), rough=0.9)
    roots = []
    TH = 0.5
    for k, (title, col) in enumerate(BOOKS):
        cover = mat('cover%d' % k, lin(col), rough=0.45, coat=0.3)
        root = bpy.data.objects.new('book%d' % k, None)
        bpy.context.scene.collection.objects.link(root)
        w = 3.6 - 0.1 * k
        parts = [box((w, 2.4, TH), (0, 0, 0), cover, bevel=0.04), box((w - 0.12, 2.3, TH - 0.1), (0.07, 0.03, 0), pages)]
        parts.append(text_obj(title, 0.23, (0, -1.215, 0), (90, 0, 0), gold, font=FONT_SERIF, extrude=0.005))
        for sx in (-w / 2 + 0.22, w / 2 - 0.22):
            parts.append(box((0.05, 0.02, TH * 0.75), (sx, -1.205, 0), gold))
        for p_ in parts:
            p_.parent = root
        roots.append(root)
    cam = camera(lens=45)
    cam.data.dof.use_dof = False

    def upd(i, n):
        look(cam, (lerp(-0.8, 0.8, i / n), -8.2, lerp(3.0, 3.5, i / n)), (0, 0, 1.0))
        for k, r in enumerate(roots):
            kk = (i - (8 + 18 * k)) / 9.0
            z_rest = TH / 2 + k * TH
            if kk <= 0:
                r.location = (0, 0, 40)
                continue
            d_ = min(1.0, kk)
            bounce = 0.06 * math.exp(-(kk - 1) * 3) * abs(math.sin((kk - 1) * 9)) if kk > 1 else 0
            r.location = (0.08 * (k % 2 * 2 - 1), 0, lerp(z_rest + 4.5, z_rest, d_ ** 2) + bounce)
            r.rotation_euler = (0, 0, math.radians((1 - d_) * (25 if k % 2 else -25) + (2 if k % 2 else -2)))
    render_seq('books', 96, upd)


SIGNS = [('TRAINEE SOLICITOR', NAVY, WHITE, 1), ('SPECIALISE', WHITE, NAVY, -1), ('MAKE AN IMPACT', RED, WHITE, 1)]


def signpost():
    reset((720, 1080), samples=14, transparent=True)
    std()
    studio(key=1000)
    catcher(0.0)
    post_m = mat('post', lin('#1A1F2E'), rough=0.4, metal=0.6)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=6.4, location=(0, 0, 3.2), vertices=32)
    bpy.ops.object.shade_smooth()
    bpy.context.object.data.materials.append(post_m)
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.0, depth=0.3, location=(0, 0, 6.55), vertices=32)
    bpy.context.object.data.materials.append(mat('cap', lin(RED), rough=0.3))
    roots = []
    for k, (label, bgc, fgc, d) in enumerate(SIGNS):
        board = mat('sign%d' % k, lin(bgc), rough=0.35, coat=0.4)
        ink = mat('ink%d' % k, lin(fgc), rough=0.4)
        root = bpy.data.objects.new('sign%d' % k, None)
        bpy.context.scene.collection.objects.link(root)
        root.location = (0, 0, 5.6 - k * 1.3)
        L = 3.6 if len(label) > 12 else 2.8
        body = box((L, 0.16, 0.85), (0, 0, 0), board, bevel=0.03)        # box() bakes location, so move after
        body.location = (d * (L / 2 + 0.05), 0, 0)
        tip = prism(0.85, 0.16, 0.5, (d * (L + 0.05), 0, 0), board)
        tip.rotation_euler = (0, math.radians(90 * d), 0)
        txt = text_obj(label, 0.34, (d * (L / 2 + 0.05), -0.09, 0), (90, 0, 0), ink, font=FONT_B, extrude=0.004)
        for p_ in (body, tip, txt):
            p_.parent = root
        roots.append(root)
    cam = camera(lens=42)
    cam.data.dof.use_dof = False

    def upd(i, n):
        a = math.radians(lerp(-14, 10, ease(i / n)))
        look(cam, (1.3 + 14.5 * math.sin(a), -14.5 * math.cos(a), 4.4), (1.3, 0, 3.6))
        for k, r in enumerate(roots):
            kk = out_back((i - 8 - 18 * k) / 12.0, 1.8)
            r.scale = (max(0.001, min(1.2, kk)),) * 3 if kk < 1 else (1, 1, 1)
            r.rotation_euler = (0, 0, math.radians(lerp(80 * SIGNS[k][3], 0, min(1, max(0, kk))) + 3 * math.sin(i / 11 + k)))
    render_seq('signpost', 96, upd)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
