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
RD = f'{ROOT}/workspace_fridge/' + ('draft' if 'draft' in sys.argv else 'render')
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

# ------------------------------------------------------------------ the photo card with the frame-break
beauty = cv2.imread(f'{RD}/beauty.png')[..., ::-1].astype(np.float32) / 255
draw = cv2.imread(f'{RD}/drawing.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
Hr, Wr = beauty.shape[:2]
beauty = np.clip((beauty - 0.5) * 1.12 + 0.5, 0, 1) * np.array((1.03, 1.0, 0.95), np.float32)   # a touch warmer + crisper
beauty = np.clip(beauty, 0, 1)
da = draw[..., 3:4]
drgb = draw[..., 2::-1] * da                                   # premultiplied
cx0, cx1, cy0, cy1 = [int(v) for v in (Wr * 95 / 700, Wr * 585 / 700, Hr * 140 / 800, Hr * 730 / 800)]
CARD_W = 625                                                    # photo width on the post (px)
s = CARD_W / (cx1 - cx0)
bw = int(16 / s)                                                # ivory border, in render px
lay = np.zeros((Hr, Wr, 4), np.float32)
inside = np.zeros((Hr, Wr), np.float32)
inside[cy0:cy1, cx0:cx1] = 1
lay[cy0 - bw:cy1 + bw, cx0 - bw:cx1 + bw, :3] = IVORY
lay[cy0 - bw:cy1 + bw, cx0 - bw:cx1 + bw, 3] = 1
lay[cy0:cy1, cx0:cx1, :3] = beauty[cy0:cy1, cx0:cx1]
card_a = lay[..., 3].copy()
# the drawing's lifted corner, wherever it sits outside the photo (right half only)
pop = da[..., 0] * (1 - inside) * (np.arange(Wr)[None, :] > (cx0 + cx1) / 2)
sh = cv2.GaussianBlur(np.roll(np.roll(pop, int(14 / s), 0), int(8 / s), 1), (0, 0), 9 / s) * 0.45 * (1 - inside)
lay[..., :3] *= (1 - sh[..., None])
lay[..., 3] = np.maximum(lay[..., 3], sh)
lay[..., :3] = lay[..., :3] * (1 - pop[..., None]) + drgb * (pop[..., None] > 0) * (pop[..., None] / np.maximum(da, 1e-4))
lay[..., 3] = np.maximum(lay[..., 3], pop)
# premultiply for warping
pm = np.dstack([lay[..., :3] * lay[..., 3:4], lay[..., 3]])
ANG = 2.0
CC = (528, 905)
M = cv2.getRotationMatrix2D(((cx0 + cx1) / 2, (cy0 + cy1) / 2), ANG, s)
M[0, 2] += CC[0] - (cx0 + cx1) / 2
M[1, 2] += CC[1] - (cy0 + cy1) / 2
card = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
ca = cv2.warpAffine(card_a, M, (W, H), flags=cv2.INTER_LINEAR)
shadow = cv2.GaussianBlur(np.roll(ca, 22, 0), (0, 0), 22) * 0.55     # soft drop shadow of the card on the cloth
c = c * (1 - shadow[..., None])
c = c * (1 - card[..., 3:4]) + card[..., :3]

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

# hand-drawn arrow from the headline curling down to the card
def bez(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


a0, a3 = np.array((X + l1.shape[1] + 34, Y1 + 20.0)), np.array((905.0, 535.0))
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
name = 'draft.jpg' if 'draft' in sys.argv else 'post_1080x1350.jpg'
cv2.imwrite(f'{OUT}/{name}', (c[..., ::-1] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
if 'draft' not in sys.argv:
    cv2.imwrite(f'{OUT}/post_1080x1350.png', (c[..., ::-1] * 255 + 0.5).astype(np.uint8))
print('wrote', OUT, name)
