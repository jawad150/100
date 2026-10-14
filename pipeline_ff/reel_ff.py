"""Organic Fostering — "The Fostering Flow" (9:16, 33 s): becoming a foster carer as an app onboarding flow.

Style: bold colour-blocked "neo-brutalist" SaaS — cream cards with thick plum outlines and hard offset
shadows, extruded 3D titles, one flat brand colour per step (plum -> berry -> magenta -> orange -> peach -> cream).

Hook montage + "Start" button -> app window with 5 steps -> one scene per step (persistent stepper HUD,
progress bar, 3D clay icons) -> bento grid of support -> "Start your enquiry" CTA.
The background warms from plum night to peach as the flow progresses.

Usage:
  python3 reel_ff.py still 1.0,5.0
  python3 reel_ff.py range 0 990
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_ff')))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import numpy as np
import cv2
import reel_of as R
from reel_of import (kinetic_line, word_spr, sweep, glow_add, shadow, scrim, grade, whip, zoom_blur, shake,
                     check_spr, rrect_spr, clip_frame, PLUM, MAGENTA, ORANGE_B, GREEN, PEACH, INK, MUTEDC, WHITE_)
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30

# ------------------------------------------------------------------ brand + type
LILAC = hexc('#E7C6E0')
BLUSH = hexc('#F6EAF3')
CREAM = hexc('#FFF8F2')
ORANGE_L = hexc('#FFA24D')
GREEN_L = hexc('#8BC34A')
INKP = hexc('#2E0A2A')          # outline / hard-shadow ink (deep aubergine)
CREAM_C = hexc('#FFF4E8')
PB, PX, PK, PS, PM, PR = 'Poppins-Bold', 'Poppins-ExtraBold', 'Poppins-Black', 'Poppins-SemiBold', 'Poppins-Medium', \
    'Poppins-Regular'



def block(canvas, cx, cy, w, h, r=36, fill=None, op=1.0, sh=10, bw=4.0, outline=None):
    """Cream card with a thick outline and a hard offset shadow (no blur)."""
    if op <= 0.01 or w < 8 or h < 8:
        return
    fill = CREAM_C if fill is None else fill
    outline = INKP if outline is None else outline
    r = min(r, h / 2, w / 2)
    if sh > 0:
        draw(canvas, rrect_spr(w, h, r, INKP), cx + sh, cy + sh, opacity=op)
    draw(canvas, rrect_spr(w, h, r, fill, border=outline, bw=bw), cx, cy, opacity=op)


def glass(canvas, cx, cy, w, h, r=36, tint_c=(1, 1, 1), tint_a=0.18, blur=24, border_a=0.45, opacity=1.0,
          shadow_a=0.35, dark=False):
    """This reel swaps frosted glass for outlined blocks (same call signature as reel_of.glass)."""
    block(canvas, cx, cy, w, h, r, op=opacity, sh=10 if shadow_a > 0 else 6)


def title3d(canvas, text, cx, cy, size, t, t0, fill=None, ext=None, depth=6, fname=None, sweep_t=None, stagger=0.06,
            out_t=None):
    """Extruded 3D title: stacked offset layers in the extrusion colour, then the face with a light sweep."""
    fill = CREAM_C if fill is None else fill
    ext = INKP if ext is None else ext
    fname = fname or PK
    n = max(3, int(round(depth * size / 60)))        # 1 px layers at 45 degrees -> clean, solid extrusion
    for k in range(n, 0, -1):
        kinetic_line(canvas, text, cx + k, cy + k, size, t, t0, color=ext, fname=fname,
                     shadow_op=0.0, stagger=stagger, out_t=out_t)
    kinetic_line(canvas, text, cx, cy, size, t, t0, color=fill, fname=fname, shadow_op=0.0, stagger=stagger,
                 sweep_t=sweep_t, out_t=out_t)


# ------------------------------------------------------------------ timeline (120 BPM, everything on the 0.5 s grid)
T = dict(hook=0.0, flow=4.0, s1=6.5, s2=10.0, s3=13.5, s4=17.5, s5=21.5, sup=25.0, cta=28.0)
DUR = 33.0
NF = int(DUR * FPS)
VO = {'hook': 0.2, 'flow': 4.3, 'chat': 6.9, 'visit': 10.4, 'train': 13.9, 'assess': 17.9, 'panel': 21.8,
      'support': 25.2, 'cta': 28.3}
CHECKS = [9.0, 12.5, 16.0, 20.5, 23.0]           # each step's tick lands on a beat
CLICK_HOOK = 3.5
CLICK_CTA = 29.0
STEPS = [('Start a conversation', 'Informal chat', 'Chat'), ('Home visit', 'We visit you at home', 'Visit'),
         ('Apply & train', 'Application and training', 'Train'), ('Assessment', 'Getting to know you', 'Assess'),
         ('Panel & approval', 'The final step', 'Panel')]

SEQ = {}


def seq(name):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=24, loop=True)
    return SEQ[name]


@functools.lru_cache(maxsize=None)
def png(name):
    return load_png_sprite(f'{S}/src/{name}.png')


_fit = {}


def fitted(key, spr, height=None, width=None):
    k = (key, height, width)
    if k not in _fit:
        h, w = spr.shape[:2]
        sc = height / h if height else width / w
        _fit[k] = cv2.resize(spr, (max(1, int(w * sc)), max(1, int(h * sc))), interpolation=cv2.INTER_AREA)
    return _fit[k]


def paste(dst, src, cx, cy):
    """Premultiplied 'over' of src onto an RGBA sprite, centred at (cx, cy)."""
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = src[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    d = dst[Y0:Y1, X0:X1]
    d[:] = s + d * (1 - s[..., 3:4])


def txt(canvas, s, x, y, size, color, fname=PS, op=1.0, ax=0.5, shadow_op=0.0, scale=1.0):
    spr = word_spr(s, fname, size, color)
    if op <= 0:
        return spr
    if shadow_op > 0:
        sh = blur_sprite(tint(spr, (0.06, 0.0, 0.05)), 10)
        draw(canvas, sh, x, y + 6, scale=scale, opacity=shadow_op * op, ax=ax)
    draw(canvas, spr, x, y, scale=scale, opacity=op, ax=ax)
    return spr


def icon3d(canvas, name, t, x, y, size, t0=None, op=1.0, drop=False, shadow_on=True):
    """Clay icon from Blender that pops (or drops) in, then idles on its sway loop."""
    s = 1.0
    dy = 0.0
    if t0 is not None:
        if t < t0:
            return
        k = prog(t, t0, t0 + (0.6 if drop else 0.45))
        if drop:
            # fall + squash-and-stretch bounce
            e = 1 - (1 - k) ** 3
            dy = -(1 - e) * 820 + (math.sin(k * math.pi * 3) * 40 * (1 - k) if k > 0.55 else 0)
            s = 1.0
        else:
            s = e_out_back(k, 2.2)
        op *= min(1, k * 3)
    f = seq(name).frame(t)
    if f.shape[0] < 16:
        return
    sc = size / max(f.shape[:2]) * s
    if shadow_on:
        sh = tint(f, INKP[:3])
        draw(canvas, sh, x + 12, y + dy + 14, scale=sc, opacity=0.35 * op)
    draw(canvas, f, x, y + dy, scale=sc, opacity=op)


# ------------------------------------------------------------------ background: plum night -> warm peach
_Y, _X = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
RAMP = [(0.00, '#3B0D36', '#2A0926'), (0.12, '#5B174F', '#46113D'), (0.28, '#8A1C64', '#701450'),
        (0.42, '#B7006E', '#98005B'), (0.56, '#F2622E', '#DE4F22'), (0.68, '#FF7A3D', '#F0602A'),
        (0.97, '#FFD4BA', '#FFC1A0'), (1.00, '#FFF1E6', '#FFE2CC')]


def ramp(w):
    for (a, ta, ba), (b, tb, bb) in zip(RAMP, RAMP[1:]):
        if w <= b:
            k = (w - a) / (b - a)
            return [np.array(hexc(p)[:3]) * (1 - k) + np.array(hexc(q)[:3]) * k for p, q in ((ta, tb), (ba, bb))]
    return [np.array(hexc(RAMP[-1][1])[:3]), np.array(hexc(RAMP[-1][2])[:3])]


def _blob(cx, cy, r):
    d = np.sqrt((_X - cx / 4) ** 2 + (_Y - cy / 4) ** 2) / (r / 4)
    return np.exp(-d * d)[..., None]


_grid = None


def dot_grid():
    global _grid
    if _grid is None:
        g = np.zeros((H, W), np.float32)
        for y in range(30, H, 60):
            for x in range(30, W, 60):
                cv2.circle(g, (x, y), 2, 1.0, -1, cv2.LINE_AA)
        _grid = g[..., None]
    return _grid


def warmth(t):
    keys = [(0, 0.0), (T['flow'], 0.0), (T['s1'], 0.12), (T['s2'], 0.28), (T['s3'], 0.42), (T['s4'], 0.56),
            (T['s5'] - 0.01, 0.68), (T['s5'], 0.97), (T['sup'], 1.0), (40, 1.0)]
    for (a, wa), (b, wb) in zip(keys, keys[1:]):
        if t <= b:
            return wa + (wb - wa) * prog(t, a, b)
    return 1.0


def bg(t, w=None):
    """Flat brand colour with big outlined geometric shapes drifting in parallax + a dot grid."""
    w = warmth(t) if w is None else w
    top, bot = ramp(w)
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    c = np.repeat((top * (1 - ys) + bot * ys).astype(np.float32), W, axis=1)
    light = clamp((w - 0.75) / 0.25)
    tone = np.array((1, 1, 1) if light < 0.5 else PLUM[:3], np.float32)
    shapes = np.zeros((H, W), np.float32)
    rings = np.zeros((H, W), np.float32)
    cx1, cy1 = int(900 + 40 * math.sin(t * 0.4)), int(380 + 30 * math.cos(t * 0.35))
    cv2.circle(shapes, (cx1, cy1), 330, 1.0, -1, cv2.LINE_AA)
    cx2, cy2 = int(120 + 30 * math.cos(t * 0.3)), int(1640 + 40 * math.sin(t * 0.33))
    cv2.circle(shapes, (cx2, cy2), 260, 1.0, -1, cv2.LINE_AA)
    cv2.circle(rings, (cx1 - 60, cy1 + 90), 420, 1.0, 4, cv2.LINE_AA)
    cv2.circle(rings, (cx2 + 50, cy2 - 60), 340, 1.0, 4, cv2.LINE_AA)
    # squiggle
    xs = np.arange(0, W + 40, 8)
    pts = np.stack([xs, 1180 + 26 * np.sin(xs / 60.0 + t * 1.2) + 60 * math.sin(t * 0.3)], 1).astype(np.int32)
    cv2.polylines(rings, [pts], False, 1.0, 5, cv2.LINE_AA)
    c += (shapes[..., None] * (0.07 if light < 0.5 else 0.05)) * (tone - c)
    c += (rings[..., None] * (0.12 if light < 0.5 else 0.10)) * (tone - c)
    c += (dot_grid() * (0.07 if light < 0.5 else 0.08)) * (tone - c)
    return c


def dark_ui(t):
    return warmth(t) < 0.8


# ------------------------------------------------------------------ UI widgets
def card(canvas, cx, cy, w, h, t, t0, r=40, light=True, dur=0.45, rise=60, op=1.0):
    """White glass card that pops in with an ease-out-back; returns (k, dy) for its content."""
    if t < t0:
        return 0.0, 0.0
    k = prog(t, t0, t0 + dur)
    s = 0.86 + 0.14 * e_out_back(k, 1.8)
    dy = rise * (1 - e_out_cubic(k))
    glass(canvas, cx, cy + dy, w * s, h * s, r=r, tint_c=(1, 1, 1), tint_a=0.88 if light else 0.14,
          opacity=min(1, k * 3) * op, blur=26, shadow_a=0.38, border_a=0.6)
    return min(1, k * 2.2) * op, dy


def pill_spr(text, fname=PB, size=26, fill=MAGENTA, color=WHITE_, pad_x=24, pad_y=12, border=None, dot=None):
    return pill(text, fname, size, pad_x=pad_x, pad_y=pad_y, fill=fill, border=border, text_color=color, tracking=0.04,
                dot=dot)


@functools.lru_cache(maxsize=64)
def node_spr(state, n, size=58):
    """Stepper node: 'done' green tick, 'active' magenta numbered, 'todo' outline."""
    if state == 'done':
        return check_spr(size, GREEN)
    s = size * 3
    im = np.zeros((s, s), np.uint8)
    if state == 'active':
        cv2.circle(im, (s // 2, s // 2), s // 2 - 2, 255, -1, cv2.LINE_AA)
        disc = solid(im.astype(np.float32) / 255, MAGENTA)
        col = WHITE_
    else:
        cv2.circle(im, (s // 2, s // 2), s // 2 - 8, 255, 5, cv2.LINE_AA)
        disc = solid(im.astype(np.float32) / 255, (1, 1, 1, 0.55))
        col = (1, 1, 1, 0.75)
    disc = cv2.resize(disc, (size, size), interpolation=cv2.INTER_AREA)
    num = text_sprite(str(n), PB, int(size * 0.46), col)
    out = disc.copy()
    paste(out, num, size / 2, size / 2 + 1)
    return out


def progress_pct(t):
    return sum(20 * e_out_cubic(prog(t, c, c + 0.45)) for c in CHECKS)


def hud(canvas, t, op=1.0, dy=0.0):
    """Persistent stepper: title, % counter, gradient progress bar with five nodes."""
    if op <= 0.01:
        return
    light = True
    ink = PLUM
    cy = 215 + dy
    glass(canvas, W / 2, cy, 980, 250, r=44, tint_c=(1, 1, 1), tint_a=0.8 if light else 0.12, opacity=op, blur=26,
          shadow_a=0.3, border_a=0.5)
    txt(canvas, 'Your fostering journey', 100, cy - 70, 32, ink, PS, op, ax=0.0)
    p = progress_pct(t)
    txt(canvas, f'{int(round(p))}%', 980, cy - 70, 42, ORANGE_B if light else ORANGE_L, PX, op, ax=1.0)
    x0, x1, by = 110, 970, cy + 4
    L = x1 - x0
    track = rrect_spr(L, 14, 7, (PLUM[0], PLUM[1], PLUM[2], 0.14) if light else (1, 1, 1, 0.16))
    draw(canvas, track, W / 2, by, opacity=op)
    fw = L * p / 100
    if fw > 6:
        fill = rrect_spr(fw, 14, 7, None, grad=(ORANGE_B, hexc('#FFC15E')))
        draw(canvas, fill, x0 + fw / 2, by, opacity=op)
        glow_add(canvas, fill, x0 + fw / 2, by, ORANGE_B, sigma=10, strength=0.6 * op)
    for i in range(5):
        nx = x0 + L * (i + 0.5) / 5
        c = CHECKS[i]
        kd = prog(t, c, c + 0.35)
        active = (i == 0 or t >= CHECKS[i - 1]) and t < c
        state = 'done' if kd > 0 else ('active' if active else 'todo')
        if state == 'todo' and light:
            state = 'active_l'
        if state == 'active_l':
            spr = node_spr('todo', i + 1)
            spr = tint(spr, PLUM[:3], 1.0)
        else:
            spr = node_spr(state, i + 1)
        s = e_out_back(kd, 3.0) if state == 'done' else 1.0
        if active:
            pr = (t * 1.6) % 1.0
            ring = ring_sprite(120, 30 + 26 * pr, 3, MAGENTA, glow=6)
            draw(canvas, ring, nx, by, opacity=op * (1 - pr) * 0.9)
        if state == 'done' and kd < 1:
            draw(canvas, ring_sprite(140, 30 + 40 * kd, 4, GREEN, glow=8), nx, by, opacity=op * (1 - kd))
        draw(canvas, spr, nx, by, scale=max(0.01, s), opacity=op)
        lab_col = ink if (state == 'done' or active) else ((PLUM[0], PLUM[1], PLUM[2], 0.55) if light else (1, 1, 1, 0.55))
        txt(canvas, STEPS[i][2], nx, by + 62, 22, lab_col, PM, op)


def step_header(canvas, t, t0, i, light):
    """'STEP n OF 5' pill (turns green 'COMPLETE' on the tick) + kinetic step title."""
    c = CHECKS[i]
    k = prog(t, t0 + 0.05, t0 + 0.4)
    if k > 0:
        if t < c:
            p = pill_spr(f'STEP {i + 1} OF 5', PB, 24, fill=MAGENTA, dot=(1, 1, 1, 1))
            s = 1.0
        else:
            p = pill_spr(f'STEP {i + 1} COMPLETE', PB, 24, fill=GREEN, dot=(1, 1, 1, 1))
            s = e_out_back(prog(t, c, c + 0.35), 3.0)
        draw(canvas, p, W / 2, 420 + 20 * (1 - e_out_cubic(k)), scale=s, opacity=min(1, k * 2))
    if light:
        title3d(canvas, STEPS[i][0], W / 2, 520, 82, t, t0 + 0.12, fill=PLUM, ext=ORANGE_B, fname=PK, sweep_t=t0 + 0.9)
    else:
        title3d(canvas, STEPS[i][0], W / 2, 520, 82, t, t0 + 0.12, fill=CREAM_C, ext=INKP, fname=PK, sweep_t=t0 + 0.9)


def bubble(canvas, cx, cy, lines, t, t0, side='right', fill=MAGENTA, ink=WHITE_, size=38, label=None, avatar=False):
    if t < t0:
        return
    k = prog(t, t0, t0 + 0.4)
    s = e_out_back(k, 2.2)
    sprs = [word_spr(l, PS, size, ink) for l in lines]
    w = max(sp.shape[1] for sp in sprs) + 70
    h = len(lines) * size * 1.42 + 54
    x = cx - w / 2 if side == 'right' else cx + w / 2
    body = rrect_spr(w, h, 40, fill) if fill is not None else None
    ox = (1 - e_out_cubic(k)) * (60 if side == 'right' else -60)
    bx = x + ox
    if body is not None:
        block(canvas, bx, cy, w * s, h * s, 40 * s, fill=fill, op=min(1, k * 3))
    else:
        glass(canvas, bx, cy, w * s, h * s, r=40 * s, tint_c=(1, 1, 1), tint_a=0.92, opacity=min(1, k * 3), blur=20,
              shadow_a=0.35)
    for j, sp in enumerate(sprs):
        yy = cy + (j - (len(lines) - 1) / 2) * size * 1.42
        draw(canvas, sp, bx - w / 2 * s + 36 * s + sp.shape[1] / 2 * s, yy * 1.0, scale=s, opacity=min(1, k * 2.5))
    if label:
        lab_x = bx + w / 2 - 10 if side == 'right' else bx - w / 2 + 10
        txt(canvas, label, lab_x, cy - h / 2 - 30, 26, CREAM_C, PB, min(1, k * 2), ax=1.0 if side == 'right' else 0.0)
    if avatar:
        av = rrect_spr(92, 92, 46, (1, 1, 1, 1))
        em = fitted('emblem', png('emblem'), height=58)
        a = av.copy()
        paste(a, em, 46, 46)
        draw(canvas, a, bx - w / 2 * s - 66, cy + h / 2 * s - 46, scale=s, opacity=min(1, k * 3))


def typing(canvas, cx, cy, t, t0, t1):
    if not (t0 <= t < t1):
        return
    k = prog(t, t0, t0 + 0.3)
    glass(canvas, cx, cy, 170 * e_out_back(k), 84, r=42, tint_c=(1, 1, 1), tint_a=0.9, opacity=min(1, k * 3), blur=18)
    for i in range(3):
        ph = (t * 3.2 - i * 0.28) % 1.0
        yy = cy - 9 * max(0, math.sin(ph * math.pi))
        dot = solid(sdf_fill(rrect_alpha(18, 18, 9, 2)), MUTEDC)
        draw(canvas, dot, cx - 34 + i * 34, yy, opacity=0.5 + 0.5 * math.sin(ph * math.pi))


def ripple(canvas, x, y, t, t0, color=MAGENTA, n=3, rmax=260):
    for j in range(n):
        k = prog(t, t0 + j * 0.09, t0 + j * 0.09 + 0.7)
        if 0 < k < 1:
            e = e_out_cubic(k)
            r = 20 + rmax * e
            rs = ring_sprite(int(2 * r + 60), r, 5 - 2 * k, color, glow=10)
            draw(canvas, rs, x, y, opacity=(1 - k) * 0.9)


def cursor(canvas, t, p0, p1, t0, t1, click_t, size=120, op=1.0):
    if t < t0:
        return None
    k = e_inout_cubic(prog(t, t0, t1))
    x = lerp(p0[0], p1[0], k) + 40 * math.sin(k * math.pi)
    y = lerp(p0[1], p1[1], k) - 60 * math.sin(k * math.pi)
    press = 1 - 0.18 * math.sin(math.pi * prog(t, click_t - 0.06, click_t + 0.14))
    f = seq('cursor').frame(t)
    if f.shape[0] < 16:
        return x, y
    sc = size / max(f.shape[:2]) * press
    sh = blur_sprite(tint(f, (0.05, 0, 0.05)), 8)
    # the cursor tip sits at the sprite's top-left; anchor there
    draw(canvas, sh, x + 10, y + 14, scale=sc, opacity=0.5 * op * min(1, k * 4 + 0.2), ax=0.08, ay=0.04)
    draw(canvas, f, x, y, scale=sc, opacity=op * min(1, prog(t, t0, t0 + 0.2) * 1.0), ax=0.08, ay=0.04)
    return x, y


def button(canvas, cx, cy, w, h, label, t, press=0.0, op=1.0, glow_c=MAGENTA, fill=None, ink=None, size=46,
           rx=0.0, ry=0.0):
    """Chunky outlined button with a hard shadow; on click it pushes down into its shadow."""
    sh = 14 * (1 - press)
    fill = CREAM_C if fill is None else fill
    ink = PLUM if ink is None else ink
    bob = 6 * math.sin(t * 2.4) * (1 - press)
    k = 0.5 + 0.5 * math.sin(t * 4.0)
    halo = rrect_spr(w + 40, h + 40, (h + 40) / 2, (glow_c[0], glow_c[1], glow_c[2], 0.22 * k))
    draw(canvas, halo, cx + 7, cy + 7 + bob, opacity=op)
    ox = 14 - sh
    draw(canvas, rrect_spr(w, h, h / 2, INKP), cx + 14, cy + 14 + bob, opacity=op)
    draw(canvas, rrect_spr(w, h, h / 2, fill, border=INKP, bw=5), cx + ox, cy + ox + bob, opacity=op)
    lab = word_spr(label, PX, size, ink)
    draw(canvas, lab, cx + ox, cy + ox + bob + 2, opacity=op)


# ------------------------------------------------------------------ scenes
HOOK_CUTS = [(1, 1.0), (3, 1.6), (4, 1.2), (5, 0.8), (6, 1.8), (7, 1.0)]
HOOK_MONTAGE = 1.5


def sc_hook(t):
    if t < HOOK_MONTAGE:
        i = min(int(t / 0.25), len(HOOK_CUTS) - 1)
        ci, off = HOOK_CUTS[i]
        lt = t - i * 0.25
        z = 1.18 - 0.12 * e_out_cubic(lt / 0.25)
        c = grade(clip_frame(ci, off + lt * 1.4, zoom=z, rot=(-1.5 if i % 2 else 1.5) * (1 - lt / 0.25)), warm=0.6)
        c *= 0.82
        scrim(c, top=0.55, bottom=0.55, top_h=0.6, bot_h=0.5)
        title3d(c, 'Thinking about', W / 2, 860, 96, t, 0.12, fill=CREAM_C, ext=MAGENTA, stagger=0.05)
        title3d(c, 'fostering?', W / 2, 1000, 138, t, 0.3, fill=CREAM_C, ext=ORANGE_B, sweep_t=0.8)
        # quick white flash frame on every cut
        if lt < 0.04:
            c += 0.25 * (1 - lt / 0.04)
        return c
    c = bg(t, 0.0)
    lt = t - HOOK_MONTAGE
    # floating bokeh particles
    rng = np.random.default_rng(3)
    for j in range(16):
        px = rng.uniform(0, W)
        py = (rng.uniform(0, H) - t * rng.uniform(20, 60)) % H
        sz = rng.uniform(20, 70)
        dot = rrect_spr(sz * 0.5, sz * 0.5, sz * 0.25, MAGENTA if j % 3 else ORANGE_B, border=INKP, bw=2)
        draw(c, dot, px, py, opacity=0.6)
    title3d(c, "Here's the whole journey", W / 2, 560, 70, t, HOOK_MONTAGE + 0.15, fill=CREAM_C, ext=INKP)
    title3d(c, 'in 30 seconds.', W / 2, 660, 84, t, HOOK_MONTAGE + 0.6, fill=ORANGE_L, ext=INKP,
            sweep_t=HOOK_MONTAGE + 1.2)
    kb = prog(t, HOOK_MONTAGE + 0.1, HOOK_MONTAGE + 0.7)
    press = math.sin(math.pi * prog(t, CLICK_HOOK - 0.06, CLICK_HOOK + 0.2))
    if kb > 0:
        by = 1000 + 14 * math.sin(t * 2.2) + 120 * (1 - e_out_cubic(kb))
        button(c, W / 2, by, 820, 150, 'Start your fostering journey', t, press=press, op=min(1, kb * 2),
               rx=8 * math.sin(t * 1.3), ry=10 * math.cos(t * 1.1), size=44)
        ripple(c, 700, 1010, t, CLICK_HOOK, MAGENTA, n=3, rmax=420)
    cursor(c, t, (980, 1750), (700, 1010), HOOK_MONTAGE + 0.7, CLICK_HOOK - 0.05, CLICK_HOOK)
    if t > CLICK_HOOK:
        c += np.array(MAGENTA[:3], np.float32) * 0.35 * math.exp(-(t - CLICK_HOOK) * 6)
    return c


def sc_flow(t):
    t0 = T['flow']
    lt = t - t0
    c = bg(t)
    title3d(c, '5 steps.', W / 2, 250, 130, t, t0 + 0.1, fill=CREAM_C, ext=MAGENTA, depth=7, sweep_t=t0 + 0.8)
    kinetic_line(c, "We're with you on every one.", W / 2, 385, 50, t, t0 + 0.55, color=hexc('#FFD9C2'), fname=PB,
                 shadow_op=0.0, stagger=0.05)
    k = prog(t, t0, t0 + 0.5)
    wy = 1150 + 260 * (1 - e_out_cubic(k))
    # app window
    glass(c, W / 2, wy, 940, 1230, r=48, tint_c=(1, 1, 1), tint_a=0.10, opacity=min(1, k * 2), blur=28, shadow_a=0.5,
          border_a=0.55, dark=True)
    if k > 0:
        for j, col in enumerate((MAGENTA, ORANGE_B, GREEN)):
            draw(c, check_dot(col), 130 + j * 34, wy - 570, opacity=min(1, k * 2))
        txt(c, 'Your fostering journey', W / 2, wy - 570, 28, PLUM, PB, min(1, k * 2))
    for i in range(5):
        ki = prog(t, t0 + 0.45 + i * 0.12, t0 + 0.85 + i * 0.12)
        if ki <= 0:
            continue
        ry = wy - 400 + i * 175
        rx = 1 - e_out_cubic(ki)
        op = min(1, ki * 2.5)
        block(c, W / 2 + 80 * rx, ry, 840, 140, r=30, fill=[BLUSH, PEACH, hexc('#FFE3C2'), hexc('#E3F1CF'), LILAC][i],
              op=op, sh=6, bw=3)
        draw(c, tint(node_spr('todo', i + 1, 70), PLUM[:3], 1.0), 190 + 80 * rx, ry, opacity=op)
        txt(c, STEPS[i][0], 260 + 80 * rx, ry - 20, 40, PLUM, PX, op, ax=0.0)
        txt(c, STEPS[i][1], 260 + 80 * rx, ry + 30, 26, MUTEDC, PS, op, ax=0.0)
        icon3d(c, ['chat', 'house', 'doc', 'person', 'badge'][i], t + i * 0.3, 870 + 80 * rx, ry, 110,
               t0 + 0.55 + i * 0.12, op=op, shadow_on=False)
    kb = prog(t, t0 + 1.2, t0 + 1.6)
    if kb > 0:
        txt(c, '0%', 140, wy + 500, 34, ORANGE_B, PX, kb, ax=0.0)
        draw(c, rrect_spr(660, 16, 8, (PLUM[0], PLUM[1], PLUM[2], 0.14)), 600, wy + 502, opacity=kb)
    # push into step 1 as the flow hands over
    kz = e_in_cubic(prog(t, T['s1'] - 0.45, T['s1']))
    if kz > 0:
        z = 1 + 0.9 * kz
        fy = wy - 400
        M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, fy - z * fy + (H * 0.5 - fy) * kz * 0.6]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return c


@functools.lru_cache(maxsize=8)
def check_dot(col):
    s = 60
    im = np.zeros((s, s), np.uint8)
    cv2.circle(im, (s // 2, s // 2), s // 2 - 2, 255, -1, cv2.LINE_AA)
    return cv2.resize(solid(im.astype(np.float32) / 255, col), (20, 20), interpolation=cv2.INTER_AREA)


def push(c, t, t0, amt=0.035, cy=H * 0.55):
    """Slow continuous camera push on the content layer."""
    z = 1 + amt * e_inout_cubic(prog(t, t0, t0 + 3.6))
    M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, cy - z * cy]])
    return cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def done_tick(canvas, t, c, x, y, size=64):
    k = prog(t, c, c + 0.35)
    if k > 0:
        draw(canvas, check_spr(size, GREEN), x, y, scale=e_out_back(k, 3.0))
        if k < 1:
            draw(canvas, ring_sprite(int(size * 2.4), size * 0.5 + 40 * k, 4, GREEN, glow=8), x, y, opacity=1 - k)


def sc_s1(t):
    t0 = T['s1']
    c = bg(t)
    step_header(c, t, t0, 0, False)
    icon3d(c, 'chat', t, W / 2, 820, 320, t0 + 0.2)
    bubble(c, 980, 1130, ["Hi, I'd like to know more", 'about fostering.'], t, t0 + 0.55, side='right', fill=MAGENTA,
           label='You')
    typing(c, 300, 1390, t, t0 + 1.15, t0 + 1.75)
    if t >= t0 + 1.75:
        bubble(c, 215, 1400, ["Let's talk.", 'No commitment.'], t, t0 + 1.75, side='left', fill=None, ink=PLUM,
               size=44, label='Organic Fostering', avatar=False)
        # replies come with the OF emblem as avatar
        k = prog(t, t0 + 1.75, t0 + 2.1)
        av = rrect_spr(104, 104, 52, (1, 1, 1, 1))
        a = av.copy()
        paste(a, fitted('emblem', png('emblem'), height=64), 52, 52)
        draw(c, a, 140, 1555, scale=e_out_back(k, 2.0), opacity=min(1, k * 3))
    done_tick(c, t, CHECKS[0], 880, 1400)
    c = push(c, t, t0)
    hud(c, t, op=min(1, prog(t, t0 - 0.1, t0 + 0.3) * 2), dy=-80 * (1 - e_out_cubic(prog(t, t0, t0 + 0.4))))
    return c


@functools.lru_cache(maxsize=1)
def map_spr(w=900, h=440):
    """Stylised map card: blush land, white streets, a river and parks."""
    spr = rrect_spr(w, h, 36, BLUSH)
    a = spr[..., 3:4].copy()
    h, w = a.shape[:2]
    rgb = np.ones((h, w, 3), np.float32) * np.array(hexc('#EDD3E6')[:3], np.float32)
    rng = np.random.default_rng(5)
    for _ in range(8):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(40, 90)
        cv2.circle(rgb, (int(cx), int(cy)), int(r), tuple(float(v) for v in hexc('#C5E3A6')[:3]), -1, cv2.LINE_AA)
    pts = np.array([[0, h * 0.7], [w * 0.25, h * 0.55], [w * 0.5, h * 0.75], [w * 0.75, h * 0.5], [w, h * 0.62]], np.int32)
    cv2.polylines(rgb, [pts], False, tuple(float(v) for v in hexc('#E7A9CB')[:3]), 34, cv2.LINE_AA)
    wc = (1.0, 1.0, 1.0)
    for x in range(-200, w + 200, 120):
        cv2.line(rgb, (x, 0), (x + 160, h), wc, 9, cv2.LINE_AA)
    for y in range(40, h, 95):
        cv2.line(rgb, (0, y), (w, y - 50), wc, 9, cv2.LINE_AA)
    cv2.line(rgb, (0, int(h * 0.3)), (w, int(h * 0.42)), wc, 18, cv2.LINE_AA)
    return np.concatenate([rgb * a, a], 2).astype(np.float32)


@functools.lru_cache(maxsize=2)
def cal_card(booked):
    w, h = 400, 300
    spr = rrect_spr(w, h, 34, CREAM_C, border=INKP, bw=4)
    top = rrect_spr(w - 8, 92, 30, MAGENTA)
    paste(spr, top[:, :], w / 2, 46)
    paste(spr, rrect_spr(w - 8, 40, 0, MAGENTA), w / 2, 74)
    paste(spr, rrect_spr(w - 8, 4, 0, INKP), w / 2, 94)
    paste(spr, text_sprite('HOME VISIT', PB, 30, WHITE_, 0.08), w / 2, 50)
    if booked:
        paste(spr, text_sprite('Booked', PX, 56, PLUM), w / 2, 160)
        paste(spr, pill('Confirmed', PB, 24, pad_x=20, pad_y=10, fill=GREEN, border=None, text_color=WHITE_,
                        dot=(1, 1, 1, 1)), w / 2, 238)
    else:
        paste(spr, text_sprite('Pick a time', PS, 40, MUTEDC), w / 2, 170)
    return spr


def sc_s2(t):
    t0 = T['s2']
    c = bg(t)
    step_header(c, t, t0, 1, False)
    # house drops in on the beat
    icon3d(c, 'house', t, 300, 830, 360, t0 + 0.0, drop=True)
    # calendar card flips to "booked"
    kc = prog(t, t0 + 0.4, t0 + 0.8)
    if kc > 0:
        kf = prog(t, t0 + 1.0, t0 + 1.4)
        booked = kf >= 0.5
        ang = (1 - e_out_cubic(kc)) * -80 + (kf * 180 if kf < 0.5 else (kf - 1) * 180)
        spr = cal_card(booked)
        draw3d(c, tint(spr, INKP[:3]), 782, 852, 0, spr.shape[1], None, rx=ang, opacity=min(1, kc * 2))
        draw3d(c, spr, 770, 840, 0, spr.shape[1], None, rx=ang, opacity=min(1, kc * 2))
        icon3d(c, 'calendar', t, 900, 690, 130, t0 + 0.6)
    # map + pin on Manchester
    km = prog(t, t0 + 0.9, t0 + 1.3)
    if km > 0:
        m = map_spr()
        my = 1380 + 60 * (1 - e_out_cubic(km))
        sc_ = 0.94 + 0.06 * e_out_back(km)
        draw(c, rrect_spr(m.shape[1], m.shape[0], 36, INKP), W / 2 + 12, my + 12, scale=sc_, opacity=min(1, km * 2))
        draw(c, m, W / 2, my, scale=sc_, opacity=min(1, km * 2))
        draw(c, solid(sdf_stroke(rrect_alpha(m.shape[1] - 4, m.shape[0] - 4, 36, 2), 4.0), INKP), W / 2, my,
             scale=sc_, opacity=min(1, km * 2))
        land = t0 + 1.55 + 0.6
        ripple(c, W / 2, my + 70, t, land - 0.05, MAGENTA, n=2, rmax=160)
        icon3d(c, 'pin', t, W / 2, my - 40, 230, t0 + 1.55, drop=True)
        kl = prog(t, land, land + 0.35)
        if kl > 0:
            p = pill('Manchester', PB, 30, pad_x=26, pad_y=12, fill=PLUM, border=None, text_color=WHITE_, dot=ORANGE_B)
            draw(c, p, W / 2, my + 150, scale=e_out_back(kl, 2.5), opacity=min(1, kl * 3))
    done_tick(c, t, CHECKS[1], 950, 1000)
    c = push(c, t, t0)
    hud(c, t)
    return c


def sc_s3(t):
    t0 = T['s3']
    c = bg(t)
    step_header(c, t, t0, 2, False)
    # application form fills itself in, line by line
    k, dy = card(c, W / 2, 900, 920, 470, t, t0 + 0.15)
    if k > 0:
        icon3d(c, 'doc', t, 170, 760 + dy, 150, t0 + 0.3, shadow_on=False)
        txt(c, 'Application', 270, 745 + dy, 46, PLUM, PX, k, ax=0.0)
        txt(c, 'Tell us about you', 270, 795 + dy, 26, MUTEDC, PM, k, ax=0.0)
        for j, (lab, val) in enumerate([('About you', 'Ready to make a difference'), ('Your home', 'A spare bedroom'),
                                        ('Your family', 'Partner and two children')]):
            yy = 880 + j * 82 + dy
            txt(c, lab, 120, yy, 28, MUTEDC, PS, k, ax=0.0)
            box = rrect_spr(560, 60, 16, BLUSH)
            draw(c, box, 650, yy, opacity=k)
            tf = t0 + 0.6 + j * 0.42
            n = int(max(0, t - tf) * 40)
            if n > 0:
                txt(c, val[:n], 390, yy, 29, PLUM, PS, k, ax=0.0)
            if t > tf + len(val) / 40 + 0.05:
                kk = prog(t, tf + len(val) / 40 + 0.05, tf + len(val) / 40 + 0.35)
                draw(c, check_spr(40, GREEN), 905, yy, scale=e_out_back(kk, 3.0))
    # training modules stack up and tick off
    icon3d(c, 'cap', t, 175, 1420, 230, t0 + 1.5)
    for j, (lab, sub) in enumerate([('Preparation training', 'Before you foster'),
                                    ('Ongoing learning', 'Throughout your journey')]):
        tt = t0 + 1.6 + j * 0.35
        kk = prog(t, tt, tt + 0.4)
        if kk <= 0:
            continue
        x = 640 + 400 * (1 - e_out_expo(kk))
        y = 1350 + j * 150
        glass(c, x, y, 680, 128, r=30, tint_c=(1, 1, 1), tint_a=0.9, opacity=min(1, kk * 3), blur=18, shadow_a=0.35)
        txt(c, lab, x - 300, y - 18, 34, PLUM, PB, min(1, kk * 2), ax=0.0)
        txt(c, sub, x - 300, y + 26, 24, MUTEDC, PM, min(1, kk * 2), ax=0.0)
        tc = tt + 0.6
        kt = prog(t, tc, tc + 0.3)
        if kt > 0:
            draw(c, check_spr(52, GREEN), x + 270, y, scale=e_out_back(kt, 3.0))
    c = push(c, t, t0)
    hud(c, t)
    return c


TAGS = [('Your home', ORANGE_B), ('Your household', MAGENTA), ('Your strengths', GREEN), ('Your story', PLUM)]


def sc_s4(t):
    t0 = T['s4']
    c = bg(t)
    step_header(c, t, t0, 3, False)
    k, dy = card(c, W / 2, 1130, 920, 900, t, t0 + 0.15, rise=90)
    if k > 0:
        ka = prog(t, t0 + 0.35, t0 + 0.75)
        circ = rrect_spr(300, 300, 150, PEACH, border=INKP, bw=4)
        draw(c, circ, W / 2, 860 + dy, scale=e_out_back(ka, 2.0), opacity=min(1, ka * 3))
        icon3d(c, 'person', t, W / 2, 870 + dy, 250, t0 + 0.45, shadow_on=False)
        kinetic_line(c, 'Your profile', W / 2, 1080 + dy, 56, t, t0 + 0.6, color=PLUM, fname=PX, shadow_op=0.0)
        kinetic_line(c, 'Getting to know you', W / 2, 1145 + dy, 32, t, t0 + 0.8, color=MUTEDC, fname=PM,
                     shadow_op=0.0, stagger=0.04)
        # line that draws across
        kl = prog(t, t0 + 0.9, t0 + 1.3)
        if kl > 0:
            ln = rrect_spr(max(4, 700 * e_out_cubic(kl)), 4, 2, LILAC)
            draw(c, ln, W / 2, 1200 + dy)
        for j, (lab, col) in enumerate(TAGS):
            tt = VO['assess'] + 0.35 + j * 0.42
            kk = prog(t, tt, tt + 0.35)
            if kk <= 0:
                continue
            p = pill(lab, PB, 34, pad_x=30, pad_y=18, fill=(col[0], col[1], col[2], 0.12), border=col,
                     text_color=col if col != PLUM else PLUM, dot=col)
            x = W / 2 + (-215 if j % 2 == 0 else 215)
            y = 1300 + (j // 2) * 120 + dy
            draw(c, p, x, y, scale=e_out_back(kk, 2.6), opacity=min(1, kk * 3))
    c = push(c, t, t0)
    hud(c, t)
    return c


LEAVES = None


def leaf_burst(canvas, t, t0, x, y, n=18):
    global LEAVES
    if LEAVES is None:
        rng = np.random.default_rng(11)
        LEAVES = [(rng.uniform(0, 2 * math.pi), rng.uniform(380, 820), rng.uniform(70, 150),
                   ['leaf_green', 'leaf_green', 'leaf_magenta', 'leaf_orange'][i % 4], rng.uniform(0, 3))
                  for i in range(n)]
    lt = t - t0
    if lt < 0 or lt > 2.2:
        return
    for a, sp, sz, name, ph in LEAVES:
        e = 1 - math.exp(-lt * 3.2)
        px = x + math.cos(a) * sp * e
        py = y + math.sin(a) * sp * e * 0.5 + 160 * lt * lt * 0.5
        op = min(1, lt * 8) * (1 - prog(lt, 1.3, 2.2))
        R.leaf(canvas, name, t + ph, px, py, sz * (0.6 + 0.4 * e), op=op, blur=1.5 * (1 - e))


def sc_s5(t):
    t0 = T['s5']
    c = bg(t)
    step_header(c, t, t0, 4, True)
    cx, cy = W / 2, 980
    ring_r = 250
    done = CHECKS[4]
    kr = prog(t, t0 + 0.1, t0 + 0.5)
    if kr > 0:
        block(c, cx, cy, 2 * ring_r + 150, 2 * ring_r + 150, r=ring_r + 75, op=min(1, kr * 2), sh=14)
        # track + arc
        s = 2 * ring_r + 80
        tr = np.zeros((s, s), np.float32)
        cv2.circle(tr, (s // 2, s // 2), ring_r, 1.0, 34, cv2.LINE_AA)
        draw(c, solid(tr, (PLUM[0], PLUM[1], PLUM[2], 0.10)), cx, cy, opacity=kr)
        p = 80 + 20 * e_inout_cubic(prog(t, t0 + 0.4, done))
        arc = np.zeros((s, s), np.float32)
        cv2.ellipse(arc, (s // 2, s // 2), (ring_r, ring_r), -90, 0, 360 * p / 100, 1.0, 34, cv2.LINE_AA)
        ys, xs = np.mgrid[0:s, 0:s].astype(np.float32)
        ang = (np.arctan2(xs - s / 2, -(ys - s / 2)) / (2 * math.pi)) % 1.0
        col = np.array(MAGENTA[:3], np.float32) * (1 - ang[..., None]) + np.array(ORANGE_B[:3], np.float32) * ang[..., None]
        arc_spr = np.concatenate([col * arc[..., None], arc[..., None]], 2).astype(np.float32)
        if t >= done:
            arc_spr = np.concatenate([np.array(GREEN[:3], np.float32) * arc[..., None] * 1.0, arc[..., None]], 2).astype(np.float32) \
                * min(1, prog(t, done, done + 0.25)) + arc_spr * (1 - min(1, prog(t, done, done + 0.25)))
        glow_add(c, arc_spr, cx, cy, ORANGE_B if t < done else GREEN, sigma=14, strength=0.7 * kr)
        draw(c, arc_spr, cx, cy, opacity=kr)
        kd = prog(t, done, done + 0.3)
        if kd < 1:
            txt(c, f'{int(round(p))}%', cx, cy, 130, PLUM, PK, kr * (1 - kd), scale=1 + 0.3 * kd)
        if kd > 0:
            em = fitted('emblem', png('emblem'), width=360)
            draw(c, em, cx, cy, scale=e_out_back(kd, 2.4), opacity=min(1, kd * 3))
            draw(c, ring_sprite(900, ring_r + 120 * kd, 6, GREEN, glow=14), cx, cy, opacity=1 - kd)
        leaf_burst(c, t, done, cx, cy)
    # toast
    tt = done + 0.25
    kt = prog(t, tt, tt + 0.45)
    if kt > 0:
        y = 1450 + 200 * (1 - e_out_back(kt, 1.6))
        glass(c, W / 2, y, 900, 170, r=40, tint_c=(1, 1, 1), tint_a=0.94, opacity=min(1, kt * 3), blur=20,
              shadow_a=0.45, border_a=0.8)
        icon3d(c, 'badge', t, 175, y, 140, tt + 0.1, shadow_on=False)
        txt(c, 'Approved foster carer', 265, y - 22, 44, PLUM, PX, min(1, kt * 2), ax=0.0)
        txt(c, 'Welcome to the Organic Fostering family', 265, y + 32, 25, MUTEDC, PM, min(1, kt * 2), ax=0.0)
    kn = prog(t, done + 0.7, done + 1.1)
    if kn > 0:
        txt(c, 'The agency decision maker makes the final decision.', W / 2, 1625, 30, PLUM, PS, kn)
    c = push(c, t, t0)
    hud(c, t)
    return c


BENTO = [  # (x, y, w, h, title, sub, icon, tile colour)
    (60, 600, 560, 340, 'Supervising', 'social worker', 'person', MAGENTA),
    (644, 600, 376, 340, 'Advice outside', 'normal hours', 'phone', ORANGE_B),
    (60, 964, 376, 300, 'Ongoing', 'training', 'cap', GREEN),
    (460, 964, 560, 300, 'Other foster', 'carers', 'chat', PLUM),
    (60, 1288, 960, 400, None, None, 'coin', CREAM_C),
]


def bento(c, t, t0, collapse=0.0):
    for j, (x, y, w, h, t1, t2, ic, acc) in enumerate(BENTO):
        tt = t0 + 0.25 + j * 0.2
        k = prog(t, tt, tt + 0.4)
        if k <= 0:
            continue
        e = e_out_back(k, 1.6)
        cx, cy = x + w / 2, y + h / 2
        # snap in from slightly further out
        cx = lerp(W / 2 + (cx - W / 2) * 1.25, cx, e)
        cy = lerp(H / 2 + (cy - H / 2) * 1.25, cy, e)
        if collapse > 0:
            ce = e_in_cubic(collapse)
            cx, cy = lerp(cx, W / 2, ce), lerp(cy, 760, ce)
            w, h = lerp(w, 200, ce), lerp(h, 120, ce)
        op = min(1, k * 3) * (1 - collapse)
        if op <= 0.01:
            continue
        block(c, cx, cy, w, h, r=36, fill=acc, op=op, sh=12, bw=4)
        if collapse > 0.3:
            continue
        if ic == 'coin':
            icon3d(c, 'coin', t, x + 200, cy + 10, 250, tt + 0.1, op=op)
            txt(c, 'Allowance from', x + 380, cy - 95, 36, MUTEDC, PS, op, ax=0.0)
            spr = word_spr('£447.60', PK, 124, ORANGE_B, (ORANGE_B, MAGENTA))
            draw(c, spr, x + 380 + spr.shape[1] / 2, cy + 10, opacity=op)
            if t > tt + 0.6:
                p = (t - tt - 0.6) / 0.8 * 1.6 - 0.3
                if -0.3 < p < 1.3:
                    draw(c, sweep(spr, p), x + 380 + spr.shape[1] / 2, cy + 10, opacity=op)
            txt(c, 'a week*', x + 385, cy + 112, 36, PLUM, PB, op, ax=0.0)
        else:
            if w < 400:   # narrow tile: icon on top, text below
                icon3d(c, ic, t + j, x + 100, y + 40 + h * 0.3, 120, tt + 0.1, op=op, shadow_on=False)
                txt(c, t1, x + 40, y + h - 95, 36, CREAM_C, PX, op, ax=0.0)
                txt(c, t2, x + 40, y + h - 50, 30, CREAM_C, PS, op * 0.85, ax=0.0)
            else:
                icon3d(c, ic, t + j, x + 105, cy + 15, 160, tt + 0.1, op=op, shadow_on=False)
                txt(c, t1, x + 210, cy - 12, 42, CREAM_C, PX, op, ax=0.0)
                txt(c, t2, x + 210, cy + 40, 34, CREAM_C, PS, op * 0.85, ax=0.0)


def sc_sup(t):
    t0 = T['sup']
    c = bg(t)
    lt = t - t0
    title3d(c, 'And the support', W / 2, 330, 78, t, t0 + 0.05, fill=PLUM, ext=ORANGE_B, sweep_t=t0 + 0.8)
    title3d(c, "doesn't stop there.", W / 2, 440, 78, t, t0 + 0.3, fill=MAGENTA, ext=INKP)
    collapse = prog(t, T['cta'] - 0.35, T['cta'])
    bento(c, t, t0, collapse)
    # camera pull-back
    z = 1.14 - 0.14 * e_out_cubic(prog(t, t0, t0 + 1.0))
    if z > 1.001:
        M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, 1100 - z * 1100]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    # stepper slides away
    ho = 1 - prog(t, t0, t0 + 0.4)
    hud(c, t, op=ho, dy=-220 * (1 - ho))
    return c


@functools.lru_cache(maxsize=1)
def grad_bg():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    u = np.clip((xs / W * 0.45 + ys / H * 0.8) / 1.25, 0, 1)[..., None]
    a = np.array(hexc('#8E0F5E')[:3], np.float32)
    m = np.array(MAGENTA[:3], np.float32)
    o = np.array(ORANGE_B[:3], np.float32)
    return np.where(u < 0.5, a * (1 - u * 2) + m * u * 2, m * (1 - (u - 0.5) * 2) + o * (u - 0.5) * 2).astype(np.float32)


def sc_cta(t):
    t0 = T['cta']
    c = grad_bg().copy()
    rings = np.zeros((H, W), np.float32)
    for (bx, by, r, ph) in [(900, 380, 360, 0), (140, 1650, 300, 2)]:
        cv2.circle(rings, (int(bx + 40 * math.sin(t * 0.5 + ph)), int(by + 30 * math.cos(t * 0.4 + ph))), r, 1.0, -1,
                   cv2.LINE_AA)
    c += rings[..., None] * 0.08 * (1 - c)
    c += dot_grid() * 0.07 * (1 - c)
    title3d(c, 'Step 1 starts with', W / 2, 410, 74, t, t0 + 0.2, fill=CREAM_C, ext=INKP)
    title3d(c, 'a conversation.', W / 2, 510, 74, t, t0 + 0.5, fill=CREAM_C, ext=INKP, sweep_t=t0 + 1.2)
    # the bento collapses into one glowing button
    kb = prog(t, t0, t0 + 0.45)
    press = math.sin(math.pi * prog(t, CLICK_CTA - 0.06, CLICK_CTA + 0.2))
    button(c, W / 2, 760, 680 * (0.5 + 0.5 * e_out_back(kb, 1.8)), 140, 'Start your enquiry', t, press=press,
           op=min(1, kb * 2), glow_c=(1.0, 0.85, 0.7, 1), size=48)
    ripple(c, 700, 770, t, CLICK_CTA, (1, 1, 1, 1), n=3, rmax=460)
    cursor(c, t, (960, 1500), (700, 770), t0 + 0.35, CLICK_CTA - 0.05, CLICK_CTA, op=1 - prog(t, CLICK_CTA + 0.5,
                                                                                               CLICK_CTA + 0.8))
    # logo resolves
    kl = prog(t, CLICK_CTA + 0.25, CLICK_CTA + 0.75)
    if kl > 0:
        glass(c, W / 2, 1100, 860, 340, r=48, tint_c=(1, 1, 1), tint_a=0.96, opacity=min(1, kl * 2.5), blur=24,
              shadow_a=0.45, border_a=0.9)
        lg = fitted('logo', png('logo_full'), width=720)
        draw(c, lg, W / 2, 1100, scale=0.9 + 0.1 * e_out_back(kl, 2.0), opacity=min(1, kl * 2))
        if CLICK_CTA + 0.8 < t < CLICK_CTA + 1.8:
            p = (t - CLICK_CTA - 0.8) / 0.9 * 1.6 - 0.3
            draw(c, sweep(np.zeros_like(lg), p), W / 2, 1100)
            draw(c, sweep(lg, p, strength=0.6), W / 2, 1100, opacity=0.5)
    ki = prog(t, CLICK_CTA + 0.7, CLICK_CTA + 1.1)
    if ki > 0:
        title3d(c, '0161 241 1332', W / 2, 1380, 64, t, CLICK_CTA + 0.7, fill=CREAM_C, ext=INKP, depth=4)
        txt(c, 'organicfostering.co.uk', W / 2, 1462, 40, CREAM_C, PB, ki)
    ko = prog(t, CLICK_CTA + 1.0, CLICK_CTA + 1.4)
    if ko > 0:
        p = pill('Rated Good by Ofsted', PB, 30, pad_x=30, pad_y=14, fill=CREAM_C, border=INKP,
                 text_color=PLUM, dot=GREEN)
        draw(c, p, W / 2, 1560, scale=e_out_back(ko, 2.2), opacity=min(1, ko * 3))
    ks = prog(t, CLICK_CTA + 1.3, CLICK_CTA + 1.7)
    if ks > 0:
        txt(c, '*Weekly allowance for one child aged 0–4, based on current published rates.', W / 2, 1740, 26,
            CREAM_C, PS, ks, shadow_op=0.5)
        txt(c, 'Rates may vary by region and are subject to change.', W / 2, 1782, 26, CREAM_C, PS, ks,
            shadow_op=0.5)
    return c


SCENES = [(T['hook'], T['flow'], sc_hook), (T['flow'], T['s1'], sc_flow), (T['s1'], T['s2'], sc_s1),
          (T['s2'], T['s3'], sc_s2), (T['s3'], T['s4'], sc_s3), (T['s4'], T['s5'], sc_s4), (T['s5'], T['sup'], sc_s5),
          (T['sup'], T['cta'], sc_sup), (T['cta'], 99, sc_cta)]
TRANS = [(HOOK_MONTAGE, 'flash'), (T['flow'], 'zoom'), (T['s1'], 'whip'), (T['s2'], 'whip'), (T['s3'], 'whip'),
         (T['s4'], 'whip'), (T['s5'], 'flashw'), (T['sup'], 'zoom'), (T['cta'], 'flashw')]


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f
    return SCENES[-1][2]


def render_raw(t):
    c = scene_at(t)(t)
    for tc, kind in TRANS:
        d = t - tc
        if kind == 'whip' and -0.15 < d < 0.15:
            c = whip(c, 1 - abs(d) / 0.15, -1)
        elif kind == 'zoom' and -0.12 < d < 0.15:
            c = zoom_blur(c, (1 - abs(d) / 0.15) * 4)
        elif kind == 'flash' and -0.04 < d < 0.3:
            c = c + np.array((1.0, 0.85, 0.9), np.float32) * 0.9 * math.exp(-max(0, d) * 12)
        elif kind == 'flashw' and -0.1 < d < 0.35:
            c = c + 0.8 * math.exp(-abs(d) * 10)
            if abs(d) < 0.12:
                c = zoom_blur(c, (1 - abs(d) / 0.12) * 3)
    dx = dy = 0.0
    for tc in [CLICK_HOOK, CLICK_CTA] + CHECKS + [T['s2'] + 0.55]:
        sx, sy = shake(t, tc, amp=9, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - 0.35:
        c *= 1 - 0.9 * prog(t, DUR - 0.35, DUR)
    return c


def is_fast(t):
    if t < HOOK_MONTAGE + 0.1:
        return True
    return any(abs(t - tc) < 0.2 for tc, _ in TRANS) or abs(t - CLICK_HOOK) < 0.25


def render(fi):
    t = fi / FPS
    if is_fast(t):
        acc = None
        for k in range(3):
            r = render_raw(max(0.0, t + (k / 3 - 0.5) * 0.5 / FPS))
            acc = r if acc is None else acc + r
        c = acc / 3
    else:
        c = render_raw(t)
    return post(c, fi, bloom=0.18, grain=0.014, ca=1.5 if t < HOOK_MONTAGE else 0.0,
                vig=1.0 if t < HOOK_MONTAGE else 0.4)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            cv2.imwrite(f'{S}/stills/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))), [cv2.IMWRITE_JPEG_QUALITY, 90])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_out', exist_ok=True)
        for fi in range(a, b):
            cv2.imwrite(f'{S}/frames_out/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
