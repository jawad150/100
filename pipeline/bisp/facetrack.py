"""Face box of the presenter per segment, in OUTPUT coordinates (segment zoom + slow push-in applied).

    python3 facetrack.py   -> workspace_bisp/faces_seg.json  {seg_id: {top, bottom, left, right, track: [[t, x0, y0, x1, y1]...]}}

The face box is the Haar box widened to forehead (-0.32 h) and chin (+1.14 h). The protected ZONE adds the hair
and neck around it (-0.60 h .. +1.55 h, 0.35 w either side): graphics never enter the zone (reel.py bands)."""
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
                z = tl.zoom_at(s, t)
                x0, y0 = zmap(c, z, x - 0.06 * w, y - 0.32 * h)
                x1, y1 = zmap(c, z, x + 1.06 * w, y + 1.14 * h)
                X0, Y0 = zmap(c, z, x - 0.35 * w, y - 0.60 * h)
                X1, Y1 = zmap(c, z, x + 1.35 * w, y + 1.55 * h)
                track.append([round(t, 2), x0, y0, x1, y1, X0, Y0, X1, Y1])
            t += 0.2
        a = np.array([r[1:] for r in track])
        # protected ZONE around the face: hair top (-0.60 h) to below the neck (+1.55 h), 0.35 w either side; the
        # extremes over the whole segment (outliers whose size is >35 % off the median are dropped), so nothing that
        # moves in or out can ever sit on her head or neck.
        zs = np.array([r[5:] for r in track])
        hs = zs[:, 3] - zs[:, 1]
        ok = np.abs(hs / np.median(hs) - 1) < 0.35
        zs = zs[ok]
        out[s['id']] = dict(left=float(np.percentile(a[:, 0], 3)), top=float(np.percentile(a[:, 1], 3)),
                            right=float(np.percentile(a[:, 2], 97)), bottom=float(np.percentile(a[:, 3], 97)),
                            zone=[float(zs[:, 0].min()), float(zs[:, 1].min()), float(zs[:, 2].max()), float(zs[:, 3].max())],
                            n=len(track), track=[r[:5] for r in track], ztrack=[[r[0]] + r[5:] for r in track])
        r = out[s['id']]
        z = r['zone']
        print(f"{s['id']:10s} n={len(track):3d}  face y {r['top']:.0f}-{r['bottom']:.0f}   ZONE x {z[0]:.0f}-{z[2]:.0f} y {z[1]:.0f}-{z[3]:.0f}")
    json.dump(out, open(os.path.join(WS, 'faces_seg.json'), 'w'))


if __name__ == '__main__':
    main()
