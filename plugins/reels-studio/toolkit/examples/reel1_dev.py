"""reel1_dev.py: in-process review helper for reel1 (stills / strips while building; not part of the render contract).

    python3 reel1_dev.py strip 0.1,0.3,0.5 [--samples 1] [--h 640] [--cols 6] [--name hook]
        -> workspace3/out/reel1/dev/<name>.jpg : frames side by side (each scaled to --h tall), time-stamped
    python3 reel1_dev.py still 3.4 [--samples 3]   -> workspace3/out/reel1/dev/still_<t>.png (full res)
    python3 reel1_dev.py range 0.4 0.6 [--step 1]  -> strip of consecutive frames (frame step) across a cut

Prints the per-frame render time. Run with `nice -n 10`.
"""
import os
import sys
import time

import numpy as np

import core as K

OUT = os.path.join(K.OUT, 'reel1', 'dev')


def _render(mod, t, samples):
    import render
    return render.render_still(mod, t, samples)


def _label(img, txt):
    import cv2
    cv2.putText(img, txt, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.putText(img, txt, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 230, 80), 2, cv2.LINE_AA)
    return img


def strip(times, samples=1, h=640, cols=6, name='strip', guides=True):
    import cv2
    import reel1
    os.makedirs(OUT, exist_ok=True)
    tiles = []
    for t in times:
        t0 = time.time()
        u8 = _render(reel1, t, samples)
        dt = time.time() - t0
        print('t=%.3f  %.2fs' % (t, dt), flush=True)
        if guides:
            u8 = u8.copy()
            # safe-zone guides: x 70..1010, y 230..1480 (thin cyan)
            u8[230, 70:1010] = (0, 255, 255)
            u8[1480, 70:1010] = (0, 255, 255)
            u8[230:1480, 70] = (0, 255, 255)
            u8[230:1480, 1010] = (0, 255, 255)
        w = int(round(h * K.W / K.H))
        sm = cv2.resize(u8, (w, h), interpolation=cv2.INTER_AREA)
        tiles.append(_label(np.ascontiguousarray(sm), '%.2f' % t))
    rows = []
    for i in range(0, len(tiles), cols):
        r = tiles[i:i + cols]
        while len(r) < cols and len(tiles) > cols:
            r.append(np.zeros_like(tiles[0]))
        rows.append(np.concatenate(r, 1))
    img = np.concatenate(rows, 0)
    p = os.path.join(OUT, name + '.jpg')
    cv2.imwrite(p, cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('->', p)
    return p


def still(t, samples=3):
    import reel1
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    u8 = _render(reel1, t, samples)
    print('t=%.3f  samples=%d  %.2fs' % (t, samples, time.time() - t0))
    p = os.path.join(OUT, 'still_%.2f.png' % t)
    K.save_png(p, u8)
    print('->', p)
    return p


def _opt(args, k, d, f=float):
    return f(args[args.index(k) + 1]) if k in args else d


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == 'strip':
        ts = [float(v) for v in a[1].split(',')]
        strip(ts, _opt(a, '--samples', 1, int), _opt(a, '--h', 640, int), _opt(a, '--cols', 6, int),
              _opt(a, '--name', 'strip', str), '--noguides' not in a)
    elif a[0] == 'range':
        t0, t1 = float(a[1]), float(a[2])
        st = _opt(a, '--step', 1, int)
        f0, f1 = int(round(t0 * K.FPS)), int(round(t1 * K.FPS))
        ts = [f / K.FPS for f in range(f0, f1 + 1, st)]
        strip(ts, _opt(a, '--samples', 1, int), _opt(a, '--h', 480, int), _opt(a, '--cols', 8, int),
              _opt(a, '--name', 'range', str), '--noguides' not in a)
    elif a[0] == 'still':
        still(float(a[1]), _opt(a, '--samples', 3, int))
