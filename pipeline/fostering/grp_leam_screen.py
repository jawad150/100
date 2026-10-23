"""grp_leam_screen.py: the replacement monitor screen for the Leam Taxis edit (shot 2, frames 192-407).

The generated clip shows a green screen with a made-up line that his finger traces up and to the right. His
monthly calls are flat-ish (Google Business Profile, May-Oct 2026: about 19, 17, 20, 21, then 25 in September and
12 in part-month October; 114 in all), so no honest monthly chart can follow that finger. The RUNNING TOTAL of those
same calls does climb steadily, so the screen shows a calls report with the running total, clearly labelled, at a
linear y axis from 0: 19 - 36 - 56 - 77 - 102 - 114. The geometry (month spacing, baseline, px per call) is fitted
to the measured fingertip path (grp_prep.py leam: hand mattes, 'tip2'), so the line sits under his fingertip as it
draws on (rms 26 px, finger pad ~30 px under the line). Only 114 and September's 25 are printed exactly as
reported; the other monthly points are read from the Business Profile chart (labelled on screen).

    front_x(t) -> reveal front (frame px) = fingertip x + lead
    screen_lin(t, fx, t_here) -> linear premultiplied (749, 1080, 4) screen
    look_u8(scr) -> filmed-looking uint8;  composite(frame_u8, i, scr_u8) -> frame with the screen under his hand
"""
import functools
import json
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

import core as K
import grp_kit as G
import ui

Y0, Y1 = 594, 1343                    # display rows in the frame (= the matte crop, 749 rows)
SW, SH = 1080, Y1 - Y0
# chart geometry in FRAME px, fitted to the fingertip path
X0, DX, YB, PPC = 189.95, 155.10, 1290.18, 4.8402     # May x, month spacing, baseline (0 calls), px per call
CUM = [19, 36, 56, 77, 102, 114]                        # running total by month (May..Oct 2026)
MONTHS = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct*']
INK = '#1F1F1F'
YEL = '#FFC61A'
GREY = '#6B6B6B'
WHITE_OUT = np.float32([236, 240, 238]) / 255.0     # filmed monitor white / black (sRGB)
BLACK_OUT = np.float32([26, 30, 32]) / 255.0
FB = 'OpenSans-SemiBold'
FBB = 'OpenSans-Bold'
FR = 'OpenSans-Regular'
FH = 'FiraSansCondensed-ExtraBold'
FHB = 'FiraSansCondensed-Bold'


def pt(k):
    """Frame px of month k's point."""
    return X0 + DX * k, YB - PPC * CUM[k]


def loc(y):
    return y - Y0


def line_y(x):
    xs = [pt(k)[0] for k in range(6)]
    ys = [pt(k)[1] for k in range(6)]
    return float(np.interp(x, xs, ys))


def total_at(fx):
    """Running total read along the line at the front (0 a little before May, 114 at October)."""
    xs = [X0 - 60] + [pt(k)[0] for k in range(6)]
    return float(np.interp(fx, xs, [0] + CUM))


def _supersample(fn, ss=4):
    im = Image.new('RGBA', (SW * ss, SH * ss), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), ss)
    a = np.asarray(im, np.float32) / 255.0
    a = cv2.resize(a, (SW, SH), interpolation=cv2.INTER_AREA)
    out = np.zeros_like(a)
    out[..., :3] = K.to_lin(a[..., :3]) * a[..., 3:4]
    out[..., 3] = a[..., 3]
    return out


def _hex(c, a=255):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


@functools.lru_cache(maxsize=1)
def line_layer():
    """Area fill (Leam yellow) + the line, premultiplied linear (SH, SW, 4); revealed per frame by the front."""
    pts = [(pt(k)[0], loc(pt(k)[1])) for k in range(6)]
    base = loc(YB)

    def fill(d, ss):
        poly = [(x * ss, y * ss) for x, y in pts] + [(pts[-1][0] * ss, base * ss), (pts[0][0] * ss, base * ss)]
        d.polygon(poly, fill=_hex(YEL, 80))

    def line(d, ss):
        d.line([(x * ss, y * ss) for x, y in pts], fill=_hex(INK), width=int(4.5 * ss), joint='curve')
    f = _supersample(fill)
    ln = _supersample(line)
    out = f.copy()
    a = ln[..., 3:4]
    out = out * (1 - a) + ln
    out.setflags(write=False)
    return out


