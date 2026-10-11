"""assets3d_pencil_se_rewind.py - photoreal Blender props for Bijli series #1 "Pencil Se Rewind" (@jawad_mp4).

Builds the render list of brand_reels/design/reels/pencil_se_rewind/SHOTS.md section A with bpy 5.2 / Cycles CPU
(threads 2, adaptive sampling 0.02 + OpenImageDenoise with albedo/normal guides, fixed seed, view transform
Standard, look None, gamma 1) as RGBA 8-bit straight-alpha sRGB PNGs in the shared 3D asset spec:

    RWS = workspace/jawad_reels/pencil_se_rewind
    RWS/assets3d/<name>/passes/0000.png ... + meta.json      (meta.json is written LAST)
    load: S3.Asset3D(name, 'passes', root=RWS + '/assets3d')   -> .frame(i) / .by_label('key') / .features

Props (real dimensions, metres in Blender; modelled once, reused by every render)
----------------------------------------------------------------------------------
    CASSETTE    100.4 x 63.8 x 12 mm; signed-distance shell (surface nets, 0.6 mm rounded edges, hollow 1.2 mm
                walls, hub holes, 5 head openings, label recesses, screw countersinks), smoked amber-brown PS
                (transmission) with a clearer window zone, 5 cross-head screws (rust in the slots), white POM hubs
                with 6 drive teeth, oxide tape packs (radial-tangent anisotropy, banding), tape path, guide rollers,
                felt pressure pad on a phosphor-bronze leaf spring, paper label (fibre bump, generic ruled lines,
                blue ballpoint "Mix '98" / "Side A" / 6 track lines with ink pooling, chai ring, yellowed edge),
                window micro-scratches, 2 fingerprints, dust.
    PENCIL      hex 7.0 mm across flats, 120 mm (cone 13, hex 93 exposed, ferrule 9, eraser 5): rounded arrises,
                5 blade facets on the cone, blunted graphite tip, end-grain cedar, chipped chrome-yellow lacquer
                along the arrises, 4 tooth dents near the ferrule (cracked lacquer), "HB" gold foil 40 % rubbed
                off, crimped brushed-aluminium ferrule with a dent, worn angled eraser with a graphite smudge.
    WALKMAN     110 x 80 x 29 mm generic player: black ABS body (edge-wear shine, scuffs, dust in the gaps),
                brushed-aluminium lid hinged on the left with a smoked window over a CASSETTE, 4 piano keys
                (engraved white-filled stop / play / ff / rew, 3 mm travel), ribbed volume wheel, nickel jack
                with the headphone plug, 2 mm amber LED, sticker residue.
    HEADPHONES  chrome band (140 mm span), black cups, orange open-cell foam pads (one torn), tangled 2 mm cable.
    BATTERIES   2 x AA 50.5 x 14.5 mm, generic red/black sleeve "AA 1.5V", nickel terminals, one tooth-dented.
    TAPE_SPILL  3.81 x 0.05 mm ribbon (oxide front / glossy back), crinkle, accordion section, twist, kinks.
    DESK        900 x 600 x 22 mm sheesham veneer (grain, worn clear coat, compass scratches, blue ink stain,
                dust, pink eraser crumbs), plaster wall 0.9 m behind.

    Light rig LAMP: tungsten spot (2900 K, cone 60, blend 0.4, radius 6 cm) 45 cm above the desk, top-left of
    frame; FLAME rim area 20 x 6 cm back-right 15 cm above the desk; warm world #120A06 x0.35 + a warm bounce
    card front-right. No blue light.

Renders (labels in frame order; all 'passes' folders; see ASSETS.md for features and anchors)
---------------------------------------------------------------------------------------------
    hub_loop      CAM_HUB  16 f loop, pencil + hubs clockwise 22.5 deg/f   1080x1920 opaque
    hub_cover     CAM_HUB  still = hub_loop f0 at high spp                 1080x1920 opaque
    hub_rescue    CAM_HUB  32 f, crinkled tape loop drawn back in          810x1440 opaque
    label         CAM_LABEL still, top-down label + pencil                 1080x1920 opaque
    walkman_loop  CAM_WALK 8 f loop, spools 7.5 deg/f, LED on              1080x1920 opaque
    walkman_keys  CAM_WALK stills play_down / rew_down / stop_down / led_off, cropped to the key row
    walkman_eat   CAM_WALK 32 f, lid springs open, ribbon spills           810x1440 opaque
    pencil_top    ortho top-down, key + shadow                             600x1700 RGBA

CLI
---
    python3 assets3d_pencil_se_rewind.py <name> [<name> ...] [--preview] [--samples N] [--frames 0,8] [--scale K]
    python3 assets3d_pencil_se_rewind.py all [--preview]
    python3 assets3d_pencil_se_rewind.py textures       # (re)build the procedural texture maps only
    python3 assets3d_pencil_se_rewind.py cams           # solve the cameras and print the feature px (no render)
    python3 assets3d_pencil_se_rewind.py sheet          # contact sheet of the finals
    python3 assets3d_pencil_se_rewind.py previewsheet   # the same for the --preview renders
    python3 assets3d_pencil_se_rewind.py pack           # compressed copies into brand_reels/assets/pencil_se_rewind/assets3d

    --preview   16 spp, half resolution, written to RWS/out/preview3d/<name>/passes/ (finals untouched)
    --frames    render only these frame indices (tests; meta.json is not written)
    env PSR_THREADS (default 2), PSR_OUT (default RWS/assets3d). Run every render through tools/heavy.sh.

No brand marks on any prop (generic symbols and handwriting only). Nothing from the toolkit's earlier-client prop
sets is used; assets3d_hero / assets3d_bijli_chali_gayi are imported for engine helpers only (reset, mesher,
shader-graph helper, mesh primitives, meta writer).
"""
import os
import sys
import json
import math
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assets3d_hero as H              # noqa: E402  reset, mesh_field, add_mesh, write_meta
import assets3d_bijli_chali_gayi as B  # noqa: E402  shader-graph helper G, principled, primitives, lights

bpy = None
Vector = None

REEL = 'pencil_se_rewind'
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
RWS = os.path.join(H.WS, REEL)
OUT = os.environ.get('PSR_OUT', os.path.join(RWS, 'assets3d'))
PREVIEW = os.path.join(RWS, 'out', 'preview3d')
SHEETS = os.path.join(RWS, 'out', 'sheets3d')
TEX = os.path.join(RWS, 'out', 'tex3d')
CACHE = os.path.join(RWS, 'out', 'cache3d')
PACK = os.path.join(REPO, 'brand_reels', 'assets', REEL, 'assets3d')
THREADS = int(os.environ.get('PSR_THREADS', '2'))
FONT_HAND = os.path.join(H.FONTS, 'Caveat-Bold.ttf')
FONT_SANS = os.path.join(H.FONTS, 'Poppins-SemiBold.ttf')
MM = 0.001
S_PREVIEW = 16
CROP_PAD = 24

# ============================================================================= palette (sRGB hex; SHOTS.md §A)

TOK = dict(NIGHT_0='#070404', NIGHT_1='#170A07', FLAME='#FF6A1A', AMBER='#FFB547', GOLD='#FF9F1C',
           IVORY='#FFF3E6', ASH='#A8978C',
           SHELL='#3A2618', POM='#E9E4DA', OXIDE='#2B1A10', TAPEBACK='#1E140D', LABEL='#EDE3CF', RULE='#E7A27A',
           INK='#26306E', LACQUER='#E3A21A', CEDAR='#C4915E', ERASER='#D7837C', ABS='#141210', ALU='#B9B4AC',
           LED='#FFB547', FOAM='#E2581B', SLEEVE='#8C1A10', DESK='#4A2A18', WALL='#2A1C14', WORLD='#120A06',
           LAMP='#FFB46B')


