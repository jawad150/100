"""Look for Organic Fostering "One question is enough" (9:16), after the Pinterest reference: a dark textured paper
background, bold white type, a magnifying glass reading the headline (real lens magnification), a ring sweep
(eclipse) between beats, icons in circles with labels (explainer), typewriter lines (retro), cards spiralling into one
speech bubble (spiral), headline slices (layercut), a soft aurora glow (aurora), warm-ivory end card with the logo.
Brand: deep plum, warm ivory, small magenta accent; bold Nunito.
"""
import os, sys, math, functools
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_notes'))
import frames_notes as N
from frames_notes import (W, H, PLUM, MAG, ORANGE, GREEN, IVORY, INK, WHITE, GLOW, word, typed, subtitle, paste, rrect, text_sprite,
                          layercut, eclipse, aurora, grain, clamp, prog, e_out, e_inout, e_back, _grid, colour_bar, logo, F)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_oneq'
N.S = S                      # 3D tokens come from this reel's asset folder
N.token.cache_clear()
pop = N.pop
DEEP = np.array((0.30, 0.07, 0.26), np.float32)


@functools.lru_cache(None)
def paper(col=tuple(DEEP)):
    """Deep plum paper: soft mottling + fine fibres + vignette (like the reference's textured card)."""
    rng = np.random.default_rng(4)
    base = np.array(col, np.float32)
    m = cv2.resize(rng.normal(0, 1, (H // 60, W // 60)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    m2 = cv2.resize(rng.normal(0, 1, (H // 12, W // 12)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    fib = np.zeros((H, W), np.float32)
    for _ in range(900):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(8, 40)
        cv2.line(fib, (int(x), int(y)), (int(x + L * math.cos(a)), int(y + L * math.sin(a))), float(rng.uniform(0.3, 1)), 1, cv2.LINE_AA)
    c = base[None, None] * (1 + 0.08 * m[..., None] + 0.04 * m2[..., None]) + fib[..., None] * 0.025
    yy, xx = _grid()
    r = np.hypot((xx - W / 2) / W, (yy - H * 0.45) / H)
    c = c * np.clip(1.08 - 0.55 * r ** 1.6, 0, 1.1)[..., None]
    return np.clip(c, 0, 1).astype(np.float32)


@functools.lru_cache(None)
def ivory_paper():
    rng = np.random.default_rng(7)
    m = cv2.resize(rng.normal(0, 1, (H // 50, W // 50)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    c = IVORY[None, None] * (1 + 0.0035 * m[..., None])
    return np.clip(c, 0, 1).astype(np.float32)


def lens(c, cx, cy, r, zoom=1.7, a=1.0):
    """Magnify the frame inside a circle (the magnifying glass reading the headline)."""
    yy, xx = _grid()
    dx, dy = xx - cx, yy - cy
    d = np.hypot(dx, dy)
    inside = d < r
    k = 1.0 / zoom
    mx = np.where(inside, cx + dx * k, xx).astype(np.float32)
    my = np.where(inside, cy + dy * k, yy).astype(np.float32)
    z = cv2.remap(c, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    edge = np.clip((r - d) / 2.0, 0, 1)[..., None] * a
    out = c * (1 - edge) + z * edge
    ring = np.clip(1 - np.abs(d - r) / 9, 0, 1)[..., None] * a
    shine = np.clip(1 - np.hypot(dx + r * 0.35, dy + r * 0.35) / (r * 0.5), 0, 1)[..., None] * 0.12 * a * inside[..., None]
    return np.clip(out * (1 - ring) + np.array((0.95, 0.88, 0.93), np.float32) * ring + shine, 0, 1)


def ring_sweep(c, cx, cy, r, u, col=(0.92, 0.84, 0.9), width=14):
    """The reference's arc that sweeps round to wipe one beat to the next."""
    if u <= 0:
        return c
    lay = np.zeros((H, W), np.uint8)
    a1 = -90 + 360 * e_inout(clamp(u))
    a0 = -90 + 360 * e_inout(clamp(u - 0.35) / 0.65) if u > 0.35 else -90
    cv2.ellipse(lay, (int(cx * 4), int(cy * 4)), (int(r * 4), int(r * 4)), 0, a0, a1, 255, width * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    return c * (1 - m) + np.asarray(col, np.float32) * m


def icon_circle(c, cx, cy, r, name, u, label=None, a=1.0, ring_col=(0.92, 0.84, 0.9)):
    """Explainer icon: thin ring + 3D object inside + small label under it."""
    if u <= 0 or a <= 0:
        return c
    k = e_back(clamp(u / 0.35))
    lay = np.zeros((H, W), np.uint8)
    cv2.circle(lay, (int(cx * 4), int(cy * 4)), int(r * k * 4), 255, 4 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * a
    c[:] = c * (1 - m) + np.asarray(ring_col, np.float32) * m
    pop(c, name, cx, cy, r * 1.45, u, shadow=False, a=a)
    if label:
        s = text_sprite(label, 700, 34, (0.93, 0.86, 0.91))
        paste(c, s, cx, cy + r + 46, clamp((u - 0.15) / 0.2) * a)
    return c


def card(c, text, cx, cy, w, name, u, a=1.0, scale=1.0, rot=0.0, tint=IVORY):
    """A question card: ivory rounded card, plum text, 3D icon at its left."""
    if u <= 0 or a <= 0:
        return c
    k = e_back(clamp(u / 0.35)) * scale
    ww, hh = int(w * k), int(170 * k)
    if ww < 8:
        return c
    spr = rrect(ww, hh, 36 * k, tint, 1.0)
    txt = text_sprite(text, 900, 46 * k, PLUM)
    if txt.shape[1] > ww - 200 * k:
        f = (ww - 200 * k) / txt.shape[1]
        txt = text_sprite(text, 900, 46 * k * f, PLUM)
    paste(spr, txt, ww / 2 + 60 * k, hh / 2) if False else None
    out = spr.copy()
    # compose text into the card sprite
    th, tw = txt.shape[:2]
    x0 = int(150 * k)
    y0 = int(hh / 2 - th / 2)
    reg = out[max(0, y0):y0 + th, x0:x0 + tw]
    t_ = txt[:reg.shape[0], :reg.shape[1]]
    reg[..., :3] = reg[..., :3] * (1 - t_[..., 3:4]) + t_[..., :3]
    if rot:
        R = cv2.getRotationMatrix2D((ww / 2, hh / 2), rot, 1.0)
        out = cv2.warpAffine(out, R, (ww, hh), flags=cv2.INTER_CUBIC)
    sh = cv2.GaussianBlur(out[..., 3], (0, 0), 14) * 0.45
    paste(c, np.dstack([np.zeros(sh.shape + (3,), np.float32), sh]), cx + 8, cy + 16, a)
    paste(c, out, cx, cy, a)
    pop(c, name, cx - ww / 2 + 80 * k, cy, 150 * k, u, shadow=False, a=a)
    return c
