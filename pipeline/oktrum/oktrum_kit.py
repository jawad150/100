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

WIDGETS (part B; pure functions of their arguments and t; static parts cached; costs in KIT.md)
    OK.dot_sphere(cv, cam, (0, -120, 0), 330, t, assemble=K.ramp(t, 0.2, 1.6, 'linear'))   # 3D halftone logo sphere
    spr = OK.candles(28, 900, 560, K.ramp(t, 0.3, 2.0, 'linear'), t, look='cine', crash=0.0); K.draw(cv, spr, 540, 900)
    OK.ticker_tape(cv, t, 1560, look='neon')            # or plane=dict(cam=cam, center=P, width=1600, rot=(..))
    K.draw(cv, OK.line_chart(900, 420, None, K.ramp(t, 0.5, 2.5, 'inout_sine'), 'cine'), 540, 1100)
    win = OK.trade_window(look='cine', hover=hv, press=pr); win.plane(cv, cam, P, 760, rot=(6, -12, 0))
    OK.order_toast('Order Filled — BUY 0.5 BTC @ 67,200', 'cine').draw(cv, 540, 1240, opacity=u)
    OK.blink(cv, K.remap(t, 0.6, 1.3))                  # eyelids over the whole frame, before K.post
    OK.streaks(cv, [(820, 640, 1.0)], strength=K.impulse(t, 2.1, 5))   # local anamorphic streaks
    OK.light_rays(cv, (760, 380), 0.5, t, angle=120, cone=110)          # local volumetric rays
    ui.orbit_ring(cv, cam, [OK.asset_tag(*row, look='neon') for row in OK.TICKERS[:6]], phase=t * .05, look='neon')
    OK.TICKERS (INTAKE.md section 3 rows), OK.PAD (chart sprite padding), OK.blink_closure(u).
    Per-frame sprite cache: byte budget OKTRUM_KIT_CACHE_MB (default 160 MB per worker).

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


# =============================================================================================================
# PART B: shared widgets of the three Oktrum reels (pure functions of their arguments and t)
# =============================================================================================================
PAD = 40                                   # transparent padding (glow room) round chart sprites; plot origin
_CACHE_MB = float(os.environ.get('OKTRUM_KIT_CACHE_MB', '160'))   # per-frame sprite cache budget (per worker)


class _ByteLRU:
    """Byte-budgeted LRU for per-frame sprites (charts at quantised progress, button states)."""

    def __init__(self, budget_mb):
        self.budget = int(budget_mb * 2 ** 20)
        self.d, self.used = {}, 0

    def get(self, key, fn):
        if key in self.d:
            v = self.d.pop(key)
            self.d[key] = v
            return v
        v = fn()
        nb = _nbytes(v)
        if nb > self.budget:
            return v
        self.d[key] = v
        self.used += nb
        while self.used > self.budget and self.d:
            k0 = next(iter(self.d))
            self.used -= _nbytes(self.d.pop(k0))
        return v


def _nbytes(v):
    if isinstance(v, np.ndarray):
        return v.nbytes
    if isinstance(v, ui.Panel):
        return v.face.nbytes + v.shadow.nbytes
    if isinstance(v, tuple):
        return sum(_nbytes(x) for x in v)
    return 1024


_LRU = _ByteLRU(_CACHE_MB)


def _ro(a):
    a.setflags(write=False)
    return a


def _ck(c):
    """Hashable key of a colour spec."""
    if c is None or isinstance(c, str):
        return c
    return tuple(round(float(x), 5) for x in np.ravel(np.asarray(c, np.float32)))


def _rgb(c, default):
    if c is None:
        return np.asarray(default, np.float32)
    if isinstance(c, str):
        return np.asarray(K.C[c] if c in K.C else K.hexlin(c), np.float32)
    return np.asarray(c, np.float32)[:3]


def _q(x, n):
    return round(float(x) * n) / n


def _fmt(v, dec=None):
    """Price string with thousands separators: 67200 -> '67,200.0'; dec auto by magnitude."""
    if dec is None:
        a = abs(v)
        dec = 4 if a < 10 else (2 if a < 1000 else (1 if a < 100000 else 0))
    return '{:,.{}f}'.format(v, dec)


def _region_over(cv, x0, y0, rgb, a, opacity=1.0, add=None):
    """'over' premultiplied rgb (h, w, 3) + alpha (h, w) into cv at (x0, y0) (clipped); add = extra emissive."""
    h, w = a.shape
    H0, W0 = cv.shape[:2]
    u0, v0, u1, v1 = max(0, -x0), max(0, -y0), min(w, W0 - x0), min(h, H0 - y0)
    if u1 <= u0 or v1 <= v0:
        return
    reg = cv[y0 + v0:y0 + v1, x0 + u0:x0 + u1]
    k = np.float32(opacity)
    aa = a[v0:v1, u0:u1, None] * k
    reg[..., :3] *= 1 - aa
    reg[..., :3] += rgb[v0:v1, u0:u1] * k
    if add is not None:
        reg[..., :3] += add[v0:v1, u0:u1] * k
    reg[..., 3:4] *= 1 - aa
    reg[..., 3:4] += aa


def _blur_up(small, sigmas, weights, size):
    """Sum of gaussian blurs of a low-res buffer, resized up to size=(w, h)."""
    acc = None
    for s, wt in zip(sigmas, weights):
        b = cv2.GaussianBlur(small, (0, 0), s, borderType=cv2.BORDER_CONSTANT) * np.float32(wt)
        acc = b if acc is None else acc + b
    return cv2.resize(acc, size, interpolation=cv2.INTER_LINEAR)


# ------------------------------------------------------------------------------------------------ dot sphere
@functools.lru_cache(maxsize=8)
def _fib_sphere(n, seed):
    i = np.arange(n, dtype=np.float64) + 0.5
    phi = np.arccos(1.0 - 2.0 * i / n)
    th = math.pi * (1.0 + 5 ** 0.5) * i
    p = np.c_[np.cos(th) * np.sin(phi), -np.cos(phi), np.sin(th) * np.sin(phi)]
    rng = np.random.default_rng(seed)
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    sc = d * rng.uniform(1.6, 4.4, n)[:, None]
    sc[:, 2] -= rng.uniform(0.0, 2.2, n)              # part of the cloud starts between sphere and camera
    delay = rng.uniform(0.0, 0.45, n)
    twf, twp = rng.uniform(0.35, 1.3, n), rng.uniform(0, 2 * math.pi, n)
    return tuple(_ro(a) for a in (p, sc, delay, twf, twp))


