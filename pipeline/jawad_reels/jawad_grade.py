"""jawad_grade.py - the colorist's finish, per-reel looks, LUTs and colour QA for @jawad_mp4 (on top of jawad_kit).

    import jawad_grade as G                       # imports jawad_kit first, registers the looks (idempotent)
    LOOK = 'dusk'                                 # 'ember' | 'noir_ember' | 'inferno' | 'gold_hour' | 'dusk'
    def post(cv, t): return G.finish(cv, LOOK, t) # the reel module's only post call (render.py calls post)

LOOKS (one per reel; all five are orange-red on deep black, told apart by world, blacks and contrast)
    'ember'       kit: warm near-black void, flame key, gold-white cores           (jawad_kit)
    'noir_ember'  kit: near-monochrome warm black, one red-orange practical light  (jawad_kit)
    'inferno'     hot chaos: red-dominant world, harder contrast, deep red-black crush, highlights roll to orange
    'gold_hour'   dusk-to-sunrise warmth: brown-black floor, gold/amber horizon glow + god rays, softer contrast
    'dusk'        night interior: indigo-violet shadows, candle / torch practicals in red-orange
    The three new keys are added with J.register_look (backdrop, K.LOOKS post, bokeh, ui.LOOKS glass, F.GRADES),
    so K.background / K.post / ui.* / F.Clip.get / F.still accept them like the kit looks.

FINISH  G.finish(cv, look, t=0, grain=None, grain_size=None, skin=None, rays=None, rays_center=None, **ov)
    In place on a C-contiguous linear premultiplied float32 (H, W, 4) canvas; returns it (alpha 1). Cost on top
    of K.post: see GRADE.md (measured ~100-130 ms on the shared box, most of it the 2 M-pixel gain gather).
    1  K.post(cv, look, t, grain=0, **ov): exposure, bloom + halation, vignette, edge chroma, mono, crush (the toe)
    2  per-channel characteristic curve in log2 stops around 0.18 (slope `slope` at 0, mid-contrast bump of
       half-width `width` stops, soft shoulder from +2.5 stops): one gain LUT (65536 entries) indexed by the
       top 16 bits of each float (1/128-octave steps)
    3  split tone by luminance (shadows -> the look's shadow colour, highlights -> its highlight colour, mids
       neutral; multiplicative, so black stays black)
    4  blackbody roll-off of saturated emissive light (luminance > ~1): hue goes FLAME -> hot colour -> warm white
    5  saturation by luminance (deep shadows down, mids up to +8 %); skin protection: skin pixels (hue ~8-29 deg,
       fading out by 0 / 43 deg, moderate chroma, mid luminance, measured as drawn) keep 70 % of their value
       after the spatial half of K.post (mono, crush and steps 2-4 reach skin at 30 %) and half of the rest of
       their chromaticity (skin_chroma=0.5): no grey, orange or crushed skin
    6  K.grain(cv, t, amount, size)  (film grain after the tone curve; size 1.6-1.8 px survives the IG encode)
    ov: any K.post override (exposure=1.4 * push, bloom=..., footage=1, vignette=...); grain= / grain_size=;
    skin=0..1 (0 = off); rays= god-ray strength (gold_hour default 0.26) and rays_center=(x, y) px.
    Exposure pushes on cut frames: G.finish(cv, LOOK, t, exposure=1.4 * push, bloom=G.bloom(LOOK) * (1 + .9 * push)).
    Reels built on jawad_tx: G.tx_finish(cv, t, LOOK, cuts=CUTS, **plan.post_kw(t)) = jawad_tx.finish's push /
    bloom-out / rgb-split, then this finish (same argument order as X.finish).

COLOUR ONLY (no spatial ops; this is what the LUTs contain)
    G.grade_rgb(lin, look) -> graded linear float32 (h, w, 3): exposure, mono, crush, steps 2-5 (no bloom,
        halation, vignette, edge chroma or grain). G.display(lin) -> float sRGB 0..1 through the toolkit's
        shoulder (exact, no dither).
    G.cutout(spr, look, exposure=0.0) -> new premultiplied sprite graded with F.GRADES[look] plus the finish's
        skin protection (an optional footage-style match for a cut-out; colour only, never smooths texture).
        The frame is still finished once by G.finish; most scenes need no cut-out pre-grade at all.

LUTS / CHART / QA (python3 jawad_grade.py <cmd>; outputs under <WS>/looks/)
    lut <look|all>        luts/<look>_33.cube (33^3, red fastest, sRGB in -> sRGB out, includes the shoulder)
    chart <look|all>      chart_<look>_before.png / _after.png + chart_<look>.json (swatch / skin numbers)
    sheet                 looks_sheet.jpg: the same test frame (type + cut-out + UI card) under all five looks,
                          thumbnails and 5-colour k-means fingerprints
    clip <look|all> [s]   <look>/<look>_test.mp4 (s seconds of the test scene, 1 sample, CRF 14)
    verify <mp4> <look>   signalstats, hue budget, skin, vectorscope, banding after x264 CRF 23 / 3.5 Mbit
                          re-encodes, k-means fingerprint -> <mp4 dir>/qa_<name>/verify.json
    --selftest            registration, kit keys untouched, black never lifted, chart numbers, LUT identity
                          and match through ffmpeg, finish timing; exits 1 on any failure
"""
import functools
import json
import math
import os
import subprocess
import sys
import time

import jawad_kit as J                      # FIRST: brand palette, kit looks, house styles
from jawad_kit import K, ui, F             # noqa: E402

import cv2                                  # noqa: E402
import numpy as np                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LUT_DIR = os.path.join(HERE, 'luts')
OUT = os.path.join(K.WS, 'looks')
FACES_TOOLS = '/home/user/100/workspace/brand_reels/charsheet/tools'
CUTOUTS = '/home/user/100/workspace/brand_reels/charsheet/cutouts'

KIT_LOOKS = ('ember', 'noir_ember')
NEW_LOOKS = ('inferno', 'gold_hour', 'dusk')
ALL_LOOKS = KIT_LOOKS + NEW_LOOKS

LUMA = np.float32([0.2126, 0.7152, 0.0722])
LUMA4 = np.float32([[0.2126, 0.7152, 0.0722, 0.0]])

# snapshot of the kit's own keys before anything here runs (the self-test proves they stay untouched)
_KIT_SNAPSHOT = {k: repr(sorted(K.LOOKS[k].items())) for k in KIT_LOOKS}
_KIT_GRADE_SNAPSHOT = {k: repr(sorted(F.GRADES[k].items())) for k in KIT_LOOKS}
_KIT_BG_SNAPSHOT = {k: repr(K._BG_LOOKS[k]) for k in KIT_LOOKS}


def _col(spec):
    """Palette name | '#hex' | (r, g, b) linear -> np.float32[3] linear."""
    if isinstance(spec, str):
        return np.asarray(K.hexlin(spec) if spec.startswith('#') else K.C[spec], np.float32)
    return np.asarray(spec, np.float32)[:3]


# =============================================================================================== the GRADE table
# slope: log-log slope of the characteristic curve at 0.18; width: half-width (stops) of the mid-contrast bump
# (the curve returns to slope ~1 in the deep toe, where the kit's crush is the toe); shoulder: (start stops,
# depth stops). shadow / highlight: (colour, strength) of the luminance split tone. sat: (deep shadows, mids,
# highlights) saturation. bb: blackbody roll-off (hot colour and white-hot colour (linear RGB), strengths,
# thresholds l0..l1 (towards hot) and w0..w1 (towards white) in linear luminance BEFORE the curve). skin: share of
# the ungraded value skin keeps; skin_chroma: extra pull of skin's chromaticity back to ungraded. grain /
# grain_size: film grain amount / size in px.
FIN = {
    'ember': dict(
        slope=1.16, width=1.6, shoulder=(2.5, 1.5), shadow=('EMBER', 0.05), highlight=('GOLD', 0.04),
        sat=(0.82, 1.06, 1.0),
        bb=dict(hot=(1.0, 0.45, 0.12), white=(1.0, 0.88, 0.70), k_hot=0.75, k_white=0.85, l0=0.8, l1=2.5, w0=1.6,
                w1=5.0),
        skin=0.70, skin_chroma=0.5, grain=0.016, grain_size=1.8, rays=0.0),
    'noir_ember': dict(
        slope=1.26, width=1.5, shoulder=(2.5, 1.5), shadow=('SMOKE', 0.04), highlight=('AMBER', 0.03),
        sat=(0.60, 0.92, 1.0),
        bb=dict(hot=(1.0, 0.50, 0.18), white=(1.0, 0.90, 0.78), k_hot=0.70, k_white=0.85, l0=0.8, l1=2.5, w0=1.6,
                w1=5.0),
        skin=0.70, skin_chroma=0.5, grain=0.022, grain_size=1.7, rays=0.0),
    'inferno': dict(
        slope=1.30, width=1.7, shoulder=(2.5, 1.3), shadow=('EMBER', 0.08), highlight=('FLAME', 0.04),
        sat=(0.86, 1.05, 1.0),
        bb=dict(hot=(1.0, 0.30, 0.06), white=(1.0, 0.75, 0.50), k_hot=0.80, k_white=0.40, l0=0.8, l1=3.0, w0=3.0,
                w1=8.0),
        skin=0.70, skin_chroma=0.5, grain=0.020, grain_size=1.7, rays=0.0),
    'gold_hour': dict(
        slope=1.10, width=1.8, shoulder=(2.5, 1.7), shadow=('#2B1407', 0.10), highlight=('GOLD', 0.07),
        sat=(0.86, 1.05, 1.0),
        bb=dict(hot=(1.0, 0.55, 0.20), white=(1.0, 0.92, 0.78), k_hot=0.75, k_white=0.90, l0=0.7, l1=2.2, w0=1.4,
                w1=4.0),
        skin=0.70, skin_chroma=0.5, grain=0.018, grain_size=1.6, rays=0.26, rays_center=(0.52, 0.78),
        rays_threshold=0.30, rays_length=0.42),
    'dusk': dict(
        slope=1.20, width=1.6, shoulder=(2.5, 1.5), shadow=('#171431', 0.20), highlight=('FLAME', 0.04),
        sat=(0.80, 1.06, 1.0),
        bb=dict(hot=(1.0, 0.45, 0.12), white=(1.0, 0.88, 0.72), k_hot=0.75, k_white=0.80, l0=0.8, l1=2.5, w0=1.8,
                w1=5.5),
        skin=0.70, skin_chroma=0.5, grain=0.020, grain_size=1.7, rays=0.0),
}

