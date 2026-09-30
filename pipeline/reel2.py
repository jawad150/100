"""Reel 2: full split-screen result in the orange/black theme + profile / 'Comment JD' ending.

python3 reel2.py still 1.8,15,29.5
python3 reel2.py range <f0> <f1> <out.mp4>
"""
import sys, os, math, functools, subprocess, time as _time
import numpy as np
import cv2
import reel as R
from engine import *

FPS = 30
DUR = 34.0
MAIN_END = 28.0            # result video length
R.ZT0, R.ZT1, R.BADGE_T0 = 28.0, 28.85, 29.0
R.USER = '@jawad_mp4'

@functools.lru_cache(maxsize=None)
def _badge():
    name = text_sprite(R.USER, 'Unbounded-800', 50)
    sub = text_sprite("I'll upload the full process", 'Inter-600', 28, hexc('#B8B0A6'))
    btn = pill('COMMENT  "JD"', 'Inter-900', 36, pad_x=46, pad_y=26, grad=(hexc('#FF9A2E'), hexc('#FF4A00')),
               border=(1, 0.85, 0.7, 0.55), icon=chat_icon(), tracking=0.06)
    return name, sub, btn
R.badge_parts = _badge

@functools.lru_cache(maxsize=None)
def chat_icon(size=40):
    from PIL import Image, ImageDraw
    n = size * 4
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 8, n - 4, n * 0.74], radius=n * 0.2, fill=(255, 255, 255, 255))
    d.polygon([(n * 0.25, n * 0.7), (n * 0.2, n * 0.95), (n * 0.48, n * 0.72)], fill=(255, 255, 255, 255))
    for k in range(3):
        cx = n * (0.32 + 0.18 * k)
        d.ellipse([cx - n * 0.055, n * 0.4 - n * 0.055, cx + n * 0.055, n * 0.4 + n * 0.055], fill=(255, 90, 0, 255))
    return pil_to_sprite(im.resize((size, size), Image.LANCZOS))

@functools.lru_cache(maxsize=None)
def end_words():
    l1 = R.word_sprites('WANT THE', 'Unbounded-900', 78)
    l2 = R.word_sprites('TUTORIAL?', 'Unbounded-900', 96, grad=(hexc('#FFB347'), hexc('#FF4D00')))
    return l1, l2

@functools.lru_cache(maxsize=None)
def main_chip():
    return pill('AI MOTION SWAP', 'Inter-800', 26, dot=ORANGE, fill=(1, 1, 1, 0.06),
                border=(1, 0.55, 0.2, 0.5), tracking=0.1)

@functools.lru_cache(maxsize=None)
def main_cta():
    return pill('COMMENT "JD" FOR THE TUTORIAL', 'Inter-900', 31, pad_x=34, pad_y=26,
                grad=(hexc('#FF9A2E'), hexc('#FF4A00')), border=(1, 0.85, 0.7, 0.55), icon=chat_icon(46), tracking=0.03)

@functools.lru_cache(maxsize=None)
def main_cta_glow():
    return glow_of(main_cta(), 22, ORANGE, 1.0)

def main_crop(t, half):
    return R.res_half_crop(min(t, 28.0), half)

