"""grp_of.py: Organic Fostering client testimonial edit (Google Ranker Pro / Hulk Marketing), 9:16, 24 fps, 33 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp_of --audio <mix.wav>

Source: workspace3/frames/of (Seedance clip, 30.04 s): shot 1 interview 0-9.875 s, shot 2 desk + laptop
9.875-17.5 s, shot 3 close-up 17.5-30.04 s; 30.04-33.0 s end card over the held last frame.

Clean-up: the generated banner behind her carried fake lettering ("Cnar...") - shot 1 uses the slate patches from
grp_prep.py (workspace3/grp/of_banner), shot 3 is punched in past it. The blank laptop screen shows the real
organicfostering.co.uk pages (captured 22 Oct 2026). Never on screen: the homepage hero photo of children, any
allowance figure, Ofsted grade, "No.1" / page-one badges, enquiry numbers. Site facts used: HTTPS, responsive
pages, sitemap of 61 pages with 32 guides (sitemap_20261022.xml), based in Old Trafford, Manchester.
"""
import functools
import math
import os

import cv2
import numpy as np

import core as K
import grp_kit as G
import ui

DUR = 33.0
LOOK = 'natural'
BPM = 84
FPS_SRC = 24.0
N_SRC = 721
T_CUT1, T_CUT2, T_END = 237 / 24.0, 420 / 24.0, 30.0417
MAG, ORA, LEAF, PLUM, INK, IVORY, PEACH = '#B7006E', '#FF6411', '#64A60B', '#5B174F', '#321F35', '#FCF8F5', '#FFD4BA'
FH = 'Nunito-ExtraBold'
FHB = 'Nunito-Black'
FU = 'Poppins-SemiBold'
FB = 'Poppins-Medium'
FR = 'Poppins-Regular'
OF = lambda *p: G.site('organicfostering', *p)          # noqa: E731
LOGO = os.path.join(K.BRAND, 'logo_full.png')
LOGO_DARK = os.path.join(K.BRAND, 'logo_full_onDark.png')
HULK = G.site('hulkmarketing', 'hulk-marketing-logo.png')

WORDS = G.load_words('organic_fostering', fixes={55: 'enquiries'}, retime={0: (0.30, 0.72)})
CAP = G.Captions(WORDS, dict(font=FH, size=66, color='#FFFFFF', accent='#FFFFFF', mode='pill', pill_color=MAG,
                             y=1630, max_w=900, shadow=0.7), max_chars=28)

# PiP window during shot 3 (the footage becomes a rounded card at the top)
PIP_SRC = (0, 150, 1035, 1350)          # source rect x, y, w, h (stays left of the banner sliver)
PIP_S = 0.66
PIP_W, PIP_H = int(PIP_SRC[2] * PIP_S), int(PIP_SRC[3] * PIP_S)
PIP_X, PIP_Y = (1080 - PIP_W) // 2, 130
T_PIP_IN, T_PIP_OUT = 19.05, 25.75


# ---------------------------------------------------------------------------------------------- footage
def shot_of(fi):
    return 1 if fi < 237 else (2 if fi < 420 else 3)


@functools.lru_cache(maxsize=1)
def _info():
    import json
    with open(os.path.join(G.GRP, 'of_info.json')) as f:
        return json.load(f)


@functools.lru_cache(maxsize=4)
def banner_patch(fi):
    p = os.path.join(G.GRP, 'of_banner', '%05d.jpg' % fi)
    im = cv2.imread(p)
    return None if im is None else cv2.cvtColor(im, cv2.COLOR_BGR2RGB)


# ----- laptop screen (shot 2)
LAPTOP_Q = np.float32([[-70.0, 943.26], [229.84, 921.06], [368.86, 1169.56], [-70.0, 1209.89]])


@functools.lru_cache(maxsize=1)
def _laptop_layers():
    """Warped site page (sRGB float) + coverage mask for the laptop screen, minus the mug rim."""
    page = G._rgb(OF('now_areas_desktop.png'))
    ph, pw = page.shape[:2]
    Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]]), LAPTOP_Q)
    warped = cv2.warpPerspective(page.astype(np.float32), Hm, (1080, 1920), flags=cv2.INTER_AREA,
                                 borderMode=cv2.BORDER_CONSTANT)
    mask = cv2.warpPerspective(np.ones((ph, pw), np.float32), Hm, (1080, 1920), flags=cv2.INTER_LINEAR)
    mug = np.zeros((1920, 1080), np.uint8)
    cv2.ellipse(mug, (240, 1186), (108, 28), 0, 0, 360, 1, -1)
    mug[1186:1400, 132:350] = 1
    mug = cv2.GaussianBlur(mug.astype(np.float32), (0, 0), 1.5)
    mask = np.clip(mask * (1 - mug), 0, 1)
    # filmed look: defocus a touch, the original screen white (234) and a soft black level
    warped = cv2.GaussianBlur(warped, (0, 0), 1.1)
    warped = 14.0 + warped * (236.0 - 14.0) / 255.0
    return warped, mask


def laptop_u8(fr):
    warped, mask = _laptop_layers()
    out = fr.astype(np.float32)
    y0, y1 = 900, 1230
    m = mask[y0:y1, :, None]
    out[y0:y1] = out[y0:y1] * (1 - m) + warped[y0:y1] * m
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def _shot1_tf(tf):
    u = K.clamp(tf / T_CUT1)
    return (0.52, 0.45), 1.0 + 0.045 * K.EASE['inout_sine'](u)


