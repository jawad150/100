"""SaaS motion-graphics cut of the Floret animation: the same iPhone, quote cards, Sell/Buy buttons and chart,
told in five shots with cuts, rack focus and push-ins instead of one continuous shot.

    0.0-2.2  reveal  the phone turns from edge-on to face camera while the camera pushes in; list lies flat
    2.2-4.6  pop     low grazing angle across the glass; cards pop out toward camera, focus racks with them
    4.6-6.6  tap     macro on the GOLD card: glide from Sell to Buy, Buy is tapped (ripple), others dim
    6.6-8.6  chart   tracking shot across the candles on the second phone
    8.6-11.0 hero    mirrored 3/4 hero angle, all cards floating evenly; slow orbit and pull-back

Textures: ATLAS_HASH='#tap=0:5.6' node floret/render.js atlas 30 11

    python3 floret/saas_film.py still 30,100,170,230,300      # preview stills (PCT=40 SAMPLES=4 for quick ones)
    python3 floret/saas_film.py render 1 330                  # RGBA frames -> $OUT/blender/####.png (resumable)
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_kit as kit                     # imports bpy, which makes mathutils importable
import bpy
from mathutils import Vector

from phone_kit import lerp, clamp, ease, smooth, ease_out

SHOTS = [('reveal', 0.0, 2.2), ('pop', 2.2, 4.6), ('tap', 4.6, 6.6), ('chart', 6.6, 8.6), ('hero', 8.6, 11.0)]
POP_START = 2.5                             # cards pop out during the low-angle shot
TAP_AT = 5.6                                # GOLD Buy is tapped (must match ATLAS_HASH)

kit.init()
sc = kit.sc
cam = kit.camera(70)
cam.data.dof.use_dof = True
cam.data.dof.aperture_blades = 0

LIGHTS = [kit.area('Key', (-40, 10, 40), 30, 60000, (0.95, 0.96, 1.0)),
          kit.area('Top', (-10, 40, 30), 20, 22000, (0.9, 0.9, 1.0)),
          kit.area('Rim', (34, -10, 14), 30, 14000, (0.72, 0.68, 1.0), size_y=3)]
REFLECTORS = [kit.reflector('Reflector L', (-26, -6, 10), 26, 2.2), kit.reflector('Reflector R', (26, -6, 10), 26, 0.6)]

phone = kit.build_iphone('iPhone', kit.M['screen'], kit.SCREEN_REGION)
back = kit.build_iphone('iPhone Back', kit.M['back_screen'], kit.BACK_REGION)
cards = kit.make_cards(phone)
kit.M['card_face'].node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.08
back_emission = kit.M['back_screen'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
deg = math.radians


def shot_at(t):
    for name, a, b in SHOTS:
        if t < b or name == SHOTS[-1][0]:
            return name, t - a, b - a


def world(ob, local):
    """World position of a point given in an object's local coordinates."""
    bpy.context.view_layer.update()
    return ob.matrix_world @ Vector(local)


def card_axes(c):
    bpy.context.view_layer.update()
    m = c.matrix_world.to_3x3().normalized()
    return c.matrix_world.translation.copy(), m.col[0].normalized(), m.col[1].normalized(), m.col[2].normalized()


def focus_on(point, fstop):
    cam.data.dof.focus_distance = (Vector(point) - cam.location).length
    cam.data.dof.aperture_fstop = fstop


