"""Floret Capitals - cinematic SaaS motion-graphics spot (Lahore concert sponsorship), 1248x1248 @ 60 fps.

Gold #e49f38 / black / white, Rubik (the floretcapitals.com brand font). Glass UI cards placed as 3D planes,
kinetic type that rises through a slot mask, gold deep glow, a perspective data grid, gold dust, camera
pushes and true shutter motion blur.

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


def hexs(h):
    return np.float32([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


# sRGB (for Paint) and linear (for the canvas) brand colours
GOLD_S, GOLD_HI_S, GOLD_LO_S = hexs('e49f38'), hexs('f9d184'), hexs('a8661b')
WHITE_S, MUTED_S, SILVER_S, DARK_S = hexs('f6f4f0'), hexs('8d8a85'), hexs('dfe3ea'), hexs('0b0a09')
GOLD, GOLD_HI, GOLD_LO = C.to_lin(GOLD_S), C.to_lin(GOLD_HI_S), C.to_lin(GOLD_LO_S)
WHITE, MUTED, SILVER = C.to_lin(WHITE_S), C.to_lin(MUTED_S), C.to_lin(SILVER_S)

# ------------------------------------------------------------------ timeline (s)
FRAMES = [('f1', 0.0, 3.8), ('f2', 3.8, 6.8), ('f3', 6.8, 10.2), ('f4', 10.2, 13.4), ('f5', 13.4, 16.6),
          ('f6', 16.6, 20.6), ('f7', 20.6, 24.4), ('f8', 24.4, 27.8), ('f9', 27.8, 30.6), ('f10', 30.6, 36.0)]
DUR = FRAMES[-1][2]
NF = int(round(DUR * FPS))
OVL = 0.35                                    # each frame keeps drawing this long past its end (exit anim)


# ------------------------------------------------------------------ sprites
@functools.lru_cache(maxsize=1024)
def tsprite(txt, font, px, col='w', track=0.0):
    """Text -> premultiplied linear RGBA sprite (padded), baseline y, advance width."""
    m, base = U.text_mask(txt, font, px, track)
    m = cv2.resize(m, (max(1, m.shape[1] // SS), max(1, m.shape[0] // SS)), interpolation=cv2.INTER_AREA)
    P = 26
    m = np.pad(m, P)
    h = m.shape[0]
    base = base / SS + P
    if col in ('g', 's'):
        top, bot = base - px * 0.75, base
        v = np.clip((np.arange(h, dtype=np.float32) - top) / max(bot - top, 1), 0, 1)[:, None, None]
        hi, mid, lo = (GOLD_HI, GOLD, GOLD_LO) if col == 'g' else (C.to_lin(hexs('ffffff')), SILVER, C.to_lin(hexs('9aa1ab')))
        c = np.where(v < 0.5, hi + (mid - hi) * (v / 0.5), mid + (lo - mid) * ((v - 0.5) / 0.5))
    else:
        c = {'w': WHITE, 'm': MUTED, 'gold': GOLD}[col][None, None]
    rgb = c * m[..., None]
    return np.dstack([rgb, m]).astype(np.float32), base, m.shape[1] - 2 * P


def blur_spr(spr, sig):
    return cv2.GaussianBlur(spr, (0, 0), sig) if sig >= 0.6 else spr


def blit(cv, spr, x, y, ax=0.5, ay=0.5, s=1.0, op=1.0, rot=0.0, blur=0.0, clip=None, mode='over'):
    """Composite a premultiplied RGBA sprite so its (ax, ay) fraction lands on (x, y). clip=(y0, y1) canvas rows."""
    if op <= 0.003 or s <= 0.01:
        return
    spr = blur_spr(spr, blur)
    h, w = spr.shape[:2]
    M = cv2.getRotationMatrix2D((w * ax, h * ay), rot, s)
    M[0, 2] += x - w * ax
    M[1, 2] += y - h * ay
    cs = np.float32([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]]) @ M.T
    x0, y0 = np.floor(cs.min(0)).astype(int)
    x1, y1 = np.ceil(cs.max(0)).astype(int) + 1
    if clip is not None:
        y0, y1 = max(y0, int(clip[0])), min(y1, int(clip[1]))
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
    if reg.shape[2] == 4:
        reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)


def put3d(cv, img, cx, cy, wpx, rot=(0, 0, 0), depth=4.0, op=1.0, blur=0.0, dz=0.0):
    """Place an RGBA card as a 3D plane whose centre lands on screen (cx, cy) and is wpx wide at rest."""
    cam = C.Cam(0, 0, 0, F=F)
    k = depth / F
    h = img.shape[0] / img.shape[1] * wpx
    C.draw_img3d(cv, img, cam, ((cx - S / 2) * k, -(cy - S / 2) * k, depth + dz), (wpx * k, h * k), tuple(rot),
                 opacity=op, blur=blur)


def half(img):
    """Paint results are supersampled (SS x): bring them to 1x for 2D blits."""
    return cv2.resize(img, (img.shape[1] // SS, img.shape[0] // SS), interpolation=cv2.INTER_AREA)


def poly(p, pts, col, op=1.0):
    m = np.zeros((p.Hp, p.Wp), np.float32)
    cv2.fillPoly(m, [np.int32([[p.X(x) * 8, p.X(y) * 8] for x, y in pts])], 1.0, cv2.LINE_AA, shift=3)
    p.over(m, col, op)
    return m


def gcard(p, x, y, w, h, r=26, op=1.0, k=1.0):
    """Dark glass card with a gold-lit hairline edge."""
    return U.glass_panel(p, x, y, w, h, r, edge=(GOLD_S * 1.05, GOLD_S * 0.25), op=op, edge_k=0.55 * k)


def walk(seed, n=48, drift=0.6, vol=1.0):
    rng = np.random.default_rng(seed)
    v = np.cumsum(rng.normal(drift / n * 3, vol / math.sqrt(n), n))
    v = v - v.min()
    return v / max(v.max(), 1e-6)


def spark(p, x, y, w, h, seed, prog=1.0, col=GOLD_S, width=2.4, fill=True, drift=0.6):
    v = walk(seed, drift=drift)
    n = max(2, int(round(len(v) * prog)))
    pts = [(x + w * i / (len(v) - 1), y + h * (1 - v[i])) for i in range(n)]
    if fill and n > 2:
        m = poly(p, pts + [(pts[-1][0], y + h), (x, y + h)], col, 0.0)
        g = np.clip(1 - (p._yy - p.X(y)) / (h * SS), 0, 1)
        p.add(m * g, col, 0.22)
    p.line(pts, width, col, 1.0)
    p.circle(pts[-1][0], pts[-1][1], width * 1.6, WHITE_S, 1.0)
    return pts[-1]


# ------------------------------------------------------------------ Blender 3D elements (b3d.py)
B3D_N = dict(logo=120, goldbar=96, silverbar=96, barrel=96, coin=96, shield=96)
B3D_SCALE = dict(logo=0.6)


def b3d(job, fpos, pingpong=False):
    """Premultiplied linear RGBA of a Blender element at fractional 30 fps frame fpos (1-based), frame-blended;
    None if that sequence has not been rendered."""
    n = B3D_N[job]
    if pingpong:
        fpos = 1 + abs(((fpos - 1) % (2 * (n - 1))) - (n - 1))
    fpos = min(max(fpos, 1.0), float(n))
    f0 = int(math.floor(fpos))
    w = fpos - f0
    paths = [f'{ROOT}/b3d/{job}/{f:04d}.png' for f in (f0, min(n, f0 + 1))]
    if not all(os.path.exists(p) for p in paths):
        return None
    sc = B3D_SCALE.get(job, 0.5)
    a = C.load(paths[0], sc)
    if w < 0.02 or paths[1] == paths[0]:
        return a
    return a * (1 - w) + C.load(paths[1], sc) * w


def with_reflection(spr, k=0.22, length=0.35):
    """Glossy-floor reflection under a sprite (flipped, fading)."""
    h = spr.shape[0]
    ys, xs = np.where(spr[..., 3] > 0.05)
    if len(ys) == 0:
        return spr
    bottom = ys.max()
    L = int(h * length)
    ref = spr[max(0, bottom - L):bottom + 1][::-1].copy()
    fade = np.linspace(1, 0, ref.shape[0], dtype=np.float32)[:, None, None] ** 1.6 * k
    ref = cv2.GaussianBlur(ref * fade, (0, 0), 2.5)
    out = np.zeros((max(h, bottom + 1 + ref.shape[0]) + 4, spr.shape[1], 4), np.float32)
    out[:h] = spr
    seg = out[bottom + 3:bottom + 3 + ref.shape[0]]
    C.over(seg, ref[:seg.shape[0]])
    return out


# ------------------------------------------------------------------ logo
@functools.lru_cache(maxsize=1)
def logo_parts():
    im = cv2.imread(ASSETS + '/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3]
    rgb = im[..., 2::-1]
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = ys.min() - 6, ys.max() + 7, xs.min() - 6, xs.max() + 7
    a, rgb = a[y0:y1, x0:x1], rgb[y0:y1, x0:x1]
    sat = rgb.max(2) - rgb.min(2)
    gold = a * (sat > 0.2)
    arrow = a * (sat <= 0.2)
    n, lab, st, _ = cv2.connectedComponentsWithStats((gold > 0.5).astype(np.uint8))
    idx = sorted(range(1, n), key=lambda i: -st[i, 4])[:4]
    idx.sort(key=lambda i: st[i, 0])
    bars = []
    for i in idx:
        reg = cv2.dilate((lab == i).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
        bars.append((gold * reg, st[i, 1], st[i, 1] + st[i, 3]))
    return bars, arrow


@functools.lru_cache(maxsize=8)
def logo_layers(width):
    """Shaded logo pieces at `width` px: bar sprites (RGBA) with their top/bottom rows, arrow sprite + coords."""
    bars, arrow = logo_parts()
    k = width / arrow.shape[1]
    sz = (width, int(round(arrow.shape[0] * k)))
    h = sz[1]
    yy = np.arange(h, dtype=np.float32)[:, None, None] / h
    out = []
    for m, t, b in bars:
        mm = cv2.resize(m, sz, interpolation=cv2.INTER_AREA)
        col = GOLD_HI + (GOLD_LO - GOLD_HI) * np.clip((yy - 0.35) / 0.55, 0, 1)
        edge = np.clip(mm - np.roll(mm, 3, axis=0), 0, 1)                 # lit top edge
        rgb = col * mm[..., None] + edge[..., None] * C.to_lin(np.float32([1, 0.92, 0.75])) * 0.6
        out.append((np.dstack([rgb, mm]).astype(np.float32), t * k, b * k))
    am = cv2.resize(arrow, sz, interpolation=cv2.INTER_AREA)
    xx = np.arange(sz[0], dtype=np.float32)[None, :]
    g = np.clip(xx / sz[0], 0, 1)[..., None]
    col = C.to_lin(np.float32([0.80, 0.80, 0.82])) * (1 - g) + C.to_lin(np.float32([1, 1, 1])) * g
    ar = np.dstack([col * am[..., None], am]).astype(np.float32)
    ys, xs = np.where(am > 0.3)
    s = (xs - xs.min()) / (xs.max() - xs.min())              # progress coordinate along the arrow (left -> right)
    coord = np.full(am.shape, 2.0, np.float32)
    yyg, xxg = np.mgrid[0:sz[1], 0:sz[0]]
    coord = np.clip((xxg - xs.min()) / (xs.max() - xs.min()), 0, 1).astype(np.float32)
    del s
    return out, ar, coord


def logo_sprite(width, bars_p, arrow_p, sheen=None):
    """Assemble the logo: bars grow from their base (bars_p list 0..1), arrow draws left->right (arrow_p)."""
    bars, ar, coord = logo_layers(width)
    h, w = ar.shape[:2]
    out = np.zeros((h + 60, w + 60, 4), np.float32)
    o = out[30:30 + h, 30:30 + w]
    for (spr, top, bot), p in zip(bars, bars_p):
        if p <= 0:
            continue
        pe = A.BACK_OUT(min(1.0, p))
        hh = (bot - top)
        cut = bot - hh * pe
        rows = (np.arange(h, dtype=np.float32) >= cut)[:, None, None]
        # squash-stretch: shift the bar down by the missing height
        sh = int(round(hh * (1 - pe)))
        s2 = np.roll(spr, sh, axis=0) if sh else spr
        C.over(o, s2 * rows)
    if arrow_p > 0:
        front = arrow_p * 1.08
        m = np.clip((front - coord) / 0.04, 0, 1)[..., None]
        C.over(o, ar * m)
        if arrow_p < 1.0:                                      # hot drawing head
            head = np.exp(-((coord - front) / 0.03) ** 2)[..., None] * ar[..., 3:4]
            o[..., :3] += head * GOLD_HI * 3.0
    if sheen is not None and 0 < sheen < 1:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        band = np.exp(-(((xx - w * (sheen * 1.6 - 0.3)) + (yy - h / 2) * 0.55) / (w * 0.07)) ** 2)
        o[..., :3] += band[..., None] * o[..., 3:4] * 1.4
    return out


# ------------------------------------------------------------------ kinetic type
class KText:
    """Lines of words [(word, font, px, col)], centred (or left-aligned at x). Words rise through a slot mask."""

    def __init__(self, lines, cy, x=S / 2, align='c', lead=1.12):
        self.rows = []
        ys = []
        tot = sum(max(w[2] for w in ln) * lead for ln in lines)
        y = cy - tot / 2
        for ln in lines:
            px = max(w[2] for w in ln)
            y += px * lead * 0.82
            ws = []
            for word, font, wpx, col in ln:
                spr, base, adv = tsprite(word, font, wpx, col, 0.0)
                ws.append([spr, base, adv, wpx])
            gap = px * 0.26
            width = sum(w[2] for w in ws) + gap * (len(ws) - 1)
            xx = x - width / 2 if align == 'c' else x
            for w in ws:
                w.append(xx)
                xx += w[2] + gap
            self.rows.append((ws, y, px))
            ys.append(y)
            y += px * lead * 0.18

    def draw(self, cv, t, t_in, t_out=1e9, stagger=0.07, dur=0.85, line_delay=0.18, s=1.0, op=1.0, slot=True,
             highlight=None):
        k = 0
        for li, (ws, y, px) in enumerate(self.rows):
            for wi, (spr, base, adv, wpx, xx) in enumerate(ws):
                u = t - t_in - k * stagger - li * line_delay
                k += 1
                if u <= 0:
                    continue
                p = A.EXPO_OUT(A.clamp(u / dur))
                q = A.EXPO_IN(A.clamp((t - t_out - k * 0.025) / 0.42)) if t > t_out else 0.0
                dy = (1 - p) * wpx * 0.9 - q * wpx * 0.45
                o = A.ramp(u, 0, dur * 0.4) * (1 - q) * op
                if highlight is not None:
                    o *= highlight(li, wi)
                bl = (1 - p) * 6 + q * 8
                X = S / 2 + (xx - S / 2) * s
                Y = S / 2 + (y - S / 2) * s
                clip = (0, Y + wpx * 0.32 * s) if slot and p < 0.999 else None
                blit(cv, spr, X - 26 * s, Y + dy * s, ax=0, ay=base / spr.shape[0], s=s, op=o, blur=bl, clip=clip)


# ------------------------------------------------------------------ background
@functools.lru_cache(maxsize=1)
def _bg_base():
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r = np.hypot(xx - S / 2, (yy - S * 0.46) * 1.05) / S
    base = np.exp(-(r / 0.55) ** 2)[..., None] * C.to_lin(hexs('0e0b07')) + C.to_lin(hexs('030303'))
    return base.astype(np.float32)


@functools.lru_cache(maxsize=1)
def _dust():
    rng = np.random.default_rng(7)
    n = 170
    return np.c_[rng.uniform(-7, 7, n), rng.uniform(-5, 5, n), rng.uniform(2.5, 16, n)], rng.uniform(0.004, 0.012, n), \
        rng.uniform(0, 6.28, n)


def background(t, grid=1.0, cam=(0.0, 0.0, 1.0)):
    cv = _bg_base().copy()
    # drifting gold aurora (quarter res)
    q = np.zeros((S // 4, S // 4), np.float32)
    yy, xx = np.mgrid[0:S // 4, 0:S // 4].astype(np.float32)
    for i, (ax, ay, sp, r) in enumerate(((0.25, 0.25, 0.11, 0.30), (0.78, 0.68, 0.08, 0.34), (0.55, 0.05, 0.06, 0.25))):
        cx = (ax + 0.10 * math.sin(t * sp * 6.28 + i)) * S / 4
        cy = (ay + 0.08 * math.cos(t * sp * 5.1 + i * 2)) * S / 4
        q += np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * (r * S / 4) ** 2)))
    cv += cv2.resize(q, (S, S))[..., None] * GOLD * 0.010
    # perspective data grid on the floor
    if grid > 0.01:
        cx, cy, z = cam
        cam3 = C.Cam(cx * 0.4, 0.6 + cy * 0.3, 0, F=F)
        m = np.zeros((S, S), np.float32)
        off = (t * 0.9) % 1.0
        for zi in range(2, 34):
            zz = zi - off
            a = np.clip(1 - zz / 34, 0, 1) ** 1.6
            P, d = cam3.project(np.array([[-30, -1.6, zz], [30, -1.6, zz]]))
            cv2.line(m, tuple(np.int32(P[0] * 8)), tuple(np.int32(P[1] * 8)), float(a), 1, cv2.LINE_AA, shift=3)
        for xi in range(-24, 25):
            P, d = cam3.project(np.array([[xi, -1.6, 1.2], [xi, -1.6, 34]]))
            cv2.line(m, tuple(np.int32(P[0] * 8)), tuple(np.int32(P[1] * 8)), 0.55, 1, cv2.LINE_AA, shift=3)
        hor = np.clip((np.arange(S, dtype=np.float32) - S * 0.52) / (S * 0.48), 0, 1)[:, None] ** 0.8
        m *= hor
        cv += (m + cv2.GaussianBlur(m, (0, 0), 3) * 1.5)[..., None] * GOLD * 0.05 * grid
    # gold dust (3D, lens-blurred)
    P, r, ph = _dust()
    P = P.copy()
    P[:, 1] += 0.25 * np.sin(t * 0.3 + ph)
    P[:, 0] += 0.2 * np.sin(t * 0.21 + ph * 1.3) + cam[0] * 0.5
    P[:, 2] = (P[:, 2] - t * 0.35 - 4.0) % 12.5 + 4.0
    tw = 0.5 + 0.5 * np.sin(t * 2.0 + ph * 5)
    C.particles(cv, C.Cam(0, 0, 0, F=F, focus=6.0, aperture=0.05), P, r, GOLD_HI, opacity=0.35 + 0.65 * tw, glow=1.3)
    return cv


# ------------------------------------------------------------------ frame 1: logo reveal
def f1(cv, t, u, d):
    out = A.EXPO_IN(A.clamp((u - (d - 0.34)) / 0.34))
    bars_p = [A.clamp((u - 0.35 - 0.13 * i) / 0.5) for i in range(4)]
    arrow_p = A.EXPO(A.clamp((u - 0.95) / 0.65))
    sheen = (u - 1.9) / 0.7
    s = (1.0 + 0.04 * u / d) * (1 + 0.9 * out)
    lg = b3d('logo', 1 + max(0.0, u - 0.12) * 30)
    if lg is not None:
        blit(cv, with_reflection(lg), S / 2, 520 - 140 * out, s=s * 1.3, op=1 - out, blur=out * 10)
    else:
        spr = logo_sprite(380, bars_p, arrow_p, sheen)
        blit(cv, spr, S / 2, 500 - 140 * out, s=s, op=1 - out, blur=out * 10)
    # wordmark: tracking tightens while it fades in, gold rule grows
    wu = u - 1.55
    if wu > 0:
        p = A.EXPO_OUT(A.clamp(wu / 1.1))
        tr = round(0.75 - 0.5 * p, 2)
        wm, base, adv = tsprite('FLORET CAPITALS', 'Rubik-700', 62, 'w', tr)
        blit(cv, wm, S / 2, 805 - 140 * out, s=s * (1.04 - 0.04 * p), op=A.ramp(wu, 0, 0.5) * (1 - out), blur=(1 - p) * 5 + out * 8)
        rl = 330 * A.EXPO_OUT(A.clamp((wu - 0.25) / 0.9))
        if rl > 2:
            line = np.zeros((10, int(2 * rl) + 2, 4), np.float32)
            g = np.exp(-((np.arange(line.shape[1]) - rl) / (rl * 0.6)) ** 2)[None, :]
            line[4:6, :, :3] = GOLD[None, None] * g[..., None]
            line[4:6, :, 3] = g
            blit(cv, line, S / 2, 868 - 140 * out, s=s, op=(1 - out), mode='add')
            blit(cv, line, S / 2, 868 - 140 * out, s=s, op=(1 - out) * 0.8, blur=4, mode='add')


# ------------------------------------------------------------------ frame 2: leading brokerage house
@functools.lru_cache(maxsize=64)
def chart_card(prog_q):
    p = U.Paint(980, 300, pad=10)
    spark(p, 0, 20, 980, 260, seed=12, prog=prog_q / 40, width=3.2, drift=1.4)
    rng = np.random.default_rng(3)
    for i in range(22):                                       # faint candles behind the line
        x = 20 + i * 44
        v = walk(12, drift=1.4)[min(47, int(i * 47 / 21))]
        hgt = rng.uniform(30, 80)
        yc = 20 + 260 * (1 - v)
        if x / 980 <= prog_q / 40:
            p.rrect(x - 7, yc - hgt / 2, 14, hgt, 3, GOLD_S if rng.random() > 0.3 else MUTED_S, 0.18)
    return p.result()


@functools.lru_cache(maxsize=4)
def chip(txt, w=None):
    """Small glass pill with the logo icon + label."""
    spr, base, adv = tsprite(txt, 'Rubik-500', 26, 'w', 0.12)
    w = w or int(adv + 110)
    p = U.Paint(w, 64, pad=24)
    gcard(p, 0, 0, w, 64, 32)
    res = half(p.result())
    icon = logo_sprite(56, [1, 1, 1, 1], 1.0)
    blit(res, icon, 24 + 44, 24 + 32, s=0.82)
    blit(res, spr, 24 + 78 - 26, 24 + 32 + 9, ax=0, ay=base / spr.shape[0])
    return res


def f2(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    ch = chip('FLORET CAPITALS')
    p = A.EXPO_OUT(A.clamp((u - 0.1) / 0.7))
    blit(cv, ch, S / 2, 390 - (1 - p) * 30, op=A.ramp(u, 0.1, 0.4) * (1 - out), blur=(1 - p) * 4)
    kt = KText([[("Pakistan's", 'Rubik-700', 82, 'w'), ('Leading', 'Rubik-700', 82, 'w')],
                [('Brokerage', 'Rubik-800', 104, 'g'), ('House', 'Rubik-800', 104, 'g')]], 600)
    kt.draw(cv, t, FRAMES[1][1] + 0.2, FRAMES[1][2] - 0.34)
    pr = A.EXPO(A.clamp((u - 0.4) / 2.0))
    card = chart_card(int(round(pr * 40)))
    put3d(cv, card, S / 2, 930 + 30 * (1 - pr), 1000, rot=(-38, 0, 0), op=A.ramp(u, 0.3, 0.8) * (1 - out) * 0.9)


# ------------------------------------------------------------------ frame 3: 12,000+ clients map
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
    dots = []
    for y in np.arange(0, size, 15):
        for x in np.arange(0, size, 15):
            if cv2.pointPolygonTest(poly_px, (float(x), float(y)), False) >= 0:
                dots.append((x, y))
    p = U.Paint(size, size, pad=20)
    for x, y in dots:
        p.circle(x, y, 2.6, GOLD_S, 0.55)
    p.line([tuple(q) for q in poly_px] + [tuple(poly_px[0])], 1.4, GOLD_S, 0.35)
    cities = {n: proj(lo, la) for n, lo, la in CITIES}
    return half(p.result()), cities, size


def f3(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    spr, cities, size = pak_map()
    mp = A.EXPO_OUT(A.clamp(u / 1.0))
    mx, my, ms = S / 2 + 20, 660, 0.78
    blit(cv, spr, mx, my, s=ms * (0.94 + 0.06 * mp), op=0.75 * A.ramp(u, 0, 0.6) * (1 - out), blur=(1 - mp) * 5)

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
        if n != 'Lahore':                                     # arc from Lahore
            pr = A.EXPO_OUT(A.clamp(cu / 0.7))
            mxp, myp = (hub[0] + x) / 2, (hub[1] + y) / 2 - 0.25 * math.hypot(x - hub[0], y - hub[1])
            ts = np.linspace(0, pr, 40)
            px = (1 - ts) ** 2 * hub[0] + 2 * (1 - ts) * ts * mxp + ts ** 2 * x
            py = (1 - ts) ** 2 * hub[1] + 2 * (1 - ts) * ts * myp + ts ** 2 * y
            cv2.polylines(ov, [np.int32(np.c_[px, py] * 8)], False, 0.55, 1, cv2.LINE_AA, shift=3)
            cv2.circle(ov, (int(px[-1] * 8), int(py[-1] * 8)), 3 * 8, 1.2, -1, cv2.LINE_AA, shift=3)
        if cu > 0.5 or n == 'Lahore':
            pu = (cu - (0 if n == 'Lahore' else 0.5))
            cv2.circle(ov, (int(x * 8), int(y * 8)), int(5 * 8), 1.5, -1, cv2.LINE_AA, shift=3)
            rr = 6 + 40 * ((pu * 0.8) % 1.0)
            cv2.circle(ov, (int(x * 8), int(y * 8)), int(rr * 8), 0.8 * (1 - (pu * 0.8) % 1.0), 2, cv2.LINE_AA, shift=3)
    ov *= (1 - out)
    cv[..., :3] += (ov[..., None] + cv2.GaussianBlur(ov, (0, 0), 5)[..., None] * 1.6) * GOLD_HI
    cv[..., 3] = np.clip(cv[..., 3] + ov * 0.5, 0, 1)
    # tumbling 3D coins either side of the map
    for i, (x, y, sc, ph) in enumerate(((175, 470, 0.62, 0), (1075, 820, 0.5, 40))):
        cn = b3d('coin', 1 + t * 30 * 0.9 + ph, pingpong=True)
        if cn is not None:
            q = A.EXPO_OUT(A.clamp((u - 0.4 - i * 0.2) / 0.9))
            blit(cv, cn, x + (1 - q) * (-120 if i == 0 else 120), y + 14 * math.sin(t * 1.3 + i * 2), s=sc,
                 op=q * (1 - A.EXPO_IN(out)), blur=(1 - q) * 6 + (1.5 if i else 0))
    # counter
    cu = A.ramp(u, 0.35, 1.9, A.EXPO)
    n = int(round(12000 * cu / 10.0)) * 10
    txt = f'{n:,}' + ('+' if cu > 0.98 else '')
    num, base, adv = tsprite(txt, 'Rubik-800', 190, 'g', 0.0)
    pop = 1 + 0.06 * math.exp(-max(0, u - 1.95) * 6) * (u > 1.9)
    o = A.ramp(u, 0.3, 0.6) * (1 - A.EXPO_IN(out))
    blit(cv, num, S / 2, 250, s=pop, op=o, blur=(1 - A.clamp((u - 0.3) / 0.5)) * 6 + out * 10)
    kt = KText([[('Active', 'Rubik-700', 70, 'w'), ('Clients', 'Rubik-700', 70, 'w')],
                [('Nationwide', 'Rubik-500', 54, 'gold')]], 1085)
    kt.draw(cv, t, FRAMES[2][1] + 0.9, FRAMES[2][2] - 0.34)


# ------------------------------------------------------------------ frame 4: one platform, multiple markets
TABS = ['PSX', 'PMEX', 'GOLD', 'CRUDE OIL']
ROWS = [('UBL', 'Banking', 31), ('HBL', 'Banking', 32), ('OGDCL', 'Oil & Gas', 33), ('PSO', 'Energy', 34)]


@functools.lru_cache(maxsize=256)
def dashboard(tab, prog_q):
    W_, H_ = 760, 470
    p = U.Paint(W_, H_, pad=30)
    gcard(p, 0, 0, W_, H_, 30)
    p.text('FLORET CAPITALS', 30, 52, 'Rubik-700', 22, WHITE_S, 0.95, track=0.1)
    for k in range(3):
        p.circle(W_ - 40 - k * 22, 44, 5, MUTED_S, 0.5)
    x = 30
    for i, tb in enumerate(TABS):
        w = U._font('Rubik-500', 22 * SS).getlength(tb) / SS + 34
        if i == tab:
            p.rrect(x, 78, w, 40, 20, GOLD_S, 1.0)
            p.text(tb, x + w / 2, 105, 'Rubik-700', 21, DARK_S, 1.0, anchor='c')
        else:
            p.rrect(x, 78, w, 40, 20, WHITE_S, 0.06)
            p.text(tb, x + w / 2, 105, 'Rubik-500', 21, MUTED_S, 1.0, anchor='c')
        x += w + 10
    for k in range(4):                                         # chart grid
        p.line([(30, 160 + k * 70), (470, 160 + k * 70)], 1, WHITE_S, 0.06)
    spark(p, 30, 150, 440, 270, seed=40 + tab, prog=prog_q / 30, width=3.0, drift=1.0)
    for i, (tk, sec, sd) in enumerate(ROWS):
        y = 150 + i * 72
        p.rrect(500, y, 230, 60, 14, WHITE_S, 0.045)
        p.text(tk, 516, y + 28, 'Rubik-700', 21, WHITE_S, 1.0)
        p.text(sec, 516, y + 50, 'Rubik-400', 15, MUTED_S, 1.0)
        spark(p, 620, y + 12, 92, 36, seed=sd + tab, prog=1.0, width=1.8, fill=False)
    return p.result()


@functools.lru_cache(maxsize=8)
def mini_card(label, seed, sub=''):
    p = U.Paint(260, 150, pad=24)
    gcard(p, 0, 0, 260, 150, 22)
    p.text(label, 22, 44, 'Rubik-700', 24, WHITE_S, 1.0)
    if sub:
        p.text(sub, 22, 68, 'Rubik-400', 15, MUTED_S, 1.0)
    poly(p, [(230, 30), (240, 44), (220, 44)], GOLD_S, 1.0)
    spark(p, 22, 78, 216, 52, seed, 1.0, width=2.2)
    return p.result()


def f4(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    kt = KText([[('One', 'Rubik-700', 80, 'w'), ('Platform.', 'Rubik-700', 80, 'w')],
                [('Multiple', 'Rubik-800', 92, 'g'), ('Markets.', 'Rubik-800', 92, 'g')]], 255)
    kt.draw(cv, t, FRAMES[3][1] + 0.15, FRAMES[3][2] - 0.34)
    tab = min(3, int(max(0, u - 0.9) / 0.55))
    pr = A.EXPO(A.clamp((u - 0.5 - tab * 0.55) / 0.9)) if tab == 0 else A.EXPO(A.clamp((u - 0.9 - tab * 0.55) / 0.5))
    img = dashboard(tab, int(round(pr * 30)))
    p = A.EXPO_OUT(A.clamp((u - 0.25) / 1.0))
    o = A.ramp(u, 0.25, 0.6) * (1 - A.EXPO_IN(out))
    put3d(cv, img, S / 2 - 20, 790 + (1 - p) * 120, 880, rot=(14 * (1 - p) + 6, -16 + 10 * p + 4 * u / d, 0), op=o)
    for i, (lab, sd, x, y, dz) in enumerate((('PSX', 51, 190, 1040, -0.9), ('PMEX', 52, 1060, 560, -1.1))):
        q = A.EXPO_OUT(A.clamp((u - 0.6 - i * 0.2) / 0.9))
        put3d(cv, mini_card(lab, sd), x + (1 - q) * (-200 if i == 0 else 200), y + 12 * math.sin(u * 1.5 + i), 270,
              rot=(4, 18 if i == 0 else -18, 0), depth=4.0, dz=dz, op=q * (1 - out))


# ------------------------------------------------------------------ frame 5: PSX x PMEX
@functools.lru_cache(maxsize=4)
def badge(label, sub):
    """White plate with the exchange's official logo (psx.com.pk lockup / PMEX emblem), gold-lit edge."""
    W_, H_ = 400, 270
    p = U.Paint(W_, H_, pad=30)
    m = p.rrect(0, 0, W_, H_, 34, hexs('fbfaf7'), 1.0)
    p.glow(np.clip(0.5 - (np.abs(p.sdf_rrect(0, 0, W_, H_, 34)) - 1), 0, 1), GOLD_S, 8, 0.9)
    p.stroke(0, 0, W_, H_, 34, 2, GOLD_S, 0.9)
    del m
    if label == 'PMEX':
        p.text('PMEX', 180, 126, 'Rubik-800', 64, hexs('cc1721'), 1.0)
        p.text('Pakistan Mercantile', 184, 166, 'Rubik-500', 20, hexs('5b5b5b'), 1.0)
        p.text('Exchange', 184, 192, 'Rubik-500', 20, hexs('5b5b5b'), 1.0)
    res = half(p.result())
    if label == 'PSX':
        lg = C.load(ASSETS + '/psx_logo_full.png')
        blit(res, lg, 30 + W_ / 2, 30 + H_ / 2, s=(H_ - 40) / lg.shape[0])
    else:
        lg = C.load(ASSETS + '/pmex_emblem.png')
        blit(res, lg, 30 + 98, 30 + H_ / 2, s=150 / lg.shape[0])
    return res


