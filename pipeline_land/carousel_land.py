"""OF carousel "A safe place to land" - after the user's Pinterest reference: a seamless 5-slide carousel on a clean
light ground, one bold continuous path running across every slide, a 3D object travelling along it, light caps with
one bold phrase on top and a small line underneath. OF version: a child's paper aeroplane (OF orange) whose trail is a
thick plum line that loops, passes small 3D things and lands at a house; ends on "Start your enquiry".

Outputs (reel/organic_fostering/safe_place_to_land/): slide_1..5.jpg (static, 1080x1350) and slide_1..5.mp4 (the plane
flying its part of the path, 5 s each), plus swipe_preview.mp4 (all five slides swiped through).
Usage: python3 carousel_land.py [stills]
"""
import os, sys, math, functools, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/reel/organic_fostering/safe_place_to_land'
WS = f'{ROOT}/workspace_land'
os.makedirs(OUT, exist_ok=True)
SW, SH, N = 1080, 1350, 5
PW = SW * N


def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


IVORY, PLUM, MAG, ORANGE, GREEN, CHAR = hx('#FCF8F5'), hx('#5B174F'), hx('#B7006E'), hx('#FF6411'), hx('#61A80A'), hx('#2B2B2B')


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_inout(u):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def e_back(u, s=1.7):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', int(s))


@functools.lru_cache(maxsize=256)
def text(s, w, size, col, track=0.0):
    f = F(w, size)
    asc, desc = f.getmetrics()
    widths = [f.getlength(ch) for ch in s]
    tw = sum(widths) + track * size * max(0, len(s) - 1)
    im = Image.new('L', (int(tw + 24), asc + desc + 24), 0)
    d = ImageDraw.Draw(im)
    x = 12
    for ch, cw in zip(s, widths):
        d.text((x, 12), ch, font=f, fill=255)
        x += cw + track * size
    a = np.asarray(im, np.float32) / 255
    ys, xs = np.where(a > 0.01)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.dstack([a[..., None] * np.array(col, np.float32), a])


