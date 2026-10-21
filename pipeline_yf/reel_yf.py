"""Organic Fostering — "Your Year in Fostering" (9:16, 30 s): a year-in-review story recap of a foster carer's year.

Phone notification "Your Year in Fostering is ready" -> tap Play, gradient burst -> six full-screen story cards that
swipe with a 3D cube turn (flat brand colours, oversized Poppins, glossy 3D clay icons, story progress bar) ->
cards fan out into a grid and shuffle into "Your 2027 story · Not started yet" -> tap "Start your story" ->
"Enquiry started" -> OF logo end card.
Reuses the phone, glass, cursor and type helpers from reel_su.py.

Usage:
  python3 reel_yf.py still 1.0,5.0
  python3 reel_yf.py range 0 900
"""
import os, sys, math, functools
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['REEL_WORKDIR'] = os.path.abspath(os.path.join(HERE, '..', 'workspace_yf'))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_su'))
import numpy as np
import cv2
import reel_su as RS
from reel_su import (paste, fitted, png, txt, icon3d, title, bg, neon_card, ripple, sparks, cursor, confetti, icon_disc,
                     wallpaper, padlock, phone_spr, draw_phone, PW, PH, SW, SH, PINK, GOLD, INK,
                     PB, PX, PK, PS, PM, PR, PL)
from reel_of import kinetic_line, word_spr, sweep, glow_add, whip, zoom_blur, shake, check_spr, rrect_spr, \
    PLUM, MAGENTA, ORANGE_B, GREEN, PEACH, MUTEDC, WHITE_
from engine import *  # noqa: F401,F403
import engine as E

S = E.S
FPS = 30
CREAM = hexc('#FFF4E8')
OFF = (1, 1, 1, 0.82)

# ------------------------------------------------------------------ timeline (120 BPM grid)
C = [3.0, 5.65, 8.3, 10.95, 13.6, 16.25]          # card starts; card 6 holds longest
T = dict(hook=0.0, turn=21.6, cta=25.5)
DUR = 30.0
NF = int(DUR * FPS)
VO = {'hook': 0.1, 'c1': 3.35, 'c2': 6.0, 'c3': 8.6, 'c4': 11.25, 'c6': 16.4, 'turn': 21.95, 'cta': 25.5}
NOTIF = 0.55
TAP_PLAY = 2.2
SWIPE = 0.45
STORY_T = T['turn'] + 2.0                          # "Your 2027 story" card lands
BTN_T = T['turn'] + 2.5
TAP_CTA = T['cta'] + 0.4
FLIP_T = TAP_CTA + 0.2
LOGO_T = TAP_CTA + 1.25
FADE = 1.25

CARDS = [  # (bg colour, label, ink)
    (hexc('#5B174F'), 'YOUR TOP MOMENT', CREAM),
    (hexc('#FF6411'), 'YOUR MOST-PLAYED PHRASE', CREAM),
    (hexc('#FFD4BA'), 'YOUR TOP GENRE', PLUM),
    (hexc('#B7006E'), 'YOUR TEAM', CREAM),
    (hexc('#5E9E0B'), 'YOUR ALLOWANCE', CREAM),
    (None, 'YOUR BIGGEST ACHIEVEMENT', CREAM),
]


def lerp_c(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


# ------------------------------------------------------------------ card backgrounds
_yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
_xx = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]


@functools.lru_cache(maxsize=8)
def card_base(i):
    col = CARDS[i][0]
    if col is None:   # card 6: glowing magenta -> orange
        u = np.clip(_xx * 0.35 + _yy * 0.8, 0, 1)
        a = np.array(hexc('#8E0F5E')[:3], np.float32)
        m = np.array(MAGENTA[:3], np.float32)
        o = np.array(ORANGE_B[:3], np.float32)
        c = np.where(u < 0.55, a * (1 - u / 0.55) + m * u / 0.55, m * (1 - (u - 0.55) / 0.45) + o * (u - 0.55) / 0.45)
        return np.broadcast_to(c, (H, W, 3)).astype(np.float32).copy()
    base = np.array(col[:3], np.float32)
    top = np.clip(base * 1.12 + 0.03, 0, 1)
    bot = base * 0.82
    c = top * (1 - _yy) + bot * _yy
    c = np.broadcast_to(c, (H, W, 3)).astype(np.float32).copy()
    # big soft shapes for depth (same hue, lighter/darker)
    sh = np.zeros((H, W), np.float32)
    cv2.circle(sh, (900, 300), 360, 1.0, -1, cv2.LINE_AA)
    cv2.circle(sh, (120, 1700), 300, 1.0, -1, cv2.LINE_AA)
    c += cv2.GaussianBlur(sh, (0, 0), 3)[..., None] * 0.06
    return c


def card_bg(i, lt):
    c = card_base(i).copy()
    # drifting light
    x = 540 + 240 * math.sin(lt * 0.6 + i)
    y = 700 + 160 * math.cos(lt * 0.5 + i)
    g = R_blob(x, y, 700)
    c += g * 0.10
    return c


_bY, _bX = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)


def R_blob(cx, cy, r):
    d = np.sqrt((_bX - cx / 4) ** 2 + (_bY - cy / 4) ** 2) / (r / 4)
    return cv2.resize(np.exp(-d * d), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]


