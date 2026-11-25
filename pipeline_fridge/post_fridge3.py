"""OF static post "Can we put it on the fridge?" 1080x1350 (4:5), after the user's reference: a deep textured
(corduroy) colour field - OF plum here - a headline mixing bold caps with a light italic, a hand-drawn arrow, and a
framed photo. Brief: the drawing's corner breaks out of the frame (3D), official OF logo, no exclamation marks.

Usage: python3 post_fridge3.py
"""
import os, sys, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/reel/organic_fostering/can_we_put_it_on_the_fridge'
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350
PLUM = np.array((91, 23, 79), np.float32) / 255
IVORY = np.array((252, 248, 245), np.float32) / 255
ORANGE = np.array((255, 100, 17), np.float32) / 255
rng = np.random.default_rng(3)


def font(name, size):
    return ImageFont.truetype(f'{FON}/{name}.ttf', size)


def text_layer(s, f, track=0.0):
    """Text as a float alpha mask (tight box)."""
    asc, desc = f.getmetrics()
    w = int(f.getlength(s) + track * len(s) + 20)
    im = Image.new('L', (w, asc + desc + 20), 0)
    d = ImageDraw.Draw(im)
    x = 10
    for ch in s:
        d.text((x, 10), ch, font=f, fill=255)
        x += f.getlength(ch) + track
    a = np.asarray(im, np.float32) / 255
    ys, xs = np.where(a > 0.02)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def over(c, rgb, a, x, y):
    """Composite colour rgb with alpha mask a at top-left (x, y)."""
    h, w = a.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(c.shape[1], x + w), min(c.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    aa = a[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    reg = c[y0:y1, x0:x1]
    col = rgb if np.ndim(rgb) == 1 else rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    reg[:] = reg * (1 - aa) + col * aa


# ------------------------------------------------------------------ background: plum corduroy
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rib = 0.5 + 0.5 * np.cos(2 * np.pi * xx / 9.0)
rib = rib ** 1.6
colj = rng.normal(0, 1, W).astype(np.float32)
colj = np.convolve(colj, np.ones(3) / 3, 'same')[None, :]
fib = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=6)
lum = 0.8 + 0.22 * rib + 0.025 * colj + 0.03 * fib
light = 1.12 - 0.38 * np.hypot((xx - W * 0.42) / W, (yy - H * 0.18) / H)
bg = np.clip(PLUM[None, None] * 0.78 * (lum * light)[..., None], 0, 1)
c = bg.copy()

# ------------------------------------------------------------------ 3D poster: glow, an arch the fridge breaks out of, floating props
def load_rgba(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = im[..., 3:4]
    ys, xs = np.where(a[..., 0] > 0.02)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]])        # premultiplied RGB + alpha


