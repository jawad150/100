"""jawad_kit.py - brand profile for Jawad (@jawad_mp4): looks 'ember' + 'noir_ember', house type styles, glass UI
looks, footage grades and house-style helpers (glowing underline stroke, title lockup, signature, rising embers).

Jawad's palette and fonts come from project.json (wsconf applies them before core.C is built). This profile only
adds what project.json cannot express, in-process, on import (idempotent; render.py workers re-import it through
the reel module):

    import jawad_kit                                   # FIRST, before building any sprite
    from jawad_kit import K, T, ui, F, S3, SFX, J      # J = this module (helpers below)

LOOKS (pass the name wherever the toolkit takes a look: K.background, K.post, ui.*, F.Clip.get, T.VideoType...)
    'ember'       deep warm-black void, flame-orange key glow top-right with smoky curtains, ember-red haze low
                  left, a soft stage haze from the top, warm bokeh discs drifting up; post: red-orange bloom tint,
                  halation, subtle grain, vignette, CRUSHED (toe-curved, never lifted) warm blacks.
    'noir_ember'  higher contrast near-monochrome warm black with ONE red-orange practical light (top right);
                  post desaturates everything that is not orange/red (mono=0.85), deeper crush, more grain.
    K.background(look, t, cam=None, ..., bokeh=1.0)    bokeh scales the 2D bokeh layer of the Jawad looks (0 off;
                  other looks ignore it). ~45-70 ms.
    K.post(cv, look, t, **ov)  extra keys for the Jawad looks: crush=(kr, kg, kb) toe strength per channel
                  (linear; 0 = off), mono=0..1 (desaturate non-red colours to warm mono). ~140-190 ms.
    ui.LOOKS['ember'|'noir_ember']: smoky warm-black glass, flame accent, flame->red gradient, hot-orange rim
                  with red hot spot, GOLD ticks.   F.GRADES['ember'|'noir_ember']: footage / still grades.
    J.register_look('jw_x', base='ember', bg={...}, post={...}, bokeh=(n, colours, (r0, r1), bright), ui_look={...},
                  grade={...}) adds a look with the same finish (for the colorist's jw_* looks).
    Defaults: every ui function whose look defaulted to 'neon' now defaults to 'ember'; ui.app_window title/header,
    ui.button, ui.badge and T.Counter (prefix '') no longer default to the original client's copy / currency.

TYPE STYLES (T.render(text, style, px=...); T.Glyphs(text, style, px=...))
    'jw_key'      the house keyword: Instrument Serif Italic, amber->flame->red vertical gradient, hot inner glow,
                  deep flame/red glow ("yaadein", "younger self", "AI video ad").  hero 150-260 px.
    'jw_key3d'    the same keyword as a 3D extrusion (ember sides, amber rim light) for big 3D moments.
    'jw_neon'     serif-italic neon tube (signage).
    'jw_caps'     white uppercase grotesk (Poppins SemiBold, +6 % tracking, warm halo + soft shadow) - "MEETING MY".
    'jw_caps_bold' Poppins Bold version.   'jw_body' lowercase grotesk lines ("delete ... hoti").
    'jw_mono'     JetBrains Mono for timecodes / UI readouts.   'jw_handle' the '@jawad_mp4' signature.
    Font aliases (T and ui): 'serif' (Instrument Serif Italic), 'serif_roman', 'grotesk', 'grotesk_bold',
    'grotesk_medium', 'mono', 'mono_bold'; 'hand' now resolves to the serif italic (the brand's accent face).
    Existing presets re-tinted for the brand (their hard-coded hex): extrude3d side_tint, chrome sides, ink_soft,
    deep_glow fill, glass_pill_light shadow. All other preset colours follow the palette roles.

HELPERS
    ul = J.underline(760)            glowing underline stroke (thin left -> thick right, hot comet head), cached
    ul.draw(cv, x0, y, u=1, opacity=1, smear=0)   x0 = left end, y = line centre; u = draw-on progress 0..1
                                      (head rides the tip; smear = px of head travel per shutter).  ~3-6 ms.
    ht = J.HouseTitle('MEETING MY', 'younger self', caps_px=86, key_px=210)   house title lockup (cached)
    ht.draw(cv, t, x, y, t0=0, out_t0=None)   caps rise -> serif keyword rises per glyph -> underline draws on;
                                      (x, y) = centre of the keyword.  ht.height, ht.width.  ~15-60 ms.
    J.signature(cv, x, y, opacity=1, px=34)     '@jawad_mp4' (house signature, bottom centre at y ~ 1560)
    J.embers(n=140, seed=0, bright=1.0)  -> K.Particles of rising warm sparks / bokeh (3D, DOF from the cam)
    J.selftest()                      python3 jawad_kit.py selftest -> <WS>/out/selftest/jawad_kit_*.png
"""
import functools
import math
import os
import sys
import time

