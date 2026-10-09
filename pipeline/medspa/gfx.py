"""Motion-graphics pieces for the P.S. Med Spa reel.

Builds on ../engine.py (premultiplied float sprites, perspective warps).
Layers are float32 HxWx4 premultiplied RGBA at output size (1080x1920).
"""
import functools, math, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw

import common  # noqa: F401  (sets REEL_WORKDIR before engine import)
sys.path.insert(0, os.path.abspath(os.path.join(common.HERE, '..')))
import engine as E  # noqa: E402

W, H = common.W, common.H

_composite_rgb = E.composite


def _composite(canvas, spr, x0, y0, opacity=1.0, mode='over'):
    """engine.composite, extended to premultiplied RGBA canvases (layers)."""
    if canvas.shape[2] == 3:
        return _composite_rgb(canvas, spr, x0, y0, opacity, mode)
    h, w = spr.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(canvas.shape[1], x0 + w), min(canvas.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0 or opacity <= 0.001:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    dst = canvas[Y0:Y1, X0:X1]
    dst *= (1 - s[..., 3:4] * opacity)
    dst += s * opacity


E.composite = _composite  # warp/draw/draw3d resolve it from the module at call time

LIGHT_I = 'Hanken-LightItalic'
SERIF = 'Fraunces-SemiBold'
SERIF_I = 'Fraunces-SemiBoldItalic'

WHITE = (1.0, 1.0, 1.0)
RED = E.hexc(common.RED)[:3]
# "grey instead of blue": silver-grey into the brand charcoal
GREY_STOPS = [(-0.80, (0.66, 0.68, 0.72)), (-0.35, (0.50, 0.52, 0.57)), (0.05, (0.27, 0.285, 0.32))]
RED_STOPS = [(-0.80, (1.00, 0.36, 0.38)), (-0.35, E.hexc(common.RED)[:3]), (0.05, (0.66, 0.05, 0.09))]


def new_layer():
    return np.zeros((H, W, 4), np.float32)


def over(dst, src):
    """src over dst, both premultiplied (in place on dst)."""
    dst *= (1 - src[..., 3:4])
    dst += src
    return dst


# ------------------------------------------------------------------ glyph runs

@functools.lru_cache(maxsize=None)
def glyph_run(text, fname, size):
    """Per-glyph alpha masks positioned relative to (run origin x, baseline y)."""
    f = E.font(fname, size)
    pad = int(size * 0.12) + 6
    out = []
    for i, ch in enumerate(text):
        if ch == ' ':
            continue
        x = f.getlength(text[:i + 1]) - f.getlength(ch)
        bb = f.getbbox(ch, anchor='ls')
        w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        im = Image.new('L', (max(w, 1), max(h, 1)), 0)
        ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), ch, font=f, fill=255, anchor='ls')
        out.append(dict(i=i, a=np.asarray(im, np.float32) / 255.0, ox=x + bb[0] - pad, oy=bb[1] - pad))
    return out, f.getlength(text)


def _fill_rgb(h, oy, size, fill):
    if fill[0] == 'solid':
        return np.broadcast_to(np.array(fill[1], np.float32), (h, 1, 3))
    stops = fill[1]
    ys = (oy + np.arange(h, dtype=np.float32)) / size
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([s[1] for s in stops], np.float32)
    rgb = np.stack([np.interp(ys, pos, cols[:, k]) for k in range(3)], 1)
    return rgb[:, None, :]


