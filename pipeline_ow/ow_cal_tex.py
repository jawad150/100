"""Calendar texture for "One Weekend": plum header bar, 7x5 rounded lavender day squares, no month name (never dates).
Also writes the grid geometry (texture px) to cal_grid.json for exact marker placement.
"""
import os, json
from PIL import Image, ImageDraw, ImageFont
ROOT = '/home/user/100'
F = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/workspace_ow/tex'
W, H = 1400, 1500
PLUM, LAV, LAV2, IVORY, ORANGE = (91, 23, 79), (238, 224, 238), (246, 236, 245), (253, 250, 246), (255, 100, 17)
im = Image.new('RGB', (W, H), IVORY)
d = ImageDraw.Draw(im)
nun = lambda w, s: ImageFont.truetype(f'{F}/Nunito-{w}.ttf', s)
# header bar with ring holes (no month name)
d.rectangle([0, 0, W, 230], fill=PLUM)
for i in range(9):
    x = 110 + i * (W - 220) / 8
    d.ellipse([x - 18, 40, x + 18, 76], fill=(60, 12, 50))
d.rounded_rectangle([70, 120, 290, 180], 30, fill=(122, 40, 108))
d.rounded_rectangle([W - 290, 120, W - 70, 180], 30, fill=(122, 40, 108))
gx, gy, gw = 60, 300, W - 120
cw = gw / 7
rows = 5
ch = (H - 70 - gy - 40) / rows
for i, dn in enumerate(['M', 'T', 'W', 'T', 'F', 'S', 'S']):
    d.text((gx + i * cw + cw / 2, gy), dn, font=nun(900, 44), fill=ORANGE if i >= 5 else (140, 100, 130), anchor='mm')
top = gy + 50
cells = {}
day = 1
for r in range(rows):
    for c in range(7):
        x0, y0 = gx + c * cw + 8, top + r * ch + 8
        x1, y1 = x0 + cw - 16, y0 + ch - 16
        fill = LAV if c >= 5 else LAV2
        d.rounded_rectangle([x0, y0, x1, y1], 22, fill=fill)
        if day <= 31:
            d.text((x0 + 18, y0 + 12), str(day), font=nun(800, 40), fill=PLUM)
        cells[f'{r},{c}'] = [x0, y0, x1, y1]
        day += 1
im.save(f'{OUT}/cal_blank.png')
json.dump({'W': W, 'H': H, 'cells': cells, 'rows': rows}, open(f'{OUT}/cal_grid.json', 'w'))
print('ok')