# hue-budget rule per look (verify): 'share' = red-orange >= 60 % of saturated px; 'top5' = the brightest 5 %
# of saturated px are red-orange (>= 60 %) and violet <= 45 % of saturated px
BUDGET = {'ember': 'share', 'noir_ember': 'share', 'inferno': 'share', 'gold_hour': 'share', 'dusk': 'top5'}


# =============================================================================================== new looks
def _hx(h):
    return K.hexlin(h)


def _new_look_defs():
    """Backdrop, post, bokeh, glass-UI and footage grade of the three colorist looks (all ADDED keys)."""
    C, v = K.C, ui._v
    d = {}
    # ---- inferno: hot chaos. Red-black void, fire floor from below, red haze curtains, ember hazes, sparks.
    d['inferno'] = dict(
        bg=dict(top='NIGHT_0', bottom='NIGHT_1', lift=0.20, base_tint=(1.55, 0.78, 0.70),
                blobs=[
                    (0.50, 1.04, 0.95, 0.26, 0, 'EMBER', 0.46, 0.04, 0.02, 21.0, 0.6),    # fire floor from below
                    (0.52, 0.95, 0.40, 0.09, 0, 'FLAME', 0.10, 0.06, 0.02, 11.0, 0.6),    # hot band (flame tips)
                    (0.16, 0.30, 0.46, 0.26, 22, 'RED', 0.15, 0.06, 0.05, 17.0, 0.9),     # red haze top left
                    (0.88, 0.58, 0.42, 0.30, -30, 'EMBER', 0.30, 0.05, 0.05, 19.0, 0.8),  # ember haze right
                    (0.72, 0.10, 0.30, 0.14, -20, 'RED', 0.07, 0.05, 0.04, 23.0, 0.4),    # second red light
                ],
                rim=None, dots=0.0, dots_lit=0.0, noise=0.80),
        post=dict(exposure=0.0, bloom=0.70, bloom_threshold=0.38, bloom_tint=(1.0, 0.30, 0.12), halation=0.20,
                  vignette=0.58, chroma=1.4, grain=0.020, crush=(0.014, 0.018, 0.026), mono=0.0,
                  anamorphic_color=tuple(C['RED'])),
        bokeh=(34, ('RED', 'FLAME', 'EMBER'), (6, 52), 0.30),
        ui=dict(tint_top=v(K.mix(C['NIGHT_1'], C['EMBER'], 0.20)), tint_bot=v(C['NIGHT_0']), tint_a=0.72,
                accent=v(C['RED']), accent_hi=v(C['FLAME']), grad=(v(C['RED']), v(C['EMBER'])),
                grad_hi=(v(C['FLAME']), v(C['RED'])), rim=v(C['FLAME']), rim2=v(C['RED']), glow=v(C['RED']),
                ok=v(C['FLAME']), ok_hi=v(C['AMBER'])),
        grade=dict(wb=(1.03, 0.99, 0.95), exposure=-0.06, contrast=1.10, pivot=0.40, black=0.0,
                   black_tint=(0.25, 0.04, 0.03), shadow_tint=(0.0, -0.010, -0.016),
                   highlight_tint=(0.010, 0.0, -0.010), sat=0.96, shoulder=0.90))
    # ---- gold_hour: dusk-to-sunrise. Brown-black floor, gold horizon band with an amber sun core, flame edges.
    d['gold_hour'] = dict(
        bg=dict(top='NIGHT_0', bottom='NIGHT_1', lift=0.45, base_tint=(2.85, 1.95, 0.92),
                blobs=[
                    (0.50, 0.80, 0.90, 0.20, 0, 'GOLD', 0.24, 0.03, 0.01, 29.0, 0.5),     # horizon band
                    (0.52, 0.78, 0.24, 0.09, 0, 'AMBER', 0.20, 0.02, 0.01, 21.0, 0.0),    # sun core
                    (0.08, 0.68, 0.40, 0.30, 25, 'FLAME', 0.11, 0.04, 0.04, 23.0, 0.6),   # flame edge left
                    (0.94, 0.62, 0.40, 0.30, -25, 'FLAME', 0.09, 0.04, 0.04, 27.0, 0.6),  # flame edge right
                    (0.50, -0.06, 0.90, 0.22, 0, 'GOLD', 0.05, 0.03, 0.01, 31.0, 0.0),    # sky lift from the top
                    (0.50, 1.06, 0.90, 0.12, 0, 'EMBER', 0.10, 0.02, 0.01, 33.0, 0.0),    # ground
                ],
                rim=None, dots=0.0, dots_lit=0.0, noise=0.45),
        post=dict(exposure=0.0, bloom=0.66, bloom_threshold=0.42, bloom_tint=(1.0, 0.62, 0.28), halation=0.14,
                  vignette=0.42, chroma=1.0, grain=0.018, crush=(0.004, 0.007, 0.012), mono=0.0,
                  anamorphic_color=tuple(C['GOLD'])),
        bokeh=(26, ('GOLD', 'AMBER', 'FLAME'), (8, 60), 0.22),
        ui=dict(tint_top=v(K.mix(_hx('#2B1407'), C['SMOKE'], 0.5)), tint_bot=v(_hx('#1D1007')), tint_a=0.68,
                accent=v(C['GOLD']), accent_hi=v(C['AMBER']), grad=(v(C['FLAME']), v(C['RED'])),
                grad_hi=(v(C['AMBER']), v(C['FLAME'])), rim=v(C['AMBER']), rim2=v(C['FLAME']), glow=v(C['GOLD']),
                ok=v(C['GOLD']), ok_hi=v(C['LEAF_HI'])),
        grade=dict(wb=(1.02, 1.0, 0.96), exposure=0.0, contrast=1.0, pivot=0.42, black=0.0,
                   black_tint=(0.11, 0.06, 0.03), shadow_tint=(0.0, -0.002, -0.012),
                   highlight_tint=(0.006, 0.004, -0.008), sat=0.97, shoulder=0.92))
    # ---- dusk: a night interior. Indigo-violet base, a candle pool with an amber core, a torch beam, warm floor.
    d['dusk'] = dict(
        bg=dict(top='NIGHT_0', bottom='NIGHT_1', lift=0.55, base_tint=(1.05, 1.45, 7.0),
                blobs=[
                    (0.78, 0.70, 0.30, 0.20, -15, 'FLAME', 0.20, 0.02, 0.02, 7.0, 0.3),   # candle pool
                    (0.80, 0.69, 0.08, 0.06, 0, 'AMBER', 0.14, 0.01, 0.01, 3.1, 0.0),     # candle core
                    (0.30, 0.30, 0.70, 0.07, -38, 'FLAME', 0.05, 0.03, 0.02, 19.0, 0.0),  # torch beam
                    (0.10, 0.95, 0.50, 0.25, 20, 'EMBER', 0.10, 0.03, 0.03, 29.0, 0.4),   # warm floor bounce
                ],
                rim=None, dots=0.0, dots_lit=0.0, noise=0.40),
        post=dict(exposure=0.0, bloom=0.60, bloom_threshold=0.42, bloom_tint=(1.0, 0.45, 0.20), halation=0.16,
                  vignette=0.55, chroma=1.2, grain=0.020, crush=(0.010, 0.014, 0.005), mono=0.0),
        bokeh=(14, ('FLAME', 'AMBER', 'RED'), (8, 56), 0.18),
        ui=dict(tint_top=v(K.mix(_hx('#171431'), C['NIGHT_0'], 0.35)), tint_bot=v(_hx('#0C0208')), tint_a=0.72,
                text2=v(K.mix(C['IVORY'], _hx('#D9D2EE'), 0.35), 0.56), accent=v(C['FLAME']),
                accent_hi=v(C['AMBER']), grad=(v(C['FLAME']), v(C['RED'])), grad_hi=(v(C['AMBER']), v(C['FLAME'])),
                rim=v(C['HOT_PINK']), rim2=v(C['RED']), glow=v(C['FLAME']), ok=v(C['GOLD'])),
        grade=dict(wb=(1.0, 0.98, 1.03), exposure=-0.06, contrast=1.08, pivot=0.40, black=0.0,
                   black_tint=(0.09, 0.08, 0.19), shadow_tint=(-0.006, -0.008, 0.006),
                   highlight_tint=(0.020, 0.006, -0.016), sat=0.98, shoulder=0.90))
    return d


def register():
    """Add 'inferno', 'gold_hour', 'dusk' through J.register_look (idempotent; never touches existing keys)."""
    if getattr(K, '_jawad_grade_applied', False):
        return
    for name, d in _new_look_defs().items():
        if name in K.LOOKS or name in K._BG_LOOKS or name in ui.LOOKS or name in F.GRADES:
            print('[jawad_grade] %r already exists: left as it is' % name, file=sys.stderr)
            continue
        J.register_look(name, base='ember', bg=d['bg'], post=d['post'], bokeh=d['bokeh'], ui_look=d['ui'],
                        grade=d['grade'])
    K._jawad_grade_applied = True


register()


def bloom(look):
    """The look's bloom strength (for exposure pushes: bloom=G.bloom(LOOK) * (1 + 0.9 * push))."""
    return float(K.LOOKS[look].get('bloom', 0.55))


