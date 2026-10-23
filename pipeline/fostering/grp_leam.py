"""grp_leam.py: Leam Taxis client testimonial edit (Google Ranker Pro / Hulk Marketing), 9:16, 24 fps, 33 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp_leam --audio <mix.wav>

Source: workspace3/frames/leam (Seedance clip, 30.04 s): shot 1 desk 0-8.0 s, shot 2 monitor + hand 8.0-17.0 s,
shot 3 selfie 17.0-30.04 s; 30.04-33.0 s is the end card over the held last frame.

Every graphic is real: the Leam Taxis site (assets/sites/leamingtonspa-taxis, captured 22 Oct 2026), the Leam
logo (vector rebuild of the site's logo), and the Google Business Profile Calls screenshot (114 calls May-Oct
2026, September = 25, October a part month) shown at its true aspect on the monitor. No ranking badges, no
growth arrows, no invented numbers. Captions are the owner's words as spoken (spelling fixed).
"""
import functools
import math

import numpy as np

import core as K
import grp_kit as G
import grp_leam_screen as S
import ui

DUR = 33.0
LOOK = 'natural'
BPM = 100
FPS_SRC = 24.0
N_SRC = 721
T_CUT1, T_CUT2, T_END = 8.0, 17.0, 30.0417
T_HERE = 14.30                                     # "and then here" -> the September tooltip
Y, K_, Y2 = '#FFC61A', '#1F1F1F', '#FBCE08'
FONT_H = 'FiraSansCondensed-ExtraBold'
FONT_HB = 'FiraSansCondensed-Bold'
FONT_B = 'OpenSans-SemiBold'
FONT_R = 'OpenSans-Regular'
LEAM_SITE = G.site('leamingtonspa-taxis', 'now_desktop.png')
LEAM_FULL = G.site('leamingtonspa-taxis', 'now_desktop_full.png')
HULK = G.site('hulkmarketing', 'hulk-marketing-logo.png')

WORDS = G.load_words('leam_taxis',
                     fixes={5: 'Search', 6: 'Console.', 14: 'Hulk', 15: 'Marketing', 38: 'Leamington', 39: None,
                            40: 'Spa.'},
                     retime={16: (10.12, 10.32), 25: (13.95, 14.18), 28: (15.40, 15.62), 38: (21.04, 21.40),
                             40: (21.40, 21.70), 48: (25.50, 25.74)})
CAP = G.Captions(WORDS, dict(font=FONT_H, size=70, color='#FFFFFF', accent=Y, mode='color', y=1625, max_w=900,
                             shadow=0.7), max_chars=26)


# ---------------------------------------------------------------------------------------------- footage
def shot_of(fi):
    return 1 if fi < 192 else (2 if fi < 408 else 3)


def _shot1_tf(tf):
    """Punch-in that crops the pint glass out (source x < ~250) with a slow push."""
    u = K.clamp(tf / T_CUT1)
    z = 1.30 + 0.06 * K.EASE['inout_sine'](u)
    vw = 1080 / z
    cx = (1080 - vw / 2 - 4) / 1080
    return (cx, 0.545), z


def _shot3_tf(tf):
    u = K.clamp((tf - T_CUT2) / (T_END - T_CUT2))
    z = 1.0 + 0.03 * K.EASE['inout_sine'](u)
    return (0.5, 0.5), z


@functools.lru_cache(maxsize=3)
def footage(fi):
    """Graded full-frame sprite for source frame fi (same for every sub-sample of an output frame)."""
    fr = G.frame_u8('leam', fi)
    tf = fi / FPS_SRC
    sh = shot_of(fi)
    if sh == 1:
        c, z = _shot1_tf(tf)
        return G.shot_sprite(fr, 'leam_desk', c, z, sharpen=0.55)
    if sh == 2:
        fx = S.front_x(tf)
        scr = S.look_u8(S.screen_lin(tf, fx, T_HERE), fi)
        return G.shot_sprite(S.composite(fr, fi, scr), 'leam_screen', sharpen=0.15)
    c, z = _shot3_tf(tf)
    return G.shot_sprite(fr, 'leam_selfie', c, z, sharpen=0.3)


