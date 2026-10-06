"""End card: the creator's photo in a glowing orange ring -> the circle expands until the photo fills the
frame -> burn/flash into a liquid orange/black gradient -> avatar + '@jawad_mp4' letter-by-letter ->
comment-bait CTA -> a cursor clicks 'Follow' (springs to 'Following').

draw(cv, u) paints the end card at local time u (s) into a linear canvas; returns the canvas.
"""
import functools
import math
import os

import cv2
import numpy as np

import anim as A
import comp as C
import captions as K
import hud as U

USER = 'jawad_mp4'
Q1 = ['Kaunsi', 'yaad', 'bhulana']
Q2 = ['sabse', '*mushkil', 'hai?']
CTA2 = 'Comment mein batao'
ORANGE = np.array([1.0, 0.33, 0.02], np.float32)
HOT = np.array([1.0, 0.62, 0.22], np.float32)
PHOTO = os.path.join(C.ROOT, 'assets', 'user_photo.jpg')
CX, CY, R0 = 540, 800, 255

# timeline (local seconds)
T_RING = 0.0          # circle + ring draw on
T_EXPAND = 1.15       # circle grows to fill the frame (photo zooms out with it)
T_FULL = 2.05
T_BURN = 2.55         # light burn into the gradient
T_GRAD = 3.0
T_AVATAR = 3.0
T_USER = 3.25
T_Q = 4.05
T_CTA2 = 5.0
T_CURSOR = 5.2
T_CLICK = 6.05
END = 7.4


