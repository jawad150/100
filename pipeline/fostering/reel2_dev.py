"""reel2_dev.py: development helper for reel2 (not a deliverable, no side effects on import).

    python3 reel2_dev.py strip 0.1,0.3,0.5 [--samples 1] [--scale 0.5] [--out name] [--cols 6]
        renders finished frames of reel2 at the given times (render.render_still), downsizes them, burns in the
        time and writes one labelled strip/grid -> workspace3/out/reel2/dev/<name>.jpg; prints ms per frame.
    python3 reel2_dev.py frames a b n ...   n evenly spaced frames in [a, b] (same options)
    python3 reel2_dev.py stats a b [--samples 1] [--every 1]
        renders every frame in [a, b) and prints signalstats-style luma per frame (BT.709 limited range YMIN /
        YAVG, as ffmpeg signalstats reports on the encode) and every frame-to-frame jump (YMIN +6 / YAVG +-6)
        -> workspace3/out/reel2/dev/stats_<a>_<b>.csv
    python3 reel2_dev.py sfx
        mixes reel2.cues() with a -2.0 dBTP ceiling (AAC overshoot stays <= -1.5 dBTP after the mux) ->
        workspace3/audio/reel2_sfx.wav + reel2_sfx_stem.wav. render.py remixes with its default ceiling only when
        reel2.py is NEWER than the wav, so run this last (or render with --no-sfx-build).
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


def stats(t0, t1, samples=1, every=1):
    import core as K
    import render
    import reel2
    reel2.prewarm()
    w = np.array([0.2126, 0.7152, 0.0722], np.float32)
    rows = []
    f0, f1 = int(round(t0 * K.FPS)), int(round(t1 * K.FPS))
    for f in range(f0, f1, every):
        t = f / K.FPS
        u8 = render.render_still(reel2, t, samples)
        y = 16.0 + 219.0 * (u8[::2, ::2].astype(np.float32) @ w) / 255.0
        rows.append((t, float(y.min()), float(y.mean())))
    d = os.path.join(K.OUT, 'reel2', 'dev')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'stats_%.2f_%.2f.csv' % (t0, t1))
    with open(p, 'w') as fh:
        fh.write('t,ymin,yavg\n')
        for r in rows:
            fh.write('%.3f,%.1f,%.1f\n' % r)
    print('frames %d  YMIN range %.0f..%.0f  YAVG range %.0f..%.0f' % (
        len(rows), min(r[1] for r in rows), max(r[1] for r in rows), min(r[2] for r in rows),
        max(r[2] for r in rows)))
    for a, b in zip(rows, rows[1:]):
        if b[1] - a[1] >= 6 or abs(b[2] - a[2]) >= 6:
            print('%.3f -> %.3f  YMIN %3.0f -> %3.0f  YAVG %5.1f -> %5.1f' % (a[0], b[0], a[1], b[1], a[2], b[2]))
    print('->', p)
    return rows


def sfx():
    import audio as A
    import core as K
    import reel2
    rep = A.mix(reel2.cues(), reel2.DUR, os.path.join(K.AUDIO, 'reel2_sfx.wav'),
                os.path.join(K.AUDIO, 'reel2_sfx_stem.wav'), bed=reel2.BED, bed_gain_db=reel2.BED_GAIN_DB,
                tp_ceiling=-2.0, verbose=False)
    print('reel2 SFX: %.2f LUFS  %.2f dBTP  (%d cues)' % (rep['integrated_lufs'], rep['true_peak_dbtp'],
                                                      len(reel2.cues())))
    for pl in rep.get('placed', []):
        if pl.get('warn'):
            print('   cue warning: %s at %.2fs: %s' % (pl.get('name'), pl.get('t', 0.0), pl['warn']))
    return rep


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
    if a[0] == 'stats':
        stats(float(a[1]), float(a[2]), smp, _opt(a, '--every', 1, int))
        sys.exit(0)
    if a[0] == 'sfx':
        sfx()
        sys.exit(0)
    if a[0] == 'strip':
        ts = [float(x) for x in a[1].split(',')]
    elif a[0] == 'frames':
        t0, t1, n = float(a[1]), float(a[2]), int(a[3])
        ts = list(np.linspace(t0, t1, n))
    else:
        print(__doc__)
        sys.exit(1)
    strip(ts, smp, sc, name, cols)