@functools.lru_cache(maxsize=4)
def check_chip(word):
    spr, base, adv = tsprite(word, 'Rubik-500', 36, 'w', 0.0)
    w = int(adv + 104)
    p = U.Paint(w, 76, pad=24)
    gcard(p, 0, 0, w, 76, 38)
    p.circle(40, 38, 18, GOLD_S, 1.0)
    p.line([(31, 38), (38, 46), (50, 30)], 3.4, DARK_S, 1.0)
    res = half(p.result())
    blit(res, spr, 24 + 72 - 26, 24 + 38 + 13, ax=0, ay=base / spr.shape[0])
    return res


def f5(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    o = 1 - A.EXPO_IN(out)
    for i, (lab, sub) in enumerate((('PSX', 'Pakistan Stock Exchange'), ('PMEX', 'Pakistan Mercantile Exchange'))):
        p = A.EXPO_OUT(A.clamp((u - 0.15) / 0.9))
        sgn = -1 if i == 0 else 1
        x = S / 2 + sgn * (265 + (1 - p) * 360)
        put3d(cv, badge(lab, sub), x, 470, 420, rot=(0, -sgn * 22 * (1 - p) - sgn * 8, 0), op=A.ramp(u, 0.15, 0.5) * o)
    # x mark flash + data link
    xu = u - 0.75
    if xu > 0:
        xs, base, _ = tsprite('×', 'Rubik-500', 140, 'g')
        s = 1 + 0.6 * math.exp(-xu * 7)
        blit(cv, xs, S / 2, 470, s=s, op=A.ramp(xu, 0, 0.15) * o)
        flash = math.exp(-xu * 5) * 1.5
        yy, xx = np.ogrid[0:S, 0:S]
        g = np.exp(-(((xx - S / 2) / 260.0) ** 2 + ((yy - 470) / 60.0) ** 2)).astype(np.float32)
        cv[..., :3] += g[..., None] * GOLD * flash * 0.5 * o
    for i, w in enumerate(('Regulated.', 'Trusted.', 'Connected.')):
        cu = u - 1.0 - i * 0.22
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.7))
        chp = check_chip(w)
        y = 800 + i * 0
        x = S / 2 + (i - 1) * 345
        blit(cv, chp, x, y + (1 - p) * 50, s=0.96 + 0.04 * p, op=A.ramp(cu, 0, 0.3) * o, blur=(1 - p) * 5)
    # thin gold connector under the chips
    lu = A.EXPO_OUT(A.clamp((u - 1.5) / 1.0))
    if lu > 0:
        ov = np.zeros((S, S), np.float32)
        cv2.line(ov, (int((S / 2 - 520 * lu) * 8), 905 * 8), (int((S / 2 + 520 * lu) * 8), 905 * 8), 0.8, 1, cv2.LINE_AA, shift=3)
        cv[..., :3] += (ov + cv2.GaussianBlur(ov, (0, 0), 3))[..., None] * GOLD * o


