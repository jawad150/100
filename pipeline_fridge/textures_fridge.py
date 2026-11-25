"""Textures for the OF fridge post: the child's wonky crayon drawing, a school-letter sheet and a fridge snapshot."""
import os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = f'{ROOT}/workspace_fridge/tex'
FON = f'{ROOT}/workspace_sol/fonts'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def paper(w, h, col=(250, 247, 240)):
    a = np.ones((h, w, 3), np.float32) * np.array(col, np.float32) / 255
    n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.2) * 0.012
    return np.clip(a + n[..., None], 0, 1)


def crayon(img, pts, col, width=14, passes=4, jitter=4.0, alpha=0.75):
    """Waxy crayon stroke: several jittered passes through a grainy mask."""
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.float32)
    for _ in range(passes):
        p = np.array(pts, np.float32) + rng.normal(0, jitter, (len(pts), 2))
        lay = np.zeros((h, w), np.uint8)
        cv2.polylines(lay, [(p * 4).astype(np.int32)], False, 255, max(1, int(width * rng.uniform(0.7, 1.0))), cv2.LINE_AA, shift=2)
        m = np.maximum(m, lay.astype(np.float32) / 255 * rng.uniform(0.6, 1.0))
    grain = (rng.random((h, w)) > 0.33).astype(np.float32)
    grain = cv2.GaussianBlur(grain, (0, 0), 0.7)
    m = m * (0.45 + 0.55 * grain) * alpha
    img[:] = img * (1 - m[..., None]) + np.array(col, np.float32)[None, None] / 255 * m[..., None]


def scribble_fill(img, poly, col, step=12, width=10, ang=0.6):
    """Kid-style back-and-forth fill inside a polygon."""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)
    ys, xs = np.where(mask > 0)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pts = []
    d = 0
    for y in np.arange(y0 - (x1 - x0), y1 + (x1 - x0), step):
        a = (x0, y)
        b = (x1, y - (x1 - x0) * ang)
        pts += [a, b] if d % 2 == 0 else [b, a]
        d += 1
    tmp = img.copy()
    crayon(tmp, pts, col, width, passes=2, jitter=3, alpha=0.55)
    m = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 3)[..., None]
    m = np.clip(m * 1.4 - 0.1, 0, 1)
    img[:] = img * (1 - m) + tmp * m


def circle_pts(cx, cy, r, n=40, wob=0.06, start=0.0, turns=1.08):
    return [(cx + r * (1 + wob * math.sin(i * 1.7)) * math.cos(start + 2 * math.pi * turns * i / n),
             cy + r * (1 + wob * math.cos(i * 1.3)) * math.sin(start + 2 * math.pi * turns * i / n)) for i in range(n + 1)]


