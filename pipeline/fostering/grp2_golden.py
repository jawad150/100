"""grp2_golden.py: Golden Line Taxis (Warwick) client testimonial (Google Ranker Pro), 9:16, 24 fps, 28 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp2_golden --audio <mix.wav>

Source: workspace3/frames/golden (Seedance clip hf_20261024_072608, 25.04 s): shot 1 over the shoulder at a green
laptop, she turns to camera, 0-9.04 s; shot 2 side view at the desk by the window, 9.04-16.25 s; shot 3 medium
close-up, 16.25-25.04 s. End card from 25.0 s.

BEFORE / AFTER: the green laptop screen shows
  * before: an ILLUSTRATION of a dated site (assets/sites/goldenlinetaxiswarwick/before_mock, made for this video at
    the client's request; it is labelled 'Illustration' on screen and in the end-card fine print);
  * after: the real goldenlinetaxiswarwick.co.uk (captured 22 Oct 2026), revealed with a before/after divider
    on "Then Google Ranker Pro rebuilt it", as on googlerankerpro.com's own comparison slider.
The phone on the stand (shot 2) had a made-up logo on its screen: it is cleaned to a dark screen, then lights up
with the real mobile site after the rebuild. The green laptop at the edge of shot 3 shows the real site, defocused.

Data: Google Search Console, goldenlinetaxiswarwick.co.uk, 3-month preset (about 19 Jul - 18 Oct 2026):
312 clicks, 18.2K impressions; top queries 'golden line taxis warwick' (avg position 1.8), 'warwick airport taxi'
(6.1), 'kenilworth taxis' (6.7). No booking numbers exist, so "bookings ... busiest channel" stays a spoken claim.
"""
import functools
import json
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

DUR = 28.0
LOOK = 'natural'
BPM = 92
N_SRC = 601
T_END_CARD = 25.0
T_REBUILD = 11.22                     # "rebuilt it"

F.GRADES['golden_room'] = dict(wb=(1.015, 1.0, 0.985), exposure=0.02, contrast=1.10, pivot=0.42, black=0.018,
                               black_tint=(0.11, 0.10, 0.11), shadow_tint=(-0.002, 0.0, 0.008),
                               highlight_tint=(0.010, 0.006, -0.006), sat=1.02, shoulder=0.92)

GL = lambda *p: G.site('goldenlinetaxiswarwick', *p)            # noqa: E731
BEFORE_D = GL('before_mock', 'before_desktop.png')
BEFORE_M = GL('before_mock', 'before_mobile.png')
# the live site's hero tagline ('No.1 Taxi Hire & Airport Transfer Company in Warwick') is painted out: it would
# read as a ranking claim in a Google Ranker Pro testimonial and nothing backs it (noted in the end-card fine print)
AFTER_D = GL('now_desktop_notag.png')
AFTER_M = GL('now_mobile_notag.png')
LOGO = GL('logo.png')
URL = 'goldenlinetaxiswarwick.co.uk'

Q2 = [[40.0, 1096.0], [378.0, 1062.0], [439.0, 1321.0], [101.0, 1382.0]]      # shot 2 display (2 px overscan)
QP = [[507.0, 1079.0], [589.0, 1077.0], [640.0, 1263.0], [535.0, 1268.0]]     # shot 2 phone on the stand
Q3 = [[-560.0, 1040.0], [130.0, 1026.0], [168.0, 1430.0], [-560.0, 1450.0]]   # shot 3 laptop (mostly off frame)


@functools.lru_cache(maxsize=1)
def _quads1():
    with open(os.path.join(G.GRP, 'golden_quads.json')) as f:
        return {int(k): v for k, v in json.load(f).items()}


@functools.lru_cache(maxsize=8)
def _img(path):
    im = G._rgb(path)
    return np.ascontiguousarray(im[..., :3]).astype(np.float32)


def _before_loading(t):
    """'Slow': the old page repaints piece by piece (header, nav, sidebar, body)."""
    page = _img(BEFORE_D).copy()
    if not (6.08 <= t < 7.45):
        return page
    steps = [(6.08, 0), (6.35, 150), (6.62, 180), (6.95, 660), (7.25, 690), (7.45, 900)]
    y = 0
    for ts, yy in steps:
        if t >= ts:
            y = yy
    page[y:] = 255.0
    if y < 900:
        # 'loading' line under what has drawn so far
        u8 = page.astype(np.uint8)
        cv2.putText(u8, 'Loading...', (520, max(y, 180) + 80), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (120, 120, 120), 2,
                    cv2.LINE_AA)
        page = u8.astype(np.float32)
    return page


