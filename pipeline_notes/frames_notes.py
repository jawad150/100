"""Look for Organic Fostering "The Question in the Notes App" (9:16). Kinetic-typography explainer style (after the
reference): lilac-white light sections and deep plum night sections, mixed-weight Nunito words, black-and-white circle
portraits with a dotted ring, big circle wipes, glowing icon nodes on dotted paths, 3D objects on every cue word.
Skills: layercut (the three drafts), retro (that week, on tape), spiral (phone down beside the mug), explainer (support
path), eclipse + aurora (outside normal hours).
Brand: plum #5B174F, magenta #B7006E, orange #FF6411, green #61A80A, ivory #FCF8F5; Nunito; no exclamation marks.
"""
import os, sys, math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ai'))
import frames_ai as FA
from frames_ai import (W, H, load, cover, grade, grain, paste, rrect, layercut, eclipse, aurora, retro, Clip, clamp, prog, e_out,
                       e_inout, e_back, vignette, _grid)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_notes'
FON = f'{ROOT}/workspace_sol/fonts'


def hx(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


PLUM, MAG, ORANGE, GREEN, IVORY, INK = hx('5B174F'), hx('B7006E'), hx('FF6411'), hx('61A80A'), hx('FCF8F5'), hx('321F35')
BLUSH, LILAC, WHITE, NIGHT, GLOW = hx('F6EAF3'), hx('CDB8D6'), hx('FFFFFF'), hx('14060F'), hx('E05FB4')


@functools.lru_cache(None)
def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', int(s))


# ------------------------------------------------------------------ backgrounds
@functools.lru_cache(None)
def light_bg():
    yy, xx = _grid()
    r = np.hypot((xx - W * 0.5) / W, (yy - H * 0.42) / H)
    c = WHITE * (1 - np.clip(r * 1.4, 0, 1))[..., None] + BLUSH * np.clip(r * 1.4, 0, 1)[..., None]
    c = c - np.clip(r - 0.35, 0, 1)[..., None] * np.array((0.10, 0.16, 0.10), np.float32)
    return np.clip(c, 0, 1).astype(np.float32)


@functools.lru_cache(None)
def dark_bg():
    yy, xx = _grid()
    r = np.hypot((xx - W * 0.5) / W, (yy - H * 0.45) / H)
    g = np.exp(-(r / 0.42) ** 2)
    c = NIGHT * (1 - g[..., None]) + PLUM * 0.55 * g[..., None]
    return c.astype(np.float32)


def blobs(c, t, col=PLUM, a=1.0, seed=0):
    """Curvy corner shapes drifting in (the reference's purple swooshes)."""
    lay = np.zeros((H // 2, W // 2), np.uint8)
    rng = np.random.default_rng(seed)
    for k, (cx, cy, r) in enumerate(((-40, -60, 260), (W // 2 + 60, H // 2 + 40, 300))):
        ph = t * 0.6 + k
        pts = []
        for i in range(40):
            ang = i / 40 * 2 * math.pi
            rr = r * (1 + 0.18 * math.sin(3 * ang + ph) + 0.08 * math.sin(5 * ang - ph))
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        cv2.fillPoly(lay, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    m = cv2.resize(lay, (W, H)).astype(np.float32)[..., None] / 255 * a
    c[:] = c * (1 - m) + col * m
    return c


# ------------------------------------------------------------------ type
def text_sprite(s, w, size, col=PLUM, alpha=1.0):
    f = F(w, size)
    l, tp, r, b = f.getbbox(s)
    asc, desc = f.getmetrics()
    im = Image.new('L', (int(r - l + 16), asc + desc + 16), 0)
    ImageDraw.Draw(im).text((8 - l, 8), s, font=f, fill=255)
    a = np.asarray(im, np.float32)[..., None] / 255 * alpha
    return np.dstack([a * np.asarray(col, np.float32), a])


def word(c, s, x, y, size, w=900, col=PLUM, u=1.0, anchor='c', rot=0.0, glow=None):
    """A kinetic word: pops up with overshoot (u = seconds since its cue)."""
    if u <= 0:
        return c
    k = e_back(clamp(u / 0.3), 1.4)
    spr = text_sprite(s, w, size * (0.6 + 0.4 * k), col, clamp(u / 0.12))
    if rot:
        hh, ww = spr.shape[:2]
        R = cv2.getRotationMatrix2D((ww / 2, hh / 2), rot, 1.0)
        spr = cv2.warpAffine(spr, R, (ww, hh), flags=cv2.INTER_CUBIC)
    ox = 0 if anchor == 'c' else (spr.shape[1] / 2 if anchor == 'l' else -spr.shape[1] / 2)
    if glow is not None:
        g = cv2.GaussianBlur(spr[..., 3], (0, 0), 16)
        paste(c, np.dstack([g[..., None] * np.asarray(glow, np.float32), g]).astype(np.float32) * 0.9, x + ox, y)
    return paste(c, spr, x + ox, y + 18 * (1 - k))


def typed(c, s, x, y, size, n, w=800, col=INK, caret=True, t=0.0, caret_col=MAG):
    """Left-aligned typed line showing the first n characters."""
    vis = s[:max(0, int(n))]
    f = F(w, size)
    if vis:
        spr = text_sprite(vis, w, size, col)
        paste(c, spr, x + spr.shape[1] / 2 - 8, y)
        x2 = x + f.getlength(vis)
    else:
        x2 = x
    if caret and int(t * 2.4) % 2 == 0:
        paste(c, rrect(5, size * 1.05, 2, caret_col), x2 + 6, y + 4)
    return c


def subtitle(c, s, y=1520, a=1.0):
    """Nunito subtitles (brief): white on a soft plum pill."""
    if not s or a <= 0:
        return c
    f = F(800, 44)
    lines = []
    cur = ''
    for wd in s.split():
        t2 = (cur + ' ' + wd).strip()
        if f.getlength(t2) > 860 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t2
    lines.append(cur)
    hgt = 62 * len(lines) + 34
    wid = max(f.getlength(l) for l in lines) + 64
    paste(c, rrect(wid, hgt, 28, PLUM, 0.86), W / 2, y, a)
    for i, l in enumerate(lines):
        paste(c, text_sprite(l, 800, 44, WHITE), W / 2, y - (len(lines) - 1) * 31 + i * 62 + 2, a)
    return c


def speaker(c, name, col=MAG, y=1420, a=1.0):
    s = text_sprite(name.upper(), 900, 28, WHITE)
    rr = rrect(s.shape[1] + 34, 50, 25, col)
    paste(c, rr, W / 2, y, a)
    paste(c, s, W / 2, y + 1, a)


# ------------------------------------------------------------------ 3D tokens
@functools.lru_cache(maxsize=256)
def token(name, size, rot=0):
    im = load(f'{S}/assets/{name}.png')
    a = im[..., 3]
    ys, xs = np.where(a > 0.02)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = size / max(im.shape[:2])
    im = cv2.resize(im, (max(1, int(im.shape[1] * sc)), max(1, int(im.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    if rot:
        h_, w_ = im.shape[:2]
        R = cv2.getRotationMatrix2D((w_ / 2, h_ / 2), rot, 1.0)
        cs, sn = abs(R[0, 0]), abs(R[0, 1])
        nw, nh = int(h_ * sn + w_ * cs), int(h_ * cs + w_ * sn)
        R[0, 2] += nw / 2 - w_ / 2
        R[1, 2] += nh / 2 - h_ / 2
        im = cv2.warpAffine(im, R, (nw, nh), flags=cv2.INTER_CUBIC)
    return im


def pop(c, name, cx, cy, size, u, rot=0, shadow=True, glow=None, a=1.0):
    if u <= 0 or a <= 0:
        return c
    s = e_back(clamp(u / 0.42))
    if s <= 0.02:
        return c
    spr = token(name, max(8, int(size * s)), int(rot))
    al = clamp(u / 0.12) * a
    bob = math.sin(u * 2.2) * 7 * clamp(u - 0.42)
    if shadow:
        sh = spr[..., 3]
        pad = 40
        m = np.zeros((sh.shape[0] + 2 * pad, sh.shape[1] + 2 * pad), np.float32)
        m[pad:-pad, pad:-pad] = sh
        m = cv2.GaussianBlur(m, (0, 0), 18) * 0.38
        sp = np.dstack([np.zeros(m.shape + (3,), np.float32) + PLUM * 0.3 * m[..., None], m])
        paste(c, sp, cx + 12, cy + 28 + bob, al)
    if glow is not None:
        gl = cv2.GaussianBlur(spr[..., 3], (0, 0), 30)
        paste(c, np.dstack([gl[..., None] * np.asarray(glow, np.float32), gl]).astype(np.float32) * 0.7, cx, cy + bob, al)
    return paste(c, spr, cx, cy + bob, al)


# ------------------------------------------------------------------ portrait circle + nodes + wipes
def circle_portrait(c, img, cx, cy, r, bw=1.0, ring_t=0.0, a=1.0, ring_col=PLUM):
    """Footage inside a circle (black-and-white -> colour), with a rotating dotted ring."""
    d = int(r * 2)
    im = cv2.resize(img, (d, d), interpolation=cv2.INTER_AREA) if img.shape[:2] != (d, d) else img
    g = im.mean(-1, keepdims=True)
    im = np.clip(g * bw + im * (1 - bw), 0, 1)
    if bw > 0.01:
        im = np.clip((im - 0.5) * (1 + 0.25 * bw) + 0.5, 0, 1)
    m = np.zeros((d * 4, d * 4), np.uint8)
    cv2.circle(m, (d * 2, d * 2), d * 2 - 2, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (d, d), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
    paste(c, np.dstack([im * m, m[..., 0]]), cx, cy, a)
    lay = np.zeros((H, W), np.uint8)
    n = 56
    for i in range(n):
        if i % 2:
            continue
        a0 = ring_t * 18 + i * 360 / n
        cv2.ellipse(lay, (int(cx * 4), int(cy * 4)), (int((r + 26) * 4), int((r + 26) * 4)), 0, a0, a0 + 360 / n * 0.9, 255, 4 * 4,
                    cv2.LINE_AA, shift=2)
    mm = lay.astype(np.float32)[..., None] / 255 * a
    c[:] = c * (1 - mm) + ring_col * mm
    return c


def node(c, cx, cy, u, icon=None, size=120, col=GLOW, label=None, lab_side=1):
    """Glowing round icon node (explainer path)."""
    if u <= 0:
        return c
    k = e_back(clamp(u / 0.35))
    r = size / 2 * k
    yy, xx = _grid()
    d = np.hypot(xx - cx, yy - cy)
    g = np.exp(-(d / (r * 1.6 + 1)) ** 2) * 0.55
    c[:] = c + g[..., None] * np.asarray(col, np.float32) * 0.6
    disc = np.clip(r - d, 0, 1.5) / 1.5
    c[:] = c * (1 - disc[..., None]) + np.asarray((0.95, 0.72, 0.9), np.float32) * disc[..., None]
    if icon is not None and k > 0.3:
        pop(c, icon, cx, cy, size * 0.95 * k, u, shadow=False)
    if label and u > 0.2:
        s = text_sprite(label, 800, 40, WHITE)
        paste(c, s, cx + lab_side * (r + 30 + s.shape[1] / 2), cy, clamp((u - 0.2) / 0.2))
    return c


def dotted_path(c, pts, frac, col=GLOW, a=1.0):
    p = np.array(pts, np.float32)
    seg = np.hypot(*np.diff(p, axis=0).T)
    tot = seg.sum()
    L = tot * clamp(frac)
    lay = np.zeros((H, W), np.uint8)
    acc = 0.0
    step = 26
    s = 0.0
    while s < L:
        i = min(int(np.searchsorted(np.cumsum(seg), s)), len(seg) - 1)
        s0 = s - (np.cumsum(seg)[i] - seg[i])
        q = p[i] + (p[i + 1] - p[i]) * (s0 / max(seg[i], 1e-6))
        cv2.circle(lay, (int(q[0] * 4), int(q[1] * 4)), 5 * 4, 255, -1, cv2.LINE_AA, shift=2)
        s += step
    m = lay.astype(np.float32)[..., None] / 255 * a
    c[:] = c * (1 - m) + np.asarray(col, np.float32) * m
    return c


def circle_wipe(a_img, b_img, u, cx=W / 2, cy=H / 2, col=None):
    """A circle grows from (cx, cy) revealing b over a; optional coloured rim."""
    if u <= 0:
        return a_img
    if u >= 1:
        return b_img
    yy, xx = _grid()
    R = e_inout(u) * math.hypot(W, H)
    d = np.hypot(xx - cx, yy - cy)
    m = np.clip((R - d) / 2.0, 0, 1)[..., None]
    out = a_img * (1 - m) + b_img * m
    if col is not None:
        rim = np.clip(1 - np.abs(d - R) / 22, 0, 1)[..., None]
        out = out * (1 - rim) + np.asarray(col, np.float32) * rim
    return out


def spiral_warp(img, u, cx=W / 2, cy=H / 2):
    """Spiral twist + zoom into a point (u 0..1)."""
    if u <= 0:
        return img
    yy, xx = _grid()
    dx, dy = xx - cx, yy - cy
    r = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx) + u * 4.0 * np.exp(-r / 700)
    z = 1 + u * 1.6
    mx = (cx + r / z * np.cos(ang)).astype(np.float32)
    my = (cy + r / z * np.sin(ang)).astype(np.float32)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def colour_bar(c, y=H - 16, h=16):
    for i, col in enumerate((MAG, ORANGE, GREEN)):
        c[y:y + h, int(W * i / 3):int(W * (i + 1) / 3)] = col
    return c


@functools.lru_cache(None)
def logo(width=700):
    lg = load(f'{ROOT}/workspace_three/web/logo.png')
    a = lg[..., 3]
    ys, xs = np.where(a > 0.02)
    lg = lg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return cv2.resize(lg, (width, int(lg.shape[0] * width / lg.shape[1])), interpolation=cv2.INTER_AREA)
