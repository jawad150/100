"""End card (SaaS / liquid-glass style): the creator's photo in a glowing orange ring -> the circle
expands until the photo fills the frame -> the photo morphs down into the avatar of a liquid-glass
profile card floating over a 70 % black / 30 % orange liquid gradient -> '@jawad_mp4' rises letter by
letter -> comment-bait question -> a cursor clicks 'Follow' (springs to 'Following').

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
T_BURN = 2.45         # photo morphs into the card avatar
T_GRAD = 2.75         # glass card springs in
T_AVATAR = 3.2
T_USER = 3.3
T_SUB = 3.75
T_Q = 4.1
T_CTA2 = 4.9
T_CURSOR = 5.25
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


# ---------------------------------------------------------------- layout (Instagram safe area 70..950 x 250..1470)
CARD = (130, 360, 950, 1440)          # x0, y0, x1, y1
CARD_R = 58
AV = (540, 535, 108)                  # avatar centre + radius
Y_USER, Y_SUB, Y_DIV, Y_Q1, Y_Q2, Y_PILL, Y_BTN = 760, 818, 868, 968, 1078, 1170, 1318
SUB = 'Cinematic edits  \u2022  Blender  \u2022  Motion'


@functools.lru_cache(maxsize=1)
def _grid():
    yy, xx = np.mgrid[0:C.H // 4, 0:C.W // 4].astype(np.float32)
    return xx * 4, yy * 4


def gradient(u):
    """Liquid gradient, ~70 % near-black / ~30 % orange: a big orange flow from the lower left, a smaller
    one from the upper right and a slow diagonal light streak (1/4 res, upsampled)."""
    xx, yy = _grid()
    f = np.zeros_like(xx)
    blobs = [(0.02, 0.98, 0.62, 1.0, 0.07), (1.02, 0.08, 0.42, 0.75, 0.05), (0.25, 0.62, 0.22, 0.25, 0.09)]
    for i, (bx, by, r, k, sp) in enumerate(blobs):
        cx = (bx + 0.08 * math.sin(u * sp * 6.28 + i * 1.7)) * C.W
        cy = (by + 0.05 * math.cos(u * sp * 6.28 * 0.8 + i)) * C.H
        f += k * np.exp(-(((xx - cx) / (r * C.W)) ** 2 + ((yy - cy) / (r * C.W * 1.35)) ** 2))
    # diagonal streak
    d = (xx * 0.55 + yy * 0.83 - (C.W * 0.55 + C.H * 0.83) * (0.35 + 0.08 * math.sin(u * 0.4)))
    f += 0.18 * np.exp(-(d / 70.0) ** 2)
    f = np.clip(f, 0, 1.2)
    f = np.clip(f - 0.18, 0, 1) / 0.82
    f = f ** 1.7
    col = ORANGE[None, None] * f[..., None] * 0.95 + HOT[None, None] * np.clip(f - 0.55, 0, 1)[..., None] * 0.6
    col += np.float32([0.0035, 0.0025, 0.0022])
    return cv2.resize(col.astype(np.float32), (C.W, C.H), interpolation=cv2.INTER_CUBIC)


@functools.lru_cache(maxsize=1)
def _card_geom():
    """Static SDF of the card + inward refraction displacement (thick glass bending the light at the rim)."""
    yy, xx = np.mgrid[0:C.H, 0:C.W].astype(np.float32)
    x0, y0, x1, y1 = CARD
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    qx = np.abs(xx - cx) - (hw - CARD_R)
    qy = np.abs(yy - cy) - (hh - CARD_R)
    sdf = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - CARD_R
    gy, gx = np.gradient(sdf)
    n = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    band = np.clip(1 + sdf / 70.0, 0, 1) ** 2.2 * (sdf < 0)           # 1 at the rim -> 0, 70 px inside
    mx = xx + gx / n * band * 46
    my = yy + gy / n * band * 46
    mask = np.clip(0.5 - sdf, 0, 1)
    rim = np.clip(1.6 - np.abs(sdf + 1.2), 0, 1)
    inner = np.exp(-((sdf + 10) / 9.0) ** 2) * (sdf < 0)
    top = np.clip(1 - (yy - y0) / 260.0, 0, 1) ** 2 * mask
    diag = np.clip(((xx - x0) / (x1 - x0) + (yy - y0) / (y1 - y0)) / 2, 0, 1)   # 0 top-left -> 1 bottom-right
    shadow = cv2.GaussianBlur(np.roll(mask, 34, axis=0), (0, 0), 42)
    return dict(sdf=sdf, mx=mx.astype(np.float32), my=my.astype(np.float32), mask=mask, rim=rim, inner=inner,
                top=top, diag=diag, shadow=shadow, xx=xx, yy=yy)


def glass(bg, u, sweep_t):
    """Liquid-glass card over bg (linear): frosted + refracted backdrop, specular rim, inner glow, light sweep."""
    g = _card_geom()
    small = cv2.resize(bg, (C.W // 4, C.H // 4), interpolation=cv2.INTER_AREA)
    frost = cv2.resize(cv2.GaussianBlur(small, (0, 0), 7), (C.W, C.H), interpolation=cv2.INTER_LINEAR)
    refr = cv2.remap(frost, g['mx'], g['my'], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    body = refr * 1.35 + np.float32([0.020, 0.018, 0.018])              # brighten + milky tint
    rim_col = (1 - g['diag'])[..., None] * 0.55 + 0.12
    body = body + g['rim'][..., None] * rim_col * np.float32([1.0, 0.97, 0.94])
    body = body + g['inner'][..., None] * 0.05 + g['top'][..., None] * 0.045
    # moving specular sweep
    sx = (sweep_t % 3.2) / 3.2 * 2.4 - 0.7
    d = (g['xx'] - CARD[0]) / (CARD[2] - CARD[0]) * 0.8 + (g['yy'] - CARD[1]) / (CARD[3] - CARD[1]) * 0.6 - sx
    body = body + (np.exp(-(d / 0.05) ** 2) * 0.10)[..., None] * g['mask'][..., None]
    return body, g


def text_layer(u, click_state):
    """All card content as one premultiplied linear RGBA layer (cached per discrete animation state)."""
    out = np.zeros((C.H, C.W, 4), np.float32)
    # username: rises out of a mask line, letter stagger, blur-to-sharp
    name = '@' + USER
    px = 86
    widths = [U._font('InterTight-800', px * U.SS).getlength(ch) / U.SS for ch in name]
    total = sum(widths) + 3 * (len(name) - 1)
    x = C.W / 2 - total / 2
    for i, (ch, w) in enumerate(zip(name, widths)):
        lu = u - T_USER - i * 0.04
        if lu > 0:
            p = A.EXPO_OUT(A.clamp(lu / 0.7))
            spr, b = text_sprite(ch, 'InterTight-800', px, tuple(HOT) if ch == '@' else (1.0, 1.0, 1.0))
            place(out, spr, x, Y_USER - b + (1 - p) * 60, op=A.ramp(lu, 0, 0.25), blur=(1 - p) * 8,
                  clip_y=Y_USER + 24)
        x += w + 3
    lu = u - T_SUB
    if lu > 0:
        p = A.EXPO_OUT(A.clamp(lu / 0.7))
        spr, b = text_sprite(SUB, 'Inter-600', 33, (0.93, 0.92, 0.91), track=0.02)
        place(out, spr, C.W / 2 - spr.shape[1] / 2, Y_SUB - b + (1 - p) * 24, op=A.ramp(lu, 0, 0.4) * 0.92)
        # divider sweeps out from the centre
        k = A.EXPO_OUT(A.clamp((lu - 0.1) / 0.8))
        hw = 300 * k
        m = np.zeros((10, C.W), np.float32)
        cv2.line(m, (int((C.W / 2 - hw) * 16), 5 * 16), (int((C.W / 2 + hw) * 16), 5 * 16), 1.0, 2, cv2.LINE_AA, shift=4)
        out[Y_DIV - 5:Y_DIV + 5, :, :3] += m[..., None] * np.float32([0.35, 0.33, 0.32])
        out[Y_DIV - 5:Y_DIV + 5, :, 3] = np.maximum(out[Y_DIV - 5:Y_DIV + 5, :, 3], m * 0.5)
    # question
    k = 0
    for words, y in ((Q1, Y_Q1), (Q2, Y_Q2)):
        sprs = []
        for wd in words:
            key = wd.startswith('*')
            txt = wd.lstrip('*')
            sprs.append(text_sprite(txt, 'GwynerCondensed-Italic', 112, tuple(HOT)) if key else
                        text_sprite(txt, 'Poppins-700', 60, (1.0, 1.0, 1.0)))
        gap = 14
        tot = sum(sp.shape[1] for sp, _ in sprs) + gap * (len(sprs) - 1)
        xx = C.W / 2 - tot / 2
        for sp, b in sprs:
            lu = u - T_Q - k * 0.12
            if lu > 0:
                p = A.EXPO_OUT(A.clamp(lu / 0.8))
                place(out, sp, xx, y - b + (1 - p) * 40, op=A.ramp(lu, 0, 0.35), blur=(1 - p) * 9)
            xx += sp.shape[1] + gap
            k += 1
    # comment pill
    lu = u - T_CTA2
    if lu > 0:
        s = A.spring(lu, 2.0, 0.6)
        img = comment_pill()
        img = cv2.resize(img, None, fx=(0.85 + 0.15 * s) / U.SS, fy=(0.85 + 0.15 * s) / U.SS, interpolation=cv2.INTER_AREA)
        place_rgba(out, img, C.W / 2 - img.shape[1] / 2, Y_PILL - img.shape[0] / 2, A.ramp(lu, 0, 0.3))
    # follow button
    lu = u - (T_CURSOR - 0.2)
    if lu > 0:
        s = A.spring(lu, 2.0, 0.55)
        press = A.clamp(1 - abs(u - T_CLICK) / 0.1) if abs(u - T_CLICK) < 0.1 else 0.0
        img = follow_button(click_state)
        k2 = (0.8 + 0.2 * s) * (1 - 0.05 * press) / U.SS
        img = cv2.resize(img, None, fx=k2, fy=k2, interpolation=cv2.INTER_AREA)
        place_rgba(out, img, C.W / 2 - img.shape[1] / 2, Y_BTN - img.shape[0] / 2, A.ramp(lu, 0, 0.3))
    return out


@functools.lru_cache(maxsize=1)
def comment_pill():
    w, h = 600, 92
    p = U.Paint(w, h, pad=30)
    p.rrect(0, 0, w, h, 46, U.WHITE, 0.14)
    p.stroke(0, 0, w, h, 46, 1.5, U.WHITE, 0.55)
    # speech bubble icon
    p.rrect(42, 26, 46, 34, 10, HOT, 1.0)
    p.line([(52, 60), (49, 69), (64, 60)], 3.4, HOT, 1.0)
    p.text('Comment mein batao', 110, 60, 'Inter-700', 36, U.WHITE, 1.0)
    p.text('\u2193', w - 50, 61, 'Inter-700', 36, HOT, 1.0)
    return p.result()


@functools.lru_cache(maxsize=32)
def follow_button(state):
    """state 0..1: 0 = Follow (orange gradient), 1 = Following (glass)."""
    w, h = 420, 108
    p = U.Paint(w, h, pad=50)
    grad = np.clip((p._xx - p.X(0)) / (w * U.SS), 0, 1)[..., None]
    col = (ORANGE * (1 - grad) + HOT * grad) * (1 - state) + np.float32([0.09, 0.09, 0.10]) * state
    m = np.clip(0.5 - p.sdf_rrect(0, 0, w, h, 54), 0, 1)
    p.rgb = col * m[..., None] + p.rgb * (1 - m[..., None])
    p.a = m + p.a * (1 - m)
    p.glow(m, ORANGE, 18, 0.9 * (1 - state))
    p.stroke(0, 0, w, h, 54, 1.5, U.WHITE, 0.25 + 0.35 * state)
    p.stroke(2, 2, w - 4, h * 0.5, 50, 1.0, U.WHITE, 0.18 * (1 - state))
    if state < 0.5:
        p.text('Follow', w / 2, 70, 'InterTight-800', 44, U.WHITE, 1 - state * 2, anchor='c')
    else:
        p.text('Following  \u2713', w / 2, 69, 'InterTight-800', 40, U.WHITE, state * 2 - 1, anchor='c')
    return p.result()


def cursor_and_ripple(cv, u):
    if u < T_CURSOR:
        return
    cu = u - T_CURSOR
    P0, P1, P2, P3 = np.float32([880, 1440]), np.float32([920, 1360]), np.float32([700, 1290]), np.float32([600, 1322])
    q = A.SMOOTH(A.clamp(cu / (T_CLICK - T_CURSOR - 0.05)))
    pos = (1 - q) ** 3 * P0 + 3 * (1 - q) ** 2 * q * P1 + 3 * (1 - q) * q ** 2 * P2 + q ** 3 * P3
    press = A.clamp(1 - abs(u - T_CLICK) / 0.1) if abs(u - T_CLICK) < 0.1 else 0.0
    cs = U.cursor()
    cs = cv2.resize(cs, None, fx=(0.95 - 0.1 * press) / U.SS, fy=(0.95 - 0.1 * press) / U.SS, interpolation=cv2.INTER_AREA)
    place_rgba(cv, cs, pos[0] - 9, pos[1] - 9, A.ramp(cu, 0, 0.25) * (1 - A.ramp(u, T_CLICK + 0.5, T_CLICK + 0.8)))
    if u > T_CLICK:
        ru = u - T_CLICK
        if ru < 0.6:
            ring(cv, P3[0], P3[1], 16 + 50 * A.EXPO_OUT(ru / 0.6), 3, 1.0, k=(1 - ru / 0.6) * 0.9)


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
    """prev: canvas of the outgoing story shot (linear) for the opening iris."""
    ph = photo()
    ax, ay0, z0, av_s, avx, avy = framing()
    av_s *= AV[2] / 120.0                       # framing() is sized for a 120 px avatar
    bg = gradient(u)
    # ---------------- background: previous shot darkening -> black/orange liquid gradient
    if prev is not None and u < T_EXPAND:
        k = A.ramp(u, 0, 0.6, A.SMOOTH)
        cv[..., :3] = prev * (1 - k * 0.93) + bg * 0.3 * k
    else:
        cv[..., :3] = bg * (0.3 + 0.7 * A.ramp(u, T_BURN, T_GRAD + 0.3, A.SMOOTH))
    # ---------------- glass card springs in (scale, tilt, blur-in)
    if u > T_GRAD - 0.1:
        cu = u - T_GRAD
        s = A.spring(max(0.0, cu), 1.7, 0.62)
        op = A.ramp(cu, -0.1, 0.35, A.EASY)
        body, g = glass(cv[..., :3].copy(), u, u - T_GRAD + 0.6)
        layer = np.dstack([body * g['mask'][..., None], g['mask']]).astype(np.float32)
        click = round(A.clamp(A.spring(u - T_CLICK, 2.4, 0.55) if u > T_CLICK else 0.0) * 16) / 16
        layer = C.over(layer, text_layer(u, click))
        # drop shadow
        cv[..., :3] *= 1 - g['shadow'][..., None] * 0.55 * op
        sc = 0.9 + 0.1 * s
        cx, cy = (CARD[0] + CARD[2]) / 2, (CARD[1] + CARD[3]) / 2
        M = np.float32([[sc, 0, cx - sc * cx], [0, sc, cy - sc * cy + (1 - s) * 60]])
        layer = cv2.warpAffine(layer, M, (C.W, C.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        bl = (1 - A.ramp(cu, 0, 0.45, A.EASY)) * 16
        if bl > 1:
            layer = C.disc_blur(layer, bl)
        cv[..., :3] = layer[..., :3] * op + cv[..., :3] * (1 - layer[..., 3:4] * op)
    # ---------------- photo: ring -> full frame -> morphs into the avatar
    R_full = math.hypot(C.W, C.H) / 2 + 30
    if u < T_BURN:
        ue = A.ramp(u, T_EXPAND, T_FULL, A.EXPO)
        r = R0 * A.spring(u - T_RING, 1.6, 0.62) + (R_full - R0) * ue
        cx = CX + (C.W / 2 - CX) * ue
        cy = CY + (C.H / 2 - CY) * ue
        z = z0 + (1 - z0) * ue + 0.06 * (1 - A.ramp(u, 0, T_FULL, A.LINEAR)) - 0.04 * A.ramp(u, T_FULL, T_BURN, A.LINEAR)
        px, py = ax * (1 - ue) + C.W * 0.5 * ue, ay0 * (1 - ue) + C.H * 0.5 * ue
        ring_k = 1 - A.ramp(u, T_EXPAND, T_EXPAND + 0.5)
    else:
        um = A.ramp(u, T_BURN, T_BURN + 0.75, A.EXPO)                     # morph into the avatar
        r = R_full + (AV[2] - R_full) * um
        cx = C.W / 2 + (AV[0] - C.W / 2) * um
        cy = C.H / 2 + (AV[1] - C.H / 2) * um
        z = 0.96 + (av_s - 0.96) * um
        px, py = C.W * 0.5 * (1 - um) + avx * um, C.H * 0.5 * (1 - um) + avy * um
        ring_k = A.ramp(u, T_BURN + 0.5, T_BURN + 0.9)
    M = np.float32([[z, 0, cx - z * px], [0, z, cy - z * py]])
    warped = cv2.warpAffine(ph, M, (C.W, C.H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    m = circle_mask(cx, cy, max(r, 0))[..., None]
    cv[..., :3] = warped * m + cv[..., :3] * (1 - m)
    if u < T_BURN:
        ring(cv, cx, cy, r + 4, 6, A.ramp(u, 0.1, 1.0, A.SMOOTH), k=ring_k)
    else:
        ring(cv, cx, cy, r + 6, 5, A.ramp(u, T_BURN + 0.45, T_BURN + 1.1, A.SMOOTH), k=ring_k)
        ring(cv, cx, cy, r + 6 + 10 * (0.5 + 0.5 * math.sin(u * 3)), 1.5, 1.0, k=0.35 * ring_k)
    cursor_and_ripple(cv, u)
    return cv
