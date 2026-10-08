"""anim4_dev.py: development helper for anim4 (not a deliverable; no side effects on import).

    python3 anim4_dev.py strip 0.1,0.3,0.5 [--samples 1] [--scale 0.5] [--out name] [--cols 6]
        finished frames (render.render_still) downsized into one labelled grid -> workspace3/out/anim4/dev/<name>.jpg
    python3 anim4_dev.py frames a b n ...      n evenly spaced frames in [a, b] (same options)
    python3 anim4_dev.py full t [--samples k]  one full-res PNG -> workspace3/out/anim4/dev/full_<t>.png
    python3 anim4_dev.py stats a b [--samples 1] [--every 1]
        per-frame luma (BT.709 limited range, as ffmpeg signalstats reports): YMIN / YAVG / YMAX + jumps
    python3 anim4_dev.py mini a b [--fps 15]   low-res motion-check clip (1 sample) -> dev/mini_a_b.mp4
    python3 anim4_dev.py signalstats file.mp4   ffmpeg signalstats flash / lift / grey-white check of an encode
    python3 anim4_dev.py checks [a b]    layout checks (safe zones, like column, overlaps), every 2nd frame
"""
import os
import sys
import time

import numpy as np


def _out(name):
    import core as K
    d = os.path.join(K.OUT, 'anim4', 'dev')
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)


def strip(times, samples=1, scale=0.5, out='strip', cols=6):
    import cv2
    import core as K
    import render
    import anim4
    anim4.prewarm()
    tiles = []
    for t in times:
        t0 = time.time()
        u8 = render.render_still(anim4, t, samples)
        dt = time.time() - t0
        print('t=%.3f  %s samples  %.2fs' % (t, samples if samples else anim4.samples(t), dt), flush=True)
        im = cv2.resize(u8, (int(K.W * scale), int(K.H * scale)), interpolation=cv2.INTER_AREA)
        im = np.ascontiguousarray(im)
        cv2.putText(im, '%.3f' % t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(im, '%.3f' % t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (90, 20, 80), 2, cv2.LINE_AA)
        tiles.append(im)
    h, w = tiles[0].shape[:2]
    cols = min(cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.full((rows * h + (rows - 1) * 6, cols * w + (cols - 1) * 6, 3), 40, np.uint8)
    for i, im in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r * (h + 6):r * (h + 6) + h, c * (w + 6):c * (w + 6) + w] = im
    p = _out(out + '.jpg')
    cv2.imwrite(p, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('->', p)
    return p


def full(t, samples=None):
    import cv2
    import render
    import anim4
    anim4.prewarm()
    t0 = time.time()
    u8 = render.render_still(anim4, t, samples)
    print('t=%.3f %.2fs' % (t, time.time() - t0))
    p = _out('full_%.3f.png' % t)
    cv2.imwrite(p, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))
    print('->', p)
    return p


def stats(t0, t1, samples=1, every=1):
    import core as K
    import render
    import anim4
    anim4.prewarm()
    w = np.array([0.2126, 0.7152, 0.0722], np.float32)
    rows = []
    f0, f1 = int(round(t0 * K.FPS)), int(round(t1 * K.FPS))
    for f in range(f0, f1, every):
        t = f / K.FPS
        u8 = render.render_still(anim4, t, samples)
        y = 16.0 + 219.0 * (u8[::2, ::2].astype(np.float32) @ w) / 255.0
        rows.append((t, float(y.min()), float(y.mean()), float(np.percentile(y, 99.5))))
    p = _out('stats_%.2f_%.2f.csv' % (t0, t1))
    with open(p, 'w') as fh:
        fh.write('t,ymin,yavg,yp995\n')
        for r in rows:
            fh.write('%.3f,%.1f,%.1f,%.1f\n' % r)
    print('frames %d  YMIN %.0f..%.0f  YAVG %.1f..%.1f  Yp99.5 %.0f..%.0f' % (
        len(rows), min(r[1] for r in rows), max(r[1] for r in rows), min(r[2] for r in rows),
        max(r[2] for r in rows), min(r[3] for r in rows), max(r[3] for r in rows)))
    for a, b in zip(rows, rows[1:]):
        if abs(b[2] - a[2]) >= 4 or abs(b[3] - a[3]) >= 4:
            print('%.3f -> %.3f  YAVG %5.1f -> %5.1f  Yp99.5 %3.0f -> %3.0f' % (a[0], b[0], a[2], b[2], a[3], b[3]))
    print('->', p)
    return rows


def _opt(args, name, default, typ=float):
    if name in args:
        return typ(args[args.index(name) + 1])
    return default


def mini(t0, t1, fps=15, samples=1, scale=0.375, out=None):
    """Low-res motion check clip of [t0, t1) -> workspace3/out/anim4/dev/mini_<t0>_<t1>.mp4 (not a deliverable)."""
    import subprocess
    import cv2
    import core as K
    import render
    import anim4
    anim4.prewarm()
    w, h = int(K.W * scale) // 2 * 2, int(K.H * scale) // 2 * 2
    p = _out(out or 'mini_%.2f_%.2f.mp4' % (t0, t1))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (w, h),
           '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', p]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((t1 - t0) * fps))
    tt = time.time()
    for i in range(n):
        t = t0 + i / fps
        u8 = render.render_still(anim4, t, samples)
        pr.stdin.write(np.ascontiguousarray(cv2.resize(u8, (w, h), interpolation=cv2.INTER_AREA)).tobytes())
    pr.stdin.close()
    pr.wait()
    print('%d frames %.2fs/frame -> %s' % (n, (time.time() - tt) / max(1, n), p))
    return p


