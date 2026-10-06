"""SaaS-style motion graphics in the reel's black & gold look (ref 4): frosted-glass UI cards with glowing
gradient edges, live stat widgets (price ticker + sparkline, ring gauge), a cursor clicking a pill button,
a dark app panel listing the 3 reasons, and a glass card carousel.

Everything is painted procedurally at output resolution (K) as premultiplied RGBA sprites.
"""
import math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw

import gold_reel as G
from gold_reel import en, K, OW, OH, CX, CY, clamp, lerp, e_out_expo, e_out_cubic, e_out_back, draw3d, blur_sprite

GOLD = (1.0, 0.74, 0.32)
GOLD_HI = (1.0, 0.88, 0.58)
GOLD_LO = (0.80, 0.50, 0.16)
WHITE = (0.96, 0.95, 0.93)
MUTED = (0.60, 0.61, 0.64)
TEAL = (0.22, 0.80, 0.74)
GREEN = (0.32, 0.86, 0.50)
RED = (0.95, 0.33, 0.28)
EMBER = (1.0, 0.45, 0.16)


def ease(x):
    x = clamp(x)
    return x * x * x * (x * (6 * x - 15) + 10)


class Paint:
    """A small premultiplied RGBA canvas in design px (rendered at K) with UI drawing primitives."""

    def __init__(self, w, h, pad=60):
        self.p = pad
        self.W, self.H = int((w + 2 * pad) * K), int((h + 2 * pad) * K)
        self.rgb = np.zeros((self.H, self.W, 3), np.float32)
        self.a = np.zeros((self.H, self.W), np.float32)

    def _xy(self, x, y):
        return (x + self.p) * K, (y + self.p) * K

    def over(self, m, col, op=1.0):
        m = m * op
        c = np.asarray(col, np.float32)
        c = c[..., :3] if c.ndim == 3 else c[:3]
        self.rgb = c * m[..., None] + self.rgb * (1 - m[..., None])
        self.a = m + self.a * (1 - m)

    def add(self, m, col, op=1.0):
        m = m * op
        self.rgb += np.asarray(col[:3], np.float32) * m[..., None]
        self.a = np.clip(self.a + m * 0.85, 0, 1)

    def mask(self):
        return np.zeros((self.H, self.W), np.float32)

    def rrect_d(self, x, y, w, h, r):
        X, Y = self._xy(x, y)
        ys, xs = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        xs = xs + 0.5 - (X + w * K / 2)
        ys = ys + 0.5 - (Y + h * K / 2)
        qx = np.abs(xs) - (w * K / 2 - r * K)
        qy = np.abs(ys) - (h * K / 2 - r * K)
        return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r * K

    def rrect(self, x, y, w, h, r, col, op=1.0):
        m = np.clip(0.5 - self.rrect_d(x, y, w, h, r), 0, 1)
        self.over(m, col, op)
        return m

    def stroke(self, x, y, w, h, r, width, col, op=1.0, grad=None):
        d = self.rrect_d(x, y, w, h, r)
        m = np.clip(0.5 - (np.abs(d + width * K / 2) - width * K / 2), 0, 1)
        if grad is not None:
            m = m * grad
        self.over(m, col, op)
        return m

    def glow(self, m, col, sigma, strength):
        g = cv2.GaussianBlur(m, (0, 0), sigma * K)
        self.add(g, col, strength)

    def vgrad(self, y0, y1, c0, c1):
        Y0, Y1 = self._xy(0, y0)[1], self._xy(0, y1)[1]
        t = np.clip((np.arange(self.H, dtype=np.float32) - Y0) / max(Y1 - Y0, 1), 0, 1)[:, None, None]
        img = np.asarray(c0, np.float32) * (1 - t) + np.asarray(c1, np.float32) * t
        return np.broadcast_to(img, (self.H, self.W, 3))

    def diag(self, c0=1.0, c1=0.0):
        """Top-left -> bottom-right falloff field (for gradient borders)."""
        ys, xs = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        t = np.clip((xs / self.W * 0.55 + ys / self.H * 0.45), 0, 1)
        return c0 * (1 - t) + c1 * t

    def text(self, x, y, txt, fname, size, col, op=1.0, anchor='ls', tracking=0.0):
        f = en.font(fname, int(size * K))
        X, Y = self._xy(x, y)
        im = Image.new('L', (self.W, self.H), 0)
        d = ImageDraw.Draw(im)
        if tracking:
            wtot = sum(f.getlength(c) + tracking * size * K for c in txt) - tracking * size * K
            xx = X - (wtot / 2 if anchor[0] == 'm' else wtot if anchor[0] == 'r' else 0)
            for c in txt:
                d.text((xx, Y), c, font=f, fill=255, anchor='l' + anchor[1])
                xx += f.getlength(c) + tracking * size * K
            width = wtot / K
        else:
            d.text((X, Y), txt, font=f, fill=255, anchor=anchor)
            width = f.getlength(txt) / K
        m = np.asarray(im, np.float32) / 255
        self.over(m, col, op)
        return width

    def poly(self, pts, width, col, op=1.0, closed=False, glow=0.0):
        m8 = np.zeros((self.H, self.W), np.uint8)
        P = np.int32([[(x + self.p) * K * 16, (y + self.p) * K * 16] for x, y in pts])
        cv2.polylines(m8, [P], closed, 255, max(1, int(width * K)), cv2.LINE_AA, shift=4)
        m = m8.astype(np.float32) / 255
        if glow:
            self.glow(m, col, 6, glow)
        self.over(m, col, op)
        return m

    def fillpoly(self, pts, col, op=1.0):
        m8 = np.zeros((self.H, self.W), np.uint8)
        P = np.int32([[(x + self.p) * K * 16, (y + self.p) * K * 16] for x, y in pts])
        cv2.fillPoly(m8, [P], 255, cv2.LINE_AA, shift=4)
        m = m8.astype(np.float32) / 255
        self.over(m, col, op)
        return m

    def arc(self, cx, cy, r, a0, a1, width, col, op=1.0, glow=0.0):
        m8 = np.zeros((self.H, self.W), np.uint8)
        X, Y = self._xy(cx, cy)
        if a1 - a0 > 0.2:
            cv2.ellipse(m8, (int(X * 16), int(Y * 16)), (int(r * K * 16), int(r * K * 16)), 0, a0, a1, 255,
                        max(1, int(width * K)), cv2.LINE_AA, shift=4)
        m = m8.astype(np.float32) / 255
        if glow:
            self.glow(m, col, 8, glow)
        self.over(m, col, op)
        return m

    def circle(self, cx, cy, r, col, op=1.0):
        X, Y = self._xy(cx, cy)
        ys, xs = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        m = np.clip(r * K + 0.5 - np.sqrt((xs - X) ** 2 + (ys - Y) ** 2), 0, 1)
        self.over(m, col, op)
        return m

    def sprite(self):
        return np.concatenate([self.rgb, self.a[..., None]], 2)


