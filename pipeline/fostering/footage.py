"""footage.py: graded, time-remapped access to the client's footage (workspace3/frames/cXX/%05d.jpg).

Every returned image is a premultiplied LINEAR float32 RGBA sprite (alpha = 1), ready for core.draw /
core.draw_plane. Frames are decoded lazily (at 1/2 or 1/4 resolution when the output is small) into a
bounded, process-wide LRU cache of uint8 frames (env FOSTER_CLIP_CACHE_MB, default 160 MB per process).

CLIPS
    clip_info() -> {cid: {'name', 'fps', 'dur', 'w', 'h', 'frames', 'src'}}
    FOCUS[cid] -> default normalised (x, y) subject point for portrait crops (c13 already crops right).
    c = Clip('c01')            # c.fps, c.dur, c.frames, c.w, c.h, c.focus
    c.frame(t_src, blend=True) -> uint8 RGB full frame (frame-blended between neighbours for fractional t)
    c.get(t_src, out_w, out_h, center=None, zoom=1.0, rot=0.0, look=None, blend=True, pan=(0, 0))
        -> (out_h, out_w, 4) sprite. Cover-crop around `center` (normalised focus, default FOCUS[cid]),
        zoom >= 1 punches in (Ken Burns), rot in degrees (auto-zooms so no border shows), pan = extra
        offset in OUTPUT px. Crops BEFORE converting to float; times clamp to the clip.
        look: None | 'neon' | 'amber' | 'airy' | 'natural' (see grade()).
    c.at(t_out, t0, src0=0.0, speed=1.0) -> source time for a constant-speed play started at t_out = t0
    still(path, out_w, out_h, center=(0.5, 0.5), zoom=1.0, rot=0.0, look=None) -> sprite from any image
        (site_img .webp/.jpg), same cover/grade logic.

TIME
    SpeedRamp([(t_out, speed), (t_out, speed, ease_to_next), ...], src0=0.0)
        r = SpeedRamp([(0, 1.0), (0.8, 1.0), (1.3, 0.4, 'inout_sine'), (3.0, 0.4)], src0=2.0)
        r(t_out) -> source seconds (speed integrated, so motion stays continuous); r.speed(t_out)
        Before the first key and after the last one the end speeds continue.
    ramp_src(t, t0, src0, speed=1.0) -> src0 + (t - t0) * speed

GRADE (display-referred curves + luminance split-toning; skin-safe: mids stay neutral)
    grade(rgb_linear, look) -> graded linear RGB (any (h, w, 3) float array, float precision)
    grade_u8(rgb_u8, look) -> graded linear float32 (h, w, 3) (fast path used by Clip.get)
    grade_u8_display(rgb_u8, look) -> graded uint8 sRGB (h, w, 3) (for previews / sheets)
    cover_crop(img, out_w, out_h, center=(.5, .5), zoom=1, rot=0, pan=(0, 0)) -> exact-size crop of any
        uint8 image (sub-pixel accurate, anti-aliased); building block of Clip.get and still()
    GRADES[look] -> parameters: wb, exposure, contrast, pivot, black, black_tint, shadow_tint,
        highlight_tint, sat. Looks: 'neon' rich contrast, warm skin, plum shadows, magenta/orange split;
        'amber' golden-hour warm, teal-free shadows; 'airy' bright, soft contrast, milky warm blacks;
        'natural' gentle clean-up.

SHEETS
    contact_sheet(cid, n=12, cols=4, look=None, path=None, width=1800, t0=None, t1=None) -> path of a JPG
        (default out/sheets/<cid>[_look].jpg) with burnt-in timestamps

PERFORMANCE (1 core): full-bleed 1080x1920 get ~60-110 ms (two frames when blending), a 700x1000 card ~25 ms,
a 400x600 thumbnail ~8 ms. Memory: 4K frames are 21 MB decoded; small outputs decode at 1/2 - 1/8 size.

Example
    import core as K, footage as F
    clip = F.Clip('c12')
    spr = clip.get(clip.at(t, 2.0, src0=6.0), 700, 1000, zoom=1.1 + 0.05 * t, look='neon')
    K.draw_plane(cv, spr, cam, (0, 0, 200), 760, rot=(3, -12, 0))
"""
import collections
import functools
import json
import math
import os

import cv2
import numpy as np

import core as K

