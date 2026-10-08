"""anim1_fx.py: drawing helpers for ANIM 1 "DAY IN THE LIFE" (anim1.py). Pure functions + cached sprites.

PROPS
    P = Prop('backpack', height=300)          # real sprites3d asset when its meta.json exists, else a labelled
                                              # placeholder disc with the same interface
    P.draw(cv, x, y, yaw=0, scale=1, rot=0, squash=(1, 1), opacity=1)   (x, y) = ground contact point
    P.shadow(cv, x, y, light, lift=0, yaw=0, scale=1, opacity=1)       contact + cast shadow on the paper
    P.feature(key, yaw) -> (dx, dy) canvas offset of a feature from the ground point at scale 1
    drop(t, t0, dur=0.32) -> dict(lift, scale, squash, opacity, land): a toy dropping onto the desk
TYPE
    Txt(text, font, px, fill) -> .ts (TextSprite), .spr/.anc (merged sprite + anchor), .w/.h, .words
        words = [(word, x0, x1)] in text-box coords; .word_ts(i) TextSprite of word i
    draw_clip(cv, spr, x, y, anchor, rect) -> bbox: sprite clipped to a canvas rect (slot reveals)
    draw_hmask(cv, spr, x, y, anchor, x0, x1, soft, invert) -> bbox: horizontal soft wipe mask
STROKES
    stroke_alpha(pts, width, u0=0, u1=1, dash=None, ss=4) -> (alpha, x0, y0): anti-aliased partial polyline
    paint(cv, alpha, x0, y0, rgb, opacity) -> bbox: premultiplied colour through an alpha
    scribble_path(x0, x1, y, seed, loops) / wave_path(...) / chevron_pts(...)
    marker_band(w, h, seed) -> alpha (ragged highlighter swipe)
PARTICLES
    puff(cv, t, t0, x, y, n, spread, seed, color, size, up) -> flour / dust puff (pure function of t)
"""
import functools
import math
import os

import cv2
import numpy as np

import core as K
import sprites3d as S3
import type3d as T

W, H = K.W, K.H


# ============================================================================================ props
def asset_ready(name, folder='day'):
    return os.path.exists(os.path.join(K.ASSETS3D, name, folder, 'meta.json'))


class _Placeholder:
    """Stand-in for a sprites3d asset while Blender is still rendering it: a soft shaded disc + label."""
    COLS = {'backpack': 'ORANGE', 'school_bus': 'AMBER', 'book_pencil': 'MAGENTA', 'mixing_bowl': 'PEACH',
            'cupcake': 'HOT_PINK', 'alarm_clock': 'ORANGE', 'family_figures': 'MAGENTA', 'house': 'MAGENTA',
            'heart': 'MAGENTA', 'blocks': 'LEAF', 'leaf': 'LEAF', 'logo_mark3d': 'MAGENTA'}

    def __init__(self, name):
        self.name = name
        self.mode = 'static'
        n = 360
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        r = n * 0.42
        d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2)
        a = np.clip(r - d + 0.5, 0, 1)
        col = K.C[self.COLS.get(name, 'MAGENTA')]
        sh = np.clip(1.15 - 0.6 * ((xx - n * 0.38) ** 2 + (yy - n * 0.36) ** 2) / (r * r), 0.35, 1.3)
        rgb = col[None, None, :] * sh[..., None]
        spr = np.dstack([rgb * a[..., None], a]).astype(np.float32)
        lab = T.render(name.replace('_', ' '), 'ui_ink', px=34, fill='IVORY')
        lab.draw(spr, n / 2, n / 2)
        spr.setflags(write=False)
        self._spr = spr
        self.size = (n, n)
        self.anchor = (n / 2, n / 2)
        self.pivot = (n / 2, n / 2 + r)
        self.ground_y = n / 2 + r
        self.bbox = (n / 2 - r, n / 2 - r, n / 2 + r, n / 2 + r)
        self.features = {}

    def at_yaw(self, deg, interp=None):
        return self._spr

    def frame(self, i):
        return self._spr

    def feature(self, key, x=None):
        return self.anchor


PREVIEW_ROOT = os.path.join(K.OUT, 'preview3d')