# ---------------------------------------------------------------- shared pieces


def glass(P, x, y, w, h, r, edge=1.0, tint=(0.05, 0.055, 0.065), fill_op=0.62):
    """Frosted dark glass card: translucent body (the backdrop blur shows through), top sheen,
    gradient gold edge brightest top-left, soft outer glow."""
    body = np.clip(0.5 - P.rrect_d(x, y, w, h, r), 0, 1)
    P.over(body, P.vgrad(y, y + h, (tint[0] + 0.05, tint[1] + 0.05, tint[2] + 0.055), tint), fill_op)
    sheen = body * np.clip(1 - (np.arange(P.H, dtype=np.float32)[:, None] / K - P.p - y) / (h * 0.45), 0, 1) ** 2
    P.add(sheen, (1, 1, 1), 0.05)
    g = P.diag(1.0, 0.12)
    m = P.stroke(x, y, w, h, r, 1.6, GOLD_HI, 0.95 * edge, grad=g)
    P.glow(m, GOLD, 10, 0.55 * edge)
    return body


def icon(P, kind, x, y, s, col_dark=(0.06, 0.05, 0.03)):
    """Glyphs drawn inside a chip at (x, y) of size s."""
    c = (x + s / 2, y + s / 2)
    if kind == 'au':
        P.text(c[0], c[1] + 1, 'Au', 'Poppins-700', s * 0.42, col_dark, anchor='mm')
    elif kind == 'dollar':
        P.text(c[0], c[1] + 1, '$', 'Poppins-700', s * 0.55, col_dark, anchor='mm')
    elif kind == 'pct':
        P.text(c[0], c[1] + 1, '%', 'Poppins-700', s * 0.50, col_dark, anchor='mm')
    elif kind == 'bank':
        P.fillpoly([(x + s * 0.18, y + s * 0.40), (c[0], y + s * 0.18), (x + s * 0.82, y + s * 0.40)], col_dark)
        for k in range(3):
            xx = x + s * (0.30 + 0.20 * k)
            P.poly([(xx, y + s * 0.46), (xx, y + s * 0.70)], s * 0.07, col_dark)
        P.poly([(x + s * 0.18, y + s * 0.78), (x + s * 0.82, y + s * 0.78)], s * 0.07, col_dark)
    elif kind == 'chart':
        P.poly([(x + s * 0.2, y + s * 0.72), (x + s * 0.42, y + s * 0.50), (x + s * 0.56, y + s * 0.62),
                (x + s * 0.8, y + s * 0.30)], s * 0.08, col_dark)
        P.fillpoly([(x + s * 0.84, y + s * 0.24), (x + s * 0.66, y + s * 0.28), (x + s * 0.80, y + s * 0.42)], col_dark)
    elif kind == 'drop':
        P.circle(c[0], y + s * 0.60, s * 0.20, col_dark)
        P.fillpoly([(c[0], y + s * 0.18), (c[0] - s * 0.18, y + s * 0.55), (c[0] + s * 0.18, y + s * 0.55)], col_dark)
    elif kind == 'shield':
        P.fillpoly([(x + s * 0.5, y + s * 0.16), (x + s * 0.80, y + s * 0.28), (x + s * 0.76, y + s * 0.58),
                    (x + s * 0.5, y + s * 0.84), (x + s * 0.24, y + s * 0.58), (x + s * 0.20, y + s * 0.28)], col_dark)
    elif kind == 'bell':
        P.circle(c[0], y + s * 0.50, s * 0.22, col_dark)
        P.rrect(x + s * 0.28, y + s * 0.50, s * 0.44, s * 0.18, s * 0.04, col_dark)
        P.circle(c[0], y + s * 0.76, s * 0.07, col_dark)
    elif kind == 'news':
        for k in range(3):
            P.poly([(x + s * 0.24, y + s * (0.34 + 0.16 * k)), (x + s * (0.76 - 0.12 * (k == 2)), y + s * (0.34 + 0.16 * k))],
                   s * 0.08, col_dark)
    elif kind == 'alert':
        P.text(c[0], c[1] + 2, '!', 'Poppins-700', s * 0.6, col_dark, anchor='mm')
    elif kind == 'plus':
        P.poly([(c[0] - s * 0.2, c[1]), (c[0] + s * 0.2, c[1])], s * 0.09, col_dark)
        P.poly([(c[0], c[1] - s * 0.2), (c[0], c[1] + s * 0.2)], s * 0.09, col_dark)


def chip(P, x, y, s, kind, c0=GOLD_HI, c1=GOLD_LO, glow=0.35):
    m = np.clip(0.5 - P.rrect_d(x, y, s, s, s * 0.28), 0, 1)
    P.over(m, P.vgrad(y, y + s, c0, c1))
    P.glow(m, c0, 8, glow)
    icon(P, kind, x, y, s)


def tri(P, x, y, s, up, col):
    if up:
        P.fillpoly([(x, y + s * 0.8), (x + s, y + s * 0.8), (x + s / 2, y)], col)
    else:
        P.fillpoly([(x, y), (x + s, y), (x + s / 2, y + s * 0.8)], col)


