"""Spider-Man in-mask HUD / SaaS UI for the Yaadein reel: frosted glass panels with red/blue edge light,
white type. Every panel is painted per frame at 2x (premultiplied linear RGBA) and placed as a 3D plane
by the compositor, so it gets parallax, perspective, lens blur and motion blur like a real object.
"""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import anim as A
import comp as C
from captions import FONTS

SS = 2
RED = np.array([1.0, 0.09, 0.07], np.float32)
BLUE = np.array([0.16, 0.42, 1.0], np.float32)
WHITE = np.array([0.96, 0.96, 0.97], np.float32)
MUTED = np.array([0.62, 0.65, 0.72], np.float32)
DARK = np.array([0.02, 0.025, 0.04], np.float32)


@functools.lru_cache(maxsize=64)
def _font(name, px):
    return ImageFont.truetype(f'{FONTS}/{name}.ttf', int(px))


@functools.lru_cache(maxsize=512)
def text_mask(txt, name, px, track=0.0):
    f = _font(name, px * SS)
    asc, desc = f.getmetrics()
    if track:
        w = int(sum(f.getlength(c) for c in txt) + track * SS * px * (len(txt) - 1)) + 8
    else:
        w = int(f.getlength(txt)) + 8
    im = Image.new('L', (max(w, 1), asc + desc + 8), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = 4.0
        for c in txt:
            d.text((x, 4 + asc), c, font=f, fill=255, anchor='ls')
            x += f.getlength(c) + track * SS * px
    else:
        d.text((4, 4 + asc), txt, font=f, fill=255, anchor='ls')
    return np.asarray(im, np.float32) / 255, 4 + asc


class Paint:
    def __init__(self, w, h, pad=40):
        self.p = pad
        self.w, self.h = w, h
        self.Wp, self.Hp = (w + 2 * pad) * SS, (h + 2 * pad) * SS
        self.rgb = np.zeros((self.Hp, self.Wp, 3), np.float32)
        self.a = np.zeros((self.Hp, self.Wp), np.float32)
        self._yy, self._xx = np.mgrid[0:self.Hp, 0:self.Wp].astype(np.float32)

    def X(self, x):
        return (x + self.p) * SS

    def over(self, m, col, op=1.0):
        m = np.clip(m * op, 0, 1)
        if m.ndim == 2:
            m3 = m[..., None]
        self.rgb = np.asarray(col, np.float32) * m3 + self.rgb * (1 - m3)
        self.a = m + self.a * (1 - m)

    def add(self, m, col, op=1.0):
        self.rgb += np.asarray(col, np.float32) * (m * op)[..., None]
        self.a = np.clip(self.a + m * op * 0.6, 0, 1)

    def sdf_rrect(self, x, y, w, h, r):
        cx, cy = self.X(x + w / 2), self.X(y + h / 2)
        qx = np.abs(self._xx + 0.5 - cx) - (w / 2 - r) * SS
        qy = np.abs(self._yy + 0.5 - cy) - (h / 2 - r) * SS
        return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r * SS

    def rrect(self, x, y, w, h, r, col, op=1.0):
        m = np.clip(0.5 - self.sdf_rrect(x, y, w, h, r), 0, 1)
        self.over(m, col, op)
        return m

    def stroke(self, x, y, w, h, r, width, col, op=1.0, mul=None):
        d = self.sdf_rrect(x, y, w, h, r)
        m = np.clip(0.5 - (np.abs(d + width * SS / 2) - width * SS / 2), 0, 1)
        if mul is not None:
            m = m * mul
        self.over(m, col, op)
        return m

    def glow(self, m, col, sigma, k):
        g = cv2.GaussianBlur(m, (0, 0), sigma * SS)
        self.add(g, col, k)

    def text(self, txt, x, y, name='Inter-600', px=28, col=WHITE, op=1.0, anchor='l', track=0.0, reveal=1.0):
        """y = baseline. reveal 0..1 types the text on (cursor-style)."""
        if reveal <= 0:
            return
        if reveal < 1:
            txt = txt[:max(1, int(round(len(txt) * reveal)))]
        m, base = text_mask(txt, name, px, track)
        hh, ww = m.shape
        X = int(self.X(x) - (ww / 2 if anchor == 'c' else ww if anchor == 'r' else 0))
        Y = int(self.X(y) - base)
        x0, y0, x1, y1 = max(0, X), max(0, Y), min(self.Wp, X + ww), min(self.Hp, Y + hh)
        if x1 <= x0 or y1 <= y0:
            return
        full = np.zeros((self.Hp, self.Wp), np.float32)
        full[y0:y1, x0:x1] = m[y0 - Y:y1 - Y, x0 - X:x1 - X]
        self.over(full, col, op)

    def circle(self, cx, cy, r, col, op=1.0):
        d = np.hypot(self._xx + 0.5 - self.X(cx), self._yy + 0.5 - self.X(cy)) - r * SS
        m = np.clip(0.5 - d, 0, 1)
        self.over(m, col, op)
        return m

    def arc(self, cx, cy, r, width, a0, a1, col, op=1.0, grad=None):
        """Ring segment from angle a0 to a1 (deg, 0 = up, clockwise)."""
        dx, dy = self._xx + 0.5 - self.X(cx), self._yy + 0.5 - self.X(cy)
        rad = np.hypot(dx, dy)
        ang = (np.degrees(np.arctan2(dx, -dy)) + 360) % 360
        ring = np.clip(0.5 - (np.abs(rad - r * SS) - width * SS / 2), 0, 1)
        lo, hi = min(a0, a1), max(a0, a1)
        seg = np.clip((ang - lo) * r * SS * math.pi / 180 + 0.5, 0, 1) * np.clip((hi - ang) * r * SS * math.pi / 180 + 0.5, 0, 1)
        m = ring * seg
        if grad is not None:
            u = np.clip((ang - lo) / max(hi - lo, 1e-3), 0, 1)[..., None]
            col = np.asarray(grad[0], np.float32) * (1 - u) + np.asarray(grad[1], np.float32) * u
            self.rgb = col * m[..., None] + self.rgb * (1 - m[..., None])
            self.a = m + self.a * (1 - m)
        else:
            self.over(m, col, op)
        return m

    def line(self, pts, width, col, op=1.0):
        m = np.zeros((self.Hp, self.Wp), np.float32)
        P = np.int32([[self.X(x) * 8, self.X(y) * 8] for x, y in pts])
        cv2.polylines(m, [P], False, 1.0, max(1, int(width * SS)), cv2.LINE_AA, shift=3)
        self.over(m, col, op)
        return m

    def image(self, img, x, y, w, h, r=12, op=1.0):
        """Place an sRGB float image (h, w, 3) into a rounded rect."""
        im = cv2.resize(img, (int(w * SS), int(h * SS)), interpolation=cv2.INTER_AREA)
        full = np.zeros_like(self.rgb)
        X, Y = int(self.X(x)), int(self.X(y))
        full[Y:Y + im.shape[0], X:X + im.shape[1]] = im[:self.Hp - Y, :self.Wp - X]
        m = np.clip(0.5 - self.sdf_rrect(x, y, w, h, r), 0, 1) * op
        self.rgb = full * m[..., None] + self.rgb * (1 - m[..., None])
        self.a = m + self.a * (1 - m)
        return m

    def result(self):
        """premultiplied linear RGBA."""
        rgb = C.to_lin(np.clip(self.rgb, 0, 1)) * 1.0
        a = np.clip(self.a, 0, 1)
        # rgb painted with 'over' is already premultiplied by coverage
        return np.dstack([rgb, a]).astype(np.float32)


def glass_panel(p, x, y, w, h, r=28, edge=(RED, BLUE), op=1.0, edge_k=1.0):
    """Dark glass body + hairline border lit red on one corner and blue on the other."""
    body = np.clip(0.5 - p.sdf_rrect(x, y, w, h, r), 0, 1)
    p.over(body, DARK, 0.42 * op)
    p.add(body * np.clip(1 - (p._yy - p.X(y)) / (h * SS * 0.6), 0, 1), WHITE, 0.035 * op)   # top sheen
    u = np.clip(((p._xx - p.X(x)) / (w * SS) + (p._yy - p.X(y)) / (h * SS)) / 2, 0, 1)[..., None]
    col = np.asarray(edge[0]) * (1 - u) + np.asarray(edge[1]) * u
    d = p.sdf_rrect(x, y, w, h, r)
    ring = np.clip(0.5 - (np.abs(d + 0.75 * SS) - 0.75 * SS), 0, 1)
    p.rgb = col * (ring * op)[..., None] * 0.9 + p.rgb * (1 - (ring * op)[..., None])
    p.a = np.clip(p.a + ring * op, 0, 1)
    wide = cv2.GaussianBlur(ring, (0, 0), 8 * SS)
    p.rgb += col * (wide * 0.5 * op * edge_k)[..., None]
    p.a = np.clip(p.a + wide * 0.3 * op * edge_k, 0, 1)
    p.stroke(x + 1, y + 1, w - 2, h - 2, r - 1, 1, WHITE, 0.10 * op)
    return body


# ---------------------------------------------------------------- widgets
_PHOTOS = {}


def set_photo(key, img):
    _PHOTOS[key] = img


def memory_card(t, photo_key, name='MEMORY_0427.JPG', tag='KHUSHI', date='14 . 02 . 2019'):
    q = int(t * 30)
    return _memory_card(min(q, 40) if q < 40 else 40 + q % 27, photo_key, name, tag, date)


@functools.lru_cache(maxsize=128)
def _memory_card(q, photo_key, name, tag, date):
    """Glass card: memory thumbnail + file name, typing-on, scan line across the photo."""
    t = q / 30
    w, h = 660, 270
    p = Paint(w, h)
    op = 1.0
    glass_panel(p, 0, 0, w, h, 30, op=op)
    reveal = A.ramp(t, 0.15, 0.9, A.LINEAR)
    photo = _PHOTOS.get(photo_key)
    if photo is not None:
        p.image(photo, 22, 22, 226, 226, 20, op=A.ramp(t, 0.1, 0.5))
        sy = 22 + 226 * ((t * 0.9) % 1.0)
        p.add(np.exp(-((p._yy - p.X(sy)) / (3 * SS)) ** 2) * np.clip(0.5 - p.sdf_rrect(22, 22, 226, 226, 20), 0, 1),
              RED, 0.9 * op)
    p.text('MEMORY FILE', 278, 64, 'SpaceGrotesk-500', 20, MUTED, op, track=0.18, reveal=reveal)
    p.text(name, 278, 108, 'SpaceGrotesk-700', 32, WHITE, op, reveal=reveal)
    p.rrect(278, 136, 168, 44, 22, RED, 0.18 * op)
    p.stroke(278, 136, 168, 44, 22, 1.2, RED, 0.9 * op)
    p.text('♥  ' + tag, 362, 166, 'Inter-700', 20, WHITE, op * A.ramp(t, 0.4, 0.7), anchor='c', track=0.12)
    p.text(date, 278, 222, 'SpaceGrotesk-500', 20, MUTED, op * A.ramp(t, 0.5, 0.9), track=0.1)
    return p.result()


def delete_dialog(t, hover=0.0, press=0.0, cancel_hover=0.0):
    return _delete_dialog(round(hover * 16) / 16, round(press * 8) / 8, round(cancel_hover * 16) / 16)


@functools.lru_cache(maxsize=256)
def _delete_dialog(hover, press, cancel_hover):
    w, h = 720, 360
    p = Paint(w, h)
    op = 1.0
    glass_panel(p, 0, 0, w, h, 34, op=op)
    # icon
    p.circle(70, 78, 30, RED, 0.16 * op)
    p.line([(58, 66), (82, 90)], 3.2, RED, op)
    p.line([(82, 66), (58, 90)], 3.2, RED, op)
    p.text('Delete this memory?', 120, 92, 'Inter-700', 38, WHITE, op)
    p.text('Ye yaad hamesha ke liye mit jayegi.', 44, 160, 'Inter-500', 25, MUTED, op)
    p.text('This action cannot be undone.', 44, 196, 'Inter-500', 22, MUTED, 0.7 * op)
    # buttons
    bx, by, bw, bh = 44, 248, 300, 72
    p.rrect(bx, by, bw, bh, 36, WHITE, (0.06 + 0.08 * cancel_hover) * op)
    p.stroke(bx, by, bw, bh, 36, 1.2, WHITE, (0.35 + 0.4 * cancel_hover) * op)
    p.text('Cancel', bx + bw / 2, by + 46, 'Inter-600', 27, WHITE, op, anchor='c')
    dx = 376
    k = 1 - 0.04 * press
    cx, cy = dx + bw / 2, by + bh / 2
    m = p.rrect(cx - bw * k / 2, cy - bh * k / 2, bw * k, bh * k, 36, RED, (0.75 + 0.25 * hover) * op)
    p.glow(m, RED, 10, (0.5 + 0.9 * hover) * op)
    p.text('Delete', cx, by + 46, 'Inter-700', 27, WHITE, op, anchor='c')
    return p.result()


@functools.lru_cache(maxsize=2)
def cursor(scale=1.0):
    """macOS-like arrow cursor sprite (premultiplied linear RGBA), tip at (pad, pad)."""
    p = Paint(40, 56, pad=10)
    pts = [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (34, 31)]
    m = np.zeros((p.Hp, p.Wp), np.float32)
    cv2.fillPoly(m, [np.int32([[p.X(x) * 8, p.X(y) * 8] for x, y in pts])], 1.0, cv2.LINE_AA, shift=3)
    sh = cv2.GaussianBlur(np.roll(m, 4 * SS, axis=0), (0, 0), 4 * SS)
    p.over(sh * 0.6, DARK)
    ring = np.clip(cv2.dilate(m, np.ones((5, 5), np.uint8)) - m, 0, 1)
    p.over(cv2.dilate(m, np.ones((5, 5), np.uint8)), WHITE)
    p.over(m, DARK)
    p.over(np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8)), 0, 1) * 0, WHITE)
    return p.result()


