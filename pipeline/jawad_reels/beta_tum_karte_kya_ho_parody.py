"""beta_tum_karte_kya_ho_parody.py - the wrong-genre parodies of C02 inside the big translate window
(110, 590)-(970, 1160), centre (540, 875) (BRIEF r2 6.4 P1 / P2 / S4 stamp; HANDOFF r3 #4: the cartoon pop is f215).

    wedding(cv, t, xf)       P1 f147-f189: PLUM radial ground + AMBER glitter, "Happy Wedding" (Cinzel 700, 'gold',
                             96 px) wiped in f153-f165 and out f180-f189, sparkle burst at the spark landing (f159)
    cartoon(cv, t, xf, t0)   P2 from t0 (= 215/30): EMBER + FLAME halftone ground, the output pill with "Cartoon?",
                             MOTION (Bungee 180 px, IVORY + NIGHT_0 stroke + FLAME shadow) rubber-hose wobble
    stamp(cv, t, xf)         S4 from 8.4: PHONE PE LAGE / REHTE HO. RED x1.25, distressed, double border, -7 deg, SLAM

Parody fonts (OFL 1.1, never brand type): <WS>/fonts/c02_parody_wedding.ttf = Cinzel 700, c02_parody_cartoon.ttf =
Bungee Regular; ensure_fonts() restores them from the animation-studio plugin copies when the workspace lost them.
"""
import functools
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import jawad_kit                                  # noqa: F401,E402  FIRST
from jawad_kit import K, T                        # noqa: E402
import jawad_tx as X                              # noqa: E402
import beta_tum_karte_kya_ho_ui as U              # noqa: E402

import cv2                                        # noqa: E402
import numpy as np                                # noqa: E402
from PIL import Image, ImageDraw, ImageFont       # noqa: E402

FPS = K.FPS
HALF = 0.5 / FPS
WIN = U.WIN_BIG
WCX, WCY = 540.0, 875.0
WW, WH = WIN[2] - WIN[0], WIN[3] - WIN[1]          # 860 x 570

_PLUG = ('/root/.claude/plugins/synced/52e39fd9-fc02-4eeb-bd0a-78be55c219f4_9d49974d-76ce-4345-a26f-8cb895a77bfd/'
         '82436e8d-b5bb-4da5-b372-0309f771299f/skills/animation-studio')
FONT_SRC = {'c02_parody_wedding': _PLUG + '/examples/wedding-invite/assets/fonts/Cinzel-700.ttf',
            'c02_parody_cartoon': _PLUG + '/engine/fonts/Bungee-Regular.ttf'}


def ensure_fonts():
    for name, src in FONT_SRC.items():
        dst = K.font_path(name)
        if not os.path.exists(dst) and os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)


C = U.C


@functools.lru_cache(maxsize=1)
def win_alpha():
    return K.rrect_alpha(WW, WH, 24.0, 0)


# ---------------------------------------------------------------------------------------------- P1 wedding
@functools.lru_cache(maxsize=1)
def wedding_ground():
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    d = np.hypot(xx - WW / 2, yy - WH / 2) / (0.62 * WW)
    k = np.clip(1.0 - d, 0, 1) ** 1.3
    col = C('NIGHT_1')[None, None, :] * (1 - k[..., None]) + C('PLUM', 1.6)[None, None, :] * k[..., None]
    return U.ro(U.solid(win_alpha(), (1, 1, 1)) * np.concatenate([col, np.ones_like(k)[..., None]], 2))


@functools.lru_cache(maxsize=1)
def stars():
    rng = np.random.default_rng(147)
    n = 74
    x = rng.uniform(WIN[0] + 18, WIN[2] - 18, n)
    y = rng.uniform(WIN[1] + 18, WIN[3] - 18, n)
    r = rng.integers(2, 6, n)
    op = rng.uniform(0.25, 0.8, n)
    ph = rng.uniform(0, 2 * math.pi, n)
    fq = rng.uniform(1.5, 4.0, n)
    return x, y, r, op, ph, fq


