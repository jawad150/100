"""pehle_wala_ad.py - the FRAME UNDER REVIEW of reel C26: the fictional "Ubaal Chai" ad (840 x 760 px canvas) at any
state (owner: motion-timeline-builder; pure functions, static sprites cached per process).

Geometry (BRIEF 5.2 + HANDOFF 3.1 / 4, screen px; ad-local = screen - (120, 468)):
    plate        NIGHT_1 -> NIGHT_0 + ember backlight (K.radial 900 EMBER x0.9 + 420 FLAME x0.6) at (515, 980)
    glass        pw_chai_glass (Blender, 13-frame yaw set, S3 scale 0.75), base centre (515, 1190), draw scale
                 0.604936 x z x e19, yaw(a) = 5 sin(2 pi a / 8.5333) deg, flow interpolation (Python floats only)
    contact shadow (515, 1192) 300 x 40 x0.6; floor reflection from the foot line y 1215 (x0.22, 140 px fade)
    steam        270 soft particles (90, x3 from v18) + 3 (+2) wisps from the rim opening (515, 768), faded out by
                 y 560 (480 from v18); IVORY, screen; v7 adds a 3 px FLAME cartoon outline at the 0.15 iso-line
    push         plate + glass + steam + reflection scale about (515, 990) by z(s) (graphics do not push);
                 v19 x1.2 scales the glass (and its steam / sparkles) about its base first
    logo         "UBAAL CHAI": FLAME ring roundel r 26 (5 px, x1.6) with three steam strokes + jw_caps_bold 38 px,
                 top-left (154, 504); x2 / x3 / x3.75 / x4.5 / x5.4 about the top-left, x -72 / -72 / +72
    garam        jw_key 100 px right-aligned at x 900, centre y 1150; parody (pw_parody_fun) 112 px from v10,
                 wobble +-4 deg at 2 Hz; cream variants EMBER -> PLUM (never FLAME on IVORY)
    graphics     NEW (GOLD 16-point burst, (810, 800), -12 deg), 50% OFF (EMBER ribbon 460 x 120, (720, 748), -8 deg),
                 CALL NOW (GOLD pill 470 x 100 + 2 px IVORY stroke, (540, 1060)), NEW! (EMBER burst, (260, 880), +10)
    v6 cream     IVORY x0.8 floods from pin 5's point (250, 1120) over 12 f; v13 the dark floods back from (150, 600)
    v11 shadows  EMBER x0.85 at (+14, +14), no blur, on every graphic (0.42 at v23, back at v24)
    v12 glitter  GOLD x1.5 discs in an 18 px band inset 10 px (320, twinkle 3 Hz); v14 36 px, 640 + 12 stars
    v16          letterbox 64 px bars (8 f out_cubic) + two anamorphic flares (<= 3x linear) on the rim / base line
    v5 / v21     ad saturation x1.45 + exposure +0.2 stop / +10 % saturation (ad rect only)

    import pehle_wala_ad as AD
    ad = AD.canvas(st, a, garam_k=1.0)      # (760, 840, 4) opaque linear premultiplied; st = pehle_wala_state.state(s)
    AD.prewarm()                            # every static sprite + the glass flow pairs (call once per worker)
    AD.thumb(v)                             # 80 x 46 thumbnail of version v (drawer rows), cached per version
"""
import functools
import math
import os

import jawad_kit                                   # noqa: F401  FIRST
from jawad_kit import K, T, ui, S3
import jawad_grade as G                           # noqa: F401  registers 'inferno'

import cv2
import numpy as np

import pehle_wala_state as S

LOOK = 'inferno'
AD_X, AD_Y, AD_W, AD_H = 120, 468, 840, 760
PIV = (515.0, 990.0)                               # product push pivot (screen)
BASE = (515.0, 1190.0)                             # glass base centre at push 1.0 (HANDOFF D4)
GLASS_K = 0.604936                                 # 0.453702 / 0.75 (HANDOFF D5)
RW = '/home/user/100/workspace/jawad_reels/pehle_wala'
GLASS = S3.Asset3D('pw_chai_glass', 'inferno', mode='yaw', root=os.path.join(RW, 'assets3d'), scale=0.75)
GLASS_ANCHOR = (480.0 / 960.0, 1096.8 / 1280.0)    # meta anchor (base centre) as a sprite fraction
C = K.C


def lin(name, k=1.0):
    return np.asarray(C[name], np.float32) * np.float32(k)


CREAM = lin('IVORY', 0.8)                          # the "white background" gag (linear IVORY x 0.8)


def ro(a):
    a = np.ascontiguousarray(a, np.float32)
    a.flags.writeable = False
    return a


def local(x, y):
    return x - AD_X, y - AD_Y


def push_pt(p, z, e19=1.0):
    """Screen point of the product layer at push 1 / v19 1 -> pushed screen point (v19 about the glass base)."""
    x = BASE[0] + (p[0] - BASE[0]) * e19
    y = BASE[1] + (p[1] - BASE[1]) * e19
    return PIV[0] + (x - PIV[0]) * z, PIV[1] + (y - PIV[1]) * z


