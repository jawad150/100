"""Scene images for Organic Fostering "Can I Foster If…?" — v2, phone-UI story style (after the client's reference reel).

Language borrowed from the reference: a real post seen up close with hand-drawn scribbles, kinetic sentences on a
dark plum gradient with little photos inline, giant gradient type, a whip-blurred wall of posts, "But, what if…" on a
glowing dot-matrix, a light UI where an icon opens into a popover, "And done..!", stacked notification banners, a
warm film-grain photo with a handwritten note, and a black "made with care" end card.

Content stays honest: every answer is quoted from organicfostering.co.uk/faqs. Never red, never a cross.

Usage: python3 frames_cf2.py -> workspace_cf/frames2/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_cf as F
from frames_cf import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask,
                       PURPLE, ORANGE, PLUM, IVORY, LAV, PEACH, LEAF, LAV_D, WHITE, N9, N8, N7, ANS)

S = F.S
OUT = f'{S}/frames2'
WEB = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo2', 'web', 'img'))
I4, I6, I8, I9 = 'Inter-400', 'Inter-600', 'Inter-800', 'Inter-900'
HAND = 'Caveat-700'
INK = (0.08, 0.06, 0.08, 1.0)
GREY_BG = (0.93, 0.93, 0.94)


# ------------------------------------------------------------------ sources
def web(name, w, h, fx=0.5, fy=0.5, grade=False):
    im = cv2.imread(f'{WEB}/{name}', cv2.IMREAD_COLOR)[..., ::-1].astype(np.float32) / 255
    im = F.cover(im, fx, fy, 1.0, w, h)
    return F.grade(im) if grade else im


def emblem(size=80):
    lg = load_png_sprite(f'{F.OF}/src/emblem.png')
    sc = size / max(lg.shape[:2])
    return cv2.resize(lg, (int(lg.shape[1] * sc), int(lg.shape[0] * sc)), interpolation=cv2.INTER_AREA)


def avatar(size=72):
    sp = rrect(size, size, size / 2, WHITE).copy()
    e = emblem(int(size * 0.72))
    paste_spr(sp, e, size / 2, size / 2)
    return sp


# ------------------------------------------------------------------ backgrounds
def grey_bg():
    return np.ones((H, W, 3), np.float32) * np.array(GREY_BG, np.float32)


def dark_grad(glow=1.0):
    """Black top -> plum -> a magenta/orange glow rising from the bottom (the reference's dusk gradient, in brand)."""
    y = (R._Y / H)[..., None]
    c = np.array([0.03, 0.02, 0.03], np.float32) * (1 - y) + np.array(PLUM[:3], np.float32) * 0.55 * y
    for x, yy, r, col, a in ((300, H + 120, 760, PURPLE, 0.75), (820, H + 60, 620, ORANGE, 0.6)):
        g = np.exp(-((R._X - x) ** 2 + (R._Y - yy) ** 2) / (2 * r * r))[..., None] * a * glow
        c = c * (1 - g) + np.array(col[:3], np.float32) * g
    return c.astype(np.float32)


def dot_matrix(seed=3):
    """Glowing LED dot-matrix with soft magenta/orange bokeh."""
    rng = np.random.default_rng(seed)
    c = np.zeros((H, W, 3), np.float32) + 0.02
    lay = np.zeros((H, W), np.float32)
    noise = cv2.GaussianBlur(rng.random((H // 30 + 2, W // 30 + 2)).astype(np.float32), (0, 0), 1.2)
    for gy in range(H // 30 + 1):
        for gx in range(W // 30 + 1):
            v = noise[gy, gx] ** 2.5 * 1.6
            cv2.circle(lay, (gx * 30 + 15, gy * 30 + 15), 5, float(min(1, v)), -1, cv2.LINE_AA)
    col = np.array(PURPLE[:3], np.float32) * (1 - (R._X / W)[..., None]) + np.array(ORANGE[:3], np.float32) * (R._X / W)[..., None]
    c = c + lay[..., None] * (0.35 + 0.65 * col)
    bok = np.zeros((H, W), np.float32)
    for _ in range(14):
        cv2.circle(bok, (int(rng.uniform(0, W)), int(rng.uniform(0, H))), int(rng.uniform(40, 120)), float(rng.uniform(0.2, 0.6)), -1)
    bok = cv2.GaussianBlur(bok, (0, 0), 24)
    c = c + bok[..., None] * col * 0.6
    return np.clip(c, 0, 1)


# ------------------------------------------------------------------ UI pieces
def icon(kind, size=44, col=INK):
    m = np.zeros((size * 4, size * 4), np.uint8)
    s4 = size * 4
    th = max(4, int(size * 0.09)) * 4
    if kind == 'heart':
        pts = []
        for t in np.linspace(0, 2 * math.pi, 80):
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((s4 / 2 + x * s4 / 40, s4 / 2 - y * s4 / 40))
        cv2.polylines(m, [np.array(pts, np.int32)], True, 255, th, cv2.LINE_AA)
    elif kind == 'comment':
        cv2.circle(m, (s4 // 2, s4 // 2), int(s4 * 0.38), 255, th, cv2.LINE_AA)
        cv2.line(m, (int(s4 * 0.2), int(s4 * 0.82)), (int(s4 * 0.3), int(s4 * 0.68)), 255, th, cv2.LINE_AA)
    elif kind == 'send':
        pts = np.array([[0.12, 0.2], [0.88, 0.2], [0.45, 0.88], [0.4, 0.48], [0.12, 0.2]]) * s4
        cv2.polylines(m, [pts.astype(np.int32)], False, 255, th, cv2.LINE_AA)
        cv2.line(m, (int(0.4 * s4), int(0.48 * s4)), (int(0.88 * s4), int(0.2 * s4)), 255, th, cv2.LINE_AA)
    elif kind in ('bookmark', 'bookmark_fill'):
        pts = np.array([[0.22, 0.1], [0.78, 0.1], [0.78, 0.9], [0.5, 0.66], [0.22, 0.9]]) * s4
        if kind == 'bookmark_fill':
            cv2.fillPoly(m, [pts.astype(np.int32)], 255, cv2.LINE_AA)
        else:
            cv2.polylines(m, [pts.astype(np.int32)], True, 255, th, cv2.LINE_AA)
    m = cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return solid(m, col)


def post_card(img, caption, w=900, saved=False, user='organicfostering', sub='Manchester · Fostering', likes='1,204', cap_size=28):
    """A social post (generic, no platform branding): header, photo, action row, caption."""
    ih = img.shape[0]
    lh = int(cap_size * 1.6)
    hgt = 130 + ih + 110 + lh * len(caption) + 30
    card = rrect(w, hgt, 28, WHITE).copy()
    paste_spr(card, avatar(72), 70, 66)
    s = ts(user, I8, 30, INK)
    paste_spr(card, s, 124 + s.shape[1] / 2, 50)
    s2 = ts(sub, I4, 24, (0.45, 0.45, 0.5, 1))
    paste_spr(card, s2, 124 + s2.shape[1] / 2, 86)
    fb = rrect(130, 52, 14, (0.94, 0.94, 0.95, 1)).copy()
    paste_spr(fb, ts('Follow', I8, 24, INK), 65, 26)
    paste_spr(card, fb, w - 140, 66)
    ph = F.sprite_of(img, 20) if hasattr(F, 'sprite_of') else None
    m = R.sdf_fill(R.rrect_alpha(w - 40, ih, 20, 2))
    m = cv2.resize(m, (w - 40, ih))
    ph = np.concatenate([img * m[..., None], m[..., None]], 2).astype(np.float32)
    paste_spr(card, ph, w / 2, 130 + ih / 2)
    yy = 130 + ih + 55
    for j, k in enumerate(('heart', 'comment', 'send')):
        paste_spr(card, icon(k, 46), 60 + j * 80, yy)
    paste_spr(card, icon('bookmark_fill' if saved else 'bookmark', 46), w - 60, yy)
    s = ts(likes + ' likes', I8, 26, INK)
    paste_spr(card, s, 38 + s.shape[1] / 2, yy + 58)
    for j, ln in enumerate(caption):
        s = ts(ln, I6 if cap_size > 28 else I4, cap_size, INK)
        paste_spr(card, s, 38 + s.shape[1] / 2, yy + 104 + j * lh)
    return card


def scribble_text(c, text, x, y, size=84, col=PURPLE, rot=-6):
    s = solid(_wmask(text, HAND, size), col)
    draw(c, s, x, y, rot=rot)
    return s.shape[1]


def scribble_line(c, pts, col=PURPLE, w=6, head=True, wobble=4, seed=1):
    rng = np.random.default_rng(seed)
    p = np.array(pts, np.float32)
    t = np.linspace(0, 1, 60)
    curve = []
    for i in range(len(p) - 1):
        for u in t:
            q = p[i] * (1 - u) + p[i + 1] * u
            curve.append(q + rng.normal(0, wobble * 0.25, 2))
    curve = np.array(curve)
    curve = cv2.GaussianBlur(curve.reshape(-1, 1, 2), (1, 9), 3).reshape(-1, 2)
    lay = np.zeros((H, W), np.uint8)
    cv2.polylines(lay, [(curve * 4).astype(np.int32)], False, 255, w * 4, cv2.LINE_AA, shift=2)
    if head:
        d = curve[-1] - curve[-8]
        d /= np.linalg.norm(d) + 1e-6
        for ang in (2.5, -2.5):
            rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
            e = curve[-1] + rot @ d * 34
            cv2.line(lay, tuple((curve[-1] * 4).astype(int)), tuple((e * 4).astype(int)), 255, w * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def scribble_circle(c, x, y, rx, ry, col=PURPLE, w=6, turns=1.15, seed=2):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * math.pi * turns, 140)
    pts = np.stack([x + rx * np.cos(t) * (1 + 0.05 * np.sin(3 * t)) + rng.normal(0, 1.2, len(t)),
                    y + ry * np.sin(t) * (1 + 0.06 * np.cos(2 * t)) + rng.normal(0, 1.2, len(t))], 1)
    lay = np.zeros((H, W), np.uint8)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, w * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def kinetic(c, words, y, size=64, font=I6, col=WHITE, gap=None):
    """Centered sentence; a word may be a ('IMG', sprite) inline photo chip."""
    gap = gap or size * 0.32
    sprs = []
    for w in words:
        if isinstance(w, tuple):
            sprs.append(w[1])
        else:
            sprs.append(ts(w, font, size, col))
    total = sum(s.shape[1] for s in sprs) + gap * (len(sprs) - 1)
    x = W / 2 - total / 2
    for s in sprs:
        draw(c, s, x + s.shape[1] / 2, y)
        x += s.shape[1] + gap


def thumb(img, w=None, h=None, r=14, border=WHITE):
    h, w = img.shape[:2]
    m = R.sdf_fill(R.rrect_alpha(w, h, r, 2))
    m = cv2.resize(m, (w, h))
    t = np.concatenate([img * m[..., None], m[..., None]], 2).astype(np.float32)
    b = rrect(w + 8, h + 8, r + 4, border).copy()
    paste_spr(b, t, (w + 8) / 2, (h + 8) / 2)
    return b


def grad_text(text, font, size, phase=0.0):
    m = _wmask(text, font, size)
    hh, ww = m.shape
    u = np.linspace(0, 1, ww, dtype=np.float32)[None, :] + phase
    u = np.clip(u, 0, 1)
    col = np.array(PURPLE[:3], np.float32) * (1 - u[..., None]) + np.array(ORANGE[:3], np.float32) * u[..., None]
    col = np.broadcast_to(col, (hh, ww, 3))
    return np.concatenate([col * m[..., None], m[..., None]], 2).astype(np.float32)


def motion_blur(c, k=61, axis=1):
    ker = np.zeros((k, k), np.float32)
    if axis == 1:
        ker[k // 2, :] = 1.0 / k
    else:
        ker[:, k // 2] = 1.0 / k
    return cv2.filter2D(c, -1, ker)


def banner(title, body, w=1000, time='now'):
    h = 180
    card = rrect(w, h, 40, (1, 1, 1, 0.98)).copy()
    ic = rrect(112, 112, 28, WHITE).copy()
    paste_spr(ic, emblem(92), 56, 56)
    st = R.sdf_stroke(R.rrect_alpha(112, 112, 28, 0), 1.5)
    ic = R.over_spr(ic, solid(cv2.resize(st, (ic.shape[1], ic.shape[0])), (0.85, 0.85, 0.88, 1)))
    paste_spr(card, ic, 90, h / 2)
    s = ts(title, I8, 40, INK)
    paste_spr(card, s, 172 + s.shape[1] / 2, h / 2 - 30)
    s = ts(time, I4, 28, (0.5, 0.5, 0.55, 1))
    paste_spr(card, s, w - 44 - s.shape[1] / 2, h / 2 - 30)
    s = ts(body, I6, 34, INK)
    paste_spr(card, s, 172 + s.shape[1] / 2, h / 2 + 26)
    return card


def film(im, warm=True, amt=1.0, seed=4):
    """Warm, soft, grainy 'old photo' look with a strong vignette."""
    rng = np.random.default_rng(seed)
    im = cv2.GaussianBlur(im, (0, 0), 1.4)
    lum = im.mean(2, keepdims=True)
    im = np.clip(im * np.array([1.12, 0.98, 0.72], np.float32) + 0.04, 0, 1) if warm else im
    im = np.clip((im - 0.5) * 1.12 + 0.5, 0, 1)
    h, w = im.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    im = im * np.clip(1.15 - 0.6 * d ** 2, 0, 1)[..., None]
    im = im + rng.normal(0, 0.05 * amt, (h, w, 1)).astype(np.float32)
    return np.clip(im, 0, 1)


# ------------------------------------------------------------------ the story
def s01():   # "You saw the post. You even saved it."
    c = grey_bg()
    img = web('hero-family.webp', 860, 860, fy=0.45)
    card = post_card(img, ['Could you foster? Your circumstances', 'deserve a conversation.'], saved=True)
    draw(c, blur_sprite(tint(card, (0, 0, 0)), 30), W / 2, 980 + 30, opacity=0.18)
    draw(c, card, W / 2, 980, scale=1.0)
    bx, by = W / 2 + 450 - 60, 980 - card.shape[0] / 2 + 130 + 860 + 55
    scribble_circle(c, bx, by, 52, 46, col=PURPLE)
    scribble_line(c, [(bx - 360, by + 210), (bx - 200, by + 170), (bx - 70, by + 60)], col=PURPLE)
    scribble_text(c, 'saved it…', bx - 470, by + 240, 88, PURPLE)
    return c


def s02():   # "And just like that…"
    c = dark_grad()
    kinetic(c, ['And', 'just', 'like', 'that', '…'], 900, 76)
    draw(c, load_png_sprite(sorted(glob.glob(f'{F.LO2}/assets/cursor/*.png'))[-1]), 260, 1240, scale=0.18, rot=-15)
    return c


def s03():   # "you scrolled past."
    c = dark_grad()
    tb = thumb(web('hero-family.webp', 170, 120))
    kinetic(c, ['You', ('IMG', tb), 'scrolled', 'past.'], 940, 80, font=I8)
    return c


def s04():   # "Because there's always a 'but'… Can I foster if…"
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    g = grad_text('BUT', I9, 520)
    draw(c, g, W / 2 + 30, 860)
    F.pop(c, F.prop('qmark'), 830, 560, 0.75, rays=False)
    F.search_bar(c, 'Can I foster if…', y=1360, w=860)
    return c


def s05():   # "I have pets? I'm retired? I work?" — whip through a wall of doubts
    c = grey_bg()
    tiles = [('balanced-home-outdoors-2026-09-23.webp', 'I have pets?'), ('06-respite-outdoor-play.webp', 'I’m retired?'),
             ('balanced-home-learning-2026-09-23.webp', 'I work?'), ('balanced-home-reading-2026-09-23.webp', 'I have kids?'),
             ('adviser-conversation.webp', 'My health?'), ('03-short-term-everyday-connection.webp', 'I rent?')]
    for j, (name, lab) in enumerate(tiles):
        x = 200 + (j % 3) * 340
        y = 520 + (j // 3) * 520
        im = web(name, 300, 380)
        t = thumb(im, 300, 380, 22)
        draw(c, t, x, y)
        F.chip(c, lab, x, y + 150, fill=PURPLE if j % 2 == 0 else ORANGE, size=30)
    c = motion_blur(c, 81)
    a = np.zeros((300, 400), np.uint8)
    cv2.fillPoly(a, [np.array([[20, 110], [240, 110], [240, 30], [380, 150], [240, 270], [240, 190], [20, 190]])], 255, cv2.LINE_AA)
    sp = solid(a.astype(np.float32) / 255, WHITE)
    draw(c, blur_sprite(tint(sp, (0, 0, 0)), 20), W / 2 + 10, 880 + 16, opacity=0.4)
    draw(c, sp, W / 2, 880)
    draw(c, ts('EVERYONE HAS A “BUT”', I9, 70, INK, 0.02), W / 2, 1520)
    return c


def s06():   # "But what if… you just asked?"
    c = dot_matrix()
    em = rrect(110, 110, 28, WHITE).copy()
    paste_spr(em, emblem(90), 55, 55)
    kinetic(c, ['But,', 'what', 'if', ('IMG', em)], 900, 84, font=I8)
    kinetic(c, ['you', 'just', 'asked?'], 1040, 84, font=I8)
    return c


def popover(rows, w=860, hi=None):
    rh = 104
    h = 150 + rh * len(rows) + 150
    card = rrect(w, h, 34, WHITE).copy()
    s = ts('Can I foster if…', I8, 40, INK)
    paste_spr(card, s, 50 + s.shape[1] / 2, 74)
    tg = F.grad_spr(90, 50, 25)
    tg = tg.copy()
    paste_spr(tg, rrect(40, 40, 20, WHITE), 65, 25)
    paste_spr(card, tg, w - 95, 74)
    for j, (q, a) in enumerate(rows):
        y = 150 + rh * j + rh / 2
        if hi == j:
            paste_spr(card, rrect(w - 40, rh - 14, 18, LAV), w / 2, y)
        s = ts(q, I6, 34, INK)
        paste_spr(card, s, 50 + s.shape[1] / 2, y)
        fill, ink, outline = ANS[a]
        p = F.chip_spr(a, fill, ink, 30, outline) if hasattr(F, 'chip_spr') else None
        tmp = np.zeros((H, W, 3), np.float32)
        ps = ts(a, N9, 30, ink)
        pill = rrect(ps.shape[1] + 48, ps.shape[0] + 24, (ps.shape[0] + 24) / 2, fill).copy()
        if outline:
            st = R.sdf_stroke(R.rrect_alpha(pill.shape[1], pill.shape[0], pill.shape[0] / 2, 0), 3.0)
            pill = R.over_spr(pill, solid(cv2.resize(st, (pill.shape[1], pill.shape[0])), outline))
        paste_spr(pill, ps, pill.shape[1] / 2, pill.shape[0] / 2)
        paste_spr(card, pill, w - 50 - pill.shape[1] / 2, y)
    btn = F.grad_spr(w - 100, 96, 48)
    paste_spr(card, btn, w / 2, h - 90)
    tmp = np.zeros((96, w - 100, 3), np.float32)
    s = ts('Send your question', N9, 40, WHITE)
    paste_spr(card, s, w / 2, h - 90)
    return card


ROWS = [('I have pets', 'Usually'), ('I’m retired', 'Yes'), ('I already have children', 'Yes'), ('I work', 'Possibly'),
        ('A health condition', 'Not automatically')]


def s07():   # "Pets? Usually. Retired? Yes! Children? Yes! Working? Possibly. A health condition? Not automatically."
    c = grey_bg()
    bm = icon('bookmark_fill', 120, INK)
    draw(c, bm, 190, 330)
    F.pop(c, F.prop('paw'), 860, 300, 0.42, rays=False)
    card = popover(ROWS, hi=3)
    draw(c, blur_sprite(tint(card, (0, 0, 0)), 30), W / 2, 1060 + 30, opacity=0.2)
    draw(c, card, W / 2, 1060)
    draw(c, load_png_sprite(sorted(glob.glob(f'{F.LO2}/assets/cursor/*.png'))[-1]), 820, 1080, scale=0.16)
    s = ts('From our FAQs · organicfostering.co.uk/faqs', 'Poppins-Medium', 24, (0.3, 0.3, 0.35, 1))
    draw(c, s, W / 2, 1780)
    return c


def s08():   # "Real people. Honest answers." — feed of real people posts
    c = grey_bg()
    cl = F.clip(42735, 0.5, fx=0.5, fy=0.45, w=860, h=620)
    card = post_card(cl, ['Pets? Usually. “Pets are assessed for temperament,', 'care, safety and likely response to a child.”'],
                     sub='Can I foster if… I have pets?')
    draw(c, card, W / 2, 620)
    cl2 = F.clip(4764, 0.5, fx=0.45, fy=0.4, w=860, h=620)
    card2 = post_card(cl2, ['Retired? Yes. “There’s no fixed upper age limit.”'], sub='Can I foster if… I’m retired?')
    draw(c, card2, W / 2, 620 + card.shape[0] / 2 + 24 + card2.shape[0] / 2)
    F.answer_pill(c, 'Usually', 860, 420, 44)
    return c


def s09():   # "Send your question… and done!"
    c = grey_bg()
    pl = F.prop('plane')
    draw(c, blur_sprite(tint(pl, (0, 0, 0)), 30), 330, 900 + 70, scale=1.4, opacity=0.25)
    draw(c, pl, 330, 860, scale=1.4, rot=8)
    draw(c, ts('And done..!', I8, 92, INK), 770, 1010)
    return c


def s10():   # "A real person in our Manchester team replies. No pressure, no obligation."
    c = grey_bg()
    c = c * 0.92 + F.canvas() * 0.08
    b1 = banner('Organic Fostering', 'A real person in our Manchester team replied', time='now')
    b2 = banner('Organic Fostering', 'No pressure, no obligation.', time='1m')
    draw(c, blur_sprite(tint(b2, (0, 0, 0)), 24), W / 2, 905, scale=0.95, opacity=0.15)
    draw(c, b2, W / 2, 890, scale=0.95, opacity=0.9)
    draw(c, blur_sprite(tint(b1, (0, 0, 0)), 24), W / 2, 1080, opacity=0.2)
    draw(c, b1, W / 2, 1060)
    F.pop(c, F.prop('speech'), 860, 640, 0.42, rays=False)
    return c


def s11():   # "Because somewhere, a child is waiting… for someone like you."
    im = film(web('06-respite-outdoor-play.webp', 900, 1100, fx=0.55, fy=0.45))
    bg = cv2.GaussianBlur(F.cover(im, 0.5, 0.5, 1.0), (0, 0), 50)
    d = np.hypot((R._X - W / 2) / (W * 0.6), (R._Y - H / 2) / (H * 0.45))
    c = (bg * np.clip(1 - d, 0, 1)[..., None] ** 1.5 * 0.85).astype(np.float32)
    sp = thumb(im, 900, 1100, 40, border=(1, 1, 1, 0))
    draw(c, sp, W / 2, H / 2 - 40)
    s = ts('[ that smile? ]', I6, 30, WHITE)
    draw(c, rrect(s.shape[1] + 30, 52, 8, (0, 0, 0, 0.55)), W / 2, H / 2 + 420)
    draw(c, s, W / 2, H / 2 + 420)
    draw(c, avatar(70), 150, 300)
    draw(c, ts('organicfostering', I8, 30, WHITE), 330, 284)
    draw(c, ts('A safe home: every day ( for as long as needed )', I4, 26, (1, 1, 1, 0.8)), 470, 322)
    scribble_text(c, 'for someone like you ♡'.replace(' ♡', ''), 520, 1640, 96, hexc_yellow(), rot=-5)
    return c


def hexc_yellow():
    return (1.0, 0.84, 0.35, 1.0)


def s12():   # "Organic Fostering." — black end card
    c = np.zeros((H, W, 3), np.float32)
    draw(c, avatar(110), W / 2, 680)
    draw(c, ts('MADE WITH CARE', I8, 44, WHITE, 0.02), W / 2, 820)
    draw(c, ts('@organicfostering', I4, 28, (1, 1, 1, 0.7)), W / 2, 870)
    btn = F.grad_spr(640, 110, 55)
    draw(c, blur_sprite(btn, 24), W / 2, 1030, opacity=0.5)
    draw(c, btn, W / 2, 1020)
    F.text_arrow(c, 'Send your question', W / 2, 1020, size=44)
    draw(c, ts('0161 241 1332  ·  organicfostering.co.uk', I6, 30, (1, 1, 1, 0.85)), W / 2, 1150)
    draw(c, F.star(ORANGE, 30), W / 2 - 260, 1220)
    draw(c, ts('Rated Good by Ofsted · Inspected May 2025', I4, 26, (1, 1, 1, 0.7)), W / 2 + 20, 1220)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.12, grain=0.012, vig=0.15))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 6:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 6]) for i in range(0, len(th), 6)]),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
