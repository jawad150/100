"""Oktrum reel thumbnails (9:16 cover + 4:5 feed), styled after JAWAD's dark "big serif word + hero object" refs.

python3 thumbs.py <assets_dir> <fonts_dir> <out_dir>
assets_dir holds the Blender renders (RGBA PNG) and logo_mark.png.
"""
import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

A, F, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W = 1080
RNG = np.random.default_rng(7)

BLUE = (81, 112, 255)
VIOLET = (132, 101, 244)
CYAN = (129, 212, 230)
LIGHT = (129, 170, 255)
DEEP = (58, 85, 224)
NAVY = (7, 9, 26)
NAVY_HI = (27, 36, 102)
WHITE = (236, 240, 255)
GREY = (170, 176, 196)


def font(name, size):
    return ImageFont.truetype(os.path.join(F, name), size)


def rgba(path):
    return Image.open(os.path.join(A, path)).convert('RGBA')


def crop_alpha(im):
    return im.crop(im.getbbox())


def fit(im, w=None, h=None):
    im = crop_alpha(im)
    s = (w / im.width) if w else (h / im.height)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


def glow_layer(size, xy, r, color, alpha):
    """soft radial light"""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - xy[0]) / r[0]) ** 2 + ((yy - xy[1]) / r[1]) ** 2)
    a = np.clip(1 - d, 0, 1) ** 2 * alpha
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = color
    out[..., 3] = a * 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def background(H, theme):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # near-black navy, slightly lifted in the middle (like the refs' dark red haze, in Oktrum navy)
    base = np.zeros((H, W, 3), np.float32)
    top = np.array((3, 4, 12), np.float32)
    mid = np.array((10, 14, 42), np.float32)
    t = yy / H
    m = np.exp(-((t - 0.62) / 0.30) ** 2)[..., None]
    base[:] = top
    base = base * (1 - m) + mid * m
    # vignette
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.55) / (H * 0.62)) ** 2)
    base *= np.clip(1.15 - v * 0.55, 0.35, 1)[..., None]
    # faint top rays (ref: soft vertical light from above)
    rays = np.zeros((H, W), np.float32)
    for cx, wd, a in ((W * 0.5, 210, 0.10), (W * 0.36, 90, 0.05), (W * 0.64, 90, 0.05)):
        rays += a * np.exp(-((xx - cx) / wd) ** 2) * np.clip(1 - yy / (H * 0.55), 0, 1)
    base += rays[..., None] * np.array(LIGHT, np.float32) * 0.6
    # faint dot grid (site motif)
    g = 36
    grid = (((xx % g) < 1.6) & ((yy % g) < 1.6)).astype(np.float32) * 0.05
    grid *= np.clip(1 - np.abs(t - 0.5) * 1.4, 0, 1)
    base += grid[..., None] * 255
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    # big soft brand-blue haze behind the hero
    im.alpha_composite(glow_layer((W, H), (W / 2, H * 0.60), (W * 0.62, H * 0.36), BLUE, 0.28))
    im.alpha_composite(glow_layer((W, H), (W * 0.18, H * 0.78), (W * 0.45, H * 0.22), VIOLET, 0.16))
    im.alpha_composite(glow_layer((W, H), (W * 0.85, H * 0.80), (W * 0.45, H * 0.22), CYAN, 0.10))
    return im