# ============================================================================================ rasterising helpers
def poly_mask(pts, w, h, ss=4):
    """Anti-aliased coverage (h, w) of a polygon (px coords)."""
    m = np.zeros((h * ss, w * ss), np.uint8)
    p = np.round(np.asarray(pts, np.float64) * ss).astype(np.int32)
    cv2.fillPoly(m, [p], 255, cv2.LINE_8)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def star_pts(cx, cy, n, r_out, r_in, rot0=-90.0):
    out = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(rot0 + 180.0 * k / n)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def rgba(mask, col):
    s = np.zeros(mask.shape + (4,), np.float32)
    s[..., :3] = mask[..., None] * np.asarray(col, np.float32)[:3]
    s[..., 3] = mask
    return s


def over_ts(dst, ts, x, y, anchor=(0.5, 0.5)):
    """Draw a TextSprite into a sprite canvas (premultiplied)."""
    ts.draw(dst, x, y, anchor=anchor, snap=False)


@functools.lru_cache(maxsize=None)
def tstyle(name):
    """Local text styles (shared jawad_kit styles stay untouched)."""
    if name == 'garam_cream':                     # the keyword on the cream gag: EMBER -> PLUM, tight dark glow
        return T.style('jw_key', name='pw_garam_cream', fill=((0.0, '#C0201A'), (0.55, '#B3120E'), (1.0, '#4A0E08')),
                       stroke_color='#4A0E08', glow=0.35, glow_color=('EMBER', 0.5), glow_radii=(0.04, 0.12),
                       glow_weights=(0.4, 0.3), shadow=0.15)
    if name == 'parody':                          # the "fun" font in the brand gradient
        return T.style('jw_key', name='pw_parody', font='pw_parody_fun', px=112)
    if name == 'parody_cream':
        return T.style(tstyle('garam_cream'), name='pw_parody_cream', font='pw_parody_fun', px=112)
    if name == 'sil':                             # flat silhouette for the v11 hard shadows
        return T.style('flat', name='pw_sil', fill='EMBER', glow=0.0, shadow=0.0, stroke=0.0)
    if name == 'logo':                            # the fictional mark's wordmark (tighter halo than jw_caps_bold)
        return T.style('jw_caps_bold', name='pw_logo', glow=0.30, glow_radii=(0.06, 0.2), glow_weights=(0.5, 0.35),
                       shadow=0.4)
    if name == 'logo_ink':
        return T.style('jw_caps_bold', name='pw_logo_ink', fill='INK', glow=0.0, shadow=0.0)
    if name == 'ink':                             # INK text on GOLD (NEW, CALL NOW)
        return T.style('jw_caps_bold', name='pw_ink', fill='INK', glow=0.0, shadow=0.0)
    if name == 'ivory':                           # IVORY text on EMBER (50% OFF, NEW!)
        return T.style('jw_caps_bold', name='pw_ivory', fill='IVORY', fill_gain=1.05, glow=0.12,
                       glow_color=('IVORY', 0.3), glow_radii=(0.05,), glow_weights=(0.4,), shadow=0.35,
                       shadow_offset=(0.0, 0.035), shadow_blur=0.05)
    raise KeyError(name)


# ============================================================================================ static sprites
@functools.lru_cache(maxsize=1)
def plate():
    """The v1 plate: vertical NIGHT_1 -> NIGHT_0 gradient + the ember backlight at (515, 980)."""
    w, h = AD_W, AD_H
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    p = np.zeros((h, w, 4), np.float32)
    p[..., :3] = lin('NIGHT_1') * (1 - yy) + lin('NIGHT_0') * yy
    p[..., 3] = 1.0
    x, y = local(515, 980)
    K.draw(p, K.radial(900, lin('EMBER', 0.9)), x, y, mode='add')
    K.draw(p, K.radial(420, lin('FLAME', 0.6)), x, y, mode='add')
    p[..., 3] = 1.0
    return ro(p)


@functools.lru_cache(maxsize=1)
def round_mask():
    return ro(K.rrect_alpha(AD_W, AD_H, 18, 0))


@functools.lru_cache(maxsize=4)
def dist_map(ox, oy):
    yy, xx = np.mgrid[0:AD_H, 0:AD_W].astype(np.float32)
    return ro(np.sqrt((xx - ox) ** 2 + (yy - oy) ** 2))


CREAM_IN_O = local(250, 1120)                      # pin 5's marker tip: the paint-bucket click
CREAM_OUT_O = local(150, 600)                      # Mummy's marker: the dark floods back from her thread


def _rmax(o):
    return max(math.hypot(o[0] - x, o[1] - y) for x in (0, AD_W) for y in (0, AD_H)) + 40.0


def wave(o, u, x=None, y=None, soft=44.0):
    """Radial fill coverage from ad-local origin o at progress u (0..1): full map, or the value at (x, y)."""
    if u <= 0:
        return 0.0 if x is not None else None
    R = (_rmax(o) + soft) * u
    if x is not None:
        return float(np.clip((R - math.hypot(x - o[0], y - o[1])) / soft + 0.5, 0.0, 1.0))
    return np.clip((R - dist_map(*o)) / soft + 0.5, 0.0, 1.0)


