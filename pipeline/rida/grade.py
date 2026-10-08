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
    c = np.clip(c, 0, 1)
    h, s, v = rgb2hsv(c)
    w = np.array([0.2126, 0.7152, 0.0722])
    lum = (c @ w)[..., None]
    # 1) white balance: tame (not kill) the olive/yellow cast of the set lighting on the walls
    cast = (smoothstep(36, 48, h) * (1 - smoothstep(78, 100, h)))[..., None]
    c = c + cast * 0.35 * (lum - c)
    # warm daylight balance like the reference
    c = c * np.array([1.025, 1.0, 0.955])
    # 2) skin / warm wardrobe: peachy and alive (+22% chroma, a hair toward orange-red)
    skin = ((smoothstep(2, 10, h) * (1 - smoothstep(32, 40, h))) * smoothstep(0.12, 0.3, s))[..., None]
    lum = (c @ w)[..., None]
    c = c + skin * 0.18 * (c - lum) + skin * np.array([0.012, 0.003, -0.008])
    # 3) vibrance: lift low-saturation colours, leave already-rich ones
    lum = (c @ w)[..., None]
    c = c + (0.14 * (1 - smoothstep(0.25, 0.65, s)))[..., None] * (c - lum)
    # 4) tone: filmic S-curve, clean (not crushed) blacks, soft highlight roll-off
    x = np.clip(c, 0, 1) ** 0.96
    x = x + 0.17 * (x - 0.5) * (1 - np.abs(2 * x - 1) ** 1.1)
    x = 0.012 + x * (1 - 0.012)
    x = np.where(x > 0.82, 0.82 + (x - 0.82) * 0.72, x)
    return np.clip(x, 0, 1)


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
