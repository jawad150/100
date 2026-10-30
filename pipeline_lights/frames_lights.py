"""Scene images for BMHC "Lights On" — people version (after the client's concept PDF).

One day in the 1843 building, Fajr to Isha. Every room appears the moment its light switches on, now with the people who
use it. Running devices: a day dial along the top (Fajr · Dhuhr · Asr · Maghrib · Isha), a little building icon whose
windows light up one by one, room-name pills, and a 3D object for every room the voice names.

Kept from BMHC's guidelines: no depiction of the Prophet ﷺ; Qur'ans only closed and cloth-covered on a stand; no AI
recitation or adhan; no musical instruments on screen or in the sound.

Usage: python3 frames_lights.py [n ...] -> workspace_lights/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_bmhc'))
import numpy as np
import cv2
import frames_bmhc as F
from frames_bmhc import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, _wmask, GREEN_D, IVORY,
                         TEAL, GOLD, MAG, ORANGE, GREEN, WHITE, BARS, PB, PX, PS, PM, PR)

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_lights'))
OUT = f'{S}/frames'
_X, _Y = R._X, R._Y
WARM = (1.0, 0.78, 0.42)
# window boxes on bhmc-f.png at the default 9:16 cover crop: (cx, cy, w, h)
WINDOWS = [(490, 345, 60, 110), (490, 660, 110, 130), (490, 910, 110, 170), (310, 1040, 30, 160), (670, 1040, 30, 160),
           (60, 1000, 50, 70), (205, 995, 50, 70), (780, 995, 50, 70), (905, 995, 50, 70), (60, 1165, 60, 120),
           (205, 1160, 60, 120), (780, 1160, 60, 120)]
PRAYERS = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']


# ------------------------------------------------------------------ sources
def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return F.cover(im[..., ::-1].astype(np.float32) / 255, fx, fy, z, w, h)


def photo(name, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    return F.photo(name, fx=fx, fy=fy, z=z, w=w, h=h, g=False)


def prop(name):
    for d in (f'{S}/assets', f'{F.S}/assets'):
        p = f'{d}/{name}.png'
        if os.path.exists(p):
            return load_png_sprite(p)
    raise FileNotFoundError(name)


# ------------------------------------------------------------------ light grades
def warm(im, k=1.0):
    """Lights on: warm, gentle lift."""
    lum = im.mean(2, keepdims=True)
    out = np.clip(im * (1 + 0.08 * k) + np.array([0.05, 0.025, -0.02], np.float32) * k * (0.4 + lum), 0, 1)
    return out


def dawn(im):
    lum = im.mean(2, keepdims=True)
    return np.clip(im * 0.62 + lum * 0.18 + np.array([0.02, 0.07, 0.17], np.float32), 0, 1)


def night(im):
    lum = im.mean(2, keepdims=True)
    out = im * 0.18 + lum * 0.1 + np.array([0.02, 0.05, 0.14], np.float32)
    sky = np.clip(1 - _Y / 900, 0, 1)[..., None] * (lum > 0.55)
    return np.clip(out + sky * np.array([0.0, 0.03, 0.12], np.float32), 0, 1)


def lamp_light(c, x, y, r=520, amt=0.55, col=WARM):
    """A pool of warm light from a lamp at (x, y): brightens what's near, like a light just switched on."""
    d = np.hypot(_X - x, _Y - y) / r
    g = np.exp(-d * d * 1.6)[..., None]
    c[:] = np.clip(c * (1 + amt * g) + np.array(col, np.float32) * g * amt * 0.35, 0, 1)


def light_windows(c, src, n=None, amt=1.0):
    """Warm glowing windows on the facade; texture keeps the mullions."""
    lay = np.zeros((H, W), np.float32)
    for (cx, cy, w, h) in WINDOWS[:n]:
        cv2.rectangle(lay, (int(cx - w / 2), int(cy - h / 2)), (int(cx + w / 2), int(cy + h / 2)), 1.0, -1)
    lay = cv2.GaussianBlur(lay, (0, 0), 2)
    tex = 0.55 + 0.45 * np.clip(src.mean(2) * 1.6, 0, 1)
    m = (lay * tex * amt)[..., None]
    c[:] = c * (1 - m) + np.array(WARM, np.float32) * m * 1.1
    glow = cv2.GaussianBlur(lay, (0, 0), 30)[..., None] * 0.55 * amt
    c[:] = np.clip(c + glow * np.array([1.0, 0.65, 0.3], np.float32), 0, 1)