def _face(im8):
    """Largest frontal face (x, y, w, h) in an 8-bit BGR image, or None."""
    g = cv2.cvtColor(im8, cv2.COLOR_BGR2GRAY)
    cc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    f = cc.detectMultiScale(g, 1.1, 5, minSize=(g.shape[1] // 8, g.shape[1] // 8))
    return max(f, key=lambda b: b[2] * b[3]) if len(f) else None


def _head(im8, face):
    """Head centre x, top and bottom (photo px). The face box sits off the head when it is turned, so on a
    plain backdrop the hair + face silhouette sets the centre; otherwise the face box does."""
    fx, fy, fw, fh = face
    bottom = fy + fh * 1.08                                      # chin / beard
    hh = im8.shape[0] // 3                                       # top edge + upper sides (the body reaches the bottom)
    border = np.concatenate([im8[:20].reshape(-1, 3), im8[:hh, :20].reshape(-1, 3), im8[:hh, -20:].reshape(-1, 3)])
    if border.std(0).max() > 18:                                 # busy background: trust the face box
        return fx + fw / 2, fy - 0.45 * fh, bottom
    fg = (np.abs(im8.astype(np.int16) - np.median(border, 0)).max(2) > 28).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    if n < 2:
        return fx + fw / 2, fy - 0.45 * fh, bottom
    fg = lab == 1 + np.argmax(st[1:, 4])
    cols = fg[:, max(0, fx - fw // 4):fx + fw + fw // 4].any(1)
    top = int(np.argmax(cols[:fy + 1])) if cols[:fy + 1].any() else int(fy - 0.45 * fh)
    mids = [(xs.min() + xs.max()) / 2 for y in range(top, int(fy + fh), 4) if len(xs := np.where(fg[y])[0])]
    return (float(np.median(mids)) if mids else fx + fw / 2), top, bottom


@functools.lru_cache(maxsize=1)
def _photo():
    p = PHOTO
    if not os.path.exists(p):                     # until the creator's photo arrives: the hero portrait
        for q in (C.ROOT + '/plates3/a1_mask_full.png', C.ROOT + '/plates3/a1_mask_full_preview.png',
                  os.path.join(C.ROOT, 'assets', 'user_photo_placeholder.png')):
            if os.path.exists(q):
                p = q
                break
    im = cv2.imread(p, cv2.IMREAD_COLOR)
    im8 = im if im.dtype == np.uint8 else (im // 257).astype(np.uint8)
    im = im[..., ::-1].astype(np.float32) / (65535 if im.dtype == np.uint16 else 255)
    # drop flat border rows at the bottom (scanner/export strips)
    std = im8.reshape(im8.shape[0], -1).std(1)
    b = im8.shape[0]
    while b > im8.shape[0] * 0.8 and std[b - 1] < 8:
        b -= 1
    if b < im8.shape[0]:                          # plus the blended transition rows
        b -= 3
    im, im8 = im[:b], im8[:b]
    face = _face(im8) if p == PHOTO else None
    # cover-crop to 9:16, centred on the face when there is one
    h, w = im.shape[:2]
    tw = min(w, int(h * 9 / 16))
    th = min(h, int(w * 16 / 9))
    x0, y0 = (w - tw) // 2, max(0, (h - th) // 3)
    if face is not None:
        fx, fy, fw, fh = face
        hx, htop, hbot = _head(im8, face)
        x0 = int(np.clip(hx - tw / 2, 0, w - tw))
        y0 = int(np.clip(fy + fh / 2 - th * 0.45, 0, h - th))
    im = im[y0:y0 + th, x0:x0 + tw]
    k = C.W / tw
    im = cv2.resize(im, (C.W, C.H), interpolation=cv2.INTER_AREA)
    if face is None:
        frame = None
    else:                                         # on the canvas: head centre x, head top/bottom, face top/height
        frame = ((hx - x0) * k, (htop - y0) * k, (hbot - y0) * k, (fy - y0) * k, fh * k)
    return np.ascontiguousarray(C.to_lin(im)), frame


def photo():
    return _photo()[0]


def framing():
    """Where the photo sits inside the ring and the avatar: (ring anchor x, y, ring start zoom,
    avatar scale, avatar anchor x, y). Face-centred for the creator's photo, fixed for the placeholder."""
    f = _photo()[1]
    if f is None:
        return C.W / 2, C.H * 0.40, 1.9, 0.42, C.W / 2, C.H * 0.38
    hx, htop, hbot, top, fs = f
    z0 = float(np.clip(2 * R0 / (1.1 * fs), 0.6, 1.9))    # face + hairline fill the opening ring
    s = float(np.clip(0.92 * 240 / (hbot - htop), 0.15, 0.6))   # whole head inside the 120 px avatar
    return hx, top + 0.42 * fs, z0, s, hx, (htop + hbot) / 2


@functools.lru_cache(maxsize=1)
def _grid():
    yy, xx = np.mgrid[0:C.H // 4, 0:C.W // 4].astype(np.float32)
    return xx * 4, yy * 4


def gradient(u):
    """Liquid orange/black gradient: drifting soft blobs, computed at 1/4 res."""
    xx, yy = _grid()
    f = np.zeros_like(xx)
    blobs = [(0.10, 1.00, 0.70, 0.95, 0.11), (0.95, 0.02, 0.55, 0.70, 0.09), (0.70, 0.62, 0.30, 0.18, 0.07),
             (0.0, 0.30, 0.30, 0.25, 0.13)]
    for i, (bx, by, r, k, sp) in enumerate(blobs):
        cx = (bx + 0.10 * math.sin(u * sp * 6.28 + i * 1.7)) * C.W
        cy = (by + 0.06 * math.cos(u * sp * 6.28 * 0.8 + i)) * C.H
        f += k * np.exp(-(((xx - cx) / (r * C.W)) ** 2 + ((yy - cy) / (r * C.W * 1.3)) ** 2))
    f = np.clip(f, 0, 1.2)
    f = np.clip(f, 0, 1) ** 2.2
    col = (ORANGE[None, None] * f[..., None] * 0.85
           + HOT[None, None] * np.clip(f - 0.6, 0, 1)[..., None] * 0.7)
    col += np.float32([0.004, 0.0025, 0.002])
    return cv2.resize(col.astype(np.float32), (C.W, C.H), interpolation=cv2.INTER_CUBIC)


@functools.lru_cache(maxsize=1)
def _yx():
    yy, xx = np.mgrid[0:C.H, 0:C.W].astype(np.float32)
    return yy, xx


def circle_mask(cx, cy, r):
    yy, xx = _yx()
    return np.clip(r + 0.5 - np.hypot(xx - cx, yy - cy), 0, 1)


def ring(cv, cx, cy, r, width, sweep, k=1.0):
    """Glowing orange ring drawn from 12 o'clock clockwise over `sweep` (0..1)."""
    if sweep <= 0 or k <= 0:
        return
    pad = int(width + 60)
    x0, y0 = int(max(0, cx - r - pad)), int(max(0, cy - r - pad))
    x1, y1 = int(min(C.W, cx + r + pad)), int(min(C.H, cy + r + pad))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    rad = np.hypot(dx, dy)
    ang = (np.degrees(np.arctan2(dx, -dy)) + 360) % 360
    band = np.clip(width / 2 + 0.5 - np.abs(rad - r), 0, 1)
    a1 = 360 * sweep
    seg = np.clip((a1 - ang) * r * math.pi / 180 + 0.5, 0, 1)
    m = band * seg
    head = np.zeros_like(m)
    ha = math.radians(a1)
    hx, hy = cx + r * math.sin(ha) - x0, cy - r * math.cos(ha) - y0
    if sweep < 1:
        cv2.circle(head, (int(hx * 16), int(hy * 16)), int(width * 1.6 * 16), 1.0, -1, cv2.LINE_AA, shift=4)
    grad = (ang / 360)[..., None]
    col = ORANGE * (1 - grad) + HOT * grad
    glow = cv2.GaussianBlur(m, (0, 0), 10) * 1.4 + cv2.GaussianBlur(head, (0, 0), 14) * 2.5
    reg = cv[y0:y1, x0:x1]
    reg[..., :3] = reg[..., :3] * (1 - m[..., None] * k) + col * m[..., None] * 1.6 * k
    reg[..., :3] += (glow[..., None] * ORANGE + head[..., None] * 1.5) * k


@functools.lru_cache(maxsize=64)
def text_sprite(txt, name, px, color, track=0.0):
    m, base = U.text_mask(txt, name, px, track)
    m = cv2.resize(m, (m.shape[1] // U.SS, m.shape[0] // U.SS), interpolation=cv2.INTER_AREA)
    col = C.to_lin(np.float32(color))
    sh = np.clip(cv2.GaussianBlur(np.roll(m, 3, axis=0), (0, 0), 6) * 0.7, 0, 0.8)
    rgb = col * m[..., None]
    a = m + sh * (1 - m)
    return np.dstack([rgb, a]).astype(np.float32), base // U.SS


def place(cv, spr, x, y, op=1.0, scale=1.0, blur=0.0, clip_y=None):
    """Draw sprite with its left-baseline at (x, y). clip_y: hide everything below this line (mask reveal)."""
    s = spr
    if blur >= 1:
        p = int(blur)
        s = C.disc_blur(cv2.copyMakeBorder(spr, p, p, p, p, cv2.BORDER_CONSTANT, value=0), blur)
        x, y = x - p * scale, y - p * scale
    if scale != 1:
        s = cv2.resize(s, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = s.shape[:2]
    X, Y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, X), max(0, Y), min(C.W, X + w), min(C.H, Y + h)
    if clip_y is not None:
        y1 = min(y1, int(clip_y))
    if x1 <= x0 or y1 <= y0:
        return
    src = s[y0 - Y:y1 - Y, x0 - X:x1 - X] * op
    reg = cv[y0:y1, x0:x1]
    reg[..., :3] = src[..., :3] + reg[..., :3] * (1 - src[..., 3:4])


def username(cv, u):
    """'@' + letters rise out of a mask line one by one, blur-to-sharp; underline sweeps."""
    px = 92
    name = '@' + USER
    widths = [U._font('InterTight-800', px * U.SS).getlength(c) / U.SS for c in name]
    total = sum(widths) + 2 * (len(name) - 1)
    x = C.W / 2 - total / 2
    base_y = 905
    for i, (ch, w) in enumerate(zip(name, widths)):
        lu = u - T_USER - i * 0.045
        if lu > 0:
            p = A.EXPO_OUT(A.clamp(lu / 0.7))
            spr, b = text_sprite(ch, 'InterTight-800', px, tuple(HOT) if ch == '@' else (0.98, 0.97, 0.96))
            yoff = (1 - p) * 70
            place(cv, spr, x, base_y - b + yoff, op=A.ramp(lu, 0, 0.25), blur=(1 - p) * 8, clip_y=base_y + 22)
        x += w + 2
    lu = u - T_USER - 0.35
    if lu > 0:                                         # underline sweep
        p = A.EXPO_OUT(A.clamp(lu / 0.9))
        x0 = C.W / 2 - total / 2
        y = base_y + 34
        x1 = x0 + total * p
        m = np.zeros((40, C.W), np.float32)
        cv2.line(m, (int(x0 * 16), 20 * 16), (int(x1 * 16), 20 * 16), 1.0, 4, cv2.LINE_AA, shift=4)
        g = cv2.GaussianBlur(m, (0, 0), 6)
        cv[y - 20:y + 20, :, :3] += m[..., None] * C.to_lin(HOT) * 1.4 + g[..., None] * ORANGE * 1.5


def question(cv, u):
    """CTA question in white + orange keyword, each word gliding up with a focus pull."""
    rows = [(Q1, 1040), (Q2, 1145)]
    k = 0
    for words, y in rows:
        sprs = []
        for w in words:
            key = w.startswith('*')
            txt = w.lstrip('*')
            if key:
                spr, b = text_sprite(txt, 'GwynerCondensed-Italic', 112, tuple(HOT))
            else:
                spr, b = text_sprite(txt, 'Poppins-600', 64, (0.97, 0.96, 0.95))
            sprs.append((spr, b))
        gap = 6
        total = sum(s.shape[1] for s, _ in sprs) + gap * (len(sprs) - 1)
        x = C.W / 2 - total / 2
        for spr, b in sprs:
            lu = u - T_Q - k * 0.16
            if lu > 0:
                p = A.EXPO_OUT(A.clamp(lu / 0.85))
                place(cv, spr, x, y - b + (1 - p) * 46, op=A.ramp(lu, 0, 0.35), blur=(1 - p) * 10)
            x += spr.shape[1] + gap
            k += 1
    lu = u - T_CTA2
    if lu > 0:
        p = A.EXPO_OUT(A.clamp(lu / 0.8))
        spr, b = text_sprite(CTA2 + '  ↓', 'Inter-600', 38, (0.85, 0.83, 0.82), track=0.04)
        place(cv, spr, C.W / 2 - spr.shape[1] / 2, 1240 - b + (1 - p) * 30, op=A.ramp(lu, 0, 0.4) * 0.9)


@functools.lru_cache(maxsize=64)
def follow_button(state):
    """state 0..1: 0 = Follow (orange), 1 = Following (glass)."""
    p = U.Paint(320, 96, pad=40)
    m = p.rrect(0, 0, 320, 96, 48, ORANGE * (1 - state) + np.float32([0.10, 0.10, 0.11]) * state, 1.0)
    p.glow(m, ORANGE, 14, 0.9 * (1 - state))
    p.stroke(0, 0, 320, 96, 48, 1.4, U.WHITE, 0.25 + 0.3 * state)
    if state < 0.5:
        p.text('Follow', 160, 62, 'Inter-700', 36, U.WHITE, 1 - state * 2, anchor='c')
    else:
        p.text('Following ✓', 160, 62, 'Inter-700', 34, U.WHITE, state * 2 - 1, anchor='c')
    return p.result()


def follow(cv, u):
    lu = u - T_CURSOR + 0.25
    if lu <= 0:
        return
    press = A.clamp(1 - abs(u - T_CLICK) / 0.12) if abs(u - T_CLICK) < 0.12 else 0.0
    state = A.spring(u - T_CLICK, 2.4, 0.55) if u > T_CLICK else 0.0
    s = A.EXPO_OUT(A.clamp(lu / 0.7))
    img = follow_button(round(A.clamp(state) * 16) / 16)
    k = 1.18 * (0.7 + 0.3 * s) * (1 - 0.05 * press) * (1 + 0.04 * max(0.0, math.sin(min(1.0, max(0.0, u - T_CLICK) * 3) * math.pi)))
    img2 = cv2.resize(img, None, fx=k / U.SS, fy=k / U.SS, interpolation=cv2.INTER_AREA)
    h, w = img2.shape[:2]
    place_rgba(cv, img2, C.W / 2 - w / 2, 1360 - h / 2 + (1 - s) * 30, A.ramp(lu, 0, 0.3))
    # cursor glides in on a curved path, hesitates, clicks
    if u > T_CURSOR:
        cu = u - T_CURSOR
        P0, P1, P2, P3 = np.float32([860, 1400]), np.float32([900, 1330]), np.float32([700, 1300]), np.float32([590, 1372])
        q = A.SMOOTH(A.clamp(cu / (T_CLICK - T_CURSOR - 0.05)))
        pos = (1 - q) ** 3 * P0 + 3 * (1 - q) ** 2 * q * P1 + 3 * (1 - q) * q ** 2 * P2 + q ** 3 * P3
        cs = U.cursor()
        cs = cv2.resize(cs, None, fx=(0.9 - 0.08 * press) / U.SS, fy=(0.9 - 0.08 * press) / U.SS,
                        interpolation=cv2.INTER_AREA)
        place_rgba(cv, cs, pos[0] - 9, pos[1] - 9, A.ramp(cu, 0, 0.25) * (1 - A.ramp(u, T_CLICK + 0.5, T_CLICK + 0.8)))
        if u > T_CLICK:                                   # click ripple
            ru = u - T_CLICK
            if ru < 0.6:
                rr = 16 + 52 * A.EXPO_OUT(ru / 0.6)
                ring(cv, P3[0], P3[1], rr, 3, 1.0, k=(1 - ru / 0.6) * 0.8)


def place_rgba(cv, img, x, y, op=1.0):
    h, w = img.shape[:2]
    X, Y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, X), max(0, Y), min(C.W, X + w), min(C.H, Y + h)
    if x1 <= x0 or y1 <= y0 or op <= 0:
        return
    src = img[y0 - Y:y1 - Y, x0 - X:x1 - X] * op
    reg = cv[y0:y1, x0:x1]
    reg[..., :3] = src[..., :3] + reg[..., :3] * (1 - src[..., 3:4])


def draw(cv, u, prev=None):
    """prev: canvas of the outgoing story shot (linear) for the opening iris."""
    ph = photo()
    ax, ay0, z0, av_s, avx, avy = framing()
    # ---------------- background: previous shot darkening -> black / gradient
    grad = gradient(u)
    if prev is not None and u < T_EXPAND:
        k = A.ramp(u, 0, 0.6, A.SMOOTH)
        bg = prev * (1 - k * 0.92) + grad * 0.25 * k
    elif u < T_BURN:
        bg = grad * 0.25
    else:
        bg = grad * (0.25 + 0.75 * A.ramp(u, T_BURN, T_GRAD + 0.4, A.SMOOTH))
    cv[..., :3] = bg
    # ---------------- photo circle -> fill
    if u < T_GRAD + 0.2:
        ue = A.ramp(u, T_EXPAND, T_FULL, A.EXPO)                       # graph-editor S curve
        r_open = R0 * A.spring(u - T_RING, 1.6, 0.62)
        R_full = math.hypot(C.W, C.H) / 2 + 30
        r = r_open + (R_full - R0) * ue
        cx = CX + (C.W / 2 - CX) * ue
        cy = CY + (C.H / 2 - CY) * ue
        # photo inside the circle: framed on the face, settles to full frame as the circle opens
        z = z0 + (1 - z0) * ue + 0.06 * (1 - A.ramp(u, 0, T_FULL, A.LINEAR)) - 0.04 * A.ramp(u, T_FULL, T_BURN + 0.6, A.LINEAR)
        M = np.float32([[z, 0, 0], [0, z, 0]])
        M[0, 2] = cx - z * (ax * (1 - ue) + C.W * 0.5 * ue)
        M[1, 2] = cy - z * (ay0 * (1 - ue) + C.H * 0.5 * ue)
        warped = cv2.warpAffine(ph, M, (C.W, C.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
        m = circle_mask(cx, cy, max(r, 0))[..., None]
        burn = A.ramp(u, T_BURN, T_GRAD + 0.15, A.SMOOTH)
        cv[..., :3] = warped * m * (1 - burn) + cv[..., :3] * (1 - m * (1 - burn))
        ring(cv, cx, cy, r + 4, 6, A.ramp(u, 0.1, 1.0, A.SMOOTH), k=1 - A.ramp(u, T_EXPAND, T_EXPAND + 0.5))
        if T_BURN - 0.2 < u < T_GRAD + 0.5:                  # light burn: orange flash blooming from an edge
            bu = (u - (T_BURN - 0.2)) / (T_GRAD + 0.7 - T_BURN)
            yy, xx = _yx()
            f = np.exp(-((xx - C.W * (1.1 - bu)) ** 2 / (2 * (C.W * 0.5) ** 2) + (yy - C.H * 0.3) ** 2 / (2 * (C.H * 0.6) ** 2)))
            cv[..., :3] += f[..., None] * (ORANGE * 1.1 + HOT * 0.25) * math.sin(math.pi * A.clamp(bu)) ** 1.5
    # ---------------- profile card
    if u > T_AVATAR:
        au = u - T_AVATAR
        s = A.spring(au, 1.9, 0.6)
        r = 120 * s
        if r > 1:
            ay = 640
            small = cv2.resize(ph, (int(C.W * av_s), int(C.H * av_s)), interpolation=cv2.INTER_AREA)
            M = np.float32([[1, 0, C.W / 2 - avx * av_s], [0, 1, ay - avy * av_s]])
            warped = cv2.warpAffine(small, M, (C.W, C.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            m = circle_mask(C.W / 2, ay, r)[..., None]
            cv[..., :3] = warped * m + cv[..., :3] * (1 - m)
            ring(cv, C.W / 2, ay, r + 7, 4, A.ramp(au, 0.05, 0.9, A.SMOOTH))
    username(cv, u)
    question(cv, u)
    follow(cv, u)
    return cv
