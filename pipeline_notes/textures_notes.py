"""Flat textures for the 3D objects: the Notes-app screen, three drafts (Mon / Wed / Fri), the social worker's badge.
-> workspace_notes/tex/*.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/workspace_notes/tex'
os.makedirs(OUT, exist_ok=True)
PLUM, MAG, ORANGE, GREEN, IVORY, INK = (91, 23, 79), (183, 0, 110), (255, 100, 17), (97, 168, 10), (252, 248, 245), (50, 31, 53)
GREY = (140, 128, 140)


def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', s)


def notes_screen():
    W, H = 760, 1600
    im = Image.new('RGB', (W, H), IVORY)
    d = ImageDraw.Draw(im)
    d.text((40, 40), '9:41', font=F(800, 34), fill=INK)
    d.text((40, 120), '‹ Notes', font=F(700, 38), fill=ORANGE)
    d.text((40, 220), 'Questions', font=F(900, 64), fill=INK)
    d.text((40, 310), 'Tuesday 23:48', font=F(700, 30), fill=GREY)
    y = 380
    for line in ('This might be a', 'silly question…'):
        d.text((40, y), line, font=F(700, 50), fill=INK)
        y += 66
    d.rectangle([40 + d.textlength('silly question…', font=F(700, 50)) + 6, y - 62, 40 + d.textlength('silly question…', font=F(700, 50)) + 11, y - 8], fill=MAG)
    # keyboard hint
    d.rounded_rectangle([20, 1120, W - 20, 1580], 28, fill=(236, 228, 236))
    for r, n in enumerate((10, 9, 7)):
        for k in range(n):
            x0 = 40 + (W - 80) * k / 10 + r * 26
            d.rounded_rectangle([x0, 1150 + r * 110, x0 + 58, 1240 + r * 110], 10, fill=(255, 255, 255))
    d.rounded_rectangle([W - 150, 1370, W - 40, 1460], 12, fill=(214, 200, 214))
    d.text((W - 95, 1415), '⌫', font=F(800, 44), fill=INK, anchor='mm')
    im.save(f'{OUT}/notes_screen.png')


def draft(day, when):
    W, H = 600, 760
    im = Image.new('RGB', (W, H), IVORY)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 90], fill=(255, 236, 200))
    d.text((30, 45), day, font=F(900, 44), fill=PLUM, anchor='lm')
    d.text((W - 30, 45), when, font=F(700, 30), fill=GREY, anchor='rm')
    y = 150
    for line in ('What happens if', 'I’m struggling after', 'a child comes to', 'live with me?'):
        d.text((30, y), line, font=F(800, 46), fill=INK)
        y += 64
    d.line([(30, 270), (W - 40, 400)], fill=MAG, width=8)          # crossed out / deleted
    d.text((30, H - 70), 'Deleted', font=F(800, 34), fill=MAG)
    im.save(f'{OUT}/draft_{day.lower()}.png')


def badge():
    W, H = 640, 880
    im = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 170], fill=PLUM)
    d.text((W / 2, 85), 'ORGANIC FOSTERING', font=F(900, 40), fill=(255, 255, 255), anchor='mm')
    d.ellipse([W / 2 - 130, 220, W / 2 + 130, 480], fill=(246, 234, 243))
    # simple heart in the photo circle
    cx, cy = W / 2, 350
    d.ellipse([cx - 70, cy - 60, cx, cy + 10], fill=MAG)
    d.ellipse([cx, cy - 60, cx + 70, cy + 10], fill=MAG)
    d.polygon([(cx - 68, cy - 14), (cx + 68, cy - 14), (cx, cy + 70)], fill=MAG)
    d.text((W / 2, 560), 'Your supervising', font=F(800, 44), fill=INK, anchor='mm')
    d.text((W / 2, 620), 'social worker', font=F(900, 52), fill=PLUM, anchor='mm')
    for i, c in enumerate((MAG, ORANGE, GREEN)):
        d.rectangle([i * W / 3, H - 40, (i + 1) * W / 3, H], fill=c)
    im.save(f'{OUT}/badge.png')


notes_screen()
draft('MON', '23:41')
draft('WED', '00:12')
draft('FRI', '22:58')
badge()
print('textures written')
