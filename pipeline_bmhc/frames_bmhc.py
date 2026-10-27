"""Scene images (one per voice beat) for BMHC "The First Word" — people + heritage story version.

Story: people walk through the gates of the British Muslim Heritage Centre in Whalley Range — a building that has been
a place of learning since 1843. A question pops up: what was the very first word of the Qur'an to be revealed? The
answer, "Iqra — Read", opens a journey along a golden pen line: Baghdad's House of Wisdom, al-Qarawiyyin in Fez, back to
Manchester 1843 and BMHC today. Whatever the voice says pops on screen (3D props, chips, cards).

Respect rules kept from BMHC's concept PDF: no depiction of the Prophet ﷺ, angels or Companions; verses shown as the
English translation with reference only (no typed / AI Qur'anic Arabic), quiet "sacred mode" for the verse beats, every
fact carries a source tag, the quiz answers that are not the answer simply fade (no crosses).

Usage: python3 frames_bmhc.py  -> workspace_bmhc/frames/scene_XX.png + storyboard.jpg
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pipeline_sol'))
import numpy as np
import cv2
import reel_sol as R
from reel_sol import W, H, draw, blur_sprite, tint, rrect, ts, solid, paste_spr, load_png_sprite, hexc, _wmask

S = os.path.abspath(os.path.join(HERE, '..', 'workspace_bmhc'))
OUT = f'{S}/frames'
IMG = f'{S}/web/img'

GREEN_D, IVORY, TEAL, GOLD = hexc('#122F2A'), hexc('#EFEEEA'), hexc('#09999C'), hexc('#DD9933')
MAG, ORANGE, GREEN = hexc('#DB225E'), hexc('#F26721'), hexc('#76BF43')
WHITE = (1.0, 1.0, 1.0, 1.0)
BARS = (MAG, TEAL, ORANGE, GREEN)                       # the four colour bars under BMHC's logo
PB, PX, PS, PM, PR = 'Poppins-Black', 'Poppins-ExtraBold', 'Poppins-SemiBold', 'Poppins-Medium', 'Poppins-Regular'
AR = 'AmiriAr-700'


# ------------------------------------------------------------------ sources
def grade(im, warm=1.0):
    """Heritage grade: deep-green shadows, warm golden highlights, gentle contrast."""
    lum = im.mean(2, keepdims=True)
    im = np.clip((im - 0.5) * 1.06 + 0.5, 0, 1)
    sh = np.clip(1 - lum * 2.0, 0, 1)
    hi = np.clip((lum - 0.55) * 2.2, 0, 1)
    im = im * (1 - 0.22 * sh) + np.array(GREEN_D[:3], np.float32) * 0.22 * sh
    im = im + hi * np.array([0.05, 0.025, -0.03], np.float32) * warm
    return np.clip(im, 0, 1).astype(np.float32)


def cover(im, fx=0.5, fy=0.5, z=1.0, w=W, h=H, sharpen=True):
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    cw, ch = w / sc, h / sc
    x0 = min(max(fx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(fy * ih - ch / 2, 0), ih - ch)
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    out = cv2.warpAffine(im, M, (int(w), int(h)), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if sharpen and sc > 1.5:
        bl = cv2.GaussianBlur(out, (0, 0), 1.6)
        out = np.clip(out * 1.45 - bl * 0.45, 0, 1)
    return out


def clip(cid, t=0.45, fx=0.5, fy=0.5, z=1.0, w=W, h=H):
    cap = cv2.VideoCapture(f'{S}/clips/{cid}.mp4')
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * t))
    ok, im = cap.read()
    return grade(cover(im[..., ::-1].astype(np.float32) / 255, fx, fy, z, w, h))


def photo(name, fx=0.5, fy=0.5, z=1.0, w=W, h=H, g=True):
    im = cv2.imread(f'{IMG}/{name}', cv2.IMREAD_COLOR)[..., ::-1].astype(np.float32) / 255
    im = cover(im, fx, fy, z, w, h)
    return grade(im) if g else im


def prop(name):
    return load_png_sprite(f'{S}/assets/{name}.png')


def sprite_of(im, r=34):
    """Photo -> rounded-corner RGBA sprite."""
    h, w = im.shape[:2]
    m = R.sdf_fill(R.rrect_alpha(w, h, r, 2))
    m = cv2.resize(m, (w, h)) if m.shape[:2] != (h, w) else m
    return np.concatenate([im * m[..., None], m[..., None]], 2).astype(np.float32)


# ------------------------------------------------------------------ shading / overlays
def shade(c, top=0.55, amt=0.85, col=GREEN_D):
    g = np.clip((R._Y / H - top) / (1 - top), 0, 1)[..., None] ** 1.3
    return c * (1 - amt * g) + np.array(col[:3], np.float32) * amt * g


def top_shade(c, h=0.2, amt=0.55):
    g = np.clip(1 - R._Y / (H * h), 0, 1)[..., None] ** 1.5
    return c * (1 - amt * g)


def sacred_bg():
    """Deep green with a faint eight-point geometric lattice (BMHC's own pattern language, no clichés)."""
    c = np.ones((H, W, 3), np.float32) * np.array(GREEN_D[:3], np.float32)
    lay = np.zeros((H, W), np.uint8)
    s = 180
    for gy in range(-1, H // s + 2):
        for gx in range(-1, W // s + 2):
            cx, cy = gx * s + (s // 2 if gy % 2 else 0), gy * s
            for rot in (0, 45):
                pts = []
                for k in range(4):
                    a = math.radians(rot + 45 + k * 90)
                    pts.append([cx + 56 * math.cos(a), cy + 56 * math.sin(a)])
                cv2.polylines(lay, [(np.array(pts) * 4).astype(np.int32)], True, 255, 2 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - 0.06 * m) + np.array(GOLD[:3], np.float32) * 0.06 * m
    d = np.hypot(R._X - W / 2, R._Y - H * 0.45) / (H * 0.7)
    c = c * (1.0 + 0.35 * np.clip(1 - d, 0, 1)[..., None] ** 2)
    return np.clip(c, 0, 1)


def glow(c, x, y, r, col=GOLD, amt=0.5):
    d = np.hypot(R._X - x, R._Y - y) / r
    g = np.exp(-d * d * 2.2)[..., None] * amt
    c[:] = c * (1 - g) + np.array(col[:3], np.float32) * g


def glass(c, x, y, w, h, r=36, tint_=(1, 1, 1), a=0.16, border=0.35):
    """Frosted-glass card: blurs what's behind it, adds a light fill and a hairline border."""
    x0, y0 = int(x - w / 2), int(y - h / 2)
    x1, y1 = x0 + int(w), y0 + int(h)
    if x1 <= 0 or y1 <= 0 or x0 >= c.shape[1] or y0 >= c.shape[0]:
        return
    sub = c[max(0, y0):y1, max(0, x0):x1]
    bl = cv2.GaussianBlur(sub, (0, 0), 22)
    m = R.sdf_fill(R.rrect_alpha(int(w), int(h), r, 2))
    m = cv2.resize(m, (int(w), int(h)))[max(0, -y0):, max(0, -x0):][:sub.shape[0], :sub.shape[1], None]
    sub[:] = sub * (1 - m) + (bl * (1 - a) + np.array(tint_, np.float32) * a) * m
    st = R.sdf_stroke(R.rrect_alpha(int(w), int(h), r, 2), 1.5) if hasattr(R, 'sdf_stroke') else None
    if st is not None:
        draw(c, solid(cv2.resize(st, (int(w), int(h))), (1, 1, 1, border)), x, y)


def drop(c, spr, x, y, sc=1.0, rot=0, sh=0.45, sigma=18):
    draw(c, blur_sprite(tint(spr, (0.0, 0.05, 0.04)), sigma), x + 8, y + 22, scale=sc, rot=rot, opacity=sh)
    draw(c, spr, x, y, scale=sc, rot=rot)


def pop(c, spr, x, y, sc=1.0, rays=True, col=GOLD):
    """A popped-in object: gold burst rays, soft shadow."""
    if rays:
        lay = np.zeros((H, W), np.uint8)
        r0 = max(spr.shape[:2]) * sc * 0.44
        for j in range(12):
            a = j / 12 * 2 * math.pi + 0.15
            ln = 30 if j % 2 else 46
            cv2.line(lay, (int((x + math.cos(a) * r0) * 4), int((y + math.sin(a) * r0) * 4)),
                     (int((x + math.cos(a) * (r0 + ln)) * 4), int((y + math.sin(a) * (r0 + ln)) * 4)), 255, 5 * 4,
                     cv2.LINE_AA, shift=2)
        m = lay.astype(np.float32)[..., None] / 255 * 0.9
        c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    drop(c, spr, x, y, sc)


def chip(c, text, x, y, fill=TEAL, ink=WHITE, size=40, rot=0, font=PX, dot=None, opacity=1.0):
    s = ts(text, font, size, ink, 0.02)
    pad = 60 if dot else 0
    p = rrect(s.shape[1] + 60 + pad, s.shape[0] + 36, (s.shape[0] + 36) / 2, fill).copy()
    if dot:
        paste_spr(p, rrect(22, 22, 11, dot), 40, p.shape[0] / 2)
    paste_spr(p, s, 30 + pad + s.shape[1] / 2, p.shape[0] / 2)
    draw(c, blur_sprite(tint(p, (0, 0.04, 0.03)), 12), x + 6, y + 12, rot=rot, opacity=0.45 * opacity)
    draw(c, p, x, y, rot=rot, opacity=opacity)
    return p.shape[1]


def bars(c, x, y, w=320, h=12, gap=6):
    seg = (w - gap * 3) / 4
    for j, col in enumerate(BARS):
        draw(c, rrect(seg, h, h / 2, col), x + seg / 2 + j * (seg + gap), y)


def progress(c, k, n=13):
    """Story progress bar along the top, in the four logo colours."""
    seg = (W - 120 - (n - 1) * 8) / n
    for j in range(n):
        col = BARS[j % 4] if j < k else (1, 1, 1, 0.28)
        draw(c, rrect(seg, 7, 3.5, col), 60 + seg / 2 + j * (seg + 8), 64)


def tag(c, text, x=70, y=170, icon=None):
    """Location / date tag: glass pill with the four colour bars underneath."""
    s = ts(text, PS, 30, WHITE, 0.16)
    w = s.shape[1] + 70 + (40 if icon else 0)
    glass(c, x + w / 2, y, w, 70, 35, a=0.2)
    xx = x + 35
    if icon == 'pin':
        m = np.zeros((48, 36), np.uint8)
        cv2.circle(m, (18, 16), 14, 255, -1, cv2.LINE_AA)
        cv2.fillPoly(m, [np.array([[6, 22], [30, 22], [18, 44]])], 255, cv2.LINE_AA)
        cv2.circle(m, (18, 16), 6, 0, -1, cv2.LINE_AA)
        draw(c, solid(m.astype(np.float32) / 255, GOLD), xx + 14, y)
        xx += 40
    draw(c, s, xx + s.shape[1] / 2, y)
    bars(c, x + 20, y + 52, min(w - 40, 260), 6, 5)


def source(c, text, x=None, y=1840):
    s = ts('SOURCE · ' + text, PM, 24, (1, 1, 1, 0.92), 0.08)
    w = s.shape[1] + 44
    x = W - 60 - w / 2 if x is None else x
    draw(c, rrect(w, 50, 25, (0.03, 0.12, 0.1, 0.72)), x, y)
    draw(c, s, x, y)


def words_line(spec, size):
    """spec: [(word, style)] style: None | 'gold' | 'hl' (teal highlight pill) | 'ar' (Arabic glyph run)."""
    out = []
    for w, st in spec:
        if st == 'ar':
            out.append((solid(_wmask(w, AR, int(size * 1.0)), GOLD), st))
        else:
            out.append((solid(_wmask(w, PX, size), GOLD if st == 'gold' else WHITE), st))
    return out


def caption(c, lines, y=1560, size=78, x0=80):
    """Lower caption: Poppins ExtraBold; key words gold, or on a teal highlight pill. Shrinks to fit the frame."""
    while size > 40:
        wmax = max(sum(sp.shape[1] for sp, _ in words_line(l, size)) + size * 0.18 * (len(l) - 1) for l in lines)
        if wmax <= W - 2 * x0:
            break
        size -= 2
    for li, line in enumerate(lines):
        x = x0
        yy = y + li * size * 1.22
        for s, st in words_line(line, size):
            if st == 'hl':
                draw(c, rrect(s.shape[1] + 8, size * 1.08, 16, TEAL), x + s.shape[1] / 2, yy + 2)
            else:
                draw(c, blur_sprite(tint(s, (0, 0.03, 0.02)), 10), x + s.shape[1] / 2 + 3, yy + 6, opacity=0.5)
            draw(c, s, x + s.shape[1] / 2, yy)
            x += s.shape[1] + size * 0.18


def search_bar(c, text, y=760, w=940, caret=True, size=40, sub=None):
    """Glass search bar with a magnifier, typed question, and a caret."""
    lines = text if isinstance(text, list) else [text]
    hgt = 70 + len(lines) * size * 1.3
    drop(c, rrect(w, hgt, 44, (1, 1, 1, 0.97)), W / 2, y, sh=0.5, sigma=26)
    m = np.zeros((60, 60), np.uint8)
    cv2.circle(m, (24, 24), 16, 255, 5, cv2.LINE_AA)
    cv2.line(m, (36, 36), (52, 52), 255, 7, cv2.LINE_AA)
    draw(c, solid(m.astype(np.float32) / 255, TEAL), W / 2 - w / 2 + 62, y - hgt / 2 + 35 + size * 0.65)
    x0 = W / 2 - w / 2 + 112
    for li, ln in enumerate(lines):
        s = ts(ln, PS, size, GREEN_D, 0.0)
        yy = y - hgt / 2 + 35 + size * 0.65 + li * size * 1.3
        draw(c, s, x0 + s.shape[1] / 2, yy)
        if caret and li == len(lines) - 1:
            draw(c, rrect(5, size * 1.1, 2, TEAL), x0 + s.shape[1] + 12, yy)
    if sub:
        s = ts(sub, PM, 26, (1, 1, 1, 0.9), 0.1)
        draw(c, s, W / 2, y + hgt / 2 + 44)


def counter_ring(c, x, y, r, frac, label, col=GOLD):
    lay = np.zeros((H, W), np.uint8)
    cv2.circle(lay, (int(x * 4), int(y * 4)), int(r * 4), 255, 14 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255 * 0.3
    c[:] = c * (1 - m) + m
    lay[:] = 0
    cv2.ellipse(lay, (int(x * 4), int(y * 4)), (int(r * 4), int(r * 4)), -90, 0, 360 * frac, 255, 14 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + np.array(col[:3], np.float32) * m
    s = ts(label, PB, int(r * 0.9), WHITE)
    draw(c, s, x, y)


def logo(white=True):
    """BMHC logo (line-art building + wordmark) with its four colour bars."""
    lw = load_png_sprite(f'{IMG}/bmhc-white-logo.png')
    lc = load_png_sprite(f'{IMG}/Website-1-2.png')
    h = lw.shape[0]
    cut = int(h * 0.86)                                  # the colour bars live in the bottom ~14%
    out = lw.copy()
    out[cut:] = lc[cut:]
    if not white:
        out[:cut] = tint(lw[:cut], GREEN_D[:3])
    big = cv2.resize(out, (out.shape[1] * 3, out.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
    bl = cv2.GaussianBlur(big, (0, 0), 1.2)
    return np.clip(big * 1.4 - bl * 0.4, 0, 1)


def pen_line(c, pts, col=GOLD, w=6, amt=1.0):
    """Gold pen line (the thread that links every stop of the journey)."""
    lay = np.zeros((H, W), np.uint8)
    p = np.array(pts, np.float32)
    t = np.linspace(0, 1, 120)
    curve = []
    for i in range(len(p) - 1):                          # smooth with a Catmull-Rom spline
        p0, p1, p2, p3 = p[max(i - 1, 0)], p[i], p[i + 1], p[min(i + 2, len(p) - 1)]
        for u in t:
            curve.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u +
                                (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    cv2.polylines(lay, [(np.array(curve) * 4).astype(np.int32)], False, 255, int(w * 4), cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    g = cv2.GaussianBlur(m[..., 0], (0, 0), 12)[..., None] * 0.6
    c[:] = c * (1 - g * amt) + np.array(col[:3], np.float32) * g * amt
    c[:] = c * (1 - m * amt) + np.array((1.0, 0.85, 0.5), np.float32) * m * amt
    return np.array(curve)


def sparkle(c, x, y, r=26, col=(1, 0.95, 0.8)):
    m = np.zeros((int(r * 4), int(r * 4)), np.float32)
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]].astype(np.float32) - r * 2
    m = np.clip(1 - (np.abs(xx) * np.abs(yy)) ** 0.5 / (r * 0.35), 0, 1) * np.clip(1 - np.hypot(xx, yy) / (r * 2), 0, 1)
    draw(c, solid(m, (*col, 1.0)), x, y)


# ------------------------------------------------------------------ the story, beat by beat
def s01():   # "Every day, people walk through these gates in Whalley Range..."
    c = photo('W6A9208-1-scaled.jpg', fx=0.52, fy=0.5, z=1.0)
    c = shade(top_shade(c), 0.5)
    tag(c, 'WHALLEY RANGE · MANCHESTER', 70, 190, icon='pin')
    caption(c, [[('Every', None), ('day,', None), ('people', 'gold')], [('walk', None), ('through', None), ('these', None)],
                [('gates', 'hl'), ('...', None)]], y=1440, size=86)
    return c


def s02():   # "...into a building that's been a place of learning since 1843."
    c = photo('bhmc-f.png', fx=0.5, fy=0.5, z=1.0)
    c = shade(top_shade(c), 0.52)
    old = photo('BMHC-Year-1866.jpg', fx=0.55, fy=0.5, w=560, h=380, g=False)
    old = old.mean(2, keepdims=True) * np.array([1.0, 0.94, 0.82], np.float32)
    card = sprite_of(old, 22)
    frame = rrect(584, 404, 30, IVORY)
    drop(c, frame, 720, 560, rot=-4)
    draw(c, card, 720, 560, rot=-4)
    chip(c, 'Since 1843', 820, 790, fill=GOLD, ink=GREEN_D, size=44, rot=-4)
    caption(c, [[('A', None), ('place', None), ('of', None), ('learning', 'gold')], [('since', None), ('1843.', 'hl')]],
            y=1520, size=86)
    return c


def s03():   # "But here's a question. What was the very first word of the Qur'an to be revealed?"
    c = clip(8800, 0.5, fx=0.55, fy=0.5)
    c = shade(c, 0.45, 0.9)
    search_bar(c, ['What was the very first word', "of the Qur'an to be revealed?"], y=1180, size=44,
               sub='ASK YOURSELF FIRST')
    chip(c, 'A quick question', 300, 940, fill=MAG, size=38, rot=-3)
    return c


def s04():   # "Pray? Fast? Read? Give? Take a guess."
    c = clip(49306, 0.5, fx=0.5, fy=0.4)
    c = shade(c, 0.5, 0.88)
    for (t, col, x, y, r) in (('Pray', MAG, 250, 1140, -4), ('Fast', ORANGE, 800, 1080, 3), ('Read', TEAL, 300, 1300, 2),
                              ('Give', GREEN, 790, 1270, -3)):
        chip(c, t + '?', x, y, fill=col, size=58, rot=r)
    counter_ring(c, W / 2, 1530, 90, 0.66, '3')
    s = ts('TAKE A GUESS', PX, 40, WHITE, 0.2)
    draw(c, s, W / 2, 1690)
    return c


def s05():   # "It was Iqra. Read. Revealed to the Prophet Muhammad, peace be upon him."
    c = clip(34275, 0.45, fx=0.45, fy=0.55)
    c = shade(c, 0.4, 0.9)
    for (t, x, y) in (('Pray?', 250, 600), ('Fast?', 800, 560), ('Give?', 790, 760)):
        chip(c, t, x, y, fill=(1, 1, 1, 0.25), size=44, opacity=0.5)
    glow(c, 330, 760, 220, TEAL, 0.35)
    chip(c, 'Read.', 330, 760, fill=TEAL, size=72)
    s = ts('IQRA', PB, 210, GOLD, 0.06)
    drop(c, s, W / 2, 1180)
    s2 = ts('the first word', PM, 44, (1, 1, 1, 0.92), 0.1)
    draw(c, s2, W / 2, 1320)
    line = [('revealed', None), ('to', None), ('the', None), ('Prophet', None), ('Muhammad', 'gold'), ('ﷺ', 'ar')]
    caption(c, [line[:3], line[3:]], y=1520, size=68)
    source(c, 'Sahih al-Bukhari 3')
    return c


def s06():   # SACRED MODE — "Read! In the name of your Lord who created." (no music, no SFX, no people)
    c = sacred_bg()
    glow(c, W / 2, 1180, 360, GOLD, 0.25)
    b = prop('book')
    drop(c, b, W / 2, 1250, 1.05, sh=0.35)
    ty = 560
    for ln in ('“Read! In the name', 'of your Lord', 'who created.”'):
        s = ts(ln, 'Poppins-SemiBold', 76, IVORY, 0.0)
        draw(c, s, W / 2, ty)
        ty += 100
    s = ts("AL-'ALAQ 96:1", PX, 32, GOLD, 0.25)
    draw(c, s, W / 2, 900)
    s = ts('trans. M.A.S. Abdel Haleem', PR, 26, (1, 1, 1, 0.65), 0.04)
    draw(c, s, W / 2, 1610)
    bars(c, W / 2 - 160, 1680, 320, 8, 6)
    return c


def s07():   # "...who taught by means of the pen." (96:4) — the pen becomes the gold line of knowledge
    c = clip(50700, 0.55, fx=0.48, fy=0.5)
    c = c * 0.55 + np.array(GREEN_D[:3], np.float32) * 0.45
    pts = [(120, 1500), (300, 1300), (520, 1380), (700, 1150), (900, 1050), (1000, 820)]
    curve = pen_line(c, pts, w=7)
    for p in curve[::90]:
        sparkle(c, p[0], p[1], 18)
    q = prop('quill')
    glow(c, 820, 860, 260, GOLD, 0.25)
    pop(c, q, 820, 860, 1.25)
    ty = 330
    for ln in ('“who taught', 'by [means of]', 'the pen”'):
        s = ts(ln, 'Poppins-SemiBold', 74, IVORY)
        draw(c, s, 80 + s.shape[1] / 2, ty)
        ty += 96
    chip(c, "AL-'ALAQ 96:4", 210, ty + 20, fill=GOLD, ink=GREEN_D, size=30)
    caption(c, [[('The', None), ('pen', 'hl'), ('drew', None), ('a', None), ('line...', None)]], y=1700, size=70)
    return c


def s08():   # "...through Baghdad's House of Wisdom, where al-Khwarizmi gave us algebra."
    c = clip(24632, 0.5, fx=0.5, fy=0.5)
    c = shade(top_shade(c), 0.5, 0.85)
    pen_line(c, [(-20, 380), (300, 330), (600, 420), (1100, 300)], w=5, amt=0.9)
    tag(c, 'BAGHDAD · 9TH CENTURY', 70, 190, icon='pin')
    pop(c, prop('astrolabe'), 800, 640, 0.85)
    glass(c, W / 2, 1100, 900, 300, 40, a=0.18)
    s = ts('House of Wisdom', PX, 64, WHITE)
    draw(c, s, W / 2, 1010)
    ar = solid(_wmask('الجبر', AR, 96), GOLD)
    draw(c, ar, 300, 1150)
    m = np.zeros((40, 120), np.uint8)
    cv2.line(m, (6, 20), (100, 20), 255, 6, cv2.LINE_AA)
    cv2.fillPoly(m, [np.array([[96, 6], [116, 20], [96, 34]])], 255, cv2.LINE_AA)
    draw(c, solid(m.astype(np.float32) / 255, WHITE), 500, 1160)
    s = ts('algebra', PX, 76, TEAL)
    draw(c, s, 720, 1150)
    chip(c, 'al-Khwārizmī', 300, 1340, fill=GOLD, ink=GREEN_D, size=44, rot=-3)
    chip(c, 'Algoritmi', 640, 1440, fill=(1, 1, 1, 0.9), ink=GREEN_D, size=38, rot=2)
    chip(c, 'algorithm', 870, 1520, fill=TEAL, size=38, rot=-2)
    caption(c, [[('Baghdad\'s', None), ('House', 'gold'), ('of', 'gold'), ('Wisdom.', 'gold')]], y=1660, size=70)
    return c


def s09():   # "...to Fez, where Fatima al-Fihri founded al-Qarawiyyin in 859 — still teaching today."
    c = clip(45772, 0.5, fx=0.5, fy=0.5)
    c = shade(top_shade(c), 0.42, 0.9)
    tag(c, 'FEZ · 859 CE', 70, 190, icon='pin')
    glow(c, W / 2, 760, 330, GOLD, 0.3)
    pop(c, prop('arch'), W / 2, 760, 0.95)
    chip(c, 'Fatima al-Fihri', 300, 1120, fill=MAG, size=46, rot=-3)
    chip(c, 'al-Qarawiyyin', 780, 1200, fill=TEAL, size=46, rot=2)
    glass(c, W / 2, 1400, 760, 120, 60, a=0.2)
    draw(c, rrect(22, 22, 11, GREEN), W / 2 - 300, 1400)
    s = ts('Still teaching · 1,167 years', PX, 46, WHITE)
    draw(c, s, W / 2 + 20, 1400)
    caption(c, [[('The', None), ('world\'s', None), ('oldest', 'gold'), ('university.', 'hl')]], y=1640, size=66)
    source(c, 'Guinness World Records')
    return c


def s10():   # "...and back to Manchester, 1843 — where this building first opened as a college."
    c = photo('Dut-kbsW4AIRs6T.jpg', fx=0.5, fy=0.4, z=1.0)
    old = photo('BMHC-Year-1855-before-photography.jpg', fx=0.5, fy=0.4, z=1.0, g=False)
    old = old.mean(2, keepdims=True) * np.array([1.0, 0.93, 0.8], np.float32) * np.ones(3, np.float32)
    k = np.clip((R._X - (W * 0.5 + (R._Y - H / 2) * 0.25)) / 6 + 0.5, 0, 1)[..., None]     # diagonal wipe then → now
    c = old * (1 - k) + c * k
    lay = np.zeros((H, W), np.uint8)
    cv2.line(lay, (int((W * 0.5 - H / 2 * 0.25) * 4), 0), (int((W * 0.5 + H / 2 * 0.25) * 4), H * 4), 255, 8 * 4, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c = c * (1 - m) + np.array(GOLD[:3], np.float32) * m
    c = shade(top_shade(c), 0.55, 0.85)
    tag(c, 'MANCHESTER · 1843', 70, 190, icon='pin')
    chip(c, 'THEN', 260, 1180, fill=IVORY, ink=GREEN_D, size=40, rot=-3)
    chip(c, 'NOW', 840, 1180, fill=TEAL, size=40, rot=3)
    caption(c, [[('Lancashire', None), ('Independent', None)], [('College,', 'gold'), ('1843.', 'hl')]], y=1500, size=74)
    return c


def s11():   # "Today, it's the British Muslim Heritage Centre — Qur'an classes, study circles, exhibitions and youth clubs."
    c = np.ones((H, W, 3), np.float32) * np.array(IVORY[:3], np.float32)
    c = c - R.grid_layer()[:H, :W][..., None] * 0.05
    panels = (('Screenshot-2025-10-26-033526.png', 300, 520, -3, "Qur'an classes", TEAL, 0.5, 0.5),
              ('MAS09785-scaled.jpg', 780, 600, 3, 'Study circles', GREEN, 0.5, 0.45),
              ('487090267_1088144326686714_8941517225088640181_n.jpg', 300, 1050, 2, 'Exhibitions', ORANGE, 0.45, 0.6),
              ('scouts.jpg', 780, 1130, -3, 'Youth clubs', MAG, 0.5, 0.4))
    for name, x, y, rot, label, col, fx, fy in panels:
        im = photo(name, fx=fx, fy=fy, w=440, h=420)
        drop(c, rrect(464, 444, 34, WHITE), x, y, rot=rot, sh=0.3)
        draw(c, sprite_of(im, 26), x, y, rot=rot)
        chip(c, label, x, y + 230, fill=col, size=36, rot=rot)
    s = ts('130K+', PB, 150, GREEN_D, 0.0)
    draw(c, s, W / 2, 1540)
    s = ts('VISITORS EVERY YEAR', PX, 36, TEAL, 0.25)
    draw(c, s, W / 2, 1650)
    bars(c, W / 2 - 200, 1730, 400, 10, 8)
    tag_ = ts('TODAY · BRITISH MUSLIM HERITAGE CENTRE', PS, 28, GREEN_D, 0.14)
    draw(c, tag_, W / 2, 170)
    return c


def s12():   # "It all began with one word. So, what will you read next?"
    c = clip(6049, 0.5, fx=0.5, fy=0.55)
    c = shade(top_shade(c), 0.35, 0.92)
    glow(c, 860, 300, 220, TEAL, 0.3)
    pop(c, prop('star'), 860, 300, 0.5, rays=False)
    caption(c, [[('It', None), ('all', None), ('began', None), ('with', None)], [('one', 'gold'), ('word.', 'hl')]],
            y=1060, size=84)
    search_bar(c, 'So, what will you read next?', y=1450, size=44, sub='TELL US IN THE COMMENTS')
    return c


def s13():   # end card — "Find a class at bmhc.org.uk"
    c = sacred_bg()
    glow(c, W / 2, 700, 420, TEAL, 0.18)
    lg = logo()
    draw(c, lg, W / 2, 640, scale=0.95)
    s = ts('Find a class at', PM, 52, (1, 1, 1, 0.9))
    draw(c, s, W / 2, 1020)
    drop(c, rrect(720, 120, 60, GOLD), W / 2, 1140, sh=0.4)
    s = ts('bmhc.org.uk', PB, 64, GREEN_D)
    draw(c, s, W / 2, 1140)
    for j, ln in enumerate(('College Road, Whalley Range', 'Manchester M16 8BP')):
        s = ts(ln, PM, 36, (1, 1, 1, 0.75), 0.04)
        draw(c, s, W / 2, 1330 + j * 56)
    for j, (t, col) in enumerate((('Learn', TEAL), ('Meet', MAG), ('Belong', GREEN))):
        chip(c, t, W / 2 - 290 + j * 290, 1560, fill=col, size=38)
    return c


SCENES = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13]


def to_u8(im):
    return (np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = [int(a) for a in sys.argv[1:]]
    for j, fn in enumerate(SCENES, start=1):
        if only and j not in only:
            continue
        c = fn()
        if j not in (6, 13):
            progress(c, j)
        im = to_u8(R.post(c, j, bloom=0.12, grain=0.012, vig=0.3 if j not in (11,) else 0.0))
        cv2.imwrite(f'{OUT}/scene_{j:02d}.png', im)
        print('scene', j, flush=True)
    import glob
    fs = sorted(glob.glob(f'{OUT}/scene_*.png'))
    th = [cv2.resize(cv2.imread(f), (324, 576)) for f in fs]
    while len(th) % 7:
        th.append(np.zeros_like(th[0]))
    cv2.imwrite(f'{OUT}/storyboard.jpg', np.vstack([np.hstack(th[i:i + 7]) for i in range(0, len(th), 7)]),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
