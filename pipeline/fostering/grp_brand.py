"""grp_brand.py: Google Ranker Pro brand pieces for the GRP client testimonial set (Oct 2026 clips: of2, leam2,
york, golden, coventry, zentro).

Brand tokens come from googlerankerpro.com's site.css (brand-blue #3fa9f5, brand-orange #f7931e, heading #0b1628,
body #475569, action-blue #006eb8, surface-blue #eaf5fd, border #dbe6ef, Inter UI type, 12 px button radius).

LOGO       logo(h, dark) vector rebuild of the site logo (ring 'g' mark in blue / orange / black, dot, smile,
           'Google Ranker' in Poppins Bold and a blue script 'Pro'); mark(h, dark) the symbol alone
PIECES     logo_bug(cv, t, t0, t1), ai_label(cv, t, ...), end_card(cv, t, t0, client, url, extra_fine)
           backdrop() airy white-blue brand plate;  band_wipe(...) blue -> orange diagonal band for cuts
           captions(words, ...) caption style (Inter Bold, white, active word on an action-blue pill)
CARDS      card(w, h) white UI card;  chip(text, icon) pill;  search_bar(cv, t, ...) typed query
"""
import functools
import math

import cv2
import numpy as np

import core as K
import grp_kit as G
import ui

BLUE, ORANGE, INK, BODY, ACTION, SURF, BORDER = '#3FA9F5', '#F7931E', '#0B1628', '#475569', '#006EB8', '#EAF5FD', \
    '#DBE6EF'
GREEN = '#16A34A'
FB, FS, FM = 'Inter-Bold', 'Inter-SemiBold', 'Inter-Medium'
F_LOGO, F_PRO = 'Poppins-Bold', 'Caveat-Bold'
W, H = K.W, K.H


# ---------------------------------------------------------------------------------------------- logo
# Geometry measured on the site's logo-approved.png (215 x 85 px), in those logo px:
#   ring centre (27, 35), outer radius 23, inner 12; blue / orange split at 37 deg, orange / black at -18 deg,
#   black / blue at -140 deg (maths angles, y up); dot centre (46.5, 9.5) r 6.5;
#   smile: lower half ring centred (27, 59), outer 24.5, inner 13;
#   'Google' baseline 37, 'Ranker' baseline 69, both from x 67, 109 px wide; 'Pro' from x 180, baseline 73.
def _mark_layers(k, ss=4):
    """Coverage masks (h, w) at logo scale k (px per logo px) for the mark's parts, over a box 0..56 x 0..85."""
    w, h = int(math.ceil(56 * k)) + 2, int(math.ceil(85 * k)) + 2
    xs = (np.arange(w * ss, dtype=np.float32) + 0.5) / (ss * k)
    ys = (np.arange(h * ss, dtype=np.float32) + 0.5) / (ss * k)
    X, Y = np.meshgrid(xs, ys)
    dx, dy = X - 27.0, Y - 35.0
    d = np.sqrt(dx * dx + dy * dy)
    ring = (d <= 23.0) & (d >= 12.0)
    ang = np.degrees(np.arctan2(-dy, dx))
    orange = ring & (ang > -18) & (ang < 37)
    black = ring & (ang <= -18) & (ang > -140)
    blue = ring & ~orange & ~black
    dot = (X - 46.5) ** 2 + (Y - 9.5) ** 2 <= 6.5 ** 2
    uy = Y - 59.0
    du = np.sqrt((X - 27.0) ** 2 + uy * uy)
    smile = (du <= 24.5) & (du >= 13.0) & (uy >= 0)

    def down(m):
        return cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    return dict(blue=down(blue), orange=down(orange), black=down(black | dot | smile)), w, h


