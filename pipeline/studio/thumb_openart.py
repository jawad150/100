"""Cover for the creator's OpenArt Awards AI video ad entry, in the reel family's look: black stage with
soft orange rays and dust, OpenArt wordmark (white, from the openart.ai site footer), a glowing orange
ring with a play button, and the caption type (Poppins white + GwynerCondensed-Italic orange, snake line).

Logo source: https://openart.ai (footer brand image) saved as workspace3/assets/openart_logo.png.
python3 thumb_openart.py  -> workspace3/out/openart_cover_*.jpg (9:16 reel cover + 3:4 grid preview)
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'memories'))
import captions as K  # noqa: E402
import comp as C  # noqa: E402
import ending as E  # noqa: E402
import hud as U  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'workspace3'))
W, H = C.W, C.H
RC = (540, 900, 205)                         # ring centre + radius (the stage rays radiate from here)
ORANGE = np.float32([1.0, 0.33, 0.03])


def place_mask(cv, m, cx, cy, col, op=1.0, glow=None):
    """Additively composite a coverage mask (centred at cx, cy) as colour col over linear cv."""
    h, w = m.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    reg = cv[y0:y0 + h, x0:x0 + w]
    if glow is not None:
        g = cv2.GaussianBlur(m, (0, 0), glow[0]) * 0.8 + cv2.GaussianBlur(m, (0, 0), glow[0] * 3) * 0.5
        reg += g[..., None] * glow[1] * op
    a = m[..., None] * op
    reg[...] = reg * (1 - a) + col * a


def logo(width):
    im = cv2.imread(ROOT + '/assets/openart_logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3]
    ys, xs = np.where(a > 0.02)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h = int(round(a.shape[0] * width / a.shape[1]))
    a = cv2.resize(a, (width, h), interpolation=cv2.INTER_AREA)
    return np.pad(a, 40)


def text(txt, font, px, track):
    m, _ = U.text_mask(txt, font, px, track)
    return np.pad(cv2.resize(m, (m.shape[1] // U.SS, m.shape[0] // U.SS), interpolation=cv2.INTER_AREA), 30)


def play_button(cv, cx, cy, r):
    """Rounded play triangle inside the ring, white core with orange glow."""
    m = np.zeros((H, W), np.float32)
    pts = np.float32([[cx - r * 0.42, cy - r * 0.62], [cx - r * 0.42, cy + r * 0.62], [cx + r * 0.68, cy]])
    cv2.fillPoly(m, [np.int32(pts * 16)], 1.0, cv2.LINE_AA, shift=4)
    m = cv2.GaussianBlur(m, (0, 0), 2.2)
    m = np.clip((m - 0.25) * 1.8, 0, 1)                    # rounded corners
    g = cv2.GaussianBlur(m, (0, 0), 18) * 0.9 + cv2.GaussianBlur(m, (0, 0), 50) * 0.6
    cv += g[..., None] * C.to_lin(ORANGE) * 1.2
    cv[...] = cv * (1 - m[..., None]) + m[..., None] * C.to_lin(np.float32([1.0, 0.93, 0.86]))


def dust(cv, seed=4, n=420):
    rng = np.random.default_rng(seed)
    ov = np.zeros((H // 2, W // 2), np.float32)
    x, y = rng.uniform(0, W, n), rng.uniform(150, H - 150, n)
    d = np.hypot(x - RC[0], (y - RC[1]) * 0.8)
    b = rng.uniform(0.3, 1.0, n) * (0.25 + 0.9 * np.exp(-(d / 520) ** 2))
    r = rng.uniform(0.6, 2.0, n)
    for xi, yi, ri, bi in zip(x, y, r, b):
        cv2.circle(ov, (int(xi * 4), int(yi * 4)), max(1, int(ri * 4 * 0.6)), float(bi), -1, cv2.LINE_AA, shift=3)
    cv += cv2.resize(cv2.GaussianBlur(ov, (0, 0), 0.8), (W, H))[..., None] * C.to_lin(np.float32([1.0, 0.75, 0.5])) * 0.7
    ov = np.zeros((H // 4, W // 4), np.float32)                # a few out-of-focus foreground discs
    for _ in range(14):
        cv2.circle(ov, (int(rng.uniform(0, W) / 2), int(rng.uniform(200, H - 200) / 2)), int(rng.uniform(10, 24)),
                   float(rng.uniform(0.2, 0.55)), -1, cv2.LINE_AA, shift=1)
    cv += cv2.resize(cv2.GaussianBlur(ov, (0, 0), 1.6), (W, H))[..., None] * C.to_lin(np.float32([1.0, 0.6, 0.3])) * 0.08


def render():
    cv = E.stage(2.0).copy()
    # warm floor glow + top spotlight haze for depth
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    cv += np.exp(-((yy - 1750) / 260) ** 2) * C.to_lin(ORANGE) * 0.05
    dust(cv)
    cx, cy, r = RC
    # ring: dark glass disc, pulse rings, main glowing ring, play button
    disc = E.circle_mask(cx, cy, r - 6)[..., None]
    cv[...] = cv * (1 - disc * 0.75) + disc * C.to_lin(np.float32([0.06, 0.045, 0.04])) * 0.75
    E.ring(cv, cx, cy, r + 46, 2, 1.0, k=0.35)
    E.ring(cv, cx, cy, r + 100, 1.5, 1.0, k=0.15)
    E.ring(cv, cx, cy, r, 6, 1.0, k=1.0)
    play_button(cv, cx + 8, cy, r * 0.42)
    # OpenArt wordmark + AWARDS
    lg = logo(560)
    place_mask(cv, lg, 540, 380, np.float32([1.0, 1.0, 1.0]), glow=(6, np.float32([1.0, 0.85, 0.7]) * 0.25))
    aw = text('AWARDS', 'Poppins-600', 40, 0.62)
    place_mask(cv, aw, 540, 492, C.to_lin(np.float32([1.0, 0.55, 0.18])), glow=(5, C.to_lin(ORANGE) * 0.6))
    for x0, x1 in ((290, 400), (680, 790)):                    # thin orange rules either side
        m = np.zeros((H, W), np.float32)
        cv2.line(m, (x0 * 16, 492 * 16), (x1 * 16, 492 * 16), 1.0, 2, cv2.LINE_AA, shift=4)
        cv += (m[..., None] + cv2.GaussianBlur(m, (0, 0), 4)[..., None] * 2) * C.to_lin(ORANGE) * 0.8
    # title in the caption type
    K.WHITE_PX, K.KEY_PX = 86, 220
    snake = lambda x0, x1, y, amp: K.Path(K.bezier([(x0, y + 6), (x0 + (x1 - x0) * 0.3, y - amp),  # noqa: E731
                                                     (x0 + (x1 - x0) * 0.64, y + amp), (x1, y - 4)]))
    K.Phrase([('MY', 0.0, False), ('ENTRY', 0.0, False)], snake(300, 780, 1295, 8), 1e9, line=False).draw(cv, 5.0)
    K.Phrase([('AI', 0.0, True), ('video', 0.0, True), ('ad', 0.0, True)], snake(80, 1000, 1490, 24), 1e9).draw(cv, 5.0)
    hd = text('@jawad_mp4', 'Poppins-600', 30, 0.08)
    place_mask(cv, hd, 540, 1628, C.to_lin(np.float32([0.78, 0.74, 0.7])))
    # finish like the end card
    f = C.deep_glow(cv, 0.6, 0.45, (1.0, 0.7, 0.5))
    f = C.halation(f, 0.16)
    f = C.anamorphic(f, 1.6, 0.06, (1.0, 0.55, 0.25), 0.3)
    s = C.grade(f, 'orange', vignette=0.5)
    s = C.grain(s, 3.0, 0.016)
    return (np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    im = render()
    out = ROOT + '/out'
    os.makedirs(out, exist_ok=True)
    cv2.imwrite(out + '/openart_cover_1080x1920.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 96])
    cv2.imwrite(out + '/openart_cover_grid_3x4_preview.jpg', im[240:1680], [cv2.IMWRITE_JPEG_QUALITY, 95])
    print('ok')