def fmt_price(v):
    return '$' + f'{int(round(v)):,}'

# ---------------------------------------------------------------- talking-head widgets

TICK_SERIES = {
    'down': [0.30, 0.34, 0.28, 0.36, 0.33, 0.40, 0.46, 0.52, 0.50, 0.62, 0.70, 0.78, 0.86, 0.92],
    'up': [0.86, 0.90, 0.80, 0.82, 0.70, 0.74, 0.62, 0.58, 0.60, 0.48, 0.44, 0.38, 0.34, 0.28],
}


def ticker_card(u, p0, p1, delta, up, series):
    """XAU/USD live ticker: count-up price, delta pill, sparkline drawing on."""
    w, h = 380, 250
    P = Paint(w, h)
    glass(P, 0, 0, w, h, 30)
    chip(P, 24, 22, 40, 'au')
    P.text(76, 50, 'XAU / USD', 'Poppins-600', 21, (0.72, 0.72, 0.75), tracking=0.08)
    live = 0.55 + 0.45 * math.sin(u * 14)
    P.circle(w - 74, 42, 5, GREEN if up else RED, op=live)
    P.text(w - 62, 49, 'LIVE', 'Poppins-600', 17, MUTED, tracking=0.10)
    q = ease(clamp((u - 0.05) / 0.85))
    P.text(22, 134, fmt_price(lerp(p0, p1, q)), 'Poppins-700', 62, WHITE)
    col = GREEN if up else RED
    pw = 112
    P.rrect(w - pw - 20, 96, pw, 38, 19, col, 0.18)
    tri(P, w - pw - 6, 106, 16, up, col)
    P.text(w - pw + 18, 122, delta, 'Poppins-700', 20, col)
    # sparkline
    x0, y0, sw, sh = 24, 150, w - 48, 74
    pts = [(x0 + sw * k / (len(series) - 1), y0 + sh * v) for k, v in enumerate(series)]
    d = ease(clamp((u - 0.12) / 0.75))
    n = max(2, int(d * (len(pts) - 1)) + 1)
    frac = d * (len(pts) - 1) - (n - 2)
    vis = pts[:n - 1] + [(lerp(pts[n - 2][0], pts[n - 1][0], min(frac, 1)), lerp(pts[n - 2][1], pts[n - 1][1], min(frac, 1)))]
    area = vis + [(vis[-1][0], y0 + sh + 8), (vis[0][0], y0 + sh + 8)]
    m = np.zeros((P.H, P.W), np.uint8)
    cv2.fillPoly(m, [np.int32([[(x + P.p) * K * 16, (y + P.p) * K * 16] for x, y in area])], 255, cv2.LINE_AA, shift=4)
    fill = m.astype(np.float32) / 255 * np.clip(1 - (np.arange(P.H, dtype=np.float32)[:, None] / K - P.p - y0) / (sh + 8), 0, 1)
    P.over(fill, GOLD, 0.30)
    P.poly(vis, 3.2, GOLD_HI, glow=0.9)
    ex, ey = vis[-1]
    P.circle(ex, ey, 6.5, GOLD_HI)
    P.circle(ex, ey, 6.5 + 8 * (0.5 + 0.5 * math.sin(u * 12)), GOLD, op=0.18)
    return P.sprite()


def gauge_card(u, v0, v1, label, sub):
    """Ring gauge: probability arc sweeping from v0 to v1 with a glowing gold progress."""
    w, h = 360, 330
    P = Paint(w, h)
    glass(P, 0, 0, w, h, 30)
    chip(P, 24, 22, 40, 'pct')
    P.text(76, 42, 'RATE HIKE ODDS', 'Poppins-600', 20, (0.72, 0.72, 0.75), tracking=0.08)
    P.text(76, 66, sub, 'Inter-500', 18, (0.52, 0.53, 0.56))
    cx, cy, r = w / 2, 196, 84
    P.arc(cx, cy, r, 0, 360, 15, (1, 1, 1), op=0.08)
    v = lerp(v0, v1, ease(clamp((u - 0.08) / 0.8)))
    a1 = -90 + 360 * v
    P.arc(cx, cy, r, -90, a1, 15, GOLD, glow=1.0)
    ang = math.radians(a1)
    P.circle(cx + r * math.cos(ang), cy + r * math.sin(ang), 10, GOLD_HI)
    lab = label if u > 0.55 else f'{int(round(v * 100))}%'
    P.text(cx, cy + 2, lab, 'Poppins-700', 48 if len(lab) < 5 else 38, WHITE, anchor='mm')
    P.text(cx, cy + 40, 'probability', 'Inter-500', 17, MUTED, anchor='mm')
    return P.sprite()


@functools.lru_cache(maxsize=None)
def cursor_sprite():
    P = Paint(40, 54, pad=10)
    pts = [(0, 0), (0, 42), (11, 32), (19, 50), (26, 47), (18, 29), (32, 29)]
    P.fillpoly(pts, (0.05, 0.05, 0.06))
    inner = [(3, 7), (3, 35), (12, 27), (20, 44), (22, 43), (14, 25), (25, 25)]
    P.fillpoly(inner, WHITE)
    return P.sprite()


def button_card(u, text='Selective Buying'):
    """Glass pill button; a cursor glides in and clicks it: press, gold fill, ripple."""
    w, h = 430, 104
    P = Paint(w, h, pad=80)
    click = 0.52
    pressed = u >= click
    k = clamp((u - click) / 0.25)
    if pressed:
        m = np.clip(0.5 - P.rrect_d(0, 0, w, h, h / 2), 0, 1)
        P.over(m, P.vgrad(0, h, GOLD_HI, GOLD_LO), ease(k))
        P.glow(m, GOLD, 18, 0.9 * ease(k))
    glass(P, 0, 0, w, h, h / 2, edge=1.0, fill_op=0.62 * (1 - 0.8 * ease(k)))
    chip(P, 18, 18, 68, 'plus')
    txt_col = tuple(lerp(WHITE[i], 0.07, ease(k)) for i in range(3))
    P.text(104, h / 2 + 2, text, 'Poppins-600', 32, txt_col, anchor='lm')
    if pressed and k < 1:                       # ripple from the click point
        P.arc(w * 0.66, h * 0.55, 10 + 70 * ease(k), 0, 360, 2.5, GOLD_HI, op=0.65 * (1 - k))
    return P.sprite(), 80


