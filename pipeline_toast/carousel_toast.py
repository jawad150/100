"""Organic Fostering carousel: "Can I make toast whenever?" (from the Toast Reel brief), after the user's Pinterest
'What's Trending' reference: slide 1 is a white disc with photo cards circling around a two-tone title; the next slides
carry the story with a phone mock-up playing a clip, header strip, big title, quote and body text. Slide 7 brings the
circling disc back around the official logo. 4:5 (1080x1350), each slide an MP4 (Instagram carousels play video) plus
a JPG still.

Usage: python3 carousel_toast.py [slide numbers...]   -> workspace_toast/out/slide_N.mp4/.jpg (+ strip)
"""
import os, sys, math, functools, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_toast'
CL = f'{S}/clips'
FON = f'{ROOT}/workspace_sol/fonts'
OUT = f'{S}/out'
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1350, 30


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PLUM, MAG, ORANGE, GREEN, IVORY, INK = hx('5B174F'), hx('B7006E'), hx('FF6411'), hx('61A80A'), hx('FCF8F5'), hx('321F35')
PINK, PINK2, BLUSH, WHITE = hx('EDB9D6'), hx('E3A1C6'), hx('F6EAF3'), (255, 255, 255)


@functools.lru_cache(None)
def F(w, s):
    return ImageFont.truetype(f'{FON}/Nunito-{w}.ttf', int(s))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_back(u, s=1.6):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


@functools.lru_cache(None)
def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W * 0.5) / W, (yy - H * 0.45) / H)
    a = np.array(PINK, np.float32)
    b = np.array(PINK2, np.float32)
    c = a * (1 - np.clip(r * 1.3, 0, 1))[..., None] + b * np.clip(r * 1.3, 0, 1)[..., None]
    rng = np.random.default_rng(1)
    c += rng.normal(0, 1.6, (H, W, 1))
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).convert('RGBA')


def frame_of(clip, t):
    cap = cv2.VideoCapture(f'{CL}/{clip}.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    cap.release()
    return Image.fromarray(f[..., ::-1])


def cover_crop(im, w, h, fx=0.5, fy=0.5):
    iw, ih = im.size
    s = max(w / iw, h / ih)
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int(clamp(fx * nw - w / 2, 0, nw - w))
    y = int(clamp(fy * nh - h / 2, 0, nh - h))
    return im.crop((x, y, x + w, y + h))


def rounded(im, r, border=0, bcol=WHITE):
    w, h = im.size
    out = Image.new('RGBA', (w + 2 * border, h + 2 * border), (0, 0, 0, 0))
    m = Image.new('L', out.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, out.size[0] - 1, out.size[1] - 1], r + border, fill=255)
    base = Image.new('RGBA', out.size, bcol + (255,))
    base.paste(im.convert('RGB'), (border, border))
    out.paste(base, (0, 0), m)
    return out


