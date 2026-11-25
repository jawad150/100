"""OF static post "Can we put it on the fridge?" 1080x1350 (4:5), after the user's reference: a deep textured
(corduroy) colour field - OF plum here - a headline mixing bold caps with a light italic, a hand-drawn arrow, and a
framed photo. Brief: the drawing's corner breaks out of the frame (3D), official OF logo, no exclamation marks.

Usage: python3 post_fridge.py [draft]
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

# ------------------------------------------------------------------ the frame + the 3D fridge breaking out of it
FX0, FX1, FY0, FY1, BW = 110, 760, 610, 1290, 16
yy2, xx2 = yy, xx
inner = (xx2 >= FX0) & (xx2 < FX1) & (yy2 >= FY0) & (yy2 < FY1)
outer = (xx2 >= FX0 - BW) & (xx2 < FX1 + BW) & (yy2 >= FY0 - BW) & (yy2 < FY1 + BW)
sh = cv2.GaussianBlur(np.roll(outer.astype(np.float32), 24, 0), (0, 0), 24) * 0.5
c = c * (1 - sh[..., None])
c[outer] = IVORY
# soft kitchen wall: warm lilac-ivory, morning window light falling across it, a floor line
WALL = np.array((243, 232, 236), np.float32) / 255
FLOOR = np.array((226, 210, 200), np.float32) / 255
t = np.clip((yy2 - FY0) / (FY1 - FY0), 0, 1)
wall = WALL * (1.03 - 0.1 * t[..., None])
fl = yy2 > FY1 - 150
wall[fl] = FLOOR * (0.96 + 0.06 * ((yy2[fl] - (FY1 - 150)) / 150))[..., None]
win = np.zeros((H, W), np.float32)
for k in range(2):
    for j in range(2):
        x0, y0 = FX0 + 40 + k * 150, FY0 + 30 + j * 170
        pts = np.array([(x0, y0), (x0 + 130, y0 - 40), (x0 + 210, y0 + 110), (x0 + 80, y0 + 150)], np.int32)
        cv2.fillPoly(win, [pts], 1.0)
win = cv2.GaussianBlur(win, (0, 0), 6) * (~fl)
wall = wall + win[..., None] * np.array((0.05, 0.035, 0.0), np.float32)
wall = np.clip(wall, 0, 1)
c[inner] = wall[inner]
# the fridge render: inside the frame everything (incl. its floor shadow); outside, only the fridge itself
fr = cv2.imread(f'{ROOT}/workspace_fridge/render2/fridge.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
fa = fr[..., 3:4]
frgb = fr[..., 2::-1]
ys, xs = np.where(fa[..., 0] > 0.9)
FH = 790                                                         # fridge height on the post
s = FH / (ys.max() - ys.min())
fcx, fby = 598, 1252                                             # centre x, feet line
M = np.float32([[s, 0, fcx - s * (xs.min() + xs.max()) / 2], [0, s, fby - s * ys.max()]])
pm = np.dstack([frgb * fa, fa[..., 0]])
pm = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_AREA)
lum = pm[..., :3].mean(-1) / np.maximum(pm[..., 3], 1e-4)
obj = np.clip((lum - 0.12) / 0.15, 0, 1) * (pm[..., 3] > 0.02)
keep = np.where(inner, 1.0, obj)
keep[yy2 >= FY1] = 0
keep = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.6)
a_ = pm[..., 3:4] * keep[..., None]
c = c * (1 - a_) + pm[..., :3] * keep[..., None]
# contact shadow of the part that hangs over the frame's border onto the cloth
over_a = (pm[..., 3] * obj * (~inner)).astype(np.float32)
osh = cv2.GaussianBlur(np.roll(np.roll(over_a, 16, 0), 10, 1), (0, 0), 12) * 0.35 * (~outer | inner == False)
c = c * (1 - (osh * (1 - over_a))[..., None])

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

ARROW_TO = (900.0, 840.0)
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
d = path[-1] - path[-6]
d /= np.linalg.norm(d)
for sgn in (-1, 1):
    a = math.radians(150 * sgn)
    r = np.array((d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a)))
    cv2.line(arr, tuple((a3 * 4).astype(int)), tuple(((a3 + r * 34) * 4).astype(int)), 255, 18, cv2.LINE_AA)
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
