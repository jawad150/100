# /// script
# dependencies = ["numpy", "opencv-python-headless", "pillow"]
# ///
import numpy as np, cv2, sys
from PIL import Image
src = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
H, W = src.shape[:2]
BX, BY, BW, BH = 770, 330, 340, 360
S = 4                                         # work at 4x
crop = cv2.resize(src[BY:BY+BH, BX:BX+BW], (BW*S, BH*S), interpolation=cv2.INTER_LANCZOS4)
h, w = crop.shape[:2]
rng = np.random.default_rng(7)

# --- skin mask: YCrCb skin tones inside a hand-placed head/neck region, feathered
ycc = cv2.cvtColor(np.clip(crop,0,255).astype(np.uint8), cv2.COLOR_RGB2YCrCb).astype(np.float32)
Y, Cr, Cb = ycc[...,0], ycc[...,1], ycc[...,2]
skin = ((Cr > 141) & (Cr < 178) & (Cb > 85) & (Cb < 124) & (Y > 55) & (Y < 222)).astype(np.float32)
skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3*S, 3*S), np.uint8))
region = np.zeros((h, w), np.float32)
cv2.ellipse(region, (int(158*S), int(132*S)), (int(62*S), int(78*S)), 0, 0, 360, 1, -1)   # face
cv2.ellipse(region, (int(200*S), int(185*S)), (int(34*S), int(28*S)), 0, 0, 360, 1, -1)   # neck
cv2.ellipse(region, (int(212*S), int(110*S)), (int(16*S), int(22*S)), 0, 0, 360, 1, -1)   # ear
m = cv2.GaussianBlur(skin * region, (0, 0), 2.5*S)
m = np.clip(m * 1.3, 0, 1)

# --- 1) pores + fine skin texture (multi-scale, luminance only)
def band(sigma, amp):
    n = rng.standard_normal((h, w)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), sigma); n /= n.std() + 1e-6
    return n * amp
tex = band(0.9*S/2, 1.0) + band(1.8*S/2, 0.8) + band(4*S/2, 0.45)
# pores: sparse small dark dots
dots = (rng.random((h, w)) > 0.9965).astype(np.float32)
dots = cv2.GaussianBlur(dots, (0, 0), 0.9*S/2); dots /= dots.max() + 1e-6
lum = crop.mean(axis=2, keepdims=True)
crop = crop + (tex[..., None] * 2.5 - dots[..., None] * 11) * m[..., None] * np.clip(lum / 180, 0.4, 1.2)

# --- 2) natural tone variation: faint blotchy redness on cheeks/nose, slight unevenness
blot = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 14*S/2); blot /= blot.std()
red = np.zeros((h, w), np.float32)
cv2.ellipse(red, (int(135*S), int(140*S)), (int(22*S), int(16*S)), 0, 0, 360, 1, -1)   # cheek
cv2.ellipse(red, (int(122*S), int(150*S)), (int(9*S), int(9*S)), 0, 0, 360, 0.8, -1)   # nose tip
red = cv2.GaussianBlur(red, (0, 0), 8*S)
crop[..., 0] += (red * 3.5 + blot * 1.2) * m
crop[..., 1] -= (red * 1.5) * m
crop[..., 2] -= (red * 1.0) * m

# --- 3) micro-contrast: bring back stubble, brows, lashes, lip line (detail layer, face only)
blur = cv2.GaussianBlur(crop, (0, 0), 1.6*S)
detail = crop - blur
fm = np.zeros((h, w), np.float32)
cv2.ellipse(fm, (int(158*S), int(132*S)), (int(66*S), int(82*S)), 0, 0, 360, 1, -1)
fm = cv2.GaussianBlur(fm, (0, 0), 6*S)
crop = crop + detail * 0.55 * fm[..., None]

# --- 4) soften the waxy specular sheen slightly (AI skin often over-glossy)
hi = np.clip((lum[..., 0] - 205) / 40, 0, 1) * m
crop = crop - hi[..., None] * 8

# back to original scale, then camera-like grain over the person so the face isn't cleaner than the rest
out = cv2.resize(crop, (BW, BH), interpolation=cv2.INTER_AREA)
pm = cv2.resize(cv2.GaussianBlur(region, (0, 0), 6*S), (BW, BH), interpolation=cv2.INTER_AREA)
pm = np.clip(pm * 1.15, 0, 1)
grain = cv2.GaussianBlur(rng.standard_normal((BH, BW)).astype(np.float32), (0, 0), 0.6) * 2.2
ms = cv2.resize(m, (BW, BH), interpolation=cv2.INTER_AREA)
out = out + grain[..., None] * ms[..., None]
res = src.copy()
orig = src[BY:BY+BH, BX:BX+BW]
fmask = np.clip(np.maximum(ms * 1.2, cv2.resize(cv2.GaussianBlur(fm, (0, 0), 2*S), (BW, BH)) * 0.0), 0, 1)
fmask = np.clip(cv2.GaussianBlur(np.maximum(ms, cv2.resize(fm, (BW, BH)) * (ms > 0.02)), (0, 0), 1.2) * 1.2, 0, 1)
res[BY:BY+BH, BX:BX+BW] = orig * (1 - fmask[..., None]) + out * fmask[..., None]
res = np.clip(res, 0, 255).astype(np.uint8)
Image.fromarray(res).save(sys.argv[2])
# before/after of the head at 3x for review
a = Image.fromarray(src[BY+40:BY+250, BX+60:BX+260].astype(np.uint8)).resize((600, 630), Image.LANCZOS)
b = Image.fromarray(res[BY+40:BY+250, BX+60:BX+260]).resize((600, 630), Image.LANCZOS)
cmp = Image.new('RGB', (1210, 630), 'white'); cmp.paste(a, (0, 0)); cmp.paste(b, (610, 0)); cmp.save(sys.argv[3])
print('changed pixels outside head box:', int((np.abs(res.astype(int) - src.astype(int)).sum(2) > 0)[:BY].sum()))
