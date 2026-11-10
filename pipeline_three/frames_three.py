"""Scene images for Organic Fostering "Three of Me" (the PDF: one presenter, three characters, one objection).

Story: 5:30 pm, commuters stream home. One woman, three versions of her: THE WORRIER (grey top, mug, cool light),
THE OPTIMIST (pink top, sunshine) and THE REALIST (white blazer, clipboard). They argue it out in jump cuts; every factor
the voice names slaps onto the screen as a glossy 3D sticker with a white die-cut border. Split screen of all three for
"You ask." End card: Ask us about fostering around your work · Start your enquiry · 0161 241 1332.

Footage: one Mixkit actor (same person, same set) in two outfits; the Worrier lives in a cool, near-monochrome grade.

Usage: python3 frames_three.py [n ...] -> workspace_three/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import reel_sol as R
from reel_sol import W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, hexc, _wmask

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_three'
OUT = f'{S}/frames'
_X, _Y = R._X, R._Y

PURPLE, ORANGE, PLUM = hexc('#B7006E'), hexc('#FF6411'), hexc('#5B174F')
IVORY, LAV, PEACH, LEAF = hexc('#FCF8F5'), hexc('#F6EAF3'), hexc('#FFD4BA'), hexc('#64A60B')
SLATE, SUN = hexc('#5C6B7A'), hexc('#FFB020')
WHITE = (1.0, 1.0, 1.0, 1.0)
N9, N8, N7 = 'Nunito-900', 'Nunito-800', 'Nunito-700'
CHAR = {'worrier': ('THE WORRIER', SLATE, 'mug'), 'optimist': ('THE OPTIMIST', ORANGE, 'sun'),
        'realist': ('THE REALIST', PURPLE, 'clipboard')}


# ------------------------------------------------------------------ footage
def frame_of(cid, t):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def cover(im, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    return cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def grade(im, kind):
    """Each character has her own light: cool and flat (worrier), warm and bright (optimist), clean and neutral (realist)."""
    lum = im.mean(2, keepdims=True)
    if kind == 'worrier':
        im = im * 0.18 + lum * 0.82                              # nearly monochrome, cool and a little dim
        im = np.clip((im - 0.5) * 1.12 + 0.47, 0, 1) * np.array([0.9, 0.97, 1.1], np.float32)
    elif kind == 'optimist':
        im = np.clip((im - 0.5) * 1.06 + 0.53, 0, 1) * np.array([1.06, 1.0, 0.92], np.float32)
    elif kind == 'realist':
        im = np.clip((im - 0.5) * 1.08 + 0.5, 0, 1) * np.array([1.0, 0.99, 1.0], np.float32)
    else:
        im = np.clip((im - 0.5) * 1.05 + 0.5, 0, 1)
    return np.clip(im, 0, 1).astype(np.float32)


def recolour_top(im, box, col=(0.30, 0.32, 0.37)):
    """Turn the white blazer into a soft grey top inside `box` (x0, y0, x1, y1 as fractions of the frame)."""
    h, w = im.shape[:2]
    hsv = cv2.cvtColor((np.clip(im, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    sat, val = hsv[..., 1] / 255, hsv[..., 2] / 255
    m = np.clip((0.24 - sat) / 0.08, 0, 1) * np.clip((val - 0.42) / 0.1, 0, 1)
    reg = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)
    reg[y0:y1, x0:x1] = 1
    reg = cv2.GaussianBlur(reg, (0, 0), 12)
    m = cv2.GaussianBlur(m * reg, (0, 0), 1.5)[..., None]
    shade = (val[..., None] - 0.42) / 0.58                     # keep the folds
    grey = np.array(col, np.float32) * (0.75 + 0.5 * shade)
    return im * (1 - m) + np.clip(grey, 0, 1) * m


def char_frame(kind, cid, t, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    im = frame_of(cid, t)
    return grade(cover(im, fx, fy, z, w, h), kind)


# ------------------------------------------------------------------ stickers (3D objects with a white die-cut border)
_TOK = {}


def token(name):
    if name not in _TOK:
        sp = load_png_sprite(f'{S}/assets/{name}.png')
        a = sp[..., 3]
        ys, xs = np.where(a > 0.01)
        _TOK[name] = np.ascontiguousarray(sp[max(0, ys.min() - 6):ys.max() + 7, max(0, xs.min() - 6):xs.max() + 7])
    return _TOK[name]


_STK = {}


def sticker(name, size):
    """3D object -> sticker: thick white die-cut outline, a hairline grey edge, ready to slap on screen."""
    key = (name, int(size))
    if key in _STK:
        return _STK[key]
    sp = token(name)
    sc = size / max(sp.shape[:2])
    sp = cv2.resize(sp, (max(2, int(sp.shape[1] * sc)), max(2, int(sp.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    pad = int(size * 0.09) + 6
    sp = cv2.copyMakeBorder(sp, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    a = (sp[..., 3] > 0.3).astype(np.uint8)
    r = int(size * 0.055) + 3
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    border = cv2.GaussianBlur(cv2.dilate(a, k).astype(np.float32), (0, 0), 1.2)
    edge = np.clip(cv2.GaussianBlur(cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 5, 2 * r + 5))).astype(np.float32), (0, 0), 1.2) - border, 0, 1)
    base = np.zeros_like(sp)
    base[..., :3] = border[..., None] * 1.0 + edge[..., None] * 0.72
    base[..., 3] = np.clip(border + edge, 0, 1)
    out = sp + base * (1 - sp[..., 3:4])
    _STK[key] = out.astype(np.float32)
    return _STK[key]


def slap(c, name, x, y, size, rot=-6, k=1.0, shadow=0.45):
    st = sticker(name, size)
    draw(c, blur_sprite(tint(st, (0.15, 0.05, 0.12)), 14), x + 10, y + 16, rot=rot, opacity=shadow * k)
    draw(c, st, x, y, rot=rot, opacity=k)


def word_sticker(c, text, x, y, fill=ORANGE, ink=WHITE, size=86, rot=-4):
    """Big type sticker (white die-cut border)."""
    s = ts(text, N9, size, ink, 0.01)
    p = rrect(s.shape[1] + 70, s.shape[0] + 40, 30, fill).copy()
    paste_spr(p, s, p.shape[1] / 2, p.shape[0] / 2)
    b = rrect(p.shape[1] + 26, p.shape[0] + 26, 42, WHITE)
    draw(c, blur_sprite(tint(b, (0.15, 0.05, 0.12)), 14), x + 10, y + 16, rot=rot, opacity=0.45)
    draw(c, b, x, y, rot=rot)
    draw(c, p, x, y, rot=rot)


def name_tag(c, kind, x=70, y=330, k=1.0):
    label, col, _ = CHAR[kind]
    s = ts(label, N9, 40, WHITE, 0.08)
    p = rrect(s.shape[1] + 60, 74, 37, col).copy()
    paste_spr(p, s, p.shape[1] / 2, 37)
    draw(c, blur_sprite(tint(p, (0.1, 0.03, 0.08)), 12), x + p.shape[1] / 2 + 6, y + 10, opacity=0.4 * k)
    draw(c, p, x + p.shape[1] / 2, y, opacity=k)


def caption(c, words, keys=(), y=1450, size=66, col=WHITE, hl=ORANGE):
    """Nunito Black captions (the PDF's caption style); key words on a colour highlight. Auto-fits, two lines max."""
    lines = [words] if isinstance(words, str) else words
    while size > 40:
        wmax = max(sum(_wmask(w, N9, size).shape[1] for w in l.split()) + size * 0.24 * (len(l.split()) - 1) for l in lines)
        if wmax <= W - 140:
            break
        size -= 2
    for li, l in enumerate(lines):
        ws = l.split()
        ms = [_wmask(w, N9, size) for w in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ms) - 1)
        x = W / 2 - tw / 2
        yy = y + li * size * 1.22
        for w, m in zip(ws, ms):
            cx = x + m.shape[1] / 2
            if w.strip('.,?!…').lower() in keys:
                draw(c, rrect(m.shape[1] + 20, size * 1.12, 18, hl), cx, yy + 3)
            else:
                draw(c, blur_sprite(solid(m, (0.1, 0.02, 0.08, 1)), 10), cx + 3, yy + 7, opacity=0.6)
            draw(c, solid(m, col), cx, yy)
            x += m.shape[1] + size * 0.24


