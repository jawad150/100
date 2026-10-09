"""Organic Fostering — 'Day in the life' reel (1080x1920, 30 fps, ~19 s).

Cinematic AI footage + SaaS-style motion graphics: the £447.60 weekly allowance
"travels" as glowing orbs into each everyday moment of a child's day.

Usage:
  python3 reel_of.py still 1.5,3.6,9.0     # preview frames -> workspace_of/stills
  python3 reel_of.py range 0 570           # render frames [a,b) -> workspace_of/frames_out
"""
import os, sys, math, functools
os.environ.setdefault('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace_of')))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pipeline'))
import numpy as np
import cv2
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
DUR = 19.0
NF = int(DUR * FPS)

# ------------------------------------------------------------------ brand palette
PLUM = hexc('#5B174F')
MAGENTA = hexc('#B7006E')
ORANGE_B = hexc('#FF6411')
GREEN = hexc('#61A80A')
IVORY = hexc('#FCF8F5')
PAPER = hexc('#FFFDFB')
BLUSH = hexc('#F6EAF3')
PEACH = hexc('#FFD4BA')
LEAF_T = hexc('#E8F3D8')
INK = hexc('#321F35')
MUTEDC = hexc('#655563')
WHITE_ = (1.0, 1.0, 1.0, 1.0)

F_X = 'Nunito-900'
F_B = 'Nunito-800'
F_M = 'Nunito-700'
F_R = 'Nunito-400'
TRK = -0.02

# ------------------------------------------------------------------ sources
CLIPS = {i: VideoFrames(f'{S}/frames/c{i}/*.jpg', 24) for i in range(1, 8)}
SEQ = {}


def seq(name):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=24, loop=True)
    return SEQ[name]


@functools.lru_cache(maxsize=None)
def logo_full():
    return load_png_sprite(f'{S}/src/logo_full.png')


# ------------------------------------------------------------------ backgrounds
_Y, _X = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)


def _blob(cx, cy, r):
    d = np.sqrt((_X - cx / 4) ** 2 + (_Y - cy / 4) ** 2) / (r / 4)
    return np.exp(-d * d)[..., None]


def bg_ivory(t):
    """Paper/blush gradient with slow drifting brand-colour glows (SaaS light stage)."""
    base = vgrad(H // 4, W // 4, PAPER, BLUSH)
    for (cx, cy, r, col, a, ph) in [(180, 380, 520, MAGENTA, 0.20, 0.0), (930, 640, 560, ORANGE_B, 0.18, 1.7),
                                    (300, 1600, 600, GREEN, 0.12, 3.1), (900, 1500, 520, PEACH, 0.45, 4.4)]:
        x = cx + 90 * math.sin(t * 0.6 + ph)
        y = cy + 70 * math.cos(t * 0.5 + ph)
        base = base * (1 - _blob(x, y, r) * a) + np.array(col[:3], np.float32) * _blob(x, y, r) * a
    return cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)


def bg_plum(t):
    base = vgrad(H // 4, W // 4, hexc('#3E0F37'), INK)
    for (cx, cy, r, col, a, ph) in [(540, 560, 650, MAGENTA, 0.55, 0.0), (120, 1500, 520, ORANGE_B, 0.18, 2.0),
                                    (980, 1250, 520, PLUM, 0.6, 3.0)]:
        x = cx + 80 * math.sin(t * 0.7 + ph)
        y = cy + 60 * math.cos(t * 0.6 + ph)
        base = base * (1 - _blob(x, y, r) * a) + np.array(col[:3], np.float32) * _blob(x, y, r) * a
    return cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)


_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]


def scrim(canvas, top=0.0, bottom=0.0, top_h=0.45, bot_h=0.35, color=(0.10, 0.03, 0.09)):
    """Darken top/bottom for text legibility (plum-tinted)."""
    c = np.array(color, np.float32)
    if top > 0:
        a = np.clip(1 - _yy / top_h, 0, 1) ** 1.6 * top
        canvas *= (1 - a)
        canvas += c * a
    if bottom > 0:
        a = np.clip((_yy - (1 - bot_h)) / bot_h, 0, 1) ** 1.6 * bottom
        canvas *= (1 - a)
        canvas += c * a


def grade(img, warm=0.0, night=0.0):
    """Light brand grade: plum-lifted shadows, slight warmth."""
    out = img * 0.97 + np.array([0.035, 0.008, 0.03], np.float32) * (1 - img)
    if warm:
        out = out * np.array([1 + 0.04 * warm, 1.0, 1 - 0.05 * warm], np.float32)
    if night:
        out = out * np.array([1 - 0.05 * night, 1 - 0.06 * night, 1 + 0.03 * night], np.float32)
    return np.clip(out, 0, 1)


def clip_frame(ci, tl, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0):
    img = CLIPS[ci].get(max(0.0, min(tl, 5.0)))
    z = max(zoom, 1.0)
    out = crop_resize(img, cx, cy, W / z, H / z, W, H)
    if abs(rot) > 0.01:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1.0)
        out = cv2.warpAffine(out, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out.astype(np.float32)


# ------------------------------------------------------------------ text helpers
@functools.lru_cache(maxsize=512)
def word_spr(txt, fname, size, color, grad=None):
    return text_sprite(txt, fname, size, color, TRK, grad)


def space_w(fname, size):
    return font(fname, size).getlength(' ') * 0.9


def sweep(spr, p, width=0.12, angle=0.35, strength=0.9):
    """Diagonal light sweep across a text sprite; p in [-0.3, 1.3]."""
    h, w = spr.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xs / w) * math.cos(angle) + (ys / h) * math.sin(angle) * (h / w)
    band = np.exp(-((u - p) / width) ** 2) * strength
    out = spr.copy()
    out[..., :3] += band[..., None] * spr[..., 3:4]
    return out


