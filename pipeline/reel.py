"""Higgsfield Genjutsu reel — orange/black SaaS motion-graphics edit.

python3 reel.py still 1.2,3.4 ...          -> renders stills to out/still_*.png
python3 reel.py range <f0> <f1> <out.mp4>  -> renders frames [f0,f1) to a video chunk
"""
import sys, math, os, functools, subprocess, time as _time
import numpy as np
import cv2
from engine import *

FPS = 30
DUR = 32.0
NSUB = int(os.environ.get('NSUB', '6'))      # motion-blur sub-samples
SHUTTER = 0.55                               # fraction of frame interval

# ============================================================== sources

RES = VideoFrames(S + '/frames/res/*.jpg', 24.0)
SCR_SEGS = {}
for st in ('12.0', '18.6', '27.2', '57.4', '61.8'):
    SCR_SEGS[float(st)] = VideoFrames(f'{S}/frames/scr/s{st}_*.jpg', 30.0, start=float(st))

def scr_frame(src_t):
    best = None
    for st, vf in SCR_SEGS.items():
        if st - 0.01 <= src_t <= st + len(vf.files) / 30.0 + 0.5:
            best = vf
    if best is None:
        best = min(SCR_SEGS.values(), key=lambda v: abs(v.start - src_t))
    return best.get(src_t)

SEQ = {}
def seq(name):
    if name not in SEQ:
        fps = {'logo3d': 30, 'torus': 14, 'capsule': 14, 'rcube': 14, 'arrow3d': 18}.get(name, 22)
        SEQ[name] = Seq(name, fps=fps, loop=(name != 'logo3d'))
    return SEQ[name]

# ============================================================== static sprites (lazy)

@functools.lru_cache(maxsize=None)
def bg_base():
    g = vgrad(H, W, hexc('#0E0B09'), hexc('#050404'))
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    # faint dot grid, fading towards the edges
    dots = ((np.abs((xs % 40) - 20) < 1.2) & (np.abs((ys % 40) - 20) < 1.2)).astype(np.float32)
    r = np.sqrt(((xs - CX) / W) ** 2 + ((ys - H * 0.45) / (H * 0.8)) ** 2)
    g += dots[..., None] * np.clip(0.9 - r * 1.3, 0, 1)[..., None] * 0.05
    return g.astype(np.float32)

@functools.lru_cache(maxsize=None)
def glow_spr():
    return radial_sprite(512, ORANGE, power=2.2)

@functools.lru_cache(maxsize=None)
def glow_white():
    return radial_sprite(256, (1, 0.92, 0.85), power=2.0)

@functools.lru_cache(maxsize=None)
def dot_spr(r):
    return radial_sprite(r * 2 + 2, (1.0, 0.72, 0.45), power=1.6, core=1.5)

@functools.lru_cache(maxsize=None)
def streak():
    return streak_sprite(1600, 90, ORANGE2, (1, 0.9, 0.8))

@functools.lru_cache(maxsize=None)
def rays_spr():
    n = 900
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    a = np.arctan2(ys - n / 2, xs - n / 2)
    r = np.sqrt((xs - n / 2) ** 2 + (ys - n / 2) ** 2) / (n / 2)
    beams = (np.cos(a * 9) * 0.5 + 0.5) ** 6 + 0.5 * (np.cos(a * 5 + 1.3) * 0.5 + 0.5) ** 10
    al = beams * np.clip(1 - r, 0, 1) ** 1.3 * np.clip(r * 3, 0, 1)
    c = np.array(ORANGE2[:3], np.float32)
    return np.concatenate([al[..., None] * c, al[..., None]], 2).astype(np.float32)

@functools.lru_cache(maxsize=None)
def grid_tex():
    n = 1600
    im = np.zeros((n, n), np.float32)
    for k in range(0, n, 80):
        im[:, k:k + 2] = 1
        im[k:k + 2, :] = 1
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt(((xs - n / 2) / (n / 2)) ** 2 + ((ys - n / 2) / (n / 2)) ** 2)
    im *= np.clip(1 - r, 0, 1) ** 1.2
    c = np.array(ORANGE[:3], np.float32)
    return np.concatenate([im[..., None] * c, im[..., None]], 2).astype(np.float32) * 0.5

@functools.lru_cache(maxsize=None)
def star_icon(size=34, color=WHITE):
    n = size * 4
    from PIL import Image, ImageDraw
    im = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(im)
    c = n / 2
    pts = []
    for k in range(8):
        a = k * math.pi / 4 - math.pi / 2
        r = c * 0.95 if k % 2 == 0 else c * 0.26
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=255)
    im = im.resize((size, size), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    return pad(solid(a, color), 2)

@functools.lru_cache(maxsize=None)
def play_icon(size=46):
    n = size * 4
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, n - 1, n - 1], fill=(255, 255, 255, 255))
    c = n / 2
    d.polygon([(c - n * 0.13, c - n * 0.2), (c - n * 0.13, c + n * 0.2), (c + n * 0.22, c)], fill=(255, 98, 0, 255))
    im = im.resize((size, size), Image.LANCZOS)
    return pil_to_sprite(im)

@functools.lru_cache(maxsize=None)
def logomark_icon(h=30):
    spr = load_png_sprite(S + '/assets/logomark_lime.png')
    sh, sw = spr.shape[:2]
    return cv2.resize(spr, (int(sw * h / sh), h), interpolation=cv2.INTER_AREA)

@functools.lru_cache(maxsize=None)
def logo_flat(w=560):
    spr = load_png_sprite(S + '/assets/logo_lime.png')
    sh, sw = spr.shape[:2]
    return cv2.resize(spr, (w, int(sh * w / sw)), interpolation=cv2.INTER_AREA)

# chips / pills -------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def chip(kind):
    if kind == 'brand':
        return pill('HIGGSFIELD  GENJUTSU', 'Inter-800', 26, icon=logomark_icon(28), fill=(1, 1, 1, 0.06),
                    border=(1, 1, 1, 0.18), tracking=0.08)
    if kind == 'original':
        return pill('ORIGINAL', 'Inter-800', 22, pad_x=18, pad_y=12, fill=(0.04, 0.04, 0.04, 0.72),
                    border=(1, 1, 1, 0.25), dot=(0.75, 0.75, 0.75, 1), tracking=0.1)
    if kind == 'genjutsu':
        return pill('GENJUTSU', 'Inter-800', 22, pad_x=18, pad_y=12, grad=(hexc('#FF8A1F'), hexc('#FF4D00')),
                    border=(1, 0.8, 0.6, 0.6), dot=(1, 1, 1, 1), tracking=0.1)
    if kind == 'cta':
        return pill('WATCH FULL VIDEO FOR THE GUIDE', 'Inter-900', 31, pad_x=34, pad_y=26,
                    grad=(hexc('#FF9A2E'), hexc('#FF4A00')), border=(1, 0.85, 0.7, 0.55), icon=play_icon(50),
                    tracking=0.03, glow=None)
    if kind == 'steps':
        return pill('4 SIMPLE STEPS', 'Inter-800', 28, fill=(1, 1, 1, 0.06), border=(1, 0.55, 0.2, 0.5),
                    dot=ORANGE, tracking=0.1)
    if kind == 'output':
        return pill('GENJUTSU OUTPUT', 'Inter-800', 22, pad_x=18, pad_y=12, grad=(hexc('#FF8A1F'), hexc('#FF4D00')),
                    border=(1, 0.8, 0.6, 0.6), icon=star_icon(20), tracking=0.1)
    if kind == '1080':
        return pill('1080p', 'JetBrainsMono-700', 22, pad_x=16, pad_y=12, fill=(0.04, 0.04, 0.04, 0.7),
                    border=(1, 1, 1, 0.25), tracking=0.02)
    if kind == 'sheet':
        return pill('CHARACTER SHEET  ·  9 ANGLES', 'Inter-800', 26, fill=(0.06, 0.05, 0.04, 0.85),
                    border=(1, 0.55, 0.2, 0.7), icon=star_icon(24, ORANGE2), tracking=0.06)
    if kind == 'motion':
        return pill('GENJUTSU  ·  MOTION TRANSFER', 'Inter-800', 26, fill=(1, 1, 1, 0.05),
                    border=(1, 0.55, 0.2, 0.55), dot=ORANGE, tracking=0.08)
    if kind.startswith('help'):
        txt = {'help1': 'Model: Higgsfield Genjutsu', 'help2': 'Motion Library  →  Recreate',
               'help3': 'Upload your character sheet', 'help4': '1080p  →  Generate'}[kind]
        return pill(txt, 'Inter-700', 29, fill=(0.97, 0.95, 0.92, 0.96), border=None, text_color=hexc('#141210'),
                    pad_x=26, pad_y=18, tracking=0.0)
    raise KeyError(kind)

def pill_sheen(spr, phase):
    """Additive diagonal sheen band restricted to the pill alpha."""
    h, w = spr.shape[:2]
    xs = np.arange(w, dtype=np.float32)[None, :] + np.arange(h, dtype=np.float32)[:, None] * 0.6
    pos = lerp(-200, w + 200, phase)
    band = np.exp(-((xs - pos) / 38) ** 2) * 0.55
    a = spr[..., 3] * band
    return np.concatenate([np.repeat(a[..., None], 3, 2), a[..., None]], 2).astype(np.float32)