# =============================================================================================== curves
def _sstep(a, b, x):
    t = np.clip((np.asarray(x, np.float64) - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _stops(s, P):
    """Characteristic curve in log2 stops around 0.18: slope P['slope'] at 0, back to ~1 in the toe."""
    g, w = P['slope'], P['width']
    s = np.asarray(s, np.float64)
    y = s + (g - 1.0) * s * np.exp(-s * s / (2.0 * w * w))
    a, D = P['shoulder']
    return np.where(y > a, a + D * (1.0 - np.exp(-(y - a) / D)), y)


def tone_curve(x, look):
    """Scalar / array linear -> linear through the look's characteristic curve (no LUT quantisation)."""
    P = FIN[look]
    x = np.asarray(x, np.float64)
    xs = np.maximum(x, 2.0 ** -12)
    return x * (0.18 * 2.0 ** _stops(np.log2(xs / 0.18), P) / xs)


def _norm_dir(col):
    c = np.maximum(_col(col).astype(np.float64), 1e-5)
    return c / float(c @ LUMA)


@functools.lru_cache(maxsize=8)
def _params(look):
    """Derived per-look tables: tone gain LUT, split/sat LUTs, blackbody constants."""
    if look not in FIN:
        raise KeyError('jawad_grade: unknown look %r (use one of %s)' % (look, ', '.join(ALL_LOOKS)))
    P = FIN[look]
    # 2: tone as a GAIN LUT indexed by the top 16 bits of the float32 value (sign, exponent, 7 mantissa bits:
    #    a log-spaced index, 1/128 octave per step, 0.16 % gain steps at most); evaluated at each bucket's middle
    codes = np.arange(65536, dtype=np.uint32)
    with np.errstate(invalid='ignore', over='ignore'):
        xm = ((codes << 16) | 0x8000).view(np.float32).astype(np.float64)
        ok = np.isfinite(xm) & (xm >= 0) & (codes < 0x8000)
    xs = np.maximum(np.where(ok, xm, 1.0), 2.0 ** -12)
    gain = np.where(ok, 0.18 * 2.0 ** _stops(np.log2(xs / 0.18), P) / xs, 1.0).astype(np.float32)
    gain.flags.writeable = False
    # 3 + 5: split tone and saturation by luminance; index = round(255 * sqrt(L)) (L clipped to 1)
    i = np.arange(256, dtype=np.float64)
    Lq = (i / 255.0) ** 2
    s = np.log2(np.maximum(Lq, 2.0 ** -16) / 0.18)
    w_sh = 1.0 - _sstep(-4.5, -1.0, s)
    w_hi = _sstep(0.5, 2.5, s)
    sc, sa = P['shadow']
    hc, ha = P['highlight']
    gs = _norm_dir(sc)[None, :] ** (sa * w_sh[:, None]) * _norm_dir(hc)[None, :] ** (ha * w_hi[:, None])
    gs /= (gs @ LUMA.astype(np.float64))[:, None]
    k_lo, k_mid, k_hi = P['sat']
    k = k_lo + (k_mid - k_lo) * _sstep(-6.5, -3.0, s)
    k = k + (k_hi - k) * _sstep(0.8, 2.6, s)
    tabA = np.zeros((256, 1, 4), np.float32)
    tabB = np.zeros((256, 1, 4), np.float32)
    tabA[:, 0, :3] = gs * k[:, None]
    tabA[:, 0, 3] = 1.0
    tabB[:, 0, :3] = gs * (1.0 - k)[:, None]
    # 4: blackbody: thresholds on the luminance BEFORE the curve (a saturated glow's own channel shoulder would
    #    hide its intensity after it); hot / white colours are blackbody-like (B rises with G: gold, then warm white,
    #    never lemon yellow)
    bb = dict(P['bb'])
    bbp = dict(l0=bb['l0'], l1=bb['l1'], w0=bb['w0'], w1=bb['w1'], k_hot=bb['k_hot'], k_white=bb['k_white'],
               n_hot=_norm_dir(bb['hot']).astype(np.float32), n_white=_norm_dir(bb['white']).astype(np.float32))
    return dict(gain=gain, tabA=tabA, tabB=tabB, bb=bbp, k=k, gs=gs)


# =============================================================================================== colour steps
def _ss32(a, b, x):
    t = np.clip((x - np.float32(a)) * np.float32(1.0 / (b - a)), 0.0, 1.0)
    return t * t * (np.float32(3.0) - np.float32(2.0) * t)


def _blackbody(cv, L, idx, Lin, Q):
    """Step 4: saturated pixels idx (pre-curve luminance Lin above l0) move from their own hue towards the hot
    colour, then towards warm white, as Lin rises (L = luminance after the curve, kept)."""
    bb = Q['bb']
    flat = cv.reshape(-1, cv.shape[-1])
    c = flat[idx, :3]
    lm = L.ravel()[idx]
    mx = c.max(1)
    sat = (mx - c.min(1)) / np.maximum(mx, np.float32(1e-6))
    wf = _ss32(0.35, 0.75, sat)
    t1 = _ss32(bb['l0'], bb['l1'], Lin) * np.float32(bb['k_hot']) * wf
    t2 = _ss32(bb['w0'], bb['w1'], Lin) * np.float32(bb['k_white']) * wf
    n = c / np.maximum(lm, np.float32(1e-6))[:, None]
    n += (bb['n_hot'][None, :] - n) * t1[:, None]
    n += (bb['n_white'][None, :] - n) * t2[:, None]
    flat[idx, :3] = n * lm[:, None]


def _color(cv, look):
    """Steps 2-4 + saturation, in place on an (h, w, 4) float32 canvas (alpha comes back as 1)."""
    Q = _params(look)
    Lin = cv2.transform(cv, LUMA4).ravel()                                            # pre-curve luminance
    hot = np.flatnonzero(Lin > np.float32(Q['bb']['l0']))
    Lhot = Lin[hot]
    cv2.multiply(cv, Q["gain"][cv.view(np.uint16)[..., 1::2]], dst=cv)               # tone (bf16-indexed gain)
    cv[..., 3] = 1.0
    L = cv2.transform(cv, LUMA4)
    i4 = cv2.cvtColor(cv2.convertScaleAbs(cv2.sqrt(cv2.max(L, 0.0)), alpha=255.0), cv2.COLOR_GRAY2RGBA)
    A = cv2.LUT(i4, Q['tabA'])
    B = cv2.LUT(i4, Q['tabB'])
    cv2.multiply(cv, A, dst=cv)
    cv2.multiply(B, cv2.cvtColor(L, cv2.COLOR_GRAY2RGBA), dst=B)
    cv2.add(cv, B, dst=cv)
    if hot.size:
        _blackbody(cv, L, hot, Lhot, Q)
    return cv


def _skin_weight(rgb):
    """Skin likelihood 0..1 of linear RGB (h, w, 3): hue ~8-29 deg (fading out by 0 and 43), chroma 0.30-0.60
    (HSV S of sqrt-encoded values), mid luminance (linear ~0.045-0.5). Brand orange / red (S ~0.9), warm-white
    fabric under warm light (S ~0.2) and warm blacks score 0. Colour qualifier only (as on a grading desk)."""
    q = np.sqrt(np.maximum(np.asarray(rgb, np.float32), 0.0))
    R, G, B = q[..., 0], q[..., 1], q[..., 2]
    d = R - B
    hf = (G - B) / np.maximum(d, np.float32(1e-4))         # HSV hue / 60 deg when R >= G >= B
    S = d / np.maximum(R, np.float32(1e-4))                # HSV saturation
    Y = np.sqrt(np.maximum((q * q) @ LUMA, 0.0))
    w = _ss32(0.0, 0.13, hf) * (1 - _ss32(0.48, 0.72, hf))       # wide, smooth ramps: a 33-point LUT follows them
    w *= _ss32(0.16, 0.30, S) * (1 - _ss32(0.60, 0.76, S))
    w *= _ss32(0.11, 0.21, Y) * (1 - _ss32(0.70, 0.90, Y))
    return w.astype(np.float32)


def _skin_map(cv):
    """Quarter-res skin analysis of the canvas as drawn -> (flat pixel indices, full-res weights there) or None.
    Only pixels near skin-like colour are touched later (gather / scatter), so the cost follows the skin area."""
    h, w = cv.shape[:2]
    sm = cv2.resize(cv, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    wt = _skin_weight(sm[..., :3])
    if float(wt.max()) < 0.02:
        return None
    wt = cv2.GaussianBlur(wt, (0, 0), 0.7)
    m = cv2.dilate((wt > 0.01).astype(np.uint8), np.ones((3, 3), np.uint8))
    idx = np.flatnonzero(cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST))
    if idx.size == 0:
        return None
    wf = cv2.resize(wt, (w, h), interpolation=cv2.INTER_LINEAR).ravel()[idx]
    return idx, wf


def _skin_blend(flat, idx, ref, w, extra):
    """flat = canvas.reshape(-1, C); pixels idx keep share w of their ungraded value `ref` (n, 3); then their
    chromaticity is pulled a further `extra` of the way back (at the blended luminance), so a strong look never
    turns skin orange or grey."""
    o = flat[idx, :3]
    o += (ref - o) * w[:, None]
    if extra > 0:
        Lo = o @ LUMA
        Lr = ref @ LUMA
        ok = Lr > 1e-5
        k = np.where(ok, Lo / np.maximum(Lr, np.float32(1e-5)), 0.0).astype(np.float32)
        wk = (w * np.float32(extra) * ok).astype(np.float32)
        o += (ref * k[:, None] - o) * wk[:, None]
    flat[idx, :3] = o


def _post_split(cv, look, t, ov):
    """K.post in two halves so the skin reference sits between them: the toolkit's spatial post (exposure,
    bloom + halation, vignette, edge chroma; grain off) and then the kit's per-pixel mono + crush, exactly as
    jawad_kit's K.post wrapper orders them. Returns a callable that runs the second half."""
    orig = getattr(K.post, '_jawad_orig', None)
    if orig is None or look not in J.LOOK_NAMES:                     # kit wrapper missing: one call, no split
        K.post(cv, look, t, **dict(ov, grain=0.0))
        return lambda: None
    cfg = dict(K.LOOKS[look])
    cfg.update(ov)
    orig(cv, look, t, **dict(ov, grain=0.0))

    def second():
        J._mono(cv, float(cfg.get('mono') or 0.0))
        J._crush(cv, cfg.get('crush'))
        cv[..., 3] = 1.0
    return second


def finish(cv, look, t=0.0, grain=None, grain_size=None, skin=None, rays=None, rays_center=None, **ov):
    """The reel's finish (see the module docstring). In place; returns cv (alpha 1)."""
    P = FIN[look]
    sk = P['skin'] if skin is None else float(skin)
    rs = P.get('rays', 0.0) if rays is None else float(rays)
    if rs > 0:
        c = rays_center or (P['rays_center'][0] * K.W, P['rays_center'][1] * K.H)
        K.god_rays(cv, c, strength=rs, threshold=P.get('rays_threshold', 0.3), length=P.get('rays_length', 0.4),
                   tint=(1.0, 0.78, 0.45))
    if not (isinstance(cv, np.ndarray) and cv.dtype == np.float32 and cv.ndim == 3 and cv.flags.c_contiguous):
        raise ValueError('G.finish needs a C-contiguous float32 (H, W, 4) canvas')
    sm = _skin_map(cv) if sk > 0 else None                           # skin as drawn (before exposure pushes)
    second = _post_split(cv, look, t, ov)
    flat = cv.reshape(-1, cv.shape[2])
    ref = flat[sm[0], :3] if sm is not None else None                # skin's ungraded value (spatial post only)
    second()                                                         # mono + crush (the toe)
    _color(cv, look)                                                 # steps 2-5
    if ref is not None:
        _skin_blend(flat, sm[0], ref, sm[1] * np.float32(sk), P.get('skin_chroma', 0.0))
    g = P['grain'] if grain is None else float(grain)
    if g > 0:
        K.grain(cv, t, g, P['grain_size'] if grain_size is None else float(grain_size))
    cv[..., 3] = 1.0
    return cv


def tx_finish(cv, t, look, cuts=(), **kw):
    """Drop-in for jawad_tx.finish (same argument order and keywords: cuts, push, bloomout, rgb_split,
    push_decay, bloom_scale, any K.post key) that ends in G.finish: jawad_tx computes the exposure push / L4
    bloom-out / D7 split exactly as it does today, then this finish grades the frame.
        def post(cv, t): return G.tx_finish(cv, t, LOOK, cuts=CUTS, **plan.post_kw(t))
    (jawad_tx's K.post call is captured for the duration of the call: render workers are single-threaded.)"""
    import jawad_tx as X
    got = {}

    def _capture(canvas, lk, tt=0.0, **ov):
        got.update(ov)
        return canvas
    orig = K.post
    K.post = _capture
    try:
        X.finish(cv, t, look, cuts=cuts, **kw)
    finally:
        K.post = orig
    extra = {k: got.pop(k) for k in ('grain', 'grain_size', 'skin', 'rays', 'rays_center') if k in got}
    return finish(cv, look, t, **extra, **got)


def grade_rgb(lin, look, skin=True):
    """Colour-only grade of linear RGB (h, w, 3) (or (n, 3)) -> graded linear float32, same shape: exposure,
    mono, crush (the kit's per-pixel post), steps 2-5 and the skin blend. Exactly what the .cube holds
    (before the toolkit shoulder)."""
    lin = np.asarray(lin, np.float32)
    shp = lin.shape
    a = lin.reshape(-1, 1, 3) if lin.ndim == 2 else lin
    cv = np.ones(a.shape[:2] + (4,), np.float32)
    cv[..., :3] = a
    P, cfg = FIN[look], K.LOOKS[look]
    w = _skin_weight(cv[..., :3]).ravel() * np.float32(P['skin']) if skin and P['skin'] > 0 else None
    if cfg.get('exposure'):
        cv[..., :3] *= np.float32(2.0 ** cfg['exposure'])
    flat = cv.reshape(-1, 4)
    idx = np.flatnonzero(w > 0) if w is not None else None
    ref = flat[idx, :3] if w is not None else None
    J._mono(cv, float(cfg.get('mono') or 0.0))
    if cfg.get('crush'):
        J._crush(cv, cfg['crush'])
    cv[..., 3] = 1.0
    _color(cv, look)
    if w is not None and idx.size:
        _skin_blend(flat, idx, ref, w[idx], P.get('skin_chroma', 0.0))
    return np.ascontiguousarray(cv[..., :3]).reshape(shp)


def display(lin):
    """Linear RGB -> float sRGB 0..1 through the toolkit's shoulder (exact, no dither)."""
    return K.to_srgb(K._shoulder_curve(np.asarray(lin, np.float64))).astype(np.float32)


def cutout(spr, look, exposure=0.0):
    """Footage-style match for a cut-out sprite (premultiplied linear (h, w, 4)) -> NEW sprite graded with
    F.GRADES[look] (white balance, contrast about the pivot, never-lifted blacks, split tints, saturation), with
    the finish's skin protection (skin keeps 70 % of its value + half of the rest of its chromaticity).
    Colour only: texture, pores and hair stay as they are. The frame is still finished once by G.finish."""
    a = spr[..., 3:4]
    rgb = np.clip(spr[..., :3] / np.maximum(a, 1e-6) * np.float32(2.0 ** exposure), 0, 1).astype(np.float32)
    g = F.grade(rgb, look).astype(np.float32)
    P = FIN[look]
    w = _skin_weight(rgb).ravel() * np.float32(P['skin'])
    idx = np.flatnonzero(w > 0)
    if idx.size:
        flat = g.reshape(-1, 3)
        _skin_blend(flat, idx, rgb.reshape(-1, 3)[idx], w[idx], P.get('skin_chroma', 0.0))
    out = np.empty_like(spr)
    out[..., :3] = g * a
    out[..., 3:] = a
    return out


def footage_skin_check(look):
    """F.GRADES[look] alone on the chart's skin patches -> [(name, dhue OKLab deg, chroma ratio, dL x 100)]
    (footage read with F.Clip.get(look=...) / F.still(look=...) has no skin protection before the finish)."""
    out = []
    for name, hx in SKIN_PATCHES:
        c = np.asarray(K.hexlin(hx), np.float32)[None, None]
        b, a = _u8(display(c[0, 0])), _u8(display(F.grade(c, look)[0, 0]))
        L0, C0, h0 = _lch(oklab_u8(b))
        L1, C1, h1 = _lch(oklab_u8(a))
        out.append((name, round(float(_dhue(h1, h0)), 2), round(float(C1 / C0), 3), round(float((L1 - L0) * 100), 2)))
    return out


# =============================================================================================== metrics
def oklab_u8(rgb_u8):
    """uint8 sRGB (..., 3) -> OKLab (..., 3) float64."""
    return K._oklab(K.to_lin(np.asarray(rgb_u8, np.float32) / 255.0).astype(np.float64))


def _lch(lab):
    lab = np.asarray(lab, np.float64)
    return lab[..., 0], np.hypot(lab[..., 1], lab[..., 2]), np.degrees(np.arctan2(lab[..., 2], lab[..., 1]))


def _dhue(h1, h0):
    return (h1 - h0 + 180.0) % 360.0 - 180.0


def hsv_hue_deg(rgb_u8):
    """Median HSV hue (degrees) and saturation of uint8 RGB pixels (n, 3)."""
    p = np.asarray(rgb_u8, np.uint8).reshape(-1, 1, 3)
    hsv = cv2.cvtColor(p, cv2.COLOR_RGB2HSV_FULL).reshape(-1, 3).astype(np.float64)
    ang = hsv[:, 0] / 256.0 * 2 * math.pi
    hue = math.degrees(math.atan2(np.median(np.sin(ang)), np.median(np.cos(ang)))) % 360.0
    return hue, float(np.median(hsv[:, 1]) / 255.0)


def hue_budget(rgb_u8, mode='share'):
    """OpenCV-HSV hue budget of a uint8 RGB frame: pixels with S > 80 and V > 60. Returns dict with the
    red-orange share (H 0-25 or 170-180), the violet share (H 115-165) and the red-orange share of the brightest
    5 % of saturated pixels."""
    hsv = cv2.cvtColor(np.ascontiguousarray(rgb_u8), cv2.COLOR_RGB2HSV)
    Hh, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    sat = (S > 80) & (V > 60)
    n = int(sat.sum())
    if n == 0:
        return dict(sat_px=0, red_orange=None, violet=None, top5_red_orange=None)
    h = Hh[sat]
    ro = (h <= 25) | (h >= 170)
    vi = (h >= 115) & (h <= 165)
    v = V[sat].astype(np.int32)
    thr = np.percentile(v, 95)
    top = v >= thr
    return dict(sat_px=n, sat_frac=round(n / sat.size, 4), red_orange=round(float(ro.mean()), 4),
                violet=round(float(vi.mean()), 4), top5_red_orange=round(float(ro[top].mean()), 4))


# =============================================================================================== chart
SKIN_PATCHES = (('skin_light', '#E0B49A'), ('skin_jawad_suit', '#C49487'), ('skin_jawad_street', '#B4806F'),
                ('skin_deep', '#6E4A3A'))
SWATCHES = ('FLAME', 'RED', 'EMBER', 'GOLD', 'AMBER', 'NIGHT_0', 'NIGHT_1', 'SMOKE', 'ASH', 'IVORY')
EMISSIVE = (('FLAME', 3.0), ('FLAME', 6.0), ('FLAME', 12.0), ('RED', 4.0), ('RED', 9.0), ('GOLD', 4.0),
            ('GOLD', 10.0), ('IVORY', 1.6))


def chart_canvas():
    """1080x1920 linear test chart -> (canvas (H, W, 4), regions {name: (y0, y1, x0, x1, kind)})."""
    W, H = K.W, K.H
    cv = np.zeros((H, W, 4), np.float32)
    cv[..., 3] = 1.0
    reg = {}
    # grey ramp 0..1.6 linear
    x = np.linspace(0.0, 1.6, 1000, dtype=np.float32)
    cv[60:170, 40:1040, :3] = x[None, :, None]
    reg['grey_ramp'] = (60, 170, 40, 1040, 'ramp')
    # hue wheels: HSV(hue = angle, sat = radius), V 0.85 (left, big) and V 0.40 (right, small)
    for (cx, cy, r, val, name) in ((300, 470, 240, 0.85, 'wheel_bright'), (810, 470, 170, 0.40, 'wheel_dark')):
        yy, xx = np.mgrid[cy - r:cy + r, cx - r:cx + r].astype(np.float32)
        dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
        rr = np.sqrt(dx * dx + dy * dy) / r
        hue = (np.degrees(np.arctan2(-dy, dx)) % 360.0) / 2.0
        hsv = np.dstack([hue, np.clip(rr, 0, 1) * 255, np.full_like(rr, val * 255)]).astype(np.float32)
        rgb = cv2.cvtColor(np.round(hsv).astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
        m = (rr <= 1.0)[..., None]
        blk = cv[cy - r:cy + r, cx - r:cx + r, :3]
        cv[cy - r:cy + r, cx - r:cx + r, :3] = np.where(m, K.to_lin(rgb), blk)
        reg[name] = (cy - r, cy + r, cx - r, cx + r, 'wheel')
    # palette swatches at 0.5x / 1x / 2x
    for j, ex in enumerate((0.5, 1.0, 2.0)):
        y0 = 760 + j * 100
        for i, name in enumerate(SWATCHES):
            x0 = 40 + i * 100
            cv[y0:y0 + 90, x0:x0 + 92, :3] = K.C[name] * ex
            kind = 'swatch' if K.lum(K.C[name]) * ex <= 1 else 'emissive'
            reg['%s@%gx' % (name, ex)] = (y0, y0 + 90, x0, x0 + 92, kind)
    # skin patches
    for i, (name, hx) in enumerate(SKIN_PATCHES):
        x0 = 40 + i * 252
        cv[1080:1300, x0:x0 + 240, :3] = K.hexlin(hx)
        reg[name] = (1080, 1300, x0, x0 + 240, 'skin')
    # dark warm gradient (banding / toe check): 0 -> 1.6 x SMOKE, and a neutral one 0 -> 0.04
    ramp = np.linspace(0.0, 1.0, 1000, dtype=np.float32)
    cv[1340:1460, 40:1040, :3] = ramp[None, :, None] * (K.C['SMOKE'] * 1.6)[None, None, :]
    reg['dark_warm_gradient'] = (1340, 1460, 40, 1040, 'ramp')
    cv[1470:1540, 40:1040, :3] = (ramp * 0.04)[None, :, None]
    reg['dark_neutral_gradient'] = (1470, 1540, 40, 1040, 'ramp')
    # emissive patches (> 1.0; excluded from the LUT error)
    for i, (name, ex) in enumerate(EMISSIVE):
        x0 = 40 + i * 126
        cv[1600:1800, x0:x0 + 116, :3] = K.C[name] * ex
        reg['%s@%gx' % (name, ex)] = (1600, 1800, x0, x0 + 116, 'emissive')
    return cv, reg


def _label_u8(img, text, x, y, scale=0.9):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, (235, 228, 220), 1, cv2.LINE_AA)


def _u8(srgb01):
    return np.clip(np.round(np.asarray(srgb01) * 255.0), 0, 255).astype(np.uint8)


def _patch_med(img, r, inset=0.2):
    y0, y1, x0, x1 = r[:4]
    dy, dx = int((y1 - y0) * inset), int((x1 - x0) * inset)
    return np.median(img[y0 + dy:y1 - dy, x0 + dx:x1 - dx].reshape(-1, 3), 0)


def chart(look, out=None):
    """Write the before / after chart pair and its numbers -> dict."""
    out = out or OUT
    os.makedirs(out, exist_ok=True)
    cv, reg = chart_canvas()
    before = _u8(display(cv[..., :3]))
    after = _u8(display(grade_rgb(cv[..., :3], look)))
    res = dict(look=look, swatches={}, skin={})
    for name, r in reg.items():
        if r[4] in ('swatch', 'emissive'):
            b, a = _patch_med(before, r), _patch_med(after, r)
            res['swatches'][name] = dict(before=[int(v) for v in b], after=[int(v) for v in a],
                                         dE=round(float(np.linalg.norm(oklab_u8(a) - oklab_u8(b)) * 100), 2))
        elif r[4] == 'skin':
            b, a = _patch_med(before, r), _patch_med(after, r)
            Lb, Cb, hb = _lch(oklab_u8(b))
            La, Ca, ha = _lch(oklab_u8(a))
            res['skin'][name] = dict(before=[int(v) for v in b], after=[int(v) for v in a],
                                     dhue_oklab=round(float(_dhue(ha, hb)), 2), dL=round(float((La - Lb) * 100), 2),
                                     chroma_ratio=round(float(Ca / max(Cb, 1e-6)), 3),
                                     hsv_hue_before=round(hsv_hue_deg(b[None])[0], 1),
                                     hsv_hue_after=round(hsv_hue_deg(a[None])[0], 1))
    res['footage_grade_skin'] = footage_skin_check(look)
    res['FLAME@1x_dE'] = res['swatches']['FLAME@1x']['dE']
    res['RED@1x_dE'] = res['swatches']['RED@1x']['dE']
    res['skin_max_dhue'] = max(abs(v['dhue_oklab']) for v in res['skin'].values())
    res['skin_max_dL'] = max(v['dL'] for v in res['skin'].values())
    res['skin_chroma_range'] = [min(v['chroma_ratio'] for v in res['skin'].values()),
                                max(v['chroma_ratio'] for v in res['skin'].values())]
    for img, tag in ((before, 'before'), (after, 'after')):
        im = img.copy()
        _label_u8(im, '%s  %s' % (look, tag), 40, 40, 1.0)
        _label_u8(im, 'grey ramp 0..1.6', 44, 200, 0.7)
        _label_u8(im, 'swatches 0.5x / 1x / 2x', 44, 750, 0.7)
        _label_u8(im, 'skin: light / Jawad suit / Jawad street / deep', 44, 1070, 0.7)
        _label_u8(im, 'dark warm + neutral gradients', 44, 1332, 0.7)
        _label_u8(im, 'emissive (FLAME 3/6/12, RED 4/9, GOLD 4/10, IVORY 1.6)', 44, 1590, 0.7)
        if tag == 'after':
            _label_u8(im, 'FLAME dE %.2f  RED dE %.2f  skin dhue <= %.1f deg  dL <= %+.2f' % (
                res['FLAME@1x_dE'], res['RED@1x_dE'], res['skin_max_dhue'], res['skin_max_dL']), 44, 1860, 0.75)
        cv2.imwrite(os.path.join(out, 'chart_%s_%s.png' % (look, tag)), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
    res['before_png'] = os.path.join(out, 'chart_%s_before.png' % look)
    res['after_png'] = os.path.join(out, 'chart_%s_after.png' % look)
    with open(os.path.join(out, 'chart_%s.json' % look), 'w') as f:
        json.dump(res, f, indent=1)
    return res


# =============================================================================================== LUTs
def _lut_grid(n=33):
    g = np.linspace(0.0, 1.0, n, dtype=np.float64)
    bb, gg, rr = np.meshgrid(g, g, g, indexing='ij')             # flattened C-order: red fastest
    return np.stack([rr, gg, bb], -1).reshape(n * n, n, 3)


def lut_values(look, n=33):
    """(n^3, 3) sRGB output of the look for the sRGB grid (red index fastest)."""
    grid = _lut_grid(n)
    lin = K.to_lin(grid.astype(np.float32))
    out = display(grade_rgb(lin, look))
    return out.reshape(-1, 3)


def _write_cube(path, title, vals, n=33):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('TITLE "%s"\n' % title)
        f.write('# jawad_grade.py: sRGB in -> %s look (colour part of G.finish + toolkit shoulder) -> sRGB out\n'
                % title)
        f.write('# no spatial ops (bloom, halation, vignette, edge chroma, grain): previews / NLE / external clips\n')
        f.write('LUT_3D_SIZE %d\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n' % n)
        f.write('\n'.join('%.6f %.6f %.6f' % tuple(v) for v in np.clip(vals, 0, 1)))
        f.write('\n')
    return path


def write_lut(look, n=33):
    return _write_cube(os.path.join(LUT_DIR, '%s_%d.cube' % (look, n)), 'jawad %s' % look, lut_values(look, n), n)


def write_identity(path, n=33):
    return _write_cube(path, 'identity', _lut_grid(n).reshape(-1, 3), n)


def read_cube(path):
    n, vals = None, []
    with open(path) as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith('LUT_3D_SIZE'):
                n = int(s.split()[1])
            elif s[0].isdigit() or s[0] in '-.':
                vals.append([float(v) for v in s.split()])
    return n, np.asarray(vals, np.float64)


def _ffmpeg_lut(src_png, cube, dst_png, deep=True):
    """Apply a .cube with ffmpeg (tetrahedral). deep=True runs lut3d in 16 bit and writes a 16-bit PNG (exact
    LUT content; ffmpeg's 8-bit lut3d path truncates, ~-0.25 code on average) -> float RGB in 0..255."""
    if deep:                                    # exact 16-bit input (v * 257), so no swscale conversion happens
        src16 = src_png[:-4] + '_16.png'
        if not os.path.exists(src16) or os.path.getmtime(src16) < os.path.getmtime(src_png):
            cv2.imwrite(src16, cv2.imread(src_png, cv2.IMREAD_COLOR).astype(np.uint16) * 257)
        src_png = src16
    vf = 'lut3d=file=%s:interp=tetrahedral' % cube
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src_png, '-vf', vf, '-pix_fmt', 'rgb48be' if deep else 'rgb24',
           dst_png]
    subprocess.run(cmd, check=True)
    im = cv2.imread(dst_png, cv2.IMREAD_UNCHANGED)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float64)
    return im * (255.0 / 65535.0) if im.dtype == np.float64 and deep else im


def _oklab_f(rgb255):
    """float sRGB 0..255 (..., 3) -> OKLab."""
    return K._oklab(K.to_lin(np.clip(np.asarray(rgb255, np.float32) / 255.0, 0, 1)).astype(np.float64))


def lut_check(look, work=None):
    """Identity orientation proof + the look's .cube vs the in-process grade on the chart, both through ffmpeg
    lut3d (tetrahedral). Errors in OKLab x 100 on non-emissive pixels: 'deep' = lut3d in 16 bit vs the float
    in-process grade (the LUT itself), 'rgb24' = ffmpeg's 8-bit path vs the rounded in-process grade."""
    work = work or os.path.join(OUT, 'lutcheck')
    os.makedirs(work, exist_ok=True)
    cv, reg = chart_canvas()
    src = _u8(K.to_srgb(np.clip(cv[..., :3], 0, 1)))            # no shoulder: the LUT sees plain sRGB
    src_png = os.path.join(work, 'chart_src.png')
    cv2.imwrite(src_png, cv2.cvtColor(src, cv2.COLOR_RGB2BGR))
    idc = os.path.join(work, 'identity_33.cube')
    write_identity(idc)
    ident8 = _ffmpeg_lut(src_png, idc, os.path.join(work, 'chart_identity.png'), deep=False)
    ident16 = _ffmpeg_lut(src_png, idc, os.path.join(work, 'chart_identity16.png'), deep=True)
    cube = os.path.join(LUT_DIR, '%s_33.cube' % look)
    via16 = _ffmpeg_lut(src_png, cube, os.path.join(work, 'chart_%s_lut16.png' % look), deep=True)
    via8 = _ffmpeg_lut(src_png, cube, os.path.join(work, 'chart_%s_lut.png' % look), deep=False)
    ref = display(grade_rgb(K.to_lin(src.astype(np.float32) / 255.0), look)).astype(np.float64) * 255.0
    mask = np.ones(src.shape[:2], bool)
    for r in reg.values():
        if r[4] == 'emissive':
            mask[r[0]:r[1], r[2]:r[3]] = False
    d16 = np.linalg.norm(_oklab_f(via16[mask]) - _oklab_f(ref[mask]), axis=-1) * 100
    d8 = np.linalg.norm(_oklab_f(via8[mask]) - _oklab_f(np.round(ref[mask])), axis=-1) * 100
    code16 = np.abs(via16[mask] - ref[mask]).max(-1)
    return dict(identity_max_code_rgb24=float(np.abs(ident8 - src).max()),
                identity_max_code_16bit=round(float(np.abs(ident16 - src).max()), 3),
                mean_dE=round(float(d16.mean()), 3), max_dE=round(float(d16.max()), 3),
                p99_dE=round(float(np.percentile(d16, 99)), 3), max_code=round(float(code16.max()), 2),
                rgb24_mean_dE=round(float(d8.mean()), 3), rgb24_max_dE=round(float(d8.max()), 3),
                rgb24_mean_code=round(float((via8[mask] - np.round(ref[mask])).mean()), 3), cube=cube)


# =============================================================================================== test scene
def _faces():
    if FACES_TOOLS not in sys.path:
        sys.path.append(FACES_TOOLS)
    import faces as FA                                              # face-compositor's library (read-only use)
    return FA


@functools.lru_cache(maxsize=2)
def _subject(name='street_smirk', width=760):
    """Jawad's cut-out with the face-compositor's rim light (falls back to the plain cut-out)."""
    try:
        FA = _faces()
        plain = FA.load(name, size=width)
        hero = FA.rim_light(plain, FA.depth(name, plain.shape[:2]))
        return plain, hero, FA.anchor_at(plain, hero, (plain.shape[1] / 2, plain.shape[0]))
    except Exception as e:                                          # pragma: no cover - fallback path
        print('[jawad_grade] faces.py unavailable (%s): plain cut-out' % e, file=sys.stderr)
        spr = K.load_image(os.path.join(CUTOUTS, name + '.png'), size=width)
        return spr, spr, (0.5, 1.0)


@functools.lru_cache(maxsize=6)
def _scene_assets(look):
    win = ui.app_window(w=640, h=430, look=look, title='grade_v03.cube', header='Color grade',
                        sub='%s  1080 x 1920  30 fps' % look, sidebar=False)
    return dict(title=J.HouseTitle('HAR FRAME', 'ek kahani', caps_px=84, key_px=220), win=win,
                sparks=J.embers(90, seed=4))


SCENE_ROWS = (('Tone curve', 0.6), ('Skin protect', 0.9), ('Film grain', 1.2))


def scene(look, t, subject=True):
    """The shared test frame: the look's world + house title + glass UI card + Jawad cut-out + sparks."""
    A = _scene_assets(look)
    u = K.EASE['inout_sine'](min(1.0, t / 3.0))
    cam = K.Cam.orbit((0, 0, 0), 1500 - 60 * u, yaw=K.lerp(2.0, -1.5, u), pitch=K.lerp(-1.0, 0.6, u), aperture=26)
    cv = K.background(look, t, cam)
    A['title'].draw(cv, t + 1.2, K.CX, 330, t0=0.0)
    win = A['win']
    f = win.face_at(sweep=(0.1 + t * 0.4) % 1)
    x, y, sw, sh = win.meta['slot']
    for i, (label, tick) in enumerate(SCENE_ROWS):
        win.put(f, ui.check_row(label, w=sw, t=t + 1.0 - tick, look=look), x - ui.ROW_PAD, y + i * 100 - ui.ROW_PAD)
    win.plane(cv, cam, (-110, -150, -30), 640, rot=(5, -8, 0.6), face=f)
    if subject:
        plain, hero, anc = _subject()
        K.draw(cv, hero, K.CX + 170, K.H + 4, anchor=anc)
    A['sparks'].draw(cv, cam, t)
    J.signature(cv, 250, 1585)
    return cv


def render_frame(look, t, **kw):
    cv = scene(look, t)
    finish(cv, look, t, **kw)
    return K.to_srgb8(cv, t)


# =============================================================================================== verify
def _ffprobe_stats(mp4):
    keys = ['YMIN', 'YLOW', 'YAVG', 'YHIGH', 'YMAX', 'SATAVG', 'HUEMED']
    ent = ','.join('lavfi.signalstats.' + k for k in keys)
    p = subprocess.run(['ffprobe', '-v', 'error', '-f', 'lavfi', '-i', 'movie=%s,signalstats' % mp4,
                        '-show_entries', 'frame_tags=' + ent, '-of', 'csv=p=0'], capture_output=True, text=True,
                       check=True)
    rows = [[float(v) for v in ln.split(',') if v != ''] for ln in p.stdout.strip().splitlines() if ln.strip()]
    rows = [r for r in rows if len(r) == len(keys)]
    return keys, np.asarray(rows, np.float64), p.stdout


def _frames(mp4, fps):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', 'fps=%g' % fps, '-f', 'rawvideo',
                        '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height', '-of', 'csv=p=0', mp4], capture_output=True, text=True, check=True)
    w, h = [int(v) for v in probe.stdout.strip().split(',')[:2]]
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w, 3)


