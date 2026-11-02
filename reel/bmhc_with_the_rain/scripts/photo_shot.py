"""A still photo as a moving 9:16 shot: slow eased push from one crop to another, graded with a LUT.
Usage: python3 -I photo_shot.py NAME PHOTO x0,y0,h0 x1,y1,h1 LUT
  crops are in source pixels (top-left x, y and height; width follows 9:16). Output covers shot start-0.6 .. end+0.6."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
W, H, FPS, M = 1080, 1920, 30, 0.6
name, photo, c0, c1, lut = sys.argv[1:6]
TL = json.load(open(P('timeline.json'))); s = {x['name']: x for x in TL['shots']}[name]
D = s['end'] - s['start'] + 2 * M
def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
im = Image.open(photo if os.path.isabs(photo) else P(photo)).convert('RGB')
k = 2 if im.height < 2400 else 1
src = im.resize((im.width * k, im.height * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2)) if k > 1 else im
(x0, y0, h0), (x1, y1, h1) = [tuple(float(v) * k for v in c.split(',')) for c in (c0, c1)]
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-vf', f"lut3d=file={P('luts', lut + '.cube')},format=yuv420p", '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '10',
                        P('shots', f'{name}.mp4')], stdin=subprocess.PIPE)
n = int(round(D * FPS))
for fi in range(n):
    u = ease(fi / (n - 1))
    h = h0 + (h1 - h0) * u; w = h * 9 / 16
    x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u
    fr = src.transform((W, H), Image.AFFINE, (w / W, 0, x, 0, h / H, y), resample=Image.BICUBIC)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print(name, 'frames', n, 'from', os.path.basename(photo))
