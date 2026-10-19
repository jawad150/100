"""Composite the Blender RGBA frames over the navy background and encode the final videos.

    python3 floret/composite.py            # uses $OUT/blender/####.png, writes $OUT/video_3d_silent.mp4
"""
import glob, os, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', os.path.join(HERE, 'out'))
FPS = int(os.environ.get('FPS', 30))
W, H = 1080, 1920

frames = sorted(glob.glob(os.path.join(OUT, 'blender', '*.png')))
assert frames, 'no Blender frames found'

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# ---- navy background #1A1734 with the fine weave + grain of the reference swatch
def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)

g = yy[:, :1] / (H - 1)
top, mid, bot = hexrgb('#191632'), hexrgb('#1a1734'), hexrgb('#1d1a39')
grad = np.where(g < 0.6, top + (mid - top) * (g / 0.6), mid + (bot - mid) * ((g - 0.6) / 0.4))
bg = np.repeat(grad[:, None, :], W, axis=1).reshape(H, W, 3)
xi, yi = xx.astype(int), yy.astype(int)
weave = np.where((xi + yi) % 4 == 0, 1.6, 0) + np.where((xi - yi + 4000) % 6 == 0, -1.2, 0)
n = (np.random.default_rng(7).random((H, W), dtype=np.float32) - 0.5) * 5 + weave
bg += np.stack([n, n, n * 1.3], -1)

# ---- vignette (on top of everything)
dx, dy = (xx - 0.5 * W) / (0.85 * W), (yy - 0.48 * H) / (0.70 * H)
r = np.sqrt(dx * dx + dy * dy)
vig_a = (np.clip((r - 0.55) / 0.45, 0, 1) * 0.55)[..., None]
vig_c = hexrgb('#060414')

navy = hexrgb('#1a1734')
glow_c = np.array([78, 64, 190], np.float32)


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'video_3d_silent.mp4')],
                       stdin=subprocess.PIPE)
for i, f in enumerate(frames):
    t = i / FPS
    # slowly breathing purple glow behind the phone
    cx, cy = (0.5 + 0.03 * np.sin(t * 0.25)) * W, (0.48 + 0.02 * np.cos(t * 0.2)) * H
    gr = np.sqrt(((xx - cx) / (0.6 * W)) ** 2 + ((yy - cy) / (0.45 * H)) ** 2)
    ga = (np.clip(1 - gr / 0.7, 0, 1) * 0.22)[..., None]
    frame = bg * (1 - ga) + glow_c * ga
    fg = np.asarray(Image.open(f).convert('RGBA'), np.float32)
    a = fg[..., 3:] / 255
    frame = fg[..., :3] * a + frame * (1 - a)
    frame = frame * (1 - vig_a) + vig_c * vig_a
    fade = 1 - smooth(t / 0.8)
    frame = frame * (1 - fade) + navy * fade
    enc.stdin.write(np.clip(frame + 0.5, 0, 255).astype(np.uint8).tobytes())
    if i % 60 == 0:
        print('composite', i, len(frames), flush=True)
enc.stdin.close()
enc.wait()
print(os.path.join(OUT, 'video_3d_silent.mp4'))