CLICK_PT = (0.66, 0.55)      # where the cursor clicks, as a fraction of the button


def card_scale(u, t_hold):
    """Entrance/exit for widgets: (scale, opacity, blur, lift)."""
    a = ease(clamp(u / 0.35))
    b = ease(clamp((t_hold - u) / 0.25))
    return lerp(0.9, 1.0, a) * lerp(0.96, 1.0, b), min(a, b), (1 - a) * 8, (1 - a) * 26

# ---------------------------------------------------------------- full-screen SaaS b-roll


@functools.lru_cache(maxsize=None)
def _bg_static():
    y = np.linspace(0, 1, OH, dtype=np.float32)[:, None, None]
    bg = np.array([0.016, 0.018, 0.024], np.float32) * (1 - y) + np.array([0.010, 0.012, 0.016], np.float32) * y
    bg = np.broadcast_to(bg, (OH, OW, 3)).copy()
    step = int(64 * K)
    bg[::step, :, :] += 0.012
    bg[:, ::step, :] += 0.012
    return bg


@functools.lru_cache(maxsize=None)
def _blob(col, size):
    n = int(size * K)
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
    r = np.sqrt((xs - n / 2) ** 2 + (ys - n / 2) ** 2) / (n / 2)
    a = np.exp(-(r / 0.5) ** 2) * (r < 1)
    return np.concatenate([a[..., None] * np.array(col, np.float32), a[..., None]], 2).astype(np.float32)


def aurora(t, cols=((1.0, 0.55, 0.12), (0.10, 0.55, 0.55))):
    cv = _bg_static().copy()
    G.draw(cv, _blob(cols[0], 1400), CX - 260 + 120 * math.sin(t * 0.7), 560 + 80 * math.cos(t * 0.5), 1.0, 0, 0.55, 'add')
    G.draw(cv, _blob(cols[1], 1500), CX + 300 + 100 * math.cos(t * 0.6), 1420 + 90 * math.sin(t * 0.8), 1.0, 0, 0.45, 'add')
    return cv


REASONS = [('chart', 'US Treasury Yields', 'Highest since June 2007', TEAL, '01'),
           ('dollar', 'US Dollar', 'Dollar strong hua', GREEN, '02'),
           ('bank', 'Fed Rate Hike', 'October · 25 bp', GOLD, '03')]


def reasons_panel(t, t_in, row_times, pick_t):
    """Dark app panel ('3 bari wajahain'): sidebar, typed header, the three reasons sliding in on the beat,
    a selection glow landing on 01 - which is the next chapter."""
    w, h = 860, 1000
    P = Paint(w, h, pad=70)
    body = glass(P, 0, 0, w, h, 44, edge=1.0, tint=(0.03, 0.033, 0.04), fill_op=0.9)
    # glowing ember edge along the top-left (ref 4's lit panel rim)
    rim = P.stroke(0, 0, w, h, 44, 2.6, EMBER, 1.0, grad=P.diag(1.0, -0.6).clip(0, 1))
    P.glow(rim, EMBER, 22, 1.2)
    # sidebar
    P.rrect(0, 0, 112, h, 44, (0.02, 0.022, 0.028), 0.9)
    P.poly([(112, 40), (112, h - 40)], 1.2, (1, 1, 1), op=0.06)
    chip(P, 30, 46, 52, 'au')
    for k, kind in enumerate(('chart', 'dollar', 'bank', 'drop')):
        yy = 150 + k * 92
        m = np.clip(0.5 - P.rrect_d(32, yy, 48, 48, 14), 0, 1)
        P.over(m, (1, 1, 1), 0.05)
        icon(P, kind, 32, yy, 48, col_dark=(0.55, 0.56, 0.6))
    u = t - t_in
    P.text(156, 96, 'GOLD MARKET  ·  OVERVIEW', 'Poppins-600', 18, MUTED, tracking=0.14)
    title = '3 bari wajahain'
    n = int(clamp((u - 0.05) / 0.45) * len(title) + 0.999)
    if n:
        wd = P.text(156, 172, title[:n], 'Poppins-700', 58, WHITE)
        if n < len(title) and int(u * 8) % 2 == 0:
            P.rrect(156 + wd + 6, 128, 4, 52, 2, GOLD_HI)
    P.poly([(156, 214), (w - 48, 214)], 1.2, (1, 1, 1), op=0.07)
    for k, (kind, ttl, sub, col, num) in enumerate(REASONS):
        a = ease(clamp((t - row_times[k]) / 0.32))
        if a <= 0:
            continue
        y = 256 + k * 236
        dx = (1 - a) * 70
        sel = k == 0 and t >= pick_t
        s_ = ease(clamp((t - pick_t) / 0.25)) if sel else 0
        if s_:
            m = np.clip(0.5 - P.rrect_d(140, y - 14, w - 172, 206, 28), 0, 1)
            P.over(m, GOLD, 0.10 * s_)
            ms = P.stroke(140, y - 14, w - 172, 206, 28, 2.0, GOLD_HI, 0.9 * s_)
            P.glow(ms, GOLD, 14, 0.9 * s_)
        m = np.clip(0.5 - P.rrect_d(156 + dx, y + 20, 96, 96, 26), 0, 1)
        P.over(m, P.vgrad(y + 20, y + 116, tuple(min(1, c * 1.15) for c in col), tuple(c * 0.6 for c in col)), a)
        P.glow(m, col, 14, 0.5 * a)
        icon(P, kind, 156 + dx, y + 20, 96)
        P.text(282 + dx, y + 66, ttl, 'Poppins-600', 38, WHITE, op=a)
        P.text(282 + dx, y + 106, sub, 'Inter-500', 25, MUTED, op=a)
        pm = P.stroke(w - 140 + dx, y + 46, 92, 46, 23, 1.6, GOLD_HI, 0.9 * a)
        P.text(w - 94 + dx, y + 78, num, 'Poppins-700', 22, GOLD_HI, op=a, anchor='ms')
        if k < 2:
            P.poly([(156, y + 182), (w - 48, y + 182)], 1.0, (1, 1, 1), op=0.06 * a)
    return P.sprite()