def dot_sphere(cv, cam, center=(0.0, 0.0, 0.0), radius=320.0, t=0.0, rot=(-14.0, 0.0, -8.0), spin=12.0,
               assemble=1.0, n=2600, dot=0.30, light=(0.45, 0.32, -0.83), back=0.22, look='neon', gain=None,
               glow=1.0, tint=0.35, twinkle=0.12, opacity=1.0, seed=3, dof=True, core=0.8):
    """The Oktrum halftone dot sphere (logo mark) as a true 3D point cloud, drawn into cv in place.
    Fibonacci points on a sphere of `radius` world units at `center`; rot=(rx, ry, rz) degrees plus spin deg/s
    of yaw; dot radius follows the logo halftone falloff from `light` (direction toward the light, world, y down,
    -z = toward the viewer); back-facing dots are small and dim (`back`); lit dots lean light blue, shadowed ones
    violet (`tint`); emissive blue + soft glow + hot cores (`core`) on dark looks, flat BLUE paint on the light look. assemble 0..1
    flies the dots in from a scattered swirling cloud (staggered). Thin-lens DOF from cam (dof=False: sharp).
    Returns dict(xy=screen centre, r=screen radius px, bbox) or None.
        OK.dot_sphere(cv, cam, (0, -120, 0), 330, t, assemble=K.ramp(t, 0.2, 1.6, 'out_cubic'))"""
    if opacity <= 1e-3:
        return None
    dark = not _is_light(look)
    p, sc, delay, twf, twp = _fib_sphere(int(n), int(seed))
    c = np.asarray(center, np.float64)
    R = K._rot(rot[0], rot[1] + spin * t, rot[2])
    Nw = p @ R.T
    tgt = c + Nw * radius
    L = np.asarray(light, np.float64)
    L = L / np.linalg.norm(L)
    nl = Nw @ L
    view = cam.pos - tgt
    facing = np.einsum('ij,ij->i', Nw, view) / np.linalg.norm(view, axis=1)
    front = np.clip((facing + 0.06) / 0.30, 0, 1)
    front = front * front * (3 - 2 * front)
    hs = np.clip((nl - 0.02) / 0.9, 0, 1) ** 0.9
    spacing = math.sqrt(4 * math.pi / len(p)) * radius
    size = spacing * dot * (front * (0.10 + 0.90 * hs) + (1 - front) * 0.30)
    if dark:                                          # punchier halftone in light: dim shadow side, hot lit side,
        rim = np.clip(1 - np.abs(facing), 0, 1) ** 4   # plus a fresnel lift on the limb (poster sphere)
        inten = front * (0.20 + 0.80 * hs ** 1.2 + 0.45 * rim) + (1 - front) * back
    else:
        inten = front * (0.42 + 0.58 * hs) + (1 - front) * back
    hue = 0.5 + tint * (hs - 0.45) * front - 0.2 * tint * (1 - front)
    if twinkle:
        inten = inten * (1 + twinkle * np.sin(2 * math.pi * twf * t + twp))
    P = tgt
    a = float(np.clip(assemble, 0.0, 1.0))
    if a < 1.0:
        e = np.clip((a - delay) / 0.55, 0, 1)
        e = 1 - (1 - e) ** 3
        ang = (1 - e) * 1.9 + 0.12 * t
        ca, sa = np.cos(ang), np.sin(ang)
        sx = sc[:, 0] * ca - sc[:, 2] * sa
        sz = sc[:, 0] * sa + sc[:, 2] * ca
        start = c + np.c_[sx, sc[:, 1], sz] * radius
        P = start + (tgt - start) * e[:, None]
        size = spacing * 0.15 + (size - spacing * 0.15) * e
        inten = 0.85 + (inten - 0.85) * e
        hue = 0.78 + (hue - 0.78) * e
    xy, z = cam.project(P)
    ok = np.isfinite(xy[:, 0]) & (z > cam.near)
    if not ok.any():
        return None
    xy, z, size, inten, hue, front = xy[ok], z[ok], size[ok], inten[ok], hue[ok], front[ok]
    r = size * cam.focal / z
    if dof and cam.aperture > 0:
        coc = cam.coc(z)
        re = np.sqrt(r * r + coc * coc)
        inten = inten * (r / re) ** 2
        r = re
    small = r < 0.8
    inten = np.where(small, inten * (r / 0.8) ** 2, inten)
    r = np.maximum(r, 0.8)
    gpad = 0 if not (dark and glow > 0) else int(24 + 0.08 * radius * cam.focal / max(cam.depth(c), 1))
    H0, W0 = cv.shape[:2]
    x0 = int(max(0, math.floor((xy[:, 0] - r).min()) - gpad - 2))
    y0 = int(max(0, math.floor((xy[:, 1] - r).min()) - gpad - 2))
    x1 = int(min(W0, math.ceil((xy[:, 0] + r).max()) + gpad + 2))
    y1 = int(min(H0, math.ceil((xy[:, 1] + r).max()) + gpad + 2))
    if x1 <= x0 or y1 <= y0:
        return None
    bw, bh = x1 - x0, y1 - y0
    if dark:
        c0, c1, c2 = VIOLET, BLUE, np.asarray(K.mix(BLUE, HOT_PINK, 0.7), np.float32)
        g = 1.45 if gain is None else gain
    else:
        c0, c1, c2 = VIOLET, BLUE, BLUE
        g = 1.0 if gain is None else gain
    hh = np.clip(hue, 0, 1)[:, None]
    colr = np.where(hh < 0.5, c0 + (c1 - c0) * np.clip(hh * 2, 0, 1), c1 + (c2 - c1) * np.clip(hh * 2 - 1, 0, 1))
    colr = colr * np.clip(inten, 0, 1)[:, None] * 255.0
    order = np.argsort(-z)
    X = np.round((xy[order, 0] - x0) * 16).astype(np.int32).tolist()
    Y = np.round((xy[order, 1] - y0) * 16).astype(np.int32).tolist()
    Rr = np.round(r[order] * 16).astype(np.int32).tolist()
    nc = 3 if dark else 4
    if dark:
        cl = np.round(colr[order]).astype(np.int32)
    else:                                         # paint: premultiplied colour, alpha from the dot weight
        al = np.clip(front * 1.0 + (1 - front) * back * 0.6, 0, 1)[order] if a >= 1.0 else np.ones(len(order))
        cb = colr[order] / np.maximum(np.clip(inten[order], 0, 1), 1e-3)[:, None]
        cl = np.round(np.c_[cb * al[:, None], al * 255.0]).astype(np.int32)
    cl = [tuple(v) for v in cl.tolist()]
    buf = np.zeros((bh, bw, nc), np.uint8)
    circ, AA = cv2.circle, cv2.LINE_AA
    for x_, y_, r_, c_ in zip(X, Y, Rr, cl):
        circ(buf, (x_, y_), r_, c_, -1, AA, 4)
    if dark and core > 0:                         # hot white-blue cores on the lit dots (sparkle, feeds bloom)
        hot = np.clip((hue[order] - 0.5) * 3.0, 0, 1) * np.clip(inten[order], 0, 1) * core
        sel = np.nonzero((hot > 0.05) & (r[order] > 1.6))[0]
        if len(sel):
            cc = np.asarray(K.mix(HOT_PINK, IVORY, 0.55), np.float32)
            ccl = np.round(cc[None] * hot[sel, None] * 255.0).astype(np.int32).tolist()
            for j, c_ in zip(sel.tolist(), ccl):
                circ(buf, (X[j], Y[j]), max(8, int(Rr[j] * 0.48)), tuple(c_), -1, AA, 4)
    reg = cv[y0:y1, x0:x1]
    k = np.float32(g * opacity / 255.0)
    if dark:
        rgb = np.multiply(buf, k, dtype=np.float32)
        if glow > 0:
            sm = cv2.resize(rgb, (max(1, bw // 4), max(1, bh // 4)), interpolation=cv2.INTER_AREA)
            rgb += _blur_up(sm, (1.5, 4.5, 13.0), (0.30 * glow, 0.20 * glow, 0.14 * glow), (bw, bh))
        reg[..., :3] += rgb                       # emissive light (alpha 0): dots never occlude, they glow
    else:
        S = np.multiply(buf, np.float32(1 / 255.0), dtype=np.float32)
        S[..., :3] *= np.float32(g)
        K._blend(reg, S, opacity, 'over')
    cxy, cz = cam.project(c[None])
    return dict(xy=(float(cxy[0, 0]), float(cxy[0, 1])), r=float(radius * cam.focal / max(cz[0], 1e-3)),
                bbox=(x0, y0, x1, y1))


# ------------------------------------------------------------------------------------------------ small drawing
def _fillrect(img, x0, y0, x1, y1, rgb, a=1.0, vgrad=None, emit=False):
    """Anti-aliased (fractional-edge) axis-aligned rect 'over' img (premultiplied RGBA) in place.
    vgrad=(g_top, g_bottom) multiplies rgb down the rect; emit=True adds light (alpha unchanged)."""
    H0, W0 = img.shape[:2]
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    X0, Y0 = max(0, int(math.floor(x0))), max(0, int(math.floor(y0)))
    X1, Y1 = min(W0, int(math.ceil(x1))), min(H0, int(math.ceil(y1)))
    if X1 <= X0 or Y1 <= Y0:
        return
    ix = np.arange(X0, X1, dtype=np.float32)
    iy = np.arange(Y0, Y1, dtype=np.float32)
    cx = np.clip(np.minimum(x1, ix + 1) - np.maximum(x0, ix), 0, 1)
    cy = np.clip(np.minimum(y1, iy + 1) - np.maximum(y0, iy), 0, 1)
    m = (cy[:, None] * cx[None, :] * np.float32(a))[..., None]
    c = np.asarray(rgb, np.float32)[None, None, :3]
    if vgrad is not None:
        gy = np.linspace(vgrad[0], vgrad[1], Y1 - Y0, dtype=np.float32)[:, None, None]
        c = c * gy
    reg = img[Y0:Y1, X0:X1]
    if emit:
        reg[..., :3] += c * m
        return
    reg[..., :3] = reg[..., :3] * (1 - m) + c * m
    reg[..., 3:4] = reg[..., 3:4] * (1 - m) + m


@functools.lru_cache(maxsize=32)
def _tri(size, up, color):
    """Anti-aliased ▲ / ▼ sprite (size px), colour key -> read-only sprite."""
    s = 4
    n = int(size)
    m = np.zeros((n * s, n * s), np.uint8)
    w, h = n * s, n * s
    pts = np.array([[w * 0.5, h * 0.14], [w * 0.95, h * 0.86], [w * 0.05, h * 0.86]]) if up else \
        np.array([[w * 0.05, h * 0.14], [w * 0.95, h * 0.14], [w * 0.5, h * 0.86]])
    cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (n, n), interpolation=cv2.INTER_AREA)
    out = np.dstack([a[..., None] * np.asarray(color, np.float32), a]).astype(np.float32)
    return _ro(out)


def _arrow_text(dst, x, y, chg, size, col, fnt='mono', anchor='l'):
    """'▲ +2.34%' at baseline-left x (or right-aligned when anchor='r'); returns the width."""
    txt = '{:+.2f}%'.format(chg)
    tw = ui.measure(txt, size, fnt)
    ts = int(round(size * 0.62))
    gap = int(size * 0.28)
    wtot = ts + gap + tw
    xl = x - wtot if anchor == 'r' else x
    ui.paste(dst, _tri(ts, chg >= 0, _ck(col)), xl, y - ts - int(size * 0.04))
    ui.put_text(dst, xl + ts + gap, y, txt, size, fnt, col, 'ls')
    return wtot


# ------------------------------------------------------------------------------------------------ candles
@functools.lru_cache(maxsize=16)
def _candle_series(n, seed, price, vol, trend):
    rng = np.random.default_rng(seed)
    ret = rng.normal(0.0, vol, n)
    ret += 1.1 * vol * np.sin(np.arange(n) * 0.42 + seed)          # waves, not white noise
    ret += trend * vol - ret.mean()                                   # exact drift: trend > 0 rises
    close = np.exp(np.cumsum(ret))
    close = close / close[-1] * price
    opn = np.r_[close[0] * math.exp(-ret[0]), close[:-1]]
    wick = np.abs(rng.normal(0, vol * 0.55, (2, n))) + vol * 0.12
    hi = np.maximum(opn, close) * (1 + wick[0])
    lo = np.minimum(opn, close) * (1 - wick[1])
    return tuple(_ro(a) for a in (opn, close, hi, lo))


def _chart_cols(look):
    dark = not _is_light(look)
    c = ink(look)
    if dark:
        return dict(dark=True, up=UP, down=DOWN, line=IVORY, line_a=0.07, label=c['text2'], tag_text=INK, c=c)
    return dict(dark=False, up=UP_DEEP, down=DOWN_DEEP, line=INK, line_a=0.08, label=c['text2'],
                tag_text=_lin('WHITE'), c=c)


def _candles_layout(n, w, h, axis):
    aw = 150 if axis else 0
    x0, x1 = PAD + 12, PAD + w - aw - 12
    y0, y1 = PAD + 28, PAD + h - 28
    slot = (x1 - x0) / (n + 1)
    return x0, x1, y0, y1, slot, aw


@functools.lru_cache(maxsize=12)
def _candles_base(n, w, h, look, seed, price, vol, trend, axis, drop, grid):
    cl = _chart_cols(look)
    f = np.zeros((h + 2 * PAD + int(drop), w + 2 * PAD, 4), np.float32)
    x0, x1, y0, y1, slot, aw = _candles_layout(n, w, h, axis)
    o, c, hi, lo = _candle_series(n, seed, price, vol, trend)
    vmin, vmax = float(lo.min()), float(hi.max())
    span = vmax - vmin
    vmin, vmax = vmin - 0.08 * span, vmax + 0.08 * span
    for k in range(grid + 1):
        yy = y0 + (y1 - y0) * k / grid
        _fillrect(f, x0, yy - 0.6, x1 + (aw * 0.15 if axis else 0), yy + 0.6, cl['line'], cl['line_a'] * 1.4)
        if axis:
            v = vmax - (vmax - vmin) * k / grid
            ui.put_text(f, PAD + w - 12, yy + 8, _fmt(v, 0 if abs(v) >= 1000 else None), 22, 'mono_reg',
                        cl['label'], 'rs')
    nv = 6
    for k in range(1, nv):
        xx = x0 + (x1 - x0) * k / nv
        _fillrect(f, xx - 0.6, y0, xx + 0.6, y1, cl['line'], cl['line_a'])
    return _ro(f), (vmin, vmax)


def candles(n=28, w=900, h=560, progress=1.0, t=0.0, seed=7, crash=0.0, look='neon', price=67200.0, vol=0.004,
            trend=0.3, axis=True, drop=0, grid=4, glow=1.0, tick=1.0, info=False):
    """Glass-UI candlestick chart sprite (h + 2*PAD + drop, w + 2*PAD; plot box starts at (PAD, PAD)).
    UP / DOWN bodies (glass: dim gradient fill, bright edge, emissive glow on dark looks; solid UP_DEEP /
    DOWN_DEEP on the light look), wicks, faint grid, mono price axis (axis=False hides it) and a last-price tag
    with a dashed line. progress 0..1 builds the candles left to right (each grows from its open); the newest
    candle ticks with t (tick = amplitude); crash 0..1 adds one long DOWN candle in the reserved last slot that
    extends to the plot bottom at 1 (and `drop` px further into extra room below the plot).
    Writable per-frame sprite; info=True returns (sprite, dict(last=(x, y), tip=(x, y) crash tip, price=v)).
        spr = OK.candles(28, 900, 560, K.ramp(t, 0.3, 2.0, 'linear'), t, look='cine'); K.draw(cv, spr, 540, 900)"""
    n, w, h = int(n), int(w), int(h)
    cl = _chart_cols(look)
    base, (vmin, vmax) = _candles_base(n, w, h, look, int(seed), float(price), float(vol), float(trend), bool(axis),
                                       int(drop), int(grid))
    f = base.copy()
    x0, x1, y0, y1, slot, aw = _candles_layout(n, w, h, axis)
    o, c, hi, lo = (a.copy() for a in _candle_series(n, int(seed), float(price), float(vol), float(trend)))
    yv = lambda v: y0 + (vmax - v) / (vmax - vmin) * (y1 - y0)
    vy = lambda y: vmax - (y - y0) / (y1 - y0) * (vmax - vmin)
    pn = float(np.clip(progress, 0, 1)) * n
    last = max(0, min(n - 1, int(math.ceil(pn)) - 1))
    if tick and pn > 0:
        amp = tick * (0.45 * abs(c[last] - o[last]) + vol * price * 0.35)
        c[last] = c[last] + amp * K.wiggle(t, 1.6, 1.0, seed=int(seed) + 11)
        hi[last] = max(hi[last], c[last], o[last])
        lo[last] = min(lo[last], c[last], o[last])
    Hs, Ws = f.shape[:2]
    gs = np.zeros((Hs // 4 + 1, Ws // 4 + 1, 3), np.float32)
    bwid = max(2.0, slot * 0.62)
    dark = cl['dark']
    last_xy = (x0, yv(c[0]))
    last_v = c[0]

    def body(i, vo, vc, vh, vl, u, col, hot=1.0):
        xc = x0 + slot * (i + 0.5)
        yo, yc = yv(vo), yv(vc)
        yc = yo + (yc - yo) * u
        yh = yo + (yv(vh) - yo) * u
        yl = yo + (yv(vl) - yo) * u
        al = min(1.0, u * 3)
        ww = max(1.6, slot * 0.07)
        _fillrect(f, xc - ww / 2, yh, xc + ww / 2, yl, col * (1.15 if dark else 1.0), 0.9 * al)
        top, bot = min(yo, yc), max(yo, yc)
        if bot - top < 1.5:
            top, bot = (top + bot) / 2 - 0.75, (top + bot) / 2 + 0.75
        if dark:
            _fillrect(f, xc - bwid / 2, top, xc + bwid / 2, bot, col * 1.5, 0.95 * al)
            e = 2.0
            if bwid > 3 * e and bot - top > 3 * e:
                _fillrect(f, xc - bwid / 2 + e, top + e, xc + bwid / 2 - e, bot - e, col * 0.55, 0.82 * al,
                          vgrad=(1.35, 0.55))
        else:
            _fillrect(f, xc - bwid / 2, top, xc + bwid / 2, bot, col, al)
            if bwid > 6 and bot - top > 6:
                _fillrect(f, xc - bwid / 2 + 2, top + 2, xc + bwid / 2 - 2, top + min(10, (bot - top) / 2),
                          IVORY, 0.18 * al, emit=False)
        cv2.rectangle(gs, (int((xc - bwid / 2) / 4), int(top / 4)), (int(math.ceil((xc + bwid / 2) / 4)),
                      int(math.ceil(bot / 4))), tuple(float(v) for v in col * al * hot), -1)
        return xc, yc

    for i in range(min(n, int(math.ceil(pn)))):
        u = float(np.clip(pn - i, 0, 1))
        u = 1 - (1 - u) ** 3
        col = cl['up'] if c[i] >= o[i] else cl['down']
        last_xy = body(i, o[i], c[i], hi[i], lo[i], u, col)
        last_v = o[i] + (c[i] - o[i]) * u
    tip = None
    if crash > 0:
        vo = c[n - 1]
        yo = yv(vo)
        ybot = y1 + int(drop)
        yc = yo + (ybot - yo) * float(np.clip(crash, 0, 1))
        last_xy = body(n, vo, vy(yc), vo * (1 + vol * 0.3), vy(yc), 1.0, cl['down'], hot=2.2)
        tip = (last_xy[0], yc)
        last_v = vy(yc)
    if glow > 0:
        k = (0.9 if dark else 0.22) * glow
        g = _blur_up(gs, (2.0, 6.0), (0.55 * k, 0.45 * k), (gs.shape[1] * 4, gs.shape[0] * 4))[:Hs, :Ws]
        f[..., :3] += g
    # last price: dashed line + tag on the axis
    if pn > 0 or crash > 0:
        ly = float(np.clip(last_xy[1], y0 - 10, Hs - 30))
        up_last = crash <= 0 and c[last] >= o[last]
        tc = cl['up'] if up_last else cl['down']
        xe = x1 + (aw * 0.15 if axis else 0)
        xx = x0
        while xx < xe:
            _fillrect(f, xx, ly - 0.8, min(xx + 9, xe), ly + 0.8, tc, 0.55)
            xx += 16
        if axis:
            txt = _fmt(max(0.0, last_v))
            tw = ui.measure(txt, 24, 'mono_bold')
            S = ui.Surf(Ws, Hs, f)
            bx = PAD + w - aw + 8
            bwd = max(aw - 14, tw + 24)
            a_, X0, Y0 = S.rrect(bx, ly - 21, bwd, 42, 10, tc)
            if dark:
                S.glow(a_, X0, Y0, tc, (5, 14), 0.5)
            ui.put_text(f, bx + bwd / 2, ly + 9, txt, 24, 'mono_bold', cl['tag_text'], 'ms')
    if info:
        return f, dict(last=last_xy, tip=tip, price=float(last_v))
    return f


# ------------------------------------------------------------------------------------------------ ticker tape
# INTAKE.md section 3: the first three rows carry the site's own figures; the rest are illustrative UI values
# (never presented as live quotes).
TICKERS = (('EUR/USD', '1.0847', 0.12), ('BTC/USD', '67,420', 2.34), ('XAU/USD', '2,338.40', -0.44),
           ('AAPL', '228.52', 0.86), ('GBP/USD', '1.2714', -0.08), ('ETH/USD', '3,412.60', 1.92),
           ('NVDA', '131.26', 3.10), ('S&P 500', '5,612.30', 0.41), ('USD/JPY', '149.82', -0.21),
           ('WTI OIL', '78.64', -0.62), ('TSLA', '248.50', 1.47), ('NASDAQ', '19,743.10', 0.66),
           ('SOL/USD', '152.30', 4.05), ('DAX 40', '18,912.40', -0.18), ('XAG/USD', '29.84', 0.53))


@functools.lru_cache(maxsize=6)
def _tape_strip(items, h, size, look):
    c = ink(look)
    gap_in, gap_sep = int(size * 0.45), int(size * 1.7)
    ms = size * 0.92
    parts, x = [], gap_sep // 2
    for lab, price, chg in items:
        wl = ui.measure(lab, size, FONT_UI)
        wp = ui.measure(price, ms, 'mono')
        wc = int(ms * 0.62) + int(ms * 0.28) + ui.measure('{:+.2f}%'.format(chg), ms, 'mono')
        parts.append((x, lab, price, chg, wl, wp))
        x += wl + gap_in + wp + gap_in + wc + gap_sep
    W = int(math.ceil(x))
    f = np.zeros((h, W, 4), np.float32)
    yb = h / 2 + size * 0.36
    for x, lab, price, chg, wl, wp in parts:
        ui.put_text(f, x, yb, lab, size, FONT_UI, c['text'], 'ls')
        ui.put_text(f, x + wl + gap_in, yb, price, ms, 'mono', c['text'], 'ls')
        _arrow_text(f, x + wl + gap_in + wp + gap_in, yb, chg, ms, c['up'] if chg >= 0 else c['down'])
    for x, *_ in parts:                                   # separators: small accent dots between items
        S = ui.Surf(W, h, f)
        S.circle(x - gap_sep / 2, h / 2, 3.2, c['accent'], 0.7)
    return _ro(np.concatenate([f, f], axis=1)), W


@functools.lru_cache(maxsize=6)
def _tape_band(w, h, look, fade):
    dark = not _is_light(look)
    f = np.zeros((h, w, 4), np.float32)
    if dark:
        _fillrect(f, 0, 0, w, h, NAVY * 0.6, 0.72, vgrad=(1.6, 0.6))
        _fillrect(f, 0, 0, w, 1.5, CYAN * 0.9, 1.0, emit=True)
        _fillrect(f, 0, h - 1.5, w, h, BLUE * 0.8, 1.0, emit=True)
        _fillrect(f, 0, 1.5, w, 7, CYAN * 0.10, 1.0, emit=True)
    else:
        _fillrect(f, 0, 0, w, h, IVORY, 0.80)
        _fillrect(f, 0, 0, w, 1.5, INK, 0.10)
        _fillrect(f, 0, h - 1.5, w, h, INK, 0.12)
    if fade > 0:
        x = np.arange(w, dtype=np.float32)
        r = np.clip(np.minimum(x, w - 1 - x) / fade, 0, 1)
        f *= (r * r * (3 - 2 * r))[None, :, None]
    return _ro(f)


def ticker_tape(cv, t, y=1500, items=None, speed=110.0, look='neon', plane=None, h=88, size=32, w=None, fade=None,
                opacity=1.0):
    """Scrolling ticker strip drawn into cv: pair (Inter SemiBold) / price (JetBrains Mono) / ▲▼ change (UP /
    DOWN; UP_DEEP / DOWN_DEEP on the light look) on a glass band with cyan hairlines. items: tuple of
    (label, price_str, change_pct) (default TICKERS, INTAKE.md section 3); speed px/s (negative scrolls right).
    2D (plane=None): full width (or w px, centred) at screen y. 3D: plane=dict(cam=cam, center=(x, y, z),
    width=1400, rot=(rx, ry, rz)) projects the band (edges fade out).
        OK.ticker_tape(cv, t, 1560, look='neon')
        OK.ticker_tape(cv, t, 0, plane=dict(cam=cam, center=(0, 420, 120), width=1600, rot=(0, -18, -6)))"""
    items = TICKERS if items is None else tuple((str(a), str(b), float(c)) for a, b, c in items)
    w = int(w or (1600 if plane else cv.shape[1]))
    if fade is None:
        fade = 160 if plane else 0
    strip, SW = _tape_strip(items, int(h), float(size), look)
    off = (speed * t) % SW
    i0 = int(math.floor(off))
    fr = np.float32(off - i0)
    i0 %= SW
    need = w + 1
    idx = (np.arange(i0, i0 + need)) % (2 * SW)
    win = strip[:, idx]
    win = win[:, :-1] * (1 - fr) + win[:, 1:] * fr
    f = _tape_band(w, int(h), look, int(fade)).copy()
    if fade > 0:
        x = np.arange(w, dtype=np.float32)
        r = np.clip(np.minimum(x, w - 1 - x) / fade, 0, 1)
        win = win * (r * r * (3 - 2 * r))[None, :, None]
    K._blend(f, win, 1.0, 'over')
    if plane:
        kw = dict(plane)
        cam = kw.pop('cam')
        return K.draw_plane(cv, f, cam, kw.pop('center'), kw.pop('width', w), opacity=opacity, **kw)
    ui.paste(cv, f, (cv.shape[1] - w) // 2, int(round(y - h / 2)), opacity)
    return None


# ------------------------------------------------------------------------------------------------ line chart
def _catmull(P, k):
    if k <= 1 or len(P) < 3:
        return P
    Pp = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    out = []
    s = np.linspace(0, 1, k, endpoint=False)[:, None]
    for i in range(1, len(Pp) - 2):
        p0, p1, p2, p3 = Pp[i - 1], Pp[i], Pp[i + 1], Pp[i + 2]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s ** 2 +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-1:])
    return np.vstack(out)


def line_chart(w=900, h=420, values=None, progress=1.0, look='neon', color=None, fill=0.30, glow=1.0, width=4.0,
               dot=True, smooth=8, seed=5):
    """Glowing price line with a gradient fill under it, drawn on by `progress` 0..1 (arc length) with a glowing
    head dot. values: sequence of numbers (default: a seeded rising walk). Sprite (h + 2*PAD, w + 2*PAD), plot
    box at (PAD, PAD). Dark looks: BLUE -> CYAN emissive line; light look: BLUE_DEEP line, pale BLUE fill.
    Cached per (args, progress quantised to 1/400) in a byte-budgeted LRU (OKTRUM_KIT_CACHE_MB).
        K.draw(cv, OK.line_chart(900, 420, None, K.ramp(t, 0.5, 2.5, 'inout_sine'), 'cine'), 540, 1100)"""
    if values is None:
        rng = np.random.default_rng(seed)
        v = np.cumsum(rng.normal(0.35, 1.0, 40)) + 4 * np.sin(np.linspace(0, 5, 40))
        values = tuple(np.round(v, 4).tolist())
    key = ('line', int(w), int(h), tuple(float(x) for x in values), _q(np.clip(progress, 0, 1), 400), look,
           _ck(color), float(fill), float(glow), float(width), bool(dot), int(smooth))
    return _LRU.get(key, lambda: _ro(_line_chart(*key[1:])))


def _line_chart(w, h, values, progress, look, color, fill, glow, width, dot, smooth):
    dark = not _is_light(look)
    Ws, Hs = w + 2 * PAD, h + 2 * PAD
    f = np.zeros((Hs, Ws, 4), np.float32)
    if progress <= 0:
        return f
    v = np.asarray(values, np.float64)
    lo_, hi_ = v.min(), v.max()
    yn = (v - lo_) / max(hi_ - lo_, 1e-9)
    P = np.c_[PAD + np.linspace(0, w, len(v)), PAD + h * (0.92 - 0.82 * yn)]
    P = _catmull(P, int(smooth))
    seg = np.hypot(*np.diff(P, axis=0).T)
    cum = np.r_[0, np.cumsum(seg)]
    L = cum[-1] * progress
    j = int(np.searchsorted(cum, L, side='right'))
    if j >= len(P):
        Q = P
    else:
        u = (L - cum[j - 1]) / max(seg[j - 1], 1e-9)
        Q = np.vstack([P[:j], P[j - 1] + (P[j] - P[j - 1]) * u])
    head = Q[-1]
    c0 = _rgb(color, BLUE if dark else BLUE_DEEP)
    c1 = _rgb(color, CYAN if dark else BLUE_DEEP)
    gx = np.clip((np.arange(Ws, dtype=np.float32) - PAD) / w, 0, 1)[None, :, None]
    grad = c0 * (1 - gx) + c1 * gx
    # fill
    if fill > 0 and len(Q) > 1:
        poly = np.vstack([Q, [Q[-1, 0], PAD + h], [Q[0, 0], PAD + h]])
        m = np.zeros((Hs, Ws), np.uint8)
        cv2.fillPoly(m, [np.round(poly * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
        yy = np.clip((PAD + h - np.arange(Hs, dtype=np.float32)) / h, 0, 1) ** 1.6
        fa = m.astype(np.float32) * np.float32(fill / 255.0) * yy[:, None]
        fc = BLUE if dark else BLUE
        f[..., :3] += fa[..., None] * fc * (0.9 if dark else 1.0)
        f[..., 3] += fa if not dark else fa * 0.6
    # line
    m = np.zeros((Hs, Ws), np.uint8)
    cv2.polylines(m, [np.round(Q * 16).astype(np.int32)], False, 255, max(1, int(round(width))), cv2.LINE_AA, 4)
    la = m.astype(np.float32) * np.float32(1 / 255.0)
    gain = 1.5 if dark else 1.0
    f[..., :3] = f[..., :3] * (1 - la[..., None]) + la[..., None] * grad * gain
    f[..., 3] = f[..., 3] * (1 - la) + la
    if glow > 0:
        sm = cv2.resize(la[..., None] * grad, (Ws // 4, Hs // 4), interpolation=cv2.INTER_AREA)
        k = (1.0 if dark else 0.25) * glow
        f[..., :3] += _blur_up(sm, (1.5, 5.0), (0.8 * k, 0.6 * k), (Ws, Hs))
    if dot:
        S = ui.Surf(Ws, Hs, f)
        hc = c1 if progress > 0.5 else c0
        a_, X0, Y0 = S.circle(head[0], head[1], 9, IVORY if dark else hc)
        S.ring(head[0], head[1], 15, 2.0, hc * (1.4 if dark else 1.0), 0.8)
        if dark:
            S.glow(a_, X0, Y0, hc, (6, 18), 1.2, knock=0.0)
    return f


# ------------------------------------------------------------------------------------------------ glass UI
def asset_tag(label='BTC/USD', price=None, change=None, look='neon', color=None, size=32, h=80, rim=0.5):
    """Glass pill tag -> ui.Panel: colour dot + label (Inter SemiBold) + price (mono) + ▲▼ change (UP / DOWN).
    Works as an ui.orbit_ring item (Panels are accepted) or alone: tag.draw(cv, x, y) / tag.plane(cv, cam, P).
        tags = [OK.asset_tag(*row, look='neon') for row in OK.TICKERS[:6]]
        ui.orbit_ring(cv, cam, tags, phase=t * 0.05, look='neon', mid=lambda c: OK.dot_sphere(c, cam, ...))"""
    return _asset_tag(str(label), None if price is None else str(price), None if change is None else float(change),
                      look, _ck(color), float(size), int(h), float(rim))


@functools.lru_cache(maxsize=48)
def _asset_tag(label, price, change, look, color, size, h, rim):
    c = ink(look)
    dark = not _is_light(look)
    ms = size * 0.9
    dr = h * 0.13
    gap = size * 0.42
    wl = ui.measure(label, size, FONT_UI)
    wp = ui.measure(price, ms, 'mono') if price else 0
    wc = (int(ms * 0.62) + int(ms * 0.28) + ui.measure('{:+.2f}%'.format(change), ms, 'mono')) if change is not None \
        else 0
    w = int(math.ceil(h * 0.42 + 2 * dr + gap + wl + (gap + wp if price else 0) + (gap + wc if wc else 0) + h * 0.42))
    base = ui.glass_card(w, h, h / 2, look, rim=rim, glow=0.6)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    if color is None:
        dc = (c['up'] if change >= 0 else c['down']) if change is not None else c['accent']
    else:
        dc = _rgb(color if isinstance(color, str) else np.asarray(color), BLUE)
    x = p + h * 0.42 + dr
    a_, X0, Y0 = S.circle(x, p + h / 2, dr, dc * (1.3 if dark else 1.0))
    if dark:
        S.glow(a_, X0, Y0, dc, (4, 10), 0.8, knock=0.0)
    x += dr + gap
    yb = p + h / 2 + size * 0.36
    ui.put_text(f, x, yb, label, size, FONT_UI, c['text'], 'ls')
    x += wl + gap
    if price:
        ui.put_text(f, x, yb, price, ms, 'mono', c['text2'] if dark else c['text'], 'ls')
        x += wp + gap
    if change is not None:
        _arrow_text(f, x, yb, change, ms, c['up'] if change >= 0 else c['down'])
    return ui.derive_panel(base, f)


def order_toast(text='Order Filled — BUY 0.5 BTC @ 67,200', look='neon', w=760, rim=0.6):
    """Glass toast -> ui.Panel: UP check disc + title (before ' — ') + mono detail (after it), 'BUY' / 'SELL'
    coloured UP / DOWN. Verified copy: INTAKE.md section 3. Animate like ui.toast (slide + scale + opacity).
        OK.order_toast(look='cine').draw(cv, 540, 1240 + 40 * (1 - K.ramp(t, t0, t0 + 0.5)), opacity=K.ramp(...))"""
    return _order_toast(str(text), look, int(w), float(rim))


@functools.lru_cache(maxsize=12)
def _order_toast(text, look, w, rim):
    c = ink(look)
    dark = not _is_light(look)
    title, _, sub = text.partition(' — ')
    h = 136 if sub else 108
    base = ui.glass_card(w, h, 36, look, rim=rim, glow=0.7)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    cx, cy, r = p + 30 + 34, p + h / 2, 34
    a_, X0, Y0 = S.circle(cx, cy, r, c['up'])
    g = np.linspace(1.25, 0.8, a_.shape[0], dtype=np.float32)[:, None, None] * c['up']
    S.fill(a_, X0, Y0, g)
    if dark:
        S.glow(a_, X0, Y0, UP, (6, 16), 0.6)
    S.sheen(cx - r + 1, cy - r + 1, 2 * r - 2, 2 * r - 2, r, 0.14, 0.0, 0.55)
    S.paste(ui.icon('check', 40, INK if dark else IVORY, stroke=3.2), cx, cy, anchor=(0.5, 0.5))
    tx = p + 30 + 68 + 26
    if sub:
        ui.put_text(f, tx, p + h / 2 - 8, title, 36, FONT_UI, c['text'], 'ls')
        toks = sub.split(' ', 1)
        side = toks[0].upper()
        if side in ('BUY', 'SELL'):
            ws = ui.put_text(f, tx, p + h / 2 + 36, toks[0], 28, 'mono_bold', c['up'] if side == 'BUY' else c['down'],
                             'ls')
            ui.put_text(f, tx + ws + 12, p + h / 2 + 36, toks[1] if len(toks) > 1 else '', 28, 'mono', c['text2'], 'ls')
        else:
            ui.put_text(f, tx, p + h / 2 + 36, sub, 28, 'mono', c['text2'], 'ls')
    else:
        ui.put_text(f, tx, p + h / 2, title, 36, FONT_UI, c['text'], 'lm')
    return ui.derive_panel(base, f)


def trade_window(pair='BTC/USD', bid=67180.0, ask=67200.0, lot=0.5, look='neon', w=760, h=720, chart='line',
                 hover=0.0, press=0.0, which='buy', sub='Bitcoin / US Dollar', change=2.34, seed=4, rim=0.9):
    """Glass MT5-style order window -> ui.Panel: header (pair, sub, mono price + ▲▼ change), a chart (chart=
    'line' | 'candles' | None), volume stepper (lot), SELL (bid, DOWN) and BUY (ask, UP) buttons with INK labels
    (white on the light look's deep colours). hover / press 0..1 light up / push `which` button (quantised,
    cached). meta: 'buy' / 'sell' / 'chart' = (x, y, w, h) card-local; cursor target:
        win = OK.trade_window(look='cine', hover=hv, press=pr); win.plane(cv, cam, P, 760, rot=(6, -12, 0))
        bx, by, bw, bh = win.meta['buy']; xy = win.screen(cam, P, 760, (6, -12, 0), bx + bw / 2, by + bh / 2)"""
    key = ('tw', str(pair), float(bid), float(ask), float(lot), look, int(w), int(h), chart, _q(hover, 12),
           _q(press, 12), which, str(sub), float(change), int(seed), float(rim))
    return _LRU.get(key, lambda: _trade_window(*key[1:]))


@functools.lru_cache(maxsize=6)
def _trade_base(pair, bid, ask, lot, look, w, h, chart, sub, change, seed, rim):
    c = ink(look)
    dark = not _is_light(look)
    base = ui.glass_card(w, h, 44, look, rim=rim, glow=0.8)
    f = base.face.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    # header
    a_, X0, Y0 = S.circle(p + 56, p + 70, 24, BLUE)
    g = ui._lingrad(a_.shape[1], a_.shape[0], VIOLET, CYAN, -45)
    S.fill(a_, X0, Y0, g)
    S.sheen(p + 33, p + 47, 46, 46, 23, 0.16, 0.0, 0.6)
    ui.put_text(f, p + 96, p + 84, pair, 42, FONT_HEAD, c['text'], 'ls')
    ui.put_text(f, p + 97, p + 118, sub, 24, FONT_BODY, c['text2'], 'ls')
    ui.put_text(f, p + w - 36, p + 84, _fmt(ask), 40, 'mono_bold', c['text'], 'rs')
    _arrow_text(f, p + w - 36, p + 118, change, 24, c['up'] if change >= 0 else c['down'], anchor='r')
    _fillrect(f, p + 28, p + 146, p + w - 28, p + 147.2, c['text'], 0.10)
    # chart slot
    cx0, cy0, cw, ch = 28, 164, w - 56, h - 164 - 300
    if chart == 'line':
        spr = line_chart(cw, ch, None, 1.0, look, seed=seed, dot=True)
        ui.paste(f, spr, p + cx0 - PAD, p + cy0 - PAD)
    elif chart == 'candles':
        spr = candles(22, cw, ch, 1.0, 0.0, seed=seed, look=look, price=ask, axis=False, tick=0)
        ui.paste(f, spr, p + cx0 - PAD, p + cy0 - PAD)
    # volume stepper
    vy = h - 286
    ui.put_text(f, p + 36, p + vy + 46, 'Volume', 26, FONT_UI_MED, c['text2'], 'ls')
    sx, sw_ = w - 36 - 330, 330
    S.rrect(p + sx, p + vy, sw_, 72, 22, IVORY if dark else INK, 0.06 if dark else 0.05)
    S.stroke_rrect(p + sx, p + vy, sw_, 72, 22, 1.4, c['text'], 0.16)
    for k, sym in ((0, '-'), (1, '+')):
        bx = p + sx + (10 if k == 0 else sw_ - 62)
        S.rrect(bx, p + vy + 10, 52, 52, 16, c['text'], 0.08)
        _fillrect(f, bx + 16, p + vy + 35, bx + 36, p + vy + 37.4, c['text'], 0.9)
        if sym == '+':
            _fillrect(f, bx + 24.8, p + vy + 26, bx + 27.2, p + vy + 46, c['text'], 0.9)
    ui.put_text(f, p + sx + sw_ / 2 - 6, p + vy + 49, '{:.2f}'.format(lot), 34, 'mono_bold', c['text'], 'rs')
    ui.put_text(f, p + sx + sw_ / 2 + 4, p + vy + 49, 'lot', 24, FONT_BODY, c['text2'], 'ls')
    return base, _ro(f)


def _trade_window(pair, bid, ask, lot, look, w, h, chart, hover, press, which, sub, change, seed, rim):
    c = ink(look)
    dark = not _is_light(look)
    base, f0 = _trade_base(pair, bid, ask, lot, look, w, h, chart, sub, change, seed, rim)
    f = f0.copy()
    p = base.pad
    S = ui.Surf(f.shape[1], f.shape[0], f)
    by, bh = h - 172, 140
    gap = 20
    bw = (w - 56 - gap) / 2
    meta = {}
    for k, (side, price) in enumerate((('SELL', bid), ('BUY', ask))):
        bx = 28 + k * (bw + gap)
        meta[side.lower()] = (bx, by, bw, bh)
        col = (c['down'] if side == 'SELL' else c['up'])
        hv = hover if which == side.lower() else 0.0
        pr = press if which == side.lower() else 0.0
        ins = 4 * pr
        x, y, ww, hh = p + bx + ins, p + by + ins, bw - 2 * ins, bh - 2 * ins
        g0 = 1.12 + 0.18 * hv - 0.22 * pr
        a_, X0, Y0 = S.rrect_mask(x, y, ww, hh, 26)
        gy = np.linspace(g0, g0 - 0.30, a_.shape[0], dtype=np.float32)[:, None, None] * col
        S.fill(a_, X0, Y0, gy)
        S.sheen(x + 2, y + 2, ww - 4, hh - 4, 24, 0.16 + 0.08 * hv, 0.0, 0.5)
        if dark:
            S.glow(a_, X0, Y0, col, (8, 22), 0.35 + 0.9 * hv, knock=0.9)
        elif hv > 0:
            S.glow(a_, X0, Y0, col, (8, 22), 0.25 * hv, knock=0.9)
        tc = INK if dark else IVORY
        ui.put_text(f, x + ww / 2, y + hh / 2 - 10, side, 30, FONT_HEAD, tc, 'ms', tracking=0.06)
        ui.put_text(f, x + ww / 2, y + hh / 2 + 34, _fmt(price), 32, 'mono_bold', tc, 'ms')
    meta['chart'] = (28, 164, w - 56, h - 164 - 300)
    return ui.derive_panel(base, f, meta)


# ------------------------------------------------------------------------------------------------ cine effects
def blink_closure(u):
    """Eyelid closure 0..1 for blink progress u 0..1 (fast close, short hold, slower open)."""
    u = float(np.clip(u, 0, 1))
    if u < 0.40:
        x = u / 0.40
        return x * x * (3 - 2 * x)
    if u < 0.52:
        return 1.0
    x = (u - 0.52) / 0.48
    return 1.0 - (1 - (1 - x) ** 3)


def blink(cv, u, color=None, soft=1.0, rim=0.08, meet=0.55):
    """Eyelid blink overlay on the whole frame, in place: upper and lower lids with a soft curved (almond)
    edge close and reopen (u 0..1 = open -> closed at ~0.4-0.52 -> open), an occlusion shadow inside the edge
    and a faint cyan rim light on the lid edge. reel2 hook: tick the price while u is in the closed hold.
        OK.blink(cv, K.remap(t, 0.6, 1.3))           # after the scene, before K.post"""
    c = blink_closure(u)
    if c <= 1e-3:
        return cv
    H0, W0 = cv.shape[:2]
    gw, gh = W0 // 4, H0 // 4
    xs = (np.arange(gw, dtype=np.float32) + 0.5) * 4
    ys = (np.arange(gh, dtype=np.float32) + 0.5) * 4
    xn = (xs - W0 / 2) / (W0 * 0.5)
    prof = 1.0 - 0.10 * xn * xn                           # gentle lid arc: higher in the middle, no porthole
    m = H0 * meet
    gu = (1 - c) * (m + 140) / 0.82
    gl = (1 - c) * (H0 - m + 140) / 0.82
    yu = m - gu * prof + 36 * c * xn * xn                 # closing lids curve a touch more at the sides
    yl = m + gl * prof - 20 * c * xn * xn
    d = np.minimum(ys[:, None] - yu[None, :], yl[None, :] - ys[:, None])
    s = (8 + 22 * soft) * (0.6 + 0.4 * c)
    a = np.clip(d / (2 * s), 0, 1)
    a = a * a * (3 - 2 * a)
    shade = 0.35 + 0.65 * np.clip(d / 160.0, 0, 1) ** 0.8
    mult = (a * shade).astype(np.float32)
    lid = _rgb(color, _lin('NIGHT_0') * 0.5)
    rimm = np.exp(-((d + s * 0.3) / (s * 0.45)) ** 2) * rim * (1 - a)
    add = ((1 - a)[..., None] * lid + rimm[..., None] * (CYAN * 0.6)).astype(np.float32)
    need = (mult < 0.999).any(axis=1) | (add > 1e-5).any(axis=(1, 2))
    rows = np.nonzero(need)[0]
    if not len(rows):
        return cv
    # work on the lid bands only (rows the overlay touches); the open middle stays untouched
    mid = np.nonzero(~need)[0]
    spans = [(0, gh)] if not len(mid) else [(0, int(mid[0])), (int(mid[-1]) + 1, gh)]
    for r0, r1 in spans:
        if r1 <= r0:
            continue
        R0, R1 = r0 * 4, min(H0, r1 * 4)
        q0, q1 = max(0, r0 - 1), min(gh, r1 + 1)               # one row of margin for the bilinear resize
        mu = cv2.resize(mult[q0:q1], (W0, (q1 - q0) * 4), interpolation=cv2.INTER_LINEAR)
        ad = cv2.resize(add[q0:q1], (W0, (q1 - q0) * 4), interpolation=cv2.INTER_LINEAR)
        o = R0 - q0 * 4
        reg = cv[R0:R1]
        reg[..., :3] *= mu[o:o + (R1 - R0), :, None]
        reg[..., :3] += ad[o:o + (R1 - R0)]
    cv[..., 3] = 1.0
    return cv


@functools.lru_cache(maxsize=16)
def _streak_spr(length, thick, color, core):
    s = K.streak(int(length), int(thick), np.asarray(color, np.float32), np.asarray(core, np.float32))
    return _ro(s)


def streaks(cv, points, strength=1.0, color=None, length=560, thickness=7, wide=0.35):
    """Local anamorphic horizontal light streaks at screen points (emissive, mode 'add'), never full-frame.
    points: [(x, y)] or [(x, y, k)] with per-point gain k; length / thickness px of the core streak; wide adds
    a longer, softer blue twin. Use on highlights: the price head, button press, a glint on glass.
        OK.streaks(cv, [(820, 640, 1.0), (300, 1210, 0.5)], strength=K.impulse(t, 2.1, 5))"""
    if strength <= 1e-3:
        return
    col = _rgb(color, CYAN)
    sp = _streak_spr(int(length), int(thickness * 6), _ck(col * 1.4), _ck(IVORY * 1.2))
    sw = _streak_spr(int(length * 2.2), int(thickness * 14), _ck(BLUE * 0.6), _ck(BLUE * 0.25)) if wide > 0 else None
    for pt in points:
        x, y = float(pt[0]), float(pt[1])
        k = float(pt[2]) if len(pt) > 2 else 1.0
        if sw is not None:
            K.draw(cv, sw, x, y, opacity=strength * k * wide, mode='add')
        K.draw(cv, sp, x, y, opacity=strength * k, mode='add')


def light_rays(cv, origin, strength=0.6, t=0.0, color=None, length=1100, angle=90.0, cone=360.0, n=18, seed=0,
               softness=1.0):
    """Volumetric light rays (emissive, local: only within `length` px of origin): a fan of soft shafts whose
    pattern drifts with t, a hot core at the origin, radial falloff. angle (deg, screen, 90 = pointing down) +
    cone (deg; 360 = all round) aim them. Rendered at 1/4 res.
        OK.light_rays(cv, (760, 380), 0.5, t, angle=120, cone=110)"""
    if strength <= 1e-3:
        return
    H0, W0 = cv.shape[:2]
    ox, oy = float(origin[0]), float(origin[1])
    x0, y0 = max(0, int(ox - length)), max(0, int(oy - length))
    x1, y1 = min(W0, int(ox + length)), min(H0, int(oy + length))
    if x1 <= x0 or y1 <= y0:
        return
    gw, gh = max(2, (x1 - x0) // 4), max(2, (y1 - y0) // 4)
    xs = x0 + (np.arange(gw, dtype=np.float32) + 0.5) * (x1 - x0) / gw - ox
    ys = y0 + (np.arange(gh, dtype=np.float32) + 0.5) * (y1 - y0) / gh - oy
    X, Y = np.meshgrid(xs, ys)
    r = np.sqrt(X * X + Y * Y)
    th = np.arctan2(Y, X)
    rng = np.random.default_rng(seed)
    nb = 1024
    tb = np.linspace(-math.pi, math.pi, nb, endpoint=False)
    ray = np.zeros(nb, np.float64)
    for j in range(5):
        fr = int(n * (0.5 + j * 0.45))
        ph = rng.uniform(0, 2 * math.pi) + t * rng.uniform(-0.35, 0.35)
        ray += rng.uniform(0.5, 1.0) * np.cos(fr * tb + ph + 0.4 * np.sin(t * 0.3 + j))
    ray = np.clip(0.5 + 0.28 * ray, 0, 1) ** (2.2 / softness)
    idx = ((th + math.pi) / (2 * math.pi) * nb).astype(np.int32) % nb
    R = ray[idx].astype(np.float32)
    fall = np.clip(1 - r / length, 0, 1) ** 2.2 * (r / (r + 40.0))
    I = R * fall + np.exp(-(r / 70.0) ** 2) * 0.8
    if cone < 360:
        da = np.abs((np.degrees(th) - angle + 180) % 360 - 180)
        cm = np.clip(1 - da / (cone / 2), 0, 1)
        I *= cm * cm * (3 - 2 * cm)
    I = cv2.GaussianBlur(I.astype(np.float32), (0, 0), 1.2)
    col = _rgb(color, K.mix(CYAN, BLUE, 0.35))
    I = cv2.resize(I, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    cv[y0:y1, x0:x1, :3] += I[..., None] * (np.asarray(col, np.float32) * np.float32(strength))


# =============================================================================================== self-test
def _timed(fn, reps=3):
    fn()
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        ts.append((time.perf_counter() - t0) * 1e3)
    return round(float(np.median(ts)), 1)


def _label(cv, txt, y=70, look='neon'):
    ui.put_text(cv, 54, y, txt, 34, 'mono', ink(look)['text2'], 'ls')


def _st_widgets(out):
    rep = {}
    cam = K.Cam(aperture=18)

    def save(name, cv, look, t=0.5):
        K.post(cv, look, t)
        K.save_png(os.path.join(out, 'kit_%s.png' % name), cv)

    # dot sphere: assembled (neon), mid-assemble, light look, fine poster density
    cv = K.background('neon', 0.5, cam)
    rep['dot_sphere n2600'] = _timed(lambda: dot_sphere(cv.copy(), cam, (0, -420, 0), 300, 0.5))
    rep['dot_sphere n2600 assemble0.5'] = _timed(lambda: dot_sphere(cv.copy(), cam, (0, 420, 0), 300, 0.5,
                                                                    assemble=0.5))
    dot_sphere(cv, cam, (0, -440, 0), 300, 0.5)
    dot_sphere(cv, cam, (0, 430, 0), 300, 0.5, assemble=0.55)
    _label(cv, 'dot_sphere  assemble=1  %.0f ms' % rep['dot_sphere n2600'])
    _label(cv, 'assemble=0.55  %.0f ms' % rep['dot_sphere n2600 assemble0.5'], 1080)
    save('dot_sphere', cv, 'neon')
    cv = K.background('airy', 0.5, cam)
    dot_sphere(cv, cam, (0, -440, 0), 300, 0.5, look='airy')
    cv2_ = cv
    rep['dot_sphere n6000 dot0.22'] = _timed(lambda: dot_sphere(cv2_.copy(), cam, (0, 430, 0), 300, 0.5, n=6000,
                                                                dot=0.22, look='airy'))
    dot_sphere(cv, cam, (0, 430, 0), 300, 0.5, n=6000, dot=0.22, look='airy')
    _label(cv, "dot_sphere look='airy'", look='airy')
    _label(cv, 'n=6000 dot=0.22  %.0f ms' % rep['dot_sphere n6000 dot0.22'], 1080, 'airy')
    save('dot_sphere_airy', cv, 'airy')
    # candles: cine building, neon full, airy crash
    cv = K.background('cine', 0.5)
    for k, (look_, pr, cr) in enumerate((('cine', 0.75, 0.0), ('cine', 1.0, 1.0))):
        ui.glass_card(960, 600, 40, look_).draw(cv, 540, 520 + k * 820)
        rep['candles 28 %s crash%.0f' % (look_, cr)] = _timed(lambda: candles(28, 900, 540, pr, 1.2, look=look_,
                                                                              crash=cr))
        K.draw(cv, candles(28, 900, 540, pr, 1.2, look=look_, crash=cr), 540, 520 + k * 820)
    _label(cv, 'candles progress=0.75  %.0f ms' % rep['candles 28 cine crash0'], 160, 'cine')
    _label(cv, 'candles crash=1  %.0f ms' % rep['candles 28 cine crash1'], 980, 'cine')
    save('candles', cv, 'cine')
    cv = K.background('airy', 0.5)
    ui.glass_card(960, 600, 40, 'airy').draw(cv, 540, 520)
    K.draw(cv, candles(28, 900, 540, 1.0, 1.2, look='airy'), 540, 520)
    ui.glass_card(960, 600, 40, 'airy').draw(cv, 540, 1240)
    spr = candles(28, 900, 540, 1.0, 1.2, look='airy', crash=0.85, drop=300)
    K.draw(cv, spr, 540, 1240, anchor=(0.5, (PAD + 270) / spr.shape[0]))
    _label(cv, "candles look='airy'", 160, 'airy')
    _label(cv, 'crash=0.85 drop=300', 900, 'airy')
    save('candles_airy', cv, 'airy')
    # ticker tape
    for look_ in ('neon', 'airy'):
        cv = K.background(look_, 0.5, cam)
        rep['ticker_tape 2D %s' % look_] = _timed(lambda: ticker_tape(cv.copy(), 1.3, 700, look=look_))
        ticker_tape(cv, 1.3, 700, look=look_)
        pl = dict(cam=cam, center=(0, 300, 60), width=1500, rot=(8, -24, -7))
        rep['ticker_tape plane %s' % look_] = _timed(lambda: ticker_tape(cv.copy(), 1.3, 0, look=look_, plane=pl))
        ticker_tape(cv, 1.3, 0, look=look_, plane=pl)
        _label(cv, 'ticker_tape 2D  %.0f ms' % rep['ticker_tape 2D %s' % look_], 600, look_)
        _label(cv, 'plane  %.0f ms' % rep['ticker_tape plane %s' % look_], 1040, look_)
        save('ticker_tape_%s' % look_, cv, look_)
    # line chart + trade window + toast
    for look_ in ('cine', 'airy'):
        cv = K.background(look_, 0.5, cam)
        rep['line_chart %s' % look_] = _timed(lambda: _line_chart(900, 360, tuple(np.cumsum(np.ones(40))), 0.73,
                                                                  look_, None, 0.3, 1.0, 4.0, True, 8))
        K.draw(cv, line_chart(900, 360, None, 0.73, look_), 540, 330)
        rep['trade_window build %s (state change)' % look_] = _timed(
            lambda: _trade_window('BTC/USD', 67180.0, 67200.0, 0.5, look_, 760, 720, 'line', 0.5, 0.0, 'buy',
                                  'Bitcoin / US Dollar', 2.34, 4, 0.9))
        rep['trade_window build %s (first, base)' % look_] = _timed(
            lambda: _trade_base.__wrapped__('BTC/USD', 67180.0, 67200.0, 0.5, look_, 760, 720, 'line',
                                            'Bitcoin / US Dollar', 2.34, 4, 0.9), 1)
        win = trade_window(look=look_, hover=1.0, press=0.5)
        rep['trade_window.draw %s' % look_] = _timed(lambda: win.draw(cv.copy(), 540, 1010))
        win.draw(cv, 540, 1010)
        bx, by, bw, bh = win.meta['buy']
        xy = win.screen2d(540, 1010, bx + bw * 0.62, by + bh * 0.6)
        ui.draw_cursor(cv, xy[0], xy[1], 'hand', 84, press=0.5, look=look_)
        toast = order_toast(look=look_)
        rep['order_toast.draw %s' % look_] = _timed(lambda: toast.draw(cv.copy(), 540, 1560))
        toast.draw(cv, 540, 1560)
        if look_ == 'cine':
            streaks(cv, [(912, 330, 1.0)], 0.9)
        _label(cv, 'line_chart progress=0.73  %.0f ms' % rep['line_chart %s' % look_], 120, look_)
        _label(cv, 'trade_window + order_toast', 1800, look_)
        save('trade_%s' % look_, cv, look_)
    # asset tags on an orbit ring round the sphere
    for look_ in ('neon', 'airy'):
        cam2 = K.Cam.orbit((0, 0, 0), 1500, yaw=8, pitch=6, aperture=18)
        cv = K.background(look_, 0.5, cam2)
        rep['asset_tag build %s' % look_] = _timed(lambda: _asset_tag.cache_clear() or
                                                   asset_tag('BTC/USD', '67,420', 2.34, look=look_), 2)
        tags = [asset_tag(a, b, c, look=look_, size=26, h=64) for a, b, c in TICKERS[:6]]
        rep['orbit_ring 6 tags + sphere %s' % look_] = _timed(lambda: ui.orbit_ring(
            cv.copy(), cam2, tags, phase=0.08, radius=(440, 440), look=look_, back_scale=0.9,
            mid=lambda c: dot_sphere(c, cam2, (0, 0, 0), 300, 0.5, look=look_)))
        ui.orbit_ring(cv, cam2, tags, phase=0.08, radius=(440, 440), look=look_, back_scale=0.9,
                      mid=lambda c: dot_sphere(c, cam2, (0, 0, 0), 300, 0.5, look=look_))
        asset_tag('XAU/USD', '2,338.40', -0.44, look=look_).draw(cv, 540, 1500)
        _label(cv, 'asset_tag x6 on ui.orbit_ring + dot_sphere  %.0f ms' % rep['orbit_ring 6 tags + sphere %s' % look_],
               120, look_)
        save('asset_tag_%s' % look_, cv, look_)
    # blink + streaks + rays (cine)
    cv0 = K.background('cine', 0.5, cam)
    ui.glass_card(960, 600, 40, 'cine').draw(cv0, 540, 960)
    K.draw(cv0, candles(28, 900, 540, 1.0, 1.0, look='cine'), 540, 960)
    rep['light_rays'] = _timed(lambda: light_rays(cv0.copy(), (860, 300), 0.5, 1.0, angle=120, cone=120))
    rep['streaks x3'] = _timed(lambda: streaks(cv0.copy(), [(800, 760), (300, 1100, 0.6), (700, 1300, 0.4)], 1.0))
    rep['blink'] = _timed(lambda: blink(cv0.copy(), 0.3))
    frames = []
    for u in (0.0, 0.22, 0.34, 0.75):
        cv = cv0.copy()
        light_rays(cv, (860, 300), 0.5, 1.0, angle=120, cone=120)
        streaks(cv, [(800, 760), (300, 1100, 0.6), (700, 1300, 0.4)], 1.0)
        blink(cv, u)
        K.post(cv, 'cine', 0.5)
        _label(cv, 'blink u=%.2f' % u, 1860, 'cine')
        frames.append(cv2.resize(K.to_srgb8(cv, 0.5), (540, 960), interpolation=cv2.INTER_AREA))
    K.save_png(os.path.join(out, 'kit_blink_streaks_rays.png'), np.hstack(frames))
    return rep


def _st_looks(out):
    rep = {}
    for look_ in ('neon', 'cine', 'airy', 'amber'):
        cam = K.Cam.orbit((0, 0, 0), 1500, yaw=6, pitch=4, aperture=18)
        t = 1.2

        def frame():
            cv = K.background(look_, t, cam)
            if look_ == 'cine':
                light_rays(cv, (900, 260), 0.45, t, angle=125, cone=100)
            dot_sphere(cv, cam, (0, -380, 120), 280, t, look=look_)
            ui.glass_card(960, 560, 40, look_).draw(cv, 540, 1060)
            K.draw(cv, candles(26, 900, 500, 1.0, t, look=look_), 540, 1060)
            ticker_tape(cv, t, 1440, look=look_)
            asset_tag('BTC/USD', '67,420', 2.34, look=look_).draw(cv, 330, 1620)
            asset_tag('XAU/USD', '2,338.40', -0.44, look=look_).draw(cv, 760, 1700)
            if look_ == 'cine':
                streaks(cv, [(870, 980, 0.8)], 0.8)
            K.post(cv, look_, t)
            return cv
        rep['look frame %s' % look_] = _timed(frame, 1)
        cv = frame()
        ui.put_text(cv, 54, 90, "look '%s'" % look_, 40, 'mono', ink(look_)['text2'], 'ls')
        K.save_png(os.path.join(out, 'kit_look_%s.png' % look_), cv)
    return rep


def selftest(names=None):
    """Write <WS>/out/kit/kit_*.png (one still per look and per widget) + kit_report.json (ms per call)."""
    out = os.path.join(K.WS, 'out', 'kit')
    os.makedirs(out, exist_ok=True)
    rep = {}
    if not names or 'widgets' in names:
        rep.update(_st_widgets(out))
    if not names or 'looks' in names:
        rep.update(_st_looks(out))
    old = {}
    pj = os.path.join(out, 'kit_report.json')
    if os.path.exists(pj):
        try:
            old = json.load(open(pj))
        except ValueError:
            old = {}
    old.update(rep)
    json.dump(old, open(pj, 'w'), indent=1)
    for k, v in rep.items():
        print('%-44s %8.1f ms' % (k, v))
    return rep


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest(sys.argv[2:])
