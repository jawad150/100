"""pehle_wala_ui.py - the dark-glass REVIEW PLAYER of reel C26 and everything on it except the ad (owner:
motion-timeline-builder): window, version counter, status / clock chips, the client's (and Owner ki Mummy's) pins,
cards, leader lines, collapsed dots, the version drawer, the hover / payoff marker, the Ctrl+Z chip. Static sprites
are built once per process (lru_cache); every draw is a pure function of the state dict (pehle_wala_state.state).

Layout (BRIEF 5.1 / 6.1 / 6.3, HANDOFF D2): player body x 80-1000, y 236-1268 (ui.app_window 920 x 1032, title
'ubaal_chai_ad.mp4', header 'Review · POV'); counter chip centre (908, 280) 140 x 60, T.Counter jw_mono 56 'v';
status chip right edge x 960, y 404 ('Approved' 272 x 64 EMBER -> PLUM, 'Changes requested' 400 x 64); clock chip
'3:47 AM' (836, 512); pin cards = glass card r 24 (name jw_mono 34 ASH at inset (28, 22), text jw_body 44 IVORY,
baseline inset 26; w = max(text, name) + 56, h 118 / 170 (two lines) / 84 (thread follow-ups) / 126 (payoff 56 px));
marker = 44 px NIGHT_1 disc, 4 px ring (client FLAME x1.8, Mummy GOLD x1.6), 'C' / 'M' jw_caps_bold 26, 12 px pointer,
disc centre = tip + (0, -34); 2 px FLAME leader (alpha 0.6); collapsed marker = 14 px dot; drawer 760 x 300 centre
(540, 1060), rows y 960 / 1022 / 1084 / 1146 (80 x 46 thumbnail + jw_mono 40 filename); Ctrl+Z chip 410 x 96 r 24
centre (540, 1388) with 'Ctrl+Z ×26' jw_mono 56.

    import pehle_wala_ui as UI
    UI.draw_window(cv, dx, dy); UI.draw_ui(cv, st, dx, dy)      # dx, dy = the player-layer shake (state)
    UI.draw_ctrlz(cv, t)                                         # outside W_core (never rewinds)
    UI.marker(cv, (tip_x, tip_y), who, opacity, sx, sy)          # the review pin (also used for pre1)
"""
import functools
import math

import jawad_kit                                   # noqa: F401  FIRST
from jawad_kit import K, T, ui
import jawad_grade as G                           # noqa: F401  registers 'inferno'

import cv2
import numpy as np

import pehle_wala_state as S
import pehle_wala_ad as AD

LOOK = 'inferno'
WIN_XY = (80, 236)
lin = AD.lin
ro = AD.ro


# ============================================================================================ window + chips + counter
@functools.lru_cache(maxsize=1)
def window():
    return ui.app_window(w=920, h=1032, look=LOOK, title='ubaal_chai_ad.mp4', header='Review · POV', sidebar=False,
                         header_size=52)


def draw_window(cv, dx=0.0, dy=0.0):
    window().draw(cv, WIN_XY[0] + dx, WIN_XY[1] + dy, anchor=(0, 0))


@functools.lru_cache(maxsize=1)
def counter_card():
    return ui.glass_card(140, 60, r=18, look=LOOK, shadow=0.4)


@functools.lru_cache(maxsize=1)
def counter_obj():
    return T.Counter('jw_mono', prefix='v', decimals=0, px=56)


@functools.lru_cache(maxsize=32)
def counter_static(v):
    return counter_obj().sprite(float(v), 0.0)


def draw_counter(cv, st, dx, dy, vel=0.0):
    counter_card().draw(cv, 908 + dx, 280 + dy)
    v = st['counter']
    if abs(v - round(v)) < 1e-4 and abs(vel) < 1e-3:
        spr = counter_static(int(round(v)))
    else:
        spr = counter_obj().sprite(v, vel)
    spr.draw(cv, 908 + dx, 280 + dy, snap=False)


@functools.lru_cache(maxsize=4)
def chip_spr(name):
    if name == 'Approved':
        return ui.chip('Approved', sel=1.0, look=LOOK, size=34, h=64, icon_name='check', pad_x=26, grad=('EMBER', 'PLUM'))
    if name == 'Changes requested':
        return ui.chip('Changes requested', sel=0.0, look=LOOK, size=34, h=64, pad_x=26)
    if name == 'clock':
        return ui.chip('3:47 AM', sel=0.0, look=LOOK, size=34, h=56, icon_name='clock', pad_x=22)
    raise KeyError(name)


CHIP_W = {'Approved': 272, 'Changes requested': 400}


def draw_status(cv, st, dx, dy):
    name, k = st['chip']
    cx = 960 - CHIP_W[name] / 2.0
    ui.place(cv, chip_spr(name), cx + dx, 404 + dy, scale=k)


