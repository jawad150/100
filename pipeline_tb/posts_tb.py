"""Organic Fostering "Two Toothbrushes" — static post (1080x1350), three 3D options from the concept PDF.

A · The Shelf        — the PDF layout: photoreal 3D close-up (top 56%), ivory panel with the copy
B · Shadow House     — full-bleed: morning sun turns the two brushes and their cup into the shadow of a little house
C · Clay Home        — full-bleed soft-clay miniature: a house-shaped holder, the two brushes leaning together over its roof

Copy (PDF, word for word): "Two toothbrushes. One home." · "Living together can help brothers and sisters keep an
important source of connection during major change." · "Could your home keep them together?" · "Start your enquiry →" ·
0161 241 1332 · real logo bottom-left.

Usage: python3 posts_tb.py [A B C] -> workspace_tb/posts/option_X.png + overview.jpg
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_respite'))
import numpy as np
import cv2
import posts_respite as P
from posts_respite import F, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, N9, N8, N7, PW, PH, YY, XX, CREAM, text

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_tb'
OUT = f'{S}/posts'
HAND = 'Caveat-700'
RED = (0.88, 0.18, 0.24, 1)           # warm red bridging magenta and orange
IVORY = (0.988, 0.973, 0.961)
LAV = (0.965, 0.918, 0.953)
WHITE = (1, 1, 1, 1)
SUB = ['Living together can help brothers and sisters keep an', 'important source of connection during major change.']


def render(name, w=PW, h=PH):
    im = cv2.imread(f'{S}/renders/{name}.png')[..., ::-1].astype(np.float32) / 255
    ih, iw = im.shape[:2]
    s = max(w / iw, h / ih)
    im = cv2.resize(im, (int(round(iw * s)), int(round(ih * s))), interpolation=cv2.INTER_AREA)
    y0 = (im.shape[0] - h) // 2
    x0 = (im.shape[1] - w) // 2
    return im[y0:y0 + h, x0:x0 + w].copy()


def eyebrow(c, x=72, y=110, ink=PLUM, fill=(1, 1, 1, 0.85)):
    s = ts('FOSTERING SIBLINGS', 'Poppins-SemiBold', 24, ink, 0.08)
    w = s.shape[1] + 44
    draw(c, rrect(w, 54, 27, fill), x + w / 2, y)
    draw(c, s, x + w / 2, y)


def headline(c, x, y, size=88, ink=PLUM, accent=RED, center=False):
    for i, (s_, col) in enumerate((('Two toothbrushes.', ink), ('One home.', accent))):
        m = _wmask(s_, N9, size)
        xx = PW / 2 if center else x + m.shape[1] / 2
        draw(c, solid(m, col), xx, y + i * size * 1.06)


def subline(c, x, y, size=30, ink=PLUM, center=False):
    for i, ln in enumerate(SUB):
        s = ts(ln, N7, size, ink)
        draw(c, s, (PW / 2 if center else x + s.shape[1] / 2), y + i * size * 1.38)


def ask_block(c, y, ink=PLUM, center=False):
    """Ask line, gradient button, then logo (left) + phone (right)."""
    s = ts('Could your home keep them together?', N9, 40, ink)
    draw(c, s, (PW / 2 if center else 72 + s.shape[1] / 2), y)
    bw, bh = 520, 92
    bx = PW / 2 if center else 72 + bw / 2
    b = F.grad_spr(bw, bh, bh / 2)
    draw(c, blur_sprite(b, 16), bx, y + 98, opacity=0.4)
    draw(c, b, bx, y + 90)
    F.text_arrow(c, 'Start your enquiry', bx, y + 90, size=34)


def footer(c, y=1262, ink=PLUM, white_logo=False):
    lg = F.logo()
    if white_logo:
        a = lg[..., 3:4]
        lg = np.concatenate([np.ones_like(lg[..., :3]) * a, a], 2)
    draw(c, lg, 72 + 100, y, scale=200 / lg.shape[1])
    sp = ts('0161 241 1332', N9, 34, ink)
    draw(c, sp, PW - 72 - sp.shape[1] / 2, y - 14)
    sw = ts('organicfostering.co.uk', N7, 22, ink)
    draw(c, sw, PW - 72 - sw.shape[1] / 2, y + 22)


def soft_panel(c, y0, col=IVORY, amt=0.96, ramp=140):
    g = np.clip((YY - y0) / ramp, 0, 1)[..., None] ** 1.2
    c[:] = c * (1 - amt * g) + np.array(col, np.float32) * amt * g


# ------------------------------------------------------------------ A · The Shelf
def option_a():
    c = np.ones((PH, PW, 3), np.float32) * np.array(IVORY, np.float32)
    photo = render('shelf', PW, 756)
    photo = P.warm_grade(photo, 0.35)
    c[:756] = photo
    # gentle seam
    g = np.clip((YY - 740) / 22, 0, 1)[..., None] * (YY < 770)[..., None]
    c[:] = c * (1 - g * 0.0)
    eyebrow(c)
    headline(c, 72, 812, 84)
    subline(c, 72, 975, 29)
    ask_block(c, 1068)
    footer(c, 1286)
    return P.grain(c, 0.008)


# ------------------------------------------------------------------ B · Shadow House
def option_b():
    c = render('shadow')
    c = cv2.warpAffine(c, np.float32([[1, 0, 0], [0, 1, -60]]), (PW, PH), borderMode=cv2.BORDER_REPLICATE)
    c = P.warm_grade(c, 0.4)
    # soft top veil for the headline
    t = np.clip(1 - YY / 520, 0, 1)[..., None] ** 1.4
    c = c * (1 - 0.35 * t) + np.array(IVORY, np.float32) * 0.35 * t
    eyebrow(c, y=96)
    headline(c, 72, 196, 82)
    # a handwritten nudge towards the shadow
    m = solid(_wmask('look at the shadow', HAND, 46), PURPLE)
    draw(c, m, 805, 440, rot=-4)
    lay = np.zeros((PH, PW), np.uint8)
    pts = np.array([(825, 470), (805, 515), (775, 552)], np.float32)
    tt = np.linspace(0, 1, 30)
    cur = np.array([(1 - s) ** 2 * pts[0] + 2 * (1 - s) * s * pts[1] + s ** 2 * pts[2] for s in tt])
    cv2.polylines(lay, [(cur * 4).astype(np.int32)], False, 255, 4 * 4, cv2.LINE_AA, shift=2)
    for ang in (2.4, -2.4):
        dv = cur[-1] - cur[-5]; dv /= np.linalg.norm(dv)
        rm = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        e = cur[-1] + rm @ dv * 20
        cv2.line(lay, tuple((cur[-1] * 4).astype(int)), tuple((e * 4).astype(int)), 255, 4 * 4, cv2.LINE_AA, shift=2)
    mm = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - mm) + np.array(PURPLE[:3], np.float32) * mm
    soft_panel(c, 985, IVORY, 0.95, 110)
    subline(c, 72, 1004, 28)
    ask_block(c, 1098)
    footer(c, 1288)
    return P.grain(c, 0.008)


# ------------------------------------------------------------------ C · Clay Home
def option_c():
    c = render('clay')
    t = np.clip(1 - YY / 480, 0, 1)[..., None] ** 1.4
    c = c * (1 - 0.25 * t) + np.array(LAV, np.float32) * 0.25 * t
    eyebrow(c, fill=(1, 1, 1, 0.9))
    headline(c, 72, 230, 92, center=True)
    soft_panel(c, 950, (0.99, 0.97, 0.98), 0.94, 130)
    subline(c, 72, 990, 28, center=True)
    s = ts('Could your home keep them together?', N9, 40, PLUM)
    draw(c, s, PW / 2, 1080)
    bw, bh = 520, 92
    b = F.grad_spr(bw, bh, bh / 2)
    draw(c, blur_sprite(b, 16), PW / 2, 1178, opacity=0.4)
    draw(c, b, PW / 2, 1170)
    F.text_arrow(c, 'Start your enquiry', PW / 2, 1170, size=34)
    footer(c, 1288)
    return P.grain(c, 0.008)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:] or ['A', 'B', 'C']
    for k in want:
        im = {'A': option_a, 'B': option_b, 'C': option_c}[k]()
        cv2.imwrite(f'{OUT}/option_{k}.png', F.to_u8(im))
        print('option', k, flush=True)
    th = [cv2.resize(cv2.imread(f'{OUT}/option_{k}.png'), (540, 675)) for k in 'ABC' if os.path.exists(f'{OUT}/option_{k}.png')]
    if len(th) == 3:
        g = np.ones((675, 24, 3), np.uint8) * 245
        cv2.imwrite(f'{OUT}/overview.jpg', np.hstack([th[0], g, th[1], g, th[2]]), [cv2.IMWRITE_JPEG_QUALITY, 92])