# ------------------------------------------------------------------ frame 6: commodities
OBJ3D = dict(gold='goldbar', silver='silverbar', oil='barrel', more='coin')


@functools.lru_cache(maxsize=8)
def commodity_card(kind, icon=True):
    W_, H_ = 400, 260
    p = U.Paint(W_, H_, pad=30)
    gcard(p, 0, 0, W_, H_, 30, k=1.2)
    cx, cy = 92, 110
    if not icon:
        p.circle(cx, cy + 34, 44, GOLD_S, 0.07)                 # soft pad the 3D object sits on
        name = dict(gold='GOLD', silver='SILVER', oil='CRUDE OIL', more='AND MORE')[kind]
    elif kind in ('gold', 'silver'):
        hi, mid, lo = (GOLD_HI_S, GOLD_S, GOLD_LO_S) if kind == 'gold' else (hexs('ffffff'), SILVER_S, hexs('8f969f'))
        poly(p, [(cx - 50, cy + 30), (cx + 50, cy + 30), (cx + 34, cy - 8), (cx - 34, cy - 8)], mid, 1.0)
        poly(p, [(cx - 34, cy - 8), (cx + 34, cy - 8), (cx + 24, cy - 26), (cx - 24, cy - 26)], hi, 1.0)
        poly(p, [(cx + 34, cy - 8), (cx + 50, cy + 30), (cx + 40, cy + 30), (cx + 24, cy - 26)], lo, 0.9)
        name = 'GOLD' if kind == 'gold' else 'SILVER'
    elif kind == 'oil':
        p.circle(cx, cy + 12, 30, hexs('2b2620'), 1.0)
        poly(p, [(cx - 27, cy + 2), (cx, cy - 44), (cx + 27, cy + 2)], hexs('2b2620'), 1.0)
        p.stroke(cx - 31, cy - 19, 62, 62, 31, 2.4, GOLD_S, 0.9)
        p.circle(cx - 9, cy + 6, 7, WHITE_S, 0.35)
        name = 'CRUDE OIL'
    else:
        p.circle(cx, cy, 34, GOLD_S, 1.0)
        p.line([(cx - 15, cy), (cx + 15, cy)], 5, DARK_S, 1.0)
        p.line([(cx, cy - 15), (cx, cy + 15)], 5, DARK_S, 1.0)
        name = 'AND MORE'
    p.text(name, 160, 104, 'Rubik-700', 32, WHITE_S, 1.0)
    p.text('PMEX', 160, 134, 'Rubik-400', 18, MUTED_S, 1.0, track=0.1)
    spark(p, 34, 166, 332, 70, {'gold': 61, 'silver': 62, 'oil': 63}.get(kind, 64), 1.0, width=2.6)
    return p.result()


