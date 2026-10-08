"""Rida — Japan bonds / Yen carry trade reel.

Talking-head edit in the style of the caption reference: punch-in jump cuts on the talent,
single-word pop captions (SF-Pro-style bold sans, here Inter Display), yellow glowing kinetic
type stacked in 3D space, yellow glowing icons and a face-tracking box, plus After-Effects-style
3D-space motion-graphic cutaways (3D camera, perspective grid floor, glass cards, coins, charts).

  python3 pipeline/rida/edit.py still 1.0,7.5,...      -> workspace/rida/stills/*.jpg
  python3 pipeline/rida/edit.py chunk <f0> <f1> <out>   -> renders frames [f0,f1) to an mp4
  python3 pipeline/rida/edit.py sfx <out.json>          -> SFX cue list for audio.py
"""
import os, sys, json, math, subprocess
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.setdefault('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', '..', 'workspace', 'rida')))
sys.path.insert(0, os.path.dirname(HERE))
import engine as E
from engine import (W, H, CX, CY, Cam, clamp, lerp, prog, e_out_expo, e_out_back, e_out_cubic, e_inout_cubic,
                    e_in_cubic, smooth, draw, draw3d, composite, blur_sprite, tint, pad, solid, over_spr, rrect_alpha,
                    sdf_fill, sdf_stroke, radial_sprite, rotm, project_pts)

FPS = 30


def _composite4(canvas, spr, x0, y0, opacity=1.0, mode='over'):
    """engine.composite, extended to premultiplied RGBA layers (for the 3D text layer)."""
    h, w = spr.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x0 + w), min(canvas.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0 or opacity <= 0.001:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    dst = canvas[Y0:Y1, X0:X1]
    c = dst.shape[2]
    if mode in ('add', 'screen'):
        dst[..., :3] += s[..., :3] * opacity
    else:
        dst *= (1 - s[..., 3:4] * opacity)
        dst += s[..., :c] * opacity


E.composite = _composite4
# Instagram Reels safe zone (1080x1920): keep text clear of the top header (~260px), the bottom
# caption/username/audio bar (~440px) and the right-hand like/comment/share column (~140px).
SAFE = dict(x0=64, x1=940, y0=260, y1=1480)
SAFE_CAP_T = 1120   # caption centre over the talent
SAFE_CAP_G = 1420   # caption centre in the 3D cutaways
PLATE = f'{WORK}/work_graded.mp4'
WORDS = json.load(open(f'{WORK}/ana/captions_words.json'))
FACE = json.load(open(f'{WORK}/ana/face.json'))
NFR = FACE['n']
DUR = NFR / FPS

YEL = (1.0, 0.84, 0.12)
YEL_TOP = (1.0, 0.91, 0.38)
YEL_BOT = (1.0, 0.72, 0.02)
GLOW = (1.0, 0.58, 0.0)
WHITE = (1.0, 1.0, 1.0)
GREEN = (0.30, 0.88, 0.42)
RED = (1.0, 0.28, 0.26)
FB = 'InterDisplay-Bold'
FX = 'InterDisplay-ExtraBold'
FK = 'InterDisplay-Black'

# ====================================================================== sprites


def _glyph_mask(ch, fname, size):
    """Single glyph on a fixed ascent+descent box (no trimming) so letters share one baseline."""
    from PIL import Image, ImageDraw
    f = E.font(fname, size)
    asc, desc = f.getmetrics()
    wd = int(math.ceil(f.getlength(ch))) + 8
    im = Image.new('L', (wd, asc + desc + 8), 0)
    ImageDraw.Draw(im).text((4, 4), ch, font=f, fill=255)
    return np.asarray(im).astype(np.float32) / 255.0


def _mask(txt, fname, size, squeeze=1.0, tracking=-0.02):
    if txt.startswith('\x00'):
        a = _glyph_mask(txt[1:], fname, size)
    else:
        a = E.text_mask(txt, fname, size, tracking)
    if abs(squeeze - 1) > 1e-3:
        a = cv2.resize(a, (max(2, int(a.shape[1] * squeeze)), a.shape[0]), interpolation=cv2.INTER_AREA)
    return a


_tc = {}


def tpad(size):
    return int(size * 1.1) + 10


def text(txt, size, style='w', fname=None, squeeze=None, shadow=0.55, glow=None, extrude=0):
    """Premultiplied text sprite. style 'w' white bold, 'y' yellow gradient heavy + glow,
    'g' green, 'r' red, 'd' dark."""
    key = (txt, size, style, fname, squeeze, shadow, glow, extrude)
    if key in _tc:
        return _tc[key]
    if fname is None:
        fname = FB if style == 'w' else FK
    if squeeze is None:
        squeeze = 1.0 if style == 'w' else 0.9
    a = _mask(txt, fname, size, squeeze)
    P = tpad(size)
    a = np.pad(a, P)
    h, w = a.shape
    if style == 'y':
        t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        rgb = np.array(YEL_TOP, np.float32) * (1 - t) + np.array(YEL_BOT, np.float32) * t
        fill = np.concatenate([rgb * a[..., None], a[..., None]], 2)
        glow = 0.6 if glow is None else glow
        gcol = GLOW
    else:
        col = {'w': WHITE, 'g': GREEN, 'r': RED, 'd': (0.06, 0.06, 0.08)}[style]
        fill = solid(a, col + (1.0,))
        gcol = col
    spr = np.zeros((h, w, 4), np.float32)
    if shadow:
        # smooth two-layer drop shadow: soft contact shadow + wide ambient shadow (keeps text readable
        # on the bright wall without an outline)
        s1 = cv2.GaussianBlur(np.roll(a, int(size * 0.035) + 1, 0), (0, 0), size * 0.05 + 1.5) * 0.55
        s2 = cv2.GaussianBlur(np.roll(a, int(size * 0.06) + 2, 0), (0, 0), size * 0.20 + 4) * 0.55
        sa = np.clip(1 - (1 - s1) * (1 - s2), 0, 1) * min(1.0, shadow / 0.55)
        spr = over_spr(spr, solid(sa, (0, 0, 0, 1)))
    if glow:
        g = cv2.GaussianBlur(a, (0, 0), size * 0.10 + 2)
        g2 = cv2.GaussianBlur(a, (0, 0), size * 0.30 + 5)
        ga = np.clip(g * 0.45 + g2 * 0.22, 0, 1) * glow
        gs = solid(ga, gcol + (1.0,))
        gs[..., 3] *= 0.0  # additive-ish glow: colour without occluding
        spr = spr + gs
    if extrude:
        # extruded 3D lettering: stacked, progressively darker copies behind the face
        n = int(extrude)
        base = np.array(YEL_BOT if style == 'y' else (0.75, 0.75, 0.78), np.float32)
        for k in range(n, 0, -1):
            m = np.roll(np.roll(a, k, 0), int(k * 0.55), 1)
            shade = base * (0.30 + 0.32 * (1 - k / n))
            spr = over_spr(spr, np.concatenate([shade * m[..., None], m[..., None]], 2).astype(np.float32))
    spr = over_spr(spr, fill)
    _tc[key] = spr
    return spr


def load_rgba(path, max_side):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.concatenate([im, np.full(im.shape[:2] + (1,), 255, np.uint8)], 2)
    ys, xs = np.where(im[..., 3] > 8)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = max_side / max(im.shape[:2])
    im = cv2.resize(im, (max(1, int(im.shape[1] * s)), max(1, int(im.shape[0] * s))), interpolation=cv2.INTER_AREA)
    return E.to_premul(im[..., [2, 1, 0, 3]])


def glowify(spr, color, sigma=16, strength=0.9, fill=None):
    """Tint a silhouette icon and give it the reference's yellow glow."""
    s = spr if fill is None else tint(spr, fill)
    s = pad(s, int(sigma * 3))
    g = cv2.GaussianBlur(s[..., 3], (0, 0), sigma) * strength
    gs = np.zeros_like(s)
    gs[..., :3] = np.array(color, np.float32) * g[..., None]
    return gs + s


SRC = f'{WORK}/src/broll'
_spr = {}


def asset(name):
    if name in _spr:
        return _spr[name]
    if name == 'gold':
        s = load_rgba(f'{SRC}/pngwing4.png', 520)
        s = glowify(s, (1.0, 0.65, 0.1), 22, 0.35)
    elif name == 'hand':
        s = glowify(load_rgba(f'{SRC}/hand_dollar.png', 300), GLOW, 12, 0.5, fill=YEL)
    elif name == 'yen_icon':
        s = glowify(load_rgba(f'{SRC}/yen.png', 260), GLOW, 12, 0.5, fill=YEL)
    elif name in ('up_g', 'down_r', 'up_r', 'down_g'):
        boxes = {'up_r': (570, 830), 'down_r': (2240, 980), 'up_g': (570, 4320), 'down_g': (2240, 4470)}
        x, y = boxes[name]
        im = cv2.imread(f'{SRC}/arrows.png', cv2.IMREAD_UNCHANGED)[y:y + 2700, x:x + 1500]
        im = cv2.resize(im, (150, 270), interpolation=cv2.INTER_AREA)
        s = E.to_premul(im[..., [2, 1, 0, 3]])
        col = GREEN if name.endswith('g') else RED
        s = glowify(s, col, 10, 0.45)
    elif name == 'bang':
        s = bang_sprite()
    elif name == 'jp':
        s = flag_card('jp')
    elif name == 'us':
        s = flag_card('us')
    elif name == 'cursor':
        s = cursor_sprite()
    elif name == 'coin_yen':
        s = coin('¥')
    elif name == 'coin_usd':
        s = coin('$')
    _spr[name] = s
    return s


def dof_sprite(name, depth, focus=0.0, k=1 / 170.0, cap=12):
    """Depth-of-field for 3D scene elements: blur grows with distance from the focus plane."""
    sig = min(cap, abs(depth - focus) * k)
    lv = round(sig / 1.5) * 1.5
    if lv < 0.75:
        return asset(name)
    return cached(('dof', name, lv), lambda: blur_sprite(asset(name), lv))


def coin(sym, d=300):
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32)
    r = np.sqrt((xx - d / 2 + .5) ** 2 + (yy - d / 2 + .5) ** 2)
    disc = np.clip(d / 2 - 2 - r, 0, 1)
    rim = np.clip(1 - np.abs(r - d * 0.41) / (d * 0.025), 0, 1)
    t = ((xx + yy) / (2 * d))[..., None]
    rgb = np.array([1.0, 0.86, 0.32]) * (1 - t) + np.array([0.86, 0.52, 0.02]) * t
    rgb = rgb * (1 - 0.18 * rim[..., None])
    spec = np.exp(-(((xx - d * 0.36) / (d * 0.18)) ** 2 + ((yy - d * 0.3) / (d * 0.1)) ** 2))[..., None]
    rgb = np.clip(rgb + spec * 0.35, 0, 1)
    spr = np.concatenate([rgb * disc[..., None], disc[..., None]], 2).astype(np.float32)
    g = _mask(sym, FK, int(d * 0.62), 1.0, 0)
    gh, gw = g.shape
    lay = np.zeros((d, d), np.float32)
    y0, x0 = (d - gh) // 2, (d - gw) // 2
    lay[y0:y0 + gh, x0:x0 + gw] = g[:min(gh, d - y0), :min(gw, d - x0)]
    spr = over_spr(spr, solid(lay * disc, (0.55, 0.30, 0.0, 0.9)))
    return glowify(spr, GLOW, 14, 0.35)


