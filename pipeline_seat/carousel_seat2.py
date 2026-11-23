"""BMHC carousel "I saved you a seat." - v2, after the user's second Pinterest reference: hands typing in the dark, a big
phone keyboard laid over the scene with each key popping as it's tapped, the line typing out top-left in white bold
with a gold cursor, a white silk end card. BMHC: Inter ExtraBold, ink, Heritage Magenta on the key words, four bars.

Slides 1-4 type the brief's lines; slide 5 is the silk card with the closing question and the official logo.
Each slide: MP4 (with soft key taps) + JPG. Usage: python3 carousel_seat2.py [n ...]
"""
import os, sys, math, functools, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_seat2'
OUT = f'{S}/out'
os.makedirs(OUT, exist_ok=True)
CLIP = f'{S}/clips/4915.mp4'
FON = f'{ROOT}/workspace_sol/fonts'
W, H, FPS, SR = 1080, 1350, 30, 48000
INK, MAG, TEAL, ORANGE, LIME, WHITE = (11, 11, 11), (230, 5, 133), (45, 200, 146), (255, 66, 0), (105, 255, 0), (255, 255, 255)
GOLD = (232, 181, 74)
BARS = (MAG, TEAL, ORANGE, LIME)


@functools.lru_cache(None)
def F(w, s):
    return ImageFont.truetype(f'{FON}/Inter-{w}.ttf', int(s))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_back(u, s=1.6):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


# ------------------------------------------------------------------ typing schedule
def schedule(text, t0=0.5, seed=0):
    """Time each character is typed (a human rhythm: quick letters, small pauses after spaces/punctuation)."""
    rng = np.random.default_rng(seed)
    ts, t = [], t0
    for ch in text:
        ts.append(t)
        d = rng.uniform(0.06, 0.12)
        if ch == ' ':
            d += rng.uniform(0.03, 0.08)
        if ch in '.,?”':
            d += 0.22
        t += d
    return ts, t


# ------------------------------------------------------------------ keyboard (laid over the scene, like the reference)
ROWS = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
KB_Y, KB_W, KEY_H = 820, 1000, 118


def key_pos(ch):
    ch = ch.lower()
    for r, row in enumerate(ROWS):
        if ch in row:
            k = row.index(ch)
            n = len(row)
            kw = KB_W / 10
            x0 = W / 2 - n * kw / 2 + (kw if r == 2 else 0) * 0
            if r == 2:
                x0 = W / 2 - 7 * kw / 2
            return x0 + (k + 0.5) * kw, KB_Y + r * KEY_H
    if ch == ' ':
        return W / 2, KB_Y + 3 * KEY_H
    return None


@functools.lru_cache(None)
def keyboard_layer():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = F(500, 46)
    for r, row in enumerate(ROWS):
        for ch in row:
            x, y = key_pos(ch)
            d.text((x, y), ch, font=f, fill=(235, 235, 235, 210), anchor='mm')
    y3 = KB_Y + 3 * KEY_H
    d.text((W / 2 - 7 * 50 - 40, KB_Y + 2 * KEY_H), '⇧', font=F(500, 44), fill=(235, 235, 235, 190), anchor='mm')
    d.text((W / 2 + 7 * 50 + 40, KB_Y + 2 * KEY_H), '⌫', font=F(500, 40), fill=(235, 235, 235, 190), anchor='mm')
    d.text((110, y3), '123', font=F(500, 34), fill=(235, 235, 235, 190), anchor='mm')
    d.rounded_rectangle([W / 2 - 300, y3 - 34, W / 2 + 300, y3 + 34], 14, fill=(255, 255, 255, 26))
    d.text((W - 120, y3), 'return', font=F(500, 32), fill=(235, 235, 235, 190), anchor='mm')
    return np.asarray(im).astype(np.float32) / 255


