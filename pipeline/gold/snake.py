"""Snake captions (ref 5): the line's words flow along a rounded curve around her head - an arc over her
head, a curve down her empty side, or a gentle wave under her face - led by a thin glowing guide line
that draws ahead of the words like a snake. Words slide into place along the curve with a motion-blur
trail and slide off the end when the line is done. The curve is rebuilt every frame from her tracked
face, so it moves with her and the camera.

Gwyner gold keywords + Poppins white words (Roman Urdu / Hinglish, as spoken).
"""
import math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw

import gold_reel as G
from gold_reel import en, K, clamp, lerp

WHITE_F, WHITE_PX = 'Poppins-600', 56
GOLD_PX = 98
LINE = (1.0, 0.80, 0.42)
SAFE = (70, 250, 950, 1470)


def _ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 4

# ---------------------------------------------------------------- glyphs


@functools.lru_cache(maxsize=6000)
def glyph(ch, font, px, gold):
    """Single character sprite (premultiplied RGBA at K), with its pen/baseline anchor as fractions."""
    f = en.font(font, int(px * K))
    asc, desc = f.getmetrics()
    pad = int(px * 0.45 * K) + 6
    w = int(math.ceil(f.getlength(ch))) + 2 * pad + 4
    h = asc + desc + 2 * pad
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((pad, pad + asc), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im, np.float32) / 255
    if gold:
        a = cv2.dilate(a, np.ones((3, 3), np.uint8), iterations=max(1, int(round(0.6 * K))))
    sh = np.clip(np.roll(cv2.GaussianBlur(a, (0, 0), 2.5 * K), int(2 * K), axis=0) * 0.6
                 + cv2.GaussianBlur(a, (0, 0), 9 * K) * 0.4, 0, 0.85)
    rgb = np.zeros((h, w, 3), np.float32)
    al = sh.copy()
    if gold:
        g = cv2.GaussianBlur(a, (0, 0), 5 * K) * 0.55
        rgb += g[..., None] * np.array([1.0, 0.70, 0.24], np.float32)
        al = np.clip(al + g * 0.6, 0, 1)
        ys = np.clip((np.arange(h, dtype=np.float32) - pad) / max(asc, 1), 0, 1)[:, None, None]
        face = np.array([1.0, 0.92, 0.60], np.float32) * (1 - ys) + np.array([0.93, 0.62, 0.20], np.float32) * ys
    else:
        g = cv2.GaussianBlur(a, (0, 0), 6 * K) * 0.12
        rgb += g[..., None] * np.array([1.0, 0.95, 0.88], np.float32)
        al = np.clip(al + g * 0.5, 0, 1)
        face = np.broadcast_to(np.array([0.97, 0.96, 0.94], np.float32), (h, w, 3))
    rgb = face * a[..., None] + rgb * (1 - a[..., None])
    al = a + al * (1 - a)
    return np.concatenate([rgb, al[..., None]], 2).astype(np.float32), pad / w, (pad + asc) / h


@functools.lru_cache(maxsize=2000)
def advances(word, font, px):
    """Per-character pen advances (design px) including kerning."""
    f = en.font(font, int(px * K))
    out, prev = [], 0.0
    for i in range(len(word)):
        cur = f.getlength(word[:i + 1])
        out.append((cur - prev) / K)
        prev = cur
    return out


def word_font(w, key_font, k=1.0):
    return (key_font, GOLD_PX * k) if w['gold'] else (WHITE_F, WHITE_PX * k)


def text_len(words, key_font, k=1.0):
    total = 0.0
    for j, w in enumerate(words):
        f, px = word_font(w, key_font, k)
        total += sum(advances(w['text'], f, round(px)))
        if j:
            total += WHITE_PX * k * 0.34
    return total

# ---------------------------------------------------------------- paths


class Path:
    def __init__(self, pts):
        pts = np.asarray(pts, np.float64)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
        self.p, self.s, self.L = pts, d, d[-1]

    def at(self, s):
        s = np.clip(s, 0, self.L)
        x = np.interp(s, self.s, self.p[:, 0])
        y = np.interp(s, self.s, self.p[:, 1])
        e = 2.0
        x1 = np.interp(np.clip(s + e, 0, self.L), self.s, self.p[:, 0])
        y1 = np.interp(np.clip(s + e, 0, self.L), self.s, self.p[:, 1])
        x0 = np.interp(np.clip(s - e, 0, self.L), self.s, self.p[:, 0])
        y0 = np.interp(np.clip(s - e, 0, self.L), self.s, self.p[:, 1])
        return x, y, np.degrees(np.arctan2(y1 - y0, x1 - x0))


