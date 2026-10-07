"""reel2_dev.py: development helper for reel2 (not a deliverable, no side effects on import).

    python3 reel2_dev.py strip 0.1,0.3,0.5 [--samples 1] [--scale 0.5] [--out name] [--cols 6]
        renders finished frames of reel2 at the given times (render.render_still), downsizes them, burns in the
        time and writes one labelled strip/grid -> workspace3/out/reel2/dev/<name>.jpg; prints ms per frame.
    python3 reel2_dev.py frames a b n ...   n evenly spaced frames in [a, b] (same options)
"""
import os
import sys
import time

import numpy as np


def strip(times, samples=1, scale=0.5, out='strip', cols=6):
    import cv2
    import core as K
    import render
    import reel2
    reel2.prewarm()
    tiles = []
    for t in times:
        t0 = time.time()
        u8 = render.render_still(reel2, t, samples)
        dt = time.time() - t0
        print('t=%.3f  %d samples  %.2fs' % (t, samples if samples else reel2.samples(t), dt), flush=True)
        im = cv2.resize(u8, (int(K.W * scale), int(K.H * scale)), interpolation=cv2.INTER_AREA)
        im = np.ascontiguousarray(im)
        cv2.putText(im, '%.3f' % t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(im, '%.3f' % t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 120), 2, cv2.LINE_AA)
        tiles.append(im)
    h, w = tiles[0].shape[:2]
    cols = min(cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.zeros((rows * h + (rows - 1) * 6, cols * w + (cols - 1) * 6, 3), np.uint8)
    for i, im in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r * (h + 6):r * (h + 6) + h, c * (w + 6):c * (w + 6) + w] = im
    d = os.path.join(K.OUT, 'reel2', 'dev')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, out + '.jpg')
    cv2.imwrite(p, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('->', p)
    return p


def _opt(args, name, default, typ=float):
    if name in args:
        return typ(args[args.index(name) + 1])
    return default


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(0)
    smp = _opt(a, '--samples', 1, int)
    sc = _opt(a, '--scale', 0.5)
    name = _opt(a, '--out', 'strip', str)
    cols = _opt(a, '--cols', 6, int)
    if a[0] == 'strip':
        ts = [float(x) for x in a[1].split(',')]
    elif a[0] == 'frames':
        t0, t1, n = float(a[1]), float(a[2]), int(a[3])
        ts = list(np.linspace(t0, t1, n))
    else:
        print(__doc__)
        sys.exit(1)
    strip(ts, smp, sc, name, cols)