@functools.lru_cache(maxsize=2)
def person(fi):
    """The speaker cut out of the graded footage (shots 1 and 3), to composite over cards placed behind him."""
    sh = shot_of(fi)
    if sh == 2:
        return None
    tf = fi / FPS_SRC
    c, z = _shot1_tf(tf) if sh == 1 else _shot3_tf(tf)
    return G.person_sprite(footage(fi), 'leam', fi, c, z)


def person_over(cv, t):
    """Re-composite the speaker over whatever was drawn so far (not during shot transitions)."""
    if t < 0.75 or 7.84 <= t < 17.24 or t >= 29.2:
        return
    p = person(G.fidx(t, N_SRC))
    if p is not None:
        K.over(cv, p)


def plate(t):
    """Footage layer with the shot transitions (mask wipes), as a fresh canvas."""
    fi = G.fidx(t, N_SRC)
    cv = footage(fi).copy()
    # 1 -> 2: yellow diagonal band wipe 7.86-8.14 (shot 2 behind the band from its first frame)
    if 7.86 <= t < 8.16:
        u = K.ramp(t, 7.86, 8.16, 'inout_cubic')
        other = footage(192 if t < T_CUT1 else 191)
        m = G.wipe(K.W, K.H, u, angle=-60, soft=0.001)
        new_first = t < T_CUT1
        m3 = m[..., None]
        if new_first:
            cv[:] = cv * (1 - m3) + other * m3
        else:
            cv[:] = other * (1 - m3) + cv * m3
        _band(cv, u)
    # 2 -> 3: iris from the fingertip 16.86-17.22
    if 16.86 <= t < 17.22:
        u = K.ramp(t, 16.86, 17.22, 'inout_cubic')
        m1 = G.iris(K.W, K.H, u, 1000 / 1080, 686 / 1920, soft=14)
        m = m1[..., None]
        if t < T_CUT2:
            cv[:] = cv * (1 - m) + footage(408) * m
        else:
            cv[:] = footage(407) * (1 - m) + cv * m
        ring = np.clip(m1 - G.iris(K.W, K.H, max(0.0, u - 0.035), 1000 / 1080, 686 / 1920, soft=14), 0, 1)
        ring *= np.float32(1 - u ** 3)
        cv[..., :3] = cv[..., :3] * (1 - ring[..., None]) + G.lin(Y) * ring[..., None]
    # end: hold the last frame, defocus it under the end card
    if t >= T_END:
        cv = footage(N_SRC - 1).copy()
    if t >= 29.2:
        k = K.ramp(t, 29.2, 30.4, 'inout_cubic')
        blur = 18 * k
        if blur > 0.3:
            cv = K.gblur(cv, blur)
        cv[..., :3] *= np.float32(1 - 0.55 * k)
    return cv


def _band(cv, u):
    """A yellow band riding the wipe edge."""
    a = math.radians(-60)
    dx, dy = math.cos(a), -math.sin(a)
    span = 0.5 * (abs(dx) + abs(dy))
    front = -span + u * (2 * span)
    xs = (np.arange(K.W, dtype=np.float32) + 0.5) / K.W - 0.5
    ys = (np.arange(K.H, dtype=np.float32) + 0.5) / K.H - 0.5
    proj = xs[None, :] * dx + ys[:, None] * dy
    w = 0.055
    m = np.clip(1 - np.abs(proj - front + w / 2) / (w / 2), 0, 1) ** 0.35
    m = np.clip(m * 1.4, 0, 1)
    col = G.lin(Y)
    cv[..., :3] = cv[..., :3] * (1 - m[..., None]) + col * m[..., None]