def bezier(P, n=160):
    P = np.asarray(P, np.float64)
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3])


def make_path(kind, fr, side, row=0, rows=1, k=1.0, wobble=0.0):
    x0, y0, x1, y1 = fr
    fcx, fcy, fw, fh = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    if kind == 'arc':                                   # rainbow over her head, reads left -> right
        rx, ry = fw * 0.62 + 44 * k, fh * 0.60 + 52 * k
        th = np.radians(np.linspace(206, 334, 160))
        pts = np.c_[fcx + rx * np.cos(th), fcy + ry * np.sin(th) + 8 * wobble]
        return Path(pts)
    if kind == 'side':                                  # curls from over her head down the empty side
        xs = x1 if side > 0 else x0
        P = [(fcx - side * fw * 0.10, y0 - 46 * k), (fcx + side * fw * 0.62, y0 - 70 * k),
             (xs + side * 70 * k, fcy - fh * 0.05), (xs + side * 26 * k, y1 + 70 * k)]
        pts = bezier(P)
        if side < 0:
            pts = pts[::-1]                             # on the left it reads upward (left -> right)
        return Path(pts)
    if kind == 'smile':                                 # curves under her chin, reads left -> right
        rx = fw * 0.66 + 36 * k
        ry = fh * 0.5 + 34 * k + GOLD_PX * k * 0.85
        th = np.radians(np.linspace(158, 22, 160))
        pts = np.c_[fcx + rx * np.cos(th), fcy + ry * np.sin(th) + 6 * wobble]
        return Path(pts)
    if kind == 'diag':                                  # snake S sweeping across, left -> right
        width = SAFE[2] - SAFE[0] - 20
        xa, xb = fcx - width / 2, fcx + width / 2
        sh = (xa - SAFE[0] - 15) if xa < SAFE[0] + 15 else (xb - SAFE[2] + 15) if xb > SAFE[2] - 15 else 0
        xa, xb = xa - sh, xb - sh
        ya = y1 + 50 * k + GOLD_PX * k * 0.8
        dy = side * 200 * k
        P = [(xa, ya + max(0, -dy)), (xa + width * 0.36, ya + max(0, -dy) + 230 * k),
             (xa + width * 0.64, ya + max(0, dy) - 190 * k), (xb, ya + max(0, dy) + 30 * k)]
        return Path(bezier(P))
    # 'wave': gentle S under her face; extra rows stack below
    width = min(SAFE[2] - SAFE[0] - 40, max(fw * 2.3, 640))
    ys = y1 + 64 * k + GOLD_PX * k * 0.55 + row * (GOLD_PX * k * 1.05)
    xs = np.linspace(fcx - width / 2, fcx + width / 2, 160)
    xs = np.clip(xs, SAFE[0] + 10, SAFE[2] - 10)
    ph = 0.6 * row + wobble
    pts = np.c_[xs, ys + 30 * k * np.sin((xs - xs[0]) / max(width, 1) * 2 * math.pi * 0.9 + ph)]
    return Path(pts)

# ---------------------------------------------------------------- drawing


def _draw_glyph(cv, spr, ax, ay, x, y, rot, op):
    h, w = spr.shape[:2]
    en.warp(cv, spr, en.quad_2d(x, y, w / K, h / K, 1.0, rot, ax, ay), op, 'over')


