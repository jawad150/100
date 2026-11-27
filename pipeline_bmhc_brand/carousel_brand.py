"""BMHC "Brand identity" carousel - 6 slides, 1080x1350, after the user's Pinterest reference (an editorial brand
identity case study: grainy coloured grounds, corner registration marks, black label tags, a big split headline,
mockup collage, palette with colour values, logos, type specimen + photography grid, call to action).
Content: BMHC Digital & Social Brand Guidelines v1.0. -> reel/bmhc/brand_identity_carousel/slide_1..6.jpg + strip"""
import os, math, functools
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FON = f'{ROOT}/workspace_sol/fonts'
WS = f'{ROOT}/workspace_brandcar'
IMG = f'{ROOT}/workspace_bmhc/web/img'
OUT = f'{ROOT}/reel/bmhc/brand_identity_carousel'
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350


def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


MAG, TEAL, ORANGE, LIME = hx('#E60585'), hx('#2DC892'), hx('#FF4200'), hx('#69FF00')
INK, CHAR, SLATE, STONE, MIST, WHITE = hx('#0B0B0B'), hx('#1F1F1F'), hx('#5C5C5C'), hx('#E9E6DF'), hx('#F6F5F1'), hx('#FFFFFF')
rng = np.random.default_rng(11)


def F(w, s):
    return ImageFont.truetype(f'{FON}/Inter-{w}.ttf', int(s))


@functools.lru_cache(maxsize=512)
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
    a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 1):xs.max() + 2]
    return np.dstack([a[..., None] * np.array(col, np.float32), a])


def paste(c, spr, x, y, a=1.0, anchor='tl'):
    sh, sw = spr.shape[:2]
    if anchor == 'c':
        x, y = x - sw / 2, y - sh / 2
    elif anchor == 'l':
        y = y - sh / 2
    elif anchor == 'r':
        x, y = x - sw, y - sh / 2
    x0, y0 = int(round(x)), int(round(y))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(c.shape[1], x0 + sw), min(c.shape[0], y0 + sh)
    if X1 <= X0 or Y1 <= Y0:
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


def rot(spr, deg):
    h, w = spr.shape[:2]
    D = int(math.hypot(w, h)) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    M[0, 2] += D / 2 - w / 2
    M[1, 2] += D / 2 - h / 2
    return cv2.warpAffine(spr, M, (D, D), flags=cv2.INTER_LINEAR)


def rmask(w, h, r):
    w, h, r = int(w), int(h), int(r)
    m = np.zeros((h * 2, w * 2), np.uint8)
    cv2.rectangle(m, (r * 2, 0), ((w - r) * 2, h * 2), 255, -1)
    cv2.rectangle(m, (0, r * 2), (w * 2, (h - r) * 2), 255, -1)
    for x in (r, w - r):
        for y in (r, h - r):
            cv2.circle(m, (x * 2, y * 2), max(1, r * 2), 255, -1, cv2.LINE_AA)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def shadowed(spr, blur=18, dy=16, amt=0.3):
    h, w = spr.shape[:2]
    p = blur * 3 + dy
    out = np.zeros((h + 2 * p, w + 2 * p, 4), np.float32)
    sh = np.zeros(out.shape[:2], np.float32)
    sh[p + dy:p + dy + h, p:p + w] = spr[..., 3]
    out[..., 3] = cv2.GaussianBlur(sh, (0, 0), blur) * amt
    reg = out[p:p + h, p:p + w]
    a = spr[..., 3:4]
    reg[..., :3] = spr[..., :3] + reg[..., :3] * (1 - a)
    reg[..., 3:4] = a + reg[..., 3:4] * (1 - a)
    return out


def card_from(path, w, radius=10, border=0, crop=None):
    im = cv2.imread(path)[..., ::-1].astype(np.float32) / 255
    if crop:
        im = im[crop[1]:crop[3], crop[0]:crop[2]]
    h = int(im.shape[0] * w / im.shape[1])
    im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    if border:
        im = cv2.copyMakeBorder(im, border, border, border, border, cv2.BORDER_CONSTANT, value=(1, 1, 1))
    m = rmask(im.shape[1], im.shape[0], radius)
    return np.dstack([im * m[..., None], m])