@functools.lru_cache(maxsize=8)
def star_sprite(r):
    return U.ro(K.glow(K.disc(float(r), C('AMBER', 1.3)), C('GOLD'), sigmas=(r * 1.2, r * 3.2), strength=0.55))


@functools.lru_cache(maxsize=1)
def wedding_title():
    ensure_fonts()
    st = T.style('gold', font='c02_parody_wedding', px=96)
    return T.Glyphs('Happy Wedding', st, px=96)


@functools.lru_cache(maxsize=1)
def burst():
    rng = np.random.default_rng(159)
    n = 22
    ang = rng.uniform(0, 2 * math.pi, n)
    sp = rng.uniform(260, 620, n)
    sz = rng.uniform(2.5, 5.0, n)
    vx, vy = np.cos(ang) * sp, np.sin(ang) * sp
    vx[0], vy[0], sp[0] = 980.0, 260.0, 1010.0          # the one sparkle that lands outside the window frame
    return vx, vy, sz


def wedding(cv, t, xf, t_spark=159 / FPS):
    """P1 (f147-f189). Ground fades in f147-f159 (out_cubic) and out f180-f189 with the title wipe."""
    k = K.ramp(t, 147 / FPS - HALF, 159 / FPS, 'out_cubic') * (1.0 - K.ramp(t, 6.0, 189 / FPS, 'in_cubic'))
    if k <= 1e-4:
        return
    cx, cy = xf.p(WCX, WCY)
    K.draw(cv, wedding_ground(), cx, cy, scale=xf.s, opacity=k)
    x, y, r, op, ph, fq = stars()
    for i in range(len(x)):
        o = op[i] * (0.55 + 0.45 * math.sin(2 * math.pi * fq[i] * t + ph[i])) * k
        if o > 0.02:
            px, py = xf.p(x[i], y[i])
            K.draw(cv, star_sprite(int(r[i])), px, py, opacity=o, mode='add')
    if t >= 5.1 - HALF:
        tx, ty = xf.p(540, 875)
        wedding_title().wipe(cv, t, tx, ty, t0=5.1, dur=0.4, out_t0=6.0, out_dur=0.3)
    # sparkle burst at the spark landing (0.3 s)
    d = t - t_spark
    if 0 <= d < 0.32:
        vx, vy, sz = burst()
        drag = (1 - math.exp(-4.0 * d)) / 4.0
        fade = (1 - d / 0.32) ** 1.5
        for i in range(len(vx)):
            px, py = xf.p(WCX + vx[i] * drag, WCY + vy[i] * drag)
            K.draw(cv, star_sprite(int(round(sz[i]))), px, py, opacity=fade, mode='add')


# ---------------------------------------------------------------------------------------------- P2 cartoon
@functools.lru_cache(maxsize=1)
def cartoon_ground():
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    g = 26.0
    r = 2.0 + 7.0 * np.clip((xx / WW + yy / WH) / 2.0, 0, 1)
    dx = np.mod(xx, g) - g / 2
    dy = np.mod(yy, g) - g / 2
    cov = np.clip(r - np.hypot(dx, dy) + 0.5, 0, 1)
    col = C('EMBER', 0.85)[None, None, :] * (1 - cov[..., None]) + C('FLAME', 0.9)[None, None, :] * cov[..., None]
    a = win_alpha()
    out = np.zeros((WH, WW, 4), np.float32)
    out[..., :3] = col * a[..., None]
    out[..., 3] = a
    return U.ro(out)