def _shot2_tf(tf):
    u = K.clamp((tf - T_CUT1) / (T_CUT2 - T_CUT1))
    return (0.40, 0.55), 1.0 + 0.03 * K.EASE['inout_sine'](u)


def _shot3_tf(tf):
    u = K.clamp((tf - T_CUT2) / (T_END - T_CUT2))
    z = 1.05 + 0.04 * K.EASE['inout_sine'](u)
    vw = 1080 / z
    cx = (1032 - vw / 2) / 1080                       # keep the right edge of the view at source x <= 1032
    return (cx, 0.47), z


@functools.lru_cache(maxsize=3)
def graded_frame(fi):
    """Full source frame after clean-up / screen replacement, graded (no crop) -> linear sprite."""
    fr = G.frame_u8('of', fi)
    sh = shot_of(fi)
    if sh == 1:
        p = banner_patch(fi)
        if p is not None:
            fr = fr.copy()
            x0, y0, x1, y1 = _info()['banner']['1']
            fr[y0:y1, x0:x1] = p
    elif sh == 2:
        fr = laptop_u8(fr)
    return fr


@functools.lru_cache(maxsize=3)
def footage(fi):
    fr = graded_frame(fi)
    tf = fi / FPS_SRC
    sh = shot_of(fi)
    c, z = (_shot1_tf, _shot2_tf, _shot3_tf)[sh - 1](tf)
    return G.shot_sprite(fr, 'of_warm', c, z, sharpen=0.25)


@functools.lru_cache(maxsize=2)
def pip_sprite(fi):
    fr = graded_frame(fi)
    x, y, w, h = PIP_SRC
    sub = np.ascontiguousarray(fr[y:y + h, x:x + w])
    sub = cv2.resize(sub, (PIP_W, PIP_H), interpolation=cv2.INTER_AREA)
    return G.shot_sprite(G.sharpen_u8(sub, 0.3), 'of_warm')


@functools.lru_cache(maxsize=1)
def airy_bg():
    cv = K.background('airy', 3.0, dots=0.5, rim=0.0)
    return cv


def pip_amount(t):
    return min(K.EASE['inout_cubic'](K.ramp(t, T_PIP_IN, T_PIP_IN + 0.6, 'linear')),
               1 - K.EASE['inout_cubic'](K.ramp(t, T_PIP_OUT, T_PIP_OUT + 0.6, 'linear')))


@functools.lru_cache(maxsize=2)
def person(fi):
    """The speaker cut out of the graded, cropped footage (to composite over cards placed behind her)."""
    sh = shot_of(fi)
    c, z = (_shot1_tf, _shot2_tf, _shot3_tf)[sh - 1](fi / FPS_SRC)
    return G.person_sprite(footage(fi), 'of', fi, c, z)


def person_over(cv, t):
    if t < 0.78 or T_CUT1 - 0.16 <= t < T_CUT1 + 0.16 or T_CUT2 - 0.13 <= t < T_CUT2 + 0.31 \
            or T_PIP_IN <= t < T_PIP_OUT + 0.6 or t >= 29.4:
        return
    p = person(G.fidx(t, N_SRC))
    if p is not None:
        K.over(cv, p)


def plate(t):
    fi = G.fidx(t, N_SRC)
    cv = footage(fi).copy()
    # 1 -> 2: brand-gradient diagonal band wipe
    if T_CUT1 - 0.15 <= t < T_CUT1 + 0.15:
        u = K.ramp(t, T_CUT1 - 0.15, T_CUT1 + 0.15, 'inout_cubic')
        new_first = t < T_CUT1
        other = footage(237 if new_first else 236)
        m = G.wipe(K.W, K.H, u, angle=-60, soft=0.001)[..., None]
        cv[:] = (cv * (1 - m) + other * m) if new_first else (other * (1 - m) + cv * m)
        _band(cv, u)
    # 2 -> 3: rounded rect grows from her face
    if T_CUT2 - 0.12 <= t < T_CUT2 + 0.30:
        u = K.EASE['inout_cubic'](K.ramp(t, T_CUT2 - 0.12, T_CUT2 + 0.30, 'linear'))
        m = G.rrect_grow(K.W, K.H, u, 40 * (1 - u) + 2, 0.5, 0.42, 240, 240)[..., None]
        if t < T_CUT2:
            cv[:] = cv * (1 - m) + footage(420) * m
        else:
            cv[:] = footage(419) * (1 - m) + cv * m
    # shot 3 picture-in-picture: the footage shrinks into a rounded window on the airy brand backdrop
    p = pip_amount(t) if T_PIP_IN <= t < T_PIP_OUT + 0.6 else 0.0
    if p > 0:
        cv = _pip(cv, fi, p, t)
    if t >= T_END:
        cv = footage(N_SRC - 1).copy()
    if t >= 29.4:
        k = K.EASE['inout_cubic'](K.ramp(t, 29.4, 30.4, 'linear'))
        bg = airy_bg()
        cv = K.gblur(cv, 16 * k) if k > 0.02 else cv
        cv[:] = cv * (1 - 0.82 * k) + bg * (0.82 * k)
    return cv


