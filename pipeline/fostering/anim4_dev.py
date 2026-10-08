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
    python3 anim4_dev.py speeds a b [--limit 8]   stepped-copy probe: screen motion per render sample of each drawn box
"""
import math
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


def speeds(t0, t1, limit=8.0, kinds=None):
    """Stepped-copy probe: draws every frame in [t0, t1) with the box recorder, matches each prop / text / coin box
    to the next frame's (text by label, others by nearest box of similar size) and reports the screen motion per
    render sample (centre travel or edge growth / samples(t)) above `limit` px. Coins drawn swept are smeared within
    each sample, so their rows are informative only."""
    import core as K
    import anim4
    import anim4_fx as X
    anim4.prewarm()
    f0, f1 = int(round(t0 * K.FPS)), int(round(t1 * K.FPS))
    prev = None
    worst = {}
    for f in range(f0, f1 + 1):
        t = f / K.FPS
        X.REC = []
        try:
            anim4.draw(t)
            rec = X.REC
        finally:
            X.REC = None
        cur = [r for r in rec if r[2] > 0.3 and (kinds is None or r[0] in kinds)]
        if prev is not None:
            n = anim4.samples(t - 0.5 / K.FPS)
            used = set()
            for r in prev:
                kind, (x0, y0, x1, y1) = r[0], r[1]
                if x1 < 0 or x0 > K.W or y1 < 0 or y0 > K.H:
                    continue
                cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
                best, bj = None, None
                for j, q in enumerate(cur):
                    if j in used or q[0] != kind:
                        continue
                    if kind == 'text' and (len(q) > 3 and len(r) > 3 and q[3] != r[3]):
                        continue
                    qx0, qy0, qx1, qy1 = q[1]
                    qw, qh = qx1 - qx0, qy1 - qy0
                    if abs(qw - w) > 0.3 * w + 20 or abs(qh - h) > 0.3 * h + 20:
                        continue
                    d = math.hypot((qx0 + qx1) / 2 - cx, (qy0 + qy1) / 2 - cy)
                    if best is None or d < best:
                        best, bj = d, j
                if bj is None or best > 400:
                    continue
                used.add(bj)
                q = cur[bj]
                grow = max(abs((q[1][2] - q[1][0]) - w), abs((q[1][3] - q[1][1]) - h)) / 2
                step = (best + grow) / n
                lab = r[3] if len(r) > 3 else ''
                key = (kind, lab)
                if step > limit:
                    print('%.3f  n=%d  %-5s %-22s travel %.0f grow %.0f px/frame -> %.1f px/sample  at (%.0f, %.0f)'
                          % (t, n, kind, lab[:22], best, grow, step, cx, cy), flush=True)
                if step > worst.get(key, (0, 0))[0]:
                    worst[key] = (round(step, 1), round(t, 3))
        prev = cur
    print('worst per kind:')
    for k, v in sorted(worst.items(), key=lambda kv: -kv[1][0])[:15]:
        print('   ', k, v)


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
    elif a[0] == 'speeds':
        kd = _opt(a, '--kinds', '', str)
        speeds(float(a[1]), float(a[2]), _opt(a, '--limit', 8.0), kd.split(',') if kd else None)
    elif a[0] == 'checks':
        import anim4
        rng = [float(x) for x in a[1:3]] if len(a) >= 3 and not a[1].startswith('--') else [0.0, None]
        anim4.checks(step=_opt(a, '--step', 1.0 / 15), t0=rng[0], t1=rng[1])