import cv2
import numpy as np

import core as K
import type3d as T
import ui
import footage as F
import sprites3d as S3
import audio as SFX

J = sys.modules[__name__]
LOOK_NAMES = {'ember', 'noir_ember'}          # looks finished by the kit's post (register_look() adds more)

# brand tokens (project.json carries them; the fallbacks keep the profile importable without it)
_TOKENS = {'FLAME': '#FF6A1A', 'RED': '#F2312B', 'EMBER': '#B3120E', 'GOLD': '#FF9F1C', 'ASH': '#A8978C',
           'SMOKE': '#2A1A15', 'AMBER': '#FFB547'}
SERIF = 'InstrumentSerif-RegularItalic'
SERIF_ROMAN = 'InstrumentSerif-Regular'
GROTESK, GROTESK_BOLD, GROTESK_MEDIUM = 'Poppins-SemiBold', 'Poppins-Bold', 'Poppins-Medium'
MONO, MONO_BOLD = 'JetBrainsMono-Medium', 'JetBrainsMono-Bold'
HANDLE = '@jawad_mp4'


def _lin(name):
    return np.asarray(K.C[name], np.float32)


# =============================================================================================== backgrounds
# blob: (cx, cy, rx, ry, angle, colour, intensity, drift_x, drift_y, period[, aurora]) - core._BG_LOOKS format
_BG = {
    'ember': dict(
        top='NIGHT_0', bottom='NIGHT_0', lift=0.30, base_tint=(1.25, 0.92, 0.85),
        blobs=[
            (0.50, -0.08, 0.70, 0.20, 0, 'FLAME', 0.07, 0.03, 0.01, 27.0, 0.0),     # stage haze from the top
            (0.88, 0.18, 0.48, 0.24, -24, 'FLAME', 0.12, 0.05, 0.04, 23.0, 0.75),   # key glow, smoky curtains
            (0.82, 0.22, 0.14, 0.08, -24, 'AMBER', 0.05, 0.04, 0.03, 17.0, 0.4),    # its hot core
            (0.04, 0.80, 0.52, 0.38, 28, 'EMBER', 0.24, 0.05, 0.05, 29.0, 0.5),     # ember haze low left
            (0.12, 0.76, 0.20, 0.14, 28, 'RED', 0.05, 0.05, 0.05, 19.0, 0.6),
            (0.60, 1.08, 0.80, 0.14, 0, 'EMBER', 0.16, 0.03, 0.01, 31.0, 0.0),      # warm floor bounce
        ],
        rim=None, dots=0.0, dots_lit=0.0, noise=0.62),
    'noir_ember': dict(
        top='NIGHT_0', bottom='NIGHT_0', lift=0.10, base_tint=(1.0, 0.86, 0.80),
        blobs=[
            (0.90, 0.26, 0.40, 0.30, -20, 'FLAME', 0.20, 0.03, 0.03, 25.0, 0.45),   # the single practical light
            (0.93, 0.24, 0.11, 0.08, -20, 'AMBER', 0.10, 0.02, 0.02, 17.0, 0.0),
            (0.30, 0.82, 0.80, 0.46, 10, 'SMOKE', 0.55, 0.03, 0.03, 33.0, 0.3),     # neutral warm-black fill
        ],
        rim=None, dots=0.0, dots_lit=0.0, noise=0.5),
}
# bokeh layer: (count, colour names, radius range px, brightness)
_BOKEH = {'ember': (22, ('FLAME', 'AMBER', 'RED', 'GOLD'), (8, 64), 0.24),
          'noir_ember': (10, ('FLAME', 'RED'), (8, 48), 0.16)}


@functools.lru_cache(maxsize=64)
def _bokeh_disc(r, cname):
    """Emissive cinematic bokeh disc (alpha 0): flat body, brighter rim, 1.2 px AA edge. Read-only, cached."""
    n = int(math.ceil(r)) + 3
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    d = np.sqrt(xx * xx + yy * yy)
    body = np.clip((r - d) / 1.2 + 0.5, 0, 1)
    rimk = np.clip((d / max(r, 1) - 0.62) / 0.36, 0, 1) ** 2
    prof = body * (0.62 + 0.55 * rimk)
    spr = np.zeros(d.shape + (4,), np.float32)
    spr[..., :3] = prof[..., None] * _lin(cname)
    spr.flags.writeable = False
    return spr