# ---------------------------------------------------------------------------------------------- overlays
def logo_bug(cv, t):
    """Small Leam logo top-left + AI label (persistent from the intro to the end card)."""
    if t < 2.5 or t >= 29.6:
        return
    k = min(K.ramp(t, 2.5, 2.62), 1 - K.ramp(t, 29.3, 29.6, 'in_cubic'))
    lg = G.leam_logo(54, strap=False)
    K.draw(cv, lg, 64, 104, anchor=(0, 0.5), opacity=k)


def ai_label(cv, t):
    if t < 0.8:
        return
    k = K.ramp(t, 0.8, 1.2)
    txt = 'AI re-creation · real client data'
    w = G.measure(txt, 24, FONT_B)
    pnl, pad = G.panel(int(w + 32), 40, 20, fill='#000000', fill_a=0.42, border_a=0.0, shadow=0.0)
    y = 1862
    K.draw(cv, pnl, 64 - pad, y - 20 - pad, anchor=(0, 0), opacity=k)
    G.draw_text(cv, txt, 80, y + 8, 24, FONT_B, '#FFFFFF', 'ls', opacity=0.9 * k)


def intro(cv, t):
    """0-0.75 s: footage revealed through a growing yellow-edged pill; 0.35-2.5 s: client-story lockup."""
    if t < 0.75:
        u = K.EASE['inout_quart'](K.ramp(t, 0.0, 0.74, 'linear'))
        w0, h0 = 380, 120
        m = G.rrect_grow(K.W, K.H, u, 60 * (1 - u) + 1, 0.5, 0.5, w0, h0)
        bg = K.new_canvas(G.lin('#141414'))
        glow = K.radial(900, G.lin(Y), 2.0, 0.18)
        K.draw(bg, glow, 540, 770, mode='add')
        cv[:] = bg * (1 - m[..., None]) + cv * m[..., None]
        bw = w0 + (K.W - w0) * u
        bh = h0 + (K.H - h0) * u
        st = ui.Surf(K.W, K.H)
        st.stroke_rrect(540 - bw / 2, 0.5 * K.H - bh / 2, bw, bh, min(60 * (1 - u) + 1, bw / 2, bh / 2), 5,
                        G.lin(Y), 1.0 - u ** 2)
        K.over(cv, st.img)
    if 0.30 <= t < 2.65:
        cx, cy = 540, 400
        a_in = K.spring(t - 0.30, 2.2, 0.62)
        a_out = K.ramp(t, 2.20, 2.55, 'in_cubic')
        # panel
        pnl, pad = G.panel(720, 300, 36, fill='#121212', fill_a=0.80, border='#FFFFFF', border_a=0.10,
                           shadow=0.5)
        sc = (0.86 + 0.14 * a_in) * (1 - 0.25 * a_out)
        K.draw(cv, pnl, cx, cy, scale=sc, opacity=min(1.0, (t - 0.30) / 0.12) * (1 - a_out), frost=10)
        op = (1 - a_out) * K.ramp(t, 0.42, 0.62)
        # tag
        tag = 'CLIENT STORY'
        G.draw_text(cv, tag, cx, cy - 92, 28, FONT_HB, Y, 'ms', opacity=op, tracking=0.18)
        # logo: wipes in from the left, then flies to the corner
        lg = G.leam_logo(104, strap=True, strap_color='#FFFFFF')
        h, w = lg.shape[:2]
        wu = K.ramp(t, 0.55, 1.05, 'out_cubic')
        if wu > 0:
            m = G.wipe(w, h, wu, angle=0, soft=0.12)
            spr = G.masked(lg, m)
            fly = K.EASE['inout_cubic'](K.ramp(t, 2.18, 2.6, 'linear'))
            x = K.lerp(cx, 64 + G.leam_logo(54, strap=False).shape[1] / 2, fly)
            y = K.lerp(cy + 12, 104 + 22 * 54 / 104, fly)
            s = K.lerp(1.0, 54 / 104, fly)
            K.draw(cv, spr, x, y, scale=s, opacity=1.0 - K.ramp(t, 2.5, 2.62))
        # url chip
        cu = K.spring(t - 1.0, 2.6, 0.6) if t > 1.0 else 0
        if cu > 0:
            txt = 'leamingtonspa-taxis.co.uk'
            tw = G.measure(txt, 26, FONT_B)
            chip, cp = G.panel(int(tw + 70), 48, 24, fill='#FFFFFF', fill_a=0.10, border='#FFC61A',
                               border_a=0.55, border_w=1.5, shadow=0.0)
            K.draw(cv, chip, cx, cy + 112, scale=0.9 + 0.1 * cu, opacity=min(1, cu) * (1 - a_out))
            gl = ui.icon('globe', 26, color=Y, stroke=2.2)
            K.draw(cv, gl, cx - tw / 2 - 6, cy + 112, opacity=min(1, cu) * (1 - a_out))
            G.draw_text(cv, txt, cx - tw / 2 + 16, cy + 121, 26, FONT_B, '#FFFFFF', 'ls',
                        opacity=min(1, cu) * (1 - a_out))


