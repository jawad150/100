"""Organic Fostering carousel "A little care goes a long way" - five static 1080x1350 slides (JPG + PNG).

Frame-break (after the brief's reference): a top photo and a bottom photo joined by a stylised Instagram strip; a 3D
object (teddy, school bag, puzzle piece, two hands, an open front door) breaks through the strip with real overlap and
shadows. Photos: Organic Fostering's own homepage imagery (realistic British homes). No fictional engagement counts.
Brand: plum, ivory, magenta; Nunito; official logo; no exclamation marks.
"""
import os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_frame'
OFI = f'{S}/of'
OUT = f'{ROOT}/reel/organic_fostering/a_little_care_carousel'
os.makedirs(OUT, exist_ok=True)
FON = f'{ROOT}/workspace_sol/fonts'
W, H = 1080, 1350
PLUM, MAG, ORANGE, GREEN, IVORY, INK = (91, 23, 79), (183, 0, 110), (255, 100, 17), (97, 168, 10), (252, 248, 245), (50, 31, 53)
GREY = (130, 118, 128)


@functools.lru_cache(None)
def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', s)


def crop(path, w, h, fx, fy, zoom=1.0):
    im = Image.open(path).convert('RGB')
    iw, ih = im.size
    s = max(w / iw, h / ih) * zoom
    nw, nh = int(iw * s), int(ih * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int(min(max(fx * nw - w / 2, 0), nw - w))
    y = int(min(max(fy * nh - h / 2, 0), nh - h))
    return im.crop((x, y, x + w, y + h))


def warm(im, a=0.06):
    """A gentle shared grade so the two halves sit together."""
    arr = np.asarray(im).astype(np.float32)
    arr = arr * np.array((1 + a, 1 + a * 0.3, 1 - a * 0.5), np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ the stylised Instagram strip
def heart(d, x, y, s, col, width=5):
    pts = []
    import math
    for i in range(60):
        t = i / 60 * 2 * math.pi
        px = 16 * math.sin(t) ** 3
        py = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + px * s, y + py * s))
    d.line(pts + [pts[0]], fill=col, width=width, joint='curve')


def strip(headline, y0, h=286):
    """White Instagram-style band: icons row, the account + the headline as the caption. No counts."""
    im = Image.new('RGBA', (W, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    # icons
    heart(d, 70, 52, 1.55, MAG, 6)
    d.ellipse([124, 30, 170, 76], outline=INK, width=5)                              # comment bubble
    d.polygon([(132, 70), (124, 84), (142, 74)], fill=INK)
    d.polygon([(196, 32), (244, 52), (196, 74), (204, 52)], outline=INK, width=5)    # share arrow
    d.line([(204, 52), (244, 52)], fill=INK, width=4)
    d.polygon([(W - 82, 30), (W - 50, 30), (W - 50, 78), (W - 66, 64), (W - 82, 78)], fill=INK)   # bookmark
    # avatar + account
    lg = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
    lg = lg.crop(lg.getbbox())
    av = Image.new('RGBA', (56, 56), (255, 255, 255, 255))
    lg2 = lg.crop((0, 0, int(lg.height * 0.98), int(lg.height * 0.8)))                          # the OF mark (left part of the logo)
    lg2.thumbnail((48, 48), Image.LANCZOS)
    av.paste(lg2, ((56 - lg2.width) // 2, (56 - lg2.height) // 2), lg2)
    m = Image.new('L', (56, 56), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 55, 55], fill=255)
    ring = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, 63, 63], outline=MAG + (255,), width=3)
    im.alpha_composite(ring, (36, 104))
    im.paste(av, (40, 108), m)
    d.text((112, 130), 'organicfostering', font=F(900, 30), fill=INK, anchor='lm')
    # headline as the caption
    f = F(900, 46)
    words, lines, cur = headline.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) > 620 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    yy = 194
    for ln in lines:
        d.text((40, yy), ln, font=f, fill=PLUM, anchor='lm')
        yy += 54
    return im, y0