# ---------------------------------------------------------------------------------------------- static page
@functools.lru_cache(maxsize=1)
def base_screen():
    """Browser chrome + the report page (axes, labels, KPI block), linear premultiplied (SH, SW, 4)."""
    S = ui.Surf(SW, SH)
    S.rrect(-10, 0, SW + 20, SH, 0, ui.col('#FFFFFF'), 1.0)
    # tab strip
    S.rrect(-10, 0, SW + 20, 46, 0, ui.col('#DEE1E6'), 1.0)
    S.rrect(118, 6, 330, 44, 12, ui.col('#FFFFFF'), 1.0)
    S.rrect(456, 8, 300, 34, 10, ui.col('#E9EBEE'), 1.0)
    fav = G.image_crop('/home/user/100/workspace3/leam/cropped-Leam-taxis-icon-270x270.png', None, 22)
    ui.paste(S.img, fav, 134, 15)
    S.text(166, 34, 'Leam Taxis · Calls report', 19, FB, '#3C4043')
    ui.paste(S.img, fav, 470, 14)
    S.text(500, 33, 'Leam Taxis | Leamington Spa Taxis', 18, FR, '#5F6368')
    S.text(778, 33, '+', 26, FR, '#5F6368')
    # toolbar
    S.rrect(-10, 46, SW + 20, 46, 0, ui.col('#FFFFFF'), 1.0)
    back = np.ascontiguousarray(ui.icon('arrow_right', 22, color='#5F6368', stroke=2.4)[:, ::-1])
    ui.paste(S.img, back, 20, 58)
    ui.paste(S.img, ui.icon('arrow_right', 22, color='#BDC1C6', stroke=2.4), 56, 58)
    S.circle(104, 69, 9, ui.col('#5F6368'), 1.0)
    S.circle(104, 69, 6.5, ui.col('#FFFFFF'), 1.0)
    S.rrect(140, 52, 820, 34, 17, ui.col('#F1F3F4'), 1.0)
    ui.paste(S.img, ui.icon('book', 18, color='#5F6368', stroke=2.2), 156, 60)
    S.text(184, 75, 'Leam Taxis – Google Business Profile report – Oct 2026', 19, FR, '#202124')
    S.circle(1010, 69, 14, ui.col(YEL), 1.0)
    S.text(1003, 76, 'L', 18, FBB, INK)
    S.rrect(-10, 91, SW + 20, 1, 0, ui.col('#DADCE0'), 1.0)
    # gridlines + y labels (linear axis from 0)
    for v in (0, 30, 60, 90, 120):
        y = loc(YB - PPC * v)
        if v == 0:
            S.rrect(150, y - 1, 890, 2, 0, ui.col('#BDBDBD'), 1.0)
        else:
            for x in range(150, 1040, 14):
                S.rrect(x, y - 0.75, 7, 1.5, 0, ui.col('#E3E3E3'), 1.0)
        S.text(136, round(y + 6), str(v), 17, FR, '#9AA0A6', anchor='rs')
    for k, m in enumerate(MONTHS):
        x, _ = pt(k)
        S.text(round(x), round(loc(YB) + 30), m, 18, FB, '#5F6368', anchor='ms')
    # KPI block (white backing over the gridlines)
    KX = 168
    S.rrect(KX - 14, 104, 560, 222, 18, ui.col('#FFFFFF'), 1.0)
    S.text(KX, 136, 'CALLS FROM GOOGLE BUSINESS PROFILE', 17, FBB, GREY, tracking=0.06)
    adv = S.text(KX - 2, 236, '114', 98, FH, INK)
    S.text(KX - 2 + adv + 12, 236, 'calls', 40, FHB, INK)
    S.rrect(KX, 250, 120, 6, 3, ui.col(YEL), 1.0)
    S.text(KX, 286, 'Running total · May–Oct 2026', 21, FB, '#3C4043')
    S.text(KX, 314, '*Oct is a part month. Monthly points read from the Business Profile chart.', 14, FR, '#8A8A8A')
    S.img.setflags(write=False)
    return S.img