def paste(c, spr, cx, cy, a=1.0):
    sh, sw = spr.shape[:2]
    x0, y0 = int(round(cx - sw / 2)), int(round(cy - sh / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(c.shape[1], x0 + sw), min(c.shape[0], y0 + sh)
    if X1 <= X0 or Y1 <= Y0 or a <= 0:
        return c
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = s[..., 3:4] * a
    reg = c[Y0:Y1, X0:X1]
    if c.shape[2] == 4:
        reg[..., :3] = reg[..., :3] * (1 - al) + s[..., :3] * a
        reg[..., 3:4] = reg[..., 3:4] * (1 - al) + al
    else:
        reg[:] = reg * (1 - al) + s[..., :3] * a
    return c


def xform(spr, scale=1.0, rot=0.0):
    if abs(scale - 1) < 1e-3 and abs(rot) < 1e-3:
        return spr
    h, w = spr.shape[:2]
    D = int(math.hypot(w, h) * scale) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += D / 2 - w / 2
    M[1, 2] += D / 2 - h / 2
    return cv2.warpAffine(spr, M, (D, D), flags=cv2.INTER_LINEAR)


@functools.lru_cache(maxsize=32)
def obj(path, size, crop_thr=0.5):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    solid = (im[..., 3] > crop_thr).astype(np.uint8)
    keep = np.clip(cv2.GaussianBlur(cv2.dilate(solid, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2) * 1.2, 0, 1)
    im[..., 3] *= keep
    ys, xs = np.where(im[..., 3] > 0.5)
    im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    sc = size / max(im.shape[:2])
    im = cv2.resize(im, (max(1, int(im.shape[1] * sc)), max(1, int(im.shape[0] * sc))), interpolation=cv2.INTER_AREA)
    return np.dstack([im[..., 2::-1] * im[..., 3:4], im[..., 3]]).astype(np.float32)


def shadowed(spr, blur=16, off=(10, 26), amt=0.28):
    h, w = spr.shape[:2]
    p = blur * 3 + max(off)
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    sh = np.zeros(out.shape[:2], np.float32)
    sh[p + off[1]:p + off[1] + h, p + off[0]:p + off[0] + w] = spr[..., 3]
    out[..., 3] = cv2.GaussianBlur(sh, (0, 0), blur) * amt
    reg = out[p:p + h, p:p + w]
    a = spr[..., 3:4]
    reg[..., :3] = spr[..., :3] + reg[..., :3] * (1 - a)
    reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)
    return out


# ------------------------------------------------------------------ the path (Catmull-Rom through hand-placed points)
CTRL = [(470, 800), (700, 760), (980, 640), (1240, 600), (1500, 560), (1720, 430), (1850, 600), (1700, 790), (1520, 660),
        (1640, 470), (1900, 560), (2160, 700), (2420, 830), (2700, 730), (2980, 860), (3240, 790), (3520, 700), (3760, 790),
        (3950, 950), (4130, 1080), (4380, 1110), (4620, 1080), (4820, 1070)]


def catmull(pts, n=40):
    P = np.array([pts[0]] + pts + [pts[-1]], np.float32)
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out, np.float32)


PATH = catmull(CTRL)
SEG = np.r_[0, np.cumsum(np.hypot(*np.diff(PATH, axis=0).T))]
TOTAL = SEG[-1]
LW = 62


def at(s):
    """Point and heading (deg, image coords) at arc length s."""
    s = clamp(s, 0, TOTAL - 1e-3)
    i = int(np.searchsorted(SEG, s) - 1)
    i = max(0, min(i, len(PATH) - 2))
    f = (s - SEG[i]) / max(1e-6, SEG[i + 1] - SEG[i])
    p = PATH[i] * (1 - f) + PATH[i + 1] * f
    d = PATH[min(i + 3, len(PATH) - 1)] - PATH[max(i - 2, 0)]
    return p, math.degrees(math.atan2(d[1], d[0]))


def arc_at_x(x):
    """First arc length where the path crosses panorama x (for slide boundaries)."""
    idx = np.where(PATH[:, 0] >= x)[0]
    return SEG[idx[0]] if len(idx) else TOTAL


def draw_path(c, s_end, xoff=0):
    """Thick plum line from the start up to arc length s_end (c is a slide or the whole panorama)."""
    k = int(np.searchsorted(SEG, s_end))
    if k < 2:
        return
    pts = PATH[:k].copy()
    p, _ = at(s_end)
    pts = np.vstack([pts, p])
    pts[:, 0] -= xoff
    lay = np.zeros(c.shape[:2], np.uint8)
    cv2.polylines(lay, [(pts * 4).astype(np.int32)], False, 255, LW, cv2.LINE_AA, shift=2)
    m = lay.astype(np.float32)[..., None] / 255
    c[:] = c * (1 - m) + PLUM * m


# ------------------------------------------------------------------ assets
PLANE = f'{WS}/assets/plane.png'
LAND_X = 3730
NOSE = -7.0                                         # the render's nose heading (deg, image coords)
HOUSE = f'{ROOT}/workspace_page/assets/house.png'
BOOK = f'{ROOT}/workspace_page/assets/book3q.png'
HEART = f'{ROOT}/workspace_fridge/props/heart.png'
STAR = f'{ROOT}/workspace_fridge/props/star.png'
CRAYON = f'{ROOT}/workspace_fridge/props/crayon_green.png'
LOGO = f'{ROOT}/workspace_three/web/logo.png'

PROPS = [(BOOK, 2330, 250, -6), (HEART, 2700, 150, -10), (CRAYON, 2900, 190, 20), (STAR, 3110, 120, 15)]   # (asset, x on path, size, rot)


def plane_spr(heading, size=300, scale=1.0):
    sp = obj(PLANE, size)
    return xform(shadowed(sp, 14, (8, 30), 0.22), scale, -(heading - NOSE))


def prop_at(x):
    s = arc_at_x(x)
    p, hd = at(s)
    return p, s


# ------------------------------------------------------------------ slide content
def headline(c, light, bold, y=150):
    s1 = text(light, 400, 54, tuple(CHAR), 0.04)
    s2 = text(bold, 900, 66, tuple(PLUM), 0.03)
    paste(c, s1, SW / 2, y)
    paste(c, s2, SW / 2, y + 80)


def subline(c, s, y=1240):
    paste(c, text(s, 700, 34, tuple(CHAR)), SW / 2, y)


@functools.lru_cache(None)
def logo_spr(width):
    lg = cv2.imread(LOGO, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    lg = cv2.resize(lg, (width, int(lg.shape[0] * width / lg.shape[1])), interpolation=cv2.INTER_AREA)
    return np.dstack([lg[..., 2::-1] * lg[..., 3:4], lg[..., 3]]).astype(np.float32)


def button(c, t_glow=0.0):
    f = F(800, 46)
    tw = f.getlength('Start your enquiry')
    w, h = int(tw + 110), 112
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.rectangle(m, (h * 2, 0), (w * 4 - h * 2, h * 4), 255, -1)
    for x in (h * 2, w * 4 - h * 2):
        cv2.circle(m, (x, h * 2), h * 2, 255, -1, cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    spr = np.dstack([m[..., None] * PLUM, m])
    paste(spr, text('Start your enquiry', 800, 46, tuple(IVORY)), w / 2, h / 2)
    s = 1 + 0.05 * t_glow
    paste(c, xform(shadowed(spr, 14, (0, 16), 0.25), s), BTN[0], BTN[1])


BTN = (4900 - 4 * SW + 0, 1070)        # slide-5 coordinates of the button centre (path ends at its left edge)
BTN = (560, 1070)


def slide_static(i, c):
    """Text and fixed objects of slide i (0-based) drawn in slide coordinates."""
    if i == 0:
        headline(c, 'EVERY CHILD NEEDS A', 'SAFE PLACE TO LAND.')
        subline(c, 'Foster carers make the landing soft.')
    elif i == 1:
        headline(c, 'SOME JOURNEYS HAVE', 'A FEW LOOPS.')
        subline(c, 'New homes. New schools. New faces.')
    elif i == 2:
        headline(c, 'ALONG THE WAY,', 'SMALL THINGS MATTER.')
        subline(c, 'A bedtime story. A drawing. A seat at the table.')
    elif i == 3:
        headline(c, 'YOU COULD BE THE', 'SOFT LANDING.')
        subline(c, 'Foster with Organic Fostering in Greater Manchester.')
    elif i == 4:
        paste(c, logo_spr(520), SW / 2, 200)
        paste(c, text('THINKING ABOUT FOSTERING IN', 400, 50, tuple(CHAR), 0.04), SW / 2, 470)
        paste(c, text('GREATER MANCHESTER?', 900, 66, tuple(PLUM), 0.03), SW / 2, 550)
        subline(c, 'organicfostering.co.uk', 1240)


def house(c, glow=1.0):
    hs = obj(HOUSE, 430)
    if glow > 0:                                                         # a warm light in the windows once it lands
        g = np.zeros((hs.shape[0] + 200, hs.shape[1] + 200), np.float32)
        cv2.ellipse(g, (g.shape[1] // 2, g.shape[0] // 2 + 40), (180, 120), 0, 0, 360, 1.0, -1)
        g = cv2.GaussianBlur(g, (0, 0), 50) * 0.35 * glow
        paste(c, np.dstack([g[..., None] * np.array((1.0, 0.78, 0.45), np.float32), g]), 820, 980)
    paste(c, shadowed(hs, 18, (14, 30), 0.25), 820, 960)


def props(c, i, s_now, t=0.0):
    for k, (path, x, size, rot) in enumerate(PROPS):
        p, s = prop_at(x)
        if not (i * SW - 300 < p[0] < (i + 1) * SW + 300):
            continue
        u = (s_now - s + 120) / 220                                       # pops when the plane reaches it
        if u <= 0:
            continue
        sc = e_back(clamp(u), 1.8)
        bob = 6 * math.sin(t * 2 + k)
        sp = xform(shadowed(obj(path, size), 12, (8, 20), 0.22), max(0.01, sc), rot)
        paste(c, sp, p[0] - i * SW, p[1] - size * 0.42 + bob, clamp(u * 3))


def compose(i, s_path, plane_s=None, t=0.0, landed=None, btn_glow=0.0):
    """Slide i with the path drawn up to s_path and the plane at plane_s (arc length) if given."""
    c = np.empty((SH, SW, 3), np.float32)
    c[:] = IVORY
    yy, xx = np.mgrid[0:SH, 0:SW].astype(np.float32)
    c = c * (1.0 - 0.035 * (np.hypot((xx - SW / 2) / SW, (yy - SH / 2) / SH) ** 2))[..., None]
    draw_path(c, s_path, i * SW)
    if i == 3:                                                           # the path runs in behind the house
        house(c, 1.0 if landed is None else landed)
    props(c, i, s_path, t)
    slide_static(i, c)
    if i == 4:
        button(c, btn_glow)
    if plane_s is not None:
        p, hd = at(plane_s)
        if -400 < p[0] - i * SW < SW + 400:
            paste(c, plane_spr(hd, 380 if i == 0 else 300), p[0] - i * SW, p[1] - 80)
    return c


def write(path, c):
    cv2.imwrite(path, (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])


def statics():
    for i in range(N):
        plane = 60 if i == 0 else (arc_at_x(LAND_X) if i == 3 else None)   # taking off on slide 1, landing on slide 4
        c = compose(i, TOTAL, plane)
        write(f'{OUT}/slide_{i + 1}.jpg', c)
    strip = np.hstack([cv2.resize(cv2.imread(f'{OUT}/slide_{i + 1}.jpg'), (432, 540)) for i in range(N)])
    cv2.imwrite(f'{OUT}/carousel_strip.jpg', strip, [cv2.IMWRITE_JPEG_QUALITY, 92])


FPS = 30
DUR = 5.0


def animate():
    """slide_i.mp4: the plane flies its part of the path, the trail drawing behind it."""
    bounds = [arc_at_x(i * SW) for i in range(N)] + [TOTAL]
    bounds[0] = 0.0
    for i in range(N):
        d = f'{WS}/anim/s{i}'
        os.makedirs(d, exist_ok=True)
        a, b = bounds[i], bounds[i + 1]
        for f in range(int(DUR * FPS)):
            t = f / FPS
            u = e_inout(clamp((t - 0.4) / 3.6))
            s = a + (b - a) * u
            if i == 0:
                s = max(40, s)
            land = clamp((t - 3.4) / 0.8) if i == 3 else None
            ps = s if not (i == 4 and u >= 1) else None
            if i == 3:
                s_land = arc_at_x(LAND_X)
                ps = min(s, s_land) if s < s_land + 1 else s_land
                s = min(s, b)
            glow = clamp((t - 4.0) / 0.3) * (1 - clamp((t - 4.6) / 0.3)) if i == 4 else 0.0
            c = compose(i, s, ps, t, land, glow)
            cv2.imwrite(f'{d}/{f:04d}.png', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{d}/%04d.png', '-c:v', 'libx264', '-preset', 'slow',
                        '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{OUT}/slide_{i + 1}.mp4'], check=True)
        print('slide', i + 1, flush=True)


if __name__ == '__main__':
    statics()
    print('statics written', flush=True)
    if 'stills' not in sys.argv:
        animate()
