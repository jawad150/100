"""Organic Fostering "Two Toothbrushes" — FINAL, Option B premium: "Shadow House" (1080x1350).

Full-bleed 3D render (blender_tb2.py): morning sun through a window lays a bright patch on subway tiles; the two leaning
brushes and their cup cast a little house, its four-pane window glowing through a cut in the cup. Warm light rays and
dust in the beam, a hand-drawn "see it?" pointing at the shadow house, and a frosted-glass card holding the copy.

Usage: python3 posts_tb2.py -> workspace_tb/posts/final_B.png (+ story 1080x1920)
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import posts_tb as T
from posts_tb import F, P, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, N9, N8, N7, PW, PH, YY, XX, \
    HAND, RED, IVORY, SUB

S = T.S
OUT = T.OUT
GOLD = (1.0, 0.84, 0.55)


def load_render(w=PW, h=PH, dy=0):
    im = cv2.imread(f'{S}/renders/shadow2.png')[..., ::-1].astype(np.float32) / 255
    im = cv2.resize(im, (w, int(round(im.shape[0] * w / im.shape[1]))), interpolation=cv2.INTER_AREA)
    if im.shape[0] != h or dy:
        M = np.float32([[1, 0, 0], [0, 1, dy + (h - im.shape[0]) / 2]])
        im = cv2.warpAffine(im, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return im


def rays(c, origin=(-260, -220), ang0=0.62, spread=0.34, n=7, amt=0.12, yy=None, xx=None):
    """Soft warm light shafts from the window (top left), following the sun direction."""
    yy = YY if yy is None else yy
    xx = XX if xx is None else xx
    h, w = c.shape[:2]
    lay = np.zeros((h, w), np.uint8)
    rng = np.random.default_rng(5)
    for j in range(n):
        a = ang0 + (j / (n - 1) - 0.5) * spread
        wd = rng.uniform(0.012, 0.03)
        L = 2600
        p0 = origin
        p1 = (origin[0] + math.cos(a - wd) * L, origin[1] + math.sin(a - wd) * L)
        p2 = (origin[0] + math.cos(a + wd) * L, origin[1] + math.sin(a + wd) * L)
        cv2.fillPoly(lay, [np.array([p0, p1, p2], np.int32)], int(rng.uniform(120, 255)), cv2.LINE_AA)
    m = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 26)
    fall = np.clip(1 - np.hypot(xx - origin[0], yy - origin[1]) / 2000, 0, 1) ** 1.2
    c[:] = np.clip(c + (m * fall)[..., None] * amt * np.array(GOLD, np.float32), 0, 1)


def motes(c, region, n=70, seed=4, amt=0.9):
    x0, y0, x1, y1 = region
    h, w = c.shape[:2]
    lay = np.zeros((h, w), np.float32)
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(0.8, 2.6)
        cv2.circle(lay, (int(x), int(y)), int(max(1, r)), rng.uniform(0.25, 1.0), -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.3)[..., None]
    c[:] = np.clip(c + lay * amt * np.array(GOLD, np.float32) * 0.5, 0, 1)


def sparkle(c, x, y, s=22, col=(1, 0.95, 0.8, 1)):
    m = np.zeros((int(s * 8), int(s * 8)), np.uint8)
    cc = s * 4
    pts = [(cc + math.cos(i * math.pi / 4) * cc * (1 if i % 2 == 0 else 0.2), cc + math.sin(i * math.pi / 4) * cc * (1 if i % 2 == 0 else 0.2)) for i in range(8)]
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    sp = solid(cv2.resize(m, (int(s * 2), int(s * 2)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, col)
    draw(c, blur_sprite(sp, 6), x, y, opacity=0.9)
    draw(c, sp, x, y)


def hand_arrow(c, pts, col=PURPLE, th=4):
    h, w = c.shape[:2]
    lay = np.zeros((h, w), np.uint8)
    p = np.array(pts, np.float32)
    t = np.linspace(0, 1, 40)
    cur = np.array([(1 - s) ** 2 * p[0] + 2 * (1 - s) * s * p[1] + s ** 2 * p[2] for s in t])
    cv2.polylines(lay, [(cur * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    for ang in (2.45, -2.45):
        dv = cur[-1] - cur[-5]; dv /= np.linalg.norm(dv)
        rm = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        e = cur[-1] + rm @ dv * 22
        cv2.line(lay, tuple((cur[-1] * 4).astype(int)), tuple((e * 4).astype(int)), 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def frosted_card(c, x0, y0, x1, y1, r=38, tint_col=(1.0, 0.985, 0.975), amt=0.72):
    """Glass card: blurred background + milky tint + hairline border + soft drop shadow."""
    w, h = int(x1 - x0), int(y1 - y0)
    m = cv2.resize(F.R.sdf_fill(F.R.rrect_alpha(w, h, r, 2)), (w, h))[..., None]
    sh = np.zeros(c.shape[:2], np.float32)
    sh[y0 + 18:y1 + 18, x0 + 6:x1 + 6] = m[..., 0]
    sh = cv2.GaussianBlur(sh, (0, 0), 26)[..., None] * 0.28
    c[:] = c * (1 - sh) + np.array([0.25, 0.1, 0.12], np.float32) * sh
    region = c[y0:y1, x0:x1]
    bl = cv2.GaussianBlur(region, (0, 0), 22)
    glass = bl * (1 - amt) + np.array(tint_col, np.float32) * amt
    region[:] = region * (1 - m) + glass * m
    edge = (m[..., 0] - cv2.erode(m[..., 0], np.ones((5, 5), np.uint8)))[..., None]
    region[:] = np.clip(region + edge * 0.5, 0, 1)


def logo_at(c, x, y, w=190):
    lg = F.logo()
    draw(c, lg, x + w / 2, y, scale=w / lg.shape[1])


def build_feed():
    c = load_render(dy=0)
    c = P.warm_grade(c, 0.35)
    rays(c)
    motes(c, (60, 120, 900, 760))
    # top veil for the headline
    t = np.clip(1 - YY / 520, 0, 1)[..., None] ** 1.5
    c = c * (1 - 0.22 * t) + np.array(IVORY, np.float32) * 0.22 * t
    # eyebrow (glass pill)
    s = ts('FOSTERING SIBLINGS', 'Poppins-SemiBold', 24, PLUM, 0.1)
    w = s.shape[1] + 48
    draw(c, rrect(w, 56, 28, (1, 1, 1, 0.82)), 72 + w / 2, 104)
    draw(c, s, 72 + w / 2, 104)
    # headline
    for i, (txt, col) in enumerate((('Two toothbrushes.', PLUM), ('One home.', RED))):
        m = _wmask(txt, N9, 100)
        draw(c, blur_sprite(solid(m, (1, 1, 1, 1)), 14), 72 + m.shape[1] / 2, 215 + i * 106, opacity=0.45)
        draw(c, solid(m, col), 72 + m.shape[1] / 2, 210 + i * 106)
    # "see it?" pointing at the shadow house; a sparkle on its glowing window
    hm = solid(_wmask('see it?', HAND, 66), PURPLE)
    draw(c, hm, 860, 455, rot=-6)
    hand_arrow(c, [(840, 492), (815, 545), (745, 585)])
    # the glowing window in the shadow house: a soft bloom and a sparkle
    reg = c[760:925, 520:820].mean(2)
    yy_, xx_ = np.unravel_index(np.argmax(cv2.GaussianBlur(reg, (0, 0), 8)), reg.shape)
    wx, wy = 520 + xx_, 760 + yy_
    g = np.exp(-((XX - wx) ** 2 + (YY - wy) ** 2) / (2 * 38 ** 2))[..., None] * 0.22
    c = np.clip(c + g * np.array(GOLD, np.float32), 0, 1)
    sparkle(c, wx + 40, wy - 38, 16)
    sparkle(c, wx - 34, wy - 54, 9)
    return c


def finish_feed(c):
    # frosted card with the copy
    x0, y0, x1, y1 = 44, 942, PW - 44, 1306
    frosted_card(c, x0, y0, x1, y1)
    for i, ln in enumerate(SUB):
        s = ts(ln, N7, 28, PLUM)
        draw(c, s, 84 + s.shape[1] / 2, 988 + i * 38)
    s = ts('Could your home keep them together?', N9, 40, PLUM)
    draw(c, s, 84 + s.shape[1] / 2, 1076)
    bw, bh = 480, 86
    b = F.grad_spr(bw, bh, bh / 2)
    draw(c, blur_sprite(b, 16), 84 + bw / 2, 1164, opacity=0.4)
    draw(c, b, 84 + bw / 2, 1156)
    F.text_arrow(c, 'Start your enquiry', 84 + bw / 2, 1156, size=32)
    ph = ts('0161 241 1332', N9, 36, PLUM)
    draw(c, ph, x1 - 40 - ph.shape[1] / 2, 1146)
    wb = ts('organicfostering.co.uk', N7, 22, PLUM)
    draw(c, wb, x1 - 40 - wb.shape[1] / 2, 1182)
    draw(c, rrect(x1 - x0 - 80, 2, 1, (0.36, 0.09, 0.31, 0.15)), (x0 + x1) / 2, 1220)
    logo_at(c, 84, 1262, 180)
    s2 = ts('An initial conversation doesn’t commit you to applying.', N7, 20, (0.36, 0.09, 0.31, 0.75))
    draw(c, s2, x1 - 40 - s2.shape[1] / 2, 1262)
    return P.grain(c, 0.007)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    c = build_feed()
    # locate the glowing window: brightest small blob right of the cup in the lower patch
    c = finish_feed(c)
    cv2.imwrite(f'{OUT}/final_B.png', F.to_u8(c))
    print('final_B')