# =============================================================================================== clips
FOCUS = {
    'c00': (0.44, 0.45), 'c01': (0.47, 0.45), 'c02': (0.40, 0.50), 'c03': (0.45, 0.50),
    'c04': (0.52, 0.45), 'c05': (0.45, 0.40), 'c06': (0.45, 0.45), 'c07': (0.60, 0.50),
    'c08': (0.50, 0.50), 'c09': (0.55, 0.50), 'c10': (0.52, 0.42), 'c11': (0.60, 0.45),
    'c12': (0.55, 0.42), 'c13': (0.68, 0.45), 'c14': (0.52, 0.45), 'c15': (0.50, 0.45),
    'c16': (0.62, 0.40), 'c17': (0.50, 0.40), 'c18': (0.60, 0.45),
}


@functools.lru_cache(maxsize=1)
def _manifest():
    with open(os.path.join(K.FRAMES, 'manifest.json')) as f:
        return json.load(f)


@functools.lru_cache(maxsize=64)
def _clip_meta(cid):
    m = dict(_manifest()[cid])
    d = os.path.join(K.FRAMES, cid)
    files = sorted(f for f in os.listdir(d) if f.endswith('.jpg'))
    from PIL import Image
    with Image.open(os.path.join(d, files[0])) as im:      # header only
        w, h = im.size
    return {'name': m.get('name', cid), 'fps': float(m['fps']), 'dur': float(m['dur']), 'w': w, 'h': h,
            'frames': len(files), 'src': m.get('src', ''), 'dir': d}


def clip_info():
    """All clips: {cid: {'name', 'fps', 'dur', 'w', 'h', 'frames', 'src'}} (frame dims as decoded)."""
    out = {}
    for cid in sorted(_manifest()):
        m = _clip_meta(cid)
        out[cid] = {k: m[k] for k in ('name', 'fps', 'dur', 'w', 'h', 'frames', 'src')}
    return out


class _FrameCache:
    """Process-wide LRU of decoded uint8 frames, bounded by bytes."""

    def __init__(self, budget_mb):
        self.d = collections.OrderedDict()
        self.bytes = 0
        self.budget = int(budget_mb * 1024 * 1024)
        self.hits = self.misses = 0

    def get(self, key, loader):
        v = self.d.get(key)
        if v is not None:
            self.d.move_to_end(key)
            self.hits += 1
            return v
        self.misses += 1
        v = loader()
        self.d[key] = v
        self.bytes += v.nbytes
        while self.bytes > self.budget and len(self.d) > 1:
            _, old = self.d.popitem(last=False)
            self.bytes -= old.nbytes
        return v

    def clear(self):
        self.d.clear()
        self.bytes = 0


_FRAMES = _FrameCache(float(os.environ.get('FOSTER_CLIP_CACHE_MB', '160')))
_REDUCE_FLAGS = {1: cv2.IMREAD_COLOR, 2: cv2.IMREAD_REDUCED_COLOR_2, 4: cv2.IMREAD_REDUCED_COLOR_4,
                 8: cv2.IMREAD_REDUCED_COLOR_8}


def ramp_src(t, t0, src0, speed=1.0):
    """Source time for constant-speed playback that starts at output time t0 at source time src0."""
    return src0 + (t - t0) * speed