def ceiling_rows(c, rows=3, y0=120, amt=0.9):
    """Rows of ceiling lights fading up (Fajr)."""
    for j in range(rows):
        y = y0 + j * 90
        for i in range(5):
            x = 140 + i * 200 + (j % 2) * 40
            g = np.exp(-(((_X - x) / 60) ** 2 + ((_Y - y) / 18) ** 2))[..., None] * amt
            c[:] = np.clip(c + g * np.array([1.0, 0.92, 0.75], np.float32), 0, 1)


# ------------------------------------------------------------------ overlays
def day_dial(c, k, y=150, light=True):
    """Fajr → Isha track along the top; a sun/moon marker at position k (0..1)."""
    x0, x1 = 120, 960
    ink = (1, 1, 1, 0.9) if light else (0.07, 0.18, 0.16, 0.85)
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (x0 * 4, y * 4), (x1 * 4, y * 4), 255, 3 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.55
    c[:] = c * (1 - m) + np.array(ink[:3], np.float32) * m
    for j, p in enumerate(PRAYERS):
        x = x0 + (x1 - x0) * j / 4
        draw(c, rrect(12, 12, 6, ink), x, y)
        s = ts(p.upper(), PS, 20, ink, 0.14)
        draw(c, s, x, y + 32)
    mx = x0 + (x1 - x0) * k
    moon = k > 0.8 or k < 0.05
    col = (0.95, 0.95, 1.0, 1) if moon else GOLD
    draw(c, blur_sprite(rrect(60, 60, 30, (*col[:3], 0.6)), 10), mx, y)
    draw(c, rrect(34, 34, 17, col), mx, y)


def building_icon(c, lit, x=950, y=270, sc=1.0, light=True):
    """A tiny facade (tower + wings) with 9 windows; `lit` of them glow."""
    w, h = int(150 * sc), int(120 * sc)
    spr = np.zeros((h + 10, w + 10, 4), np.float32)
    ink = (1, 1, 1, 0.85) if light else (*GREEN_D[:3], 0.85)
    body = np.zeros((h + 10, w + 10), np.uint8)
    cv2.rectangle(body, (5, int(h * 0.45)), (w + 5, h + 5), 255, -1)
    cv2.rectangle(body, (int(w * 0.38), 5), (int(w * 0.62), h + 5), 255, -1)
    spr = solid(body.astype(np.float32) / 255 * 0.25, ink)
    k = 0
    for (fx, fy) in ((0.5, 0.18), (0.5, 0.38), (0.5, 0.6), (0.13, 0.62), (0.25, 0.62), (0.75, 0.62), (0.87, 0.62), (0.13, 0.84), (0.87, 0.84)):
        on = k < lit
        col = (1.0, 0.8, 0.4, 1) if on else (1, 1, 1, 0.35) if light else (*GREEN_D[:3], 0.3)
        paste_spr(spr, rrect(12 * sc, 15 * sc, 2, col), fx * w + 5, fy * h + 5)
        k += 1
    if lit:
        draw(c, blur_sprite(rrect(w, h * 0.7, 20, (1.0, 0.75, 0.35, 0.35)), 14), x, y + 10)
    draw(c, spr, x, y)


def room_pill(c, text, x=None, y=1500, dark=False):
    s = ts(text.upper(), PS, 30, GREEN_D if not dark else IVORY, 0.12)
    w = s.shape[1] + 60
    x = W / 2 if x is None else x
    fill = (*IVORY[:3], 0.95) if not dark else (*GREEN_D[:3], 0.85)
    draw(c, blur_sprite(rrect(w, 66, 33, (0, 0, 0, 0.5)), 12), x + 4, y + 10, opacity=0.5)
    draw(c, rrect(w, 66, 33, fill), x, y)
    draw(c, s, x, y)