def particles(H, floor_y, n_floor=9000, n_air=70):
    """blue dust floor + sparse floating motes (the refs' red glitter, in brand blue/cyan)"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n_floor):
        y = floor_y + (H - floor_y) * (RNG.random() ** 0.75)
        x = RNG.random() * W
        depth = (y - floor_y) / max(1, H - floor_y)
        # denser in the centre band, thinning to the sides near the horizon
        if RNG.random() > 0.35 + 0.65 * depth and abs(x - W / 2) > W * 0.3:
            continue
        r = 0.6 + 1.6 * depth * RNG.random()
        c = BLUE if RNG.random() < 0.6 else (CYAN if RNG.random() < 0.5 else LIGHT)
        a = int(60 + 150 * RNG.random() * (0.4 + 0.6 * depth))
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (a,))
    for _ in range(n_air):
        x, y = RNG.random() * W, RNG.random() * H * 0.9
        r = 1.0 + 2.2 * RNG.random()
        c = LIGHT if RNG.random() < 0.6 else CYAN
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (int(90 + 120 * RNG.random()),))
    glow = lay.filter(ImageFilter.GaussianBlur(3))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(lay)
    return out


def spaced(draw, xy, text, fnt, fill, track, anchor='mm'):
    """letter-spaced caps; xy is the centre (anchor mm) or left edge (lm) or right edge (rm)"""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if anchor == 'mm':
        x -= total / 2
    elif anchor == 'rm':
        x -= total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill, anchor='lm')
        x += w + track
    return total


def big_word(word, size, H):
    """the refs' giant bevelled serif word, in the Oktrum blue: gradient face, dark extrude, rim light, glow"""
    fnt = font('IS-Regular.ttf', size)
    pad = 120
    tmp = ImageDraw.Draw(Image.new('L', (10, 10)))
    l, t, r, b = tmp.textbbox((0, 0), word, font=fnt)
    w, h = r - l + pad * 2, b - t + pad * 2
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), word, font=fnt, fill=255)
    m = np.asarray(mask, np.float32) / 255
    # face gradient: light blue top -> brand blue -> deep blue bottom
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    c0, c1, c2 = (np.array(c, np.float32) for c in ((160, 186, 255), (88, 116, 255), (44, 66, 214)))
    face = np.where(yy < 0.5, c0 + (c1 - c0) * (yy / 0.5), c1 + (c2 - c1) * ((yy - 0.5) / 0.5))
    face = np.broadcast_to(face, (h, w, 3)).copy()
    # bevel: lighten the up-left edges, darken down-right (emboss from the mask)
    blur = np.asarray(mask.filter(ImageFilter.GaussianBlur(3.5)), np.float32) / 255
    gy, gx = np.gradient(blur)
    shade = np.clip(-(gx + gy) * 6.0, -1, 1)[..., None]
    face = face + np.where(shade > 0, (255 - face) * shade * 0.75, face * shade * 0.55)
    out = np.zeros((h, w, 4), np.float32)
    # extrude: stacked offsets towards down-right in deep navy
    ext = np.zeros((h, w), np.float32)
    steps = 12
    for i in range(steps, 0, -1):
        ext = np.maximum(ext, np.roll(np.roll(m, i, 0), int(i * 0.5), 1) * 1.0)
    ext_col = np.array((22, 30, 96), np.float32)
    out[..., :3] = ext_col
    out[..., 3] = ext * 255
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + face * m[..., None]
    out[..., 3] = np.maximum(out[..., 3], m * 255)
    word_im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
    # outer glow
    g = Image.new('RGBA', (w, h), BLUE + (0,))
    g.putalpha(mask.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55)))
    res = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    res.alpha_composite(g)
    # soft drop shadow under the extrude
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh.putalpha(Image.fromarray((ext * 200).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)))
    res.alpha_composite(sh, (6, 14))
    res.alpha_composite(word_im)
    return res, pad - l, pad - t, r - l, b - t