def cream_at(st, x, y):
    """Cream amount (0..1) at an ad-local point."""
    a = wave(CREAM_IN_O, st['cream_in'], x, y)
    if a <= 0:
        return 0.0
    b = wave(CREAM_OUT_O, st['cream_out'], x, y)
    return a * (1.0 - b)


@functools.lru_cache(maxsize=1)
def contact_shadow():
    m = np.zeros((120, 400), np.float32)
    cv2.ellipse(m, (200, 60), (150, 20), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 9)
    s = np.zeros((120, 400, 4), np.float32)
    s[..., 3] = m
    return ro(s)


@functools.lru_cache(maxsize=1)
def reflection_ramp():
    """Vertical fade of the floor reflection (1 at the foot line -> 0 over 140 px)."""
    return np.clip(1.0 - np.arange(160, dtype=np.float32) / 140.0, 0.0, 1.0) ** 1.5


class Graphic:
    """A static 2D ad graphic: parts drawn about one anchor with scale k and rotation (deg, clockwise).
    parts = [(sprite or TextSprite, (ox, oy) offset at k = 1, anchor fraction, R (built resolution))]"""

    def __init__(self, parts):
        self.parts = parts

    def draw(self, cv, x, y, k=1.0, rot=0.0, opacity=1.0, mode='over'):
        if opacity <= 1e-4 or k <= 1e-3:
            return
        r = math.radians(rot)
        c, sn = math.cos(r), math.sin(r)
        for spr, (ox, oy), an, R in self.parts:
            px = x + (ox * c - oy * sn) * k
            py = y + (ox * sn + oy * c) * k
            if isinstance(spr, np.ndarray):
                K.draw(cv, spr, px, py, scale=k / R, rot=rot, opacity=opacity, anchor=an, mode=mode)
            else:
                spr.draw(cv, px, py, anchor=an, scale=k / R, rot=rot, opacity=opacity, snap=False)


