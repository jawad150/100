"""type3d.py: cinematic typography for the Organic Fostering reels: 3D extrusion with bevel lighting, deep glow,
light sweeps, neon, brand gradient, ink-on-ivory, glass pills, footage-in-letters with zoom-throughs, per-glyph
kinetic animators, 3D orbit rings and slot/odometer counters.

Sprites follow core's convention: premultiplied LINEAR float32 RGBA. Text is laid out with real kerning (raqm /
GPOS, ligatures off), rasterised 2x (3x below 56 px) with sub-pixel glyph positions and area-downsampled; every
static part (masks, bevel lighting, extrusion, glows) is cached in a byte-budget LRU (env FOSTER_TYPE_CACHE_MB,
default 400), so per-frame work is warping cached layers (+ one cheap band for a light sweep). Hero words build
in ~0.3-1.2 s once per process (call them in prewarm()); draws cost ~2-25 ms. Import has no side effects.
Self-test: python3 type3d.py selftest  (writes workspace3/out/selftest/type3d_*.png)

UNITS, FRAMES, COLOURS
    A "block" is laid-out text. Block coords = 1x canvas px, origin at the top-left of the TEXT BOX: x spans the
    ink of the widest line, y spans cap-top of line 1 to the baseline of the last line. So anchor (.5, .5)
    centres caps optically; descenders, glows, extrusions and shadows extend outside the box.
    Style lengths are in em (multiples of the font px) so a style scales with px.
    Colour spec: 'MAGENTA' (core.C name) | '#B7006E' (sRGB hex) | (r, g, b) linear | ('ORANGE', 1.8) = x gain.
    Gradient spec: ('MAGENTA', 'ORANGE') or ((0, c0), (0.6, c1), (1, c2)); angle uses core's convention
    (degrees CCW from +x: 0 = left->right, -90 = top->bottom, 35 = the brand sunset diagonal).

FONTS / LAYOUT
    Aliases: 'display' Nunito-Black, 'display2' Nunito-ExtraBold, 'display_bold' Nunito-Bold, 'ui' Poppins-
    SemiBold, 'ui_bold' Poppins-Bold, 'body' Poppins-Regular, 'medium' Poppins-Medium, 'hand' Caveat-Bold, or
    any ttf basename in workspace3/fonts. '\u2192' (->) and '\u2713' (check) are drawn as vector glyphs matched
    to the font's stem weight (the brand fonts lack them).
    font(name, px) -> cached PIL font.  measure(text, style, **kw) -> (w, h) text box, no rasterising.
    layout(text, font, px, tracking=0, line_height=1.08, align='center'|'left'|'right', max_width=0 (px, wraps
    words)) -> Layout: .w .h .cap .ink .lines [(x0, x1, baseline)] .glyphs [_G(ch, i, line, x, base, adv, ink)]

STYLES  (frozen dataclass Style; presets in STYLES; style(name_or_Style, **overrides); st.but(**overrides))
    'flat'        plain face (any colour / gradient fill).
    'ui', 'ui_ink' Poppins SemiBold 40 px IVORY / INK (ui_ink thickens coverage for dark-on-light) - fine print
                  stays crisp down to 28 px.
    'extrude3d'   real-looking 3D: perspective-converging extrusion whose sides are shaded from the contour
                  normals (key light, viewer-facing ratio, depth gradient, coloured far-edge rim light), a bevelled
                  front face from SDF normals (Lambert key, grazing Blinn-Phong spec, coloured rim light, chrome
                  environment banding), face gradient, inner shadow, drop shadow, soft glow. side=None derives the
                  sides from the face colour (plum-tinted), so gradient faces ('MAGENTA'->'ORANGE') just work.
    'chrome'      white chrome: sky / dark horizon line / peach ground reflection, orange rim, plum sides.
    'gold'        amber-gold chrome extrusion (reel 2 hero and totals).
    'deep_glow'   white-hot core, coloured inner bleed, 5-radius wide outer glow. Add scrim=0.75-0.85 for a dark
                  soft backing over bright footage (legibility).
    'neon'        glowing tube outline with a white-hot centre line, faint glass fill and halo (neon_flicker(t)).
    'gradient'    brand gradient fill MAGENTA -> HOT_PINK -> ORANGE at 35 deg, glossy soft bevel, shadow, glow.
    'ink_soft'    INK on ivory: soft long shadow, subtle plum 3D lip, bevel highlight, slight white bloom.
    'glass_pill' / 'glass_pill_light'  text in a frosted capsule (frost, dark veil / white body, top sheen,
                  rim light, tinted bottom glow, soft shadow). pill_box = capsule rect in block coords.
    Style fields (lengths in em): font px tracking line_height align max_width(px) ss gamma | face fill
    fill_angle fill_gain | bevel profile('chamfer'|'round'|'soft') light ambient spec shininess spec_color
    spec_light rim rim_color rim_dir env env_horizon env_ground inner_shadow(_color,_size,_offset)
    inner_glow(_color,_size) | depth angle(deg the extrusion recedes toward, CCW from +x; -64 = down, a bit right)
    persp side side_gain side_tint side_falloff side_key side_ambient side_rim edge_rim | stroke stroke_color
    tube tube_color tube_core tube_fill | glow glow_color glow_radii glow_weights glow_src('face'|'all') |
    shadow shadow_color shadow_offset shadow_blur long_shadow(_len,_angle,_color,_blur) scrim scrim_color
    scrim_size | pill pill_dark pill_color pill_pad pill_radius pill_rim pill_frost pill_shadow
    pill_shadow_color pill_tint pill_tint_amount.  Use tuples (not numpy arrays) for colours inside a Style.

RENDER + DRAW
    ts = render(text, style='flat', frame=None, **overrides) -> TextSprite (cached on text + Style + frame)
        ts.w, ts.h (text box), ts.layout, ts.style, ts.layers [Layer(spr, box, res, mode, frost, part)] drawn in
        order pill -> glow -> back -> front -> sweep; ts.bounds() union box; ts.pill_box.
        ts.draw(cv, x, y, anchor=(.5, .5), scale=1, rot=0, opacity=1, blur=0, sweep=None, sweep_kw=None,
                parts=None) -> bbox.  anchor is relative to the TEXT BOX ((0, .5) = left-centre, also 'left',
                'right', 'top', 'baseline', 'tl', 'bl'); scale may be (sx, sy); rot degrees clockwise;
                scale 1 + rot 0 snaps to whole px (razor sharp).
        ts.draw_quad(cv, quad, ...)   quad = screen corners [TL, TR, BR, BL] of the text box (perspective).
        ts.draw_plane(cv, cam, center, rot=(rx, ry, rz), scale=1, anchor=(.5, .5), dof=True, sweep=None, ...)
            3D plane via core.draw_plane (DOF / near clipping); scale = world units per text px.
        ts.sprite / ts.sprite_anchor(anchor) -> one merged sprite + the core.draw anchor fraction for it
            (to bake text into UI cards); ts.merged() -> that as a Layer.
    light_sweep(ts, u, width=0.09, angle=-32, color='WHITE', strength=1.25, face=0.5, bevel=1.6, halo=0.22)
        -> TextSprite with one additive layer aligned to ts; or ts.draw(..., sweep=u, sweep_kw={...}).
        u in [0, 1]: the band enters at u=0 and has fully left at u=1; angle = direction it travels (deg CCW
        from +x, so -32 runs left->right, slightly down: a diagonal band). Masked to face + bevel; face/bevel
        masks are cached so a frame costs one exp() over the face (~5-12 ms for a hero word).
        e.g. you.draw(cv, 540, 900, sweep=K.ramp(t, 1.0, 1.9, 'inout_sine'))

KINETIC (per-glyph; glyph sprites are rendered in the block's frame so gradients and sweeps stay continuous,
         and a settled block is drawn from the exact whole-block sprite)
    g = Glyphs('A SAFE HOME.', 'deep_glow', px=130, scrim=0.8)
    g.rise(cv, t, x, y, t0=0, stagger=0.035, dur=0.7, dist=0.45, blur=10, scale0=0.9, order='ltr'|'rtl'|
           'center'|'random')                                  per-glyph rise + blur-in + scale
    g.slam(cv, t, x, y, t0=0, s0=1.6, dur=0.45, freq=3.2, damping=0.45, stagger=0, smear=True)
                                                               1.6 -> 1 spring overshoot + exact motion smear
    g.typewriter(cv, t, x, y, t0=0, cps=16, caret=True)        pop-on chars + blinking caret
    g.wipe(cv, t, x, y, t0=0, dur=0.6, angle=0, soft=0.12, edge=1.0)   soft mask wipe + bright leading edge
    g.track(cv, t, x, y, t0=0, dur=0.9, amount=0.45, blur=8)   tracking expand: spread glyphs settle in
    g.flip(cv, t, x, y, t0=0, stagger=0.05, dur=0.6, from_angle=-100)  3D rotateX per glyph (draw_quad)
    g.scramble(cv, t, x, y, t0=0, dur=0.7, stagger=0.04, rate=22, charset=None)  decode effect
    Any animator also takes out_t0=, out_dur=0.4, out_dist=0.3, out_blur=8 (lift, blur and fade out).
    Draw kwargs for all: anchor=(.5, .5), scale=1, rot=0, opacity=1, blur=0, tilt=(rx, ry, rz) (3D tilt of the
    whole block, perspective focal=1600), sweep=None|u, sweep_kw, mblur=0|n|'auto' (+ mspan seconds: averaged
    sub-samples = motion smear on top of render_frame's own blur).
    Low level: states, blk = g.anim('rise', t, **kw); g.render(cv, states, x, y, block=blk, **draw_kw);
    GlyphState(dx, dy, z, sx, sy, rot, rx, ry, opacity, blur, alt, sweep); g.boxes(); g.glyph(k); g.block.

ORBIT TEXT
    ot = OrbitText('NURTURE \u2022 DEVELOP \u2022 GROW \u2022 ', 'flat', px=56, radius=380, tilt=14, roll=-8,
                   fill=True, **style_overrides)   # tilt: ring plane tipped toward camera (deg); fill=True
        repeats the text round the ring; fill='IVORY' (a colour) sets the text colour and repeats; repeat=False
        draws it once.
    ot.draw(cv, cam, center=(0, 0, 0), t=t, spin=20, phase=0, part='all'|'back'|'front', back_opacity=0.35,
            back_blur=5, dof=True, opacity=1, scale=1, sweep=None)
        glyphs stand on a 3D circle facing outward, depth-sorted; the back half is seen from behind (mirrored),
        dimmer and blurred. Draw part='back', then your 3D object, then part='front'.  ~1 ms per glyph.
    ot.add_to_scene(sc, center, t, spin=...) registers each glyph in a core.Scene for full depth interleaving.

COUNTER (tabular figures; the style's glow is applied once to the composed number)
    cnt = Counter('gold', px=150, prefix='\u00a3', suffix='', decimals=2, sep=',', point='.', blur_cap=0.12)
        blur_cap = max per-digit motion blur (sigma, fraction of the cap height): 0.12 keeps spinning digits legible
        as gold streaks; 0.26 = the old physically flat 'barcode' look at full speed.
    cnt.draw(cv, value, x, y, anchor=(.5, .5), scale=1, vel=0)  odometer roll; vel = value units per second
        (e.g. track.vel(t)) gives per-digit vertical motion blur; leading digits grow in smoothly.
    cnt.slot(cv, t, 23275.20, x, y, t0=0, dur=1.4, stagger=0.09, spins=2, order='rtl')  slot reels land with a
        small overshoot.  cnt.sprite(value, vel) / cnt.slot_sprite(...) -> TextSprite (e.g. for draw_plane);
        cnt.width(value).  ~20-90 ms per frame while rolling, ~20 ms settled.
    Tip: K.Track([(0, 0, 'out_expo'), (2.0, 23275.20)]) - a key's ease applies from that key to the next.

VIDEO IN TYPE
    vt = VideoType('NURTURE', px=200, tracking=-0.01, look='dark'|'light', rim_style=None, back_style=None)
    vt.draw(cv, footage, x, y, anchor=(.5, .5), scale=1, rot=0, opacity=1, lock='screen'|'text', rim=1, back=1,
            sweep=None)   footage seen through the letters, with a bevel/inner-shadow rim overlay and an
        extruded back layer. lock='screen': footage is a canvas-sized sprite (clip.get(t, 1080, 1920)), fixed
        on screen, so a zoom-through ends exactly on that full-frame footage; lock='text': any sprite,
        cover-fitted to the text box, moving with it.
    vt.mask_canvas(x, y, anchor, scale, rot) -> (H, W) alpha of the letters (for custom composites).
    vt.zoom_point(char='U', index=None, kind='stroke'|'counter') -> (bx, by) block coords: the thickest point of
        that letter's ink (zoom INTO the footage) or the centre of its counter / bowl (zoom THROUGH the hole).
    vt.zoom(u, point, x, y, anchor=(.5, .5), s0=1, s1=40, target=(540, 960), ease='in_expo') -> dict(x, y,
        anchor, scale): splat into vt.draw(cv, footage, **z). Scale grows exponentially while the point glides
        to the target; pair it with K.zoom_blur for the transition.

EXAMPLES
    import core as K, type3d as T
    cv = K.background('neon', t)
    T.render('Could', 'flat', px=120, glow=0.5, glow_color=('MAGENTA', 2)).draw(cv, 540, 700)
    you = T.render('YOU', 'extrude3d', px=240, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, fill_gain=1.2)
    you.draw(cv, 540, 900, scale=K.lerp(1.3, 1, K.ramp(t, 0, .5)), sweep=K.ramp(t, .6, 1.4, 'inout_sine'))
    T.Glyphs('Foster Carer?', 'deep_glow', px=120, glow_color=('ORANGE', 2.4)).rise(cv, t, 540, 1100, t0=0.8)
    T.render('Start your enquiry \u2192', 'glass_pill', px=44).draw(cv, 540, 1450)
    trk = K.Track([(0, 0, 'out_expo'), (2, 447.60)]); T.Counter('gold', px=150).draw(cv, trk(t), 540, 960,
                                                                                    vel=trk.vel(t))
"""
import collections
import dataclasses
import functools
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import core as K

__all__ = ['Style', 'STYLES', 'style', 'col', 'font', 'layout', 'measure', 'render', 'TextSprite', 'Layer',
           'light_sweep', 'Glyphs', 'GlyphState', 'OrbitText', 'Counter', 'VideoType', 'neon_flicker']

FONT_ALIAS = {'display': 'Nunito-Black', 'display2': 'Nunito-ExtraBold', 'display_bold': 'Nunito-Bold',
              'ui': 'Poppins-SemiBold', 'ui_bold': 'Poppins-Bold', 'body': 'Poppins-Regular',
              'medium': 'Poppins-Medium', 'hand': 'Caveat-Bold'}
_REF = 1000.0                    # reference size for metrics (font units for 1000-upm fonts)
_FEAT = ['-liga', '-calt', '-clig', '-dlig']
_CUSTOM = {'→': 0.92, '✓': 0.82}      # vector glyphs: advance in em


# =============================================================================================== colour
def col(c):
    """Colour spec -> linear float32[3]: 'MAGENTA' | '#B7006E' | (r, g, b) linear | ('ORANGE', gain)."""
    if c is None:
        return None
    if isinstance(c, str):
        return K.hexlin(c) if c.startswith('#') else np.asarray(K.C[c.upper()], np.float32)
    if isinstance(c, (tuple, list)) and len(c) == 2 and not isinstance(c[0], (int, float, np.floating)) \
            and isinstance(c[1], (int, float, np.floating)):
        return col(c[0]) * np.float32(c[1])
    if isinstance(c, (tuple, list)) and len(c) == 1:
        return col(c[0])
    if isinstance(c, (tuple, list)) and len(c) >= 2 and not isinstance(c[0], (int, float, np.floating)):
        st = _stops(c)                                       # gradient spec used as a colour: its first stop
        return st[0][1] if st else col(c[0])
    return np.asarray(c, np.float32).reshape(-1)[:3].astype(np.float32)


def _stops(spec):
    """Gradient spec -> [(pos, rgb), ...], or None when spec is a single colour."""
    if not isinstance(spec, (tuple, list)) or len(spec) < 2:
        return None
    if isinstance(spec[0], (int, float, np.floating)):
        return None                                          # (r, g, b)
    if len(spec) == 2 and isinstance(spec[1], (int, float, np.floating)):
        return None                                          # (colour, gain)
    out = []
    n = len(spec)
    for i, s in enumerate(spec):
        if isinstance(s, (tuple, list)) and len(s) == 2 and isinstance(s[0], (int, float, np.floating)) \
                and not isinstance(s[1], (int, float, np.floating)):
            out.append((float(s[0]), col(s[1])))
        else:
            out.append((i / (n - 1), col(s)))
    return out


def _hashable(v):
    if isinstance(v, np.ndarray):
        return tuple(float(x) for x in v.reshape(-1))
    if isinstance(v, list):
        return tuple(_hashable(x) for x in v)
    if isinstance(v, tuple):
        return tuple(_hashable(x) for x in v)
    return v


def _lut(stops, n=1024):
    return K._ramp_lut([(p, c) for p, c in stops], n)


def _fill_map(spec, angle, X, Y, fw, fh):
    """Colour map (h, w, 3) of a fill spec at frame coords X (w,), Y (h,) over a frame fw x fh."""
    st = _stops(spec)
    if st is None:
        c = col(spec)
        return np.broadcast_to(c, (len(Y), len(X), 3)).astype(np.float32)
    lut = _lut(st)
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    ext = abs(fw / 2 * dx) + abs(fh / 2 * dy)
    u = ((X[None, :] - fw / 2) * dx + (Y[:, None] - fh / 2) * dy) / max(ext, 1e-6)
    idx = np.clip((u + 1) * 0.5 * (len(lut) - 1), 0, len(lut) - 1).astype(np.int32)
    return lut[idx]


# =============================================================================================== fonts / layout
def font_name(name):
    return FONT_ALIAS.get(name, name)


@functools.lru_cache(maxsize=512)
def font(name, px):
    """Cached PIL FreeType font (raqm layout: kerning on, ligatures off). px may be fractional."""
    return ImageFont.truetype(K.font_path(font_name(name)), float(px), layout_engine=ImageFont.Layout.RAQM)


