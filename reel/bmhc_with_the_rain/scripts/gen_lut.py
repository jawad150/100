import numpy as np, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def grade(a, preset):
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    if preset == 'night':
        a = lum + (a - lum) * 0.55
        a = np.clip(a, 0, 1) ** 1.35 * 0.78 * np.array([0.82, 0.95, 1.12])
        hi = np.clip((lum - 0.55) / 0.45, 0, 1)
        a = a * (1 - hi * 0.4) + hi * 0.4 * np.array([1.0, 0.78, 0.48]) * lum
    elif preset == 'deep':
        a = lum + (a - lum) * 0.35
        a = np.clip(a, 0, 1) ** 1.8 * 0.55 * np.array([0.78, 0.92, 1.15])
    elif preset == 'warm':
        a = lum + (a - lum) * 0.9
        a = np.clip(a, 0, 1) ** 1.1 * np.array([1.08, 0.98, 0.86])
    return np.clip(a, 0, 1)
N = 33
r = np.linspace(0, 1, N)
# .cube order: R fastest, then G, then B
bb, gg, rr = np.meshgrid(r, r, r, indexing='ij')
rgb = np.stack([rr, gg, bb], -1).reshape(-1, 3)
for p in ['night', 'deep', 'warm']:
    out = grade(rgb.copy(), p)
    with open(os.path.join(B, 'luts', f'{p}.cube'), 'w') as f:
        f.write(f'TITLE "{p}"\nLUT_3D_SIZE {N}\n')
        for v in out: f.write(f'{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
    print('lut', p)
