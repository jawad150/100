"""2.5D cinematic compositor for the Yaadein reel (linear-light float32, 1080x1920).

- 3D camera (position, roll, zoom) over depth-layered Blender plates -> real parallax
- true 3D sprite planes (photos, shards, web strands) projected through the same camera
- physically based lens blur (disc bokeh) from depth vs focus, for foreground 'depth' elements
- true shutter motion blur: each output frame averages N sub-frame renders across a 180 deg shutter
- post: halation/bloom, anamorphic streaks, red/blue split-tone grade, vignette, chroma fringe, grain
"""
import functools
import math
import os

import cv2
import numpy as np

W, H = 1080, 1920
FPS = 60
SHUTTER = 0.5 / FPS                  # 180 degree shutter
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace2'))
cv2.setNumThreads(2)


# ---------------------------------------------------------------- colour
def to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype(np.float32)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


@functools.lru_cache(maxsize=64)
def load(path, scale=1.0):
    """PNG/JPG -> premultiplied linear RGBA float32 (H, W, 4)."""
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise FileNotFoundError(path)
    if im.dtype == np.uint16:
        im = im.astype(np.float32) / 65535
    else:
        im = im.astype(np.float32) / 255
    if im.ndim == 2:
        im = np.dstack([im] * 3)
    if im.shape[2] == 3:
        im = np.dstack([im, np.ones(im.shape[:2], np.float32)])
    im = im[..., [2, 1, 0, 3]]
    if scale != 1.0:
        im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    rgb = to_lin(im[..., :3]) * im[..., 3:]
    return np.ascontiguousarray(np.dstack([rgb, im[..., 3]]))


# ---------------------------------------------------------------- camera
class Cam:
    """Camera at (x, y, z) metres looking down +Z; roll in degrees; zoom multiplies focal length.
    F is the canvas focal length in px (vertical fov ~ 50 deg). aperture = entrance pupil diameter (m),
    e.g. 0.035 for a 50mm at f/1.4."""

    def __init__(self, x=0.0, y=0.0, z=0.0, roll=0.0, zoom=1.0, F=2060.0, focus=5.0, aperture=0.0):
        self.x, self.y, self.z, self.roll, self.zoom, self.F = x, y, z, roll, zoom, F
        self.focus, self.aperture = focus, aperture

    def project(self, P):
        """P: (N,3) world points -> (N,2) canvas px, (N,) depth."""
        P = np.asarray(P, np.float64)
        d = P[:, 2] - self.z
        d = np.maximum(d, 1e-3)
        f = self.F * self.zoom
        x = (P[:, 0] - self.x) * f / d
        y = -(P[:, 1] - self.y) * f / d
        r = math.radians(self.roll)
        c, s = math.cos(r), math.sin(r)
        xr, yr = x * c - y * s, x * s + y * c
        return np.c_[xr + W / 2, yr + H / 2], d

    def coc(self, depth):
        """Circle of confusion diameter in px for a point at depth (m)."""
        if self.aperture <= 0:
            return 0.0
        d = max(depth - self.z, 1e-3)
        return min(260.0, abs(1.0 / self.focus - 1.0 / d) * self.aperture * self.F * self.zoom)

    def layer_matrix(self, depth, src_w, src_h, fill=1.0, offset=(0.0, 0.0)):
        """2x3 affine placing a full-frame plate shot at `depth` so it fills the canvas at rest."""
        d = max(depth - self.z, 1e-3)
        s = (depth / d) * self.zoom * fill * max(W / src_w, H / src_h)
        tx = -(self.x - offset[0]) * self.F * self.zoom / d
        ty = (self.y - offset[1]) * self.F * self.zoom / d
        r = math.radians(self.roll)
        c, sn = math.cos(r) * s, math.sin(r) * s
        # rotate/scale about plate centre, then move to canvas centre (+ parallax shift, rotated too)
        cx, cy = src_w / 2, src_h / 2
        txr = tx * math.cos(r) - ty * math.sin(r)
        tyr = tx * math.sin(r) + ty * math.cos(r)
        return np.float32([[c, -sn, W / 2 + txr - (c * cx - sn * cy)],
                           [sn, c, H / 2 + tyr - (sn * cx + c * cy)]])