def put(c, spr, cx, cy, size, rot=0.0, blur=0.0, shadow=0.35, a=1.0):
    h, w = spr.shape[:2]
    sc_ = size / max(h, w)
    D = int(math.hypot(w, h) * sc_) + 8
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, sc_)
    M[0, 2] += D / 2 - w / 2
    M[1, 2] += D / 2 - h / 2
    im = cv2.warpAffine(spr, M, (D, D), flags=cv2.INTER_AREA if sc_ < 1 else cv2.INTER_CUBIC)
    if blur:
        im = cv2.GaussianBlur(im, (0, 0), blur)
    x0, y0 = int(cx - D / 2), int(cy - D / 2)
    if shadow:
        sh = cv2.GaussianBlur(im[..., 3], (0, 0), 10 + blur) * shadow
        over(c, np.zeros(3, np.float32), sh, x0 + 14, y0 + 26)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + D), min(H, y0 + D)
    s_ = im[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    reg = c[Y0:Y1, X0:X1]
    reg[:] = reg * (1 - s_[..., 3:4] * a) + s_[..., :3] * a


# soft glow behind the hero (magenta into orange)
g = np.exp(-(((xx - 560) / 360) ** 2 + ((yy - 900) / 430) ** 2))
c = c * (1 - 0.35 * g[..., None]) + (np.array((0.72, 0.1, 0.45), np.float32) * 0.55 + np.array((1.0, 0.45, 0.1), np.float32) * 0.2) * 0.35 * g[..., None]
# the arch: ivory outline + a soft lilac panel with a floor, rounded top
AX0, AX1, AY0, AY1 = 190, 860, 600, 1285
R_ = (AX1 - AX0) / 2
cxA = (AX0 + AX1) / 2
inner = ((yy >= AY0 + R_) | (np.hypot(xx - cxA, yy - (AY0 + R_)) <= R_)) & (xx >= AX0) & (xx < AX1) & (yy < AY1) & (yy >= AY0)
inner_f = cv2.GaussianBlur(inner.astype(np.float32), (0, 0), 0.8)
outer = cv2.dilate(inner.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (37, 37))).astype(bool)
outer_f = cv2.GaussianBlur(outer.astype(np.float32), (0, 0), 0.8)
sh = cv2.GaussianBlur(np.roll(outer_f, 26, 0), (0, 0), 26) * 0.5
c = c * (1 - sh[..., None])
c = c * (1 - outer_f[..., None]) + IVORY * outer_f[..., None]
t = np.clip((yy - AY0) / (AY1 - AY0), 0, 1)
panel = np.array((246, 236, 242), np.float32) / 255 * (1.02 - 0.08 * t[..., None])
fl = yy > AY1 - 170
panel[fl] = np.array((232, 214, 222), np.float32) / 255 * (0.97 + 0.05 * ((yy[fl] - (AY1 - 170)) / 170))[..., None]
ish = np.clip(1 - cv2.GaussianBlur(inner.astype(np.float32), (0, 0), 16), 0, 1) * inner     # inner shadow
panel = panel * (1 - 0.25 * ish[..., None])
c = c * (1 - inner_f[..., None]) + panel * inner_f[..., None]
# orange offset outline (trend detail)
ring = cv2.dilate(inner.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))) - cv2.dilate(inner.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (55, 55)))
ring = np.roll(np.roll(ring, 16, 0), 16, 1).astype(np.float32)
ring = cv2.GaussianBlur(ring, (0, 0), 0.7) * (1 - outer_f)
c = c * (1 - ring[..., None]) + ORANGE * ring[..., None]

# props behind the arch (deep, blurred)
P = f'{ROOT}/workspace_fridge/props'
put(c, load_rgba(f'{P}/letter_o.png'), 1022, 520, 95, -14, blur=3.5, shadow=0.25)
put(c, load_rgba(f'{P}/star.png'), 105, 760, 120, 18, blur=2.5, shadow=0.25)

# the fridge: inside the arch everything (incl. its floor shadow); outside, only the fridge itself
fr = cv2.imread(f'{ROOT}/workspace_fridge/render2/fridge.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
fa = fr[..., 3:4]
frgb = fr[..., 2::-1]
ys, xs = np.where(fa[..., 0] > 0.9)
FH = 745
s = FH / (ys.max() - ys.min())
fcx, fby = 560, 1242
M = np.float32([[s, 0, fcx - s * (xs.min() + xs.max()) / 2], [0, s, fby - s * ys.max()]])
pm = np.dstack([frgb * fa, fa[..., 0]])
pm = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_AREA)
lum = pm[..., :3].mean(-1) / np.maximum(pm[..., 3], 1e-4)
obj = np.clip((lum - 0.12) / 0.15, 0, 1) * (pm[..., 3] > 0.02)
keep = np.where(inner, 1.0, obj)
keep[yy >= AY1] = 0
keep = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.6)
over_a = (pm[..., 3] * obj * (~inner)).astype(np.float32)
osh = cv2.GaussianBlur(np.roll(np.roll(over_a, 22, 0), 12, 1), (0, 0), 14) * 0.4
c = c * (1 - osh[..., None])
a_ = pm[..., 3:4] * keep[..., None]
c = c * (1 - a_) + pm[..., :3] * keep[..., None]

