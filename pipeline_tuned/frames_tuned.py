"""Scene images for BMHC "Tuned In" (Heritage Radio 90.6 FM), video version with a people story and 3D pop-ups.

Story: dawn in Whalley Range, footsteps along the path to the Centre. Inside, one small studio: the ON AIR lamp lights.
The signal leaves the building as golden rings and spreads over a living map of Manchester, lighting up the
neighbourhoods. Then we follow it through one day into the places people listen: a radio switched on in the kitchen,
morning tea, a rainy commute with 90.6 on the dashboard, a walk with headphones, the bus, the corner shop, a podcast
for later. At dusk the rings flow back home to the Centre, and the dial settles on 90.6 FM.

Signature device: a golden FM tuning strip along the top whose needle drifts across the band as the day passes and
locks on 90.6 at the end. Every cue word pops a glossy 3D object.

Usage: python3 frames_tuned.py [n ...] -> workspace_tuned/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_bmhc'))
import numpy as np
import cv2
import frames_bmhc as FB
from frames_bmhc import (R, W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, _wmask, load_png_sprite, GREEN_D, IVORY,
                         TEAL, GOLD, MAG, ORANGE, GREEN, BARS, PB, PX, PS, PM, PR, glass, glow, chip, bars, cover, grade, shade, top_shade)

ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_tuned'
OUT = f'{S}/frames'
IMG = f'{ROOT}/workspace_bmhc/web/img'
_X, _Y = R._X, R._Y
WHITE = (1, 1, 1, 1)
HGOLD = R.hexc('#B8913A')            # heritage gold (the PDF's signal colour)
LGOLD = (1.0, 0.86, 0.55, 1)
RED = (0.92, 0.2, 0.16, 1)


# ------------------------------------------------------------------ sources
def frame_of(cid, t=0.45):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return im[..., ::-1].astype(np.float32) / 255


def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H, g=True):
    im = cover(frame_of(cid, t), fx, fy, z, w, h)
    return grade(im) if g else im


def photo(name, fx=0.5, fy=0.5, z=1.0, w=W, h=H, g=True):
    im = cv2.imread(f'{IMG}/{name}', cv2.IMREAD_COLOR)[..., ::-1].astype(np.float32) / 255
    im = cover(im, fx, fy, z, w, h)
    return grade(im) if g else im


_TOK = {}


def token(name):
    if name not in _TOK:
        sp = load_png_sprite(f'{S}/assets/{name}.png')
        a = sp[..., 3]
        ys, xs = np.where(a > 0.01)
        _TOK[name] = np.ascontiguousarray(sp[max(0, ys.min() - 6):ys.max() + 7, max(0, xs.min() - 6):xs.max() + 7])
    return _TOK[name]


def daylight(c, kind):
    """Colour of the hour: the day passes as the reel plays."""
    tints = dict(dawn=((1.0, 0.86, 0.7), 0.16), studio=((1.0, 0.5, 0.35), 0.08), morning=((1.0, 0.9, 0.75), 0.1),
                 rain=((0.75, 0.85, 0.95), 0.12), midday=((1.0, 1.0, 0.95), 0.04), evening=((1.0, 0.75, 0.5), 0.14),
                 dusk=((0.35, 0.45, 0.85), 0.25))
    col, a = tints[kind]
    return np.clip(c * (1 - a) + c * np.array(col, np.float32) * a * 1.25, 0, 1)


# ------------------------------------------------------------------ the golden FM tuning strip (signature device)
def tuner(c, freq, lock=0.0, y=290, a=1.0):
    """FM band 87.5-108 MHz as a slim gold scale; the needle sits on `freq`; `lock` grows a 90.6 readout."""
    x0, x1 = 90, W - 90
    lay = np.zeros((H, W), np.uint8)
    for f10 in range(875, 1081, 5):
        x = x0 + (f10 - 875) / (1080 - 875) * (x1 - x0)
        hgt = 26 if f10 % 20 == 0 else (16 if f10 % 10 == 0 else 9)
        cv2.line(lay, (int(x * 4), int((y - hgt / 2) * 4)), (int(x * 4), int((y + hgt / 2) * 4)), 255, 2 * 4 if f10 % 10 == 0 else 4,
                 cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.85 * a
    c[:] = c * (1 - m) + np.array(LGOLD[:3], np.float32) * m
    for f in (88, 92, 96, 100, 104, 108):
        x = x0 + (f * 10 - 875) / (1080 - 875) * (x1 - x0)
        draw(c, ts(str(f), PM, 22, (1, 0.92, 0.75, 0.85)), x, y + 34, opacity=a)
    xn = x0 + (freq * 10 - 875) / (1080 - 875) * (x1 - x0)
    glow(c, xn, y, 60, LGOLD, 0.35 * a)
    draw(c, rrect(6, 70, 3, RED), xn, y, opacity=a)
    if lock > 0:
        s = ts('90.6 FM', PB, 34, WHITE)
        w = s.shape[1] + 40
        draw(c, rrect(w, 56, 28, RED), xn, y - 66, scale=0.7 + 0.3 * lock, opacity=lock * a)
        draw(c, s, xn, y - 66, scale=0.7 + 0.3 * lock, opacity=lock * a)


def rings(c, x, y, k, n=4, rmax=900, col=HGOLD, w=4, alpha=0.9, inward=False):
    """Golden signal ripples spreading from (x, y). k = phase 0..1+ (loops)."""
    lay = np.zeros((H, W), np.float32)
    for j in range(n):
        p = (k + j / n) % 1.0
        if inward:
            p = 1 - p
        r = 30 + p * rmax
        tmp = np.zeros((H, W), np.uint8)
        cv2.circle(tmp, (int(x * 4), int(y * 4)), int(r * 4), 255, int(w * 4 * (1.4 - p)), cv2.LINE_AA, shift=2)
        lay = np.maximum(lay, tmp.astype(np.float32) / 255 * (1 - p) ** 1.2)
    bl = cv2.GaussianBlur(lay, (0, 0), 8)
    m = np.clip(lay + bl * 0.8, 0, 1)[..., None] * alpha
    c[:] = c * (1 - m) + np.array(LGOLD[:3] if col is None else col[:3], np.float32) * 0 + np.array(LGOLD[:3], np.float32) * m


def pill(c, text, x, y, fill=IVORY, ink=GREEN_D, size=34):
    return chip(c, text, x, y, fill=fill, ink=ink, size=size, font=PS, dot=TEAL)


def pop(c, name, x, y, size, rot=0, rays=True, col=None):
    sp = token(name)
    sc = size / max(sp.shape[:2])
    if rays:
        lay = np.zeros((H, W), np.uint8)
        r0 = size * 0.5
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = 28 if j % 2 else 44
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((y + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + ln)) * 4), int((y + math.sin(a) * (r0 + ln)) * 4)), 255, 5 * 4, cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.9
        c[:] = c * (1 - m) + np.array((col or LGOLD)[:3], np.float32) * m
    draw(c, blur_sprite(tint(sp, (0.0, 0.05, 0.04)), 20), x + 8, y + 24, scale=sc, rot=rot, opacity=0.5)
    draw(c, sp, x, y, scale=sc, rot=rot)


def caption(c, spec, y=1430, size=70):
    """Poppins Bold captions, voiceover word for word; cue words on a teal highlight (the PDF's teal cue words)."""
    lines = spec if isinstance(spec[0], list) else [spec]
    FB.caption(c, [[(w, 'hl' if w.startswith('*') else None) for w in l] for l in lines], y=y, size=size)


def cap(c, text, y=1430, size=70):
    """'From one *room in *Whalley *Range…|second line' -> caption spec."""
    lines = [[w.lstrip('*') if not w.startswith('*') else w for w in ln.split()] for ln in text.split('|')]
    spec = [[(w.lstrip('*'), 'hl' if w.startswith('*') else None) for w in ln] for ln in lines]
    FB.caption(c, spec, y=y, size=size)


def logo_small(c, x=905, y=170, w=240):
    lg = FB.logo()
    draw(c, lg, x, y, scale=w / lg.shape[1], opacity=0.95)


def tag(c, text, x=70, y=400):
    FB.tag(c, text, x, y, icon='pin')


# ------------------------------------------------------------------ the living map of Manchester
AREAS = [  # (name, dx, dy) offsets in px from Whalley Range on a stylised map (north up, roughly to scale)
    ('City Centre', 120, -330), ('Salford', -150, -400), ('Moss Side', 120, -140), ('Hulme', 90, -230),
    ('Old Trafford', -170, -130), ('Chorlton', -160, 190), ('Rusholme', 260, -60), ('Longsight', 400, -10),
    ('Levenshulme', 430, 170), ('Fallowfield', 280, 140), ('Didsbury', 250, 380), ('Stretford', -330, 40),
    ('Cheetham Hill', 200, -620), ('Sale', -230, 400), ('Withington', 210, 280), ('Ancoats', 300, -400),
]
WR = (470, 980)


def map_bg(k=1.0, lit=1.0):
    """Deep-green night map: soft street grid, the M60 ring, the Irwell, gold area labels that light as rings pass."""
    c = np.ones((H, W, 3), np.float32) * np.array(GREEN_D[:3], np.float32) * 0.9
    rng = np.random.default_rng(3)
    lay = np.zeros((H, W), np.uint8)
    for i in range(140):                                                    # organic streets
        x, y = rng.uniform(-100, W + 100), rng.uniform(100, H - 100)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(120, 420)
        pts = []
        for s in np.linspace(0, 1, 8):
            pts.append([x + math.cos(a) * L * s + math.sin(s * 6 + i) * 14, y + math.sin(a) * L * s + math.cos(s * 5 + i) * 14])
        cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], False, 255, 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.12
    c = c * (1 - m) + np.array(IVORY[:3], np.float32) * m
    lay = np.zeros((H, W), np.uint8)                                        # M60 ring road
    pts = [[WR[0] + 60 + 560 * math.cos(t) * (1 + 0.08 * math.sin(3 * t)), WR[1] - 150 + 760 * math.sin(t) * (1 + 0.06 * math.cos(2 * t))]
           for t in np.linspace(0, 2 * math.pi, 200)]
    cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], True, 255, 5 * 4, cv2.LINE_AA, shift=2)
    pts = [[WR[0] - 380 + 700 * s, WR[1] - 700 + 160 * math.sin(s * 7) + 260 * s] for s in np.linspace(0, 1, 60)]   # the river
    lay2 = np.zeros((H, W), np.uint8)
    cv2.polylines(lay2, [(np.array(pts) * 4).astype(np.int32)], False, 255, 9 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.22
    c = c * (1 - m) + np.array(GOLD[:3], np.float32) * m
    m = lay2.astype(np.float32)[..., None] / 255 * 0.35
    c = c * (1 - m) + np.array(TEAL[:3], np.float32) * m
    d = np.hypot(_X - WR[0], _Y - WR[1])
    c = c * (0.75 + 0.45 * np.exp(-(d / 700) ** 2)[..., None])
    return np.clip(c, 0, 1)


def map_labels(c, radius, soft=120):
    for name, dx, dy in AREAS:
        x, y = WR[0] + dx, WR[1] + dy
        on = float(np.clip((radius - math.hypot(dx, dy)) / soft, 0, 1))
        col = (1, 1, 1, 0.35 + 0.65 * on)
        if on > 0:
            glow(c, x, y, 50, LGOLD, 0.35 * on)
        dot = np.zeros((20, 20), np.uint8)
        cv2.circle(dot, (10, 10), 7, 255, -1, cv2.LINE_AA)
        draw(c, solid(dot.astype(np.float32) / 255, LGOLD if on > 0.5 else (1, 1, 1, 0.5)), x, y)
        s = ts(name, PS, 28, col)
        side = -1 if x + s.shape[1] + 30 > W - 40 else 1
        draw(c, s, x + side * (s.shape[1] / 2 + 18), y)


# ------------------------------------------------------------------ scenes (one per voice beat)
def s01():   # "From one room in Whalley Range…" (opening story: dawn footsteps towards the Centre)
    c = clip(4893, 0.4, fx=0.5, fy=0.6)
    c = daylight(c, 'dawn')
    c = top_shade(c, 0.25, 0.6)
    c = shade(c, 0.62, 0.8)
    tuner(c, 88.0)
    tag(c, 'WHALLEY RANGE · MANCHESTER', 70, 420)
    lg = load_png_sprite(f'{IMG}/Generated-Image-September-14-2025-9_38PM.png')
    card = FB.sprite_of(photo('Generated-Image-September-14-2025-9_38PM.png', 0.5, 0.45, 1.0, 470, 300), 28)
    FB.drop(c, rrect(490, 320, 36, WHITE), 760, 760, rot=4)
    FB.drop(c, card, 760, 760, rot=4)
    pop(c, 'pin', 760, 560, 200)
    cap(c, 'From one room in *Whalley *Range…')
    return c


def s02():   # (same line) the studio: ON AIR lamp switches on above the mic
    c = clip(24621, 0.5, fx=0.45, fy=0.5, z=1.05)
    c = daylight(c, 'studio')
    glow(c, 540, 620, 360, RED, 0.25)
    c = shade(c, 0.66, 0.75)
    tuner(c, 89.0)
    pop(c, 'onair', 540, 560, 460, rot=-3, col=RED)
    pop(c, 'mic', 860, 1080, 280)
    logo_small(c)
    cap(c, 'From one *room in Whalley Range…')
    return c


def s03():   # "…to the whole of Manchester." — the signal leaves the building and lights the map
    c = map_bg()
    rings(c, *WR, 0.35, n=5, rmax=1100)
    map_labels(c, 620)
    bld = FB.sprite_of(photo('Generated-Image-September-14-2025-9_38PM.png', 0.5, 0.5, 1.0, 300, 190), 20)
    draw(c, rrect(316, 206, 26, LGOLD), *WR)
    draw(c, bld, *WR)
    pop(c, 'mast', 850, 1190, 250)
    tuner(c, 89.8)
    cap(c, '…to the whole of *Manchester.')
    return c


def s04():   # "Spiritual talks and faith reflections…" — the kitchen radio switches on at dawn
    c = clip(43370, 0.35, fx=0.42, fy=0.5)
    c = daylight(c, 'morning')
    c = shade(c, 0.64, 0.8)
    tuner(c, 90.2)
    rings(c, 350, 820, 0.2, n=3, rmax=420)
    pop(c, 'radio', 760, 650, 380)
    pill(c, 'Spiritual talks · faith reflections', 540, 1250)
    cap(c, 'Spiritual talks and *faith *reflections|with your morning tea.')
    return c


def s05():   # "…with your morning tea."
    c = clip(45086, 0.5, fx=0.6, fy=0.5)
    c = daylight(c, 'morning')
    c = shade(c, 0.64, 0.75)
    tuner(c, 90.4)
    pop(c, 'tea', 800, 620, 320)
    FB.sparkle(c, 640, 520) if hasattr(FB, 'sparkle') else None
    cap(c, 'Spiritual talks and faith reflections|with your morning *tea.')
    return c


def lcd(c, x, y, text='90.6', w=330, h=130, a=1.0):
    """Dashboard radio display composited in the edit (amber segment-style readout)."""
    draw(c, rrect(w + 16, h + 16, 22, (0.08, 0.08, 0.08, 0.95)), x, y, opacity=a)
    draw(c, rrect(w, h, 16, (0.12, 0.07, 0.02, 1)), x, y, opacity=a)
    glow(c, x, y, w * 0.5, (1.0, 0.6, 0.15, 1), 0.25 * a)
    s = ts(text, PB, 84, (1.0, 0.72, 0.28, 1), 0.06)
    draw(c, blur_sprite(s, 6), x - 20, y, opacity=0.7 * a)
    draw(c, s, x - 20, y, opacity=a)
    draw(c, ts('FM', PS, 28, (1.0, 0.72, 0.28, 1)), x + w / 2 - 40, y + 24, opacity=a)


def s06():   # "Community news on the way to work." — rainy windscreen, dashboard reads 90.6
    c = clip(2846, 0.5, fx=0.55, fy=0.5)
    c = daylight(c, 'rain')
    c = shade(c, 0.62, 0.8)
    tuner(c, 90.6)
    lcd(c, 540, 980)
    pop(c, 'news', 790, 600, 330, rot=4)
    pill(c, 'Community news', 300, 760)
    cap(c, '*Community *news on the way to work.')
    return c


def s07():   # "Health, well-being,…" — a walk with headphones
    c = clip(4855, 0.5, fx=0.58, fy=0.5)
    c = daylight(c, 'midday')
    c = shade(c, 0.62, 0.8)
    tuner(c, 90.6)
    pop(c, 'heart', 300, 640, 260)
    pill(c, 'Health · well-being', 300, 830)
    cap(c, 'Health, *well-being, youth and|family conversations, wherever you are.', size=64)
    return c


def s08():   # "…youth and family conversations,…" — on the bus
    c = clip(46702, 0.5, fx=0.45, fy=0.5)
    c = daylight(c, 'midday')
    c = shade(c, 0.62, 0.8)
    tuner(c, 90.6)
    pop(c, 'bubbles', 760, 560, 320)
    pop(c, 'family', 300, 820, 260, rays=False)
    pill(c, 'Youth · family conversations', 540, 1150)
    cap(c, 'Health, well-being, youth and|*family *conversations, wherever you are.', size=64)
    return c


def s09():   # "…wherever you are." — three quick places: shop counter, street, bus (split triptych)
    c = np.zeros((H, W, 3), np.float32)
    panes = [(15914, 0.5, 0.45), (4855, 0.3, 0.55), (47203, 0.5, 0.5)]
    hh = (H - 40) // 3
    for i, (cid, t, fx) in enumerate(panes):
        sub = daylight(clip(cid, t, fx=fx, fy=0.5, w=W, h=hh), 'midday')
        c[20 + i * (hh + 10) - 10 * (i > 0):20 + i * (hh + 10) - 10 * (i > 0) + hh] = sub
    c = shade(c, 0.66, 0.85)
    tuner(c, 90.6)
    pop(c, 'speaker', 860, 470, 230)
    pop(c, 'earbuds', 220, 1060, 230)
    cap(c, 'Health, well-being, youth and|family conversations, *wherever *you *are.', size=64)
    return c


def s10():   # "Missed it? It's on the podcast." — evening, headphones
    c = clip(51134, 0.3, fx=0.5, fy=0.5)
    c = daylight(c, 'evening')
    c = shade(c, 0.62, 0.8)
    tuner(c, 90.6)
    pop(c, 'headphones', 760, 600, 340)
    pop(c, 'play', 330, 900, 210, rays=False)
    pill(c, 'YouTube · Spotify · Apple Podcasts', 540, 1230)
    cap(c, "Missed it? It's on the *podcast.")
    return c


def dusk_centre(fy=0.42, z=1.0):
    """The Centre at dusk: deep-blue sky, floodlit stone, warm lit windows (the daytime windows are the dark spots)."""
    day = photo('Generated-Image-September-14-2025-9_38PM.png', 0.5, fy, z, g=False)
    lum = day.mean(2)
    sky = np.clip((day[..., 2] - day[..., 0] + 0.02) * 12, 0, 1) * np.clip((lum - 0.45) * 5, 0, 1)
    sky = cv2.GaussianBlur(sky.astype(np.float32), (0, 0), 6)
    night = day * np.array([0.32, 0.38, 0.62], np.float32)
    flood = np.clip((_Y - 450) / 700, 0, 1)[..., None] * np.array([0.35, 0.24, 0.1], np.float32) * lum[..., None]
    c = night + flood
    grad = np.array([0.06, 0.1, 0.28], np.float32) * (1 - _Y[..., None] / H) + np.array([0.3, 0.25, 0.42], np.float32) * (_Y[..., None] / H)
    c = c * (1 - sky[..., None]) + grad * sky[..., None]
    facade = (np.abs(_X - 540) < 540) & (_Y > 380) & (_Y < 1180)
    win = np.clip((0.32 - lum) * 6, 0, 1) * facade * (1 - sky)
    win = cv2.GaussianBlur(win.astype(np.float32), (0, 0), 1.2)
    c = c * (1 - win[..., None]) + np.array([1.0, 0.72, 0.32], np.float32) * win[..., None]
    c = c + cv2.GaussianBlur(win, (0, 0), 14)[..., None] * np.array([0.9, 0.55, 0.2], np.float32) * 0.8
    return np.clip(c, 0, 1)


def s11():   # "Heritage Radio. To inform, inspire and elevate." — the Centre at dusk, rings flow back home
    c = dusk_centre()
    rings(c, 540, 760, 0.6, n=4, rmax=900, inward=True)
    c = shade(c, 0.62, 0.85)
    tuner(c, 90.6)
    for i, (nm, lab, x) in enumerate((('bulb', 'inform', 220), ('star', 'inspire', 540), ('arrow', 'elevate', 860))):
        pop(c, nm, x, 1060 - i * 40, 190, rays=(i == 2))
        chip(c, lab, x, 1200 - i * 40, fill=(1, 1, 1, 0.95), ink=GREEN_D, size=34, font=PB)
    cap(c, 'Heritage Radio. To inform, inspire|and *elevate.')
    return c


def s12():   # end card: "Tune in: ninety point six FM, DAB+ and the free app."
    c = FB.sacred_bg()
    rings(c, 540, 560, 0.3, n=4, rmax=600, alpha=0.5)
    tuner(c, 90.6, lock=1.0, y=330)
    big = ts('90.6 FM', PB, 170, WHITE)
    draw(c, blur_sprite(tint(big, LGOLD[:3]), 24), 540, 560, opacity=0.5)
    draw(c, big, 540, 560)
    draw(c, ts('DAB+ Manchester  ·  Online  ·  Free app', PM, 38, (1, 1, 1, 0.92)), 540, 690)
    b = rrect(560, 112, 56, MAG)
    draw(c, blur_sprite(b, 20), 540, 836, opacity=0.5)
    draw(c, b, 540, 820)
    draw(c, ts('Listen live', PB, 48, WHITE), 540, 820)
    draw(c, ts('Heritage Radio · inform, inspire, elevate', PS, 32, LGOLD), 540, 950)
    pop(c, 'phone', 850, 1120, 250, rays=False)
    pop(c, 'radio', 240, 1130, 240, rays=False)
    lg = FB.logo()
    draw(c, lg, 540, 1330, scale=420 / lg.shape[1])
    cap(c, 'Tune in: *ninety *point *six FM, DAB+|and the free app.', y=1450, size=58)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    which = [int(a) for a in sys.argv[1:]] or range(1, len(SCENES) + 1)
    for j in which:
        im = to_u8(SCENES[j - 1]())
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (270, 480), interpolation=cv2.INTER_AREA) for f in fs]
    while len(th) % 6:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 6]) for i in range(0, len(th), 6)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
