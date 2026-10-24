"""grp2_leam.py: Leam Taxis (Leamington Spa) client testimonial (Google Ranker Pro), 9:16, 24 fps, 32.3 s.

    cd pipeline/fostering && FOSTER_FPS=24 python3 render.py grp2_leam --audio <mix.wav>

Source: workspace3/frames/leam2 (Seedance clip hf_20261024_062503, 30.04 s): shot 1 at his desk 0-7.79 s (punched in
to keep a glass of tea, which reads as a pint, out of frame); shot 2 over the shoulder at a GREEN monitor while his
finger traces a rising line, 7.79-16.5 s, then one continuous camera move to a selfie close-up (green still
visible at the right edge) to 30.04 s. End card from 29.3 s.

SCREEN: the green monitor is keyed and replaced with a calls report (the hand, his head and anything in front stay;
the made-up line and labels go). His monthly calls are fairly flat (Google Business Profile, May-Oct 2026, 114 in
all), so the screen shows the RUNNING TOTAL of those calls (19, 36, 56, 77, 102, 114), clearly labelled, on a linear
axis from 0. The month spacing and scale are fitted to his tracked fingertip (grp_prep2.py leam2 / leam2fit: rms
about 7 px), so the line draws on just under his finger. We have no Search Console export for Leam Taxis: the voice
says "search console ... clicks"; the screen says what it is (Business Profile calls). Flagged in the README.
"""
import functools
import json
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import core as K
import footage as F
import grp_base as GB
import grp_brand as B
import grp_kit as G
import ui

DUR = 32.3
LOOK = 'natural'
BPM = 92
N_SRC = 721
T_END_CARD = 29.3
YEL, KK = '#FFC61A', '#1F1F1F'
URL = 'leamingtonspa-taxis.co.uk'
LEAM_SITE = G.site('leamingtonspa-taxis', 'now_desktop.png')
LEAM_FULL = G.site('leamingtonspa-taxis', 'now_desktop_full.png')
FAV = os.path.join(K.WS, 'leam', 'cropped-Leam-taxis-icon-270x270.png')

F.GRADES['leam2_desk'] = dict(wb=(1.035, 0.99, 0.985), exposure=0.05, contrast=1.14, pivot=0.42, black=0.018,
                              black_tint=(0.10, 0.11, 0.13), shadow_tint=(-0.006, 0.0, 0.012),
                              highlight_tint=(0.010, 0.004, -0.010), sat=1.05, shoulder=0.92)
F.GRADES['leam2_room'] = dict(wb=(1.02, 0.99, 0.99), exposure=0.04, contrast=1.12, pivot=0.40, black=0.016,
                              black_tint=(0.10, 0.11, 0.13), shadow_tint=(-0.004, 0.0, 0.012),
                              highlight_tint=(0.008, 0.004, -0.006), sat=0.97, shoulder=0.92)


# ---------------------------------------------------------------------------------------------- screen data
@functools.lru_cache(maxsize=1)
def _scr():
    with open(os.path.join(G.GRP, 'leam2_screen.json')) as f:
        d = json.load(f)
    d['quads'] = {int(k): v for k, v in d['quads'].items()}
    d['swing'] = {int(k): v for k, v in d.get('swing', {}).items()}
    return d


CW, CH = 1600, 900
CUM = [19, 36, 56, 77, 102, 114]
MONTHS = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct*']


def _fit():
    return _scr()['fit']


def pt(k):
    x0, dx, yb, ppc = _fit()
    return x0 + dx * k, yb - ppc * CUM[k]


@functools.lru_cache(maxsize=1)
def _tip_series():
    tips = np.array(_scr()['tips'])
    return tips[:, 0], tips[:, 1]


def front_x(fi):
    """Reveal front (screen px) for source frame fi: the fingertip's x, interpolated through gaps."""
    fs, xs = _tip_series()
    x0 = pt(0)[0]
    x5 = pt(5)[0]
    if fi < fs[0]:
        return x0 - 40
    tip = float(np.clip(np.interp(fi, fs, xs) + 6, x0 - 40, x5 + 60))
    if fi >= 376:                                   # finger leaves: finish the last few px to October
        x376 = float(np.interp(376, fs, xs)) + 6
        return max(tip, float(np.interp(fi, [376, 386], [x376, x5 + 60])))
    return tip


def total_at(x):
    xs = [pt(0)[0] - 40] + [pt(k)[0] for k in range(6)]
    return float(np.interp(x, xs, [0] + CUM))