def f6(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    o = 1 - A.EXPO_IN(out)
    T0 = FRAMES[5][1]
    words = [('Gold.', 'g'), ('Silver.', 's'), ('Crude Oil.', 'w'), ('And More.', 'g')]
    starts = [0.2, 0.85, 1.5, 2.2]
    cur = sum(1 for s0 in starts if u >= s0) - 1
    for i, ((w, col), s0) in enumerate(zip(words, starts)):
        kt = KText([[(w, 'Rubik-800', 96, col)]], 360 + i * 150, x=110, align='l')
        hl = 1.0 if i == cur or u > 2.9 else 0.38
        kt.draw(cv, t, T0 + s0, FRAMES[5][2] - 0.34, op=hl)
    kinds = ['gold', 'silver', 'oil', 'more']
    for i in range(4):
        cu = u - starts[i] - 0.05
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.8))
        x, y = 880 + (i % 2) * 40, 330 + i * 200
        co = A.ramp(cu, 0, 0.35) * o * (1.0 if i == cur or u > 2.9 else 0.7)
        has3d = b3d(OBJ3D[kinds[i]], 1) is not None
        xx = x + (1 - p) * 320
        put3d(cv, commodity_card(kinds[i], not has3d), xx, y, 380, rot=(4, -20 + 6 * p, 0), op=co)
        if has3d:
            ob = b3d(OBJ3D[kinds[i]], 1 + (t - T0 - starts[i]) * 30 * 1.1, pingpong=True)
            sc = (0.6 if kinds[i] != 'more' else 0.42) * (0.75 + 0.25 * A.BACK_OUT(A.clamp(cu / 0.7)))
            blit(cv, ob, xx - 100, y - 22, s=sc, op=co)


