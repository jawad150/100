"""Blender (bpy) shot matched to the MT5 reference: a silver iPhone 16 Pro lying on a steep diagonal, turned
on its long axis so its left side (buttons) faces the camera. The quote list starts lying in the screen and
pops out into evenly spaced floating cards; a second iPhone with a chart sits behind.

Textures come from `node floret/render.js atlas 30 10` (ui_atlas.html: one atlas JPEG per frame).

    python3 floret/blender_phone.py still 1,150,300        # preview stills (PCT=40 SAMPLES=4 for quick ones)
    python3 floret/blender_phone.py render 1 300           # RGBA frames -> $OUT/blender/####.png (resumable)
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_kit as kit                     # imports bpy, which makes mathutils importable
from mathutils import Vector

POP_START, POP_STAGGER, POP_TIME = 0.6, 0.2, 0.85     # seconds

# ---------------------------------------------------------------- camera / pose, fitted to the reference
LENS, CAM_D = 85.0, 51.97
# The reference is a TikTok screen recording (9:19.9) that fills the phone by cropping the sides of the ad,
# so its phone fills the frame width. Zoom so our 1080 px width is exactly the reference's visible width
# (477 -> 384 px), framing its y 85..768.
FRAME_ZOOM, FRAME_SHIFT_Y = 477 / 384, -0.003
POSE = dict(tilt=-21.90, roll=37.43, angle=36.62)    # top tilted away, left side toward camera, in-plane
PHONE_POS = (1.109, 1.713)                           # start; slides up its own long axis at constant speed
PAN = (-0.679, 0.923)                                # (tracked on the reference: linear, ~3.2 x 4.3 px/s)
BACK_OFFSET = (9.908, 8.155, -19.572)     # in the phone's own axes; fitted: ~20 cm behind, so it reads smaller
BACK_TURN = 2.78                            # extra in-plane turn of the back phone (deg)

kit.init()
cam = kit.camera(LENS * FRAME_ZOOM)
cam.data.shift_y = FRAME_SHIFT_Y
cam.location = (0, 0, CAM_D)

# big soft key from the camera's left: the silver left side and buttons catch it, like the reference
kit.area('Key', (-40, 6, 40), 30, 60000, (0.95, 0.96, 1.0))
kit.area('Top', (-10, 40, 30), 20, 22000, (0.9, 0.9, 1.0))
kit.area('Rim', (30, -20, 12), 30, 9000, (0.7, 0.68, 1.0), size_y=3)
# The left side of the phone mirrors the direction (-0.87, -0.33, -0.37): a big soft panel there turns the
# whole titanium side into the bright silver strip seen in the reference.
kit.reflector('Side Reflector', (-26, -10, -11), 26, 3.0)

rig = kit.empty('Rig')
rig.rotation_euler = (math.radians(POSE['tilt']), math.radians(POSE['roll']), math.radians(POSE['angle']))
front = kit.build_iphone('iPhone', kit.M['screen'], kit.SCREEN_REGION)
front.parent = rig
back = kit.build_iphone('iPhone Back', kit.M['back_screen'], kit.BACK_REGION)
back.parent = rig
back.location = Vector(BACK_OFFSET)
back.rotation_euler = (0, 0, math.radians(BACK_TURN))
cards = kit.make_cards(front)


def set_frame(f):
    t = (f - 1) / kit.FPS
    k = t / (kit.FRAMES / kit.FPS)
    rig.location = (PHONE_POS[0] + PAN[0] * k, PHONE_POS[1] + PAN[1] * k, 0)
    for i, c in enumerate(cards):
        kit.place_card(c, kit.pop_pose(i, t, POP_START, POP_STAGGER, POP_TIME))


kit.run(set_frame)