# ============================================================== shared drawing helpers

PARTS = None
def particles():
    global PARTS
    if PARTS is None:
        rng = np.random.default_rng(3)
        PARTS = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), vx=rng.uniform(-8, 8), vy=rng.uniform(10, 45),
                      r=int(rng.choice([3, 4, 6, 9, 14])), a=rng.uniform(0.15, 0.6), ph=rng.uniform(0, 6.28))
                 for _ in range(55)]
    return PARTS

def background(cv, t, glow=1.0, rays=0.0, grid=0.0, glow_pos=None):
    cv[:] = bg_base()
    g = glow_spr()
    gp = glow_pos or [(170 + wobble(t, 0.07, 60), 420 + wobble(t, 0.05, 50), 1500, 0.20),
                      (930 + wobble(t, 0.06, 50, 2), 1480 + wobble(t, 0.08, 60, 1), 1600, 0.22),
                      (540, 960 + wobble(t, 0.04, 80), 1300, 0.10)]
    for x, y, size, a in gp:
        draw(cv, g, x, y, scale=size / 512, opacity=a * glow, mode='add')
    if rays > 0:
        r = rays_spr()
        draw(cv, r, 540, 900, scale=2.6, rot=t * 9, opacity=0.22 * rays, mode='add')
    if grid > 0:
        off = (t * 70) % 80
        q, ok = plane_quad(540, 1650 + 0, 400 - off * 0, 3200, 3200, rx=82, cam=None)
        # scroll by shifting the plane along its local y
        R = rotm(82, 0, 0)
        c = np.array([540, 1700, 350]) + R @ np.array([0, off * 2, 0])
        q, ok = plane_quad(c[0], c[1], c[2], 3200, 3200, rx=82)
        if ok:
            warp(cv, grid_tex(), q, opacity=grid * 0.55, mode='add')
    for p in particles():
        x = (p['x'] + p['vx'] * t) % W
        y = (p['y'] - p['vy'] * t) % H
        tw = 0.6 + 0.4 * math.sin(t * 2.2 + p['ph'])
        draw(cv, dot_spr(p['r']), x, y, opacity=p['a'] * tw * 0.55 * glow, mode='add')

OBJ_SCALE = {'sphere': 0.75, 'torus': 0.85, 'capsule': 0.6, 'rcube': 0.75, 'arrow3d': 0.8}

def obj3d(cv, name, t, x, y, size, blur=0.0, rot=0.0, opacity=1.0, t_off=0.0, cam=None, z=0.0):
    sp = seq(name).frame(t + t_off, blur)
    sh, sw = sp.shape[:2]
    size = size * OBJ_SCALE.get(name, 0.8)
    if cam is None and z == 0:
        draw(cv, sp, x, y, scale=size / (sw - 4), rot=rot, opacity=opacity)
    else:
        draw3d(cv, sp, x, y, z, w=size * sw / (sw - 4), rz=rot, cam=cam, opacity=opacity)

def pop(t, t0, dur=0.45, s=2.2):
    """Scale-in with overshoot."""
    x = prog(t, t0, t0 + dur)
    return 0.0 if x <= 0 else e_out_back(x, s)

def word_sprites(text, fname, size, color=WHITE, grad=None, tracking=0.0):
    return [text_sprite(w, fname, size, color, tracking, grad) for w in text.split(' ')]

def draw_words(cv, sprs, cx, cy, t, t0, stagger=0.07, dur=0.55, dy=60, blur=9.0, space=None,
               exit_t=None, exit_dur=0.3, exit_dy=-70, opacity=1.0, glow=None, scale=1.0):
    """Kinetic word-by-word reveal (slide up + unblur), centered line."""
    if space is None:
        space = sprs[0].shape[0] * 0.26
    widths = [s.shape[1] * scale for s in sprs]
    total = sum(widths) + space * scale * (len(sprs) - 1)
    x = cx - total / 2
    for i, s in enumerate(sprs):
        p = e_out_expo(prog(t, t0 + i * stagger, t0 + i * stagger + dur))
        if p <= 0:
            x += widths[i] + space * scale
            continue
        oy = (1 - p) * dy
        op = min(1.0, p * 1.6) * opacity
        bl = (1 - p) * blur
        if exit_t is not None and t > exit_t:
            q = e_in_expo(prog(t, exit_t + i * 0.03, exit_t + i * 0.03 + exit_dur))
            oy += q * exit_dy
            op *= 1 - q
            bl += q * 10
        sp = blur_sprite(s, bl) if bl > 0.4 else s
        if glow is not None and op > 0.05:
            gl = _glow_cache(id(s), s, glow)
            draw(cv, gl, x + widths[i] / 2, cy + oy, scale=scale, opacity=op * 0.9, mode='add')
        draw(cv, sp, x + widths[i] / 2, cy + oy, scale=scale, opacity=op)
        x += widths[i] + space * scale

_gc = {}
def _glow_cache(k, s, color):
    if k not in _gc:
        _gc[k] = glow_of(s, 16, color, 0.9)
    return _gc[k]

def light_streak(cv, t, t0, y, dur=0.45, width=1.0, opacity=1.0, direction=1):
    p = prog(t, t0, t0 + dur)
    if p <= 0 or p >= 1:
        return
    x = lerp(-500, W + 500, e_inout_cubic(p)) if direction > 0 else lerp(W + 500, -500, e_inout_cubic(p))
    a = math.sin(p * math.pi) * opacity
    draw(cv, streak(), x, y, scale=width, opacity=a, mode='add')

def shake(t, hits, amp=10.0, decay=9.0, freq=23.0):
    dx = dy = 0.0
    for h in hits:
        if t >= h:
            k = math.exp(-(t - h) * decay) * amp
            dx += k * math.sin((t - h) * freq * 6.28)
            dy += k * math.cos((t - h) * freq * 5.1 * 1.3)
    return dx, dy

# ---- card sprite builder -----------------------------------------------------

@functools.lru_cache(maxsize=None)
def card_chrome(w, h, r, P=50, glow=0.35, shadow=0.7):
    d = rrect_alpha(w, h, r, P)
    back = np.zeros(d.shape + (4,), np.float32)
    sh = sdf_fill(d - 4)
    sh = cv2.GaussianBlur(sh, (0, 0), 18) * shadow
    back = over_spr(back, solid(sh, (0, 0, 0, 1)))
    if glow > 0:
        gl = cv2.GaussianBlur(sdf_fill(d), (0, 0), 22) * glow
        gl_spr = solid(gl, ORANGE)
        back = back + gl_spr * 0.9
        back[..., 3] = np.clip(back[..., 3], 0, 1)
    mask = sdf_fill(d)
    # border: bright top edge fading down
    st = sdf_stroke(d, 2.0)
    ys = np.linspace(0, 1, d.shape[0], dtype=np.float32)[:, None]
    border = solid(st * (0.55 - 0.35 * ys), (1, 0.8, 0.65, 1))
    return back, mask, border

def make_card(rgb, w, h, r=30, P=50, glow=0.35, badges=(), dim=0.0):
    """rgb: content (h,w,3) float. badges: list of (sprite, x, y, scale, opacity) in card-local px."""
    back, mask, border = card_chrome(w, h, r, P, glow)
    spr = back.copy()
    content = np.zeros_like(spr)
    content[P:P + h, P:P + w, :3] = rgb * (1 - dim)
    content[P:P + h, P:P + w, 3] = 1
    content *= mask[..., None]
    spr = over_spr(spr, content)
    for (b, bx, by, bs, bo) in badges:
        if bo <= 0.01:
            continue
        tmp = np.zeros_like(spr)
        bh, bw = b.shape[:2]
        if abs(bs - 1) > 0.01:
            b = cv2.resize(b, (max(1, int(bw * bs)), max(1, int(bh * bs))), interpolation=cv2.INTER_LINEAR)
            bh, bw = b.shape[:2]
        x0, y0 = int(P + bx - bw / 2), int(P + by - bh / 2)
        composite_spr(tmp, b * bo, x0, y0)
        spr = over_spr(spr, tmp * mask[..., None] if False else tmp)
    spr = spr + border * 1.0
    spr[..., 3] = np.clip(spr[..., 3], 0, 1)
    return spr

