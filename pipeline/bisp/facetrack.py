"""Face box of the presenter per segment, in OUTPUT coordinates (segment zoom + slow push-in applied).

    python3 facetrack.py   -> workspace_bisp/faces_seg.json  {seg_id: {top, bottom, left, right, track: [[t, x0, y0, x1, y1]...]}}

The protected "face area" is the Haar face box widened to forehead (-0.32 h) and chin (+1.14 h); graphics are laid
out so they never enter it (reel.py bands)."""
import os, sys, json
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edl

WS = edl.WS
FACES = json.load(open(os.path.join(WS, 'faces.json')))
fc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def zmap(clip, z, x, y):
    f = FACES[clip]
    px, py = f['cx'], f['cy'] - 0.15 * f['size']
    return px + z * (x - px), py + z * (y - py)


def main():
    tl = edl.timeline()
    out = {}
    for s in tl.segs:
        c = s['clip']
        med = FACES[c]
        n = len(os.listdir(os.path.join(WS, 'frames', c)))
        track = []
        t = s['t0']
        while t < s['t1']:
            src = s['a'] + (t - s['t0'])
            idx = min(n - 1, int(round(src * edl.FPS)))
            im = cv2.imread(os.path.join(WS, 'frames', c, f'{idx:05d}.jpg'))
            g = cv2.cvtColor(cv2.resize(im, (540, 960)), cv2.COLOR_BGR2GRAY)
            fs = fc.detectMultiScale(g, 1.08, 5, minSize=(40, 40))
            fs = [(x * 2, y * 2, w * 2, h * 2) for x, y, w, h in fs
                  if abs(x * 2 + w - med['cx']) < 0.8 * med['size'] and abs(y * 2 + h - med['cy']) < 0.8 * med['size']]
            if fs:
                x, y, w, h = max(fs, key=lambda r: r[2] * r[3])
                q = (t - s['t0']) / max(1e-3, s['t1'] - s['t0'])
                z = s['zoom'] * (1 + 0.045 * q)
                x0, y0 = zmap(c, z, x - 0.06 * w, y - 0.32 * h)
                x1, y1 = zmap(c, z, x + 1.06 * w, y + 1.14 * h)
                track.append([round(t, 2), x0, y0, x1, y1])
            t += 0.25
        a = np.array([r[1:] for r in track])
        out[s['id']] = dict(left=float(np.percentile(a[:, 0], 3)), top=float(np.percentile(a[:, 1], 3)),
                            right=float(np.percentile(a[:, 2], 97)), bottom=float(np.percentile(a[:, 3], 97)),
                            n=len(track), track=track)
        r = out[s['id']]
        print(f"{s['id']:10s} n={len(track):3d}  face x {r['left']:.0f}-{r['right']:.0f}  y {r['top']:.0f}-{r['bottom']:.0f}")
    json.dump(out, open(os.path.join(WS, 'faces_seg.json'), 'w'))


if __name__ == '__main__':
    main()