def draw_clock(cv, st, dx, dy):
    c = st['clock']
    if c is None:
        return
    k, op, ddy = c
    if op > 1e-3:
        ui.place(cv, chip_spr('clock'), 836 + dx, 512 + ddy + dy, scale=k, opacity=op)


# ============================================================================================ markers, dots, lines
MS = 2.0                                           # markers are built at 2x for crisp squash


@functools.lru_cache(maxsize=4)
def marker_spr(who):
    """Review pin: NIGHT_1 disc r 22, 4 px ring, initial, 12 px pointer; returns (sprite at 2x, tip anchor)."""
    ring_col = lin('FLAME', 1.8) if who == 'C' else lin('GOLD', 1.6)
    s = MS
    W_, H_ = int(120 * s), int(140 * s)
    tip = (W_ / 2.0, H_ - 24 * s)
    cx, cy = tip[0], tip[1] - 34 * s
    spr = np.zeros((H_, W_, 4), np.float32)
    tri = AD.poly_mask([(cx - 9 * s, cy + 12 * s), (cx + 9 * s, cy + 12 * s), (tip[0], tip[1])], W_, H_)
    spr += AD.rgba(tri, ring_col * 0.85)
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    disc = np.clip(22 * s - d + 0.5, 0, 1)
    ring = np.clip(2 * s + 0.5 - np.abs(d - 20 * s), 0, 1)
    body = AD.rgba(disc, lin('NIGHT_1'))
    spr = body + spr * (1 - disc[..., None])
    spr = spr * (1 - ring[..., None]) + AD.rgba(ring, ring_col)
    g = K.glow(np.ascontiguousarray(AD.rgba(np.maximum(ring, tri * 0.6), ring_col / 1.8)), None, sigmas=(3 * s, 10 * s),
               strength=0.5, include=False)
    pad = (g.shape[0] - H_) // 2
    full = np.array(g, copy=True)
    reg = full[pad:pad + H_, pad:pad + W_]
    reg *= 1 - spr[..., 3:4]
    reg += spr
    T.render('C' if who == 'C' else 'M', 'jw_caps_bold', px=26 * s).draw(full, cx + pad, cy + pad + 0.5 * s, snap=False)
    anchor = ((tip[0] + pad) / full.shape[1], (tip[1] + pad) / full.shape[0])
    return ro(full), anchor


def marker(cv, tip, who='C', opacity=1.0, sx=1.0, sy=1.0):
    if opacity <= 1e-3:
        return
    spr, an = marker_spr(who)
    K.draw(cv, spr, tip[0], tip[1], scale=(sx / MS, sy / MS), anchor=an, opacity=opacity)


@functools.lru_cache(maxsize=4)
def dot_spr(who):
    col = lin('FLAME', 1.6) if who == 'C' else lin('GOLD', 1.5)
    d = K.disc(7.0, col)
    return ro(K.glow(d, col / 1.6, sigmas=(3, 8), strength=0.45))


def draw_dot(cv, x, y, who, opacity):
    if opacity > 1e-3:
        K.draw(cv, dot_spr(who), x, y, opacity=opacity)


def line(cv, p0, p1, width=2.0, col=None, opacity=0.6):
    """Anti-aliased line segment (premultiplied over), sub-pixel accurate."""
    col = lin('FLAME', 1.2) if col is None else col
    x0, y0 = p0
    x1, y1 = p1
    m = width + 2
    X0, Y0 = int(max(0, math.floor(min(x0, x1) - m))), int(max(0, math.floor(min(y0, y1) - m)))
    X1, Y1 = int(min(cv.shape[1], math.ceil(max(x0, x1) + m))), int(min(cv.shape[0], math.ceil(max(y0, y1) + m)))
    if X1 <= X0 or Y1 <= Y0:
        return
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 < 1e-6:
        return
    u = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    d = np.sqrt((xx - x0 - u * dx) ** 2 + (yy - y0 - u * dy) ** 2)
    a = np.clip(width / 2 + 0.5 - d, 0, 1) * np.float32(opacity)
    reg = cv[Y0:Y1, X0:X1]
    reg *= 1 - a[..., None]
    reg[..., :3] += a[..., None] * col
    reg[..., 3] += a


def leader(cv, disc_c, rect, opacity):
    """2 px FLAME leader (alpha 0.6) from the disc edge to the nearest edge of the card rect (x0, y0, x1, y1)."""
    if opacity <= 1e-3:
        return
    cx, cy = disc_c
    x0, y0, x1, y1 = rect
    nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
    vx, vy = nx - cx, ny - cy
    L = math.hypot(vx, vy)
    if L < 24.0:
        return
    sx, sy = cx + vx / L * 23.0, cy + vy / L * 23.0
    line(cv, (sx, sy), (nx, ny), 2.0, None, 0.6 * opacity)