def _roundel(R, ring_col, stroke_col, glow=True, sil=False):
    """The Ubaal Chai roundel at resolution R: ring r 26 (5 px) + three short steam strokes. Centred sprite."""
    r, wdt = 26.0 * R, 5.0 * R
    n = int(math.ceil(r + wdt + 4 * R))
    size = 2 * n + 1
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) - n
    d = np.sqrt(xx * xx + yy * yy)
    ring = np.clip(wdt / 2 + 0.5 - np.abs(d - r), 0, 1)
    strokes = np.zeros((size * 4, size * 4), np.uint8)
    for j, dx in enumerate((-9.0, 0.0, 9.0)):
        pts = []
        for k in range(24):
            u = k / 23.0
            yv = (11.0 - 22.0 * u) * R
            xv = (dx + 3.2 * math.sin(u * 2 * math.pi + j * 0.9)) * R
            pts.append(((xv + n) * 4, (yv + n - 1.5 * R) * 4))
        cv2.polylines(strokes, [np.round(np.array(pts)).astype(np.int32)], False, 255,
                      max(1, int(round(2.6 * R * 4))), cv2.LINE_AA)
    st = cv2.resize(strokes, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    if sil:
        m = np.maximum(ring, st)
        return ro(rgba(m, lin('EMBER')))
    spr = rgba(ring, ring_col) + rgba(st, stroke_col) * (1 - ring[..., None])
    spr[..., 3] = np.maximum(ring, st)
    if glow:
        spr = K.glow(spr, np.asarray(ring_col, np.float32) / 1.6 * 0.9, sigmas=(2.5 * R, 8 * R), strength=0.55,
                     weights=(1.0, 0.5))
    return ro(spr)


@functools.lru_cache(maxsize=None)
def logo(R, variant='brand'):
    """Logo Graphic at resolution R (1, 3, 6), anchored at its top-left; variants 'brand' | 'cream' | 'sil'."""
    if variant == 'brand':
        rd = _roundel(R, lin('FLAME', 1.6), lin('IVORY'))
        wm = T.render('UBAAL CHAI', tstyle('logo'), px=38 * R)
    elif variant == 'cream':
        rd = _roundel(R, lin('EMBER'), lin('INK'), glow=False)
        wm = T.render('UBAAL CHAI', tstyle('logo_ink'), px=38 * R)
    else:
        rd = _roundel(R, None, None, glow=False, sil=True)
        wm = T.render('UBAAL CHAI', tstyle('sil'), font='grotesk_bold', px=38 * R, tracking=0.05)
    return Graphic([(rd, (26.0, 26.0), (0.5, 0.5), R), (wm, (64.0, 26.0), (0.0, 0.5), R)])


LOGO_LEVELS = (1.0, 3.0, 6.0)


def logo_level(k):
    for R in LOGO_LEVELS:
        if k <= R + 1e-6:
            return R
    return LOGO_LEVELS[-1]


@functools.lru_cache(maxsize=None)
def garam(kind, R=1.0):
    """garam keyword TextSprites: 'brand' | 'cream' (jw_key 100 px), 'parody' | 'parody_cream' (112 px), 'sil_parody'."""
    if kind == 'brand':
        return T.render('garam', 'jw_key', px=100 * R)
    if kind == 'cream':
        return T.render('garam', tstyle('garam_cream'), px=100 * R)
    if kind == 'parody':
        return T.render('garam', tstyle('parody'), px=112 * R)
    if kind == 'parody_cream':
        return T.render('garam', tstyle('parody_cream'), px=112 * R)
    if kind == 'sil_parody':
        return T.render('garam', tstyle('sil'), font='pw_parody_fun', px=112 * R)
    raise KeyError(kind)


def _badge(kind, R):
    """Static badge sprites (NEW burst, NEW! burst, 50% OFF ribbon, CALL NOW pill) at resolution R, centred; plus
    their EMBER silhouettes. -> (sprite, silhouette)"""
    if kind in ('new', 'new2'):
        n, ro_, ri = 16, (116 if kind == 'new' else 100) * R, (90 if kind == 'new' else 78) * R
        size = int(2 * ro_ + 8 * R)
        c = size / 2.0
        m = poly_mask(star_pts(c, c, n, ro_, ri), size, size)
        inner = poly_mask(star_pts(c, c, n, ro_ - 5 * R, ri - 5 * R), size, size)
        if kind == 'new':
            body = rgba(m, lin('GOLD', 1.0) * 0.82) + 0.0
            body[..., :3] = m[..., None] * lin('EMBER', 0.9) * (1 - inner[..., None]) + \
                inner[..., None] * lin('GOLD', 1.05)
            ts = T.render('NEW', tstyle('ink'), px=60 * R)
        else:
            body = rgba(m, lin('EMBER'))
            body[..., :3] = m[..., None] * lin('RED', 0.9) * (1 - inner[..., None]) + inner[..., None] * lin('EMBER')
            ts = T.render('NEW!', tstyle('ivory'), px=52 * R)
        over_ts(body, ts, c, c)
        return ro(body), ro(rgba(m, lin('EMBER')))
    if kind == 'ribbon':
        w, h, r = int(460 * R), int(120 * R), 16 * R
        pad = int(6 * R)
        a = K.rrect_alpha(w, h, r, pad)
        hh, ww = a.shape
        yy = np.linspace(0, 1, hh, dtype=np.float32)[:, None, None]
        body = np.zeros((hh, ww, 4), np.float32)
        body[..., :3] = a[..., None] * (lin('EMBER', 1.12) * (1 - yy) + lin('EMBER', 0.8) * yy)
        body[..., 3] = a
        hl = K.rrect_alpha(w - int(8 * R), max(2, int(3 * R)), 2 * R, 0)
        K.draw(body, rgba(hl, lin('RED', 0.55)), ww / 2, pad + 7 * R)
        over_ts(body, T.render('50% OFF', tstyle('ivory'), px=84 * R), ww / 2, hh / 2)
        return ro(body), ro(rgba(a, lin('EMBER')))
    if kind == 'pill':
        w, h, r = int(470 * R), int(100 * R), 50 * R
        pad = int(6 * R)
        a = K.rrect_alpha(w, h, r, pad)
        inner = K.rrect_alpha(w - int(4 * R), h - int(4 * R), r - 2 * R, pad + int(2 * R))
        hh, ww = a.shape
        body = np.zeros((hh, ww, 4), np.float32)
        body[..., :3] = a[..., None] * lin('IVORY') * (1 - inner[..., None]) + inner[..., None] * lin('GOLD', 1.02)
        body[..., 3] = a
        over_ts(body, T.render('CALL NOW', tstyle('ink'), px=72 * R), ww / 2, hh / 2)
        return ro(body), ro(rgba(a, lin('EMBER')))
    raise KeyError(kind)


@functools.lru_cache(maxsize=None)
def badge(kind, R=1.0):
    spr, sil = _badge(kind, R)
    return Graphic([(spr, (0.0, 0.0), (0.5, 0.5), R)]), Graphic([(sil, (0.0, 0.0), (0.5, 0.5), R)])


BADGE_R = {'new': 1.25, 'ribbon': 1.25, 'new2': 1.0, 'pill': 1.0}     # v19 x1.2 hits only the first two


@functools.lru_cache(maxsize=8)
def sparkle_icon(size, cname):
    return ui.icon('sparkle', size, color=tuple(lin(cname, 2.0)), stroke=1.6, fill_a=0.85, glow=0.9,
                   glow_color=tuple(lin(cname, 1.2)))


SPARKLES = (((440, 860), 90, 'AMBER'), ((610, 900), 70, 'IVORY'), ((470, 1080), 56, 'AMBER'), ((590, 1150), 48, 'IVORY'))


@functools.lru_cache(maxsize=2)
def flare_spr():
    return ro(K.streak(1500, 64, lin('FLAME', 1.5), lin('AMBER', 1.2)))


# ============================================================================================ steam
STEAM_BOX = (255, 380, 775, 800)                   # x0 y0 x1 y1 (screen, push 1 / v19 1)
SB_W, SB_H = (STEAM_BOX[2] - STEAM_BOX[0]) // 2, (STEAM_BOX[3] - STEAM_BOX[1]) // 2
RIM = (515.0, 774.0)
T_LIFE = 5.2
N_BASE, N_DENSE = 90, 180


@functools.lru_cache(maxsize=1)
def steam_params():
    rng = np.random.default_rng(26)
    n = N_BASE + N_DENSE
    grp = np.r_[np.zeros(N_BASE), np.ones(N_DENSE)]
    idx = np.r_[np.arange(N_BASE) / N_BASE, np.arange(N_DENSE) / N_DENSE]
    P = dict(
        b=(idx + rng.uniform(0, 1.0, n) / np.where(grp > 0, N_DENSE, N_BASE)) * T_LIFE,
        x0=rng.uniform(-92, 92, n), vy=58.0 * rng.uniform(0.85, 1.2, n) * np.where(grp > 0, 1.12, 1.0),
        amp=rng.uniform(10, 26, n), fr=rng.uniform(0.22, 0.42, n), ph=rng.uniform(0, 2 * math.pi, n),
        r0=rng.uniform(10, 16, n), r1=rng.uniform(24, 40, n), al=rng.uniform(0.06, 0.20, n), grp=grp)
    return P


@functools.lru_cache(maxsize=64)
def gauss_kernel(sig2):
    """Gaussian splat kernel at half resolution, stretched 1.7x vertically (rising steam); sig2 = 2 x sigma_x
    (half-res px) as an int bin."""
    sig = sig2 / 2.0
    sy = sig * 1.7
    nx, ny = int(math.ceil(sig * 2.6)), int(math.ceil(sy * 2.6))
    yy, xx = np.mgrid[-ny:ny + 1, -nx:nx + 1].astype(np.float32)
    return ro(np.exp(-(xx * xx) / (2 * sig * sig) - (yy * yy) / (2 * sy * sy)))


WISPS = ((-34.0, 0.0, 1.0, 0), (6.0, 2.1, 0.9, 0), (40.0, 4.0, 1.1, 0), (-66.0, 1.2, 0.8, 1), (70.0, 5.1, 0.85, 1))


def steam_density(st, p):
    """Half-res steam density (SB_H, SB_W) float32 at steam clock p."""
    P = steam_params()
    d = np.zeros((SB_H, SB_W), np.float32)
    dense = st['dense']
    top = st['steam_top']
    age = np.mod(p - P['b'], T_LIFE)
    y = RIM[1] - P['vy'] * age
    x = RIM[0] + P['x0'] * (1.0 + 0.35 * age / T_LIFE) + P['amp'] * np.sin(2 * math.pi * P['fr'] * age + P['ph']) * \
        np.minimum(1.0, age / 1.2)
    r = P['r0'] + (P['r1'] - P['r0']) * np.minimum(1.0, age / 3.5)
    fin = np.clip(age / 0.3, 0, 1)
    fout = np.clip((y - top) / 120.0, 0, 1)
    fend = np.clip((T_LIFE - age) / 0.6, 0, 1)
    a = P['al'] * fin * fout * fend * np.where(P['grp'] > 0, dense, 1.0)
    hx = (x - STEAM_BOX[0]) / 2.0
    hy = (y - STEAM_BOX[1]) / 2.0
    for i in np.flatnonzero(a > 0.004):
        sig2 = int(round(r[i] / 2.0))                  # sigma = r / 2 (full res) = r / 4 (half) -> bin 2 sigma
        kern = gauss_kernel(max(2, sig2))
        ny, nx = kern.shape[0] // 2, kern.shape[1] // 2
        cx, cy = int(round(hx[i])), int(round(hy[i]))
        x0, y0, x1, y1 = cx - nx, cy - ny, cx + nx + 1, cy + ny + 1
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(SB_W, x1), min(SB_H, y1)
        if X1 <= X0 or Y1 <= Y0:
            continue
        d[Y0:Y1, X0:X1] += kern[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * np.float32(a[i])
    # wisps: thin rising ribbons for shape
    wm = np.zeros((SB_H, SB_W), np.uint8)
    for cx0, ph, amp, g in WISPS:
        k = 1.0 if g == 0 else dense
        if k <= 0.01:
            continue
        ys = np.linspace(RIM[1] - 6, top - 10, 36)
        hgt = RIM[1] - ys
        xs = RIM[0] + cx0 + amp * (5.0 + 0.13 * hgt) * np.sin(2 * math.pi * (hgt / 150.0 - 0.42 * p) + ph)
        fade = np.clip(hgt / 30.0, 0, 1) * np.clip((ys - top) / 110.0, 0, 1)
        for j in range(len(ys) - 1):
            v = int(255 * 0.75 * k * fade[j])
            if v < 3:
                continue
            p0 = (int(round((xs[j] - STEAM_BOX[0]) / 2.0 * 16)), int(round((ys[j] - STEAM_BOX[1]) / 2.0 * 16)))
            p1 = (int(round((xs[j + 1] - STEAM_BOX[0]) / 2.0 * 16)), int(round((ys[j + 1] - STEAM_BOX[1]) / 2.0 * 16)))
            cv2.line(wm, p0, p1, v, 2, cv2.LINE_AA, shift=4)
    if wm.any():
        d += cv2.GaussianBlur(wm.astype(np.float32) / 255.0 * 0.30, (0, 0), 1.2)
    return d


def steam_layers(st, p):
    """(steam light sprite (full res, alpha 0), outline sprite or None), both in STEAM_BOX coords at push 1."""
    d = steam_density(st, p)
    a = 1.0 - np.exp(-1.15 * d)
    af = cv2.resize(a, (SB_W * 2, SB_H * 2), interpolation=cv2.INTER_LINEAR)
    light = np.zeros(af.shape + (4,), np.float32)
    light[..., :3] = af[..., None] * (lin('IVORY', 0.92) * np.float32([1.0, 0.95, 0.9]))
    out = None
    k = st['outline']
    if k > 0:
        gy, gx = np.gradient(af)
        g = np.sqrt(gx * gx + gy * gy) + 0.004
        line = np.clip(1.0 - np.abs(af - 0.15) / (1.5 * g), 0.0, 1.0) * (af > 0.02)
        glow = cv2.GaussianBlur(line, (0, 0), 3.0)
        out = np.zeros(af.shape + (4,), np.float32)
        out[..., :3] = (line * 1.5 + glow * 0.8)[..., None] * lin('FLAME') * np.float32(k)
        out[..., 3] = line * np.float32(0.95 * k)
    return light, out


# ============================================================================================ glitter (v12 / v14)
N_GLIT = 640


@functools.lru_cache(maxsize=1)
def glitter_params():
    rng = np.random.default_rng(1226)
    return dict(u=rng.uniform(0, 1, N_GLIT), d=rng.uniform(0, 1, N_GLIT), r=rng.uniform(3.0, 6.0, N_GLIT),
                ph=rng.uniform(0, 1, N_GLIT), dl=rng.uniform(0, 6, N_GLIT), hot=rng.uniform(0.6, 1.0, N_GLIT))


@functools.lru_cache(maxsize=16)
def glitter_disc(rb):
    r = rb / 2.0
    n = int(math.ceil(r + 2))
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    dd = np.sqrt(xx * xx + yy * yy)
    core = np.clip(r - dd + 0.5, 0, 1)
    glow = np.exp(-(dd / (r * 0.9)) ** 2) * 0.35
    return ro(np.maximum(core * (0.65 + 0.35 * np.clip(1 - dd / r, 0, 1)), glow))


def perimeter(u, inset):
    """Point at perimeter fraction u (0..1) of the ad rect inset by `inset` px (vectorised)."""
    w, h = AD_W - 2 * inset, AD_H - 2 * inset
    L = 2 * (w + h)
    s = u * L
    x = np.where(s < w, inset + s, np.where(s < w + h, inset + w, np.where(s < 2 * w + h, inset + w - (s - w - h), inset)))
    y = np.where(s < w, inset, np.where(s < w + h, inset + (s - w), np.where(s < 2 * w + h, inset + h,
                                                                            inset + h - (s - 2 * w - h))))
    return x, y


def draw_glitter(ad, st, a):
    g12, g14, e19 = st['glitter']
    if g12 <= 0:
        return
    s = st['s']
    P = glitter_params()
    band = (18.0 + 18.0 * g14) * (1.0 + (e19 - 1.0) * (1.0 if g14 > 0 else 0.0))
    x, y = perimeter(P['u'], 10.0 + P['d'] * band)
    tw = 0.55 + 0.45 * np.sin(2 * math.pi * (3.0 * a + P['ph']))
    t12 = np.clip((s - (384 + P['dl']) / 30.0) / (2 / 30.0), 0, 1)
    t14 = np.clip((s - (416 + P['dl']) / 30.0) / (2 / 30.0), 0, 1)
    vis = np.where(np.arange(N_GLIT) < 320, t12, t14) * tw * P['hot']
    col = lin('GOLD', 1.5)
    for i in np.flatnonzero(vis > 0.01):
        k = glitter_disc(int(round(P['r'][i] * 2)))
        n = k.shape[0] // 2
        cx, cy = int(round(x[i])), int(round(y[i]))
        x0, y0 = cx - n, cy - n
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(AD_W, x0 + k.shape[1]), min(AD_H, y0 + k.shape[0])
        if X1 <= X0 or Y1 <= Y0:
            continue
        kk = k[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * np.float32(vis[i])
        reg = ad[Y0:Y1, X0:X1]
        reg[..., :3] = reg[..., :3] * (1 - kk[..., None] * 0.6) + kk[..., None] * col
    if g14 > 0:                                    # 12 sparkle stars along the band
        for j in range(12):
            u = (j + 0.37) / 12.0
            sx, sy = perimeter(np.array([u]), 10.0 + 0.5 * band)
            ph = j * 0.618
            k = g14 * (0.55 + 0.45 * math.sin(2 * math.pi * (1.3 * a + ph)))
            K.draw(ad, sparkle_icon(34, 'GOLD' if j % 2 else 'IVORY'), float(sx[0]), float(sy[0]),
                   rot=25.0 * a + 40 * j, scale=0.8 + 0.25 * k, opacity=min(1.0, 1.2 * k))


# ============================================================================================ the ad canvas
def _plate_pushed(z):
    p = plate()
    if abs(z - 1.0) < 1e-5:
        return np.array(p, copy=True)
    px, py = local(*PIV)
    M = np.float32([[z, 0, px * (1 - z)], [0, z, py * (1 - z)]])
    return cv2.warpAffine(p, M, (AD_W, AD_H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def _draw_glass(ad, st, a, z, e19):
    img = GLASS.at_yaw(S.yaw(a), interp='flow')
    bx, by = push_pt(BASE, z)
    k = GLASS_K * z * e19
    lx, ly = local(bx, by)
    # floor reflection (flipped about the foot line, x0.22, fading over 140 px; clipped by the ad rect)
    fy = push_pt((515.0, 1215.0), z, e19)[1] - AD_Y
    if fy < AD_H - 1:
        h = int(min(160, AD_H - math.floor(fy)))
        if h > 1:
            y0 = int(math.floor(fy))
            tmp = np.zeros((h, AD_W, 4), np.float32)
            K.draw(tmp, img, lx, (2 * fy - ly) - y0, scale=(k, -k), anchor=GLASS_ANCHOR)
            tmp *= reflection_ramp()[:h, None, None] * np.float32(0.22)
            reg = ad[y0:y0 + h]
            reg *= 1.0 - tmp[..., 3:4]
            reg += tmp
    K.draw(ad, img, lx, ly, scale=k, anchor=GLASS_ANCHOR)


def _draw_steam(ad, st, a, z, e19, s):
    p = S.steam_clock(s, a)
    light, outline = steam_layers(st, p)
    x, y = push_pt((STEAM_BOX[0], STEAM_BOX[1]), z, e19)
    lx, ly = local(x, y)
    K.draw(ad, light, lx, ly, scale=z * e19, anchor=(0, 0), mode='screen')
    if outline is not None:
        K.draw(ad, outline, lx, ly, scale=z * e19, anchor=(0, 0))


def _draw_sparkles(ad, st, a, z, e19):
    for j, ((x, y), size, cname) in enumerate(SPARKLES):
        k, op = st['sparkles'][j]
        if op <= 0:
            continue
        px, py = push_pt((x, y), z, e19)
        pulse = 0.9 + 0.1 * math.sin(2 * math.pi * 2.0 * a + j * 1.7)
        lx, ly = local(px, py)
        K.draw(ad, sparkle_icon(size, cname), lx, ly, scale=k * pulse * z * e19, rot=25.0 * a + 37.0 * j, opacity=op)


def _draw_logo(ad, st):
    k = st['logo_k'] * st['e19']
    R = logo_level(k)
    x, y = local(154.0 + st['logo_dx'], 504.0)
    sh = st['shadow']
    if sh > 0:
        logo(min(R, 6.0) if R >= 3 else 3.0, 'sil').draw(ad, x + 14, y + 14, k=k, opacity=sh)
    logo(R, 'brand').draw(ad, x, y, k=k)
    w = cream_at(st, x + 26 * k, y + 26 * k)
    if w > 0:
        logo(3.0, 'cream').draw(ad, x, y, k=k, opacity=w)


def _draw_garam(ad, st, a, garam_k):
    if garam_k <= 0:
        return
    e = st['e19']
    lx, ly = local(900.0, 1150.0)
    w = cream_at(st, lx - 120, ly + 16)
    pr = st['parody']
    if pr < 1:                                     # the v1 keyword (right-aligned, centre y 1150)
        ts = garam('brand')
        ts.draw(ad, lx, ly, anchor=(1.0, 0.5), opacity=garam_k * (1 - pr))
        if w > 0:
            garam('cream').draw(ad, lx, ly, anchor=(1.0, 0.5), opacity=garam_k * (1 - pr) * w, snap=False)
    if pr > 0:                                     # v10 parody: 112 px, wobble +-4 deg at 2 Hz about its centre
        R = 1.2 if e > 1.0 + 1e-4 else 1.0
        ts = garam('parody', R)
        k = st['parody_pop'] * e
        wob = 4.0 * math.sin(2 * math.pi * 2.0 * a) * pr
        cx = lx - ts.w / R * k / 2.0
        sh = st['shadow']
        if sh > 0:
            garam('sil_parody', R).draw(ad, cx + 14, ly + 14, anchor=(0.5, 0.5), scale=k / R, rot=wob,
                                        opacity=sh * pr * garam_k, snap=False)
        ts.draw(ad, cx, ly, anchor=(0.5, 0.5), scale=k / R, rot=wob, opacity=pr * garam_k, snap=False)
        if w > 0:
            garam('parody_cream').draw(ad, cx, ly, anchor=(0.5, 0.5), scale=k, rot=wob, opacity=pr * w * garam_k,
                                       snap=False)


def _draw_badge(ad, st, kind, xy, rot, scale_key, k_extra=1.0):
    k, op = st[scale_key]
    if op <= 0:
        return
    R = BADGE_R[kind]
    g, sil = badge(kind, R)
    lx, ly = local(*xy)
    kk = k * k_extra
    sh = st['shadow']
    if sh > 0:
        sil.draw(ad, lx + 14, ly + 14, k=kk, rot=rot, opacity=sh * op)
    g.draw(ad, lx, ly, k=kk, rot=rot, opacity=op)


def canvas(st, a=None, garam_k=1.0):
    """The ad at state st (pehle_wala_state.state(s)) and ambient a (default s): (760, 840, 4) opaque canvas."""
    s = st['s']
    a = s if a is None else a
    z, e19 = st['z'], st['e19']
    ad = _plate_pushed(z)
    # ---- v6 cream gag (inside the ad rect only)
    if st['cream_in'] > 0 and st['cream_out'] < 1:
        m = wave(CREAM_IN_O, st['cream_in'])
        mo = wave(CREAM_OUT_O, st['cream_out'])
        if mo is not None:
            m = m * (1.0 - mo)
        ad[..., :3] += (CREAM - ad[..., :3]) * m[..., None]
    # ---- product layer (pushed)
    cs = contact_shadow()
    cx, cy = push_pt((515.0, 1192.0), z, e19)
    K.draw(ad, cs, cx - AD_X, cy - AD_Y, scale=z * e19, opacity=0.6)
    _draw_glass(ad, st, a, z, e19)
    _draw_steam(ad, st, a, z, e19, s)
    _draw_sparkles(ad, st, a, z, e19)
    # ---- graphics (not pushed)
    _draw_logo(ad, st)
    _draw_garam(ad, st, a, garam_k)
    _draw_badge(ad, st, 'new', (810.0, 800.0), -12.0, 'burst1', e19)
    _draw_badge(ad, st, 'ribbon', (720.0, 748.0), -8.0, 'ribbon', e19)
    _draw_badge(ad, st, 'pill', (540.0, 1060.0), 0.0, 'pill')
    _draw_badge(ad, st, 'new2', (260.0, 880.0), 10.0, 'burst2')
    # ---- v16 cinematic: flares on the rim / base line, then letterbox bars
    fl = st['flares']
    if fl > 0:
        br = fl * (0.92 + 0.08 * math.sin(2 * math.pi * 0.5 * a))
        for (fx, fy), g in (((515.0, 790.0), 1.0), ((515.0, 1140.0), 0.8)):
            px, py = push_pt((fx, fy), z, e19)
            K.draw(ad, flare_spr(), px - AD_X, py - AD_Y, scale=(1.0, e19), opacity=br * g, mode='add')
    lb = st['letterbox']
    if lb > 0:
        hb = 64.0 * (e19 if s >= 512 / 30.0 else 1.0)
        top = hb * lb
        it = int(math.floor(top))
        night = lin('NIGHT_0')
        if it > 0:
            ad[:it, :, :3] = night
            ad[AD_H - it:, :, :3] = night
        fr_ = top - it
        if fr_ > 0 and it < AD_H // 2:
            ad[it, :, :3] += (night - ad[it, :, :3]) * np.float32(fr_)
            ad[AD_H - it - 1, :, :3] += (night - ad[AD_H - it - 1, :, :3]) * np.float32(fr_)
    draw_glitter(ad, st, a)
    # ---- v5 / v21 saturation + exposure (ad rect only)
    sat, ex = st['sat'], st['expo']
    if sat > 1.0001 or ex > 1e-4:
        rgb = ad[..., :3]
        L = rgb @ np.float32([0.2126, 0.7152, 0.0722])
        rgb -= L[..., None]
        rgb *= np.float32(sat)
        rgb += L[..., None]
        np.maximum(rgb, 0.0, out=rgb)
        if ex > 0:
            rgb *= np.float32(2.0 ** ex)
    ad[..., 3] = 1.0
    return ad


# ============================================================================================ drawer thumbnails
THUMB_W, THUMB_H = 80, 46


@functools.lru_cache(maxsize=8)
def thumb(v):
    """80 x 46 thumbnail of version v (the ad at that version's change frame + 10 f), centre-cropped, read-only."""
    f = (S.CHANGE_FRAMES[v - 2] if v >= 2 else 0) + 10
    s = f / 30.0
    st = S.state(s)
    ad = canvas(st, s)
    h = int(round(AD_W * THUMB_H / THUMB_W))
    y0 = max(0, int(round(AD_H * 0.42 - h / 2)))
    crop = np.ascontiguousarray(ad[y0:y0 + h])
    sm = cv2.resize(crop, (THUMB_W, THUMB_H), interpolation=cv2.INTER_AREA)
    m = K.rrect_alpha(THUMB_W, THUMB_H, 6, 0)
    sm *= m[..., None]
    return ro(sm)


def prewarm():
    plate()
    round_mask()
    contact_shadow()
    dist_map(*CREAM_IN_O)
    dist_map(*CREAM_OUT_O)
    for R in LOGO_LEVELS:
        logo(R, 'brand')
    logo(3.0, 'cream')
    logo(3.0, 'sil')
    logo(6.0, 'sil')
    for kd in ('brand', 'cream'):
        garam(kd)
    for R in (1.0, 1.2):
        garam('parody', R)
        garam('sil_parody', R)
    garam('parody_cream')
    for kd, R in BADGE_R.items():
        badge(kd, R)
    for (_, size, cname) in SPARKLES:
        sparkle_icon(size, cname)
    sparkle_icon(34, 'GOLD')
    sparkle_icon(34, 'IVORY')
    flare_spr()
    steam_params()
    glitter_params()
    for i in range(-5, 5):                          # the 10 glass flow pairs between -5 and +5 deg
        GLASS.at_yaw(float(i) + 0.5, interp='flow')
