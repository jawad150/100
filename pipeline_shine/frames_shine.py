"""Scene images for BMHC "Shine" (the PDF, word for word), video version with a story and 3D lanterns.

Story: at dusk, two pairs of trainers walk side by side towards the Centre; a girl's cupped hands hold a tiny flame
("Every girl has a spark"). The spark drifts into the dark and lights five 3D paper lanterns, one on each cue word, each with
a white line icon and a pill (Faith & Character · Creative Activities · Life Skills & Well-being · Sports & Fitness ·
Social & Community). On "shine" the lanterns rise past the 1843 tower into a warming sky. End card.

No faces anywhere (the PDF's guideline): only feet and hands. No music (voice and natural sounds only).

Usage: python3 frames_shine.py [n ...] -> workspace_shine/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_bmhc'))
import numpy as np
import cv2
import frames_bmhc as FB
from frames_bmhc import R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, GREEN_D, IVORY, TEAL, GOLD, MAG, ORANGE, GREEN

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_shine'
OUT = f'{S}/frames'
IMG = f'{ROOT}/workspace_bmhc/web/img'
_X, _Y = R._X, R._Y
WHITE = (1, 1, 1, 1)
PB, PS = 'Poppins-Bold', 'Poppins-SemiBold'
WARM = (1.0, 0.82, 0.5)

LANT = {   # name: (hex for recolour, pill text, BMHC colour)
    'faith': ('#09999C', 'Faith & Character', TEAL),
    'creative': ('#DB225E', 'Creative Activities', MAG),
    'wellbeing': ('#F26721', 'Life Skills & Well-being', ORANGE),
    'sport': ('#76BF43', 'Sports & Fitness', GREEN),
    'social': ('#DD9933', 'Social & Community', GOLD),
}
ORDER = ['faith', 'creative', 'wellbeing', 'sport', 'social']


def hexf(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ------------------------------------------------------------------ sources
def frame_of(cid, t=0.45):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def cover(im, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    return FB.F.cover(im, fx, fy, z, w, h) if hasattr(FB, 'F') else R_cover(im, fx, fy, z, w, h)


def R_cover(im, fx, fy, z, w, h):
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    return cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def dusk(im, amt=1.0):
    """Night-green grade: deep green shadows, lowered exposure, warm highlights kept."""
    lum = (im * np.array([0.3, 0.59, 0.11], np.float32)).sum(2, keepdims=True)
    g = np.array(hexf('#122F2A'), np.float32)
    out = im * (0.42 + 0.5 * lum) + g * 0.35 * (1 - lum)
    hi = np.clip((lum - 0.65) * 2.5, 0, 1)
    out = out + hi * np.array([0.12, 0.06, -0.02], np.float32)
    return np.clip(im * (1 - amt) + out * amt, 0, 1).astype(np.float32)


def clip(cid, t, fx=0.5, fy=0.5, z=1.0, w=W, h=H, amt=1.0):
    return dusk(R_cover(frame_of(cid, t), fx, fy, z, w, h), amt)


def building(name='x.jpg', fx=0.5, fy=0.5, z=1.0, night=0.85, w=W, h=H):
    im = cv2.imread(f'{IMG}/{name}')[..., ::-1].astype(np.float32) / 255
    im = R_cover(im, fx, fy, z, w, h)
    # day-for-night: desaturate, deep-green multiply, darker towards the top of the frame
    lum = (im * np.array([0.3, 0.59, 0.11], np.float32)).sum(2, keepdims=True)
    im = im * 0.35 + lum * 0.65
    im = dusk(im, night) * 0.62
    k = np.clip(1 - np.arange(h, dtype=np.float32)[:, None] / (h * 0.75), 0, 1)[..., None] ** 1.2
    g = np.array(hexf('#0A1F1B'), np.float32)
    return np.clip(im * (1 - 0.6 * k) + g * 0.6 * k, 0, 1).astype(np.float32)


_SPR = {}


def lantern(name, on=True):
    key = (name, on)
    if key not in _SPR:
        sp = load_png_sprite(f'{S}/lanterns/{name}_{"on" if on else "off"}.png')
        sp = recolour(sp, LANT[name][0], 1.25 if on else 1.0)
        _SPR[key] = sp
    return _SPR[key]


def recolour(sp, hx, sat_boost=1.2):
    """Pin the paper to its BMHC hue (the renderer's light shifts warm colours together)."""
    a = sp[..., 3:4]
    rgb = np.where(a > 1e-4, sp[..., :3] / np.maximum(a, 1e-4), 0).astype(np.float32)
    hsv = cv2.cvtColor(np.clip(rgb, 0, 1), cv2.COLOR_RGB2HSV)
    th = cv2.cvtColor(np.array([[hexf(hx)]], np.float32), cv2.COLOR_RGB2HSV)[0, 0]
    h_, w_ = hsv.shape[:2]
    rows = np.arange(h_)[:, None] / h_
    body = ((rows > 0.12) & (rows < 0.84)).astype(np.float32) * np.ones((1, w_), np.float32)
    paper = (hsv[..., 1] > 0.12).astype(np.float32) * body
    paper = cv2.GaussianBlur(paper, (0, 0), 1.5)
    hsv2 = hsv.copy()
    hsv2[..., 0] = th[0]
    hsv2[..., 1] = np.clip(np.maximum(hsv[..., 1], th[1] * 0.75) * sat_boost, 0, 1)
    rgb2 = cv2.cvtColor(hsv2, cv2.COLOR_HSV2RGB)
    rgb = rgb * (1 - paper[..., None]) + rgb2 * paper[..., None]
    return np.concatenate([rgb * a, a], 2).astype(np.float32)


# ------------------------------------------------------------------ light
def glow(c, x, y, r, col=WARM, amt=0.5):
    g = np.exp(-((_X - x) ** 2 + (_Y - y) ** 2) / (2 * r * r))[..., None] * amt
    c[:] = np.clip(c + g * np.array(col[:3], np.float32), 0, 1)


def pool(c, x, y, col, r=420, amt=0.35):
    """The soft coloured pool a lit lantern casts on the dark."""
    g = np.exp(-((_X - x) ** 2 + ((_Y - y) * 0.85) ** 2) / (2 * r * r))[..., None] * amt
    c[:] = np.clip(c * (1 - g * 0.3) + g * np.array(col[:3], np.float32), 0, 1)


def spark(c, x, y, s=1.0):
    glow(c, x, y, 70 * s, WARM, 0.45)
    glow(c, x, y, 22 * s, (1, 0.95, 0.8), 0.9)
    glow(c, x, y, 7 * s, (1, 1, 1), 1.0)


def trail(c, pts, col=(1, 0.85, 0.55), th=3, amt=0.8, dots=True, seed=0):
    p = np.array(pts, np.float32)
    lay = np.zeros((H, W), np.uint8)
    cv2.polylines(lay, [(p * 4).astype(np.int32)], False, 255, th * 4, cv2.LINE_AA, shift=2)
    m = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 3)[..., None]
    fade = np.linspace(0.05, 1, len(p))
    c[:] = np.clip(c + m * amt * np.array(col, np.float32) * 0.8, 0, 1)
    if dots:
        rng = np.random.default_rng(seed)
        for k in range(0, len(p), 3):
            jx, jy = rng.normal(0, 14, 2)
            glow(c, p[k][0] + jx, p[k][1] + jy, rng.uniform(2, 5), (1, 0.9, 0.6), rng.uniform(0.3, 0.9) * fade[k])


