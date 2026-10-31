"""Storyboards (3 options) for Organic Fostering "One Weekend at a Time" — respite fostering static post, 1080x1350.

Sketch-style layout boards: the post drawn flat with numbered callouts, and a notes column beside it.
Usage: python3 storyboard_respite.py -> workspace_respite/storyboards/option_A|B|C.jpg + overview.jpg
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
from frames_cf import draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask, PURPLE, ORANGE, PLUM, PEACH, LEAF, WHITE, N9, N8, N7

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_respite'))
OUT = f'{S}/storyboards'
PW, PH = 1080, 1350
NOTE_W = 760
HAND = 'Caveat-700'
PAPER = (0.97, 0.955, 0.93)
PENCIL = (0.33, 0.27, 0.32, 1)
CREAM = (1.0, 0.992, 0.984, 1)
PEACH_W = (1.0, 0.86, 0.77)
INK = PLUM


def canvas(col):
    return np.ones((PH, PW, 3), np.float32) * np.array(col[:3], np.float32)


def outline(c, x, y, w, h, r=10, col=PENCIL, th=3, fill=None, rot=0.0):
    if fill is not None:
        draw(c, rrect(w, h, r, fill), x, y, rot=rot)
    m = cv2.resize(F.R.sdf_stroke(F.R.rrect_alpha(int(w), int(h), r, 0), th), (int(w), int(h)))
    draw(c, solid(m, col), x, y, rot=rot)


def text(c, s, x, y, font=N9, size=40, col=INK, anchor='l'):
    sp = ts(s, font, size, col)
    xx = x + sp.shape[1] / 2 if anchor == 'l' else x
    draw(c, sp, xx, y)
    return sp.shape[1]


def hand(c, s, x, y, size=40, col=INK, rot=0, anchor='c'):
    sp = solid(_wmask(s, HAND, size), col)
    xx = x if anchor == 'c' else x + sp.shape[1] / 2
    draw(c, sp, xx, y, rot=rot)
    return sp.shape[1]


def marker_circle(c, x, y, rx, ry, col=ORANGE, th=5, seed=1):
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * math.pi * 1.12, 120)
    pts = np.stack([x + rx * np.cos(t) * (1 + 0.04 * np.sin(3 * t)) + rng.normal(0, 0.8, len(t)),
                    y + ry * np.sin(t) * (1 + 0.05 * np.cos(2 * t)) + rng.normal(0, 0.8, len(t))], 1)
    lay = np.zeros(c.shape[:2], np.uint8)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def pin(c, n, x, y):
    draw(c, rrect(46, 46, 23, ORANGE), x, y)
    draw(c, ts(str(n), N9, 26, WHITE), x, y)


def grad_btn(c, label, x, y, w=560, h=86):
    b = F.grad_spr(w, h, h / 2)
    draw(c, b, x + w / 2, y)
    F.text_arrow(c, label, x + w / 2, y, size=30)


def logo(c, x, y, w=220):
    lg = F.logo()
    draw(c, lg, x + w / 2, y, scale=w / lg.shape[1])


def eyebrow(c, label, x, y, right=True):
    sp = ts(label.upper(), 'Poppins-SemiBold', 24, PLUM)
    w = sp.shape[1] + 44
    cx = x - w / 2 if right else x + w / 2
    draw(c, rrect(w, 52, 26, CREAM), cx, y)
    draw(c, sp, cx, y)


def signoff(c, y=1215):
    grad_btn(c, 'Talk to us about respite fostering', 70, y, 590, 84)
    text(c, '0161 241 1332 · organicfostering.co.uk', 70, y + 78, N7, 26, INK)
    sp = ts('Rated Good by Ofsted', N7, 24, INK)
    draw(c, F.star(ORANGE, 24), 1010 - sp.shape[1] - 24, y + 78)
    draw(c, sp, 1010 - sp.shape[1] / 2, y + 78)


def headline(c, l1, l2_parts, y=230, size=74, x=70):
    text(c, l1, x, y, N9, size, INK)
    xx = x
    for part, col in l2_parts:
        xx += text(c, part, xx, y + size * 1.08, N9, size, col) + size * 0.25


def subline(c, y=1120):
    text(c, 'Respite fostering gives a child planned short breaks:', 70, y, N8, 30, INK)
    text(c, 'one night, a weekend or part of a school holiday.', 70, y + 40, N8, 30, INK)


# ------------------------------------------------------------------ option A: the calendar (PDF concept)
def option_a():
    c = canvas(PEACH_W)
    # window light
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    c = c * (0.93 + 0.1 * np.clip((xx - 300) / 800, 0, 1))[..., None]
    for k in range(3):
        band = ((np.abs((xx * 0.8 + yy * 0.3) - (900 + k * 160)) < 30)).astype(np.float32)[..., None] * 0.04
        c = c + band
    logo(c, 70, 95)
    eyebrow(c, 'Respite fostering', 1010, 95)
    headline(c, 'Some fostering happens', [('one weekend', ORANGE), ('at a time.', INK)], y=220)
    # calendar
    cx, cy, cw, ch = 540, 700, 860, 640
    rot = -2.0
    cal = np.ones((ch, cw, 4), np.float32)
    cal[..., :3] = np.array(CREAM[:3], np.float32)
    calc = cal[..., :3].copy()
    text(calc, 'November', 40, 50, N9, 44, INK)
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    gx, gy, cwid, chei = 30, 110, (cw - 60) / 7, (ch - 140) / 6
    for i, d in enumerate(days):
        text(calc, d, gx + i * cwid + 10, gy - 8, 'Poppins-SemiBold', 18, (0.45, 0.3, 0.42, 1))
    for r in range(7):
        cv2.line(calc, (int(gx), int(gy + 10 + r * chei)), (int(cw - 30), int(gy + 10 + r * chei)), (0.82, 0.78, 0.8), 1)
    for i in range(8):
        cv2.line(calc, (int(gx + i * cwid), int(gy + 10)), (int(gx + i * cwid), int(gy + 10 + 6 * chei)), (0.82, 0.78, 0.8), 1)
    notes = {3: 'Swim 6pm', 5: 'Bonfire night', 11: 'Dentist', 16: 'Book club', 19: 'Training', 28: "Mum's 60th"}
    for day in range(1, 31):
        idx = day + 5          # Nov 1 2026 is a Sunday -> column 6
        r, col = divmod(idx, 7)
        x0, y0 = gx + col * cwid, gy + 10 + r * chei
        text(calc, str(day), x0 + 8, y0 + 18, N8, 20, INK)
        if day in notes:
            hand(calc, notes[day], x0 + cwid / 2, y0 + chei * 0.6, 26, (0.25, 0.22, 0.45, 1))
    for (d1, label, seed) in ((7, 'Pancakes + park', 2), (21, 'Pancakes again!', 3)):
        r, col = divmod(d1 + 5, 7)
        x0, y0 = gx + col * cwid, gy + 10 + r * chei
        marker_circle(calc, x0 + cwid, y0 + chei / 2, cwid * 1.0, chei * 0.48, seed=seed)
        hand(calc, label, x0 + cwid, y0 + chei * 0.68, 30, ORANGE)
    cal[..., :3] = calc
    draw(c, blur_sprite(tint(cal, (0.3, 0.15, 0.1)), 18), cx + 10, cy + 20, rot=rot, opacity=0.35)
    draw(c, cal, cx, cy, rot=rot)
    draw(c, rrect(54, 54, 27, ORANGE), cx + 10, cy - ch / 2 + 6)
    subline(c, 1100)
    signoff(c, 1225)
    pins = [(1, 40, 95), (2, 1040, 140), (3, 40, 230), (4, 120, 420), (5, 940, 600), (6, 40, 1100), (7, 40, 1225)]
    notes_txt = [
        'Logo: the real Organic Fostering SVG, top left.',
        'Eyebrow pill: "Respite fostering".',
        'Headline: "Some fostering happens one weekend at a time." Nunito Black, plum, "one weekend" in orange.',
        'The hero: a real paper wall calendar on a peach kitchen wall, slightly crooked, held by an orange magnet. Everyday notes are texture: Swim 6pm, Bonfire night, Dentist, Book club...',
        'The story: two weekends circled in orange marker. "Pancakes + park", then two weeks later "Pancakes again!": the same child came back, trust is growing.',
        'Subline from the website: planned short breaks, one night, a weekend or part of a school holiday.',
        'Sign-off: gradient button, phone, web address, Rated Good by Ofsted.',
    ]
    return c, pins, notes_txt, 'Option A · The Calendar', 'The PDF concept. A family wall calendar tells the story: the same child coming back for "Pancakes again!".'


# ------------------------------------------------------------------ option B: the weekend bag
def option_b():
    c = canvas((0.98, 0.9, 0.84))
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    floor = (yy > 1010).astype(np.float32)[..., None]
    c = c * (1 - floor) + floor * np.array([0.82, 0.66, 0.52], np.float32)
    logo(c, 70, 95)
    eyebrow(c, 'Respite fostering', 1010, 95)
    headline(c, 'Some fostering fits', [('in a weekend bag.', ORANGE)], y=220)
    # front door (right)
    outline(c, 860, 720, 300, 580, 8, PENCIL, 3, fill=(0.36, 0.09, 0.31, 1))
    draw(c, rrect(18, 18, 9, (0.95, 0.8, 0.4, 1)), 740, 740)
    outline(c, 860, 500, 220, 70, 6, (1, 1, 1, 0.6), 2)
    # coat hooks + bag
    draw(c, rrect(380, 26, 8, (0.75, 0.55, 0.4, 1)), 420, 520)
    for x in (300, 420, 540):
        draw(c, rrect(20, 40, 8, (0.55, 0.38, 0.28, 1)), x, 545)
    # rucksack shape
    bag = np.zeros((420, 320), np.uint8)
    cv2.ellipse(bag, (160, 230), (140, 180), 0, 0, 360, 255, -1, cv2.LINE_AA)
    cv2.rectangle(bag, (30, 230), (290, 410), 255, -1)
    bg = solid(bag.astype(np.float32) / 255, (0.97, 0.45, 0.2, 1))
    draw(c, blur_sprite(tint(bg, (0.2, 0.1, 0.05)), 16), 430, 790, opacity=0.35)
    draw(c, bg, 420, 770)
    outline(c, 420, 840, 200, 120, 30, (0.6, 0.22, 0.1, 1), 4)
    lay = np.zeros((PH, PW), np.uint8)
    cv2.ellipse(lay, (420 * 4, 580 * 4), (60 * 4, 50 * 4), 0, 180, 360, 255, 8 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array([0.55, 0.2, 0.08], np.float32) * m
    # luggage tag
    tag = rrect(300, 150, 16, CREAM).copy()
    draw(c, tag, 230, 900, rot=-8)
    hand(c, 'Fri 5pm', 230, 870, 40, PLUM, rot=-8)
    hand(c, 'back again soon!', 230, 925, 36, ORANGE, rot=-8)
    cv2.line(c, (330, 860), (380, 820), (0.4, 0.3, 0.3), 2, cv2.LINE_AA)
    # small wellies + sticky note
    for x in (560, 610):
        draw(c, rrect(44, 110, 14, (0.46, 0.65, 0.04, 1)), x, 1000)
    draw(c, rrect(170, 150, 6, (1.0, 0.94, 0.55, 1)), 640, 460, rot=5)
    hand(c, 'Pancakes', 640, 445, 34, PLUM, rot=5)
    hand(c, 'Saturday?', 640, 485, 34, PLUM, rot=5)
    subline(c, 1100)
    signoff(c, 1225)
    pins = [(1, 40, 95), (2, 1040, 140), (3, 40, 230), (4, 600, 680), (5, 100, 900), (6, 750, 420), (7, 40, 1100), (8, 40, 1225)]
    notes_txt = [
        'Logo, top left.',
        'Eyebrow pill: "Respite fostering".',
        'Headline: "Some fostering fits in a weekend bag." The second line in orange.',
        'The hero: a small packed rucksack hanging on a coat hook by a plum front door, a pair of little green wellies on the mat. Warm hallway light. No people.',
        'Handwritten luggage tag: "Fri 5pm · back again soon!" One look says: a planned stay, and a child who returns.',
        'A yellow sticky note on the wall: "Pancakes Saturday?" The small, warm detail that makes people smile.',
        'Subline from the website: planned short breaks, one night, a weekend or part of a school holiday.',
        'Sign-off: gradient button, phone, web address, Rated Good by Ofsted.',
    ]
    return c, pins, notes_txt, 'Option B · The Weekend Bag', 'A packed little rucksack by the front door with a tag "Fri 5pm, back again soon!": a planned break, and someone coming back.'


# ------------------------------------------------------------------ option C: one night · a weekend · a holiday
def option_c():
    c = canvas((0.99, 0.97, 0.96))
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    for x0, y0, r, col, a in ((150, 200, 420, PURPLE, 0.12), (950, 1150, 480, ORANGE, 0.14)):
        g = np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * r * r))[..., None] * a
        c = c * (1 - g) + np.array(col[:3], np.float32) * g
    logo(c, 70, 95)
    eyebrow(c, 'Respite fostering', 1010, 95)
    headline(c, 'Some fostering happens', [('one weekend', ORANGE), ('at a time.', INK)], y=220)
    cards = [('One night', 'moon', (0.36, 0.09, 0.31, 1), WHITE), ('A weekend', None, (1, 1, 1, 1), PLUM),
             ('Part of a school holiday', 'sun', (1.0, 0.83, 0.73, 1), PLUM)]
    ys = [520, 700, 880]
    for (label, icon, fill, ink), y in zip(cards, ys):
        outline(c, 540, y, 940, 150, 34, (0.36, 0.09, 0.31, 0.25), 2, fill=fill)
        if icon:
            sp = load_png_sprite(sorted(__import__('glob').glob(f'{F.OF}/assets/{icon}/*.png'))[-1])
            draw(c, sp, 165, y, scale=120 / max(sp.shape[:2]))
        else:
            for k in range(3):
                draw(c, rrect(110 - k * 6, 26, 13, (0.93, 0.7, 0.35, 1)), 165, y + 26 - k * 22)
            draw(c, rrect(30, 14, 7, ORANGE), 165, y - 46)
        text(c, label, 260, y, N9, 54, ink)
    hand(c, 'same child, again and again', 600, 1010, 46, ORANGE, rot=-3)
    text(c, 'Some respite carers support the same child regularly,', 70, 1110, N8, 28, INK)
    text(c, 'so trust can grow.', 70, 1148, N8, 28, INK)
    signoff(c, 1225)
    pins = [(1, 40, 95), (2, 1040, 140), (3, 40, 230), (4, 40, 520), (5, 40, 700), (6, 40, 880), (7, 1040, 1010), (8, 40, 1110), (9, 40, 1225)]
    notes_txt = [
        'Logo, top left.',
        'Eyebrow pill: "Respite fostering".',
        'Headline: "Some fostering happens one weekend at a time."',
        'Card 1, plum: a 3D moon and "One night".',
        'Card 2, white: a 3D stack of pancakes and "A weekend".',
        'Card 3, peach: a 3D sun and "Part of a school holiday". The three cards are the website\'s own three lengths of stay.',
        'Handwritten orange note with an arrow: "same child, again and again".',
        'Line from the website: "Some respite carers support the same child regularly, so trust can grow."',
        'Sign-off: gradient button, phone, web address, Rated Good by Ofsted.',
    ]
    return c, pins, notes_txt, 'Option C · Three Ways to Stay', 'A clean graphic post: three cards with 3D icons for the three lengths of stay, plus a handwritten "same child, again and again".'


def board(fn, path):
    c, pins, notes, title, summary = fn()
    for n, x, y in pins:
        pin(c, n, x, y)
    full = np.ones((PH + 160, PW + NOTE_W + 120, 3), np.float32) * np.array(PAPER, np.float32)
    frame = rrect(PW + 16, PH + 16, 18, (0.75, 0.7, 0.72, 1))
    draw(full, frame, 60 + PW / 2, 120 + PH / 2)
    full[120:120 + PH, 60:60 + PW] = c
    text(full, title, 60, 62, N9, 50, PLUM)
    text(full, '1080 × 1350 · Instagram & Facebook feed · storyboard sketch', PW - 560, 66, 'Poppins-Medium', 22, (0.4, 0.33, 0.38, 1))
    x0 = PW + 110
    y = 150
    for line in F.wrap(summary, N8, 30, NOTE_W - 30):
        text(full, line, x0, y, N8, 30, PLUM)
        y += 42
    y += 30
    for i, note in enumerate(notes, 1):
        pin(full, i, x0 + 23, y + 12)
        for li, line in enumerate(F.wrap(note, N7, 24, NOTE_W - 90)):
            text(full, line, x0 + 64, y + 12 + li * 34, N7, 24, (0.25, 0.2, 0.25, 1))
        y += 34 * len(F.wrap(note, N7, 24, NOTE_W - 90)) + 26
    cv2.imwrite(path, F.to_u8(full), [cv2.IMWRITE_JPEG_QUALITY, 92])
    return F.to_u8(c)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    posts = []
    for key, fn in (('A', option_a), ('B', option_b), ('C', option_c)):
        posts.append(board(fn, f'{OUT}/option_{key}.jpg'))
        print('option', key, flush=True)
    th = [cv2.resize(p, (540, 675)) for p in posts]
    gap = np.ones((675, 30, 3), np.uint8) * 245
    row = np.hstack([th[0], gap, th[1], gap, th[2]])
    cv2.imwrite(f'{OUT}/overview.jpg', row, [cv2.IMWRITE_JPEG_QUALITY, 92])
