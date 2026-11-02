"""Organic Fostering "The Family Book" — how matching works. Static post, 3 realistic options (1080x1350).

A · Hello, This Is Us  — overhead flat lay of the open family book (the PDF concept)
B · Page One           — a low, close angle on page one with soft depth of field
C · Closed Book        — the closed book, "Hello! This is us." on the cover, prints spilling out around it

Usage: python3 posts_fb.py [A B C] -> workspace_fb/posts/option_X.png + overview.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_respite'))
import numpy as np
import cv2
import posts_respite as P
from posts_respite import F, draw, blur_sprite, tint, rrect, ts, solid, _wmask, PURPLE, ORANGE, PLUM, N9, N8, N7, PW, PH, YY, XX, CREAM, text, logo

S = '/home/user/100/workspace_fb'
OUT = f'{S}/posts'


def eyebrow(c, label='HOW MATCHING WORKS', x=1010, y=100):
    sp = ts(label, 'Poppins-SemiBold', 25, PLUM, 0.06)
    w = sp.shape[1] + 46
    draw(c, blur_sprite(rrect(w, 56, 28, (0.3, 0.1, 0.05, 0.3)), 10), x - w / 2, y + 5)
    draw(c, rrect(w, 56, 28, (*CREAM, 1)), x - w / 2, y)
    draw(c, sp, x - w / 2, y)


def headline(c, y=215, size=74, x=70):
    text(c, 'Before a child arrives,', x, y, N9, size, PLUM, 0.25)
    text(c, 'a family book can', x, y + size * 1.08, N9, size, PLUM, 0.25)
    text(c, 'say hello.', x, y + size * 2.16, N9, size, ORANGE, 0.25)


def sign_off(c, y=1150, panel=True):
    if panel:
        g = np.clip((YY - (y - 140)) / 140, 0, 1)[..., None] ** 1.2
        c[:] = c * (1 - 0.93 * g) + np.array(CREAM, np.float32) * 0.93 * g
    line = 'It may include your home, the bedroom, pets, local places and routines.'
    size = 32
    while ts(line, N8, size, PLUM).shape[1] > PW - 140 and size > 22:
        size -= 1
    text(c, line, 70, y + 10, N8, size, PLUM)
    bw, bh = 520, 86
    b = F.grad_spr(bw, bh, bh / 2)
    draw(c, blur_sprite(b, 16), 70 + bw / 2, y + 98, opacity=0.4)
    draw(c, b, 70 + bw / 2, y + 90)
    F.text_arrow(c, 'Ask how matching works', 70 + bw / 2, y + 90, size=30)
    text(c, 'organicfostering.co.uk', 70, y + 165, N8, 28, PLUM)
    sp = ts('0161 241 1332', N9, 30, PLUM)
    draw(c, sp, 1010 - sp.shape[1] / 2, y + 165)


def load(mode):
    im = cv2.imread(f'{S}/tex/render_{mode}.png')[..., ::-1].astype(np.float32) / 255
    return cv2.resize(im, (PW, PH), interpolation=cv2.INTER_AREA)


def top_soft(c, h=430, amt=0.3):
    t = np.clip(1 - YY / h, 0, 1)[..., None] ** 1.5
    return c * (1 - amt * t) + np.array(CREAM, np.float32) * amt * t


def option_a():
    c = P.warm_grade(load('open_top'), 0.5)
    c = top_soft(c, 380, 0.25)
    logo(c); eyebrow(c); headline(c)
    sign_off(c, 1140)
    return P.vignette(P.grain(c, 0.01), 0.1)


def option_b():
    c = P.warm_grade(load('open_angle'), 0.6)
    c = top_soft(c, 520, 0.5)
    logo(c); eyebrow(c); headline(c)
    sign_off(c, 1140)
    return P.vignette(P.grain(c, 0.012), 0.14)


def option_c():
    c = P.warm_grade(load('closed'), 0.5)
    c = top_soft(c, 380, 0.25)
    logo(c); eyebrow(c); headline(c)
    sign_off(c, 1140)
    return P.vignette(P.grain(c, 0.01), 0.1)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:] or ['A', 'B', 'C']
    for k in want:
        im = {'A': option_a, 'B': option_b, 'C': option_c}[k]()
        cv2.imwrite(f'{OUT}/option_{k}.png', F.to_u8(im))
        print('option', k, flush=True)
    if len(want) == 3:
        th = [cv2.resize(cv2.imread(f'{OUT}/option_{k}.png'), (540, 675)) for k in 'ABC']
        g = np.ones((675, 24, 3), np.uint8) * 245
        cv2.imwrite(f'{OUT}/overview.jpg', np.hstack([th[0], g, th[1], g, th[2]]), [cv2.IMWRITE_JPEG_QUALITY, 92])
