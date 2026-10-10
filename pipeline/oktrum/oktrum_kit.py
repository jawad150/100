"""oktrum_kit.py: the Oktrum brand profile and the shared widgets of the three Oktrum reels.

USE (first import of every Oktrum module, before any sprite is built):
    import oktrum_kit as OK
    from oktrum_kit import K, T, ui, F, S3, SFX       # SFX (audio.py, +70 MB) is imported lazily on first use

PROFILE (applied in-process on import; idempotent; a process that never imports this module is untouched)
    project.json already maps the palette roles and fonts. This profile re-points what project.json cannot reach
    (BRAND.md section 6) to Oktrum navy / violet / blue / cyan:
    core   K.LOOKS neon/amber/airy/natural bloom_tint + black_tint (+ new keys halation_tint, split_tone,
           leak_colors read by the wrapped K.post); _BG_LOOKS neon rim (cyan -> light blue), amber (cool
           dashboard: cyan aurora, violet accent, navy base), airy (ice-white page that encodes ~#F3F6FC, pale
           violet / blue / cyan blooms, faint navy dot grid; dots=0 hides it); K.light_leak default colours,
           K.brand_gradient default = VIOLET -> CYAN at -45 deg (CSS 135 deg).
    look   NEW 'cine' (reel2): K.background('cine', ...), K.post(cv, 'cine', t), ui look 'cine', F.GRADES['cine']:
           navy-black low-key haze, cyan anamorphic streaks, stronger grain, gentle vignette, cool highlights.
    type3d STYLES extrude3d (cool-white face, navy-violet side tint), chrome (navy sides, cyan ground), deep_glow
           (cool-white face), gradient (VIOLET -> CYAN, -45 deg), ink_soft (navy ink), glass_pill_light (navy
           shadow), every preset's side_tint; Counter prefix default '' (was GBP); old-brand hex literals in
           code and old recipes (far side #1A0518, VideoType plums, #9A1066/#22041C ...) remapped by T.col.
           New presets: 'extrude3d_brand' (violet -> blue -> cyan face, navy sides, cyan rim), 'serif_italic'
           (Instrument Serif Italic, one word per beat), 'mono' (JetBrains Mono, figures and tickers).
           Font aliases: T and ui 'mono', 'mono_bold', 'serif'.
    ui     LOOKS neon/airy grad_hi (light blue -> cyan, was -> gold); amber = navy glass with violet -> cyan
           accents (was brown/gold); airy text2/text3 darkened to pass 4.5:1 on the page; new 'cine' look;
           app_window traffic lights DOWN / AMBER / UP; badge disc brand gradient (was gold); old-client copy
           defaults re-pointed: money() symbol '', app_window title 'oktrum.com' + header 'Trade With Confidence',
           button 'Get Started', badge 'Bank-Tier Encryption', search_bar placeholder 'Search markets'.
           Always pass your own copy anyway (verified copy only: BRIEF.md / INTAKE.md section 3).
    footage F.GRADES neon/amber/airy re-pointed to navy blacks and cool highlights (were plum / warm).
    PROFILE dict: what was changed, for the hand-off notes.  OK.page_color() linear page of the light look.

COLOURS / FONTS (constants; linear RGB like K.C)
    OK.BLUE VIOLET CYAN NAVY UP DOWN BLUE_DEEP UP_DEEP DOWN_DEEP INK IVORY;  OK.ink(look) -> text colour pairs
    that pass BRAND.md contrast: dict(text, text2, accent, up, down) for dark looks and the light look.
    FONT_DISPLAY 'InterTight-Black', FONT_HEAD 'InterTight-ExtraBold', FONT_UI 'Inter-SemiBold', FONT_BODY
    'Inter-Regular', FONT_MONO 'JetBrainsMono-Medium', FONT_MONO_BOLD 'JetBrainsMono-Bold',
    FONT_SERIF 'InstrumentSerif-RegularItalic'.

SELF-TEST
    python3 oktrum_kit.py selftest [names...]   -> <WS>/out/kit/kit_*.png (one still per look and per widget,
                                                  with measured cost per call) + kit_report.json
"""
import functools
import inspect
import json
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

