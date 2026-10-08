"""Floret Capitals x World Investor Week 2026 at Riphah: Instagram 4:5 carousel.

Usage:
    python3 pipeline/riphah_photos.py SRC_DIR [OUT_DIR]

SRC_DIR holds the original photos (the Drive folder: IMG_96xx.jpg plus the
exported u*.jpg edits); each slide names its file below. Output (1080x1350),
in posting order:
    post_00_cover.jpg  title card
    post_01..10_*.jpg  photos in the Floret post template: navy band with the
                       Floret + WIW 2026 logos, photo fading into navy, website.

Grading is levelled across the set: every photo goes through the same tone and
colour look, then its exposure is nudged so the faces meter to one target, so
nobody looks brighter or darker from slide to slide.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "riphah", "assets")

W, H = 1080, 1350
NAVY = (8, 18, 28)
ORANGE = (229, 161, 58)
URL = "www.floretcapitals.com"

# Photo window on the template; the photo fades into navy at both ends.
WIN_TOP, WIN_BOT = 150, 1215
FADE_TOP, FADE_BOT = 260, 170

# Matching targets: every photo is pulled to the same white, black point,
# face brightness and skin saturation, so the set reads as one grade.
FACE_TARGET = 0.44             # mean sRGB value of the faces
NEUTRAL_TARGET = (1.01, 1.0, 0.985)  # R:G:B of greys after WB (a touch warm)
BLACK_TARGET = 0.012           # luma at the 0.5th percentile
SKIN_CHROMA_TARGET = 0.235     # mean (max-min) chroma of lit skin (set median ~0.245)

# Per photo (coordinates are in a reference pixel space ref_w wide; the
# original file is any size with the same framing, and is scaled to match):
#   file    original photo in SRC_DIR
#   x0, w   source columns shown across the 1080 px width (sets the scale)
#   y0      source row that lands on the window top (negative when the photo is
#           shorter than the window; the gap is filled by extend())
#   faces   source boxes (x0, y0, x1, y1) metered for levelling
PHOTOS = {
    "1": dict(name="handover", file="IMG_9661.jpg", ref_w=1500, x0=312, w=1188, y0=530,
              faces=[(750, 800, 820, 890), (1010, 810, 1090, 900)]),
    "2": dict(name="souvenir", file="ue5f57ebe.jpg", ref_w=1351, x0=0, w=1240, y0=740,
              faces=[(380, 1000, 470, 1110), (590, 990, 670, 1100), (810, 990, 890, 1110)]),
    "3": dict(name="trading_instruments", file="IMG_9653.jpg", ref_w=2000, x0=110, w=1320, y0=6,
              faces=[(410, 550, 550, 710)]),
    "4": dict(name="floret_intro", file="IMG_9655.jpg", ref_w=2000, x0=150, w=1500, y0=0,
              faces=[(440, 520, 560, 700)]),
    "5": dict(name="group", file="u6c5e1c03.jpg", ref_w=2000, x0=75, w=1900, y0=-225,
              faces=[(770, 680, 820, 750), (910, 660, 970, 740), (1570, 660, 1620, 740)]),
    # Second batch.
    "6": dict(name="margin_trading", file="IMG_9645.jpg", ref_w=1500, x0=0, w=1500, y0=47,
              faces=[(350, 720, 410, 820)]),
    "7": dict(name="classroom", file="IMG_9647.jpg", ref_w=2000, x0=200, w=1521, y0=0,
              faces=[(1530, 390, 1600, 470), (460, 570, 580, 700), (720, 560, 820, 660)]),
    "8": dict(name="presenter", file="u272ba09b.jpg", ref_w=2000, x0=275, w=1300, y0=123,
              faces=[(790, 520, 940, 700)]),
    "9": dict(name="box_handover", file="IMG_9669.jpg", ref_w=1500, x0=20, w=1350, y0=222,
              faces=[(330, 600, 430, 720), (570, 600, 670, 720), (980, 700, 1080, 820)]),
    "10": dict(name="pmex_bag", file="ue0e424ae.jpg", ref_w=1161, x0=0, w=1070, y0=523,
               faces=[(350, 810, 430, 920), (710, 840, 790, 950)]),
}

# Cover background: the group photo at the Riphah gate, full width (the group is
# already centred), cut just below the "Welcome to Riphah" sign so the banners
# are out. It sits under the logo band with the same soft top edge; the title
# panel overlaps from the knees.
COVER = dict(file="u6c5e1c03.jpg", ref_w=1280, x0=0, w=1280, y0=262, top=265, top_fade=150, dim=0.72,
             faces=[(493, 435, 525, 480), (582, 422, 621, 474), (1005, 422, 1037, 474)], panel=(56, 715, 1024, 1075))

# Shared look (same for every photo).
LOOK = dict(highlights=0.5, shadows=0.10, contrast=0.12, clarity=0.06,
            saturation=-0.04, vibrance=0.06, shadow_tint=(-0.010, 0.002, 0.016),
            skin_smooth=0.65)


# ---------------------------------------------------------------- colour

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


def tone(L):
    """Shared tone curve on display-referred luminance (0..1)."""
    L = L + LOOK["shadows"] * 0.88 * L * (1 - L) ** 3
    knee, hl = 0.72, LOOK["highlights"]
    over = np.clip(L - knee, 0, None) / (1 - knee)
    L = np.where(L > knee, knee + (1 - knee) * over ** (1 + hl * 0.9) * (1 - hl * 0.06), L)
    s = np.clip(L, 0, 1)
    return np.clip(s + LOOK["contrast"] * (s - 0.5) * (1 - np.abs(2 * s - 1)) * 1.2, 0, 1)


def grade(src, wb, exposure, sat=1.0):
    lin = srgb_to_lin(src) * np.array(wb, np.float32) * (2 ** exposure)
    a = lin_to_srgb(lin)
    # Same black point for every photo (filtered phone shots come in faded).
    bp = float(np.percentile(luma(a[::6, ::6]), 0.5))
    a = np.clip((a - bp) / (1 - bp), 0, 1) * (1 - BLACK_TARGET) + BLACK_TARGET

    L = luma(a)
    L2 = tone(L)
    detail = L2 - blur(L2, 0.014 * L2.shape[1])
    L2 = np.clip(L2 + LOOK["clarity"] * 1.6 * detail * 4 * L2 * (1 - L2), 0, 1)
    a = np.clip(a * ((L2 + 1e-4) / (L + 1e-4))[..., None], 0, 1)

    L = luma(a)[..., None]
    chroma = a.max(-1, keepdims=True) - a.min(-1, keepdims=True)
    vib = LOOK["vibrance"] * (1 - np.clip(chroma * 1.6, 0, 1))
    a = L + (a - L) * (1 + LOOK["saturation"] + vib) * sat
    # Cool the shadows slightly so the photo sits in the navy template.
    a = a + np.array(LOOK["shadow_tint"], np.float32) * (1 - L) ** 2
    return np.clip(a, 0, 1)


def face_level(a, faces):
    return float(np.mean([a[y0:y1, x0:x1].mean() for x0, y0, x1, y1 in faces]))


def denoise(rgb8):
    """Non-local-means denoise, strength set from the photo's measured noise."""
    gray = cv2.cvtColor(rgb8, cv2.COLOR_RGB2GRAY).astype(np.float32)
    kern = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], np.float32)
    sigma = np.sqrt(np.pi / 2) / 6 * np.abs(cv2.filter2D(gray, -1, kern)).mean()
    h = float(np.clip(sigma * 1.3, 2.0, 6.0))
    out = cv2.fastNlMeansDenoisingColored(rgb8, None, h, h + 2, 7, 21)
    return out, sigma


