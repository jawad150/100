"""Quick turntable-style look renders of imported assets: python3 lookdev.py <file> <out.png> [yaw]"""
import math
import sys

import bpy
from mathutils import Vector


def fbx_light_fix():
    """Blender 5.0's FBX importer still writes light.cycles.cast_shadow (removed from Cycles): patch it out."""
    import inspect
    import io_scene_fbx.import_fbx as F
    if not getattr(F, '_yaadein_patched', False):
        src = inspect.getsource(F.blen_read_light).replace('lamp.cycles.cast_shadow = lamp.use_shadow', 'pass')
        exec(src, F.__dict__)
        F._yaadein_patched = True


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx_light_fix()
    if path.endswith('.blend'):
        bpy.ops.wm.open_mainfile(filepath=path)
        for o in list(bpy.context.scene.objects):
            if o.type in ('CAMERA', 'LIGHT'):
                bpy.data.objects.remove(o)
    elif path.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=path)
    elif path.endswith(('.glb', '.gltf')):
        bpy.ops.import_scene.gltf(filepath=path)
    elif path.endswith('.obj'):
        bpy.ops.wm.obj_import(filepath=path)
    elif path.endswith('.stl'):
        bpy.ops.wm.stl_import(filepath=path)


def bbox():
    pts = []
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and o.visible_get():
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def shoot(out, yaw=30, res=(540, 760)):
    sc = bpy.context.scene
    lo, hi = bbox()
    c = (lo + hi) / 2
    size = max((hi - lo).length, 1e-3)
    cam = bpy.data.objects.new('lookcam', bpy.data.cameras.new('lookcam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 50
    d = size * 1.45
    a = math.radians(yaw)
    cam.location = c + Vector((math.sin(a) * d, -math.cos(a) * d, size * 0.25))
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.clip_start, cam.data.clip_end = size * 0.01, size * 20
    for i, (off, e, col) in enumerate([((-1, -1, 1), 1.0, (1, 0.95, 0.9)), ((1.2, 0.6, 0.8), 0.8, (0.6, 0.75, 1.0)),
                                       ((0, 1.5, 0.4), 1.2, (1.0, 0.3, 0.25))]):
        l = bpy.data.objects.new(f'L{i}', bpy.data.lights.new(f'L{i}', 'AREA'))
        sc.collection.objects.link(l)
        l.location = c + Vector(off) * size
        l.rotation_euler = (c - l.location).to_track_quat('-Z', 'Y').to_euler()
        l.data.size = size * 0.8
        l.data.energy = e * 300 * size ** 2
        l.data.color = col
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.02, 0.02, 0.025, 1)
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 16
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = 'AgX'
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    load(sys.argv[1])
    shoot(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 30)