def _divider(page_l, page_r, u):
    """Before / after comparer: the AFTER page sweeps in from the left behind a white divider with a handle."""
    w = page_l.shape[1]
    x = int(round(u * w))
    out = page_r.astype(np.uint8)
    out[:, :x] = page_l[:, :x]
    if 0 < x < w:
        cv2.rectangle(out, (x - 4, 0), (x + 4, out.shape[0]), (255, 255, 255), -1)
        cy = out.shape[0] // 2
        cv2.circle(out, (x, cy), 46, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(out, (x, cy), 46, (0, 110, 184), 4, cv2.LINE_AA)
        for s in (-1, 1):
            pts = np.array([[x + s * 12, cy - 14], [x + s * 26, cy], [x + s * 12, cy + 14]], np.int32)
            cv2.polylines(out, [pts], False, (0, 110, 184), 5, cv2.LINE_AA)
    return out.astype(np.float32)


def desktop_content(t):
    if t < T_REBUILD:
        return _before_loading(t)
    u = K.EASE['inout_cubic'](K.ramp(t, T_REBUILD, T_REBUILD + 0.75, 'linear'))
    if u >= 1:
        return _img(AFTER_D)
    return _divider(_img(AFTER_D), _img(BEFORE_D), u)


@functools.lru_cache(maxsize=1)
def _phone_dark():
    """A clean dark phone screen (the generated one carried a made-up logo)."""
    h, w = 400, 190
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    return np.broadcast_to((22 + 10 * y) * np.array([1.0, 1.04, 1.12], np.float32), (h, w, 3)).copy()


@functools.lru_cache(maxsize=1)
def _region3():
    m = np.zeros((K.H, K.W), np.float32)
    m[980:1200, :240] = 1.0
    return cv2.GaussianBlur(m, (0, 0), 3)


@functools.lru_cache(maxsize=1)
def _kb_mask():
    m = np.zeros((K.H, K.W), np.float32)
    cv2.fillConvexPoly(m, np.array([[100, 1330], [470, 1290], [600, 1400], [170, 1470]], np.int32), 1.0)
    return cv2.GaussianBlur(m, (0, 0), 12)


def _despill_keyboard(fr):
    """The keyboard under the (formerly green) screen still glows green: pull G down to max(R, B) there."""
    m = _kb_mask()[1250:1520, 60:660]
    sub = fr[1250:1520, 60:660].astype(np.float32)
    g2 = np.minimum(sub[..., 1], np.maximum(sub[..., 0], sub[..., 2]) + 3)
    out = fr.copy()
    out[1250:1520, 60:660, 1] = np.clip(sub[..., 1] * (1 - m) + g2 * m + 0.5, 0, 255).astype(np.uint8)
    return out


def prep(fr, fi):
    t = fi / 24.0
    if fi <= 216:
        q = _quads1()[fi]
        return GB.green_replace(fr, q, desktop_content(t))
    if fi <= 389:
        fr = GB.green_replace(fr, Q2, desktop_content(t))
        fr = _despill_keyboard(fr)
        on = K.ramp(t, T_REBUILD + 0.5, T_REBUILD + 0.9)
        fr = GB.paste_quad(fr, QP, _phone_dark(), feather=1.0, blur=0.4)
        if on > 0:
            page = _img(AFTER_M)[:1530]
            fr = GB.paste_quad(fr, [[p[0], p[1]] for p in QP], page, feather=1.0, gain=0.86, blur=0.9, opacity=on)
        return fr
    return GB.green_replace(fr, Q3, _img(AFTER_D), defocus=5.0, region=_region3(), shade=False)


CLIP = GB.Clip('golden', N_SRC, [
    (0, 216, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.0, z1=1.04)),
    (217, 389, dict(c0=(0.5, 0.52), c1=(0.5, 0.52), z0=1.0, z1=1.045)),
    (390, 600, dict(c0=(0.5, 0.48), c1=(0.5, 0.47), z0=1.03, z1=1.07)),
], 'golden_room', prep=prep)

WORDS = G.load_words('golden', fixes={29: 'cab', 43: 'busiest'})
CAP = B.captions(WORDS, max_chars=30, breaks=(20, 35))


