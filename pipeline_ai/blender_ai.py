"""3D pop-up objects for BMHC "AI can recreate this building. But not what happens inside." (glossy clay, BMHC palette).

Run: blender -b -P blender_ai.py -- [draft] [name ...]  -> workspace_ai/assets/<name>.png (RGBA 900x900)
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_ai/assets'
os.makedirs(B.OUT, exist_ok=True)

MAG, TEAL, ORANGE, LIME = hexc('#E60585'), hexc('#2DC892'), hexc('#FF4200'), hexc('#69FF00')
INK, CHAR, STONE, MIST, WHITE = hexc('#0B0B0B'), hexc('#1F1F1F'), hexc('#E9E6DF'), hexc('#F6F5F1'), hexc('#FFFFFF')
SAND, SAND_D, BRASS, AMBER, TEA = hexc('#D2BC93'), hexc('#A88D62'), hexc('#D9A441'), hexc('#FFB347'), hexc('#8A3A0E')
GLASS = None


def glass():
    return mat(WHITE, 0.03, trans=1.0, coat=0)


def ngon_prism(r, h, n, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=n)
    o = act()
    bevel(o, 0.02, 2)
    return setm(o, m)


def cone(r1, r2, h, loc, m, n=64, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, location=loc, vertices=n, rotation=rot)
    return smooth(setm(act(), m))


def arch_pts(w, h, spring, n=24, z0=0.0):
    """Pointed (gothic) arch outline: straight sides up to `spring`, two arcs meeting at an apex (h is ignored)."""
    r = w * 0.85
    cxl, cxr = -w / 2 + r, w / 2 - r
    a_end = math.acos(-cxl / r)
    pts = [(-w / 2, z0), (-w / 2, z0 + spring)]
    for i in range(1, n + 1):
        a = math.pi - (math.pi - a_end) * i / n
        pts.append((cxl + r * math.cos(a), z0 + spring + r * math.sin(a)))
    for i in range(1, n):
        a = (math.pi - a_end) - (math.pi - a_end) * i / n
        pts.append((cxr + r * math.cos(a), z0 + spring + r * math.sin(a)))
    pts.append((w / 2, z0 + spring))
    pts.append((w / 2, z0))
    return pts


def extrude_outline(pts, depth, m, y=0.0, inset=None):
    """Flat outline polygon in the XZ plane extruded along Y."""
    import bmesh
    me = bpy.data.meshes.new('p')
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, z in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    o = bpy.data.objects.new('p', me)
    bpy.context.scene.collection.objects.link(o)
    bevel(o, 0.015, 2)
    return setm(o, m)


def frame_from(outer, inner, depth, m, y=0.0):
    """A frame = outer outline minus inner outline, extruded along Y (built as a bridge between the two loops)."""
    import bmesh
    me = bpy.data.meshes.new('fr')
    bm = bmesh.new()
    n = len(outer)
    assert n == len(inner)
    lay = []
    for yy in (y, y + depth):
        lay.append(([bm.verts.new((x, yy, z)) for x, z in outer], [bm.verts.new((x, yy, z)) for x, z in inner]))
    for (o, i) in lay:
        for k in range(n):
            bm.faces.new((o[k], o[(k + 1) % n], i[(k + 1) % n], i[k]))
    for loop in (0, 1):
        a, b = lay[0][loop], lay[1][loop]
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    ob = bpy.data.objects.new('fr', me)
    bpy.context.scene.collection.objects.link(ob)
    return setm(ob, m)


def scaled(pts, s, dz=0.0):
    cx = 0.0
    zs = [p[1] for p in pts]
    cz = (min(zs) + max(zs)) / 2
    return [((x - cx) * s + cx, (z - cz) * s + cz + dz) for x, z in pts]


# ------------------------------------------------------------------ objects
def window():
    """'Every window.' A gothic window from the façade: sandstone frame, tracery, glowing glass."""
    st = mat(SAND, 0.55, coat=0.15)
    outer = arch_pts(2.0, 3.4, 2.0)
    inner = [(x * 0.82, z * 0.9 + 0.17) for x, z in outer]
    frame_from(outer, inner, 0.45, st, y=-0.2)
    glow = extrude_outline(inner, 0.05, mat(hexc('#FFE2A8'), 0.2, emit=(AMBER, 3.0)), y=0.05)
    mull = box((0.12, 0.32, 2.75), loc=(0, -0.02, 1.55), m=st, bw=0.03)
    tr = box((1.6, 0.32, 0.12), loc=(0, -0.02, 1.9), m=st, bw=0.03)
    ring = torus(0.32, 0.06, loc=(0, -0.05, 2.62), m=st, rot=(math.radians(90), 0, 0))
    sill = box((2.3, 0.7, 0.18), loc=(0, -0.1, 0.05), m=mat(SAND_D, 0.6), bw=0.04)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-22)))


def brick():
    """'Every brick.' A little wall of sandstone blocks, the last one sliding in."""
    cols = (SAND, hexc('#C9AF83'), hexc('#DCC8A2'), hexc('#BFA275'))
    k = 0
    for row in range(3):
        off = 0.0 if row % 2 == 0 else 0.55
        for i in range(3 if row < 2 else 2):
            x = -1.1 + off + i * 1.1
            box((1.04, 0.62, 0.5), loc=(x, 0, row * 0.54), m=mat(cols[k % 4], 0.6, coat=0.1), bw=0.06)
            k += 1
    box((1.04, 0.62, 0.5), loc=(1.45, -0.55, 1.2), m=mat(hexc('#E3CFA6'), 0.5, coat=0.2), bw=0.06, rot=(0, math.radians(-8), math.radians(12)))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-24)))


def pinnacle():
    """'Every detail.' A gothic pinnacle with crockets and a finial, like the tower's."""
    st = mat(SAND, 0.5, coat=0.2)
    std = mat(SAND_D, 0.55)
    ngon_prism(0.7, 0.4, 8, (0, 0, 0), std)
    ngon_prism(0.55, 1.6, 8, (0, 0, 1.0), st)
    for k in range(8):
        a = k / 8 * 2 * math.pi + math.pi / 8
        box((0.08, 0.08, 1.5), loc=(0.56 * math.cos(a), 0.56 * math.sin(a), 1.0), m=std, bw=0.02, rot=(0, 0, a))
    ngon_prism(0.66, 0.16, 8, (0, 0, 1.85), std)
    cone(0.5, 0.04, 2.2, (0, 0, 3.0), st, n=8)
    for lvl in range(4):
        z = 2.15 + lvl * 0.48
        r = 0.46 - lvl * 0.1
        for k in range(4):
            a = k / 4 * 2 * math.pi + lvl * 0.4
            sph(0.1, loc=(r * math.cos(a), r * math.sin(a), z), m=st, scale=(1, 1, 1.5))
    sph(0.16, loc=(0, 0, 4.15), m=mat(BRASS, 0.2, 0.9))
    cone(0.05, 0.0, 0.5, (0, 0, 4.5), mat(BRASS, 0.2, 0.9), n=16)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(10)))


