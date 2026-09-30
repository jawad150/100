"""Cinematic covers for both reels: 1080x1920 (reel) + 1080x1350 (feed 4:5)."""
import numpy as np, cv2, math, functools
import reel as R
from engine import *

GRAD = (hexc('#FFB347'), hexc('#FF4D00'))
T = 1.3   # time used for blob/torus sprite frames

def base(glow=1.3, rays=0.8):
    cv = np.empty((H, W, 3), np.float32)
    R.background(cv, 2.0, glow=glow, rays=rays, grid=0.5)
    return cv

def title(cv, lines, y0, maxw=960, gap=1.12):
    y = y0
    for txt, grad in lines:
        size = min(fit_size(txt, 'Unbounded-900', maxw, 150), 140)
        spr = text_sprite(txt, 'Unbounded-900', size, WHITE, 0.0, grad)
        if grad:
            draw(cv, glow_of(spr, 20, ORANGE, 1.0), 540, y, opacity=0.9, mode='add')
        draw(cv, glow_of(spr, 14, (0, 0, 0), 1.0), 540, y + 8, opacity=0.8)
        draw(cv, spr, 540, y)
        y += size * gap
    return y

def gen_face(t, w, h, cx):
    fr = R.RES.get(t)[1080:2160]
    img = crop_resize(fr, cx, 452, 905 * w / h, 905, w, h)
    bl = cv2.GaussianBlur(img, (0, 0), 1.3)
    return np.clip(img + 0.6 * (img - bl), 0, 1)

def finish(cv, name):
    out = post(cv, 0, bloom=0.6, grain=0.018)
    img = (out * 255 + 0.5).astype(np.uint8)[..., ::-1]
    cv2.imwrite(f'{S}/out/{name}_reel_1080x1920.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(f'{S}/out/{name}_feed_1080x1350.jpg', img[285:1635], [cv2.IMWRITE_JPEG_QUALITY, 95])

# ---------------------------------------------------------------- A: tutorial reel
def thumb_tutorial():
    cv = base()
    # cloned character-sheet panels fanned behind
    for slot, k in enumerate([0, 1, 5, 6, 2, 7, 3, 8]):
        ang = lerp(-62, 62, slot / 7)
        x = 540 + math.sin(math.radians(ang)) * 470
        y = 1130 - math.cos(math.radians(ang)) * 330 + 120
        pc = R.panel_card(k)
        draw3d(cv, pc, x, y, 120, w=pc.shape[1] * 0.95, rz=ang * 0.8, opacity=0.95)
    R.obj3d(cv, 'torus', T, 90, 1640, 200, blur=3, rot=-25)
    R.obj3d(cv, 'capsule', T, 960, 450, 190, blur=5, rot=30)
    # hero card: Genjutsu output face
    face = gen_face(1.0, 620, 775, 760)
    ob = R.chip('output')
    card = R.make_card(face, 620, 775, r=34, glow=0.8, badges=[(ob, 28 + ob.shape[1] / 2 - 30, 50, 1.0, 1.0)])
    draw3d(cv, card, 540, 1070, 0, w=card.shape[1], ry=-8, rx=4, rz=2)
    # tutorial window overlapping bottom-left
    win = cv2.imread(f'{S}/frames/scr/s61.8_040.jpg')[..., ::-1].astype(np.float32) / 255
    wimg = crop_resize(win, 420, 760, 1000, 500, 560, 280)
    bar = cv2.resize(R.window_bar(), (560, 30), interpolation=cv2.INTER_AREA)
    wspr = R.make_card(np.concatenate([bar[..., :3], wimg], 0), 560, 310, r=18, glow=0.6)
    draw3d(cv, wspr, 300, 1420, -60, w=wspr.shape[1], ry=18, rx=6, rz=-5)
    R.obj3d(cv, 'cursor3d', 0, 420, 1470, 70)
    R.obj3d(cv, 'blob_drop', T, 930, 760, 170, rot=8)
    R.obj3d(cv, 'blob_bear', T + 0.5, 950, 1420, 180, rot=-6)
    R.obj3d(cv, 'sphere', T, 110, 1180, 130)
    R.obj3d(cv, 'blob_flower', T, 830, 1560, 120, rot=10)
    # text
    chip = pill('FULL TUTORIAL  ·  4 STEPS', 'Inter-800', 30, fill=(0.05, 0.04, 0.04, 0.8), border=(1, 0.55, 0.2, 0.7),
                dot=ORANGE, tracking=0.1)
    draw(cv, chip, 540, 330)
    title(cv, [('HOW I PUT MYSELF', None), ('INTO A MOVIE', GRAD)], 430, maxw=980)
    finish(cv, 'cover_tutorial')

# ---------------------------------------------------------------- B: split-screen result reel
def thumb_result():
    cv = base(glow=1.2, rays=0.6)
    R.obj3d(cv, 'torus', T, 80, 700, 200, blur=3, rot=-20)
    R.obj3d(cv, 'capsule', T, 985, 500, 170, blur=5, rot=30)
    cw, ch = 1000, 458
    top = R.res_half_crop(0.9, 0, cw, ch)
    bot = R.res_half_crop(0.9, 1, cw, ch)
    ot, og = R.chip('original'), R.chip('genjutsu')
    s = 1.35
    t_card = R.make_card(top, cw, ch, r=30, glow=0.3, badges=[(ot, 26 + ot.shape[1] * s / 2 - 30, 50, s, 1.0)])
    b_card = R.make_card(bot, cw, ch, r=30, glow=0.7, badges=[(og, 26 + og.shape[1] * s / 2 - 30, 50, s, 1.0)])
    R.obj3d(cv, 'blob_drop', T, 880, 690, 190, rot=8)
    draw3d(cv, t_card, 540, 845, 0, w=t_card.shape[1], ry=-4, rx=-3)
    draw3d(cv, b_card, 540, 1330, 0, w=b_card.shape[1], ry=4, rx=3)
    draw(cv, ring_sprite(260, 60, 3, ORANGE2), 540, 1088, scale=1.2, opacity=0.7, mode='add')
    draw(cv, R.connector(), 540, 1088, scale=1.25)
    R.obj3d(cv, 'blob_bear', T + 0.5, 120, 1560, 180, rot=-8)
    R.obj3d(cv, 'sphere', T, 985, 1560, 150)
    vs = pill('ORIGINAL  vs  AI', 'Inter-900', 30, fill=(0.05, 0.04, 0.04, 0.85), border=(1, 0.55, 0.2, 0.7),
              icon=R.star_icon(26, ORANGE2), tracking=0.1)
    draw(cv, vs, 540, 1600)
    title(cv, [('I PUT MYSELF', None), ('INTO A MOVIE', GRAD)], 385, maxw=960)
    finish(cv, 'cover_result')

if __name__ == '__main__':
    thumb_tutorial()
    thumb_result()
    print('covers done')
