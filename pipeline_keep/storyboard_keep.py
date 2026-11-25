"""Scene frames for BMHC "What did you keep?" -> workspace_keep/board + reel/bmhc/what_did_you_keep/scenes_storyboard.jpg"""
import os, sys, math, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
from PIL import Image, ImageDraw
import frames_keep as G
from frames_keep import (W, H, S, ROOT, INK, WHITE, MAG, DARK, GREYT, paper, place, dotted_ring, photo_circle, type2, thumb_eclipse,
                         arrow_wipe, caption, tag, paste, rrect, text_sprite, load, logo, aurora, layercut, cover)

OUT = f'{S}/board'
os.makedirs(OUT, exist_ok=True)
REF = '/tmp/claude-0/-home-user-100/12e29207-ca18-56fe-8c40-721069807f57/scratchpad/ref10/ref.mp4'
VID = f'{ROOT}/workspace_ai/dl/bmhc-new.mp4'
SUB = 1640


def vframe(path, t):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    return f[..., ::-1].astype(np.float32) / 255


def save(i, c):
    cv2.imwrite(f'{OUT}/scene_{i:02d}.jpg', (np.clip(c, 0, 1)[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])


# recipe card position: its last (magenta) line sits around (430, 1090) at size 980
def card(c, size=980, cx=560, cy=860, rot=-4):
    place(c, 'recipe', cx, cy, size, 1.0, rot, mono=True)


sc = []
# 1 - the detail (eclipse: the thumb hides the last line)
c = paper().copy()
tag(c, 'HEART WORK', 64, 150, MAG)
card(c, 1250, 600, 980, -4)
thumb_eclipse(c, 640, 1065, 190, 1.0, 0.0)
type2(c, 'That last line', 'has nothing to do with cooking.', 64, 300, 5.0, 92)
caption(c, [('That last line', WHITE)], SUB, 1.0, 58)
save(1, c); sc.append(('0:00', 'Extreme close-up of a handwritten recipe card, the last line hidden under a thumb (ECLIPSE). Heart Work tag.', 'Owner: “That last line has nothing to do with cooking.”'))

# 2 - who gave you this (explainer 1)
c = paper().copy()
type2(c, '1. Who gave', 'you this?', 64, 260, 1.0, 92)
dotted_ring(c, 560, 900, 330, 0.0)
photo_circle(c, load(f'{ROOT}/workspace_bmhc/web/img/W6A9208-1-scaled.jpg'), 560, 900, 300, 1.0)
place(c, 'envelope', 820, 1220, 420, 1.0, -8)
caption(c, [('My nani.', WHITE)], SUB, 1.0, 58)
save(2, c); sc.append(('0:03', 'Numbered collage beat (EXPLAINER). The centre’s window in a dotted circle (B&W), an envelope slides in.', 'Off camera: “Who gave you this?” Owner: “My nani. She wrote it out for me the week I left home.”'))

# 3 - the memory: cardamom (retro + aurora)
c = paper().copy()
c = aurora(c, 1.2, 0.18, 0.05, 0.16)
type2(c, '2. What do you', 'remember about her?', 64, 260, 5.0, 92)
dotted_ring(c, 540, 900, 330, 0.4)
photo_circle(c, vframe(f'{ROOT}/workspace_toast/clips/43033.mp4', 3.0), 540, 900, 300, 1.0, 1.0)
place(c, 'cardamom', 300, 1200, 340, 1.0, 10, mono=False)
caption(c, [('Her kitchen', WHITE), ('always smelled', WHITE), ('of cardamom.', MAG)], SUB, 1.0, 54)
save(3, c); sc.append(('0:08', 'A grainy B&W kitchen in the circle (RETRO), a soft magenta glow (AURORA); cardamom pods pop in green.', '“Her kitchen always smelled of cardamom.”'))

# 4 - the spoons (spiral)
c = paper().copy()
dotted_ring(c, 540, 900, 380, 2.0)
dotted_ring(c, 540, 900, 300, -3.0)
card(c, 1500, 380, 980, -4)
place(c, 'spoon', 820, 640, 420, 1.0, 20, mono=False)
type2(c, 'She never', 'measured anything.', 64, 260, 5.0, 92)
caption(c, [('she drew little', WHITE), ('spoons instead.', MAG)], SUB, 1.0, 54)
save(4, c); sc.append(('0:13', 'The dotted rings SPIRAL in onto the little spoons drawn on the card; a 3D brass spoon drops in.', '“She never measured anything… so she drew little spoons instead.”'))

# 5 - the reveal (layercut + eclipse lifts)
c = paper().copy()
card(c, 1250, 600, 980, -4)
thumb_eclipse(c, 640, 1065, 190, 1.0, 0.6)
type2(c, '3. The line', 'we could only glimpse.', 64, 300, 5.0, 92)
cut = layercut(c.copy(), paper().copy(), 0.0)
caption(c, [('“And always make', WHITE), ('enough for', WHITE), ('one more.”', MAG)], SUB, 1.0, 50)
save(5, c); sc.append(('0:19', 'Back to the opening shot: the thumb lifts (the eclipse slides away) and the magenta line is revealed. LAYERCUT on the cut.', 'Owner reads: “And always make enough for one more.”'))

# 6 - reaction
c = paper().copy()
dotted_ring(c, 540, 880, 330, 1.0)
place(c, 'photo', 540, 880, 560, 1.0, 6)
type2(c, 'That', 'was her.', 64, 300, 1.0, 120)
caption(c, [('That was her.', WHITE)], SUB, 1.0, 58)
save(6, c); sc.append(('0:24', 'A beat for her reaction (a soft laugh). An old photograph settles into the circle.', '(laughs softly) “That was her.”'))

# 7 - pass the question on (drawer + arrow wipe)
c = paper().copy()
place(c, 'drawer', 540, 1080, 760, 1.0, 0)
place(c, 'recipe', 520, 820, 360, 1.0, -70)
type2(c, 'What’s one thing', 'your family has kept?', 64, 300, 5.0, 92)
arrow_wipe(c, 0.55)
save(7, c); sc.append(('0:27', 'The card is put away in a drawer. On screen: “What’s one thing your family has kept?” The black arrow sweeps across.', 'On screen only.'))

# 8 - end card
c = np.empty((H, W, 3), np.float32)
c[:] = INK
lg = logo(820)
paste(c, lg, 540, 820)
s = text_sprite('@thebmhc', 700, 46, (0.8, 0.8, 0.8))
paste(c, s, 540, 1120)
for i, col in enumerate(G.BARS):
    c[H - 22:, int(W * i / 4):int(W * (i + 1) / 4)] = col
save(8, c); sc.append(('0:31', 'Final 1.5 s: official BMHC logo and the account handle.', ''))

tw, th = 270, 480
cols = 4
rows = math.ceil(len(sc) / cols)
cellh = th + 200
sheet = Image.new('RGB', (cols * (tw + 26) + 26, 150 + rows * cellh), (236, 234, 230))
d = ImageDraw.Draw(sheet)
d.text((26, 28), 'BMHC  ·  What did you keep?', font=G.F(800, 42), fill=(17, 17, 17))
d.text((26, 88), '9:16 · 33 s · B&W collage (after your reference) + Heritage Magenta · scenes for approval', font=G.F(500, 22), fill=(90, 90, 90))
for i, (tc, vis, vo) in enumerate(sc):
    im = Image.open(f'{OUT}/scene_{i + 1:02d}.jpg').resize((tw, th), Image.LANCZOS)
    x = 26 + (i % cols) * (tw + 26)
    y = 140 + (i // cols) * cellh
    sheet.paste(im, (x, y))
    d.rounded_rectangle([x, y, x + 76, y + 32], 8, fill=(230, 5, 133))
    d.text((x + 9, y + 5), tc, font=G.F(700, 19), fill=(255, 255, 255))
    yy = y + th + 8
    for ln in textwrap.wrap(vo, 34)[:3]:
        d.text((x, yy), ln, font=G.F(700, 17), fill=(17, 17, 17))
        yy += 21
    for ln in textwrap.wrap(vis, 38)[:4]:
        d.text((x, yy + 4), ln, font=G.F(500, 15), fill=(95, 95, 95))
        yy += 19
for i, col in enumerate(((230, 5, 133), (45, 200, 146), (255, 66, 0), (105, 255, 0))):
    d.rectangle([int(sheet.width * i / 4), sheet.height - 10, int(sheet.width * (i + 1) / 4), sheet.height], fill=col)
dst = f'{ROOT}/reel/bmhc/what_did_you_keep'
os.makedirs(dst, exist_ok=True)
sheet.save(f'{dst}/scenes_storyboard.jpg', quality=92)
print('sheet', sheet.size)