# ------------------------------------------------------------------ frame 7: global commodities -> PSX companies
@functools.lru_cache(maxsize=1)
def _globe_pts():
    n = 1400
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
        b = 0.25 + 0.75 * (zi > 0) * zi
        cv2.circle(ov, (int((cx + xi * r) * 8), int((cy - yi * r) * 8)), int((1.4 + 0.9 * max(zi, 0)) * 8), float(b),
                   -1, cv2.LINE_AA, shift=3)
    ov *= op
    cv[..., :3] += (ov[..., None] * 0.8 + cv2.GaussianBlur(ov, (0, 0), 4)[..., None] * 0.8) * GOLD
    rim = np.zeros((S, S), np.float32)
    cv2.circle(rim, (int(cx * 8), int(cy * 8)), int(r * 8), 1.0, 2, cv2.LINE_AA, shift=3)
    cv[..., :3] += cv2.GaussianBlur(rim, (0, 0), 6)[..., None] * GOLD * 0.6 * op
    cv[..., 3] = np.clip(cv[..., 3] + ov * 0.6, 0, 1)


@functools.lru_cache(maxsize=8)
def ticker_card(tk, sec, seed):
    p = U.Paint(300, 150, pad=24)
    gcard(p, 0, 0, 300, 150, 24)
    p.rrect(20, 22, 54, 54, 16, GOLD_S, 0.16)
    p.text(tk[0], 47, 61, 'Rubik-800', 28, GOLD_S, 1.0, anchor='c')
    p.text(tk, 90, 50, 'Rubik-700', 30, WHITE_S, 1.0)
    p.text(sec, 90, 74, 'Rubik-400', 17, MUTED_S, 1.0)
    poly(p, [(270, 36), (281, 52), (259, 52)], GOLD_S, 1.0)
    spark(p, 20, 92, 260, 42, seed, 1.0, width=2.2)
    return p.result()


