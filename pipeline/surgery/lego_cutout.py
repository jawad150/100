"""Cut the client's red Lego brick photo out of its background.

$WS/src/lego_red_photo.png -> $WS/src/lego_brick_red.png (RGBA, cropped to the brick).
The client's PNG already carries an alpha channel; a flat white-background photo is keyed.

Usage: python3 lego_cutout.py
"""
import cv2
import numpy as np
from common import WS

src = cv2.imread(f'{WS}/src/lego_red_photo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
if src.shape[2] == 4 and src[..., 3].min() < 0.5:
    out = src
    ys, xs = np.where(out[..., 3] > 0.02)
    out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cv2.imwrite(f'{WS}/src/lego_brick_red.png', (out * 255 + 0.5).astype(np.uint8))
    print('wrote', f'{WS}/src/lego_brick_red.png', out.shape, '(alpha from the photo)')
    raise SystemExit
im = src[..., :3]
# white -> min(G, B) near 1; the red plastic (even its highlights) has low green/blue
gb = np.minimum(im[..., 0], im[..., 1])
a = np.clip((0.93 - gb) / 0.12, 0, 1)
# keep the brick only (largest blob), fill holes such as pale highlights
n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
solid = (lab == big).astype(np.uint8)
cnt, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
fill = np.zeros_like(solid)
cv2.drawContours(fill, cnt, -1, 1, -1)
near = cv2.dilate(fill, np.ones((5, 5), np.uint8)).astype(np.float32)
a = np.maximum(a * near, cv2.erode(fill, np.ones((5, 5), np.uint8)).astype(np.float32))
a = cv2.GaussianBlur(a, (0, 0), 0.7) * near
# remove the white spill on the soft edge: C = a*F + (1-a)*white  ->  F = (C - (1-a)) / a
fg = np.clip((im - (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0, 1)
out = np.dstack([fg, a])
ys, xs = np.where(a > 0.02)
out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
cv2.imwrite(f'{WS}/src/lego_brick_red.png', (out * 255 + 0.5).astype(np.uint8))
print('wrote', f'{WS}/src/lego_brick_red.png', out.shape)