__all__ = ['K', 'T', 'ui', 'F', 'S3', 'SFX', 'apply', 'PROFILE', 'page_color', 'ink']


def __getattr__(name):
    """Lazy SFX: `from oktrum_kit import SFX` imports audio.py (scipy, ~0.8 s, ~70 MB) only when asked."""
    if name == 'SFX':
        import audio
        globals()['SFX'] = audio
        return audio
    raise AttributeError(name)


# =============================================================================================== brand tokens
_TOKENS = {'BLUE': '#5170FF', 'VIOLET': '#8465F4', 'CYAN': '#81D4E6', 'NAVY': '#07091A', 'UP': '#34D399',
           'DOWN': '#F87171', 'BLUE_HOVER': '#6180FF', 'BLUE_MID': '#4A65FF', 'BLUE_DEEP': '#3A55E0',
           'UP_DEEP': '#047857', 'DOWN_DEEP': '#B91C1C'}

FONT_DISPLAY = 'InterTight-Black'
FONT_HEAD = 'InterTight-ExtraBold'
FONT_UI = 'Inter-SemiBold'
FONT_UI_MED = 'Inter-Medium'
FONT_BODY = 'Inter-Regular'
FONT_MONO = 'JetBrainsMono-Medium'
FONT_MONO_BOLD = 'JetBrainsMono-Bold'
FONT_SERIF = 'InstrumentSerif-RegularItalic'

# encoded ice-white page of the light look: sRGB (243, 246, 252) after core's highlight shoulder
_PAGE_SRGB8 = (243, 246, 252)

# old-brand (magenta / plum / peach / gold-money) hex literals that live in toolkit code, presets and the old
# recipes -> Oktrum. Applied by T.col and ui.col (colour specs only; K.hexlin itself is untouched).
HEX_REMAP = {
    '#8E1E68': '#3A3FA8', '#1A0518': '#05071A', '#16051A': '#07091A', '#F3EEF3': '#EEF2FF', '#D8CEDA': '#D2DAF0',
    '#F4EEF4': '#F3F6FF', '#FF9A6A': '#81D4E6', '#FFF1F8': '#F3F6FF', '#3C2740': '#07091A', '#2A1A2D': '#141A3A',
    '#6E2A60': '#2A2370', '#4A1A44': '#1A1850', '#8A5070': '#5A6AB0', '#5B2E52': '#2A2370', '#7A2E68': '#2A3A8A',
    '#3A1436': '#141A3A', '#4A1242': '#1A1850', '#0B0310': '#020309', '#C23A84': '#4A65FF', '#6E1A52': '#2A2370',
    '#7A3A5A': '#2A3570', '#9A1066': '#3A3FA8', '#22041C': '#07091A', '#2A1208': '#0A0E2A', '#0E0604': '#020309',
    '#FFE2C4': '#F3F6FF', '#FFB15C': '#81D4E6',
}

PROFILE = {}          # filled by apply(): {area: [what changed, ...]}


def _note(area, what):
    PROFILE.setdefault(area, []).append(what)


def _lin(name):
    return np.asarray(K.C[name], np.float32)


def _inv_shoulder(y, knee=0.82, top=4.0):
    """Linear value whose core shoulder output is y (y < 1)."""
    if y <= knee:
        return float(y)
    rng = 1.0 - knee
    norm = 1 - math.exp(-(top - knee) / rng)
    v = (y - knee) / rng * norm
    return float(knee - rng * math.log(max(1 - v, 1e-9)))


def page_color():
    """Linear RGB of the light-look page (encodes to sRGB ~(243, 246, 252), an ice white whose blue channel sits
    on the shoulder, so the page never reads grey). e.g. K.new_canvas(OK.page_color())"""
    return np.array([_inv_shoulder(float(K.to_lin(np.float32(c / 255.0)))) for c in _PAGE_SRGB8], np.float32)


