"""Scene images for Hulk Marketing "Same Business?" (the concept PDF, voiceover word for word), video version with people.

Each touchpoint pops in on its word as a 3D object over real people meeting it (street, shopfront, handshake, laptop,
phone, paperwork); "They are." on forest black with a confused customer; the system builds itself with the Hulk team;
every touchpoint snaps into Copperline navy and amber; Hulk's line; end card.

Usage: python3 frames_sb.py [n ...] -> workspace_hulk/sb_frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import cv2
import frames_hulk as K
from frames_hulk import (F, R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, frame_of, vivid, trim, spr,
                         cutout, logo, arrow_ne, hexc, cracks)

S = K.S
OUT = f'{S}/sb_frames'
_X, _Y = R._X, R._Y
OFF, FOREST, LIME = hexc('#F3F5F0'), hexc('#121C17'), hexc('#9DEF69')
NAVY, AMBER = hexc('#1E2A4A'), hexc('#F5A524')
WHITE = (1, 1, 1, 1)
CAP, CAPB = 'Headline-800', 'Headline-900'
SMALL = 'Hanken-700'
ITEMS = ['van', 'sign', 'card', 'web', 'insta', 'invoice']
# tilt/offset "jitter" for the before items (deliberately off-grid)
JIT = {'van': -4, 'sign': 3, 'card': -6, 'web': 5, 'insta': -3, 'invoice': 6}

_T3 = {}


def t3(name):
    if name not in _T3:
        sp = spr(f'{S}/sb_3d/{name}.png')
        ys, xs = np.where(sp[..., 3] > 0.35)
        pad = 30
        y0, y1 = max(0, ys.min() - pad), min(sp.shape[0], ys.max() + pad)
        x0, x1 = max(0, xs.min() - pad), min(sp.shape[1], xs.max() + pad)
        _T3[name] = np.ascontiguousarray(sp[y0:y1, x0:x1])
    return _T3[name]


# ------------------------------------------------------------------ canvases
def offwhite(dots=True):
    c = np.ones((H, W, 3), np.float32) * np.array(OFF[:3], np.float32)
    if dots:
        d = (((_X % 36) - 18) ** 2 + ((_Y % 36) - 18) ** 2 < 4).astype(np.float32)[..., None] * 0.09
        c = c - d * 0.6
    return c.astype(np.float32)


def forest(glow=0.12):
    c = np.ones((H, W, 3), np.float32) * np.array(FOREST[:3], np.float32)
    g = np.exp(-((_X - W / 2) ** 2 + (_Y - 820) ** 2) / (2 * 520 ** 2))[..., None] * glow
    return np.clip(c + g * np.array(LIME[:3], np.float32) * 0.5, 0, 1).astype(np.float32)


def clip(cid, t, w=W, h=H, fx=0.5, fy=0.5, z=1.0):
    return vivid(F.cover(frame_of(cid, t), fx, fy, z, w, h))


# ------------------------------------------------------------------ type
def cap(c, lines, key=(), y=1500, size=74, x=70, dark=False, center=False):
    """Inter Tight ExtraBold captions; the key word lime (on dark) or in a lime box (on light)."""
    key = {k.lower() for k in key}
    for li, ln in enumerate(lines):
        ws = ln.split()
        ms = [_wmask(w_, CAP, size) for w_ in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.22 * (len(ws) - 1)
        xx = (W / 2 - tw / 2) if center else x
        yy = y + li * size * 1.12
        for w_, m in zip(ws, ms):
            k = w_.strip('.,?!’\'…').lower() in key
            if k and not dark:
                draw(c, rrect(m.shape[1] + size * 0.2, size * 1.1, 10, LIME), xx + m.shape[1] / 2, yy + size * 0.04)
                draw(c, solid(m, FOREST), xx + m.shape[1] / 2, yy)
            else:
                col = LIME if k else (WHITE if dark else FOREST)
                draw(c, solid(m, col), xx + m.shape[1] / 2, yy)
            xx += m.shape[1] + size * 0.22


def counter(c, k, x=W - 150, y=290, dark=False):
    s = ts(f'{k} / 6', CAPB, 40, FOREST if not dark else FOREST)
    draw(c, rrect(170, 74, 37, LIME), x, y)
    draw(c, s, x, y)


def label(c, text, x, y, dark=False):
    s = ts(text.upper(), SMALL, 26, FOREST if not dark else (1, 1, 1, 0.8), 0.14)
    draw(c, s, x + s.shape[1] / 2, y)


def hulk_tag(c, x=70, y=150, dark=False):
    lg = logo()
    draw(c, lg, x + 100, y, scale=200 / lg.shape[1], opacity=0.9)


# ------------------------------------------------------------------ pieces
def card(img, w, h, r=40):
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, r, 2)), (w, h))
    pic = F.cover(img, 0.5, 0.5, 1.0, w, h) if img.shape[:2] != (h, w) else img
    return np.concatenate([pic * m[..., None], m[..., None]], 2).astype(np.float32)


def put_card(c, img, x, y, w, h, rot=0, sh=0.35):
    k = card(img, w, h)
    draw(c, blur_sprite(tint(k, (0.05, 0.08, 0.06)), 30), x + 8, y + 28, rot=rot, opacity=sh)
    draw(c, k, x, y, rot=rot)


def obj(c, name, x, y, size, rot=0, shadow=True):
    sp = t3(name)
    sc = size / max(sp.shape[:2])
    draw(c, sp, x, y, scale=sc, rot=rot)


def pop_ring(c, x, y, r, col=LIME, th=6):
    lay = np.zeros((H, W), np.uint8)
    cv2.circle(lay, (int(x * 4), int(y * 4)), int(r * 4), 255, th * 4, cv2.LINE_AA, shift=2)
    for j in range(10):
        a = j / 10 * 2 * math.pi + 0.2
        cv2.line(lay, (int((x + math.cos(a) * r * 1.15) * 4), int((y + math.sin(a) * r * 1.15) * 4)),
                 (int((x + math.cos(a) * r * 1.38) * 4), int((y + math.sin(a) * r * 1.38) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def tick(c, x, y, r=34):
    draw(c, rrect(2 * r, 2 * r, r, LIME), x, y)
    lay = np.zeros((H, W), np.uint8)
    pts = np.array([(x - r * 0.45, y + 0.02 * r), (x - r * 0.1, y + r * 0.35), (x + r * 0.48, y - r * 0.32)]) * 4
    cv2.polylines(lay, [pts.astype(np.int32)], False, 255, int(r * 0.22 * 4), cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(FOREST[:3], np.float32) * m


def guideline(c, x0, y0, x1, y1, col=(0.07, 0.11, 0.09, 0.25)):
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (int(x0), int(y0)), (int(x1), int(y1)), 255, 2, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255 * col[3]
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m


def touch_scene(cid, t, item, k, word, fx=0.5, fy=0.5, size=640, ox=W / 2, oy=980):
    """One 'before' beat: a real person meets the touchpoint; the 3D item pops in on its word."""
    c = offwhite()
    put_card(c, clip(cid, t, 940, 1000, fx, fy), W / 2, 760, 940, 1000, rot=JIT[item] * 0.3)
    pop_ring(c, ox, oy, size * 0.42)
    obj(c, f'{item}_before', ox, oy, size, rot=JIT[item])
    counter(c, k)
    hulk_tag(c)
    cap(c, [word], key=(), y=1500, size=86)
    return c


# ------------------------------------------------------------------ scenes
def s01():   # "Quick one. Are these the same business?"
    c = offwhite()
    put_card(c, clip(6302, 0.4, 940, 900, fy=0.45), W / 2, 680, 940, 900)
    pop_ring(c, 560, 1090, 300)
    obj(c, 'van_before', 560, 1090, 720, rot=-4)
    counter(c, 1)
    hulk_tag(c)
    draw(c, ts('Quick one.', CAP, 46, (0.07, 0.11, 0.09, 0.7)), 200, 1395)
    for i, w_ in enumerate(('Same', 'business?')):
        m = _wmask(w_, CAPB, 150)
        draw(c, solid(m, FOREST), 70 + m.shape[1] / 2, 1520 + i * 150)
    return c


def s02():   # "The van. The sign."
    c = touch_scene(15997, 0.55, 'sign', 2, 'The sign.', fy=0.6, size=700, oy=900)
    obj(c, 'van_before', 860, 1260, 300, rot=8)
    return c


def s03():   # "The card."
    return touch_scene(30012, 0.6, 'card', 3, 'The card.', size=620, oy=1020)


def s04():   # "The website."
    return touch_scene(4713, 0.5, 'web', 4, 'The website.', size=700, oy=1000)


def s05():   # "The Instagram."
    return touch_scene(4919, 0.5, 'insta', 5, 'The Instagram.', size=640, ox=760, oy=900)


def s06():   # "The invoice."
    return touch_scene(46505, 0.25, 'invoice', 6, 'The invoice.', size=640, ox=780, oy=980)


POS = {'van': (300, 520, 440), 'sign': (790, 470, 420), 'card': (280, 860, 380), 'web': (780, 860, 440),
       'insta': (300, 1200, 400), 'invoice': (780, 1200, 400)}


def s07():   # the mess: all six jostling, 6/6
    c = offwhite()
    for it in ITEMS:
        x, y, s = POS[it]
        obj(c, f'{it}_before', x + JIT[it] * 4, y + JIT[it] * 3, s, rot=JIT[it] * 1.5)
    counter(c, 6)
    hulk_tag(c)
    cap(c, ['Same business?'], key=('business?',), y=1540, size=90)
    return c


def s08():   # "They are. And your customers can't tell either."
    c = forest()
    for i, it in enumerate(ITEMS):
        obj(c, f'{it}_before', 110 + i * 172, 330, 150, rot=JIT[it])
    c[:200 + 220] = c[:200 + 220] * 0.55 + np.array(FOREST[:3], np.float32) * 0.45
    put_card(c, clip(9248, 0.5, 820, 640, fy=0.4), W / 2, 820, 820, 640, sh=0.6)
    for m_ in (0,):
        lay = np.zeros((H, W), np.uint8)
        cv2.rectangle(lay, (W // 2 - 412, 820 - 322), (W // 2 + 412, 820 + 322), 255, 4)
    for i, w_ in enumerate(('They are.',)):
        m = _wmask(w_, CAPB, 130)
        draw(c, solid(m, WHITE), 70 + m.shape[1] / 2, 1290)
    for i, ln in enumerate(('And your customers', 'can’t tell either.')):
        m = _wmask(ln, CAP, 74)
        draw(c, solid(m, LIME), 70 + m.shape[1] / 2, 1440 + i * 84)
    # second line in lime per the PDF
    c2 = c
    return c2


def s09():   # "Disjointed brand, diluted trust."
    c = forest()
    rng = np.random.default_rng(3)
    for i, it in enumerate(ITEMS):
        dx, dy = rng.uniform(-30, 30), rng.uniform(-40, 40)
        obj(c, f'{it}_before', 110 + i * 172 + dx, 760 + dy, 160, rot=JIT[it] * 2 + rng.uniform(-8, 8))
    cracks_dark(c)
    cap(c, ['Disjointed brand,', 'diluted trust.'], key=('trust',), y=1250, size=96, dark=True)
    lay = np.zeros((H, W), np.uint8)
    wd = _wmask('diluted', CAP, 96).shape[1] + 96 * 0.22
    wt = _wmask('trust.', CAP, 96).shape[1]
    ux0, ux1, uy = 70 + wd, 70 + wd + wt - 30, 1250 + 96 * 1.12 + 62
    cv2.line(lay, (int(ux0 * 4), int(uy * 4)), (int(ux1 * 4), int(uy * 4)), 255, 7 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(LIME[:3], np.float32) * m
    return c


def cracks_dark(c):
    """Thin hairline cracks between the six items."""
    rng = np.random.default_rng(8)
    lay = np.zeros((H, W), np.uint8)
    for i in range(5):
        x = 196 + i * 172
        px, py = x, 640
        for _ in range(7):
            nx, ny = px + rng.normal(0, 7), py + 18
            cv2.line(lay, (int(px * 4), int(py * 4)), (int(nx * 4), int(ny * 4)), 255, 2 * 4, cv2.LINE_AA, shift=2)
            px, py = nx, ny
    m = lay.astype(np.float32)[..., None] / 255 * 0.35
    c[:] = c * (1 - m) + np.array(LIME[:3], np.float32) * m


def s10():   # "So we build one system: one logo, one palette, one typeface."
    c = offwhite(dots=False)
    label(c, 'Copperline · brand guidelines', 70, 150)
    draw(c, rrect(940, 2, 1, (0.07, 0.11, 0.09, 0.2)), W / 2, 190)
    # the Hulk team building it (real people from the site)
    sp = cutout('CUT-07-oliver-james-whitmore.webp')
    draw(c, sp, 860, 980, scale=620 / sp.shape[0])
    obj(c, 'mark', 320, 420, 330)
    label(c, '01  Logo', 70, 640)
    obj(c, 'swatches', 360, 820, 520)
    label(c, '02  Palette', 70, 1010)
    for i, (col, hx) in enumerate(((NAVY, 'Navy'), (AMBER, 'Amber'), (OFF, 'Off-white'), (hexc('#606C80'), 'Slate'))):
        pass
    obj(c, 'aa', 260, 1150, 280)
    draw(c, ts('Inter Tight', 'Headline-700', 40, FOREST), 520, 1130)
    label(c, '03  Typeface', 70, 1290)
    cap(c, ['So we build one system:', 'one logo, one palette,', 'one typeface.'], key=('system',), y=1430, size=66)
    return c


def s11():   # "Then roll it out across every touchpoint."
    c = offwhite()
    gx = (290, 790)
    gy = (430, 790, 1150)
    for i, it in enumerate(ITEMS):
        x, y = gx[i % 2], gy[i // 2]
        draw(c, rrect(470, 330, 30, (1, 1, 1, 0.85)), x, y)
        obj(c, f'{it}_after', x, y, 400)
        tick(c, x + 200, y - 130, 26)
    for x in gx:
        guideline(c, x, 230, x, 1330)
    hulk_tag(c)
    cap(c, ['Then roll it out across', 'every touchpoint.'], key=('every', 'touchpoint.'), y=1450, size=70)
    return c


def s12():   # "A premium brand is a system, not a logo file."
    c = forest(0.18)
    put_card(c, clip(49023, 0.5, 860, 600, fx=0.6, fy=0.4), W / 2, 560, 860, 600, sh=0.6)
    obj(c, 'van_after', 330, 860, 440, rot=-2)
    obj(c, 'card_after', 800, 900, 330, rot=6)
    for i, (w_, col) in enumerate((('A premium brand', WHITE), ('is a system,', LIME), ('not a logo file.', WHITE))):
        m = _wmask(w_, CAPB, 92)
        draw(c, solid(m, col), 70 + m.shape[1] / 2, 1180 + i * 108)
    return c


def s13():   # "Build your brand identity with Hulk." end card
    c = forest(0.2)
    lg = logo()
    draw(c, lg, W / 2, 560, scale=820 / lg.shape[1])
    draw(c, ts('A premium brand is a system, not a logo file.', 'Hanken-700', 34, (1, 1, 1, 0.8)), W / 2, 690)
    btn = rrect(800, 140, 70, LIME)
    draw(c, blur_sprite(btn, 30), W / 2, 960, opacity=0.5)
    draw(c, btn, W / 2, 960)
    K.text_ne(c, 'Build My Brand Identity', W / 2, 960, CAPB, 50, FOREST)
    draw(c, ts('hulkmarketing.co.uk', CAPB, 44, LIME), W / 2, 1130)
    draw(c, ts('07577 764436', CAPB, 44, WHITE), W / 2, 1200)
    obj(c, 'mark', 900, 1450, 0) if False else None
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.08, grain=0.01, vig=0.12))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