CAROUSEL = [('bank', "Fed's next move", 'Rate path', GOLD), ('chart', 'PCE data', 'Inflation print', TEAL),
            ('drop', 'Oil risk', 'Middle East', EMBER)]


@functools.lru_cache(maxsize=8)
def carousel_card(k, hi):
    kind, ttl, sub, col = CAROUSEL[k]
    w, h = 340, 430
    P = Paint(w, h, pad=70)
    glass(P, 0, 0, w, h, 38, edge=0.6 + 0.4 * hi, fill_op=0.7)
    m = np.clip(0.5 - P.rrect_d(w / 2 - 66, 70, 132, 132, 38), 0, 1)
    P.over(m, P.vgrad(70, 202, tuple(min(1, c * 1.15) for c in col), tuple(c * 0.55 for c in col)))
    P.glow(m, col, 22, 0.8)
    icon(P, kind, w / 2 - 66, 70, 132)
    P.text(w / 2, 280, ttl, 'Poppins-600', 34, WHITE, anchor='ms')
    P.text(w / 2, 322, sub, 'Inter-500', 22, MUTED, anchor='ms')
    P.rrect(w / 2 - 54, 360, 108, 36, 18, col, 0.16)
    P.text(w / 2, 385, 'WATCH', 'Poppins-600', 15, col, anchor='ms', tracking=0.14)
    return P.sprite()


def render_reasons(t, ins, sw):
    """Full-screen: the 3-reasons app panel tilting in on an aurora backdrop."""
    t_in, t_out = ins[0], ins[1]
    u = t - t_in
    cv = aurora(t)
    spr = reasons_panel(t, t_in, (12.45, 12.75, 13.05), 13.30)
    p = e_out_expo(clamp(u / 0.45))
    cam = en.Cam()
    ry = lerp(26, 9, p) - 5 * (u / (t_out - t_in))
    rx = lerp(12, 4, p)
    z = lerp(320, 0, p) - 60 * u
    h = 1000 + 140
    draw3d(cv, blur_sprite(spr, (1 - p) * 10 * K) if p < 0.97 else spr, CX + 30, 930, z, h=h * 1.06, rx=rx, ry=ry,
           cam=cam, opacity=clamp(u / 0.12))
    return cv


def render_carousel(t, ins, focus_t):
    """Full-screen: glass carousel Fed -> PCE -> Oil sliding past, focused card lit, colour glows behind."""
    t_in, t_out = ins[0], ins[1]
    u = t - t_in
    cv = aurora(t, ((1.0, 0.55, 0.12), (0.12, 0.45, 0.50)))
    cam = en.Cam()
    # position of the carousel (0 = Fed centred); slides in from the right, settles on Fed, drifts on
    pos = lerp(1.3, 0.0, e_out_expo(clamp((t - t_in) / max(focus_t - t_in, 0.2)))) - 0.15 * clamp((t - focus_t) / 0.6)
    hdr_n = int(clamp(u / 0.4) * 26 + 0.999)
    hdr = Paint(760, 60, pad=10)
    hdr.text(380, 44, 'WHAT THE MARKET IS PRICING'[:hdr_n], 'Poppins-600', 30, (0.78, 0.76, 0.72), anchor='ms', tracking=0.14)
    G.draw(cv, hdr.sprite(), CX, 440, 1.0, 0, 1.0)
    slot = {0: 0, 1: 1, 2: -1}                  # Fed centre, PCE right, Oil left
    order = sorted(range(3), key=lambda k: -abs(slot[k] + pos))
    for k in order:
        off = slot[k] + pos
        hi = 1.0 if abs(off) < 0.5 else 0.0
        x = CX + off * 455
        sc = lerp(1.0, 0.78, clamp(abs(off)))
        op = lerp(1.0, 0.55, clamp(abs(off))) * clamp(u / 0.15)
        col = CAROUSEL[k][3]
        G.draw(cv, _blob(col, 1100), x, 1000, 1.0, 0, 0.35 * op * (1.2 - 0.6 * clamp(abs(off))), 'add')
        spr = carousel_card(k, hi)
        bl = clamp(abs(off) - 0.3) * 6
        draw3d(cv, blur_sprite(spr, bl * K) if bl > 0.5 else spr, x, 1000, 120 * clamp(abs(off)), h=800 * sc,
               ry=-22 * clamp(off, -1, 1), cam=cam, opacity=op)
    return cv


def cues(inserts, cards):
    """UI sound design for the SaaS pieces: (t, kind, gain)."""
    out = []
    for ins in inserts:
        if ins[2] == 'saas_reasons':
            out += [(ins[0] - 0.12, 'whoosh', 0.55), (ins[0], 'impact', 0.6)]
            out += [(tr, 'pop', 0.45) for tr in (12.45, 12.75, 13.05)]
            out += [(ins[0] + 0.08 + 0.05 * j, 'tick', 0.18) for j in range(8)]
            out.append((13.30, 'click', 0.5))
        elif ins[2] == 'saas_carousel':
            out += [(ins[0] - 0.12, 'whoosh', 0.55), (ins[0], 'hit_soft', 0.55), (ins[0] + 0.55, 'click', 0.4),
                    (ins[0] + 0.05, 'swish', 0.4)]
    for c in cards:
        t_in, t_out, kind, prm = c
        out += [(t_in + 0.02, 'pop', 0.4), (t_in + 0.1, 'swish', 0.3)]
        if kind in ('ticker', 'gauge', 'compare'):
            out.append((t_in + 0.15, 'tick_run', 0.18))
        if kind == 'feed':
            out += [(t_in + 0.35 * k, 'pop', 0.3) for k in range(1, 3)]
        if kind in ('menu', 'badge', 'toggle'):
            tc = t_in + prm.get('at', 0.55) * (t_out - t_in)
            out += [(tc - 0.02, 'click', 0.7), (tc, 'ching', 0.3)]
    return out