# ============================================================================================ cards
def card_text(lines, px):
    return [T.render(ln, 'jw_body', px=px) for ln in lines]


@functools.lru_cache(maxsize=None)
def card_panel(lines, name, w=None, h=None, px=44):
    """Glass card with the note baked into its face -> (Panel, w, h)."""
    ts = card_text(lines, px)
    nm = T.render(name, 'jw_mono', px=34, fill='ASH') if name else None
    if w is None:
        w = int(math.ceil(max([t.w for t in ts] + ([nm.w] if nm else [])) + 56))
    if h is None:
        h = 84 if not nm else (118 if len(ts) == 1 else 170)
        if px > 44:
            h = 126
    base = ui.glass_card(int(w), int(h), r=24, look=LOOK, shadow=0.5)
    f = base.copy()
    p = base.pad
    if nm:
        nm.draw(f, p + 28, p + 22, anchor=(0, 0), opacity=0.92)
    pitch = 52
    for j, t in enumerate(ts):
        yb = h - 26 - pitch * (len(ts) - 1 - j)
        t.draw(f, p + 28, p + yb, anchor=(0, 1))
    return ui.derive_panel(base, f), int(w), int(h)


def pin_card(i):
    n, v, fl, who, lines, tip, card = S.PINS[i]
    return card_panel(lines, 'Client')


def payoff_card():
    return card_panel(S.PAYOFF[4], 'Client', px=56)


def thread_card(n):
    p = [q for q in S.THREAD if q[0] == n][0]
    x0, y0, x1, y1 = p[6]
    return card_panel(p[4], 'Owner ki Mummy' if n == 11 else None, w=x1 - x0, h=y1 - y0)


def _draw_card(cv, panel, cx, cy, k, op):
    if op > 1e-3:
        panel.draw(cv, cx, cy, scale=k, opacity=op)


# ============================================================================================ drawer (v24 .. v27)
DRAWER_C = (540.0, 1060.0)
DRAWER_W, DRAWER_H = 760, 300
ROWS = (('v24_final.mp4', 24, 960), ('v25_FINAL.mp4', 25, 1022), ('v26_final_final.mp4', 26, 1084),
        ('v27_ab_pakka_final.mp4', 27, 1146))
THUMB_X = 212                                      # screen x of the thumbnail's left edge (80 x 46)
NAME_X = 308                                       # filename left edge (16 px after the thumbnail)


@functools.lru_cache(maxsize=1)
def drawer_panel():
    base = ui.glass_card(DRAWER_W, DRAWER_H, r=24, look=LOOK, shadow=0.6)
    f = base.copy()
    p = base.pad
    x0, y0 = DRAWER_C[0] - DRAWER_W / 2, DRAWER_C[1] - DRAWER_H / 2
    for name, v, y in ROWS[:3]:
        _row(f, p + THUMB_X - x0, p + y - y0, name, v)
    return ui.derive_panel(base, f)


def _row(dst, tx, cy, name, v, opacity=1.0, hot=False):
    th = AD.thumb(v)
    K.draw(dst, th, tx, cy, anchor=(0, 0.5), opacity=opacity)
    ts = T.render(name, 'jw_mono', px=40, fill=('AMBER', 1.0) if hot else ('IVORY', 0.86))
    ts.draw(dst, tx + 96, cy, anchor=(0, 0.5), opacity=opacity, snap=False)


def draw_drawer(cv, st, dx, dy):
    d = st['drawer']
    if d is None or d['op'] <= 1e-3:
        return
    cx, cy = DRAWER_C[0] + dx, DRAWER_C[1] + d['dy'] + dy
    k = d['k']
    drawer_panel().draw(cv, cx, cy, scale=k, opacity=d['op'])
    if d['r4o'] > 1e-3:                            # row v27 slides in (x +60, 6 f out_cubic)
        name, v, y = ROWS[3]
        ox = 60.0 * (1.0 - d['r4'])
        rx = cx + (THUMB_X + ox - DRAWER_C[0]) * k
        ry = cy + (y - DRAWER_C[1]) * k
        tmp_op = d['op'] * d['r4o']
        th = AD.thumb(v)
        K.draw(cv, th, rx, ry, scale=k, anchor=(0, 0.5), opacity=tmp_op)
        T.render(name, 'jw_mono', px=40, fill=('AMBER', 1.0)).draw(cv, rx + 96 * k, ry, anchor=(0, 0.5), scale=k,
                                                                     opacity=tmp_op, snap=False)


