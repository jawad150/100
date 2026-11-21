"""BISP reel colour pipeline (DaVinci-style, in code).

iPhone footage is HLG / BT.2020 10-bit. ffmpeg (zscale) converts primaries to BT.709 but keeps the HLG curve as a
log-like shaper, in 32-bit float. A per-clip 3D LUT built here then does, in order:
  1. HLG inverse OETF -> scene linear, HLG OOTF (system gamma 1.2) -> display linear (1.0 = reference white, 203 nit)
  2. per-clip balance in linear light (exposure + white balance, matched on skin so every shot cuts together)
  3. contrast in log2 around mid grey, then a filmic shoulder (ACES-fit) so the bright walls roll off instead of clipping
  4. the BISP look in display space: emerald shadows, warm gold highlights, purple tamed (aquarium), skin protected,
     slight matte black, gentle saturation
  5. Rec.709 encode (2.2 power, what phones show)

python3 grade.py measure   -> workspace_bisp/grade/balance.json (per-clip gains from skin + grey-world)
python3 grade.py luts      -> workspace_bisp/grade/<clip>.cube
python3 grade.py preview   -> workspace_bisp/grade/preview.jpg (before/after per clip)
"""
import os, sys, json, glob
import numpy as np
import cv2

WS = os.environ.get('BISP_WS', os.path.join(os.path.dirname(__file__), '..', '..', 'workspace_bisp'))
WS = os.path.abspath(WS)
GD = os.path.join(WS, 'grade')
os.makedirs(GD, exist_ok=True)

# ffmpeg: HLG BT.2020 -> HLG BT.709 (float). The LUT is applied right after this.
CST = ('zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=arib-std-b67:p=bt709:m=bt709:r=full,'
       'format=gbrpf32le')

A, B = 0.17883277, 1 - 4 * 0.17883277
C = 0.5 - A * np.log(4 * A)
REF_SCENE = 0.2646  # scene-linear value of HLG reference white (signal 0.75)


def hlg_to_display(E):
    """HLG signal (0..1) -> display linear relative to reference white (1.0 = 203 nit, peak ~4.9)."""
    E = np.clip(E, 0, 1)
    L = np.where(E <= 0.5, E * E / 3.0, (np.exp((E - C) / A) + B) / 12.0)
    Y = 0.2627 * L[..., 0] + 0.6780 * L[..., 1] + 0.0593 * L[..., 2]  # OOTF on luminance (BT.2100)
    g = np.power(np.maximum(Y, 1e-9), 0.2)[..., None]
    return L * g / (REF_SCENE ** 1.2)


def luma709(x):
    return 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]


def aces(x):
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)


# ---- the BISP look -------------------------------------------------------------------------------------------
LOOK = dict(
    contrast=1.10,        # log2 contrast around mid grey
    pre=0.62,             # ACES-fit input scale (sets where ref white lands)
    shadow_tint=(-0.030, 0.012, 0.004),   # emerald shadows (chroma offset, luma-neutral-ish)
    high_tint=(0.022, 0.008, -0.034),     # warm gold highlights
    sat=1.06,
    purple_sat=0.50,      # aquarium / magenta tamed
    skin_sat=0.98,
    lift=0.018,           # matte black
    white=0.985,          # soft white ceiling
)


def look(D, gain):
    """D: display-linear (ref white 1.0). gain: (3,) per-clip balance. Returns Rec.709 2.2-encoded 0..1."""
    x = D * np.asarray(gain, np.float32)
    # contrast in log2 around mid grey (0.18)
    y = luma709(x)
    ly = np.log2(np.maximum(y, 1e-6) / 0.18)
    ly2 = ly * LOOK['contrast']
    x = x * (np.power(2.0, ly2 - ly))[..., None]
    # filmic shoulder, hybrid: per-channel (film-like highlight desat) mixed with luminance-preserving
    xp = x * LOOK['pre']
    per = aces(xp)
    yl = luma709(xp)
    lum = xp * (aces(yl) / np.maximum(yl, 1e-6))[..., None]
    lin = 0.55 * per + 0.45 * np.clip(lum, 0, 1.2)
    lin = np.clip(lin, 0, 1)
    v = np.power(lin, 1 / 2.2)
    # display-space creative grade
    Y = luma709(v)[..., None]
    ws = np.clip(1 - Y / 0.55, 0, 1) ** 2
    wh = np.clip((Y - 0.45) / 0.55, 0, 1) ** 1.5
    v = v + ws * np.array(LOOK['shadow_tint']) + wh * np.array(LOOK['high_tint'])
    # hue-selective saturation in YCbCr
    Y = luma709(v)
    cb = (v[..., 2] - Y) / 1.8556
    cr = (v[..., 0] - Y) / 1.5748
    hue = np.degrees(np.arctan2(cr, cb)) % 360  # 0 = blue(+cb), 90 = red(+cr)
    sat = np.full(Y.shape, LOOK['sat'], np.float32)
    # magenta/purple sits between +cb and +cr (~20..75 deg here); skin/orange ~ 100..140
    def band(h, c, w):
        d = np.abs(((h - c + 180) % 360) - 180)
        return np.clip(1 - d / w, 0, 1)
    pm = band(hue, 40, 38)
    sk = band(hue, 122, 28)
    sat = sat * (1 - pm) + LOOK['purple_sat'] * pm
    sat = sat * (1 - sk) + LOOK['skin_sat'] * sk
    cb, cr = cb * sat, cr * sat
    r = Y + 1.5748 * cr
    b = Y + 1.8556 * cb
    g = (Y - 0.2126 * r - 0.0722 * b) / 0.7152
    v = np.stack([r, g, b], -1)
    v = LOOK['lift'] + v * (LOOK['white'] - LOOK['lift'])
    return np.clip(v, 0, 1)


