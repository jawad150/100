"""ui.py: SaaS UI kit for the Organic Fostering reels - frosted glass, app windows, widgets, cursors, orbit rings.

Every sprite follows core's convention: premultiplied LINEAR float32 RGBA (h, w, 4). Components are pure functions
of their parameters: static layers are built once and cached (functools.lru_cache keyed by the parameters; cached
arrays are read-only - copy before editing, or use Panel.face_at() which returns a writable copy); animated parts
(checkbox ticks, comet rim light, ripples, bars) are rendered per call from cached pieces. Text is drawn with PIL
(raqm layout = real kerning) at 2x and area-downsampled: Poppins for UI ('ui' SemiBold, 'ui_medium', 'body'
Regular, 'ui_bold'), Nunito for headings ('head' ExtraBold, 'head_black', 'head_bold'). Default sizes respect the
brief: UI body 34-46 px, fine print >= 28 px. Spacing sits on an 8 px grid. Importing has no side effects.
Self-test: python3 ui.py selftest -> workspace3/out/selftest/ui_{neon,amber,airy,components,motion,icons}*.png

LOOKS ('neon' | 'amber' dark smoky glass with neon rims, 'airy' white frosted glass with soft plum shadows;
aliases night/dark -> neon, light/day -> airy)
    L = ui.LOOKS['neon'] (or ui.look('neon')): .dark .text .text2 (muted) .text3 (faint) .accent .accent_hi
    .grad (c0, c1) fill gradient .rim .rim2 (neon edge colour, hot-spot colour) .glow .shadow .ok .ok_hi (LEAF)
    .frost (default frost sigma px) - all linear RGB.  ui.col('MAGENTA' | '#B7006E' | (r, g, b) linear).
    ui.money(23275.2) -> '£23,275.20'

TEXT
    ui.put_text(dst, x, y, 'Am I eligible?', 52, 'head', color=None, anchor='ls', tracking=0, opacity=1,
                grad=None, angle=0, max_w=None) -> advance px. anchor: l/m/r + s (baseline) | m (cap middle) |
                t (cap top) | b (descender); max_w shrinks the size to fit. Integer-snapped = razor sharp.
    t = ui.text('£23,275.20', 104, 'head_black', grad=('#FFE2C4', '#FFB15C'), angle=-90) -> Txt: .spr, .ox/.oy
        (pen origin in the sprite), .adv, .cap; t.topleft(x, y, anchor).  ui.measure(txt, size, fnt),
        ui.wrap(txt, size, fnt, max_w) -> lines, ui.fit_size(txt, size, fnt, max_w), ui.font(name, px).
    Dark text gets a slight coverage boost (weight 0.82) so ink-on-ivory stays as bold as light-on-dark.

SPRITE HELPERS
    ui.place(cv, spr, x, y, anchor=(.5, .5), opacity=1, mode='over', scale=1)   most widget sprites carry
        padding for glows with the BODY CENTRED, so place(cv, spr, cx, cy) centres the body.
    ui.paste(dst, spr, x, y, opacity, mode) integer top-left composite (fast, clipped).
    ui.Surf(w, h): analytic AA drawing surface (.rrect, .rrect_grad, .stroke_rrect, .circle, .ring, .glow,
        .sheen, .text, .paste, .fill, .emit; .img is the sprite) for custom widgets.
    Vector: ui.parse_path(svg_d) -> [(pts, closed)], ui.stroke_mask(polys, w, h, width, scale, offset) (round
        caps/joins, SDF), ui.fill_mask(...), ui.trim_polyline(pts, t0, t1) (draw-on).

ICONS (24-unit Lucide-style geometry, rounded strokes, SDF-rendered: crisp at any size)
    ui.ICONS = home house heart chat calendar user users settings shield star pound check leaf phone arrow_right
               search bell book graduation sparkle clock globe puzzle key (+ chart grid pin plus coin mail menu)
    ui.icon('heart', 96, color='IVORY', stroke=2.0, fill_a=0, glow=0, glow_color=None, grad=None) -> sprite
        (icon box centred; glow adds padding). fill_a 0..1 = duotone fill of closed shapes; grad=(c0, c1).

GLASS PANELS
    p = ui.glass_card(w, h, r=40, look='neon', rim=1, rim_color=None, rim2=None, rim_angle=-55, rim_spread=2,
                      glow=1, shadow=1, tint=None, tint_a=None, border=1, spec=1, noise=1, frost=None) -> Panel
        Smoky (dark) or white (airy) frosted glass: tint gradient, glass grain, fresnel edge, top specular
        sheen + diagonal highlight, inner gradient border (bright top-left, fading), a neon rim whose hot spot
        (rim2) faces rim_angle (deg CCW from +x; -55 = bottom-right), outer glow, soft drop shadow (separate
        sprite, 1/4 res) and corner radius. ~0.3-1 s to build once, cached.
    Panel: .w .h .r .pad .face (padded sprite; alpha = body only, so it is also the frost mask) .shadow
        .rim_layer (baked emissive rim) .meta .frost. Card-local px: (0, 0) = top-left of the body.
        f = p.face_at(sweep=None, sweep_len=0.14, sweep_gain=1, sweep_color=None, sweeps=1, light=None,
                      rim_gain=None) -> writable face copy (~10-25 ms): sweep = phase 0..1 of a neon comet running
                      clockwise round the edge from 12 o'clock (white-hot head, rim-coloured tail; animate it e.g.
                      (t * 0.4) % 1); light = 0..1 diagonal specular glint across the glass; rim_gain scales the
                      static rim (0 off .. 2 double).
        p.put(f, spr, x, y, anchor=(0, 0), opacity=1, mode='over', scale=1)  composite content at card px.
        p.text(f, x, y, txt, size, fnt, color, anchor)
        p.draw(cv, x, y, scale=1, rot=0, opacity=1, anchor=(.5, .5), face=None, frost=None, shadow=1)  2D: the
            shadow, a frost (canvas blurred once at 1/4 res inside the card outline) and the face.
        info = p.plane(cv, cam, center, width=None, rot=(rx, ry, rz), opacity=1, anchor=(.5, .5), face=None,
                       frost=None, shadow=1, shadow_z=30, dof=True, blur=0) -> core.draw_plane dict. width =
            body width in world units; frost follows the projected outline (perspective-correct), the shadow
            sits shadow_z behind along the card normal; DOF / near clipping from core. ~40-90 ms for a window.
        p.child(cv, cam, center, width, rot, spr, x, y, z=-20)  draw spr on a parallel plane lifted z toward
            the viewer at card px (x, y): layered UI with real parallax under camera moves.
        p.screen(cam, center, width, rot, x, y, z=0) -> screen px of card px (put cursors on tilted UI);
            p.world(...) -> world point; p.screen2d(x0, y0, x, y, scale) for 2D draws; p.outline().
    ui.frost_poly(cv, poly_xy, sigma, amount=1)  frosted blur inside any screen polygon.
    ui.media_fit(spr, w, h, r=0, center=(.5, .5), zoom=1) -> cover-fit + rounded corners (footage slots).
    ui.put_media(panel, face, spr, x, y, w, h, r=24, opacity=1)  footage clipped into a rounded slot.
    ui.media_face(panel, media, inset=0, sweep=None, light=None) -> face with footage filling the card under the
        rim / sheen (a tilted glass card playing footage: clip.get(t, p.w, p.h, look=...)).
    ui.derive_panel(base, face, meta) -> Panel sharing base's geometry, shadow and rim.

APP WINDOW
    win = ui.app_window(w=900, h=1240, look='neon', title='organicfostering.co.uk', header='Am I eligible to
              foster?', sub=None, icons=('home', 'users', 'chat', 'calendar', 'settings'), active=0,
              sidebar=True, traffic=True, header_size=52, r=44, rim=1, glow=1, shadow=1) -> Panel (cached)
        title bar (traffic-light dots + URL pill), icon sidebar with gradient active tile, Nunito header.
        win.meta['slot'] = (x, y, w, h) content area; meta['sidebar'] = icon centres; meta['titlebar'].
    x, y, sw, sh = win.meta['slot']
    f = win.face_at(sweep=(t * .35) % 1)
    for i, lab in enumerate(rows):
        win.put(f, ui.check_row(lab, w=sw, t=t - tick[i], look='neon'), x - ui.ROW_PAD, y + i * 120 - ui.ROW_PAD)
    win.plane(cv, cam, (0, 0, 0), 900, rot=(7, -16, 1.5), face=f)
    xy = win.screen(cam, (0, 0, 0), 900, (7, -16, 1.5), x + 58, y + 2 * 120 + 48, z=-60)
    ui.draw_cursor(cv, xy[0], xy[1], 'arrow', 76, press=K.impulse(t, tick[2], 9), click=t - tick[2])

WIDGETS (sprites unless noted; `look` = 'neon' | 'amber' | 'airy')
    ui.checkbox(t, size=60, look) -> 2*size sprite. t = s since the tick (None/<0 empty): 0-.22 s check draws on,
        .12 s LEAF fill + spring pop (+24 % overshoot) + burst ring, glow settles.
    ui.check_row(label, sub=None, w=700, t=None, look, h=None, hl=0, box=60, label_size=38, sub_size=28)
        -> (w + 48) x (h + 48), body at (ROW_PAD, ROW_PAD); h 96 (120 with sub); hl 0..1 accent focus ring;
        ticked rows get a LEAF edge tint. Settled states are cached.
    ui.toggle(p, w=112, h=64, look, on=None) -> knob squashes mid-travel, gradient fill follows the knob. Feed it
        K.spring(t - t0, 2.6, .45) for a bouncy switch.
    ui.chip(text, sel=0, look, size=34, h=72, icon_name=None, grad=None, origin=(.5, .5)); ui.chip_size(...)
        sel 0..1 reveals the selected gradient state as a circular wipe from origin (keeps text crisp).
    ui.button(text='Start your enquiry', hover=0, press=0, ripple=None, ripple_at=(.5, .5), look, h=112,
              size=40, icon_name='arrow_right', grad=None) -> body + BUTTON_PAD; MAGENTA -> ORANGE pill, gloss,
        glow; hover lifts the glow + nudges the arrow; press 0..1 = 94 % + darker; ripple = s since click.
        ui.button_size(text, h, size).
    ui.cursor(kind='arrow'|'hand', size=72, press=0, look) white face, dark outline, extruded thickness, soft
        shadow; ui.cursor_anchor(kind, size) -> hotspot anchor; ui.click_ring(t, r, color, look);
        ui.draw_cursor(cv, x, y, kind, size, press=0, click=None, opacity=1, look, scale=1, rot=0) puts the
        hotspot (arrow tip / fingertip) on (x, y) and adds the click ring while 0 <= click < .65 s.
    ui.progress_ring(p, size=320, width=24, look, label='auto', sub=None, colors=None, glow=1, label_size=None)
        clockwise gradient arc from 12 o'clock, round caps, hot head dot, glow, centred % label.
    ui.slider(v, w=720, look, label='52 weeks', colors=None, ticks=[(0, '1'), (1, '52')], bubble=True)
        -> (w + 80) x 252; ui.slider_knob(v, w) -> knob centre in sprite px (for a dragging cursor).
    ui.bar_chart(values, labels, grow=1 | [per bar], active=None | float index, w=760, h=560, look='amber',
                 fmt=money, vmax=None, grid=4, colors=None, dim=.42, depth=0) -> (w + 64) x (h + 64)
        glossy gradient bars (gloss stripe, cap highlight) on a dashed baseline grid; value labels count up
        with grow; the active bar glows while others dim; depth > 0 adds an isometric 3D side/top. ~20 ms.
        grow=[K.ramp(t, t0 + .2 * i, t0 + .2 * i + .8, 'out_back') for i in range(4)]
    ui.toast(title, sub=None, icon_name='check', look, w=640, accent=None) -> glass Panel (draw / plane it).
    ui.tag(text, thumb=None, look, size=34, h=84, icon_name=None, accent=None, thumb_key=None) -> glass pill
        Panel (thumb = any sprite in a round crop; give a stable thumb_key); ui.tag_size(...).
    ui.badge(text='Rated Good by Ofsted', sub='Inspected May 2025', look, icon_name='star') -> glass Panel.
    ui.dock_tile(title, sub, icon_name, look, w=300, h=460, accent=None, r=44) -> glass Panel with a media
        slot (meta['slot'] = (x, y, w, h, r)); ui.dock_face(tile, focus=0, media=None, media_mix=1,
        sweep=None, light=None, icon_spr=None) -> per-frame face: focus lights edge + slot, media plays footage
        in the slot (a small icon disc stays), icon_spr swaps in a sprites3d frame.
        ui.carousel(n, focus, spacing=360, grow=.16) -> [(dx, scale, weight)] for a sliding dock.
    ui.search_bar(text, n=None, t=0, w=720, h=96, look, placeholder='Search support', go=True) typing (n chars)
        + caret (solid while typing, 1.4 Hz blink idle).
    ui.avatar(img, size=120, look, ring=None, ring_w=5, gap=5, status=False) photo/footage in a gradient ring.
    ui.steps(active, n=5, w=880, look, labels=None, size=72) 01..05 dots, filling track, done checks, active glow.

ORBIT RING
    ui.orbit_ring(cv, cam, items, phase=0, center=(0, 0, 0), radius=360 | (rx, rz), tilt=16, roll=-10,
                  look='airy', ring=True, ring_color=None, mid=None, back_blur=3.5, back_dim=None,
                  back_scale=.8, size=1, opacity=1, dof=True, yaw_follow=0, enter=None) -> [(i, xy, depth, front)]
        Glass tags (str, (text, thumb[, key]) or Panels) on a tilted 3D ellipse, depth-sorted through the camera;
        back items smaller, dimmer and blurred (+ camera DOF); a thin ring line (back half dim). mid(cv) is
        drawn between the back and front halves (the hero object). phase in turns (t * .05); roll's sign tilts
        the ring the other way; enter = per-item 0..1 pop-in. Focus the camera on the front of the ring:
        cam = K.Cam.orbit((0, 60, 0), 1500, yaw=-6, pitch=7, aperture=18, focus_dist=1500 - rz * cos(tilt)).

PERFORMANCE (1 core, warm caches): glass_card build 0.3-1 s, app_window ~1.5 s (once); face_at + sweep 10-25 ms;
window plane() 40-90 ms (frost + shadow + face); check_row 1-6 ms; bar_chart ~20 ms; progress_ring ~40 ms per new
value; orbit_ring with 6 tags ~70 ms; dock_face ~25 ms. Pre-build panels in the reel's prewarm().

EXAMPLE
    import core as K, ui
    def draw(t):
        cam = K.Cam(pos=(0, 0, -1600 + 60 * t), aperture=24)
        cv = K.background('neon', t, cam)
        win = ui.app_window(look='neon')
        f = win.face_at(sweep=(t * .35) % 1)
        x, y, sw, sh = win.meta['slot']
        win.put(f, ui.check_row('A spare bedroom', w=sw, t=t - 1.0), x - ui.ROW_PAD, y - ui.ROW_PAD)
        win.plane(cv, cam, (0, 0, 0), 900, rot=(7, -16, 1.5), face=f)
        return cv
"""
import functools
import math
import os
import re
import sys

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

import core as K

C = K.C
W, H = K.W, K.H
SS = 2                     # text supersampling
GRID = 8                   # spacing grid (px)


# =============================================================================================== looks
def _v(c, k=1.0):
    return (np.asarray(c, np.float32)[:3] * np.float32(k)).astype(np.float32)


class Look:
    """Colour tokens for one UI look. All colours are linear RGB (np.float32[3])."""

    def __init__(self, name, **kw):
        self.name = name
        self.__dict__.update(kw)

    def __repr__(self):
        return 'Look(%s)' % self.name


def _make_looks():
    m, o, hp, am = C['MAGENTA'], C['ORANGE'], C['HOT_PINK'], C['AMBER']
    neon = Look(
        'neon', dark=True,
        tint_top=_v(K.mix(C['NIGHT_1'], C['PLUM'], 0.55), 1.0), tint_bot=_v(C['NIGHT_0'], 1.0), tint_a=0.66,
        text=_v(C['IVORY']), text2=_v(K.mix(C['IVORY'], C['LAVENDER'], 0.5), 0.52), text3=_v(C['LAVENDER'], 0.30),
        accent=_v(m), accent_hi=_v(hp), grad=(_v(m), _v(o)), grad_hi=(_v(hp), _v(am)),
        rim=_v(hp), rim2=_v(o), glow=_v(m), border=_v(C['WHITE']), border_a=0.55,
        shadow=_v((0.0, 0.0, 0.0)), shadow_a=0.62, surface=_v(C['WHITE']), surface_a=0.045,
        line=_v(C['WHITE']), line_a=0.09, ok=_v(C['LEAF']), ok_hi=_v(C['LEAF_HI']),
        frost=16.0, fresnel=0.022, spec=0.03, rim_k=1.0, glow_k=1.0, noise=0.0022,
        knob=_v(C['WHITE']), track_a=0.12, chip_text=_v(C['IVORY'], 0.80))
    amber = Look(
        'amber', dark=True,
        tint_top=_v(K.mix(K.hexlin('#2A1208'), C['PLUM'], 0.25)), tint_bot=_v(K.hexlin('#0E0604')), tint_a=0.66,
        text=_v(C['IVORY']), text2=_v(K.mix(C['IVORY'], C['PEACH'], 0.5), 0.52), text3=_v(C['PEACH'], 0.30),
        accent=_v(o), accent_hi=_v(am), grad=(_v(o), _v(am)), grad_hi=(_v(am), _v(C['PEACH'])),
        rim=_v(am), rim2=_v(m), glow=_v(o), border=_v(C['WHITE']), border_a=0.55,
        shadow=_v((0.0, 0.0, 0.0)), shadow_a=0.62, surface=_v(C['WHITE']), surface_a=0.045,
        line=_v(C['WHITE']), line_a=0.09, ok=_v(C['LEAF']), ok_hi=_v(C['LEAF_HI']),
        frost=16.0, fresnel=0.022, spec=0.03, rim_k=1.0, glow_k=1.0, noise=0.0022,
        knob=_v(C['WHITE']), track_a=0.12, chip_text=_v(C['IVORY'], 0.80))
    airy = Look(
        'airy', dark=False,
        tint_top=_v(C['WHITE']), tint_bot=_v(K.mix(C['IVORY'], C['LAVENDER'], 0.6)), tint_a=0.56,
        text=_v(C['INK']), text2=_v(K.mix(C['INK'], C['LAVENDER'], 0.42)), text3=_v(K.mix(C['INK'], C['LAVENDER'], 0.7)),
        accent=_v(m), accent_hi=_v(hp), grad=(_v(m), _v(o)), grad_hi=(_v(hp), _v(am)),
        rim=_v(C['PEACH']), rim2=_v(hp), glow=_v(C['PEACH']), border=_v(C['WHITE']), border_a=0.95,
        shadow=_v(K.mix(C['PLUM'], C['INK'], 0.3)), shadow_a=0.34, surface=_v(C['WHITE']), surface_a=0.55,
        line=_v(C['INK']), line_a=0.08, ok=_v(C['LEAF']), ok_hi=_v(C['LEAF_HI']),
        frost=20.0, fresnel=0.22, spec=0.30, rim_k=0.35, glow_k=0.35, noise=0.004,
        knob=_v(C['WHITE']), track_a=0.10, chip_text=_v(C['INK'], 0.85))
    return {'neon': neon, 'amber': amber, 'airy': airy, 'night': neon, 'dark': neon, 'light': airy, 'day': airy}


LOOKS = _make_looks()


def look(name):
    """Look tokens by name ('neon' | 'amber' | 'airy'; aliases night/dark -> neon, light/day -> airy)."""
    if isinstance(name, Look):
        return name
    return LOOKS[name]


def col(c):
    """Colour spec -> linear float32[3]: core.C name ('MAGENTA'), '#hex' (sRGB), or a linear triple."""
    if isinstance(c, str):
        return _v(C[c]) if c in C else _v(K.hexlin(c))
    return _v(c)


# =============================================================================================== helpers
def _ro(a):
    a.setflags(write=False)
    return a


def _empty(w, h):
    return np.zeros((int(h), int(w), 4), np.float32)


def paste(dst, spr, x, y, opacity=1.0, mode='over'):
    """Composite sprite `spr` onto `dst` with its top-left at integer (x, y) (clipped). In place."""
    if spr is None or opacity <= 0:
        return dst
    x, y = int(round(x)), int(round(y))
    sh, sw = spr.shape[:2]
    H0, W0 = dst.shape[:2]
    u0, v0 = max(0, -x), max(0, -y)
    u1, v1 = min(sw, W0 - x), min(sh, H0 - y)
    if u1 <= u0 or v1 <= v0:
        return dst
    K._blend(dst[y + v0:y + v1, x + u0:x + u1], spr[v0:v1, u0:u1], opacity, mode)
    return dst


def place(dst, spr, x, y, anchor=(0.5, 0.5), opacity=1.0, mode='over', scale=1.0):
    """paste() with an anchor (fractions of the sprite) and optional scale (sub-pixel via core.draw)."""
    if spr is None:
        return dst
    sh, sw = spr.shape[:2]
    if scale == 1.0:
        return paste(dst, spr, x - anchor[0] * sw, y - anchor[1] * sh, opacity, mode)
    K.draw(dst, spr, x, y, scale=scale, anchor=anchor, opacity=opacity, mode=mode)
    return dst


def _grid(x0, y0, x1, y1):
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    return xs + 0.5, ys + 0.5


def _rr_sdf_xy(xs, ys, cx, cy, hw, hh, r):
    qx = np.abs(xs - cx) - (hw - r)
    qy = np.abs(ys - cy) - (hh - r)
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r


def _cov(d, aa=1.0):
    """Coverage from a signed distance (px, <0 inside)."""
    return np.clip(0.5 - d / aa, 0.0, 1.0).astype(np.float32)