# ---------------------------------------------------------------------------------------------- pieces
def client_card(cv, t, t0=0.35, t1=2.35):
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 470, 196
    cx, cy = 275, 300 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 32)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    tu = K.ramp(t, t0 + 0.2, t0 + 0.5, 'out_cubic') * (1 - out)
    G.draw_text(cv, 'CLIENT STORY', cx, cy - 52, 21, B.FS, B.BODY, 'ms', opacity=tu, tracking=0.2)
    lg = G.image_logo(LOGO, 300)
    m = G.wipe(lg.shape[1], lg.shape[0], K.ramp(t, t0 + 0.15, t0 + 0.6, 'out_cubic'), angle=0, soft=0.12)
    K.draw(cv, G.masked(lg, m), cx, cy + 6, opacity=1 - out)
    G.draw_text(cv, URL, cx, cy + 72, 22, B.FM, B.ACTION, 'ms', opacity=tu)


def tag(cv, t, text, x, y, t0, t1, fill=B.INK, color='#FFFFFF', size=24, icon=None):
    if not (t0 <= t < t1):
        return
    spr, pad, w, h = B.chip(text, icon, size, fill=fill, color=color, icon_color=color, border_a=0.0, shadow=0.25)
    u, out, op = B.pop(t, t0, t1, fout=0.2)
    K.draw(cv, spr, x + w / 2, y + 12 * (1 - u), scale=0.9 + 0.1 * u, opacity=op)


def before_tags(cv, t):
    # shot 1: on the laptop's top edge; shot 2: above the small laptop
    tag(cv, t, 'BEFORE  ·  illustration', 50, 742, 2.15, 9.0, fill='#3A3F47')
    tag(cv, t, 'BEFORE  ·  illustration', 44, 1010, 9.1, T_REBUILD + 0.15, fill='#3A3F47', size=22)
    tag(cv, t, 'AFTER  ·  live site', 44, 1010, T_REBUILD + 0.35, 12.45, fill=B.ACTION, size=22)


def broken_phone(cv, t, t0=6.72, t1=7.92):
    """'...broken on phones': the illustrated old page on a phone, too small to use."""
    if not (t0 <= t < t1):
        return
    crd = B.phone_card(BEFORE_M, (0, 0, 780, 1450), 250)
    u = K.spring(t - t0, 2.4, 0.6)
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    crd.draw(cv, 210 - 260 * out, 450 + 40 * (1 - u), rot=-5 + 3 * (1 - u), opacity=min(1, (t - t0) / 0.1) * (1 - out))
    # red 'x' badge
    bu = K.spring(t - (t0 + 0.25), 3.0, 0.5) if t > t0 + 0.25 else 0
    if bu > 0:
        K.draw(cv, K.disc(30, G.lin('#D93025')), 318 - 260 * out, 190 + 40 * (1 - u), scale=bu, opacity=1 - out)
        K.draw(cv, ui.icon('plus', 34, color='#FFFFFF', stroke=3.4), 318 - 260 * out, 190 + 40 * (1 - u), rot=45,
               scale=bu, opacity=1 - out)


def lost_search(cv, t, t0=7.9, t1=9.0):
    """'...and nobody could find it': a search that shakes (no fake results shown)."""
    if not (t0 <= t < t1):
        return
    shake = 0.0
    if t > 8.42:
        shake = 12 * math.sin((t - 8.42) * 40) * math.exp(-(t - 8.42) * 6)
    B.search_bar(cv, t, 'taxi Warwick', t0, t1, cx=280 + shake, cy=250, w=470, h=96, type_dur=0.4, size=34)


def grp(cv, t, t0=10.1, t1=12.2):
    GB.card_in(cv, B.grp_card(460, 186), t, t0, t1, 360, 420, rise=36)


@functools.lru_cache(maxsize=1)
def _after_card():
    return GB.site_card(AFTER_D, (0, 80, 1440, 540), 640, URL)


def after_card(cv, t, t0=12.3, t1=14.6):
    """'Look at that.': the rebuilt site lifts off the laptop into a browser window."""
    if not (t0 <= t < t1):
        return
    crd = _after_card()
    u = K.EASE['out_cubic'](K.ramp(t, t0, t0 + 0.6, 'linear'))
    out = K.ramp(t, t1 - 0.3, t1, 'in_cubic')
    x = K.lerp(240, 362, u)
    y = K.lerp(1220, 600, u) - 30 * out
    s = K.lerp(0.48, 1.0, u)
    crd.draw(cv, x, y, scale=s * (1 - 0.06 * out), opacity=min(1, (t - t0) / 0.08) * (1 - out))


@functools.lru_cache(maxsize=1)
def _phone_after():
    return B.phone_card(AFTER_M, (0, 0, 780, 1688), 300)


