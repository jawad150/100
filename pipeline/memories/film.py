"""Yaadein - Spider-Man memory reel: Blender (Cycles) shots built from the user's assets.

python3 film.py <shot> [<layer>]       layer: full (default) | bg | hero | fg | anim
  -> workspace2/plates3/<shot>_<layer>.png  (16-bit RGBA, + _mist.png for depth fog)
  anim -> workspace2/plates3/<shot>/0001.png ... (true 3D camera/object animation with Cycles motion blur)
Env: RES (scale of 1080x1920, default 1.2), SAMPLES, PREVIEW=1 (fast, low res)
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cast as CA  # noqa: E402
import world as W  # noqa: E402

OUT = W.ROOT + '/plates3'
X = CA.X
RED = (1.0, 0.06, 0.04)
MOON = (0.45, 0.6, 1.0)
WARM = (1.0, 0.55, 0.25)
FPS = 60


# ================================================================== helpers
def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


def put(objs, cname):
    c = coll(cname)
    for o in objs:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        c.objects.link(o)
        for ch in o.children_recursive:
            for uc in list(ch.users_collection):
                uc.objects.unlink(ch)
            c.objects.link(ch)


def sky_emissive(objs, strength=1.0, tint=(1, 1, 1)):
    """Turn an environment's textured sky sphere into a pure emitter that doesn't block the sun."""
    for o in objs:
        if o.type == 'MESH' and o.name.startswith('Sphere'):
            m = o.material_slots[0].material
            nt = m.node_tree
            keep = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0].name
            for n in list(nt.nodes):
                if n.name != keep:
                    nt.nodes.remove(n)
            tex = nt.nodes[keep]
            mix = nt.nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            mix.inputs['Factor'].default_value = 1.0
            mix.inputs['B'].default_value = (*tint, 1)
            e = nt.nodes.new('ShaderNodeEmission')
            e.inputs['Strength'].default_value = strength
            out = nt.nodes.new('ShaderNodeOutputMaterial')
            nt.links.new(tex.outputs['Color'], mix.inputs['A'])
            nt.links.new(mix.outputs['Result'], e.inputs['Color'])
            nt.links.new(e.outputs[0], out.inputs['Surface'])
            o.visible_shadow = False
            o.visible_diffuse = False
            o.visible_glossy = True
            o.rotation_mode = 'XYZ'
            return o


def sun_from(az_src, el, color, strength, angle=1.2, name='sun'):
    """Sun lamp whose light comes FROM compass azimuth az_src (deg, 0=+X east, 90=+Y north), elevation el."""
    phi = math.radians(az_src + 90)                    # see derivation: travel = -(cos az, sin az)
    return W.sun((90 - el, 0, math.degrees(phi)), color, strength, angle, name)


def align_sky(sphere, az_src):
    """Rotate a textured sky dome so the brightest point of its texture (the sun) sits at azimuth az_src."""
    import numpy as np
    m = sphere.material_slots[0].material
    img = [n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE'][0].image
    w, h = img.size
    px = np.array(img.pixels[:], np.float32).reshape(h, w, -1)[..., :3]
    lum = px.mean(2)
    lum = lum * (np.arange(h)[:, None] > h * 0.35)            # ignore the ground half (v small = bottom)
    v, u = np.unravel_index(np.argmax(lum), lum.shape)
    uv_t = (u / w, v / h)
    me = sphere.data
    uvl = me.uv_layers.active.data
    best, vid = 9, 0
    for li, loop in enumerate(me.loops):
        uv = uvl[li].uv
        d = (uv[0] - uv_t[0]) ** 2 + (uv[1] - uv_t[1]) ** 2
        if d < best:
            best, vid = d, loop.vertex_index
    p = sphere.matrix_world @ me.vertices[vid].co - sphere.matrix_world.translation
    az_now = math.degrees(math.atan2(p.y, p.x))
    sphere.rotation_euler.z += math.radians(az_src - az_now)
    bpy.context.view_layer.update()
    return az_now


def kill_lights(objs):
    """Remove imported lights; returns the surviving objects."""
    keep = [o for o in objs if o.type != 'LIGHT']
    for o in [o for o in objs if o.type == 'LIGHT']:
        bpy.data.objects.remove(o)
    return keep


def wet(objs, rough_mul=0.45):
    for o in objs:
        if o.type != 'MESH':
            continue
        for s in o.material_slots:
            m = s.material
            if not m or not m.node_tree or m.get('wet'):
                continue
            b = m.node_tree.nodes.get('Principled BSDF')
            if not b:
                continue
            if b.inputs['Roughness'].links:
                mm = m.node_tree.nodes.new('ShaderNodeMath')
                mm.operation = 'MULTIPLY'
                mm.inputs[1].default_value = rough_mul
                m.node_tree.links.new(b.inputs['Roughness'].links[0].from_socket, mm.inputs[0])
                m.node_tree.links.new(mm.outputs[0], b.inputs['Roughness'])
            else:
                b.inputs['Roughness'].default_value *= rough_mul
            m['wet'] = 1


def emissive_boost(objs, name_has, strength):
    for o in objs:
        if o.type == 'MESH':
            for s in o.material_slots:
                m = s.material
                if m and name_has.lower() in m.name.lower():
                    b = m.node_tree.nodes.get('Principled BSDF')
                    if b:
                        b.inputs['Emission Strength'].default_value = strength


def suit_wet(meshes, k=0.6):
    """Rain sheen on the suit."""
    wet(meshes, k)


# ================================================================== environments
def env_ruins(scale=26.0, fogd=0.012):
    new = CA._import(X + '/dark-scene-diorama/source/unz/DARK.fbx')
    CA.bind_textures(new, X + '/dark-scene-diorama/textures',
                     [('Arbol', 'Arbol_Low'), ('Piso', 'Piso_Low'), ('Cruz', 'Cruz_Low'), ('Vela', 'Velas_Low'),
                      ('Piedra', 'Piedras_Low'), ('Stone', 'Stone_Low'), ('pCube', 'ladrillos_low'), ('', 'ladrillos_low')])
    new = kill_lights(new)
    arm, meshes, root = CA.normalise(new, None, name='ruins')
    root.scale = (scale,) * 3
    bpy.context.view_layer.update()
    wet(meshes, 0.5)
    emissive_boost(meshes, 'Velas', 12)
    put([root], 'env')
    # night sky + moon backlight + red emergency glow + haze
    W.world_hdri('kloppenheim_06_puresky', strength=0.06, rot_z=40, tint=(0.35, 0.45, 1.0),
                 bg_strength=0.05, bg_tint=(0.25, 0.33, 0.9))
    W.sun((68, 0, 168), MOON, 2.2, angle=0.5, name='moon')                  # backlight from the north
    W.area((6, 6, 1.2), (-2, 0, 2.5), RED, 2600, size=3, name='redglow')     # emergency-flare glow
    W.area((2, -9, 6), (-2, 0, 2), (0.5, 0.6, 1.0), 260, size=8, name='skyfill')
    ext = W.plane((200, 200), (0, 0, 0.28), W.pbr('rubble', 'brown_mud_leaves_01', scale=3.0, tint=(0.25, 0.25, 0.28),
                                                     wet=0.8), name='groundext')
    put([ext], 'env')
    if fogd:
        f = W.fog((60, 60, 16), (0, 0, 7), fogd, color=(0.72, 0.8, 1.0), anis=0.62, noise=0.5, name='ruinfog')
        put([f], 'fx')
    return meshes


def env_temple(sun_az=182, sun_el=6, fogd=0.010, sky=1.1):
    new = CA._import(X + '/an-overgrown-japanese-style-location/source/локация  на скетч.fbx')
    new = kill_lights(new)
    sph = sky_emissive(new, sky, (1.0, 0.80, 0.66))
    if sph:
        align_sky(sph, sun_az)
    put([o for o in new if o.parent is None], 'env')
    W.world_hdri('grasslands_sunset', strength=0.25)
    sun_from(sun_az, sun_el, (1.0, 0.56, 0.28), 4.5, angle=1.2)
    W.area((2, -2, 9), (-3, -2, 0), (1.0, 0.72, 0.5), 450, size=10, name='bounce')
    if fogd:
        f = W.fog((60, 60, 16), (0, 0, 7), fogd, color=(1.0, 0.85, 0.7), anis=0.7, noise=0.4, name='templefog')
        put([f], 'fx')
    return new


def env_land(sun_az=48, sun_el=4, fogd=0.0025, sky=1.0, warm=1.0):
    new = CA._import(X + '/landscape-forest-mountains/source/пейзаж ск.fbx')
    new = kill_lights(new)
    sph = sky_emissive(new, sky, (1.0, 0.86 - 0.12 * warm, 0.8 - 0.25 * warm))
    if sph:
        align_sky(sph, sun_az)
    put([o for o in new if o.parent is None], 'env')
    W.world_hdri('kloppenheim_06_puresky', strength=0.25, rot_z=sun_az)
    sun_from(sun_az, sun_el, (1.0, 0.48, 0.25), 3.5 * warm + 0.6, angle=1.5)
    if fogd:
        f = W.fog((120, 120, 24), (0, 15, 10), fogd, color=(1.0, 0.82, 0.72), anis=0.7, noise=0.3, name='landfog')
        put([f], 'fx')
    return new


def env_void(haze=0.004):
    w = bpy.context.scene.world
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.0005, 0.0006, 0.001, 1)
    if haze:
        f = W.fog((12, 12, 8), (0, 0, 2), haze, color=(0.8, 0.85, 1.0), anis=0.5, noise=0.6, name='voidfog')
        put([f], 'fx')


def ground(x, y, top=60.0):
    """Highest environment surface at (x, y) (ray cast down, ignoring fog volumes)."""
    dg = bpy.context.evaluated_depsgraph_get()
    origin = Vector((x, y, top))
    while True:
        hit, loc, nrm, idx, ob, mat = bpy.context.scene.ray_cast(dg, origin, Vector((0, 0, -1)))
        if not hit:
            return 0.0
        if 'fog' in ob.name.lower() or ob.name.startswith('Sphere') or ob.parent is None and ob.name.startswith('Sphere'):
            origin = loc + Vector((0, 0, -0.01))
            continue
        if ob.users_collection and ob.users_collection[0].name in ('hero', 'fg', 'fx'):
            origin = loc + Vector((0, 0, -0.01))
            continue
        return loc.z


def _blocked(a, b):
    """True if environment geometry lies between points a and b."""
    dg = bpy.context.evaluated_depsgraph_get()
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    d.normalize()
    o = a
    travelled = 0.0
    while travelled < L:
        hit, loc, nrm, idx, ob, mat = bpy.context.scene.ray_cast(dg, o, d, distance=L - travelled)
        if not hit:
            return False
        cn = ob.users_collection[0].name if ob.users_collection else ''
        if 'fog' in ob.name.lower() or ob.name.startswith('Sphere') or cn in ('hero', 'fg', 'fx'):
            step = (loc - o).length + 0.01
            o = loc + d * 0.01
            travelled += step
            continue
        return True
    return False


def pick_eye(target, az, el, dist, sweep=(0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90, 120, -120, 180)):
    """Camera position at compass azimuth az (deg) / elevation el around target with a clear line of
    sight (tries nearby azimuths, then shorter distances)."""
    t = Vector(target)
    for k in (1.0, 0.8, 0.6, 0.45):
        for da in sweep:
            a, e = math.radians(az + da), math.radians(el)
            eye = t + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * dist * k
            if not _blocked(t, eye) and not _blocked(eye + Vector((0, 0, 0.05)), eye - Vector((0, 0, 0.05))):
                return eye
    return t + Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.3)) * dist


# ================================================================== cast
def spidey(pose='stand', loc=(0, 0, 0), rot_z=0.0, wetness=0.0, **kw):
    arm, meshes, root = CA.raimi()
    getattr(CA, 'pose_' + pose)(arm, CA.RAIMI, **kw)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rot_z))
    bpy.context.view_layer.update()
    if wetness:
        suit_wet(meshes, 1 - 0.5 * wetness)
    put([root], 'hero')
    return arm, meshes, root


def mary_jane(loc=(0, 0, 0), rot_z=0.0, height=1.25):
    arm, meshes, root = CA.mary_jane(height)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rot_z))
    put([root], 'hero')
    return meshes, root


def goblin(loc=(0, 0, 0), rot_z=0.0, height=2.2):
    new = CA.goblin()
    arm, meshes, root = CA.normalise(new, height, name='goblin')
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rot_z))
    put([root], 'hero')
    return meshes, root


def prop(rel, height, loc, rot=(0, 0, 0), cname='hero', name=None, bind=None, fit_max=False):
    new = CA._import(X + '/' + rel)
    if bind:
        CA.bind_textures(new, X + '/' + bind[0], bind[1])
    new = kill_lights(new)
    arm, meshes, root = CA.normalise(new, height, name=name or 'prop')
    if fit_max:
        lo, hi = CA.world_bbox(meshes)
        k = height / max(hi - lo)
        root.scale = tuple(v * k for v in root.scale)
        root.location = root.location * k
        bpy.context.view_layer.update()
        lo, hi = CA.world_bbox(meshes)
        root.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2))
        bpy.context.view_layer.update()
    root.location = loc
    root.rotation_euler = tuple(math.radians(r) for r in rot)
    put([root], cname)
    return meshes, root


def pivot(root, meshes, name='pivot'):
    """Empty at the meshes' bbox centre that carries `root` (keeps world transform) - animate this."""
    lo, hi = CA.world_bbox(meshes)
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = (lo + hi) / 2
    bpy.context.view_layer.update()
    mw = root.matrix_world.copy()
    root.parent = e
    root.matrix_world = mw
    e.rotation_mode = 'XYZ'
    bpy.context.view_layer.update()
    return e


