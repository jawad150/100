"""3D objects for BMHC "Manchester, can you name this place by ear?" (glossy clay, BMHC palette).

Run: blender -b -P blender_ear.py -- [draft] [name ...] -> workspace_ear/assets/<name>.png (RGBA 900x900)
"""
import bpy, sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_tuned'))
import blender_tuned as B
from blender_tuned import mat, setm, act, bevel, smooth, box, cyl, sph, torus, text, curve_path, group, hexc, reset

ROOT = os.path.abspath(os.path.join(HERE, '..'))
B.OUT = f'{ROOT}/workspace_ear/assets'
os.makedirs(B.OUT, exist_ok=True)
MAG, TEAL, ORANGE, LIME = hexc('#E60585'), hexc('#2DC892'), hexc('#FF4200'), hexc('#69FF00')
INK, CHAR, SLATE, STONE, WHITE = hexc('#0B0B0B'), hexc('#1F1F1F'), hexc('#5C5C5C'), hexc('#E9E6DF'), hexc('#FFFFFF')
STEEL, WOOD = hexc('#BFC3C9'), hexc('#C79A62')


def mic():
    """The hand-held microphone of the hook."""
    head = sph(0.62, loc=(0, 0, 1.55), m=mat(STEEL, 0.35, 1.0), scale=(1, 1, 1.12))
    for k in range(7):
        torus(0.6 - abs(k - 3) * 0.07, 0.012, loc=(0, 0, 1.25 + k * 0.1), m=mat(hexc('#8E9399'), 0.4, 1.0))
    torus(0.6, 0.06, loc=(0, 0, 1.2), m=mat(MAG, 0.3, coat=0.6))
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0.26, depth=1.9, location=(0, 0, 0.15), vertices=64)
    smooth(setm(act(), mat(INK, 0.3, coat=0.7)))
    box((0.16, 0.08, 0.5), loc=(0, -0.38, 0.4), m=mat(TEAL, 0.3, emit=(TEAL, 0.6)), bw=0.03, rot=(math.radians(-8), 0, 0))
    cyl(0.27, 0.12, loc=(0, 0, -0.85), m=mat(MAG, 0.3), bw=0.03)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(-18), math.radians(22), math.radians(-10)))


def ball():
    """Sports clue: a basketball-style ball in BMHC orange with ink seams."""
    sph(1.0, m=mat(ORANGE, 0.55, coat=0.15))
    ink = mat(INK, 0.5)
    torus(1.0, 0.03, m=ink)
    torus(1.0, 0.03, m=ink, rot=(math.radians(90), 0, 0))
    for s in (-1, 1):
        curve_path([(s * 0.35, -0.94, 0.0), (s * 0.62, -0.62, 0.55), (s * 0.7, 0.0, 0.72), (s * 0.62, 0.62, 0.55), (s * 0.35, 0.94, 0.0)], 0.03, ink)
        curve_path([(s * 0.35, -0.94, 0.0), (s * 0.62, -0.62, -0.55), (s * 0.7, 0.0, -0.72), (s * 0.62, 0.62, -0.55), (s * 0.35, 0.94, 0.0)], 0.03, ink)
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(math.radians(20), math.radians(-15), math.radians(25)))