def set_frame(f):
    t = (f - 1) / kit.FPS
    name, u, d = shot_at(t)
    k = u / d
    for i, c in enumerate(cards):
        kit.place_card(c, kit.pop_pose(i, t, POP_START))
    kit.set_visible(phone, True)
    kit.set_visible(back, True)
    for i, c in enumerate(cards):
        kit.place_card(c, kit.pop_pose(i, t, POP_START))         # (set_visible touched the cards too)
    back_emission.default_value = 0.5
    # at grazing angles the glass is a mirror: keep the light panels out of it in the close-ups
    grazing = name in ('pop', 'chart')
    for r in REFLECTORS:
        r.hide_render = grazing or name == 'hero'           # the hero angle would mirror them in the display
    for l in LIGHTS:
        l.visible_glossy = not grazing and not (name == 'hero' and l.name != 'Rim')

    if name == 'reveal':
        # upright phone turns from edge-on (left side, buttons) to face the camera; camera pushes in
        e = ease_out(k, 3)
        phone.location = (0, 0.2, 0)
        phone.rotation_euler = (deg(-8), deg(lerp(78, 16, e)), deg(lerp(-6, 4, e)))
        back.location = (9.5, -3.5, -16)
        back.rotation_euler = (deg(-6), deg(-24), deg(8))
        cam.data.lens = 70
        kit.look_at(cam, (0, lerp(1.4, 0.7, e), lerp(44, 36, ease(k))), (0, 0.2, 0))
        focus_on(phone.location, 3.2)

    elif name == 'pop':
        # phone flat, screen up; a wide lens skims the glass from beyond its bottom edge
        phone.location = (0, 0, 0)
        phone.rotation_euler = (0, 0, deg(-4))
        kit.set_visible(back, False)
        cam.data.lens = 30
        eye = world(phone, (lerp(3.4, 2.7, ease(k)), lerp(-10.8, -9.6, ease(k)), lerp(9.6, 8.6, ease(k))))
        kit.look_at(cam, eye, world(phone, (0.9, -1.6, 1.0)), roll=-7)
        # rack focus onto whichever card is rising
        idx = clamp((t - POP_START - 0.35) / 0.2, 0, 4)
        i0 = int(idx); i1 = min(4, i0 + 1)
        p0 = card_axes(cards[i0])[0]; p1 = card_axes(cards[i1])[0]
        focus_on(p0.lerp(p1, idx - i0), 2.4)

    elif name == 'tap':
        # macro on the GOLD card: glide from the Sell button to the Buy button, which gets tapped
        phone.location = (0, 0, 0)
        phone.rotation_euler = (deg(-10), deg(-8), deg(-4))
        kit.set_visible(back, False)
        for i, c in enumerate(cards):
            kit.place_card(c, kit.pop_pose(i, t, POP_START), tint=1.0 if i == 0 else lerp(1.0, 0.4, smooth(k * 3)))
        o, ax, ay, az = card_axes(cards[0])
        w = kit.CARD_W * kit.K * cards[0].scale.x
        glide = ease(clamp(k / 0.5))
        target = o + ax * lerp(-0.26 * w, 0.30 * w, glide) + ay * 0.05
        cam.data.lens = 50
        eye = target + az * lerp(9.0, 7.8, ease(k)) - ay * 2.6 + ax * 1.2
        kit.look_at(cam, eye, target, roll=lerp(-4, 2, ease(k)))
        focus_on(target, 1.8)

    elif name == 'chart':
        # tracking shot across the candles on the second phone, tilted back
        kit.set_visible(phone, False)
        back_emission.default_value = 1.0
        back.location = (0, 0, 0)
        back.rotation_euler = (deg(-58), 0, deg(-12))
        cam.data.lens = 45
        e = ease(k)
        eye = world(back, (lerp(-3.4, 2.6, e), lerp(-5.0, -2.0, e), 9.5))
        kit.look_at(cam, eye, world(back, (lerp(-1.6, 1.8, e), lerp(-0.5, 2.0, e), 0.4)), roll=lerp(8, -4, e))
        focus_on(world(back, (lerp(-1.6, 1.8, e), lerp(-0.5, 2.0, e), 0.4)), 2.8)

    else:
        # hero: mirrored 3/4 angle (right side and Camera Control toward camera), cards floating evenly
        e = ease(k)
        phone.location = (-1.2, 0.6, 0)
        phone.rotation_euler = (deg(-16), deg(lerp(-24, -30, e)), deg(lerp(-14, -19, e)))
        back.location = (-11, -6.5, -18)
        back.rotation_euler = (deg(-12), deg(-26), deg(-16))
        cam.data.lens = 70
        kit.look_at(cam, (lerp(-0.2, 0.9, e), lerp(-0.4, -0.8, e), lerp(40, 44, e)), (-0.6, 0.2, 0))
        focus_on(phone.location, 4.5)


kit.run(set_frame)
