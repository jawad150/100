"""BMHC carousel "I saved you a seat." (Heart Work), five 1080x1350 slides, after the Pinterest reference: a kinetic word
drum on black - a list of words rolls past like a wheel, the word at the arrow sharp and bright, the rest curving away,
blurred and dim. Here in Heritage Magenta on BMHC ink, with Inter ExtraBold headlines, a 3D BMHC hall chair (red velvet,
gold frame) with the note on its seat, and real moments from BMHC's own film.

Each slide is exported as an MP4 (animated) and a JPG (still), plus a strip.
Usage: python3 carousel_seat.py [slide numbers]
"""
import os, sys, math, functools, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
S = f'{ROOT}/workspace_seat'
OUT = f'{S}/out'
os.makedirs(OUT, exist_ok=True)
VID = f'{ROOT}/workspace_ai/dl/bmhc-new.mp4'
FON = f'{ROOT}/workspace_sol/fonts'
W, H, FPS = 1080, 1350, 30
INK, MAG, TEAL, ORANGE, LIME, WHITE = (11, 11, 11), (230, 5, 133), (45, 200, 146), (255, 66, 0), (105, 255, 0), (255, 255, 255)
BARS = (MAG, TEAL, ORANGE, LIME)


@functools.lru_cache(None)
def F(w, s):
    return ImageFont.truetype(f'{FON}/Inter-{w}.ttf', int(s))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def e_out(u):
    return 1 - (1 - clamp(u)) ** 3


def e_inout(u):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def e_back(u, s=1.5):
    u = clamp(u) - 1
    return u * u * ((s + 1) * u + s) + 1


# ------------------------------------------------------------------ the word drum (after the reference)
@functools.lru_cache(maxsize=512)
def word_rgba(text, size, col, weight=800):
    f = F(weight, size)
    l, t, r, b = f.getbbox(text)
    im = Image.new('RGBA', (r - l + 40, b - t + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20 - l, 20 - t), text, font=f, fill=col + (255,))
    return np.asarray(im).astype(np.float32) / 255


def drum(items, pos, x0, cy, size=78, spacing=96, col=MAG, tilt=-9.0, arrow=True, dim=0.42, wrap=True, w=W, h=H):
    """Render the drum to an RGBA float layer. pos is the (fractional) index of the item at the arrow."""
    lay = np.zeros((h, w, 4), np.float32)
    R = spacing / 0.36
    n = len(items)
    for k in range(-6, 7):
        i = int(math.floor(pos)) + k
        if not wrap and (i < 0 or i >= n):
            continue
        d = i - pos
        th = d * 0.36
        if abs(th) >= math.pi / 2 * 0.98:
            continue
        txt = items[i % n]
        y = cy + R * math.sin(th)
        sc = 0.62 + 0.38 * math.cos(th)
        foc = clamp(1 - abs(d) * 1.6)
        al = (math.cos(th) ** 1.6) * (dim + (1 - dim) * foc)
        c = tuple(int(v * (0.55 + 0.45 * foc) + 255 * 0.0) for v in col)
        spr = word_rgba(txt, int(size * sc), c)
        bl = abs(d) * 2.6
        if bl > 0.3:
            spr = cv2.GaussianBlur(spr, (0, 0), bl)
        sh, sw = spr.shape[:2]
        yy0 = int(y - sh / 2)
        xx0 = int(x0 + (1 - sc) * 30 - 20)
        Y0, X0 = max(0, yy0), max(0, xx0)
        Y1, X1 = min(h, yy0 + sh), min(w, xx0 + sw)
        if Y1 <= Y0 or X1 <= X0:
            continue
        s = spr[Y0 - yy0:Y1 - yy0, X0 - xx0:X1 - xx0] * al
        reg = lay[Y0:Y1, X0:X1]
        reg[..., :3] = reg[..., :3] * (1 - s[..., 3:4]) + s[..., :3]
        reg[..., 3] = np.maximum(reg[..., 3], s[..., 3])
    if arrow:
        a = word_rgba('→', size, col)
        sh, sw = a.shape[:2]
        yy0, xx0 = int(cy - sh / 2), int(x0 - sw - 4)
        if xx0 >= 0:
            reg = lay[yy0:yy0 + sh, xx0:xx0 + sw]
            reg[..., :3] = reg[..., :3] * (1 - a[..., 3:4]) + a[..., :3]
            reg[..., 3] = np.maximum(reg[..., 3], a[..., 3])
    if tilt:
        M = cv2.getRotationMatrix2D((x0 + 200, cy), tilt, 1.0)
        lay = cv2.warpAffine(lay, M, (w, h), flags=cv2.INTER_LINEAR)
    return lay


