# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python-headless", "numpy", "pillow"]
# ///
"""Trace the real Hulk Marketing logo PNG into vector paths (assets/logo/logo_paths.json).
Each colour layer (green box/text, black text) becomes canvas Path2D strings in the source's
pixel space, so the film can draw the logo at any size without upscaling blur."""
import json, sys
import cv2, numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert("RGBA")).astype(np.float32)
S = 8
big = cv2.resize(im, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
a = big[..., 3] / 255
rgb = big[..., :3]
lum = rgb.mean(axis=2)
green = ((a > 0.5) & (lum > 90)).astype(np.uint8) * 255
dark = ((a > 0.5) & (lum <= 90)).astype(np.uint8) * 255

def paths(mask):
    mask = cv2.GaussianBlur(mask, (0, 0), S * 0.35)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    d = []
    for c in cs:
        if cv2.contourArea(c) < 4 * S * S:
            continue
        c = cv2.approxPolyDP(c, 0.6, True)[:, 0, :] / S
        d.append("M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in c) + "Z")
    return " ".join(d)

col = rgb[(green > 0)].mean(axis=0) if green.any() else [0, 0, 0]
json.dump({"w": im.shape[1], "h": im.shape[0], "green": paths(green), "dark": paths(dark),
           "green_rgb": [int(v) for v in col]}, open(out, "w"))
print("traced", out, "green colour", [int(v) for v in col])
