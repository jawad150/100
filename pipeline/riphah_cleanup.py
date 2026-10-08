"""Remove the passer-by from the box-handover photo (slide 9) with LaMa inpainting.

Usage:
    python3 pipeline/riphah_cleanup.py SRC_DIR

Reads SRC_DIR/IMG_9669.jpg and writes SRC_DIR/IMG_9669_clean.png, which
riphah_photos.py uses for slide 9. Needs onnxruntime and the LaMa ONNX model
(https://huggingface.co/Carve/LaMa-ONNX, lama_fp32.onnx), looked up at
$LAMA_ONNX or ~/.cache/lama/lama_fp32.onnx.
"""
import os
import sys

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps

MODEL = os.environ.get("LAMA_ONNX", os.path.expanduser("~/.cache/lama/lama_fp32.onnx"))

# Outline of the man walking behind the group, in original pixels (3024x4032).
PERSON = [(200, 1647), (313, 1651), (357, 1757), (403, 1800), (424, 1987), (433, 2067), (451, 2200),
          (407, 2237), (384, 2333), (357, 2440), (349, 2473), (253, 2477), (240, 2427), (267, 2333),
          (247, 2233), (160, 2233), (163, 2127), (171, 2027), (149, 1880), (187, 1773), (200, 1733),
          (197, 1673)]
# His shadow on the paving, re-filled in a second pass with the cleaned image as context.
SHADOW = [(120, 2150), (420, 2150), (440, 2520), (110, 2520)]


def lama(sess, im, mask, pad):
    """Inpaint `mask` (uint8, 255 = fill) using a square context `pad` x the hole size."""
    x, y, w, h = cv2.boundingRect(mask)
    side = int(max(w, h) * pad)
    cx, cy = x + w // 2, y + h // 2
    X0 = max(0, min(im.shape[1] - side, cx - side // 2))
    Y0 = max(0, min(im.shape[0] - side, cy - side // 2))
    crop, mc = im[Y0:Y0 + side, X0:X0 + side], mask[Y0:Y0 + side, X0:X0 + side]
    i5 = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    m5 = (cv2.resize(mc, (512, 512), interpolation=cv2.INTER_NEAREST) > 127).astype(np.float32)
    o = sess.run(None, {"image": i5.transpose(2, 0, 1)[None], "mask": m5[None, None]})[0][0]
    fill = cv2.resize(np.clip(o.transpose(1, 2, 0), 0, 255).astype(np.uint8), (side, side),
                      interpolation=cv2.INTER_CUBIC).astype(np.float32)
    soft = cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 3)[..., None]
    out = im.copy()
    out[Y0:Y0 + side, X0:X0 + side] = (crop * (1 - soft) + fill * soft + 0.5).astype(np.uint8)
    return out


def main():
    src_dir = sys.argv[1]
    sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    im = np.asarray(ImageOps.exif_transpose(Image.open(os.path.join(src_dir, "IMG_9669.jpg"))).convert("RGB"))

    person = np.zeros(im.shape[:2], np.uint8)
    cv2.fillPoly(person, [np.array(PERSON, np.int32)], 255)
    person = cv2.dilate(person, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    out = lama(sess, im, person, pad=1.3)

    shadow = np.zeros(im.shape[:2], np.uint8)
    cv2.fillPoly(shadow, [np.array(SHADOW, np.int32)], 255)
    out = lama(sess, out, shadow, pad=2.0)

    dst = os.path.join(src_dir, "IMG_9669_clean.png")
    Image.fromarray(out).save(dst, optimize=False, compress_level=3)
    print(dst)


if __name__ == "__main__":
    main()
