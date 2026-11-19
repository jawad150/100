# /// script
# dependencies = ["numpy", "opencv-python-headless", "pillow"]
# ///
"""RKN ad, clean 4K rebuild: AI-upscaled photo + every piece of text redrawn as crisp type.

  uv run ad2/compose.py ad2/original.png ad2/up4x.png ad2/RKN_ad_4K.png

Coordinates below are measured on the 1122x1402 original and scaled by S. Old AI lettering is removed
(dark-pixel mask + fill from the surrounding wall / paper / floor) and redrawn in EB Garamond and Inter.
"""
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ORIG, UP, OUT = sys.argv[1:4]
FONTS = sys.argv[4] if len(sys.argv) > 4 else '.'
S = 3
INTER = '/usr/share/fonts/opentype/inter/'
f_inter = lambda w, px: ImageFont.truetype(INTER + {'light': 'Inter-Light.otf', 'reg': 'Inter-Regular.otf', 'med': 'Inter-Medium.otf',
    'semi': 'Inter-SemiBold.otf', 'bold': 'Inter-Bold.otf', 'xbold': 'InterDisplay-ExtraBold.otf'}[w], int(round(px)))
f_ebg = lambda name, px: ImageFont.truetype(f'{FONTS}/{name}', int(round(px)))
rng = np.random.default_rng(3)

orig = np.asarray(Image.open(ORIG).convert('RGB')).astype(np.float32)
H0, W0 = orig.shape[:2]
W, H = W0 * S, H0 * S
up = np.asarray(Image.open(UP).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
lanc = np.asarray(Image.open(ORIG).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
# AI upscale alone looks painted; blend it with a plain upscale of the photo (more so on the person)
person = np.zeros((H, W), np.float32)
cv2.fillPoly(person, [np.array([[x * S, y * S] for x, y in [(845, 325), (1015, 325), (1110, 520), (1122, 700), (690, 700), (690, 630), (850, 600)]], np.int32)], 1)
person = cv2.GaussianBlur(person, (0, 0), 12 * S)
wa = (0.62 - 0.27 * person)[..., None]
img = up * wa + lanc * (1 - wa)
img = img + (lanc - cv2.GaussianBlur(lanc, (0, 0), 1.0 * S)) * 0.35 * person[..., None]   # keep the photo's own fine detail
P = lambda pts: np.array([[x * S, y * S] for x, y in pts], np.int32)

def lum(a): return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114

# ------------------------------------------------------------------ 1. remove the old lettering
def norm_fill(a, mask, sigma):
    keep = (1 - mask)[..., None]
    num = cv2.GaussianBlur(a * keep, (0, 0), sigma)
    den = cv2.GaussianBlur(1 - mask, (0, 0), sigma)[..., None]
    return num / np.maximum(den, 1e-4)

def dark_mask(region_pts, thresh, bg_sigma, dil, exclude=()):
    reg = np.zeros((H, W), np.uint8); cv2.fillPoly(reg, [P(region_pts)], 1)
    for (cx, cy, r) in exclude: cv2.circle(reg, (cx * S, cy * S), r * S, 0, -1)
    L = lum(img)
    bg = cv2.dilate(L, np.ones((9 * S, 9 * S), np.uint8))           # local paper / wall brightness
    bg = cv2.GaussianBlur(bg, (0, 0), 3 * S)
    m = ((bg - L) > thresh).astype(np.uint8) * reg
    m = cv2.dilate(m, np.ones((dil, dil), np.uint8))
    return m.astype(np.float32)

def fill_smooth(m, sigma, grain=1.6):
    global img
    f = norm_fill(img, m, sigma)
    f = f + rng.standard_normal((H, W, 1)).astype(np.float32) * grain
    mm = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]
    img = img * (1 - mm) + f * mm

def fill_inpaint(m, radius):
    global img
    u8 = np.clip(img, 0, 255).astype(np.uint8)
    out = cv2.inpaint(u8, (m > 0).astype(np.uint8), radius, cv2.INPAINT_TELEA).astype(np.float32)
    out = out + rng.standard_normal((H, W, 1)).astype(np.float32) * 2.0 * (m[..., None] > 0)
    mm = cv2.GaussianBlur(m, (0, 0), 1.0)[..., None]
    img = img * (1 - mm) + out * mm

# header (logo, headline, sub-line) on the plain wall
def fill_surface(region_pts, thresh, dil):
    # the wall behind the header is a smooth gradient: fit a quadratic surface to the clean wall pixels
    # around the lettering and replace the lettering with it (no smudges, no ghost strokes)
    global img
    m = dark_mask(region_pts, thresh, 6, dil)
    reg = np.zeros((H, W), np.uint8); cv2.fillPoly(reg, [P(region_pts)], 1)
    ring = cv2.dilate(reg, np.ones((24 * S, 24 * S), np.uint8))
    ys, xs = np.where((ring > 0) & (m == 0))
    sel = rng.choice(len(xs), size=min(len(xs), 60000), replace=False); ys, xs = ys[sel], xs[sel]
    def basis(x, y):
        x = x / W; y = y / H
        return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y, x ** 3, y ** 3, x * x * y, x * y * y], 1)
    A = basis(xs.astype(np.float64), ys.astype(np.float64))
    coef = [np.linalg.lstsq(A, img[ys, xs, c], rcond=None)[0] for c in range(3)]
    # replace the whole block (feathered), so no letter-shaped seams remain
    blk = cv2.dilate(np.maximum(reg.astype(np.float32), m), np.ones((4 * S, 4 * S), np.uint8))
    my, mx = np.where(blk > 0)
    B = basis(mx.astype(np.float64), my.astype(np.float64))
    surf = img.copy()
    for c in range(3): surf[my, mx, c] = B @ coef[c]
    surf[my, mx] += rng.standard_normal((len(my), 1)).astype(np.float32) * 1.4
    mm = np.clip(cv2.GaussianBlur(blk, (0, 0), 5 * S) * 1.6, 0, 1)
    mm = np.maximum(mm, cv2.GaussianBlur(m, (0, 0), 1.0))[..., None]
    img = img * (1 - mm) + surf * mm

