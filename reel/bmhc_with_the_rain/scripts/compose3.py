"""v2 stage 2: graded shots + rain + purposeful transitions + the timed overlay layer -> video (no audio).
Usage: python3 -I compose3.py OUT.mp4 [--stills t1,t2,...]   (stills are written as OUT_<t>.jpg)
Each cut has its own transition, chosen for what the story is doing at that moment (see TRANSITIONS)."""
import json, os, subprocess, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(B, *p)
W, H, FPS, M = 1080, 1920, 30, 0.6
TL = json.load(open(P('timeline.json')))
SH = {s['name']: s for s in TL['shots']}
ORDER = [s['name'] for s in TL['shots']]
OVD = P('overlays3')

def clamp(u): return min(max(u, 0.0), 1.0)
def ease(u): u = clamp(u); return u * u * (3 - 2 * u)
def ease_in(u): u = clamp(u); return u * u * u
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3

# ---------------------------------------------------------------- static layers
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(1 - 0.35 * (((XX - W / 2) / (W / 1.4)) ** 2 + ((YY - H / 2) / (H / 1.4)) ** 2), 0.55, 1)
VIG = np.repeat((vig * 255).astype(np.uint8)[..., None], 3, 2)
shade_a = np.interp(YY[:, 0], [0, 0.38 * H, 0.52 * H, 0.68 * H, H], [0, 0, 0.50, 0.42, 0.10])
SHADE = (1 - shade_a)[:, None, None].astype(np.float32)
# a soft dark pool behind the gold مَعَ / WITH, used on the bright hall photo so the word reads clearly
_top = np.exp(-(((XX - W / 2) / (W * 0.42)) ** 2 + ((YY - 600) / 330) ** 2))
TOPSHADE = (1 - 0.55 * _top)[..., None].astype(np.float32)
g = np.exp(-(((XX - W * 0.62) / (W * 0.35)) ** 2 + ((YY - H * 0.22) / (H * 0.25)) ** 2))
GLOW = (np.stack([g * 1.0, g * 0.72, g * 0.38], -1) * 0.22 * 0.6 * 255).astype(np.uint8)
BLACK = np.zeros((H, W, 3), np.uint8)
WARM = np.array([255, 196, 128], np.float32)
del g, vig

def screen(a, b):
    return 255 - cv2.multiply(255 - a, 255 - b, scale=1 / 255)

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
            self.frames.append(cv2.resize(np.asarray(img.filter(ImageFilter.GaussianBlur(0.7))), (W, H), interpolation=cv2.INTER_LINEAR))
    def rgb(self, fi, amt):
        L = self.frames[fi % len(self.frames)].astype(np.float32) * amt
        return np.clip(np.stack([L * 0.85, L * 0.92, L], -1), 0, 255).astype(np.uint8)

RAIN_H = Rain(3); RAIN_L = Rain(5, n=(160, 70, 18), bright=(70, 110, 160))
RAIN = {'window': (RAIN_L, 0.35, 0), 'man': (RAIN_H, 0.6, 0), 'umbrella': (RAIN_H, 0.45, 17),
        'ease': (RAIN_L, 0.3, 41), 'bmhc': (RAIN_L, 0.5, 31)}
CAPTION_SHOTS = {'window', 'man', 'umbrella', 'with2', 'ease', 'console', 'phonep', 'bmhc', 'inside', 'convo'}

# ---------------------------------------------------------------- shot readers
class Reader:
    def __init__(self, name):
        self.proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', P('shots', f'{name}.mp4'), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                     stdout=subprocess.PIPE)
        self.idx = -1; self.cur = BLACK
    def frame(self, i):
        while self.idx < i:
            buf = self.proc.stdout.read(W * H * 3); self.idx += 1
            if len(buf) == W * H * 3: self.cur = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        return self.cur
READ = {n: Reader(n) for n in ORDER if n != 'endcard'}

def grab(name, t):
    """one frame of a graded shot at absolute time t (for measuring light positions)"""
    s = SH[name]; tt = max(0.0, t - (s['start'] - M))
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{tt:.3f}', '-i', P('shots', f'{name}.mp4'), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    return np.frombuffer(out, np.uint8).reshape(H, W, 3)
def brightest(img, warm=False):
    f = img.astype(np.float32)
    lum = f[..., 0] * 0.6 + f[..., 1] * 0.3 + f[..., 2] * 0.1 if warm else f.mean(2)
    lum = cv2.GaussianBlur(lum, (0, 0), 40)
    y, x = np.unravel_index(np.argmax(lum[200:H - 300]), lum[200:H - 300].shape)
    return float(x), float(y + 200)

