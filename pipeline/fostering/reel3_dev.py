"""reel3_dev.py: development helper for reel3 (stills strips for critique; not part of the render contract).

    python3 reel3_dev.py 0.3,0.7,1.2 [--samples 1] [--scale 0.5] [--name hook] [--full] [--cols N]
    python3 reel3_dev.py f25-54 ...      every frame (frame indices at 30 fps) in that range; --samples 0 = reel's own
        -> workspace3/out/reel3/dev/<name>.jpg (a horizontal strip of the frames, labelled with t and ms)
           --full also writes each frame at full size: dev/<name>_<t>.png
"""
import os
import sys
import time

import cv2
import numpy as np


def main(argv):
    import core as K
    import render
    import reel3
    if argv[0].startswith('f'):
        a, b = [int(x) for x in argv[0][1:].split('-')]
        times = [i / K.FPS for i in range(a, b + 1)]
    else:
        times = [float(x) for x in argv[0].split(',') if x.strip()]
    cols = int(argv[argv.index('--cols') + 1]) if '--cols' in argv else len(times)
    samples = int(argv[argv.index('--samples') + 1]) if '--samples' in argv else 1
    scale = float(argv[argv.index('--scale') + 1]) if '--scale' in argv else 0.5
    name = argv[argv.index('--name') + 1] if '--name' in argv else 'strip'
    full = '--full' in argv
    out = os.path.join(K.OUT, 'reel3', 'dev')
    os.makedirs(out, exist_ok=True)
    tiles = []
    for t in times:
        t0 = time.time()
        u8 = render.render_still(reel3, t, samples)
        ms = (time.time() - t0) * 1000
        print('t=%.3f  %d samples  %.0f ms' % (t, samples, ms), flush=True)
        if full:
            cv2.imwrite(os.path.join(out, '%s_%.3f.png' % (name, t)), cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
        sm = cv2.resize(u8, (int(u8.shape[1] * scale), int(u8.shape[0] * scale)), interpolation=cv2.INTER_AREA)
        sm = np.ascontiguousarray(sm)
        lab = 'f%d t=%.3f' % (int(round(t * K.FPS)), t)
        cv2.putText(sm, lab, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(sm, lab, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(sm)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    strip = np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])
    p = os.path.join(out, name + '.jpg')
    cv2.imwrite(p, cv2.cvtColor(strip, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('->', p)


if __name__ == '__main__':
    main(sys.argv[1:])