# ---------------------------------------------------------------- more talking-head widgets

BADGE = {'down': ('\u25bc', RED), 'up': ('\u25b2', GREEN), 'teal': ('\u25b2', TEAL), 'gold': ('\u25b2', GOLD),
         'ok': ('\u2713', GREEN), 'dot': ('\u25cf', TEAL)}


def toast_card(u, kind, title, sub, badge):
    """Notification toast (compact): icon chip, title, subtitle, status badge."""
    w, h = 400, 150
    P = Paint(w, h)
    glass(P, 0, 0, w, h, 32)
    chip(P, 20, 20, 72, kind)
    P.text(108, 52, title, 'Poppins-600', 29, WHITE)
    P.text(108, 88, sub, 'Inter-500', 23, (0.66, 0.67, 0.70))
    sym, col = BADGE[badge]
    a = ease(clamp((u - 0.25) / 0.3))
    if a > 0:
        cx_, cy_ = 46 + 10, 124
        P.rrect(20, 108, 72, 30, 15, col, 0.18 * a)
        if sym in ('\u25bc', '\u25b2'):
            tri(P, 47, 115, 16, sym == '\u25b2', col)
        else:
            P.text(56, 124, sym, 'Poppins-700', 20, col, op=a, anchor='mm')
    P.text(108, 128, 'now', 'Inter-500', 17, (0.48, 0.49, 0.52))
    return P.sprite()


def compare_card(u):
    """Bonds vs Gold: bond yield bar grows, gold stays at 0% interest."""
    w, h = 400, 300
    P = Paint(w, h)
    glass(P, 0, 0, w, h, 30)
    chip(P, 22, 22, 44, 'chart', TEAL, (0.08, 0.45, 0.42))
    P.text(80, 52, 'YIELD vs GOLD', 'Poppins-600', 20, (0.72, 0.72, 0.75), tracking=0.08)
    rows = [('US Bonds', 0.82, TEAL, 'Yield up'), ('Gold', 0.035, GOLD, '0% interest')]
    for k, (lab, v, col, tag) in enumerate(rows):
        y = 112 + k * 92
        P.text(24, y, lab, 'Poppins-600', 23, WHITE)
        tw = P.text(w - 24, y, tag, 'Poppins-600', 18, col, anchor='rs')
        if k == 0:
            tri(P, w - 24 - tw - 22, y - 15, 14, True, col)
        P.rrect(24, y + 18, w - 48, 22, 11, (1, 1, 1), 0.07)
        q = ease(clamp((u - 0.15 - 0.15 * k) / 0.6))
        bw = max(22, (w - 48) * v * q)
        m = np.clip(0.5 - P.rrect_d(24, y + 18, bw, 22, 11), 0, 1)
        P.over(m, col)
        P.glow(m, col, 8, 0.6)
    return P.sprite()


def toggle_card(u, sw):
    """'This drop is': segmented control slides from 'Structural crash' to 'Macro correction' at sw."""
    w, h = 440, 196
    P = Paint(w, h)
    glass(P, 0, 0, w, h, 30)
    P.text(24, 48, 'THIS DROP IS', 'Poppins-600', 20, (0.72, 0.72, 0.75), tracking=0.10)
    x0, y0, sw_w, sh = 22, 76, w - 44, 92
    P.rrect(x0, y0, sw_w, sh, 26, (1, 1, 1), 0.06)
    q = ease(clamp((u - sw) / 0.35))
    half = sw_w / 2
    px = x0 + 6 + q * (half - 6)
    col = tuple(lerp(RED[i], GOLD[i], q) for i in range(3))
    m = np.clip(0.5 - P.rrect_d(px, y0 + 6, half - 6, sh - 12, 22), 0, 1)
    P.over(m, P.vgrad(y0, y0 + sh, tuple(min(1, c * 1.1) for c in col), tuple(c * 0.7 for c in col)))
    P.glow(m, col, 12, 0.6)
    on, off = (0.07, 0.06, 0.05), (0.80, 0.80, 0.82)
    c_l = tuple(lerp(on[i], off[i], q) for i in range(3))
    c_r = tuple(lerp(off[i], on[i], q) for i in range(3))
    P.text(x0 + half / 2, y0 + 40, 'Structural', 'Poppins-600', 22, c_l, anchor='ms')
    P.text(x0 + half / 2, y0 + 68, 'crash', 'Poppins-600', 22, c_l, anchor='ms')
    P.text(x0 + half * 1.5, y0 + 40, 'Macro', 'Poppins-600', 22, c_r, anchor='ms')
    P.text(x0 + half * 1.5, y0 + 68, 'correction', 'Poppins-600', 22, c_r, anchor='ms')
    if q > 0.6:                                     # strike through the rejected option
        P.poly([(x0 + 26, y0 + sh / 2), (x0 + 26 + (half - 52) * ease((q - 0.6) / 0.4), y0 + sh / 2)], 2.5, RED, op=0.9)
    return P.sprite()


