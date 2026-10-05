"""Face boxes (OpenCV Haar) for every frame, gap-filled and smoothed, for the hand-drawn tracking box.
Writes $GOLD_WORKDIR/work/face_track.json: per frame [cx, cy, w, h] in 1080x1920 design px (or null)."""
import os, json
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter1d

S = os.environ.get('GOLD_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'workspace')))


def main():
    det = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    head = json.load(open(S + '/work/head_track.json'))
    cuts = json.load(open(S + '/work/cuts.json'))
    n = len(head)
    raw = np.full((n, 4), np.nan, np.float32)
    for i in range(n):
        f = cv2.imread(f'{S}/frames/{i:05d}.jpg', 0)
        k = 1080 / f.shape[1]
        g = cv2.resize(f, (540, 960))
        hx, hy, hs = head[i]
        faces = det.detectMultiScale(g, 1.08, 4, minSize=(30, 30))
        best = None
        for (x, y, w, h) in faces:
            cx, cy = (x + w / 2) * 2, (y + h / 2) * 2
            d = abs(cx - hx) + abs(cy - hy)
            if d < hs * 0.8 and (best is None or d < best[0]):
                best = (d, cx, cy, w * 2.0, h * 2.0)
        if best:
            raw[i] = best[1:]
    out = raw.copy()
    for k, a in enumerate(cuts):
        b = cuts[k + 1] if k + 1 < len(cuts) else n
        seg = raw[a:b]
        ok = ~np.isnan(seg[:, 0])
        if ok.sum() < 3:
            continue
        idx = np.arange(b - a)
        for c in range(4):
            col = np.interp(idx, idx[ok], seg[ok, c])
            out[a:b, c] = gaussian_filter1d(col, 3 if c < 2 else 8, mode='nearest')
    json.dump([None if np.isnan(r[0]) else [round(float(v), 1) for v in r] for r in out],
              open(S + '/work/face_track.json', 'w'))
    print('faces found in', int((~np.isnan(raw[:, 0])).sum()), 'of', n, 'frames')


if __name__ == '__main__':
    main()
