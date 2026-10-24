"""grp2_of.py: Organic Fostering client testimonial (Google Ranker Pro), 9:16, 24 fps, 31.6 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp2_of --audio <mix.wav>

Source: workspace3/frames/of2 (Seedance clip hf_20261024_062502, 30.04 s): shot 1 interview 0-10.0 s, shot 2 desk +
laptop from behind 10.0-17.08 s, shot 3 close-up 17.08-30.04 s.
EDIT: the generated voice garbles a phrase at source 15.85-17.16 s ("...and uoating for Manchester,") while she
has her back to camera, so that stretch is cut (remap at output 15.85 s, +1.31 s); the sentence runs on as
"They rebuilt our site, fixed the technical issues, and got our local profile working for Manchester."
The same cut is applied to the dialogue in grp_audio.py.

Real material only: organicfostering.co.uk (captured 22 Oct 2026; never the homepage photo of children, no
allowance figures, no Ofsted grade, no rankings or enquiry numbers). Site facts: the homepage trust ticks, HTTPS,
responsive pages, 61 pages / 32 guides in sitemap_20261022.xml, based in Old Trafford, Manchester.
"""
import functools
import math
import os

import cv2
import numpy as np

import core as K
import footage as F
import grp_base as GB
import grp_brand as B
import grp_kit as G
import ui

DUR = 31.6
LOOK = 'natural'
BPM = 84
N_SRC = 721
CUT_OUT, CUT_OFF = 15.85, 1.31
T_END_CARD = 28.6
MAG, ORA, LEAF, PLUM, INK, PEACH = '#B7006E', '#FF6411', '#64A60B', '#5B174F', '#321F35', '#FFD4BA'
FU, FB_, FR_ = 'Poppins-SemiBold', 'Poppins-Medium', 'Poppins-Regular'
FH = 'Nunito-ExtraBold'
OF = lambda *p: G.site('organicfostering', *p)          # noqa: E731
LOGO = os.path.join(K.BRAND, 'logo_full.png')
URL = 'organicfostering.co.uk'

F.GRADES['of2_office'] = dict(wb=(1.02, 1.0, 0.98), exposure=0.03, contrast=1.10, pivot=0.42, black=0.02,
                              black_tint=(0.16, 0.11, 0.16), shadow_tint=(0.008, -0.003, 0.010),
                              highlight_tint=(0.012, 0.004, -0.010), sat=1.03, shoulder=0.92)

LAPTOP_Q = [[-20.0, 1080.0], [134.0, 1074.0], [226.0, 1268.0], [-20.0, 1325.0]]


@functools.lru_cache(maxsize=1)
def _laptop_page():
    return np.ascontiguousarray(G._rgb(OF('now_areas_desktop.png'))[:, :700, :3]).astype(np.float32)


def prep(fr, fi):
    if 240 <= fi <= 409:
        return GB.paste_quad(fr, LAPTOP_Q, _laptop_page(), feather=1.0, gain=0.93, blur=0.9)
    return fr


CLIP = GB.Clip('of2', N_SRC, [
    (0, 239, dict(c0=(0.5, 0.47), c1=(0.5, 0.45), z0=1.0, z1=1.045)),
    (240, 409, dict(c0=(0.42, 0.55), c1=(0.42, 0.55), z0=1.0, z1=1.03)),
    (410, 720, dict(c0=(0.5, 0.46), c1=(0.5, 0.45), z0=1.04, z1=1.08)),
], 'of2_office', remap=[(CUT_OUT, CUT_OFF)], prep=prep)

WORDS0 = G.load_words('of2')
WORDS = G.load_words('of2', fixes={44: None, 45: None, 46: None, 47: None, 43: 'issues,', 70: 'enquiries'},
                     retime={i: (WORDS0[i][1] - CUT_OFF, WORDS0[i][2] - CUT_OFF) for i in range(48, 85)})
CAP = B.captions(WORDS, max_chars=28)

# picture-in-picture window during the close-up
PIP_SRC = (40, 60, 1000, 1300)
PIP_S = 0.64
PIP_W, PIP_H = int(PIP_SRC[2] * PIP_S), int(PIP_SRC[3] * PIP_S)
PIP_X, PIP_Y = (1080 - PIP_W) // 2, 128
T_PIP_IN, T_PIP_OUT = 16.2, 23.95