def meter(t, value, label='KHUSHI', crash=0.0):
    return _meter(round(value * 2) / 2, label, round(crash * 16) / 16)


@functools.lru_cache(maxsize=512)
def _meter(value, label, crash):
    """Ring gauge. value 0..100. crash 0..1 -> red glitch state."""
    w = h = 460
    p = Paint(w, h)
    op = 1.0
    glass_panel(p, 0, 0, w, h, 230, op=op, edge_k=0.6)
    cx = cy = 230
    p.arc(cx, cy, 168, 16, 0, 360, WHITE, 0.08 * op)
    col_hi = WHITE * (1 - crash) + RED * crash
    a1 = 360 * value / 100
    if a1 > 0.5:
        m = p.arc(cx, cy, 168, 16, 0, a1, None, op, grad=(BLUE * (1 - crash) + RED * crash, col_hi))
        p.glow(m, col_hi, 9, 0.7 * op)
    p.text(f'{int(round(value))}', cx, cy + 34, 'InterTight-800', 108, col_hi, op, anchor='c')
    p.text('%', cx + 92, cy - 18, 'Inter-700', 34, MUTED, op, anchor='c')
    p.text(label, cx, cy + 92, 'SpaceGrotesk-700', 24, MUTED * (1 - crash) + RED * crash, op, anchor='c', track=0.3)
    return p.result()


