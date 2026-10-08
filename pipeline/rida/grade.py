"""Natural, airy grade matched to the colour reference (clean neutral whites, true warm
skin, soft contrast, slightly lifted shadows, muted sage/olive). Written out as a 3D LUT (.cube)
so the same look can be loaded in After Effects / Premiere / Resolve."""
import sys
import numpy as np


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def rgb2hsv(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(-1), c.min(-1)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 1e-6, (mx - mn) / (mx + 1e-9), 0)
    return h, s, mx


def grade(c):
    """Neutral and natural: skin keeps its original colour, only tone/contrast and the wall cast change."""
    c = np.clip(c, 0, 1)
    h, s, v = rgb2hsv(c)
    w = np.array([0.2126, 0.7152, 0.0722])
    lum = (c @ w)[..., None]
    # 1) tame the olive/yellow cast on the low-saturation walls only (no global white-balance shift)
    cast = (smoothstep(38, 50, h) * (1 - smoothstep(78, 100, h)) * (1 - smoothstep(0.25, 0.45, s)))[..., None]
    c = c + cast * 0.40 * (lum - c)
    # 2) a little life in non-skin colours; skin (hue 0-38) is left exactly as shot
    skin = ((1 - smoothstep(30, 40, h)) + smoothstep(345, 355, h)) * smoothstep(0.08, 0.2, s)
    lum = (c @ w)[..., None]
    c = c + (0.06 * (1 - np.clip(skin, 0, 1)))[..., None] * (c - lum)
    # 3) tone on luminance only (additive), so contrast never shifts hue or skin colour
    L = np.clip(c @ w, 0, 1)
    L2 = L + 0.12 * (L - 0.5) * (1 - np.abs(2 * L - 1) ** 1.1)
    L2 = 0.010 + L2 * (1 - 0.010)
    L2 = np.where(L2 > 0.84, 0.84 + (L2 - 0.84) * 0.75, L2)
    c = c + (L2 - L)[..., None]
    return np.clip(c, 0, 1)


def write_cube(path, n=65):
    g = np.linspace(0, 1, n)
    b, gg, r = np.meshgrid(g, g, g, indexing='ij')  # .cube: red fastest
    c = np.stack([r, gg, b], -1).reshape(-1, 3)
    o = grade(c)
    with open(path, 'w') as f:
        f.write('TITLE "Rida natural reference grade"\nLUT_3D_SIZE %d\n' % n)
        for row in o:
            f.write('%.6f %.6f %.6f\n' % tuple(row))


if __name__ == '__main__':
    write_cube(sys.argv[1] if len(sys.argv) > 1 else 'rida_grade.cube')
