"""B-roll grade: Sony S-Log3 / S-Gamut3.Cine -> Rec.709, plus a look matched to the
graded interview (low-key, warm mids, teal-leaning blues, soft highlight roll-off).

All maths on float32 RGB. `grade(rgb, p)` takes S-Log3 code values (0..1, full range,
as the camera records them) and returns display-referred Rec.709 R'G'B' (0..1).
`write_cube()` bakes the same function into a .cube 3D LUT for ffmpeg's lut3d.
"""
import numpy as np

# ---------------------------------------------------------------- technical transform

def slog3_to_linear(x):
    x = np.asarray(x, np.float32)
    hi = (np.power(10.0, (x * 1023.0 - 420.0) / 261.5) * (0.18 + 0.01) - 0.01)
    lo = (x * 1023.0 - 95.0) * 0.01125 / (171.2102946929 - 95.0)
    return np.where(x >= 171.2102946929 / 1023.0, hi, lo).astype(np.float32)


def _rgb_to_xyz(prim, white=(0.3127, 0.3290)):
    xy = np.array(prim, np.float64)
    xyz = np.stack([xy[:, 0] / xy[:, 1], np.ones(3), (1 - xy[:, 0] - xy[:, 1]) / xy[:, 1]], 0)
    wx, wy = white
    W = np.array([wx / wy, 1.0, (1 - wx - wy) / wy])
    S = np.linalg.solve(xyz, W)
    return xyz * S


SGAMUT3_CINE = [(0.766, 0.275), (0.225, 0.800), (0.089, -0.087)]
REC709 = [(0.64, 0.33), (0.30, 0.60), (0.15, 0.06)]
M_SG3C_TO_709 = (np.linalg.inv(_rgb_to_xyz(REC709)) @ _rgb_to_xyz(SGAMUT3_CINE)).astype(np.float32)

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def gamut_compress(lin):
    """Pull out-of-gamut (negative) colours toward their own luma until they fit."""
    m = lin.min(axis=-1, keepdims=True)
    Y = np.maximum((lin @ LUMA)[..., None], 1e-6)
    t = np.where(m < 0, -m / np.maximum(Y - m, 1e-6), 0.0)
    return lin + t * (Y - lin)


# ---------------------------------------------------------------- look

DEFAULT = dict(
    exposure=0.0,          # stops, scene-linear
    wb=(1.0, 1.0, 1.0),    # linear RGB gains (after gamut transform)
    contrast=1.0,          # logistic slope multiplier
    mid=0.36,              # display code value for 18% grey
    black=0.012,           # display floor
    white=0.86,            # display ceiling (soft shoulder)
    sat=0.86,              # global saturation
    blue_teal=0.55,        # how far saturated blues rotate toward teal (0..1)
    blue_sat=0.70,         # extra saturation multiplier on blues
    skin_warm=0.012,       # warm push on skin/orange hues
    shadow_tint=(0.004, -0.004),   # (cb, cr) offsets in shadows: slightly teal
    mid_tint=(-0.016, 0.004),      # mids: warm/yellow like the interview grade
    high_tint=(-0.022, -0.006),    # highlights: warm yellow
)


def tone(lin, p):
    """Film-like characteristic curve in log2 exposure space, per channel."""
    s = np.log2(np.maximum(lin, 1e-5) / 0.18)
    L, H, m = p["black"], p["white"], p["mid"]
    k = 0.52 * p["contrast"]
    # choose offset so that s=0 (18% grey) maps to `mid`
    q = (m - L) / (H - L)
    s0 = np.log(q / (1 - q)) / k
    y = L + (H - L) / (1 + np.exp(-k * (s * 1.0 + s0 * 1.0) * 1.0))
    return y.astype(np.float32)


def ycc(rgb):
    Y = rgb @ LUMA
    cb = (rgb[..., 2] - Y) / 1.8556
    cr = (rgb[..., 0] - Y) / 1.5748
    return Y, cb, cr


def rgb_from_ycc(Y, cb, cr):
    R = Y + 1.5748 * cr
    B = Y + 1.8556 * cb
    G = (Y - 0.2126 * R - 0.0722 * B) / 0.7152
    return np.stack([R, G, B], -1)


def look(rgb, p):
    Y, cb, cr = ycc(rgb)
    # hue-selective: saturated blues -> teal and calmer
    ang = np.arctan2(cr, cb)               # blue ~ -0.2 rad (cb>0, cr slightly <0)
    mag = np.sqrt(cb * cb + cr * cr)
    blue_w = np.exp(-((ang - (-0.35)) / 0.55) ** 2) * np.clip(mag / 0.06, 0, 1)
    rot = -0.38 * p["blue_teal"] * blue_w   # rotate toward cyan (more negative cr)
    ca, sa = np.cos(rot), np.sin(rot)
    cb, cr = cb * ca - cr * sa, cb * sa + cr * ca
    scale = p["sat"] * (1 - blue_w * (1 - p["blue_sat"]))
    cb, cr = cb * scale, cr * scale
    # skin / orange hues (cb<0, cr>0): small warm push
    skin_w = np.exp(-((ang - 2.2) / 0.5) ** 2) * np.clip(mag / 0.03, 0, 1)
    cr = cr + p["skin_warm"] * skin_w
    cb = cb - p["skin_warm"] * 0.6 * skin_w
    # split toning by luma
    ws = np.clip(1 - Y / 0.25, 0, 1) ** 2
    wh = np.clip((Y - 0.45) / 0.4, 0, 1) ** 1.5
    wm = np.clip(1 - ws - wh, 0, 1)
    for (tcb, tcr), w in ((p["shadow_tint"], ws), (p["mid_tint"], wm), (p["high_tint"], wh)):
        cb = cb + tcb * w
        cr = cr + tcr * w
    return rgb_from_ycc(Y, cb, cr)


def grade(code, p=None):
    q = dict(DEFAULT)
    if p:
        q.update(p)
    lin = slog3_to_linear(code)
    lin = lin @ M_SG3C_TO_709.T
    lin = gamut_compress(lin)
    lin = lin * np.float32(2 ** q["exposure"]) * np.array(q["wb"], np.float32)
    disp = tone(lin, q)
    out = look(disp, q)
    return np.clip(out, 0, 1).astype(np.float32)


def write_cube(path, p=None, n=65):
    g = np.linspace(0, 1, n, dtype=np.float32)
    # .cube order: R changes fastest
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")
    code = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = grade(code, p)
    with open(path, "w") as f:
        f.write(f'TITLE "slog3-sgamut3cine-to-709-look"\nLUT_3D_SIZE {n}\n')
        f.write("DOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n")
        np.savetxt(f, out, fmt="%.6f")