def stars(c, n=90, seed=5, y1=900, amt=0.8):
    rng = np.random.default_rng(seed)
    lay = np.zeros((H, W), np.float32)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, y1)
        cv2.circle(lay, (int(x), int(y)), 1 + int(rng.random() > 0.85), rng.uniform(0.3, 1), -1, cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 0.8)[..., None]
    c[:] = np.clip(c + lay * amt, 0, 1)


def night(glow_y=1100, warm=0.0):
    k = (_Y / H)[..., None]
    c = np.array(hexf('#0A1A17'), np.float32) * (1 - k) + np.array(hexf('#122F2A'), np.float32) * k
    if warm:
        g = np.exp(-((_X - W / 2) ** 2 + (_Y - glow_y) ** 2) / (2 * 700 ** 2))[..., None] * warm
        c = c + g * np.array([0.45, 0.32, 0.12], np.float32)
    return np.clip(c, 0, 1).astype(np.float32)


def put_lantern(c, name, x, y, size, on=True, rot=0, cast=True):
    sp = lantern(name, on)
    sc = size / sp.shape[0]
    if on and cast:
        pool(c, x, y + size * 0.1, LANT[name][2], r=size * 0.9, amt=0.32)
        glow(c, x, y, size * 0.45, LANT[name][2], 0.35)
    draw(c, sp, x, y, scale=sc, rot=rot, opacity=1.0 if on else 0.75)


