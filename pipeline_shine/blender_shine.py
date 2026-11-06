"""BMHC "Shine": five 3D paper lanterns (ribbed paper, thin gold rims, white line icon), each rendered unlit and lit.

Usage: python3 blender_shine.py [names...]   names: faith creative wellbeing sport social  (renders <name>_off, <name>_on)
       python3 blender_shine.py icons        (draws the five white line icons first)
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_shine/lanterns'
ICONS = f'{ROOT}/workspace_shine/icons'
LANTERNS = {'faith': '#09999C', 'creative': '#DB225E', 'wellbeing': '#F26721', 'sport': '#76BF43', 'social': '#DD9933'}


def draw_icons():
    from PIL import Image, ImageDraw
    os.makedirs(ICONS, exist_ok=True)
    S = 1024
    W_ = 46

    def canvas():
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im)

    def line(d, pts, w=W_):
        d.line(pts, fill=(255, 255, 255, 255), width=w, joint='curve')
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=(255, 255, 255, 255))

    def heart_pts(cx, cy, s, t0=0.0, t1=2 * math.pi, n=160):
        pts = []
        for i in range(n + 1):
            t = t0 + (t1 - t0) * i / n
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((cx + x * s, cy + y * s))
        return pts

    # faith & character: an open heart (a gap at the top, like an open hand)
    im, d = canvas()
    line(d, heart_pts(512, 540, 20, 0.35, 2 * math.pi - 0.35))
    im.save(f'{ICONS}/faith.png')
    # creative: a paintbrush and a swoosh
    im, d = canvas()
    line(d, [(300, 760), (640, 380)], 50)
    d.polygon([(620, 330), (720, 230), (780, 290), (690, 400)], fill=(255, 255, 255, 255))
    line(d, [(250, 860), (380, 820), (520, 880), (700, 820), (800, 860)], 34)
    im.save(f'{ICONS}/creative.png')
    # well-being: a leaf-heart (heart outline with a leaf vein)
    im, d = canvas()
    line(d, heart_pts(512, 520, 19))
    line(d, [(512, 460), (512, 800)], 30)
    for k in range(3):
        y = 540 + k * 80
        line(d, [(512, y + 40), (430 - k * 10, y - 10)], 24)
        line(d, [(512, y + 40), (594 + k * 10, y - 10)], 24)
    im.save(f'{ICONS}/wellbeing.png')
    # sport: a trainer in profile
    im, d = canvas()
    line(d, [(200, 680), (820, 680), (850, 640), (820, 590), (640, 540), (560, 430), (470, 410), (430, 480), (300, 470), (230, 520), (200, 600), (200, 680)])
    for k in range(3):
        line(d, [(470 + k * 45, 470 + k * 25), (520 + k * 45, 440 + k * 25)], 26)
    line(d, [(200, 740), (840, 740)], 30)
    im.save(f'{ICONS}/sport.png')
    # social & community: two cups side by side, steam
    im, d = canvas()
    for cx in (360, 650):
        line(d, [(cx - 110, 470), (cx - 90, 760), (cx + 90, 760), (cx + 110, 470), (cx - 110, 470)])
        d.arc([cx + 80, 520, cx + 190, 660], -90, 90, fill=(255, 255, 255, 255), width=40)
        line(d, [(cx - 20, 400), (cx - 45, 340), (cx - 10, 280), (cx - 30, 230)], 26)
        line(d, [(cx + 40, 400), (cx + 15, 340), (cx + 50, 280), (cx + 30, 230)], 26)
    im.save(f'{ICONS}/social.png')
    print('icons')


if len(sys.argv) > 1 and sys.argv[1] == 'icons':
    draw_icons()
    sys.exit(0)

import bpy, bmesh
from mathutils import Vector


def lin(h):
    h = h.lstrip('#')

    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0:2]), c(h[2:4]), c(h[4:6]), 1)


def build(name, col, lit):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 64
    sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x, sc.render.resolution_y = 640, 820
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = lin('#122F2A')
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6

    # ribbed paper body
    bm = bmesh.new()
    nr, nz = 96, 48
    R, Hh = 1.0, 1.35
    rings = []
    for j in range(nz + 1):
        v = j / nz
        z = (v - 0.5) * 2 * Hh
        prof = math.sin(math.pi * (0.08 + 0.84 * v)) ** 0.85
        row = []
        for i in range(nr):
            a = i / nr * 2 * math.pi
            rib = 1 - 0.045 * (1 - abs(math.cos(a * 6)))      # 12 soft ribs
            r = R * prof * rib
            row.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        rings.append(row)
    uvl = bm.loops.layers.uv.new()
    for j in range(nz):
        for i in range(nr):
            f = bm.faces.new((rings[j][i], rings[j][(i + 1) % nr], rings[j + 1][(i + 1) % nr], rings[j + 1][i]))
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uvl].uv = (a / nr, b / nz)
    me = bpy.data.meshes.new('body'); bm.to_mesh(me); bm.free()
    body = bpy.data.objects.new('body', me); sc.collection.objects.link(body)
    for p in me.polygons:
        p.use_smooth = True
    sol = body.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.01
    m = bpy.data.materials.new('paper'); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = lin(col)
    bsdf.inputs['Roughness'].default_value = 0.65
    bsdf.inputs['Subsurface Weight'].default_value = 0.35 if lit else 0.1
    bsdf.inputs['Subsurface Radius'].default_value = (0.6, 0.4, 0.3)
    bsdf.inputs['Transmission Weight'].default_value = 0.55 if lit else 0.0
    if lit:
        bsdf.inputs['Emission Color'].default_value = lin(col)
        bsdf.inputs['Emission Strength'].default_value = 0.35
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 80; n.inputs['Detail'].default_value = 8
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08
    nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    body.data.materials.append(m)

    gold = bpy.data.materials.new('gold'); gold.use_nodes = True
    g = gold.node_tree.nodes['Principled BSDF']
    g.inputs['Base Color'].default_value = lin('#E2B354'); g.inputs['Metallic'].default_value = 1.0; g.inputs['Roughness'].default_value = 0.25
    for z, r in ((Hh * 0.96, 0.27), (-Hh * 0.96, 0.27)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.04, location=(0, 0, z), major_segments=64)
        bpy.context.object.data.materials.append(gold); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.12, location=(0, 0, z + (0.04 if z > 0 else -0.04)), vertices=64)
        bpy.context.object.data.materials.append(gold); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.025, location=(0, 0, Hh + 0.3), rotation=(math.radians(90), 0, 0), major_segments=48)
    bpy.context.object.data.materials.append(gold); bpy.ops.object.shade_smooth()
    # tassel
    tas = bpy.data.materials.new('tassel'); tas.use_nodes = True
    tas.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = lin(col)
    bpy.ops.mesh.primitive_cone_add(radius1=0.1, radius2=0.03, depth=0.4, location=(0, 0, -Hh - 0.3), rotation=(0, 0, 0), vertices=24)
    bpy.context.object.data.materials.append(tas)

    # white line icon on the front (glows when lit)
    im = bpy.data.images.load(f'{ICONS}/{name}.png')
    ic = bpy.data.materials.new('icon'); ic.use_nodes = True
    t = ic.node_tree
    for nd in list(t.nodes):
        t.nodes.remove(nd)
    o = t.nodes.new('ShaderNodeOutputMaterial'); mix = t.nodes.new('ShaderNodeMixShader')
    tr = t.nodes.new('ShaderNodeBsdfTransparent'); em = t.nodes.new('ShaderNodeEmission')
    tex = t.nodes.new('ShaderNodeTexImage'); tex.image = im
    em.inputs['Color'].default_value = (1, 1, 1, 1); em.inputs['Strength'].default_value = 6.0 if lit else 0.9
    t.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
    t.links.new(tr.outputs[0], mix.inputs[1]); t.links.new(em.outputs[0], mix.inputs[2])
    t.links.new(mix.outputs[0], o.inputs['Surface'])
    # a gently curved decal following the front of the body
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=24, size=1.0, location=(0, 0, 0))
    dec = bpy.context.object
    for v in dec.data.vertices:
        x, y = v.co.x, v.co.y
        a = x * 1.0
        z = y * 1.0
        prof = math.sin(math.pi * (0.08 + 0.84 * (z / (2 * Hh) + 0.5))) ** 0.85
        r = R * prof * 0.955 + 0.075
        v.co = Vector((math.sin(a) * r, -math.cos(a) * r - 0.0, z))
    dec.data.materials.append(ic)
    if lit:
        bpy.ops.object.light_add(type='POINT', location=(0, 0, -0.1))
        L = bpy.context.object; L.data.energy = 260; L.data.color = (1.0, 0.97, 0.93); L.data.shadow_soft_size = 0.3
    # key + rim
    for loc, e, colr in (((-3, -4, 3), 160 if lit else 380, (1.0, 0.95, 0.9)), ((3, 2, 2), 120, (0.7, 0.9, 1.0))):
        bpy.ops.object.light_add(type='AREA', location=loc)
        a_ = bpy.context.object; a_.data.size = 3; a_.data.energy = e; a_.data.color = colr
        a_.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 70
    cam.location = (0.0, -9.0, 0.6)
    cam.rotation_euler = (Vector((0, 0, 0.05)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    os.makedirs(OUT, exist_ok=True)
    sc.render.filepath = f'{OUT}/{name}_{"on" if lit else "off"}.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', name, lit, flush=True)


if __name__ == '__main__':
    names = sys.argv[1:] or list(LANTERNS)
    for nme in names:
        for lit in (False, True):
            col = LANTERNS[nme]
            if lit:
                col = {'creative': '#E0156E', 'social': '#E8B10E', 'wellbeing': '#F0560A'}.get(nme, col)
            build(nme, col, lit)
