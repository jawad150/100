"""sprites3d.py - runtime loader for the pre-rendered 3D sprite sequences in workspace3/assets3d/.

Works for ANY asset folder that follows the shared 3D asset spec (assets3d_icons.py and the other
Blender renderer write the same layout):

    workspace3/assets3d/<name>/<variant>/0000.png ...  RGBA 8-bit PNG, straight alpha, sRGB
    workspace3/assets3d/<name>/<variant>/meta.json     {name, variant, mode, frames, fps_hint, yaw_range,
                                                        size, anchor, loop, notes, ...}

Every image returned is an (H, W, 4) float32 array of PREMULTIPLIED LINEAR-light RGBA, the
compositor's pixel convention (core.hexlin space). Frames are decoded lazily and kept in a
process-wide byte-budgeted LRU cache (env FOSTER_S3_CACHE_MB, default 768 MB per process; render.py
workers default to 448 MB).

Quick reference
---------------
    from sprites3d import Asset3D, get, list_assets

    heart = get('heart', 'night')          # cached Asset3D instance (== Asset3D('heart', 'night'))
    heart.mode, heart.n, heart.size        # 'yaw', 49, (720, 720)
    heart.anchor                           # (x, y) visual centre in px  -> place this point on the canvas
    heart.pivot, heart.bbox, heart.ground_y  # projected rotation axis, union alpha bbox, lowest opaque row
    img = heart.frame(24)                  # one rendered frame (read-only cached array, do not modify)
    img = heart.at_yaw(-12.5)              # yaw in degrees; blends the two neighbouring frames
    img = heart.at_yaw(-12.5, interp='flow')   # optical-flow in-between: no cross-fade doubling of rims
                                               # (use for slow hero rotations; ~0.1 s/call at 720 px)
    img = heart.float_yaw(t, amp=14, period=4.5, phase=0.3)   # gentle floating rotation at time t (s)
    img = heart.at_time(t)                 # see 'at_time' below

    coin = Asset3D('coin_gbp', 'night', mode='spin')   # resolves folder 'night_spin' (or variant='night_spin')
    img = coin.at_time(t, fps=30)          # looping 360-degree flip, sub-frame blended (motion-blur friendly)
    img = coin.at_yaw(200)                 # spin mode: any angle, wraps at 360

    orbs = get('orbs', 'day')              # mode 'static': one object per frame
    img = orbs.frame(0); img = orbs.by_label('torus_glass')

    small = Asset3D('heart', 'night', scale=0.5)   # pre-downscaled (INTER_AREA in linear premultiplied);
                                                    # anchor/pivot/bbox/size are scaled to match

Modes
-----
    'yaw'    frame i shows yaw = a + (b - a) * i / (n - 1), yaw_range [a, b] (spec: -40..+40, 49 frames).
             Positive yaw turns the object's front towards screen-right (its left side comes into view).
             at_yaw clamps to the range. at_time(t) plays an eased ping-pong across the whole sweep,
             one sweep every (n - 1) / fps seconds (fps defaults to meta fps_hint).
    'spin'   frame i = 360 * i / n degrees; at_yaw wraps; at_time loops (or clamps if loop=False).
    'anim'   a specific animation: at_time plays it at fps (loop per meta / argument), frame-blended.
    'static' independent frames (e.g. one object per frame); at_time returns frame 0; use frame(i).

In-between frames (at_yaw / at_time / float_yaw / blend take interp=...)
---------------------------------------------------------------------
    'blend'   (default) cross-fade of the two neighbouring frames, ~3-7 ms at 720 px. Fine for fast
              moves and under motion-blur sub-sampling; at mid-step a glossy rim can show faintly doubled.
    'flow'    DIS optical flow between the neighbours (computed at half res, cached per pair, ~0.3 s the
              first time) and a symmetric warp of both, ~50 ms/call: in-betweens match a true render
              (p99 error 4.5x lower than 'blend'). Use for slow hero rotations seen large.
    'nearest' snap to the closest rendered frame.
    Set the process default with env FOSTER_SPRITE_INTERP.

Points of interest: a.features {key: (x, y)} (scaled px, from meta 'features'), a.feature(key, x=None)
(interpolated per frame when meta has 'features_per_frame'), a.feature_at_time(key, t).

Other helpers: a.blend(x) (fractional frame index), a.yaw_to_index(deg), a.index_to_yaw(i),
cache_stats(), clear_cache(), list_assets(), decode_png(path), to_srgb8(img), over(dst, spr, x, y, anchor).
Arrays returned by frame() are shared cache entries (read-only): copy before modifying in place.

Robustness: if a variant folder is missing the loader falls back to another variant of the same
asset (a.fallback is True and a.variant tells which one it used); if meta.json is missing (render in
progress) it infers frames/size from the PNGs; missing frame files resolve to the nearest rendered one.

Self-test: python3 sprites3d.py selftest  ->  workspace3/out/selftest/sprites3d_*.png
"""
import os
import sys
import json
import math
import threading
from collections import OrderedDict
from functools import lru_cache

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_WS = os.environ.get('FOSTER_WS', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace3')))


def _ws():
    ws = os.environ.get('FOSTER_WS')
    if ws:
        return ws
    try:  # core.WS is the contract; fall back silently if core is absent or mid-edit
        sys.path.insert(0, HERE)
        import core  # noqa: F401
        return getattr(core, 'WS', _DEFAULT_WS)
    except Exception:
        return _DEFAULT_WS
    finally:
        if sys.path and sys.path[0] == HERE:
            sys.path.pop(0)


def assets_root():
    return os.path.join(_ws(), 'assets3d')


# ----------------------------------------------------------------------------- decoding + LRU cache

_LUT = None


def _lut():
    global _LUT
    if _LUT is None:
        c = np.arange(256, dtype=np.float64) / 255.0
        _LUT = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)
    return _LUT