def _noise(h, w, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((h, w)).astype(np.float32)
    return cv2.GaussianBlur(n, (0, 0), 0.6)


def _vgrad(h, c0, c1, y0=0.0, y1=None):
    y1 = h if y1 is None else y1
    t = np.clip((np.arange(h, dtype=np.float32) + 0.5 - y0) / max(y1 - y0, 1e-3), 0, 1)[:, None, None]
    return (np.asarray(c0, np.float32) * (1 - t) + np.asarray(c1, np.float32) * t).astype(np.float32)


def _lingrad(w, h, c0, c1, angle=35.0, gain=1.0):
    return (K.gradient(int(w), int(h), [col(c0), col(c1)], angle=angle) * np.float32(gain)).astype(np.float32)


def money(v, decimals=2, symbol='£'):
    """money(23275.2) -> '£23,275.20'."""
    return symbol + ('{:,.%df}' % decimals).format(v)


# =============================================================================================== text
FONT_ALIAS = {'ui': 'Poppins-SemiBold', 'ui_bold': 'Poppins-Bold', 'ui_medium': 'Poppins-Medium',
              'body': 'Poppins-Regular', 'head': 'Nunito-ExtraBold', 'head_black': 'Nunito-Black',
              'head_bold': 'Nunito-Bold'}


@functools.lru_cache(maxsize=96)
def font(name, px):
    """Cached PIL font (raqm layout = real kerning). name: alias ('ui', 'body', 'head', ...) or ttf basename."""
    name = FONT_ALIAS.get(name, name)
    return ImageFont.truetype(K.font_path(name), int(px), layout_engine=ImageFont.Layout.RAQM)


class Txt:
    """A rendered text run: .spr premultiplied sprite, (.ox, .oy) = pen origin (left end of the baseline) in
    sprite px, .adv advance width, .cap cap height, .asc / .desc font metrics (px)."""
    __slots__ = ('spr', 'ox', 'oy', 'adv', 'cap', 'asc', 'desc', 'size')

    def __init__(self, spr, ox, oy, adv, cap, asc, desc, size):
        self.spr, self.ox, self.oy, self.adv, self.cap, self.asc, self.desc, self.size = \
            spr, ox, oy, adv, cap, asc, desc, size

    @property
    def w(self):
        return self.adv

    def topleft(self, x, y, anchor='ls'):
        """Sprite top-left for an anchor ('l'|'m'|'r' + 's' baseline | 'm' cap middle | 't' cap top | 'b' descent)."""
        hx = {'l': 0.0, 'm': 0.5, 'r': 1.0}[anchor[0]]
        va = anchor[1]
        if va == 's':
            base = y
        elif va == 'm':
            base = y + self.cap / 2
        elif va == 't':
            base = y + self.cap
        else:
            base = y - self.desc
        return x - self.ox - hx * self.adv, base - self.oy


@functools.lru_cache(maxsize=2048)
def _text_mask(txt, fname, size, tracking=0.0, ss=SS):
    f = font(fname, round(size * ss))
    fs = round(size * ss)
    n = len(txt)
    if tracking and n > 1:
        tr = tracking * fs
        pos = [f.getlength(txt[:i]) + i * tr for i in range(n)]
        adv = f.getlength(txt) + (n - 1) * tr
    else:
        pos = None
        adv = f.getlength(txt) if txt else 0.0
    if txt.strip():
        l, t, r, b = f.getbbox(txt, anchor='ls')
    else:
        l, t, r, b = 0, -fs * 0.7, max(adv, 1), fs * 0.2
    if pos is not None:
        r = max(r, adv + fs * 0.1)
    pad = 3 * ss
    ox = int(math.ceil((pad - min(l, 0)) / ss)) * ss
    oy = int(math.ceil((pad - t) / ss)) * ss
    Wd = int(math.ceil((ox + max(r, adv) + pad) / ss)) * ss
    Hd = int(math.ceil((oy + b + pad) / ss)) * ss
    im = Image.new('L', (Wd, Hd), 0)
    d = ImageDraw.Draw(im)
    if pos is None:
        d.text((ox, oy), txt, font=f, fill=255, anchor='ls')
    else:
        for ch, px in zip(txt, pos):
            d.text((ox + px, oy), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im, np.float32) / 255.0
    if ss > 1:
        a = cv2.resize(a, (Wd // ss, Hd // ss), interpolation=cv2.INTER_AREA)
    asc, desc = f.getmetrics()
    cap = -f.getbbox('H', anchor='ls')[1]
    return _ro(a), ox // ss, oy // ss, adv / ss, cap / ss, asc / ss, desc / ss


def text(txt, size=40, fnt='ui', color=None, tracking=0.0, opacity=1.0, grad=None, angle=0.0, weight=None):
    """Render a text run -> Txt (cached). color: colour spec (default IVORY); grad=(c0, c1) gradient fill along
    `angle`; tracking in em; weight: coverage gamma (<1 thickens, default auto 0.82 for dark text)."""
    return _text_cached(txt, float(size), fnt, _key(color), float(tracking), float(opacity), _key(grad),
                        float(angle), weight)


def _key(c):
    if c is None:
        return None
    if isinstance(c, str):
        return c
    if isinstance(c, (tuple, list)) and len(c) and isinstance(c[0], (str, tuple, list, np.ndarray)):
        return tuple(_key(x) for x in c)
    return tuple(round(float(x), 5) for x in np.asarray(c).ravel()[:3])


@functools.lru_cache(maxsize=2048)
def _text_cached(txt, size, fnt, color, tracking, opacity, grad, angle, weight):
    a, ox, oy, adv, cap, asc, desc = _text_mask(txt, fnt, size, tracking)
    c = col(color) if color is not None else _v(C['IVORY'])
    if weight is None:
        weight = 0.82 if (grad is None and float(K.lum(c)) < 0.2) else 1.0
    if weight != 1.0:
        a = a ** np.float32(weight)
    a = a * np.float32(opacity)
    h, w = a.shape
    spr = np.zeros((h, w, 4), np.float32)
    if grad is not None:
        g = _lingrad(w, h, grad[0], grad[1], angle)
        spr[..., :3] = g * a[..., None]
    else:
        spr[..., :3] = c * a[..., None]
    spr[..., 3] = a
    return Txt(_ro(spr), ox, oy, adv, cap, asc, desc, size)


def measure(txt, size=40, fnt='ui', tracking=0.0):
    """Advance width (px) of a text run."""
    return _text_mask(txt, fnt, float(size), float(tracking))[3]


def wrap(txt, size, fnt, max_w, tracking=0.0):
    """Greedy word wrap -> list of lines that fit max_w px."""
    words = txt.split()
    lines, cur = [], ''
    for wd in words:
        cand = wd if not cur else cur + ' ' + wd
        if measure(cand, size, fnt, tracking) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fit_size(txt, size, fnt, max_w, min_size=24, tracking=0.0):
    """Largest size <= size (step 1 px) whose run fits max_w."""
    s = float(size)
    while s > min_size and measure(txt, s, fnt, tracking) > max_w:
        s -= 1
    return s


def put_text(dst, x, y, txt, size=40, fnt='ui', color=None, anchor='ls', tracking=0.0, opacity=1.0, grad=None,
             angle=0.0, max_w=None, mode='over'):
    """Draw text into a sprite/canvas at integer-snapped (x, y) with an anchor ('ls', 'ms', 'mm', 'lm', 'rs',
    'lt', ...). max_w shrinks the size to fit. Returns the advance width."""
    if not txt:
        return 0.0
    if max_w is not None:
        size = fit_size(txt, size, fnt, max_w, tracking=tracking)
    t = text(txt, size, fnt, color, tracking, 1.0, grad, angle)
    x0, y0 = t.topleft(x, y, anchor)
    paste(dst, t.spr, round(x0), round(y0), opacity, mode)
    return t.adv


# =============================================================================================== surface
class Surf:
    """A small premultiplied linear RGBA drawing surface (w x h px) with analytic anti-aliased primitives.
    All coordinates are float px; shapes are computed from signed distances only inside their bbox."""

    def __init__(self, w, h, img=None):
        self.w, self.h = int(w), int(h)
        self.img = np.zeros((self.h, self.w, 4), np.float32) if img is None else img

    # ---- low level
    def _box(self, x0, y0, x1, y1, m=2):
        X0 = max(0, int(math.floor(x0)) - m)
        Y0 = max(0, int(math.floor(y0)) - m)
        X1 = min(self.w, int(math.ceil(x1)) + m)
        Y1 = min(self.h, int(math.ceil(y1)) + m)
        return X0, Y0, X1, Y1

    def fill(self, a, X0, Y0, color, opacity=1.0):
        """'over' a coverage region a (hh, ww) at (X0, Y0) with color (rgb or (hh, ww, 3) image)."""
        if a is None or a.size == 0 or opacity <= 0:
            return
        hh, ww = a.shape
        reg = self.img[Y0:Y0 + hh, X0:X0 + ww]
        m = (a * np.float32(opacity))[..., None]
        c = np.asarray(color, np.float32)
        reg[..., :3] = reg[..., :3] * (1 - m) + c * m
        reg[..., 3:4] = reg[..., 3:4] * (1 - m) + m

    def emit(self, a, X0, Y0, color, gain=1.0):
        """Add emissive light (alpha unchanged) over a region."""
        if a is None or a.size == 0 or gain == 0:
            return
        hh, ww = a.shape
        reg = self.img[Y0:Y0 + hh, X0:X0 + ww]
        reg[..., :3] += np.asarray(color, np.float32) * (a * np.float32(gain))[..., None]

    def erase(self, a, X0, Y0, amount=1.0):
        hh, ww = a.shape
        self.img[Y0:Y0 + hh, X0:X0 + ww] *= (1 - a * np.float32(amount))[..., None]

    # ---- shapes (return (coverage, X0, Y0) so callers can reuse masks)
    def rrect_mask(self, x, y, w, h, r, grow=0.0):
        X0, Y0, X1, Y1 = self._box(x - grow, y - grow, x + w + grow, y + h + grow)
        if X1 <= X0 or Y1 <= Y0:
            return None, X0, Y0
        xs, ys = _grid(X0, Y0, X1, Y1)
        d = _rr_sdf_xy(xs, ys, x + w / 2, y + h / 2, w / 2, h / 2, min(r, w / 2, h / 2)) - grow
        return _cov(d), X0, Y0

    def rrect_sdf(self, x, y, w, h, r, m=2):
        X0, Y0, X1, Y1 = self._box(x, y, x + w, y + h, m)
        xs, ys = _grid(X0, Y0, X1, Y1)
        return _rr_sdf_xy(xs, ys, x + w / 2, y + h / 2, w / 2, h / 2, min(r, w / 2, h / 2)), X0, Y0

    def rrect(self, x, y, w, h, r, color, opacity=1.0, emit=False):
        a, X0, Y0 = self.rrect_mask(x, y, w, h, r)
        if a is not None:
            (self.emit if emit else self.fill)(a, X0, Y0, color, opacity)
        return a, X0, Y0

    def rrect_grad(self, x, y, w, h, r, c0, c1, angle=35.0, opacity=1.0, gain=1.0):
        a, X0, Y0 = self.rrect_mask(x, y, w, h, r)
        if a is not None:
            hh, ww = a.shape
            g = _lingrad(ww, hh, c0, c1, angle, gain)
            self.fill(a, X0, Y0, g, opacity)
        return a, X0, Y0

    def stroke_rrect(self, x, y, w, h, r, width, color, opacity=1.0, inset=True, weight=None, emit=False):
        """Rounded-rect outline; inset=True keeps it inside the shape. weight(xs, ys) -> per-pixel gain."""
        d, X0, Y0 = self.rrect_sdf(x, y, w, h, r, m=int(width) + 3)
        off = width / 2 if inset else 0.0
        a = _cov(np.abs(d + off) - width / 2)
        if weight is not None:
            xs, ys = _grid(X0, Y0, X0 + a.shape[1], Y0 + a.shape[0])
            a = a * weight(xs, ys)
        (self.emit if emit else self.fill)(a, X0, Y0, color, opacity)
        return a, X0, Y0

    def circle(self, cx, cy, r, color, opacity=1.0, emit=False):
        X0, Y0, X1, Y1 = self._box(cx - r, cy - r, cx + r, cy + r)
        if X1 <= X0 or Y1 <= Y0:
            return None, X0, Y0
        xs, ys = _grid(X0, Y0, X1, Y1)
        a = _cov(np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) - r)
        (self.emit if emit else self.fill)(a, X0, Y0, color, opacity)
        return a, X0, Y0

    def ring(self, cx, cy, r, width, color, opacity=1.0, emit=False):
        X0, Y0, X1, Y1 = self._box(cx - r - width, cy - r - width, cx + r + width, cy + r + width)
        xs, ys = _grid(X0, Y0, X1, Y1)
        a = _cov(np.abs(np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) - r) - width / 2)
        (self.emit if emit else self.fill)(a, X0, Y0, color, opacity)
        return a, X0, Y0

    def glow(self, a, X0, Y0, color, sigmas=(6, 18), strength=1.0, weights=None, knock=0.85):
        """Emissive multi-radius glow of a coverage region (spreads outside the region, clipped to the surf);
        knock 0..1 removes that much of it inside the region itself (keeps fills saturated)."""
        if a is None:
            return
        weights = weights or [1.0 / (1 + 0.6 * i) for i in range(len(sigmas))]
        p = int(max(sigmas) * 2.8)
        full = np.zeros((self.h, self.w), np.float32)
        hh, ww = a.shape
        full[Y0:Y0 + hh, X0:X0 + ww] = a
        xa, ya = max(0, X0 - p), max(0, Y0 - p)
        xb, yb = min(self.w, X0 + ww + p), min(self.h, Y0 + hh + p)
        sub = full[ya:yb, xa:xb]
        acc = np.zeros_like(sub)
        for s, wt in zip(sigmas, weights):
            acc += K.gblur(sub, s, border='constant') * np.float32(wt)
        if knock > 0:
            acc *= 1 - sub * np.float32(knock)
        self.emit(acc, xa, ya, color, strength)

    def sheen(self, x, y, w, h, r, amount=0.10, top=0.0, bottom=0.55, color=None):
        """Emissive vertical gloss inside a rounded rect: `amount` at the top fading to 0 at `bottom` (fraction)."""
        a, X0, Y0 = self.rrect_mask(x, y, w, h, r)
        if a is None:
            return
        yy = (np.arange(a.shape[0], dtype=np.float32) + Y0 + 0.5 - y) / max(h, 1)
        g = np.clip((bottom - yy) / max(bottom - top, 1e-3), 0, 1) ** 1.5
        self.emit(a * g[:, None], X0, Y0, col(color) if color is not None else _v(C['WHITE']), amount)

    def text(self, x, y, txt, size=40, fnt='ui', color=None, anchor='ls', tracking=0.0, opacity=1.0, grad=None,
             angle=0.0, max_w=None):
        return put_text(self.img, x, y, txt, size, fnt, color, anchor, tracking, opacity, grad, angle, max_w)

    def paste(self, spr, x, y, opacity=1.0, mode='over', anchor=(0.0, 0.0)):
        sh, sw = spr.shape[:2]
        paste(self.img, spr, x - anchor[0] * sw, y - anchor[1] * sh, opacity, mode)

    def sprite(self):
        return self.img


# =============================================================================================== vector paths
_PATH_TOK = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)')


