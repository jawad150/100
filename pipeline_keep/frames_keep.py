"""Look for BMHC "What did you keep?" after the user's Pinterest reference: a monochrome editorial collage - light paper,
a faint dot grid, black-and-white cut-outs with soft shadows inside dotted circles, mixed bold/light type, numbered
beats, a black diagonal arrow wipe - with BMHC's Heritage Magenta as the one accent (the handwritten last line).
Brand: Inter (ExtraBold for subtitles: white on ink, 2-3 words), Heart Work tag in the first second, official logo.
Skills: eclipse (the thumb hiding the last line, then lifting), retro (grainy B&W photos), aurora (a soft glow over
the memory), spiral (the dotted ring spinning into the spoons), layercut (the reveal), explainer (numbered beats).
"""
import os, sys, math, functools
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_ai'))
import frames_ai as FA
from frames_ai import (W, H, INK, WHITE, MAG, TEAL, ORANGE, LIME, BARS, load, cover, paste, rrect, text_sprite, caption, F, clamp, prog,
                       e_out, e_inout, e_back, _grid, grain, logo, Clip, tag, layercut, aurora)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_keep'
PAPER = np.array((0.925, 0.918, 0.902), np.float32)
DARK = np.array((0.11, 0.11, 0.11), np.float32)
GREYT = np.array((0.45, 0.45, 0.45), np.float32)


@functools.lru_cache(None)
def paper():
    yy, xx = _grid()
    c = np.empty((H, W, 3), np.float32)
    c[:] = PAPER
    r = np.hypot((xx - W / 2) / W, (yy - H * 0.45) / H)
    c = c * (1.02 - 0.12 * r[..., None] ** 1.5)
    dots = ((xx.astype(int) % 54 == 27) & (yy.astype(int) % 54 == 27)).astype(np.float32)
    dots = cv2.GaussianBlur(dots, (0, 0), 1.2) * 3
    c = c - dots[..., None] * 0.06
    rng = np.random.default_rng(2)
    c = c + rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    return np.clip(c, 0, 1).astype(np.float32)


