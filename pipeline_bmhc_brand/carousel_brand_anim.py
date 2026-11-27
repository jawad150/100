"""Moving version of the BMHC brand identity carousel: 6 x 5 s video slides (1080x1350, 30 fps). Elements animate in
with 3D perspective tilts and flips, and real 3D turntables (lantern, rings, radio, ball) spin and float.
-> reel/bmhc/brand_identity_carousel/slide_1..6.mp4 + swipe_preview.mp4"""
import os, math, subprocess, functools
import numpy as np
import cv2
import carousel_brand as CB
from carousel_brand import (W, H, MAG, TEAL, ORANGE, LIME, INK, SLATE, STONE, MIST, WHITE, text, paste, rot, rmask, shadowed,
                            card_from, photo, ground, marks, header, tag, logo_white, logo_colour, building_mark, F, WR, BENTO, AYAH)

FPS, DUR = 30, 5.0
NFR = int(FPS * DUR)
ROOT = CB.ROOT
TURN = f'{ROOT}/workspace_brandcar/turn'
OUT = CB.OUT


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_back(u, s=1.7):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


def e_inout(u):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def persp(spr, ry=0.0, rx=0.0, s=1.0, f=1600.0):
    """Rotate a flat sprite in 3D (degrees about its vertical / horizontal axis) and project it."""
    h, w = spr.shape[:2]
    pts = np.array([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], np.float32) * s
    a, b = math.radians(ry), math.radians(rx)
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]], np.float32)
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]], np.float32)
    P = pts @ (Rx @ Ry).T
    z = P[:, 2] + f
    proj = np.stack([P[:, 0] * f / z, P[:, 1] * f / z], 1)
    D = int(max(w, h) * s * 1.5) + 8
    dst = proj + D / 2
    M = cv2.getPerspectiveTransform(np.array([(0, 0), (w, 0), (w, h), (0, h)], np.float32), dst.astype(np.float32))
    return cv2.warpPerspective(spr, M, (D, D), flags=cv2.INTER_LINEAR)


