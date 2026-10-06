"""Cinematic snake captions (Roman Urdu), brand palette orange / black / white.

A phrase lies along a smooth bezier 'snake' path. A thin glowing guide line draws ahead of the voice;
each word glides in along the path as it is spoken (long liquid ease-out), pulling focus from a soft
blur to sharp while it fades up, then the phrase drifts on along the path and defocuses out.
Keywords (*word in script.py) are orange serif-italic with a warm glow; the rest are white sans.
"""
import functools
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import anim as A
import comp as C

FONTS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace', 'fonts'))
WHITE_F, WHITE_PX = 'Poppins-600', 54
KEY_F, KEY_PX = 'GwynerCondensed-Italic', 104
ORANGE_HI = np.array([1.0, 0.62, 0.20], np.float32)
ORANGE = np.array([1.0, 0.36, 0.02], np.float32)
WHITE = np.array([0.97, 0.96, 0.95], np.float32)
LINE = np.array([1.0, 0.45, 0.08], np.float32)
SPACE = 0.42


@functools.lru_cache(maxsize=32)
def font(name, px):
    return ImageFont.truetype(f'{FONTS}/{name}.ttf', px)


@functools.lru_cache(maxsize=4000)
def glyph(ch, key, blur=0):
    """Premultiplied *linear* RGBA sprite of one character + anchor (pen x, baseline y) in sprite px."""
    f = font(KEY_F, KEY_PX) if key else font(WHITE_F, WHITE_PX)
    px = KEY_PX if key else WHITE_PX
    asc, desc = f.getmetrics()
    pad = int(px * 0.5) + int(blur * 1.5)
    w = int(math.ceil(f.getlength(ch))) + 2 * pad + 4
    h = asc + desc + 2 * pad
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).text((pad, pad + asc), ch, font=f, fill=255, anchor='ls')
    a = np.asarray(im, np.float32) / 255
    if blur > 0:
        a = C.disc_blur(a, blur)
    # soft black drop shadow for legibility on bright plates
    sh = np.clip(cv2.GaussianBlur(np.roll(a, 5, axis=0), (0, 0), 4 + blur * 0.5) * 0.95
                 + cv2.GaussianBlur(np.roll(a, 9, axis=0), (0, 0), 14 + blur) * 0.65, 0, 0.92)
    if key:
        ys = np.clip((np.arange(h, dtype=np.float32) - pad) / max(asc, 1), 0, 1)[:, None, None]
        face = ORANGE_HI * (1 - ys) + ORANGE * ys
        glow = cv2.GaussianBlur(a, (0, 0), 9) * 0.55
        rgb = face * a[..., None] + glow[..., None] * ORANGE * (1 - a[..., None])
        al = a + np.maximum(sh, glow * 0.25) * (1 - a)
    else:
        glow = cv2.GaussianBlur(a, (0, 0), 7) * 0.10
        rgb = WHITE * a[..., None] + glow[..., None] * WHITE * (1 - a[..., None])
        al = a + sh * (1 - a)
    rgb = C.to_lin(np.clip(rgb, 0, 1)) * (1 if True else 1)
    spr = np.dstack([rgb * 1.0, al]).astype(np.float32)
    spr[..., :3] = rgb                                  # rgb already carries coverage (premultiplied)
    return spr, pad, pad + asc


@functools.lru_cache(maxsize=2000)
def advances(word, key):
    f = font(KEY_F, KEY_PX) if key else font(WHITE_F, WHITE_PX)
    out, prev = [], 0.0
    for i in range(len(word)):
        cur = f.getlength(word[:i + 1])
        out.append(cur - prev)
        prev = cur
    return tuple(out)


@functools.lru_cache(maxsize=4000)
def glow_sprite(ch, key):
    """Soft additive glow of a glyph (same anchor as glyph(ch, key, 0))."""
    spr, ax, ay = glyph(ch, key, 0)
    a = spr[..., 3] * (spr[..., :3].max(2) > 0.02)
    g = cv2.GaussianBlur(a, (0, 0), 9) * 0.7 + cv2.GaussianBlur(a, (0, 0), 22) * 0.5
    col = ORANGE if key else np.float32([1.0, 0.78, 0.62])
    out = np.zeros_like(spr)
    out[..., :3] = g[..., None] * col
    out[..., 3] = 0
    return out, ax, ay