# ---- measurement ---------------------------------------------------------------------------------------------
def load_probe(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)[..., ::-1].astype(np.float32) / 65535.0
    return im


_face = None


def faces(rgb8):
    global _face
    if _face is None:
        _face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    g = cv2.cvtColor(rgb8, cv2.COLOR_RGB2GRAY)
    f = _face.detectMultiScale(g, 1.1, 4, minSize=(24, 24))
    return sorted(f, key=lambda r: -r[2] * r[3])


SKIN_TARGET_Y = 0.52      # skin luminance in display linear (ref white 1.0) after balance
SKIN_TARGET_RB = (1.62, 0.74)   # skin r/g and b/g in display linear after balance (warm, natural)


def measure():
    clips = sorted({os.path.basename(p).rsplit('_', 1)[0] for p in glob.glob(os.path.join(WS, 'probe', '*_[0-9].png'))})
    out = {}
    for c in clips:
        skins, greys = [], []
        for p in sorted(glob.glob(os.path.join(WS, 'probe', c + '_*.png'))):
            D = hlg_to_display(load_probe(p))
            prev = (np.clip(look(D, (1, 1, 1)), 0, 1) * 255).astype(np.uint8)
            fs = faces(prev)
            if len(fs):
                x, y, w, h = fs[0]
                cx, cy = x + w // 2, y + int(h * 0.58)
                patch = D[cy - h // 6: cy + h // 8, cx - w // 5: cx + w // 5].reshape(-1, 3)
                yy = luma709(patch)
                keep = (yy > np.percentile(yy, 20)) & (yy < np.percentile(yy, 85))
                skins.append(np.median(patch[keep], 0))
            # grey world on mid tones
            flat = D.reshape(-1, 3)
            yy = luma709(flat)
            m = (yy > 0.08) & (yy < 1.6)
            greys.append(flat[m].mean(0))
        g = np.mean(greys, 0)
        rec = dict(grey=g.tolist(), n_faces=len(skins))
        if skins:
            s = np.median(skins, 0)
            rec['skin'] = s.tolist()
            ys = float(luma709(s))
            exp = SKIN_TARGET_Y / ys
            # wb: move skin ratios 60% of the way to target, grey-world 0% (rooms are warm by design)
            rg, bg = s[0] / s[1], s[2] / s[1]
            kr = (SKIN_TARGET_RB[0] / rg) ** 0.5
            kb = (SKIN_TARGET_RB[1] / bg) ** 0.5
        else:
            exp, kr, kb = 1.0, 1.0, 1.0
        exp = float(np.clip(exp, 0.12, 1.6))
        gain = np.array([kr, 1.0, kb]) * exp
        gain = gain / luma709(np.array([kr, 1.0, kb])) * 1.0  # keep luma of the wb at 1
        rec['gain'] = gain.tolist()
        rec['exp'] = exp
        out[c] = rec
        print(c, 'faces', len(skins), 'exp %.3f' % exp, 'gain', np.round(gain, 3), 'skin', np.round(rec.get('skin', [0, 0, 0]), 3))
    json.dump(out, open(os.path.join(GD, 'balance.json'), 'w'), indent=1)


def clip_gain(c):
    bal = json.load(open(os.path.join(GD, 'balance.json')))
    over = {}
    po = os.path.join(os.path.dirname(__file__), 'grade_overrides.json')
    if os.path.exists(po):
        over = json.load(open(po))
    g = np.array(bal[c]['gain'], np.float64)
    o = over.get(c, {})
    g = g * np.array(o.get('mul', [1, 1, 1])) * (2 ** o.get('ev', 0.0))
    return g


def write_cube(path, fn, n=33):
    lin = np.linspace(0, 1, n, dtype=np.float32)
    b, g, r = np.meshgrid(lin, lin, lin, indexing='ij')  # r fastest
    src = np.stack([r, g, b], -1).reshape(-1, 3)
    out = fn(src)
    with open(path, 'w') as f:
        f.write(f'TITLE "BISP look"\nLUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        np.savetxt(f, out, fmt='%.6f')


def luts():
    bal = json.load(open(os.path.join(GD, 'balance.json')))
    for c in bal:
        g = clip_gain(c)
        write_cube(os.path.join(GD, c + '.cube'), lambda s: look(hlg_to_display(s), g))
        print('lut', c, np.round(g, 3))


def preview():
    bal = json.load(open(os.path.join(GD, 'balance.json')))
    rows = []
    for c in bal:
        p = sorted(glob.glob(os.path.join(WS, 'probe', c + '_*.png')))[2]
        E = load_probe(p)
        naive = np.clip(E, 0, 1)  # HLG shown as if SDR (what a straight conversion looks like)
        flat = look(hlg_to_display(E), (1, 1, 1))
        graded = look(hlg_to_display(E), clip_gain(c))
        row = np.concatenate([naive, flat, graded], 1)
        row = (row * 255).astype(np.uint8)
        cv2.putText(row, c, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        rows.append(row)
    half = (len(rows) + 1) // 2
    a = np.concatenate(rows[:half], 0)
    b = np.concatenate(rows[half:] + [np.zeros_like(rows[0])] * (half * 2 - len(rows)), 0)
    sheet = np.concatenate([a, b], 1)
    cv2.imwrite(os.path.join(GD, 'preview.jpg'), sheet[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
    print('preview', sheet.shape)


if __name__ == '__main__':
    {'measure': measure, 'luts': luts, 'preview': preview}[sys.argv[1]]()