def shot_img(name, t, fi):
    s = SH[name]
    if name == 'endcard':          # the last picture keeps playing while the panel opens over it
        return shot_img(ORDER[-2], t, fi) if t < s['start'] + M - 0.05 else BLACK
    li = max(int(round((t - (s['start'] - M)) * FPS)), 0)
    im = READ[name].frame(li)
    if name == 'verse': im = cv2.add(im, GLOW)
    im = cv2.multiply(im, VIG, scale=1 / 255)
    if name in RAIN:
        rr, amt, off = RAIN[name]; im = screen(im, rr.rgb(fi + off, amt))
    if name == 'phonep':                      # the buzz shakes the frame for half a second
        tb = t - s['start']
        if 0 <= tb < 0.5:
            k = math.sin(tb * 2 * math.pi * 16) * (1 - tb / 0.5)
            im = shift(im, 4 * k)
    return im

# ---------------------------------------------------------------- transition helpers
def bloom(im, p, radius, strength, lift=0.0):
    """additive warm light centred on p (strength 0..1), plus an optional whole-frame warm lift"""
    if strength <= 0.002 and lift <= 0.002: return im
    sm = 4; gy, gx = YY[::sm, ::sm], XX[::sm, ::sm]
    gl = np.exp(-(((gx - p[0]) ** 2 + (gy - p[1]) ** 2) / (2 * radius ** 2)))
    gl = cv2.resize(gl, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    f = im.astype(np.float32) + (gl * strength * 1.15 + lift) * WARM
    return np.clip(f, 0, 255).astype(np.uint8)
def zoom(im, s, p):
    if abs(s - 1) < 1e-3: return im
    Mx = np.float32([[s, 0, p[0] * (1 - s)], [0, s, p[1] * (1 - s)]])
    return cv2.warpAffine(im, Mx, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def gain(im, k, add=0.0):
    return np.clip(im.astype(np.float32) * k + add * WARM, 0, 255).astype(np.uint8)
def mix(a, b, alpha):            # alpha: HxW float (1 = b)
    al = alpha[..., None] if alpha.ndim == 2 else alpha
    return (a.astype(np.float32) * (1 - al) + b.astype(np.float32) * al).astype(np.uint8)
def shift(im, dx):
    if abs(dx) < 0.5: return im
    return cv2.warpAffine(im, np.float32([[1, 0, dx], [0, 1, 0]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def shift_blur(im, dx, blur):
    out = shift(im, dx)
    k = int(round(blur))
    return cv2.blur(out, (k, 1)) if k > 1 else out

# ripple geometry (verse -> umbrella)
RC = (540.0, 980.0)
RR = np.sqrt((XX - RC[0]) ** 2 + (YY - RC[1]) ** 2) + 1e-3
RUX, RUY = (XX - RC[0]) / RR, (YY - RC[1]) / RR
# rain-streak edge (ease -> console): smooth wander + fine streaks, per column
rng = np.random.default_rng(11)
_n = cv2.GaussianBlur(rng.uniform(0, 1, (1, W)).astype(np.float32), (0, 0), 30)
_n = (_n - _n.min()) / (np.ptp(_n) + 1e-6)
_f = cv2.GaussianBlur(rng.uniform(0, 1, (1, W)).astype(np.float32), (0, 0), 3); _f = (_f - _f.min()) / (np.ptp(_f) + 1e-6)
STREAK = (_n * 180 + _f ** 2 * 55).ravel()   # slow wander plus rivulets, like water running down glass

LIGHT = {}
def measure():
    c1 = SH['window']['end']
    LIGHT['open'] = brightest(grab('window', 0.6), warm=True)
    LIGHT['A1'] = brightest(grab('window', c1 - 0.1), warm=True)
    LIGHT['B1'] = brightest(grab('man', c1 + 0.1), warm=True)
    door = json.load(open(P('shots', 'bmhc_door.json')))
    last = max(door, key=float); LIGHT['door'] = tuple(door[last])
    print('lights', {k: tuple(round(v) for v in p) for k, p in LIGHT.items()}, flush=True)

# ---------------------------------------------------------------- transitions, one per cut
def T(name): return SH[name]['start']
def frame_at(t, fi):
    cur = next((s for s in TL['shots'] if s['start'] <= t < s['end']), TL['shots'][-1])['name']
    im = shot_img(cur, t, fi)

    # OPEN · curiosity: a single warm light blooms out of black, then the window resolves around it
    if t < 1.4:
        k = ease((t - 0.25) / 0.95)
        b = ease(t / 0.45) * (1 - ease((t - 0.45) / 0.9))
        im = bloom((im.astype(np.float32) * k).astype(np.uint8), LIGHT['open'], 150 + 260 * ease(t / 1.2), 0.55 * b)

    # window -> man · light match: the amber window light carries across the cut and becomes the street light
    c = T('man')
    if c - 0.3 <= t < c + 0.3:
        u = (t - (c - 0.3)) / 0.6
        p = (LIGHT['A1'][0] + (LIGHT['B1'][0] - LIGHT['A1'][0]) * ease(u), LIGHT['A1'][1] + (LIGHT['B1'][1] - LIGHT['A1'][1]) * ease(u))
        im = bloom(im, p, 260 + 160 * math.sin(math.pi * u), 0.75 * math.sin(math.pi * u), lift=0.10 * math.sin(math.pi * u))

    # man -> verse · seriousness: push into the dark of his coat until it swallows the frame; the verse rises out of black
    c = T('verse')
    if c - 0.65 <= t < c:
        u = (t - (c - 0.65)) / 0.65
        im = zoom(im, 1 + 0.38 * ease_in(u), (540, 1180))
        im = (im.astype(np.float32) * (1 - ease(u * 1.05))).astype(np.uint8)
    if c <= t < c + 1.3:
        im = (im.astype(np.float32) * ease((t - c - 0.2) / 1.0)).astype(np.uint8)

    # verse -> umbrella · the key message lands: a raindrop ripple opens from the water into the next scene
    c = T('umbrella')
    if c - 0.08 <= t < c + 0.62:
        u = (t - (c - 0.08)) / 0.7
        R = 1300 * ease_out(u) ** 1.1
        A = shot_img('verse', t, fi) if cur != 'verse' else im
        Bm = shot_img('umbrella', t, fi) if cur != 'umbrella' else im
        A = (A.astype(np.float32) * (1 - 0.35 * u)).astype(np.uint8)
        off = (22 * (1 - u)) * np.exp(-((RR - R) / 46) ** 2)
        mx, my = XX + RUX * off, YY + RUY * off
        A = cv2.remap(A, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        Bm = cv2.remap(Bm, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        al = np.clip((R - RR) / 28 + 0.5, 0, 1)
        f = A.astype(np.float32) * (1 - al[..., None]) + Bm.astype(np.float32) * al[..., None]
        ring = (np.exp(-((RR - R) / 10) ** 2) * 70 + np.exp(-((RR - R * 0.72) / 8) ** 2) * 28) * (1 - u)
        im = np.clip(f + ring[..., None] * np.array([0.85, 0.92, 1.0], np.float32), 0, 255).astype(np.uint8)

    # umbrella -> with2 · motion handoff: both shots walk away from us, so the cut rides a forward push (z-axis blur)
    c = T('with2')
    if c - 0.22 <= t < c + 0.3:
        if t < c:
            u = ease_in((t - (c - 0.22)) / 0.22); im = zoom(im, 1 + 0.16 * u, (540, 900))
            if u > 0.05: im = cv2.addWeighted(im, 0.55, zoom(im, 1 + 0.05 * u, (540, 900)), 0.45, 0)
        else:
            u = ease_out((t - c) / 0.3); im = zoom(im, 1.14 - 0.14 * u, (540, 900))
            if u < 0.95: im = cv2.addWeighted(im, 0.6, zoom(im, 1 + 0.05 * (1 - u), (540, 900)), 0.4, 0)

    # with2 -> ease · clarity: light breaks through, the frame over-exposes warm and settles on the lamp in the rain
    c = T('ease')
    if c - 0.3 <= t < c:
        u = ease_in((t - (c - 0.3)) / 0.3); im = gain(im, 1 + 1.6 * u, 0.55 * u)
    elif c <= t < c + 0.55:
        u = ease_out((t - c) / 0.55); im = gain(im, 2.6 - 1.6 * u, 0.55 * (1 - u))

    # ease -> console · emotional connection: a rain-streak wipe runs down the glass and reveals the two of them
    c = T('console')
    if c - 0.3 <= t < c + 0.38:
        u = ease((t - (c - 0.3)) / 0.68)
        front = -300 + (H + 600) * u
        A = shot_img('ease', t, fi) if cur != 'ease' else im
        Bm = shot_img('console', t, fi) if cur != 'console' else im
        d = front + STREAK[None, :] - YY
        al = np.clip(d / 130, 0, 1)
        f = A.astype(np.float32) * (1 - al[..., None]) + Bm.astype(np.float32) * al[..., None]
        f += (np.exp(-((d - 45) / 16) ** 2) * 42)[..., None] * np.array([0.85, 0.92, 1.0], np.float32)
        im = np.clip(f, 0, 255).astype(np.uint8)

    # console -> phonep · a purposeful hard cut on the phone buzz (the shake lives in shot_img)

    # phonep -> bmhc · a door opening: the next scene parts from a centre slit, warm light on its edges
    c = T('bmhc')
    if c - 0.12 <= t < c + 0.5:
        u = ease((t - (c - 0.12)) / 0.62)
        hw = 575 * u
        A = shot_img('phonep', t, fi) if cur != 'phonep' else im
        Bm = shot_img('bmhc', t, fi) if cur != 'bmhc' else im
        dx = np.abs(XX[0] - 540)
        al = np.clip((hw - dx) / 22, 0, 1)[None, :]
        A = A.astype(np.float32) * (1 - 0.45 * u)
        f = A * (1 - al[..., None]) + Bm.astype(np.float32) * al[..., None]
        edge = np.exp(-((dx - hw) / 16) ** 2)[None, :, None] * (0.9 - 0.6 * u)
        im = np.clip(f + edge * WARM, 0, 255).astype(np.uint8)

    # bmhc -> inside · continuity: push through the lit doorway; the next scene emerges from its light
    c = T('inside')
    if c - 0.42 <= t < c:
        u = (t - (c - 0.42)) / 0.42
        im = zoom(im, 1 + 0.85 * ease_in(u), LIGHT['door'])
        im = bloom(im, LIGHT['door'], 180 + 600 * ease_in(u), 0.9 * ease(u), lift=0.75 * ease_in(u) ** 1.5)
    elif c <= t < c + 0.55:
        u = ease_out((t - c) / 0.55)
        im = zoom(im, 1.12 - 0.12 * u, (540, 960))
        im = bloom(im, (540, 960), 780, 0.6 * (1 - u), lift=0.75 * (1 - u) ** 1.5)

    # inside -> convo · rack focus from one scene to the other, the eye pulled to the conversation
    c = T('convo')
    if c - 0.32 <= t < c + 0.38:
        A = shot_img('inside', t, fi) if cur != 'inside' else im
        Bm = shot_img('convo', t, fi) if cur != 'convo' else im
        sa = 18 * ease_in((t - (c - 0.32)) / 0.32) if t < c + 0.12 else 18
        sb = 18 * (1 - ease_out((t - c + 0.1) / 0.48))
        A = cv2.GaussianBlur(A, (0, 0), max(sa, 0.1)) if sa > 0.3 else A
        Bm = cv2.GaussianBlur(Bm, (0, 0), max(sb, 0.1)) if sb > 0.3 else Bm
        im = cv2.addWeighted(A, 1 - ease((t - (c - 0.12)) / 0.24), Bm, ease((t - (c - 0.12)) / 0.24), 0)

    # convo -> end card · the gold line under "support..." opens into the brand panel (drawn in the overlay layer)
    if cur in CAPTION_SHOTS:
        im = (im.astype(np.float32) * (SHADE * TOPSHADE if cur == 'with2' else SHADE)).astype(np.uint8)
    return overlay(im, fi)

def overlay(im, fi):
    fn = os.path.join(OVD, f'f_{fi:05d}.png')
    if not os.path.exists(fn): return im
    ov = Image.open(fn)
    if ov.mode != 'RGBA': ov = ov.convert('RGBA')
    if ov.getchannel('A').getbbox() is None: return im
    base = Image.fromarray(im).convert('RGBA'); base.alpha_composite(ov)
    return np.asarray(base.convert('RGB'))

def main():
    out = sys.argv[1]
    stills = None
    if len(sys.argv) > 3 and sys.argv[2] == '--stills':
        stills = {int(round(float(x) * FPS)): x for x in sys.argv[3].split(',')}
    measure()
    n = int(round(TL['end'] * FPS))
    enc = None
    if stills is None:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    last = max(stills) if stills else n - 1
    for fi in range(last + 1):
        t = fi / FPS
        if stills and fi not in stills:
            # keep the readers in step cheaply: advance whichever shots are live
            for nme in ORDER:
                s = SH[nme]
                if nme != 'endcard' and s['start'] - M <= t <= s['end'] + M:
                    READ[nme].frame(max(int(round((t - (s['start'] - M)) * FPS)), 0))
            continue
        im = frame_at(t, fi)
        if enc: enc.stdin.write(np.ascontiguousarray(im).tobytes())
        if stills and fi in stills: Image.fromarray(im).save(out.replace('.jpg', f'_{float(stills[fi]):05.2f}.jpg'), quality=88)
        if fi % 150 == 0: print(f'{fi}/{n}', flush=True)
    if enc: enc.stdin.close(); enc.wait()
    print('done')

if __name__ == '__main__':
    main()