def f7(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    o = 1 - A.EXPO_IN(out)
    T0 = FRAMES[6][1]
    kt = KText([[('From', 'Rubik-500', 58, 'w'), ('Global', 'Rubik-700', 58, 'w'), ('Commodities', 'Rubik-700', 58, 'g')],
                [('to', 'Rubik-500', 58, 'w'), ("Pakistan's", 'Rubik-700', 58, 'w'), ('Leading', 'Rubik-700', 58, 'w'),
                 ('Companies', 'Rubik-700', 58, 'g')]], 235)
    kt.draw(cv, t, T0 + 0.1, FRAMES[6][2] - 0.34, stagger=0.05)
    gp = A.EXPO_OUT(A.clamp((u - 0.2) / 1.0))
    globe(cv, 330 - (1 - gp) * 60, 690, 230 * (0.85 + 0.15 * gp), u * 0.45 + 0.5, A.ramp(u, 0.2, 0.7) * o)
    for i, (tk, sec, sd) in enumerate(ROWS):
        cu = u - 1.0 - i * 0.16
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.8))
        x = 870 + (i % 2) * 0
        y = 470 + i * 150
        put3d(cv, ticker_card(tk, sec, sd), x + (1 - p) * 220, y, 330, rot=(0, -14, 0), op=A.ramp(cu, 0, 0.3) * o,
              dz=-0.15 * i)
        # link from the globe to each card
        ov = np.zeros((S, S), np.float32)
        x0, y0 = 330 + 230 * 0.8, 690 + (i - 1.5) * 80
        x1, y1 = x + (1 - p) * 220 - 170, y
        ts = np.linspace(0, p, 30)
        px = x0 + (x1 - x0) * ts
        py = y0 + (y1 - y0) * (3 * ts ** 2 - 2 * ts ** 3)
        cv2.polylines(ov, [np.int32(np.c_[px, py] * 8)], False, 0.6, 1, cv2.LINE_AA, shift=3)
        cv[..., :3] += (ov + cv2.GaussianBlur(ov, (0, 0), 3))[..., None] * GOLD * o
    # ticker band
    bu = A.EXPO_OUT(A.clamp((u - 1.6) / 0.8))
    if bu > 0:
        band, base, adv = tsprite('UBL  ·  HBL  ·  OGDCL  ·  PSO  ·  ', 'Rubik-700', 40, 'gold', 0.06)
        off = (u * 120) % adv
        for k in range(-1, 3):
            blit(cv, band, k * adv - off, 1130, ax=0, op=bu * o * 0.9)


