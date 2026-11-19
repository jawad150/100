# /// script
# dependencies = ["numpy", "opencv-python-headless", "pillow"]
# ///
import numpy as np, cv2, sys
from PIL import Image
src = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
X0, Y0, X1, Y1 = 880, 440, 1000, 535
S = 6
crop = cv2.resize(src[Y0:Y1, X0:X1], ((X1-X0)*S, (Y1-Y0)*S), interpolation=cv2.INTER_CUBIC)
h, w = crop.shape[:2]
P = lambda pts: (np.array([[(x - X0) * S, (y - Y0) * S] for x, y in pts], np.int32))
rng = np.random.default_rng(11)

# beard region (hand traced from the 6x view), lips cut out, edge broken up with noise
beard = np.zeros((h, w), np.float32)
cv2.fillPoly(beard, [P([(932, 467), (948, 463), (964, 463), (976, 471), (984, 487), (982, 502), (970, 513), (950, 520), (930, 519), (918, 512), (912, 503), (904, 495), (901, 487), (906, 482), (918, 480), (927, 475)])], 1)
lips = np.zeros((h, w), np.float32)
cv2.fillPoly(lips, [P([(900, 488), (912, 486), (924, 489), (928, 494), (920, 498), (908, 497), (902, 494)])], 1)
beard = np.clip(beard - cv2.GaussianBlur(lips, (0, 0), 1.0 * S) * 1.6, 0, 1)
edge_noise = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 1.5 * S); edge_noise /= edge_noise.std()
bm = cv2.GaussianBlur(beard, (0, 0), 2.2 * S)
bm = np.clip((bm - 0.5 + 0.15 * edge_noise) * 1.8 + 0.5, 0, 1)

# keep the beard's own shape and darkness (low frequencies); drop only the painted swirl texture
base = cv2.GaussianBlur(crop, (0, 0), 1.5 * S)
lum = base.mean(2)
around = cv2.GaussianBlur(crop.mean(2), (0, 0), 9 * S)              # local skin level
dens = np.clip((around - lum) / 45.0 + 0.25, 0, 1) * bm            # where the beard is, and how thick

# hairs: short tapered strokes along the growth pattern
hair = np.zeros((h, w), np.float32)
def growth(x, y):
    if y < 492 and x < 932: return np.deg2rad(112)
    if x > 962: return np.deg2rad(92 - (x - 962) * 0.9)
    return np.deg2rad(100)
n = 0
ys, xs = np.where(dens > 0.05)
idx = rng.choice(len(xs), size=min(len(xs), 30000), replace=False)
for i in idx:
    y, x = ys[i], xs[i]
    if rng.random() > dens[y, x]: continue
    ox, oy = X0 + x / S, Y0 + y / S
    a = growth(ox, oy) + rng.normal(0, 0.3)
    L = (1.0 + rng.random() * 1.8) * S
    cv2.line(hair, (int(x), int(y)), (int(x + np.cos(a) * L), int(y + np.sin(a) * L)), float(0.6 + 0.4 * rng.random()), 1, cv2.LINE_AA)
    n += 1
hair = cv2.GaussianBlur(hair, (0, 0), 0.3 * S)
tex = hair - cv2.GaussianBlur(hair, (0, 0), 1.2 * S)               # zero-mean: texture, not extra darkness
tex /= (np.abs(tex)[dens > 0.2].mean() + 1e-6)
pores = rng.standard_normal((h, w)).astype(np.float32); pores = cv2.GaussianBlur(pores, (0, 0), 0.4 * S); pores /= pores.std()
canvas = base - tex[..., None] * 15 * dens[..., None] + pores[..., None] * 2.0 * bm[..., None]
canvas = crop * (1 - bm[..., None]) + canvas * bm[..., None]
out = cv2.resize(canvas, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
fm = cv2.resize(np.clip(bm * 1.2, 0, 1), (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
res = src.copy()
res[Y0:Y1, X0:X1] = src[Y0:Y1, X0:X1] * (1 - fm[..., None]) + out * fm[..., None]
res = np.clip(res, 0, 255).astype(np.uint8)
Image.fromarray(res).save(sys.argv[2])
a = Image.open(sys.argv[1]).convert('RGB').crop((860, 400, 1010, 540)).resize((600, 560), Image.LANCZOS)
b = Image.fromarray(res).crop((860, 400, 1010, 540)).resize((600, 560), Image.LANCZOS)
c = Image.new('RGB', (1210, 560), 'white'); c.paste(a, (0, 0)); c.paste(b, (610, 0)); c.save(sys.argv[3])
print('hairs drawn', n)