def stepping(t, n_steps, step=0.62, hold_last=True):
    """Index that snaps from item to item like the reference (ease between)."""
    k = t / step
    i = math.floor(k)
    f = k - i
    p = i + e_inout(clamp((f - 0.55) / 0.45))
    if hold_last:
        p = min(p, n_steps)
    return p


# ------------------------------------------------------------------ helpers
def over(c, lay, a=1.0):
    al = lay[..., 3:4] * a
    c[:] = c * (1 - al) + lay[..., :3] * a
    return c


def canvas():
    c = np.zeros((H, W, 3), np.float32)
    c[:] = np.array(INK, np.float32) / 255
    rng = np.random.default_rng(3)
    return c


@functools.lru_cache(None)
def base_ink():
    c = canvas()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W * 0.6) / W, (yy - H * 0.45) / H)
    c += (np.exp(-(r / 0.5) ** 2) * 0.05)[..., None] * np.array((1, 0.5, 0.75), np.float32)
    return c


def text_block(c, lines, x, y, size, weight=800, col=WHITE, lead=1.12, a=1.0, maxw=None):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ln, colr in lines:
        d.text((x, y), ln, font=F(weight, size), fill=(colr or col) + (int(255 * a),))
        y += size * lead
    lay = np.asarray(im).astype(np.float32) / 255
    over(c, lay)
    return y


def wrap(text, size, weight, width):
    f = F(weight, size)
    out, cur = [], ''
    for w_ in text.split():
        t2 = (cur + ' ' + w_).strip()
        if f.getlength(t2) > width and cur:
            out.append(cur)
            cur = w_
        else:
            cur = t2
    out.append(cur)
    return out


def tag(c, label='HEART', x=60, y=60):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = F(700, 26)
    tw = f.getlength(label) + len(label) * 3
    d.rounded_rectangle([x, y, x + tw + 50, y + 54], 27, fill=MAG + (255,))
    xx = x + 25
    for ch in label:
        d.text((xx, y + 27), ch, font=f, fill=WHITE + (255,), anchor='lm')
        xx += f.getlength(ch) + 3
    d.text((W - 60, y + 27), 'BRITISH MUSLIM HERITAGE CENTRE', font=F(600, 22), fill=(200, 200, 200, 255), anchor='rm')
    over(c, np.asarray(im).astype(np.float32) / 255)


def bars(c, y=H - 16, h=16):
    for i, col in enumerate(BARS):
        c[y:y + h, int(W * i / 4):int(W * (i + 1) / 4)] = np.array(col, np.float32) / 255


@functools.lru_cache(None)
def asset(name, size):
    im = Image.open(f'{S}/assets/{name}.png').convert('RGBA')
    im = im.crop(im.getbbox())
    sc = size / max(im.size)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]
    return a


def paste(c, spr, cx, cy, a=1.0, shadow=True):
    sh, sw = spr.shape[:2]
    if shadow:
        m = cv2.GaussianBlur(spr[..., 3], (0, 0), 22) * 0.6
        _p(c, np.dstack([np.zeros((sh, sw, 3), np.float32), m]), cx + 10, cy + 26, a)
    _p(c, spr, cx, cy, a)


def _p(c, spr, cx, cy, a):
    sh, sw = spr.shape[:2]
    x0, y0 = int(cx - sw / 2), int(cy - sh / 2)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + sw), min(H, y0 + sh)
    if X1 <= X0 or Y1 <= Y0:
        return
    s = spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    al = s[..., 3:4] * a
    c[Y0:Y1, X0:X1] = c[Y0:Y1, X0:X1] * (1 - al) + s[..., :3] * a