def lin(c):
    if isinstance(c, str):
        h = TOK.get(c, c).lstrip('#')
        return tuple(H._s2l(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return tuple(float(x) for x in c[:3])


def mixl(a, b, t):
    a, b = lin(a), lin(b)
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


def srgb8(c):
    h = TOK.get(c, c).lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ============================================================================= cassette layout (metres, cassette local)
#   origin = centre of the body footprint on the desk, +X along the long axis, +Y towards the top edge (away from
#   the head openings), +Z up (side A faces +Z), body z 0 .. 12 mm.

C_HX, C_HY, C_T = 0.0502, 0.0319, 0.012
HUB_X, HUB_Y = 0.021, 0.0025
HUB_HOLE_R = 0.0066
HUB_R_IN, HUB_R_OUT = 0.0040, 0.0109
WIN_HX, WIN_HY = 0.027, 0.007
LAB_X0, LAB_X1, LAB_Y0, LAB_Y1 = -0.0445, 0.0445, -0.0155, 0.0295
LAB_DEPTH = 0.00025
SCREWS = [(-0.0472, 0.0284), (0.0472, 0.0284), (-0.0472, -0.0284), (0.0472, -0.0284), (0.0, -0.0238)]
OPENINGS = [(0.0, 0.0047), (-0.0135, 0.0032), (0.0135, 0.0032), (-0.0245, 0.0016), (0.0245, 0.0016)]
ROLLERS = [(-0.0300, -0.0262), (0.0300, -0.0262)]
LABEL_PX_MM = 40          # label texture resolution (px per mm)

# pencil (pencil local: axis +Z, tip at z = 0; flats face 0, 60, ... deg; the HB facet faces +X)
P_FLAT = 0.0035           # half across flats
P_RC = 0.00032            # arris rounding radius
P_CONE, P_HEX, P_FER, P_ERA = 0.013, 0.093, 0.009, 0.005
P_LEN = P_CONE + P_HEX + P_FER + P_ERA          # 0.120
P_FER_Z0 = P_CONE + P_HEX                       # 0.106
P_ERA_Z0 = P_FER_Z0 + P_FER                     # 0.115
P_SHOULDER_IN_HUB = 0.0052                      # cone shoulder height above the desk when it stands in the hub
DENTS = [(0.0, 0.0985, -0.0007), (0.0, 0.1012, 0.0009), (180.0, 0.0992, 0.0004), (180.0, 0.1018, -0.0010)]

# walkman (walkman local: origin = footprint centre on the desk, +X right, +Y back, +Z up; keys on the front strip)
W_HX, W_HY, W_T = 0.055, 0.040, 0.029
W_LID = dict(x0=-0.0543, x1=0.0543, y0=-0.0283, y1=0.0393, t=0.0016)
W_CASS = (0.0, 0.0055, 0.0150)                  # cassette origin inside the compartment
W_KEYS = ['stop', 'play', 'ff', 'rew']
W_KEY_X = [-0.0330, -0.0170, -0.0010, 0.0150]
W_KEY_Y, W_KEY_W, W_KEY_D, W_KEY_UP = -0.0340, 0.0140, 0.0090, 0.0030
W_LED = (0.0330, -0.0340)
W_WIN = (0.0, HUB_Y + W_CASS[1], 0.031, 0.013)  # lid window centre x, y, half w, half h


# ============================================================================= procedural textures (numpy / cv2 / PIL)

def _tex_path(name):
    return os.path.join(TEX, name)


def _fbm(h, w, scales, seed, amp=0.5):
    """Sum of upsampled random grids (cheap value-noise fBm) in [0, 1]."""
    import cv2
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    a, tot = 1.0, 0.0
    for s in scales:
        g = rng.random((max(2, h // s), max(2, w // s))).astype(np.float32)
        out += a * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += a
        a *= amp
    out /= tot
    return np.clip((out - out.min()) / max(1e-6, out.max() - out.min()), 0, 1)


def _hand_text(draw_img, text, xy_px, size_px, seed, ink_lvl=1.0, slant=0.0):
    """Draw handwriting (Caveat) one glyph at a time with baseline / size / rotation jitter into a float mask."""
    from PIL import Image, ImageDraw, ImageFont
    rng = np.random.default_rng(seed)
    x, y = xy_px
    for ch in text:
        sz = int(size_px * (1.0 + rng.normal(0, 0.035)))
        font = ImageFont.truetype(FONT_HAND, sz)
        bb = font.getbbox(ch)
        cw = max(1, bb[2] - bb[0]) if ch != ' ' else int(sz * 0.28)
        if ch != ' ':
            pad = int(sz * 0.6)
            tile = Image.new('L', (cw + 2 * pad, int(sz * 1.6) + 2 * pad), 0)
            ImageDraw.Draw(tile).text((pad - bb[0], pad), ch, font=font, fill=255)
            tile = tile.rotate(rng.normal(0, 2.5) + slant, resample=Image.BICUBIC, expand=False)
            a = np.asarray(tile, np.float32) / 255.0 * ink_lvl
            yy = int(y + rng.normal(0, size_px * 0.025)) - pad
            xx = int(x) - pad
            h0, w0 = a.shape
            ys0, xs0 = max(0, yy), max(0, xx)
            ys1, xs1 = min(draw_img.shape[0], yy + h0), min(draw_img.shape[1], xx + w0)
            if ys1 > ys0 and xs1 > xs0:
                sub = a[ys0 - yy:ys1 - yy, xs0 - xx:xs1 - xx]
                draw_img[ys0:ys1, xs0:xs1] = np.maximum(draw_img[ys0:ys1, xs0:xs1], sub)
        x += cw * (0.93 + rng.normal(0, 0.03)) + size_px * 0.02
    return x


def _ink_pooling(mask, rng, k=1.0):
    """Ballpoint look: thin the strokes a little, vary the pressure along them, add darker pools at stroke ends
    (end points of the skeleton found by a 3x3 neighbour count) and a few skips."""
    import cv2
    m8 = (mask > 0.5).astype(np.uint8)
    # skeleton (morphological, iterative)
    sk = np.zeros_like(m8)
    img = m8.copy()
    el = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    for _ in range(40):
        er = cv2.erode(img, el)
        op = cv2.dilate(er, el)
        sk |= (img - op).clip(0, 1).astype(np.uint8)
        img = er
        if not img.any():
            break
    nb = cv2.filter2D(sk.astype(np.float32), -1, np.ones((3, 3), np.float32)) - sk
    ends = (sk > 0) & (nb <= 1.0)
    ys, xs = np.nonzero(ends)
    pools = np.zeros(mask.shape, np.float32)
    for y, x in zip(ys, xs):
        if rng.random() < 0.65:
            r = rng.uniform(1.2, 2.4) * k
            cv2.circle(pools, (int(x), int(y)), int(round(r)), 1.0, -1, lineType=cv2.LINE_AA)
    pools = cv2.GaussianBlur(pools, (0, 0), 0.8 * k)
    h, w = mask.shape
    press = 0.72 + 0.28 * _fbm(h, w, (90, 30, 12), int(rng.integers(1e6)))
    skip = (_fbm(h, w, (14, 6), int(rng.integers(1e6))) > 0.86).astype(np.float32) * 0.30
    ink = np.clip(mask * (press - skip), 0, 1)
    ink = np.maximum(ink, np.minimum(pools, 1.0) * np.clip(mask * 4, 0, 1) * 1.0)
    ink = np.maximum(ink, pools * 0.85)
    return np.clip(ink, 0, 1)


def tex_label():
    """Side-A label over the whole cassette face (LABEL_PX_MM px/mm): RGBA (alpha = paper coverage, window and hub
    holes cut out) + a grey 'ink' map (ballpoint density, for roughness / bump)."""
    import cv2
    from PIL import Image, ImageDraw, ImageFont
    k = LABEL_PX_MM
    W, Hh = int(round(2 * C_HX * 1000 * k)), int(round(2 * C_HY * 1000 * k))

    def px(xm, ym):     # cassette local metres -> label px
        return ((xm + C_HX) * 1000 * k, (C_HY - ym) * 1000 * k)

    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    xm = xx / (1000 * k) - C_HX
    ym = C_HY - yy / (1000 * k)
    # coverage: label rect (rounded 1.5 mm) minus the window (rounded rect + hub circles)
    cx, cy = (LAB_X0 + LAB_X1) / 2, (LAB_Y0 + LAB_Y1) / 2
    d_lab = B.sd_rect(xm - cx, ym - cy, (LAB_X1 - LAB_X0) / 2, (LAB_Y1 - LAB_Y0) / 2, 0.0015)
    d_win = B.sd_rect(xm, ym - HUB_Y, WIN_HX, WIN_HY, 0.0035)
    for hx in (-HUB_X, HUB_X):
        d_win = np.minimum(d_win, np.hypot(xm - hx, ym - HUB_Y) - 0.0081)
    d = np.maximum(d_lab, -d_win)
    pxmm = 1.0 / (1000 * k)
    alpha = np.clip(0.5 - d / pxmm, 0, 1)
    # paper: off-white, fibre mottling, yellowed edges, chai ring
    rng = np.random.default_rng(98)
    paper = np.array(srgb8('LABEL'), np.float32)[None, None, :] / 255.0
    mott = _fbm(Hh, W, (400, 120, 40, 12), 3)
    col = np.ones((Hh, W, 3), np.float32) * paper * (0.955 + 0.07 * mott[..., None])
    edge = np.clip(1.0 - (-d) / 0.0022, 0, 1) ** 1.6 * (0.7 + 0.3 * _fbm(Hh, W, (200, 60), 5))
    yellow = np.array([0.80, 0.66, 0.42], np.float32)
    col = col * (1 - 0.42 * edge[..., None]) + yellow * 0.42 * edge[..., None] * paper.max()
    # printed generic layout (RULE colour): border inset 1.2 mm, ruled lines, a boxed "A" side marker
    printed = np.zeros((Hh, W), np.float32)
    pim = Image.new('L', (W, Hh), 0)
    pd = ImageDraw.Draw(pim)
    lw = max(2, int(0.22 * k))
    x0, y0 = px(LAB_X0 + 0.0012, LAB_Y1 - 0.0012)
    x1, y1 = px(LAB_X1 - 0.0012, LAB_Y0 + 0.0012)
    pd.rounded_rectangle([x0, y0, x1, y1], radius=int(1.0 * k), outline=255, width=lw)
    rules_top = [0.0248, 0.0204, 0.0160, 0.0119]     # title line + 3 track lines (y of the baselines)
    rules_bot = [-0.0081, -0.0113, -0.0145]
    for yr in rules_top + rules_bot:
        xa, ya = px(LAB_X0 + 0.0080 if yr == rules_top[0] else LAB_X0 + 0.0030, yr)
        xb, _ = px(LAB_X1 - 0.0030, yr)
        pd.line([xa, ya, xb, ya], fill=200, width=max(2, int(0.16 * k)))
    bx0, by0 = px(LAB_X0 + 0.0022, LAB_Y1 - 0.0022)
    pd.rectangle([bx0, by0, bx0 + 4.4 * k, by0 + 4.4 * k], outline=255, width=lw)
    fA = ImageFont.truetype(FONT_SANS, int(3.8 * k))
    pd.text((bx0 + 2.2 * k, by0 + 2.4 * k), 'A', font=fA, fill=255, anchor='mm')
    printed = np.asarray(pim, np.float32) / 255.0
    rule = np.array(srgb8('RULE'), np.float32) / 255.0
    col = col * (1 - 0.85 * printed[..., None]) + rule * 0.85 * printed[..., None]
    # chai ring (8 %), partly off the label, top-right
    rc = np.hypot(xm - 0.0352, ym - 0.0262)
    ring = np.exp(-((rc - 0.0118) / 0.00045) ** 2) * 0.9 + np.clip(1 - rc / 0.0118, 0, 1) * 0.25
    ring *= 0.55 + 0.45 * _fbm(Hh, W, (300, 80, 20), 9)
    chai = np.array([0.55, 0.36, 0.18], np.float32)
    col = col * (1 - 0.08 * ring[..., None]) + chai * 0.08 * ring[..., None]
    # blue ballpoint handwriting
    ink = np.zeros((Hh, W), np.float32)
    lines = [("Mix '98", 0.0250, LAB_X0 + 0.0090, 4.9, 1.6),
             ('Side A', 0.0250, 0.0190, 4.0, -0.5),
             ('1. barsaat ki raat', 0.0204, LAB_X0 + 0.0078, 3.6, 0.0),
             ('2. dosti - side mix', 0.0160, LAB_X0 + 0.0035, 3.6, 0.6),
             ('3. yaadein (live)', 0.0119, LAB_X0 + 0.0035, 3.6, -0.4),
             ('4. chand raat', -0.0081, LAB_X0 + 0.0035, 3.0, 0.3),
             ('5. safar  6. bas yehi  7. dil', -0.0113, LAB_X0 + 0.0035, 3.0, -0.2)]
    for i, (txt, yb, xs, hmm, sl) in enumerate(lines):
        X0, Yb = px(xs, yb)
        size = hmm * k
        if txt.endswith('7. dil'):
            xpre = _hand_text(np.zeros_like(ink), txt[:-6], (X0, Yb - size * 1.02), size, seed=100 + i, slant=sl)
            XSCRIB = (xpre + 0.0 * k) / (1000 * k) - C_HX
        _hand_text(ink, txt, (X0, Yb - size * 1.02), size, seed=100 + i, slant=sl)
    # a scribbled-out word and a tick mark (real handwriting slips)
    sc = Image.new('L', (W, Hh), 0)
    sd = ImageDraw.Draw(sc)
    sxa, sya = px(XSCRIB, -0.0113 + 0.0017)
    pts = [(sxa + i * 0.45 * k, sya + (0.7 * k if i % 2 else -0.5 * k) + rng.normal(0, 0.12 * k)) for i in range(14)]
    sd.line(pts, fill=255, width=max(2, int(0.30 * k)), joint='curve')
    ink = np.maximum(ink, np.asarray(sc, np.float32) / 255.0 * 0.95)
    ink = cv2.erode(ink, np.ones((2, 2), np.uint8))          # ballpoint, thinner than the font
    ink = _ink_pooling(ink, rng, k / 40.0)
    ink = cv2.GaussianBlur(ink, (0, 0), 0.6)
    inkc = np.array(srgb8('INK'), np.float32) / 255.0
    col = col * (1 - 0.92 * ink[..., None]) + inkc * 0.92 * ink[..., None]
    rgba = np.dstack([np.clip(col, 0, 1), alpha])
    os.makedirs(TEX, exist_ok=True)
    Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), 'RGBA').save(_tex_path('label_a.png'))
    Image.fromarray((ink * 255 + 0.5).astype(np.uint8), 'L').save(_tex_path('label_a_ink.png'))
    # side B: blank paper with the printed layout only
    colb = np.ones((Hh, W, 3), np.float32) * paper * (0.955 + 0.07 * mott[::-1, :, None])
    colb = colb * (1 - 0.85 * printed[..., None]) + rule * 0.85 * printed[..., None]
    Image.fromarray((np.dstack([np.clip(colb, 0, 1), alpha]) * 255 + 0.5).astype(np.uint8), 'RGBA').save(
        _tex_path('label_b.png'))


def tex_wear(size=2048, seed=7, name='wear.png'):
    """Generic wear map (tileable enough at object scale): R = micro-scratches (random short AA lines, a few long
    ones), G = fingerprints (2 elliptical ridge whorls, oily), B = dust specks. Mapped by object coords in shaders."""
    import cv2
    from PIL import Image
    rng = np.random.default_rng(seed)
    S = size
    scr = np.zeros((S, S), np.float32)
    for _ in range(900):
        x, y = rng.uniform(0, S, 2)
        ang = rng.normal(0.3, 0.9)
        ln = rng.lognormal(3.0, 0.6)
        x2, y2 = x + ln * math.cos(ang), y + ln * math.sin(ang)
        cv2.line(scr, (int(x * 4), int(y * 4)), (int(x2 * 4), int(y2 * 4)), float(rng.uniform(0.25, 1.0)), 1,
                 lineType=cv2.LINE_AA, shift=2)
    for _ in range(14):
        x, y = rng.uniform(0, S, 2)
        r = rng.uniform(S * 0.2, S * 0.7)
        a0 = rng.uniform(0, 360)
        cv2.ellipse(scr, (int(x), int(y)), (int(r), int(r)), 0, a0, a0 + rng.uniform(10, 40),
                    float(rng.uniform(0.3, 0.8)), 1, lineType=cv2.LINE_AA)
    fin = np.zeros((S, S), np.float32)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    for (fx, fy, fr, fa) in ((0.30, 0.38, 0.11, 25.0), (0.68, 0.62, 0.09, -40.0)):
        cx, cy = fx * S, fy * S
        ca, sa = math.cos(math.radians(fa)), math.sin(math.radians(fa))
        u = ((xx - cx) * ca + (yy - cy) * sa) / (fr * S)
        v = (-(xx - cx) * sa + (yy - cy) * ca) / (fr * S * 1.35)
        rr = np.sqrt(u * u + v * v)
        warp = _fbm(S, S, (256, 64), int(rng.integers(1e6))) * 0.25
        ridges = 0.5 + 0.5 * np.cos((rr + warp) * 2 * math.pi * 16)
        env = np.clip(1.0 - rr, 0, 1) ** 0.6 * (rr < 1.0)
        fin = np.maximum(fin, ridges * env * (0.6 + 0.4 * _fbm(S, S, (128, 32), int(rng.integers(1e6)))))
    dust = np.zeros((S, S), np.float32)
    for _ in range(2600):
        x, y = rng.uniform(0, S, 2)
        r = rng.lognormal(0.0, 0.5)
        cv2.circle(dust, (int(x * 4), int(y * 4)), int(r * 4), float(rng.uniform(0.4, 1.0)), -1,
                   lineType=cv2.LINE_AA, shift=2)
    for _ in range(40):                                        # fibres
        x, y = rng.uniform(0, S, 2)
        pts = np.cumsum(rng.normal(0, 3, (12, 2)), 0) + [x, y]
        cv2.polylines(dust, [(pts * 4).astype(np.int32)], False, 0.7, 1, lineType=cv2.LINE_AA, shift=2)
    rgb = np.dstack([scr, fin, dust])
    os.makedirs(TEX, exist_ok=True)
    Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB').save(_tex_path(name))


DESK_TEX_M = 0.60          # the desk detail map covers +-0.30 m around the subject


def tex_desk(size=4096, seed=21):
    """Desk detail map over DESK_TEX_M x DESK_TEX_M: R = scratches (compass arcs, pen lines, gouges), G = dust and
    crumb-shadow specks, B = old blue ink stain, A = worn (dull) clear-coat patches."""
    import cv2
    from PIL import Image
    rng = np.random.default_rng(seed)
    S = size
    ppm = S / DESK_TEX_M                    # px per metre

    def P(xm, ym):
        return (int((xm + DESK_TEX_M / 2) * ppm * 4), int((DESK_TEX_M / 2 - ym) * ppm * 4))
    scr = np.zeros((S, S), np.float32)
    for _ in range(26):                     # compass arcs (school geometry boxes)
        cx, cy = rng.uniform(-0.25, 0.25, 2)
        r = rng.uniform(0.02, 0.09)
        a0 = rng.uniform(0, 360)
        c = P(cx, cy)
        cv2.ellipse(scr, c, (int(r * ppm * 4), int(r * ppm * 4)), 0, a0, a0 + rng.uniform(30, 200),
                    float(rng.uniform(0.35, 0.9)), 1, lineType=cv2.LINE_AA, shift=2)
        cv2.circle(scr, c, int(0.0005 * ppm * 4), 1.0, -1, lineType=cv2.LINE_AA, shift=2)   # the pivot hole
    for _ in range(700):                    # light random scratches
        x, y = rng.uniform(-0.3, 0.3, 2)
        ang = rng.uniform(0, math.pi)
        ln = rng.lognormal(-4.2, 0.6)
        cv2.line(scr, P(x, y), P(x + ln * math.cos(ang), y + ln * math.sin(ang)), float(rng.uniform(0.15, 0.6)), 1,
                 lineType=cv2.LINE_AA, shift=2)
    for _ in range(9):                      # deeper gouges
        x, y = rng.uniform(-0.25, 0.25, 2)
        ang = rng.uniform(0, math.pi)
        ln = rng.uniform(0.02, 0.07)
        cv2.line(scr, P(x, y), P(x + ln * math.cos(ang), y + ln * math.sin(ang)), 1.0, 2, lineType=cv2.LINE_AA,
                 shift=2)
    dust = np.zeros((S, S), np.float32)
    for _ in range(9000):
        x, y = rng.uniform(-0.3, 0.3, 2)
        r = rng.lognormal(-9.3, 0.5)            # ~0.05-0.2 mm
        cv2.circle(dust, P(x, y), max(1, int(r * ppm * 4)), float(rng.uniform(0.3, 1.0)), -1,
                   lineType=cv2.LINE_AA, shift=2)
    dust = np.maximum(dust, (_fbm(S, S, (600, 200), 4) > 0.72) * 0.25)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    xm = xx / ppm - DESK_TEX_M / 2
    ym = DESK_TEX_M / 2 - yy / ppm
    blob = _fbm(S, S, (500, 160, 50), 11)
    rr = np.hypot((xm - 0.150) / 1.4, ym + 0.105)
    ink = np.clip((0.034 - rr) / 0.012 + (blob - 0.5) * 1.6, 0, 1)
    ink = np.maximum(ink, np.clip((0.007 - np.hypot(xm - 0.188, ym + 0.082)) / 0.002 + (blob - 0.5), 0, 1))
    ink = cv2.GaussianBlur(ink, (0, 0), 3) * (0.75 + 0.25 * _fbm(S, S, (60, 20), 12))
    worn = _fbm(S, S, (900, 300, 90), 13)
    worn = np.clip((worn - 0.45) / 0.3, 0, 1)
    rgba = np.dstack([scr, dust, ink, worn])
    os.makedirs(TEX, exist_ok=True)
    Image.fromarray((np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(_tex_path('desk.png'))


def tex_hb():
    """'HB' gold-foil mask for one pencil facet, 40 % rubbed off (u along the pencil axis, v across the facet)."""
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    rng = np.random.default_rng(5)
    W, Hh = 960, 240                         # 24 mm x 6 mm at 40 px/mm (u = along the axis)
    im = Image.new('L', (W, Hh), 0)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_SANS, 128)
    d.text((W * 0.5, Hh * 0.52), 'HB', font=f, fill=255, anchor='mm')
    m = np.asarray(im, np.float32) / 255.0
    rub = _fbm(Hh, W, (60, 20, 6), 6)
    rub = np.clip((rub - 0.38) / 0.12, 0, 1)
    streak = _fbm(Hh, W, (4, 2), 7)
    m = m * rub * (0.8 + 0.2 * streak)
    m = cv2.GaussianBlur(m, (0, 0), 0.7)
    Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), 'L').save(_tex_path('hb.png'))


def tex_battery():
    """AA sleeve unwrap (u = around 45.55 mm, v = along 50.5 mm, 24 px/mm): deep red with a black band, white
    'AA 1.5V' and '+' only (generic)."""
    from PIL import Image, ImageDraw, ImageFont
    k = 24
    W, Hh = int(45.55 * k), int(50.5 * k)
    im = Image.new('RGB', (W, Hh), srgb8('SLEEVE'))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(Hh * 0.70), W, int(Hh * 0.80)], fill=(14, 12, 12))     # black band near the '-' end? (v=0 is +)
    d.rectangle([0, 0, W, int(1.1 * k)], fill=(150, 146, 140))                  # bare can lip at the + end
    big = ImageFont.truetype(FONT_SANS, int(6.0 * k))
    small = ImageFont.truetype(FONT_SANS, int(3.4 * k))
    txt = Image.new('L', (int(40 * k), int(8 * k)), 0)
    td = ImageDraw.Draw(txt)
    td.text((0, int(0.6 * k)), 'AA', font=big, fill=255)
    td.text((int(15.5 * k), int(2.8 * k)), '1.5V', font=small, fill=255)
    txt = txt.rotate(-90, expand=True)            # runs along the cell
    im.paste((245, 240, 232), (int(W * 0.30), int(Hh * 0.12)), txt)
    d.text((int(W * 0.72), int(Hh * 0.10)), '+', font=big, fill=(245, 240, 232))
    im.save(_tex_path('battery.png'))


