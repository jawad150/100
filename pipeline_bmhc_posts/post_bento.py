"""BMHC static post 1 "Everything under one roof" - 3D bento grid (Pinterest-style glossy 3D icons in a bento layout),
1080 x 1350 (4:5). Brand: ink ground, Inter ExtraBold caps headline, Inter Medium/Regular, tag top-left, reversed
logo, four-bar strip; approved pairings (white on magenta / ink; ink on the light tiles).
-> reel/bmhc/static_everything_under_one_roof/post_1080x1350.png/.jpg"""
import os, math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
A = f'{ROOT}/workspace_bmhc_posts/assets'
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/reel/bmhc/static_everything_under_one_roof'
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350


def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


INK, CHAR, SLATE, STONE, MIST, WHITE = hx('#0B0B0B'), hx('#1F1F1F'), hx('#5C5C5C'), hx('#E9E6DF'), hx('#F6F5F1'), hx('#FFFFFF')
MAG, TEAL, ORANGE, LIME = hx('#E60585'), hx('#2DC892'), hx('#FF4200'), hx('#69FF00')


def F(w, s):
    return ImageFont.truetype(f'{FON}/Inter-{w}.ttf', int(s))


def text(s, w, size, col, track=0.0):
    f = F(w, size)
    asc, desc = f.getmetrics()
    widths = [f.getlength(ch) for ch in s]
    tw = sum(widths) + track * size * (len(s) - 1)
    im = Image.new('L', (int(tw + 20), asc + desc + 20), 0)
    d = ImageDraw.Draw(im)
    x = 10
    for ch, cw in zip(s, widths):
        d.text((x, 10), ch, font=f, fill=255)
        x += cw + track * size
    a = np.asarray(im, np.float32) / 255
    ys, xs = np.where(a > 0.01)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.dstack([a[..., None] * np.array(col, np.float32), a])


def paste(c, spr, x, y, a=1.0, anchor='tl'):
    sh, sw = spr.shape[:2]
    if anchor == 'c':
        x, y = x - sw / 2, y - sh / 2
    x0, y0 = int(round(x)), int(round(y))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(c.shape[1], x0 + sw), min(c.shape[0], y0 + sh)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = s[..., 3:4] * a
    c[Y0:Y1, X0:X1] = c[Y0:Y1, X0:X1] * (1 - al) + s[..., :3] * a


def rrect_mask(w, h, r):
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.rectangle(m, (r * 4, 0), ((w - r) * 4, h * 4), 255, -1)
    cv2.rectangle(m, (0, r * 4), (w * 4, (h - r) * 4), 255, -1)
    for x in (r, w - r):
        for y in (r, h - r):
            cv2.circle(m, (x * 4, y * 4), r * 4, 255, -1, cv2.LINE_AA)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