def book():
    """Study-circle clue: an open book, a page lifting, a pencil underlining."""
    cover = mat(TEAL, 0.3, coat=0.5)
    page = mat(hexc('#FBF8F1'), 0.6, coat=0.05)
    for s in (-1, 1):
        box((1.55, 2.1, 0.08), loc=(s * 0.8, 0, 0), m=cover, bw=0.03, rot=(0, s * math.radians(-6), 0))
        box((1.45, 2.0, 0.2), loc=(s * 0.76, 0, 0.14), m=page, bw=0.04, rot=(0, s * math.radians(-6), 0))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    p = act()
    p.scale = (0.72, 1.0, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    p.location = (0.33, 0, 0.42)
    p.rotation_euler = (0, math.radians(-38), 0)
    sd = p.modifiers.new('s', 'SOLIDIFY')
    sd.thickness = 0.01
    setm(p, page)
    for j in range(6):
        box((0.95, 0.04, 0.02), loc=(-0.78, -0.7 + j * 0.28, 0.25), m=mat(hexc('#A0A0A0'), 0.6), bw=0)
    box((0.95, 0.05, 0.03), loc=(-0.78, -0.14, 0.255), m=mat(MAG, 0.4, emit=(MAG, 0.5)), bw=0)
    cyl(0.07, 1.8, loc=(-0.3, -0.75, 0.55), m=mat(hexc('#F2C230'), 0.4), rot=(math.radians(70), 0, math.radians(-50)), v=6, bw=0.01)
    bpy.ops.mesh.primitive_cone_add(radius1=0.07, radius2=0.0, depth=0.22, location=(-0.98, -0.2, 0.25), rotation=(math.radians(-110), 0, math.radians(-50)), vertices=6)
    setm(act(), mat(WOOD, 0.5))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    group(objs, rot=(math.radians(16), 0, math.radians(-12)))


def fader():
    """Heritage Radio clue: a studio desk strip with faders, one pushed up, an ON AIR light."""
    box((3.0, 1.6, 0.3), m=mat(CHAR, 0.4, coat=0.5), bw=0.08)
    for i in range(5):
        x = -1.1 + i * 0.55
        box((0.07, 1.2, 0.04), loc=(x, 0, 0.17), m=mat(INK, 0.3), bw=0)
        y = 0.35 if i == 2 else (-0.3 + 0.1 * (i % 2))
        box((0.3, 0.2, 0.22), loc=(x, y, 0.27), m=mat(MAG if i == 2 else STONE, 0.3, emit=(MAG, 0.5) if i == 2 else None), bw=0.04)
        for k in range(4):
            box((0.12, 0.05, 0.02), loc=(x + 0.18, -0.5 + k * 0.32, 0.17), m=mat(LIME if k < 2 + (i == 2) * 2 else SLATE, 0.3,
                emit=(LIME, 1.0) if k < 2 + (i == 2) * 2 else None), bw=0)
    box((1.2, 0.3, 0.4), loc=(0, 0.95, 0.4), m=mat(hexc('#E8332A'), 0.25, emit=(hexc('#E8332A'), 1.2)), bw=0.06)
    text('ON AIR', 0.18, (0, 0.79, 0.4), mat(WHITE, 0.3, emit=(WHITE, 1.5)), ext=0.02, font='Inter-800')
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'FONT')]
    group(objs, rot=(math.radians(28), 0, math.radians(-14)))


def headphones():
    band = curve_path([(-1.0, 0, 0.2), (-0.85, 0, 1.0), (0, 0, 1.45), (0.85, 0, 1.0), (1.0, 0, 0.2)], 0.09, mat(INK, 0.3, coat=0.6))
    for s, col in ((-1, MAG), (1, TEAL)):
        cyl(0.42, 0.3, loc=(s * 1.0, 0, 0), m=mat(col, 0.3, coat=0.6), rot=(0, math.radians(90), 0), v=64, bw=0.06)
        cyl(0.36, 0.1, loc=(s * 0.82, 0, 0), m=mat(CHAR, 0.6), rot=(0, math.radians(90), 0), v=64, bw=0.03)
    objs = [o for o in bpy.context.scene.objects if o.type in ('MESH', 'CURVE')]
    group(objs, rot=(math.radians(10), 0, math.radians(-25)))


ALL = ['mic', 'ball', 'book', 'fader', 'headphones']

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    draft = 'draft' in argv
    names = [a for a in argv if a != 'draft'] or ALL
    for n in names:
        reset()
        bpy.context.scene.cycles.samples = 24 if draft else 96
        globals()[n]()
        B.render(n)