def rose(loc, rot=(0, 0, 0), height=0.42, cname='hero'):
    return prop('red-rose/source/unz/Red_rose_SF.obj', height, loc, rot, cname, 'rose')


def frame(loc, rot=(0, 0, 0), height=0.32, photo=None, cname='hero'):
    """'memory bank' frame; its front panel gets the memory photo."""
    meshes, root = prop('memory-bank/source/memory_bank.glb', height, loc, rot, cname, 'frame')
    for o in meshes:
        o.data.materials.clear()
        o.data.materials.append(W.plain('framebody', (0.04, 0.035, 0.035), 0.35, 0.3))
    if photo:
        lo, hi = CA.world_bbox(meshes)
        # photo card slightly in front of the panel (local -Y of the root after rotation)
        bpy.ops.mesh.primitive_plane_add(size=1)
        p = bpy.context.object
        p.name = 'photo'
        p.scale = ((hi.x - lo.x) * 0.0 + height * 0.62, height * 0.5, 1)
        p.data.materials.append(photo_mat(photo))
        p.rotation_euler = (math.radians(90), 0, 0)
        p.parent = root
        p.location = (0, -0.6, 0.5)
    return meshes, root


def photo_mat(path, strength=0.0):
    m = bpy.data.materials.new('photo')
    m.use_nodes = True
    nt = m.node_tree
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(path, check_existing=True)
    b = nt.nodes['Principled BSDF']
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.25
    if strength:
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = strength
    return m