def tulip_glass(x, tilt, band):
    pts = []
    import bmesh
    # profile of a tulip tea glass, revolved
    prof = [(0.0, 0.0), (0.42, 0.0), (0.45, 0.06), (0.36, 0.45), (0.3, 0.75), (0.36, 1.1), (0.46, 1.45), (0.48, 1.5)]
    me = bpy.data.meshes.new('g')
    bm = bmesh.new()
    n = 64
    rings = []
    for r, z in prof:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z)) for k in range(n)])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.to_mesh(me)
    g = bpy.data.objects.new('g', me)
    bpy.context.scene.collection.objects.link(g)
    sol = g.modifiers.new('s', 'SOLIDIFY')
    sol.thickness = 0.03
    smooth(g)
    setm(g, glass())
    tea = cyl(0.33, 0.9, loc=(0, 0, 0.55), m=mat(TEA, 0.08, trans=0.3), v=64, bw=0)
    bd = torus(0.335, 0.03, loc=(0, 0, 0.75), m=mat(BRASS, 0.2, 0.9))
    sau = cyl(0.75, 0.08, loc=(0, 0, -0.06), m=mat(band, 0.25), v=96)
    return group([g, tea, bd, sau], rot=(0, tilt, 0), loc=(x, 0, 0))


def chai():
    """'The friendships formed.' Two tea glasses raised together."""
    tulip_glass(-0.55, math.radians(12), MAG)
    tulip_glass(0.55, math.radians(-12), TEAL)
    for k in range(5):
        a = k / 5 * 2 * math.pi
        sph(0.05, loc=(0.18 * math.cos(a), -0.3, 1.9 + 0.1 * math.sin(a)), m=mat(WHITE, 0.3, emit=(WHITE, 2.0)))


