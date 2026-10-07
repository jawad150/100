"""reel3_fx.py: helper effects for reel3.py (REEL 3 "NURTURE · DEVELOP · GROW"). Pure functions, no side effects.

    plate(clip, t_src, cx, cy, width, focus=(u, v), look='airy') -> canvas-sized (H, W, 4) linear sprite:
        the WHOLE source frame scaled to `width` canvas px, source point `focus` (normalised) placed on canvas
        (cx, cy); transparent outside the frame. Used as the scene "behind" video-in-type letters: the letters
        are near the lens, the footage plate is far behind, so a zoom-through grows the letters ~40x while the
        plate only grows ~2-3x until it covers the frame (parallax) and the faces stay readable at rest.
    cover_width(clip, focus, cx, cy) -> smallest plate width that covers the canvas for that placement.
    soft_ellipse(w, h, feather) -> (h, w) alpha (cached), iris_mask(r, cx, cy, soft) -> canvas alpha.
"""
import functools
import math

import cv2
import numpy as np

import core as K
import footage as F


def _frame_u8(clip, t_src, reduce):
    f = clip.index(t_src)
    i0 = int(math.floor(f))
    w = f - i0
    a = clip._read(i0, reduce)
    if w < 0.01 or i0 + 1 >= clip.frames:
        return a
    if w > 0.99:
        return clip._read(i0 + 1, reduce)
    return cv2.addWeighted(a, 1.0 - w, clip._read(i0 + 1, reduce), w, 0.0)


def cover_width(clip, focus, cx, cy, W=K.W, H=K.H):
    """Smallest plate width so the scaled frame covers the whole canvas with focus at (cx, cy)."""
    u, v = focus
    asp = clip.w / clip.h
    need = [cx / max(u, 1e-3), (W - cx) / max(1 - u, 1e-3),
            asp * cy / max(v, 1e-3), asp * (H - cy) / max(1 - v, 1e-3)]
    return max(need)