def object_with_shadow(canvas, name, cx, cy, size, rot=0, shadow_off=(18, 30), blur=22, alpha=110):
    spr = Image.open(f'{S}/assets/{name}.png').convert('RGBA')
    spr = spr.crop(spr.getbbox())
    sc = size / max(spr.size)
    spr = spr.resize((int(spr.width * sc), int(spr.height * sc)), Image.LANCZOS)
    if rot:
        spr = spr.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', spr.size, (40, 10, 30, 0))
    sh.putalpha(spr.split()[3].point(lambda v: v * alpha // 255))
    pad = blur * 3
    big = Image.new('RGBA', (spr.width + 2 * pad, spr.height + 2 * pad), (0, 0, 0, 0))
    big.paste(sh, (pad, pad))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    x, y = int(cx - spr.width / 2), int(cy - spr.height / 2)
    canvas.alpha_composite(big, (x - pad + shadow_off[0], y - pad + shadow_off[1]))
    canvas.alpha_composite(spr, (x, y))
    return spr


def colour_bar(c, h=12):
    d = ImageDraw.Draw(c)
    for i, col in enumerate((MAG, ORANGE, GREEN)):
        d.rectangle([int(W * i / 3), H - h, int(W * (i + 1) / 3), H], fill=col)


# ------------------------------------------------------------------ slides
SPLIT = 600          # where the strip starts
STRIP_H = 286


def frame_break(n, headline, img, top, bottom, obj, obj_xy, obj_size, obj_rot=0, extra=None):
    c = Image.new('RGBA', (W, H), IVORY + (255,))
    t = warm(crop(f'{OFI}/{img}.webp', W, SPLIT + 40, *top))
    b = warm(crop(f'{OFI}/{img}.webp', W, H - SPLIT - STRIP_H + 40, *bottom))
    c.paste(t, (0, 0))
    c.paste(b, (0, SPLIT + STRIP_H - 40))
    st, y0 = strip(headline, SPLIT, STRIP_H)
    # soft shadow above and below the strip
    sh = Image.new('RGBA', (W, STRIP_H + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 30, W, STRIP_H + 30], fill=(30, 10, 25, 90))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (0, SPLIT - 30))
    c.alpha_composite(st, (0, SPLIT))
    if extra:
        extra(c)
    object_with_shadow(c, obj, obj_xy[0], obj_xy[1], obj_size, obj_rot)
    # small slide counter top-right, like a carousel
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([W - 120, 32, W - 32, 76], 22, fill=(20, 10, 18, 140))
    d.text((W - 76, 54), f'{n}/5', font=F(800, 24), fill=(255, 255, 255), anchor='mm')
    colour_bar(c)
    return c.convert('RGB')


def slide5():
    c = Image.new('RGBA', (W, H), PLUM + (255,))
    # warm hallway glow behind the door
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([240, 40, 840, 640], fill=(255, 190, 110, 120))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    st, _ = strip('Could you make room for fostering?', SPLIT, STRIP_H)
    sh = Image.new('RGBA', (W, STRIP_H + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 30, W, STRIP_H + 30], fill=(20, 5, 15, 110))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (0, SPLIT - 30))
    c.alpha_composite(st, (0, SPLIT))
    # ivory lower panel with logo, website, CTA
    low = Image.new('RGBA', (W, H - SPLIT - STRIP_H), IVORY + (255,))
    c.alpha_composite(low, (0, SPLIT + STRIP_H))
    lg = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
    lg = lg.crop(lg.getbbox())
    lw = 430
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    c.alpha_composite(lg, (int(W / 2 - lw / 2), SPLIT + STRIP_H + 60))
    d = ImageDraw.Draw(c)
    bw, bh, by = 520, 96, SPLIT + STRIP_H + 60 + lg.height + 36
    d.rounded_rectangle([W / 2 - bw / 2, by, W / 2 + bw / 2, by + bh], bh // 2, fill=MAG)
    d.text((W / 2, by + bh / 2), 'Start your enquiry', font=F(900, 42), fill=(255, 255, 255), anchor='mm')
    d.text((W / 2, by + bh + 50), 'organicfostering.co.uk', font=F(800, 34), fill=PLUM, anchor='mm')
    # the open front door breaks out of the frame: from the plum top, over the strip, onto the ivory panel
    object_with_shadow(c, 'door', 800, 430, 600, 0, (20, 34), 26, 120)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([W - 120, 32, W - 32, 76], 22, fill=(20, 10, 18, 140))
    d.text((W - 76, 54), '5/5', font=F(800, 24), fill=(255, 255, 255), anchor='mm')
    colour_bar(c)
    return c.convert('RGB')


SLIDES = {
    1: lambda: frame_break(1, 'Small gestures. Meaningful beginnings.', '05-emergency-a-calm-welcome',
                           (0.72, 0.30, 1.35), (0.30, 0.55, 1.35), 'teddy', (870, 700), 390, 8),
    2: lambda: frame_break(2, 'Someone to encourage them.', '08-teenagers-time-to-talk',
                           (0.70, 0.33, 1.45), (0.33, 0.50, 1.3), 'backpack', (880, 700), 330, -6),
    3: lambda: frame_break(3, 'Someone to grow with.', '01-hero-cultural-belonging',
                           (0.37, 0.20, 1.9), (0.46, 0.74, 1.7), 'puzzle', (880, 700), 300, 10),
    4: lambda: frame_break(4, 'Someone to count on.', '04-long-term-family-belonging',
                           (0.64, 0.30, 1.35), (0.36, 0.40, 1.35), 'hands', (930, 730), 600, 0),
    5: slide5,
}

if __name__ == '__main__':
    import sys
    ns = [int(a) for a in sys.argv[1:]] or list(SLIDES)
    for n in ns:
        im = SLIDES[n]()
        im.save(f'{OUT}/slide_{n}.jpg', quality=94)
        print('slide', n)
    ims = [Image.open(f'{OUT}/slide_{n}.jpg') for n in SLIDES if os.path.exists(f'{OUT}/slide_{n}.jpg')]
    sw = W // 3
    st = Image.new('RGB', (len(ims) * (sw + 10), H // 3), (40, 30, 40))
    for i, im in enumerate(ims):
        st.paste(im.resize((sw, H // 3)), (i * (sw + 10), 0))
    st.save(f'{OUT}/strip.jpg', quality=90)