@functools.lru_cache(maxsize=32)
def _fmetrics(name):
    from fontTools.ttLib import TTFont
    tt = TTFont(K.font_path(font_name(name)), lazy=True)
    upm = tt['head'].unitsPerEm
    s = _REF / upm
    os2 = tt['OS/2']
    cap = (getattr(os2, 'sCapHeight', 0) or 0.7 * upm) * s
    xh = (getattr(os2, 'sxHeight', 0) or 0.5 * upm) * s
    cmap = set(tt.getBestCmap().keys())
    f = font(name, _REF)
    stem = f.getbbox('l', anchor='ls')
    return {'cap': float(cap), 'xh': float(xh), 'asc': tt['hhea'].ascent * s, 'desc': -tt['hhea'].descent * s,
            'cmap': cmap, 'stem': float(stem[2] - stem[0])}


@functools.lru_cache(maxsize=8192)
def _gmet(name, ch):
    """(advance, (x0, y0, x1, y1) ink box rel. to pen/baseline, y down) at the 1000 px reference."""
    m = _fmetrics(name)
    if ch in _CUSTOM and ord(ch) not in m['cmap']:
        adv = _CUSTOM[ch] * _REF
        if ch == '→':
            st = m['stem'] * 0.9
            return adv, (0.08 * _REF - st / 2, -m['cap'] * 0.5 - 0.3 * _REF, adv - 0.06 * _REF + st / 2,
                         -m['cap'] * 0.5 + 0.3 * _REF)
        return adv, (0.06 * _REF, -m['cap'] * 0.95, adv - 0.04 * _REF, 0.02 * _REF)
    f = font(name, _REF)
    adv = f.getlength(ch, features=_FEAT)
    if ch.isspace():
        return adv, None
    b = f.getbbox(ch, anchor='ls', features=_FEAT)
    if b[2] <= b[0]:
        return adv, None
    return adv, (float(b[0]), float(b[1]), float(b[2]), float(b[3]))


@functools.lru_cache(maxsize=4096)
def _pen(name, line):
    """Kerned pen x of every char of a line at the reference size (custom glyphs measured separately)."""
    m = _fmetrics(name)
    f = font(name, _REF)
    sub = ''.join(' ' if (c in _CUSTOM and ord(c) not in m['cmap']) else c for c in line)
    nb = f.getlength(' ', features=_FEAT)
    pos = []
    extra = 0.0
    for i, c in enumerate(line):
        pre = f.getlength(sub[:i + 1], features=_FEAT) - f.getlength(sub[i], features=_FEAT)
        pos.append(pre + extra)
        if c in _CUSTOM and ord(c) not in m['cmap']:
            extra += _CUSTOM[c] * _REF - nb
    return tuple(pos)


class _G:
    __slots__ = ('ch', 'i', 'line', 'x', 'base', 'adv', 'ink')

    def __init__(self, ch, i, line, x, base, adv, ink):
        self.ch, self.i, self.line, self.x, self.base, self.adv, self.ink = ch, i, line, x, base, adv, ink

    def __repr__(self):
        return f'_G({self.ch!r}, x={self.x:.1f}, base={self.base:.1f})'


class Layout:
    """Kerned multi-line layout in block coords (see module docstring)."""

    def __init__(self, text, fnt, px, tracking=0.0, line_height=1.08, align='center', max_width=0.0):
        self.text, self.font, self.px = text, fnt, float(px)
        self.tracking, self.line_height, self.align = tracking, line_height, align
        m = _fmetrics(fnt)
        s = self.px / _REF
        self.cap = m['cap'] * s
        lines = []
        for para in text.split('\n'):
            lines.extend(self._wrap(para, max_width) if max_width and max_width > 0 else [para])
        lh = line_height * self.px
        rows = []
        for li, ln in enumerate(lines):
            pens = _pen(fnt, ln) if ln else ()
            gl = []
            for ci, ch in enumerate(ln):
                adv, ink = _gmet(fnt, ch)
                x = pens[ci] * s + ci * tracking * self.px
                gl.append([ch, x, adv * s, None if ink is None else tuple(v * s for v in ink)])
            inks = [(g[1] + g[3][0], g[1] + g[3][2]) for g in gl if g[3] is not None]
            if inks:
                x0, x1 = min(a for a, _ in inks), max(b for _, b in inks)
            else:
                x0 = x1 = 0.0
            rows.append((gl, x0, x1))
        wmax = max([r[2] - r[1] for r in rows] + [1.0])
        self.w = float(wmax)
        self.h = float(self.cap + (len(rows) - 1) * lh)
        self.lines = []
        self.glyphs = []
        k = 0
        for li, (gl, x0, x1) in enumerate(rows):
            base = self.cap + li * lh
            lw = x1 - x0
            off = {'left': 0.0, 'right': wmax - lw}.get(align, (wmax - lw) / 2) - x0
            for ch, x, adv, ink in gl:
                inkb = None if ink is None else (x + off + ink[0], base + ink[1], x + off + ink[2], base + ink[3])
                self.glyphs.append(_G(ch, k, li, x + off, base, adv, inkb))
                k += 1
            self.lines.append((x0 + off, x1 + off, base))
        boxes = [g.ink for g in self.glyphs if g.ink is not None]
        if boxes:
            self.ink = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes),
                        max(b[3] for b in boxes))
        else:
            self.ink = (0.0, 0.0, self.w, self.h)

    def _wrap(self, para, max_width):
        words = para.split(' ')
        out, cur = [], ''
        for wd in words:
            trial = wd if not cur else cur + ' ' + wd
            if cur and self._width(trial) > max_width:
                out.append(cur)
                cur = wd
            else:
                cur = trial
        out.append(cur)
        return out

    def _width(self, line):
        s = self.px / _REF
        pens = _pen(self.font, line)
        x1 = 0.0
        for ci, ch in enumerate(line):
            adv, ink = _gmet(self.font, ch)
            if ink is not None:
                x1 = max(x1, (pens[ci] + ink[2]) * s + ci * self.tracking * self.px)
        return x1

    def text_width(self):
        return self.w

    def line_of(self, y):
        lh = self.line_height * self.px
        return int(np.clip(round((y - self.cap) / max(lh, 1e-6)), 0, len(self.lines) - 1))


@functools.lru_cache(maxsize=2048)
def layout(text, font='display', px=160, tracking=0.0, line_height=1.08, align='center', max_width=0.0):
    """Cached Layout (see module docstring)."""
    return Layout(text, font, px, tracking, line_height, align, max_width)


def _draw_custom(d, ch, X, Y, px, fname):
    """Vector arrow / check glyph with round caps, stroke matched to the font's stem."""
    m = _fmetrics(fname)
    s = px / _REF
    st = m['stem'] * s * 0.9
    cy = Y - m['cap'] * s * 0.5
    if ch == '→':
        adv = _CUSTOM[ch] * px
        x0, x1 = X + 0.08 * px, X + adv - 0.06 * px
        hw = 0.3 * px
        segs = [((x0, cy), (x1, cy)), ((x1 - hw, cy - hw), (x1, cy)), ((x1 - hw, cy + hw), (x1, cy))]
    else:
        adv = _CUSTOM[ch] * px
        segs = [((X + 0.1 * px, Y - m['cap'] * s * 0.45), (X + 0.33 * px, Y - 0.05 * px)),
                ((X + 0.33 * px, Y - 0.05 * px), (X + adv - 0.08 * px, Y - m['cap'] * s * 0.92))]
    for (ax, ay), (bx, by) in segs:
        d.line([(ax, ay), (bx, by)], fill=255, width=max(1, int(round(st))))
        for (px_, py_) in ((ax, ay), (bx, by)):
            d.ellipse([px_ - st / 2, py_ - st / 2, px_ + st / 2, py_ + st / 2], fill=255)


def _raster(lay, ss, region, only=None):
    """Glyph coverage (h*ss, w*ss) float32 of a layout over an integer block-coords region."""
    rx0, ry0, rx1, ry1 = region
    W_, H_ = (rx1 - rx0) * ss, (ry1 - ry0) * ss
    im = Image.new('L', (int(W_), int(H_)), 0)
    d = ImageDraw.Draw(im)
    f = font(lay.font, lay.px * ss)
    cm = _fmetrics(lay.font)['cmap']
    for g in lay.glyphs:
        if g.ink is None or (only is not None and g.i not in only):
            continue
        X, Y = (g.x - rx0) * ss, (g.base - ry0) * ss
        if g.ch in _CUSTOM and ord(g.ch) not in cm:
            _draw_custom(d, g.ch, X, Y, lay.px * ss, lay.font)
        else:
            d.text((X, Y), g.ch, font=f, fill=255, anchor='ls', features=_FEAT)
    return np.asarray(im, np.float32) * np.float32(1 / 255)


# =============================================================================================== style
@dataclasses.dataclass(frozen=True)
class Style:
    """Composable text style (all lengths in em). See STYLES for presets and the module docstring."""
    name: str = 'flat'
    font: str = 'Nunito-Black'
    px: float = 160.0
    tracking: float = 0.0
    line_height: float = 1.08
    align: str = 'center'
    max_width: float = 0.0
    ss: int = 0
    gamma: float = 1.0
    # face
    face: bool = True
    fill: object = 'IVORY'
    fill_angle: float = -90.0
    fill_gain: float = 1.0
    # bevel + lighting
    bevel: float = 0.0
    profile: str = 'round'
    light: tuple = (-0.42, -0.72, 0.78)
    ambient: float = 0.55
    spec: float = 0.0
    shininess: float = 30.0
    spec_color: object = 'WHITE'
    spec_light: tuple = (-0.55, -0.75, 0.4)
    rim: float = 0.0
    rim_color: object = 'ORANGE'
    rim_dir: tuple = (0.8, 0.6)
    env: float = 0.0
    env_horizon: float = 0.56
    env_ground: object = 'PEACH'
    inner_shadow: float = 0.0
    inner_shadow_color: object = 'PLUM'
    inner_shadow_size: float = 0.03
    inner_shadow_offset: tuple = (0.0, 0.025)
    inner_glow: float = 0.0
    inner_glow_color: object = 'HOT_PINK'
    inner_glow_size: float = 0.05
    # extrusion
    depth: float = 0.0
    angle: float = -62.0
    persp: float = 0.0
    side: object = None
    side_gain: float = 0.42
    side_tint: object = '#8E1E68'
    side_falloff: float = 0.6
    side_key: float = 0.55
    side_ambient: float = 0.35
    side_rim: float = 0.8
    edge_rim: float = 0.0
    # outline / neon
    stroke: float = 0.0
    stroke_color: object = 'WHITE'
    tube: float = 0.0
    tube_color: object = 'HOT_PINK'
    tube_core: float = 2.0
    tube_fill: float = 0.0
    # glow
    glow: float = 0.0
    glow_color: object = 'MAGENTA'
    glow_radii: tuple = (0.04, 0.12, 0.32)
    glow_weights: tuple = (1.0, 0.8, 0.6)
    glow_src: str = 'face'
    # shadows / backing
    shadow: float = 0.0
    shadow_color: object = 'NIGHT_0'
    shadow_offset: tuple = (0.0, 0.06)
    shadow_blur: float = 0.06
    long_shadow: float = 0.0
    long_shadow_len: float = 0.5
    long_shadow_angle: float = -50.0
    long_shadow_color: object = 'INK'
    long_shadow_blur: float = 0.05
    scrim: float = 0.0
    scrim_color: object = 'NIGHT_0'
    scrim_size: float = 0.5
    # glass pill
    pill: float = 0.0
    pill_dark: float = 0.0
    pill_color: object = 'WHITE'
    pill_pad: tuple = (0.75, 0.55)
    pill_radius: float = -1.0
    pill_rim: float = 0.55
    pill_frost: float = 16.0
    pill_shadow: float = 0.35
    pill_shadow_color: object = 'NIGHT_0'
    pill_tint: object = None
    pill_tint_amount: float = 0.35

    def but(self, **kw):
        return dataclasses.replace(self, **{k: _hashable(v) for k, v in kw.items()})


STYLES = {
    'flat': Style(name='flat'),
    'ui': Style(name='ui', font='Poppins-SemiBold', px=40, fill='IVORY', tracking=0.005),
    'ui_ink': Style(name='ui_ink', font='Poppins-SemiBold', px=40, fill='INK', tracking=0.005, gamma=0.82),
    'extrude3d': Style(
        name='extrude3d', fill=((0.0, '#FFFFFF'), (0.5, '#F3EEF3'), (1.0, '#D8CEDA')), fill_gain=0.94,
        bevel=0.03, profile='chamfer', ambient=0.42, spec=1.0, shininess=28, rim=1.0, rim_color=('HOT_PINK', 1.5),
        env=0.25, inner_shadow=0.18, inner_shadow_color='PLUM', depth=0.15, angle=-64, persp=0.05,
        side=None, side_gain=0.5, side_falloff=0.0, side_key=0.35, side_ambient=0.3,
        side_rim=0.2, edge_rim=0.9, glow=0.3, glow_color=('MAGENTA', 1.4), glow_radii=(0.15, 0.45), glow_weights=(0.6, 0.45),
        glow_src='all', shadow=0.55, shadow_offset=(0.02, 0.12), shadow_blur=0.09),
    'gold': Style(
        name='gold', fill=((0.0, '#FFF1D2'), (0.45, '#FFC46A'), (1.0, '#F08A1E')), fill_gain=1.05,
        bevel=0.03, profile='chamfer', ambient=0.45, spec=1.0, shininess=30, rim=0.7,
        rim_color=('#FFD9A0', 1.3), env=0.5, env_horizon=0.58, env_ground='#FFB15C', inner_shadow=0.22,
        inner_shadow_color='#7A2A00', depth=0.14, angle=-66, persp=0.05, side=(('#9A3A06', 1.0), ('#1E0802', 1.0)),
        side_falloff=0.0, side_key=0.4, side_ambient=0.32, side_rim=0.15, edge_rim=0.8, glow=0.3,
        glow_color=('ORANGE', 1.5), glow_radii=(0.15, 0.45), glow_weights=(0.6, 0.45), glow_src='all',
        shadow=0.55, shadow_offset=(0.02, 0.12), shadow_blur=0.09),
    'chrome': Style(
        name='chrome', fill=((0.0, '#FFFFFF'), (1.0, '#F4EEF4')), fill_gain=1.0, bevel=0.03, profile='round',
        ambient=0.45, spec=1.2, shininess=40, rim=1.0, rim_color=('ORANGE', 1.6), env=0.85, env_horizon=0.55,
        env_ground='#FF9A6A', inner_shadow=0.12, depth=0.13, angle=-68, persp=0.05,
        side=(('#8E1E68', 1.0), ('#16051A', 1.0)), side_falloff=0.0, side_key=0.35, side_ambient=0.3,
        side_rim=0.15, edge_rim=1.0, glow=0.3, glow_color=('MAGENTA', 1.6), glow_radii=(0.15, 0.45),
        glow_weights=(0.6, 0.45), glow_src='all', shadow=0.5, shadow_offset=(0.0, 0.1)),
    'deep_glow': Style(
        name='deep_glow', fill=((0.0, '#FFFFFF'), (1.0, '#FFF1F8')), fill_gain=1.55, inner_glow=0.75,
        inner_glow_color=('HOT_PINK', 1.3), inner_glow_size=0.045, glow=1.0, glow_color=('MAGENTA', 2.8),
        glow_radii=(0.02, 0.06, 0.16, 0.38, 0.8), glow_weights=(0.9, 0.8, 0.7, 0.6, 0.45), scrim=0.0,
        gamma=1.08),
    'neon': Style(
        name='neon', face=False, tube=0.042, tube_color=('HOT_PINK', 1.5), tube_core=2.2, tube_fill=0.06,
        glow=1.0, glow_color=('MAGENTA', 2.4), glow_radii=(0.025, 0.08, 0.24), glow_weights=(1.0, 0.7, 0.5)),
    'gradient': Style(
        name='gradient', fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, bevel=0.022, profile='soft',
        ambient=0.7, spec=0.55, shininess=26, inner_glow=0.25, inner_glow_color=('AMBER', 1.0),
        inner_glow_size=0.03, glow=0.3, glow_color=('MAGENTA', 1.4), shadow=0.45, shadow_offset=(0.0, 0.06)),
    'ink_soft': Style(
        name='ink_soft', fill=((0.0, '#3C2740'), (1.0, '#2A1A2D')), bevel=0.018, profile='soft', ambient=0.8,
        spec=0.5, shininess=20, depth=0.03, angle=-55, side=(('#6E2A60', 1.0), ('#4A1A44', 1.0)),
        side_falloff=0.0, side_key=0.4, side_ambient=0.7, side_rim=0.0, long_shadow=0.38,
        long_shadow_len=0.65, long_shadow_angle=-52, long_shadow_color='#8A5070', long_shadow_blur=0.04,
        glow=0.22, glow_color=('WHITE', 0.5), glow_radii=(0.12, 0.35), glow_weights=(0.7, 0.5),
        shadow=0.16, shadow_color='#5B2E52', shadow_offset=(0.01, 0.035), shadow_blur=0.035),
    'glass_pill': Style(
        name='glass_pill', font='Poppins-SemiBold', px=40, fill='IVORY', tracking=0.01, pill=0.07,
        pill_dark=0.42, pill_pad=(0.8, 0.62), pill_rim=0.85, pill_frost=18, pill_shadow=0.45,
        pill_tint=('MAGENTA', 1.4), pill_tint_amount=0.45),
    'glass_pill_light': Style(
        name='glass_pill_light', font='Poppins-SemiBold', px=40, fill='INK', tracking=0.01, pill=0.5,
        pill_dark=0.0, pill_pad=(0.8, 0.62), pill_rim=1.0, pill_frost=12, pill_shadow=0.14,
        pill_shadow_color='#5B2E52', pill_tint='PEACH', pill_tint_amount=0.35),
}


def style(spec='flat', /, **kw):
    """Style from a preset name / Style / None plus overrides: style('extrude3d', px=220, depth=0.2).
    (spec is positional-only, so the Style field `spec` (specular) can be overridden too: style('gold', spec=0.6).)"""
    if spec is None:
        base = STYLES['flat']
    elif isinstance(spec, Style):
        base = spec
    else:
        base = STYLES[spec]
    if kw:
        if 'font' in kw:
            kw['font'] = font_name(kw['font'])
        base = base.but(**kw)
    elif base.font in FONT_ALIAS:
        base = base.but(font=font_name(base.font))
    return base