def colorize(spr, dark, light, gamma=1.0, light_top=None):
    """Map a rendered sprite's luminance onto a dark->light brand ramp (keeps 3D shading).
    Clipped faces take `light` (optionally a vertical light_top->light gradient)."""
    a = spr[..., 3:4]
    rgb = spr[..., :3] / np.maximum(a, 1e-4)
    lum = rgb.mean(axis=2, keepdims=True)
    lum = np.clip(lum / max(float(lum.max()), 1e-3), 0, 1) ** gamma
    d = np.array(dark[:3], np.float32)
    h = spr.shape[0]
    if light_top is not None:
        ys = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        l = np.array(light_top[:3], np.float32) * (1 - ys) + np.array(light[:3], np.float32) * ys
    else:
        l = np.array(light[:3], np.float32)
    out = d * (1 - lum) + l * lum
    return np.concatenate([out * a, a], 2).astype(np.float32)


_col_cache = {}


def colorized(name, idx, dark, light, gamma=1.0):
    key = (name, idx, dark, light)
    if key not in _col_cache:
        if len(_col_cache) > 200:
            _col_cache.clear()
        _col_cache[key] = colorize(seq(name).frame(idx / 24.0), dark, light, gamma, light_top=hexc('#E83C9C'))
    return _col_cache[key]


def glow_add(canvas, spr, cx, cy, color, sigma=16, strength=0.8, scale=1.0):
    g = blur_sprite(tint(spr, color), sigma) * strength
    draw(canvas, g, cx, cy, scale=scale, mode='add')


def shadow(canvas, spr, cx, cy, op=0.55, sigma=12, dy=8, scale=1.0):
    s = blur_sprite(tint(spr, (0.05, 0.0, 0.04)), sigma)
    draw(canvas, s, cx, cy + dy, scale=scale, opacity=op)


def kinetic_line(canvas, text, cx, cy, size, t, t0, color=WHITE_, fname=F_B, stagger=0.06, dur=0.42,
                 grad=None, glow=None, glow_str=0.6, shadow_op=0.5, sweep_t=None, out_t=None, out_dur=0.3,
                 rise=46):
    """Word-by-word blur-in with rise and settle; optional glow, shadow, light sweep and blur-out."""
    if t < t0:
        return
    words = text.split(' ')
    sprs = [word_spr(wd, fname, size, color, grad) for wd in words]
    sw = space_w(fname, size)
    widths = [s.shape[1] - 12 for s in sprs]
    total = sum(widths) + sw * (len(words) - 1)
    x = cx - total / 2
    fade_out = 1.0
    blur_out = 0.0
    if out_t is not None and t > out_t:
        k = prog(t, out_t, out_t + out_dur)
        fade_out = 1 - e_in_cubic(k)
        blur_out = 14 * k
    for i, (wd, s, wdt) in enumerate(zip(words, sprs, widths)):
        k = prog(t, t0 + i * stagger, t0 + i * stagger + dur)
        if k <= 0:
            x += wdt + sw
            continue
        e = e_out_expo(k)
        op = min(1.0, k * 2.2) * fade_out
        b = (1 - e) * 12 + blur_out
        sc = 1 + 0.10 * (1 - e)
        wx = x + wdt / 2
        wy = cy + rise * (1 - e)
        spr = s
        if sweep_t is not None and t >= sweep_t:
            p = (t - sweep_t) / 0.7 * 1.6 - 0.3 - (wx - (cx - total / 2)) / total * 0.6
            if -0.3 < p < 1.3:
                spr = sweep(s, p)
        if shadow_op > 0:
            shadow(canvas, s, wx, wy, op=shadow_op * op, scale=sc)
        if glow is not None:
            glow_add(canvas, s, wx, wy, glow, strength=glow_str * op, scale=sc)
        draw(canvas, blur_sprite(spr, b), wx, wy, scale=sc, opacity=op)
        x += wdt + sw


def type_line(canvas, text, cx, cy, size, t, t0, cps=26, color=PLUM, fname=F_B, cursor=True):
    """Typewriter reveal with a blinking caret (SaaS input feel)."""
    if t < t0:
        return
    n = int((t - t0) * cps)
    shown = text[:max(0, min(len(text), n))]
    full = word_spr(text, fname, size, color)
    if shown:
        spr = word_spr(shown, fname, size, color)
        left = cx - (full.shape[1] - 12) / 2
        draw(canvas, spr, left + spr.shape[1] / 2 - 6, cy)
        xend = left + spr.shape[1] - 10
    else:
        xend = cx - (full.shape[1] - 12) / 2
    if cursor and (int(t * 2.4) % 2 == 0 or n < len(text)):
        car = solid(np.ones((int(size * 0.95), 6), np.float32), MAGENTA)
        draw(canvas, car, xend + 10, cy + 2)


# ------------------------------------------------------------------ UI pieces
def rrect_spr(w, h, r, fill, border=None, bw=2.0, grad=None):
    d = rrect_alpha(int(w), int(h), r, 2)
    a = sdf_fill(d)
    if grad is not None:
        rgb = hgrad(a.shape[0], a.shape[1], grad[0], grad[1])
        spr = np.concatenate([rgb * a[..., None], a[..., None]], 2).astype(np.float32)
    else:
        spr = solid(a, fill)
    if border is not None:
        spr = over_spr(spr, solid(sdf_stroke(d, bw), border))
    return spr


