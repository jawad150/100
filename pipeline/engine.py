"""Tiny 2.5D motion-graphics compositor (numpy + OpenCV).

Canvas: float32 HxWx3, linear-ish sRGB values in [0,1] (opaque).
Sprites: float32 hxwx4, premultiplied alpha.
"""
import math, os, functools, glob
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(1)

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
FONTS = S + '/fonts'
W, H = 1080, 1920
CX, CY = W / 2, H / 2
FOCAL = 1500.0

# ------------------------------------------------------------------ easing

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def prog(t, a, b):
    """0..1 progress of t within [a,b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))

def e_out_expo(x):
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)

def e_in_expo(x):
    return 0.0 if x <= 0 else 2 ** (10 * x - 10)

def e_inout_expo(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 2 ** (20 * x - 10) / 2 if x < 0.5 else (2 - 2 ** (-20 * x + 10)) / 2

def e_out_cubic(x):
    return 1 - (1 - x) ** 3

def e_in_cubic(x):
    return x ** 3

def e_inout_cubic(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

def e_out_back(x, s=1.70158):
    c3 = s + 1
    return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2

def e_out_quint(x):
    return 1 - (1 - x) ** 5

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def wobble(t, f=0.5, a=1.0, ph=0.0):
    return a * math.sin(2 * math.pi * f * t + ph)

# ------------------------------------------------------------------ colors

def hexc(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

ORANGE = hexc('#FF6A00')
ORANGE2 = hexc('#FF8A1F')
ORANGE_HOT = hexc('#FFB347')
ORANGE_DEEP = hexc('#E04300')
WHITE = hexc('#F6F3EE')
MUTED = hexc('#9C958D')
LIME = hexc('#D1FE17')

# ------------------------------------------------------------------ sprite utils

def to_premul(rgba_u8):
    a = rgba_u8[..., 3:4].astype(np.float32) / 255.0
    rgb = rgba_u8[..., :3].astype(np.float32) / 255.0
    return np.concatenate([rgb * a, a], axis=2).astype(np.float32)

def pil_to_sprite(im):
    return to_premul(np.asarray(im.convert('RGBA')))

def pad(spr, p):
    return np.pad(spr, ((p, p), (p, p), (0, 0)))

@functools.lru_cache(maxsize=None)
def load_png_sprite(path):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.concatenate([im, np.full(im.shape[:2] + (1,), 255, np.uint8)], 2)
    im = im[..., [2, 1, 0, 3]]
    return pad(to_premul(im), 2)

def blur_sprite(spr, sigma):
    if sigma < 0.3:
        return spr
    p = int(sigma * 3) + 2
    s = pad(spr, p)
    return cv2.GaussianBlur(s, (0, 0), sigma)

def tint(spr, rgb, amount=1.0):
    out = spr.copy()
    a = spr[..., 3:4]
    col = np.array(rgb[:3], np.float32) * a
    out[..., :3] = spr[..., :3] * (1 - amount) + col * amount
    return out

# mip cache for downscaled draws
_mips = {}

def _mip(spr, scale):
    """Return (sprite_level, factor) where factor = level_size / original_size."""
    if scale >= 0.7:
        return spr, 1.0
    key = id(spr)
    lv = _mips.get(key)
    if lv is None or lv[0] is not spr:
        lv = (spr, {})
        _mips[key] = lv
        if len(_mips) > 400:
            _mips.clear()
            _mips[key] = lv
    f = 1.0
    while scale / f < 0.7 and f > 1 / 32:
        f *= 0.5
    d = lv[1]
    if f not in d:
        h, w = spr.shape[:2]
        d[f] = cv2.resize(spr, (max(1, int(round(w * f))), max(1, int(round(h * f)))), interpolation=cv2.INTER_AREA)
    s = d[f]
    return s, s.shape[1] / spr.shape[1]

# ------------------------------------------------------------------ compositing

def composite(canvas, spr, x0, y0, opacity=1.0, mode='over'):
    """Blit a sprite (premul RGBA) at integer position."""
    h, w = spr.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x0 + w), min(canvas.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0 or opacity <= 0.001:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    dst = canvas[Y0:Y1, X0:X1]
    if mode == 'add':
        dst += s[..., :3] * opacity
    elif mode == 'screen':
        src = s[..., :3] * opacity
        dst[:] = 1 - (1 - dst) * (1 - src)
    else:
        a = s[..., 3:4] * opacity
        dst *= (1 - a)
        dst += s[..., :3] * opacity

def warp(canvas, spr, quad, opacity=1.0, mode='over'):
    """Draw sprite so its corners map to quad [(x,y)*4] (TL,TR,BR,BL)."""
    if opacity <= 0.001:
        return
    q = np.asarray(quad, np.float32)
    xs, ys = q[:, 0], q[:, 1]
    x0 = int(math.floor(xs.min())) - 1
    y0 = int(math.floor(ys.min())) - 1
    x1 = int(math.ceil(xs.max())) + 1
    y1 = int(math.ceil(ys.max())) + 1
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    if X1 <= X0 or Y1 <= Y0:
        return
    h, w = spr.shape[:2]
    # approximate scale for mipmapping
    area = 0.5 * abs((xs[0] * ys[1] - xs[1] * ys[0]) + (xs[1] * ys[2] - xs[2] * ys[1]) +
                     (xs[2] * ys[3] - xs[3] * ys[2]) + (xs[3] * ys[0] - xs[0] * ys[3]))
    sc = math.sqrt(max(area, 1e-6) / (w * h))
    s2, f = _mip(spr, sc)
    h2, w2 = s2.shape[:2]
    src = np.float32([[0, 0], [w2, 0], [w2, h2], [0, h2]])
    dst = q - np.float32([X0, Y0])
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(s2, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    composite(canvas, out, X0, Y0, opacity, mode)

def quad_2d(cx, cy, w, h, scale=1.0, rot=0.0, ax=0.5, ay=0.5):
    """Quad for a 2D transform: position of anchor (ax,ay) at (cx,cy)."""
    w2, h2 = w * scale, h * scale
    pts = [(-ax * w2, -ay * h2), ((1 - ax) * w2, -ay * h2), ((1 - ax) * w2, (1 - ay) * h2), (-ax * w2, (1 - ay) * h2)]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]

def draw(canvas, spr, cx, cy, scale=1.0, rot=0.0, opacity=1.0, mode='over', ax=0.5, ay=0.5):
    h, w = spr.shape[:2]
    if abs(scale - 1) < 1e-4 and abs(rot) < 1e-4:
        composite(canvas, spr, int(round(cx - ax * w)), int(round(cy - ay * h)), opacity, mode)
    else:
        warp(canvas, spr, quad_2d(cx, cy, w, h, scale, rot, ax, ay), opacity, mode)

# ------------------------------------------------------------------ 3D

class Cam:
    def __init__(self, x=0, y=0, z=0, rx=0, ry=0, rz=0, focal=FOCAL):
        self.x, self.y, self.z, self.rx, self.ry, self.rz, self.focal = x, y, z, rx, ry, rz, focal

def rotm(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def project_pts(P, cam=None):
    """P: Nx3 world points (x,y in canvas px, z depth away from viewer). Returns Nx2, ok flag."""
    P = np.asarray(P, np.float64)
    if cam is not None:
        P = P - np.array([CX + cam.x, CY + cam.y, cam.z])
        if cam.rx or cam.ry or cam.rz:
            P = P @ rotm(cam.rx, cam.ry, cam.rz)
        P = P + np.array([CX, CY, 0])
        f = cam.focal
    else:
        f = FOCAL
    d = f + P[:, 2]
    ok = bool((d > 60).all())
    d = np.maximum(d, 60)
    s = f / d
    return np.stack([CX + (P[:, 0] - CX) * s, CY + (P[:, 1] - CY) * s], 1), ok

def plane_quad(cx, cy, cz, w, h, rx=0, ry=0, rz=0, cam=None):
    loc = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]], np.float64)
    R = rotm(rx, ry, rz)
    P = loc @ R.T + np.array([cx, cy, cz])
    return project_pts(P, cam)

def draw3d(canvas, spr, cx, cy, cz=0, w=None, h=None, rx=0, ry=0, rz=0, cam=None, opacity=1.0, mode='over'):
    sh, sw = spr.shape[:2]
    if w is None and h is None:
        w, h = sw, sh
    elif h is None:
        h = w * sh / sw
    elif w is None:
        w = h * sw / sh
    q, ok = plane_quad(cx, cy, cz, w, h, rx, ry, rz, cam)
    if ok:
        warp(canvas, spr, q, opacity, mode)
    return q

def homography_for(spr_w, spr_h, quad):
    src = np.float32([[0, 0], [spr_w, 0], [spr_w, spr_h], [0, spr_h]])
    return cv2.getPerspectiveTransform(src, np.float32(quad))

def apply_h(M, x, y):
    v = M @ np.array([x, y, 1.0])
    return v[0] / v[2], v[1] / v[2]

# ------------------------------------------------------------------ shapes (SDF)

def rrect_alpha(w, h, r, pad_px=0, ss=1.0):
    """Anti-aliased rounded-rect alpha of size (h+2p, w+2p)."""
    W2, H2 = w + 2 * pad_px, h + 2 * pad_px
    ys, xs = np.mgrid[0:H2, 0:W2].astype(np.float32)
    xs = xs + 0.5 - pad_px - w / 2
    ys = ys + 0.5 - pad_px - h / 2
    qx = np.abs(xs) - (w / 2 - r)
    qy = np.abs(ys) - (h / 2 - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return d

def sdf_fill(d):
    return np.clip(0.5 - d, 0, 1).astype(np.float32)

def sdf_stroke(d, width):
    return np.clip(0.5 - (np.abs(d + width / 2) - width / 2), 0, 1).astype(np.float32)

def solid(alpha, color):
    c = np.array(color[:3], np.float32)
    a = alpha * color[3]
    return np.concatenate([a[..., None] * c, a[..., None]], 2).astype(np.float32)

def vgrad(h, w, c0, c1):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    c0 = np.array(c0[:3], np.float32); c1 = np.array(c1[:3], np.float32)
    return np.broadcast_to(c0 * (1 - t) + c1 * t, (h, w, 3)).copy()

def hgrad(h, w, c0, c1):
    t = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    c0 = np.array(c0[:3], np.float32); c1 = np.array(c1[:3], np.float32)
    return np.broadcast_to(c0 * (1 - t) + c1 * t, (h, w, 3)).copy()

def over_spr(a, b):
    """b over a (same size premul)."""
    return b + a * (1 - b[..., 3:4])

def glow_of(spr, sigma, color=None, strength=1.0):
    s = spr if color is None else tint(spr, color)
    return blur_sprite(s, sigma) * strength

# ------------------------------------------------------------------ text

@functools.lru_cache(maxsize=None)
def font(name, size):
    return ImageFont.truetype(f'{FONTS}/{name}.ttf', size)

def text_mask(txt, fname, size, tracking=0.0):
    """Returns float alpha mask (h,w) tightly around text with small padding, plus baseline info."""
    f = font(fname, size)
    asc, desc = f.getmetrics()
    if tracking == 0:
        bbox = f.getbbox(txt)
        wid = bbox[2] + 4
    else:
        wid = int(sum(f.getlength(ch) + tracking * size for ch in txt) - tracking * size) + 8
    hgt = asc + desc
    p = 6
    im = Image.new('L', (int(wid) + 2 * p, hgt + 2 * p), 0)
    d = ImageDraw.Draw(im)
    if tracking == 0:
        d.text((p, p), txt, font=f, fill=255)
    else:
        x = p
        for ch in txt:
            d.text((x, p), ch, font=f, fill=255)
            x += f.getlength(ch) + tracking * size
    a = np.asarray(im).astype(np.float32) / 255.0
    # trim horizontally/vertically (keep a margin)
    ys, xs = np.where(a > 0.004)
    if len(xs) == 0:
        return a
    m = 4
    a = a[max(0, ys.min() - m):ys.max() + m + 1, max(0, xs.min() - m):xs.max() + m + 1]
    return a

_text_cache = {}

def text_sprite(txt, fname, size, color=WHITE, tracking=0.0, grad=None, glow=0.0):
    key = (txt, fname, size, color, tracking, grad)
    if key in _text_cache:
        return _text_cache[key]
    a = text_mask(txt, fname, size, tracking)
    h, w = a.shape
    if grad is not None:
        rgb = vgrad(h, w, grad[0], grad[1])
        spr = np.concatenate([rgb * a[..., None], a[..., None]], 2).astype(np.float32)
    else:
        spr = solid(a, color)
    spr = pad(spr, 3)
    _text_cache[key] = spr
    return spr

def fit_size(txt, fname, max_w, start=200, tracking=0.0):
    s = start
    while s > 8:
        a = text_mask(txt, fname, s, tracking)
        if a.shape[1] <= max_w:
            return s
        s -= 2
    return s

# ------------------------------------------------------------------ UI pieces

def pill(text, fname='Inter-700', size=30, pad_x=28, pad_y=16, fill=(1, 1, 1, 0.07), border=(1, 1, 1, 0.16),
         text_color=WHITE, dot=None, icon=None, grad=None, radius=None, tracking=0.02, min_w=0, glow=None):
    ts = text_sprite(text, fname, size, text_color, tracking)
    th, tw = ts.shape[:2]
    left = 0
    if dot is not None:
        left = 26
    if icon is not None:
        left = icon.shape[1] + 12
    w = max(min_w, tw + 2 * pad_x + left - 6)
    h = th + 2 * pad_y - 6
    r = h / 2 if radius is None else radius
    P = 30
    d = rrect_alpha(w, h, r, P)
    body = sdf_fill(d)
    if grad is not None:
        rgb = hgrad(body.shape[0], body.shape[1], grad[0], grad[1])
        spr = np.concatenate([rgb * body[..., None], body[..., None]], 2).astype(np.float32)
    else:
        spr = solid(body, fill)
    if border is not None:
        spr = over_spr(spr, solid(sdf_stroke(d, 1.6), border))
    if glow is not None:
        g = solid(sdf_fill(d), glow)
        g = cv2.GaussianBlur(g, (0, 0), 12)
        spr = over_spr(g, spr)
    x = P + pad_x - 3
    cy = P + h / 2
    if dot is not None:
        dd = np.sqrt((np.mgrid[0:spr.shape[0], 0:spr.shape[1]][1] - (x + 6)) ** 2 +
                     (np.mgrid[0:spr.shape[0], 0:spr.shape[1]][0] - cy) ** 2).astype(np.float32)
        da = np.clip(6.5 - dd, 0, 1)
        dg = np.clip(1 - dd / 22, 0, 1) ** 2 * 0.55
        spr = over_spr(spr, solid(dg, dot))
        spr = over_spr(spr, solid(da, dot))
        x += 26
    if icon is not None:
        ih, iw = icon.shape[:2]
        tmp = np.zeros_like(spr)
        y0 = int(round(cy - ih / 2))
        tmp[y0:y0 + ih, int(x):int(x) + iw] = icon
        spr = over_spr(spr, tmp)
        x += iw + 12
    tmp = np.zeros_like(spr)
    y0 = int(round(cy - th / 2))
    tmp[y0:y0 + th, int(x):int(x) + tw] = ts
    spr = over_spr(spr, tmp)
    return spr

def radial_sprite(size, color, power=2.0, core=0.0):
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.sqrt((xs - size / 2 + 0.5) ** 2 + (ys - size / 2 + 0.5) ** 2) / (size / 2)
    a = np.clip(1 - r, 0, 1) ** power
    if core:
        a = a + core * np.clip(1 - r * 6, 0, 1) ** 2
    c = np.array(color[:3], np.float32)
    return np.concatenate([a[..., None] * c, a[..., None]], 2).astype(np.float32)

def streak_sprite(w, h, color, core_color=(1, 1, 1)):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    x = (xs - w / 2) / (w / 2)
    y = (ys - h / 2) / (h / 2)
    fall = np.clip(1 - np.abs(x), 0, 1) ** 1.6
    a = np.exp(-(y * 6) ** 2) * fall
    core = np.exp(-(y * 22) ** 2) * np.clip(1 - np.abs(x) * 1.6, 0, 1) ** 2
    c = np.array(color[:3], np.float32)
    cc = np.array(core_color[:3], np.float32)
    rgb = a[..., None] * c + core[..., None] * cc
    return np.concatenate([rgb, np.clip(a + core, 0, 1)[..., None]], 2).astype(np.float32)

def ring_sprite(size, radius, width, color, glow=6):
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.sqrt((xs - size / 2) ** 2 + (ys - size / 2) ** 2)
    d = np.abs(r - radius) - width / 2
    a = np.clip(0.5 - d, 0, 1)
    g = np.exp(-np.maximum(d, 0) / glow) * 0.6
    c = np.array(color[:3], np.float32)
    aa = np.clip(a + g, 0, 1)
    return np.concatenate([aa[..., None] * c, aa[..., None]], 2).astype(np.float32)

# ------------------------------------------------------------------ assets

class Seq:
    """3D-rendered PNG sequence (from Blender)."""
    def __init__(self, name, fps=24, loop=True):
        self.files = sorted(glob.glob(f'{S}/assets/{name}/*.png'))
        self.fps, self.loop = fps, loop
        self.cache = {}
        # union alpha bbox over all frames so `size` means visible size
        x0 = y0 = 10 ** 9
        x1 = y1 = 0
        for f in self.files:
            a = cv2.imread(f, cv2.IMREAD_UNCHANGED)[..., 3]
            ys, xs = np.where(a > 8)
            if len(xs):
                x0, x1 = min(x0, xs.min()), max(x1, xs.max())
                y0, y1 = min(y0, ys.min()), max(y1, ys.max())
        m = 6
        if not self.files:
            x0 = y0 = 0
        self.bbox = (max(0, x0 - m), max(0, y0 - m), x1 + m + 1, y1 + m + 1)

    def frame(self, t, blur=0.0):
        n = len(self.files)
        if n == 0:
            return np.zeros((8, 8, 4), np.float32)
        i = int(t * self.fps)
        i = i % n if self.loop else min(max(i, 0), n - 1)
        b = round(blur * 2) / 2
        k = (i, b)
        if k not in self.cache:
            spr = load_png_sprite(self.files[i])
            bx0, by0, bx1, by1 = self.bbox
            spr = spr[by0 + 2:by1 + 2, bx0 + 2:bx1 + 2]
            if b > 0:
                spr = blur_sprite(spr, b)
            if len(self.cache) > 160:
                self.cache.clear()
            self.cache[k] = spr
        return self.cache[k]

# ------------------------------------------------------------------ video sources

class VideoFrames:
    def __init__(self, pattern, fps, start=0.0):
        self.files = sorted(glob.glob(pattern))
        self.fps, self.start = fps, start
        self.cache = {}

    def idx(self, t):
        return int(min(max((t - self.start) * self.fps + 1e-6, 0), len(self.files) - 1))

    def get(self, t):
        i = self.idx(t)
        if i not in self.cache:
            im = cv2.imread(self.files[i])[..., ::-1].astype(np.float32) / 255.0
            if len(self.cache) > 24:
                self.cache.pop(next(iter(self.cache)))
            self.cache[i] = im
        return self.cache[i]

def crop_resize(img, cx, cy, cw, ch, ow, oh):
    """Crop region centered (cx,cy) size (cw,ch) with clamping, resize to (ow,oh)."""
    Hs, Ws = img.shape[:2]
    cw, ch = min(cw, Ws), min(ch, Hs)
    x0 = clamp(cx - cw / 2, 0, Ws - cw)
    y0 = clamp(cy - ch / 2, 0, Hs - ch)
    sx, sy = ow / cw, oh / ch
    M = np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]])
    interp = cv2.INTER_AREA if sx < 0.8 else cv2.INTER_CUBIC
    if interp == cv2.INTER_AREA:
        sub = img[int(y0):int(math.ceil(y0 + ch)), int(x0):int(math.ceil(x0 + cw))]
        return cv2.resize(sub, (ow, oh), interpolation=cv2.INTER_AREA)
    return cv2.warpAffine(img, M, (ow, oh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def rgb_to_sprite(rgb, alpha):
    return np.concatenate([rgb * alpha[..., None], alpha[..., None]], 2).astype(np.float32)

# ------------------------------------------------------------------ post

_post = {}

def post_init(seed=7):
    rng = np.random.default_rng(seed)
    _post['grain'] = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xs - CX) / (W * 0.62)) ** 2 + ((ys - CY) / (H * 0.62)) ** 2)
    _post['vig'] = np.clip(1 - 0.42 * r ** 2.4, 0.35, 1)[..., None].astype(np.float32)

def post(canvas, frame_idx, bloom=0.55, grain=0.022, ca=0.0, flash=0.0, flash_color=(1, 0.55, 0.2), fade=0.0):
    if not _post:
        post_init()
    img = canvas
    # bloom
    if bloom > 0:
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        br = np.maximum(small - 0.62, 0)
        b1 = cv2.GaussianBlur(br, (0, 0), 5)
        b2 = cv2.GaussianBlur(br, (0, 0), 18)
        b = b1 * 0.6 + b2 * 1.0
        b = b * np.array([1.0, 0.78, 0.6], np.float32)
        img = img + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    if ca > 0.05:
        k = int(round(ca))
        if k >= 1:
            r = np.roll(img[..., 0], k, axis=1)
            b = np.roll(img[..., 2], -k, axis=1)
            img = np.stack([r, img[..., 1], b], 2)
    if flash > 0:
        img = img + np.array(flash_color, np.float32) * flash
    # soft shoulder
    img = np.where(img > 0.82, 0.82 + 0.18 * np.tanh((img - 0.82) / 0.18), img)
    img = img * _post['vig']
    # warm lift in the blacks
    img = img * 0.985 + np.array([0.012, 0.008, 0.006], np.float32)
    if grain > 0:
        g = _post['grain'][frame_idx % len(_post['grain'])]
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        img = img + g[..., None] * grain
    if fade > 0:
        img = img * (1 - fade)
    return np.clip(img, 0, 1)
