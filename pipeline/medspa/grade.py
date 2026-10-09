"""Color grade for the P.S. Med Spa reel.

The delivered edit is already display-referred Rec.709 (blacks ~code 20, normal
contrast), so no S-Log3 -> Rec.709 transform is applied (doing so crushes it;
see README). The grade is:

  1. per-shot balance (exposure + white balance, in linear light)
  2. a global "look" baked into a 65^3 3D LUT (Rec.709 in -> Rec.709 out):
     filmic S-curve with soft highlight roll-off, OKLCh color work (richer
     reds, protected skin, tamed blue gloves), warm-highlight/cool-shadow split.

`python3 grade.py cube` writes the look as a .cube LUT that loads in DaVinci
Resolve (Color page -> LUTs, or node -> LUT), and `python3 grade.py preview`
writes before/after stills.
"""
import os, sys
import numpy as np, cv2
from common import WS, SHOTS, HERE

N_LUT = 65

# per-shot balance: (exposure stops, (r, g, b) linear gains)
# from neutral-highlight measurements: most shots read slightly blue,
# the hallway shots slightly green; shot 3 sits a touch under.
BALANCE = {
    0: (0.00, (1.000, 0.995, 0.965)),
    1: (-0.05, (0.990, 0.995, 1.000)),
    2: (0.05, (1.020, 0.975, 0.975)),
    3: (0.22, (1.020, 0.975, 0.980)),
    4: (0.05, (1.010, 0.990, 0.965)),
    5: (0.00, (1.000, 0.995, 0.962)),
    6: (0.00, (1.000, 0.995, 0.965)),
    7: (0.00, (1.005, 0.985, 0.965)),
    8: (0.00, (1.000, 0.985, 0.985)),
    9: (0.02, (1.000, 1.000, 0.975)),
    10: (-0.05, (1.020, 0.990, 0.950)),
    11: (0.00, (1.020, 0.995, 0.965)),
    12: (-0.05, (1.020, 0.990, 0.960)),
    13: (0.02, (1.000, 1.000, 0.972)),
}

# ------------------------------------------------------------------ color math

def to_lin(v):
    return np.power(np.clip(v, 0, None), 2.4)

def to_disp(l):
    return np.power(np.clip(l, 0, None), 1 / 2.4)

M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
               [0.2119034982, 0.6806995451, 0.1073969566],
               [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
               [1.9779984951, -2.4285922050, 0.4505937099],
               [0.0259040371, 0.7827717662, -0.8086757660]])
M1i = np.linalg.inv(M1)
M2i = np.linalg.inv(M2)

def lin_to_oklab(c):
    lms = np.cbrt(c @ M1.T)
    return lms @ M2.T

def oklab_to_lin(lab):
    lms = lab @ M2i.T
    return (lms ** 3) @ M1i.T

def bump(h, center, width):
    """Smooth hue window (degrees) -> 0..1."""
    d = np.abs((h - center + 180) % 360 - 180)
    return np.clip(1 - d / width, 0, 1) ** 2 * (3 - 2 * np.clip(1 - d / width, 0, 1))

# display-domain tone curve (monotone cubic through control points)
CURVE_X = np.array([0.0, 0.05, 0.16, 0.42, 0.70, 0.88, 1.0])
CURVE_Y = np.array([0.012, 0.045, 0.150, 0.432, 0.735, 0.900, 0.975])

def tone(v):
    from scipy.interpolate import PchipInterpolator
    f = PchipInterpolator(CURVE_X, CURVE_Y, extrapolate=True)
    return f(np.clip(v, 0, 1))

def look(rgb):
    """rgb: (...,3) display-referred Rec.709 in [0,1] -> graded display values."""
    v = np.asarray(rgb, np.float64)
    # luminance-driven curve, applied mostly as a ratio (keeps hue), a bit per channel
    lin = to_lin(v)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722])
    yd = to_disp(Y)
    yd2 = tone(yd)
    ratio = to_lin(yd2) / np.maximum(Y, 1e-6)
    lin_r = lin * ratio[..., None]
    lin_c = to_lin(tone(v))
    lin = lin_r * 0.75 + lin_c * 0.25

    lab = lin_to_oklab(np.clip(lin, 0, None))
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360

    sat = 1.06 * np.ones_like(C)
    sat *= 1 + 0.14 * bump(h, 20, 16)          # reds / brand red / lips
    sat *= 1 - 0.05 * bump(h, 58, 18)          # skin: keep natural, a hair softer
    sat *= 1 - 0.16 * bump(h, 255, 35)         # blue gloves
    sat *= 1 - 0.10 * bump(h, 140, 35)         # greens
    sat *= 1 - 0.35 * np.clip((L - 0.86) / 0.14, 0, 1)   # highlight roll-off
    sat *= 1 - 0.25 * np.clip((0.22 - L) / 0.22, 0, 1)   # quiet shadows
    hshift = 4 * bump(h, 58, 22) - 6 * bump(h, 255, 35)  # skin toward golden, blue toward cyan
    h2 = np.radians(h + hshift)
    C2 = C * sat
    a, b = C2 * np.cos(h2), C2 * np.sin(h2)
    # split tone: cool-teal shadows, warm highlights
    sh = np.clip((0.45 - L) / 0.45, 0, 1) ** 1.5
    hi = np.clip((L - 0.55) / 0.45, 0, 1)
    a = a - 0.006 * sh + 0.003 * hi
    b = b - 0.008 * sh + 0.009 * hi
    lin = oklab_to_lin(np.stack([L, a, b], -1))
    return np.clip(to_disp(np.clip(lin, 0, None)), 0, 1)