def auto_wb(src):
    """Gains that bring the photo's near-neutral midtones to NEUTRAL_TARGET."""
    lin = srgb_to_lin(src[::4, ::4])
    L = lin.mean(-1)
    neutral = ((src[::4, ::4].max(-1) - src[::4, ::4].min(-1)) < 0.10) & (L > 0.05) & (L < 0.8)
    m = lin[neutral].mean(0)
    gains = np.array(NEUTRAL_TARGET, np.float32) / (m / m[1])
    return 1 + (gains - 1) * 0.85


def skin_chroma(a, faces):
    vals = []
    for x0, y0, x1, y1 in faces:
        f = a[y0:y1, x0:x1].reshape(-1, 3)
        lit = f[luma(f) > 0.3]
        if len(lit):
            vals.append((lit.max(-1) - lit.min(-1)).mean())
    return float(np.mean(vals)) if vals else SKIN_CHROMA_TARGET


FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def smooth_skin(rgb8, faces, scale=1.0):
    """Soften skin only: a skin-tone mask around each face (listed + detected),
    bilateral-smoothed and blended back partly so natural texture stays."""
    gray = cv2.cvtColor(rgb8, cv2.COLOR_RGB2GRAY)
    found = FACE_CASCADE.detectMultiScale(gray, 1.1, 6, minSize=(int(36 * scale), int(36 * scale)))
    boxes = list(faces) + [(x, y, x + w, y + h) for x, y, w, h in found]

    ycc = cv2.cvtColor(rgb8, cv2.COLOR_RGB2YCrCb)
    skin = ((ycc[..., 0] > 50) & (ycc[..., 1] >= 133) & (ycc[..., 1] <= 178) &
            (ycc[..., 2] >= 77) & (ycc[..., 2] <= 130)).astype(np.float32)
    mask = np.zeros(gray.shape, np.float32)
    H_, W_ = gray.shape
    for x0, y0, x1, y1 in boxes:
        w, h = x1 - x0, y1 - y0
        X0, X1 = max(0, int(x0 - 0.5 * w)), min(W_, int(x1 + 0.5 * w))
        Y0, Y1 = max(0, int(y0 - 0.6 * h)), min(H_, int(y1 + 1.0 * h))
        mask[Y0:Y1, X0:X1] = np.maximum(mask[Y0:Y1, X0:X1], skin[Y0:Y1, X0:X1])
    mask = cv2.GaussianBlur(mask, (0, 0), 4 * scale)

    smooth = cv2.bilateralFilter(rgb8, 0, 24, 5 * scale).astype(np.float32)
    smooth = cv2.bilateralFilter(smooth.astype(np.uint8), 0, 18, 3 * scale).astype(np.float32)
    k = (mask * LOOK["skin_smooth"])[..., None]
    out = rgb8.astype(np.float32) * (1 - k) + smooth * k
    return np.clip(out + 0.5, 0, 255).astype(np.uint8), len(found)