def plate(clip, t_src, cx, cy, width, focus=(0.5, 0.5), look='airy', W=K.W, H=K.H, region=False, rot=0.0):
    """Footage plate (see module docstring). region=True returns (sprite, x0, y0) cropped to the visible part
    instead of a canvas-sized sprite (cheaper to composite). rot: degrees clockwise about the focus point."""
    if abs(rot) > 1e-3:
        return _plate_rot(clip, t_src, cx, cy, width, focus, look, W, H, rot)
    sw, sh = clip.w, clip.h
    scale = float(width) / sw
    pw, ph = sw * scale, sh * scale
    pl = cx - focus[0] * pw
    pt = cy - focus[1] * ph
    x0 = max(0, int(math.floor(pl)))
    y0 = max(0, int(math.floor(pt)))
    x1 = min(W, int(math.ceil(pl + pw)))
    y1 = min(H, int(math.ceil(pt + ph)))
    if x1 <= x0 or y1 <= y0:
        return (None, 0, 0) if region else np.zeros((H, W, 4), np.float32)
    r = 1
    while r < 8 and scale * r * 2 <= 1.0:
        r *= 2
    img = _frame_u8(clip, t_src, r)
    s = scale * r * (sw / r) / img.shape[1] if img.shape[1] else scale * r
    # crop the source to the visible part (+margin) before warping
    ix0 = max(0, int(math.floor((x0 - pl) / s)) - 3)
    iy0 = max(0, int(math.floor((y0 - pt) / s)) - 3)
    ix1 = min(img.shape[1], int(math.ceil((x1 - pl) / s)) + 3)
    iy1 = min(img.shape[0], int(math.ceil((y1 - pt) / s)) + 3)
    sub = img[iy0:iy1, ix0:ix1]
    if s < 0.85:
        sig = 0.5 * math.sqrt(1.0 / (s * s) - 1.0)
        sub = cv2.GaussianBlur(sub, (0, 0), sig)
    M = np.array([[s, 0.0, pl + (ix0 + 0.5) * s - 0.5 - x0], [0.0, s, pt + (iy0 + 0.5) * s - 0.5 - y0]])
    out = cv2.warpAffine(np.ascontiguousarray(sub), M, (x1 - x0, y1 - y0),
                         flags=cv2.INTER_CUBIC if s > 1.05 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    spr = F._to_sprite(out, look)
    xs = np.arange(x0, x1, dtype=np.float32)
    ys = np.arange(y0, y1, dtype=np.float32)
    ax = np.clip(np.minimum(xs + 1 - pl, pl + pw - xs), 0, 1)
    ay = np.clip(np.minimum(ys + 1 - pt, pt + ph - ys), 0, 1)
    if ax.min() < 1 or ay.min() < 1:
        spr *= (ay[:, None] * ax[None, :])[..., None]
    if region:
        return spr, x0, y0
    full = np.zeros((H, W, 4), np.float32)
    full[y0:y1, x0:x1] = spr
    return full


@functools.lru_cache(maxsize=16)
def soft_ellipse(w, h, feather=0.35, power=1.6):
    """(h, w) alpha: 1 in the middle, smooth falloff to 0 at the ellipse edge (feather = falloff fraction)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx + 0.5) / (w / 2) - 1) ** 2 + ((yy + 0.5) / (h / 2) - 1) ** 2)
    a = np.clip((1 - d) / feather, 0, 1) ** power
    a.setflags(write=False)
    return a


def circle_alpha(cx, cy, r, soft=1.2, W=K.W, H=K.H, box=None):
    """Anti-aliased disc alpha on a canvas-sized grid, computed only inside its bbox. Returns (a, x0, y0)."""
    x0 = max(0, int(math.floor(cx - r - 2)))
    y0 = max(0, int(math.floor(cy - r - 2)))
    x1 = min(W, int(math.ceil(cx + r + 2)))
    y1 = min(H, int(math.ceil(cy + r + 2)))
    if x1 <= x0 or y1 <= y0 or r <= 0:
        return None, 0, 0
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2)
    return np.clip((r - d) / soft + 0.5, 0, 1), x0, y0


def composite_region(cv, spr, x0, y0, alpha=None, opacity=1.0):
    """'over' a region sprite (premultiplied) at integer (x0, y0), optionally masked by alpha (same h, w)."""
    if spr is None:
        return cv
    h, w = spr.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(cv.shape[1], x0 + w), min(cv.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return cv
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    k = np.float32(opacity)
    if alpha is not None:
        a = alpha[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * k
        src = s * a
    else:
        src = s * k if opacity != 1.0 else s
    dst = cv[Y0:Y1, X0:X1]
    dst *= 1 - src[..., 3:4]
    dst += src
    return cv


def _plate_rot(clip, t_src, cx, cy, width, focus, look, W, H, rot):
    """Rotated plate (canvas-sized). Same mapping as plate() plus a clockwise rotation about the focus point."""
    sw, sh = clip.w, clip.h
    scale = float(width) / sw
    r = 1
    while r < 8 and scale * r * 2 <= 1.0:
        r *= 2
    img = _frame_u8(clip, t_src, r)
    s = width / img.shape[1]
    if s < 0.85:
        img = cv2.GaussianBlur(img, (0, 0), 0.5 * math.sqrt(1.0 / (s * s) - 1.0))
    fx, fy = focus[0] * img.shape[1], focus[1] * img.shape[0]
    a = math.radians(rot)
    c, n = math.cos(a) * s, math.sin(a) * s
    M = np.array([[c, -n, 0.0], [n, c, 0.0]])
    M[0, 2] = cx - (M[0, 0] * fx + M[0, 1] * fy) - 0.5 + (M[0, 0] + M[0, 1]) * 0.5
    M[1, 2] = cy - (M[1, 0] * fx + M[1, 1] * fy) - 0.5 + (M[1, 0] + M[1, 1]) * 0.5
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    ones = np.full(img.shape[:2], 255, np.uint8)
    al = cv2.warpAffine(ones, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    spr = F._to_sprite(out, look)
    spr *= (al.astype(np.float32) / 255.0)[..., None]
    return spr