def ink(look='neon'):
    """Text colour set that passes BRAND.md contrast on the look (linear RGB).
    dark looks: text IVORY, text2 ~70 % IVORY, accent CYAN, up UP, down DOWN, blue HOT_PINK (light blue text);
    light look ('airy'): text INK, text2 navy-grey (>= 7:1), accent BLUE_DEEP, up UP_DEEP, down DOWN_DEEP.
        c = OK.ink(LOOK); ui.put_text(cv, 80, 400, 'BTC/USD', 40, 'ui', c['text'])"""
    if _is_light(look):
        return dict(text=_lin('INK'), text2=np.asarray(K.mix(K.C['INK'], K.C['PEACH'], 0.28), np.float32),
                    accent=_lin('BLUE_DEEP'), up=_lin('UP_DEEP'), down=_lin('DOWN_DEEP'), blue=_lin('BLUE_DEEP'))
    return dict(text=_lin('IVORY'), text2=_lin('IVORY') * np.float32(0.62), accent=_lin('CYAN'), up=_lin('UP'),
                down=_lin('DOWN'), blue=_lin('HOT_PINK'))


def _is_light(look):
    if isinstance(look, ui.Look):
        return not look.dark
    return look in ('airy', 'light', 'day')


# =============================================================================================== profile pieces
def _apply_tokens():
    for k, v in _TOKENS.items():
        if k not in K.C:
            K.PALETTE_HEX[k] = v
            K.C[k] = K.hexlin(v)
            _note('tokens', 'added %s %s' % (k, v))
    K.C['OK_PAGE'] = page_color()
    _note('tokens', 'K.C[OK_PAGE] = linear ice-white page %s' % np.round(K.C['OK_PAGE'], 3).tolist())


