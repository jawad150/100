"""Key-frame images (one per scene) for IC London "What Is the SQE?" — 1080x1920, brand navy/red, real 3D props.

Usage: python3 frames_sqe.py   -> workspace_sqe/frames/scene_1..6.png + contact sheet
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import reel_sol as R
from reel_sol import (W, H, draw, blur_sprite, tint, rrect, ts, wspr, check, icon, chip, bg, grid_layer, load_png_sprite,
                      NAVY, RED, RED_L, WHITE_, ICE, INK, GREY, LINE, F9, F8, F7, F6, F5, hexc, paste_spr)

SQ = os.path.abspath(os.path.join(HERE, '..', 'workspace_sqe'))
SOL = os.path.abspath(os.path.join(HERE, '..', 'workspace_sol'))
OUT = f'{SQ}/frames'
T = 1.5


def prop(name):
    return load_png_sprite(f'{SQ}/assets/{name}.png')


def last(seq, root=SOL):
    fs = sorted(glob.glob(f'{root}/assets/{seq}/*.png'))
    return load_png_sprite(fs[-1])


def shadowed(c, spr, x, y, sc=1.0, op=0.45):
    draw(c, blur_sprite(tint(spr, (0.0, 0.02, 0.1)), 22), x + 14, y + 34, scale=sc, opacity=op)
    draw(c, spr, x, y, scale=sc)


def line_text(c, parts, x, y, size, font=F9, align='left'):
    """One line of words with individual colours on a shared baseline."""
    sprs = [wspr(w, font, size, col) for w, col in parts]
    sp = size * 0.13
    total = sum(s.shape[1] for s in sprs) + sp * (len(sprs) - 1)
    xx = x if align == 'left' else x - total / 2
    for s in sprs:
        draw(c, s, xx + s.shape[1] / 2, y)
        xx += s.shape[1] + sp
    return total


def logo_badge(c, dark=True):
    lg = load_png_sprite(f'{SQ}/src/logo_full.png')
    sc = 0.36
    w, h = lg.shape[1] * sc + 44, lg.shape[0] * sc + 30
    draw(c, rrect(w, h, 22, (1, 1, 1, 0.96)), 70 + w / 2, 110)
    draw(c, lg, 70 + w / 2, 110, scale=sc)


def pill(c, text, x, y, fill=RED, ink=WHITE_, size=30, align='center', font=F8, trk=0.1):
    s = ts(text, font, size, ink, trk)
    w, h = s.shape[1] + 56, s.shape[0] + 30
    cx = x if align == 'center' else x + w / 2
    draw(c, rrect(w, h, h / 2, fill), cx, y)
    draw(c, s, cx, y)
    return w


def skyline(c, base_y, col=LINE, op=0.5):
    """Thin line-art London skyline: St Paul's, the Shard, the Gherkin and Big Ben."""
    lay = np.zeros((H, W), np.uint8)
    pts = [(0, base_y), (90, base_y), (90, base_y - 120), (150, base_y - 120), (150, base_y - 60), (200, base_y - 60)]
    cv2.polylines(lay, [np.array(pts, np.int32)], False, 255, 3, cv2.LINE_AA)
    cv2.ellipse(lay, (300, base_y - 160), (95, 95), 0, 180, 360, 255, 3, cv2.LINE_AA)            # St Paul's dome
    cv2.line(lay, (300, base_y - 255), (300, base_y - 300), 255, 3, cv2.LINE_AA)
    cv2.rectangle(lay, (190, base_y - 160), (410, base_y), 255, 3, cv2.LINE_AA)
    cv2.polylines(lay, [np.array([(470, base_y), (560, base_y - 520), (650, base_y)], np.int32)], False, 255, 3, cv2.LINE_AA)  # Shard
    cv2.ellipse(lay, (760, base_y - 170), (60, 170), 0, 0, 360, 255, 3, cv2.LINE_AA)               # Gherkin
    cv2.rectangle(lay, (880, base_y - 330), (950, base_y), 255, 3, cv2.LINE_AA)                     # Big Ben
    cv2.polylines(lay, [np.array([(880, base_y - 330), (915, base_y - 420), (950, base_y - 330)], np.int32)], False, 255, 3, cv2.LINE_AA)
    cv2.circle(lay, (915, base_y - 270), 22, 255, 3, cv2.LINE_AA)
    cv2.line(lay, (0, base_y), (W, base_y), 255, 3, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255 * op
    return c * (1 - m) + np.array(col[:3], np.float32) * m


def ice_bg():
    c = np.ones((H, W, 3), np.float32) * np.array(ICE[:3], np.float32)
    return c - grid_layer()[:H, :W][..., None] * 0.12


# ------------------------------------------------------------------ scenes
def scene1():
    c = bg(T)
    logo_badge(c)
    pill(c, 'SQE EXPLAINED  ·  30 SEC', 540, 250, size=26)
    line_text(c, [('Confused', WHITE_), ('about', WHITE_)], 540, 400, 104, align='center')
    line_text(c, [('the', WHITE_), ('SQE?', RED)], 540, 520, 120, align='center')
    line_text(c, [("Let's", GREY), ('simplify', GREY), ('it.', GREY)], 540, 650, 58, font=F8, align='center')
    k = prop('knot')
    shadowed(c, k, 540, 1150, 1.15)
    for j, (txt, x, y, rot) in enumerate([('SQE1', 170, 900, -12), ('FLK', 900, 960, 10), ('QWE', 150, 1420, 8), ('SRA', 930, 1440, -9),
                                          ('SQE2', 260, 1660, 6), ('MCQ', 820, 1690, -6)]):
        s = ts(txt, F9, 40, WHITE_, 0.06)
        p_ = rrect(s.shape[1] + 50, 74, 37, NAVY if j % 2 else RED)
        draw(c, blur_sprite(tint(p_, (0, 0, 0.1)), 12), x + 6, y + 12, rot=rot, opacity=0.5)
        draw(c, p_, x, y, rot=rot)
        draw(c, s, x, y, rot=rot)
    shadowed(c, last('qmark'), 860, 800, 0.62)
    return c


def scene2():
    c = bg(T)
    c = skyline(c, 1330, op=0.35)
    logo_badge(c)
    line_text(c, [('What', WHITE_), ('is', WHITE_), ('the', WHITE_), ('SQE?', RED)], 540, 330, 96, align='center')
    shadowed(c, prop('letters'), 540, 1030, 1.05)
    y = 1520
    parts = [('S', RED), ('olicitors', WHITE_)]
    line_text(c, [('Solicitors', WHITE_)], 540, y, 64, font=F8, align='center')
    line_text(c, [('Qualifying', WHITE_)], 540, y + 82, 64, font=F8, align='center')
    line_text(c, [('Examination', WHITE_)], 540, y + 164, 64, font=F8, align='center')
    for k, (yy, word) in enumerate([(y, 'Solicitors'), (y + 82, 'Qualifying'), (y + 164, 'Examination')]):
        full = wspr(word, F8, 64, WHITE_).shape[1]
        first = wspr(word[0], F8, 64, RED)
        draw(c, first, 540 - full / 2 + first.shape[1] / 2, yy)
    pill(c, 'ENGLAND & WALES', 540, 1790, fill=NAVY, size=28)
    return c


def scene3():
    c = bg(T)
    logo_badge(c)
    pill(c, 'STEP 1', 70, 260, size=28, align='left')
    line_text(c, [('SQE1', RED)], 70, 400, 150)
    line_text(c, [('Functioning', WHITE_), ('Legal', WHITE_)], 70, 540, 64, font=F8)
    line_text(c, [('Knowledge', WHITE_)], 70, 620, 64, font=F8)
    shadowed(c, prop('arch1'), 360, 1080, 0.95)
    shadowed(c, prop('papers'), 720, 1330, 0.85)
    w = pill(c, '2 multiple-choice exams', 540, 1660, fill=(1, 1, 1, 1), ink=INK, size=34, font=F7, trk=0.0)
    draw(c, check(50), 540 - w / 2 - 40, 1660)
    pill(c, 'Ethics tested throughout', 540, 1765, fill=NAVY, size=30, font=F7, trk=0.0)
    return c


def scene4():
    c = bg(T)
    logo_badge(c)
    pill(c, 'STEP 2', 70, 260, size=28, align='left')
    line_text(c, [('SQE2', RED)], 70, 400, 150)
    line_text(c, [('Practical', WHITE_), ('Legal', WHITE_), ('Skills', WHITE_)], 70, 540, 64, font=F8)
    shadowed(c, prop('arch2'), 540, 1060, 0.8)
    for name, x, y in [('speech', 190, 820), ('lectern', 900, 840), ('magnifier', 180, 1300), ('pen', 900, 1300)]:
        shadowed(c, prop(name), x, y, 0.5)
    chips = ['Client interview', 'Advocacy', 'Legal research', 'Legal writing', 'Legal drafting', 'Case analysis']
    for j, txt in enumerate(chips):
        x = 290 if j % 2 == 0 else 790
        y = 1540 + (j // 2) * 92
        s = ts(txt, F7, 32, INK)
        card = rrect(430, 74, 37, (1, 1, 1, 1)).copy()
        paste_spr(card, check(40), 40, 37)
        paste_spr(card, s, 76 + s.shape[1] / 2, 37)
        draw(c, card, x, y)
    pill(c, 'Oral + written assessments', 540, 1830, fill=NAVY, size=28, font=F7, trk=0.0)
    return c


def scene5():
    c = bg(T)
    logo_badge(c)
    line_text(c, [('How', WHITE_), ('it', WHITE_), ('all', WHITE_), ('fits', RED)], 70, 330, 96)
    stops = [('Degree', 'any subject, or equivalent', None, last('cap')),
             ('SQE1', 'legal knowledge', 'ok', prop('arch1')),
             ('SQE2', 'practical skills', 'ok', prop('arch2')),
             ('QWE', "2 years' qualifying work experience", None, prop('calendar')),
             ('Character & suitability', "the SRA's checks", 'ok', last('ic_shield'))]
    x0, y0, dy = 140, 560, 230
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (x0, y0), (x0, y0 + dy * 5), 255, 10, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255
    c = c + cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 10)[..., None] * np.array(LINE[:3], np.float32) * 0.5
    c = c * (1 - m) + np.array(LINE[:3], np.float32) * m
    for j, (title, sub, ok, spr) in enumerate(stops):
        y = y0 + j * dy
        draw(c, rrect(64, 64, 32, RED if ok else WHITE_), x0, y)
        draw(c, check(64) if ok else ts(str(j + 1), F9, 32, NAVY), x0, y)
        s1 = wspr(title, F8, 48, WHITE_)
        draw(c, s1, x0 + 60 + s1.shape[1] / 2, y - 18)
        s2 = wspr(sub, F6, 30, GREY)
        draw(c, s2, x0 + 60 + s2.shape[1] / 2, y + 30)
        sc = {'Degree': 0.5, 'SQE1': 0.26, 'SQE2': 0.26, 'QWE': 0.36, 'Character & suitability': 0.42}[title]
        draw(c, blur_sprite(rrect(170, 170, 85, (0.55, 0.68, 1.0, 1)), 30), 930, y, opacity=0.18, mode='add')
        shadowed(c, spr, 930, y, sc, 0.35)
    yq = y0 + 5 * dy - 20
    draw(c, rrect(84, 84, 42, RED), x0, yq)
    draw(c, check(84), x0, yq)
    line_text(c, [('Qualified', WHITE_), ('Solicitor', RED)], x0 + 70, yq, 64)
    shadowed(c, prop('door'), 950, yq + 40, 0.26, 0.4)
    return c


def scene6():
    c = ice_bg()
    lg = load_png_sprite(f'{SQ}/src/logo_full.png')
    draw(c, blur_sprite(tint(lg, (0.0, 0.05, 0.2)), 18), 540, 560, scale=1.25, opacity=0.18)
    draw(c, lg, 540, 540, scale=1.25)
    shadowed(c, last('cap'), 860, 300, 0.5, 0.3)
    line_text(c, [('Find', INK), ('out', INK), ('more', INK), ('about', INK)], 540, 930, 72, align='center')
    line_text(c, [('SQE', RED), ('preparation', RED)], 540, 1040, 96, align='center')
    line_text(c, [('at', INK), ('IC', INK), ('London', INK)], 540, 1150, 72, align='center')
    lay = np.zeros((H, W), np.uint8)
    pts = [(300 + 480 * u, 1225 + 12 * math.sin(u * 3.2)) for u in np.linspace(0, 1, 40)]
    cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 9 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(RED[:3], np.float32) * m
    s = ts('iclondon.co.uk', F7, 46, NAVY)
    draw(c, s, 510, 1360)
    bx = 510 + s.shape[1] / 2 + 64
    draw(c, rrect(80, 80, 40, RED), bx, 1360)
    draw(c, R.arrow_spr(), bx, 1360)
    pill(c, '100% ONLINE  ·  STUDY AT YOUR OWN PACE', 540, 1460, fill=NAVY, size=26)
    shadowed(c, prop('letters'), 540, 1700, 0.8, 0.25)
    return c


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    thumbs = []
    for j, fn in enumerate([scene1, scene2, scene3, scene4, scene5, scene6], start=1):
        im = to_u8(R.post(fn(), j, bloom=0.12, grain=0.01, vig=0.4 if j < 6 else 0.0))
        cv2.imwrite(f'{OUT}/scene_{j}.png', im)
        thumbs.append(cv2.resize(im, (360, 640)))
        print('scene', j, flush=True)
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(thumbs[:3]), np.hstack(thumbs[3:])]), [cv2.IMWRITE_JPEG_QUALITY, 90])