def cap_text(c, lines, y=1660, size=64, hl=()):
    """PDF caption style: Poppins Bold, white, soft shadow; key words in gold."""
    for li, line in enumerate(lines):
        words = line.split(' ')
        sprs = [solid(_wmask(w, 'Poppins-Bold', size), GOLD if w.strip('.,!?').lower() in hl else WHITE) for w in words]
        total = sum(s.shape[1] for s in sprs) + size * 0.22 * (len(sprs) - 1)
        x = W / 2 - total / 2
        yy = y + li * size * 1.25
        for s in sprs:
            draw(c, blur_sprite(tint(s, (0, 0, 0)), 12), x + s.shape[1] / 2 + 2, yy + 6, opacity=0.7)
            draw(c, s, x + s.shape[1] / 2, yy)
            x += s.shape[1] + size * 0.22


def switch_pop(c, x, y, on=True, sc=0.32):
    F.pop(c, prop('switch_on' if on else 'switch_off'), x, y, sc, rays=on, col=GOLD)


def bottom(c, amt=0.75, top=0.55):
    g = np.clip((_Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    return c * (1 - amt * g) + np.array([0.03, 0.07, 0.06], np.float32) * amt * g


def topfade(c, h=0.2, amt=0.55):
    g = np.clip(1 - _Y / (H * h), 0, 1)[..., None] ** 1.5
    return c * (1 - amt * g)


# ------------------------------------------------------------------ scenes
def s01():   # "Every day, people walk through these gates."
    c = warm(photo('W6A9208-1-scaled.jpg', 0.52, 0.5), 0.6)
    c = bottom(topfade(c))
    day_dial(c, 0.22)
    F.tag(c, 'COLLEGE ROAD · WHALLEY RANGE', 70, 290, icon='pin')
    cap_text(c, ['Every day, people walk', 'through these gates.'], hl=('gates.',))
    return c


def s02():   # "This building went up in 1843, as a college."  (blue hour, one window glows)
    src = photo('bhmc-f.png', 0.5, 0.5)
    c = night(src) * 1.6
    c = np.clip(c, 0, 1)
    light_windows(c, src, n=2)
    c = bottom(c, 0.6)
    s = ts('1843', PB, 300, GOLD)
    draw(c, blur_sprite(tint(s, (0, 0, 0)), 20), W / 2 + 8, 1330, opacity=0.6)
    draw(c, s, W / 2, 1320)
    F.chip(c, 'Grade II* listed', W / 2, 1490, fill=IVORY, ink=GREEN_D, size=38)
    old = F.photo('BMHC-Year-1866.jpg', fx=0.55, fy=0.5, w=420, h=290, g=False)
    old = old.mean(2, keepdims=True) * np.array([1.0, 0.94, 0.82], np.float32)
    card = rrect(444, 314, 24, IVORY).copy()
    paste_spr(card, F.sprite_of(old, 16), 222, 157)
    F.drop(c, card, 800, 560, rot=5)
    building_icon(c, 1, light=True)
    cap_text(c, ['This building went up in', '1843, as a college.'], y=1680, hl=('1843,', 'college.'))
    return c


def s03():   # "Today, it's still a place of learning!"  (door lamp on)
    c = photo('1-BMHC-web.jpg', 0.5, 0.5)
    c = c * 0.72
    lamp_light(c, 540, 1300, 560, 0.9)
    lamp_light(c, 138, 1220, 200, 0.9)
    c = warm(c)
    c = bottom(topfade(c), 0.7, 0.6)
    day_dial(c, 0.08)
    F.pop(c, prop('bulb'), 540, 1060, 0.42, col=GOLD)
    building_icon(c, 2)
    room_pill(c, 'Still a place of learning', y=1470)
    cap_text(c, ["Today, it's still a", 'place of learning!'], y=1640, hl=('learning!',))
    return c


def s04():   # "Before sunrise, the first lights come on for Fajr."
    src = photo('MAS09785-scaled.jpg', 0.5, 0.45)
    c = dawn(src)
    ceiling_rows(c, 3, 140, 0.8)
    lamp_light(c, 540, 300, 700, 0.45, (0.85, 0.9, 1.0))
    c = bottom(c, 0.7)
    day_dial(c, 0.0)
    switch_pop(c, 880, 560)
    building_icon(c, 3)
    room_pill(c, 'Daily prayers', y=1470)
    cap_text(c, ['Before sunrise, the first', 'lights come on for Fajr.'], y=1640, hl=('fajr.',))
    return c


def s05():   # "Then the classrooms, for Qur'an classes, and GCSE Islamic Studies."
    c = warm(photo('Screenshot-2025-10-26-033526.png', 0.3, 0.5))
    lamp_light(c, 300, 300, 700, 0.35)
    c = bottom(topfade(c), 0.75, 0.5)
    day_dial(c, 0.25)
    F.pop(c, prop('rehal'), 830, 600, 0.5, col=GOLD)
    building_icon(c, 4)
    room_pill(c, "Qur'an classes", x=330, y=1380)
    room_pill(c, 'GCSE Islamic Studies', x=640, y=1470)
    cap_text(c, ["Then the classrooms, for Qur'an", 'classes and GCSE Islamic Studies.'], y=1640, size=56, hl=("qur'an", 'gcse'))
    return c


def s06():   # "The sports hall, for taekwondo."
    c = warm(clip(48142, 0.75, fx=0.55, fy=0.5))
    c = bottom(topfade(c), 0.7, 0.6)
    day_dial(c, 0.45)
    F.pop(c, prop('belt'), 860, 620, 0.5, col=GOLD)
    building_icon(c, 5)
    room_pill(c, 'Taekwondo', y=1470)
    cap_text(c, ['The sports hall,', 'for taekwondo.'], y=1640, hl=('taekwondo.',))
    return c


def s07():   # "The studio, where Heritage Radio broadcasts twenty-four hours a day."
    c = clip(2957, 0.4, fx=0.42, fy=0.5) * 0.85
    lamp_light(c, 860, 360, 420, 0.5, (1.0, 0.35, 0.3))
    c = bottom(topfade(c), 0.75, 0.55)
    day_dial(c, 0.55)
    F.pop(c, prop('clock'), 870, 1180, 0.38, col=GOLD)
    building_icon(c, 6)
    room_pill(c, 'Heritage Radio · 24 hours a day', y=1470)
    cap_text(c, ['The studio, where Heritage Radio', 'broadcasts 24 hours a day.'], y=1640, size=56, hl=('heritage', 'radio', '24'))
    return c


def s08():   # "The youth club. The scouts."
    c = np.zeros((H, W, 3), np.float32)
    top = warm(clip(5333, 0.5, fx=0.5, fy=0.5, w=W, h=H // 2))
    bot = warm(photo('scouts.jpg', 0.5, 0.4, w=W, h=H // 2))
    c[:H // 2] = top
    c[H // 2:] = bot
    c[H // 2 - 4:H // 2 + 4] = np.array(GOLD[:3], np.float32)
    c = bottom(topfade(c), 0.75, 0.62)
    day_dial(c, 0.62)
    F.pop(c, prop('dice'), 860, 640, 0.4, col=GOLD)
    F.pop(c, prop('compass'), 200, 1220, 0.4, col=GOLD)
    room_pill(c, 'Youth club', x=250, y=880)
    room_pill(c, 'Muslim scouts', x=800, y=1080)
    building_icon(c, 7)
    cap_text(c, ['The youth club.', 'The scouts.'], y=1660, hl=('youth', 'scouts.'))
    return c


def s09():   # "Open days for neighbours of every faith, and none."
    c = warm(photo('476280551_1049256607242153_4186426492440189340_n.jpg', 0.5, 0.5))
    c = bottom(topfade(c), 0.75, 0.5)
    day_dial(c, 0.7)
    F.pop(c, prop('tea'), 820, 640, 0.48, col=GOLD)
    building_icon(c, 8)
    room_pill(c, 'Open days · all welcome', y=1470)
    cap_text(c, ['Open days for neighbours of', 'every faith, and none.'], y=1640, hl=('every', 'faith,'))
    return c


def s10():   # "And every Friday, a khutbah in English."
    c = warm(photo('Screenshot-2025-10-26-055143.png', 0.5, 0.5))
    lamp_light(c, 540, 500, 700, 0.3)
    c = bottom(topfade(c), 0.75, 0.5)
    day_dial(c, 0.25)
    building_icon(c, 9)
    F.chip(c, 'FRIDAY', 230, 560, fill=GOLD, ink=GREEN_D, size=48, rot=-4)
    room_pill(c, 'Friday khutbah in English', y=1470)
    cap_text(c, ['And every Friday, a', 'khutbah in English.'], y=1640, hl=('friday,', 'english.'))
    return c


def s11():   # "Your donations help the Centre carry on all of it."  — night, every window lit
    src = photo('bhmc-f.png', 0.5, 0.5)
    c = night(src) * 1.25
    light_windows(c, src)
    for (x, y) in ((138, 1210), (888, 1260)):
        lamp_light(c, x, y, 160, 0.9)
    c = bottom(np.clip(c, 0, 1), 0.6)
    day_dial(c, 1.0)
    building_icon(c, 9)
    cap_text(c, ['Your donations help the Centre', 'carry on all of it.'], y=1640, size=58, hl=('donations',))
    return c


GRID = [('photo', 'MAS09785-scaled.jpg'), ('photo', 'Screenshot-2025-10-26-033526.png'), ('clip', 48142), ('clip', 2957),
        ('clip', 5333), ('photo', 'scouts.jpg'), ('photo', '476280551_1049256607242153_4186426492440189340_n.jpg'),
        ('photo', 'Screenshot-2025-10-26-055143.png'), ('photo', 'W6A9208-1-scaled.jpg')]


def s12():   # "Help keep the lights on." — every room is a lit window
    c = np.zeros((H, W, 3), np.float32) + np.array([0.03, 0.08, 0.1], np.float32)
    cw, ch, gap = 300, 400, 26
    x0 = (W - 3 * cw - 2 * gap) / 2 + cw / 2
    y0 = 330
    for j, (kind, src) in enumerate(GRID):
        im = photo(src, fx=0.3 if '033526' in str(src) else 0.5, w=cw, h=ch) if kind == 'photo' else clip(src, 0.5, fx=0.42 if src == 2957 else 0.5, w=cw, h=ch)
        im = warm(im)
        x = x0 + (j % 3) * (cw + gap)
        y = y0 + (j // 3) * (ch + gap)
        draw(c, blur_sprite(rrect(cw + 30, ch + 30, 20, (1.0, 0.72, 0.35, 0.8)), 22), x, y)
        fr = rrect(cw + 14, ch + 14, 16, (*GOLD[:3], 1)).copy()
        paste_spr(fr, F.sprite_of(im, 10), (cw + 14) / 2, (ch + 14) / 2)
        draw(c, fr, x, y)
    switch_pop(c, 540, 1480, True, 0.24)
    cap_text(c, ['Help keep the', 'lights on.'], y=1620, size=86, hl=('lights', 'on.'))
    return c


def s13():   # "Become a Friend of the Centre." — end card
    src = photo('bhmc-f.png', 0.5, 0.5)
    c = night(src) * 1.15
    light_windows(c, src)
    c = np.clip(c, 0, 1)
    g = np.clip((_Y / H - 0.42) / 0.3, 0, 1)[..., None]
    c = c * (1 - 0.9 * g) + np.array(GREEN_D[:3], np.float32) * 0.9 * g
    lg = F.logo()
    draw(c, lg, W / 2, 1010, scale=0.8)
    cap_text(c, ['Help keep the lights on.'], y=1220, size=70, hl=('lights', 'on.'))
    F.drop(c, rrect(780, 120, 60, GOLD), W / 2, 1380, sh=0.4)
    draw(c, ts('Become a Friend of the Centre', PB, 44, GREEN_D), W / 2, 1380)
    draw(c, ts('bmhc.org.uk/friend-of-the-centre', PS, 36, IVORY), W / 2, 1520)
    draw(c, ts('Registered charity 1110104', PM, 26, (*IVORY[:3], 0.7)), W / 2, 1580)
    F.bars(c, W / 2 - 200, 1660, 400, 10, 8)
    switch_pop(c, 890, 560, True, 0.3)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = F.to_u8(R.post(fn(), j, bloom=0.16, grain=0.012, vig=0.3))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
