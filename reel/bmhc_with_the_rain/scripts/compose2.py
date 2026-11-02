"""Stage 2: composite graded shot clips + rain + captions + transitions -> video (no audio).
Usage: python3 -I compose2.py OUT.mp4 [--stills t1,t2,...]"""
import json, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
W, H, FPS, M = 1080, 1920, 30, 0.6
TL = json.load(open(P('timeline.json')))
VO = json.load(open(P('audio', 'vo', 'lines.json')))
SH = {s['name']: s for s in TL['shots']}
ORDER = [s['name'] for s in TL['shots']]

def ease(u):
    u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- static layers
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(1 - 0.35 * (((xx - W / 2) / (W / 1.4)) ** 2 + ((yy - H / 2) / (H / 1.4)) ** 2), 0.55, 1)
VIG = Image.fromarray((vig * 255).astype(np.uint8)).convert('RGB')
shade_a = np.interp(yy[:, 0], [0, 0.38 * H, 0.52 * H, 0.68 * H, H], [0, 0, 0.50, 0.42, 0.10])
SHADE = Image.new('RGBA', (W, H), (0, 0, 0, 0)); SHADE.putalpha(Image.fromarray((np.repeat(shade_a[:, None], W, 1) * 255).astype(np.uint8)))
g = np.exp(-(((xx - W * 0.62) / (W * 0.35)) ** 2 + ((yy - H * 0.22) / (H * 0.25)) ** 2))
GLOW = Image.fromarray((np.stack([g * 1.0, g * 0.72, g * 0.38], -1) * 0.22 * 0.6 * 255).astype(np.uint8))
BLACK = Image.new('RGB', (W, H), (0, 0, 0))
del yy, xx, g

class Rain:
    def __init__(self, seed, n=(240, 120, 36), wraps=(2, 3, 5), length=(36, 80, 170), bright=(90, 140, 200), loop=90):
        r = np.random.default_rng(seed); hw, hh = W // 2, H // 2; span = hh + 200
        layers = [dict(x=r.uniform(-80, hw + 40, n[i]), y=r.uniform(0, span, n[i]), L=r.uniform(0.6, 1.2, n[i]) * length[i] / 2,
                       v=wraps[i] * span / loop, b=r.uniform(0.6, 1, n[i]) * bright[i], w=i + 1) for i in range(3)]
        self.frames = []
        for f in range(loop):
            img = Image.new('L', (hw, hh), 0); d = ImageDraw.Draw(img)
            for lay in layers:
                ys = (lay['y'] + lay['v'] * f) % span - 100
                for x, y, L, b in zip(lay['x'], ys, lay['L'], lay['b']):
                    d.line([(x, y), (x + 0.14 * L, y + L)], fill=int(b), width=lay['w'])
            self.frames.append(img.filter(ImageFilter.GaussianBlur(0.7)))
    def rgb(self, fi, amt):
        L = self.frames[fi % len(self.frames)].resize((W, H), Image.BILINEAR)
        return Image.merge('RGB', [L.point(lambda v, k=amt * c: int(v * k)) for c in (0.85, 0.92, 1.0)])

RAIN_H = Rain(3); RAIN_L = Rain(5, n=(160, 70, 18), bright=(70, 110, 160))
RAIN = {'window': (RAIN_L, 0.35, 0), 'man': (RAIN_H, 0.6, 0), 'umbrella': (RAIN_H, 0.45, 17), 'bmhc': (RAIN_L, 0.5, 31)}

# ---------------------------------------------------------------- shot readers
class Reader:
    def __init__(self, name):
        self.name = name
        self.proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', P('shots', f'{name}.mp4'), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                     stdout=subprocess.PIPE)
        self.idx = -1; self.cur = None
    def frame(self, i):
        while self.idx < i:
            buf = self.proc.stdout.read(W * H * 3); self.idx += 1
            if len(buf) == W * H * 3: self.cur = Image.frombytes('RGB', (W, H), buf)
        return self.cur
READ = {n: Reader(n) for n in ORDER if n != 'endcard'}

def shot_img(name, t, fi):
    s = SH[name]
    if name == 'endcard':
        return BLACK
    li = max(int(round((t - (s['start'] - M)) * FPS)), 0)
    im = READ[name].frame(li)
    if name == 'verse':
        im = ImageChops.add(im, GLOW)
    im = ImageChops.multiply(im, VIG)
    if name in RAIN:
        rr, amt, off = RAIN[name]
        im = ImageChops.screen(im, rr.rgb(fi + off, amt))
    if name == 'phone':
        tb = t - s['start']
        if 0 <= tb < 0.7:
            k = math.sin(tb * 2 * math.pi * 14) * (1 - tb / 0.7)
            im = ImageChops.offset(im, int(round(3 * k)), 0)
    return im

# ---------------------------------------------------------------- overlays
_ov = {}
def ov(name):
    if name not in _ov:
        _ov[name] = Image.open(P('overlays', name + '.png')).convert('RGBA')
    return _ov[name]
