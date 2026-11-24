"""Scene map for BMHC "Name this place by ear": each reference scene (extracted frame) beside its BMHC frame.
-> workspace_ear/board/scene_XX.jpg + reel/bmhc/name_this_place_by_ear/scenes_storyboard.jpg
"""
import os, sys, math, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
from PIL import Image, ImageDraw
import frames_ear as G
from frames_ear import (W, H, S, ROOT, INK, WHITE, MAG, TEAL, ORANGE, LIME, light_bg, dark_bg, pop, word, highlight, pill, clue_no,
                        card, orbit, confetti, caption, tag, paste, rrect, text_sprite, cover, load, logo)

OUT = f'{S}/board'
os.makedirs(OUT, exist_ok=True)
REF = '/tmp/claude-0/-home-user-100/12e29207-ca18-56fe-8c40-721069807f57/scratchpad/ref9/ref.mp4'
VID = f'{ROOT}/workspace_ai/dl/bmhc-new.mp4'
DL = f'{ROOT}/workspace_ai/dl'


def vframe(path, t):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    return f[..., ::-1].astype(np.float32) / 255


def save(i, c):
    cv2.imwrite(f'{OUT}/scene_{i:02d}.jpg', (np.clip(c, 0, 1)[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])


SUB = 1610
scenes = []

# 1 - hook: kinetic words + highlight box + mic (ref 1)
c = light_bg().copy()
tag(c, 'HEART', 64, 150, MAG)
word(c, 'Manchester,', 540, 470, 96, (0.04, 0.04, 0.04))
word(c, 'can you name', 540, 590, 84, (0.04, 0.04, 0.04))
word(c, 'this place', 540, 700, 84, (0.04, 0.04, 0.04))
highlight(c, 'by ear?', 540, 830, 96, 1.0)
pop(c, 'mic', 760, 1150, 520, 1.0)
caption(c, [('Manchester,', WHITE), ('name this place', WHITE)], SUB, 1.0, 62)
save(1, c); scenes.append((1.5, 1, '0:00', 'Kinetic words, the highlight box lands on "by ear?"; HEART tag; a 3D microphone.', '“Manchester, can you name this place by ear?”'))

# 2 - three sounds: floating 3D objects + notification pills (ref 3)
c = dark_bg(1).copy()
pop(c, 'ball', 300, 520, 300, 1.0)
pop(c, 'book', 780, 760, 380, 1.0)
pop(c, 'fader', 360, 1080, 400, 1.0)
pill(c, '[ball bouncing]', 640, 430, 1.0)
pill(c, '[page rustling]', 400, 930, 1.0)
pill(c, '[switch clicks]', 700, 1300, 1.0)
save(2, c); scenes.append((7.0, 2, '0:02', 'Three sounds cut into the silence: 3D ball, book, fader float in, each with a caption pill.', '[ball bouncing] [page rustling] [switch clicks]'))

# 3 - first clue: glowing landscape + 01 + bouncing ball (ref 4)
c = dark_bg(2, True).copy()
clue_no(c, 1, 540, 420, 1.0)
word(c, 'First clue.', 540, 650, 96, WHITE)
pop(c, 'ball', 620, 1060, 260, 1.0)
pill(c, '[ball bouncing]', 540, 1500, 1.0)
caption(c, [('First', WHITE), ('clue.', MAG)], SUB, 1.0, 62)
save(3, c); scenes.append((9.5, 3, '0:04', 'Magenta “01”. The ball bounces twice across a glowing landscape, shadow following; a trainer squeaks to a stop.', '“First clue.” [ball bouncing] [trainer squeaks]'))

# 4 - second clue: book + page + pencil (ref 5)
c = dark_bg(3).copy()
clue_no(c, 2, 540, 420, 1.0)
word(c, 'Second clue.', 540, 650, 96, WHITE)
pop(c, 'book', 540, 1050, 560, 1.0)
pill(c, '[page rustling]', 540, 1420, 1.0)
caption(c, [('Second', WHITE), ('clue.', MAG)], SUB, 1.0, 62)
save(4, c); scenes.append((11.3, 4, '0:10', 'Magenta “02”. A page lifts and falls; a pencil underlines one word in magenta.', '“Second clue.” [page rustling] [pencil scratching]'))

# 5 - last one: orbit + fader + headphones (ref 7)
c = dark_bg(4).copy()
clue_no(c, 3, 540, 400, 1.0)
word(c, 'Last one.', 540, 620, 96, WHITE)
orbit(c, 540, 1060, 330, 1.0, [(MAG, 90), (TEAL, 70), (ORANGE, 60), (LIME, 70), (MAG, 60)], 1.0)
pop(c, 'fader', 540, 1060, 420, 1.0)
pop(c, 'headphones', 820, 830, 260, 1.0)
pill(c, '[switch clicks]', 540, 1430, 1.0)
caption(c, [('Assalamu alaikum,', WHITE), ('Manchester.', MAG)], SUB, 1.0, 60)
save(5, c); scenes.append((17.0, 5, '0:16', 'Magenta “03”. Orbiting nodes; the fader is pushed up, headphones settle; the presenter leans in.', '“Last one.” [switch clicks] Presenter: “Assalamu alaikum, Manchester.”'))

# 6 - got a guess? (ref 9 / ref 10)
c = light_bg(2).copy()
word(c, 'Got a', 540, 700, 130, (0.04, 0.04, 0.04))
highlight(c, 'guess?', 540, 860, 140, 1.0)
for (x, y, s) in ((230, 420, '[ball bouncing]'), (830, 1080, '[page rustling]'), (300, 1180, '[switch clicks]')):
    pill(c, s, x + 60, y, 1.0, dark=False)
confetti(c, 1.0, 0.5)
save(6, c); scenes.append((31.2, 6, '0:22', 'A beat to guess: kinetic “Got a guess?” with the three sound tags floating; four-colour confetti.', 'On screen: “Got a guess?”'))

# 7 - the reveal: wide shots as floating cards (ref 8)
c = dark_bg(5).copy()
card(c, cover(vframe(VID, 3.5), 0.5, 0.5, 1.0, 560, 380), 360, 470, 560, 380, 1.0, 0.06, '[ball bouncing]')
card(c, cover(vframe(VID, 12.6), 0.5, 0.5, 1.0, 560, 380), 720, 900, 560, 380, 1.0, -0.06, '[page rustling]')
card(c, cover(load(f'{DL}/18953234_1692708564077281_8688673643638198134_o.jpg'), 0.5, 0.45, 1.0, 560, 380), 360, 1330, 560, 380, 1.0, 0.06, '[switch clicks]')
save(7, c); scenes.append((20.5, 7, '0:23', 'The sounds replay over BMHC’s real wide shots, floating as cards: sports, the hall, Heritage Radio.', '(the three sounds, again)'))

# 8 - name the place: logo reveal over the real tower (ref 6)
c = dark_bg(6).copy()
card(c, cover(vframe(VID, 34.0), 0.45, 0.6, 1.0, 860, 760), 540, 980, 860, 760, 1.0, 0.0)
word(c, 'Three sounds.', 540, 360, 90, WHITE)
word(c, 'One address.', 540, 470, 90, MAG)
caption(c, [('The British Muslim', WHITE), ('Heritage Centre,', WHITE)], SUB, 1.0, 58)
save(8, c); scenes.append((14.2, 8, '0:27', 'Outside to the real BMHC building (their own drone footage) in a big floating card.', '“Three sounds. One address. The British Muslim Heritage Centre, Whalley Range.”'))

# 9 - end card (ref 12)
c = np.empty((H, W, 3), np.float32)
c[:] = INK
lg = logo(820)
paste(c, lg, 540, 760)
word(c, 'Which clue gave it away?', 540, 1080, 62, WHITE)
word(c, '@thebmhc  ·  bmhc.org.uk', 540, 1180, 40, (0.75, 0.75, 0.75), w=600)
for i, col in enumerate(G.BARS):
    c[H - 22:, int(W * i / 4):int(W * (i + 1) / 4)] = col
save(9, c); scenes.append((40.0, 9, '0:32', 'Final 1.5 s: official reversed logo on ink, handle, one question.', 'On screen: “Which clue gave it away?”'))

# ---------------- sheet: reference frame | BMHC frame
tw, th = 180, 320
cols = 3
rows = math.ceil(len(scenes) / cols)
cellw, cellh = 2 * tw + 30 + 40, th + 170
sheet = Image.new('RGB', (cols * cellw + 40, 150 + rows * cellh), (11, 11, 11))
d = ImageDraw.Draw(sheet)
d.text((30, 28), 'BMHC  ·  Manchester, can you name this place by ear?', font=G.F(800, 38), fill=(255, 255, 255))
d.text((30, 84), 'Reference scene (left)  →  BMHC scene (right)  ·  9:16  ·  34 s  ·  scenes for approval', font=G.F(500, 22), fill=(170, 170, 170))
for i, (rt, n, tc, vis, vo) in enumerate(scenes):
    x = 30 + (i % cols) * cellw
    y = 140 + (i // cols) * cellh
    rf = (vframe(REF, rt) * 255).astype(np.uint8)
    sheet.paste(Image.fromarray(rf).resize((tw, th)), (x, y))
    sheet.paste(Image.open(f'{OUT}/scene_{n:02d}.jpg').resize((tw, th), Image.LANCZOS), (x + tw + 30, y))
    d.text((x + tw + 4, y + th / 2 - 14), '→', font=G.F(800, 22), fill=(230, 5, 133))
    d.rounded_rectangle([x + tw + 30, y, x + tw + 30 + 66, y + 30], 8, fill=(230, 5, 133))
    d.text((x + tw + 38, y + 4), tc, font=G.F(700, 19), fill=(255, 255, 255))
    yy = y + th + 8
    for ln in textwrap.wrap(vo, 44)[:2]:
        d.text((x, yy), ln, font=G.F(700, 17), fill=(255, 255, 255))
        yy += 22
    for ln in textwrap.wrap(vis, 52)[:4]:
        d.text((x, yy + 4), ln, font=G.F(500, 15), fill=(165, 165, 165))
        yy += 19
for i, col in enumerate(((230, 5, 133), (45, 200, 146), (255, 66, 0), (105, 255, 0))):
    d.rectangle([int(sheet.width * i / 4), sheet.height - 10, int(sheet.width * (i + 1) / 4), sheet.height], fill=col)
dst = f'{ROOT}/reel/bmhc/name_this_place_by_ear'
os.makedirs(dst, exist_ok=True)
sheet.save(f'{dst}/scenes_storyboard.jpg', quality=92)
print('sheet', sheet.size)