def menu_card(u, items, pick, pick_u):
    """Trader's move: the hover follows the cursor down the list, the pick turns gold with a check."""
    w = 400
    rh = 82
    h = 74 + rh * len(items)
    P = Paint(w, h)
    glass(P, 0, 0, w, h, 30)
    P.text(24, 48, "TRADER'S MOVE", 'Poppins-600', 20, (0.72, 0.72, 0.75), tracking=0.10)
    hov = lerp(0, pick, ease(clamp((u - 0.15) / max(pick_u - 0.2, 0.1))))
    sel = ease(clamp((u - pick_u) / 0.2))
    yh = 66 + hov * rh
    m = np.clip(0.5 - P.rrect_d(12, yh, w - 24, rh - 6, 20), 0, 1)
    P.over(m, (1, 1, 1), 0.07 * (1 - sel))
    if sel > 0:
        m = np.clip(0.5 - P.rrect_d(12, 66 + pick * rh, w - 24, rh - 6, 20), 0, 1)
        P.over(m, P.vgrad(66 + pick * rh, 66 + (pick + 1) * rh, GOLD_HI, GOLD_LO), sel)
        P.glow(m, GOLD, 14, 0.8 * sel)
    for k, (kind, lab) in enumerate(items):
        y = 66 + k * rh
        col = WHITE if not (k == pick and sel > 0.5) else (0.07, 0.06, 0.05)
        m = np.clip(0.5 - P.rrect_d(28, y + 16, 46, 46, 13), 0, 1)
        P.over(m, (1, 1, 1), 0.08)
        icon(P, kind, 28, y + 16, 46, col_dark=(0.78, 0.78, 0.8) if not (k == pick and sel > 0.5) else (0.07, 0.06, 0.05))
        P.text(92, y + 48, lab, 'Poppins-600', 25, col)
        if k == pick and sel > 0.5:
            P.poly([(w - 66, y + 40), (w - 56, y + 50), (w - 38, y + 28)], 4, (0.07, 0.06, 0.05))
    return P.sprite()


def feed_card(u, items):
    """News feed: headlines stack in one after another."""
    w, rh = 400, 104
    h = rh * len(items)
    P = Paint(w, h)
    for k, (kind, title, sub) in enumerate(items):
        a = ease(clamp((u - 0.35 * k) / 0.35))
        if a <= 0:
            continue
        y = k * rh + (1 - a) * 30
        glass(P, 0, y, w, rh - 12, 24, edge=0.8 * a, fill_op=0.6 * a)
        chip(P, 16, y + 16, 60, kind, glow=0.25 * a)
        P.text(92, y + 44, title, 'Poppins-600', 26, WHITE, op=a)
        P.text(92, y + 75, sub, 'Inter-500', 20, MUTED, op=a)
    return P.sprite()


def badge_card(u, ring='GOLD MARKET \u00b7 DAILY UPDATES \u00b7 ', cta='Follow'):
    """Outro: gold Au coin with circular text rotating around it, and a Follow pill (cursor clicks it)."""
    w, h = 420, 560
    P = Paint(w, h)
    cx, cy, r = w / 2, 200, 150
    coin = np.clip(0.5 - P.rrect_d(cx - 92, cy - 92, 184, 184, 92), 0, 1)
    P.over(coin, P.vgrad(cy - 92, cy + 92, GOLD_HI, GOLD_LO))
    P.glow(coin, GOLD, 26, 1.0)
    P.text(cx, cy + 4, 'Au', 'Poppins-700', 84, (0.07, 0.05, 0.03), anchor='mm')
    P.arc(cx, cy, r + 26, 0, 360, 1.4, GOLD_HI, op=0.35)
    rot = u * 70
    f = en.font('Poppins-600', int(22 * K))
    n = len(ring)
    for j, ch in enumerate(ring):
        ang = math.radians(rot + 360 * j / n - 90)
        im = Image.new('L', (int(40 * K), int(40 * K)), 0)
        ImageDraw.Draw(im).text((20 * K, 20 * K), ch, font=f, fill=255, anchor='mm')
        im = im.rotate(-(rot + 360 * j / n), resample=Image.BICUBIC)
        X, Y = P._xy(cx + r * math.cos(ang), cy + r * math.sin(ang))
        x0_, y0_ = int(X - 20 * K), int(Y - 20 * K)
        m = np.zeros((P.H, P.W), np.float32)
        a = np.asarray(im, np.float32) / 255
        m[y0_:y0_ + a.shape[0], x0_:x0_ + a.shape[1]] = a
        P.over(m, (0.90, 0.88, 0.84))
    # follow pill
    click = 0.55
    k = clamp((u - click) / 0.25)
    pw, ph_, px, py = 260, 84, (w - 260) / 2, 420
    if u >= click:
        m = np.clip(0.5 - P.rrect_d(px, py, pw, ph_, ph_ / 2), 0, 1)
        P.over(m, P.vgrad(py, py + ph_, GOLD_HI, GOLD_LO), ease(k))
        P.glow(m, GOLD, 16, 0.9 * ease(k))
    glass(P, px, py, pw, ph_, ph_ / 2, fill_op=0.6 * (1 - 0.8 * ease(k)))
    txt = 'Following' if k > 0.5 else cta
    P.text(w / 2, py + ph_ / 2 + 2, txt, 'Poppins-600', 30,
           tuple(lerp(WHITE[i], 0.07, ease(k)) for i in range(3)), anchor='mm')
    return P.sprite()

# ---------------------------------------------------------------- fast full-screen SaaS clips


SPARK = {'up': [0.82, 0.78, 0.80, 0.70, 0.72, 0.60, 0.55, 0.58, 0.44, 0.38, 0.30, 0.22, 0.12],
         'down': [0.18, 0.22, 0.16, 0.28, 0.26, 0.38, 0.44, 0.40, 0.56, 0.62, 0.72, 0.80, 0.90]}