# ================================================================== layers & output
def render_layers(name, layers, cam_lens=None):
    sc = bpy.context.scene
    vl = sc.view_layers[0]
    pre = OUT + '/' + name
    os.makedirs(OUT, exist_ok=True)
    suffix = '_preview' if os.environ.get('PREVIEW') else ''

    def setlayer(hide=(), holdout=()):
        for lc in vl.layer_collection.children:
            lc.exclude = lc.name in hide
            lc.holdout = lc.name in holdout
    for L in layers:
        sc.render.film_transparent = L in ('hero', 'fg')
        if L == 'full':
            setlayer()
        elif L == 'bg':
            setlayer(hide=('hero', 'fg'))
        elif L == 'hero':
            setlayer(hide=('fg', 'fx'), holdout=('env',))       # no fog in the cut-out layers (bg carries it)
        elif L == 'fg':
            setlayer(hide=('fx',), holdout=('env', 'hero'))
        W.render(f'{pre}_{L}{suffix}.png')


def finish(name, layers=('full',)):
    lay = os.environ.get('LAYERS')
    if lay:
        layers = tuple(lay.split(','))
    render_layers(name, layers)


def animate_render(name, frames):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = FPS
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    d = OUT + '/' + name + ('_preview' if os.environ.get('PREVIEW') else '')
    os.makedirs(d, exist_ok=True)
    sc.render.filepath = d + '/'
    sc.render.image_settings.file_format = 'PNG'
    step = int(os.environ.get('STEP', '1'))
    sc.frame_step = step
    bpy.ops.render.render(animation=True)