@functools.lru_cache(maxsize=24)
def logo(h=170, dark=False, mark_only=False):
    """Premultiplied linear sprite of the GRP logo, h = logo height in px (the 85-px-tall site logo scaled)."""
    k = h / 85.0
    ink = '#FFFFFF' if dark else '#0E0E10'
    wide = 56 if mark_only else 216
    S = ui.Surf(int(math.ceil(wide * k)) + 8, int(math.ceil(85 * k)) + 8)
    ox, oy = 4, 4
    layers, mw, mh = _mark_layers(k)
    for name, c in (('blue', BLUE), ('orange', ORANGE), ('black', ink)):
        S.fill(layers[name], ox, oy, G.lin(c), 1.0)
    if not mark_only:
        size = 30.0 * k
        size *= 109.0 * k / max(G.measure('Google', size, F_LOGO), 1)
        S.text(round(ox + 66 * k), round(oy + 37 * k), 'Google', size, F_LOGO, ink)
        S.text(round(ox + 66 * k), round(oy + 69 * k), 'Ranker', size, F_LOGO, ink)
        ps = 31.0 * k
        S.text(round(ox + 180 * k), round(oy + 74 * k), 'Pro', ps, F_PRO, BLUE)
    S.img.setflags(write=False)
    return S.img


def mark(h=120, dark=False):
    return logo(h, dark, True)


# ---------------------------------------------------------------------------------------------- plates
@functools.lru_cache(maxsize=1)
def backdrop():
    """Airy brand plate: white to surface-blue, soft blue / orange glows, faint dot grid (linear RGBA, opaque)."""
    cv = K.new_canvas()
    top, bot = np.array(G.lin('#FFFFFF'), np.float32), np.array(G.lin(SURF), np.float32)
    y = (np.arange(H, dtype=np.float32) / (H - 1))[:, None, None]
    cv[..., :3] = top * (1 - y) + bot * y
    cv[..., 3] = 1.0
    X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    for (cx, cy, r, c, a) in ((930, 260, 520, BLUE, 0.20), (120, 1640, 560, ORANGE, 0.12), (980, 1500, 380, BLUE, 0.08)):
        g = np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * r * r)).astype(np.float32) * np.float32(a)
        cv[..., :3] = cv[..., :3] * (1 - g[..., None]) + np.array(G.lin(c), np.float32) * g[..., None]
    # dot grid (every 44 px), very faint
    dots = np.zeros((H, W), np.float32)
    dots[22::44, 22::44] = 1.0
    dots = cv2.GaussianBlur(dots, (0, 0), 1.2) * np.float32(1.2 * 2 * math.pi * 1.44)
    dots = np.clip(dots, 0, 1) * np.float32(0.10)
    cv[..., :3] = cv[..., :3] * (1 - dots[..., None]) + np.array(G.lin('#9FB6CC'), np.float32) * dots[..., None]
    cv.setflags(write=False)
    return cv


def band_wipe(cv, other, u, other_is_new, angle=-60, width=0.06):
    """Diagonal wipe between cv (current shot) and other, with a blue -> orange band riding the edge."""
    m = G.wipe(W, H, u, angle=angle, soft=0.001)[..., None]
    if other_is_new:
        cv[:] = cv * (1 - m) + other * m
    else:
        cv[:] = other * (1 - m) + cv * m
    a = math.radians(angle)
    dx, dy = math.cos(a), -math.sin(a)
    span = 0.5 * (abs(dx) + abs(dy))
    front = -span + u * (2 * span)
    xs = (np.arange(W, dtype=np.float32) + 0.5) / W - 0.5
    ys = (np.arange(H, dtype=np.float32) + 0.5) / H - 0.5
    proj = xs[None, :] * dx + ys[:, None] * dy
    b = np.clip(np.clip(1 - np.abs(proj - front + width / 2) / (width / 2), 0, 1) ** 0.6 * 1.25, 0, 1)
    g = _band_grad()
    cv[..., :3] = cv[..., :3] * (1 - b[..., None]) + g * b[..., None]


@functools.lru_cache(maxsize=1)
def _band_grad():
    return K.gradient(W, H, [G.lin(BLUE), G.lin(ORANGE)], angle=35)