class Footage:
    def __init__(self, start, fx, fy, z=1.0, speed=0.6):
        self.cap = cv2.VideoCapture(VID)
        self.cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.t = 0.0
        self.last = None
        self.fx, self.fy, self.z, self.speed = fx, fy, z, speed

    def at(self, t, w=W, h=H):
        tt = t * self.speed
        while self.last is None or self.t + 1 / self.fps <= tt + 1e-4:
            ok, f = self.cap.read()
            if not ok:
                break
            self.last = f
            self.t += 1 / self.fps
        img = self.last[..., ::-1].astype(np.float32) / 255
        ih, iw = img.shape[:2]
        s = max(w / iw, h / ih) * (self.z + 0.03 * t)
        cx = clamp(self.fx * iw, w / 2 / s, iw - w / 2 / s)
        cy = clamp(self.fy * ih, h / 2 / s, ih - h / 2 / s)
        M = np.array([[s, 0, w / 2 - s * cx], [0, s, h / 2 - s * cy]], np.float32)
        return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def darken(img, top=0.15, bottom=0.88, amt=0.75):
    yy = np.linspace(0, 1, img.shape[0], dtype=np.float32)[:, None, None]
    g = np.clip((yy - top) / (bottom - top), 0, 1)
    shade = 1 - amt * (1 - np.abs(g * 2 - 1) ** 1.5 * 0 - 0.0) * 0
    lum = img.mean(-1, keepdims=True)
    img = lum + (img - lum) * 0.85
    vign = 0.35 + 0.65 * (1 - np.clip(np.abs(yy - 0.5) * 2, 0, 1)) ** 0.5
    return np.clip(img * 0.62 * vign, 0, 1)


# ------------------------------------------------------------------ slides
GREET = ['Salaam', 'Welcome', 'Hello', 'Over here', 'Tea?', 'Sit with us']
CHAT = ['Salaam, Aunty', 'How’s your mum?', 'Long time', 'Same table?', 'Did you bring dates?', 'There he is', 'Budge up']
INVITE = ['…', 'Excuse me?', 'Hi', '“Come sit with us.”']
ROLES = ['Newcomer', 'Guest', 'Regular', 'Friend', 'The one who saves a seat']
WHO = ['A neighbour', 'An aunty', 'A volunteer', 'A stranger', 'A friend', 'Someone at BMHC']


def s1(t):
    c = base_ink().copy()
    tag(c)
    text_block(c, [('I SAVED', None), ('YOU A SEAT.', MAG)], 60, 150, 104, 800, WHITE, 1.02)
    # the chair is pulled out
    u = e_out(clamp((t - 0.2) / 1.1))
    ch = asset('chair_note', 760)
    paste(c, ch, 640 + 150 * (1 - u), 860 - 40 * (1 - u), clamp(t / 0.3))
    lay = drum(GREET, stepping(max(0, t - 0.4), 99, 0.62, False) % len(GREET), 120, 1170, 58, 74, MAG, tilt=-8)
    over(c, lay)
    bars(c)
    return c


FOOT = {}


def s2(t):
    c = darken(FOOT[2].at(t))
    tag(c)
    lines = wrap('Ever walked into a room where everyone already seems to know each other?', 74, 800, 940)
    text_block(c, [(l, None) for l in lines], 60, 150, 74, 800, WHITE, 1.1, a=clamp(t / 0.5))
    lay = drum(CHAT, (t / 0.5) % len(CHAT), 160, 1020, 56, 74, MAG, tilt=-8, dim=0.6, arrow=False)
    over(c, lay, 0.95)
    bars(c)
    return c


def s3(t):
    c = darken(FOOT[3].at(t))
    tag(c)
    text_block(c, [('Then someone', None), ('catches your eye.', None)], 60, 150, 74, 800, WHITE, 1.1, a=clamp(t / 0.5))
    p = stepping(max(0, t - 0.5), len(INVITE) - 1, 0.75, True)
    lay = drum(INVITE, p, 130, 1040, 70, 92, MAG, tilt=-8, wrap=False)
    over(c, lay)
    bars(c)
    return c


