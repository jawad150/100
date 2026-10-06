"""Realistic MakeHuman (MPFB) characters for the Yaadein plates, posed with IK.

Imported from scenes.py inside Blender (bpy). The MPFB extension and the
MakeHuman asset packs (system assets, shirts02, pants01, poses01) must be
installed in the Blender user config.
"""
import math

import bpy
from mathutils import Matrix, Vector

from bl_ext.user_default.mpfb.services.humanservice import HumanService


def make(name, gender=1.0, age=0.5, muscle=0.6, weight=0.45, height=0.55, proportions=0.7,
         skin='young_asian_male', hair='short04', clothes=('elvs_hooded_sweat_jacket1', 'cortu_cargo_pants', 'shoes06'),
         eyebrows='eyebrow001', race=(0.55, 0.3, 0.15)):
    info = HumanService._create_default_human_info_dict()
    info['name'] = name
    info['phenotype'].update(gender=gender, age=age, muscle=muscle, weight=weight, height=height,
                             proportions=proportions, cupsize=0.5, firmness=0.5)
    info['phenotype']['race'] = dict(asian=race[0], caucasian=race[1], african=race[2])
    info['rig'] = 'game_engine'
    info['eyes'] = 'high-poly.mhclo'
    info['eyebrows'] = eyebrows + '.mhclo'
    info['eyelashes'] = 'eyelashes01.mhclo'
    info['hair'] = (hair + '.mhclo') if hair else ''
    info['clothes'] = [c + '.mhclo' for c in clothes]
    info['skin_mhmat'] = skin + '.mhmat'
    info['skin_material_type'] = 'ENHANCED_SSS'
    info['eyes_material_type'] = 'MAKESKIN'
    st = HumanService.get_default_deserialization_settings()
    st['subdiv_levels'] = 1
    body = HumanService.deserialize_from_dict(info, st)
    rig = body.parent
    for o in [rig] + list(rig.children_recursive):
        o['human'] = name
    return rig


def _upd():
    bpy.context.view_layer.update()


def rot(rig, bone, axis, deg):
    """Rotate a pose bone about its head, around an armature-space axis (x right, y back, z up)."""
    pb = rig.pose.bones[bone]
    head = pb.head.copy()
    R = Matrix.Rotation(math.radians(deg), 4, Vector(axis).normalized())
    pb.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ pb.matrix
    _upd()


def ik(rig, bone, target, pole=None, chain=2, pole_angle=None):
    """IK the chain ending at `bone` (lowerarm_x / calf_x) to world points."""
    def empty(nm, p):
        e = bpy.data.objects.new(nm, None)
        bpy.context.scene.collection.objects.link(e)
        e.location = p
        return e
    c = rig.pose.bones[bone].constraints.new('IK')
    c.target = empty(rig.name + '.' + bone + '.tgt', target)
    c.chain_count = chain
    if pole is not None:
        c.pole_target = empty(rig.name + '.' + bone + '.pole', pole)
        c.pole_angle = math.radians(-90 if pole_angle is None else pole_angle)
    _upd()
    return c


def bone_world(rig, bone, tail=False):
    pb = rig.pose.bones[bone]
    return rig.matrix_world @ (pb.tail if tail else pb.head)


def place(rig, loc, rot_z=0.0):
    rig.location = loc
    rig.rotation_euler = (0, 0, math.radians(rot_z))
    _upd()


def dark_clothes(rig, tint=(0.035, 0.034, 0.036), rough=0.85):
    """Re-tint clothing towards near black so it reads in silhouette but keeps folds and sheen."""
    for o in rig.children_recursive:
        if o.type != 'MESH' or not o.material_slots:
            continue
        n = o.name.lower()
        if any(k in n for k in ('jacket', 'pants', 'shoe', 'suit', 'sweat', 'shirt', 'sweater')):
            for s in o.material_slots:
                m = s.material
                if not m or not m.use_nodes:
                    continue
                for nd in m.node_tree.nodes:
                    if nd.type == 'BSDF_PRINCIPLED':
                        tex = nd.inputs['Base Color'].links
                        if tex:
                            mix = m.node_tree.nodes.new('ShaderNodeMix')
                            mix.data_type = 'RGBA'
                            mix.blend_type = 'MULTIPLY'
                            mix.inputs['Factor'].default_value = 1.0
                            m.node_tree.links.new(tex[0].from_socket, mix.inputs['A'])
                            mix.inputs['B'].default_value = (*[t * 6 for t in tint], 1)
                            m.node_tree.links.new(mix.outputs['Result'], nd.inputs['Base Color'])
                        else:
                            nd.inputs['Base Color'].default_value = (*tint, 1)
                        nd.inputs['Roughness'].default_value = rough