def shadowed(c, spr, x, y, blur=18, off=(10, 16), a=90):
    sh = Image.new('RGBA', spr.size, (60, 10, 50, 0))
    sh.putalpha(spr.split()[3].point(lambda v: v * a // 255))
    pad = blur * 3
    big = Image.new('RGBA', (spr.size[0] + 2 * pad, spr.size[1] + 2 * pad), (0, 0, 0, 0))
    big.paste(sh, (pad, pad))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    c.alpha_composite(big, (int(x - pad + off[0]), int(y - pad + off[1])))
    c.alpha_composite(spr, (int(x), int(y)))


def text_card(lines, bg, fg, w=146, h=182):
    im = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(im)
    y = h / 2 - (len(lines) - 1) * 21
    for ln, sz in lines:
        d.text((w / 2, y), ln, font=F(900, int(sz * 0.8)), fill=fg, anchor='mm')
        y += 42
    return im


# ------------------------------------------------------------------ the circling disc
CARDS = [('photo', '43903', 4.0, 0.55), ('text', [('6:42', 50), ('pm', 34)], PLUM, IVORY), ('photo', '42912', 1.5, 0.5),
         ('photo', '46512', 8.0, 0.55), ('photo', '40522', 4.0, 0.55), ('text', [('Even', 34), ('after tea.', 34)], MAG, IVORY),
         ('photo', '28980', 3.0, 0.35), ('photo', '3797', 5.0, 0.6), ('photo', '898', 6.0, 0.6),
         ('text', [('8:16', 50), ('pm', 34)], ORANGE, IVORY), ('photo', '28983', 6.0, 0.5), ('photo', '4866', 4.0, 0.5)]


@functools.lru_cache(None)
def card_sprites(w=146, h=182):
    out = []
    for kind, a, b, cfx in CARDS:
        if kind == 'photo':
            im = cover_crop(frame_of(a, b), w, h, fx=cfx)
        else:
            im = text_card(a, b, cfx, w, h)
        out.append(rounded(im, 20, 7))
    return out


def disc(c, cx, cy, R, t, period=12.0, pop_u=1.0):
    """White disc + cards orbiting at radius R*0.77, each card leaning along the circle."""
    k = e_back(pop_u, 1.2)
    rr = int(R * k)
    if rr < 4:
        return
    d = Image.new('RGBA', (2 * rr + 80, 2 * rr + 80), (0, 0, 0, 0))
    ImageDraw.Draw(d).ellipse([40, 40, 40 + 2 * rr, 40 + 2 * rr], fill=(255, 255, 255, 255))
    sh = d.copy()
    sh.putalpha(sh.split()[3].point(lambda v: v * 70 // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    c.alpha_composite(sh, (int(cx - rr - 40 + 8), int(cy - rr - 40 + 22)))
    c.alpha_composite(d, (int(cx - rr - 40), int(cy - rr - 40)))
    # inner hint of a ring (like a record)
    ImageDraw.Draw(c).ellipse([cx - rr * 0.5, cy - rr * 0.5, cx + rr * 0.5, cy + rr * 0.5], outline=(240, 228, 236, 255), width=3)
    cards = card_sprites()
    rot0 = 360 * (t / period)
    for i, spr in enumerate(cards):
        ci = clamp((pop_u - 0.3 - i * 0.04) / 0.4)
        if ci <= 0:
            continue
        ang = math.radians(rot0 + i * 360 / len(cards) - 90)
        r = R * 0.79 * k
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        lean = -18 * math.cos(ang) + 5 * math.sin(ang * 3 + i)
        s = e_back(ci) * (R / 490)
        sp = spr.resize((max(2, int(spr.size[0] * s * k)), max(2, int(spr.size[1] * s * k))), Image.LANCZOS)
        sp = sp.rotate(lean, resample=Image.BICUBIC, expand=True)
        shadowed(c, sp, x - sp.size[0] / 2, y - sp.size[1] / 2, blur=10, off=(5, 9), a=70)


def chevron(c, x=W - 70, y=H * 0.5, a=1.0):
    d = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(d).rounded_rectangle([0, 0, 99, 99], 26, fill=(255, 245, 250, int(235 * a)))
    ImageDraw.Draw(d).line([(40, 30), (60, 50), (40, 70)], fill=PLUM + (int(255 * a),), width=7, joint='curve')
    c.alpha_composite(d, (int(x - 50), int(y - 50)))


def label_box(c, text, w, size, bg, fg, cx, y, a=1.0, pad=(34, 16)):
    f = F(900, size)
    tw = f.getlength(text)
    bw, bh = int(tw + pad[0] * 2), int(size * 1.25 + pad[1] * 2)
    im = Image.new('RGBA', (bw, bh), bg + (int(255 * a),))
    ImageDraw.Draw(im).text((bw / 2, bh / 2), text, font=f, fill=fg + (int(255 * a),), anchor='mm')
    c.alpha_composite(im, (int(cx - bw / 2), int(y - bh / 2)))


def slide_cover(t):
    c = background().copy()
    u = t / 1.0
    disc(c, W / 2, 640, 490, t, period=12.0, pop_u=clamp(t / 0.9))
    k = e_back(clamp((t - 0.5) / 0.5), 1.3)
    if k > 0:
        label_box(c, 'Can I make toast', 0, int(62 * (0.8 + 0.2 * k)), PLUM, IVORY, W / 2, 600, clamp((t - 0.5) / 0.2))
        label_box(c, 'whenever?', 0, int(70 * (0.8 + 0.2 * k)), MAG, IVORY, W / 2, 700, clamp((t - 0.62) / 0.2))
        d = ImageDraw.Draw(c)
        al = int(255 * clamp((t - 0.9) / 0.3))
        d.text((W / 2, 790), 'A FIRST-EVENING STORY', font=F(800, 24), fill=PLUM + (al,), anchor='mm')
    d = ImageDraw.Draw(c)
    d.text((60, 1220), 'ORGANIC FOSTERING', font=F(900, 26), fill=PLUM)
    d.text((W - 60, 1220), 'DRAMATISATION', font=F(800, 24), fill=PLUM, anchor='ra')
    bar(c)
    chevron(c, a=0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 4)))
    return c


def bar(c):
    d = ImageDraw.Draw(c)
    for i, col in enumerate((MAG, ORANGE, GREEN)):
        d.rectangle([int(W * i / 3), H - 14, int(W * (i + 1) / 3), H], fill=col)


# ------------------------------------------------------------------ story slides
class Reader:
    def __init__(self, clip, start):
        self.cap = cv2.VideoCapture(f'{CL}/{clip}.mp4')
        self.cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.t = 0.0
        self.last = None

    def at(self, t):
        while self.last is None or self.t + 1 / self.fps <= t + 1e-4:
            ok, f = self.cap.read()
            if not ok:
                break
            self.last = f
            self.t += 1 / self.fps if self.last is not None else 0
        return Image.fromarray(self.last[..., ::-1])


def phone(c, img, x, y, w=400, a=1.0):
    h = int(w * 2.05)
    scr = cover_crop(img, w - 28, h - 28, fx=PHONE_FX)
    body = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 58, fill=255)
    base = Image.new('RGBA', (w, h), (255, 252, 254, 255))
    sm = Image.new('L', (w - 28, h - 28), 0)
    ImageDraw.Draw(sm).rounded_rectangle([0, 0, w - 29, h - 29], 46, fill=255)
    base.paste(scr, (14, 14), sm)
    ImageDraw.Draw(base).rounded_rectangle([w / 2 - 60, 26, w / 2 + 60, 50], 12, fill=(20, 10, 20, 255))
    body.paste(base, (0, 0), m)
    shadowed(c, body, x, y, blur=24, off=(14, 22), a=110)


PHONE_FX = 0.5


def wrap(text, font, width):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t2 = (cur + ' ' + w_).strip()
        if font.getlength(t2) > width and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t2
    lines.append(cur)
    return lines


def story(t, n, title, quote, body, clip, start, fx=0.5, who=None, title_col=PLUM, quote2=None):
    global PHONE_FX
    PHONE_FX = fx
    c = background().copy()
    d = ImageDraw.Draw(c)
    d.text((60, 60), 'ORGANIC FOSTERING', font=F(900, 24), fill=PLUM)
    d.text((W - 60, 60), f'DRAMATISATION  ·  {n}/7', font=F(800, 22), fill=PLUM, anchor='ra')
    # title slides in
    k = e_out((t - 0.1) / 0.6)
    if k > 0:
        tl = Image.new('RGBA', (W, 170), (0, 0, 0, 0))
        ImageDraw.Draw(tl).text((60, 10), title, font=F(900, 118), fill=title_col + (int(255 * k),))
        c.alpha_composite(tl, (int(-40 * (1 - k)), 150))
    # speaker label + quote, typed on
    y = 340
    if who:
        a = clamp((t - 0.5) / 0.3)
        label_box(c, who.upper(), 0, 22, MAG, IVORY, 60 + F(900, 22).getlength(who.upper()) / 2 + 22, y + 8, a, pad=(22, 8))
        y += 60
    fq = F(900, 54)
    for qi, q in enumerate([quote] + ([quote2] if quote2 else [])):
        lines = wrap(q, fq, 620)
        t0 = 0.6 + qi * 1.6
        n_chars = int(len(q) * clamp((t - t0) / (0.035 * len(q) + 0.2)))
        done = 0
        for ln in lines:
            vis = ln[:max(0, n_chars - done)]
            done += len(ln) + 1
            if vis:
                ImageDraw.Draw(c).text((60, y), vis, font=fq, fill=(MAG if qi == 0 else PLUM))
            y += 68
        y += 18
    # body
    if body:
        fb = F(700, 34)
        a = int(255 * clamp((t - 2.4) / 0.5))
        for ln in wrap(body, fb, 560):
            ImageDraw.Draw(c).text((60, y + 20), ln, font=fb, fill=INK + (a,))
            y += 48
    # phone rises in from the bottom right and plays the clip
    k = e_out((t - 0.2) / 0.9)
    img = READERS[n].at(t)
    phone(c, img, 640, int(H - 640 + 700 * (1 - k)), 400)
    bar(c)
    chevron(c, W - 70, 680, 0.55)
    return c


def slide_end(t):
    c = background().copy()
    disc(c, W / 2, 560, 445, t, period=12.0, pop_u=clamp(t / 0.9))
    lg = Image.open(f'{ROOT}/workspace_three/web/logo.png').convert('RGBA')
    lg = lg.crop(lg.getbbox())
    lw = 300
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    k = e_back(clamp((t - 0.6) / 0.5), 1.2)
    if k > 0:
        l2 = lg.resize((max(2, int(lg.width * k)), max(2, int(lg.height * k))), Image.LANCZOS)
        c.alpha_composite(l2, (int(W / 2 - l2.width / 2), int(560 - l2.height / 2)))
    d = ImageDraw.Draw(c)
    a = int(255 * clamp((t - 1.0) / 0.4))
    d.text((W / 2, 1050), 'Thinking about fostering', font=F(900, 50), fill=PLUM + (a,), anchor='mm')
    d.text((W / 2, 1110), 'in Greater Manchester?', font=F(900, 50), fill=PLUM + (a,), anchor='mm')
    kb = e_back(clamp((t - 1.4) / 0.4))
    if kb > 0:
        bw, bh = int(480 * kb), 96
        btn = Image.new('RGBA', (max(2, bw), bh), (0, 0, 0, 0))
        ImageDraw.Draw(btn).rounded_rectangle([0, 0, max(1, bw - 1), bh - 1], 48, fill=MAG)
        if kb > 0.6:
            ImageDraw.Draw(btn).text((bw / 2, bh / 2), 'Start your enquiry', font=F(900, 40), fill=IVORY, anchor='mm')
        c.alpha_composite(btn, (int(W / 2 - bw / 2), 1160))
    d.text((W / 2, 1290), 'Link in bio  ·  organicfostering.co.uk', font=F(800, 30), fill=PLUM + (int(255 * clamp((t - 1.8) / 0.4)),), anchor='mm')
    bar(c)
    return c


SLIDES = {
    1: (12.0, slide_cover),
    2: (8.0, lambda t: story(t, 2, '6:42 pm', '“Can I make toast whenever?”', 'Their first evening. A hand reaches towards the bread, then a look across the kitchen.',
                            '43903', 3.0, 0.45, who='Teen')),
    3: (8.0, lambda t: story(t, 3, 'Of course.', '“Yeah, of course. Plates are in there. Jam’s in the fridge.”',
                            'The carer carries on washing up and nods towards the cupboard.', '40522', 2.0, 0.55, who='Carer')),
    4: (8.0, lambda t: story(t, 4, 'After tea?', '“Even after tea?”', None, '46512', 6.0, 0.55, who='Teen', quote2='“Even after tea.”')),
    5: (8.0, lambda t: story(t, 5, '8:16 pm', '“Want one?”', 'Later that evening. Two plates out of the cupboard, bread in the toaster.',
                            '898', 2.0, 0.62, who='Teen', quote2='“Go on, then.”')),
    6: (8.0, lambda t: story(t, 6, 'Two plates.', 'Sometimes feeling at home starts with knowing you can help yourself.', None,
                            '28980', 4.0, 0.42, title_col=MAG)),
    7: (8.0, slide_end),
}
CLIPS = {2: ('43903', 3.0), 3: ('40522', 2.0), 4: ('46512', 6.0), 5: ('898', 2.0), 6: ('28980', 4.0)}
READERS = {}


def render(n):
    dur, fn = SLIDES[n]
    if n in CLIPS:
        READERS[n] = Reader(*CLIPS[n])
    nf = int(dur * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                          f'{OUT}/slide_{n}.mp4'], stdin=subprocess.PIPE)
    still_t = {1: 11.0, 7: 7.5}.get(n, 7.5)
    for i in range(nf):
        t = i / FPS
        im = fn(t).convert('RGB')
        p.stdin.write(im.tobytes())
        if abs(t - still_t) < 0.5 / FPS:
            im.save(f'{OUT}/slide_{n}.jpg', quality=93)
    p.stdin.close()
    p.wait()
    print('slide', n, flush=True)


if __name__ == '__main__':
    ns = [int(a) for a in sys.argv[1:]] or list(SLIDES)
    for n in ns:
        render(n)
    ims = [Image.open(f'{OUT}/slide_{n}.jpg') for n in SLIDES if os.path.exists(f'{OUT}/slide_{n}.jpg')]
    if ims:
        sw = W // 3
        st = Image.new('RGB', (len(ims) * (sw + 10), H // 3), (40, 30, 40))
        for i, im in enumerate(ims):
            st.paste(im.resize((sw, H // 3)), (i * (sw + 10), 0))
        st.save(f'{OUT}/strip.jpg', quality=90)
