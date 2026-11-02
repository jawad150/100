"""grp3_common.py: shared screen content for the Nov 2026 Google Ranker Pro clips (grp3_*.py, videos 7-10).

Screen content is built as sRGB float images (0..255, RGB) and keyed into the tracked green screens
(workspace3/grp/<cid>_quads.json, from grp_prep3.py) with grp_base.green_replace / paste_quad.

page(path, w, h, scroll, paint)   a site capture scaled to the screen width, scrolled, with boxes painted out
search_screen(w, h, query, k)     plain search page (no search-engine branding): a box with the query typed to k chars
report_screen(...)                Google Ranker Pro report layouts (Search Console capture / the site's report copy)
key_with_hand(fr, quad, content)  green key that keeps only big foreground blobs (a hand / arm) and replaces thin
                                  generated marks on the green (chart lines, dots, axis text)
"""
import functools
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import grp_base as GB
import grp_kit as G

FONTS = '/home/user/100/workspace3/fonts'
W, H = 1080, 1920

# Zentro's unsourced review badges (flagged in research/client_zentro.md): never shown. Boxes in capture pixels.
ZEN_PAINT = {
    'now_desktop.png': [(100, 628, 500, 690)],                       # '5,000+ Happy Customers, 4.8/5 (2,560+)'
    'laptop-repair_desktop.png': [(748, 586, 870, 626)],             # 'stars, Trusted by thousands'
    'laptop-repair_desktop_full.png': [(748, 586, 870, 626)],
    'mobile-repair_desktop.png': [(748, 586, 870, 626)],
    'mobile-repair_desktop_full.png': [(748, 586, 870, 626)],
    'nav_repair_menu_laptop_desktop.png': [(100, 628, 500, 690)],
    'nav_repair_menu_mobile_desktop.png': [(100, 628, 500, 690)],
}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + '.ttf'), int(size))


@functools.lru_cache(maxsize=24)
def _capture(path, width, paint=()):
    im = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    for (x0, y0, x1, y1) in paint:
        # fill with the colour just left of the box (the card / page background)
        c = np.median(im[y0:y1, max(0, x0 - 6):x0].reshape(-1, 3), axis=0)
        im[y0:y1, x0:x1] = c
    s = width / im.shape[1]
    im = cv2.resize(im, (width, int(round(im.shape[0] * s))), interpolation=cv2.INTER_AREA)
    out = im.astype(np.float32)
    out.setflags(write=False)
    return out


def page(path, w, h, scroll=0.0, paint=()):
    im = _capture(path, w, tuple(paint))
    y = int(round(min(max(scroll, 0), max(im.shape[0] - h, 0))))
    out = im[y:y + h]
    if out.shape[0] < h:
        out = np.concatenate([out, np.full((h - out.shape[0], w, 3), 255, np.float32)], 0)
    return out


def zen_page(name, w, h, scroll=0.0):
    return page(G.site('zentro', name), w, h, scroll, ZEN_PAINT.get(name, ()))


def xfade(a, b, u):
    u = float(np.clip(u, 0, 1))
    if u <= 0:
        return a
    if u >= 1:
        return b
    return a * (1 - u) + b * u


@functools.lru_cache(maxsize=64)
def search_screen(w, h, query, k, caret=True):
    """White page, a rounded search box (magnifier + query typed to k characters). No search-engine logo."""
    ss = 2
    im = Image.new('RGB', (w * ss, h * ss), (255, 255, 255))
    d = ImageDraw.Draw(im)
    bw, bh = int(w * 0.62) * ss, int(h * 0.105) * ss
    x0, y0 = (w * ss - bw) // 2, int(h * 0.36) * ss
    for k2, a in enumerate((40, 26, 14)):
        g = 6 * ss - k2 * 2 * ss
        d.rounded_rectangle([x0 - g, y0 - g + 6 * ss, x0 + bw + g, y0 + bh + g + 6 * ss], radius=bh // 2 + g,
                            fill=(255 - a // 3, 255 - a // 3, 255 - a // 3))
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=bh // 2, fill=(255, 255, 255),
                        outline=(218, 220, 224), width=2 * ss)
    # magnifier
    cx, cy, r = x0 + bh * 0.55, y0 + bh * 0.47, bh * 0.17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(112, 117, 122), width=int(4 * ss))
    d.line([cx + r * 0.7, cy + r * 0.7, cx + r * 1.6, cy + r * 1.6], fill=(112, 117, 122), width=int(5 * ss))
    f = font('Inter-Medium', bh * 0.36)
    txt = query[:k]
    tx = x0 + bh * 1.05
    d.text((tx, y0 + bh / 2), txt, font=f, fill=(32, 33, 36), anchor='lm')
    if caret:
        cxp = tx + d.textlength(txt, font=f) + 3 * ss
        d.line([cxp, y0 + bh * 0.28, cxp, y0 + bh * 0.72], fill=(26, 115, 232), width=3 * ss)
    im = im.resize((w, h), Image.LANCZOS)
    out = np.asarray(im, np.float32)
    out.setflags(write=False)
    return out


