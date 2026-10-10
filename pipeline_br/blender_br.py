"""Bodyrade 3D elements rendered with Blender Cycles as transparent PNG sequences.

Usage: REEL_WORKDIR=.../workspace_br python3 blender_br.py <asset> [...]
Assets: pouch_orange pouch_raspberry pouch_pear chevron text_5in1 orange_slice mango_cube raspberry
        pear_cube ice_cube
"""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline_of'))
import bpy, bmesh
from mathutils import Vector
import blender_of as B   # shared toolkit: reset, mat, area, panel, camera, render_seq, curve_obj, to_mesh, lin

S = B.S
B.FONT = S + '/fonts/Jost-900.ttf'
YELLOW = B.lin('#FDCF09')
BLACK = B.lin('#141414')
ORANGE = B.lin('#FF6A13')
RASP = B.lin('#D2143F')
PEAR = B.lin('#9BC53D')


def studio_dark(rim=(1.0, 0.82, 0.2), key=700, rim_e=1600):
    B.area((-3.2, -3.6, 4.0), (math.radians(50), 0, math.radians(-40)), (3, 3), key, (1.0, 0.95, 0.88))
    B.area((3.8, 2.5, 1.8), (math.radians(70), 0, math.radians(125)), (2.5, 5), rim_e, rim)
    B.area((-3.8, 2.0, 0.5), (math.radians(80), 0, math.radians(-120)), (2.0, 5), rim_e * 0.7, rim)
    B.area((3.5, -3, -1.5), (math.radians(110), 0, math.radians(45)), (4, 4), 120, (1.0, 0.9, 0.8))
    B.panel((-2.5, -2.5, 3.5), (math.radians(50), 0, math.radians(-40)), (2.6, 0.35), (1, 0.97, 0.92), 14)
    B.panel((3.0, 1.5, 0.5), (math.radians(80), 0, math.radians(120)), (0.4, 4.0), rim, 16)