def drawing():
    W, H = 1600, 1200
    img = paper(W, H)
    PLUM, MAG, ORANGE, GREEN, YEL, BLUE, BROWN, SKIN = (91, 23, 79), (183, 0, 110), (255, 100, 17), (97, 168, 10), (255, 200, 30), (60, 120, 210), (130, 80, 40), (190, 120, 80)
    # sky scribble + sun
    for k in range(3):                                                      # sky: a few loose blue scribbles along the top
        crayon(img, [(40 + i * 40, 70 + k * 42 + 14 * math.sin(i * 0.9 + k)) for i in range(39)], (120, 180, 240), 16, passes=2)
    scribble_fill(img, circle_pts(1310, 230, 120, 30, 0.05), YEL, step=14, width=12)
    crayon(img, circle_pts(1310, 230, 125, 36, 0.05), ORANGE, 12)
    for i in range(9):
        a = i * 2 * math.pi / 9 + 0.2
        crayon(img, [(1310 + 160 * math.cos(a), 230 + 160 * math.sin(a)), (1310 + 240 * math.cos(a), 230 + 240 * math.sin(a))], ORANGE, 11)
    # grass
    scribble_fill(img, [(40, 980), (1560, 960), (1570, 1160), (40, 1170)], GREEN, step=16, width=13, ang=0.05)
    pts = [(40 + i * 30, 985 - (25 if i % 2 else 0) + rng.normal(0, 5)) for i in range(51)]
    crayon(img, pts, GREEN, 11)
    # house: wonky walls, plum roof, door, windows
    walls = [(180, 520), (690, 540), (700, 990), (170, 985)]
    scribble_fill(img, walls, (255, 160, 120), step=18, width=12)
    crayon(img, walls + [walls[0]], (200, 70, 40), 13)
    roof = [(130, 540), (440, 250), (760, 555)]
    scribble_fill(img, roof, PLUM, step=14, width=12)
    crayon(img, roof + [roof[0]], PLUM, 14)
    door = [(380, 990), (385, 760), (500, 755), (505, 990)]
    scribble_fill(img, door, BROWN, step=12, width=10)
    crayon(img, door, BROWN, 12)
    for wx, wy in ((240, 620), (560, 625)):
        win = [(wx, wy), (wx + 100, wy - 4), (wx + 104, wy + 95), (wx + 2, wy + 98), (wx, wy)]
        scribble_fill(img, win, YEL, step=12, width=9)
        crayon(img, win, BLUE, 10)
        crayon(img, [(wx + 52, wy), (wx + 52, wy + 96)], BLUE, 8)
    # chimney + smoke curl
    crayon(img, [(600, 430), (600, 330), (660, 330), (665, 480)], (200, 70, 40), 12)
    crayon(img, [(630 + 25 * math.sin(i / 3), 300 - i * 8) for i in range(22)], (150, 150, 160), 8)

    # two people holding hands: a tall one (carer) and a small one (me)
    def person(x, foot, h, body, hair):
        head = foot - h
        scribble_fill(img, circle_pts(x, head + 55, 55, 24, 0.04), SKIN, step=10, width=8)
        crayon(img, circle_pts(x, head + 55, 58, 30, 0.04), (110, 60, 40), 9)
        crayon(img, [(x - 60 + i * 8, head + 15 - 18 * math.sin(i / 15 * math.pi)) for i in range(16)], hair, 14)
        for ex in (-20, 20):
            crayon(img, circle_pts(x + ex, head + 48, 5, 8, 0.0), (40, 30, 30), 7, passes=2, jitter=1)
        crayon(img, [(x - 24 + i * 4, head + 72 + 12 * math.sin(i / 12 * math.pi)) for i in range(13)], (60, 30, 30), 6, passes=2, jitter=1)
        tri = [(x, head + 115), (x - 0.22 * h, foot - 0.25 * h), (x + 0.22 * h, foot - 0.25 * h)]
        scribble_fill(img, tri, body, step=12, width=10)
        crayon(img, tri + [tri[0]], body, 10)
        crayon(img, [(x - 0.08 * h, foot - 0.25 * h), (x - 0.1 * h, foot)], (40, 30, 30), 10)
        crayon(img, [(x + 0.08 * h, foot - 0.25 * h), (x + 0.1 * h, foot)], (40, 30, 30), 10)
        return head

    person(1000, 1000, 520, PLUM, (60, 40, 30))
    person(1250, 1005, 340, ORANGE, (40, 30, 25))
    crayon(img, [(1060, 700), (1130, 780), (1195, 800)], (110, 60, 40), 10)          # holding hands
    crayon(img, [(940, 700), (880, 790)], (110, 60, 40), 10)
    crayon(img, [(1305, 805), (1365, 760)], (110, 60, 40), 10)
    # heart between them + wobbly words
    hp = [(1125 + 60 * (16 * math.sin(t) ** 3) / 16, 470 - 60 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
          for t in np.linspace(0, 2 * math.pi, 40)]
    scribble_fill(img, hp, MAG, step=10, width=9)
    crayon(img, hp, MAG, 11)
    f = ImageFont.truetype(f'{FON}/Nunito-800.ttf', 120)
    x = 640
    for ch in 'ME + JO':
        adv = f.getlength(ch) + 10
        if ch != ' ':
            lay = Image.new('L', (170, 190), 0)
            ImageDraw.Draw(lay).text((25, 10), ch, font=f, fill=255)
            lay = lay.rotate(rng.uniform(-12, 12), resample=Image.BICUBIC)
            m = np.asarray(lay, np.float32) / 255
            grain = cv2.GaussianBlur((rng.random(m.shape) > 0.3).astype(np.float32), (0, 0), 0.7)
            mm = m * (0.45 + 0.55 * grain) * 0.85
            y0 = 120 + int(rng.normal(0, 14))
            x0 = int(x)
            reg = img[y0:y0 + 190, x0:x0 + 170]
            reg[:] = reg * (1 - mm[..., None]) + np.array(PLUM, np.float32) / 255 * mm[..., None]
        x += adv
    # paper edge shading + a fold crease
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.clip(img, 0, 1)
    cv2.imwrite(f'{OUT}/drawing.png', (img[..., ::-1] * 255).astype(np.uint8))


def letter():
    W, H = 800, 1100
    img = paper(W, H, (246, 246, 244))
    im = Image.fromarray((img * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(f'{FON}/Nunito-900.ttf', 54)
    f2 = ImageFont.truetype(f'{FON}/Nunito-400.ttf', 30)
    d.text((60, 60), 'Swimming - Tuesdays', font=f1, fill=(60, 60, 70))
    for i in range(14):
        y = 170 + i * 58
        d.rounded_rectangle([60, y, 60 + int(rng.uniform(380, 680)), y + 18], 9, fill=(190, 190, 195))
    d.text((60, 1000), 'Bring a towel + goggles', font=f2, fill=(120, 120, 130))
    im.save(f'{OUT}/letter.png')


def snapshot():
    src = cv2.imread(f'{ROOT}/workspace_frame/of/04-long-term-family-belonging.webp')
    h, w = src.shape[:2]
    s = min(h, w)
    crop = src[(h - s) // 2:(h - s) // 2 + s, (w - s) // 2:(w - s) // 2 + s]
    crop = cv2.resize(crop, (700, 700), interpolation=cv2.INTER_AREA)
    card = np.full((880, 780, 3), 246, np.uint8)
    card[40:740, 40:740] = crop
    cv2.imwrite(f'{OUT}/snapshot.png', card)


if __name__ == '__main__':
    drawing()
    letter()
    snapshot()
    print('textures done')
