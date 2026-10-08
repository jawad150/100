"""Face track of the talent (OpenCV Haar), smoothed; drives punch-in framing and the tracking box."""
import json, sys
import numpy as np, cv2

cap = cv2.VideoCapture(sys.argv[1])
cas = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
raw, i = [], 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    if i % 3 == 0:
        g = cv2.cvtColor(cv2.resize(f, (540, 960)), cv2.COLOR_BGR2GRAY)
        fs = cas.detectMultiScale(g, 1.08, 5, minSize=(30, 30))
        if len(fs):
            x, y, w, h = max(fs, key=lambda r: r[2] * r[3])
            raw.append((i, (x + w / 2) * 2, (y + h / 2) * 2, w * 2))
    i += 1
n = i
idx = np.array([r[0] for r in raw]); arr = np.array([r[1:] for r in raw])
med = np.median(arr, 0)
keep = np.all(np.abs(arr - med) < [120, 120, 60], 1)
idx, arr = idx[keep], arr[keep]
tr = np.stack([np.interp(np.arange(n), idx, arr[:, k]) for k in range(3)], 1)
k = 15
ker = np.ones(k) / k
tr = np.stack([np.convolve(np.pad(tr[:, c], k // 2, mode='edge'), ker, 'valid')[:n] for c in range(3)], 1)
json.dump(dict(n=n, median=med.tolist(), track=np.round(tr, 1).tolist()), open(sys.argv[2], 'w'))
print('frames', n, 'detections', len(raw), 'kept', keep.sum(), 'median', med)