def key_cam(cam, keys, focus_obj=None):
    """keys: [(frame, loc, target)]. Smooth bezier keyframes on location + a tracked target empty."""
    tgt = bpy.data.objects.new('camtgt', None)
    bpy.context.scene.collection.objects.link(tgt)
    con = cam.constraints.new('TRACK_TO')
    con.target = tgt
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    cam.rotation_euler = (0, 0, 0)
    for f, loc, t in keys:
        cam.location = loc
        cam.keyframe_insert('location', frame=f)
        tgt.location = t
        tgt.keyframe_insert('location', frame=f)
    if focus_obj is not None:
        cam.data.dof.focus_object = focus_obj
    for ob in (cam, tgt):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in _fcurves(ad.action):
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.easing = 'EASE_IN_OUT'
                    kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
    return tgt


def _fcurves(action):
    if hasattr(action, 'fcurves') and len(getattr(action, 'fcurves', [])):
        return action.fcurves
    out = []
    for layer in getattr(action, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out


# ================================================================== shots
SHOTS = {}


def bone_w(arm, key, tail=False):
    pb = arm.pose.bones[CA.RAIMI[key]]
    return arm.matrix_world @ (pb.tail if tail else pb.head)


def shot(fn):
    SHOTS[fn.__name__] = fn
    return fn


@shot
def a1_mask(layers=('full',)):
    """Hook: extreme close-up of the mask in the night ruins, lightning rim, rain."""
    W.reset(48)
    env_ruins(fogd=0.03)
    gx, gy = HERO_RUINS
    arm, meshes, root = spidey('crouch', (gx, gy, ground(gx, gy)), rot_z=15, wetness=1.0, look_pitch=4, look_yaw=-8)
    head = arm.matrix_world @ arm.pose.bones[CA.RAIMI['head']].head
    W.area((head.x - 1.0, head.y + 1.3, head.z + 0.8), head, MOON, 420, size=0.9, name='rim')
    W.area((head.x + 1.1, head.y + 0.6, head.z + 0.1), head, RED, 160, size=0.6, name='redrim')
    W.area((head.x - 0.4, head.y - 1.6, head.z + 0.4), head, (0.55, 0.65, 1.0), 18, size=1.8, name='fill')
    W.camera(pick_eye(head, -60, -2, 1.2), (head.x, head.y, head.z + 0.02), lens=75, fstop=1.8)
    finish('a1_mask', layers)


@shot
def a2_reveal(layers=('bg', 'hero', 'fg')):
    """Behind-reveal: camera slides past a ruined wall to the crouched hero on the wall top."""
    W.reset(48)
    env_ruins()
    gx, gy = HERO_RUINS
    gz = ground(gx, gy)
    spidey('crouch', (gx, gy, gz), rot_z=15, wetness=1.0)
    # foreground occluder for the behind-reveal: a broken brick pillar close to the lens
    tgt = Vector((gx - 0.1, gy, gz + 0.6))
    eye = pick_eye(tgt, -55, 6, 5.0)
    pil = W.box((0.9, 0.9, 6.0), tuple(near_lens(eye, tgt, 1.6, -0.55, 0.0)) , W.pbr('pillar', 'brick_wall_001', scale=1.0,
                tint=(0.35, 0.3, 0.3), wet=0.6), name='pillar', bevel=0.05)
    put([pil], 'fg')
    W.camera(eye, tgt, lens=32, fstop=2.0)
    finish('a2_reveal', layers)


@shot
def a4_wide(layers=('full',)):
    W.reset(48)
    env_ruins()
    gx, gy = HERO_RUINS
    gz = ground(gx, gy)
    spidey('crouch', (gx, gy, gz), rot_z=15, wetness=1.0)
    W.area((gx + 1.2, gy - 1.0, gz + 1.5), (gx, gy, gz + 0.5), RED, 260, size=0.8, name='herored')
    tgt = Vector((gx - 1.5, gy + 1.5, gz + 0.5))
    W.camera(pick_eye(tgt, -70, 32, 12.0), tgt, lens=24, fstop=4.0)
    finish('a4_wide', layers)


HERO_RUINS = (1.0, -1.6)
SIT_RUINS = (-4.8, -1.75)
PHOTO = W.ROOT + '/plates3/c2_mj_portrait_full.png'


KNEEL_RUINS = (2.4, -2.4)


def ruins_hold():
    """Hero kneeling in the open ruins holding the memory frame (photo glows softly)."""
    env_ruins()
    x, y = KNEEL_RUINS
    gz = ground(x, y)
    arm, meshes, root = spidey('kneel_hold', (x, y, gz), rot_z=-20, wetness=1.0)
    wl, wr = bone_w(arm, 'wrist_l'), bone_w(arm, 'wrist_r')
    mid = (wl + wr) / 2
    ph = PHOTO if os.path.exists(PHOTO) else None
    fm, froot = frame((mid.x, mid.y - 0.06, mid.z - 0.02), rot=(30, 0, 160), height=0.30, photo=ph)
    W.area((mid.x + 0.25, mid.y - 0.5, mid.z + 0.15), mid, (1.0, 0.72, 0.55), 22, size=0.3, name='photoglow')
    W.area((x + 2.5, y - 2.5, gz + 2.0), (x, y, gz + 0.8), (0.55, 0.65, 1.0), 220, size=2, name='moonkey')
    W.area((x - 1.5, y + 1.8, gz + 1.2), (x, y, gz + 0.9), RED, 300, size=1, name='redrim')
    return arm, mid, gz


@shot
def b1_frame(layers=('bg', 'hero')):
    """Over-the-shoulder close-up on the frame in his hands, rack focus target = photo."""
    W.reset(48)
    arm, mid, gz = ruins_hold()
    head = bone_w(arm, 'head')
    tgt = mid + Vector((0, -0.05, -0.02))
    W.camera(pick_eye(tgt, 80, 42, 0.85), tgt, lens=45, fstop=2.0)
    finish('b1_frame', layers)


@shot
def b2_hands(layers=('full',)):
    """Front low close-up: his masked face looking down at the glowing photo."""
    W.reset(48)
    arm, mid, gz = ruins_hold()
    head = bone_w(arm, 'head')
    tgt = (head + mid) / 2
    W.camera(pick_eye(tgt, -80, -8, 1.1), tgt, lens=60, fstop=1.6)
    finish('b2_hands', layers)


# ---------------------------------------------------------------- golden-hour memory (temple)
MJ_SPOT = (-6.0, -3.1)          # west courtyard wall top, the pagoda + sunset behind her


def cam_basis(eye, target):
    f = (Vector(target) - Vector(eye)).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    return f, r, u


def near_lens(eye, target, dist, right, up):
    f, r, u = cam_basis(eye, target)
    return Vector(eye) + f * dist + r * right + u * up


def mj_face(meshes):
    lo, hi = CA.world_bbox(meshes)
    return Vector(((lo.x + hi.x) / 2 + 0.05, (lo.y + hi.y) / 2, hi.z - 0.13))


@shot
def c1_temple(layers=('bg', 'hero', 'fg')):
    W.reset(48)
    env_temple()
    gx, gy = MJ_SPOT
    gz = ground(gx, gy)
    mary_jane((gx, gy, gz), rot_z=90)
    tgt = Vector((gx, gy, gz + 0.7))
    eye = pick_eye(tgt, -20, 18, 6.0)
    rose(near_lens(eye, tgt, 0.7, -0.28, -0.24), rot=(20, 40, 10), height=0.45, cname='fg')
    W.camera(eye, tgt, lens=32, fstop=2.0, focus=(Vector(tgt) - Vector(eye)).length)
    finish('c1_temple', layers)


@shot
def c2_mj_portrait(layers=('full',)):
    W.reset(64)
    env_temple(fogd=0.016)
    gx, gy = MJ_SPOT
    gz = ground(gx, gy)
    meshes, root = mary_jane((gx, gy, gz), rot_z=90)
    face = mj_face(meshes)
    W.area((face.x + 1.0, face.y - 0.9, face.z + 0.35), face, (1.0, 0.8, 0.66), 45, size=1.0, name='softkey')
    W.camera((face.x + 0.95, face.y - 0.42, face.z - 0.04), face, lens=85, fstop=1.6)
    finish('c2_mj_portrait', layers)


@shot
def c3_together(layers=('anim',)):
    """Spidey crouched beside Mary Jane on the temple wall - slow real 3D orbit."""
    W.reset(24)
    env_temple(fogd=0)
    gx, gy = MJ_SPOT
    gz = ground(gx, gy)
    mary_jane((gx, gy, gz), rot_z=90)
    sx, sy = gx + 0.05, gy - 1.3
    spidey('crouch', (sx, sy, ground(sx, sy)), rot_z=90, look_yaw=32, look_pitch=-2)
    c = Vector((gx + 0.1, gy - 0.65, gz + 0.65))
    cam = W.camera((c.x + 3, c.y, c.z), c, lens=40, fstop=2.4)
    keys = []
    for i, f in enumerate((1, 46, 90)):
        a = math.radians(-38 + 30 * i)
        keys.append((f, (c.x + math.cos(a) * 3.3, c.y + math.sin(a) * 3.3, c.z - 0.35 + 0.1 * i), c))
    key_cam(cam, keys)
    animate_render('c3_together', 90)


@shot
def d1_lasso(layers=('anim',)):
    W.reset(32)
    env_void()
    meshes, root = prop('lasso-of-truth/source/unz/Lasso of Truth Replica.fbx', 0.9, (0, 0, 1.3), (80, 0, 0), name='lasso')
    gold = W.plain('lassogold', (1.0, 0.62, 0.22), 0.25, 1.0)
    gold.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1.0, 0.55, 0.15, 1)
    gold.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.5
    for o in meshes:
        o.data.materials.clear()
        o.data.materials.append(gold)
    pv = pivot(root, meshes, 'lassopivot')
    pv.location = (0, 0, 1.3)
    for f, rz, rx in ((1, 0, 80), (78, 200, 60)):
        pv.rotation_euler = (math.radians(rx), 0, math.radians(rz))
        pv.keyframe_insert('rotation_euler', frame=f)
    W.area((1.5, 1.5, 2.5), (0, 0, 1.3), RED, 400, size=1, name='rimR')
    W.area((-1.8, 1.2, 1.8), (0, 0, 1.3), (0.2, 0.4, 1.0), 400, size=1, name='rimB')
    W.spot((0, -2, 4), (0, 0, 1.3), (1, 0.9, 0.8), 600, 25, name='top')
    W.camera((0, -2.6, 1.35), (0, 0, 1.3), lens=50, fstop=2.8)
    animate_render('d1_lasso', 78)