def truth_check(t, progress, result=0.0):
    return _truth_check(round(min(t, 1.0) * 30) / 30, round(progress * 100) / 100, round(result * 24) / 24)


@functools.lru_cache(maxsize=512)
def _truth_check(t, progress, result):
    w, h = 640, 210
    p = Paint(w, h)
    op = 1.0
    glass_panel(p, 0, 0, w, h, 26, op=op)
    p.text('TRUTH CHECK', 36, 58, 'SpaceGrotesk-700', 24, MUTED, op, track=0.3)
    p.text(f'{int(progress * 100):3d}%', w - 36, 58, 'SpaceGrotesk-700', 24, WHITE, op, anchor='r')
    p.rrect(36, 82, w - 72, 10, 5, WHITE, 0.10 * op)
    if progress > 0.005:
        m = p.rrect(36, 82, (w - 72) * progress, 10, 5, BLUE * (1 - result) + RED * result, op)
        p.glow(m, BLUE * (1 - result) + RED * result, 6, 0.8 * op)
    if result > 0:
        k = A.BACK_OUT(A.clamp(result))
        p.text('FALSE', w / 2, 178, 'InterTight-900', int(64 * (0.6 + 0.4 * k)), RED, op * A.clamp(result * 2), anchor='c',
               track=0.25)
    else:
        p.text('analysing memory…', 36, 160, 'SpaceGrotesk-500', 24, MUTED, op, reveal=A.ramp(t, 0.1, 0.8, A.LINEAR))
    return p.result()


def glitch(img, amount, t, seed=0):
    """RGB split + horizontal slice offsets on a canvas region (linear HxWx3/4)."""
    if amount <= 0.01:
        return img
    rng = np.random.default_rng(int(t * 60) * 7 + seed)
    out = img.copy()
    h, w = img.shape[:2]
    sh = int(18 * amount)
    out[..., 0] = np.roll(img[..., 0], sh, axis=1)
    out[..., 2] = np.roll(img[..., 2], -sh, axis=1)
    for _ in range(int(10 * amount)):
        y0 = rng.integers(0, h - 10)
        hh = rng.integers(6, max(8, int(h * 0.06)))
        dx = int(rng.normal(0, 60 * amount))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], dx, axis=1)
    return out
