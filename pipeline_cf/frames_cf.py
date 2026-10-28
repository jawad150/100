"""Scene images (one per voice beat) for Organic Fostering "Can I Foster If…?" — people version.

Story: across Manchester, people quietly think about fostering, then hit a "but". A glowing search bar (magenta-to-
orange brand ring) floats beside them like a thought: "Can I foster if…". Each doubt opens as an answer card over a
real person living that situation (a couple with their dog, a retired couple, a family breakfast, someone closing
their laptop, a woman in a wheelchair), with the site's honest answer pill: Yes · Usually · Possibly · Not
automatically. The bar finally becomes the "Send your question →" button.

Every answer on screen is quoted from organicfostering.co.uk/faqs (via the concept PDF). Never a red, never a cross.

Usage: python3 frames_cf.py  -> workspace_cf/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import reel_sol as R
from reel_sol import W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, hexc, _wmask

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_cf'))
OUT = f'{S}/frames'
LO2 = os.path.abspath(os.path.join(HERE, '..', 'workspace_lo2'))
OF = os.path.abspath(os.path.join(HERE, '..', 'workspace_of'))

PURPLE, ORANGE, PLUM = hexc('#B7006E'), hexc('#FF6411'), hexc('#5B174F')
IVORY, LAV, PEACH, LEAF = hexc('#FCF8F5'), hexc('#F6EAF3'), hexc('#FFD4BA'), hexc('#64A60B')
LAV_D = hexc('#D9B8D2')
WHITE = (1.0, 1.0, 1.0, 1.0)
N9, N8, N7, N4 = 'Nunito-900', 'Nunito-800', 'Nunito-700', 'Nunito-400'
PM = 'Poppins-Medium'
ANS = {'Yes': (LEAF, WHITE, None), 'Usually': (WHITE, LEAF, LEAF), 'Possibly': (PEACH, PLUM, None),
       'Not automatically': (LAV_D, PLUM, None)}


# ------------------------------------------------------------------ sources
def grade(im):
    """Warm, soft grade: plum-tinted shadows, peachy highlights."""
    lum = im.mean(2, keepdims=True)
    im = np.clip((im - 0.5) * 1.05 + 0.5, 0, 1)
    sh = np.clip(1 - lum * 2.0, 0, 1)
    hi = np.clip((lum - 0.55) * 2.2, 0, 1)
    im = im * (1 - 0.2 * sh) + np.array(PLUM[:3], np.float32) * 0.2 * sh
    im = im + hi * np.array([0.04, 0.015, -0.01], np.float32)
    return np.clip(im, 0, 1).astype(np.float32)


def cover(im, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    out = cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if sc > 1.5:
        bl = cv2.GaussianBlur(out, (0, 0), 1.6)
        out = np.clip(out * 1.45 - bl * 0.45, 0, 1)
    return out


def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return grade(cover(im[..., ::-1].astype(np.float32) / 255, fx, fy, z, w, h))


def prop(name):
    return load_png_sprite(f'{S}/assets/{name}.png')


def lo2(name):
    return load_png_sprite(sorted(glob.glob(f'{LO2}/assets/{name}/*.png'))[-1])


def logo():
    return load_png_sprite(f'{OF}/src/logo_full.png')


# ------------------------------------------------------------------ overlays
def shade(c, top=0.55, amt=0.85, col=PLUM):
    g = np.clip((R._Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    return c * (1 - amt * g) + np.array(col[:3], np.float32) * amt * g


def top_shade(c, h=0.2, amt=0.5):
    g = np.clip(1 - R._Y / (H * h), 0, 1)[..., None] ** 1.5
    return c * (1 - amt * g)


def canvas():
    """Ivory-to-lavender help-centre canvas with slow magenta and orange glows."""
    k = (R._Y / H)[..., None]
    c = np.array(IVORY[:3], np.float32) * (1 - k) + np.array(LAV[:3], np.float32) * k
    for x, y, r, col, a in ((180, 380, 520, PURPLE, 0.16), (930, 1500, 600, ORANGE, 0.14)):
        g = np.exp(-((R._X - x) ** 2 + (R._Y - y) ** 2) / (2 * r * r))[..., None] * a
        c = c * (1 - g) + np.array(col[:3], np.float32) * g
    return c.astype(np.float32)


def glow(c, x, y, r, col=ORANGE, amt=0.4):
    g = np.exp(-((R._X - x) ** 2 + (R._Y - y) ** 2) / (2 * r * r))[..., None] * amt
    c[:] = c * (1 - g) + np.array(col[:3], np.float32) * g


def grad_spr(w, h, r, a0=PURPLE, a1=ORANGE, phase=0.0):
    """Rounded rect filled with the brand magenta-to-orange gradient (premultiplied)."""
    m = R.sdf_fill(R.rrect_alpha(int(w), int(h), r, 2))
    hh, ww = m.shape
    u = (np.arange(ww, dtype=np.float32)[None, :] / ww + phase) % 1.0
    u = 0.5 - 0.5 * np.cos(u * 2 * math.pi)
    col = np.array(a0[:3], np.float32) * (1 - u[..., None]) + np.array(a1[:3], np.float32) * u[..., None]
    col = np.broadcast_to(col, (hh, ww, 3))
    return np.concatenate([col * m[..., None], m[..., None]], 2).astype(np.float32)


def drop(c, spr, x, y, sc=1.0, rot=0, sh=0.4, sigma=20):
    draw(c, blur_sprite(tint(spr, PLUM[:3]), sigma), x + 6, y + 20, scale=sc, rot=rot, opacity=sh)
    draw(c, spr, x, y, scale=sc, rot=rot)


def pop(c, spr, x, y, sc=1.0, rays=True, col=ORANGE):
    if rays:
        lay = np.zeros((H, W), np.uint8)
        r0 = max(spr.shape[:2]) * sc * 0.44
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = 28 if j % 2 else 44
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((y + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + ln)) * 4), int((y + math.sin(a) * (r0 + ln)) * 4)), 255, 5 * 4,
                     cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.9
        c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    drop(c, spr, x, y, sc)


def chip(c, text, x, y, fill=PURPLE, ink=WHITE, size=38, rot=0, font=N8, outline=None, opacity=1.0):
    s = ts(text, font, size, ink, 0.0)
    p = rrect(s.shape[1] + 56, s.shape[0] + 30, (s.shape[0] + 30) / 2, fill).copy()
    if outline:
        st = R.sdf_stroke(R.rrect_alpha(p.shape[1], p.shape[0], p.shape[0] / 2, 0), 3.0)
        st = cv2.resize(st, (p.shape[1], p.shape[0]))
        p = R.over_spr(p, solid(st, outline))
    paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
    draw(c, blur_sprite(tint(p, PLUM[:3]), 12), x + 5, y + 12, rot=rot, opacity=0.35 * opacity)
    draw(c, p, x, y, rot=rot, opacity=opacity)
    return p.shape[1]


def answer_pill(c, ans, x, y, size=58):
    fill, ink, outline = ANS[ans]
    return chip(c, ans, x, y, fill=fill, ink=ink, size=size, font=N9, outline=outline)


def search_bar(c, text, x=W / 2, y=760, w=900, size=50, caret=True, label=None, phase=0.0):
    """The brand search bar: white pill with a turning magenta→orange gradient ring and a soft glow."""
    h = 124
    ring = grad_spr(w + 14, h + 14, (h + 14) / 2, phase=phase)
    draw(c, blur_sprite(ring, 26), x, y, opacity=0.75)
    draw(c, ring, x, y)
    draw(c, rrect(w, h, h / 2, (1, 1, 1, 1)), x, y)
    m = np.zeros((56, 56), np.uint8)
    cv2.circle(m, (22, 22), 15, 255, 5, cv2.LINE_AA)
    cv2.line(m, (33, 33), (49, 49), 255, 7, cv2.LINE_AA)
    draw(c, solid(m.astype(np.float32) / 255, PURPLE), x - w / 2 + 64, y)
    x0 = x - w / 2 + 112
    if text:
        s = ts(text, N8, size, PLUM)
        draw(c, s, x0 + s.shape[1] / 2, y)
        x0 += s.shape[1] + 10
    if caret:
        draw(c, rrect(5, size * 1.15, 2, PURPLE), x0 + 4, y)
    if label:
        s = ts(label, N8, 40, WHITE)
        draw(c, blur_sprite(tint(s, PLUM[:3]), 8), x + 2, y - h / 2 - 54, opacity=0.6)
        draw(c, s, x, y - h / 2 - 56)


def suggest_list(c, rows, x=W / 2, y=900, w=900, hi=0, dim=None):
    rh = 92
    hgt = rh * len(rows) + 30
    drop(c, rrect(w, hgt, 22, (1, 1, 1, 0.97)), x, y + hgt / 2, sh=0.35)
    for j, r in enumerate(rows):
        yy = y + 15 + rh * j + rh / 2
        if j == hi:
            draw(c, rrect(w - 24, rh - 12, 16, LAV), x, yy)
        a = 0.4 if dim is not None and j != dim else 1.0
        s = ts(r, N7, 40, PLUM)
        draw(c, s, x - w / 2 + 44 + s.shape[1] / 2, yy, opacity=a)


def answer_card(c, q, ans, quote, y=1150, x=W / 2, w=920, n=None):
    """Answer card: question, answer pill, the FAQ line (quoted) and the source."""
    lines = wrap(quote, N7, 36, w - 100)
    hgt = 250 + len(lines) * 48
    top = y - hgt / 2
    drop(c, rrect(w, hgt, 22, (1, 1, 1, 0.97)), x, y, sh=0.4)
    s = ts('CAN I FOSTER IF…', PM, 24, PURPLE, 0.16)
    draw(c, s, x - w / 2 + 50 + s.shape[1] / 2, top + 50)
    if n:
        s = ts(n, PM, 24, (0.36, 0.09, 0.31, 0.6), 0.12)
        draw(c, s, x + w / 2 - 50 - s.shape[1] / 2, top + 50)
    s = ts(q, N9, 56, PLUM)
    draw(c, s, x - w / 2 + 50 + s.shape[1] / 2, top + 112)
    pw = chip_w(ans, 46)
    answer_pill(c, ans, x - w / 2 + 50 + pw / 2, top + 190, 46)
    for j, ln in enumerate(lines):
        s = ts(ln, N7, 36, (0.36, 0.09, 0.31, 0.85))
        draw(c, s, x - w / 2 + 50 + s.shape[1] / 2, top + 262 + j * 48)
    return top, hgt


def chip_w(text, size, font=N9):
    return ts(text, font, size, WHITE).shape[1] + 56


def wrap(text, font, size, maxw):
    out, cur = [], ''
    for w in text.split(' '):
        t = (cur + ' ' + w).strip()
        if cur and ts(t, font, size, WHITE).shape[1] > maxw:
            out.append(cur)
            cur = w
        else:
            cur = t
    out.append(cur)
    return out


def source(c, y=1850):
    s = ts('From our FAQs · organicfostering.co.uk/faqs', PM, 22, (1, 1, 1, 0.92), 0.04)
    w = s.shape[1] + 40
    draw(c, rrect(w, 46, 23, (0.36, 0.09, 0.31, 0.7)), W - 60 - w / 2, y)
    draw(c, s, W - 60 - w / 2, y)


def counter(c, k, n=5, y=150):
    """Doubt counter: five dots, answered ones filled with the gradient."""
    s = ts('%d / %d' % (k, n), N8, 30, WHITE, 0.06)
    draw(c, s, 70 + s.shape[1] / 2, y)
    for j in range(n):
        x = 190 + j * 40
        if j < k:
            draw(c, grad_spr(26, 26, 13, phase=j * 0.15), x, y)
        else:
            draw(c, rrect(26, 26, 13, (1, 1, 1, 0.35)), x, y)


def tag(c, text, x=70, y=170):
    s = ts(text, N8, 30, WHITE, 0.12)
    w = s.shape[1] + 90
    draw(c, rrect(w, 66, 33, (0.36, 0.09, 0.31, 0.6)), x + w / 2, y)
    m = np.zeros((44, 32), np.uint8)
    cv2.circle(m, (16, 15), 13, 255, -1, cv2.LINE_AA)
    cv2.fillPoly(m, [np.array([[5, 21], [27, 21], [16, 41]])], 255, cv2.LINE_AA)
    cv2.circle(m, (16, 15), 5, 0, -1, cv2.LINE_AA)
    draw(c, solid(m.astype(np.float32) / 255, ORANGE), x + 38, y)
    draw(c, s, x + 64 + s.shape[1] / 2, y)


def caption(c, lines, y=1600, size=76, x0=80):
    """Nunito Black caption; key words get a magenta→orange gradient underline swoosh."""
    for li, line in enumerate(lines):
        x = x0
        yy = y + li * size * 1.2
        for w, key in line:
            s = solid(_wmask(w, N9, size), WHITE)
            if key:
                u = grad_spr(s.shape[1] - 8, size * 0.2, size * 0.1)
                draw(c, u, x + s.shape[1] / 2, yy + size * 0.52)
            draw(c, blur_sprite(tint(s, PLUM[:3]), 10), x + s.shape[1] / 2 + 3, yy + 6, opacity=0.55)
            draw(c, s, x + s.shape[1] / 2, yy)
            x += s.shape[1] + size * 0.2


def age_track(c, y=1500, x0=120):
    """'No fixed upper age limit': a track that draws off the edge with no end marker."""
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (x0 * 4, y * 4), ((W + 40) * 4, y * 4), 255, 8 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    col = np.array(LEAF[:3], np.float32) * (1 - (R._X / W)[..., None]) + np.array(ORANGE[:3], np.float32) * (R._X / W)[..., None]
    c[:] = c * (1 - m) + col * m
    for j, a in enumerate((30, 50, 70, 90)):
        x = x0 + 40 + j * 230
        draw(c, rrect(4, 26, 2, WHITE), x, y)
        s = ts(str(a), N8, 30, WHITE)
        draw(c, s, x, y - 40)
    text_arrow(c, 'no upper limit', W - 210, y + 46, font=N8, size=30)


def arrow(col=WHITE, size=52):
    """Right arrow sprite (Nunito has no → glyph)."""
    w, h = int(size * 0.9), int(size * 0.8)
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.line(m, (4 * 4, h * 2), ((w - 10) * 4, h * 2), 255, int(size * 0.13) * 4, cv2.LINE_AA)
    cv2.polylines(m, [np.array([[(w - h * 0.42 - 6) * 4, h * 4 * 0.14], [(w - 6) * 4, h * 2], [(w - h * 0.42 - 6) * 4, h * 4 * 0.86]], np.int32)],
                  False, 255, int(size * 0.13) * 4, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return solid(m, col)


def star(col=ORANGE, size=34):
    r = size * 2
    pts = [((r + r * (1 if i % 2 == 0 else 0.45) * math.sin(i * math.pi / 5)), (r - r * (1 if i % 2 == 0 else 0.45) * math.cos(i * math.pi / 5)))
           for i in range(10)]
    m = np.zeros((2 * r, 2 * r), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    return solid(cv2.resize(m, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, col)


def text_arrow(c, text, x, y, font=N9, size=52, col=WHITE):
    s = ts(text, font, size, col)
    a = arrow(col, size)
    tw = s.shape[1] + 16 + a.shape[1]
    draw(c, s, x - tw / 2 + s.shape[1] / 2, y)
    draw(c, a, x + tw / 2 - a.shape[1] / 2, y + 2)


def cta_button(c, x, y):
    btn = grad_spr(760, 130, 65)
    draw(c, blur_sprite(btn, 24), x, y + 20, opacity=0.55)
    draw(c, btn, x, y)
    text_arrow(c, 'Send your question', x, y)


# ------------------------------------------------------------------ the story, beat by beat
def s01():   # "Every day, across Manchester, someone thinks about fostering."
    c = clip(46494, 0.4, fx=0.5, fy=0.5)
    c = shade(top_shade(c), 0.5)
    tag(c, 'MANCHESTER · NORTH WEST')
    pop(c, prop('house'), 820, 640, 0.6)
    caption(c, [[('Thinking', False), ('about', False)], [('fostering?', True)]], y=1520, size=96)
    return c


def s02():   # "And then comes the 'but'… can I foster if…"
    c = clip(33379, 0.5, fx=0.55, fy=0.5)
    c = shade(c, 0.5, 0.8)
    search_bar(c, 'Can I foster if…', y=1060, label='How can we help?')
    pop(c, prop('qmark'), 860, 560, 0.55)
    caption(c, [[("You've", False), ('probably', False), ('wondered…', True)]], y=1640, size=70)
    return c


Q = ['…I have pets?', '…I’m retired?', '…I already have children?', '…I work?', '…I have a health condition?']


def s03():   # "Here are the honest answers."
    c = clip(15776, 0.5, fx=0.45, fy=0.4)
    c = shade(c, 0.35, 0.85)
    search_bar(c, 'Can I foster if', y=700, caret=True)
    suggest_list(c, Q, y=800, hi=0)
    pop(c, prop('magnifier'), 880, 1500, 0.42)
    caption(c, [[('Here', False), ('are', False), ('the', False), ('honest', True), ('answers.', False)]], y=1720, size=68)
    return c


def s04():   # "Pets? Usually. They're assessed for temperament and safety."
    c = clip(42735, 0.5, fx=0.5, fy=0.45)
    c = top_shade(c, 0.25)
    counter(c, 1)
    pop(c, prop('paw'), 850, 420, 0.5)
    top, h = answer_card(c, 'I have pets?', 'Usually',
                         '“Pets are assessed for temperament, care, safety and likely response to a child.”', y=1300, n='1 of 5')
    chip(c, 'Temperament', 300, top - 50, fill=PURPLE, rot=-3)
    chip(c, 'Safety', 700, top - 40, fill=ORANGE, rot=3)
    source(c)
    return c


def s05():   # "Retired? Yes. There's no fixed upper age limit."
    c = clip(4764, 0.5, fx=0.45, fy=0.4)
    c = shade(top_shade(c, 0.25), 0.62, 0.85)
    counter(c, 2)
    pop(c, prop('infinity'), 820, 960, 0.48)
    answer_card(c, 'I’m retired?', 'Yes', '“There’s no fixed upper age limit.”', y=1180, n='2 of 5')
    age_track(c, y=1560)
    source(c)
    return c


def s06():   # "Already have children? Yes. Their views are part of the assessment."
    c = clip(15800, 0.55, fx=0.5, fy=0.45)
    c = top_shade(c, 0.25)
    counter(c, 3)
    pop(c, prop('speech'), 300, 470, 0.5)
    chip(c, 'Their views', 300, 640, fill=LAV_D, ink=PLUM, rot=-3)
    answer_card(c, 'I already have children?', 'Yes',
                '“Your children’s views, ages, needs and the possible effect of fostering on family life form part of assessment.”',
                y=1330, n='3 of 5')
    source(c)
    return c


def s07():   # "Working? Possibly. It depends on your hours, flexibility and support."
    c = clip(4954, 0.5, fx=0.5, fy=0.45)
    c = top_shade(c, 0.25)
    counter(c, 4)
    pop(c, lo2('clock'), 850, 460, 0.5)
    top, h = answer_card(c, 'I work?', 'Possibly',
                         '“It depends on your hours, flexibility, support network, household and the child’s needs.”', y=1330, n='4 of 5')
    for j, (t, col, ink) in enumerate((('Hours', PURPLE, WHITE), ('Flexibility', ORANGE, WHITE), ('Support', PEACH, PLUM))):
        chip(c, t, 210 + j * 300, top - 50, fill=col, ink=ink, rot=(-3, 2, -2)[j])
    source(c)
    return c


def s08():   # "A health condition? It doesn't automatically rule you out."
    c = clip(47980, 0.5, fx=0.5, fy=0.42, z=1.0)
    c = top_shade(c, 0.25)
    counter(c, 5)
    pop(c, lo2('heart'), 830, 430, 0.5)
    answer_card(c, 'I have a health condition?', 'Not automatically',
                '“A disability, medical condition or mental-health history does not automatically prevent fostering.”', y=1330,
                n='5 of 5')
    source(c)
    return c


def s09():   # "Your question's not on the list? Your circumstances deserve a conversation."
    c = clip(39791, 0.5, fx=0.5, fy=0.45)
    c = shade(c, 0.45, 0.85)
    search_bar(c, 'Can I foster if', y=820, phase=0.3)
    drop(c, rrect(860, 300, 22, (1, 1, 1, 0.96)), W / 2, 1160)
    s = ts('NOT ON THE LIST?', PM, 26, PURPLE, 0.16)
    draw(c, s, W / 2, 1060)
    for j, ln in enumerate(('Your circumstances', 'deserve a conversation.')):
        draw(c, ts(ln, N9, 54, PLUM), W / 2, 1140 + j * 70)
    pop(c, prop('speech'), 880, 1440, 0.42)
    caption(c, [[('Your', False), ('question', True), ('not', False), ('on', False), ('the', False), ('list?', False)]], y=1680,
            size=64)
    return c


def s10():   # "Send your question to a real person in our Manchester team."
    c = clip(23073, 0.5, fx=0.6, fy=0.45)
    c = shade(c, 0.45, 0.85)
    cta_button(c, W / 2, 980)
    draw(c, lo2('cursor'), 760, 1060, scale=0.35)
    pop(c, prop('plane'), 840, 560, 0.55)
    chip(c, 'A real person replies', 340, 1170, fill=WHITE, ink=PLUM, rot=-2)
    chip(c, 'Manchester team', 760, 1250, fill=PURPLE, rot=2)
    caption(c, [[('A', False), ('real', True), ('person,', True)], [('in', False), ('Manchester.', False)]], y=1600, size=76)
    return c


def s11():   # "No pressure, no obligation."
    c = clip(18258, 0.5, fx=0.5, fy=0.45)
    c = shade(top_shade(c), 0.5, 0.85)
    caption(c, [[('No', False), ('pressure,', True)], [('no', False), ('obligation.', True)]], y=1500, size=100)
    return c


def s12():   # "Organic Fostering." end card
    c = canvas()
    lg = logo()
    sc = 760 / lg.shape[1]
    draw(c, lg, W / 2, 560, scale=sc)
    cta_button(c, W / 2, 980)
    draw(c, ts('No pressure, no obligation.', N7, 40, PLUM), W / 2, 1120)
    draw(c, ts('0161 241 1332', N9, 64, PURPLE), W / 2, 1290)
    draw(c, ts('organicfostering.co.uk', N8, 44, PLUM), W / 2, 1375)
    s = ts('Rated Good by Ofsted · Inspected May 2025', N7, 30, PLUM)
    drop(c, rrect(s.shape[1] + 110, 70, 35, (1, 1, 1, 0.95)), W / 2, 1520, sh=0.25)
    draw(c, star(), W / 2 - s.shape[1] / 2 - 10, 1520)
    draw(c, s, W / 2 + 20, 1520)
    pop(c, prop('house'), 870, 820, 0.32, rays=False)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = to_u8(R.post(fn(), j, bloom=0.1, grain=0.01, vig=0.25 if j != 12 else 0.0))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 6:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 6]) for i in range(0, len(th), 6)]),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