def _bbox(quad):
    q = np.float32(quad)
    x0 = int(max(0, np.floor(q[:, 0].min()) - 3))
    y0 = int(max(0, np.floor(q[:, 1].min()) - 3))
    x1 = int(min(W, np.ceil(q[:, 0].max()) + 4))
    y1 = int(min(H, np.ceil(q[:, 1].max()) + 4))
    return x0, y0, x1, y1


def key_with_hand(fr, quad, content, s_min=150, v_min=150, open_px=25, inset=5, **kw):
    """green_replace where everything non-green inside the screen that is NOT part of a big blob (the hand / arm)
    is forced to screen. fr: RGB uint8."""
    x0, y0, x1, y1 = _bbox(quad)
    if x1 <= x0 or y1 <= y0:
        return fr
    sub = cv2.cvtColor(np.ascontiguousarray(fr[y0:y1, x0:x1]), cv2.COLOR_RGB2HSV)
    h, s, v = [sub[..., c].astype(np.int32) for c in range(3)]
    green = (h > 35) & (h < 90) & (s > s_min * 0.55) & (v > v_min * 0.55)
    qm = np.zeros((y1 - y0, x1 - x0), np.uint8)
    cv2.fillConvexPoly(qm, np.int32(np.round(np.float32(quad) - [x0, y0])), 1)
    inner = cv2.erode(qm, np.ones((2 * inset + 1, 2 * inset + 1), np.uint8))
    fg = ((~green) & (qm > 0)).astype(np.uint8)
    hand = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_px, open_px)))
    # keep only blobs that reach the screen's edge region (an arm comes in from outside)
    n, lab, st, _ = cv2.connectedComponentsWithStats(hand, 8)
    keep = np.zeros_like(hand)
    for c in range(1, n):
        if st[c, cv2.CC_STAT_AREA] > 1500:
            keep[lab == c] = 1
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    extra = (inner > 0) & (keep == 0)
    ea = cv2.GaussianBlur(extra.astype(np.float32), (0, 0), 1.0)
    return GB.green_replace(fr, quad, content, extra_alpha=ea, **kw)


# ---------------------------------------------------------------------------------------------- GRP report screens
INK, BODY, ACTION, BLUE, ORANGE, SURF, BORDER = (11, 22, 40), (71, 85, 105), (0, 110, 184), (63, 169, 245), \
    (247, 147, 30), (234, 245, 253), (219, 230, 239)


@functools.lru_cache(maxsize=4)
def grp_logo_rgba(h):
    import grp_brand as B
    lg = B.logo(h)                                  # linear premultiplied RGBA sprite
    a = np.clip(lg[..., 3:4], 1e-6, 1)
    rgb = np.clip(lg[..., :3] / a, 0, 1) ** (1 / 2.2) * 255
    return np.concatenate([rgb, lg[..., 3:4] * 255], 2).astype(np.uint8)


def paste_rgba(im, rgba, x, y):
    pil = Image.fromarray(rgba, 'RGBA')
    im.paste(pil, (int(x), int(y)), pil)