@functools.lru_cache(maxsize=8)
def _dot(r, fill, ring=None, ring_w=0.0, glow=0.0):
    d = int(r * 2 + ring_w * 2 + glow * 3 + 6)
    S = ui.Surf(d, d)
    c = d / 2
    if glow > 0:
        a, X0_, Y0_ = S.circle(c, c, r + ring_w, ui.col(fill), 0.0)
        S.glow(a, X0_, Y0_, ui.col(fill), sigmas=(glow * 0.4, glow), strength=0.8, knock=0.0)
    if ring is not None:
        S.circle(c, c, r + ring_w, ui.col(ring), 1.0)
    S.circle(c, c, r, ui.col(fill), 1.0)
    S.img.setflags(write=False)
    return S.img


@functools.lru_cache(maxsize=4)
def _chip(text, fill, color, size=19, pad=14, h=34):
    w = int(ui.measure(text, size, FBB) + 2 * pad)
    S = ui.Surf(w + 12, h + 16)
    S.rrect(6, 4, w, h, h / 2, ui.col(fill), 1.0)
    S.text(6 + pad, 4 + h / 2 + size * 0.36, text, size, FBB, color)
    S.img.setflags(write=False)
    return S.img


@functools.lru_cache(maxsize=1)
def _total_tip():
    """Dark callout '114 calls in total' with a pointer on its right (for the October end point)."""
    w, h = 214, 50
    S = ui.Surf(w + 30, h + 8)
    S.rrect(2, 2, w, h, 10, ui.col(INK), 1.0)
    a = np.zeros((h + 8, w + 30), np.float32)
    tri = np.array([[w + 1, 14], [w + 16, 27], [w + 1, 40]], np.int32)
    cv2.fillPoly(a, [tri * 1], 1.0)
    S.fill(a, 0, 0, ui.col(INK), 1.0)
    S.text(18, 35, '114', 26, FH, YEL)
    S.text(70, 35, 'calls in total', 19, FB, '#FFFFFF')
    S.img.setflags(write=False)
    return S.img