def _font(name, px):
    return ImageFont.truetype(K.font_path(name), int(px))


def _hex(c, a=255):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


SS = 2


@functools.lru_cache(maxsize=1)
def base_page():
    """The report page (browser chrome, KPI block, axes, month labels): sRGB float (CH, CW, 3)."""
    im = Image.new('RGB', (CW * SS, CH * SS), (255, 255, 255))
    d = ImageDraw.Draw(im)
    s = SS

    def R(x0, y0, x1, y1, fill, r=0):
        d.rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s], radius=r * s, fill=fill)

    def T(x, y, txt, size, font, fill, anchor='ls'):
        d.text((x * s, y * s), txt, font=_font(font, size * s), fill=fill, anchor=anchor)
    R(0, 0, CW, 50, (222, 225, 230))
    R(120, 8, 520, 58, (255, 255, 255), 12)
    fav = Image.open(FAV).convert('RGBA').resize((26 * s, 26 * s), Image.LANCZOS)
    im.paste(fav, (138 * s, 18 * s), fav)
    T(176, 38, 'Leam Taxis · Calls report', 21, 'Inter-SemiBold', (60, 64, 67))
    R(0, 50, CW, 100, (255, 255, 255))
    R(150, 58, 1060, 92, (241, 243, 244), 17)
    T(180, 82, 'Leam Taxis – Google Business Profile report – Oct 2026', 20, 'Inter-Medium', (32, 33, 36))
    R(0, 99, CW, 100, (218, 220, 224))
    x0, dx, yb, ppc = _fit()
    for v in (0, 30, 60, 90, 120):
        y = yb - ppc * v
        if v == 0:
            R(x0 - 40, y - 1, CW, y + 1, (189, 189, 189))
        else:
            for x in range(int(x0 - 40), CW, 16):
                R(x, y - 0.8, x + 8, y + 0.8, (227, 227, 227))
        T(x0 - 52, y + 7, str(v), 19, 'Inter-Medium', (154, 160, 166), 'rs')
    for k, m in enumerate(MONTHS):
        T(pt(k)[0], yb + 32, m, 19, 'Inter-SemiBold', (95, 99, 104), 'ms')
    # KPI block (white backing over the gridlines), clear of his head and of the line
    KX = 372
    R(KX - 16, 112, KX + 470, 318, (255, 255, 255), 16)
    T(KX, 146, 'CALLS FROM GOOGLE BUSINESS PROFILE', 19, 'Inter-SemiBold', (107, 107, 107))
    T(KX - 2, 246, '114', 100, 'Inter-Bold', _hex(KK)[:3])
    T(KX + 200, 246, 'calls', 42, 'Inter-Bold', _hex(KK)[:3])
    R(KX, 260, KX + 120, 266, _hex(YEL)[:3], 3)
    T(KX, 296, 'Running total · May–Oct 2026', 23, 'Inter-SemiBold', (60, 64, 67))
    T(KX, 318 + 4, '*Oct is a part month', 16, 'Inter-Medium', (138, 138, 138))
    a = np.asarray(im.resize((CW, CH), Image.LANCZOS), np.float32)
    a.setflags(write=False)
    return a


@functools.lru_cache(maxsize=1)
def line_layer():
    """Yellow area fill + dark line, sRGB straight alpha (CH, CW, 4) floats."""
    im = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
    fill = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
    pts = [(pt(k)[0] * SS, pt(k)[1] * SS) for k in range(6)]
    yb = _fit()[2] * SS
    ImageDraw.Draw(fill).polygon(pts + [(pts[-1][0], yb), (pts[0][0], yb)], fill=_hex(YEL, 60))
    ImageDraw.Draw(im).line(pts, fill=_hex(KK), width=int(6 * SS), joint='curve')
    out = Image.alpha_composite(fill, im).resize((CW, CH), Image.LANCZOS)
    a = np.asarray(out, np.float32)
    rgba = a.copy()
    rgba[..., 3] /= 255.0
    rgba.setflags(write=False)
    return rgba


@functools.lru_cache(maxsize=16)
def _label(text, size, fg, bg, font='Inter-Bold', padx=14, h=None):
    f = _font(font, size * SS)
    w = int(f.getlength(text) / SS + padx * 2)
    h = h or int(size * 1.7)
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=10 * SS, fill=_hex(bg))
    d.text((w * SS / 2, h * SS / 2), text, font=f, fill=_hex(fg), anchor='mm')
    a = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32)
    rgba = a.copy()
    rgba[..., 3] /= 255.0
    return rgba