def composite_spr(dst, src, x0, y0):
    h, w = src.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = src[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    d = dst[Y0:Y1, X0:X1]
    d[:] = s + d * (1 - s[..., 3:4])

# ============================================================== SCENE 1: HOOK (0 - 6.9)

CW, CH = 980, 449
TOP_C, BOT_C = (540, 762), (540, 1238)
HOOK_CUT = 2.9

def res_half_crop(src_t, half, w=CW, h=CH):
    fr = RES.get(src_t)
    y0 = half * 1080
    sub = fr[y0 + 60:y0 + 780, 175:1745]
    return cv2.resize(sub, (w, h), interpolation=cv2.INTER_AREA)

def hook_src(t):
    return 0.2 + t if t < HOOK_CUT else 21.0 + (t - HOOK_CUT)

def hook_content(t, half):
    a, b = HOOK_CUT - 0.14, HOOK_CUT + 0.14
    if t < a or t > b:
        return res_half_crop(hook_src(min(t, a) if t < a else t), half)
    p = e_inout_expo(prog(t, a, b))
    old = res_half_crop(hook_src(a - 0.01), half)
    new = res_half_crop(hook_src(b), half)
    off = int(round(p * CH))
    stack = np.concatenate([old, new], 0)
    return stack[off:off + CH]

@functools.lru_cache(maxsize=None)
def hook_words():
    size = fit_size('I PUT MYSELF', 'Unbounded-900', 900)
    l1 = word_sprites('I PUT MYSELF', 'Unbounded-900', size)
    l2 = word_sprites('INTO A MOVIE', 'Unbounded-900', size, grad=(hexc('#FFB347'), hexc('#FF4D00')))
    return l1, l2, size

def scene_hook(cv, t, cam):
    ex = e_in_expo(prog(t, 6.5, 6.88))       # exit progress
    # --- far 3D decor (behind)
    obj3d(cv, 'capsule', t, 95 + wobble(t, 0.2, 8) - ex * 200, 175 + wobble(t, 0.25, 10) - ex * 300,
          150 * pop(t, 0.5), blur=5, rot=-20, opacity=0.85)
    obj3d(cv, 'rcube', t, 70 + wobble(t, 0.3, 6) - ex * 300, 1735 + wobble(t, 0.2, 10) + ex * 300,
          115 * pop(t, 0.9), blur=4, rot=10)
    # blob peeking behind top card
    pk = e_out_back(prog(t, 1.0, 1.55), 2.0)
    obj3d(cv, 'blob_drop', t, 870 + wobble(t, 0.4, 4), lerp(660, 522, pk) + wobble(t, 0.5, 5) - ex * 900, 175,
          rot=8, t_off=0.3)

    # --- cards
    p1 = e_out_expo(prog(t, 0.05, 0.95))
    p2 = e_out_expo(prog(t, 0.15, 1.05))
    sway = wobble(t, 0.18, 2.2)
    badge_p = e_out_back(prog(t, 0.85, 1.25))
    for half, (c, p, sgn) in enumerate([(TOP_C, p1, -1), (BOT_C, p2, 1)]):
        rgb = hook_content(t, half)
        badge = chip('original' if half == 0 else 'genjutsu')
        bw = badge.shape[1]
        spr = make_card(rgb, CW, CH, r=28, glow=0.28 if half == 0 else 0.5,
                        badges=[(badge, 26 + bw / 2 - 30, 44, 0.6 + 0.4 * badge_p, min(1, badge_p * 1.5))])
        cy = lerp(c[1] + sgn * 900, c[1], p) + wobble(t, 0.22, 4, half)
        cz = lerp(500, 0, p) - ex * 1300
        cy += ex * sgn * 520
        rx = lerp(-sgn * 55, 0, p) + wobble(t, 0.15, 1.2, half) - ex * sgn * 25
        ry = sway * (1 if half == 0 else -1)
        rz = ex * sgn * 8
        op = prog(t, 0.05, 0.3) * (1 - prog(t, 6.75, 6.9))
        draw3d(cv, spr, c[0], cy, cz, w=spr.shape[1], rx=rx, ry=ry, rz=rz, cam=cam, opacity=op)

    # seam connector
    cp = pop(t, 0.8, 0.5)
    if cp > 0 and ex < 1:
        pulse = (t * 0.8) % 1.0
        ring = ring_sprite(260, 60, 3, ORANGE2)
        draw(cv, ring, 540, 1000, scale=(0.55 + pulse * 1.2) * cp, opacity=(1 - pulse) * 0.8 * (1 - ex), mode='add')
        draw(cv, connector(), 540, 1000, scale=cp * (1 - ex * 0.6), rot=(1 - cp) * 90, opacity=1 - ex)

    # front 3D decor
    obj3d(cv, 'blob_bear', t, 130 + wobble(t, 0.35, 4) - ex * 400, 1470 + wobble(t, 0.45, 6) + ex * 300,
          165 * pop(t, 1.15), rot=-8, t_off=0.7)
    obj3d(cv, 'sphere', t, 985 + wobble(t, 0.2, 5) + ex * 300, 1510 + wobble(t, 0.3, 8) + ex * 400,
          150 * pop(t, 1.3), rot=0)
    obj3d(cv, 'torus', t, 975 + wobble(t, 0.25, 6) + ex * 300, 225 + wobble(t, 0.3, 8) - ex * 300,
          185 * pop(t, 0.7), blur=1.5, rot=-15)

    # --- headline
    l1, l2, size = hook_words()
    bc = chip('brand')
    bp = e_out_expo(prog(t, 0.3, 0.8))
    draw(cv, bc, 540, 205 + (1 - bp) * 30 - ex * 90, opacity=bp * (1 - ex))
    draw_words(cv, l1, 540, 300, t, 0.42, exit_t=6.45)
    draw_words(cv, l2, 540, 300 + size * 1.18, t, 0.62, exit_t=6.5, glow=ORANGE)

    # --- CTA
    ctp = pop(t, 1.35, 0.55, 1.8)
    if ctp > 0:
        cta = chip('cta')
        y = 1572 + (1 - min(ctp, 1)) * 40 + ex * 200
        op = min(1, ctp * 1.5) * (1 - ex)
        glowc = cta_glow()
        draw(cv, glowc, 540, y + 10, scale=ctp, opacity=op * (0.55 + 0.25 * math.sin(t * 5)), mode='add')
        s = ctp * (1 + 0.025 * math.sin(t * 5))
        draw(cv, cta, 540, y, scale=s, opacity=op)
        ph = ((t - 1.6) % 1.9) / 1.2
        if 0 < ph < 1:
            draw(cv, pill_sheen(cta, ph), 540, y, scale=s, opacity=op, mode='add')

    # light streaks
    light_streak(cv, t, 0.0, 1000, 0.6, 1.2)
    light_streak(cv, t, HOOK_CUT - 0.2, 1000, 0.4, 1.0, direction=-1)

@functools.lru_cache(maxsize=None)
def cta_glow():
    c = chip('cta')
    return glow_of(c, 22, ORANGE, 1.0)

@functools.lru_cache(maxsize=None)
def connector():
    n = 92
    d = rrect_alpha(n, n, n / 2, 20)
    body = sdf_fill(d)
    rgb = vgrad(body.shape[0], body.shape[1], hexc('#FFA040'), hexc('#FF4A00'))
    spr = np.concatenate([rgb * body[..., None], body[..., None]], 2).astype(np.float32)
    spr = over_spr(spr, solid(sdf_stroke(d, 3), (0.05, 0.04, 0.03, 1)))
    ic = star_icon(40)
    tmp = np.zeros_like(spr)
    composite_spr(tmp, ic, spr.shape[1] // 2 - ic.shape[1] // 2, spr.shape[0] // 2 - ic.shape[0] // 2)
    spr = over_spr(spr, tmp)
    g = cv2.GaussianBlur(solid(body, ORANGE), (0, 0), 14)
    return over_spr(g * 0.9, spr)

# ============================================================== SCENE 2: HERE'S HOW (6.6 - 8.8)

HOW_T0 = 6.78

@functools.lru_cache(maxsize=None)
def how_letters():
    a = [text_sprite(ch, 'Unbounded-900', 128) for ch in "HERE'S"]
    b = [text_sprite(ch, 'Unbounded-900', 300, grad=(hexc('#FFB347'), hexc('#FF4200'))) for ch in 'HOW']
    return a, b

def slam_line(cv, letters, cy, t, t0, stagger=0.05, trk=0.0, sx=0, sy=0, ex=0.0):
    widths = [l.shape[1] for l in letters]
    total = sum(widths) + trk * (len(letters) - 1)
    x = 540 - total / 2
    for i, l in enumerate(letters):
        p = e_out_expo(prog(t, t0 + i * stagger, t0 + i * stagger + 0.32))
        if p > 0:
            sc = lerp(2.6, 1.0, p) * (1 + ex * 1.8)
            op = min(1, p * 2.5) * (1 - ex)
            bl = (1 - p) * 6
            spr = blur_sprite(l, bl) if bl > 0.5 else l
            cx = x + widths[i] / 2
            cx = 540 + (cx - 540) * (1 + ex * 1.2)
            draw(cv, spr, cx + sx, cy + sy + (1 - p) * -40, scale=sc, opacity=op)
        x += widths[i] + trk

def scene_how(cv, t, cam):
    lt = t
    ex = e_in_expo(prog(t, 8.42, 8.78))
    ent = prog(t, 6.6, 6.95)
    sx, sy = shake(t, [HOW_T0 + 0.3, HOW_T0 + 0.62], amp=9)
    # blobs pop around
    for i, (nm, x, y, s, t0, rot) in enumerate([('blob_flower', 185, 640, 175, 7.05, -10), ('blob_cube', 905, 625, 150, 7.15, 8),
                                                 ('blob_drop', 170, 1345, 150, 7.25, -6), ('blob_bear', 915, 1330, 175, 7.35, 10)]):
        pp = pop(t, t0, 0.5)
        if pp <= 0:
            continue
        dx, dy = (x - 540), (y - 960)
        obj3d(cv, nm, t, x + dx * ex * 1.5 + wobble(t, 0.5, 5, i), y + dy * ex * 1.5 + wobble(t, 0.6, 7, i),
              s * pp * (1 + ex), rot=rot, t_off=i * 0.37, opacity=1 - ex)
    a, b = how_letters()
    slam_line(cv, a, 800, t, HOW_T0, 0.04, 6, sx, sy, ex)
    slam_line(cv, b, 1010, t, HOW_T0 + 0.28, 0.07, 10, sx, sy, ex)
    cp = e_out_expo(prog(t, 7.45, 7.95))
    draw(cv, chip('steps'), 540 + sx, 1225 + (1 - cp) * 40 + sy, opacity=cp * (1 - ex))

# ============================================================== SCENE 3: STEPS (8.5 - 21.7)

STEP_B = [8.6, 11.4, 14.8, 19.2, 21.6]
WIN_W = 1000
WIN_BAR = 48
WIN_CH = int(round(WIN_W * 958 / 1920))    # 499
WIN_H = WIN_BAR + WIN_CH
WIN_C = (540, 935)
CLONE_T0 = 16.15
CLONE_T1 = 17.95

TITLES = [('OPEN', 'GENJUTSU'), ('PICK A', 'MOTION VIDEO'), ('ADD YOUR', 'CHARACTER'), ('HIT', 'GENERATE')]
SUBS = ['higgsfield.ai  →  Genjutsu  →  Motion transfer', 'Choose any clip from the Motion Library',
        'Drop in your character sheet', 'Set quality to 1080p, then generate']

def step_of(t):
    for i in range(4):
        if t < STEP_B[i + 1]:
            return i
    return 3

def step_src(t):
    """Returns (src_time, zoom, cx, cy, dim) for the window content at out-time t."""
    i = step_of(t)
    lt = t - STEP_B[i]
    if i == 0:
        src = 12.25 + lt
        p = e_inout_cubic(prog(lt, 0.35, 2.1))
        return src, lerp(1.0, 1.75, p), lerp(960, 560, p), lerp(479, 300, p), 0.0
    if i == 1:
        src = 19.55 + lt * 1.12
        p = e_inout_cubic(prog(lt, 1.55, 2.5))
        return src, lerp(1.04, 2.1, p), lerp(960, 1480, p), lerp(479, 760, p), 0.0
    if i == 2:
        if t < CLONE_T1:
            src = min(27.3 + lt, 28.75 + (lt - 1.45) * 0.4) if lt > 1.45 else 27.3 + lt
            p = e_inout_cubic(prog(lt, 0.1, 1.1))
            dim = 0.6 * smooth(prog(t, CLONE_T0 - 0.05, CLONE_T0 + 0.25)) * (1 - smooth(prog(t, CLONE_T1 - 0.2, CLONE_T1)))
            return src, lerp(1.0, 1.7, p), lerp(960, 520, p), lerp(479, 520, p), dim
        src = 57.72 + (t - CLONE_T1)
        return src, 1.7, 520, 520, 0.0
    src = 62.0 + lt
    p = e_inout_cubic(prog(lt, 0.0, 0.5))
    return src, lerp(1.7, 2.3, p), lerp(520, 420, p), lerp(520, 780, p), 0.0

CLICKS = [  # (out_time, crop_u, crop_v)
    (8.6 + 22.85 - 19.55 + 2.85 - 2.85 + 0.0, 0, 0),
]
CLICKS = [
    (11.4 + (22.85 - 19.55) / 1.12, 1712, 900),          # Recreate
    (14.8 + 1.3, 396, 492),                               # Upload media
    (CLONE_T1 + (57.86 - 57.72), 558, 474),               # select uploaded character
    (19.2 + 0.10, 120, 862),                              # quality
    (19.2 + 1.50, 392, 866),                              # 1080p
    (19.2 + 2.25, 176, 934),                              # Generate
]

@functools.lru_cache(maxsize=None)
def window_bar():
    w, h = WIN_W, WIN_BAR
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = np.array([0.075, 0.066, 0.06], np.float32)
    spr[..., 3] = 1
    # traffic lights
    for k, col in enumerate([ORANGE, (0.36, 0.33, 0.3, 1), (0.36, 0.33, 0.3, 1)]):
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt((xs - (26 + k * 22)) ** 2 + (ys - h / 2) ** 2)
        a = np.clip(6.5 - d, 0, 1)
        spr = over_spr(spr, solid(a, col))
    url = pill('higgsfield.ai/ai/video?model=genjutsu', 'Inter-500', 19, pad_x=16, pad_y=8,
               fill=(1, 1, 1, 0.06), border=None, text_color=hexc('#CFC8C0'), icon=logomark_icon(16))
    composite_spr(spr, url, w // 2 - url.shape[1] // 2, h // 2 - url.shape[0] // 2)
    spr[-1:, :, :3] = 0.14
    return spr

def window_content(t):
    src, z, cx, cy, dim = step_src(t)
    fr = scr_frame(src)
    vw, vh = 1920 / z, 958 / z
    img = crop_resize(fr, cx, cy, vw, vh, WIN_W, WIN_CH)
    return img, (src, z, cx, cy, dim)

def content_whip(t):
    """Horizontal whip between steps (returns content rgb)."""
    for b in STEP_B[1:4]:
        a0, a1 = b - 0.16, b + 0.16
        if a0 <= t <= a1:
            p = e_inout_expo(prog(t, a0, a1))
            old, _ = window_content(a0 - 0.001)
            new, _ = window_content(a1)
            st = np.concatenate([old, new], 1)
            off = int(round(p * WIN_W))
            return st[:, off:off + WIN_W], None
    return window_content(t)

def win_pose(t):
    i = step_of(t)
    ry_tgt = [-9, 9, -8, 8][i]
    # blend ry across boundaries
    ry = ry_tgt
    for k, b in enumerate(STEP_B[1:4]):
        prev = [-9, 9, -8, 8][k]
        nxt = [-9, 9, -8, 8][k + 1]
        if b - 0.35 <= t <= b + 0.35:
            ry = lerp(prev, nxt, e_inout_cubic(prog(t, b - 0.35, b + 0.35)))
    rx = 7 + wobble(t, 0.17, 1.5)
    ry += wobble(t, 0.13, 1.5)
    ent = e_out_expo(prog(t, 8.5, 9.2))
    ext = e_in_expo(prog(t, 21.45, 21.7))
    cz = lerp(1400, 0, ent) - ext * 400
    rx += (1 - ent) * 30
    return WIN_C[0], WIN_C[1] + wobble(t, 0.2, 6), cz, rx, ry, ent, ext

def build_window(t):
    img, info = content_whip(t)
    dim = step_src(t)[4] if info is None else info[4]
    bar = window_bar()
    rgb = np.concatenate([bar[..., :3], img * (1 - dim)], 0)
    spr = make_card(rgb, WIN_W, WIN_H, r=22, P=50, glow=0.45)
    return spr

def win_point(t, u, v, quad_M):
    """Map crop coords (u,v) of current content to screen via window homography."""
    src, z, cx, cy, dim = step_src(t)
    vw, vh = 1920 / z, 958 / z
    x0 = clamp(cx - vw / 2, 0, 1920 - vw)
    y0 = clamp(cy - vh / 2, 0, 958 - vh)
    px = (u - x0) * WIN_W / vw
    py = (v - y0) * WIN_CH / vh + WIN_BAR
    return apply_h(quad_M, px + 50, py + 50)

@functools.lru_cache(maxsize=None)
def title_sprites(i):
    l1 = word_sprites(TITLES[i][0], 'Unbounded-800', 70)
    l2 = word_sprites(TITLES[i][1], 'Unbounded-800', 70, grad=(hexc('#FFB347'), hexc('#FF4D00')))
    sub = text_sprite(SUBS[i], 'Inter-500', 30, MUTED)
    lab = text_sprite(f'STEP 0{i + 1}', 'JetBrainsMono-700', 26, ORANGE2, 0.08)
    return l1, l2, sub, lab

@functools.lru_cache(maxsize=None)
def of4():
    return text_sprite('/ 04', 'JetBrainsMono-700', 26, hexc('#5E5750'), 0.08)

def progress_bar(cv, t, op):
    segw, gap, h = 196, 12, 6
    x0 = 540 - (4 * segw + 3 * gap) / 2
    for k in range(4):
        fill = prog(t, STEP_B[k] + 0.1, STEP_B[k + 1])
        bgc = np.zeros((h + 8, segw + 8, 4), np.float32)
        d = rrect_alpha(segw, h, h / 2, 4)
        track = solid(sdf_fill(d), (1, 1, 1, 0.12))
        composite(cv, track, int(x0 + k * (segw + gap)) - 4, 262 - 4, op)
        if fill > 0:
            fw = max(h, int(segw * fill))
            d2 = rrect_alpha(fw, h, h / 2, 4)
            fs = solid(sdf_fill(d2), ORANGE2)
            composite(cv, fs, int(x0 + k * (segw + gap)) - 4, 262 - 4, op)
            composite(cv, glow_bar(fw), int(x0 + k * (segw + gap)) - 14, 262 - 14, op * 0.8, 'add')

@functools.lru_cache(maxsize=64)
def glow_bar(fw):
    d = rrect_alpha(fw, 6, 3, 14)
    return cv2.GaussianBlur(solid(sdf_fill(d), ORANGE), (0, 0), 6)

HELP = [('blob_drop', 'help1'), ('blob_flower', 'help2'), ('blob_bear', 'help3'), ('blob_cube', 'help4')]

def scene_steps(cv, t, cam):
    i = step_of(t)
    cx, cy, cz, rx, ry, ent, ext = win_pose(t)
    op_all = prog(t, 8.5, 8.8) * (1 - prog(t, 21.55, 21.7))

    # far decor
    obj3d(cv, 'torus', t, 985 + wobble(t, 0.2, 10), 520 + wobble(t, 0.25, 12), 170, blur=6, rot=20, opacity=0.8 * op_all)
    obj3d(cv, 'capsule', t, 80 + wobble(t, 0.22, 8), 1545 + wobble(t, 0.2, 10), 150, blur=5, rot=30, opacity=0.8 * op_all)

    # window
    spr = build_window(t)
    q = draw3d(cv, spr, cx, cy, cz, w=spr.shape[1], rx=rx, ry=ry, cam=cam, opacity=op_all)
    M = homography_for(spr.shape[1], spr.shape[0], q)

    # annotation for step 1: highlight genjutsu card
    if i == 0:
        ap = e_out_expo(prog(t, 10.2, 10.6))
        if ap > 0:
            p0 = win_point(t, 22, 96, M)
            p1 = win_point(t, 330, 236, M)
            hl = highlight_box(int(p1[0] - p0[0]), int(p1[1] - p0[1]))
            draw(cv, hl, (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, scale=lerp(1.15, 1, ap), opacity=ap * op_all)

    # clicks: cursor + ripple
    for (tc, u, v) in CLICKS:
        if tc - 0.6 <= t <= tc + 0.6 and step_of(tc) == i:
            if t < STEP_B[i] + 0.02 and tc - STEP_B[i] < 0.3 and False:
                continue
            px, py = win_point(t, u, v, M)
            cursor_click(cv, t, tc, px, py, op_all)

    # step 3 clone sequence
    if CLONE_T0 - 0.05 <= t <= CLONE_T1 + 0.05:
        clone_seq(cv, t, M)

    # helper pill + blob
    hp = e_out_expo(prog(t, STEP_B[i] + 0.35, STEP_B[i] + 0.8))
    hx = e_in_expo(prog(t, STEP_B[i + 1] - 0.3, STEP_B[i + 1] - 0.05)) if i < 3 else e_in_expo(prog(t, 21.3, 21.55))
    if hp > 0:
        nm, key = HELP[i]
        pl = chip(key)
        pw = pl.shape[1]
        total = 130 + pw
        x0 = 540 - total / 2
        yb = 1335 + (1 - hp) * 50 + hx * 30
        o = hp * (1 - hx) * op_all
        obj3d(cv, nm, t, x0 + 60, yb - 6 + wobble(t, 0.6, 4), 125 * pop(t, STEP_B[i] + 0.35, 0.5), rot=-6, opacity=o, t_off=i)
        draw(cv, pl, x0 + 130 + pw / 2 - 10, yb, opacity=o)

    # front decor
    obj3d(cv, 'sphere', t, 985 + wobble(t, 0.2, 6), 1215 + wobble(t, 0.3, 8), 120, blur=0, opacity=op_all)
    obj3d(cv, 'rcube', t, 90 + wobble(t, 0.3, 6), 640 + wobble(t, 0.2, 10), 110, blur=2.5, rot=-12, opacity=op_all)

    # titles
    l1, l2, sub, lab = title_sprites(i)
    t0 = STEP_B[i] + (0.05 if i > 0 else 0.35)
    exit_t = STEP_B[i + 1] - 0.28 if i < 3 else 21.35
    lab_p = e_out_expo(prog(t, t0 - 0.05, t0 + 0.35))
    lab_x = e_in_expo(prog(t, exit_t, exit_t + 0.25))
    o4 = of4()
    tw = lab.shape[1] + 14 + o4.shape[1]
    draw(cv, lab, 540 - tw / 2 + lab.shape[1] / 2, 212 + (1 - lab_p) * 20 - lab_x * 30, opacity=lab_p * (1 - lab_x) * op_all)
    draw(cv, o4, 540 + tw / 2 - o4.shape[1] / 2, 212 + (1 - lab_p) * 20 - lab_x * 30, opacity=lab_p * (1 - lab_x) * op_all)
    progress_bar(cv, t, op_all * prog(t, 8.6, 9.0))
    draw_words(cv, l1, 540, 345, t, t0, exit_t=exit_t, opacity=op_all)
    draw_words(cv, l2, 540, 432, t, t0 + 0.08, exit_t=exit_t + 0.03, opacity=op_all, glow=ORANGE)
    sp = e_out_expo(prog(t, t0 + 0.25, t0 + 0.7))
    sx_ = e_in_expo(prog(t, exit_t, exit_t + 0.25))
    draw(cv, sub, 540, 510 + (1 - sp) * 20, opacity=sp * (1 - sx_) * op_all)

    # generate burst
    tg = CLICKS[-1][0]
    if tg <= t <= tg + 0.5:
        p = prog(t, tg, tg + 0.45)
        px, py = win_point(tg, 176, 934, M)
        rs = ring_sprite(400, 180, 6, ORANGE2, glow=14)
        draw(cv, rs, px, py, scale=0.2 + e_out_expo(p) * 7, opacity=(1 - p), mode='add')

@functools.lru_cache(maxsize=None)
def highlight_box(w, h):
    w, h = max(w, 20), max(h, 20)
    d = rrect_alpha(w, h, 14, 24)
    st = solid(sdf_stroke(d, 3.0), ORANGE2)
    g = cv2.GaussianBlur(solid(sdf_stroke(d, 4.0), ORANGE), (0, 0), 8)
    fill = solid(sdf_fill(d), (1, 0.45, 0.1, 0.10))
    return over_spr(over_spr(fill, g * 1.2), st)

@functools.lru_cache(maxsize=None)
def cursor_tip():
    a = seq('cursor3d').frame(0)[..., 3]
    ys, xs = np.where(a > 0.5)
    y = ys.min()
    return float(xs[ys <= y + 3].min()), float(y)

def cursor_click(cv, t, tc, px, py, op=1.0):
    ap = e_out_cubic(prog(t, tc - 0.55, tc - 0.06))
    fade = 1 - prog(t, tc + 0.28, tc + 0.5)
    cur = seq('cursor3d').frame(0)
    ch, cw = cur.shape[:2]
    tipx, tipy = cursor_tip()
    x = lerp(px + 160, px, ap)
    y = lerp(py + 210, py, ap)
    press = 1 - 0.18 * math.sin(math.pi * prog(t, tc - 0.06, tc + 0.14))
    sc = 64 / cw * press
    # cursor tip in sprite ~ (0.3w, 0.2h)
    o = min(1, prog(t, tc - 0.55, tc - 0.35) * 1.0) * fade * op
    if t >= tc:
        p = prog(t, tc, tc + 0.5)
        draw(cv, ring_sprite(240, 100, 4, ORANGE2, 8), px, py, scale=0.15 + e_out_expo(p) * 0.85, opacity=(1 - p) * op, mode='add')
        draw(cv, glow_white(), px, py, scale=0.9 * (1 - p) + 0.2, opacity=(1 - p) * 0.9 * op, mode='add')
    if o > 0:
        draw(cv, cur, x + (cw / 2 - tipx) * sc, y + (ch / 2 - tipy) * sc, scale=sc, opacity=o)

# ---- character sheet clone -------------------------------------------------

SHEET_PANELS = [  # x0,x1,y0,y1 in 3840x2160
    (914, 1698, 0, 1071), (1709, 2449, 0, 1071), (2459, 3147, 0, 1071), (3155, 3840, 0, 1071),
    (0, 903, 0, 2160),
    (914, 1698, 1080, 2160), (1709, 2449, 1080, 2160), (2459, 3147, 1080, 2160), (3155, 3840, 1080, 2160),
]

@functools.lru_cache(maxsize=None)
def sheet_img():
    im = cv2.imread(S + '/src/charsheet.png')[..., ::-1].astype(np.float32) / 255
    return im

@functools.lru_cache(maxsize=None)
def sheet_card():
    im = cv2.resize(sheet_img(), (960, 540), interpolation=cv2.INTER_AREA)
    return make_card(im, 960, 540, r=26, P=50, glow=0.6)

@functools.lru_cache(maxsize=None)
def panel_card(k, hpx=345):
    x0, x1, y0, y1 = SHEET_PANELS[k]
    sub = sheet_img()[y0:y1, x0:x1]
    h = hpx if k != 4 else int(hpx * 1.25)
    w = int(round(h * (x1 - x0) / (y1 - y0)))
    im = cv2.resize(sub, (w, h), interpolation=cv2.INTER_AREA)
    return make_card(im, w, h, r=18, P=50, glow=0.55)

def clone_seq(cv, t, M):
    u = t - CLONE_T0
    tile = win_point(CLONE_T1 + 0.2, 558, 474, M)
    src_pt = win_point(t, 396, 492, M)
    card = sheet_card()
    PW = card.shape[1]
    if u < 0.78:
        a = e_out_expo(prog(u, 0.0, 0.5))
        cx = lerp(src_pt[0], 540, a)
        cy = lerp(src_pt[1], 960, a)
        w = lerp(90, 960, a) * (PW / 960)
        rx = lerp(40, 0, a) + wobble(t, 0.3, 3)
        ry = lerp(-30, 0, a) + wobble(t, 0.25, 4)
        op = prog(u, 0.0, 0.08)
        draw3d(cv, card, cx, cy, -80 * a, w=w, rx=rx, ry=ry, opacity=op)
        lp = e_out_back(prog(u, 0.28, 0.6))
        if lp > 0:
            draw(cv, chip('sheet'), 540, 620 - (1 - lp) * 30, scale=0.8 + 0.2 * lp, opacity=min(1, lp))
        return
    # split into 9 clones -> fan -> fly into upload tile
    order = [0, 1, 5, 6, 4, 2, 7, 3, 8]
    fan_p = e_out_expo(prog(u, 0.78, 1.28))
    fly_p = prog(u, 1.36, 1.8)
    lp = 1 - prog(u, 1.2, 1.4)
    if lp > 0:
        draw(cv, chip('sheet'), 540, 620 - (1 - lp) * 20, opacity=lp)
    items = []
    for slot, k in enumerate(order):
        x0, x1, y0, y1 = SHEET_PANELS[k]
        sc = 960 / 3840
        sx = 540 + ((x0 + x1) / 2 - 1920) * sc
        sy = 960 + ((y0 + y1) / 2 - 1080) * sc
        sw = (x1 - x0) * sc
        ang = lerp(-30, 30, slot / 8)
        R = 740
        fx = 540 + math.sin(math.radians(ang)) * R
        fy = 1000 + (1 - math.cos(math.radians(ang))) * R * 0.9 - 40
        pc = panel_card(k)
        ph, pw_ = pc.shape[:2]
        fw = pw_ * (0.78 if k != 4 else 0.9)
        cxk = lerp(sx, fx, fan_p)
        cyk = lerp(sy, fy, fan_p)
        wk = lerp(sw * pw_ / (pw_ - 100), fw, fan_p)
        rz = ang * fan_p
        cz = -80 + abs(slot - 4) * 40 * fan_p
        # fly into the tile, staggered
        fp = e_in_expo(prog(fly_p, slot * 0.05, 0.6 + slot * 0.05))
        cxk = lerp(cxk, tile[0], fp)
        cyk = lerp(cyk, tile[1], fp)
        wk = lerp(wk, 60, fp)
        rz = lerp(rz, 0, fp)
        cz = lerp(cz, 0, fp)
        op = 1 - prog(fp, 0.85, 1.0)
        bob = wobble(t, 0.8, 6, slot) * fan_p * (1 - fp)
        items.append((cz, pc, cxk, cyk + bob, wk, rz, op, fan_p))
    items.sort(key=lambda it: -it[0])
    for cz, pc, x, y, w, rz, op, fp in items:
        draw3d(cv, pc, x, y, cz, w=w, rz=rz, ry=wobble(t, 0.5, 6) * fp, opacity=op)
    if fly_p > 0.2:
        pp = prog(fly_p, 0.2, 1.0)
        draw(cv, glow_white(), tile[0], tile[1], scale=1.5 * math.sin(pp * math.pi) + 0.1,
             opacity=math.sin(pp * math.pi), mode='add')

# ============================================================== SCENE 4: PAYOFF (21.55 - 24.45)

PAY_T0 = 21.6
BIG_W, BIG_H = 940, 1175
BIG_C = (540, 1030)

def pay_src(t):
    return 0.25 + (t - PAY_T0)

def big_card_rgb(t):
    s = pay_src(t)
    fr = RES.get(s)
    half = fr[1080:2160]
    cx = lerp(740, 1060, smooth(prog(s, 0.6, 2.6)))
    img = crop_resize(half, cx, 452, 724, 905, BIG_W, BIG_H)
    bl = cv2.GaussianBlur(img, (0, 0), 1.4)
    return np.clip(img + 0.6 * (img - bl), 0, 1)

@functools.lru_cache(maxsize=None)
def pay_words():
    l1 = word_sprites('ONE CHARACTER.', 'Unbounded-900', 72)
    l2 = word_sprites('ANY SCENE.', 'Unbounded-900', 72, grad=(hexc('#FFB347'), hexc('#FF4D00')))
    return l1, l2

def scene_pay(cv, t, cam):
    ent = e_out_expo(prog(t, PAY_T0, PAY_T0 + 0.5))
    ex = prog(t, 24.15, 24.45)
    # decor behind
    obj3d(cv, 'blob_flower', t, 915 + wobble(t, 0.4, 5), lerp(590, 478, e_out_back(prog(t, 22.2, 22.7))) + wobble(t, 0.5, 5),
          165, rot=10, t_off=0.2, opacity=1 - ex)
    obj3d(cv, 'torus', t, 70, 700 + wobble(t, 0.3, 10), 190 * pop(t, 22.0), blur=3, rot=-25, opacity=1 - ex)
    if t < 24.2:
        rgb = big_card_rgb(t)
        o_badge = e_out_back(prog(t, 22.0, 22.4))
        ob = chip('output')
        k8 = chip('1080')
        spr = make_card(rgb, BIG_W, BIG_H, r=34, P=50, glow=0.6,
                        badges=[(ob, 28 + ob.shape[1] / 2 - 30, 50, 0.6 + 0.4 * o_badge, min(1, o_badge * 1.4)),
                                (k8, BIG_W - 26 - k8.shape[1] / 2 + 30, 50, 0.6 + 0.4 * o_badge, min(1, o_badge * 1.4))])
        push = (t - PAY_T0) * 18
        cz = lerp(900, 0, ent) - push
        rx = lerp(-28, 0, ent) + wobble(t, 0.2, 1.2)
        ry = wobble(t, 0.16, 2.0)
        draw3d(cv, spr, BIG_C[0], BIG_C[1], cz, w=spr.shape[1], rx=rx, ry=ry, cam=cam, opacity=prog(t, PAY_T0, PAY_T0 + 0.12))
        # PiP original
        pp = e_out_back(prog(t, 22.25, 22.75), 1.6)
        if pp > 0:
            fr = RES.get(pay_src(t))
            small = cv2.resize(fr[40:900, 175:1745], (340, 186), interpolation=cv2.INTER_AREA)
            och = chip('original')
            pip = make_card(small, 340, 186, r=18, P=50, glow=0.2,
                            badges=[(och, 14 + och.shape[1] * 0.75 / 2 - 22, 28, 0.75, 1.0)])
            draw3d(cv, pip, lerp(-200, 215, pp), 1545 + wobble(t, 0.3, 4), -40, w=pip.shape[1], rz=-4 + wobble(t, 0.3, 1.5),
                   ry=8, cam=cam)
    obj3d(cv, 'blob_cube', t, 935 + wobble(t, 0.4, 5), 1580 + wobble(t, 0.5, 6), 150 * pop(t, 22.45), rot=8, t_off=0.5,
          opacity=1 - ex)
    obj3d(cv, 'sphere', t, 120 + wobble(t, 0.3, 5), 1790, 130 * pop(t, 22.6), opacity=1 - ex)
    l1, l2 = pay_words()
    draw_words(cv, l1, 540, 262, t, 21.8, exit_t=23.8, exit_dur=0.28)
    draw_words(cv, l2, 540, 350, t, 21.95, exit_t=23.83, exit_dur=0.28, glow=ORANGE)

# ============================================================== SCENE 5: CLONE WALL (24.15 - 26.1)

WALL_COLS, WALL_ROWS = 5, 7
TILE_W, TILE_H, TILE_G = 300, 375, 28
WALL_T0 = 24.15

@functools.lru_cache(maxsize=None)
def wall_tex():
    Wt = WALL_COLS * TILE_W + (WALL_COLS - 1) * TILE_G
    Ht = WALL_ROWS * TILE_H + (WALL_ROWS - 1) * TILE_G
    P = 40
    tex = np.zeros((Ht + 2 * P, Wt + 2 * P, 4), np.float32)
    rng = np.random.default_rng(11)
    sheet = sheet_img()
    gen_times = [0.4, 1.0, 1.6, 2.2, 4.5, 6.5, 9.0, 12.0, 16.0, 21.2, 22.0, 23.0, 25.5, 26.5]
    idx = 0
    cells = []
    for r in range(WALL_ROWS):
        for c in range(WALL_COLS):
            cells.append((r, c))
    center = (WALL_ROWS // 2, WALL_COLS // 2)
    kinds = []
    for (r, c) in cells:
        if (r, c) == center:
            kinds.append(('gen', 2.85))
            continue
        m = (r * 7 + c * 3) % 5
        if m in (0, 2):
            kinds.append(('panel', (r * 5 + c) % 9))
        elif m in (1, 3):
            kinds.append(('gen', gen_times[(r * 3 + c) % len(gen_times)]))
        else:
            kinds.append(('accent', (r + c) % 3))
    d = rrect_alpha(TILE_W, TILE_H, 22, 0)
    mask = sdf_fill(d)
    stroke = sdf_stroke(d, 2.0)
    for (r, c), (kind, val) in zip(cells, kinds):
        x0 = P + c * (TILE_W + TILE_G)
        y0 = P + r * (TILE_H + TILE_G)
        if kind == 'panel':
            px0, px1, py0, py1 = SHEET_PANELS[val]
            sub = sheet[py0:py1, px0:px1]
            sh_, sw_ = sub.shape[:2]
            # cover crop to 4:5
            tw_ = min(sw_, int(sh_ * 0.8))
            th_ = int(tw_ / 0.8)
            ox = (sw_ - tw_) // 2
            sub = sub[0:th_, ox:ox + tw_]
            img = cv2.resize(sub, (TILE_W, TILE_H), interpolation=cv2.INTER_AREA)
            col = (1, 0.55, 0.2, 0.7)
        elif kind == 'gen':
            fr = RES.get(val)[1080:2160]
            cxx = 1060 if abs(val - 2.85) < 1e-3 else (900 if val < 3 else 960)
            img = crop_resize(fr, cxx, 452, 724, 905, TILE_W, TILE_H)
            col = (1, 1, 1, 0.22)
        else:
            base = [hexc('#FF6A00'), hexc('#161311'), hexc('#FF8A1F')][val]
            img = vgrad(TILE_H, TILE_W, base, (base[0] * 0.6, base[1] * 0.5, base[2] * 0.5, 1))
            col = (1, 1, 1, 0.3)
        spr = rgb_to_sprite(img, mask)
        spr = over_spr(spr, solid(stroke, col))
        if kind == 'accent':
            bl = seq(['blob_bear', 'blob_drop', 'blob_flower'][val]).frame(0.3 * val)
            bl = cv2.resize(bl, (200, 200), interpolation=cv2.INTER_AREA)
            composite_spr(spr, bl, TILE_W // 2 - 100, TILE_H // 2 - 110)
        composite_spr(tex, spr, x0, y0)
    return tex, Wt, Ht, P

@functools.lru_cache(maxsize=None)
def wall_words():
    l1 = word_sprites('CLONE YOURSELF', 'Unbounded-900', 76)
    l2 = word_sprites('INTO ANY VIDEO', 'Unbounded-900', 76, grad=(hexc('#FFB347'), hexc('#FF4D00')))
    return l1, l2

@functools.lru_cache(maxsize=None)
def text_band():
    h = 520
    y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    a = np.exp(-(y * 1.9) ** 4) * np.ones((1, W), np.float32)
    return np.concatenate([np.zeros((h, W, 3), np.float32), a[..., None]], 2)

@functools.lru_cache(maxsize=None)
def dark_band():
    return radial_sprite(512, (0, 0, 0), power=1.3)

def scene_wall(cv, t, cam):
    tex, Wt, Ht, P = wall_tex()
    u = t - WALL_T0
    p = e_inout_expo(prog(u, 0.0, 0.85))
    ex = e_in_expo(prog(t, 25.75, 26.15))
    s0 = BIG_W / TILE_W
    s1 = 0.62
    sc = lerp(s0, s1, p)
    rx = lerp(0, 32, p) + ex * 25
    rz = lerp(0, -9, p)
    drift = max(0, u - 0.6) * 60
    cy = BIG_C[1] - drift * math.cos(math.radians(rx)) + ex * -300
    cz = ex * 1600 - max(0, u - 0.85) * 60
    w = (Wt + 2 * P) * sc
    op = 1 - prog(t, 25.95, 26.15)
    draw3d(cv, tex, BIG_C[0], cy, cz, w=w, rx=rx, rz=rz, cam=cam, opacity=op)
    # vignette band behind text
    bp = prog(u, 0.3, 0.6) * (1 - ex)
    if bp > 0:
        draw(cv, text_band(), 540, 935, opacity=0.9 * bp)
        l1, l2 = wall_words()
        draw_words(cv, l1, 540, 890, t, WALL_T0 + 0.4, stagger=0.06, exit_t=25.8)
        draw_words(cv, l2, 540, 985, t, WALL_T0 + 0.5, stagger=0.06, exit_t=25.82, glow=ORANGE)

# ============================================================== SCENE 6: OUTRO (25.9 - 30)

OUT_T0 = 25.95

@functools.lru_cache(maxsize=None)
def out_words():
    l1 = word_sprites('WATCH THE FULL VIDEO', 'Unbounded-800', 54)
    l2 = word_sprites('FOR THE COMPLETE GUIDE', 'Unbounded-800', 54, grad=(hexc('#FFB347'), hexc('#FF4D00')))
    return l1, l2

@functools.lru_cache(maxsize=None)
def logo_glow():
    sp = seq('logo3d').frame(10)
    return glow_of(sp, 40, (1, 0.55, 0.2), 0.8)

def scene_out(cv, t, cam):
    u = t - OUT_T0
    # far decor
    obj3d(cv, 'torus', t, 110 + wobble(t, 0.2, 8), 330 + wobble(t, 0.25, 10), 230 * pop(t, OUT_T0 + 0.3), blur=5, rot=-25)
    obj3d(cv, 'capsule', t, 960, 1720 + wobble(t, 0.2, 10), 170 * pop(t, OUT_T0 + 0.5), blur=6, rot=35)
    obj3d(cv, 'rcube', t, 980 + wobble(t, 0.3, 6), 300, 120 * pop(t, OUT_T0 + 0.6), blur=4, rot=15)
    obj3d(cv, 'sphere', t, 95, 1650 + wobble(t, 0.25, 8), 150 * pop(t, OUT_T0 + 0.7), blur=2)
    # logo
    lg = seq('logo3d').frame(u)
    lp = prog(t, OUT_T0, OUT_T0 + 0.25)
    y = 820 + wobble(t, 0.3, 6) * prog(t, 28, 28.5)
    sc = 900 / lg.shape[1] * (1 + max(0, u - 2.0) * 0.012)
    glow_a = prog(t, OUT_T0 + 1.2, OUT_T0 + 2.0)
    if glow_a > 0:
        draw(cv, logo_glow(), 540, y, scale=sc, opacity=0.55 * glow_a, mode='add')
    draw(cv, lg, 540, y, scale=sc, opacity=lp)
    # blobs around the lockup
    for i, (nm, x, yy, s, t0, rot) in enumerate([('blob_flower', 150, 585, 150, 27.0, -10), ('blob_drop', 935, 590, 140, 27.1, 8),
                                                  ('blob_bear', 160, 1060, 160, 27.2, -6), ('blob_cube', 925, 1065, 130, 27.3, 10)]):
        pp = pop(t, t0, 0.5)
        if pp > 0:
            obj3d(cv, nm, t, x + wobble(t, 0.5, 5, i), yy + wobble(t, 0.6, 7, i), s * pp, rot=rot, t_off=i * 0.37)
    cp = e_out_expo(prog(t, 27.15, 27.6))
    draw(cv, chip('motion'), 540, 985 + (1 - cp) * 30, opacity=cp)

# ============================================================== SCENE 7: PROFILE ENDING (28.3 - 32)

ZT0, ZT1 = 28.3, 29.15
BADGE_T0 = 29.3
USER = '@jawad_mp4'

@functools.lru_cache(maxsize=None)
def avatar_img():
    im = cv2.imread(S + '/src/profile.webp')
    if im is None:
        from PIL import Image
        im = np.asarray(Image.open(S + '/src/profile.webp').convert('RGB'))[..., ::-1]
    im = im[..., ::-1].astype(np.float32) / 255
    h, w = im.shape[:2]
    side = int(min(w, h) * 0.74)
    cx, cy = int(w * 0.46), int(h * 0.44)
    sub = im[max(0, cy - side // 2):cy + side // 2, max(0, cx - side // 2):cx + side // 2]
    return cv2.resize(sub, (700, 700), interpolation=cv2.INTER_AREA)

@functools.lru_cache(maxsize=64)
def avatar_sprite(r):
    d = 2 * r
    img = cv2.resize(avatar_img(), (d, d), interpolation=cv2.INTER_AREA)
    ys, xs = np.mgrid[0:d, 0:d].astype(np.float32)
    dist = np.sqrt((xs - r + 0.5) ** 2 + (ys - r + 0.5) ** 2)
    return pad(rgb_to_sprite(img, np.clip(r - dist, 0, 1)), 2)

@functools.lru_cache(maxsize=64)
def ring_glow(r):
    return ring_sprite(2 * r + 80, r + 3, 5, ORANGE2, glow=10)

@functools.lru_cache(maxsize=None)
def badge_parts():
    name = text_sprite(USER, 'Unbounded-800', 50)
    sub = text_sprite('Follow for more AI tutorials', 'Inter-600', 28, hexc('#B8B0A6'))
    btn = pill('FOLLOW  +', 'Inter-900', 34, pad_x=46, pad_y=26, grad=(hexc('#FF9A2E'), hexc('#FF4A00')),
               border=(1, 0.85, 0.7, 0.55), tracking=0.08)
    return name, sub, btn

def zoom_state(t):
    p = e_inout_expo(prog(t, ZT0, ZT1))
    return p, lerp(1200, 120, p), lerp(960, 840, p), lerp(1.0, 0.16, p)

def profile_ending(cv, inner, t):
    """cv: fresh background; inner: the rendered reel frame to be zoomed out into the avatar circle."""
    p, r, cy, sc = zoom_state(t)
    cx = 540
    # badge phase: circle travels to the badge's left end
    bp = e_inout_cubic(prog(t, BADGE_T0, BADGE_T0 + 0.6))
    bx, by, br = 222, 900, 92
    cx, cy, r = lerp(cx, bx, bp), lerp(cy, by, bp), lerp(r, br, bp)
    # badge body grows out of the circle
    if bp > 0:
        name, sub, btn = badge_parts()
        bw = lerp(2 * br, 860, bp)
        bh = 2 * br + 36
        d = rrect_alpha(int(bw), int(bh), bh / 2, 40)
        body = solid(sdf_fill(d), (0.07, 0.06, 0.055, 0.92))
        body = over_spr(body, solid(sdf_stroke(d, 2.0), (1, 0.55, 0.2, 0.55)))
        gl = glow_bar_badge(int(bw), int(bh))
        composite(cv, gl, int(bx - br - 18 - 40 - 20), int(by - bh / 2 - 40 - 20), 0.9 * bp, 'add')
        composite(cv, body, int(bx - br - 18 - 40), int(by - bh / 2 - 40), 1.0)
        tp = e_out_expo(prog(t, BADGE_T0 + 0.35, BADGE_T0 + 0.85))
        tx = bx + br + 34
        draw(cv, name, tx + name.shape[1] / 2 + (1 - tp) * 40, by - 26, opacity=tp)
        sp = e_out_expo(prog(t, BADGE_T0 + 0.5, BADGE_T0 + 1.0))
        draw(cv, sub, tx + sub.shape[1] / 2 + (1 - sp) * 40, by + 34, opacity=sp)
        fp = pop(t, BADGE_T0 + 0.9, 0.5, 2.0)
        if fp > 0:
            bty = 1130
            draw(cv, cta_glow_btn(), 540, bty + 8, scale=fp, opacity=0.6 + 0.2 * math.sin(t * 5), mode='add')
            s_ = fp * (1 + 0.03 * math.sin(t * 5))
            draw(cv, btn, 540, bty, scale=s_)
            ph = ((t - BADGE_T0 - 1.2) % 1.6) / 1.1
            if 0 < ph < 1:
                draw(cv, pill_sheen(btn, ph), 540, bty, scale=s_, mode='add')
        for i, (nm, x, yy, sz, t0, rot) in enumerate([('blob_flower', 150, 640, 140, BADGE_T0 + 0.8, -10),
                                                     ('blob_drop', 940, 660, 130, BADGE_T0 + 0.9, 8),
                                                     ('blob_bear', 170, 1300, 150, BADGE_T0 + 1.0, -6),
                                                     ('blob_cube', 915, 1310, 120, BADGE_T0 + 1.1, 10)]):
            pp_ = pop(t, t0, 0.5)
            if pp_ > 0:
                obj3d(cv, nm, t, x + wobble(t, 0.5, 5, i), yy + wobble(t, 0.6, 7, i), sz * pp_, rot=rot, t_off=i * 0.37)
    # circle contents: zoomed-out reel frame, cross-fading to the avatar
    ri = int(max(8, r))
    x0, y0 = int(cx - ri), int(cy - ri)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + 2 * ri), min(H, y0 + 2 * ri)
    if X1 <= X0 or Y1 <= Y0:
        return
    M = np.float32([[sc, 0, cx - 540 * sc - X0], [0, sc, cy - 960 * sc - Y0]])
    roi = cv2.warpAffine(inner, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_AREA if sc < 0.9 else cv2.INTER_LINEAR)
    av_a = smooth(prog(t, ZT1 - 0.45, ZT1 + 0.05))
    if av_a > 0:
        av = cv2.resize(avatar_img(), (2 * ri, 2 * ri), interpolation=cv2.INTER_AREA)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
        roi = roi * (1 - av_a) + av * av_a
    ys, xs = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    m = np.clip(r - dist, 0, 1)[..., None]
    cv[Y0:Y1, X0:X1] = cv[Y0:Y1, X0:X1] * (1 - m) + roi * m
    ra = prog(t, ZT0 + 0.2, ZT1)
    if ra > 0:
        rg = ring_glow(ri)
        draw(cv, rg, cx, cy, opacity=ra, mode='add')
        pulse = ((t - ZT1) * 0.7) % 1.0 if t > ZT1 else 0
        if t > ZT1:
            draw(cv, ring_sprite(400, 180, 3, ORANGE2), cx, cy, scale=(r / 180) * (1 + pulse * 0.6),
                 opacity=(1 - pulse) * 0.7, mode='add')

@functools.lru_cache(maxsize=64)
def glow_bar_badge(bw, bh):
    d = rrect_alpha(bw, bh, bh / 2, 60)
    return cv2.GaussianBlur(solid(sdf_fill(d), ORANGE), (0, 0), 20) * 0.5

@functools.lru_cache(maxsize=None)
def cta_glow_btn():
    return glow_of(badge_parts()[2], 22, ORANGE, 1.0)

# ============================================================== frame assembly

SCENES = [
    (0.0, 6.92, scene_hook),
    (6.55, 8.8, scene_how),
    (8.45, 21.72, scene_steps),
    (21.5, 24.5, scene_pay),
    (24.12, 26.2, scene_wall),
    (25.9, 32.01, scene_out),
]

def cam_at(t):
    c = Cam()
    c.z = -40 * (t % 1000) / 30.0 * 0  # static base
    c.rz = wobble(t, 0.07, 0.4)
    sx, sy = shake(t, [0.9, 6.86, 8.62, 21.6, 25.98], amp=7, decay=7)
    c.x = wobble(t, 0.05, 6) + sx
    c.y = wobble(t, 0.06, 8) + sy
    return c

def bg_params(t):
    rays = prog(t, 6.6, 7.0) * (1 - prog(t, 8.4, 8.8)) + prog(t, 25.95, 26.8)
    grid = prog(t, 6.6, 7.0) * (1 - prog(t, 8.4, 8.8)) + prog(t, 26.0, 27.0)
    glow = 1.0 + 0.6 * rays
    return glow, rays, grid

def render_sub(t):
    cv = np.empty((H, W, 3), np.float32)
    glow, rays, grid = bg_params(t)
    background(cv, t, glow=glow, rays=rays, grid=grid)
    cam = cam_at(t)
    for a, b, fn in SCENES:
        if a <= t < b:
            fn(cv, t, cam)
    if t >= ZT0:
        inner = cv
        cv = np.empty((H, W, 3), np.float32)
        background(cv, t, glow=1.2, rays=0.6, grid=0.0)
        profile_ending(cv, inner, t)
    return cv

FLASHES = [(0.0, 0.9, 0.5), (6.85, 0.55, 0.3), (21.58, 0.9, 0.35), (24.2, 0.25, 0.3), (25.98, 0.5, 0.45), (29.1, 0.3, 0.35)]
CA_HITS = [2.9, 6.85, 8.6, 11.4, 14.8, 19.2, 21.58, 24.3, 25.98]

def post_params(t):
    fl = 0.0
    for t0, amp, dur in FLASHES:
        if t0 <= t <= t0 + dur:
            fl = max(fl, amp * (1 - prog(t, t0, t0 + dur)) ** 2)
    if t < 0.2:
        fl = max(fl, 0)
    ca = 0.0
    for h in CA_HITS:
        if abs(t - h) < 0.25:
            ca = max(ca, 6 * (1 - abs(t - h) / 0.25))
    fade_in = 1 - prog(t, 0.0, 0.18)
    fade = max(prog(t, 31.72, 32.0), fade_in)
    return fl, ca, fade

def render_frame(fi, nsub=NSUB):
    t = fi / FPS
    if nsub <= 1:
        acc = render_sub(t)
    else:
        acc = None
        for k in range(nsub):
            ts = t + (k / (nsub - 1) - 0.5) * SHUTTER / FPS
            ts = max(0.0, ts)
            f = render_sub(ts)
            acc = f if acc is None else acc + f
        acc /= nsub
    fl, ca, fade = post_params(t)
    out = post(acc, fi, bloom=0.55, grain=0.02, ca=ca, flash=fl, fade=fade)
    return (out * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    mode = sys.argv[1]
    os.makedirs(S + '/out', exist_ok=True)
    if mode == 'still':
        ns = int(os.environ.get('NSUB_STILL', '1'))
        for ts in sys.argv[2].split(','):
            t0 = _time.time()
            fi = int(round(float(ts) * FPS))
            img = render_frame(fi, ns)
            cv2.imwrite(f'{S}/out/still_{float(ts):05.2f}.png', img[..., ::-1])
            print('still', ts, f'{_time.time() - t0:.2f}s', flush=True)
    elif mode == 'range':
        f0, f1, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        ff = 'ffmpeg'
        p = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                              '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '12',
                              '-pix_fmt', 'yuv420p', outp], stdin=subprocess.PIPE)
        t0 = _time.time()
        for fi in range(f0, f1):
            img = render_frame(fi)
            p.stdin.write(img.tobytes())
            if (fi - f0) % 20 == 0:
                print(f'{outp}: frame {fi} ({(_time.time() - t0) / (fi - f0 + 1):.2f}s/f)', flush=True)
        p.stdin.close()
        p.wait()
        print('done', outp, flush=True)