def measure(text, st='flat', **kw):
    """(w, h) of the text box in px for a style (no rasterising)."""
    s = style(st, **kw)
    lay = layout(text, font_name(s.font), s.px, s.tracking, s.line_height, s.align, s.max_width)
    return lay.w, lay.h


# =============================================================================================== byte-budget cache
class _LRU:
    def __init__(self, mb):
        self.d = collections.OrderedDict()
        self.bytes = 0
        self.budget = mb * 1024 * 1024

    def get(self, key, fn):
        v = self.d.get(key)
        if v is not None:
            self.d.move_to_end(key)
            return v
        v = fn()
        nb = getattr(v, 'nbytes', 0)
        self.d[key] = v
        self.bytes += nb
        while self.bytes > self.budget and len(self.d) > 1:
            _, old = self.d.popitem(last=False)
            self.bytes -= getattr(old, 'nbytes', 0)
        return v

    def clear(self):
        self.d.clear()
        self.bytes = 0


_CACHE = _LRU(int(os.environ.get('FOSTER_TYPE_CACHE_MB', '400')))


def clear_cache():
    _CACHE.clear()


# =============================================================================================== image helpers
def _shift(a, dx, dy, sc=1.0, c=(0.0, 0.0)):
    """Translate (and scale about c) an image with bilinear filtering, zero border."""
    M = np.float32([[sc, 0, (1 - sc) * c[0] + dx], [0, sc, (1 - sc) * c[1] + dy]])
    return cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                          borderValue=0)


def _blur(a, sigma):
    if sigma < 0.3:
        return a
    return K.gblur(np.ascontiguousarray(a, np.float32), sigma, border='constant')


def _sdf(A):
    """Signed distance in px of the coverage image A (positive inside), sub-pixel at the edge."""
    b = (A >= 0.5).astype(np.uint8)
    din = cv2.distanceTransform(b, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    dout = cv2.distanceTransform(1 - b, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    d = np.where(b > 0, din - 0.5, 0.5 - dout).astype(np.float32)
    edge = (np.abs(d) <= 1.0) & (A > 0.002) & (A < 0.998)
    d = np.where(edge, A - 0.5, d).astype(np.float32)
    return cv2.GaussianBlur(d, (0, 0), 0.7)


def _grad(d):
    gx = cv2.Sobel(d, cv2.CV_32F, 1, 0, ksize=3) * np.float32(0.125)
    gy = cv2.Sobel(d, cv2.CV_32F, 0, 1, ksize=3) * np.float32(0.125)
    n = np.sqrt(gx * gx + gy * gy) + np.float32(1e-6)
    return gx / n, gy / n


def _down(a, ss):
    if ss == 1:
        return a
    h, w = a.shape[:2]
    return cv2.resize(a, (w // ss, h // ss), interpolation=cv2.INTER_AREA)


def _sstep(e0, e1, x):
    """Array-friendly smoothstep."""
    x = np.clip((np.asarray(x, np.float32) - e0) / (e1 - e0), 0, 1)
    return x * x * (3 - 2 * x)


def _premul(rgb, a):
    return np.dstack([rgb * a[..., None], a]).astype(np.float32)


def _norm3(v):
    v = np.asarray(v, np.float64)
    return v / max(np.linalg.norm(v), 1e-9)


def _over_into(dst, src):
    """dst = src over dst (same shape premultiplied)."""
    dst *= (1 - src[..., 3:4])
    dst += src
    return dst


# =============================================================================================== layers / TextSprite
class Layer:
    """One cached sprite of a text: spr covers block-coords box=(x0, y0, x1, y1) at res sprite px per block px.
    mode: core blend mode; frost: frosted-glass sigma; part: 'pill' | 'glow' | 'back' | 'front' | 'sweep'."""
    __slots__ = ('spr', 'box', 'res', 'mode', 'frost', 'part')

    def __init__(self, spr, box, res=1.0, mode='over', frost=0.0, part='front'):
        self.spr, self.box, self.res, self.mode, self.frost, self.part = spr, box, res, mode, frost, part

    @property
    def nbytes(self):
        return self.spr.nbytes

    def corners(self):
        x0, y0, x1, y1 = self.box
        return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float64)


_ORDER = {'pill': 0, 'glow': 1, 'back': 2, 'front': 3, 'sweep': 4}


class TextSprite:
    """A rendered text: layers in draw order + cached face/bevel masks for light sweeps (see module docs)."""

    def __init__(self, lay, st, layers, face=None, frame=None, pill_box=None):
        self.layout, self.style = lay, st
        self.layers = sorted(layers, key=lambda L: _ORDER[L.part])
        self.w, self.h = lay.w, lay.h
        self.face = face                 # (region box, face alpha 1x, bevel weight 1x) or None
        self.frame = frame or (0.0, 0.0, lay.w, lay.h)
        self.pill_box = pill_box
        self._merged = None
        self._sweep_cache = {}

    @property
    def nbytes(self):
        n = sum(L.nbytes for L in self.layers)
        if self.face is not None:
            n += self.face[1].nbytes + self.face[2].nbytes
        return n

    def anchor_point(self, anchor=(0.5, 0.5)):
        if isinstance(anchor, str):
            anchor = {'center': (0.5, 0.5), 'left': (0.0, 0.5), 'right': (1.0, 0.5), 'top': (0.5, 0.0),
                      'baseline': (0.5, 1.0), 'tl': (0.0, 0.0), 'bl': (0.0, 1.0)}[anchor]
        return anchor[0] * self.w, anchor[1] * self.h

    def bounds(self):
        """Union of all layer boxes (block coords)."""
        b = np.array([L.box for L in self.layers], np.float64)
        return b[:, 0].min(), b[:, 1].min(), b[:, 2].max(), b[:, 3].max()

    # ---------------------------------------------------------------- drawing
    def _layers(self, parts, sweep, sweep_kw):
        ls = [L for L in self.layers if parts is None or L.part in parts]
        if sweep is not None and self.face is not None and (parts is None or 'front' in parts or 'sweep' in parts):
            sw = self.sweep_layer(sweep, **(sweep_kw or {}))
            if sw is not None:
                ls.append(sw)
        return ls

    def draw(self, cv, x, y, anchor=(0.5, 0.5), scale=1.0, rot=0.0, opacity=1.0, blur=0.0, sweep=None,
             sweep_kw=None, parts=None, snap=True, mode=None):
        """Draw with the text-box anchor at canvas (x, y). scale float or (sx, sy); rot degrees clockwise."""
        if opacity <= 1e-4:
            return None
        ax, ay = self.anchor_point(anchor)
        sx, sy = (scale, scale) if not isinstance(scale, (tuple, list, np.ndarray)) else scale
        r = math.radians(rot)
        c, s = math.cos(r), math.sin(r)
        M = np.array([[c * sx, -s * sy, 0.0], [s * sx, c * sy, 0.0]])
        M[0, 2] = x - (M[0, 0] * ax + M[0, 1] * ay)
        M[1, 2] = y - (M[1, 0] * ax + M[1, 1] * ay)
        if snap and rot == 0 and abs(sx - 1) < 1e-9 and abs(sy - 1) < 1e-9:
            M[0, 2], M[1, 2] = round(M[0, 2]), round(M[1, 2])
        return _draw_layers_affine(cv, self._layers(parts, sweep, sweep_kw), M, opacity, blur, mode)

    def draw_quad(self, cv, quad, opacity=1.0, blur=0.0, sweep=None, sweep_kw=None, parts=None, mode=None):
        """Map the text box onto a screen quad [TL, TR, BR, BL] (perspective) and draw every layer."""
        q = np.asarray(quad, np.float64).reshape(4, 2)
        Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [self.w, 0], [self.w, self.h], [0, self.h]]),
                                         np.float32(q)).astype(np.float64)
        return _draw_layers_h(cv, self._layers(parts, sweep, sweep_kw), Hm, opacity, blur, mode)

    def draw_plane(self, cv, cam, center, rot=(0.0, 0.0, 0.0), scale=1.0, anchor=(0.5, 0.5), opacity=1.0,
                   dof=True, blur=0.0, sweep=None, sweep_kw=None, parts=None, mode=None):
        """3D: text box anchor at world `center`, plane rotation rot (core.draw_plane conventions);
        scale = world units per text px."""
        ax, ay = self.anchor_point(anchor)
        out = None
        for L in self._layers(parts, sweep, sweep_kw):
            x0, y0, x1, y1 = L.box
            lw, lh = (x1 - x0) * scale, (y1 - y0) * scale
            an = ((ax - x0) / (x1 - x0), (ay - y0) / (y1 - y0))
            r = K.draw_plane(cv, L.spr, cam, center, lw, rot=rot, opacity=opacity, mode=mode or L.mode,
                             dof=dof, height=lh, blur=blur, frost=L.frost, anchor=an)
            if L.part == 'front' and r is not None:
                out = r
        return out

    # ---------------------------------------------------------------- sweep
    def sweep_layer(self, u, width=0.09, angle=-32.0, color='WHITE', strength=1.25, face=0.5, bevel=1.6,
                    halo=0.22, frame=None):
        """Additive specular band layer at progress u (see light_sweep)."""
        if self.face is None or u is None or u <= 0 or u >= 1:
            return None
        box, fa, bw = self.face
        fx, fy, FW, FH = frame or self.frame
        key = (angle, box)
        sm = self._sweep_cache.get(key)
        if sm is None:
            dx, dy = math.cos(math.radians(angle)), -math.sin(math.radians(angle))
            ext = abs(FW / 2 * dx) + abs(FH / 2 * dy)            # half extent of the frame along the travel
            X = np.arange(box[0], box[2], dtype=np.float32) + 0.5 + fx - FW / 2
            Y = np.arange(box[1], box[3], dtype=np.float32) + 0.5 + fy - FH / 2
            sm = (X[None, :] * dx + Y[:, None] * dy).astype(np.float32)          # px along the travel
            nz = (fa > 0.003) | (bw > 0.003)
            ys, xs = np.nonzero(nz)
            crop = (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1) if len(ys) else (0, 1, 0, 1)
            y0, y1, x0, x1 = crop
            sm = (sm[y0:y1, x0:x1], (fa * face)[y0:y1, x0:x1].astype(np.float32),
                  (bw * bevel)[y0:y1, x0:x1].astype(np.float32), crop, ext)
            self._sweep_cache[key] = sm
        s, fw_, bw_, crop, ext = sm
        wpx = max(1.0, width * self.style.px)
        reach = ext + 2.2 * wpx * (1 + 3 * halo)
        pos = -reach + u * 2 * reach
        dd = (s - np.float32(pos)) * np.float32(1 / wpx)
        dd2 = dd * dd
        band = np.exp(-dd2)
        if halo > 0:
            band += np.float32(halo) * np.exp(dd2 * np.float32(-1 / 16))
        k = band * (fw_ + bw_ * band)
        c = col(color) * np.float32(strength)
        spr = np.zeros(k.shape + (4,), np.float32)
        spr[..., :3] = k[..., None] * c
        y0, y1, x0, x1 = crop
        return Layer(spr, (box[0] + x0, box[1] + y0, box[0] + x1, box[1] + y1), 1.0, 'add', 0.0, 'sweep')

    # ---------------------------------------------------------------- merged sprite
    @property
    def sprite(self):
        """All layers merged into one sprite (frost is lost); use sprite_anchor() for core.draw anchors."""
        if self._merged is None:
            bx0, by0, bx1, by1 = [int(math.floor(v)) if i < 2 else int(math.ceil(v))
                                  for i, v in enumerate(self.bounds())]
            out = np.zeros((by1 - by0, bx1 - bx0, 4), np.float32)
            M = np.array([[1.0, 0, -bx0], [0, 1.0, -by0]])
            _draw_layers_affine(out, self.layers, M, 1.0, 0.0, None)
            self._merged = (out, (bx0, by0, bx1, by1))
        return self._merged[0]

    def merged(self):
        """The merged sprite as a single Layer (block-coords box), e.g. for many small 3D glyph quads."""
        spr = self.sprite
        return Layer(spr, self._merged[1], 1.0, 'over', 0.0, 'front')

    def sprite_anchor(self, anchor=(0.5, 0.5)):
        """core.draw anchor fraction for .sprite that corresponds to a text-box anchor."""
        spr = self.sprite
        bx0, by0, bx1, by1 = self._merged[1]
        ax, ay = self.anchor_point(anchor)
        return (ax - bx0) / spr.shape[1], (ay - by0) / spr.shape[0]


def _draw_layers_affine(cv, layers, M, opacity, blur, mode):
    """Draw layers through the 2x3 affine M (block coords -> canvas)."""
    bb = None
    pure = abs(M[0, 0] - 1) < 1e-9 and abs(M[1, 1] - 1) < 1e-9 and abs(M[0, 1]) < 1e-12 and abs(M[1, 0]) < 1e-12
    for L in layers:
        m = mode or L.mode
        if pure and L.res == 1.0 and blur <= 0:
            r = K.draw(cv, L.spr, M[0, 2] + L.box[0], M[1, 2] + L.box[1], anchor=(0, 0), opacity=opacity,
                       mode=m, frost=L.frost)
        else:
            q = L.corners() @ M[:, :2].T + M[:, 2]
            r = K.draw_quad(cv, L.spr, q, opacity=opacity, mode=m, blur=blur, frost=L.frost)
        bb = _bb_union(bb, r)
    return bb


def _draw_layers_h(cv, layers, Hm, opacity, blur, mode):
    bb = None
    for L in layers:
        c = np.c_[L.corners(), np.ones(4)] @ Hm.T
        if (c[:, 2] <= 1e-6).any():
            continue
        q = c[:, :2] / c[:, 2:3]
        r = K.draw_quad(cv, L.spr, q, opacity=opacity, mode=mode or L.mode, blur=blur, frost=L.frost)
        bb = _bb_union(bb, r)
    return bb


def _bb_union(a, b):
    if b is None:
        return a
    if a is None:
        return b
    return min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])


# =============================================================================================== builder
def render(text, st='flat', frame=None, **kw):
    """Render text with a style (preset name or Style, plus overrides) -> cached TextSprite.
    frame=(fx, fy, FW, FH): place this text's box at (fx, fy) inside a larger FW x FH frame so fills and
    sweeps line up with a parent block (used for per-glyph sprites)."""
    s = style(st, **kw)
    key = ('render', text, s, frame)
    return _CACHE.get(key, lambda: _build(text, s, frame))


def _build(text, st, frame=None):
    lay = layout(text, font_name(st.font), st.px, st.tracking, st.line_height, st.align, st.max_width)
    return _build_layout(lay, st, frame)


