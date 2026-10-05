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
                    e_in_cubic, e_inout_cubic, e_out_back, smooth, hexc, draw3d, blur_sprite,
                    text_sprite, text_mask, radial_sprite, streak_sprite, rrect_alpha, sdf_fill, sdf_stroke, solid,
                    over_spr, pad, rotm)
import timeline as TL

S = os.environ['REEL_WORKDIR']
FPS = TL.FPS
# Layout lives in a 1080x1920 design space; frames are rendered K times larger (K=2 -> native 4K 2160x3840).
K = float(os.environ.get('OUT_K', '2'))
OW, OH = int(round(W * K)), int(round(H * K))
FRAMES_DIR = os.environ.get('FRAMES_DIR', 'frames4k' if K > 1.5 else 'frames')
_warp_design = en.warp


def _warp_out(canvas, spr, quad, opacity=1.0, mode='over'):
    return _warp_design(canvas, spr, np.asarray(quad, np.float64) * K, opacity, mode)


en.warp = _warp_out   # every engine draw (draw3d etc.) now maps design px -> output px
_composite3 = en.composite
DIRTY = []


def _composite_any(canvas, spr, x0, y0, opacity=1.0, mode='over'):
    """engine.composite plus support for premultiplied RGBA layer canvases (records the touched rect)."""
    if canvas.shape[2] == 3:
        return _composite3(canvas, spr, x0, y0, opacity, mode)
    h, w = spr.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x0 + w), min(canvas.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0 or opacity <= 0.001:
        return
    sp = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    dst = canvas[Y0:Y1, X0:X1]
    if mode == 'add':
        dst[..., :3] += sp[..., :3] * opacity
    else:
        dst *= 1 - sp[..., 3:4] * opacity
        dst += sp * opacity
    DIRTY.append((X0, Y0, X1, Y1))


en.composite = _composite_any


def draw(cv, spr, cx, cy, scale=1.0, rot=0.0, opacity=1.0, mode='over'):
    """2D draw of an output-resolution sprite at a design-space position."""
    h, w = spr.shape[:2]
    en.warp(cv, spr, en.quad_2d(cx, cy, w / K, h / K, scale, rot), opacity, mode)
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

def _key_cam_values(t):
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


# Fast-paced edit layer (reference style): on every new caption phrase the camera snaps to a new
# angle - a 0.3 s expo move (motion-blurred), every third one a hard angle cut.
SNAP_POOL = [(1.06, -24, -30, 1.8, -3.0), (1.00, 20, -8, -1.4, 3.0), (1.10, 0, -50, 0.0, 0.0),
             (1.02, -16, -12, -2.2, -2.5), (1.07, 26, -26, 1.2, 3.5), (0.99, -6, -6, 0.6, -3.5)]
SNAP_NEUTRAL = (1.0, 0.0, 0.0, 0.0, 0.0)
SNAP_MOVE = 0.30
_snaps = None


def snap_events():
    global _snaps
    if _snaps is None:
        ev, last = [], -9.0
        for p in phrases():
            t = p['t_on'] + 0.02
            if any(abs(t - c) < 0.5 for c in TL.CUT_T[1:]):
                continue
            if any(sc['t_in'] - 0.3 <= t <= sc['t_out'] + 0.3 for sc in TL.SECTIONS):
                continue
            if t - last < 0.9:
                continue
            ev.append(t)
            last = t
        _snaps = ev
    return _snaps


def snap_values(t):
    """(zoom mult, dx, dy, droll, dry), moving-flag."""
    ev = snap_events()
    start = TL.CUT_T[shot_of(t)]
    idx = [k for k, te in enumerate(ev) if start <= te <= t]
    if not idx:
        return SNAP_NEUTRAL, False
    k = idx[-1]
    cur = SNAP_POOL[k % len(SNAP_POOL)]
    prev = SNAP_POOL[(k - 1) % len(SNAP_POOL)] if len(idx) > 1 else SNAP_NEUTRAL
    hard = k % 3 == 2
    u = 1.0 if hard else e_inout_expo(prog(t, ev[k], ev[k] + SNAP_MOVE))
    return tuple(lerp(a, b, u) for a, b in zip(prev, cur)), (not hard and t - ev[k] < SNAP_MOVE)


SIDE_LOCKED = {0, 2, 3, 4, 5, 6}   # shots where her body touches / crosses the frame sides
COVER_ALL = False                  # True when the plate is one layer: keep every frame edge covered


def _cover(v, shot):
    """Raise zoom until the plate edges (where her body is cut by the original frame) stay off screen."""
    z = max(v['zoom'], 1.0)
    th = math.radians(v['roll'])
    c, s_ = abs(math.cos(th)), abs(math.sin(th))
    m = 1.012 + abs(v['ry']) * 0.003
    for _ in range(80):
        hw, hh = 540 / z, 960 / z
        ex, ey = (hw * c + hh * s_) * m, (hw * s_ + hh * c) * m
        cx, cy = 540 + v['x'], 960 + v['y']
        ok = cy + ey <= 1920 and (not COVER_ALL or cy - ey >= 0)
        if shot in SIDE_LOCKED or COVER_ALL:
            ok = ok and cx - ex >= 0 and cx + ex <= 1080
        if ok:
            break
        z *= 1.006
    v['zoom'] = z
    return v


def base_cam_values(t):
    v = _key_cam_values(t)
    (sz, sx, sy, sr, sry), _ = snap_values(t)
    v['zoom'] *= sz
    v['x'] += sx
    v['y'] += sy
    v['roll'] += sr
    v['ry'] += sry
    return _cover(v, shot_of(t))


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


    def layers(self, i):
        if i in self.cache:
            return self.cache[i]
        f = cv2.imread(f'{S}/{FRAMES_DIR}/{i:05d}.jpg')[..., ::-1].astype(np.float32) / 255.0
        Hs, Ws = f.shape[:2]
        rel = Ws / 1440
        m = cv2.imread(f'{S}/matte/{i:05d}.png', 0)
        m = cv2.resize(m, (Ws, Hs), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
        person = np.concatenate([grade_person(f, m, rel) * m[..., None], m[..., None]], 2)
        # background: fill where she stands from the surrounding stage (normalized convolution)
        qw, qh = Ws // 4, Hs // 4
        mq = cv2.resize(m, (qw, qh), interpolation=cv2.INTER_AREA)
        kd = int(9 * rel) | 1
        md = cv2.dilate((mq > 0.03).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kd, kd))).astype(np.float32)
        md = cv2.GaussianBlur(md, (0, 0), 2.0)
        fq = cv2.resize(f, (qw, qh), interpolation=cv2.INTER_AREA)
        wgt = 1 - md
        num = cv2.GaussianBlur(fq * wgt[..., None], (0, 0), 22 * rel)
        den = cv2.GaussianBlur(wgt, (0, 0), 22 * rel)[..., None] + 1e-4
        fill = num / den
        hw, hh = Ws // 2, Hs // 2
        fh = cv2.resize(f, (hw, hh), interpolation=cv2.INTER_AREA)
        mdh = cv2.resize(md, (hw, hh))[..., None]
        bg = fh * (1 - mdh) + cv2.resize(fill, (hw, hh)) * mdh
        bg = grade_stage(bg)
        P = int(hw * 0.18)
        bg = cv2.copyMakeBorder(bg, P, P, P, P, cv2.BORDER_REFLECT)
        if len(self.cache) > 2:
            self.cache.pop(next(iter(self.cache)))
        self.cache[i] = dict(person=person, bg=bg, pad=P / hw)
        return self.cache[i]