# ------------------------------------------------------------------ LUT

_lut = None

def get_lut():
    global _lut
    if _lut is None:
        path = f'{WS}/look.npy'
        if os.path.exists(path):
            _lut = np.load(path)
        else:
            g = np.linspace(0, 1, N_LUT)
            R, G, B = np.meshgrid(g, g, g, indexing='ij')
            _lut = look(np.stack([R, G, B], -1)).astype(np.float32)   # [r,g,b,3]
            np.save(path, _lut)
    return _lut

def apply_lut(img, lut=None):
    """Trilinear 3D LUT on float32 HxWx3 in [0,1]."""
    lut = get_lut() if lut is None else lut
    n = lut.shape[0]
    x = np.clip(img, 0, 1) * (n - 1)
    i0 = np.minimum(x.astype(np.int32), n - 2)
    f = x - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    flat = lut.reshape(-1, 3)
    base = (r0 * n + g0) * n + b0
    def at(dr, dg, db):
        return flat[base + (dr * n + dg) * n + db]
    c00 = at(0, 0, 0) * (1 - fb) + at(0, 0, 1) * fb
    c01 = at(0, 1, 0) * (1 - fb) + at(0, 1, 1) * fb
    c10 = at(1, 0, 0) * (1 - fb) + at(1, 0, 1) * fb
    c11 = at(1, 1, 0) * (1 - fb) + at(1, 1, 1) * fb
    c0 = c00 * (1 - fg) + c01 * fg
    c1 = c10 * (1 - fg) + c11 * fg
    return c0 * (1 - fr) + c1 * fr

# per-shot black pull + saturation (display domain): the macro / pigment shots
# came in with lifted, milky blacks next to their neighbours
LIFT = {8: (0.045, 1.16), 10: (0.015, 1.06), 11: (0.06, 1.0), 12: (0.055, 1.08)}

def balance(img, shot):
    ev, gains = BALANCE.get(shot, (0.0, (1, 1, 1)))
    k = np.array(gains, np.float32) * np.float32(2 ** ev)
    v = to_disp(to_lin(img) * k).astype(np.float32)
    if shot in LIFT:
        blk, sat = LIFT[shot]
        # remove the pedestal with a soft quadratic toe below 2*blk (C1-continuous)
        v = np.where(v >= 2 * blk, (v - blk) / (1 - blk), v * v / (4 * blk) / (1 - blk)).astype(np.float32)
        if sat != 1.0:
            Y = (v @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
            v = np.clip(Y + (v - Y) * np.float32(sat), 0, 1)
    return v

_lut8 = None

def get_lut8():
    """The look expanded to every 8-bit RGB triplet (256^3, uint8): one gather per pixel."""
    global _lut8
    if _lut8 is None:
        path = f'{WS}/look8.npy'
        if os.path.exists(path):
            _lut8 = np.load(path, mmap_mode='r')
        else:
            v = np.arange(256, dtype=np.float32) / 255
            out = np.empty((256, 256, 256, 3), np.uint8)
            for r in range(256):
                G_, B_ = np.meshgrid(v, v, indexing='ij')
                rgb = np.stack([np.full_like(G_, v[r]), G_, B_], -1)
                out[r] = (np.clip(apply_lut(rgb), 0, 1) * 255 + 0.5).astype(np.uint8)
            np.save(path, out.reshape(-1, 3))
            _lut8 = np.load(path, mmap_mode='r')
    return _lut8

def grade(img, shot):
    """img float32 HxWx3 display Rec.709 [0,1] -> graded."""
    q = (np.clip(balance(img, shot), 0, 1) * 255 + 0.5).astype(np.uint32)
    idx = (q[..., 0] << 16) | (q[..., 1] << 8) | q[..., 2]
    return np.asarray(get_lut8())[idx].astype(np.float32) * np.float32(1 / 255)

def write_cube(path):
    lut = get_lut()
    n = lut.shape[0]
    with open(path, 'w') as f:
        f.write('TITLE "PS Med Spa look (Rec709 in/out)"\n')
        f.write(f'LUT_3D_SIZE {n}\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n')
        for b in range(n):          # .cube order: red changes fastest
            for g in range(n):
                for r in range(n):
                    c = lut[r, g, b]
                    f.write(f'{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}\n')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    if cmd == 'cube':
        out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', '..', 'reel', 'medspa', 'PS_MedSpa_Look_Rec709.cube')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        write_cube(out)
        print('wrote', out)
    else:
        if os.path.exists(f'{WS}/look.npy'):
            os.remove(f'{WS}/look.npy')
        from common import frame_path
        os.makedirs(f'{WS}/look', exist_ok=True)
        tiles = []
        for k, (a, b) in enumerate(SHOTS):
            im = cv2.imread(frame_path((a + b) // 2))[..., ::-1].astype(np.float32) / 255
            im = cv2.resize(im, (360, 640), interpolation=cv2.INTER_AREA)
            g = grade(im, k)
            tiles.append(np.concatenate([im, g], 1))
        rows = [np.concatenate(tiles[i:i + 4], 1) for i in range(0, 12, 4)]
        rows.append(np.concatenate(tiles[12:14] + [np.zeros_like(tiles[0])] * 2, 1))
        sheet = np.concatenate(rows, 0)
        cv2.imwrite(f'{WS}/look/grade_ab.jpg', (sheet[..., ::-1] * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print('preview', f'{WS}/look/grade_ab.jpg')