def pill(c, text, x, y, col, size=34):
    s = ts(text, PS, size, WHITE)
    w = s.shape[1] + 56
    draw(c, blur_sprite(tint(rrect(w, size * 1.9, size * 0.95, col), (0, 0, 0)), 14), x, y + 8, opacity=0.4)
    draw(c, rrect(w, size * 1.9, size * 0.95, col), x, y)
    draw(c, s, x, y)


def caption(c, lines, keys=(), y=1540, size=64, keycol=GOLD):
    keys = {k.lower() for k in keys}
    for li, ln in enumerate(lines):
        ws = ln.split()
        ms = [_wmask(w_, PB, size) for w_ in ws]
        tw = sum(m.shape[1] for m in ms) + size * 0.24 * (len(ws) - 1)
        xx = W / 2 - tw / 2
        yy = y + li * size * 1.22
        for w_, m in zip(ws, ms):
            k = w_.strip('.,…!?').lower() in keys
            col = keycol if k else WHITE
            if k:
                draw(c, blur_sprite(solid(m, col), 14), xx + m.shape[1] / 2, yy, opacity=0.8)
            draw(c, blur_sprite(solid(m, (0, 0, 0, 1)), 10), xx + m.shape[1] / 2 + 2, yy + 5, opacity=0.6)
            draw(c, solid(m, col), xx + m.shape[1] / 2, yy)
            xx += m.shape[1] + size * 0.24


def eyebrow(c, text='SHINE · YOUTH CLUB FOR GIRLS', y=290):
    s = ts(text, PS, 26, (1, 0.9, 0.7, 0.9), 0.2)
    draw(c, s, W / 2, y)


