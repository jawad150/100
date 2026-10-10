"""Bodyrade — three 9:16 SaaS/cinematic reels from one compositor.

  REEL=fresh   "Only mix it fresh"   (~28 s)  problem -> Mixology capsule 4 steps -> locked in fresh
  REEL=five    "5 in 1"              (~26 s)  dashboard breakdown of the five actives
  REEL=flavour "Pick your flavour"   (~24 s)  three flavour worlds with 3D fruit

Usage:
  REEL=fresh python3 reel_br.py still 1.0,5.0
  REEL=fresh python3 reel_br.py range 0 840
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('REEL_WORKDIR', os.path.abspath(os.path.join(HERE, '..', 'workspace_br')))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_of'))
import numpy as np
import cv2
import reel_of as R   # shared SaaS helpers: glass, kinetic_line, sweep, colorize, orb, whip, zoom_blur, ...
from reel_of import (glass, kinetic_line, type_line, word_spr, sweep, glow_add, shadow, scrim, whip, zoom_blur,
                     light_leak, shake, check_spr, rrect_spr)
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
REEL = os.environ.get('REEL', 'fresh')

# ------------------------------------------------------------------ brand
YEL = hexc('#FDCF09')
YEL2 = hexc('#FFB400')
BLK = hexc('#0D0D0F')
PANEL = hexc('#17171A')
OFFW = hexc('#F6F4EE')
WHT = (1.0, 1.0, 1.0, 1.0)
GREY = hexc('#9A9AA0')
FL = {'orange': (hexc('#FF6A13'), hexc('#FFB21A'), 'Orange & Mango'),
      'raspberry': (hexc('#D2143F'), hexc('#FF4F7A'), 'Sour Raspberry'),
      'pear': (hexc('#9BC53D'), hexc('#D8F05A'), 'Sweet Pear')}
H9 = 'Jost-900'
H8 = 'Jost-800'
H7 = 'Jost-700'
H6 = 'Jost-600'
H5 = 'Jost-500'
I9 = 'JostItalic-900'
BEAT = 0.5   # 120 BPM — cuts and hits land on the grid

SEQ = {}


def seq(name):
    if name not in SEQ:
        SEQ[name] = Seq(name, fps=24, loop=True)
    return SEQ[name]


@functools.lru_cache(maxsize=None)
def img(path, alpha=False):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if alpha:
        if im.shape[2] == 3:
            im = np.concatenate([im, np.full(im.shape[:2] + (1,), 255, np.uint8)], 2)
        return to_premul(im[..., [2, 1, 0, 3]])
    return im[..., :3][..., ::-1].astype(np.float32) / 255.0


def logo():
    return img(f'{S}/site/logo.png', True)


def step_icon(n):
    return img(f'{S}/site/step{n}.png', True)


def photo(name):
    return img(f'{S}/{name}')


# ------------------------------------------------------------------ backgrounds
_Y, _X = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)


def _blob(cx, cy, r):
    d = np.sqrt((_X - cx / 4) ** 2 + (_Y - cy / 4) ** 2) / (r / 4)
    return np.exp(-d * d)[..., None]


def bg_black(t, accent=YEL, beams=True, grid=True):
    base = vgrad(H // 4, W // 4, hexc('#151518'), hexc('#060607'))
    a = np.array(accent[:3], np.float32)
    base += a * _blob(540 + 120 * math.sin(t * 0.7), 760, 700) * 0.16
    base += a * _blob(200, 1700, 500) * 0.06
    if beams:
        # two diagonal light beams sweeping slowly (stage lighting)
        for k, (ang, off, wdt, st) in enumerate([(0.62, 0.0, 70, 0.18), (-0.55, 0.9, 50, 0.12)]):
            u = (_X * 4 * math.cos(ang) + _Y * 4 * math.sin(ang)) / 900 - (t * 0.12 + off) % 2.4 + 0.6
            beam = np.exp(-(u * 900 / wdt) ** 2)[..., None]
            base += a * beam * st
    out = cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)
    if grid:
        g = _grid(t)
        out += g[..., None] * np.array(accent[:3], np.float32) * 0.22
    return out


_gridc = {}


def _grid(t):
    """Perspective floor grid in the lower third, scrolling toward camera."""
    k = int((t * 30) % 30)
    if k in _gridc:
        return _gridc[k]
    g = np.zeros((H, W), np.float32)
    horizon = 1180
    ph = (t * 0.6) % 1.0
    for i in range(1, 22):
        z = (i - ph) / 3.0 + 0.2
        y = int(horizon + 520 / z)
        if horizon < y < H:
            cv2.line(g, (0, y), (W, y), 1.0 * min(1, (y - horizon) / 300), 2, cv2.LINE_AA)
    for xi in range(-12, 13):
        x_bot = W / 2 + xi * 260
        cv2.line(g, (int(W / 2 + xi * 18), horizon), (int(x_bot), H), 0.7, 2, cv2.LINE_AA)
    g[:horizon] = 0
    fade = np.clip((np.arange(H)[:, None] - horizon) / 500, 0, 1)
    g = cv2.GaussianBlur(g * fade, (0, 0), 1.0)
    if len(_gridc) > 40:
        _gridc.clear()
    _gridc[k] = g
    return g


def bg_yellow(t):
    base = vgrad(H // 4, W // 4, hexc('#FFE14A'), hexc('#FDB800'))
    base += _blob(780 + 80 * math.sin(t), 500, 600) * 0.25
    base = base * (1 - _blob(200, 1500, 700) * 0.12)
    out = cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)
    # faint giant chevron stripes
    ys, xs = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    v = (np.abs(xs * 4 - W / 2) + ys * 4 * 0.9 - t * 80) % 520
    stripe = ((v > 0) & (v < 140)).astype(np.float32)
    stripe = cv2.GaussianBlur(stripe, (0, 0), 1.0)
    out *= 1 - cv2.resize(stripe, (W, H))[..., None] * 0.07
    return np.clip(out, 0, 1.2)


def bg_flavour(t, fl):
    c1, c2, _ = FL[fl]
    base = vgrad(H // 4, W // 4, tuple(np.array(c2[:3]) * 1.0), tuple(np.array(c1[:3]) * 0.55))
    base += np.array(c2[:3], np.float32) * _blob(540, 800 + 60 * math.sin(t), 620) * 0.45
    base = base * (1 - _blob(540, 1900, 900) * 0.45)
    out = cv2.resize(base, (W, H), interpolation=cv2.INTER_CUBIC)
    return out


# ------------------------------------------------------------------ pieces
def pouch(canvas, fl, cx, cy, height, angle=0.0, op=1.0, blur=0.0, shadow_op=0.5):
    s = seq('pouch_' + fl)
    n = max(1, len(s.files))
    idx = int(round((angle % 360) / 360 * n)) % n
    f = s.frame(idx / 24.0, blur=blur)
    if f.shape[0] < 16:
        return
    sc = height / f.shape[0]
    if shadow_op > 0:
        sh = blur_sprite(tint(f, (0, 0, 0)), 30)
        draw(canvas, sh, cx + 20 * sc * 3, cy + height * 0.06, scale=sc * 1.02, opacity=shadow_op * op)
    draw(canvas, f, cx, cy, scale=sc, opacity=op)


def pouch_flat(canvas, fl, cx, cy, height, rot=0.0, op=1.0):
    spr = img(f'{S}/src/cut_{fl}.png', True)
    sc = height / spr.shape[0]
    sh = blur_sprite(tint(spr, (0, 0, 0)), 26)
    draw(canvas, sh, cx + 18, cy + 30, scale=sc, rot=rot, opacity=0.5 * op)
    draw(canvas, spr, cx, cy, scale=sc, rot=rot, opacity=op)


def seq_draw(canvas, name, t, x, y, size, op=1.0, blur=0.0, idx=None, rot=0.0):
    s = seq(name)
    f = s.frame(idx / 24.0 if idx is not None else t, blur=blur)
    if f.shape[0] < 16:
        return
    draw(canvas, f, x, y, scale=size / max(f.shape[:2]), opacity=op, rot=rot)


def title(canvas, text, cx, cy, size, t, t0, color=WHT, fname=H9, **kw):
    kw.setdefault('shadow_op', 0.6)
    kw.setdefault('stagger', 0.05)
    kinetic_line(canvas, text, cx, cy, size, t, t0, color=color, fname=fname, **kw)


def chip(canvas, text, cx, cy, t, t0, fill=YEL, color=BLK, size=36, dot=None, op=1.0):
    if t < t0:
        return
    k = prog(t, t0, t0 + 0.35)
    pl = pill(text, H7, size, pad_x=34, pad_y=18, fill=fill[:3] + (fill[3] if len(fill) > 3 else 1.0,),
              border=None, text_color=color, dot=dot)
    draw(canvas, pl, cx, cy + 24 * (1 - e_out_expo(k)), scale=0.85 + 0.15 * e_out_back(k, 2.0),
         opacity=min(1, k * 3) * op)


def counter_spr(value, decimals, unit, size, color):
    txt = f'{value:.{decimals}f}{unit}'
    return word_spr(txt, H9, size, color)


def photo_card(canvas, name, cx, cy, w, h, t, t0, zoom0=1.15, zoom1=1.0, r=34, op=1.0, rot=0.0, focus=(0.5, 0.5)):
    if t < t0 or op <= 0:
        return
    k = prog(t, t0, t0 + 0.55)
    e = e_out_expo(k)
    im = photo(name)
    z = zoom0 + (zoom1 - zoom0) * prog(t, t0, t0 + 3.0)
    ih, iw = im.shape[:2]
    asp = w / h
    if iw / ih > asp:
        ch_ = ih / z
        cw_ = ch_ * asp
    else:
        cw_ = iw / z
        ch_ = cw_ / asp
    crop = crop_resize(im, iw * focus[0], ih * focus[1], cw_, ch_, int(w), int(h))
    a = sdf_fill(rrect_alpha(int(w), int(h), r, 0))
    spr = rgb_to_sprite(crop.astype(np.float32), a)
    spr = over_spr(spr, solid(sdf_stroke(rrect_alpha(int(w), int(h), r, 0), 3), (1, 1, 1, 0.35)))
    sh = blur_sprite(solid(a, (0, 0, 0, 1)), 30)
    s = 0.9 + 0.1 * e
    draw(canvas, sh, cx, cy + 30 + 60 * (1 - e), scale=s, rot=rot, opacity=0.55 * e * op)
    draw(canvas, spr, cx, cy + 60 * (1 - e), scale=s, rot=rot, opacity=min(1, k * 2) * op)


def fullbleed_photo(name, t, t0, dur, z0=1.25, z1=1.1, pan=(0.5, 0.5), pan1=None, rot0=0.0):
    im = photo(name)
    ih, iw = im.shape[:2]
    k = prog(t, t0, t0 + dur)
    z = z0 + (z1 - z0) * k
    p = pan if pan1 is None else (pan[0] + (pan1[0] - pan[0]) * k, pan[1] + (pan1[1] - pan[1]) * k)
    ch_ = ih / z
    cw_ = ch_ * W / H
    out = crop_resize(im, iw * p[0], ih * p[1], cw_, ch_, W, H)
    if abs(rot0) > 0.01:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), rot0 * (1 - k), 1.0)
        out = cv2.warpAffine(out, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out.astype(np.float32)


class Fruits:
    """3D fruit pieces flying through depth around the pack (parallax + depth of field)."""

    def __init__(self, names, n=14, seed=1):
        rng = np.random.default_rng(seed)
        self.items = []
        for i in range(n):
            self.items.append(dict(name=names[i % len(names)], x=rng.uniform(-620, 620), y=rng.uniform(-1050, 1050),
                                   z=rng.uniform(-500, 900), vy=rng.uniform(-120, -40), ph=rng.uniform(0, 3),
                                   spin=rng.uniform(0.6, 1.4), size=rng.uniform(230, 330)))

    def draw(self, canvas, t, t0, layer='all', burst=0.0, focus_z=0.0, op=1.0):
        lt = t - t0
        for it in sorted(self.items, key=lambda d: -d['z']):
            z = it['z'] - lt * 260          # dolly toward camera
            if layer == 'back' and z < 150:
                continue
            if layer == 'front' and z >= 150:
                continue
            s = FOCAL / (FOCAL + z)
            if s <= 0.05 or z < -1300:
                continue
            bx = it['x'] * (1 + burst * 0.6)
            by = it['y'] + it['vy'] * lt
            x = CX + bx * s
            y = CY + by * s
            blur = min(14, abs(z - focus_z) / 70)
            seq_draw(canvas, it['name'], t * it['spin'] + it['ph'], x, y, it['size'] * s, op=op, blur=blur)


def stepper(canvas, cx, cy, n_steps, active, k, accent=YEL):
    """SaaS onboarding progress: numbered dots joined by a filling bar."""
    gap = 170
    x0 = cx - gap * (n_steps - 1) / 2
    line = solid(np.ones((6, int(gap * (n_steps - 1))), np.float32), (1, 1, 1, 0.18))
    composite(canvas, line, int(x0), int(cy - 3))
    fill_w = int(gap * max(0, (active - 1) + k))
    if fill_w > 2:
        composite(canvas, solid(np.ones((6, fill_w), np.float32), accent), int(x0), int(cy - 3))
    for i in range(n_steps):
        x = x0 + i * gap
        on = i + 1 <= active
        cur = i + 1 == active
        d = rrect_alpha(64, 64, 32, 2)
        fillc = accent if on else (0.12, 0.12, 0.13, 1.0)
        spr = over_spr(solid(sdf_fill(d), fillc), solid(sdf_stroke(d, 2.5), (1, 1, 1, 0.3)))
        sc = 1.0 + (0.18 * math.sin(k * math.pi) if cur else 0)
        if cur:
            draw(canvas, radial_sprite(180, accent, 2.0), x, cy, opacity=0.5, mode='add')
        draw(canvas, spr, x, cy, scale=sc)
        num = word_spr(f'{i + 1}', H8, 34, BLK if on else GREY)
        draw(canvas, num, x, cy - 1, scale=sc)


def flash(canvas, t, t0, dur=0.18, amt=0.9, color=(1, 1, 1)):
    k = prog(t, t0, t0 + dur)
    if 0 < k < 1:
        canvas += np.array(color, np.float32) * amt * (1 - k) ** 2


def end_card(canvas, t, t0, line1, line2=None, accent=YEL):
    k = prog(t, t0, t0 + 0.6)
    e = e_out_expo(k)
    lg = logo()
    sc = 760 / lg.shape[1] * (0.92 + 0.08 * e)
    glow_add(canvas, lg, W / 2, 760, accent, sigma=30, strength=0.5 * k, scale=sc)
    draw(canvas, lg, W / 2, 760 + 40 * (1 - e), scale=sc, opacity=min(1, k * 2))
    title(canvas, line1, W / 2, 1010, 92, t, t0 + 0.35, color=WHT, glow=accent, glow_str=0.5,
          sweep_t=t0 + 0.9)
    if line2:
        title(canvas, line2, W / 2, 1105, 44, t, t0 + 0.6, color=GREY, fname=H6, shadow_op=0.0)
    chip(canvas, 'Register your interest at bodyrade.com', W / 2, 1260, t, t0 + 0.9, fill=YEL, color=BLK, size=34)
    k2 = prog(t, t0 + 1.1, t0 + 1.5)
    if k2 > 0:
        fp = word_spr('Developed in Sweden  ·  Made in the UK', H5, 30, GREY)
        draw(canvas, fp, W / 2, 1360, opacity=k2)


# ================================================================== REEL 1: ONLY MIX IT FRESH
F1 = dict(hook=0.0, problem=2.0, turn=7.0, steps=9.0, benefits=21.0, end=25.0, dur=28.5)
HOOK_PHOTOS = ['site/pre_workout.jpg', 'src/gym_rack.png', 'site/supplements.jpg', 'site/flat_lay.png',
               'site/water_fill.jpg', 'site/funnel.jpg', 'site/gift_box.jpg', 'site/pre_workout.jpg']


def r1_hook(t):
    i = min(int(t / 0.25), len(HOOK_PHOTOS) - 1)
    lt = t - i * 0.25
    c = fullbleed_photo(HOOK_PHOTOS[i], lt, 0, 0.25, z0=1.45, z1=1.25, pan=(0.35 + 0.3 * (i % 2), 0.5),
                        rot0=(-1) ** i * 3)
    c = c * 0.55
    flash(c, lt, 0.0, 0.08, 0.5)
    scrim(c, top=0.0, bottom=0.0)
    title(c, 'STOP', W / 2, 760, 210, t, 0.05, color=YEL, fname=I9, glow=YEL, glow_str=0.6, shadow_op=0.8,
          rise=80)
    title(c, 'PRE-MIXING.', W / 2, 960, 150, t, 0.4, color=WHT, fname=I9, glow=YEL, glow_str=0.35, shadow_op=0.8,
          sweep_t=1.1, rise=80)
    chip(c, "Here's why", W / 2, 1150, t, 1.0, fill=(1, 1, 1, 0.95), color=BLK, size=40)
    return c


def r1_problem(t):
    t0 = F1['problem']
    c = bg_black(t)
    lt = t - t0
    title(c, 'Your shaker is', W / 2, 330, 84, t, t0 + 0.05, fname=H8)
    title(c, 'working against you.', W / 2, 430, 84, t, t0 + 0.35, fname=H8, color=YEL, glow=YEL, glow_str=0.35)
    # dashboard card: freshness line dropping (qualitative)
    k = prog(t, t0 + 0.6, t0 + 1.1)
    if k > 0:
        cw, ch = 900, 560
        cy_ = 900
        glass(c, W / 2, cy_ + 60 * (1 - e_out_expo(k)), cw, ch, r=40, tint_c=(0.1, 0.1, 0.11), tint_a=0.6,
              opacity=min(1, k * 2), blur=24)
        hdr = word_spr('Ingredient freshness  ·  pre-mixed', H6, 34, GREY)
        draw(c, hdr, W / 2 - cw / 2 + 40 + hdr.shape[1] / 2, cy_ - ch / 2 + 60, opacity=k)
        live = word_spr('LIVE', H8, 26, hexc('#FF4D4D'))
        draw(c, live, W / 2 + cw / 2 - 70, cy_ - ch / 2 + 60, opacity=k * (0.6 + 0.4 * math.sin(t * 8)))
        # axes
        x0, x1 = W / 2 - cw / 2 + 70, W / 2 + cw / 2 - 60
        y0, y1 = cy_ - ch / 2 + 120, cy_ + ch / 2 - 90
        axis = np.zeros((H, W), np.float32)
        cv2.line(axis, (int(x0), int(y1)), (int(x1), int(y1)), 0.35, 2, cv2.LINE_AA)
        cv2.line(axis, (int(x0), int(y0)), (int(x0), int(y1)), 0.35, 2, cv2.LINE_AA)
        c += axis[..., None] * 0.6 * k
        kd = prog(t, t0 + 1.0, t0 + 3.2)
        npts = 60
        pts = []
        for j in range(int(npts * kd) + 1):
            u = j / npts
            yv = 1 - 0.78 * (1 - math.exp(-u * 2.6)) - 0.04 * math.sin(u * 30) * u
            pts.append((x0 + u * (x1 - x0), y1 - (y1 - y0) * yv))
        if len(pts) > 1:
            ln = np.zeros((H, W), np.float32)
            cv2.polylines(ln, [np.int32(pts)], False, 1.0, 6, cv2.LINE_AA)
            glow = cv2.GaussianBlur(ln, (0, 0), 10)
            col = np.array([1.0, 0.3, 0.25], np.float32)
            c += ln[..., None] * col * 0.95 + glow[..., None] * col * 0.9
            hx, hy = pts[-1]
            draw(c, radial_sprite(90, (1, 0.35, 0.3), 2.0, core=0.8), hx, hy, mode='add')
        for j, (lab, tt) in enumerate([('Air', 1.3), ('Moisture', 2.0), ('Light', 2.6)]):
            u = [0.18, 0.45, 0.75][j]
            if lt > tt:
                kk = prog(lt, tt, tt + 0.3)
                pl = pill(lab, H6, 28, pad_x=22, pad_y=12, fill=(0.2, 0.2, 0.22, 0.95), border=(1, 1, 1, 0.2),
                          text_color=WHT, dot=hexc('#FF4D4D'))
                draw(c, pl, x0 + u * (x1 - x0), y0 + 40 + j * 10, scale=e_out_back(kk, 2), opacity=min(1, kk * 3))
    # consequences (from bodyrade.com)
    for j, (lab, tt) in enumerate([('Clumping', 3.4), ('Lost potency', 3.8), ('Wasted product', 4.2)]):
        if lt > tt:
            kk = prog(lt, tt, tt + 0.35)
            y = 1290 + j * 105
            glass(c, W / 2, y, 640 * e_out_expo(kk) + 10, 84, r=42, tint_c=(0.25, 0.04, 0.04), tint_a=0.55,
                  opacity=min(1, kk * 3), blur=18)
            x_ = solid(sdf_fill(rrect_alpha(44, 44, 22, 2)), hexc('#FF4D4D'))
            draw(c, x_, W / 2 - 270, y, opacity=kk)
            xs = word_spr('×', H8, 40, WHT)
            draw(c, xs, W / 2 - 270, y - 3, opacity=kk)
            ls = word_spr(lab, H7, 44, WHT)
            draw(c, ls, W / 2 - 220 + ls.shape[1] / 2, y, opacity=min(1, kk * 2))
    ks = prog(t, t0 + 4.4, t0 + 4.8)
    if ks > 0:
        src = word_spr('Creatine absorbs moisture from the air.', H6, 38, OFFW)
        draw(c, src, W / 2, 1640, opacity=ks)
    return c


def r1_turn(t):
    t0 = F1['turn']
    c = bg_yellow(t)
    lt = t - t0
    seq_draw(c, 'chevron', t, W / 2, 560, 420, idx=min(47, int(lt * 30)))
    title(c, 'ONLY MIX', W / 2, 900, 170, t, t0 + 0.15, color=BLK, fname=I9, shadow_op=0.0, rise=90)
    title(c, 'IT FRESH.', W / 2, 1080, 170, t, t0 + 0.45, color=BLK, fname=I9, shadow_op=0.0, rise=90,
          sweep_t=t0 + 1.0)
    chip(c, 'The Bodyrade Mixology Bottle', W / 2, 1280, t, t0 + 0.9, fill=BLK, color=YEL, size=38)
    return c


STEPS = [('Load the capsule', 'Pour or scoop straight into the capsule.', 'site/funnel.jpg', (0.45, 0.45)),
         ('Insert the capsule', 'Tighten it onto the bottle neck.', None, None),
         ('Add cold water', 'Fill with ice-cold water to the line.', 'site/water_fill.jpg', (0.55, 0.5)),
         ('Open & shake', 'Release, shake, drink it fresh.', None, None)]


def r1_steps(t):
    t0 = F1['steps']
    c = bg_black(t, grid=False)
    i = min(int((t - t0) / 3.0), 3)
    st = t0 + i * 3.0
    lt = t - st
    name, sub, ph, focus = STEPS[i]
    # header + stepper
    hdr = word_spr('HOW IT WORKS', H8, 34, YEL)
    draw(c, hdr, W / 2, 230)
    stepper(c, W / 2, 330, 4, i + 1, prog(lt, 0, 0.6))
    # big step number with outline glow
    num = word_spr(f'0{i + 1}', H9, 300, (1, 1, 1, 0.08))
    draw(c, num, W / 2 + 260, 640 + 30 * (1 - e_out_expo(prog(lt, 0, 0.5))))
    # visual
    if ph:
        photo_card(c, ph, W / 2, 850, 720, 760, t, st + 0.05, zoom0=1.25, zoom1=1.05, focus=focus)
        ic = step_icon(i + 1)
        glass(c, W / 2 + 270, 1140, 230, 230, r=115, tint_c=(0.05, 0.05, 0.06), tint_a=0.7,
              opacity=min(1, prog(lt, 0.3, 0.6) * 2), blur=16)
        draw(c, tint(ic, YEL), W / 2 + 270, 1140, scale=180 / ic.shape[1] * e_out_back(prog(lt, 0.3, 0.7), 2))
    else:
        ic = step_icon(i + 1)
        k = prog(lt, 0.05, 0.5)
        glass(c, W / 2, 850, 720, 760, r=40, tint_c=(0.1, 0.1, 0.11), tint_a=0.55, opacity=min(1, k * 2), blur=24)
        wob = math.sin(lt * 18) * 6 * (1 - prog(lt, 1.2, 2.4)) if i == 3 else 0
        draw(c, glow_of(tint(ic, YEL), 14, strength=0.6), W / 2, 850, scale=600 / ic.shape[1] * e_out_expo(k),
             mode='add', rot=wob)
        draw(c, tint(ic, WHT), W / 2, 850, scale=600 / ic.shape[1] * e_out_expo(k), opacity=min(1, k * 2), rot=wob)
        if i == 3:
            for j in range(3):
                seq_draw(c, 'ice_cube', t + j, W / 2 + (-260 + j * 260), 1180 - 60 * math.sin(lt * 2 + j), 170,
                         op=min(1, prog(lt, 0.4 + 0.15 * j, 0.8 + 0.15 * j) * 2))
    title(c, name, W / 2, 1360, 96, t, st + 0.2, fname=H9, color=WHT, glow=YEL, glow_str=0.3)
    title(c, sub, W / 2, 1460, 40, t, st + 0.45, fname=H5, color=GREY, shadow_op=0.0, stagger=0.02)
    return c


BENEFITS = ['Airtight compartments', 'No clumping, no potency loss', 'Mix it only when you’re ready to lift']


def r1_benefits(t):
    t0 = F1['benefits']
    c = bg_black(t, accent=FL['orange'][0])
    lt = t - t0
    ang = 330 + lt * 55
    pouch(c, 'orange', W / 2, 880, 1000 * (0.9 + 0.1 * e_out_expo(prog(lt, 0, 0.6))), angle=ang)
    title(c, 'Fresh every time.', W / 2, 300, 96, t, t0 + 0.1, fname=H9, color=YEL, glow=YEL, glow_str=0.4,
          sweep_t=t0 + 0.8)
    for j, b in enumerate(BENEFITS):
        tt = t0 + 0.6 + j * 0.55
        if t < tt:
            continue
        kk = prog(t, tt, tt + 0.4)
        y = 1420 + j * 112
        ts = word_spr(b, H7, 42, WHT)
        w = ts.shape[1] + 130
        glass(c, W / 2, y, w * (0.6 + 0.4 * e_out_expo(kk)), 92, r=46, tint_c=(0.08, 0.08, 0.09), tint_a=0.7,
              opacity=min(1, kk * 3), blur=18)
        draw(c, check_spr(48, YEL), W / 2 - w / 2 + 52, y, scale=e_out_back(kk, 2.5))
        draw(c, ts, W / 2 - w / 2 + 96 + ts.shape[1] / 2, y, opacity=min(1, kk * 2))
    return c


def r1_end(t):
    t0 = F1['end']
    c = bg_black(t)
    end_card(c, t, t0, 'LOCKED IN FRESH.', 'Blood flow · Energy · Strength · Endurance · Recovery')
    return c


SC1 = [(F1['hook'], F1['problem'], r1_hook), (F1['problem'], F1['turn'], r1_problem), (F1['turn'], F1['steps'], r1_turn),
       (F1['steps'], F1['benefits'], r1_steps), (F1['benefits'], F1['end'], r1_benefits), (F1['end'], 99, r1_end)]
TR1 = [(F1['problem'], 'flash'), (F1['turn'], 'whip'), (F1['steps'], 'zoom'), (F1['steps'] + 3, 'whip'),
       (F1['steps'] + 6, 'whip'), (F1['steps'] + 9, 'whip'), (F1['benefits'], 'zoom'), (F1['end'], 'flash')]

# ================================================================== REEL 2: 5 IN 1
F2 = dict(hook=0.0, serving=2.5, actives=5.0, total=20.0, end=23.0, dur=26.5)
ACTIVES = [('Creatine', 5.0, 1, 'g'), ('Citrulline Malate', 2.5, 1, 'g'), ('Beta-Alanine', 1.5, 1, 'g'),
           ('Caffeine', 200, 0, 'mg'), ('L-Theanine', 200, 0, 'mg')]
ACT_G = [5.0, 2.5, 1.5, 0.2, 0.2]
ACT_COL = [YEL, hexc('#FF6A13'), hexc('#D2143F'), hexc('#9BC53D'), hexc('#7FD3FF')]


def r2_hook(t):
    c = bg_black(t)
    # rapid flicker of the three pouches behind
    fl = ['orange', 'raspberry', 'pear'][int(t / 0.25) % 3]
    if t < 1.5:
        pouch(c, fl, W / 2, 1150, 820, angle=(t * 400) % 360, op=0.35, blur=4, shadow_op=0)
    k = prog(t, 0.1, 0.1 + 40 / 30)
    idx = min(39, int((t - 0.1) * 30)) if t > 0.1 else 0
    f = seq('text_5in1').frame(idx / 24.0)
    if f.shape[0] > 16 and t > 0.1:
        sc = 920 / f.shape[1]
        glow_add(c, f, W / 2, 760, YEL, sigma=40, strength=0.5, scale=sc)
        draw(c, f, W / 2, 760, scale=sc * (1.3 - 0.3 * e_out_expo(prog(t, 0.1, 0.7))))
    title(c, 'WHAT’S IN', W / 2, 1060, 110, t, 0.7, fname=I9, color=WHT, glow=YEL, glow_str=0.3, rise=70)
    title(c, 'ONE SCOOP?', W / 2, 1190, 110, t, 1.0, fname=I9, color=YEL, glow=YEL, glow_str=0.5, rise=70,
          sweep_t=1.6)
    return c


def gauge(canvas, cx, cy, r, k, color, label, sub):
    g = np.zeros((int(r * 2 + 60), int(r * 2 + 60)), np.float32)
    ctr = (g.shape[1] // 2, g.shape[0] // 2)
    cv2.ellipse(g, ctr, (int(r), int(r)), 0, 0, 360, 0.18, 22, cv2.LINE_AA)
    track = solid(g, (1, 1, 1, 1))
    draw(canvas, track, cx, cy)
    g2 = np.zeros_like(g)
    cv2.ellipse(g2, ctr, (int(r), int(r)), -90, 0, 360 * k, 1.0, 22, cv2.LINE_AA)
    arc = solid(g2, color)
    draw(canvas, blur_sprite(arc, 12), cx, cy, mode='add', opacity=0.8)
    draw(canvas, arc, cx, cy)
    num = word_spr(label, H9, 150, WHT)
    draw(canvas, num, cx, cy - 10)
    s2 = word_spr(sub, H6, 36, GREY)
    draw(canvas, s2, cx, cy + 95)


def r2_serving(t):
    t0 = F2['serving']
    c = bg_black(t, accent=FL['raspberry'][0])
    lt = t - t0
    pouch(c, 'raspberry', W / 2 + 230, 1180, 900, angle=340 + lt * 25, op=min(1, prog(lt, 0, 0.4) * 2))
    k = e_out_cubic(prog(lt, 0.2, 1.6))
    gauge(c, W / 2 - 170, 760, 230, k, YEL, f'{10 * k:.0f}g', 'per serving')
    title(c, 'One 10g serving.', W / 2, 330, 84, t, t0 + 0.1, fname=H9)
    title(c, 'Five actives.', W / 2, 430, 84, t, t0 + 0.4, fname=H9, color=YEL, glow=YEL, glow_str=0.35)
    return c


def r2_actives(t):
    t0 = F2['actives']
    c = bg_black(t)
    i = min(int((t - t0) / 3.0), 4)
    st = t0 + i * 3.0
    lt = t - st
    name, val, dec, unit = ACTIVES[i]
    col = ACT_COL[i]
    # big counter
    pouch(c, ['raspberry', 'orange', 'pear', 'raspberry', 'orange'][i], W / 2, 1830, 760,
          angle=330 + (t - t0) * 30, op=0.95, shadow_op=0.3)
    kv = e_out_cubic(prog(lt, 0.05, 0.9))
    cs = counter_spr(val * kv, dec, unit, 300 if unit == 'g' else 250, WHT)
    glow_add(c, cs, W / 2, 640, col, sigma=36, strength=0.55)
    draw(c, cs, W / 2, 640 + 40 * (1 - e_out_expo(prog(lt, 0, 0.4))), opacity=min(1, prog(lt, 0, 0.2) * 3))
    title(c, name, W / 2, 870, 96, t, st + 0.25, fname=H9, color=col, glow=col, glow_str=0.35, sweep_t=st + 0.9)
    chip(c, f'Active {i + 1} of 5', W / 2, 410, t, st + 0.05, fill=(1, 1, 1, 0.1), color=WHT, size=32, dot=col)
    # stacked serving bar (dashboard)
    bx0, bw, by = 110, W - 220, 1240
    glass(c, W / 2, by + 60, bw + 60, 330, r=36, tint_c=(0.1, 0.1, 0.11), tint_a=0.6, blur=22)
    lab = word_spr('10g serving', H6, 32, GREY)
    draw(c, lab, bx0 + lab.shape[1] / 2, by - 40)
    tot_done = sum(ACT_G[:i]) + ACT_G[i] * e_out_cubic(prog(lt, 0.2, 1.2))
    tv = word_spr(f'{tot_done:.1f}g actives', H7, 32, WHT)
    draw(c, tv, bx0 + bw - tv.shape[1] / 2, by - 40)
    composite(c, solid(sdf_fill(rrect_alpha(int(bw), 56, 28, 0)), (1, 1, 1, 0.08)), int(bx0), int(by))
    x = bx0
    for j in range(i + 1):
        seg = bw * ACT_G[j] / 10.0
        kk = 1.0 if j < i else e_out_cubic(prog(lt, 0.2, 1.2))
        wseg = max(4, int(seg * kk))
        composite(c, solid(np.ones((56, wseg), np.float32), ACT_COL[j]), int(x), int(by))
        x += seg
    # legend chips
    for j in range(i + 1):
        lx = bx0 + 20 + (j % 3) * 300
        ly = by + 130 + (j // 3) * 70
        dotc = solid(sdf_fill(rrect_alpha(22, 22, 11, 2)), ACT_COL[j])
        draw(c, dotc, lx + 11, ly)
        nm = word_spr(ACTIVES[j][0], H6, 30, WHT if j == i else GREY)
        draw(c, nm, lx + 34 + nm.shape[1] / 2, ly)
    return c


def r2_total(t):
    t0 = F2['total']
    c = bg_black(t, accent=FL['orange'][0])
    lt = t - t0
    for j, fl in enumerate(['raspberry', 'orange', 'pear']):
        kk = e_out_expo(prog(lt, 0.05 + 0.1 * j, 0.6 + 0.1 * j))
        x = W / 2 + (j - 1) * 330 * kk
        h = 760 if j == 1 else 640
        pouch(c, fl, x, 1050 + (0 if j == 1 else 40), h, angle=(j - 1) * -20 + 360, op=min(1, kk * 2))
    title(c, '9.4g of actives', W / 2, 330, 96, t, t0 + 0.1, fname=H9, color=YEL, glow=YEL, glow_str=0.4,
          sweep_t=t0 + 0.8)
    title(c, 'in every 10g scoop.', W / 2, 440, 72, t, t0 + 0.4, fname=H8)
    chip(c, 'Same formula · three flavours', W / 2, 1560, t, t0 + 0.8, fill=YEL, color=BLK, size=36)
    return c


def r2_end(t):
    c = bg_black(t)
    end_card(c, t, F2['end'], '5 IN 1 BLEND.', 'Blood flow · Energy · Strength · Endurance · Recovery')
    return c


SC2 = [(F2['hook'], F2['serving'], r2_hook), (F2['serving'], F2['actives'], r2_serving),
       (F2['actives'], F2['total'], r2_actives), (F2['total'], F2['end'], r2_total), (F2['end'], 99, r2_end)]
TR2 = [(F2['serving'], 'flash'), (F2['actives'], 'zoom')] + [(F2['actives'] + 3 * k, 'whip') for k in range(1, 5)] + \
      [(F2['total'], 'zoom'), (F2['end'], 'flash')]

# ================================================================== REEL 3: PICK YOUR FLAVOUR
F3 = dict(hook=0.0, orange=2.5, raspberry=8.5, pear=14.5, trio=20.5, dur=25.0)
FRUITS = {'orange': ['orange_slice', 'mango_cube'], 'raspberry': ['raspberry'], 'pear': ['pear_cube']}
TASTE = {'orange': 'Juicy orange. Ripe mango.', 'raspberry': 'Sharp, sour raspberry.', 'pear': 'Crisp, sweet pear.'}
FRUIT_SYS = {k: Fruits(v + ['ice_cube'] if k != 'raspberry' else v + ['raspberry', 'ice_cube'], n=14, seed=i + 3)
             for i, (k, v) in enumerate(FRUITS.items())}


def r3_hook(t):
    order = ['orange', 'raspberry', 'pear']
    i = int(t / 0.25)
    fl = order[i % 3]
    lt = t - i * 0.25
    c = bg_flavour(t, fl)
    pouch(c, fl, W / 2, 1050, 1000 * (1.1 - 0.1 * e_out_expo(lt / 0.25)), angle=(i * 47) % 360)
    flash(c, lt, 0, 0.08, 0.35)
    k = prog(t, 1.4, 2.5)
    title(c, 'THREE FLAVOURS.', W / 2, 330, 110, t, 0.05, fname=I9, color=WHT, shadow_op=0.8, rise=70)
    title(c, 'WHICH ONE ARE YOU?', W / 2, 460, 72, t, 0.6, fname=I9, color=BLK if fl == 'pear' else YEL,
          shadow_op=0.0 if fl == 'pear' else 0.7, rise=50)
    return c


def r3_flavour(t, fl, t0, num):
    c = bg_flavour(t, fl)
    c1, c2, nice = FL[fl]
    lt = t - t0
    fs = FRUIT_SYS[fl]
    fs.draw(c, t, t0 - 1.0, layer='back', focus_z=0)
    k = e_out_expo(prog(lt, 0.0, 0.7))
    ang = 300 + lt * 70
    pouch(c, fl, W / 2, 1060 + 120 * (1 - k), 1080 * (0.85 + 0.15 * k), angle=ang, op=min(1, k * 2), shadow_op=0.45)
    fs.draw(c, t, t0 - 1.0, layer='front', focus_z=0)
    dark = fl == 'pear'
    tc = BLK if dark else WHT
    chip(c, f'0{num} / 03', W / 2, 210, t, t0 + 0.1, fill=(0, 0, 0, 0.8) if not dark else (0, 0, 0, 0.85), color=WHT,
         size=32, dot=c2)
    words = nice.upper().split(' ')
    title(c, words[0], W / 2, 330, 130, t, t0 + 0.15, fname=I9, color=tc, shadow_op=0.0 if dark else 0.7, rise=80)
    title(c, ' '.join(words[1:]), W / 2, 470, 130, t, t0 + 0.4, fname=I9, color=YEL if not dark else BLK,
          glow=YEL if not dark else None, glow_str=0.4, shadow_op=0.0 if dark else 0.7, rise=80, sweep_t=t0 + 1.1)
    chip(c, TASTE[fl], W / 2, 1720, t, t0 + 0.9, fill=(0, 0, 0, 0.75), color=WHT, size=38)
    return c


def r3_orange(t):
    return r3_flavour(t, 'orange', F3['orange'], 1)


def r3_raspberry(t):
    return r3_flavour(t, 'raspberry', F3['raspberry'], 2)


def r3_pear(t):
    return r3_flavour(t, 'pear', F3['pear'], 3)


def r3_trio(t):
    t0 = F3['trio']
    c = bg_yellow(t)
    lt = t - t0
    for j, fl in enumerate(['raspberry', 'pear', 'orange']):
        kk = e_out_back(prog(lt, 0.05 + 0.08 * j, 0.6 + 0.08 * j), 1.6)
        x = W / 2 + [-310, 310, 0][j] * kk
        h = [600, 600, 720][j]
        rot = [-8, 8, 0][j] * kk
        pouch_flat(c, fl, x, 1080 + [40, 40, 0][j], h, rot=rot, op=min(1, kk * 2))
    title(c, 'PICK YOUR', W / 2, 330, 130, t, t0 + 0.15, fname=I9, color=BLK, shadow_op=0.0, rise=80)
    title(c, 'FLAVOUR.', W / 2, 470, 130, t, t0 + 0.4, fname=I9, color=BLK, shadow_op=0.0, rise=80,
          sweep_t=t0 + 1.0)
    kl = prog(lt, 1.0, 1.5)
    if kl > 0:
        lg = logo()
        dark_bg = solid(sdf_fill(rrect_alpha(560, 150, 75, 2)), (0.05, 0.05, 0.06, 1))
        draw(c, dark_bg, W / 2, 1560, scale=0.9 + 0.1 * e_out_back(kl), opacity=min(1, kl * 2))
        draw(c, lg, W / 2, 1560, scale=460 / lg.shape[1] * (0.9 + 0.1 * e_out_back(kl)), opacity=min(1, kl * 2))
    chip(c, 'Same 5 in 1 formula · bodyrade.com', W / 2, 1700, t, t0 + 1.4, fill=BLK, color=YEL, size=34)
    return c


SC3 = [(F3['hook'], F3['orange'], r3_hook), (F3['orange'], F3['raspberry'], r3_orange),
       (F3['raspberry'], F3['pear'], r3_raspberry), (F3['pear'], F3['trio'], r3_pear), (F3['trio'], 99, r3_trio)]
TR3 = [(F3['orange'], 'wipe'), (F3['raspberry'], 'wipe'), (F3['pear'], 'wipe'), (F3['trio'], 'flash')]

REELS = {'fresh': (SC1, TR1, F1['dur']), 'five': (SC2, TR2, F2['dur']), 'flavour': (SC3, TR3, F3['dur'])}
SCENES, TRANS, DUR = REELS[REEL]
NF = int(DUR * FPS)


def scene_at(t):
    for a, b, f in SCENES:
        if a <= t < b:
            return f, a
    return SCENES[-1][2], SCENES[-1][0]


def render_raw(t):
    f, a = scene_at(t)
    c = f(t)
    for tc, kind in TRANS:
        d = t - tc
        if kind == 'whip' and -0.15 < d < 0.15:
            c = whip(c, 1 - abs(d) / 0.15, -1 if d < 0 else -1)
        elif kind == 'zoom' and -0.12 < d < 0.12:
            c = zoom_blur(c, (1 - abs(d) / 0.12) * 4)
        elif kind == 'flash' and -0.05 < d < 0.25:
            flash(c, t, tc - 0.05, 0.3, 0.9)
        elif kind == 'wipe' and 0 <= d < 0.35:
            # previous scene shrinks behind an expanding circle of the new world
            prev_f, _ = scene_at(tc - 0.01)
            old = prev_f(tc - 0.01 + d * 0.3)
            r = e_inout_cubic(d / 0.35) * 1300
            m = np.zeros((H, W), np.float32)
            cv2.circle(m, (W // 2, H // 2), int(r), 1.0, -1, cv2.LINE_AA)
            m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
            ring = np.zeros((H, W), np.float32)
            cv2.circle(ring, (W // 2, H // 2), int(r), 1.0, 14, cv2.LINE_AA)
            c = old * (1 - m) + c * m + cv2.GaussianBlur(ring, (0, 0), 8)[..., None] * np.array(YEL[:3], np.float32) * 0.9
    # beat-synced camera punch on scene starts
    dx = dy = 0.0
    for tc, _ in TRANS:
        sx, sy = shake(t, tc, amp=12, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - 0.4:
        c *= 1 - 0.9 * prog(t, DUR - 0.4, DUR)
    return c


def is_fast(t):
    if t < 2.5:
        return True
    return any(abs(t - tc) < 0.25 for tc, _ in TRANS)


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
    return post(c, fi, bloom=0.5, grain=0.016, ca=2.0 if t < 2.0 else 0.0)


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        os.makedirs(f'{S}/stills_{REEL}', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            cv2.imwrite(f'{S}/stills_{REEL}/s_{t:05.2f}.jpg', to_u8(render(int(round(t * FPS)))),
                        [cv2.IMWRITE_JPEG_QUALITY, 90])
            print('still', t, flush=True)
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f'{S}/frames_{REEL}', exist_ok=True)
        for fi in range(a, b):
            cv2.imwrite(f'{S}/frames_{REEL}/{fi:04d}.png', to_u8(render(fi)), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            print('frame', fi, flush=True)
