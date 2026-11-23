"""Scene frames for Organic Fostering "One question is enough" -> workspace_oneq/board + reel sheet."""
import os, sys, math, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
from PIL import Image, ImageDraw
import frames_oneq as G
from frames_oneq import (W, H, S, ROOT, PLUM, MAG, IVORY, INK, WHITE, GLOW, paper, ivory_paper, lens, ring_sweep, icon_circle, card,
                         word, typed, subtitle, paste, rrect, text_sprite, layercut, eclipse, aurora, grain, pop, logo, colour_bar)
import frames_notes as N

OUT = f'{S}/board'
os.makedirs(OUT, exist_ok=True)
LIGHT = (0.95, 0.88, 0.93)


def save(i, c):
    cv2.imwrite(f'{OUT}/scene_{i:02d}.jpg', (np.clip(c, 0, 1)[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('scene', i, flush=True)


def head(c):
    word(c, 'ORGANIC FOSTERING', 540, 130, 30, 800, LIGHT)


# 01 - headline beat 1, the magnifying glass reading it
c = paper().copy()
head(c)
word(c, 'HOW MANY', 540, 560, 150, 900, WHITE)
word(c, 'QUESTIONS', 540, 720, 150, 900, WHITE)
c = lens(c, 560, 640, 128, 1.6)
pop(c, 'magnifier', 616, 720, 430, 1.0, shadow=False)
subtitle(c, 'How many questions do you need answered…')
save(1, grain(c, 0.015))

# 02 - beat 2 (layercut slices)
c = paper().copy()
head(c)
word(c, 'HOW MANY QUESTIONS', 540, 520, 96, 900, WHITE)
word(c, 'do you need answered', 540, 650, 62, 700, LIGHT)
word(c, 'before you enquire', 540, 730, 62, 700, LIGHT)
word(c, 'about fostering?', 540, 830, 92, 900, (1.0, 0.62, 0.85))
pop(c, 'qmark', 860, 1180, 380, 1.0)
c = layercut(c.copy(), paper().copy(), 0.12, n=6)
subtitle(c, '…before you enquire about fostering?')
save(2, grain(c, 0.015))

# 03 - ring sweep (eclipse) into question 1: the key
c = paper().copy()
head(c)
c = ring_sweep(c, 540, 820, 240, 0.6)
icon_circle(c, 540, 820, 190, 'key', 1.0)
word(c, 'Can I foster', 540, 1160, 96, 900, WHITE)
word(c, 'if I rent?', 540, 1270, 96, 900, WHITE)
subtitle(c, 'Can I foster if I rent?')
save(3, grain(c, 0.015))

# 04 - question 2: the calendar
c = paper().copy()
head(c)
icon_circle(c, 250, 420, 110, 'key', 1.0, 'Renting', a=0.55)
icon_circle(c, 540, 820, 190, 'calendar', 1.0)
word(c, 'How would fostering', 540, 1160, 76, 900, WHITE)
word(c, 'fit around work?', 540, 1260, 92, 900, WHITE)
subtitle(c, 'How would fostering fit around work?')
save(4, grain(c, 0.015))

# 05 - question 3: the phone; the three icons as a row (explainer)
c = paper().copy()
head(c)
icon_circle(c, 250, 420, 110, 'key', 1.0, 'Renting', a=0.6)
icon_circle(c, 830, 420, 110, 'calendar', 1.0, 'Work', a=0.6)
icon_circle(c, 540, 820, 190, 'phone', 1.0)
word(c, 'Who can I call', 540, 1160, 92, 900, WHITE)
word(c, 'if I need support?', 540, 1265, 80, 900, WHITE)
subtitle(c, 'Who can I call if I need support?')
save(5, grain(c, 0.015))

# 06 - spiral: three cards spiral into one speech bubble
c = paper().copy()
head(c)
yy, xx = N._grid()
for i, (txt, nm, ang) in enumerate((('Can I foster if I rent?', 'key', 200), ('How would it fit around work?', 'calendar', 320),
                                    ('Who can I call for support?', 'phone', 80))):
    a = math.radians(ang)
    card(c, txt, 540 + 250 * math.cos(a), 860 + 420 * math.sin(a), 860, nm, 1.0, scale=0.85, rot=(-10, 6, -5)[i])
pop(c, 'bubble', 540, 860, 380, 1.0, glow=np.array((0.9, 0.2, 0.6), np.float32))
save(6, grain(c, 0.015))

# 07 - one question is enough (aurora glow, typewriter)
c = paper().copy()
c = aurora(c, 1.2, 0.35, 0.05, 0.2)
head(c)
pop(c, 'bubble', 540, 760, 640, 1.0, glow=np.array((0.9, 0.2, 0.6), np.float32))
typed(c, 'One question', 210, 1170, 104, 99, 900, WHITE, caret=False)
typed(c, 'is enough to start.', 160, 1290, 86, 99, 900, (1.0, 0.62, 0.85), caret=True, t=0.1, caret_col=MAG)
subtitle(c, 'One question is enough to start.')
save(7, grain(c, 0.015))

# 08 - warm ivory end card
c = ivory_paper().copy()
lg = logo(760)
paste(c, lg, 540, 620)
word(c, 'Thinking about fostering', 540, 940, 64, 900, PLUM)
word(c, 'in Greater Manchester?', 540, 1020, 64, 900, PLUM)
paste(c, rrect(560, 112, 56, MAG), 540, 1180)
word(c, 'Start your enquiry', 540, 1180, 50, 900, IVORY)
word(c, 'Link in bio', 540, 1300, 44, 800, PLUM)
colour_bar(c)
save(8, c)

BEATS = [
    ('00:00', 'Deep-plum paper. The headline builds in two quick beats while a 3D magnifying glass reads it (real lens zoom).', 'VO: “How many questions do you need answered…”'),
    ('00:01', 'LAYERCUT: the headline lines slice in as layers; a 3D question mark.', '“…before you enquire about fostering?”'),
    ('00:03', 'ECLIPSE: the ring sweeps round and opens the first question; a 3D key with a little house fob. Soft click.', '“Can I foster if I rent?”'),
    ('00:05', 'EXPLAINER: the key steps aside into a small labelled circle; a 3D calendar takes centre. Click.', '“How would fostering fit around work?”'),
    ('00:07', 'Third beat: a 3D phone with a call and a heart. The three circles sit in a row. Click.', '“Who can I call if I need support?”'),
    ('00:10', 'SPIRAL: the three question cards spiral into one speech bubble (magenta accent).', '(the cards come together)'),
    ('00:11', 'Hold the bubble. RETRO typewriter line; a soft AURORA glow behind.', '“One question is enough to start.” (smiling)'),
    ('00:15', 'Warm-ivory end card: Organic Fostering logo, CTA, link in bio. Hold.', '“Thinking about fostering in Greater Manchester? Start your enquiry. Link in bio.”'),
]
tw, th = 300, 533
cols = 4
rows = math.ceil(len(BEATS) / cols)
cellh = th + 200
sheet = Image.new('RGB', (cols * (tw + 26) + 26, 150 + rows * cellh + 20), (252, 248, 245))
d = ImageDraw.Draw(sheet)
d.text((26, 28), 'Organic Fostering  ·  One question is enough', font=N.F(900, 44), fill=(91, 23, 79))
d.text((26, 90), '9:16  ·  22 s  ·  deep plum + warm ivory  ·  3D object on every cue  ·  scenes for approval', font=N.F(700, 24), fill=(120, 100, 115))
for i, (tc, vis, vo) in enumerate(BEATS):
    im = Image.open(f'{OUT}/scene_{i + 1:02d}.jpg').resize((tw, th), Image.LANCZOS)
    x = 26 + (i % cols) * (tw + 26)
    y = 150 + (i // cols) * cellh
    sheet.paste(im, (x, y))
    d.rounded_rectangle([x, y, x + 90, y + 38], 10, fill=(183, 0, 110))
    d.text((x + 10, y + 6), tc, font=N.F(800, 22), fill=(255, 255, 255))
    yy = y + th + 10
    for ln in textwrap.wrap(vo, 30)[:3]:
        d.text((x, yy), ln, font=N.F(800, 19), fill=(91, 23, 79))
        yy += 24
    for ln in textwrap.wrap(vis, 36)[:4]:
        d.text((x, yy + 4), ln, font=N.F(700, 17), fill=(110, 95, 108))
        yy += 22
for i, col in enumerate(((183, 0, 110), (255, 100, 17), (97, 168, 10))):
    d.rectangle([int(sheet.width * i / 3), sheet.height - 12, int(sheet.width * (i + 1) / 3), sheet.height], fill=col)
dst = f'{ROOT}/reel/organic_fostering/one_question_is_enough'
os.makedirs(dst, exist_ok=True)
sheet.save(f'{dst}/scenes_storyboard.jpg', quality=92)
print('sheet', sheet.size)