for box, dil in [([(128, 40), (600, 40), (600, 142), (128, 142)], 9), ([(128, 182), (898, 182), (898, 296), (850, 326), (128, 340)], 9),
                 ([(128, 340), (775, 340), (775, 392), (128, 392)], 8)]:
    m = dark_mask(box, 6, 6, dil * S)
    f = norm_fill(img, m, 14 * S)
    f = f + cv2.GaussianBlur(rng.standard_normal((H, W, 1)).astype(np.float32), (0, 0), 0.6)[..., None] * 1.8 if False else f
    n = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.6)
    f = f + n[..., None] * 2.0
    mm = np.clip(cv2.GaussianBlur(m, (0, 0), 3 * S) * 1.4, 0, 1)[..., None]
    img = img * (1 - mm) + f * mm
# the ledger on the paper (text + grid lines; the grey header band and the gold pins stay)
LEDGER = [(532, 708), (862, 708), (874, 790), (866, 1000), (845, 1100), (800, 1165), (345, 1138), (420, 1000), (478, 880), (515, 790)]
fill_smooth(dark_mask(LEDGER, 30, 4, 4 * S, exclude=[(887, 760, 15), (874, 921, 15), (859, 1041, 15)]), 4 * S, grain=1.2)
band_old = np.zeros((H, W), np.uint8); cv2.fillPoly(band_old, [P([(476, 792), (880, 794), (880, 845), (474, 843)])], 1)
fill_smooth(band_old.astype(np.float32), 10 * S, grain=1.0)
title_old = np.zeros((H, W), np.uint8); cv2.fillPoly(title_old, [P([(552, 716), (856, 716), (856, 786), (528, 786)])], 1)
fill_smooth(title_old.astype(np.float32), 10 * S, grain=1.0)
# URL on the floor, plaque on the brass: inpaint (textured surfaces)
fill_inpaint(dark_mask([(660, 1312), (1090, 1312), (1090, 1362), (660, 1362)], 40, 4, 5 * S), 7)
fill_inpaint(dark_mask([(143, 1290), (268, 1300), (266, 1332), (141, 1320)], 35, 3, 3 * S), 5)

