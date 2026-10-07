"""Cover for the Yaadein (Spider-Man) reel: the hero mask portrait plate in the reel's dark red/blue grade,
the hook's 'ERROR - CAN'T DELETE THIS MEMORY' panel, and the caption type (Poppins white + Gwyner orange,
snake guide line). 1080x1920 with everything important inside the 3:4 profile-grid crop.

python3 thumb_yaadein.py  -> workspace2/out/yaadein_cover_*.jpg
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import captions as K  # noqa: E402
import comp as C  # noqa: E402
import ending as E  # noqa: E402
import hud as U  # noqa: E402
import saas_hook as SH  # noqa: E402

W, H = C.W, C.H
RED = np.float32([1.0, 0.08, 0.04])
BLUE = np.float32([0.10, 0.22, 1.0])


def plate():
    im = C.load(C.ROOT + '/plates3/a1_mask_full.png')[..., :3].copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # night-ify the pale haze: pull the background down and toward blue, keep the mask's red
    lum = im @ np.float32([0.2126, 0.7152, 0.0722])
    redness = np.clip((im[..., 0] - im[..., 2]) * 4, 0, 1)
    bg = (1 - redness)[..., None]
    im = im * (1 - bg * 0.9) + bg * lum[..., None] * BLUE * 0.22
    # red key from the right, cold blue from top-left, falloff toward the bottom for the title
    key = np.exp(-(((xx - 900) / 520) ** 2 + ((yy - 700) / 700) ** 2))[..., None]
    cold = np.exp(-(((xx - 80) / 600) ** 2 + ((yy - 200) / 700) ** 2))[..., None]
    im = im * (0.75 + 0.6 * key * RED / RED.max()) + cold * BLUE * 0.035
    floor = np.clip((yy - 1050) / 650, 0, 1)[..., None]
    return (im * (1 - 0.82 * floor ** 1.3)).astype(np.float32)


def embers(cv, seed=11, n=260):
    rng = np.random.default_rng(seed)
    ov = np.zeros((H // 2, W // 2), np.float32)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(150, H - 120)
        cv2.circle(ov, (int(x * 4), int(y * 4)), max(1, int(rng.uniform(0.6, 2.0) * 2.4)), float(rng.uniform(0.2, 1.0)),
                   -1, cv2.LINE_AA, shift=3)
    cv += cv2.resize(cv2.GaussianBlur(ov, (0, 0), 0.8), (W, H))[..., None] * C.to_lin(np.float32([1.0, 0.45, 0.25])) * 0.45
    ov = np.zeros((H // 4, W // 4), np.float32)
    for _ in range(12):
        cv2.circle(ov, (int(rng.uniform(0, W) / 2), int(rng.uniform(250, H - 250) / 2)), int(rng.uniform(10, 26)),
                   float(rng.uniform(0.2, 0.6)), -1, cv2.LINE_AA, shift=1)
    cv += cv2.resize(cv2.GaussianBlur(ov, (0, 0), 1.6), (W, H))[..., None] * C.to_lin(np.float32([1.0, 0.25, 0.15])) * 0.08


def error_panel(cv, cy):
    img = SH.delete_panel(73, 16)                              # error state of the hook panel
    img = cv2.resize(img, (img.shape[1] // U.SS, img.shape[0] // U.SS), interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    x0, y0 = W // 2 - w // 2, int(cy - h / 2)
    reg = cv[y0:y0 + h, x0:x0 + w]
    m = np.clip(img[..., 3:4] * 1.6, 0, 1)                     # frosted glass only under the panel itself
    reg[...] = reg * (1 - m) + cv2.GaussianBlur(reg, (0, 0), 18) * 0.5 * m
    glow = cv2.GaussianBlur(img[..., 3], (0, 0), 24)
    cv[y0:y0 + h, x0:x0 + w] += glow[..., None] * RED * 0.10
    E.place_rgba(cv, img, x0, y0, 1.0)


def render():
    cv = plate()
    embers(cv)
    error_panel(cv, 1080)
    K.WHITE_PX, K.KEY_PX = 72, 190
    snake = lambda x0, x1, y, amp: K.Path(K.bezier([(x0, y + 6), (x0 + (x1 - x0) * 0.3, y - amp),  # noqa: E731
                                                     (x0 + (x1 - x0) * 0.64, y + amp), (x1, y - 4)]))
    K.Phrase([('KUCH', 0.0, False), ('yaadein', 0.0, True)], snake(150, 930, 1345, 18), 1e9).draw(cv, 5.0)
    K.Phrase([('delete', 0.0, False), ('nahi', 0.0, True), ('hoti', 0.0, False)], snake(170, 910, 1585, 14), 1e9,
             scale=0.86).draw(cv, 5.0)
    f = C.deep_glow(cv, 0.6, 0.45, (1.0, 0.55, 0.5))
    f = C.halation(f, 0.16)
    f = C.anamorphic(f, 1.3, 0.12, (0.35, 0.55, 1.0), 0.4)
    s = C.grade(f, 'spider', exposure=0.05, sat=1.12, contrast=1.15, vignette=0.85)
    s = C.grain(s, 2.0, 0.018)
    return (np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    im = render()
    out = C.ROOT + '/out'
    cv2.imwrite(out + '/yaadein_cover_1080x1920.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 96])
    cv2.imwrite(out + '/yaadein_cover_grid_3x4_preview.jpg', im[240:1680], [cv2.IMWRITE_JPEG_QUALITY, 95])
    print('ok')
