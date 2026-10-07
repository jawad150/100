"""End card, clean and minimal (same language as the Higgsfield Genjutsu reel): the last shot zooms out
into a glowing orange ring, the creator's photo fades in, the ring glides into a dark capsule badge
(@jawad_mp4 + one line), a bold Unbounded headline asks the question and a single orange pill asks for
the comment. Black stage with soft orange light rays (~70 % black / 30 % orange).

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
T_RING = 0.0          # last shot zooms out into the ring
T_EXPAND = 0.95       # photo fully in, ring pulse
T_FULL = 0.95
T_BURN = 1.35         # ring glides to the badge
T_GRAD = 1.55         # badge body grows out of the ring
T_AVATAR = 1.55
T_USER = 1.85
T_SUB = 2.05
T_Q = 2.55            # headline
T_CTA2 = 3.35         # comment pill
T_CURSOR = 4.4
T_CLICK = 4.75        # pill 'tap' pulse
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



# ---------------------------------------------------------------- layout (Instagram safe area 70..950 x 250..1470)
RING_C = (540, 840, 128)               # ring centre + radius after the zoom-out
BADGE = (130, 950, 900, 220)           # x0, x1, centre y, height  (capsule)
AV_R = 90
BX = BADGE[0] + 20 + AV_R              # avatar centre x inside the badge
Y_HEAD = (455, 560, 680)
Y_CTA = 1140
SUBLINE = 'Follow for more cinematic stories'
HEADLINE = (('KAUNSI YAAD', 78, False), ('BHULANA SABSE', 78, False), ('MUSHKIL HAI?', 96, True))   # (text, px, orange)
AVATAR_FALLBACK = os.path.join(C.ROOT, 'assets', 'avatar_from_genjutsu.png')


@functools.lru_cache(maxsize=1)
def avatar():
    """Square linear RGB avatar: the creator's photo (face-framed) if present, else the Genjutsu-reel avatar."""
    if os.path.exists(PHOTO):
        ph, frame = _photo()
        _, _, _, av_s, avx, avy = framing()
        side = int(240 / max(av_s, 1e-3))
        x0, y0 = int(avx - side / 2), int(avy - side / 2)
        sub = cv2.copyMakeBorder(ph, side, side, side, side, cv2.BORDER_REFLECT101)[y0 + side:y0 + 2 * side, x0 + side:x0 + 2 * side]
        return cv2.resize(sub, (512, 512), interpolation=cv2.INTER_AREA)
    im = cv2.imread(AVATAR_FALLBACK)
    if im is None:
        im = (np.ones((512, 512, 3)) * 40).astype(np.uint8)
    im = im[..., ::-1].astype(np.float32) / 255
    return np.ascontiguousarray(C.to_lin(cv2.resize(im, (512, 512), interpolation=cv2.INTER_AREA)))


