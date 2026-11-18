"""Compose the final 4:5 post: 3D render + official logo (unmodified, on a clean ivory plate) + CTA line, pill and URL.

Usage: python3 compose_letter.py A|B draft|final -> workspace_letter/post/<layout>_<quality>.png/.jpg
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
PLUM, MAG = (91, 23, 79), (183, 0, 110)
L, Q = sys.argv[1], sys.argv[2]
W, H = 1080, 1350


def F(n, s):
    return ImageFont.truetype(f'{FON}/{n}.ttf', s)


im = Image.open(f'{ROOT}/workspace_letter/render/{L}_{Q}.png').convert('RGB').resize((W, H), Image.LANCZOS)
# soft ivory fade at the foot so the CTA sits on calm ground
a = np.array(im).astype(np.float32)
y = np.arange(H)[:, None, None]
g = np.clip((y - 1080) / 170, 0, 1) * 0.86
a = a * (1 - g) + np.array([252, 248, 245], np.float32) * g
im = Image.fromarray(a.astype(np.uint8))
d = ImageDraw.Draw(im, 'RGBA')

# official logo, unmodified, on an ivory plate (clear space all round)
logo = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
bb = logo.getbbox()
logo = logo.crop(bb)
lw = 300
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
px, py = 54, 48
pad = 26
plate = Image.new('RGBA', (lw + 2 * pad, logo.height + 2 * pad), (0, 0, 0, 0))
pd = ImageDraw.Draw(plate)
pd.rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], 26, fill=(252, 248, 245, 245))
sh = Image.new('RGBA', (plate.width + 40, plate.height + 40), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle([20, 26, plate.width + 20, plate.height + 26], 26, fill=(40, 10, 35, 90))
im.paste(sh.filter(ImageFilter.GaussianBlur(12)), (px - 20, py - 20), sh.filter(ImageFilter.GaussianBlur(12)))
im.paste(plate, (px, py), plate)
im.paste(logo, (px + pad, py + pad), logo)

d = ImageDraw.Draw(im, 'RGBA')
d.text((W / 2, 1172), 'A conversation is a beginning, not a commitment.', font=F('Nunito-700', 34), fill=PLUM, anchor='mm')
bw, bh = 380, 82
bx, by = 70, 1222
d.rounded_rectangle([bx, by, bx + bw, by + bh], bh // 2, fill=MAG)
d.text((bx + bw / 2, by + bh / 2), 'Start your enquiry', font=F('Nunito-800', 36), fill=(255, 255, 255), anchor='mm')
d.text((W - 70, by + bh / 2), 'organicfostering.co.uk', font=F('Nunito-800', 32), fill=PLUM, anchor='rm')
for i, col in enumerate((MAG, (255, 100, 17), (97, 168, 10))):
    d.rectangle([i * W // 3, H - 12, (i + 1) * W // 3, H], fill=col)

os.makedirs(f'{ROOT}/workspace_letter/post', exist_ok=True)
im.save(f'{ROOT}/workspace_letter/post/{L}_{Q}.png')
im.save(f'{ROOT}/workspace_letter/post/{L}_{Q}.jpg', quality=93)
print('composed', L, Q)
