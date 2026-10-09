"""Overlay Friends-style typography on the generated cover art."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = "/tmp/claude-0/-home-user-100/6c4f3e0a-ecdf-5bb7-9131-394110ae8620/scratchpad/fonts/"
ANTON = FONTS + "Anton-Regular.ttf"
MARKER = FONTS + "PermanentMarker-Regular.ttf"
MONT = FONTS + "Montserrat.ttf"

# The three Friends-logo dot colours
DOTS = [(229, 57, 53), (253, 216, 53), (30, 136, 229)]
WHITE = (255, 255, 255)
CREAM = (255, 244, 225)
GOLD = (255, 196, 61)

src, out = sys.argv[1], sys.argv[2]
img = Image.open(src).convert("RGBA")
W, H = img.size
s = W / 1080  # scale everything off a 1080-wide design grid


def font(path, size, wght=None):
    f = ImageFont.truetype(path, int(size * s))
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


# Top scrim so the title reads on any background
scrim = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(scrim)
top = int(H * 0.40)
for y in range(top):
    d.line([(0, y), (W, y)], fill=int(190 * (1 - y / top) ** 1.6))
bottom = int(H * 0.22)
for y in range(bottom):
    d.line([(0, H - y), (W, H - y)], fill=int(215 * (1 - y / bottom) ** 1.5))
img = Image.composite(Image.new("RGBA", (W, H), (12, 8, 6, 255)), img, scrim)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dl, ds = ImageDraw.Draw(layer), ImageDraw.Draw(shadow)


def text_w(f, t, tracking=0):
    return sum(f.getlength(c) for c in t) + tracking * (len(t) - 1)


def spaced(y, t, f, fill, tracking=0, dots=False, cx=W / 2):
    """Draw centred text; optional Friends-style coloured dots between letters."""
    dot_gap = f.size * 0.16 if dots else 0
    gaps = len(t) - 1
    total = sum(f.getlength(c) for c in t) + gaps * (tracking + dot_gap)
    x = cx - total / 2
    asc, desc = f.getmetrics()
    for i, c in enumerate(t):
        for dd, col in ((ds, (0, 0, 0, 170)), (dl, fill)):
            off = int(5 * s) if dd is ds else 0
            dd.text((x + off, y + off), c, font=f, fill=col)
        x += f.getlength(c)
        if i < gaps:
            if dots and c != " " and t[i + 1] != " ":
                r = f.size * 0.045
                cx_dot = x + (tracking + dot_gap) / 2
                cy_dot = y + asc * 0.80
                col = DOTS[i % 3]
                dl.ellipse([cx_dot - r, cy_dot - r, cx_dot + r, cy_dot + r], fill=col)
            x += tracking + dot_gap


# 1. kicker
f_kick = font(MONT, 26, 700)
k = "A  BEGINNER'S  GUIDE  TO"
spaced(int(46 * s), k, f_kick, CREAM, tracking=int(5 * s))

# 2. MARGIN (Friends-dot treatment)
f_big = font(ANTON, 142)
spaced(int(72 * s), "MARGIN", f_big, WHITE, tracking=int(2 * s), dots=True)

# 3. TRADING
f_big2 = font(ANTON, 142)
spaced(int(222 * s), "TRADING", f_big2, GOLD, tracking=int(2 * s), dots=True)

# 4. handwritten sub-line
f_hand = font(MARKER, 38)
spaced(int(H / s * s - 150 * s), "Chandler explains. Joey... tries.", f_hand, GOLD)

# 5. swipe hint
f_sw = font(MONT, 28, 700)
spaced(int(H - 76 * s), "SWIPE  TO  LEARN   →", f_sw, WHITE, tracking=int(4 * s))

shadow = shadow.filter(ImageFilter.GaussianBlur(8 * s))
img = Image.alpha_composite(img, shadow)
img = Image.alpha_composite(img, layer)
img.convert("RGB").save(out, quality=95)
print("saved", out, img.size)