def _arc_pts(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cp * dx2 + sp * dy2
    y1p = -sp * dx2 + cp * dy2
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den > 0 else 0.0
    if fa == fs:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dth > 0:
        dth -= 2 * math.pi
    elif fs and dth < 0:
        dth += 2 * math.pi
    n = max(3, int(math.ceil(abs(dth) * max(rx, ry) / 0.35)))
    out = []
    for i in range(1, n + 1):
        th = th1 + dth * i / n
        out.append((cx + rx * math.cos(th) * cp - ry * math.sin(th) * sp,
                    cy + rx * math.cos(th) * sp + ry * math.sin(th) * cp))
    return out


def _bez(p0, p1, p2, p3, n=16):
    t = np.linspace(0, 1, n + 1)[1:, None]
    p0, p1, p2, p3 = (np.asarray(p, np.float64) for p in (p0, p1, p2, p3))
    pts = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
    return [tuple(p) for p in pts]


def parse_path(d):
    """SVG path data (M L H V C S Q T A Z, absolute + relative) -> list of (points (N, 2) array, closed)."""
    toks = [(m.group(1), m.group(2)) for m in _PATH_TOK.finditer(d)]
    i = 0
    subs = []
    pts = []
    x = y = 0.0
    sx = sy = 0.0
    cmd = None
    last_c = None
    last_q = None

    def nums(k):
        nonlocal i
        out = []
        while len(out) < k:
            c, n = toks[i]
            if c:
                raise ValueError('path: expected number')
            out.append(float(n))
            i += 1
        return out

    def flush(closed):
        nonlocal pts
        if len(pts) >= 2:
            subs.append((np.array(pts, np.float64), closed))
        pts = []

    while i < len(toks):
        c, n = toks[i]
        if c:
            cmd = c
            i += 1
            if cmd in 'Zz':
                flush(True)
                x, y = sx, sy
                cmd = None
                last_c = last_q = None
                continue
        elif cmd is None:
            raise ValueError('path: number without command')
        rel = cmd.islower()
        C_ = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if C_ == 'M':
            a, b = nums(2)
            flush(False)
            x, y = ox + a, oy + b
            sx, sy = x, y
            pts = [(x, y)]
            cmd = 'l' if rel else 'L'
            last_c = last_q = None
            continue
        if not pts:
            pts = [(x, y)]
        if C_ == 'L':
            a, b = nums(2)
            x, y = ox + a, oy + b
            pts.append((x, y))
            last_c = last_q = None
        elif C_ == 'H':
            a, = nums(1)
            x = (x if rel else 0.0) + a
            pts.append((x, y))
            last_c = last_q = None
        elif C_ == 'V':
            b, = nums(1)
            y = (y if rel else 0.0) + b
            pts.append((x, y))
            last_c = last_q = None
        elif C_ == 'C':
            a = nums(6)
            p1 = (ox + a[0], oy + a[1])
            p2 = (ox + a[2], oy + a[3])
            p3 = (ox + a[4], oy + a[5])
            pts += _bez((x, y), p1, p2, p3)
            last_c = p2
            last_q = None
            x, y = p3
        elif C_ == 'S':
            a = nums(4)
            p1 = (2 * x - last_c[0], 2 * y - last_c[1]) if last_c else (x, y)
            p2 = (ox + a[0], oy + a[1])
            p3 = (ox + a[2], oy + a[3])
            pts += _bez((x, y), p1, p2, p3)
            last_c = p2
            last_q = None
            x, y = p3
        elif C_ == 'Q':
            a = nums(4)
            q = (ox + a[0], oy + a[1])
            p3 = (ox + a[2], oy + a[3])
            p1 = (x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts += _bez((x, y), p1, p2, p3)
            last_q = q
            last_c = None
            x, y = p3
        elif C_ == 'T':
            a = nums(2)
            q = (2 * x - last_q[0], 2 * y - last_q[1]) if last_q else (x, y)
            p3 = (ox + a[0], oy + a[1])
            p1 = (x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts += _bez((x, y), p1, p2, p3)
            last_q = q
            last_c = None
            x, y = p3
        elif C_ == 'A':
            a = nums(7)
            x2, y2 = ox + a[5], oy + a[6]
            pts += _arc_pts(x, y, a[0], a[1], a[2], int(a[3]), int(a[4]), x2, y2)
            x, y = x2, y2
            last_c = last_q = None
        else:
            raise ValueError('path: unsupported command %r' % cmd)
    flush(False)
    return subs


def _seg_dist(xs, ys, A, B, chunk=8192):
    """Min distance from pixel centres (xs, ys same shape) to segments A->B ((n, 2) arrays)."""
    P = np.stack([xs.ravel(), ys.ravel()], 1).astype(np.float32)
    A = A.astype(np.float32)
    BA = (B - A).astype(np.float32)
    L2 = np.maximum((BA ** 2).sum(1), 1e-9)
    out = np.empty(len(P), np.float32)
    for s in range(0, len(P), chunk):
        p = P[s:s + chunk]
        pax = p[:, None, 0] - A[None, :, 0]
        pay = p[:, None, 1] - A[None, :, 1]
        h = np.clip((pax * BA[None, :, 0] + pay * BA[None, :, 1]) / L2[None], 0, 1)
        dx = pax - BA[None, :, 0] * h
        dy = pay - BA[None, :, 1] * h
        out[s:s + chunk] = np.sqrt((dx * dx + dy * dy).min(1))
    return out.reshape(xs.shape)


def _segments(polys):
    A, B = [], []
    for pts, closed in polys:
        p = np.asarray(pts, np.float64)
        if closed and len(p) > 2:
            p = np.vstack([p, p[:1]])
        if len(p) == 1:
            p = np.vstack([p, p])
        A.append(p[:-1])
        B.append(p[1:])
    if not A:
        return np.zeros((0, 2)), np.zeros((0, 2))
    return np.vstack(A), np.vstack(B)


def stroke_mask(polys, w, h, width, scale=1.0, offset=(0.0, 0.0)):
    """Anti-aliased round-cap / round-join stroke coverage (h, w) of polylines [(pts, closed)], with
    pts mapped by p * scale + offset (px) and `width` in px."""
    A, B = _segments(polys)
    m = np.zeros((h, w), np.float32)
    if len(A) == 0:
        return m
    A = A * scale + np.asarray(offset)
    B = B * scale + np.asarray(offset)
    lo = np.minimum(A, B).min(0) - width
    hi = np.maximum(A, B).max(0) + width
    X0, Y0 = max(0, int(lo[0]) - 2), max(0, int(lo[1]) - 2)
    X1, Y1 = min(w, int(hi[0]) + 3), min(h, int(hi[1]) + 3)
    if X1 <= X0 or Y1 <= Y0:
        return m
    xs, ys = _grid(X0, Y0, X1, Y1)
    d = _seg_dist(xs, ys, A, B)
    m[Y0:Y1, X0:X1] = _cov(d - width / 2)
    return m


def fill_mask(polys, w, h, scale=1.0, offset=(0.0, 0.0), ss=4):
    """Anti-aliased even-odd fill coverage (h, w) of closed polygons (pts * scale + offset px)."""
    big = np.zeros((h * ss, w * ss), np.uint8)
    cnts = []
    for pts, _ in polys:
        p = (np.asarray(pts) * scale + np.asarray(offset)) * ss
        cnts.append(np.round(p * 16).astype(np.int32))
    if cnts:
        cv2.fillPoly(big, cnts, 255, cv2.LINE_AA, shift=4)
    return cv2.resize(big.astype(np.float32) / 255.0, (w, h), interpolation=cv2.INTER_AREA)


def _poly_len(p):
    return float(np.sqrt((np.diff(p, axis=0) ** 2).sum(1)).sum()) if len(p) > 1 else 0.0


def trim_polyline(p, t0, t1):
    """Part of a polyline between arc-length fractions t0..t1 (draw-on animation)."""
    p = np.asarray(p, np.float64)
    seg = np.sqrt((np.diff(p, axis=0) ** 2).sum(1))
    cum = np.r_[0, np.cumsum(seg)]
    L = cum[-1]
    if L <= 0 or t1 <= t0:
        return p[:1]
    a, b = t0 * L, t1 * L

    def at(s):
        k = int(np.clip(np.searchsorted(cum, s) - 1, 0, len(seg) - 1))
        f = (s - cum[k]) / max(seg[k], 1e-9)
        return p[k] + (p[k + 1] - p[k]) * f
    inner = [p[k] for k in range(len(p)) if a < cum[k] < b]
    return np.array([at(a)] + inner + [at(b)])


# =============================================================================================== icons
def _gear_path(n=8, r0=6.8, r1=9.6, cx=12, cy=12):
    pts = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        for f, r in ((-0.30, r0), (-0.16, r1), (0.16, r1), (0.30, r0)):
            a = a0 + f * 2 * math.pi / n
            pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return 'M' + ' L'.join('%.3f %.3f' % p for p in pts) + ' Z'


_HEART = ('M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 '
          '2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z')
_POUND = ['M17 7.2c0-5.4-8-5.4-8 0', 'M9 7.2v8.6c0 2.2-.8 3.8-2.6 5.2', 'M6.2 21h12', 'M5.8 13.4h9.6']

ICON_DEFS = {
    'home': ['M3 10.5L12 3l9 7.5', 'M5 9v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9', 'M9.5 21v-5.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1V21'],
    'house': ['M3 10.5L12 3l9 7.5', 'M5 9v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9', ('f', _HEART, (0.36, 12, 15.2))],
    'heart': [_HEART],
    'chat': ['M7.9 20A9 9 0 1 0 4 16.1L2 22Z', ('dot', 8, 12, 1.25), ('dot', 12, 12, 1.25), ('dot', 16, 12, 1.25)],
    'calendar': [('rect', 3, 4.5, 18, 17, 2.6), 'M8 2.5v4', 'M16 2.5v4', 'M3 10h18', ('dot', 8, 14.2, 1.1),
                 ('dot', 12, 14.2, 1.1), ('dot', 16, 14.2, 1.1), ('dot', 8, 17.8, 1.1), ('dot', 12, 17.8, 1.1)],
    'user': [('circle', 12, 7.8, 4.2), 'M20 21v-1.6a4.4 4.4 0 0 0-4.4-4.4H8.4A4.4 4.4 0 0 0 4 19.4V21'],
    'users': [('circle', 9, 7.8, 4.0), 'M16 21v-1.6a4.4 4.4 0 0 0-4.4-4.4H6.4A4.4 4.4 0 0 0 2 19.4V21',
              'M15.8 3.4a4 4 0 0 1 0 7.8', 'M22 21v-1.6a4.4 4.4 0 0 0-3.3-4.25'],
    'settings': [_gear_path(), ('circle', 12, 12, 3.0)],
    'shield': ['M12 22C12 22 20 18.2 20 12V5.2L12 2.2 4 5.2V12C4 18.2 12 22 12 22Z', 'M8.6 12.2l2.4 2.4 4.4-4.6'],
    'star': ['M12 2.6l2.95 6.0 6.6.95-4.78 4.65 1.13 6.57L12 17.67l-5.9 3.1 1.13-6.57L2.45 9.55l6.6-.95Z'],
    'pound': list(_POUND),
    'check': ['M20 6.5L9.2 17.3 4 12.1'],
    'leaf': ['M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z',
             'M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12'],
    'phone': ['M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07'
              '-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 '
              '16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92Z'],
    'arrow_right': ['M4.5 12h15', 'M13 5.5l6.5 6.5-6.5 6.5'],
    'search': [('circle', 10.8, 10.8, 7.2), 'M21 21l-4.9-4.9'],
    'bell': ['M6 8.5A6 6 0 0 1 18 8.5C18 15 21 17 21 17H3S6 15 6 8.5', 'M10.3 21a1.94 1.94 0 0 0 3.4 0'],
    'book': ['M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2Z', 'M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7Z'],
    'graduation': ['M2 9.5L12 4.5l10 5-10 5Z', 'M6 11.6v4.9c3.2 3 8.8 3 12 0v-4.9', 'M22 9.5v6'],
    'sparkle': ['M11 3.5Q12 11 19.5 12.5 12 14 11 21.5 10 14 2.5 12.5 10 11 11 3.5Z', 'M19.5 2.5v4', 'M17.5 4.5h4',
                ('dot', 19.5, 19.5, 1.2)],
    'clock': [('circle', 12, 12, 9.6), 'M12 6.5V12l3.6 2.1'],
    'globe': [('circle', 12, 12, 9.6), 'M2.4 12h19.2', 'M12 2.4a14.5 14.5 0 0 0 0 19.2 14.5 14.5 0 0 0 0-19.2'],
    'puzzle': ['M5 6.5h4a2.3 2.3 0 1 1 4.6 0h4v4.2a2.3 2.3 0 1 1 0 4.6v4.2H5v-4.2a2.3 2.3 0 1 0 0-4.6Z'],
    'key': [('circle', 7.5, 16.0, 4.6), 'M10.8 12.7L20.5 3', 'M16.6 6.9l3 3', 'M14.3 9.2l2.2 2.2'],
    # extras
    'chart': ['M3 3v15a3 3 0 0 0 3 3h15', 'M8 17v-4', 'M12.5 17V8', 'M17 17v-6.5'],
    'grid': [('rect', 3, 3, 7.5, 7.5, 2), ('rect', 13.5, 3, 7.5, 7.5, 2), ('rect', 3, 13.5, 7.5, 7.5, 2),
             ('rect', 13.5, 13.5, 7.5, 7.5, 2)],
    'pin': ['M20 10C20 16 12 22 12 22S4 16 4 10A8 8 0 0 1 20 10Z', ('circle', 12, 10, 3)],
    'plus': ['M12 5v14', 'M5 12h14'],
    'coin': [('circle', 12, 12, 9.8)] + [('s', d, (0.55, 12, 12.3)) for d in _POUND],
    'mail': [('rect', 2.5, 5, 19, 14, 2.5), 'M3 7l9 6 9-6'],
    'menu': ['M4 6.5h16', 'M4 12h16', 'M4 17.5h10'],
}
ICONS = tuple(ICON_DEFS)


def _tf_polys(polys, tf):
    if tf is None:
        return polys
    s, cx, cy = tf
    return [((p - 12.0) * s + (cx, cy), c) for p, c in polys]


@functools.lru_cache(maxsize=64)
def icon_geometry(name):
    """(stroke_polys, fill_polys, closed_polys) in the 24-unit icon grid."""
    strokes, fills, closed = [], [], []
    for el in ICON_DEFS[name]:
        if isinstance(el, str):
            ps = parse_path(el)
            strokes += ps
            closed += [p for p in ps if p[1]]
        elif el[0] == 's':
            ps = _tf_polys(parse_path(el[1]), el[2])
            strokes += ps
        elif el[0] == 'f':
            fills += _tf_polys(parse_path(el[1]), el[2] if len(el) > 2 else None)
        elif el[0] == 'dot':
            _, cx, cy, r = el
            a = np.linspace(0, 2 * math.pi, 48, endpoint=False)
            fills.append((np.c_[cx + r * np.cos(a), cy + r * np.sin(a)], True))
        elif el[0] == 'circle':
            _, cx, cy, r = el
            a = np.linspace(0, 2 * math.pi, max(24, int(r * 12)), endpoint=False)
            p = (np.c_[cx + r * np.cos(a), cy + r * np.sin(a)], True)
            strokes.append(p)
            closed.append(p)
        elif el[0] == 'rect':
            _, x, y, w, h, r = el
            d = 'M%f %fH%fA%f %f 0 0 1 %f %fV%fA%f %f 0 0 1 %f %fH%fA%f %f 0 0 1 %f %fV%fA%f %f 0 0 1 %f %fZ' % (
                x + r, y, x + w - r, r, r, x + w, y + r, y + h - r, r, r, x + w - r, y + h, x + r, r, r, x, y + h - r,
                y + r, r, r, x + r, y)
            ps = parse_path(d)
            strokes += ps
            closed += ps
    return strokes, fills, closed


def icon_mask(name, size=48, stroke=2.0, fill_a=0.0, pad=0):
    """Coverage (size+2p)^2 of icon `name` drawn in a size px box (24-unit grid, stroke in grid units)."""
    return _icon_mask(name, int(size), float(stroke), float(fill_a), int(pad))


@functools.lru_cache(maxsize=256)
def _icon_mask(name, size, stroke, fill_a, pad):
    strokes, fills, closed = icon_geometry(name)
    n = size + 2 * pad
    s = size / 24.0
    m = stroke_mask(strokes, n, n, stroke * s, s, (pad, pad))
    if fills:
        m = np.maximum(m, fill_mask(fills, n, n, s, (pad, pad)))
    if fill_a > 0 and closed:
        f = fill_mask(closed, n, n, s, (pad, pad))
        m = np.maximum(m, f * np.float32(fill_a))
    return _ro(m)


def icon(name, size=48, color=None, stroke=2.0, fill_a=0.0, glow=0.0, glow_color=None, grad=None, pad=None):
    """Vector icon sprite (crisp at any size, rounded strokes). name in ICONS. color: spec (default IVORY);
    grad=(c0, c1) gradient fill at 35 deg; fill_a: duotone fill of closed shapes; glow: emissive glow
    strength (adds padding). Returns a (size+2p)^2 sprite with the icon box centred."""
    return _icon_cached(name, int(size), _key(color), float(stroke), float(fill_a), float(glow), _key(glow_color),
                        _key(grad), pad)


@functools.lru_cache(maxsize=512)
def _icon_cached(name, size, color, stroke, fill_a, glow, glow_color, grad, pad):
    if pad is None:
        pad = int(math.ceil(size * 0.35)) if glow > 0 else 2
    m = icon_mask(name, size, stroke, fill_a, pad)
    n = m.shape[0]
    spr = np.zeros((n, n, 4), np.float32)
    if grad is not None:
        g = _lingrad(n, n, grad[0], grad[1], 35.0)
        spr[..., :3] = g * m[..., None]
    else:
        spr[..., :3] = col(color if color is not None else C['IVORY']) * m[..., None]
    spr[..., 3] = m
    if glow > 0:
        gc = col(glow_color) if glow_color is not None else (spr[..., :3].sum((0, 1)) / max(m.sum(), 1e-6))
        g = np.zeros((n, n), np.float32)
        for sg, wt in ((size * 0.05, 1.0), (size * 0.14, 0.6)):
            g += K.gblur(m, max(sg, 0.8), border='constant') * np.float32(wt)
        spr[..., :3] += np.asarray(gc, np.float32) * (g * np.float32(glow))[..., None]
    return _ro(spr)


# =============================================================================================== glass panels
def _perimeter_s(x, y, w, h, r):
    """Arc-length parameter s in [0, 1) of the nearest rounded-rect boundary point, clockwise from the top
    centre. x, y relative to the card centre (arrays)."""
    hx, hy = w / 2 - r, h / 2 - r
    cx = np.clip(x, -hx, hx)
    cy = np.clip(y, -hy, hy)
    dx, dy = x - cx, y - cy
    inside = (dx == 0) & (dy == 0)
    side_lr = inside & ((hx - np.abs(x)) < (hy - np.abs(y)))
    side_tb = inside & ~side_lr
    dx = np.where(side_lr, np.sign(x) + (x == 0), dx)
    dy = np.where(side_tb, np.sign(y) + (y == 0), dy)
    q = math.pi * r / 2
    Ls = [hx, q, 2 * hy, q, 2 * hx, q, 2 * hy, q, hx]
    off = np.cumsum([0] + Ls)
    L = off[-1]
    phi = np.arctan2(dy, dx)            # screen angle, y down: -pi/2 = up
    on_x = dy == 0                      # left / right edges
    on_y = dx == 0                      # top / bottom edges
    s = np.zeros_like(x, dtype=np.float32)
    # corners
    corner = ~(on_x | on_y)
    tr = corner & (dx > 0) & (dy < 0)
    br = corner & (dx > 0) & (dy > 0)
    bl = corner & (dx < 0) & (dy > 0)
    tl = corner & (dx < 0) & (dy < 0)
    s = np.where(tr, off[1] + (phi + math.pi / 2) * r, s)
    s = np.where(br, off[3] + phi * r, s)
    s = np.where(bl, off[5] + (phi - math.pi / 2) * r, s)
    s = np.where(tl, off[7] + (phi + math.pi) * r, s)
    top = on_y & (dy < 0)
    bot = on_y & (dy > 0)
    right = on_x & (dx > 0)
    left = on_x & (dx < 0)
    s = np.where(top & (cx >= 0), cx, s)
    s = np.where(top & (cx < 0), off[8] + (cx + hx), s)
    s = np.where(right, off[2] + (cy + hy), s)
    s = np.where(bot, off[4] + (hx - cx), s)
    s = np.where(left, off[6] + (hy - cy), s)
    return (s / L).astype(np.float32) % 1.0


def frost_poly(cv, poly, sigma, amount=1.0):
    """Frosted-glass blur of the canvas inside a screen polygon (N, 2) (e.g. a projected card outline), in
    place. The region is blurred once at reduced resolution (sigma >= 8: 1/4, >= 4: 1/2) and blended in with an
    anti-aliased mask, so it costs ~10-30 ms for a full window. Returns the touched bbox or None."""
    poly = np.asarray(poly, np.float64)
    if sigma < 0.5 or amount <= 0 or len(poly) < 3 or not np.isfinite(poly).all():
        return None
    Hc, Wc = cv.shape[:2]
    X0, Y0 = max(0, int(math.floor(poly[:, 0].min()))), max(0, int(math.floor(poly[:, 1].min())))
    X1, Y1 = min(Wc, int(math.ceil(poly[:, 0].max())) + 1), min(Hc, int(math.ceil(poly[:, 1].max())) + 1)
    if X1 - X0 < 2 or Y1 - Y0 < 2:
        return None
    m = int(sigma * 2.5) + 2
    xa, ya, xb, yb = max(0, X0 - m), max(0, Y0 - m), min(Wc, X1 + m), min(Hc, Y1 + m)
    srcr = cv[ya:yb, xa:xb, :3]
    f = 4 if sigma >= 8 else (2 if sigma >= 4 else 1)
    if f > 1:
        sw, sh = max(1, (xb - xa) // f), max(1, (yb - ya) // f)
        small = cv2.resize(srcr, (sw, sh), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), sigma / f)
        bl = cv2.resize(small, (xb - xa, yb - ya), interpolation=cv2.INTER_LINEAR)
    else:
        bl = cv2.GaussianBlur(srcr, (0, 0), sigma)
    bl = bl[Y0 - ya:Y1 - ya, X0 - xa:X1 - xa]
    mask = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
    pts = np.round((poly - (X0, Y0)) * 16).astype(np.int32)
    cv2.fillPoly(mask, [pts], 255, cv2.LINE_AA, shift=4)
    k = mask.astype(np.float32) * np.float32(min(1.0, amount) / 255.0)
    reg = cv[Y0:Y1, X0:X1, :3]
    reg += (bl - reg) * k[..., None]
    return X0, Y0, X1, Y1


class Panel:
    """A glass (or any) UI panel: padded `face` sprite (body + content + emissive rim/glow; alpha only on the
    body so it doubles as the frost mask), a soft `shadow` (stored at 1/4 res) in the same padded frame,
    the body size (w, h), corner radius r, padding `pad`, look name and default frost sigma (px at scale 1).
    Card-local coordinates: (0, 0) = top-left corner of the body, (w, h) = bottom-right.

        p = glass_card(640, 400, look='neon')
        p.draw(cv, 540, 960)                                  # 2D, anchor = card centre
        p.plane(cv, cam, (0, 0, 0), 640, rot=(8, -14, 0))    # 3D plane (width = body width, world units)
        f = p.face_at(sweep=0.3)                              # writable face copy with a rim light comet
        p.put(f, spr, 40, 120)                                # paste a sprite at card-local px
        p.plane(cv, cam, (0, 0, 0), 640, rot=(8, -14, 0), face=f)
        xy = p.screen(cam, (0, 0, 0), 640, (8, -14, 0), 120, 200)   # where card px (120, 200) lands
    """

    def __init__(self, face, shadow, w, h, r, pad, look='neon', frost=16.0, rim_color=None, rim2=None, meta=None,
                 spad=None):
        self.face, self.shadow = face, shadow
        self.w, self.h, self.r, self.pad = int(w), int(h), float(r), int(pad)
        self.spad = (float(pad), float(pad)) if spad is None else tuple(spad)   # shadow padding (x, y) body px
        self.look = look
        self.frost = float(frost)
        self.rim_color = rim_color
        self.rim2 = rim2
        self.meta = dict(meta or {})
        self.rim_layer = None          # emissive static rim (+ glow) baked into face; face_at(rim_gain=) scales it
        self._band = None
        self._grid = None

    # ---- geometry
    @property
    def size(self):
        return self.w, self.h

    @property
    def pw(self):
        return self.w + 2 * self.pad

    @property
    def ph(self):
        return self.h + 2 * self.pad

    def anchor(self, anchor=(0.5, 0.5)):
        """core.draw / draw_plane anchor fraction (of the padded sprite) for a body-relative anchor."""
        return ((self.pad + anchor[0] * self.w) / self.pw, (self.pad + anchor[1] * self.h) / self.ph)

    def uv(self, x, y):
        """Normalised padded-sprite uv of card-local px."""
        return ((self.pad + x) / self.pw, (self.pad + y) / self.ph)

    def world(self, center, width, rot, x, y, anchor=(0.5, 0.5), z=0.0):
        """World point of card-local px (x, y) for a card drawn with plane(center, width, rot, anchor); z moves
        along the card normal (negative = toward the viewer)."""
        k = width / self.w
        P = K.plane_point(center, self.pw * k, self.ph * k, rot, self.uv(x, y), self.anchor(anchor))
        if z:
            P = P + _normal(rot) * z
        return P

    def screen(self, cam, center, width, rot, x, y, anchor=(0.5, 0.5), z=0.0):
        """Screen px of card-local px (x, y) (e.g. to put a cursor on a tilted window)."""
        xy, d = cam.project(self.world(center, width, rot, x, y, anchor, z))
        return xy[0]

    def screen2d(self, x0, y0, x, y, scale=1.0, anchor=(0.5, 0.5)):
        """Canvas px of card-local (x, y) for a 2D draw at (x0, y0) with scale (no rotation)."""
        return x0 + (x - anchor[0] * self.w) * scale, y0 + (y - anchor[1] * self.h) * scale

    # ---- faces
    def copy(self):
        return self.face.copy()

    def put(self, face, spr, x, y, anchor=(0.0, 0.0), opacity=1.0, mode='over', scale=1.0):
        """Composite spr onto a face copy at card-local (x, y) with an anchor (fractions of spr)."""
        if scale == 1.0:
            sh, sw = spr.shape[:2]
            paste(face, spr, self.pad + x - anchor[0] * sw, self.pad + y - anchor[1] * sh, opacity, mode)
        else:
            K.draw(face, spr, self.pad + x, self.pad + y, scale=scale, anchor=anchor, opacity=opacity, mode=mode)
        return face

    def text(self, face, x, y, txt, size=40, fnt='ui', color=None, anchor='ls', **kw):
        return put_text(face, self.pad + x, self.pad + y, txt, size, fnt, color, anchor, **kw)

    def _band_data(self, band=44):
        """Pixels within `band` px of the edge, sorted by perimeter parameter s, with the phase-independent
        comet profiles precomputed: (flat_idx, s, core_profile, glow_profile)."""
        if self._band is None:
            p = self.pad
            ys, xs = np.mgrid[0:self.ph, 0:self.pw].astype(np.float32)
            x = xs + 0.5 - (p + self.w / 2)
            y = ys + 0.5 - (p + self.h / 2)
            d = _rr_sdf_xy(x, y, 0, 0, self.w / 2, self.h / 2, self.r)
            sel = np.abs(d) < band
            idx = np.flatnonzero(sel.ravel())
            s = _perimeter_s(x.ravel()[idx], y.ravel()[idx], self.w, self.h, self.r)
            order = np.argsort(s)
            dd = d.ravel()[idx][order].astype(np.float32)
            ad = np.abs(dd)
            core = np.exp(-((dd - 0.2) / 1.2) ** 2).astype(np.float32)
            taper = np.clip((band - ad) / (band * 0.5), 0, 1) ** 2 * np.where(dd < 0, 0.55, 1.0)
            glw = ((1.1 * np.exp(-ad / 5.0) + 0.45 * np.exp(-ad / 16.0)) * taper).astype(np.float32)
            keep = (core > 1e-3) | (glw > 1e-3)
            self._band = (idx[order][keep], s[order][keep].astype(np.float32), core[keep], glw[keep])
        return self._band

    def outline(self, n_arc=10):
        """(N, 2) card-local points along the body outline (clockwise)."""
        r, w, h = self.r, self.w, self.h
        pts = []
        for cx, cy, a0 in ((w - r, r, -90), (w - r, h - r, 0), (r, h - r, 90), (r, r, 180)):
            for k in range(n_arc + 1):
                a = math.radians(a0 + 90 * k / n_arc)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return np.array(pts, np.float64)

    def _uvgrid(self):
        if self._grid is None:
            ys, xs = np.mgrid[0:self.ph, 0:self.pw].astype(np.float32)
            u = (xs + 0.5 - self.pad) / self.w
            v = (ys + 0.5 - self.pad) / self.h
            d = _rr_sdf_xy(xs + 0.5, ys + 0.5, self.pad + self.w / 2, self.pad + self.h / 2, self.w / 2, self.h / 2,
                           self.r)
            self._grid = (u, v, _cov(d))
        return self._grid

    def face_at(self, sweep=None, sweep_len=0.14, sweep_gain=1.0, sweep_color=None, sweeps=1, light=None,
                light_gain=None, light_angle=-28.0, light_width=0.07, rim_gain=None, face=None, copy=True):
        """Face for one frame. sweep: phase 0..1 of a neon comet running clockwise round the edge (from the
        top centre; sweeps=2 adds an opposite one); light: 0..1 diagonal specular light sweep across the body;
        rim_gain: multiplier on the baked static neon rim + glow (0 = off, 1 = as built, 2 = twice as bright).
        face: start from this face instead of self.face. Returns a writable array when copy=True."""
        f = self.face if face is None else face
        if copy or sweep is not None or light is not None or rim_gain is not None:
            f = f.copy() if (copy or face is None) else f
        if rim_gain is not None and rim_gain != 1.0 and self.rim_layer is not None:
            f += self.rim_layer * np.float32(rim_gain - 1.0)
        if sweep is not None and sweep_gain > 0:
            self._add_sweep(f, sweep, sweep_len, sweep_gain, sweep_color, sweeps)
        if light is not None and 0.0 < light < 1.0:
            self._add_light(f, light, light_gain, light_angle, light_width)
        return f

    def _add_sweep(self, f, phase, length, gain, color, sweeps):
        idx, s, core_p, glw_p = self._band_data()
        L = look(self.look)
        c_head = col(color) if color is not None else (self.rim2 if self.rim2 is not None else L.rim2)
        c_tail = self.rim_color if self.rim_color is not None else L.rim
        c_core = _v(K.mix(c_head, C['WHITE'], 0.6))
        flat = f.reshape(-1, 4)
        head = 0.016
        k_dark = 1.0 if L.dark else 0.55
        e0 = math.exp(-3.0)
        for k in range(sweeps):
            ph = (phase + k / sweeps) % 1.0
            lo, hi = ph - length * 3.0, ph + head * 3.0
            sel = []
            for a, b in ((lo, hi), (lo + 1, hi + 1), (lo - 1, hi - 1)):
                i0, i1 = np.searchsorted(s, [max(a, 0.0), min(b, 1.0)])
                if i1 > i0:
                    sel.append(slice(i0, i1))
            for sl in sel:
                ds = (s[sl] - np.float32(ph) + np.float32(0.5)) % np.float32(1.0) - np.float32(0.5)
                hd = np.exp(-(ds / np.float32(head)) ** 2)
                tail = np.clip((np.exp(ds / np.float32(length)) - e0) / (1 - e0), 0, 1)
                inten = np.where(ds > 0, hd, np.maximum(tail, hd))
                g = inten * np.float32(gain * k_dark)
                cp = core_p[sl] * g
                a_core = cp * hd * (2.4 + 4.0 * hd)
                a_col = cp * (1 - hd) * 2.4 + glw_p[sl] * g * 1.6
                cc = c_tail[None, :] + (c_head - c_tail)[None, :] * inten[:, None]
                flat[idx[sl], :3] += a_core[:, None] * c_core + a_col[:, None] * cc

    def _add_light(self, f, u_, gain, angle, width):
        u, v, body = self._uvgrid()
        L = look(self.look)
        gain = (0.14 if L.dark else 0.35) if gain is None else gain
        a = math.radians(angle)
        q = u * math.cos(a) * self.w / max(self.w, self.h) - v * math.sin(a) * self.h / max(self.w, self.h)
        qmin, qmax = float(q[body > 0.5].min()), float(q[body > 0.5].max())
        c = qmin - 0.25 + (qmax - qmin + 0.5) * u_
        band = 0.55 * np.exp(-((q - c) / width) ** 2) + 0.9 * np.exp(-((q - c) / (width * 0.22)) ** 2) + \
            0.30 * np.exp(-((q - c + width * 2.4) / (width * 0.35)) ** 2)
        e = (band * body * np.float32(gain)).astype(np.float32)
        f[..., :3] += e[..., None] * col(C['WHITE'])
        if not L.dark:
            f[..., 3] = np.clip(f[..., 3] + e * 0.15, 0, 1)

    # ---- drawing
    def draw(self, cv, x, y, scale=1.0, rot=0.0, opacity=1.0, anchor=(0.5, 0.5), face=None, frost=None, shadow=1.0,
             blur=0.0, mode='over'):
        """2D draw with the body anchor at canvas (x, y): shadow, then the face with background frost."""
        if opacity <= 1e-4:
            return None
        ap = self.anchor(anchor)
        sc = (scale, scale) if np.ndim(scale) == 0 else tuple(scale)
        if shadow > 0 and self.shadow is not None:
            sh, sw = self.shadow.shape[:2]
            spx, spy = self.spad
            spw, sph = self.w + 2 * spx, self.h + 2 * spy
            asp = ((spx + anchor[0] * self.w) / spw, (spy + anchor[1] * self.h) / sph)
            K.draw(cv, self.shadow, x, y, scale=(sc[0] * spw / sw, sc[1] * sph / sh), rot=rot,
                   opacity=opacity * shadow, anchor=asp, blur=blur)
        fr = (self.frost if frost is None else frost) * math.sqrt(abs(sc[0] * sc[1]))
        if fr > 0.5 and mode == 'over':
            o = self.outline() - (anchor[0] * self.w, anchor[1] * self.h)
            a = math.radians(rot)
            ca, sa = math.cos(a), math.sin(a)
            px = o[:, 0] * sc[0]
            py = o[:, 1] * sc[1]
            poly = np.c_[x + ca * px - sa * py, y + sa * px + ca * py]
            frost_poly(cv, poly, fr, min(1.0, opacity * 1.5))
        return K.draw(cv, self.face if face is None else face, x, y, scale=sc, rot=rot, opacity=opacity, mode=mode,
                      anchor=ap, blur=blur)

    def plane(self, cv, cam, center, width=None, rot=(0.0, 0.0, 0.0), opacity=1.0, anchor=(0.5, 0.5), face=None,
              frost=None, shadow=1.0, shadow_z=30.0, dof=True, blur=0.0, mode='over', dof_scale=1.0):
        """3D draw as a plane through core.draw_plane (perspective, DOF, near clipping) with frost computed
        from the warped body alpha. width = body width in world units (default w). Returns draw_plane's dict."""
        if opacity <= 1e-4:
            return None
        width = float(self.w if width is None else width)
        k = width / self.w
        ap = self.anchor(anchor)
        if shadow > 0 and self.shadow is not None:
            cs = np.asarray(center, np.float64) + _normal(rot) * shadow_z
            spx, spy = self.spad
            spw, sph = self.w + 2 * spx, self.h + 2 * spy
            asp = ((spx + anchor[0] * self.w) / spw, (spy + anchor[1] * self.h) / sph)
            K.draw_plane(cv, self.shadow, cam, cs, spw * k, rot, opacity * shadow, dof=dof, height=sph * k,
                         anchor=asp, blur=blur, dof_scale=dof_scale)
        depth = max(cam.depth(np.asarray(center, np.float64)), cam.near)
        fr = (self.frost if frost is None else frost) * k * cam.focal / depth
        core_frost = 0.0
        if fr > 0.5 and mode == 'over':
            o = self.outline()
            uv = np.c_[(self.pad + o[:, 0]) / self.pw, (self.pad + o[:, 1]) / self.ph]
            P = K.plane_point(center, self.pw * k, self.ph * k, rot, uv, ap)
            xy, dz = cam.project(P)
            if np.isfinite(xy).all() and (dz > cam.near).all():
                frost_poly(cv, xy, fr, min(1.0, opacity * 1.5))
            else:
                core_frost = fr
        return K.draw_plane(cv, self.face if face is None else face, cam, center, self.pw * k, rot, opacity, mode,
                            dof, height=self.ph * k, blur=blur, frost=core_frost, anchor=ap, dof_scale=dof_scale)

    def child(self, cv, cam, center, width, rot, spr, x, y, z=-20.0, spr_anchor=(0.5, 0.5), opacity=1.0,
              anchor=(0.5, 0.5), dof=True, blur=0.0, mode='over', scale=1.0, frost=0.0):
        """Draw `spr` on a plane parallel to the card, at card-local (x, y), lifted by z (negative = toward the
        viewer: layered UI with real parallax). spr px map to card px times `scale`."""
        k = width / self.w
        P = self.world(center, width, rot, x, y, anchor, z)
        return K.draw_plane(cv, spr, cam, P, spr.shape[1] * k * scale, rot, opacity, mode, dof, anchor=spr_anchor,
                            blur=blur, frost=frost)


@functools.lru_cache(maxsize=32)
def _normal_c(rx, ry, rz):
    P = K.plane_corners((0, 0, 0), 1.0, 1.0, (rx, ry, rz))
    n = np.cross(P[1] - P[0], P[3] - P[0])
    return n / np.linalg.norm(n)


def _normal(rot):
    return _normal_c(round(float(rot[0]), 3), round(float(rot[1]), 3), round(float(rot[2]), 3))


def _pad_for(glow, rim):
    p = 24 + (2.6 * 30 * min(1.0, glow * rim) if glow > 0 and rim > 0 else 0)
    return int(math.ceil(p / 8.0) * 8)


def _shadow_sprite(w, h, r, L, amount, ds=4):
    """Soft drop shadow (+ tight contact shadow) at 1/ds resolution, knocked out under the body.
    Returns (sprite, spad) where spad is the padding in body px."""
    sig = 22 + 0.02 * max(w, h)
    dy = 14 + 0.025 * h
    sp = int(math.ceil((sig * 2.8 + dy) / 8.0) * 8)
    ws, hs = int(math.ceil((w + 2 * sp) / ds)), int(math.ceil((h + 2 * sp) / ds))
    sp_x = (ws * ds - w) / 2.0
    ys, xs = np.mgrid[0:hs, 0:ws].astype(np.float32)
    xs = (xs + 0.5) * ds
    ys = (ys + 0.5) * ds
    cx, cy = sp_x + w / 2, (hs * ds) / 2.0

    def body_at(dyy, soft):
        return np.clip(0.5 - _rr_sdf_xy(xs, ys - dyy, cx, cy, w / 2, h / 2, r) / soft, 0, 1)
    sh = K.gblur(body_at(dy, ds), sig / ds, border='constant') + \
        K.gblur(body_at(4, ds), 5.0 / ds, border='constant') * 0.45
    sh = np.clip(sh, 0, 1) * np.float32(L.shadow_a * amount) * (1 - body_at(0, ds) * 0.85)
    spr = np.zeros((hs, ws, 4), np.float32)
    spr[..., :3] = L.shadow * sh[..., None]
    spr[..., 3] = sh
    return _ro(spr), (sp_x, (hs * ds - h) / 2.0)


def glass_card(w, h, r=40, look='neon', rim=1.0, rim_color=None, rim2=None, rim_angle=-55.0, rim_spread=2.0,
               glow=1.0, shadow=1.0, tint=None, tint_a=None, border=1.0, spec=1.0, noise=1.0, frost=None, pad=None,
               seed=0):
    """Frosted glass card -> Panel (cached on its parameters; treat .face / .shadow as read-only).
    look: 'neon' | 'amber' (dark smoky glass, neon rim) | 'airy' (white frosted glass, soft shadow).
    rim: strength of the neon edge (0 = none); rim_color: edge colour; rim2: hot-spot colour where the rim light
    peaks (direction rim_angle, deg CCW from +x, -55 = bottom-right; rim_spread sharpens it);
    glow: outer glow amount; shadow: drop shadow amount; tint / tint_a: body colour / opacity override;
    border: inner gradient stroke (bright top-left); spec: top specular sheen; noise: glass grain;
    frost: background blur sigma (px at scale 1; default per look)."""
    return _glass_cached(int(w), int(h), float(r), look, float(rim), _key(rim_color), _key(rim2), float(rim_angle),
                         float(rim_spread), float(glow), float(shadow), _key(tint), tint_a, float(border), float(spec),
                         float(noise), frost, pad, seed)


@functools.lru_cache(maxsize=48)
def _glass_cached(w, h, r, lk, rim, rim_color, rim2, rim_angle, rim_spread, glow, shadow, tint, tint_a, border, spec,
                  noise, frost, pad, seed):
    L = look(lk)
    r = min(r, w / 2, h / 2)
    p = _pad_for(glow, rim) if pad is None else int(pad)
    Hp, Wp = h + 2 * p, w + 2 * p
    ys, xs = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
    xs += 0.5
    ys += 0.5
    sdf = _rr_sdf_xy(xs, ys, p + w / 2, p + h / 2, w / 2, h / 2, r).astype(np.float32)
    body = _cov(sdf)
    u = (xs - p) / w
    v = (ys - p) / h
    ta = L.tint_a if tint_a is None else float(tint_a)
    if tint is not None:
        c0 = c1 = col(tint)
    else:
        c0, c1 = L.tint_top, L.tint_bot
    vv = np.clip(v, 0, 1)[..., None]
    rgb = (c0 * (1 - vv) + c1 * vv) * (ta * body)[..., None]
    a = ta * body
    face = np.zeros((Hp, Wp, 4), np.float32)
    face[..., :3] = rgb
    face[..., 3] = a
    S = Surf(Wp, Hp, face)
    inside = np.minimum(sdf, 0.0)
    # glass grain
    if noise > 0 and L.noise > 0:
        n = _noise(Hp, Wp, seed + 17)
        face[..., :3] += (n * np.float32(L.noise * noise) * body)[..., None] * (1.0 if L.dark else 0.6)
    # fresnel: brighter, denser glass near the edge
    fr = np.exp(inside / 18.0) * body * (0.55 + 0.45 * np.clip(1 - v, 0, 1))
    if L.dark:
        face[..., :3] += fr[..., None] * col(C['WHITE']) * np.float32(L.fresnel)
    else:
        S.fill(fr * np.float32(L.fresnel), 0, 0, col(C['WHITE']))
    # top specular sheen + broad diagonal highlight
    if spec > 0:
        sheen = body * np.clip(1 - v / 0.46, 0, 1) ** 2.2
        diag = body * np.exp(-((u * 0.75 + v * 0.55 - 0.18) / 0.20) ** 2) * 0.5
        e = (sheen + diag) * np.float32(L.spec * spec)
        if L.dark:
            face[..., :3] += e[..., None] * col(C['WHITE'])
        else:
            S.fill(e * 0.6, 0, 0, col(C['WHITE']))
    # inner gradient border: bright top-left, fading to the bottom-right
    if border > 0:
        bw = 1.7 if L.dark else 2.2
        m = _cov(np.abs(sdf + bw / 2 + 0.25) - bw / 2)
        g = 0.10 + 0.90 * np.clip(1.08 - (u * 0.62 + v * 0.58), 0, 1) ** 1.6
        S.fill(m * g * np.float32(L.border_a * border), 0, 0, L.border)
        # crisp top highlight line, hottest near the top-left
        tl = np.exp(-((sdf + 1.2) / 0.85) ** 2) * np.clip(1 - v * 7, 0, 1) * np.clip(1.15 - u * 0.9, 0, 1)
        if L.dark:
            face[..., :3] += (tl * 0.5 * border)[..., None] * col(C['WHITE'])
        if not L.dark:
            # thin darker edge bottom-right to define white glass on ivory
            g2 = np.clip((u * 0.6 + v * 0.6) - 0.55, 0, 1) * 1.6
            m2 = _cov(np.abs(sdf + 0.6) - 0.6)
            S.fill(m2 * g2 * np.float32(0.10 * border), 0, 0, L.text)
    # neon rim + outer glow (emissive: alpha stays the body only)
    rc = col(rim_color) if rim_color is not None else L.rim
    r2 = col(rim2) if rim2 is not None else L.rim2
    if rim > 0:
        dx = (xs - (p + w / 2)) / (w / 2)
        dy = (ys - (p + h / 2)) / (h / 2)
        th = np.arctan2(-dy, dx)
        wr = (0.5 + 0.5 * np.cos(th - math.radians(rim_angle))) ** rim_spread
        line = np.exp(-((sdf - 0.35) / 1.05) ** 2)
        base = 0.30
        k_line = line * (base + (1.0 - base) * wr) * np.float32(rim * L.rim_k)
        colr = rc[None, None, :] * (1 - wr[..., None]) + r2[None, None, :] * wr[..., None]
        rim_l = (k_line * 1.5)[..., None] * colr
        # coloured light bleeding into the glass just inside the edge
        inner = np.exp(inside / 7.0) * body * (0.15 + 0.85 * wr) * np.float32(rim * L.rim_k * 0.10)
        rim_l += inner[..., None] * colr
        if glow > 0:
            src = np.ascontiguousarray((line * (0.25 + 0.75 * wr))[..., None] * colr)
            gl = K.gblur(src, 4.0, border='constant') * 0.9 + K.gblur(src, 13.0, border='constant') * 0.55 + \
                K.gblur(src, 30.0, border='constant') * 0.30
            rim_l += gl * np.float32(glow * rim * L.glow_k) * (1 - body[..., None] * 0.6)
        face[..., :3] += rim_l
        rim_layer = np.zeros_like(face)
        rim_layer[..., :3] = rim_l
        rim_layer = _ro(rim_layer)
    else:
        rim_layer = None
    shadow_spr, spad = (None, p)
    if shadow > 0:
        shadow_spr, spad = _shadow_sprite(w, h, r, L, shadow)
    fr_sig = L.frost if frost is None else float(frost)
    pn = Panel(_ro(face), shadow_spr, w, h, r, p, lk, fr_sig, rc, r2, spad=spad)
    pn.rim_layer = rim_layer
    return pn


def derive_panel(base, face, meta=None):
    """New Panel sharing base's geometry/shadow with a different (static) face."""
    p = Panel(_ro(face), base.shadow, base.w, base.h, base.r, base.pad, base.look, base.frost, base.rim_color,
              base.rim2, dict(base.meta, **(meta or {})), spad=base.spad)
    p.rim_layer = base.rim_layer
    p._band, p._grid = base._band, base._grid
    return p


def media_fit(spr, w, h, r=0.0, center=(0.5, 0.5), zoom=1.0):
    """Cover-fit any sprite into w x h with rounded corners r (premultiplied alpha). For footage, prefer
    Clip.get(t, w, h) (already the right size) - this then only applies the rounded mask."""
    w, h = int(w), int(h)
    sh, sw = spr.shape[:2]
    if (sw, sh) != (w, h) or zoom != 1.0:
        s = max(w / sw, h / sh) * zoom
        cx, cy = center[0] * sw, center[1] * sh
        cx = np.clip(cx, w / (2 * s), sw - w / (2 * s))
        cy = np.clip(cy, h / (2 * s), sh - h / (2 * s))
        M = np.float32([[s, 0, w / 2 - s * cx], [0, s, h / 2 - s * cy]])
        src = spr
        if s < 0.5:
            f = max(1, int(1 / s / 1.5))
            src = cv2.resize(spr, (max(1, sw // f), max(1, sh // f)), interpolation=cv2.INTER_AREA)
            M = np.float32([[s * f, 0, w / 2 - s * cx], [0, s * f, h / 2 - s * cy]])
            M[0, 2] = w / 2 - s * cx
            M[1, 2] = h / 2 - s * cy
            M[0, 0] = M[1, 1] = s * sw / src.shape[1]
        out = cv2.warpAffine(src, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    else:
        out = spr.copy()
    if r > 0:
        out = out * _rr_alpha(w, h, float(r))[..., None]
    return out.astype(np.float32)


@functools.lru_cache(maxsize=64)
def _rr_alpha(w, h, r):
    xs, ys = _grid(0, 0, w, h)
    return _ro(_cov(_rr_sdf_xy(xs, ys, w / 2, h / 2, w / 2, h / 2, min(r, w / 2, h / 2))))


def put_media(panel, face, spr, x, y, w, h, r=24.0, opacity=1.0, inner=True):
    """Clip a footage/photo sprite into a rounded rect at card-local (x, y, w, h) of a face copy, with a soft
    inner edge shade and a hairline highlight so it sits inside the glass."""
    m = media_fit(spr, w, h, r)
    if inner:
        a = _rr_alpha(int(w), int(h), float(r))
        xs, ys = _grid(0, 0, int(w), int(h))
        d = _rr_sdf_xy(xs, ys, w / 2, h / 2, w / 2, h / 2, min(r, w / 2, h / 2))
        shade = (1 - 0.35 * np.exp(d / 14.0)) * a
        m[..., :3] *= shade[..., None] / np.maximum(a[..., None], 1e-6) * (a[..., None] > 0)
        hl = _cov(np.abs(d + 0.8) - 0.8) * np.clip(1.2 - ys / h * 2.0, 0, 1) * 0.35
        m[..., :3] += hl[..., None]
    panel.put(face, m, x, y, opacity=opacity)
    return face


def media_face(panel, media, inset=0, sweep=None, light=None, opacity=1.0, rim_gain=None, vignette=True):
    """Face of `panel` with a footage / photo sprite filling its body (inset px from the edge, corners follow the
    card radius) under the glass rim, border and sheen, e.g. a tilted glass card playing c01:
        card = glass_card(720, 960, 48, 'neon')
        f = media_face(card, clip.get(t, 720, 960, look='neon'), sweep=t * .3 % 1)
        card.plane(cv, cam, (0, 0, 900), 720, rot=(4, -14, 0), face=f)"""
    f = panel.face_at(sweep=None, light=None, rim_gain=rim_gain)
    w, h = panel.w - 2 * inset, panel.h - 2 * inset
    r = max(0.0, panel.r - inset)
    m = media_fit(media, w, h, r)
    if vignette:
        xs, ys = _grid(0, 0, int(w), int(h))
        d = _rr_sdf_xy(xs, ys, w / 2, h / 2, w / 2, h / 2, min(r, w / 2, h / 2))
        m[..., :3] *= (1 - 0.30 * np.exp(d / 40.0))[..., None]
    # media under the glass highlights: composite media, then re-add the emissive edge (rim) + sheen on top
    panel.put(f, m, inset, inset, opacity=opacity)
    if panel.rim_layer is not None:
        # restore the part of the rim / inner light the media just covered (the outside glow is untouched)
        cov = np.zeros(f.shape[:2], np.float32)
        y0, x0 = panel.pad + int(inset), panel.pad + int(inset)
        cov[y0:y0 + m.shape[0], x0:x0 + m.shape[1]] = m[..., 3] * np.float32(opacity)
        f[..., :3] += panel.rim_layer[..., :3] * (cov * np.float32(1.0 if rim_gain is None else rim_gain))[..., None]
    u, v, body = panel._uvgrid()
    sheen = body * np.clip(1 - v / 0.4, 0, 1) ** 2 * np.float32(0.05 * opacity)
    f[..., :3] += sheen[..., None]
    if sweep is not None:
        panel._add_sweep(f, sweep, 0.14, 1.0, None, 1)
    if light is not None and 0 < light < 1:
        panel._add_light(f, light, None, -28.0, 0.07)
    return f


# =============================================================================================== app window
@functools.lru_cache(maxsize=16)
def app_window(w=900, h=1240, look='neon', title='organicfostering.co.uk', header='Am I eligible to foster?',
               sub=None, icons=('home', 'users', 'chat', 'calendar', 'settings'), active=0, sidebar=True,
               traffic=True, header_size=52, r=44, rim=1.0, glow=1.0, shadow=1.0, rim_angle=-55.0):
    """Glass app window -> Panel (cached). Title bar (traffic-light dots + a subtle centred title), a left
    sidebar of icons with an active highlight, a header (Nunito ExtraBold) and optional sub line.
    panel.meta['slot'] = (x, y, w, h) card-local content area for rows; meta['sidebar'] = [(x, y) icon centres].
        win = app_window(look='neon', header='Am I eligible to foster?')
        face = win.face_at(sweep=t * 0.4 % 1); x, y, sw, sh = win.meta['slot']
        win.put(face, check_row('A spare bedroom', w=sw, t=t - 1.0), x, y)"""
    L = LOOKS[look]
    base = glass_card(w, h, r, look, rim=rim, glow=glow, shadow=shadow, rim_angle=rim_angle)
    f = base.face.copy()
    p = base.pad
    S = Surf(f.shape[1], f.shape[0], f)
    TB = 88 if (traffic or title) else 0
    SB = 128 if sidebar else 0
    lc, la = L.line, L.line_a
    if TB:
        # title bar: slightly denser glass + separator
        S.rrect(p + 1, p + 1, w - 2, TB, r - 1, L.surface, 0.035 if L.dark else 0.25)
        S.rrect(p + 24, p + TB - 1, w - 48, 1.5, 0.75, lc, la * 1.2)
        if traffic:
            dots = [C['HOT_PINK'], C['AMBER'], C['LEAF_HI']]
            for i, dc in enumerate(dots):
                cx, cy = p + 44 + i * 30, p + TB / 2
                S.circle(cx, cy, 8.5, _v(dc, 0.85 if L.dark else 1.0), 1.0)
                S.circle(cx - 2, cy - 2.5, 3.0, _v(C['WHITE']), 0.35)
        if title:
            tw = measure(title, 28, 'ui_medium')
            S.rrect(p + w / 2 - tw / 2 - 40, p + TB / 2 - 24, tw + 80, 48, 24, L.surface, 0.06 if L.dark else 0.5)
            ic = icon('shield', 24, L.text3, stroke=2.4)
            S.paste(ic, p + w / 2 - tw / 2 - 28 - ic.shape[1] / 2 + 12, p + TB / 2, anchor=(0.5, 0.5))
            put_text(f, p + w / 2 + 12, p + TB / 2, title, 28, 'ui_medium', L.text2, anchor='mm')
    centres = []
    if SB:
        S.rrect(p + SB - 1, p + TB + 24, 1.5, h - TB - 48, 0.75, lc, la * 1.2)
        for i, nm in enumerate(icons):
            cx, cy = p + SB / 2, p + TB + 72 + i * 104
            centres.append((cx - p, cy - p))
            if i == active:
                a, X0, Y0 = S.rrect_grad(cx - 38, cy - 38, 76, 76, 24, L.grad[0], L.grad[1], 35, 1.0, 1.0)
                S.glow(a, X0, Y0, L.glow, (8, 22), 0.40 if L.dark else 0.22, knock=0.92)
                S.sheen(cx - 37, cy - 37, 74, 74, 23, 0.10, 0.0, 0.6)
                S.rrect(p + 4, cy - 22, 5, 44, 2.5, L.accent_hi if L.dark else L.accent, 1.0)
                S.paste(icon(nm, 40, C['WHITE'], stroke=2.2), cx, cy, anchor=(0.5, 0.5))
            else:
                S.paste(icon(nm, 40, L.text2, stroke=2.0), cx, cy, anchor=(0.5, 0.5))
    hx = SB + 48
    hy = TB + 56 + header_size * 0.74
    if header:
        put_text(f, p + hx, p + hy, header, header_size, 'head', L.text, anchor='ls', max_w=w - hx - 40)
    y_end = hy + 16
    if sub:
        put_text(f, p + hx, p + hy + 50, sub, 30, 'body', L.text2, anchor='ls', max_w=w - hx - 40)
        y_end = hy + 50 + 14
    slot = (SB + 40, int(math.ceil((y_end + 32) / 8) * 8), w - SB - 80, 0)
    slot = (slot[0], slot[1], slot[2], h - slot[1] - 40)
    return derive_panel(base, f, {'slot': slot, 'sidebar': centres, 'titlebar': TB, 'header_xy': (hx, hy)})


# =============================================================================================== checkbox / rows
def _check_pts(size, x0=0.0, y0=0.0):
    return np.array([[0.27, 0.53], [0.43, 0.68], [0.74, 0.35]]) * size + (x0, y0)


def checkbox(t=None, size=60, look='neon', color=None):
    """Animated checkbox sprite (2*size square, box centred). t = seconds since the tick started (None or < 0
    = empty): 0-0.22 s the check draws on, from 0.14 s the box fills LEAF with a spring pop, a burst ring and
    a glow settle in. color: fill colour spec (default LEAF)."""
    if t is not None and t >= 0:
        t = round(min(t, 1.2) * 240) / 240.0
    else:
        t = -1.0
    return _checkbox_cached(float(t), int(size), look, _key(color))


@functools.lru_cache(maxsize=1024)
def _checkbox_cached(t, size, lk, color):
    L = LOOKS[lk]
    n = size * 2
    S = Surf(n, n)
    c = n / 2
    fill = 0.0 if t < 0 else K.ramp(t, 0.12, 0.26, 'out_cubic')
    draw = 0.0 if t < 0 else K.ramp(t, 0.0, 0.22, 'out_cubic')
    if t >= 0.12:
        u = t - 0.12
        sc = 1.0 + 0.24 * math.exp(-7.5 * u) * math.sin(2 * math.pi * 3.0 * u)
    else:
        sc = 1.0 - 0.06 * K.ramp(t, 0.0, 0.12, 'out_cubic') if t >= 0 else 1.0
    s = size * sc
    r = s * 0.30
    x0, y0 = c - s / 2, c - s / 2
    cg0 = col(color) if color is not None else L.ok_hi
    cg1 = col(color) * 0.7 if color is not None else L.ok
    # empty state
    if fill < 1:
        if L.dark:
            S.rrect(x0, y0, s, s, r, _v(C['WHITE']), 0.06 * (1 - fill))
            S.stroke_rrect(x0, y0, s, s, r, 3.0, _v(C['WHITE']), 0.38 * (1 - fill))
        else:
            S.rrect(x0, y0, s, s, r, _v(C['WHITE']), 0.85 * (1 - fill))
            S.stroke_rrect(x0, y0, s, s, r, 3.0, L.text, 0.40 * (1 - fill))
    if fill > 0:
        a, X0, Y0 = S.rrect_grad(x0, y0, s, s, r, cg0, cg1, -70, fill, 1.0)
        S.glow(a, X0, Y0, cg1, (5, 14), 0.55 * fill * (1.0 + 1.2 * math.exp(-6 * max(0.0, t - 0.14))))
        S.rrect(x0 + 2, y0 + 2, s - 4, s * 0.45, r - 2, _v(C['WHITE']), 0.16 * fill, emit=True)
        S.stroke_rrect(x0, y0, s, s, r, 1.5, _v(C['WHITE']), 0.35 * fill)
    # burst ring
    if t >= 0.12:
        u = K.ramp(t, 0.12, 0.62, 'out_cubic')
        rr = s * (0.62 + 0.55 * u)
        S.ring(c, c, rr, 3.0 * (1 - u) + 0.6, cg0, (1 - u) * 0.9, emit=True)
    # check stroke
    if draw > 0:
        pts = trim_polyline(_check_pts(s, x0, y0), 0, draw)
        ck = _v(C['WHITE']) * (1.0 if fill > 0.5 else 1.0)
        m = stroke_mask([(pts, False)], n, n, max(3.0, s * 0.105))
        if fill < 0.5 and not L.dark:
            ck = L.ok
        S.fill(m, 0, 0, ck if fill > 0.3 else K.mix(cg0, C['WHITE'], 0.3), 1.0)
    return _ro(S.img)


ROW_PAD = 24


def check_row(label, sub=None, w=700, t=None, look='neon', h=None, hl=0.0, box=60, label_size=38, sub_size=28,
              done_tint=True):
    """Checklist row sprite (w + 2*ROW_PAD wide, h + 2*ROW_PAD tall; the row body starts at (ROW_PAD, ROW_PAD)).
    t: seconds since its tick (None / < 0 = unchecked) drives checkbox(); hl 0..1 = focus highlight ring.
        spr = check_row('A spare bedroom', 'Space for a child of their own', w=700, t=t - 2.0)"""
    hh = int(h or (120 if sub else 96))
    tt = -1.0 if (t is None or t < 0) else float(t)
    if (tt < 0 or tt >= 1.2) and hl in (0, 0.0, 1, 1.0):
        return _row_settled(label, sub, int(w), hh, look, int(box), float(label_size), float(sub_size),
                            -1.0 if tt < 0 else 1.2, float(hl), bool(done_tint))
    return _row_render(label, sub, int(w), hh, look, int(box), float(label_size), float(sub_size), tt, float(hl),
                       bool(done_tint))


@functools.lru_cache(maxsize=24)
def _row_settled(label, sub, w, hh, look, box, ls, ss, tt, hl, done_tint):
    return _ro(_row_render(label, sub, w, hh, look, box, ls, ss, tt, hl, done_tint))


def _row_render(label, sub, w, hh, look, box, label_size, sub_size, tt, hl, done_tint):
    base = _row_base(label, sub, int(w), hh, look, int(box), float(label_size), float(sub_size))
    if tt < 0 and hl <= 0:
        cb = checkbox(None, box, look)
        out = base.copy()
        paste(out, cb, ROW_PAD + 28 + box / 2 - cb.shape[1] / 2, ROW_PAD + hh / 2 - cb.shape[0] / 2)
        return out
    out = base.copy()
    if done_tint and tt >= 0:
        k = K.ramp(tt, 0.12, 0.5, 'out_cubic')
        if k > 0:
            hi = _row_hi(int(w), hh, look)
            K._blend(out, hi, k, 'over')
    if hl > 0:
        ring = _row_ring(int(w), hh, look)
        K._blend(out, ring, hl, 'over')
    cb = checkbox(tt, box, look)
    paste(out, cb, ROW_PAD + 28 + box / 2 - cb.shape[1] / 2, ROW_PAD + hh / 2 - cb.shape[0] / 2)
    return out


@functools.lru_cache(maxsize=64)
def _row_base(label, sub, w, h, lk, box, ls, ss):
    L = LOOKS[lk]
    P = ROW_PAD
    S = Surf(w + 2 * P, h + 2 * P)
    r = 26
    if L.dark:
        S.rrect(P, P, w, h, r, _v(C['WHITE']), 0.045)
        S.stroke_rrect(P, P, w, h, r, 1.3, _v(C['WHITE']), 0.10,
                       weight=lambda xs, ys: np.clip(1.2 - (ys - P) / h, 0.3, 1.0))
    else:
        S.rrect(P, P, w, h, r, _v(C['WHITE']), 0.62)
        S.stroke_rrect(P, P, w, h, r, 1.3, L.text, 0.06)
    tx = P + 28 + box + 28
    maxw = w - (tx - P) - 24
    if sub:
        put_text(S.img, tx, P + h / 2 - 6, label, ls, 'ui', L.text, 'ls', max_w=maxw)
        put_text(S.img, tx, P + h / 2 + 34, sub, ss, 'body', L.text2, 'ls', max_w=maxw)
    else:
        put_text(S.img, tx, P + h / 2, label, ls, 'ui', L.text, 'lm', max_w=maxw)
    return _ro(S.img)


@functools.lru_cache(maxsize=16)
def _row_hi(w, h, lk):
    """'Done' overlay: leaf-tinted body + leaf left accent."""
    L = LOOKS[lk]
    P = ROW_PAD
    S = Surf(w + 2 * P, h + 2 * P)
    a, X0, Y0 = S.rrect_mask(P, P, w, h, 26)
    xs = (np.arange(a.shape[1], dtype=np.float32) + X0 + 0.5 - P) / w
    k = np.clip(1 - xs * 1.6, 0, 1) ** 1.5
    S.fill(a * k[None, :], X0, Y0, L.ok_hi, 0.10 if L.dark else 0.14)
    S.stroke_rrect(P, P, w, h, 26, 1.6, L.ok_hi, 0.40 if L.dark else 0.55,
                   weight=lambda xs_, ys_: np.clip(1.25 - (xs_ - P) / w * 1.3, 0.1, 1))
    return _ro(S.img)


@functools.lru_cache(maxsize=16)
def _row_ring(w, h, lk):
    L = LOOKS[lk]
    P = ROW_PAD
    S = Surf(w + 2 * P, h + 2 * P)
    a, X0, Y0 = S.stroke_rrect(P, P, w, h, 26, 2.0, L.accent_hi, 0.9)
    S.glow(a, X0, Y0, L.glow, (4, 12), 0.6 if L.dark else 0.3)
    S.rrect(P, P, w, h, 26, L.accent_hi, 0.06 if L.dark else 0.05)
    return _ro(S.img)


# =============================================================================================== toggle / chips
def toggle(p=0.0, w=112, h=64, look='neon', on=None):
    """Toggle switch sprite ((w+48) x (h+48), body centred). p 0 = off .. 1 = on (feed it an eased or spring
    value; the knob squashes mid-travel). on: on-colour pair (default the look's gradient)."""
    p = round(float(p) * 120) / 120.0
    return _toggle_cached(p, int(w), int(h), look, _key(on))


@functools.lru_cache(maxsize=512)
def _toggle_cached(p, w, h, lk, on):
    L = LOOKS[lk]
    P = 24
    S = Surf(w + 2 * P, h + 2 * P)
    r = h / 2
    pc = min(max(p, 0.0), 1.0)
    c0, c1 = (col(on[0]), col(on[1])) if on is not None else L.grad
    kr = r - 6
    squash = math.sin(math.pi * pc) * 0.38
    kw = 2 * kr * (1 + squash)
    kx = P + 6 + (w - 12 - kw) * p
    if L.dark:
        S.rrect(P, P, w, h, r, _v(C['WHITE']), L.track_a)
        S.stroke_rrect(P, P, w, h, r, 1.5, _v(C['WHITE']), 0.18)
    else:
        S.rrect(P, P, w, h, r, L.text, 0.14)
        S.stroke_rrect(P, P, w, h, r, 1.5, L.text, 0.10)
    if pc > 0:
        # the on-fill follows the knob from the left, fully opaque, fading in over the first 25 %
        fw = min(w, kx + kw + 6 - P)
        a, X0, Y0 = S.rrect_mask(P, P, fw, h, r)
        g = _lingrad(a.shape[1], a.shape[0], c0, c1, 0)
        op = K.smoothstep(0.0, 0.25, pc)
        S.fill(a, X0, Y0, g, op)
        S.glow(a, X0, Y0, (c0 + c1) / 2, (6, 16), 0.35 * op * (1.0 if L.dark else 0.5), knock=0.92)
        S.sheen(P + 2, P + 2, fw - 4, h - 4, r - 2, 0.08 * op, 0.0, 0.6)
    # knob shadow + knob
    a, X0, Y0 = S.rrect_mask(kx, P + 6 + 3, kw, 2 * kr, kr)
    if a is not None:
        sh = K.gblur(np.pad(a, 8), 3.0, border='constant')
        S.fill(sh, X0 - 8, Y0 - 8, L.shadow if L.dark else _v(C['INK']), 0.45 if L.dark else 0.22)
    S.rrect_grad(kx, P + 6, kw, 2 * kr, kr, C['WHITE'], K.mix(C['WHITE'], C['LAVENDER'], 0.8), -90, 1.0)
    S.stroke_rrect(kx, P + 6, kw, 2 * kr, kr, 1.0, _v(C['WHITE']), 0.8)
    return _ro(S.img)


def chip_size(text, size=34, h=72, icon_name=None, pad_x=32):
    """(w, h) of a chip body."""
    tw = measure(text, size, 'ui')
    iw = (h * 0.5 + 12) if icon_name else 0
    return int(math.ceil((tw + 2 * pad_x + iw) / 8.0) * 8), int(h)


def chip(text, sel=0.0, look='neon', size=34, h=72, icon_name=None, pad_x=32, grad=None, origin=(0.5, 0.5)):
    """Chip / tag sprite ((w+48) x (h+48), body centred): unselected glass outline -> selected gradient fill with
    glow and white text. sel 0..1 reveals the selected state as a soft circular wipe growing from `origin` (uv on
    the body, e.g. the click point), so text stays crisp mid-transition (add a spring pop with the draw scale)."""
    a = _chip_cached(text, look, float(size), int(h), icon_name, float(pad_x), _key(grad), False)
    if sel <= 0:
        return a
    b = _chip_cached(text, look, float(size), int(h), icon_name, float(pad_x), _key(grad), True)
    if sel >= 1:
        return b
    hh, ww = a.shape[:2]
    P = 24
    ox, oy = P + origin[0] * (ww - 2 * P), P + origin[1] * (hh - 2 * P)
    rmax = math.hypot(max(ox, ww - ox), max(oy, hh - oy))
    xs, ys = _grid(0, 0, ww, hh)
    d = np.sqrt((xs - ox) ** 2 + (ys - oy) ** 2)
    k = np.clip((K.EASE['out_cubic'](sel) * (rmax + 12) - d) / 12.0, 0, 1)[..., None]
    return (a * (1 - k) + b * k).astype(np.float32)


@functools.lru_cache(maxsize=128)
def _chip_cached(text, lk, size, h, icon_name, pad_x, grad, selected):
    L = LOOKS[lk]
    w, h = chip_size(text, size, h, icon_name, pad_x)
    P = 24
    S = Surf(w + 2 * P, h + 2 * P)
    r = h / 2
    if selected:
        c0, c1 = (col(grad[0]), col(grad[1])) if grad is not None else L.grad
        a, X0, Y0 = S.rrect_grad(P, P, w, h, r, c0, c1, 20, 1.0)
        S.glow(a, X0, Y0, (c0 + c1) / 2, (6, 18), 0.40 if L.dark else 0.22, knock=0.92)
        S.sheen(P + 2, P + 2, w - 4, h - 4, r - 2, 0.09, 0.0, 0.6)
        S.stroke_rrect(P, P, w, h, r, 1.4, _v(C['WHITE']), 0.45,
                       weight=lambda xs, ys: np.clip(1.3 - (ys - P) / h * 1.4, 0.15, 1))
        tc = _v(C['WHITE'])
    else:
        if L.dark:
            S.rrect(P, P, w, h, r, _v(C['WHITE']), 0.06)
            S.stroke_rrect(P, P, w, h, r, 1.6, _v(C['WHITE']), 0.30,
                           weight=lambda xs, ys: np.clip(1.25 - (ys - P) / h * 0.9, 0.35, 1))
        else:
            S.rrect(P, P, w, h, r, _v(C['WHITE']), 0.75)
            S.stroke_rrect(P, P, w, h, r, 1.5, L.text, 0.14)
        tc = L.chip_text
    x = P + pad_x
    if icon_name:
        isz = int(h * 0.5)
        S.paste(icon(icon_name, isz, tc, stroke=2.3), x + isz / 2, P + h / 2, anchor=(0.5, 0.5))
        x += isz + 12
    put_text(S.img, x, P + h / 2, text, size, 'ui', tc, 'lm')
    return _ro(S.img)


# =============================================================================================== button
def button_size(text, h=112, size=40, icon_name='arrow_right'):
    tw = measure(text, size, 'ui')
    iw = (size * 1.0 + 16) if icon_name else 0
    return int(math.ceil((tw + iw + 2 * h * 0.5) / 8.0) * 8), int(h)


BUTTON_PAD = 56


def button(text='Start your enquiry', hover=0.0, press=0.0, ripple=None, ripple_at=(0.5, 0.5), look='neon', h=112,
           size=40, icon_name='arrow_right', grad=None, w=None):
    """Gradient pill button sprite (body + BUTTON_PAD each side, body centred). MAGENTA -> ORANGE fill with gloss,
    inner border and glow. hover 0..1 brightens + lifts the glow and nudges the arrow; press 0..1 scales to 94 %
    and darkens; ripple = seconds since the click (white ripple from ripple_at (uv on the body) + an expanding
    ring outside the pill)."""
    w0, h0 = button_size(text, h, size, icon_name) if w is None else (int(w), int(h))
    hv = round(float(hover) * 24) / 24.0
    base = _button_cached(text, look, int(h0), float(size), icon_name, _key(grad), int(w0), hv)
    out = base
    if press > 0:
        s = 1 - 0.06 * press
        hh, ww = base.shape[:2]
        M = np.float32([[s, 0, ww / 2 * (1 - s)], [0, s, hh / 2 * (1 - s)]])
        out = cv2.warpAffine(base, M, (ww, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        out[..., :3] *= np.float32(1 - 0.12 * press)
    if ripple is not None and ripple >= 0 and ripple < 0.9:
        out = out.copy() if out is base else out
        _button_ripple(out, ripple, ripple_at, w0, h0, 1 - 0.06 * press)
    return out


@functools.lru_cache(maxsize=64)
def _button_cached(text, lk, h, size, icon_name, grad, w, hover):
    L = LOOKS[lk]
    P = BUTTON_PAD
    S = Surf(w + 2 * P, h + 2 * P)
    r = h / 2
    c0, c1 = (col(grad[0]), col(grad[1])) if grad is not None else (_v(C['MAGENTA']), _v(C['ORANGE']))
    gain = 1.0 + 0.12 * hover
    if not L.dark:      # coloured soft shadow on light scenes
        a, X0, Y0 = S.rrect_mask(P + 8, P + 18, w - 16, h - 8, r)
        sh = K.gblur(np.pad(a, 40), 16.0, border='constant')
        S.fill(sh, X0 - 40, Y0 - 40, _v(C['MAGENTA'], 0.8), 0.30)
    a, X0, Y0 = S.rrect_grad(P, P, w, h, r, c0, c1, 15, 1.0, gain)
    S.glow(a, X0, Y0, (c0 * 0.55 + c1 * 0.45), (8, 22, 44), (0.30 + 0.40 * hover) * (1.0 if L.dark else 0.45),
           knock=0.92)
    S.sheen(P + 2, P + 2, w - 4, h - 4, r - 2, 0.07 + 0.03 * hover, 0.0, 0.58)
    # darker lower half: a rounded, pressed-out pill
    a2, X2, Y2 = S.rrect_mask(P, P, w, h, r)
    yy = (np.arange(a2.shape[0], dtype=np.float32) + Y2 + 0.5 - P) / h
    shade = np.clip((yy - 0.45) / 0.55, 0, 1) ** 1.4 * 0.22
    S.img[Y2:Y2 + a2.shape[0], X2:X2 + a2.shape[1], :3] *= (1 - a2 * shade[:, None])[..., None]
    S.stroke_rrect(P, P, w, h, r, 1.6, _v(C['WHITE']), 0.55,
                   weight=lambda xs, ys: np.clip(1.25 - (ys - P) / h * 1.6, 0.0, 1) * (0.6 + 0.4 * np.clip(
                       1.2 - (xs - P) / w, 0, 1)))
    tw = measure(text, size, 'ui')
    iw = (size + 16) if icon_name else 0
    x0 = P + w / 2 - (tw + iw) / 2
    put_text(S.img, x0, P + h / 2, text, size, 'ui', C['WHITE'], 'lm')
    if icon_name:
        ic = icon(icon_name, int(size * 1.0), C['WHITE'], stroke=2.6)
        S.paste(ic, x0 + tw + 16 + size / 2 + 6 * hover, P + h / 2 + 1, anchor=(0.5, 0.5))
    return _ro(S.img)


def _button_ripple(out, t, at, w, h, s):
    P = BUTTON_PAD
    hh, ww = out.shape[:2]
    cx = ww / 2 + (at[0] - 0.5) * w * s
    cy = hh / 2 + (at[1] - 0.5) * h * s
    xs, ys = _grid(0, 0, ww, hh)
    body = _cov(_rr_sdf_xy(xs, ys, ww / 2, hh / 2, w * s / 2, h * s / 2, h * s / 2))
    u = K.ramp(t, 0.0, 0.7, 'out_cubic')
    rr = 16 + u * w * 0.85
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    disc = np.clip((rr - dist) / (rr * 0.55 + 4), 0, 1) ** 0.8
    k = (disc * body * (0.30 * (1 - u) ** 1.3)).astype(np.float32)
    out[..., :3] += k[..., None] * _v(C['WHITE'])
    # outer ring leaving the pill
    v = K.ramp(t, 0.0, 0.7, 'out_cubic')
    d = _rr_sdf_xy(xs, ys, ww / 2, hh / 2, w * s / 2 + v * P * 0.9, h * s / 2 + v * P * 0.9, h * s / 2 + v * P * 0.9)
    ring = np.exp(-(d / 1.6) ** 2) * (1 - v) ** 1.6 * 1.3
    out[..., :3] += (ring * (1 - body))[..., None].astype(np.float32) * _v(K.mix(C['HOT_PINK'], C['WHITE'], 0.4))


# =============================================================================================== cursor
_ARROW = [(0.0, 0.0), (0.0, 16.6), (3.95, 12.95), (6.75, 19.55), (9.45, 18.45), (6.7, 11.95), (12.05, 11.95)]


def _poly_sdf(xs, ys, pts):
    pts = np.asarray(pts, np.float64)
    A = pts
    B = np.roll(pts, -1, axis=0)
    d = _seg_dist(xs, ys, A, B)
    inside = np.zeros(xs.shape, bool)
    for (x1, y1), (x2, y2) in zip(A, B):
        cond = ((y1 > ys) != (y2 > ys))
        xint = (x2 - x1) * (ys - y1) / ((y2 - y1) if y2 != y1 else 1e-9) + x1
        inside ^= cond & (xs < xint)
    return np.where(inside, -d, d)


def _capsule(xs, ys, a, b, r):
    ax, ay = a
    bx, by = b
    pax, pay = xs - ax, ys - ay
    bax, bay = bx - ax, by - ay
    hh = np.clip((pax * bax + pay * bay) / max(bax * bax + bay * bay, 1e-9), 0, 1)
    return np.sqrt((pax - bax * hh) ** 2 + (pay - bay * hh) ** 2) - r


def _hand_sdf(xs, ys):
    """Pointing hand in a 24 x 28 unit box; returns (union sdf, finger-separation line mask distance)."""
    idx = _capsule(xs, ys, (9.0, 3.6), (9.0, 16.5), 2.65)
    mid = _capsule(xs, ys, (13.25, 11.6), (13.25, 17.5), 2.5)
    rng = _capsule(xs, ys, (17.3, 12.6), (17.3, 18.0), 2.4)
    pnk = _capsule(xs, ys, (21.0, 14.0), (21.0, 18.8), 2.2)
    palm = _rr_sdf_xy(xs, ys, 14.9, 21.0, 8.5, 6.2, 5.2)
    thumb = _capsule(xs, ys, (7.4, 21.6), (3.0, 16.6), 2.35)
    u = np.minimum.reduce([idx, mid, rng, pnk, palm, thumb])
    sep = np.minimum.reduce([np.where(ys < 18.6, np.abs(mid), 99), np.where(ys < 18.8, np.abs(rng), 99),
                             np.where(ys < 19.0, np.abs(pnk), 99), np.where(ys < 17.0, np.abs(idx), 99)])
    return u, sep


CURSOR_HOT = {'arrow': None, 'hand': None}


def cursor(kind='arrow', size=72, press=0.0, look='neon'):
    """3D mouse cursor sprite: macOS-like arrow ('arrow') or pointing hand ('hand'), white face with a dark
    outline, a slight extruded thickness and a soft shadow. press 0..1 squashes it toward the surface.
    Place it with cursor_anchor(kind, size): K.draw(cv, spr, x, y, anchor=cursor_anchor(kind, size)) puts
    the hotspot (arrow tip / fingertip) on (x, y). Or use draw_cursor()."""
    p = round(float(press) * 8) / 8.0
    return _cursor_cached(kind, int(size), p)


def cursor_anchor(kind='arrow', size=72):
    _cursor_cached(kind, int(size), 0.0)
    return _CURSOR_ANCHOR[(kind, int(size))]


_CURSOR_ANCHOR = {}


@functools.lru_cache(maxsize=64)
def _cursor_cached(kind, size, press):
    ss = 2
    if kind == 'arrow':
        unit_h = 19.6
        hot = (0.0, 0.0)
    else:
        unit_h = 28.0
        hot = (9.0, 1.0)
    k = size / unit_h * ss                # px per unit at ss
    pad = int(size * 0.55) * ss
    n_w = int((24 if kind == 'hand' else 13.5) * k) + 2 * pad
    n_h = int(unit_h * k) + 2 * pad
    sq = 1.0 - 0.08 * press
    ys, xs = np.mgrid[0:n_h, 0:n_w].astype(np.float32)

    def sdf_at(dx, dy, s=1.0):
        u = (xs + 0.5 - pad - dx) / (k * s)
        v = (ys + 0.5 - pad - dy) / (k * s)
        if kind == 'arrow':
            d = _poly_sdf(u, v, _ARROW) - 0.35
            return d * k * s, None
        d, sep = _hand_sdf(u, v)
        return d * k * s, sep * k * s
    out_w = (1.0 if kind == 'arrow' else 1.25) * k   # outline width (px at ss)
    lift = (1 - press) * 1.0
    # soft shadow
    d_sh, _ = sdf_at(2.2 * k * lift + 0.6 * k, 3.4 * k * lift + 0.8 * k, sq)
    sh = K.gblur(_cov(d_sh, 1.0), max(1.0, (1.4 + 1.6 * lift) * k), border='constant')
    # extrusion (thickness): several offset copies toward the bottom-right
    S = Surf(n_w, n_h)
    S.fill(sh, 0, 0, _v(C['INK'], 0.6), 0.42)
    depth = 1.1 * k * (1 - 0.4 * press)
    steps = 6
    for i in range(steps, 0, -1):
        dd = depth * i / steps
        d_e, _ = sdf_at(dd * 0.55, dd, sq)
        a = _cov(d_e + out_w * 0.5, ss * 0.6)
        shade = 0.30 + 0.25 * (1 - i / steps)
        S.fill(a, 0, 0, _v(K.mix(C['INK'], C['LAVENDER'], shade)), 1.0)
    d0, sep = sdf_at(0, 0, sq)
    outline = _cov(d0 - out_w * 0.5, ss * 0.6)
    S.fill(outline, 0, 0, _v(C['INK'], 0.55), 1.0)
    face = _cov(d0 + out_w * 0.5, ss * 0.6)
    vv = np.clip((ys - pad) / (unit_h * k), 0, 1)[..., None]
    fc = _v(C['WHITE']) * (1 - vv * 0.16) + _v(C['LAVENDER']) * (vv * 0.16)
    S.fill(face, 0, 0, fc, 1.0)
    # rim highlight on the upper-left edge of the face
    hl = np.exp(-((d0 + out_w * 0.5 + 1.2 * ss) / (0.9 * ss)) ** 2) * face
    S.emit(hl * np.clip(1.2 - vv[..., 0] * 1.5, 0, 1), 0, 0, _v(C['WHITE']), 0.25)
    if sep is not None:
        line = _cov(sep - 0.55 * k * 0.5, ss * 0.6) * face
        S.fill(line, 0, 0, _v(C['INK'], 0.55), 0.9)
    img = cv2.resize(S.img, (n_w // ss, n_h // ss), interpolation=cv2.INTER_AREA)
    _CURSOR_ANCHOR[(kind, size)] = ((pad + hot[0] * k) / n_w, (pad + hot[1] * k) / n_h)
    return _ro(img.astype(np.float32))


def click_ring(t, r=64, color=None, look='neon'):
    """Click feedback sprite (emissive): an expanding ring + a quick inner flash, t = seconds since the click
    (0..0.6). Draw it centred on the hotspot with mode='add' (dark looks) or 'over'."""
    t = round(max(0.0, float(t)) * 120) / 120.0
    return _click_cached(t, int(r), _key(color), look)


@functools.lru_cache(maxsize=256)
def _click_cached(t, r, color, lk):
    L = LOOKS[lk]
    c = col(color) if color is not None else (L.accent_hi if L.dark else L.accent)
    n = int(r * 2.6)
    S = Surf(n, n)
    u = K.ramp(t, 0.0, 0.55, 'out_cubic')
    rr = r * (0.25 + 0.75 * u)
    fade = (1 - K.ramp(t, 0.1, 0.6, 'linear'))
    fl = 1 - K.ramp(t, 0.0, 0.18, 'out_cubic')
    if L.dark:
        a, X0, Y0 = S.ring(n / 2, n / 2, rr, 2.5 + 3.5 * (1 - u), c, fade, emit=True)
        S.glow(a, X0, Y0, c, (4, 10), 0.6 * fade)
        S.circle(n / 2, n / 2, r * 0.32, _v(C['WHITE']), 0.45 * fl, emit=True)
    else:
        S.circle(n / 2, n / 2, r * 0.32, c, 0.22 * fl)
        a, X0, Y0 = S.ring(n / 2, n / 2, rr, 2.5 + 3.5 * (1 - u), c, 0.85 * fade)
    return _ro(S.img)


def draw_cursor(cv, x, y, kind='arrow', size=72, press=0.0, click=None, opacity=1.0, look='neon', scale=1.0,
                rot=0.0):
    """Draw a cursor with its hotspot at (x, y) (+ a click ring when click = seconds since a click)."""
    if click is not None and 0 <= click < 0.65:
        cr = click_ring(click, int(size * 0.9), look=look)
        K.draw(cv, cr, x, y, scale=scale, opacity=opacity, mode='add' if LOOKS[look].dark else 'over')
    spr = cursor(kind, size, press, look)
    return K.draw(cv, spr, x, y, scale=scale, rot=rot, opacity=opacity, anchor=_CURSOR_ANCHOR[(kind, int(size))])


# =============================================================================================== progress ring
def progress_ring(p=0.0, size=320, width=24, look='neon', label='auto', sub=None, colors=None, glow=1.0,
                  label_size=None):
    """Progress ring sprite ((size + 96)^2, centred). p 0..1 fills clockwise from 12 o'clock with a gradient arc,
    round caps, a hot head dot and glow. label: 'auto' = '{p:.0%}', None = none, or any text; sub: line below."""
    p = round(min(max(float(p), 0.0), 1.0) * 400) / 400.0
    lab = ('%d%%' % round(p * 100)) if label == 'auto' else label
    return _ring_cached(p, int(size), float(width), look, lab, sub, _key(colors), float(glow), label_size)


@functools.lru_cache(maxsize=512)
def _ring_cached(p, size, width, lk, label, sub, colors, glow, label_size):
    L = LOOKS[lk]
    P = 48
    n = size + 2 * P
    S = Surf(n, n)
    c = n / 2
    R = size / 2 - width / 2
    xs, ys = _grid(0, 0, n, n)
    dx, dy = xs - c, ys - c
    rho = np.sqrt(dx * dx + dy * dy)
    band = np.abs(rho - R) - width / 2
    # track
    if L.dark:
        S.fill(_cov(band), 0, 0, _v(C['WHITE']), 0.09)
        S.fill(_cov(np.abs(rho - R - width / 2 + 0.6) - 0.6), 0, 0, _v(C['WHITE']), 0.10)
    else:
        S.fill(_cov(band), 0, 0, L.text, 0.07)
    c0, c1 = (col(colors[0]), col(colors[1])) if colors is not None else L.grad
    if p > 0:
        th = (np.arctan2(dx, -dy) / (2 * math.pi)) % 1.0
        if p >= 1.0:
            d = band
        else:
            ea = 2 * math.pi * p
            ex, ey = c + R * math.sin(ea), c - R * math.cos(ea)
            ds_ = np.sqrt((xs - c) ** 2 + (ys - (c - R)) ** 2) - width / 2
            de_ = np.sqrt((xs - ex) ** 2 + (ys - ey) ** 2) - width / 2
            d = np.where(th <= p, band, np.minimum(ds_, de_))
        a = _cov(d)
        tn = np.clip(th / max(p, 1e-3), 0, 1)
        tn = np.where((th > p) & (np.abs(dx) < width) & (dy < 0), 0.0, tn)
        img = c0[None, None, :] * (1 - tn[..., None]) + c1[None, None, :] * tn[..., None]
        S.fill(a, 0, 0, img.astype(np.float32), 1.0)
        # glow
        src = np.ascontiguousarray(img * a[..., None])
        gl = K.gblur(src, 7.0, border='constant') * 0.8 + K.gblur(src, 20.0, border='constant') * 0.5
        S.img[..., :3] += gl * np.float32(glow * (1.0 if L.dark else 0.45)) * (1 - a[..., None] * 0.85)
        # inner sheen on the arc
        sh = np.exp(-((rho - (R - width * 0.22)) / (width * 0.18)) ** 2) * a * 0.18
        S.emit(sh, 0, 0, _v(C['WHITE']), 1.0)
        if p < 1.0:
            ea = 2 * math.pi * p
            ex, ey = c + R * math.sin(ea), c - R * math.cos(ea)
            hd, X0, Y0 = S.circle(ex, ey, width * 0.26, _v(C['WHITE']), 0.95)
            S.glow(hd, X0, Y0, K.mix(c1, C['WHITE'], 0.3), (4, 12), 1.2 * glow, knock=0.0)
    if label:
        ls = label_size or size * 0.25
        dy_ = -ls * 0.12 if sub else 0
        put_text(S.img, c, c + dy_, label, ls, 'head_black', L.text, 'mm')
        if sub:
            put_text(S.img, c, c + ls * 0.55 + 18, sub, 28, 'ui_medium', L.text2, 'mm', max_w=size * 0.8)
    return _ro(S.img)


# =============================================================================================== slider
SLIDER_PAD = 40


def slider_knob(v, w=720):
    """(x, y) of the slider knob centre in sprite px."""
    return SLIDER_PAD + min(max(v, 0.0), 1.0) * w, SLIDER_PAD + 104 + 24


def slider(v=0.0, w=720, look='neon', label=None, colors=None, ticks=None, bubble=True, knob=48, track_h=12):
    """Horizontal slider sprite ((w + 80) x 252): track, gradient fill up to the knob, white knob with glow, a value
    bubble (label, e.g. '52 weeks') above the knob and optional ticks [(frac, text), ...] under the track.
    slider_knob(v, w) gives the knob centre (for a dragging cursor)."""
    v = round(min(max(float(v), 0.0), 1.0) * 1000) / 1000.0
    return _slider_cached(v, int(w), look, label, _key(colors), tuple(ticks) if ticks else None, bool(bubble),
                          int(knob), int(track_h))


@functools.lru_cache(maxsize=512)
def _slider_cached(v, w, lk, label, colors, ticks, bubble, knob, th):
    L = LOOKS[lk]
    P = SLIDER_PAD
    Hs = 252
    S = Surf(w + 2 * P, Hs)
    kx, ky = slider_knob(v, w)
    c0, c1 = (col(colors[0]), col(colors[1])) if colors is not None else L.grad
    # track
    if L.dark:
        S.rrect(P, ky - th / 2, w, th, th / 2, _v(C['WHITE']), 0.12)
    else:
        S.rrect(P, ky - th / 2, w, th, th / 2, L.text, 0.15)
    if v > 0:
        fw = max(kx - P, th)
        a, X0, Y0 = S.rrect_mask(P, ky - th / 2, fw, th, th / 2)
        g = _lingrad(a.shape[1], a.shape[0], c0, c1, 0)
        S.fill(a, X0, Y0, g, 1.0)
        S.glow(a, X0, Y0, (c0 + c1) / 2, (5, 14), 0.6 if L.dark else 0.3, knock=0.8)
    if ticks:
        for fr, tx in ticks:
            x = P + fr * w
            S.rrect(x - 1, ky + 22, 2, 10, 1, L.text3, 1.0)
            put_text(S.img, x, ky + 66, tx, 28, 'ui_medium', L.text2, 'ms')
    # knob
    kr = knob / 2
    a, X0, Y0 = S.rrect_mask(kx - kr, ky - kr + 5, knob, knob, kr)
    sh = K.gblur(np.pad(a, 12), 5.0, border='constant')
    S.fill(sh, X0 - 12, Y0 - 12, L.shadow if L.dark else _v(C['INK']), 0.55 if L.dark else 0.25)
    a, X0, Y0 = S.circle(kx, ky, kr, _v(C['WHITE']), 1.0)
    S.glow(a, X0, Y0, c1, (6, 16), 0.55 if L.dark else 0.25)
    S.ring(kx, ky, kr - 1.5, 3.0, c1, 0.9)
    S.circle(kx, ky, kr * 0.28, c0, 1.0)
    # bubble
    if bubble and label:
        tw = measure(label, 34, 'ui')
        bw, bh = tw + 44, 62
        bx = min(max(kx - bw / 2, 4), w + 2 * P - bw - 4)
        by = ky - kr - 22 - bh
        a, X0, Y0 = S.rrect_mask(bx, by, bw, bh, 18)
        g = _lingrad(a.shape[1], a.shape[0], c0, c1, 20)
        tri = fill_mask([(np.array([[kx - 11, by + bh - 2], [kx + 11, by + bh - 2], [kx, by + bh + 12]]), True)],
                        w + 2 * P, Hs)
        S.fill(tri, 0, 0, K.mix(c0, c1, (kx - bx) / bw), 1.0)
        S.fill(a, X0, Y0, g, 1.0)
        S.glow(a, X0, Y0, (c0 + c1) / 2, (6, 16), 0.35 if L.dark else 0.2, knock=0.9)
        S.sheen(bx + 1, by + 1, bw - 2, bh - 2, 17, 0.08, 0.0, 0.6)
        put_text(S.img, bx + bw / 2, by + bh / 2, label, 34, 'ui', C['WHITE'], 'mm')
    return _ro(S.img)


# =============================================================================================== bar chart
def bar_chart(values, labels=None, grow=1.0, active=None, w=760, h=560, look='amber', fmt=None, vmax=None, grid=4,
              colors=None, value_labels=True, bar_r=18, gap=0.40, dim=0.42, depth=0, label_size=30,
              value_size=30):
    """Glossy gradient bar chart sprite ((w + 64) x (h + 64)): baseline grid, bars that grow (grow = scalar or one
    value per bar, 0..1, overshoot ok), value labels that count up with each bar (fmt(v), default money), x labels,
    and an active bar (index; fractional = cross-fade) that glows while the others dim.
    depth > 0 adds an isometric 3D side + top face (px).
        bars = bar_chart([447.60, 473.17, 515.52, 554.02], ['0–4', '5–10', '11–14', '15+'],
                         grow=[K.ramp(t, 5.2 + .2 * i, 6.0 + .2 * i, 'out_back') for i in range(4)], active=act)"""
    vals = tuple(float(x) for x in values)
    n = len(vals)
    g = [float(grow)] * n if np.ndim(grow) == 0 else [float(x) for x in grow]
    fmt = fmt or (lambda v: money(v))
    L = LOOKS[look]
    P = 32
    S = Surf(w + 2 * P, h + 2 * P)
    S.img[:] = _bar_grid(w, h, look, grid, tuple(labels) if labels else None, n, float(label_size))
    TL, BL = 72, (64 if labels else 16)
    PH = h - TL - BL
    base = P + TL + PH
    vmax = vmax or max(vals) * 1.12
    slot = w / n
    bw = slot * (1 - gap)
    c0, c1 = (col(colors[0]), col(colors[1])) if colors is not None else \
        ((_v(C['ORANGE'], 0.85), _v(C['AMBER'])) if look == 'amber' else L.grad)
    for i, v in enumerate(vals):
        gi = max(0.0, g[i])
        if gi <= 0:
            continue
        act = 1.0 if active is None else float(np.clip(1 - abs(i - active), 0, 1))
        op = 1.0 if active is None else dim + (1 - dim) * act
        hgt = PH * v / vmax * gi
        x = P + slot * i + (slot - bw) / 2
        top = base - hgt
        r = min(bar_r if not depth else 6, bw / 2, max(hgt, 1) / 2 + 0.01)
        a, X0, Y0 = S.rrect_mask(x, top, bw, hgt + r + 2, r)
        if a is None:
            continue
        yy = np.arange(a.shape[0], dtype=np.float32) + Y0 + 0.5
        a = a * (yy < base)[:, None]
        hh_, ww_ = a.shape
        ty = np.clip((yy - top) / max(PH, 1), 0, 1)[:, None, None]
        xn = ((np.arange(ww_, dtype=np.float32) + X0 + 0.5 - x) / bw)[None, :, None]
        fill = c1[None, None, :] * (1 - ty) + c0[None, None, :] * ty
        fill = fill * (1.0 + 0.25 * act) * (1 - 0.22 * np.clip((xn - 0.62) / 0.38, 0, 1))
        if depth:
            dx_, dy_ = depth * 0.8, depth * 0.55
            side = fill_mask([(np.array([[x + bw, top], [x + bw + dx_, top - dy_], [x + bw + dx_, base - dy_],
                                         [x + bw, base]]), True)], S.w, S.h)
            S.fill(side, 0, 0, c0 * 0.55 * (1 + 0.2 * act), op)
            topf = fill_mask([(np.array([[x, top], [x + bw, top], [x + bw + dx_, top - dy_], [x + dx_, top - dy_]]),
                               True)], S.w, S.h)
            S.fill(topf, 0, 0, K.mix(c1, C['WHITE'], 0.25) * (1 + 0.2 * act), op)
        S.fill(a, X0, Y0, fill.astype(np.float32), op)
        # gloss stripe + top cap
        stripe = np.exp(-((xn[..., 0] - 0.24) / 0.10) ** 2) * 0.30 + np.exp(-((xn[..., 0] - 0.08) / 0.05) ** 2) * 0.12
        S.emit(a * stripe * np.clip(1.15 - ty[..., 0] * 0.8, 0.3, 1), X0, Y0, _v(C['WHITE']), op)
        cap = np.exp(-((yy[:, None] - top - 2.5) / 1.6) ** 2) * a
        S.emit(cap, X0, Y0, _v(C['WHITE']), 0.5 * op)
        if act > 0 and active is not None:
            S.glow(a, X0, Y0, (c0 + c1) / 2, (8, 24, 48), 0.55 * act * (1.0 if L.dark else 0.5))
        if value_labels and gi > 0.02:
            vs = value_size + 4 * act
            tc = K.mix(L.text2, L.text, act) if active is not None else L.text
            put_text(S.img, x + bw / 2 + (depth * 0.4 if depth else 0), top - 18 - (depth * 0.55 if depth else 0),
                     fmt(v * min(gi, 1.0)), vs, 'ui', tc, 'ms', opacity=min(1.0, gi * 3) * (0.6 + 0.4 * op))
    if labels and active is not None:
        for i, lab in enumerate(labels):
            act = float(np.clip(1 - abs(i - active), 0, 1))
            if act > 0:
                x = P + slot * i + slot / 2
                put_text(S.img, x, base + 46, lab, label_size, 'ui', L.text, 'ms', opacity=act)
    return S.img


@functools.lru_cache(maxsize=16)
def _bar_grid(w, h, lk, grid, labels, n, label_size):
    L = LOOKS[lk]
    P = 32
    S = Surf(w + 2 * P, h + 2 * P)
    TL, BL = 72, (64 if labels else 16)
    PH = h - TL - BL
    base = P + TL + PH
    for k in range(1, grid + 1):
        y = base - PH * k / grid
        for xx in range(0, w, 16):
            S.rrect(P + xx, y - 0.75, 8, 1.5, 0.75, L.line, L.line_a * 1.1)
    S.rrect(P, base - 1, w, 2.0, 1.0, L.line, L.line_a * 2.6)
    if labels:
        slot = w / n
        for i, lab in enumerate(labels):
            put_text(S.img, P + slot * i + slot / 2, base + 46, lab, label_size, 'ui_medium', L.text2, 'ms')
    return _ro(S.img)


# =============================================================================================== toast / tags / badge
@functools.lru_cache(maxsize=32)
def toast(title, sub=None, icon_name='check', look='neon', w=640, accent=None, rim=0.6):
    """Toast notification -> glass Panel: icon disc (LEAF gradient by default) + title + sub.
    Animate with the draw: e.g. y offset 40 * (1 - K.ramp(t, t0, t0 + .5)), scale 0.94 -> 1, opacity."""
    L = LOOKS[look]
    h = 132 if sub else 108
    base = glass_card(w, h, 34, look, rim=rim, glow=0.7)
    f = base.face.copy()
    p = base.pad
    S = Surf(f.shape[1], f.shape[0], f)
    cx, cy = p + 28 + 34, p + h / 2
    c0, c1 = (col(accent[0]), col(accent[1])) if accent else (L.ok_hi, L.ok)
    a, X0, Y0 = S.circle(cx, cy, 34, c1)
    g = _lingrad(a.shape[1], a.shape[0], c0, c1, -70)
    S.fill(a, X0, Y0, g, 1.0)
    S.glow(a, X0, Y0, c1, (6, 16), 0.5 if L.dark else 0.25)
    S.sheen(cx - 33, cy - 33, 66, 66, 33, 0.12, 0.0, 0.55)
    S.paste(icon(icon_name, 38, C['WHITE'], stroke=2.8), cx, cy, anchor=(0.5, 0.5))
    tx = p + 28 + 68 + 24
    mw = w - (tx - p) - 28
    if sub:
        put_text(f, tx, p + h / 2 - 6, title, 36, 'ui', L.text, 'ls', max_w=mw)
        put_text(f, tx, p + h / 2 + 34, sub, 28, 'body', L.text2, 'ls', max_w=mw)
    else:
        put_text(f, tx, p + h / 2, title, 36, 'ui', L.text, 'lm', max_w=mw)
    return derive_panel(base, f)


def tag_size(text, size=34, h=84, thumb=False, icon_name=None):
    tw = measure(text, size, 'ui')
    lead = (h - 16 + 16) if thumb else ((h * 0.42 + 14) if icon_name else 0)
    return int(math.ceil((tw + 2 * 30 + lead - (14 if thumb else 0)) / 8.0) * 8), int(h)


def tag(text, thumb=None, look='neon', size=34, h=84, icon_name=None, accent=None, rim=0.5, thumb_key=None):
    """Glass pill tag -> Panel: text with an optional rounded thumbnail (any sprite; pass a stable thumb_key
    string so it caches) or icon. Used by orbit_ring(); also good for chips that need real frost."""
    key = thumb_key if thumb_key is not None else (_content_key(thumb) if thumb is not None else None)
    return _tag_cached(text, look, float(size), int(h), icon_name, _key(accent), float(rim), key,
                       _ThumbBox(thumb))


def _content_key(spr):
    """Stable cache key from a sprite's content (shape + a strided pixel sample hash). Replaces the old id()
    fallback, which could be reused by a different array after garbage collection (wrong thumbnail)."""
    a = np.ascontiguousarray(np.asarray(spr)[::7, ::7])
    return ('px', a.shape, hash(a.tobytes()))


class _ThumbBox:
    """Hash-neutral holder so a sprite can ride along an lru_cache key (identity is in thumb_key)."""
    __slots__ = ('spr',)

    def __init__(self, spr):
        self.spr = spr

    def __hash__(self):
        return 0

    def __eq__(self, o):
        return isinstance(o, _ThumbBox)


@functools.lru_cache(maxsize=64)
def _tag_cached(text, lk, size, h, icon_name, accent, rim, key, thumb_box):
    L = LOOKS[lk]
    thumb = thumb_box.spr
    w, h = tag_size(text, size, h, thumb is not None, icon_name)
    base = glass_card(w, h, h / 2, lk, rim=rim, glow=0.6, shadow=0.8)
    f = base.face.copy()
    p = base.pad
    x = 30
    if thumb is not None:
        ts = h - 16
        put_media(base, f, thumb, 8, 8, ts, ts, ts / 2)
        S = Surf(f.shape[1], f.shape[0], f)
        S.ring(p + 8 + ts / 2, p + 8 + ts / 2, ts / 2 - 0.5, 1.6, _v(C['WHITE']), 0.7)
        x = 8 + ts + 16
    elif icon_name:
        isz = int(h * 0.42)
        ac = col(accent) if accent is not None else (L.accent_hi if L.dark else L.accent)
        base_ic = icon(icon_name, isz, ac, stroke=2.4, glow=0.5 if L.dark else 0.0)
        paste(f, base_ic, p + x + isz / 2 - base_ic.shape[1] / 2, p + h / 2 - base_ic.shape[0] / 2)
        x += isz + 14
    put_text(f, p + x, p + h / 2, text, size, 'ui', L.text, 'lm')
    return derive_panel(base, f)


@functools.lru_cache(maxsize=16)
def badge(text='Rated Good by Ofsted', sub=None, look='neon', icon_name='star', size=34, glass=True):
    """Badge -> Panel: a gold star disc + text (+ sub line), e.g. badge('Rated Good by Ofsted',
    'Inspected May 2025'). glass=False gives a plain sprite in .face with no frost needed."""
    L = LOOKS[look]
    tw = max(measure(text, size, 'ui'), measure(sub, 28, 'body') if sub else 0)
    h = 112 if sub else 88
    w = int(math.ceil((tw + 24 + 64 + 20 + 36) / 8) * 8)
    base = glass_card(w, h, h / 2, look, rim=0.5, glow=0.6, shadow=0.8 if glass else 0.0)
    f = base.face.copy()
    p = base.pad
    S = Surf(f.shape[1], f.shape[0], f)
    cx, cy = p + 16 + 32, p + h / 2
    a, X0, Y0 = S.circle(cx, cy, 32, _v(C['AMBER']))
    g = _lingrad(a.shape[1], a.shape[0], C['AMBER'], _v(C['ORANGE']), -70)
    S.fill(a, X0, Y0, g, 1.0)
    S.glow(a, X0, Y0, _v(C['AMBER']), (5, 14), 0.5 if L.dark else 0.25)
    S.sheen(cx - 31, cy - 31, 62, 62, 31, 0.16, 0.0, 0.55)
    S.paste(icon(icon_name, 36, C['WHITE'], stroke=2.2, fill_a=1.0), cx, cy, anchor=(0.5, 0.5))
    tx = p + 16 + 64 + 20
    if sub:
        put_text(f, tx, p + h / 2 - 6, text, size, 'ui', L.text, 'ls')
        put_text(f, tx, p + h / 2 + 32, sub, 28, 'body', L.text2, 'ls')
    else:
        put_text(f, tx, p + h / 2, text, size, 'ui', L.text, 'lm')
    return derive_panel(base, f)


# =============================================================================================== dock tile
@functools.lru_cache(maxsize=32)
def dock_tile(title, sub=None, icon_name='graduation', look='neon', w=300, h=460, accent=None, r=44,
              title_size=36, sub_size=28):
    """Dock tile -> glass Panel: a media slot at the top (coloured glow blob + glowing vector icon), a title (wraps
    to 2 lines) and a subtitle (2 lines). meta['slot'] = (x, y, w, h, r). Animate it with dock_face(tile, focus,
    media, ...). accent: colour spec for the blob / focus light (default the look's accent).
        tiles = [dock_tile('Full Training', 'Preparation & ongoing learning', 'graduation', accent='MAGENTA'), ...]"""
    L = LOOKS[look]
    base = glass_card(w, h, r, look, rim=0.7, glow=0.8)
    f = base.face.copy()
    p = base.pad
    S = Surf(f.shape[1], f.shape[0], f)
    ac = col(accent) if accent is not None else L.accent
    tl = wrap(title, title_size, 'ui', w - 52)[:2]
    sl = wrap(sub, sub_size, 'body', w - 52)[:2] if sub else []
    text_h = 24 + len(tl) * (title_size + 8) + (8 + len(sl) * (sub_size + 10) if sl else 0) + 20
    sx, sy, sw = 18, 18, w - 36
    sh = int(min(h * 0.56, h - sy - text_h))
    sr = r - 16
    # slot: deeper glass + glow blob + icon
    S.rrect(p + sx, p + sy, sw, sh, sr, (L.tint_bot if L.dark else _v(C['WHITE'])), 0.55 if L.dark else 0.5)
    blob = K.radial(int(sw * 1.1), ac, power=1.8)
    bm, X0, Y0 = S.rrect_mask(p + sx, p + sy, sw, sh, sr)
    tmp = np.zeros_like(f)
    K.draw(tmp, blob, p + sx + sw / 2, p + sy + sh * 0.62, mode='add')
    f[Y0:Y0 + bm.shape[0], X0:X0 + bm.shape[1], :3] += tmp[Y0:Y0 + bm.shape[0], X0:X0 + bm.shape[1], :3] * \
        bm[..., None] * (0.9 if L.dark else 0.6)
    S.stroke_rrect(p + sx, p + sy, sw, sh, sr, 1.3, _v(C['WHITE']), 0.22 if L.dark else 0.8,
                   weight=lambda xs, ys: np.clip(1.2 - (ys - p - sy) / sh, 0.2, 1))
    if icon_name:
        ic = icon(icon_name, int(min(sh, sw) * 0.46), C['WHITE'], stroke=2.1, glow=0.9,
                  glow_color=K.mix(ac, C['WHITE'], 0.2))
        S.paste(ic, p + sx + sw / 2, p + sy + sh / 2, anchor=(0.5, 0.5))
    y = sy + sh + 24 + title_size * 0.78
    for ln in tl:
        put_text(f, p + 26, p + y, ln, title_size, 'ui', L.text, 'ls', max_w=w - 52)
        y += title_size + 8
    y += 8 + sub_size * 0.2
    for ln in sl:
        put_text(f, p + 26, p + y, ln, sub_size, 'body', L.text2, 'ls', max_w=w - 52)
        y += sub_size + 10
    return derive_panel(base, f, {'slot': (sx, sy, sw, sh, sr), 'accent': tuple(ac), 'icon': icon_name})


@functools.lru_cache(maxsize=32)
def _focus_layer(tile):
    """Emissive focus light for a tile (edge glow in the accent colour + brighter slot)."""
    L = LOOKS[tile.look]
    ac = np.asarray(tile.meta.get('accent', L.accent), np.float32)
    out = np.zeros_like(tile.face)
    S = Surf(out.shape[1], out.shape[0], out)
    p = tile.pad
    a, X0, Y0 = S.stroke_rrect(p, p, tile.w, tile.h, tile.r, 2.2, K.mix(ac, C['WHITE'], 0.35), 1.0, emit=True)
    S.glow(a, X0, Y0, ac, (6, 18, 40), 0.9, knock=0.0)
    sx, sy, sw, sh, sr = tile.meta['slot']
    m, X0, Y0 = S.rrect_mask(p + sx, p + sy, sw, sh, sr)
    S.emit(m, X0, Y0, ac, 0.10 if L.dark else 0.05)
    out[..., 3] = 0
    return _ro(out)


def dock_face(tile, focus=0.0, media=None, media_mix=1.0, sweep=None, light=None, icon_spr=None, icon_scale=1.0):
    """Per-frame face of a dock tile: focus 0..1 lights the edge and slot; media (a footage sprite, e.g.
    clip.get(t, sw, sh, look=...)) fills the slot with rounded corners (media_mix fades it in, a small icon
    disc stays in the corner); icon_spr (e.g. a sprites3d frame) replaces the vector icon; sweep / light as in
    Panel.face_at."""
    f = tile.face_at(sweep=sweep, light=None)
    if focus > 0:
        f += _focus_layer(tile) * np.float32(focus)
    sx, sy, sw, sh, sr = tile.meta['slot']
    L = LOOKS[tile.look]
    if icon_spr is not None:
        s = min(sw * 0.62 / icon_spr.shape[1], sh * 0.82 / icon_spr.shape[0]) * icon_scale
        K.draw(f, icon_spr, tile.pad + sx + sw / 2, tile.pad + sy + sh / 2, scale=s)
    if media is not None and media_mix > 0:
        put_media(tile, f, media, sx, sy, sw, sh, sr, opacity=media_mix)
        if media_mix > 0.05:
            ac = np.asarray(tile.meta.get('accent', L.accent), np.float32)
            S = Surf(f.shape[1], f.shape[0], f)
            cx, cy = tile.pad + sx + 44, tile.pad + sy + 44
            a, X0, Y0 = S.circle(cx, cy, 28, ac, media_mix)
            S.glow(a, X0, Y0, ac, (4, 12), 0.5 * media_mix)
            S.sheen(cx - 27, cy - 27, 54, 54, 27, 0.12 * media_mix, 0, 0.55)
            if tile.meta.get('icon'):
                S.paste(icon(tile.meta['icon'], 30, C['WHITE'], stroke=2.6), cx, cy, opacity=media_mix,
                        anchor=(0.5, 0.5))
    if light is not None:
        tile._add_light(f, light, None, -28.0, 0.07)
    return f


def carousel(n, focus, spacing=360.0, grow=0.16, lift=0.0):
    """Carousel layout for n tiles with a (fractional) focus index -> list of (dx, scale, weight) where weight
    1 = focused. dx is relative to the focused tile; neighbours spread a little so the enlarged one fits."""
    out = []
    for i in range(n):
        d = i - focus
        wgt = max(0.0, 1 - abs(d))
        s = 1 + grow * wgt
        dx = d * spacing + np.sign(d) * grow * spacing * 0.5 * min(1.0, abs(d))
        out.append((float(dx), float(s), float(wgt)))
    return out


# =============================================================================================== small widgets
def search_bar(text='', n=None, t=0.0, w=720, h=96, look='neon', placeholder='Search support', caret=True,
               go=True):
    """Search bar sprite ((w + 48) x (h + 48)): glass pill, search icon, typed text (n = characters typed, float;
    None = all) with a caret (solid while typing, blinking 1.4 Hz when idle) and a gradient go button."""
    L = LOOKS[look]
    base = _search_base(int(w), int(h), look, bool(go))
    out = base.copy()
    P = 24
    k = len(text) if n is None else int(max(0, min(len(text), math.floor(n))))
    shown = text[:k]
    tx = P + 32 + 40 + 20
    if shown:
        put_text(out, tx, P + h / 2, shown, 36, 'ui_medium', L.text, 'lm')
    elif placeholder:
        put_text(out, tx, P + h / 2, placeholder, 36, 'body', L.text3, 'lm')
    if caret:
        typing = n is not None and n < len(text) and n > 0
        on = typing or ((t * 1.4) % 1.0 < 0.6)
        if on:
            cx = tx + (measure(shown, 36, 'ui_medium') if shown else 0) + 4
            S = Surf(out.shape[1], out.shape[0], out)
            S.rrect(cx, P + h / 2 - 22, 3.5, 44, 1.75, L.accent_hi if L.dark else L.accent, 1.0)
    return out


@functools.lru_cache(maxsize=8)
def _search_base(w, h, lk, go):
    L = LOOKS[lk]
    P = 24
    S = Surf(w + 2 * P, h + 2 * P)
    r = h / 2
    if L.dark:
        S.rrect(P, P, w, h, r, L.tint_top, 0.75)
        S.rrect(P, P, w, h, r, _v(C['WHITE']), 0.05)
        S.stroke_rrect(P, P, w, h, r, 1.6, _v(C['WHITE']), 0.35,
                       weight=lambda xs, ys: np.clip(1.25 - (ys - P) / h * 0.9, 0.3, 1))
    else:
        a, X0, Y0 = S.rrect_mask(P + 6, P + 12, w - 12, h - 6, r)
        S.fill(K.gblur(np.pad(a, 16), 9.0, border='constant'), X0 - 16, Y0 - 16, L.shadow, 0.18)
        S.rrect(P, P, w, h, r, _v(C['WHITE']), 0.92)
        S.stroke_rrect(P, P, w, h, r, 1.5, L.text, 0.08)
    S.paste(icon('search', 40, L.text2, stroke=2.4), P + 32 + 20, P + h / 2, anchor=(0.5, 0.5))
    if go:
        gs = h - 20
        gx = P + w - 10 - gs
        a, X0, Y0 = S.rrect_grad(gx, P + 10, gs, gs, gs / 2, C['MAGENTA'], C['ORANGE'], 35)
        S.glow(a, X0, Y0, _v(C['HOT_PINK']), (5, 14), 0.4 if L.dark else 0.2)
        S.sheen(gx + 1, P + 11, gs - 2, gs - 2, gs / 2, 0.10, 0, 0.55)
        S.paste(icon('arrow_right', int(gs * 0.48), C['WHITE'], stroke=2.8), gx + gs / 2, P + h / 2, anchor=(0.5, 0.5))
    return _ro(S.img)


def avatar(img, size=120, look='neon', ring=None, ring_w=5, gap=5, status=False, zoom=1.0, center=(0.5, 0.42)):
    """Avatar sprite ((size + 48)^2): a photo / footage sprite cover-cropped into a circle inside a gradient ring
    (ring=(c0, c1), default brand) with a transparent gap, soft shadow and an optional LEAF status dot."""
    L = LOOKS[look]
    P = 24
    n = int(size + 2 * P)
    S = Surf(n, n)
    c = n / 2
    R = size / 2
    sh = np.zeros((n, n), np.float32)
    xs, ys = _grid(0, 0, n, n)
    sh = _cov(np.sqrt((xs - c) ** 2 + (ys - c - 6) ** 2) - R)
    S.fill(K.gblur(sh, 8.0, border='constant'), 0, 0, L.shadow, 0.5 if L.dark else 0.2)
    c0, c1 = (col(ring[0]), col(ring[1])) if ring is not None else (_v(C['MAGENTA']), _v(C['ORANGE']))
    ra = _cov(np.abs(np.sqrt((xs - c) ** 2 + (ys - c) ** 2) - (R - ring_w / 2)) - ring_w / 2)
    S.fill(ra, 0, 0, _lingrad(n, n, c0, c1, 35), 1.0)
    S.glow(ra, 0, 0, (c0 + c1) / 2, (4, 10), 0.4 if L.dark else 0.15, knock=0.5)
    pr = R - ring_w - gap
    ph = media_fit(img, int(2 * pr) + 2, int(2 * pr) + 2, 0, center=center, zoom=zoom)
    pm = _cov(np.sqrt((xs - c) ** 2 + (ys - c) ** 2) - pr)
    x0 = int(round(c - pr - 1))
    big = np.zeros((n, n, 4), np.float32)
    paste(big, ph, x0, x0)
    big *= pm[..., None]
    K._blend(S.img, big, 1.0, 'over')
    if status:
        sx_, sy_ = c + R * 0.70, c + R * 0.70
        S.circle(sx_, sy_, size * 0.10 + 3, L.tint_bot if L.dark else _v(C['WHITE']), 1.0)
        a, X0, Y0 = S.circle(sx_, sy_, size * 0.10, L.ok_hi, 1.0)
        S.glow(a, X0, Y0, L.ok, (3, 8), 0.5)
    return S.img


def steps(active=0.0, n=5, w=880, look='neon', labels=None, size=72, numbers=True):
    """Step indicator sprite ((w + 64) x (size + 140)): numbered dots 01..0n joined by a track that fills up to
    `active` (float index), done dots filled with a check, the active dot enlarged with glow. labels: optional
    texts under each dot (keep them short: >= 28 px)."""
    a = round(float(active) * 60) / 60.0
    return _steps_cached(a, int(n), int(w), look, tuple(labels) if labels else None, int(size), bool(numbers))


@functools.lru_cache(maxsize=512)
def _steps_cached(active, n, w, lk, labels, size, numbers):
    L = LOOKS[lk]
    P = 32
    Hs = size + 140
    S = Surf(w + 2 * P, Hs)
    cy = P + size / 2 + 12
    xs_ = [P + size / 2 + (w - size) * i / max(n - 1, 1) for i in range(n)]
    c0, c1 = L.grad
    # track
    S.rrect(xs_[0], cy - 3, xs_[-1] - xs_[0], 6, 3, _v(C['WHITE']) if L.dark else L.text, 0.12 if L.dark else 0.12)
    fx = np.interp(min(max(active, 0), n - 1), np.arange(n), xs_)
    if fx > xs_[0]:
        a, X0, Y0 = S.rrect_mask(xs_[0], cy - 3, fx - xs_[0], 6, 3)
        S.fill(a, X0, Y0, _lingrad(a.shape[1], a.shape[0], c0, c1, 0), 1.0)
        S.glow(a, X0, Y0, (c0 + c1) / 2, (4, 10), 0.45 if L.dark else 0.2)
    for i, x in enumerate(xs_):
        act = float(np.clip(1 - abs(i - active), 0, 1))
        done = float(np.clip(active - i + 0.5, 0, 1)) if i < active else 0.0
        r = size / 2 * (1 + 0.16 * act)
        if done > 0 or act > 0:
            k = max(done, act)
            a, X0, Y0 = S.circle(x, cy, r, c0, 0)
            S.fill(a, X0, Y0, _lingrad(a.shape[1], a.shape[0], c0, c1, 35), k)
            S.glow(a, X0, Y0, (c0 + c1) / 2, (6, 18), (0.25 + 0.55 * act) * (1.0 if L.dark else 0.5), knock=0.9)
            S.sheen(x - r, cy - r, 2 * r, 2 * r, r, 0.10 * k, 0, 0.55)
        if k_rest := (1 - max(done, act)):
            if L.dark:
                S.circle(x, cy, r, L.tint_top, k_rest)
                S.ring(x, cy, r - 1, 2.0, _v(C['WHITE']), 0.25 * k_rest)
            else:
                S.circle(x, cy, r, _v(C['WHITE']), 0.9 * k_rest)
                S.ring(x, cy, r - 1, 2.0, L.text, 0.22 * k_rest)
        if numbers:
            if done > 0.5 and act < 0.5:
                S.paste(icon('check', int(size * 0.42), C['WHITE'], stroke=3.0), x, cy, anchor=(0.5, 0.5))
            else:
                tc = K.mix(L.text2, C['WHITE'], max(act, done))
                put_text(S.img, x, cy, '%02d' % (i + 1), 28 + 4 * act, 'ui', tc, 'mm')
        if labels:
            put_text(S.img, x, cy + size / 2 + 56, labels[i], 28, 'ui_medium', K.mix(L.text2, L.text, act), 'ms')
    return S.img


# =============================================================================================== orbit ring
def _orbit_points(angles, radius, tilt, roll):
    """Local ring points: a horizontal circle (x-z plane) seen from `tilt` degrees above (the far side rises on
    screen), then rolled `roll` degrees clockwise. Returns (N, 3) and the pre-roll depth z (for front/back)."""
    a = np.asarray(angles, np.float64)
    rx, rz = (radius, radius) if np.ndim(radius) == 0 else radius
    x = rx * np.cos(a)
    z = rz * np.sin(a)
    t = math.radians(tilt)
    y = -z * math.sin(t)
    z2 = z * math.cos(t)
    r = math.radians(roll)
    xr = x * math.cos(r) - y * math.sin(r)
    yr = x * math.sin(r) + y * math.cos(r)
    return np.stack([xr, yr, z2], 1), z


def _ring_line(cv, cam, center, radius, tilt, roll, color, part, opacity, width=2.0, glow=1.0, dashed=False,
               light=False):
    a = np.linspace(0, 2 * math.pi, 361)
    P, z = _orbit_points(a, radius, tilt, roll)
    P = P + np.asarray(center, np.float64)
    xy, d = cam.project(P)
    ok = np.isfinite(xy).all(1)
    if ok.sum() < 4:
        return
    x0, y0 = np.nanmin(xy[ok], 0) - 40
    x1, y1 = np.nanmax(xy[ok], 0) + 40
    X0, Y0 = max(0, int(x0)), max(0, int(y0))
    X1, Y1 = min(cv.shape[1], int(x1)), min(cv.shape[0], int(y1))
    if X1 <= X0 or Y1 <= Y0:
        return
    ss = 2
    m8 = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    zn = z / max(np.max(np.abs(z)), 1e-6)            # -1 front .. 1 back
    for i in range(0, 360, 6):
        j = i + 6
        zz = zn[i:j + 1].mean()
        if part == 'back' and zz < 0 or part == 'front' and zz >= 0:
            continue
        if dashed and (i // 6) % 2:
            continue
        seg = xy[i:j + 1]
        if not np.isfinite(seg).all():
            continue
        k = 0.30 + 0.70 * (1 - (zz + 1) / 2)
        pts = np.round((seg - (X0, Y0)) * ss * 16).astype(np.int32)
        cv2.polylines(m8, [pts], False, int(255 * k), max(1, int(width * ss)), cv2.LINE_AA, shift=4)
    m = cv2.resize(m8.astype(np.float32) / 255.0, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    c = col(color)
    reg = cv[Y0:Y1, X0:X1]
    gl = K.gblur(m, 6.0, border='constant') * 0.9 + K.gblur(m, 18.0, border='constant') * 0.6
    if light:
        k = np.clip(m * 0.9 + gl * 0.25 * glow, 0, 1)[..., None] * np.float32(opacity)
        reg[..., :3] = reg[..., :3] * (1 - k) + c * k
    else:
        reg[..., :3] += (m * 1.4 + gl * glow)[..., None] * c * np.float32(opacity)


def orbit_ring(cv, cam, items, phase=0.0, center=(0.0, 0.0, 0.0), radius=360.0, tilt=16.0, roll=-10.0, look='airy',
               ring=True, ring_color=None, mid=None, back_blur=3.5, back_dim=None, back_scale=0.80, size=1.0,
               opacity=1.0, dof=True, yaw_follow=0.0, frost=True, enter=None):
    """Glass tags on a tilted 3D ellipse around `center`, depth-sorted and drawn through core.Cam: back items are
    smaller (back_scale), dimmer (back_dim) and blurred (back_blur px + the camera's DOF). items: list of str,
    (text, thumb_sprite[, thumb_key]) or ready Panels (tag(...)). phase: rotation in turns (animate it: t * 0.06).
    radius: px or (rx, rz); tilt: view elevation (deg, 90 = top view); roll: clockwise ring roll (deg; use the
    opposite sign for a ring 'tilted the other way'). mid(cv) is called between the back and front halves (put
    the hero 3D object there). enter: optional per-item 0..1 build-on (list) for staggered pops.
    Returns [(item_index, screen_xy, depth, front_weight)] in draw order.
        ui.orbit_ring(cv, cam, ['Short-term', ('Siblings', thumb, 'sib')], phase=t * 0.05, look='airy',
                      mid=lambda c: K.draw(c, house_spr, 540, 960))"""
    L = LOOKS[look]
    if back_dim is None:
        back_dim = 0.42 if L.dark else 0.70
    n = len(items)
    panels = []
    for it in items:
        if isinstance(it, Panel):
            panels.append(it)
        elif isinstance(it, str):
            panels.append(tag(it, look=look))
        else:
            txt, th = it[0], it[1]
            key = it[2] if len(it) > 2 else txt
            panels.append(tag(txt, th, look=look, thumb_key=key))
    ang = 2 * math.pi * (np.arange(n) / max(n, 1) + phase) + math.pi / 2
    P, z = _orbit_points(ang, radius, tilt, roll)
    zr = np.max(np.abs(z)) if n else 1.0
    Pw = P + np.asarray(center, np.float64)
    depths = np.array([cam.depth(p) for p in Pw])
    order = np.argsort(-depths)
    rc = ring_color if ring_color is not None else (L.accent_hi if L.dark else L.accent)
    out = []
    if ring:
        _ring_line(cv, cam, center, radius, tilt, roll, rc, 'back', opacity * (0.55 if L.dark else 0.30),
                   light=not L.dark)
    rot_face = (cam.pitch, cam.yaw, cam.roll)
    drew_mid = False
    for idx in order:
        back = float((z[idx] / max(zr, 1e-6) + 1) / 2)          # 0 front .. 1 back
        if not drew_mid and back < 0.5:
            if mid is not None:
                mid(cv)
            if ring:
                _ring_line(cv, cam, center, radius, tilt, roll, rc, 'front', opacity * (0.85 if L.dark else 0.55),
                           light=not L.dark)
            drew_mid = True
        e = 1.0 if enter is None else float(enter[idx])
        if e <= 0:
            continue
        pnl = panels[idx]
        s = (1 + (back_scale - 1) * back) * size * (0.6 + 0.4 * K.EASE['out_back'](min(e, 1.0)))
        op = opacity * (1 + (back_dim - 1) * back) * min(1.0, e * 2)
        bl = back_blur * back ** 1.5
        yaw_extra = -yaw_follow * math.cos(ang[idx])
        rot = (rot_face[0], rot_face[1] + yaw_extra, rot_face[2])
        pnl.plane(cv, cam, Pw[idx], pnl.w * s, rot, opacity=op, dof=dof, blur=bl,
                         frost=None if frost else 0.0, shadow=0.7 * (1 - back * 0.6))
        xy, _ = cam.project(Pw[idx:idx + 1])
        out.append((int(idx), xy[0], float(depths[idx]), 1 - back))
    if not drew_mid:
        if mid is not None:
            mid(cv)
        if ring:
            _ring_line(cv, cam, center, radius, tilt, roll, rc, 'front', opacity * (0.85 if L.dark else 0.55),
                           light=not L.dark)
    return out


# =============================================================================================== self-test
def _save_sheet(path, frames, scale=1.0):
    u8 = [f if f.dtype == np.uint8 else K.to_srgb8(f) for f in frames]
    h = max(f.shape[0] for f in u8)
    row = np.hstack([np.pad(f, ((0, h - f.shape[0]), (0, 0), (0, 0))) for f in u8])
    if scale != 1.0:
        row = cv2.resize(row, (int(row.shape[1] * scale), int(row.shape[0] * scale)), interpolation=cv2.INTER_AREA)
    K.save_png(path, row)
    return path


def _st_heading(cv, txt, y, look_name, size=76, x=540, anchor='ms'):
    L = LOOKS[look_name]
    put_text(cv, x, y, txt, size, 'head', L.text, anchor, max_w=940)


def _st_neon(F, S3):
    lk = 'neon'
    frames = []
    # ---- A: eligibility window, mid-animation, perspective + rack focus
    T = 7.3
    cam = K.Cam(pos=(-40, -10, -1640), yaw=-1.5, pitch=1.5, aperture=28, focus_dist=1600)
    cv = K.background(lk, T, cam)
    win = app_window(look=lk, w=860, h=1250, header='Am I eligible to foster?',
                     icons=('home', 'users', 'chat', 'calendar', 'settings'), active=0)
    face = win.face_at(sweep=(T * 0.35) % 1.0)
    x, y, sw, sh = win.meta['slot']
    rows = [('A spare bedroom', None), ('Time & flexibility', None), ('Single or in a relationship', None),
            ('Rent or own your home', None), ('No previous experience needed', None)]
    ticks = [5.9, 6.65, 7.2, 99, 99]
    for i, (lab, sub) in enumerate(rows):
        r = check_row(lab, sub, w=sw, t=T - ticks[i], look=lk, hl=1.0 if i == 2 else 0.0)
        win.put(face, r, x - ROW_PAD, y + i * 120 - ROW_PAD)
    ring = progress_ring(0.6, 250, 22, lk, sub='eligible')
    win.put(face, ring, x + sw / 2, y + 5 * 120 + 150, anchor=(0.5, 0.5))
    rot = (7, -16, 1.5)
    ctr = (-20, -30, 0)
    win.plane(cv, cam, ctr, 860, rot=rot, face=face)
    # floating toast in front of the window (own frost over the window)
    tst = toast('You could be a great fit', 'Start a conversation today', look=lk, w=600)
    tp = win.world(ctr, 860, rot, 470, 1130, z=-150)
    tst.plane(cv, cam, tp, 600, rot=rot, opacity=0.95)
    # cursor clicking row 3's checkbox
    xy = win.screen(cam, ctr, 860, rot, x + 28 + 30, y + 2 * 120 + 48, z=-60)
    draw_cursor(cv, xy[0] + 8, xy[1] + 10, 'arrow', 76, press=0.8, click=T - 7.2, look=lk)
    K.Particles(140, seed=4, bright=0.8).draw(cv, cam, T)
    frames.append(K.post(cv, lk, T))
    # ---- B: support dock, 3 tiles, focus on the middle one playing footage
    T = 13.4
    cam = K.Cam(pos=(0, 0, -1500), yaw=0.0, aperture=22)
    cv = K.background(lk, T, cam, boost=0.2)
    _st_heading(cv, 'Support is part', 520, lk, 84)
    _st_heading(cv, 'of the role.', 618, lk, 84)
    tiles = [dock_tile('Full Training', 'Preparation & ongoing learning', 'graduation', lk, accent='MAGENTA'),
             dock_tile('Ongoing Support', 'Your supervising social worker', 'chat', lk, accent='HOT_PINK'),
             dock_tile('Weekly Allowance', 'From £447.60 a week per child', 'pound', lk, accent='ORANGE')]
    lay = carousel(3, 1.0, spacing=318, grow=0.12)
    for i, (dx, s, wgt) in enumerate(lay):
        blob = K.radial(560, col(tiles[i].meta['accent']), power=2.0)
        K.draw(cv, blob, 540 + dx, 1080, scale=1.0 + 0.3 * wgt, opacity=0.35 + 0.35 * wgt, mode='add')
    sx, sy, sw, sh, sr = tiles[1].meta['slot']
    media = F.Clip('c04').get(2.2, sw, sh, look=lk) if F else None
    icons3d = [None, None, None]
    if S3 is not None:
        try:
            icons3d = [S3.get('grad_cap', 'night').float_yaw(T), None, S3.get('coin_gbp', 'night').float_yaw(T)]
        except Exception:
            pass
    for i in [0, 2, 1]:
        dx, s, wgt = lay[i]
        f = dock_face(tiles[i], focus=wgt, media=media if i == 1 else None, sweep=0.83 if i == 1 else None,
                      light=0.62 if i == 1 else None, icon_spr=icons3d[i])
        tiles[i].plane(cv, cam, (dx, 1080 - 960, -70 * wgt), 300 * s, rot=(0, -10 * (i - 1), 0), face=f)
    draw_cursor(cv, 600, 1010, 'hand', 84, look=lk)
    K.Particles(140, seed=9, bright=0.8).draw(cv, cam, T)
    frames.append(K.post(cv, lk, T))
    return frames


def _st_amber(F, S3):
    lk = 'amber'
    frames = []
    W_, H_ = 900, 1320
    win = app_window(look=lk, w=W_, h=H_, header='Allowance calculator', sub='Weekly allowance per child',
                     icons=('home', 'pound', 'chart', 'calendar', 'settings'), active=1)
    x, y, sw, sh = win.meta['slot']
    labels = ['0–4', '5–10', '11–14', '15+']
    vals = [447.60, 473.17, 515.52, 554.02]
    for k, (T, sel, grow, act, sv, wk, tot, cur) in enumerate([
            (7.1, 0.7, [1.0, 0.9, 0.55, 0.15], 0.0, 0.38, '20 weeks', 447.60 * 20, 'chip'),
            (12.0, 1.0, [1.0] * 4, 0.0, 1.0, '52 weeks', 23275.20, 'slider')]):
        cam = K.Cam(pos=(0, 0, -1500), aperture=18 if k == 0 else 0)
        cv = K.background(lk, T, cam)
        face = win.face_at(sweep=(T * 0.3) % 1.0)
        cx = x
        for i, lab in enumerate(labels):
            c = chip(lab, sel if i == 0 else 0.0, look=lk)
            win.put(face, c, cx - 24, y - 24)
            cx += c.shape[1] - 48 + 16
        bars = bar_chart(vals, labels, grow=grow, active=act, w=sw, h=440, look=lk)
        win.put(face, bars, x - 32, y + 100 - 32)
        sl = slider(sv, w=sw - 80, look=lk, label=wk, ticks=[(0, '1'), (1, '52')])
        win.put(face, sl, x, y + 548)
        tt = text(money(tot), 104, 'head_black', grad=('#FFE2C4', '#FFB15C'), angle=-90)
        g = K.glow(tt.spr, C['ORANGE'], (6, 18, 40), 0.55)
        pg = (g.shape[1] - tt.spr.shape[1]) // 2
        paste(face, g, win.pad + x - tt.ox - pg, win.pad + y + 900 - tt.oy - pg)
        put_text(face, win.pad + x, win.pad + y + 952, 'Estimated allowance · 52 weeks · one child aged 0–4',
                 28, 'ui_medium', LOOKS[lk].text2, 'ls', max_w=sw)
        put_text(face, win.pad + x, win.pad + y + 996, 'Rates may vary by region and are subject to change.', 28,
                 'body', LOOKS[lk].text3 * 1.4, 'ls', max_w=sw)
        rot = (6, 16, -1.5) if k == 0 else (0, 0, 0)
        ctr = (0, 10, 40) if k == 0 else (0, 0, 120)
        win.plane(cv, cam, ctr, W_, rot=rot, face=face)
        if cur == 'chip':
            xy = win.screen(cam, ctr, W_, rot, x + 60, y + 40, z=-40)
            draw_cursor(cv, xy[0], xy[1], 'hand', 84, press=0.8, click=0.18, look=lk)
        else:
            kx, ky = slider_knob(sv, sw - 80)
            xy = win.screen(cam, ctr, W_, rot, x + kx, y + 548 + ky, z=-20)
            draw_cursor(cv, xy[0] + 4, xy[1] + 6, 'hand', 84, press=0.6, look=lk)
        K.Particles(120, seed=3, bright=0.8, colors=[C['AMBER'], C['ORANGE'], C['PEACH']]).draw(cv, cam, T)
        frames.append(K.post(cv, lk, T))
    return frames


def _st_airy(F, S3):
    lk = 'airy'
    frames = []
    # ---- A: orbit ring of image tags around a 3D heart
    T = 17.2
    cam = K.Cam.orbit((0, 60, 0), 1500, yaw=-6, pitch=7, aperture=18, focus_dist=1260)
    cv = K.background(lk, T, cam)
    _st_heading(cv, 'Different children need', 470, lk, 64)
    _st_heading(cv, 'different kinds of care', 550, lk, 64)
    names = ['03-short-term-everyday-connection.webp', '04-long-term-family-belonging.webp',
             '05-emergency-a-calm-welcome.webp', '06-respite-outdoor-play.webp',
             '07-siblings-growing-together.webp', '08-teenagers-time-to-talk.webp']
    labs = ['Short-term', 'Long-term', 'Emergency', 'Respite', 'Siblings', 'Teenagers']
    items = []
    for nm, lab in zip(names, labs):
        th = F.still(nm, 140, 140, look='airy', center=(0.5, 0.4)) if F else None
        items.append((lab, th, nm) if th is not None else lab)
    heart = None
    if S3 is not None:
        try:
            heart = S3.get('heart', 'day').float_yaw(T)
        except Exception:
            heart = None

    def mid(c):
        g = K.radial(700, C['HOT_PINK'], power=2.2)
        xy, _ = cam.project(np.array([[0, 60, 0]]))
        K.draw(c, g, xy[0][0], xy[0][1], opacity=0.25, mode='over')
        if heart is not None:
            K.draw(c, heart, xy[0][0], xy[0][1], scale=0.44)
        else:
            K.draw(c, icon('heart', 240, 'MAGENTA', fill_a=1.0, glow=0.4), xy[0][0], xy[0][1])
    orbit_ring(cv, cam, items, phase=T * 0.05, center=(0, 60, 0), radius=(345, 430), tilt=26, roll=9, look=lk,
               mid=mid, size=0.86)
    K.Particles(90, seed=2, bright=0.6, colors=[C['WHITE'], C['PEACH'], C['AMBER']]).draw(cv, cam, T)
    frames.append(K.post(cv, lk, T))
    # ---- B: trust pills, badge, CTA, steps
    T = 21.4
    cam = K.Cam(aperture=0)
    cv = K.background(lk, T, cam)
    _st_heading(cv, 'Nurture. Develop. Grow.', 330, lk, 76)
    st = steps(2.0, 5, 820, lk)
    place(cv, st, 540, 480)
    if S3 is not None:
        try:
            sh_ = S3.get('shield_check', 'day').float_yaw(T)
            K.draw(cv, sh_, 540, 720, scale=0.30)
        except Exception:
            pass
    pills = ['Independent Fostering Agency', 'Cultural Matching Specialists', 'Rated Good by Ofsted']
    for i, tx in enumerate(pills):
        p = tag(tx, look=lk, icon_name='check', accent='LEAF', size=36, h=96)
        e = 1.0 if i < 2 else 0.7
        p.draw(cv, 540, 900 + i * 124 + 30 * (1 - e), scale=0.92 + 0.08 * e, opacity=e)
    b = badge('Rated Good by Ofsted', 'Inspected May 2025', look=lk)
    b.draw(cv, 540, 1290)
    bt = button('Start your enquiry', hover=1.0, press=0.4, ripple=0.16, ripple_at=(0.62, 0.55), look=lk)
    place(cv, bt, 540, 1450)
    draw_cursor(cv, 620, 1470, 'hand', 84, press=0.4, look=lk)
    put_text(cv, 540, 1575, '0161 241 1332  ·  organicfostering.co.uk', 32, 'ui_medium', LOOKS[lk].text2, 'ms')
    frames.append(K.post(cv, lk, T))
    return frames


def _st_components(look_name):
    """Every widget state on one canvas (for the API reference)."""
    L = LOOKS[look_name]
    cv = K.background(look_name, 2.0)
    for i, (hv, pr, rp) in enumerate([(0, 0, None), (1, 0, None), (1, 1, 0.08), (0.6, 0.3, 0.32)]):
        place(cv, button('Start your enquiry', hover=hv, press=pr, ripple=rp, ripple_at=(0.75, 0.5),
                         look=look_name, h=96, size=36), 290 + (i % 2) * 520, 110 + (i // 2) * 150)
    for i, t in enumerate([-1, 0.06, 0.12, 0.17, 0.24, 0.34, 0.5, 1.0]):
        place(cv, checkbox(t, 60, look_name), 90 + i * 128, 430)
        put_text(cv, 90 + i * 128, 500, '%.2fs' % t if t >= 0 else 'empty', 22, 'ui_medium', L.text2, 'ms')
    for i, p in enumerate([0, 0.35, 0.7, 1.0]):
        place(cv, toggle(p, look=look_name), 120 + i * 170, 590)
    place(cv, progress_ring(0.66, 200, 18, look_name), 900, 650)
    xx = 60
    for i, (tx, s) in enumerate([('0–4', 1), ('5–10', 0), ('11–14', 0.5), ('15+', 0)]):
        c = chip(tx, s, look=look_name)
        place(cv, c, xx, 720, anchor=(0, 0.5))
        xx += c.shape[1] - 32
    place(cv, slider(0.62, 640, look_name, label='32 weeks'), 420, 880)
    place(cv, search_bar('Foster carer support', n=13.6, t=0, w=680, look=look_name), 420, 1050)
    place(cv, steps(2.4, 5, 760, look_name, labels=None), 450, 1200)
    for i, (kind, pr, ck) in enumerate([('arrow', 0, None), ('arrow', 1, 0.14), ('hand', 0, None), ('hand', 1, 0.3)]):
        draw_cursor(cv, 90 + i * 110, 1340, kind, 72, press=pr, click=ck, look=look_name)
    toast('Check complete', 'All five boxes ticked', look=look_name, w=500).draw(cv, 790, 1380)
    for i, nm in enumerate(ICONS[:24]):
        place(cv, icon(nm, 64, L.text, stroke=2.0, glow=0.5 if L.dark else 0.0,
                       glow_color=L.accent_hi), 80 + (i % 8) * 132, 1560 + (i // 8) * 116)
    return K.post(cv, look_name, 2.0)


def _st_motion():
    """Filmstrip of the animated widgets over time (rows: checklist tick, chip select, toggle, button click,
    progress ring, cursor press + click ring)."""
    lk = 'neon'
    times = [0.0, 0.06, 0.12, 0.18, 0.26, 0.36, 0.5, 0.8]
    cw, rh = 300, 170
    bg = K.background(lk, 1.0)
    cv = np.ascontiguousarray(cv2.resize(bg, (cw * len(times), rh * 6 + 40), interpolation=cv2.INTER_AREA))
    cv[..., 3] = 1.0
    for j, t in enumerate(times):
        x = j * cw + cw / 2
        put_text(cv, x, 34, '%.2f s' % t, 26, 'ui_medium', LOOKS[lk].text2, 'ms')
        place(cv, check_row('Spare room', w=250, t=t, look=lk, box=52, label_size=34), x, 40 + rh * 0.5)
        place(cv, chip('0\u20134', K.ramp(t, 0.0, 0.35, 'out_cubic'), look=lk, origin=(0.3, 0.5)), x,
              40 + rh * 1.5, scale=1 + 0.12 * K.impulse(t, 0.0, 9.0) * math.sin(t * 30))
        place(cv, toggle(K.spring(t, 2.6, 0.45), look=lk), x, 40 + rh * 2.5)
        place(cv, button('Enquire', hover=1.0, press=K.impulse(t, 0.0, 9.0), ripple=t, ripple_at=(0.4, 0.5),
                         look=lk, h=88, size=34), x, 40 + rh * 3.5, scale=0.9)
        place(cv, progress_ring(K.ramp(t, 0.0, 0.8, 'out_cubic'), 130, 14, lk, label_size=34), x, 40 + rh * 4.5)
        draw_cursor(cv, x, 40 + rh * 5.5, 'arrow', 64, press=K.impulse(t, 0.0, 9.0), click=t, look=lk)
    return K.post(cv, lk, 1.0)


def selftest():
    import time
    os.makedirs(K.SELFTEST, exist_ok=True)
    try:
        import footage as F
    except Exception:
        F = None
    try:
        import sprites3d as S3
    except Exception:
        S3 = None
    t0 = time.time()
    out = []
    for nm, fn in (('neon', _st_neon), ('amber', _st_amber), ('airy', _st_airy)):
        t = time.time()
        fr = fn(F, S3)
        p = _save_sheet(os.path.join(K.SELFTEST, 'ui_%s.png' % nm), fr)
        for i, f in enumerate(fr):
            K.save_png(os.path.join(K.SELFTEST, 'ui_%s_%d.png' % (nm, i)), f)
        out.append(p)
        print('ui selftest %-6s %.1f s -> %s' % (nm, time.time() - t, p))
    comps = [_st_components('neon'), _st_components('airy')]
    out.append(_save_sheet(os.path.join(K.SELFTEST, 'ui_components.png'), comps))
    out.append(K.save_png(os.path.join(K.SELFTEST, 'ui_motion.png'), _st_motion()))
    ic = K.new_canvas(LOOKS['neon'].tint_bot, w=8 * 136, h=((len(ICONS) + 7) // 8) * 150)
    for i, nm in enumerate(ICONS):
        x, y = (i % 8) * 136 + 68, (i // 8) * 150 + 62
        place(ic, icon(nm, 72, 'IVORY', stroke=2.0), x, y)
        put_text(ic, x, y + 70, nm, 22, 'ui_medium', LOOKS['neon'].text2, 'ms')
    out.append(K.save_png(os.path.join(K.SELFTEST, 'ui_icons.png'), ic))
    # steady-state cost of one animated window frame (caches warm)
    win = app_window(look='neon', w=880, h=1250)
    x, y, sw, sh = win.meta['slot']
    cam = K.Cam(aperture=20)
    cv = K.background('neon', 1.0, cam)
    t = time.time()
    for k in range(5):
        f = win.face_at(sweep=0.1 * k)
        for i in range(5):
            win.put(f, check_row('A spare bedroom', w=sw, t=0.05 * k - 0.05 * i, look='neon'), x - ROW_PAD,
                    y + i * 120 - ROW_PAD)
        win.plane(cv, cam, (0, 0, 0), 880, rot=(6, -15, 1), face=f)
    print('ui steady-state window frame: %.0f ms' % ((time.time() - t) / 5 * 1000))
    print('ui selftest done in %.1f s' % (time.time() - t0))
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        print(__doc__)