def _draw_line(cv, path, s0, s1, off, op):
    """Thin glowing guide line along the path, offset to the outside of the text, soft ends."""
    if s1 - s0 < 4 or op <= 0.01:
        return
    ss = np.linspace(s0, s1, max(8, int((s1 - s0) / 4)))
    x, y, ang = path.at(ss)
    a = np.radians(ang)
    nx, ny = -np.sin(a), np.cos(a)
    px, py = (x + nx * off) * K, (y + ny * off) * K
    pad = int(14 * K)
    bx0, by0 = int(max(0, px.min() - pad)), int(max(0, py.min() - pad))
    bx1, by1 = int(min(cv.shape[1], px.max() + pad)), int(min(cv.shape[0], py.max() + pad))
    if bx1 <= bx0 or by1 <= by0:
        return
    m8 = np.zeros((by1 - by0, bx1 - bx0), np.uint8)
    P = np.int32(np.c_[(px - bx0) * 16, (py - by0) * 16])
    cv2.polylines(m8, [P], False, 255, max(1, int(2.8 * K)), cv2.LINE_AA, shift=4)
    m = m8.astype(np.float32) / 255
    # fade both ends
    n = len(ss)
    fade = np.clip(np.minimum(np.arange(n), n - 1 - np.arange(n)) / max(n * 0.18, 1), 0, 1)
    fm = np.zeros_like(m)
    for j in range(0, n, max(1, n // 40)):
        cv2.circle(fm, (int(px[j] - bx0), int(py[j] - by0)), int(10 * K), float(fade[j]), -1)
    m *= cv2.GaussianBlur(fm, (0, 0), 6 * K)
    g = cv2.GaussianBlur(m, (0, 0), 4 * K)
    reg = cv[by0:by1, bx0:bx1]
    col = np.array(LINE, np.float32)
    reg += g[..., None] * col * 0.95 * op
    a_ = (m * 1.0 * op)[..., None]
    reg[:] = reg * (1 - a_) + col * a_


def draw_phrase(cv, t, ph, fr, choice, key_font):
    """choice: (kind, side, k, rows) fixed per line. fr: her face rect on screen this frame."""
    kind, side, k, rows = choice
    words_all = [w for r in ph['rows'] for w in r]
    out_q = clamp((t - (ph['t_off'] - 0.22)) / 0.22)
    groups = rows if kind == 'wave' else [words_all]
    for gi, words in enumerate(groups):
        path = make_path(kind, fr, side, gi, len(groups), k, wobble=0.15 * math.sin(t * 1.3 + ph['i']))
        L = text_len(words, key_font, k)
        s0 = max(0.0, (path.L - L) / 2)
        # pen positions
        chars = []
        s = s0
        for j, w in enumerate(words):
            f, px = word_font(w, key_font, k)
            px = round(px)
            if j:
                s += WHITE_PX * k * 0.34
            for ch, adv in zip(w['text'], advances(w['text'], f, px)):
                chars.append((w, ch, f, px, s, adv))
                s += adv
        # guide line: grows ahead of the latest word, retracts with the exit
        spoken = [c for c in chars if t >= c[0]['t'] - 0.03]
        if spoken:
            last = spoken[-1]
            p_last = _ease_out((t - (last[0]['t'] - 0.03)) / 0.32)
            head = lerp(last[4] - 40, last[4] + last[5] + 46, p_last)
            tail = s0 - 34 + out_q * out_q * (L + 120)
            off = WHITE_PX * k * 0.42
            _draw_line(cv, path, tail, min(path.L, head + out_q * out_q * 160), off, 0.9 * (1 - out_q))
        for (w, ch, f, px, sc, adv) in chars:
            u = t - (w['t'] - 0.03)
            if u < 0 or ch == ' ':
                continue
            spr, ax, ay = glyph(ch, f, px, w['gold'])
            D = 170 * k
            op = clamp(u / 0.07) * (1 - out_q)
            if op <= 0.01:
                continue
            # entrance: slide along the curve from behind, real sub-frame trail = motion blur
            trail = [(0.0, 1.0)] + [(0.010 * q, a) for q, a in ((1, 0.42), (2, 0.26), (3, 0.15), (4, 0.08))]
            for dtq, a in reversed(trail):
                uu = u - dtq
                if uu < 0:
                    continue
                pos = sc + adv / 2 - (1 - _ease_out(uu / 0.34)) * D
                ex = t - dtq - (ph['t_off'] - 0.22)
                if ex > 0:
                    pos += (clamp(ex / 0.22) ** 2) * 150
                x, y, ang = path.at(pos)
                # pen sits at pos - adv/2 along the tangent
                r = math.radians(float(ang))
                xp, yp = float(x) - math.cos(r) * adv / 2, float(y) - math.sin(r) * adv / 2
                if a < 1.0 and (u - dtq) > 0.34 and ex <= 0:
                    continue                                # settled: no trail
                _draw_glyph(cv, spr, ax, ay, xp, yp, float(ang), op * a)
