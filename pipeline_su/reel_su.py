"""Organic Fostering — "Support Update Available" (9:16, 30 s): a software-update metaphor for existing foster carers.

Montage hook -> 3D phone lock screen with "Fostering Support: update available" -> system check (six questions,
3D clay icons, spinners) -> release notes (checks cascade, Ofsted badge, "All included.") -> "the children I look
after" chat over cinematic footage -> Install becomes "Explore a transfer" -> leafy end card.
Look: night-neon glass (plum, magenta edge glow, orange buttons, green checks, Poppins).

Usage:
  python3 reel_su.py still 1.0,5.0
  python3 reel_su.py range 0 900
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_su')))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import numpy as np
import cv2
import reel_of as R
from reel_of import (glass, kinetic_line, word_spr, sweep, glow_add, shadow, scrim, grade, whip, zoom_blur, shake,
                     check_spr, rrect_spr, clip_frame, light_leak, PLUM, MAGENTA, ORANGE_B, GREEN, PEACH, MUTEDC, WHITE_)
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30

# ------------------------------------------------------------------ brand + type
PINK = hexc('#FF5FB0')
LAV = hexc('#F7ECF6')
GOLD = hexc('#FFD54A')
ORANGE_L = hexc('#FFA24D')
INK = hexc('#3A0E35')
PB, PX, PK, PS, PM, PR, PL = ('Poppins-Bold', 'Poppins-ExtraBold', 'Poppins-Black', 'Poppins-SemiBold',
                              'Poppins-Medium', 'Poppins-Regular', 'Poppins-Light')

# ------------------------------------------------------------------ timeline (120 BPM grid)
T = dict(hook=0.0, lock=1.0, tap=3.5, check=4.25, notes=8.0, care=15.0, install=21.5, cta=25.4)
DUR = 30.0
NF = int(DUR * FPS)
# VO starts; visuals below are synced to the phrase onsets inside each line (see vo_su.py)
VO = {'hook': 0.15, 'check': 4.4, 'included': 8.2, 'care': 15.15, 'install': 21.7, 'cta': 25.65}
NOTIF = 1.3
Q_T = [4.5 + 0.6 * i for i in range(6)]
CHK_T = [8.9 + 0.2 * i for i in range(6)]
ALL_T = VO['included'] + 1.75                        # "...it's all included."
OFSTED_T = VO['included'] + 3.45                     # "From an Ofsted-rated Good..."
IND_T = VO['included'] + 5.1                         # "...independent agency."
CARE_CUT = VO['care'] + 1.85                         # cut to the hands as she says "We focus on..."
TAP_INSTALL = 22.6
TOAST_T = VO['install'] + 1.7                        # "...with no immediate commitment."
CTA_TALK = VO['cta'] + 1.82                          # "Let's talk."
FADE = 1.3                                           # gentle fade-out at the very end
QUESTIONS = [(('A supervising social worker', 'who knows your family?'), 'person'),
             (('Advice outside', 'normal hours?'), 'clock'),
             (('Ongoing learning', 'and training?'), 'book'),
             (('Other foster carers', 'to lean on?'), 'group'),
             (('Help with school', 'and health needs?'), 'cap'),
             (('Matching that sees culture,', 'faith and identity?'), 'heart')]
NOTES = [('A supervising social worker', 'who knows your family'), ('Advice outside normal hours',),
         ('Ongoing learning and training',), ('Other foster carers to lean on',),
         ('Help with school and health needs',), ('Matching that sees culture,', 'faith and identity')]

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


def paste(dst, src, cx, cy, op=1.0):
    h, w = src.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = src[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * op
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


def icon3d(canvas, name, t, x, y, size, t0=None, op=1.0, glow=None):
    s = 1.0
    if t0 is not None:
        if t < t0:
            return
        k = prog(t, t0, t0 + 0.45)
        s = e_out_back(k, 2.2)
        op *= min(1, k * 3)
    f = seq(name).frame(t)
    if f.shape[0] < 16:
        return
    sc = size / max(f.shape[:2]) * s
    if glow is not None:
        glow_add(canvas, f, x, y, glow, sigma=18, strength=0.5 * op, scale=sc)
    sh = blur_sprite(tint(f, (0.10, 0.0, 0.08)), 12)
    draw(canvas, sh, x + 6, y + size * 0.08, scale=sc, opacity=0.4 * op)
    draw(canvas, f, x, y, scale=sc, opacity=op)


def title(canvas, text, cx, cy, size, t, t0, color=WHITE_, glow=MAGENTA, fname=PK, sweep_t=None, depth=0,
          ext=None, stagger=0.05, glow_str=0.55, shadow_op=0.6):
    """Readable headline: optional 3D extrusion, deep glow, soft shadow and light sweep."""
    if depth:
        for k in range(depth, 0, -1):
            kinetic_line(canvas, text, cx + k, cy + k, size, t, t0, color=ext or INK, fname=fname, shadow_op=0.0,
                         stagger=stagger)
    kinetic_line(canvas, text, cx, cy, size, t, t0, color=color, fname=fname, glow=glow, glow_str=glow_str,
                 shadow_op=shadow_op, stagger=stagger, sweep_t=sweep_t)


# ------------------------------------------------------------------ background: night neon
_Y, _X = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)


def _blob(cx, cy, r):
    d = np.sqrt((_X - cx / 4) ** 2 + (_Y - cy / 4) ** 2) / (r / 4)
    return np.exp(-d * d)[..., None]


def bg(t, bright=0.0):
    base = vgrad(H // 4, W // 4, hexc('#2A0926'), hexc('#140512'))
    for (cx, cy, r, col, a, ph) in [(220, 380, 560, MAGENTA, 0.55, 0.0), (900, 1500, 620, ORANGE_B, 0.30, 1.9),
                                    (980, 600, 420, PLUM, 0.7, 3.0), (120, 1650, 480, MAGENTA, 0.35, 4.2)]:
        x = cx + 80 * math.sin(t * 0.5 + ph)
        y = cy + 60 * math.cos(t * 0.45 + ph)
        b = _blob(x, y, r) * (a + bright * 0.2)
        base = base * (1 - b) + np.array(col[:3], np.float32) * b
    c = cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)
    # diagonal neon light beams
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    for off, col, a in ((0.15 + 0.05 * math.sin(t * 0.4), MAGENTA, 0.10), (0.75 + 0.04 * math.cos(t * 0.3), ORANGE_B, 0.06)):
        u = xs * 0.8 + ys * 0.45 - off
        beam = np.exp(-(u / 0.05) ** 2)[..., None]
        c += beam * np.array(col[:3], np.float32) * a
    return c


def neon_card(canvas, cx, cy, w, h, r=40, op=1.0, light=True, glow_c=MAGENTA, glow_a=0.55):
    """Glass card with a soft magenta edge glow (light lavender glass by default)."""
    if op <= 0.01:
        return
    edge = solid(sdf_stroke(rrect_alpha(int(w), int(h), r, 30), 6.0), glow_c)
    draw(canvas, blur_sprite(edge, 16), cx, cy, opacity=glow_a * op, mode='add')
    glass(canvas, cx, cy, w, h, r=r, tint_c=(0.98, 0.93, 0.98) if light else (0.35, 0.08, 0.32),
          tint_a=0.88 if light else 0.35, opacity=op, blur=24, shadow_a=0.45, border_a=0.7)


def spinner(canvas, x, y, t, size=58, color=MAGENTA, op=1.0):
    s = size * 2
    im = np.zeros((s, s), np.float32)
    a0 = (t * 540) % 360
    cv2.ellipse(im, (s // 2, s // 2), (s // 2 - 8, s // 2 - 8), a0, 0, 250, 1.0, 7, cv2.LINE_AA)
    spr = cv2.resize(solid(im, color), (size, size), interpolation=cv2.INTER_AREA)
    draw(canvas, spr, x, y, opacity=op)


def ripple(canvas, x, y, t, t0, color=MAGENTA, n=3, rmax=260):
    for j in range(n):
        k = prog(t, t0 + j * 0.09, t0 + j * 0.09 + 0.7)
        if 0 < k < 1:
            r = 20 + rmax * e_out_cubic(k)
            draw(canvas, ring_sprite(int(2 * r + 60), r, 5 - 2 * k, color, glow=10), x, y, opacity=(1 - k) * 0.9)


def sparks(canvas, x, y, t, t0, color=WHITE_, n=5, r0=70, r1=130):
    k = prog(t, t0, t0 + 0.35)
    if not 0 < k < 1:
        return
    for j in range(n):
        a = -math.pi / 2 + (j - (n - 1) / 2) * 0.55
        p0 = (x + math.cos(a) * (r0 + 40 * k), y + math.sin(a) * (r0 + 40 * k))
        p1 = (x + math.cos(a) * (r0 + (r1 - r0) * e_out_cubic(k)), y + math.sin(a) * (r0 + (r1 - r0) * e_out_cubic(k)))
        cv2.line(canvas, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), tuple(float(v) * (1 - k) + 0.0 for v in color[:3]),
                 5, cv2.LINE_AA)


def cursor(canvas, t, p0, p1, t0, t1, click_t, size=120, op=1.0):
    if t < t0:
        return
    k = e_inout_cubic(prog(t, t0, t1))
    x = lerp(p0[0], p1[0], k) + 40 * math.sin(k * math.pi)
    y = lerp(p0[1], p1[1], k) - 60 * math.sin(k * math.pi)
    press = 1 - 0.18 * math.sin(math.pi * prog(t, click_t - 0.06, click_t + 0.14))
    f = seq('cursor').frame(t)
    if f.shape[0] < 16:
        return
    sc = size / max(f.shape[:2]) * press
    sh = blur_sprite(tint(f, (0.05, 0, 0.05)), 8)
    o = op * min(1, prog(t, t0, t0 + 0.2))
    draw(canvas, sh, x + 10, y + 14, scale=sc, opacity=0.5 * o, ax=0.08, ay=0.04)
    draw(canvas, f, x, y, scale=sc, opacity=o, ax=0.08, ay=0.04)


# ------------------------------------------------------------------ phone (2.5D, drawn on a perspective plane)
PW, PH = 640, 1310
SW, SH = 584, 1254


@functools.lru_cache(maxsize=1)
def phone_body():
    a = sdf_fill(rrect_alpha(PW, PH, 96, 0))
    h, w = a.shape
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xs / w * 0.6 + ys / h * 0.4)
    rim = np.array(hexc('#6B2A60')[:3]) * (1 - u[..., None]) + np.array(hexc('#1C0819')[:3]) * u[..., None]
    rim += np.exp(-((xs / w - 0.12) / 0.05) ** 2)[..., None] * 0.35          # specular strip on the frame
    body = np.concatenate([rim * a[..., None], a[..., None]], 2).astype(np.float32)
    bez = rrect_spr(PW - 14, PH - 14, 90, (0.02, 0.01, 0.02, 1.0))
    paste(body, bez, w / 2, h / 2)
    return body


@functools.lru_cache(maxsize=1)
def screen_mask():
    return sdf_fill(rrect_alpha(SW, SH, 74, 0))[..., None]


@functools.lru_cache(maxsize=1)
def wallpaper():
    ys = np.linspace(0, 1, SH, dtype=np.float32)[:, None, None]
    top = np.array(hexc('#2B0A28')[:3], np.float32)
    mid = np.array(hexc('#6A1B5C')[:3], np.float32)
    bot = np.array(hexc('#C2185B')[:3], np.float32)
    rgb = np.where(ys < 0.6, top * (1 - ys / 0.6) + mid * ys / 0.6, mid * (1 - (ys - 0.6) / 0.4) + bot * (ys - 0.6) / 0.4)
    rgb = np.repeat(rgb, SW, axis=1)
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    g = np.exp(-(((xx - SW * 0.85) / 260) ** 2 + ((yy - SH * 0.92) / 240) ** 2))[..., None]
    rgb = rgb * (1 - g * 0.6) + np.array(ORANGE_B[:3], np.float32) * g * 0.6
    return rgb.astype(np.float32)


@functools.lru_cache(maxsize=1)
def padlock():
    s = 120
    im = np.zeros((s, s), np.float32)
    cv2.ellipse(im, (s // 2, 46), (24, 26), 0, 180, 360, 1.0, 9, cv2.LINE_AA)
    cv2.rectangle(im, (s // 2 - 34, 46), (s // 2 + 34, 100), 1.0, -1, cv2.LINE_AA)
    return cv2.resize(solid(im, WHITE_), (52, 52), interpolation=cv2.INTER_AREA)


def notif_spr():
    w, h = 540, 170
    spr = rrect_spr(w, h, 34, (0.99, 0.92, 0.98, 0.95), border=(1, 1, 1, 1), bw=2)
    ic = rrect_spr(88, 88, 22, (1, 1, 1, 1))
    paste(ic, fitted('emblem', png('emblem'), height=58), 44, 44)
    paste(spr, ic, 72, h / 2)
    app = text_sprite('Organic Fostering', PM, 22, hexc('#7A5A78'))
    paste(spr, app, 135 + app.shape[1] / 2, 50)
    paste(spr, text_sprite('now', PM, 22, hexc('#7A5A78')), w - 50, 50)
    for j, line in enumerate(('Fostering Support:', 'update available')):
        ts = text_sprite(line, PB, 32, INK)
        paste(spr, ts, 135 + ts.shape[1] / 2, 94 + j * 40)
    return spr


@functools.lru_cache(maxsize=1)
def notif_cached():
    return notif_spr()


def lock_screen(t):
    scr = np.concatenate([wallpaper().copy(), np.ones((SH, SW, 1), np.float32)], 2)
    paste(scr, text_sprite('9:14', PS, 24, WHITE_), 70, 40)
    for j in range(4):
        paste(scr, rrect_spr(7, 10 + j * 5, 2, WHITE_), SW - 150 + j * 11, 44 - j * 2.5)
    paste(scr, rrect_spr(46, 22, 7, (1, 1, 1, 0.9)), SW - 70, 40)
    paste(scr, padlock(), SW / 2, 150)
    paste(scr, text_sprite('9:14', PL, 190, WHITE_), SW / 2, 300)
    paste(scr, text_sprite('Monday 12 October', PM, 34, (1, 1, 1, 0.9)), SW / 2, 425)
    k = prog(t, NOTIF, NOTIF + 0.45)
    if k > 0:
        y = 560 + (1 - e_out_back(k, 1.8)) * -420
        n = notif_cached()
        g = blur_sprite(tint(rrect_spr(n.shape[1], n.shape[0], 34, WHITE_), MAGENTA[:3]), 18)
        paste(scr, g, SW / 2, y, op=0.8 * min(1, k * 2))
        paste(scr, n, SW / 2, y, op=min(1, k * 3))
    return scr


def app_screen(t, t0):
    scr = np.concatenate([np.ones((SH, SW, 3), np.float32) * np.array(LAV[:3], np.float32),
                          np.ones((SH, SW, 1), np.float32)], 2)
    paste(scr, fitted('logo_s', png('logo_full'), width=400), SW / 2, 230)
    k = prog(t, t0, t0 + 0.35)
    y = 640 + 80 * (1 - e_out_cubic(k))
    card = rrect_spr(500, 280, 36, (1, 1, 1, 1), border=(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.25), bw=2)
    paste(scr, card, SW / 2, y, op=min(1, k * 2))
    paste(scr, text_sprite('Checking', PM, 40, INK), SW / 2, y - 70, op=k)
    paste(scr, text_sprite('your support…', PM, 40, INK), SW / 2, y - 20, op=k)
    paste(scr, rrect_spr(380, 30, 15, (PLUM[0], PLUM[1], PLUM[2], 0.12)), SW / 2, y + 70, op=k)
    p = e_inout_cubic(prog(t, t0 + 0.2, t0 + 1.4))
    if p > 0.02:
        bar = rrect_spr(380 * p, 30, 15, None, grad=(MAGENTA, ORANGE_B))
        paste(scr, bar, SW / 2 - 190 + 190 * p, y + 70, op=k)
    return scr


def phone_spr(screen):
    body = phone_body().copy()
    scr = screen * screen_mask()
    paste(body, scr, PW / 2, PH / 2)
    paste(body, rrect_spr(150, 40, 20, (0, 0, 0, 1)), PW / 2, 62)      # dynamic island
    # glass reflection
    h, w = body.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    refl = np.clip(1 - np.abs((xs / w) - (ys / h) * 0.5 - 0.15) / 0.12, 0, 1) * 0.06
    body[..., :3] += refl[..., None] * body[..., 3:4]
    return body


def draw_phone(canvas, spr, cx, cy, w, rx, ry, rz=0.0, op=1.0):
    q = plane_quad(cx, cy, 0, w, w * PH / PW, rx, ry, rz)[0]
    # soft drop shadow under the phone
    sh = blur_sprite(tint(rrect_spr(PW, PH, 96, WHITE_), (0.04, 0.0, 0.04)), 30)
    draw3d(canvas, sh, cx + 30, cy + 40, 0, w * 1.02, None, rx=rx, ry=ry, rz=rz, opacity=0.6 * op)
    edge = blur_sprite(tint(rrect_spr(PW, PH, 96, WHITE_), MAGENTA[:3]), 26)
    draw3d(canvas, edge, cx, cy, 0, w * 1.04, None, rx=rx, ry=ry, rz=rz, opacity=0.5 * op, mode='add')
    draw3d(canvas, spr, cx, cy, 0, w, None, rx=rx, ry=ry, rz=rz, opacity=op)
    return q


# ------------------------------------------------------------------ scenes
HOOK_CUTS = [(1, 1.0), (5, 1.4), (6, 1.8), (7, 1.0)]


def sc_hook(t):
    i = min(int(t / 0.25), 3)
    ci, off = HOOK_CUTS[i]
    lt = t - i * 0.25
    z = 1.2 - 0.12 * e_out_cubic(lt / 0.25)
    c = grade(clip_frame(ci, off + lt * 1.5, zoom=z, rot=(1.6 if i % 2 else -1.6) * (1 - lt / 0.25)), warm=0.5)
    c = c * 0.78 + np.array([0.08, 0.0, 0.06], np.float32)
    scrim(c, top=0.5, bottom=0.6, top_h=0.55, bot_h=0.55)
    # glitch on each cut: RGB split + scanlines
    if lt < 0.06:
        k = 1 - lt / 0.06
        sh = int(18 * k)
        c = np.stack([np.roll(c[..., 0], sh, 1), c[..., 1], np.roll(c[..., 2], -sh, 1)], 2)
        c[::6] *= 1 - 0.25 * k
        c += 0.18 * k
    title(c, 'Already a', W / 2, 820, 104, t, 0.06, glow=MAGENTA, depth=6, ext=MAGENTA)
    title(c, 'foster carer?', W / 2, 950, 112, t, 0.18, glow=ORANGE_B, depth=6, ext=ORANGE_B, sweep_t=0.55)
    return c


def phone_pose(t):
    """Cinematic camera on the phone: arcs in, settles, then pushes into the screen."""
    k = e_out_cubic(prog(t, T['lock'], T['lock'] + 0.9))
    rx = lerp(28, 7, k) + 1.5 * math.sin(t * 1.3)
    ry = lerp(-26, -9, k) + 2.0 * math.sin(t * 0.9)
    rz = lerp(-6, -1.5, k)
    cx, cy, w = W / 2, lerp(1300, 1130, k), lerp(580, 700, k)
    kt = e_inout_cubic(prog(t, T['tap'] - 0.1, T['tap'] + 0.3))
    rx, ry, rz = lerp(rx, 0, kt), lerp(ry, 0, kt), lerp(rz, 0, kt)
    kp = e_in_cubic(prog(t, T['tap'] + 0.35, T['check']))
    w = w * (1 + 1.9 * kp)
    cy = lerp(cy, H / 2, kp)
    # buzz
    for tb in (NOTIF - 0.05, NOTIF + 0.2):
        kb = prog(t, tb, tb + 0.18)
        if 0 < kb < 1:
            rz += 2.2 * math.sin(kb * math.pi * 8) * (1 - kb)
    return cx, cy, w, rx, ry, rz


def sc_lock(t):
    c = bg(t)
    title(c, 'Already a foster carer?', W / 2, 200, 70, t, T['lock'] - 0.2, glow=MAGENTA, fname=PK, stagger=0.0)
    kinetic_line(c, "This one's for you.", W / 2, 300, 58, t, T['lock'] + 0.45, color=PINK, fname=PB, glow=MAGENTA,
                 glow_str=0.5, shadow_op=0.6, sweep_t=T['lock'] + 1.1)
    fade_txt = prog(t, T['tap'], T['tap'] + 0.3)
    if fade_txt > 0:
        c = bg(t) * fade_txt + c * (1 - fade_txt)
    scr = lock_screen(t) if t < T['tap'] + 0.05 else app_screen(t, T['tap'] + 0.05)
    if T['tap'] - 0.02 < t < T['tap'] + 0.15:
        a = prog(t, T['tap'] - 0.02, T['tap'] + 0.15)
        scr = lock_screen(t) * (1 - a) + app_screen(t, T['tap'] + 0.05) * a
    cx, cy, w, rx, ry, rz = phone_pose(t)
    draw_phone(c, phone_spr(scr), cx, cy, w, rx, ry, rz)
    # cursor taps the notification
    ny = cy + (28 + 560 - PH / 2) * w / PW
    if t < T['tap'] + 0.45:
        cursor(c, t, (980, 1800), (620, ny + 10), T['lock'] + 1.3, T['tap'] - 0.05, T['tap'],
               op=1 - prog(t, T['tap'] + 0.15, T['tap'] + 0.4))
        ripple(c, 620, ny + 10, t, T['tap'], MAGENTA, n=2, rmax=200)
    return c


def sc_check(t):
    t0 = T['check']
    c = bg(t, 0.2)
    title(c, 'Checking your support…', W / 2, 250, 60, t, t0 + 0.05, glow=MAGENTA, fname=PX, stagger=0.04)
    p = e_inout_cubic(prog(t, t0 + 0.1, T['notes'] - 0.25))
    draw(c, rrect_spr(820, 18, 9, (1, 1, 1, 0.14)), W / 2, 335)
    if p > 0.01:
        bar = rrect_spr(820 * p, 18, 9, None, grad=(MAGENTA, ORANGE_B))
        glow_add(c, bar, W / 2 - 410 + 410 * p, 335, ORANGE_B, sigma=12, strength=0.7)
        draw(c, bar, W / 2 - 410 + 410 * p, 335)
    for i, ((l1, l2), ic) in enumerate(QUESTIONS):
        k = prog(t, Q_T[i], Q_T[i] + 0.4)
        if k <= 0:
            continue
        e = e_out_back(k, 1.5)
        y = 500 + i * 200 + 140 * (1 - e)
        newest = i == 5 or t < Q_T[min(i + 1, 5)]
        neon_card(c, W / 2, y, 920, 172, r=36, op=min(1, k * 2.5), glow_a=0.95 if newest else 0.35)
        icon3d(c, ic, t + i * 0.4, 165, y, 132, Q_T[i] + 0.08)
        txt(c, l1, 260, y - 24, 37, INK, PB, min(1, k * 2), ax=0.0)
        txt(c, l2, 260, y + 26, 37, INK, PB, min(1, k * 2), ax=0.0)
        spinner(c, 930, y, t + i * 0.2, 60, MAGENTA, min(1, k * 2))
    # gentle camera drift
    z = 1 + 0.03 * prog(t, t0, T['notes'])
    M = cv2.getRotationMatrix2D((W / 2, H * 0.55), 0.6 * math.sin(t * 0.8), z)
    return cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)


@functools.lru_cache(maxsize=1)
def ofsted_spr():
    s = 250
    im = np.zeros((s * 2, s * 2), np.float32)
    cv2.circle(im, (s, s), s - 6, 1.0, -1, cv2.LINE_AA)
    disc = solid(cv2.resize(im, (s, s), interpolation=cv2.INTER_AREA), hexc('#3F8F0B'))
    ring = np.zeros((s * 2, s * 2), np.float32)
    cv2.circle(ring, (s, s), s - 20, 1.0, 6, cv2.LINE_AA)
    disc = over_spr(disc, solid(cv2.resize(ring, (s, s), interpolation=cv2.INTER_AREA), (1, 1, 1, 0.8)))
    crown = np.zeros((120, 160), np.float32)
    pts = np.array([[20, 100], [20, 40], [55, 70], [80, 25], [105, 70], [140, 40], [140, 100]], np.int32)
    cv2.fillPoly(crown, [pts], 1.0, cv2.LINE_AA)
    paste(disc, cv2.resize(solid(crown, GOLD), (46, 34), interpolation=cv2.INTER_AREA), s / 2, 52)
    paste(disc, text_sprite('Rated', PB, 28, WHITE_), s / 2, 92)
    paste(disc, text_sprite('Good', PK, 50, GOLD), s / 2, 133)
    paste(disc, text_sprite('by Ofsted', PB, 26, WHITE_), s / 2, 172)
    paste(disc, text_sprite('May 2025', PM, 20, (1, 1, 1, 0.9)), s / 2, 202)
    return disc


def sc_notes(t):
    t0 = T['notes']
    c = bg(t, 0.3)
    k = prog(t, t0, t0 + 0.5)
    ke = e_out_cubic(k)
    cy = 1010 + 700 * (1 - ke)
    cw, ch = 940, 1250
    neon_card(c, W / 2, cy, cw, ch, r=48, op=min(1, k * 2), glow_a=0.7)
    top = cy - ch / 2
    if k > 0.2:
        op = min(1, (k - 0.2) * 3)
        txt(c, "What's included with", 110, top + 95, 50, INK, PX, op, ax=0.0)
        spr = word_spr('Organic Fostering', PK, 60, hexc('#4E9A0A'))
        draw(c, spr, 110 + spr.shape[1] / 2, top + 165, opacity=op)
        y = top + 290
        for i, lines in enumerate(NOTES):
            hh = 52 * len(lines)
            yc = y + hh / 2 - 26
            kk = prog(t, t0 + 0.3 + i * 0.07, t0 + 0.6 + i * 0.07)
            if kk > 0:
                draw(c, rrect_spr(cw - 120, hh + 40, 24, (1, 1, 1, 0.55)), W / 2, yc, opacity=min(1, kk * 2))
                kc = prog(t, CHK_T[i], CHK_T[i] + 0.3)
                if kc <= 0:
                    spinner(c, 160, yc, t + i * 0.3, 56, MAGENTA, min(1, kk * 2))
                else:
                    draw(c, check_spr(60, GREEN), 160, yc, scale=e_out_back(kc, 3.0))
                    if kc < 1:
                        draw(c, ring_sprite(200, 30 + 50 * kc, 4, GREEN, glow=8), 160, yc, opacity=1 - kc)
                for j, ln in enumerate(lines):
                    txt(c, ln, 215, yc + (j - (len(lines) - 1) / 2) * 50, 35, INK, PM, min(1, kk * 2), ax=0.0)
            y += hh + 62
        # "All included." pill
        ka = prog(t, ALL_T, ALL_T + 0.4)
        if ka > 0:
            p = pill('All included.', PK, 52, pad_x=60, pad_y=22, fill=hexc('#7CC223'), border=None,
                     text_color=INK, glow=(0.49, 0.76, 0.14, 0.6))
            py = cy + ch / 2 - 115
            draw(c, p, W / 2, py, scale=e_out_back(ka, 2.4), opacity=min(1, ka * 3))
            sparks(c, W / 2 + p.shape[1] / 2 - 30, py - 30, t, ALL_T + 0.15, hexc('#7CC223'))
    # Ofsted badge pins to the corner (and pulses as the voice says "Ofsted-rated Good")
    ko = prog(t, OFSTED_T, OFSTED_T + 0.4)
    if ko > 0:
        b = ofsted_spr()
        bx, by = W - 165, top + 30
        pulse = 1 + 0.06 * math.sin(math.pi * prog(t, IND_T, IND_T + 0.5))
        glow_add(c, b, bx, by, GREEN, sigma=20, strength=(0.6 + 0.4 * math.sin(math.pi * prog(t, IND_T, IND_T + 0.7))) * ko)
        draw(c, b, bx, by, scale=(1.6 - 0.6 * e_out_back(ko, 2.0)) * pulse, rot=-12 * (1 - ko) + 6,
             opacity=min(1, ko * 3))
    ki = prog(t, IND_T, IND_T + 0.4)
    if ki > 0:
        p = pill('Independent agency · Rated Good by Ofsted', PB, 30, pad_x=30, pad_y=14, fill=(1, 1, 1, 0.12),
                 border=(1, 1, 1, 0.6), text_color=WHITE_, dot=hexc('#7CC223'))
        draw(c, p, W / 2, 1760, scale=e_out_back(ki, 2.0), opacity=min(1, ki * 3))
    # slow push while the release notes hold
    z = 1 + 0.035 * e_inout_cubic(prog(t, t0 + 0.6, T['care']))
    if z > 1.001:
        M = np.float32([[z, 0, W / 2 - z * W / 2], [0, z, 1000 - z * 1000]])
        c = cv2.warpAffine(c, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return c


def chat(canvas, cx, cy, lines, t, t0, side, bold_idx=None, avatar=None):
    if t < t0:
        return
    k = prog(t, t0, t0 + 0.4)
    s = e_out_back(k, 2.2)
    sprs = [word_spr(l, PX if j == bold_idx else PS, 40, MAGENTA if j == bold_idx else INK) for j, l in enumerate(lines)]
    w = max(sp.shape[1] for sp in sprs) + 80
    h = len(lines) * 56 + 56
    bx = cx - w / 2 if side == 'right' else cx + w / 2
    bx += (1 - e_out_cubic(k)) * (80 if side == 'right' else -80)
    neon_card(canvas, bx, cy, w * s, h * s, r=40 * s, op=min(1, k * 3), glow_a=0.45)
    for j, sp in enumerate(sprs):
        yy = cy + (j - (len(lines) - 1) / 2) * 56
        draw(canvas, sp, bx - w / 2 * s + 40 * s + sp.shape[1] / 2 * s, yy, scale=s, opacity=min(1, k * 2.5))
    if avatar is not None:
        ax_ = bx + w / 2 * s + 80 if side == 'right' else bx - w / 2 * s - 80
        av = rrect_spr(120, 120, 60, (1, 1, 1, 1), border=(MAGENTA[0], MAGENTA[1], MAGENTA[2], 0.8), bw=3)
        draw(canvas, av, ax_, cy - h / 2 * s + 50, scale=s, opacity=min(1, k * 3))
        if avatar == 'emblem':
            draw(canvas, fitted('emblem', png('emblem'), height=70), ax_, cy - h / 2 * s + 50, scale=s,
                 opacity=min(1, k * 3))
        else:
            icon3d(canvas, avatar, t, ax_, cy - h / 2 * s + 52, 96, op=min(1, k * 3))
    return bx, w, h


def sc_care(t):
    t0 = T['care']
    lt = t - t0
    if t < CARE_CUT:   # shot 1: night bedroom, slow push
        z = 1.05 + 0.08 * e_inout_cubic(prog(t, t0, CARE_CUT))
        c = grade(clip_frame(6, 0.3 + lt * 0.8, zoom=z, cy=H * 0.5), warm=0.2, night=0.4)
        c = c * 0.85 + np.array([0.04, 0.0, 0.04], np.float32)
    else:              # shot 2: hands and seedling
        z = 1.06 + 0.10 * e_inout_cubic(prog(t, CARE_CUT, T['install']))
        c = grade(clip_frame(7, 0.4 + (t - CARE_CUT) * 0.9, zoom=z, cy=H * 0.55), warm=0.3)
        c = c * 0.72 + np.array([0.05, 0.0, 0.04], np.float32)
    scrim(c, top=0.75, bottom=0.92, top_h=0.55, bot_h=0.5)
    light_leak(c, prog(t, t0, t0 + 1.2) * 0.35, (1.0, 0.5, 0.35), side=1)
    chat(c, 820, 470, ['But what about the', 'children I look after?'], t, t0 + 0.3, 'right', avatar='person')
    ty = CARE_CUT - 1.0
    if ty <= t < ty + 1.1:
        k = prog(t, ty, ty + 0.2)
        glass(c, 330, 760, 180 * e_out_back(k), 90, r=45, tint_c=(1, 1, 1), tint_a=0.9, opacity=min(1, k * 3), blur=18)
        for i in range(3):
            ph = (t * 3.2 - i * 0.28) % 1.0
            dot = solid(sdf_fill(rrect_alpha(18, 18, 9, 2)), MUTEDC)
            draw(c, dot, 296 + i * 34, 760 - 9 * max(0, math.sin(ph * math.pi)))
    r = chat(c, 250, 790, ['We focus on', 'continuity of care', 'for them.'], t, CARE_CUT + 0.1, 'left', bold_idx=1,
             avatar='emblem')
    if r is not None:
        bx, w, h = r
        icon3d(c, 'heart', t, bx + w / 2 - 30, 790 + h / 2 - 20, 110, CARE_CUT + 0.45, glow=MAGENTA)
    title(c, 'Thinking of moving?', W / 2, 1560, 64, t, VO['care'] + 0.05, glow=MAGENTA, fname=PX, shadow_op=0.85)
    title(c, 'Start with a conversation.', W / 2, 1650, 58, t, CARE_CUT + 0.9, color=hexc('#FFE3F2'), glow=ORANGE_B,
          fname=PX, sweep_t=CARE_CUT + 1.6, shadow_op=0.85)
    kb = prog(t, CARE_CUT + 1.3, CARE_CUT + 1.7)
    if kb > 0:
        bar = rrect_spr(max(4, 260 * e_out_cubic(kb)), 10, 5, None, grad=(MAGENTA, ORANGE_B))
        draw(c, bar, W / 2, 1730)
    return c


def sc_install(t):
    t0 = T['install']
    c = bg(t, 0.4)
    # OF "app" icon
    ka = prog(t, t0, t0 + 0.45)
    if ka > 0:
        ic = rrect_spr(230, 230, 56, (1, 1, 1, 1))
        ic2 = ic.copy()
        paste(ic2, fitted('emblem', png('emblem'), height=150), 115, 115)
        glow_add(c, ic, W / 2, 500, MAGENTA, sigma=24, strength=0.6 * ka)
        draw(c, ic2, W / 2, 500, scale=e_out_back(ka, 2.0), opacity=min(1, ka * 3))
        txt(c, 'Organic Fostering', W / 2, 655, 34, WHITE_, PB, min(1, ka * 2), shadow_op=0.5)
    # big orange button: Install -> Explore a transfer (flip)
    kb = prog(t, t0 + 0.15, t0 + 0.55)
    if kb > 0:
        bw_, bh_ = 780, 200
        kf = prog(t, t0 + 0.55, t0 + 0.85)
        press = math.sin(math.pi * prog(t, TAP_INSTALL - 0.06, TAP_INSTALL + 0.2))
        spr = np.zeros((bh_ + 60, bw_ + 60, 4), np.float32)
        paste(spr, rrect_spr(bw_, bh_, 60, None, grad=(hexc('#FF7A1A'), hexc('#FF9A3C'))), spr.shape[1] / 2, spr.shape[0] / 2)
        paste(spr, solid(sdf_stroke(rrect_alpha(bw_, bh_, 60, 0), 3), (1, 1, 1, 0.55)), spr.shape[1] / 2, spr.shape[0] / 2)
        if kf < 0.5:
            paste(spr, text_sprite('Install', PK, 76, WHITE_), spr.shape[1] / 2, spr.shape[0] / 2)
        else:
            paste(spr, text_sprite('Explore', PK, 64, WHITE_), spr.shape[1] / 2, spr.shape[0] / 2 - 36)
            paste(spr, text_sprite('a transfer', PK, 64, WHITE_), spr.shape[1] / 2, spr.shape[0] / 2 + 38)
        ang = kf * 180 if kf < 0.5 else (kf - 1) * 180
        s = (0.8 + 0.2 * e_out_back(kb, 2.0)) * (1 - 0.05 * press)
        g = blur_sprite(tint(rrect_spr(bw_, bh_, 60, WHITE_), ORANGE_B[:3]), 30)
        draw(c, g, W / 2, 900, scale=s * 1.05, opacity=0.8 * (0.8 + 0.2 * math.sin(t * 5)), mode='add')
        draw3d(c, spr, W / 2, 900, 0, spr.shape[1] * s, None, rx=ang, opacity=min(1, kb * 3))
        sparks(c, W / 2 + 300, 830, t, TAP_INSTALL + 0.02, WHITE_, n=5, r0=60, r1=140)
        ripple(c, W / 2 + 210, 920, t, TAP_INSTALL, WHITE_, n=3, rmax=320)
    cursor(c, t, (980, 1700), (W / 2 + 210, 920), t0 + 0.4, TAP_INSTALL - 0.05, TAP_INSTALL,
           op=1 - prog(t, TOAST_T, TOAST_T + 0.3))
    # progress panel
    kp = prog(t, TAP_INSTALL + 0.05, TAP_INSTALL + 0.3)
    if kp > 0:
        neon_card(c, W / 2, 1160, 780, 190, r=40, op=min(1, kp * 3), light=False)
        p = e_inout_cubic(prog(t, TAP_INSTALL + 0.1, TOAST_T - 0.05))
        draw(c, rrect_spr(640, 26, 13, (1, 1, 1, 0.15)), W / 2, 1130, opacity=kp)
        if p > 0.01:
            bar = rrect_spr(640 * p, 26, 13, None, grad=(MAGENTA, PINK))
            glow_add(c, bar, W / 2 - 320 + 320 * p, 1130, MAGENTA, sigma=12, strength=0.7)
            draw(c, bar, W / 2 - 320 + 320 * p, 1130)
        txt(c, 'Conversation requested…', W / 2, 1200, 34, WHITE_, PM, kp)
        icon3d(c, 'sync', t * 2.5, W / 2 + 330, 1050, 90, TAP_INSTALL + 0.1, op=1 - prog(t, TOAST_T, TOAST_T + 0.2))
    # toast
    kt = prog(t, TOAST_T, TOAST_T + 0.45)
    if kt > 0:
        y = 1480 + 260 * (1 - e_out_back(kt, 1.6))
        neon_card(c, W / 2, y, 880, 300, r=44, op=min(1, kt * 3), glow_a=0.7, glow_c=GREEN)
        kc = prog(t, TOAST_T + 0.15, TOAST_T + 0.45)
        draw(c, check_spr(110, GREEN), W / 2, y - 70, scale=e_out_back(kc, 3.0))
        if 0 < kc < 1:
            draw(c, ring_sprite(300, 55 + 70 * kc, 5, GREEN, glow=10), W / 2, y - 70, opacity=1 - kc)
        ts = txt(c, 'Conversation requested', W / 2 - 28, y + 30, 42, INK, PX, min(1, kt * 2))
        draw(c, check_spr(44, GREEN), W / 2 - 28 + ts.shape[1] / 2 + 22, y + 30, opacity=min(1, kt * 2))
        txt(c, 'No immediate commitment.', W / 2, y + 88, 34, MUTEDC, PM, min(1, kt * 2))
        confetti(c, t, TOAST_T + 0.15, W / 2, y - 70)
    return c


CONF = None


def confetti(canvas, t, t0, x, y, n=26):
    global CONF
    if CONF is None:
        rng = np.random.default_rng(8)
        CONF = [(rng.uniform(-math.pi, 0), rng.uniform(300, 700), [MAGENTA, ORANGE_B, GREEN, GOLD, PINK][i % 5],
                 rng.uniform(8, 16), rng.uniform(0, 6)) for i in range(n)]
    lt = t - t0
    if lt < 0 or lt > 1.6:
        return
    for a, sp, col, sz, ph in CONF:
        e = 1 - math.exp(-lt * 4)
        px = x + math.cos(a) * sp * e
        py = y + math.sin(a) * sp * e * 0.8 + 500 * lt * lt * 0.5
        rr = rrect_spr(sz, sz * 0.5, 2, col)
        draw(canvas, rr, px, py, rot=(lt * 400 + ph * 60) % 360, opacity=1 - prog(lt, 1.0, 1.6))


@functools.lru_cache(maxsize=1)
def cta_base():
    """Ivory end card with warm light and soft-focus leaves (as in the storyboard)."""
    c = np.ones((H, W, 3), np.float32) * np.array(hexc('#FFF8EF')[:3], np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xs - W * 0.5) / 700) ** 2 + ((ys - H * 0.42) / 800) ** 2))[..., None]
    c = c * (1 - 0.15 * (1 - g)) + np.array(hexc('#FFE9D6')[:3], np.float32) * 0.15 * (1 - g)
    return c


def sc_cta(t):
    t0 = T['cta']
    c = cta_base().copy()
    # out-of-focus leaves drifting at the edges
    for (name, x, y, sz, bl, ph) in [('leaf_green', 90, 230, 330, 7, 0.0), ('leaf_green', 1010, 160, 280, 9, 1.0),
                                     ('leaf_green', 980, 1760, 360, 6, 2.0), ('leaf_green', 60, 1690, 300, 8, 3.0),
                                     ('leaf_orange', 1030, 1080, 160, 4, 4.0), ('leaf_magenta', 40, 980, 150, 4, 5.0)]:
        R.leaf(c, name, t + ph, x + 14 * math.sin(t * 0.7 + ph), y + 10 * math.cos(t * 0.6 + ph), sz, blur=bl, op=0.85)
    kl = prog(t, t0 + 0.05, t0 + 0.55)
    lg = fitted('logo', png('logo_full'), width=800)
    if kl > 0:
        draw(c, lg, W / 2, 720, scale=0.86 + 0.14 * e_out_back(kl, 1.8), opacity=min(1, kl * 2))
        if t0 + 0.6 < t < t0 + 1.5:
            p = (t - t0 - 0.6) / 0.8 * 1.6 - 0.3
            draw(c, sweep(lg, p, strength=0.5), W / 2, 720, opacity=0.6)
    title(c, 'Already fostering?', W / 2, 1060, 80, t, VO['cta'], color=INK, glow=None, fname=PK, shadow_op=0.0,
          depth=4, ext=hexc('#F3C6DE'))
    title(c, "Let's talk.", W / 2, 1170, 96, t, CTA_TALK - 0.08, color=MAGENTA, glow=None, fname=PK, shadow_op=0.0,
          depth=5, ext=hexc('#F9C9A8'), sweep_t=CTA_TALK + 0.5)
    for j, (label, icon) in enumerate([('0161 241 1332', 'phone'), ('organicfostering.co.uk', 'web')]):
        kk = prog(t, CTA_TALK + 0.45 + j * 0.15, CTA_TALK + 0.8 + j * 0.15)
        if kk <= 0:
            continue
        y = 1370 + j * 110
        ic = icon_disc(icon)
        ts = word_spr(label, PB, 44, INK)
        total = ic.shape[1] + 24 + ts.shape[1]
        x0 = W / 2 - total / 2
        draw(c, ic, x0 + ic.shape[1] / 2, y, scale=e_out_back(kk, 2.4), opacity=min(1, kk * 3))
        draw(c, ts, x0 + ic.shape[1] + 24 + ts.shape[1] / 2, y + 2, opacity=min(1, kk * 3))
    ko = prog(t, CTA_TALK + 0.9, CTA_TALK + 1.3)
    if ko > 0:
        p = pill('Rated Good by Ofsted · May 2025', PB, 28, pad_x=30, pad_y=14, fill=hexc('#3F8F0B'), border=None,
                 text_color=WHITE_, dot=GOLD)
        draw(c, p, W / 2, 1630, scale=e_out_back(ko, 2.2), opacity=min(1, ko * 3))
    return c


@functools.lru_cache(maxsize=4)
def icon_disc(kind):
    s = 240
    im = np.zeros((s, s), np.float32)
    cv2.circle(im, (s // 2, s // 2), s // 2 - 4, 1.0, -1, cv2.LINE_AA)
    disc = solid(im, MAGENTA)
    g = np.zeros((s, s), np.float32)
    if kind == 'phone':
        cv2.ellipse(g, (s // 2 + 6, s // 2 - 4), (52, 52), 120, 0, 120, 1.0, 26, cv2.LINE_AA)
        cv2.circle(g, (s // 2 - 30, s // 2 - 46), 20, 1.0, -1, cv2.LINE_AA)
        cv2.circle(g, (s // 2 + 46, s // 2 + 32), 20, 1.0, -1, cv2.LINE_AA)
    else:
        cv2.circle(g, (s // 2, s // 2), 64, 1.0, 12, cv2.LINE_AA)
        cv2.ellipse(g, (s // 2, s // 2), (28, 64), 0, 0, 360, 1.0, 10, cv2.LINE_AA)
        cv2.line(g, (s // 2 - 64, s // 2), (s // 2 + 64, s // 2), 1.0, 10, cv2.LINE_AA)
    spr = over_spr(disc, solid(g, WHITE_))
    return cv2.resize(spr, (78, 78), interpolation=cv2.INTER_AREA)


SCENES = [(T['hook'], T['lock'], sc_hook), (T['lock'], T['check'], sc_lock), (T['check'], T['notes'], sc_check),
          (T['notes'], T['care'], sc_notes), (T['care'], T['install'], sc_care), (T['install'], T['cta'], sc_install),
          (T['cta'], 99, sc_cta)]
TRANS = [(0.25, 'cut'), (0.5, 'cut'), (0.75, 'cut'), (T['lock'], 'flash'), (T['check'], 'zoom'), (T['notes'], 'whip'),
         (T['care'], 'flash'), (CARE_CUT, 'flash'), (T['install'], 'whip'), (T['cta'], 'flashw')]


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
            c = c + np.array((1.0, 0.75, 0.9), np.float32) * 0.8 * math.exp(-max(0, d) * 12)
        elif kind == 'flashw' and -0.1 < d < 0.35:
            c = c + 0.85 * math.exp(-abs(d) * 9)
    dx = dy = 0.0
    for tc in [T['tap'], TAP_INSTALL, CHK_T[-1], OFSTED_T, T['lock']]:
        sx, sy = shake(t, tc, amp=9, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c *= 1 - 0.85 * e_inout_cubic(prog(t, DUR - FADE, DUR))
    return c


def is_fast(t):
    if t < T['lock'] + 0.1:
        return True
    return any(abs(t - tc) < 0.2 for tc, _ in TRANS) or abs(t - T['tap']) < 0.2


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
    light = t >= T['cta']
    return post(c, fi, bloom=0.2 if light else (0.25 if T['care'] <= t < T['install'] else 0.5), grain=0.014, ca=1.5 if t < T['lock'] else 0.0,
                vig=0.35 if light else 1.0)


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
