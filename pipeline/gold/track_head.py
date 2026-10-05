"""Track the presenter's head in every frame from the RVM matte (for motion-tracked captions).

For each frame: head box from the top of the person matte (the rows above the shoulders),
then a zero-phase smoothing so tracked text glides like an After Effects track.
Writes $GOLD_WORKDIR/work/head_track.json: per frame [cx, cy, size] in 1080x1920 design px.
"""
import os, json
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter1d

S = os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace')))


def head_of(m):
    """m: uint8 matte 1080x1920 -> (cx, cy, size) or None."""
    b = m > 128
    rows = np.where(b.any(1))[0]
    if len(rows) < 40:
        return None
    top = rows[0]
    widths = b.sum(1).astype(np.float32)
    # head = rows from the top down to where the silhouette widens into the shoulders
    seg = widths[top:top + 700]
    ref = np.median(seg[40:200]) if len(seg) > 200 else seg.max()
    shoulder = np.where(seg > ref * 1.9)[0]
    hh = int(np.clip(shoulder[0] if len(shoulder) else 260, 140, 420))
    ys, xs = np.where(b[top:top + hh])
    if len(xs) < 50:
        return None
    cx = float(np.median(xs))
    return cx, top + hh * 0.5, float(hh)


def main():
    cuts = json.load(open(S + '/work/cuts.json'))
    n = len(os.listdir(S + '/matte'))
    raw = []
    for i in range(n):
        m = cv2.imread(f'{S}/matte/{i:05d}.png', 0)
        raw.append(head_of(m))
    bounds = cuts + [n]
    out = np.zeros((n, 3), np.float32)
    for k in range(len(cuts)):
        a, b = bounds[k], bounds[k + 1]
        seg = raw[a:b]
        good = [j for j, v in enumerate(seg) if v is not None]
        if not good:
            out[a:b] = (540, 520, 300)
            continue
        arr = np.array([seg[j] if seg[j] is not None else (np.nan,) * 3 for j in range(len(seg))], np.float32)
        for c in range(3):
            col = arr[:, c]
            idx = np.arange(len(col))
            ok = ~np.isnan(col)
            col = np.interp(idx, idx[ok], col[ok])
            # heavier smoothing for size, light for position (tracks gestures without jitter)
            arr[:, c] = gaussian_filter1d(col, 7 if c < 2 else 14, mode='nearest')
        out[a:b] = arr
    json.dump(out.round(1).tolist(), open(S + '/work/head_track.json', 'w'))
    print('tracked', n)


if __name__ == '__main__':
    main()
