"""Organic Fostering "One Weekend at a Time" — respite fostering static post, 3 realistic options (1080x1350).

A · Pancakes Again   — a real 4K photo of a weekend pancake stack, a little paper flag: "Pancakes again!"
B · Two Saturdays    — two real photos as Polaroids on a sunlit peach wall, two weeks apart
C · The Calendar     — a photoreal 3D render of the family wall calendar (the PDF idea), two weekends circled

Usage: python3 posts_respite.py [A B C] -> workspace_respite/posts/option_X.png
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
from frames_cf import draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, PURPLE, ORANGE, PLUM, WHITE, N9, N8, N7

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_respite'))
OUT = f'{S}/posts'
PW, PH = 1080, 1350
HAND = 'Caveat-700'
CREAM = (1.0, 0.992, 0.984)
YY, XX = np.mgrid[0:PH, 0:PW].astype(np.float32)


def frame(cid, frac):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * frac))
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def crop(im, cx, cy, w, h, ow, oh):
    ih, iw = im.shape[:2]
    x0 = int(np.clip(cx * iw - w / 2, 0, iw - w)); y0 = int(np.clip(cy * ih - h / 2, 0, ih - h))
    out = cv2.resize(im[y0:y0 + int(h), x0:x0 + int(w)], (ow, oh), interpolation=cv2.INTER_AREA if w > ow else cv2.INTER_CUBIC)
    if w < ow:
        bl = cv2.GaussianBlur(out, (0, 0), 1.2)
        out = np.clip(out * 1.35 - bl * 0.35, 0, 1)
    return out


def warm_grade(im, amt=1.0):
    lum = im.mean(2, keepdims=True)
    im = np.clip((im - 0.5) * 1.04 + 0.5, 0, 1)
    return np.clip(im + np.array([0.035, 0.015, -0.02], np.float32) * amt * (0.3 + lum), 0, 1)


def blinds(c, amt=0.22, angle=-24, pitch=70, x0=PW * 0.95, y0=-50, reach=1300, soft=9):
    """Late-afternoon light through window blinds: warm diagonal light bars with soft shadows between."""
    a = math.radians(angle)
    u = (XX * math.sin(a) + YY * math.cos(a))
    bars = (0.5 + 0.5 * np.cos(u / pitch * 2 * math.pi))
    bars = cv2.GaussianBlur(np.clip((bars - 0.35) * 2.5, 0, 1), (0, 0), soft)
    fall = np.clip(1 - np.hypot(XX - x0, YY - y0) / reach, 0, 1) ** 1.3
    light = (bars * fall)[..., None]
    shade = ((1 - bars) * fall)[..., None]
    c[:] = np.clip(c * (1 - shade * amt * 0.6) + light * amt * np.array([1.0, 0.8, 0.55], np.float32) * 0.9, 0, 1)


def grain(c, amt=0.018, seed=2):
    rng = np.random.default_rng(seed)
    return np.clip(c + rng.normal(0, amt, (PH, PW, 1)).astype(np.float32), 0, 1)


def vignette(c, amt=0.18):
    d = np.hypot((XX - PW / 2) / (PW * 0.7), (YY - PH / 2) / (PH * 0.7))
    return c * (1 - amt * np.clip(d - 0.4, 0, 1)[..., None])


# ------------------------------------------------------------------ type kit
def text(c, s, x, y, font=N9, size=40, col=PLUM, shadow=0.0):
    sp = ts(s, font, size, col)
    if shadow:
        draw(c, blur_sprite(tint(sp, (0.25, 0.1, 0.05)), 10), x + sp.shape[1] / 2 + 2, y + 4, opacity=shadow)
    draw(c, sp, x + sp.shape[1] / 2, y)
    return sp.shape[1]


def headline(c, y=250, size=80, x=70, ink=PLUM, accent=ORANGE, shadow=0.0, l1='Some fostering happens', l2=(('one weekend', 1), ('at a time.', 0))):
    text(c, l1, x, y, N9, size, ink, shadow)
    xx = x
    for part, hi in l2:
        xx += text(c, part, xx, y + size * 1.1, N9, size, accent if hi else ink, shadow) + size * 0.24


def logo(c, x=70, y=100, w=230, white=False):
    lg = F.logo()
    if white:
        lg = tint(lg, (1, 1, 1))
    draw(c, lg, x + w / 2, y, scale=w / lg.shape[1])


def eyebrow(c, x=1010, y=100):
    sp = ts('RESPITE FOSTERING', 'Poppins-SemiBold', 25, PLUM, 0.06)
    w = sp.shape[1] + 46
    draw(c, blur_sprite(rrect(w, 56, 28, (0.3, 0.1, 0.05, 0.35)), 10), x - w / 2, y + 5)
    draw(c, rrect(w, 56, 28, (*CREAM, 1)), x - w / 2, y)
    draw(c, sp, x - w / 2, y)


def sign_off(c, y=1150, ink=PLUM, panel=True):
    if panel:
        g = np.clip((YY - (y - 170)) / 170, 0, 1)[..., None] ** 1.2
        c[:] = c * (1 - 0.94 * g) + np.array(CREAM, np.float32) * 0.94 * g
    text(c, 'Respite fostering gives a child planned short breaks:', 70, y, N8, 30, ink)
    text(c, 'one night, a weekend or part of a school holiday.', 70, y + 40, N8, 30, ink)
    bw, bh = 590, 86
    b = F.grad_spr(bw, bh, bh / 2)
    draw(c, blur_sprite(b, 16), 70 + bw / 2, y + 128, opacity=0.4)
    draw(c, b, 70 + bw / 2, y + 120)
    F.text_arrow(c, 'Talk to us about respite fostering', 70 + bw / 2, y + 120, size=30)
    text(c, '0161 241 1332 · organicfostering.co.uk', 70, y + 190, N7, 26, ink)
    sp = ts('Rated Good by Ofsted', N7, 25, ink)
    draw(c, F.star(ORANGE, 26), 1010 - sp.shape[1] - 26, y + 190)
    draw(c, sp, 1010 - sp.shape[1] / 2, y + 190)


def sign_off2(c, y=1150, ink=PLUM):
    """Cleaner sign-off: one-line subline, button, web address left and phone number right."""
    g = np.clip((YY - (y - 150)) / 150, 0, 1)[..., None] ** 1.2
    c[:] = c * (1 - 0.94 * g) + np.array(CREAM, np.float32) * 0.94 * g
    line = 'Planned short breaks: one night, a weekend or part of a school holiday.'
    size = 32
    while ts(line, N8, size, ink).shape[1] > PW - 140 and size > 22:
        size -= 1
    text(c, line, 70, y + 10, N8, size, ink)
    bw, bh = 590, 86
    b = F.grad_spr(bw, bh, bh / 2)
    draw(c, blur_sprite(b, 16), 70 + bw / 2, y + 98, opacity=0.4)
    draw(c, b, 70 + bw / 2, y + 90)
    F.text_arrow(c, 'Talk to us about respite fostering', 70 + bw / 2, y + 90, size=30)
    text(c, 'organicfostering.co.uk', 70, y + 165, N8, 28, ink)
    sp = ts('0161 241 1332', N9, 30, ink)
    draw(c, sp, 1010 - sp.shape[1] / 2, y + 165)


def hand(c, s, x, y, size, col, rot=0):
    sp = solid(_wmask(s, HAND, size), col)
    draw(c, sp, x, y, rot=rot)


def paper_flag(c, x, y, label, rot=-6):
    """A little cream paper flag on a wooden toothpick, stuck in the stack (x, y = where the stick enters)."""
    stick_h = 300
    st = np.zeros((stick_h, 14, 4), np.float32)
    st[:, 3:11] = (0.80, 0.64, 0.42, 1)
    st[:, 3:5, :3] *= 0.85
    for k in range(stick_h):
        st[k, :, :3] *= 0.92 + 0.08 * math.sin(k * 0.3)
    st[..., :3] *= st[..., 3:4]
    fw, fh = 330, 116
    flag = np.zeros((fh, fw, 4), np.float32)
    pts = np.array([[0, 0], [fw, 0], [fw - 30, fh / 2], [fw, fh], [0, fh]], np.int32)
    m = np.zeros((fh, fw), np.uint8)
    cv2.fillPoly(m, [pts], 255, cv2.LINE_AA)
    mf = m.astype(np.float32) / 255
    paper = np.ones((fh, fw, 3), np.float32) * np.array([0.99, 0.97, 0.92], np.float32)
    paper *= (0.97 + 0.03 * np.random.default_rng(1).random((fh, fw, 1))).astype(np.float32)
    paper *= (1 - 0.06 * np.linspace(0, 1, fw)[None, :, None])
    flag[..., :3] = paper * mf[..., None]
    flag[..., 3] = mf
    sp_t = solid(_wmask(label, HAND, 58), (0.91, 0.32, 0.04, 1))
    paste_spr(flag, sp_t, fw / 2 - 14, fh / 2 + 2)
    whole = np.zeros((stick_h + 20, fw + 20, 4), np.float32)
    paste_spr(whole, st, 12, (stick_h + 20) / 2)
    paste_spr(whole, flag, 12 + fw / 2, fh / 2 + 14)
    cx, cy = x + (whole.shape[1] / 2 - 12) * math.cos(math.radians(rot)), y - whole.shape[0] / 2
    draw(c, blur_sprite(tint(whole, (0.25, 0.1, 0.03)), 12), cx + 26, cy + 34, rot=rot, opacity=0.45)
    draw(c, whole, cx, cy, rot=rot)


# ------------------------------------------------------------------ A: Pancakes Again
def option_a():
    im = frame(4860, 0.95)
    hh = 860
    sc = hh / im.shape[0]
    big = cv2.resize(im, (int(im.shape[1] * sc), hh), interpolation=cv2.INTER_AREA)
    cx = int(0.37 * big.shape[1])
    x0 = int(np.clip(cx - PW / 2, 0, big.shape[1] - PW))
    photo = big[:, x0:x0 + PW]
    yo = PH - hh - 60
    ext = cv2.GaussianBlur(cv2.resize(photo[:140], (PW, PH), interpolation=cv2.INTER_LINEAR), (0, 0), 10)
    c = ext.copy()
    c[PH - 60:] = cv2.resize(photo[-60:], (PW, 60))
    alpha = np.zeros((PH, PW, 1), np.float32)
    alpha[yo:yo + hh] = 1
    feather = np.clip((YY - yo) / 140, 0, 1)[..., None]
    alpha = alpha * feather
    layer = np.zeros_like(c); layer[yo:yo + hh] = photo
    c = c * (1 - alpha) + layer * alpha
    c[yo + hh:] = cv2.resize(photo[-20:], (PW, PH - yo - hh)) if PH - yo - hh > 0 else c[yo + hh:]
    c = warm_grade(c)
    top = np.clip(1 - YY / 560, 0, 1)[..., None] ** 1.3
    c = c * (1 - 0.86 * top) + np.array(CREAM, np.float32) * 0.86 * top
    blinds(c, 0.1, pitch=60, x0=PW, y0=260, reach=900)
    sx = int(0.39 * big.shape[1]) - x0
    paper_flag(c, sx, yo + int(0.355 * hh), 'Pancakes again!', rot=-4)
    logo(c)
    eyebrow(c)
    headline(c, y=245)
    hand(c, 'same child,', 870, 640, 44, PLUM, rot=-4)
    hand(c, 'two weeks later', 870, 690, 44, PLUM, rot=-4)
    sign_off(c, 1110)
    return vignette(grain(c, 0.012), 0.1)


# ------------------------------------------------------------------ B: Two Saturdays
def wall_peach(seed=3):
    rng = np.random.default_rng(seed)
    base = np.ones((PH, PW, 3), np.float32) * np.array([0.97, 0.80, 0.69], np.float32)
    n = cv2.GaussianBlur(rng.normal(0, 1, (PH, PW)).astype(np.float32), (0, 0), 1.0) * 0.012
    n2 = cv2.resize(cv2.GaussianBlur(rng.normal(0, 1, (PH // 8, PW // 8)).astype(np.float32), (0, 0), 3), (PW, PH)) * 0.02
    base = base + (n + n2)[..., None]
    grad = (0.9 + 0.12 * (XX / PW) + 0.04 * (1 - YY / PH))[..., None]
    return np.clip(base * grad, 0, 1)


def polaroid(img, caption1, caption2, w=430):
    ph = w - 40
    pic = cv2.resize(img, (ph, ph), interpolation=cv2.INTER_AREA)
    H_ = ph + 150
    card = np.ones((H_, w, 4), np.float32)
    card[..., :3] = np.array([0.99, 0.985, 0.97], np.float32) * (0.97 + 0.03 * np.random.default_rng(5).random((H_, w, 1)))
    card[20:20 + ph, 20:20 + ph, :3] = pic
    sp1 = solid(_wmask(caption1, HAND, 46), (0.25, 0.22, 0.42, 1))
    sp2 = solid(_wmask(caption2, HAND, 52), (0.91, 0.32, 0.04, 1))
    paste_spr(card, sp1, w / 2, ph + 58)
    paste_spr(card, sp2, w / 2, ph + 110)
    return card


def magnet(c, x, y, r=34):
    draw(c, blur_sprite(rrect(r * 2, r * 2, r, (0.3, 0.1, 0.03, 0.6)), 8), x + 6, y + 10)
    m = np.zeros((r * 2, r * 2, 4), np.float32)
    yy, xx = np.mgrid[0:r * 2, 0:r * 2].astype(np.float32)
    d = np.hypot(xx - r, yy - r) / r
    inside = np.clip((1 - d) * r, 0, 1)
    shade = np.clip(1.15 - np.hypot(xx - r * 0.7, yy - r * 0.6) / (r * 1.4), 0.55, 1.2)
    col = np.array(ORANGE[:3], np.float32) * shade[..., None]
    spec = np.exp(-(((xx - r * 0.65) / (r * 0.25)) ** 2 + ((yy - r * 0.55) / (r * 0.18)) ** 2))[..., None] * 0.6
    m[..., :3] = np.clip(col + spec, 0, 1) * inside[..., None]
    m[..., 3] = inside
    draw(c, m, x, y)


def option_b():
    c = wall_peach()
    blinds(c, 0.26, angle=-22, pitch=64, x0=PW * 1.05, y0=-80, reach=1500, soft=10)
    p1 = polaroid(crop(frame(11705, 0.9), 0.62, 0.62, 720, 720, 390, 390), 'Sat 7 Nov', 'Pancakes + park')
    p2 = polaroid(crop(frame(4860, 0.95), 0.2, 0.62, 1500, 1500, 390, 390), 'Sat 21 Nov', 'Pancakes again!')
    for p, x, y, rot in ((p1, 330, 760, -6), (p2, 740, 800, 5)):
        draw(c, blur_sprite(tint(p, (0.3, 0.12, 0.05)), 22), x + 22, y + 34, rot=rot, opacity=0.5)
        draw(c, blur_sprite(tint(p, (0.3, 0.12, 0.05)), 6), x + 6, y + 9, rot=rot, opacity=0.35)
        draw(c, p, x, y, rot=rot)
        magnet(c, int(x + math.sin(math.radians(rot)) * 290), int(y - 285))
    lay = np.zeros((PH, PW), np.uint8)
    pts = np.array([[470, 520], [540, 470], [620, 500]], np.float32)
    t = np.linspace(0, 1, 40)
    curve = np.array([(1 - u) ** 2 * pts[0] + 2 * (1 - u) * u * pts[1] + u ** 2 * pts[2] for u in t])
    cv2.polylines(lay, [(curve * 4).astype(np.int32)], False, 255, 5 * 4, cv2.LINE_AA, shift=2)
    for ang in (2.4, -2.4):
        dv = curve[-1] - curve[-6]; dv /= np.linalg.norm(dv)
        rot_m = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        e = curve[-1] + rot_m @ dv * 22
        cv2.line(lay, tuple((curve[-1] * 4).astype(int)), tuple((e * 4).astype(int)), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(PLUM[:3], np.float32) * m
    hand(c, 'two weeks later', 545, 430, 46, PLUM, rot=-3)
    logo(c)
    eyebrow(c)
    headline(c, y=230)
    sign_off(c, 1110)
    return vignette(grain(c, 0.014), 0.14)


# ------------------------------------------------------------------ C: The Calendar (photoreal render)
def option_c():
    im = cv2.imread(f'{S}/tex/cal_render.png')[..., ::-1].astype(np.float32) / 255
    c = cv2.resize(im, (PW, PH), interpolation=cv2.INTER_AREA)
    blinds(c, 0.2, angle=-26, pitch=58, x0=PW * 1.1, y0=-120, reach=1350, soft=8)
    top = np.clip(1 - YY / 420, 0, 1)[..., None] ** 1.6
    c = c * (1 - 0.35 * top) + np.array(CREAM, np.float32) * 0.35 * top
    logo(c)
    eyebrow(c)
    headline(c, y=230)
    hand(c, 'same child,', 935, 560, 42, PLUM, rot=-4)
    hand(c, 'two weeks later', 935, 606, 42, PLUM, rot=-4)
    sign_off(c, 1110)
    return vignette(grain(c, 0.01), 0.1)


# ------------------------------------------------------------------ D: The Calendar + a string of family photos
WEB = '/home/user/100/workspace_lo2/web/img'
STRING_PHOTOS = [('06-respite-outdoor-play.webp', 'Park!', 0.5, 0.45), ('balanced-home-baking-2026-09-23.webp', 'Baking', 0.42, 0.5),
                 ('balanced-home-reading-2026-09-23.webp', 'Story time', 0.5, 0.5), ('balanced-home-outdoors-2026-09-23.webp', 'Walkies', 0.45, 0.5)]


def web_photo(name, w, h, fx=0.5, fy=0.5):
    im = cv2.imread(f'{WEB}/{name}', cv2.IMREAD_COLOR)[..., ::-1].astype(np.float32) / 255
    ih, iw = im.shape[:2]
    s = max(w / iw, h / ih)
    cw, ch = w / s, h / s
    x0 = int(np.clip(fx * iw - cw / 2, 0, iw - cw)); y0 = int(np.clip(fy * ih - ch / 2, 0, ih - ch))
    return warm_grade(cv2.resize(im[y0:y0 + int(ch), x0:x0 + int(cw)], (w, h), interpolation=cv2.INTER_AREA), 0.6)


def print_card(img, caption, w=196):
    ph_w, ph_h = img.shape[1], img.shape[0]
    H_ = ph_h + 62
    card = np.ones((H_, w, 4), np.float32)
    card[..., :3] = np.array([0.99, 0.985, 0.975], np.float32) * (0.97 + 0.03 * np.random.default_rng(7).random((H_, w, 1)))
    card[10:10 + ph_h, 10:10 + ph_w, :3] = img
    sp = solid(_wmask(caption, HAND, 36), (0.25, 0.22, 0.42, 1))
    paste_spr(card, sp, w / 2, ph_h + 38)
    return card


def peg():
    p = np.zeros((70, 26, 4), np.float32)
    p[2:68, 3:23] = (0.84, 0.68, 0.48, 1)
    p[2:68, 12:14, :3] *= 0.7
    p[30:38, 3:23, :3] *= 0.8
    yy = np.arange(70)[:, None]
    p[..., :3] *= (0.92 + 0.08 * np.sin(yy * 0.9))[..., None] if False else 1
    p[..., :3] *= p[..., 3:4]
    return p


def photo_string(c, y_left=440, y_right=430, sag=70, n_bulbs=11):
    xs = np.linspace(-20, PW + 20, 200)
    u = (xs - xs[0]) / (xs[-1] - xs[0])
    ys = y_left + (y_right - y_left) * u + sag * 4 * u * (1 - u)
    lay = np.zeros((PH, PW), np.uint8)
    cv2.polylines(lay, [(np.stack([xs, ys], 1) * 4).astype(np.int32)], False, 255, 3 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    sh = cv2.GaussianBlur(np.roll(np.roll(m[..., 0], 14, 0), -10, 1), (0, 0), 4)[..., None] * 0.35
    c[:] = c * (1 - sh)
    c[:] = c * (1 - m) + np.array([0.72, 0.6, 0.47], np.float32) * m
    yat = lambda x: y_left + (y_right - y_left) * ((x + 20) / (PW + 40)) + sag * 4 * ((x + 20) / (PW + 40)) * (1 - (x + 20) / (PW + 40))
    for k in range(n_bulbs):
        x = 40 + k * (PW - 80) / (n_bulbs - 1)
        y = yat(x) + 10
        g = np.exp(-((XX - x) ** 2 + (YY - y) ** 2) / (2 * 26 ** 2))[..., None] * 0.55
        c[:] = np.clip(c + g * np.array([1.0, 0.72, 0.35], np.float32), 0, 1)
        draw(c, rrect(16, 22, 8, (1.0, 0.93, 0.7, 1)), x, y)
    for (name, cap, fx, fy), x, rot in zip(STRING_PHOTOS, (120, 318, 762, 960), (-7, 4, -4, 6)):
        card = print_card(web_photo(name, 176, 185, fx, fy), cap)
        top = yat(x)
        cy = top + card.shape[0] / 2 - 8
        draw(c, blur_sprite(tint(card, (0.3, 0.12, 0.05)), 14), x - 14, cy + 22, rot=rot, opacity=0.5)
        draw(c, card, x, cy, rot=rot)
        pg = peg()
        draw(c, blur_sprite(tint(pg, (0.2, 0.1, 0.05)), 4), x - 4, top + 12, opacity=0.4)
        draw(c, pg, x, top + 6)


def option_d():
    im = cv2.imread(f'{S}/tex/cal_render.png')[..., ::-1].astype(np.float32) / 255
    c = cv2.resize(im, (PW, PH), interpolation=cv2.INTER_AREA)
    blinds(c, 0.2, angle=-26, pitch=58, x0=PW * 1.1, y0=-120, reach=1350, soft=8)
    top = np.clip(1 - YY / 420, 0, 1)[..., None] ** 1.6
    c = c * (1 - 0.35 * top) + np.array(CREAM, np.float32) * 0.35 * top
    photo_string(c)
    logo(c)
    eyebrow(c)
    headline(c, y=230)
    hand(c, 'same child,', 960, 880, 40, PLUM, rot=-4)
    hand(c, '2 weeks later', 960, 924, 40, PLUM, rot=-4)
    sign_off2(c, 1130)
    return vignette(grain(c, 0.01), 0.1)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:] or ['A', 'B', 'C']
    for k in want:
        im = {'A': option_a, 'B': option_b, 'C': option_c, 'D': option_d}[k]()
        cv2.imwrite(f'{OUT}/option_{k}.png', F.to_u8(im))
        print('option', k, flush=True)