def label(c, text, lt, ink, y=430):
    k = prog(lt, 0.15, 0.5)
    if k <= 0:
        return
    col = (ink[0], ink[1], ink[2], 0.16)
    p = pill(text, PB, 28, pad_x=28, pad_y=13, fill=col, border=None, text_color=ink, tracking=0.12)
    draw(c, p, W / 2, y + 20 * (1 - e_out_cubic(k)), opacity=min(1, k * 2))


def big(c, text, y, size, t, t0, ink, glow=None, dur=0.42, stagger=0.06, sweep_t=None, shadow_op=0.35):
    kinetic_line(c, text, W / 2, y, size, t, t0, color=ink, fname=PK, glow=glow, glow_str=0.45, shadow_op=shadow_op,
                 dur=dur, stagger=stagger, sweep_t=sweep_t, rise=60)


@functools.lru_cache(maxsize=4)
def star_spr(size=40):
    s = size * 3
    im = np.zeros((s, s), np.float32)
    pts = []
    for k in range(8):
        a = k * math.pi / 4
        r = s / 2 - 2 if k % 2 == 0 else s * 0.12
        pts.append([s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)])
    cv2.fillPoly(im, [np.array(pts, np.int32)], 1.0, cv2.LINE_AA)
    return cv2.resize(solid(im, (1.0, 0.95, 0.8, 1)), (size, size), interpolation=cv2.INTER_AREA)


STARS = [(np.random.default_rng(4).uniform(80, 1000), np.random.default_rng(40 + j).uniform(250, 1650),
          np.random.default_rng(80 + j).uniform(18, 46), j * 0.7) for j in range(14)]


def card1(t, lt):
    c = card_bg(0, lt)
    ink = CARDS[0][2]
    for j, (x, y, sz, ph) in enumerate(STARS):
        x = 80 + (j * 137) % 920
        tw = 0.5 + 0.5 * math.sin(t * 3 + ph)
        draw(c, star_spr(int(sz)), x, y, opacity=0.35 + 0.5 * tw * min(1, lt * 2))
    label(c, 'YOUR TOP MOMENT', lt, ink)
    big(c, 'The first', 640, 128, t, C[0] + 0.25, ink, dur=0.9, stagger=0.18)
    big(c, '‘goodnight’', 800, 140, t, C[0] + 0.55, hexc('#FFD4BA'), glow=hexc('#FFD4BA'), dur=0.9, stagger=0.18,
        sweep_t=C[0] + 1.5)
    k = e_out_cubic(prog(lt, 0.2, 1.6))
    y = lerp(1820, 1300, k)
    f = RS.seq('moon').frame(t)
    if f.shape[0] > 16:
        sc = 470 / max(f.shape[:2])
        glow_add(c, f, 540, y, (1.0, 0.92, 0.7), sigma=40, strength=0.7 * k, scale=sc)
        draw(c, f, 540, y, scale=sc, opacity=min(1, k * 2))
    return c


def card2(t, lt):
    c = card_bg(1, lt)
    ink = CARDS[1][2]
    label(c, 'YOUR MOST-PLAYED PHRASE', lt, ink)
    big(c, '“Can we have', 640, 104, t, C[1] + 0.2, ink)
    big(c, 'pizza tonight?”', 780, 104, t, C[1] + 0.45, ink, sweep_t=C[1] + 1.2)
    # audio player card with a waveform bouncing on the beat
    k = prog(lt, 0.5, 0.9)
    if k > 0:
        y = 1060 + 60 * (1 - e_out_cubic(k))
        draw(c, rrect_spr(900, 230, 50, (0.25, 0.04, 0.12, 0.35)), 540, y, opacity=min(1, k * 2))
        disc = rrect_spr(120, 120, 60, CREAM)
        tri = np.zeros((60, 60), np.float32)
        cv2.fillPoly(tri, [np.array([[18, 10], [52, 30], [18, 50]], np.int32)], 1.0, cv2.LINE_AA)
        d2 = disc.copy()
        paste(d2, solid(tri, ORANGE_B), 64, 60)
        draw(c, d2, 175, y, opacity=min(1, k * 2))
        beat = (t % 0.5) / 0.5
        env = math.exp(-beat * 4)
        for j in range(30):
            ph = math.sin(j * 1.7 + t * 9) * 0.5 + 0.5
            hgt = 18 + 110 * (0.25 + 0.75 * env) * (0.3 + 0.7 * ph) * (0.5 + 0.5 * math.sin(j * 0.45))
            draw(c, rrect_spr(12, hgt, 6, CREAM), 280 + j * 21, y, opacity=min(1, k * 2))
        txt(c, '0:03', 920, y + 80, 24, OFF, PM, min(1, k * 2), ax=1.0)
    icon3d(c, 'pizza', t, 540, 1480, 430, C[1] + 0.7)
    return c


