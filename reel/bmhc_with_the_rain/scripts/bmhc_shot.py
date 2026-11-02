import json, os, subprocess, numpy as np
from PIL import Image, ImageFilter, ImageChops
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
W, H, FPS, M = 1080, 1920, 30, 0.6
TL = json.load(open(P('timeline.json'))); SH = {s['name']: s for s in TL['shots']}
s = SH['bmhc']; dur = s['end'] - s['start']; D = dur + 2 * M
def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
im = Image.open(P('bmhc_photos', 'img', '38_Dut-kbsW4AIRs6T.jpg')).convert('RGB')
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
a = np.asarray(im).astype(np.float32) / 255
lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
a = lum + (a - lum) * 0.55
a = np.clip(a, 0, 1) ** 1.35 * 0.78 * np.array([0.82, 0.95, 1.12], np.float32)
hi = np.clip((lum - 0.55) / 0.45, 0, 1); a = a * (1 - hi * 0.4) + hi * 0.4 * np.array([1.0, 0.78, 0.48], np.float32) * lum
G = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)); BW, BH = G.size
gy, gx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10', '-pix_fmt', 'yuv420p', P('shots', 'bmhc.mp4')], stdin=subprocess.PIPE)
n = int(round(D * FPS))
for fi in range(n):
    tl = fi / FPS - M; t_abs = s['start'] + tl
    u = ease(tl / dur)
    top, bot = 0.0 + 0.20 * u, 0.79
    hh = (bot - top) * BH; ww = hh * 9 / 16
    cx, cy = 0.47 * BW, top * BH + hh / 2
    x0 = min(max(cx - ww / 2, 0), BW - ww); y0 = min(max(cy - hh / 2, 0), BH - hh)
    fr = G.transform((W, H), Image.AFFINE, (ww / W, 0, x0, 0, hh / H, y0), resample=Image.BICUBIC)
    g_on = ease((t_abs - (TL['vo']['L7'] + 0.1)) / 2.2)
    if g_on > 0:
        dx = (0.47 * BW - x0) / ww * W; dy = (0.705 * BH - y0) / hh * H; sc = (0.035 * BH) / hh * H
        gl = np.exp(-(((gx - dx) / (sc * 1.15)) ** 2 + ((gy - dy) / (sc * 2.0)) ** 2))
        sp = np.exp(-(((gx - dx) / (sc * 3.2)) ** 2 + ((gy - (dy + sc * 2.5)) / (sc * 1.2)) ** 2))
        f = g_on * (gl * 0.9 + sp * 0.35)
        rgb = (np.stack([f * 1.0, f * 0.72, f * 0.38], -1) * 255).clip(0, 255).astype(np.uint8)
        glow = Image.fromarray(rgb).resize((W, H), Image.BILINEAR)
        fr = ImageChops.add(fr, glow)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print('bmhc frames', n)
