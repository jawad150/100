"""Story version: scene images for IC London "What Is the SQE?" (one image per voice beat).

Story: London wakes up and goes to work — into courtrooms (law), boardrooms (HR) and trading floors (finance), the three
worlds IC London teaches. We then follow one aspiring solicitor: confused by the SQE, it gets simplified step by step,
and the story ends back at the court, qualified. Every spoken key word pops its object on screen.

Own visual language (not the reference's): documentary lower-thirds with a red brand bar, key words underlined with a
red marker swipe, emblem-shaped pillar badges (LAW / HR / FINANCE), 3D props popping in with a white ring.

Usage: python3 frames_story.py -> workspace_sqe/frames_story/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_people as P
from frames_people import (clip_frame, prop, last, pop, chip, bottom_shade, top_shade, logo_badge, panel, ice_bg, W, H, R,
                           draw, blur_sprite, tint, rrect, ts, wspr, solid, paste_spr, _wmask, load_png_sprite,
                           NAVY, RED, RED_L, WHITE_, INK, GREY, LINE, F9, F8, F7, F6, hexc, SOL, SQ)

OUT = f'{SQ}/frames_story'


def caption(c, lines, y=1560, size=86):
    """Lower-third caption: red brand bar on the left, Inter Black, key words underlined with a red marker swipe."""
    n = len(lines)
    draw(c, rrect(12, size * 1.15 * n + 10, 6, RED), 70, y + (n - 1) * size * 0.575)
    for li, line in enumerate(lines):
        x = 108
        yy = y + li * size * 1.15
        for w, key in line:
            s = wspr(w, F9, size, WHITE_)
            if key:
                lay = np.zeros((H, W), np.uint8)
                pts = [(x + 4 + (s.shape[1] - 8) * u, yy + size * 0.42 + 5 * math.sin(u * 6)) for u in np.linspace(0, 1, 30)]
                cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, int(size * 0.16) * 4, cv2.LINE_AA, shift=2)
                m = lay.astype(np.float32)[..., None] / 255
                c[:] = c * (1 - m) + np.array(RED[:3], np.float32) * m
            draw(c, blur_sprite(tint(s, (0, 0, 0)), 10), x + s.shape[1] / 2 + 3, yy + 6, opacity=0.45)
            draw(c, s, x + s.shape[1] / 2, yy)
            x += s.shape[1] + size * 0.16


def doc_tag(c, text, x=80, y=300):
    """Documentary location/time tag."""
    s = ts(text, F8, 30, WHITE_, 0.2)
    w = s.shape[1] + 60
    draw(c, rrect(w, 64, 8, (0.02, 0.06, 0.2, 0.75)), x + w / 2, y)
    draw(c, rrect(8, 64, 4, RED), x + 4, y)
    draw(c, s, x + 30 + s.shape[1] / 2, y)


def pillar(c, label, x, y, active=True):
    """Emblem-shaped pillar badge: navy spire + red block with white circle + label."""
    m = np.zeros((220, 160), np.uint8)
    cv2.fillPoly(m, [np.array([[80, 6], [150, 70], [10, 70]], np.int32)], 255, cv2.LINE_AA)
    navy = solid(m.astype(np.float32) / 255, NAVY if active else (0.6, 0.65, 0.8, 1))
    b = np.zeros((220, 160), np.uint8)
    cv2.rectangle(b, (10, 80), (150, 200), 255, -1)
    cv2.circle(b, (80, 140), 36, 0, -1, cv2.LINE_AA)
    blk = solid(b.astype(np.float32) / 255, RED if active else (0.75, 0.75, 0.8, 1))
    em = R.over_spr(navy, blk)
    card = rrect(400, 130, 30, (1, 1, 1, 0.96)).copy()
    paste_spr(card, cv2.resize(em, (64, 88), interpolation=cv2.INTER_AREA), 60, 65)
    s = ts(label, F9, 54, NAVY, 0.04)
    paste_spr(card, s, 110 + s.shape[1] / 2, 65)
    w = 130 + s.shape[1]
    card = card[:, :int(w)]
    pop(c, card, x, y, 1.0)


def chart_spr():
    m = np.zeros((360, 420), np.uint8)
    for j, hgt in enumerate((90, 150, 210, 290)):
        cv2.rectangle(m, (40 + j * 90, 330 - hgt), (100 + j * 90, 330), 255, -1)
    lay = np.zeros((360, 420), np.uint8)
    cv2.polylines(lay, [np.array([[30, 250], [140, 190], [230, 210], [380, 60]], np.int32)], False, 255, 18, cv2.LINE_AA)
    cv2.fillPoly(lay, [np.array([[395, 40], [350, 60], [385, 95]], np.int32)], 255, cv2.LINE_AA)
    bars = solid(m.astype(np.float32) / 255, NAVY)
    line = solid(lay.astype(np.float32) / 255, RED)
    card = rrect(460, 400, 40, (1, 1, 1, 0.97)).copy()
    paste_spr(card, R.over_spr(bars, line), 230, 200)
    return card


# ------------------------------------------------------------------ the story, beat by beat
def s01():   # "Every morning, London goes to work."
    c = clip_frame(4169, 0.4, fx=0.55, fy=0.45)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    doc_tag(c, 'LONDON  ·  08:00', y=290)
    caption(c, [[('Every', False), ('morning,', False)], [('London', True), ('goes', False), ('to', False)], [('work.', False)]], y=1440)
    return c


def s02():   # "Into courtrooms,"
    c = clip_frame(12315, 0.5, fx=0.45, fy=0.4)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    pillar(c, 'LAW', 760, 520)
    pop(c, load_png_sprite(sorted(glob.glob(f'{SOL}/assets/ic_scales/*.png'))[18]), 760, 900, 0.75)
    caption(c, [[('Into', False), ('courtrooms,', True)]], y=1640)
    return c


def s03():   # "boardrooms"
    c = clip_frame(5520, 0.5, fx=0.3, fy=0.45)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    pillar(c, 'HR', 760, 1040)
    pop(c, load_png_sprite(sorted(glob.glob(f'{SOL}/assets/ic_briefcase/*.png'))[18]), 820, 1300, 0.6)
    caption(c, [[('boardrooms', True)]], y=1660)
    return c


def s04():   # "and trading floors."
    c = clip_frame(9607, 0.5, fx=0.5, fy=0.5)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    pillar(c, 'FINANCE', 640, 520)
    pop(c, chart_spr(), 600, 920, 0.95)
    caption(c, [[('and', False), ('trading', True), ('floors.', True)]], y=1640)
    return c


def s05():   # "Thinking of law?"
    c = clip_frame(15923, 0.5, fx=0.5, fy=0.4)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    pop(c, last('qmark'), 820, 520, 0.6)
    pillar(c, 'LAW', 280, 560)
    caption(c, [[('Thinking', False), ('of', False), ('law?', True)]], y=1640)
    return c


def s06():   # "Confused about the SQE? Let's simplify it."
    c = clip_frame(28321, 0.35, fx=0.42, fy=0.5)
    c = bottom_shade(top_shade(c), 0.5)
    logo_badge(c)
    for txt, x, y, rot, col in [('SQE1', 200, 520, -10, RED), ('FLK', 860, 470, 8, NAVY), ('QWE', 900, 820, -6, RED),
                                ('SRA', 170, 860, 7, NAVY), ('MCQ', 760, 1080, 5, NAVY), ('SQE2', 260, 1160, -6, RED)]:
        chip(c, txt, x, y, fill=col, rot=rot)
    caption(c, [[('Confused', False), ('about', False)], [('the', False), ('SQE?', True)], [("Let's", False), ('simplify', True), ('it.', False)]],
            y=1390, size=80)
    return c


def s07():   # "SQE1 tests your legal knowledge, across two multiple-choice exams."
    c = clip_frame(9011, 0.5, fx=0.38, fy=0.45)
    c = bottom_shade(top_shade(c), 0.5)
    logo_badge(c)
    chip(c, 'SQE1', 860, 300, fill=RED, size=70)
    pop(c, prop('papers'), 780, 1180, 0.62)
    chip(c, 'LEGAL KNOWLEDGE', 780, 900, fill=(1, 1, 1, 1), ink=INK, size=34)
    caption(c, [[('SQE1', True), ('tests', False), ('your', False)], [('legal', True), ('knowledge.', True)]], y=1550)
    return c


def s08():   # "SQE2 tests practical skills: client interviews, advocacy, research and drafting."
    c = np.ones((H, W, 3), np.float32) * np.array(hexc('#071233')[:3], np.float32)
    c = c + R.grid_layer()[:H, :W][..., None] * 0.35 * np.array(LINE[:3], np.float32)
    logo_badge(c)
    chip(c, 'SQE2', 880, 105, fill=RED, size=60)
    pw, ph_ = 470, 540
    spots = [(15858, 290, 520, 'speech', 'Client interviews', 0.4), (22961, 790, 520, 'lectern', 'Advocacy', 0.45),
             (50722, 290, 1110, 'magnifier', 'Research', 0.3), (17049, 790, 1110, 'pen', 'Drafting', 0.55)]
    for cid, x, y, icon_, lab, fx in spots:
        panel(c, cid, x, y, pw, ph_, 0.5, fx, 0.5)
        bx_, by_ = x + pw / 2 - 70, y - ph_ / 2 + 70
        draw(c, rrect(124, 124, 62, WHITE_), bx_, by_)
        draw(c, prop(icon_), bx_, by_, scale=0.2)
        s = ts(lab, F8, 34, INK)
        draw(c, rrect(s.shape[1] + 44, 64, 32, (1, 1, 1, 1)), x - pw / 2 + 30 + (s.shape[1] + 44) / 2, y + ph_ / 2 - 54)
        draw(c, s, x - pw / 2 + 30 + (s.shape[1] + 44) / 2, y + ph_ / 2 - 54)
    caption(c, [[('SQE2', True), ('tests', False), ('practical', True)], [('legal', False), ('skills.', False)]], y=1560, size=80)
    return c


def s09():   # "Add a degree,"
    c = clip_frame(12820, 0.5, fx=0.5, fy=0.4)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    pop(c, last('cap'), 780, 560, 0.6)
    chip(c, 'DEGREE  ·  ANY SUBJECT', 740, 820, fill=(1, 1, 1, 1), ink=INK, size=32)
    caption(c, [[('Add', False), ('a', False), ('degree,', True)]], y=1640)
    return c


def s10():   # "two years' qualifying work experience"
    c = clip_frame(8873, 0.5, fx=0.66, fy=0.45)
    c = bottom_shade(top_shade(c), 0.55)
    logo_badge(c)
    pop(c, prop('calendar'), 300, 700, 0.72)
    chip(c, 'QWE', 300, 990, fill=NAVY, size=44)
    caption(c, [[("two", True), ("years'", True), ('work', False)], [('experience,', False)]], y=1560)
    return c


def s11():   # "and the SRA's character checks, and you can qualify."
    c = clip_frame(16107, 0.5, fx=0.62, fy=0.45)
    c = bottom_shade(top_shade(c), 0.5)
    logo_badge(c)
    pop(c, last('ic_shield'), 300, 600, 0.72)
    chip(c, 'CHARACTER & SUITABILITY', 470, 860, fill=(1, 1, 1, 1), ink=INK, size=30)
    s = ts('QUALIFIED SOLICITOR', F9, 46, WHITE_, 0.06)
    p = rrect(s.shape[1] + 130, 104, 52, RED).copy()
    paste_spr(p, R.check(70), 56, 52)
    paste_spr(p, s, 100 + s.shape[1] / 2, 52)
    pop(c, p, 540, 1200, 1.0)
    caption(c, [[('and', False), ('you', False), ('can', False), ('qualify.', True)]], y=1640)
    return c


def s12():   # "Find out more about SQE preparation at IC London."
    c = clip_frame(4457, 0.6, fx=0.42, fy=0.45)
    c = top_shade(c, 0.3)
    g = np.clip((R._Y / H - 0.4) / 0.18, 0, 1)[..., None]
    c = c * (1 - g) + ice_bg() * g
    lg = load_png_sprite(f'{SQ}/src/logo_full.png')
    pop(c, lg, 540, 1000, 1.0, rays=False)
    for j, lab in enumerate(['LAW', 'HR', 'FINANCE']):
        x = [300, 540, 790][j]
        s = ts(lab, F9, 34, WHITE_, 0.08)
        draw(c, rrect(s.shape[1] + 50, 70, 35, NAVY if j else RED), x, 1270)
        draw(c, s, x, 1270)
    for li, (words, size, col) in enumerate([(['Find', 'out', 'more', 'about'], 62, INK), (['SQE', 'preparation'], 86, RED)]):
        sprs = [wspr(w, F9, size, col) for w in words]
        total = sum(s.shape[1] for s in sprs) + size * 0.13 * (len(sprs) - 1)
        x = 540 - total / 2
        y = 1420 + li * 100
        for s in sprs:
            draw(c, s, x + s.shape[1] / 2, y)
            x += s.shape[1] + size * 0.13
    s = ts('iclondon.co.uk', F7, 46, NAVY)
    draw(c, s, 510, 1660)
    bx = 510 + s.shape[1] / 2 + 64
    draw(c, rrect(80, 80, 40, RED), bx, 1660)
    draw(c, R.arrow_spr(), bx, 1660)
    pop(c, last('cap'), 880, 720, 0.45, rays=False)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    thumbs = []
    for j, fn in enumerate(SCENES, start=1):
        im = P.to_u8(R.post(fn(), j, bloom=0.1, grain=0.012, vig=0.35 if j < 12 else 0.0))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        thumbs.append(cv2.resize(im, (270, 480)))
        print('scene', j, flush=True)
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(thumbs[:6]), np.hstack(thumbs[6:])]), [cv2.IMWRITE_JPEG_QUALITY, 90])
