"""Paper textures for Organic Fostering "The letter you never received" (3D static post).

letter.png   ivory writing paper: heading in Nunito, three handwritten reasons in ink, each struck through in magenta
card.png     plum card: "You haven't been rejected. / You haven't even asked yet."
envelope.png envelope front: "To: you" handwritten, a small leaf stamp (no official marks)
damask.png   ivory-on-ivory leaf damask for the tablecloth (from the brand leaf pattern)
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = f'{ROOT}/workspace_letter/tex'
FON = f'{ROOT}/workspace_sol/fonts'
os.makedirs(OUT, exist_ok=True)
PLUM, MAG, ORANGE, GREEN = (91, 23, 79), (183, 0, 110), (255, 100, 17), (97, 168, 10)
IVORY, INK = (252, 248, 240), (40, 36, 60)


def F(name, size):
    return ImageFont.truetype(f'{FON}/{name}.ttf', size)


def paper(w, h, base=IVORY, seed=1):
    rng = np.random.default_rng(seed)
    a = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    n = rng.normal(0, 1, (h // 4, w // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    a = a * (0.97 + 0.04 * n[..., None])
    fib = rng.normal(0, 3.0, (h, w, 1)).astype(np.float32)
    a = np.clip(a + fib, 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def strike(d, x0, x1, y, seed):
    """A hand-drawn marker strike: slightly wavy, slightly rising, two passes."""
    rng = np.random.default_rng(seed)
    for p in range(2):
        pts = []
        for i in range(24):
            u = i / 23
            pts.append((x0 + (x1 - x0) * u, y - 6 * u + rng.normal(0, 1.6) + p * 4))
        d.line(pts, fill=MAG + (235,), width=13 - p * 4, joint='curve')


def letter():
    W, H = 1700, 2200
    im = paper(W, H).convert('RGBA')
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 34], fill=PLUM)
    d.text((140, 170), 'THE LETTER YOU', font=F('Nunito-900', 128), fill=PLUM)
    d.text((140, 320), 'NEVER RECEIVED.', font=F('Nunito-900', 128), fill=PLUM)
    d.line([(140, 520), (W - 140, 520)], fill=(214, 196, 205), width=4)
    d.text((140, 570), 'REASONS YOU MAY HAVE RULED YOURSELF OUT', font=F('Nunito-800', 46), fill=(110, 96, 110))
    hand = F('Caveat-700', 150)
    for i, s in enumerate(("I'm single.", 'I rent my home.', "I'm not sure I'm ready.")):
        y = 760 + i * 300
        d.text((150, y), s, font=hand, fill=INK)
        tw = d.textlength(s, font=hand)
        strike(d, 130, 150 + tw + 30, y + 112, i + 3)
    # ruled lines, very faint
    for y in range(1700, 2120, 90):
        d.line([(140, y), (W - 140, y)], fill=(225, 214, 220), width=3)
    return im.convert('RGB')


def card():
    W, H = 1600, 760
    im = Image.new('RGB', (W, H), PLUM)
    a = np.array(im).astype(np.float32)
    rng = np.random.default_rng(4)
    a = np.clip(a * (0.96 + 0.06 * rng.random((H, W, 1))), 0, 255)
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((110, 150), "You haven't been rejected.", font=F('Nunito-800', 100), fill=(255, 253, 251))
    d.text((110, 330), "You haven't even", font=F('Nunito-900', 128), fill=(255, 212, 186))
    d.text((110, 490), 'asked yet.', font=F('Nunito-900', 128), fill=(255, 212, 186))
    return im


def envelope():
    W, H = 1800, 1200
    im = paper(W, H, (246, 238, 226), 7).convert('RGB')
    d = ImageDraw.Draw(im)
    d.text((620, 520), 'To: you', font=F('Caveat-700', 190), fill=INK)
    d.line([(600, 760), (1350, 760)], fill=(200, 186, 190), width=4)
    # a leaf "stamp" (not a postage or official mark)
    d.rounded_rectangle([1460, 110, 1690, 380], 18, fill=(236, 245, 226), outline=GREEN, width=8)
    leaf = [(1575 + 70 * math.cos(t) * math.cos(0.8) - 32 * math.sin(t) * math.sin(0.8) * (1 if True else 0),
             245 + 70 * math.cos(t) * math.sin(0.8) + 32 * math.sin(t) * math.cos(0.8)) for t in np.linspace(0, 2 * math.pi, 60)]
    d.polygon(leaf, fill=GREEN)
    d.line([(1530, 290), (1620, 200)], fill=(236, 245, 226), width=6)
    return im


def damask():
    W = H = 1024
    im = Image.new('RGB', (W, H), (246, 241, 232))
    d = ImageDraw.Draw(im)
    step = 128
    for gy in range(0, H + step, step):
        for gx in range(0, W + step, step):
            ox = step // 2 if (gy // step) % 2 else 0
            cx, cy = gx + ox, gy
            for a in (-45, 45, 135, 225):
                r = math.radians(a)
                px, py = cx + 26 * math.cos(r), cy + 26 * math.sin(r)
                d.ellipse([px - 22, py - 9, px + 22, py + 9], fill=(226, 214, 200))
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(232, 222, 210))
    return im.filter(ImageFilter.GaussianBlur(1.2))


if __name__ == '__main__':
    letter().save(f'{OUT}/letter.png')
    card().save(f'{OUT}/card.png')
    envelope().save(f'{OUT}/envelope.png')
    damask().save(f'{OUT}/damask.png')
    print('textures written')