# ------------------------------------------------------------------ 2. realism: skin texture on face + hands, film grain
def skin_texture(region_pts, amount=2.2):
    global img
    reg = np.zeros((H, W), np.float32); cv2.fillPoly(reg, [P(region_pts)], 1)
    ycc = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2YCrCb).astype(np.float32)
    Y, Cr, Cb = ycc[..., 0], ycc[..., 1], ycc[..., 2]
    skin = ((Cr > 138) & (Cr < 178) & (Cb > 85) & (Cb < 126) & (Y > 55) & (Y < 230)).astype(np.float32)
    m = cv2.GaussianBlur(skin * reg, (0, 0), 1.5 * S)
    def band(sig):
        n = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), sig); return n / (n.std() + 1e-6)
    tex = band(0.5 * S) * 1.0 + band(1.0 * S) * 0.7
    dots = (rng.random((H, W)) > 0.996).astype(np.float32); dots = cv2.GaussianBlur(dots, (0, 0), 0.6 * S); dots /= dots.max() + 1e-6
    img = img + (tex[..., None] * amount - dots[..., None] * 9) * m[..., None]
    # micro-contrast: knuckles, brows, lashes, stubble
    det = img - cv2.GaussianBlur(img, (0, 0), 1.2 * S)
    img = img + det * 0.5 * cv2.GaussianBlur(reg, (0, 0), 4 * S)[..., None]

skin_texture([(862, 338), (1005, 338), (1010, 470), (975, 515), (900, 512), (868, 470)])          # face + neck
skin_texture([(700, 640), (840, 640), (842, 694), (700, 694)], amount=1.8)                        # hands on the keyboard
# gentle clarity + one even film grain over the whole photograph (before any type is drawn)
blur = cv2.GaussianBlur(img, (0, 0), 6 * S)
img = img + (img - blur) * 0.12
g = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.55)
img = img + g[..., None] * 2.6
canvas = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

# ------------------------------------------------------------------ 3. crisp type
draw = ImageDraw.Draw(canvas)
def fit(font_fn, text, width_px, lo=10, hi=600):
    # font size whose advance width is width_px (binary search)
    for _ in range(30):
        mid = (lo + hi) / 2
        if font_fn(mid).getlength(text) > width_px: hi = mid
        else: lo = mid
    return font_fn(lo)
def put(text, font_fn, x0, x1, base, color, anchor='ls'):
    f = fit(font_fn, text, (x1 - x0) * S)
    draw.text((x0 * S, base * S), text, font=f, fill=color, anchor=anchor)

BRONZE_INK, NEAR_BLACK = (110, 74, 22), (17, 17, 17)
# logo: the real monogram (solid bronze, the light-background variant) + wordmark
mono = Image.open(f'{FONTS}/monogram.png').convert('RGBA')
a = mono.split()[3]
grad = np.zeros((mono.height, mono.width, 3), np.float32)
t = np.linspace(0, 1, mono.height)[:, None]
for c, (c0, c1) in enumerate([(150, 112), (104, 78), (36, 26)]):
    grad[..., c] = c0 * (1 - t) + c1 * t
monoB = Image.fromarray(grad.astype(np.uint8)); monoB.putalpha(a)
mh = (130 - 50) * S
monoB = monoB.resize((int(mono.width * mh / mono.height), mh), Image.LANCZOS)
canvas.paste(monoB, (141 * S, 50 * S), monoB)
put('RKN', lambda s: f_inter('bold', s), 226, 306, 102, BRONZE_INK)
put('ACCOUNTANCY', lambda s: f_inter('light', s), 317, 575, 102, BRONZE_INK)
# headline + sub-line
put('Your paperwork shouldn’t', lambda s: f_inter('xbold', s), 141, 884, 246, NEAR_BLACK)
put('outgrow your business.', lambda s: f_ebg('ebg-italic-600.ttf', s), 140, 829, 306, (112, 76, 20))
put('Digital bookkeeping. Personal support.', lambda s: f_inter('reg', s), 141, 757, 376, (24, 24, 24))