# ---------------------------------------------------------------------------------------------- PiP
def pip_surround(t):
    """How far the surround has dissolved from the footage to the brand plate (0..1)."""
    p = pip_amount(t) if T_PIP_IN <= t < T_PIP_OUT + 0.6 else 0.0
    return K.EASE['inout_cubic'](K.clamp(p / 0.4))


def pip_amount(t):
    return min(K.EASE['inout_cubic'](K.ramp(t, T_PIP_IN, T_PIP_IN + 0.6, 'linear')),
               1 - K.EASE['inout_cubic'](K.ramp(t, T_PIP_OUT, T_PIP_OUT + 0.6, 'linear')))


@functools.lru_cache(maxsize=3)
def pip_sprite(fi, w_out, h_out):
    fr = CLIP.frame(fi)
    x, y, w, h = PIP_SRC
    sub = np.ascontiguousarray(fr[y:y + h, x:x + w])
    interp = cv2.INTER_AREA if w_out < w else cv2.INTER_CUBIC
    sub = cv2.resize(sub, (int(w_out), int(h_out)), interpolation=interp)
    return G.shot_sprite(G.sharpen_u8(sub, 0.3 if w_out < w * 0.8 else 0.2), 'of2_office')


def _pip(fi, p):
    # dissolve the surround (footage -> brand plate) over the first part of the move instead of cutting to it
    a = K.EASE['inout_cubic'](K.clamp(p / 0.4))
    out = CLIP.footage(fi).copy()
    out[..., :3] = out[..., :3] * (1 - a) + B.backdrop()[..., :3] * a
    c, z = CLIP.tf(fi)
    vw, vh = 1080 / z, 1920 / z
    x0 = c[0] * 1080 - vw / 2
    y0 = c[1] * 1920 - vh / 2
    sx, sy, sw, shh = PIP_SRC
    fx0, fy0 = (sx - x0) * z, (sy - y0) * z
    fw, fh = sw * z, shh * z
    wx, wy = K.lerp(fx0, PIP_X, p), K.lerp(fy0, PIP_Y, p)
    ww, wh = K.lerp(fw, PIP_W, p), K.lerp(fh, PIP_H, p)
    r = 44 * p
    sw_, sh_ = int(round(ww)), int(round(wh))
    spr = pip_sprite(fi, sw_, sh_)
    if p > 0.05:
        sh = ui.Surf(K.W, K.H)
        sh.rrect(wx, wy + 18, ww, wh, max(r, 0.5), (0.02, 0.10, 0.20), 1.0)
        sa = K.gblur(sh.img[..., 3], 26, border='constant') * np.float32(0.30 * p)
        out[..., :3] *= (1 - sa[..., None])
    layer = K.new_canvas()
    layer[...] = 0
    K.draw(layer, spr, wx + ww / 2, wy + wh / 2, scale=(ww / sw_, wh / sh_))
    m = G.canvas_rrect_mask(wx, wy, ww, wh, max(r, 0.5))
    out = out * (1 - m[..., None]) + layer * m[..., None]
    if p > 0.05:
        S = ui.Surf(K.W, K.H)
        S.stroke_rrect(wx, wy, ww, wh, max(r, 0.5), 3, G.lin('#FFFFFF'), 0.9 * p)
        K.over(out, S.img)
    return out


# ---------------------------------------------------------------------------------------------- pieces
def white_card(w, h, r=30):
    return G.panel(w, h, r, fill='#FFFFFF', fill_a=0.97, border=PLUM, border_a=0.10, border_w=1.5, shadow=0.40,
                   shadow_blur=24, shadow_dy=14)


def client_card(cv, t, t0=0.35, t1=2.45):
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 560, 200
    cx, cy = 540, 138 - 20 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    G.draw_text(cv, 'CLIENT STORY', cx, cy - 58, 21, B.FS, B.BODY, 'ms', opacity=op * K.ramp(t, t0 + 0.12, t0 + 0.4),
                tracking=0.2)
    lg = G.image_logo(LOGO, 360)
    m = G.wipe(lg.shape[1], lg.shape[0], K.ramp(t, t0 + 0.15, t0 + 0.6, 'out_cubic'), angle=0, soft=0.12)
    K.draw(cv, G.masked(lg, m), cx, cy + 18, opacity=1 - out)


