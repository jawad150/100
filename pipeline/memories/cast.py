"""The user's character / prop assets (Google Drive 'spiderman' folder), loaded into clean, posable form.

Every character is normalised to: armature at the origin with identity transform, metres, Z up, feet on
z=0, facing -Y. Poses are built with world-axis bone rotations (human.rot) plus IK chains, so the same
pose recipes work on any of the rigs through a bone-name map.
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

X = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace2', 'assets',
                                 'drive', 'x'))

RAIMI = dict(hips='GLTF_created_0_rootJoint', spine='Spine_51', chest='Chest_50', upper_chest='Upper Chest_49',
             neck='Neck_29', head='Head_28',
             shoulder_l='Left shoulder_27', arm_l='Left arm_26', elbow_l='Left elbow_25', wrist_l='Left wrist_24',
             shoulder_r='Right shoulder_48', arm_r='Right arm_47', elbow_r='Right elbow_46', wrist_r='Right wrist_45',
             leg_l='Left leg_4', knee_l='Left knee_3', ankle_l='Left ankle_2', toe_l='Left toe_1',
             leg_r='Right leg_8', knee_r='Right knee_7', ankle_r='Right ankle_6', toe_r='Right toe_5')


def fbx_light_fix():
    """Blender 5.0's FBX importer still writes light.cycles.cast_shadow (removed from Cycles): patch it out."""
    import inspect
    import io_scene_fbx.import_fbx as F
    if not getattr(F, '_yaadein_patched', False):
        src = inspect.getsource(F.blen_read_light).replace('lamp.cycles.cast_shadow = lamp.use_shadow', 'pass')
        exec(src, F.__dict__)
        F._yaadein_patched = True