def photo(name, w, h, fx=0.5, fy=0.5, z=1.0):
    im = cv2.imread(f'{IMG}/{name}')[..., ::-1].astype(np.float32) / 255
    ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih) * z
    rs = cv2.resize(im, (int(iw * sc) + 2, int(ih * sc) + 2), interpolation=cv2.INTER_AREA)
    x0, y0 = int((rs.shape[1] - w) * fx), int((rs.shape[0] - h) * fy)
    return rs[y0:y0 + h, x0:x0 + w]


def grain(c, amt=0.03):
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 0.6)
    return np.clip(c + n[..., None] * amt, 0, 1)


def ground(col):
    c = np.ones((H, W, 3), np.float32) * col
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    c = c * (1.03 - 0.08 * (np.hypot((xx - W / 2) / W, (yy - H / 2) / H) ** 2))[..., None]
    return c


def marks(c, col):
    """The reference's registration marks: a ring and a crosshair ring in each corner."""
    lay = np.zeros((H * 2, W * 2), np.uint8)
    for (x, y) in ((40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)):
        for k, dx in enumerate((0, 34 if x < W / 2 else -34)):
            cx, cy = (x + dx) * 2, y * 2
            cv2.circle(lay, (cx, cy), 16, 255, 3, cv2.LINE_AA)
            if k == 1:
                cv2.line(lay, (cx - 22, cy), (cx + 22, cy), 255, 3, cv2.LINE_AA)
                cv2.line(lay, (cx, cy - 22), (cx, cy + 22), 255, 3, cv2.LINE_AA)
            else:
                cv2.circle(lay, (cx, cy), 7, 255, -1, cv2.LINE_AA)
    m = cv2.resize(lay, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255 * 0.85
    c[:] = c * (1 - m) + np.array(col, np.float32) * m


def header(c, s, col):
    paste(c, text(s, 500, 26, tuple(col)), W / 2, 42, 1, 'c')


def tag(c, s, x, y, inv=False):
    t = text(s, 500, 22, tuple(WHITE if not inv else INK), 0.1)
    w, h = t.shape[1] + 28, t.shape[0] + 18
    box = np.dstack([np.ones((h, w, 3), np.float32) * (INK if not inv else WHITE), np.ones((h, w), np.float32)])
    paste(box, t, 14, 9)
    paste(c, box, x, y)
    return w, h


@functools.lru_cache(None)
def logo_white(width):
    """The supplied logo, background keyed out, line art reversed to white (approved 'reversed on ink'); bars keep colour."""
    lg = cv2.imread(f'{ROOT}/workspace_bmhc_posts/bmhc_logo_colour.png', cv2.IMREAD_UNCHANGED)[..., 2::-1].astype(np.float32) / 255
    big = cv2.resize(lg, (lg.shape[1] * 3, lg.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
    lum = (big * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1)
    sat = big.max(-1) - big.min(-1)
    bar = np.clip((sat - 0.18) / 0.12, 0, 1)
    la = np.clip((0.9 - lum) / 0.7, 0, 1)
    alpha = np.maximum(bar, la)
    rgb = WHITE[None, None] * (1 - bar[..., None]) + big * bar[..., None]
    ys, xs = np.where(alpha > 0.1)
    rgb, alpha = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1], alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hh = int(alpha.shape[0] * width / alpha.shape[1])
    rgb = cv2.resize(rgb, (width, hh), interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(alpha, (width, hh), interpolation=cv2.INTER_AREA)
    return np.dstack([rgb * alpha[..., None], alpha]).astype(np.float32)


@functools.lru_cache(None)
def logo_colour(width):
    lg = cv2.imread(f'{ROOT}/workspace_bmhc_posts/bmhc_logo_transparent.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    hh = int(lg.shape[0] * width / lg.shape[1])
    lg = cv2.resize(lg, (width, hh), interpolation=cv2.INTER_AREA)
    return np.dstack([lg[..., 2::-1] * lg[..., 3:4], lg[..., 3]]).astype(np.float32)


def building_mark(width, white=False):
    """The tower line art on its own (top part of the logo, above the wordmark)."""
    lg = logo_white(900) if white else logo_colour(900)
    a = lg[..., 3]
    rows = np.where(a.max(1) > 0.3)[0]
    # the wordmark starts at the first long fully-inked text band below the building: cut at 68% of the height
    cut = int(lg.shape[0] * 0.66)
    bm = lg[:cut]
    ys, xs = np.where(bm[..., 3] > 0.1)
    bm = bm[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hh = int(bm.shape[0] * width / bm.shape[1])
    return cv2.resize(bm, (width, hh), interpolation=cv2.INTER_AREA)


def four_bars(c, x, y, w, h=14):
    for i, col in enumerate((MAG, TEAL, ORANGE, LIME)):
        c[int(y):int(y + h), int(x + w * i / 4):int(x + w * (i + 1) / 4) - 4] = col


WR = lambda n: f'{WS}/wr_{n}.png'
BENTO = f'{ROOT}/reel/bmhc/static_everything_under_one_roof/post_1080x1350.jpg'
AYAH = f'{WS}/ayah.png'


# ------------------------------------------------------------------ slides
def slide1():
    c = photo('1-BMHC-web.jpg', W, H, 0.5, 0.35, 1.25)
    g = (c * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    c = c * 0.45 + g * np.array((0.62, 0.78, 0.86), np.float32) * 0.62                 # cool, soft, editorial
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    c = c * (1 - 0.7 * np.clip((yy - 950) / 400, 0, 1)) * (1 - 0.25 * np.clip(1 - yy / 560, 0, 1))
    marks(c, WHITE)
    header(c, 'Visual identity', WHITE)
    paste(c, text('Brand', 400, 150, tuple(WHITE), -0.03), 54, 120)
    paste(c, text('Identity', 800, 150, tuple(WHITE), -0.03), W - 54, 370, 1, 'r')
    for i, s in enumerate(('DIGITAL & SOCIAL', 'EDITION · V1.0')):
        paste(c, text(s, 500, 22, tuple(WHITE), 0.1), 58, 470 + i * 30)
    for i, s in enumerate(('BRITISH MUSLIM', 'HERITAGE CENTRE', 'WHALLEY RANGE')):
        paste(c, text(s, 500, 22, tuple(WHITE), 0.1), W - 58, 480 + i * 30, 1, 'r')
    cards = [card_from(BENTO, 300, 10, 8), card_from(WR(174), 236, 10, 8), card_from(AYAH, 300, 10, 8, crop=(4, 4, 565, 700))]
    xs = [200, 540, 880]
    for x, cd, r in zip(xs, cards, (-4, 0, 4)):
        paste(c, rot(shadowed(cd, 20, 18, 0.35), r), x, 840, 1, 'c')
    paste(c, logo_white(330), W / 2, 1200, 1, 'c')
    paste(c, text('bmhc.org.uk', 500, 24, tuple(WHITE)), W - 70, 1290, 1, 'r')
    return grain(c)


def slide2():
    c = ground(STONE)
    marks(c, INK)
    header(c, 'Visual identity', INK)
    tag(c, 'ART DIRECTION', 60, 100)
    paste(c, text('Ink, white, one pillar colour, four bars.', 500, 28, tuple(SLATE)), 60, 165)
    pieces = [(BENTO, 470, None, 330, 560, -3), (WR(315), 240, None, 830, 450, 4), (WR(435), 240, None, 850, 905, -3),
              (AYAH, 330, (4, 4, 565, 700), 290, 1060, 3), (None, 230, None, 590, 1135, -2)]
    for path, w, crop, x, y, r in pieces:
        if path is None:                                                   # the tower photo as a print
            ph = photo('Dut-kbsW4AIRs6T.jpg', w, int(w * 1.15), 0.5, 0.0, 1.5)
            m = np.ones(ph.shape[:2], np.float32)
            cd = np.dstack([cv2.copyMakeBorder(ph, 12, 50, 12, 12, cv2.BORDER_CONSTANT, value=(1, 1, 1)), cv2.copyMakeBorder(m, 12, 50, 12, 12, cv2.BORDER_CONSTANT, value=1)])
        else:
            cd = card_from(path, w, 12, 0, crop)
        paste(c, rot(shadowed(cd, 22, 20, 0.32), r), x, y, 1, 'c')
    return grain(c, 0.025)


def swatch(col, name, theme, hexs, rgb, cmyk, w, h, txt):
    sw = np.dstack([np.ones((h, w, 3), np.float32) * col, np.ones((h, w), np.float32)])
    paste(sw, text(name, 700, 30, tuple(txt)), 24, 22)
    paste(sw, text(theme, 500, 22, tuple(txt), 0.06), 24, 64)
    for i, s in enumerate((f'HEX {hexs}', f'RGB {rgb}', f'CMYK {cmyk}')):
        paste(sw, text(s, 500, 19, tuple(txt), 0.06), 24, h - 98 + i * 28)
    return sw


def slide3():
    c = photo('bhmc-f.png', W, H, 0.5, 0.4, 1.3)
    g = (c * np.array((0.3, 0.59, 0.11), np.float32)).sum(-1, keepdims=True)
    c = (c * 0.35 + g * 0.65) * 0.55
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
        paste(c, swatch(*it, sw_w, sw_h, it[-1]) if False else swatch(it[0], it[1], it[2], it[3], it[4], it[5], sw_w, sw_h, it[6]), x, y)
    tag(c, 'NEUTRALS', 60, 820, inv=True)
    neu = [(INK, 'Ink', 'TEXT · STORIES', '#0B0B0B', '11 11 11', '0 0 0 96', WHITE),
           (STONE, 'Stone', 'LINES', '#E9E6DF', '233 230 223', '0 1 5 9', INK),
           (MIST, 'Mist', 'PANELS', '#F6F5F1', '246 245 241', '0 0 2 4', INK)]
    nw = int((960 - 40) / 3)
    for i, it in enumerate(neu):
        paste(c, swatch(it[0], it[1], it[2], it[3], it[4], it[5], nw, 300, it[6]), 60 + i * (nw + 20), 880)
    paste(c, text('Values as published in the BMHC Digital & Social Brand Guidelines v1.0', 500, 20, tuple(WHITE * 0.8)), 60, 1205)
    paste(c, text('BMHC', 800, 30, tuple(WHITE), 0.12), W / 2, 1290, 1, 'c')
    return grain(c, 0.025)


def slide4():
    c = np.ones((H, W, 3), np.float32) * WHITE
    c[:H // 2] = INK
    marks(c, MIST)
    header(c, 'Visual identity', WHITE)
    tw, th = tag(c, 'PRIMARY LOGO', W / 2 - 110, 110, inv=True)
    paste(c, logo_white(720), W / 2, 400, 1, 'c')
    tag(c, 'BUILDING MARK', W / 2 - 115, H // 2 + 60)
    paste(c, building_mark(560), W / 2, H // 2 + 330, 1, 'c')
    four_bars(c, W / 2 - 280, H // 2 + 470, 560, 14)
    paste(c, text('Reversed on ink · colour on white · never redrawn', 500, 22, tuple(SLATE)), W / 2, H - 70, 1, 'c')
    return grain(c, 0.02)


def spec_row(c, label, y, x0=60, x1=300):
    paste(c, text(label, 500, 20, tuple(SLATE), 0.1), x0, y, 1, 'l')
    c[int(y), x0 + 170:x1 + 40] = SLATE * 0.6 + MIST * 0.4


def slide5():
    tint = WHITE * 0.86 + MAG * 0.14
    c = ground(tint)
    marks(c, INK)
    header(c, 'Visual identity', INK)
    tag(c, 'TYPOGRAPHY', 60, 100)
    spec_row(c, 'SUBHEADLINE', 230)
    paste(c, text('Inter Bold, sentence case', 700, 30, tuple(INK)), 360, 230, 1, 'l')
    spec_row(c, 'HEADLINE', 330)
    paste(c, text('ONE VERSE.', 800, 74, tuple(INK), 0.02), 360, 300, 1, 'l')
    paste(c, text('ONE ACTION.', 800, 74, tuple(MAG), 0.02), 360, 380, 1, 'l')
    spec_row(c, 'BODY', 480)
    for i, s in enumerate(('Body copy reads like this. Inter Regular,', 'line height 1.4, never below 28 px.')):
        paste(c, text(s, 400, 28, tuple(INK)), 360, 470 + i * 40, 1, 'l')
    tag(c, 'PHOTOGRAPHY', 60, 600)
    grid = [('1-BMHC-web.jpg', 0.5, 0.45, 1.6), ('bhmc-f.png', 0.5, 0.35, 1.0), ('Dut-kbsW4AIRs6T.jpg', 0.5, 0.05, 1.3),
            ('bhmc-f.png', 0.15, 0.6, 2.2), ('1-BMHC-web.jpg', 0.85, 0.7, 2.4), ('Dut-kbsW4AIRs6T.jpg', 0.5, 0.3, 2.2)]
    cw, ch = 300, 262
    for i, (n, fx, fy, z) in enumerate(grid):
        ph = photo(n, cw, ch, fx, fy, z)
        m = rmask(cw, ch, 18)
        x = 60 + (i % 3) * (cw + 30)
        y = 680 + (i // 3) * (ch + 26)
        paste(c, shadowed(np.dstack([ph * m[..., None], m]), 14, 10, 0.22), x - 56, y - 42)
    paste(c, text('The building, objects and places. No identifiable under-18s.', 500, 22, tuple(SLATE)), 60, 1282, 1, 'l')
    return grain(c, 0.025)


def slide6():
    c = ground(MIST)
    marks(c, INK)
    header(c, 'Visual identity', INK)
    cards = [card_from(BENTO, 250, 10, 6), card_from(WR(315), 196, 10, 6), card_from(WR(435), 196, 10, 6), card_from(WR(1080), 196, 10, 6)]
    xs = [180, 430, 650, 880]
    for x, cd, r in zip(xs, cards, (-5, -1, 2, 5)):
        paste(c, rot(shadowed(cd, 18, 16, 0.3), r), x, 330, 1, 'c')
    paste(c, text('Now you can read our feed by colour.', 500, 38, tuple(INK)), W / 2, 640, 1, 'c')
    paste(c, text('Five themes.', 900, 120, tuple(INK), -0.03), W / 2, 760, 1, 'c')
    paste(c, text('One centre.', 900, 120, tuple(MAG), -0.03), W / 2, 890, 1, 'c')
    chips = [('HEART', MAG, WHITE), ("QUR'AN", TEAL, INK), ('PRODUCTIVITY', ORANGE, INK), ('SUNNAH', LIME, INK), ('STORIES', INK, WHITE)]
    widths = [F(700, 22).getlength(s) + 44 for s, _, _ in chips]
    x = W / 2 - (sum(widths) + 12 * 4) / 2
    for (s, bg, fg), w in zip(chips, widths):
        m = rmask(w, 50, 25)
        chip = np.dstack([m[..., None] * bg, m])
        paste(chip, text(s, 700, 22, tuple(fg), 0.08), w / 2, 25, 1, 'c')
        paste(c, chip, x, 1000)
        x += w + 12
    t = text('SAVE THIS POST', 500, 28, tuple(WHITE), 0.12)
    bw_, bh_ = t.shape[1] + 60, t.shape[0] + 34
    box = np.dstack([np.ones((bh_, bw_, 3), np.float32) * INK, np.ones((bh_, bw_), np.float32)])
    paste(box, t, 30, 17)
    paste(c, box, W / 2, 1125, 1, 'c')
    paste(c, text('Follow @thebmhc for weekly reminders', 500, 28, tuple(SLATE)), W / 2, 1205, 1, 'c')
    paste(c, logo_colour(250), W / 2, 1290, 1, 'c')
    return grain(c, 0.025)


SLIDES = [slide1, slide2, slide3, slide4, slide5, slide6]
if __name__ == '__main__':
    for i, fn in enumerate(SLIDES):
        c = fn()
        cv2.imwrite(f'{OUT}/slide_{i + 1}.jpg', (np.clip(c, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
        print('slide', i + 1, flush=True)
    strip = np.hstack([cv2.resize(cv2.imread(f'{OUT}/slide_{i + 1}.jpg'), (432, 540)) for i in range(len(SLIDES))])
    cv2.imwrite(f'{OUT}/carousel_strip.jpg', strip, [cv2.IMWRITE_JPEG_QUALITY, 92])