class Prop:
    """A 3D toy prop: the final sprites3d render when its meta.json exists, else the Blender agent's low-res
    preview render (out/preview3d, same layout), else a labelled placeholder disc. .source tells which."""

    def __init__(self, name, height=300, mode=None, variant='day'):
        folder = variant + ('_' + mode if mode else '')
        self.name = name
        root = None
        if asset_ready(name, folder):
            self.source = 'final'
        elif os.path.exists(os.path.join(PREVIEW_ROOT, name, folder, 'meta.json')):
            self.source, root = 'preview', PREVIEW_ROOT
        else:
            self.source = 'placeholder'
        self.real = self.source != 'placeholder'
        if self.real:
            a = S3.Asset3D(name, variant, mode=mode, root=root)
            bx0, by0, bx1, by1 = a.bbox
            k = height / max(by1 - by0, 1)
            if k < 0.9:
                a = S3.Asset3D(name, variant, mode=mode, scale=k, root=root)   # pre-downscaled frames (cached)
                k = height / max(a.bbox[3] - a.bbox[1], 1)
            self.a = a
        else:
            self.a = _Placeholder(name)
            k = height / (self.a.bbox[3] - self.a.bbox[1])
        self.k = float(k)
        self.height = height
        self._shadow_cache = {}

    @property
    def width(self):
        b = self.a.bbox
        return (b[2] - b[0]) * self.k

    def sprite(self, yaw=0.0):
        if self.a.mode == 'yaw':
            return self.a.at_yaw(yaw)
        if self.a.mode == 'spin':
            return self.a.at_yaw(yaw)
        return self.a.frame(0)

    def ground(self):
        gx = self.a.pivot[0] if self.a.pivot is not None else self.a.anchor[0]
        return gx, float(self.a.ground_y)

    def anchor_frac(self):
        gx, gy = self.ground()
        return gx / self.a.size[0], gy / self.a.size[1]

    def draw(self, cv, x, y, yaw=0.0, scale=1.0, rot=0.0, squash=(1.0, 1.0), opacity=1.0, blur=0.0, spr=None):
        spr = self.sprite(yaw) if spr is None else spr
        s = self.k * scale
        return K.draw(cv, spr, x, y, scale=(s * squash[0], s * squash[1]), rot=rot, anchor=self.anchor_frac(),
                      opacity=opacity, blur=blur)

    def feature(self, key, yaw=0.0):
        """Canvas offset (dx, dy) of a feature from the ground point, at scale 1, no rotation."""
        try:
            if self.a.mode == 'yaw':
                fx, fy = self.a.feature(key, self.a.yaw_to_index(yaw))
            else:
                fx, fy = self.a.feature(key)
        except Exception:
            fx, fy = self.a.anchor
        gx, gy = self.ground()
        return (fx - gx) * self.k, (fy - gy) * self.k

    def center_offset(self):
        """(dx, dy) from the ground point to the visual centre (bbox centre), scale 1."""
        b = self.a.bbox
        gx, gy = self.ground()
        return ((b[0] + b[2]) / 2 - gx) * self.k, ((b[1] + b[3]) / 2 - gy) * self.k

    def _sil(self, spr):
        key = id(spr)
        hit = self._shadow_cache.get(key)
        if hit is not None and hit[0] is spr:
            return hit[1]
        a = spr[..., 3]
        sil = np.zeros(spr.shape, np.float32)
        sil[..., 3] = a
        if len(self._shadow_cache) > 6:
            self._shadow_cache.clear()
        self._shadow_cache[key] = (spr, sil)
        return sil

    def shadow(self, cv, x, y, light, lift=0.0, yaw=0.0, scale=1.0, opacity=1.0, rot=0.0, spr=None,
               strength=1.0):
        """Soft contact shadow + a cast shadow falling away from the light, darker/tighter as the toy lands.
        lift: height above the paper in px (dropping toys)."""
        spr = self.sprite(yaw) if spr is None else spr
        (dx, dy), ln = light.shadow_dir()
        w = self.width * scale
        # cast shadow: the silhouette, squashed toward the ground, offset away from the light
        sil = self._sil(spr)
        off = (0.10 * self.height * min(ln, 3.0) * 0.45 + 0.55 * lift) * scale
        s = self.k * scale
        bl = 6.0 + 0.10 * lift + 2.0 * min(ln, 3.0)
        op = opacity * strength * 0.30 * float(np.clip(1.0 - lift / 500.0, 0.25, 1.0))
        K.draw(cv, _tinted(sil, SHADOW_RGB), x + dx * off, y + dy * off + 0.25 * off,
               scale=(s * 1.02, s * 0.96), rot=rot, anchor=self.anchor_frac(), opacity=op, blur=bl)
        # contact shadow (ambient occlusion under the base)
        c = _contact()
        cw = w * 0.92 * (1.0 + 0.004 * lift)
        cop = opacity * strength * 0.55 * float(np.clip(1.0 - lift / 140.0, 0.0, 1.0))
        if cop > 0.01:
            K.draw(cv, c, x + dx * 4, y + 2, scale=(cw / c.shape[1], cw * 0.16 / c.shape[0]), opacity=cop)


