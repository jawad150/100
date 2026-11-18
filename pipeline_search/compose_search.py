"""Overlay for "Asked the internet? Ask us." -> workspace_search/post/<q>.png/.jpg (1080x1350)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
Q = sys.argv[1]
W, H = 1080, 1350
PLUM, MAG, PEACH = (91, 23, 79), (183, 0, 110), (255, 212, 186)


def F(n, s):
    return ImageFont.truetype(f'{FON}/{n}.ttf', s)


im = Image.open(f'{ROOT}/workspace_search/render/{Q}.png').convert('RGB').resize((W, H), Image.LANCZOS)
a = np.array(im).astype(np.float32)
y = np.arange(H)[:, None, None]
top = np.clip((260 - y) / 260, 0, 1) * 0.55
bot = np.clip((y - 1150) / 140, 0, 1) * 0.92
a = a * (1 - top) + np.array([30, 10, 28], np.float32) * top
a = a * (1 - bot) + np.array([91, 23, 79], np.float32) * bot
im = Image.fromarray(a.astype(np.uint8)).convert('RGBA')
d = ImageDraw.Draw(im)
for txt, yy, col, size in (('Asked the internet?', 92, (255, 253, 251), 82), ('Ask us instead.', 188, PEACH, 82)):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((W / 2 + 3, yy + 6), txt, font=F('Nunito-900', size), fill=(0, 0, 0, 150), anchor='mm')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d.text((W / 2, yy), txt, font=F('Nunito-900', size), fill=col, anchor='mm')
logo = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
logo = logo.crop(logo.getbbox())
lw = 250
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
pad = 18
px, py = 46, H - 46 - logo.height - 2 * pad
d.rounded_rectangle([px, py, px + lw + 2 * pad, py + logo.height + 2 * pad], 22, fill=(252, 248, 245, 250))
im.alpha_composite(logo, (px + pad, py + pad))
bw, bh = 400, 88
bx, by = W - 46 - bw, H - 46 - bh - 14
d.rounded_rectangle([bx, by, bx + bw, by + bh], bh // 2, fill=MAG)
d.text((bx + bw / 2, by + bh / 2), 'Start your enquiry', font=F('Nunito-800', 40), fill=(255, 255, 255), anchor='mm')
d.text((bx + bw / 2, by + bh + 14), 'No pressure, no obligation', font=F('Nunito-700', 24), fill=PEACH, anchor='mm')
for i, col in enumerate((MAG, (255, 100, 17), (97, 168, 10))):
    d.rectangle([i * W // 3, H - 12, (i + 1) * W // 3, H], fill=col)
os.makedirs(f'{ROOT}/workspace_search/post', exist_ok=True)
im = im.convert('RGB')
im.save(f'{ROOT}/workspace_search/post/{Q}.png')
im.save(f'{ROOT}/workspace_search/post/{Q}.jpg', quality=93)
print('composed', Q)