def faded(img, a):
    if a >= 0.999: return img
    r, g_, b, al = img.split()
    return Image.merge('RGBA', (r, g_, b, al.point(lambda v: int(v * a))))
def comp(base, layer, a=1.0):
    if a <= 0.001: return base
    return Image.alpha_composite(base, faded(layer, a))

def caption_until(L):
    return {'L1': SH['window']['end'] - 0.12, 'L2': SH['man']['end'] - 0.25, 'L4': SH['umbrella']['end'] - 0.1,
            'L5': SH['mug']['end'] - 0.05, 'L6': SH['phone']['end'] - 0.05, 'L7': TL['vo']['L8'] - 0.1, 'L8': TL['vo']['L8'] + VO['L8']['dur'] + 0.15}[L]

def overlays(base_rgb, t, shot):
    a = base_rgb.convert('RGBA')
    if shot in ('window', 'man', 'umbrella', 'mug', 'phone', 'bmhc'):
        a = Image.alpha_composite(a, SHADE)
    v = SH['verse']
    if v['start'] <= t < v['end'] + 0.3:
        fo = 1 - ease((t - (v['end'] - 0.45)) / 0.5)
        a = comp(a, ov('verse_ar'), ease((t - (TL['vo']['rec5'] - 0.2)) / 0.9) * fo)
        a = comp(a, ov('verse_tr'), ease((t - (TL['vo']['L3'] - 0.15)) / 0.8) * fo)
    u_ = SH['umbrella']
    t_with = TL['vo']['L4'] + VO['L4']['words'][3]['s']
    if u_['start'] <= t < u_['end'] + 0.3:
        a = comp(a, ov('with_ar'), ease((t - t_with + 0.05) / 0.45) * (1 - ease((t - (u_['end'] - 0.3)) / 0.35)))
    for L in ['L1', 'L2', 'L4', 'L5', 'L6', 'L7', 'L8']:
        t0 = TL['vo'][L]; t1 = caption_until(L)
        if t0 - 0.05 <= t < t1 + 0.25:
            k = sum(1 for w in VO[L]['words'] if t >= t0 + w['s'] - 0.04)
            if k >= 1:
                a = comp(a, ov(f'cap_{L}_{k}'), 1 - ease((t - t1) / 0.25))
    ec = SH['endcard']
    if t >= ec['start'] - 0.6:
        L9 = TL['vo']['L9']
        a = comp(a, ov('end_bg'), ease((t - (ec['start'] - 0.6)) / 0.6))
        a = comp(a, ov('end_logo'), ease((t - (ec['start'] + 0.1)) / 0.6))
        a = comp(a, ov('end_title'), ease((t - (L9 - 0.1)) / 0.5))
        a = comp(a, ov('end_details'), ease((t - (L9 + 1.2)) / 0.5))
        a = comp(a, ov('end_crisis'), ease((t - (L9 + 1.8)) / 0.5))
        a = comp(a, ov('end_ai'), ease((t - (L9 + 2.3)) / 0.5))
    return a.convert('RGB')

DISSOLVES = (('window', 'man', 0.4), ('umbrella', 'mug', 0.4), ('mug', 'phone', 0.3), ('phone', 'bmhc', 0.4))
def frame_at(t, fi):
    cur = next((s for s in TL['shots'] if s['start'] <= t < s['end']), TL['shots'][-1])
    name = cur['name']
    im = shot_img(name, t, fi)
    if name == 'man' and t > cur['end'] - 0.5:
        im = Image.blend(BLACK, im, 1 - ease((t - (cur['end'] - 0.5)) / 0.5))
    if name == 'verse':
        k = ease((t - cur['start']) / 0.7)
        if t > cur['end'] - 0.45: k *= 1 - ease((t - (cur['end'] - 0.45)) / 0.45)
        im = Image.blend(BLACK, im, k)
    if name == 'umbrella':
        im = Image.blend(BLACK, im, ease((t - cur['start']) / 0.5))
    for A_, B_, d in DISSOLVES:
        b = SH[B_]['start']
        if b - d / 2 <= t < b + d / 2:
            u = ease((t - (b - d / 2)) / d)
            fa = im if name == A_ else shot_img(A_, t, fi)
            fb = im if name == B_ else shot_img(B_, t, fi)
            im = Image.blend(fa, fb, u)
    return overlays(im, t, name)

def main():
    out = sys.argv[1]
    stills = None
    if len(sys.argv) > 3 and sys.argv[2] == '--stills':
        stills = {int(round(float(x) * FPS)): x for x in sys.argv[3].split(',')}
    n = int(round(TL['end'] * FPS))
    enc = None
    if stills is None:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    last = max(stills) if stills else n - 1
    for fi in range(last + 1):
        t = fi / FPS
        im = frame_at(t, fi)
        if enc: enc.stdin.write(im.tobytes())
        if stills and fi in stills: im.save(out.replace('.jpg', f'_{float(stills[fi]):05.2f}.jpg'), quality=88)
        if fi % 150 == 0: print(f'{fi}/{n}', flush=True)
    if enc: enc.stdin.close(); enc.wait()
    print('done')

if __name__ == '__main__':
    main()
