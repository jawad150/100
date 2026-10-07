"""Cover / thumbnail for the studio reel: a still of the same scene (both silhouettes in the orange deep
glow, Netflix grade) with the reel's caption type - Poppins white + GwynerCondensed-Italic orange, snake
guide line. 1080x1920 for the reel, with everything important inside the 3:4 profile-grid crop.

python3 thumb.py  -> workspace3/out/thumb_*.png|jpg (reel 9:16, grid 3:4 preview, feed 4:5 preview)
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import studio as ST  # noqa: E402
from studio import K, C  # noqa: E402

T = 28.95                                    # lights on, warm 'better' swell starting
CAM = (575.0, 1014.0, 1.39, 0.0)             # both of them, feet ~y 1500
GRID = (240, 1680)                           # 3:4 crop rows of the 9:16 cover


def title_phrases():
    K.WHITE_PX, K.KEY_PX = 84, 218           # big title type (glyph caches are still empty here)
    snake = lambda x0, x1, y, amp: K.Path(K.bezier([(x0, y + 6), (x0 + (x1 - x0) * 0.3, y - amp),  # noqa: E731
                                                     (x0 + (x1 - x0) * 0.64, y + amp), (x1, y - 4)]))
    out = [
        K.Phrase([('MEETING', 0.0, False), ('MY', 0.0, False)], snake(250, 830, 400, 10), 1e9, line=False),
        K.Phrase([('younger', 0.0, True), ('self', 0.0, True)], snake(90, 990, 590, 26), 1e9),
        K.Phrase([("You're", 0.0, False), ('better.', 0.0, True)], snake(300, 780, 1600, 14), 1e9, scale=0.52),
    ]
    return out


def render():
    ST.camera = lambda t: CAM
    ST.activity = lambda who, t: 1.0
    ST.voice = lambda t: 0.45
    cv = ST.story(T)
    for p in title_phrases():
        p.draw(cv, 5.0)
    s = ST.finish_story(cv, T)
    return (np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    im = render()
    os.makedirs(ST.OUT, exist_ok=True)
    cv2.imwrite(ST.OUT + '/thumb_reel_1080x1920.png', im)
    cv2.imwrite(ST.OUT + '/thumb_reel_1080x1920.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 96])
    cv2.imwrite(ST.OUT + '/thumb_grid_3x4_preview.jpg', im[GRID[0]:GRID[1]], [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(ST.OUT + '/thumb_feed_4x5_preview.jpg', im[285:1635], [cv2.IMWRITE_JPEG_QUALITY, 95])
    print('ok')