@functools.lru_cache(maxsize=2)
def motion_glyphs(px=180):
    """Per-glyph MOTION sprites (IVORY fill, NIGHT_0 stroke 0.068 em, FLAME shadow (0.053, 0.053) em), all in one
    vertical frame whose bottom row is the word's ink bottom; -> [(sprite, x_centre_rel, anchor_x)], word ink box."""
    ensure_fonts()
    ss = 2
    f = ImageFont.truetype(K.font_path('c02_parody_cartoon'), int(px * ss))
    word = 'MOTION'
    sw = int(round(0.068 * px * ss))
    so = 0.053 * px * ss
    asc, desc = f.getmetrics()
    Hc = asc + desc + 2 * sw + int(so) + 8 * ss
    out = []
    xs = []
    total = f.getlength(word)
    tops, bots = [], []
    imgs = []
    for i, ch in enumerate(word):
        x_i = f.getlength(word[:i])
        adv = f.getlength(ch)
        bb = f.getbbox(ch, stroke_width=sw)
        Wc = int(bb[2] - bb[0] + 2 * sw + so + 8 * ss)
        ox = -bb[0] + sw + 2 * ss
        oy = sw + 2 * ss
        lay = []
        for (dxs, dys, stroke, kind) in ((so, so, sw, 'sh'), (0, 0, sw, 'st'), (0, 0, 0, 'fi')):
            im = Image.new('L', (Wc, Hc), 0)
            ImageDraw.Draw(im).text((ox + dxs, oy + dys), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
            lay.append(np.asarray(im, np.float32) / 255.0)
        imgs.append((lay, x_i + bb[0] - ox, adv))
        nz = np.nonzero(np.maximum(lay[0], lay[1]).any(1))[0]
        tops.append(nz[0])
        bots.append(nz[-1] + 1)
    top, bot = min(tops), max(bots)
    for (lay, xoff, adv) in imgs:
        sh, st, fi = [m[top:bot] for m in lay]
        rgb = C('FLAME')[None, None, :] * sh[..., None]
        a = sh.copy()
        rgb = C('NIGHT_0')[None, None, :] * st[..., None] + rgb * (1 - st[..., None])
        a = st + a * (1 - st)
        rgb = C('IVORY')[None, None, :] * fi[..., None] + rgb * (1 - fi[..., None])
        a = fi + a * (1 - fi)
        spr = np.concatenate([rgb, a[..., None]], 2).astype(np.float32)
        h2, w2 = spr.shape[0] // ss, spr.shape[1] // ss
        spr = cv2.resize(spr, (w2, h2), interpolation=cv2.INTER_AREA)
        cols = np.nonzero(spr[..., 3].max(0) > 0.02)[0]
        cx_ink = (cols[0] + cols[-1] + 1) / 2.0 if len(cols) else w2 / 2.0
        out.append((U.ro(spr), (xoff / ss) + cx_ink, cx_ink / w2))
        xs.append(((xoff / ss) + cols[0], (xoff / ss) + cols[-1] + 1) if len(cols) else (0, 0))
    x0 = min(a for a, _ in xs)
    x1 = max(b for _, b in xs)
    hh = out[0][0].shape[0]
    return out, (x0, x1, hh), total / ss


MOTION_BOTTOM = 1031.0
MOTION_CX = 540.0


def motion(cv, t, xf, t0, t2):
    """MOTION rubber-hose wobble per glyph, anchored at the ink bottom: y-scale = 1 + 0.25 (1 - JELLY(t - t0 - 0.05 i))
    (+ boing 2 at t2 as a sine-started spring), rot = 6 deg sin(2 pi 2.5 (t - t0) + i)."""
    gl, (x0, x1, hh), _ = motion_glyphs(180)
    shift = MOTION_CX - (x0 + x1) / 2.0
    for i, (spr, xc, ax) in enumerate(gl):
        tt = t - t0 - 0.05 * i
        sy = 1.0 + 0.25 * (1.0 - X.spring(max(0.0, tt), 'JELLY'))
        d2 = t - t2 - 0.05 * i
        if d2 > 0:
            sy += 0.20 * math.exp(-d2 / 0.13) * math.sin(2 * math.pi * 3.2 * d2)
        rot = 6.0 * math.sin(2 * math.pi * 2.5 * (t - t0) + i)
        px, py = xf.p(xc + shift, MOTION_BOTTOM)
        K.draw(cv, spr, px, py, scale=(xf.s, sy * xf.s), rot=rot, anchor=(ax, 1.0))


PILL_R = (282, 607, 798, 745)


def cartoon(cv, t, xf, t0=215 / FPS, t2=221 / FPS):
    """P2: everything POPs at t0 (4 f): ground, output pill + 'Cartoon?' (SETTLE), MOTION (JELLY)."""
    if t < t0 - HALF:
        return
    op = K.ramp(t, t0 - HALF, t0 + 3 / FPS, 'out_cubic')
    cx, cy = xf.p(WCX, WCY)
    K.draw(cv, cartoon_ground(), cx, cy, scale=xf.s, opacity=op)
    motion(cv, t, xf, t0, t2)
    pop = 0.7 + 0.3 * X.spring(max(0.0, t - t0), 'POP')
    pc = xf.p((PILL_R[0] + PILL_R[2]) / 2.0, (PILL_R[1] + PILL_R[3]) / 2.0)
    U.glass(PILL_R[2] - PILL_R[0], PILL_R[3] - PILL_R[1], 69.0).draw(cv, pc[0], pc[1], scale=pop * xf.s, opacity=op,
                                                                      frost=0)
    ws = 0.9 + 0.1 * X.spring(max(0.0, t - t0), 'SETTLE')
    wx, wy = xf.p(540, 676)
    U.tx('Cartoon?', 'jw_key', 130).draw(cv, wx, wy, scale=ws * xf.s, opacity=op)


# ---------------------------------------------------------------------------------------------- S4 stamp
@functools.lru_cache(maxsize=1)
def stamp_sprite():
    BW, BH, pad = 685, 215, 40
    Wd, Hd = BW + 2 * pad, BH + 2 * pad
    lay = np.zeros((Hd, Wd, 4), np.float32)
    red = C('RED', 1.25)
    o = K.rrect_alpha(BW, BH, 18.0, pad)
    o_in = K.rrect_alpha(BW - 14, BH - 14, 11.0, pad + 7)
    i_out = K.rrect_alpha(BW - 34, BH - 34, 8.0, pad + 17)
    i_in = K.rrect_alpha(BW - 38, BH - 38, 6.0, pad + 19)
    border = np.clip(o - o_in, 0, 1) + np.clip(i_out - i_in, 0, 1)
    U.over(lay, U.solid(np.clip(border, 0, 1), red))
    for s, yy in (('PHONE PE LAGE', Hd / 2 - 47.5), ('REHTE HO.', Hd / 2 + 47.5)):
        T.render(s, 'jw_caps_bold', px=76, fill=('RED', 1.25)).draw(lay, Wd / 2, yy)
    n = X.up(X.fbm(9, 3.0, 4))
    n = np.ascontiguousarray(n[600:600 + Hd, 150:150 + Wd])
    rng = np.random.default_rng(9)
    speck = cv2.GaussianBlur(rng.random((Hd, Wd)).astype(np.float32), (0, 0), 1.2)
    keep = np.clip((n - 0.25) / 0.06, 0, 1) * np.clip((speck - 0.36) / 0.05 + 0.5, 0, 1)
    keep = 1.0 - (1.0 - keep) * 0.92
    lay *= keep[..., None]
    return U.ro(lay)


def stamp(cv, t, xf, t0=8.4):
    if t < t0 - HALF:
        return
    s = 1.5 + (1.0 - 1.5) * X.spring(max(0.0, t - t0), 'SLAM')
    x, y = xf.p(540, 875)
    K.draw(cv, stamp_sprite(), x, y, scale=s * xf.s, rot=-7.0)