def lower_third(cv, t, t0=2.95, t1=5.35):
    if not (t0 <= t < t1):
        return
    u_in = K.ramp(t, t0, t0 + 0.45, 'out_expo')
    u_out = K.ramp(t, t1 - 0.35, t1, 'in_cubic')
    x0, y0 = 64, 1372
    name, sub = 'Leam Taxis', 'Owner · Leamington Spa'
    w = int(max(G.measure(name, 50, FONT_H), G.measure(sub, 28, FONT_B)) + 76)
    pnl, pad = G.panel(w, 128, 22, fill='#141414', fill_a=0.86, border_a=0.08, accent=Y, accent_w=10, shadow=0.45)
    m = G.wipe(pnl.shape[1], pnl.shape[0], u_in * (1 - u_out) if u_out > 0 else u_in, angle=0, soft=0.08)
    K.draw(cv, G.masked(pnl, m), x0 - pad, y0 - pad, anchor=(0, 0))
    tu = K.ramp(t, t0 + 0.15, t0 + 0.55, 'out_cubic') * (1 - u_out)
    G.draw_text(cv, name, x0 + 38 - 20 * (1 - tu), y0 + 60, 50, FONT_H, '#FFFFFF', 'ls', opacity=tu)
    G.draw_text(cv, sub, x0 + 38 - 20 * (1 - tu), y0 + 102, 28, FONT_B, Y, 'ls', opacity=tu)


@functools.lru_cache(maxsize=1)
def _site_page():
    """The homepage, top 1600 px of the full capture, at card width (scrollable)."""
    return G.image_crop(LEAM_FULL, (0, 0, 1440, 2060), 860)


def site_card(cv, t, t0=5.45, t1=7.9):
    """Browser card with the live site; scrolls to the services; the cursor clicks 'Calculate price'."""
    if not (t0 <= t < t1):
        return
    fr = G.browser_frame(860, 450, 'leamingtonspa-taxis.co.uk')
    sc = 70.0 * K.EASE['inout_cubic'](K.ramp(t, 5.95, 6.7, 'linear'))
    card = G.browser_view(fr, _site_page(), sc)
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.42, 'out_cubic'), angle=-90, soft=0.10)
    cx, cy = 540, 470 - 40 * (1 - u) - 120 * out
    card.draw(cv, cx, cy, scale=0.92 + 0.08 * u, opacity=1 - out, mask=reveal)


def site_cursor(cv, t, t0=5.45, t1=7.9):
    """Cursor -> 'Calculate price' on the site card (form button at (1020, 569) in the capture); in front."""
    if not (t0 + 0.5 < t < t1):
        return
    sc = 70.0 * K.EASE['inout_cubic'](K.ramp(t, 5.95, 6.7, 'linear'))
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    u = K.spring(t - t0, 2.3, 0.62)
    cx, cy = 540, 470 - 40 * (1 - u) - 120 * out
    s = 860 / 1440
    bx = cx - 430 + 1020 * s
    by = cy - (58 + 450) / 2 + 58 + 569 * s - sc
    ct = K.EASE['inout_cubic'](K.ramp(t, t0 + 0.5, 7.05, 'linear'))
    x = K.lerp(bx + 220, bx + 10, ct)
    y = K.lerp(by + 260, by + 6, ct)
    ui.draw_cursor(cv, x, y, 'hand', 62, press=K.impulse(t, 7.12, 9), click=t - 7.12 if t > 7.12 else None,
                   opacity=1 - out)