def bang_sprite():
    """The reference's three yellow glowing exclamation marks."""
    S = 420
    lay = np.zeros((S, S, 4), np.float32)
    for dx, rot, sc in ((-120, -22, 0.8), (0, 0, 1.15), (120, 22, 0.8)):
        g = text('!', int(170 * sc), 'y', glow=0.0, shadow=0)
        h, w = g.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), -rot, 1.0)
        g = cv2.warpAffine(g, M, (w, h))
        x0, y0 = int(S / 2 + dx - w / 2), int(S / 2 - h / 2 + (20 if dx else -10))
        tmp = np.zeros_like(lay)
        tmp[max(0, y0):y0 + h, max(0, x0):x0 + w] = g[max(0, -y0):S - y0, max(0, -x0):S - x0]
        lay = over_spr(lay, tmp)
    return glowify(lay, GLOW, 14, 0.5)


def flag_card(kind, w=300, h=200):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rgb = np.ones((h, w, 3), np.float32) * 0.97
    if kind == 'jp':
        r = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2)
        a = np.clip(h * 0.3 - r, 0, 1)[..., None]
        rgb = rgb * (1 - a) + np.array([0.80, 0.07, 0.15]) * a
    else:
        stripe = (np.floor(yy / (h / 13)) % 2 == 0)[..., None]
        rgb = np.where(stripe, np.array([0.70, 0.13, 0.20]), rgb)
        canton = ((xx < w * 0.42) & (yy < h * 7 / 13))[..., None]
        rgb = np.where(canton, np.array([0.24, 0.23, 0.43]), rgb)
        dots = (((xx % 21) - 10) ** 2 + ((yy % 15) - 7) ** 2 < 6)[..., None] & canton
        rgb = np.where(dots, 0.95, rgb)
    d = rrect_alpha(w, h, 22, 0)
    a = sdf_fill(d)
    spr = np.concatenate([rgb * a[..., None], a[..., None]], 2).astype(np.float32)
    return spr


def cursor_sprite():
    pts = np.array([[0, 0], [0, 60], [15, 46], [26, 70], [36, 66], [25, 43], [45, 43]], np.float32) * 1.6 + 12
    m = np.zeros((140, 110), np.uint8)
    cv2.fillPoly(m, [pts.astype(np.int32)], 255, cv2.LINE_AA)
    o = cv2.dilate(m, np.ones((7, 7), np.uint8))
    a, ao = m.astype(np.float32) / 255, o.astype(np.float32) / 255
    spr = solid(ao, (0.05, 0.05, 0.05, 1))
    spr = over_spr(spr, solid(a, (1, 1, 1, 1)))
    sh = cv2.GaussianBlur(np.roll(ao, 6, 0), (0, 0), 5) * 0.45
    return over_spr(solid(sh, (0, 0, 0, 1)), spr)


def card(w, h, rows, accent=None, radius=34, fill=(0.09, 0.10, 0.13, 0.82), border=(1, 1, 1, 0.16)):
    """Glass card. rows: list of (sprite, x, y) placed relative to card centre."""
    P = 40
    d = rrect_alpha(w, h, radius, P)
    body = sdf_fill(d)
    hh, ww = body.shape
    t = np.linspace(0, 1, hh, dtype=np.float32)[:, None, None]
    rgb = np.array(fill[:3], np.float32) * (1.15 - 0.3 * t)
    spr = np.concatenate([rgb * body[..., None] * fill[3], body[..., None] * fill[3]], 2).astype(np.float32)
    spr = over_spr(spr, solid(sdf_stroke(d, 2.0), border))
    if accent is not None:
        g = cv2.GaussianBlur(sdf_stroke(d, 3.0), (0, 0), 14) * 0.9
        gl = np.zeros_like(spr)
        gl[..., :3] = np.array(accent, np.float32) * g[..., None]
        spr = spr + gl
        spr = over_spr(spr, solid(sdf_stroke(d, 2.4), accent + (0.9,)))
    for s, x, y in rows:
        sh, sw = s.shape[:2]
        x0, y0 = int(ww / 2 + x - sw / 2), int(hh / 2 + y - sh / 2)
        tmp = np.zeros_like(spr)
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(ww, x0 + sw), min(hh, y0 + sh)
        tmp[Y0:Y1, X0:X1] = s[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
        spr = over_spr(spr, tmp)
    return spr


_cards = {}


def cached(key, fn):
    if key not in _cards:
        _cards[key] = fn()
    return _cards[key]


# ====================================================================== animation helpers

_draw, _draw3d = draw, draw3d


def _blurred(spr, blur):
    lv = round(blur * 2) / 2
    if lv < 0.75:
        return spr
    key = (id(spr), lv)
    b = _blur_cache.get(key)
    if b is None or b[0] is not spr:
        if len(_blur_cache) > 300:
            _blur_cache.clear()
        b = (spr, blur_sprite(spr, lv))
        _blur_cache[key] = b
    return b[1]


_blur_cache = {}


def draw(canvas, spr, cx, cy, scale=1.0, rot=0.0, opacity=1.0, mode='over', ax=0.5, ay=0.5, blur=0.0):
    """engine.draw + optional defocus/motion softness (padding is symmetric, so the centre holds)."""
    return _draw(canvas, _blurred(spr, blur), cx, cy, scale, rot, opacity, mode, ax, ay)


def draw3d(canvas, spr, cx, cy, cz=0, w=None, h=None, rx=0, ry=0, rz=0, cam=None, opacity=1.0, mode='over', blur=0.0):
    b = _blurred(spr, blur)
    if b is not spr:
        if w is not None:
            w = w * b.shape[1] / spr.shape[1]
        if h is not None:
            h = h * b.shape[0] / spr.shape[0]
    return _draw3d(canvas, b, cx, cy, cz, w, h, rx, ry, rz, cam, opacity, mode)


def pblur(t, t0, dur=0.28, amt=10.0):
    """Blur-in: elements resolve from soft to sharp as they arrive."""
    return amt * (1 - e_out_cubic(prog(t, t0, t0 + dur)))


def sheen(spr, t, t0, dur=0.55, strength=0.55, width=0.10):
    """A diagonal light sweep across a sprite (masked by its alpha) — glossy 'AE' highlight pass."""
    p = prog(t, t0, t0 + dur)
    if p <= 0 or p >= 1:
        return spr
    h, w = spr.shape[:2]
    xs = np.arange(w, dtype=np.float32)[None, :] / w
    ys = np.arange(h, dtype=np.float32)[:, None] / max(h, w)
    pos = -0.35 + 1.7 * e_inout_cubic(p)
    band = np.exp(-((xs - ys * 0.6 - pos) / width) ** 2) * strength
    out = spr.copy()
    out[..., :3] += band[..., None] * spr[..., 3:4]
    return out

def popv(t, t0, dur=0.36):
    """(scale, opacity) for a pop-in that overshoots like the reference's captions."""
    p = prog(t, t0, t0 + dur)
    if p <= 0:
        return 0.0, 0.0
    return e_out_back(p, 1.1), smooth(min(1.0, p * 2.2))


def fly(t, t0, dur=0.5):
    return e_out_expo(prog(t, t0, t0 + dur))


def shake(t, t0, amp=18, dur=0.35, seed=1):
    p = prog(t, t0, t0 + dur)
    if p <= 0 or p >= 1:
        return 0.0, 0.0
    k = (1 - p) ** 2 * amp
    return k * math.sin(t * 97 + seed), k * math.cos(t * 83 + seed * 2)


# ====================================================================== edit plan

# graphic (3D cutaway) segments; everything else is the talent
G_SEGS = [
    (6.06, 9.55, 'connect'), (13.55, 16.35, 'yields'), (23.85, 31.45, 'carry'), (33.95, 41.40, 'trillion'),
    (43.40, 48.95, 'since1996'), (56.15, 60.95, 'flowback'), (60.95, 67.45, 'impact'), (67.45, 71.65, 'commod'),
    (82.50, 85.55, 'opps'),
]
# talent shots: (start, zoom) — jump-cut punch-ins between medium and close, slow push inside each
T_SHOTS = [(0.0, 1.42), (2.94, 2.05), (9.55, 1.55), (11.84, 2.0), (16.35, 1.38), (18.80, 1.9), (20.84, 1.5),
           (31.45, 1.95), (41.40, 2.15), (48.95, 1.5), (51.30, 1.75), (54.32, 2.1), (71.65, 1.45), (73.76, 1.95),
           (76.84, 1.55), (79.66, 1.9), (85.55, 1.5), (87.48, 1.95)]

# kinetic 3D type stacks over the talent: (t0, t1, cx, cy, ry, rz, [(text, time, style, size, align)])
STACKS = [
    (0.0, 2.94, 390, 720, 16, -6, [('Agar aap', 0.0, 'w', 78, 'l'), ('GOLD,', 0.66, 'y', 170, 'l'),
                                  ('DOLLAR', 1.10, 'y', 150, 'r'), ('ya Global', 1.46, 'w', 84, 'l'),
                                  ('MARKETS', 1.96, 'y', 132, 'l'), ('trade karte hain?', 2.36, 'w', 64, 'l')]),
    (20.84, 23.85, 380, 760, 16, -6, [('Kaafi arsay tak', 20.84, 'w', 72, 'l'), ('Japan mein', 21.62, 'w', 84, 'l'),
                                     ('INTEREST', 22.18, 'y', 140, 'l'), ('RATES', 22.52, 'y', 170, 'r'),
                                     ('bohot kam rahe.', 22.82, 'w', 70, 'l')]),
    (31.45, 33.95, 380, 760, 14, -6, [('Is strategy ko', 31.66, 'w', 74, 'l'), ('YEN', 32.56, 'y', 250, 'l'),
                                     ('CARRY TRADE', 32.88, 'y', 118, 'l'), ('kehte hain.', 33.34, 'w', 76, 'r')]),
    (41.40, 43.40, 380, 760, 16, -6, [('Lekin ab', 41.48, 'w', 86, 'l'), ('SITUATION', 41.96, 'y', 138, 'l'),
                                     ('CHANGE', 42.34, 'y', 170, 'r'), ('ho rahi hai.', 42.78, 'w', 76, 'l')]),
    (51.30, 54.32, 380, 760, 16, -6, [('Agar Japan mein', 51.30, 'w', 70, 'l'), ('RATES', 51.98, 'y', 170, 'l'),
                                     ('BARHNE', 52.22, 'y', 130, 'r'), ('ki expectations', 52.66, 'w', 70, 'l'),
                                     ('aur mazboot hon,', 53.16, 'w', 70, 'l')]),
    (54.32, 56.15, 380, 760, 16, -6, [('to carry trade', 54.32, 'w', 80, 'l'), ('UNWIND', 54.90, 'y', 200, 'l'),
                                     ('ho sakti hai.', 55.28, 'w', 80, 'r')]),
    (79.66, 82.50, 380, 760, 16, -6, [('Japan ke', 79.66, 'w', 84, 'l'), ('BOND YIELDS', 80.26, 'y', 124, 'l'),
                                     ('aur YEN', 80.78, 'y', 150, 'r'), ('par bhi nazar', 81.24, 'w', 74, 'l'),
                                     ('ZAROORI', 81.90, 'y', 150, 'l')]),
]

CUTS = sorted(set([g[0] for g in G_SEGS] + [g[1] for g in G_SEGS]))


def seg_at(t):
    for a, b, name in G_SEGS:
        if a <= t < b:
            return ('G', a, b, name)
    a = max([s for s, _ in T_SHOTS if s <= t] + [0])
    return ('T', a, None, None)


# ====================================================================== talent plate

_dv = {}


def devignette_gain():
    if 'g' not in _dv:
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xs - W / 2) / (W * 0.62)) ** 2 + ((ys - H * 0.47) / (H * 0.6)) ** 2)
        g = (1 + 0.35 * np.clip(r - 0.45, 0, None) ** 1.6 * 2.2) ** 0.45
        # subject power-window: gently darken the set away from the talent so she separates from the wall
        fx, fy = FACE['median'][0], FACE['median'][1]
        rw = np.sqrt(((xs - (fx - 30)) / (W * 0.55)) ** 2 + ((ys - (fy + 360)) / (H * 0.62)) ** 2)
        g = g * (1 - 0.20 * np.clip((rw - 0.55) / 0.6, 0, 1) ** 1.5)
        _dv['g'] = g[..., None].astype(np.float32)
    return _dv['g']