@shot
def d2_dagger(layers=('anim',)):
    W.reset(32)
    env_void()
    meshes, root = prop('gladius-one-truth-can-puncture-a-thousand-lies/source/252_Weapon.fbx', 1.1, (0, 0, 1.3), (0, 0, 0),
                        name='gladius', bind=('gladius-one-truth-can-puncture-a-thousand-lies/textures', [('', '')]),
                        fit_max=True)
    piv = bpy.data.objects.new('gpivot', None)
    bpy.context.scene.collection.objects.link(piv)
    piv.location = (0, 0, 1.3)
    root.parent = piv
    root.location = Vector(root.location) + Vector((0, 0, -1.3))
    piv.rotation_mode = 'XYZ'
    for f, rz, rx in ((1, -35, 70), (60, 35, 82)):
        piv.rotation_euler = (math.radians(rx), 0, math.radians(rz))
        piv.keyframe_insert('rotation_euler', frame=f)
    W.area((1.2, 1.0, 2.0), (0, 0, 1.3), RED, 500, size=0.4, name='rimR')
    W.area((-1.4, 0.8, 1.6), (0, 0, 1.3), (0.2, 0.4, 1.0), 500, size=0.4, name='rimB')
    W.area((0.2, -1.4, 2.6), (0, 0, 1.2), (1, 0.95, 0.9), 120, size=0.2, name='glint')
    W.camera((0.2, -2.4, 1.35), (0, 0, 1.3), lens=55, fstop=2.8)
    animate_render('d2_dagger', 60)


