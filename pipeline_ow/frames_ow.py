"""Scene images for Organic Fostering "One Weekend" (respite fostering), video version with people and 3D.

Story: Friday at golden hour, a couple walk home; a hand circles a weekend on the kitchen calendar (a photoreal, dateless
3D wall calendar); the circle stretches to part of a school holiday, then another agreed period, each with a glossy 3D
object (weekend bag, bucket & spade, clipboard). Two 3D houses link up; a moon settles over the first, which gets its rest.
A front door opens: the same home, time after time. Pages flip with the same weekend lit; the circled weekends stack
into a chain. End card.

Signature device: the hand-drawn magenta-to-orange marker loop circles the dates AND the cue words in the captions.
No children are shown.

Usage: python3 frames_ow.py [n ...] -> workspace_ow/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_cf'))
import numpy as np
import cv2
import frames_cf as F
from frames_cf import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask, PURPLE, ORANGE,
                       PLUM, IVORY, LAV, PEACH, LEAF, WHITE, N9, N8, N7)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_ow'
OUT = f'{S}/frames'
HAND = 'Caveat-700'
_X, _Y = R._X, R._Y
GRID = json.load(open(f'{S}/tex/cal_grid.json'))
PROJ = json.load(open(f'{S}/tex/cal_proj.json'))


# ------------------------------------------------------------------ sources
def frame_of(cid, t=0.45):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def clip(cid, t, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    return F.grade(F.cover(frame_of(cid, t), fx, fy, z, w, h))


_SPR = {}


def spr(path):
    if path not in _SPR:
        sp = load_png_sprite(path)
        ys, xs = np.where(sp[..., 3] > 0.05)
        _SPR[path] = np.ascontiguousarray(sp[max(0, ys.min() - 10):ys.max() + 10, max(0, xs.min() - 10):xs.max() + 10])
    return _SPR[path]


def token(name):
    for p in (f'{S}/assets/{name}.png', f'{ROOT}/workspace_cf/assets/{name}.png', f'{ROOT}/workspace_yah/assets/{name}.png'):
        if os.path.exists(p):
            return spr(p)
    raise FileNotFoundError(name)


def calendar_bg():
    im = cv2.imread(f'{S}/tex/cal_render.png')[..., ::-1].astype(np.float32) / 255
    return cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)


def tex2img(x, y):
    """Calendar texture px -> render px (affine from the projected corners)."""
    u, v = x / GRID['W'], y / GRID['H']
    tl, tr, bl = np.array(PROJ['tl']), np.array(PROJ['tr']), np.array(PROJ['bl'])
    p = tl + (tr - tl) * u + (bl - tl) * v
    return float(p[0]), float(p[1])


def cell_box(r, c):
    x0, y0, x1, y1 = GRID['cells'][f'{r},{c}']
    a = tex2img(x0, y0)
    b = tex2img(x1, y1)
    return a[0], a[1], b[0], b[1]


# ------------------------------------------------------------------ marker (hand-drawn gradient loop)
def grad_col(u):
    u = np.clip(u, 0, 1)[..., None]
    return np.array(PURPLE[:3], np.float32) * (1 - u) + np.array(ORANGE[:3], np.float32) * u


def loop_pts(x0, y0, x1, y1, k=1.0, seed=0, pad=14, turns=1.12):
    rng = np.random.default_rng(seed)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad
    n = 140
    t = np.linspace(0, 2 * math.pi * turns * k, max(3, int(n * k)))
    t0 = -2.3
    wob = 1 + 0.035 * np.sin(3 * t + seed) + 0.02 * np.cos(5 * t)
    xs = cx + rx * np.cos(t + t0) * wob + rng.normal(0, 0.8, len(t))
    ys = cy + ry * np.sin(t + t0) * wob * (1 + 0.04 * t / (2 * math.pi)) + rng.normal(0, 0.8, len(t))
    return np.stack([xs, ys], 1)


def marker(c, pts, th=9):
    lay = np.zeros(c.shape[:2], np.uint8)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    u = np.clip((_X[:c.shape[0], :c.shape[1]] - pts[:, 0].min()) / max(1, np.ptp(pts[:, 0])), 0, 1)
    c[:] = c * (1 - m * 0.95) + grad_col(u) * m * 0.95


def fill_cells(c, cells, amt=0.75):
    lay = np.zeros(c.shape[:2], np.float32)
    for r_, c_ in cells:
        x0, y0, x1, y1 = cell_box(r_, c_)
        m = cv2.resize(R.sdf_fill(R.rrect_alpha(int(x1 - x0), int(y1 - y0), 16, 2)), (int(x1 - x0), int(y1 - y0)))
        lay[int(y0):int(y0) + m.shape[0], int(x0):int(x0) + m.shape[1]] = np.maximum(lay[int(y0):int(y0) + m.shape[0], int(x0):int(x0) + m.shape[1]], m)
    m = lay[..., None] * amt
    xs = [cell_box(r_, c_)[0] for r_, c_ in cells] + [cell_box(r_, c_)[2] for r_, c_ in cells]
    u = np.clip((_X - min(xs)) / max(1, max(xs) - min(xs)), 0, 1)
    # keep the day numbers readable: multiply-ish blend
    c[:] = c * (1 - m) + (c * 0.25 + grad_col(u) * 0.75) * m


def circle_span(c, cells, seed=0, k=1.0):
    xs0 = min(cell_box(*rc)[0] for rc in cells); ys0 = min(cell_box(*rc)[1] for rc in cells)
    xs1 = max(cell_box(*rc)[2] for rc in cells); ys1 = max(cell_box(*rc)[3] for rc in cells)
    marker(c, loop_pts(xs0, ys0, xs1, ys1, k, seed))


# ------------------------------------------------------------------ type
def caption(c, lines, keys=(), y=1560, size=70, col=PLUM, center=True, loop_keys=True):
    """Nunito Black captions; key words circled by the gradient marker (drawn behind the letters)."""
    keys = {k.lower() for k in keys}
    for li, ln in enumerate(lines):
        ws = ln.split()
        ms = [_wmask(w_, N9, size) for w_ in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ws) - 1)
        x0 = W / 2 - tw / 2 if center else 70
        yy = y + li * size * 1.25
        spans, xx = [], x0
        for w_, m in zip(ws, ms):
            if w_.strip('.,…!?’').lower() in keys:
                spans.append([xx, xx + m.shape[1]])
            xx += m.shape[1] + size * 0.24
        if loop_keys and spans:
            groups = [spans[0]]
            for a_, b_ in spans[1:]:
                if a_ - groups[-1][1] < size * 0.5:
                    groups[-1][1] = b_
                else:
                    groups.append([a_, b_])
            for gi, (a_, b_) in enumerate(groups):
                pts = loop_pts(a_ - size * 0.1, yy - size * 0.5, b_ + size * 0.1, yy + size * 0.5, 1.0, seed=li * 7 + gi, pad=16)
                marker(c, pts, th=7)
        xx = x0
        for w_, m in zip(ws, ms):
            draw(c, blur_sprite(solid(m, (1, 1, 1, 1)), 10), xx + m.shape[1] / 2, yy + 3, opacity=0.7)
            draw(c, solid(m, col), xx + m.shape[1] / 2, yy)
            xx += m.shape[1] + size * 0.24


def pill(c, text, x, y, col=PURPLE, size=36):
    s = ts(text, N8, size, WHITE)
    w = s.shape[1] + 60
    draw(c, blur_sprite(tint(rrect(w, size * 1.9, size * 0.95, col), (0.3, 0.05, 0.2)), 14), x, y + 8, opacity=0.4)
    draw(c, F.grad_spr(w, size * 1.9, size * 0.95) if col is None else rrect(w, size * 1.9, size * 0.95, col), x, y)
    draw(c, s, x, y)


def pop(c, sp, x, y, size, rot=0, rays=True):
    sc = size / max(sp.shape[:2])
    if rays:
        F.pop(c, sp, x, y, sc, rays=True, col=ORANGE)
    else:
        F.drop(c, sp, x, y, sc, rot)


def hand(c, s, x, y, size=60, col=PURPLE, rot=0):
    draw(c, solid(_wmask(s, HAND, size), col), x, y, rot=rot)


def logo_small(c, x=930, y=150, w=210):
    lg = F.logo()
    draw(c, lg, x, y, scale=w / lg.shape[1])


def canvas():
    return F.canvas()


def ivory_veil(c, y0=1380, amt=0.9):
    g = np.clip((_Y - y0) / 220, 0, 1)[..., None] ** 1.2
    c[:] = c * (1 - amt * g) + np.array(IVORY[:3], np.float32) * amt * g


def top_veil(c, h=420, amt=0.6):
    g = np.clip(1 - _Y / h, 0, 1)[..., None] ** 1.5
    c[:] = c * (1 - amt * g) + np.array(IVORY[:3], np.float32) * amt * g


def put_card(c, img, x, y, w, h, rot=0, r=34):
    m = cv2.resize(R.sdf_fill(R.rrect_alpha(w, h, r, 2)), (w, h))
    pic = F.cover(img, 0.5, 0.5, 1.0, w, h)
    k = np.concatenate([pic * m[..., None], m[..., None]], 2).astype(np.float32)
    frame = rrect(w + 20, h + 20, r + 8, (1, 1, 1, 1))
    draw(c, blur_sprite(tint(frame, (0.3, 0.05, 0.2)), 26), x + 8, y + 24, rot=rot, opacity=0.45)
    draw(c, frame, x, y, rot=rot)
    draw(c, F.grade(k[..., :3]) if False else k, x, y, rot=rot)


WEEKEND = [(1, 5), (1, 6)]                 # 13 + 14
HOLIDAY = [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)]   # a school-holiday week
AGREED = [(2, 2), (2, 3), (2, 4), (2, 5)]  # another agreed span


# ------------------------------------------------------------------ scenes
def s01():   # "Fostering doesn't always mean every day."
    c = clip(4661, 0.45, fy=0.55)
    top_veil(c, 460, 0.55)
    g = np.clip((_Y - 1150) / 500, 0, 1)[..., None]
    c = c * (1 - 0.85 * g) + np.array(IVORY[:3], np.float32) * 0.85 * g
    pop(c, token('calendar'), 790, 980, 300)
    hand(c, 'Friday, 5:30pm', 270, 330, 64, PURPLE, rot=-4)
    logo_small(c)
    caption(c, ['Fostering doesn’t always', 'mean every day.'], keys=('every', 'day.'), y=1560, size=66)
    return c


def s02():   # "Respite care is planned for a short period."
    c = calendar_bg()
    fill_cells(c, WEEKEND, 0.7)
    circle_span(c, WEEKEND, seed=1)
    put_card(c, frame_of(17412, 0.6), 280, 300, 420, 300, rot=-4)
    hand(c, 'planned', 820, 300, 76, PURPLE, rot=-6)
    ivory_veil(c, 1380)
    caption(c, ['Respite care is planned', 'for a short period.'], keys=('planned',), y=1560, size=66)
    return c


def s03():   # "A weekend."
    c = calendar_bg()
    fill_cells(c, WEEKEND, 0.7)
    circle_span(c, WEEKEND, seed=1)
    put_card(c, frame_of(45511, 0.55), 300, 290, 400, 280, rot=3)
    pop(c, token('bag'), 820, 330, 300)
    x0, y0, x1, y1 = cell_box(*WEEKEND[0])
    pill(c, 'A weekend', (cell_box(*WEEKEND[0])[0] + cell_box(*WEEKEND[1])[2]) / 2, y1 + 60)
    ivory_veil(c, 1380)
    caption(c, ['A weekend.'], keys=('weekend',), y=1600, size=80)
    return c


def s04():   # "Part of a school holiday."
    c = calendar_bg()
    fill_cells(c, HOLIDAY, 0.7)
    circle_span(c, HOLIDAY, seed=2)
    pop(c, token('bucket'), 830, 330, 300)
    y1 = cell_box(*HOLIDAY[0])[3]
    pill(c, 'Part of a school holiday', 540, y1 + 60)
    ivory_veil(c, 1380)
    caption(c, ['Part of a school holiday.'], keys=('school', 'holiday'), y=1600, size=70)
    return c


def s05():   # "Or another agreed period."
    c = calendar_bg()
    fill_cells(c, AGREED, 0.7)
    circle_span(c, AGREED, seed=3)
    pop(c, token('clipboard'), 830, 320, 290)
    y1 = cell_box(*AGREED[0])[3]
    pill(c, 'Another agreed period', 600, y1 + 60)
    ivory_veil(c, 1380)
    caption(c, ['Or another agreed period.'], keys=('agreed',), y=1600, size=70)
    return c


def houses(c, rest=False):
    hx = [(300, 900), (790, 900)]
    lay = np.zeros((H, W), np.uint8)
    pts = [(300 + 490 * u, 900 - math.sin(u * math.pi) * 170) for u in np.linspace(0, 1, 60)]
    for i in range(0, 58, 3):
        cv2.line(lay, (int(pts[i][0] * 4), int(pts[i][1] * 4)), (int(pts[i + 1][0] * 4), int(pts[i + 1][1] * 4)), 255, 9 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + grad_col((_X - 300) / 490) * m
    hs = token('house')
    for i, (x, y) in enumerate(hx):
        sp = hs
        if rest and i == 0:
            sp = hs * np.array([0.72, 0.7, 0.85, 1.0], np.float32)
        F.drop(c, sp, x, y + 60, 300 / max(hs.shape[:2]))
    return hx


def s06():   # "It may support a child and their family,"
    c = canvas()
    hx = houses(c)
    hand(c, 'a family', 300, 680, 62, PURPLE, rot=-5)
    hand(c, 'you', 790, 680, 62, ORANGE, rot=4)
    pop(c, token('infinity'), 545, 700, 160, rays=False) if False else None
    logo_small(c)
    caption(c, ['It may support a child', 'and their family,'], keys=('family,', 'family'), y=1500, size=66)
    return c


def s07():   # "…or give another foster household time to rest."
    c = canvas()
    night = np.clip(1 - np.hypot(_X - 300, _Y - 900) / 520, 0, 1)[..., None] * 0.35
    c = c * (1 - night) + np.array([0.32, 0.22, 0.42], np.float32) * night
    hx = houses(c, rest=True)
    pop(c, token('moon'), 300, 640, 210, rays=False)
    put_card(c, frame_of(25377, 0.4), 760, 470, 360, 420, rot=4)
    hand(c, 'zzz', 400, 600, 60, PLUM, rot=-8)
    caption(c, ['or give another foster', 'household time to rest.'], keys=('rest.', 'rest'), y=1500, size=66)
    return c


def s08():   # "And it works best when it's the same home,"
    c = clip(21813, 0.2, fx=0.55)
    top_veil(c, 420, 0.5)
    g = np.clip((_Y - 1200) / 450, 0, 1)[..., None]
    c = c * (1 - 0.88 * g) + np.array(IVORY[:3], np.float32) * 0.88 * g
    pop(c, token('key'), 840, 1180, 240)
    logo_small(c)
    caption(c, ['And it works best when', 'it’s the same home,'], keys=('same', 'home,'), y=1540, size=66)
    return c


def mini_month(w, h, lit=True, seed=0):
    """A small calendar page (from the texture) with the same weekend circled."""
    tex = cv2.imread(f'{S}/tex/cal_blank.png')[..., ::-1].astype(np.float32) / 255
    sc = w / tex.shape[1]
    page = cv2.resize(tex, (w, int(tex.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    page = np.ascontiguousarray(page[:h])
    if lit:
        x0, y0, _, _ = GRID['cells']['1,5']
        _, _, x1, y1 = GRID['cells']['1,6']
        sub = page.copy()
        lay = np.zeros(page.shape[:2], np.float32)
        a, b = int(x0 * sc), int(y0 * sc)
        lay[b:int(y1 * sc), a:int(x1 * sc)] = 1
        uu = np.clip((np.arange(page.shape[1])[None, :] - a) / max(1, int(x1 * sc) - a), 0, 1)
        col = np.array(PURPLE[:3], np.float32) * (1 - uu[..., None]) + np.array(ORANGE[:3], np.float32) * uu[..., None]
        page = page * (1 - lay[..., None] * 0.7) + col * lay[..., None] * 0.7
        pts = loop_pts(x0 * sc, y0 * sc, x1 * sc, y1 * sc, 1.0, seed, pad=8)
        L = np.zeros(page.shape[:2], np.uint8)
        cv2.polylines(L, [(pts * 4).astype(np.int32)], False, 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = L.astype(np.float32)[..., None] / 255
        page = page * (1 - m) + np.array(PURPLE[:3], np.float32) * m
    a = np.ones(page.shape[:2] + (1,), np.float32)
    return np.concatenate([page, a], 2)


def s09():   # "time after time." — pages flip, the same weekend lights up each month
    c = canvas()
    for k in range(4):
        pg = mini_month(560, 600, True, seed=k)
        x, y = 540 + (3 - k) * 18, 860 - (3 - k) * 26
        rot = (3 - k) * -3.5
        draw(c, blur_sprite(tint(pg, (0.3, 0.05, 0.2)), 20), x + 8, y + 22, rot=rot, opacity=0.35)
        draw(c, pg, x, y, rot=rot)
    # a page mid-flip (squashed vertically, fading)
    pg = mini_month(560, 600, True, seed=9)
    flip = cv2.resize(pg, (560, 200))
    draw(c, flip, 540, 420, opacity=0.6)
    hand(c, 'again', 860, 420, 70, ORANGE, rot=8)
    hand(c, 'and again', 250, 1270, 64, PURPLE, rot=-5)
    caption(c, ['the same home,', 'time after time.'], keys=('time', 'after'), y=1520, size=72)
    return c


def s10():   # "Although the time is short, consistency matters."
    c = canvas()
    xs = 540
    ys = [420, 620, 820, 1020, 1220]
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (xs * 4, ys[0] * 4), (xs * 4, ys[-1] * 4), 255, 5 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + grad_col((_Y - ys[0]) / (ys[-1] - ys[0])) * m
    for i, y in enumerate(ys):
        chip = F.grad_spr(300, 120, 60, phase=i * 0.1)
        draw(c, blur_sprite(tint(chip, (0.3, 0.05, 0.2)), 16), xs + 6, y + 14, opacity=0.4)
        draw(c, chip, xs, y)
        draw(c, ts('S   S', N9, 50, WHITE), xs, y)
        draw(c, rrect(16, 16, 8, ORANGE), xs - 210, y)
    hand(c, 'every month', 230, 700, 60, PURPLE, rot=-8)
    caption(c, ['Although the time is short,', 'consistency matters.'], keys=('consistency',), y=1500, size=66)
    return c


def s11():   # end card
    c = canvas()
    lg = F.logo()
    draw(c, lg, W / 2, 520, scale=700 / lg.shape[1])
    hand(c, 'one weekend at a time', W / 2, 720, 76, ORANGE, rot=-3)
    btn = F.grad_spr(820, 130, 65)
    draw(c, blur_sprite(btn, 24), W / 2, 960 + 20, opacity=0.55)
    draw(c, btn, W / 2, 960)
    F.text_arrow(c, 'Ask us about respite fostering', W / 2, 960, size=46)
    draw(c, ts('0161 241 1332', N9, 64, PURPLE), W / 2, 1130)
    draw(c, ts('organicfostering.co.uk', N8, 40, PLUM), W / 2, 1210)
    s = ts('Rated Good by Ofsted', N7, 32, PLUM)
    F.drop(c, rrect(s.shape[1] + 110, 70, 35, (1, 1, 1, 0.95)), W / 2, 1330, sh=0.25)
    draw(c, F.star(), W / 2 - s.shape[1] / 2 - 10, 1330)
    draw(c, s, W / 2 + 20, 1330)
    pop(c, token('calendar'), 860, 1560, 220, rays=False)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.08, grain=0.01, vig=0.15))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 6:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 6]) for i in range(0, len(th), 6)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
