"""Floret Capitals - cinematic SaaS motion-graphics spot (Lahore concert sponsorship), 1248x1248 @ 60 fps.

Look: near-black stage lit by slow liquid colour blooms, real liquid-glass panels (edge lensing, chromatic
dispersion, frosted core, specular rim, soft shadow) that refract whatever glows behind them, glossy rim-lit
Blender objects, text orbiting objects in 3D, and General Sans typography (light / semibold pairings,
tracked micro-labels) revealed letter by letter with blur, tracking and light sweeps.

python3 floret.py still <t> [<t> ...]   -> workspace4/work/stills/*.jpg
python3 floret.py render [workers]      -> workspace4/work/video.mp4
"""
import functools
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'memories'))
import anim as A  # noqa: E402
import comp as C  # noqa: E402
import hud as U  # noqa: E402

S = 1248
C.W = C.H = S
FPS = 60
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'workspace4'))
ASSETS, WORK, OUT = ROOT + '/assets', ROOT + '/work', ROOT + '/out'
F = 1340.0                                   # focal length (px) of the UI camera
SS = U.SS
CAM = C.Cam(0, 0, 0, F=F)

# General Sans weights
XL, L, R, M, SB, B = (f'GeneralSans-{w}' for w in (200, 300, 400, 500, 600, 700))