def _import(path):
    before = set(bpy.data.objects)
    if path.endswith('.fbx'):
        fbx_light_fix()
        bpy.ops.import_scene.fbx(filepath=path)
    elif path.endswith(('.glb', '.gltf')):
        bpy.ops.import_scene.gltf(filepath=path)
    elif path.endswith('.obj'):
        bpy.ops.wm.obj_import(filepath=path)
    elif path.endswith('.stl'):
        bpy.ops.wm.stl_import(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def _select(objs, active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def world_bbox(objs):
    """World bbox of the *evaluated* (deformed) meshes."""
    dg = bpy.context.evaluated_depsgraph_get()
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != 'MESH':
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        n = len(me.vertices)
        if n:
            import numpy as np
            co = np.empty(n * 3, np.float32)
            me.vertices.foreach_get('co', co)
            co = co.reshape(-1, 3)
            M = np.array(ev.matrix_world)
            w = co @ M[:3, :3].T + M[:3, 3]
            lo = Vector(np.minimum(np.array(lo), w.min(0)))
            hi = Vector(np.maximum(np.array(hi), w.max(0)))
        ev.to_mesh_clear()
    return lo, hi


def normalise(new, height=None, face_rot=0.0, name='char'):
    """Keep the imported hierarchy; parent its top objects to a root empty that is scaled/moved so the
    model stands on z=0, centred, `height` tall, rotated by face_rot. Returns (armature, meshes, root)."""
    newset = set(new)
    tops = [o for o in new if o.parent not in newset]
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for o in tops:
        mw = o.matrix_world.copy()
        o.parent = root
        o.matrix_world = mw
    meshes = [o for o in new if o.type == 'MESH']
    arms = [o for o in new if o.type == 'ARMATURE']
    bpy.context.view_layer.update()
    lo, hi = world_bbox(meshes)
    s = (height / (hi.z - lo.z)) if height else 1.0
    c = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    root.matrix_world = Matrix.Rotation(math.radians(face_rot), 4, 'Z') @ Matrix.Scale(s, 4) @ Matrix.Translation(-c)
    bpy.context.view_layer.update()
    root['height'] = height or (hi.z - lo.z)
    return (arms[0] if arms else None), meshes, root


def raimi(height=1.78, name='spidey'):
    """Accurate Raimi suit (CC-BY ScruffyMcducky) - textured and rigged."""
    new = _import(X + '/symbiote-spiderman-tobey-maguire/source/unz/scene.gltf')
    for o in list(new):
        if o.name.startswith('Icosphere'):
            bpy.data.objects.remove(o)
            new.remove(o)
    arm, meshes, root = normalise(new, height, name=name)
    for b in arm.pose.bones:
        b.rotation_mode = 'XYZ'
    return arm, meshes, root


def mary_jane(height=1.15, name='mj'):
    """Crouching statue (includes its plinth); height is of the whole statue."""
    new = _import(X + '/mary-jane-spiderman/source/spider woman.glb')
    return normalise(new, height, name=name)


def goblin(height=1.85, name='goblin', glider=True):
    new = _import(X + '/green-goblin-2002/source/greengoblin.fbx')
    tex = X + '/green-goblin-2002/textures/'
    for m in {s.material for o in new if o.type == 'MESH' for s in o.material_slots if s.material}:
        img = {'goblin': 'bodygoblin.png', 'norman': 'norman.png', 'glider': 'glider.png'}.get(m.name)
        if img:
            nt = m.node_tree
            t = nt.nodes.new('ShaderNodeTexImage')
            t.image = bpy.data.images.load(tex + img, check_existing=True)
            nt.links.new(t.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    keep = [o for o in new if o.type in ('MESH', 'ARMATURE')]
    bomb_parts = [o for o in keep if o.name.split('.')[0] in ('Bomb', 'Lights', 'Ring', 'Light', 'Shell')]
    for o in bomb_parts:
        bpy.data.objects.remove(o)
    new = [o for o in new if o.name in bpy.data.objects and bpy.data.objects[o.name] == o] if False else \
        [o for o in bpy.data.objects if o in set(new)]
    if not glider:
        for o in list(new):
            if 'glider' in o.name.lower() or o.name.startswith('Glider'):
                bpy.data.objects.remove(o)
        new = [o for o in bpy.data.objects if o in set(new)]
    return new


def prop(rel, height=None, name=None, face_rot=0.0):
    """Static prop from the Drive folder (path relative to drive/x)."""
    new = _import(X + '/' + rel)
    return normalise(new, height, face_rot=face_rot, name=name or os.path.basename(rel))


# ---------------------------------------------------------------- posing
def upd():
    bpy.context.view_layer.update()


def _ax(arm, v):
    """world direction -> armature space direction."""
    return (arm.matrix_world.inverted().to_3x3() @ Vector(v)).normalized()


def _pt(arm, p):
    return arm.matrix_world.inverted() @ Vector(p)


def rot(arm, bone, axis, deg):
    """Rotate a pose bone about its head around a WORLD axis (x right, y back, z up for a -Y facing rig)."""
    pb = arm.pose.bones[bone]
    head = pb.head.copy()
    R = Matrix.Rotation(math.radians(deg), 4, _ax(arm, axis))
    pb.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ pb.matrix
    upd()


def aim(arm, bone, direction, up_hint=None):
    """Rotate bone (about its head) so it points along a world direction (minimal rotation)."""
    pb = arm.pose.bones[bone]
    cur = (pb.tail - pb.head).normalized()
    d = _ax(arm, direction)
    q = cur.rotation_difference(d)
    head = pb.head.copy()
    pb.matrix = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head) @ pb.matrix
    upd()


def chain_to(arm, upper, lower, end, target, pole):
    """Analytic two-bone IK in armature space: place `end` bone head at target, knee/elbow toward pole."""
    pu, pl = arm.pose.bones[upper], arm.pose.bones[lower]
    mw = arm.matrix_world
    a = mw @ pu.head
    l1 = (mw @ pl.head - a).length
    l2 = (mw @ arm.pose.bones[end].head - mw @ pl.head).length
    t = Vector(target)
    d = t - a
    dist = min(d.length, (l1 + l2) * 0.999)
    d.normalize()
    # elbow position in the plane of (d, pole)
    p = Vector(pole) - a
    n = (p - d * p.dot(d)).normalized()
    cos_a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    cos_a = max(-1.0, min(1.0, cos_a))
    sin_a = math.sqrt(1 - cos_a * cos_a)
    elbow = a + d * (l1 * cos_a) + n * (l1 * sin_a)
    aim(arm, upper, elbow - a)
    aim(arm, lower, (a + d * dist) - mw @ arm.pose.bones[lower].head)


def look(arm, M, yaw=0.0, pitch=0.0, roll=0.0, neck_share=0.4):
    """pitch > 0 looks UP, yaw > 0 turns to the character's left (screen right when facing camera)."""
    for b, k in ((M['neck'], neck_share), (M['head'], 1 - neck_share)):
        rot(arm, b, (0, 0, 1), yaw * k)
        rot(arm, b, (1, 0, 0), -pitch * k)
        rot(arm, b, (0, 1, 0), roll * k)


def bend_spine(arm, M, fwd=0.0, side=0.0, twist=0.0):
    """fwd > 0 bends forward (towards -Y)."""
    for b, k in ((M['spine'], 0.4), (M['chest'], 0.35), (M['upper_chest'], 0.25)):
        rot(arm, b, (1, 0, 0), fwd * k)
        rot(arm, b, (0, 1, 0), side * k)
        rot(arm, b, (0, 0, 1), twist * k)


def hips_to(arm, M, z=None, dx=0.0, dy=0.0, pitch=0.0, yaw=0.0):
    """Move/rotate the hips bone in armature space (whole upper body + legs follow)."""
    pb = arm.pose.bones[M['hips']]
    mw = arm.matrix_world
    head_w = mw @ pb.head
    goal = Vector((head_w.x + dx, head_w.y + dy, head_w.z if z is None else z))
    delta = mw.inverted().to_3x3() @ (goal - head_w)
    m = pb.matrix.copy()
    m.translation += delta
    pb.matrix = m
    upd()
    if pitch:
        rot(arm, M['hips'], (1, 0, 0), pitch)
    if yaw:
        rot(arm, M['hips'], (0, 0, 1), yaw)


def foot(arm, M, side, target, knee_pole, flat=True):
    chain_to(arm, M['leg_' + side], M['knee_' + side], M['ankle_' + side], target, knee_pole)
    if flat:
        aim(arm, M['ankle_' + side], Vector((0, -1, -0.5)))


def hand(arm, M, side, target, elbow_pole):
    chain_to(arm, M['arm_' + side], M['elbow_' + side], M['wrist_' + side], target, elbow_pole)


# ---------------------------------------------------------------- pose recipes (rig at origin facing -Y)
def pose_crouch(arm, M, hand_down='r', look_pitch=-10.0, look_yaw=0.0):
    """Iconic perched crouch: knees wide, torso pitched forward, one hand planted between the feet."""
    hips_to(arm, M, z=0.50, dy=0.10)
    bend_spine(arm, M, fwd=34)
    foot(arm, M, 'l', (0.24, -0.08, 0.07), (0.65, -0.9, 0.6))
    foot(arm, M, 'r', (-0.24, -0.04, 0.07), (-0.65, -0.9, 0.6))
    other = 'l' if hand_down == 'r' else 'r'
    sx = -1 if hand_down == 'r' else 1
    hand(arm, M, hand_down, (sx * 0.06, -0.30, 0.05), (sx * 0.5, 0.3, 0.6))
    hand(arm, M, other, (-sx * 0.30, -0.38, 0.52), (-sx * 0.6, 0.4, 0.8))
    look(arm, M, yaw=look_yaw, pitch=30 + look_pitch)


def pose_kneel(arm, M, reach=0.0, head_down=25.0):
    """Right knee on the ground, left foot planted forward; right hand reaching down (reach 0..1)."""
    hips_to(arm, M, z=0.52, dy=0.08)
    bend_spine(arm, M, fwd=12 + 22 * reach)
    foot(arm, M, 'l', (0.16, -0.38, 0.07), (0.3, -1.2, 0.6))
    chain_to(arm, M['leg_r'], M['knee_r'], M['ankle_r'], (-0.14, 0.42, 0.10), (-0.2, -0.8, 0.1))
    aim(arm, M['ankle_r'], (0, 0.6, -0.8))
    hand(arm, M, 'l', (0.24, -0.33, 0.52), (0.6, 0.3, 0.7))
    hand(arm, M, 'r', (-0.16 + 0.05 * reach, -0.32 - 0.18 * reach, 0.62 - 0.52 * reach), (-0.7, 0.4, 0.8))
    look(arm, M, pitch=-head_down)


def pose_sit_edge(arm, M, ledge_z=0.0, head_down=30.0):
    """Sitting on a ledge edge (ledge top at the rig's z=0 + hips height), legs hanging, photo in both hands."""
    hips_to(arm, M, z=0.10, dy=0.05)
    bend_spine(arm, M, fwd=20)
    foot(arm, M, 'l', (0.16, -0.52, -0.38), (0.25, -1.3, 0.4), flat=False)
    foot(arm, M, 'r', (-0.16, -0.50, -0.40), (-0.25, -1.3, 0.4), flat=False)
    hand(arm, M, 'l', (0.06, -0.40, 0.32), (0.6, 0.2, 0.2))
    hand(arm, M, 'r', (-0.06, -0.40, 0.32), (-0.6, 0.2, 0.2))
    look(arm, M, pitch=-head_down)


def pose_stand(arm, M, head_pitch=6.0, arms_out=8.0, weight=0.0):
    hips_to(arm, M, dx=0.03 * weight)
    for s, sg in (('l', 1), ('r', -1)):
        rot(arm, M['arm_' + s], (0, 1, 0), sg * (24 - arms_out))
        rot(arm, M['elbow_' + s], (1, 0, 0), 10)
    look(arm, M, pitch=head_pitch)


def pose_grief(arm, M):
    """Standing, shoulders slumped, head hung low."""
    bend_spine(arm, M, fwd=14)
    for s, sg in (('l', 1), ('r', -1)):
        rot(arm, M['arm_' + s], (0, 1, 0), sg * 26)
        rot(arm, M['shoulder_' + s], (1, 0, 0), 6)
    look(arm, M, pitch=-38)


# ---------------------------------------------------------------- texture binding for Sketchfab exports
_MAPS = (('BaseColor', 'albedo', 'Diffuse', '_D.', 'diff', 'color'), ('Normal', 'normal', '_N.'),
         ('Roughness', 'roughness', 'rough'), ('Metallic', 'Metalness', 'metallic', 'metal'),
         ('Emissive', 'emissive', 'Emission'), ('opacity', 'Opacity', 'alpha'), ('AmbientOcclusion', '_AO', 'AO.'))


def _find_maps(files, prefix):
    pre = [f for f in files if os.path.basename(f).lower().startswith(prefix.lower())]
    out = {}
    for key in _MAPS:
        for f in pre:
            b = os.path.basename(f)
            if any(k.lower() in b.lower() for k in key):
                out.setdefault(key[0], f)
    return out


def pbr_material(name, maps, emit_strength=4.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']

    def img(path, non_color=True):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(path, check_existing=True)
        if non_color:
            t.image.colorspace_settings.name = 'Non-Color'
        return t
    if 'BaseColor' in maps:
        t = img(maps['BaseColor'], False)
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if 'opacity' not in maps and t.image.depth in (32, 64) and maps['BaseColor'].endswith('.png'):
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    if 'Normal' in maps:
        t = img(maps['Normal'])
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(t.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if 'Roughness' in maps:
        t = img(maps['Roughness'])
        nt.links.new(t.outputs['Color'], b.inputs['Roughness'])
    if 'Metallic' in maps:
        t = img(maps['Metallic'])
        nt.links.new(t.outputs['Color'], b.inputs['Metallic'])
    if 'Emissive' in maps:
        t = img(maps['Emissive'], False)
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = emit_strength
    if 'opacity' in maps:
        t = img(maps['opacity'])
        nt.links.new(t.outputs['Color'], b.inputs['Alpha'])
    return m


def bind_textures(objs, texdir, rules):
    """rules: [(object-or-material name prefix, texture file prefix), ...] first match wins.
    Prefixes are matched against the object name, then the material name."""
    files = [os.path.join(texdir, f) for f in os.listdir(texdir)]
    cache = {}
    for o in objs:
        if o.type != 'MESH':
            continue
        for i, slot in enumerate(o.material_slots):
            mname = slot.material.name if slot.material else ''
            for pre, tpre in rules:
                if o.name.lower().startswith(pre.lower()) or mname.lower().startswith(pre.lower()):
                    if tpre not in cache:
                        cache[tpre] = pbr_material(tpre, _find_maps(files, tpre))
                    slot.material = cache[tpre]
                    break


def pose_kneel_hold(arm, M, head_down=32.0):
    """Kneeling on one knee, both hands holding something (the memory frame) at chest height."""
    hips_to(arm, M, z=0.52, dy=0.08)
    bend_spine(arm, M, fwd=18)
    foot(arm, M, 'l', (0.16, -0.38, 0.07), (0.3, -1.2, 0.6))
    chain_to(arm, M['leg_r'], M['knee_r'], M['ankle_r'], (-0.14, 0.42, 0.10), (-0.2, -0.8, 0.1))
    aim(arm, M['ankle_r'], (0, 0.6, -0.8))
    hand(arm, M, 'l', (0.11, -0.36, 0.92), (0.55, 0.1, 0.7))
    hand(arm, M, 'r', (-0.11, -0.36, 0.92), (-0.55, 0.1, 0.7))
    look(arm, M, pitch=-head_down)
