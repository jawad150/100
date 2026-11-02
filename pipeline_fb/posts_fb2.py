"""Organic Fostering "The Family Book" — 3 new design treatments (1080x1350), same realistic family-book renders.

D · Editorial Split  — photo top, deep plum panel below with ivory type and a handwritten "say hello."
E · Gradient Frame   — brand magenta-to-orange background, the open book as a framed photo card, round sticker
F · Note Card        — full-bleed closed book, big handwritten "Hello! This is us.", a white card holding the message

Usage: python3 posts_fb2.py [D E F] -> workspace_fb/posts/option_X.png + overview2.jpg
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_respite'))
import numpy as np
import cv2
import posts_respite as P
from posts_respite import F, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, N9, N8, N7, PW, PH, YY, XX, CREAM, text, logo

S = '/home/user/100/workspace_fb'
OUT = f'{S}/posts'
HAND = 'Caveat-700'
IVORY = (1.0, 0.98, 0.95, 1)
WHITE = (1, 1, 1, 1)


def load(mode, w=PW, h=PH, fx=0.5, fy=0.5):
    im = cv2.imread(f'{S}/tex/render_{mode}.png')[..., ::-1].astype(np.float32) / 255
    ih, iw = im.shape[:2]
    s = max(w / iw, h / ih)
    cw, ch = w / s, h / s
    x0 = int(np.clip(fx * iw - cw / 2, 0, iw - cw)); y0 = int(np.clip(fy * ih - ch / 2, 0, ih - ch))
    return P.warm_grade(cv2.resize(im[y0:y0 + int(ch), x0:x0 + int(cw)], (w, h), interpolation=cv2.INTER_AREA), 0.5)


def hand(c, s, x, y, size, col, rot=0, anchor='l'):
    sp = solid(_wmask(s, HAND, size), col)
    xx = x + sp.shape[1] / 2 if anchor == 'l' else x
    draw(c, sp, xx, y, rot=rot)
    return sp.shape[1]


def pill(c, label, x, y, fill, ink, size=24):
    sp = ts(label, 'Poppins-SemiBold', size, ink, 0.08)
    w = sp.shape[1] + 44
    x = min(x, 1010 - w)
    draw(c, rrect(w, size * 2.2, size * 1.1, fill), x + w / 2, y)
    draw(c, sp, x + w / 2, y)
    return w


def button(c, x, y, label='Ask how matching works', w=520, h=86, light=False):
    if light:
        b = rrect(w, h, h / 2, IVORY)
        draw(c, b, x + w / 2, y)
        sp = ts(label, N9, 30, PLUM); a = F.arrow(PLUM, 30)
        tw = sp.shape[1] + 14 + a.shape[1]
        draw(c, sp, x + w / 2 - tw / 2 + sp.shape[1] / 2, y); draw(c, a, x + w / 2 + tw / 2 - a.shape[1] / 2, y + 2)
    else:
        b = F.grad_spr(w, h, h / 2)
        draw(c, blur_sprite(b, 16), x + w / 2, y + 8, opacity=0.4)
        draw(c, b, x + w / 2, y)
        F.text_arrow(c, label, x + w / 2, y, size=30)


def footer(c, y, ink):
    text(c, 'organicfostering.co.uk', 70, y, N8, 28, ink)
    sp = ts('0161 241 1332', N9, 30, ink)
    draw(c, sp, 1010 - sp.shape[1] / 2, y)


def white_logo(c, x=70, y=100, w=230):
    lg = F.logo()
    a = lg[..., 3:4]
    wl = np.concatenate([np.ones_like(lg[..., :3]) * a, a], 2)
    draw(c, wl, x + w / 2, y, scale=w / lg.shape[1])


SUB = 'It may include your home, the bedroom, pets, local places and routines.'


# ------------------------------------------------------------------ D: Editorial split
def option_d():
    c = np.zeros((PH, PW, 3), np.float32)
    split = 760
    c[:split] = load('open_angle', PW, split, 0.5, 0.3)
    c[split:] = np.array(PLUM[:3], np.float32)
    # soft blend line + subtle texture on the panel
    g = np.clip((YY - split) / 6, 0, 1)[..., None]
    rng = np.random.default_rng(4)
    noise = cv2.GaussianBlur(rng.normal(0, 1, (PH, PW)).astype(np.float32), (0, 0), 1.0)[..., None] * 0.012
    c = c * (1 - g) + (np.array(PLUM[:3], np.float32) + noise) * g
    top = np.clip(1 - YY / 230, 0, 1)[..., None] ** 1.3
    c = c * (1 - 0.7 * top) + np.array(CREAM, np.float32) * 0.7 * top
    logo(c)
    pill(c, 'HOW MATCHING WORKS', 760, 100, IVORY, PLUM)
    # big sticker on the seam
    st = rrect(230, 230, 115, ORANGE).copy()
    for li, ln in enumerate(('What is a', 'family', 'book?')):
        paste_spr(st, ts(ln, N9, 38 if li != 1 else 46, WHITE), 115, 70 + li * 46)
    draw(c, blur_sprite(tint(st, (0.2, 0.05, 0.05)), 14), 900 + 6, split - 10 + 12, rot=-10, opacity=0.4)
    draw(c, st, 900, split - 10, rot=-10)
    text(c, 'Before a child arrives,', 70, split + 110, N9, 70, IVORY)
    text(c, 'a family book can', 70, split + 190, N9, 70, IVORY)
    hand(c, 'say hello.', 70, split + 285, 118, (1.0, 0.55, 0.25, 1), rot=-2)
    text(c, SUB, 70, split + 385, N7, 27, (1, 1, 1, 0.82))
    button(c, 70, split + 470, light=True)
    footer(c, split + 545, (1, 1, 1, 0.9))
    return P.grain(c, 0.008)


# ------------------------------------------------------------------ E: Gradient frame
def option_e():
    u = (XX / PW * 0.55 + YY / PH * 0.45)[..., None]
    c = np.array(PURPLE[:3], np.float32) * (1 - u) + np.array(ORANGE[:3], np.float32) * u
    # soft light blobs
    for x, y, r, a in ((200, 300, 420, 0.18), (950, 1150, 380, 0.14)):
        gb = np.exp(-((XX - x) ** 2 + (YY - y) ** 2) / (2 * r * r))[..., None] * a
        c = c + gb
    c = np.clip(c, 0, 1)
    white_logo(c)
    pill(c, 'HOW MATCHING WORKS', 760, 100, (1, 1, 1, 0.18), WHITE)
    text(c, 'Before a child arrives,', 70, 225, N9, 68, WHITE)
    w = text(c, 'a family book can', 70, 300, N9, 68, WHITE)
    hand(c, 'say hello.', 70 + w + 18, 296, 96, (1.0, 0.9, 0.55, 1), rot=-3)
    # framed photo card
    cw, ch = 900, 700
    photo = load('open_top', cw - 36, ch - 36, 0.5, 0.56)
    card = rrect(cw, ch, 30, WHITE).copy()
    m = cv2.resize(F.R.sdf_fill(F.R.rrect_alpha(cw - 36, ch - 36, 18, 2)), (cw - 36, ch - 36))
    paste_spr(card, np.concatenate([photo * m[..., None], m[..., None]], 2).astype(np.float32), cw / 2, ch / 2)
    draw(c, blur_sprite(tint(card, (0.25, 0.02, 0.15)), 30), PW / 2 + 10, 770 + 30, rot=-2, opacity=0.5)
    draw(c, card, PW / 2, 770, rot=-2)
    # round sticker
    st = rrect(200, 200, 100, (1.0, 0.94, 0.6, 1)).copy()
    for li, ln in enumerate(('Hello!', 'This is us.')):
        paste_spr(st, solid(_wmask(ln, HAND, 52 if li == 0 else 40), PLUM), 100, 78 + li * 50)
    draw(c, blur_sprite(tint(st, (0.2, 0.05, 0.05)), 12), 900 + 6, 470 + 10, rot=12, opacity=0.4)
    draw(c, st, 900, 470, rot=12)
    text(c, SUB, 70, 1180, N7, 27, WHITE)
    button(c, 70, 1250, light=True)
    sp = ts('0161 241 1332', N9, 30, WHITE)
    draw(c, sp, 1010 - sp.shape[1] / 2, 1225)
    draw(c, ts('organicfostering.co.uk', N8, 26, (1, 1, 1, 0.9)), 1010 - ts('organicfostering.co.uk', N8, 26, WHITE).shape[1] / 2, 1275)
    return P.grain(c, 0.008)


# ------------------------------------------------------------------ F: Note card
def option_f():
    c = load('closed', PW, PH, 0.5, 0.5)
    c = P.vignette(c, 0.25)
    logo(c)
    pill(c, 'HOW MATCHING WORKS', 760, 100, IVORY, PLUM)
    # handwritten callout pointing at the cover label
    hand(c, 'What’s inside?', 650, 300, 70, PLUM, rot=-6)
    lay = np.zeros((PH, PW), np.uint8)
    pts = np.array([(700, 345), (640, 420), (575, 470)], np.float32)
    t = np.linspace(0, 1, 40)
    curve = np.array([(1 - s) ** 2 * pts[0] + 2 * (1 - s) * s * pts[1] + s ** 2 * pts[2] for s in t])
    cv2.polylines(lay, [(curve * 4).astype(np.int32)], False, 255, 6 * 4, cv2.LINE_AA, shift=2)
    for ang in (2.5, -2.5):
        dv = curve[-1] - curve[-6]; dv /= np.linalg.norm(dv)
        rm = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        e = curve[-1] + rm @ dv * 26
        cv2.line(lay, tuple((curve[-1] * 4).astype(int)), tuple((e * 4).astype(int)), 255, 6 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(PLUM[:3], np.float32) * m
    # the message card
    cw, ch = 960, 470
    card = rrect(cw, ch, 36, (1, 1, 1, 0.97))
    draw(c, blur_sprite(tint(card, (0.25, 0.1, 0.05)), 30), PW / 2, 1080 + 26, opacity=0.45)
    draw(c, card, PW / 2, 1080)
    x0 = PW / 2 - cw / 2 + 50
    text(c, 'Before a child arrives,', x0, 905, N9, 60, PLUM)
    w = text(c, 'a family book can', x0, 970, N9, 60, PLUM)
    hand(c, 'say hello.', x0 + w + 16, 966, 84, ORANGE, rot=-2)
    text(c, SUB, x0, 1040, N7, 25, (0.36, 0.09, 0.31, 0.85))
    button(c, x0, 1125, w=500)
    footer_y = 1215
    text(c, 'organicfostering.co.uk', x0, footer_y, N8, 26, PLUM)
    sp = ts('0161 241 1332', N9, 28, PLUM)
    draw(c, sp, PW / 2 + cw / 2 - 50 - sp.shape[1] / 2, footer_y)
    return P.grain(c, 0.01)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:] or ['D', 'E', 'F']
    for k in want:
        im = {'D': option_d, 'E': option_e, 'F': option_f}[k]()
        cv2.imwrite(f'{OUT}/option_{k}.png', F.to_u8(im))
        print('option', k, flush=True)
    th = [cv2.resize(cv2.imread(f'{OUT}/option_{k}.png'), (540, 675)) for k in 'DEF' if os.path.exists(f'{OUT}/option_{k}.png')]
    if len(th) == 3:
        g = np.ones((675, 24, 3), np.uint8) * 245
        cv2.imwrite(f'{OUT}/overview2.jpg', np.hstack([th[0], g, th[1], g, th[2]]), [cv2.IMWRITE_JPEG_QUALITY, 92])