@functools.lru_cache(maxsize=4096)
def glyph_sprite(text, fname, size, gi, fill, shadow, blur):
    """Premultiplied sprite of glyph gi with fill + optional soft shadow; returns (spr, ox, oy)."""
    glyphs, _ = glyph_run(text, fname, size)
    g = glyphs[gi]
    a = g['a']
    sig_max = max(p[1] for p in (shadow if isinstance(shadow[0], tuple) else (shadow,))) if shadow else 0
    m = int(max(sig_max * 3, blur * 3)) + 6
    a = np.pad(a, m)
    rgb = _fill_rgb(a.shape[0], g['oy'] - m, size, fill)
    spr = np.concatenate([rgb * a[..., None], a[..., None]], 2).astype(np.float32)
    if shadow:
        passes = shadow if isinstance(shadow[0], tuple) else (shadow,)
        sa = np.zeros_like(a)
        for op, sig, dy in passes:
            s1 = np.roll(cv2.GaussianBlur(a, (0, 0), sig), int(dy), axis=0) * op
            sa = sa + s1 * (1 - sa)
        sh = np.concatenate([np.zeros(sa.shape + (3,), np.float32), sa[..., None]], 2)
        spr = spr + sh * (1 - spr[..., 3:4])
    if blur > 0.3:
        spr = cv2.GaussianBlur(spr, (0, 0), blur)
    return spr, g['ox'] - m, g['oy'] - m


def text_width(text, fname, size):
    return glyph_run(text, fname, size)[1]


def fit(text, fname, size, max_w):
    while size > 20 and text_width(text, fname, size) > max_w:
        size -= 4
    return size


def draw_run(layer, text, fname, size, x0, base_y, fill=('solid', WHITE), shadow=None,
             reveal=None, t=0.0, opacity=1.0, rise=0.55, stagger=0.0, dur=0.32, max_blur=7.0,
             scale_from=1.0):
    """Animate a glyph run. reveal: list of (char_index_start, t_start) for words, or None (all at once).
    Each glyph eases in over `dur` (fade, rise by `rise`*size*0.3, de-blur)."""
    if opacity <= 0.003:
        return
    glyphs, _ = glyph_run(text, fname, size)
    starts = []
    for g in glyphs:
        ts = reveal[0][1] if reveal else 0.0
        if reveal:
            for ci, tw in reveal:
                if g['i'] >= ci:
                    ts = tw
        starts.append(ts)
    for k, g in enumerate(glyphs):
        p = E.prog(t, starts[k] + k * stagger, starts[k] + k * stagger + dur)
        if p <= 0:
            continue
        e = E.e_out_cubic(p)
        bl = round((1 - e) * max_blur * 2) / 2
        spr, ox, oy = glyph_sprite(text, fname, size, k, fill, shadow, bl)
        dy = (1 - e) * rise * size * 0.3
        sc = scale_from + (1 - scale_from) * e
        if abs(sc - 1) > 1e-3:
            h, w = spr.shape[:2]
            cx, cy = x0 + ox + w / 2, base_y + oy + h / 2 + dy
            E.draw(layer, spr, cx, cy, scale=sc, opacity=e * opacity)
        else:
            E.composite(layer, spr, int(round(x0 + ox)), int(round(base_y + oy + dy)), e * opacity)


def word_reveal(words, ws, times):
    """Join display words; return (text, [(char_index, t_start)])."""
    text, rev = '', []
    for w, t in zip(words, times):
        if text:
            text += ' '
        rev.append((len(text), t))
        text += w
    return text, rev


# ------------------------------------------------------------------ captions

CAP_SIZE = 70
CAP_SHADOW = ((0.70, 10.0, 3), (0.45, 2.5, 1))


def caption(layer, t, words, times, t_end, cx, base_y, size=CAP_SIZE, font=LIGHT_I, fill=('solid', WHITE),
            shadow=CAP_SHADOW, out_dur=0.04):
    """Small white word-by-word caption (centered phrase, words appear as spoken)."""
    if t < times[0] - 0.01 or t > t_end + out_dur:
        return
    text, rev = word_reveal(words, None, times)
    wdt = text_width(text, font, size)
    op = 1.0 - E.prog(t, t_end, t_end + out_dur)
    draw_run(layer, text, font, size, cx - wdt / 2, base_y, fill=fill, shadow=shadow, reveal=rev, t=t,
             opacity=op, dur=0.22, max_blur=5.0, rise=0.8)