def two_taps(cv, t, t0=14.5, t1=16.2):
    """'...book a cab in two taps': the real mobile site, two taps marked 1 and 2."""
    if not (t0 <= t < t1):
        return
    crd = _phone_after()
    u = K.spring(t - t0, 2.4, 0.62)
    out = K.ramp(t, t1 - 0.25, t1, 'in_cubic')
    cx, cy = 330, 560 + 40 * (1 - u) - 30 * out
    op = min(1, (t - t0) / 0.1) * (1 - out)
    crd.draw(cv, cx, cy, scale=0.92 + 0.08 * u, opacity=op)
    bez = crd.content[0]
    sw = crd.content[2]
    k = sw / 780.0
    x0 = cx - crd.w / 2 + bez
    y0 = cy - crd.h / 2 + bez
    for n, (px, py, tt) in enumerate([(192, 1640, 15.02), (390, 1172, 15.52)], 1):
        if t < tt:
            continue
        X, Y = x0 + px * k, y0 + py * k
        r = (t - tt)
        ring = 26 + 60 * K.EASE['out_cubic'](K.clamp(r / 0.5))
        K.draw(cv, K.ring(ring, 4, G.lin(B.ACTION)), X, Y, opacity=(1 - K.clamp(r / 0.5)) * op)
        bu = K.spring(r, 3.0, 0.55)
        K.draw(cv, K.disc(24, G.lin(B.ACTION)), X + 46, Y - 40, scale=bu, opacity=op)
        G.draw_text(cv, str(n), X + 46, Y - 40, 28, B.FB, '#FFFFFF', 'mm', opacity=op * min(1, bu))


@functools.lru_cache(maxsize=1)
def _book_widget():
    return GB.site_card(AFTER_D, (205, 290, 462, 316), 430, URL)


def booking_card(cv, t, t0=18.05, t1=20.55):
    """'Online bookings...': the site's real Quote & Book widget."""
    GB.card_in(cv, _book_widget(), t, t0, t1, 300, 262, rise=30)


def _count(t, t0, v, dur=0.9):
    return v * K.EASE['out_cubic'](K.clamp((t - t0) / dur))