def spark_panel(u, up):
    w, h = 760, 820
    P = Paint(w, h, pad=70)
    glass(P, 0, 0, w, h, 44, fill_op=0.85, tint=(0.03, 0.033, 0.04))
    chip(P, 36, 34, 64, 'au')
    P.text(120, 78, 'XAU / USD', 'Poppins-600', 30, (0.78, 0.78, 0.8), tracking=0.08)
    col = GREEN if up else RED
    P.rrect(w - 200, 40, 164, 56, 28, col, 0.18)
    tri(P, w - 182, 56, 22, up, col)
    P.text(w - 150, 80, '+1.3%' if up else '-4.0%', 'Poppins-700', 26, col)
    x0, y0, cw, ch = 40, 150, w - 80, h - 200
    for k in range(5):
        P.poly([(x0, y0 + ch * k / 4), (x0 + cw, y0 + ch * k / 4)], 1, (1, 1, 1), op=0.05)
    ser = SPARK['up' if up else 'down']
    pts = [(x0 + cw * k / (len(ser) - 1), y0 + ch * v) for k, v in enumerate(ser)]
    d = ease(clamp(u / 0.8))
    n = max(2, int(d * (len(pts) - 1)) + 1)
    fr = d * (len(pts) - 1) - (n - 2)
    vis = pts[:n - 1] + [(lerp(pts[n - 2][0], pts[n - 1][0], min(fr, 1)), lerp(pts[n - 2][1], pts[n - 1][1], min(fr, 1)))]
    m = np.zeros((P.H, P.W), np.uint8)
    area = vis + [(vis[-1][0], y0 + ch), (vis[0][0], y0 + ch)]
    cv2.fillPoly(m, [np.int32([[(x + P.p) * K * 16, (y + P.p) * K * 16] for x, y in area])], 255, cv2.LINE_AA, shift=4)
    fill = m.astype(np.float32) / 255 * np.clip(1 - (np.arange(P.H, dtype=np.float32)[:, None] / K - P.p - y0) / ch, 0, 1)
    P.over(fill, GOLD, 0.3)
    P.poly(vis, 5, GOLD_HI, glow=1.2)
    ex, ey = vis[-1]
    P.circle(ex, ey, 11, GOLD_HI)
    P.circle(ex, ey, 11 + 14 * (0.5 + 0.5 * math.sin(u * 20)), GOLD, op=0.2)
    return P.sprite()


def render_spark(t, ins, up):
    u = (t - ins[0]) / (ins[1] - ins[0])
    cv = aurora(t, ((1.0, 0.55, 0.12), (0.12, 0.6, 0.4) if up else (0.6, 0.12, 0.08)))
    spr = spark_panel(u * 1.15, up)
    p = e_out_expo(clamp(u / 0.5))
    draw3d(cv, spr, CX, 960, lerp(380, -40, p) - 60 * u, h=1100, rx=lerp(14, 6, p), ry=lerp(-24, -10, p),
           cam=en.Cam(), opacity=clamp(u / 0.12))
    return cv


@functools.lru_cache(maxsize=12)
def app_icon(kind, col):
    s = 420
    P = Paint(s, s, pad=90)
    m = np.clip(0.5 - P.rrect_d(0, 0, s, s, 110), 0, 1)
    P.over(m, P.vgrad(0, s, tuple(min(1, c * 1.2) for c in col), tuple(c * 0.5 for c in col)))
    P.glow(m, col, 40, 1.0)
    P.stroke(0, 0, s, s, 110, 3, (1, 1, 1), 0.5, grad=P.diag(1.0, 0.0))
    icon(P, kind, 60, 60, s - 120)
    return P.sprite()


def render_icon(t, ins, kind, col):
    """Glowing app-icon reveal with orbiting arcs and a light sweep."""
    u = (t - ins[0]) / (ins[1] - ins[0])
    cv = aurora(t, (col, (0.12, 0.45, 0.50)))
    cam = en.Cam()
    p = e_out_back(clamp(u / 0.45), 1.6)
    ring = Paint(900, 900, pad=10)
    a0 = u * 260
    ring.arc(450, 450, 400, a0, a0 + 120, 3, GOLD_HI, op=0.8, glow=0.8)
    ring.arc(450, 450, 340, -a0 * 1.4 + 180, -a0 * 1.4 + 250, 2, col, op=0.7, glow=0.6)
    G.draw(cv, ring.sprite(), CX, 940, 1.0, 0, clamp(u / 0.2))
    spr = app_icon(kind, col)
    draw3d(cv, spr, CX, 940, lerp(500, 0, p), h=600 * lerp(0.6, 1.0, p), ry=lerp(-30, 0, p) + 8 * u, cam=cam,
           opacity=clamp(u / 0.1))
    return cv


def render_stack(t, ins):
    """Cascade of glass UI cards flying along a 3D diagonal (ref 4 image stack)."""
    u = (t - ins[0]) / (ins[1] - ins[0])
    cv = aurora(t)
    cam = en.Cam()
    items = [('au', 'Gold'), ('dollar', 'US Dollar'), ('bank', 'Fed'), ('chart', 'Yields'), ('drop', 'Oil'),
             ('pct', 'Odds'), ('shield', 'Risk')]
    for k, (kind, lab) in enumerate(items):
        d = k - 1.5 - (len(items) - 3) * u
        x = CX + d * 135
        y = 960 - d * 190
        z = 160 + d * 150
        spr = stack_card(kind, lab)
        draw3d(cv, spr, x, y, z, h=470, ry=-28, rx=10, rz=-8, cam=cam, opacity=clamp(1.3 - abs(d) * 0.22))
    return cv


@functools.lru_cache(maxsize=12)
def stack_card(kind, lab):
    w, h = 320, 380
    P = Paint(w, h, pad=50)
    glass(P, 0, 0, w, h, 36, fill_op=0.75)
    chip(P, w / 2 - 70, 70, 140, kind)
    P.text(w / 2, 300, lab, 'Poppins-600', 36, WHITE, anchor='ms')
    return P.sprite()


def render_clip(t, ins):
    name = ins[2]
    if name == 'saas_spark_up':
        return render_spark(t, ins, True)
    if name == 'saas_spark_down':
        return render_spark(t, ins, False)
    if name == 'saas_stack':
        return render_stack(t, ins)
    if name.startswith('saas_icon_'):
        kind = name[len('saas_icon_'):]
        col = {'dollar': GREEN, 'bank': GOLD, 'pct': GOLD, 'au': GOLD, 'chart': TEAL}.get(kind, GOLD)
        return render_icon(t, ins, kind, col)
    return None