def card3(t, lt):
    c = card_bg(2, lt)
    ink = CARDS[2][2]
    label(c, 'YOUR TOP GENRE', lt, ink)
    big(c, 'Bedtime', 640, 140, t, C[2] + 0.2, ink, shadow_op=0.0)
    big(c, 'stories', 790, 140, t, C[2] + 0.4, MAGENTA, shadow_op=0.0, sweep_t=C[2] + 1.1)
    # book stack drops in and settles
    k = prog(lt, 0.35, 0.95)
    if k > 0:
        e = 1 - (1 - k) ** 3
        dy = -(1 - e) * 700 + (math.sin(k * math.pi * 3) * 30 * (1 - k) if k > 0.6 else 0)
        f = RS.seq('books').frame(t)
        if f.shape[0] > 16:
            sc = 480 / max(f.shape[:2])
            sh = blur_sprite(tint(f, (0.35, 0.12, 0.1)), 14)
            draw(c, sh, 550, 1230 + 30, scale=sc, opacity=0.35 * min(1, k * 2))
            draw(c, f, 540, 1200 + dy, scale=sc, opacity=min(1, k * 3))
    # counter spins, then gives up: "Lost count"
    kc = prog(lt, 0.9, 1.2)
    if kc > 0:
        y = 1620
        draw(c, rrect_spr(620, 150, 75, (PLUM[0], PLUM[1], PLUM[2], 0.92)), 540, y, scale=0.9 + 0.1 * e_out_back(kc),
             opacity=min(1, kc * 3))
        if lt < 1.9:
            n = int(7 + (lt - 0.9) ** 2 * 900 + (lt * 97) % 13)
            ts = word_spr(f'{n}', PK, 74, CREAM)
            draw(c, blur_sprite(ts, 1.5), 540, y + 4)
        else:
            k2 = prog(lt, 1.9, 2.2)
            ts = word_spr('Lost count', PK, 66, CREAM)
            draw(c, ts, 510, y + 4, scale=0.8 + 0.2 * e_out_back(k2, 2.5), opacity=min(1, k2 * 3))
            icon3d(c, 'book', t, 510 + ts.shape[1] / 2 + 50, y, 90, C[2] + 1.95)
    return c


TEAM = [('person', 'Supervising', 'social worker'), ('clock', 'Advice outside', 'normal hours'),
        ('book', 'Ongoing', 'learning'), ('group', 'Other foster', 'carers')]