@functools.lru_cache(maxsize=4)
def report_gsc(w, h, domain, png, crop, title='Your monthly report', sub='Google Search Console · last 3 months'):
    """GRP report header bar + a real Search Console capture (crop) below it."""
    ss = 2
    im = Image.new('RGB', (w * ss, h * ss), (246, 248, 251))
    d = ImageDraw.Draw(im)
    hb = int(h * 0.17) * ss
    d.rectangle([0, 0, w * ss, hb], fill=(255, 255, 255))
    d.line([0, hb, w * ss, hb], fill=BORDER, width=2 * ss)
    lg = grp_logo_rgba(int(hb * 0.42))
    paste_rgba(im, lg, 34 * ss, (hb - lg.shape[0]) // 2)
    d.text((w * ss - 34 * ss, hb * 0.40), title, font=font('Inter-Bold', hb * 0.24), fill=INK, anchor='rm')
    d.text((w * ss - 34 * ss, hb * 0.72), domain, font=font('Inter-Medium', hb * 0.16), fill=ACTION, anchor='rm')
    d.text((34 * ss, hb + 34 * ss), sub, font=font('Inter-SemiBold', 30 * ss), fill=BODY, anchor='lm')
    src = Image.open(png).convert('RGB')
    crops = crop if isinstance(crop[0], (tuple, list)) else (crop,)
    tw = w * ss - 68 * ss
    y = hb + 62 * ss
    for cr in crops:
        if len(cr) == 5:                                # (other capture, x, y, w, h)
            pth, x, yy, cw, ch = cr
            cap = Image.open(pth).convert('RGB').crop((x, yy, x + cw, yy + ch))
        else:
            x, yy, cw, ch = cr
            cap = src.crop((x, yy, x + cw, yy + ch))
        th = int(cap.height * tw / cap.width)
        cap = cap.resize((tw, th), Image.LANCZOS)
        d.rounded_rectangle([34 * ss - 2, y - 2, 34 * ss + tw + 2, y + th + 2], radius=10 * ss, outline=BORDER,
                            width=2 * ss)
        im.paste(cap, (34 * ss, y))
        y += th + 26 * ss
    im = im.resize((w, h), Image.LANCZOS)
    out = np.asarray(im, np.float32)
    out.setflags(write=False)
    return out


GRP_REPORT_QS = [('01', 'Are the right people finding you?'), ('02', 'What happens after the click?'),
                 ('03', 'What should change next?')]


@functools.lru_cache(maxsize=8)
def report_questions(w, h, n_on=3, hi=-1):
    """Google Ranker Pro's 'A useful report answers better questions' (googlerankerpro.com/seo-services), as a
    clean report page: header, the three questions as rows, n_on of them shown, row `hi` highlighted."""
    ss = 2
    im = Image.new('RGB', (w * ss, h * ss), (246, 248, 251))
    d = ImageDraw.Draw(im)
    hb = int(h * 0.16) * ss
    d.rectangle([0, 0, w * ss, hb], fill=(255, 255, 255))
    d.line([0, hb, w * ss, hb], fill=BORDER, width=2 * ss)
    lg = grp_logo_rgba(int(hb * 0.46))
    paste_rgba(im, lg, 40 * ss, (hb - lg.shape[0]) // 2)
    d.text((w * ss - 40 * ss, hb / 2), 'Monthly review', font=font('Inter-Bold', hb * 0.26), fill=INK, anchor='rm')
    d.text((40 * ss, hb + 70 * ss), 'A useful report answers better questions.', font=font('Inter-Bold', 44 * ss),
           fill=INK, anchor='lm')
    rh = int((h * ss - hb - 140 * ss - 30 * ss) / 3)
    for k, (num, q) in enumerate(GRP_REPORT_QS[:n_on]):
        y = hb + 120 * ss + k * rh
        fill = (255, 255, 255)
        d.rounded_rectangle([40 * ss, y, w * ss - 40 * ss, y + rh - 22 * ss], radius=22 * ss, fill=fill,
                            outline=ACTION if k == hi else BORDER, width=(4 if k == hi else 2) * ss)
        d.rounded_rectangle([64 * ss, y + (rh - 22 * ss) / 2 - 34 * ss, 64 * ss + 68 * ss,
                             y + (rh - 22 * ss) / 2 + 34 * ss], radius=16 * ss,
                            fill=ACTION if k == hi else SURF)
        d.text((98 * ss, y + (rh - 22 * ss) / 2), num, font=font('Inter-Bold', 30 * ss),
               fill=(255, 255, 255) if k == hi else ACTION, anchor='mm')
        d.text((160 * ss, y + (rh - 22 * ss) / 2), q, font=font('Inter-Bold', 40 * ss), fill=INK, anchor='lm')
    im = im.resize((w, h), Image.LANCZOS)
    out = np.asarray(im, np.float32)
    out.setflags(write=False)
    return out


def despill_skin(fr, max_excess=70, r_min=90):
    """Take generated green spill off skin (hand / arm lit by the old green screen): where G sits above R on a
    warm pixel, pull G down to R. Plants (darker, much greener) are left alone. fr: RGB uint8."""
    im = fr.astype(np.int16)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mx = np.maximum(r, b)
    spill = (g > r) & (r > b + 8) & (g - mx < max_excess) & (r > r_min)
    out = fr.copy()
    out[..., 1] = np.where(spill, np.minimum(g, r - 2), g).astype(np.uint8)
    return out


def neutralise_green(fr, y_max, excess=10, keep=0.25):
    """Pull strong green casts (glasses / skin lit by a green screen) toward neutral above row y_max."""
    sub = fr[:y_max].astype(np.int16)
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    mx = np.maximum(r, b)
    over = g - mx
    m = over > excess
    g2 = np.where(m, mx + excess + (over - excess) * keep, g)
    out = fr.copy()
    out[:y_max, :, 1] = np.clip(g2, 0, 255).astype(np.uint8)
    return out


def kill_bright_green(fr, quad, g_min=165, excess=40, keep=10):
    """Very bright, saturated green OUTSIDE the screen quad (spill on an arm crossing the bezel) -> neutral.
    Plant leaves are darker and keep their colour."""
    im = fr.astype(np.int16)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mx = np.maximum(r, b)
    m = (g > g_min) & (g - mx > excess)
    qm = np.zeros(m.shape, np.uint8)
    cv2.fillConvexPoly(qm, np.int32(np.round(quad)), 1)
    m &= qm == 0
    if not m.any():
        return fr
    mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
    out = fr.astype(np.float32)
    tgt = np.minimum(g, mx + keep).astype(np.float32)
    out[..., 1] = out[..., 1] * (1 - mf) + tgt * mf
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)