def _build_layout(lay, st, frame):
    L = st.px
    ss = st.ss or (3 if L < 56 else 2)
    frame = frame or (0.0, 0.0, lay.w, lay.h)
    fx, fy, FW, FH = frame
    dep = st.depth * L
    bev = st.bevel * L
    pad_f = int(math.ceil(max(3.0, st.stroke * L + 2, st.tube * L + 2,
                              4.0 if (st.inner_shadow > 0 or st.inner_glow > 0) else 0.0))) + 2
    ext = [float(pad_f), dep * (1.05 + st.persp) + 3]
    if st.shadow > 0:
        ext.append(max(abs(st.shadow_offset[0]), abs(st.shadow_offset[1])) * L + 3 * st.shadow_blur * L + dep)
    if st.long_shadow > 0:
        ext.append(st.long_shadow_len * L * 1.1 + 3 * st.long_shadow_blur * L * 2.5)
    pad = max(pad_f, int(math.ceil(max(ext))) + 2)
    ix0, iy0, ix1, iy1 = lay.ink
    region = (int(math.floor(ix0)) - pad, int(math.floor(iy0)) - pad, int(math.ceil(ix1)) + pad,
              int(math.ceil(iy1)) + pad)
    region_f = (int(math.floor(ix0)) - pad_f, int(math.floor(iy0)) - pad_f, int(math.ceil(ix1)) + pad_f,
                int(math.ceil(iy1)) + pad_f)
    rx0, ry0, rx1, ry1 = region
    fx0, fy0 = region_f[0], region_f[1]
    A = _raster(lay, ss, region_f)
    if st.gamma != 1.0:
        A = A ** np.float32(st.gamma)
    Hs, Ws = A.shape
    # frame coords of ss pixel centres
    Xs = (np.arange(Ws, dtype=np.float32) + 0.5) / ss + fx0 + fx
    Ys = (np.arange(Hs, dtype=np.float32) + 0.5) / ss + fy0 + fy
    need_sdf = bev > 0 or st.tube > 0 or st.stroke > 0
    d = _sdf(A) / np.float32(ss) if need_sdf else None          # 1x px units
    gx = gy = None
    if d is not None:
        gx, gy = _grad(d)                                        # unit, pointing inward
    Lv = [float(v) for v in _norm3(st.light)]
    layers = []
    face_alpha = None
    bevel_w = None
    # ------------------------------------------------------------------ front face
    front = np.zeros((Hs, Ws, 4), np.float32)
    if st.face:
        F = _fill_map(st.fill, st.fill_angle, Xs, Ys, FW, FH) * np.float32(st.fill_gain)
        rgb = np.array(F, np.float32, copy=True)
        if bev > 0:
            x = np.clip(d / bev, 0, 1)
            if st.profile == 'chamfer':
                slope = (x < 1).astype(np.float32) * 1.0
            elif st.profile == 'soft':
                slope = 3.0 * (1 - x) ** 2
            else:
                slope = np.clip((1 - x) / np.sqrt(np.maximum(1 - (1 - x) ** 2, 1e-3)), 0, 4.0)
            slope = slope.astype(np.float32)
            nx, ny = -slope * gx, -slope * gy
            nz = np.ones_like(nx)
            nn = np.sqrt(nx * nx + ny * ny + 1)
            nx, ny, nz = nx / nn, ny / nn, nz / nn
            ndl = nx * Lv[0] + ny * Lv[1] + nz * Lv[2]
            lam = st.ambient + (1 - st.ambient) * np.clip(ndl, 0, None) / Lv[2]
            rgb *= lam[..., None].astype(np.float32)
            if st.spec > 0:
                Hv = [float(v) for v in _norm3(_norm3(st.spec_light) + np.array([0, 0, 1.0]))]
                ndh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)
                base = Hv[2] ** st.shininess
                sp = np.clip(ndh ** st.shininess - base, 0, None) / max(1 - base, 1e-6)
                rgb += (sp * st.spec)[..., None] * col(st.spec_color)
            if st.rim > 0:
                rd = np.asarray(st.rim_dir, np.float32)
                rd = rd / max(np.linalg.norm(rd), 1e-6)
                rimk = (1 - nz) ** 1.1 * np.clip(nx * rd[0] + ny * rd[1], 0, None)
                rgb += (rimk * st.rim * 1.6)[..., None] * col(st.rim_color)
            bevel_w = np.clip((1 - nz) * 3.0, 0, 1) * A
        else:
            nx = ny = None
            nz = np.ones_like(A)
        if st.env > 0:
            # chrome environment: sky above a horizon line, a dark band under it, warm floor bounce; reflected
            # through the bevel normals so the bands bend around the letter edges
            v = _line_v(lay, Ys - fy)
            vv = v[:, None] + (np.float32(0.0) if nx is None else np.float32(0.45) * (2 * nz * ny))
            hz = st.env_horizon
            tsky = np.clip((hz - vv) / max(hz, 1e-3), 0, 1)
            sky = 0.9 + 0.4 * tsky ** 0.8
            below = np.clip((vv - hz) / max(1.15 - hz, 1e-3), 0, 1)
            gc = col(st.env_ground)
            gc = gc / max(float(gc.max()), 1e-6)
            grd = (0.38 + 0.62 * below[..., None] ** 0.7) * gc
            k = _sstep(hz - 0.012, hz + 0.012, vv)[..., None]
            E = sky[..., None] * (1 - k) + grd * k
            dark = np.exp(-((vv - hz - 0.025) / 0.045) ** 2)[..., None]
            E = E * (1 - 0.7 * dark)
            rgb *= (1 + st.env * (E - 1)).astype(np.float32)
        if st.inner_glow > 0:
            sg = st.inner_glow_size * L * ss
            ig = np.clip(_blur(1 - A, sg) * 1.6, 0, 1) * A
            igc = col(st.inner_glow_color)
            k = (ig * st.inner_glow)[..., None]
            rgb = rgb * (1 - k * 0.6) + igc * k
        if st.inner_shadow > 0:
            ox, oy = st.inner_shadow_offset
            sh = _blur(1 - _shift(A, ox * L * ss, oy * L * ss), st.inner_shadow_size * L * ss)
            k = (np.clip(sh, 0, 1) * st.inner_shadow)[..., None]
            rgb = rgb * (1 - k) + col(st.inner_shadow_color) * k
        front = _premul(rgb, A)
        face_alpha = A
    if st.stroke > 0:
        wv = st.stroke * L
        dist = -d                                               # outside distance
        a_st = np.clip((wv - dist) * ss + 0.5, 0, 1) * np.clip(dist * ss + 1.0, 0, 1)
        a_st = np.maximum(a_st - A, 0) if st.face else a_st
        _over_into_under(front, _premul(np.broadcast_to(col(st.stroke_color), A.shape + (3,)), a_st))
    if st.tube > 0:
        hw = st.tube * L / 2
        ad = np.abs(d)
        ta = np.clip((hw - ad) * ss + 0.5, 0, 1)
        prof = np.clip(1 - (ad / hw) ** 2, 0, 1)
        tc = col(st.tube_color)
        rgb = tc[None, None, :] * (0.55 + 0.9 * prof)[..., None] + (np.float32(st.tube_core) * prof ** 5)[..., None]
        tube = _premul(rgb.astype(np.float32), ta)
        if st.tube_fill > 0:
            _over_into(front, _premul(np.broadcast_to(tc, A.shape + (3,)), A * st.tube_fill))
        _over_into(front, tube)
        face_alpha = np.maximum(ta, 0 if face_alpha is None else face_alpha)
        bevel_w = ta * prof
    front1 = _down(front, ss)
    A1f = _down(A, ss)
    layers.append(Layer(front1, region_f, 1.0, 'over', 0.0, 'front'))
    if face_alpha is not None:
        fa1 = _down(face_alpha, ss) if face_alpha is not A else A1f
        bw1 = _down(bevel_w, ss) if bevel_w is not None else np.zeros_like(fa1)
        face = (region_f, fa1.astype(np.float32), bw1.astype(np.float32))
    else:
        face = None
    # 1x coverage on the big (back) region
    h1, w1 = ry1 - ry0, rx1 - rx0
    A1 = np.zeros((h1, w1), np.float32)
    ox_, oy_ = fx0 - rx0, fy0 - ry0
    A1[oy_:oy_ + A1f.shape[0], ox_:ox_ + A1f.shape[1]] = A1f
    if face is not None:
        FA = np.zeros((h1, w1), np.float32)
        FA[oy_:oy_ + A1f.shape[0], ox_:ox_ + A1f.shape[1]] = face[1]
    else:
        FA = A1
    # ------------------------------------------------------------------ back: extrusion + shadows
    back = np.zeros((h1, w1, 4), np.float32)
    union = A1.copy() if st.face else FA.copy()
    if dep > 0:
        ang = math.radians(st.angle)
        ux, uy = math.cos(ang), -math.sin(ang)
        # smooth outward contour normals (from a blurred coverage, not the faceted distance field)
        Ab = cv2.GaussianBlur(A1, (0, 0), max(1.0, 0.012 * L))
        gx1 = cv2.Sobel(Ab, cv2.CV_32F, 1, 0, ksize=3)
        gy1 = cv2.Sobel(Ab, cv2.CV_32F, 0, 1, ksize=3)
        gn = np.sqrt(gx1 * gx1 + gy1 * gy1) + np.float32(1e-6)
        nxo, nyo = -gx1 / gn, -gy1 / gn                        # outward contour normals
        l2 = np.array([Lv[0], Lv[1]], np.float32)
        l2 /= max(np.linalg.norm(l2), 1e-6)
        key = np.clip(nxo * l2[0] + nyo * l2[1], 0, None)
        facing = np.clip(nxo * ux + nyo * uy, 0, 1) ** 0.7     # sides turned toward the viewer read lighter
        rd = np.asarray(st.rim_dir, np.float32)
        rd = rd / max(np.linalg.norm(rd), 1e-6)
        rimk = np.clip(nxo * rd[0] + nyo * rd[1], 0, None) ** 4
        lam = (st.side_ambient + st.side_key * key + 0.5 * facing).astype(np.float32)
        Ff = _fill_map(st.fill, st.fill_angle, (np.arange(w1) + 0.5 + rx0 + fx).astype(np.float32),
                       (np.arange(h1) + 0.5 + ry0 + fy).astype(np.float32), FW, FH)
        sst = _stops(st.side) if st.side is not None else None
        if st.side is None:
            # auto: a darker, plum-tinted version of the face colour (works for any fill / gradient)
            tint = col(st.side_tint)
            near = Ff * np.float32(st.side_gain * 0.55) + tint * np.float32(0.45)
            far = Ff * np.float32(0.05) + col('#1A0518') * np.float32(1 - st.side_falloff)
        elif sst is None:
            near = np.broadcast_to(col(st.side), (h1, w1, 3))
            far = near * np.float32(1 - st.side_falloff)
        else:
            near = np.broadcast_to(sst[0][1], (h1, w1, 3))
            far = np.broadcast_to(sst[-1][1], (h1, w1, 3)) * np.float32(1 - st.side_falloff)
        rimc = col(st.rim_color) * np.float32(st.side_rim) * rimk[..., None]
        Pn = np.dstack([(near * lam[..., None] + rimc) * A1[..., None], A1]).astype(np.float32)
        Pf = np.ascontiguousarray(((far * lam[..., None] + rimc * 0.35) * A1[..., None]).astype(np.float32))
        n = max(3, int(math.ceil(dep / 0.6)))
        cxy = (lay.w / 2 - rx0, lay.h / 2 - ry0)
        ext_a = np.zeros((h1, w1, 4), np.float32)
        for i in range(n, 0, -1):
            f = i / n
            sc = 1 - st.persp * f
            dx, dy = ux * dep * f, uy * dep * f
            pn = _shift(Pn, dx, dy, sc, cxy)
            pf = _shift(Pf, dx, dy, sc, cxy)
            lay_rgba = pn
            lay_rgba[..., :3] = pn[..., :3] * np.float32(1 - f) + pf * np.float32(f)
            _over_into(ext_a, lay_rgba)
        # dark occlusion right under the face lip so the face pops off the side
        occ = np.clip(_blur(A1, 1.2) * 1.0, 0, 1)
        ext_a[..., :3] *= (1 - 0.35 * occ * (1 - A1))[..., None]
        if st.edge_rim > 0:
            # rim light catching the far silhouette edge of the extrusion (thin coloured line)
            ea = ext_a[..., 3]
            wv = max(1.2, 0.012 * L)
            edge = np.clip(ea - _shift(ea, ux * wv, uy * wv), 0, 1) * np.clip(1 - _shift(A1, 0, 0) * 1.0, 0, 1)
            edge = _blur(edge, 0.6)
            ext_a[..., :3] += (edge * st.edge_rim)[..., None] * col(st.rim_color)
        union = 1 - (1 - union) * (1 - ext_a[..., 3])
        back = ext_a
    if st.long_shadow > 0:
        ls = _long_shadow(A1, st.long_shadow_len * L, st.long_shadow_angle, st.long_shadow_blur * L)
        back = _under(back, _premul(np.broadcast_to(col(st.long_shadow_color), ls.shape + (3,)),
                                    ls * st.long_shadow))
    if st.shadow > 0:
        ox, oy = st.shadow_offset
        sh = _blur(_shift(union, ox * L, oy * L), st.shadow_blur * L)
        back = _under(back, _premul(np.broadcast_to(col(st.shadow_color), sh.shape + (3,)),
                                    np.clip(sh, 0, 1) * st.shadow))
    if back[..., 3].max() > 0 or back[..., :3].max() > 0:
        layers.append(Layer(back, region, 1.0, 'over', 0.0, 'back'))
    # ------------------------------------------------------------------ glow / scrim (low-res layer)
    if st.glow > 0 or st.scrim > 0:
        layers.extend(_glow_layers(st, L, region, union if st.glow_src == 'all' else FA, A1))
    # ------------------------------------------------------------------ glass pill
    pill_box = None
    if st.pill > 0:
        pl, pill_box = _pill_layers(st, lay)
        layers.extend(pl)
    return TextSprite(lay, st, layers, face, frame, pill_box)


def _line_v(lay, Yb):
    """Per-row position 0 (cap top) .. 1 (baseline) within the row's own line."""
    lh = lay.line_height * lay.px
    li = np.clip(np.round((Yb - lay.cap) / max(lh, 1e-6)), 0, len(lay.lines) - 1)
    top = lay.cap * 0 + li * lh
    return ((Yb - top) / max(lay.cap, 1e-6)).astype(np.float32)


def _under(dst, src):
    """dst over src -> new array."""
    return dst + src * (1 - dst[..., 3:4])


def _over_into_under(dst, src):
    dst[:] = dst + src * (1 - dst[..., 3:4])
    return dst