def tex_keys():
    """Engraved key symbols (white fill, partly worn), one 14 x 9 mm tile per key at 40 px/mm."""
    from PIL import Image, ImageDraw
    import cv2
    k = 40
    for i, nm in enumerate(W_KEYS):
        W, Hh = int(14 * k), int(9 * k)
        im = Image.new('L', (W, Hh), 0)
        d = ImageDraw.Draw(im)
        cx, cy = W / 2, Hh / 2
        s = 2.1 * k
        if nm == 'stop':
            d.rectangle([cx - s * 0.75, cy - s * 0.75, cx + s * 0.75, cy + s * 0.75], fill=255)
        elif nm == 'play':
            d.polygon([(cx - s * 0.7, cy - s * 0.9), (cx - s * 0.7, cy + s * 0.9), (cx + s * 0.95, cy)], fill=255)
        elif nm == 'ff':
            for o in (-0.85, 0.55):
                d.polygon([(cx + (o - 0.55) * s, cy - s * 0.75), (cx + (o - 0.55) * s, cy + s * 0.75),
                           (cx + (o + 0.75) * s, cy)], fill=255)
        else:
            for o in (0.85, -0.55):
                d.polygon([(cx + (o + 0.55) * s, cy - s * 0.75), (cx + (o + 0.55) * s, cy + s * 0.75),
                           (cx + (o - 0.75) * s, cy)], fill=255)
        m = np.asarray(im, np.float32) / 255.0
        wear = _fbm(Hh, W, (30, 10, 4), 40 + i)
        fill = m * np.clip((wear - 0.22) / 0.2, 0, 1)
        m = cv2.GaussianBlur(m, (0, 0), 0.8)
        Image.fromarray((np.dstack([m, cv2.GaussianBlur(fill, (0, 0), 0.6), np.zeros_like(m)]) * 255).astype(np.uint8),
                        'RGB').save(_tex_path(f'key_{nm}.png'))


def build_textures(force=False):
    os.makedirs(TEX, exist_ok=True)
    jobs = [('label_a.png', tex_label), ('wear.png', tex_wear), ('desk.png', tex_desk), ('hb.png', tex_hb),
            ('battery.png', tex_battery), ('key_rew.png', tex_keys)]
    for fn, job in jobs:
        if force or not os.path.exists(_tex_path(fn)):
            t0 = time.time()
            job()
            print(f'[tex] {fn} {time.time() - t0:.1f}s', flush=True)


# ============================================================================= bpy helpers

def _bpy():
    global bpy, Vector
    if bpy is None:
        B._bpy()
        import bpy as _b
        from mathutils import Vector as _V
        bpy, Vector = _b, _V
    return bpy


def reset(res, samples):
    sc = H.reset(res, samples, 'night')
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = THREADS
    sc.cycles.samples = samples
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.adaptive_min_samples = 0
    sc.cycles.seed = 98
    sc.cycles.use_animated_seed = False
    sc.cycles.use_light_tree = True
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.transparent_max_bounces = 12
    sc.cycles.blur_glossy = 1.0
    sc.cycles.sample_clamp_indirect = 6.0
    sc.cycles.denoising_prefilter = 'ACCURATE'
    sc.render.film_transparent = False
    sc.render.use_persistent_data = True
    sc.render.dither_intensity = 1.0
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new('W_warm')
    sc.world = w
    bg = w.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = lin('WORLD') + (1,)
    bg.inputs['Strength'].default_value = 0.35
    return sc


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o


def parent_to(objs, root):
    for o in objs:
        o.parent = root
    return objs


def sdf_obj(name, fn, lo, hi, step, mat, key):
    f = H.FieldFn(fn, lo, hi)
    os.makedirs(CACHE, exist_ok=True)
    H.CACHE = CACHE
    V, Q, N = H.mesh_field(f, step, cache_key=f'{REEL}:{key}:{step}', verbose=True)
    o = H.add_mesh(name, V, Q, N, mat, icon_frame=False)
    return o, V, Q


def face_centres(V, Q):
    return np.asarray(V)[np.asarray(Q)].mean(1)


def set_face_mats(o, idx, mats):
    me = o.data
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set('material_index', np.asarray(idx, np.int32))


def grid_mesh(name, V3, closed_u=True, mat=None, smooth=True, cap0=None, cap1=None):
    """Quad grid from V3 (nv rings, nu points per ring, 3); closed in u; optional fan caps (apex points)."""
    nv, nu, _ = V3.shape
    V = V3.reshape(-1, 3)
    F = []
    for j in range(nv - 1):
        for i in range(nu if closed_u else nu - 1):
            i2 = (i + 1) % nu
            F.append((j * nu + i, j * nu + i2, (j + 1) * nu + i2, (j + 1) * nu + i))
    extra = []
    if cap0 is not None:
        a = len(V) + len(extra)
        extra.append(cap0)
        F += [(a, (i + 1) % nu, i) for i in range(nu)]
    if cap1 is not None:
        a = len(V) + len(extra)
        extra.append(cap1)
        base = (nv - 1) * nu
        F += [(a, base + i, base + (i + 1) % nu) for i in range(nu)]
    if extra:
        V = np.vstack([V, np.asarray(extra, float)])
    return B.mesh_from(name, V, F, mat, smooth=smooth), V, F


def lathe_mesh(name, prof, seg, mat, disp=None, uv=False, smooth=True):
    """Surface of revolution about Z: prof = [(r, z), ...]; disp(V, theta, j) -> V for dents. Optional UV
    (u = angle / 2pi, v = z) via a seam-split grid."""
    prof = np.asarray(prof, float)
    nseg = seg + (1 if uv else 0)
    a = np.linspace(0, 2 * np.pi, nseg, endpoint=uv)
    V3 = np.stack([np.cos(a)[None, :] * prof[:, 0:1], np.sin(a)[None, :] * prof[:, 0:1],
                   np.repeat(prof[:, 1:2], nseg, 1)], -1)
    if disp is not None:
        V3 = disp(V3, a)
    nv, nu, _ = V3.shape
    V = V3.reshape(-1, 3)
    F = []
    for j in range(nv - 1):
        for i in range(nu if not uv else nu - 1):
            i2 = (i + 1) % nu
            F.append((j * nu + i, j * nu + i2, (j + 1) * nu + i2, (j + 1) * nu + i))
    UV = None
    if uv:
        zz = prof[:, 1]
        UV = np.stack([np.tile(a / (2 * np.pi), nv), np.repeat((zz - zz.min()) / max(1e-9, zz.max() - zz.min()), nu)], -1)
    o = B.mesh_from(name, V, F, mat, uv=UV, smooth=smooth)
    m = o.modifiers.new('weld', 'WELD')
    m.merge_threshold = 1e-7
    return o