def blit(cv, spr, ax, ay, x, y, rot, scale, op, mode='over'):
    """Place sprite so its anchor (ax, ay) lands on canvas (x, y), rotated (deg) and scaled."""
    if op <= 0.004:
        return
    h, w = spr.shape[:2]
    r = math.radians(rot)
    c, s = math.cos(r) * scale, math.sin(r) * scale
    M = np.float32([[c, -s, x - (c * ax - s * ay)], [s, c, y - (s * ax + c * ay)]])
    corners = np.float32([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]]) @ M.T
    x0, y0 = np.floor(corners.min(0)).astype(int) - 1
    x1, y1 = np.ceil(corners.max(0)).astype(int) + 1
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(C.W, x1), min(C.H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    M[0, 2] -= x0
    M[1, 2] -= y0
    out = cv2.warpAffine(spr, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    out *= op
    reg = cv[y0:y1, x0:x1]
    if mode == 'add':
        reg[..., :3] += out[..., :3]
    else:
        reg[..., :3] = out[..., :3] + reg[..., :3] * (1 - out[..., 3:4])


class Path:
    def __init__(self, pts):
        pts = np.asarray(pts, np.float64)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
        self.p, self.s, self.L = pts, d, d[-1]

    def at(self, s):
        s = np.clip(s, -400, self.L + 400)
        x = np.interp(s, self.s, self.p[:, 0])
        y = np.interp(s, self.s, self.p[:, 1])
        # extrapolate linearly beyond the ends
        e = 3.0
        sa, sb = np.clip(s - e, 0, self.L), np.clip(s + e, 0, self.L)
        dx = np.interp(sb, self.s, self.p[:, 0]) - np.interp(sa, self.s, self.p[:, 0])
        dy = np.interp(sb, self.s, self.p[:, 1]) - np.interp(sa, self.s, self.p[:, 1])
        n = np.maximum(np.hypot(dx, dy), 1e-6)
        over = np.clip(s - self.L, 0, None) + np.clip(s, None, 0)
        return x + dx / n * over, y + dy / n * over, np.degrees(np.arctan2(dy, dx))


def bezier(P, n=200):
    """Chain of cubic segments: P = [p0, c1, c2, p1, c3, c4, p2, ...]."""
    P = np.asarray(P, np.float64)
    out = []
    for i in range(0, len(P) - 3, 3):
        t = np.linspace(0, 1, n)[:, None]
        seg = ((1 - t) ** 3 * P[i] + 3 * (1 - t) ** 2 * t * P[i + 1] + 3 * (1 - t) * t ** 2 * P[i + 2]
               + t ** 3 * P[i + 3])
        out.append(seg if not out else seg[1:])
    return np.vstack(out)


def _guide(cv, path, s0, s1, off, op):
    if s1 - s0 < 6 or op <= 0.01:
        return
    ss = np.linspace(s0, s1, max(10, int((s1 - s0) / 5)))
    x, y, ang = path.at(ss)
    a = np.radians(ang)
    px, py = x - np.sin(a) * off, y + np.cos(a) * off
    pad = 30
    bx0, by0 = int(max(0, px.min() - pad)), int(max(0, py.min() - pad))
    bx1, by1 = int(min(C.W, px.max() + pad)), int(min(C.H, py.max() + pad))
    if bx1 <= bx0 or by1 <= by0:
        return
    m = np.zeros((by1 - by0, bx1 - bx0), np.float32)
    n = len(ss)
    fade = np.clip(np.arange(n) / max(n * 0.35, 1), 0, 1) ** 1.5             # tail fades, head is hot
    P = np.c_[(px - bx0), (py - by0)]
    for j in range(n - 1):
        cv2.line(m, tuple(np.int32(P[j] * 16)), tuple(np.int32(P[j + 1] * 16)), float(fade[j]), 2, cv2.LINE_AA, shift=4)
    head = np.zeros_like(m)
    cv2.circle(head, tuple(np.int32(P[-1] * 16)), 3 * 16, 1.0, -1, cv2.LINE_AA, shift=4)
    glow = cv2.GaussianBlur(m, (0, 0), 3.0) * 0.9 + cv2.GaussianBlur(head, (0, 0), 7) * 2.2
    reg = cv[by0:by1, bx0:bx1]
    reg[..., :3] += (glow[..., None] * LINE * 1.2 + (m + head * 0.8)[..., None] * C.to_lin(np.float32([1, 0.8, 0.6]))) * op


class Phrase:
    """words: [(text, t, key)], path: Path, t_out: when it leaves."""

    def __init__(self, words, path, t_out, scale=1.0, line=True, enter=0.75, travel=70):
        # auto-fit: a phrase longer than its path is scaled down (keeps it inside the safe area)
        raw = sum(sum(advances(txt, key)) for txt, _, key in words) + WHITE_PX * SPACE * (len(words) - 1)
        if raw * scale > path.L * 0.9:
            scale = path.L * 0.9 / raw
        self.words, self.path, self.t_out, self.k = words, path, t_out, scale
        self.line, self.enter, self.travel = line, enter, travel
        # lay words out along the path, centred
        lay = []
        s = 0.0
        for j, (txt, t, key) in enumerate(words):
            if j:
                s += WHITE_PX * SPACE * scale
            adv = [a * scale for a in advances(txt, key)]
            lay.append((txt, t, key, s, adv))
            s += sum(adv)
        self.len = s
        s0 = max(0.0, (path.L - s) / 2)
        self.lay = [(txt, t, key, s0 + ss, adv) for (txt, t, key, ss, adv) in lay]
        self.s0 = s0

    def _scrim(self):
        """Soft dark backing along the phrase (depth + legibility over bright plates), quarter res."""
        if getattr(self, 'scrim', None) is None:
            m = np.zeros((C.H // 4, C.W // 4), np.float32)
            ss = np.linspace(self.s0 - 40, self.s0 + self.len + 40, 40)
            x, y, _ = self.path.at(ss)
            for xi, yi in zip(x, y):
                cv2.circle(m, (int(xi / 4), int(yi / 4 - KEY_PX * 0.18 * self.k / 4)), int(KEY_PX * 0.95 * self.k / 4), 1.0, -1)
            m = cv2.GaussianBlur(m, (0, 0), 14)
            self.scrim = cv2.resize(np.clip(m * 1.2, 0, 1), (C.W, C.H), interpolation=cv2.INTER_LINEAR)[..., None]
        return self.scrim

    def draw(self, cv, t):
        out_u = (t - self.t_out) / 0.55                               # exit: 0..1
        if out_u >= 1 or t < self.lay[0][1] - 0.4:
            return
        out_e = A.EXPO_IN(A.clamp(out_u)) if out_u > 0 else 0.0
        drift = out_e * 160 * self.k
        vis = A.ramp(t, self.lay[0][1] - 0.3, self.lay[0][1] + 0.2) * (1 - A.clamp(out_u * 1.2))
        if vis > 0.01:
            cv[...] = cv * (1 - self._scrim() * 0.55 * vis)
        if self.line:
            spoken = [w for w in self.lay if t >= w[1] - 0.06]
            if spoken:
                txt, tw, key, ss, adv = spoken[-1]
                p = A.EXPO_OUT(A.clamp((t - tw + 0.06) / self.enter))
                head = ss - 30 + (sum(adv) + 70) * p + drift * 1.4
                tail = self.s0 - 40 + out_e * (self.len + 140)
                _guide(cv, self.path, tail, min(self.path.L + 60, head), KEY_PX * 0.52 * self.k,
                       0.85 * (1 - A.clamp(out_u * 1.4)))
        for (txt, tw, key, ss, adv) in self.lay:
            u = t - (tw - 0.06)
            if u < 0:
                continue
            p = A.EXPO_OUT(A.clamp(u / self.enter))                   # liquid glide in
            op = A.ramp(u, 0, self.enter * 0.55, A.EASY) * (1 - A.clamp(out_u * 1.25))
            if op <= 0.004:
                continue
            fb = (1 - A.ramp(u, 0, self.enter * 0.8, A.QUART_OUT)) * 10 + out_e * 14   # focus pull
            fb = 0 if fb < 1.0 else float(round(fb))
            sc = self.k * (1.0 + 0.10 * (1 - p) + 0.06 * out_e)
            back = (1 - p) * self.travel * self.k
            pen = ss - back + drift
            for ch, a in zip(txt, adv):
                if ch != ' ':
                    spr, ax, ay = glyph(ch, key, fb)
                    x, y, ang = self.path.at(pen + a / 2)
                    r = math.radians(float(ang))
                    xp, yp = float(x) - math.cos(r) * a / 2, float(y) - math.sin(r) * a / 2
                    gk = (0.35 + 1.6 * (1 - p)) * (1.4 if key else 0.8)       # glow flares while it animates in
                    gs, gax, gay = glow_sprite(ch, key)
                    blit(cv, gs, gax, gay, xp, yp, float(ang), sc, op * gk, mode='add')
                    blit(cv, spr, ax, ay, xp, yp, float(ang), sc, op)
                pen += a