@functools.lru_cache(maxsize=1)
def _ticks_card():
    """The homepage's three trust ticks (text only, no photos)."""
    w, h = 292, 430
    pnl, pad = white_card(w, h, 28)
    spr = pnl.copy()
    S = ui.Surf(spr.shape[1], spr.shape[0], img=spr)
    ox, oy = pad, pad
    ui.paste(spr, ui.icon('globe', 20, color=MAG, stroke=2.2), ox + 22, oy + 26)
    S.text(ox + 48, oy + 43, URL, 17, FB_, PLUM)
    S.rrect(ox + 22, oy + 64, w - 44, 1.5, 0, G.lin(PLUM), 0.15)
    rows = [('Independent', 'Fostering Agency'), ('Cultural Matching', 'Specialists'), ('Informal First', 'Conversation')]
    for i, (l1, l2) in enumerate(rows):
        y = oy + 92 + i * 112
        S.circle(ox + 36, y + 23, 17, G.lin(LEAF), 1.0)
        ui.paste(spr, ui.icon('check', 21, color='#FFFFFF', stroke=3.0), ox + 26, y + 13)
        S.text(ox + 64, y + 22, l1, 22, FU, INK)
        S.text(ox + 64, y + 53, l2, 22, FU, INK)
    spr.setflags(write=False)
    return spr, pad, w, h


def ticks_card(cv, t, t0=2.75, t1=5.75):
    """Left of her, partly behind her shoulder: the site's trust ticks; 'Cultural Matching' lights up."""
    if not (t0 <= t < t1):
        return
    spr, pad, w, h = _ticks_card()
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    x0, y0 = 24, 420 + 30 * (1 - u) + 40 * out
    m = np.zeros(spr.shape[:2], np.float32)
    m[pad:pad + h, pad:pad + w] = G.wipe(w, h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=-90, soft=0.1)
    m = np.maximum(m, K.gblur(m, 16, border='constant'))
    K.draw(cv, G.masked(spr, m), x0 - pad, y0 - pad, anchor=(0, 0), opacity=1 - out)
    hl = K.ramp(t, 4.6, 5.0, 'out_cubic') * (1 - out)
    if hl > 0:
        ry = y0 + 92 + 112 - 14
        S = ui.Surf(w - 20, 98)
        S.rrect(2, 2, w - 24, 94, 18, G.lin(PEACH), 1.0)
        mm = G.wipe(S.img.shape[1], S.img.shape[0], hl, angle=0, soft=0.06)
        K.draw(cv, G.masked(S.img, mm), x0 + 10, ry, anchor=(0, 0), mode='multiply')
        ring = ui.Surf(w - 4, 114)
        ring.stroke_rrect(4, 4, w - 12, 106, 22, 3, G.lin(MAG), 1.0)
        K.draw(cv, ring.img, x0 + 2, ry - 8, anchor=(0, 0), opacity=K.ramp(t, 4.9, 5.2) * (1 - out))


def search(cv, t, t0=6.0, t1=8.4):
    shake = 0.0
    if t > 7.5:
        shake = 10 * math.sin((t - 7.5) * 38) * math.exp(-(t - 7.5) * 6)
    B.search_bar(cv, t, 'foster agency Manchester', t0, t1, cx=540 + shake, cy=215, w=780, h=100, type_dur=1.0,
                 size=36)


