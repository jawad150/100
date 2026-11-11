"""Turntable renders: each 3D object spun through 360 degrees (36 frames), so the edit can show real 3D rotation.
Also glossy extruded 3D numerals 1-7.

Run: blender -b -P blender_spin.py -- [name ...]  -> workspace_nq/spin/<name>/000.png .. 035.png
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_three'))
import blender_tuned as B
import blender_three as B3
import blender_nqtok as BN

ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_nq/spin'
NFR = 24


def numeral(d):
    def f():
        m = B.mat(B.hexc('#FF6411'), 0.22, coat=0.8)
        t = B.text(str(d), 2.4, (0, 0, 0), m, ext=0.32, font='Nunito-900')
        t.data.bevel_depth = 0.06
        t.data.bevel_resolution = 4
    return f


TOK = {}
TOK.update(BN.TOK)
for k in ('gradcap', 'house', 'network', 'phone', 'clock', 'calendar', 'heart'):
    TOK[k] = B3.TOK[k]
for d in range(1, 8):
    TOK[f'n{d}'] = numeral(d)


def spin_render(name):
    B.reset()
    TOK[name]()
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = 420
    sc.cycles.samples = 16
    bpy.context.view_layer.update()
    objs = [o for o in sc.objects if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render]
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (lo + hi) / 2
    spin = bpy.data.objects.new('spin', None)
    sc.collection.objects.link(spin)
    spin.location = (ctr.x, ctr.y, 0)
    bpy.context.view_layer.update()
    inv = spin.matrix_world.inverted()
    for o in list(sc.objects):
        if o is spin or o.type in ('CAMERA', 'LIGHT') or o.parent is not None:
            continue
        mw = o.matrix_world.copy()
        o.parent = spin
        o.matrix_world = mw
    # radius that stays in frame for every angle
    rxy = max(math.hypot(p.x - ctr.x, p.y - ctr.y) for p in pts)
    hz = (hi.z - lo.z) / 2
    rad = math.sqrt(rxy ** 2 + hz ** 2) * 1.02
    cam = sc.camera
    d = rad / math.tan(cam.data.angle / 2) * 1.05
    fwd = Vector((0, math.sin(math.radians(71)), -math.cos(math.radians(71))))
    cam.location = Vector((ctr.x, ctr.y, ctr.z)) - fwd * d
    os.makedirs(f'{OUT}/{name}', exist_ok=True)
    for i in range(NFR):
        spin.rotation_euler = (0, 0, math.radians(i * 360 / NFR))
        sc.render.filepath = f'{OUT}/{name}/{i:03d}.png'
        bpy.ops.render.render(write_still=True)
    print('spun', name, flush=True)


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for n in (argv or list(TOK)):
        if os.path.exists(f'{OUT}/{n}/{NFR - 1:03d}.png'):
            continue
        spin_render(n)
