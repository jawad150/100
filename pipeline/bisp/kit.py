"""Drawing kit for the BISP reel: easing, text, vector icons, rounded-rect SDFs and the liquid-glass panel.

All frames are float32 RGB in 0..1 (H, W, 3). Layers are premultiplied RGBA float32 (h, w, 4).
"""
import os, math
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.environ.get('BISP_WS', os.path.join(HERE, '..', '..', 'workspace_bisp')))
FONTS = os.path.join(WS, 'fonts')

# ---- brand ----------------------------------------------------------------------------------------------------
def hexc(h, a=None):
    h = h.lstrip('#')
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)

GREEN = hexc('#0E7A43')       # BISP / Pakistan green (from the official banner)
GREEN_D = hexc('#06401F')
GREEN_L = hexc('#2FB56A')
GOLD = hexc('#F2C14E')        # banner gold
GOLD_L = hexc('#FFE9A8')
GOLD_D = hexc('#C88A1C')
WHITE = (1.0, 1.0, 1.0)
INK = hexc('#0B1A12')
RED = hexc('#E5484D')
AMBER = hexc('#FFB224')


# ---- easing -----------------------------------------------------------------------------------------------------
def clamp01(x):
    return 0.0 if x <= 0 else 1.0 if x >= 1 else x

def lin(t, a, b):
    return clamp01((t - a) / (b - a)) if b > a else float(t >= a)

def ease_out_cubic(x):
    x = clamp01(x); return 1 - (1 - x) ** 3

def ease_in_cubic(x):
    x = clamp01(x); return x ** 3

def ease_io(x):
    x = clamp01(x); return 3 * x * x - 2 * x * x * x

def ease_out_expo(x):
    x = clamp01(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)

def ease_in_expo(x):
    x = clamp01(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)

def ease_out_back(x, s=1.70158):
    x = clamp01(x); x -= 1; return x * x * ((s + 1) * x + s) + 1

def spring(x, freq=2.2, damp=5.5):
    """0 -> 1 with a soft overshoot, x in seconds-ish normalised units (0..1 ~ settle)."""
    if x <= 0: return 0.0
    return 1 - math.exp(-damp * x) * math.cos(2 * math.pi * freq * x)

def env(t, t_in, t_out, d_in=0.25, d_out=0.2):
    """0..1 presence: eased in at t_in, eased out at t_out."""
    if t < t_in or t > t_out + d_out: return 0.0
    a = ease_out_cubic(lin(t, t_in, t_in + d_in))
    b = 1 - ease_in_cubic(lin(t, t_out, t_out + d_out))
    return min(a, b)