def shade(c, top=0.62, amt=0.75):
    g = np.clip((_Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    c[:] = c * (1 - amt * g) + np.array(hexf('#0A1A17'), np.float32) * amt * g


def top_shade(c, h=420, amt=0.6):
    g = np.clip(1 - _Y / h, 0, 1)[..., None] ** 1.5
    c[:] = c * (1 - amt * g) + np.array(hexf('#0A1A17'), np.float32) * amt * g


def arch_card(img, w, h, border=10, glow_col=GOLD):
    m = np.zeros((h * 2, w * 2), np.uint8)
    cv2.rectangle(m, (0, w), (w * 2, h * 2), 255, -1)
    cv2.circle(m, (w, w), w, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    inner = cv2.GaussianBlur(cv2.erode(m, np.ones((border * 2 + 1, border * 2 + 1), np.uint8)), (0, 0), 0.8)
    pic = R_cover(img, 0.5, 0.5, 1.0, w, h)
    rgb = pic * inner[..., None] + np.array(glow_col[:3], np.float32) * (m - inner)[..., None]
    return np.concatenate([rgb, m[..., None]], 2).astype(np.float32)


def put_arch(c, img, x, y, w, h, col=GOLD):
    a = arch_card(img, w, h, glow_col=col)
    draw(c, blur_sprite(tint(a, col[:3]), 26), x, y, opacity=0.5)
    draw(c, a, x, y)


# ------------------------------------------------------------------ scenes
def s01():   # "Every girl…" — two pairs of trainers walking side by side at dusk, towards the Centre
    c = clip(32616, 0.45, fx=0.42, fy=0.75)
    top_shade(c, 520, 0.7)
    shade(c, 0.6, 0.8)
    b = building('bhmc-f.png', 0.5, 0.45, 1.0, 0.9, W, 560)
    m = np.clip(1 - np.abs(np.arange(560) - 280) / 280, 0, 1)[:, None, None] ** 0.8 * 0.45
    c[60:620] = c[60:620] * (1 - m) + b * m
    spark(c, 760, 860, 0.8)
    eyebrow(c)
    caption(c, ['Every girl…'], y=1540, size=74)
    return c


def s02():   # "…has a spark." — a girl's cupped hands around a small flame (no face)
    c = clip(41739, 0.5, fy=0.62, z=1.25, amt=0.6)
    top_shade(c, 700, 0.85)
    shade(c, 0.66, 0.8)
    spark(c, 545, 900, 1.6)
    trail(c, [(545, 880), (600, 760), (700, 620), (760, 520), (820, 470)], seed=2)
    eyebrow(c)
    caption(c, ['Every girl has a spark.'], keys=('spark',), y=1540, size=70)
    return c


def lantern_set(c, lit, positions, size=560, dim_others=True):
    for nm in ORDER:
        x, y, rot = positions[nm]
        if nm in lit:
            put_lantern(c, nm, x, y, size, True, rot)
        elif dim_others:
            put_lantern(c, nm, x, y, size * 0.9, False, rot, cast=False)


POS = {'faith': (250, 760, -4), 'creative': (830, 690, 5), 'wellbeing': (545, 1040, -2), 'sport': (215, 1240, 6), 'social': (865, 1200, -5)}


def string_lines(c):
    """Fine strings the lanterns hang from (rising out of frame)."""
    lay = np.zeros((H, W), np.uint8)
    for nm in ORDER:
        x, y, _ = POS[nm]
        cv2.line(lay, (x, 0), (x, int(y - 200)), 255, 1, cv2.LINE_AA)
    m = lay.astype(np.float32)[..., None] / 255 * 0.25
    c[:] = c * (1 - m) + np.array(hexf('#C9A15A'), np.float32) * m


def lantern_scene(lit, newest, line_words, keys, trail_from=None):
    c = night(1300, 0.08)
    b = building('bhmc-f.png', 0.5, 0.5, 1.0, 0.95, W, 600)
    m = np.clip((np.arange(600) - 80) / 300, 0, 1)[:, None, None] * 0.35
    c[1320:1920] = c[1320:1920] * (1 - m) + b * m
    stars(c, 70, y1=700, amt=0.5)
    string_lines(c)
    if trail_from is not None:
        x1, y1, _ = POS[newest]
        x0, y0 = trail_from
        pts = [(x0 + (x1 - x0) * u + math.sin(u * 5) * 40, y0 + (y1 - y0) * u - math.sin(u * math.pi) * 160) for u in np.linspace(0, 1, 40)]
        trail(c, pts, seed=len(lit))
    lantern_set(c, lit, POS)
    x, y, _ = POS[newest]
    pill(c, LANT[newest][1], min(max(x, 230), W - 230), y + 245, LANT[newest][2])
    shade(c, 0.76, 0.85)
    caption(c, line_words, keys=keys, keycol=LANT[newest][2], y=1610, size=62)
    return c


def s03():   # "At Shine, it grows through faith and character…"
    return lantern_scene(['faith'], 'faith', ['At Shine, it grows through', 'faith and character…'], ('faith', 'character…'), trail_from=(560, 300))


def s04():   # "…creativity…"
    return lantern_scene(['faith', 'creative'], 'creative', ['…creativity…'], ('creativity',), trail_from=POS['faith'][:2])


def s05():   # "…life skills and well-being…"
    return lantern_scene(['faith', 'creative', 'wellbeing'], 'wellbeing', ['…life skills and well-being…'], ('well-being…', 'well-being'),
                         trail_from=POS['creative'][:2])


def s06():   # "…sport…" — with a glimpse of trainers on the move
    c = lantern_scene(['faith', 'creative', 'wellbeing', 'sport'], 'sport', ['…sport…'], ('sport',), trail_from=POS['wellbeing'][:2])
    put_arch(c, dusk(frame_of(32622, 0.4), 0.5), 545, 420, 250, 330, GREEN)
    return c


def s07():   # "…and friendship." — all five glow; two friends' trainers side by side
    c = lantern_scene(ORDER, 'social', ['…and friendship.'], ('friendship.', 'friendship'), trail_from=POS['sport'][:2])
    put_arch(c, dusk(frame_of(32616, 0.3), 0.5), 545, 420, 250, 330, GOLD)
    return c


def rise_bg(warm):
    c = building('x.jpg', 0.5, 0.55, 1.0, 0.9)
    k = np.clip(1 - _Y / 1100, 0, 1)[..., None]
    c = c * (1 - 0.25 * k)
    g = np.exp(-((_X - W / 2) ** 2 + (_Y - 600) ** 2) / (2 * 750 ** 2))[..., None] * warm
    c = np.clip(c + g * np.array([0.5, 0.36, 0.14], np.float32), 0, 1)
    stars(c, 60, y1=500, amt=0.45)
    return c


RISE = {'faith': (270, 520, -6), 'creative': (720, 400, 4), 'wellbeing': (500, 700, -3), 'sport': (210, 880, 7), 'social': (850, 780, -4)}


def s08():   # "Give your daughter a place where she can shine,"
    c = rise_bg(0.25)
    for nm in ORDER:
        x, y, r = RISE[nm]
        put_lantern(c, nm, x, y + 160, 250, True, r)
        trail(c, [(x, y + 420), (x + 6, y + 340), (x - 4, y + 270)], th=2, amt=0.4, seed=ORDER.index(nm))
    shade(c, 0.66, 0.8)
    eyebrow(c)
    caption(c, ['Give your daughter a place', 'where she can shine,'], keys=('shine,', 'shine'), y=1520, size=62)
    return c


def s09():   # "…grow, and feel confident."
    c = rise_bg(0.5)
    for nm in ORDER:
        x, y, r = RISE[nm]
        put_lantern(c, nm, x, y - 160, 190, True, r)
    rng = np.random.default_rng(9)
    for _ in range(40):
        glow(c, rng.uniform(80, 1000), rng.uniform(150, 1200), rng.uniform(2, 5), (1, 0.9, 0.6), rng.uniform(0.3, 0.9))
    shade(c, 0.64, 0.82)
    eyebrow(c)
    caption(c, ['where she can shine,', 'grow, and feel confident.'], keys=('shine,', 'grow,', 'confident.'), y=1500, size=62)
    return c


def s10():   # end card
    c = night(700, 0.12)
    stars(c, 80, y1=1900, amt=0.35)
    spark(c, W / 2, 330, 1.0)
    m = _wmask('Shine', 'Caveat-700', 260)
    draw(c, blur_sprite(solid(m, GOLD), 26), W / 2, 560, opacity=0.9)
    draw(c, solid(m, (1, 0.93, 0.78, 1)), W / 2, 560)
    draw(c, ts('Youth Club for girls · 14–18', PB, 46, WHITE), W / 2, 760)
    draw(c, ts('Qualified female mentors · weekly at BMHC', PS, 32, (1, 1, 1, 0.8)), W / 2, 840)
    bw, bh = 720, 120
    btn = rrect(bw, bh, bh / 2, GOLD)
    draw(c, blur_sprite(btn, 30), W / 2, 1000, opacity=0.6)
    draw(c, btn, W / 2, 1000)
    draw(c, ts('Join Shine Youth Club', PB, 46, hexf('#122F2A') + (1,)), W / 2, 1000)
    draw(c, ts('0161 881 8062 · link in bio', PS, 34, (1, 1, 1, 0.85)), W / 2, 1130)
    lg = FB.logo(True)
    draw(c, lg, W / 2, 1360, scale=520 / lg.shape[1])
    for i, nm in enumerate(ORDER):
        put_lantern(c, nm, 180 + i * 180, 1640, 260, True, 0, cast=False)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        im = to_u8(R.post(fn(), j, bloom=0.22, grain=0.012, vig=0.3))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 5:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 5]) for i in range(0, len(th), 5)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