# ----- shot 2 overlay cards
def card_calls(cv, t, t0=8.35, t1=16.92):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.2, 0.62)
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    w, h = 660, 210
    cx, cy = 400, 330 - 30 * (1 - u) - 90 * out
    pnl, pad = G.panel(w, h, 30, fill='#121212', fill_a=0.84, border='#FFFFFF', border_a=0.10, accent=Y, accent_w=9)
    m = G.wipe(pnl.shape[1], pnl.shape[0], K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=0, soft=0.10)
    K.draw(cv, G.masked(pnl, m), cx, cy, opacity=1 - out, frost=8)
    op = K.ramp(t, t0 + 0.2, t0 + 0.5) * (1 - out)
    x0, y0 = cx - w / 2 + 44, cy - h / 2
    ic = ui.icon('phone', 30, color=Y, stroke=2.4)
    K.draw(cv, ic, x0 + 14, y0 + 46, opacity=op)
    G.draw_text(cv, 'Calls from Google Business Profile', x0 + 42, y0 + 56, 28, FONT_B, '#E8E8E8', 'ls', opacity=op)
    # the count runs with the line under his finger (running total read along the line)
    n = int(round(S.total_at(S.front_x(t))))
    G.draw_text(cv, str(n), x0, y0 + 160, 112, FONT_H, '#FFFFFF', 'ls', opacity=op)
    G.draw_text(cv, 'calls', x0 + G.measure('114', 112, FONT_H) + 18, y0 + 160, 50, FONT_HB, Y, 'ls', opacity=op)
    G.draw_text(cv, 'Running total', x0 + 380, y0 + 128, 30, FONT_B, '#FFFFFF', 'ls', opacity=op)
    G.draw_text(cv, 'May–Oct 2026', x0 + 380, y0 + 164, 26, FONT_R, '#BDBDBD', 'ls', opacity=op)


def card_sept(cv, t, t0=T_HERE + 0.05, t1=16.92):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.6, 0.55)
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    w, h = 600, 120
    cx, cy = 640, 488 - 20 * (1 - u) - 90 * out
    pnl, pad = G.panel(w, h, 26, fill=Y, fill_a=0.96, border_a=0.0, shadow=0.45)
    K.draw(cv, pnl, cx, cy, scale=0.85 + 0.15 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out))
    op = K.ramp(t, t0 + 0.1, t0 + 0.35) * (1 - out)
    x0, y0 = cx - w / 2 + 34, cy - h / 2
    G.draw_text(cv, 'Sept 2026: 25 calls', x0, y0 + 60, 52, FONT_H, K_, 'ls', opacity=op)
    G.draw_text(cv, 'the best of the six months shown · Oct is a part month', x0, y0 + 98, 23, FONT_B, K_, 'ls',
                opacity=op)


# ----- shot 3 cards
def hero_card(cv, t, t0=17.35, t1=22.55):
    if not (t0 <= t < t1):
        return
    card = G.browser_card(LEAM_SITE, (0, 40, 1440, 620), 880, 'leamingtonspa-taxis.co.uk')
    u = K.spring(t - t0, 2.3, 0.62)
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    reveal = G.rrect_grow(card.w, card.h, K.EASE['out_expo'](K.ramp(t, t0, t0 + 0.5, 'linear')), 26, 0.5, 0.5, 120, 40)
    cx, cy = 540, 410 - 30 * (1 - u) - 120 * out
    card.draw(cv, cx, cy, scale=0.94 + 0.06 * u, opacity=1 - out, mask=reveal)
    # marker under the H1 "LEAMINGTON SPA TAXIS -" while he says "taxis in Leamington Spa"
    mk = K.ramp(t, 20.5, 21.3, 'inout_cubic') * (1 - out)
    if mk > 0:
        s = 880 / 1440
        x0 = cx - 440 + 172 * s
        y0 = cy - card.h / 2 + 58 + (408 - 40) * s
        bw, bh = (668 - 172) * s, 46 * s
        bar = np.zeros((int(bh), int(bw) + 2, 4), np.float32)
        bar[..., :3] = G.lin(Y)
        bar[..., 3] = 1
        m = G.wipe(bar.shape[1], bar.shape[0], mk, angle=0, soft=0.05)
        K.draw(cv, G.masked(bar, m), x0, y0, anchor=(0, 0), mode='multiply', opacity=0.75)