# ============================================================================================ Ctrl+Z chip (D9)
@functools.lru_cache(maxsize=1)
def ctrlz_panel():
    base = ui.glass_card(410, 96, r=24, look=LOOK, shadow=0.5)
    f = base.copy()
    p = base.pad
    T.render('Ctrl+Z ×26', 'jw_mono', px=56).draw(f, p + 205, p + 48)
    return ui.derive_panel(base, f)


def draw_ctrlz(cv, t):
    """'Ctrl+Z ×26' chip: POP in at f784 (solid from f784), exit f832-f838 (in_cubic, scale 0.92, y +16)."""
    if not S.on(t, 783) or S.on(t, 839):
        return
    d = t - 784 / 30.0
    op = S.ease('inout_sine', (t - 783 / 30.0) / (3 / 30.0))
    k = 0.86 + 0.14 * S.spring(d + 1 / 30.0, 'POP')
    ex = S.ease('in_cubic', (t - 832 / 30.0) / (6 / 30.0))
    op *= 1.0 - ex
    if op > 1e-3:
        ctrlz_panel().draw(cv, 540, 1388 + 16 * ex, scale=k * (1 - 0.08 * ex), opacity=op)


# ============================================================================================ the UI layer
def card_rect(cx, cy, w, h, k=1.0):
    return (cx - w * k / 2, cy - h * k / 2, cx + w * k / 2, cy + h * k / 2)


def draw_ui(cv, st, dx=0.0, dy=0.0, counter_vel=0.0):
    """Everything on the player except the window and the ad (in z-order)."""
    draw_counter(cv, st, dx, dy, counter_vel)
    draw_status(cv, st, dx, dy)
    draw_clock(cv, st, dx, dy)
    for x, y, who, op in st['dots']:
        draw_dot(cv, x + dx, y + dy, who, op)
    for p in st['pins']:
        m = p['marker']
        if p['who'] == 'M':
            continue
        if p['card'] is not None:
            panel, w, h = pin_card(p['i'])
            cx, cy, k, op = p['card']
            if m is not None:
                leader(cv, (m[0] + dx, m[1] - S.DISC_UP * m[4] + dy), card_rect(cx + dx, cy + dy, w, h, k), op * m[2])
            _draw_card(cv, panel, cx + dx, cy + dy, k, op)
        if m is not None:
            marker(cv, (m[0] + dx, m[1] + dy), 'C', m[2], m[3], m[4])
    # Owner ki Mummy's thread (one GOLD marker, stacked cards)
    cards, cu = st['thread']
    mm = [p for p in st['pins'] if p['who'] == 'M']
    if mm:
        m = mm[0]['marker']
        if cards and m is not None:
            r0 = cards[0][0]
            leader(cv, (m[0] + dx, m[1] - S.DISC_UP * m[4] + dy), (r0[0] + dx, r0[1] + dy, r0[2] + dx, r0[3] + dy),
                   cards[0][3] * m[2])
        for (x0, y0, x1, y1), lines, k, op, first in cards:
            n = [q[0] for q in S.THREAD if q[6] == (x0, y0, x1, y1)][0]
            panel, w, h = thread_card(n)
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            if cu > 0:                             # the thread folds into Mummy's marker
                tx, ty = S.MUMMY_TIP[0], S.MUMMY_TIP[1] - S.DISC_UP
                cx, cy = cx + (tx - cx) * cu * 0.6, cy + (ty - cy) * cu * 0.6
            _draw_card(cv, panel, cx + dx, cy + dy, k, op)
        if m is not None:
            marker(cv, (m[0] + dx, m[1] + dy), 'M', m[2], m[3], m[4])
    draw_drawer(cv, st, dx, dy)
    h = st['hover']
    if h is not None:
        marker(cv, (h[0] + dx, h[1] + dy), 'C', h[2], h[3], h[4])
    po = st['payoff']
    if po is not None:
        m = po['marker']
        cx, cy, k, op = po['card']
        panel, w, h_ = payoff_card()
        leader(cv, (m[0] + dx, m[1] - S.DISC_UP * m[4] + dy), card_rect(cx + dx, cy + dy, w, h_, k), op)
        _draw_card(cv, panel, cx + dx, cy + dy, k, op)
        marker(cv, (m[0] + dx, m[1] + dy), 'C', m[2], m[3], m[4])


def prewarm():
    window()
    counter_card()
    counter_obj()
    for v in range(1, 28):
        counter_static(v)
    for nm in ('Approved', 'Changes requested', 'clock'):
        chip_spr(nm)
    for who in ('C', 'M'):
        marker_spr(who)
        dot_spr(who)
    for i, p in enumerate(S.PINS):
        if p[3] == 'C':
            pin_card(i)
        else:
            thread_card(p[0])
    payoff_card()
    drawer_panel()
    for v in (24, 25, 26, 27):
        AD.thumb(v)
    ctrlz_panel()