LUMA = np.array([0.299, 0.587, 0.114], np.float32)


def _grade_luts():
    """Per-channel tone curves: deep blacks, filmic S-curve, warm-gold highlights / neutral shadows."""
    x = np.linspace(0, 1, 1024, dtype=np.float32)
    y = np.clip((x - 0.012) / 0.988, 0, 1)
    y = y + 0.18 * (y * y * (3 - 2 * y) - y)
    hi = np.clip((y - 0.45) / 0.5, 0, 1) ** 1.5
    return [np.clip(y + hi * d, 0, 1).astype(np.float32) for d in (0.040, 0.016, -0.030)]


GRADE_LUT = _grade_luts()


def grade_person(f, m, rel):
    """Cinematic grade + detail pass for the presenter: crisper detail, filmic contrast, warm-gold
    highlights, neutral shadows, natural skin, and the teal spill from the keyed stage removed."""
    Hs, Ws = f.shape[:2]
    y = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
    # detail: fine unsharp mask (thresholded so grain is left alone) + clarity from a low-res blur
    fine = y - cv2.GaussianBlur(y, (0, 0), 1.1 * rel)
    fine = np.sign(fine) * np.maximum(np.abs(fine) - 0.004, 0)
    sm = cv2.resize(y, (Ws // 8, Hs // 8), interpolation=cv2.INTER_AREA)
    clar = y - cv2.resize(cv2.GaussianBlur(sm, (0, 0), 14 * rel / 8), (Ws, Hs), interpolation=cv2.INTER_LINEAR)
    f = f + (0.45 * fine + 0.10 * clar)[..., None]
    # teal spill suppression (cyan where g ~ b > r), weighted toward edges/hair; computed at quarter res
    q = cv2.resize(f, (Ws // 4, Hs // 4), interpolation=cv2.INTER_AREA)
    r, g, b = q[..., 0], q[..., 1], q[..., 2]
    cyan = np.clip(np.minimum(g, b) - r, 0, None) * np.clip(1 - np.abs(g - b) * 6, 0, 1)
    mq = cv2.resize(m, (Ws // 4, Hs // 4), interpolation=cv2.INTER_AREA)
    spill = cv2.resize(np.clip(cyan * 5, 0, 1) * (0.55 + 0.45 * (1 - mq)) * 0.8, (Ws, Hs))
    if spill.max() > 0.01:
        yy = cv2.cvtColor(np.clip(f, 0, 1), cv2.COLOR_RGB2GRAY)[..., None]
        f += (yy - f) * spill[..., None]
    # tone curves + split tone via 1D LUTs
    idx = np.clip(f * 1023, 0, 1023).astype(np.int16)
    out = np.empty_like(f)
    for c in range(3):
        out[..., c] = GRADE_LUT[c][idx[..., c]]
    return out


def grade_stage(bg):
    """Push the teal studio toward a deep neutral black, warm where the floor catches light."""
    y = (bg @ LUMA)[..., None]
    bg = y * 0.80 + (bg - y) * 0.28
    warm = np.clip((y - 0.12) / 0.35, 0, 1)
    bg = bg * (1 + warm * np.array([0.10, 0.03, -0.08], np.float32))
    return np.clip(bg * 0.92 - 0.004, 0, 1)


SRC = Source()
_bgblur = {}


def bg_sprite(i, sigma):
    key = (i, round(sigma * 2) / 2)
    if key not in _bgblur:
        bg = SRC.layers(i)['bg']
        s = key[1] * bg.shape[1] / (1 + 2 * SRC.layers(i)['pad']) / 1080  # sigma given at 1080 design scale
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


PALE_GOLD = np.array([1.0, 0.90, 0.70], np.float32)


def emboss(a, scale, kind='gold'):
    """Bevel & emboss for a text/shape alpha mask -> premultiplied RGBA.
    gold: metallic #E49F38 with pale-gold top-left highlights, deeper shade below and a top sheen,
    so it reads as gold leaf rather than flat orange. white: soft bevel with a cool-grey falloff."""
    h = a.shape[0]
    hgt = cv2.GaussianBlur(a, (0, 0), 1.8 * scale)
    gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3)
    shade = np.clip((-0.55 * gx - 0.83 * gy) * 2.6 * scale, -1, 1)[..., None]   # light from top-left
    ys = np.where(a.max(1) > 0.5)[0]
    y0, y1 = (ys.min(), ys.max()) if len(ys) else (0, h)
    v = np.clip((np.arange(h, dtype=np.float32) - y0) / max(y1 - y0, 1), 0, 1)[:, None, None]
    if kind == 'gold':
        base = GOLD3 * (1.10 - 0.32 * v)                       # lighter top, deeper bottom
        sheen = np.exp(-((v - 0.30) / 0.10) ** 2) * 0.22       # soft horizontal sheen band
        base = base + sheen * (PALE_GOLD - base)
        hi, lo = PALE_GOLD, GOLD3 * 0.38
    else:
        base = np.array([0.97, 0.96, 0.93], np.float32) * (1.0 - 0.12 * v)
        hi, lo = np.array([1.0, 1.0, 1.0], np.float32), np.array([0.62, 0.62, 0.66], np.float32)
    up, dn = np.clip(shade, 0, 1), np.clip(-shade, 0, 1)
    rgb = base + up * (hi - base) * 0.85 + dn * (lo - base) * 0.75
    rgb = np.clip(rgb, 0, 1)
    return np.concatenate([rgb * a[..., None], a[..., None]], 2).astype(np.float32)


def _shift(a, dx, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR)


def deep_style(a, kind='gold', ext=8.0, glow=1.0, bevel=1.2, sig=(14, 40)):
    """Cinematic 3D type from an alpha mask (needs ~ (ext + 45) * K px of padding):
    deep layered glow, contact shadow, an extruded side (down-right) shaded dark->mid, and an
    embossed bevel face on top. ext / bevel are in design px."""
    gold = kind == 'gold'
    n = max(2, int(round(ext * K)))
    out = np.zeros(a.shape + (4,), np.float32)
    if glow > 0:
        g = cv2.GaussianBlur(a, (0, 0), sig[0] * K) * 0.55 + cv2.GaussianBlur(a, (0, 0), sig[1] * K) * 0.65
        gcol = GOLD if gold else (1.0, 0.84, 0.58, 1)
        out = over_spr(out, solid(np.clip(g, 0, 1) * glow * (1.0 if gold else 0.35), gcol))
    sh = cv2.GaussianBlur(_shift(a, n * 0.55, n * 1.5), (0, 0), 5 * K)
    out = over_spr(out, solid(sh * 0.85, (0, 0, 0, 1)))
    near = GOLD3 * 0.66 if gold else np.array([0.58, 0.57, 0.55], np.float32)
    far = GOLD3 * 0.20 if gold else np.array([0.16, 0.16, 0.17], np.float32)
    for i in range(n, 0, -1):
        c = far + (near - far) * (1 - i / n) ** 1.4
        out = over_spr(out, solid(_shift(a, i * 0.42, i * 1.0), (c[0], c[1], c[2], 1)))
    return over_spr(out, emboss(a, K * bevel, kind))


@functools.lru_cache(maxsize=None)
def gold_text(text, fname, size, tracking=0.0):
    return pad(emboss(text_mask(text, fname, size, tracking), K, 'gold'), int(3 * K))


@functools.lru_cache(maxsize=None)
def glow_spr():
    return radial_sprite(256, GOLD, power=2.2)


@functools.lru_cache(maxsize=None)
def dot_spr():
    return radial_sprite(64, GOLD, power=1.6, core=0.6)


@functools.lru_cache(maxsize=None)
def rays_spr():
    n = int(900 * max(1.0, K * 0.8))
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
    return streak_sprite(int(1400 * K), int(80 * K), GOLD, (1.0, 0.92, 0.75))


@functools.lru_cache(maxsize=None)
def big_type(text, height):
    size = int(height * 1.32 * K)
    m = text_mask(text, TITLE_FONT, size, TITLE_TRACK)
    BIG_GLYPH_H[(text, height)] = m.shape[0]
    a = np.pad(m, int(130 * K))
    if BIG_STYLE == 'flat':        # reference look: flat gold fill with a hot glow, no extrusion
        g = cv2.GaussianBlur(a, (0, 0), 10 * K) * 0.8 + cv2.GaussianBlur(a, (0, 0), 34 * K) * 0.7
        return over_spr(solid(np.clip(g, 0, 1), GOLD), solid(a, GOLD))
    return deep_style(a, 'gold', ext=max(6.0, height * 0.075), glow=1.0, bevel=2.4)


BIG_GLYPH_H = {}


def big_scale(text, height, sz):
    """World units per sprite pixel so the letters (not the padded sprite) are `sz` tall."""
    big_type(text, height)
    return sz / BIG_GLYPH_H[(text, height)]


@functools.lru_cache(maxsize=None)
def neon_type(text, height):
    size = int(height * 1.32 * K)
    a = text_mask(text, NEON_FONT, size, 0.04)
    a = np.pad(a, int(40 * K))
    kk = int(9 * K) | 1
    k = np.ones((kk, kk), np.uint8)
    edge = np.clip(cv2.dilate(a, k) - cv2.erode(a, k), 0, 1)
    core = solid(edge, (1.0, 0.86, 0.6, 1))
    halo = solid(cv2.GaussianBlur(edge, (0, 0), 14 * K) * 1.6, GOLD)
    halo2 = solid(cv2.GaussianBlur(edge, (0, 0), 40 * K) * 1.2, GOLD)
    inner = solid(a * 0.10, GOLD)
    return over_spr(over_spr(over_spr(halo2, halo), inner), core)


@functools.lru_cache(maxsize=None)
def gold_pill(text, size=34, outline=False):
    """Gold tag (outline) or solid gold label, built at output resolution."""
    ts = gold_text(text, PILL_FONT, int(size * K), 0.06) if outline else \
        text_sprite(text, PILL_FONT, int(size * K), INK, 0.06)
    th, tw = ts.shape[:2]
    px, py = (24, 14) if outline else (30, 18)
    w, h = int(tw + (2 * px - 6) * K), int(th + (2 * py - 6) * K)
    P = int(36 * K)
    d = rrect_alpha(w, h, (10 if outline else 14) * K, P)
    spr = solid(sdf_fill(d), (0.02, 0.02, 0.02, 0.72)) if outline else emboss(sdf_fill(d), K * 1.5, 'gold')
    if outline:
        spr = over_spr(spr, solid(sdf_stroke(d, 2.0 * K), GOLD))
    g = cv2.GaussianBlur(solid(sdf_fill(d), (GOLD[0], GOLD[1], GOLD[2], 0.35 if outline else 0.55)), (0, 0), 12 * K)
    spr = over_spr(g, spr)
    tmp = np.zeros_like(spr)
    y0, x0 = int(round(P + h / 2 - th / 2)), int(round(P + (w - tw) / 2))
    tmp[y0:y0 + th, x0:x0 + tw] = ts
    return over_spr(spr, tmp)


@functools.lru_cache(maxsize=None)
def stage_bg():
    im = cv2.imread(f'{S}/assets2d/bg_dark_stage.jpg')[..., ::-1].astype(np.float32) / 255
    h, w = im.shape[:2]
    s = max(OW * 1.25 / w, OH * 1.25 / h)
    im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    lum = (im @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    im = lum * np.array([1.0, 0.86, 0.66], np.float32) * 0.9   # neutral-warm dark stage
    return np.concatenate([im, np.ones(im.shape[:2] + (1,), np.float32)], 2)


@functools.lru_cache(maxsize=3)
def card_mask(w, h, r):
    d = rrect_alpha(w, h, r, 0)
    return sdf_fill(d)


@functools.lru_cache(maxsize=None)
def card_border(w, h, r):
    """Gold edge + glow and the drop shadow of a w x h (output px) card; returns P in design px."""
    P = int(60 * K)
    d = rrect_alpha(w, h, r, P)
    line = solid(sdf_stroke(d, 4 * K), GOLD)
    glow = solid(cv2.GaussianBlur(sdf_stroke(d, 6 * K), (0, 0), 16 * K) * 1.4, GOLD)
    shadow = solid(cv2.GaussianBlur(sdf_fill(d), (0, 0), 30 * K) * 0.8, (0, 0, 0, 1))
    return over_spr(glow, line), shadow, P / K

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
            spr = blur_sprite(spr, bl * K)
        pos, sz = _anchor_cached(('big', t_in), CX, sy, height, dz, t_in + 0.3)
        h3 = spr.shape[0] * big_scale(text, height, sz)
        draw3d(cv, spr, pos[0] + u * 14, pos[1], pos[2], h=h3 * sc, ry=-4 + u * 2, cam=cam, opacity=op)


_anchors = {}


def _anchor_cached(key, sx, sy, size, dz, ta):
    if key not in _anchors:
        _anchors[key] = anchor_world(sx, sy, size, dz, ta)
    return _anchors[key]


@functools.lru_cache(maxsize=None)
def halo_spr():
    n = int(700 * K)
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((xs - n / 2) ** 2 + (ys - n / 2) ** 2) / (n / 2)
    disc = np.clip((1 - r) / 0.12, 0, 1) * (0.62 + 0.38 * np.clip(1 - r, 0, 1) ** 0.5)
    glow = np.clip(1 - r, 0, 1) ** 2 * 0.0
    a = np.clip(disc + glow, 0, 1)
    c = np.array([1.0, 0.86, 0.60], np.float32)
    return np.concatenate([a[..., None] * c, a[..., None]], 2).astype(np.float32)


@functools.lru_cache(maxsize=None)
def title_block(text):
    ts = text_sprite(text, BLOCK_FONT, int(150 * K), INK, 0.02)
    th, tw = ts.shape[:2]
    P, px, py = int(40 * K), int(34 * K), int(10 * K)
    w, h = tw + 2 * px, th + 2 * py
    d = rrect_alpha(w, h, 8 * K, P)
    spr = over_spr(cv2.GaussianBlur(solid(sdf_fill(d), (GOLD[0], GOLD[1], GOLD[2], 0.6)), (0, 0), 18 * K),
                   emboss(sdf_fill(d), K * 2.0, 'gold'))
    tmp = np.zeros_like(spr)
    tmp[P + py:P + py + th, P + px:P + px + tw] = ts
    return over_spr(spr, tmp)


def _spline(pts, n=220):
    """Catmull-Rom through the control points."""
    p = np.asarray([pts[0]] + list(pts) + [pts[-1]], np.float64)
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for u in np.linspace(0, 1, n // (len(p) - 3), endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    out.append(p[-2])
    return np.asarray(out)


def _trail(cv, t, cam, t_in, t_out, pts):
    """Neon gold light trail drawing on along a spline (trim-path), with glow."""
    u = t - t_in
    head = e_out_cubic(clamp(u / 0.65))
    tail = e_in_cubic(clamp((t - (t_out - 0.45)) / 0.45))
    if head <= tail + 0.01:
        return
    key = ('trail', t_in)
    if key not in _anchors:
        cam0, _, _ = camera(t_in + 0.3)
        zq = person_depth(cam0) + 40
        sp = _spline(pts)
        _anchors[key] = np.array([unproject(x, y, zq, cam0) for x, y in sp])
    world = _anchors[key]
    n = len(world)
    seg = world[int(tail * (n - 1)):max(int(head * (n - 1)) + 1, int(tail * (n - 1)) + 2)]
    scr, ok = en.project_pts(seg, cam)
    if not ok:
        return
    scr = scr * K
    m = int(40 * K)
    x0, y0 = int(scr[:, 0].min()) - m, int(scr[:, 1].min()) - m
    x1, y1 = int(scr[:, 0].max()) + m, int(scr[:, 1].max()) + m
    x0, y0, x1, y1 = max(x0, -m), max(y0, -m), min(x1, OW + m), min(y1, OH + m)
    if x1 <= x0 or y1 <= y0:
        return
    mask = np.zeros((y1 - y0, x1 - x0), np.float32)
    p = np.round((scr - [x0, y0]) * 4).astype(np.int32)
    cv2.polylines(mask, [p], False, 1.0, int(5 * K), cv2.LINE_AA, shift=2)
    glow = cv2.GaussianBlur(mask, (0, 0), 9 * K) * 1.6 + cv2.GaussianBlur(mask, (0, 0), 28 * K) * 1.2
    core = np.array([1.0, 0.93, 0.78], np.float32)
    rgb = mask[..., None] * core + np.clip(glow, 0, 1.5)[..., None] * GOLD3
    a = np.clip(mask + glow * 0.5, 0, 1)
    en.composite(cv, np.concatenate([rgb, a[..., None]], 2).astype(np.float32), x0, y0, 1.0, 'add')


def _hook(cv, t, cam, layer):
    hk = TL.HOOK
    if t > 3.6:
        return
    if layer == 'back':
        t_in, t_out, sx, sy, dia = hk['halo']
        if t_in <= t < t_out:
            p = clamp((t - t_in) / 0.35)
            op = clamp((t_out - t) / 0.25)
            pos, sz = _anchor_cached(('halo',), sx, sy, dia, 260, 0.6)
            draw3d(cv, glow_spr(), pos[0], pos[1], pos[2] + 2, h=sz * 1.9, cam=cam, opacity=0.65 * op, mode='add')
            draw3d(cv, halo_spr(), pos[0], pos[1], pos[2], h=sz * lerp(0.4, 1.0, e_out_back(p, 1.8)), cam=cam,
                   opacity=0.92 * op * clamp(p * 4))
        for word, t_in, t_out, sy, height, ry in hk['flank']:
            if not (t_in <= t < t_out):
                continue
            u = t - t_in
            p = clamp(u / 0.30)
            op = clamp(u / 0.06) * clamp((t_out - t) / 0.12)
            full = big_type(word, height)
            spr = full if p >= 1 else blur_sprite(full, (1 - p) * 14 * K)
            pos, sz = _anchor_cached(('flank', word), CX, sy, height, 320, t_in + 0.25)
            h3 = spr.shape[0] * big_scale(word, height, sz)
            draw3d(cv, spr, pos[0] + u * 16, pos[1], pos[2], h=h3 * lerp(1.45, 1.0, e_out_expo(p)), ry=ry,
                   cam=cam, opacity=op)
    for t_in, t_out, ly, pts in hk['trails']:
        if ly == layer and t_in <= t < t_out:
            _trail(cv, t, cam, t_in, t_out, pts)
    if layer == 'front':
        t_in, t_out, text, sx, sy, rot = hk['block']
        if t_in <= t < t_out:
            u = t - t_in
            p = clamp(u / 0.26)
            op = clamp(u / 0.05) * clamp((t_out - t) / 0.18)
            spr = title_block(text)
            pos, sz = _anchor_cached(('block', text), sx, sy, spr.shape[0] / K, -150, t_in + 0.2)
            draw3d(cv, spr, pos[0], pos[1], pos[2], h=sz * lerp(2.3, 1.0, e_out_expo(p)),
                   rz=rot + (1 - e_out_expo(p)) * -10, cam=cam, opacity=op)


def _pills(cv, t, cam, layer):
    for t_in, t_out, text, sx, sy, ly in TL.PILLS:
        if ly != layer or not (t_in <= t < t_out):
            continue
        spr = gold_pill(text, 34, outline=True)
        u, out = t - t_in, t_out - t
        p = clamp(u / 0.35)
        op = clamp(u / 0.1) * clamp(out / 0.2)
        pos, sz = _anchor_cached(('pill', t_in, text), sx, sy, spr.shape[0] / K, -60 if layer == 'front' else 60, t_in + 0.3)
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
    P = int(24 * K)
    d = rrect_alpha(int(w * K), int(26 * K), 13 * K, P)
    track = over_spr(solid(sdf_fill(d), (0.03, 0.03, 0.03, 0.85)), solid(sdf_stroke(d, 2 * K), GOLD))
    lab = gold_text(label, 'Cinzel-700', int(30 * K), 0.08)
    return track, lab, P


def _meters(cv, t, cam):
    for t_in, t_out, v0, v1, sx, sy, label in TL.METERS:
        if not (t_in <= t < t_out):
            continue
        u, out = t - t_in, t_out - t
        op = clamp(u / 0.15) * clamp(out / 0.2)
        wbar = 340
        track, lab, P = meter_parts(wbar, label)
        top = int(60 * K)
        cv_l = np.zeros((track.shape[0] + top, track.shape[1], 4), np.float32)
        cv_l[top:] = track
        v = lerp(v0, v1, e_inout_cubic(clamp((u - 0.25) / 0.9)))
        fw = max(2, int((wbar - 8) * v * K))
        bh, inset = int(18 * K), int(4 * K)
        d = rrect_alpha(fw, bh, 9 * K, 0)
        fill = solid(sdf_fill(d), GOLD)
        y0 = top + P + inset
        cv_l[y0:y0 + bh, P + inset:P + inset + fw] = over_spr(cv_l[y0:y0 + bh, P + inset:P + inset + fw], fill)
        lh, lw = lab.shape[:2]
        x0 = (cv_l.shape[1] - lw) // 2
        y1 = int(8 * K)
        cv_l[y1:y1 + lh, x0:x0 + lw] = over_spr(cv_l[y1:y1 + lh, x0:x0 + lw], lab)
        pos, sz = _anchor_cached(('meter', t_in), sx, sy, cv_l.shape[0] / K, 120, t_in + 0.3)
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
    cv = np.zeros((OH, OW, 3), np.float32)
    ocam = Cam(x=30 * math.sin(u * 0.6), y=10 * math.sin(u * 0.5), z=40 * u, ry=3 * math.sin(u * 0.7), rz=0)
    bg = stage_bg()
    draw3d(cv, bg, CX, CY, 300, h=bg.shape[0] * 1.2 / K, cam=ocam, opacity=k)
    # giant neon outline word behind the card, scrolling sideways
    nt = neon_type(s['neon'], 760)
    draw3d(cv, nt, CX + 120 - u * 90, CY - 40, 220, h=nt.shape[0] * 1.15 / K, cam=ocam, opacity=k * 0.95, mode='add')
    draw3d(cv, glow_spr(), CX, CY + 80, 250, h=1700, cam=ocam, opacity=0.35 * k, mode='add')
    # the live video becomes a floating rounded card
    sc = lerp(1.0, 0.64, k)
    r = int(round(lerp(0, 56, k) / max(sc, 0.3) / 8)) * 8
    a = card_mask(OW, OH, int(r * K)) if r > 0 else np.ones((OH, OW), np.float32)
    card = np.concatenate([inner * a[..., None], a[..., None]], 2)
    ry = lerp(0, -13, k) + 3 * math.sin(u * 1.2) * k
    rx = lerp(0, 5, k)
    cy = CY + lerp(0, -40, k)
    bspr, shadow, P = card_border(OW, OH, int(56 * K))
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
            draw3d(cv, spr, CX + fx * W * sc * 1.02, cy + fy * H * sc, -40, h=spr.shape[0] / K * lerp(0.4, 1, e_out_back(tp, 2)),
                   ry=ry * 0.6, cam=ocam, opacity=tp * k)
        # numbered chapter pill
        tp = clamp((u - 0.35) / 0.35)
        if tp > 0:
            txt = f"{s['num']}  ·  {s['title']}"
            n = max(1, int(round(len(txt) * e_out_cubic(clamp((u - 0.35) / 0.55)))))
            spr = gold_pill(txt[:n], 46)
            draw3d(cv, spr, CX, cy - H * sc * 0.5 - 6, -60, h=spr.shape[0] / K * lerp(0.5, 1, e_out_back(tp, 2)),
                   ry=ry * 0.5, cam=ocam, opacity=tp * k)
            nb = gold_pill(s['num'], 64)
            draw3d(cv, nb, CX, cy - H * sc * 0.02, -50, h=nb.shape[0] / K * lerp(0.3, 1, e_out_back(clamp((u - 0.25) / 0.3), 2.5)),
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


def phrases():
    global PHRASES
    if PHRASES is None:
        PHRASES = _parse_captions()
    return PHRASES


TITLE_FONT, TITLE_TRACK = 'Cinzel-900', 0.02   # cinematic titles; captions stay General Sans
PILL_FONT, NEON_FONT, BLOCK_FONT, BIG_STYLE = 'Cinzel-800', 'Cinzel-900', 'Cinzel-900', 'deep'
CAP_STYLE = {True: ('GeneralSans-700', 104, GOLD), False: ('GeneralSans-600', 70, WHITE)}


@functools.lru_cache(maxsize=16)
def glyph(text, gold):
    """Word sprite at output resolution with its exact pen origin: (sprite, baseline_row, origin_col, advance_px)."""
    fname, size, col = CAP_STYLE[gold]
    f = en.font(fname, int(size * K))
    x0, y0, x1, y1 = f.getbbox(text, anchor='ls')
    p = int(80 * K)
    from PIL import Image, ImageDraw
    im = Image.new('L', (x1 - x0 + 2 * p, y1 - y0 + 2 * p), 0)
    ImageDraw.Draw(im).text((p - x0, p - y0), text, font=f, fill=255, anchor='ls')
    a = np.asarray(im).astype(np.float32) / 255.0
    spr = deep_style(a, 'gold', ext=7.0, glow=0.8, bevel=1.2, sig=(9, 24)) if gold else \
        deep_style(a, 'white', ext=4.0, glow=0.5, bevel=0.9, sig=(9, 24))
    return spr, p - y0, p - x0, f.getlength(text)


@functools.lru_cache(maxsize=None)
def cap_metrics(gold):
    fname, size, _ = CAP_STYLE[gold]
    f = en.font(fname, int(size * K))
    cap = -f.getbbox('H', anchor='ls')[1] / K
    return cap, f.getlength(' ') / K


@functools.lru_cache(maxsize=None)
def phrase_layout(i):
    """Centre-aligned lines sharing exact baselines; returns [(word, sprite, cx, cy)] in design px."""
    ph = phrases()[i]
    lines = []
    for row in ph['rows']:
        items, x = [], 0.0
        for j, w in enumerate(row):
            spr, base, left, adv = glyph(w['text'], w['gold'])
            if j:
                x += max(cap_metrics(w['gold'])[1], cap_metrics(row[j - 1]['gold'])[1]) * 1.55 + 4
            items.append((w, spr, base, left, x))
            x += adv / K
        cap = max(cap_metrics(w['gold'])[0] for w in row)
        lines.append((items, x, cap))
    # baselines: first line at its cap height, then leading = 0.30 cap of the next line
    ys, y = [], 0.0
    for n, (items, wid, cap) in enumerate(lines):
        y += cap if n == 0 else cap * 1.30
        ys.append(y)
    top, bottom = 0.0, ys[-1]
    place = []
    for (items, wid, cap), yb in zip(lines, ys):
        x_left = -wid / 2
        for w, spr, base, left, x in items:
            h, wpx = spr.shape[:2]
            cx = x_left + x - left / K + wpx / K / 2
            cy = (yb - (top + bottom) / 2) - base / K + h / K / 2
            place.append((w, spr, cx, cy))
    return place


def draw_captions(cv, t, v, shot):
    for ph in phrases():
        if not (ph['t_on'] <= t < ph['t_off']):
            continue
        out = clamp((t - (ph['t_off'] - 0.09)) / 0.09)     # exit finishes before the next phrase starts
        base_y = TL.CAPTION_Y[shot_of(ph['t_on'] + 0.05)]
        # captions ride along with the camera (partially) so they feel attached to the shot
        z = v['zoom'] ** 0.25
        ax = CX - (v['x'] - v.get('xw', 0.0)) * 0.22 - v.get('xw', 0.0) * 0.6
        ay = base_y - v['y'] * 0.15 - out * 40
        for w, spr0, ox, oy in phrase_layout(ph['i']):
            u = t - w['t'] + 0.03
            if u < 0:
                continue
            p = clamp(u / 0.16)
            sc = lerp(0.55, 1.0, e_out_back(p, 2.2)) * z
            op = clamp(u / 0.06) * (1 - out)
            px = ax + ox * z
            py = ay + oy * z + (1 - e_out_cubic(p)) * 26
            bl = (1 - p) * 6 + out * 8
            spr = spr0 if bl < 0.6 else blur_sprite(spr0, bl * K)
            draw(cv, spr, px, py, sc * spr.shape[0] / spr0.shape[0], 0, op)

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


def draw_stage(cv, t, i, cam, plates, v):
    sigma, dim, bcam = dof_at(t), bg_dim_at(t), bg_camera(v)
    for sh, xoff in plates:
        fi = hold_frame(i, sh)
        L = SRC.layers(fi)
        bg = bg_sprite(fi, sigma)
        draw3d(cv, bg, CX + xoff, CY, 0, w=W * (1 + 2 * L['pad']), h=H + 2 * L['pad'] * W, cam=bcam, opacity=dim)
    _rays(cv, t, cam, shot_of(t))
    _dust_draw(cv, t, cam, front=False)


def draw_back(cv, t, cam, plates):
    _hook(cv, t, cam, 'back')
    _big_types(cv, t, cam)
    _ingot_rain(cv, t, cam, 'back')
    for el in elements():
        if el.e['layer'] == 'back' and el.active(t):
            xoff = dict(plates).get(el.shot, None)
            if xoff is not None:
                el.draw(cv, t, cam, xoff)
    _pills(cv, t, cam, 'back')
    _meters(cv, t, cam)


def draw_person(cv, i, cam, plates):
    for sh, xoff in plates:
        draw3d(cv, SRC.layers(hold_frame(i, sh))['person'], CX + xoff, CY, 0, w=W, h=H, cam=cam)


def draw_front(cv, t, cam, plates):
    for el in elements():
        if el.e['layer'] == 'front' and el.active(t):
            xoff = dict(plates).get(el.shot, None)
            if xoff is not None:
                el.draw(cv, t, cam, xoff)
    _pills(cv, t, cam, 'front')
    _ingot_rain(cv, t, cam, 'front')
    _hook(cv, t, cam, 'front')


def render_inner(t, i):
    cam, plates, v = camera(t)
    cv = np.zeros((OH, OW, 3), np.float32)
    draw_stage(cv, t, i, cam, plates, v)
    draw_back(cv, t, cam, plates)
    draw_person(cv, i, cam, plates)
    draw_front(cv, t, cam, plates)
    _dust_draw(cv, t, cam, front=True)
    return cv, cam, v, plates


def camera_fast(t):
    """True while the camera itself moves fast enough to need the plate motion-blurred too."""
    if transition_state(t) or snap_values(t)[1]:
        return True
    s_, k, u = section_k(t)
    if s_ is not None and 0 < k < 1:
        return True
    return any(tp - 0.05 <= t < tp + 0.4 for tp, kick, amp in TL.PUNCH)


class Layer:
    """Premultiplied RGBA accumulator for sub-frame motion blur of graphics only."""
    def __init__(self):
        self.acc = np.zeros((OH, OW, 4), np.float32)
        self.tmp = np.zeros((OH, OW, 4), np.float32)
        self.rect = None

    def sample(self, fn):
        DIRTY.clear()
        fn(self.tmp)
        if not DIRTY:
            return
        x0 = min(r[0] for r in DIRTY); y0 = min(r[1] for r in DIRTY)
        x1 = max(r[2] for r in DIRTY); y1 = max(r[3] for r in DIRTY)
        self.acc[y0:y1, x0:x1] += self.tmp[y0:y1, x0:x1]
        self.tmp[y0:y1, x0:x1] = 0
        r = self.rect
        self.rect = (x0, y0, x1, y1) if r is None else (min(r[0], x0), min(r[1], y0), max(r[2], x1), max(r[3], y1))

    def over(self, cv, n):
        if self.rect is None:
            return
        x0, y0, x1, y1 = self.rect
        a = self.acc[y0:y1, x0:x1] / n
        dst = cv[y0:y1, x0:x1]
        dst *= 1 - a[..., 3:4]
        dst += a[..., :3]
        self.acc[y0:y1, x0:x1] = 0
        self.rect = None


_layers = {}


def layer(name):
    if name not in _layers:
        _layers[name] = Layer()
    return _layers[name]


def nsub_at(t):
    if transition_state(t):
        return 7
    s, k, u = section_k(t)
    if s is not None and 0 < k < 1:
        return 7
    for e in TL.ELEMENTS:
        if e['t0'] - 0.02 <= t < e['t0'] + 0.5 or e['t1'] - 0.3 <= t < e['t1']:
            return 5
    for tp, kick, amp in TL.PUNCH:
        if tp <= t < tp + 0.35:
            return 5
    if snap_values(t)[1]:
        return 4
    for k in TL.CAM:
        if k[7] and abs(t - k[0]) < 0.02:
            return 1
    return 3


def render_frame(fi):
    t = fi / FPS
    en._mips.clear()
    n = nsub_at(t)
    shutter = 0.55 / FPS
    if n > 1 and not camera_fast(t):
        cv = _render_layered(fi, t, n, shutter)
    else:
        cv = _render_full(fi, t, n, shutter)
    return _finish(cv, fi, t)


def _render_layered(fi, t, n, shutter):
    """Slow camera: stage + presenter once at the frame centre, graphics and captions motion-blurred."""
    cam, plates, v = camera(t)
    cv = np.zeros((OH, OW, 3), np.float32)
    draw_stage(cv, t, fi, cam, plates, v)
    back, front = layer('back'), layer('front')
    for j in range(n):
        ts = t + ((j + 0.5) / n - 0.5) * shutter
        cj, pj, vj = camera(ts)
        back.sample(lambda c: draw_back(c, ts, cj, pj))
        front.sample(lambda c: (draw_front(c, ts, cj, pj), draw_captions(c, ts, vj, shot_of(ts))))
    back.over(cv, n)
    draw_person(cv, fi, cam, plates)
    s_, k, u = section_k(t)
    if s_ is not None and k > 0.001:
        front.over(cv, n)
        _dust_draw(cv, t, cam, front=True)
        return render_section(cv, t, s_, k, u)
    front.over(cv, n)
    _dust_draw(cv, t, cam, front=True)
    return cv


def _render_full(fi, t, n, shutter):
    acc = np.zeros((OH, OW, 3), np.float32)
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
    return acc / n


def _finish(cv, fi, t):
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
    return post_out(cv, fi, bloom=0.55, grain=0.016, ca=ca, flash=flash, flash_color=(1.0, 0.75, 0.42), fade=fade)


_post = {}


def post_out(img, fi, bloom=0.55, grain=0.016, ca=0.0, flash=0.0, flash_color=(1, 0.75, 0.42), fade=0.0):
    """Gold-tinted bloom, chromatic aberration, flash, vignette, filmic shoulder, deep blacks, grain -> uint8."""
    if not _post:
        rng = np.random.default_rng(7)
        _post['grain'] = [np.clip(rng.normal(0, 1, (OH // 2, OW // 2)) * 255 * 0.016, -12, 12).astype(np.int16)
                          for _ in range(6)]
        ys, xs = np.mgrid[0:OH, 0:OW].astype(np.float32)
        r = np.sqrt(((xs - OW / 2) / (OW * 0.62)) ** 2 + ((ys - OH / 2) / (OH * 0.62)) ** 2)
        _post['vig'] = np.clip(1 - 0.42 * r ** 2.4, 0.35, 1).astype(np.float32)
        x = np.linspace(0, 2, 2048, dtype=np.float32)
        y = np.where(x > 0.82, 0.82 + 0.18 * np.tanh((x - 0.82) / 0.18), x)
        _post['lut'] = y * 0.995 + 0.003
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    br = np.maximum(small - 0.62, 0)
    b = cv2.GaussianBlur(br, (0, 0), 5) * 0.6 + cv2.GaussianBlur(br, (0, 0), 18) * 1.0
    b = b * (np.array([1.0, 0.74, 0.45], np.float32) * bloom)         # halation leans gold
    if flash > 0:
        b = b + np.array(flash_color, np.float32) * flash
    img += cv2.resize(b, (OW, OH), interpolation=cv2.INTER_LINEAR)
    if ca > 0.05:
        k = int(round(ca * K))
        if k >= 1:
            img = np.stack([np.roll(img[..., 0], k, axis=1), img[..., 1], np.roll(img[..., 2], -k, axis=1)], 2)
    img *= _post['vig'][..., None]
    lut = _post['lut'] * (1 - fade)
    idx = np.clip(img * 1023.5, 0, 2047).astype(np.int16)
    out = (lut[idx] * 255).astype(np.int16)
    if grain > 0:
        g = cv2.resize(_post['grain'][fi % 6], (OW, OH), interpolation=cv2.INTER_NEAREST)
        out += g[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def to_u8(img):
    if img.dtype == np.uint8:
        return img
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
                              '-s', f'{OW}x{OH}', '-r', '30000/1001', '-i', '-', '-c:v', 'libx264', '-preset', 'faster',
                              '-crf', '11', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for fi in range(f0, f1):
            p.stdin.write(to_u8(render_frame(fi)).tobytes())
            if fi % 20 == 0:
                print('frame', fi, flush=True)
        p.stdin.close()
        p.wait()


if __name__ == '__main__':
    main()
