"""Background camera-motion track per shot (person masked out), so text placed
"behind" her stays pinned to the wall while the camera drifts.

Writes $WS/track.json: list of [dx, dy] per frame (output px, cumulative from
the first frame of its shot, smoothed).
"""
import json, sys
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d
from common import WS, SHOTS, NFRAMES, frame_path, matte_path, W

S = 360 / W   # tracking resolution / output resolution
# region of interest per shot (fractions of frame: x0, y0, x1, y1); default: whole frame
ROI = {4: (0.0, 0.0, 0.78, 0.7), 10: (0.0, 0.0, 0.6, 1.0)}


def gray(fi):
    g = cv2.cvtColor(cv2.imread(frame_path(fi)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = cv2.resize(g, (360, 640), interpolation=cv2.INTER_AREA)
    m = cv2.resize(cv2.imread(matte_path(fi), 0).astype(np.float32) / 255, (360, 640), interpolation=cv2.INTER_AREA)
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    bg = cv2.GaussianBlur(g, (0, 0), 25)
    return g * (1 - m) + bg * m


def main():
    track = np.zeros((NFRAMES, 2))
    win = None
    for k, (a, b) in enumerate(SHOTS):
        x0, y0, x1, y1 = ROI.get(k, (0, 0, 1, 1))
        sl = (slice(int(y0 * 640), int(y1 * 640)), slice(int(x0 * 360), int(x1 * 360)))
        prev = None
        acc = np.zeros(2)
        raw = []
        for fi in range(a, b):
            g = gray(fi)[sl]
            win = cv2.createHanningWindow(g.shape[::-1], cv2.CV_32F)
            if prev is not None:
                (dx, dy), r = cv2.phaseCorrelate(prev, g, win)
                if r > 0.05 and abs(dx) < 40 and abs(dy) < 40:
                    acc = acc + np.array([dx, dy]) / S
            raw.append(acc.copy())
            prev = g
        raw = np.array(raw)
        if len(raw) > 5:
            raw = gaussian_filter1d(raw, 2.0, axis=0, mode='nearest')
        track[a:b] = raw - raw[0]
        print('shot', k, 'max drift', np.abs(track[a:b]).max(0).round(1))
    json.dump(track.round(2).tolist(), open(f'{WS}/track.json', 'w'))


def jamb():
    """Shot 4 (prep room seen through a doorway): the out-of-focus door jamb in the
    foreground slides right across frame. Detect its left edge (smooth, light,
    texture-free band), fit a smooth path and save it so the renderer can treat it
    as an occluder in front of the big '8.5'."""
    a, b = SHOTS[4]
    xs, es = [], []
    for fi in range(a, min(b, a + 32)):
        g = cv2.cvtColor(cv2.imread(frame_path(fi)), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        g = cv2.resize(g, (360, 640), interpolation=cv2.INTER_AREA)
        gx = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3))
        tex = cv2.blur(gx, (9, 1))[60:420].mean(0)
        bri = g[60:420].mean(0)
        cand = (tex < 0.02) & (bri > 0.45)
        for x in range(120, 340):
            if cand[x:x + 25].mean() > 0.9:
                xs.append(fi)
                es.append(x / S)
                break
    c = np.polyfit(xs, es, 2)
    out = {}
    for fi in range(a, b):
        e = float(np.polyval(c, fi))
        if e < W + 40:
            out[fi] = round(e, 1)
    json.dump(out, open(f'{WS}/jamb.json', 'w'))
    print('jamb edge', {k: out[k] for k in list(out)[::6]})


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'jamb':
        jamb()
    else:
        main()
        jamb()