# ---------------------------------------------------------------------------------------------- UI pieces
def card(w, h, r=28, fill='#FFFFFF', fill_a=0.97, shadow=0.38, border_a=0.9, accent=None):
    return G.panel(int(w), int(h), r, fill=fill, fill_a=fill_a, border=BORDER, border_a=border_a, border_w=1.5,
                   shadow=shadow, shadow_blur=24, shadow_dy=14, accent=accent, accent_w=10)


@functools.lru_cache(maxsize=64)
def chip(text, icon=None, size=30, fill='#FFFFFF', color=INK, icon_color=ACTION, h=None, font=FS, pad_x=26,
         border_a=0.9, shadow=0.3, dot=None):
    """Pill with optional leading icon (ui.icon name) or coloured dot. Returns (sprite, pad, w, h)."""
    h = h or int(size * 2.1)
    tw = G.measure(text, size, font)
    lead = (size * 1.05 + 12) if (icon or dot) else 0
    w = int(tw + lead + pad_x * 2)
    pnl, pad = G.panel(w, h, h // 2, fill=fill, fill_a=0.97, border=BORDER, border_a=border_a, border_w=1.5,
                       shadow=shadow, shadow_blur=14, shadow_dy=7)
    spr = pnl.copy()
    S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
    x = pad + pad_x
    if icon:
        ic = ui.icon(icon, int(size * 1.05), color=icon_color, stroke=2.4)
        ui.paste(spr, ic, round(x), round(pad + h / 2 - ic.shape[0] / 2))
        x += lead
    elif dot:
        S.circle(x + size * 0.32, pad + h / 2, size * 0.32, G.lin(dot), 1.0)
        x += size * 0.64 + 14
    S.text(round(x), round(pad + h / 2 + size * 0.36), text, size, font, color)
    spr.setflags(write=False)
    return spr, pad, w, h


def pop(t, t0, t1, fin=0.1, fout=0.25, freq=2.4, damping=0.6):
    """(spring-in amount, fade-out amount, opacity) for an element alive in [t0, t1)."""
    u = K.spring(t - t0, freq, damping) if t >= t0 else 0.0
    out = K.ramp(t, t1 - fout, t1, 'in_cubic')
    op = min(1.0, max(0.0, (t - t0) / fin)) * (1 - out)
    return u, out, op


def draw_chip(cv, t, text, x, y, t0, t1, icon=None, size=30, anchor='m', dot=None, fill='#FFFFFF', color=INK,
              icon_color=ACTION, rise=24):
    if not (t0 <= t < t1):
        return
    spr, pad, w, h = chip(text, icon, size, fill=fill, color=color, icon_color=icon_color, dot=dot)
    u, out, op = pop(t, t0, t1)
    ax = {'l': 0.0, 'm': 0.5, 'r': 1.0}[anchor]
    cx = x + (0.5 - ax) * w
    K.draw(cv, spr, cx, y + rise * (1 - u) - 20 * out, scale=0.86 + 0.14 * u, opacity=op)


def search_bar(cv, t, query, t0, t1, cx=540, cy=240, w=800, h=108, type_dur=1.0, caret=ACTION, size=38):
    """Google-style search pill with the query typing on."""
    if not (t0 <= t < t1):
        return
    u, out, op = pop(t, t0, t1)
    cy = cy - 20 * (1 - u) - 40 * out
    pnl, pad = G.panel(w, h, h // 2, fill='#FFFFFF', fill_a=0.98, border=BORDER, border_a=1.0, shadow=0.38)
    K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=op)
    op2 = K.ramp(t, t0 + 0.1, t0 + 0.3) * (1 - out)
    K.draw(cv, ui.icon('search', 40, color='#5F6368', stroke=2.4), cx - w / 2 + 58, cy, opacity=op2)
    n = int(len(query) * K.clamp((t - (t0 + 0.35)) / type_dur))
    txt = query[:n]
    G.draw_text(cv, txt, cx - w / 2 + 104, cy + 13, size, FM, INK, 'ls', opacity=op2)
    if (t * 2.2) % 1 < 0.6 or n < len(query):
        tw = G.measure(txt, size, FM) if txt else 0
        bar = np.zeros((int(size * 1.15), 3, 4), np.float32)
        bar[..., :3] = G.lin(caret)
        bar[..., 3] = 1
        K.draw(cv, bar, cx - w / 2 + 108 + tw, cy, opacity=op2)


