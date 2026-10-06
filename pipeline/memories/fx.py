"""Cinematic effects for the Yaadein compositor (all linear-light, 1080x1920).

anim clips with optical-flow 30->60 fps interpolation, polaroid sprites, glass shatter, lightning,
explosion fireball, light leaks, petals / embers / dust particles, whip and zoom-through blurs.
"""
import functools
import glob
import math
import os

import cv2
import numpy as np

import anim as A
import comp as C

PLATES = C.ROOT + '/plates3'


# ---------------------------------------------------------------- plates & clips
def plate_path(name, layer='full'):
    for p in (f'{PLATES}/{name}_{layer}.png', f'{PLATES}/{name}_{layer}_preview.png'):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'{name}_{layer}')


def plate(name, layer='full'):
    return C.load(plate_path(name, layer))


def has_layer(name, layer):
    try:
        plate_path(name, layer)
        return True
    except FileNotFoundError:
        return False


class Clip:
    """Rendered animation (every 2nd frame at 60 fps); frames between are synthesised from optical flow."""

    def __init__(self, name):
        d = f'{PLATES}/{name}'
        if not os.path.isdir(d) or not glob.glob(d + '/*.png'):
            d = d + '_preview'
        self.files = sorted(glob.glob(d + '/*.png'))
        self.nums = [int(os.path.basename(f)[:-4]) for f in self.files]
        self.cache = {}
        self.flows = {}

    def _get(self, i):
        if i not in self.cache:
            if len(self.cache) > 6:
                self.cache.pop(next(iter(self.cache)))
            self.cache[i] = C.load.__wrapped__(self.files[i]) if hasattr(C.load, '__wrapped__') else C.load(self.files[i])
        return self.cache[i]

    def _flow(self, i):
        if i not in self.flows:
            if len(self.flows) > 4:
                self.flows.pop(next(iter(self.flows)))
            a = cv2.cvtColor((np.clip(C.to_srgb(self._get(i)[..., :3]), 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            b = cv2.cvtColor((np.clip(C.to_srgb(self._get(i + 1)[..., :3]), 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
            self.flows[i] = (dis.calc(a, b, None), dis.calc(b, a, None))
        return self.flows[i]

    def frame(self, f):
        """f = 60 fps frame number (1-based, float ok)."""
        if not self.files:
            return None
        f = min(max(f, self.nums[0]), self.nums[-1])
        j = int(np.searchsorted(self.nums, f, side='right') - 1)
        j = min(j, len(self.nums) - 1)
        if j == len(self.nums) - 1 or abs(f - self.nums[j]) < 1e-3:
            return self._get(j)
        u = (f - self.nums[j]) / (self.nums[j + 1] - self.nums[j])
        a, b = self._get(j), self._get(j + 1)
        fab, fba = self._flow(j)
        h, w = a.shape[:2]
        gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        wa = cv2.remap(a, gx - fba[..., 0] * u, gy - fba[..., 1] * u, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        wb = cv2.remap(b, gx - fab[..., 0] * (1 - u), gy - fab[..., 1] * (1 - u), cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REPLICATE)
        return wa * (1 - u) + wb * u

    @property
    def last(self):
        return self.nums[-1] if self.nums else 1


# ---------------------------------------------------------------- polaroids
@functools.lru_cache(maxsize=16)
def polaroid(name, layer='full', crop=(0.0, 0.18, 1.0, 0.72), w=420, aged=0.0):
    """White-bordered instant photo sprite (premultiplied linear RGBA) from a plate crop."""
    im = plate(name, layer)[..., :3]
    h0, w0 = im.shape[:2]
    x0, y0, x1, y1 = crop
    sub = im[int(y0 * h0):int(y1 * h0), int(x0 * w0):int(x1 * w0)]
    pw = w - 40
    ph = int(pw * 1.0)
    sub = cv2.resize(sub, (pw, ph), interpolation=cv2.INTER_AREA)
    if aged:
        lum = sub.mean(2, keepdims=True)
        sub = sub * (1 - aged * 0.4) + lum * np.float32([1.0, 0.85, 0.6]) * aged * 0.4
    H = ph + 20 + 90
    card = np.ones((H, w, 3), np.float32) * C.to_lin(np.float32([0.93, 0.91, 0.87]))
    card[20:20 + ph, 20:20 + pw] = sub
    a = np.ones((H, w, 1), np.float32)
    return np.ascontiguousarray(np.dstack([card, a]))


def polaroid_key(name, **kw):
    key = 'pol_' + name + '_' + '_'.join(f'{k}{v}' for k, v in sorted(kw.items()))
    if key not in C._SPRITES:
        C.register(key, polaroid(name, **{k: v for k, v in kw.items()}))
    return key


# ---------------------------------------------------------------- shatter
class Shatter:
    """Breaks an image (full-frame linear RGB) into triangular glass shards that fly toward the camera."""

    def __init__(self, img, n=70, seed=3, center=(540, 900), depth=3.0, F=2060.0):
        rng = np.random.default_rng(seed)
        h, w = img.shape[:2]
        pts = np.vstack([rng.uniform((0, 0), (w, h), (n, 2)),
                         [[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1], [w / 2, 0], [w / 2, h - 1], [0, h / 2], [w - 1, h / 2]]])
        # bias points toward the impact centre (smaller shards there)
        pts = np.vstack([pts, np.asarray(center) + rng.normal(0, 90, (int(n * 0.6), 2))])
        pts[:, 0] = np.clip(pts[:, 0], 0, w - 1)
        pts[:, 1] = np.clip(pts[:, 1], 0, h - 1)
        sub = cv2.Subdiv2D((0, 0, w, h))
        for p in pts:
            sub.insert((float(p[0]), float(p[1])))
        tris = sub.getTriangleList().reshape(-1, 3, 2)
        self.shards = []
        for t in tris:
            if (t < -1).any() or (t[:, 0] > w).any() or (t[:, 1] > h).any():
                continue
            x0, y0 = np.floor(t.min(0)).astype(int)
            x1, y1 = np.ceil(t.max(0)).astype(int) + 1
            if x1 - x0 < 3 or y1 - y0 < 3:
                continue
            m = np.zeros((y1 - y0, x1 - x0), np.float32)
            cv2.fillConvexPoly(m, np.int32((t - [x0, y0]) * 16), 1.0, cv2.LINE_AA, shift=4)
            spr = np.dstack([img[y0:y1, x0:x1] * m[..., None], m])
            # bright glass edge
            edge = np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8)), 0, 1)
            spr[..., :3] += edge[..., None] * 0.35
            c = t.mean(0)
            d = (c - np.asarray(center)) / 540.0
            dist = float(np.hypot(*d))
            self.shards.append(dict(spr=spr, c=c, size=(x1 - x0, y1 - y0), off=((x0 + x1) / 2 - c[0], (y0 + y1) / 2 - c[1]),
                                    v=np.array([d[0] * 2.2, -d[1] * 2.2, -rng.uniform(1.5, 3.8)]) * (0.6 + 0.6 / (0.3 + dist)),
                                    w=rng.normal(0, 260, 3), delay=dist * 0.05))
        self.depth, self.F = depth, F

    def draw(self, cv, cam, u):
        """u = seconds since impact."""
        D = self.depth
        for s in self.shards:
            uu = max(0.0, u - s['delay'])
            k = D / self.F
            cx = (s['c'][0] + s['off'][0] - C.W / 2) * k
            cy = -(s['c'][1] + s['off'][1] - C.H / 2) * k
            p = np.array([cx, cy, D]) + s['v'] * uu + np.array([0, -1.6, 0]) * uu * uu
            if p[2] - cam.z < 0.25:
                continue
            rot = tuple(s['w'] * uu)
            C.draw_img3d(cv, s['spr'], cam, tuple(p), (s['size'][0] * k, s['size'][1] * k), rot, opacity=1.0)
        return cv


# ---------------------------------------------------------------- light & weather
def lightning(cv, t, t0, strength=2.5, color=(0.65, 0.75, 1.0)):
    """Double-strike flash with fast decay."""
    u = t - t0
    if u < 0 or u > 0.6:
        return cv
    k = math.exp(-u * 14) + 0.7 * math.exp(-max(0, u - 0.12) * 18) * (u > 0.12)
    cv[..., :3] = cv[..., :3] * (1 + k * strength * 0.6) + np.float32(color) * k * strength * 0.08
    return cv


@functools.lru_cache(maxsize=1)
def _yx():
    yy, xx = np.mgrid[0:C.H // 4, 0:C.W // 4].astype(np.float32)
    return yy * 4, xx * 4


def light_leak(cv, t, strength=0.5, colors=((1.0, 0.25, 0.05), (1.0, 0.55, 0.15)), seed=0, speed=0.35):
    yy, xx = _yx()
    acc = np.zeros(yy.shape + (3,), np.float32)
    rng = np.random.default_rng(seed)
    for i, col in enumerate(colors):
        ph = rng.uniform(0, 6.28, 3)
        cx = C.W * (0.5 + 0.65 * math.sin(t * speed + ph[0]))
        cy = C.H * (0.5 + 0.55 * math.sin(t * speed * 0.7 + ph[1]))
        r = C.W * (0.55 + 0.2 * math.sin(t * 0.5 + ph[2]))
        acc += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))[..., None] * np.float32(col)
    acc = cv2.resize(acc, (C.W, C.H), interpolation=cv2.INTER_LINEAR)
    cv[..., :3] += acc * strength
    return cv


def fireball(cv, u, center=(540, 960), scale=1.0):
    """Explosion: white core -> orange fire with turbulent edge -> smoke, plus shock ring. u seconds."""
    if u < 0 or u > 1.4:
        return cv
    yy, xx = _yx()
    r = (120 + 900 * A.EXPO_OUT(min(1.0, u / 0.9))) * scale
    d = np.hypot(xx - center[0], yy - center[1])
    ang = np.arctan2(yy - center[1], xx - center[0])
    turb = 1 + 0.18 * np.sin(ang * 7 + u * 9) + 0.12 * np.sin(ang * 13 - u * 14) + 0.08 * np.sin(ang * 23 + u * 5)
    core = np.clip(1 - d / (r * 0.45 * turb), 0, 1) ** 1.5
    fire = np.clip(1 - d / (r * turb), 0, 1) ** 0.8
    fade = math.exp(-u * 2.2)
    heat = np.clip(1 - u / 1.1, 0, 1)
    col = (fire[..., None] * np.float32([1.0, 0.28, 0.04]) * 1.3 * fade
           + core[..., None] * np.float32([1.0, 0.7, 0.4]) * 1.8 * heat * heat)
    ring = np.exp(-((d - r * 1.25) / (18 + 60 * u)) ** 2) * math.exp(-u * 4) * 1.4
    col += ring[..., None] * np.float32([1.0, 0.6, 0.3])
    col = cv2.resize(col.astype(np.float32), (C.W, C.H), interpolation=cv2.INTER_LINEAR)
    flash = math.exp(-u * 18) * 1.2
    cv[..., :3] = cv[..., :3] + col + flash
    return cv


def drift_particles(n, seed, box, vel, life=None):
    """Deterministic particle cloud: returns f(t) -> (N,3) positions."""
    rng = np.random.default_rng(seed)
    lo, hi = np.asarray(box[0], np.float64), np.asarray(box[1], np.float64)
    P0 = rng.uniform(lo, hi, (n, 3))
    V = np.asarray(vel, np.float64) * rng.uniform(0.6, 1.4, (n, 1))
    ph = rng.uniform(0, 6.28, (n, 3))
    span = hi - lo

    def at(t):
        P = P0 + V * t + 0.08 * np.sin(t * 0.9 + ph) * span * 0.05
        return lo + np.mod(P - lo, span)
    return at


def whip(img, amount, angle=0.0):
    """Directional motion smear (for whip pans). amount in px."""
    if amount < 1:
        return img
    k = int(amount) | 1
    ker = np.zeros((k, k), np.float32)
    ker[k // 2, :] = 1.0 / k
    M = cv2.getRotationMatrix2D((k / 2 - 0.5, k / 2 - 0.5), angle, 1)
    ker = cv2.warpAffine(ker, M, (k, k))
    ker /= ker.sum()
    small = cv2.resize(img, (C.W // 2, C.H // 2), interpolation=cv2.INTER_AREA)
    small = cv2.filter2D(small, -1, cv2.resize(ker, (max(1, k // 2) | 1, max(1, k // 2) | 1)), borderType=cv2.BORDER_REFLECT)
    return cv2.resize(small, (C.W, C.H), interpolation=cv2.INTER_LINEAR)


def radial_blur(img, amount, center=(540, 960), n=8):
    """Zoom-through blur: average of scaled copies about centre."""
    if amount < 0.004:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        s = 1 + amount * i / (n - 1)
        M = np.float32([[s, 0, (1 - s) * center[0]], [0, s, (1 - s) * center[1]]])
        acc += cv2.warpAffine(img, M, (C.W, C.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n


def fit_frame(img):
    """Resize a (non-canvas-sized) linear image to fill the canvas."""
    if img.shape[0] == C.H and img.shape[1] == C.W:
        return img[..., :3]
    s = max(C.W / img.shape[1], C.H / img.shape[0])
    r = cv2.resize(img, (int(img.shape[1] * s + 0.5), int(img.shape[0] * s + 0.5)), interpolation=cv2.INTER_LINEAR)
    y0 = (r.shape[0] - C.H) // 2
    x0 = (r.shape[1] - C.W) // 2
    return np.ascontiguousarray(r[y0:y0 + C.H, x0:x0 + C.W, :3])