def calls_card(cv, t, t0=22.6, t1=24.05):
    if not (t0 <= t < t1):
        return
    u = K.spring(t - t0, 2.6, 0.55)
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    w, h = 760, 190
    cx, cy = 540, 390 - 20 * (1 - u) - 80 * out
    pnl, pad = G.panel(w, h, 34, fill='#121212', fill_a=0.86, border='#FFFFFF', border_a=0.10)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=min(1, (t - t0) / 0.1) * (1 - out), frost=8)
    op = K.ramp(t, t0 + 0.08, t0 + 0.3) * (1 - out)
    # ringing phone in a yellow disc with ripples
    px, py = cx - w / 2 + 100, cy
    for k in range(2):
        ph = ((t - t0) * 1.6 + k * 0.5) % 1.0
        rg = K.ring(52 + 50 * ph, 3, G.lin(Y))
        K.draw(cv, rg, px, py, opacity=op * (1 - ph) * 0.8)
    K.draw(cv, K.disc(52, G.lin(Y)), px, py, opacity=op)
    wig = 9 * math.sin((t - t0) * 40) * max(0.0, 1 - (t - t0) / 1.2)
    K.draw(cv, ui.icon('phone', 52, color=K_, stroke=2.6), px, py, rot=wig, opacity=op)
    x0 = px + 90
    G.draw_text(cv, '114 calls', x0, cy + 6, 74, FONT_H, '#FFFFFF', 'ls', opacity=op)
    G.draw_text(cv, 'from Google Business Profile · May–Oct 2026', x0, cy + 52, 25, FONT_B, '#D0D0D0', 'ls',
                opacity=op)


def airports_card(cv, t, t0=24.0, t1=25.5):
    if not (t0 <= t < t1):
        return
    card = G.browser_card(LEAM_FULL, (100, 4496, 1220, 162), 900, 'leamingtonspa-taxis.co.uk')
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.4, 'out_cubic'), angle=0, soft=0.12)
    cx, cy = 540 + 60 * (1 - u), 410 - 80 * out
    card.draw(cv, cx, cy, opacity=1 - out, mask=reveal)
    op = K.ramp(t, t0 + 0.2, t0 + 0.45) * (1 - out)
    txt = 'Airport transfers · on the website'
    tw = G.measure(txt, 26, FONT_B)
    chip, cp = G.panel(int(tw + 40), 46, 23, fill='#141414', fill_a=0.85, border_a=0.0, shadow=0.3)
    K.draw(cv, chip, cx, cy + card.h / 2 + 46, opacity=op)
    G.draw_text(cv, txt, cx, cy + card.h / 2 + 55, 26, FONT_B, Y, 'ms', opacity=op)


def drivers_card(cv, t, t0=25.45, t1=27.75):
    if not (t0 <= t < t1):
        return
    crop = (110, 2850, 720, 460)
    card = G.browser_card(LEAM_FULL, crop, 600, 'leamingtonspa-taxis.co.uk')
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    reveal = G.wipe(card.w, card.h, K.ramp(t, t0, t0 + 0.45, 'out_cubic'), angle=-90, soft=0.12)
    cx, cy = 470, 395 - 30 * (1 - u) - 100 * out
    card.draw(cv, cx, cy, scale=0.94 + 0.06 * u, opacity=1 - out, mask=reveal)