def streak(H, y, x0, x1, color=CYAN, alpha=0.9, thick=3):
    """anamorphic lens streak (ref 3's horizontal flare across the word)"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    xx = np.arange(W, dtype=np.float32)
    cx = (x0 + x1) / 2
    a = np.clip(1 - np.abs(xx - cx) / ((x1 - x0) / 2), 0, 1) ** 1.6
    band = np.zeros((40, W, 4), np.float32)
    yy = np.arange(40, dtype=np.float32)[:, None] - 20
    band[..., :3] = np.array(color, np.float32)
    band[..., 3] = (np.exp(-(yy / thick) ** 2) * a[None] * 255 * alpha)
    b = Image.fromarray(band.astype(np.uint8), 'RGBA')
    lay.alpha_composite(b, (0, int(y) - 20))
    wide = b.resize((W, 120)).filter(ImageFilter.GaussianBlur(14))
    lay.alpha_composite(wide, (0, int(y) - 60))
    return lay


def reflection(obj, height_frac=0.35, alpha=0.32):
    r = obj.transpose(Image.FLIP_TOP_BOTTOM)
    h = int(r.height * height_frac)
    r = r.crop((0, 0, r.width, h))
    grad = np.linspace(alpha, 0, h, dtype=np.float32) ** 1.4
    a = np.asarray(r.getchannel('A'), np.float32) * grad[:, None]
    r.putalpha(Image.fromarray(a.astype(np.uint8)))
    return r.filter(ImageFilter.GaussianBlur(3))


def place(canvas, obj, cx, cy, blur=0, alpha=1.0, glow=None):
    pad = int(max(blur * 3, (glow[1] * 3) if glow else 0)) + 2
    big = Image.new('RGBA', (obj.width + pad * 2, obj.height + pad * 2), (0, 0, 0, 0))
    big.alpha_composite(obj, (pad, pad))
    obj = big
    if blur:
        obj = obj.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1:
        obj = obj.copy()
        obj.putalpha(obj.getchannel('A').point(lambda v: int(v * alpha)))
    if glow:
        g = Image.new('RGBA', obj.size, glow[0] + (0,))
        g.putalpha(obj.getchannel('A').filter(ImageFilter.GaussianBlur(glow[1])).point(lambda v: int(v * glow[2])))
        canvas.alpha_composite(g, (int(cx - obj.width / 2), int(cy - obj.height / 2)))
    canvas.alpha_composite(obj, (int(cx - obj.width / 2), int(cy - obj.height / 2)))


def icons(draw, H, y):
    """bottom row: SAVE FOR LATER (bookmark) / FOLLOW FOR MORE (bubble), as in the refs"""
    f = font('IT-Medium.ttf', 22)
    x = 86
    draw.polygon([(x, y - 22), (x + 20, y - 22), (x + 20, y + 20), (x + 10, y + 10), (x, y + 20)], fill=GREY)
    draw.text((x + 30, y - 10), 'SAVE', font=f, fill=GREY, anchor='lm')
    draw.text((x + 30, y + 10), 'FOR LATER', font=f, fill=GREY, anchor='lm')
    x = W - 238
    draw.rounded_rectangle((x, y - 22, x + 28, y + 4), 6, fill=GREY)
    draw.polygon([(x + 6, y + 2), (x + 14, y + 2), (x + 6, y + 14)], fill=GREY)
    draw.text((x + 40, y - 10), 'FOLLOW', font=f, fill=GREY, anchor='lm')
    draw.text((x + 40, y + 10), 'FOR MORE', font=f, fill=GREY, anchor='lm')


def arrow_btn(draw, cx, cy):
    r = 40
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(220, 226, 240), width=3)
    draw.line((cx - 16, cy, cx + 16, cy), fill=LIGHT, width=4)
    draw.line((cx + 2, cy - 14, cx + 17, cy + 1), fill=LIGHT, width=4)
    draw.line((cx + 2, cy + 14, cx + 17, cy - 1), fill=LIGHT, width=4)


def compose(spec, H):
    feed = H < 1600
    # the feed (4:5) layout is the 9:16 design mapped onto a shorter frame: Y() moves, Z scales objects
    Y = (lambda y: y) if not feed else (lambda y: y * 0.882 - 110)
    Z = 1.0 if not feed else 0.88
    cv = background(H, spec)
    floor_y = Y(1345)
    d = ImageDraw.Draw(cv)
    # top: oktrum.com (where the refs put the handle) + the Oktrum dot-sphere mark as the badge
    top = Y(250)
    d.text((W / 2, top), 'oktrum.com', font=font('IT-SemiBold.ttf', 30), fill=LIGHT, anchor='mm')
    place(cv, fit(rgba('logo_mark.png'), h=120), W / 2, top + 100)
    y_caps = top + 210
    spaced(d, (W / 2, y_caps), spec['caps'], font('IT-Medium.ttf', spec.get('caps_size', 46)), WHITE,
           spec.get('caps_track', 16))
    bw, ox, oy, tw, th = big_word(spec['word'], int(spec['word_size'] * (1 if not feed else 0.92)), H)
    wx = int(W / 2 - tw / 2 - ox)
    wy = int(y_caps + 30 + spec.get('word_dy', 0) * Z - oy)
    hero = rgba(spec['hero'])
    hero = fit(hero, w=int(spec['hero_w'] * Z)) if spec.get('hero_w') else fit(hero, h=int(spec['hero_h'] * Z))
    hx, hy = W / 2 + spec.get('hero_dx', 0), Y(spec['hero_y'])
    if spec.get('streak'):
        cv.alpha_composite(streak(H, wy + oy + th * 0.55, 30, W - 30))
    for e in spec.get('extras_back', []):
        place(cv, fit(rgba(e['img']), w=int(e['w'] * Z)), e['x'], Y(e['y']), blur=e.get('blur', 0),
              alpha=e.get('a', 1))
    cv.alpha_composite(bw, (wx, wy))
    cv.alpha_composite(particles(H, floor_y))
    refl = reflection(hero)
    base_y = hy + hero.height / 2 - spec.get('foot', 0) * Z
    cv.alpha_composite(refl, (int(hx - refl.width / 2), int(base_y)))
    cv.alpha_composite(glow_layer((W, H), (hx, base_y), (hero.width * 0.55, 40), BLUE, 0.55))
    place(cv, hero, hx, hy, glow=(BLUE, 36, 0.45))
    for e in spec.get('extras_front', []):
        o = fit(rgba(e['img']), w=int(e['w'] * Z))
        if e.get('rot'):
            o = o.rotate(e['rot'], resample=Image.BICUBIC, expand=True)
        place(cv, o, e['x'], Y(e['y']), blur=e.get('blur', 0), alpha=e.get('a', 1), glow=e.get('glow'))
    d = ImageDraw.Draw(cv)
    ys = Y(spec['split_y'])
    fs = font('IT-Medium.ttf', 42)
    spaced(d, (86, ys), spec['left'], fs, WHITE, spec.get('left_track', 30), anchor='lm')
    spaced(d, (W - 74, ys), spec['right'], fs, WHITE, spec.get('right_track', 14), anchor='rm')
    arrow_btn(d, W - 145, Y(spec['arrow_y']))
    icons(d, H, Y(1588))
    return cv.convert('RGB')


SPECS = {
    'reel1_every_market': dict(
        caps='TRADE THE GLOBAL', word='Markets', word_size=330, word_dy=-10, caps_track=18,
        hero='okt_mark.png', hero_h=560, hero_y=1060, foot=30,
        extras_back=[dict(img='gold_bar.png', w=210, x=860, y=905, blur=2.0, a=0.9),
                     dict(img='chip.png', w=170, x=210, y=935, blur=3.0, a=0.85)],
        extras_front=[dict(img='coin_btc.png', w=230, x=250, y=1200, glow=(BLUE, 24, 0.3)),
                      dict(img='coin_usd.png', w=200, x=840, y=1250, blur=1.0, glow=(BLUE, 24, 0.3)),
                      dict(img='coin_btc.png', w=330, x=0, y=1740, blur=16, a=0.7),
                      dict(img='gold_bar.png', w=380, x=1060, y=1770, blur=18, a=0.65)],
        left='ONE', right='PLATFORM.', split_y=1450, arrow_y=1080, left_track=34, right_track=16),
    'reel2_blink': dict(
        caps='THE MARKET MOVES IN A', word='Blink.', word_size=380, word_dy=-20, caps_size=40, caps_track=13,
        hero='candles3d.png', hero_w=800, hero_y=1050, foot=60, streak=True,
        extras_front=[dict(img='candles3d.png', w=420, x=40, y=1740, blur=16, a=0.6),
                      dict(img='candles3d.png', w=380, x=1060, y=1720, blur=18, a=0.55)],
        left='SEIZE', right='EVERY OPPORTUNITY.', split_y=1450, arrow_y=1220, left_track=24, right_track=10),
    'reel3_peace_of_mind': dict(
        caps='YOUR ACCOUNT CAN NEVER GO BELOW', word='Zero', word_size=420, word_dy=-30, caps_size=33,
        caps_track=9,
        hero='shield_lock.png', hero_h=600, hero_y=1125, foot=30, streak=True,
        extras_front=[dict(img='shield_lock.png', w=300, x=40, y=1720, blur=16, a=0.6, rot=14),
                      dict(img='shield_lock.png', w=280, x=1050, y=1740, blur=18, a=0.55, rot=-12)],
        left='PEACE', right='OF MIND.', split_y=1450, arrow_y=1120, left_track=30, right_track=18),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[4:] or list(SPECS)
    for name in only:
        for H, tag in ((1920, 'reel_1080x1920'), (1350, 'feed_1080x1350')):
            im = compose(SPECS[name], H)
            p = os.path.join(OUT, f'oktrum_{name}_thumb_{tag}.png')
            im.save(p, optimize=True)
            print(p)
