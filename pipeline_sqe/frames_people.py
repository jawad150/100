"""Scene images (one per voice beat) for IC London "What Is the SQE?" — people version.

Real people footage (Mixkit, free licence) with word-synced pop-ups: when the voice says a word, its object pops on screen
(3D props from Blender, chips, badges). Caption style taken from the client's reference: bold condensed captions at the
bottom with key words in brand red, a small STEP counter, and collage panels.

Usage: python3 frames_people.py  -> workspace_sqe/frames_people/beat_XX.png + storyboard
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import reel_sol as R
from reel_sol import (W, H, draw, blur_sprite, tint, rrect, ts, wspr, check, load_png_sprite, solid, paste_spr,
                      NAVY, RED, RED_L, WHITE_, ICE, INK, GREY, LINE, F9, F8, F7, F6, hexc, _wmask)

SQ = os.path.abspath(os.path.join(HERE, '..', 'workspace_sqe'))
SOL = os.path.abspath(os.path.join(HERE, '..', 'workspace_sol'))
OUT = f'{SQ}/frames_people'
CAP = 'Anton-400'


def clip_frame(cid, t_frac=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    cap = cv2.VideoCapture(f'{SQ}/clips/{cid}.mp4')
    n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * t_frac))
    ok, im = cap.read()
    im = im[..., ::-1].astype(np.float32) / 255.0
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    out = cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if sc > 1.6:                                       # gentle sharpen for upscaled 720p sources
        bl = cv2.GaussianBlur(out, (0, 0), 1.6)
        out = np.clip(out * 1.5 - bl * 0.5, 0, 1)
    return grade(out)


def grade(im):
    """Cinematic grade: slightly lifted contrast, cool navy shadows, warm highlights."""
    lum = im.mean(2, keepdims=True)
    im = np.clip((im - 0.5) * 1.08 + 0.5, 0, 1)
    shadow = np.clip(1 - lum * 2.2, 0, 1)
    im = im * (1 - 0.18 * shadow) + np.array([0.02, 0.06, 0.22], np.float32) * 0.18 * shadow
    return im


def prop(name):
    return load_png_sprite(f'{SQ}/assets/{name}.png')


def last(seq):
    return load_png_sprite(sorted(glob.glob(f'{SOL}/assets/{seq}/*.png'))[-1])


def pop(c, spr, x, y, sc=1.0, rays=True):
    """A popped-in object: soft shadow, white glow ring and little burst rays."""
    if rays:
        lay = np.zeros((H, W), np.uint8)
        r0 = max(spr.shape[:2]) * sc * 0.42
        for j in range(10):
            a = j / 10 * 2 * math.pi + 0.2
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((y + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + 36)) * 4), int((y + math.sin(a) * (r0 + 36)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.85
        c[:] = c * (1 - m) + np.array(WHITE_[:3], np.float32) * m
    draw(c, blur_sprite(tint(spr, (0.0, 0.02, 0.1)), 22), x + 12, y + 30, scale=sc, opacity=0.5)
    draw(c, spr, x, y, scale=sc)


def chip(c, text, x, y, fill=RED, ink=WHITE_, size=40, rot=0, font=F9):
    s = ts(text, font, size, ink, 0.04)
    p = rrect(s.shape[1] + 56, s.shape[0] + 34, (s.shape[0] + 34) / 2, fill)
    draw(c, blur_sprite(tint(p, (0, 0, 0.1)), 12), x + 6, y + 12, rot=rot, opacity=0.5)
    draw(c, p, x, y, rot=rot)
    draw(c, s, x, y, rot=rot)


def bottom_shade(c, top=0.55):
    g = np.clip((R._Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.2
    return c * (1 - 0.82 * g) + np.array(hexc('#041640')[:3], np.float32) * 0.82 * g


def top_shade(c, h=0.22):
    g = np.clip(1 - R._Y / (H * h), 0, 1)[..., None] ** 1.5
    return c * (1 - 0.6 * g)


def caption(c, lines, y=1600, size=104):
    """Bold condensed caption, key words in brand red (lines = [[(word, red?), ...], ...])."""
    for li, line in enumerate(lines):
        sprs = [solid(_wmask(w, CAP, size), RED_L if red else WHITE_) for w, red in line]
        sp = size * 0.2
        total = sum(s.shape[1] for s in sprs) + sp * (len(sprs) - 1)
        x = 80
        yy = y + li * size * 1.08
        for s in sprs:
            draw(c, blur_sprite(tint(s, (0, 0, 0)), 10), x + s.shape[1] / 2 + 4, yy + 6, opacity=0.5)
            draw(c, s, x + s.shape[1] / 2, yy)
            x += s.shape[1] + sp


def step(c, n, y=1480, label=None):
    """Signal-bar STEP counter (reference style)."""
    for j in range(6):
        hgt = 10 + j * 6
        col = RED if j < n + 1 else (1, 1, 1, 0.35)
        draw(c, rrect(9, hgt, 2, col), 92 + j * 15, y - hgt / 2 + 18)
    s = ts(label or ('STEP 0%d' % n), F8, 26, WHITE_, 0.18)
    draw(c, s, 200 + s.shape[1] / 2, y + 8)


def logo_badge(c):
    lg = load_png_sprite(f'{SQ}/src/logo_full.png')
    sc = 0.32
    w, h = lg.shape[1] * sc + 40, lg.shape[0] * sc + 26
    draw(c, rrect(w, h, 20, (1, 1, 1, 0.95)), 70 + w / 2, 105)
    draw(c, lg, 70 + w / 2, 105, scale=sc)


def side_label(c, text, x=1040, y=900):
    s = ts(text, F8, 24, (1, 1, 1, 0.8), 0.3)
    s = np.rot90(s, 1).copy()
    draw(c, s, x, y)


def panel(c, cid, x, y, w, h, t_frac=0.45, fx=0.5, fy=0.5):
    im = clip_frame(cid, t_frac, fx, fy, 1.0, w, h)
    spr = np.concatenate([im, np.ones((h, w, 1), np.float32)], 2)
    m = solid(R.sdf_fill(R.rrect_alpha(w, h, 26, 2)), WHITE_)[..., 3:4]
    mm = cv2.resize(m, (w, h))[..., None] if m.shape[:2] != (h, w) else m
    spr = spr * mm
    draw(c, blur_sprite(tint(spr, (0, 0, 0.1)), 16), x + 8, y + 18, opacity=0.45)
    draw(c, spr, x, y)


def ice_bg():
    c = np.ones((H, W, 3), np.float32) * np.array(ICE[:3], np.float32)
    return c - R.grid_layer()[:H, :W][..., None] * 0.12


# ------------------------------------------------------------------ beats
def b01():   # "Confused about the SQE?"
    c = clip_frame(28321, 0.35, fx=0.42, fy=0.5)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    for txt, x, y, rot, col in [('SQE1', 200, 520, -10, RED), ('FLK', 860, 470, 8, NAVY), ('QWE', 900, 820, -6, RED),
                                ('SRA', 170, 860, 7, NAVY), ('MCQ', 760, 1080, 5, NAVY), ('SQE2', 260, 1160, -6, RED)]:
        chip(c, txt, x, y, fill=col, rot=rot)
    pop(c, last('qmark'), 560, 380, 0.62)
    caption(c, [[('CONFUSED', False), ('ABOUT', False)], [('THE', False), ('SQE?', True)]], y=1560)
    return c


def b02():   # "Let's simplify it."
    c = clip_frame(28321, 0.7, fx=0.42, fy=0.5)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (90, 1300), (990, 1300), 255, 12, cv2.LINE_AA)
    m = lay.astype(np.float32) / 255
    c = c + cv2.GaussianBlur(m, (0, 0), 14)[..., None] * np.array(LINE[:3], np.float32) * 0.9
    c = c * (1 - m[..., None]) + np.array(WHITE_[:3], np.float32) * m[..., None]
    for j, txt in enumerate(['SQE1', 'SQE2', 'QWE', 'SRA']):
        chip(c, txt, 190 + j * 235, 1300, fill=RED if j < 2 else NAVY, size=36)
    pop(c, R.check(150), 900, 1110, 1.0)
    caption(c, [[("LET'S", False), ('SIMPLIFY', True), ('IT.', False)]], y=1600)
    return c


def b03():   # "The SQE is the Solicitors Qualifying Examination ... in England and Wales"
    c = clip_frame(33823, 0.5, fx=0.72, fy=0.45)
    c = bottom_shade(top_shade(c), 0.5)
    logo_badge(c)
    pop(c, prop('letters'), 540, 820, 0.9)
    pop(c, load_png_sprite(sorted(glob.glob(f'{SOL}/assets/ic_pin/*.png'))[18]), 900, 1180, 0.6)
    chip(c, 'ENGLAND & WALES', 660, 1330, fill=NAVY, size=34)
    caption(c, [[('SOLICITORS', True)], [('QUALIFYING', True)], [('EXAMINATION.', False)]], y=1470, size=96)
    side_label(c, 'THE SOLICITOR ROUTE')
    return c


def b04():   # "Step one: SQE1. It tests your legal knowledge,"
    c = clip_frame(9011, 0.5, fx=0.38, fy=0.45)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    chip(c, 'SQE1', 820, 360, fill=RED, size=72)
    pop(c, last('bulb'), 230, 640, 0.5)
    chip(c, 'LEGAL KNOWLEDGE', 330, 900, fill=(1, 1, 1, 1), ink=INK, size=36)
    step(c, 1)
    caption(c, [[('IT', False), ('TESTS', False), ('YOUR', False)], [('LEGAL', True), ('KNOWLEDGE.', True)]], y=1580)
    side_label(c, 'FUNCTIONING LEGAL KNOWLEDGE')
    return c


def b05():   # "...across two multiple-choice exams."
    c = clip_frame(50126, 0.55, fx=0.42, fy=0.5)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    pop(c, prop('papers'), 540, 820, 0.95)
    for j, l in enumerate('ABCDE'):
        x = 230 + j * 155
        col = RED if l == 'C' else (1, 1, 1, 1)
        draw(c, rrect(96, 96, 48, col), x, 1250)
        draw(c, ts(l, F9, 44, WHITE_ if l == 'C' else NAVY), x, 1250)
    step(c, 1)
    caption(c, [[('TWO', True), ('MULTIPLE-CHOICE', False)], [('EXAMS.', False)]], y=1580)
    return c


def b06():   # "Step two: SQE2. It tests practical skills, like client interviews, advocacy, research and drafting."
    c = np.ones((H, W, 3), np.float32) * np.array(hexc('#071233')[:3], np.float32)
    logo_badge(c)
    chip(c, 'SQE2', 860, 105, fill=RED, size=60)
    pw, ph_ = 470, 560
    spots = [(15858, 290, 560, 'speech', 'CLIENT INTERVIEWS', 0.4, 0.5), (22961, 790, 560, 'lectern', 'ADVOCACY', 0.45, 0.5),
             (50722, 290, 1170, 'magnifier', 'RESEARCH', 0.3, 0.5), (17049, 790, 1170, 'pen', 'DRAFTING', 0.55, 0.5)]
    for cid, x, y, icon_, lab, fx, fy in spots:
        panel(c, cid, x, y, pw, ph_, 0.5, fx, fy)
        bx_, by_ = x + pw / 2 - 70, y - ph_ / 2 + 70
        draw(c, blur_sprite(tint(rrect(124, 124, 62, WHITE_), (0, 0, 0.1)), 10), bx_ + 4, by_ + 8, opacity=0.5)
        draw(c, rrect(124, 124, 62, WHITE_), bx_, by_)
        draw(c, prop(icon_), bx_, by_, scale=0.2)
        s = solid(_wmask(lab, CAP, 50), WHITE_)
        draw(c, rrect(s.shape[1] + 40, 74, 12, RED), x - pw / 2 + 30 + (s.shape[1] + 40) / 2, y + ph_ / 2 - 60)
        draw(c, s, x - pw / 2 + 30 + (s.shape[1] + 40) / 2, y + ph_ / 2 - 60)
    step(c, 2, y=1555)
    caption(c, [[('PRACTICAL', True), ('LEGAL', False), ('SKILLS.', False)]], y=1660, size=96)
    s = ts('Oral + written assessments', F7, 30, (1, 1, 1, 0.8))
    draw(c, s, 80 + s.shape[1] / 2, 1770)
    return c


def b07():   # "Pass SQE1 first. Then, with a degree,"
    c = clip_frame(48165, 0.5, fx=0.62, fy=0.5)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    chip(c, 'SQE1  ✓', 300, 420, fill=RED, size=52) if False else chip(c, 'PASS SQE1 FIRST', 360, 420, fill=RED, size=44)
    pop(c, last('cap'), 760, 820, 0.62)
    chip(c, 'DEGREE  ·  ANY SUBJECT', 560, 1080, fill=(1, 1, 1, 1), ink=INK, size=34)
    step(c, 3, label='HOW IT FITS')
    caption(c, [[('THEN,', False), ('WITH', False), ('A', False)], [('DEGREE,', True)]], y=1580)
    return c


def b08():   # "two years' qualifying work experience"
    c = clip_frame(8873, 0.5, fx=0.66, fy=0.45)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    pop(c, prop('calendar'), 330, 720, 0.75)
    chip(c, 'QWE', 330, 1010, fill=NAVY, size=44)
    step(c, 4, label='HOW IT FITS')
    caption(c, [[("TWO", True), ("YEARS'", True), ('QUALIFYING', False)], [('WORK', False), ('EXPERIENCE,', False)]], y=1580)
    return c


def b09():   # "and the SRA's character checks, you can qualify."
    c = clip_frame(16107, 0.5, fx=0.62, fy=0.45)
    c = bottom_shade(top_shade(c))
    logo_badge(c)
    pop(c, last('ic_shield'), 300, 640, 0.75)
    chip(c, 'CHARACTER & SUITABILITY', 470, 900, fill=(1, 1, 1, 1), ink=INK, size=32)
    s = ts('QUALIFIED SOLICITOR', F9, 46, WHITE_, 0.06)
    p = rrect(s.shape[1] + 130, 104, 52, RED).copy()
    paste_spr(p, R.check(70), 56, 52)
    paste_spr(p, s, 100 + s.shape[1] / 2, 52)
    pop(c, p, 540, 1260, 1.0)
    step(c, 5, label='HOW IT FITS')
    caption(c, [[('YOU', False), ('CAN', False), ('QUALIFY.', True)]], y=1600)
    return c


def b10():   # "Find out more about SQE preparation at IC London."
    c = clip_frame(4457, 0.6, fx=0.42, fy=0.45)
    c = top_shade(c, 0.3)
    g = np.clip((R._Y / H - 0.42) / 0.2, 0, 1)[..., None]
    c = c * (1 - g) + ice_bg() * g
    lg = load_png_sprite(f'{SQ}/src/logo_full.png')
    pop(c, lg, 540, 1060, 1.0, rays=False)
    R.line_text = None
    for li, (words, size, col) in enumerate([(['Find', 'out', 'more', 'about'], 64, INK), (['SQE', 'preparation'], 88, RED)]):
        sprs = [wspr(w, F9, size, col) for w in words]
        total = sum(s.shape[1] for s in sprs) + size * 0.13 * (len(sprs) - 1)
        x = 540 - total / 2
        y = 1360 + li * 100
        for s in sprs:
            draw(c, s, x + s.shape[1] / 2, y)
            x += s.shape[1] + size * 0.13
    s = ts('iclondon.co.uk', F7, 46, NAVY)
    draw(c, s, 510, 1610)
    bx = 510 + s.shape[1] / 2 + 64
    draw(c, rrect(80, 80, 40, RED), bx, 1610)
    draw(c, R.arrow_spr(), bx, 1610)
    s2 = ts('100% ONLINE  ·  STUDY AT YOUR OWN PACE', F8, 26, GREY, 0.14)
    draw(c, s2, 540, 1710)
    pop(c, last('cap'), 880, 760, 0.45, rays=False)
    return c


BEATS = [b01, b02, b03, b04, b05, b06, b07, b08, b09, b10]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    thumbs = []
    for j, fn in enumerate(BEATS, start=1):
        im = to_u8(R.post(fn(), j, bloom=0.1, grain=0.012, vig=0.35 if j < 10 else 0.0))
        cv2.imwrite(f'{OUT}/beat_{j:02d}.png', im)
        thumbs.append(cv2.resize(im, (324, 576)))
        print('beat', j, flush=True)
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(thumbs[:5]), np.hstack(thumbs[5:])]), [cv2.IMWRITE_JPEG_QUALITY, 90])