SHADOW_RGB = (0.115, 0.075, 0.070)


def _tinted(sil, rgb):
    """Silhouette (rgb 0, alpha a) -> shadow sprite with colour rgb (cached by identity)."""
    key = (id(sil), rgb)
    hit = _TINT.get(key)
    if hit is not None and hit[0] is sil:
        return hit[1]
    out = sil.copy()
    out[..., :3] = sil[..., 3:4] * np.float32(rgb)
    out.setflags(write=False)
    if len(_TINT) > 12:
        _TINT.clear()
    _TINT[key] = (sil, out)
    return out


_TINT = {}


@functools.lru_cache(maxsize=1)
def _contact():
    n = 256
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    d = np.sqrt(((xx + 0.5) / (n / 2) - 1) ** 2 + ((yy + 0.5) / (n / 2) - 1) ** 2)
    a = np.clip(1 - d, 0, 1) ** 1.8
    spr = np.zeros((n, n, 4), np.float32)
    spr[..., 3] = a
    spr[..., :3] = a[..., None] * np.float32(SHADOW_RGB) * 0.6
    spr.setflags(write=False)
    return spr


def drop(t, t0, dur=0.30, h0=420.0, s0=0.45, bounce=0.10):
    """A toy dropped onto the desk from above the camera side: returns lift (px above the paper), scale
    (bigger while near the lens), squash (sx, sy) at the landing, opacity, landed fraction.
    Lands exactly at t0 + dur."""
    if t < t0:
        return None
    u = (t - t0) / dur
    if u < 1:
        f = 1.0 - u * u                       # falling (accelerating)
        lift = h0 * f
        sc = 1.0 + s0 * f
        sq = (1.0 - 0.06 * u, 1.0 + 0.10 * u)  # stretch while falling
        op = min(1.0, u / 0.18)
        return dict(lift=lift, scale=sc, squash=sq, opacity=op, land=0.0)
    dt = t - (t0 + dur)
    # small hop after landing + squash spring
    hop = bounce * h0 * max(0.0, math.sin(min(dt / 0.22, 1.0) * math.pi)) * math.exp(-dt * 2.0)
    imp = math.exp(-dt * 9.0) * math.cos(dt * 34.0)
    sq = (1.0 + 0.10 * imp, 1.0 - 0.13 * imp)
    return dict(lift=hop, scale=1.0 + 0.0008 * hop, squash=sq, opacity=1.0, land=1.0)


# ============================================================================================ type
class Txt:
    """A line of type rendered once (flat ink), with word boxes for per-word animation."""

    def __init__(self, text, font='display', px=120, fill='#5B174F', tracking=0.0, **kw):
        self.text = text
        self.font, self.px, self.fill, self.tracking, self.kw = font, px, fill, tracking, kw
        self.ts = T.render(text, 'flat', font=font, px=px, fill=fill, tracking=tracking, **kw)
        self.spr = self.ts.sprite
        self.w, self.h = self.ts.w, self.ts.h
        lay = self.ts.layout
        items = [g for g in lay.glyphs if g.ink is not None]
        words, cur = [], None
        k = 0
        for i, ch in enumerate(text):
            if ch == ' ':
                if cur:
                    words.append(cur)
                    cur = None
                continue
            g = next((g for g in items if g.i == i), None)
            if g is None:
                continue
            if cur is None:
                cur = [ch, g.ink[0], g.ink[2]]
            else:
                cur[0] += ch
                cur[1] = min(cur[1], g.ink[0])
                cur[2] = max(cur[2], g.ink[2])
        if cur:
            words.append(cur)
        self.words = [tuple(w) for w in words]
        self._wts = {}

    def anc(self, anchor=(0.5, 0.5)):
        return self.ts.sprite_anchor(anchor)

    def word_ts(self, i):
        if i not in self._wts:
            self._wts[i] = T.render(self.words[i][0], 'flat', font=self.font, px=self.px, fill=self.fill,
                                    tracking=self.tracking, **self.kw)
        return self._wts[i]

    def draw(self, cv, x, y, anchor=(0.5, 0.5), **kw):
        return self.ts.draw(cv, x, y, anchor=anchor, **kw)


def draw_clip(cv, spr, x, y, anchor, rect, opacity=1.0):
    """Draw spr (scale 1) with its anchor at (x, y), clipped to the canvas rect (x0, y0, x1, y1)."""
    sh, sw = spr.shape[:2]
    X0 = x - anchor[0] * sw
    Y0 = y - anchor[1] * sh
    cx0, cy0, cx1, cy1 = rect
    r0 = int(max(0, math.ceil(cy0 - Y0)))
    r1 = int(min(sh, math.floor(cy1 - Y0)))
    c0 = int(max(0, math.ceil(cx0 - X0)))
    c1 = int(min(sw, math.floor(cx1 - X0)))
    if r1 <= r0 or c1 <= c0:
        return None
    sub = spr[r0:r1, c0:c1]
    return K.draw(cv, sub, X0 + c0, Y0 + r0, anchor=(0.0, 0.0), opacity=opacity)