def _blend(dst, rgba, x, y):
    h, w = rgba.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0:
        return
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4]
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a


def page_at(fi, t):
    """The report page for source frame fi (line revealed to the fingertip)."""
    out = base_page().copy()
    fx = front_x(fi)
    lay = line_layer()
    xs = np.arange(CW, dtype=np.float32)
    m = np.clip((fx - xs) / 6.0, 0, 1)[None, :, None]
    a = lay[..., 3:4] * m
    out = out * (1 - a) + lay[..., :3] * a
    x0 = pt(0)[0]
    if fx > x0 - 20:
        xx = min(fx, pt(5)[0])
        xs_ = [pt(k)[0] for k in range(6)]
        ys_ = [pt(k)[1] for k in range(6)]
        yy = float(np.interp(xx, xs_, ys_))
        cv2.circle(out, (int(xx), int(yy)), 14, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(out, (int(xx), int(yy)), 10, _hex(KK)[:3], -1, cv2.LINE_AA)
        n = int(round(total_at(min(fx, pt(5)[0]))))
        if t < 15.65:
            lab = _label('%d calls' % n, 22, '#FFFFFF', KK)
            _blend(out, lab, xx - lab.shape[1] - 26, yy - lab.shape[0] - 6)
    # end: the total callout above October
    if t >= 15.7:
        k = K.ramp(t, 15.7, 16.0)
        lab = _label('114 calls in total', 24, KK, YEL)
        ox, oy = pt(5)
        tmp = lab.copy()
        tmp[..., 3] *= k
        _blend(out, tmp, ox - lab.shape[1] + 30, oy - lab.shape[0] - 30)
    return out


# ---------------------------------------------------------------------------------------------- footage prep
@functools.lru_cache(maxsize=1)
def _k_open():
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))


