"""Scene images for Organic Fostering Reel 02 "You Don't Have to Be the Whole Team", as a short FILM (not animation).

One carer, one long day. Cold open on rain and a 07:00 alarm; the day stacks up (school run, homework, the call she
didn't expect) faster and faster until the screen splinters into a hundred tiny frames and cuts to silence. A door
opens: someone else's hands. Guidance, learning, support arrive as film titles. Two hands meet in backlight. The film
ends where it began: 07:00 the next morning, but the rain has stopped and the light is warm.

Film language: scope letterbox, cold teal grade for the struggle and warm grade after the turn, grain, halation,
anamorphic flares, slow push-ins, time-of-day chapter stamps, subtitle-style captions (Nunito, brand palette).
Adults only on camera.

Usage: python3 frames_team.py [n ...] -> workspace_team/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_recipe'))
import numpy as np
import cv2
import frames_recipe as FR
from frames_recipe import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, cover,
                           PLUM, MAG, ORANGE, GREEN, IVORY, PEACH, BLUSH, LEAFT, WHITE, N8, N7, HAND, colour_bar, LOGO)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_team'
OUT = f'{S}/frames'
_X, _Y = R._X, R._Y
BAR = 250                                   # scope letterbox height (top and bottom)


# ------------------------------------------------------------------ footage + film grade
def frame_of(cid, t):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def grade(im, mood):
    """cold: desaturated teal shadows, lifted blacks (the struggle). warm: amber highlights, rich skin (after the turn)."""
    lum = im.mean(2, keepdims=True)
    if mood == 'cold':
        im = im * 0.62 + lum * 0.38
        sh = np.clip(1 - lum * 1.8, 0, 1)
        im = im + sh * np.array([-0.04, 0.02, 0.05], np.float32)
        im = np.clip((im - 0.5) * 1.12 + 0.47, 0, 1) * np.array([0.9, 0.98, 1.05], np.float32)
        im = im * 0.92 + 0.03
    elif mood == 'warm':
        hi = np.clip((lum - 0.45) * 2, 0, 1)
        im = np.clip((im - 0.5) * 1.08 + 0.52, 0, 1)
        im = im + hi * np.array([0.08, 0.035, -0.04], np.float32)
        sh = np.clip(1 - lum * 2, 0, 1)
        im = im + sh * np.array([0.02, -0.01, 0.0], np.float32)
    elif mood == 'night':
        im = im * 0.55 + lum * 0.45
        im = np.clip((im - 0.5) * 1.15 + 0.4, 0, 1) * np.array([0.82, 0.9, 1.08], np.float32) * 0.8
    return np.clip(im, 0, 1).astype(np.float32)


def shot(cid, t, mood, fx=0.5, fy=0.5, z=1.0):
    return grade(cover(frame_of(cid, t), fx, fy, z, W, H), mood)


def halation(c, amt=0.35):
    """Film halation: bright areas bleed a soft red-orange glow."""
    hi = np.clip(c.mean(2) - 0.62, 0, 1)
    small = cv2.resize(hi, (W // 4, H // 4))
    g = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (W, H))[..., None]
    return np.clip(c + g * np.array([1.0, 0.45, 0.2], np.float32) * amt * 2.2, 0, 1)


def flare(c, x, y, amt=0.5, col=(1.0, 0.7, 0.45)):
    """Anamorphic lens flare: a long horizontal streak and a soft core."""
    streak = np.exp(-((_Y - y) / 7) ** 2) * np.exp(-np.abs(_X - x) / 420)
    core = np.exp(-(((_X - x) / 90) ** 2 + ((_Y - y) / 90) ** 2))
    c[:] = np.clip(c + (streak * 0.9 + core * 0.7)[..., None] * np.array(col, np.float32) * amt, 0, 1)


def film(c, seed=0, vig=0.45):
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 0.035, (H // 2, W // 2)).astype(np.float32)
    c = np.clip(c + cv2.resize(g, (W, H))[..., None], 0, 1)
    v = np.clip(1 - (((_X - W / 2) / (W * 0.7)) ** 2 + ((_Y - H / 2) / (H * 0.62)) ** 2), 0, 1)[..., None]
    c = c * (1 - vig + vig * v)
    c[:BAR] = 0.0
    c[H - BAR:] = 0.0
    return c


def stamp(c, text, x=80, y=BAR + 70, size=40, col=(1, 1, 1, 0.9)):
    """Chapter time stamp, like a film's on-screen time code."""
    s = ts(text, 'Inter-600', size, col, 0.18)
    draw(c, s, x + s.shape[1] / 2, y)
    draw(c, rrect(70, 4, 2, (1, 1, 1, 0.7)), x + 35, y + 32)