def draw_hmask(cv, spr, x, y, anchor, mx0, mx1, soft=6.0, opacity=1.0, invert=False, scale=1.0):
    """Draw spr with a horizontal soft mask: visible for canvas x in [mx0, mx1] (soft edges), or outside it with
    invert=True. Used for highlighter wipes and write-ons."""
    sh, sw = spr.shape[:2]
    X0 = x - anchor[0] * sw * scale
    xs = X0 + (np.arange(sw, dtype=np.float32) + 0.5) * scale
    m = np.clip((xs - mx0) / soft + 0.5, 0, 1) * np.clip((mx1 - xs) / soft + 0.5, 0, 1)
    if invert:
        m = 1.0 - m
    if m.max() <= 1e-4:
        return None
    nz = np.nonzero(m > 1e-4)[0]
    c0, c1 = int(nz[0]), int(nz[-1]) + 1
    sub = spr[:, c0:c1] * m[None, c0:c1, None]
    return K.draw(cv, sub, X0 + c0 * scale, y - anchor[1] * sh * scale, anchor=(0.0, 0.0), opacity=opacity,
                  scale=scale)


# ============================================================================================ strokes
def _arclen(pts):
    d = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1))
    return np.concatenate([[0.0], np.cumsum(d)])


def resample(pts, step=2.0):
    pts = np.asarray(pts, np.float64)
    s = _arclen(pts)
    n = max(2, int(s[-1] / step) + 1)
    ss = np.linspace(0, s[-1], n)
    return np.stack([np.interp(ss, s, pts[:, 0]), np.interp(ss, s, pts[:, 1])], 1)


def sub_path(pts, u0, u1):
    """Part of a polyline between arc-length fractions u0..u1 (interpolated ends)."""
    pts = np.asarray(pts, np.float64)
    s = _arclen(pts)
    L = s[-1]
    a, b = u0 * L, u1 * L
    if b <= a:
        return None
    keep = (s > a) & (s < b)
    pa = np.array([np.interp(a, s, pts[:, 0]), np.interp(a, s, pts[:, 1])])
    pb = np.array([np.interp(b, s, pts[:, 0]), np.interp(b, s, pts[:, 1])])
    return np.vstack([pa[None], pts[keep], pb[None]])


def path_point(pts, u):
    """(x, y, angle_deg) at arc fraction u along a polyline."""
    pts = np.asarray(pts, np.float64)
    s = _arclen(pts)
    a = float(np.clip(u, 0, 1)) * s[-1]
    x = np.interp(a, s, pts[:, 0])
    y = np.interp(a, s, pts[:, 1])
    e = 6.0
    x2 = np.interp(min(a + e, s[-1]), s, pts[:, 0]); y2 = np.interp(min(a + e, s[-1]), s, pts[:, 1])
    x1 = np.interp(max(a - e, 0), s, pts[:, 0]); y1 = np.interp(max(a - e, 0), s, pts[:, 1])
    return x, y, math.degrees(math.atan2(y2 - y1, x2 - x1))