def bw(img, contrast=1.25, keep_mag=False):
    """Black-and-white collage treatment (keeps magenta pixels if asked: the one accent)."""
    rgb = img[..., :3]
    g = (rgb * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    g = np.clip((g - 0.5) * contrast + 0.5, 0, 1)
    out = np.repeat(g, 3, -1)
    if keep_mag:
        r, gg, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        a = img[..., 3] if img.shape[-1] == 4 else 1.0
        sat = np.clip((r - gg) * 3 - 0.2, 0, 1)[..., None]
        out = out * (1 - sat) + rgb * sat
    if img.shape[-1] == 4:
        out = out * (img[..., 3:4] > 0)
        return np.dstack([out * 1.0, img[..., 3]]).astype(np.float32)
    return out.astype(np.float32)


@functools.lru_cache(maxsize=128)
def token(name, size, rot=0, mono=True, keep_mag=True):
    im = load(f'{S}/assets/{name}.png')
    a = im[..., 3]
    ys, xs = np.where(a > 0.02)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = size / max(im.shape[:2])
    im = cv2.resize(im, (max(1, int(im.shape[1] * sc)), max(1, int(im.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    if mono:
        al = np.clip(im[..., 3:4], 1e-4, 1)
        straight = np.dstack([im[..., :3] / al, im[..., 3]])
        m = bw(straight, 1.2, keep_mag)
        im = np.dstack([m[..., :3] * im[..., 3:4], im[..., 3]])
    if rot:
        h_, w_ = im.shape[:2]
        R = cv2.getRotationMatrix2D((w_ / 2, h_ / 2), rot, 1.0)
        cs, sn = abs(R[0, 0]), abs(R[0, 1])
        nw, nh = int(h_ * sn + w_ * cs), int(h_ * cs + w_ * sn)
        R[0, 2] += nw / 2 - w_ / 2
        R[1, 2] += nh / 2 - h_ / 2
        im = cv2.warpAffine(im, R, (nw, nh), flags=cv2.INTER_CUBIC)
    return im


def place(c, name, cx, cy, size, u, rot=0, mono=True, a=1.0, slide=(0, 0)):
    """Cut-out placed into the collage: slides in from an offset with a soft paper shadow."""
    if u <= 0 or a <= 0:
        return c
    k = e_out(clamp(u / 0.45))
    spr = token(name, int(size), int(rot), mono)
    x = cx + slide[0] * (1 - k)
    y = cy + slide[1] * (1 - k)
    m = cv2.GaussianBlur(np.pad(spr[..., 3], 40), (0, 0), 14) * 0.35
    paste(c, np.dstack([np.zeros(m.shape + (3,), np.float32), m]), x + 12, y + 20, a * k)
    return paste(c, spr, x, y, a * clamp(u / 0.15))


def dotted_ring(c, cx, cy, r, t=0.0, u=1.0, col=DARK, n=90, width=3, frac=1.0):
    if u <= 0:
        return c
    lay = np.zeros((H, W), np.uint8)
    for i in range(int(n * frac)):
        if i % 2:
            continue
        a0 = -90 + i * 360 / n + t * 20
        cv2.ellipse(lay, (int(cx * 4), int(cy * 4)), (int(r * 4), int(r * 4)), 0, a0, a0 + 360 / n * 0.5, 255, width * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * clamp(u / 0.3) * 0.7
    c[:] = c * (1 - m) + np.asarray(col, np.float32) * m
    return c


def photo_circle(c, img, cx, cy, r, u, retro_t=0.0):
    """A grainy black-and-white photo inside a circle (retro)."""
    if u <= 0:
        return c
    k = e_back(clamp(u / 0.45), 1.2)
    rr = int(r * k)
    if rr < 4:
        return c
    im = bw(cover(img, 0.5, 0.5, 1.0, 2 * rr, 2 * rr), 1.3)
    rng = np.random.default_rng(int(retro_t * 24))
    im = np.clip(im + rng.normal(0, 0.05, (2 * rr, 2 * rr, 1)), 0, 1)
    m = np.zeros((2 * rr * 4, 2 * rr * 4), np.uint8)
    cv2.circle(m, (rr * 4, rr * 4), rr * 4 - 4, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (2 * rr, 2 * rr), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
    return paste(c, np.dstack([im * m, m[..., 0]]).astype(np.float32), cx, cy, clamp(u / 0.15))


def type2(c, bold, light, x, y, u, size=84, col_bold=DARK, col_light=GREYT, gap=0.95, anchor='l'):
    """Reference-style mixed type: a bold line and a light line under it, typed in."""
    if u <= 0:
        return c
    for i, (txt, w, col) in enumerate(((bold, 800, col_bold), (light, 400, col_light))):
        if not txt:
            continue
        ui = u - i * 0.25
        if ui <= 0:
            continue
        n = max(1, int(len(txt) * clamp(ui / (0.025 * len(txt) + 0.15))))
        s = text_sprite(txt[:n], w, size if i == 0 else int(size * 0.62), col)
        xx = x + s.shape[1] / 2 if anchor == 'l' else x
        paste(c, s, xx, y + i * size * gap)
    return c


def thumb_eclipse(c, x, y, r, u_cover, u_lift):
    """The thumb hiding the last line - a soft dark disc (eclipse) that slides away on the reveal."""
    if u_cover <= 0:
        return c
    k = e_out(clamp(u_cover / 0.4)) * (1 - e_inout(clamp(u_lift)))
    if k <= 0.01:
        return c
    off = 360 * e_inout(clamp(u_lift))
    yy, xx = _grid()
    d = np.hypot((xx - x - off) / 1.25, yy - y)
    m = np.clip((r - d) / 18, 0, 1)[..., None] * k
    glow = np.exp(-((d - r) / 26) ** 2)[..., None] * 0.25 * k
    c[:] = c * (1 - m) + np.array((0.16, 0.12, 0.11), np.float32) * m + np.array((1, 0.85, 0.7), np.float32) * glow * 0.4
    return c


def arrow_wipe(c, u):
    """The reference's thick black diagonal arrow sweeping across."""
    if u <= 0 or u >= 1:
        return c
    lay = np.zeros((H, W), np.uint8)
    k = e_inout(u)
    x0, y0 = -400 + 1900 * k, H + 300 - 2300 * k
    d = np.array((0.6, -1.0))
    d = d / np.linalg.norm(d)
    p0 = np.array((x0, y0)) - d * 1600
    p1 = np.array((x0, y0))
    cv2.line(lay, tuple((p0 * 4).astype(int)), tuple((p1 * 4).astype(int)), 255, 150 * 4, cv2.LINE_AA, shift=2)
    nrm = np.array((-d[1], d[0]))
    tip = [p1 + d * 230, p1 + nrm * 210, p1 - nrm * 210]
    cv2.fillPoly(lay, [(np.array(tip) * 4).astype(np.int32)], 255, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + DARK * m
    return c