def scene_main(cv, t, cam):
    obj = R.obj3d
    obj(cv, 'capsule', t, 95 + wobble(t, 0.2, 8), 175 + wobble(t, 0.25, 10), 150 * R.pop(t, 0.5), blur=5, rot=-20, opacity=0.85)
    obj(cv, 'rcube', t, 70 + wobble(t, 0.3, 6), 1735 + wobble(t, 0.2, 10), 115 * R.pop(t, 0.9), blur=4, rot=10)
    pk = e_out_back(prog(t, 1.0, 1.55), 2.0)
    obj(cv, 'blob_drop', t, 870 + wobble(t, 0.4, 4), lerp(660, 522, pk) + wobble(t, 0.5, 5), 175, rot=8, t_off=0.3)
    p1 = e_out_expo(prog(t, 0.05, 0.95))
    p2 = e_out_expo(prog(t, 0.15, 1.05))
    sway = wobble(t, 0.18, 2.2)
    badge_p = e_out_back(prog(t, 0.85, 1.25))
    push = t * 1.2
    for half, (c, p, sgn) in enumerate([(R.TOP_C, p1, -1), (R.BOT_C, p2, 1)]):
        rgb = main_crop(t, half)
        badge = R.chip('original' if half == 0 else 'genjutsu')
        bw = badge.shape[1]
        spr = R.make_card(rgb, R.CW, R.CH, r=28, glow=0.28 if half == 0 else 0.5,
                          badges=[(badge, 26 + bw / 2 - 30, 44, 0.6 + 0.4 * badge_p, min(1, badge_p * 1.5))])
        cy = lerp(c[1] + sgn * 900, c[1], p) + wobble(t, 0.22, 4, half)
        cz = lerp(500, 0, p) - push
        rx = lerp(-sgn * 55, 0, p) + wobble(t, 0.15, 1.2, half)
        ry = sway * (1 if half == 0 else -1)
        draw3d(cv, spr, c[0], cy, cz, w=spr.shape[1], rx=rx, ry=ry, cam=cam, opacity=prog(t, 0.05, 0.3))
    cp = R.pop(t, 0.8, 0.5)
    if cp > 0:
        pulse = (t * 0.8) % 1.0
        draw(cv, ring_sprite(260, 60, 3, ORANGE2), 540, 1000, scale=(0.55 + pulse * 1.2) * cp, opacity=(1 - pulse) * 0.8, mode='add')
        draw(cv, R.connector(), 540, 1000, scale=cp, rot=(1 - cp) * 90)
    obj(cv, 'blob_bear', t, 130 + wobble(t, 0.35, 4), 1470 + wobble(t, 0.45, 6), 165 * R.pop(t, 1.15), rot=-8, t_off=0.7)
    obj(cv, 'sphere', t, 985 + wobble(t, 0.2, 5), 1510 + wobble(t, 0.3, 8), 150 * R.pop(t, 1.3))
    obj(cv, 'torus', t, 975 + wobble(t, 0.25, 6), 225 + wobble(t, 0.3, 8), 185 * R.pop(t, 0.7), blur=1.5, rot=-15)
    l1, l2, size = R.hook_words()
    bp = e_out_expo(prog(t, 0.3, 0.8))
    draw(cv, main_chip(), 540, 205 + (1 - bp) * 30, opacity=bp)
    R.draw_words(cv, l1, 540, 300, t, 0.42)
    R.draw_words(cv, l2, 540, 300 + size * 1.18, t, 0.62, glow=ORANGE)
    ctp = R.pop(t, 1.35, 0.55, 1.8)
    if ctp > 0:
        cta = main_cta()
        y = 1572 + (1 - min(ctp, 1)) * 40
        op = min(1, ctp * 1.5)
        draw(cv, main_cta_glow(), 540, y + 10, scale=ctp, opacity=op * (0.55 + 0.25 * math.sin(t * 5)), mode='add')
        s = ctp * (1 + 0.025 * math.sin(t * 5))
        draw(cv, cta, 540, y, scale=s, opacity=op)
        ph = ((t - 1.6) % 1.9) / 1.2
        if 0 < ph < 1:
            draw(cv, R.pill_sheen(cta, ph), 540, y, scale=s, opacity=op, mode='add')
    R.light_streak(cv, t, 0.0, 1000, 0.6, 1.2)

def render_sub(t):
    cv = np.empty((H, W, 3), np.float32)
    R.background(cv, t)
    cam = R.cam_at(t)
    scene_main(cv, t, cam)
    if t >= R.ZT0:
        inner = cv
        cv = np.empty((H, W, 3), np.float32)
        R.background(cv, t, glow=1.2, rays=0.6)
        R.profile_ending(cv, inner, t)
        l1, l2 = end_words()
        R.draw_words(cv, l1, 540, 420, t, R.BADGE_T0 + 0.5)
        R.draw_words(cv, l2, 540, 525, t, R.BADGE_T0 + 0.62, glow=ORANGE)
    return cv

FLASHES = [(0.0, 0.9, 0.5), (28.85, 0.3, 0.35)]

def render_frame(fi):
    t = fi / FPS
    nsub = 6 if (t < 1.4 or t > 27.9) else 2
    acc = None
    for k in range(nsub):
        ts = max(0.0, t + (k / (nsub - 1) - 0.5) * R.SHUTTER / FPS)
        f = render_sub(ts)
        acc = f if acc is None else acc + f
    acc /= nsub
    fl = 0.0
    for t0, amp, dur in FLASHES:
        if t0 <= t <= t0 + dur:
            fl = max(fl, amp * (1 - prog(t, t0, t0 + dur)) ** 2)
    fade = max(prog(t, DUR - 0.3, DUR), 1 - prog(t, 0.0, 0.18))
    ca = 6 * max(0, 1 - abs(t - 28.4) / 0.4)
    out = post(acc, fi, bloom=0.55, grain=0.02, ca=ca, flash=fl, fade=fade)
    return (out * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for ts in sys.argv[2].split(','):
            img = render_frame(int(round(float(ts) * FPS)))
            cv2.imwrite(f'{S}/out/r2_still_{float(ts):05.2f}.png', img[..., ::-1])
            print('still', ts, flush=True)
    else:
        f0, f1, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                              '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '12',
                              '-pix_fmt', 'yuv420p', outp], stdin=subprocess.PIPE)
        for fi in range(f0, f1):
            p.stdin.write(render_frame(fi).tobytes())
        p.stdin.close(); p.wait()
        print('done', outp, flush=True)
