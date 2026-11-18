"""Little 3D houses whose two round windows are eyes (the Organic Fostering twist on the 'eyes' carousel).

Run: blender -b -P blender_eyehouse.py -- name roof_hex gaze_x gaze_y [lean_deg] [wide]
     gaze in -1..1 (x right, y up); wide=1 makes the eyes bigger (surprised)
-> workspace_swipe/assets/<name>.png
"""
import bpy, sys, os, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_swipe/assets'
os.makedirs(B.OUT, exist_ok=True)


def eyehouse(roof, gx, gy, lean=0.0, wide=0):
    walls = box((2.2, 1.6, 1.7), loc=(0, 0, 0), m=mat(hexc('#FCF8F5'), 0.35, coat=0.3), bw=0.12)
    bpy.ops.mesh.primitive_cone_add(radius1=1.75, depth=1.15, vertices=4, location=(0, 0, 1.42), rotation=(0, 0, math.radians(45)))
    r = act()
    r.scale = (1.0, 0.82, 1)
    bpy.ops.object.transform_apply(scale=True)
    bevel(r, 0.08)
    smooth(r)
    setm(r, mat(hexc(roof), 0.28, coat=0.5))
    door = box((0.5, 0.1, 0.72), loc=(0, -0.81, -0.5), m=mat(hexc(roof), 0.3, coat=0.4), bw=0.06)
    knob = sph(0.04, loc=(0.14, -0.88, -0.5), m=mat(hexc('#E2A93B'), 0.25, 0.9))
    er = 0.47 if wide else 0.4
    for sx in (-0.55, 0.55):
        ring = cyl(er + 0.07, 0.1, loc=(sx, -0.8, 0.32), m=mat(hexc(roof), 0.3), rot=(math.radians(90), 0, 0), bw=0.03)
        white = sph(er, loc=(sx, -0.83, 0.32), m=mat(hexc('#FFFFFF'), 0.15, coat=1.0), scale=(1, 0.45, 1))
        px, pz = sx + gx * er * 0.48, 0.32 + gy * er * 0.48
        iris = sph(er * 0.55, loc=(px, -0.95, pz), m=mat(hexc('#6B3A1E'), 0.2, coat=1.0), scale=(1, 0.3, 1))
        pupil = sph(er * 0.32, loc=(px, -1.0, pz), m=mat(hexc('#140C10'), 0.1, coat=1.0), scale=(1, 0.25, 1))
        glint = sph(er * 0.1, loc=(px - er * 0.18, -1.05, pz + er * 0.18), m=mat(hexc('#FFFFFF'), 0.1, emit=(hexc('#FFFFFF'), 2.0)))
    chim = box((0.3, 0.3, 0.6), loc=(0.6, 0.2, 1.75), m=mat(hexc(roof), 0.3), bw=0.04)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(0, math.radians(lean), math.radians(-8)))


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    name, roof, gx, gy = a[0], a[1], float(a[2]), float(a[3])
    lean = float(a[4]) if len(a) > 4 else 0.0
    wide = int(a[5]) if len(a) > 5 else 0
    reset()
    eyehouse(roof, gx, gy, lean, wide)
    B.render(name)