def _luma(rgb_u8):
    return cv2.cvtColor(np.ascontiguousarray(rgb_u8), cv2.COLOR_RGB2YCrCb)[..., 0]


def find_dark_gradient(rgb_u8, size=300):
    """(y, x) of the size x size window holding the darkest smooth gradient of the world: not clipped to black
    (5th percentile >= 6 full-range codes), mean 8-60, the widest ramp, no type / sparks / UI edges."""
    Y = _luma(rgb_u8).astype(np.float32)
    blur = cv2.GaussianBlur(Y, (0, 0), 12)
    hf = np.abs(Y - cv2.GaussianBlur(Y, (0, 0), 2.0))
    best, pos = -1.0, None
    for y in range(0, Y.shape[0] - size + 1, 40):
        for x in range(0, Y.shape[1] - size + 1, 40):
            b = blur[y:y + size, x:x + size]
            m = float(b.mean())
            if m > 60 or m < 8 or float(np.percentile(Y[y:y + size, x:x + size], 5)) < 6:
                continue
            busy = float(np.percentile(hf[y:y + size, x:x + size], 99))
            rng = float(b.max() - b.min())
            score = rng / (1.0 + busy) / (1.0 + m / 40.0)
            if score > best:
                best, pos = score, (y, x)
    return pos if pos is not None else (Y.shape[0] - size, 0)