def shade(c, top=0.62, amt=0.75, col=PLUM):
    g = np.clip((_Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    return c * (1 - amt * g) + np.array(col[:3], np.float32) * amt * g


def top_shade(c, h=0.22, amt=0.45):
    g = np.clip(1 - _Y / (H * h), 0, 1)[..., None] ** 1.5
    return c * (1 - amt * g)


def logo():
    lg = load_png_sprite(f'{S}/web/logo.png')
    a = lg[..., 3]
    ys, xs = np.where(a > 0.02)
    return np.ascontiguousarray(lg[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def logo_small(c, x=920, y=170, w=240, k=1.0):
    lg = logo()
    b = rrect(w + 30, int(lg.shape[0] * w / lg.shape[1]) + 24, 20, (1, 1, 1, 0.92))
    draw(c, b, x, y, opacity=k)
    draw(c, lg, x, y, scale=w / lg.shape[1], opacity=k)


def canvas():
    k = (_Y / H)[..., None]
    c = np.array(IVORY[:3], np.float32) * (1 - k) + np.array(LAV[:3], np.float32) * k
    for x, y, r, col, a in ((180, 380, 520, PURPLE, 0.16), (930, 1500, 600, ORANGE, 0.14)):
        g = np.exp(-((_X - x) ** 2 + (_Y - y) ** 2) / (2 * r * r))[..., None] * a
        c = c * (1 - g) + np.array(col[:3], np.float32) * g
    return c.astype(np.float32)


def grad_spr(w, h, r, a0=PURPLE, a1=ORANGE, phase=0.0):
    m = R.sdf_fill(R.rrect_alpha(int(w), int(h), r, 2))
    hh, ww = m.shape
    u = (np.arange(ww, dtype=np.float32)[None, :] / ww + phase) % 1.0
    u = 0.5 - 0.5 * np.cos(u * 2 * math.pi)
    col = np.array(a0[:3], np.float32) * (1 - u[..., None]) + np.array(a1[:3], np.float32) * u[..., None]
    col = np.broadcast_to(col, (hh, ww, 3))
    return np.concatenate([col * m[..., None], m[..., None]], 2).astype(np.float32)


def clock_tag(c, text='5:30 PM', x=70, y=330):
    s = ts(text, N9, 44, WHITE, 0.06)
    p = rrect(s.shape[1] + 60, 80, 40, (0.1, 0.05, 0.1, 0.72)).copy()
    paste_spr(p, s, p.shape[1] / 2, 40)
    draw(c, p, x + p.shape[1] / 2, y)


# ------------------------------------------------------------------ scenes (one per beat of the PDF)
WOR = (4833, 8.4, 0.52, 0.45, 1.0)       # (clip, time, fx, fy, zoom): frowning down at her tablet
OPT = (4869, 9.6, 0.70, 0.45, 1.0)       # pink top, lively hands
REA = (4834, 6.3, 0.52, 0.45, 1.0)       # white blazer, straight to camera


def s01():   # WORRIER: "I work full time. So I can't foster, right?" (opens on the 5:30 pm walk home)
    c = grade(cover(frame_of(25890, 3.0), 0.5, 0.6), 'worrier')
    c = top_shade(c)
    clock_tag(c)
    slap(c, 'clock', 780, 760, 300, rot=8)
    slap(c, 'briefcase', 300, 1050, 300, rot=-8)
    c = shade(c)
    caption(c, 'I work full time.', keys=('full', 'time'), hl=SLATE)
    return c


def s02():
    c = char_frame('worrier', *WOR)
    c = top_shade(c)
    name_tag(c, 'worrier')
    slap(c, 'mug', 840, 1050, 240, rot=6)
    slap(c, 'house', 250, 720, 250, rot=-8)
    slap(c, 'question', 420, 560, 150, rot=10)
    c = shade(c)
    caption(c, ["I work full time.", "So I can't foster, right?"], keys=('foster',), hl=SLATE)
    return c


def s03():   # OPTIMIST: "Wait. Nobody said that's an automatic no."
    c = char_frame('optimist', *OPT)
    c = top_shade(c)
    name_tag(c, 'optimist')
    slap(c, 'sun', 260, 640, 240, rot=-8)
    slap(c, 'nostamp', 330, 1080, 330, rot=-10)
    lay = np.zeros((H, W), np.uint8)                       # the NO gets struck out
    cv2.line(lay, (150 * 4, 1180 * 4), (520 * 4, 980 * 4), 255, 22 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(LEAF[:3], np.float32) * m
    c = shade(c)
    caption(c, ["Wait. Nobody said that's", "an automatic no."], keys=('automatic', 'no'), hl=ORANGE)
    return c


def s04():   # REALIST: "The honest answer is: possibly."
    c = char_frame('realist', *REA)
    c = top_shade(c)
    name_tag(c, 'realist')
    slap(c, 'clipboard', 860, 1030, 250, rot=8)
    word_sticker(c, 'POSSIBLY.', 540, 1180, fill=PURPLE, size=96, rot=-5)
    slap(c, 'possibly', 300, 660, 260, rot=-6)
    c = shade(c)
    caption(c, 'The honest answer is: possibly.', keys=('possibly',), hl=PURPLE)
    return c


def s05():   # REALIST: "It depends on your hours, your flexibility, your support network and the child's needs."
    c = char_frame('realist', 4834, 9.0, 0.52, 0.42, 1.12)
    c = top_shade(c)
    name_tag(c, 'realist')
    for name, x, y, r, lab in (('clock', 210, 600, -8, 'hours'), ('calendar', 870, 620, 7, 'flexibility'),
                               ('network', 220, 1110, 6, 'support network'), ('heart', 870, 1090, -6, "child's needs")):
        slap(c, name, x, y, 230, rot=r)
        s = ts(lab, N9, 34, WHITE)
        p = rrect(s.shape[1] + 40, 58, 29, PURPLE).copy()
        paste_spr(p, s, p.shape[1] / 2, 29)
        draw(c, p, x, y + 150, rot=r * 0.5)
    c = shade(c, 0.66)
    caption(c, ["It depends on your hours, your flexibility,", "your support network and the child's needs."],
            keys=('hours', 'flexibility', 'support', 'network', 'needs'), hl=PURPLE, size=58)
    return c


def s06():   # OPTIMIST: "There's training, meetings, school events…" / REALIST: "…some in working hours. Plan for that."
    c = np.zeros((H, W, 3), np.float32)
    top = char_frame('optimist', 4869, 3.5, 0.7, 0.45, 1.0, W, H // 2)
    bot = char_frame('realist', 4834, 11.3, 0.52, 0.4, 1.0, W, H // 2)
    c[:H // 2] = top
    c[H // 2:] = bot
    c[H // 2 - 4:H // 2 + 4] = 1.0
    name_tag(c, 'optimist', 60, 300)
    name_tag(c, 'realist', 60, H // 2 + 80)
    slap(c, 'gradcap', 300, 620, 200, rot=-8)
    slap(c, 'calendar', 520, 760, 170, rot=6)
    slap(c, 'backpack', 840, 640, 190, rot=8)
    slap(c, 'briefcase', 820, 1300, 200, rot=-6)
    slap(c, 'clipboard', 230, 1420, 190, rot=6)
    c = shade(c, 0.72, 0.8)
    caption(c, ["There's training, meetings, school events…", "…some in working hours. Plan for that."],
            keys=('training', 'meetings', 'school', 'plan'), hl=ORANGE, y=1560, size=56)
    return c


def s07():   # WORRIER leans in: "So how do I know if it works for me?"
    c = char_frame('worrier', 4833, 8.8, 0.52, 0.40, 1.25)
    c = top_shade(c)
    name_tag(c, 'worrier')
    slap(c, 'magnifier', 800, 760, 280, rot=10)
    c = shade(c)
    caption(c, ["So how do I know", "if it works for me?"], keys=('works',), hl=SLATE)
    return c


def s08():   # ALL THREE: "You ask." — split screen
    c = np.zeros((H, W, 3), np.float32)
    pw = (W - 16) // 3
    for i, (kind, cid, t, fx) in enumerate((('worrier', 4833, 7.6, 0.52), ('optimist', 4869, 12.0, 0.70), ('realist', 4834, 12.6, 0.52))):
        sub = char_frame(kind, cid, t, fx, 0.42, 1.0, pw, 1240)
        c[200:1440, i * (pw + 8):i * (pw + 8) + pw] = sub
        label, col, prop = CHAR[kind]
        s = ts(label.replace('THE ', ''), N9, 30, WHITE, 0.06)
        p = rrect(s.shape[1] + 34, 54, 27, col).copy()
        paste_spr(p, s, p.shape[1] / 2, 27)
        draw(c, p, i * (pw + 8) + pw / 2, 1390)
        slap(c, prop, i * (pw + 8) + pw / 2, 300, 150, rot=(-8, 6, -4)[i])
    c[:200] = np.array(PLUM[:3], np.float32)
    c[1440:] = np.array(PLUM[:3], np.float32)
    word_sticker(c, 'YOU ASK.', 540, 1560, fill=ORANGE, size=110, rot=-3)
    slap(c, 'phone', 900, 1560, 200, rot=10)
    return c


def s09():   # end card
    c = canvas()
    lg = logo()
    draw(c, lg, W / 2, 470, scale=760 / lg.shape[1])
    s = ts('Ask us about fostering', N9, 70, PLUM)
    draw(c, s, W / 2, 760)
    s = ts('around your work', N9, 70, PURPLE)
    draw(c, s, W / 2, 850)
    btn = grad_spr(700, 130, 65)
    draw(c, blur_sprite(btn, 24), W / 2, 1035, opacity=0.5)
    draw(c, btn, W / 2, 1015)
    s = ts('Start your enquiry', N9, 52, WHITE)
    draw(c, s, W / 2 - 24, 1015)
    tri = np.zeros((44, 36), np.uint8)
    cv2.fillPoly(tri, [np.array([[4, 4], [4, 40], [32, 22]])], 255, cv2.LINE_AA)
    draw(c, solid(tri.astype(np.float32) / 255, WHITE), W / 2 + s.shape[1] / 2 + 6, 1015)
    draw(c, ts('0161 241 1332', N9, 72, PURPLE), W / 2, 1200)
    draw(c, ts('organicfostering.co.uk', N8, 42, PLUM), W / 2, 1285)
    for name, x, y, r in (('mug', 200, 1520, -8), ('sun', 540, 1560, 4), ('clipboard', 880, 1520, 8)):
        slap(c, name, x, y, 200, rot=r)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    which = [int(a) for a in sys.argv[1:]] or range(1, len(SCENES) + 1)
    for j in which:
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', to_u8(SCENES[j - 1]()))
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (270, 480), interpolation=cv2.INTER_AREA) for f in fs]
    while len(th) % 5:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 5]) for i in range(0, len(th), 5)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
