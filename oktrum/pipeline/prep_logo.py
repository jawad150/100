"""Split the Oktrum logo (workspace/src/logo.png) into mark + wordmark sprites and
trace the wordmark outline for the Blender extrusion (workspace/logo_contours.json)."""
import os, json
import numpy as np
import cv2

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
os.makedirs(S + '/assets', exist_ok=True)

im = cv2.imread(S + '/src/logo.png', cv2.IMREAD_UNCHANGED)          # BGRA, transparent bg
a = im[..., 3]
ys, xs = np.where(a > 12)
im = im[ys.min() - 4:ys.max() + 5, xs.min() - 4:xs.max() + 5]
a = im[..., 3]
# split mark | wordmark at the widest empty column gap in the left third
cols = (a > 12).sum(0)
on = np.where(cols > 0)[0]
gaps = np.diff(on)
gi = int(np.argmax(gaps[:len(gaps) // 2]))
split = int((on[gi] + on[gi + 1]) / 2)
cv2.imwrite(S + '/assets/logo_full.png', im)
mark, word = im[:, :split], im[:, split:]

def trim(x):
    yy, xx = np.where(x[..., 3] > 12)
    return x[yy.min() - 3:yy.max() + 4, xx.min() - 3:xx.max() + 4]

mark, word = trim(mark), trim(word)
cv2.imwrite(S + '/assets/logo_mark.png', mark)
cv2.imwrite(S + '/assets/logo_word.png', word)

# white wordmark (for colour-flexible use) — alpha only
ww = np.zeros_like(word); ww[..., :3] = 255; ww[..., 3] = word[..., 3]
cv2.imwrite(S + '/assets/logo_word_white.png', ww)

# contours of the wordmark (upsampled + smoothed for clean curves)
K = 6
m = word[..., 3].astype(np.float32)
up = cv2.GaussianBlur(cv2.resize(m, None, fx=K, fy=K, interpolation=cv2.INTER_CUBIC), (0, 0), K * 0.6)
th = (up > 127).astype(np.uint8) * 255
H, W = th.shape
cnts, hier = cv2.findContours(th, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
out = []
for c in cnts:
    if cv2.contourArea(c) < 200:
        continue
    p = cv2.approxPolyDP(c, 1.2, True)[:, 0, :].astype(float)
    out.append([[(x - W / 2) / H, -(y - H / 2) / H] for x, y in p])
json.dump({'contours': out, 'aspect': W / H}, open(S + '/logo_contours.json', 'w'))
print('mark', mark.shape, 'word', word.shape, 'contours', len(out), 'aspect', round(W / H, 3))
