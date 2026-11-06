"""Hulk Marketing "Silence Looks Like Guilt" — static post (1080x1350) + LinkedIn cut (1080x1080).

A 3D night scene (blender_silence.py): an empty restaurant after close, a phone glowing on the table with an unanswered
2-star review. Out of the phone, on a thin lime beam, float the clearly labelled EXAMPLE review and the calm reply, its
four parts marked with numbered lime dots; four lime tags spell the method; the sign-off offers the audit.

Copy is the PDF's, word for word. "Sam P." and "Maple Kitchen" are invented and labelled; the cards are generic, not any
platform's interface.

Usage: python3 post_silence.py -> workspace_silence/post_feed.png, post_linkedin.png
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
from frames_cf import draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_silence'


def hexc(h, a=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


FOREST, LIME, LABEL, SAGE = hexc('#121C17'), hexc('#9DEF69'), hexc('#3C4A42'), hexc('#C9D6CB')
WHITE, INK = (1, 1, 1, 1), hexc('#121C17')
HX, HB = 'Headline-800', 'Headline-900'
HK5, HK7 = 'Hanken-500', 'Hanken-700'

REVIEW = 'Waited 40 minutes past my booking. Food was fine, but nobody told us what was going on.'
REPLY = ["Thanks for telling us, Sam.",
         "You’re right: a 40-minute wait with no update isn’t good enough, and I’m sorry.",
         "We’ve changed how we update tables when the kitchen runs late.",
         "I’d love to make it up to you: please email me at the address on our website."]
TAGS = ['Thank them', 'Own it', 'Fix it', 'Take it offline']


def wrap(text, font, size, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if ts(t, font, size, WHITE).shape[1] <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def star_spr(size, col):
    r = size * 2
    pts = [(r + r * (1 if i % 2 == 0 else 0.45) * math.sin(i * math.pi / 5), r - r * (1 if i % 2 == 0 else 0.45) * math.cos(i * math.pi / 5)) for i in range(10)]
    m = np.zeros((2 * r, 2 * r), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    return solid(cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, col)


def arrow_ne(size=40, col=INK):
    n = int(size * 4)
    m = np.zeros((n, n), np.uint8)
    t = int(size * 0.14 * 4)
    p0, p1 = (int(n * 0.18), int(n * 0.82)), (int(n * 0.8), int(n * 0.2))
    cv2.line(m, p0, p1, 255, t, cv2.LINE_AA)
    cv2.line(m, p1, (int(n * 0.36), int(n * 0.2)), 255, t, cv2.LINE_AA)
    cv2.line(m, p1, (int(n * 0.8), int(n * 0.64)), 255, t, cv2.LINE_AA)
    return solid(cv2.resize(m, (int(size), int(size)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, col)


def card_sprite(w, h, edge=False):
    sp = rrect(w, h, 24, WHITE).copy()
    if edge:
        hh, ww = sp.shape[:2]
        lay = np.zeros((hh, ww), np.float32)
        lay[:, :(ww - w) // 2 + 8] = 1
        m = sp[..., 3] * lay
        sp[..., :3] = sp[..., :3] * (1 - m[..., None]) + np.array(LIME[:3], np.float32) * m[..., None]
    return sp


def avatar(letter, d, fill, ink):
    sp = rrect(d, d, d / 2, fill).copy()
    paste_spr(sp, ts(letter, HB, int(d * 0.5), ink), d / 2, d / 2)
    return sp


def num_dot(n, d=34):
    sp = rrect(d, d, d / 2, LIME).copy()
    paste_spr(sp, ts(str(n), HB, int(d * 0.58), INK), d / 2, d / 2 + 1)
    return sp


def review_card(w=620, fs=27):
    pad = 36
    lines = wrap(f'“{REVIEW}”', HK5, fs, w - 2 * pad)
    h = 140 + len(lines) * int(fs * 1.4) + 22
    sp = card_sprite(w, h)
    paste_spr(sp, avatar('S', 64, SAGE, LABEL), pad + 32, 62)
    n = ts('Sam P.', HX, 32, INK)
    paste_spr(sp, n, pad + 82 + n.shape[1] / 2, 46)
    for i in range(5):
        paste_spr(sp, star_spr(26, INK if i < 2 else SAGE), pad + 96 + i * 32, 86)
    ex = ts('EXAMPLE', HK7, 20, LABEL, 0.12)
    pw = ex.shape[1] + 30
    paste_spr(sp, rrect(pw, 38, 19, hexc('#EEF2EE')), w - pad - pw / 2, 46)
    paste_spr(sp, ex, w - pad - pw / 2, 46)
    for i, ln in enumerate(lines):
        s = ts(ln, HK5, fs, INK)
        paste_spr(sp, s, pad + s.shape[1] / 2, 140 + i * int(fs * 1.4))
    return sp


def reply_card(w=936, size=25):
    pad, lh = 44, int(size * 1.36)
    blocks = []
    y = 106
    for i, sent in enumerate(REPLY):
        lines = wrap(sent, HK5, size, w - 2 * pad - 52)
        blocks.append((i + 1, y, lines))
        y += len(lines) * lh + 8
    h = y - 14
    sp = card_sprite(w, h, edge=True)
    paste_spr(sp, avatar('M', 56, FOREST, LIME), pad + 28, 54)
    t1 = ts('Reply from Maple Kitchen', HX, 30, INK)
    paste_spr(sp, t1, pad + 72 + t1.shape[1] / 2, 44)
    t2 = ts('(fictional)', HK5, 22, LABEL)
    paste_spr(sp, t2, pad + 72 + t2.shape[1] / 2, 76)
    ex = ts('EXAMPLE', HK7, 20, LABEL, 0.12)
    pw = ex.shape[1] + 30
    paste_spr(sp, rrect(pw, 38, 19, hexc('#EEF2EE')), w - pad - pw / 2, 46)
    paste_spr(sp, ex, w - pad - pw / 2, 46)
    for n, y0, lines in blocks:
        paste_spr(sp, num_dot(n), pad + 17, y0 + 2)
        for j, ln in enumerate(lines):
            s = ts(ln, HK5, size, INK)
            paste_spr(sp, s, pad + 52 + s.shape[1] / 2, y0 + j * lh)
    return sp


def float_card(c, sp, x, y, rot, glow=None):
    if glow is not None:
        draw(c, blur_sprite(tint(sp, glow[:3]), 34), x, y, rot=rot, opacity=0.55)
    draw(c, blur_sprite(tint(sp, (0, 0, 0)), 30), x + 10, y + 30, rot=rot, opacity=0.6)
    draw(c, sp, x, y, rot=rot)


def beam(c, p0, p1, w=3):
    H_, W_ = c.shape[:2]
    lay = np.zeros((H_, W_), np.uint8)
    pts = [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * (p1[0] + 60) + u * u * p1[0],
            (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * ((p0[1] + p1[1]) / 2) + u * u * p1[1]) for u in np.linspace(0, 1, 50)]
    cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, w * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    g = cv2.GaussianBlur(m[..., 0], (0, 0), 10)[..., None]
    c[:] = np.clip(c + g * np.array(LIME[:3], np.float32) * 1.2 + m * np.array(LIME[:3], np.float32), 0, 1)
    for p in (p0, p1):
        gg = np.exp(-((np.arange(W_)[None, :] - p[0]) ** 2 + (np.arange(H_)[:, None] - p[1]) ** 2) / (2 * 22 ** 2))[..., None]
        c[:] = np.clip(c + gg * np.array(LIME[:3], np.float32) * 0.9, 0, 1)


def tag(c, n, text, x, y):
    s = ts(text, HX, 26, INK)
    d = num_dot(n, 30)
    w = s.shape[1] + d.shape[1] + 44
    draw(c, rrect(w, 52, 26, LIME), x + w / 2, y)
    draw(c, d if False else rrect(30, 30, 15, FOREST), x + 22 + 15, y)
    draw(c, ts(str(n), HB, 18, LIME), x + 22 + 15, y + 1)
    draw(c, s, x + 22 + 30 + 10 + s.shape[1] / 2, y)
    return w


def headline(c, x, y, size):
    m1 = _wmask('Silence looks', HB, size)
    draw(c, blur_sprite(solid(m1, (0, 0, 0, 1)), 16), x + m1.shape[1] / 2 + 3, y + 8, opacity=0.6)
    draw(c, solid(m1, WHITE), x + m1.shape[1] / 2, y)
    y2 = y + size * 1.05
    m2 = _wmask('like', HB, size)
    draw(c, blur_sprite(solid(m2, (0, 0, 0, 1)), 16), x + m2.shape[1] / 2 + 3, y2 + 8, opacity=0.6)
    draw(c, solid(m2, WHITE), x + m2.shape[1] / 2, y2)
    gx = x + m2.shape[1] + size * 0.22
    m3 = _wmask('guilt.', HB, size)
    blk = rrect(m3.shape[1] + size * 0.24, size * 1.08, 12, LIME)
    draw(c, blur_sprite(blk, 26), gx + m3.shape[1] / 2, y2 + size * 0.04, opacity=0.7)
    draw(c, blk, gx + m3.shape[1] / 2, y2 + size * 0.04)
    draw(c, solid(m3, INK), gx + m3.shape[1] / 2, y2)


def logo(c, x, y, w=230):
    lg = load_png_sprite(f'{ROOT}/workspace_hulk/web/hulk-marketing-logo.png')
    draw(c, lg, x + w / 2, y, scale=w / lg.shape[1])


def eyebrow(c, x, y):
    s = ts('REPUTATION · HOW TO REPLY', HK7, 22, LIME, 0.2)
    w = s.shape[1] + 40
    lay = rrect(w, 46, 23, (0.62, 0.94, 0.41, 0.14))
    draw(c, lay, x + w / 2, y)
    draw(c, s, x + w / 2, y)


def button(c, x, y, w=560, h=88):
    b = rrect(w, h, h / 2, LIME)
    draw(c, blur_sprite(b, 26), x + w / 2, y + 6, opacity=0.6)
    draw(c, b, x + w / 2, y)
    s = ts('Get Free Reputation Audit', HX, 32, INK)
    a = arrow_ne(30, INK)
    tw = s.shape[1] + 12 + a.shape[1]
    draw(c, s, x + w / 2 - tw / 2 + s.shape[1] / 2, y)
    draw(c, a, x + w / 2 + tw / 2 - a.shape[1] / 2, y - 2)


def background(W_=1080, H_=1350):
    im = cv2.imread(f'{S}/render.png')[..., ::-1].astype(np.float32) / 255
    im = cv2.resize(im, (W_, int(im.shape[0] * W_ / im.shape[1])), interpolation=cv2.INTER_AREA)
    if im.shape[0] != H_:
        y0 = max(0, (im.shape[0] - H_) // 2)
        im = im[y0:y0 + H_]
    Y = np.arange(H_, dtype=np.float32)[:, None, None]
    top = np.clip(1 - Y / 600, 0, 1) ** 1.4
    bot = np.clip((Y - 880) / 380, 0, 1) ** 1.2
    f = np.array(FOREST[:3], np.float32)
    im = im * (1 - 0.72 * top) + f * 0.72 * top
    im = im * (1 - 0.55 * bot) + f * 0.55 * bot
    return np.clip(im, 0, 1).astype(np.float32)


def feed():
    c = background()
    logo(c, 72, 84, 300)
    eyebrow(c, 72, 156)
    headline(c, 72, 228, 90)
    # the example review floats up out of the phone on a lime beam
    rc = review_card(580)
    ry0 = 382 + rc.shape[0] / 2
    beam(c, (770, 600), (650, ry0 + 10))
    float_card(c, rc, 72 + 290, ry0, -2.0)
    rp = reply_card(936)
    ry = ry0 + rc.shape[0] / 2 + 16 + rp.shape[0] / 2
    float_card(c, rp, 540, ry, 1.0, glow=LIME)
    ty = ry + rp.shape[0] / 2 + 40
    x = 72
    for i, t in enumerate(TAGS):
        x += tag(c, i + 1, t, x, ty) + 12
    s = ts('Never miss a review again.', HX, 36, WHITE)
    draw(c, s, 72 + s.shape[1] / 2, ty + 70)
    button(c, 72, ty + 146, 540, 84)
    u = ts('hulkmarketing.co.uk', HK7, 26, (1, 1, 1, 0.8))
    draw(c, u, 1008 - u.shape[1] / 2, ty + 146)
    print('bottom of button', ty + 146 + 42)
    return c


def linkedin():
    """1:1 cut for LinkedIn (PDF): no eyebrow; tighter layout; the logo moves top-right."""
    c = background(1080, 1350)[150:1230].copy()
    lg = load_png_sprite(f'{ROOT}/workspace_hulk/web/hulk-marketing-logo.png')
    draw(c, lg, 1008 - 130, 70, scale=260 / lg.shape[1])
    headline(c, 72, 120, 78)
    rc = review_card(540, 24)
    ry0 = 262 + rc.shape[0] / 2
    beam(c, (770, 470), (620, ry0 + 10))
    float_card(c, rc, 72 + 270, ry0, -2.0)
    rp = reply_card(936, 24)
    ry = ry0 + rc.shape[0] / 2 + 12 + rp.shape[0] / 2
    float_card(c, rp, 540, ry, 1.0, glow=LIME)
    ty = ry + rp.shape[0] / 2 + 36
    x = 72
    for i, t in enumerate(TAGS):
        x += tag(c, i + 1, t, x, ty) + 12
    button(c, 72, ty + 82, 520, 76)
    u = ts('hulkmarketing.co.uk', HK7, 26, (1, 1, 1, 0.8))
    draw(c, u, 1008 - u.shape[1] / 2, ty + 82)
    print('linkedin bottom', ty + 82 + 38)
    return c


if __name__ == '__main__':
    f = feed()
    rng = np.random.default_rng(2)
    f = np.clip(f + cv2.GaussianBlur(rng.normal(0, 1, f.shape[:2]).astype(np.float32), (0, 0), 0.7)[..., None] * 0.008, 0, 1)
    cv2.imwrite(f'{S}/post_feed.png', F.to_u8(f))
    l = linkedin()
    cv2.imwrite(f'{S}/post_linkedin.png', F.to_u8(l))
    print('posts')
