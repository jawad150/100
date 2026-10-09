"""Procedural 3D assets for the Treats redesign, rendered with Blender (bpy, Cycles).

Usage (bpy wheel runs on Python 3.11):
    python3.11 treats3d.py <job> [<job> ...]       # jobs listed in JOBS at the bottom
    ONE=1 python3.11 treats3d.py bagel             # render a single test frame

Frames land in $TREATS_3D_WORK (default: ./work); pack.py turns them into
WebP sprite sheets for the site.
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("TREATS_3D_WORK", os.path.join(HERE, "work"))
TURN_FRAMES = 40


def lin(hexstr, a=1.0):
    """sRGB hex -> linear RGBA."""
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*c, a)


LILAC = lin("#866DAF")
INK = lin("#1E1430")
CHEESE = lin("#F7B81C")
TOMATO = lin("#E0402B")
LEAF = lin("#5FA83A")
CREAM = lin("#FFF1D6")

# ------------------------------------------------------------------ scene


def reset(res=(512, 512), samples=24):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.cycles.max_bounces = 6
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = lin("#F3EEF9")
    bg.inputs["Strength"].default_value = 0.25
    return sc


def area(loc, target, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    l.data.shape = "RECTANGLE"
    l.data.size, l.data.size_y = size
    l.data.energy = energy
    l.data.color = color
    return l


def studio(scale=1.0):
    s = scale
    area((-3.5 * s, -3.0 * s, 4.5 * s), (0, 0, 0.4), (3.5 * s, 3.5 * s), 560 * s * s, (1.0, 0.94, 0.86))   # warm key
    area((3.6 * s, 2.8 * s, 2.6 * s), (0, 0, 0.5), (2.0 * s, 4.0 * s), 650 * s * s, (0.72, 0.6, 1.0))      # lilac rim
    area((3.0 * s, -4.0 * s, 1.2 * s), (0, 0, 0.4), (4.0 * s, 3.0 * s), 140 * s * s, (1.0, 0.98, 0.95))   # fill
    area((0, 0, 6 * s), (0, 0, 0), (3 * s, 3 * s), 120 * s * s)                                             # top


def shadow_catcher(size=30):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    p = bpy.context.object
    p.is_shadow_catcher = True
    return p


def camera(loc, target, lens=50, ortho=None):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.data.lens = lens
    if ortho:
        c.data.type = "ORTHO"
        c.data.ortho_scale = ortho
    bpy.context.scene.camera = c
    return c


# ------------------------------------------------------------------ materials


def principled(name, color, rough=0.4, coat=0.0, sss=0.0, metal=0.0, transmission=0.0, ior=1.45, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = 0.08
    b.inputs["IOR"].default_value = ior
    b.inputs["Specular IOR Level"].default_value = spec
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)
        b.inputs["Subsurface Scale"].default_value = 0.08
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    return m


def bread(name, low, high, zmin, zmax, rough=0.5, coat=0.25, bump=0.25, mottle=0.25, flour=0.0):
    """Bread crust: colour ramps from `low` (sides) to `high` (top) by object-space Z,
    with noise mottling, optional flour dusting and a fine crumb bump."""
    m = principled(name, low, rough=rough, coat=coat, sss=0.12)
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = zmin
    mr.inputs["From Max"].default_value = zmax
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.5
    noise.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    add = N.new("ShaderNodeMath")
    add.operation = "ADD"
    sub = N.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    L.new(noise.outputs["Fac"], sub.inputs[0])
    sub.inputs[1].default_value = 0.5
    mul = N.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(sub.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = mottle
    L.new(mr.outputs["Result"], add.inputs[0])
    L.new(mul.outputs[0], add.inputs[1])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = low
    ramp.color_ramp.elements[1].color = high
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[1].position = 0.85
    L.new(add.outputs[0], ramp.inputs["Fac"])
    color_out = ramp.outputs["Color"]
    if flour:
        fn = N.new("ShaderNodeTexNoise")
        fn.inputs["Scale"].default_value = 14
        fn.inputs["Detail"].default_value = 10
        L.new(tc.outputs["Object"], fn.inputs["Vector"])
        fr = N.new("ShaderNodeValToRGB")
        fr.color_ramp.elements[0].position = 0.55 - flour * 0.2
        fr.color_ramp.elements[1].position = 0.62 - flour * 0.2
        L.new(fn.outputs["Fac"], fr.inputs["Fac"])
        mix = N.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        L.new(fr.outputs["Color"], mix.inputs["Factor"])
        L.new(color_out, mix.inputs[6])
        mix.inputs[7].default_value = lin("#FBF4EA")
        color_out = mix.outputs[2]
    ao = N.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.12
    aor = N.new("ShaderNodeMapRange")
    aor.inputs["To Min"].default_value = 0.45
    L.new(ao.outputs["AO"], aor.inputs["Value"])
    aom = N.new("ShaderNodeMix")
    aom.data_type = "RGBA"
    aom.blend_type = "MULTIPLY"
    aom.inputs["Factor"].default_value = 1.0
    L.new(color_out, aom.inputs[6])
    L.new(aor.outputs["Result"], aom.inputs[7])
    color_out = aom.outputs[2]
    L.new(color_out, b.inputs["Base Color"])
    bn = N.new("ShaderNodeTexNoise")
    bn.inputs["Scale"].default_value = 60
    bn.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], bn.inputs["Vector"])
    bp = N.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.02
    L.new(bn.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def bumpy(m, scale=25, strength=0.4):
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 8
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return m


# ------------------------------------------------------------------ mesh helpers


def new_obj(name, bm, mat=None, smooth=True, sub=0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if mat:
        me.materials.append(mat)
    if sub:
        m = o.modifiers.new("sub", "SUBSURF")
        m.levels = m.render_levels = sub
    return o


def tube(name, center_fn, radius_fn, n_rings=120, n_seg=48, flat=0.8, mat=None, sub=1):
    """Closed tube along a parametric path. center_fn(t) -> (Vector pos, Vector tangent);
    radius_fn(t) -> radius. Cross-section is an ellipse squashed by `flat` in Z."""
    bm = bmesh.new()
    rings = []
    for i in range(n_rings + 1):
        t = i / n_rings
        pos, tan = center_fn(t)
        tan = tan.normalized()
        up = Vector((0, 0, 1))
        side = tan.cross(up).normalized()
        upv = side.cross(tan).normalized()
        r = radius_fn(t)
        ring = []
        for j in range(n_seg):
            a = j / n_seg * 2 * math.pi
            p = pos + side * (math.cos(a) * r) + upv * (math.sin(a) * r * flat)
            ring.append(bm.verts.new(p))
        rings.append(ring)
    for i in range(n_rings):
        for j in range(n_seg):
            a, b = rings[i][j], rings[i][(j + 1) % n_seg]
            c, d = rings[i + 1][(j + 1) % n_seg], rings[i + 1][j]
            bm.faces.new((a, b, c, d))
    for ring, rev in ((rings[0], True), (rings[-1], False)):
        bm.faces.new(list(reversed(ring)) if rev else ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, mat, sub=sub)


def ellipsoid(name, loc, scale, mat=None, seg=48, ring=24, flatten_below=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=1.0)
    for v in bm.verts:
        if flatten_below is not None and v.co.z < flatten_below:
            v.co.z = flatten_below + (v.co.z - flatten_below) * 0.08
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    o = new_obj(name, bm, mat)
    o.location = loc
    return o


def rounded_cyl(name, r, h, loc, mat, bevel=0.08, seg=64, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r2 if r2 is not None else r, depth=h)
    o = new_obj(name, bm, mat)
    o.location = loc
    bv = o.modifiers.new("bv", "BEVEL")
    bv.width = bevel
    bv.segments = 6
    bv.limit_method = "ANGLE"
    s = o.modifiers.new("sub", "SUBSURF")
    s.levels = s.render_levels = 1
    return o


def scatter(name, points, size, mat, jitter=0.4, seed=1):
    """Many small ellipsoids (seeds, crumbs) in one mesh. points: [(pos, normal)]"""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for pos, nrm in points:
        q = Vector(nrm).normalized().to_track_quat("Z", "Y")
        spin = Quaternion(Vector((0, 0, 1)), rnd.uniform(0, math.pi * 2))
        k = 1 + rnd.uniform(-jitter, jitter) * 0.5
        S = Matrix.Diagonal((size[0] * k, size[1] * k, size[2], 1))
        M = Matrix.Translation(pos) @ q.to_matrix().to_4x4() @ spin.to_matrix().to_4x4() @ S
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=M)
    return new_obj(name, bm, mat)


def ruffle_disc(name, radius, mat, waves=9, amp=0.06, droop=0.12, res=72, thick=0.025, seed=0, ellipse=(1, 1)):
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=res, y_segments=res, size=radius * 1.05)
    kill = [v for v in bm.verts if (v.co.x / ellipse[0]) ** 2 + (v.co.y / ellipse[1]) ** 2 > (radius * (1 + 0.06 * math.sin(math.atan2(v.co.y, v.co.x) * 13 + ph))) ** 2]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    for v in bm.verts:
        r = math.hypot(v.co.x / ellipse[0], v.co.y / ellipse[1]) / radius
        a = math.atan2(v.co.y, v.co.x)
        e = max(0.0, min(1.0, (r - 0.55) / 0.45))
        v.co.z = amp * math.sin(waves * a + 4 * r + ph) * e - droop * e * e
    o = new_obj(name, bm, mat, sub=1)
    so = o.modifiers.new("solid", "SOLIDIFY")
    so.thickness = thick
    o.modifiers.move(1, 0)
    return o


def displace(o, strength=0.04, scale=0.4, seed=0):
    tex = bpy.data.textures.new(o.name + "_tex", "CLOUDS")
    tex.noise_scale = scale
    d = o.modifiers.new("disp", "DISPLACE")
    d.texture = tex
    d.strength = strength
    d.texture_coords = "OBJECT"
    return d


def group(name, objs, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    for o in objs:
        o.parent = e
    return e


# ------------------------------------------------------------------ products


def make_bagel():
    R, r, zs = 0.66, 0.36, 0.78
    bm = bmesh.new()
    U, V = 96, 48
    verts = []
    for i in range(U):
        u = i / U * 2 * math.pi
        row = []
        for j in range(V):
            v = j / V * 2 * math.pi
            x = (R + r * math.cos(v)) * math.cos(u)
            y = (R + r * math.cos(v)) * math.sin(u)
            z = r * math.sin(v) * zs + r * zs
            row.append(bm.verts.new((x, y, z)))
        verts.append(row)
    for i in range(U):
        for j in range(V):
            bm.faces.new((verts[i][j], verts[(i + 1) % U][j], verts[(i + 1) % U][(j + 1) % V], verts[i][(j + 1) % V]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    crust = bread("bagel", lin("#C9792E"), lin("#8A4515"), 0.15, 0.56, coat=0.45, rough=0.38, mottle=0.35)
    body = new_obj("bagel", bm, crust, sub=1)
    displace(body, 0.025, 0.35)
    rnd = random.Random(4)
    pts = []
    for _ in range(170):
        u = rnd.uniform(0, 2 * math.pi)
        v = rnd.uniform(math.radians(25), math.radians(155))
        x = (R + r * math.cos(v)) * math.cos(u)
        y = (R + r * math.cos(v)) * math.sin(u)
        z = r * math.sin(v) * zs + r * zs
        n = Vector((math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v) / zs))
        pts.append((Vector((x, y, z)) + n.normalized() * 0.004, n))
    seeds = scatter("seeds", pts, (0.042, 0.022, 0.012), principled("seed", CREAM, rough=0.45, sss=0.2), seed=4)
    return group("bagel_rig", [body, seeds]), 0.55


def burger_layers():
    bun = bread("bun", lin("#E9A04B"), lin("#B4601C"), 0.0, 0.6, coat=0.55, rough=0.32, mottle=0.18)
    bunb = bread("bunb", lin("#F2C384"), lin("#C97A2E"), -0.15, 0.16, coat=0.2, rough=0.45, mottle=0.15)
    layers = {}
    layers["bottom"] = rounded_cyl("bottom", 0.95, 0.34, (0, 0, 0.17), bunb, bevel=0.15)
    patty_m = bumpy(principled("patty", lin("#5A2C17"), rough=0.6, sss=0.05), 28, 0.6)
    p = rounded_cyl("patty", 1.0, 0.3, (0, 0, 0.5), patty_m, bevel=0.1)
    displace(p, 0.05, 0.25)
    layers["patty"] = p
    # cheese: square slice with drooping corners
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=48, y_segments=48, size=0.9)
    for v in bm.verts:
        d = math.hypot(v.co.x, v.co.y)
        v.co.z = -0.75 * max(0.0, d - 0.78) ** 1.5
    ch = new_obj("cheese", bm, principled("cheese", CHEESE, rough=0.3, sss=0.35, coat=0.3), sub=1)
    so = ch.modifiers.new("solid", "SOLIDIFY")
    so.thickness = 0.05
    ch.modifiers.move(1, 0)
    ch.location = (0, 0, 0.68)
    ch.rotation_euler = (0, 0, math.radians(20))
    layers["cheese"] = ch
    tom_m = principled("tomato", TOMATO, rough=0.18, sss=0.4, coat=0.6)
    t1 = rounded_cyl("tomato1", 0.46, 0.1, (0.38, -0.2, 0.78), tom_m, bevel=0.035)
    t2 = rounded_cyl("tomato2", 0.46, 0.1, (-0.36, 0.22, 0.78), tom_m, bevel=0.035)
    t3 = rounded_cyl("tomato3", 0.44, 0.1, (-0.1, -0.45, 0.77), tom_m, bevel=0.035)
    layers["tomato"] = group("tomato_g", [t1, t2, t3])
    let = ruffle_disc("lettuce", 1.12, principled("lettuce", LEAF, rough=0.35, sss=0.35, coat=0.3), amp=0.07, droop=0.16, seed=2)
    let.location = (0, 0, 0.9)
    layers["lettuce"] = let
    top = ellipsoid("topbun", (0, 0, 0.99), (1.0, 1.0, 0.68), bun, seg=64, ring=32, flatten_below=-0.12)
    rnd = random.Random(7)
    pts = []
    for _ in range(70):
        th = rnd.uniform(0, 2 * math.pi)
        ph = math.radians(rnd.uniform(0, 62))
        n = Vector((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)))
        p = Vector((n.x, n.y, n.z * 0.68))
        nn = Vector((n.x, n.y, n.z / 0.68))
        pts.append((p + nn.normalized() * 0.006, nn))
    seeds = scatter("bseeds", pts, (0.05, 0.026, 0.014), principled("seed", CREAM, rough=0.45, sss=0.2), seed=7)
    seeds.parent = top
    layers["top"] = top
    return layers


def make_burger():
    L = burger_layers()
    return group("burger_rig", list(L.values())), 0.85


def croissant_mesh(name="croissant"):
    Ra = 1.05

    def center(t):
        th = (t - 0.5) * 2.5
        tip = abs(th) / 1.25
        pos = Vector((Ra * math.sin(th), Ra * math.cos(th) - Ra * 0.62, 0))
        tan = Vector((math.cos(th), -math.sin(th), 0))
        return pos, tan

    def radius(t):
        base = 0.46 * math.sin(math.pi * t) ** 0.85 + 0.045
        ridge = 0.86 + 0.24 * math.sin(math.pi * 7 * t) ** 2
        return base * ridge

    def center_z(t):
        pos, tan = center(t)
        r = radius(t)
        th = (t - 0.5) * 2.5
        pos.z = r * 0.8 * 0.96 - 0.06 * (abs(th) / 1.25) ** 2
        return pos, tan

    m = bread("croissant", lin("#E39A3E"), lin("#8E4512"), 0.05, 0.7, coat=0.7, rough=0.3, mottle=0.3)
    return tube(name, center_z, radius, n_rings=160, n_seg=48, flat=0.8, mat=m)


def make_croissant():
    c = croissant_mesh()
    return group("croissant_rig", [c], loc=(0, 0.25, 0)), 0.55


def long_roll(name, length, rad, flat, mat, end_pow=0.55, z0=0.0):
    def center(t):
        return Vector((-length / 2 + length * t, 0, z0 + rad * flat * 0.96)), Vector((1, 0, 0))

    def radius(t):
        return rad * math.sin(math.pi * t) ** end_pow + 0.02

    return tube(name, center, radius, n_rings=120, n_seg=48, flat=flat, mat=mat)


def make_torpedo():
    m = bread("torpedo", lin("#E7A04C"), lin("#9A4F17"), 0.1, 0.62, coat=0.35, rough=0.4, mottle=0.3)
    L, RAD, FL = 2.8, 0.44, 0.8
    body = long_roll("torpedo", L, RAD, FL, m, end_pow=0.6)
    score = bread("score", lin("#E9B56E"), lin("#F4D49C"), -0.04, 0.04, coat=0.0, rough=0.75, mottle=0.25)
    cuts = []
    for k, x in enumerate((-0.78, -0.26, 0.26, 0.78)):
        t = (x + L / 2) / L
        top = RAD * FL * 0.96 + (RAD * math.sin(math.pi * t) ** 0.6 + 0.02) * FL
        e = ellipsoid(f"cut{k}", (x, 0, top - 0.035), (0.3, 0.085, 0.05), score, seg=32, ring=16)
        e.rotation_euler = (0, 0, math.radians(38))
        cuts.append(e)
    return group("torpedo_rig", [body] + cuts), 0.45


def make_finger_roll():
    pale = bread("finger", lin("#F3D6A4"), lin("#E2B072"), 0.2, 0.75, coat=0.15, rough=0.6, mottle=0.25, flour=0.0)
    paleb = bread("fingerb", lin("#F6DDB0"), lin("#DDA762"), -0.05, 0.2, coat=0.1, rough=0.55, mottle=0.2)
    bottom = long_roll("fr_bottom", 2.4, 0.42, 0.5, paleb, end_pow=0.35)
    let = ruffle_disc("fr_lettuce", 1.2, principled("lettuce", LEAF, rough=0.35, sss=0.35, coat=0.3),
                      waves=22, amp=0.05, droop=0.05, seed=3, ellipse=(1.0, 0.36))
    let.location = (0, 0, 0.42)
    ham = ruffle_disc("fr_ham", 1.1, principled("ham", lin("#F09A95"), rough=0.35, sss=0.4),
                      waves=10, amp=0.03, droop=0.04, seed=5, ellipse=(1.0, 0.33), thick=0.04)
    ham.location = (0, 0, 0.47)
    egg = ruffle_disc("fr_cheese", 1.05, principled("cheese", CHEESE, rough=0.3, sss=0.35),
                      waves=6, amp=0.02, droop=0.03, seed=6, ellipse=(1.0, 0.3), thick=0.04)
    egg.location = (0, 0, 0.52)
    top = long_roll("fr_top", 2.45, 0.44, 0.78, pale, end_pow=0.35, z0=0.5)
    return group("finger_rig", [bottom, let, ham, egg, top]), 0.6


def make_salad():
    rnd = random.Random(11)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.12], context="VERTS")
    for v in bm.verts:
        v.co.x *= 1.15
        v.co.y *= 1.15
        v.co.z = max(v.co.z, -0.86) * 0.72
    bowl_m = principled("bowl", lin("#FBF8FF"), rough=0.12, coat=1.0)
    # lilac rim band by Z
    nt = bowl_m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.02
    ramp.color_ramp.elements[0].color = lin("#FBF8FF")
    ramp.color_ramp.elements[1].position = 0.03
    ramp.color_ramp.elements[1].color = LILAC
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.08
    mr.inputs["From Max"].default_value = 0.09
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "GREATER_THAN"
    inv.inputs[1].default_value = 0.6
    nt.links.new(mr.outputs["Result"], inv.inputs[0])
    nt.links.new(inv.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    bowl = new_obj("bowl", bm, bowl_m, sub=1)
    so = bowl.modifiers.new("solid", "SOLIDIFY")
    so.thickness = 0.06
    bowl.modifiers.move(1, 0)
    bowl.location = (0, 0, 0.62)
    parts = [bowl]
    leaf_m = principled("leaf", LEAF, rough=0.35, sss=0.35, coat=0.3)
    leaf2_m = principled("leaf2", lin("#8CCB5E"), rough=0.35, sss=0.35, coat=0.3)
    for k in range(16):
        a = k / 16 * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        rr = rnd.uniform(0.15, 0.75)
        lf = ruffle_disc(f"leaf{k}", rnd.uniform(0.32, 0.45), leaf_m if k % 3 else leaf2_m, waves=7, amp=0.035,
                         droop=-0.06, res=28, seed=k, ellipse=(1.0, 0.55), thick=0.02)
        lf.location = (math.cos(a) * rr, math.sin(a) * rr, 0.62 + rnd.uniform(0.0, 0.18) + (0.75 - rr) * 0.12)
        lf.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), a + rnd.uniform(-1, 1))
        parts.append(lf)
    tom_m = principled("tomato", TOMATO, rough=0.12, sss=0.35, coat=0.8)
    for k in range(6):
        a = k / 6 * 2 * math.pi + 0.4
        rr = rnd.uniform(0.25, 0.6)
        parts.append(ellipsoid(f"cherry{k}", (math.cos(a) * rr, math.sin(a) * rr, 0.84 + rnd.uniform(0, 0.08)), (0.15, 0.15, 0.14), tom_m, seg=32, ring=16))
    cuc = principled("cucumber", lin("#DDEFC0"), rough=0.3, sss=0.3)
    cuc_skin = principled("cskin", lin("#2F6B22"), rough=0.3)
    for k in range(5):
        a = k / 5 * 2 * math.pi + 1.1
        rr = rnd.uniform(0.2, 0.55)
        c = rounded_cyl(f"cuc{k}", 0.17, 0.05, (math.cos(a) * rr, math.sin(a) * rr, 0.9 + rnd.uniform(0, 0.05)), cuc, bevel=0.015, seg=32)
        c.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0)
        ring = rounded_cyl(f"cucr{k}", 0.185, 0.045, (0, 0, 0), cuc_skin, bevel=0.01, seg=32)
        ring.parent = c
        ring.scale = (1, 1, 0.9)
        parts += [c, ring]
    olive = principled("olive", lin("#2A2032"), rough=0.12, coat=0.8)
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.2
        rr = rnd.uniform(0.15, 0.5)
        o = ellipsoid(f"olive{k}", (math.cos(a) * rr, math.sin(a) * rr, 0.9), (0.09, 0.07, 0.07), olive, seg=24, ring=12)
        o.rotation_euler = (0, 0, a)
        parts.append(o)
    return group("salad_rig", parts), 0.7


def make_cup():
    cup_m = principled("cup", lin("#FFFFFF"), rough=0.25, coat=0.6)
    sleeve_m = principled("sleeve", LILAC, rough=0.35, coat=0.4)
    lid_m = principled("lid", INK, rough=0.2, coat=0.8)
    body = rounded_cyl("cup", 0.48, 1.55, (0, 0, 0.775), cup_m, bevel=0.03, r2=0.62)
    sleeve = rounded_cyl("sleeve", 0.565, 0.52, (0, 0, 0.82), sleeve_m, bevel=0.02, r2=0.6)
    lid = rounded_cyl("lid", 0.67, 0.12, (0, 0, 1.6), lid_m, bevel=0.04)
    dome = ellipsoid("dome", (0, 0, 1.64), (0.6, 0.6, 0.16), lid_m, flatten_below=0.0)
    # TREATS wordmark on the sleeve, wrapped round the cup
    cu = bpy.data.curves.new("word", "FONT")
    cu.body = "TREATS"
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = 0.2
    cu.extrude = 0.008
    tx = bpy.data.objects.new("word", cu)
    bpy.context.scene.collection.objects.link(tx)
    tx.data.materials.append(principled("txt", lin("#FFFFFF"), rough=0.3))
    tx.location = (0, -0.6, 0.82)
    tx.rotation_euler = (math.radians(90), 0, 0)
    sd = tx.modifiers.new("bend", "SIMPLE_DEFORM")
    sd.deform_method = "BEND"
    sd.deform_axis = "Z"
    sd.angle = math.radians(-70)
    return group("cup_rig", [body, sleeve, lid, dome, tx]), 0.9


def scores(xs, top_fn, mat, length=0.3, width=0.085, angle=38, prefix="cut", depth=0.045):
    out = []
    for k, x in enumerate(xs):
        e = ellipsoid(f"{prefix}{k}", (x, 0, top_fn(x) - 0.045), (length, width, depth), mat, seg=32, ring=16)
        e.rotation_euler = (0, 0, math.radians(angle))
        out.append(e)
    return out


def roll_top(L, RAD, FL, end_pow, z0=0.0):
    return lambda x: z0 + RAD * FL * 0.96 + (RAD * math.sin(math.pi * ((x + L / 2) / L)) ** end_pow + 0.02) * FL


def make_baps():
    m = bread("baps", lin("#F1D3A0"), lin("#CF9550"), -0.1, 0.5, coat=0.05, rough=0.7, mottle=0.45, flour=0.0)
    a = ellipsoid("bap1", (-0.55, 0.15, 0.3), (0.8, 0.8, 0.42), m, flatten_below=-0.55)
    b = ellipsoid("bap2", (0.6, -0.2, 0.3), (0.78, 0.78, 0.4), m, flatten_below=-0.55)
    return group("baps_rig", [a, b]), 0.4


def make_ciabatta():
    m = bread("ciabatta", lin("#E8C080"), lin("#B97735"), -0.1, 0.35, coat=0.05, rough=0.75, mottle=0.55, flour=0.0)
    o = ellipsoid("ciabatta", (0, 0, 0.26), (1.4, 0.72, 0.3), m, flatten_below=-0.6)
    displace(o, 0.09, 0.45)
    return group("ciabatta_rig", [o]), 0.3


def tri_slice(name, mat_crumb, mat_crust, z, th=0.17, size=1.0, bevel=0.06, segs=4):
    bm = bmesh.new()
    pts = [Vector((-1.05, -0.62, 0)) * size, Vector((1.05, -0.62, 0)) * size, Vector((0, 1.0, 0)) * size]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += th
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for fc in bm.faces:
        fc.material_index = 0 if abs(fc.normal.z) > 0.5 else 1
    o = new_obj(name, bm, None, smooth=False)
    o.data.materials.append(mat_crumb)
    o.data.materials.append(mat_crust)
    bv = o.modifiers.new("bv", "BEVEL")
    bv.width = bevel
    bv.segments = segs
    bv.harden_normals = False
    o.location = (0, 0, z)
    return o


def make_sandwich():
    crumb = bread("crumb", lin("#FFF4E0"), lin("#F6E3C2"), -0.1, 0.2, coat=0.0, rough=0.85, mottle=0.2, bump=0.5)
    crust = bread("crust", lin("#C98A44"), lin("#B57434"), -0.1, 0.2, coat=0.1, rough=0.6, mottle=0.2)
    bottom = tri_slice("s_bottom", crumb, crust, 0.0)
    let = ruffle_disc("s_let", 1.0, principled("lettuce", LEAF, rough=0.35, sss=0.35, coat=0.3), waves=12, amp=0.04, droop=0.04, seed=8, ellipse=(1.05, 0.85))
    let.location = (0, 0.05, 0.2)
    tom = principled("tomato", TOMATO, rough=0.15, sss=0.4, coat=0.6)
    ts = [rounded_cyl(f"s_tom{k}", 0.3, 0.07, (x, -0.2 + abs(x) * 0.0, 0.25), tom, bevel=0.02, seg=40) for k, x in enumerate((-0.45, 0.0, 0.45))]
    ham = ruffle_disc("s_ham", 0.95, principled("ham", lin("#F09A95"), rough=0.35, sss=0.4), waves=8, amp=0.03, droop=0.03, seed=9, ellipse=(1.0, 0.8), thick=0.04)
    ham.location = (0, 0.05, 0.3)
    top = tri_slice("s_top", crumb, crust, 0.34)
    return group("sandwich_rig", [bottom, let, ham, top] + ts), 0.3


def make_khubz():
    m = bread("khubz", lin("#F5DDB2"), lin("#E6BE80"), -0.05, 0.1, coat=0.0, rough=0.7, mottle=0.9, bump=0.4)
    parts = []
    for k in range(3):
        d = rounded_cyl(f"khubz{k}", 1.05, 0.09, (k * 0.12 - 0.12, k * 0.08, 0.05 + k * 0.1), m, bevel=0.045, seg=72)
        displace(d, 0.05, 0.5)
        d.rotation_euler = (math.radians(4 * (k - 1)), math.radians(-3 * (k - 1)), k)
        parts.append(d)
    return group("khubz_rig", parts), 0.25


def make_pocket():
    m = bread("pita", lin("#EFCB92"), lin("#D9A35E"), -1.0, 0.1, coat=0.0, rough=0.7, mottle=1.1, bump=0.35)
    body = ellipsoid("pocket", (0, 0, 0.0), (1.1, 0.3, 1.0), m, flatten_below=None)
    bm = bmesh.new()
    bm.from_mesh(body.data)
    for v in bm.verts:
        if v.co.z > 0.06:
            v.co.z = 0.06 + (v.co.z - 0.06) * 0.04
            v.co.y *= 1.15
    bm.to_mesh(body.data)
    bm.free()
    body.location = (0, 0, 1.0)
    parts = [body]
    rnd = random.Random(21)
    leaf = principled("lettuce", LEAF, rough=0.35, sss=0.35, coat=0.3)
    for k in range(7):
        lf = ruffle_disc(f"pl{k}", 0.34, leaf, waves=7, amp=0.04, droop=-0.04, res=28, seed=k + 30, ellipse=(1.0, 0.55), thick=0.02)
        lf.location = (rnd.uniform(-0.8, 0.8), rnd.uniform(-0.12, 0.12), 1.12 + rnd.uniform(0, 0.12))
        lf.rotation_euler = (rnd.uniform(0.6, 1.4) * (1 if k % 2 else -1), rnd.uniform(-0.4, 0.4), rnd.uniform(-0.6, 0.6))
        parts.append(lf)
    tom = principled("tomato", TOMATO, rough=0.12, sss=0.35, coat=0.8)
    for k, x in enumerate((-0.45, 0.1, 0.55)):
        t = rounded_cyl(f"pt{k}", 0.2, 0.06, (x, -0.05, 1.16), tom, bevel=0.02, seg=32)
        t.rotation_euler = (math.radians(70), 0, rnd.uniform(-0.3, 0.3))
        parts.append(t)
    rig = group("pocket_rig", parts)
    return rig, 0.7


def make_kebab():
    meat = bumpy(principled("kebab", lin("#7A3A1C"), rough=0.5, coat=0.3, sss=0.05), 18, 0.7)
    steel = principled("steel", lin("#C9CDD6"), rough=0.2, metal=1.0)
    parts = []
    sk = rounded_cyl("skewer", 0.035, 3.4, (0, 0, 0.3), steel, bevel=0.01, seg=24)
    sk.rotation_euler = (0, math.radians(90), 0)
    parts.append(sk)
    ring = None
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.025, location=(1.82, 0, 0.3), rotation=(0, math.radians(90), 0))
    ring = bpy.context.object
    ring.data.materials.append(steel)
    parts.append(ring)

    def seg_center(x0, ln):
        return lambda t: (Vector((x0 + ln * t, 0, 0.3)), Vector((1, 0, 0)))

    def seg_radius(t):
        return 0.24 * math.sin(math.pi * t) ** 0.3 * (1 + 0.08 * math.sin(t * math.pi * 9)) + 0.01

    for k, x0 in enumerate((-1.45, -0.2)):
        parts.append(tube(f"meat{k}", seg_center(x0, 1.05), seg_radius, n_rings=80, n_seg=36, flat=1.0, mat=meat))
    onion = principled("onion", lin("#E7D3EE"), rough=0.3, sss=0.4)
    for k, x in enumerate((-0.32, 0.95)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.05, location=(x, 0, 0.3), rotation=(0, math.radians(90), 0))
        o = bpy.context.object
        o.data.materials.append(onion)
        bpy.ops.object.shade_smooth()
        parts.append(o)
    pep = principled("pepper", lin("#3E9A35"), rough=0.2, coat=0.6)
    bpy.ops.mesh.primitive_cube_add(size=0.34, location=(-1.62, 0, 0.3))
    pc = bpy.context.object
    bv = pc.modifiers.new("bv", "BEVEL")
    bv.width = 0.08
    bv.segments = 5
    pc.data.materials.append(pep)
    bpy.ops.object.shade_smooth()
    parts.append(pc)
    rig = group("kebab_rig", parts)
    return rig, 0.3


def make_wrap():
    tort = bread("tortilla", lin("#EFCD93"), lin("#D7A35F"), -0.6, 0.6, coat=0.0, rough=0.7, mottle=1.3, bump=0.35)
    fill = [(0.33, lin("#FFF1DA")), (0.27, LEAF), (0.19, TOMATO), (0.11, lin("#F2D29C"))]
    parts = []
    for k, (x, y, h, tilt) in enumerate(((-0.45, 0.1, 1.3, -8), (0.45, -0.1, 1.05, 10))):
        body = rounded_cyl(f"wrap{k}", 0.4, h, (x, y, h / 2), tort, bevel=0.03, seg=64)
        cap = []
        for j, (r, col) in enumerate(fill):
            c = rounded_cyl(f"wf{k}{j}", r, 0.06, (x, y, h + 0.005 + j * 0.006), principled(f"f{j}", col, rough=0.35, sss=0.3), bevel=0.02, seg=48)
            cap.append(c)
        g = group(f"wrapg{k}", [body] + cap)
        g.rotation_euler = (math.radians(tilt), 0, 0)
        parts.append(g)
    return group("wrap_rig", parts), 0.65


def make_baguettes():
    m = bread("baguette", lin("#E39A4A"), lin("#99501A"), 0.05, 0.5, coat=0.3, rough=0.45, mottle=0.3)
    sc = bread("score", lin("#E9B56E"), lin("#F4D49C"), -0.04, 0.04, coat=0.0, rough=0.75, mottle=0.25)
    parts = []
    for k, (y, rz) in enumerate(((-0.25, -14), (0.35, 12))):
        L, RAD, FL = 3.2, 0.27, 0.85
        body = long_roll(f"bag{k}", L, RAD, FL, m, end_pow=0.45)
        cuts = scores((-1.0, -0.33, 0.33, 1.0), roll_top(L, RAD, FL, 0.45), sc, length=0.28, width=0.05, prefix=f"bc{k}")
        g = group(f"bagg{k}", [body] + cuts, loc=(0, y, k * 0.02))
        g.rotation_euler = (0, 0, math.radians(rz))
        parts.append(g)
    return group("baguettes_rig", parts), 0.3


def make_bloomer():
    m = bread("bloomer", lin("#D98B3C"), lin("#7E3E12"), 0.05, 0.9, coat=0.25, rough=0.5, mottle=0.35)
    sc = bread("score", lin("#EBC283"), lin("#F6DDB0"), -0.04, 0.04, coat=0.0, rough=0.8, mottle=0.3, flour=0.3)
    L, RAD, FL = 2.4, 0.68, 0.72
    body = long_roll("bloomer", L, RAD, FL, m, end_pow=0.3)
    cuts = scores((-0.75, -0.38, 0.0, 0.38, 0.75), lambda x: roll_top(L, RAD, FL, 0.3)(x) - 0.01, sc, length=0.34, width=0.07, angle=62, prefix="blc", depth=0.07)
    return group("bloomer_rig", [body] + cuts), 0.5


def make_samosa():
    m = bumpy(bread("samosa", lin("#E2A04A"), lin("#A85E1C"), 0.0, 0.6, coat=0.15, rough=0.45, mottle=0.6, bump=0.0), 16, 0.7)
    parts = []
    for k, (x, y, rz, sc) in enumerate(((-0.7, 0.4, 15, 0.95), (0.8, -0.35, 150, 0.8))):
        o = tri_slice(f"samosa{k}", m, m, 0.0, th=0.62, size=sc * 0.8, bevel=0.26, segs=6)
        sub = o.modifiers.new("sub", "SUBSURF")
        sub.levels = sub.render_levels = 2
        o.location = (x, y, 0)
        o.rotation_euler = (0, 0, math.radians(rz))
        parts.append(o)
    return group("samosa_rig", parts), 0.3


def make_med_roll():
    m = bread("medroll", lin("#E5A65A"), lin("#9C5520"), 0.0, 0.55, coat=0.2, rough=0.5, mottle=0.35)
    body = ellipsoid("medroll", (0, 0, 0.42), (0.95, 0.95, 0.52), m, flatten_below=-0.75)
    rnd = random.Random(33)
    olive = principled("olive", lin("#2A2032"), rough=0.15, coat=0.8)
    tom = principled("sundried", lin("#B5281C"), rough=0.3, coat=0.5, sss=0.3)
    herb = principled("herb", lin("#3D7A2A"), rough=0.4)
    cheese = principled("feta", lin("#FFF8EA"), rough=0.6, sss=0.3)
    parts = [body]

    def on_top(rmax):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0, rmax)
        x, y = math.cos(a) * r * 0.95, math.sin(a) * r * 0.95
        z = 0.42 + 0.52 * math.sqrt(max(0.0, 1 - r * r))
        n = Vector((x / 0.95 ** 2, y / 0.95 ** 2, (z - 0.42) / 0.52 ** 2)).normalized()
        return Vector((x, y, z)), n

    for k in range(6):
        p, n = on_top(0.75)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.035, location=p)
        o = bpy.context.object
        o.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
        o.data.materials.append(olive)
        bpy.ops.object.shade_smooth()
        parts.append(o)
    for k in range(7):
        p, n = on_top(0.8)
        o = ellipsoid(f"sd{k}", p, (0.11, 0.07, 0.03), tom, seg=24, ring=12)
        o.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
        parts.append(o)
    for k in range(5):
        p, n = on_top(0.6)
        o = ellipsoid(f"feta{k}", p, (0.08, 0.08, 0.06), cheese, seg=16, ring=8)
        displace(o, 0.02, 0.1)
        parts.append(o)
    pts = [on_top(0.85) for _ in range(40)]
    parts.append(scatter("herbs", pts, (0.03, 0.015, 0.006), herb, seed=5))
    return group("medroll_rig", parts), 0.5


RANGE = {
    "baps": (make_baps, 4.0), "ciabattas": (make_ciabatta, 4.0), "sandwich": (make_sandwich, 3.8),
    "khubz": (make_khubz, 3.9), "pockets": (make_pocket, 4.2), "kebab": (make_kebab, 4.9),
    "wrap": (make_wrap, 4.0), "baguettes": (make_baguettes, 5.4), "bloomer": (make_bloomer, 4.4),
    "samosa": (make_samosa, 4.4), "medroll": (make_med_roll, 3.5),
}


def range_still(name):
    reset((448, 448), samples=int(os.environ.get("SAMPLES", 24)))
    studio()
    shadow_catcher()
    fn, d = RANGE[name]
    rig, zc = fn()
    rig.rotation_euler.z += math.radians(-22)
    camera((0, -d * 0.87, d * 0.5), (0, 0, zc * 0.8), lens=50)
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(out_dir("range"), f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered range", name, flush=True)


PRODUCTS = {
    "bagel": make_bagel,
    "croissant": make_croissant,
    "burger": make_burger,
    "finger": make_finger_roll,
    "torpedo": make_torpedo,
    "salad": make_salad,
    "cup": make_cup,
}


CAM_DIST = {"bagel": 3.9, "croissant": 4.0, "burger": 4.6, "finger": 4.5, "torpedo": 4.5, "salad": 4.2, "cup": 4.7}


def out_dir(name):
    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)
    return d


def render_frames(name, n, update):
    sc = bpy.context.scene
    d = out_dir(name)
    if os.environ.get("ONE"):
        n = 1
    for i in range(n):
        update(i, n)
        sc.render.filepath = os.path.join(d, f"{i:03d}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", name, i, flush=True)


def turntable(name):
    reset((448, 448), samples=int(os.environ.get("SAMPLES", 16)))
    studio()
    shadow_catcher()
    rig, zc = PRODUCTS[name]()
    d = CAM_DIST.get(name, 5.0)
    camera((0, -d * 0.87, d * 0.5), (0, 0, zc * 0.8), lens=50)

    def upd(i, n):
        rig.rotation_euler = (0, 0, -2 * math.pi * i / n)

    render_frames(name, TURN_FRAMES, upd)


def explode():
    reset((400, 500), samples=int(os.environ.get("SAMPLES", 16)))
    studio(1.2)
    shadow_catcher()
    L = burger_layers()
    order = ["bottom", "patty", "cheese", "tomato", "lettuce", "top"]
    base = {k: L[k].location.copy() for k in order}
    rig = group("rig", [L[k] for k in order])
    cam = camera((0, -7.6, 3.4), (0, 0, 1.55), lens=50)
    tilt = [0.0, -0.06, 0.08, -0.05, 0.07, -0.08]

    def upd(i, n):
        e = i / (n - 1)
        e = e * e * (3 - 2 * e)  # smoothstep
        for k, key in enumerate(order):
            L[key].location = base[key] + Vector((0, 0, k * 0.5 * e))
            L[key].rotation_euler.x = tilt[k] * e
            L[key].rotation_euler.y = tilt[(k + 2) % 6] * e
        rig.rotation_euler = (0, 0, math.radians(-25 + 50 * e))

    render_frames("explode", 40, upd)


# ------------------------------------------------------------------ SaaS shapes + logo


def gloss(color, rough=0.12):
    return principled("gloss", color, rough=rough, coat=1.0, sss=0.05)


def shape(name):
    reset((420, 420), samples=28)
    studio(0.9)
    camera((0, -5.5, 1.6), (0, 0, 0), lens=55)
    if name == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.38, major_segments=96, minor_segments=48)
        o = bpy.context.object
        o.data.materials.append(gloss(LILAC))
        bpy.ops.object.shade_smooth()
        o.rotation_euler = (math.radians(62), math.radians(-18), 0)
    elif name == "pill":
        o = tube("pill", lambda t: (Vector((-1.0 + 2.0 * t, 0, 0)), Vector((1, 0, 0))),
                 lambda t: 0.5 * math.sqrt(max(0.0, 1 - (max(0.0, abs(t - 0.5) - 0.25) / 0.25) ** 2)) + 0.002,
                 n_rings=96, n_seg=48, flat=1.0, mat=gloss(CHEESE))
        o.rotation_euler = (0, math.radians(-35), math.radians(25))
    elif name == "sphere":
        o = ellipsoid("sphere", (0, 0, 0), (1, 1, 1), gloss(TOMATO, 0.08), seg=64, ring=32)
    elif name == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1.5)
        o = bpy.context.object
        bv = o.modifiers.new("bv", "BEVEL")
        bv.width = 0.3
        bv.segments = 10
        o.data.materials.append(gloss(INK, 0.15))
        bpy.ops.object.shade_smooth()
        o.rotation_euler = (math.radians(35), math.radians(20), math.radians(40))
    elif name == "glass":  # second ring, cheese yellow
        bpy.ops.mesh.primitive_torus_add(major_radius=0.9, minor_radius=0.42, major_segments=96, minor_segments=48)
        o = bpy.context.object
        o.data.materials.append(gloss(CHEESE))
        bpy.ops.object.shade_smooth()
        o.rotation_euler = (math.radians(-55), math.radians(25), 0)
    elif name == "blob":
        mb = bpy.data.metaballs.new("mb")
        mb.resolution = 0.05
        mb.render_resolution = 0.025
        o = bpy.data.objects.new("blob", mb)
        bpy.context.scene.collection.objects.link(o)
        for co, r in (((0, 0, 0), 1.0), ((0.75, 0.1, 0.35), 0.7), ((-0.7, -0.1, -0.3), 0.75), ((0.1, 0, -0.75), 0.6)):
            el = mb.elements.new()
            el.co = co
            el.radius = r
        o.data.materials.append(gloss(LILAC, 0.1))
    elif name == "seed":
        o = ellipsoid("seed", (0, 0, 0), (1.0, 0.52, 0.3), principled("seed", CREAM, rough=0.4, sss=0.3), seg=48, ring=24)
        o.rotation_euler = (math.radians(30), 0, math.radians(30))
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(out_dir("shapes"), f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered shape", name, flush=True)


def logo():
    reset((1600, 560), samples=32)
    studio(1.6)
    shadow_catcher(60)
    tile_m = gloss(LILAC, 0.18)
    txt_m = principled("txt", (1, 1, 1, 1), rough=0.25, coat=0.4)
    parts = []
    for k, ch in enumerate("TREATS"):
        x = (k - 2.5) * 1.18
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0.6))
        t = bpy.context.object
        t.scale = (1.02, 0.5, 1.2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bv = t.modifiers.new("bv", "BEVEL")
        bv.width = 0.12
        bv.segments = 8
        bpy.ops.object.shade_smooth()
        t.data.materials.append(tile_m)
        cu = bpy.data.curves.new("L", "FONT")
        cu.body = ch
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.size = 0.82
        cu.extrude = 0.06
        cu.bevel_depth = 0.012
        tx = bpy.data.objects.new("L", cu)
        bpy.context.scene.collection.objects.link(tx)
        tx.data.materials.append(txt_m)
        tx.location = (0, -0.27, -0.04)
        tx.rotation_euler = (math.radians(90), 0, 0)
        tx.parent = t
        t.rotation_euler = (0, math.radians((k % 2) * 6 - 3), math.radians((k - 2.5) * -4))
        t.location.z = 0.6 + (0.18 if k % 2 else 0)
        parts.append(t)
    camera((0, -13.0, 3.4), (0, 0, 0.7), lens=58)
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(out_dir("shapes"), "logo.png")
    bpy.ops.render.render(write_still=True)
    print("rendered logo", flush=True)


JOBS = {
    **{k: (lambda k=k: turntable(k)) for k in PRODUCTS},
    "explode": explode,
    "logo": logo,
    **{f"shape_{s}": (lambda s=s: shape(s)) for s in ("torus", "pill", "sphere", "cube", "glass", "blob", "seed")},
    **{f"range_{k}": (lambda k=k: range_still(k)) for k in RANGE},
}

if __name__ == "__main__":
    for job in sys.argv[1:]:
        JOBS[job]()
