"""Cut out pouch pack shots (white bg -> alpha), crop, save to workspace_br/src/cut_*.png."""
import sys, os
import numpy as np, cv2
from PIL import Image

W = sys.argv[1]
for name, f in [('orange', '2.webp'), ('raspberry', '4.webp'), ('pear', '6.webp')]:
    im = np.asarray(Image.open(f'{W}/src/{f}').convert('RGB'))
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    bgish = ((hsv[..., 2] > 200) & (hsv[..., 1] < 40)).astype(np.uint8)
    # flood fill background connected to the border
    mask = np.zeros((im.shape[0] + 2, im.shape[1] + 2), np.uint8)
    ff = bgish.copy() * 255
    for seed in [(0, 0), (im.shape[1] - 1, 0), (0, im.shape[0] - 1), (im.shape[1] - 1, im.shape[0] - 1)]:
        cv2.floodFill(ff, mask, seed, 128)
    bg = (ff == 128).astype(np.uint8)
    fg = 1 - bg
    # keep largest component, fill holes
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
    big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    fg = (lab == big).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # fruit art can touch the pouch edge with near-white flesh: fill the hull in the fruit band
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = np.zeros_like(fg)
    cv2.fillPoly(hull, [cv2.convexHull(max(cnts, key=cv2.contourArea))], 1)
    band = np.zeros_like(fg)
    ys_, xs_ = np.where(fg > 0)
    by0, by1 = ys_.min(), ys_.max()
    bx0, bx1 = xs_.min(), xs_.max()
    band[int(by0 + 0.15 * (by1 - by0)):int(by0 + 0.5 * (by1 - by0)), int(bx0 + 0.7 * (bx1 - bx0)):] = 1
    fg = np.maximum(fg, hull * band)
    a = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 1.2)
    a = np.clip((a - 0.5) * 2.5 + 0.5, 0, 1)
    ys, xs = np.where(a > 0.02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([im, (a * 255).astype(np.uint8)])[y0:y1, x0:x1]
    Image.fromarray(rgba).save(f'{W}/src/cut_{name}.png')
    print(name, rgba.shape)