def key_pop(c, ch, u):
    """The tapped key pops up big (the reference's enlarged key), then settles."""
    p = key_pos(ch)
    if p is None or u < 0 or u > 0.32 or ch == ' ':
        return
    x, y = p
    k = e_back(clamp(u / 0.1)) * (1 - clamp((u - 0.2) / 0.12))
    if k <= 0.02:
        return
    s = int(84 * (0.7 + 0.6 * k))
    im = Image.new('RGBA', (220, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([110 - s * 0.55, 110 - s * 0.7, 110 + s * 0.55, 110 + s * 0.7], 18, fill=(255, 255, 255, int(235 * k)))
    d.text((110, 110), ch.lower(), font=F(800, s), fill=INK + (int(255 * k),), anchor='mm')
    a = np.asarray(im).astype(np.float32) / 255
    paste(c, a, x, y - 70 * k)


def paste(c, a, cx, cy, op=1.0):
    h, w = a.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = s[..., 3:4] * op
    c[Y0:Y1, X0:X1] = c[Y0:Y1, X0:X1] * (1 - al) + s[..., :3] * al


# ------------------------------------------------------------------ the typed line
def wrap_words(words, size, width):
    f = F(800, size)
    lines, cur = [], []
    for w_, col in words:
        test = ' '.join(x for x, _ in cur + [(w_, col)])
        if (f.getlength(test) > width or w_.startswith('“')) and cur:
            lines.append(cur)
            cur = [(w_, col)]
        else:
            cur.append((w_, col))
    lines.append(cur)
    return lines


def typed_text(c, words, n, t, size=70, x0=64, y0=96, lead=1.18):
    """Draw the first n characters of the (word, colour) list, wrapped, with a blinking gold cursor."""
    f = F(800, size)
    lines = wrap_words(words, size, W - 2 * x0)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    left = n
    y = y0
    cx, cy = x0, y0
    done = False
    for li, line in enumerate(lines):
        x = x0
        for wi, (w_, col) in enumerate(line):
            token = w_ + (' ' if wi < len(line) - 1 else '')
            vis = token[:max(0, left)]
            if vis:
                d.text((x, y), vis, font=f, fill=col + (255,))
            left -= len(token)
            x += f.getlength(vis)
            if left <= 0 and not done:
                cx, cy = x, y
                done = True
            if left <= 0:
                break
        if left <= 0:
            break
        left -= 1 if li < len(lines) - 1 else 0
        y += size * lead
    if not done:
        cx, cy = x, y
    if int(t * 2.2) % 2 == 0 or n < sum(len(w_) + 1 for w_, _ in words) - 1:
        d.rectangle([cx + 4, cy + 4, cx + 9, cy + size * 1.08], fill=GOLD + (255,))
    over = np.asarray(im).astype(np.float32) / 255
    al = over[..., 3:4]
    c[:] = c * (1 - al) + over[..., :3] * al


# ------------------------------------------------------------------ footage
class Footage:
    def __init__(self, start):
        self.cap = cv2.VideoCapture(CLIP)
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
            self.t += 1 / self.fps
        img = self.last[..., ::-1].astype(np.float32) / 255
        ih, iw = img.shape[:2]
        s = H / ih * 1.18
        cx, cy = iw * 0.47, ih * 0.52
        M = np.array([[s, 0, W / 2 - s * cx], [0, s, H * 0.62 - s * cy]], np.float32)
        return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)


@functools.lru_cache(None)
def shade():
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    top = np.clip((yy - 0.18) / 0.3, 0, 1)
    v = top * (1 - 0.45 * xx ** 2) * (1 - 0.5 * np.clip((yy - 0.85) / 0.15, 0, 1))
    return v[..., None]


def dark(img):
    lum = img.mean(-1, keepdims=True)
    img = lum + (img - lum) * 0.8
    img = np.clip((img - 0.04) * 0.9, 0, 1) ** 1.15
    return img * shade()


def bars(c, h=12):
    for i, col in enumerate(BARS):
        c[H - h:, int(W * i / 4):int(W * (i + 1) / 4)] = np.array(col, np.float32) / 255


def small_tag(c, n):
    im = Image.new('RGBA', (W, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((64, 40), 'BRITISH MUSLIM HERITAGE CENTRE', font=F(600, 22), fill=(190, 190, 190, 255), anchor='lm')
    d.text((W - 64, 40), f'{n} / 5', font=F(600, 22), fill=(190, 190, 190, 255), anchor='rm')
    a = np.asarray(im).astype(np.float32) / 255
    c[H - 100:H - 20] = c[H - 100:H - 20] * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]


# ------------------------------------------------------------------ slides
M = MAG
LINES = {
    1: [('I', WHITE), ('saved', WHITE), ('you', WHITE), ('a', WHITE), ('seat.', M)],
    2: [(w, WHITE) for w in 'Ever walked into a room where everyone already seems to know each other?'.split()],
    3: [(w, WHITE) for w in 'Then someone catches your eye.'.split()] + [('“Come', M), ('sit', M), ('with', M), ('us.”', M)],
    4: [(w, WHITE) for w in 'Next time,'.split()] + [('you’re', M), ('the', M), ('one', M)] + [(w, WHITE) for w in 'pulling out the chair.'.split()],
}
SIZES = {1: 104, 2: 70, 3: 76, 4: 80}
CLIP_START = {1: 0.5, 2: 4.0, 3: 8.0, 4: 11.0}


def story_slide(n):
    words = LINES[n]
    text = ' '.join(w for w, _ in words)
    ts, tend = schedule(text, 0.6, n)
    dur = tend + 2.2
    foot = Footage(CLIP_START[n])
    kb = keyboard_layer()

    def fn(t):
        c = dark(foot.at(t))
        al = kb[..., 3:4] * clamp(t / 0.4)
        c[:] = c * (1 - al * 0.85) + kb[..., :3] * al * 0.85
        k = sum(1 for x in ts if x <= t)
        for i, x in enumerate(ts):
            if 0 <= t - x < 0.35:
                key_pop(c, text[i], t - x)
        typed_text(c, words, k, t, SIZES[n])
        small_tag(c, n)
        bars(c)
        return c
    return dur, fn, ts


@functools.lru_cache(None)
def silk():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = (np.sin(xx / 140 + yy / 260 + np.sin(yy / 300) * 2.2) * 0.5 + 0.5) * 0.6 + (np.sin(xx / 60 - yy / 90 + np.sin(xx / 210) * 1.6) * 0.5 + 0.5) * 0.4
    v = cv2.GaussianBlur(v, (0, 0), 10)
    c = 0.86 + 0.13 * v
    return np.dstack([c * 0.995, c * 0.99, c]).astype(np.float32)


@functools.lru_cache(None)
def logo_colour(width=620):
    lc = np.asarray(Image.open(f'{ROOT}/workspace_bmhc/web/img/Website-1-2.png').convert('RGBA')).astype(np.float32) / 255
    sc = width / lc.shape[1]
    big = cv2.resize(lc, (width, int(lc.shape[0] * sc)), interpolation=cv2.INTER_CUBIC)
    bl = cv2.GaussianBlur(big, (0, 0), 1.0)
    return np.clip(big * 1.5 - bl * 0.5, 0, 1)


def end_slide():
    dur = 6.0

    def fn(t):
        c = silk().copy()
        drift = np.roll(c, int(t * 6), axis=1)
        c = c * 0.7 + drift * 0.3
        lg = logo_colour(560)
        paste(c, lg, W / 2, 300, clamp(t / 0.5))
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        a = int(255 * clamp((t - 0.3) / 0.5))
        d.text((W / 2, 610), 'Who saved', font=F(800, 108), fill=INK + (a,), anchor='mm')
        d.text((W / 2, 730), 'you a seat?', font=F(800, 108), fill=MAG + (a,), anchor='mm')
        a2 = int(255 * clamp((t - 0.9) / 0.5))
        d.text((W / 2, 880), 'Send this to the person', font=F(600, 46), fill=INK + (a2,), anchor='mm')
        d.text((W / 2, 940), 'who welcomed you.', font=F(600, 46), fill=INK + (a2,), anchor='mm')
        a3 = int(255 * clamp((t - 1.4) / 0.5))
        # instagram + web lines, as on the reference card
        y = 1090
        d.rounded_rectangle([W / 2 - 205, y - 22, W / 2 - 161, y + 22], 12, outline=INK + (a3,), width=4)
        d.ellipse([W / 2 - 194, y - 11, W / 2 - 172, y + 11], outline=INK + (a3,), width=4)
        d.text((W / 2 - 140, y), '@thebmhc', font=F(700, 40), fill=INK + (a3,), anchor='lm')
        y = 1160
        d.ellipse([W / 2 - 205, y - 22, W / 2 - 161, y + 22], outline=INK + (a3,), width=4)
        d.line([(W / 2 - 205, y), (W / 2 - 161, y)], fill=INK + (a3,), width=3)
        d.ellipse([W / 2 - 192, y - 22, W / 2 - 174, y + 22], outline=INK + (a3,), width=3)
        d.text((W / 2 - 140, y), 'bmhc.org.uk', font=F(700, 40), fill=INK + (a3,), anchor='lm')
        ov = np.asarray(im).astype(np.float32) / 255
        c = c * (1 - ov[..., 3:4]) + ov[..., :3] * ov[..., 3:4]
        bars(c, 16)
        return c
    return dur, fn, []


def tap(v=0.25):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(int(v * 1000))
    x = rng.normal(0, 1, n) * np.exp(-t * 160) * 0.6 + np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 220) * 0.4
    return x * v


def render(n):
    dur, fn, ts = end_slide() if n == 5 else story_slide(n)
    nf = int(dur * FPS)
    # soft key taps (the reference has keyboard sounds)
    aud = np.zeros(int(dur * SR) + SR)
    rng = np.random.default_rng(n)
    for x in ts:
        i = int(x * SR)
        tp = tap(rng.uniform(0.15, 0.28))
        aud[i:i + len(tp)] += tp
    aud = np.stack([aud, aud], 1)[:int(dur * SR)]
    apath = f'{S}/tap_{n}.wav'
    import soundfile as sf
    sf.write(apath, aud.astype(np.float32), SR)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', apath, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                          '-shortest', '-movflags', '+faststart', f'{OUT}/slide_{n}.mp4'], stdin=subprocess.PIPE)
    still_t = dur - 0.6
    for i in range(nf):
        t = i / FPS
        rgb = (np.clip(fn(t), 0, 1) * 255 + 0.5).astype(np.uint8)
        p.stdin.write(rgb.tobytes())
        if abs(t - still_t) < 0.5 / FPS:
            Image.fromarray(rgb).save(f'{OUT}/slide_{n}.jpg', quality=93)
    p.stdin.close()
    p.wait()
    print('slide', n, round(dur, 1), 's', flush=True)


if __name__ == '__main__':
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    for n in ns:
        render(n)
    ims = [Image.open(f'{OUT}/slide_{n}.jpg') for n in range(1, 6) if os.path.exists(f'{OUT}/slide_{n}.jpg')]
    if ims:
        sw = W // 3
        st = Image.new('RGB', (len(ims) * (sw + 10), H // 3), (40, 40, 40))
        for i, im in enumerate(ims):
            st.paste(im.resize((sw, H // 3)), (i * (sw + 10), 0))
        st.save(f'{OUT}/strip.jpg', quality=90)