@functools.lru_cache(maxsize=4)
def _bokeh_set(look, seed):
    n, cols, (r0, r1), br = _BOKEH[look]
    rng = np.random.default_rng(1000 + seed)
    d = dict(x=rng.uniform(-0.05, 1.05, n), y=rng.uniform(0.0, 1.0, n),
                r=np.round(r0 + (r1 - r0) * rng.uniform(0, 1, n) ** 2.2).astype(int),
                c=[cols[i] for i in rng.integers(0, len(cols), n)], v=rng.uniform(0.006, 0.02, n),
                sway=rng.uniform(0.004, 0.018, n), ph=rng.uniform(0, 2 * math.pi, n),
                tw=rng.uniform(0.25, 0.9, n), b=br * rng.uniform(0.35, 1.0, n), z=rng.uniform(1.1, 1.7, n))
    # a big defocused disc spreads the same light over more area: dimmer (keeps big ones from reading as stains)
    d['b'] = d['b'] * np.minimum(1.0, (r0 * 1.6 / d['r']) ** 0.7)
    # big discs only in the saturated flame / red (a dim amber disc reads olive on the dark red haze)
    big = ('FLAME', 'RED')
    d['c'] = [c if r <= 26 else big[i % 2] for i, (c, r) in enumerate(zip(d['c'], d['r']))]
    return d


def _draw_bokeh(cv, look, t, cam, amount, seed, parallax):
    B = _bokeh_set(look, seed)
    s, rot, tx, ty = (1.0, 0.0, 0.0, 0.0)
    if cam is not None and parallax > 0:
        s, rot, tx, ty = K._bg_transform(cam, min(1.0, parallax))
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(len(B['r'])):
        y = (B['y'][i] - B['v'][i] * t) % 1.12 - 0.06                   # rising slowly, wraps
        x = B['x'][i] + B['sway'][i] * math.sin(t * 0.5 + B['ph'][i])
        px, py = x * K.W - K.CX, y * K.H - K.CY
        z = B['z'][i]                                                    # nearer than the backdrop
        sx = K.CX + (tx * z) + (px * cr - py * sr) * (1 + (s - 1) * z)
        sy = K.CY + (ty * z) + (px * sr + py * cr) * (1 + (s - 1) * z)
        a = B['b'][i] * amount * (1 - B['tw'][i] * 0.5 * (1 + math.sin(t * 1.3 * B['tw'][i] + B['ph'][i])))
        edge = min(1.0, (y + 0.06) / 0.12, (1.06 - y) / 0.12)            # fade at the wrap
        if a * edge > 0.003:
            K.draw(cv, _bokeh_disc(int(B['r'][i]), B['c'][i]), sx, sy, opacity=a * edge)


# =============================================================================================== post
def _crush(cv, k):
    """Toe curve per channel in linear light: c' = c^2 / (c + k). Deep blacks go deeper, nothing is lifted;
    mids and highlights (and emissive > 1) lose only ~k (1-2 %). Alpha is set to 1 by the caller."""
    if not k or max(k) <= 0:
        return cv
    np.maximum(cv, 0, out=cv)
    den = cv2.add(cv, (float(k[0]), float(k[1]), float(k[2]), 1.0))
    sq = cv2.multiply(cv, cv)
    cv2.divide(sq, den, dst=cv)
    return cv


def _mono(cv, amount, warm=(1.0, 0.92, 0.84)):
    """Desaturate everything that is not orange / red towards a warm mono (noir_ember)."""
    if amount <= 0:
        return cv
    r, g, b, a = cv2.split(cv)
    L = cv2.transform(cv, np.float32([[0.2126, 0.7152, 0.0722, 0.0]]))
    red = cv2.divide(cv2.subtract(r, cv2.max(g, b)), cv2.add(r, 0.02), scale=1.6)
    keep = cv2.max(cv2.min(cv2.subtract(red, 0.35), 1.0), 0.0)            # 1 = orange/red, 0 = everything else
    keep = cv2.add(cv2.multiply(keep, float(amount)), float(1.0 - amount))  # 1 - amount * (1 - red)
    out = []
    for ch, wk in zip((r, g, b), warm):
        m = cv2.multiply(L, float(wk))
        out.append(cv2.add(m, cv2.multiply(cv2.subtract(ch, m), keep)))
    cv2.merge(out + [a], dst=cv)
    return cv


# =============================================================================================== apply
def _retarget_defaults(mod, old, new):
    """Replace a default argument value in every function (and lru_cache-wrapped function) of a module."""
    n = 0
    for name in dir(mod):
        f = getattr(mod, name)
        if not callable(f) or getattr(f, '__module__', None) != mod.__name__:
            continue
        g = getattr(f, '__wrapped__', f)
        d = getattr(g, '__defaults__', None)
        if d and old in d:
            g.__defaults__ = tuple(new if v == old else v for v in d)
            n += 1
    return n


def _set_default(fn, param, value):
    g = getattr(fn, '__wrapped__', fn)
    code = g.__code__
    names = code.co_varnames[:code.co_argcount]
    d = list(g.__defaults__)
    i = names.index(param) - (len(names) - len(d))
    d[i] = value
    g.__defaults__ = tuple(d)