@functools.lru_cache(maxsize=1)
def _polar():
    yy, xx = np.mgrid[0:C.H // 4, 0:C.W // 4].astype(np.float32)
    dx, dy = xx * 4 - 540, yy * 4 - 900
    return np.arctan2(dy, dx), np.hypot(dx, dy)


def stage(u):
    """Black stage, soft orange centre glow + slowly turning light rays (1/4 res)."""
    ang, rad = _polar()
    glow = np.exp(-(rad / 430.0) ** 2) * 0.24 + np.exp(-(rad / 950.0) ** 2) * 0.04
    rays = 0.0
    for k, (n, sp, a) in enumerate(((9, 0.05, 1.0), (14, -0.035, 0.6), (5, 0.02, 0.5))):
        rays = rays + a * np.clip(np.sin(ang * n + u * sp * 6.28 + k), 0, 1) ** 12
    rays = rays * np.exp(-(rad / 820.0) ** 1.5) * np.clip(rad / 160.0, 0, 1) * 0.16
    f = glow + rays
    col = f[..., None] * ORANGE[None, None] * 0.55 + np.float32([0.004, 0.0032, 0.003])
    return cv2.resize(col.astype(np.float32), (C.W, C.H), interpolation=cv2.INTER_CUBIC)


@functools.lru_cache(maxsize=16)
def headline_sprite(txt, px, grad):
    """Unbounded-900 line, white or orange-gradient with a warm glow (premultiplied linear)."""
    m, base = U.text_mask(txt, 'Unbounded-900', px, 0.02)
    m = cv2.resize(m, (m.shape[1] // U.SS, m.shape[0] // U.SS), interpolation=cv2.INTER_AREA)
    pad = 30
    m = cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    h = m.shape[0]
    if grad:
        v = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        col = C.to_lin(np.float32([1.0, 0.70, 0.28])) * (1 - v) + C.to_lin(np.float32([1.0, 0.30, 0.0])) * v
        glow = cv2.GaussianBlur(m, (0, 0), 14)[..., None] * ORANGE * 0.55
    else:
        col = np.ones((1, 1, 3), np.float32)
        glow = cv2.GaussianBlur(m, (0, 0), 14)[..., None] * np.float32([0.25, 0.2, 0.18]) * 0.3
    sh = np.clip(cv2.GaussianBlur(np.roll(m, 4, axis=0), (0, 0), 7) * 0.7, 0, 0.8)
    rgb = col * m[..., None] + glow * (1 - m[..., None])
    a = np.clip(m + sh * (1 - m) + glow.max(2) * 0.4, 0, 1)
    return np.dstack([rgb, a]).astype(np.float32), base // U.SS + pad


def fit_px(txt, px, max_w=860):
    w = U._font('Unbounded-900', px * U.SS).getlength(txt) / U.SS
    return int(px * min(1.0, max_w / max(w, 1)))


@functools.lru_cache(maxsize=1)
def chat_icon(size=44):
    p = U.Paint(size, size, pad=4)
    p.rrect(0, 2, size, size * 0.72, size * 0.2, U.WHITE, 1.0)
    p.line([(size * 0.25, size * 0.68), (size * 0.2, size * 0.95), (size * 0.48, size * 0.72)], 3, U.WHITE, 1.0)
    for k in range(3):
        p.circle(size * (0.3 + 0.2 * k), size * 0.38, size * 0.055, ORANGE, 1.0)
    return p.result()


@functools.lru_cache(maxsize=1)
def cta_pill():
    """Orange gradient pill 'COMMENT YOUR ANSWER' with chat icon."""
    w, h = 640, 104
    p = U.Paint(w, h, pad=40)
    grad = np.clip((p._xx - p.X(0)) / (w * U.SS), 0, 1)[..., None]
    col = HOT * (1 - grad) + ORANGE * grad
    m = np.clip(0.5 - p.sdf_rrect(0, 0, w, h, h / 2), 0, 1)
    p.rgb = col * m[..., None] + p.rgb * (1 - m[..., None])
    p.a = m + p.a * (1 - m)
    p.stroke(0, 0, w, h, h / 2, 1.6, np.float32([1.0, 0.85, 0.7]), 0.55)
    ic = chat_icon()
    ic_m = ic[..., 3]
    y0, x0 = int(p.X(h / 2 - 22) - 8), int(p.X(48))
    reg = p.rgb[y0:y0 + ic.shape[0], x0:x0 + ic.shape[1]]
    reg[...] = C.to_srgb(ic[..., :3]) + reg * (1 - ic_m[..., None])
    p.a[y0:y0 + ic.shape[0], x0:x0 + ic.shape[1]] = np.maximum(p.a[y0:y0 + ic.shape[0], x0:x0 + ic.shape[1]], ic_m)
    p.text('COMMENT YOUR ANSWER', w / 2 + 30, 66, 'Inter-900', 34, U.WHITE, 1.0, anchor='c', track=0.05)
    return p.result()


def pill_draw(cv, img, cx, cy, scale, op, sheen=None):
    img2 = cv2.resize(img, None, fx=scale / U.SS, fy=scale / U.SS, interpolation=cv2.INTER_AREA)
    if sheen is not None and 0 < sheen < 1:
        h, w = img2.shape[:2]
        xx = np.arange(w, dtype=np.float32)[None, :]
        yy = np.arange(h, dtype=np.float32)[:, None]
        band = np.exp(-(((xx - w * (sheen * 1.4 - 0.2)) + (yy - h / 2) * 0.6) / (w * 0.06)) ** 2)
        img2 = img2.copy()
        img2[..., :3] += band[..., None] * img2[..., 3:4] * 0.55
    place_rgba(cv, img2, cx - img2.shape[1] / 2, cy - img2.shape[0] / 2, op)


def badge_body(cv, w, cy, h, op):
    """Dark capsule growing to the right from the avatar ring."""
    x0 = BADGE[0]
    x1 = x0 + w
    pad = 50
    X0, Y0, X1, Y1 = int(x0 - pad), int(cy - h / 2 - pad), int(x1 + pad), int(cy + h / 2 + pad)
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
    r = h / 2
    qx = np.abs(xx - (x0 + x1) / 2) - (w / 2 - r)
    qy = np.abs(yy - cy) - (h / 2 - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    fill = np.clip(0.5 - d, 0, 1)
    stroke = np.clip(1.0 - np.abs(d + 1.0), 0, 1)
    glow = np.exp(-np.clip(d, 0, None) / 18.0) * (d > 0)
    reg = cv[Y0:Y1, X0:X1]
    reg[..., :3] += (glow[..., None] * ORANGE * 0.18) * op
    body = C.to_lin(np.float32([0.07, 0.06, 0.055]))
    a = fill[..., None] * 0.92 * op
    reg[..., :3] = reg[..., :3] * (1 - a) + body * a
    reg[..., :3] += stroke[..., None] * C.to_lin(np.float32([1.0, 0.55, 0.2])) * 0.55 * op


def disc_image(cv, img, cx, cy, r, op=1.0):
    ri = int(max(4, r))
    X0, Y0, X1, Y1 = max(0, int(cx - ri)), max(0, int(cy - ri)), min(C.W, int(cx + ri)), min(C.H, int(cy + ri))
    if X1 <= X0 or Y1 <= Y0:
        return
    sub = cv2.resize(img, (2 * ri, 2 * ri), interpolation=cv2.INTER_AREA)
    sub = sub[Y0 - int(cy - ri):Y1 - int(cy - ri), X0 - int(cx - ri):X1 - int(cx - ri)]
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
    m = (np.clip(r - np.hypot(xx - cx, yy - cy), 0, 1) * op)[..., None]
    reg = cv[Y0:Y1, X0:X1]
    reg[..., :3] = reg[..., :3] * (1 - m) + sub[:reg.shape[0], :reg.shape[1]] * m


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
    """prev: canvas of the outgoing story shot (linear) - it zooms out into the ring."""
    bg = stage(u)
    k_in = A.ramp(u, 0.0, 0.7, A.SMOOTH)
    cv[..., :3] = bg * k_in
    cx0, cy0, r0 = RING_C
    R_full = math.hypot(C.W, C.H) / 2 + 40
    # ---------------- zoom-out of the last shot into the ring, photo fades in
    z = A.ramp(u, 0.0, 0.85, A.EXPO)
    r = R_full + (r0 - R_full) * z
    cx, cy = C.W / 2 + (cx0 - C.W / 2) * z, C.H / 2 + (cy0 - C.H / 2) * z
    # glide to the badge
    g = A.ramp(u, T_BURN, T_BURN + 0.6, A.SMOOTH)
    cx, cy, r = cx + (BX - cx) * g, cy + (BADGE[2] - cy) * g, r + (AV_R - r) * g
    if g > 0:
        w = 2 * AV_R + 40 + (BADGE[1] - BADGE[0] - 2 * AV_R - 40) * A.ramp(u, T_GRAD - 0.15, T_GRAD + 0.5, A.EXPO)
        badge_body(cv, w, BADGE[2], BADGE[3], A.ramp(u, T_GRAD - 0.2, T_GRAD + 0.1))
    if prev is not None and u < 1.0:
        sc = r / R_full * 1.05
        tmp = cv2.warpAffine(prev, np.float32([[sc, 0, cx - sc * C.W / 2], [0, sc, cy - sc * C.H / 2]]), (C.W, C.H),
                             flags=cv2.INTER_AREA if sc < 0.9 else cv2.INTER_LINEAR)
        m = circle_mask(cx, cy, r)[..., None] * (1 - A.ramp(u, 0.55, 0.95))
        cv[..., :3] = tmp * m + cv[..., :3] * (1 - m)
    disc_image(cv, avatar(), cx, cy, r, A.ramp(u, 0.5, 0.95, A.SMOOTH))
    ring(cv, cx, cy, r + 5, 5, A.ramp(u, 0.15, 0.95, A.SMOOTH), k=0.9)
    if u > T_EXPAND:
        pu = ((u - T_EXPAND) * 0.7) % 1.0
        ring(cv, cx, cy, r + 8 + 60 * pu, 2, 1.0, k=0.45 * (1 - pu))
    # ---------------- name + subline
    tx = BX + AV_R + 34
    lu = u - T_USER
    if lu > 0:
        p = A.EXPO_OUT(A.clamp(lu / 0.7))
        spr, b = text_sprite('@' + USER, 'Unbounded-800', 50, (1.0, 1.0, 1.0))
        place(cv, spr, tx + (1 - p) * 40, BADGE[2] - 6 - b, op=A.ramp(lu, 0, 0.3))
    lu = u - T_SUB
    if lu > 0:
        p = A.EXPO_OUT(A.clamp(lu / 0.7))
        spr, b = text_sprite(SUBLINE, 'Inter-600', 28, (0.72, 0.69, 0.65))
        place(cv, spr, tx + (1 - p) * 40, BADGE[2] + 44 - b, op=A.ramp(lu, 0, 0.35))
    # ---------------- headline (question)
    for i, ((txt, px, grad), y) in enumerate(zip(HEADLINE, Y_HEAD)):
        lu = u - T_Q - i * 0.14
        if lu > 0:
            p = A.EXPO_OUT(A.clamp(lu / 0.8))
            spr, b = headline_sprite(txt, fit_px(txt, px), grad)
            place(cv, spr, C.W / 2 - spr.shape[1] / 2, y - b + (1 - p) * 50, op=A.ramp(lu, 0, 0.35), blur=(1 - p) * 10)
    # ---------------- comment pill: pop, glow pulse, sheen, tap
    lu = u - T_CTA2
    if lu > 0:
        s = A.spring(lu, 2.2, 0.5)
        tap = 1 - 0.06 * math.exp(-((u - T_CLICK) / 0.06) ** 2)
        breathe = 1 + 0.025 * math.sin(u * 5)
        yy = Y_CTA + (1 - min(s, 1)) * 30
        glow_k = (0.55 + 0.25 * math.sin(u * 5)) * A.ramp(lu, 0, 0.3)
        gy0, gy1 = int(yy - 110), int(yy + 110)
        g2 = np.exp(-((np.arange(gy0, gy1, dtype=np.float32)[:, None] - yy) / 46.0) ** 2) * \
            np.exp(-((np.arange(C.W, dtype=np.float32)[None, :] - 540) / 300.0) ** 2)
        cv[gy0:gy1, :, :3] += g2[..., None] * ORANGE * 0.5 * glow_k
        ph = ((u - T_CTA2 - 0.5) % 1.8) / 1.2
        pill_draw(cv, cta_pill(), 540, yy, max(0.01, s) * breathe * tap, A.ramp(lu, 0, 0.25), sheen=ph)
        if u > T_CLICK:
            ru = u - T_CLICK
            if ru < 0.7:
                rr = 60 + 260 * A.EXPO_OUT(ru / 0.7)
                ring(cv, 540, yy, rr, 2.5, 1.0, k=(1 - ru / 0.7) * 0.6)
    return cv