class Clip:
    """Time-remapped access to one footage clip (see module docstring)."""

    def __init__(self, cid):
        m = _clip_meta(cid)
        self.cid = cid
        self.name = m['name']
        self.fps = m['fps']
        self.frames = m['frames']
        self.dur = self.frames / self.fps
        self.w, self.h = m['w'], m['h']
        self.dir = m['dir']
        self.focus = FOCUS.get(cid, (0.5, 0.5))

    def __repr__(self):
        return 'Clip(%s %dx%d %.2ffps %.2fs)' % (self.cid, self.w, self.h, self.fps, self.dur)

    # ---- raw frames
    def _read(self, i, reduce=1):
        i = int(min(max(i, 0), self.frames - 1))
        path = os.path.join(self.dir, '%05d.jpg' % i)

        def load():
            im = cv2.imread(path, _REDUCE_FLAGS[reduce])
            if im is None:
                raise FileNotFoundError(path)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            im.setflags(write=False)
            return im
        return _FRAMES.get((self.cid, i, reduce), load)

    def index(self, t_src):
        """Fractional frame index for a source time (clamped to the clip)."""
        return min(max(t_src * self.fps, 0.0), self.frames - 1.0)

    def at(self, t_out, t0, src0=0.0, speed=1.0):
        return ramp_src(t_out, t0, src0, speed)

    def frame(self, t_src, blend=True, reduce=1):
        """uint8 RGB frame at source time t_src; fractional times blend neighbouring frames."""
        f = self.index(t_src)
        i0 = int(math.floor(f))
        w = f - i0
        a = self._read(i0, reduce)
        if not blend or w < 0.01 or i0 + 1 >= self.frames:
            return a
        if w > 0.99:
            return self._read(i0 + 1, reduce)
        return cv2.addWeighted(a, 1.0 - w, self._read(i0 + 1, reduce), w, 0.0)

    # ---- graded sprites
    def get(self, t_src, out_w, out_h, center=None, zoom=1.0, rot=0.0, look=None, blend=True, pan=(0.0, 0.0)):
        """Graded linear RGBA sprite (out_h, out_w, 4), cover-cropped (see module docstring)."""
        out_w, out_h = int(out_w), int(out_h)
        center = self.focus if center is None else center
        f = self.index(t_src)
        i0 = int(math.floor(f))
        w = f - i0
        reduce = _pick_reduce(self.w, self.h, out_w, out_h, zoom, rot)
        idx = [(i0, 1.0)]
        if blend and 0.01 <= w <= 0.99 and i0 + 1 < self.frames:
            idx = [(i0, 1.0 - w), (i0 + 1, w)]
        elif blend and w > 0.99 and i0 + 1 < self.frames:
            idx = [(i0 + 1, 1.0)]
        u8 = None
        for i, wt in idx:
            img = self._read(i, reduce)
            crop = cover_crop(img, out_w, out_h, center, zoom, rot, pan)
            if u8 is None:
                u8 = crop if wt == 1.0 else crop
                w0 = wt
            else:
                u8 = cv2.addWeighted(u8, w0, crop, wt, 0.0)
        return _to_sprite(u8, look)


def _pick_reduce(sw, sh, out_w, out_h, zoom, rot):
    """Largest JPEG DCT downscale (1/2/4/8) that still leaves >= 1 source px per output px."""
    scale = max(out_w / sw, out_h / sh) * max(zoom, 1e-3) * _rot_cover(out_w, out_h, sw, sh, rot)
    r = 1
    while r < 8 and scale * (r * 2) <= 1.0:
        r *= 2
    return r


def _rot_cover(ow, oh, sw, sh, rot):
    if abs(rot) < 1e-3:
        return 1.0
    a = math.radians(rot)
    c, s = abs(math.cos(a)), abs(math.sin(a))
    base = max(ow / sw, oh / sh)
    cw, ch = ow / base, oh / base
    bw, bh = cw * c + ch * s, cw * s + ch * c
    return max(1.0, bw / sw, bh / sh)