def banding(y_patch):
    """Luma banding numbers of a uint8 patch: distinct levels (> 0.5 % of px), share of perfectly flat 8x8
    blocks (x264 zero-residual blocks = contour bands) and of pixels whose 5x5 neighbourhood is constant."""
    p = np.asarray(y_patch, np.float32)
    h, w = p.shape
    blocks = p[:h // 8 * 8, :w // 8 * 8].reshape(h // 8, 8, w // 8, 8).std(axis=(1, 3))
    vals, cnt = np.unique(p.astype(np.int32), return_counts=True)
    mn = cv2.erode(p, np.ones((5, 5), np.uint8))
    mx = cv2.dilate(p, np.ones((5, 5), np.uint8))
    return dict(levels=int((cnt > p.size * 0.005).sum()), flat8=round(float((blocks == 0).mean()), 4),
                flat5px=round(float((mx[2:-2, 2:-2] == mn[2:-2, 2:-2]).mean()), 4),
                range=round(float(np.percentile(p, 99) - np.percentile(p, 1)), 1), mean=round(float(p.mean()), 2),
                std=round(float(p.std()), 2))


def _yplane(mp4, fps=1):
    """Limited-range Y planes (uint8) at `fps`."""
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height', '-of', 'csv=p=0', mp4], capture_output=True, text=True, check=True)
    w, h = [int(v) for v in probe.stdout.strip().split(',')[:2]]
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp4, '-vf', 'fps=%g,extractplanes=y' % fps, '-f', 'rawvideo',
                        '-pix_fmt', 'gray', '-'], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w)


