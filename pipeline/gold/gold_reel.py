"""Black-and-gold motion graphics over the color-corrected presenter video.

Renders 1080x1920 frames: virtual 3D camera on the plate (presenter and background split by the
RVM matte for parallax), Blender gold elements, big type behind the presenter, reference-style
chapter cards, word-by-word Roman Urdu captions synced to the speech, transitions, light FX,
real motion blur (sub-frame accumulation) and filmic post.

  python3 gold_reel.py still 2.0,16.5,26.0        -> $GOLD_WORKDIR/stills/*.jpg
  python3 gold_reel.py range <f0> <f1> <out.mp4>  -> encoded chunk (no audio)
"""
import os, sys, math, json, glob, functools, subprocess
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
os.environ.setdefault('REEL_WORKDIR', os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace'))))
import engine as en
from engine import (W, H, CX, CY, FOCAL, Cam, clamp, lerp, prog, e_out_expo, e_in_expo, e_inout_expo, e_out_cubic,
                    e_in_cubic, e_inout_cubic, e_out_back, smooth, hexc, draw3d, draw, warp, composite, blur_sprite,
                    text_sprite, text_mask, radial_sprite, streak_sprite, rrect_alpha, sdf_fill, sdf_stroke, solid,
                    over_spr, pad, rotm, post)
import timeline as TL

S = os.environ['REEL_WORKDIR']
FPS = TL.FPS
GOLD = hexc('#E49F38')
WHITE = hexc('#F5F2EC')
INK = hexc('#0A0A0A')
GOLD3 = np.array(GOLD[:3], np.float32)

# ------------------------------------------------------------------ helpers

def shot_of(t):
    k = 0
    for i, c in enumerate(TL.CUT_T):
        if t >= c - 1e-6:
            k = i
    return k


def src_index(t):
    return int(clamp(round(t * FPS), 0, TL.NFRAMES - 1))


def env_val(keys, t):
    """Piecewise-smooth lookup in [(t, v), ...]."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t < t1:
            return lerp(v0, v1, smooth(prog(t, t0, t1)))
    return keys[-1][1]


def hold_frame(i, shot):
    """Source frame clamped inside a shot (used while two shots overlap in a transition)."""
    a = TL.CUTS[shot]
    b = TL.CUTS[shot + 1] - 1 if shot + 1 < len(TL.CUTS) else TL.NFRAMES - 1
    return int(clamp(i, a, b))

# ------------------------------------------------------------------ camera

def base_cam_values(t):
    keys = TL.CAM
    a = 0
    for i, k in enumerate(keys):
        if k[0] <= t + 1e-6:
            a = i
    ka = keys[a]
    if a + 1 < len(keys) and not keys[a + 1][7]:
        kb = keys[a + 1]
        u = e_inout_cubic(prog(t, ka[0], kb[0]))
        vals = [lerp(ka[j], kb[j], u) for j in range(1, 7)]
    else:
        vals = list(ka[1:7])
    zoom, x, y, roll, rx, ry = vals
    # handheld drift so no shot is ever static
    x += 6 * math.sin(t * 0.83) + 3 * math.sin(t * 2.1 + 1)
    y += 5 * math.sin(t * 0.67 + 2) + 2 * math.sin(t * 1.9)
    roll += 0.35 * math.sin(t * 0.5 + 0.3)
    # punches and shakes
    for tp, kick, amp in TL.PUNCH:
        if tp - 0.05 <= t < tp + 0.9:
            u = t - tp
            if u < 0:
                zoom *= 1 + kick * e_in_cubic((u + 0.05) / 0.05) * 0.4
            else:
                zoom *= 1 + kick * math.exp(-u * 7)
                d = math.exp(-u * 9) * amp
                x += d * math.sin(u * 71)
                y += d * math.cos(u * 59)
                roll += d * 0.06 * math.sin(u * 47)
    return dict(zoom=zoom, x=x, y=y, roll=roll, rx=rx, ry=ry)


def transition_state(t):
    """Returns (kind, k, phase) when t is inside a transition window around cut k."""
    for k, (kind, d) in TL.TRANSITIONS.items():
        tc = TL.CUT_T[k]
        pre, post_ = (0.24, 0.30) if kind != 'whip' else (0.22, 0.22)
        if tc - pre <= t < tc + post_:
            return kind, d, k, tc, pre, post_
    return None


WHIP_GAP = W * 1.22


def camera(t):
    """Final camera + list of plates to draw [(shot, x_offset)]."""
    v = base_cam_values(t)
    sh = shot_of(t)
    plates = [(sh, 0.0)]
    tr = transition_state(t)
    if tr:
        kind, d, k, tc, pre, post_ = tr
        if kind == 'zoom':
            if t < tc:
                v['zoom'] *= 1 + 1.7 * e_in_cubic(prog(t, tc - pre, tc))
            else:
                v['zoom'] *= 1 + 0.9 * (1 - e_out_cubic(prog(t, tc, tc + post_)))
        elif kind == 'spin':
            if t < tc:
                p = e_in_cubic(prog(t, tc - pre, tc))
                v['roll'] += 32 * d * p
                v['zoom'] *= 1 + 0.9 * p
            else:
                p = 1 - e_out_cubic(prog(t, tc, tc + post_))
                v['roll'] -= 32 * d * p
                v['zoom'] *= 1 + 0.9 * p
        elif kind == 'whip':
            u = e_inout_cubic(prog(t, tc - pre, tc + post_))
            va, vb = base_cam_values(tc - pre), base_cam_values(tc + post_)
            for key in ('zoom', 'y', 'roll', 'rx', 'ry'):
                v[key] = lerp(va[key], vb[key], u)
            v['x'] = lerp(va['x'], vb['x'], u)
            if t < tc:
                plates = [(k - 1, 0.0), (k, d * WHIP_GAP)]
                v['xw'] = d * WHIP_GAP * u
            else:
                plates = [(k - 1, -d * WHIP_GAP), (k, 0.0)]
                v['xw'] = d * WHIP_GAP * (u - 1)
            v['x'] += v['xw']
            v['roll'] += 3 * d * math.sin(u * math.pi)
    v.setdefault('xw', 0.0)
    cam = Cam(x=v['x'], y=v['y'], z=FOCAL * (1 - 1 / v['zoom']), rx=v['rx'], ry=v['ry'], rz=v['roll'])
    return cam, plates, v


def bg_camera(v):
    """The stage moves ~80% as much as the presenter: parallax without ever uncovering its edges."""
    zb = v['zoom'] ** 0.8
    return Cam(x=(v['x'] - v['xw']) * 0.8 + v['xw'], y=v['y'] * 0.8, z=FOCAL * (1 - 1 / zb),
               rx=v['rx'] * 0.8, ry=v['ry'] * 0.8, rz=v['roll'])


def person_depth(cam):
    return -cam.z  # camera-space depth of the presenter plane (z = 0)


def unproject(sx, sy, zq, cam):
    """Screen point + camera-space depth -> world point (inverse of engine.project_pts)."""
    f = cam.focal
    q = np.array([(sx - CX) * (f + zq) / f, (sy - CY) * (f + zq) / f, zq])
    R = rotm(cam.rx, cam.ry, cam.rz)
    return q @ R.T + np.array([CX + cam.x, CY + cam.y, cam.z])


def anchor_world(sx, sy, size, dz, t_anchor):
    cam, _, _ = camera(t_anchor)
    zq = person_depth(cam) + dz
    p = unproject(sx, sy, zq, cam)
    return p, size * (cam.focal + zq) / cam.focal

# ------------------------------------------------------------------ sources

class Source:
    def __init__(self):
        self.cache = {}
        self.k_dil = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

    def layers(self, i):
        if i in self.cache:
            return self.cache[i]
        f = cv2.imread(f'{S}/frames/{i:05d}.jpg')[..., ::-1].astype(np.float32) / 255.0
        Hs, Ws = f.shape[:2]
        m = cv2.imread(f'{S}/matte/{i:05d}.png', 0)
        m = cv2.resize(m, (Ws, Hs), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
        # soften the very bottom of the matte (feet / frame edge are unreliable)
        person = np.concatenate([f * m[..., None], m[..., None]], 2)
        # background: fill where she stands from the surrounding stage (normalized convolution)
        qw, qh = Ws // 4, Hs // 4
        mq = cv2.resize(m, (qw, qh), interpolation=cv2.INTER_AREA)
        md = cv2.dilate((mq > 0.03).astype(np.uint8), self.k_dil).astype(np.float32)
        md = cv2.GaussianBlur(md, (0, 0), 2.0)
        fq = cv2.resize(f, (qw, qh), interpolation=cv2.INTER_AREA)
        wgt = 1 - md
        num = cv2.GaussianBlur(fq * wgt[..., None], (0, 0), 22)
        den = cv2.GaussianBlur(wgt, (0, 0), 22)[..., None] + 1e-4
        fill = num / den
        hw, hh = Ws // 2, Hs // 2
        fh = cv2.resize(f, (hw, hh), interpolation=cv2.INTER_AREA)
        mdh = cv2.resize(md, (hw, hh))[..., None]
        bg = fh * (1 - mdh) + cv2.resize(fill, (hw, hh)) * mdh
        # push the teal stage toward black so the gold reads (presenter untouched)
        lum = (bg @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
        bg = (lum + (bg - lum) * 0.42) * 0.80
        P = int(hw * 0.18)
        bg = cv2.copyMakeBorder(bg, P, P, P, P, cv2.BORDER_REFLECT)
        if len(self.cache) > 3:
            self.cache.pop(next(iter(self.cache)))
        self.cache[i] = dict(person=person, bg=bg, pad=P / hw)
        return self.cache[i]


SRC = Source()
_bgblur = {}


def bg_sprite(i, sigma):
    key = (i, round(sigma * 2) / 2)
    if key not in _bgblur:
        bg = SRC.layers(i)['bg']
        s = key[1] * 0.67  # half-res image, sigma given at 1080 scale
        b = cv2.GaussianBlur(bg, (0, 0), s) if s > 0.3 else bg
        if len(_bgblur) > 3:
            _bgblur.pop(next(iter(_bgblur)))
        _bgblur[key] = np.concatenate([b, np.ones(b.shape[:2] + (1,), np.float32)], 2)
    return _bgblur[key]

# ------------------------------------------------------------------ sprites / assets

class Seq3:
    def __init__(self, name):
        self.files = sorted(glob.glob(f'{S}/assets3d/{name}/*.png'))
        x0 = y0 = 10 ** 9
        x1 = y1 = 0
        for fn in self.files[::max(1, len(self.files) // 12)] + self.files[-1:]:
            a = cv2.imread(fn, cv2.IMREAD_UNCHANGED)[..., 3]
            ys, xs = np.where(a > 6)
            if len(xs):
                x0, x1 = min(x0, xs.min()), max(x1, xs.max())
                y0, y1 = min(y0, ys.min()), max(y1, ys.max())
        m = 10
        self.bbox = (max(0, x0 - m), max(0, y0 - m), x1 + m, y1 + m) if self.files else (0, 0, 8, 8)

    def n(self):
        return len(self.files)

    @functools.lru_cache(maxsize=40)
    def frame(self, i):
        im = cv2.imread(self.files[i], cv2.IMREAD_UNCHANGED)
        x0, y0, x1, y1 = self.bbox
        im = im[y0:y1, x0:x1]
        a = im[..., 3:4].astype(np.float32) / 255
        rgb = im[..., [2, 1, 0]].astype(np.float32) / 255
        return np.concatenate([rgb * a, a], 2)


@functools.lru_cache(maxsize=None)
def seq(name):
    return Seq3(name)


@functools.lru_cache(maxsize=None)
def png(name):
    im = cv2.imread(f'{S}/assets2d/{name}.png', cv2.IMREAD_UNCHANGED)
    a = im[..., 3:4].astype(np.float32) / 255
    rgb = im[..., [2, 1, 0]].astype(np.float32) / 255
    return np.concatenate([rgb * a, a], 2)


@functools.lru_cache(maxsize=None)
def glow_spr():
    return radial_sprite(256, GOLD, power=2.2)


@functools.lru_cache(maxsize=None)
def dot_spr():
    return radial_sprite(64, GOLD, power=1.6, core=0.6)


@functools.lru_cache(maxsize=None)
def rays_spr():
    n = 900
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    dx, dy = xs - n / 2, ys - n / 2
    r = np.sqrt(dx * dx + dy * dy) / (n / 2)
    ang = np.arctan2(dy, dx)
    rng = np.random.default_rng(3)
    v = np.zeros_like(ang)
    for k, (fq, ph, amp) in enumerate([(9, rng.uniform(0, 6), 1.0), (14, rng.uniform(0, 6), 0.7),
                                       (23, rng.uniform(0, 6), 0.5), (37, rng.uniform(0, 6), 0.35)]):
        v += amp * np.maximum(np.cos(ang * fq + ph), 0) ** 6
    a = np.clip(v / 1.6, 0, 1) * np.clip(1 - r, 0, 1) ** 1.4 * np.clip(r * 5, 0, 1)
    c = GOLD3 * 0.85 + 0.15
    return np.concatenate([a[..., None] * c, a[..., None]], 2).astype(np.float32)


@functools.lru_cache(maxsize=None)
def streak():
    return streak_sprite(1400, 80, GOLD, (1.0, 0.92, 0.75))


@functools.lru_cache(maxsize=None)
def big_type(text, height):
    size = int(height * 1.32)
    a = text_mask(text, 'Anton-400', size, 0.01)
    hh = a.shape[0]
    g = np.linspace(1.08, 0.72, hh, dtype=np.float32)[:, None, None]
    rgb = np.clip(GOLD3[None, None] * g, 0, 1)
    spr = np.concatenate([rgb * a[..., None], a[..., None]], 2).astype(np.float32)
    return pad(spr, 4)


@functools.lru_cache(maxsize=None)
def neon_type(text, height):
    size = int(height * 1.32)
    a = text_mask(text, 'Anton-400', size, 0.02)
    a = np.pad(a, 40)
    k = np.ones((9, 9), np.uint8)
    edge = np.clip(cv2.dilate(a, k) - cv2.erode(a, k), 0, 1)
    core = solid(edge, (1.0, 0.86, 0.6, 1))
    halo = solid(cv2.GaussianBlur(edge, (0, 0), 14) * 1.6, GOLD)
    halo2 = solid(cv2.GaussianBlur(edge, (0, 0), 40) * 1.2, GOLD)
    inner = solid(a * 0.10, GOLD)
    return over_spr(over_spr(over_spr(halo2, halo), inner), core)


@functools.lru_cache(maxsize=None)
def gold_pill(text, size=34, outline=False):
    if outline:
        return en.pill(text, 'GeneralSans-700', size, pad_x=24, pad_y=14, fill=(0.02, 0.02, 0.02, 0.72),
                       border=GOLD, text_color=GOLD, radius=10, glow=(GOLD[0], GOLD[1], GOLD[2], 0.35))
    return en.pill(text, 'GeneralSans-700', size, pad_x=30, pad_y=18, fill=GOLD, border=None, text_color=INK,
                   radius=14, glow=(GOLD[0], GOLD[1], GOLD[2], 0.55))


@functools.lru_cache(maxsize=None)
def stage_bg():
    im = cv2.imread(f'{S}/assets2d/bg_dark_stage.jpg')[..., ::-1].astype(np.float32) / 255
    h, w = im.shape[:2]
    s = max(W * 1.25 / w, H * 1.25 / h)
    im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    lum = (im @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    im = lum * np.array([1.0, 0.86, 0.66], np.float32) * 0.9   # neutral-warm dark stage
    return np.concatenate([im, np.ones(im.shape[:2] + (1,), np.float32)], 2)


@functools.lru_cache(maxsize=None)
def card_mask(w, h, r):
    d = rrect_alpha(w, h, r, 0)
    return sdf_fill(d)


@functools.lru_cache(maxsize=None)
def card_border(w, h, r):
    P = 60
    d = rrect_alpha(w, h, r, P)
    line = solid(sdf_stroke(d, 4), GOLD)
    glow = solid(cv2.GaussianBlur(sdf_stroke(d, 6), (0, 0), 16) * 1.4, GOLD)
    shadow = solid(cv2.GaussianBlur(sdf_fill(d), (0, 0), 30) * 0.8, (0, 0, 0, 1))
    return over_spr(glow, line), shadow, P

# ------------------------------------------------------------------ elements

def _enter(e, t):
    """(scale, dy, blur, opacity, extra_rot) for the entry/exit animation."""
    u = t - e['t0']
    out = e['t1'] - t
    kind = e['enter']
    sc, dy, bl, op, rot = 1.0, 0.0, 0.0, 1.0, 0.0
    if kind == 'pop':
        p = clamp(u / 0.42)
        sc = max(e_out_back(p, 2.4), 0.0) if p < 1 else 1.0
        bl = (1 - p) * 10
        op = clamp(u / 0.12)
    elif kind == 'slam':
        p = clamp(u / 0.30)
        sc = lerp(2.6, 1.0, e_out_expo(p))
        bl = (1 - p) * 16
        op = clamp(u / 0.08)
    elif kind == 'fly':
        p = clamp(u / 0.5)
        sc = lerp(0.3, 1.0, e_out_expo(p))
        dy = (1 - e_out_expo(p)) * 260
        bl = (1 - p) * 14
        op = clamp(u / 0.12)
        rot = (1 - e_out_expo(p)) * -25
    elif kind == 'drop':
        p = clamp(u / 0.55)
        dy = -(1 - e_out_back(p, 1.6)) * 520 if p < 1 else 0
        bl = (1 - p) * 10
        op = clamp(u / 0.1)
    elif kind == 'rise':
        p = clamp(u / 0.6)
        dy = (1 - e_out_expo(p)) * 420
        sc = lerp(0.7, 1.0, e_out_expo(p))
        bl = (1 - p) * 12
        op = clamp(u / 0.15)
    if out < 0.28:
        q = 1 - clamp(out / 0.28)
        sc *= 1 - 0.55 * e_in_cubic(q)
        op *= 1 - q
        bl += q * 10
        dy -= q * 60
    return sc, dy, bl, op, rot


class Element:
    def __init__(self, e):
        self.e = e
        anchor = min(e['t0'] + 0.4, e['t1'] - 0.02)
        self.shot = shot_of(e['t0'] + 0.01)
        self.pos, self.size = anchor_world(e['sx'], e['sy'], e['size'], e['dz'], anchor)

    def active(self, t):
        return self.e['t0'] <= t < self.e['t1']

    def sprite(self, t):
        e = self.e
        if e['kind'] == 'png':
            return png(e['name'])
        s = seq(e['name'])
        n = s.n()
        if n == 0:
            return None
        fi = int((t - e['t0']) * e['fps'])
        fi = fi % n if e['play'] == 'loop' else min(fi, n - 1)
        return s.frame(fi)

    def draw(self, cv, t, cam, xoff):
        e = self.e
        sc, dy, bl, op, rot = _enter(e, t)
        if op <= 0.01 or sc <= 0.02:
            return
        spr = self.sprite(t)
        if spr is None:
            return
        h, w = spr.shape[:2]
        size = self.size * sc
        u = t - e['t0']
        fl = 8 * math.sin(u * 1.6 + e['sx'] * 0.01)
        x, y, z = self.pos[0] + xoff, self.pos[1] + dy + fl, self.pos[2]
        ry = e['sway'] * math.sin(u * 1.1 + e['sy'] * 0.01) if e['kind'] == 'png' else 0
        if e['spin']:
            ry += (u * 220 * e['spin']) % 360
            if 90 < ry % 360 < 270:
                ry += 180   # keep the face toward camera (flat sprite)
        rz = rot + 3 * math.sin(u * 0.9 + e['sy'])
        if e['glow'] > 0:
            g = glow_spr()
            draw3d(cv, g, x, y, z + 5, h=size * 1.9, cam=cam, opacity=e['glow'] * op, mode='add')
        if bl > 0.6:
            spr = blur_sprite(spr, bl * min(1.0, w / 400))
            h2, w2 = spr.shape[:2]
            size = size * h2 / h
        draw3d(cv, spr, x, y, z, h=size, rx=0, ry=ry, rz=rz, cam=cam, opacity=op)


def _ingot_rain(cv, t, cam, layer):
    if t > 2.4:
        return
    s = seq('ingot')
    n = s.n()
    if n == 0:
        return
    for t0, sx, size, dz, off, rot in TL.INGOT_RAIN:
        if (layer == 'back') != (dz > 0):
            continue
        u = t - t0
        if u < 0:
            continue
        sy = -260 + u * 900 + 0.5 * 2600 * u * u
        if sy > H + 400:
            continue
        cam0, _, _ = camera(min(t, 0.9))
        zq = person_depth(cam0) + dz
        p = unproject(sx, sy, zq, cam0)
        spr = s.frame((int(u * 26) + off) % n)
        sz = size * (cam0.focal + zq) / cam0.focal
        if dz < 0:
            spr = blur_sprite(spr, 3.0)       # foreground bars are out of focus
        draw3d(cv, spr, p[0], p[1], p[2], h=sz, rz=rot + u * 40, cam=cam, opacity=min(1, u / 0.08))

# ------------------------------------------------------------------ big type, pills, meters, rays, dust

def _big_types(cv, t, cam):
    for t_in, t_out, text, sy, height, dz in TL.BIG_TYPE:
        if not (t_in <= t < t_out):
            continue
        spr = big_type(text, height)
        u, out = t - t_in, t_out - t
        p = clamp(u / 0.35)
        sc = lerp(1.6, 1.0, e_out_expo(p))
        op = clamp(u / 0.06) * clamp(out / 0.2)
        bl = (1 - p) * 12 + (1 - clamp(out / 0.2)) * 8
        if bl > 0.6:
            spr = blur_sprite(spr, bl)
        pos, sz = _anchor_cached(('big', t_in), CX, sy, height, dz, t_in + 0.3)
        hh, ww = spr.shape[:2]
        sz = sz * hh / big_type(text, height).shape[0]
        draw3d(cv, spr, pos[0] + u * 14, pos[1], pos[2], h=sz * sc * 1.0, ry=-4 + u * 2, cam=cam, opacity=op)


_anchors = {}


def _anchor_cached(key, sx, sy, size, dz, ta):
    if key not in _anchors:
        _anchors[key] = anchor_world(sx, sy, size, dz, ta)
    return _anchors[key]


def _pills(cv, t, cam, layer):
    for t_in, t_out, text, sx, sy, ly in TL.PILLS:
        if ly != layer or not (t_in <= t < t_out):
            continue
        spr = gold_pill(text, 34, outline=True)
        u, out = t - t_in, t_out - t
        p = clamp(u / 0.35)
        op = clamp(u / 0.1) * clamp(out / 0.2)
        pos, sz = _anchor_cached(('pill', t_in, text), sx, sy, spr.shape[0], -60 if layer == 'front' else 60, t_in + 0.3)
        sz *= lerp(0.6, 1.0, e_out_back(p, 2.0))
        draw3d(cv, spr, pos[0], pos[1] + (1 - e_out_expo(p)) * 40, pos[2], h=sz, ry=6 * math.sin(u * 1.3),
               cam=cam, opacity=op)
        if text.startswith('STRUCTURAL') and u > 0.55:
            q = e_out_cubic(clamp((u - 0.55) / 0.3))
            line = solid(np.ones((10, max(2, int(spr.shape[1] * 0.86 * q))), np.float32), GOLD)
            draw3d(cv, line, pos[0] - spr.shape[1] * 0.43 * (1 - q) * sz / spr.shape[0], pos[1], pos[2] - 2,
                   h=10 * sz / spr.shape[0], cam=cam, opacity=op)


@functools.lru_cache(maxsize=None)
def meter_parts(w, label):
    P = 24
    d = rrect_alpha(w, 26, 13, P)
    track = over_spr(solid(sdf_fill(d), (0.03, 0.03, 0.03, 0.85)), solid(sdf_stroke(d, 2), GOLD))
    lab = text_sprite(label, 'GeneralSans-600', 30, WHITE, 0.08)
    return track, lab, P


def _meters(cv, t, cam):
    for t_in, t_out, v0, v1, sx, sy, label in TL.METERS:
        if not (t_in <= t < t_out):
            continue
        u, out = t - t_in, t_out - t
        op = clamp(u / 0.15) * clamp(out / 0.2)
        wbar = 340
        track, lab, P = meter_parts(wbar, label)
        cv_l = np.zeros((track.shape[0] + 60, track.shape[1], 4), np.float32)
        cv_l[60:] = track
        v = lerp(v0, v1, e_inout_cubic(clamp((u - 0.25) / 0.9)))
        fw = max(2, int((wbar - 8) * v))
        d = rrect_alpha(fw, 18, 9, 0)
        fill = solid(sdf_fill(d), GOLD)
        y0 = 60 + P + 4
        cv_l[y0:y0 + 18, P + 4:P + 4 + fw] = over_spr(cv_l[y0:y0 + 18, P + 4:P + 4 + fw], fill)
        lh, lw = lab.shape[:2]
        x0 = (cv_l.shape[1] - lw) // 2
        cv_l[8:8 + lh, x0:x0 + lw] = over_spr(cv_l[8:8 + lh, x0:x0 + lw], lab)
        pos, sz = _anchor_cached(('meter', t_in), sx, sy, cv_l.shape[0], 120, t_in + 0.3)
        draw3d(cv, cv_l, pos[0], pos[1], pos[2], h=sz, ry=-8, cam=cam, opacity=op)


def _rays(cv, t, cam, shot):
    for t_in, t_out, s in TL.RAYS:
        if t_in <= t < t_out:
            op = s * clamp((t - t_in) / 0.5) * clamp((t_out - t) / 0.5)
            hx = {0: 560, 5: 500, 6: 600, 7: 580}.get(shot, 540)
            pos, sz = _anchor_cached(('rays', t_in), hx, 420, 1500, 300, t_in + 0.6)
            spr = rays_spr()
            draw3d(cv, spr, pos[0], pos[1], pos[2], h=sz, rz=t * 6, cam=cam, opacity=op, mode='add')
            draw3d(cv, glow_spr(), pos[0], pos[1], pos[2] + 1, h=sz * 0.55, cam=cam, opacity=op * 0.8, mode='add')


_dust = None


def _dust_field():
    global _dust
    if _dust is None:
        rng = np.random.default_rng(11)
        n = 70
        _dust = dict(x=rng.uniform(-200, W + 200, n), y=rng.uniform(-200, H + 200, n), z=rng.uniform(-500, 900, n),
                     s=rng.uniform(6, 18, n), v=rng.uniform(10, 40, n), ph=rng.uniform(0, 6.28, n))
    return _dust


def _dust_draw(cv, t, cam, front):
    d = _dust_field()
    spr = dot_spr()
    for k in range(len(d['x'])):
        z = d['z'][k]
        if (z < 0) != front:
            continue
        y = (d['y'][k] - t * d['v'][k]) % (H + 400) - 200
        x = d['x'][k] + 20 * math.sin(t * 0.4 + d['ph'][k])
        fl = 0.55 + 0.45 * math.sin(t * 2.3 + d['ph'][k] * 3)
        size = d['s'][k] * (2.6 if z < 0 else 1.0)
        draw3d(cv, spr, x, y, z, h=size, cam=cam, opacity=0.5 * fl, mode='add')

# ------------------------------------------------------------------ chapter cards

def section_k(t):
    for s in TL.SECTIONS:
        if s['t_in'] <= t < s['t_out']:
            a = e_inout_expo(clamp((t - s['t_in']) / 0.5))
            b = e_inout_expo(clamp((s['t_out'] - t) / 0.5))
            return s, min(a, b), t - s['t_in']
    return None, 0.0, 0.0


def render_section(inner, t, s, k, u):
    cv = np.zeros((H, W, 3), np.float32)
    ocam = Cam(x=30 * math.sin(u * 0.6), y=10 * math.sin(u * 0.5), z=40 * u, ry=3 * math.sin(u * 0.7), rz=0)
    bg = stage_bg()
    draw3d(cv, bg, CX, CY, 300, h=bg.shape[0] * 1.2, cam=ocam, opacity=k)
    # giant neon outline word behind the card, scrolling sideways
    nt = neon_type(s['neon'], 760)
    draw3d(cv, nt, CX + 120 - u * 90, CY - 40, 220, h=nt.shape[0] * 1.15, cam=ocam, opacity=k * 0.95, mode='add')
    draw3d(cv, glow_spr(), CX, CY + 80, 250, h=1700, cam=ocam, opacity=0.35 * k, mode='add')
    # the live video becomes a floating rounded card
    sc = lerp(1.0, 0.64, k)
    r = int(round(lerp(0, 56, k) / max(sc, 0.3) / 8)) * 8
    a = card_mask(W, H, r) if r > 0 else np.ones((H, W), np.float32)
    card = np.concatenate([inner * a[..., None], a[..., None]], 2)
    ry = lerp(0, -13, k) + 3 * math.sin(u * 1.2) * k
    rx = lerp(0, 5, k)
    cy = CY + lerp(0, -40, k)
    bspr, shadow, P = card_border(W, H, 56)
    if k > 0.02:
        draw3d(cv, shadow, CX + 20, cy + 40, 30, w=(W + 2 * P) * sc, h=(H + 2 * P) * sc, rx=rx, ry=ry, rz=lerp(0, -1.5, k),
               cam=ocam, opacity=k)
    q = draw3d(cv, card, CX, cy, 0, w=W * sc, h=H * sc, rx=rx, ry=ry, rz=lerp(0, -1.5, k), cam=ocam)
    if k > 0.02:
        draw3d(cv, bspr, CX, cy, -1, w=(W + 2 * P) * sc, h=(H + 2 * P) * sc, rx=rx, ry=ry, rz=lerp(0, -1.5, k),
               cam=ocam, opacity=k)
        # tags around the card
        spots = [(-0.52, -0.30), (0.50, -0.05), (-0.48, 0.30)]
        for j, (tag, (fx, fy)) in enumerate(zip(s['tags'], spots)):
            tp = clamp((u - 0.45 - j * 0.12) / 0.3)
            if tp <= 0:
                continue
            spr = gold_pill(tag, 30, outline=True)
            draw3d(cv, spr, CX + fx * W * sc * 1.02, cy + fy * H * sc, -40, h=spr.shape[0] * lerp(0.4, 1, e_out_back(tp, 2)),
                   ry=ry * 0.6, cam=ocam, opacity=tp * k)
        # numbered chapter pill
        tp = clamp((u - 0.35) / 0.35)
        if tp > 0:
            txt = f"{s['num']}  ·  {s['title']}"
            n = max(1, int(round(len(txt) * e_out_cubic(clamp((u - 0.35) / 0.55)))))
            spr = gold_pill(txt[:n], 46)
            draw3d(cv, spr, CX, cy - H * sc * 0.5 - 6, -60, h=spr.shape[0] * lerp(0.5, 1, e_out_back(tp, 2)),
                   ry=ry * 0.5, cam=ocam, opacity=tp * k)
            nb = gold_pill(s['num'], 64)
            draw3d(cv, nb, CX, cy - H * sc * 0.02, -50, h=nb.shape[0] * lerp(0.3, 1, e_out_back(clamp((u - 0.25) / 0.3), 2.5)),
                   cam=ocam, opacity=clamp((u - 0.25) / 0.15) * clamp((0.9 - u) / 0.25) * k)
    return cv

# ------------------------------------------------------------------ captions

def _parse_captions():
    words = json.load(open(f'{S}/work/words_large-v3_en.json'))
    phrases = []
    for line in TL.CAPTIONS.strip().splitlines():
        rows = []
        for row in line.split(' / '):
            r = []
            for tok in row.split():
                gold = tok.startswith('*')
                tok = tok.lstrip('*')
                if '@' in tok:
                    txt, ts = tok.rsplit('@', 1)
                    t0 = float(ts)
                else:
                    txt, idx = tok.rsplit(':', 1)
                    t0 = words[int(idx)]['s']
                r.append(dict(text=txt, t=t0, gold=gold))
            rows.append(r)
        phrases.append(rows)
    out = []
    for i, rows in enumerate(phrases):
        ws = [w for r in rows for w in r]
        t_on = ws[0]['t'] - 0.04
        last = ws[-1]['t']
        nxt = phrases[i + 1][0][0]['t'] - 0.04 if i + 1 < len(phrases) else last + 1.2
        t_off = min(nxt, last + 0.9)
        out.append(dict(rows=rows, t_on=t_on, t_off=t_off, i=i))
    return out


PHRASES = None


@functools.lru_cache(maxsize=None)
def word_spr(text, gold):
    if gold:
        return text_sprite(text, 'GeneralSans-700', 104, GOLD, -0.01)
    return text_sprite(text, 'GeneralSans-600', 70, WHITE, -0.005)


@functools.lru_cache(maxsize=None)
def word_shadow(text, gold):
    s = word_spr(text, gold)
    a = pad(s, 24)[..., 3]
    return solid(cv2.GaussianBlur(a, (0, 0), 10) * 0.75, (0, 0, 0, 1))


@functools.lru_cache(maxsize=None)
def word_glow(text):
    s = pad(word_spr(text, True), 30)
    return solid(cv2.GaussianBlur(s[..., 3], (0, 0), 14) * 0.9, GOLD)


@functools.lru_cache(maxsize=None)
def phrase_layout(i):
    ph = PHRASES[i]
    lines = []
    for row in ph['rows']:
        sprs = [word_spr(w['text'], w['gold']) for w in row]
        gap = 14
        wid = sum(s.shape[1] for s in sprs) + gap * (len(sprs) - 1)
        hgt = max(s.shape[0] for s in sprs)
        lines.append((row, sprs, wid, hgt))
    total = sum(l[3] * 0.88 for l in lines)
    y = -total / 2
    place = []
    for row, sprs, wid, hgt in lines:
        x = -wid / 2
        for w, s in zip(row, sprs):
            place.append((w, s, x + s.shape[1] / 2, y + hgt * 0.88 / 2 + (hgt - s.shape[0]) * 0.32))
            x += s.shape[1] + 14
        y += hgt * 0.88
    return place


def draw_captions(cv, t, v, shot):
    global PHRASES
    if PHRASES is None:
        PHRASES = _parse_captions()
    for ph in PHRASES:
        if not (ph['t_on'] <= t < ph['t_off'] + 0.2):
            continue
        out = clamp((t - ph['t_off']) / 0.2)
        base_y = TL.CAPTION_Y[shot_of(ph['t_on'] + 0.05)]
        # captions ride along with the camera (partially) so they feel attached to the shot
        z = v['zoom'] ** 0.35
        ax = CX - v['x'] * 0.25
        ay = base_y - v['y'] * 0.18 - out * 40
        rot = v['roll'] * 0.5 + (2.0 if ph['i'] % 2 else -2.0)
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for w, s, ox, oy in phrase_layout(ph['i']):
            u = t - w['t'] + 0.03
            if u < 0:
                continue
            p = clamp(u / 0.16)
            sc = lerp(0.55, 1.0, e_out_back(p, 2.2)) * z
            op = clamp(u / 0.06) * (1 - out)
            px = ax + (ox * cr - oy * sr) * z
            py = ay + (ox * sr + oy * cr) * z + (1 - e_out_cubic(p)) * 26
            bl = (1 - p) * 6 + out * 8
            spr = s if bl < 0.6 else blur_sprite(s, bl)
            draw(cv, word_shadow(w['text'], w['gold']), px, py + 7, sc, rot, op * 0.85)
            if w['gold']:
                pulse = 0.55 + 0.45 * math.exp(-u * 3)
                draw(cv, word_glow(w['text']), px, py, sc, rot, op * 0.5 * pulse, mode='add')
            draw(cv, spr, px, py, sc * spr.shape[0] / s.shape[0], rot, op)

# ------------------------------------------------------------------ frame

ELEMS = None


def elements():
    global ELEMS
    if ELEMS is None:
        ELEMS = [Element(e) for e in TL.ELEMENTS]
    return ELEMS


def dof_at(t):
    return env_val(TL.DOF, t)


def bg_dim_at(t):
    return env_val(TL.BG_DIM, t)


def render_inner(t, i):
    cam, plates, v = camera(t)
    cv = np.zeros((H, W, 3), np.float32)
    sigma = dof_at(t)
    dim = bg_dim_at(t)
    bcam = bg_camera(v)
    for sh, xoff in plates:
        fi = hold_frame(i, sh)
        L = SRC.layers(fi)
        bg = bg_sprite(fi, sigma)
        draw3d(cv, bg, CX + xoff, CY, 0, w=W * (1 + 2 * L['pad']), h=H + 2 * L['pad'] * W, cam=bcam, opacity=dim)
    shot = shot_of(t)
    _rays(cv, t, cam, shot)
    _dust_draw(cv, t, cam, front=False)
    _big_types(cv, t, cam)
    _ingot_rain(cv, t, cam, 'back')
    for el in elements():
        if el.e['layer'] == 'back' and el.active(t):
            xoff = dict(plates).get(el.shot, None)
            if xoff is not None:
                el.draw(cv, t, cam, xoff)
    _pills(cv, t, cam, 'back')
    _meters(cv, t, cam)
    for sh, xoff in plates:
        fi = hold_frame(i, sh)
        person = SRC.layers(fi)['person']
        draw3d(cv, person, CX + xoff, CY, 0, w=W, h=H, cam=cam)
    for el in elements():
        if el.e['layer'] == 'front' and el.active(t):
            xoff = dict(plates).get(el.shot, None)
            if xoff is not None:
                el.draw(cv, t, cam, xoff)
    _pills(cv, t, cam, 'front')
    _ingot_rain(cv, t, cam, 'front')
    _dust_draw(cv, t, cam, front=True)
    return cv, cam, v, plates


def nsub_at(t):
    if transition_state(t):
        return 9
    s, k, u = section_k(t)
    if s is not None and 0 < k < 1:
        return 7
    for e in TL.ELEMENTS:
        if e['t0'] - 0.02 <= t < e['t0'] + 0.5 or e['t1'] - 0.3 <= t < e['t1']:
            return 5
    for tp, kick, amp in TL.PUNCH:
        if tp <= t < tp + 0.35:
            return 5
    for k in TL.CAM:
        if k[7] and abs(t - k[0]) < 0.02:
            return 1
    return 3


def render_frame(fi):
    t = fi / FPS
    en._mips.clear()
    n = nsub_at(t)
    shutter = 0.55 / FPS
    acc = np.zeros((H, W, 3), np.float32)
    for j in range(n):
        ts = t + ((j + 0.5) / n - 0.5) * shutter if n > 1 else t
        # never sample across a hard cut (the plate would jump)
        k_now = shot_of(t)
        if shot_of(ts) != k_now and not transition_state(t):
            ts = t
        cv, cam, v, plates = render_inner(ts, fi)
        s, k, u = section_k(ts)
        if s is not None and k > 0.001:
            cv = render_section(cv, ts, s, k, u)
        draw_captions(cv, ts, v, shot_of(ts))
        acc += cv
    cv = acc / n
    # transition flash + light streak
    flash, ca = 0.0, 0.0
    tr = transition_state(t)
    if tr:
        kind, d, k, tc, pre, post_ = tr
        x = abs(t - tc)
        flash = 0.35 * math.exp(-x * 14) if kind != 'whip' else 0.18 * math.exp(-x * 16)
        ca = 6 * math.exp(-x * 10)
        sp = streak()
        draw(cv, sp, CX, CY + (-1) ** k * 420, 1.6 * (1 - x * 2), 0, 0.8 * math.exp(-x * 9), 'add')
    s, k, u = section_k(t)
    if s is not None and 0.0 < u < 0.25:
        flash = max(flash, 0.22 * (1 - u / 0.25))
    for tp, kick, amp in TL.PUNCH:
        if tp <= t < tp + 0.25 and amp >= 12:
            ca = max(ca, 5 * (1 - (t - tp) / 0.25))
    fade = clamp((t - 78.9) / 0.5)
    return post(cv, fi, bloom=0.55, grain=0.018, ca=ca, flash=flash, flash_color=(1.0, 0.75, 0.42), fade=fade)


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def main():
    cmd = sys.argv[1]
    if cmd == 'still':
        os.makedirs(S + '/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            fi = int(round(float(ts) * FPS))
            img = render_frame(fi)
            cv2.imwrite(f'{S}/stills/s_{float(ts):06.2f}.jpg', to_u8(img)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
            print('still', ts, flush=True)
    elif cmd == 'range':
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                              '-s', f'{W}x{H}', '-r', '30000/1001', '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                              '-crf', '12', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for fi in range(f0, f1):
            p.stdin.write(to_u8(render_frame(fi)).tobytes())
            if fi % 20 == 0:
                print('frame', fi, flush=True)
        p.stdin.close()
        p.wait()


if __name__ == '__main__':
    main()