def ribbon(name, P, Wd, width, mats, thick=0.00005, Nrm=None):
    """Flat tape ribbon along centreline P (n, 3) with width direction Wd (n, 3); solidified (front material 0,
    back material 1 via the solidify material offset)."""
    P = np.asarray(P, float)
    Wd = np.asarray(Wd, float)
    Wd = Wd / np.maximum(np.linalg.norm(Wd, axis=1, keepdims=True), 1e-12)
    V = np.concatenate([P - Wd * width / 2, P + Wd * width / 2], 0)
    n = len(P)
    F = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    s = np.concatenate([np.zeros(n), np.ones(n)])
    t = np.concatenate([np.arange(n), np.arange(n)]) / max(1, n - 1)
    o = B.mesh_from(name, V, F, None, uv=np.stack([t, s], -1), smooth=True)
    for m in mats:
        o.data.materials.append(m)
    sm = o.modifiers.new('solid', 'SOLIDIFY')
    sm.thickness = thick
    sm.offset = 0.0
    sm.material_offset = 1
    sm.use_even_offset = True
    return o


def img_node(g, fname, vec, noncolor=False, ext='CLIP', interp='Cubic'):
    n = g.n('ShaderNodeTexImage')
    n.image = bpy.data.images.load(_tex_path(fname), check_existing=True)
    n.image.colorspace_settings.name = 'Non-Color' if noncolor else 'sRGB'
    n.extension = ext
    n.interpolation = interp
    if vec is not None:
        g.put(n.inputs['Vector'], vec)
    return n


def obj_uv(g, sx, sy, ox=0.5, oy=0.5, axes=(0, 1)):
    """Object coords -> (x * sx + ox, y * sy + oy, 0) for image lookups."""
    c = g.xyz(g.co('Object'))
    return g.comb(g.m('MULTIPLY_ADD', c[axes[0]], sx, ox), g.m('MULTIPLY_ADD', c[axes[1]], sy, oy), 0.0)


def colour_node(g, c):
    rgb = g.n('ShaderNodeRGB')
    rgb.outputs[0].default_value = tuple(lin(c)) + (1.0,)
    return rgb.outputs[0]


def wear_maps(g, scale=10.0, coord=None, offset=(0.0, 0.0)):
    """The generic wear map (R scratches, G fingerprints, B dust) by object xy (1 / scale metres per tile)."""
    uv = coord if coord is not None else obj_uv(g, scale, scale, offset[0], offset[1])
    n = img_node(g, 'wear.png', uv, noncolor=True, ext='REPEAT', interp='Linear')
    sep = g.n('ShaderNodeSeparateColor')
    g.put(sep.inputs[0], n.outputs['Color'])
    return sep.outputs[0], sep.outputs[1], sep.outputs[2]


def add_dust(g, b, base_sock, dust, amount=0.6, col='#8A7D70'):
    """Mix light dust into a base colour socket and roughen it."""
    k = g.m('MULTIPLY', dust, amount, clamp=True)
    c = g.mix(k, base_sock, colour_node(g, col))
    g.put(b.inputs['Base Color'], c)
    return k


# ============================================================================= materials

MATS = {}


def mat(name):
    if name not in MATS:
        MATS[name] = MAT_BUILDERS[name]()
    return MATS[name]


def m_shell():
    # per-pass tint: two 1.2 mm walls read as the smoked #3A2618 shell over a bright ground
    m, b, g = B.principled('shell_ps', mixl('SHELL', '#B07A4E', 0.55), rough=0.06, ior=1.59, spec=0.5)
    b.inputs['Transmission Weight'].default_value = 0.85
    scr, fin, dust = wear_maps(g, 9.0)
    r = g.m('MULTIPLY_ADD', scr, 0.06, 0.05)
    r = g.m('MULTIPLY_ADD', fin, 0.10, r)
    k = g.m('MULTIPLY', dust, 0.35, clamp=True)
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', k, 0.6, r))
    g.put(b.inputs['Transmission Weight'], g.m('MULTIPLY_ADD', k, -0.8, 0.85))
    x, y, z = g.xyz(g.co('Object'))
    seam = g.mr(g.m('ABSOLUTE', g.m('SUBTRACT', z, C_T / 2)), 0.00016, 0.0, 0.0, 1.0, smooth=True)
    h = g.m('ADD', g.m('MULTIPLY', seam, -1.0), g.m('MULTIPLY', scr, -0.3))
    g.put(b.inputs['Normal'], g.bump(h, 0.25, 0.0001))
    add_dust(g, b, colour_node(g, mixl('SHELL', '#B07A4E', 0.55)), dust, 0.35)
    return m


def m_window():
    m, b, g = B.principled('window_ps', mixl('SHELL', '#F2DCC4', 0.75), rough=0.02, ior=1.59)
    b.inputs['Transmission Weight'].default_value = 0.96
    scr, fin, dust = wear_maps(g, 11.0, offset=(0.2, 0.7))
    r = g.m('MULTIPLY_ADD', scr, 0.10, 0.02)
    r = g.m('MULTIPLY_ADD', fin, 0.14, r)
    k = g.m('MULTIPLY', dust, 0.4, clamp=True)
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', k, 0.6, r))
    g.put(b.inputs['Transmission Weight'], g.m('MULTIPLY_ADD', k, -0.9, 0.96))
    g.put(b.inputs['Normal'], g.bump(g.m('MULTIPLY', scr, -1.0), 0.2, 0.00005))
    add_dust(g, b, colour_node(g, mixl('SHELL', '#F2DCC4', 0.75)), dust, 0.4)
    return m


def m_grip():
    m, b, g = B.principled('grip_ps', mixl('SHELL', '#B07A4E', 0.45), rough=0.30, ior=1.59)
    b.inputs['Transmission Weight'].default_value = 0.6
    x, y, z = g.xyz(g.co('Object'))
    rib = g.m('SINE', g.m('MULTIPLY', y, 2 * math.pi / 0.0009))
    g.put(b.inputs['Normal'], g.bump(rib, 0.5, 0.00008))
    return m


def m_pom():
    m, b, g = B.principled('hub_pom', lin('POM'), rough=0.45, sss=0.03, sss_radius=(1.0, 0.9, 0.8), sss_scale=0.002)
    scr, fin, dust = wear_maps(g, 30.0, offset=(0.3, 0.1))
    base = g.vscale(colour_node(g, 'POM'), g.m('MULTIPLY_ADD', g.noise(g.co('Object'), 900.0, 2.0), 0.08, 0.94))
    add_dust(g, b, base, dust, 0.3, '#6E625A')
    g.put(b.inputs['Normal'], g.bump(g.noise(g.co('Object'), 3000.0, 2.0), 0.08, 0.00003))
    return m


def m_oxide():
    m, b, g = B.principled('tape_oxide', lin('OXIDE'), rough=0.22, aniso=0.85, spec=0.6)
    tg = g.n('ShaderNodeTangent', direction_type='RADIAL', axis='Z')
    g.put(b.inputs['Tangent'], tg.outputs[0])
    x, y, z = g.xyz(g.co('Object'))
    r = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', y, y)))
    th = g.m('ARCTAN2', y, x)
    c6 = g.m('MULTIPLY', g.m('COSINE', g.m('MULTIPLY', th, 6.0)), 0.25)
    s6 = g.m('MULTIPLY', g.m('SINE', g.m('MULTIPLY', th, 6.0)), 0.25)
    band = g.noise(g.comb(g.m('MULTIPLY', r, 2600.0), c6, s6), 1.0, 3.0, 0.6)
    fine = g.noise(g.comb(g.m('MULTIPLY', r, 22000.0), c6, s6), 1.0, 2.0, 0.5)
    k = g.m('MULTIPLY_ADD', g.m('SUBTRACT', band, 0.5), 0.32, 1.0)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', fine, 0.10, 0.95))
    g.put(b.inputs['Base Color'], g.vscale(colour_node(g, 'OXIDE'), k))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', band, 0.10, 0.17))
    return m


def m_tape_front():
    m, b, g = B.principled('tape_front', lin('OXIDE'), rough=0.35, spec=0.5)
    return m


def m_tape_back():
    m, b, g = B.principled('tape_back', lin('TAPEBACK'), rough=0.30, spec=0.6)
    return m


def m_tape_stretched():
    m, b, g = B.principled('tape_stretched', mixl('OXIDE', '#6B4A30', 0.6), rough=0.4)
    b.inputs['Transmission Weight'].default_value = 0.25
    return m


def m_steel():
    m, b, g = B.principled('screw_steel', (0.55, 0.54, 0.52), rough=0.30, metal=1.0)
    x, y, z = g.xyz(g.co('Object'))
    slot = g.m('MAXIMUM', g.mr(g.m('ABSOLUTE', x), 0.00026, 0.00014, 0.0, 1.0),
               g.mr(g.m('ABSOLUTE', y), 0.00026, 0.00014, 0.0, 1.0))
    deep = g.mr(z, -0.00012, -0.00030, 0.0, 1.0)
    rr = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', y, y)))
    rim = g.mr(rr, 0.00105, 0.00125, 0.0, 0.6)
    n = g.noise(g.co('Object'), 6000.0, 3.0, 0.6)
    rust = g.m('MULTIPLY', g.m('MAXIMUM', g.m('MULTIPLY', slot, deep), rim), g.mr(n, 0.3, 0.6, 0.3, 1.0), clamp=True)
    g.put(b.inputs['Base Color'], g.mix(rust, (0.55, 0.54, 0.52), (0.20, 0.07, 0.025)))
    g.put(b.inputs['Metallic'], g.m('MULTIPLY_ADD', rust, -1.0, 1.0))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', rust, 0.55, 0.28))
    return m


def m_felt():
    m, b, g = B.principled('felt', (0.05, 0.045, 0.04), rough=1.0, sheen=0.8)
    g.put(b.inputs['Normal'], g.bump(g.noise(g.co('Object'), 8000.0, 3.0, 0.7), 0.6, 0.0001))
    return m


def m_bronze():
    m, b, g = B.principled('phosphor_bronze', (0.62, 0.38, 0.18), rough=0.32, metal=1.0)
    return m


