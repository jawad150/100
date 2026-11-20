"""Scene frames for Organic Fostering "The Question in the Notes App" -> workspace_notes/board + reel sheet."""
import os, sys, math, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
from PIL import Image, ImageDraw
import frames_notes as G
from frames_notes import (W, H, S, ROOT, PLUM, MAG, ORANGE, GREEN, IVORY, INK, BLUSH, WHITE, GLOW, light_bg, dark_bg, blobs, word,
                          typed, subtitle, speaker, pop, circle_portrait, node, dotted_path, circle_wipe, spiral_warp, colour_bar,
                          logo, text_sprite, paste, rrect, cover, layercut, eclipse, aurora, retro, grain, load)

OUT = f'{S}/board'
os.makedirs(OUT, exist_ok=True)
CL = f'{S}/clips'


def frame_at(clip, t):
    cap = cv2.VideoCapture(f'{CL}/{clip}.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    return f[..., ::-1].astype(np.float32) / 255


def save(i, c):
    cv2.imwrite(f'{OUT}/scene_{i:02d}.jpg', (np.clip(c, 0, 1)[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('scene', i, flush=True)


# 01 - the delete key
c = light_bg().copy()
blobs(c, 0.3, PLUM, 1.0)
word(c, 'The question', 540, 330, 70, 700, PLUM)
word(c, 'I kept', 540, 430, 110, 900, INK)
word(c, 'deleting', 540, 560, 150, 900, MAG)
cv2.line(c, (250, 565), (830, 548), MAG.tolist(), 10, cv2.LINE_AA)
pop(c, 'phone_notes', 540, 1080, 700, 1.0, rot=0)
subtitle(c, '')
save(1, c)

# 02 - three times (layercut drafts)
c = light_bg().copy()
blobs(c, 1.0, PLUM, 1.0, 1)
pop(c, 'drafts', 540, 900, 760, 1.0)
word(c, '×3', 850, 470, 220, 900, MAG, glow=G.GLOW)
word(c, 'the same question', 380, 380, 64, 700, PLUM)
subtitle(c, "I'd typed the same question three times…")
save(2, c)

# 03 - that week (retro tape)
c = light_bg().copy()
pop(c, 'calendar', 540, 900, 700, 1.0)
c = retro(c, 2.0, 0.9)
word(c, 'MON 23:41', 250, 230, 52, 800, (1, 1, 1))
word(c, '◀◀ REW', 860, 230, 48, 800, (1, 1, 1))
word(c, 'that week.', 540, 1330, 120, 900, (1, 0.93, 0.85))
subtitle(c, '…that week.')
save(3, c)

# 04 - spiral: the phone goes down beside the mug
c = light_bg().copy()
pop(c, 'mug', 650, 940, 520, 1.0)
pop(c, 'phone_notes', 330, 1050, 420, 1.0, rot=-70)
c = spiral_warp(c, 0.35, 560, 900)
word(c, 'later that day', 540, 330, 80, 800, PLUM)
save(4, c)

# 05 - circle wipe onto the call
a = c.copy()
b = G.grade(cover(frame_at('39790', 3.0), fx=0.33, fy=0.4, z=1.05), warm=0.3, contrast=1.05, vig=0.4)
c = circle_wipe(a, b, 0.55, 540, 900, col=MAG)
save(5, c)

# 06 - "Can I ask something?"
c = G.grade(cover(frame_at('39790', 6.0), fx=0.3, fy=0.4, z=1.05), warm=0.3, contrast=1.05, vig=0.45)
word(c, 'Can I ask', 540, 360, 90, 700, WHITE, glow=PLUM)
word(c, 'something?', 540, 480, 130, 900, WHITE, glow=MAG)
speaker(c, 'Caller', MAG, 1420)
subtitle(c, 'Can I ask something?')
save(6, c)

# 07 - "struggling" + "a child comes to live with me"
c = G.grade(cover(frame_at('39790', 9.0), fx=0.3, fy=0.4, z=1.08), warm=0.1, contrast=1.05, vig=0.5, exp=0.8)
pop(c, 'cloud', 300, 560, 380, 1.0)
pop(c, 'home_door', 760, 1040, 440, 1.0, glow=np.array((1, 0.7, 0.4), np.float32))
word(c, 'struggling', 330, 800, 84, 900, WHITE, glow=MAG)
subtitle(c, "What happens if I'm struggling after a child comes to live with me?")
save(7, c)

# 08 - the answer: supervising social worker (dark, portrait circle, badge, mug stops)
c = dark_bg().copy()
port = cover(frame_at('39791', 3.0), fx=0.5, fy=0.35, z=1.0, w=560, h=560)
circle_portrait(c, port, 540, 560, 260, bw=1.0, ring_t=1.0, ring_col=GLOW)
pop(c, 'badge', 820, 1040, 420, 1.0)
pop(c, 'mug', 250, 1110, 300, 1.0)
word(c, 'supervising', 380, 920, 70, 700, WHITE)
word(c, 'social worker', 380, 1010, 86, 900, GLOW, glow=MAG)
speaker(c, 'Organic Fostering', MAG, 1420)
subtitle(c, "You'll have a supervising social worker.")
save(8, c)

# 09 - explainer path: talk you through what support looks like
c = dark_bg().copy()
pts = [(200, 330), (420, 560), (300, 830), (620, 1050), (860, 1260)]
dotted_path(c, pts, 1.0)
node(c, 200, 330, 1.0, 'badge', 150, label='Your social worker')
node(c, 420, 560, 1.0, 'chat', 150, label='Talk it through')
node(c, 300, 830, 1.0, 'calendar', 150, label='What support looks like')
node(c, 620, 1050, 1.0, 'night_clock', 150, label='Out of hours', lab_side=-1)
subtitle(c, 'We can talk you through what that support looks like…')
save(9, c)

# 10 - outside normal hours: eclipse + aurora
c = dark_bg().copy()
c = aurora(c, 1.5, 0.75, 0.08, 0.3)
c = eclipse(c, 540, 560, 170, 0.8, warm=(1.0, 0.75, 0.5))
pop(c, 'night_clock', 540, 1050, 520, 1.0, glow=np.array((0.9, 0.4, 0.8), np.float32))
word(c, 'outside', 540, 830, 70, 700, WHITE)
word(c, 'normal hours', 540, 1340, 96, 900, GLOW, glow=MAG)
subtitle(c, '…including who to call outside normal hours.')
save(10, c)

# 11 - back to the Notes app: a new line
c = light_bg().copy()
blobs(c, 2.0, PLUM, 1.0, 2)
card = rrect(900, 760, 46, WHITE, 0.97)
paste(c, card, 540, 820)
word(c, 'Questions', 260, 520, 64, 900, INK, anchor='l')
typed(c, '✓ What happens if I’m struggling?', 140, 640, 40, 99, 700, (0.55, 0.5, 0.55), caret=False)
typed(c, 'Can I ask about training as well?', 140, 740, 44, 99, 800, INK, t=0.1)
pop(c, 'cap', 760, 1180, 420, 1.0)
circle_portrait(c, cover(frame_at('39791', 8.0), fx=0.5, fy=0.35, z=1.0, w=300, h=300), 270, 1190, 140, bw=0.0, ring_t=2, ring_col=MAG)
subtitle(c, 'Okay. Can I ask about training as well?')
save(11, c)

# 12 - plum end card
c = np.empty((H, W, 3), np.float32)
c[:] = PLUM
blobs(c, 0.5, np.array((0.42, 0.06, 0.36), np.float32), 1.0, 3)
lg = logo(640)
paste(c, rrect(760, lg.shape[0] + 110, 40, IVORY), 540, 560)
paste(c, lg, 540, 560)
word(c, 'Start your enquiry', 540, 860, 76, 900, WHITE)
paste(c, rrect(560, 104, 52, MAG), 540, 1010)
word(c, 'organicfostering.co.uk', 540, 1010, 44, 800, WHITE)
word(c, 'We’ll talk through your questions,', 540, 1170, 42, 700, (0.95, 0.85, 0.93))
word(c, 'with no obligation.', 540, 1230, 42, 700, (0.95, 0.85, 0.93))
colour_bar(c)
save(12, c)

BEATS = [
    ('00:00', 'Starts on the delete-key tap. Kinetic opening text; the 3D phone deletes “This might be a silly question…”.', 'Opening text: “The question I kept deleting”'),
    ('00:02', 'LAYERCUT: three drafts (Mon, Wed, Fri) peel apart as layers; a glowing ×3.', '“I’d typed the same question three times…”'),
    ('00:04', 'RETRO: the week rewinds on tape; a 3D calendar circles three late nights.', '“…that week.”'),
    ('00:05', 'SPIRAL: the phone spins down beside a 3D mug. “Later that day”.', '(the phone goes down)'),
    ('00:06', 'A magenta circle wipe opens onto the caller, phone to her ear.', '(she dials)'),
    ('00:07', 'Kinetic words land as she speaks.', 'Caller: “Can I ask something?”'),
    ('00:08', 'A 3D rain cloud on “struggling”; a home with its door open on “comes to live with me”.', '“What happens if I’m struggling after a child comes to live with me?”'),
    ('00:11', 'Night plum. Her portrait in a dotted ring; the 3D badge; the turning mug stops.', 'Team: “You’ll have a supervising social worker.”'),
    ('00:15', 'EXPLAINER: glowing nodes join up along a dotted path.', '“We can talk you through what that support looks like,”'),
    ('00:19', 'ECLIPSE: the sun slides into night; AURORA; the 3D night clock.', '“including who to call outside normal hours.”'),
    ('00:22', 'Back in the Notes app: the old line ticked, a new one typed; 3D cap on “training”.', 'Caller (smiling): “Okay. Can I ask about training as well?”'),
    ('00:27', 'Plum end card, official logo, Start your enquiry, organicfostering.co.uk.', '“Start your enquiry with Organic Fostering. We’ll talk through your questions, with no obligation.”'),
]
tw, th = 300, 533
cols = 6
rows = math.ceil(len(BEATS) / cols)
cellh = th + 200
sheet = Image.new('RGB', (cols * (tw + 26) + 26, 150 + rows * cellh + 20), (252, 248, 245))
d = ImageDraw.Draw(sheet)
d.text((26, 28), 'Organic Fostering  ·  The Question in the Notes App', font=G.F(900, 44), fill=(91, 23, 79))
d.text((26, 90), '9:16  ·  ~33 s  ·  kinetic explainer style  ·  3D object on every cue word  ·  scenes for approval', font=G.F(700, 26), fill=(120, 100, 115))
for i, (tc, vis, vo) in enumerate(BEATS):
    im = Image.open(f'{OUT}/scene_{i + 1:02d}.jpg').resize((tw, th), Image.LANCZOS)
    x = 26 + (i % cols) * (tw + 26)
    y = 150 + (i // cols) * cellh
    sheet.paste(im, (x, y))
    d.rounded_rectangle([x, y, x + 90, y + 38], 10, fill=(183, 0, 110))
    d.text((x + 10, y + 6), tc, font=G.F(800, 22), fill=(255, 255, 255))
    yy = y + th + 10
    for ln in textwrap.wrap(vo, 30)[:3]:
        d.text((x, yy), ln, font=G.F(800, 19), fill=(91, 23, 79))
        yy += 24
    for ln in textwrap.wrap(vis, 36)[:4]:
        d.text((x, yy + 4), ln, font=G.F(600, 17) if os.path.exists(f'{G.FON}/Nunito-600.ttf') else G.F(700, 17), fill=(110, 95, 108))
        yy += 22
for i, col in enumerate(((183, 0, 110), (255, 100, 17), (97, 168, 10))):
    d.rectangle([int(sheet.width * i / 3), sheet.height - 12, int(sheet.width * (i + 1) / 3), sheet.height], fill=col)
dst = f'{ROOT}/reel/organic_fostering/question_in_the_notes_app'
os.makedirs(dst, exist_ok=True)
sheet.save(f'{dst}/scenes_storyboard.jpg', quality=92)
print('sheet', sheet.size)