def glass(canvas, cx, cy, w, h, r=36, tint_c=(1, 1, 1), tint_a=0.18, blur=24, border_a=0.45, opacity=1.0,
          shadow_a=0.35, dark=False):
    """Frosted-glass card: blurs what is behind it, tints, adds rim light and soft shadow."""
    if opacity <= 0.01 or w < 8 or h < 8:
        return
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    w, h = int(w), int(h)
    # shadow
    if shadow_a > 0:
        sh = blur_sprite(rrect_spr(w, h, r, (0.08, 0.0, 0.06, 1.0)), 26)
        draw(canvas, sh, cx, cy + 22, opacity=shadow_a * opacity)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    pad_ = int(blur * 2)
    a0, b0, a1, b1 = max(0, X0 - pad_), max(0, Y0 - pad_), min(W, X1 + pad_), min(H, Y1 + pad_)
    region = canvas[b0:b1, a0:a1]
    small = cv2.resize(region, (max(1, (a1 - a0) // 4), max(1, (b1 - b0) // 4)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), blur / 4)
    bl = cv2.resize(small, (a1 - a0, b1 - b0), interpolation=cv2.INTER_LINEAR)[Y0 - b0:Y1 - b0, X0 - a0:X1 - a0]
    tc = np.array(tint_c, np.float32)
    frosted = bl * (1 - tint_a) + tc * tint_a
    if dark:
        frosted = frosted * 0.78
    d = rrect_alpha(w, h, r, 0)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    m = (sdf_fill(d) * opacity)[..., None]
    dst = canvas[Y0:Y1, X0:X1]
    dst[:] = dst * (1 - m) + frosted * m
    # rim + top sheen
    rim = solid(sdf_stroke(rrect_alpha(w, h, r, 2), 2.0), (1, 1, 1, border_a))
    draw(canvas, rim, cx, cy, opacity=opacity)
    sheen_h = int(h * 0.5)
    ys = np.linspace(1, 0, sheen_h, dtype=np.float32)[:, None] ** 2 * 0.10
    sheen_a = sdf_fill(rrect_alpha(w, h, r, 0))[:sheen_h] * ys
    sheen = np.concatenate([np.ones(sheen_a.shape + (3,), np.float32) * sheen_a[..., None], sheen_a[..., None]], 2)
    composite(canvas, sheen, x0, y0, opacity)


@functools.lru_cache(maxsize=None)
def check_spr(size=44, color=GREEN):
    """Rounded green tick badge."""
    s = size * 3
    im = np.zeros((s, s), np.uint8)
    cv2.circle(im, (s // 2, s // 2), s // 2 - 2, 255, -1, cv2.LINE_AA)
    disc = im.astype(np.float32) / 255
    tk = np.zeros((s, s), np.uint8)
    pts = np.array([[s * 0.28, s * 0.52], [s * 0.44, s * 0.68], [s * 0.74, s * 0.36]], np.int32)
    cv2.polylines(tk, [pts], False, 255, int(s * 0.11), cv2.LINE_AA)
    tick = tk.astype(np.float32) / 255
    spr = over_spr(solid(disc, color), solid(tick, WHITE_))
    return cv2.resize(spr, (size, size), interpolation=cv2.INTER_AREA)


def coin_icon(t, size=78):
    f = seq('coin').frame(t)
    if f.shape[0] < 16:
        return solid(np.ones((size, size), np.float32), MAGENTA)
    sc = size / max(f.shape[:2])
    return cv2.resize(f, (max(1, int(f.shape[1] * sc)), max(1, int(f.shape[0] * sc))), interpolation=cv2.INTER_AREA)


def tag(canvas, t, t0, cx, cy, label, sub=None, dark=True):
    """Glass tag that pops in: [£ coin] label ✓ — money landing in a moment."""
    if t < t0:
        return
    k = prog(t, t0, t0 + 0.5)
    s = e_out_back(k, 2.2) if k < 1 else 1.0
    op = min(1, k * 3)
    ts = word_spr(label, F_B, 46, WHITE_ if dark else PLUM)
    tw = ts.shape[1]
    w = tw + 78 + 64 + 70
    h = 104 if sub is None else 136
    glass(canvas, cx, cy, w * s, h * s, r=h * s / 2, tint_c=(0.22, 0.05, 0.18) if dark else (1, 1, 1),
          tint_a=0.38 if dark else 0.5, opacity=op, blur=26)
    x = cx - w * s / 2 + 26 * s
    ic = coin_icon(t - t0, int(76 * s) or 1)
    draw(canvas, ic, x + ic.shape[1] / 2, cy - (14 * s if sub else 0), opacity=op)
    x += 84 * s
    draw(canvas, ts, x + tw * s / 2, cy - (14 * s if sub else 0), scale=s, opacity=op)
    if sub:
        ss = word_spr(sub, F_M, 28, PEACH)
        draw(canvas, ss, x + ss.shape[1] * s / 2, cy + 30 * s, scale=s, opacity=op)
    kc = prog(t, t0 + 0.25, t0 + 0.6)
    if kc > 0:
        cs = e_out_back(kc, 3.0)
        draw(canvas, check_spr(), cx + w * s / 2 - 46 * s, cy, scale=cs * s, opacity=op)


def orb(canvas, t, t0, t1, p0, p1, p2, color, size=165, trail=16):
    """Glowing money orb travelling on a quadratic bezier, with comet trail + sparkles."""
    if t < t0 or t > t1 + 0.6:
        return None
    u = e_inout_cubic(prog(t, t0, t1))

    def bez(v):
        return ((1 - v) ** 2 * p0[0] + 2 * (1 - v) * v * p1[0] + v * v * p2[0],
                (1 - v) ** 2 * p0[1] + 2 * (1 - v) * v * p1[1] + v * v * p2[1])
    if t <= t1:
        for i in range(trail, 0, -1):
            v = max(0.0, u - i * 0.022)
            x, y = bez(v)
            f = 1 - i / (trail + 1)
            draw(canvas, radial_sprite(int(size * 0.9), color, 1.8), x, y, scale=0.25 + 0.6 * f,
                 opacity=0.55 * f, mode='add')
        x, y = bez(u)
        draw(canvas, radial_sprite(size * 2, color, 2.2), x, y, opacity=1.0, mode='add')
        draw(canvas, radial_sprite(size * 4, color, 3.0), x, y, opacity=0.35, mode='add')
        draw(canvas, radial_sprite(int(size * 0.7), (1, 1, 1), 2.5, core=0.6), x, y, opacity=1.0, mode='add')
        rng = np.random.default_rng(int(t * 1000) % 9973)
        for _ in range(5):
            v = max(0.0, u - rng.uniform(0, 0.25))
            sx, sy = bez(v)
            draw(canvas, radial_sprite(18, (1, 0.95, 0.85), 1.5, core=1.0), sx + rng.normal(0, 22),
                 sy + rng.normal(0, 22), opacity=0.8, mode='add')
    else:
        # landing burst
        k = prog(t, t1, t1 + 0.6)
        x, y = p2
        rs = ring_sprite(300, 120, 6, color)
        draw(canvas, rs, x, y, scale=0.3 + 1.4 * e_out_expo(k), opacity=(1 - k) * 0.9, mode='add')
        draw(canvas, radial_sprite(size * 3, color, 2.0), x, y, opacity=(1 - k) * 0.8, mode='add')
    return None


def leaf(canvas, name, t, x, y, size, blur=0.0, op=1.0, phase=0.0):
    f = seq(name).frame(t * 0.6 + phase, blur=blur)
    if f.shape[0] < 16:
        return
    sc = size / max(f.shape[:2])
    draw(canvas, f, x, y, scale=sc, opacity=op)


def seq_draw(canvas, name, t, x, y, size, op=1.0, blur=0.0, fps_idx=None):
    s = seq(name)
    if fps_idx is not None:
        f = s.frame(fps_idx / 24.0, blur=blur)
    else:
        f = s.frame(t, blur=blur)
    if f.shape[0] < 16:
        return
    sc = size / max(f.shape[1], 1)
    draw(canvas, f, x, y, scale=sc, opacity=op)


TIMES = [(2.7, '7:00 am', 'sun'), (5.1, '7:10 am', 'sun'), (6.1, '7:40 am', 'sun'), (7.25, '7:45 am', 'sun'),
         (8.45, '7:50 am', 'sun'), (11.0, '7:30 pm', 'moon')]


def clock_pill(canvas, t):
    """Live time pill at the top — the 'day' ticking along like a SaaS status chip."""
    if t < 2.75 or t > 14.15:
        return
    op = min(prog(t, 2.75, 3.05), 1 - prog(t, 13.85, 14.15))
    cur = 0
    for i, (tt0, _, _) in enumerate(TIMES):
        if t >= tt0:
            cur = i
    tt0, label, icon = TIMES[cur]
    prev = TIMES[cur - 1][1] if cur > 0 else label
    k = e_out_expo(prog(t, tt0 + 0.05, tt0 + 0.45)) if cur > 0 else 1.0
    w, h = 300, 84
    cx, cy = W / 2, 214
    night = icon == 'moon'
    glass(canvas, cx, cy, w, h, r=42, tint_c=(0.2, 0.05, 0.17), tint_a=0.42, opacity=op, blur=22, shadow_a=0.25)
    # icon dot
    dot_col = ORANGE_B if not night else hexc('#C9B8FF')
    draw(canvas, radial_sprite(60, dot_col, 2.0), cx - w / 2 + 44, cy, opacity=op, mode='add')
    draw(canvas, solid(sdf_fill(rrect_alpha(18, 18, 9, 2)), dot_col), cx - w / 2 + 44, cy, opacity=op)
    # rolling digits
    tx = cx + 22
    if k < 1:
        so = word_spr(prev, F_B, 42, WHITE_)
        draw(canvas, blur_sprite(so, 6 * k), tx, cy - 40 * k, opacity=op * (1 - k))
    sn = word_spr(label, F_B, 42, WHITE_)
    draw(canvas, blur_sprite(sn, 6 * (1 - k)), tx, cy + 40 * (1 - k), opacity=op * k)


def chat_bubble(canvas, t, t0, cx, cy, text, typing_until):
    if t < t0:
        return
    k = prog(t, t0, t0 + 0.45)
    s = e_out_back(k, 2.0)
    op = min(1, k * 3)
    if t < typing_until:
        w, h = 190, 96
        glass(canvas, cx - 160, cy, w * s, h * s, r=48 * s, tint_c=(1, 1, 1), tint_a=0.82, opacity=op, blur=20)
        for i in range(3):
            ph = (t * 3.2 - i * 0.28) % 1.0
            yy = cy - 10 * max(0, math.sin(ph * math.pi))
            dot = solid(sdf_fill(rrect_alpha(20, 20, 10, 2)), MUTEDC)
            draw(canvas, dot, cx - 160 - 36 + i * 36, yy, scale=s, opacity=op * (0.5 + 0.5 * math.sin(ph * math.pi)))
        return
    k2 = prog(t, typing_until, typing_until + 0.45)
    s2 = e_out_back(k2, 2.4)
    ts = word_spr(text, F_B, 54, PLUM)
    w, h = ts.shape[1] + 90, 120
    glass(canvas, cx, cy, w * s2, h * s2, r=60 * s2, tint_c=(1, 1, 1), tint_a=0.9, opacity=min(1, k2 * 3),
          blur=20, shadow_a=0.45)
    draw(canvas, ts, cx, cy, scale=s2, opacity=min(1, k2 * 3))
    # little tail
    tail = solid(sdf_fill(rrect_alpha(30, 30, 15, 2)), (1, 1, 1, 0.9))
    draw(canvas, tail, cx - w * s2 / 2 + 34, cy + h * s2 / 2 - 6, scale=s2, opacity=min(1, k2 * 3) * 0.9)
    # heart reaction
    kh = prog(t, typing_until + 0.55, typing_until + 1.0)
    if kh > 0:
        seq_draw(canvas, 'heart', t, cx + w * s2 / 2 - 10, cy - h * s2 / 2 - 8, 120 * e_out_back(kh, 3.0),
                 op=min(1, kh * 3))


def colour_bar(canvas, cx, cy, w, h, k):
    """Brand three-colour bar drawing on left to right."""
    if k <= 0:
        return
    seg = w / 3
    x0 = cx - w / 2
    for i, c in enumerate((MAGENTA, ORANGE_B, GREEN)):
        kk = clamp(k * 3 - i)
        if kk <= 0:
            continue
        ww = max(2, seg * e_out_cubic(kk))
        spr = solid(np.ones((int(h), int(ww)), np.float32), c)
        composite(canvas, spr, int(x0 + seg * i), int(cy - h / 2))


# ------------------------------------------------------------------ transitions / post fx
def whip(canvas, amount, direction=1):
    """Horizontal whip-pan: shift + directional blur."""
    if amount <= 0.001:
        return canvas
    k = int(10 + 120 * amount)
    kern = np.ones((1, k), np.float32) / k
    out = cv2.filter2D(canvas, -1, kern, borderType=cv2.BORDER_REFLECT)
    sh = int(direction * amount * 260)
    return np.roll(out, sh, axis=1)


def zoom_blur(canvas, amount, cx=W / 2, cy=H / 2):
    if amount <= 0.01:
        return canvas
    acc = canvas.copy()
    n = 6
    for i in range(1, n):
        s = 1 + amount * 0.06 * i
        M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
        acc += cv2.warpAffine(canvas, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return acc / n


def light_leak(canvas, k, color=(1.0, 0.55, 0.3), side=1):
    if k <= 0:
        return
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    g = np.exp(-((xs - (0.5 + 0.6 * side * (k - 0.5))) / 0.32) ** 2) * math.sin(k * math.pi)
    canvas += g * np.array(color, np.float32) * 0.9


def shake(t, t0, amp=14, dur=0.35):
    k = prog(t, t0, t0 + dur)
    if k <= 0 or k >= 1:
        return 0.0, 0.0
    a = amp * (1 - k) ** 2
    return a * math.sin(t * 91), a * math.cos(t * 73)


# ------------------------------------------------------------------ scenes
HOOK_CUTS = [(1, 1.2), (3, 2.0), (4, 1.4), (5, 0.8), (6, 1.6), (2, 2.2)]


def sc_hook(t):
    """0.00-0.84 flash montage of the day."""
    i = min(int(t / 0.14), len(HOOK_CUTS) - 1)
    ci, off = HOOK_CUTS[i]
    lt = t - i * 0.14
    z = 1.28 - 0.18 * e_out_expo(lt / 0.14)
    c = grade(clip_frame(ci, off + lt, zoom=z, rot=(-1) ** i * 1.2 * (1 - lt / 0.14)), warm=0.5)
    c = c * 0.86
    flash = max(0.0, 1 - lt / 0.07) * 0.45
    c += flash
    # title pill
    k = prog(t, 0.04, 0.4)
    sp = e_out_back(k, 2.0)
    pl = pill('A day in the life', F_B, 46, pad_x=40, pad_y=24, fill=(1, 1, 1, 0.92), border=None, text_color=PLUM,
              dot=MAGENTA)
    draw(c, pl, W / 2, 960, scale=sp, opacity=min(1, k * 3))
    return c


def sc_money(t):
    """0.84-2.75 SaaS light stage: 3D coin + 3D £447.60, the allowance."""
    c = bg_ivory(t)
    lt = t - 0.84
    # background leaves (soft focus)
    leaf(c, 'leaf_green', t, 150, 520 + 20 * math.sin(t * 2), 230, blur=5, op=0.9)
    leaf(c, 'leaf_orange', t, 950, 420 + 20 * math.cos(t * 2.2), 200, blur=6, op=0.85, phase=0.7)
    leaf(c, 'leaf_plum', t, 960, 1560, 260, blur=4, op=0.9, phase=0.3)
    leaf(c, 'leaf_magenta', t, 120, 1450, 210, blur=7, op=0.85, phase=1.1)
    # coin flies in from depth
    k = prog(lt, 0.0, 0.45)
    e = e_out_expo(k)
    exit_k = prog(t, 2.32, 2.75)
    ex = e_in_expo(exit_k)
    cs = (0.15 + 0.85 * e) * (1 + 7 * ex)
    cy = 690 - 220 * (1 - e)
    if exit_k < 1:
        seq_draw(c, 'coin', t * 1.5, W / 2, cy, 470 * cs, op=min(1, k * 4) * (1 - ex ** 3),
                 blur=(1 - e) * 6 + ex * 10)
        glow_r = radial_sprite(700, MAGENTA, 2.0)
        draw(c, glow_r, W / 2, cy + 40, scale=cs, opacity=0.25 * min(1, k * 3), mode='add')
    # 3D amount text (spin-in sequence frames)
    kt = prog(t, 1.02, 1.02 + 47 / 24)
    if t >= 1.02 and exit_k < 1:
        idx = min(33, int((t - 1.02) * 24))
        f = seq('text_money').frame(idx / 24.0)
        if f.shape[0] > 16:
            sc = 860 / f.shape[1]
            ff = colorized('text_money', idx, hexc('#2A0826'), hexc('#A3005F'), 1.8)
            sh = blur_sprite(tint(f, (0.25, 0.04, 0.2)), 16)
            draw(c, sh, W / 2, 1197, scale=sc, opacity=0.45 * (1 - ex))
            pp = (t - 2.0) / 0.6 * 1.6 - 0.3
            if -0.3 < pp < 1.3:
                ff = sweep(ff, pp, width=0.1, strength=0.8)
            draw(c, ff, W / 2, 1175, scale=sc * (1 + 0.6 * ex), opacity=(1 - ex))
        else:
            ts = word_spr('£447.60', F_X, 190, PLUM)
            draw(c, ts, W / 2, 1150, opacity=(1 - ex))
    # pill
    if t >= 1.35:
        kp = prog(t, 1.35, 1.75)
        pl = pill('Weekly fostering allowance', F_B, 38, pad_x=36, pad_y=20, fill=PLUM + (), border=None,
                  text_color=IVORY, dot=GREEN)
        draw(c, pl, W / 2, 1360 + 30 * (1 - e_out_expo(kp)), scale=0.9 + 0.1 * e_out_back(kp), opacity=min(1, kp * 3) * (1 - ex))
    if exit_k <= 0.0:
        type_line(c, 'Where does it go?', W / 2, 1500, 64, t, 1.75, cps=24, color=MAGENTA)
    # four orbs burst outward = the money travelling into the day
    if t > 2.28:
        for j, (col, ang) in enumerate([(ORANGE_B, -2.3), (MAGENTA, -0.6), (GREEN, 0.9), (PEACH, 2.5)]):
            kk = e_in_cubic(prog(t, 2.28, 2.75))
            r = 40 + 900 * kk
            x = W / 2 + math.cos(ang) * r
            y = 690 + math.sin(ang) * r * 1.2
            draw(c, radial_sprite(220, col[:3], 2.0), x, y, opacity=0.9, mode='add')
            draw(c, radial_sprite(80, (1, 1, 1), 2.5, core=0.6), x, y, opacity=0.9, mode='add')
    if exit_k > 0.6:
        c += (exit_k - 0.6) / 0.4 * 0.9
    return c


def sc_bedroom(t):
    """2.75-5.10 Child's bedroom, morning light."""
    lt = t - 2.75
    z = 1.04 + 0.07 * (lt / 2.4)
    c = grade(clip_frame(1, 0.4 + lt * 0.9, zoom=z), warm=0.6)
    scrim(c, top=0.66, top_h=0.5, bottom=0.25)
    # flash in from previous white
    c += max(0.0, 1 - lt / 0.25) * 0.9
    seq_draw(c, 'sun', t, 950, 335 + 10 * math.sin(t * 2), 140, op=min(1, prog(t, 3.2, 3.6)))
    kinetic_line(c, 'Sometimes,', W / 2, 470, 104, t, 3.0, color=WHITE_, glow=MAGENTA, glow_str=0.35,
                 out_t=4.75, out_dur=0.25)
    kinetic_line(c, "it's not the", W / 2, 600, 104, t, 3.45, color=WHITE_, glow=MAGENTA, glow_str=0.35,
                 out_t=4.78, out_dur=0.25)
    kinetic_line(c, 'big things.', W / 2, 735, 118, t, 3.75, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFE3CF'), hexc('#FF8A3D')), glow=ORANGE_B, glow_str=0.75, sweep_t=4.15, shadow_op=0.85,
                 out_t=4.82, out_dur=0.25)
    return c


def sc_light(t):
    """5.10-6.10 Morning light on the windowsill seedling; the first orb arrives."""
    lt = t - 5.1
    c = grade(clip_frame(2, 1.2 + lt, zoom=1.06 + 0.05 * lt), warm=0.4)
    scrim(c, top=0.3, bottom=0.2)
    orb(c, t, 5.25, 5.85, (-120, 300), (300, 520), (560, 1080), ORANGE_B)
    return c


def sc_shoes(t):
    lt = t - 6.1
    c = grade(clip_frame(3, 0.6 + lt, zoom=1.05 + 0.04 * lt), warm=0.4)
    scrim(c, top=0.3, bottom=0.2)
    orb(c, t, 6.12, 6.5, (1200, 500), (900, 760), (560, 1190), MAGENTA)
    tag(c, t, 6.5, W / 2, 960, 'School shoes')
    return c


def sc_bag(t):
    lt = t - 7.25
    c = grade(clip_frame(4, 0.4 + lt, zoom=1.04 + 0.05 * lt, cx=W / 2 - 40), warm=0.4)
    scrim(c, top=0.3, bottom=0.25)
    orb(c, t, 7.27, 7.62, (-150, 1500), (200, 900), (470, 640), GREEN)
    tag(c, t, 7.62, W / 2, 1240, 'Books & packed lunch')
    return c


def sc_kitchen(t):
    lt = t - 8.45
    c = grade(clip_frame(5, 0.15 + lt * 0.95, zoom=1.03 + 0.04 * lt), warm=0.5)
    scrim(c, top=0.78, top_h=0.5, bottom=0.2)
    orb(c, t, 8.5, 8.85, (1250, 1700), (900, 1300), (420, 1090), PEACH)
    kinetic_line(c, "It's breakfast", W / 2, 470, 104, t, 8.75, color=WHITE_, glow=ORANGE_B, glow_str=0.35,
                 out_t=10.75, out_dur=0.3)
    kinetic_line(c, 'at the table.', W / 2, 600, 104, t, 9.05, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFE3CF'), hexc('#FF8A3D')), glow=ORANGE_B, glow_str=0.6, sweep_t=9.5, shadow_op=0.9,
                 out_t=10.78, out_dur=0.3)
    kh = prog(t, 9.6, 10.0)
    if kh > 0:
        seq_draw(c, 'heart', t, 905, 790 + 10 * math.sin(t * 3), 120 * e_out_back(kh, 2.6),
                 op=min(1, kh * 3) * (1 - prog(t, 10.7, 10.95)))
    tag(c, t, 8.9, W / 2, 1360, 'Breakfast')
    return c


def sc_night(t):
    lt = t - 11.0
    c = grade(clip_frame(6, 0.1 + lt * 0.85, zoom=1.04 + 0.04 * lt), night=0.6)
    scrim(c, top=0.5, bottom=0.25)
    seq_draw(c, 'moon', t, 890, 400 + 10 * math.sin(t * 1.6), 170, op=min(1, prog(t, 11.3, 11.7)))
    kinetic_line(c, 'A goodnight', W / 2, 470, 104, t, 11.2, color=WHITE_, glow=hexc('#C9B8FF'), glow_str=0.4,
                 out_t=12.45, out_dur=0.3)
    kinetic_line(c, 'at bedtime.', W / 2, 600, 104, t, 11.5, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFF1E3'), hexc('#FFB36B')), glow=ORANGE_B, glow_str=0.5, sweep_t=11.9,
                 out_t=12.48, out_dur=0.3)
    kinetic_line(c, 'Someone asking,', W / 2, 520, 84, t, 12.7, color=WHITE_, fname=F_B, glow=MAGENTA,
                 glow_str=0.3, out_t=13.9, out_dur=0.25)
    chat_bubble(c, t, 12.95, W / 2, 700, '“How was your day?”', typing_until=13.4)
    return c


def sc_message(t):
    """14.15-16.85 Plum stage: the line that lands it, 3D 'extraordinary'."""
    c = bg_plum(t)
    lt = t - 14.15
    # hands + seedling clip in a rounded, gently tilting card
    k = prog(t, 14.2, 14.9)
    e = e_out_expo(k)
    cw, ch = 700, 900
    img = grade(clip_frame(7, 0.3 + lt * 0.8, zoom=1.08), warm=0.4)
    small = cv2.resize(img, (cw, int(cw * H / W)), interpolation=cv2.INTER_AREA)
    y0 = (small.shape[0] - ch) // 2
    card = small[y0:y0 + ch]
    a = sdf_fill(rrect_alpha(cw, ch, 40, 0))
    spr = rgb_to_sprite(card, a)
    sh = blur_sprite(solid(a, (0.05, 0.0, 0.04, 1)), 30)
    ry = 8 * math.sin(lt * 1.2)
    cy_ = 1330 + 300 * (1 - e)
    draw3d(c, sh, W / 2, cy_ + 30, 40, w=cw * 1.04, rx=6, ry=ry, opacity=0.6 * e)
    draw3d(c, spr, W / 2, cy_, 0, w=cw, rx=6 * (1 - e) + 3, ry=ry, opacity=e)
    leaf(c, 'leaf_green', t, 150, 1050 + 20 * math.sin(t * 2), 220, blur=3, op=e)
    leaf(c, 'leaf_magenta', t, 950, 1700, 240, blur=2, op=e, phase=0.6)
    leaf(c, 'leaf_orange', t, 940, 980, 160, blur=6, op=e * 0.8, phase=1.3)
    kinetic_line(c, 'Sometimes, ordinary moments', W / 2, 300, 64, t, 14.35, color=WHITE_, fname=F_B,
                 stagger=0.05, glow=MAGENTA, glow_str=0.4, shadow_op=0.3)
    kinetic_line(c, 'help create', W / 2, 395, 64, t, 14.75, color=WHITE_, fname=F_B, glow=MAGENTA,
                 glow_str=0.4, shadow_op=0.3)
    # 3D extraordinary
    kx = prog(t, 15.05, 15.5)
    if kx > 0:
        fi_ = int(t * 24) % 24
        f = seq('text_extra').frame(fi_ / 24.0)
        ex_s = 0.85 + 0.15 * e_out_back(kx, 1.8)
        if f.shape[0] > 16:
            sc = 960 / f.shape[1] * ex_s
            glow_add(c, f, W / 2, 545, MAGENTA, sigma=34, strength=0.42 * kx, scale=sc)
            f = colorized('text_extra', fi_, hexc('#4A1040'), hexc('#FFC9DF'), 1.6)
            p = (t - 15.55) / 0.8 * 1.6 - 0.3
            ff = sweep(f, p, width=0.07, strength=0.5) if -0.3 < p < 1.3 else f
            draw(c, blur_sprite(ff, (1 - kx) * 10), W / 2, 545 + 40 * (1 - e_out_expo(kx)), scale=sc, opacity=min(1, kx * 2))
        else:
            kinetic_line(c, 'extraordinary', W / 2, 545, 130, t, 15.05, color=WHITE_, fname=F_X)
    kinetic_line(c, 'change.', W / 2, 700, 118, t, 15.45, color=WHITE_, fname=F_X,
                 grad=(hexc('#FFD4BA'), hexc('#FF6411')), glow=ORANGE_B, glow_str=0.9, sweep_t=15.9, shadow_op=0.3)
    return c


def sc_end(t):
    """16.85-19.0 Logo end card on paper."""
    c = bg_ivory(t)
    lt = t - 16.85
    leaf(c, 'leaf_green', t, 160 - 60 * (1 - e_out_expo(prog(lt, 0, 0.8))), 520, 200, blur=3)
    leaf(c, 'leaf_orange', t, 930 + 60 * (1 - e_out_expo(prog(lt, 0.1, 0.9))), 450, 170, blur=5, phase=0.5)
    leaf(c, 'leaf_magenta', t, 940, 1500, 230, blur=2, phase=1.0)
    leaf(c, 'leaf_plum', t, 140, 1420, 190, blur=4, phase=0.2)
    k = prog(t, 16.95, 17.6)
    e = e_out_expo(k)
    lg = logo_full()
    sc = 860 / lg.shape[1] * (0.94 + 0.06 * e)
    draw(c, lg, W / 2, 880 + 40 * (1 - e), scale=sc, opacity=min(1, k * 1.6))
    colour_bar(c, W / 2, 1160, 520, 12, prog(t, 17.45, 18.0))
    kp = prog(t, 17.7, 18.1)
    if kp > 0:
        pl = pill('organicfostering.co.uk', F_B, 40, pad_x=40, pad_y=22, fill=PLUM + (), border=None,
                  text_color=IVORY)
        draw(c, pl, W / 2, 1290 + 20 * (1 - e_out_expo(kp)), scale=0.9 + 0.1 * e_out_back(kp), opacity=min(1, kp * 3))
    kf = prog(t, 18.0, 18.4)
    if kf > 0:
        fp = word_spr('Allowance shown is the weekly rate for one child aged 0 to 4.', F_M, 26, MUTEDC)
        fp2 = word_spr('Rates vary by age and region.', F_M, 26, MUTEDC)
        draw(c, fp, W / 2, 1520, opacity=kf)
        draw(c, fp2, W / 2, 1560, opacity=kf)
    return c


SCENES = [(0.0, 0.84, sc_hook), (0.84, 2.75, sc_money), (2.75, 5.1, sc_bedroom), (5.1, 6.1, sc_light),
          (6.1, 7.25, sc_shoes), (7.25, 8.45, sc_bag), (8.45, 11.0, sc_kitchen), (11.0, 14.15, sc_night),
          (14.15, 16.85, sc_message), (16.85, DUR + 1, sc_end)]


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    c = scene_at(t)(t)
    # cross-scene transitions
    if 4.95 <= t < 5.1:
        c = whip(c, prog(t, 4.95, 5.1), -1)
    elif 5.1 <= t < 5.25:
        c = whip(c, 1 - prog(t, 5.1, 5.25), -1)
    if 7.15 <= t < 7.35:
        k = 1 - abs((t - 7.25) / 0.1)
        c = zoom_blur(c, max(0, k) * 3)
    if 6.0 <= t < 6.2:
        c = whip(c, 1 - abs((t - 6.1) / 0.1), 1)
    if 8.3 <= t < 8.6:
        light_leak(c, prog(t, 8.3, 8.6), (1.0, 0.62, 0.35), 1)
    if 10.85 <= t < 11.15:
        # day -> night dip
        k = 1 - abs((t - 11.0) / 0.15)
        c *= 1 - 0.85 * max(0, k)
    if 13.95 <= t < 14.35:
        k = 1 - abs((t - 14.15) / 0.2)
        c = zoom_blur(c, max(0, k) * 4)
        c += max(0, k) ** 2 * np.array([0.9, 0.4, 0.7], np.float32)
    if 16.7 <= t < 17.0:
        k = 1 - abs((t - 16.85) / 0.15)
        c += max(0, k) ** 1.5 * 0.95
    clock_pill(c, t)
    dx, dy = 0.0, 0.0
    for st in (0.84, 2.75, 6.5, 7.62, 15.05):
        a, b = shake(t, st, amp=10)
        dx += a
        dy += b
    if abs(dx) + abs(dy) > 0.5:
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return c


FAST = [(0.0, 0.9), (2.25, 2.85), (4.9, 5.3), (5.2, 5.9), (6.0, 6.55), (7.15, 7.65), (8.5, 8.9), (13.9, 14.4)]


def render(fi):
    t = fi / FPS
    sub = 3 if any(a <= t < b for a, b in FAST) else 1
    if sub == 1:
        c = render_raw(t)
    else:
        acc = None
        for k in range(sub):
            tt = t + (k / sub - 0.5) * 0.5 / FPS
            r = render_raw(max(0.0, tt))
            acc = r if acc is None else acc + r
        c = acc / sub
    ca = 2.5 if t < 0.84 else 0.0
    night = 11.0 <= t < 14.15
    return post(c, fi, bloom=0.45 if not night else 0.6, grain=0.018, ca=ca)


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 92])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            cv2.imwrite(f'{S}/frames_out/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