def hero_l2(layer, t, text, t0, t_end, cx, base_y, size, color='grey', out_dur=0.22, opacity=0.94, drift=0.035):
    """Big Fraunces word (goes BEHIND the subject: draw on the behind layer)."""
    if t < t0 or t > t_end + out_dur:
        return
    stops = GREY_STOPS if color == 'grey' else RED_STOPS
    wdt = text_width(text, SERIF, size)
    # slow drift (scale about center) for life
    life = E.prog(t, t0, t_end + out_dur)
    op = opacity * (1.0 - E.e_in_cubic(E.prog(t, t_end, t_end + out_dur)))
    tmp = new_layer() if drift else layer
    draw_run(tmp, text, SERIF, size, cx - wdt / 2, base_y, fill=('grad', tuple(stops)), shadow=None,
             t=t, opacity=op, stagger=min(0.035, 0.26 / max(1, len(text))), dur=0.40, max_blur=9.0, rise=0.9,
             reveal=[(0, t0)])
    if drift:
        s = 1.0 + drift * life
        M = np.float32([[s, 0, cx * (1 - s)], [0, s, (base_y - size * 0.35) * (1 - s)]])
        tmp = cv2.warpAffine(tmp, M, (W, H), flags=cv2.INTER_LINEAR)
        over(layer, tmp)


def hero_l1(layer, t, words, times, t_end, x_left, base_y, size=70, out_dur=0.18, fill=('solid', WHITE)):
    if t < times[0] - 0.01 or t > t_end + out_dur:
        return
    text, rev = word_reveal(words, None, times)
    op = 1.0 - E.prog(t, t_end, t_end + out_dur)
    draw_run(layer, text, LIGHT_I, size, x_left, base_y, fill=fill, shadow=((0.65, 9.0, 3), (0.4, 2.5, 1)), reveal=rev, t=t,
             opacity=op, dur=0.25, max_blur=5.0, rise=0.8)


def hero_l3(layer, t, words, times, t_end, cx, base_y, size=104, out_dur=0.18, fill=('solid', WHITE), font=SERIF_I):
    if t < times[0] - 0.01 or t > t_end + out_dur:
        return
    text, rev = word_reveal(words, None, times)
    wdt = text_width(text, font, size)
    op = 1.0 - E.prog(t, t_end, t_end + out_dur)
    draw_run(layer, text, font, size, cx - wdt / 2, base_y, fill=fill, shadow=((0.6, 10.0, 4), (0.35, 2.5, 1)), reveal=rev, t=t,
             opacity=op, dur=0.28, max_blur=6.0, rise=0.8)


# ------------------------------------------------------------------ red strike line

def strike(layer, t, x0, x1, y, t0, t_end, thick=9, out_dur=0.15):
    if t < t0 or t > t_end + out_dur:
        return
    p = E.e_inout_cubic(E.prog(t, t0, t0 + 0.30))
    op = 1.0 - E.prog(t, t_end, t_end + out_dur)
    xe = x0 + (x1 - x0) * p
    if xe - x0 < 2:
        return
    a = np.zeros((H, W), np.float32)
    cv2.line(a, (int(x0), int(y)), (int(xe), int(y)), 1.0, thick, cv2.LINE_AA)
    glow = cv2.GaussianBlur(a, (0, 0), 10) * 0.55
    col = np.array(RED, np.float32)
    spr = np.concatenate([col * np.clip(a + glow, 0, 1)[..., None], np.clip(a + glow * 0.8, 0, 1)[..., None]], 2)
    over(layer, spr * op)


# ------------------------------------------------------------------ photo cards