# ------------------------------------------------------------------ frame 8: insights / decisions / trust
@functools.lru_cache(maxsize=4)
def icon_disc(kind):
    p = U.Paint(130, 130, pad=30)
    p.circle(65, 65, 62, DARK_S, 0.85)
    p.stroke(3, 3, 124, 124, 62, 2, GOLD_S, 0.9)
    c = GOLD_S
    if kind == 'bulb':
        p.circle(65, 56, 24, c, 1.0)
        p.rrect(54, 74, 22, 20, 5, c, 1.0)
        p.line([(56, 98), (74, 98)], 3, c, 1.0)
        for a in range(-60, 61, 30):
            r = math.radians(a - 90)
            p.line([(65 + math.cos(r) * 33, 56 + math.sin(r) * 33), (65 + math.cos(r) * 40, 56 + math.sin(r) * 40)], 3, c, 1.0)
    elif kind == 'target':
        for rr, w in ((30, 3), (19, 3)):
            p.stroke(65 - rr, 65 - rr, 2 * rr, 2 * rr, rr, w, c, 1.0)
        p.circle(65, 65, 7, c, 1.0)
        p.line([(65, 65), (96, 34)], 3.5, WHITE_S, 1.0)
        poly(p, [(96, 34), (84, 36), (94, 46)], WHITE_S, 1.0)
    else:
        poly(p, [(65, 30), (96, 42), (93, 72), (65, 100), (37, 72), (34, 42)], c, 1.0)
        p.line([(51, 66), (62, 77), (82, 54)], 5, DARK_S, 1.0)
    return half(p.result())