# button: a fresh gold pill, crisp label
bx0, by0, bx1, by1 = 725 * S, 1238 * S, 1080 * S, 1311 * S
sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((bx0 + 6, by0 + 18, bx1 - 6, by1 + 14), radius=(by1 - by0) // 2, fill=120)
sh = sh.filter(ImageFilter.GaussianBlur(14))
canvas.paste(Image.new('RGB', (W, H), (60, 45, 25)), (0, 0), sh)
pill = np.zeros((by1 - by0, bx1 - bx0, 3), np.float32)
tt = np.linspace(0, 1, by1 - by0)[:, None, None]
pill[...] = np.array([252, 214, 110]) * (1 - tt) ** 1.4 + np.array([214, 156, 40]) * (1 - (1 - tt) ** 1.4)
hl = np.clip(1 - np.abs(tt - 0.12) / 0.12, 0, 1) * 30; pill += hl
pill_img = Image.fromarray(np.clip(pill, 0, 255).astype(np.uint8))
pm = Image.new('L', pill_img.size, 0); ImageDraw.Draw(pm).rounded_rectangle((0, 0, pill_img.width - 1, pill_img.height - 1), radius=pill_img.height // 2, fill=255)
canvas.paste(pill_img, (bx0, by0), pm)
draw = ImageDraw.Draw(canvas)
draw.rounded_rectangle((bx0, by0, bx1, by1), radius=(by1 - by0) // 2, outline=(176, 120, 30), width=3)
put('Enquire now', lambda s: f_inter('bold', s), 781, 1032, 1286, NEAR_BLACK)
put('rknaccountancy.co.uk', lambda s: f_inter('semi', s), 668, 1078, 1348, NEAR_BLACK)

# ------------------------------------------------------------------ 4. the ledger, in perspective on the paper
# homography: flat table (u 0..1000, v 0..900) -> original-image coords (measured grid corners + column lines)
src_pts = np.float32([[0, 0], [440, 0], [700, 0], [1000, 0], [0, 900], [440, 900], [700, 900], [1000, 900]])
dst_pts = np.float32([[488, 800], [658, 800], [771, 800], [872, 804], [358, 1121], [573, 1140], [699, 1146], [800, 1155]])
Hm, _ = cv2.findHomography(src_pts, dst_pts)
Hinv = np.linalg.inv(Hm)
def to_flat(x, y):
    p = Hinv @ np.array([x, y, 1.0]); return p[:2] / p[2]
FS = 4                                                     # flat canvas pixels per flat unit
V0 = -320                                                  # flat canvas starts above the table (title)
U0 = -150
fw, fh = 1350 * FS, (900 - V0) * FS
flat = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
fd = ImageDraw.Draw(flat)
def fl(u, v): return ((u - U0) * FS, (v - V0) * FS)
INK = (24, 24, 26, 255)
def ltext(text, fontname, xl, yl, xr, yr, color=INK, extra=1.0):
    (ul, vl), (ur, vr) = to_flat(xl, yl), to_flat(xr, yr)
    v = (vl + vr) / 2
    f = fit(lambda s: f_ebg(fontname, s), text, (ur - ul) * FS * extra)
    fd.text(fl(ul, v), text, font=f, fill=color, anchor='ls')
band = [to_flat(486, 801), to_flat(872, 803), to_flat(872, 838), to_flat(484, 836)]
fd.polygon([fl(u, v) for u, v in band], fill=(226, 222, 215, 255))
ltext('Description', 'ebg-italic-600.ttf', 503, 820, 593, 821)
ltext('Money in', 'ebg-italic-600.ttf', 676, 822, 751, 824)
ltext('Money out', 'ebg-italic-600.ttf', 780, 826, 859, 828)
ROWS = [
    ('Sales invoices', 485, 867, 616, 869, '£12,450.00', 660, 870, 755, 871, '£25.00', 802, 873, 863, 874),
    ('Supplier bills', 469, 921, 601, 925, '£85.00', 681, 925, 744, 926, '£3,280.00', 769, 930, 855, 931),
    ('Business', 456, 970, 546, 972, '£125.00', 658, 985, 735, 987, '£780.50', 774, 990, 851, 992),
    ('Payroll', 428, 1041, 508, 1045, '£40.00', 650, 1050, 716, 1052, '£6,750.00', 740, 1055, 837, 1058),
    ('VAT records', 398, 1111, 545, 1117, '£1,260.00', 607, 1117, 701, 1120, '£95.00', 753, 1120, 818, 1122),
]
for r in ROWS:
    ltext(r[0], 'ebg-italic-700.ttf', *r[1:5])
    ltext(r[5], 'ebg-italic-600.ttf', *r[6:10])
    ltext(r[10], 'ebg-italic-600.ttf', *r[11:15])
ltext('expenses', 'ebg-italic-700.ttf', 448, 994, 550, 996)
# grid: column rules and row rules (flat space, so they follow the paper)
LINE = (118, 132, 142, 235)
def col_line(gaps):          # gaps: image points midway between two columns, one per row -> least-squares line in flat space
    pts = np.array([to_flat(x, y) for x, y in gaps])
    k, c = np.polyfit(pts[:, 1], pts[:, 0], 1)          # u = k v + c
    fd.line([fl(c + k * -5, -5), fl(c + k * 905, 905)], fill=LINE, width=int(1.1 * FS))
mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
col_line([mid((593, 821), (676, 822)), mid((616, 869), (660, 870)), mid((601, 925), (681, 925)), mid((546, 972), (658, 985)),
          mid((508, 1045), (650, 1050)), mid((545, 1117), (607, 1117))])
col_line([mid((751, 824), (780, 826)), mid((755, 871), (802, 873)), mid((744, 926), (769, 930)), mid((735, 987), (774, 990)),
          mid((716, 1052), (740, 1055)), mid((701, 1120), (753, 1120))])
# warp flat -> final image (S-scaled original coords)
Tflat = np.array([[1 / FS, 0, U0], [0, 1 / FS, V0], [0, 0, 1]])            # flat canvas px -> (u, v)
Sm = np.diag([S, S, 1.0])
M = Sm @ Hm @ Tflat
warped = cv2.warpPerspective(np.asarray(flat), M, (W, H), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
wimg = Image.fromarray(warped, 'RGBA')
# printed ink, not stickers: multiply onto the paper so its shading shows through
base = np.asarray(canvas).astype(np.float32)
wa = warped[..., 3:4].astype(np.float32) / 255
ink = warped[..., :3].astype(np.float32)
base = base * (1 - wa) + (base * ink / 255) * wa * 0.25 + ink * wa * 0.75
canvas = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

# title block: perfectly level, crisp
draw = ImageDraw.Draw(canvas)
cx = 700 * S
ft = fit(lambda s: f_ebg('ebg-600.ttf', s), 'BOOKKEEPING', (838 - 566) * S)
draw.text((cx, 744 * S), 'BOOKKEEPING', font=ft, fill=(22, 22, 24), anchor='ms')
fs2 = fit(lambda s: f_ebg('ebg-italic-600.ttf', s), 'Business records', (762 - 612) * S)
draw.text((cx, 777 * S), 'Business records', font=fs2, fill=(40, 40, 42), anchor='ms')
tw = fs2.getlength('Business records') / 2
yr = int(771 * S)
for (a, b) in [(cx - tw - 26 * S - 68 * S, cx - tw - 12 * S), (cx + tw + 12 * S, cx + tw + 26 * S + 68 * S)]:
    draw.rectangle((a, yr - 3, b, yr + 3), fill=(166, 114, 38))

# ------------------------------------------------------------------ 5. brass plaque, engraved
pl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
f = fit(lambda s: f_ebg('ebg-600.ttf', s), 'ACCOUNTS', (262 - 148) * S)
angle = np.degrees(np.arctan2(1322 - 1306, 262 - 148))
txt = Image.new('RGBA', (int(f.getlength('ACCOUNTS')) + 40, int(f.size * 1.6)), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)
td.text((20, f.size * 1.2 + 3), 'ACCOUNTS', font=f, fill=(255, 226, 150, 150), anchor='ls')     # engraved lip highlight
td.text((20, f.size * 1.2), 'ACCOUNTS', font=f, fill=(34, 24, 10, 255), anchor='ls')
txt = txt.rotate(-angle, resample=Image.BICUBIC, expand=True)
canvas.paste(txt, (int(148 * S - 20), int(1306 * S - f.size * 1.2 - 4)), txt)

# ------------------------------------------------------------------ 6. eyes lowered to the keyboard (lids closed down)
a = np.asarray(canvas).copy()
af = a.astype(np.float32)
Lm = lum(af)
def poly(pts): return np.array(pts, np.int32)
# near eye: the opening (white + iris) becomes lid skin
m1 = np.zeros(a.shape[:2], np.uint8)
cv2.fillPoly(m1, [poly([(2681, 1301), (2690, 1294), (2706, 1291), (2724, 1292), (2739, 1297), (2731, 1306), (2712, 1311), (2692, 1308)])], 255)
m1 = cv2.dilate(m1, np.ones((3, 3), np.uint8))
# far eye (profile edge): remove only the dark lash / iris pixels; neighbours decide wall or skin
reg = np.zeros(a.shape[:2], np.uint8); cv2.fillPoly(reg, [poly([(2596, 1284), (2646, 1292), (2650, 1324), (2610, 1324), (2596, 1300)])], 1)
m2 = (((Lm < 120) & (reg > 0)).astype(np.uint8) * 255)
m2 = cv2.dilate(m2, np.ones((5, 5), np.uint8))
a = cv2.inpaint(a, m1, 7, cv2.INPAINT_TELEA)
a = cv2.inpaint(a, m2, 4, cv2.INPAINT_TELEA)
af = a.astype(np.float32)
# eyelid shading: slightly deeper, warmer skin toward the lash line, plus skin grain
lid = np.zeros(a.shape[:2], np.float32)
cv2.fillPoly(lid, [poly([(2683, 1300), (2692, 1292), (2708, 1289), (2726, 1290), (2740, 1296), (2731, 1305), (2712, 1309), (2692, 1306)])], 1)
lid = cv2.GaussianBlur(lid, (0, 0), 2.2)
yy = np.arange(a.shape[0], dtype=np.float32)[:, None]
grad = np.clip((yy - 1290) / 16, 0, 1)
af = af * (1 - lid[..., None] * (0.05 + 0.07 * grad[..., None]) * np.array([0.8, 1.0, 1.1]))
nz = cv2.GaussianBlur(rng.standard_normal(a.shape[:2]).astype(np.float32), (0, 0), 0.9) * 3.2
af = af + nz[..., None] * np.maximum(lid, cv2.GaussianBlur(m2.astype(np.float32) / 255, (0, 0), 2))[..., None]
# lash line: soft, slightly irregular, thicker in the middle (closed-down lid seen from above)
ov = Image.new('L', (a.shape[1], a.shape[0]), 0); od = ImageDraw.Draw(ov)
r2 = np.random.default_rng(21)
pts = [(2683 + i, 1302 + 5.5 * np.sin(np.pi * i / 55) - 0.05 * i + r2.normal(0, 0.25)) for i in range(0, 56)]
for j in range(len(pts) - 1):
    w = 1 + int(2.4 * np.sin(np.pi * j / 55) + 0.6)
    od.line([pts[j], pts[j + 1]], fill=210, width=w)
for i in range(4, 52, 2):                              # fine lashes: short, mostly hidden, low contrast
    x, y = pts[i]
    od.line([(x, y), (x - 1.5 - r2.random(), y + 2.5 + 2.5 * r2.random())], fill=110, width=1)
# far eye: a short downward lash at the profile edge, soft
for k in range(3):
    od.line([(2631 - k, 1300 + k * 1.2), (2624 - k * 1.2, 1309 + k)], fill=150, width=2)
ov = np.asarray(ov.filter(ImageFilter.GaussianBlur(0.9))).astype(np.float32)[..., None] / 255
af = af * (1 - ov * 0.82) + np.array([46, 33, 28], np.float32) * (ov * 0.82)
canvas = Image.fromarray(np.clip(af, 0, 255).astype(np.uint8))
canvas.save(OUT, optimize=True)
print('saved', OUT, canvas.size)