def img_mat(name, path, rough=0.42, coat=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(path)
    tex.interpolation = 'Cubic'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Coat Weight'].default_value = coat
    bsdf.inputs['Coat Roughness'].default_value = 0.12
    bsdf.inputs['Specular IOR Level'].default_value = 0.55
    return m, tex.image


def pouch(flavour):
    path = f'{S}/src/cut_{flavour}.png'
    B.reset((720, 1120), samples=24)
    rim = {'orange': (1.0, 0.55, 0.15), 'raspberry': (1.0, 0.25, 0.4), 'pear': (0.7, 1.0, 0.3)}[flavour]
    studio_dark(rim=rim)
    m_front, im = img_mat('front', path)
    w_px, h_px = im.size
    aspect = w_px / h_px
    Hh = 3.0
    Ww = Hh * aspect
    bm = bmesh.new()
    nu, nv = 48, 80
    verts = {}
    for side in (1, -1):
        for j in range(nv + 1):
            for i in range(nu + 1):
                u, v = i / nu, j / nv
                x = (u - 0.5) * Ww
                z = (v - 0.5) * Hh
                # pillow inflation, flatter toward the crimped top seal
                puff = (1 - abs(2 * u - 1) ** 3.2) * (1 - abs(2 * v - 1) ** 3.5)
                seal = 1.0 if v < 0.86 else max(0.0, 1 - (v - 0.86) / 0.06)
                y = -side * 0.22 * puff * seal
                verts[(side, i, j)] = bm.verts.new((x, y, z))
    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.new()
    for side in (1, -1):
        for j in range(nv):
            for i in range(nu):
                q = [verts[(side, i, j)], verts[(side, i + 1, j)], verts[(side, i + 1, j + 1)], verts[(side, i, j + 1)]]
                if side == -1:
                    q = q[::-1]
                f = bm.faces.new(q)
                f.material_index = 0 if side == 1 else 1
                for loop in f.loops:
                    key = [k for k, vv in verts.items() if vv == loop.vert][0] if False else None
                for loop, (ii, jj) in zip(f.loops, ([(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)] if side == 1
                                                   else [(i, j + 1), (i + 1, j + 1), (i + 1, j), (i, j)])):
                    uu = ii / nu if side == 1 else 1 - ii / nu
                    loop[uv_layer].uv = (uu, jj / nv)
    me = bpy.data.meshes.new('pouch')
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('pouch', me)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    o.data.materials.append(m_front)
    # back: same silhouette (alpha) but matte black foil
    m_back, _ = img_mat('back', path, rough=0.5, coat=0.2)
    nt = m_back.node_tree
    bsdf = nt.nodes['Principled BSDF']
    for l in list(bsdf.inputs['Base Color'].links):
        nt.links.remove(l)
    bsdf.inputs['Base Color'].default_value = (0.012, 0.012, 0.012, 1)
    o.data.materials.append(m_back)
    B.camera((0, -5.75, 0.1), (0, 0, 0.0), lens=58)

    def upd(i, n):
        ang = i / n * 2 * math.pi
        o.rotation_euler = (math.radians(4), 0, ang)
        o.location.z = 0.0
    B.render_seq('pouch_' + flavour, 64, upd)


def chevron():
    """Extrude the logo chevron mark (right part of the logo) in glossy yellow."""
    import cv2
    B.reset((620, 620), samples=24)
    studio_dark()
    im = cv2.imread(f'{S}/site/logo.png', cv2.IMREAD_UNCHANGED)
    a = im[..., 3]
    h, w = a.shape
    sub = a[:, int(w * 0.70):]
    cnts, hier = cv2.findContours((sub > 128).astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    loops = []
    s = 3.0 / max(sub.shape)
    for c in cnts:
        if cv2.contourArea(c) < 20:
            continue
        c = cv2.approxPolyDP(c, 0.8, True)
        loops.append([((p[0][0] - sub.shape[1] / 2) * s, -(p[0][1] - sub.shape[0] / 2) * s) for p in c])
    o = B.curve_obj('chev', loops, extrude=0.22, bevel=0.04, res=4)
    o = B.to_mesh(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(B.mat('y', YELLOW, rough=0.18, coat=1.0, metal=0.2))
    B.camera((0, -9.5, 0.3), (0, 0, 0), lens=60)

    def upd(i, n):
        u = i / max(n - 1, 1)
        e = 1 - (1 - min(u / 0.55, 1)) ** 3
        ang = (1 - e) * 120 + 10 * math.sin(u * math.pi * 2) * e
        o.rotation_euler = (math.radians(90 + (1 - e) * 15), 0, math.radians(ang))
    B.render_seq('chevron', 48, upd)


def text_5in1():
    B.reset((1300, 560), samples=16)
    studio_dark(key=900, rim_e=2000)
    bpy.ops.object.text_add()
    t = bpy.context.object
    t.data.body = '5in1'
    t.data.font = bpy.data.fonts.load(B.FONT)
    t.data.align_x = 'CENTER'
    t.data.align_y = 'CENTER'
    t.data.extrude = 0.16
    t.data.bevel_depth = 0.025
    t.data.bevel_resolution = 4
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(B.mat('y', YELLOW, rough=0.16, coat=1.0, metal=0.15))
    bpy.context.view_layer.update()
    B.camera((0, -7.0, 0.0), (0, 0, 0), lens=60)
    cam = bpy.context.scene.camera
    cam.data.sensor_fit = 'HORIZONTAL'
    cam.location.y = -t.dimensions.x * 1.25 * cam.data.lens / cam.data.sensor_width

    def upd(i, n):
        u = i / max(n - 1, 1)
        e = 1 - (1 - min(u / 0.6, 1)) ** 3
        ang = (1 - e) * 90 + 6 * math.sin(u * math.pi * 2) * e
        t.rotation_euler = (math.radians(90 + (1 - e) * 20), 0, math.radians(ang))
    B.render_seq('text_5in1', 40, upd)


def _tumble(name, obj, n=32, res=(380, 380)):
    def upd(i, nn):
        ph = i / nn * 2 * math.pi
        obj.rotation_euler = (ph * 0.5 + 0.4, ph + 0.3, ph * 0.25)
    B.render_seq(name, n, upd)


def fruit_scene():
    B.reset((380, 380), samples=16)
    studio_dark(rim=(1, 0.9, 0.7), key=900)
    B.camera((0, -6.4, 0.3), (0, 0, 0), lens=70)


def orange_slice():
    fruit_scene()
    from PIL import Image, ImageDraw
    sz = 512
    img = Image.new('RGB', (sz, sz), (255, 140, 30))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, sz, sz), fill=(255, 120, 10))
    d.ellipse((22, 22, sz - 22, sz - 22), fill=(255, 245, 220))
    d.ellipse((34, 34, sz - 34, sz - 34), fill=(255, 150, 30))
    c = sz / 2
    for k in range(10):
        a0 = k / 10 * 2 * math.pi
        for r in range(40, int(sz / 2 - 36), 3):
            x0, y0 = c + math.cos(a0) * r, c + math.sin(a0) * r
            d.line([(c, c), (x0, y0)], fill=(255, 238, 205), width=3)
    d.ellipse((c - 14, c - 14, c + 14, c + 14), fill=(255, 238, 205))
    px = f'{S}/src/orange_slice_tex.png'
    img.save(px)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.22, vertices=96, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.04; bv.segments = 4
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new('os'); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(px)
    coord = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.5, 0.5, 0.5); mp.inputs['Location'].default_value = (0.5, 0.5, 0.5)
    nt.links.new(coord.outputs['Object'], mp.inputs['Vector'])
    # project on XZ (cap faces are along Y)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); comb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(mp.outputs['Vector'], sep.inputs[0])
    nt.links.new(sep.outputs['X'], comb.inputs['X']); nt.links.new(sep.outputs['Y'], comb.inputs['Y'])
    nt.links.new(comb.outputs[0], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.25
    b.inputs['Subsurface Weight'].default_value = 0.4
    b.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.2)
    b.inputs['Subsurface Scale'].default_value = 0.1
    b.inputs['Coat Weight'].default_value = 0.6
    o.data.materials.append(m)
    _tumble('orange_slice', o)