def signalstats(mp4, jump=4.0):
    """ffmpeg signalstats over an encode: per-frame YMIN / YAVG / YMAX (limited range). Prints the ranges and any
    frame-to-frame YAVG jump >= `jump` or YMAX dip (whites greying) / YMIN lift (blacks lifting) -> flash check."""
    import subprocess
    import re
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', mp4, '-vf', 'signalstats,metadata=print:file=-', '-f', 'null',
                          '-'], capture_output=True, text=True).stdout
    rows, cur = [], {}
    for line in out.splitlines():
        m = re.match(r'frame:(\d+)\s+pts:\S+\s+pts_time:(\S+)', line)
        if m:
            if cur:
                rows.append(cur)
            cur = dict(t=float(m.group(2)))
            continue
        m = re.match(r'lavfi\.signalstats\.(YMIN|YAVG|YMAX|YLOW|YHIGH)=(\S+)', line)
        if m:
            cur[m.group(1)] = float(m.group(2))
    if cur:
        rows.append(cur)
    if not rows:
        print('no stats')
        return rows
    for k in ('YMIN', 'YLOW', 'YAVG', 'YHIGH', 'YMAX'):
        v = [r[k] for r in rows if k in r]
        print('%-5s %.1f .. %.1f' % (k, min(v), max(v)))
    for a_, b_ in zip(rows, rows[1:]):
        if abs(b_['YAVG'] - a_['YAVG']) >= jump or b_['YHIGH'] < a_['YHIGH'] - 3 or b_['YLOW'] > a_['YLOW'] + 6:
            print('%.3f -> %.3f  YAVG %.1f -> %.1f  YLOW %.0f -> %.0f  YHIGH %.0f -> %.0f' % (
                a_['t'], b_['t'], a_['YAVG'], b_['YAVG'], a_['YLOW'], b_['YLOW'], a_['YHIGH'], b_['YHIGH']))
    return rows


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
    elif a[0] == 'strip':
        strip([float(x) for x in a[1].split(',')], smp, sc, name, cols)
    elif a[0] == 'frames':
        t0, t1, n = float(a[1]), float(a[2]), int(a[3])
        strip(list(np.linspace(t0, t1, n)), smp, sc, name, cols)
    elif a[0] == 'full':
        full(float(a[1]), _opt(a, '--samples', None, int))
    elif a[0] == 'mini':
        mini(float(a[1]), float(a[2]), fps=_opt(a, '--fps', 15, int), samples=smp)
    elif a[0] == 'signalstats':
        signalstats(a[1])
    elif a[0] == 'checks':
        import anim4
        rng = [float(x) for x in a[1:3]] if len(a) >= 3 and not a[1].startswith('--') else [0.0, None]
        anim4.checks(step=_opt(a, '--step', 1.0 / 15), t0=rng[0], t1=rng[1])