@shot
def d4_goblin(layers=('full',)):
    W.reset(48)
    env_void(0.008)
    meshes, root = goblin((0, 0, 0.6), rot_z=-15, height=2.4)
    for o in meshes:
        if 'norman' in o.name.lower():
            o.hide_render = True
    W.area((0.5, 2.0, 3.2), (0, 0, 1.8), RED, 700, size=1.5, name='rimR')
    W.area((-2.0, 1.5, 1.0), (0, 0, 1.5), (0.1, 1.0, 0.25), 120, size=1.0, name='greenrim')
    W.area((0.6, -2.0, 0.2), (0, 0, 2.0), (1.0, 0.4, 0.2), 30, size=1.0, name='under')
    W.camera((0.6, -4.2, 0.9), (0, 0, 2.0), lens=40, fstop=2.2)
    finish('d4_goblin', layers)


@shot
def e1_bomb(layers=('anim',)):
    W.reset(32)
    env_void()
    meshes, root = prop('spiderman-green-goblin-pumpkin-bomb/source/Gobbo bomb 2 final .fbx', 0.35, (0, 3.0, 1.4), (0, 0, 0),
                        name='bomb', fit_max=True)
    pv = pivot(root, meshes, 'bombpivot')
    for f, y, rz, rx in ((1, 3.0, 0, 0), (54, -0.75, 540, 160)):
        pv.location = (0.05, y, 1.4)
        pv.rotation_euler = (math.radians(rx), 0, math.radians(rz))
        pv.keyframe_insert('location', frame=f)
        pv.keyframe_insert('rotation_euler', frame=f)
    W.area((1.2, 1.5, 2.5), (0, 1, 1.4), RED, 500, size=1.0, name='rimR')
    W.area((-1.4, 1.2, 1.6), (0, 1, 1.4), (0.2, 0.4, 1.0), 300, size=1.0, name='rimB')
    W.point((0, 3.5, 1.4), (1.0, 0.4, 0.1), 40, 0.1, name='fuse')
    W.camera((0, -1.6, 1.4), (0, 2, 1.4), lens=35, fstop=2.8)
    animate_render('e1_bomb', 54)


@shot
def e3_kneel(layers=('bg', 'hero')):
    W.reset(48)
    env_ruins(fogd=0.016)
    x, y = 2.4, -2.4
    gz = ground(x, y)
    arm, meshes, root = spidey('kneel', (x, y, gz), rot_z=-20, wetness=1.0, head_down=35)
    W.area((x + 2.5, y - 2.5, gz + 2.0), (x, y, gz + 0.8), (0.55, 0.65, 1.0), 260, size=2, name='moonkey')
    W.area((x - 1.5, y + 1.8, gz + 1.2), (x, y, gz + 0.9), RED, 300, size=1, name='redrim')
    tgt = Vector((x - 0.1, y, gz + 0.8))
    W.camera(pick_eye(tgt, -50, 4, 4.0), tgt, lens=40, fstop=2.0)
    finish('e3_kneel', layers)


# ---------------------------------------------------------------- dawn burial + sunrise (landscape)
GRAVE = (4.0, -5.0)


def landscape_grave(dawn=True):
    env_land(sun_el=3 if dawn else 8, warm=0.7 if dawn else 1.0)
    gx, gy = GRAVE
    gz = ground(gx, gy)
    prop('major-general-f-f-minchin-1860-1922-cross/source/unz/Textured_mesh_1.obj', 1.25, (gx, gy + 0.9, gz - 0.05),
         (0, 0, 0), name='cross', cname='env')
    for i, (dx, dy) in enumerate(((-0.55, 0.45), (0.6, 0.35), (-0.3, 0.0))):
        prop('hw-xyz-damage-emotional/source/HW XYZ Damage (emotional).fbx', 0.16, (gx + dx, gy + dy, gz), (0, 0, 40 * i),
             name='candle', cname='env')
        W.point((gx + dx, gy + dy, gz + 0.22), (1.0, 0.55, 0.2), 6, 0.02, name='flame')
    return gx, gy, gz


@shot
def f1_grave(layers=('bg', 'hero', 'fg')):
    W.reset(48)
    gx, gy, gz = landscape_grave()
    spidey('kneel', (gx + 0.1, gy - 0.55, gz), rot_z=180, reach=0.6, head_down=30)
    frame((gx - 0.05, gy + 0.35, gz + 0.1), rot=(75, 0, 180), height=0.28, photo=PHOTO if os.path.exists(PHOTO) else None)
    tgt = Vector((gx, gy + 0.15, gz + 0.62))
    eye = pick_eye(tgt, 200, 4, 2.7)
    rose(near_lens(eye, tgt, 0.55, -0.24, -0.2), rot=(0, 70, 30), height=0.45, cname='fg')
    W.area((gx - 2.0, gy - 1.5, gz + 1.5), (gx, gy, gz + 0.6), (0.6, 0.7, 1.0), 120, size=2, name='dawnfill')
    W.camera(eye, tgt, lens=35, fstop=1.8)
    finish('f1_grave', layers)


