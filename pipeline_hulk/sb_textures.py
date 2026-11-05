"""Artwork for "Same Business?": the six Copperline touchpoints, BEFORE (clashing colours/fonts) and AFTER (one system:
navy + amber, Inter Tight, one mark). Copperline Plumbing is fictional (per the concept PDF).

Usage: python3 sb_textures.py -> workspace_hulk/sb_tex/*.png
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FD = f'{ROOT}/workspace_sol/fonts'
OUT = f'{ROOT}/workspace_hulk/sb_tex'
NAVY, AMBER, OFF, SLATE = (30, 42, 74), (245, 165, 36), (243, 245, 240), (96, 108, 128)


def F(name, size):
    return ImageFont.truetype(f'{FD}/{name}.ttf', size)


INTER, INTER8, HANK, HANK5 = 'Headline-900', 'Headline-800', 'Hanken-700', 'Hanken-500'


def centered(d, xy, text, font, fill, anchor='mm', spacing=0):
    d.text(xy, text, font=font, fill=fill, anchor=anchor)


def mark(size, fg=AMBER, drop=OFF, bg=None):
    """Copperline mark: a copper pipe bent into a C, with a drop at the open end."""
    S = size * 4
    im = Image.new('RGBA', (S, S), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = int(S * 0.15)
    pad = int(S * 0.12)
    d.arc([pad, pad, S - pad, S - pad], start=40, end=320, fill=fg, width=w)
    for a in (40, 320):
        r = (S - 2 * pad) / 2
        cx, cy = S / 2 + math.cos(math.radians(a)) * (r - w / 2), S / 2 + math.sin(math.radians(a)) * (r - w / 2)
        d.ellipse([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], fill=fg)
    # drop
    cx, cy, r = S * 0.68, S * 0.52, S * 0.12
    d.ellipse([cx - r, cy - r * 0.2, cx + r, cy + r * 1.8], fill=drop)
    d.polygon([(cx - r * 0.92, cy + r * 0.5), (cx, cy - r * 1.6), (cx + r * 0.92, cy + r * 0.5)], fill=drop)
    return im.resize((size, size), Image.LANCZOS)


def logo_lockup(w, h, bg=NAVY, fg=OFF, sub=True):
    im = Image.new('RGBA', (w, h), bg)
    d = ImageDraw.Draw(im)
    m = mark(int(h * 0.78))
    im.alpha_composite(m, (int(h * 0.12), int(h * 0.11)))
    x = int(h * 1.0)
    d.text((x, h * (0.42 if sub else 0.5)), 'COPPERLINE', font=F(INTER, int(h * 0.42)), fill=fg, anchor='lm')
    if sub:
        d.text((x + 4, h * 0.78), 'PLUMBING & HEATING', font=F(HANK, int(h * 0.14)), fill=AMBER, anchor='lm')
    return im


def stencil(d, xy, text, font, fill, bg, gaps=0.07):
    """Bold type with stencil bridges (horizontal cut through every letter)."""
    d.text(xy, text, font=font, fill=fill, anchor='mm')
    bb = d.textbbox(xy, text, font=font, anchor='mm')
    hgt = bb[3] - bb[1]
    y = (bb[1] + bb[3]) / 2
    d.rectangle([bb[0], y - hgt * gaps / 4, bb[2], y + hgt * gaps / 4], fill=bg)


# ------------------------------------------------------------------ BEFORE
def van_before():
    im = Image.new('RGBA', (1600, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((800, 260), 'Copperline', font=F('Caveat-700', 300), fill=(255, 245, 230), anchor='mm')
    d.text((800, 470), 'plumbing - heating - bathrooms!!', font=F('Poppins-Bold', 64), fill=(255, 220, 90), anchor='mm')
    return im


def sign_before():
    im = Image.new('RGBA', (1400, 500), (46, 139, 62, 255))
    d = ImageDraw.Draw(im)
    stencil(d, (700, 230), 'COPPERLINE', F('Anton-400', 250), (240, 240, 210), (46, 139, 62))
    d.text((700, 430), 'PLUMBERS', font=F('Anton-400', 70), fill=(255, 230, 0), anchor='mm')
    return im


def card_before():
    im = Image.new('RGBA', (1050, 600), (107, 63, 160, 255))
    d = ImageDraw.Draw(im)
    d.text((80, 200), 'CopperLine', font=F('Cardo-700', 140), fill=(255, 255, 255), anchor='lm')
    d.text((84, 320), 'Plumbing Services Ltd', font=F('CardoItalic-400', 56), fill=(230, 210, 255), anchor='lm')
    d.text((84, 470), 'Call: 0161 000 0000', font=F('Cardo-400', 48), fill=(255, 255, 255), anchor='lm')
    return im


def web_before():
    im = Image.new('RGBA', (1280, 800), (236, 236, 236, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1280, 190], fill=(255, 212, 59))
    d.text((60, 95), 'copper line', font=F('Poppins-Bold', 92), fill=(220, 40, 40), anchor='lm')
    d.text((700, 110), 'plumbing & heating', font=F('Caveat-700', 64), fill=(30, 90, 200), anchor='lm')
    d.rectangle([60, 260, 760, 300], fill=(190, 190, 190))
    d.rectangle([60, 330, 640, 370], fill=(205, 205, 205))
    d.rectangle([60, 430, 360, 510], fill=(0, 160, 220))
    d.text((210, 470), 'CLICK HERE', font=F('Anton-400', 44), fill=(255, 255, 255), anchor='mm')
    for i in range(3):
        d.rectangle([60 + i * 400, 580, 400 + i * 400, 760], fill=(215, 215, 215))
    return im


def insta_before():
    im = Image.new('RGBA', (720, 1440), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.ellipse([40, 60, 200, 220], fill=(255, 120, 160))
    d.text((240, 110), 'copperline_plumbs', font=F('Poppins-Bold', 40), fill=(20, 20, 20), anchor='lm')
    d.text((240, 170), 'Plumber!! Manchester', font=F('Nunito-700', 34), fill=(90, 90, 90), anchor='lm')
    cols = [(255, 214, 224), (200, 236, 255), (255, 244, 190), (214, 255, 214), (240, 220, 255), (255, 225, 200),
            (255, 255, 255), (222, 222, 222), (180, 230, 230)]
    fonts = ['Caveat-700', 'Anton-400', 'Cardo-700', 'Poppins-Bold', 'Nunito-900', 'Caveat-700', 'Anton-400', 'Cardo-700', 'Poppins-Bold']
    for i in range(9):
        x, y = 8 + (i % 3) * 238, 300 + (i // 3) * 238
        d.rectangle([x, y, x + 230, y + 230], fill=cols[i])
        d.text((x + 115, y + 115), ['Leak?', 'SALE', 'Boilers', 'tips!', 'NEW', 'Hello', 'CALL', 'Taps', 'Fixed'][i],
               font=F(fonts[i], 56), fill=[(220, 40, 90), (20, 120, 40), (60, 40, 160), (240, 120, 0), (0, 0, 0), (0, 120, 200),
                                          (200, 0, 0), (60, 60, 60), (0, 140, 140)][i], anchor='mm')
    return im


def invoice_before():
    im = Image.new('RGBA', (900, 1200), (226, 226, 226, 255))
    d = ImageDraw.Draw(im)
    d.text((70, 120), 'INVOICE', font=F('Cardo-400', 96), fill=(40, 40, 40), anchor='lm')
    d.text((70, 220), 'copperline plumbing', font=F('Cardo-400', 44), fill=(80, 80, 80), anchor='lm')
    for i in range(7):
        d.line([70, 360 + i * 90, 830, 360 + i * 90], fill=(150, 150, 150), width=3)
        d.rectangle([70, 380 + i * 90, 70 + 200 + (i * 53) % 300, 400 + i * 90], fill=(185, 185, 185))
    d.text((830, 1060), 'Total: £___', font=F('Cardo-400', 52), fill=(40, 40, 40), anchor='rm')
    return im


# ------------------------------------------------------------------ AFTER (one system)
def van_after():
    im = Image.new('RGBA', (1600, 600), (0, 0, 0, 0))
    lk = logo_lockup(1300, 330, bg=(0, 0, 0, 0))
    im.alpha_composite(lk, (150, 90))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 500, 1600, 560], fill=AMBER)
    return im


def sign_after():
    im = Image.new('RGBA', (1400, 500), NAVY + (255,))
    lk = logo_lockup(1200, 300, bg=NAVY + (255,))
    im.alpha_composite(lk, (110, 100))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 460, 1400, 500], fill=AMBER)
    return im


def card_after():
    im = Image.new('RGBA', (1050, 600), NAVY + (255,))
    im.alpha_composite(mark(300), (80, 150))
    d = ImageDraw.Draw(im)
    d.text((430, 250), 'COPPERLINE', font=F(INTER, 96), fill=OFF, anchor='lm')
    d.text((434, 330), 'PLUMBING & HEATING', font=F(HANK, 34), fill=AMBER, anchor='lm')
    d.text((434, 450), '0161 000 0000  ·  copperline.example', font=F(HANK5, 30), fill=(200, 208, 222), anchor='lm')
    d.rectangle([0, 570, 1050, 600], fill=AMBER)
    return im


def web_after():
    im = Image.new('RGBA', (1280, 800), OFF + (255,))
    im.alpha_composite(logo_lockup(1280, 190, sub=False), (0, 0))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(('Services', 'Areas', 'Contact')):
        d.text((860 + i * 140, 95), t, font=F(HANK, 30), fill=OFF, anchor='mm')
    d.text((60, 300), 'Plumbing & heating,', font=F(INTER, 70), fill=NAVY, anchor='lm')
    d.text((60, 380), 'done properly.', font=F(INTER, 70), fill=NAVY, anchor='lm')
    d.rounded_rectangle([60, 450, 400, 530], 40, fill=AMBER)
    d.text((230, 490), 'Book a plumber', font=F(INTER8, 34), fill=NAVY, anchor='mm')
    for i in range(3):
        d.rounded_rectangle([60 + i * 400, 590, 400 + i * 400, 760], 20, fill=(226, 230, 238))
        im.alpha_composite(mark(90, fg=NAVY, drop=AMBER), (85 + i * 400, 630))
    return im


def insta_after():
    im = Image.new('RGBA', (720, 1440), OFF + (255,))
    d = ImageDraw.Draw(im)
    d.ellipse([40, 60, 200, 220], fill=NAVY)
    im.alpha_composite(mark(120), (60, 80))
    d.text((240, 110), 'copperline', font=F(INTER, 44), fill=NAVY, anchor='lm')
    d.text((240, 170), 'Plumbing & heating · Manchester', font=F(HANK, 30), fill=SLATE, anchor='lm')
    labels = ['Leak?', 'Boilers', 'Tips', 'Taps', '', 'Fixed', 'Heating', 'Call', 'Hello']
    for i in range(9):
        x, y = 8 + (i % 3) * 238, 300 + (i // 3) * 238
        col = [NAVY, AMBER, OFF][(i + i // 3) % 3]
        ink = OFF if col == NAVY else NAVY
        d.rectangle([x, y, x + 230, y + 230], fill=col if col != OFF else (226, 230, 238))
        if i == 4:
            im.alpha_composite(mark(170, fg=AMBER, drop=NAVY), (x + 30, y + 30))
        else:
            d.text((x + 115, y + 115), labels[i], font=F(INTER, 48), fill=ink, anchor='mm')
    return im


def invoice_after():
    im = Image.new('RGBA', (900, 1200), OFF + (255,))
    im.alpha_composite(logo_lockup(900, 220), (0, 0))
    d = ImageDraw.Draw(im)
    d.text((70, 320), 'INVOICE', font=F(INTER, 64), fill=NAVY, anchor='lm')
    for i in range(6):
        d.line([70, 420 + i * 90, 830, 420 + i * 90], fill=(210, 214, 222), width=3)
        d.rectangle([70, 445 + i * 90, 70 + 200 + (i * 53) % 300, 465 + i * 90], fill=(190, 198, 212))
    d.rectangle([70, 1010, 830, 1100], fill=AMBER)
    d.text((110, 1055), 'Total', font=F(INTER, 44), fill=NAVY, anchor='lm')
    return im


def palette_page():
    im = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
    return im


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for fn in (van_before, sign_before, card_before, web_before, insta_before, invoice_before,
               van_after, sign_after, card_after, web_after, insta_after, invoice_after):
        fn().save(f'{OUT}/{fn.__name__}.png')
        print(fn.__name__)
    mark(1024).save(f'{OUT}/mark.png')
    logo_lockup(1400, 360).save(f'{OUT}/lockup.png')