def cover_crop(img, out_w, out_h, center=(0.5, 0.5), zoom=1.0, rot=0.0, pan=(0.0, 0.0)):
    """Cover-crop a uint8 (or float) image to exactly (out_h, out_w) around a normalised focus point,
    with zoom (>= 1 punches in), rotation (degrees, auto-zoom to hide borders) and an output-px pan.
    Sub-pixel accurate (no jitter on slow Ken Burns moves); anti-aliased when shrinking."""
    sh, sw = img.shape[:2]
    zoom = max(zoom, 1e-3)
    scale = max(out_w / sw, out_h / sh) * zoom
    scale *= _rot_cover(out_w, out_h, sw, sh, rot) if abs(rot) > 1e-3 else 1.0
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    # source-space size of the rotated output footprint (axis-aligned bbox)
    cw, ch = out_w / scale, out_h / scale
    bw, bh = cw * abs(c) + ch * abs(s), cw * abs(s) + ch * abs(c)
    cx = center[0] * sw - pan[0] / scale
    cy = center[1] * sh - pan[1] / scale
    cx = min(max(cx, bw / 2), sw - bw / 2) if bw <= sw else sw / 2
    cy = min(max(cy, bh / 2), sh - bh / 2) if bh <= sh else sh / 2
    # integer sub-window with margin
    x0 = max(0, int(math.floor(cx - bw / 2)) - 2)
    y0 = max(0, int(math.floor(cy - bh / 2)) - 2)
    x1 = min(sw, int(math.ceil(cx + bw / 2)) + 2)
    y1 = min(sh, int(math.ceil(cy + bh / 2)) + 2)
    sub = img[y0:y1, x0:x1]
    lcx, lcy = cx - x0, cy - y0
    # pre-shrink by powers of two with area filtering so the warp works near 1:1
    k = 1
    while scale * k * 2 <= 1.0 and min(sub.shape[:2]) // (k * 2) > 8:
        k *= 2
    if k > 1:
        sub = cv2.resize(sub, (max(1, sub.shape[1] // k), max(1, sub.shape[0] // k)), interpolation=cv2.INTER_AREA)
        fx = sub.shape[1] / ((x1 - x0) / k) / k
        fy = sub.shape[0] / ((y1 - y0) / k) / k
        lcx, lcy = lcx * fx, lcy * fy
        sc = scale / fx
    else:
        sc = scale
    if sc < 0.85:                                     # residual minification: gaussian pre-filter
        sig = 0.5 * math.sqrt(1.0 / (sc * sc) - 1.0)
        sub = cv2.GaussianBlur(sub, (0, 0), sig)
    # affine: output pixel centre -> sub pixel centre
    # X_out = R * sc * (X_sub - lc) + out_c   (continuous coords, rotation clockwise)
    M = np.array([[c * sc, -s * sc, 0.0], [s * sc, c * sc, 0.0]])
    M[0, 2] = out_w / 2 - (M[0, 0] * lcx + M[0, 1] * lcy) - 0.5 + (M[0, 0] + M[0, 1]) * 0.5
    M[1, 2] = out_h / 2 - (M[1, 0] * lcx + M[1, 1] * lcy) - 0.5 + (M[1, 0] + M[1, 1]) * 0.5
    interp = cv2.INTER_CUBIC if sc > 1.05 else cv2.INTER_LINEAR
    return cv2.warpAffine(np.ascontiguousarray(sub), M, (out_w, out_h), flags=interp,
                          borderMode=cv2.BORDER_REFLECT101)


# =============================================================================================== grade
GRADES = {
    # wb: linear-light channel gains; exposure: stops; contrast: slope at pivot (display space);
    # black: lift of the black point towards black_tint (sRGB colour); tints: display-space offsets
    # weighted by shadow / highlight luminance (mids stay neutral so skin stays natural).
    'neon': dict(wb=(1.02, 1.0, 0.97), exposure=0.0, contrast=1.18, pivot=0.40, black=0.035,
                 black_tint=(0.36, 0.09, 0.31), shadow_tint=(0.026, -0.010, 0.032),
                 highlight_tint=(0.018, 0.004, -0.016), sat=1.05, shoulder=0.92),
    'amber': dict(wb=(1.07, 1.0, 0.88), exposure=0.05, contrast=1.12, pivot=0.40, black=0.03,
                  black_tint=(0.30, 0.14, 0.06), shadow_tint=(0.022, 0.008, -0.012),
                  highlight_tint=(0.030, 0.006, -0.030), sat=1.04, shoulder=0.92),
    'airy': dict(wb=(1.03, 1.0, 0.97), exposure=0.30, contrast=0.88, pivot=0.45, black=0.075,
                 black_tint=(0.62, 0.52, 0.58), shadow_tint=(0.012, 0.0, 0.014),
                 highlight_tint=(0.012, 0.006, -0.008), sat=0.95, shoulder=0.88),
    'natural': dict(wb=(1.0, 1.0, 1.0), exposure=0.0, contrast=1.05, pivot=0.42, black=0.01,
                    black_tint=(0.2, 0.2, 0.2), shadow_tint=(0.0, 0.0, 0.0), highlight_tint=(0.0, 0.0, 0.0),
                    sat=1.0, shoulder=0.95),
}


def _s_curve(x, contrast, pivot):
    """Power S-curve with slope `contrast` at `pivot`, mapping 0->0 and 1->1."""
    x = np.clip(x, 0.0, 1.0)
    lo = pivot * (x / pivot) ** contrast
    hi = 1.0 - (1.0 - pivot) * ((1.0 - x) / (1.0 - pivot)) ** contrast
    return np.where(x < pivot, lo, hi)


@functools.lru_cache(maxsize=16)
def _channel_lut(look, n=256):
    """Per-channel 1D part of the grade: (n, 3) display-space output for display-space input levels."""
    g = GRADES[look]
    s = np.linspace(0.0, 1.0, n)
    lin = K.to_lin(s).astype(np.float64)
    out = np.zeros((n, 3))
    for c in range(3):
        l = lin * g['wb'][c] * 2 ** g['exposure']
        # gentle highlight shoulder in linear light before re-encoding
        k = g['shoulder']
        l = np.where(l <= k, l, k + (1 - k) * (1 - np.exp(-(l - k) / (1 - k))))
        d = K.to_srgb(np.clip(l, 0, 1)).astype(np.float64)
        d = _s_curve(d, g['contrast'], g['pivot'])
        d = d * (1 - g['black']) + g['black'] * g['black_tint'][c]
        out[:, c] = d
    return out.astype(np.float32)


@functools.lru_cache(maxsize=8)
def _sat_matrix(sat):
    l = np.array([0.2126, 0.7152, 0.0722], np.float32)
    return (np.eye(3, dtype=np.float32) * sat + (1 - sat) * np.tile(l, (3, 1))).astype(np.float32)


@functools.lru_cache(maxsize=1)
def _lin_lut4096():
    return K.to_lin(np.arange(4096, dtype=np.float32) / 4095.0)


@functools.lru_cache(maxsize=1)
def _rgba_lut():
    """(256, 1, 4) float LUT: sRGB u8 -> linear for RGB, 255 -> 1.0 for alpha."""
    lut = np.zeros((256, 1, 4), np.float32)
    lut[:, 0, :3] = K._lin_lut8()[:, None]
    lut[:, 0, 3] = np.arange(256, dtype=np.float32) / 255.0
    return lut


@functools.lru_cache(maxsize=16)
def _tint_lut(look):
    """(256, 1, 3) display-space offsets as a function of luma: shadow tint + highlight tint."""
    g = GRADES[look]
    L = np.arange(256, dtype=np.float64) / 255.0
    sh = np.clip(1.0 - L * 2.2, 0, 1) ** 2
    hl = np.clip((L - 0.5) * 2.0, 0, 1) ** 1.5
    t = sh[:, None] * np.asarray(g['shadow_tint']) + hl[:, None] * np.asarray(g['highlight_tint'])
    return t.astype(np.float32).reshape(256, 1, 3)


_LUMA_ROW = np.float32([[0.2126, 0.7152, 0.0722]])


def _grade_display(s, look):
    """Cross-channel part on display-space float32 (h, w, 3) that already went through the channel LUT:
    saturation matrix, then luminance-driven split toning (shadows / highlights only)."""
    g = GRADES[look]
    if g['sat'] != 1.0:
        s = cv2.transform(s, _sat_matrix(float(g['sat'])))
    if np.any(g['shadow_tint']) or np.any(g['highlight_tint']):
        L = cv2.transform(s, _LUMA_ROW)
        Lq = cv2.convertScaleAbs(L, alpha=255.0)
        T = cv2.LUT(cv2.cvtColor(Lq, cv2.COLOR_GRAY2RGB), _tint_lut(look))
        s = cv2.add(s, T)
    return s


def _display_to_lin(s):
    idx = s * np.float32(4095.0)
    idx += np.float32(0.5)
    np.clip(idx, 0, 4095, out=idx)
    return _lin_lut4096()[idx.astype(np.uint16)]


def grade_u8_display(rgb_u8, look):
    """uint8 sRGB -> graded uint8 sRGB (h, w, 3) (fast; the grade's output is re-quantised to 8 bit)."""
    if look is None or look == 'none':
        return rgb_u8
    s = cv2.LUT(np.ascontiguousarray(rgb_u8), _channel_lut(look).reshape(256, 1, 3))
    s = _grade_display(s, look)
    return cv2.convertScaleAbs(s, alpha=255.0)


def grade_u8(rgb_u8, look):
    """uint8 sRGB (h, w, 3) -> graded linear float32 (h, w, 3). look None/'none' = plain linearisation."""
    return cv2.LUT(grade_u8_display(rgb_u8, look), K._lin_lut8())


def grade(rgb_linear, look):
    """Grade any linear float RGB array (h, w, 3) -> graded linear float32 (h, w, 3) (float precision)."""
    if look is None or look == 'none':
        return np.asarray(rgb_linear, np.float32)
    s = K.to_srgb(np.asarray(rgb_linear, np.float32)[..., :3])
    lut = _channel_lut(look, 4096)
    idx = np.clip(np.round(s * 4095), 0, 4095).astype(np.int32)
    d = np.stack([lut[idx[..., c], c] for c in range(3)], -1).astype(np.float32)
    return _display_to_lin(_grade_display(d, look))


def _to_sprite(u8, look):
    """Graded uint8 RGB -> (h, w, 4) premultiplied linear sprite with alpha 1 (two OpenCV LUT passes)."""
    g = grade_u8_display(u8, look)
    return cv2.LUT(cv2.cvtColor(g, cv2.COLOR_RGB2RGBA), _rgba_lut())


@functools.lru_cache(maxsize=24)
def _still_u8(path):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    if im is None:
        from PIL import Image
        im = np.asarray(Image.open(path).convert('RGB'))
    else:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im.setflags(write=False)
    return im


def still(path, out_w, out_h, center=(0.5, 0.5), zoom=1.0, rot=0.0, look=None, pan=(0.0, 0.0)):
    """Graded cover-cropped sprite from a still image (e.g. workspace3/site_img/*.webp)."""
    if not os.path.isabs(path):
        cand = os.path.join(K.SITE_IMG, path)
        path = cand if os.path.exists(cand) else path
    img = _still_u8(path)
    return _to_sprite(cover_crop(img, int(out_w), int(out_h), center, zoom, rot, pan), look)


# =============================================================================================== time
class SpeedRamp:
    """Output time -> source time with a variable playback speed (integrated, so motion is continuous).
    keys: [(t_out, speed), (t_out, speed, ease_to_next), ...] (Track semantics for the speed curve)."""

    def __init__(self, keys, src0=0.0, dt=1.0 / 600.0):
        self.track = K.Track([(k[0], float(k[1])) + tuple(k[2:]) for k in keys], ease='inout_sine')
        self.t0 = float(self.track.start)
        self.t1 = float(self.track.end)
        self.src0 = float(src0)
        n = max(2, int(math.ceil((self.t1 - self.t0) / dt)) + 1)
        self.ts = np.linspace(self.t0, self.t1, n)
        sp = np.array([self.track(t) for t in self.ts])
        cum = np.concatenate([[0.0], np.cumsum((sp[1:] + sp[:-1]) * 0.5 * np.diff(self.ts))])
        self.cum = cum
        self.v0, self.v1 = float(sp[0]), float(sp[-1])

    def speed(self, t):
        return self.track(t)

    def __call__(self, t):
        if t <= self.t0:
            return self.src0 + (t - self.t0) * self.v0
        if t >= self.t1:
            return self.src0 + self.cum[-1] + (t - self.t1) * self.v1
        return self.src0 + float(np.interp(t, self.ts, self.cum))


# =============================================================================================== sheets
def contact_sheet(cid, n=12, cols=4, look=None, path=None, width=1800, t0=None, t1=None):
    """Write a contact sheet of n evenly spaced frames of a clip (timestamps burnt in). Returns the path."""
    c = Clip(cid)
    t0 = 0.0 if t0 is None else t0
    t1 = c.dur - 1.0 / c.fps if t1 is None else t1
    rows = int(math.ceil(n / cols))
    tw = width // cols
    th = int(round(tw * c.h / c.w))
    sheet = np.zeros((rows * th + 50, cols * tw, 3), np.uint8)
    for k in range(n):
        t = t0 + (t1 - t0) * k / max(1, n - 1)
        spr = c.get(t, tw, th, center=(0.5, 0.5), look=look)
        u8 = K.to_srgb8(spr, dither=False)
        cv2.putText(u8, '%.2fs' % t, (8, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(u8, '%.2fs' % t, (8, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 230, 80), 1, cv2.LINE_AA)
        r, q = divmod(k, cols)
        sheet[50 + r * th:50 + (r + 1) * th, q * tw:(q + 1) * tw] = u8
    title = '%s  %s  %dx%d  %.2f fps  %.2f s  look=%s' % (cid, c.name, c.w, c.h, c.fps, c.dur, look)
    cv2.putText(sheet, title, (12, 34), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1, cv2.LINE_AA)
    path = path or os.path.join(K.OUT, 'sheets', '%s%s.jpg' % (cid, '_' + look if look else ''))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    return path


# =============================================================================================== self-test
def selftest():
    import time
    os.makedirs(K.SELFTEST, exist_ok=True)
    outs = []
    # 1. grade looks side by side on c01 and c12 (skin check), portrait crops at native-ish res
    rows = []
    for cid, t in (('c01', 7.0), ('c12', 14.7), ('c10', 18.0)):
        clip = Clip(cid)
        tiles = []
        for look in (None, 'natural', 'neon', 'amber', 'airy'):
            spr = clip.get(t, 540, 960, look=look)
            u8 = K.to_srgb8(spr, dither=False)
            u8 = np.ascontiguousarray(u8)
            cv2.putText(u8, '%s %s' % (cid, look or 'ungraded'), (14, 40), cv2.FONT_HERSHEY_DUPLEX, 1.0,
                        (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(u8, '%s %s' % (cid, look or 'ungraded'), (14, 40), cv2.FONT_HERSHEY_DUPLEX, 1.0,
                        (255, 255, 255), 1, cv2.LINE_AA)
            tiles.append(u8)
        rows.append(np.concatenate(tiles, 1))
    p = os.path.join(K.SELFTEST, 'footage_grades.png')
    cv2.imwrite(p, cv2.cvtColor(np.concatenate(rows, 0), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    outs.append(p)
    print('wrote', p)
    # 2. skin close-up crops (full resolution) neon vs ungraded
    clip = Clip('c01')
    a = K.to_srgb8(clip.get(7.0, 540, 540, center=(0.47, 0.42), zoom=2.2, look=None), dither=False)
    b = K.to_srgb8(clip.get(7.0, 540, 540, center=(0.47, 0.42), zoom=2.2, look='neon'), dither=False)
    c = K.to_srgb8(clip.get(7.0, 540, 540, center=(0.47, 0.42), zoom=2.2, look='amber'), dither=False)
    d = K.to_srgb8(clip.get(7.0, 540, 540, center=(0.47, 0.42), zoom=2.2, look='airy'), dither=False)
    p = os.path.join(K.SELFTEST, 'footage_skin.png')
    cv2.imwrite(p, cv2.cvtColor(np.concatenate([a, b, c, d], 1), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    outs.append(p)
    print('wrote', p)
    # 3. Ken Burns + rotation + speed ramp strip
    clip = Clip('c12')
    ramp = SpeedRamp([(0, 1.0), (0.6, 1.0), (1.2, 0.4), (2.0, 0.4)], src0=5.0)
    tiles = []
    for k, t in enumerate(np.linspace(0, 2.0, 6)):
        spr = clip.get(ramp(t), 360, 640, zoom=1.0 + 0.25 * t, rot=-4 + 4 * t, look='neon')
        u8 = np.ascontiguousarray(K.to_srgb8(spr, dither=False))
        cv2.putText(u8, 't=%.1f src=%.2f v=%.1f' % (t, ramp(t), ramp.speed(t)), (8, 28), cv2.FONT_HERSHEY_DUPLEX,
                    0.6, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(u8)
    p = os.path.join(K.SELFTEST, 'footage_kenburns.png')
    cv2.imwrite(p, cv2.cvtColor(np.concatenate(tiles, 1), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    outs.append(p)
    print('wrote', p)
    # 4. contact sheet
    p = contact_sheet('c13', n=8, cols=4, look='neon', path=os.path.join(K.SELFTEST, 'footage_sheet_c13.png'))
    outs.append(p)
    print('wrote', p)
    # 5. timing
    for cid, ow, oh in (('c01', 1080, 1920), ('c01', 700, 1000), ('c10', 1080, 1920), ('c10', 400, 600)):
        clip = Clip(cid)
        clip.get(3.0, ow, oh, look='neon')
        t0 = time.time()
        for k in range(6):
            clip.get(3.0 + k * 0.013, ow, oh, zoom=1.05, look='neon')
        print('get %s %dx%d: %.1f ms (cache %d MB)' % (cid, ow, oh, (time.time() - t0) / 6 * 1000,
                                                       _FRAMES.bytes // 2 ** 20))
    return outs


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        selftest()
    else:
        print(__doc__)