# ---- layers -------------------------------------------------------------------------------------------------------
def to_layer(img):
    """PIL RGBA -> premultiplied float layer."""
    a = np.asarray(img, np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a

def scale_layer(L, s):
    if abs(s - 1) < 1e-3: return L
    h, w = L.shape[:2]
    nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
    return cv2.resize(L, (nw, nh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)

def blit(frame, L, cx, cy, alpha=1.0, scale=1.0, anchor='c', rot=0.0):
    """Composite premultiplied layer L onto frame with its anchor at (cx, cy)."""
    if alpha <= 0.002 or scale <= 0.01: return
    if rot:
        h, w = L.shape[:2]
        d = int(math.ceil(math.hypot(w, h))) + 2
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0)
        M[0, 2] += (d - w) / 2; M[1, 2] += (d - h) / 2
        L = cv2.warpAffine(L, M, (d, d), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    L = scale_layer(L, scale)
    h, w = L.shape[:2]
    if anchor == 'c': x0, y0 = cx - w / 2, cy - h / 2
    elif anchor == 'l': x0, y0 = cx, cy - h / 2
    elif anchor == 'r': x0, y0 = cx - w, cy - h / 2
    elif anchor == 'tl': x0, y0 = cx, cy
    else: x0, y0 = cx - w / 2, cy - h / 2
    # sub-pixel position: shift with warpAffine only when fractional part matters (keeps text crisp otherwise)
    xi, yi = int(math.floor(x0)), int(math.floor(y0))
    fx, fy = x0 - xi, y0 - yi
    if fx > 0.05 or fy > 0.05:
        M = np.float32([[1, 0, fx], [0, 1, fy]])
        L = cv2.warpAffine(L, M, (w + 1, h + 1), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        h, w = L.shape[:2]
    H, W = frame.shape[:2]
    ax0, ay0, ax1, ay1 = max(0, xi), max(0, yi), min(W, xi + w), min(H, yi + h)
    if ax1 <= ax0 or ay1 <= ay0: return
    sub = L[ay0 - yi:ay1 - yi, ax0 - xi:ax1 - xi]
    a = sub[..., 3:4] * alpha
    frame[ay0:ay1, ax0:ax1] = frame[ay0:ay1, ax0:ax1] * (1 - a) + sub[..., :3] * alpha


# ---- text ---------------------------------------------------------------------------------------------------------
FONT_FILES = {
    'black': 'Poppins-900.ttf', 'xbold': 'Poppins-800.ttf', 'bold': 'Poppins-700.ttf', 'semi': 'Poppins-600.ttf',
    'med': 'Poppins-500.ttf', 'ui': 'Inter-600.ttf', 'ui_b': 'Inter-700.ttf', 'ui_x': 'Inter-800.ttf',
    'ui_m': 'Inter-500.ttf',
}

@lru_cache(64)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, FONT_FILES.get(name, name)), int(size))

def text_size(s, fname, size, tracking=0):
    f = font(fname, size)
    if tracking:
        return sum(f.getlength(ch) for ch in s) + tracking * (len(s) - 1), size
    return f.getlength(s), size

@lru_cache(2048)
def text_layer(s, fname, size, color=(1, 1, 1), stroke=0, stroke_color=(0, 0, 0, 0.6), shadow=0.0, shadow_blur=8,
               shadow_dy=4, gradient=None, tracking=0, pad=None):
    """Render text -> premultiplied RGBA layer (cached). gradient=(top_rgb, bottom_rgb) fills vertically."""
    f = font(fname, size)
    asc, desc = f.getmetrics()
    tw = text_size(s, fname, size, tracking)[0]
    p = pad if pad is not None else int(max(stroke * 2, shadow_blur * 2.2 if shadow else 0) + 6)
    Wd, Hd = int(math.ceil(tw)) + 2 * p, asc + desc + 2 * p
    mask = Image.new('L', (Wd, Hd), 0)
    d = ImageDraw.Draw(mask)
    if tracking:
        x = p
        for ch in s:
            d.text((x, p), ch, font=f, fill=255)
            x += f.getlength(ch) + tracking
    else:
        d.text((p, p), s, font=f, fill=255)
    m = np.asarray(mask, np.float32) / 255.0
    out = np.zeros((Hd, Wd, 4), np.float32)
    if shadow:
        sm = Image.new('L', (Wd, Hd), 0)
        sd = ImageDraw.Draw(sm)
        if tracking:
            x = p
            for ch in s:
                sd.text((x, p + shadow_dy), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
                x += f.getlength(ch) + tracking
        else:
            sd.text((p, p + shadow_dy), s, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
        sm = sm.filter(ImageFilter.GaussianBlur(shadow_blur))
        sa = np.asarray(sm, np.float32) / 255.0 * shadow
        out[..., 3] = sa  # black shadow (premultiplied rgb = 0)
    if stroke:
        st = Image.new('L', (Wd, Hd), 0)
        sd = ImageDraw.Draw(st)
        if tracking:
            x = p
            for ch in s:
                sd.text((x, p), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
                x += f.getlength(ch) + tracking
        else:
            sd.text((p, p), s, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
        sa = np.asarray(st, np.float32)[..., None] / 255.0 * stroke_color[3]
        out = out * (1 - sa) + np.concatenate([np.array(stroke_color[:3], np.float32) * sa, sa], -1)
    if gradient is not None:
        top, bot = np.array(gradient[0], np.float32), np.array(gradient[1], np.float32)
        yy = np.linspace(0, 1, Hd, dtype=np.float32)[:, None, None]
        yy = np.clip((yy * Hd - p - asc * 0.15) / (asc * 0.95), 0, 1)
        col = top * (1 - yy) + bot * yy
        col = np.broadcast_to(col, (Hd, Wd, 3))
    else:
        col = np.broadcast_to(np.array(color, np.float32), (Hd, Wd, 3))
    a = m[..., None]
    out = out * (1 - a) + np.concatenate([col * a, a], -1)
    out.setflags(write=False)
    return out

GOLD_GRAD = ((1.0, 0.93, 0.66), (0.93, 0.66, 0.20))
WHITE_GRAD = ((1, 1, 1), (0.86, 0.92, 0.88))


# ---- SDF / masks ----------------------------------------------------------------------------------------------------
@lru_cache(256)
def rrect_field(w, h, r, pad):
    """Signed distance (px, negative inside) of a w x h rounded rect, on a grid padded by pad; plus outward normal."""
    W, H = w + 2 * pad, h + 2 * pad
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    px, py = xs + 0.5 - W / 2, ys + 0.5 - H / 2
    hx, hy = w / 2 - r, h / 2 - r
    qx, qy = np.abs(px) - hx, np.abs(py) - hy
    ox, oy = np.maximum(qx, 0), np.maximum(qy, 0)
    d = np.sqrt(ox * ox + oy * oy) + np.minimum(np.maximum(qx, qy), 0) - r
    # normal
    nx = np.where(qx > 0, ox, 0) * np.sign(px)
    ny = np.where(qy > 0, oy, 0) * np.sign(py)
    inner = (qx <= 0) & (qy <= 0)
    nx = np.where(inner & (qx > qy), np.sign(px), nx)
    ny = np.where(inner & (qx <= qy), np.sign(py), ny)
    n = np.sqrt(nx * nx + ny * ny) + 1e-6
    res = (d.astype(np.float32), (nx / n).astype(np.float32), (ny / n).astype(np.float32))
    for a in res: a.setflags(write=False)
    return res

def rrect_mask(w, h, r, pad=0):
    d = rrect_field(w, h, r, pad)[0]
    return np.clip(0.5 - d, 0, 1)


# ---- liquid glass ---------------------------------------------------------------------------------------------------
def glass(frame, cx, cy, w, h, r=None, *, alpha=1.0, tint=(1, 1, 1), tint_a=0.10, blur=22, refract=26, bevel=None,
          vibrancy=1.25, lift=0.05, rim=0.85, shadow=0.32, sheen=0.10, dark=0.0, chroma=0.35, border=None):
    """Liquid-glass panel (Apple-style): frosted blur of what is behind it, lens refraction that bends the background at
    the rim, vibrancy, a tint, a specular rim lit from the top-left and a soft drop shadow. Draws onto frame in place.
    dark>0 darkens the glass (for white text on bright scenes)."""
    if alpha <= 0.003 or w < 4 or h < 4: return
    w, h = int(round(w)), int(round(h))
    if r is None: r = min(w, h) * 0.5
    r = float(min(r, w / 2, h / 2))
    bevel = bevel or min(42.0, min(w, h) * 0.34)
    pad = int(refract + 4)
    H, W = frame.shape[:2]
    x0, y0 = int(round(cx - w / 2)) - pad, int(round(cy - h / 2)) - pad
    gw, gh = w + 2 * pad, h + 2 * pad
    d, nx, ny = rrect_field(w, h, int(round(r)), pad)
    # region (with border clamp)
    bx0, by0 = max(0, x0 - pad), max(0, y0 - pad)
    bx1, by1 = min(W, x0 + gw + pad), min(H, y0 + gh + pad)
    if bx1 <= bx0 or by1 <= by0: return
    region = frame[by0:by1, bx0:bx1]
    # frosted: downsample -> blur -> upsample
    k = 4
    small = cv2.resize(region, (max(1, region.shape[1] // k), max(1, region.shape[0] // k)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), blur / k)
    frost = cv2.resize(small, (region.shape[1], region.shape[0]), interpolation=cv2.INTER_LINEAR)
    # vibrancy + lift + tint
    lum = frost @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    frost = lum[..., None] + (frost - lum[..., None]) * vibrancy
    frost = frost * (1 - dark) + lift
    frost = frost * (1 - tint_a) + np.array(tint, np.float32) * tint_a
    # refraction: sample inward near the rim (magnifies the rim like a thick lens)
    e = np.clip(1 + d / bevel, 0, 1)               # 1 at the edge, 0 deeper than bevel
    inside = d < 0
    disp = refract * e ** 2.2 * inside
    gx, gy = np.meshgrid(np.arange(gw, dtype=np.float32), np.arange(gh, dtype=np.float32))
    ox, oy = x0 - bx0, y0 - by0
    mx = gx + ox - nx * disp
    my = gy + oy - ny * disp
    out = np.empty((gh, gw, 3), np.float32)
    if chroma:
        for c, s in ((0, 1 + chroma * 0.25), (1, 1.0), (2, 1 - chroma * 0.25)):
            mxc = gx + ox - nx * disp * s
            myc = gy + oy - ny * disp * s
            out[..., c] = cv2.remap(frost[..., c], mxc, myc, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    else:
        out = cv2.remap(frost, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # specular rim (light from top-left) + faint opposite rim + top sheen
    L = np.array([-0.55, -0.83], np.float32)
    lam = nx * L[0] + ny * L[1]
    band = np.clip(1 - np.abs(d + 1.6) / 1.9, 0, 1)
    wide = np.clip(1 - np.abs(d + 5.0) / 6.0, 0, 1)
    spec = band * (0.30 + 0.95 * np.clip(lam, 0, 1) ** 1.5 + 0.35 * np.clip(-lam, 0, 1) ** 2) * rim
    spec += wide * 0.18 * np.clip(lam, 0, 1) * rim
    yrel = np.clip((gy - pad) / max(h, 1), 0, 1)
    out += (spec + sheen * (1 - yrel) ** 2 * inside)[..., None]
    if border is not None:
        bb = np.clip(1 - np.abs(d + 1.2) / 1.4, 0, 1)[..., None] * border[3]
        out = out * (1 - bb) + np.array(border[:3], np.float32) * bb
    m = np.clip(0.5 - d, 0, 1)[..., None] * alpha
    # drop shadow
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(W, x0 + gw), min(H, y0 + gh)
    if fx1 <= fx0 or fy1 <= fy0: return
    if shadow:
        drop_shadow(frame, cx, cy, w, h, r, shadow * alpha)
    sub_o = out[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    sub_m = m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - sub_m) + np.clip(sub_o, 0, 1.2) * sub_m


def drop_shadow(frame, cx, cy, w, h, r, strength):
    """Soft drop shadow under a rounded rect: own canvas padded by 3 sigma + offset (no hard edges), blurred at 1/4
    resolution, offset downwards by slicing."""
    if strength <= 0.003: return
    sig = max(4.0, min(w, h) * 0.06)
    off = int(min(18, h * 0.06))
    k = 4
    sw, shh = max(2, int(round(w / k))), max(2, int(round(h / k)))
    sp = int(np.ceil((3 * sig) / k)) + 2
    m = np.clip(0.5 - rrect_field(sw, shh, int(round(min(r, w / 2, h / 2) / k)), sp)[0], 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), sig / k)
    gw_, gh_ = (sw + 2 * sp) * k, (shh + 2 * sp) * k
    m = cv2.resize(m, (gw_, gh_), interpolation=cv2.INTER_LINEAR) * strength
    H, W = frame.shape[:2]
    x0 = int(round(cx - gw_ / 2)); y0 = int(round(cy - gh_ / 2)) + off
    ax0, ay0, ax1, ay1 = max(0, x0), max(0, y0), min(W, x0 + gw_), min(H, y0 + gh_)
    if ax1 <= ax0 or ay1 <= ay0: return
    frame[ay0:ay1, ax0:ax1] *= (1 - m[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0, None])


def fill_rrect(frame, cx, cy, w, h, r, color, alpha=1.0, grad=None):
    """Solid (or vertical-gradient) anti-aliased rounded rect."""
    if alpha <= 0.003: return
    w, h = int(round(w)), int(round(h))
    m = rrect_mask(w, h, int(round(min(r, w / 2, h / 2))), 1)
    hh, ww = m.shape
    if grad is not None:
        yy = np.linspace(0, 1, hh, dtype=np.float32)[:, None, None]
        col = np.array(grad[0], np.float32) * (1 - yy) + np.array(grad[1], np.float32) * yy
        col = np.broadcast_to(col, (hh, ww, 3))
    else:
        col = np.broadcast_to(np.array(color, np.float32), (hh, ww, 3))
    L = np.concatenate([col * m[..., None], m[..., None]], -1)
    blit(frame, L, cx, cy, alpha)


# ---- icons (vector, drawn at 4x and downsampled) --------------------------------------------------------------------
@lru_cache(256)
def icon(name, size, color=(1, 1, 1), stroke=None):
    S = 4
    N = int(size * S)
    img = Image.new('L', (N, N), 0)
    d = ImageDraw.Draw(img)
    lw = int((stroke or max(2.0, size * 0.085)) * S)
    def R(x0, y0, x1, y1, rr=0.0, fill=None, width=lw):
        d.rounded_rectangle([x0 * N, y0 * N, x1 * N, y1 * N], radius=rr * N, fill=fill, outline=None if fill else 255, width=width)
    def E(x0, y0, x1, y1, fill=None, width=lw):
        d.ellipse([x0 * N, y0 * N, x1 * N, y1 * N], fill=fill, outline=None if fill else 255, width=width)
    def Lne(pts, width=lw):
        d.line([(x * N, y * N) for x, y in pts], fill=255, width=width, joint='curve')
        for x, y in (pts[0], pts[-1]):
            d.ellipse([x * N - width / 2, y * N - width / 2, x * N + width / 2, y * N + width / 2], fill=255)
    def P(pts, fill=255):
        d.polygon([(x * N, y * N) for x, y in pts], fill=fill)
    def A(x0, y0, x1, y1, a0, a1, width=lw):
        d.arc([x0 * N, y0 * N, x1 * N, y1 * N], a0, a1, fill=255, width=width)
    if name == 'check':
        Lne([(0.22, 0.52), (0.42, 0.72), (0.80, 0.30)], width=int(lw * 1.5))
    elif name == 'cross':
        Lne([(0.27, 0.27), (0.73, 0.73)], width=int(lw * 1.5)); Lne([(0.73, 0.27), (0.27, 0.73)], width=int(lw * 1.5))
    elif name == 'wallet':
        R(0.10, 0.28, 0.90, 0.84, 0.10)
        Lne([(0.16, 0.28), (0.62, 0.14), (0.70, 0.28)])
        R(0.58, 0.46, 0.92, 0.66, 0.08)
        E(0.66, 0.52, 0.74, 0.60, fill=255)
    elif name == 'pin':
        d.pieslice([0.2 * N, 0.08 * N, 0.8 * N, 0.68 * N], 0, 360, fill=255)
        P([(0.24, 0.48), (0.76, 0.48), (0.5, 0.92)])
        E(0.38, 0.26, 0.62, 0.50, fill=0)
    elif name == 'clock':
        E(0.10, 0.10, 0.90, 0.90)
        Lne([(0.5, 0.5), (0.5, 0.26)]); Lne([(0.5, 0.5), (0.68, 0.60)])
    elif name == 'calendar':
        R(0.12, 0.20, 0.88, 0.88, 0.10)
        d.rectangle([0.12 * N, 0.20 * N, 0.88 * N, 0.38 * N], fill=255)
        Lne([(0.32, 0.10), (0.32, 0.26)]); Lne([(0.68, 0.10), (0.68, 0.26)])
        for i in range(3):
            for j in range(2):
                E(0.25 + i * 0.2, 0.50 + j * 0.18, 0.33 + i * 0.2, 0.58 + j * 0.18, fill=255)
    elif name == 'heart':
        d.pieslice([0.08 * N, 0.16 * N, 0.54 * N, 0.62 * N], 135, 360 + 0, fill=255)
        d.pieslice([0.46 * N, 0.16 * N, 0.92 * N, 0.62 * N], 180, 405, fill=255)
        P([(0.115, 0.48), (0.885, 0.48), (0.5, 0.88)])
        E(0.08, 0.16, 0.54, 0.62, fill=255); E(0.46, 0.16, 0.92, 0.62, fill=255)
    elif name == 'person':
        E(0.34, 0.08, 0.66, 0.40, fill=255)
        d.pieslice([0.14 * N, 0.46 * N, 0.86 * N, 1.18 * N], 180, 360, fill=255)
    elif name == 'woman':
        E(0.34, 0.10, 0.66, 0.42, fill=255)
        A(0.24, 0.02, 0.76, 0.58, 160, 380, width=int(lw * 1.1))      # dupatta
        d.pieslice([0.12 * N, 0.48 * N, 0.88 * N, 1.20 * N], 180, 360, fill=255)
    elif name == 'users':
        for cx0, s in ((0.27, 0.8), (0.73, 0.8), (0.5, 1.0)):
            r0 = 0.13 * s
            E(cx0 - r0, 0.22 - r0 + (0.0 if s == 1 else 0.06), cx0 + r0, 0.22 + r0 + (0.0 if s == 1 else 0.06), fill=255)
            d.pieslice([(cx0 - 0.24 * s) * N, (0.50 + (0 if s == 1 else 0.05)) * N, (cx0 + 0.24 * s) * N,
                        (0.98 + (0 if s == 1 else 0.05)) * N], 180, 360, fill=255)
    elif name == 'store':
        R(0.14, 0.40, 0.86, 0.88, 0.04)
        for i in range(4):
            d.pieslice([(0.10 + i * 0.2) * N, 0.22 * N, (0.30 + i * 0.2) * N, 0.50 * N], 0, 180, fill=255)
        d.rectangle([0.10 * N, 0.14 * N, 0.90 * N, 0.36 * N], fill=255)
        R(0.40, 0.60, 0.60, 0.88, 0.02, fill=255)
    elif name == 'bank':
        P([(0.08, 0.34), (0.5, 0.08), (0.92, 0.34)])
        for i in range(4):
            d.rectangle([(0.18 + i * 0.19) * N, 0.40 * N, (0.26 + i * 0.19) * N, 0.76 * N], fill=255)
        d.rectangle([0.10 * N, 0.80 * N, 0.90 * N, 0.90 * N], fill=255)
    elif name == 'phone':
        R(0.26, 0.06, 0.74, 0.94, 0.10)
        Lne([(0.44, 0.84), (0.56, 0.84)])
    elif name == 'sms':
        R(0.08, 0.14, 0.92, 0.70, 0.16, fill=255)
        P([(0.24, 0.66), (0.44, 0.66), (0.22, 0.88)])
        for i in range(3):
            E(0.28 + i * 0.17, 0.38, 0.38 + i * 0.17, 0.48, fill=0)
    elif name == 'idcard':
        R(0.06, 0.20, 0.94, 0.80, 0.08)
        R(0.14, 0.32, 0.40, 0.66, 0.04, fill=255)
        Lne([(0.50, 0.38), (0.84, 0.38)]); Lne([(0.50, 0.52), (0.84, 0.52)]); Lne([(0.50, 0.66), (0.72, 0.66)])
    elif name == 'fingerprint':
        w8 = max(2, int(lw * 0.62))
        gaps = [75, 115, 60, 125, 85]
        for k in range(5):
            rx, ry = 0.055 + k * 0.078, 0.085 + k * 0.088
            g = gaps[k]
            A(0.5 - rx, 0.50 - ry, 0.5 + rx, 0.50 + ry, g + 34, g + 360, width=w8)
    elif name == 'cash':
        R(0.06, 0.26, 0.94, 0.74, 0.06)
        E(0.38, 0.36, 0.62, 0.64)
        E(0.14, 0.44, 0.22, 0.56, fill=255); E(0.78, 0.44, 0.86, 0.56, fill=255)
    elif name == 'shield':
        P([(0.5, 0.06), (0.88, 0.20), (0.84, 0.56), (0.5, 0.94), (0.16, 0.56), (0.12, 0.20)])
        P([(0.5, 0.17), (0.78, 0.27), (0.75, 0.53), (0.5, 0.82), (0.25, 0.53), (0.22, 0.27)], fill=0)
        Lne([(0.36, 0.50), (0.47, 0.61), (0.66, 0.38)])
    elif name == 'lock':
        R(0.18, 0.44, 0.82, 0.90, 0.10, fill=255)
        A(0.30, 0.14, 0.70, 0.62, 180, 360)
        Lne([(0.30, 0.38), (0.30, 0.46)]); Lne([(0.70, 0.38), (0.70, 0.46)])
        E(0.44, 0.58, 0.56, 0.70, fill=0)
    elif name == 'warning':
        P([(0.5, 0.08), (0.95, 0.88), (0.05, 0.88)])
        P([(0.5, 0.22), (0.82, 0.80), (0.18, 0.80)], fill=0)
        Lne([(0.5, 0.40), (0.5, 0.60)], width=int(lw * 1.2)); E(0.45, 0.66, 0.55, 0.76, fill=255)
    elif name == 'globe':
        E(0.08, 0.08, 0.92, 0.92)
        E(0.30, 0.08, 0.70, 0.92)
        Lne([(0.5, 0.08), (0.5, 0.92)]); Lne([(0.08, 0.5), (0.92, 0.5)])
        A(0.12, -0.10, 0.88, 0.40, 30, 150, width=int(lw * 0.8)); A(0.12, 0.60, 0.88, 1.10, 210, 330, width=int(lw * 0.8))
    elif name == 'sim':
        P([(0.20, 0.06), (0.62, 0.06), (0.80, 0.24), (0.80, 0.94), (0.20, 0.94)])
        P([(0.27, 0.13), (0.59, 0.13), (0.73, 0.27), (0.73, 0.87), (0.27, 0.87)], fill=0)
        R(0.34, 0.44, 0.66, 0.78, 0.04, fill=255)
    elif name == 'arrow':
        Lne([(0.12, 0.5), (0.80, 0.5)], width=int(lw * 1.3)); Lne([(0.56, 0.26), (0.82, 0.5), (0.56, 0.74)], width=int(lw * 1.3))
    elif name == 'rise':
        Lne([(0.10, 0.80), (0.38, 0.52), (0.56, 0.66), (0.88, 0.28)], width=int(lw * 1.2))
        Lne([(0.66, 0.26), (0.89, 0.26), (0.89, 0.48)], width=int(lw * 1.2))
    elif name == 'sparkle':
        P([(0.5, 0.04), (0.6, 0.4), (0.96, 0.5), (0.6, 0.6), (0.5, 0.96), (0.4, 0.6), (0.04, 0.5), (0.4, 0.4)])
    elif name == 'question':
        A(0.26, 0.10, 0.74, 0.54, 190, 400, width=int(lw * 1.4))
        Lne([(0.62, 0.48), (0.5, 0.58), (0.5, 0.68)], width=int(lw * 1.4))
        E(0.44, 0.78, 0.56, 0.90, fill=255)
    elif name == 'hand_coin':
        E(0.36, 0.06, 0.70, 0.40)
        Lne([(0.08, 0.66), (0.30, 0.60), (0.52, 0.66), (0.70, 0.62)])
        Lne([(0.08, 0.86), (0.40, 0.92), (0.90, 0.70)])
    else:
        raise KeyError(name)
    a = np.asarray(img.resize((int(size), int(size)), Image.LANCZOS), np.float32) / 255.0
    L = np.zeros((int(size), int(size), 4), np.float32)
    L[..., 3] = a
    L[..., :3] = np.array(color, np.float32) * a[..., None]
    L.setflags(write=False)
    return L


def disc(size, color, ring=None, ring_w=3):
    """Filled AA circle layer (optionally with a lighter ring)."""
    N = int(size)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    r = np.sqrt((xx + 0.5 - N / 2) ** 2 + (yy + 0.5 - N / 2) ** 2)
    m = np.clip(N / 2 - r, 0, 1)
    col = np.broadcast_to(np.array(color, np.float32), (N, N, 3)).copy()
    # soft vertical gradient for depth
    g = np.linspace(1.12, 0.86, N, dtype=np.float32)[:, None, None]
    col = np.clip(col * g, 0, 1)
    if ring is not None:
        rm = np.clip(1 - np.abs(r - (N / 2 - ring_w / 2 - 0.5)) / (ring_w / 2), 0, 1)
        col = col * (1 - rm[..., None]) + np.array(ring, np.float32) * rm[..., None]
    return np.concatenate([col * m[..., None], m[..., None]], -1)


def icon_badge(name, size, bg=GREEN, fg=WHITE, ring=(1, 1, 1)):
    """Icon in a filled circle."""
    L = disc(size, bg, ring=(*[min(1, c * 0.5 + 0.5) for c in bg],) if ring else None, ring_w=max(2, size * 0.035)).copy()
    ic = icon(name, int(size * 0.58), fg)
    h = ic.shape[0]
    o = (L.shape[0] - h) // 2
    a = ic[..., 3:4]
    L[o:o + h, o:o + h] = L[o:o + h, o:o + h] * (1 - a) + ic
    return L


# ---- logo ---------------------------------------------------------------------------------------------------------------
@lru_cache(8)
def logo_layer(width):
    """Official BISP banner (bisp.gov.pk header logo), scaled to width."""
    im = Image.open(os.path.join(WS, 'brand', 'dl', 'bisplogonew.png')).convert('RGBA')
    h = int(round(im.height * width / im.width))
    im = im.resize((int(width), h), Image.LANCZOS)
    L = to_layer(im)
    L.setflags(write=False)
    return L


# ---- finishing -------------------------------------------------------------------------------------------------------
@lru_cache(2)
def vignette_map(W, H, strength=0.22):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r = np.sqrt(nx * nx * 1.0 + ny * ny * 0.85)
    v = 1 - strength * np.clip((r - 0.55) / 0.9, 0, 1) ** 1.6
    return v[..., None].astype(np.float32)

def grain(frame, t, amount=0.022, seed=0):
    rng = np.random.default_rng(int(t * 1000) + seed)
    H, W = frame.shape[:2]
    n = rng.standard_normal((H // 2, W // 2), dtype=np.float32)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)
    lum = frame @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    w = (0.4 + 0.6 * (1 - np.abs(lum - 0.45) * 1.6).clip(0, 1))[..., None]
    frame += n[..., None] * amount * w
