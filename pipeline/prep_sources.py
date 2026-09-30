"""Prepare sources for the reel pipeline.

Expects in $REEL_WORKDIR/src (default ../workspace/src):
  screenrec.mp4      screen recording of the Genjutsu tutorial (1920x1200)
  result_split.mp4   Genjutsu split-screen result (1920x2160, Original on top)
  charsheet.png      character sheet (3840x2160)
  logo.png           Higgsfield logo (lime on black)

Produces: fonts/, frames/res, frames/scr, assets/logo_*.png, logo_contours.json
"""
import os, re, json, subprocess, urllib.request
import numpy as np
import cv2

S = os.environ.get('REEL_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')))
FF = os.environ.get('FFMPEG', 'ffmpeg')


def fonts():
    os.makedirs(S + '/fonts', exist_ok=True)
    url = ('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Anton'
           '&family=Space+Grotesk:wght@500;700&family=Unbounded:wght@600;800;900'
           '&family=JetBrains+Mono:wght@500;700&family=Sora:wght@600;800')
    css = urllib.request.urlopen(url).read().decode()
    for m in re.finditer(r"font-family: '([^']+)';\s*font-style: (\w+);\s*font-weight: (\d+);.*?src: url\(([^)]+)\)", css, re.S):
        fam, _, w, u = m.groups()
        fn = f"{S}/fonts/{fam.replace(' ', '')}-{w}.ttf"
        if not os.path.exists(fn):
            urllib.request.urlretrieve(u, fn)


def frames():
    os.makedirs(S + '/frames/res', exist_ok=True)
    os.makedirs(S + '/frames/scr', exist_ok=True)
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', S + '/src/result_split.mp4', '-q:v', '2',
                    '-start_number', '0', S + '/frames/res/%04d.jpg'], check=True)
    # tutorial segments (start, duration) cropped to the site area (no browser chrome / taskbar)
    for st, d in [('12.0', 3.6), ('18.6', 4.8), ('27.2', 3.0), ('57.4', 2.6), ('61.8', 3.2)]:
        subprocess.run([FF, '-y', '-loglevel', 'error', '-ss', st, '-i', S + '/src/screenrec.mp4', '-t', str(d),
                        '-vf', 'fps=30,crop=1920:958:0:170', '-q:v', '2', '-start_number', '0',
                        f'{S}/frames/scr/s{st}_%03d.jpg'], check=True)


def logo():
    os.makedirs(S + '/assets', exist_ok=True)
    im = cv2.imread(S + '/src/logo.png').astype(np.float32)
    B, G = im[..., 0], im[..., 1]
    m = np.clip((G - B - 40) / 150, 0, 1)
    ys, xs = np.where(m > 0.3)
    crop = m[ys.min() - 6:ys.max() + 7, xs.min() - 6:xs.max() + 7] * 255
    K = 8
    up = cv2.GaussianBlur(cv2.resize(crop, None, fx=K, fy=K, interpolation=cv2.INTER_CUBIC), (0, 0), K * 0.5)
    th = (up > 127).astype(np.uint8) * 255
    H, W = th.shape

    def save(mask, path):
        rgba = np.zeros(mask.shape + (4,), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 2] = 23, 254, 209
        rgba[..., 3] = cv2.GaussianBlur(mask, (0, 0), 1.0)
        cv2.imwrite(path, rgba)
    save(th, S + '/assets/logo_lime.png')
    colsum = (th > 0).sum(axis=0)
    xs_on = np.where(colsum > 0)[0]
    gaps = np.diff(xs_on)
    gi = np.argmax(gaps[:len(gaps) // 3])
    split = (xs_on[gi] + xs_on[gi + 1]) / 2
    mk = th.copy(); mk[:, int(split):] = 0
    yy, xx = np.where(mk > 0)
    save(mk[yy.min():yy.max() + 1, xx.min():xx.max() + 1], S + '/assets/logomark_lime.png')
    cnts, _ = cv2.findContours(th, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cnts:
        if cv2.contourArea(c) < 50:
            continue
        a = cv2.approxPolyDP(c, 1.0, True)[:, 0, :].astype(float)
        out.append({'pts': [[(p[0] - W / 2) / H, -(p[1] - H / 2) / H] for p in a], 'mark': bool(a[:, 0].mean() < split)})
    json.dump({'contours': out, 'aspect': W / H}, open(S + '/logo_contours.json', 'w'))


if __name__ == '__main__':
    fonts()
    logo()
    frames()
    print('sources ready in', S)