@shot
def f2_rose(layers=('full',)):
    W.reset(48)
    gx, gy, gz = landscape_grave()
    arm, meshes, root = spidey('kneel', (gx + 0.1, gy - 0.55, gz), rot_z=180, reach=1.0, head_down=40)
    w = bone_w(arm, 'wrist_r')
    rose((w.x, w.y + 0.02, w.z - 0.16), rot=(80, 0, 200), height=0.40)
    W.area((w.x - 0.8, w.y - 0.8, w.z + 0.8), w, (0.65, 0.72, 1.0), 40, size=1, name='fill')
    tgt = Vector((w.x, w.y + 0.1, gz + 0.14))
    W.camera(pick_eye(tgt, 190, 8, 0.85), tgt, lens=50, fstop=1.6)
    finish('f2_rose', layers)


@shot
def g1_sunrise(layers=('anim',)):
    """Hero stands on the hill facing the sunrise; the camera orbits round from behind him (real 3D)."""
    W.reset(24)
    env_land(sun_el=6, fogd=0, warm=1.0)
    x, y = HILL
    gz = ground(x, y, top=80)
    arm, meshes, root = spidey('stand', (x, y, gz), rot_z=135, head_pitch=8)
    c = Vector((x, y, gz + 1.15))
    cam = W.camera((x, y - 4, gz + 1.5), c, lens=35, fstop=2.8)
    keys = []
    for i, f in enumerate((1, 60, 120)):
        a = math.radians(-150 + 40 * i)
        keys.append((f, (c.x + math.cos(a) * (4.5 - 0.6 * i), c.y + math.sin(a) * (4.5 - 0.6 * i), c.z + 0.2 + 0.25 * i), c))
    key_cam(cam, keys)
    animate_render('g1_sunrise', 120)


HILL = (2.0, 37.0)


@shot
def logo_spin(layers=('anim',)):
    W.reset(32)
    env_void()
    meshes, root = prop('miles-morales-spiderman-logo/source/unz/miles logo.stl', 0.9, (0, 0, 1.3), (0, 0, 0), name='logo',
                        fit_max=True)
    lo, hi = CA.world_bbox(meshes)
    print('logo dims', hi - lo)
    chrome = W.plain('logochrome', (0.9, 0.05, 0.04), 0.18, 1.0)
    for o in meshes:
        o.data.materials.clear()
        o.data.materials.append(chrome)
    root.rotation_mode = 'XYZ'
    piv = bpy.data.objects.new('lpivot', None)
    bpy.context.scene.collection.objects.link(piv)
    piv.location = (0, 0, 1.3)
    root.parent = piv
    root.location = Vector(root.location) + Vector((0, 0, -1.3))
    piv.rotation_mode = 'XYZ'
    for f, rz in ((1, -400), (60, -180)):
        piv.rotation_euler = (0, 0, math.radians(rz))
        piv.keyframe_insert('rotation_euler', frame=f)
    W.area((1.5, 1.0, 2.5), (0, 0, 1.3), (1, 0.9, 0.85), 500, size=2, name='key')
    W.area((-1.8, 1.2, 1.0), (0, 0, 1.3), (0.2, 0.4, 1.0), 400, size=1, name='rimB')
    W.camera((0, -2.8, 1.3), (0, 0, 1.3), lens=50, fstop=4)
    animate_render('logo_spin', 60)



# ================================================================== animated hero shots (v2: real camera motion)
def keyed_light(light, keys, attr='energy'):
    """keys: [(frame, value)] with CONSTANT steps (lightning) or smooth (pulses)."""
    for f, v in keys:
        setattr(light.data, attr, v)
        light.data.keyframe_insert(attr, frame=f)
    ad = light.data.animation_data
    if ad and ad.action:
        for fc in _fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def floating_photos(center, n=10, seed=4, spread=(2.6, 2.6, 1.6), frames=132):
    """Real 3D polaroids (memory photos) drifting around the hero."""
    rnd = random.Random(seed)
    srcs = [p for p in (OUT + '/c2_mj_portrait_full.png', OUT + '/c1_temple_bg.png') if os.path.exists(p)]
    if not srcs:
        return
    mats = [photo_mat(p, 0.35) for p in srcs]
    white = W.plain('polaroidwhite', (0.85, 0.83, 0.8), 0.6)
    for i in range(n):
        bpy.ops.mesh.primitive_plane_add(size=1)
        card = bpy.context.object
        card.scale = (0.26, 0.32, 1)
        card.data.materials.append(white)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.035, 0.001))
        pic = bpy.context.object
        pic.scale = (0.23, 0.23, 1)
        pic.data.materials.append(mats[i % len(mats)])
        pic.parent = card
        pic.location = (0, 0.035 / 0.32, 0.002)
        c = Vector(center) + Vector((rnd.uniform(-1, 1) * spread[0], rnd.uniform(-1, 1) * spread[1],
                                     rnd.uniform(-0.3, 1) * spread[2]))
        r0 = Vector((rnd.uniform(40, 130), rnd.uniform(-40, 40), rnd.uniform(0, 360)))
        for f, k in ((1, 0.0), (frames, 1.0)):
            card.location = c + Vector((0.15, -0.1, -0.35)) * k
            card.rotation_euler = tuple(math.radians(a) for a in (r0 + Vector((25, 40, 60)) * k))
            card.keyframe_insert('location', frame=f)
            card.keyframe_insert('rotation_euler', frame=f)
        put([card], 'hero')


def project_track(cam, point, frames, path):
    """Per-frame canvas position (1080x1920 px) of a world point, for compositor tracking (HUD reticle)."""
    import json
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    out = {}
    for f in range(1, frames + 1):
        sc.frame_set(f)
        co = world_to_camera_view(sc, cam, Vector(point))
        out[f] = (co.x * 1080, (1 - co.y) * 1920, co.z)
    json.dump(out, open(path, 'w'))