def _pip(cv_full, fi, p, t):
    """Blend between full-frame footage (p=0) and the PiP window layout (p=1)."""
    out = airy_bg().copy()
    # window geometry interpolated from the full frame
    # full-frame footage position of the PiP source rect (shot 3 transform)
    c, z = _shot3_tf(fi / FPS_SRC)
    vw, vh = 1080 / z, 1920 / z
    x0 = c[0] * 1080 - vw / 2
    y0 = c[1] * 1920 - vh / 2
    sx, sy, sw, shh = PIP_SRC
    fx0, fy0 = (sx - x0) * z, (sy - y0) * z
    fw, fh = sw * z, shh * z
    wx = K.lerp(fx0, PIP_X, p)
    wy = K.lerp(fy0, PIP_Y, p)
    ww = K.lerp(fw, PIP_W, p)
    wh = K.lerp(fh, PIP_H, p)
    r = 44 * p
    spr = pip_sprite(fi)
    K.draw(out, spr, wx + ww / 2, wy + wh / 2, scale=(ww / PIP_W, wh / PIP_H))
    m = G.canvas_rrect_mask(wx, wy, ww, wh, max(r, 0.5))
    # outside the window: backdrop (p) vs full footage (1 - p)
    a = float(np.clip(1 - p * 1.6, 0, 1))
    res = out * m[..., None] + (cv_full * a + out * (1 - a)) * (1 - m[..., None])
    # window border + shadow
    if p > 0.05:
        S = ui.Surf(K.W, K.H)
        S.stroke_rrect(wx, wy, ww, wh, max(r, 0.5), 3, G.lin('#FFFFFF'), 0.9 * p)
        sh = ui.Surf(K.W, K.H)
        sh.rrect(wx, wy + 18, ww, wh, max(r, 0.5), (0.20, 0.06, 0.18), 1.0)
        sa = K.gblur(sh.img[..., 3], 26, border='constant') * np.float32(0.35 * p) * (1 - m)
        res[..., :3] *= (1 - sa[..., None])
        K.over(res, S.img)
    return res


def _band(cv, u):
    a = math.radians(-60)
    dx, dy = math.cos(a), -math.sin(a)
    span = 0.5 * (abs(dx) + abs(dy))
    front = -span + u * (2 * span)
    xs = (np.arange(K.W, dtype=np.float32) + 0.5) / K.W - 0.5
    ys = (np.arange(K.H, dtype=np.float32) + 0.5) / K.H - 0.5
    proj = xs[None, :] * dx + ys[:, None] * dy
    w = 0.06
    m = np.clip(np.clip(1 - np.abs(proj - front + w / 2) / (w / 2), 0, 1) ** 0.35 * 1.4, 0, 1)
    g = K.gradient(K.W, K.H, [G.lin(MAG), G.lin(ORA)], angle=35)
    cv[..., :3] = cv[..., :3] * (1 - m[..., None]) + g * m[..., None]


# ---------------------------------------------------------------------------------------------- pieces
def white_card(w, h, r=30, accent=None):
    return G.panel(w, h, r, fill='#FFFFFF', fill_a=0.97, border=PLUM, border_a=0.10, border_w=1.5, shadow=0.40,
                   shadow_blur=24, shadow_dy=14, accent=accent, accent_w=10)


def logo_bug(cv, t):
    if t < 2.55 or t >= 29.5:
        return
    k = min(K.ramp(t, 2.55, 2.67), 1 - K.ramp(t, 29.2, 29.5, 'in_cubic'))
    lg = G.image_logo(LOGO, 210)
    pnl, pad = G.panel(244, lg.shape[0] + 22, 22, fill='#FFFFFF', fill_a=0.94, border_a=0.0, shadow=0.3,
                       shadow_blur=12, shadow_dy=6)
    K.draw(cv, pnl, 64 - pad, 70 - pad, anchor=(0, 0), opacity=k)
    K.draw(cv, lg, 64 + 17, 70 + 11, anchor=(0, 0), opacity=k)


def ai_label(cv, t):
    if t < 0.8:
        return
    k = K.ramp(t, 0.8, 1.2)
    txt = 'AI re-creation · real client website'
    w = G.measure(txt, 24, FU)
    pnl, pad = G.panel(int(w + 32), 40, 20, fill='#000000', fill_a=0.40, border_a=0.0, shadow=0.0)
    y = 1862
    if T_PIP_IN + 0.3 < t < T_PIP_OUT + 0.3 or t >= 29.5:
        pnl, pad = G.panel(int(w + 32), 40, 20, fill=PLUM, fill_a=0.85, border_a=0.0, shadow=0.0)
    K.draw(cv, pnl, 64 - pad, y - 20 - pad, anchor=(0, 0), opacity=k)
    G.draw_text(cv, txt, 80, y + 8, 24, FU, '#FFFFFF', 'ls', opacity=0.92 * k)