def _thin_marks(fr, quad, fi=None):
    """Force-replace the made-up line and labels: non-green pieces inside the display that are thin."""
    q = np.float32(quad)
    x0 = int(max(0, np.floor(q[:, 0].min()) - 3))
    y0 = int(max(0, np.floor(q[:, 1].min()) - 3))
    x1 = int(min(K.W, np.ceil(q[:, 0].max()) + 4))
    y1 = int(min(K.H, np.ceil(q[:, 1].max()) + 4))
    sub = fr[y0:y1, x0:x1].astype(np.int32)
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    gs = (g - np.maximum(r, b)) > 45
    fg = (~gs).astype(np.uint8)
    big = cv2.morphologyEx(fg, cv2.MORPH_OPEN, _k_open())
    big = cv2.dilate(big, np.ones((3, 3), np.uint8))
    thin = (fg > 0) & (big == 0)
    thin = cv2.dilate(thin.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    thin = np.clip(cv2.GaussianBlur(thin, (0, 0), 1.5) * 1.6, 0, 1) * (1 - big.astype(np.float32))
    # the made-up arrowhead / line ends touching his finger: bright, colourless and outside the person matte
    pa = G.person_alpha_u8('leam2', fi) if fi is not None else None
    if pa is not None:
        mn, mx = np.minimum(np.minimum(r, g), b), np.maximum(np.maximum(r, g), b)
        # (RVM counts the arrowhead as part of his hand; his grey hair is only at the left, so x > 480)
        xs = np.arange(x0, x1)[None, :]
        white = ((mn > 165) & (mx - mn < 45) & (g >= r - 2) & (xs > 480)).astype(np.uint8)
        white = cv2.dilate(white, np.ones((7, 7), np.uint8)).astype(np.float32)
        thin = np.maximum(thin, np.clip(cv2.GaussianBlur(white, (0, 0), 1.2) * 1.5, 0, 1))
    return thin


def prep(fr, fi):
    t = fi / 24.0
    d = _scr()
    if 187 <= fi <= 398:
        q = d['quads'][fi]
        page = page_at(fi, t)
        th = _thin_marks(fr, q, fi)
        return GB.green_replace(fr, q, page, extra_alpha=th, blur=0.8, black=16, white=236)
    if 399 <= fi <= 406 and fi in d['swing']:
        q = d['swing'][fi]['q']
        th = _thin_marks(fr, q)
        return GB.green_replace(fr, q, page_at(392, 16.5), extra_alpha=th, blur=0.8 + 0.6 * (fi - 399),
                                black=16, white=236)
    if fi > 406:
        # defocused sliver at the right edge: a soft page with the line, laid over the green's extent
        g = fr[..., 1].astype(np.int32) - np.maximum(fr[..., 0], fr[..., 2]).astype(np.int32)
        ys, xs = np.where(g[:, 700:] > 30)
        if len(xs) < 300:
            return fr
        xmin = 700 + xs.min()
        yt, ybm = ys.min(), ys.max()
        h = ybm - yt
        q = [[xmin - 1.2 * h, yt - 0.08 * h], [xmin + 0.9 * h, yt], [xmin + 0.9 * h, ybm], [xmin - 1.2 * h, ybm + 0.1 * h]]
        page = _defocused_page()
        reg = np.zeros((K.H, K.W), np.float32)
        reg[:, 640:] = 1.0
        # the defocused made-up line is not green: replace everything in the screen's extent that is not him
        pa = G.person_alpha_u8('leam2', fi)
        extra = None
        if pa is not None:
            qq = np.float32(q)
            bx0 = int(max(0, np.floor(qq[:, 0].min()) - 3))
            by0 = int(max(0, np.floor(qq[:, 1].min()) - 3))
            bx1 = int(min(K.W, np.ceil(qq[:, 0].max()) + 4))
            by1 = int(min(K.H, np.ceil(qq[:, 1].max()) + 4))
            sub = 1 - cv2.GaussianBlur(pa[by0:by1, bx0:bx1].astype(np.float32) / 255.0, (0, 0), 2.0)
            gmask = (g[by0:by1, bx0:bx1] > 12).astype(np.uint8)
            hull = np.zeros_like(gmask)
            pts = cv2.findNonZero(gmask)
            if pts is not None:
                cv2.fillConvexPoly(hull, cv2.convexHull(pts), 1)
            extra = np.clip(sub * cv2.GaussianBlur(hull.astype(np.float32), (0, 0), 6) * 1.3, 0, 1)
        return GB.green_replace(fr, q, page, region=reg, blur=0.0, defocus=0.0, black=16, white=232, shade=False,
                                extra_alpha=extra)
    return fr


@functools.lru_cache(maxsize=1)
def _defocused_page():
    p = page_at(392, 16.5)[:, 520:1100]
    return cv2.GaussianBlur(p, (0, 0), 9)


CLIP = GB.Clip('leam2', N_SRC, [
    (0, 186, dict(c0=(0.662, 0.52), c1=(0.662, 0.52), z0=1.50, z1=1.56, look='leam2_desk')),
    (187, 720, dict(c0=(0.5, 0.5), c1=(0.5, 0.5), z0=1.0, z1=1.03)),
], 'leam2_room', prep=prep, sharpen=0.3)

WORDS = G.load_words('leam2', fixes={4: 'Search', 5: 'Console.', 17: 'Ranker', 18: 'Pro,', 42: 'Spa.'})
CAP = B.captions(WORDS, max_chars=26)

# selfie section: picture-in-picture window with cards below
PIP_SRC = (60, 0, 960, 1300)
PIP_S = 0.64
PIP_W, PIP_H = int(PIP_SRC[2] * PIP_S), int(PIP_SRC[3] * PIP_S)
PIP_X, PIP_Y = (1080 - PIP_W) // 2, 128
T_PIP_IN, T_PIP_OUT = 18.6, 26.3


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
    return G.shot_sprite(G.sharpen_u8(sub, 0.3 if w_out < w * 0.8 else 0.2), 'leam2_room')


def _pip(fi, p):
    out = B.backdrop().copy()
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
def client_card(cv, t, t0=0.35, t1=2.55):
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 560, 210
    cx, cy = 540, 300 - 24 * (1 - u) - 30 * out
    pnl, pad = B.card(w, h, 34)
    K.draw(cv, pnl, cx, cy, scale=0.88 + 0.12 * u, opacity=op)
    G.draw_text(cv, 'CLIENT STORY', cx, cy - 58, 21, B.FS, B.BODY, 'ms', opacity=op * K.ramp(t, t0 + 0.12, t0 + 0.4),
                tracking=0.2)
    lg = G.leam_logo(64, strap=False)
    m = G.wipe(lg.shape[1], lg.shape[0], K.ramp(t, t0 + 0.15, t0 + 0.6, 'out_cubic'), angle=0, soft=0.12)
    K.draw(cv, G.masked(lg, m), cx, cy + 4, opacity=1 - out)
    G.draw_text(cv, URL, cx, cy + 70, 25, B.FM, B.ACTION, 'ms', opacity=op * K.ramp(t, t0 + 0.3, t0 + 0.6))


def search(cv, t):
    B.search_bar(cv, t, 'taxi Leamington Spa', 2.75, 7.6, cx=540, cy=210, w=800, h=104, type_dur=0.9)


@functools.lru_cache(maxsize=1)
def _site_card():
    return GB.site_card(LEAM_SITE, (0, 40, 1440, 620), 820, URL)


def site_card(cv, t, t0=5.5, t1=7.6):
    """'...that's people finding us on Google': the live site, under the search."""
    GB.card_in(cv, _site_card(), t, t0, t1, 540, 520, rise=40)


def grp(cv, t, t0=8.3, t1=10.6):
    """'Before Google Ranker Pro...': the GRP card above the monitor (keys and corkboard)."""
    GB.card_in(cv, B.grp_card(440, 180), t, t0, t1, 770, 300, rise=30)


def calls_card(cv, t, t0=10.6, t1=16.55):
    """Above the monitor: the running count read along the line, in step with his finger."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 560, 200
    cx, cy = 770, 290 - 24 * (1 - u) - 40 * out
    pnl, pad = B.card(w, h, 30, accent=YEL)
    K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=op)
    x0, y0 = cx - w / 2 + 40, cy - h / 2
    K.draw(cv, ui.icon('phone', 30, color=B.ACTION, stroke=2.4), x0 + 14, y0 + 44, opacity=op)
    G.draw_text(cv, 'Calls from Google Business Profile', x0 + 40, y0 + 54, 25, B.FS, B.BODY, 'ls', opacity=op)
    n = int(round(total_at(front_x(CLIP.fi(t)))))
    G.draw_text(cv, str(n), x0, y0 + 156, 96, B.FB, B.INK, 'ls', opacity=op)
    G.draw_text(cv, 'calls', x0 + G.measure('114', 96, B.FB) + 14, y0 + 156, 40, B.FB, B.INK, 'ls', opacity=op)
    G.draw_text(cv, 'Running total', x0 + 300, y0 + 120, 25, B.FS, B.INK, 'ls', opacity=op)
    G.draw_text(cv, 'May–Oct 2026', x0 + 300, y0 + 154, 23, B.FM, B.BODY, 'ls', opacity=op)


@functools.lru_cache(maxsize=1)
def _hero_card():
    return GB.site_card(LEAM_SITE, (0, 40, 1440, 620), 860, URL)


def hero_card(cv, t, t0=19.1, t1=22.35):
    GB.card_in(cv, _hero_card(), t, t0, t1, 540, 1250, rise=30, wipe_angle=0)


@functools.lru_cache(maxsize=1)
def _airports_card():
    return GB.site_card(LEAM_FULL, (100, 4496, 1220, 162), 900, URL)


def airports_card(cv, t, t0=22.45, t1=24.3):
    if not (t0 <= t < t1):
        return
    GB.card_in(cv, _airports_card(), t, t0, t1, 540, 1180, rise=30, wipe_angle=0)
    B.draw_chip(cv, t, 'Airport transfers · on the website', 540, 1340, t0 + 0.2, t1, icon='pin', size=28)


def ringing_card(cv, t, t0=24.35, t1=26.55):
    """'...the phone's ringing all day': the real calls total (Business Profile)."""
    if not (t0 <= t < t1):
        return
    u, out, op = B.pop(t, t0, t1, fout=0.3)
    w, h = 820, 200
    cx, cy = 540, 1250 + 24 * (1 - u) + 30 * out
    pnl, pad = B.card(w, h, 34, accent=YEL)
    K.draw(cv, pnl, cx, cy, scale=0.9 + 0.1 * u, opacity=op)
    px, py = cx - w / 2 + 110, cy
    for k in range(2):
        ph = ((t - t0) * 1.6 + k * 0.5) % 1.0
        K.draw(cv, K.ring(52 + 46 * ph, 3, G.lin(B.ACTION)), px, py, opacity=op * (1 - ph) * 0.8)
    K.draw(cv, K.disc(52, G.lin(YEL)), px, py, opacity=op)
    wig = 9 * math.sin((t - t0) * 40) * max(0.0, 1 - (t - t0) / 1.2)
    K.draw(cv, ui.icon('phone', 52, color=KK, stroke=2.6), px, py, rot=wig, opacity=op)
    x0 = px + 96
    G.draw_text(cv, '114 calls', x0, cy + 4, 70, B.FB, B.INK, 'ls', opacity=op)
    G.draw_text(cv, 'from Google Business Profile · May–Oct 2026', x0, cy + 50, 25, B.FM, B.BODY, 'ls', opacity=op)


# ---------------------------------------------------------------------------------------------- contract
def draw(t):
    fi = CLIP.fi(t)
    cv = CLIP.plate(t, {0: 'band'}, end_t0=T_END_CARD - 0.15)
    p = pip_amount(t) if T_PIP_IN <= t < T_PIP_OUT + 0.6 else 0.0
    if p > 0:
        cv = _pip(fi, p)
    GB.intro_reveal(cv, t)
    if t < T_END_CARD:
        client_card(cv, t)
        search(cv, t)
        site_card(cv, t)
        grp(cv, t)
        calls_card(cv, t)
        CLIP.person_over(cv, t, skip=[(0, 0.8), (T_PIP_IN, T_PIP_OUT + 0.6)])
        hero_card(cv, t)
        airports_card(cv, t)
        ringing_card(cv, t)
        G.bottom_shade(cv, 0.42, 1330, opacity=(1 - p) * (1 - K.ramp(t, T_END_CARD - 0.4, T_END_CARD)))
        if p > 0.5:
            CAP.draw(cv, t, color=B.INK, shadow=0.0)
        else:
            CAP.draw(cv, t)
        if 26.9 <= t < T_END_CARD:
            k = min(K.ramp(t, 26.9, 27.8, 'inout_sine'), 1 - K.ramp(t, T_END_CARD - 0.7, T_END_CARD, 'inout_sine'))
            K.light_leak(cv, t, colors=[G.lin('#FFE7A3'), G.lin(YEL)], strength=0.16 * k, seed=5, speed=0.6)
        B.logo_bug(cv, t, 2.6, T_END_CARD)
    B.ai_label(cv, t, solid=(T_PIP_IN + 0.3 < t < T_PIP_OUT + 0.3) or t >= T_END_CARD,
               text='AI re-creation · real client data')
    B.end_card(cv, t, T_END_CARD, 'Leam Taxis', URL,
               extra_fine=('Screen data: Leam Taxis’ Google Business Profile calls,',
                           'May–Oct 2026, shown as a running total (Oct part month).'))
    return np.ascontiguousarray(cv, dtype=np.float32)


post = GB.post
FAST = [(0.0, 0.8), (7.6, 8.0), (16.3, 17.6), (T_PIP_IN, T_PIP_IN + 0.7), (T_PIP_OUT, T_PIP_OUT + 0.7),
        (T_END_CARD - 0.2, T_END_CARD + 1.8)]


def samples(t):
    return 7 if any(a <= t < b for a, b in FAST) else 1


def cues():
    c1 = CLIP.cuts[0][0]
    return [
        dict(t=0.06, name='whoosh_fast', gain_db=-5),
        dict(t=0.76, name='impact_soft', gain_db=-8),
        dict(t=0.40, name='pop', gain_db=-6, params=dict(pitch=1.05)),
        dict(t=2.77, name='swish_small', gain_db=-6),
        dict(t=3.10, name='typing', gain_db=-10, align='start', params=dict(n=19, cps=21)),
        dict(t=5.52, name='card_slide', gain_db=-7),
        dict(t=c1, name='whip', gain_db=-6),
        dict(t=8.32, name='pop', gain_db=-6, params=dict(pitch=1.1), pan=0.3),
        dict(t=10.62, name='swish_small', gain_db=-7, pan=0.3),
        dict(t=15.72, name='shimmer', gain_db=-13),
        dict(t=15.80, name='pop', gain_db=-5, params=dict(pitch=1.15)),
        dict(t=T_PIP_IN + 0.3, name='card_slide', gain_db=-7),
        dict(t=19.12, name='swish_small', gain_db=-6),
        dict(t=22.47, name='swish_small', gain_db=-6),
        dict(t=22.70, name='pop', gain_db=-8, params=dict(pitch=1.1)),
        dict(t=24.37, name='glass_tap', gain_db=-6),
        dict(t=T_PIP_OUT + 0.35, name='whoosh_fast', gain_db=-9),
        dict(t=T_END_CARD, name='logo_sting', gain_db=-4),
        dict(t=T_END_CARD + 0.95, name='pop', gain_db=-7, params=dict(pitch=1.2)),
    ]


def prewarm():
    B.prewarm()
    _scr()
    base_page()
    line_layer()
    _defocused_page()
    _site_card()
    _hero_card()
    _airports_card()
    B.grp_card(440, 180)