def mango_cube():
    fruit_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.4)
    o = bpy.context.object
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.18; bv.segments = 6
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 1
    disp_tex = bpy.data.textures.new('n', 'CLOUDS'); disp_tex.noise_scale = 0.35
    d = o.modifiers.new('d', 'DISPLACE'); d.texture = disp_tex; d.strength = 0.04
    bpy.ops.object.shade_smooth()
    o.data.materials.append(B.mat('mango', B.lin('#FFB21A'), rough=0.22, coat=0.7, sss=0.5))
    _tumble('mango_cube', o)


def raspberry():
    fruit_scene()
    mt = B.mat('rasp', B.lin('#C8102E'), rough=0.32, coat=0.5, sss=0.6)
    root = bpy.data.objects.new('r', None)
    bpy.context.scene.collection.objects.link(root)
    rng = np.random.default_rng(3)
    golden = math.pi * (3 - math.sqrt(5))
    nd = 90
    for k in range(nd):
        yv = 1 - (k / (nd - 1)) * 1.7
        r = math.sqrt(max(0, 1 - yv * yv))
        th = golden * k
        p = Vector((math.cos(th) * r * 0.85, math.sin(th) * r * 0.85, yv * 0.95))
        if p.z < -0.6:
            continue
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2 + rng.uniform(-0.02, 0.02), location=p * 1.0,
                                             segments=16, ring_count=10)
        s = bpy.context.object
        bpy.ops.object.shade_smooth()
        s.data.materials.append(mt)
        s.parent = root
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.82, segments=32, ring_count=16)
    core = bpy.context.object
    core.data.materials.append(B.mat('rc', B.lin('#8A0A20'), rough=0.4))
    core.parent = root
    _tumble('raspberry', root)


def pear_cube():
    fruit_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.4)
    o = bpy.context.object
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.14; bv.segments = 6
    bpy.ops.object.shade_smooth()
    o.data.materials.append(B.mat('flesh', B.lin('#F3F1D2'), rough=0.3, coat=0.5, sss=0.6))
    # skin on one face
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.72))
    sk = bpy.context.object
    sk.scale = (1.38, 1.38, 0.06)
    bv = sk.modifiers.new('bv', 'BEVEL'); bv.width = 0.05; bv.segments = 4
    bpy.ops.object.shade_smooth()
    sk.data.materials.append(B.mat('skin', B.lin('#B5D334'), rough=0.3, coat=0.6, sss=0.2))
    sk.parent = o
    _tumble('pear_cube', o)


def ice_cube():
    fruit_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.4)
    o = bpy.context.object
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.12; bv.segments = 5
    disp_tex = bpy.data.textures.new('n', 'CLOUDS'); disp_tex.noise_scale = 0.4
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = sub.render_levels = 2
    d = o.modifiers.new('d', 'DISPLACE'); d.texture = disp_tex; d.strength = 0.05
    bpy.ops.object.shade_smooth()
    bpy.context.scene.cycles.film_transparent_glass = True
    m = B.mat('ice', (0.85, 0.95, 1.0, 1), rough=0.05, transmission=1.0)
    m.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value = 1.31
    o.data.materials.append(m)
    _tumble('ice_cube', o)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a.startswith('pouch_'):
            pouch(a[6:])
        else:
            globals()[a]()
