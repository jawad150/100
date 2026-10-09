"""Pack rendered frames into WebP sprite sheets for the site.

Usage: python3 pack.py <work_dir> <out_dir>

Turntables / explode -> one sheet per sequence (8 columns), frames resized to FRAME px.
Shapes and logo -> trimmed single WebP stills.
"""
import os, sys, glob, json
from PIL import Image

work, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
COLS = 8
SMALL = 0.57  # phone sheets: 448 px frames -> 256 px
SEQS = {  # name: frame width (height follows the render aspect)
    "bagel": 448, "croissant": 448, "burger": 448, "finger": 448, "torpedo": 448, "salad": 448, "cup": 448,
    "explode": 400,
}
manifest = {}


def soften_edges(im):
    """The shadow catcher picks up a faint ambient shadow across the whole frame, which
    shows as a box edge. Fade semi-transparent (shadow) pixels out towards the frame edge;
    solid object pixels are left alone."""
    import numpy as np
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    fade = np.clip((0.98 - r) / 0.4, 0, 1)
    alpha = a[..., 3]
    shadow = alpha < 235
    alpha = np.where(shadow, alpha * fade, alpha)
    alpha = np.where(alpha < 4, 0, alpha)
    a[..., 3] = alpha
    return Image.fromarray(a.astype(np.uint8), "RGBA")


for name, fw in SEQS.items():
    frames = sorted(glob.glob(os.path.join(work, name, "*.png")))
    if not frames:
        continue
    first = Image.open(frames[0])
    fh = round(first.height * fw / first.width)
    rows = (len(frames) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (COLS * fw, rows * fh), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        im = soften_edges(Image.open(f).convert("RGBA")).resize((fw, fh), Image.LANCZOS)
        sheet.paste(im, ((i % COLS) * fw, (i // COLS) * fh))
    path = os.path.join(out, f"{name}.webp")
    sheet.save(path, "WEBP", quality=82, method=6)
    # phone variant: same grid at ~57% size, about a third of the decoded memory
    sw, sh = round(fw * SMALL), round(fh * SMALL)
    small = sheet.resize((COLS * sw, rows * sh), Image.LANCZOS)
    small.save(os.path.join(out, f"{name}-sm.webp"), "WEBP", quality=80, method=4)
    # first frame as a light poster for no-JS / early paint
    soften_edges(Image.open(frames[0]).convert("RGBA")).resize((fw, fh), Image.LANCZOS).save(os.path.join(out, f"{name}-poster.webp"), "WEBP", quality=82, method=6)
    manifest[name] = {"frames": len(frames), "cols": COLS, "rows": rows, "w": fw, "h": fh, "sm": [sw, sh]}
    print(name, len(frames), "frames ->", path, os.path.getsize(path) // 1024, "KB")

for f in sorted(glob.glob(os.path.join(work, "shapes", "*.png"))):
    im = Image.open(f).convert("RGBA")
    bbox = im.getchannel("A").point(lambda a: 255 if a > 6 else 0).getbbox()
    if bbox:
        pad = 8
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))
        im = im.crop(bbox)
    name = os.path.splitext(os.path.basename(f))[0]
    path = os.path.join(out, f"{name}.webp")
    im.save(path, "WEBP", quality=86, method=6)
    manifest[name] = {"w": im.width, "h": im.height}
    print(name, im.size, os.path.getsize(path) // 1024, "KB")

range_dir = os.path.join(out, "range")
for f in sorted(glob.glob(os.path.join(work, "range", "*.png"))):
    os.makedirs(range_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(f))[0]
    path = os.path.join(range_dir, f"{name}.webp")
    soften_edges(Image.open(f).convert("RGBA")).save(path, "WEBP", quality=84, method=6)
    print("range", name, os.path.getsize(path) // 1024, "KB")

with open(os.path.join(out, "manifest.json"), "w") as fp:
    json.dump(manifest, fp, indent=1)
# same data as a script, so the page also works opened straight from disk (file://)
with open(os.path.join(out, "manifest.js"), "w") as fp:
    fp.write("window.SPRITE_MANIFEST = " + json.dumps(manifest) + ";\n")