def over(dst, src):
    """premultiplied src over dst (both HxWx4 or dst HxWx3 opaque)."""
    a = src[..., 3:4]
    dst[..., :3] = src[..., :3] + dst[..., :3] * (1 - a)
    if dst.shape[2] == 4:
        dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)
    return dst


def add(dst, src, k=1.0):
    dst[..., :3] += src[..., :3] * k
    return dst


def draw_plate(canvas, img, cam, depth, fill=1.0, opacity=1.0, offset=(0, 0), mode='over', blur=0.0):
    M = cam.layer_matrix(depth, img.shape[1], img.shape[0], fill, offset)
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101
                         if img[..., 3].min() > 0.999 else cv2.BORDER_CONSTANT)
    if blur > 0.3:
        out = disc_blur(out, blur)
    if opacity < 1:
        out *= opacity
    if mode == 'add':
        return add(canvas, out)
    return over(canvas, out)


# ---------------------------------------------------------------- lens blur
@functools.lru_cache(maxsize=64)
def _disc(r):
    r = max(0.5, r)
    n = int(math.ceil(r)) * 2 + 1
    yy, xx = np.mgrid[:n, :n] - n // 2
    k = np.clip(r + 0.5 - np.hypot(xx, yy), 0, 1).astype(np.float32)
    return k / k.sum()