def card4(t, lt):
    c = card_bg(3, lt)
    ink = CARDS[3][2]
    label(c, 'YOUR TEAM', lt, ink)
    big(c, 'A whole team', 620, 112, t, C[3] + 0.2, ink)
    big(c, 'behind you.', 760, 112, t, C[3] + 0.4, hexc('#FFD4BA'), sweep_t=C[3] + 1.1)
    for j, (ic, l1, l2) in enumerate(TEAM):
        k = prog(lt, 0.55 + j * 0.18, 0.95 + j * 0.18)
        if k <= 0:
            continue
        x = 290 if j % 2 == 0 else 790
        y = 1080 + (j // 2) * 420
        s = e_out_back(k, 2.4)
        circ = rrect_spr(230, 230, 115, CREAM)
        draw(c, blur_sprite(tint(circ, (0.25, 0, 0.12)), 16), x + 6, y + 16, scale=s, opacity=0.4 * min(1, k * 2))
        draw(c, circ, x, y, scale=s, opacity=min(1, k * 3))
        icon3d(c, ic, t + j * 0.5, x, y + 4, 170 * s, op=min(1, k * 3))
        txt(c, l1, x, y + 160, 34, ink, PX, min(1, k * 2))
        txt(c, l2, x, y + 205, 30, (1, 0.9, 0.85, 0.9), PS, min(1, k * 2))
    return c


SLOT = '£447.60'


def card5(t, lt):
    c = card_bg(4, lt)
    ink = CARDS[4][2]
    label(c, 'YOUR ALLOWANCE', lt, ink)
    big(c, 'From', 610, 96, t, C[4] + 0.2, ink)
    # slot-machine counter
    k = prog(lt, 0.3, 0.6)
    if k > 0:
        wy = 860
        ww, wh = 940, 270
        frame = rrect_spr(ww + 24, wh + 24, 60, GOLD)
        draw(c, blur_sprite(tint(frame, (0.1, 0.2, 0)), 20), 540, wy + 20, opacity=0.4 * k)
        draw(c, frame, 540, wy, scale=0.9 + 0.1 * e_out_back(k), opacity=min(1, k * 3))
        draw(c, rrect_spr(ww, wh, 50, hexc('#2E0A2A')), 540, wy, scale=0.9 + 0.1 * e_out_back(k), opacity=min(1, k * 3))
        size = 170
        glyphs = [word_spr(ch, PK, size, CREAM) for ch in SLOT]
        fnt = font(PK, size)
        rb = fnt.getbbox('4')
        base = [((fnt.getbbox(ch)[1] + fnt.getbbox(ch)[3]) / 2 - (rb[1] + rb[3]) / 2) for ch in SLOT]
        widths = [g.shape[1] - 14 for g in glyphs]
        x = 540 - sum(widths) / 2
        reel_i = 0
        for ch, g, w_, by in zip(SLOT, glyphs, widths, base):
            cx = x + w_ / 2
            if ch.isdigit():
                stop = 0.75 + 0.22 * reel_i
                reel_i += 1
                kk = prog(lt, 0.55, stop)
                if kk < 1:
                    # rolling: scroll a strip of digits with motion blur, easing into the final digit
                    pos = (1 - e_out_cubic(kk)) * 24
                    for off in (-1, 0, 1):
                        d = (int(ch) + int(math.floor(pos)) + off) % 10
                        frac = pos - math.floor(pos)
                        dy = (off - frac) * size * 1.05
                        if abs(dy) < wh * 0.6:
                            gs = blur_sprite(word_spr(str(d), PK, size, CREAM), 4 * (1 - kk) + 0.5)
                            draw(c, gs, cx, wy + dy, opacity=max(0, 1 - abs(dy) / (wh * 0.55)) * min(1, k * 3))
                else:
                    bounce = math.sin(math.pi * prog(lt, stop, stop + 0.2)) * -14
                    draw(c, g, cx, wy + bounce, opacity=min(1, k * 3))
            else:
                draw(c, g, cx, wy + by, opacity=min(1, k * 3))
            x += w_
        # window shading so digits roll "behind glass"
        for sgn in (-1, 1):
            g = np.linspace(1, 0, 70, dtype=np.float32)[:, None] if sgn < 0 else np.linspace(0, 1, 70, dtype=np.float32)[:, None]
            band = np.concatenate([np.zeros((70, ww - 40, 3), np.float32), np.repeat(g, ww - 40, 1)[..., None] * 0.9], 2)
            band[..., :3] = np.array(hexc('#2E0A2A')[:3]) * band[..., 3:4]
            draw(c, band, 540, wy + sgn * (wh / 2 - 45), opacity=min(1, k * 3))
    big(c, 'a week*', 1110, 92, t, C[4] + 1.5, hexc('#E8F7C8'), sweep_t=C[4] + 2.0)
    kc = prog(lt, 1.55, 2.0)
    if kc > 0:
        s_ = RS.seq('coin')
        n = len(s_.files)
        idx = int(round(2.5 * math.sin(t * 2.2))) % n
        f = s_.frame(idx / 24.0)
        sc = 330 / max(f.shape[:2]) * e_out_back(kc, 2.2)
        glow_add(c, f, 540, 1430, (1, 0.9, 0.5), sigma=30, strength=0.5 * kc, scale=sc)
        draw(c, blur_sprite(tint(f, (0.1, 0.25, 0)), 14), 550, 1460, scale=sc, opacity=0.4 * kc)
        draw(c, f, 540, 1430, scale=sc, opacity=min(1, kc * 3))
    kf = prog(lt, 1.8, 2.1)
    if kf > 0:
        txt(c, '*For one child aged 0–4. Rates may vary.', 540, 1720, 28, OFF, PS, kf)
    return c


def rays(c, cx, cy, t, strength=0.25, color=(1.0, 0.85, 0.6)):
    ys, xs = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    a = np.arctan2(ys - cy / 4, xs - cx / 4)
    r = np.sqrt((ys - cy / 4) ** 2 + (xs - cx / 4) ** 2)
    m = (0.5 + 0.5 * np.cos(a * 12 + t * 0.6)) ** 6 * np.exp(-r / 160)
    c += cv2.resize(m, (W, H))[..., None] * np.array(color, np.float32) * strength


def card6(t, lt):
    c = card_bg(5, lt)
    ink = CARDS[5][2]
    pulse = 0.5 + 0.5 * math.sin(t * 2.4)
    rays(c, 540, 1300, t, 0.22 + 0.08 * pulse)
    label(c, 'YOUR BIGGEST ACHIEVEMENT', lt, ink)
    v = VO['c6']
    big(c, 'A safe home.', 620, 112, t, v + 2.3, ink, glow=(1, 0.8, 0.6, 1), sweep_t=v + 3.2)
    big(c, 'Everyday care.', 750, 112, t, v + 3.0, hexc('#FFE3D1'))
    big(c, 'A place to belong.', 880, 104, t, v + 3.7, ink, glow=(1, 0.8, 0.6, 1), sweep_t=v + 4.4)
    k = prog(lt, 0.2, 0.8)
    if k > 0:
        f = RS.seq('house').frame(t)
        if f.shape[0] > 16:
            sc = 520 / max(f.shape[:2]) * (0.85 + 0.15 * e_out_back(k, 1.6))
            glow_add(c, f, 540, 1330, (1, 0.8, 0.55), sigma=50, strength=(0.6 + 0.3 * pulse) * k, scale=sc)
            draw(c, f, 540, 1330, scale=sc, opacity=min(1, k * 2))
    icon3d(c, 'heart', t, 700, 1080 + 12 * math.sin(t * 2), 150, C[5] + 0.9)
    # card glows at its edges
    edge = solid(sdf_stroke(rrect_alpha(W - 40, H - 40, 60, 30), 10.0), (1, 0.85, 0.6, 1))
    draw(c, blur_sprite(edge, 22), W / 2, H / 2, opacity=0.35 + 0.25 * pulse, mode='add')
    return c


CARD_FN = [card1, card2, card3, card4, card5, card6]


def card(i, t):
    return CARD_FN[i](t, t - C[i])


# ------------------------------------------------------------------ story header + cube swipe
def story_header(c, t):
    op = min(1, prog(t, C[0], C[0] + 0.3)) * (1 - prog(t, T['turn'], T['turn'] + 0.3))
    if op <= 0:
        return
    n = 6
    gap = 10
    sw = (W - 80 - gap * (n - 1)) / n
    for i in range(n):
        x0 = 40 + i * (sw + gap)
        end = C[i + 1] if i + 1 < n else T['turn']
        p = clamp((t - C[i]) / (end - C[i]))
        draw(c, rrect_spr(sw, 8, 4, (1, 1, 1, 0.35)), x0 + sw / 2, 60, opacity=op)
        if p > 0:
            draw(c, rrect_spr(max(8, sw * p), 8, 4, (1, 1, 1, 1)), x0 + max(8, sw * p) / 2, 60, opacity=op)
    av = rrect_spr(76, 76, 38, (1, 1, 1, 1))
    a2 = av.copy()
    paste(a2, fitted('emblem_s', png('emblem'), height=48), 38, 38)
    draw(c, a2, 85, 130, opacity=op)
    txt(c, 'Your Year in Fostering', 140, 118, 32, (1, 1, 1, 1), PB, op, ax=0.0, shadow_op=0.4)
    txt(c, '2027 recap', 140, 152, 24, (1, 1, 1, 0.8), PM, op, ax=0.0, shadow_op=0.4)


def as_spr(c, shade=0.0):
    return np.concatenate([c * (1 - shade), np.ones((H, W, 1), np.float32)], 2)


def cube(prev, nxt, p):
    """Story-style 3D cube turn from prev to nxt, p in [0, 1]."""
    a = 90 * e_inout_cubic(p)
    out = np.zeros((H, W, 3), np.float32) + np.array([0.06, 0.01, 0.05], np.float32)
    d = W / 2
    ra = math.radians(a)
    faces = [(as_spr(prev, 0.45 * math.sin(ra)), W / 2 - d * math.sin(ra), d - d * math.cos(ra), a),
             (as_spr(nxt, 0.45 * math.cos(ra)), W / 2 + d * math.cos(ra), d - d * math.sin(ra), a - 90)]
    order = [1, 0] if a < 45 else [0, 1]
    for j in order:
        spr, cx, cz, ry = faces[j]
        if abs(ry) < 89.5:
            draw3d(out, spr, cx, H / 2, cz, W, H, ry=ry)
    return out


# ------------------------------------------------------------------ hook: phone + notification
def notif_spr(t):
    w, h = 540, 190
    spr = rrect_spr(w, h, 34, (0.99, 0.92, 0.98, 0.96), border=(1, 1, 1, 1), bw=2)
    ic = rrect_spr(88, 88, 22, (1, 1, 1, 1))
    paste(ic, fitted('emblem', png('emblem'), height=58), 44, 44)
    paste(spr, ic, 72, 80)
    app = text_sprite('Organic Fostering', PM, 22, hexc('#7A5A78'))
    paste(spr, app, 135 + app.shape[1] / 2, 44)
    paste(spr, text_sprite('now', PM, 22, hexc('#7A5A78')), w - 50, 44)
    xend = 0
    for j, line in enumerate(('Your Year in Fostering', 'is ready')):
        ts = text_sprite(line, PB, 29, INK)
        paste(spr, ts, 135 + ts.shape[1] / 2, 86 + j * 40)
        xend = 135 + ts.shape[1]
    f = RS.seq('gift').frame(t)
    if f.shape[0] > 16:
        g = cv2.resize(f, (int(f.shape[1] * 56 / f.shape[0]), 56), interpolation=cv2.INTER_AREA)
        paste(spr, g, xend + 34, 122)
    # Play pill
    pl = rrect_spr(150, 50, 25, None, grad=(MAGENTA, ORANGE_B))
    tri = np.zeros((40, 40), np.float32)
    cv2.fillPoly(tri, [np.array([[10, 6], [34, 20], [10, 34]], np.int32)], 1.0, cv2.LINE_AA)
    paste(pl, cv2.resize(solid(tri, WHITE_), (20, 20), interpolation=cv2.INTER_AREA), 40, 25)
    paste(pl, text_sprite('Play', PB, 24, WHITE_), 88, 26)
    paste(spr, pl, 135 + 75, 165)
    return spr


def lock_screen(t):
    scr = np.concatenate([wallpaper().copy(), np.ones((SH, SW, 1), np.float32)], 2)
    paste(scr, text_sprite('8:02', PS, 24, WHITE_), 70, 40)
    paste(scr, padlock(), SW / 2, 150)
    paste(scr, text_sprite('8:02', PL, 190, WHITE_), SW / 2, 300)
    paste(scr, text_sprite('Friday 1 January', PM, 34, (1, 1, 1, 0.9)), SW / 2, 425)
    k = prog(t, NOTIF, NOTIF + 0.45)
    if k > 0:
        y = 580 + (1 - e_out_back(k, 1.8)) * -440
        n = notif_spr(t)
        g = blur_sprite(tint(rrect_spr(n.shape[1], n.shape[0], 34, WHITE_), MAGENTA[:3]), 18)
        paste(scr, g, SW / 2, y, op=0.8 * min(1, k * 2))
        paste(scr, n, SW / 2, y, op=min(1, k * 3))
    return scr


@functools.lru_cache(maxsize=1)
def burst_grad():
    u = np.clip(_xx * 0.4 + _yy * 0.8, 0, 1)
    m = np.array(MAGENTA[:3], np.float32)
    o = np.array(ORANGE_B[:3], np.float32)
    return np.broadcast_to(m * (1 - u) + o * u, (H, W, 3)).astype(np.float32).copy()


def sc_hook(t):
    c = bg(t)
    title(c, 'What if this was', W / 2, 190, 76, t, 0.25, glow=MAGENTA, fname=PK, depth=5, ext=MAGENTA)
    title(c, 'your 2027?', W / 2, 295, 92, t, 0.5, color=hexc('#FFD9C2'), glow=ORANGE_B, fname=PK, depth=5,
          ext=ORANGE_B, sweep_t=1.2)
    k = e_out_cubic(prog(t, 0.0, 0.9))
    rx = lerp(26, 6, k) + 1.5 * math.sin(t * 1.3)
    ry = lerp(-24, -8, k) + 2 * math.sin(t * 0.9)
    rz = lerp(-6, -1.5, k)
    cy, w = lerp(1350, 1150, k), lerp(580, 680, k)
    kt = e_inout_cubic(prog(t, TAP_PLAY - 0.3, TAP_PLAY + 0.1))
    rx, ry, rz = lerp(rx, 0, kt), lerp(ry, 0, kt), lerp(rz, 0, kt)
    for tb in (NOTIF - 0.05, NOTIF + 0.2):
        kb = prog(t, tb, tb + 0.18)
        if 0 < kb < 1:
            rz += 2.2 * math.sin(kb * math.pi * 8) * (1 - kb)
    draw_phone(c, phone_spr(lock_screen(t)), W / 2, cy, w, rx, ry, rz)
    # Play pill position on screen -> canvas
    # notification sprite (544x194) is centred at screen (SW/2, 580); its Play pill sits at (210, 165) inside it
    sx_, sy_ = SW / 2 - 272 + 210, 580 - 97 + 165
    px = W / 2 + (sx_ + (PW - SW) / 2 - PW / 2) * w / PW
    py = cy + (sy_ + (PH - SH) / 2 - PH / 2) * w / PW
    cursor(c, t, (980, 1800), (px, py), 1.1, TAP_PLAY - 0.05, TAP_PLAY, op=1 - prog(t, TAP_PLAY + 0.15, TAP_PLAY + 0.3))
    ripple(c, px, py, t, TAP_PLAY, MAGENTA, n=2, rmax=220)
    # burst into the magenta -> orange gradient
    kb = prog(t, TAP_PLAY + 0.05, C[0] - 0.05)
    if kb > 0:
        r = e_in_cubic(kb) * 2300
        m = np.zeros((H, W), np.float32)
        cv2.circle(m, (int(px), int(py)), int(r), 1.0, -1, cv2.LINE_AA)
        m = cv2.GaussianBlur(m, (0, 0), 10)[..., None]
        c = c * (1 - m) + burst_grad() * m
        ring = np.zeros((H, W), np.float32)
        cv2.circle(ring, (int(px), int(py)), int(r), 1.0, 18, cv2.LINE_AA)
        c += cv2.GaussianBlur(ring, (0, 0), 14)[..., None] * 0.8
    return c


# ------------------------------------------------------------------ the turn: fan out, shuffle, "Your 2027 story"
@functools.lru_cache(maxsize=8)
def thumb(i):
    c = card(i, C[i] + (2.4 if i < 5 else 4.6))
    spr = np.concatenate([c, np.ones((H, W, 1), np.float32)], 2)
    small = cv2.resize(spr, (270, 480), interpolation=cv2.INTER_AREA)
    a = sdf_fill(rrect_alpha(270, 480, 28, 0))
    a = cv2.resize(a, (270, 480))[..., None]
    return (small * a).astype(np.float32)


GRID = [(225, 720), (540, 720), (855, 720), (225, 1260), (540, 1260), (855, 1260)]


def story_card(c, t, cx, cy, s, op, face='story', rot=0.0):
    w, h = 760, 1180
    spr = np.zeros((h + 80, w + 80, 4), np.float32)
    body = rrect_spr(w, h, 56, None, grad=(hexc('#3B0D36'), hexc('#5B174F')))
    paste(spr, body, spr.shape[1] / 2, spr.shape[0] / 2)
    paste(spr, solid(sdf_stroke(rrect_alpha(w, h, 56, 0), 3), (1, 1, 1, 0.35)), spr.shape[1] / 2, spr.shape[0] / 2)
    ox, oy = 40, 40
    if face == 'story':
        sw = (w - 80 - 50) / 6
        for i in range(6):
            paste(spr, rrect_spr(sw, 8, 4, (1, 1, 1, 0.3)), ox + 40 + sw / 2 + i * (sw + 10), oy + 50)
        ts = text_sprite('Your 2027 story', PK, 62, CREAM)
        paste(spr, ts, spr.shape[1] / 2, oy + 200)
        f = RS.seq('year').frame(t)
        if f.shape[0] > 16:
            yr = cv2.resize(f, (560, int(f.shape[0] * 560 / f.shape[1])), interpolation=cv2.INTER_AREA)
            paste(spr, yr, spr.shape[1] / 2, oy + 470)
        dash = np.zeros((300, 620), np.float32)
        for x in range(0, 620, 34):
            cv2.line(dash, (x, 2), (min(619, x + 18), 2), 1.0, 3)
            cv2.line(dash, (x, 297), (min(619, x + 18), 297), 1.0, 3)
        for y in range(0, 300, 34):
            cv2.line(dash, (2, y), (2, min(299, y + 18)), 1.0, 3)
            cv2.line(dash, (617, y), (617, min(299, y + 18)), 1.0, 3)
        paste(spr, solid(dash, (1, 1, 1, 0.35)), spr.shape[1] / 2, oy + 800)
        paste(spr, text_sprite('Not started yet', PM, 40, (1, 1, 1, 0.8)), spr.shape[1] / 2, oy + 800)
    else:   # back face: the toast
        ck = cv2.resize(check_spr(160, GREEN), (160, 160))
        paste(spr, ck, spr.shape[1] / 2, oy + 470)
        paste(spr, text_sprite('Enquiry started', PK, 66, CREAM), spr.shape[1] / 2, oy + 640)
        paste(spr, text_sprite('We’ll be in touch soon.', PM, 36, (1, 1, 1, 0.8)), spr.shape[1] / 2, oy + 710)
    edge = blur_sprite(tint(rrect_spr(w, h, 56, WHITE_), MAGENTA[:3]), 26)
    if abs(rot) > 0.5:
        draw3d(c, edge, cx, cy, 0, edge.shape[1] * s * 1.02, None, ry=rot, opacity=0.6 * op, mode='add')
    else:
        draw(c, edge, cx, cy, scale=s * 1.02, opacity=0.6 * op, mode='add')
    if abs(rot) > 0.5:
        draw3d(c, spr, cx, cy, 0, spr.shape[1] * s, None, ry=rot, opacity=op)
    else:
        draw(c, spr, cx, cy, scale=s, opacity=op)
    return (h * s) / 2


def start_button(c, cx, cy, t, press=0.0, op=1.0):
    bw_, bh_ = 560, 130
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    g = blur_sprite(tint(rrect_spr(bw_, bh_, 65, WHITE_), ORANGE_B[:3]), 26)
    draw(c, g, cx, cy, scale=1.05 + 0.06 * pulse, opacity=op * (0.6 + 0.4 * pulse), mode='add')
    b = rrect_spr(bw_, bh_, 65, None, grad=(hexc('#FF7A1A'), hexc('#FFA24D')))
    s = 1 - 0.06 * press
    draw(c, b, cx, cy, scale=s, opacity=op)
    draw(c, word_spr('Start your story', PK, 46, WHITE_), cx, cy + 2, scale=s, opacity=op)


def sc_turn(t):
    t0 = T['turn']
    c = bg(t, 0.3)
    lt = t - t0
    # 1) fan out into a grid
    shuffle = prog(lt, 1.2, 1.9)
    for i in range(6):
        k = e_out_back(prog(lt, 0.05 + i * 0.06, 0.6 + i * 0.06), 1.4)
        gx, gy = GRID[i]
        x = lerp(W / 2, gx, k)
        y = lerp(H / 2, gy, k)
        rot = lerp(0, (-8, 3, 7, -5, 4, -3)[i], k)
        sc = lerp(1.6, 1.0, k)
        if shuffle > 0:
            es = e_inout_cubic(shuffle)
            swirl = math.sin(es * math.pi) * (160 if i % 2 else -160)
            x = lerp(x, W / 2 + swirl, es)
            y = lerp(y, H / 2 + 60, es)
            rot = rot + es * (i - 2.5) * 22
            sc = lerp(sc, 1.6, es)
        op = 1 - prog(lt, 1.8, 2.05)
        if op > 0:
            th = thumb(i)
            draw(c, blur_sprite(tint(th, (0.05, 0, 0.05)), 12), x + 10, y + 18, scale=sc, rot=rot, opacity=0.5 * op)
            draw(c, th, x, y, scale=sc, rot=rot, opacity=op)
    # 2) one card with a blank year
    ks = prog(t, STORY_T - 0.15, STORY_T + 0.35)
    if ks > 0:
        story_card(c, t, W / 2, 1060, 0.95 * (0.85 + 0.15 * e_out_back(ks, 1.8)), min(1, ks * 3))
        kb = prog(t, BTN_T, BTN_T + 0.35)
        if kb > 0:
            start_button(c, W / 2, 1530, t, op=min(1, kb * 3))
    title(c, "Next year's recap starts", W / 2, 190, 62, t, VO['turn'] - 0.05, glow=MAGENTA, fname=PX)
    title(c, 'with one conversation.', W / 2, 275, 62, t, VO['turn'] + 0.9, color=hexc('#FFD9C2'), glow=ORANGE_B,
          fname=PX, sweep_t=VO['turn'] + 1.6)
    return c


def sc_cta(t):
    t0 = T['cta']
    if t < LOGO_T:
        c = bg(t, 0.3)
        title(c, "Next year's recap starts", W / 2, 190, 62, t, -10, glow=MAGENTA, fname=PX)
        title(c, 'with one conversation.', W / 2, 275, 62, t, -10, color=hexc('#FFD9C2'), glow=ORANGE_B, fname=PX)
        kf = prog(t, FLIP_T, FLIP_T + 0.45)
        fold = e_in_cubic(prog(t, LOGO_T - 0.4, LOGO_T))
        s = 0.95 * (1 - 0.75 * fold)
        ang = 180 * e_inout_cubic(kf)
        face = 'story' if ang < 90 else 'toast'
        rot = ang if ang < 90 else ang - 180
        story_card(c, t, W / 2, lerp(1060, 900, fold), s, 1 - fold * 0.6, face=face, rot=rot + fold * 25)
        if face == 'toast':
            confetti(c, t, FLIP_T + 0.25, W / 2, 900)
        if kf < 0.3:
            press = math.sin(math.pi * prog(t, TAP_CTA - 0.06, TAP_CTA + 0.2))
            start_button(c, W / 2, 1530, t, press=press, op=1 - kf / 0.3)
            ripple(c, W / 2 + 120, 1540, t, TAP_CTA, WHITE_, n=3, rmax=320)
            sparks(c, W / 2 + 230, 1470, t, TAP_CTA + 0.02, WHITE_)
        cursor(c, t, (960, 1880), (W / 2 + 120, 1540), t0 - 0.1, TAP_CTA - 0.05, TAP_CTA,
               op=1 - prog(t, TAP_CTA + 0.25, TAP_CTA + 0.5))
        if fold > 0:
            c = c * (1 - fold) + burst_grad() * fold
        return c
    c = burst_grad().copy()
    lt = t - LOGO_T
    shapes = np.zeros((H, W), np.float32)
    cv2.circle(shapes, (int(900 + 30 * math.sin(t * 0.5)), 330), 340, 1.0, -1, cv2.LINE_AA)
    cv2.circle(shapes, (int(140 + 30 * math.cos(t * 0.4)), 1680), 300, 1.0, -1, cv2.LINE_AA)
    c += shapes[..., None] * 0.07 * (1 - c)
    kl = prog(lt, 0.0, 0.5)
    from reel_of import glass
    glass(c, W / 2, 640, 880, 340, r=48, tint_c=(1, 1, 1), tint_a=0.96, opacity=min(1, kl * 2.5), blur=24,
          shadow_a=0.45, border_a=0.9)
    lg = fitted('logo', png('logo_full'), width=740)
    draw(c, lg, W / 2, 640, scale=0.9 + 0.1 * e_out_back(kl, 2.0), opacity=min(1, kl * 2))
    if 0.5 < lt < 1.4:
        p = (lt - 0.5) / 0.8 * 1.6 - 0.3
        draw(c, sweep(lg, p, strength=0.5), W / 2, 640, opacity=0.5)
    ke = prog(lt, 0.3, 0.7)
    if ke > 0:
        p = pill('Start your enquiry', PK, 48, pad_x=50, pad_y=24, fill=CREAM, border=None, text_color=PLUM)
        draw(c, blur_sprite(tint(p, (0.3, 0, 0.15)), 14), W / 2 + 6, 960 + 14, opacity=0.5 * ke)
        draw(c, p, W / 2, 960, scale=e_out_back(ke, 2.2), opacity=min(1, ke * 3))
    for j, (label_, ic) in enumerate([('0161 241 1332', 'phone'), ('organicfostering.co.uk', 'web')]):
        kk = prog(lt, 0.55 + j * 0.15, 0.9 + j * 0.15)
        if kk <= 0:
            continue
        y = 1150 + j * 105
        ic_ = cv2.resize(icon_disc(ic), (78, 78))
        ts = word_spr(label_, PX, 46, CREAM)
        total = 84 + 22 + ts.shape[1]
        x0 = W / 2 - total / 2
        draw(c, ic_, x0 + 42, y, scale=e_out_back(kk, 2.4), opacity=min(1, kk * 3))
        draw(c, blur_sprite(tint(ts, (0.3, 0, 0.15)), 8), x0 + 106 + ts.shape[1] / 2 + 3, y + 7, opacity=0.5 * kk)
        draw(c, ts, x0 + 106 + ts.shape[1] / 2, y + 2, opacity=min(1, kk * 3))
    ko = prog(lt, 0.95, 1.3)
    if ko > 0:
        p = pill('Rated Good by Ofsted', PB, 30, pad_x=30, pad_y=14, fill=hexc('#3F8F0B'), border=(1, 1, 1, 0.6),
                 text_color=WHITE_, dot=GOLD)
        draw(c, p, W / 2, 1400, scale=e_out_back(ko, 2.2), opacity=min(1, ko * 3))
    ks = prog(lt, 1.1, 1.5)
    if ks > 0:
        for j, ln in enumerate(['*Weekly allowance for one child aged 0–4, based on current published rates.',
                                'Rates may vary by region and are subject to change.',
                                'Moments shown are illustrative.']):
            txt(c, ln, W / 2, 1700 + j * 38, 25, CREAM, PS, ks, shadow_op=0.5)
    return c


# ------------------------------------------------------------------ assembly
def render_raw(t):
    if t < C[0]:
        c = sc_hook(t)
    elif t < T['turn']:
        i = max(j for j in range(6) if C[j] <= t)
        d = t - C[i]
        if d < SWIPE:
            prev = sc_hook(C[0] - 0.01) if i == 0 else card(i - 1, t)
            c = cube(prev, card(i, t), d / SWIPE)
        else:
            c = card(i, t)
        story_header(c, t)
        if T['turn'] - 0.35 < t:
            k = prog(t, T['turn'] - 0.35, T['turn'])
            c = zoom_blur(c, k * 3) * (1 - 0.3 * k)
    elif t < T['cta']:
        c = sc_turn(t)
        if t < T['turn'] + 0.25:
            c = c + 0.7 * math.exp(-(t - T['turn']) * 12)
    else:
        c = sc_cta(t)
    dx = dy = 0.0
    for tc in [TAP_PLAY, TAP_CTA, C[4] + 1.41, LOGO_T]:
        sx, sy = shake(t, tc, amp=9, dur=0.3)
        dx += sx
        dy += sy
    if abs(dx) + abs(dy) > 0.5:
        c = cv2.warpAffine(c, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t > DUR - FADE:
        c *= 1 - 0.85 * e_inout_cubic(prog(t, DUR - FADE, DUR))
    return c


def is_fast(t):
    return any(0 <= t - tc < SWIPE for tc in C) or abs(t - TAP_PLAY) < 0.2 or abs(t - T['turn']) < 0.3 \
        or abs(t - LOGO_T) < 0.25


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
    flat = C[0] <= t < T['turn'] or t >= LOGO_T
    return post(c, fi, bloom=0.22 if flat else 0.45, grain=0.022, vig=0.45 if flat else 1.0)


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