def intro_reveal(cv, t):
    """0-0.78 s: the footage opens out of a rounded square with a brand-gradient edge."""
    if t >= 0.78:
        return
    u = K.EASE['inout_quart'](K.ramp(t, 0.0, 0.76, 'linear'))
    w0, h0 = 300, 300
    m = G.rrect_grow(K.W, K.H, u, 150 * (1 - u) + 1, 0.5, 0.42, w0, h0)
    bg = airy_bg()
    cv[:] = bg * (1 - m[..., None]) + cv * m[..., None]
    bw = w0 + (K.W - w0) * u
    bh = h0 + (K.H - h0) * u
    st = ui.Surf(K.W, K.H)
    a, X0, Y0 = st.stroke_rrect(540 - bw / 2, 0.42 * K.H - bh / 2, bw, bh, min(150 * (1 - u) + 1, bw / 2, bh / 2),
                                6, (1, 1, 1), 0.0)
    g = K.gradient(a.shape[1], a.shape[0], [G.lin(MAG), G.lin(ORA)], angle=35)
    st.fill(a, X0, Y0, g, 1.0 - u ** 2)
    K.over(cv, st.img)


def intro_card(cv, t):
    """0.3-2.6 s: client-story card in the top band, tucked behind her head; the logo then flies to the bug."""
    if not (0.30 <= t < 2.7):
        return
    cx, cy = 540, 168
    a_in = K.spring(t - 0.30, 2.2, 0.62)
    a_out = K.ramp(t, 2.25, 2.6, 'in_cubic')
    pnl, pad = white_card(600, 252, 40)
    K.draw(cv, pnl, cx, cy, scale=(0.86 + 0.14 * a_in) * (1 - 0.2 * a_out),
           opacity=min(1.0, (t - 0.30) / 0.12) * (1 - a_out))
    op = (1 - a_out) * K.ramp(t, 0.42, 0.62)
    G.draw_text(cv, 'CLIENT STORY', cx, cy - 78, 24, FU, MAG, 'ms', opacity=op, tracking=0.2)
    lg = G.image_logo(LOGO, 420)
    h, w = lg.shape[:2]
    wu = K.ramp(t, 0.55, 1.05, 'out_cubic')
    if wu > 0:
        m = G.wipe(w, h, wu, angle=0, soft=0.12)
        fly = K.EASE['inout_cubic'](K.ramp(t, 2.2, 2.62, 'linear'))
        x = K.lerp(cx, 64 + 17 + 105, fly)
        y = K.lerp(cy + 22, 70 + 11 + h * 210 / 420 / 2, fly)
        K.draw(cv, G.masked(lg, m), x, y, scale=K.lerp(1.0, 210 / 420, fly), opacity=1 - K.ramp(t, 2.55, 2.67))


@functools.lru_cache(maxsize=1)
def _ticks_card():
    """The homepage's three trust ticks, set as a narrow card (no photos of children)."""
    w, h = 300, 440
    pnl, pad = white_card(w, h, 28)
    spr = pnl.copy()
    S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
    ox, oy = pad, pad
    ui.paste(spr, ui.icon('globe', 20, color=MAG, stroke=2.2), ox + 24, oy + 26)
    S.text(ox + 50, oy + 43, 'organicfostering.co.uk', 17, FB, PLUM)
    S.rrect(ox + 24, oy + 64, w - 48, 1.5, 0, G.lin(PLUM), 0.15)
    rows = [('Independent', 'Fostering Agency'), ('Cultural Matching', 'Specialists'), ('Informal First', 'Conversation')]
    for i, (l1, l2) in enumerate(rows):
        y = oy + 94 + i * 114
        S.circle(ox + 38, y + 23, 17, G.lin(LEAF), 1.0)
        ui.paste(spr, ui.icon('check', 21, color='#FFFFFF', stroke=3.0), ox + 28, y + 13)
        S.text(ox + 66, y + 22, l1, 23, FU, INK)
        S.text(ox + 66, y + 54, l2, 23, FU, INK)
    spr.setflags(write=False)
    return spr, pad, w, h


def cultural_card(cv, t, t0=2.75, t1=5.15):
    """Left of her head, tucked behind her: the site's trust ticks; 'Cultural Matching Specialists' lights up
    as she says it."""
    if not (t0 <= t < t1):
        return
    spr, pad, w, h = _ticks_card()
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    x0, y0 = 30, 410 + 30 * (1 - u) + 40 * out
    m = np.zeros(spr.shape[:2], np.float32)
    m[pad:pad + h, pad:pad + w] = G.wipe(w, h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=-90, soft=0.1)
    m = np.maximum(m, K.gblur(m, 16, border='constant'))
    K.draw(cv, G.masked(spr, m), x0 - pad, y0 - pad, anchor=(0, 0), opacity=1 - out)
    hl = K.ramp(t, 3.55, 3.95, 'out_cubic') * (1 - out)
    if hl > 0:
        ry = y0 + 94 + 114 - 14
        S = ui.Surf(w - 20, 100)
        S.rrect(2, 2, w - 24, 96, 18, G.lin(PEACH), 1.0)
        mm = G.wipe(S.img.shape[1], S.img.shape[0], hl, angle=0, soft=0.06)
        K.draw(cv, G.masked(S.img, mm), x0 + 10, ry, anchor=(0, 0), mode='multiply')
        ring = ui.Surf(w - 4, 116)
        ring.stroke_rrect(4, 4, w - 12, 108, 22, 3, G.lin(MAG), 1.0)
        K.draw(cv, ring.img, x0 + 2, ry - 8, anchor=(0, 0), opacity=K.ramp(t, 3.85, 4.15) * (1 - out))