def stroke_alpha(pts, width, u0=0.0, u1=1.0, dash=None, ss=4, taper=0.0):
    """Anti-aliased alpha of a (partial) polyline. dash=(on, off) px along the arc. Returns (alpha, x0, y0)."""
    p = sub_path(pts, u0, u1) if (u0 > 0 or u1 < 1) else np.asarray(pts, np.float64)
    if p is None or len(p) < 2:
        return None, 0, 0
    pad = width + 4
    x0 = int(math.floor(p[:, 0].min() - pad)); y0 = int(math.floor(p[:, 1].min() - pad))
    x1 = int(math.ceil(p[:, 0].max() + pad)); y1 = int(math.ceil(p[:, 1].max() + pad))
    img = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    q = ((p - [x0, y0]) * ss * 16).astype(np.int32)        # 4 fractional bits
    th = max(1, int(round(width * ss)))
    if dash is None:
        cv2.polylines(img, [q], False, 255, th, cv2.LINE_AA, shift=4)
    else:
        on, off = dash
        s = _arclen(p)
        per = on + off
        L = s[-1]
        st = 0.0
        # dashes are anchored to the full path (u0 offset) so they don't crawl as the path draws on
        base = u0 * _arclen(np.asarray(pts, np.float64))[-1]
        st = -(base % per)
        while st < L:
            a, b = max(st, 0.0), min(st + on, L)
            if b > a:
                seg = sub_path(p, a / L, b / L)
                if seg is not None and len(seg) >= 2:
                    cv2.polylines(img, [((seg - [x0, y0]) * ss * 16).astype(np.int32)], False, 255, th,
                                  cv2.LINE_AA, shift=4)
            st += per
    a = cv2.resize(img.astype(np.float32) / 255.0, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    return a, x0, y0


def paint(cv, alpha, x0, y0, rgb, opacity=1.0):
    """Composite a flat colour through an alpha at integer (x0, y0) (premultiplied over). Returns bbox."""
    if alpha is None:
        return None
    h, w = alpha.shape
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(cv.shape[1], x0 + w), min(cv.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return None
    a = alpha[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * np.float32(opacity)
    d = cv[Y0:Y1, X0:X1]
    d *= (1.0 - a)[..., None]
    d[..., :3] += a[..., None] * np.float32(rgb)
    d[..., 3] += a
    return X0, Y0, X1, Y1


def scribble_path(x0, x1, y, seed=3, amp=10.0, loops=0, slope=-4.0):
    """A hand-drawn underline: slightly wavy, rising, with an optional return stroke (double line)."""
    rng = np.random.default_rng(seed)
    n = 60
    xs = np.linspace(x0, x1, n)
    ph = rng.uniform(0, 6.28)
    ys = y + amp * 0.35 * np.sin(np.linspace(0, 2.6, n) + ph) + np.linspace(0, slope, n)
    pts = np.stack([xs, ys], 1)
    if loops:
        # swing back a little lower: the classic double underline flourish
        xs2 = np.linspace(x1 - 10, x0 + 0.18 * (x1 - x0), n)
        ys2 = y + amp * 0.9 + amp * 0.3 * np.sin(np.linspace(0, 2.2, n) + ph + 1.0) + np.linspace(slope * 0.4, 2, n)
        turn = np.array([[x1 + 8, y + slope + amp * 0.35], [x1 + 4, y + amp * 0.75]])
        pts = np.vstack([pts, turn, np.stack([xs2, ys2], 1)])
    return resample(pts, 3.0)


def chevron_pts(cx, cy, size, direction=-1):
    """'<' (direction -1) or '>' (+1) chevron polyline centred at (cx, cy); size = height."""
    hw = size * 0.36
    return np.array([[cx - direction * hw, cy - size / 2], [cx + direction * hw, cy],
                     [cx - direction * hw, cy + size / 2]], np.float64)


@functools.lru_cache(maxsize=8)
def chevron_sprite(size, stroke, direction, rgb):
    pts = chevron_pts(0, 0, size, direction)
    a, x0, y0 = stroke_alpha(pts, stroke, ss=4)
    spr = np.zeros(a.shape + (4,), np.float32)
    spr[..., :3] = a[..., None] * np.float32(rgb)
    spr[..., 3] = a
    spr.setflags(write=False)
    return spr, (-x0) / a.shape[1], (-y0) / a.shape[0]


@functools.lru_cache(maxsize=4)
def marker_band(w, h, seed=5):
    """Highlighter / brush swipe -> (alpha, shade): alpha (h, w) is a smooth band with gently uneven long edges
    and rounded / dry ends; shade (h, w) is the dry-brush streak density (0.86..1) for the colour (not the
    relief, so the deboss stays clean)."""
    rng = np.random.default_rng(seed)
    xs = np.arange(w, dtype=np.float32)

    def edge(scale, sig=26):
        n = rng.normal(0, 1, w + 160).astype(np.float32)
        n = cv2.GaussianBlur(n[None, :], (0, 0), sig)[0][80:80 + w]
        n2 = rng.normal(0, 1, w + 160).astype(np.float32)
        n2 = cv2.GaussianBlur(n2[None, :], (0, 0), 9.0)[0][80:80 + w]
        return scale * (n / (n.std() + 1e-6)) + 0.3 * scale * (n2 / (n2.std() + 1e-6))
    top = 0.08 * h + edge(0.022 * h)
    bot = 0.93 * h + edge(0.026 * h)
    yy = np.arange(h, dtype=np.float32)[:, None]
    fe = 1.8                                  # feathered edges (felt marker), also keeps the deboss soft
    a = np.clip((yy - top[None, :]) / fe + 0.5, 0, 1) * np.clip((bot[None, :] - yy) / fe + 0.5, 0, 1)
    r = 0.5 * h
    # rounded start, slanted dry end
    dl = np.clip(xs / r, 0, 1)
    a *= np.clip((np.sqrt(1 - (1 - dl) ** 2)[None, :] * r - np.abs(yy - h * 0.5) + r * (1 - 1)) / 3.0 + 0.5, 0, 1)
    endx = (w - 1) - (yy - h * 0.5) * 0.35 - 0.12 * h
    a *= np.clip((endx - xs[None, :]) / 6.0 + 0.5, 0, 1)
    st = rng.normal(0, 1, (h, 1)).astype(np.float32)
    st = cv2.GaussianBlur(st, (0, 0), 1.6)
    st = st / (st.std() + 1e-6)
    tail = np.clip((xs - 0.78 * w) / (0.22 * w), 0, 1)[None, :]
    shade = np.clip(0.95 + 0.05 * st - tail * (0.10 + 0.08 * np.clip(st, 0, None)), 0.80, 1.0)
    a = np.clip(a, 0, 1).astype(np.float32)
    shade = (shade * np.ones_like(a)).astype(np.float32)
    a.setflags(write=False)
    shade.setflags(write=False)
    return a, shade


# ============================================================================================ particles
@functools.lru_cache(maxsize=64)
def _soft_disc(r10, rgb=(1.0, 1.0, 1.0)):
    r = r10 / 10.0
    n = int(math.ceil(r * 2 + 6))
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    d = np.sqrt((xx + 0.5 - n / 2) ** 2 + (yy + 0.5 - n / 2) ** 2) / max(r, 0.5)
    a = np.clip(1 - d, 0, 1) ** 1.5
    spr = np.zeros((n, n, 4), np.float32)
    spr[..., 3] = a
    spr[..., :3] = a[..., None] * np.float32(rgb)
    spr.setflags(write=False)
    return spr


def puff(cv, t, t0, x, y, n=36, spread=170.0, seed=1, rgb=(1.0, 0.97, 0.92), size=(6, 22), up=-0.8,
         dur=1.3, opacity=0.85, gravity=60.0, ang=(-180.0, 0.0)):
    """Flour / paper-dust puff: particles burst from (x, y), decelerate (drag), drift and grow while fading."""
    dt = t - t0
    if dt < 0 or dt > dur:
        return
    rng = np.random.default_rng(seed)
    a = np.radians(rng.uniform(ang[0], ang[1], n))
    sp = spread * rng.uniform(0.35, 1.0, n)
    sz = rng.uniform(size[0], size[1], n)
    lag = rng.uniform(0, 0.08, n)
    for i in range(n):
        d = dt - lag[i]
        if d <= 0:
            continue
        f = (1 - math.exp(-d * 4.2)) / 4.2 * 4.2         # drag: approaches 1
        px = x + math.cos(a[i]) * sp[i] * f
        py = y + math.sin(a[i]) * sp[i] * f * (1 if math.sin(a[i]) > 0 else 1) + up * 40 * d + gravity * d * d * 0.2
        life = d / (dur - lag[i])
        op = opacity * (1 - life) ** 1.6 * min(1.0, d / 0.05)
        r = sz[i] * (0.6 + 1.2 * life)
        spr = _soft_disc(int(round(r * 10)) // 4 * 4 + 4, tuple(float(c) for c in rgb))
        sc = r / max(r, 0.5)
        K.draw(cv, spr, px, py, opacity=op * 0.9, scale=sc)
        if op <= 0:
            continue
    # tint: discs are white; colour via a final pass would cost more - flour is near white anyway


# ============================================================================================ foreground
@functools.lru_cache(maxsize=2)
def leaf_sprite(n=420, seed=2):
    """Procedural glossy leaf (pointing up), premultiplied linear: used heavily defocused as a near-lens foreground
    element, so only its silhouette, gradient and sheen matter. Anchor = stem base (0.5, ~0.97)."""
    ss = 2
    N = n * ss
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
    v = 1.0 - yy                           # 0 at the stem, 1 at the tip
    halfw = 0.30 * np.clip(np.sin(np.clip(v, 0, 1) * math.pi), 0, 1) ** 0.85 * (1 - 0.25 * v)
    u = (xx - 0.5)
    bend = 0.05 * np.sin(v * 2.6)
    d = np.abs(u - bend) - halfw
    a = np.clip(-d * N / 1.5 + 0.5, 0, 1) * (v > 0.03) * (v < 0.995)
    stem = (np.abs(u - bend) < 0.012) & (v > -0.0) & (v < 0.06)
    a = np.maximum(a, stem.astype(np.float32))
    side = np.clip((u - bend) / np.maximum(halfw, 1e-3), -1, 1)
    c_lo, c_hi = K.C['LEAF'], K.C['LEAF_HI']
    g = np.clip(0.35 + 0.5 * v + 0.25 * side, 0, 1)[..., None]
    col = c_lo[None, None, :] * (1 - g) + c_hi[None, None, :] * g
    col = col * (0.75 + 0.25 * (1 - np.abs(side)))[..., None]
    rib = np.exp(-((u - bend) / 0.008) ** 2) * (v > 0.04)
    col = col * (1 - 0.25 * rib[..., None])
    sheen = np.exp(-((side + 0.45) / 0.18) ** 2) * np.clip(v * 1.4, 0, 1)
    col = col + 0.18 * sheen[..., None]
    spr = np.dstack([col * a[..., None], a]).astype(np.float32)
    spr = cv2.resize(spr, (n, n), interpolation=cv2.INTER_AREA)
    spr.setflags(write=False)
    return spr


@functools.lru_cache(maxsize=2)
def leaf_shadow_sprite(n=420):
    spr = leaf_sprite(n)
    out = np.zeros_like(spr)
    out[..., 3] = spr[..., 3]
    out[..., :3] = spr[..., 3:4] * np.float32(SHADOW_RGB)
    out.setflags(write=False)
    return out


# ============================================================================================ book + pencil split
def _to_srgb8(img):
    """premultiplied linear RGBA -> straight sRGB uint8 RGB + alpha uint8."""
    a = img[..., 3:4]
    rgb = np.where(a > 1e-4, img[..., :3] / np.maximum(a, 1e-4), 0)
    s = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * np.power(np.clip(rgb, 0, None), 1 / 2.4) - 0.055)
    return (np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8), (np.clip(a[..., 0], 0, 1) * 255 + 0.5).astype(np.uint8)


def _from_srgb8(rgb8, a8):
    c = rgb8.astype(np.float32) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    a = a8.astype(np.float32)[..., None] / 255.0
    return np.concatenate([lin * a, a], 2).astype(np.float32)


@functools.lru_cache(maxsize=2)
def split_book(prop_id, yaw=0.0):
    """Split the book_pencil sprite at `yaw` into (book without pencil, pencil only, tip (x, y), eraser (x, y))
    in sprite px. The pencil is found from its yellow body (PCA axis) + the meta 'pencil_tip' feature; the page
    under it is inpainted. prop_id: the Prop instance (cached by identity)."""
    pr = _PROPS[prop_id]
    spr = pr.sprite(yaw)
    rgb8, a8 = _to_srgb8(spr)
    r, g, b = [rgb8[..., i].astype(np.int32) for i in range(3)]
    yellow = (r > 190) & (g > 150) & (b < 150) & (r - b > 70) & (a8 > 200)
    ys, xs = np.nonzero(yellow)
    if len(xs) < 30:
        return None
    try:
        idx = pr.a.yaw_to_index(yaw) if pr.a.mode == 'yaw' else None
        tip = np.array(pr.a.feature('pencil_tip', idx), np.float64)
    except Exception:
        tip = None
    P = np.stack([xs, ys], 1).astype(np.float64)
    c = P.mean(0)
    u, sv, vt = np.linalg.svd(P - c, full_matrices=False)
    d = vt[0]
    if tip is None:
        proj = (P - c) @ d
        tip = c + d * proj.min()
    if (c - tip) @ d < 0:
        d = -d
    proj = (P - tip) @ d
    L = proj.max()
    n = np.array([-d[1], d[0]])
    hw = np.percentile(np.abs((P - tip) @ n), 97) + 1.5
    eras = tip + d * (L + 2.2 * hw)                    # ferrule + eraser beyond the yellow body
    hh, ww = a8.shape
    gy, gx = np.mgrid[0:hh, 0:ww].astype(np.float64)
    G = np.stack([gx - tip[0], gy - tip[1]], -1)
    along = G @ d
    across = np.abs(G @ n)
    cone = np.clip((along + 2.0) / (2.6 * hw), 0, 1)
    width = hw * np.where(along < 2.6 * hw, np.maximum(cone, 0.18), 1.0) + 1.2
    m = (along > -4.0) & (along < L + 2.4 * hw) & (across < width)
    mask = np.clip((width - across) / 1.2, 0, 1) * m
    pen = spr * mask[..., None].astype(np.float32)
    # book without the pencil: inpaint colour + alpha under a dilated mask
    # inpaint region: the pencil + its halo + its cast shadow (falls on the +n side, lower right)
    sgn = G @ n
    sh = (along > -8.0) & (along < L + 2.6 * hw) & (sgn > -width - 3.0) & (sgn < width + 0.55 * hw + 9.0)
    k = max(3, int(round(hw * 0.5)) | 1)
    mk = cv2.dilate(((mask > 0.02) | sh).astype(np.uint8), np.ones((k, k), np.uint8)) * 255
    bgr = cv2.cvtColor(rgb8, cv2.COLOR_RGB2BGR)
    # transparent pixels carry black RGB: pre-fill them so the inpaint does not bleed grey into the page
    void = ((a8 < 40) & (mk == 0)).astype(np.uint8) * 255
    bgr = cv2.inpaint(bgr, cv2.dilate(void, np.ones((3, 3), np.uint8)), 3, cv2.INPAINT_TELEA)
    bgr = cv2.inpaint(bgr, mk, 9, cv2.INPAINT_TELEA)
    # alpha under the removed pencil: the convex hull of the rest of the book (the cover corner stays solid,
    # the void beyond it, where the eraser stuck out, becomes transparent)
    rest = ((a8 > 128) & (mk == 0)).astype(np.uint8)
    cnts, _ = cv2.findContours(rest, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    hull = np.zeros_like(a8)
    if cnts:
        cv2.fillConvexPoly(hull, cv2.convexHull(np.vstack(cnts)), 255)
    hull = cv2.GaussianBlur(hull, (0, 0), 0.8)
    a_in = np.where(mk > 0, np.minimum(hull, np.maximum(a8, hull)), a8).astype(np.uint8)
    book = _from_srgb8(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), a_in)
    for x in (book, pen):
        x.setflags(write=False)
    return book, pen.astype(np.float32), (float(tip[0]), float(tip[1])), (float(eras[0]), float(eras[1]))


_PROPS = {}


def register_prop(p):
    _PROPS[id(p)] = p
    return id(p)


# ============================================================================================ house windows / blocks
@functools.lru_cache(maxsize=2)
def house_states(prop_id, yaw=-10.0):
    """(off, on, glow) sprites of the house at `yaw`: 'on' is the render (glowing ORANGE panes + door glow),
    'off' has the emissive pixels dimmed to dusky glass, 'glow' is an additive bloom of the lit panes."""
    pr = _PROPS[prop_id]
    spr = pr.sprite(yaw)
    rgb8, a8 = _to_srgb8(spr)
    r, g, b = [rgb8[..., i].astype(np.int32) for i in range(3)]
    lit = (r > 225) & (g > 95) & (b < 175) & (r - b > 80) & (a8 > 180)
    m = cv2.GaussianBlur(lit.astype(np.float32), (0, 0), 1.0)
    m = np.clip(m * 1.6, 0, 1)
    off = spr.copy()
    dim = np.float32([0.10, 0.075, 0.11])
    off[..., :3] = spr[..., :3] * (1 - m[..., None]) + m[..., None] * dim * spr[..., 3:4]
    gl = np.zeros_like(spr)
    src = (m * spr[..., 3])[..., None] * np.float32([1.0, 0.62, 0.26])
    acc = 0.9 * cv2.GaussianBlur(src, (0, 0), 4.0) + 0.6 * cv2.GaussianBlur(src, (0, 0), 14.0)
    gl[..., :3] = acc
    for x in (off, gl):
        x.setflags(write=False)
    return off, spr, gl, float(m.sum())


@functools.lru_cache(maxsize=2)
def split_blocks(prop_id, yaw=0.0):
    """Split the 3-block stack sprite into [(sprite, ground anchor frac, height px)] bottom -> top, cutting at the
    two narrowest silhouette rows (the seams between the rounded blocks). None if it fails."""
    pr = _PROPS[prop_id]
    spr = pr.sprite(yaw)
    a = spr[..., 3]
    rows = np.nonzero(a.max(1) > 0.5)[0]
    if len(rows) < 30:
        return None
    y0, y1 = rows[0], rows[-1] + 1
    width = (a > 0.5).sum(1).astype(np.float32)
    width = np.convolve(width, np.ones(3) / 3, mode='same')
    hgt = y1 - y0
    cuts = []
    for frac in (1 / 3, 2 / 3):
        c = y0 + int(frac * hgt)
        lo, hi = c - int(0.09 * hgt), c + int(0.09 * hgt)
        seg = width[lo:hi]
        cuts.append(lo + int(np.argmin(seg)))
    bounds = [y0] + cuts + [y1]
    out = []
    for i in range(3):
        ya, yb = bounds[2 - i], bounds[3 - i]           # bottom block first
        sub = np.zeros_like(spr)
        sub[ya:yb] = spr[ya:yb]
        cols = np.nonzero(sub[..., 3].max(0) > 0.3)[0]
        cx = (cols[0] + cols[-1] + 1) / 2 if len(cols) else spr.shape[1] / 2
        sub = np.ascontiguousarray(sub)
        sub.setflags(write=False)
        out.append((sub, (cx / spr.shape[1], yb / spr.shape[0]), float(yb - ya)))
    return out