def gsc_card(cv, t, t0=20.6, t1=22.85):
    """Search Console totals (real, last 3 months)."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 930, 262
    cx, cy = 540, 258 + 30 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.92 + 0.08 * u, opacity=op)
    x0, y0 = cx - w / 2, cy - h / 2
    G.draw_text(cv, 'Google Search Console  ·  last 3 months', x0 + 40, y0 + 52, 26, B.FS, B.BODY, 'ls', opacity=op)
    c = _count(t, t0 + 0.2, 312)
    G.draw_text(cv, '%d' % round(c), x0 + 40, y0 + 160, 92, B.FB, '#1A73E8', 'ls', opacity=op)
    G.draw_text(cv, 'clicks from Google', x0 + 44, y0 + 214, 28, B.FM, B.INK, 'ls', opacity=op)
    imp = _count(t, t0 + 0.35, 18.2)
    G.draw_text(cv, '%.1fK' % imp, x0 + 500, y0 + 160, 92, B.FB, '#7B3FC4', 'ls', opacity=op)
    G.draw_text(cv, 'impressions in search', x0 + 504, y0 + 214, 28, B.FM, B.INK, 'ls', opacity=op)
    S = ui.Surf(4, 150)
    S.rrect(0, 0, 3, 150, 1.5, G.lin(B.BORDER), 1.0)
    K.draw(cv, S.img, x0 + 462, y0 + 150, opacity=op)


QUERIES = [('golden line taxis warwick', '1.8'), ('warwick airport taxi', '6.1'), ('kenilworth taxis', '6.7')]


def queries_card(cv, t, t0=22.95, t1=24.95):
    """'Warwick finally knows we exist': real top queries with their average positions."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 930, 290
    cx, cy = 540, 272 + 30 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.92 + 0.08 * u, opacity=op)
    x0, y0 = cx - w / 2, cy - h / 2
    G.draw_text(cv, 'Searches finding the site', x0 + 40, y0 + 50, 26, B.FS, B.BODY, 'ls', opacity=op)
    G.draw_text(cv, 'avg. position', x0 + w - 40, y0 + 50, 22, B.FM, B.BODY, 'rs', opacity=op)
    for k, (q, p) in enumerate(QUERIES):
        ru = K.ramp(t, t0 + 0.15 + 0.18 * k, t0 + 0.45 + 0.18 * k, 'out_cubic') * op
        y = y0 + 112 + k * 66
        K.draw(cv, ui.icon('search', 30, color=B.ACTION, stroke=2.4), x0 + 58, y - 10, opacity=ru)
        G.draw_text(cv, q, x0 + 92, y, 32, B.FS, B.INK, 'ls', opacity=ru)
        G.draw_text(cv, p, x0 + w - 40, y, 34, B.FB, B.ACTION, 'rs', opacity=ru)
        if k < 2:
            S = ui.Surf(int(w - 80), 3)
            S.rrect(0, 0, w - 80, 2, 1, G.lin(B.BORDER), 1.0)
            K.draw(cv, S.img, cx, y + 26, opacity=ru)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    cv = CLIP.plate(t, {0: 'band', 1: 'grow'}, end_t0=T_END_CARD - 0.15)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        client_card(cv, t)
        broken_phone(cv, t)
        lost_search(cv, t)
        grp(cv, t)
        after_card(cv, t)
        two_taps(cv, t)
        booking_card(cv, t)
        gsc_card(cv, t)
        queries_card(cv, t)
        CLIP.person_over(cv, t, skip=[(-1.0, 0.8)])
        before_tags(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD))
        CAP.draw(cv, t, opacity=1 - K.ramp(t, T_END_CARD - 0.3, T_END_CARD - 0.05, 'inout_sine'))
        B.logo_bug(cv, t, 2.4, 17.9)
    B.ai_label(cv, t, solid=t >= T_END_CARD,
               text='AI re-creation · old site illustrated' if t < T_REBUILD + 0.4 else
               'AI re-creation · real client website')
    B.end_card(cv, t, T_END_CARD, 'Golden Line Taxis', URL,
               extra_fine=('The “before” website is an illustration; one site tagline removed.',
                           'Search data: Google Search Console, Jul–Oct 2026.'))
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8), (8.85, 9.2), (T_REBUILD, T_REBUILD + 0.8), (12.3, 12.95), (16.1, 16.6),
        (T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    c1, c2 = CLIP.cuts[0][0], CLIP.cuts[1][0]
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.76, name='impact_soft', gain_db=-8),
        dict(t=0.40, name='pop', gain_db=-6, params=dict(pitch=1.05)),
        dict(t=2.18, name='swish_small', gain_db=-9),
        dict(t=6.10, name='glitch_short', gain_db=-15),
        dict(t=6.75, name='card_slide', gain_db=-7, pan=-0.4),
        dict(t=7.00, name='pop', gain_db=-8, params=dict(pitch=0.8), pan=-0.4),
        dict(t=7.92, name='swish_small', gain_db=-7, pan=-0.3),
        dict(t=8.10, name='typing', gain_db=-11, align='start', params=dict(n=10, cps=24)),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=10.12, name='pop', gain_db=-6, params=dict(pitch=1.1), pan=-0.3),
        dict(t=T_REBUILD, name='air_zoom', gain_db=-9, align='start'),
        dict(t=T_REBUILD + 0.75, name='shimmer', gain_db=-13),
        dict(t=12.32, name='whoosh_fast', gain_db=-9, pan=-0.3),
        dict(t=14.52, name='card_slide', gain_db=-7, pan=-0.3),
        dict(t=15.02, name='ui_click', gain_db=-4, pan=-0.3),
        dict(t=15.52, name='ui_click', gain_db=-4, pan=-0.3),
        dict(t=c2, name='air_zoom', gain_db=-10),
        dict(t=18.08, name='swish_small', gain_db=-6, pan=-0.3),
        dict(t=20.62, name='pop', gain_db=-6, params=dict(pitch=1.1)),
        dict(t=20.85, name='typing', gain_db=-14, align='start', params=dict(n=6, cps=8)),
        dict(t=22.97, name='swish_small', gain_db=-6),
        dict(t=23.15, name='check_ding', gain_db=-13),
        dict(t=23.33, name='check_ding', gain_db=-13, params=dict(pitch=1.06)),
        dict(t=23.51, name='check_ding', gain_db=-13, params=dict(pitch=1.12)),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _quads1()
    for p in (BEFORE_D, BEFORE_M, AFTER_D, AFTER_M):
        _img(p)
    _after_card()
    _phone_after()
    _book_widget()
    B.phone_card(BEFORE_M, (0, 0, 780, 1450), 250)
    B.grp_card(460, 186)
    G.image_logo(LOGO, 300)
