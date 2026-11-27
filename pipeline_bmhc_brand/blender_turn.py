"""360-degree turntables of the BMHC 3D objects (lantern, radio, rings, ball) for the moving carousel.
Reuses the builders in pipeline_bmhc_posts/blender_bento.py. Run: blender -b -P blender_turn.py -- name [name...]
-> workspace_brandcar/turn/<name>/0000..0047.png (RGBA)"""
import bpy, sys, os, math, importlib.util
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
names = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['lantern']
saved = sys.argv
sys.argv = ['blender', '--', 'draft', '__none__']                  # load the builders without rendering anything
spec = importlib.util.spec_from_file_location('bento', os.path.join(ROOT, 'pipeline_bmhc_posts', 'blender_bento.py'))
bento = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bento)
sys.argv = saved
B = bento.B
NF = 48
for name in names:
    bento.reset()
    sc = bpy.context.scene
    sc.cycles.samples = 28
    sc.render.resolution_x = sc.render.resolution_y = 520
    getattr(bento, name)()
    B.frame_all()
    cam = sc.camera
    cam.location = cam.location + (cam.location - Vector((0, 0, 1.2))) * 0.3          # extra room for the spin
    g = [o for o in sc.objects if o.type == 'EMPTY'][0]
    base = g.rotation_euler.z
    out = f'{ROOT}/workspace_brandcar/turn/{name}'
    os.makedirs(out, exist_ok=True)
    for f in range(NF):
        g.rotation_euler.z = base + 2 * math.pi * f / NF
        sc.render.filepath = f'{out}/{f:04d}.png'
        bpy.ops.render.render(write_still=True)
    print('turntable', name, flush=True)