def drivers_cursor(cv, t, t0=25.45, t1=27.75):
    """Cursor clicks 'BECOME A DRIVER' (button centre (276, 3265) in the full capture); in front."""
    if not (t0 + 0.4 < t < t1):
        return
    card = G.browser_card(LEAM_FULL, (110, 2850, 720, 460), 600, 'leamingtonspa-taxis.co.uk')
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.28, t1, 'in_cubic')
    cx, cy = 470, 395 - 30 * (1 - u) - 100 * out
    s = 600 / 720
    bx = cx - 300 + (276 - 110) * s
    by = cy - card.h / 2 + 58 + (3265 - 2850) * s
    ct = K.EASE['inout_cubic'](K.ramp(t, t0 + 0.4, 26.55, 'linear'))
    x = K.lerp(bx + 300, bx, ct)
    y = K.lerp(by + 220, by, ct)
    ui.draw_cursor(cv, x, y, 'hand', 62, press=K.impulse(t, 26.62, 9), click=t - 26.62 if t > 26.62 else None,
                   opacity=1 - out)


def end_card(cv, t, t0=29.35):
    if t < t0:
        return
    # yellow sweep line
    lw = 760 * K.EASE['inout_cubic'](K.ramp(t, t0 + 0.1, t0 + 0.7, 'linear'))
    if lw > 2:
        bar = np.zeros((6, int(lw), 4), np.float32)
        bar[..., :3] = G.lin(Y)
        bar[..., 3] = 1
        K.draw(cv, bar, 540, 930)
    lg = G.leam_logo(110, strap=True, strap_color='#FFFFFF')
    lu = K.spring(t - (t0 + 0.15), 2.2, 0.6) if t > t0 + 0.15 else 0
    K.draw(cv, lg, 540, 760 - 30 * (1 - lu), scale=0.9 + 0.1 * lu, opacity=min(1, lu))
    G.draw_text(cv, 'leamingtonspa-taxis.co.uk', 540, 885, 30, FONT_B, '#FFFFFF', 'ms',
                opacity=K.ramp(t, t0 + 0.3, t0 + 0.6))
    hu = K.spring(t - (t0 + 0.55), 2.2, 0.6) if t > t0 + 0.55 else 0
    G.draw_text(cv, 'Results by', 540, 1010, 30, FONT_B, '#BDBDBD', 'ms', opacity=K.ramp(t, t0 + 0.55, t0 + 0.8))
    hulk = G.image_logo(HULK, 600)
    K.draw(cv, hulk, 540, 1085 + 20 * (1 - hu), scale=0.92 + 0.08 * hu, opacity=min(1, hu))
    cu = K.spring(t - (t0 + 0.9), 2.4, 0.6) if t > t0 + 0.9 else 0
    txt = 'googlerankerpro.com'
    tw = G.measure(txt, 38, FONT_HB)
    pill, pp = G.panel(int(tw + 96), 84, 42, fill=Y, fill_a=1.0, border_a=0.0, shadow=0.45)
    K.draw(cv, pill, 540, 1235, scale=0.85 + 0.15 * cu, opacity=min(1, cu * 1.5))
    G.draw_text(cv, txt, 540, 1248, 38, FONT_HB, K_, 'ms', opacity=min(1, cu * 1.5))
    fp = K.ramp(t, t0 + 1.2, t0 + 1.5)
    G.draw_text(cv, 'Data: Leam Taxis’ Google Business Profile, May–Oct 2026 (Oct part month).', 540, 1350, 22,
                FONT_R, '#CFCFCF', 'ms', opacity=fp)
    G.draw_text(cv, 'AI re-creation of the client’s testimonial. Results vary by business.', 540, 1384, 22,
                FONT_R, '#CFCFCF', 'ms', opacity=fp)


