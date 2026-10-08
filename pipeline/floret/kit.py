"""kit.py: the Organic Fostering motion toolkit (pipeline/fostering) installed for Floret Capitals.

Importing this module gives a Floret profile of the whole toolkit WITHOUT editing a line of it:
    canvas      1248 x 1248 @ 60 fps by default (env FLORET_W / FLORET_H / FLORET_FPS, or kit.canvas(w, h, fps)
                - e.g. kit.canvas(1080, 1920, 30) for 9:16 Reels); every toolkit default sized for 1080x1920 follows.
    palette     GOLD #E49F38, GOLD_HI, GOLD_LO, CHAMPAGNE, BRONZE, ONYX_0/1, SILVER, ELECTRIC, PSX_GREEN, PMEX_RED,
                PEARL ... added to core.C. The Organic Fostering brand tokens the widgets use (MAGENTA, ORANGE,
                HOT_PINK, AMBER, LEAF, PLUM, INK, NIGHT_0/1 ...) are re-pointed at gold equivalents (BRAND_REMAP);
                the originals stay as OF_MAGENTA, OF_ORANGE, ... (this process only - Organic Fostering renders
                are untouched).
    fonts       General Sans everywhere (downloaded from Fontshare automatically if workspace/fonts lacks it) (aliases 'display' 700, 'display2'/'head' 600, 'ui' 500, 'body' 400,
                'light' 300, 'thin' 200); Nunito / Poppins / Caveat still resolve by full name.
    looks       'gold' (onyx void, gold aurora, electric-blue accent) and 'pearl' (ivory/champagne daylight) for
                core.background / core.post / ui widgets / footage grades.
    type styles extrude3d_gold, chrome_gold, gradient_gold, deep_glow_gold, neon_gold, glass_pill_gold
                (+ every Organic Fostering preset: flat ui ui_ink extrude3d chrome gold deep_glow neon gradient ...).
    outputs     workspace4/kit_out/<module>/ (renders, sheets, selftest), workspace4/audio/ (SFX mixes).
    currency    Pakistani rupee: icons 'rupee' and 'coin_rs' ('pound' / 'coin' draw them too in Floret processes),
                ui.money() and T.Counter default to 'Rs '; kit.money(12500) -> 'Rs 12,500'.
    3D objects  kit.obj('logo' | 'goldbar' | 'silverbar' | 'barrel' | 'coin' | 'shield') -> the Floret Blender
                sequences (workspace4/b3d2) as linear premultiplied sprites; the toolkit's own assets
                (S3.get('shield_check', 'night'), orbs, check_tile, star_badge, ...) still load from workspace3.

Use it exactly like pipeline/fostering/TOOLKIT.md describes (same module contract, same APIs), with
`import kit` as the first import of a Floret module:

    import kit                                   # applies the Floret profile (idempotent)
    from kit import K, T, ui, F, S3, SFX         # core, type3d, ui, footage, sprites3d, audio
    DUR, LOOK, BPM = 12.0, 'gold', 120
    def draw(t): cv = K.background(LOOK, t, K.Cam()); ...; return cv

    python3 kit.py sheet <module> [N]                    # contact sheet in the canvas aspect
    python3 kit.py render <module> [render.py options]   # --stills a,b / --preview / --range a b / full master + SFX
    python3 kit.py selftest                              # Floret-branded showcase -> workspace4/kit_out/selftest/
"""
import functools
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
FOSTER = os.path.join(REPO, 'pipeline', 'fostering')
WS4 = os.path.join(REPO, 'workspace4')
for p in (FOSTER, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import core as K  # noqa: E402
import footage as F  # noqa: E402
import type3d as T  # noqa: E402
import ui  # noqa: E402
import sprites3d as S3  # noqa: E402
import audio as SFX  # noqa: E402

# ============================================================================================ palette
FLORET_HEX = {
    'GOLD': '#E49F38', 'GOLD_HI': '#F7D08A', 'GOLD_LO': '#B06A1C', 'CHAMPAGNE': '#FFF1D6', 'BRONZE': '#6B4310',
    'AMBER_DEEP': '#FF7A1A', 'ONYX_0': '#050506', 'ONYX_1': '#100D09', 'ONYX_INK': '#15120E', 'SILVER': '#DFE3EA',
    'ELECTRIC': '#2F63FF', 'ICE': '#A9C8FF', 'VIOLET': '#7B4DFF', 'PSX_GREEN': '#19B36E', 'PMEX_RED': '#E8262F',
    'PEARL': '#FBF8F2', 'SAND': '#F3E7D2', 'MUTED': '#8E8B86',
}

# The toolkit's widgets name the Organic Fostering brand tokens directly (MAGENTA -> ORANGE buttons, HOT_PINK
# highlights, LEAF checks, PLUM shadows ...). In a Floret process those tokens are re-pointed at the Floret
# palette, so every widget, style and look comes out gold; the originals stay available as OF_<NAME>.
BRAND_REMAP = {
    'MAGENTA': '#B87318', 'LOGO_MAGENTA': '#B87318', 'ORANGE': '#E49F38', 'LOGO_ORANGE': '#E49F38',
    'HOT_PINK': '#F7D08A', 'AMBER': '#FFE2AE', 'PLUM': '#3A2608', 'INK': '#15120E', 'NIGHT_0': '#050506',
    'NIGHT_1': '#100D09', 'PEACH': '#F3E7D2', 'LAVENDER': '#F6F1E8', 'LEAF': '#19B36E', 'LEAF_HI': '#5FE3A1',
}

# General Sans weights (files GeneralSans-<weight>.ttf)
GS = {w: 'GeneralSans-%d' % w for w in (200, 300, 400, 500, 600, 700)}
FONT_MAP = {'Nunito-Black': GS[700], 'Nunito-ExtraBold': GS[600], 'Nunito-Bold': GS[600], 'Nunito-SemiBold': GS[500],
            'Poppins-Bold': GS[600], 'Poppins-SemiBold': GS[500], 'Poppins-Medium': GS[500],
            'Poppins-Regular': GS[400]}

# Pakistani rupee ("Rs") on the toolkit's 24-unit icon grid: R (stem, bowl, leg) + a small s.
RUPEE = ['M4.3 19V5h4.5a3.5 3.5 0 0 1 0 7H4.3', 'M8.3 12l3.6 7',
         'M20.2 13.4c-.5-.9-1.4-1.4-2.5-1.4-1.4 0-2.4.8-2.4 1.9 0 2.6 5.1 1.4 5.1 4 0 1.2-1.1 2.1-2.7 2.1'
         '-1.1 0-2.1-.5-2.6-1.3']
CURRENCY = 'Rs '

_STATE = {'applied': False, 'canvas': (K.W, K.H, K.FPS)}


# ============================================================================================ canvas
def _functions(mod):
    """Every plain function / method defined in a toolkit module (module level + classes)."""
    for v in list(vars(mod).values()):
        if inspect.isfunction(v) and v.__module__ == mod.__name__:
            yield v
        elif inspect.isclass(v) and v.__module__ == mod.__name__:
            for a in vars(v).values():
                f = a.__func__ if isinstance(a, (staticmethod, classmethod)) else a
                if inspect.isfunction(f):
                    yield f


def _retarget(fn, table):
    """Replace defaults (by parameter name) whose value equals table[name][0] with table[name][1]."""
    code = fn.__code__
    names = code.co_varnames[:code.co_argcount]
    if fn.__defaults__:
        d = list(fn.__defaults__)
        off = len(names) - len(d)
        for i, v in enumerate(d):
            rule = table.get(names[off + i])
            if rule and _same(v, rule[0]):
                d[i] = rule[1]
        fn.__defaults__ = tuple(d)
    if fn.__kwdefaults__:
        for k, v in list(fn.__kwdefaults__.items()):
            rule = table.get(k)
            if rule and _same(v, rule[0]):
                fn.__kwdefaults__[k] = rule[1]


def _same(a, b):
    try:
        return type(a) in (int, float, tuple, str) and a == b
    except Exception:
        return False


def _render_mod():
    import render as R
    return R


def canvas(w=None, h=None, fps=None):
    """Set the toolkit canvas (default 1248 x 1248 @ 60). Child render workers inherit it through the env."""
    w = int(w or os.environ.get('FLORET_W', 1248))
    h = int(h or os.environ.get('FLORET_H', 1248))
    fps = int(fps or os.environ.get('FLORET_FPS', 60))
    w0, h0, f0 = _STATE['canvas']
    os.environ['FLORET_W'], os.environ['FLORET_H'], os.environ['FLORET_FPS'] = str(w), str(h), str(fps)
    if (w, h, fps) == (w0, h0, f0):
        return w, h, fps
    table = {'w': (w0, w), 'h': (h0, h), 'fps': (f0, fps), 'size': ((w0, h0), (w, h)), 'shape': ((h0, w0), (h, w)),
             'target': ((w0 / 2.0, h0 / 2.0), (w / 2.0, h / 2.0))}
    for mod in (K, F, T, ui, S3, _render_mod()):
        for fn in _functions(mod):
            _retarget(fn, table)
    K.W, K.H, K.FPS, K.CX, K.CY = w, h, fps, w / 2.0, h / 2.0
    ui.W, ui.H = w, h
    _STATE['canvas'] = (w, h, fps)
    return w, h, fps


# ============================================================================================ fonts
def _font_farm():
    """workspace4/fonts: symlinks to the toolkit fonts (workspace3) + General Sans (workspace/fonts)."""
    dst = os.path.join(WS4, 'fonts')
    os.makedirs(dst, exist_ok=True)
    for src in (os.path.join(REPO, 'workspace3', 'fonts'), os.path.join(REPO, 'workspace', 'fonts')):
        if not os.path.isdir(src):
            continue
        for fn in os.listdir(src):
            if fn.lower().endswith(('.ttf', '.otf')):
                p = os.path.join(dst, fn)
                if not os.path.lexists(p):
                    try:
                        os.symlink(os.path.join(src, fn), p)
                    except OSError:
                        pass
    missing = [f for f in GS.values() if not os.path.exists(os.path.join(dst, f + '.ttf'))]
    if missing and _fetch_general_sans():
        return _font_farm()
    if missing:
        print('kit: General Sans weights missing in %s: %s (download: api.fontshare.com/v2/fonts/download/'
              'general-sans)' % (dst, ', '.join(missing)), file=sys.stderr)
    return dst


GS_URL = 'https://api.fontshare.com/v2/fonts/download/general-sans'
GS_FILES = {'Extralight': 200, 'Light': 300, 'Regular': 400, 'Medium': 500, 'Semibold': 600, 'Bold': 700}


def _fetch_general_sans():
    """Download General Sans (Fontshare, free licence) into workspace/fonts as GeneralSans-<weight>.ttf.
    Only the six static TTFs are read from the zip; nothing in it is executed. Returns True on success."""
    import io
    import urllib.request
    import zipfile
    dst = os.path.join(REPO, 'workspace', 'fonts')
    if _STATE.get('gs_fetch_tried'):
        return False
    _STATE['gs_fetch_tried'] = True
    try:
        data = urllib.request.urlopen(GS_URL, timeout=60).read()
        zf = zipfile.ZipFile(io.BytesIO(data))
        os.makedirs(dst, exist_ok=True)
        got = 0
        for info in zf.infolist():
            base = os.path.basename(info.filename)
            stem = base[len('GeneralSans-'):-len('.ttf')] if base.startswith('GeneralSans-') and \
                base.endswith('.ttf') else None
            if '/WEB/fonts/' in info.filename and stem in GS_FILES:
                with open(os.path.join(dst, 'GeneralSans-%d.ttf' % GS_FILES[stem]), 'wb') as f:
                    f.write(zf.read(info))
                got += 1
        return got == len(GS_FILES)
    except Exception as e:  # offline / blocked: keep going with whatever fonts exist
        print('kit: General Sans download failed (%s)' % e, file=sys.stderr)
        return False


def _fonts():
    K.FONTS = _font_farm()
    T.FONT_ALIAS.update({'display': GS[700], 'display2': GS[600], 'display_bold': GS[600], 'ui': GS[500],
                         'ui_bold': GS[600], 'body': GS[400], 'medium': GS[500], 'light': GS[300], 'thin': GS[200],
                         'semibold': GS[600], 'bold': GS[700]})
    ui.FONT_ALIAS.update({'ui': GS[500], 'ui_bold': GS[600], 'ui_medium': GS[500], 'body': GS[400],
                          'head': GS[600], 'head_black': GS[700], 'head_bold': GS[600], 'light': GS[300],
                          'thin': GS[200]})
    table = {'font': None}
    for mod in (T, ui):
        for fn in _functions(mod):
            for old, new in FONT_MAP.items():
                table['font'] = (old, new)
                _retarget(fn, table)
    for name, st in list(T.STYLES.items()):
        if st.font in FONT_MAP:
            T.STYLES[name] = st.but(font=FONT_MAP[st.font])


# ============================================================================================ looks
def _looks():
    for k, v in FLORET_HEX.items():
        K.PALETTE_HEX.setdefault(k, v)
        K.C.setdefault(k, K.hexlin(v))
    for k, v in BRAND_REMAP.items():
        if 'OF_' + k not in K.C:
            K.PALETTE_HEX['OF_' + k], K.C['OF_' + k] = K.PALETTE_HEX[k], K.C[k]
        K.PALETTE_HEX[k], K.C[k] = v, K.hexlin(v)
    K._BG_LOOKS['gold'] = dict(
        top='ONYX_0', bottom='ONYX_1', lift=0.3, base_tint=(1.25, 0.95, 0.6),
        blobs=[
            (0.50, 0.28, 0.50, 0.28, 18, 'GOLD', 0.34, 0.06, 0.04, 25.0, 1.0),
            (0.53, 0.31, 0.16, 0.10, 18, 'GOLD_HI', 0.15, 0.05, 0.035, 18.0, 0.5),
            (0.96, 0.74, 0.44, 0.38, -30, 'ELECTRIC', 0.16, 0.05, 0.05, 27.0, 0.5),
            (0.02, 0.12, 0.30, 0.22, -12, 'AMBER_DEEP', 0.16, 0.04, 0.03, 21.0, 0.3),
            (0.06, 0.92, 0.40, 0.30, 15, 'BRONZE', 0.30, 0.05, 0.04, 33.0, 0.0),
        ],
        rim=('GOLD_HI', 'GOLD', 0.9), rim_geom=(0.62, 1.55, 0.68), dots=0.012, dots_lit=0.7, noise=0.5)
    K._BG_LOOKS['pearl'] = dict(
        top='PEARL', bottom='PEARL', lift=0.0,
        blobs=[
            (0.86, 0.12, 0.72, 0.50, -30, 'SAND', 1.0, 0.05, 0.04, 26.0),
            (0.80, 0.16, 0.38, 0.26, -30, 'GOLD_HI', 0.30, 0.04, 0.03, 19.0),
            (0.08, 0.38, 0.62, 0.50, 25, 'CHAMPAGNE', 1.0, 0.05, 0.05, 22.0),
            (0.12, 0.42, 0.40, 0.30, 25, 'ICE', 0.22, 0.05, 0.05, 30.0),
            (0.88, 0.84, 0.66, 0.46, -20, 'SAND', 1.0, 0.05, 0.04, 24.0),
            (0.92, 0.88, 0.36, 0.25, -20, 'GOLD', 0.22, 0.04, 0.04, 21.0),
            (0.35, 0.99, 0.80, 0.34, 10, 'CHAMPAGNE', 0.8, 0.04, 0.03, 34.0),
        ],
        rim=None, dots=0.0, dots_lit=0.0, noise=0.12, paper=0.014)
    K.LOOKS['gold'] = dict(K.LOOKS['amber'], bloom_tint=(1.0, 0.80, 0.52), halation=0.10,
                           black_tint=(0.0012, 0.0009, 0.0004))
    K.LOOKS['pearl'] = dict(K.LOOKS['airy'], bloom_tint=(1.0, 0.92, 0.80))
    if 'amber' in F.GRADES:
        F.GRADES.setdefault('gold', F.GRADES['amber'])
    if 'airy' in F.GRADES:
        F.GRADES.setdefault('pearl', F.GRADES['airy'])

    C, v, mix = K.C, ui._v, K.mix
    am, ai = dict(ui.LOOKS['amber'].__dict__), dict(ui.LOOKS['airy'].__dict__)
    am.pop('name', None)
    ai.pop('name', None)
    am.update(
        tint_top=v(mix(K.hexlin('#1C150C'), C['ONYX_1'], 0.3)), tint_bot=v(C['ONYX_0']),
        text2=v(mix(C['IVORY'], C['CHAMPAGNE'], 0.5), 0.52), text3=v(C['CHAMPAGNE'], 0.30),
        accent=v(C['GOLD']), accent_hi=v(C['GOLD_HI']), grad=(v(C['GOLD_LO']), v(C['GOLD_HI'])),
        grad_hi=(v(C['GOLD_HI']), v(C['CHAMPAGNE'])), rim=v(C['GOLD_HI']), rim2=v(C['GOLD']), glow=v(C['GOLD']),
        ok=v(C['PSX_GREEN']), ok_hi=v(K.hexlin('#5FE3A1')))
    ai.update(
        tint_top=v(C['WHITE']), tint_bot=v(mix(C['PEARL'], C['SAND'], 0.6)),
        text=v(C['ONYX_INK']), text2=v(mix(C['ONYX_INK'], C['SAND'], 0.45)),
        text3=v(mix(C['ONYX_INK'], C['SAND'], 0.7)), accent=v(C['GOLD']), accent_hi=v(C['GOLD_HI']),
        grad=(v(C['GOLD_LO']), v(C['GOLD'])), grad_hi=(v(C['GOLD']), v(C['GOLD_HI'])), rim=v(C['CHAMPAGNE']),
        rim2=v(C['GOLD_HI']), glow=v(C['CHAMPAGNE']), shadow=v(mix(C['BRONZE'], C['ONYX_INK'], 0.4)),
        line=v(C['ONYX_INK']), ok=v(C['PSX_GREEN']), ok_hi=v(K.hexlin('#5FE3A1')), chip_text=v(C['ONYX_INK'], 0.85))
    ui.LOOKS['gold'] = ui.Look('gold', **am)
    ui.LOOKS['pearl'] = ui.Look('pearl', **ai)

    S = T.STYLES
    S['extrude3d_gold'] = S['extrude3d'].but(rim_color=('GOLD_HI', 1.4), inner_shadow_color='BRONZE',
                                             glow_color=('GOLD', 1.3), side=(('#5A3A10', 1.0), ('#0E0A04', 1.0)))
    S['chrome_gold'] = S['chrome'].but(rim_color=('GOLD_HI', 1.6), env_ground='#E49F38', glow_color=('GOLD', 1.4),
                                       side=(('#6B4A12', 1.0), ('#120C04', 1.0)))
    S['gradient_gold'] = S['gradient'].but(fill=('GOLD_LO', 'GOLD', 'GOLD_HI'), inner_glow_color=('CHAMPAGNE', 1.0),
                                           glow_color=('GOLD', 1.4))
    S['deep_glow_gold'] = S['deep_glow'].but(fill=((0.0, '#FFFFFF'), (1.0, '#FFF4E0')),
                                             inner_glow_color=('GOLD_HI', 1.3), glow_color=('GOLD', 2.6))
    S['neon_gold'] = S['neon'].but(tube_color=('GOLD_HI', 1.5), glow_color=('GOLD', 2.4))
    S['glass_pill_gold'] = S['glass_pill'].but(pill_tint=('GOLD', 1.3))


_BG = K.background


def _background(look='neon', *a, **kw):
    """core.background with the light 'pearl' look (core only treats 'airy' as a light paper look)."""
    if look != 'pearl':
        return _BG(look, *a, **kw)
    keep = K._BG_LOOKS['airy']
    K._BG_LOOKS['airy'] = K._BG_LOOKS['pearl']
    try:
        return _BG('airy', *a, **kw)
    finally:
        K._BG_LOOKS['airy'] = keep


# ============================================================================================ currency
def _currency():
    """Rupee icons ('rupee', 'coin_rs'; 'pound' / 'coin' re-pointed at them, originals as 'of_pound' / 'of_coin')
    and 'Rs ' as the default symbol of ui.money() and the prefix of type3d.Counter."""
    D = ui.ICON_DEFS
    if 'of_pound' not in D:
        D['of_pound'], D['of_coin'] = D['pound'], D['coin']
    D['rupee'] = list(RUPEE)
    D['coin_rs'] = [('circle', 12, 12, 9.8)] + [('s', d, (0.5, 12.2, 12.2)) for d in RUPEE]
    D['pound'], D['coin'] = D['rupee'], D['coin_rs']
    ui.ICONS = tuple(D)
    for fn in (ui.money, T.Counter.__init__):
        _retarget(fn, {'symbol': ('\u00a3', CURRENCY), 'prefix': ('\u00a3', CURRENCY)})


def money(v, decimals=0, symbol=CURRENCY):
    """money(12500) -> 'Rs 12,500'."""
    return ui.money(v, decimals, symbol)


# ============================================================================================ paths
def _paths():
    out = os.path.join(WS4, 'kit_out')
    K.OUT, K.SELFTEST, K.AUDIO = out, os.path.join(out, 'selftest'), os.path.join(WS4, 'audio')
    for name, val in (('OUT', out), ('SELFTEST', K.SELFTEST), ('AUDIO', K.AUDIO)):
        if hasattr(SFX, name):
            setattr(SFX, name, val)


# ============================================================================================ Floret 3D
B3D_DIRS = (os.path.join(WS4, 'b3d2'), os.path.join(WS4, 'b3d'))
B3D_FRAMES = dict(logo=120, goldbar=96, silverbar=96, barrel=96, coin=96, shield=96)


@functools.lru_cache(maxsize=256)
def _b3d_frame(job, f, scale):
    for d in B3D_DIRS:
        p = os.path.join(d, job, '%04d.png' % f)
        if os.path.exists(p):
            im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0
            if scale != 1.0:
                im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            a = im[..., 3:4]
            spr = np.concatenate([K.to_lin(im[..., 2::-1]) * a, a], axis=2).astype(np.float32)
            spr.setflags(write=False)
            return spr
    return None


def obj(job, t=None, frame=None, fps=30.0, loop='pingpong', scale=0.5):
    """A Floret Blender object as a linear premultiplied sprite (read-only): by `frame` (1-based) or time `t`
    (s; loop 'pingpong' | 'wrap' | 'hold'). None when the sequence has not been rendered."""
    n = B3D_FRAMES[job]
    if frame is None:
        x = (t or 0.0) * fps
        if loop == 'pingpong':
            x = abs((x % (2 * (n - 1))) - (n - 1)) if n > 1 else 0
        elif loop == 'wrap':
            x = x % n
        frame = int(min(max(x, 0), n - 1)) + 1
    return _b3d_frame(job, int(frame), float(scale))


# ============================================================================================ apply
def apply():
    """Install the Floret profile into the toolkit modules (idempotent)."""
    if _STATE['applied']:
        return
    _fonts()
    _looks()
    _currency()
    _paths()
    K.background = _background
    canvas()
    _STATE['applied'] = True


apply()


# ============================================================================================ selftest
def _st_hero(t=2.0):
    cam = K.Cam.orbit((0, 0, 0), 1500, yaw=4, pitch=3, aperture=20)
    cv = K.background('gold', t, cam)
    ring = T.OrbitText('PSX  •  PMEX  •  GOLD  •  EQUITIES  •  COMMODITIES  •  ', 'flat',
                       px=34, fill='GOLD_HI', radius=360, tilt=22, roll=-8)
    ring.draw(cv, cam, (0, -60, 0), t=t, part='back')
    lg = obj('logo', frame=120, scale=0.55)
    if lg is not None:
        xy, _ = cam.project(np.array([[0.0, -60.0, 0.0]]))
        K.draw(cv, K.glow(lg, K.C['GOLD'], (10, 40, 110), 0.7), xy[0][0], xy[0][1], mode='add')
        K.draw(cv, lg, xy[0][0], xy[0][1])
    ring.draw(cv, cam, (0, -60, 0), t=t, part='front')
    T.render('FLORET CAPITALS', 'extrude3d_gold', px=96, tracking=0.08).draw(cv, K.CX, K.H * 0.80, sweep=0.55)
    T.render('floretcapitals.com', 'glass_pill_gold', px=30).draw(cv, K.CX, K.H * 0.90)
    K.Particles(120, seed=3, bright=0.8, colors=[K.C['GOLD_HI'], K.C['GOLD'], K.C['CHAMPAGNE']]).draw(cv, cam, t)
    return K.post(cv, 'gold', t)


def _st_dashboard(t=3.0):
    lk = 'gold'
    cam = K.Cam(aperture=14)
    cv = K.background(lk, t, cam)
    win = ui.app_window(w=980, h=860, look=lk, title='floretcapitals.com', header='Markets', sub='PSX · PMEX',
                        icons=('home', 'chart', 'rupee', 'globe', 'settings'), active=1)
    x, y, sw, sh = win.meta['slot']
    face = win.face_at(sweep=0.35)
    cx = x
    for i, lab in enumerate(['PSX', 'PMEX', 'Gold', 'Crude Oil']):
        c = ui.chip(lab, 1.0 if i == 0 else 0.0, look=lk)
        win.put(face, c, cx - 24, y - 24)
        cx += c.shape[1] - 48 + 12
    bars = ui.bar_chart([42, 55, 48, 66, 73, 81], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], grow=1.0, active=5,
                        w=sw, h=400, look=lk, fmt=lambda v: '')
    win.put(face, bars, x - 32, y + 100 - 32)
    win.plane(cv, cam, (0, -40, 60), 900, rot=(8, 12, -1.2), face=face)
    ui.toast('Order filled', 'PSX · market order', look=lk, w=520).draw(cv, K.W * 0.70, K.H * 0.82)
    xy = win.screen(cam, (0, -40, 60), 900, (8, 12, -1.2), x + 60, y + 30, z=-40)
    ui.draw_cursor(cv, xy[0], xy[1], 'hand', 80, press=0.6, click=0.15, look=lk)
    return K.post(cv, lk, t)


