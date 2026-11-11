"""Scene images for Organic Fostering "No Qualification Needed" (the PDF: notebook, stern "Entry requirements" page, orange
NO QUALIFICATION NEEDED sticker, "My top 7" pages, learning continues, Ask us about training).

Story: dusk, people walking home through town; a woman at her table writes in a notebook. We drop into HER notebook: a
photoreal 3D spiral notepad on a wooden desk (Blender). Each page is drawn in the edit and mapped onto the 3D page.
Signature device: a POP-UP NOTEBOOK. Every topic's 3D object rises out of the page on a folded paper stand, like a
pop-up book, while a marker doodle draws itself; pages flip over the top spiral; taped photos bring in real people.

Usage: python3 frames_nq.py [n ...] -> workspace_nq/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_three'))
import numpy as np
import cv2
import frames_three as F3
from frames_three import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, PURPLE, ORANGE,
                          PLUM, IVORY, LAV, PEACH, LEAF, WHITE, N9, N8, N7, cover, grade)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_nq'
OUT = f'{S}/frames'
F3.S = f'{ROOT}/workspace_three'                      # logo + earlier stickers live there
_X, _Y = R._X, R._Y
HAND = 'Caveat-700'
PROJ = json.load(open(f'{S}/tex/pad_proj.json'))
TW, TH = 1000, 1360                                    # page texture size (same aspect as the 3D page)
INK = (0.18, 0.12, 0.2, 1)

TOPICS = [  # (number, title lines, 3D object, doodle, photo (clip, t) or None)
    (1, ['Why children', 'enter care'], 'umbrella', 'rain', None),
    (2, ['The role of a', 'foster carer'], 'house', 'hearts', ('4950', 4.0)),
    (3, ['Safeguarding &', 'professional', 'boundaries'], 'shield', 'fence', None),
    (4, ['Identity, culture,', 'equality &', 'inclusion'], 'network', 'stars', None),
    (5, ['Working with', 'birth families'], 'tree', 'link', ('4661', 4.0)),
    (6, ['How trauma can', 'influence', 'behaviour'], 'heartplaster', 'wave', None),
    (7, ['Recording,', 'confidentiality', '& teamwork'], 'padlock', 'ticks', ('4809', 3.0)),
]


# ------------------------------------------------------------------ sources
@__import__('functools').lru_cache(maxsize=1)
def DESK():
    return cv2.imread(f'{S}/tex/desk.png')[..., ::-1].astype(np.float32) / 255


@__import__('functools').lru_cache(maxsize=1)
def RINGS():
    r = cv2.imread(f'{S}/tex/rings.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = r[..., 3:4]
    return np.concatenate([r[..., 2::-1] * a, a], 2)              # premultiplied RGBA


@__import__('functools').lru_cache(maxsize=1)
def SHADING():
    """Lighting of the blank 3D page (relative), used to light whatever we draw on it."""
    d = DESK()
    m = page_mask()
    lum = d.mean(2)
    ref = np.median(lum[m > 0.5])
    sh = np.clip(lum / ref, 0.5, 1.3)[..., None]
    return sh


@__import__('functools').lru_cache(maxsize=1)
def HOM():
    src = np.float32([[0, 0], [TW, 0], [TW, TH], [0, TH]])
    dst = np.float32([PROJ['tl'], PROJ['tr'], PROJ['br'], PROJ['bl']])
    return cv2.getPerspectiveTransform(src, dst)


@__import__('functools').lru_cache(maxsize=1)
def page_mask():
    m = cv2.warpPerspective(np.ones((TH, TW), np.float32), HOM(), (W, H), flags=cv2.INTER_LINEAR)
    return m


_TOK = {}


def token(name):
    if name not in _TOK:
        p = f'{S}/assets/{name}.png'
        if not os.path.exists(p):
            p = f'{ROOT}/workspace_three/assets/{name}.png'
        sp = load_png_sprite(p)
        a = sp[..., 3]
        ys, xs = np.where(a > 0.01)
        _TOK[name] = np.ascontiguousarray(sp[max(0, ys.min() - 6):ys.max() + 7, max(0, xs.min() - 6):xs.max() + 7])
    return _TOK[name]


def frame_of(cid, t):
    for d in ('workspace_nq', 'workspace_three', 'workspace_tuned', 'workspace_three2'):
        p = f'{ROOT}/{d}/clips/{cid}.mp4'
        if os.path.exists(p):
            cap = cv2.VideoCapture(p)
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, im = cap.read()
            return im[..., ::-1].astype(np.float32) / 255
    raise FileNotFoundError(cid)


# ------------------------------------------------------------------ the page texture (dotted bullet-journal paper)
@__import__('functools').lru_cache(maxsize=1)
def PAPER():
    t = np.ones((TH, TW, 3), np.float32) * np.array([0.985, 0.972, 0.945], np.float32)
    for y in range(90, TH - 40, 40):
        for x in range(40, TW - 20, 40):
            cv2.circle(t, (x, y), 2, (0.80, 0.77, 0.80), -1, cv2.LINE_AA)
    rng = np.random.default_rng(2)
    t *= (1 - 0.015 * rng.random((TH, TW, 1))).astype(np.float32)
    return t


def tdraw(t, spr, x, y, scale=1.0, rot=0.0, opacity=1.0):
    draw(t, spr, x, y, scale=scale, rot=rot, opacity=opacity)


def ttext(t, s, x, y, size, col=PLUM, font=N9, rot=0, opacity=1.0, anchor='c'):
    sp = solid(_wmask(s, font, size), col)
    if anchor == 'l':
        x = x + sp.shape[1] / 2
    tdraw(t, sp, x, y, rot=rot, opacity=opacity)
    return sp.shape[1]


def marker_path(t, pts, col=ORANGE, th=8, k=1.0):
    pts = np.array(pts, np.float32)
    n = max(2, int(len(pts) * k))
    lay = np.zeros(t.shape[:2], np.uint8)
    cv2.polylines(lay, [(pts[:n] * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.92
    t[:] = t * (1 - m) + np.array(col[:3], np.float32) * m


def doodle(t, kind, k=1.0, cx=500, cy=900):
    rng = np.random.default_rng(len(kind))
    if kind == 'rain':
        for i in range(9):
            x0, y0 = 300 + i * 50, 640 + (i % 3) * 30
            marker_path(t, [(x0, y0), (x0 - 12, y0 + 40)], col=(0.45, 0.62, 0.85, 1), th=6, k=min(1, k * 1.5))
    elif kind == 'hearts':
        for j, (x, y) in enumerate(((260, 660), (760, 640), (720, 1120))):
            pts = [(x + 26 * (16 * math.sin(a) ** 3) / 16, y - 26 * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16)
                   for a in np.linspace(0, 2 * math.pi, 40)]
            marker_path(t, pts, col=PURPLE, th=6, k=k)
    elif kind == 'fence':
        pts = []
        for i in range(8):
            x = 240 + i * 75
            marker_path(t, [(x, 1150), (x, 1060), (x + 15, 1040), (x + 30, 1060), (x + 30, 1150)], col=LEAF, th=6, k=k)
        marker_path(t, [(225, 1095), (800, 1095)], col=LEAF, th=6, k=k)
    elif kind == 'stars':
        for (x, y, c) in ((240, 640, ORANGE), (780, 660, PURPLE), (250, 1120, LEAF), (790, 1110, ORANGE)):
            pts = [(x + (34 if i % 2 == 0 else 15) * math.sin(i * math.pi / 5), y - (34 if i % 2 == 0 else 15) * math.cos(i * math.pi / 5))
                   for i in range(11)]
            marker_path(t, pts, col=c, th=6, k=k)
    elif kind == 'link':
        marker_path(t, [(230, 1120 - 40 * math.sin(u * math.pi)) if False else (230 + u * 560, 1130 - 70 * math.sin(u * math.pi))
                        for u in np.linspace(0, 1, 40)], col=ORANGE, th=7, k=k)
    elif kind == 'wave':
        marker_path(t, [(220 + u * 580, 1110 + 40 * math.sin(u * 14) * (1 - u)) for u in np.linspace(0, 1, 60)], col=PURPLE, th=7, k=k)
    elif kind == 'ticks':
        for i in range(3):
            y = 1040 + i * 50
            marker_path(t, [(250, y), (268, y + 18), (300, y - 16)], col=LEAF, th=7, k=k)
            marker_path(t, [(330, y), (520 - 40 * i, y)], col=(0.6, 0.55, 0.62, 1), th=5, k=k)


def popup_base(c, x, y, w, k=1.0):
    """The folded paper stand a pop-up object rises on (two lavender panels meeting at a crease)."""
    if k <= 0:
        return
    hh = int(w * 0.32 * k)
    if hh < 3:
        return
    lay = np.zeros((hh + 40, int(w) + 40, 4), np.float32)
    pts_l = np.array([[20, hh + 20], [20 + w / 2, 20], [20 + w / 2, hh + 20]], np.int32)
    pts_r = np.array([[20 + w / 2, 20], [20 + w, hh + 20], [20 + w / 2, hh + 20]], np.int32)
    for pts, shade in ((pts_l, 0.92), (pts_r, 0.78)):
        m = np.zeros(lay.shape[:2], np.uint8)
        cv2.fillPoly(m, [pts], 255, cv2.LINE_AA)
        mm = m.astype(np.float32)[..., None] / 255
        col = np.array(LAV[:3], np.float32) * shade
        lay[..., :3] = lay[..., :3] * (1 - mm) + col * mm
        lay[..., 3:] = np.maximum(lay[..., 3:], mm)
    draw(c, blur_sprite(tint(lay, (0.2, 0.1, 0.15)), 10), x + 8, y + 10, opacity=0.35)
    draw(c, lay, x, y)


def pop_object(c, name, x, y, size, k=1.0, rot=0, stand=True):
    """Pop-up book: the 3D object unfolds upward from the page (scale in y from the base), with its paper stand."""
    if k <= 0:
        return
    sp = token(name)
    e = min(1.0, k)
    eb = e if k <= 1 else 1.0
    sc = size / max(sp.shape[:2])
    hh = max(2, int(sp.shape[0] * sc * eb))
    ww = max(2, int(sp.shape[1] * sc * (0.85 + 0.15 * eb)))
    s2 = cv2.resize(sp, (ww, hh), interpolation=cv2.INTER_AREA)
    if stand:
        popup_base(c, x, y + 10, ww * 0.9, eb)
    draw(c, blur_sprite(tint(s2, (0.15, 0.08, 0.12)), 18), x + 18, y - hh / 2 + 30, rot=rot, opacity=0.4 * eb)
    draw(c, s2, x, y - hh / 2 - 12 * eb, rot=rot)


def polaroid(cid, t, w=300, h=240, cap_text=None):
    im = grade(cover(frame_of(cid, t), 0.5, 0.45, 1.0, w, h), 'realist')
    card = np.ones((h + 80, w + 30, 4), np.float32)
    card[15:15 + h, 15:15 + w, :3] = im
    if cap_text:
        paste_spr(card, solid(_wmask(cap_text, HAND, 34), INK), (w + 30) / 2, h + 48)
    return card


def tape(c, x, y, rot):
    tp = rrect(130, 40, 4, (1.0, 0.93, 0.75, 0.75))
    draw(c, tp, x, y, rot=rot)


def page_texture(kind, k=1.0, idx=None):
    t = PAPER().copy()
    if kind == 'entry':
        ttext(t, 'Entry requirements', 500, 170, 78, PLUM)
        marker_path(t, [(150, 225), (850, 222)], col=PLUM, th=6, k=1)
        for i, (lab, sub) in enumerate((('University degree', 'in a relevant subject'), ('Childcare qualification', 'Level 3 or above'),
                                        ('Teaching course', 'completed'))):
            y = 380 + i * 170
            box = np.zeros((80, 80), np.uint8)
            cv2.rectangle(box, (6, 6), (74, 74), 255, 6)
            tdraw(t, solid(box.astype(np.float32) / 255, PLUM), 170, y)
            ttext(t, lab, 250, y - 14, 50, INK, N8, anchor='l')
            ttext(t, sub, 252, y + 38, 34, (0.45, 0.4, 0.48, 1), N7, anchor='l')
        ttext(t, 'Must hold ALL of the above.', 500, 920, 40, (0.6, 0.15, 0.2, 1), N8)
    elif kind == 'learn':
        ttext(t, "What you'll learn", 500, 180, 74, PLUM)
        ttext(t, 'before approval:', 500, 270, 74, PLUM)
        marker_path(t, [(170, 320), (830, 318)], col=ORANGE, th=7, k=1)
        ttext(t, 'my top 7', 500, 420, 80, ORANGE, HAND, rot=-4)
        for i in range(7):
            y = 560 + i * 90
            ttext(t, f'{i + 1}.', 200, y, 54, ORANGE, HAND)
            marker_path(t, [(250, y + 10), (250 + 420 + 40 * ((i * 3) % 4), y + 10)], col=(0.8, 0.76, 0.8, 1), th=4, k=1)
    elif kind == 'topic':
        n, lines, obj, dd, photo = TOPICS[idx]
        ttext(t, str(n), 150, 190, 210, ORANGE, HAND, rot=-6)
        for j, l in enumerate(lines):
            ttext(t, l, 262, 140 + j * 84, 74, PLUM, N9, anchor='l')
        doodle(t, dd, k)
        for i in range(7):                                 # progress dots along the foot of the page
            col = ORANGE if i <= idx else (0.82, 0.78, 0.82, 1)
            cv2.circle(t, (320 + i * 60, 1290), 13 if i == idx else 10, col[:3], -1, cv2.LINE_AA)
    elif kind == 'more':
        ttext(t, "And it doesn't stop", 500, 170, 70, PLUM)
        ttext(t, 'learning continues', 500, 270, 66, ORANGE, HAND)
        ttext(t, 'throughout fostering', 500, 340, 66, ORANGE, HAND)
        marker_path(t, [(200, 390), (800, 386)], col=PURPLE, th=6, k=1)
        for i, lab in enumerate(('online', 'workshops', 'group discussion')):
            ttext(t, lab, (200, 500, 800)[i], 1180, 46, PLUM, HAND)
    elif kind == 'end':
        lg = F3.logo()
        tdraw(t, lg, 500, 260, scale=700 / lg.shape[1])
        ttext(t, 'Ask us about', 500, 560, 92, PLUM)
        ttext(t, 'training', 500, 670, 120, ORANGE, HAND, rot=-3)
        marker_path(t, [(330, 730), (690, 724)], col=ORANGE, th=8, k=1)
        ttext(t, '0161 241 1332', 500, 1010, 70, PURPLE)
        ttext(t, 'organicfostering.co.uk', 500, 1090, 44, PLUM, N8)
    elif kind == 'cover':
        t[:] = np.array(PLUM[:3], np.float32)
        ttext(t, 'notes', 500, 680, 120, (1, 1, 1, 0.85), HAND)
    return t


def put_page(c, tex, alpha=1.0):
    warped = cv2.warpPerspective(tex, HOM(), (W, H), flags=cv2.INTER_LINEAR)
    m = page_mask()[..., None] * alpha
    lit = warped * SHADING()
    c[:] = c * (1 - m) + lit * m


def page_xy(u, v):
    """Texture coords (u in 0..TW, v in 0..TH) -> frame coords."""
    p = HOM() @ np.array([u, v, 1.0])
    return p[0] / p[2], p[1] / p[2]


def rings_over(c):
    r = RINGS()
    a = r[..., 3:4]
    c[:] = c * (1 - a) + r[..., :3]


def desk_with(tex):
    c = DESK().copy()
    put_page(c, tex)
    rings_over(c)
    return c


def caption(c, lines, keys=(), y=1760, size=58, hl=ORANGE):
    F3.caption(c, lines, keys=keys, y=y, size=size, hl=hl)


def sticker_no_qual(c, x=540, y=1000, rot=-8, sc=1.0):
    s1 = ts('NO QUALIFICATION', N9, 84, WHITE, 0.01)
    s2 = ts('NEEDED', N9, 120, WHITE, 0.02)
    w = max(s1.shape[1], s2.shape[1]) + 90
    p = rrect(w, 290, 40, ORANGE).copy()
    paste_spr(p, s1, w / 2, 90)
    paste_spr(p, s2, w / 2, 200)
    b = rrect(w + 30, 320, 54, WHITE).copy()
    paste_spr(b, p, b.shape[1] / 2, b.shape[0] / 2)
    draw(c, blur_sprite(tint(b, (0.15, 0.05, 0.12)), 18), x + 14, y + 22, rot=rot, scale=sc, opacity=0.5)
    draw(c, b, x, y, rot=rot, scale=sc)


# ------------------------------------------------------------------ scenes
def s01():   # "Before you can foster…" — dusk, people walking home through town
    c = grade(cover(frame_of('3428', 9.0), 0.5, 0.55, 1.0), 'optimist')
    c = F3.top_shade(c)
    c = F3.shade(c)
    caption(c, ["Before you can foster,"], y=1500, size=66)
    return c


def s02():   # "…you'll need to study…" — at her table, writing in her notebook
    c = grade(cover(frame_of('4953', 4.0), 0.5, 0.5, 1.0), 'realist')
    c = F3.top_shade(c)
    pop = token('books')
    draw(c, blur_sprite(tint(pop, PLUM[:3]), 18), 798, 640, scale=280 / max(pop.shape[:2]), opacity=0.4)
    draw(c, pop, 790, 620, scale=280 / max(pop.shape[:2]))
    c = F3.shade(c)
    caption(c, ["Before you can foster,", "you'll need to study…"], keys=('study',), y=1500, size=66)
    return c


def s03():   # the stern Entry requirements page, objects popping up from the page
    c = desk_with(page_texture('entry'))
    x, y = page_xy(760, 1150)
    pop_object(c, 'certificate', x, y, 240, 1.0)
    x, y = page_xy(300, 1180)
    pop_object(c, 'gradcap', x, y, 220, 1.0)
    caption(c, ["Before you can foster,", "you'll need to study…"], keys=('study',))
    return c


def s04():   # "…with us. No qualification needed." — the orange sticker slaps on, the boxes get ticked away
    c = desk_with(page_texture('entry'))
    sticker_no_qual(c, 540, 980, rot=-8)
    caption(c, ["…with us.", "No qualification needed."], keys=('no', 'qualification', 'needed'))
    return c


def s05():   # "What you'll learn before approval:" — page flips to the top-7 list
    c = desk_with(page_texture('learn'))
    caption(c, ["What you'll learn", "before approval:"], keys=('learn',), hl=PURPLE)
    return c


def topic_scene(i):
    n, lines, obj, dd, photo = TOPICS[i]
    c = desk_with(page_texture('topic', 1.0, i))
    x, y = page_xy(500, 900)
    pop_object(c, obj, x, y + 40, 330, 1.0)
    if photo:
        pc = polaroid(*photo)
        px, py = page_xy(800, 1150)
        draw(c, blur_sprite(tint(pc, (0.15, 0.08, 0.12)), 16), px + 10, py + 16, rot=7, opacity=0.4)
        draw(c, pc, px, py, rot=7, scale=0.85)
        tape(c, px, py - 140, 4)
    caption(c, [f'{n}. ' + ' '.join(lines).replace('& ', '& ')], keys=(), size=54)
    return c


def s06():
    return topic_scene(0)


def s07():
    return topic_scene(1)


def s08():
    return topic_scene(3)


def s09():
    return topic_scene(4)


def s10():
    return topic_scene(6)


def s11():   # "And it doesn't stop: learning continues throughout fostering." — the notebook grows more pages
    c = desk_with(page_texture('more'))
    for j, (obj, u) in enumerate((('laptop', 200), ('workshop', 500), ('bubbles', 800))):
        x, y = page_xy(u, 1080)
        pop_object(c, obj, x, y, 220, 1.0)
    caption(c, ["And it doesn't stop: learning", "continues throughout fostering."], keys=('learning', 'continues'), size=54)
    return c


def s12():   # "Ask us about training." — the last page is the end card
    c = desk_with(page_texture('end'))
    x, y = page_xy(500, 1230)
    btn = F3.grad_spr(640, 120, 60)
    draw(c, blur_sprite(btn, 22), x, y + 18, opacity=0.5)
    draw(c, btn, x, y)
    s = ts('Start your enquiry', N9, 50, WHITE)
    draw(c, s, x - 20, y)
    tri = np.zeros((44, 36), np.uint8)
    cv2.fillPoly(tri, [np.array([[4, 4], [4, 40], [32, 22]])], 255, cv2.LINE_AA)
    draw(c, solid(tri.astype(np.float32) / 255, WHITE), x + s.shape[1] / 2 + 6, y)
    xx, yy = page_xy(840, 900)
    pop_object(c, 'phone', xx, yy, 170, 1.0)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]


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
    while len(th) % 6:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 6]) for i in range(0, len(th), 6)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