def _apply_core():
    L = K.LOOKS
    cool_black = (0.0006, 0.0009, 0.0024)
    leak = (K.C['CYAN'], K.C['VIOLET'] * 0.9, K.C['HOT_PINK'])
    L['neon'].update(bloom_tint=(0.55, 0.72, 1.0), black_tint=cool_black, halation_tint=(0.30, 0.55, 1.0),
                     leak_colors=leak)
    L['amber'].update(bloom_tint=(0.60, 0.85, 1.0), black_tint=cool_black, halation_tint=(0.30, 0.62, 1.0),
                      leak_colors=leak)
    L['airy'].update(bloom=0.28, bloom_threshold=1.35, bloom_knee=0.15, bloom_tint=(0.85, 0.90, 1.0), halation=0.0,
                     vignette=0.07, chroma=0.6, grain=0.008, leak_colors=(K.C['LAVENDER'], K.C['PEACH'], K.C['CYAN']))
    L['natural'].update(bloom_tint=(0.85, 0.90, 1.0), halation_tint=(0.35, 0.55, 1.0))
    L['cine'] = dict(exposure=-0.05, bloom=0.55, bloom_threshold=0.5, bloom_knee=0.3, bloom_radii=(8, 26, 70, 170),
                     bloom_tint=(0.50, 0.82, 1.0), halation=0.05, halation_tint=(0.30, 0.60, 1.0),
                     anamorphic=0.30, anamorphic_color=tuple(float(x) for x in K.C['CYAN']), vignette=0.50,
                     chroma=1.3, grain=0.030, black_tint=(0.0005, 0.0009, 0.0026),
                     split_tone=((0.90, 1.0, 1.12), 0.55), leak_colors=leak)
    _note('core', "LOOKS neon/amber bloom_tint + black_tint cool, halation_tint cool; airy bloom threshold 1.35 "
                  "(page > 1), cool tint, vignette 0.07; natural bloom_tint cool; NEW LOOKS['cine']")
    B = K._BG_LOOKS
    B['neon'] = dict(B['neon'], rim=('ORANGE', 'HOT_PINK', 1.0),
                     blobs=[(0.78, 0.22, 0.56, 0.30, -28, 'MAGENTA', 0.80, 0.06, 0.04, 23.0, 1.0),
                            (0.70, 0.26, 0.17, 0.10, -28, 'HOT_PINK', 0.34, 0.05, 0.035, 17.0, 0.5),
                            (0.06, 0.66, 0.50, 0.42, 32, 'PLUM', 0.55, 0.05, 0.05, 29.0, 0.4),
                            (0.10, 0.60, 0.26, 0.20, 32, 'VIOLET', 0.22, 0.05, 0.05, 19.0, 0.8),
                            (0.96, 0.80, 0.34, 0.24, 15, 'CYAN', 0.10, 0.03, 0.03, 31.0, 0.0)])
    B['amber'] = dict(B['amber'], base_tint=(0.85, 0.95, 1.25), rim=('CYAN', 'IVORY', 0.8),
                      blobs=[(0.24, 0.24, 0.56, 0.32, 24, 'CYAN', 0.40, 0.06, 0.04, 25.0, 1.0),
                             (0.30, 0.27, 0.18, 0.11, 24, 'HOT_PINK', 0.26, 0.05, 0.035, 18.0, 0.5),
                             (0.95, 0.70, 0.46, 0.40, -30, 'VIOLET', 0.20, 0.05, 0.05, 27.0, 0.5),
                             (1.00, 0.14, 0.26, 0.20, -12, 'BLUE', 0.24, 0.04, 0.03, 21.0, 0.3),
                             (0.05, 0.90, 0.40, 0.30, 15, 'PLUM', 0.32, 0.05, 0.04, 33.0, 0.0)])
    B['airy'] = dict(B['airy'], top='OK_PAGE', bottom='OK_PAGE', paper=0.006, noise=0.10,
                     dots=-0.16, dots_lit=0.001,
                     blobs=[(0.86, 0.12, 0.72, 0.50, -30, 'LAVENDER', 1.0, 0.05, 0.04, 26.0),
                            (0.80, 0.16, 0.38, 0.26, -30, 'VIOLET', 0.10, 0.04, 0.03, 19.0),
                            (0.08, 0.38, 0.62, 0.50, 25, 'PEACH', 0.9, 0.05, 0.05, 22.0),
                            (0.12, 0.40, 0.42, 0.30, 25, 'CYAN', 0.22, 0.05, 0.05, 30.0),
                            (0.88, 0.84, 0.66, 0.46, -20, 'LAVENDER', 0.85, 0.05, 0.04, 24.0),
                            (0.92, 0.88, 0.36, 0.25, -20, 'BLUE', 0.07, 0.04, 0.04, 21.0),
                            (0.35, 0.99, 0.80, 0.34, 10, 'PEACH', 0.7, 0.04, 0.03, 34.0),
                            (0.14, 0.86, 0.34, 0.24, 0, 'CYAN', 0.12, 0.04, 0.04, 27.0)])
    B['cine'] = dict(top='NIGHT_0', bottom='NIGHT_1', lift=0.22,
                     blobs=[(0.62, 0.10, 0.70, 0.30, -14, 'BLUE', 0.30, 0.03, 0.02, 31.0, 0.15),
                            (0.70, 0.16, 0.22, 0.10, -14, 'CYAN', 0.12, 0.03, 0.02, 23.0, 0.0),
                            (0.10, 0.78, 0.60, 0.40, 25, 'PLUM', 0.42, 0.04, 0.04, 37.0, 0.0),
                            (0.92, 0.66, 0.40, 0.30, -20, 'VIOLET', 0.06, 0.03, 0.03, 29.0, 0.0)],
                     rim=None, dots=0.0, dots_lit=0.0, noise=0.65)
    for fn in (K._bg_base, K._bg_maps, K._bg_maps_nodots):
        fn.cache_clear()
    _note('core', '_BG_LOOKS neon rim cyan->light blue + violet blob; amber cool dashboard; airy ice-white page '
                  '+ navy dot grid (dots=0 hides it); NEW cine backdrop')