# ---------------------------------------------------------------------------------------------- overlays
def logo_bug(cv, t, t0, t1, x=60, y=66):
    """Small GRP logo on a white pill, top left."""
    if not (t0 <= t < t1):
        return
    k = min(K.ramp(t, t0, t0 + 0.2), 1 - K.ramp(t, t1 - 0.25, t1, 'in_cubic'))
    lg = logo(62)
    pw, ph = lg.shape[1] + 26, lg.shape[0] + 14
    pnl, pad = G.panel(pw, ph, 22, fill='#FFFFFF', fill_a=0.95, border_a=0.0, shadow=0.3, shadow_blur=12,
                       shadow_dy=6)
    K.draw(cv, pnl, x - pad, y - pad, anchor=(0, 0), opacity=k)
    K.draw(cv, lg, x + 13, y + 7, anchor=(0, 0), opacity=k)


def ai_label(cv, t, t0=0.8, solid=False, text='AI re-creation · real client website'):
    if t < t0:
        return
    k = K.ramp(t, t0, t0 + 0.4)
    w = G.measure(text, 24, FS)
    if solid:
        pnl, pad = G.panel(int(w + 32), 40, 20, fill=INK, fill_a=0.80, border_a=0.0, shadow=0.0)
    else:
        pnl, pad = G.panel(int(w + 32), 40, 20, fill='#000000', fill_a=0.40, border_a=0.0, shadow=0.0)
    y = 1862
    K.draw(cv, pnl, 60 - pad, y - 20 - pad, anchor=(0, 0), opacity=k)
    G.draw_text(cv, text, 76, y + 8, 24, FS, '#FFFFFF', 'ls', opacity=0.92 * k)


def captions(words, max_chars=28, breaks=(), y=1640, size=60):
    return G.Captions(words, dict(font=FB, size=size, color='#FFFFFF', accent='#FFFFFF', mode='pill',
                                  pill_color=ACTION, y=y, max_w=900, shadow=0.7, line_h=1.16),
                      max_chars=max_chars, breaks=breaks)


def end_backdrop(cv, t, t0, footage_last=None, dur=0.5):
    """Blur the current footage (which holds its last frame once the clip ends) and fade the brand plate over it.
    (footage_last is unused: swapping to the clip's last frame here caused a jump and a motion-blur ghost.)"""
    if t < t0:
        return cv
    k = K.EASE['inout_cubic'](K.ramp(t, t0, t0 + dur, 'linear'))
    base = cv
    if k > 0.02:
        base = K.gblur(base, 18 * k)
    kk = k ** 2.2                                   # linear-light mix: keep the veil perceptually even
    return base * (1 - 0.9 * kk) + backdrop() * (0.9 * kk)


def _swoosh(w, h=26, color=ORANGE, thick=7.0):
    """Hand-drawn style underline (a shallow arc that thins at the ends), as on the site's hero."""
    S = np.zeros((h * 4, w * 4), np.float32)
    xs = np.linspace(0, 1, 400)
    pts = []
    for x in xs:
        yy = 0.70 - 0.42 * math.sin(math.pi * x) * (0.9 + 0.1 * x)
        pts.append((x * (w * 4 - 40) + 20, yy * (h * 4)))
    for i, (x, yv) in enumerate(pts):
        r = thick * 4 * (0.35 + 0.65 * math.sin(math.pi * min(1, max(0, i / 399.0))))
        cv2.circle(S, (int(x), int(yv)), max(1, int(r / 2)), 1.0, -1, lineType=cv2.LINE_AA)
    a = cv2.resize(S, (w, h), interpolation=cv2.INTER_AREA)
    spr = np.zeros((h, w, 4), np.float32)
    spr[..., :3] = np.array(G.lin(color), np.float32) * a[..., None]
    spr[..., 3] = a
    return spr