def face_at(fi):
    tr = FACE['track'][min(max(fi, 0), NFR - 1)]
    return tr[0], tr[1], tr[2]


# smooth camera zoom moves on the talent: (start, duration, from, to). Zoom-outs open a shot
# (start tight, pull back); zoom-ins land on the emphasis word.
ZOOM_MOVES = [
    (2.50, 0.44, 1.00, 1.14),   # hook stack exits: push in, type falls out of focus
    (4.70, 0.40, 1.00, 1.16),   # lands for "important"
    (9.55, 0.80, 1.28, 1.00),   # pull out
    (12.55, 0.70, 1.00, 1.10),
    (16.35, 0.75, 1.30, 1.00),  # pull out
    (18.70, 0.40, 1.00, 1.12),  # lands for "behtar returns"
    (23.20, 0.50, 1.00, 1.15),  # stack exits
    (31.45, 0.55, 1.22, 1.00),  # pull out into YEN CARRY TRADE
    (41.40, 0.65, 1.25, 1.00),  # pull out
    (48.95, 0.80, 1.30, 1.00),  # pull out
    (49.30, 0.40, 1.00, 1.10),  # lands for "strong"
    (53.75, 0.50, 1.00, 1.10),  # stack exits
    (55.35, 0.50, 1.00, 1.14),  # UNWIND stack exits
    (71.65, 0.80, 1.30, 1.00),  # pull out
    (74.25, 0.40, 1.00, 1.16),  # lands for "volatility"
    (76.84, 0.75, 1.25, 1.00),  # pull out
    (82.05, 0.42, 1.00, 1.12),  # stack exits
    (85.55, 0.80, 1.30, 1.00),  # pull out
]
Z_MAX = 2.45  # keep the up-scale of the 1080p plate modest so the host stays crisp


def _shot_start(t):
    return max([s for s, _ in T_SHOTS if s <= t] + [x for x in CUTS if x <= t] + [0.0])


def zoom_mult(t):
    st = _shot_start(t)
    mv = [m for m in ZOOM_MOVES if st - 1e-6 <= m[0] <= t]
    if not mv:
        return 1.0
    t0, d, m0, m1 = mv[-1]
    p = prog(t, t0, t0 + d)
    e = e_out_cubic(p) if m1 < m0 else e_inout_cubic(p)
    return lerp(m0, m1, e)


def zoom_at(t):
    a, z = max([(s, z) for s, z in T_SHOTS if s <= t] + [(0.0, 1.42)])
    nxt = min([s for s, _ in T_SHOTS if s > t] + [x for x in CUTS if x > t] + [DUR])
    push = 1 + 0.035 * smooth(prog(t, a, nxt))
    return min(Z_MAX, z * push * zoom_mult(t) * transition(t)[0]), a


def crop_box(t, fi):
    z, shot_t = zoom_at(t)
    fx, fy, fw = face_at(fi)
    cw, ch = W / z, H / z
    # keep her face at ~56% across and ~30% (medium) .. 34% (close) down the frame
    rel_y = lerp(0.29, 0.35, clamp((z - 1.4) / 0.8))
    cx = fx - (0.56 - 0.5) * cw
    cy = fy + (0.5 - rel_y) * ch
    cx = clamp(cx, cw / 2, W - cw / 2)
    cy = clamp(cy, ch / 2, H - ch / 2)
    return cx, cy, cw, ch, z