def _apply_core_wrappers():
    orig = K.__dict__.setdefault('_ok_orig', {})
    orig.setdefault('post', K.post)
    orig.setdefault('_halation_small', K._halation_small)
    orig.setdefault('light_leak', K.light_leak)
    hal = [None]

    def _halation_small(small, strength, threshold, tint, radius):
        return orig['_halation_small'](small, strength, threshold, tint if hal[0] is None else hal[0], radius)

    def post(canvas, look='neon', t=0.0, **ov):
        """core.post with the Oktrum keys: halation_tint (the film halation colour, core hard-codes orange) and
        split_tone=((r, g, b), amount) (tints highlights; 'cine' cools them). Same call as core.post."""
        cfg = K.LOOKS[look]
        tint = ov.pop('halation_tint', cfg.get('halation_tint'))
        split = ov.pop('split_tone', cfg.get('split_tone'))
        hal[0] = tint
        try:
            out = orig['post'](canvas, look, t, **ov)
        finally:
            hal[0] = None
        if split:
            _split_tone(out, split[0], split[1])
        return out

    def light_leak(canvas, t, colors=None, *a, **kw):
        """core.light_leak with Oktrum default colours (cyan, violet, light blue) when colors is None."""
        if colors is None:
            colors = (K.C['CYAN'], K.C['VIOLET'] * 0.9, K.C['HOT_PINK'])
        return orig['light_leak'](canvas, t, colors, *a, **kw)

    post.__wrapped__ = orig['post']
    light_leak.__wrapped__ = orig['light_leak']
    K._halation_small = _halation_small
    K.post = post
    K.light_leak = light_leak
    K.brand_gradient.__defaults__ = (-45.0, K.C['VIOLET'].copy(), K.C['CYAN'].copy(), None)
    _note('core', 'K.post wrapped (halation_tint, split_tone); K.light_leak default colours; K.brand_gradient '
                  'default VIOLET->CYAN at -45 deg')


