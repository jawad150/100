import numpy as np, os, sys
from PIL import Image, ImageDraw, ImageFilter
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(B, 'sb')
rng = np.random.default_rng(7)

def rain_layer(w=1080, h=1920, seed=0, density=1.0):
    r = np.random.default_rng(seed)
    img = Image.new('L', (w, h), 0)
    for depth, n, ln, wd, br, blur in [(0, 260, (40, 90), 1, (60, 110), 0.6), (1, 140, (90, 170), 2, (90, 150), 0.9), (2, 40, (180, 320), 3, (120, 190), 1.6)]:
        layer = Image.new('L', (w, h), 0); d = ImageDraw.Draw(layer)
        for _ in range(int(n * density)):
            x = r.uniform(-100, w + 100); y = r.uniform(-300, h); L = r.uniform(*ln); ang = np.deg2rad(r.uniform(6, 10))
            x2 = x + L * np.sin(ang); y2 = y + L * np.cos(ang)
            d.line([(x, y), (x2, y2)], fill=int(r.uniform(*br)), width=wd)
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
        img = Image.fromarray(np.maximum(np.array(img), np.array(layer)))
    return img

def grade(im, preset):
    a = np.asarray(im.convert('RGB')).astype(np.float32) / 255.0
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    if preset == 'night':      # cool, dark, keep warm highlights
        sat = 0.55; a = lum + (a - lum) * sat
        a = np.clip(a, 0, 1) ** 1.35 * 0.78
        tint = np.array([0.82, 0.95, 1.12]); a = a * tint
        hi = np.clip((lum - 0.55) / 0.45, 0, 1); a = a * (1 - hi * 0.4) + hi * 0.4 * np.array([1.0, 0.78, 0.48]) * lum
    elif preset == 'dusk':
        sat = 0.7; a = lum + (a - lum) * sat; a = np.clip(a, 0, 1) ** 1.2 * 0.85
        a = a * np.array([0.88, 0.95, 1.08])
    elif preset == 'warm':
        sat = 0.9; a = lum + (a - lum) * sat; a = np.clip(a, 0, 1) ** 1.1
        a = a * np.array([1.08, 0.98, 0.86])
    elif preset == 'deep':     # very dark water for the verse
        sat = 0.35; a = lum + (a - lum) * sat; a = np.clip(a, 0, 1) ** 1.8 * 0.55
        a = a * np.array([0.78, 0.92, 1.15])
        # warm lamp glow from top
        h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
        g = np.exp(-(((xx - w * 0.62) / (w * 0.35)) ** 2 + ((yy - h * 0.22) / (h * 0.25)) ** 2))[..., None]
        a = a + g * 0.22 * np.array([1.0, 0.72, 0.38]) * (0.4 + lum)
    # vignette
    h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.35 * (((xx - w / 2) / (w / 1.4)) ** 2 + ((yy - h / 2) / (h / 1.4)) ** 2)
    a = a * np.clip(v, 0.55, 1)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def add_rain(im, seed=1, amt=0.55, density=1.0):
    r = np.asarray(rain_layer(seed=seed, density=density)).astype(np.float32)[..., None] / 255.0 * amt
    a = np.asarray(im).astype(np.float32) / 255.0
    a = 1 - (1 - a) * (1 - r * np.array([0.85, 0.92, 1.0]))   # screen
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

def crop916(path, cx=0.5, top=0.0, bottom=1.0):
    im = Image.open(path).convert('RGB'); W, H = im.size
    y0, y1 = int(H * top), int(H * bottom); h = y1 - y0; w = int(round(h * 9 / 16))
    if w > W: w = W; h = int(round(w * 16 / 9)); y1 = y0 + h
    x0 = int(min(max(cx * W - w / 2, 0), W - w))
    return im.crop((x0, y0, x0 + w, y1)).resize((1080, 1920), Image.LANCZOS)

P = lambda *p: os.path.join(B, *p)
jobs = {
 'f_window3':   (Image.open(P('picks_rain', 's1_window_3.jpg')), 'night', 0),
 'f_window1':   (Image.open(P('picks_rain', 's1_window_1.jpg')), 'night', 0),
 'f_man_lamp':  (Image.open(P('picks_people', 's2_busstop_3.jpg')), 'night', 0.6),
 'f_man_walk':  (Image.open(P('picks_people', 's2_busstop_2.jpg')), 'night', 0.6),
 'f_puddle':    (Image.open(P('picks_rain', 's3_puddle_1.jpg')), 'deep', 0),
 'f_umbrella':  (Image.open(P('picks_people', 's4_umbrella_1.jpg')), 'night', 0.45),
 'f_tea':       (Image.open(P('picks_interior', 's5_tea_1.jpg')), 'warm', 0),
 'f_phone':     (Image.open(P('picks_interior', 's6_phone_2.jpg')), 'warm', 0),
 'f_phone_lamp':(Image.open(P('picks_interior', 's6_phone_1.jpg')), 'warm', 0),
 'f_city_lamps':(Image.open(P('picks_people', 'x_city_3.jpg')), 'night', 0),
 'f_city_wet':  (Image.open(P('picks_people', 'x_city_2.jpg')), 'night', 0),
 'f_city_tram': (Image.open(P('picks_people', 'x_city_1.jpg')), 'dusk', 0.45),
 'f_bmhc_tower':(crop916(P('bmhc_photos', 'img', '38_Dut-kbsW4AIRs6T.jpg'), cx=0.47, top=0.0, bottom=0.79), 'night', 0.55),
 'f_bmhc_door': (crop916(P('bmhc_photos', 'img', '35_512783950_23901286552860169_4153225704051740605_n.jpg'), cx=0.42, top=0.0, bottom=0.40), 'dusk', 0.5),
 'f_bmhc_aerial':(crop916(P('bmhc_photos', 'img', '39_Generated-Image-October-05-2025-9_57PM-high-fidelity-v2-4x-1.jpeg'), cx=0.47), 'dusk', 0.4),
 'f_bmhc_snow': (crop916(P('bmhc_photos', 'img', '13_1-BMHC-web.jpg'), cx=0.48), 'dusk', 0.45),
}
for name, (im, pre, rain) in jobs.items():
    im = im.convert('RGB').resize((1080, 1920), Image.LANCZOS) if im.size != (1080, 1920) else im.convert('RGB')
    g = grade(im, pre)
    if rain: g = add_rain(g, seed=hash(name) % 1000, amt=rain)
    g.save(os.path.join(OUT, name + '.jpg'), quality=90)
    print('ok', name)
rain_layer(seed=3).save(os.path.join(OUT, 'rain_layer.png'))