def apply():
    """Install the profile into core / type3d / ui / footage (idempotent)."""
    if getattr(K, '_jawad_kit_applied', False):
        return
    for k, v in _TOKENS.items():                       # tokens normally come from project.json
        if k not in K.C:
            K.PALETTE_HEX[k] = v
            K.C[k] = K.hexlin(v)
    # ---- core: backdrops + post looks
    K._BG_LOOKS.update(_BG)
    K.LOOKS['ember'] = dict(
        exposure=0.0, bloom=0.62, bloom_threshold=0.40, bloom_knee=0.3, bloom_radii=(8, 26, 70, 170),
        bloom_tint=(1.0, 0.46, 0.20), halation=0.16, anamorphic=0.0, anamorphic_color=tuple(_lin('FLAME')),
        vignette=0.50, chroma=1.2, grain=0.016, black_tint=None, crush=(0.010, 0.015, 0.020), mono=0.0)
    K.LOOKS['noir_ember'] = dict(
        exposure=-0.05, bloom=0.50, bloom_threshold=0.48, bloom_knee=0.3, bloom_radii=(8, 26, 70, 170),
        bloom_tint=(1.0, 0.40, 0.16), halation=0.12, anamorphic=0.0, vignette=0.62, chroma=1.0, grain=0.022,
        black_tint=None, crush=(0.018, 0.024, 0.030), mono=0.85)
    orig_bg, orig_post = K.background, K.post

    @functools.wraps(orig_bg)
    def background(look='ember', t=0.0, cam=None, center=None, boost=0.0, dots=1.0, rim=1.0, seed=0, parallax=1.0,
                   intensity=1.0, bokeh=1.0):
        cv = orig_bg(look, t, cam, center, boost, dots, rim, seed, parallax, intensity)
        if look in _BOKEH and bokeh > 0:
            _draw_bokeh(cv, look, t, cam, bokeh * intensity, seed, parallax)
        return cv

    @functools.wraps(orig_post)
    def post(canvas, look='ember', t=0.0, **ov):
        if look not in LOOK_NAMES:
            return orig_post(canvas, look, t, **ov)
        cfg = dict(K.LOOKS[look])
        cfg.update(ov)
        ov = dict(ov, grain=0.0)
        orig_post(canvas, look, t, **ov)
        _mono(canvas, float(cfg.get('mono') or 0.0))
        _crush(canvas, cfg.get('crush'))
        if cfg.get('grain', 0) > 0:
            K.grain(canvas, t, cfg['grain'])
        canvas[..., 3] = 1.0
        return canvas

    background._jawad_orig = orig_bg
    post._jawad_orig = orig_post
    K.background, K.post = background, post
    # ---- footage grades (display-referred; black=0 -> never lifted)
    F.GRADES.setdefault('ember', dict(
        wb=(1.06, 1.0, 0.90), exposure=-0.04, contrast=1.22, pivot=0.40, black=0.0, black_tint=(0.25, 0.06, 0.03),
        shadow_tint=(0.022, -0.004, -0.018), highlight_tint=(0.030, 0.010, -0.030), sat=1.05, shoulder=0.90))
    F.GRADES.setdefault('noir_ember', dict(
        wb=(1.03, 1.0, 0.94), exposure=-0.08, contrast=1.35, pivot=0.42, black=0.0, black_tint=(0.2, 0.1, 0.06),
        shadow_tint=(0.012, 0.002, -0.008), highlight_tint=(0.020, 0.008, -0.020), sat=0.40, shoulder=0.90))
    # ---- ui looks
    f = dict(ui.LOOKS['neon'].__dict__)
    f.pop('name')
    v = ui._v
    em = dict(f, tint_top=v(K.mix(K.C['NIGHT_1'], K.C['SMOKE'], 0.6)), tint_bot=v(K.C['NIGHT_0']), tint_a=0.70,
              text=v(K.C['IVORY']), text2=v(K.mix(K.C['IVORY'], K.C['PEACH'], 0.5), 0.55),
              text3=v(K.C['PEACH'], 0.30), accent=v(K.C['FLAME']), accent_hi=v(K.C['AMBER']),
              grad=(v(K.C['FLAME']), v(K.C['RED'])), grad_hi=(v(K.C['AMBER']), v(K.C['FLAME'])),
              rim=v(K.C['HOT_PINK']), rim2=v(K.C['RED']), glow=v(K.C['FLAME']), ok=v(K.C['GOLD']),
              ok_hi=v(K.C['LEAF_HI']), chip_text=v(K.C['IVORY'], 0.80))
    noir = dict(em, tint_top=v(K.mix(K.C['NIGHT_1'], K.C['SMOKE'], 0.4)), tint_a=0.74, rim=v(K.C['FLAME']),
                rim2=v(K.C['AMBER']), glow=v(K.C['EMBER']), rim_k=0.8, glow_k=0.6)
    ui.LOOKS['ember'] = ui.Look('ember', **em)
    ui.LOOKS['noir_ember'] = ui.Look('noir_ember', **noir)
    _retarget_defaults(ui, 'neon', 'ember')
    _set_default(ui.app_window, 'title', '')
    _set_default(ui.app_window, 'header', '')
    _set_default(ui.button, 'text', 'Follow')
    _set_default(ui.badge, 'text', HANDLE)
    _set_default(T.Counter.__init__, 'prefix', '')
    ui.FONT_ALIAS.update(serif=SERIF, serif_roman=SERIF_ROMAN, mono=MONO, mono_bold=MONO_BOLD)
    # ---- type: aliases, re-tinted presets, house styles
    T.FONT_ALIAS.update(hand=SERIF, serif=SERIF, serif_roman=SERIF_ROMAN, grotesk=GROTESK, grotesk_bold=GROTESK_BOLD,
                        grotesk_medium=GROTESK_MEDIUM, mono=MONO, mono_bold=MONO_BOLD)
    S = T.STYLES
    S['extrude3d'] = S['extrude3d'].but(side_tint='#7A1A0C', fill=((0.0, '#FFFFFF'), (0.5, '#FFF1E6'), (1.0, '#E8D3C6')),
                                        rim_color=('HOT_PINK', 1.3))
    S['chrome'] = S['chrome'].but(side=(('#7A1A0C', 1.0), ('#140504', 1.0)))
    S['deep_glow'] = S['deep_glow'].but(fill=((0.0, '#FFFFFF'), (1.0, '#FFF4E8')))
    S['ink_soft'] = S['ink_soft'].but(fill=((0.0, '#2A1A15'), (1.0, '#170A07')), side=(('#5A1A0E', 1.0), ('#3A0E08', 1.0)),
                                      long_shadow_color='#8A4A30', shadow_color='#4A1A10')
    S['glass_pill_light'] = S['glass_pill_light'].but(pill_shadow_color='#4A1A10')
    # keyword fill measured on the covers: amber-gold top (#F4A21A..#FB8626) -> orange (#F07124) -> red-orange
    # bottom (#CD5024 / #F84600); a soft bevel gives the slight emboss, the glow is red-orange and wide
    flame = ((0.0, '#FFC34D'), (0.45, '#FF8A1F'), (1.0, '#F04A16'))
    S['jw_key'] = T.Style(
        name='jw_key', font=SERIF, px=210, tracking=-0.005, fill=flame, fill_angle=-90, fill_gain=1.0,
        stroke=0.008, stroke_color='#FF7A1C', bevel=0.012, profile='soft', ambient=0.78, spec=0.35, shininess=20,
        glow=1.0, glow_color=('#FF4A1A', 1.3), glow_radii=(0.04, 0.12, 0.36, 0.8), glow_weights=(0.4, 0.4, 0.35, 0.3),
        shadow=0.35, shadow_offset=(0.0, 0.04), shadow_blur=0.08)
    S['jw_key3d'] = S['extrude3d'].but(
        name='jw_key3d', font=SERIF, fill=flame, fill_angle=-90, fill_gain=1.15, bevel=0.012, profile='round',
        ambient=0.72, spec=0.55, env=0.0, rim_color=('AMBER', 1.4), inner_shadow_color='PLUM', depth=0.14,
        side=(('#8A1A08', 1.0), ('#1A0503', 1.0)), glow_color=('FLAME', 1.6), edge_rim=0.7)
    S['jw_neon'] = S['neon'].but(name='jw_neon', font=SERIF, tube=0.034, tube_color=('HOT_PINK', 1.5),
                                 glow_color=('RED', 2.2))
    caps = dict(fill=((0.0, '#FFFFFF'), (1.0, 'IVORY')), fill_angle=-90, fill_gain=1.12, glow=0.45,
                glow_color=('FLAME', 0.75), glow_radii=(0.06, 0.2, 0.55), glow_weights=(0.55, 0.4, 0.3),
                shadow=0.55, shadow_offset=(0.0, 0.04), shadow_blur=0.08)
    S['jw_caps'] = T.Style(name='jw_caps', font=GROTESK, px=86, tracking=0.06, **caps)
    S['jw_caps_bold'] = T.Style(name='jw_caps_bold', font=GROTESK_BOLD, px=86, tracking=0.05, **caps)
    S['jw_body'] = T.Style(name='jw_body', font=GROTESK, px=72, tracking=0.0, **caps)
    S['jw_mono'] = T.Style(name='jw_mono', font=MONO, px=36, tracking=0.02, fill=('IVORY', 0.86), glow=0.25,
                           glow_color=('FLAME', 0.6), glow_radii=(0.08, 0.3), glow_weights=(0.5, 0.3))
    S['jw_handle'] = T.Style(name='jw_handle', font=GROTESK_MEDIUM, px=34, tracking=0.03, fill=('IVORY', 0.85),
                             glow=0.3, glow_color=('FLAME', 0.5), glow_radii=(0.1, 0.35), glow_weights=(0.5, 0.3),
                             shadow=0.5, shadow_offset=(0.0, 0.05), shadow_blur=0.1)
    K._jawad_kit_applied = True


