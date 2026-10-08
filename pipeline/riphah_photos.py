"""Colour-grade and crop the Riphah x Floret Capitals / PMEX visit photos for
Instagram 4:5 feed posts (1080x1350).

Usage:
    python3 pipeline/riphah_photos.py SRC_DIR [OUT_DIR]

SRC_DIR must hold 1.jpg ... 5.jpg. Output goes to riphah/ by default.

Every photo gets the same finishing look (neutral white balance, recovered
highlights, lifted shadows, gentle S-curve, vibrance, clarity, output
sharpening) after a per-photo correction that brings it to a common baseline,
so the set reads as one carousel.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

W, H = 1080, 1350  # Instagram 4:5 portrait

# Per-photo settings.
#   crop:  (x0, y0, width) in source pixels; height follows from 4:5.
#          None = the whole frame is kept and set on a blurred backdrop.
#   rotate: degrees counter-clockwise to level the frame.
#   wb:    RGB gains to neutralise the cast before the shared look.
#   exposure: stops.  highlights/shadows: -1..1 recovery/lift amounts.
PHOTOS = {
    "1": dict(crop=(90, 0, 1410), rotate=0.0, wb=(0.99, 1.0, 1.03),
              exposure=0.05, highlights=0.45, shadows=0.30, contrast=0.16,
              vibrance=0.18, saturation=0.02),
    "2": dict(crop=(2, 316, 1347), rotate=0.0, wb=(1.0, 1.0, 1.0),
              exposure=-0.08, highlights=0.55, shadows=0.20, contrast=0.08,
              vibrance=0.04, saturation=-0.08),
    "3": dict(crop=(190, 0, 1200), rotate=0.0, wb=(0.94, 1.0, 1.06),
              exposure=0.10, highlights=0.35, shadows=0.25, contrast=0.18,
              vibrance=0.12, saturation=0.0),
    "4": dict(crop=(190, 0, 1200), rotate=0.0, wb=(0.95, 1.0, 1.05),
              exposure=-0.12, highlights=0.55, shadows=0.20, contrast=0.22,
              vibrance=0.12, saturation=0.0),
    "5": dict(crop=None, rotate=0.0, wb=(1.0, 1.0, 1.01),
              exposure=-0.05, highlights=0.55, shadows=0.20, contrast=0.08,
              vibrance=0.04, saturation=-0.06),
}

# Shared finishing look, applied after the per-photo correction.
LOOK = dict(warmth=0.015, clarity=0.22, vignette=0.12, sharpen=0.6)


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def _box(arr, r, axis):
    pad = [(0, 0)] * arr.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(arr, pad, mode="edge"), axis=axis, dtype=np.float64)
    n = arr.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(arr, radius):
    """Approximate Gaussian blur of a float HxW array (three box passes)."""
    r = max(1, int(round(radius * 0.58)))
    for _ in range(3):
        arr = _box(_box(arr, r, 0), r, 1)
    return arr


def tone(L, highlights, shadows, contrast):
    """Tone curve on display-referred luminance (0..1)."""
    # Shadow lift: raise the low end, fading out by the midtones.
    L = L + shadows * 0.22 * L * (1 - L) ** 3 * 4
    # Highlight recovery: compress the top quarter towards a soft shoulder.
    knee = 0.72
    over = np.clip(L - knee, 0, None)
    span = 1 - knee
    L = np.where(L > knee, knee + span * (over / span) ** (1 + highlights * 0.9) *
                 (1 - highlights * 0.06), L)
    # Midtone S-curve around 0.5.
    s = np.clip(L, 0, 1)
    curve = s + contrast * (s - 0.5) * (1 - np.abs(2 * s - 1)) * 1.2
    return np.clip(curve, 0, 1)


def grade(img, p):
    a = np.asarray(img, dtype=np.float32) / 255.0
    lin = srgb_to_lin(a)

    # White balance + exposure in linear light.
    lin = lin * np.array(p["wb"], dtype=np.float32) * (2 ** p["exposure"])
    warm = LOOK["warmth"]
    lin = lin * np.array([1 + warm, 1.0, 1 - warm], dtype=np.float32)
    a = lin_to_srgb(lin)

    # Tone on luminance, applied as a ratio so hue is preserved.
    L = luma(a)
    L2 = tone(L, p["highlights"], p["shadows"], p["contrast"])

    # Clarity: local-contrast boost on luminance, protected at the extremes.
    base = blur(L2, 28)
    detail = L2 - base
    mask = 4 * L2 * (1 - L2)
    L2 = np.clip(L2 + LOOK["clarity"] * detail * mask * 1.6, 0, 1)

    ratio = (L2 + 1e-4) / (L + 1e-4)
    a = np.clip(a * ratio[..., None], 0, 1)
    # Pull any channel that blew past 1 back towards the luminance.
    a = np.clip(a, 0, 1)

    # Vibrance (boosts muted colours more than saturated ones) + saturation.
    L = luma(a)[..., None]
    chroma = a.max(-1, keepdims=True) - a.min(-1, keepdims=True)
    vib = p["vibrance"] * (1 - np.clip(chroma * 1.6, 0, 1))
    a = np.clip(L + (a - L) * (1 + p["saturation"] + vib), 0, 1)
    return a


def vignette(a, amount):
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    v = 1 - amount * np.clip((d - 0.45) / 0.55, 0, 1) ** 2
    return a * v[..., None]


def to_image(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def crop_45(img, box):
    x0, y0, w = box
    h = round(w * 5 / 4)
    if x0 + w > img.width or y0 + h > img.height:
        raise ValueError(f"crop {box} -> {w}x{h} exceeds {img.size}")
    return img.crop((x0, y0, x0 + w, y0 + h))


def backdrop(img):
    """Whole frame centred on a soft, darkened blur of itself (for wide group shots)."""
    bg = ImageOps.fit(img, (W, H), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(60))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (12, 20, 44)), 0.7)
    fw = W
    fh = round(img.height * fw / img.width)
    fg = img.resize((fw, fh), Image.LANCZOS)
    # Soft shadow under the photo so it sits on the backdrop.
    shadow = Image.new("L", (W, H), 0)
    top = (H - fh) // 2
    shadow.paste(140, (0, top + 10, W, top + fh + 10))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    bg = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), bg, shadow)
    bg.paste(fg, (0, top))
    return bg


def process(src, p):
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if p["rotate"]:
        img = img.rotate(p["rotate"], Image.BICUBIC, expand=False)
    graded = to_image(grade(img, p))

    if p["crop"] is not None:
        out = crop_45(graded, p["crop"]).resize((W, H), Image.LANCZOS)
        out = to_image(vignette(np.asarray(out, np.float32) / 255, LOOK["vignette"]))
    else:
        out = backdrop(graded)

    out = out.filter(ImageFilter.UnsharpMask(radius=1.2,
                                             percent=int(LOOK["sharpen"] * 100),
                                             threshold=2))
    return out


def main():
    src_dir = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "riphah"
    os.makedirs(out_dir, exist_ok=True)
    for name, p in PHOTOS.items():
        out = process(os.path.join(src_dir, f"{name}.jpg"), p)
        dst = os.path.join(out_dir, f"riphah_{name}_1080x1350.jpg")
        out.save(dst, quality=95, subsampling=0, optimize=True)
        print(dst, out.size)


if __name__ == "__main__":
    main()