@functools.lru_cache(maxsize=None)
def card_sprite(path, w, h, radius=30):
    """Rounded photo card (cover-fit) with a thin glass edge, premultiplied."""
    im = cv2.imread(path)[..., ::-1].astype(np.float32) / 255
    ih, iw = im.shape[:2]
    s = max(w / iw, h / ih)
    im = cv2.resize(im, (int(math.ceil(iw * s)), int(math.ceil(ih * s))), interpolation=cv2.INTER_AREA)
    y0, x0 = (im.shape[0] - h) // 2, (im.shape[1] - w) // 2
    im = im[y0:y0 + h, x0:x0 + w]
    P = 3
    d = E.rrect_alpha(w, h, radius, P)
    body = E.sdf_fill(d)
    imp = np.pad(im, ((P, P), (P, P), (0, 0)), mode='edge')
    # subtle glass sheen from the top-left
    yy, xx = np.mgrid[0:body.shape[0], 0:body.shape[1]].astype(np.float32)
    sheen = np.clip(1 - (xx / body.shape[1] * 0.6 + yy / body.shape[0]), 0, 1) ** 3 * 0.10
    rgb = np.clip(imp + sheen[..., None], 0, 1)
    spr = np.concatenate([rgb * body[..., None], body[..., None]], 2).astype(np.float32)
    edge = E.sdf_stroke(d, 2.2) * 0.55
    spr = E.over_spr(spr, E.solid(edge, (1, 1, 1, 1)))
    return spr


@functools.lru_cache(maxsize=None)
def shadow_sprite(w, h, radius=30, sigma=26):
    P = int(sigma * 3)
    d = E.rrect_alpha(w, h, radius, P)
    a = cv2.GaussianBlur(E.sdf_fill(d), (0, 0), sigma)
    return np.concatenate([np.zeros(a.shape + (3,), np.float32), a[..., None]], 2), P


def draw_card(layer, path, cx, cy, w, h, rx=0, ry=0, rz=0, z=0, opacity=1.0, shadow=0.55, sh_off=(14, 30)):
    """3D-tilted card with a soft drop shadow behind it. Returns projected center."""
    if opacity <= 0.003:
        return None
    spr = card_sprite(path, int(w), int(h))
    if shadow > 0:
        ssp, P = shadow_sprite(int(w), int(h))
        sw, shh = w + 2 * P, h + 2 * P
        E.draw3d(layer, ssp, cx + sh_off[0], cy + sh_off[1], z + 40, w=sw, h=shh, rx=rx, ry=ry, rz=rz,
                 opacity=shadow * opacity)
    q = E.draw3d(layer, spr, cx, cy, z, w=spr.shape[1], h=spr.shape[0], rx=rx, ry=ry, rz=rz, opacity=opacity)
    q = np.asarray(q[0] if isinstance(q, tuple) else q)
    return q.mean(0)


# ------------------------------------------------------------------ glowing line