def screen_lin(t, fx, t_here, t_start=8.0):
    """Linear screen at time t. fx = reveal front in frame px; t_here = 'and then here' (total callout)."""
    scr = base_screen().copy()
    xs = np.arange(SW, dtype=np.float32) + 0.5
    m = np.clip((fx - xs) / 5.0 + 0.5, 0, 1)[None, :, None]
    lay = line_layer()
    scr[:] = scr * (1 - lay[..., 3:4] * m) + lay * m
    x_first, x_last = pt(0)[0], pt(5)[0]
    # hover guide at the front while it moves along the line
    if x_first - 120 < fx < x_last + 2:
        gx = int(round(fx))
        y_top, y_bot = int(loc(YB - PPC * 120)), int(loc(YB))
        seg = ((np.arange(y_bot - y_top) // 7) % 2 == 0).astype(np.float32)[:, None, None] * 0.55
        reg = scr[y_top:y_bot, gx:gx + 2]
        reg[..., :3] = reg[..., :3] * (1 - seg) + K.to_lin(np.float32([0.62, 0.62, 0.62])) * seg
    # points pop as the front passes them
    for k in range(6):
        px, py = pt(k)
        if fx < px - 1:
            continue
        pop = K.spring((fx - px) / 450.0, 2.6, 0.5)
        if k == 4:
            dot = _dot(8.0, YEL, ring=INK, ring_w=3.0)
        else:
            dot = _dot(6.5, '#FFFFFF', ring=INK, ring_w=3.0)
        K.draw(scr, dot, px, loc(py), scale=0.35 + 0.65 * min(1.15, pop))
    # September: the one exact monthly figure
    sx, sy = pt(4)
    if fx >= sx:
        u = K.spring((fx - sx) / 380.0, 2.4, 0.55)
        chip = _chip('+25 in Sept · best month', INK, YEL)
        K.draw(scr, chip, sx - 20, loc(sy) - 40, scale=0.6 + 0.4 * min(1.1, u), opacity=min(1.0, u * 2),
               anchor=(0.62, 0.5))
    # travelling dot riding the line at the front
    if x_first <= fx < x_last:
        K.draw(scr, _dot(7.0, YEL, ring=INK, ring_w=2.5, glow=10.0), fx, loc(line_y(fx)))
    # 'and then here': callout on the 114 end point
    if t >= t_here:
        u = K.spring(t - t_here, 3.0, 0.55)
        ex, ey = pt(5)
        tip = _total_tip()
        K.draw(scr, tip, ex - 14, loc(ey) - 52, anchor=(1.0, 0.5), scale=0.7 + 0.3 * min(1.1, u),
               opacity=min(1.0, (t - t_here) / 0.08))
        K.draw(scr, _dot(9.0, YEL, ring=INK, ring_w=3.0), ex, loc(ey), scale=1.0 + 0.3 * K.impulse(t, t_here, 6))
    return scr


def look_u8(scr_lin, seed=0):
    """Make the clean screen look filmed: monitor white / black levels, slight defocus, falloff, noise."""
    s = K.to_srgb(np.clip(scr_lin[..., :3], 0, 1))
    s = cv2.GaussianBlur(s, (0, 0), 0.85)
    s = BLACK_OUT + (WHITE_OUT - BLACK_OUT) * s
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    v = 1.0 - 0.07 * (((xx - SW * 0.55) / SW) ** 2 * 2.2 + ((yy - SH * 0.4) / SH) ** 2 * 1.6)
    s = s * v[..., None]
    rng = np.random.default_rng(seed)
    s = s * 255.0 + rng.normal(0, 1.6, (SH, SW, 1)).astype(np.float32)
    return np.clip(s + 0.5, 0, 255).astype(np.uint8)


@functools.lru_cache(maxsize=8)
def matte(i):
    p = os.path.join(G.GRP, 'leam_matte', '%05d.png' % i)
    m = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    return None if m is None else m.astype(np.float32) / 255.0


def composite(frame, i, scr_u8):
    """Put the screen into the frame (rows Y0..Y1) under the hand matte; despill the hand edges."""
    out = frame.copy()
    reg = out[Y0:Y1].astype(np.float32)
    a = matte(i)
    if a is None:
        a = np.zeros((SH, SW), np.float32)
    r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
    hand = np.dstack([r, np.minimum(g, np.maximum(r, b) + 4), b])
    ef = np.ones((SH, 1), np.float32)
    ef[0, 0] = 0.6
    ef[-1, 0] = 0.6
    a3 = a[..., None]
    comp = scr_u8.astype(np.float32) * (1 - a3) + hand * a3
    comp = comp * ef[..., None] + reg * (1 - ef[..., None])
    out[Y0:Y1] = np.clip(comp + 0.5, 0, 255).astype(np.uint8)
    return out


# ---------------------------------------------------------------------------------------------- finger -> front
@functools.lru_cache(maxsize=1)
def _front_table():
    """Fingertip x per frame (hand-matte point farthest from where the arm enters), median filtered, monotonic
    (the line never un-draws), lightly smoothed."""
    with open(os.path.join(G.GRP, 'leam_track.json')) as f:
        tr = json.load(f)
    fr = sorted(int(k) for k in tr)
    fx = np.array([tr[str(k)]['tip2'][0] if tr[str(k)].get('tip2') else np.nan for k in fr], np.float64)
    ok = ~np.isnan(fx)
    fx = np.interp(np.arange(len(fr)), np.nonzero(ok)[0], fx[ok])
    pad = np.pad(fx, 2, mode='edge')
    fx = np.array([np.median(pad[i:i + 5]) for i in range(len(fx))])
    fx = np.maximum.accumulate(fx)
    fx = np.convolve(np.pad(fx, 2, mode='edge'), np.ones(5) / 5, mode='valid')
    return np.array(fr, np.float64), fx


def finger_x(fi):
    fr, fx = _front_table()
    return float(np.interp(fi, fr, fx))


def front_x(t, fps=24.0):
    """Reveal front (frame px) = the fingertip's x plus a small lead, so the line draws just under it."""
    return finger_x(t * fps) + 12.0