WORK_W = 2 * W  # columns kept while processing: 2x the output, downsized once at the end


def graded_photo(path, p):
    """Load the original, keep the columns the slide uses at up to 2x output
    resolution (never upscaled), denoise, grade to the shared targets and
    smooth skin. Returns the image and its scale (working px per reference px)."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    native = im.width / p["ref_w"]
    F = min(WORK_W / p["w"], native)
    box = [round(v * native) for v in (p["x0"], 0, p["x0"] + p["w"])] + [im.height]
    im = im.crop((box[0], 0, box[2], box[3]))
    im = im.resize((round(p["w"] * F), round(im.height * F / native)), Image.LANCZOS)
    faces = [(round((x0 - p["x0"]) * F), round(y0 * F), round((x1 - p["x0"]) * F), round(y1 * F))
             for x0, y0, x1, y1 in p["faces"]]
    faces = [(max(0, x0), y0, min(im.width, x1), y1) for x0, y0, x1, y1 in faces if x1 > 0 and x0 < im.width]

    rgb8, noise = denoise(np.asarray(im))
    src = rgb8.astype(np.float32) / 255
    wb = auto_wb(src)

    # Meter on a small copy (fast), then grade the full-size image once.
    k = 0.35
    small = cv2.resize(src, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    sfaces = [tuple(round(v * k) for v in f) for f in faces]
    ev, sat = 0.0, 1.0
    for _ in range(6):
        a = grade(small, wb, ev, sat)
        step = np.log2(FACE_TARGET / face_level(a, sfaces)) * 0.9
        sat = float(np.clip(sat * SKIN_CHROMA_TARGET / skin_chroma(a, sfaces), 0.7, 1.25))
        if abs(step) < 0.01:
            break
        ev = float(np.clip(ev + step, -0.7, 0.7))
    a = grade(src, wb, ev, sat)
    out, n_found = smooth_skin((a * 255 + 0.5).astype(np.uint8), faces, scale=F)
    print(f"  {os.path.basename(path)}: {im.width}x{im.height} working, noise {noise:.1f}, "
          f"EV {ev:+.2f}, sat x{sat:.2f}, faces {face_level(a, faces):.3f}, "
          f"skin {skin_chroma(a, faces):.3f}, +{n_found} detected")
    return Image.fromarray(out), F


# ---------------------------------------------------------------- layout

def font(name, size):
    return ImageFont.truetype(os.path.join(ASSETS, name), size)


def logo(name, height):
    im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    im = im.crop(im.split()[3].getbbox())
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def lockup(floret_h, wiw_h, gap, divider_h):
    """Floret mark | WIW 2026 logo, as one transparent image."""
    f, w = logo("floret_logo.png", floret_h), logo("wiw2026_logo_white.png", wiw_h)
    h = max(f.height, w.height, divider_h)
    out = Image.new("RGBA", (f.width + 2 * gap + 2 + w.width, h), (0, 0, 0, 0))
    out.alpha_composite(f, (0, (h - f.height) // 2))
    x = f.width + gap
    ImageDraw.Draw(out).rectangle([x, (h - divider_h) // 2, x + 1, (h + divider_h) // 2],
                                  fill=(255, 255, 255, 110))
    out.alpha_composite(w, (x + 2 + gap, (h - w.height) // 2))
    return out


def smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def center_text(draw, y, text, fnt, fill=(255, 255, 255)):
    l, t, r, b = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((W - (r - l)) / 2 - l, y - t), text, font=fnt, fill=fill)
    return b - t


def extend(big, top):
    """Fill the photo window top to bottom. A photo shorter than the window (the
    wide group shot) is continued with a blurred mirror of its own edges, so
    every slide uses exactly the same fades."""
    a = np.asarray(big, np.float32)
    pad_top, pad_bot = max(0, top - WIN_TOP), max(0, WIN_BOT - (top + a.shape[0]))
    if not pad_top and not pad_bot:
        return big, top
    ext = np.pad(a, ((pad_top, pad_bot), (0, 0), (0, 0)), mode="symmetric")
    soft = np.stack([blur(ext[..., c] / 255, 30) * 255 for c in range(3)], -1)
    rows = np.arange(ext.shape[0], dtype=np.float32)
    inside = smoothstep((rows - pad_top) / 40) * smoothstep((pad_top + a.shape[0] - rows) / 40)
    if not pad_top:
        inside = np.where(rows < a.shape[0] / 2, 1, inside)
    if not pad_bot:
        inside = np.where(rows > a.shape[0] / 2, 1, inside)
    out = soft + (ext - soft) * inside[:, None, None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)), top - pad_top


def post(photo, p, F):
    s = W / photo.width  # photo is the slide's column crop, F px per reference px
    big = photo.resize((W, round(photo.height * s)), Image.LANCZOS)
    big, top = extend(big, WIN_TOP - round(p["y0"] * F * s))

    # Same fades on every slide: the window always spans WIN_TOP..WIN_BOT.
    y = np.arange(H, dtype=np.float32)
    alpha = smoothstep((y - WIN_TOP) / FADE_TOP) * smoothstep((WIN_BOT - y) / FADE_BOT)
    alpha[(y < WIN_TOP) | (y >= WIN_BOT)] = 0

    layer = Image.new("RGB", (W, H), NAVY)
    layer.paste(big, (0, top))
    base = np.full((H, W, 3), NAVY, np.float32)
    out = base + (np.asarray(layer, np.float32) - base) * alpha[:, None, None]
    out += np.random.default_rng(3).normal(0, 0.6, out.shape)  # dither: no banding in the fades
    img = Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))
    img = img.filter(ImageFilter.UnsharpMask(radius=0.9, percent=45, threshold=4))

    img = img.convert("RGBA")
    lk = lockup(floret_h=68, wiw_h=78, gap=32, divider_h=58)
    img.alpha_composite(lk, ((W - lk.width) // 2, 78 - lk.height // 2))
    center_text(ImageDraw.Draw(img), 1250, URL, font("Poppins-Medium.ttf", 29))
    return img.convert("RGB")


def cover(photo, F, c=COVER):
    """Title card: event photo dimmed into navy, frosted title panel, logos."""
    big = photo.crop((0, round(c["y0"] * F), photo.width, photo.height))
    big = big.resize((W, round(big.height * W / photo.width)), Image.LANCZOS)
    a = np.asarray(big, np.float32)
    L = luma(a)[..., None]
    a = (L + (a - L) * 0.85) * c["dim"] + np.array(NAVY, np.float32) * (1 - c["dim"])

    canvas = np.full((H, W, 3), NAVY, np.float32)
    t = c["top"]
    h = min(a.shape[0], H - t)
    y = np.arange(h, dtype=np.float32) + t  # canvas rows
    # Soft top edge, then dissolve into navy behind the title panel.
    top_fade = smoothstep((y - t) / c["top_fade"])
    bot_fade = 1 - smoothstep((y - (c["panel"][1] - 40)) / (t + h - c["panel"][1] + 40))
    canvas[t:t + h] += (a[:h] - canvas[t:t + h]) * (top_fade * bot_fade)[:, None, None]
    canvas += np.random.default_rng(7).normal(0, 1.2, canvas.shape)  # grain, no banding
    img = Image.fromarray(np.clip(canvas + 0.5, 0, 255).astype(np.uint8))

    # Frosted panel: blur what's behind it, then a faint white glass tint.
    px0, py0, px1, py1 = c["panel"]
    pw, ph = px1 - px0, py1 - py0
    img.paste(img.crop((px0, py0, px1, py1)).filter(ImageFilter.GaussianBlur(18)), (px0, py0))
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=26, fill=255)
    tint = np.linspace(0.10, 0.20, pw, dtype=np.float32)[None, :].repeat(ph, 0)
    alpha = (tint * np.asarray(mask, np.float32)).astype(np.uint8)
    glass = Image.new("RGBA", (pw, ph), (255, 255, 255, 0))
    glass.putalpha(Image.fromarray(alpha))
    img = img.convert("RGBA")
    img.alpha_composite(glass, (px0, py0))
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle([px0, py0, px1 - 1, py1 - 1], radius=26,
                                           outline=(255, 255, 255, 36), width=2)
    img.alpha_composite(edge)
    d = ImageDraw.Draw(img)

    # Title, each line fitted to the panel width.
    inner = pw - 96

    def fitted(text, size):
        while d.textlength(text, font=font("Anton-Regular.ttf", size)) > inner:
            size -= 2
        return font("Anton-Regular.ttf", size)

    lines = [("WORLD INVESTOR WEEK 2026", 118, (255, 255, 255), 26),
             ("AT RIPHAH INTERNATIONAL UNIVERSITY", 70, ORANGE, 30),
             ("Invest in Your Future. Protect It Today.", 56, (255, 255, 255), 0)]
    lines = [(t, fitted(t, size), col, gap) for t, size, col, gap in lines]
    heights = [d.textbbox((0, 0), t, font=f)[3] - d.textbbox((0, 0), t, font=f)[1] for t, f, _, _ in lines]
    y = (py0 + py1) / 2 - (sum(heights) + sum(g for *_, g in lines)) / 2
    for (t, f, col, gap), hgt in zip(lines, heights):
        center_text(d, y, t, f, col)
        y += hgt + gap

    lk = lockup(floret_h=68, wiw_h=78, gap=32, divider_h=58)  # same band as the photo slides
    img.alpha_composite(lk, ((W - lk.width) // 2, 78 - lk.height // 2))
    center_text(d, 1250, URL, font("Poppins-Medium.ttf", 29))
    return img.convert("RGB")


def main():
    src_dir = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "riphah")
    os.makedirs(out_dir, exist_ok=True)
    for k, p in PHOTOS.items():
        photo, F = graded_photo(os.path.join(src_dir, p["file"]), p)
        dst = os.path.join(out_dir, f"post_{int(k):02d}_{p['name']}.jpg")
        post(photo, p, F).save(dst, quality=98, subsampling=0, optimize=True)
        print(dst)
    dst = os.path.join(out_dir, "post_00_cover.jpg")
    cover(*graded_photo(os.path.join(src_dir, COVER["file"]), COVER)).save(
        dst, quality=98, subsampling=0, optimize=True)
    print(dst)


if __name__ == "__main__":
    main()