def book():
    """'The knowledge passed on.' An open book, pages lifting."""
    cover = mat(TEAL, 0.3, coat=0.5)
    page = mat(MIST, 0.6, coat=0.05)
    for sx in (-1, 1):
        box((1.55, 2.1, 0.08), loc=(sx * 0.8, 0, 0), m=cover, bw=0.03, rot=(0, sx * math.radians(-6), 0))
        box((1.45, 2.0, 0.22), loc=(sx * 0.76, 0, 0.15), m=page, bw=0.04, rot=(0, sx * math.radians(-6), 0))
    for i in range(4):
        a = math.radians(25 + i * 28)
        pts = [(0.0, -0.95 + 0, 0.3), (0.0, 0.95, 0.3)]
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        p = act()
        p.scale = (0.72, 1.0, 1)
        bpy.ops.object.transform_apply(scale=True)
        bm_mod = p.modifiers.new('sb', 'SIMPLE_DEFORM')
        bm_mod.deform_method, bm_mod.angle, bm_mod.deform_axis = 'BEND', math.radians(30), 'Y'
        p.location = (0.72 * math.cos(a) * 0 + 0.0, 0, 0.3)
        p.rotation_euler = (0, -a, 0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        p.location = (0.36 * math.cos(a), 0, 0.3 + 0.36 * math.sin(a))
        sol = p.modifiers.new('s', 'SOLIDIFY')
        sol.thickness = 0.01
        setm(p, page)
    for j in range(5):
        box((0.9, 0.05, 0.02), loc=(-0.78, -0.6 + j * 0.3, 0.27), m=mat(hexc('#9A9A9A'), 0.6), bw=0)
    curve_path([(0.2, 0.9, 0.3), (0.25, 1.1, -0.1), (0.15, 1.25, -0.5)], 0.04, mat(MAG, 0.4))
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(math.radians(14), 0, math.radians(-14)))


def target():
    """'Finding their confidence.' An archery target with an arrow in the gold."""
    cols = (WHITE, INK, TEAL, MAG, ORANGE)
    for i, c in enumerate(cols):
        r = 1.5 - i * 0.28
        cyl(r, 0.25 + i * 0.02, loc=(0, 0, 0), m=mat(c, 0.35, coat=0.5), rot=(math.radians(90), 0, 0), v=96, bw=0.03)
    sph(0.12, loc=(0, -0.2, 0), m=mat(LIME, 0.3, emit=(LIME, 0.6)))
    for sx in (-1, 1):
        box((0.12, 0.12, 2.7), loc=(sx * 0.9, 0.35, -0.8), m=mat(hexc('#8A5A36'), 0.6), bw=0.03, rot=(math.radians(15), 0, sx * math.radians(10)))
    d = Vector((0.85, -0.5, 0.32)).normalized()
    tip = Vector((0, -0.2, 0))
    q = d.to_track_quat('Z', 'Y').to_euler()
    L = 2.4
    shaft = cyl(0.06, L, loc=tuple(tip + d * (L / 2)), m=mat(hexc('#3A2A20'), 0.4), rot=tuple(q), bw=0)
    end = tip + d * (L - 0.25)
    for k in range(3):
        bpy.ops.mesh.primitive_plane_add(size=0.4, location=tuple(end))
        f = act()
        f.rotation_euler = q
        f.rotation_mode = 'XYZ'
        bpy.context.view_layer.update()
        f.rotation_euler.rotate_axis('Z', k * 2 * math.pi / 3)
        f.rotation_euler.rotate_axis('Y', math.pi / 2)
        f.scale = (1.0, 0.45, 1)
        f.location = tuple(end + (q.to_matrix() @ Vector((math.cos(k * 2.094), math.sin(k * 2.094), 0))) * 0.1)
        sol = f.modifiers.new('s', 'SOLIDIFY')
        sol.thickness = 0.02
        setm(f, mat(MAG, 0.4))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-26)))


def bubble(w, h, loc, col, word, tail=1, txtcol=WHITE):
    b = box((w, 0.5, h), loc=loc, m=mat(col, 0.28, coat=0.6), bw=0.4)
    bpy.ops.mesh.primitive_cone_add(radius1=0.32, radius2=0, depth=0.6, location=(loc[0] + tail * w * 0.28, loc[1], loc[2] - h / 2 - 0.15),
                                    rotation=(0, math.radians(180 + tail * 20), 0), vertices=32)
    t_ = smooth(setm(act(), mat(col, 0.28, coat=0.6)))
    t = text(word, 0.5, (loc[0], loc[1] - 0.27, loc[2]), mat(txtcol, 0.3), ext=0.04, font='Inter-800')
    return [b, t_, t]


def bubbles():
    """'The conversations that bring communities together.' Salaam / Hello."""
    a = bubble(2.4, 1.1, (-0.75, 0, 0.75), MAG, 'Salaam', -1)
    b = bubble(2.2, 1.1, (0.85, -0.4, -0.55), TEAL, 'Hello', 1, INK)
    group(a + b, rot=(0, 0, math.radians(-12)))