def m_label(which='a'):
    m, b, g = B.principled(f'label_{which}', lin('LABEL'), rough=0.82, spec=0.35, sss=0.08,
                           sss_radius=(1.0, 0.9, 0.7), sss_scale=0.0008)
    b.inputs['Sheen Weight'].default_value = 0.15
    uv = obj_uv(g, 1.0 / (2 * C_HX), 1.0 / (2 * C_HY))
    im = img_node(g, f'label_{which}.png', uv)
    scr, fin, dust = wear_maps(g, 12.0, offset=(0.6, 0.2))
    add_dust(g, b, im.outputs['Color'], dust, 0.25, '#B8AC9C')
    fib = g.noise(g.co('Object'), 5000.0, 4.0, 0.65)
    h = fib
    if which == 'a':
        ink = img_node(g, 'label_a_ink.png', uv, noncolor=True)
        g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', ink.outputs['Color'], -0.38, 0.82))
        h = g.m('MULTIPLY_ADD', ink.outputs['Color'], -0.6, fib)        # ballpoint grooves in the paper
    g.put(b.inputs['Normal'], g.bump(h, 0.22, 0.00012))
    nt = m.node_tree
    out = nt.nodes['Material Output']
    tr = g.n('ShaderNodeBsdfTransparent')
    mx = g.n('ShaderNodeMixShader')
    g.put(mx.inputs[0], im.outputs['Alpha'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(b.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    m.blend_method = 'HASHED' if hasattr(m, 'blend_method') else None
    return m


def _hex_phi(g):
    """Angular distance to the nearest pencil arris, 0 at a flat centre, 1 at an arris (pencil object coords)."""
    x, y, z = g.xyz(g.co('Object'))
    th = g.m('ARCTAN2', y, x)
    ph = g.m('SUBTRACT', g.m('FLOORED_MODULO', g.m('ADD', th, math.pi / 6), math.pi / 3), math.pi / 6)
    return g.m('DIVIDE', g.m('ABSOLUTE', ph), math.pi / 6), x, y, z


def m_lacquer():
    m, b, g = B.principled('pencil_lacquer', lin('LACQUER'), rough=0.22, coat=0.5, coat_rough=0.12)
    c, x, y, z = _hex_phi(g)
    co = g.co('Object')
    # chips along the arrises: noise along z decides where the lacquer is gone
    nz = g.noise(g.comb(g.m('MULTIPLY', x, 0.2), g.m('MULTIPLY', y, 0.2), g.m('MULTIPLY', z, 1.0)), 900.0, 4.0, 0.65)
    chip_edge = g.mr(c, 0.80, 0.93, 0.0, 1.0, smooth=True)
    chip = g.m('MULTIPLY', chip_edge, g.mr(nz, 0.50, 0.56, 0.0, 1.0, smooth=True))
    small = g.mr(g.noise(co, 5000.0, 2.0, 0.6), 0.70, 0.73, 0.0, 1.0)
    chip = g.m('MAXIMUM', chip, g.m('MULTIPLY', small, g.mr(c, 0.6, 0.9, 0.0, 0.8)))
    # tooth dents: cracked lacquer around them (Voronoi crack lines near the dent rows)
    dz = g.m('MINIMUM', g.m('ABSOLUTE', g.m('SUBTRACT', z, 0.0995)), g.m('ABSOLUTE', g.m('SUBTRACT', z, 0.1015)))
    near = g.mr(dz, 0.0011, 0.0003, 0.0, 1.0, smooth=True)
    near = g.m('MULTIPLY', near, g.mr(g.m('ABSOLUTE', y), 0.0024, 0.0012, 0.0, 1.0, smooth=True))
    vor = g.n('ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE')
    vor.inputs['Scale'].default_value = 2600.0
    g.put(vor.inputs['Vector'], co)
    crack = g.m('MULTIPLY', g.mr(vor.outputs['Distance'], 0.05, 0.0, 0.0, 1.0), near)
    flake = g.m('MULTIPLY', near, g.mr(g.noise(co, 2500.0, 2.0), 0.58, 0.62, 0.0, 1.0))
    chip = g.m('MAXIMUM', chip, flake)
    # HB gold foil on the +X facet (u along z, v along y)
    fu = g.m('MULTIPLY_ADD', z, 1.0 / 0.024, -0.083 / 0.024)
    fv = g.m('MULTIPLY_ADD', y, 1.0 / 0.006, 0.5)
    foil_img = img_node(g, 'hb.png', g.comb(fu, fv, 0.0), noncolor=True)
    onx = g.mr(x, 0.0032, 0.0034, 0.0, 1.0)
    foil = g.m('MULTIPLY', foil_img.outputs['Color'], onx)
    # colour: lacquer, slight dull oxidation/grime, wood where chipped, gold where foiled
    grime = g.noise(co, 120.0, 3.0, 0.6)
    lac = g.vscale(colour_node(g, 'LACQUER'), g.m('MULTIPLY_ADD', grime, 0.12, 0.90))
    wood = g.vscale(colour_node(g, 'CEDAR'), g.m('MULTIPLY_ADD', nz, 0.3, 0.8))
    col = g.mix(chip, lac, wood)
    col = g.mix(crack, col, (0.25, 0.14, 0.03))
    col = g.mix(foil, col, (0.85, 0.62, 0.25))
    g.put(b.inputs['Base Color'], col)
    g.put(b.inputs['Metallic'], foil)
    g.put(b.inputs['Roughness'], g.m('ADD', g.m('MULTIPLY_ADD', chip, 0.5, 0.22), g.m('MULTIPLY', foil, 0.13)))
    g.put(b.inputs['Coat Weight'], g.m('MULTIPLY_ADD', g.m('MAXIMUM', chip, foil), -0.5, 0.5))
    h = g.m('ADD', g.m('MULTIPLY', chip, -1.0), g.m('MULTIPLY', crack, -0.6))
    h = g.m('ADD', h, g.m('MULTIPLY', g.noise(co, 1800.0, 2.0), 0.05))
    g.put(b.inputs['Normal'], g.bump(h, 0.5, 0.00006))
    return m


def m_cedar():
    """Sharpened cone: end-grain cedar with blade chatter; graphite core (r < 1 mm) in the middle."""
    m, b, g = B.principled('pencil_cedar', lin('CEDAR'), rough=0.62, spec=0.4)
    x, y, z = g.xyz(g.co('Object'))
    r = g.m('SQRT', g.m('ADD', g.m('MULTIPLY', x, x), g.m('MULTIPLY', y, y)))
    rings = g.wave(g.comb(g.m('MULTIPLY', x, 1.0), g.m('MULTIPLY', y, 1.0), g.m('MULTIPLY', z, 0.02)), 900.0, 3.0, 2.0,
                   bands='Z')
    grain = g.noise(g.comb(x, y, g.m('MULTIPLY', z, 0.05)), 3500.0, 3.0, 0.6)
    k = g.m('MULTIPLY', g.mr(rings, 0.0, 1.0, 0.82, 1.08), g.m('MULTIPLY_ADD', grain, 0.2, 0.9))
    wood = g.vscale(colour_node(g, 'CEDAR'), k)
    gr = g.mr(r, 0.00104, 0.00096, 0.0, 1.0)
    col = g.mix(gr, wood, (0.035, 0.035, 0.038))
    g.put(b.inputs['Base Color'], col)
    g.put(b.inputs['Metallic'], g.m('MULTIPLY', gr, 0.25))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', gr, -0.27, 0.62))
    chatter = g.wave(g.co('Object'), 1400.0, 1.0, 1.0, bands='Z')
    g.put(b.inputs['Normal'], g.bump(g.m('ADD', g.m('MULTIPLY', grain, 0.6), g.m('MULTIPLY', chatter, 0.25)), 0.35,
                                     0.00005))
    return m


def m_ferrule():
    m, b, g = B.principled('ferrule_alu', (0.80, 0.78, 0.74), rough=0.26, metal=1.0, aniso=0.6)
    tg = g.n('ShaderNodeTangent', direction_type='RADIAL', axis='Z')
    g.put(b.inputs['Tangent'], tg.outputs[0])
    co = g.co('Object')
    ox = g.noise(co, 1500.0, 3.0, 0.6)
    g.put(b.inputs['Base Color'], g.mix(g.mr(ox, 0.5, 0.75, 0.0, 0.5), (0.80, 0.78, 0.74), (0.45, 0.42, 0.38)))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', ox, 0.2, 0.2))
    x, y, z = g.xyz(co)
    brush = g.noise(g.comb(g.m('MULTIPLY', z, 30.0), g.m('MULTIPLY', x, 0.3), g.m('MULTIPLY', y, 0.3)), 600.0, 2.0)
    g.put(b.inputs['Normal'], g.bump(brush, 0.1, 0.00002))
    return m


def m_eraser():
    m, b, g = B.principled('eraser', lin('ERASER'), rough=0.75, spec=0.35, sss=0.1, sss_radius=(1.0, 0.4, 0.3),
                           sss_scale=0.0008)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    top = g.mr(z, P_LEN - 0.0022, P_LEN - 0.0008, 0.0, 1.0, smooth=True)
    smudge = g.m('MULTIPLY', top, g.mr(g.noise(co, 700.0, 3.0, 0.6), 0.35, 0.65, 0.0, 0.85))
    col = g.mix(smudge, colour_node(g, 'ERASER'), (0.10, 0.09, 0.09))
    g.put(b.inputs['Base Color'], col)
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', smudge, -0.2, 0.78))
    g.put(b.inputs['Normal'], g.bump(g.noise(co, 9000.0, 3.0, 0.6), 0.35, 0.00005))
    return m


def m_desk():
    m, b, g = B.principled('desk_sheesham', lin('DESK'), rough=0.45, coat=1.0, coat_rough=0.25, spec=0.5)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    # grain along X: distorted bands, dark sheesham streaks, pores
    warp = g.noise(g.comb(g.m('MULTIPLY', x, 2.0), g.m('MULTIPLY', y, 30.0), z), 3.0, 4.0, 0.6)
    gy = g.m('ADD', y, g.m('MULTIPLY', warp, 0.012))
    bands = g.wave(g.comb(g.m('MULTIPLY', x, 0.05), gy, z), 140.0, 2.0, 3.0, bands='Y')
    streak = g.noise(g.comb(g.m('MULTIPLY', x, 0.6), g.m('MULTIPLY', gy, 18.0), z), 6.0, 5.0, 0.65)
    pores = g.noise(g.comb(g.m('MULTIPLY', x, 0.08), g.m('MULTIPLY', y, 1.0), z), 2500.0, 2.0, 0.6)
    k = g.m('MULTIPLY', g.mr(bands, 0.0, 1.0, 0.75, 1.15), g.mr(streak, 0.35, 0.70, 0.55, 1.15))
    k = g.m('MULTIPLY', k, g.mr(pores, 0.55, 0.75, 1.0, 0.82))
    wood = g.vscale(colour_node(g, 'DESK'), k)
    uv = obj_uv(g, 1.0 / DESK_TEX_M, 1.0 / DESK_TEX_M)
    dm = img_node(g, 'desk.png', uv, noncolor=True, ext='EXTEND', interp='Linear')
    sep = g.n('ShaderNodeSeparateColor')
    g.put(sep.inputs[0], dm.outputs['Color'])
    scr, dust, ink = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    worn = dm.outputs['Alpha']
    col = g.mix(g.m('MULTIPLY', scr, 0.55), wood, (0.32, 0.21, 0.13))
    col = g.mix(g.m('MULTIPLY', ink, 0.9), col, (0.020, 0.025, 0.070))
    col = g.mix(g.m('MULTIPLY', dust, 0.45), col, (0.30, 0.27, 0.24))
    g.put(b.inputs['Base Color'], col)
    cr = g.m('MULTIPLY_ADD', worn, 0.35, 0.25)
    cr = g.m('MAXIMUM', cr, g.m('MULTIPLY', scr, 0.7))
    cr = g.m('MAXIMUM', cr, g.m('MULTIPLY', dust, 0.9))
    g.put(b.inputs['Coat Roughness'], cr)
    g.put(b.inputs['Coat Weight'], g.m('MULTIPLY_ADD', worn, -0.35, 1.0))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', dust, 0.4, 0.5))
    h = g.m('ADD', g.m('MULTIPLY', scr, -0.8), g.m('MULTIPLY', pores, -0.15))
    g.put(b.inputs['Normal'], g.bump(h, 0.35, 0.00015))
    g.put(b.inputs['Coat Normal'], g.bump(g.m('ADD', g.m('MULTIPLY', scr, -0.6),
                                                g.m('MULTIPLY', g.noise(co, 40.0, 3.0, 0.6), 0.2)), 0.25, 0.0002))
    return m


def m_wall():
    m, b, g = B.principled('wall_plaster', lin('WALL'), rough=0.92, spec=0.3)
    co = g.co('Object')
    k = g.m('MULTIPLY_ADD', g.noise(co, 3.0, 4.0, 0.6), 0.35, 0.82)
    g.put(b.inputs['Base Color'], g.vscale(colour_node(g, 'WALL'), k))
    return m


def m_crumb():
    m, b, g = B.principled('eraser_crumb', mixl('ERASER', '#7A6A66', 0.35), rough=0.85, sss=0.1,
                           sss_radius=(1.0, 0.4, 0.3), sss_scale=0.0005)
    co = g.co('Object')
    g.put(b.inputs['Base Color'], g.mix(g.mr(g.noise(co, 3000.0, 3.0), 0.4, 0.7, 0.0, 0.7),
                                        colour_node(g, mixl('ERASER', '#7A6A66', 0.35)), (0.08, 0.07, 0.07)))
    g.put(b.inputs['Normal'], g.bump(g.noise(co, 9000.0, 3.0, 0.6), 0.5, 0.00005))
    return m


def m_abs():
    m, b, g = B.principled('walkman_abs', lin('ABS'), rough=0.45, spec=0.5)
    co = g.co('Object')
    geo = g.n('ShaderNodeNewGeometry')
    edge = g.m('MULTIPLY', g.mr(geo.outputs['Pointiness'], 0.52, 0.60, 0.0, 1.0, smooth=True),
               g.mr(g.noise(co, 600.0, 3.0, 0.6), 0.40, 0.60, 0.3, 1.0))
    scr, fin, dust = wear_maps(g, 8.0, offset=(0.1, 0.4))
    ao = g.n('ShaderNodeAmbientOcclusion', samples=8)
    ao.inputs['Distance'].default_value = 0.0015
    cav = g.mr(ao.outputs['AO'], 0.85, 0.4, 0.0, 1.0)
    dk = g.m('MAXIMUM', g.m('MULTIPLY', cav, 0.8), g.m('MULTIPLY', dust, 0.5))
    base = g.vscale(colour_node(g, 'ABS'), g.m('MULTIPLY_ADD', g.noise(co, 200.0, 2.0), 0.15, 0.92))
    base = g.mix(g.m('MULTIPLY', edge, 0.6), base, (0.035, 0.032, 0.03))
    add_dust(g, b, base, dk, 0.8, '#5A5048')
    r = g.m('MULTIPLY_ADD', edge, -0.25, 0.45)
    r = g.m('MULTIPLY_ADD', fin, -0.15, r)
    r = g.m('MULTIPLY_ADD', scr, 0.2, r)
    g.put(b.inputs['Roughness'], g.m('MAXIMUM', r, g.m('MULTIPLY', dk, 0.9)))
    g.put(b.inputs['Normal'], g.bump(g.m('ADD', g.noise(co, 2500.0, 3.0, 0.6), g.m('MULTIPLY', scr, -0.5)), 0.12,
                                     0.00005))
    return m


def m_alu_lid():
    m, b, g = B.principled('lid_alu', lin('ALU'), rough=0.28, metal=1.0, aniso=0.7)
    co = g.co('Object')
    x, y, z = g.xyz(co)
    tg = g.n('ShaderNodeTangent', direction_type='UV_MAP') if False else None
    brush = g.noise(g.comb(g.m('MULTIPLY', x, 0.02), g.m('MULTIPLY', y, 1.0), z), 9000.0, 2.0, 0.5)
    scr, fin, dust = wear_maps(g, 9.0, offset=(0.45, 0.15))
    # sticker residue (top-right corner of the lid): rough, dull, yellowish, ragged edge
    sx = g.mr(x, 0.031, 0.034, 0.0, 1.0)
    sy = g.mr(y, 0.0245, 0.0215, 0.0, 1.0)
    rag = g.mr(g.noise(co, 900.0, 4.0, 0.6), 0.35, 0.65, 0.0, 1.0)
    st = g.m('MULTIPLY', g.m('MULTIPLY', sx, sy), g.mr(rag, 0.0, 0.5, 0.4, 1.0), clamp=True)
    col = g.vscale(colour_node(g, 'ALU'), g.m('MULTIPLY_ADD', brush, 0.10, 0.93))
    col = g.mix(st, col, (0.42, 0.37, 0.28))
    add_dust(g, b, col, dust, 0.4, '#6E665E')
    g.put(b.inputs['Metallic'], g.m('MULTIPLY_ADD', st, -0.8, 1.0))
    r = g.m('MULTIPLY_ADD', brush, 0.08, 0.24)
    r = g.m('MULTIPLY_ADD', fin, 0.18, r)
    r = g.m('MULTIPLY_ADD', scr, 0.15, r)
    g.put(b.inputs['Roughness'], g.m('MAXIMUM', r, g.m('MULTIPLY', st, 0.75)))
    g.put(b.inputs['Normal'], g.bump(g.m('ADD', g.m('MULTIPLY', brush, 0.4), g.m('MULTIPLY', scr, -0.6)), 0.15,
                                     0.00003))
    tg = g.n('ShaderNodeTangent', direction_type='RADIAL', axis='Y')   # brushed along X (radial about Y)
    g.put(b.inputs['Tangent'], tg.outputs[0])
    return m


def m_smoke_glass():
    m, b, g = B.principled('lid_window', (0.30, 0.20, 0.13), rough=0.03, ior=1.52)
    b.inputs['Transmission Weight'].default_value = 0.92
    scr, fin, dust = wear_maps(g, 13.0, offset=(0.8, 0.5))
    r = g.m('MULTIPLY_ADD', scr, 0.10, 0.03)
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', fin, 0.15, r))
    return m


def m_key(nm):
    m, b, g = B.principled(f'key_{nm}', (0.035, 0.032, 0.030), rough=0.38, spec=0.5)
    uv = obj_uv(g, 1.0 / (W_KEY_W), 1.0 / (W_KEY_D))
    t = img_node(g, f'key_{nm}.png', uv, noncolor=True)
    sep = g.n('ShaderNodeSeparateColor')
    g.put(sep.inputs[0], t.outputs['Color'])
    engr, fill = sep.outputs[0], sep.outputs[1]
    x, y, z = g.xyz(g.co('Object'))
    ontop = g.mr(z, W_KEY_UP - 0.0006, W_KEY_UP - 0.0002, 0.0, 1.0)
    fill = g.m('MULTIPLY', fill, ontop)
    geo = g.n('ShaderNodeNewGeometry')
    edge = g.mr(geo.outputs['Pointiness'], 0.52, 0.6, 0.0, 1.0)
    base = g.mix(g.m('MULTIPLY', edge, 0.5), (0.035, 0.032, 0.030), (0.09, 0.085, 0.08))
    g.put(b.inputs['Base Color'], g.mix(fill, base, (0.80, 0.78, 0.74)))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', fill, 0.4, g.m('MULTIPLY_ADD', edge, -0.15, 0.38)))
    g.put(b.inputs['Normal'], g.bump(g.m('MULTIPLY', g.m('MULTIPLY', engr, ontop), -1.0), 0.6, 0.00008))
    return m


def m_nickel():
    m, b, g = B.principled('nickel', (0.66, 0.62, 0.56), rough=0.22, metal=1.0)
    co = g.co('Object')
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', g.noise(co, 2000.0, 3.0), 0.2, 0.14))
    return m


def m_rubber():
    m, b, g = B.principled('rubber', (0.022, 0.020, 0.019), rough=0.65, spec=0.4)
    g.put(b.inputs['Normal'], g.bump(g.noise(g.co('Object'), 4000.0, 2.0), 0.1, 0.00003))
    return m


def m_led():
    m, b, g = B.principled('led', lin('LED'), rough=0.1, ior=1.5)
    b.inputs['Transmission Weight'].default_value = 0.5
    b.inputs['Emission Color'].default_value = lin('LED') + (1,)
    b.inputs['Emission Strength'].default_value = 6.0
    return m


def m_led_off():
    m, b, g = B.principled('led_off', mixl('LED', '#3A2010', 0.7), rough=0.1, ior=1.5)
    b.inputs['Transmission Weight'].default_value = 0.5
    return m


def m_chrome():
    m, b, g = B.principled('band_chrome', (0.78, 0.77, 0.75), rough=0.10, metal=1.0)
    scr, fin, dust = wear_maps(g, 25.0, offset=(0.2, 0.9))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', scr, 0.25, g.m('MULTIPLY_ADD', fin, 0.1, 0.07)))
    g.put(b.inputs['Normal'], g.bump(g.m('MULTIPLY', scr, -1.0), 0.2, 0.00002))
    return m


def m_cup():
    m, b, g = B.principled('cup_black', (0.025, 0.023, 0.022), rough=0.4)
    scr, fin, dust = wear_maps(g, 20.0, offset=(0.7, 0.3))
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', scr, 0.25, 0.38))
    add_dust(g, b, colour_node(g, '#0A0908'), dust, 0.4, '#5A5048')
    return m


def m_foam():
    m, b, g = B.principled('foam_orange', lin('FOAM'), rough=1.0, spec=0.25, sss=0.2, sss_radius=(1.0, 0.45, 0.2),
                           sss_scale=0.0015)
    b.inputs['Sheen Weight'].default_value = 0.4
    co = g.co('Object')
    vor = g.n('ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE')
    vor.inputs['Scale'].default_value = 2600.0
    g.put(vor.inputs['Vector'], co)
    vor2 = g.n('ShaderNodeTexVoronoi', feature='F1')
    vor2.inputs['Scale'].default_value = 5200.0
    g.put(vor2.inputs['Vector'], co)
    cells = g.mr(vor.outputs['Distance'], 0.0, 0.12, 0.0, 1.0)
    pore = g.m('MULTIPLY', cells, g.mr(vor2.outputs['Distance'], 0.0, 0.5, 0.6, 1.0))
    k = g.m('MULTIPLY_ADD', pore, 0.35, 0.65)
    k = g.m('MULTIPLY', k, g.m('MULTIPLY_ADD', g.noise(co, 80.0, 3.0, 0.6), 0.25, 0.88))
    g.put(b.inputs['Base Color'], g.vscale(colour_node(g, 'FOAM'), k))
    g.put(b.inputs['Normal'], g.bump(pore, 0.9, 0.00025))
    return m


def m_cable():
    m, b, g = B.principled('cable', (0.018, 0.017, 0.016), rough=0.7, spec=0.4)
    return m


def m_sleeve():
    m, b, g = B.principled('aa_sleeve', lin('SLEEVE'), rough=0.62, spec=0.45, coat=0.2, coat_rough=0.3)
    t = img_node(g, 'battery.png', g.uv(), ext='REPEAT')
    scr, fin, dust = wear_maps(g, 30.0, offset=(0.1, 0.6))
    add_dust(g, b, t.outputs['Color'], dust, 0.3, '#7A6E66')
    g.put(b.inputs['Roughness'], g.m('MULTIPLY_ADD', scr, 0.2, 0.55))
    g.put(b.inputs['Normal'], g.bump(g.m('MULTIPLY', scr, -1.0), 0.15, 0.00003))
    return m


MAT_BUILDERS = dict(shell=m_shell, window=m_window, grip=m_grip, pom=m_pom, oxide=m_oxide, tape_front=m_tape_front,
                    tape_back=m_tape_back, tape_stretched=m_tape_stretched, steel=m_steel, felt=m_felt,
                    bronze=m_bronze, label_a=lambda: m_label('a'), label_b=lambda: m_label('b'), lacquer=m_lacquer,
                    cedar=m_cedar, ferrule=m_ferrule, eraser=m_eraser, desk=m_desk, wall=m_wall, crumb=m_crumb,
                    abs=m_abs, alu=m_alu_lid, smoke=m_smoke_glass, nickel=m_nickel, rubber=m_rubber, led=m_led,
                    led_off=m_led_off, chrome=m_chrome, cup=m_cup, foam=m_foam, cable=m_cable, sleeve=m_sleeve,
                    **{f'key_{k}': (lambda k=k: m_key(k)) for k in W_KEYS})


# ============================================================================= CASSETTE

def _cass_shell_fn(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    r = 0.0006
    outer = B.extrude(B.sd_rect(x, y, C_HX, C_HY, 0.0028) + r, np.abs(z - C_T / 2) - C_T / 2 + r) - r
    inner = B.extrude(B.sd_rect(x, y, C_HX - 0.0014, C_HY - 0.0014, 0.0016), np.abs(z - C_T / 2) - (C_T / 2 - 0.0012))
    for sx, sy in SCREWS:
        inner = np.maximum(inner, -(np.hypot(x - sx, y - sy) - 0.0023))
    # internal rib walls framing the tape path behind the head openings (with gaps for the tape)
    rib = B.extrude(B.sd_rect(x, y + 0.0236, 0.017, 0.0005, 0.0002), np.abs(z - C_T / 2) - C_T / 2)
    inner = np.maximum(inner, -rib)
    d = np.maximum(outer, -inner)
    for hx in (-HUB_X, HUB_X):
        d = np.maximum(d, -(np.hypot(x - hx, y - HUB_Y) - HUB_HOLE_R))
    for cx, hw in OPENINGS:
        q = np.stack([x - cx, y + C_HY, z - C_T / 2], -1)
        d = np.maximum(d, -H.sd3_round_box(q, (hw, 0.0042, C_T / 2 - 0.0013), 0.0003))
    lab2 = B.sd_rect(x - (LAB_X0 + LAB_X1) / 2, y - (LAB_Y0 + LAB_Y1) / 2, (LAB_X1 - LAB_X0) / 2 + 0.0003,
                     (LAB_Y1 - LAB_Y0) / 2 + 0.0003, 0.0018)
    for zf in (C_T, 0.0):
        d = np.maximum(d, -B.extrude(lab2, np.abs(z - zf) - LAB_DEPTH))
        for sx, sy in SCREWS:
            d = np.maximum(d, -B.extrude(np.hypot(x - sx, y - sy) - 0.00165, np.abs(z - zf) - 0.0006))
    # two small alignment holes either side of the centre opening
    for ax in (-0.0072, 0.0072):
        d = np.maximum(d, -(np.hypot(x - ax, y + 0.0262) - 0.0011))
    return d


def _hub_fn(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    r = np.hypot(x, y)
    th = np.arctan2(y, x)
    rr = 0.0003
    hh = 0.0032
    ring = B.extrude(np.maximum(r - HUB_R_OUT, HUB_R_IN - r) + rr, np.abs(z - C_T / 2) - hh + rr) - rr
    for zf in (C_T / 2 + hh, C_T / 2 - hh):
        ring = np.maximum(ring, -B.extrude(np.abs(r - 0.0074) - 0.0008, np.abs(z - zf) - 0.0005))
    ph = np.mod(th + np.pi / 6, np.pi / 3) - np.pi / 6
    u, v = r * np.cos(ph), r * np.sin(ph)
    tooth = B.extrude(B.sd_rect(u - 0.0040, v, 0.00052, 0.00055, 0.00018), np.abs(z - C_T / 2) - (hh - 0.0004))
    d = np.minimum(ring, tooth)
    for a in (1.90, 2.20):     # leader-clip slots
        u2, v2 = r * np.cos(th - a), r * np.sin(th - a)
        d = np.maximum(d, -B.sd_rect(u2 - 0.0103, v2, 0.0010, 0.00013, 0.0))
    return d


def _screw_fn(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    r = np.hypot(x, y)
    head = H.sd3_ellipsoid(np.stack([x, y, z + 0.00025], -1), (0.00125, 0.00125, 0.00075))
    head = np.maximum(head, -z - 0.00055)
    slot = np.minimum(B.sd_rect(x, y, 0.0011, 0.00016, 0.00003), B.sd_rect(x, y, 0.00016, 0.0011, 0.00003))
    d = np.maximum(head, -B.extrude(slot, np.abs(z - 0.0003) - 0.0006))
    return d


def tangent_point(C, R, Q, side=1):
    """Tangent point on circle (C, R) from external point Q (2D); side picks one of the two."""
    C, Q = np.asarray(C, float), np.asarray(Q, float)
    d = Q - C
    L = np.linalg.norm(d)
    a = math.acos(min(1.0, R / L))
    b = math.atan2(d[1], d[0])
    t = b + side * a
    return C + R * np.array([math.cos(t), math.sin(t)])


def build_cassette(name='cass', rL=0.017, rR=0.0204, parent=None, q=1.0, inner=True):
    """CASSETTE in cassette local coords under an empty. Returns dict(root, hubL, hubR, objs)."""
    root = empty(name, parent=parent)
    step = 0.00015 if q >= 1 else 0.00024
    lo, hi = (-C_HX - 0.001, -C_HY - 0.001, -0.001), (C_HX + 0.001, C_HY + 0.001, C_T + 0.001)
    shell, V, Q = sdf_obj(f'{name}_shell', _cass_shell_fn, lo, hi, step, None, 'shell2')
    fc = face_centres(V, Q)
    d_win = B.sd_rect(fc[:, 0], fc[:, 1] - HUB_Y, WIN_HX + 0.0005, WIN_HY + 0.0005, 0.0035)
    for hx in (-HUB_X, HUB_X):
        d_win = np.minimum(d_win, np.hypot(fc[:, 0] - hx, fc[:, 1] - HUB_Y) - 0.0085)
    idx = np.zeros(len(fc), np.int32)
    idx[(d_win < 0) & ((fc[:, 2] > C_T - 0.0013) | (fc[:, 2] < 0.0013))] = 1
    idx[np.abs(fc[:, 0]) > C_HX - 0.0009] = 2
    set_face_mats(shell, idx, [mat('shell'), mat('window'), mat('grip')])
    objs = [shell]
    # labels (alpha-cut planes in the recesses)
    for side, zl, mn in (('a', C_T - LAB_DEPTH + 0.00009, 'label_a'), ('b', LAB_DEPTH - 0.00009, 'label_b')):
        Vp = np.array([[-C_HX, -C_HY, zl], [C_HX, -C_HY, zl], [C_HX, C_HY, zl], [-C_HX, C_HY, zl]])
        F = [(0, 1, 2, 3)] if side == 'a' else [(0, 3, 2, 1)]
        lab = B.mesh_from(f'{name}_label_{side}', Vp, F, mat(mn), smooth=False)
        objs.append(lab)
    # screws (top face only; the bottom ones are never seen)
    sV, sQ, sN = H.mesh_field(H.FieldFn(_screw_fn, (-0.0014, -0.0014, -0.0007), (0.0014, 0.0014, 0.0006)),
                              0.00003 if q >= 1 else 0.00005, cache_key=f'{REEL}:screw:{q >= 1}')
    for i, (sx, sy) in enumerate(SCREWS):
        so = H.add_mesh(f'{name}_screw{i}', sV, sQ, sN, mat('steel'), icon_frame=False)
        so.location = (sx, sy, C_T - 0.00055)
        so.rotation_euler = (0, 0, math.radians(17 + 37 * i))
        objs.append(so)
    hubs = []
    if inner:
        hV, hQ, hN = H.mesh_field(H.FieldFn(_hub_fn, (-0.0115, -0.0115, 0.0024), (0.0115, 0.0115, 0.0096)),
                                  0.00008 if q >= 1 else 0.00012, cache_key=f'{REEL}:hub:{q >= 1}')
        for side, hx, R in (('L', -HUB_X, rL), ('R', HUB_X, rR)):
            ho = H.add_mesh(f'{name}_hub{side}', hV, hQ, hN, mat('pom'), icon_frame=False)
            ho.location = (hx, HUB_Y, 0.0)
            ho.parent = root
            prof = [(HUB_R_OUT - 0.0001, C_T / 2 - 0.0019), (R - 0.0002, C_T / 2 - 0.0019),
                    (R, C_T / 2 - 0.0017), (R, C_T / 2 + 0.0017), (R - 0.0002, C_T / 2 + 0.0019),
                    (HUB_R_OUT - 0.0001, C_T / 2 + 0.0019)]
            pk = lathe_mesh(f'{name}_pack{side}', prof, 192, mat('oxide'))
            pk.parent = ho
            hubs.append(ho)
        # tape path: left pack -> left roller -> along the head openings -> right roller -> right pack
        (lx, ly), (rx, ry) = ROLLERS
        rr = 0.0016
        tL = tangent_point((-HUB_X, HUB_Y), rL, (lx - rr, ly), side=1)
        tR = tangent_point((HUB_X, HUB_Y), rR, (rx + rr, ry), side=-1)
        pts = [tL]
        for a in np.linspace(math.pi, 1.5 * math.pi, 8):
            pts.append((lx + rr * math.cos(a), ly + rr * math.sin(a)))
        for a in np.linspace(1.5 * math.pi, 2 * math.pi, 8):
            pts.append((rx + rr * math.cos(a), ry + rr * math.sin(a)))
        pts.append(tR)
        P2 = np.asarray(pts)
        # resample densely
        seg = np.linalg.norm(np.diff(P2, axis=0), axis=1)
        s = np.concatenate([[0], np.cumsum(seg)])
        ss = np.linspace(0, s[-1], 200)
        P2 = np.stack([np.interp(ss, s, P2[:, 0]), np.interp(ss, s, P2[:, 1])], -1)
        P3 = np.column_stack([P2, np.full(len(P2), C_T / 2)])
        tp = ribbon(f'{name}_tapepath', P3, np.tile([0, 0, 1.0], (len(P3), 1)), 0.00381,
                    [mat('tape_front'), mat('tape_back')])
        objs.append(tp)
        for i, (gx, gy) in enumerate(ROLLERS):
            ro = B.cyl(f'{name}_roller{i}', (gx, gy, C_T / 2), 0.0015, 0.0066, mat('pom'), seg=32)
            pin = B.cyl(f'{name}_pin{i}', (gx, gy, C_T / 2), 0.0006, C_T - 0.0016, mat('steel'), seg=16)
            objs += [ro, pin]
        # pressure pad on a phosphor-bronze leaf spring
        pad = B.cube(f'{name}_pad', (-0.0022, -0.0276, C_T / 2 - 0.0015), (0.0022, -0.0262, C_T / 2 + 0.0015),
                     mat('felt'), bevel=0.0002)
        xs = np.linspace(-0.0055, 0.0055, 23)
        yb = -0.0258 + 0.0012 * (xs / 0.0055) ** 2
        Vs = []
        for zz in (C_T / 2 - 0.002, C_T / 2 + 0.002):
            for xx, yy in zip(xs, yb):
                Vs.append((xx, yy, zz))
        n = len(xs)
        Fs = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
        spring = B.mesh_from(f'{name}_spring', Vs, Fs, mat('bronze'))
        sm = spring.modifiers.new('solid', 'SOLIDIFY')
        sm.thickness = 0.00015
        objs += [pad, spring]
    parent_to(objs, root)
    return dict(root=root, hubL=hubs[0] if hubs else None, hubR=hubs[1] if hubs else None, objs=objs)


# ============================================================================= PENCIL

def _rounded_hex(a=P_FLAT, rc=P_RC, n_flat=9, n_arc=9):
    """Rounded hexagon outline (CCW), flats normal to 0, 60, ... deg. Returns points (N, 2) and normal angle (N)."""
    pts, nrm = [], []
    ai = a - rc
    R_in = ai / math.cos(math.pi / 6)
    for k in range(6):
        t0 = math.radians(60 * k)
        c_prev = R_in * np.array([math.cos(t0 - math.pi / 6), math.sin(t0 - math.pi / 6)])
        c_next = R_in * np.array([math.cos(t0 + math.pi / 6), math.sin(t0 + math.pi / 6)])
        nv = np.array([math.cos(t0), math.sin(t0)])
        p0, p1 = c_prev + rc * nv, c_next + rc * nv
        for s in np.linspace(0, 1, n_flat, endpoint=False):
            pts.append(p0 + (p1 - p0) * s)
            nrm.append(t0)
        for s in np.linspace(0, 1, n_arc, endpoint=False):
            ang = t0 + math.radians(60) * s
            pts.append(c_next + rc * np.array([math.cos(ang), math.sin(ang)]))
            nrm.append(ang)
    return np.asarray(pts), np.asarray(nrm)


def build_pencil(name='pencil', parent=None, q=1.0):
    root = empty(name, parent=parent)
    O, NA = _rounded_hex(n_flat=9 if q >= 1 else 6, n_arc=9 if q >= 1 else 5)
    th = np.arctan2(O[:, 1], O[:, 0])
    rO = np.linalg.norm(O, axis=1)
    zs = np.concatenate([np.linspace(0.00002, P_CONE, 150 if q >= 1 else 70),
                         np.linspace(P_CONE, 0.096, 120)[1:],
                         np.linspace(0.096, 0.1035, 110 if q >= 1 else 50)[1:],
                         np.linspace(0.1035, P_FER_Z0 + 0.0015, 12)[1:]])
    rng = np.random.default_rng(12)
    phis = np.radians(np.array([8.0, 80.0, 147.0, 221.0, 290.0]) + rng.normal(0, 4, 5))
    d0 = 0.00052 + rng.normal(0, 0.00004, 5)
    slope = (P_FLAT * 1.02 - 0.00052) / P_CONE * (1 + rng.normal(0, 0.03, 5))
    V3 = np.zeros((len(zs), len(O), 3))
    facet = np.zeros((len(zs), len(O)), bool)
    for j, z in enumerate(zs):
        r = rO.copy()
        if z < P_CONE + 0.0006:
            rf = np.full(len(O), np.inf)
            for k in range(5):
                c = np.cos(th - phis[k])
                dk = d0[k] + slope[k] * z
                rk = np.where(c > 1e-3, dk / np.maximum(c, 1e-3), np.inf)
                rf = np.minimum(rf, rk)
            facet[j] = rf < r - 1e-7
            r = np.minimum(r, rf)
            if z < 0.00045:   # blunted graphite tip
                rt = math.sqrt(max(0.0, 0.00045 ** 2 - (0.00045 - z) ** 2)) * 1.25
                r = np.minimum(r, rt)
        V3[j, :, 0] = np.cos(th) * r
        V3[j, :, 1] = np.sin(th) * r
        V3[j, :, 2] = z
    # tooth dents (radially inward, elongated across the facet)
    for (phd, zc, tc) in DENTS:
        ph = math.radians(phd)
        tang = np.array([-math.sin(ph), math.cos(ph)])
        on = np.cos(NA - ph) > math.cos(math.radians(40))
        t = O @ tang
        for j, z in enumerate(zs):
            if abs(z - zc) > 0.0012:
                continue
            dep = 0.00024 * np.exp(-((t - tc) / 0.0011) ** 2 - ((z - zc) / 0.00028) ** 2) * on
            rr = np.hypot(V3[j, :, 0], V3[j, :, 1])
            k = np.maximum(rr - dep, 1e-6) / np.maximum(rr, 1e-9)
            V3[j, :, 0] *= k
            V3[j, :, 1] *= k
    body, V, F = grid_mesh(f'{name}_body', V3, mat=None, cap0=(0, 0, 0.0), cap1=(0, 0, zs[-1]))
    nq = (len(zs) - 1) * len(O)
    fl = facet.reshape(-1)
    Fq = np.asarray(F[:nq])
    wood = fl[Fq].mean(1) > 0.5
    idx = np.concatenate([wood.astype(np.int32), np.ones(len(O), np.int32), np.zeros(len(O), np.int32)])
    set_face_mats(body, idx, [mat('lacquer'), mat('cedar')])
    sm = np.ones(len(idx), bool)
    sm[:nq] = ~wood
    sm[nq:nq + len(O)] = False
    body.data.polygons.foreach_set('use_smooth', sm)
    # ferrule: lathe with two crimp grooves and a small dent
    z0, z1 = P_FER_Z0 - 0.0002, P_ERA_Z0 + 0.0002
    Rf = 0.00372
    prof = [(Rf - 0.0003, z0 - 0.0001), (Rf - 0.00005, z0 + 0.00005), (Rf, z0 + 0.0003)]
    zz = np.linspace(z0 + 0.0004, z1 - 0.0004, 160)
    for z in zz:
        g1 = math.exp(-((z - (z0 + 0.0026)) / 0.0003) ** 2) + math.exp(-((z - (z0 + 0.0064)) / 0.0003) ** 2)
        rib = 0.00005 * math.cos((z - z0) / 0.0006 * 2 * math.pi) * (z0 + 0.0034 < z < z0 + 0.0056)
        prof.append((Rf - 0.00026 * g1 + rib, z))
    prof += [(Rf, z1 - 0.0003), (Rf - 0.00005, z1 - 0.00005), (Rf - 0.0003, z1 + 0.0001)]

    def fdent(V3f, a):
        c = np.array([math.cos(math.radians(130)), math.sin(math.radians(130))])
        zc = z0 + 0.0046
        rr = np.hypot(V3f[..., 0], V3f[..., 1])
        cosang = (V3f[..., 0] * c[0] + V3f[..., 1] * c[1]) / np.maximum(rr, 1e-9)
        ang = np.arccos(np.clip(cosang, -1, 1))
        dep = 0.00018 * np.exp(-(ang / 0.22) ** 2 - ((V3f[..., 2] - zc) / 0.0007) ** 2)
        k = (rr - dep) / np.maximum(rr, 1e-9)
        V3f[..., 0] *= k
        V3f[..., 1] *= k
        return V3f
    fer = lathe_mesh(f'{name}_ferrule', prof, 128 if q >= 1 else 64, mat('ferrule'), disp=fdent)
    # eraser: SDF cylinder with a worn, angled, rounded top
    al = math.radians(13.0)
    nrm = np.array([-math.sin(al), 0.0, math.cos(al)])

    def efn(P):
        d_cyl = np.hypot(P[..., 0], P[..., 1]) - 0.00318
        d_top = (P[..., 0] * nrm[0] + (P[..., 2] - (P_LEN - 0.0007)) * nrm[2])
        d = B.smax(d_cyl, d_top, 0.0007)
        return np.maximum(d, (P_ERA_Z0 - 0.0012) - P[..., 2])
    ev, eq, en = H.mesh_field(H.FieldFn(efn, (-0.0034, -0.0034, P_ERA_Z0 - 0.0013), (0.0034, 0.0034, P_LEN + 0.0002)),
                              0.00006 if q >= 1 else 0.0001, cache_key=f'{REEL}:eraser:{q >= 1}')
    era = H.add_mesh(f'{name}_eraser', ev, eq, en, mat('eraser'), icon_frame=False)
    parent_to([body, fer, era], root)
    return dict(root=root, objs=[body, fer, era])


# ============================================================================= DESK, WALL, CRUMBS

def build_desk(center=(0, 0), wall_dist=0.9, wall_dir=(0.0, 1.0), front=0.22):
    """Desk top at z = 0. `center` = the subject; the desk extends `front` metres towards -wall_dir."""
    wd = np.asarray(wall_dir, float) / np.linalg.norm(wall_dir)
    side = np.array([wd[1], -wd[0]])
    c = np.asarray(center, float)
    mid = c + wd * (0.30 - front)
    corners = []
    for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        corners.append(mid + side * 0.45 * s + wd * 0.30 * t)
    desk = B.cube('desk', (-0.45, -0.30, -0.022), (0.45, 0.30, 0.0), mat('desk'), bevel=0.0015, seg=3)
    # the desk texture is centred on the subject: shift the mesh so object coords stay subject-centred
    me = desk.data
    ang = math.atan2(wd[1], wd[0]) - math.pi / 2
    for v in me.vertices:
        x, y, z = v.co
        X = mid[0] + x * math.cos(ang) - y * math.sin(ang) - c[0]
        Y = mid[1] + x * math.sin(ang) + y * math.cos(ang) - c[1]
        v.co = (X, Y, z)
    desk.location = (c[0], c[1], 0)
    wc = c + wd * wall_dist
    wall = B.cube('wall', (-1.5, -0.01, -0.8), (1.5, 0.0, 1.2), mat('wall'))
    wall.location = (wc[0], wc[1], 0)
    wall.rotation_euler = (0, 0, ang)
    return [desk, wall]


def build_crumbs(n, center, rmin, rmax, seed, avoid=None, ang_range=(0, 360)):
    """Rolled pink eraser crumbs (0.5-2.2 mm worms) scattered on the desk."""
    rng = np.random.default_rng(seed)
    objs = []
    for i in range(n):
        for _ in range(50):
            a = math.radians(rng.uniform(*ang_range))
            r = rng.uniform(rmin, rmax) * (0.5 + 0.5 * rng.random() ** 0.5)
            x, y = center[0] + r * math.cos(a), center[1] + r * math.sin(a)
            if avoid is None or not avoid(x, y):
                break
        L = rng.uniform(0.0006, 0.0024)
        rad = rng.uniform(0.00018, 0.00042)
        ts = np.linspace(-1, 1, 9)
        bend = rng.normal(0, 0.25)
        cen = np.stack([ts * L / 2, bend * (ts ** 2) * L * 0.3, np.zeros_like(ts)], -1)
        ring = np.linspace(0, 2 * np.pi, 10, endpoint=False)
        V3 = []
        for t, cc in zip(ts, cen):
            rr = rad * math.sqrt(max(0.05, 1 - t ** 4)) * (1 + rng.normal(0, 0.08))
            V3.append(np.stack([np.full_like(ring, cc[0]), cc[1] + rr * np.cos(ring), rr * np.sin(ring) + rad * 0.85], -1))
        V3 = np.asarray(V3)
        V3 += rng.normal(0, rad * 0.06, V3.shape)
        o, _, _ = grid_mesh(f'crumb{i}', V3, mat=mat('crumb'), cap0=(cen[0][0] - rad * 0.2, cen[0][1], rad * 0.85),
                            cap1=(cen[-1][0] + rad * 0.2, cen[-1][1], rad * 0.85))
        o.location = (x, y, 0)
        o.rotation_euler = (0, 0, rng.uniform(0, 2 * np.pi))
        objs.append(o)
    return objs


# ============================================================================= light rig LAMP + cameras

def lamp_rig(center, cam_az, key=9.0, rim=3.2, bounce=0.6, key_side=0.20, key_back=0.10, key_h=0.45):
    """Tungsten key spot top-left of frame, FLAME rim back-right, warm bounce card front-right (relative to the
    camera azimuth `cam_az` = direction from the subject to the camera, radians)."""
    c = np.asarray(center, float)
    fwd = -np.array([math.cos(cam_az), math.sin(cam_az)])
    right = np.array([fwd[1], -fwd[0]])
    tgt = (c[0], c[1], 0.004)
    kp = c - right * key_side + fwd * key_back
    k = B.light('LAMP_key', 'SPOT', (kp[0], kp[1], key_h), key, lin('LAMP'), target=tgt, soft=0.06, spot=60.0,
                blend=0.4)
    rp = c + right * 0.14 + fwd * 0.22
    r = B.light('LAMP_rim', 'AREA', (rp[0], rp[1], 0.15), rim, lin('FLAME'), target=tgt, size=(0.20, 0.06))
    bp = c + right * 0.26 - fwd * 0.22
    bl = B.light('LAMP_bounce', 'AREA', (bp[0], bp[1], 0.10), bounce, mixl('LAMP', '#FFE2C4', 0.5), target=tgt,
                 size=(0.25, 0.25))
    return dict(key=k, rim=r, bounce=bl)


def make_cam(res, lens, target, elev, az, dist, px=None, fstop=None, focus=None, ortho=None, roll=0.0):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('cam')
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_width = cd.sensor_height = 36.0
    cd.lens = lens
    cd.clip_start = 0.005
    cd.clip_end = 20.0
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho
    o = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(o)
    sc.camera = o
    t = np.asarray(target, float)
    loc = t + dist * np.array([math.cos(elev) * math.cos(az), math.cos(elev) * math.sin(az), math.sin(elev)])
    o.location = tuple(loc)
    if elev > math.radians(89.5):
        o.rotation_euler = (0.0, 0.0, az + math.pi / 2 + roll)
    else:
        B._aim(o, tuple(t))
        if roll:
            o.rotation_euler.rotate_axis('Z', roll)
    bpy.context.view_layer.update()
    if px is not None:
        W, Hh = res
        md = max(W, Hh)
        for _ in range(6):
            p = proj_px(t)
            cd.shift_x += (p[0] - px[0]) / md
            cd.shift_y -= (p[1] - px[1]) / md
            bpy.context.view_layer.update()
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 7
        cd.dof.aperture_rotation = math.radians(12)
        f = np.asarray(focus if focus is not None else target, float)
        vd = np.asarray(o.matrix_world.to_3x3() @ Vector((0, 0, -1)))
        cd.dof.focus_distance = float(np.dot(f - loc, vd))
    return o


def proj_px(pt):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    co = world_to_camera_view(sc, sc.camera, Vector(tuple(float(v) for v in pt)))
    return [float(co.x * sc.render.resolution_x), float((1 - co.y) * sc.render.resolution_y)]


def wpos(obj, local):
    return np.asarray(obj.matrix_world @ Vector(tuple(local)))


def keyframe_spin(obj, deg_total, n_frames, axis=2, base=None):
    """Linear rotation about the object's local axis: 0 at frame 0 -> deg_total at frame n_frames."""
    prefs = bpy.context.preferences.edit
    prefs.keyframe_new_interpolation_type = 'LINEAR'
    r0 = list(obj.rotation_euler) if base is None else list(base)
    obj.rotation_euler = r0
    obj.keyframe_insert('rotation_euler', frame=0)
    r1 = list(r0)
    r1[axis] += math.radians(deg_total)
    obj.rotation_euler = r1
    obj.keyframe_insert('rotation_euler', frame=n_frames)
    obj.rotation_euler = r0


def motion_blur(on=True, shutter=0.5):
    sc = bpy.context.scene
    sc.render.use_motion_blur = on
    sc.render.motion_blur_shutter = shutter


# ============================================================================= scenes

CASS_YAW_HUB = math.radians(18.0)
CAM_HUB = dict(lens=100.0, elev=58.0, dist=0.31, az=-90.0, fstop=6.3, hub_px=(560, 1260))


def scene_hub(res, q, rescue=False):
    """CAM_HUB scene: cassette side A up, yawed 18 deg, pencil standing in the left hub, desk, crumbs, rig."""
    C = build_cassette('cass', rL=0.017, rR=0.0204, q=q)
    C['root'].rotation_euler = (0, 0, CASS_YAW_HUB)
    Pn = build_pencil('pencil', parent=C['hubL'], q=q)
    Pn['root'].location = (0, 0, P_SHOULDER_IN_HUB - P_CONE)
    Pn['root'].rotation_euler = (0, 0, math.radians(-120))
    build_desk(center=(0, 0), wall_dist=0.9, wall_dir=(0, 1), front=0.20)

    def avoid(x, y):
        c, s = math.cos(-CASS_YAW_HUB), math.sin(-CASS_YAW_HUB)
        lx, ly = x * c - y * s, x * s + y * c
        return abs(lx) < C_HX + 0.002 and abs(ly) < C_HY + 0.002
    build_crumbs(26 if q >= 1 else 12, (-0.01, -0.035), 0.012, 0.055, 4, avoid=avoid, ang_range=(150, 330))
    bpy.context.view_layer.update()
    hub_top = wpos(C['hubL'], (0, 0, C_T - 0.0012))
    cam_az = math.radians(CAM_HUB['az'])
    lamp_rig((0.0, 0.0), cam_az)
    focus = wpos(C['hubL'], (0, 0, C_T + 0.006))
    cam = make_cam(res, CAM_HUB['lens'], hub_top, math.radians(CAM_HUB['elev']), cam_az, CAM_HUB['dist'],
                   px=tuple(v * res[0] / 1080.0 for v in CAM_HUB['hub_px']), fstop=CAM_HUB['fstop'], focus=focus)
    return dict(C=C, P=Pn, cam=cam)


def hub_features(S):
    C, Pn = S['C'], S['P']
    bpy.context.view_layer.update()
    f = {}
    f['hub_xy'] = proj_px(wpos(C['hubL'], (0, 0, C_T)))
    f['hub_r_xy'] = proj_px(wpos(C['hubR'], (0, 0, C_T)))
    f['eraser_xy'] = proj_px(wpos(Pn['root'], (0, 0, P_LEN)))
    f['pencil_contact_xy'] = proj_px(wpos(Pn['root'], (0, 0, C_T - P_SHOULDER_IN_HUB + P_CONE)))
    win = [proj_px(wpos(C['root'], (sx * WIN_HX, HUB_Y + sy * WIN_HY, C_T))) for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
    f['window_quad'] = win
    xs = [p[0] for p in win]
    ys = [p[1] for p in win]
    f['window_rect'] = [min(xs), min(ys), max(xs), max(ys)]
    f['pencil_axis'] = [f['pencil_contact_xy'], f['eraser_xy']]
    lab = [proj_px(wpos(C['root'], (x, y, C_T))) for x, y in ((LAB_X0, LAB_Y1), (LAB_X1, LAB_Y1), (LAB_X1, LAB_Y0), (LAB_X0, LAB_Y0))]
    f['label_quad'] = lab
    return {k: (np.round(np.asarray(v, float), 1).tolist()) for k, v in f.items()}


# ============================================================================= quick camera solve (no render)

def cams_report():
    _bpy()
    res = (1080, 1920)
    reset(res, 16)
    S = scene_hub(res, 0.5)
    f = hub_features(S)
    print('CAM_HUB', json.dumps(f))
    return f


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == '_cams':
    cams_report()