def subtitle(c, lines, keys=(), hl=MAG, y=None, size=50):
    """Film-subtitle captions in the lower letterbox: Nunito, white, cue words on a brand highlight."""
    y = H - BAR + 70 if y is None else y
    lines = [lines] if isinstance(lines, str) else lines
    for li, l in enumerate(lines):
        ws = l.split()
        ms = [_wmask(w, N8, size) for w in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ms) - 1)
        x = W / 2 - tw / 2
        yy = y + li * size * 1.3
        for w, m in zip(ws, ms):
            cx = x + m.shape[1] / 2
            if w.strip('.,?…:').lower() in keys:
                draw(c, rrect(m.shape[1] + 20, size * 1.14, 14, hl), cx, yy + 2)
            draw(c, solid(m, WHITE), cx, yy)
            x += m.shape[1] + size * 0.24


def title_card(c, text, y, size=96, col=WHITE, k=1.0):
    s = ts(text, N8, size, col, -0.01)
    draw(c, blur_sprite(solid(_wmask(text, N8, size), (0, 0, 0, 1)), 14), W / 2 + 3, y + 8, opacity=0.6 * k)
    draw(c, s, W / 2, y, opacity=k)


_TOK = {}


def token(name):
    if name not in _TOK:
        for d in ('workspace_three/assets', 'workspace_nq/assets', 'workspace_recipe/assets'):
            p = f'{ROOT}/{d}/{name}.png'
            if os.path.exists(p):
                sp = load_png_sprite(p)
                ys, xs = np.where(sp[..., 3] > 0.01)
                _TOK[name] = np.ascontiguousarray(sp[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
                break
    return _TOK[name]


def floating(c, name, x, y, size, rot=0, blur=0, op=1.0):
    sp = token(name)
    if blur:
        sp = blur_sprite(sp, blur)
    sc = size / max(sp.shape[:2])
    draw(c, blur_sprite(tint(sp, (0, 0, 0)), 18), x + 10, y + 26, scale=sc, rot=rot, opacity=0.45 * op)
    draw(c, sp, x, y, scale=sc, rot=rot, opacity=op)


# ------------------------------------------------------------------ scenes
def s01():   # COLD OPEN: rain on the window before dawn; 07:00
    c = shot('20311', 6.0, 'cold')
    c = c * 0.75
    stamp(c, '07:00')
    title_card(c, 'One day.', 960, 120)
    return film(c, 1)


def s02():   # the alarm, a hand reaches out
    c = shot('4758', 4.5, 'cold', 0.7, 0.5, 1.0)
    stamp(c, '07:00')
    return film(c, 2)


def s03():   # "One school run." — the drive, hands on the wheel, the road
    c = shot('4521', 6.0, 'cold', 0.4, 0.5, 1.1)
    c = halation(c, 0.3)
    flare(c, 760, 760, 0.35)
    floating(c, 'backpack', 830, 1180, 220, rot=8)
    stamp(c, '08:12')
    c = film(c, 3)
    subtitle(c, ['One school run.'], keys=('school', 'run'), hl=ORANGE)
    return c


def s04():   # "One homework question." — her hands, papers, calculator
    c = shot('4533', 8.0, 'cold', 0.5, 0.5, 1.1)
    floating(c, 'question', 820, 760, 200, rot=10)
    stamp(c, '16:40')
    c = film(c, 4)
    subtitle(c, ['One homework question.'], keys=('homework',), hl=ORANGE)
    return c


def s05():   # "One appointment you didn't expect." — the phone call on the sofa
    c = shot('4513', 3.5, 'cold', 0.5, 0.45, 1.25)
    floating(c, 'calendar', 820, 1150, 220, rot=-8)
    stamp(c, '17:25')
    c = film(c, 5)
    subtitle(c, ["One appointment you didn't expect."], keys=('appointment',), hl=MAG)
    return c


def s06():   # "And sometimes, one day feels like a hundred things." — the frame splinters into a hundred
    base = shot('4526', 7.0, 'cold', 0.5, 0.45, 1.2)
    c = np.zeros_like(base)
    srcs = [('4526', 7.0), ('4533', 5.0), ('4513', 3.5), ('4521', 6.0), ('4517', 4.0), ('38501', 6.0), ('4758', 3.0), ('39790', 5.0)]
    cache = {s_: cover(frame_of(*s_), 0.5, 0.5, 1.0, 108, 192) for s_ in srcs}
    rng = np.random.default_rng(3)
    cols, rows = 10, 10
    cw, chh = W / cols, H / rows
    for r in range(rows):
        for q in range(cols):
            tile = grade(cache[srcs[rng.integers(0, len(srcs))]], 'cold')
            tile = cv2.resize(tile, (int(cw) - 4, int(chh) - 4))
            y0, x0 = int(r * chh) + 2, int(q * cw) + 2
            c[y0:y0 + tile.shape[0], x0:x0 + tile.shape[1]] = tile * rng.uniform(0.5, 1.0)
    m = np.clip(1 - np.hypot(_X - 540, _Y - 900) / 520, 0, 1)[..., None] ** 0.7
    c = c * (1 - m) + base * m
    for nm, x, y, r in (('clock', 220, 560, -12), ('phone', 860, 600, 14), ('calendar', 230, 1250, 8), ('backpack', 860, 1260, -10),
                        ('briefcase', 540, 430, 4), ('house', 540, 1420, -6)):
        floating(c, nm, x, y, 170, rot=r, blur=2)
    stamp(c, '21:30')
    c = film(c, 6)
    subtitle(c, ['And sometimes, one day', 'feels like a hundred things.'], keys=('hundred',), hl=MAG, size=46)
    return c


def s07():   # SILENCE: she lies back. Black, one breath.
    c = shot('4534', 5.0, 'night', 0.5, 0.42, 1.15)
    stamp(c, '23:05')
    return film(c, 7, vig=0.6)


def s08():   # "But fostering was never meant to be something you manage alone." — a door opens
    c = shot('21813', 6.0, 'warm', 0.55, 0.45, 1.1)
    c = halation(c, 0.45)
    flare(c, 380, 700, 0.55)
    c = film(c, 8)
    subtitle(c, ['But fostering was never meant to be', 'something you manage alone.'], keys=('alone',), hl=MAG, size=44)
    return c


def s09():   # the second pair of hands
    c = shot('4571', 4.0, 'warm', 0.5, 0.62, 1.0)
    c = halation(c, 0.3)
    c = film(c, 9)
    subtitle(c, ['But fostering was never meant to be', 'something you manage alone.'], keys=('alone',), hl=MAG, size=44)
    return c


def s10():   # "At Organic Fostering, you have guidance and ongoing support." — three titles over three moments
    c = np.zeros((H, W, 3), np.float32)
    band = (H - 2 * BAR) // 3
    for i, (cid, t, lab, col) in enumerate((('4571', 12.0, 'Guidance', MAG), ('4547', 8.0, 'Learning', ORANGE), ('4573', 9.0, 'Support', GREEN))):
        im = grade(cover(frame_of(cid, t), 0.5, 0.45, 1.0, W, band - 6), 'warm')
        y0 = BAR + i * band + 3
        c[y0:y0 + im.shape[0]] = im
        s = ts(lab, N8, 64, WHITE)
        p = rrect(s.shape[1] + 70, 92, 46, col).copy()
        paste_spr(p, s, p.shape[1] / 2, 46)
        draw(c, blur_sprite(tint(p, (0, 0, 0)), 14), 80 + p.shape[1] / 2 + 6, y0 + band - 70 + 10, opacity=0.5)
        draw(c, p, 80 + p.shape[1] / 2, y0 + band - 70)
    c = film(c, 10, vig=0.3)
    subtitle(c, ['At Organic Fostering, you have', 'guidance and ongoing support.'], keys=('guidance', 'support'), hl=MAG, size=44)
    return c


def s11():   # "Because when you care for a child, someone should be looking after you, too." — two hands meet in backlight
    c = shot('4505', 6.5, 'warm', 0.5, 0.5, 1.15)
    c = halation(c, 0.6)
    flare(c, 540, 820, 0.7)
    c = film(c, 11)
    subtitle(c, ['Because when you care for a child, someone', 'should be looking after you, too.'], keys=('you,', 'too'), hl=MAG, size=40)
    return c


def s12():   # THE END OF THE STORY: 07:00 the next morning, rain stopped, warm light through the window
    c = shot('4758', 4.5, 'warm', 0.7, 0.5, 1.0)
    g = np.exp(-(((_X - 900) / 520) ** 2 + ((_Y - 520) / 700) ** 2))[..., None]
    c = np.clip(c + g * np.array([0.35, 0.2, 0.05], np.float32), 0, 1)
    c = halation(c, 0.6)
    flare(c, 880, 560, 0.7)
    stamp(c, '07:00')
    title_card(c, 'The next day.', 960, 100)
    return film(c, 12)


def s13():   # end card
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    lg = LOGO()
    draw(c, lg, 540, 600, scale=760 / lg.shape[1])
    draw(c, ts('You do not have to', N8, 66, PLUM), 540, 900)
    draw(c, ts('manage it alone.', N8, 66, MAG), 540, 985)
    btn = rrect(620, 120, 60, MAG)
    draw(c, btn, 540, 1160)
    draw(c, ts('Start your enquiry', N8, 48, WHITE), 540, 1160)
    draw(c, ts('No pressure, no obligation.', N7, 40, PLUM), 540, 1270)
    draw(c, ts('0161 241 1332  ·  organicfostering.co.uk', N7, 34, R.hexc('#655563')), 540, 1350)
    c[:BAR] = 0.0
    c[H - BAR:] = 0.0
    colour_bar(c, H - BAR - 14, 14)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13]


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
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