def _reencode(src, dst, mode):
    if mode == 'crf23':
        args = ['-crf', '23', '-preset', 'medium']
    else:
        args = ['-b:v', '3.5M', '-maxrate', '4M', '-bufsize', '8M', '-preset', 'medium']
    subprocess.run(['nice', '-n', '10', 'ffmpeg', '-v', 'error', '-y', '-i', src, '-c:v', 'libx264'] + args +
                   ['-pix_fmt', 'yuv420p', '-threads', '2', dst], check=True)
    return dst


def kmeans_fingerprint(frames, k=5):
    px = np.concatenate([cv2.resize(f, (135, 240), interpolation=cv2.INTER_AREA).reshape(-1, 3) for f in frames])
    px = px.astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, lab, cen = cv2.kmeans(px, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    share = np.bincount(lab.ravel(), minlength=k) / lab.size
    order = np.argsort(-share)
    return [dict(hex='#%02X%02X%02X' % tuple(int(round(v)) for v in cen[i]), share=round(float(share[i]), 3))
            for i in order]


def _faces_in(rgb_u8):
    fc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    g = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2GRAY)
    g = cv2.equalizeHist(g)
    f = fc.detectMultiScale(g, 1.1, 5, minSize=(110, 110))
    return [tuple(int(v) for v in r) for r in f]


