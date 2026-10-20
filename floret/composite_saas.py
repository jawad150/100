"""Composite the SaaS cut: Blender RGBA frames over the navy background, with motion-graphics transitions.

At every cut: a 2-frame white flash, a zoom punch (the new shot starts 6 % in and eases out over 0.35 s),
and a soft light sweep across the background. The purple glow behind the device breathes throughout.

    python3 floret/composite_saas.py           # $OUT/blender/####.png -> $OUT/video_saas_silent.mp4
"""
import glob, os, subprocess
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', os.path.join(HERE, 'out'))
FPS = int(os.environ.get('FPS', 30))
CUTS = [2.2, 4.6, 6.6, 8.6]                 # must match SHOTS in saas_film.py
W, H = 1080, 1920

frames = sorted(glob.glob(os.path.join(OUT, 'blender', '*.png')))
assert frames, 'no Blender frames found'
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)


# navy #1A1734 with the fine weave + grain of the reference swatch
g = yy[:, :1] / (H - 1)
top, mid, bot = hexrgb('#191632'), hexrgb('#1a1734'), hexrgb('#1d1a39')
grad = np.where(g < 0.6, top + (mid - top) * (g / 0.6), mid + (bot - mid) * ((g - 0.6) / 0.4))
bg = np.repeat(grad[:, None, :], W, axis=1).reshape(H, W, 3)
xi, yi = xx.astype(int), yy.astype(int)
weave = np.where((xi + yi) % 4 == 0, 1.6, 0) + np.where((xi - yi + 4000) % 6 == 0, -1.2, 0)
n = (np.random.default_rng(7).random((H, W), dtype=np.float32) - 0.5) * 5 + weave
bg += np.stack([n, n, n * 1.3], -1)

dx, dy = (xx - 0.5 * W) / (0.85 * W), (yy - 0.48 * H) / (0.70 * H)
vig_a = (np.clip((np.sqrt(dx * dx + dy * dy) - 0.55) / 0.45, 0, 1) * 0.55)[..., None]
vig_c = hexrgb('#060414')
navy = hexrgb('#1a1734')
glow_c = np.array([78, 64, 190], np.float32)
sweep_c = np.array([150, 140, 255], np.float32)


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def since_cut(t):
    past = [c for c in CUTS if c <= t + 1e-6]
    return t - past[-1] if past else None


def punch(img, s):
    """Scale an RGBA frame about its centre by s >= 1 (crop back to size)."""
    if s <= 1.0005:
        return img
    w, h = round(W * s), round(H * s)
    big = img.resize((w, h), Image.BICUBIC)
    x0, y0 = (w - W) // 2, (h - H) // 2
    return big.crop((x0, y0, x0 + W, y0 + H))


out_path = os.path.join(OUT, 'video_saas_silent.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
for i, f in enumerate(frames):
    t = i / FPS
    sc = since_cut(t)
    # breathing glow behind the device
    cx, cy = (0.5 + 0.04 * np.sin(t * 0.5)) * W, (0.47 + 0.03 * np.cos(t * 0.4)) * H
    gr = np.sqrt(((xx - cx) / (0.62 * W)) ** 2 + ((yy - cy) / (0.46 * H)) ** 2)
    ga = (np.clip(1 - gr / 0.7, 0, 1) * (0.20 + 0.05 * np.sin(t * 1.3)))[..., None]
    frame = bg * (1 - ga) + glow_c * ga
    # light sweep across the background after each cut (a soft diagonal band moving left to right)
    if sc is not None and sc < 0.9:
        pos = -0.3 + 1.6 * smooth(sc / 0.9)
        band = np.exp(-(((xx / W - pos) + (yy / H - 0.5) * 0.35) / 0.09) ** 2) * 0.10 * (1 - sc / 0.9)
        frame = frame * (1 - band[..., None]) + sweep_c * band[..., None]
    fg = Image.open(f).convert('RGBA')
    if sc is not None:
        fg = punch(fg, 1 + 0.06 * (1 - smooth(sc / 0.35)))
    fg = np.asarray(fg, np.float32)
    a = fg[..., 3:] / 255
    frame = fg[..., :3] * a + frame * (1 - a)
    frame = frame * (1 - vig_a) + vig_c * vig_a
    if sc is not None and sc < 2 / FPS:                       # white flash on the cut
        frame = frame * 0.45 + 255 * 0.55 * (1 - sc * FPS / 2)
    fade = 1 - smooth(t / 0.4)                                # open from navy
    fade = max(fade, smooth((t - (len(frames) - 1) / FPS + 0.5) / 0.5))   # close to navy
    frame = frame * (1 - fade) + navy * fade
    enc.stdin.write(np.clip(frame + 0.5, 0, 255).astype(np.uint8).tobytes())
    if i % 60 == 0:
        print('composite', i, len(frames), flush=True)
enc.stdin.close()
enc.wait()
print(out_path)