@functools.lru_cache(None)
def obj(name, size):
    im = cv2.imread(f'{A}/{name}.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    solid = (im[..., 3] > 0.5).astype(np.uint8)                        # drop the faint shadow-catcher haze around the object
    keep = cv2.GaussianBlur(cv2.dilate(solid, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2)
    im[..., 3] *= np.clip(keep * 1.2, 0, 1)
    im[..., :3] *= np.clip(keep * 1.2, 0, 1)[..., None]
    a = im[..., 3]
    ys, xs = np.where(a > 0.5)
    pad = 30
    im = im[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    sc = size / max(ys.max() - ys.min(), xs.max() - xs.min())
    im = cv2.resize(im, (int(im.shape[1] * sc), int(im.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


def put_obj(c, name, cx, cy, size, rot=0.0, glow=None, shadow=0.55):
    spr = obj(name, size)
    if rot:
        h, w = spr.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0)
        spr = cv2.warpAffine(spr, M, (w, h))
    h, w = spr.shape[:2]
    x0, y0 = cx - w / 2, cy - h / 2
    if glow is not None:                                                 # soft coloured glow behind the object
        p = int(size * 0.5)
        g = cv2.GaussianBlur(np.pad(spr[..., 3], p), (0, 0), size * 0.14) * 0.55
        paste(c, np.dstack([g[..., None] * np.array(glow, np.float32), g]), x0 - p, y0 - p)
    if shadow:                                                           # contact shadow under it
        sh = np.zeros((int(h * 0.3) + 40, w), np.float32)
        cv2.ellipse(sh, (w // 2, 20 + int(h * 0.05)), (int(w * 0.33), int(h * 0.055)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        sh = cv2.GaussianBlur(sh, (0, 0), 12) * shadow
        paste(c, np.dstack([np.zeros(sh.shape + (3,), np.float32), sh]), x0, y0 + h * 0.84)
    paste(c, spr, x0, y0)


# ------------------------------------------------------------------ ground
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
c = np.empty((H, W, 3), np.float32)
c[:] = INK
g = np.exp(-(((xx - 540) / 620) ** 2 + ((yy - 760) / 620) ** 2))
c = c + g[..., None] * np.array((0.07, 0.065, 0.075), np.float32)
dots = ((xx.astype(int) % 36 == 18) & (yy.astype(int) % 36 == 18)).astype(np.float32)
c = c + cv2.GaussianBlur(dots, (0, 0), 0.8)[..., None] * 0.05

# ------------------------------------------------------------------ header
X = 58
tg = text('COMMUNITY', 800, 22, tuple(INK), 0.12)
pw, ph = tg.shape[1] + 34, tg.shape[0] + 22
paste(c, np.dstack([rrect_mask(pw, ph, 8)[..., None] * WHITE, rrect_mask(pw, ph, 8)]), X, 56)
paste(c, tg, X + 17, 56 + 11)
logo = cv2.imread(f'{ROOT}/workspace_bmhc/web/img/bmhc-white-logo.png', cv2.IMREAD_UNCHANGED)
if logo.shape[2] == 3:
    g_ = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    logo = np.dstack([logo, np.clip((g_.astype(np.float32) - 40) * 2, 0, 255).astype(np.uint8)])
logo = logo.astype(np.float32) / 255
LW = 250
logo = cv2.resize(logo, (LW, int(logo.shape[0] * LW / logo.shape[1])), interpolation=cv2.INTER_AREA)
paste(c, np.dstack([logo[..., 2::-1] * logo[..., 3:4], logo[..., 3]]), W - X - LW, 40)

h1 = text('EVERYTHING', 800, 98, tuple(WHITE), 0.02)
paste(c, h1, X, 150)
h2a = text('UNDER ', 800, 98, tuple(WHITE), 0.02)
h2b = text('ONE ROOF', 800, 98, tuple(MAG), 0.02)
paste(c, h2a, X, 150 + h1.shape[0] + 22)
paste(c, h2b, X + h2a.shape[1] + 30, 150 + h1.shape[0] + 22)
sub = text('Seven doors. One address in Whalley Range.', 500, 30, tuple(hx('#BDBDBD')))
paste(c, sub, X, 150 + 2 * h1.shape[0] + 62)

# ------------------------------------------------------------------ bento grid
GX0, GY0, GAP = 58, 440, 18
CW = (W - 2 * GX0 - 2 * GAP) // 3
RH = 248
TILES = [  # col, row, colspan, rowspan, fill, title, sub, text colour, object, size, centre (px from tile top-right), glow
    (0, 0, 2, 1, CHAR, 'Daily prayers', '& Friday Jummah', WHITE, 'lantern', 250, (-150, 105), TEAL),
    (2, 0, 1, 1, CHAR, "Qur'an", 'classes for all ages', WHITE, 'rehal', 175, (-100, 62), LIME),
    (0, 1, 1, 2, MAG, 'Imam', 'counselling', WHITE, 'bubbles', 235, (-156, 190), None),
    (1, 1, 1, 1, CHAR, 'Youth', 'clubs & sport', WHITE, 'ball', 135, (-88, 58), ORANGE),
    (2, 1, 1, 1, CHAR, '90.6 FM', 'Heritage Radio', WHITE, 'radio', 165, (-98, 54), ORANGE),
    (1, 2, 1, 1, CHAR, 'Heritage', 'tours & Umrah', WHITE, 'mappin', 165, (-96, 56), MAG),
    (2, 2, 1, 1, CHAR, 'Nikah', 'ceremonies', WHITE, 'rings', 150, (-92, 60), hx('#E2B04A')),
]
for col, row, cs, rs, fill, title, subt, tcol, name, osz, (dx, dy), glow in TILES:
    x0 = GX0 + col * (CW + GAP)
    y0 = GY0 + row * (RH + GAP)
    w = CW * cs + GAP * (cs - 1)
    h = RH * rs + GAP * (rs - 1)
    m = rrect_mask(w, h, 34)
    # tile: soft top-light gradient + thin rim
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    tile = fill[None, None] * (1.08 - 0.12 * t) if fill is CHAR else fill[None, None] * (1.04 - 0.1 * t)
    rim = np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8)), 0, 1)
    tile = tile * np.ones((h, w, 3), np.float32) + rim[..., None] * 0.08
    sh = cv2.GaussianBlur(np.pad(m, 30), (0, 0), 14) * 0.5
    paste(c, np.dstack([np.zeros(sh.shape + (3,), np.float32), sh]), x0 - 30, y0 - 30 + 12)
    paste(c, np.dstack([tile * m[..., None], m]), x0, y0)
    tt = text(title, 800, 44, tuple(tcol))
    st = text(subt, 500, 28, tuple(tcol * 0.78 + (0.0 if fill is MAG else 0.0)))
    paste(c, tt, x0 + 28, y0 + h - 30 - st.shape[0] - 14 - tt.shape[0])
    paste(c, st, x0 + 28, y0 + h - 30 - st.shape[0])
    put_obj(c, name, x0 + w + dx, y0 + dy, osz, glow=glow, shadow=0.5 if fill is CHAR else 0.35)

# ------------------------------------------------------------------ footer + four bars
ft = text('College Road, Whalley Range  ·  bmhc.org.uk', 500, 28, tuple(hx('#9A9A9A')))
paste(c, ft, X, 1262)
bars = (MAG, TEAL, ORANGE, LIME)
for i, col in enumerate(bars):
    c[H - 16:, int(W * i / 4):int(W * (i + 1) / 4)] = col

rng = np.random.default_rng(2)
c = np.clip(c + rng.normal(0, 0.006, (H, W, 1)).astype(np.float32), 0, 1)
img = (c[..., ::-1] * 255 + 0.5).astype(np.uint8)
cv2.imwrite(f'{OUT}/post_1080x1350.png', img)
cv2.imwrite(f'{OUT}/post_1080x1350.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 95])
print('wrote', OUT)