def register_look(name, base='ember', bg=None, post=None, bokeh=None, ui_look=None, grade=None):
    """Add a look that gets the kit's finish (crush / mono / grain order, bokeh layer), e.g. the colorist's
    jw_* looks:  J.register_look('jw_inferno', bg=dict(J.BG['ember'], noise=0.7), post=dict(bloom=0.8),
    bokeh=(30, ('FLAME', 'RED'), (8, 60), 0.3)).  bg / post are merged over the base look's dicts; ui_look
    and grade default to the base's (pass a ui.Look field dict / an F.GRADES dict to change them)."""
    K._BG_LOOKS[name] = dict(K._BG_LOOKS[base], **(bg or {}))
    K.LOOKS[name] = dict(K.LOOKS[base], **(post or {}))
    if bokeh is not None or base in _BOKEH:
        _BOKEH[name] = bokeh if bokeh is not None else _BOKEH[base]
    f = dict(ui.LOOKS[base].__dict__)
    f.pop('name')
    f.update(ui_look or {})
    ui.LOOKS[name] = ui.Look(name, **f)
    F.GRADES[name] = dict(F.GRADES[base], **(grade or {}))
    LOOK_NAMES.add(name)
    return name


BG = _BG


# =============================================================================================== helpers
class Underline:
    """Glowing underline stroke of the covers: thin on the left, thickening to the right, hot comet head.
    Built once (cached via underline()); draw() crops it for a draw-on and puts the head on the tip."""

    def __init__(self, length, thick=5.0, arc=0.0, core=None, glow_color=None, head=1.0):
        self.length, self.thick, self.arc = int(length), float(thick), float(arc)
        core = _lin('AMBER') * 0.55 + _lin('WHITE') * 0.45 if core is None else np.asarray(core, np.float32)
        gcol = _lin('FLAME') if glow_color is None else np.asarray(glow_color, np.float32)
        Lh = self.length
        hh = int(math.ceil(thick * 2 + abs(arc) + 6))
        xs = np.arange(Lh, dtype=np.float32) + 0.5
        u = xs / Lh
        yc = hh / 2 + arc * (4 * u * (1 - u) - 0.5)
        prof = (np.clip(u / 0.45, 0, 1) ** 0.9) * (0.30 + 0.70 * u)
        hw = thick / 2 * prof
        yy = np.arange(hh, dtype=np.float32)[:, None] + 0.5
        cov = np.clip(hw[None, :] - np.abs(yy - yc[None, :]) + 0.5, 0, 1) * np.clip(u * 8, 0, 1)[None, :]
        line = np.zeros((hh, Lh, 4), np.float32)
        line[..., :3] = cov[..., None] * core * 1.6
        line[..., 3] = cov
        sp = K.glow(line, gcol, sigmas=(3, 9, 26), strength=1.15, weights=(0.9, 0.6, 0.45))
        sp2 = K.glow(np.ascontiguousarray(line), _lin('RED'), sigmas=(40,), strength=0.35, include=False)
        p1, p2 = (sp.shape[0] - hh) // 2, (sp2.shape[0] - hh) // 2
        d = p2 - p1
        sp2[d:d + sp.shape[0], d:d + sp.shape[1], :3] += sp[..., :3]
        sp2[d:d + sp.shape[0], d:d + sp.shape[1], 3] = np.maximum(sp2[d:d + sp.shape[0], d:d + sp.shape[1], 3],
                                                                    sp[..., 3])
        sp2.flags.writeable = False
        self.spr, self.pad, self.hh = sp2, p2, hh
        self.yc_end = float(yc[-1])
        self.yc = yc
        hr = thick * 0.85 * head
        self.hr = max(hr, 1.5)
        hd = K.disc(hr, _lin('WHITE') * 1.8)
        self.head = K.glow(hd, _lin('AMBER') * 1.2, sigmas=(4, 12, 30), strength=1.3 * head, weights=(1.0, 0.6, 0.35))
        self.head.flags.writeable = False

    def draw(self, cv, x0, y, u=1.0, opacity=1.0, feather=36, smear=0.0):
        """Draw with its left end at x0 and its centre line at y; u = draw-on progress (0..1). smear = px the
        head travels during the shutter (HouseTitle passes it) so a fast draw-on gives a streak, not dots."""
        u = float(np.clip(u, 0, 1))
        if u <= 0 or opacity <= 0:
            return
        tip = self.length * u
        if u < 1:
            cut = int(min(self.spr.shape[1], self.pad + tip + feather * 0.25 + 1))
            s = self.spr[:, :cut].copy()
            xs = np.arange(cut, dtype=np.float32) - self.pad
            m = np.clip((tip - xs) / feather + 0.25, 0, 1)
            s *= m[None, :, None]
        else:
            s = self.spr
        K.draw(cv, s, x0 - self.pad, y - self.pad - self.hh / 2, anchor=(0, 0), opacity=opacity)
        iy = min(len(self.yc) - 1, max(0, int(tip) - 1))
        hk = opacity * (0.55 + 0.45 * K.smoothstep(0.85, 1.0, u)) if u < 1 else opacity
        hy = y + (self.yc[iy] - self.hh / 2)
        if smear > self.hr and u < 1:                    # spread the head along its shutter path (a streak)
            n = min(12, int(smear / self.hr) + 1)
            for k in range(n):
                K.draw(cv, self.head, x0 + tip - smear * k / (n - 1), hy, opacity=hk * 1.6 / n)
        else:
            K.draw(cv, self.head, x0 + tip, hy, opacity=hk)