# ---------------------------------------------------------------------------------------------- module contract
def draw(t):
    cv = plate(t)
    # behind the speaker
    site_card(cv, t)
    hero_card(cv, t)
    calls_card(cv, t)
    airports_card(cv, t)
    drivers_card(cv, t)
    person_over(cv, t)
    # in front
    intro(cv, t)
    card_calls(cv, t)
    card_sept(cv, t)
    site_cursor(cv, t)
    drivers_cursor(cv, t)
    if t < 29.3:
        G.bottom_shade(cv, 0.45, 1330, opacity=1 - K.ramp(t, 29.0, 29.3))
    lower_third(cv, t)
    if t < 29.25:
        CAP.draw(cv, t)
    logo_bug(cv, t)
    ai_label(cv, t)
    end_card(cv, t)
    return np.ascontiguousarray(cv, dtype=np.float32)


def post(cv, t):
    cv = np.ascontiguousarray(cv, dtype=np.float32)
    K.vignette(cv, 0.16, 0.8, 1.8)
    K.grain(cv, t, 0.011, 1.2)
    cv[..., 3] = 1.0
    return cv


FAST = [(0.0, 0.8), (2.15, 2.7), (5.4, 5.9), (7.8, 8.2), (8.3, 8.8), (14.2, 14.6), (16.8, 17.8), (22.5, 22.9),
        (23.95, 24.5), (25.4, 25.95), (29.3, 30.2)]


def samples(t):
    return 3 if any(a <= t < b for a, b in FAST) else 1


# ---------------------------------------------------------------------------------------------- sound cues
def _point_times():
    """When the reveal front passes each real data point (May..Oct) - a small pop each, rising in pitch."""
    out = []
    ts = np.arange(T_CUT1, T_CUT2, 1 / 96.0)
    fx = np.array([S.front_x(t) for t in ts])
    for k in range(6):
        sx = S.pt(k)[0]
        hit = np.nonzero(fx >= sx - 1)[0]
        if len(hit):
            out.append((k, float(ts[hit[0]])))
    return out


def cues():
    c = [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.72, name='impact_soft', gain_db=-6),
        dict(t=0.62, name='swish_small', gain_db=-3, pan=-0.2),
        dict(t=1.02, name='pop', gain_db=-6, params=dict(pitch=1.1)),
        dict(t=2.38, name='whoosh_fast', gain_db=-9, pan=-0.4),
        dict(t=2.98, name='swish_small', gain_db=-5, pan=-0.3),
        dict(t=5.50, name='whoosh_fast', gain_db=-7),
        dict(t=7.12, name='ui_click', gain_db=-3),
        dict(t=8.00, name='whip', gain_db=-5),
        dict(t=8.40, name='card_slide', gain_db=-7, pan=-0.3),
        dict(t=10.05, name='grow_swell', gain_db=-16, align='start', params=dict(duration=3.2)),
        dict(t=T_HERE, name='toast_chime', gain_db=-7, pan=0.2),
        dict(t=16.98, name='air_zoom', gain_db=-9),
        dict(t=17.42, name='whoosh_fast', gain_db=-8),
        dict(t=20.55, name='shimmer', gain_db=-14),
        dict(t=22.62, name='glass_tap', gain_db=-7),
        dict(t=22.70, name='ripple', gain_db=-16, params=dict(dur=1.2)),
        dict(t=24.02, name='swish_small', gain_db=-6, pan=0.3),
        dict(t=25.48, name='whoosh_fast', gain_db=-9),
        dict(t=26.62, name='ui_click', gain_db=-3),
        dict(t=29.35, name='logo_sting', gain_db=-4),
        dict(t=30.28, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]
    for k, tt in _point_times():
        if tt > T_CUT1 + 0.05:
            c.append(dict(t=tt, name='pop', gain_db=-15, params=dict(pitch=0.9 + 0.08 * k), pan=-0.6 + 0.24 * k))
    return c


def prewarm():
    S.base_screen()
    S.line_layer()
    G.leam_logo(104, True, '#FFFFFF')
    G.leam_logo(54, False)
    G.leam_logo(110, True, '#FFFFFF')
    _site_page()
