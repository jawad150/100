"""Realistic Spider-Man-themed plates for the Yaadein reel (Cycles).

python3 shots.py <shot> [...]     -> workspace2/plates2/<shot>.png   (PREVIEW=1 for a fast low-res check)
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import world as W  # noqa: E402

OUT = W.ROOT + '/plates2'


# ------------------------------------------------------------------ rooftop set
def rooftop(wet=1.0, city=True, neon=True):
    """Our roof at z=0 (x -14..14, y -16..3), parapet along y=3; the city falls away to street z=-95."""
    roof = W.pbr('roof', 'concrete_floor_worn_001', scale=2.5, rough_mul=0.9, tint=(0.55, 0.55, 0.58), wet=wet)
    wall = W.pbr('wall', 'concrete_wall_008', scale=2.0, tint=(0.5, 0.5, 0.52), wet=0.3)
    brick = W.pbr('brick', 'brick_wall_001', scale=1.6, tint=(0.45, 0.42, 0.42))
    W.box((28, 19, 0.4), (0, -6.5, -0.2), roof, name='roof')
    W.box((28, 0.45, 1.05), (0, 3.0, 0.52), wall, name='parapet', bevel=0.02)
    W.box((0.45, 19, 1.05), (-14, -6.5, 0.52), wall, name='parapet_l')
    W.box((0.45, 19, 1.05), (14, -6.5, 0.52), wall, name='parapet_r')
    W.box((28.6, 19.6, 95), (0, -6.5, -47.9), brick, name='tower')            # our building body
    # roof clutter
    W.prop('exterior_aircon_unit', (-5.5, -3.0, 0), (0, 0, 15), 1.0)
    W.prop('exterior_aircon_unit', (-7.2, -3.4, 0), (0, 0, 10), 1.0)
    W.prop('modular_airduct_rectangular_01', (6.5, -5.0, 0), (0, 0, 90), 1.0)
    W.prop('power_box_01', (9.5, 1.9, 0), (0, 0, 180), 1.0)
    W.prop('security_light', (-13.6, -1.0, 2.6), (0, 0, -90), 1.0)
    W.prop('modular_electric_cables', (-2, -10, 0.0), (0, 0, 0), 1.0)
    # water tank + antenna mast
    rust = W.pbr('rust', 'rusty_metal_02', scale=1.0, tint=(0.6, 0.55, 0.55))
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=3.2, location=(8.5, -10.5, 4.6), vertices=48)
    bpy.context.object.data.materials.append(rust)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        W.box((0.12, 0.12, 3.0), (8.5 + dx, -10.5 + dy, 1.5), rust)
    W.box((0.18, 0.18, 14), (-10.5, -12, 7), rust, name='mast')
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(-10.5, -12, 14.2))
    bpy.context.object.data.materials.append(W.emit('mastbeacon', W.RED, 400))
    if city:
        W.skyline((-700, 700, 25, 1500), -95, seed=11, avoid=(-40, 40, -60, 30), lit=0.28, strength=4.0, name='cityN')
        W.skyline((-700, 700, -700, 25), -95, seed=12, avoid=(-60, 60, -80, 40), lit=0.22, strength=3.0, name='cityS')
        W.streets((-700, 700, -700, 1500), -95, color=(1.0, 0.12, 0.08), strength=3.0)
        # local rain haze only near the roof (distance haze is added from the mist pass in compositing)
        W.fog((60, 60, 30), (0, 10, 5), 0.012, color=(0.8, 0.85, 1.0), anis=0.55, noise=0.5, name='haze')
    if neon:
        # giant red sign on the neighbouring tower facing us, below our roof line -> red uplight
        W.neon_sign((16, 4.5), (-24, 34, -12), W.RED, 30, rot_z=0)
        W.neon_sign((3.5, 26), (30, 40, -20), W.BLUE, 22, rot_z=-30)
    return roof


def night_sky():
    W.world_hdri('kloppenheim_06_puresky', strength=0.05, rot_z=200, tint=(0.35, 0.45, 1.0),
                 bg_strength=0.035, bg_tint=(0.28, 0.38, 1.0))


def shot_roof_env():
    sc = W.reset(64)
    night_sky()
    rooftop()
    W.area((0, 8, -6), (0, 2, 1), W.RED, 3500, size=10, size_y=3, name='redbounce')
    W.area((6, 14, 9), (0, 0, 0.5), W.CYAN, 1800, size=8, name='moonrim')
    W.area((-3, -8, 7), (0, 0, 0), (0.6, 0.7, 1.0), 120, size=6, name='fill')
    W.camera((2.6, -7.5, 1.6), (0, 6, 0.6), lens=24, fstop=2.0, focus=10.5)
    W.render(f'{OUT}/roof_env{"_preview" if os.environ.get("PREVIEW") else ""}.png')


SHOTS = {k[5:]: v for k, v in globals().items() if k.startswith('shot_')}

if __name__ == '__main__':
    for s in sys.argv[1:]:
        SHOTS[s]()