def phone_card(cv, t, t0=8.6, t1=9.80):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.6, 0.55)
    out = K.ramp(t, t1 - 0.22, t1, 'in_cubic')
    cx, cy = 935, 560 + 20 * (1 - u)
    K.draw(cv, K.disc(66, G.lin('#FFFFFF')), cx, cy, scale=0.8 + 0.2 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    tilt = -8 + 3 * math.sin((t - t0) * 2.0)
    K.draw(cv, ui.icon('phone', 62, color='#8A93A0', stroke=2.4), cx, cy, rot=tilt,
           opacity=K.ramp(t, t0 + 0.05, t0 + 0.25) * (1 - out))
    lw = 190 * K.ramp(t, t0 + 0.2, t0 + 0.8, 'out_cubic')
    if lw > 2:
        bar = np.zeros((4, int(lw), 4), np.float32)
        bar[..., :3] = 1.0
        bar[..., 3] = 1.0
        K.draw(cv, bar, cx, cy + 100, opacity=0.85 * (1 - out))


def grp(cv, t, t0=10.6, t1=12.75):
    GB.card_in(cv, B.grp_card(470, 190), t, t0, t1, 330, 300, rise=36)


def _card_body(card):
    p = card.pad
    return np.ascontiguousarray(card.spr[p:p + card.h, p:p + card.w])


@functools.lru_cache(maxsize=1)
def _rebuild_card():
    return G.browser_card(OF('now_areas_desktop.png'), (0, 0, 1440, 900), 600, URL + '/areas-we-cover',
                          url_font='Inter-Medium')


def rebuild_card(cv, t, t0=13.05, t1=15.85):
    """'They rebuilt our site': the page on the laptop lifts off into a floating browser window."""
    if not (t0 <= t < t1):
        return
    card = _rebuild_card()
    body = _card_body(card)
    u = K.EASE['inout_cubic'](K.ramp(t, t0, t0 + 0.65, 'linear'))
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    w, h = card.w, card.h
    cx, cy = 340, 395 - 40 * out
    target = np.float32([[cx - w / 2, cy - h / 2], [cx + w / 2, cy - h / 2], [cx + w / 2, cy + h / 2],
                         [cx - w / 2, cy + h / 2]])
    c, z = CLIP.tf(CLIP.fi(t))
    vw, vh = 1080 / z, 1920 / z
    ox, oy = c[0] * 1080 - vw / 2, c[1] * 1920 - vh / 2
    src = (np.float32(LAPTOP_Q) - np.float32([ox, oy])) * z
    q = src * (1 - u) + target * u
    if u > 0.02:
        sh = np.zeros((h + 80, w + 80, 4), np.float32)
        S = ui.Surf(w + 80, h + 80, img=sh)
        S.rrect(40, 52, w, h, 26, (0.02, 0.06, 0.12), 1.0)
        sh[..., 3] = K.gblur(sh[..., 3], 22, border='constant') * 0.40
        sh[..., :3] = 0
        K.draw(cv, sh, cx, cy + 6, opacity=u * (1 - out))
    K.draw_quad(cv, body, [tuple(p) for p in q], opacity=(0.3 + 0.7 * u) * (1 - out))


CHIPS = [('Secure HTTPS', 'shield'), ('Mobile-friendly pages', 'check'), ('Sitemap · 61 pages', 'grid')]


def tech_chips(cv, t, t0=14.6, t1=15.85):
    """'...fixed the technical issues': three facts checked on the live site, under the card (clear of the mug)."""
    for i, (lab, icn) in enumerate(CHIPS):
        B.draw_chip(cv, t, lab, 50, 676 + i * 78, t0 + 0.22 * i, t1, icon=icn, size=28, anchor='l',
                    icon_color=LEAF, rise=0)


@functools.lru_cache(maxsize=1)
def _map_tile(w=520, h=230):
    """Abstract street-map tile (no real map data)."""
    S = ui.Surf(w, h)
    S.rrect(0, 0, w, h, 24, G.lin('#EEF4F8'), 1.0)
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
    a, X0, Y0 = S.rrect_mask(0, 0, w, h, 24)
    S.fill(a * cv2.GaussianBlur(park.astype(np.float32) / 255.0, (0, 0), 1.0), 0, 0, G.lin('#DCEBCB'), 1.0)
    S.fill(a * canal, 0, 0, G.lin('#CFE3F2'), 1.0)
    S.fill(a * streets, 0, 0, G.lin('#FFFFFF'), 1.0)
    S.img.setflags(write=False)
    return S.img


def manchester_card(cv, t, t0=16.45, t1=18.9):
    """'...and got our local profile working for Manchester' (no profile data shown: the base, from the site)."""
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    w, h = 600, 380
    cx, cy = 540, 1250 + 30 * (1 - u) + 30 * out
    pnl, pad = B.card(w, h, 32)
    K.draw(cv, pnl, cx, cy, scale=0.92 + 0.08 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    tile = _map_tile(552, 230)
    K.draw(cv, tile, cx, cy - 52, opacity=(1 - out) * K.ramp(t, t0 + 0.05, t0 + 0.25))
    pt = t - (t0 + 0.25)
    if pt > 0:
        drop = K.EASE['out_back'](K.clamp(pt / 0.4))
        py = cy - 52 - 120 * (1 - drop)
        for k in range(2):
            ph = ((pt - 0.35) * 0.9 + k * 0.5) % 1.0 if pt > 0.35 else None
            if ph is not None:
                K.draw(cv, K.ring(18 + 60 * ph, 3, G.lin(B.ACTION)), cx, cy - 52 + 4, scale=(1.0, 0.45),
                       opacity=(1 - ph) * (1 - out))
        K.draw(cv, ui.icon('pin', 76, color=MAG, stroke=2.6, fill_a=1.0), cx, py - 30, opacity=(1 - out))
        K.draw(cv, K.disc(9, G.lin('#FFFFFF')), cx, py - 36, opacity=(1 - out))
    op = K.ramp(t, t0 + 0.3, t0 + 0.55) * (1 - out)
    G.draw_text(cv, 'Manchester', cx - w / 2 + 34, cy + h / 2 - 58, 42, B.FB, B.INK, 'ls', opacity=op)
    G.draw_text(cv, 'Based in Old Trafford', cx - w / 2 + 34, cy + h / 2 - 22, 25, B.FM, B.BODY, 'ls', opacity=op)
    G.draw_text(cv, 'Local search', cx + w / 2 - 34, cy + h / 2 - 22, 25, B.FS, B.ACTION, 'rs', opacity=op)


def guides_card(cv, t, t0=19.15, t1=21.75):
    if not (t0 <= t < t1):
        return
    crop = (96, 196, 560, 300)
    card = G.browser_card(OF('now_blog_desktop.png'), crop, 640, URL + '/blog', url_font='Inter-Medium')
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=0, soft=0.1)
    cx, cy = 540, 1262 + 30 * (1 - u) + 40 * out
    card.draw(cv, cx, cy, scale=0.95 + 0.05 * u, opacity=1 - out, mask=reveal)
    cu = K.spring(t - (t0 + 0.6), 2.6, 0.55) if t > t0 + 0.6 else 0
    if cu > 0:
        txt = '32 plain-English guides'
        tw = G.measure(txt, 30, B.FS)
        pnl, pad = G.panel(int(tw + 60), 64, 32, fill=B.ACTION, fill_a=1.0, border_a=0.0, shadow=0.4)
        K.draw(cv, pnl, cx + 200, cy - card.h / 2 - 8, scale=0.85 + 0.15 * cu, opacity=min(1, cu * 1.5) * (1 - out))
        G.draw_text(cv, txt, cx + 200, cy - card.h / 2 + 3, 30, B.FS, '#FFFFFF', 'ms',
                    opacity=min(1, cu * 1.5) * (1 - out))


def enquiry_card(cv, t, t0=21.85, t1=24.25):
    if not (t0 <= t < t1):
        return
    crop = (60, 270, 620, 390)
    card = G.browser_card(OF('now_enquire_desktop.png'), crop, 620, URL + '/enquire', url_font='Inter-Medium')
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=-90, soft=0.1)
    cx, cy = 540, 1272 + 30 * (1 - u) + 40 * out
    card.draw(cv, cx, cy, scale=0.95 + 0.05 * u, opacity=1 - out, mask=reveal)
    bx = cx - 310 + (187 - 60)
    by = cy - card.h / 2 + 58 + (617 - 270)
    tc = t0 + 1.35
    if t > t0 + 0.5:
        ct = K.EASE['inout_cubic'](K.ramp(t, t0 + 0.5, tc - 0.05, 'linear'))
        x = K.lerp(bx + 380, bx, ct)
        y = K.lerp(by - 60, by, ct)
        ui.draw_cursor(cv, x, y, 'hand', 62, press=K.impulse(t, tc, 9), click=t - tc if t > tc else None,
                       opacity=1 - out, look='airy')


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    fi = CLIP.fi(t)
    cv = CLIP.plate(t, {0: 'band', 1: 'grow'}, end_t0=T_END_CARD - 0.15)
    p = pip_amount(t) if T_PIP_IN <= t < T_PIP_OUT + 0.6 else 0.0
    if p > 0:
        cv = _pip(fi, p)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        client_card(cv, t)
        ticks_card(cv, t)
        search(cv, t)
        phone_card(cv, t)
        grp(cv, t)
        rebuild_card(cv, t)
        tech_chips(cv, t)
        CLIP.person_over(cv, t, skip=[(-1.0, 0.8), (T_PIP_IN, T_PIP_OUT + 0.6)])
        manchester_card(cv, t)
        guides_card(cv, t)
        enquiry_card(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=(1 - p) * (1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD)))
        cap_k = 1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine')
        if pip_surround(t) > 0.5:
            CAP.draw(cv, t, color=B.INK, shadow=0.0, opacity=cap_k)
        else:
            CAP.draw(cv, t, opacity=cap_k)
        if 24.6 <= t < T_END_CARD:
            k = min(K.ramp(t, 24.6, 25.6, 'inout_sine'), 1 - K.ramp(t, T_END_CARD - 0.7, T_END_CARD, 'inout_sine'))
            K.light_leak(cv, t, colors=[G.lin(PEACH), G.lin(ORA)], strength=0.18 * k, seed=3, speed=0.6)
        B.logo_bug(cv, t, 2.5, T_END_CARD)
    B.ai_label(cv, t, solid=(T_PIP_IN + 0.3 < t < T_PIP_OUT + 0.3) or t >= T_END_CARD)
    B.end_card(cv, t, T_END_CARD, 'Organic Fostering', URL)
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8), (9.8, 10.2), (13.0, 13.8), (CUT_OUT - 0.2, CUT_OUT + 0.4), (T_PIP_IN, T_PIP_IN + 0.7),
        (T_PIP_OUT, T_PIP_OUT + 0.7), (T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.76, name='impact_soft', gain_db=-8),
        dict(t=0.40, name='pop', gain_db=-6, params=dict(pitch=1.05)),
        dict(t=2.80, name='card_slide', gain_db=-7, pan=-0.4),
        dict(t=4.62, name='shimmer', gain_db=-15, pan=-0.4),
        dict(t=4.95, name='pop', gain_db=-5, params=dict(pitch=1.0), pan=-0.4),
        dict(t=6.02, name='swish_small', gain_db=-6),
        dict(t=6.35, name='typing', gain_db=-10, align='start', params=dict(n=22, cps=22)),
        dict(t=7.50, name='glitch_short', gain_db=-15),
        dict(t=8.62, name='pop', gain_db=-8, params=dict(pitch=0.8), pan=0.4),
        dict(t=10.0, name='whip', gain_db=-6),
        dict(t=10.62, name='pop', gain_db=-6, params=dict(pitch=1.1), pan=-0.3),
        dict(t=13.07, name='air_zoom', gain_db=-10, align='start'),
        dict(t=14.62, name='check_ding', gain_db=-11, pan=-0.4),
        dict(t=14.84, name='check_ding', gain_db=-12, pan=-0.4, params=dict(pitch=1.06)),
        dict(t=15.06, name='check_ding', gain_db=-12, pan=-0.4, params=dict(pitch=1.12)),
        dict(t=CUT_OUT + 0.02, name='air_zoom', gain_db=-10),
        dict(t=T_PIP_IN + 0.3, name='card_slide', gain_db=-7),
        dict(t=16.72, name='seed_plip', gain_db=-9),
        dict(t=16.95, name='ripple', gain_db=-17, params=dict(dur=1.2)),
        dict(t=19.17, name='swish_small', gain_db=-5),
        dict(t=19.80, name='pop', gain_db=-6, params=dict(pitch=1.15)),
        dict(t=21.87, name='swish_small', gain_db=-5),
        dict(t=23.20, name='ui_click', gain_db=-3),
        dict(t=T_PIP_OUT + 0.35, name='whoosh_fast', gain_db=-9),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _laptop_page()
    _ticks_card()
    _rebuild_card()
    _map_tile(552, 230)
    G.image_logo(LOGO, 360)
    B.grp_card(470, 190)