def _long_shadow(A, length, angle, blur):
    """Soft long shadow: max of shifted copies with a fade, penumbra widening with distance (half res)."""
    h, w = A.shape
    q = 2 if length > 30 else 1
    As = cv2.resize(A, (max(1, w // q), max(1, h // q)), interpolation=cv2.INTER_AREA) if q > 1 else A
    ln, bl = length / q, blur / q
    a = math.radians(angle)
    ux, uy = math.cos(a), -math.sin(a)
    n = max(4, int(ln / 0.9))
    bands = 3
    acc = np.zeros_like(As)
    for b in range(bands):
        mx = np.zeros_like(As)
        i0, i1 = b * n // bands, (b + 1) * n // bands
        for i in range(max(1, i0), i1 + 1):
            f = i / n
            mx = np.maximum(mx, _shift(As, ux * ln * f, uy * ln * f) * np.float32((1 - f) ** 1.5))
        acc = np.maximum(acc, _blur(mx, bl * (0.6 + 1.6 * b)))
    if q > 1:
        acc = cv2.resize(acc, (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip(acc, 0, 1)


def _glow_layers(st, L, region, src_alpha, A1):
    """Deep glow (+ scrim) as emissive layers: tight radii at full / half res, wide radii at quarter res."""
    sig = [r * L for r in st.glow_radii] if st.glow > 0 else []
    wts = list(st.glow_weights) + [st.glow_weights[-1]] * max(0, len(sig) - len(st.glow_weights))
    groups = {}
    for s_, w_ in zip(sig, wts):
        res = 1.0 if s_ < 5 else (0.5 if s_ < 16 else 0.25)
        groups.setdefault(res, []).append((s_, w_))
    out = []
    if st.scrim > 0:
        out.append(_glow_one(st, L, region, src_alpha, A1, [], 0.25, scrim=True))
    for res in sorted(groups, reverse=True):
        out.append(_glow_one(st, L, region, src_alpha, A1, groups[res], res, scrim=False))
    return out


def _glow_one(st, L, region, src_alpha, A1, items, res, scrim):
    rx0, ry0, rx1, ry1 = region
    smax = max([s_ for s_, _ in items] + [st.scrim_size * L * 2.6 if scrim else 0.0])
    q = int(round(1 / res))
    pg = int(math.ceil(2.8 * smax)) + 4
    pg = pg + (-pg) % q
    w1, h1 = rx1 - rx0, ry1 - ry0
    W2, H2 = w1 + 2 * pg, h1 + 2 * pg
    W2 += (-W2) % q
    H2 += (-H2) % q
    src = np.zeros((H2, W2), np.float32)
    src[pg:pg + h1, pg:pg + w1] = src_alpha
    small = cv2.resize(src, (W2 // q, H2 // q), interpolation=cv2.INTER_AREA) if q > 1 else src
    out = np.zeros(small.shape + (4,), np.float32)
    if scrim:
        a1 = np.zeros((H2, W2), np.float32)
        a1[pg:pg + h1, pg:pg + w1] = A1
        a1s = cv2.resize(a1, (W2 // q, H2 // q), interpolation=cv2.INTER_AREA) if q > 1 else a1
        r = st.scrim_size * L * res
        k = max(3, int(r * 2.6) | 1)
        kh = max(3, int(r * 2.4) | 1)
        dil = cv2.dilate(a1s, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, kh)))
        sa = np.clip(_blur(dil, r * 1.25) * 1.35, 0, 1) ** 0.75 * st.scrim
        out[..., :3] = col(st.scrim_color) * sa[..., None]
        out[..., 3] = sa
    if items and st.glow > 0:
        gc = col(st.glow_color)
        acc = np.zeros_like(small)
        for s_, w_ in items:
            acc += _blur(small, s_ * res) * np.float32(w_)
        out[..., :3] += (acc * st.glow)[..., None] * gc
    box = (rx0 - pg, ry0 - pg, rx0 - pg + W2, ry0 - pg + H2)
    return Layer(out, box, res, 'over', 0.0, 'glow')


def _pill_layers(st, lay):
    L = st.px
    px_, py_ = st.pill_pad
    bw = lay.w + 2 * px_ * L
    bh = lay.h + 2 * py_ * L
    rad = bh / 2 if st.pill_radius < 0 else st.pill_radius * L
    x0, y0 = -px_ * L, -py_ * L
    shp = int(math.ceil(0.5 * bh)) + 6
    W_, H_ = int(math.ceil(bw)), int(math.ceil(bh))
    sdf = K.rrect_sdf(W_, H_, rad, shp)
    a = np.clip(0.5 - sdf, 0, 1).astype(np.float32)
    hh, ww = a.shape
    box = (x0 - shp, y0 - shp, x0 - shp + ww, y0 - shp + hh)
    yy = (np.arange(hh, dtype=np.float32) + 0.5 - shp) / max(H_, 1)
    xx = (np.arange(ww, dtype=np.float32) + 0.5 - shp) / max(W_, 1)
    out = []
    if st.pill_shadow > 0:
        sh = _blur(_shift(a, 0, 0.18 * bh), 0.22 * bh) * st.pill_shadow
        out.append(Layer(_premul(np.broadcast_to(col(st.pill_shadow_color), a.shape + (3,)), sh), box, 1.0,
                         'over', 0.0, 'pill'))
    base = col(st.pill_color)
    # body: darkening veil (pill_dark) + light added by the glass (pill), brighter toward the top (sheen),
    # a soft specular band under the top edge, a tinted glow along the bottom inner edge and a rim light
    inner = np.clip(-sdf / max(0.5 * bh, 1), 0, 1)
    sheen = np.clip(1 - yy, 0, 1)[:, None] ** 1.6
    spec = np.exp(-((yy - 0.16) / 0.09) ** 2)[:, None] * np.clip(1 - np.abs(xx - 0.5) * 2.0, 0, 1)[None, :] ** 0.6
    light = st.pill * (0.55 + 0.7 * sheen) + 0.10 * spec * (st.pill_rim > 0)
    rgb = (base[None, None, :] * (light * a)[..., None]).astype(np.float32)
    alpha = np.clip(st.pill_dark + (st.pill if st.pill_dark <= 0 else 0.0) * (0.75 + 0.5 * sheen), 0, 1) * a
    alpha = alpha.astype(np.float32)
    if st.pill_tint is not None:
        tg = np.exp(-((1 - yy) / 0.32) ** 2)[:, None] * (1 - inner) ** 1.2 * a * st.pill_tint_amount
        rgb = rgb + col(st.pill_tint)[None, None, :] * tg[..., None]
    if st.pill_rim > 0:
        stroke = np.clip(1.5 - np.abs(sdf + 1.0), 0, 1)
        top = np.clip(1 - yy * 1.25, 0, 1)[:, None]
        left = np.clip(1.2 - xx * 0.7, 0, 1)[None, :]
        rimg = 0.22 + 0.78 * (top * left) ** 1.2
        rk = (stroke * rimg * st.pill_rim).astype(np.float32)
        rgb = rgb * (1 - rk[..., None]) + col('WHITE') * rk[..., None] * 1.15
        alpha = np.maximum(alpha, rk * 0.9)
    body = np.dstack([rgb, alpha]).astype(np.float32)
    out.append(Layer(body, box, 1.0, 'over', float(st.pill_frost), 'pill'))
    return out, (x0, y0, x0 + bw, y0 + bh)


def light_sweep(ts, u, **kw):
    """Animated specular band over a TextSprite's face + bevel at progress u in [0, 1] -> TextSprite with one
    additive layer aligned to ts (draw it with the same placement), or use ts.draw(..., sweep=u, sweep_kw=kw).
    kw: width (em), angle (deg, direction the band travels; -24 = right and slightly down), color, strength,
    face (gain on the flat face), bevel (gain on bevel edges), halo (soft wide part)."""
    L = ts.sweep_layer(u, **kw)
    if L is None:
        return TextSprite(ts.layout, ts.style, [], None, ts.frame)
    return TextSprite(ts.layout, ts.style, [L], None, ts.frame)


def neon_flicker(t, seed=0, amount=1.0):
    """Opacity multiplier for neon: mostly 1 with rare quick dips (deterministic in t)."""
    k = int(t * 30)
    r = (math.sin(k * 12.9898 + seed * 78.233) * 43758.5453) % 1.0
    dip = 0.35 if r > 0.93 else (0.75 if r > 0.86 else 1.0)
    return 1 - amount * (1 - dip) - 0.03 * amount * math.sin(t * 50 + seed)


# =============================================================================================== kinetic glyphs
class GlyphState:
    """Per-glyph animation state (block coords; identity = settled)."""
    __slots__ = ('dx', 'dy', 'z', 'sx', 'sy', 'rot', 'rx', 'ry', 'opacity', 'blur', 'alt', 'sweep', 'mask')

    def __init__(self, dx=0.0, dy=0.0, z=0.0, sx=1.0, sy=1.0, rot=0.0, rx=0.0, ry=0.0, opacity=1.0, blur=0.0,
                 alt=None, sweep=None, mask=None):
        self.dx, self.dy, self.z, self.sx, self.sy, self.rot = dx, dy, z, sx, sy, rot
        self.rx, self.ry, self.opacity, self.blur, self.alt, self.sweep, self.mask = rx, ry, opacity, blur, alt, \
            sweep, mask

    def identity(self):
        return (abs(self.dx) < 1e-3 and abs(self.dy) < 1e-3 and abs(self.z) < 1e-3 and abs(self.sx - 1) < 1e-4
                and abs(self.sy - 1) < 1e-4 and abs(self.rot) < 1e-3 and abs(self.rx) < 1e-3 and abs(self.ry) < 1e-3
                and self.opacity > 0.999 and self.blur < 0.05 and self.alt is None and self.mask is None)


def _rotm(rx, ry, rz):
    rx, ry, rz = math.radians(rx), math.radians(ry), math.radians(rz)
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


class Glyphs:
    """Per-glyph sprites + layout positions + animators (see module docstring)."""
    DRAW_KEYS = ('anchor', 'scale', 'rot', 'opacity', 'tilt', 'focal', 'sweep', 'sweep_kw', 'mblur', 'blur')

    def __init__(self, text, st='flat', **kw):
        self.style = style(st, **kw)
        s = self.style
        self.text = text
        self.layout = layout(text, font_name(s.font), s.px, s.tracking, s.line_height, s.align, s.max_width)
        self.w, self.h = self.layout.w, self.layout.h
        self.items = [g for g in self.layout.glyphs if g.ink is not None]
        self.n = len(self.items)
        self._gst = s.but(pill=0.0) if s.pill > 0 else s

    @property
    def block(self):
        return render(self.text, self.style)

    def boxes(self):
        """Per-glyph text boxes (x0, y0, x1, y1) in block coords (ink width x cap height)."""
        cap = self.layout.cap
        return [(g.ink[0], g.base - cap, g.ink[2], g.base) for g in self.items]

    def glyph(self, k):
        """TextSprite of glyph k (box placed at boxes()[k] inside the block frame)."""
        g = self.items[k]
        x0, y0, x1, y1 = self.boxes()[k]
        return render(g.ch, self._gst, frame=(x0, y0, self.w, self.h))

    def alt_glyph(self, ch):
        return render(ch, self._gst)

    # ---------------------------------------------------------------- animators -> (states, block)
    def _order(self, order, seed=0):
        n = self.n
        if order == 'rtl':
            return list(range(n - 1, -1, -1))
        if order == 'center':
            c = (n - 1) / 2
            return sorted(range(n), key=lambda i: abs(i - c))
        if order == 'random':
            rng = np.random.default_rng(seed)
            return list(rng.permutation(n))
        return list(range(n))

    def _rank(self, order, seed=0):
        r = [0] * self.n
        for pos, i in enumerate(self._order(order, seed)):
            r[i] = pos
        return r

    def anim(self, kind, t, **kw):
        fn = getattr(self, '_a_' + kind)
        out_kw = {k: kw.pop(k) for k in ('out_t0', 'out_dur', 'out_dist', 'out_blur') if k in kw}
        states, blk = fn(t, **kw)
        if out_kw.get('out_t0') is not None:
            q = K.ramp(t, out_kw['out_t0'], out_kw['out_t0'] + out_kw.get('out_dur', 0.4), 'in_cubic')
            if q > 0:
                dist = out_kw.get('out_dist', 0.3) * self.style.px
                bl = out_kw.get('out_blur', 8.0)
                for s in states:
                    s.dy -= q * dist
                    s.opacity *= (1 - q)
                    s.blur += q * bl
        return states, blk

    def _a_rise(self, t, t0=0.0, stagger=0.035, dur=0.7, dist=0.45, blur=10.0, scale0=0.9, ease='out_expo',
                order='ltr', seed=0, fade=0.45):
        rk = self._rank(order, seed)
        out = []
        for i in range(self.n):
            p = K.ramp(t, t0 + rk[i] * stagger, t0 + rk[i] * stagger + dur, ease)
            pf = K.ramp(t, t0 + rk[i] * stagger, t0 + rk[i] * stagger + dur * fade, 'out_cubic')
            s = K.lerp(scale0, 1.0, p)
            out.append(GlyphState(dy=(1 - p) * dist * self.style.px, sx=s, sy=s, opacity=pf, blur=(1 - p) * blur))
        return out, {}

    def _a_slam(self, t, t0=0.0, s0=1.6, dur=0.45, freq=3.2, damping=0.45, stagger=0.0, blur=6.0, order='ltr'):
        if stagger > 0:
            rk = self._rank(order)
            out = []
            for i in range(self.n):
                tt = t - (t0 + rk[i] * stagger)
                sp = K.spring(max(tt, 0) / max(dur, 1e-3) * 0.45, freq, damping) if tt > 0 else 0.0
                s = s0 + (1 - s0) * sp
                op = K.clamp(tt / 0.05) if tt > 0 else 0.0
                out.append(GlyphState(sx=s, sy=s, opacity=op, blur=blur * max(0.0, 1 - sp) if tt > 0 else 0))
            return out, {}
        tt = t - t0
        if tt <= 0:
            return [GlyphState(opacity=0.0) for _ in range(self.n)], {'opacity': 0.0}
        sp = K.spring(tt / max(dur, 1e-3) * 0.45, freq, damping)
        s = s0 + (1 - s0) * sp
        op = K.clamp(tt / 0.05)
        return [GlyphState() for _ in range(self.n)], {'scale': s, 'opacity': op,
                                                       'blur': blur * max(0.0, 1 - sp) ** 2}

    def _a_typewriter(self, t, t0=0.0, cps=16.0, pop=0.08, caret=True):
        out = []
        for g in self.items:
            ti = t0 + g.i / cps
            p = K.ramp(t, ti, ti + pop, 'out_cubic')
            s = K.lerp(1.12, 1.0, p)
            out.append(GlyphState(sx=s, sy=s, opacity=p, dy=(1 - p) * 0.05 * self.style.px))
        blk = {}
        if caret:
            nvis = int(np.clip(math.ceil((t - t0) * cps - 1e-6), 0, len(self.layout.glyphs)))
            done = (t - t0) * cps >= len(self.layout.glyphs)
            blk['caret'] = (nvis, done, t)
        return out, blk

    def _a_wipe(self, t, t0=0.0, dur=0.6, angle=0.0, soft=0.12, ease='inout_cubic', edge=1.0):
        p = K.ramp(t, t0, t0 + dur, ease)
        return [GlyphState() for _ in range(self.n)], {'wipe': (p, angle, soft, edge)}

    def _a_track(self, t, t0=0.0, dur=0.9, amount=0.45, blur=8.0, ease='out_expo', fade=0.5):
        p = K.ramp(t, t0, t0 + dur, ease)
        pf = K.ramp(t, t0, t0 + dur * fade, 'out_cubic')
        c = (self.n - 1) / 2
        out = []
        for i in range(self.n):
            out.append(GlyphState(dx=(i - c) * amount * self.style.px * (1 - p), opacity=pf, blur=(1 - p) * blur))
        return out, {}

    def _a_flip(self, t, t0=0.0, stagger=0.05, dur=0.6, from_angle=-100.0, ease='out_back', order='ltr',
                lift=0.15):
        rk = self._rank(order)
        out = []
        for i in range(self.n):
            ts_ = t0 + rk[i] * stagger
            p = K.ramp(t, ts_, ts_ + dur, ease)
            pl = K.ramp(t, ts_, ts_ + dur, 'out_cubic')
            op = K.ramp(t, ts_, ts_ + dur * 0.35, 'out_cubic')
            out.append(GlyphState(rx=from_angle * (1 - p), dy=(1 - pl) * lift * self.style.px, opacity=op))
        return out, {}

    def _a_scramble(self, t, t0=0.0, dur=0.7, stagger=0.04, rate=22.0, charset=None, order='ltr', seed=3):
        charset = charset or 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789#%&?'
        if self.items and self.items[0].ch.islower():
            charset = charset.lower()
        rk = self._rank(order)
        out = []
        for i in range(self.n):
            ts_ = t0 + rk[i] * stagger
            tr = ts_ + dur
            if t < ts_:
                out.append(GlyphState(opacity=0.0))
            elif t < tr:
                k = int((t - ts_) * rate)
                h = (math.sin((i * 31 + k * 7 + seed) * 12.9898) * 43758.5453) % 1.0
                ch = charset[int(h * len(charset)) % len(charset)]
                out.append(GlyphState(alt=ch, opacity=0.55 + 0.45 * K.ramp(t, ts_, ts_ + 0.08)))
            else:
                p = K.ramp(t, tr, tr + 0.12, 'out_cubic')
                s = K.lerp(1.08, 1.0, p)
                out.append(GlyphState(sx=s, sy=s))
        return out, {}

    # ---------------------------------------------------------------- convenience animators
    def _run(self, kind, cv, t, x, y, kw):
        dkw = {k: kw.pop(k) for k in list(kw) if k in self.DRAW_KEYS}
        mbl = dkw.pop('mblur', 0)
        span = dkw.pop('mspan', None)
        if kind == 'slam' and kw.pop('smear', True):
            mbl = max(mbl, 1) if mbl else 'auto'
            span = span or 2.2 / K.FPS
        if mbl:
            span = span or 1.0 / K.FPS
            if mbl == 'auto':
                a = self.anim(kind, t, **dict(kw))
                b = self.anim(kind, t - span, **dict(kw))
                px = self._motion_px(a, b) * (dkw.get('scale', 1.0) if not isinstance(dkw.get('scale', 1.0),
                                                                                          tuple) else 1.0)
                mbl = int(np.clip(px / 2.5, 1, 24))
            if mbl > 1:
                subs = [self.anim(kind, t - span * (1 - (j + 0.5) / mbl), **dict(kw)) for j in range(int(mbl))]
                return self._render_avg(cv, subs, x, y, **dkw)
        states, blk = self.anim(kind, t, **kw)
        return self.render(cv, states, x, y, block=blk, **dkw)

    def _motion_px(self, a, b):
        """Rough max screen displacement (px) between two animator results (for adaptive smear samples)."""
        (sa, ba), (sb, bb) = a, b
        R = max(self.w, self.h) / 2
        m = abs(ba.get('scale', 1.0) - bb.get('scale', 1.0)) * R
        m = max(m, abs(ba.get('dx', 0) - bb.get('dx', 0)), abs(ba.get('dy', 0) - bb.get('dy', 0)))
        for p, q in zip(sa, sb):
            m = max(m, abs(p.dx - q.dx), abs(p.dy - q.dy), abs(p.sx - q.sx) * self.style.px,
                    abs(p.rx - q.rx) * 0.01 * self.style.px)
        return m

    def rise(self, cv, t, x, y, **kw):
        """Staggered per-glyph rise with blur-in and scale (t0, stagger, dur, dist em, blur, scale0, order)."""
        return self._run('rise', cv, t, x, y, kw)

    def slam(self, cv, t, x, y, **kw):
        """Block slam: scale s0 -> 1 with spring overshoot and a motion smear (t0, s0, dur, smear, stagger)."""
        return self._run('slam', cv, t, x, y, kw)

    def typewriter(self, cv, t, x, y, **kw):
        """Glyphs pop on at cps chars / s with a blinking caret (t0, cps, caret)."""
        return self._run('typewriter', cv, t, x, y, kw)

    def wipe(self, cv, t, x, y, **kw):
        """Soft-edged mask wipe across the block with a bright leading edge (t0, dur, angle, soft, edge)."""
        return self._run('wipe', cv, t, x, y, kw)

    def track(self, cv, t, x, y, **kw):
        """Tracking expand: spread glyphs settle to their kerned positions (t0, dur, amount em, blur)."""
        return self._run('track', cv, t, x, y, kw)

    def flip(self, cv, t, x, y, **kw):
        """Per-glyph 3D rotateX flip-in (t0, stagger, dur, from_angle, order)."""
        return self._run('flip', cv, t, x, y, kw)

    def scramble(self, cv, t, x, y, **kw):
        """Decode: random characters resolve into the text (t0, dur, stagger, rate, charset)."""
        return self._run('scramble', cv, t, x, y, kw)

    # ---------------------------------------------------------------- rendering
    def _render_avg(self, cv, subs, x, y, **dkw):
        """Motion smear: composite each sub-sample normally into its own (lazily zeroed) buffer, average the
        premultiplied results, then lay the average over the canvas (exact temporal box filter)."""
        # one scratch canvas + one accumulator for all sub-samples; only the touched bbox is cleared / summed
        # (the old version allocated two full 1080x1920 float buffers per sub-sample: ~33 MB each, x24 on a slam)
        acc = np.zeros_like(cv)
        tmp = np.zeros_like(cv)
        bb = None
        w = np.float32(1.0 / len(subs))
        for states, blk in subs:
            b = self.render(tmp, states, x, y, block=blk, **dkw)
            if b is None:
                continue
            x0, y0, x1, y1 = [int(v) for v in b]
            acc[y0:y1, x0:x1] += tmp[y0:y1, x0:x1] * w
            tmp[y0:y1, x0:x1] = 0.0
            bb = _bb_union(bb, b)
        if bb is None:
            return None
        x0, y0, x1, y1 = [int(v) for v in bb]
        K.over(cv[y0:y1, x0:x1], acc[y0:y1, x0:x1])
        return bb

    def render(self, cv, states, x, y, block=None, anchor=(0.5, 0.5), scale=1.0, rot=0.0, opacity=1.0, tilt=None,
               focal=1600.0, sweep=None, sweep_kw=None, blur=0.0, _accum=None):
        """Draw glyph states with the block anchor at (x, y). tilt=(rx, ry, rz) tilts the block in 3D."""
        _accum = None          # (ignored: smears composite each sub-sample normally, see _render_avg)
        blk = dict(block or {})
        scale = scale * blk.get('scale', 1.0)
        opacity = opacity * blk.get('opacity', 1.0)
        blur = blur + blk.get('blur', 0.0)
        x, y = x + blk.get('dx', 0.0), y + blk.get('dy', 0.0)
        if opacity <= 1e-4:
            return None
        mode_over = 'over' if _accum is None else 'add'
        op_k = opacity if _accum is None else opacity * _accum
        ax, ay = anchor[0] * self.w, anchor[1] * self.h
        Rt = _rotm(*tilt) if tilt is not None and any(abs(v) > 1e-6 for v in tilt) else None
        all_id = all(s.identity() for s in states)
        wipe = blk.get('wipe')
        # ---- settled but tilted: the block is planar, so map its box corners (exact homography)
        if all_id and Rt is not None and wipe is None and _accum is None:
            q = self._project_box(x, y, ax, ay, scale, rot, Rt, focal)
            bb = self.block.draw_quad(cv, q, opacity=op_k, blur=blur, sweep=sweep, sweep_kw=sweep_kw)
            if 'caret' in blk:
                Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [self.w, 0], [self.w, self.h], [0, self.h]]),
                                                 np.float32(q)).astype(np.float64)

                def mp(P, Hm=Hm):
                    c = np.c_[P, np.ones(len(P))] @ Hm.T
                    return c[:, :2] / c[:, 2:3]
                bb = _bb_union(bb, self._caret(cv, blk['caret'], mp, op_k, mode_over))
            return bb
        # ---- settled: draw the exact whole-block sprite
        if all_id and Rt is None:
            ts = self.block
            layers = ts._layers(None, sweep, sweep_kw)
            if wipe is not None:
                layers = _wipe_layers(ts, layers, *wipe)
            r = math.radians(rot)
            c, s = math.cos(r), math.sin(r)
            M = np.array([[c * scale, -s * scale, 0.0], [s * scale, c * scale, 0.0]])
            M[0, 2] = x - (M[0, 0] * ax + M[0, 1] * ay)
            M[1, 2] = y - (M[1, 0] * ax + M[1, 1] * ay)
            if rot == 0 and abs(scale - 1) < 1e-9 and _accum is None:
                M[0, 2], M[1, 2] = round(M[0, 2]), round(M[1, 2])
            bb = _draw_layers_affine(cv, layers, M, op_k, blur, None if _accum is None else 'add')
            if 'caret' in blk:
                bb = _bb_union(bb, self._caret(cv, blk['caret'], lambda p: p @ M[:, :2].T + M[:, 2], op_k,
                                               mode_over))
            return bb
        # ---- per glyph (a block pill, if any, is drawn first with the block transform)
        boxes = self.boxes()
        pill_bb = None
        if self.style.pill > 0:
            pls = [L for L in self.block.layers if L.part == 'pill']
            pop = float(np.mean([st_.opacity for st_ in states])) if states else 1.0
            if Rt is None:
                cr0, sr0 = math.cos(math.radians(rot)), math.sin(math.radians(rot))
                M = np.array([[cr0 * scale, -sr0 * scale, x - (cr0 * ax - sr0 * ay) * scale],
                              [sr0 * scale, cr0 * scale, y - (sr0 * ax + cr0 * ay) * scale]])
                pill_bb = _draw_layers_affine(cv, pls, M, op_k * pop, blur, None if _accum is None else 'add')
            else:
                q = self._project_box(x, y, ax, ay, scale, rot, Rt, focal)
                Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [self.w, 0], [self.w, self.h], [0, self.h]]),
                                                 np.float32(q)).astype(np.float64)
                pill_bb = _draw_layers_h(cv, pls, Hm, op_k * pop, blur, None if _accum is None else 'add')
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        bb = pill_bb
        jobs = []
        for k, (g, st_) in enumerate(zip(self.items, states)):
            if st_.opacity <= 1e-3:
                continue
            gx0, gy0, gx1, gy1 = boxes[k]
            gc = ((gx0 + gx1) / 2, (gy0 + gy1) / 2)
            if st_.alt is not None:
                ts = self.alt_glyph(st_.alt)
                off = (gc[0] - ts.w / 2, gy0)
                fit = min(1.0, (gx1 - gx0 + 0.12 * self.style.px) / max(ts.w, 1.0))
                if fit < 1:
                    st_ = GlyphState(st_.dx, st_.dy, st_.z, st_.sx * fit, st_.sy, st_.rot, st_.rx, st_.ry,
                                     st_.opacity, st_.blur, st_.alt, st_.sweep, st_.mask)
            else:
                ts = self.glyph(k)
                off = (gx0, gy0)
            gop = st_.opacity
            if wipe is not None:
                gop *= _wipe_glyph_op(wipe, gc, self.w, self.h)
            rg = _rotm(st_.rx, st_.ry, st_.rot) if (st_.rx or st_.ry) else None
            cg, sg = math.cos(math.radians(st_.rot)), math.sin(math.radians(st_.rot))

            def mapper(P, off=off, gc=gc, st_=st_, rg=rg, cg=cg, sg=sg):
                P = np.asarray(P, np.float64)
                rx_ = P[:, 0] + off[0] - gc[0]
                ry_ = P[:, 1] + off[1] - gc[1]
                rx_, ry_ = rx_ * st_.sx, ry_ * st_.sy
                if rg is not None:
                    V = np.c_[rx_, ry_, np.zeros_like(rx_)] @ rg.T
                else:
                    V = np.c_[rx_ * cg - ry_ * sg, rx_ * sg + ry_ * cg, np.zeros_like(rx_)]
                V[:, 0] += gc[0] + st_.dx - ax
                V[:, 1] += gc[1] + st_.dy - ay
                V[:, 2] += st_.z
                if Rt is not None:
                    V = V @ Rt.T
                if Rt is not None or rg is not None or st_.z:
                    f = focal / np.maximum(focal + V[:, 2], 1e-3)
                    V[:, 0] *= f
                    V[:, 1] *= f
                X = V[:, 0] * scale
                Y = V[:, 1] * scale
                return np.c_[x + X * cr - Y * sr, y + X * sr + Y * cr]
            jobs.append((ts, mapper, gop, st_))
        for passes in (('glow', 'back'), ('front',)):
            for ts, mapper, gop, st_ in jobs:
                ls = [L for L in ts.layers if L.part in passes]
                if 'front' in passes:
                    su = st_.sweep if st_.sweep is not None else sweep
                    if su is not None and ts.face is not None:
                        sl = ts.sweep_layer(su, **(sweep_kw or {}))
                        if sl is not None:
                            ls.append(sl)
                for L in ls:
                    q = mapper(L.corners())
                    if _quad_area(q) < 0.5:
                        continue
                    m = L.mode if _accum is None else ('add' if L.mode in ('over', 'add') else L.mode)
                    r = K.draw_quad(cv, L.spr, q, opacity=op_k * gop, mode=m, blur=blur + st_.blur,
                                    frost=L.frost if _accum is None else 0.0)
                    bb = _bb_union(bb, r)
        if 'caret' in blk:
            M = np.array([[cr * scale, -sr * scale, x - (cr * ax - sr * ay) * scale],
                          [sr * scale, cr * scale, y - (sr * ax + cr * ay) * scale]])
            bb = _bb_union(bb, self._caret(cv, blk['caret'], lambda p: p @ M[:, :2].T + M[:, 2], op_k, mode_over))
        return bb

    def _project_box(self, x, y, ax, ay, scale, rot, Rt, focal):
        """Screen quad of the block box under block tilt Rt (perspective focal), scale and rot."""
        P = np.array([[0, 0, 0], [self.w, 0, 0], [self.w, self.h, 0], [0, self.h, 0]], np.float64)
        P[:, 0] -= ax
        P[:, 1] -= ay
        V = P @ Rt.T
        f = focal / np.maximum(focal + V[:, 2], 1e-3)
        X, Y = V[:, 0] * f * scale, V[:, 1] * f * scale
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        return np.c_[x + X * c - Y * s, y + X * s + Y * c]

    def _caret(self, cv, info, mapper, opacity, mode):
        nvis, done, t = info
        if done and (t * 1.6) % 1.0 > 0.55:
            return None
        lay = self.layout
        gl = lay.glyphs
        if nvis <= 0:
            xg, base = (lay.lines[0][0], lay.lines[0][2])
        else:
            g = gl[min(nvis, len(gl)) - 1]
            xg = (g.ink[2] if g.ink is not None else g.x + g.adv) + 0.06 * lay.px
            base = g.base
        wv = max(2.0, 0.07 * lay.px)
        hv = lay.cap * 1.18
        spr = _caret_sprite(int(round(wv)), int(round(hv)), self.style)
        P = np.array([[xg, base - lay.cap * 1.09], [xg + wv, base - lay.cap * 1.09],
                      [xg + wv, base - lay.cap * 1.09 + hv], [xg, base - lay.cap * 1.09 + hv]])
        return K.draw_quad(cv, spr, mapper(P), opacity=opacity, mode=mode)


@functools.lru_cache(maxsize=32)
def _caret_sprite(w, h, st):
    a = K.rrect_alpha(w, h, w / 2, 0)
    c = col(_stops(st.fill)[0][1]) if _stops(st.fill) else col(st.fill)
    if not st.face:
        c = col(st.tube_color)
    return _premul(np.broadcast_to(c * np.float32(max(st.fill_gain, 1.0)), a.shape + (3,)), a)


def _quad_area(q):
    x, y = q[:, 0], q[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def _wipe_coord(angle, W_, H_):
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    ext = abs(W_ / 2 * dx) + abs(H_ / 2 * dy)
    return dx, dy, ext


def _wipe_glyph_op(wipe, gc, W_, H_):
    p, angle, soft, edge = wipe
    dx, dy, ext = _wipe_coord(angle, W_, H_)
    s = ((gc[0] - W_ / 2) * dx + (gc[1] - H_ / 2) * dy) / max(ext, 1e-6) * 0.5 + 0.5
    pos = -soft + p * (1 + 2 * soft)
    return float(np.clip((pos - s) / max(soft, 1e-3) + 0.5, 0, 1))


def _wipe_layers(ts, layers, p, angle, soft, edge):
    """Per-frame masked copies of the block layers (+ a bright edge band on the face)."""
    if p >= 1:
        return layers
    if p <= 0:
        return []
    dx, dy, ext = _wipe_coord(angle, ts.w, ts.h)
    pos = -soft + p * (1 + 2 * soft)
    out = []
    for L in layers:
        x0, y0, x1, y1 = L.box
        hh, ww = L.spr.shape[:2]
        X = x0 + (np.arange(ww, dtype=np.float32) + 0.5) / L.res - ts.w / 2
        Y = y0 + (np.arange(hh, dtype=np.float32) + 0.5) / L.res - ts.h / 2
        s = (X[None, :] * dx + Y[:, None] * dy) / max(ext, 1e-6) * 0.5 + 0.5
        m = np.clip((pos - s) / max(soft, 1e-3) + 0.5, 0, 1).astype(np.float32)
        out.append(Layer(L.spr * m[..., None], L.box, L.res, L.mode, L.frost, L.part))
    if edge > 0 and ts.face is not None:
        sl = ts.sweep_layer(np.clip(p, 0.001, 0.999), width=soft * 0.6 * ts.w / ts.style.px, angle=angle,
                            strength=1.2 * edge, halo=0.0, face=0.9, bevel=1.0)
        if sl is not None:
            # place the band on the wipe edge (sweep param maps u differently: recompute exactly)
            box = sl.box
            hh, ww = sl.spr.shape[:2]
            X = box[0] + np.arange(ww, dtype=np.float32) + 0.5 - ts.w / 2
            Y = box[1] + np.arange(hh, dtype=np.float32) + 0.5 - ts.h / 2
            s = (X[None, :] * dx + Y[:, None] * dy) / max(ext, 1e-6) * 0.5 + 0.5
            band = np.exp(-((s - pos + soft * 0.35) / max(soft * 0.22, 1e-3)) ** 2).astype(np.float32)
            fa = ts.face[1]
            fb = ts.face[0]
            fa_c = fa[box[1] - fb[1]:box[3] - fb[1], box[0] - fb[0]:box[2] - fb[0]]
            spr = np.zeros((hh, ww, 4), np.float32)
            spr[..., :3] = (band * fa_c * 0.9 * edge)[..., None] * col('WHITE')
            out.append(Layer(spr, box, 1.0, 'add', 0.0, 'sweep'))
    return out


# =============================================================================================== orbit text
class OrbitText:
    """Glyphs on a tilted 3D circle around a centre, facing outward (see module docstring).
    tilt: degrees the ring plane is tipped toward the camera (0 = edge-on, 90 = face-on);
    roll: in-plane screen roll of the ring (degrees, clockwise). fill=True repeats the text to wrap the
    full circle with even spacing."""

    def __init__(self, text, st='flat', radius=420.0, tilt=16.0, roll=0.0, fill=True, gap=0.0, repeat=None, **kw):
        # fill: True/False = repeat the text round the ring (legacy meaning); any other value is the Style fill
        # colour (and the text repeats). repeat= overrides the repeat flag explicitly.
        if not isinstance(fill, (bool, np.bool_)) and fill is not None:
            kw['fill'] = fill
            fill = True
        if repeat is not None:
            fill = bool(repeat)
        self.g = Glyphs(text, st, **kw)
        self.radius, self.tilt, self.roll = float(radius), float(tilt), float(roll)
        lay = self.g.layout
        self.cap = lay.cap
        adv = []
        for gl in lay.glyphs:
            adv.append(gl.adv + lay.tracking * lay.px)
        tot = sum(adv) + gap * lay.px
        circ = 2 * math.pi * self.radius
        reps = max(1, int(circ // max(tot, 1))) if fill else 1
        k = circ / (tot * reps) if fill else 1.0
        self.slots = []                      # (glyph index into g.items, theta)
        idx = {g.i: n for n, g in enumerate(self.g.items)}
        s = 0.0
        for r in range(reps):
            for gi, gl in enumerate(lay.glyphs):
                a = adv[gi] * k
                if gl.ink is not None:
                    cx = (gl.ink[0] + gl.ink[2]) / 2 - gl.x            # glyph ink centre from its pen
                    self.slots.append((idx[gl.i], (s + cx * k) / self.radius))
                s += a
            s += gap * lay.px * k

    def items(self, cam, center=(0, 0, 0), t=0.0, spin=20.0, phase=0.0, scale=1.0):
        """Per-glyph ring placement (unsorted): [(depth, glyph index, P, T, U, facing, box)] with world
        position P, tangent T, up U and facing = cos(angle between the glyph normal and the camera)."""
        R = _rotm(self.tilt, 0, self.roll)
        C = np.asarray(center, np.float64)
        out = []
        boxes = self.g.boxes()
        for gi, th0 in self.slots:
            th = th0 - math.radians(spin * t + phase)
            P = C + R @ np.array([self.radius * scale * math.sin(th), 0.0, -self.radius * scale * math.cos(th)])
            T = R @ np.array([math.cos(th), 0.0, math.sin(th)])
            U = R @ np.array([0.0, -1.0, 0.0])
            N = R @ np.array([math.sin(th), 0.0, -math.cos(th)])
            to_cam = np.asarray(cam.pos, np.float64) - P
            facing = float(np.dot(N, to_cam / max(np.linalg.norm(to_cam), 1e-9)))
            depth = float(cam.depth(P))
            out.append((depth, gi, P, T, U, facing, boxes[gi]))
        return out

    def draw(self, cv, cam, center=(0, 0, 0), t=0.0, spin=20.0, phase=0.0, part='all', back_opacity=0.35,
             back_blur=5.0, dof=True, opacity=1.0, scale=1.0, sweep=None):
        its = self.items(cam, center, t, spin, phase, scale)
        its.sort(key=lambda it: -it[0])
        bb = None
        for depth, gi, P, T, U, facing, box in its:
            front = facing > 0
            if (part == 'back' and front) or (part == 'front' and not front):
                continue
            bb = _bb_union(bb, self._draw_one(cv, cam, gi, P, T, U, facing, box, back_opacity, back_blur, dof,
                                              opacity, scale, sweep))
        return bb

    def _draw_one(self, cv, cam, gi, P, T, U, facing, box, back_opacity, back_blur, dof, opacity, scale, sweep):
        ts = self.g.glyph(gi)
        gx0, gy0, gx1, gy1 = box
        gcx, gcy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
        k = smooth01((facing + 0.25) / 0.5)
        op = opacity * K.lerp(back_opacity, 1.0, k)
        bl = back_blur * (1 - k)
        depth = float(cam.depth(P))
        if dof and cam.aperture > 0:
            bl += 0.5 * float(cam.coc(depth))
        bb = None
        layers = [ts.merged()]
        if sweep is not None and facing > 0:
            sl = ts.sweep_layer(sweep)
            if sl is not None:
                layers.append(sl)
        for L in layers:
            C = L.corners()
            loc_x = (C[:, 0] + gx0 - gcx) * scale
            loc_y = (C[:, 1] + gy0 - gcy) * scale
            Wp = P[None, :] + loc_x[:, None] * T[None, :] - loc_y[:, None] * U[None, :]
            xy, z = cam.project(Wp)
            if np.isnan(z).any() or (z < cam.near).any():
                continue
            if _quad_area(xy) < 0.5:
                continue
            bb = _bb_union(bb, K.draw_quad(cv, L.spr, xy, opacity=op, mode=L.mode, blur=bl))
        return bb

    def add_to_scene(self, sc, center=(0, 0, 0), t=0.0, spin=20.0, phase=0.0, back_opacity=0.35, back_blur=5.0,
                     dof=True, opacity=1.0, scale=1.0):
        """Register each glyph as a depth-sorted custom item in a core.Scene."""
        for depth, gi, P, T, U, facing, box in self.items(sc.cam, center, t, spin, phase, scale):
            sc.custom(P, (lambda cv, cam, gi=gi, P=P, T=T, U=U, facing=facing, box=box:
                          self._draw_one(cv, cam, gi, P, T, U, facing, box, back_opacity, back_blur, dof, opacity,
                                         scale, None)))
        return sc


def smooth01(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# =============================================================================================== counter
class Counter:
    """Tabular-figure number renderer with odometer / slot-machine digit rolls and per-digit vertical motion
    blur (see module docstring). The style's glow is applied once to the composed number."""

    def __init__(self, st='flat', prefix='\u00a3', suffix='', decimals=2, sep=',', point='.', min_int=1,
                 blur_cap=0.12, **kw):
        self.style = style(st, **kw)
        self.prefix, self.suffix, self.decimals = prefix, suffix, decimals
        # max per-digit vertical blur sigma as a fraction of the cap height. Physically a wheel spinning faster
        # than ~1 digit per shutter averages into a flat bar (the old fixed 0.26 looked like a barcode); 0.12 keeps
        # every digit legible as a gold streak, the usual motion-design cheat.
        self.blur_cap = float(blur_cap)
        self.sep, self.point, self.min_int = sep, point, min_int
        s = self.style
        self._ds = s.but(glow=0.0, scrim=0.0)
        fn = font_name(s.font)
        self._glyph = {}
        for d in '0123456789':
            self._prep(d)
        advs = [_gmet(fn, str(d))[0] * s.px / _REF for d in range(10)]
        self.cell = max(advs) + s.tracking * s.px
        self.cap = render('0', self._ds).h
        # vertical ink extent of the digits relative to the cap box (extrusion / shadow hang below)
        ys = [self._glyph[d][2] for d in '0123456789']
        self.top = min(y for y, _ in ys)
        self.bot = max(y for _, y in ys)
        self.pitch = self.cap * ((self.bot - self.top) + 0.12)

    def _prep(self, ch):
        g = self._glyph.get(ch)
        if g is None:
            ts = render(ch, self._ds)
            spr = ts.sprite
            an = ts.sprite_anchor((0.5, 0.5))
            # visible ink extent (rows with alpha) in cap units relative to the cap-box top
            rows = np.nonzero(spr[..., 3].max(1) > 0.02)[0]
            r0, r1 = (rows[0], rows[-1] + 1) if len(rows) else (0, spr.shape[0])
            y_top = 0.5 * ts.h - an[1] * spr.shape[0]
            g = self._glyph[ch] = (spr, an, ((y_top + r0) / ts.h, (y_top + r1) / ts.h))
        return g

    def _adv(self, ch):
        s = self.style
        return _gmet(font_name(s.font), ch)[0] * s.px / _REF + s.tracking * s.px

    def _slots(self, value, ndig=None):
        """[(kind, payload, width, presence)] left to right."""
        v = max(0.0, float(value))
        ip = int(math.floor(v + 1e-9))
        nint = max(self.min_int, len(str(ip)) if ndig is None else ndig)
        slots = []
        for ch in self.prefix:
            slots.append(('char', ch, self._adv(ch), 1.0))
        for k in range(nint - 1, -1, -1):
            pres = 1.0 if (k == 0 or ndig is not None) else float(_sstep(0.86, 1.0, v / (10 ** k)))
            slots.append(('digit', k + self.decimals, self.cell, pres))
            if k > 0 and k % 3 == 0 and self.sep:
                slots.append(('char', self.sep, self._adv(self.sep), pres))
        if self.decimals > 0:
            slots.append(('char', self.point, self._adv(self.point), 1.0))
            for j in range(self.decimals - 1, -1, -1):
                slots.append(('digit', j, self.cell, 1.0))
        for ch in self.suffix:
            slots.append(('char', ch, self._adv(ch), 1.0))
        return slots

    def width(self, value):
        return sum(w * p for _, _, w, p in self._slots(value))

    def sprite(self, value, vel=0.0, wheels=None, ndig=None):
        """TextSprite of the number. vel: value units / s (motion blur). wheels: optional {power: (pos 0..10,
        speed digits/s)} overriding the odometer (used by slot())."""
        v = max(0.0, float(value))
        N = v * 10 ** self.decimals
        dN = abs(vel) * 10 ** self.decimals
        slots = self._slots(v, ndig)
        tot = sum(w * p for _, _, w, p in slots)
        s = self.style
        cap = self.cap
        mx = int(math.ceil(0.25 * s.px + s.depth * s.px)) + 4
        my0 = int(math.ceil(max(0.0, -self.top) * cap)) + 4
        my1 = int(math.ceil(max(0.0, self.bot - 1) * cap)) + 4
        Wt = int(math.ceil(tot)) + 2 * mx
        Ht = int(math.ceil(cap)) + my0 + my1
        out = np.zeros((Ht, Wt, 4), np.float32)
        x = float(mx)
        expo = 0.5 / K.FPS
        yy = (np.arange(Ht, dtype=np.float32) + 0.5 - my0) / cap
        w0, w1 = self.top - 0.03, self.bot + 0.03
        win = (_sstep(w0, w0 + 0.12, yy) * (1 - _sstep(w1 - 0.12, w1, yy))).astype(np.float32)
        for kind, pay, wd, pres in slots:
            w_eff = wd * pres
            if pres <= 1e-3:
                continue
            cx = x + w_eff / 2
            if kind == 'char':
                spr, an, _ = self._prep(pay)
                K.draw(out, spr, cx, my0 + cap / 2, anchor=an, opacity=pres)
            else:
                k = pay
                if wheels is not None and k in wheels:
                    p, spd = wheels[k]
                else:
                    wk = N / 10 ** k
                    spd = dN / 10 ** k
                    if spd * expo > 0.3:
                        p = wk % 10.0
                    else:
                        r = (N % (10 ** k)) if k > 0 else 0.0
                        f = float(np.clip(r - (10 ** k - 1), 0, 1)) if k > 0 else (wk % 1.0)
                        p = (math.floor(wk) % 10) + f
                        if k > 0 and 0 < f < 1:
                            spd = max(spd, dN)
                cw = int(math.ceil(w_eff)) + 2 * mx
                colb = np.zeros((Ht, cw, 4), np.float32)
                ccx = mx + w_eff / 2
                a = int(math.floor(p)) % 10
                fr = p - math.floor(p)
                for dd, off in ((a, -fr), ((a + 1) % 10, 1 - fr), ((a - 1) % 10, -fr - 1)):
                    if abs(off) > 1.2:
                        continue
                    spr, an, _ = self._prep(str(dd))
                    K.draw(colb, spr, ccx, my0 + cap / 2 + off * self.pitch, anchor=an)
                sig = min(cap * self.blur_cap, spd * expo * self.pitch * 0.5)
                if sig > 0.6:
                    colb = cv2.GaussianBlur(colb, (1, int(sig * 6) | 1), sigmaX=0, sigmaY=sig)
                if sig > 0.6:
                    sf = 0.12 + 0.9 * sig / cap                 # softer window edges while spinning fast
                    wv = (_sstep(w0, w0 + sf, yy) * (1 - _sstep(w1 - sf, w1, yy))).astype(np.float32)
                else:
                    wv = win
                colb *= (wv * pres)[:, None, None]
                x0i = int(round(x - mx))
                xs0, xs1 = max(0, x0i), min(Wt, x0i + cw)
                if xs1 > xs0:
                    _over_into(out[:, xs0:xs1], colb[:, xs0 - x0i:xs1 - x0i])
            x += w_eff
        lay = _CounterLayout(tot, cap)
        box = (-mx, -my0, -mx + Wt, -my0 + Ht)
        layers = [Layer(out, box, 1.0, 'over', 0.0, 'front')]
        if s.glow > 0:
            layers.extend(_glow_layers(s, s.px, box, out[..., 3], out[..., 3]))
        return TextSprite(lay, s, layers, None)

    def draw(self, cv, value, x, y, anchor=(0.5, 0.5), scale=1.0, rot=0.0, vel=0.0, opacity=1.0, blur=0.0,
             ndig=None):
        """Odometer: draw `value` (vel = value units per second for the per-digit motion blur)."""
        return self.sprite(value, vel, ndig=ndig).draw(cv, x, y, anchor, scale, rot, opacity, blur, snap=False)

    def slot(self, cv, t, target, x, y, t0=0.0, dur=1.4, stagger=0.09, spins=2, order='rtl', anchor=(0.5, 0.5),
             scale=1.0, opacity=1.0, ease='out_cubic'):
        """Slot-machine: every digit reel spins and lands on `target` (staggered, small overshoot)."""
        return self.slot_sprite(t, target, t0, dur, stagger, spins, order, ease).draw(
            cv, x, y, anchor, scale, 0.0, opacity, snap=False)

    def slot_sprite(self, t, target, t0=0.0, dur=1.4, stagger=0.09, spins=2, order='rtl', ease='out_cubic'):
        v = float(target)
        N = int(round(v * 10 ** self.decimals))
        nint = max(self.min_int, len(str(int(math.floor(v + 1e-9)))))
        nd = nint + self.decimals
        wheels = {}
        e = K.get_ease(ease)
        for k in range(nd):
            rank = k if order == 'rtl' else nd - 1 - k
            ts_ = t0 + rank * stagger
            u = float(np.clip((t - ts_) / dur, 0, 1))
            tgt = (N // 10 ** k) % 10
            total = spins * 10 + tgt
            p = total * float(e(u))
            spd = (total * (float(e(min(1.0, u + 0.01))) - float(e(u))) / (0.01 * dur)) if u < 1 else 0.0
            if u >= 1:
                tl = t - (ts_ + dur)
                p = total + (0.12 * math.exp(-tl * 10) * math.sin(tl * 32) if tl < 0.5 else 0.0)
            wheels[k] = (p % 10.0, abs(spd))
        return self.sprite(v, 0.0, wheels=wheels, ndig=nint)


class _CounterLayout:
    def __init__(self, w, h):
        self.w, self.h, self.cap, self.px = w, h, h, h
        self.lines = [(0, w, h)]
        self.glyphs = []
        self.line_height = 1.0


# =============================================================================================== video in type
class VideoType:
    """Footage seen through giant letters (+ rim/bevel overlay and a back layer). See module docstring."""

    def __init__(self, text, font='Nunito-Black', px=250.0, tracking=-0.01, rim_style=None, back_style=None,
                 line_height=1.0, look='dark'):
        fn = font_name(font)
        self.text = text
        self.px = px
        self.layout = layout(text, fn, px, tracking, line_height, 'center', 0.0)
        self.w, self.h = self.layout.w, self.layout.h
        base = Style(name='video_mask', font=fn, px=px, tracking=tracking, line_height=line_height)
        mask_ts = render(text, base.but(fill='WHITE'))
        L = mask_ts.layers[0]
        self.mask_box = L.box
        self.mask = np.ascontiguousarray(L.spr[..., 3])
        self._mask4 = np.repeat(self.mask[..., None], 4, axis=2).astype(np.float32)
        rim_style = rim_style or base.but(
            name='video_rim', fill='WHITE', bevel=0.03, profile='round', ambient=1.0, spec=0.0, rim=0.0)
        self.rim = _rim_overlay(text, rim_style)
        if back_style is None and look == 'light':
            back_style = base.but(name='video_back_light', fill='INK', depth=0.06, angle=-70, persp=0.05,
                                  side=(('#7A2E68', 1.0), ('#3A1436', 1.0)), side_rim=0.35, side_key=0.5,
                                  side_ambient=0.5, rim_color=('PEACH', 1.0), edge_rim=0.5, side_falloff=0.0,
                                  shadow=0.28, shadow_color='#5B2E52', shadow_offset=(0.0, 0.08),
                                  shadow_blur=0.09, long_shadow=0.22, long_shadow_len=0.4,
                                  long_shadow_color='#8A5070')
        back_style = back_style or base.but(name='video_back', fill='NIGHT_0', depth=0.07, angle=-70, persp=0.06,
                                            side=(('#4A1242', 1.0), ('#0B0310', 1.0)), side_rim=0.45,
                                            edge_rim=0.9, rim_color=('ORANGE', 1.3), side_falloff=0.0, shadow=0.5,
                                            shadow_offset=(0.0, 0.08), shadow_blur=0.08, glow=0.35,
                                            glow_color=('MAGENTA', 1.5), glow_src='all')
        bt = render(text, back_style)
        self.back = TextSprite(bt.layout, bt.style, [L_ for L_ in bt.layers if L_.part in ('back', 'glow')], None)
        self.face = TextSprite(self.layout, base, [], self.rim.face)

    def _M(self, x, y, anchor, scale, rot):
        ax, ay = anchor[0] * self.w, anchor[1] * self.h
        r = math.radians(rot)
        c, s = math.cos(r), math.sin(r)
        M = np.array([[c * scale, -s * scale, 0.0], [s * scale, c * scale, 0.0]])
        M[0, 2] = x - (M[0, 0] * ax + M[0, 1] * ay)
        M[1, 2] = y - (M[1, 0] * ax + M[1, 1] * ay)
        return M

    def mask_canvas(self, x, y, anchor=(0.5, 0.5), scale=1.0, rot=0.0, shape=(K.H, K.W)):
        """(H, W) float32 alpha of the letters on the canvas."""
        M = self._M(x, y, anchor, scale, rot)
        tmp = np.zeros(shape + (4,), np.float32)
        q = Layer(self._mask4, self.mask_box).corners() @ M[:, :2].T + M[:, 2]
        K.draw_quad(tmp, self._mask4, q)
        return tmp[..., 3]

    def draw(self, cv, footage, x, y, anchor=(0.5, 0.5), scale=1.0, rot=0.0, opacity=1.0, lock='screen', rim=1.0,
             back=1.0, sweep=None, sweep_kw=None, blur=0.0):
        """Composite footage through the letters. lock='screen': footage is a canvas-sized sprite;
        lock='text': footage is cover-fitted to the text box and moves with it."""
        M = self._M(x, y, anchor, scale, rot)
        bb = None
        if back > 0:
            bb = _bb_union(bb, _draw_layers_affine(cv, self.back.layers, M, opacity * back, blur, None))
        q = Layer(self._mask4, self.mask_box).corners() @ M[:, :2].T + M[:, 2]
        if lock == 'screen':
            x0 = int(max(0, math.floor(q[:, 0].min()) - 2))
            y0 = int(max(0, math.floor(q[:, 1].min()) - 2))
            x1 = int(min(cv.shape[1], math.ceil(q[:, 0].max()) + 2))
            y1 = int(min(cv.shape[0], math.ceil(q[:, 1].max()) + 2))
            if x1 > x0 and y1 > y0:
                reg = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
                K.draw_quad(reg, self._mask4, q - [x0, y0], blur=blur)
                m = reg[..., 3:4]
                fg = footage[y0:y1, x0:x1]
                if fg.shape[:2] != m.shape[:2]:
                    fg = cv2.resize(footage, (cv.shape[1], cv.shape[0]))[y0:y1, x0:x1]
                src = fg * m
                K.over(cv[y0:y1, x0:x1], src, opacity)
                bb = _bb_union(bb, (x0, y0, x1, y1))
        else:
            bx0, by0, bx1, by1 = self.mask_box
            hh, ww = self.mask.shape
            fh, fw = footage.shape[:2]
            sc_ = max(ww / fw, hh / fh)
            rs = cv2.resize(footage, (max(ww, int(math.ceil(fw * sc_))), max(hh, int(math.ceil(fh * sc_)))),
                            interpolation=cv2.INTER_AREA if sc_ < 1 else cv2.INTER_LINEAR)
            oy, ox = (rs.shape[0] - hh) // 2, (rs.shape[1] - ww) // 2
            spr = rs[oy:oy + hh, ox:ox + ww] * self.mask[..., None]
            bb = _bb_union(bb, K.draw_quad(cv, np.ascontiguousarray(spr, np.float32), q, opacity=opacity, blur=blur))
        if rim > 0:
            bb = _bb_union(bb, _draw_layers_affine(cv, self.rim.layers, M, opacity * rim, blur, None))
        if sweep is not None:
            sl = self.face.sweep_layer(sweep, **(sweep_kw or {}))
            if sl is not None:
                bb = _bb_union(bb, _draw_layers_affine(cv, [sl], M, opacity, blur, None))
        return bb

    def glyph_index(self, char=None, index=None):
        gl = [g for g in self.layout.glyphs if g.ink is not None]
        if index is not None:
            return gl[index]
        for g in gl:
            if g.ch == char:
                return g
        raise KeyError(char)

    def zoom_point(self, char='U', index=None, kind='stroke'):
        """Block-coords point inside a letter: kind='stroke' -> thickest point of its ink (zoom INTO the
        footage); 'counter' -> centre of the counter / bowl (zoom THROUGH the hole)."""
        g = self.glyph_index(char, index)
        x0, y0, x1, y1 = g.ink
        bx0, by0 = self.mask_box[0], self.mask_box[1]
        X0, Y0 = int(math.floor(x0 - bx0)), int(math.floor(y0 - by0))
        X1, Y1 = int(math.ceil(x1 - bx0)), int(math.ceil(y1 - by0))
        crop = self.mask[Y0:Y1, X0:X1]
        # isolate this glyph from neighbours that may overlap the box
        own = (_raster(self.layout, 1, (int(math.floor(x0)), int(math.floor(y0)), int(math.ceil(x1)),
                                        int(math.ceil(y1))), only={g.i}) > 0.5)
        ink = own if own.shape == crop.shape else (crop > 0.5)
        if kind == 'counter':
            free = np.pad((~ink).astype(np.uint8), 1, constant_values=0)
            dt = cv2.distanceTransform(free, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)[1:-1, 1:-1]
        else:
            dt = cv2.distanceTransform(np.pad(ink.astype(np.uint8), 1), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)[1:-1, 1:-1]
        # prefer the horizontal centre of the glyph on ties (symmetric letters)
        hh, ww = dt.shape
        bias = (1 - 0.03 * np.abs(np.arange(ww) - ww / 2)[None, :] / max(ww, 1)
                - 0.03 * np.abs(np.arange(hh) - hh / 2)[:, None] / max(hh, 1))
        iy, ix = np.unravel_index(np.argmax(dt * bias), dt.shape)
        return float(x0 + ix + 0.5), float(y0 + iy + 0.5)

    def zoom(self, u, point, x, y, anchor=(0.5, 0.5), s0=1.0, s1=40.0, target=(K.CX, K.CY), ease='in_expo',
             move_ease='inout_cubic'):
        """Zoom-through transform at progress u: returns dict(x, y, anchor, scale) for draw()/mask_canvas()."""
        e = float(K.get_ease(ease)(np.clip(u, 0, 1)))
        em = float(K.get_ease(move_ease)(np.clip(u, 0, 1)))
        ax, ay = anchor[0] * self.w, anchor[1] * self.h
        p0 = (x + (point[0] - ax) * s0, y + (point[1] - ay) * s0)
        sc = s0 * (s1 / s0) ** e
        px_, py_ = K.lerp(p0[0], target[0], em), K.lerp(p0[1], target[1], em)
        return {'x': px_, 'y': py_, 'anchor': (point[0] / self.w, point[1] / self.h), 'scale': sc}


def _rim_overlay(text, st):
    """Bevel highlight + inner shadow + thin bright edge, as an overlay for footage-filled letters."""
    key = ('rim', text, st)

    def make():
        lay = layout(text, font_name(st.font), st.px, st.tracking, st.line_height, st.align, st.max_width)
        L = st.px
        ss = st.ss or 2
        pad = 6
        ix0, iy0, ix1, iy1 = lay.ink
        region = (int(math.floor(ix0)) - pad, int(math.floor(iy0)) - pad, int(math.ceil(ix1)) + pad,
                  int(math.ceil(iy1)) + pad)
        A = _raster(lay, ss, region)
        d = _sdf(A) / np.float32(ss)
        gx, gy = _grad(d)
        bev = st.bevel * L
        x = np.clip(d / bev, 0, 1)
        slope = np.clip((1 - x) / np.sqrt(np.maximum(1 - (1 - x) ** 2, 1e-3)), 0, 4.0)
        nx, ny = -slope * gx, -slope * gy
        nn = np.sqrt(nx * nx + ny * ny + 1)
        nx, ny, nz = nx / nn, ny / nn, 1 / nn
        Lv = _norm3(st.light)
        ndl = nx * Lv[0] + ny * Lv[1] + nz * Lv[2]
        hi = np.clip(ndl - Lv[2], 0, None) * 2.2 * A                        # lit bevel facets
        lo = np.clip(Lv[2] - ndl, 0, None) * 1.4 * A                        # facets turned away
        rd = np.array([0.8, 0.6])
        rd /= np.linalg.norm(rd)
        rimk = (1 - nz) * np.clip(nx * rd[0] + ny * rd[1], 0, None) * A
        edge = np.clip(1.2 - np.abs(d) * ss, 0, 1) * 0.0
        inner = _blur(1 - _shift(A, 0, 0.03 * L * ss), 0.05 * L * ss) * A * 0.42
        dark = np.clip(lo * 0.45 + inner, 0, 0.7)
        rgb = (col('WHITE') * (hi * 1.3)[..., None] + col(('HOT_PINK', 1.4)) * (rimk * 1.2)[..., None]
               + col('WHITE') * edge[..., None])
        # premultiplied: darkening via alpha with black, light via emissive rgb
        spr = np.dstack([rgb, dark]).astype(np.float32)
        spr1 = _down(spr, ss)
        bw1 = _down(np.clip((1 - nz) * 3, 0, 1) * A, ss)
        A1 = _down(A, ss)
        return TextSprite(lay, st, [Layer(spr1, region, 1.0, 'over', 0.0, 'front')], (region, A1, bw1))
    return _CACHE.get(key, make)


# =============================================================================================== self-test
_SAMPLE_ROWS = {
    'night': [
        ('extrude3d', 'Could YOU', dict(px=168, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, fill_gain=1.2),
         0.62),
        ('chrome', 'NURTURE', dict(px=150), 0.4),
        ('deep_glow', 'Financial Support', dict(px=100), None),
        ('neon', 'Start your enquiry', dict(px=86, font='Nunito-ExtraBold'), None),
        ('gradient', 'Foster Carer?', dict(px=118), None),
        ('extrude3d', '\u00a323,275.20', dict(px=120), 0.3),
        ('glass_pill', 'Start your enquiry \u2192', dict(px=44), None),
        ('ui', 'Rates may vary by region and are subject to change.', dict(px=30, font='Poppins-Regular'), None),
    ],
    'amber': [
        ('gold', 'Financial Support', dict(px=118), 0.55),
        ('gold', '\u00a323,275.20', dict(px=150), 0.3),
        ('deep_glow', 'NURTURE', dict(px=140, glow_color=('ORANGE', 2.6), inner_glow_color=('AMBER', 1.3)), None),
        ('neon', 'Start your enquiry', dict(px=86, font='Nunito-ExtraBold', tube_color=('ORANGE', 1.6),
                                            glow_color=('ORANGE', 2.2)), None),
        ('gradient', 'Could YOU', dict(px=130, fill=('ORANGE', 'AMBER'), fill_angle=90,
                                       glow_color=('ORANGE', 1.2)), None),
        ('glass_pill', 'Ages 0\u20134', dict(px=42, font='Poppins-Medium', pill_tint=('ORANGE', 1.4)), None),
        ('ui', 'Estimated allowance \u00b7 52 weeks \u00b7 one child aged 0\u20134', dict(px=32), None),
        ('ui', 'Rates may vary by region and are subject to change.', dict(px=28, font='Poppins-Regular',
                                                                          fill='PEACH'), None),
    ],
    'ivory': [
        ('ink_soft', 'NURTURE', dict(px=190), 0.5),
        ('ink_soft', 'A small beginning', dict(px=104), None),
        ('gradient', 'Financial Support', dict(px=104, shadow=0.22, shadow_color='#7A3A5A', glow=0.0), 0.55),
        ('extrude3d', 'Could YOU', dict(px=130, fill=('MAGENTA', 'ORANGE'), fill_angle=35, fill_gain=1.15, glow=0.0,
                                        shadow=0.22, shadow_color='#5B2E52', side=(('#C23A84', 1.0),
                                                                                  ('#6E1A52', 1.0))), 0.4),
        ('neon', '\u00a323,275.20', dict(px=96, font='Nunito-ExtraBold', tube=0.06, tube_color=('MAGENTA', 1.0),
                                          tube_core=0.35, glow=0.25, glow_color=('HOT_PINK', 0.8)), None),
        ('deep_glow', 'Start your enquiry', dict(px=84, fill=('INK',), fill_gain=1.0, inner_glow=0.0, glow=0.55,
                                                 glow_color=('PEACH', 1.0), glow_radii=(0.06, 0.2, 0.5)), None),
        ('glass_pill_light', 'Start your enquiry \u2192', dict(px=44), None),
        ('ui_ink', 'Rates may vary by region and are subject to change.', dict(px=30, font='Poppins-Regular'),
         None),
    ],
}


def _row_extent(ts):
    b = [L.box for L in ts.layers if L.part in ('front', 'back')]
    if ts.pill_box is not None:
        b.append(ts.pill_box)
    b = np.array(b, np.float64)
    return b[:, 1].min(), b[:, 3].max()


def _styles_sheet(look, name, out):
    """One 1080x1920 sheet: every style on one background with real copy (+ a light sweep on hero rows)."""
    cv = K.background(look, 0.8, intensity=0.9)
    rows = []
    for sty, text, kw, sweep in _SAMPLE_ROWS[name]:
        ts = render(text, sty, **kw)
        rows.append((ts, sweep) + _row_extent(ts))
    tot = sum(r[3] - r[2] for r in rows)
    gap = max(18.0, (1920 - 150 - tot) / (len(rows) + 1))
    y = 75 + gap
    for ts, sweep, e0, e1 in rows:
        ts.draw(cv, 540, y - e0 + ts.h / 2, sweep=sweep)
        y += (e1 - e0) + gap
    cv = K.post(cv, look, 0.8)
    path = os.path.join(out, f'type3d_styles_{name}.png')
    K._write_u8(path, K.to_srgb8(cv, 0.8))
    return path


def _label(u8, text, x=10, y=26, sc=0.6):
    cv2.putText(u8, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, sc, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(u8, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, sc, (255, 255, 255), 1, cv2.LINE_AA)
    return u8


def _sweep_strip(out):
    ts = render('YOU', 'extrude3d', px=230, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, fill_gain=1.2)
    ts2 = render('NURTURE', 'chrome', px=120)
    tiles = []
    times = []
    for u in (0.12, 0.3, 0.45, 0.6, 0.75, 0.9):
        cv = K.background('neon', 0.5)[700:1220, 160:920].copy()
        import time
        t0 = time.perf_counter()
        ts.draw(cv, 380, 200, sweep=u)
        ts2.draw(cv, 380, 430, sweep=u)
        times.append(time.perf_counter() - t0)
        tiles.append(_label(K.to_srgb8(cv), f'sweep u={u:.2f}'))
    img = np.concatenate([np.concatenate(tiles[:3], 1), np.concatenate(tiles[3:], 1)], 0)
    path = os.path.join(out, 'type3d_sweep.png')
    K._write_u8(path, img)
    print('sweep draw (2 words, cached masks) %.1f ms/frame' % (1000 * np.mean(times[1:])))
    return path


def _kinetic_strip(out):
    import time
    anims = [('rise', 'A SAFE HOME.', dict(st='deep_glow', px=96), dict(t0=0.0)),
             ('slam', 'EVERYDAY CARE.', dict(st='extrude3d', px=88, fill=('MAGENTA', 'ORANGE'), fill_angle=35,
                                             fill_gain=1.2), dict(t0=0.02)),
             ('typewriter', 'Start your enquiry', dict(st='ui', px=52), dict(t0=0.0, cps=16)),
             ('wipe', 'Foster Carer?', dict(st='gradient', px=96), dict(t0=0.0, dur=0.7)),
             ('track', 'NURTURE', dict(st='neon', px=96), dict(t0=0.0, dur=0.9)),
             ('flip', 'TO BELONG.', dict(st='chrome', px=96), dict(t0=0.0, tilt=(18, -12, 0))),
             ('scramble', '\u00a3447.60 a week', dict(st='ui', px=64, font='Poppins-Bold'), dict(t0=0.0, dur=0.5))]
    times = [0.1, 0.22, 0.38, 0.6, 1.3]
    rows = []
    for name, text, skw, akw in anims:
        g = Glyphs(text, **skw)
        tiles = []
        for t in times:
            cv = K.new_canvas(K.C['NIGHT_1'], 520, 190)
            K.draw(cv, K.radial(380, K.C['PLUM'] * 0.8), 260, 95, scale=(1.6, 0.6))
            t0 = time.perf_counter()
            getattr(g, name)(cv, t, 260, 95, scale=min(1.0, 470 / g.w), **akw)
            dt = time.perf_counter() - t0
            tiles.append(_label(K.to_srgb8(cv), f'{name}  t={t:.2f}  {dt * 1000:.0f} ms', sc=0.45, y=18))
        rows.append(np.concatenate(tiles, 1))
    img = np.concatenate(rows, 0)
    path = os.path.join(out, 'type3d_kinetic.png')
    K._write_u8(path, img)
    return path


def _orbit_counter_sheet(out):
    import time
    cv = K.background('amber', 1.0)
    # orbit ring around a glowing orb (back half, orb, front half)
    ot = OrbitText('SUPERVISING SOCIAL WORKER \u2022 ONGOING TRAINING \u2022 ', 'flat', px=46, radius=360, tilt=13,
                   roll=-7, fill='IVORY', glow=0.6, glow_color=('ORANGE', 1.8), glow_radii=(0.06, 0.2),
                   glow_weights=(0.8, 0.5))
    cam = K.Cam(pos=(0, -90, -1500), pitch=-3.5, aperture=35)
    ot.draw(cv.copy(), cam, (0, -330, 0), t=0.0, spin=18)          # warm the glyph cache
    t0 = time.perf_counter()
    ot.draw(cv, cam, (0, -330, 0), t=1.0, spin=18, part='back')
    orb = K.glow(K.disc(110, K.C['AMBER'] * 1.6), K.C['ORANGE'], (16, 50, 120), 1.2)
    K.draw_billboard(cv, orb, cam, (0, -330, 0), 260 * orb.shape[1] / 220)
    ot.draw(cv, cam, (0, -330, 0), t=1.0, spin=18, part='front')
    t_orbit = time.perf_counter() - t0
    # counters
    cnt = Counter('gold', px=118)
    cnt.draw(cv.copy(), 1234.5, 540, 900)
    tr = K.Track([(0, 0.0, 'out_expo'), (2.0, 23275.20)])
    t0 = time.perf_counter()
    for i, tt in enumerate((0.25, 0.7, 2.2)):
        cnt.draw(cv, float(tr(tt)), 540, 980 + i * 190, vel=float(tr.vel(tt)), scale=0.92)
    t_cnt = (time.perf_counter() - t0) / 3
    c2 = Counter('flat', px=96, fill='IVORY', glow=0.5, glow_color=('ORANGE', 1.6), glow_radii=(0.05, 0.2),
                 glow_weights=(0.7, 0.4))
    c2.slot(cv, 0.75, 447.60, 300, 1580, t0=0.0, dur=1.0, scale=0.8)
    c2.slot(cv, 2.0, 447.60, 780, 1580, t0=0.0, dur=1.0, scale=0.8)
    render('/ week per child', 'ui', px=34, fill='PEACH').draw(cv, 780, 1660)
    cv = K.post(cv, 'amber', 1.0)
    u8 = K.to_srgb8(cv, 1.0)
    _label(u8, f'orbit {t_orbit * 1000:.0f} ms   counter {t_cnt * 1000:.0f} ms/frame', y=40, sc=0.8)
    path = os.path.join(out, 'type3d_orbit_counter.png')
    K._write_u8(path, u8)
    return path


def _video_sheet(out):
    import time
    import footage as F
    vt = VideoType('NURTURE', px=200, tracking=-0.01, look='light')
    clip = F.Clip('c11')
    fg = clip.get(2.0, K.W, K.H, look='airy')
    pt = vt.zoom_point('U', kind='stroke')
    tiles = []
    for u in (0.0, 0.35, 0.6, 0.8, 0.93, 1.0):
        cv = K.background('airy', 0.5)
        t0 = time.perf_counter()
        z = vt.zoom(u, pt, 540, 900, s1=34)
        vt.draw(cv, fg, sweep=0.5 if u == 0 else None, **z)
        render('A safe home & everyday care', 'ui_ink', px=40).draw(cv, 540, 1030, opacity=1 - min(1, u * 3))
        dt = time.perf_counter() - t0
        u8 = K.to_srgb8(K.post(cv, 'airy', 0.5), 0.5)
        tiles.append(_label(cv2.resize(u8, (360, 640), interpolation=cv2.INTER_AREA),
                            f'zoom u={u:.2f} {dt * 1000:.0f}ms', sc=0.5))
    img = np.concatenate(tiles, 1)
    cv = K.background('neon', 0.5)
    fg2 = F.Clip('c01').get(4.0, K.W, K.H, look='neon')
    vt2 = VideoType('GROW', px=300, tracking=0.0)
    vt2.draw(cv, fg2, 540, 960, sweep=0.55)
    VideoType('NURTURE', px=200, tracking=-0.01).draw(cv, fg, 540, 1350, lock='text', scale=0.9)
    u8 = K.to_srgb8(K.post(cv, 'neon', 0.5), 0.5)[700:1550]
    img2 = cv2.resize(u8, (img.shape[1], int(u8.shape[0] * img.shape[1] / u8.shape[1])), interpolation=cv2.INTER_AREA)
    path = os.path.join(out, 'type3d_video.png')
    K._write_u8(path, np.concatenate([img, img2], 0))
    return path


def _plane_sheet(out):
    """3D placement: draw_plane with perspective + DOF, a tilted kinetic block and a far defocused line."""
    cv = K.background('neon', 1.2)
    cam = K.Cam(pos=(0, 0, -1500), yaw=0, pitch=1, aperture=45, focus_dist=1500)
    rot = (4, -16, 0)
    ts = render('Could', 'flat', px=120, fill='IVORY', glow=0.5, glow_color=('MAGENTA', 2.0),
                glow_radii=(0.05, 0.2), glow_weights=(0.7, 0.4))
    you = render('YOU', 'extrude3d', px=240, fill=('MAGENTA', 'HOT_PINK', 'ORANGE'), fill_angle=35, fill_gain=1.2)
    fc = render('Foster Carer?', 'deep_glow', px=104, glow_color=('ORANGE', 2.4), inner_glow_color=('AMBER', 1.2))
    far = render('Nurture. Develop. Grow.', 'flat', px=90, fill='PEACH')
    far.draw_plane(cv, cam, (-80, -900, 2200), rot=rot, opacity=0.8)
    ts.draw_plane(cv, cam, (-150, -330, 250), rot=rot)
    you.draw_plane(cv, cam, (0, -80, 0), rot=rot, sweep=0.4)
    render('be a', 'flat', px=80, fill='IVORY').draw_plane(cv, cam, (-170, 150, -40), rot=rot)
    fc.draw_plane(cv, cam, (0, 330, -80), rot=rot)
    g = Glyphs('Support is part of the role.', 'ui', px=46)
    g.rise(cv, 0.9, 540, 1500, tilt=(28, -16, 0), t0=0.0)
    cv = K.post(cv, 'neon', 1.2)
    path = os.path.join(out, 'type3d_3d.png')
    K._write_u8(path, K.to_srgb8(cv, 1.2))
    return path


def _hook_sheet(out):
    """Legibility over busy footage: slammed deep-glow / extruded hook words with a dark scrim, a multi-line
    question block and a glass pill over full-bleed graded footage."""
    import footage as F
    tiles = []
    specs = [('c12', 3.0, 'A SAFE HOME.', 'deep_glow', dict(px=128, scrim=0.8), 0.12),
             ('c10', 15.0, 'EVERYDAY CARE.', 'extrude3d', dict(px=118, scrim=0.8), 1.2),
             ('c08', 4.0, 'Could YOU\nbe a\nFoster Carer?', 'deep_glow',
              dict(px=120, glow_color=('ORANGE', 2.4), inner_glow_color=('AMBER', 1.2), scrim=0.75,
                   line_height=1.12), 1.2)]
    for cid, ts_, text, sty, kw, t in specs:
        cv = F.Clip(cid).get(ts_, K.W, K.H, look='neon')
        cv = cv.copy()
        g = Glyphs(text, sty, **kw)
        if '\n' in text:
            g.rise(cv, t, 540, 900, t0=0.0, stagger=0.03)
        else:
            g.slam(cv, t, 540, 900, t0=0.0)
        render('Start your enquiry \u2192', 'glass_pill', px=44).draw(cv, 540, 1450)
        cv = K.post(cv, 'neon', t)
        tiles.append(cv2.resize(K.to_srgb8(cv, t), (540, 960), interpolation=cv2.INTER_AREA))
    path = os.path.join(out, 'type3d_hook.png')
    K._write_u8(path, np.concatenate(tiles, 1))
    return path


def _fineprint_sheet(out):
    rows = [('ui', 'Rates may vary by region and are subject to change.', 28, 'Poppins-Regular'),
            ('ui', 'Your supervising social worker', 34, 'Poppins-Medium'),
            ('ui', 'Preparation & ongoing learning', 40, 'Poppins-SemiBold'),
            ('ui', '0161 241 1332 \u00b7 organicfostering.co.uk', 46, 'Poppins-SemiBold')]
    tiles = []
    for look, sty_fill in (('neon', 'IVORY'), ('airy', 'INK')):
        cv = K.background(look, 0.5)[400:760, :].copy()
        y = 50
        for _, text, px, fnt in rows:
            ts = render(text, 'ui', px=px, font=fnt, fill=sty_fill)
            ts.draw(cv, 60, y, anchor=(0, 0.5))
            y += px * 2.0
        u8 = K.to_srgb8(cv)
        tiles.append(cv2.resize(u8[:, :760], None, fx=1.5, fy=1.5, interpolation=cv2.INTER_NEAREST))
    path = os.path.join(out, 'type3d_fineprint.png')
    K._write_u8(path, np.concatenate(tiles, 0))
    return path


def selftest():
    import time
    out = K.SELFTEST
    os.makedirs(out, exist_ok=True)
    paths = []
    for look, name in (('neon', 'night'), ('amber', 'amber'), ('airy', 'ivory')):
        t0 = time.time()
        paths.append(_styles_sheet(look, name, out))
        print('  %s sheet %.1fs (builds included)' % (name, time.time() - t0))
    for fn in (_sweep_strip, _kinetic_strip, _orbit_counter_sheet, _video_sheet, _plane_sheet, _hook_sheet,
               _fineprint_sheet):
        t0 = time.time()
        paths.append(fn(out))
        print('  %s %.1fs' % (fn.__name__, time.time() - t0))
    # per-frame cost of cached draws
    cv = K.new_canvas(K.C['NIGHT_1'])
    ts = render('Could YOU', 'extrude3d', px=168)
    t0 = time.perf_counter()
    for i in range(10):
        ts.draw(cv, 540, 900, scale=1.0 + 0.01 * i, sweep=0.1 * i)
    print('  hero extrude3d draw + sweep at scale != 1: %.1f ms' % ((time.perf_counter() - t0) * 100))
    return paths


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        print(__doc__)