def skin_stats(rgb_u8, box):
    """Median skin of a face box (cheek / forehead band, skin-like pixels): HSV hue, sat, OKLab L / C / h."""
    x, y, w, h = box
    roi = rgb_u8[y + int(.25 * h):y + int(.62 * h), x + int(.2 * w):x + int(.8 * w)].reshape(-1, 3)
    hsv = cv2.cvtColor(roi.reshape(-1, 1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)
    m = (hsv[:, 1] > 30) & (hsv[:, 2] > 50) & ((hsv[:, 0] <= 25) | (hsv[:, 0] >= 172))
    if m.sum() < 50:
        return None
    med = np.median(roi[m], 0)
    L, Cc, hh = _lch(oklab_u8(med))
    hue, sat = hsv_hue_deg(roi[m])
    return dict(px=int(m.sum()), median_rgb=[int(v) for v in med], hsv_hue=round(hue, 1), hsv_sat=round(sat, 3),
                oklab_L=round(float(L * 100), 1), oklab_C=round(float(Cc * 100), 2), oklab_h=round(float(hh), 1))


def verify(mp4, look, out=None, skin_ref=None):
    """Measure a rendered master -> dict (also written to <out>/verify.json)."""
    out = out or os.path.join(os.path.dirname(os.path.abspath(mp4)),
                              'qa_' + os.path.splitext(os.path.basename(mp4))[0])
    os.makedirs(out, exist_ok=True)
    res = dict(mp4=mp4, look=look)
    keys, S, raw = _ffprobe_stats(mp4)
    with open(os.path.join(out, 'stats.csv'), 'w') as f:
        f.write(','.join(keys) + '\n' + raw)
    rng = {k: [round(float(S[:, i].min()), 1), round(float(S[:, i].mean()), 1), round(float(S[:, i].max()), 1)]
           for i, k in enumerate(keys)}
    ymin = S[:, 0]
    jumps = [int(i + 1) for i in np.flatnonzero(np.diff(ymin) > 6)]
    res['signalstats_min_mean_max'] = rng
    res['frames'] = int(S.shape[0])
    res['ymin_jumps_gt6'] = jumps
    yp = _yplane(mp4, 1)
    res['luma_1fps'] = dict(p1=[int(np.percentile(y, 1)) for y in yp], p10=[int(np.percentile(y, 10)) for y in yp],
                            below16_share=[round(float((y < 16).mean()), 5) for y in yp])
    # hue budget at 1 fps
    fr1 = _frames(mp4, 1)
    hb = [hue_budget(f) for f in fr1]
    res['hue_budget_1fps'] = hb
    ro = [h['red_orange'] for h in hb if h['red_orange'] is not None]
    top = [h['top5_red_orange'] for h in hb if h['top5_red_orange'] is not None]
    vio = [h['violet'] for h in hb if h['violet'] is not None]
    res['hue_budget_summary'] = dict(red_orange_mean=round(float(np.mean(ro)), 3) if ro else None,
                                     red_orange_min=round(float(np.min(ro)), 3) if ro else None,
                                     top5_red_orange_min=round(float(np.min(top)), 3) if top else None,
                                     violet_max=round(float(np.max(vio)), 3) if vio else None, rule=BUDGET.get(look))
    # skin: faces at 1 fps (Haar), vectorscope of the first face crop
    sk = []
    for i, f in enumerate(fr1):
        fb = _faces_in(f)
        for b in sorted(fb, key=lambda r: -r[2] * r[3])[:1]:              # the largest face only
            s = skin_stats(f, b)
            if s:
                s['t'] = i + 0.5
                sk.append(s)
                if len(sk) == 1:
                    x, y, w, h = b
                    fp = os.path.join(out, 'face.png')
                    cv2.imwrite(fp, cv2.cvtColor(f[y:y + h, x:x + w], cv2.COLOR_RGB2BGR))
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', fp, '-vf',
                                    'vectorscope=mode=color3:graticule=color,scale=512:512',
                                    os.path.join(out, 'vs.png')], check=False)
    res['skin'] = sk
    if skin_ref is not None and sk:
        res['skin_vs_ref'] = dict(ref=skin_ref, dhue_hsv=round(float(np.median([s['hsv_hue'] for s in sk]) -
                                                                     skin_ref['hsv_hue']), 1),
                                  dL=round(float(np.median([s['oklab_L'] for s in sk]) - skin_ref['oklab_L']), 1),
                                  dhue_oklab=round(float(_dhue(np.median([s['oklab_h'] for s in sk]),
                                                               skin_ref['oklab_h'])), 1))
    # banding after the Instagram-like re-encodes (CRF 23 and 3.5 Mbit/s x264), darkest smooth world gradient
    mid = fr1[len(fr1) // 2]
    y, x = find_dark_gradient(mid)
    res['banding_patch_yx'] = [int(y), int(x)]
    band = {}
    for tag, src in (('master', mp4), ('crf23', _reencode(mp4, os.path.join(out, 'ig_crf23.mp4'), 'crf23')),
                     ('ig_3m5', _reencode(mp4, os.path.join(out, 'ig_3m5.mp4'), '3m5'))):
        frs = _frames(src, 1)
        f = frs[len(frs) // 2]
        patch = _luma(f)[y:y + 300, x:x + 300]
        band[tag] = banding(patch)
        st = np.clip((patch.astype(np.float32) - np.percentile(patch, 1)) * 255.0 /
                     max(1.0, float(np.percentile(patch, 99) - np.percentile(patch, 1))), 0, 255).astype(np.uint8)
        cv2.imwrite(os.path.join(out, 'band_%s.png' % tag), cv2.resize(st, (600, 600), interpolation=cv2.INTER_NEAREST))
    res['banding'] = band
    # k-means fingerprint at 2 fps
    fr2 = _frames(mp4, 2)
    res['fingerprint'] = kmeans_fingerprint(fr2)
    with open(os.path.join(out, 'verify.json'), 'w') as f:
        json.dump(res, f, indent=1)
    res['dir'] = out
    return res


# =============================================================================================== clip + sheet
def render_clip(look, dur=3.0, out=None, **kw):
    out = out or os.path.join(OUT, look)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, '%s_test.mp4' % look)
    n = int(round(dur * K.FPS))
    t0 = time.perf_counter()
    with K.FFWriter(path, crf=14, preset='medium', extra=('-threads', '2')) as fw:
        for i in range(n):
            fw.write(render_frame(look, i / K.FPS, **kw))
    return path, (time.perf_counter() - t0) / n


def sheet(t=1.6, out=None):
    """Five-look comparison sheet: the same test frame under each look + thumbnails + k-means fingerprints."""
    out = out or OUT
    os.makedirs(out, exist_ok=True)
    cw, ch, pad = 432, 768, 16
    tw, th = 108, 192
    H = 64 + ch + 20 + th + 20 + 70 + 210
    Wd = pad + len(ALL_LOOKS) * (cw + pad)
    sh = np.full((H, Wd, 3), 14, np.uint8)
    _label_u8(sh, 'jawad_grade: the same test frame under the five looks (t = %.1f s)' % t, pad, 40, 1.0)
    info = {}
    for i, look in enumerate(ALL_LOOKS):
        x0 = pad + i * (cw + pad)
        t0 = time.perf_counter()
        fr = render_frame(look, t)
        dt = time.perf_counter() - t0
        cv2.imwrite(os.path.join(out, 'frame_%s.png' % look), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
        sh[64:64 + ch, x0:x0 + cw] = cv2.resize(fr, (cw, ch), interpolation=cv2.INTER_AREA)
        y = 64 + ch + 20
        sh[y:y + th, x0:x0 + tw] = cv2.resize(fr, (tw, th), interpolation=cv2.INTER_AREA)
        fp = kmeans_fingerprint([fr])
        hb = hue_budget(fr)
        Y = _luma(fr)
        yl = 16 + Y.astype(np.float64) * 219 / 255
        info[look] = dict(fingerprint=fp, hue=hb, Ymin=round(float(yl.min()), 1), Yavg=round(float(yl.mean()), 1),
                          render_s=round(dt, 2))
        bx = x0 + tw + 12
        acc = 0
        for c in fp:
            wseg = int(round(c['share'] * (cw - tw - 12)))
            rgb = tuple(int(c['hex'][j:j + 2], 16) for j in (1, 3, 5))
            sh[y:y + th, bx + acc:bx + acc + wseg] = rgb
            acc += wseg
        y += th + 20
        _label_u8(sh, look, x0, y + 24, 0.9)
        _label_u8(sh, 'Yavg %.0f  Ymin %.0f' % (info[look]['Yavg'], info[look]['Ymin']), x0, y + 56, 0.6)
        ro = hb['red_orange']
        _label_u8(sh, 'red-orange %s  top5 %s' % ('%.0f%%' % (ro * 100) if ro is not None else '-',
                                                  '%.0f%%' % (hb['top5_red_orange'] * 100) if ro is not None else '-'),
                  x0, y + 84, 0.6)
        _label_u8(sh, 'violet %s' % ('%.0f%%' % (hb['violet'] * 100) if ro is not None else '-'), x0, y + 112, 0.6)
    p = os.path.join(out, 'looks_sheet.jpg')
    cv2.imwrite(p, cv2.cvtColor(sh, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # thumbnail strip (feed-size check): the five frames at 135x240 side by side
    strip = np.concatenate([cv2.resize(cv2.cvtColor(cv2.imread(os.path.join(out, 'frame_%s.png' % lk)),
                                                    cv2.COLOR_BGR2RGB), (135, 240), interpolation=cv2.INTER_AREA)
                            for lk in ALL_LOOKS], 1)
    cv2.imwrite(os.path.join(out, 'looks_thumbs.png'), cv2.cvtColor(strip, cv2.COLOR_RGB2BGR))
    info['_thumb_distance'] = thumb_distance({lk: cv2.cvtColor(cv2.imread(os.path.join(out, 'frame_%s.png' % lk)),
                                                               cv2.COLOR_BGR2RGB) for lk in ALL_LOOKS})
    with open(os.path.join(out, 'looks_sheet.json'), 'w') as f:
        json.dump(info, f, indent=1)
    return p, info


def thumb_distance(frames, size=(27, 48)):
    """Pairwise mean OKLab distance (x 100) of feed-thumbnail-sized versions of frames {look: uint8 RGB}:
    how far apart two looks read at a glance (same layout, so only the grade / world differ)."""
    labs = {k: oklab_u8(cv2.resize(v, size, interpolation=cv2.INTER_AREA)) for k, v in frames.items()}
    ks = list(labs)
    return {'%s|%s' % (a, b): round(float(np.linalg.norm(labs[a] - labs[b], axis=-1).mean() * 100), 2)
            for i, a in enumerate(ks) for b in ks[i + 1:]}


# =============================================================================================== self-test
def selftest():
    fails = []

    def check(ok, msg):
        print(('  ok   ' if ok else '  FAIL ') + msg)
        if not ok:
            fails.append(msg)

    print('jawad_grade self-test')
    # registration
    for lk in ALL_LOOKS:
        check(lk in K.LOOKS and lk in K._BG_LOOKS and lk in ui.LOOKS and lk in F.GRADES and lk in J.LOOK_NAMES
              and lk in FIN, 'look %s registered everywhere' % lk)
    before = {lk: id(K.LOOKS[lk]) for lk in NEW_LOOKS}
    register()
    check(all(id(K.LOOKS[lk]) == before[lk] for lk in NEW_LOOKS), 'register() is idempotent')
    for lk in KIT_LOOKS:
        check(repr(sorted(K.LOOKS[lk].items())) == _KIT_SNAPSHOT[lk] and
              repr(sorted(F.GRADES[lk].items())) == _KIT_GRADE_SNAPSHOT[lk] and
              repr(K._BG_LOOKS[lk]) == _KIT_BG_SNAPSHOT[lk], 'kit look %s untouched' % lk)
    for lk in ('neon', 'amber', 'airy'):
        check(lk not in FIN, 'old client look %s not graded here' % lk)
    # curve sanity
    for lk in ALL_LOOKS:
        Q = _params(lk)
        y = tone_curve(np.geomspace(1e-6, 8, 2000), lk)
        check(bool(np.all(np.diff(y) > 0)) and np.isfinite(Q['gain']).all(), '%s tone curve monotonic' % lk)
        s0 = (math.log2(tone_curve(0.18 * 2 ** 0.01, lk) / 0.18) -
              math.log2(tone_curve(0.18 * 2 ** -0.01, lk) / 0.18)) / 0.02
        check(1.08 <= s0 <= 1.36, '%s slope at 0.18 = %.3f (1.1-1.35)' % (lk, s0))
    # black never lifted (finish, grain off)
    for lk in ALL_LOOKS:
        cv = np.zeros((K.H, K.W, 4), np.float32)
        cv[..., 3] = 1
        finish(cv, lk, 0.0, grain=0.0)
        mx = int(K.to_srgb8(cv, 0.0, dither=False).max())
        check(mx <= 4, '%s: black frame stays black after finish (max code %d)' % (lk, mx))
    # chart numbers
    charts = {}
    for lk in ALL_LOOKS:
        r = chart(lk)
        charts[lk] = r
        check(r['FLAME@1x_dE'] <= 3.0 and r['RED@1x_dE'] <= 3.0,
              '%s: FLAME dE %.2f, RED dE %.2f (<= 3)' % (lk, r['FLAME@1x_dE'], r['RED@1x_dE']))
        check(r['skin_max_dhue'] <= 4.0, '%s: skin hue shift %.2f deg (<= 4)' % (lk, r['skin_max_dhue']))
        check(r['skin_max_dL'] <= 1.5, '%s: skin not lighter (dL max %+.2f <= 1.5)' % (lk, r['skin_max_dL']))
        lo, hi = r['skin_chroma_range']
        check(0.85 <= lo and hi <= 1.12, '%s: skin chroma ratio %.3f..%.3f (no grey, no orange)' % (lk, lo, hi))
    for lk in NEW_LOOKS:
        fs = footage_skin_check(lk)
        mh = max(abs(v[1]) for v in fs)
        mc = max(v[2] for v in fs)
        check(mh <= 4.0 and mc <= 1.12 and min(v[2] for v in fs) >= 0.88,
              '%s: F.GRADES skin hue <= %.1f deg, chroma ratio <= %.2f' % (lk, mh, mc))
    # LUTs through ffmpeg
    for lk in ALL_LOOKS:
        cube = os.path.join(LUT_DIR, '%s_33.cube' % lk)
        if not os.path.exists(cube):
            check(False, '%s: %s missing (python3 jawad_grade.py lut all)' % (lk, cube))
            continue
        n, vals = read_cube(cube)
        fresh = lut_values(lk)
        check(n == 33 and vals.shape == (33 ** 3, 3) and float(np.abs(vals - fresh).max()) < 2e-6,
              '%s: cube header + values current' % lk)
        r = lut_check(lk)
        check(r['identity_max_code_rgb24'] <= 1 and r['identity_max_code_16bit'] <= 0.5,
              'identity cube through ffmpeg: max %.0f code (rgb24), %.3f (16 bit)' % (
                  r['identity_max_code_rgb24'], r['identity_max_code_16bit']))
        check(r['mean_dE'] < 1.0 and r['max_dE'] < 2.5,
              '%s: LUT vs in-process mean dE %.3f (< 1), max %.3f (< 2.5)' % (lk, r['mean_dE'], r['max_dE']))
    # tx_finish == finish with jawad_tx's push kwargs; K.post restored
    try:
        import jawad_tx as X
        cv0 = scene('dusk', 0.5)
        a = tx_finish(cv0.copy(), 0.5, 'dusk', cuts=(0.5,), grain=0.0)
        p = X.push_at(0.5, (0.5,))
        b = finish(cv0.copy(), 'dusk', 0.5, grain=0.0, exposure=K.LOOKS['dusk'].get('exposure', 0.0) + 1.4 * p,
                   bloom=K.LOOKS['dusk']['bloom'] * (1 + 0.9 * p))
        check(float(np.abs(a - b).max()) < 1e-5 and K.post is not None and
              getattr(K.post, '_jawad_orig', None) is not None,
              'tx_finish == finish with the jawad_tx push (max diff %.2e), K.post restored'
              % float(np.abs(a - b).max()))
    except ImportError:
        print('       jawad_tx not present: tx_finish not tested')
    # finish timing on a real frame
    for lk in ALL_LOOKS:
        cv0 = scene(lk, 1.0)
        c1 = cv0.copy()
        K.post(c1, lk, 1.0)
        c1 = cv0.copy()
        t0 = time.perf_counter()
        K.post(c1, lk, 1.0)
        tp = (time.perf_counter() - t0) * 1e3
        c2 = cv0.copy()
        finish(c2, lk, 1.0)
        c2 = cv0.copy()
        t0 = time.perf_counter()
        finish(c2, lk, 1.0)
        tf = (time.perf_counter() - t0) * 1e3
        check(np.isfinite(c2).all() and float(c2[..., 3].min()) == 1.0, '%s: finish output finite, alpha 1' % lk)
        print('       %s: K.post %.0f ms, G.finish %.0f ms (+%.0f ms)' % (lk, tp, tf, tf - tp))
        check(tf - tp < 400, '%s: finish overhead %.0f ms (< 400 on a loaded box)' % (lk, tf - tp))
    print('self-test %s (%d failures)' % ('PASSED' if not fails else 'FAILED', len(fails)))
    return not fails


def _main(argv):
    if not argv or argv[0] in ('-h', '--help', 'help'):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    looks = (lambda a: list(ALL_LOOKS) if (not a or a[0] == 'all') else [a[0]])
    if cmd in ('--selftest', 'selftest'):
        return 0 if selftest() else 1
    if cmd == 'lut':
        for lk in looks(rest):
            print(write_lut(lk))
        print(write_identity(os.path.join(LUT_DIR, 'identity_33.cube')))
        return 0
    if cmd == 'lutcheck':
        for lk in looks(rest):
            print(lk, json.dumps(lut_check(lk)))
        return 0
    if cmd == 'chart':
        for lk in looks(rest):
            r = chart(lk)
            print(lk, json.dumps({k: r[k] for k in ('FLAME@1x_dE', 'RED@1x_dE', 'skin_max_dhue', 'skin_max_dL',
                                                    'skin_chroma_range')}))
        return 0
    if cmd == 'sheet':
        p, info = sheet()
        print(p)
        print(json.dumps(info, indent=1))
        return 0
    if cmd == 'clip':
        dur = float(rest[1]) if len(rest) > 1 else 3.0
        for lk in looks(rest):
            p, spf = render_clip(lk, dur)
            print(p, '%.2f s/frame' % spf)
        return 0
    if cmd == 'verify':
        r = verify(rest[0], rest[1])
        print(json.dumps(r, indent=1))
        return 0
    print('unknown command %r' % cmd)
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(_main(sys.argv[1:]))