_SWOOSH = {}


def end_card(cv, t, t0, client, url, extra_fine=(), captured='Oct 2026'):
    """GRP end card (draw over end_backdrop): logo, the site's promise line, the client, CTA and fine print."""
    if t < t0:
        return
    tt = t - t0
    # logo
    lu = K.spring(tt - 0.10, 2.2, 0.62) if tt > 0.10 else 0.0
    lg = logo(214)
    K.draw(cv, lg, 540, 420 - 30 * (1 - lu), scale=0.9 + 0.1 * lu, opacity=min(1.0, lu * 1.4))
    # promise line from the site hero
    hu = K.ramp(tt, 0.35, 0.75, 'out_cubic')
    G.draw_text(cv, 'Your next customer', 540, 652 + 16 * (1 - hu), 62, FB, INK, 'ms', opacity=hu)
    w1 = G.measure('is ', 62, FB)
    w2 = G.measure('searching.', 62, FB)
    x0 = 540 - (w1 + w2) / 2
    hu2 = K.ramp(tt, 0.48, 0.88, 'out_cubic')
    G.draw_text(cv, 'is ', x0, 728 + 16 * (1 - hu2), 62, FB, INK, 'ls', opacity=hu2)
    G.draw_text(cv, 'searching.', x0 + w1, 728 + 16 * (1 - hu2), 62, FB, BLUE, 'ls', opacity=hu2)
    su = K.EASE['inout_cubic'](K.ramp(tt, 0.75, 1.15, 'linear'))
    if su > 0.01:
        sw = int(w2 + 20)
        if sw not in _SWOOSH:
            _SWOOSH[sw] = _swoosh(sw)
        sp = _SWOOSH[sw]
        m = G.wipe(sp.shape[1], sp.shape[0], su, angle=0, soft=0.05)
        K.draw(cv, G.masked(sp, m), x0 + w1 - 10, 744, anchor=(0, 0))
    # client
    cu = K.spring(tt - 0.65, 2.4, 0.62) if tt > 0.65 else 0.0
    if cu > 0:
        cw, ch = 780, 150
        pnl, pad = card(cw, ch, 30, shadow=0.25)
        y = 910 + 24 * (1 - cu)
        op = min(1.0, cu * 1.5)
        K.draw(cv, pnl, 540, y, scale=0.94 + 0.06 * cu, opacity=op)
        G.draw_text(cv, 'CLIENT', 540, y - 34, 22, FS, BODY, 'ms', opacity=op, tracking=0.22)
        G.draw_text(cv, client, 540, y + 14, 40, FB, INK, 'ms', opacity=op)
        G.draw_text(cv, url, 540, y + 56, 28, FM, ACTION, 'ms', opacity=op)
    # CTA (the site's own call to action)
    bu = K.spring(tt - 0.8, 2.4, 0.6) if tt > 0.8 else 0.0
    if bu > 0:
        txt = 'Get your free SEO audit'
        tw = G.measure(txt, 38, FS)
        bw, bh = int(tw + 150), 104
        btn, pad = G.panel(bw, bh, 24, fill=ORANGE, fill_a=1.0, border_a=0.0, shadow=0.35, shadow_blur=18,
                           shadow_dy=10)
        y = 1122
        op = min(1.0, bu * 1.5)
        K.draw(cv, btn, 540, y, scale=0.88 + 0.12 * bu, opacity=op)
        G.draw_text(cv, txt, 540 - 22, y + 13, 38, FS, INK, 'ms', opacity=op)
        K.draw(cv, ui.icon('arrow_right', 34, color=INK, stroke=3.0), 540 + tw / 2 + 12, y, opacity=op)
        G.draw_text(cv, 'googlerankerpro.com', 540, y + 118, 40, FB, ACTION, 'ms',
                    opacity=K.ramp(tt, 0.95, 1.2))
    fp = K.ramp(tt, 1.0, 1.3)
    lines = ['AI re-creation of the client’s testimonial.', 'Client website as captured %s.' % captured] + \
        list(extra_fine) + ['Results vary by business.']
    for k, ln in enumerate(lines):
        G.draw_text(cv, ln, 540, 1330 + 34 * k, 25, FM, BODY, 'ms', opacity=fp)