def decode_png(path):
    """PNG (straight alpha, sRGB) -> (H, W, 4) float32 premultiplied linear RGBA."""
    import cv2
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im is None:
        raise FileNotFoundError(path)
    if im.dtype != np.uint8:
        im = (im.astype(np.float32) / (65535.0 if im.dtype == np.uint16 else 1.0) * 255 + 0.5).clip(0, 255).astype(np.uint8)
    if im.ndim == 2:
        im = np.dstack([im, im, im])
    if im.shape[2] == 3:
        im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
    lut = _lut()
    out = np.empty(im.shape[:2] + (4,), np.float32)
    a = im[:, :, 3].astype(np.float32) * (1.0 / 255.0)
    out[:, :, 0] = lut[im[:, :, 2]] * a
    out[:, :, 1] = lut[im[:, :, 1]] * a
    out[:, :, 2] = lut[im[:, :, 0]] * a
    out[:, :, 3] = a
    return out


class _LRU:
    """Byte-budgeted LRU for decoded frames (thread-safe)."""

    def __init__(self, budget_mb):
        self.budget = int(budget_mb * 1024 * 1024)
        self.d = OrderedDict()
        self.bytes = 0
        self.lock = threading.Lock()
        self.hits = self.misses = 0

    def get(self, key, make):
        with self.lock:
            v = self.d.get(key)
            if v is not None:
                self.d.move_to_end(key)
                self.hits += 1
                return v
        v = make()
        v.flags.writeable = False
        with self.lock:
            self.misses += 1
            if key not in self.d:
                self.d[key] = v
                self.bytes += v.nbytes
            while self.bytes > self.budget and len(self.d) > 1:
                _, old = self.d.popitem(last=False)
                self.bytes -= old.nbytes
        return v

    def clear(self):
        with self.lock:
            self.d.clear()
            self.bytes = 0

    def stats(self):
        return dict(items=len(self.d), mb=round(self.bytes / 1048576, 1), hits=self.hits, misses=self.misses)


# own env name: FOSTER_SPRITE_CACHE_MB is also core.py's mip/blur cache budget (default 256), so setting it
# changed both. FOSTER_S3_CACHE_MB wins; the shared name is still honoured when it is the only one set.
CACHE = _LRU(float(os.environ.get('FOSTER_S3_CACHE_MB', os.environ.get('FOSTER_SPRITE_CACHE_MB', '768'))))
DEFAULT_INTERP = os.environ.get('FOSTER_SPRITE_INTERP', 'blend')