@functools.lru_cache(maxsize=32)
def underline(length, thick=5.0, arc=0.0, head=1.0):
    """Cached Underline(length, thick, arc).  e.g. J.underline(760).draw(cv, 160, 1010, u=K.ramp(t, .6, 1.2))"""
    return Underline(length, thick, arc, head=head)


class HouseTitle:
    """Jawad's title lockup: white uppercase grotesk line + glowing serif-italic keyword + underline stroke.
        ht = J.HouseTitle('MEETING MY', 'younger self'); ht.draw(cv, t, 540, 820, t0=0.2)
    (x, y) = centre of the keyword's text box. Static parts are built once per process (cache it with
    lru_cache in the reel's assets())."""

    def __init__(self, caps, key, caps_px=86, key_px=210, caps_style='jw_caps', key_style='jw_key', gap=0.30,
                 underline=True, max_w=940):
        self.caps_txt, self.key_txt = caps, key
        kw = T.measure(key, key_style, px=key_px)[0]
        if kw > max_w:
            key_px *= max_w / kw
        cw = T.measure(caps, caps_style, px=caps_px)[0] if caps else 0
        if cw > max_w:
            caps_px *= max_w / cw
        self.key = T.Glyphs(key, key_style, px=key_px)
        self.key_static = T.render(key, key_style, px=key_px)
        self.caps = T.render(caps, caps_style, px=caps_px) if caps else None
        self.key_px, self.caps_px = key_px, caps_px
        self.gap = gap * key_px
        self.kw, self.kh = self.key_static.w, self.key_static.h
        self.ul_len = int(min(max_w + 40, self.kw * 1.08 + 40))
        self.ul = J.underline(self.ul_len, thick=max(4.0, key_px * 0.026)) if underline else None
        ch = self.caps.h if self.caps else 0
        self.height = ch + self.gap + self.kh + key_px * 0.45
        self.width = max(self.kw, self.caps.w if self.caps else 0)

    def draw(self, cv, t, x, y, t0=0.0, out_t0=None, caps_dur=0.6, key_t=0.22, ul_t=0.55, ul_dur=0.7, opacity=1.0):
        out = 1.0 if out_t0 is None else 1.0 - K.ramp(t, out_t0, out_t0 + 0.35, 'in_cubic')
        if out <= 0 or t < t0:
            return
        op = opacity * out
        if self.caps is not None:
            cy = y - self.kh / 2 - self.gap - self.caps.h / 2
            uc = K.ramp(t, t0, t0 + caps_dur, 'out_cubic')
            self.caps.draw(cv, x, cy + 28 * (1 - uc), opacity=op * K.ramp(t, t0, t0 + caps_dur * 0.7, 'inout_sine'),
                           blur=6 * (1 - uc))
        tk = t0 + key_t
        if t >= tk:
            if t - tk < 1.2 or op < 1:
                self.key.rise(cv, t, x, y, t0=tk, stagger=0.03, dur=0.5, dist=0.3, blur=7, scale0=0.94,
                              opacity=op)
            else:
                self.key_static.draw(cv, x, y, opacity=op)
        if self.ul is not None:
            def uu(tt):
                return K.ramp(tt, t0 + ul_t, t0 + ul_t + ul_dur, 'inout_cubic')
            u = uu(t)
            if u > 0:
                speed = (uu(t + 0.004) - uu(t - 0.004)) / 0.008 * self.ul_len        # px / s
                self.ul.draw(cv, x - self.ul_len / 2, y + self.kh / 2 + self.key_px * 0.36, u=u, opacity=op,
                             smear=speed * 0.25 / K.FPS)