def _split_tone(cv, tint, amount, lo=0.18, hi=1.1):
    """Highlights (by luminance, 1/4-res weight map) pushed toward `tint`, in place."""
    h, w = cv.shape[:2]
    small = cv2.resize(np.ascontiguousarray(cv[..., :3]), (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    lum = small @ np.float32([0.2126, 0.7152, 0.0722])
    x = np.clip((lum - lo) / (hi - lo), 0, 1)
    m = cv2.resize((x * x * (3 - 2 * x) * np.float32(amount)).astype(np.float32), (w, h),
                   interpolation=cv2.INTER_LINEAR)
    for c in range(3):
        k = float(tint[c]) - 1.0
        if abs(k) > 1e-6:
            cv[..., c] *= 1.0 + m * np.float32(k)
    return cv


def _apply_type():
    S = T.STYLES
    old_side = '#8E1E68'
    for k in list(S):
        if S[k].side_tint == old_side:
            S[k] = S[k].but(side_tint='#3A3FA8')
    S['extrude3d'] = S['extrude3d'].but(fill=((0.0, '#FFFFFF'), (0.5, '#EEF2FF'), (1.0, '#D2DAF0')),
                                        side_tint='#3A3FA8', rim_color=('HOT_PINK', 1.5))
    S['chrome'] = S['chrome'].but(fill=((0.0, '#FFFFFF'), (1.0, '#F3F6FF')), env_ground='#81D4E6',
                                  side=(('#2A2370', 1.0), ('#07091A', 1.0)))
    S['deep_glow'] = S['deep_glow'].but(fill=((0.0, '#FFFFFF'), (1.0, '#F3F6FF')))
    S['gradient'] = S['gradient'].but(fill=('VIOLET', 'CYAN'), fill_angle=-45, inner_glow_color=('HOT_PINK', 0.8),
                                      glow_color=('BLUE', 1.4))
    S['ink_soft'] = S['ink_soft'].but(fill=((0.0, '#07091A'), (1.0, '#141A3A')), side=(('#2A2370', 1.0),
                                      ('#1A1850', 1.0)), long_shadow_color='#5A6AB0', shadow_color='#2A2370')
    S['glass_pill_light'] = S['glass_pill_light'].but(pill_shadow_color='#2A2370')
    S['extrude3d_brand'] = S['extrude3d'].but(
        name='extrude3d_brand', fill=('VIOLET', 'BLUE', 'CYAN'), fill_angle=-45, fill_gain=1.15, env=0.0,
        ambient=0.74, spec=0.65, depth=0.22, angle=-70, persp=0.08, side=(('#2A2370', 1.0), ('#05071A', 1.0)),
        rim_color=('CYAN', 1.4), glow_color=('BLUE', 1.3))
    S['serif_italic'] = T.Style(name='serif_italic', font=FONT_SERIF, px=140, fill='IVORY', tracking=-0.005,
                                side_tint='#3A3FA8')
    S['mono'] = T.Style(name='mono', font=FONT_MONO, px=40, fill='IVORY', tracking=0.0, side_tint='#3A3FA8')
    T.FONT_ALIAS.update(mono=FONT_MONO, mono_bold=FONT_MONO_BOLD, serif=FONT_SERIF)
    _set_defaults(T.Counter.__init__, prefix='')
    orig = T.__dict__.setdefault('_ok_orig_col', T.col)

    def col(c):
        """type3d.col with Oktrum's remap of old-brand hex literals (HEX_REMAP)."""
        if isinstance(c, str) and c.startswith('#'):
            c = HEX_REMAP.get(c.upper(), c)
        return orig(c)
    col.__wrapped__ = orig
    T.col = col
    T.clear_cache()
    for fn in (T.font,):
        fn.cache_clear()
    _note('type3d', 'STYLES extrude3d/chrome/deep_glow/gradient/ink_soft/glass_pill_light re-pointed; side_tint '
                    '#3A3FA8 on every preset; NEW extrude3d_brand, serif_italic, mono; Counter prefix ""; '
                    'T.col remaps old-brand hex (HEX_REMAP)')


def _set_defaults(fn, **new):
    """Re-point default values of fn's keyword parameters by name (works through functools wrappers)."""
    f = inspect.unwrap(fn)
    params = [p for p in inspect.signature(f).parameters.values()
              if p.default is not inspect.Parameter.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    names = [p.name for p in params]
    d = list(f.__defaults__ or ())
    for k, v in new.items():
        if k in names:
            d[names.index(k)] = v
        elif f.__kwdefaults__ and k in f.__kwdefaults__:
            f.__kwdefaults__[k] = v
        else:
            raise KeyError('%s has no default %s' % (f.__name__, k))
    f.__defaults__ = tuple(d)
    if hasattr(fn, 'cache_clear'):
        fn.cache_clear()


def _clone_look(src, name, **kw):
    f = dict(ui.LOOKS[src].__dict__)
    f.pop('name')
    f.update(kw)
    return ui.Look(name, **f)


def _apply_ui():
    C = K.C
    v = ui._v
    Ln, La, Lr = ui.LOOKS['neon'], ui.LOOKS['amber'], ui.LOOKS['airy']
    Ln.grad_hi = (v(C['HOT_PINK']), v(C['CYAN']))
    Lr.grad_hi = (v(C['HOT_PINK']), v(C['CYAN']))
    # light look: the muted text tones must keep >= 4.5:1 on the ice page (BRAND.md section 2)
    Lr.text2 = v(K.mix(C['INK'], C['PEACH'], 0.30))
    Lr.text3 = v(K.mix(C['INK'], C['PEACH'], 0.45))
    for k, val in dict(tint_top=v(K.mix(C['NIGHT_1'], C['PLUM'], 0.35)), tint_bot=v(C['NIGHT_0']),
                       text2=v(K.mix(C['IVORY'], C['PEACH'], 0.5), 0.52), accent=v(C['CYAN']),
                       accent_hi=v(K.mix(C['CYAN'], C['IVORY'], 0.35)), grad=(v(C['VIOLET']), v(C['CYAN'])),
                       grad_hi=(v(C['LEAF_HI']), v(C['CYAN'])), rim=v(C['CYAN']), rim2=v(C['VIOLET']),
                       glow=v(C['CYAN'])).items():
        setattr(La, k, val)
    ui.LOOKS['cine'] = _clone_look('neon', 'cine', tint_top=v(K.mix(C['NIGHT_0'], C['NIGHT_1'], 0.7)),
                                   tint_bot=v(C['NIGHT_0']), tint_a=0.72, accent=v(C['BLUE']),
                                   accent_hi=v(C['CYAN']), grad=(v(C['BLUE']), v(C['CYAN'])),
                                   grad_hi=(v(C['HOT_PINK']), v(C['CYAN'])), rim=v(C['CYAN']),
                                   rim2=v(K.mix(C['CYAN'], C['IVORY'], 0.5)), glow=v(C['BLUE']), rim_k=0.85,
                                   glow_k=0.8, text2=v(C['IVORY'], 0.56), text3=v(C['PEACH'], 0.32))
    ui.FONT_ALIAS.update(mono=FONT_MONO, mono_bold=FONT_MONO_BOLD, mono_reg='JetBrainsMono-Regular',
                         serif=FONT_SERIF)
    # old-client copy defaults -> neutral / verified Oktrum copy
    _set_defaults(ui.money, symbol='')
    _set_defaults(ui.button, text='Get Started')
    _set_defaults(ui.search_bar, placeholder='Search markets')
    _set_defaults(ui.app_window, title='oktrum.com', header='Trade With Confidence')
    orig = ui.__dict__.setdefault('_ok_orig', {})
    orig.setdefault('col', ui.col)
    orig.setdefault('app_window', ui.app_window)
    orig.setdefault('badge', ui.badge)

    def col(c):
        """ui.col with Oktrum's remap of old-brand hex literals (HEX_REMAP)."""
        if isinstance(c, str) and c.startswith('#'):
            c = HEX_REMAP.get(c.upper(), c)
        return orig['col'](c)
    col.__wrapped__ = orig['col']
    ui.col = col
    ui.app_window = _app_window_wrapper(orig['app_window'])
    ui.badge = _badge
    _note('ui', 'LOOKS neon/airy grad_hi light blue->cyan; amber navy glass + violet->cyan; airy text2/text3 '
                'darker; NEW cine; traffic lights DOWN/AMBER/UP; badge disc brand gradient; copy defaults: money '
                'symbol "", app_window oktrum.com / Trade With Confidence, button Get Started, badge Bank-Tier '
                'Encryption, search_bar Search markets; ui.col remaps old-brand hex; fonts mono/serif')


def _app_window_wrapper(orig):
    sig = inspect.signature(inspect.unwrap(orig))

    @functools.lru_cache(maxsize=16)
    def app_window(*args, **kw):
        win = orig(*args, **kw)
        b = sig.bind(*args, **kw)
        b.apply_defaults()
        a = b.arguments
        if not a['traffic']:
            return win
        f = win.face.copy()
        p = win.pad
        TB = 88
        S = ui.Surf(f.shape[1], f.shape[0], f)
        dark = ui.LOOKS[a['look']].dark
        for i, nm in enumerate(('DOWN', 'AMBER', 'UP')):
            cx, cy = p + 44 + i * 30, p + TB / 2
            S.circle(cx, cy, 9.2, ui._v(K.C[nm], 0.85 if dark else 1.0), 1.0)
            S.circle(cx - 2, cy - 2.5, 3.0, ui._v(K.C['WHITE']), 0.35)
        return ui.derive_panel(win, ui._ro(f), dict(win.meta))
    app_window.__wrapped__ = orig
    app_window.__doc__ = (orig.__doc__ or '') + '\n    [oktrum_kit] traffic lights DOWN / AMBER / UP.'
    return app_window


@functools.lru_cache(maxsize=16)
def _badge(text='Bank-Tier Encryption', sub=None, look='neon', icon_name='shield', size=34, glass=True,
           accent=None):
    """Badge -> glass Panel: a brand-gradient disc (VIOLET -> CYAN, or accent=(c0, c1)) with a white icon + text
    (+ sub line). Replaces ui.badge's gold disc (same arguments, plus accent).
        ui.badge('PCI DSS Compliant', look='airy', icon_name='shield').draw(cv, 540, 1290)"""
    L = ui.LOOKS[look]
    tw = max(ui.measure(text, size, 'ui'), ui.measure(sub, 28, 'body') if sub else 0)
    h = 112 if sub else 88
    w = int(math.ceil((tw + 24 + 64 + 20 + 36) / 8) * 8)
    base = ui.glass_card(w, h, h / 2, look, rim=0.5, glow=0.6, shadow=0.8 if glass else 0.0)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    cx, cy = p + 16 + 32, p + h / 2
    c0, c1 = (ui.col(accent[0]), ui.col(accent[1])) if accent else (ui._v(K.C['VIOLET']), ui._v(K.C['CYAN']))
    a, X0, Y0 = S.circle(cx, cy, 32, c0)
    S.fill(a, X0, Y0, ui._lingrad(a.shape[1], a.shape[0], c0, c1, -45), 1.0)
    S.glow(a, X0, Y0, c0 * 0.5 + c1 * 0.5, (5, 14), 0.5 if L.dark else 0.22)
    S.sheen(cx - 31, cy - 31, 62, 62, 31, 0.16, 0.0, 0.55)
    S.paste(ui.icon(icon_name, 36, K.C['WHITE'], stroke=2.4), cx, cy, anchor=(0.5, 0.5))
    tx = p + 16 + 64 + 20
    if sub:
        ui.put_text(f, tx, p + h / 2 - 6, text, size, 'ui', L.text, 'ls')
        ui.put_text(f, tx, p + h / 2 + 32, sub, 28, 'body', L.text2, 'ls')
    else:
        ui.put_text(f, tx, p + h / 2, text, size, 'ui', L.text, 'lm')
    return ui.derive_panel(base, f)


def _apply_footage():
    G = F.GRADES
    G['neon'] = dict(G['neon'], wb=(0.98, 1.0, 1.03), black_tint=(0.06, 0.10, 0.30),
                     shadow_tint=(-0.010, 0.004, 0.040), highlight_tint=(-0.008, 0.010, 0.020))
    G['amber'] = dict(G['amber'], wb=(0.98, 1.0, 1.04), black_tint=(0.08, 0.14, 0.30),
                      shadow_tint=(-0.008, 0.006, 0.030), highlight_tint=(0.0, 0.010, 0.018))
    G['airy'] = dict(G['airy'], wb=(0.99, 1.0, 1.02), black_tint=(0.55, 0.58, 0.70),
                     shadow_tint=(0.0, 0.004, 0.016), highlight_tint=(0.0, 0.004, 0.010))
    G['cine'] = dict(G['neon'], exposure=-0.10, contrast=1.30, black=0.04, sat=0.92,
                     highlight_tint=(-0.012, 0.008, 0.024))
    for nm in dir(F):
        fn = getattr(F, nm)
        if callable(fn) and hasattr(fn, 'cache_clear'):
            fn.cache_clear()
    _note('footage', 'GRADES neon/amber/airy navy blacks + cool highlights; NEW cine')


def apply():
    """Apply the Oktrum profile to this process (idempotent; runs on import). Returns PROFILE."""
    if getattr(K, '_OKTRUM_PROFILE', False):
        return PROFILE
    _apply_tokens()
    _apply_core()
    _apply_core_wrappers()
    _apply_type()
    _apply_ui()
    _apply_footage()
    K._OKTRUM_PROFILE = True
    return PROFILE


apply()

BLUE, VIOLET, CYAN, NAVY = _lin('BLUE'), _lin('VIOLET'), _lin('CYAN'), _lin('NAVY')
UP, DOWN, BLUE_DEEP, UP_DEEP, DOWN_DEEP = _lin('UP'), _lin('DOWN'), _lin('BLUE_DEEP'), _lin('UP_DEEP'), _lin('DOWN_DEEP')
INK, IVORY, HOT_PINK, PLUM = _lin('INK'), _lin('IVORY'), _lin('HOT_PINK'), _lin('PLUM')
for _a in (BLUE, VIOLET, CYAN, NAVY, UP, DOWN, BLUE_DEEP, UP_DEEP, DOWN_DEEP, INK, IVORY, HOT_PINK, PLUM):
    _a.setflags(write=False)