def search_card(cv, t, t0=5.25, t1=7.95):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    w, h = 760, 104
    cx, cy = 540, 232 - 20 * (1 - u) - 40 * out
    # gentle 'not found' shake on "nobody could find us"
    sh = 10 * math.sin((t - 6.62) * 38) * math.exp(-(t - 6.62) * 6) if t > 6.62 else 0.0
    pnl, pad = G.panel(w, h, h // 2, fill='#FFFFFF', fill_a=0.97, border=PLUM, border_a=0.12, shadow=0.4)
    K.draw(cv, pnl, cx + sh, cy, scale=0.9 + 0.1 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    op = K.ramp(t, t0 + 0.1, t0 + 0.3) * (1 - out)
    K.draw(cv, ui.icon('search', 40, color='#7A6A7E', stroke=2.4), cx - w / 2 + 56 + sh, cy, opacity=op)
    q = 'foster agency Manchester'
    n = int(len(q) * K.clamp((t - (t0 + 0.35)) / 1.0))
    txt = q[:n]
    G.draw_text(cv, txt, cx - w / 2 + 100 + sh, cy + 14, 38, FB, INK, 'ls', opacity=op)
    if (t * 2.2) % 1 < 0.6 or n < len(q):
        tw = G.measure(txt, 38, FB) if txt else 0
        bar = np.zeros((44, 3, 4), np.float32)
        bar[..., :3] = G.lin(MAG)
        bar[..., 3] = 1
        K.draw(cv, bar, cx - w / 2 + 104 + tw + sh, cy, opacity=op)


def phone_card(cv, t, t0=8.25, t1=9.8):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.6, 0.55)
    out = K.ramp(t, t1 - 0.22, t1, 'in_cubic')
    cx, cy = 190, 640 + 20 * (1 - u)
    disc = K.disc(70, G.lin('#FFFFFF'))
    K.draw(cv, disc, cx, cy, scale=0.8 + 0.2 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    tilt = -8 + 3 * math.sin((t - t0) * 2.0)
    K.draw(cv, ui.icon('phone', 66, color='#9A8C9D', stroke=2.4), cx, cy, rot=tilt,
           opacity=K.ramp(t, t0 + 0.05, t0 + 0.25) * (1 - out))
    # flat line: silence
    lw = 220 * K.ramp(t, t0 + 0.2, t0 + 0.8, 'out_cubic')
    if lw > 2:
        bar = np.zeros((4, int(lw), 4), np.float32)
        bar[..., :3] = 1.0
        bar[..., 3] = 1.0
        K.draw(cv, bar, cx, cy + 108, opacity=0.8 * (1 - out))


def hulk_card(cv, t, t0=10.45, t1=12.55):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.5, 0.55)
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    lg = G.image_logo(HULK, 520)
    w, h = 620, 150
    cx, cy = 400, 430 - 20 * (1 - u) - 60 * out
    pnl, pad = G.panel(w, h, 34, fill='#17121A', fill_a=0.94, border='#FFFFFF', border_a=0.10, shadow=0.45)
    K.draw(cv, pnl, cx, cy, scale=0.85 + 0.15 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    m = G.wipe(lg.shape[1], lg.shape[0], K.ramp(t, t0 + 0.12, t0 + 0.55, 'out_cubic'), angle=0, soft=0.1)
    K.draw(cv, G.masked(lg, m), cx, cy, opacity=1 - out)


def _card_body(card):
    p = card.pad
    return np.ascontiguousarray(card.spr[p:p + card.h, p:p + card.w])


def rebuild_card(cv, t, t0=12.6, t1=17.4):
    """The page on the laptop lifts off the screen into a floating browser card ('They rebuilt our website')."""
    if not (t0 <= t < t1):
        return
    card = G.browser_card(OF('now_areas_desktop.png'), (0, 0, 1440, 900), 680, 'organicfostering.co.uk/areas-we-cover',
                          accent=MAG)
    body = _card_body(card)
    u = K.EASE['inout_cubic'](K.ramp(t, t0, t0 + 0.65, 'linear'))
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    w, h = card.w, card.h
    cx, cy = 400, 470 - 60 * out
    # tech-chips phase: the card eases up a little and shrinks
    k2 = K.EASE['inout_cubic'](K.ramp(t, 13.95, 14.4, 'linear'))
    sc = 1.0 - 0.12 * k2
    cy -= 40 * k2
    target = np.float32([[cx - w * sc / 2, cy - h * sc / 2], [cx + w * sc / 2, cy - h * sc / 2],
                         [cx + w * sc / 2, cy + h * sc / 2], [cx - w * sc / 2, cy + h * sc / 2]])
    # source quad: the laptop screen with a title bar's worth above it
    src = LAPTOP_Q.copy()
    q = src * (1 - u) + target * u
    if u > 0.02:
        # soft shadow under the flying card
        sh = np.zeros((h + 80, w + 80, 4), np.float32)
        S = ui.Surf(w + 80, h + 80, img=sh)
        S.rrect(40, 52, w, h, 26, (0.12, 0.03, 0.10), 1.0)
        sh[..., 3] = K.gblur(sh[..., 3], 22, border='constant') * 0.45
        sh[..., :3] = 0
        K.draw(cv, sh, cx, cy + 6, scale=sc, opacity=u * (1 - out))
    K.draw_quad(cv, body, [tuple(p) for p in q], opacity=(0.3 + 0.7 * u) * (1 - out))


def tech_chips(cv, t, t0=14.05, t1=17.4):
    if not (t0 <= t < t1):
        return
    labels = [('Secure HTTPS', 'shield'), ('Mobile-friendly pages', 'check'), ('Sitemap · 61 pages', 'grid')]
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    y0 = 740
    for i, (lab, icn) in enumerate(labels):
        ti = t0 + 0.28 * i
        if t < ti:
            continue
        u = K.spring(t - ti, 2.8, 0.55)
        tw = G.measure(lab, 30, FU)
        w, h = int(tw + 110), 70
        x = 90
        y = y0 + i * 86
        pnl, pad = G.panel(w, h, 35, fill='#FFFFFF', fill_a=0.97, border=PLUM, border_a=0.10, shadow=0.35,
                           shadow_blur=14, shadow_dy=8)
        dx = -40 * (1 - u)
        K.draw(cv, pnl, x - pad + dx, y - pad, anchor=(0, 0), opacity=min(1, (t - ti) / 0.08) * (1 - out))
        K.draw(cv, K.disc(22, G.lin(LEAF)), x + 38 + dx, y + h / 2, opacity=(1 - out))
        K.draw(cv, ui.icon('check', 26, color='#FFFFFF', stroke=3.0), x + 38 + dx, y + h / 2, opacity=(1 - out))
        G.draw_text(cv, lab, x + 74 + dx, y + h / 2 + 11, 30, FU, INK, 'ls', opacity=(1 - out))


@functools.lru_cache(maxsize=1)
def _map_tile(w=520, h=250):
    """Abstract street-map tile (no real map data): ivory ground, pale streets, a park and a canal."""
    S = ui.Surf(w, h)
    S.rrect(0, 0, w, h, 26, G.lin('#F6EFE9'), 1.0)
    rng = np.random.default_rng(7)
    img = np.zeros((h * 2, w * 2), np.uint8)
    for _ in range(9):
        x0 = rng.uniform(-50, w * 2 + 50)
        cv2.line(img, (int(x0), -10), (int(x0 + rng.uniform(-200, 200)), h * 2 + 10), 255, 10, cv2.LINE_AA)
    for _ in range(6):
        y0 = rng.uniform(-20, h * 2 + 20)
        cv2.line(img, (-10, int(y0)), (w * 2 + 10, int(y0 + rng.uniform(-120, 120))), 255, 14, cv2.LINE_AA)
    streets = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    park = np.zeros((h, w), np.uint8)
    cv2.ellipse(park, (int(w * 0.2), int(h * 0.7)), (70, 40), 15, 0, 360, 255, -1)
    canal = np.zeros((h * 2, w * 2), np.uint8)
    pts = np.array([[0, int(h * 1.4)], [int(w * 0.6), int(h * 1.1)], [int(w * 1.3), int(h * 1.5)],
                    [w * 2, int(h * 0.9)]], np.int32)
    cv2.polylines(canal, [pts], False, 255, 16, cv2.LINE_AA)
    canal = cv2.resize(canal, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    a, X0, Y0 = S.rrect_mask(0, 0, w, h, 26)
    S.fill(a * cv2.GaussianBlur(park.astype(np.float32) / 255.0, (0, 0), 1.0), 0, 0, G.lin('#DCEBCB'), 1.0)
    S.fill(a * canal, 0, 0, G.lin('#CFE3F2'), 1.0)
    S.fill(a * streets, 0, 0, G.lin('#FFFFFF'), 1.0)
    S.img.setflags(write=False)
    return S.img


def manchester_card(cv, t, t0=15.25, t1=17.4):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    w, h = 520, 330
    cx, cy = 330, 1405 + 30 * (1 - u) + 40 * out
    pnl, pad = white_card(w, h, 32)
    K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    tile = _map_tile(470, 200)
    K.draw(cv, tile, cx, cy - 38, opacity=(1 - out) * K.ramp(t, t0 + 0.05, t0 + 0.25))
    # pin drop + ripple
    pt = t - (t0 + 0.25)
    if pt > 0:
        drop = K.EASE['out_back'](K.clamp(pt / 0.4))
        py = cy - 40 - 120 * (1 - drop)
        for k in range(2):
            ph = ((pt - 0.35) * 0.9 + k * 0.5) % 1.0 if pt > 0.35 else None
            if ph is not None:
                K.draw(cv, K.ring(18 + 60 * ph, 3, G.lin(MAG)), cx, cy - 40 + 4, scale=(1.0, 0.45),
                       opacity=(1 - ph) * (1 - out))
        pin = ui.icon('pin', 76, color=MAG, stroke=2.6, fill_a=1.0)
        K.draw(cv, pin, cx, py - 30, opacity=(1 - out))
        K.draw(cv, K.disc(9, G.lin('#FFFFFF')), cx, py - 36, opacity=(1 - out))
    op = K.ramp(t, t0 + 0.3, t0 + 0.55) * (1 - out)
    G.draw_text(cv, 'Manchester', cx - w / 2 + 34, cy + h / 2 - 52, 40, FH, INK, 'ls', opacity=op)
    G.draw_text(cv, 'Based in Old Trafford', cx - w / 2 + 34, cy + h / 2 - 18, 24, FR, '#6E5E72', 'ls', opacity=op)


def guides_card(cv, t, t0=19.55, t1=22.25):
    if not (t0 <= t < t1):
        return
    crop = (96, 196, 560, 300)
    card = G.browser_card(OF('now_blog_desktop.png'), crop, 620, 'organicfostering.co.uk/blog', accent=MAG)
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=0, soft=0.1)
    cx, cy = 540, 1290 + 30 * (1 - u) + 40 * out
    card.draw(cv, cx, cy, scale=0.95 + 0.05 * u, opacity=1 - out, mask=reveal)
    mk = K.ramp(t, 20.9, 21.7, 'inout_cubic') * (1 - out)
    if mk > 0:
        s = 620 / 560
        x0 = cx - 310 + (165 - 96) * s
        y0 = cy - card.h / 2 + 58 + (464 - 196) * s
        bw, bh = (568 - 165) * s, 28 * s
        S = ui.Surf(int(bw) + 4, int(bh) + 4)
        S.rrect(2, 2, bw, bh, 6, G.lin(PEACH), 1.0)
        m = G.wipe(S.img.shape[1], S.img.shape[0], mk, angle=0, soft=0.06)
        K.draw(cv, G.masked(S.img, m), x0, y0, anchor=(0, 0), mode='multiply')
    cu = K.spring(t - (t0 + 0.7), 2.6, 0.55) if t > t0 + 0.7 else 0
    if cu > 0:
        txt = '32 plain-English guides'
        tw = G.measure(txt, 30, FU)
        pnl, pad = G.panel(int(tw + 60), 64, 32, grad=(MAG, ORA), grad_angle=0, fill_a=1.0, border_a=0.0, shadow=0.4)
        K.draw(cv, pnl, cx + 220, cy - card.h / 2 - 10, scale=0.85 + 0.15 * cu, opacity=min(1, cu * 1.5) * (1 - out))
        G.draw_text(cv, txt, cx + 220, cy - card.h / 2 + 1, 30, FU, '#FFFFFF', 'ms', opacity=min(1, cu * 1.5) * (1 - out))


def enquiry_card(cv, t, t0=22.3, t1=25.7):
    if not (t0 <= t < t1):
        return
    crop = (60, 270, 620, 390)
    card = G.browser_card(OF('now_enquire_desktop.png'), crop, 620, 'organicfostering.co.uk/enquire', accent=MAG)
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=-90, soft=0.1)
    cx, cy = 540, 1300 + 30 * (1 - u) + 40 * out
    card.draw(cv, cx, cy, scale=0.95 + 0.05 * u, opacity=1 - out, mask=reveal)
    # cursor -> "Start your enquiry" button (centre (187, 617) in the capture)
    bx = cx - 310 + (187 - 60)
    by = cy - card.h / 2 + 58 + (617 - 270)
    if t > t0 + 0.5:
        ct = K.EASE['inout_cubic'](K.ramp(t, t0 + 0.5, 23.95, 'linear'))
        x = K.lerp(bx + 380, bx, ct)
        y = K.lerp(by - 60, by, ct)
        ui.draw_cursor(cv, x, y, 'hand', 62, press=K.impulse(t, 24.02, 9), click=t - 24.02 if t > 24.02 else None,
                       opacity=1 - out, look='airy')


def end_card(cv, t, t0=29.5):
    if t < t0:
        return
    lg = G.image_logo(LOGO, 640)
    lu = K.spring(t - (t0 + 0.1), 2.2, 0.6) if t > t0 + 0.1 else 0
    K.draw(cv, lg, 540, 700 - 30 * (1 - lu), scale=0.9 + 0.1 * lu, opacity=min(1, lu))
    G.draw_text(cv, 'organicfostering.co.uk', 540, 900, 32, FU, PLUM, 'ms', opacity=K.ramp(t, t0 + 0.3, t0 + 0.6))
    lw = 700 * K.EASE['inout_cubic'](K.ramp(t, t0 + 0.2, t0 + 0.8, 'linear'))
    if lw > 2:
        g = np.zeros((5, int(lw), 4), np.float32)
        g[..., :3] = K.gradient(int(lw), 5, [G.lin(MAG), G.lin(ORA)], angle=0)
        g[..., 3] = 1
        K.draw(cv, g, 540, 960)
    G.draw_text(cv, 'Results by', 540, 1040, 30, FB, '#6E5E72', 'ms', opacity=K.ramp(t, t0 + 0.55, t0 + 0.8))
    hu = K.spring(t - (t0 + 0.55), 2.2, 0.6) if t > t0 + 0.55 else 0
    hk = G.image_logo(HULK, 560)
    pnl, pad = G.panel(640, 130, 30, fill='#17121A', fill_a=0.96, border_a=0.0, shadow=0.35)
    K.draw(cv, pnl, 540, 1120 + 20 * (1 - hu), scale=0.92 + 0.08 * hu, opacity=min(1, hu))
    K.draw(cv, hk, 540, 1120 + 20 * (1 - hu), scale=0.92 + 0.08 * hu, opacity=min(1, hu))
    cu = K.spring(t - (t0 + 0.9), 2.4, 0.6) if t > t0 + 0.9 else 0
    txt = 'googlerankerpro.com'
    tw = G.measure(txt, 38, FH)
    pill, pp = G.panel(int(tw + 96), 84, 42, grad=(MAG, ORA), grad_angle=0, fill_a=1.0, border_a=0.0, shadow=0.4)
    K.draw(cv, pill, 540, 1270, scale=0.85 + 0.15 * cu, opacity=min(1, cu * 1.5))
    G.draw_text(cv, txt, 540, 1283, 38, FH, '#FFFFFF', 'ms', opacity=min(1, cu * 1.5))
    fp = K.ramp(t, t0 + 1.2, t0 + 1.5)
    G.draw_text(cv, 'AI re-creation of the client’s testimonial. Website shown as captured 22 Oct 2026.',
                540, 1390, 22, FR, '#6E5E72', 'ms', opacity=fp)
    G.draw_text(cv, 'Results vary by business.', 540, 1424, 22, FR, '#6E5E72', 'ms', opacity=fp)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = plate(t)
    intro_reveal(cv, t)
    # behind the speaker
    intro_card(cv, t)
    cultural_card(cv, t)
    search_card(cv, t)
    phone_card(cv, t)
    hulk_card(cv, t)
    rebuild_card(cv, t)
    tech_chips(cv, t)
    manchester_card(cv, t)
    person_over(cv, t)
    # in front
    guides_card(cv, t)
    enquiry_card(cv, t)
    pip = pip_amount(t) if T_PIP_IN <= t < T_PIP_OUT + 0.6 else 0.0
    if t < 29.4:
        G.bottom_shade(cv, 0.42, 1330, opacity=(1 - pip) * (1 - K.ramp(t, 29.1, 29.4)))
    if t < 29.45:
        p = pip_amount(t) if T_PIP_IN <= t < T_PIP_OUT + 0.6 else 0.0
        if p > 0.5:
            CAP.draw(cv, t, color=INK, shadow=0.0)
        else:
            CAP.draw(cv, t)
    if 26.2 <= t < 29.6:
        k = min(K.ramp(t, 26.2, 27.2, 'inout_sine'), 1 - K.ramp(t, 28.9, 29.6, 'inout_sine'))
        K.light_leak(cv, t, colors=[G.lin(PEACH), G.lin(ORA)], strength=0.22 * k, seed=3, speed=0.6)
    logo_bug(cv, t)
    ai_label(cv, t)
    end_card(cv, t)
    return np.ascontiguousarray(cv, dtype=np.float32)


def post(cv, t):
    cv = np.ascontiguousarray(cv, dtype=np.float32)
    K.vignette(cv, 0.14, 0.8, 1.8)
    K.grain(cv, t, 0.010, 1.2)
    cv[..., 3] = 1.0
    return cv


FAST = [(0.0, 0.8), (2.2, 2.7), (9.7, 10.05), (10.45, 10.8), (12.55, 13.35), (17.3, 17.85), (19.0, 19.8),
        (25.7, 26.4), (29.4, 30.3)]


def samples(t):
    return 3 if any(a <= t < b for a, b in FAST) else 1


# ---------------------------------------------------------------------------------------------- sound cues
def cues():
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.76, name='impact_soft', gain_db=-7),
        dict(t=0.62, name='swish_small', gain_db=-3),
        dict(t=1.02, name='pop', gain_db=-6, params=dict(pitch=1.1)),
        dict(t=2.38, name='whoosh_fast', gain_db=-9, pan=-0.4),
        dict(t=2.80, name='card_slide', gain_db=-7),
        dict(t=3.70, name='shimmer', gain_db=-15),
        dict(t=3.86, name='pop', gain_db=-4, params=dict(pitch=1.0)),
        dict(t=5.30, name='swish_small', gain_db=-5),
        dict(t=5.62, name='typing', gain_db=-10, align='start', params=dict(n=22, cps=22)),
        dict(t=6.62, name='glitch_short', gain_db=-14),
        dict(t=8.30, name='pop', gain_db=-8, params=dict(pitch=0.8)),
        dict(t=T_CUT1, name='whip', gain_db=-5),
        dict(t=10.50, name='glass_tap', gain_db=-5, pan=-0.2),
        dict(t=12.62, name='air_zoom', gain_db=-10, align='start'),
        dict(t=14.07, name='check_ding', gain_db=-11, pan=-0.4),
        dict(t=14.35, name='check_ding', gain_db=-12, pan=-0.4, params=dict(pitch=1.06)),
        dict(t=14.63, name='check_ding', gain_db=-12, pan=-0.4, params=dict(pitch=1.12)),
        dict(t=15.62, name='seed_plip', gain_db=-9, pan=0.2),
        dict(t=15.85, name='ripple', gain_db=-17, params=dict(dur=1.2)),
        dict(t=T_CUT2 + 0.02, name='air_zoom', gain_db=-10),
        dict(t=T_PIP_IN + 0.3, name='card_slide', gain_db=-7),
        dict(t=19.58, name='swish_small', gain_db=-5),
        dict(t=20.28, name='pop', gain_db=-6, params=dict(pitch=1.15)),
        dict(t=20.95, name='shimmer', gain_db=-15),
        dict(t=22.33, name='swish_small', gain_db=-5),
        dict(t=24.02, name='ui_click', gain_db=-3),
        dict(t=T_PIP_OUT + 0.35, name='whoosh_fast', gain_db=-9),
        dict(t=29.95, name='logo_sting', gain_db=-4),
        dict(t=30.42, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    _laptop_layers()
    airy_bg()
    _map_tile(470, 200)
    G.image_logo(LOGO, 520)
    G.image_logo(LOGO, 210)
    G.image_logo(LOGO, 640)