def prewarm():
    logo(214)
    logo(62)
    backdrop()
    _band_grad()


@functools.lru_cache(maxsize=16)
def phone_card(path, crop, width, shadow=0.45):
    """A plain dark phone (rounded bezel, speaker pill) holding a site capture crop -> G.Card (body = phone)."""
    bez = max(10, int(width * 0.035))
    sw = width - 2 * bez
    img = G.image_crop(path, crop, sw)
    sh = img.shape[0]
    w, h = width, sh + 2 * bez
    r = int(width * 0.13)
    body, pad = G.panel(w, h, r, fill='#111317', fill_a=1.0, border='#FFFFFF', border_a=0.18, border_w=2.0,
                        shadow=shadow, shadow_blur=30, shadow_dy=18)
    spr = body.copy()
    S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
    a, X0, Y0 = S.rrect_mask(pad + bez, pad + bez, sw, sh, r - bez * 0.8)
    m = np.zeros(spr.shape[:2], np.float32)
    m[Y0:Y0 + a.shape[0], X0:X0 + a.shape[1]] = a
    sub = m[pad + bez:pad + bez + sh, pad + bez:pad + bez + sw][..., None]
    reg = spr[pad + bez:pad + bez + sh, pad + bez:pad + bez + sw]
    reg[...] = reg * (1 - sub) + img * sub
    # speaker pill
    S.rrect(pad + w / 2 - w * 0.14, pad + bez + 10, w * 0.28, bez * 1.5, bez * 0.75, (0.004, 0.004, 0.005), 1.0)
    spr.setflags(write=False)
    return G.Card(spr, pad, w, h, (bez, bez, sw, sh))


@functools.lru_cache(maxsize=16)
def logo_card(path, logo_w, w, h, label=None, r=30):
    """White card with a client logo image centred (optional small label above)."""
    pnl, pad = card(w, h, r)
    spr = pnl.copy()
    lg = G.image_logo(path, logo_w)
    ly = pad + h / 2 - lg.shape[0] / 2 + (14 if label else 0)
    ui.paste(spr, lg, round(pad + w / 2 - lg.shape[1] / 2), round(ly))
    if label:
        S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
        tw = G.measure(label, 22, FS, 0.2)
        S.text(round(pad + w / 2 - tw / 2), round(pad + 40), label, 22, FS, BODY, tracking=0.2)
    spr.setflags(write=False)
    return G.Card(spr, pad, w, h, (0, 0, w, h))


@functools.lru_cache(maxsize=8)
def grp_card(w=560, h=200, sub='googlerankerpro.com'):
    """White card with the GRP logo (and the site URL under it)."""
    pnl, pad = card(w, h, 32)
    spr = pnl.copy()
    lg = logo(int(h * 0.56))
    ui.paste(spr, lg, round(pad + w / 2 - lg.shape[1] / 2), round(pad + h * 0.42 - lg.shape[0] / 2))
    if sub:
        S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
        tw = G.measure(sub, 24, FM)
        S.text(round(pad + w / 2 - tw / 2), round(pad + h * 0.86), sub, 24, FM, ACTION)
    spr.setflags(write=False)
    return G.Card(spr, pad, w, h, (0, 0, w, h))