def talent(frame_bgr, t, fi, sdx=0.0, sdy=0.0):
    img = frame_bgr.astype(np.float32) * (1 / 255.0)
    img = img * devignette_gain()
    cx, cy, cw, ch, z = crop_box(t, fi)
    cx -= sdx * cw / W
    cy -= sdy * cw / W
    sx = W / cw
    M = np.float32([[sx, 0, -(cx - cw / 2) * sx], [0, sx, -(cy - ch / 2) * sx]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    # sharpen: stronger when punched in (up-scaled)
    amt = 0.40 + 0.25 * clamp((z - 1.2) / 1.0)
    bl = cv2.GaussianBlur(out, (0, 0), 1.0 + 0.35 * (z - 1))
    out = out + amt * (out - bl)
    bl2 = cv2.GaussianBlur(out, (0, 0), 6)
    out = out + 0.12 * (out - bl2)  # local contrast / clarity
    return np.clip(out[..., ::-1], 0, 1), (cx, cy, cw, ch)


def to_screen(px, py, box):
    cx, cy, cw, ch = box
    return (px - (cx - cw / 2)) * W / cw, (py - (cy - ch / 2)) * H / ch


# ====================================================================== captions

KEY_Y = {'important', '360', 'trillion', '2.34', '1996', '3%', 'unwind', 'volatility', 'floret capitals',
         'opportunities', 'risks', 'strong', 'pressure', 'demand'}


def _n(w):
    return w.lower().strip('.,:;?!()')


def build_chunks():
    ch, i = [], 0
    while i < len(WORDS):
        grp = [WORDS[i]]
        if len(_n(WORDS[i]['w'])) <= 3 and i + 1 < len(WORDS) and len(WORDS[i]['w'] + WORDS[i + 1]['w']) <= 11 \
                and WORDS[i + 1]['s'] - WORDS[i]['e'] < 0.35:
            grp.append(WORDS[i + 1])
        i += len(grp)
        txt = ' '.join(g['w'] for g in grp).strip('()').replace('(', '').replace(')', '')
        ch.append(dict(txt=txt, s=grp[0]['s'], e=grp[-1]['e']))
    for k in range(len(ch)):
        nxt = ch[k + 1]['s'] if k + 1 < len(ch) else DUR
        ch[k]['end'] = min(nxt, ch[k]['e'] + 0.9)
    return ch


CHUNKS = build_chunks()


def stack_active(t):
    return any(a <= t < b for a, b, *_ in STACKS)


def draw_caption(cv, t, y, fr=None):
    if fr is not None and fr[1] - 60 < y < fr[3] + 70:
        y = fr[3] + 70  # never over the face
    for c in CHUNKS:
        if c['s'] - 0.03 <= t < c['end']:
            yel = any(_n(p) in KEY_Y for p in c['txt'].split()) or _n(c['txt']) in KEY_Y
            size = 112 if len(c['txt']) <= 9 else (100 if len(c['txt']) <= 13 else 86)
            spr = text(c['txt'], size + (14 if yel else 0), 'y' if yel else 'w', fname=FK if yel else FB,
                       squeeze=0.9 if yel else 1.0, glow=0.5 if yel else None)
            e = e_out_cubic(prog(t, c['s'] - 0.04, c['s'] + 0.22))
            out = prog(t, c['end'] - 0.08, c['end'])
            k = CHUNKS.index(c)
            if yel and len(c['txt']) <= 16:
                caption_3d_letters(cv, t, c['s'] - 0.04, c['txt'], size + 14, y, out)
            elif k % 6 == 3:
                caption_3d_flip(cv, t, c['s'] - 0.04, spr, y, out)
            else:
                op = smooth(min(1.0, e * 1.5)) * (1 - out)
                draw(cv, spr, CX, y + 26 * (1 - e) - 10 * out, scale=0.94 + 0.06 * e, opacity=op,
                     blur=9 * (1 - e) + 7 * out)
            return


_adv = {}


def _char_layout(txt, size, fname, squeeze):
    """Glyph centres along the word using the font's own advances (with the word sprites' tight tracking)."""
    key = (txt, size, fname, squeeze)
    if key not in _adv:
        f = E.font(fname, size)
        tr = -0.02 * size
        xs = [(f.getlength(txt[:i]) + i * tr + f.getlength(ch) / 2) * squeeze for i, ch in enumerate(txt)]
        _adv[key] = (xs, (f.getlength(txt) + (len(txt) - 1) * tr) * squeeze)
    return _adv[key]


def caption_3d_letters(cv, t, t0, txt, size, y, out):
    """Key words: extruded 3D letters cascade in, each flipping up from its baseline."""
    xs, total = _char_layout(txt, size, FK, 0.9)
    x0 = CX - total / 2
    for i, ch in enumerate(txt):
        if ch == ' ':
            continue
        ti = t0 + i * 0.03
        p = prog(t, ti, ti + 0.42)
        if p <= 0:
            continue
        e = e_out_back(p, 1.3)
        spr = text('\x00' + ch, size, 'y', fname=FK, squeeze=0.9, glow=0.45, extrude=max(4, size // 14))
        spr = sheen(spr, t, t0 + 0.35 + i * 0.02, 0.45)
        draw3d(cv, spr, x0 + xs[i], y + 30 * (1 - e) - 10 * out, 260 * (1 - min(1, e)) + 60 * out,
               rx=-80 * (1 - e) + 25 * out, ry=0, opacity=smooth(min(1, p * 2.2)) * (1 - out),
               blur=8 * (1 - min(1, e)) + 6 * out)


def caption_3d_flip(cv, t, t0, spr, y, out):
    """Whole word flips in on its horizontal axis, in perspective."""
    p = prog(t, t0, t0 + 0.38)
    e = e_out_back(p, 1.2)
    draw3d(cv, spr, CX, y + 20 * (1 - e), 180 * (1 - min(1, e)), rx=70 * (1 - e) - 20 * out,
           opacity=smooth(min(1, p * 2.0)) * (1 - out), blur=7 * (1 - min(1, e)) + 6 * out)


def face_rect(fi, box):
    """Screen-space rectangle around the talent's head (face + hair + chin) to keep text off."""
    fx, fy, fw = face_at(fi)
    x0, y0 = to_screen(fx - fw * 0.85, fy - fw * 1.0, box)
    x1, y1 = to_screen(fx + fw * 0.85, fy + fw * 1.05, box)
    return x0, y0, x1, y1


def draw_stack(cv, t, st, dx=0, dy=0, fr=None):
    t0, t1, bx, by, ry, rz, lines = st
    out = prog(t, t1 - 0.14, t1)
    ys, y = [], 0
    hs = [text(l[0], l[3], l[2]).shape[0] - 2 * tpad(l[3]) for l in lines]
    for hh, l in zip(hs, lines):
        ys.append(y + hh / 2)
        y += hh + 10 + 0.06 * l[3]
    total = y
    ry, rz = 12, -4  # one consistent tilt for every stack
    R = rotm(0, ry, rz)
    bw = 560
    maxw = max(text(l[0], l[3], l[2]).shape[1] - 2 * tpad(l[3]) for l in lines)
    bx = SAFE['x0'] + 46 + bw / 2  # flush-left on a common margin
    if fr is not None:
        # keep the whole stack clear of the face: drop it below the chin if it would overlap
        top, bot = by - total / 2 - 30, by + total / 2 + 30
        left, right = bx - bw / 2 - 30, bx - bw / 2 + maxw + 30
        if right > fr[0] and left < fr[2] and bot > fr[1] and top < fr[3]:
            by = fr[3] + 40 + total / 2
            by = min(by, SAFE['y1'] - total / 2 - 20)
    for (txt, tw, style, size, align), ly in zip(lines, ys):
        if t < tw - 0.02:
            continue
        spr = text(txt, size, style)
        P = tpad(size)
        w_vis = spr.shape[1] - 2 * P
        lx = -bw / 2 + w_vis / 2  # flush-left
        e = e_out_cubic(prog(t, tw - 0.02, tw + 0.30))
        op = smooth(min(1.0, e * 1.5))
        sc = 1.10 - 0.10 * e if style == 'y' else 1.0  # heavy words settle in from slightly larger
        if style == 'y':
            spr = sheen(spr, t, tw + 0.28, 0.55)
        v = R @ np.array([lx, ly - total / 2 + 34 * (1 - e), 0.0])
        draw3d(cv, spr, bx + dx + v[0], by + dy + v[1], v[2] - 40 * out, w=spr.shape[1] * sc, ry=ry, rz=rz,
               opacity=op * (1 - out), blur=10 * (1 - e) + 8 * out)


# ====================================================================== talent overlays

def face_box(cv, t, fi, box, t0, t1):
    if not (t0 <= t < t1):
        return
    fx, fy, fw = face_at(fi)
    sx, sy = to_screen(fx, fy - fw * 0.05, box)
    s = fw * 1.55 * W / box[2]
    p = e_out_back(prog(t, t0, t0 + 0.25), 2)
    o = 1 - prog(t, t1 - 0.12, t1)
    key = ('fbox',)
    if key not in _cards:
        S = 400
        lay = np.zeros((S + 120, S + 120), np.float32)
        q = 60
        segs = [((q - 18, q), (q + S + 14, q + 4)), ((q + S, q - 14), (q + S - 4, q + S + 18)),
                ((q + S + 16, q + S), (q - 10, q + S - 3)), ((q + 2, q + S + 14), (q - 3, q - 16))]
        for a, b in segs:
            cv2.line(lay, a, b, 1.0, 9, cv2.LINE_AA)
        g = cv2.GaussianBlur(lay, (0, 0), 10)
        spr = solid(lay, YEL + (1,))
        gl = np.zeros_like(spr)
        gl[..., :3] = np.array(GLOW, np.float32) * (g * 1.4)[..., None]
        _cards[key] = spr + gl
    spr = _cards[key]
    draw(cv, spr, sx, sy, scale=(s / 400) * (1.25 - 0.25 * p), opacity=o * min(1, p * 3))


def bang(cv, t, fi, box, t0, t1):
    if not (t0 <= t < t1):
        return
    fx, fy, fw = face_at(fi)
    sx, sy = to_screen(fx, fy - fw * 1.2, box)
    sc, op = popv(t, t0, 0.3)
    wob = math.sin((t - t0) * 9) * 4 * (1 - prog(t, t0, t0 + 0.8))
    o = 1 - prog(t, t1 - 0.12, t1)
    draw(cv, asset('bang'), sx, sy, scale=0.8 * sc * (W / box[2]) / 1.9, rot=wob, opacity=op * o)


def icon_pop(cv, t, name, x, y, t0, t1, scale=1.0, rot=0.0, bob=True):
    if not (t0 <= t < t1):
        return
    sc, op = popv(t, t0, 0.32)
    o = 1 - prog(t, t1 - 0.12, t1)
    yb = math.sin((t - t0) * 3.2) * 8 if bob else 0
    draw(cv, asset(name), x, y + yb, scale=scale * sc, rot=rot, opacity=op * o)


def cta(cv, t):
    t0 = 87.48
    if t < t0:
        return
    k = fly(t, t0, 0.55)
    avatar = cached('avatar', lambda: _avatar())
    clicked = t >= 88.62
    def mk(clicked):
        btn_txt = text('Following' if clicked else 'Follow', 54, 'd' if not clicked else 'w', fname=FX, shadow=0)
        bw, bh = 300, 96
        d = rrect_alpha(bw, bh, 48, 20)
        bf = solid(sdf_fill(d), (YEL + (1,)) if not clicked else (0.25, 0.27, 0.32, 1))
        bf = over_spr(bf, _center(btn_txt, bf.shape))
        name = text('Floret Capitals', 66, 'w', fname=FX, shadow=0)
        handle = text('@floretcapitals', 40, 'w', fname=FB, shadow=0) * 0.7
        return card(860, 300, [(avatar, -300, 0), (name, 90, -62), (handle, 30, -4), (bf, 60, 84)], accent=YEL)
    spr = cached(('cta', clicked), lambda: mk(clicked))
    ry = lerp(-35, -8, k) + math.sin(t * 1.3) * 2
    cy = lerp(2150, 1250, k)
    sc = 1.0 - 0.06 * max(0, 1 - abs(t - 88.66) / 0.1) if t > 88.5 else 1.0
    draw3d(cv, spr, CX - 30, cy, 0, w=spr.shape[1] * sc * 0.95, rx=6, ry=ry, rz=-2)
    # cursor travels to the button and clicks
    if t >= 87.9:
        p = e_inout_cubic(prog(t, 87.9, 88.55))
        x, y = lerp(980, CX + 60, p), lerp(1900, cy + 92, p)
        press = 0.88 if 88.55 <= t < 88.72 else 1.0
        draw(cv, asset('cursor'), x + 30, y + 40, scale=press, opacity=min(1, (t - 87.9) * 6))
        if t >= 88.6:
            r = prog(t, 88.6, 89.0)
            ring = cached('ring', lambda: E.ring_sprite(260, 100, 6, YEL))
            draw(cv, ring, CX + 60, cy + 92, scale=0.4 + r * 1.2, opacity=(1 - r) * 0.9, mode='add')


def _center(s, shape):
    tmp = np.zeros(shape, np.float32)
    h, w = s.shape[:2]
    y0, x0 = (shape[0] - h) // 2, (shape[1] - w) // 2
    tmp[max(0, y0):y0 + h, max(0, x0):x0 + w] = s[max(0, -y0):shape[0] - y0, max(0, -x0):shape[1] - x0]
    return tmp


def _avatar():
    """Floret Capitals profile picture: their logo on a white disc, with the yellow ring."""
    d = 200
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32)
    r = np.sqrt((xx - d / 2) ** 2 + (yy - d / 2) ** 2)
    a = np.clip(d / 2 - 1 - r, 0, 1)
    ring = np.clip(1 - np.abs(r - (d / 2 - 5)) / 3.5, 0, 1)
    spr = solid(a, (1, 1, 1, 1))
    im = cv2.imread(f'{WORK}/src/floret_logo.png', cv2.IMREAD_UNCHANGED)
    if im.shape[2] == 3:
        im = np.concatenate([im, np.full(im.shape[:2] + (1,), 255, np.uint8)], 2)
    ink = (im[..., 3] > 8) & (im[..., :3].min(2) < 235)  # logo marks, not the white/transparent ground
    ys, xs = np.where(ink)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = d * 0.60 / max(im.shape[:2])
    im = cv2.resize(im, (int(im.shape[1] * sc), int(im.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    logo = E.to_premul(im[..., [2, 1, 0, 3]])
    spr = over_spr(spr, _center(logo, spr.shape) * a[..., None])
    spr = over_spr(spr, solid(ring, YEL + (1,)))
    return spr


# ====================================================================== 3D-space backdrop

_bg = {}


def backdrop(cam, t):
    if 'grad' not in _bg:
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
        tt = ys / H
        base = np.array([0.035, 0.040, 0.055]) * (1 - tt[..., None]) + np.array([0.075, 0.08, 0.10]) * tt[..., None]
        r = np.sqrt(((xs - CX) / 700) ** 2 + ((ys - 820) / 900) ** 2)
        spot = np.exp(-r ** 2 * 1.6)[..., None] * np.array([0.16, 0.11, 0.035])
        vig = np.clip(1 - 0.5 * (((xs - CX) / (W * 0.7)) ** 2 + ((ys - CY) / (H * 0.62)) ** 2), 0.3, 1)[..., None]
        _bg['grad'] = ((base + spot) * vig).astype(np.float32)
        _bg['fade'] = np.clip((ys - 900) / 1000, 0, 1).astype(np.float32)[..., None]
        rng = np.random.default_rng(3)
        _bg['dust'] = np.stack([rng.uniform(-1800, 2900, 70), rng.uniform(-400, 2200, 70), rng.uniform(-300, 2600, 70)], 1)
        _bg['dot'] = radial_sprite(24, (1, 0.8, 0.45), 2.2)
    cv = _bg['grad'].copy()
    # perspective grid floor
    lay = np.zeros((H, W), np.float32)
    FY = 1650
    xs = np.arange(-2600, 4600, 220)
    zs = np.arange(-400, 5200, 220)
    for x in xs:
        p, ok = project_pts([[x, FY, zs[0]], [x, FY, zs[-1]]], cam)
        cv2.line(lay, tuple(np.int32(p[0])), tuple(np.int32(p[1])), 0.55, 1, cv2.LINE_AA)
    for z in zs:
        p, ok = project_pts([[xs[0], FY, z], [xs[-1], FY, z]], cam)
        if ok:
            cv2.line(lay, tuple(np.int32(p[0])), tuple(np.int32(p[1])), 0.55, 1, cv2.LINE_AA)
    cv += (lay[..., None] * _bg['fade'] * np.array([0.55, 0.45, 0.25], np.float32) * 0.5)
    # floating dust in depth
    for i, (x, y, z) in enumerate(_bg['dust']):
        yy = y - (t * 22 + i * 37) % 600
        p, ok = project_pts([[x, yy, z]], cam)
        if ok:
            s = 1500 / (1500 + z - cam.z + 1e-3)
            draw(cv, _bg['dot'], p[0][0], p[0][1], scale=max(0.15, s * 0.8), opacity=0.35, mode='add')
    return cv


def light_line(cv, pts, color, width=6, glow=18, opacity=1.0):
    lay = np.zeros((H, W), np.float32)
    pts = np.int32(np.round(pts))
    cv2.polylines(lay, [pts], False, 1.0, width, cv2.LINE_AA)
    g = cv2.GaussianBlur(lay, (0, 0), glow)
    c = np.array(color, np.float32)
    cv[:] = cv * (1 - lay[..., None] * opacity) + lay[..., None] * c * opacity + g[..., None] * c * 1.3 * opacity


def lbl(txt, size, style='w'):
    return text(txt, size, style, shadow=0.4)


# ====================================================================== 3D scenes

def sc_connect(cv, t, a, b, cam):
    jp = cached('c_jp', lambda: card(420, 470, [(asset('jp'), 0, -60), (lbl('JAPAN', 74, 'w'), 0, 150)]))
    us = cached('c_us', lambda: card(500, 470, [(asset('us'), 0, -60), (lbl('U.S. TREASURY', 64, 'w'), 0, 150)]))
    k1, k2 = fly(t, 6.06, 0.6), fly(t, 6.70, 0.6)
    pa = (300, 680, lerp(900, 0, k1))
    pb = (760, 1060, lerp(900, 0, k2))
    qa = draw3d(cv, jp, pa[0], pa[1], pa[2], ry=lerp(60, 18, k1), rz=-3, cam=cam, opacity=min(1, k1 * 2))
    lp = prog(t, 6.40, 7.3)
    if lp > 0 and k2 > 0.3:
        A = np.array(project_pts([[pa[0] + 160, pa[1] + 120, pa[2]]], cam)[0][0])
        B = np.array(project_pts([[pb[0] - 190, pb[1] - 150, pb[2]]], cam)[0][0])
        C = (A + B) / 2 + np.array([160, -60])
        ts = np.linspace(0, e_out_cubic(lp), 60)[:, None]
        pts = (1 - ts) ** 2 * A + 2 * (1 - ts) * ts * C + ts ** 2 * B
        light_line(cv, pts, YEL, 6, 16)
        if lp >= 1:
            for k in range(3):
                u = ((t - 7.3) * 0.9 + k / 3) % 1
                P = (1 - u) ** 2 * A + 2 * (1 - u) * u * C + u ** 2 * B
                draw(cv, cached('pulse', lambda: radial_sprite(90, YEL, 1.6, 1.0)), P[0], P[1], mode='add')
    draw3d(cv, us, pb[0], pb[1], pb[2], ry=lerp(-60, -16, k2), rz=3, cam=cam, opacity=min(1, k2 * 2))
    if t >= 7.58:
        sc, op = popv(t, 7.58, 0.35)
        _pb = pblur(t, 7.58)
        q = text('?', 300, 'y')
        draw3d(cv, q, 800, 470, -80, w=q.shape[1] * sc, ry=-14, rz=8, cam=cam, opacity=op, blur=_pb)


def sc_yields(cv, t, a, b, cam):
    W2, H2 = 900, 700
    def mk_frame():
        rows = [(lbl('JAPAN GOVT BOND YIELDS', 44, 'w'), -110, -290)]
        return card(W2, H2, rows, accent=None)
    fr = cached('y_card', mk_frame)
    k = fly(t, 13.62, 0.6)
    ry, rx = lerp(40, -12, k), 10
    cx, cy, cz = 540, 900, lerp(700, 0, k)
    q = draw3d(cv, fr, cx, cy, cz, rx=rx, ry=ry, cam=cam, opacity=min(1, k * 2))
    # chart drawn in the card's plane
    lp = e_inout_cubic(prog(t, 14.08, 15.9))
    if lp > 0:
        xs = np.linspace(-360, 360, 80)
        base = 0.08 + 0.92 * ((xs + 360) / 720) ** 2.6
        noise = np.sin(xs * 0.05) * 0.03 + np.sin(xs * 0.13) * 0.02
        ys = 220 - (base + noise) * 400
        n = max(2, int(len(xs) * lp))
        R = rotm(rx, ry, 0)
        P = np.stack([xs[:n], ys[:n], np.zeros(n)], 1) @ R.T + np.array([cx, cy, cz])
        pts, ok = project_pts(P, cam)
        # area fill
        Pb = np.stack([xs[:n], np.full(n, 230.0), np.zeros(n)], 1) @ R.T + np.array([cx, cy, cz])
        bpts, _ = project_pts(Pb, cam)
        poly = np.concatenate([pts, bpts[::-1]], 0)
        lay = np.zeros((H, W), np.float32)
        cv2.fillPoly(lay, [np.int32(poly)], 0.22, cv2.LINE_AA)
        cv[:] = cv + lay[..., None] * np.array(YEL, np.float32) * 0.8
        light_line(cv, pts, YEL, 7, 14)
        draw(cv, cached('pulse', lambda: radial_sprite(90, YEL, 1.6, 1.0)), pts[-1][0], pts[-1][1], mode='add')
        if t >= 15.64:
            sc, op = popv(t, 15.64, 0.3)
            _pb = pblur(t, 15.64)
            draw(cv, asset('up_g'), pts[-1][0] - 40, pts[-1][1] - 30, scale=0.9 * sc, opacity=op, blur=_pb)
            u = text('YIELDS ↑', 92, 'g', fname=FK)
            draw(cv, u, 500, 430, scale=0.8 + 0.2 * sc, opacity=op, blur=_pb)


def sc_carry(cv, t, a, b, cam):
    stations = [(540, 'coin_yen', 'YEN', 'SASTA QARZ', 25.02, 25.48),
                (1440, 'coin_usd', 'U.S. BONDS', '', 26.34, None),
                (2340, None, 'GLOBAL ASSETS', 'ZYADA MUNAFA', 29.62, 28.48)]
    for i, (x, ic, title, sub, tt, ts) in enumerate(stations):
        t_on = min(tt, ts or tt) if i else 24.0
        if t < t_on - 0.4:
            continue
        k = fly(t, t_on - 0.4, 0.7)
        y = 860
        if ic:
            coin_s = asset(ic)
            spin = math.cos((t - t_on) * 2.4) * 35
            draw3d(cv, coin_s, x, y, lerp(800, 0, k), w=380, ry=spin, cam=cam, opacity=min(1, 2 * k))
        else:
            pie = cached('assets_card', lambda: card(520, 420, [(lbl('STOCKS', 46), 0, -110), (lbl('BONDS', 46), 0, -30),
                                                                (lbl('REAL ESTATE', 46), 0, 50), (lbl('EMERGING MKTS', 40), 0, 125)],
                                                     accent=GREEN))
            draw3d(cv, pie, x, y, lerp(800, 0, k), ry=-10, cam=cam, opacity=min(1, 2 * k))
        if t >= tt - 0.05:
            sc, op = popv(t, tt - 0.05, 0.3)
            _pb = pblur(t, tt - 0.05)
            s = text(title, 104 if len(title) < 8 else 84, 'y')
            draw3d(cv, s, x, y + 330, 0, w=s.shape[1] * sc, cam=cam, opacity=op, blur=_pb)
        if sub and ts and t >= ts:
            sc, op = popv(t, ts, 0.3)
            _pb = pblur(t, ts)
            s = text(sub, 66, 'w' if i == 0 else 'g', fname=FK)
            draw3d(cv, s, x, y - 330, 0, w=s.shape[1] * sc, cam=cam, opacity=op, blur=_pb)
            if i == 2:
                draw3d(cv, asset('up_g'), x + 300, y - 330, 0, w=90 * sc, cam=cam, opacity=op, blur=_pb)
    # animated dashed flow arrows between stations
    for x0, x1, tt in ((540 + 230, 1440 - 230, 25.9), (1440 + 230, 2340 - 300, 27.0)):
        p = e_out_cubic(prog(t, tt, tt + 0.7))
        if p <= 0:
            continue
        xs = np.linspace(x0, x0 + (x1 - x0) * p, 40)
        P = np.stack([xs, np.full_like(xs, 860.0), np.zeros_like(xs)], 1)
        pts, ok = project_pts(P, cam)
        light_line(cv, pts, YEL, 5, 12, 0.8)
        for k in range(4):
            u = ((t - tt) * 0.8 + k / 4) % 1
            if u < p:
                q, _ = project_pts([[x0 + (x1 - x0) * u, 860, 0]], cam)
                draw(cv, cached('chev', lambda: text('›', 120, 'y', glow=0.6, shadow=0)), q[0][0], q[0][1] - 6)
    if t >= 30.52:
        sc, op = popv(t, 30.52, 0.3)
        _pb = pblur(t, 30.52)
        s = text('INVEST', 150, 'y')
        draw3d(cv, s, 1440, 400, -300, w=s.shape[1] * sc, cam=cam, opacity=op, blur=_pb)


def cam_carry(t):
    x = 900 * e_inout_cubic(prog(t, 25.7, 26.6)) + 900 * e_inout_cubic(prog(t, 27.2, 28.3))
    r = e_inout_cubic(prog(t, 29.9, 31.0))
    # wide 3D reveal: swing round so the three stations recede diagonally into depth
    return Cam(x + 420 * r, -60 * r, 60 * (t - 23.85) / 7 - 1450 * r, 6 * r, 4 * math.sin(t * 0.7) - 34 * r, 0)


def sc_trillion(cv, t, a, b, cam):
    rng = np.random.default_rng(11)
    for i in range(18):
        x, y = rng.uniform(-200, 1280), rng.uniform(150, 1800)
        z0 = rng.uniform(300, 2800)
        z = z0 - ((t - a) * 260 + i * 140) % 2800
        if z < -900:
            continue
        spin = (t * 70 + i * 40) % 360
        draw3d(cv, dof_sprite('coin_yen', z + 400 - cam.z, 300), x, y, z + 400, w=200, ry=spin * 0.5 - 40, rx=20, cam=cam,
               opacity=clamp(prog(t, a, a + 0.5)) * 0.8)
    if t >= 35.80:
        sc, op = popv(t, 35.80, 0.3)
        _pb = pblur(t, 35.80)
        s = text('CROSS-BORDER YEN BORROWING', 54, 'w', fname=FX)
        draw3d(cv, s, CX, 640, 0, w=s.shape[1] * sc, rx=8, cam=cam, opacity=op * (1 - prog(t, 38.9, 39.2)))
    if t >= 37.16:
        v = int(round(360 * e_out_expo(prog(t, 37.16, 37.9))))
        sc, op = popv(t, 37.16, 0.3)
        _pb = pblur(t, 37.16)
        s = text(f'¥{v}', 330, 'y', extrude=14)
        k = prog(t, 39.1, 39.6)
        draw3d(cv, s, CX, 900 - 200 * e_out_cubic(k), 500 * e_out_cubic(k), w=s.shape[1] * sc, rx=6 + 10 * k, ry=-6, cam=cam, opacity=op, blur=_pb)
        if t >= 37.74:
            sc2, op2 = popv(t, 37.74, 0.3)
            _pb2 = pblur(t, 37.74)
            s2 = text('TRILLION', 150, 'y')
            draw3d(cv, s2, CX, 1130 - 200 * e_out_cubic(k), 500 * e_out_cubic(k), w=s2.shape[1] * sc2, rx=6 + 10 * k, ry=-6,
                   cam=cam, opacity=op2, blur=_pb2)
    if t >= 39.28:
        sc, op = popv(t, 39.28, 0.35)
        _pb = pblur(t, 39.28)
        c = cached('usd_card', lambda: card(820, 300, [(text('≈ $2.34 TRILLION', 104, 'g', fname=FK), 0, -30),
                                                        (lbl('U.S. DOLLARS', 50), 0, 90)], accent=GREEN))
        draw3d(cv, c, CX, 1200, 0, w=c.shape[1] * (0.7 + 0.3 * sc), rx=8, ry=8, cam=cam, opacity=op, blur=_pb)


YEARS = list(range(1996, 2027, 2))


def sc_1996(cv, t, a, b, cam):
    # a timeline in 3D space; the camera tracks along it from 1996 to today
    dim = 1 - 0.75 * prog(t, 47.3, 47.6)
    on = clamp(prog(t, 43.4, 43.8))
    x_of = lambda i: 540 + i * 320
    rail, ok = project_pts([[x_of(0) - 400, 1080, 0], [x_of(len(YEARS) - 1) + 400, 1080, 0]], cam)
    light_line(cv, rail, YEL, 5, 12, on * dim)
    for i, y in enumerate(YEARS):
        big = y in (1996, 2026)
        tk, ok = project_pts([[x_of(i), 1050, 0], [x_of(i), 1110, 0]], cam)
        if ok:
            light_line(cv, tk, (1, 1, 1), 3, 4, 0.5 * on * dim)
        s = text(str(y), 190 if big else 96, 'y' if big else 'w', fname=FK)
        draw3d(cv, s, x_of(i), 940 if big else 980, 0, cam=cam, opacity=on * dim * (1 if big else 0.5))
    if t >= 44.62:
        sc, op = popv(t, 44.62, 0.3)
        _pb = pblur(t, 44.62)
        s = text('PEHLI DAFA SINCE 1996', 70, 'w', fname=FX)
        draw(cv, s, CX, 470, scale=sc, opacity=op * (1 - prog(t, 47.3, 47.6)))
    if t >= 46.10:
        sc, op = popv(t, 46.10, 0.3)
        _pb = pblur(t, 46.10)
        c = cached('jgb', lambda: card(900, 170, [(cv2.resize(asset('jp'), (150, 100), interpolation=cv2.INTER_AREA), -340, 0), (lbl('10-YEAR JGB YIELD', 58), 80, 0)]))
        draw(cv, c, CX, 640, scale=0.85 * (0.8 + 0.2 * sc), opacity=op, blur=_pb)
    if t >= 47.50:
        p = prog(t, 47.50, 47.68)
        sc, op = 1.6 - 0.6 * e_out_cubic(p), min(1, p * 4)
        s = text('3%', 460, 'y', extrude=18)
        dx, dy = shake(t, 47.68, 22)
        draw(cv, s, CX - 50 + dx, 1080 + dy, scale=sc, opacity=op, blur=_pb)
        draw(cv, asset('up_g'), CX + 320 + dx, 1020 + dy, scale=1.1 * min(1, sc), opacity=op, blur=_pb)


def cam_1996(t):
    p = e_inout_cubic(prog(t, 44.0, 46.4))
    return Cam((len(YEARS) - 1) * 320 * p, 0, -500 + 200 * p, 8, -24 + 10 * math.sin(t * 0.5), 0)


def sc_flowback(cv, t, a, b, cam):
    fi = cached('foreign', lambda: card(500, 420, [(asset('coin_usd'), 0, -60), (lbl('FOREIGN', 56), 0, 110),
                                                    (lbl('INVESTMENTS', 56), 0, 170)]))
    jp = cached('c_jp2', lambda: card(440, 420, [(asset('jp'), 0, -40), (lbl('JAPAN', 70), 0, 140)], accent=YEL))
    k1 = fly(t, 57.3, 0.6)
    draw3d(cv, fi, 300, 700, lerp(800, 0, k1), ry=24, cam=cam, opacity=min(1, 2 * k1))
    if t >= 58.42:
        sc, op = popv(t, 58.42, 0.3)
        _pb = pblur(t, 58.42)
        draw3d(cv, asset('down_r'), 520, 560, -60, w=110 * sc, cam=cam, opacity=op, blur=_pb)
        s = text('KAM', 96, 'r', fname=FK)
        draw3d(cv, s, 300, 420, 0, w=s.shape[1] * sc, cam=cam, opacity=op, blur=_pb)
    k2 = fly(t, 59.2, 0.6)
    draw3d(cv, jp, 760, 1130, lerp(800, 0, k2), ry=-24, cam=cam, opacity=min(1, 2 * k2))
    if t >= 58.94:
        A = np.array([420, 880, 0.0]); B = np.array([700, 1030, 0.0]); C = np.array([880, 780, -300.0])
        for k in range(10):
            u = ((t - 58.94) * 0.7 + k / 10) % 1
            P = (1 - u) ** 2 * A + 2 * (1 - u) * u * C + u ** 2 * B
            draw3d(cv, dof_sprite('coin_yen', P[2] - cam.z, 0, 1 / 60.0), P[0], P[1], P[2], w=90 + 40 * math.sin(u * 3.14), ry=(t * 200 + k * 36) % 360,
                   cam=cam, opacity=min(1, (t - 58.94) * 3) * math.sin(u * 3.14) ** 0.5)
    if t >= 59.74:
        sc, op = popv(t, 59.74, 0.3)
        _pb = pblur(t, 59.74)
        s = text('WAPAS', 150, 'y')
        draw3d(cv, s, 300, 1120, 0, w=s.shape[1] * sc * 0.8, ry=14, cam=cam, opacity=op, blur=_pb)


def sc_impact(cv, t, a, b, cam):
    items = [(61.66, 'U.S. TREASURY', 'DEMAND', 'down_r', 'r'), (64.10, 'BOND YIELDS', 'MOVE', 'up_g', 'y'),
             (65.86, 'DOLLAR', 'PRESSURE', 'down_r', 'r')]
    for i, (tt, a1, a2, ic, st) in enumerate(items):
        if t < tt - 0.35:
            continue
        def mk(a1=a1, a2=a2, ic=ic, st=st):
            rows = [(lbl(a1, 60), -40, -48), (text(a2, 86, st, fname=FK), -40, 44), (asset(ic), 330, 0)]
            if ic == 'up_g':
                rows.append((asset('down_r'), 230, 0))
            return card(860, 250, rows, accent=GREEN if st == 'y' else RED)
        c = cached(('imp', i), mk)
        k = fly(t, tt - 0.35, 0.6)
        draw3d(cv, c, CX, 560 + i * 330, lerp(900, 0, k), rx=4, ry=lerp(70, -14, k), cam=cam, opacity=min(1, 2 * k))


def sc_commod(cv, t, a, b, cam):
    k = fly(t, 67.45, 0.6)
    bob = math.sin(t * 2) * 12
    draw3d(cv, asset('gold'), 320, 640 + bob, lerp(900, 0, k), w=520, ry=lerp(40, 10, k), cam=cam, opacity=min(1, 2 * k))
    if t >= 67.52:
        sc, op = popv(t, 67.52, 0.3)
        _pb = pblur(t, 67.52)
        s = text('GOLD', 130, 'y')
        draw3d(cv, s, 320, 930, 0, w=s.shape[1] * sc, cam=cam, opacity=op, blur=_pb)
    if t >= 67.95:
        k2 = fly(t, 67.95, 0.6)
        oil = cached('oil', lambda: card(380, 400, [(_drop(), 0, -50), (lbl('OIL', 90), 0, 120)]))
        draw3d(cv, oil, 770, 700 + bob * 0.6, lerp(900, 0, k2), ry=lerp(-50, -14, k2), cam=cam, opacity=min(1, 2 * k2))
    if t >= 69.24:
        for j, (txt, tt) in enumerate((('DOLLAR', 69.24), ('BOND YIELDS', 69.84))):
            if t >= tt:
                sc, op = popv(t, tt, 0.3)
                _pb = pblur(t, tt)
                p = cached(('chip', txt), lambda txt=txt: card(400 if j == 0 else 520, 120, [(lbl(txt, 56), 0, 0)], radius=60))
                draw3d(cv, p, 300 + j * 450, 1170, 0, w=p.shape[1] * sc * 0.9, rx=6, cam=cam, opacity=op, blur=_pb)
    if t >= 70.40:
        sc, op = popv(t, 70.40, 0.3)
        _pb = pblur(t, 70.40)
        s = text('AHEM FACTORS', 120, 'y')
        draw3d(cv, s, CX, 1300, 0, w=s.shape[1] * sc * 0.9, cam=cam, opacity=op, blur=_pb)


def _drop():
    d = 200
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32)
    cx, cy, r = d / 2, d * 0.62, d * 0.3
    circ = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) < r
    tri = (yy < cy) & (np.abs(xx - cx) < (yy - d * 0.08) / (cy - d * 0.08) * r * 0.97)
    a = cv2.GaussianBlur((circ | tri).astype(np.float32), (0, 0), 1.0)
    t = (yy / d)[..., None]
    rgb = np.array([0.28, 0.30, 0.36]) * (1 - t) + np.array([0.05, 0.05, 0.07]) * t
    spec = np.exp(-(((xx - d * 0.42) / 14) ** 2 + ((yy - d * 0.6) / 26) ** 2))[..., None] * 0.6
    return np.concatenate([np.clip(rgb + spec, 0, 1) * a[..., None], a[..., None]], 2).astype(np.float32)


def sc_opps(cv, t, a, b, cam):
    if t >= 83.24:
        sc, op = popv(t, 83.24, 0.3)
        _pb = pblur(t, 83.24)
        s = text('TRADING', 110, 'w', fname=FK)
        draw3d(cv, s, CX, 470, 0, w=s.shape[1] * sc, cam=cam, opacity=op, blur=_pb)
    for x, tt, txt, ic, col, ry in ((300, 83.52, 'OPPORTUNITIES', 'up_g', GREEN, 22), (760, 84.48, 'RISKS', 'down_r', RED, -22)):
        if t < tt - 0.3:
            continue
        k = fly(t, tt - 0.3, 0.6)
        c = cached(('opp', txt), lambda txt=txt, ic=ic, col=col: card(470, 560, [(asset(ic), 0, -70),
                                                                                 (text(txt, 62 if len(txt) > 6 else 96, 'g' if col == GREEN else 'r', fname=FK), 0, 170)],
                                                                      accent=col))
        draw3d(cv, c, x, 960, lerp(900, 0, k), ry=lerp(ry * 3, ry, k), cam=cam, opacity=min(1, 2 * k))


SCENES = {'connect': sc_connect, 'yields': sc_yields, 'carry': sc_carry, 'trillion': sc_trillion,
          'since1996': sc_1996, 'flowback': sc_flowback, 'impact': sc_impact, 'commod': sc_commod, 'opps': sc_opps}


def scene_cam(name, t, a, b):
    if name == 'carry':
        return cam_carry(t)
    if name == 'since1996':
        return cam_1996(t)
    p = (t - a) / (b - a)
    if name == 'impact':
        return Cam(0, 330 * e_inout_cubic(prog(t, 62.6, 66.4)) - 180, -350 + 250 * p, 0, 6 * math.sin(t * 0.8), 0)
    return Cam(40 * math.sin(t * 0.9), 0, -260 + 300 * p, 0, 7 * math.sin(t * 0.6 + 1), 0)


# ====================================================================== frame

def text_anchor(t):
    """Time the on-screen text was set in focus (start of the current stack / caption)."""
    st = [x for x in STACKS if x[0] <= t < x[1]]
    if st:
        return st[0][0]
    for c in CHUNKS:
        if c['s'] - 0.04 <= t < c['end']:
            return c['s'] - 0.04
    return t


def dof_composite(cv, ov, t, focus_xy):
    """3D text layer: it sits nearer the lens than the host, so a camera zoom-in pushes it toward the
    camera (parallax) and out of the shallow focus plane (wide aperture) while the host stays sharp."""
    ta = text_anchor(t)
    rel = 1.0
    if _shot_start(ta) == _shot_start(t) and t > ta:
        # focus was set at the widest framing since the text appeared; only zoom-ins defocus it
        ref = min(zoom_mult(ta + (t - ta) * k / 8) for k in range(9))
        rel = zoom_mult(t) / max(1e-3, ref)
        if not [x for x in STACKS if x[0] <= t < x[1]]:
            rel = 1 + (rel - 1) * 0.6  # single-word captions stay a bit more legible
    if abs(rel - 1) > 0.004:
        s = rel ** 1.9
        fx, fy = focus_xy
        M = np.float32([[s, 0, fx * (1 - s)], [0, s, fy * (1 - s)]])
        ov = cv2.warpAffine(ov, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        sig = min(16.0, 60.0 * abs(rel - 1))
        if sig > 0.4:
            ov = cv2.GaussianBlur(ov, (0, 0), sig)
    return cv * (1 - ov[..., 3:4]) + ov[..., :3]


def render_one(t, fi, frame_bgr, ts):
    kind, a, b, name = seg_at(t)
    if kind == 'G':
        acc = None
        for u in ts:  # motion blur: average sub-frames of the whole 3D scene
            cam = scene_cam(name, u, a, b)
            cv = backdrop(cam, u)
            SCENES[name](cv, u, a, b, cam)
            draw_caption(cv, u, SAFE_CAP_G)
            acc = cv if acc is None else acc + cv
        return acc / len(ts), 'G'
    dx, dy = 0, 0
    for tt in (54.90, 74.72, 42.34):  # impact shakes
        sx, sy = shake(t, tt, 20)
        dx += sx; dy += sy
    cv, box = talent(frame_bgr, t, fi, dx, dy)
    fr = face_rect(fi, box)
    st = [s for s in STACKS if s[0] <= t < s[1]]
    if st:
        # darken the plate slightly behind kinetic type, like the reference
        k = min(prog(t, st[0][0], st[0][0] + 0.2), 1 - prog(t, st[0][1] - 0.15, st[0][1]))
        cv *= 1 - 0.16 * k
    ov = np.zeros((H, W, 4), np.float32)
    for u in ts:  # motion blur on the 3D text layer (the host plate stays a single sharp frame)
        lay = np.zeros((H, W, 4), np.float32)
        stu = [s for s in STACKS if s[0] <= u < s[1]]
        if stu:
            draw_stack(lay, u, stu[0], 0, 0, fr)
        elif u < 87.9:  # the CTA card carries the last words
            draw_caption(lay, u, SAFE_CAP_T, fr)
        ov += lay
    ov /= len(ts)
    # face-locked overlays stay on the host plane (sharp)
    face_box(cv, t, fi, box, 9.70, 13.40)
    face_box(cv, t, fi, box, 76.84, 79.60)
    # floating 3D icons share the text layer
    bang(ov, t, fi, box, 5.16, 6.06)
    icon_pop(ov, t, 'gold', 870, 840, 0.66, 2.94, 0.55)
    icon_pop(ov, t, 'hand', 860, 1090, 1.10, 2.94, 0.62)
    icon_pop(ov, t, 'down_r', 850, 900, 23.14, 23.85, 0.9)
    icon_pop(ov, t, 'yen_icon', 230, 820, 49.26, 51.30, 0.85)
    icon_pop(ov, t, 'up_g', 400, 760, 49.76, 51.30, 0.85)
    if 74.72 <= t < 76.84:
        for i, (nm, x, y) in enumerate((('up_g', 180, 700), ('down_r', 860, 820), ('up_r', 200, 1250), ('down_g', 850, 1300))):
            icon_pop(ov, t, nm, x, y, 74.72 + i * 0.08, 76.84, 0.7)
    fx, fy, fw = face_at(fi)
    cv = dof_composite(cv, ov, t, to_screen(fx, fy, box))
    cta(cv, t)
    return cv, 'T'


def render(t, fi, frame_bgr):
    ts = [t + d / FPS for d in (-0.25, 0.0, 0.25)]
    return render_one(t, fi, frame_bgr, ts)


def transition(t):
    """Zoom-through between talent and 3D cutaways: (scale, blur) applied to the frame."""
    for c in CUTS:
        d = t - c
        if 0 <= d < 0.2:
            p = d / 0.2
            return 1.18 - 0.18 * e_out_cubic(p), (1 - p)
        if -0.12 <= d < 0:
            p = (d + 0.12) / 0.12
            return 1 + 0.12 * e_in_cubic(p), p
    for c, _ in T_SHOTS[1:]:  # punch-in jump cuts get a tiny settle
        d = t - c
        if 0 <= d < 0.12 and not any(abs(c - x) < 0.05 for x in CUTS):
            return 1.04 - 0.04 * e_out_cubic(d / 0.12), 0.0
    return 1.0, 0.0


def finish(res, t, fi):
    cv, kind = res
    sc, bl = transition(t)
    if kind == 'T':
        sc, bl = 1.0, 0.0  # host: scale already applied in the crop, never blurred
    if sc != 1.0:
        M = cv2.getRotationMatrix2D((CX, CY), 0, sc)
        cv = cv2.warpAffine(cv, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if bl > 0.02:
        acc = cv.copy()
        for k in range(1, 5):
            s = 1 + 0.02 * k * bl
            M = cv2.getRotationMatrix2D((CX, CY), 0, s)
            acc += cv2.warpAffine(cv, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        cv = acc / 5
    # light grain
    rng = np.random.default_rng(fi % 8)
    g = cv2.resize(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (W, H))
    cv = cv + g[..., None] * 0.012
    return np.clip(cv, 0, 1)


def frame_iter(f0, f1):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{f0 / FPS:.6f}', '-i', PLATE, '-frames:v', str(f1 - f0),
           '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    for fi in range(f0, f1):
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield fi, np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.stdout.close()
    p.wait()


def chunk(f0, f1, out):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13',
                            '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for fi, fr in frame_iter(f0, f1):
        t = fi / FPS
        cv = finish(render(t, fi, fr), t, fi)
        enc.stdin.write((cv * 255 + 0.5).astype(np.uint8).tobytes())
        if fi % 60 == 0:
            print(f'[{f0}-{f1}] frame {fi}', flush=True)
    enc.stdin.close()
    enc.wait()


def stills(times):
    os.makedirs(f'{WORK}/stills', exist_ok=True)
    for t in times:
        fi = int(round(t * FPS))
        _, fr = next(frame_iter(fi, fi + 1))
        cv = finish(render(t, fi, fr), t, fi)
        if os.environ.get('SAFE_GUIDE'):
            cv = cv.copy()
            cv2.rectangle(cv, (SAFE['x0'], SAFE['y0']), (SAFE['x1'], SAFE['y1']), (1, 0, 1), 3)
        cv2.imwrite(f'{WORK}/stills/s_{t:06.2f}.jpg', (cv[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])


# ====================================================================== sound design cues

def sfx_cues():
    """(time, sample, gain_db) — every cue uses the SFX sliced from the reference video."""
    cues = []
    wh = ['whoosh_a', 'whoosh_b', 'whoosh_c', 'whoosh_d', 'whoosh_e']
    for i, c in enumerate(CUTS):
        if c < DUR - 0.5:
            cues.append((c - 0.30, wh[i % len(wh)], -4))
    for i, (s, _) in enumerate(T_SHOTS[1:]):
        if not any(abs(s - x) < 0.05 for x in CUTS):
            cues.append((s - 0.02, ['swish_s', 'click_b'][i % 2], -9))
    pops = ['pop_a', 'click_a', 'tick', 'blip_a', 'pop_hit', 'blip_b', 'blip_c']
    k = 0
    for st in STACKS:
        for txt, tw, style, size, al in st[6]:
            if style == 'y':
                cues.append((tw - 0.01, 'pop_hit' if size < 200 else 'boom', -6 if size < 200 else -3))
            else:
                cues.append((tw - 0.01, pops[k % len(pops)], -11)); k += 1
    # big reveals
    for tt, s, g in ((37.16, 'boom', -2), (47.50, 'whoosh_b', -6), (32.56, 'hit_c', -4), (54.90, 'boom_b', -3),
                     (5.16, 'ding', -7), (88.62, 'ding', -4), (88.6, 'click_a', -2), (87.48, 'whoosh_c', -6),
                     (74.72, 'hit_c', -5), (15.64, 'pop_hit', -6), (39.28, 'pop_hit', -5), (7.58, 'pop_a', -6),
                     (9.70, 'tick', -8), (76.84, 'tick', -8), (49.26, 'pop_a', -8), (49.76, 'pop_hit', -8),
                     (23.14, 'pop_hit', -7), (58.42, 'pop_hit', -7), (70.40, 'pop_hit', -6), (83.52, 'pop_hit', -6),
                     (84.48, 'pop_hit', -6), (0.66, 'hit_c', -6)):
        cues.append((tt - 0.01, s, g))
    cues.append((47.67, 'boom_b', -3))
    # scene element pops inside the 3D cutaways
    for tt in (6.06, 6.70, 13.62, 25.02, 26.34, 28.48, 29.62, 30.52, 35.80, 43.48, 44.62, 46.10, 57.3, 59.2, 59.74,
               61.31, 63.75, 65.51, 67.52, 67.95, 69.24, 69.84, 83.24):
        cues.append((tt - 0.01, pops[k % len(pops)], -10)); k += 1
    # camera zoom-ins get a soft swish from the reference
    for t0, d, m0, m1 in ZOOM_MOVES:
        if m1 > m0:
            cues.append((t0 - 0.05, 'swish_s', -13))
    # caption pops (quiet, like the reference's per-word ticks) — only every other word to avoid clutter
    for i, c in enumerate(CHUNKS):
        if not stack_active(c['s']) and i % 2 == 0:
            cues.append((c['s'] - 0.01, 'click_b' if i % 4 else 'click_a', -20))
    return sorted(cues)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'still':
        stills([float(x) for x in sys.argv[2].split(',')])
    elif cmd == 'chunk':
        chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == 'sfx':
        json.dump(sfx_cues(), open(sys.argv[2], 'w'))
    elif cmd == 'nframes':
        print(NFR)