def f8(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    o = 1 - A.EXPO_IN(out)
    T0 = FRAMES[7][1]
    rows = [('Expert', 'Insights.', 'bulb'), ('Smarter', 'Decisions.', 'target'), ('Built on', 'Trust.', 'shield')]
    sh = b3d('shield', 1 + max(0.0, u) * 30 * 0.95)
    if sh is not None:
        q = A.EXPO_OUT(A.clamp(u / 0.9))
        blit(cv, sh, S / 2, 260 + 10 * math.sin(u * 1.6), s=1.9 * (0.8 + 0.2 * q), op=A.ramp(u, 0, 0.4) * o, blur=(1 - q) * 6)
    for i, (a, b, ic) in enumerate(rows):
        y = 540 + i * 175
        cu = u - 0.2 - i * 0.55
        if cu <= 0:
            continue
        p = A.EXPO_OUT(A.clamp(cu / 0.8))
        blit(cv, icon_disc(ic), 215, y, s=1.2 * (0.6 + 0.4 * A.BACK_OUT(A.clamp(cu / 0.6))), op=A.ramp(cu, 0, 0.25) * o,
             rot=(1 - p) * -40)
        kt = KText([[(a, 'Rubik-700', 74, 'w'), (b, 'Rubik-800', 74, 'g')]], y + 4, x=320, align='l')
        kt.draw(cv, t, T0 + 0.25 + i * 0.55, FRAMES[7][2] - 0.34)
        # connector line down to the next row
        if i < 2:
            lu = A.EXPO_OUT(A.clamp((cu - 0.35) / 0.5))
            ov = np.zeros((S, S), np.float32)
            cv2.line(ov, (215 * 8, int((y + 72) * 8)), (215 * 8, int((y + 72 + 56 * lu) * 8)), 0.7, 1, cv2.LINE_AA, shift=3)
            cv[..., :3] += (ov + cv2.GaussianBlur(ov, (0, 0), 3))[..., None] * GOLD * o


# ------------------------------------------------------------------ frame 9: more markets tunnel
@functools.lru_cache(maxsize=16)
def tile(i):
    labels = [('PSX', 'Equities'), ('PMEX', 'Commodities'), ('GOLD', 'Metals'), ('SILVER', 'Metals'), ('CRUDE OIL', 'Energy'),
              ('UBL', 'Banking'), ('HBL', 'Banking'), ('OGDCL', 'Oil & Gas'), ('PSO', 'Energy'), ('KSE-100', 'Index')]
    lab, sub = labels[i % len(labels)]
    p = U.Paint(280, 170, pad=10)
    gcard(p, 0, 0, 280, 170, 22)
    p.text(lab, 22, 46, 'Rubik-700', 26, WHITE_S, 1.0)
    p.text(sub, 22, 70, 'Rubik-400', 15, MUTED_S, 1.0)
    spark(p, 22, 92, 236, 56, 80 + i, 1.0, width=2.2)
    return p.result()


def f9(cv, t, u, d):
    out = A.clamp((u - (d - 0.34)) / 0.34)
    o = 1 - A.EXPO_IN(out)
    z0 = u * 5.0 + A.EXPO_IN(A.clamp(u / d)) * 4
    cam = C.Cam(0.15 * math.sin(u * 0.8), 0, z0, roll=4 * math.sin(u * 0.6), F=F, focus=z0 + 4.0, aperture=0.008)
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
            C.draw_img3d(cv, tile(ti), cam, (x, y, z), (1.4, 0.85), (rx, ry, 0), opacity=fade * o * 0.9)
        except cv2.error:                                     # far tile smaller than its blur
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
    kt = KText([[('More', 'Rubik-700', 96, 'w'), ('Markets.', 'Rubik-700', 96, 'w')],
                [('More', 'Rubik-800', 104, 'g'), ('Possibilities.', 'Rubik-800', 104, 'g')]], 610)
    # dark core behind the type so the tunnel never fights it
    yy, xx = np.ogrid[0:S, 0:S]
    g = np.exp(-(((xx - S / 2) / 520.0) ** 2 + ((yy - 610) / 200.0) ** 2)).astype(np.float32)
    cv[..., :3] *= 1 - 0.75 * g[..., None] * A.ramp(u, 0.1, 0.6)
    cv[..., 3] = np.clip(cv[..., 3] + 0.75 * g * A.ramp(u, 0.1, 0.6), 0, 1)
    kt.draw(cv, t, FRAMES[8][1] + 0.25, FRAMES[8][2] - 0.34)


# ------------------------------------------------------------------ frame 10: THINK BIGGER. THINK FLORET.
def slam(cv, spr, x, y, u, op=1.0):
    if u <= 0:
        return
    p = A.EXPO_OUT(A.clamp(u / 0.45))
    blit(cv, spr, x, y, s=1.0 + 0.55 * (1 - p), op=A.ramp(u, 0, 0.12) * op, blur=(1 - p) * 12)


def f10(cv, t, u, d):
    T_LOGO = 2.05
    q = A.EXPO_IN(A.clamp((u - T_LOGO + 0.35) / 0.45))
    a, ba, _ = tsprite('THINK BIGGER.', 'Rubik-900', 118, 'w', 0.02)
    b, bb, _ = tsprite('THINK FLORET.', 'Rubik-900', 118, 'g', 0.02)
    slam(cv, a, S / 2, 545 - q * 120, u - 0.1, 1 - q)
    slam(cv, b, S / 2, 700 - q * 120, u - 0.62, 1 - q)
    lu = u - T_LOGO
    if lu > 0:
        bars_p = [A.clamp((lu - 0.05 - 0.09 * i) / 0.4) for i in range(4)]
        ar = A.EXPO(A.clamp((lu - 0.35) / 0.5))
        lg = b3d('logo', 1 + lu * 30 * 1.25)
        if lg is not None:
            blit(cv, with_reflection(lg), S / 2, 470, s=1.15 + 0.02 * lu / 3)
        else:
            spr = logo_sprite(300, bars_p, ar, (lu - 1.25) / 0.7)
            blit(cv, spr, S / 2, 480, s=1.0 + 0.02 * lu / 3)
        wu = lu - 0.6
        if wu > 0:
            p = A.EXPO_OUT(A.clamp(wu / 1.0))
            wm, base, _ = tsprite('FLORET CAPITALS', 'Rubik-700', 70, 'w', round(0.6 - 0.4 * p, 2))
            blit(cv, wm, S / 2, 770, op=A.ramp(wu, 0, 0.5), blur=(1 - p) * 5)
            sh = (wu - 0.9) / 0.8
            if 0 < sh < 1:
                wl, _, _ = tsprite('FLORET CAPITALS', 'Rubik-700', 70, 'g', 0.2)
                band = np.exp(-((np.arange(wl.shape[1]) - wl.shape[1] * (sh * 1.4 - 0.2)) / 60.0) ** 2)[None, :, None]
                blit(cv, wl * band, S / 2, 770, mode='add', op=1.2)
        su = lu - 1.1
        if su > 0:
            p = A.EXPO_OUT(A.clamp(su / 0.8))
            url, _, _ = tsprite('floretcapitals.com', 'Rubik-500', 30, 'gold', 0.08)
            blit(cv, url, S / 2, 862 + (1 - p) * 16, op=A.ramp(su, 0, 0.4) * 0.95)
    # end fade
    cv *= 1 - A.ramp(u, d - 0.35, d, A.EASY)


DRAW = dict(f1=f1, f2=f2, f3=f3, f4=f4, f5=f5, f6=f6, f7=f7, f8=f8, f9=f9, f10=f10)


# ------------------------------------------------------------------ camera, transitions, frame
def cam2d(t):
    """Global 2D camera on the UI layer: slow push inside each frame + punch at each cut + drift."""
    z = 1.0
    for name, a, b in FRAMES:
        if a <= t < b + OVL:
            z = 1.0 + 0.045 * A.clamp((t - a) / (b - a))
    for name, a, b in FRAMES[1:]:
        dt = t - a
        if -0.25 < dt < 0.6:
            z *= 1 + 0.07 * math.exp(-max(dt, 0) * 7) * (dt > 0) - 0.05 * A.clamp((dt + 0.25) / 0.25) * (dt <= 0)
    dx = 5 * A.wiggle(t, 0.25, 1, 3)
    dy = 4 * A.wiggle(t, 0.22, 1, 4)
    rot = 0.25 * A.wiggle(t, 0.18, 1, 5)
    return dx, dy, z, rot


def draw(t):
    dx, dy, z, rot = cam2d(t)
    cv = background(t, grid=1.0, cam=(dx / 200, dy / 200, z))
    fg = np.zeros((S, S, 4), np.float32)
    for name, a, b in FRAMES:
        if a <= t < b + OVL:
            DRAW[name](fg, t, t - a, b - a)
    M = cv2.getRotationMatrix2D((S / 2, S / 2), rot, z)
    M[0, 2] += dx
    M[1, 2] += dy
    fg = cv2.warpAffine(fg, M, (S, S), flags=cv2.INTER_LINEAR, borderValue=0)
    C.over(cv, fg)
    # cut accents: radial zoom blur + gold light sweep
    for name, a, b in FRAMES[1:]:
        dt = t - a
        if abs(dt) < 0.22:
            bump = math.exp(-(dt / 0.09) ** 2)
            cv[...] = radial(cv, 0.10 * bump)
            yy, xx = np.ogrid[0:S, 0:S]
            pos = (dt + 0.22) / 0.44 * (S * 1.6) - S * 0.3
            band = np.exp(-(((xx + yy * 0.35) - pos) / 50.0) ** 2).astype(np.float32)
            cv += band[..., None] * GOLD * 0.35 * bump
    return cv


def radial(img, amount, n=6):
    if amount < 0.004:
        return img
    acc = img.copy()
    for i in range(1, n):
        s = 1 + amount * i / n
        M = np.float32([[s, 0, (1 - s) * S / 2], [0, s, (1 - s) * S / 2]])
        acc += cv2.warpAffine(img, M, (S, S), borderMode=cv2.BORDER_REFLECT)
    return acc / n


@functools.lru_cache(maxsize=1)
def _vig():
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    r = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
    return np.clip(1 - 0.7 * np.clip(r - 0.4, 0, None) ** 1.6, 0, 1)[..., None]


def finish(f, t):
    f = C.deep_glow(f, 0.55, 0.38, (1.0, 0.7, 0.36), sat_boost=0.6)
    f = C.halation(f, 0.06, threshold=0.7)
    f = C.anamorphic(f, 1.1, 0.06, (1.0, 0.7, 0.35), 0.35)
    x = f[..., :3] / (1 + f[..., :3] * 0.18)
    s = C.to_srgb(np.clip(x, 0, 1))
    s = np.clip((s - 0.012) / 0.988, 0, 1)
    s = s * s * (3 - 2 * s) * 0.18 + s * 0.82
    s = s * _vig()
    return C.grain(s, t, 0.012, 1.2)


def samples_for(t):
    for name, a, b in FRAMES[1:]:
        if abs(t - a) < 0.3:
            return 5
    for name, a, b in FRAMES:
        if a <= t < b:
            u = t - a
            if u < 0.9 or b - t < 0.45:
                return 4
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