def _st_components(lk):
    cv = K.background(lk, 2.0)
    L = ui.LOOKS[lk]
    s = K.W / 1080.0
    for i, (hv, pr, rp) in enumerate([(0, 0, None), (1, 0, None), (1, 1, 0.08), (0.6, 0.3, 0.32)]):
        ui.place(cv, ui.button('Explore markets', hover=hv, press=pr, ripple=rp, ripple_at=(0.75, 0.5), look=lk,
                               h=96, size=34), (290 + (i % 2) * 520) * s, 100 + (i // 2) * 140)
    for i, tt in enumerate([-1, 0.06, 0.12, 0.24, 0.5, 1.0]):
        ui.place(cv, ui.checkbox(tt, 56, lk), (90 + i * 128) * s, 400)
    for i, p in enumerate([0, 0.5, 1.0]):
        ui.place(cv, ui.toggle(p, look=lk), (120 + i * 170) * s, 520)
    ui.place(cv, ui.progress_ring(0.72, 200, 18, lk), 900 * s, 470)
    xx = 60 * s
    for i, (tx, sl) in enumerate([('Equities', 1), ('Commodities', 0), ('Metals', 0.5), ('Energy', 0)]):
        c = ui.chip(tx, sl, look=lk)
        ui.place(cv, c, xx, 660, anchor=(0, 0.5))
        xx += c.shape[1] - 32
    ui.place(cv, ui.slider(0.62, int(640 * s), lk, label='Risk level'), 420 * s, 800)
    ui.place(cv, ui.search_bar('KSE-100', n=7, t=0, w=int(680 * s), look=lk, placeholder='Search markets'),
             420 * s, 960)
    ui.place(cv, ui.steps(2.4, 5, int(760 * s), lk, labels=None), 450 * s, 1090)
    for i, nm in enumerate(['home', 'chart', 'rupee', 'coin', 'globe', 'shield', 'star', 'bell', 'search', 'clock',
                            'user', 'settings']):
        ui.place(cv, ui.icon(nm, 56, L.text, stroke=2.0, glow=0.5 if L.dark else 0.0, glow_color=L.accent_hi),
                 (80 + (i % 12) * 88) * s, 1190)
    return K.post(cv, lk, 2.0)


def selftest():
    import time
    os.makedirs(K.SELFTEST, exist_ok=True)
    t0 = time.time()
    frames = [('hero_gold', _st_hero()), ('dashboard_gold', _st_dashboard()),
              ('components_gold', _st_components('gold')), ('components_pearl', _st_components('pearl'))]
    paths = []
    for name, fr in frames:
        p = os.path.join(K.SELFTEST, 'kit_%s.png' % name)
        K.save_png(p, fr)
        paths.append(p)
    small = [cv2.resize(cv2.imread(p), (624, 624), interpolation=cv2.INTER_AREA) for p in paths]
    sheet = np.vstack([np.hstack(small[:2]), np.hstack(small[2:])])
    sp = os.path.join(K.SELFTEST, 'kit_sheet.jpg')
    cv2.imwrite(sp, sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('kit selftest: %d frames in %.1f s -> %s' % (len(frames), time.time() - t0, sp))
    return sp


def sheet(module, n=12, samples=1, workers=4):
    """Contact sheet with the canvas' own aspect (render.py's --sheet tiles are fixed 9:16)."""
    import math
    import time
    R = _render_mod()
    R._worker_env(workers)
    mod = R.load_reel(module)
    dur, bpm = float(mod.DUR), getattr(mod, 'BPM', None)
    times = [(k + 0.5) * dur / n for k in range(n)]
    t0 = time.time()
    res = R.run_jobs(R._still_job, [{'reel': module, 't': t, 'samples': samples} for t in times], workers)
    cols = min(n, int(math.ceil(math.sqrt(n * K.H / K.W))))
    rows = int(math.ceil(n / cols))
    tw = 420 if cols <= 4 else 320
    th = int(round(tw * K.H / K.W))
    out = np.full((rows * (th + 6) + 6, cols * (tw + 6) + 6, 3), 18, np.uint8)
    for k, (t, u8, dt) in enumerate(res):
        im = cv2.cvtColor(cv2.resize(u8, (tw, th), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR)
        lab = 't=%.2fs' % t + ('  b%.1f' % (t * bpm / 60.0) if bpm else '')
        cv2.putText(im, lab, (8, 22), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(im, lab, (8, 22), cv2.FONT_HERSHEY_DUPLEX, 0.55, (120, 235, 255), 1, cv2.LINE_AA)
        r, c = divmod(k, cols)
        out[6 + r * (th + 6):6 + r * (th + 6) + th, 6 + c * (tw + 6):6 + c * (tw + 6) + tw] = im
    d = os.path.join(K.OUT, module)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'sheet.jpg')
    cv2.imwrite(p, out, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('sheet: %d frames in %.1fs -> %s' % (n, time.time() - t0, p))
    return p


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'selftest'
    if cmd == 'selftest':
        selftest()
    elif cmd == 'sheet':
        sheet(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
    elif cmd == 'render':
        _render_mod().main(sys.argv[2:])
    else:
        print(__doc__)