@lru_cache(maxsize=8)
def _grid(w, h):
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    gx.flags.writeable = False
    gy.flags.writeable = False
    return gx, gy


def cache_stats():
    return CACHE.stats()


def clear_cache():
    CACHE.clear()


# ----------------------------------------------------------------------------- asset

def list_assets(root=None):
    """{name: [variant folders...]} for every asset folder that has PNG frames."""
    root = root or assets_root()
    out = {}
    if not os.path.isdir(root):
        return out
    for n in sorted(os.listdir(root)):
        p = os.path.join(root, n)
        if not os.path.isdir(p):
            continue
        vs = [v for v in sorted(os.listdir(p))
              if os.path.isdir(os.path.join(p, v)) and any(f.endswith('.png') for f in os.listdir(os.path.join(p, v)))]
        if vs:
            out[n] = vs
    return out


class Asset3D:
    """A rendered 3D sprite sequence. See the module docstring for the API."""

    def __init__(self, name, variant='night', mode=None, scale=1.0, root=None, fallback=True):
        self.root = root or assets_root()
        self.name = name
        self.scale = float(scale)
        self.requested = (variant, mode)
        folder = self._resolve(name, variant, mode, fallback)
        self.folder = folder
        self.dir = os.path.join(self.root, name, folder)
        self.variant = folder
        self.fallback = folder not in (variant, f'{variant}_{mode}' if mode else variant)
        files = sorted(f for f in os.listdir(self.dir) if f.endswith('.png') and f[:-4].isdigit())
        self._files = {int(f[:-4]): os.path.join(self.dir, f) for f in files}
        meta_p = os.path.join(self.dir, 'meta.json')
        meta = {}
        if os.path.exists(meta_p):
            with open(meta_p) as fh:
                meta = json.load(fh)
        if not meta:
            meta = self._infer_meta()
        self.meta = meta
        self.mode = meta.get('mode', 'static')
        self.n = int(meta.get('frames', len(self._files)))
        self.fps = float(meta.get('fps_hint', 30))
        self.loop = bool(meta.get('loop', self.mode in ('spin', 'anim')))
        self.yaw_range = tuple(meta.get('yaw_range', (-40.0, 40.0)))
        w, h = meta.get('size', [0, 0])
        if not w and self._files:
            import cv2
            im = cv2.imread(next(iter(self._files.values())), cv2.IMREAD_UNCHANGED)
            h, w = im.shape[:2]
        self.src_size = (int(w), int(h))
        k = self.scale
        self.size = (max(1, int(round(w * k))), max(1, int(round(h * k))))
        anc = meta.get('anchor', [w / 2, h / 2])
        self.anchor = (anc[0] * k, anc[1] * k)
        piv = meta.get('pivot', anc)
        self.pivot = (piv[0] * k, piv[1] * k)
        bb = meta.get('bbox', [0, 0, w, h])
        self.bbox = tuple(v * k for v in bb)
        self.ground_y = meta.get('ground_y', bb[3]) * k
        self.labels = list(meta.get('labels', []))
        self.features = {key: (p[0] * k, p[1] * k) for key, p in (meta.get('features') or {}).items()}
        self._fpf = meta.get('features_per_frame')
        self._avail = np.array(sorted(self._files), dtype=np.int64)
        if len(self._avail) == 0:
            raise FileNotFoundError(f'no frames in {self.dir}')

    # -- resolution ------------------------------------------------------------------------------
    def _resolve(self, name, variant, mode, fallback):
        base = os.path.join(self.root, name)
        if not os.path.isdir(base):
            raise FileNotFoundError(f'3D asset {name!r} not found under {self.root}')
        have = [v for v in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, v))]
        cands = []
        if mode:
            cands += [f'{variant}_{mode}', variant] if variant else [mode]
        cands.append(variant)
        for c in cands:
            if c in have and self._has_frames(os.path.join(base, c)):
                if mode and c == variant:
                    m = self._peek_mode(os.path.join(base, c))
                    if m and m != mode:
                        continue
                return c
        if not fallback:
            raise FileNotFoundError(f'{name}/{variant} (mode {mode}) not rendered; have {have}')
        # fallback: same mode in another variant, then anything
        for c in have:
            p = os.path.join(base, c)
            if self._has_frames(p) and (not mode or self._peek_mode(p) == mode):
                return c
        for c in have:
            if self._has_frames(os.path.join(base, c)):
                return c
        raise FileNotFoundError(f'{name}: no rendered variants')

    @staticmethod
    def _has_frames(p):
        return os.path.isdir(p) and any(f.endswith('.png') for f in os.listdir(p))

    @staticmethod
    def _peek_mode(p):
        try:
            with open(os.path.join(p, 'meta.json')) as fh:
                return json.load(fh).get('mode')
        except Exception:
            return None

    def _infer_meta(self):
        n = (max(self._files) + 1) if self._files else 0
        mode = 'yaw' if n in (25, 49) else ('spin' if n == 72 else 'static')
        return {'name': self.name, 'variant': self.folder, 'mode': mode, 'frames': n, 'fps_hint': 30,
                'yaw_range': [-40, 40], 'loop': mode == 'spin', 'notes': 'meta inferred (meta.json missing)'}

    # -- frames ----------------------------------------------------------------------------------
    def _path(self, i):
        p = self._files.get(i)
        if p is None:  # nearest rendered frame
            j = self._avail[np.argmin(np.abs(self._avail - i))]
            p = self._files[int(j)]
        return p

    def frame(self, i):
        """Rendered frame i (clamped to [0, n-1]) as a read-only cached float32 premultiplied linear RGBA."""
        i = int(min(max(int(i), 0), self.n - 1))
        p = self._path(i)
        k = self.scale
        if k == 1.0:
            return CACHE.get((p, 1.0), lambda: decode_png(p))

        def make():
            import cv2
            full = CACHE.get((p, 1.0), lambda: decode_png(p)) if k > 0.5 else decode_png(p)
            return cv2.resize(full, self.size, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
        return CACHE.get((p, k), make)

    def _flows(self, i0, i1):
        """Cached optical flows between frames i0 and i1 (computed at half resolution with DIS)."""
        def make():
            import cv2
            a, b = self.frame(i0), self.frame(i1)
            h, w = a.shape[:2]
            hw, hh = max(8, w // 2), max(8, h // 2)

            def guide(img):
                g = img[:, :, :3].mean(2) + (1.0 - img[:, :, 3]) * 0.18
                g = np.clip(g, 0, 1) ** (1 / 2.2)
                return cv2.resize((g * 255).astype(np.uint8), (hw, hh), interpolation=cv2.INTER_AREA)
            dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
            ga, gb = guide(a), guide(b)
            f01 = cv2.resize(dis.calc(ga, gb, None), (w, h), interpolation=cv2.INTER_LINEAR) * np.float32(w / hw)
            f10 = cv2.resize(dis.calc(gb, ga, None), (w, h), interpolation=cv2.INTER_LINEAR) * np.float32(w / hw)
            return np.stack([f01, f10])
        return CACHE.get((self.dir, i0, i1, self.scale, 'flow'), make)

    def _flow_interp(self, i0, i1, f):
        import cv2
        a, b = self.frame(i0), self.frame(i1)
        fl = self._flows(i0, i1)
        h, w = a.shape[:2]
        gx, gy = _grid(w, h)
        m0 = cv2.convertMaps(gx - f * fl[0, :, :, 0], gy - f * fl[0, :, :, 1], cv2.CV_16SC2)
        m1 = cv2.convertMaps(gx - (1 - f) * fl[1, :, :, 0], gy - (1 - f) * fl[1, :, :, 1], cv2.CV_16SC2)
        wa = cv2.remap(a, m0[0], m0[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        wb = cv2.remap(b, m1[0], m1[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        return wa * np.float32(1 - f) + wb * np.float32(f)

    def blend(self, x, wrap=False, interp=None):
        """Frame at fractional index x from its two neighbours (wraps if `wrap`).

        interp 'blend' (default; cross-fade, ~3 ms), 'flow' (optical-flow warp of both neighbours:
        no cross-fade doubling of rims/silhouettes, ~60-120 ms at 720 px, flows cached per pair) or
        'nearest'. The default comes from env FOSTER_SPRITE_INTERP."""
        interp = interp or DEFAULT_INTERP
        n = self.n
        if wrap:
            x = x % n
            i0 = int(math.floor(x))
            i1 = (i0 + 1) % n
        else:
            x = min(max(x, 0.0), n - 1.0)
            i0 = int(math.floor(x))
            i1 = min(i0 + 1, n - 1)
        f = x - math.floor(x)
        if interp == 'nearest':
            return self.frame(i1 if f >= 0.5 else i0)
        a = self.frame(i0)
        if f < 1e-3 or i1 == i0:
            return a
        if f > 1 - 1e-3:
            return self.frame(i1)
        if interp == 'flow':
            return self._flow_interp(i0, i1, f)
        b = self.frame(i1)
        return a + (b - a) * np.float32(f)

    def yaw_to_index(self, deg):
        if self.mode == 'spin':
            return (deg % 360.0) / 360.0 * self.n
        a, b = self.yaw_range
        return (min(max(deg, min(a, b)), max(a, b)) - a) / (b - a) * (self.n - 1)

    def index_to_yaw(self, i):
        if self.mode == 'spin':
            return 360.0 * i / self.n
        a, b = self.yaw_range
        return a + (b - a) * i / max(self.n - 1, 1)

    def at_yaw(self, deg, interp=None):
        """Yaw/spin angle in degrees -> interpolated frame (yaw: clamped to yaw_range; spin: wraps)."""
        if self.mode == 'spin':
            return self.blend(self.yaw_to_index(deg), wrap=True, interp=interp)
        if self.mode != 'yaw':
            return self.frame(0)
        return self.blend(self.yaw_to_index(deg), interp=interp)

    def float_yaw(self, t, amp=12.0, period=4.0, phase=0.0, center=0.0, interp=None):
        """Gentle floating rotation: yaw = center + amp * sin(2 pi (t / period + phase))."""
        return self.at_yaw(center + amp * math.sin(2 * math.pi * (t / period + phase)), interp=interp)

    def at_time(self, t, fps=None, loop=None, interp=None):
        """Time-based playback (seconds). spin/anim: frame = t * fps, interpolated, looping per `loop`
        (default: meta loop). yaw: eased ping-pong over the whole sweep. static: frame 0."""
        fps = float(fps or self.fps)
        loop = self.loop if loop is None else loop
        if self.mode in ('spin', 'anim'):
            x = t * fps
            if loop:
                return self.blend(x, wrap=True, interp=interp)
            return self.blend(min(max(x, 0.0), self.n - 1.0), interp=interp)
        if self.mode == 'yaw':
            span = max(self.n - 1, 1)
            ph = (t * fps / span) % 2.0                 # 0..2: there and back
            u = 0.5 - 0.5 * math.cos(math.pi * ph)      # eased ping-pong
            return self.blend(u * span, interp=interp)
        return self.frame(0)

    def feature(self, key, x=None):
        """Projected point of interest (px, scaled) from meta 'features'; with a fractional frame index
        x and per-frame data ('features_per_frame') it is interpolated along the animation."""
        k = self.scale
        fpf = self._fpf
        if x is not None and fpf:
            seq = fpf.get(key) if isinstance(fpf, dict) else [f.get(key) for f in fpf]
            if seq:
                x = min(max(float(x), 0.0), len(seq) - 1.0)
                i0 = int(math.floor(x))
                i1 = min(i0 + 1, len(seq) - 1)
                f = x - i0
                p0, p1 = seq[i0], seq[i1]
                return ((p0[0] * (1 - f) + p1[0] * f) * k, (p0[1] * (1 - f) + p1[1] * f) * k)
        return self.features.get(key)

    def feature_at_time(self, key, t, fps=None, loop=None):
        """feature() at time t, following the same timing as at_time (anim/spin)."""
        fps = float(fps or self.fps)
        loop = self.loop if loop is None else loop
        x = t * fps
        x = x % self.n if loop else min(max(x, 0.0), self.n - 1.0)
        return self.feature(key, x)

    def by_label(self, label):
        """Static assets: frame by its meta label (e.g. 'torus_glass')."""
        return self.frame(self.labels.index(label))

    def __repr__(self):
        return (f'Asset3D({self.name!r}, {self.variant!r}, mode={self.mode!r}, n={self.n}, size={self.size}, '
                f'anchor=({self.anchor[0]:.1f}, {self.anchor[1]:.1f}){", FALLBACK" if self.fallback else ""})')


@lru_cache(maxsize=128)
def get(name, variant='night', mode=None, scale=1.0):
    """Cached Asset3D instance (frames themselves live in the shared byte-budgeted LRU)."""
    return Asset3D(name, variant, mode=mode, scale=scale)


# ----------------------------------------------------------------------------- helpers for previews

def to_srgb8(img):
    """Linear premultiplied RGBA or linear RGB float -> sRGB uint8 RGB (for quick previews)."""
    rgb = img[:, :, :3]
    rgb = np.clip(rgb, 0, None)
    s = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)
    return np.clip(s * 255 + 0.5, 0, 255).astype(np.uint8)


def over(dst, spr, x, y, anchor=(0.0, 0.0)):
    """Integer-placement premultiplied 'over' for previews/tests (the compositor has its own
    sub-pixel sprite draw). Places spr's `anchor` at canvas (x, y)."""
    h, w = spr.shape[:2]
    x0 = int(round(x - anchor[0]))
    y0 = int(round(y - anchor[1]))
    H, W = dst.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + w), min(H, y0 + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return dst
    s = spr[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)]
    d = dst[dy0:dy1, dx0:dx1]
    d[:, :, :3] = s[:, :, :3] + d[:, :, :3] * (1 - s[:, :, 3:4])
    if d.shape[2] == 4:
        d[:, :, 3:4] = s[:, :, 3:4] + d[:, :, 3:4] * (1 - s[:, :, 3:4])
    return dst


def _hexlin(h):
    h = h.lstrip('#')
    c = np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def _backdrop(w, h, kind):
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    xx = np.linspace(-1, 1, w, dtype=np.float32)[None, :, None]
    if kind == 'night':
        top, bot, glow = _hexlin('#1C0822'), _hexlin('#0B0310'), _hexlin('#B7006E')
        g = np.exp(-((xx - 0.3) ** 2 + (yy - 0.35) ** 2 * 3) * 2.2) * 0.35
    else:
        top, bot, glow = _hexlin('#FCF8F5'), _hexlin('#F6EAF3'), _hexlin('#FFD4BA')
        g = np.exp(-((xx + 0.3) ** 2 + (yy - 0.4) ** 2 * 3) * 2.0) * 0.5
    img = top * (1 - yy) + bot * yy
    img = img + g * (glow - img) * (1.0 if kind == 'day' else 1.0)
    return np.dstack([np.broadcast_to(img, (h, w, 3)), np.ones((h, w, 1), np.float32)]).astype(np.float32)


def selftest():
    import cv2
    import time
    out = os.path.join(_ws(), 'out', 'selftest')
    os.makedirs(out, exist_ok=True)
    have = list_assets()
    print('assets:', have)
    if not have:
        print('no rendered assets yet')
        return
    # 1) a gallery: every asset/variant at yaw -20/0/+20 (or 3 frames) over night + ivory backdrops
    cell = 220
    rows = []
    for name, variants in have.items():
        for v in variants:
            try:
                a0 = Asset3D(name, v)
                a = Asset3D(name, v, scale=cell / max(a0.src_size))
            except Exception as e:  # incomplete folders are fine during rendering
                print('skip', name, v, e)
                continue
            if a.mode == 'yaw':
                imgs = [a.at_yaw(d) for d in (-20.0, 0.0, 20.0)]
            elif a.mode == 'spin':
                imgs = [a.at_yaw(d) for d in (0.0, 45.0, 100.0)]
            else:
                imgs = [a.frame(i) for i in range(min(a.n, 6))]
            for kind in ('night', 'day'):
                tiles = []
                for im in imgs:
                    bg = _backdrop(cell, cell, kind)
                    over(bg, im, cell / 2, cell / 2, a.anchor)
                    tiles.append(to_srgb8(bg))
                row = np.concatenate(tiles, 1)[:, :, ::-1].copy()
                cv2.putText(row, f'{name}/{v} {a.mode} [{kind}]', (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                            (235, 225, 240) if kind == 'night' else (60, 30, 50), 1, cv2.LINE_AA)
                rows.append(row)
    wmax = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in rows]
    for k in range(0, len(rows), 12):
        cv2.imwrite(os.path.join(out, f'sprites3d_gallery_{k // 12}.png'), np.concatenate(rows[k:k + 12], 0))
    # 2) yaw blending check on the first completed yaw asset
    done = [(n, v) for n, vs in have.items() for v in vs
            if os.path.exists(os.path.join(assets_root(), n, v, 'meta.json'))]
    if not done:
        print('no completed asset yet (meta.json missing everywhere)')
        return
    name, v0 = next(((n, v) for n, v in done if Asset3D(n, v).mode == 'yaw'), done[0])
    a = Asset3D(name, v0)
    if a.mode == 'yaw':
        i = a.n // 2
        y0, y1 = a.index_to_yaw(i), a.index_to_yaw(i + 1)
        mid = a.at_yaw((y0 + y1) / 2)
        ref = (a.frame(i) + a.frame(i + 1)) / 2
        assert np.allclose(mid, ref, atol=1e-5), 'yaw blend mismatch'
        assert np.allclose(a.at_yaw(y0), a.frame(i)), 'exact yaw must hit the frame'
        assert np.allclose(a.at_yaw(-999), a.frame(0)) and np.allclose(a.at_yaw(999), a.frame(a.n - 1))
    # 3) timing / cache
    t = time.time()
    for k in range(30):
        a.float_yaw(k / 30.0)
    dt = (time.time() - t) / 30
    print(f'float_yaw: {dt * 1000:.1f} ms/call; cache {cache_stats()}')
    if a.mode == 'yaw':   # flow interpolation must sit closer to the true frame than a cross-fade
        i = a.n // 5                       # off-axis: the silhouette moves most away from face-on
        true = a.frame(i)
        # rebuild frame i from frames i-1 and i+1 through a 2-frame view of the same asset
        fl = Asset3D(name, v0)
        fl.dir = fl.dir + '#pair'          # separate flow-cache key
        fl._files = {0: a._path(i - 1), 1: a._path(i + 1)}
        fl.n, fl._avail = 2, np.array([0, 1])
        e_flow = np.abs(fl.blend(0.5, interp='flow') - true)[:, :, :3].mean()
        e_blend = np.abs(fl.blend(0.5, interp='blend') - true)[:, :, :3].mean()
        print(f'mid-frame error: flow {e_flow:.5f} vs blend {e_blend:.5f}')
        assert e_flow <= e_blend * 1.05
    # 4) premultiplied invariants
    f = a.frame(0)
    assert f.dtype == np.float32 and f.shape[2] == 4
    assert (f[:, :, :3] <= f[:, :, 3:4] + 1e-4).all(), 'colour must not exceed alpha (premultiplied)'
    # 5) a motion strip: float_yaw over 2 s on the night backdrop (spin assets: at_time)
    strip = []
    for name, v in done:
        a0 = Asset3D(name, v)
        a = Asset3D(name, v, scale=180.0 / max(a0.src_size))
        if a.mode not in ('yaw', 'spin'):
            continue
        tiles = []
        for k in range(8):
            t = k * 0.25
            im = a.float_yaw(t, amp=30, period=2.0) if a.mode == 'yaw' else a.at_time(t, fps=30)
            bg = _backdrop(a.size[0], a.size[1], 'night')
            over(bg, im, a.size[0] / 2, a.size[1] / 2, a.anchor)
            tiles.append(to_srgb8(bg))
        strip.append(np.concatenate(tiles, 1)[:, :, ::-1])
        if len(strip) >= 6:
            break
    if strip:
        wmax = max(r.shape[1] for r in strip)
        strip = [np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in strip]
        cv2.imwrite(os.path.join(out, 'sprites3d_motion.png'), np.concatenate(strip, 0))
    print('selftest ok ->', out)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        print(__doc__)