def catmull(pts, n=24):
    pts = np.asarray(pts, np.float64)
    P = np.vstack([pts[0] * 2 - pts[1], pts, pts[-1] * 2 - pts[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in np.linspace(0, 1, n, endpoint=False):
            s2, s3 = s * s, s * s * s
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3))
    out.append(P[-2])
    return np.array(out)


def glow_line(layer, pts, p_head, p_tail=0.0, opacity=1.0, color=RED, width=7):
    """Draw a glowing stroke along a spline through pts from fraction p_tail..p_head, with an orb at the head."""
    if opacity <= 0.003 or p_head <= p_tail:
        return
    curve = catmull(pts, 32)
    seg = np.linalg.norm(np.diff(curve, axis=0), axis=1)
    L = np.concatenate([[0], np.cumsum(seg)])
    tot = L[-1]
    a_l, b_l = p_tail * tot, p_head * tot
    sel = curve[(L >= a_l) & (L <= b_l)]
    head = np.array([np.interp(b_l, L, curve[:, 0]), np.interp(b_l, L, curve[:, 1])])
    if len(sel) < 2:
        sel = np.vstack([sel, head]) if len(sel) else np.vstack([head, head])
    else:
        sel = np.vstack([sel, head])
    s = 4  # draw at 1/4 res for the glows, full res for the core
    core = np.zeros((H, W), np.float32)
    pts_i = np.round(sel * 16).astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(core, [pts_i], False, 1.0, width, cv2.LINE_AA, shift=4)
    small = cv2.resize(core, (W // s, H // s), interpolation=cv2.INTER_AREA)
    g1 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 3), (W, H)) * 1.6
    g2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 10), (W, H)) * 2.2
    hx, hy = head
    yy, xx = np.ogrid[0:H, 0:W]
    r2 = ((xx - hx) ** 2 + (yy - hy) ** 2).astype(np.float32)
    orb = np.exp(-r2 / (2 * 9.0 ** 2)) + 0.6 * np.exp(-r2 / (2 * 34.0 ** 2))
    col = np.array(color, np.float32)
    hot = np.array([1.0, 0.82, 0.80], np.float32)
    rgb = (g2[..., None] * col * 0.9 + g1[..., None] * (col * 0.6 + hot * 0.4) + core[..., None] * hot
           + orb[..., None] * (hot * 0.9 + col * 0.3))
    a = np.clip(core + g1 * 0.55 + g2 * 0.35 + orb * 0.8, 0, 1)
    spr = np.concatenate([np.clip(rgb, 0, 1.6) * opacity, (a * opacity)[..., None]], 2).astype(np.float32)
    over(layer, spr)
    return head


# ------------------------------------------------------------------ glass pill

def glass_pill(layer, plate, t, text, cx, cy, t0, t_end, size=46, out_dur=0.2):
    """Frosted-glass pill: blurs the plate behind it."""
    if t < t0 or t > t_end + out_dur:
        return
    p = E.e_out_back(E.prog(t, t0, t0 + 0.35), 1.4)
    op = E.prog(t, t0, t0 + 0.15) * (1 - E.prog(t, t_end, t_end + out_dur))
    tw = text_width(text, 'Hanken-Medium', size)
    w, h = int(tw + 2 * 40), int(size * 1.0 + 2 * 22)
    P = 30
    d = E.rrect_alpha(w, h, h / 2, P)
    body = E.sdf_fill(d)
    bh, bw = body.shape
    sc = 0.6 + 0.4 * p
    x0, y0 = int(cx - bw / 2), int(cy - bh / 2 + (1 - p) * 30)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + bw), min(H, y0 + bh)
    if X1 <= X0 or Y1 <= Y0:
        return
    region = plate[Y0:Y1, X0:X1]
    fro = cv2.GaussianBlur(region, (0, 0), 14) * 0.42 + np.array(E.hexc(common.CHARCOAL)[:3], np.float32) * 0.50
    b = body[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    spr = np.concatenate([fro * b[..., None], b[..., None]], 2).astype(np.float32)
    edge = E.sdf_stroke(d, 1.8)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * 0.55
    spr = E.over_spr(spr, E.solid(edge, (1, 1, 1, 1)))
    # drop shadow
    sh = cv2.GaussianBlur(body, (0, 0), 14)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * 0.35
    full = np.zeros((H, W, 4), np.float32)
    full[Y0:Y1, X0:X1, 3] = np.roll(sh, 10, axis=0)
    full[Y0:Y1, X0:X1] = E.over_spr(full[Y0:Y1, X0:X1], spr)
    ts_text, rev = text, [(0, t0 + 0.08)]
    draw_run(full, ts_text, 'Hanken-Medium', size, cx - tw / 2, y0 + bh / 2 + size * 0.36, fill=('solid', WHITE),
             shadow=(0.35, 4.0, 2), reveal=rev, t=t, dur=0.25, max_blur=4.0, rise=0.5)
    if abs(sc - 1) > 1e-3:
        M = np.float32([[sc, 0, cx * (1 - sc)], [0, sc, cy * (1 - sc)]])
        full = cv2.warpAffine(full, M, (W, H), flags=cv2.INTER_LINEAR)
    over(layer, full * op)