@shot
def h1_hook(layers=('anim',)):
    """HOOK: camera rushes through the rain-dark ruins and arcs round the crouched hero, lightning strikes,
    memory photos float through the frame -> ends on the mask (132 frames @60)."""
    W.reset(20)
    env_ruins(fogd=0.016)
    gx, gy = HERO_RUINS
    gz = ground(gx, gy)
    arm, meshes, root = spidey('crouch', (gx, gy, gz), rot_z=15, wetness=1.0, look_pitch=4, look_yaw=-8)
    head = bone_w(arm, 'head')
    floating_photos(head + Vector((0, -1.2, -0.2)), n=12, frames=132)
    # lightning: a huge cold area light behind the ruins, double strike + a late flash
    flash = W.area((gx - 6, gy + 14, gz + 18), (gx, gy, gz), (0.6, 0.72, 1.0), 0, size=20, name='lightning')
    keyed_light(flash, [(1, 0), (3, 26000), (6, 2000), (9, 30000), (13, 0), (70, 0), (72, 22000), (76, 0), (132, 0)])
    red = W.area((gx + 2.5, gy - 0.5, gz + 0.4), (gx, gy, gz + 0.6), RED, 300, size=1.0, name='redpulse')
    keyed_light(red, [(f, 260 + 160 * math.sin(f * 0.35)) for f in range(1, 133, 6)])
    W.area((head.x - 1.0, head.y + 1.3, head.z + 0.8), head, MOON, 300, size=0.9, name='rim')
    cam = W.camera((gx - 3, gy - 9, gz + 0.5), head, lens=30, fstop=2.0)
    tgt_keys = []
    k1 = pick_eye(head, -112, 7, 8.5)
    k2 = pick_eye(head, -96, 9, 4.4)
    k3 = pick_eye(head, -78, 2, 2.1)
    keys = [(1, tuple(k1), head + Vector((0, 0, -0.35))),
            (50, tuple(k2), head + Vector((0, 0, -0.12))),
            (100, tuple(k3), head),
            (132, (head.x + 0.35, head.y - 1.05, head.z - 0.02), head)]
    tgt = key_cam(cam, keys)
    cam.data.dof.focus_object = None
    cam.data.dof.focus_distance = 5.0
    for f, d in ((1, 9.5), (50, 4.8), (100, 2.4), (132, 1.1)):
        cam.data.dof.focus_distance = d
        cam.data.dof.keyframe_insert('focus_distance', frame=f)
    cam.data.lens = 30
    cam.data.keyframe_insert('lens', frame=1)
    cam.data.lens = 42
    cam.data.keyframe_insert('lens', frame=132)
    project_track(cam, head, 132, OUT + '/h1_hook_head.json')
    animate_render('h1_hook', 132)


@shot
def e3_anim(layers=('anim',)):
    """Grief in the rain: slow arc + push towards the kneeling hero (90 frames @60)."""
    W.reset(20)
    env_ruins(fogd=0.016)
    x, y = KNEEL_RUINS
    gz = ground(x, y)
    arm, meshes, root = spidey('kneel', (x, y, gz), rot_z=-20, wetness=1.0, head_down=35)
    W.area((x + 2.5, y - 2.5, gz + 2.0), (x, y, gz + 0.8), (0.55, 0.65, 1.0), 260, size=2, name='moonkey')
    red = W.area((x - 1.5, y + 1.8, gz + 1.2), (x, y, gz + 0.9), RED, 300, size=1, name='redrim')
    keyed_light(red, [(f, 200 + 220 * (0.5 + 0.5 * math.sin(f * 0.21))) for f in range(1, 91, 5)])
    tgt = Vector((x - 0.1, y, gz + 0.8))
    e0 = pick_eye(tgt, -70, 6, 4.4)
    e1 = pick_eye(tgt, -38, 3, 2.6)
    cam = W.camera(e0, tgt, lens=40, fstop=2.0)
    key_cam(cam, [(1, tuple(e0), tgt), (90, tuple(e1), tgt)])
    cam.data.dof.focus_object = None
    for f, d in ((1, (e0 - tgt).length), (90, (e1 - tgt).length)):
        cam.data.dof.focus_distance = d
        cam.data.dof.keyframe_insert('focus_distance', frame=f)
    animate_render('e3_anim', 90)


@shot
def f1_anim(layers=('anim',)):
    """Dawn burial: low dolly across the candles towards the kneeling hero (90 frames @60)."""
    W.reset(20)
    gx, gy, gz = landscape_grave()
    spidey('kneel', (gx + 0.1, gy - 0.55, gz), rot_z=180, reach=0.6, head_down=30)
    frame((gx - 0.05, gy + 0.35, gz + 0.1), rot=(75, 0, 180), height=0.28, photo=PHOTO if os.path.exists(PHOTO) else None)
    tgt = Vector((gx, gy + 0.15, gz + 0.62))
    e0 = pick_eye(tgt, 215, 3, 3.0)
    e1 = pick_eye(tgt, 190, 5, 2.0)
    rose(near_lens(e0, tgt, 0.55, -0.24, -0.2), rot=(0, 70, 30), height=0.45, cname='fg')
    W.area((gx - 2.0, gy - 1.5, gz + 1.5), (gx, gy, gz + 0.6), (0.6, 0.7, 1.0), 120, size=2, name='dawnfill')
    cam = W.camera(e0, tgt, lens=35, fstop=1.8)
    key_cam(cam, [(1, tuple(e0), tgt), (90, tuple(e1), tgt)])
    cam.data.dof.focus_object = None
    for f, d in ((1, (e0 - tgt).length), (90, (e1 - tgt).length)):
        cam.data.dof.focus_distance = d
        cam.data.dof.keyframe_insert('focus_distance', frame=f)
    animate_render('f1_anim', 90)


if __name__ == '__main__':
    name = sys.argv[1]
    if len(sys.argv) > 2:
        SHOTS[name](layers=tuple(sys.argv[2].split(',')))
    else:
        SHOTS[name]()