def disc_blur(img, diameter):
    """Bokeh-shaped blur (diameter px). Large radii run at reduced resolution."""
    r = diameter / 2
    if r < 0.6:
        return img
    if r > 10:
        f = 8.0 / r
        small = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        small = cv2.filter2D(small, -1, _disc(8.0), borderType=cv2.BORDER_REPLICATE)
        return cv2.resize(small, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
    return cv2.filter2D(img, -1, _disc(round(r * 2) / 2), borderType=cv2.BORDER_REPLICATE)


# ---------------------------------------------------------------- 3D sprites
def plane_corners(center, size, rot):
    """World corners (TL, TR, BR, BL) of a w x h plane at center with Euler rot (deg, XYZ)."""
    w, h = size
    rx, ry, rz = (math.radians(a) for a in rot)
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    R = Rz @ Ry @ Rx
    loc = np.array([[-w / 2, h / 2, 0], [w / 2, h / 2, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0]])
    return loc @ R.T + np.asarray(center)


@functools.lru_cache(maxsize=256)
def _blurred_sprite(key, level):
    spr = _SPRITES[key]
    if level <= 0:
        return spr
    pad = int(level * 0.7) + 2
    p = cv2.copyMakeBorder(spr, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    return disc_blur(p, level)


_SPRITES = {}


def register(key, spr):
    _SPRITES[key] = spr
    return key


def draw_sprite3d(canvas, key, cam, center, size, rot, opacity=1.0, mode='over', extra_blur=0.0, tint=None):
    """Project a registered sprite onto a 3D plane; depth-of-field blur from its distance."""
    spr = _SPRITES[key]
    C = plane_corners(center, size, rot)
    pts, d = cam.project(C)
    if d.min() < 0.05:
        return canvas
    x0, y0 = pts.min(0)
    x1, y1 = pts.max(0)
    if x1 < -200 or y1 < -200 or x0 > W + 200 or y0 > H + 200 or (x1 - x0) * (y1 - y0) < 1:
        return canvas
    coc = cam.coc(float(np.mean(d))) + extra_blur
    # blur in sprite space: convert screen px to sprite px
    sx = spr.shape[1] / max(1.0, np.hypot(*(pts[1] - pts[0])))
    lvl = min(coc * sx, 0.6 * max(spr.shape[:2]))
    lvl = 0 if lvl < 1.0 else float(round(lvl * 2) / 2) if lvl < 12 else float(round(lvl / 4) * 4)
    src = _blurred_sprite(key, lvl)
    pad = (src.shape[0] - spr.shape[0]) / 2
    hh, ww = spr.shape[:2]
    S = np.float32([[pad, pad], [pad + ww, pad], [pad + ww, pad + hh], [pad, pad + hh]])
    # enlarge destination quad to include the blur padding
    D = pts.astype(np.float32)
    if pad > 0:
        Hm0 = cv2.getPerspectiveTransform(np.float32([[0, 0], [ww, 0], [ww, hh], [0, hh]]), D)
        S2 = np.float32([[-pad, -pad], [ww + pad, -pad], [ww + pad, hh + pad], [-pad, hh + pad]])
        D = cv2.perspectiveTransform(S2[None], Hm0)[0]
        S = np.float32([[0, 0], [src.shape[1], 0], [src.shape[1], src.shape[0]], [0, src.shape[0]]])
    M = cv2.getPerspectiveTransform(S, D)
    bx0, by0 = int(max(0, D[:, 0].min() - 2)), int(max(0, D[:, 1].min() - 2))
    bx1, by1 = int(min(W, D[:, 0].max() + 2)), int(min(H, D[:, 1].max() + 2))
    if bx1 <= bx0 or by1 <= by0:
        return canvas
    T = np.array([[1, 0, -bx0], [0, 1, -by0], [0, 0, 1]], np.float64)
    out = cv2.warpPerspective(src, T @ M, (bx1 - bx0, by1 - by0), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if tint is not None:
        out[..., :3] *= np.asarray(tint, np.float32)
    out *= opacity
    reg = canvas[by0:by1, bx0:bx1]
    if mode == 'add':
        reg[..., :3] += out[..., :3]
    else:
        over(reg, out)
    return canvas


def draw_img3d(canvas, img, cam, center, size, rot, opacity=1.0, blur=0.0, glass=None, mode='over'):
    """Project an (animated, uncached) premultiplied RGBA image onto a 3D plane.
    glass=(blurred_canvas, amount): frost what is behind the panel (uses the panel alpha)."""
    C_ = plane_corners(center, size, rot)
    pts, d = cam.project(C_)
    if d.min() < 0.05:
        return canvas
    hh, ww = img.shape[:2]
    coc = cam.coc(float(np.mean(d))) + blur
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [ww, 0], [ww, hh], [0, hh]]), pts.astype(np.float32))
    pad = int(coc) + 3
    bx0, by0 = int(max(0, pts[:, 0].min() - pad)), int(max(0, pts[:, 1].min() - pad))
    bx1, by1 = int(min(W, pts[:, 0].max() + pad)), int(min(H, pts[:, 1].max() + pad))
    if bx1 <= bx0 or by1 <= by0:
        return canvas
    T = np.array([[1, 0, -bx0], [0, 1, -by0], [0, 0, 1]], np.float64)
    out = cv2.warpPerspective(img, T @ M, (bx1 - bx0, by1 - by0), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if coc >= 1.0:
        out = disc_blur(out, coc)
    out *= opacity
    reg = canvas[by0:by1, bx0:bx1]
    if glass is not None:
        g = glass[0][by0:by1, bx0:bx1, :3]
        m = np.clip(out[..., 3:4] * 4.0, 0, 1) * glass[1]
        reg[..., :3] = reg[..., :3] * (1 - m) + g * m
    if mode == 'add':
        reg[..., :3] += out[..., :3]
    else:
        over(reg, out)
    return canvas


def frosted(canvas, sigma=26, dim=0.45):
    """Blurred, dimmed copy of the canvas for glass panels."""
    small = cv2.resize(canvas[..., :3], (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / 4)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR) * dim


# ---------------------------------------------------------------- particles
def particles(canvas, cam, P, radius, color, opacity=1.0, glow=1.0):
    """World points P (N,3) drawn as lens-blurred discs (bokeh grows with defocus), additive."""
    if len(P) == 0:
        return canvas
    pts, d = cam.project(P)
    f = cam.F * cam.zoom
    for (x, y), dd, r, c, o in zip(pts, d, np.broadcast_to(radius, len(P)), np.broadcast_to(color, (len(P), 3)),
                                   np.broadcast_to(opacity, len(P))):
        if dd < 0.1 or x < -80 or y < -80 or x > W + 80 or y > H + 80:
            continue
        rs = max(0.6, r * f / dd)
        coc = cam.coc(dd)
        R = max(rs, coc / 2)
        energy = (rs / R) ** 2                         # same light spread over a bigger disc
        a = o * energy * glow
        if a < 0.004:
            continue
        rr = int(math.ceil(R + 2))
        x0, y0 = int(x) - rr, int(y) - rr
        xa, ya = max(0, x0), max(0, y0)
        xb, yb = min(W, int(x) + rr + 1), min(H, int(y) + rr + 1)
        if xb <= xa or yb <= ya:
            continue
        yy, xx = np.mgrid[ya:yb, xa:xb]
        dist = np.hypot(xx - x, yy - y)
        disc = np.clip(R + 0.5 - dist, 0, 1)
        if R > 4:                                      # bokeh: slightly brighter rim
            disc *= 0.85 + 0.25 * np.clip((dist - R * 0.7) / (R * 0.3), 0, 1)
        canvas[ya:yb, xa:xb, :3] += (disc * a)[..., None] * np.asarray(c, np.float32)
    return canvas


def rain(canvas, cam, t, seed=1, n=900, area=(-6, 6, -3, 8, 1.0, 14.0), speed=9.0, wind=1.2,
         color=(0.75, 0.82, 1.0), opacity=0.22, streak=0.016):
    """Rain drops as world-space streaks; each drop's streak length = its travel during the shutter."""
    rng = np.random.default_rng(seed)
    x0, x1, y0, y1, z0, z1 = area
    X = rng.uniform(x0, x1, n)
    Z = rng.uniform(z0, z1, n)
    ph = rng.uniform(0, 1, n)
    v = speed * rng.uniform(0.85, 1.15, n)
    span = y1 - y0
    Y = y1 - ((ph * span + v * t) % span)
    Xw = X + wind * ((ph * span + v * t) % span) / speed
    top = np.c_[Xw, Y, Z]
    bot = np.c_[Xw + wind * streak * 6, Y - v * streak * 6, Z]
    pt, d = cam.project(top)
    pb, _ = cam.project(bot)
    layer = np.zeros((H, W), np.float32)
    for (xa, ya), (xb, yb), dd in zip(pt, pb, d):
        if dd < 0.3:
            continue
        if not (-50 < xa < W + 50 and -50 < ya < H + 50):
            continue
        th = 1 if dd > 4 else 2
        w8 = float(np.clip(2.5 / dd, 0.15, 1.0))
        cv2.line(layer, (int(xa * 4), int(ya * 4)), (int(xb * 4), int(yb * 4)), w8, th, cv2.LINE_AA, shift=2)
    layer = cv2.GaussianBlur(layer, (0, 0), 0.8)
    canvas[..., :3] += layer[..., None] * np.asarray(color, np.float32) * opacity
    return canvas


# ---------------------------------------------------------------- post
def bloom(img, threshold=0.75, strength=0.35, radii=(6, 18, 48), tint=(1.0, 0.85, 0.8)):
    hi = np.clip(img[..., :3] - threshold, 0, None)
    small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    acc = np.zeros_like(small)
    for r in radii:
        acc += cv2.GaussianBlur(small, (0, 0), r / 4)
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)
    img[..., :3] += acc * (strength / len(radii)) * np.asarray(tint, np.float32)
    return img


