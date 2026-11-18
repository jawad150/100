"""Organic Fostering "Don't swipe" carousel (5 slides, 1080x1350 each, seamless).

Little 3D houses with window-eyes watch you swipe; a magenta path runs through all five slides from house to house;
the last slide is a heart made of 3D fostering objects. Built as one 5400x1350 panorama, then cut into slides.
Brand: Nunito ExtraBold, plum ink on warm ivory, magenta/orange/green accents, no exclamation marks.

Usage: python3 compose_swipe.py -> workspace_swipe/slides/slide_1..5.png/.jpg + strip.jpg
"""
import os, math, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
A = f'{ROOT}/workspace_swipe/assets'
OUT = f'{ROOT}/workspace_swipe/slides'
os.makedirs(OUT, exist_ok=True)
SW, H, N = 1080, 1350, 5
W = SW * N
BG = (244, 240, 233)
PLUM, MAG, ORANGE, GREEN, INK = (91, 23, 79), (183, 0, 110), (255, 100, 17), (97, 168, 10), (50, 31, 53)


def F(n, s):
    return ImageFont.truetype(f'{FON}/{n}.ttf', s)


def sprite(path, size, rot=0):
    im = Image.open(path).convert('RGBA')
    r, g, b, a = im.split()
    a = a.point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 255 / 215)))   # drop faint render haze
    im = Image.merge('RGBA', (r, g, b, a))
    im = im.crop(im.getbbox())
    sc = size / max(im.size)
    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im


def place(canvas, im, cx, cy, shadow=True):
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    if shadow:
        a = im.split()[3]
        sh = Image.new('RGBA', im.size, (60, 20, 50, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.35)))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        canvas.alpha_composite(sh, (x + 10, y + 22))
    canvas.alpha_composite(im, (x, y))


def token(name):
    for d in ('workspace_three/assets', 'workspace_nq/assets', 'workspace_recipe/assets', 'workspace_tuned/assets'):
        p = f'{ROOT}/{d}/{name}.png'
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


canvas = Image.new('RGBA', (W, H), BG + (255,))
noise = (np.random.default_rng(3).normal(0, 2.2, (H, W, 1))).astype(np.float32)
base = np.clip(np.array(canvas).astype(np.float32)[..., :3] + noise, 0, 255).astype(np.uint8)
canvas = Image.fromarray(np.dstack([base, np.full((H, W), 255, np.uint8)]), 'RGBA')
d = ImageDraw.Draw(canvas)

# ---- the path that runs through every slide (dashed, hand-drawn feel) and ends at the heart
pts = []
xend = 4 * SW + SW / 2
for u in np.linspace(0, 1, 900):
    x = 120 + u * (xend - 120)
    fade = min(1.0, (xend - x) / 1000)
    y = (1040 + 140 * math.sin(u * 9.5) + 60 * math.sin(u * 23)) * fade + 985 * (1 - fade)
    pts.append((x, y))
for i in range(0, len(pts) - 1, 2):
    d.line([pts[i], pts[i + 1]], fill=MAG + (200,), width=9)

# ---- houses (each slide), looking where the story goes
H_ = [  # (file, slide, x in slide, y, size)
    ('h_plum_right', 0, 230, 300, 300), ('h_orange_up', 0, 800, 420, 220), ('h_green_right', 0, 200, 1180, 240), ('h_mag_side', 0, 850, 1060, 210),
    ('h_mag_left', 1, 830, 260, 260), ('h_green_left', 1, 230, 560, 200), ('h_plum_wide', 1, 780, 1120, 280),
    ('h_orange_down', 2, 210, 260, 250), ('h_plum_right', 2, 880, 400, 200), ('h_mag_side', 2, 300, 1150, 230), ('h_green_right', 2, 860, 1170, 220),
    ('h_plum_wide', 3, 540, 330, 330), ('h_mag_left', 3, 170, 1180, 190), ('h_orange_up', 3, 900, 1160, 190),
]
for f, s, x, y, size in H_:
    place(canvas, sprite(f'{A}/{f}.png', size), s * SW + x, y)