def s4(t):
    c = base_ink().copy()
    tag(c)
    text_block(c, [('Next time, you’re', None), ('the one pulling', None), ('out the chair.', MAG)], 60, 150, 80, 800, WHITE, 1.08,
               a=clamp(t / 0.5))
    u = e_out(clamp((t - 0.2) / 1.1))
    ch = asset('chair_back', 640)
    paste(c, ch, 770 - 160 * (1 - u), 840, clamp(t / 0.3))
    p = stepping(max(0, t - 0.5), len(ROLES) - 1, 0.7, True)
    lay = drum(ROLES, p, 120, 1170, 58, 74, MAG, tilt=-8, wrap=False)
    over(c, lay)
    bars(c)
    return c


@functools.lru_cache(None)
def logo_rgba(width=520):
    IMG = f'{ROOT}/workspace_bmhc/web/img'
    lw = np.asarray(Image.open(f'{IMG}/bmhc-white-logo.png').convert('RGBA')).astype(np.float32) / 255
    lc = np.asarray(Image.open(f'{IMG}/Website-1-2.png').convert('RGBA')).astype(np.float32) / 255
    h = lw.shape[0]
    cut = int(h * 0.86)
    out = lw.copy()
    out[cut:] = lc[cut:]
    sc = width / out.shape[1]
    big = cv2.resize(out, (width, int(out.shape[0] * sc)), interpolation=cv2.INTER_CUBIC)
    bl = cv2.GaussianBlur(big, (0, 0), 1.0)
    big = np.clip(big * 1.5 - bl * 0.5, 0, 1)
    big[..., :3] *= big[..., 3:4]
    return big


def s5(t):
    c = darken(FOOT[5].at(t))
    tag(c)
    text_block(c, [('Who saved', None), ('you a seat?', MAG)], 60, 150, 110, 800, WHITE, 1.02, a=clamp(t / 0.5))
    lay = drum(WHO, stepping(max(0, t - 0.3), 99, 0.6, False) % len(WHO), 130, 900, 62, 80, MAG, tilt=-8)
    over(c, lay)
    a = clamp((t - 0.8) / 0.5)
    text_block(c, [('Send this to the person', None), ('who welcomed you.', None)], 60, 1100, 48, 700, WHITE, 1.2, a=a)
    lg = logo_rgba(400)
    _p(c, lg, W - 60 - lg.shape[1] / 2, 1250 - lg.shape[0] / 2 + 10, a)
    bars(c)
    return c


SLIDES = {1: (6.0, s1), 2: (6.0, s2), 3: (6.0, s3), 4: (6.0, s4), 5: (7.0, s5)}
STILL_T = {1: 3.05, 2: 2.0, 3: 5.5, 4: 5.5, 5: 6.5}
# BMHC's own film: the iftar (group at the tables), the volunteer turning to the lens, a conversation at the exhibition
FOOT_SRC = {2: (17.0, 0.55, 0.45, 1.05, 0.5), 3: (11.05, 0.66, 0.42, 1.0, 0.12), 5: (28.0, 0.33, 0.42, 1.05, 0.15)}


def render(n):
    dur, fn = SLIDES[n]
    if n in FOOT_SRC:
        FOOT[n] = Footage(*FOOT_SRC[n])
    nf = int(dur * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                          f'{OUT}/slide_{n}.mp4'], stdin=subprocess.PIPE)
    for i in range(nf):
        t = i / FPS
        c = fn(t)
        rgb = (np.clip(c, 0, 1) * 255 + 0.5).astype(np.uint8)
        p.stdin.write(rgb.tobytes())
        if abs(t - STILL_T[n]) < 0.5 / FPS:
            Image.fromarray(rgb).save(f'{OUT}/slide_{n}.jpg', quality=93)
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
        st = Image.new('RGB', (len(ims) * (sw + 10), H // 3), (40, 40, 40))
        for i, im in enumerate(ims):
            st.paste(im.resize((sw, H // 3)), (i * (sw + 10), 0))
        st.save(f'{OUT}/strip.jpg', quality=90)