def astrolabe():
    """'What we preserve.' A brass astrolabe on a museum plinth, under a glass dome."""
    br = mat(BRASS, 0.22, 1.0)
    brd = mat(hexc('#B07D2A'), 0.3, 1.0)
    cyl(1.0, 0.1, loc=(0, 0, 1.5), m=br, rot=(math.radians(90), 0, 0), v=96)
    torus(1.0, 0.07, loc=(0, -0.02, 1.5), m=brd, rot=(math.radians(90), 0, 0))
    torus(0.62, 0.04, loc=(0, -0.08, 1.5), m=brd, rot=(math.radians(90), 0, 0))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        box((0.03, 0.04, 0.16), loc=(0.85 * math.cos(a), -0.08, 1.5 + 0.85 * math.sin(a)), m=brd, bw=0, rot=(0, -a + math.pi / 2, 0))
    box((1.9, 0.05, 0.08), loc=(0, -0.12, 1.5), m=br, bw=0.02, rot=(0, math.radians(30), 0))
    torus(0.18, 0.05, loc=(0, -0.02, 2.62), m=br, rot=(math.radians(90), 0, 0))
    box((0.16, 0.12, 0.2), loc=(0, -0.02, 2.48), m=br, bw=0.03)
    curve_path([(-0.5, -0.1, 1.1), (-0.1, -0.12, 1.85), (0.45, -0.1, 1.3)], 0.025, mat(TEAL, 0.3))
    cyl(0.08, 0.6, loc=(0, 0, 0.55), m=mat(INK, 0.3), bw=0.01)
    cyl(1.45, 0.5, loc=(0, 0, 0.0), m=mat(INK, 0.35, coat=0.6), v=96, bw=0.05)
    cyl(1.5, 0.08, loc=(0, 0, 0.27), m=mat(MAG, 0.35), v=96, bw=0.02)
    sph(1.4, loc=(0, 0, 1.4), m=glass(), scale=(1, 1, 1.25))


def lantern():
    """'What we keep alive.' A pierced brass lantern with magenta glass, lit."""
    br = mat(BRASS, 0.25, 1.0)
    ngon_prism(0.75, 1.5, 8, (0, 0, 0.9), mat(hexc('#FF5FB4'), 0.1, emit=(hexc('#FF8AC7'), 2.4), trans=0.4))
    for k in range(8):
        a = k / 8 * 2 * math.pi + math.pi / 8
        box((0.07, 0.07, 1.6), loc=(0.74 * math.cos(a), 0.74 * math.sin(a), 0.9), m=br, bw=0.02, rot=(0, 0, a))
    ngon_prism(0.85, 0.18, 8, (0, 0, 0.1), br)
    ngon_prism(0.85, 0.14, 8, (0, 0, 1.7), br)
    cone(0.85, 0.15, 0.9, (0, 0, 2.2), br, n=8)
    sph(0.15, loc=(0, 0, 2.75), m=br)
    torus(0.2, 0.04, loc=(0, 0, 3.0), m=br, rot=(math.radians(90), 0, 0))
    sph(0.28, loc=(0, 0, 0.8), m=mat(hexc('#FFE7B0'), 0.2, emit=(AMBER, 12.0)))
    L = bpy.data.objects.new('pl', bpy.data.lights.new('pl', 'POINT'))
    L.data.energy, L.data.color = 120, (1.0, 0.75, 0.45)
    L.location = (0, 0, 0.8)
    bpy.context.scene.collection.objects.link(L)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(12)))


def door():
    """'Come and experience it.' The centre's pointed-arch door, ajar, warm light inside."""
    st = mat(SAND, 0.55, coat=0.15)
    outer = arch_pts(2.6, 3.9, 2.3)
    inner = [(x * 0.8, z * 0.9 + 0.1) for x, z in outer]
    frame_from(outer, inner, 0.6, st, y=-0.3)
    extrude_outline(inner, 0.05, mat(hexc('#FFE2A8'), 0.3, emit=(AMBER, 4.0)), y=0.25)
    leaf = extrude_outline([(x, z) for x, z in inner if x <= 0.001] + [(0, 0.1)], 0.1, mat(hexc('#5A3420'), 0.45), y=0.0)
    leaf.rotation_euler = (0, 0, math.radians(-55))
    leaf.location = (-1.0, -0.05, 0)
    box((3.4, 1.2, 0.2), loc=(0, -0.4, -0.1), m=mat(SAND_D, 0.6), bw=0.04)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, 0, math.radians(-18)))


ALL = ['window', 'brick', 'pinnacle', 'chai', 'book', 'target', 'bubbles', 'astrolabe', 'lantern', 'door']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        bpy.context.scene.cycles.samples = 24 if draft else 96
        globals()[n]()
        B.render(n)