# ---- headlines
def headline(s, text, y=640, size=104, col=INK, sub=None, sub2=None):
    cx = s * SW + SW / 2
    d.text((cx, y), text, font=F('Nunito-900', size), fill=col, anchor='mm')
    if sub:
        d.text((cx, y + 100), sub, font=F('Nunito-800', 52), fill=PLUM, anchor='mm')
    if sub2:
        d.text((cx, y + 168), sub2, font=F('Nunito-700', 40), fill=(101, 85, 99), anchor='mm')


headline(0, "Don't swipe.", 720)
headline(1, 'Seriously, don’t.', 820)
headline(2, 'Why are you', 640, 104)
headline(2, 'still swiping?', 760, 104)
headline(3, 'Ok, fine.', 640, 120, sub='We warned you.', sub2='You might fall for every part of it.')

# ---- slide 5: a heart made of real 3D fostering moments
cx, cy = 4 * SW + SW / 2, 660
items = ['backpack', 'books', 'heart', 'seedling', 'mug', 'calendar', 'gradcap', 'teapot' if False else 'bowl', 'umbrella', 'clock',
         'recipecard', 'lantern', 'network', 'phone', 'sun', 'spicejar', 'clipboard', 'certificate', 'identity', 'pot', 'question', 'culture']
ts_ = np.linspace(0, 2 * math.pi, 4000)
cxs = 16 * np.sin(ts_) ** 3
cys = -(13 * np.cos(ts_) - 5 * np.cos(2 * ts_) - 2 * np.cos(3 * ts_) - np.cos(4 * ts_))
seg = np.hypot(np.diff(cxs), np.diff(cys))
cum = np.concatenate([[0], np.cumsum(seg)])
hp = []
for k in range(len(items)):
    j = int(np.searchsorted(cum, (k + 0.5) / len(items) * cum[-1]))
    hp.append((cx + cxs[min(j, len(cxs) - 1)] * 22, cy - 20 + cys[min(j, len(cys) - 1)] * 22))
for (x, y), name in zip(hp, items):
    try:
        place(canvas, sprite(token(name), 118, rot=int(np.random.default_rng(len(name)).integers(-14, 14))), x, y)
    except FileNotFoundError:
        pass
place(canvas, sprite(token('house'), 220), cx, cy - 10)
lg = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
lg = lg.crop(lg.getbbox())
lw = 420
lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
canvas.alpha_composite(lg, (int(cx - lw / 2), 150 - lg.height // 2 + 10))
d = ImageDraw.Draw(canvas)
d.text((cx, 1100), 'Every part of it is a home for someone.', font=F('Nunito-800', 42), fill=INK, anchor='mm')
bw, bh = 460, 92
d.rounded_rectangle([cx - bw / 2, 1150, cx + bw / 2, 1150 + bh], bh // 2, fill=MAG)
d.text((cx, 1150 + bh / 2), 'Start your enquiry', font=F('Nunito-800', 42), fill=(255, 255, 255), anchor='mm')
d.text((cx, 1285), 'No pressure, no obligation  ·  organicfostering.co.uk', font=F('Nunito-700', 30), fill=(101, 85, 99), anchor='mm')

# small swipe hints on slides 1-4 and the brand three-colour bar on every slide
for s in range(4):
    x0 = s * SW + SW - 110
    d.rounded_rectangle([x0, 600, x0 + 70, 700], 22, fill=(255, 255, 255, 170))
    d.line([(x0 + 28, 630), (x0 + 46, 650), (x0 + 28, 670)], fill=PLUM, width=6)
for s in range(N):
    for i, col in enumerate((MAG, ORANGE, GREEN)):
        d.rectangle([s * SW + i * SW // 3, H - 12, s * SW + (i + 1) * SW // 3, H], fill=col)

canvas = canvas.convert('RGB')
for s in range(N):
    sl = canvas.crop((s * SW, 0, (s + 1) * SW, H))
    sl.save(f'{OUT}/slide_{s + 1}.png')
    sl.save(f'{OUT}/slide_{s + 1}.jpg', quality=93)
strip = canvas.resize((W // 3, H // 3), Image.LANCZOS)
st = Image.new('RGB', (strip.width + 4 * 8, strip.height), (30, 30, 30))
for s in range(N):
    st.paste(strip.crop((s * SW // 3, 0, (s + 1) * SW // 3, H // 3)), (s * (SW // 3 + 8), 0))
st.save(f'{OUT}/strip.jpg', quality=90)
print('slides written')