def signature(cv, x, y, opacity=1.0, px=34):
    """'@jawad_mp4' house signature (Poppins Medium, ivory, faint flame halo). e.g. J.signature(cv, 540, 1560)"""
    _sig(px).draw(cv, x, y, opacity=opacity)


@functools.lru_cache(maxsize=8)
def _sig(px):
    return T.render(HANDLE, 'jw_handle', px=px)


def embers(n=140, seed=0, bright=1.0, vel=(0, -46, 0), size=(1.0, 3.2), twinkle=0.8):
    """Rising warm sparks / bokeh for 3D scenes (K.Particles; defocus comes from the cam's aperture).
        sparks = J.embers(160, seed=3); sparks.draw(cv, cam, t)    or  sc.particles(sparks, t)"""
    cols = [_lin('FLAME') * 1.2, _lin('AMBER'), _lin('RED') * 1.1, _lin('GOLD')]
    return K.Particles(n, seed=seed, vel=vel, size=size, colors=cols, twinkle=twinkle, bright=bright)


apply()


# =============================================================================================== selftest
def _label(cv, txt, x=40, y=70):
    T.render(txt, 'jw_mono', px=30).draw(cv, x, y, anchor=(0, 0.5))


def selftest():
    """Branded showcase: one hero frame per Jawad look + a type sheet + a ui sheet, with measured costs."""
    os.makedirs(K.SELFTEST, exist_ok=True)
    out = []
    tm = {}
    for look in ('ember', 'noir_ember'):
        t = 1.4
        K.background(look, t + 0.5)
        t0 = time.perf_counter()
        cv = K.background(look, t)
        tm[look + '_bg'] = (time.perf_counter() - t0) * 1e3
        ht = HouseTitle('MEETING MY', 'younger self') if look == 'ember' else HouseTitle('KUCH', 'yaadein')
        ht.draw(cv, 3.0, K.CX, 760)
        t0 = time.perf_counter()
        ht.draw(cv, 3.0, K.CX, 760)
        tm[look + '_title'] = (time.perf_counter() - t0) * 1e3
        win = ui.app_window(w=780, h=560, look=look, title='timeline.prproj', header='Render queue',
                            sub='3 reels · 1080 × 1920 · 30 fps', sidebar=False)
        win.draw(cv, K.CX, 1290, face=win.face_at(sweep=0.3))
        signature(cv, K.CX, 1660)
        cam = K.Cam(aperture=36)
        embers(120, seed=2).draw(cv, cam, t)
        K.post(cv.copy(), look, t)                      # warm-up (grain noise, bloom buffers)
        c2 = cv.copy()
        t0 = time.perf_counter()
        K.post(c2, look, t)
        tm[look + '_post'] = (time.perf_counter() - t0) * 1e3
        _label(c2, '%s  bg %.0f ms  title %.0f ms  post %.0f ms' % (look, tm[look + '_bg'], tm[look + '_title'],
                                                                   tm[look + '_post']))
        p = os.path.join(K.SELFTEST, 'jawad_kit_%s.png' % look)
        K.save_png(p, K.to_srgb8(c2, t))
        out.append(p)
    # type sheet
    cv = K.background('ember', 0.5, bokeh=0.5)
    y = 170
    for st, txt, px in (('jw_caps', 'MEETING MY', 86), ('jw_key', 'younger self', 200), ('jw_body', 'delete nahi hoti', 72),
                        ('jw_key3d', 'AI video', 190), ('jw_neon', 'cinema', 170), ('jw_caps_bold', 'MY ENTRY', 96),
                        ('jw_mono', '00:00:12:04  ● REC  4K  24 fps', 38), ('extrude3d', 'EDIT', 200),
                        ('jw_handle', HANDLE, 40)):
        t0 = time.perf_counter()
        ts = T.render(txt, st, px=px)
        bt = (time.perf_counter() - t0) * 1e3
        ts.draw(cv, K.CX, y + ts.h / 2)
        _label(cv, '%s  build %.0f ms' % (st, bt), 40, y - 22)
        y += ts.h + 120
    ul = underline(760)
    ul.draw(cv, K.CX - 380, y, u=1.0)
    ul.draw(cv, K.CX - 380, y + 80, u=0.55)
    _label(cv, 'underline u=1 / u=0.55', 40, y - 30)
    K.post(cv, 'ember', 0.5)
    p = os.path.join(K.SELFTEST, 'jawad_kit_type.png')
    K.save_png(p, K.to_srgb8(cv, 0.5))
    out.append(p)
    print('timings ms:', {k: round(v, 1) for k, v in tm.items()})
    for p in out:
        print('->', p)
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        print(__doc__)
