"""Projected search UI texture (RGBA) for Organic Fostering "Asked the internet? Ask us." (static 3D post).

A generic search interface (no third-party branding): search bar with the typed question, suggestions, one result card
for Organic Fostering (photo slot on the left is where the 3D house stands), and a projected keyboard.
-> workspace_search/tex/ui.png (1600 x 2000)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/workspace_search/tex'
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 2000
LIGHT = (255, 246, 252, 255)
DIM = (255, 236, 248, 150)
MAG = (255, 120, 200, 255)


def F(n, s):
    return ImageFont.truetype(f'{FON}/{n}.ttf', s)


im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
# soft projected panel
d.rounded_rectangle([60, 40, W - 60, H - 40], 70, fill=(255, 220, 240, 10), outline=(255, 220, 240, 70), width=4)
# search bar
d.rounded_rectangle([140, 150, W - 140, 300], 75, fill=(255, 240, 248, 60), outline=LIGHT, width=5)
d.ellipse([200, 192, 262, 254], outline=LIGHT, width=8)
d.line([(254, 246), (284, 276)], fill=LIGHT, width=10)
d.text((320, 225), 'Can I foster if I rent my home?', font=F('Nunito-700', 62), fill=LIGHT, anchor='lm')
d.rectangle([1330, 192, 1336, 258], fill=MAG)
# suggestions
for i, s in enumerate(('can I foster if I’m single', 'can I foster if I work full time', 'fostering support Manchester')):
    y = 380 + i * 92
    d.ellipse([200, y - 18, 236, y + 18], outline=DIM, width=5)
    d.text((270, y), s, font=F('Nunito-600' if os.path.exists(f'{FON}/Nunito-600.ttf') else 'Nunito-700', 46), fill=DIM, anchor='lm')
# result card
cx0, cy0, cx1, cy1 = 140, 680, W - 140, 1330
d.rounded_rectangle([cx0, cy0, cx1, cy1], 46, fill=(255, 235, 246, 30), outline=LIGHT, width=5)
d.rounded_rectangle([cx0 + 40, cy0 + 40, cx0 + 520, cy1 - 40], 34, fill=(255, 225, 240, 20), outline=(255, 230, 245, 140), width=3)
tx = cx0 + 580
d.text((tx, cy0 + 70), 'organicfostering.co.uk', font=F('Nunito-700', 40), fill=DIM)
d.text((tx, cy0 + 130), 'Organic Fostering', font=F('Nunito-900', 74), fill=LIGHT)
d.text((tx, cy0 + 225), 'Manchester · Rated Good by Ofsted', font=F('Nunito-700', 40), fill=MAG)
for j, line in enumerate(('Renting doesn’t automatically', 'rule you out. Ask us about', 'the space a child will need.')):
    d.text((tx, cy0 + 300 + j * 58), line, font=F('Nunito-700', 44), fill=LIGHT)
for j, lab in enumerate(('Enquire', 'Call', 'FAQs')):
    x = tx + j * 230
    d.rounded_rectangle([x, cy1 - 120, x + 200, cy1 - 50], 35, outline=LIGHT, width=4, fill=(255, 120, 200, 70) if j == 0 else None)
    d.text((x + 100, cy1 - 85), lab, font=F('Nunito-800', 36), fill=LIGHT, anchor='mm')
# projected keyboard
rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
ky = 1450
for r, keys in enumerate(rows):
    kw, gap = 118, 14
    tw = len(keys) * kw + (len(keys) - 1) * gap
    x0 = W / 2 - tw / 2
    for k, ch in enumerate(keys):
        x = x0 + k * (kw + gap)
        y = ky + r * 132
        d.rounded_rectangle([x, y, x + kw, y + 112], 20, outline=(255, 236, 248, 150), width=4, fill=(255, 230, 245, 8))
        d.text((x + kw / 2, y + 56), ch, font=F('Nunito-700', 44), fill=(255, 236, 248, 200), anchor='mm')
y = ky + 3 * 132
d.rounded_rectangle([340, y, 1100, y + 112], 22, outline=(255, 236, 248, 170), width=4, fill=(255, 230, 245, 22))
d.rounded_rectangle([1130, y, 1460, y + 112], 22, outline=MAG, width=5, fill=(255, 120, 200, 90))
d.text((1295, y + 56), 'search', font=F('Nunito-800', 44), fill=LIGHT, anchor='mm')
glow = im.filter(ImageFilter.GaussianBlur(10))
out = Image.alpha_composite(glow, im)
out.save(f'{OUT}/ui.png')
print('ui written')