def halation(img, strength=0.18, threshold=0.55):
    """Film halation: red-orange fringe around bright edges."""
    hi = np.clip(img[..., :3].max(2) - threshold, 0, None)
    small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(small, (0, 0), 3.5)
    g = cv2.resize(g, (W, H))
    img[..., :3] += g[..., None] * np.array([1.0, 0.25, 0.08], np.float32) * strength
    return img


def anamorphic(img, threshold=1.2, strength=0.25, color=(0.35, 0.55, 1.0), length=0.5):
    hi = np.clip(img[..., :3].max(2) - threshold, 0, None)
    small = cv2.resize(hi, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    k = int(W // 8 * length) | 1
    streak = cv2.blur(small, (k, 1))
    streak = cv2.GaussianBlur(streak, (0, 0), 0.7)
    streak = cv2.resize(streak, (W, H))
    img[..., :3] += streak[..., None] * np.asarray(color, np.float32) * strength * 6
    return img


@functools.lru_cache(maxsize=4)
def _vignette(power=0.55):
    yy, xx = np.mgrid[:H, :W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r = np.sqrt(nx ** 2 * 1.0 + ny ** 2 * 0.62)
    return np.clip(1 - power * np.clip(r - 0.35, 0, None) ** 1.6, 0, 1).astype(np.float32)[..., None]


def chroma_fringe(img, amount=1.6):
    """Lateral chromatic aberration growing toward the frame edges."""
    if amount <= 0:
        return img
    out = img.copy()
    for ch, k in ((0, 1.0 + amount / 1000), (2, 1.0 - amount / 1000)):
        M = np.float32([[k, 0, (1 - k) * W / 2], [0, k, (1 - k) * H / 2]])
        out[..., ch] = cv2.warpAffine(img[..., ch], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out


def grade(img, look='spider', exposure=0.0, sat=1.0, contrast=1.0, vignette=0.55):
    """Linear in -> display sRGB out (H, W, 3). Filmic shoulder + split toning."""
    x = img[..., :3] * (2 ** exposure)
    # filmic shoulder (soft clip highlights)
    x = x / (1 + x * 0.18)
    s = to_srgb(np.clip(x, 0, 1))
    if look == 'spider':                       # shadows -> deep blue, highlights -> warm red/magenta
        lum = s @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        sh = np.clip(1 - lum / 0.45, 0, 1)[..., None]
        hl = np.clip((lum - 0.55) / 0.45, 0, 1)[..., None]
        s = s + sh * np.array([-0.012, 0.0, 0.035], np.float32) * 1.0 + hl * np.array([0.03, -0.01, -0.02], np.float32)
    elif look == 'memory':                     # warm golden flashback
        lum = s @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        sh = np.clip(1 - lum / 0.5, 0, 1)[..., None]
        s = s + sh * np.array([0.02, 0.0, -0.01], np.float32) + np.array([0.02, 0.008, -0.025], np.float32)
    elif look == 'orange':                     # brand end card
        pass
    if sat != 1.0:
        lum = (s @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        s = lum + (s - lum) * sat
    if contrast != 1.0:
        s = 0.5 + (s - 0.5) * contrast
        s = np.clip(s, 0, 1)
        s = s * s * (3 - 2 * s) * (contrast - 1) * 0.5 + s * (1 - (contrast - 1) * 0.5)
    s = s * _vignette(vignette)
    return np.clip(s, 0, 1)


def grain(s, t, amount=0.022, size=1.3):
    rng = np.random.default_rng(int(t * 1000) + 17)
    n = rng.standard_normal((int(H / size), int(W / size))).astype(np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)
    lum = s.mean(2, keepdims=True)
    w = 0.5 + 0.8 * lum * (1 - lum) * 4 * 0.5         # strongest in mids
    return np.clip(s + n[..., None] * amount * w, 0, 1)


# ---------------------------------------------------------------- frame renderer
def render_frame(draw, t, samples=1, shutter=SHUTTER):
    """Average `samples` sub-frame renders over the shutter interval centred on t (true motion blur)."""
    if samples <= 1:
        return draw(t)
    acc = None
    for i in range(samples):
        tt = t + (i + 0.5) / samples * shutter - shutter / 2
        f = draw(tt)
        acc = f if acc is None else acc + f
    return acc / samples
