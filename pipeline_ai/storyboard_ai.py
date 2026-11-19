"""Scene frames (storyboard) for BMHC "AI can recreate this building. But not what happens inside."
-> workspace_ai/board/scene_XX.jpg + reel/bmhc/ai_cannot_recreate/scenes_storyboard.jpg
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import frames_ai as G
from frames_ai import (W, H, S, ROOT, INK, WHITE, MAG, TEAL, ORANGE, LIME, HOLO, canvas, load, cover, grade, grain, pop, caption,
                       prompt_bar, callout, glow_lines, blueprint_bg, eclipse, layercut, four_bar_wipe, retro, aurora, logo, paste,
                       tag, text_sprite, rrect)
import building as BL

OUT = f'{S}/board'
os.makedirs(OUT, exist_ok=True)
DL = f'{S}/dl'
ST = f'{S}/stills'
SEG = BL.segs()


def wire(c, cam, t, hi=None, amt=1.0, width=2.2):
    rgb, a = BL.render_lines(cam, SEG, t, hi=hi, width=width, colour=HOLO)
    rgb, a = glow_lines(rgb, a, 0.8)
    return np.clip(c * (1 - a[..., None] * amt) + rgb * amt, 0, 1)


def save(i, c):
    cv2.imwrite(f'{OUT}/scene_{i:02d}.jpg', (np.clip(c, 0, 1)[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('scene', i, flush=True)


def proj(cam, p):
    q, _ = cam.proj(np.array([p], np.float32))
    return float(q[0, 0]), float(q[0, 1])


# 01 - the prompt, the AI starts drawing
c = blueprint_bg(0.3)
cam = BL.Cam((-22, -58, 4), (0, 0, 14), fov=42)
c = wire(c, cam, 0.42)
prompt_bar(c, 'Recreate this historic Manchester building.', y=330, t=0.1, status='GENERATING  ·  42%')
tag(c, 'HERITAGE', 64, 150, MAG)
caption(c, [('AI can', WHITE), ('recreate this.', MAG)], 1560)
save(1, grain(c, 0.02))

# 02 - every window / every brick / every detail (explainer call-outs + pops), spiral camera
c = blueprint_bg(1.0)
cam = BL.Cam((24, -52, 20), (0, 0, 16), fov=44)
hi = {'window': (MAG, 0.85)}
c = wire(c, cam, 1.1, hi=hi)
callout(c, proj(cam, (12.6, 0, 9.4)), 'WINDOWS ×74', 1.0, side=-1, dy=-260)
callout(c, proj(cam, (-2.1, -2.6, 33.0)), 'DETAIL', 1.0, side=1, dy=-60, col=TEAL)
pop(c, 'window', 330, 640, 380, 1.2, rot=0, glow=np.array((1, 0.7, 0.4), np.float32))
caption(c, [('Every', WHITE), ('window.', MAG)], 1560)
save(2, grain(c, 0.02))

# 03 - every brick (brick-course scan) + every detail (pinnacle)
c = blueprint_bg(2.0)
cam = BL.Cam((-34, -30, 8), (-10, 0, 8), fov=46)
c = wire(c, cam, 1.1)
bl = BL.bricks(s=-1)
lay = np.zeros((H, W), np.uint8)
for p0, p1 in bl:
    q, z = cam.proj(np.array([p0, p1], np.float32))
    if (z > 0.3).all():
        cv2.line(lay, tuple((q[0] * 4).astype(int)), tuple((q[1] * 4).astype(int)), 255, 4, cv2.LINE_AA, shift=2)
m = lay.astype(np.float32)[..., None] / 255
yy = np.mgrid[0:H, 0:W][1].astype(np.float32)
scan = np.clip(1 - np.abs(yy - 640) / 380, 0, 1)[..., None]
c = c * (1 - m * scan) + np.array(MAG) * m * scan
pop(c, 'brick', 760, 520, 420, 1.2)
pop(c, 'pinnacle', 250, 1180, 420, 1.2)
caption(c, [('Every', WHITE), ('brick.', MAG)], 1560)
save(3, grain(c, 0.02))

# 04 - "But it can't recreate what happens inside": eclipse over the lit door
c = blueprint_bg(3.0)
cam = BL.Cam((0, -16, 2.2), (0, 0, 3.0), fov=50)
c = wire(c, cam, 1.2, width=3.0)
dx, dy = proj(cam, (0, -4.6, 1.8))
c = eclipse(c, dx, dy, 260, 0.82)
caption(c, [('But', WHITE), ('not this.', MAG)], 1560)
save(4, grain(c, 0.02))

# 05 - layercut opening onto real life (iftar)
a = c.copy()
b = grade(cover(load(f'{ST}/v_17.3.jpg'), fx=0.6, fy=0.45, z=1.15), warm=0.6, contrast=1.06, sat=1.05, vig=0.45)
c = layercut(a, b, 0.55)
save(5, grain(c, 0.025))

# 06 - the friendships formed (iftar + chai)
c = grade(cover(load(f'{ST}/v_18.3.jpg'), fx=0.6, fy=0.45, z=1.15), warm=0.6, contrast=1.06, sat=1.05, vig=0.45)
pop(c, 'chai', 760, 1140, 400, 1.2)
caption(c, [('The friendships', WHITE), ('formed.', MAG)], 1560)
save(6, grain(c, 0.025))

# 07 - the knowledge passed on (exhibition conversation + book)
c = grade(cover(load(f'{DL}/487090267_1088144326686714_8941517225088640181_n.jpg'), fx=0.42, fy=0.55, z=1.1), warm=0.4, contrast=1.05, vig=0.45)
pop(c, 'book', 320, 1180, 430, 1.2)
caption(c, [('Knowledge', MAG), ('passed on.', WHITE)], 1560)
save(7, grain(c, 0.025))

# 08 - young people finding their confidence (hands up + target)
c = grade(cover(load(f'{ST}/v_12.5.jpg'), fx=0.45, fy=0.4, z=1.05), warm=0.4, contrast=1.08, vig=0.45)
pop(c, 'target', 760, 1120, 400, 1.2)
caption(c, [('Finding their', WHITE), ('confidence.', MAG)], 1560)
save(8, grain(c, 0.025))

# 09 - conversations that bring communities together (bubbles)
c = grade(cover(load(f'{ST}/v_28.5.jpg'), fx=0.33, fy=0.45, z=1.05), warm=0.4, contrast=1.05, vig=0.45)
pop(c, 'bubbles', 540, 1120, 520, 1.2)
caption(c, [('Communities', WHITE), ('together.', MAG)], 1560)
save(9, grain(c, 0.025))

# 10 - what we preserve (retro tower + astrolabe)
c = grade(cover(load(f'{ST}/v_14.5.jpg'), fx=0.55, fy=0.5, z=1.1), contrast=1.1, vig=0.2)
c = retro(c, 1.3)
pop(c, 'astrolabe', 540, 1050, 520, 1.2, shadow=True)
caption(c, [('What we', WHITE), ('preserve.', MAG)], 1560)
save(10, c)

# 11 - what we keep alive (colour + aurora + lantern)
c = grade(cover(load(f'{DL}/476280551_1049256607242153_4186426492440189340_n.jpg'), fx=0.5, fy=0.5, z=1.1), warm=0.5, contrast=1.05, vig=0.4, exp=0.9)
c = aurora(c, 2.0, 0.9, 0.08, 0.3)
pop(c, 'lantern', 540, 1080, 460, 1.2, glow=np.array((1, 0.45, 0.7), np.float32))
caption(c, [('What we keep', WHITE), ('alive.', MAG)], 1560)
save(11, grain(c, 0.025))

# 12 - a living community (aerial + the AI lines dissolving into lit windows)
c = grade(cover(load(f'{ST}/v_37.5.jpg'), fx=0.42, fy=0.6, z=1.0), warm=0.3, contrast=1.06, vig=0.4)
cam = BL.Cam((-6, -95, 55), (0, 0, 2), fov=34)
pass
caption(c, [('A living', WHITE), ('community.', MAG)], 1560)
save(12, grain(c, 0.025))

# 13 - end card on ink
c = canvas(INK)
lg = logo(860)
paste(c, lg, W / 2, 760)
s = text_sprite('COME AND EXPERIENCE IT.', 800, 66, WHITE, track=0.02)
paste(c, s, W / 2, 1080)
s = text_sprite('bmhc.org.uk', 600, 44, (0.75, 0.75, 0.75))
paste(c, s, W / 2, 1170)
pop(c, 'door', 540, 1420, 300, 1.2, glow=np.array((1, 0.7, 0.4), np.float32))
for i, col in enumerate(G.BARS):
    c[H - 22:, int(W * i / 4):int(W * (i + 1) / 4)] = col
save(13, c)

# ---------------- contact sheet
BEATS = [
    ('00:00', 'Black AI screen. The prompt types itself; the façade starts drawing in white lines.', '“AI can recreate a building in seconds.”'),
    ('00:03', 'SPIRAL: camera spirals up the build. EXPLAINER call-outs; a 3D window pops out.', '“Every window…”'),
    ('00:04', 'A brick-course scan sweeps the wing; 3D bricks + the tower’s pinnacle pop.', '“…Every brick. Every detail.”'),
    ('00:06', 'Push into the line-drawn door. ECLIPSE: a dark disc covers it, warm light around it.', '“But it can’t recreate what happens inside.”'),
    ('00:08', 'LAYERCUT: the blueprint slices apart onto real BMHC footage. Digital sound drops away.', '(room tone, real life)'),
    ('00:09', 'Real iftar at BMHC, a plate passed across the table; 3D tea glasses clink.', '“The friendships formed.”'),
    ('00:11', 'Real exhibition: an elder and a young man talking; a 3D book opens, pages flip.', '“The knowledge passed on.”'),
    ('00:13', 'Real hall: hands go up (filmed from behind); the arrow hits the 3D target.', '“The young people finding their confidence.”'),
    ('00:16', 'Real exhibition conversation; “Salaam” and “Hello” bubbles meet. Four-bar wipe.', '“The conversations that bring communities together.”'),
    ('00:19', 'RETRO: the real tower stone as archive film; a 3D astrolabe under a glass dome.', '“Because heritage isn’t only what we preserve.”'),
    ('00:23', 'The dome lifts, the lantern lights. AURORA in BMHC’s four colours; colour floods back.', '“It’s what we keep alive.”'),
    ('00:26', 'Real drone shot of BMHC; the AI lines fade into it and its windows glow warm.', '“British Muslim Heritage Centre. More than a building. A living community.”'),
    ('00:30', 'Fade to ink: BMHC’s own logo + four bars, bmhc.org.uk; the door opens warm.', '“Come and experience it.”'),
]
tw, th = 300, 533
cols = 5
rows = math.ceil(len(BEATS) / cols)
cellh = th + 190
sheet = Image.new('RGB', (cols * (tw + 30) + 30, 150 + rows * cellh + 20), (11, 11, 11))
d = ImageDraw.Draw(sheet)
d.text((30, 30), 'BMHC  ·  AI can recreate this building. But not what happens inside.', font=G.F(800, 40), fill=(255, 255, 255))
d.text((30, 88), '9:16  ·  ~33 s  ·  real BMHC footage + 3D objects on every cue word  ·  scenes for approval', font=G.F(500, 26), fill=(170, 170, 170))
for i, (tc, vis, vo) in enumerate(BEATS):
    im = Image.open(f'{OUT}/scene_{i + 1:02d}.jpg').resize((tw, th), Image.LANCZOS)
    x = 30 + (i % cols) * (tw + 30)
    y = 150 + (i // cols) * cellh
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + 86, y + 36], fill=(230, 5, 133))
    d.text((x + 8, y + 5), tc, font=G.F(700, 22), fill=(255, 255, 255))
    import textwrap
    yy = y + th + 10
    for ln in textwrap.wrap(vo, 30)[:3]:
        d.text((x, yy), ln, font=G.F(700, 19), fill=(255, 255, 255))
        yy += 24
    for ln in textwrap.wrap(vis, 36)[:4]:
        d.text((x, yy + 4), ln, font=G.F(400, 17), fill=(160, 160, 160))
        yy += 22
for i, col in enumerate(G.BARS):
    d.rectangle([int(sheet.width * i / 4), sheet.height - 10, int(sheet.width * (i + 1) / 4), sheet.height], fill=tuple(int(v * 255) for v in col))
dst = f'{ROOT}/reel/bmhc/ai_cannot_recreate'
os.makedirs(dst, exist_ok=True)
sheet.save(f'{dst}/scenes_storyboard.jpg', quality=92)
print('sheet', sheet.size)