@functools.lru_cache(maxsize=256)
def turn_frame(name, i, size):
    im = cv2.imread(f'{TURN}/{name}/{i:04d}.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    solid = (im[..., 3] > 0.5).astype(np.uint8)
    keep = np.clip(cv2.GaussianBlur(cv2.dilate(solid, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.0) * 1.2, 0, 1)
    im[..., 3] *= keep
    sc = size / im.shape[0]
    im = cv2.resize(im, (int(im.shape[1] * sc), int(im.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


def spin(c, name, x, y, size, t, t0=0.0, speed=16, phase=0, bob=10):
    """A real 3D turntable object that pops in, then spins and floats."""
    u = (t - t0) / 0.5
    if u <= 0 or not os.path.isdir(f'{TURN}/{name}'):
        return
    n = len(os.listdir(f'{TURN}/{name}'))
    i = int(t * speed + phase) % n
    sp = turn_frame(name, i, size)
    s = e_back(clamp(u), 1.8)
    if abs(s - 1) > 1e-3:
        sp = cv2.resize(sp, (max(1, int(sp.shape[1] * s)), max(1, int(sp.shape[0] * s))), interpolation=cv2.INTER_LINEAR)
    paste(c, shadowed(sp, 14, 22, 0.25), x, y + bob * math.sin(t * 2.2 + phase), clamp(u * 3), 'c')


def slide_in(c, spr, x, y, t, t0, dx=0, dy=60, dur=0.55, anchor='tl'):
    u = (t - t0) / dur
    if u <= 0:
        return
    k = e_out(u)
    paste(c, spr, x + dx * (1 - k), y + dy * (1 - k), clamp(u * 2), anchor)


def card3d(c, cd, x, y, t, t0, r=0.0, wob=7.0, phase=0.0, fly=500):
    """A mockup card that flies up with a 3D tilt, then keeps a gentle 3D wobble."""
    u = (t - t0) / 0.7
    if u <= 0:
        return
    k = e_out(u)
    ry = wob * math.sin(t * 1.3 + phase) + 50 * (1 - k)
    rx = 4 * math.sin(t * 1.1 + phase * 1.7) - 30 * (1 - k)
    sp = persp(shadowed(cd, 20, 18, 0.33), ry, rx)
    sp = rot(sp, r * k)
    paste(c, sp, x, y + fly * (1 - k), clamp(u * 2), 'c')


# ------------------------------------------------------------------ slides
@functools.lru_cache(None)
def cover_bg():
    c = photo('1-BMHC-web.jpg', int(W * 1.12), int(H * 1.12), 0.5, 0.35, 1.25)
    g = (c * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    return c * 0.45 + g * np.array((0.62, 0.78, 0.86), np.float32) * 0.62


def s1(t):
    bg = cover_bg()
    z = 1 + 0.05 * t / DUR
    M = cv2.getRotationMatrix2D((bg.shape[1] / 2, bg.shape[0] / 2), 0, z)
    M[0, 2] -= (bg.shape[1] - W) / 2
    M[1, 2] -= (bg.shape[0] - H) / 2
    c = cv2.warpAffine(bg, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    c = c * (1 - 0.7 * np.clip((yy - 950) / 400, 0, 1)) * (1 - 0.25 * np.clip(1 - yy / 560, 0, 1))
    marks(c, WHITE)
    header(c, 'Visual identity', WHITE)
    slide_in(c, text('Brand', 400, 150, tuple(WHITE), -0.03), 54, 120, t, 0.15, dx=-300, dy=0)
    sp = text('Identity', 800, 150, tuple(WHITE), -0.03)
    slide_in(c, sp, W - 54 - sp.shape[1], 370 - sp.shape[0] / 2, t, 0.35, dx=300, dy=0)
    for i, s in enumerate(('DIGITAL & SOCIAL', 'EDITION · V1.0')):
        slide_in(c, text(s, 500, 22, tuple(WHITE), 0.1), 58, 470 + i * 30, t, 0.7 + 0.1 * i, dy=20)
    for i, s in enumerate(('BRITISH MUSLIM', 'HERITAGE CENTRE', 'WHALLEY RANGE')):
        sp = text(s, 500, 22, tuple(WHITE), 0.1)
        slide_in(c, sp, W - 58 - sp.shape[1], 480 + i * 30 - sp.shape[0] / 2, t, 0.75 + 0.1 * i, dy=20)
    cards = [card_from(BENTO, 300, 10, 8), card_from(WR(174), 236, 10, 8), card_from(AYAH, 300, 10, 8, crop=(4, 4, 565, 700))]
    for i, (x, cd, r) in enumerate(zip((200, 540, 880), cards, (-4, 0, 4))):
        card3d(c, cd, x, 840, t, 0.9 + 0.18 * i, r, phase=i * 1.3)
    spin(c, 'lantern', 110, 660, 190, t, 1.8, phase=0)
    spin(c, 'rings', 975, 660, 160, t, 2.0, phase=20)
    paste(c, logo_white(330), W / 2, 1200, clamp((t - 1.4) / 0.5), 'c')
    paste(c, text('bmhc.org.uk', 500, 24, tuple(WHITE)), W - 70, 1290, clamp((t - 1.6) / 0.5), 'r')
    return c


def s2(t):
    c = ground(STONE)
    marks(c, INK)
    header(c, 'Visual identity', INK)
    u = clamp(t / 0.4)
    if u > 0:
        tag(c, 'ART DIRECTION', 60 - 40 * (1 - e_out(u)), 100)
    slide_in(c, text('Ink, white, one pillar colour, four bars.', 500, 28, tuple(SLATE)), 60, 165, t, 0.25, dy=20)
    pieces = [(BENTO, 470, None, 330, 560, -3), (WR(315), 240, None, 830, 450, 4), (WR(435), 240, None, 850, 905, -3),
              (AYAH, 330, (4, 4, 565, 700), 290, 1060, 3), (None, 230, None, 590, 1135, -2)]
    for i, (path, w, crop, x, y, r) in enumerate(pieces):
        if path is None:
            ph = photo('Dut-kbsW4AIRs6T.jpg', w, int(w * 1.15), 0.5, 0.0, 1.5)
            m = np.ones(ph.shape[:2], np.float32)
            cd = np.dstack([cv2.copyMakeBorder(ph, 12, 50, 12, 12, cv2.BORDER_CONSTANT, value=(1, 1, 1)),
                            cv2.copyMakeBorder(m, 12, 50, 12, 12, cv2.BORDER_CONSTANT, value=1)])
        else:
            cd = card_from(path, w, 12, 0, crop)
        card3d(c, cd, x, y, t, 0.4 + 0.22 * i, r, wob=5, phase=i, fly=700)
    spin(c, 'ball', 960, 1250, 140, t, 1.7, phase=10)
    return c


def flip_in(c, spr, x, y, t, t0):
    """Swatch card flips into place (3D rotation about its horizontal axis)."""
    u = (t - t0) / 0.6
    if u <= 0:
        return
    k = e_back(clamp(u), 1.2)
    rx = 90 * (1 - k)
    sp = persp(spr, 0, rx)
    paste(c, sp, x + spr.shape[1] / 2, y + spr.shape[0] / 2, clamp(u * 3), 'c')


@functools.lru_cache(None)
def colour_bg():
    c = photo('bhmc-f.png', W, H, 0.5, 0.4, 1.3)
    g = (c * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    return (c * 0.35 + g * 0.65) * 0.55


def s3(t):
    c = colour_bg().copy()
    marks(c, WHITE)
    header(c, 'Visual identity', WHITE)
    tag(c, 'PILLAR COLOURS', 60, 100, inv=True)
    sw_w, sw_h = 470, 300
    items = [(MAG, 'Heritage Magenta', 'HEART WORK', '#E60585', '230 5 133', '0 98 42 10', WHITE),
             (TEAL, 'Heritage Teal', "QUR'AN IN FOCUS", '#2DC892', '45 200 146', '77 0 27 22', INK),
             (ORANGE, 'Heritage Orange', 'PRODUCTIVITY', '#FF4200', '255 66 0', '0 74 100 0', INK),
             (LIME, 'Heritage Lime', 'SUNNAH DAILY HABITS', '#69FF00', '105 255 0', '59 0 100 0', INK)]
    for i, it in enumerate(items):
        x = 60 + (i % 2) * (sw_w + 20)
        y = 160 + (i // 2) * (sw_h + 20)
        flip_in(c, CB.swatch(*it[:6], sw_w, sw_h, it[6]), x, y, t, 0.3 + 0.2 * i)
    if t > 1.2:
        tag(c, 'NEUTRALS', 60, 820, inv=True)
    neu = [(INK, 'Ink', 'TEXT · STORIES', '#0B0B0B', '11 11 11', '0 0 0 96', WHITE),
           (STONE, 'Stone', 'LINES', '#E9E6DF', '233 230 223', '0 1 5 9', INK),
           (MIST, 'Mist', 'PANELS', '#F6F5F1', '246 245 241', '0 0 2 4', INK)]
    nw = int((960 - 40) / 3)
    for i, it in enumerate(neu):
        flip_in(c, CB.swatch(*it[:6], nw, 300, it[6]), 60 + i * (nw + 20), 880, t, 1.3 + 0.18 * i)
    paste(c, text('Values as published in the BMHC Digital & Social Brand Guidelines v1.0', 500, 20, tuple(WHITE * 0.8)), 60, 1205, clamp((t - 2) / 0.5))
    paste(c, text('BMHC', 800, 30, tuple(WHITE), 0.12), W / 2, 1290, 1, 'c')
    return c


def sheen(spr, u):
    """A diagonal light sweep across a sprite (u 0..1)."""
    h, w = spr.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = xx * 0.8 + yy * 0.6 - (-200 + (w + 400) * u)
    g = np.exp(-(d / 60) ** 2)[..., None] * 0.6 * spr[..., 3:4]
    out = spr.copy()
    out[..., :3] = np.clip(out[..., :3] + g, 0, 1)
    return out


def s4(t):
    c = np.ones((H, W, 3), np.float32) * WHITE
    c[:H // 2] = INK
    marks(c, MIST)
    header(c, 'Visual identity', WHITE)
    tag(c, 'PRIMARY LOGO', W / 2 - 110, 110, inv=True)
    lg = logo_white(720)
    u = clamp((t - 0.2) / 0.6)
    if u > 0:
        sp = sheen(lg, clamp((t - 0.9) / 1.0)) if 0.9 < t < 1.9 else lg
        sp = persp(sp, 18 * (1 - e_out(u)) + 3 * math.sin(t * 1.2), 0, 0.92 + 0.08 * e_out(u))
        paste(c, sp, W / 2, 400, u, 'c')
    tag(c, 'BUILDING MARK', W / 2 - 115, H // 2 + 60)
    bm = building_mark(560)
    v = clamp((t - 1.2) / 1.4)                                            # the building draws itself on, left to right
    if v > 0:
        m = np.clip((v * (bm.shape[1] + 60) - np.arange(bm.shape[1], dtype=np.float32)) / 60, 0, 1)
        paste(c, bm * m[None, :, None], W / 2, H // 2 + 330, 1, 'c')
    for i, col in enumerate((MAG, TEAL, ORANGE, LIME)):
        k = e_out(clamp((t - 2.6 - 0.1 * i) / 0.4))
        x0 = W / 2 - 280 + 140 * i
        if k > 0:
            c[H // 2 + 470:H // 2 + 484, int(x0):int(x0 + (136) * k)] = col
    paste(c, text('Reversed on ink · colour on white · never redrawn', 500, 22, tuple(SLATE)), W / 2, H - 70, clamp((t - 3) / 0.5), 'c')
    return c


def s5(t):
    tint = WHITE * 0.86 + MAG * 0.14
    c = ground(tint)
    marks(c, INK)
    header(c, 'Visual identity', INK)
    tag(c, 'TYPOGRAPHY', 60, 100)
    rows = [('SUBHEADLINE', 230, [(text('Inter Bold, sentence case', 700, 30, tuple(INK)), 230)]),
            ('HEADLINE', 330, [(text('ONE VERSE.', 800, 74, tuple(INK), 0.02), 300), (text('ONE ACTION.', 800, 74, tuple(MAG), 0.02), 380)]),
            ('BODY', 480, [(text('Body copy reads like this. Inter Regular,', 400, 28, tuple(INK)), 470),
                           (text('line height 1.4, never below 28 px.', 400, 28, tuple(INK)), 510)])]
    for i, (lab, y, items) in enumerate(rows):
        t0 = 0.2 + 0.35 * i
        if t > t0:
            CB.spec_row(c, lab, y)
        for j, (sp, yy) in enumerate(items):
            slide_in(c, sp, 360, yy - sp.shape[0] / 2, t, t0 + 0.12 * j, dx=80, dy=0)
    if t > 1.2:
        tag(c, 'PHOTOGRAPHY', 60, 600)
    grid = [('1-BMHC-web.jpg', 0.5, 0.45, 1.6), ('bhmc-f.png', 0.5, 0.35, 1.0), ('Dut-kbsW4AIRs6T.jpg', 0.5, 0.05, 1.3),
            ('bhmc-f.png', 0.15, 0.6, 2.2), ('1-BMHC-web.jpg', 0.85, 0.7, 2.4), ('Dut-kbsW4AIRs6T.jpg', 0.5, 0.3, 2.2)]
    cw, ch = 300, 262
    for i, (n, fx, fy, z) in enumerate(grid):
        ph = photo(n, cw, ch, fx, fy, z)
        m = rmask(cw, ch, 18)
        cd = np.dstack([ph * m[..., None], m])
        x = 60 + (i % 3) * (cw + 30) + cw / 2
        y = 680 + (i // 3) * (ch + 26) + ch / 2
        u = (t - (1.3 + 0.15 * i)) / 0.55
        if u > 0:
            k = e_back(clamp(u), 1.5)
            sp = persp(shadowed(cd, 14, 10, 0.22), 35 * (1 - e_out(u)) + 3 * math.sin(t + i), -20 * (1 - e_out(u)), max(0.05, k))
            paste(c, sp, x, y, clamp(u * 3), 'c')
    paste(c, text('The building, objects and places. No identifiable under-18s.', 500, 22, tuple(SLATE)), 60, 1282, clamp((t - 2.5) / 0.5), 'l')
    return c


def s6(t):
    c = ground(MIST)
    marks(c, INK)
    header(c, 'Visual identity', INK)
    cards = [card_from(BENTO, 250, 10, 6), card_from(WR(315), 196, 10, 6), card_from(WR(435), 196, 10, 6), card_from(WR(1080), 196, 10, 6)]
    for i, (x, cd, r) in enumerate(zip((180, 430, 650, 880), cards, (-5, -1, 2, 5))):
        card3d(c, cd, x, 330, t, 0.15 + 0.15 * i, r, wob=6, phase=i, fly=-500)
    slide_in(c, text('Now you can read our feed by colour.', 500, 38, tuple(INK)), W / 2, 640, t, 0.8, dy=20, anchor='c')
    for j, (s, col, y) in enumerate((('Five themes.', INK, 760), ('One centre.', MAG, 890))):
        u = (t - (1.1 + 0.25 * j)) / 0.4
        if u > 0:
            sp = text(s, 900, 120, tuple(col), -0.03)
            sc = 1 + 0.35 * (1 - e_back(clamp(u), 2.2))
            sp = cv2.resize(sp, (int(sp.shape[1] * sc), int(sp.shape[0] * sc)), interpolation=cv2.INTER_LINEAR)
            paste(c, sp, W / 2, y, clamp(u * 2.5), 'c')
    chips = [('HEART', MAG, WHITE), ("QUR'AN", TEAL, INK), ('PRODUCTIVITY', ORANGE, INK), ('SUNNAH', LIME, INK), ('STORIES', INK, WHITE)]
    widths = [F(700, 22).getlength(s) + 44 for s, _, _ in chips]
    x = W / 2 - (sum(widths) + 12 * 4) / 2
    for i, ((s, bg, fg), w) in enumerate(zip(chips, widths)):
        u = (t - (1.7 + 0.12 * i)) / 0.4
        if u > 0:
            m = rmask(w, 50, 25)
            chip = np.dstack([m[..., None] * bg, m])
            paste(chip, text(s, 700, 22, tuple(fg), 0.08), w / 2, 25, 1, 'c')
            k = e_back(clamp(u), 2)
            chip = cv2.resize(chip, (max(1, int(chip.shape[1] * k)), max(1, int(chip.shape[0] * k))))
            paste(c, chip, x + w / 2, 1025, clamp(u * 3), 'c')
        x += w + 12
    if t > 2.5:
        tt = text('SAVE THIS POST', 500, 28, tuple(WHITE), 0.12)
        bw_, bh_ = tt.shape[1] + 60, tt.shape[0] + 34
        box = np.dstack([np.ones((bh_, bw_, 3), np.float32) * INK, np.ones((bh_, bw_), np.float32)])
        paste(box, tt, 30, 17)
        s = 1 + 0.04 * max(0, math.sin((t - 2.5) * 4))
        box = cv2.resize(box, (int(bw_ * s), int(bh_ * s)))
        paste(c, box, W / 2, 1125, clamp((t - 2.5) / 0.3), 'c')
    paste(c, text('Follow @thebmhc for weekly reminders', 500, 28, tuple(SLATE)), W / 2, 1205, clamp((t - 2.8) / 0.4), 'c')
    paste(c, logo_colour(250), W / 2, 1290, clamp((t - 3.0) / 0.4), 'c')
    spin(c, 'radio', 95, 820, 150, t, 1.5, phase=5)
    spin(c, 'lantern', 990, 820, 170, t, 1.6, phase=30)
    return c


SLIDES = [s1, s2, s3, s4, s5, s6]


def render(i):
    d = f'{ROOT}/workspace_brandcar/anim/s{i}'
    os.makedirs(d, exist_ok=True)
    for f in range(NFR):
        c = CB.grain(np.clip(SLIDES[i](f / FPS), 0, 1), 0.022)
        cv2.imwrite(f'{d}/{f:04d}.png', (c[..., ::-1] * 255 + 0.5).astype(np.uint8))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{d}/%04d.png', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{OUT}/slide_{i + 1}.mp4'], check=True)
    print('slide', i + 1, flush=True)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'still':
        for a in sys.argv[2:]:
            i, ts = a.split(':')
            c = CB.grain(np.clip(SLIDES[int(i)](float(ts)), 0, 1), 0.022)
            cv2.imwrite(f'{ROOT}/workspace_brandcar/still_{i}_{ts}.png', (c[..., ::-1] * 255 + 0.5).astype(np.uint8))
    else:
        for i in map(int, sys.argv[1:]):
            render(i)