# props in front (sharp, close to the viewer)
put(c, load_rgba(f'{P}/crayon_orange.png'), 150, 1170, 300, 8, shadow=0.4)
put(c, load_rgba(f'{P}/heart.png'), 945, 1235, 175, -10, shadow=0.4)
put(c, load_rgba(f'{P}/crayon_green.png'), 1000, 960, 230, 95, blur=1.2, shadow=0.35)
put(c, load_rgba(f'{P}/letter_b.png'), 95, 1310, 120, -12, blur=1.5, shadow=0.3)

# ------------------------------------------------------------------ headline (mixed: bold caps + light italic)
X = 92
l1 = text_layer('CAN WE PUT IT', font('Nunito-900', 86), track=3)
Y1 = 218
over(c, IVORY, l1, X, Y1)
l2f = font('Nunito-Italic-300', 132)
l2 = text_layer('on the fridge?', l2f)
over(c, IVORY, l2, X - 4, Y1 + l1.shape[0] + 26)
# orange crayon-ish underline under "fridge"
fx0 = X - 4 + int(l2f.getlength('on the ')) + 6
fx1 = X - 4 + int(l2f.getlength('on the fridge')) - 4
uy = Y1 + l1.shape[0] + 26 + l2.shape[0] + 14
und = np.zeros((H, W), np.uint8)
pts = np.array([(fx0 + (fx1 - fx0) * t, uy + 6 * math.sin(t * 3.2) - 10 * t) for t in np.linspace(0, 1, 30)], np.float32)
cv2.polylines(und, [(pts * 4).astype(np.int32)], False, 255, 9, cv2.LINE_AA, shift=2)
m = und.astype(np.float32) / 255 * (0.75 + 0.25 * (rng.random((H, W)) > 0.3))
c = c * (1 - m[..., None]) + ORANGE * m[..., None]

ARROW_TO = (858.0, 772.0)
# hand-drawn arrow from the headline curling down to the card
def bez(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


a0, a3 = np.array((X + l1.shape[1] + 34, Y1 + 20.0)), np.array(ARROW_TO)
path = bez(a0, a0 + (120, -18), a3 + (95, -150), a3)
arr = np.zeros((H * 4, W * 4), np.uint8)
for i in range(len(path) - 1):
    wdt = int(4 * (2.2 + 2.6 * math.sin(math.pi * i / (len(path) - 1))))
    cv2.line(arr, tuple((path[i] * 4).astype(int)), tuple((path[i + 1] * 4).astype(int)), 255, wdt, cv2.LINE_AA)
d = path[-1] - path[-12]
d /= np.linalg.norm(d)
for sgn in (-1, 1):
    a = math.radians(150 * sgn)
    r = np.array((d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a)))
    cv2.line(arr, tuple((a3 * 4).astype(int)), tuple(((a3 + r * 44) * 4).astype(int)), 255, 22, cv2.LINE_AA)
arr = cv2.resize(arr, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
c = c * (1 - arr[..., None]) + IVORY * arr[..., None]

# ------------------------------------------------------------------ official logo (unmodified) on an ivory tab
logo = cv2.imread(f'{ROOT}/workspace_three/web/logo.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
LW = 250
logo = cv2.resize(logo, (LW, int(logo.shape[0] * LW / logo.shape[1])), interpolation=cv2.INTER_AREA)
lh = logo.shape[0]
pw, ph = LW + 56, lh + 30
pill = np.zeros((ph * 4, pw * 4), np.uint8)
cv2.rectangle(pill, (ph * 2, 0), (pw * 4 - ph * 2, ph * 4), 255, -1)
for x in (ph * 2, pw * 4 - ph * 2):
    cv2.circle(pill, (x, ph * 2), ph * 2, 255, -1, cv2.LINE_AA)
pill = cv2.resize(pill, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
over(c, IVORY, pill, (W - pw) // 2, 44)
over(c, logo[..., 2::-1], logo[..., 3], (W - LW) // 2, 44 + 15)

c = np.clip(c + rng.normal(0, 0.006, (H, W, 1)), 0, 1)
name = 'post_1080x1350.jpg'
cv2.imwrite(f'{OUT}/{name}', (c[..., ::-1] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
if True:
    cv2.imwrite(f'{OUT}/post_1080x1350.png', (c[..., ::-1] * 255 + 0.5).astype(np.uint8))
print('wrote', OUT, name)
