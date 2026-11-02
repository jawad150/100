"""Textures for the Family Book scene: print photos, handwritten pages, notes, cover label, oak and linen."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = '/home/user/100/workspace_fb'
FONTS = '/home/user/100/workspace_sol/fonts'
C = f'{S}/clips'
INK = (52, 44, 92)
ORANGE = (232, 86, 18)


def grab(cid, frac, cx, cy, ar, out_w):
    cap = cv2.VideoCapture(f'{C}/{cid}.mp4'); cap.set(1, int(cap.get(7) * frac)); ok, im = cap.read()
    h, w = im.shape[:2]
    ch = h; cw = int(ch * ar)
    if cw > w:
        cw = w; ch = int(cw / ar)
    x0 = int(np.clip(cx * w - cw / 2, 0, w - cw)); y0 = int(np.clip(cy * h - ch / 2, 0, h - ch))
    im = im[y0:y0 + ch, x0:x0 + cw]
    im = cv2.resize(im, (out_w, int(out_w / ar)), interpolation=cv2.INTER_AREA)
    # print look: slightly warm, lifted blacks, a hint of grain
    f = im.astype(np.float32) / 255
    f = f * 0.92 + 0.05
    f[..., 2] *= 1.03; f[..., 0] *= 0.97
    f += np.random.default_rng(cid % 97).normal(0, 0.012, f.shape[:2])[..., None]
    im = (np.clip(f, 0, 1) * 255).astype(np.uint8)
    b = 26
    out = cv2.copyMakeBorder(im, b, b, b, b, cv2.BORDER_CONSTANT, value=(246, 249, 250))
    cv2.imwrite(f'{S}/tex/print_{cid}.png', out)
    return out.shape[1], out.shape[0]


sizes = {}
sizes['dog'] = grab(1552, 0.5, 0.45, 0.45, 1.0, 600)
sizes['room'] = grab(3111, 0.5, 0.32, 0.62, 1.25, 700)
sizes['kitchen'] = grab(34685, 0.5, 0.5, 0.55, 1.25, 700)
sizes['park'] = grab(19488, 0.5, 0.4, 0.5, 1.33, 700)
sizes['pizza'] = grab(44001, 0.5, 0.5, 0.5, 1.0, 500)
print(sizes)


def font(name, size):
    return ImageFont.truetype(f'{FONTS}/{name}.ttf', size)


def paper(w, h, base=(250, 246, 236), seed=1):
    rng = np.random.default_rng(seed)
    a = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.2) * 3.0
    fib = cv2.GaussianBlur(rng.normal(0, 1, (h // 4, w // 4)).astype(np.float32), (0, 0), 2)
    a += n[..., None] + cv2.resize(fib, (w, h))[..., None] * 2.5
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


hand = lambda s: font('Caveat-700', s)
# left page: Hello! This is us. + small labels area for the kitchen print
W, H = 1400, 1900
left = paper(W, H, seed=2); d = ImageDraw.Draw(left)
d.text((150, 230), 'Hello!', font=hand(230), fill=INK)
d.text((150, 470), 'This is us.', font=hand(170), fill=INK)
# little drawn heart
hx, hy = 1080, 380
pts = [(hx + 60 * 16 * math.sin(t) ** 3 / 16, hy - 60 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in np.linspace(0, 2 * math.pi, 80)]
d.line(pts + [pts[0]], fill=ORANGE, width=10, joint='curve')
d.text((230, 1800), 'Our kitchen table', font=hand(74), fill=INK)
left.save(f'{S}/tex/page_left.png')
# right page: labels under the prints
right = paper(W, H, seed=3); d = ImageDraw.Draw(right)
d.text((120, 925), 'Your room', font=hand(96), fill=ORANGE)
d.text((1010, 830), 'Biscuit, our dog', font=hand(66), fill=INK, anchor='ma')
d.text((210, 1820), 'The park down our road', font=hand(64), fill=INK)
right.save(f'{S}/tex/page_right.png')
# pizza note card
note = paper(700, 460, base=(255, 244, 196), seed=4); d = ImageDraw.Draw(note)
d.text((350, 170), 'Friday tea =', font=hand(110), fill=INK, anchor='mm')
d.text((350, 320), 'pizza night!', font=hand(120), fill=ORANGE, anchor='mm')
note.save(f'{S}/tex/note_pizza.png')
# cover label for the closed book
lab = paper(900, 520, base=(236, 214, 178), seed=5); d = ImageDraw.Draw(lab)
d.rectangle([24, 24, 876, 496], outline=(150, 115, 80), width=4)
d.text((450, 200), 'Hello!', font=hand(180), fill=INK, anchor='mm')
d.text((450, 370), 'This is us.', font=hand(130), fill=INK, anchor='mm')
lab.save(f'{S}/tex/cover_label.png')
# oak table texture (procedural grain)
rng = np.random.default_rng(9)
TW, TH = 2400, 3000
yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
warp = cv2.resize(cv2.GaussianBlur(rng.normal(0, 1, (TH // 50, TW // 50)).astype(np.float32), (0, 0), 2), (TW, TH)) * 60
rings = np.sin((xx + warp) * 0.22 + np.sin(yy * 0.006) * 5) * 0.5 + 0.5
fine = cv2.GaussianBlur(rng.normal(0, 1, (TH, TW)).astype(np.float32), (1, 41), 0) * 0.5
plank = ((xx // 600) % 2) * 0.04
v = 0.84 + 0.06 * rings ** 3 + 0.05 * fine - plank * 0.6
base = np.array([214, 178, 128], np.float32) / 255
oak = np.clip(v[..., None] * base[::-1] * 1.18, 0, 1)
for k in range(1, 4):
    oak[:, k * 600 - 3:k * 600 + 3] *= 0.75
cv2.imwrite(f'{S}/tex/oak.png', (oak * 255).astype(np.uint8))
# linen texture
LW, LH = 2400, 1200
lin = np.ones((LH, LW), np.float32) * 0.93
wx = np.sin(np.arange(LW) * 1.6)[None, :] * 0.02 + rng.normal(0, 0.02, (1, LW))
wy = np.sin(np.arange(LH) * 1.6)[:, None] * 0.02 + rng.normal(0, 0.02, (LH, 1))
lin = lin + wx + wy + cv2.GaussianBlur(rng.normal(0, 1, (LH, LW)).astype(np.float32), (0, 0), 0.8) * 0.015
linen = np.clip(lin[..., None] * np.array([214, 233, 240], np.float32) / 255 * 1.02, 0, 1)
cv2.imwrite(f'{S}/tex/linen.png', (linen * 255).astype(np.uint8))
sage = np.clip(lin[..., None] * np.array([118, 150, 134], np.float32) / 255, 0, 1)
cv2.imwrite(f'{S}/tex/sage_linen.png', (sage * 255).astype(np.uint8))
print('ok')
