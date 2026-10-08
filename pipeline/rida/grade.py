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
    lum = (c @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    # 1) white balance: the set lighting throws an olive/yellow cast on the walls -> pull those
    #    hues (40-75 deg) most of the way to neutral; skin and the brown skirt (<35 deg) untouched
    cast = (smoothstep(34, 46, h) * (1 - smoothstep(78, 100, h)))[..., None]
    c = c + cast * 0.55 * (lum - c)
    # gentle global cool-down of the warm cast in the whites
    c = c * np.array([0.985, 1.0, 1.03])
    # 2) skin: keep natural, a little more life (+8% chroma) for hue 5-35
    skin = ((smoothstep(2, 10, h) * (1 - smoothstep(30, 38, h))) * smoothstep(0.12, 0.3, s))[..., None]
    lum = (c @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    c = c + skin * 0.16 * (c - lum) + skin * np.array([0.012, 0.0, -0.008])
    # gentle vibrance on everything that isn't already saturated
    lum = (c @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    c = c + (0.10 * (1 - smoothstep(0.25, 0.6, s)))[..., None] * (1 - cast) * (c - lum)
    # 3) tone: brighter, airy mids, soft contrast, lifted (neutral) blacks, rolled-off highlights
    x = np.clip(c, 0, 1)
    x = x ** 0.87
    x = x + 0.10 * (x - 0.5) * (1 - np.abs(2 * x - 1))
    x = 0.028 + x * (1 - 0.028)
    x = np.where(x > 0.85, 0.85 + (x - 0.85) * 0.75, x)
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