def hexs(h):
    return np.float32([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


# sRGB (for Paint) and linear (for the canvas) colours
GOLD_S, GOLD_HI_S, GOLD_LO_S, CHAMP_S = hexs('e49f38'), hexs('f7d08a'), hexs('b06a1c'), hexs('fff1d6')
WHITE_S, MUTED_S, DIM_S, DARK_S = hexs('f5f3ef'), hexs('8e8b86'), hexs('5c5a57'), hexs('0b0a09')
GOLD, GOLD_HI, GOLD_LO, CHAMP = (C.to_lin(c) for c in (GOLD_S, GOLD_HI_S, GOLD_LO_S, CHAMP_S))
WHITE, MUTED = C.to_lin(WHITE_S), C.to_lin(MUTED_S)
# bloom light colours (linear)
BL_GOLD, BL_AMBER, BL_BLUE, BL_GREEN = C.to_lin(hexs('e8a040')), C.to_lin(hexs('ff6a14')), C.to_lin(hexs('2f63ff')), \
    C.to_lin(hexs('19b36e'))
BL_RED, BL_ICE, BL_VIOLET = C.to_lin(hexs('e8262f')), C.to_lin(hexs('a9c8ff')), C.to_lin(hexs('7b4dff'))

# ------------------------------------------------------------------ timeline (s)
FRAMES = [('f1', 0.0, 3.8), ('f2', 3.8, 6.8), ('f3', 6.8, 10.2), ('f4', 10.2, 13.4), ('f5', 13.4, 16.6),
          ('f6', 16.6, 20.6), ('f7', 20.6, 24.4), ('f8', 24.4, 27.8), ('f9', 27.8, 30.6), ('f10', 30.6, 36.0)]
DUR = FRAMES[-1][2]
NF = int(round(DUR * FPS))
EXIT = 0.42                                   # every scene clears in its last EXIT s, before the next enters


def exit_p(u, d):
    return A.EXPO_IN(A.clamp((u - (d - EXIT)) / EXIT))


# ------------------------------------------------------------------ sprites
@functools.lru_cache(maxsize=2048)
def tsprite(txt, font, px, col='w', track=0.0):
    """Text -> premultiplied linear RGBA sprite (padded 26 px), baseline y, advance width."""
    m, base = U.text_mask(txt, font, px, track)
    m = cv2.resize(m, (max(1, m.shape[1] // SS), max(1, m.shape[0] // SS)), interpolation=cv2.INTER_AREA)
    P = 26
    m = np.pad(m, P)
    h = m.shape[0]
    base = base / SS + P
    if col in ('g', 'wg', 's'):
        top, bot = base - px * 0.74, base + px * 0.05
        v = np.clip((np.arange(h, dtype=np.float32) - top) / max(bot - top, 1), 0, 1)[:, None, None]
        hi, mid, lo = {'g': (CHAMP, GOLD_HI, GOLD), 'wg': (C.to_lin(hexs('ffffff')), WHITE, GOLD_HI),
                       's': (C.to_lin(hexs('ffffff')), C.to_lin(hexs('dfe3ea')), C.to_lin(hexs('9aa1ab')))}[col]
        c = np.where(v < 0.45, hi + (mid - hi) * (v / 0.45), mid + (lo - mid) * ((v - 0.45) / 0.55))
    else:
        c = {'w': WHITE, 'm': MUTED, 'gold': GOLD, 'hi': GOLD_HI, 'dim': C.to_lin(DIM_S)}[col][None, None]
    rgb = c * m[..., None]
    return np.dstack([rgb, m]).astype(np.float32), base, m.shape[1] - 2 * P


def blur_spr(spr, sig):
    return cv2.GaussianBlur(spr, (0, 0), sig) if sig >= 0.6 else spr


def blit_M(cv, spr, M, op=1.0, mode='over', blur=0.0):
    """Composite a premultiplied RGBA sprite through the 2x3 affine M (sprite px -> canvas px)."""
    if op <= 0.003:
        return
    spr = blur_spr(spr, blur)
    h, w = spr.shape[:2]
    M = np.float32(M).copy()
    cs = np.float32([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]]) @ M.T
    x0, y0 = np.floor(cs.min(0)).astype(int)
    x1, y1 = np.ceil(cs.max(0)).astype(int) + 1
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(S, x1), min(S, y1)
    if x1 <= x0 or y1 <= y0:
        return
    M[0, 2] -= x0
    M[1, 2] -= y0
    out = cv2.warpAffine(spr, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderValue=0) * op
    reg = cv[y0:y1, x0:x1]
    if mode == 'add':
        reg[..., :3] += out[..., :3]
        return
    a = out[..., 3:4]
    reg[..., :3] = out[..., :3] + reg[..., :3] * (1 - a)


def blit(cv, spr, x, y, ax=0.5, ay=0.5, s=1.0, op=1.0, rot=0.0, blur=0.0, mode='over', sx=1.0):
    """Composite a sprite so its (ax, ay) fraction lands on (x, y); s = scale, sx = extra horizontal scale."""
    if op <= 0.003 or s <= 0.01:
        return
    h, w = spr.shape[:2]
    r = math.radians(-rot)
    c, sn = math.cos(r), math.sin(r)
    Ml = np.float64([[c * s * sx, -sn * s], [sn * s * sx, c * s]])
    off = np.float64([x, y]) - Ml @ np.float64([w * ax, h * ay])
    blit_M(cv, spr, np.c_[Ml, off], op, mode, blur)


def half(img):
    """Paint results are supersampled (SS x): bring them to 1x."""
    return cv2.resize(img, (img.shape[1] // SS, img.shape[0] // SS), interpolation=cv2.INTER_AREA)


def poly(p, pts, col, op=1.0):
    m = np.zeros((p.Hp, p.Wp), np.float32)
    cv2.fillPoly(m, [np.int32([[p.X(x) * 8, p.X(y) * 8] for x, y in pts])], 1.0, cv2.LINE_AA, shift=3)
    p.over(m, col, op)
    return m


def walk(seed, n=48, drift=0.6, vol=1.0):
    rng = np.random.default_rng(seed)
    v = np.cumsum(rng.normal(drift / n * 3, vol / math.sqrt(n), n))
    v = v - v.min()
    return v / max(v.max(), 1e-6)


def spark(p, x, y, w, h, seed, prog=1.0, col=GOLD_S, width=2.4, fill=True, drift=0.6, dot=True):
    v = walk(seed, drift=drift)
    n = max(2, int(round(len(v) * prog)))
    xs = np.linspace(x, x + w, len(v))
    pts = [(xs[i], y + h * (1 - v[i])) for i in range(n)]
    if fill and n > 2:
        m = poly(p, pts + [(pts[-1][0], y + h), (x, y + h)], col, 0.0)
        g = np.clip(1 - (p._yy - p.X(y)) / (h * SS), 0, 1) ** 1.5
        p.add(m * g, col, 0.28)
    lm = p.line(pts, width, col, 1.0)
    p.glow(lm, col, 5, 0.5)
    if dot:
        p.circle(pts[-1][0], pts[-1][1], width * 2.4, col, 0.25)
        p.circle(pts[-1][0], pts[-1][1], width * 1.3, CHAMP_S, 1.0)
    return pts[-1]


# ------------------------------------------------------------------ Blender 3D elements (b3d.py)
B3D_N = dict(logo=120, goldbar=96, silverbar=96, barrel=96, coin=96, shield=96)
B3D_SCALE = dict(logo=0.6)


def _b3d_path(job, f):
    for d in ('b3d2', 'b3d'):                                 # relit v2 set first, v1 as fallback
        p = f'{ROOT}/{d}/{job}/{f:04d}.png'
        if os.path.exists(p):
            return p
    return None


def b3d(job, fpos, pingpong=False):
    """Premultiplied linear RGBA of a Blender element at fractional 30 fps frame fpos (1-based), frame-blended."""
    n = B3D_N[job]
    if pingpong:
        fpos = 1 + abs(((fpos - 1) % (2 * (n - 1))) - (n - 1))
    fpos = min(max(fpos, 1.0), float(n))
    f0 = int(math.floor(fpos))
    w = fpos - f0
    p0, p1 = _b3d_path(job, f0), _b3d_path(job, min(n, f0 + 1))
    if p0 is None:
        return None
    sc = B3D_SCALE.get(job, 0.5)
    a = C.load(p0, sc)
    if w < 0.02 or p1 is None or p1 == p0:
        return a
    return a * (1 - w) + C.load(p1, sc) * w


def hero(cv, spr, x, y, s=1.0, op=1.0, blur=0.0, glow=BL_GOLD, glow_k=1.0, rim=0.9, reflect=0.0):
    """Product shot of a 3D sprite: coloured light bloom behind, hot rim light around the silhouette."""
    if spr is None or op <= 0.003:
        return
    h, w = spr.shape[:2]
    a = spr[..., 3]
    if glow_k > 0:                                            # bloom behind (quarter res)
        q = cv2.resize(a, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
        q = cv2.GaussianBlur(q, (0, 0), w / 4 * 0.12)
        g = cv2.resize(q, (w, h))
        gl = np.dstack([g[..., None] * glow * 0.55 * glow_k, g * 0]).astype(np.float32)
        blit(cv, gl, x, y, s=s * 1.25, op=op, mode='add')
    if rim > 0:                                               # rim: alpha edge, lit from above
        er = cv2.erode(a, np.ones((5, 5), np.uint8))
        edge = np.clip(a - er, 0, 1)
        yy = np.linspace(1.0, 0.35, h, dtype=np.float32)[:, None]
        edge = cv2.GaussianBlur(edge * yy, (0, 0), 1.2)
        rimspr = np.dstack([edge[..., None] * CHAMP * rim, edge * 0]).astype(np.float32)
    if reflect > 0:
        ys = np.where(a.max(1) > 0.05)[0]
        if len(ys):
            bot = ys.max()
            L = int(h * 0.3)
            ref = spr[max(0, bot - L):bot + 1][::-1]
            fade = np.linspace(1, 0, ref.shape[0], dtype=np.float32)[:, None, None] ** 1.8 * reflect
            ref = cv2.GaussianBlur(ref * fade, (0, 0), 3)
            blit(cv, ref, x, y + (bot - h / 2 + 4) * s, ay=0.0, s=s, op=op, blur=blur)
    blit(cv, spr, x, y, s=s, op=op, blur=blur)
    if rim > 0:
        blit(cv, rimspr, x, y, s=s, op=op, blur=blur, mode='add')


# ------------------------------------------------------------------ liquid glass
GP = 64                                       # padding around a glass card (room for shadow + rim glow)


@functools.lru_cache(maxsize=64)
def glass_geo(w, h, r, bevel=26):
    """Card-local geometry of a rounded-rect glass slab (with GP padding):
    (inside, lens, nx, ny) and (rim, shadow, sheen) planes."""
    W2, H2 = w + 2 * GP, h + 2 * GP
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32) + 0.5
    qx = np.abs(xx - W2 / 2) - (w / 2 - r)
    qy = np.abs(yy - H2 / 2) - (h / 2 - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    gy, gx = np.gradient(cv2.GaussianBlur(d, (0, 0), 1.0))
    n = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    nx, ny = gx / n, gy / n
    inside = np.clip(0.5 - d, 0, 1)
    tt = np.clip(-d / bevel, 0, 1)
    lens = ((1 - tt) ** 2.2) * inside
    rim = np.exp(-((d + 1.3) / 1.0) ** 2)
    sh = cv2.GaussianBlur(inside, (0, 0), 20)
    sh = np.roll(sh, 18, axis=0)
    sheen = inside * np.clip(1 - (yy - GP) / (h * 0.55), 0, 1) ** 2
    return (np.dstack([inside, lens, nx, ny]).astype(np.float32), np.dstack([rim, sh, sheen]).astype(np.float32))


def card_matrix(wb, hb, cx, cy, wpx, rot=(0, 0, 0), depth=4.0, dz=0.0):
    """Homography: card sprite px (body wb x hb + GP padding) -> canvas px, body wpx wide at rest on (cx, cy)."""
    k = wpx / wb * depth / F
    W2, H2 = wb + 2 * GP, hb + 2 * GP
    ctr = ((cx - S / 2) * depth / F, -(cy - S / 2) * depth / F, depth + dz)
    pts, d = CAM.project(C.plane_corners(ctr, (W2 * k, H2 * k), tuple(rot)))
    if d.min() < 0.05:
        return None, None
    Mx = cv2.getPerspectiveTransform(np.float32([[0, 0], [W2, 0], [W2, H2], [0, H2]]), pts.astype(np.float32))
    return Mx, pts


def glass(cv, wb, hb, r, cx, cy, wpx, rot=(0, 0, 0), depth=4.0, dz=0.0, op=1.0, content=None, refr=16.0, frost=9.0,
          dark=0.80, tint=None, rim_col=None, rim_k=0.0, spec=1.0, shadow=0.6, cblur=0.0, bevel=26):
    """Liquid-glass slab: refracts and frosts the canvas behind it, chromatic edge dispersion, specular rim,
    top sheen, soft drop shadow, optional coloured neon rim glow; then the card content on top."""
    if op <= 0.003:
        return
    Mx, pts = card_matrix(wb, hb, cx, cy, wpx, rot, depth, dz)
    if Mx is None:
        return
    pad = 40
    bx0, by0 = int(max(0, pts[:, 0].min() - pad)), int(max(0, pts[:, 1].min() - pad))
    bx1, by1 = int(min(S, pts[:, 0].max() + pad)), int(min(S, pts[:, 1].max() + pad))
    if bx1 - bx0 < 4 or by1 - by0 < 4:
        return
    T = np.array([[1, 0, -bx0], [0, 1, -by0], [0, 0, 1]], np.float64) @ Mx
    sz = (bx1 - bx0, by1 - by0)
    g1, g2 = glass_geo(wb, hb, r, bevel)
    G1 = cv2.warpPerspective(g1, T, sz, flags=cv2.INTER_LINEAR, borderValue=0)
    G2 = cv2.warpPerspective(g2, T, sz, flags=cv2.INTER_LINEAR, borderValue=0)
    ins, lens, nx, ny = (G1[..., i] for i in range(4))
    rim, sh, sheen = (G2[..., i] for i in range(3))
    scale = math.sqrt(abs(np.linalg.det(Mx[:2, :2])))           # local px per card px (approx)
    reg = cv[by0:by1, bx0:bx1]
    reg[..., :3] *= (1 - shadow * sh * op * (1 - ins))[..., None]
    base = reg[..., :3].copy()
    fro = cv2.GaussianBlur(base, (0, 0), max(0.6, frost * scale))
    mix = np.clip(lens * 0.75, 0, 1)[..., None]
    src = fro * (1 - mix) + base * mix
    hh, ww = ins.shape
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    D = refr * scale * lens
    out = np.empty_like(base)
    for ch, kc in enumerate((1.0, 1.18, 1.36)):                  # dispersion: blue bends most
        out[..., ch] = cv2.remap(src[..., ch], xx + nx * D * kc, yy + ny * D * kc, cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REFLECT)
    out *= dark
    if tint is not None:
        out += np.asarray(tint, np.float32) * ins[..., None]
    Lx, Ly = -0.5, -0.866                                        # key light from the top-left
    ndl = nx * Lx + ny * Ly
    sp = rim * (np.clip(ndl, 0, 1) ** 1.4 * 1.5 + np.clip(-ndl, 0, 1) ** 2 * 0.45 + 0.16) * spec
    out += sp[..., None] * C.to_lin(hexs('fff6e8'))
    out += (lens ** 2 * 0.05 + lens ** 3 * np.clip(ndl, 0, 1) * 0.22)[..., None] * spec
    out += (sheen * 0.035 * spec)[..., None]
    m = (ins * op)[..., None]
    reg[..., :3] = reg[..., :3] * (1 - m) + out * m
    if rim_col is not None and rim_k > 0:                        # neon rim light bleeding out of the edge
        rg = rim * np.clip(ndl * 0.6 + 0.6, 0.15, 1)
        glow = rg * 1.2 + cv2.GaussianBlur(rg, (0, 0), 5 * scale) * 6 + cv2.GaussianBlur(rg, (0, 0), 18 * scale) * 10
        reg[..., :3] += glow[..., None] * np.asarray(rim_col, np.float32) * rim_k * op
    if content is not None:
        cw = cv2.warpPerspective(content, T, sz, flags=cv2.INTER_LINEAR, borderValue=0)
        if cblur >= 0.6:
            cw = cv2.GaussianBlur(cw, (0, 0), cblur)
        C.over(reg, cw * op)


def new_card(w, h):
    return U.Paint(w, h, pad=GP)


def card_img(p):
    return half(p.result())


# ------------------------------------------------------------------ logo
@functools.lru_cache(maxsize=8)
def logo_flat(width):
    """The Floret mark (gold bars + silver arrow) as a flat sprite `width` px wide (for UI chrome)."""
    im = cv2.imread(ASSETS + '/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3]
    ys, xs = np.where(a > 0.02)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hgt = int(round(im.shape[0] * width / im.shape[1]))
    im = cv2.resize(im, (width, hgt), interpolation=cv2.INTER_AREA)
    rgb = C.to_lin(im[..., 2::-1]) * im[..., 3:4]
    return np.pad(np.dstack([rgb, im[..., 3]]).astype(np.float32), ((4, 4), (4, 4), (0, 0)))


# ------------------------------------------------------------------ typography
class Title:
    """One line of type built from segments [(text, font, px, col)]; revealed letter by letter
    (blur -> sharp, rise, tracking settles), exits with a quick blur-up; optional light sweep."""

    def __init__(self, segs, x, y, align='c', gap=0.28, track=0.0):
        self.chars = []
        X = 0.0
        for k, (text, font, px, col) in enumerate(segs):
            f = U._font(font, px * SS)
            for i, ch in enumerate(text):
                if ch != ' ':
                    self.chars.append((ch, font, px, col, X + f.getlength(text[:i]) / SS + i * px * track))
            X += f.getlength(text) / SS + (len(text) - 1) * px * track + (px * gap if k < len(segs) - 1 else 0)
        self.width = X
        self.x0 = x - X / 2 if align == 'c' else (x - X if align == 'r' else x)
        self.y = y
        self.px = max(s[2] for s in segs)

    def draw(self, cv, t, t_in, t_out=1e9, stagger=0.024, dur=0.95, op=1.0, sweep=0.55, dy=0.0, s=1.0):
        n = len(self.chars)
        xc = self.x0 + self.width / 2
        bx = None
        if sweep is not None:
            su = (t - t_in - sweep - n * stagger * 0.5) / 0.9
            if 0 < su < 1:
                bx = self.x0 - 120 + (self.width + 240) * A.EASY(su)
        for i, (ch, font, px, col, xo) in enumerate(self.chars):
            u = t - t_in - i * stagger
            if u <= 0:
                continue
            p = A.EXPO_OUT(A.clamp(u / dur))
            q = A.EXPO_IN(A.clamp((t - t_out - i * 0.008) / 0.38)) if t > t_out else 0.0
            o = A.ramp(u, 0, dur * 0.45) * (1 - q) * op
            if o <= 0.003:
                continue
            spr, base, adv = tsprite(ch, font, px, col)
            x = self.x0 + xo
            x = xc + (x - xc) * (1 + 0.06 * (1 - p)) * s
            y = self.y + dy + (1 - p) * px * 0.30 - q * px * 0.25
            yy = S / 2 + (y - S / 2) * s if s != 1.0 else y
            bl = (1 - p) * 9 + q * 9
            blit(cv, spr, x - 26 * s, yy, ax=0, ay=base / spr.shape[0], s=s, op=o, blur=bl)
            if bx is not None:
                k = math.exp(-((x + adv / 2 - bx) / (px * 1.1)) ** 2)
                if k > 0.02:
                    blit(cv, spr, x - 26 * s, yy, ax=0, ay=base / spr.shape[0], s=s, op=o * k * 0.9, mode='add')


def kicker(cv, txt, x, y, t, t_in, t_out=1e9, col='gold', px=17, op=1.0, lines=True):
    """Tracked micro-label with hairlines either side (e.g. '—  FLORET CAPITALS  —')."""
    u = t - t_in
    if u <= 0:
        return
    p = A.EXPO_OUT(A.clamp(u / 1.0))
    q = A.EXPO_IN(A.clamp((t - t_out) / 0.38)) if t > t_out else 0.0
    o = A.ramp(u, 0, 0.5) * (1 - q) * op
    spr, base, adv = tsprite(txt.upper(), M, px, col, round(0.34 + 0.18 * (1 - p), 2))
    blit(cv, spr, x, y, ay=base / spr.shape[0], op=o, blur=(1 - p) * 4 + q * 6)
    if lines:
        L = 46 * p
        w = spr.shape[1] / 2 - 26 + 18
        for sgn in (-1, 1):
            ln = np.zeros((6, int(L) + 2, 4), np.float32)
            ln[2:4, :, :3] = GOLD * 0.9
            ln[2:4, :, 3] = 0.9
            blit(cv, ln, x + sgn * (w + L / 2), y - px * 0.36, op=o)


# ------------------------------------------------------------------ orbit text
@functools.lru_cache(maxsize=8)
def _orbit_layout(text, font, px, col):
    f = U._font(font, px * SS)
    adv = np.float32([f.getlength(ch) / SS for ch in text])
    cum = np.cumsum(adv) - adv / 2
    return adv, cum, float(adv.sum())


def orbit(cv, text, font, px, col, cx, cy, R, spin, side, tilt=68.0, roll=-14.0, op=1.0, reveal=1.0, back=0.3):
    """Text on a ring in 3D around (cx, cy): ring radius R px, tilted `tilt` deg from face-on, rolled in plane.
    side='back' draws the far half (dim, soft), side='front' the near half - draw an object in between."""
    if op <= 0.003:
        return
    adv, cum, tot = _orbit_layout(text, font, px, col)
    sa, ca = math.sin(math.radians(90 - tilt)), math.cos(math.radians(90 - tilt))
    rr = math.radians(roll)
    cr, sr = math.cos(rr), math.sin(rr)
    D = R * 4.5
    for i, ch in enumerate(text):
        if ch == ' ':
            continue
        frac = cum[i] / tot
        if frac > reveal:
            continue
        th = spin + frac * 2 * math.pi
        X, Z = R * math.sin(th), R * math.cos(th)                # Z > 0: towards the viewer
        if (Z > 0) != (side == 'front'):
            continue
        Y = Z * sa                                               # tilt: near side sits lower
        Zc = Z * ca
        k = D / (D - Zc)
        x, y = X * k, Y * k
        tx, ty = math.cos(th) * k, -math.sin(th) * sa * k        # tangent d/dth
        x, y = x * cr - y * sr, x * sr + y * cr
        tx, ty = tx * cr - ty * sr, tx * sr + ty * cr
        ang = math.degrees(math.atan2(ty, tx))
        face = abs(math.cos(th)) ** 0.5
        spr, base, a = tsprite(ch, font, px, col)
        depthk = 0.5 + 0.5 * (Z / R)
        o = op * (back + (1 - back) * depthk) if Z > 0 else op * back * (0.6 + 0.4 * (1 + Z / R))
        blit(cv, spr, cx + x, cy + y, ax=0.5, ay=(base - px * 0.36) / spr.shape[0], s=k, sx=max(0.25, face),
             rot=-ang, op=o, blur=0.0 if Z > 0 else 1.2)


# ------------------------------------------------------------------ background: liquid colour blooms
# per scene: (colour, x, y, radius, intensity, phase)  - all in frame fractions
BLOOMS = {
    'f1': [(BL_GOLD, 0.50, 0.44, 0.26, 0.75, 0.0), (BL_AMBER, 0.56, 0.58, 0.16, 0.45, 1.3), (BL_BLUE, 0.12, 0.10, 0.22, 0.16, 2.0)],
    'f2': [(BL_GOLD, 0.50, 0.86, 0.32, 0.65, 0.4), (BL_BLUE, 0.88, 0.16, 0.24, 0.20, 1.0), (BL_AMBER, 0.20, 0.70, 0.16, 0.25, 2.4)],
    'f3': [(BL_GOLD, 0.52, 0.58, 0.30, 0.55, 0.2), (BL_GREEN, 0.14, 0.18, 0.22, 0.26, 1.7), (BL_BLUE, 0.90, 0.85, 0.20, 0.18, 0.8)],
    'f4': [(BL_GOLD, 0.30, 0.70, 0.30, 0.55, 0.1), (BL_BLUE, 0.84, 0.48, 0.26, 0.30, 2.2), (BL_VIOLET, 0.70, 0.95, 0.18, 0.22, 1.1)],
    'f5': [(BL_GREEN, 0.28, 0.40, 0.22, 0.55, 0.6), (BL_RED, 0.72, 0.40, 0.22, 0.50, 1.9), (BL_GOLD, 0.50, 0.80, 0.26, 0.40, 0.3)],
    'f6': [(BL_GOLD, 0.50, 0.62, 0.30, 0.55, 0.9), (BL_AMBER, 0.20, 0.30, 0.18, 0.22, 2.6), (BL_BLUE, 0.85, 0.25, 0.20, 0.22, 0.2)],
    'f7': [(BL_BLUE, 0.26, 0.58, 0.28, 0.48, 1.4), (BL_GOLD, 0.72, 0.62, 0.28, 0.50, 0.5), (BL_VIOLET, 0.10, 0.92, 0.16, 0.18, 2.1)],
    'f8': [(BL_GOLD, 0.50, 0.40, 0.28, 0.75, 0.7), (BL_AMBER, 0.50, 0.50, 0.14, 0.40, 1.6), (BL_BLUE, 0.88, 0.88, 0.20, 0.20, 2.8)],
    'f9': [(BL_GOLD, 0.50, 0.50, 0.22, 0.65, 0.3), (BL_BLUE, 0.50, 0.50, 0.40, 0.20, 1.2)],
    'f10': [(BL_GOLD, 0.50, 0.98, 0.42, 0.70, 0.0), (BL_AMBER, 0.50, 1.02, 0.26, 0.60, 1.0), (BL_BLUE, 0.15, 0.12, 0.22, 0.14, 2.3)],
}
QL = 156                                       # bloom field resolution


@functools.lru_cache(maxsize=1)
def _qgrid():
    yy, xx = np.mgrid[0:QL, 0:QL].astype(np.float32) / QL
    return yy, xx


@functools.lru_cache(maxsize=1)
def _bg_base():
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r = np.hypot(xx - S / 2, yy - S * 0.5) / S
    return (np.exp(-(r / 0.6) ** 2)[..., None] * C.to_lin(hexs('0b0a0a')) + C.to_lin(hexs('030304'))).astype(np.float32)


@functools.lru_cache(maxsize=1)
def _dust():
    rng = np.random.default_rng(7)
    n = 110
    return np.c_[rng.uniform(-7, 7, n), rng.uniform(-5, 5, n), rng.uniform(2.5, 16, n)], rng.uniform(0.004, 0.010, n), \
        rng.uniform(0, 6.28, n)


def scene_weight(t, a, b):
    return A.ramp(t, a - 0.35, a + 0.55, A.EASY) * (1 - A.ramp(t, b - 0.25, b + 0.45, A.EASY))


BOOST = {}                                     # per-frame bloom intensity overrides set by scenes


def background(t):
    cv = _bg_base().copy()
    yy, xx = _qgrid()
    q = np.zeros((QL, QL, 3), np.float32)
    for name, a, b in FRAMES:
        w = scene_weight(t, a, b)
        if w <= 0.002:
            continue
        w *= BOOST.get(name, 1.0)
        for col, x, y, r, k, ph in BLOOMS[name]:
            # liquid: domain-warped gaussian, drifting slowly
            wx = xx + 0.045 * np.sin(yy * 7.0 + t * 0.55 + ph) + 0.022 * np.sin(yy * 15.0 - t * 0.9 + ph * 2.1)
            wy = yy + 0.045 * np.sin(xx * 6.0 - t * 0.47 + ph * 1.7) + 0.022 * np.sin(xx * 13.0 + t * 0.8 + ph)
            x2 = x + 0.03 * math.sin(t * 0.31 + ph)
            y2 = y + 0.025 * math.cos(t * 0.27 + ph * 1.4)
            g = np.exp(-((wx - x2) ** 2 + (wy - y2) ** 2) / (2 * (r * 0.8) ** 2))
            q += g[..., None] * col * (k * w)
    big = cv2.resize(q, (S, S), interpolation=cv2.INTER_CUBIC)
    cv += cv2.GaussianBlur(big, (0, 0), 4) * 0.42
    P, rad, ph = _dust()
    P = P.copy()
    P[:, 1] += 0.25 * np.sin(t * 0.3 + ph)
    P[:, 0] += 0.2 * np.sin(t * 0.21 + ph * 1.3)
    P[:, 2] = (P[:, 2] - t * 0.3 - 4.0) % 12.5 + 4.0
    tw = 0.5 + 0.5 * np.sin(t * 2.0 + ph * 5)
    C.particles(cv, C.Cam(0, 0, 0, F=F, focus=6.0, aperture=0.05), P, rad, CHAMP, opacity=0.18 + 0.4 * tw, glow=1.0)
    return cv


def add_glow(cv, x, y, r, col, k, sy=1.0):
    """Additive soft light pool (elliptical gaussian) on the canvas."""
    if k <= 0.002:
        return
    x0, x1 = int(max(0, x - 3 * r)), int(min(S, x + 3 * r))
    y0, y1 = int(max(0, y - 3 * r * sy)), int(min(S, y + 3 * r * sy))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    g = np.exp(-(((xx - x) / r) ** 2 + ((yy - y) / (r * sy)) ** 2) / 2).astype(np.float32)
    cv[y0:y1, x0:x1, :3] += g[..., None] * np.asarray(col, np.float32) * k


def hline(cv, x0, x1, y, col, k, w=1.0, soft=3.0):
    ov = np.zeros((12, int(x1 - x0) + 2), np.float32)
    cv2.line(ov, (0, 6 * 8), (int((x1 - x0) * 8), 6 * 8), 1.0, max(1, int(w)), cv2.LINE_AA, shift=3)
    xs = np.linspace(0, 1, ov.shape[1], dtype=np.float32)
    ov *= np.clip(np.minimum(xs, 1 - xs) * 6, 0, 1)[None, :]
    ov = ov + cv2.GaussianBlur(ov, (0, 0), soft) * 1.5
    yy = int(y) - 6
    a, b = max(0, yy), min(S, yy + 12)
    xa, xb = max(0, int(x0)), min(S, int(x0) + ov.shape[1])
    if b <= a or xb <= xa:
        return
    cv[a:b, xa:xb, :3] += ov[a - yy:b - yy, xa - int(x0):xb - int(x0), None] * np.asarray(col, np.float32) * k


# ================================================================== scenes
# ------------------------------------------------------------------ f1: logo reveal with orbiting markets
ORBIT1 = 'PSX  •  PMEX  •  EQUITIES  •  GOLD  •  COMMODITIES  •  SILVER  •  CRUDE OIL  •  '


def f1(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    s = 1.0 + 0.035 * u / d + 0.10 * out
    cy = 520
    spin = -0.55 * u - 0.9
    rev = A.EXPO_OUT(A.clamp((u - 0.8) / 1.6))
    orbit(cv, ORBIT1, M, 21, 'hi', S / 2, cy + 20, 330 * s, spin, 'back', op=o * A.ramp(u, 0.8, 1.2), reveal=rev)
    lg = b3d('logo', 1 + max(0.0, u - 0.12) * 30)
    hero(cv, lg, S / 2, cy, s=1.08 * s, op=A.ramp(u, 0.05, 0.5) * o, blur=out * 10, glow_k=0.9)
    orbit(cv, ORBIT1, M, 21, 'w', S / 2, cy + 20, 330 * s, spin, 'front', op=o * A.ramp(u, 0.8, 1.2), reveal=rev)
    Title([('FLORET', SB, 52, 'w'), ('CAPITALS', L, 52, 'w')], S / 2, 945, gap=0.5, track=0.16).draw(
        cv, t, 1.75, d - EXIT, stagger=0.035, sweep=0.5, s=s)
    kicker(cv, 'Pakistan stock & commodity brokerage', S / 2, 1010, t, 2.2, d - EXIT, col='m', px=15)


# ------------------------------------------------------------------ f2: leading brokerage house
@functools.lru_cache(maxsize=48)
def chart_content(prog_q):
    W_, H_ = 900, 330
    p = new_card(W_, H_)
    p.text('MARKET OVERVIEW', 40, 56, M, 15, MUTED_S, 1.0, track=0.3)
    p.circle(W_ - 52, 50, 5, GOLD_S, 1.0)
    p.text('Live', W_ - 98, 56, M, 16, WHITE_S, 0.8)
    for k in range(4):
        p.line([(40, 110 + k * 54), (W_ - 40, 110 + k * 54)], 1, WHITE_S, 0.06)
    spark(p, 40, 96, W_ - 80, 200, seed=12, prog=prog_q / 40, width=3.0, drift=1.4)
    return card_img(p)


@functools.lru_cache(maxsize=4)
def pill_content(txt, logo=True):
    spr, base, adv = tsprite(txt, M, 19, 'w', 0.28)
    w = int(adv + (100 if logo else 64))
    p = new_card(w, 58)
    res = card_img(p)
    x = GP + (62 if logo else 32)
    if logo:
        blit(res, logo_flat(34), GP + 36, GP + 29)
    blit(res, spr, x - 26, GP + 29 + 7, ax=0, ay=base / spr.shape[0])
    return res, w


def f2(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[1][1]
    pc, pw = pill_content('FLORET CAPITALS')
    p = A.EXPO_OUT(A.clamp((u - 0.05) / 0.9))
    glass(cv, pw, 58, 29, S / 2, 300 - (1 - p) * 26 - out * 30, pw, op=A.ramp(u, 0.05, 0.4) * o, content=pc,
          refr=10, frost=6, cblur=(1 - p) * 4 + out * 6)
    Title([("Pakistan's", L, 84, 'w'), ('leading', L, 84, 'w')], S / 2, 470).draw(cv, t, T0 + 0.2, T0 + d - EXIT)
    Title([('Brokerage', SB, 104, 'g'), ('House', SB, 104, 'g')], S / 2, 590).draw(cv, t, T0 + 0.42, T0 + d - EXIT)
    pr = A.EXPO(A.clamp((u - 0.5) / 1.9))
    cp = A.EXPO_OUT(A.clamp((u - 0.35) / 1.2))
    glass(cv, 900, 330, 34, S / 2, 900 + 70 * (1 - cp) + 40 * out, 940, rot=(-30 + 8 * (1 - cp), 0, 0),
          op=A.ramp(u, 0.35, 0.8) * o, content=chart_content(int(round(pr * 40))), rim_col=GOLD, rim_k=0.05,
          cblur=out * 6)


# ------------------------------------------------------------------ f3: 12,000+ clients map
CITIES = [('Lahore', 74.35, 31.55), ('Karachi', 67.01, 24.86), ('Islamabad', 73.05, 33.68), ('Peshawar', 71.58, 34.01),
          ('Quetta', 67.00, 30.18), ('Multan', 71.47, 30.20), ('Faisalabad', 73.08, 31.42), ('Hyderabad', 68.37, 25.39),
          ('Sialkot', 74.53, 32.49), ('Sukkur', 68.86, 27.70), ('Gwadar', 62.33, 25.13)]


@functools.lru_cache(maxsize=1)
def pak_map():
    g = json.load(open(ASSETS + '/pak.geo.json'))['features'][0]['geometry']['coordinates'][0]
    lon = np.array([c[0] for c in g])
    lat = np.array([c[1] for c in g])
    box = (60.8, 77.9, 23.6, 37.2)
    size = 760

    def proj(lo, la):
        return ((lo - box[0]) / (box[1] - box[0]) * size, (box[3] - la) / (box[3] - box[2]) * size * 1.0)
    poly_px = np.float32([proj(a, b) for a, b in zip(lon, lat)])
    p = U.Paint(size, size, pad=20)
    cxm, cym = size * 0.62, size * 0.38
    for y in np.arange(0, size, 13):
        for x in np.arange(0, size, 13):
            if cv2.pointPolygonTest(poly_px, (float(x), float(y)), False) >= 0:
                k = math.exp(-((x - cxm) ** 2 + (y - cym) ** 2) / (2 * 260 ** 2))
                p.circle(x, y, 2.1, CHAMP_S if k > 0.5 else GOLD_S, 0.30 + 0.5 * k)
    m = p.line([tuple(q) for q in poly_px] + [tuple(poly_px[0])], 1.4, GOLD_HI_S, 0.55)
    p.glow(m, GOLD_S, 6, 0.6)
    cities = {n: proj(lo, la) for n, lo, la in CITIES}
    return half(p.result()), cities, size


def f3(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[2][1]
    spr, cities, size = pak_map()
    mp = A.EXPO_OUT(A.clamp(u / 1.2))
    mx, my, ms = S / 2 + 20, 690, 0.80 * (0.94 + 0.06 * mp) * (1 + 0.05 * out)
    blit(cv, spr, mx, my, s=ms, op=0.9 * A.ramp(u, 0, 0.6) * o, blur=(1 - mp) * 5 + out * 8)

    def scr(n):
        x, y = cities[n]
        return mx + (x + 20 - (size + 40) / 2) * ms, my + (y + 20 - (size + 40) / 2) * ms
    hub = scr('Lahore')
    ov = np.zeros((S, S), np.float32)
    for i, (n, _, _) in enumerate(CITIES):
        cu = u - 0.5 - i * 0.11
        if cu <= 0:
            continue
        x, y = scr(n)
        if n != 'Lahore':
            pr = A.EXPO_OUT(A.clamp(cu / 0.7))
            mxp, myp = (hub[0] + x) / 2, (hub[1] + y) / 2 - 0.28 * math.hypot(x - hub[0], y - hub[1])
            ts = np.linspace(0, pr, 48)
            px = (1 - ts) ** 2 * hub[0] + 2 * (1 - ts) * ts * mxp + ts ** 2 * x
            py = (1 - ts) ** 2 * hub[1] + 2 * (1 - ts) * ts * myp + ts ** 2 * y
            cv2.polylines(ov, [np.int32(np.c_[px, py] * 8)], False, 0.6, 1, cv2.LINE_AA, shift=3)
            cv2.circle(ov, (int(px[-1] * 8), int(py[-1] * 8)), 3 * 8, 1.4, -1, cv2.LINE_AA, shift=3)
        if cu > 0.5 or n == 'Lahore':
            pu = (cu - (0 if n == 'Lahore' else 0.5))
            cv2.circle(ov, (int(x * 8), int(y * 8)), int(4.5 * 8), 1.6, -1, cv2.LINE_AA, shift=3)
            rr = 6 + 36 * ((pu * 0.8) % 1.0)
            cv2.circle(ov, (int(x * 8), int(y * 8)), int(rr * 8), 0.7 * (1 - (pu * 0.8) % 1.0), 2, cv2.LINE_AA, shift=3)
    ov *= o
    cv[..., :3] += (ov[..., None] * CHAMP + cv2.GaussianBlur(ov, (0, 0), 6)[..., None] * 2.0 * GOLD)
    # Lahore label on a small glass tag
    lu = u - 0.7
    if lu > 0:
        tag, tw = pill_content('LAHORE', logo=False)
        p = A.EXPO_OUT(A.clamp(lu / 0.8))
        glass(cv, tw, 58, 29, hub[0] + 20 + tw * 0.32, hub[1] - 62 - (1 - p) * 16, tw * 0.64, op=A.ramp(lu, 0, 0.3) * o,
              content=tag, refr=8, frost=5, shadow=0.4)
    # floating 3D coins
    for i, (x, y, sc, ph) in enumerate(((165, 520, 0.56, 0), (1085, 860, 0.46, 40))):
        cn = b3d('coin', 1 + t * 30 * 0.9 + ph, pingpong=True)
        q = A.EXPO_OUT(A.clamp((u - 0.4 - i * 0.2) / 1.0))
        hero(cv, cn, x + (1 - q) * (-140 if i == 0 else 140), y + 14 * math.sin(t * 1.3 + i * 2), s=sc,
             op=q * o, blur=(1 - q) * 6 + (2.0 if i else 0) + out * 6, glow_k=0.6)
    # counter
    cu = A.ramp(u, 0.35, 2.0, A.EXPO)
    n = int(round(12000 * cu / 10.0)) * 10
    txt = f'{n:,}' + ('+' if cu > 0.98 else '')
    num, base, adv = tsprite(txt, SB, 200, 'wg', 0.0)
    pop = 1 + 0.05 * math.exp(-max(0, u - 2.05) * 6) * (u > 2.0)
    op_ = A.ramp(u, 0.3, 0.6) * o
    blit(cv, num, S / 2, 250, s=pop * (1 + 0.04 * out), op=op_, blur=(1 - A.clamp((u - 0.3) / 0.5)) * 8 + out * 10)
    kicker(cv, 'Clients across Pakistan', S / 2, 392, t, T0 + 0.6, T0 + d - EXIT, px=16)
    Title([('Active', L, 66, 'w'), ('clients', L, 66, 'w'), ('nationwide', SB, 66, 'g')], S / 2, 1118).draw(
        cv, t, T0 + 1.0, T0 + d - EXIT)


# ------------------------------------------------------------------ f4: one platform, multiple markets
TABS = ['PSX', 'PMEX', 'GOLD', 'CRUDE OIL']
ROWS = [('UBL', 'Banking', 31), ('HBL', 'Banking', 32), ('OGDCL', 'Oil & Gas', 33), ('PSO', 'Energy', 34)]
DW, DH = 820, 500


@functools.lru_cache(maxsize=1)
def _tab_x():
    xs, x = [], 44
    for tb in TABS:
        w = U._font(M, 19 * SS).getlength(tb) / SS + 40
        xs.append((x, w))
        x += w + 6
    return xs


@functools.lru_cache(maxsize=96)
def dash_base(tab, prog_q):
    p = new_card(DW, DH)
    p.text('Floret Capitals', 92, 64, SB, 22, WHITE_S, 1.0)
    p.text('Markets', 94, 86, R, 15, MUTED_S, 1.0)
    for k in range(3):
        p.circle(DW - 44 - k * 20, 58, 4.5, WHITE_S, 0.25)
    xs = _tab_x()
    p.rrect(38, 112, xs[-1][0] + xs[-1][1] - 32, 46, 23, WHITE_S, 0.06)
    p.stroke(38, 112, xs[-1][0] + xs[-1][1] - 32, 46, 23, 1, WHITE_S, 0.08)
    for k in range(4):
        p.line([(44, 210 + k * 70), (500, 210 + k * 70)], 1, WHITE_S, 0.05)
    spark(p, 44, 196, 456, 260, seed=40 + tab, prog=prog_q / 30, width=3.0, drift=1.0)
    for i, (tk, sec, sd) in enumerate(ROWS):
        y = 190 + i * 72
        p.rrect(528, y, 250, 60, 16, WHITE_S, 0.045)
        p.stroke(528, y, 250, 60, 16, 1, WHITE_S, 0.06)
        p.text(tk, 546, y + 28, SB, 19, WHITE_S, 1.0)
        p.text(sec, 546, y + 49, R, 14, MUTED_S, 1.0)
        spark(p, 658, y + 14, 100, 32, seed=sd + tab, prog=1.0, width=1.8, fill=False, dot=False)
    res = card_img(p)
    blit(res, logo_flat(40), GP + 62, GP + 70)
    return res


@functools.lru_cache(maxsize=8)
def tab_labels(tab):
    """Tab captions: the active one dark (sits on the gold pill), others muted."""
    p = new_card(DW, DH)
    for i, (x, w) in enumerate(_tab_x()):
        p.text(TABS[i], x + w / 2, 141, SB if i == tab else M, 19, DARK_S if i == tab else MUTED_S, 1.0, anchor='c')
    return card_img(p)


@functools.lru_cache(maxsize=2)
def gold_pill(w, h):
    p = U.Paint(w, h, pad=8)
    m = p.rrect(0, 0, w, h, h / 2, GOLD_S, 1.0)
    p.over(m * np.clip(1 - (p._yy - p.X(0)) / (h * SS * 0.55), 0, 1), CHAMP_S, 0.55)
    p.stroke(0.5, 0.5, w - 1, h - 1, h / 2, 1.2, hexs('fff6e0'), 0.8)
    return half(p.result())


def dash_content(pos, prog_q):
    tab = int(round(pos))
    img = dash_base(tab, prog_q).copy()
    xs = _tab_x()
    i0, fr = int(math.floor(pos)), pos - math.floor(pos)
    i1 = min(3, i0 + 1)
    x = xs[i0][0] + (xs[i1][0] - xs[i0][0]) * fr
    w = xs[i0][1] + (xs[i1][1] - xs[i0][1]) * fr
    stretch = 1 + 0.25 * math.sin(math.pi * fr)               # liquid: the pill stretches while it slides
    pl = gold_pill(int(round(w * stretch)), 38)
    blit(img, pl, GP + x + w / 2, GP + 135)
    C.over(img, tab_labels(tab))
    return img


@functools.lru_cache(maxsize=4)
def mini_content(label, seed):
    p = new_card(250, 140)
    p.text(label, 24, 46, SB, 24, WHITE_S, 1.0)
    p.text('Live market', 24, 70, R, 14, MUTED_S, 1.0)
    poly(p, [(216, 34), (226, 48), (206, 48)], GOLD_S, 1.0)
    spark(p, 24, 82, 202, 42, seed, 1.0, width=2.2)
    return card_img(p)


def f4(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[3][1]
    Title([('One', L, 74, 'w'), ('platform.', L, 74, 'w')], S / 2, 210).draw(cv, t, T0 + 0.1, T0 + d - EXIT)
    Title([('Multiple', SB, 86, 'g'), ('markets.', SB, 86, 'g')], S / 2, 312).draw(cv, t, T0 + 0.3, T0 + d - EXIT)
    sw = [0.9 + 0.55 * k for k in range(4)]
    pos = 0.0
    for k in range(1, 4):
        pos += A.EXPO(A.clamp((u - sw[k] + 0.12) / 0.38))
    tab = int(round(pos))
    t_tab = sw[tab] if tab else 0.5
    pr = A.EXPO(A.clamp((u - t_tab) / (0.9 if tab == 0 else 0.5)))
    p = A.EXPO_OUT(A.clamp((u - 0.25) / 1.1))
    for i, (lab, sd, x, y, dz) in enumerate((('PSX', 51, 215, 1040, 0.6), ('PMEX', 52, 1040, 470, 0.7))):
        q = A.EXPO_OUT(A.clamp((u - 0.7 - i * 0.2) / 1.0))
        if i == 1:                                               # the far card sits behind the dashboard
            glass(cv, 250, 140, 26, x + (1 - q) * 220, y + 10 * math.sin(u * 1.5 + i), 250, rot=(4, -20, 0), dz=dz,
                  op=A.ramp(q, 0, 0.4) * o, content=mini_content(lab, sd), refr=12, cblur=1.0 + out * 6)
    glass(cv, DW, DH, 36, S / 2, 770 + (1 - p) * 120 + out * 40, 860, rot=(12 * (1 - p) + 6, -14 + 9 * p + 3 * u / d, 0),
          op=A.ramp(u, 0.25, 0.6) * o, content=dash_content(pos, int(round(pr * 30))), refr=18, rim_col=GOLD,
          rim_k=0.10, cblur=out * 6)
    q = A.EXPO_OUT(A.clamp((u - 0.7) / 1.0))
    glass(cv, 250, 140, 26, 215 - (1 - q) * 220, 1040 + 10 * math.sin(u * 1.5), 250, rot=(4, 20, 0), dz=-0.5,
          op=A.ramp(q, 0, 0.4) * o, content=mini_content('PSX', 51), refr=12, cblur=out * 6)


# ------------------------------------------------------------------ f5: PSX x PMEX
@functools.lru_cache(maxsize=4)
def exch_content(label):
    W_, H_ = 360, 300
    p = new_card(W_, H_)
    if label == 'PMEX':
        p.text('PMEX', W_ / 2, 236, SB, 40, WHITE_S, 1.0, anchor='c', track=0.06)
    res = card_img(p)
    if label == 'PSX':
        lg = C.load(ASSETS + '/psx_logo_full.png')
        blit(res, lg, GP + W_ / 2, GP + H_ / 2 + 4, s=(H_ - 60) / lg.shape[0])
    else:
        lg = C.load(ASSETS + '/pmex_emblem.png')
        blit(res, lg, GP + W_ / 2, GP + 118, s=150 / lg.shape[0])
    return res


@functools.lru_cache(maxsize=4)
def check_content(word):
    spr, base, adv = tsprite(word, M, 30, 'w', 0.0)
    w = int(adv + 96)
    p = new_card(w, 70)
    p.circle(38, 35, 17, GOLD_S, 1.0)
    p.line([(30, 35), (36, 42), (47, 28)], 3.2, DARK_S, 1.0)
    res = card_img(p)
    blit(res, spr, GP + 68 - 26, GP + 35 + 11, ax=0, ay=base / spr.shape[0])
    return res, w


def f5(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[4][1]
    kicker(cv, 'Access both exchanges', S / 2, 188, t, T0 + 0.1, T0 + d - EXIT, px=16)
    for i, (lab, sub, col) in enumerate((('PSX', 'Pakistan Stock Exchange', BL_GREEN),
                                         ('PMEX', 'Pakistan Mercantile Exchange', BL_RED))):
        p = A.EXPO_OUT(A.clamp((u - 0.15) / 1.0))
        sgn = -1 if i == 0 else 1
        x = S / 2 + sgn * (232 + (1 - p) * 330)
        add_glow(cv, x, 470, 150, col, 0.35 * A.ramp(u, 0.15, 0.8) * o)
        glass(cv, 360, 300, 40, x, 470 - out * 30, 360, rot=(0, -sgn * 24 * (1 - p) - sgn * 9, 0),
              op=A.ramp(u, 0.15, 0.5) * o, content=exch_content(lab), refr=20, cblur=out * 6, rim_col=col, rim_k=0.05)
        Title([(sub, R, 19, 'm')], x, 672).draw(cv, t, T0 + 0.6 + i * 0.1, T0 + d - EXIT, stagger=0.01, sweep=None)
    xu = u - 0.75
    if xu > 0:
        xs, base, _ = tsprite('×', XL, 110, 'g')
        s = 1 + 0.5 * math.exp(-xu * 7)
        blit(cv, xs, S / 2, 470, s=s, op=A.ramp(xu, 0, 0.15) * o)
        add_glow(cv, S / 2, 470, 120, BL_GOLD, 1.2 * math.exp(-xu * 4) * o, sy=0.5)
    for i, w in enumerate(('Regulated.', 'Trusted.', 'Connected.')):
        cu = u - 1.0 - i * 0.22
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.8))
        chp, cw = check_content(w)
        x = S / 2 + (i - 1) * 330
        glass(cv, cw, 70, 35, x, 860 + (1 - p) * 50 - out * 30, cw, op=A.ramp(cu, 0, 0.3) * o, content=chp, refr=10,
              frost=6, cblur=(1 - p) * 5 + out * 6)
    lu = A.EXPO_OUT(A.clamp((u - 1.5) / 1.0))
    if lu > 0:
        hline(cv, S / 2 - 540 * lu, S / 2 + 540 * lu, 960, GOLD, 0.8 * o)


# ------------------------------------------------------------------ f6: commodities carousel
OBJ3D = dict(gold='goldbar', silver='silverbar', oil='barrel', more='coin')
KINDS = ['gold', 'silver', 'oil', 'more']
KNAME = dict(gold='Gold', silver='Silver', oil='Crude Oil', more='And more')
KGLOW = dict(gold=BL_GOLD, silver=BL_ICE, oil=BL_AMBER, more=BL_GOLD)
CW, CH = 300, 400


@functools.lru_cache(maxsize=8)
def com_content(kind):
    p = new_card(CW, CH)
    p.text(KNAME[kind], 30, 300, SB, 32, WHITE_S, 1.0)
    p.text('Traded on PMEX', 30, 328, R, 15, MUTED_S, 1.0)
    spark(p, 30, 346, 240, 34, {'gold': 61, 'silver': 62, 'oil': 63}.get(kind, 64), 1.0, width=2.2,
          col=GOLD_S if kind != 'silver' else hexs('cfd8e6'), fill=False, dot=False)
    return card_img(p)


def f6(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[5][1]
    starts = [0.2, 0.85, 1.5, 2.2]
    cur = max(0, sum(1 for s0 in starts if u >= s0) - 1)
    kicker(cv, 'Trade commodities', S / 2, 170, t, T0 + 0.1, T0 + d - EXIT, px=16)
    # rolling headline: current word large, previous rolls up and out
    for i, s0 in enumerate(starts):
        end = starts[i + 1] if i < 3 else 99
        if u < s0 or u > end + 0.45:
            continue
        kind = KINDS[i]
        Title([(KNAME[kind] + '.', SB, 104, 'g' if kind != 'silver' else 's')], S / 2, 312).draw(
            cv, t, T0 + s0 + (0.14 if i else 0), T0 + min(end, d - EXIT), stagger=0.02, sweep=0.3)
    # carousel: focus slides with an expo glide; ends pulled back to show all four
    foc = 0.0
    for k in range(1, 4):
        foc += A.EXPO(A.clamp((u - starts[k] + 0.05) / 0.55))
    allv = A.EXPO(A.clamp((u - 2.95) / 0.8))
    foc = foc * (1 - allv) + 1.5 * allv
    spacing = 330 * (1 - allv) + 262 * allv
    order = sorted(range(4), key=lambda i: -abs(i - foc))
    for i in order:
        kind = KINDS[i]
        cu = u - 0.05 - i * 0.12
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.9))
        dd = i - foc
        x = S / 2 + dd * spacing + (1 - p) * 300
        focus = math.exp(-dd * dd * 2.2)
        sc = (0.80 + 0.20 * focus) * (1 - 0.18 * allv) + 0.0
        ry = -max(-1, min(1, dd)) * 26 * (1 - allv)
        dz = (1 - focus) * 0.9 * (1 - allv)
        y = 720
        co = A.ramp(cu, 0, 0.35) * o * (0.55 + 0.45 * max(focus, allv))
        add_glow(cv, x, y - 40, 170 * sc, KGLOW[kind], (0.15 + 0.35 * max(focus, allv * 0.6)) * co)
        glass(cv, CW, CH, 40, x, y, CW * sc, rot=(0, ry, 0), dz=dz, op=co, content=com_content(kind), refr=18,
              cblur=(1 - focus) * (1 - allv) * 2.0 + out * 6)
        ob = b3d(OBJ3D[kind], 1 + (t - T0 - starts[i]) * 30 * 1.1, pingpong=True)
        osc = (0.86 if kind != 'more' else 0.62) * sc * (0.75 + 0.25 * A.BACK_OUT(A.clamp(cu / 0.7))) * (4.0 / (4.0 + dz))
        hero(cv, ob, x, y - 70 * sc + 6 * math.sin(t * 1.4 + i), s=osc, op=co, blur=(1 - focus) * (1 - allv) * 1.5 + out * 6,
             glow=KGLOW[kind], glow_k=0.6 * max(focus, allv))


# ------------------------------------------------------------------ f7: global commodities -> PSX companies
@functools.lru_cache(maxsize=1)
def _globe_pts():
    n = 1600
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.c_[np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)]


def globe(cv, cx, cy, r, ang, op):
    P = _globe_pts()
    c, s = math.cos(ang), math.sin(ang)
    x = P[:, 0] * c + P[:, 2] * s
    z = -P[:, 0] * s + P[:, 2] * c
    y = P[:, 1]
    tilt = math.radians(18)
    y2 = y * math.cos(tilt) - z * math.sin(tilt)
    z2 = y * math.sin(tilt) + z * math.cos(tilt)
    ov = np.zeros((S, S), np.float32)
    for xi, yi, zi in zip(x, y2, z2):
        b = 0.12 + 0.88 * max(zi, 0) ** 1.3
        cv2.circle(ov, (int((cx + xi * r) * 8), int((cy - yi * r) * 8)), int((1.2 + 1.0 * max(zi, 0)) * 8), float(b),
                   -1, cv2.LINE_AA, shift=3)
    ov *= op
    cv[..., :3] += ov[..., None] * CHAMP * 0.9 + cv2.GaussianBlur(ov, (0, 0), 4)[..., None] * GOLD * 0.7
    rim = np.zeros((S, S), np.float32)
    cv2.circle(rim, (int(cx * 8), int(cy * 8)), int(r * 8), 1.0, 2, cv2.LINE_AA, shift=3)
    cv[..., :3] += (cv2.GaussianBlur(rim, (0, 0), 3)[..., None] * BL_ICE * 0.5 +
                    cv2.GaussianBlur(rim, (0, 0), 16)[..., None] * BL_BLUE * 1.6) * op


@functools.lru_cache(maxsize=8)
def ticker_content(tk, sec, seed):
    p = new_card(320, 120)
    p.rrect(22, 26, 54, 54, 16, GOLD_S, 0.14)
    p.stroke(22, 26, 54, 54, 16, 1, GOLD_S, 0.4)
    p.text(tk[0], 49, 63, SB, 26, GOLD_HI_S, 1.0, anchor='c')
    p.text(tk, 92, 52, SB, 25, WHITE_S, 1.0)
    p.text(sec, 92, 76, R, 15, MUTED_S, 1.0)
    poly(p, [(290, 40), (300, 54), (280, 54)], GOLD_S, 1.0)
    spark(p, 196, 64, 84, 30, seed, 1.0, width=2.0, fill=False, dot=False)
    return card_img(p)


def f7(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[6][1]
    Title([('From', L, 56, 'w'), ('global', L, 56, 'w'), ('commodities', SB, 56, 'g')], S / 2, 190).draw(
        cv, t, T0 + 0.1, T0 + d - EXIT, stagger=0.018)
    Title([('to', L, 56, 'w'), ("Pakistan's", L, 56, 'w'), ('leading', L, 56, 'w'), ('companies', SB, 56, 'g')], S / 2,
          262).draw(cv, t, T0 + 0.35, T0 + d - EXIT, stagger=0.018)
    gp = A.EXPO_OUT(A.clamp((u - 0.2) / 1.1))
    gx, gy, gr = 360 - (1 - gp) * 60, 700, 250 * (0.85 + 0.15 * gp) * (1 + 0.05 * out)
    globe(cv, gx, gy, gr, u * 0.45 + 0.5, A.ramp(u, 0.2, 0.7) * o)
    for i, (tk, sec, sd) in enumerate(ROWS):
        cu = u - 1.0 - i * 0.16
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.9))
        x = 860
        y = 470 + i * 152
        ov = np.zeros((S, S), np.float32)                       # link from the globe to each card
        x0, y0 = gx + gr * 0.85, gy + (i - 1.5) * 85
        x1, y1 = x + (1 - p) * 220 - 170, y
        ts = np.linspace(0, p, 40)
        px = x0 + (x1 - x0) * ts
        py = y0 + (y1 - y0) * (3 * ts ** 2 - 2 * ts ** 3)
        cv2.polylines(ov, [np.int32(np.c_[px, py] * 8)], False, 0.6, 1, cv2.LINE_AA, shift=3)
        cv[..., :3] += (ov + cv2.GaussianBlur(ov, (0, 0), 3))[..., None] * GOLD * o
        glass(cv, 320, 120, 30, x + (1 - p) * 220, y, 330, rot=(0, -16, 0), dz=-0.12 * i, op=A.ramp(cu, 0, 0.3) * o,
              content=ticker_content(tk, sec, sd), refr=14, cblur=out * 6)
    bu = A.EXPO_OUT(A.clamp((u - 1.6) / 0.8))
    if bu > 0:
        band, base, adv = tsprite('UBL      HBL      OGDCL      PSO      KSE-100      ', M, 22, 'm', 0.3)
        off = (u * 90) % adv
        for k in range(-1, 3):
            blit(cv, band, k * adv - off, 1150, ax=0, op=bu * o * 0.8)


# ------------------------------------------------------------------ f8: insights / decisions / trust
ORBIT8 = 'EXPERT INSIGHTS  •  SMARTER DECISIONS  •  BUILT ON TRUST  •  '


def f8(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[7][1]
    spin = 0.5 * u + 2.2
    cy = 445
    q = A.EXPO_OUT(A.clamp(u / 1.0))
    rev = A.EXPO_OUT(A.clamp((u - 0.25) / 1.4))
    s = (0.86 + 0.14 * q) * (1 + 0.06 * out)
    orbit(cv, ORBIT8, M, 26, 'hi', S / 2, cy + 30, 370 * s, spin, 'back', tilt=64, roll=12, op=o, reveal=rev)
    sh = b3d('shield', 1 + max(0.0, u) * 30 * 0.95)
    hero(cv, sh, S / 2, cy + 8 * math.sin(u * 1.6), s=1.55 * s, op=A.ramp(u, 0, 0.4) * o, blur=(1 - q) * 6 + out * 8,
         glow_k=1.2)
    orbit(cv, ORBIT8, M, 26, 'w', S / 2, cy + 30, 370 * s, spin, 'front', tilt=64, roll=12, op=o, reveal=rev)
    rows = [('Expert', 'insights.'), ('Smarter', 'decisions.'), ('Built on', 'trust.')]
    for i, (a, b) in enumerate(rows):
        Title([(a, L, 60, 'w'), (b, SB, 60, 'g')], S / 2, 905 + i * 84).draw(cv, t, T0 + 0.35 + i * 0.5, T0 + d - EXIT,
                                                                          stagger=0.02)


# ------------------------------------------------------------------ f9: more markets tunnel
@functools.lru_cache(maxsize=16)
def tile(i):
    labels = [('PSX', 'Equities'), ('PMEX', 'Commodities'), ('Gold', 'Metals'), ('Silver', 'Metals'), ('Crude Oil', 'Energy'),
              ('UBL', 'Banking'), ('HBL', 'Banking'), ('OGDCL', 'Oil & Gas'), ('PSO', 'Energy'), ('KSE-100', 'Index')]
    lab, sub = labels[i % len(labels)]
    p = U.Paint(280, 170, pad=10)
    p.rrect(0, 0, 280, 170, 26, hexs('2a2218'), 0.5)
    p.over(np.clip(0.5 - p.sdf_rrect(0, 0, 280, 170, 26), 0, 1) * np.clip(1 - (p._yy - p.X(0)) / (170 * SS * 0.6), 0, 1),
           WHITE_S, 0.07)
    p.stroke(0, 0, 280, 170, 26, 1.6, CHAMP_S, 0.7)
    p.text(lab, 24, 48, SB, 26, WHITE_S, 1.0)
    p.text(sub, 24, 72, R, 15, MUTED_S, 1.0)
    spark(p, 24, 94, 232, 52, 80 + i, 1.0, width=2.2, dot=False)
    return p.result()


def f9(cv, t, u, d):
    out = exit_p(u, d)
    o = 1 - out
    T0 = FRAMES[8][1]
    z0 = u * 5.0 + A.EXPO_IN(A.clamp(u / d)) * 4
    cam = C.Cam(0.15 * math.sin(u * 0.8), 0, z0, roll=4 * math.sin(u * 0.6), F=F, focus=z0 + 4.0, aperture=0.008)
    frost = cv2.GaussianBlur(cv, (0, 0), 14)
    items = []
    for k in range(40):
        z = 3 + k * 1.15
        for j, (x, y, ry, rx) in enumerate(((-2.0, 0.75, 58, 0), (-2.0, -0.35, 58, 0), (2.0, 0.75, -58, 0), (2.0, -0.35, -58, 0),
                                            (-0.8, -1.4, 0, -70), (0.8, -1.4, 0, -70))):
            items.append((z, x, y, ry, rx, (k * 7 + j * 3) % 10))
    for z, x, y, ry, rx, ti in sorted(items, key=lambda q: -q[0]):
        dz = z - z0
        if dz < 0.4 or dz > 22:
            continue
        fade = A.clamp((22 - dz) / 6) * A.clamp((dz - 0.4) / 1.2)
        try:
            C.draw_img3d(cv, tile(ti), cam, (x, y, z), (1.4, 0.85), (rx, ry, 0), opacity=fade * o * 0.95,
                         glass=(frost, 0.8))
        except cv2.error:
            pass
    fly = [('coin', -1.3, 0.7, 5.5), ('goldbar', 1.4, -0.6, 7.0), ('coin', 1.1, 0.9, 9.0), ('silverbar', -1.2, -0.8, 10.5),
           ('coin', -0.5, 1.2, 12.5), ('goldbar', 0.6, -1.1, 14.0), ('barrel', -1.5, 0.1, 16.0), ('coin', 1.5, 0.2, 18.0)]
    for k, (job, x, y, z) in sorted(enumerate(fly), key=lambda q: -q[1][3]):
        dz = z - z0
        if dz < 0.6 or dz > 14:
            continue
        ob = b3d(job, 1 + t * 30 + k * 11, pingpong=True)
        if ob is None:
            continue
        fade = A.clamp((14 - dz) / 4) * A.clamp((dz - 0.6) / 0.8)
        try:
            C.draw_img3d(cv, ob, cam, (x, y, z), (0.75, 0.75), (0, 0, 15 * k), opacity=fade * o)
        except cv2.error:
            pass
    yy, xx = np.ogrid[0:S, 0:S]                                 # dark core behind the type
    g = np.exp(-(((xx - S / 2) / 520.0) ** 2 + ((yy - 600) / 190.0) ** 2)).astype(np.float32)
    cv[..., :3] *= 1 - 0.55 * g[..., None] * A.ramp(u, 0.1, 0.6)
    Title([('More', L, 92, 'w'), ('markets.', L, 92, 'w')], S / 2, 570).draw(cv, t, T0 + 0.25, T0 + d - EXIT)
    Title([('More', SB, 100, 'g'), ('possibilities.', SB, 100, 'g')], S / 2, 685).draw(cv, t, T0 + 0.5, T0 + d - EXIT)


# ------------------------------------------------------------------ f10: THINK BIGGER. THINK FLORET.
def horizon(cv, k, y0=1130):
    """Planet-edge sunrise: a thin bright arc with a gold atmosphere glowing above it."""
    if k <= 0.003:
        return
    yy, xx = np.ogrid[0:S, 0:S]
    Rr = 2600.0
    d = np.sqrt(((xx - S / 2) * 1.0) ** 2 + (yy - (y0 + Rr)) ** 2) - Rr     # <0 inside the planet
    d = d.astype(np.float32)
    edge = np.exp(-(d / 2.2) ** 2)
    atm = np.exp(-np.clip(d, 0, None) / 120.0) * (d > -1)
    cv[..., :3] *= (1 - np.clip(-d / 6, 0, 1) * 0.9 * k)[..., None]
    cv[..., :3] += (edge[..., None] * CHAMP * 1.6 + atm[..., None] * BL_GOLD * 0.30) * k


def f10(cv, t, u, d):
    T0 = FRAMES[9][1]
    T_LOGO = 2.05
    q = A.EXPO_IN(A.clamp((u - T_LOGO + 0.35) / 0.45))
    for k, (segs, y, t_in) in enumerate((([('Think', L, 118, 'w'), ('bigger.', L, 118, 'w')], 545, 0.1),
                                         ([('Think', SB, 118, 'g'), ('Floret.', SB, 118, 'g')], 690, 0.62))):
        ku = u - t_in
        if ku > 0:
            Title(segs, S / 2, y - q * 90).draw(cv, t, T0 + t_in, T0 + T_LOGO - 0.35, stagger=0.018, dur=0.6, sweep=0.25)
            add_glow(cv, S / 2, y - 40, 260, BL_GOLD, 0.5 * math.exp(-ku * 5), sy=0.35)
    horizon(cv, A.ramp(u, T_LOGO - 0.1, T_LOGO + 1.3, A.EXPO), 1150)
    lu = u - T_LOGO
    if lu > 0:
        lg = b3d('logo', 1 + lu * 30 * 1.25)
        hero(cv, lg, S / 2, 455, s=1.0 + 0.02 * lu / 3, op=A.ramp(lu, 0, 0.3), glow_k=1.0, reflect=0.0)
        Title([('FLORET', SB, 60, 'w'), ('CAPITALS', L, 60, 'w')], S / 2, 800, gap=0.5, track=0.16).draw(
            cv, t, T0 + T_LOGO + 0.55, stagger=0.03, sweep=0.9)
        su = lu - 1.1
        if su > 0:
            p = A.EXPO_OUT(A.clamp(su / 0.9))
            pc, pw = pill_content('floretcapitals.com', logo=False)
            glass(cv, pw, 58, 29, S / 2, 900 + (1 - p) * 22, pw, op=A.ramp(su, 0, 0.4), content=pc, refr=10, frost=6,
                  cblur=(1 - p) * 4, rim_col=GOLD, rim_k=0.06)
    cv *= 1 - A.ramp(u, d - 0.35, d, A.EASY)


DRAW = dict(f1=f1, f2=f2, f3=f3, f4=f4, f5=f5, f6=f6, f7=f7, f8=f8, f9=f9, f10=f10)


# ------------------------------------------------------------------ camera, transitions, frame
def cam2d(t):
    """Global camera on the whole frame: slow push inside each scene + soft punch at each cut + drift."""
    z = 1.02
    for name, a, b in FRAMES:
        if a <= t < b:
            z = 1.02 + 0.04 * A.SMOOTH(A.clamp((t - a) / (b - a)))
    for name, a, b in FRAMES[1:]:
        dt = t - a
        if -0.3 < dt < 0.8:
            z *= 1 + 0.05 * math.exp(-max(dt, 0) * 5) * (dt > 0) - 0.03 * A.clamp((dt + 0.3) / 0.3) * (dt <= 0)
    dx = 6 * A.wiggle(t, 0.2, 1, 3)
    dy = 5 * A.wiggle(t, 0.17, 1, 4)
    rot = 0.2 * A.wiggle(t, 0.15, 1, 5)
    return dx, dy, z, rot


def draw(t):
    BOOST.clear()
    fg_scene = [(n, a, b) for n, a, b in FRAMES if a <= t < b]
    # scenes set their bloom boosts before the background is lit: run a cheap pre-pass of the boost logic
    cv = None
    for name, a, b in fg_scene:
        _boost(name, t - a, b - a)
    cv = background(t)
    for name, a, b in fg_scene:
        DRAW[name](cv, t, t - a, b - a)
    dx, dy, z, rot = cam2d(t)
    Mx = cv2.getRotationMatrix2D((S / 2, S / 2), rot, z)
    Mx[0, 2] += dx
    Mx[1, 2] += dy
    cv = cv2.warpAffine(cv, Mx, (S, S), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # cut accents: soft radial zoom blur + a warm light leak flash
    for name, a, b in FRAMES[1:]:
        dt = t - a
        if abs(dt) < 0.3:
            bump = math.exp(-(dt / 0.11) ** 2)
            cv = radial(cv, 0.07 * bump)
            add_glow(cv, S * 0.82, S * 0.2, 520, BL_AMBER, 0.22 * bump)
    return cv


def _boost(name, u, d):
    if name == 'f1':
        BOOST['f1'] = A.ramp(u, 0.0, 1.4) * (1 + 0.6 * math.exp(-max(0, u - 0.9) * 2.5) * (u > 0.9))
    elif name == 'f8':
        BOOST['f8'] = 1 + 0.5 * math.exp(-max(0, u - 0.2) * 2.0)
    elif name == 'f10':
        BOOST['f10'] = 0.6 + 0.6 * A.ramp(u, 2.05 - 0.2, 2.05 + 1.0)


def radial(img, amount, n=6):
    if amount < 0.004:
        return img
    acc = img.copy()
    for i in range(1, n):
        s = 1 + amount * i / n
        Mx = np.float32([[s, 0, (1 - s) * S / 2], [0, s, (1 - s) * S / 2]])
        acc += cv2.warpAffine(img, Mx, (S, S), borderMode=cv2.BORDER_REFLECT)
    return acc / n


@functools.lru_cache(maxsize=1)
def _vig():
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
    return np.clip(1 - 0.75 * np.clip(r - 0.35, 0, None) ** 1.5, 0, 1)[..., None]


def finish(f, t):
    f = C.deep_glow(f, 0.55, 0.32, (1.0, 0.78, 0.52), sat_boost=0.7)
    f = C.halation(f, 0.05, threshold=0.65)
    f = C.anamorphic(f, 0.9, 0.05, (1.0, 0.72, 0.4), 0.45)
    f = C.chroma_fringe(f, 1.4)
    x = f[..., :3] / (1 + f[..., :3] * 0.22)
    s = C.to_srgb(np.clip(x * 1.08, 0, 1))
    s = np.clip((s - 0.018) / 0.982, 0, 1)
    s = s * s * (3 - 2 * s) * 0.22 + s * 0.78
    s = s * _vig()
    return C.grain(s, t, 0.014, 1.2)


def samples_for(t):
    for name, a, b in FRAMES[1:]:
        if abs(t - a) < 0.3:
            return 4
    for name, a, b in FRAMES:
        if a <= t < b:
            u = t - a
            if u < 0.9 or b - t < 0.45:
                return 3
    return 2


def render_frame(i):
    t = i / FPS
    return finish(C.render_frame(draw, t, samples_for(t)), t)


def still(ts):
    os.makedirs(WORK + '/stills', exist_ok=True)
    for t in ts:
        s = render_frame(int(round(t * FPS)))
        cv2.imwrite(f'{WORK}/stills/t{t:06.2f}.jpg', (s[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])


def _chunk(args):
    ci, i0, i1 = args
    path = f'{WORK}/chunks/c{ci:03d}.mp4'
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{S}x{S}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                          '-x264-params', 'rc-lookahead=8:sync-lookahead=0', '-threads', '2', '-pix_fmt', 'yuv420p',
                          path + '.part.mp4'], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        s = render_frame(i)
        p.stdin.write((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    os.replace(path + '.part.mp4', path)
    return path


def render(workers=4, chunk=60):
    os.makedirs(WORK + '/chunks', exist_ok=True)
    jobs = [(ci, i0, min(NF, i0 + chunk)) for ci, i0 in enumerate(range(0, NF, chunk))]
    with Pool(workers) as pool:
        paths = sorted(pool.imap_unordered(_chunk, jobs))
    with open(WORK + '/chunks/list.txt', 'w') as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', WORK + '/chunks/list.txt', '-c', 'copy',
                    WORK + '/video.mp4'], check=True)
    return WORK + '/video.mp4'


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'still'
    if cmd == 'still':
        still([float(x) for x in sys.argv[2:]])
    elif cmd == 'render':
        print(render(int(sys.argv[2]) if len(sys.argv) > 2 else 4))
